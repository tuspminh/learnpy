Trong kiến trúc Clean Architecture kết hợp DDD, Unit of Work (UoW) là một mẫu thiết kế quản lý giao dịch dữ liệu. Để hiểu chi tiết, chúng ta sẽ mổ xẻ cơ chế hoạt động, vòng đời, cách áp dụng cho SQLite thuần và lý do tại sao nó là "vũ khí tối thượng" bảo vệ toàn vẹn dữ liệu.

* * *

## 🧠 Cơ chế hoạt động của Unit of Work

Bản chất của UoW là duy trì một danh sách các thay đổi (Insert, Update, Delete) trong một phiên làm việc (Business Transaction). Nó hoạt động dựa trên 2 nguyên lý chính:

  1. Một Context duy nhất (Single Session): Đảm bảo tất cả các Repositories trong cùng một Use Case đều chia sẻ chung một kết nối (Connection/Session) duy nhất đến Cơ sở dữ liệu.
  2. Tất cả hoặc không gì cả (Atomicity): Khi Use Case chạy xong, UoW sẽ gửi toàn bộ các lệnh SQL tích lũy vào DB và gọi `COMMIT`. Nếu có bất kỳ lỗi nào xảy ra ở giữa, nó gọi `ROLLBACK` để xóa sạch dấu vết.



* * *

## 🔄 Vòng đời (Lifecycle) của UoW qua Context Manager

Trong Python, cách tốt nhất để triển khai UoW là tận dụng Context Manager thông qua từ khóa `with`. Hãy xem sơ đồ vòng đời chạy của nó:
    
    
    [Bắt đầu Use Case]
           │
           ▼
     1. Gọi `with uow:` ──────► Gọi `__enter__`()
                                 ├─ Mở kết nối Database thật (sqlite3.connect)
                                 ├─ Bắt đầu Transaction (BEGIN TRANSACTION)
                                 └─ Khởi tạo các Repositories, truyền kết nối vào
           │
           ▼
     2. Chạy logic Use Case ──► Gọi `uow.stories.save()`, `uow.users.update()`
                                 └─ Thực thi các câu lệnh SQL trên CÙNG MỘT kết nối
           │
     ┌─────┴────────────────────────┐
     │ Có lỗi (Exception) xảy ra?   │
     └─────┬──────────────────┬─────┘
           │ NO               │ YES
           ▼                  ▼
     3a. Gọi `commit()`       3b. Gọi `rollback()`
       └─ SQL `COMMIT`          └─ SQL `ROLLBACK`
           │                  │
           └─────────┬────────┘
                     │
                     ▼
     4. Gọi `__exit__`() ─────► Đóng kết nối Database (.close())
                                     │
                                     ▼
                              [Kết thúc Use Case]
    

* * *

## 💻 Triển khai Chi tiết với SQLite thuần SQL

Hãy xem mã nguồn chi tiết của `SQLiteUnitOfWork` để thấy cách nó điều khiển `sqlite3` bằng các câu lệnh SQL gốc.
    
    
    # src/infrastructure/unit_of_work.py
    import sqlite3
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.infrastructure.repositories.sqlite_repo import SQLiteStoryRepository
    
    class SQLiteUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str):
            self.db_path = db_path
            self.conn = None
    
        def __enter__(self) -> "SQLiteUnitOfWork":
            # 1. Khởi tạo kết nối vật lý với file SQLite
            self.conn = sqlite3.connect(self.db_path)
            
            # 2. Tắt chế độ tự động commit (Autocommit) của Python sqlite3.
            # Mặc định sqlite3 tự commit sau mỗi lệnh INSERT, chúng ta cần tắt đi để quản lý thủ công.
            self.conn.isolation_level = None 
            
            # 3. Phát lệnh SQL thuần để bắt đầu một Transaction
            self.conn.execute("BEGIN TRANSACTION;")
            
            # 4. Tiêm kết nối (connection) này vào Repository.
            # Nhờ vậy, Repository sẽ chạy các câu lệnh INSERT/UPDATE trên đúng Transaction này.
            self.stories = SQLiteStoryRepository(self.conn)
            
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            Hàm này luôn luôn được chạy khi thoát khỏi khối `with`, kể cả khi có lỗi.
            exc_type: Loại lỗi (nếu có, ví dụ: ValueError, KeyError). Nếu không lỗi, nó là None.
            """
            try:
                if exc_type is not None:
                    # Nếu có lỗi xảy ra bên trong khối `with`, tiến hành hủy bỏ giao dịch
                    print(f"[UoW] Có lỗi xảy ra: {exc_val}. Đang tiến hành Rollback...")
                    self.rollback()
                else:
                    # Nếu mọi thứ chạy mượt mà, lưu toàn bộ dữ liệu vào ổ cứng
                    print("[UoW] Không có lỗi. Đang tiến hành Commit...")
                    self.commit()
            finally:
                # Dù commit hay rollback thành công/thất bại, LUÔN LUÔN phải đóng kết nối DB
                if self.conn:
                    self.conn.close()
                    print("[UoW] Đã đóng kết nối Database an toàn.")
    
        def commit(self):
            """Bắn lệnh SQL thuần để xác nhận lưu dữ liệu vĩnh viễn"""
            if self.conn:
                self.conn.execute("COMMIT;")
    
        def rollback(self):
            """Bắn lệnh SQL thuần để khôi phục dữ liệu về trạng thái trước khi BEGIN"""
            if self.conn:
                self.conn.execute("ROLLBACK;")
    

* * *

## 💥 Thử nghiệm Kịch bản Lỗi để thấy giá trị của UoW

Hãy tưởng tượng trong Use Case cào truyện, bạn thực hiện 2 hành động liên tiếp:

  1. Lưu thông tin cuốn truyện vào bảng `stories`.
  2. Lưu các chương vào bảng `chapters`.



Nếu không có UoW, khi đang lưu đến chương số 5 thì mất điện hoặc dính lỗi dữ liệu, thông tin truyện vẫn nằm trong DB nhưng không có chương nào cả (Dữ liệu rác).

Có UoW bọc lại:
    
    
    # Ví dụ luồng chạy trong Use Case
    with uow:
        # Bước 1: Chạy lệnh INSERT vào bảng stories -> Thành công
        uow.stories.save_story_info(story) 
        
        # Bước 2: Duyệt vòng lặp lưu chapters
        for chapter in story.chapters:
            if chapter.title == "Chương Bị Lỗi":
                raise ValueError("Nội dung chương bị trống!") # Cố tình ném lỗi ở chương 3
            uow.stories.save_chapter(chapter)
    

Kết quả vận hành thực tế:

  * Lệnh `INSERT` của cuốn truyện và Chương 1, Chương 2 đã được gửi đến SQLite nhưng nằm ở trạng thái chờ (Pending).
  * Đến chương 3, `ValueError` bị kích hoạt. Khối `with` lập tức dừng lại và nhảy vào hàm `__exit__`.
  * Hàm `__exit__` thấy `exc_type` là `ValueError`, nó lập tức gọi `self.rollback()`.
  * SQLite xóa bỏ toàn bộ các lệnh `INSERT` đang chờ trước đó. Database của bạn quay về trạng thái sạch sẽ hoàn hảo như chưa từng thực hiện việc crawl này.



* * *

## 🚀 Tóm lại: Tại sao phải làm phức tạp như vậy?

Tiêu chí| Khi KHÔNG dùng Unit of Work| Khi CÓ Unit of Work  
---|---|---  
Quản lý Kết nối| Mỗi Repository tự mở và đóng kết nối riêng ──► Tốn tài nguyên, dễ rò rỉ (leak) kết nối.| Chỉ mở 1 kết nối duy nhất khi bắt đầu Use Case và tự đóng ở `__exit__`.  
Độ toàn vẹn dữ liệu| Lỗi bước nào, dữ liệu các bước trước vẫn bị lưu lại ──► Sinh ra dữ liệu rác, lỗi logic hệ thống.| Lỗi bất kỳ bước nào, toàn bộ giao dịch bị hủy bỏ (Rollback) ──► Dữ liệu luôn nhất quán.  
Vị trí nút Commit| Hàm `.commit()` nằm rải rác khắp nơi trong Repository hoặc Controller.| Chỉ có duy nhất 1 nút Commit nằm tập trung tại UoW, do Tầng Ứng dụng điều khiển.  
  
Bạn đã nắm được bản chất cốt lõi của Unit of Work chưa? Nếu bạn muốn đi tiếp, hãy cho tôi biết bạn có muốn tìm hiểu cách xử lý nâng cao với Domain Events (ví dụ: khi UoW commit thành công, nó sẽ tự động kích hoạt một thông báo gửi tới điện thoại của người đọc) không?