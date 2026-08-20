Dưới đây là cách tích hợp Hệ thống tạo file Log vào Unit of Work cho ứng dụng crawl truyện của bạn.

Kịch bản thực tế: Khi bạn crawl truyện, bạn muốn ghi lại toàn bộ nhật ký (ví dụ: _Crawl thành công truyện X, chương Y_). Nếu quá trình lưu database bị lỗi và hệ thống thực hiện `ROLLBACK`, bạn cũng muốn hủy bỏ (xóa sạch/hoàn tác) các dòng log tạm thời được tạo ra trong phiên làm việc đó để file log không ghi nhận những thông tin sai lệch.

* * *

## 💻 Triển khai tích hợp Log vào Unit of Work

Chúng ta sẽ tạo ra một bộ quản lý log tạm thời (`TransactionLogManager`) chạy song song với `sqlite3`. Bộ quản lý này sẽ ghi log vào bộ nhớ đệm (RAM) trước, và chỉ ghi thực sự vào file `.log` trên ổ cứng khi UoW được `COMMIT` thành công.

## 1\. Cập nhật Interface của UoW (Tầng Application)

Chúng ta bổ sung thêm một thuộc tính đại diện cho logger dịch vụ vào `AbstractUnitOfWork`.
    
    
    # src/application/unit_of_work.py
    from abc import ABC, abstractmethod
    from src.domain.repositories import StoryRepository
    
    class AbstractUnitOfWork(ABC):
        stories: StoryRepository
    
        def __enter__(self) -> "AbstractUnitOfWork": return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None: self.rollback()
            else: self.commit()
    
        @abstractmethod
        def log(self, message: str) -> None: 
            """Hàm ghi log tạm thời thuộc phạm vi transaction"""
            pass
    
        @abstractmethod
        def commit(self): pass
    
        @abstractmethod
        def rollback(self): pass
    

## 2\. Triển khai SQLiteUnitOfWork tích hợp File Log (Tầng Infrastructure)
    
    
    # src/infrastructure/unit_of_work.py
    import sqlite3
    import os
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.infrastructure.repositories.sqlite_repo import SQLiteStoryRepository
    
    class SQLiteWithLogUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str, log_path: str = "app_history.log"):
            self.db_path = db_path
            self.log_path = log_path
            self.conn = None
            self._pending_logs = []  # Bộ nhớ đệm lưu log tạm thời trên RAM
    
        def __enter__(self) -> "SQLiteWithLogUnitOfWork":
            # Khởi động DB Transaction
            self.conn = sqlite3.connect(self.db_path)
            self.conn.isolation_level = None 
            self.conn.execute("BEGIN TRANSACTION;")
            
            # Khởi tạo Repository
            self.stories = SQLiteStoryRepository(self.conn)
            
            # Xóa sạch log tạm thời của phiên cũ (nếu có)
            self._pending_logs = [] 
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                if exc_type is not None:
                    self.rollback()
                else:
                    self.commit()
            finally:
                if self.conn:
                    self.conn.close()
    
        def log(self, message: str) -> None:
            """Thay vì ghi thẳng vào file, ta lưu tạm vào RAM để chờ kết quả transaction"""
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self._pending_logs.append(formatted_message)
            print(f"[Log Tạm Thời]: {message}")
    
        def commit(self):
            # 1. Commit dữ liệu xuống SQLite
            if self.conn:
                self.conn.execute("COMMIT;")
                print("[UoW] Dữ liệu SQLite đã commit.")
    
            # 2. Ghi toàn bộ log tạm thời từ RAM xuống file vật lý trên ổ cứng
            if self._pending_logs:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.writelines(self._pending_logs)
                print(f"[UoW] Đã ghi {len(self._pending_logs)} dòng log vào file {self.log_path}.")
                self._pending_logs = []
    
        def rollback(self):
            # 1. Hủy bỏ thay đổi trong SQLite
            if self.conn:
                self.conn.execute("ROLLBACK;")
                print("[UoW] SQLite đã rollback thành công.")
                
            # 2. Giải phóng bộ nhớ đệm log mà KHÔNG ghi bất cứ thứ gì ra file
            print(f"[UoW] Hủy bỏ {len(self._pending_logs)} dòng log tạm thời. File log không bị biến động.")
            self._pending_logs = []
    

* * *

## 🧪 Chạy thử nghiệm 2 kịch bản (Thành công và Thất bại)

Hãy xem cách tầng `Application` (Use Case) sử dụng UoW này và kết quả tạo file log thực tế.

## Kịch bản 1: Sử dụng thành công (Ghi log vào file)
    
    
    # Giả định luồng chạy trong Use Case thành công
    uow = SQLiteWithLogUnitOfWork(db_path="reading_app.db", log_path="app_history.log")
    
    with uow:
        uow.log("Bắt đầu crawl truyện 'Đắc Nhân Tâm'...")
        # Giả lập thao tác lưu DB thành công
        uow.log("Crawl hoàn tất Chương 1.")
        uow.log("Crawl hoàn tất Chương 2.")
    

Kết quả hiển thị trên Terminal:
    
    
    [Log Tạm Thời]: Bắt đầu crawl truyện 'Đắc Nhân Tâm'...
    [Log Tạm Thời]: Crawl hoàn tất Chương 1.
    [Log Tạm Thời]: Crawl hoàn tất Chương 2.
    [UoW] Dữ liệu SQLite đã commit.
    [UoW] Đã ghi 3 dòng log vào file app_history.log.
    

👉 _Kiểm tra file`app_history.log` trên máy tính, bạn sẽ thấy 3 dòng nhật ký kèm thời gian được ghi nhận một cách chính xác._

* * *

## Kịch bản 2: Gặp sự cố đột xuất (Hủy bỏ log)
    
    
    # Giả định luồng chạy gặp lỗi dữ liệu ở Chương 2
    try:
        with uow:
            uow.log("Bắt đầu crawl truyện 'Đố Vui hại não'...")
            uow.log("Crawl hoàn tất Chương 1.")
            
            # Bất ngờ gặp lỗi không có nội dung ở Chương 2
            uow.log("Đang crawl Chương 2...")
            raise ValueError("Lỗi: Chương 2 trống rỗng!")
    except ValueError as e:
        print(f"Luồng chính bắt được lỗi: {e}")
    

Kết quả hiển thị trên Terminal:
    
    
    [Log Tạm Thời]: Bắt đầu crawl truyện 'Đố Vui hại não'...
    [Log Tạm Thời]: Crawl hoàn tất Chương 1.
    [Log Tạm Thời]: Đang crawl Chương 2...
    [UoW] SQLite đã rollback thành công.
    [UoW] Hủy bỏ 3 dòng log tạm thời. File log không bị biến động.
    Luồng chính bắt được lỗi: Lỗi: Chương 2 trống rỗng!
    

👉 _Kiểm tra file`app_history.log`, bạn sẽ thấy hoàn toàn trống trơn (hoặc không hề có thêm dòng log nào của cuốn truyện 'Đố Vui hại não'). Hệ thống log đã được bảo vệ sạch sẽ khỏi các dữ liệu rác của những transaction bị hỏng._

* * *

## 🛡️ Tại sao cách làm này đúng chuẩn SOLID?

  1. S (Single Responsibility): Bản thân hàm `uow.log()` không tự mở file ghi đĩa rải rác. Việc ghi đĩa tập trung một chỗ duy nhất tại thời điểm `commit()`.
  2. D (Dependency Inversion): Lớp Use Case chỉ gọi `self.uow.log("tin nhắn")` mà không cần biết phía sau UoW đang lưu log vào file `.log`, bắn log lên dịch vụ đám mây (CloudWatch), hay in ra màn hình Console.



Để phát triển sâu hơn cho kiến trúc ứng dụng này, hãy cho tôi biết:

  * Bạn có muốn tìm hiểu cách bọc toàn bộ hệ thống này thành một ứng dụng có giao diện Web API (như FastAPI) không?
  * Hay bạn muốn tìm hiểu cách viết mã nguồn cho Crawler thật bằng BeautifulSoup để bóc tách một trang web truyện thực tế?