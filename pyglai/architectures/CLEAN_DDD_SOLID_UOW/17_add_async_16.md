Để triển khai đồng bộ dữ liệu bất đồng bộ (Asynchronous Eventual Consistency) giữa Write DB (Nơi ghi dữ liệu chính xác) và Read DB (Nơi đọc dữ liệu thần tốc) thông qua Domain Events, chúng ta sẽ xây dựng một cơ chế phân tách luồng:

Khi có sách mới được cào thành công, luồng ghi (Write Side) sẽ lưu dữ liệu cốt lõi vào Write DB và bắn ra một sự kiện `BookDownloaded`. Sự kiện này thay vì được xử lý đồng bộ ngay lập tức làm chậm luồng của người dùng, sẽ được đẩy vào một Hàng đợi tạm thời (Message Queue). Một tiến trình chạy ngầm (Worker) độc lập sẽ nhặt sự kiện này lên, định dạng lại cấu trúc dữ liệu theo dạng phẳng (Denormalized) rồi lưu sang Read DB.

Dưới đây là thiết kế chi tiết áp dụng cấu trúc Clean Architecture và CQRS cho ứng dụng của bạn.

* * *

## 🧠 Sơ đồ luồng xử lý bất đồng bộ
    
    
    [MÀN HÌNH CRAWL] ──► Gửi Command ──► [Write Side Use Case]
                                                  │
                                           (Lưu PostgreSQL)
                                                  │
                                                  ▼
                                           [Write Database]
                                                  │
                                           (Commit Thành công)
                                                  │
                                                  ▼
                                        Bắn Event: BookDownloaded
                                                  │
                                          (Đẩy vào Hàng đợi)
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │  MESSAGE QUEUE   │ (Ví dụ: Memory/Redis/RabbitMQ)
                                        └─────────┬────────┘
                                                  │
                                          (Worker nhặt Event)
                                                  ▼
                                        [Read Model Listener]
                                                  │
                                         (Dàn phẳng dữ liệu)
                                                  │
                                                  ▼
                                           [Read Database] (Ví dụ: Elasticsearch/MongoDB)
                                                  ▲
                                                  │ (Truy vấn thẳng)
    [MÀN HÌNH ĐỌC TRUYỆN] ────────────────────────┘
    

* * *

## 💻 Triển khai mã nguồn minh họa với Python

Để giữ ứng dụng chạy mượt mà mà không cần cài đặt hạ tầng phức tạp như RabbitMQ hay Kafka ngay lập tức, chúng ta sẽ mô phỏng một hàng đợi bất đồng bộ bằng `queue.Queue` và `threading.Thread` của Python. Cơ chế này hoàn toàn có thể thay thế bằng các thư viện như `Celery` hoặc `Arq` sau này mà không làm ảnh hưởng tới Domain.

## 1\. Xây dựng Hàng đợi Sự kiện Bất đồng bộ (Tầng Infrastructure - Hệ thống chung)
    
    
    # src/infrastructure/messaging/async_event_bus.py
    import queue
    import threading
    from typing import Dict, List, Callable
    from src.domain.events import DomainEvent
    
    class AsyncEventBus:
        """Hệ thống quản lý và phân phối Event chạy trên luồng ngầm độc lập (Worker)"""
        def __init__(self):
            self._queue = queue.Queue()
            self._listeners: Dict[type, List[Callable]] = {}
            self._worker_thread = None
            self._running = False
    
        def register(self, event_type: type, listener: Callable):
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(listener)
    
        def publish(self, event: DomainEvent):
            """Đẩy event vào hàng đợi rồi thoát hàm ngay lập tức (Bất đồng bộ)"""
            print(f"🚀 [Event Bus] Nhận event '{type(event).__name__}', xếp hàng chờ xử lý...")
            self._queue.put(event)
    
        def start_worker(self):
            """Khởi động luồng ngầm để xử lý Event tuần tự phía sau hậu trường"""
            self._running = True
            self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self._worker_thread.start()
            print("⚙️ [Event Bus] Worker chạy ngầm đã khởi động và đang lắng nghe...")
    
        def _process_queue(self):
            while self._running:
                try:
                    # Đợi có event trong hàng đợi (chặn tối đa 1 giây để kiểm tra flag running)
                    event = self._queue.get(timeout=1)
                    event_type = type(event)
                    
                    if event_type in self._listeners:
                        for listener in self._listeners[event_type]:
                            try:
                                listener(event) # Kích hoạt bộ xử lý (Listener)
                            except Exception as e:
                                print(f"💥 Lỗi tại Listener {listener.__name__}: {e}")
                                
                    self._queue.task_done()
                except queue.Empty:
                    continue
    
    # Khởi tạo một Event Bus toàn cục cho ứng dụng
    async_bus = AsyncEventBus()
    

## 2\. Cập nhật Unit of Work để đẩy Event vào Bus bất đồng bộ (Tầng Infrastructure)

Thay vì gọi `dispatcher.dispatch(event)` đồng bộ làm nghẽn tiến trình cào sách, chúng ta chuyển qua gọi `async_bus.publish(event)`.
    
    
    # src/infrastructure/write_side/unit_of_work.py
    from src.infrastructure.messaging.async_event_bus import async_bus
    
    class SQLiteBookUnitOfWork:
        def __init__(self, db_path: str):
            self.db_path = db_path
            self.current_book = None # Giữ tham chiếu tới Aggregate Root đang tương tác
    
        def commit(self):
            self.conn.execute("COMMIT;")
            print("[Write DB] Dữ liệu gốc đã được COMMIT an toàn vĩnh viễn.")
            
            # Sau khi dữ liệu gốc đã ghi đĩa thành công, đẩy các Domain Events vào hàng đợi ngầm
            if self.current_book and hasattr(self.current_book, 'events'):
                while self.current_book.events:
                    event = self.current_book.events.pop(0)
                    async_bus.publish(event) # Bắn đi bất đồng bộ
    

## 3\. Tạo Bộ lắng nghe để đồng bộ sang Read DB (Tầng Infrastructure - Read Side)

Đây là nơi nhận Event, định dạng lại dữ liệu thô phục vụ việc hiển thị, và lưu vào Read CSDL (Ví dụ ở đây giả lập ghi vào một bảng phẳng hoặc một database đọc riêng biệt).
    
    
    # src/infrastructure/read_side/projectors.py
    import sqlite3
    import time
    from src.domain.events import BookDownloaded
    
    def update_read_model_projector(event: BookDownloaded):
        """
        Hàm này chạy trên luồng ngầm (Worker Thread). 
        Nhiệm vụ: Lấy thông tin từ Event để 'Dàn phẳng' (Denormalize) dữ liệu vào Read DB.
        """
        print(f"📥 [Worker] Bắt đầu đồng bộ sách '{event.title}' sang Read DB...")
        
        # Giả lập tác vụ xử lý mất thời gian (ví dụ: tạo index, trích xuất text nâng cao)
        time.sleep(2) 
        
        # Kết nối vào Database bên Đọc (Read Side DB)
        conn = sqlite3.connect("slideshare_crawler.db")
        cursor = conn.cursor()
        
        # Tạo bảng phẳng tối ưu cho việc hiển thị (nếu chưa có)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_catalog_read_model (
                book_id TEXT PRIMARY KEY,
                title TEXT,
                total_slides INTEGER,
                synced_at TEXT
            )
        """)
        
        # Lưu bản ghi tối ưu sẵn phục vụ hiển thị thần tốc ngoài trang chủ
        from datetime import datetime
        cursor.execute(
            "INSERT OR REPLACE INTO book_catalog_read_model (book_id, title, total_slides, synced_at) VALUES (?, ?, ?, ?)",
            (event.book_id, event.title, event.total_slides, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        print(f"✅ [Worker] Sách '{event.title}' đã sẵn sàng bên Read DB!")
    

## 4\. Ghép nối hệ thống và Chạy thử nghiệm (Tầng Presentation)

Hãy xem toàn bộ hệ thống phối hợp hoạt động một cách mượt mà và bất đồng bộ như thế nào.
    
    
    # src/presentation/main.py
    import time
    from src.infrastructure.messaging.async_event_bus import async_bus
    from src.domain.events import BookDownloaded
    from src.infrastructure.read_side.projectors import update_read_model_projector
    from src.infrastructure.write_side.unit_of_work import SQLiteBookUnitOfWork
    from src.domain.models import Book
    
    if __name__ == "__main__":
        DB_PATH = "slideshare_crawler.db"
    
        # 1. KHỞI ĐỘNG HỆ THỐNG (Wiring)
        # Đăng ký hàm cập nhật Read Model lắng nghe sự kiện BookDownloaded
        async_bus.register(BookDownloaded, update_read_model_projector)
        # Bật luồng Worker chạy ngầm
        async_bus.start_worker()
    
        # 2. MÔ PHỎNG LUỒNG GHI (Command Side)
        print("\n--- [Luồng Ghi] Bắt đầu xử lý Lưu Sách ---")
        uow = SQLiteBookUnitOfWork(DB_PATH)
        
        with uow:
            # Khởi tạo Domain Model và tích lũy dữ liệu
            book = Book(book_id="book-999", title="Kinh Tế Vĩ Mô", slideshare_url="https://...")
            book.add_slide("https://.../slide1.jpg")
            book.add_slide("https://.../slide2.jpg")
            
            # Gọi hàm nghiệp vụ để sinh Event trạng thái quá khứ
            book.complete_download() 
            
            # Đưa vào UoW
            uow.current_book = book
            print("[Luồng Ghi] Đang ghi dữ liệu gốc vào CSDL chính...")
            # (Ở đây giả định bạn đã chạy hàm SQL chèn dữ liệu cũ)
            
        print("--- [Luồng Ghi] Kết thúc xử lý. Trả kết quả về cho giao diện ngay! ---\n")
    
        # 3. GIẢ LẬP THEO DÕI HẬU TRƯỜNG
        # Để kiểm chứng Worker chạy ngầm, chúng ta cho luồng chính ngủ vài giây
        print("[Hệ Thống] Luồng chính đang rảnh rỗi hoặc xử lý yêu cầu khác...")
        time.sleep(3)
        print("[Hệ Thống] Tắt ứng dụng.")
    

* * *

## 🚀 Kết quả vận hành in ra trên Terminal

Hãy quan sát kỹ thứ tự in ra để thấy tính chất Bất đồng bộ:
    
    
    ⚙️ [Event Bus] Worker chạy ngầm đã khởi động và đang lắng nghe...
    
    --- [Luồng Ghi] Bắt đầu xử lý Lưu Sách ---
    [Luồng Ghi] Đang ghi dữ liệu gốc vào CSDL chính...
    [Write DB] Dữ liệu gốc đã được COMMIT an toàn vĩnh viễn.
    🚀 [Event Bus] Nhận event 'BookDownloaded', xếp hàng chờ xử lý...
    --- [Luồng Ghi] Kết thúc xử lý. Trả kết quả về cho giao diện ngay! ---
    
    [Hệ Thống] Luồng chính đang rảnh rỗi hoặc xử lý yêu cầu khác...
    📥 [Worker] Bắt đầu đồng bộ sách 'Kinh Tế Vĩ Mô' sang Read DB...
    ✅ [Worker] Sách 'Kinh Tế Vĩ Mô' đã sẵn sàng bên Read DB!
    [Hệ Thống] Tắt ứng dụng.
    

## 💡 Những lưu ý cốt lõi khi triển khai mô hình này

  1. Trạng thái nhất quán sau cùng (Eventual Consistency): Khách hàng khi tải xong sách sẽ thấy màn hình báo thành công ngay lập tức (Luồng Ghi hoàn tất chỉ trong tích tắc). Tuy nhiên, có thể mất từ vài mili-giây đến vài giây sau, cuốn sách mới xuất hiện trên bảng thống kê ở trang chủ (Read DB hoàn tất sau). Đây là sự đánh đổi hoàn toàn xứng đáng để hệ thống đạt được hiệu năng cực đại.
  2. Idempotency (Tính không đổi): Vì mạng có thể bị lag, Event có thể bị gửi lặp lại 2 lần. Hàm ở lớp `Projector` (Read Side) của bạn bắt buộc phải dùng lệnh `INSERT OR REPLACE` hoặc kiểm tra ID trước khi chèn để đảm bảo nếu một Event chạy 2 lần thì dữ liệu bên Read DB vẫn không bị sai lệch.
  3. Mở rộng lên Enterprise: Khi dự án có quy mô cực lớn trên Cloud, bạn chỉ cần thay thế file `async_event_bus.py` bằng một thư viện kết nối đến Kafka hoặc AWS SQS/SNS và tách code `Worker` ra thành một file `worker.py` chạy trên một server độc lập hoàn toàn với server chạy Web API.



Hệ thống kiến trúc của bạn giờ đây đã đạt mức độ hoàn thiện rất cao, sẵn sàng giải quyết các bài toán tải trọng lớn. Bạn có câu hỏi nào về chi tiết triển khai hoặc muốn tối ưu thêm phần nào trong mô hình này không?