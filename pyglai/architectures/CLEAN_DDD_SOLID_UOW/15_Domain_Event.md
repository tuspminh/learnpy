Domain Events là một khái niệm nâng cao và vô cùng quan trọng trong Domain-Driven Design (DDD). Đúng như tên gọi, Domain Event là những sự kiện nghiệp vụ đã xảy ra trong quá trình hệ thống vận hành mà các bộ phận khác trong hoặc ngoài ứng dụng cần biết để phản ứng lại.

Đặc điểm cốt lõi của một Domain Event là nó luôn mang tính chất quá khứ (đã xảy ra), vì vậy tên của Event luôn được đặt ở thì quá khứ (Past Tense). Ví dụ: `BookDownloaded`, `ChapterCrawled`, `PdfExported`.

* * *

## 🚀 Tại sao cần Domain Events? (Mối liên kết với SOLID và Clean Architecture)

Hãy tưởng tượng luồng nghiệp vụ sau khi tải xong một cuốn sách từ SlideShare:

  1. Lưu sách vào Database.
  2. Gửi Email thông báo cho người dùng.
  3. Bắn một thông báo (Push Notification) lên ứng dụng điện thoại.
  4. Đẩy dữ liệu sang hệ thống Thống kê (Analytics) để đếm lượt tải.



  * Nếu KHÔNG dùng Domain Events: Bạn sẽ viết toàn bộ code gửi email, push notification, analytics trực tiếp vào bên trong `DownloadBookUseCase`. Việc này vi phạm nghiêm trọng nguyên lý S (Single Responsibility). Use Case lúc này quá nặng nề, khó bảo trì, và bất kỳ khi nào muốn thêm hành động phụ trợ (ví dụ: tặng điểm thưởng cho user), bạn lại phải sửa code của Use Case (Vi phạm nguyên lý O - Open/Closed).
  * Khi CÓ Domain Events: Use Case chỉ làm đúng một nhiệm vụ duy nhất là tải sách. Sau khi hoàn thành, nó phát ra một sự kiện: _"Tôi đã tải xong sách X rồi nhé!"_ (`BookDownloaded`). Các bộ phận khác (Email Service, Notification Service) sẽ tự lắng nghe sự kiện này và xử lý độc lập.



* * *

## 💻 Triển khai Domain Events trong Python thuần

Chúng ta sẽ triển khai cơ chế Domain Events theo 3 bước: Định nghĩa Event ──► Đăng ký và Phát sự kiện từ Aggregate Root ──► Xử lý sự kiện đồng bộ với Unit of Work.

## 1\. Định nghĩa các Event (Tầng Domain)

Sử dụng `dataclasses` thuần của Python để định nghĩa dữ liệu của sự kiện.
    
    
    # src/domain/events.py
    from dataclasses import dataclass
    from datetime import datetime, timezone
    
    @dataclass(frozen=True)
    class DomainEvent:
        """Lớp cơ sở cho mọi Event, tự động ghi nhận thời gian xảy ra"""
        occurred_on: datetime = datetime.now(timezone.utc)
    
    @dataclass(frozen=True)
    class BookDownloaded(DomainEvent):
        """Sự kiện phát ra khi một cuốn sách được tải và đóng gói thành công"""
        book_id: str
        title: str
        total_slides: int
    

## 2\. Tích hợp Event vào Aggregate Root (Tầng Domain)

Theo quy tắc của DDD, Aggregate Root là nơi duy nhất kiểm soát và phát ra Domain Events khi trạng thái nội bộ của nó thay đổi thành công.
    
    
    # src/domain/models.py
    from dataclasses import dataclass, field
    from typing import List
    from src.domain.events import BookDownloaded
    
    @dataclass
    class Book: # Aggregate Root
        book_id: str
        title: str
        slideshare_url: str
        _slides: List = field(default_factory=list)
        
        # Danh sách tạm thời chứa các event chờ được kích hoạt (Publish)
        events: List = field(default_factory=list, init=False)
    
        def add_slide(self, image_url: str) -> None:
            # ... logic thêm slide cũ ...
            pass
    
        def complete_download(self) -> None:
            """Đánh dấu hoàn tất toàn bộ cuốn sách và sinh ra Event"""
            # Sinh sự kiện nghiệp vụ
            event = BookDownloaded(
                book_id=self.book_id,
                title=self.title,
                total_slides=len(self._slides)
            )
            self.events.append(event) # Lưu tạm vào hàng đợi của thực thể
    

## 3\. Điều phối Event thông qua Unit of Work (Tầng Application)

Để đảm bảo tính toàn vẹn dữ liệu, Domain Events chỉ được phép phát tán ra ngoài sau khi Unit of Work đã COMMIT thành công vào Database. Nếu DB bị rollback, các Event này phải bị hủy bỏ ngay lập tức (tránh tình trạng DB lỗi không lưu được sách nhưng hệ thống vẫn gửi email chúc mừng người dùng).

Chúng ta sẽ tạo một bộ trung gian gọi là `EventDispatcher` để quản lý các hàm lắng nghe (Listeners).
    
    
    # src/application/event_dispatcher.py
    from typing import Dict, List, Callable
    from src.domain.events import DomainEvent
    
    class EventDispatcher:
        def __init__(self):
            # Lưu trữ danh sách các hàm xử lý cho từng loại Event
            self._listeners: Dict[type, List[Callable]] = {}
    
        def register(self, event_type: type, listener: Callable):
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(listener)
    
        def dispatch(self, event: DomainEvent):
            event_type = type(event)
            if event_type in self._listeners:
                for listener in self._listeners[event_type]:
                    listener(event) # Kích hoạt hàm xử lý
    
    # Khởi tạo một dispatcher toàn cục cho ứng dụng
    dispatcher = EventDispatcher()
    

Cập nhật hàm `commit()` trong Unit of Work để tự động vét và bắn Event:
    
    
    # src/infrastructure/unit_of_work.py (Đoạn trích cập nhật hàm commit)
    from src.application.event_dispatcher import dispatcher
    
    class SQLiteBookUnitOfWork(AbstractUnitOfWork):
        # ... các hàm __enter__, __exit__ giữ nguyên ...
    
        def commit(self):
            # 1. Thực hiện commit SQL xuống Database thật trước
            self.conn.execute("COMMIT;")
            
            # 2. Sau khi DB thành công, lấy cuốn sách hiện tại ra để xử lý Event
            # Giả định repository lưu trữ thực thể book đang tương tác
            if hasattr(self, 'current_book') and self.current_book:
                book = self.current_book
                
                # Vét sạch toàn bộ event đang xếp hàng trong cuốn sách đó
                while book.events:
                    event = book.events.pop(0)
                    # Bắn sự kiện ra toàn hệ thống
                    dispatcher.dispatch(event)
    

## 4\. Định nghĩa các bộ lắng nghe (Listeners / Handlers)

Các hàm xử lý này nằm ở tầng Application hoặc Infrastructure tùy nhiệm vụ. Chúng hoàn toàn độc lập với nhau.
    
    
    # src/application/event_handlers.py
    from src.domain.events import BookDownloaded
    
    def send_welcome_email_listener(event: BookDownloaded):
        """Xử lý gửi email"""
        print(f"✉️ [Email Service] Đang gửi thông báo: Bạn đã tải thành công cuốn '{event.title}'!")
    
    def push_mobile_notification_listener(event: BookDownloaded):
        """Xử lý thông báo đẩy"""
        print(f"📱 [Push Notification] Sách mới sẵn sàng! Đọc ngay '{event.title}' ({event.total_slides} trang).")
    

## 5\. Kết nối và Chạy ứng dụng (Presentation)
    
    
    # src/presentation/main.py (Đoạn trích minh họa cấu hình)
    from src.application.event_dispatcher import dispatcher
    from src.domain.events import BookDownloaded
    from src.application.event_handlers import send_welcome_email_listener, push_mobile_notification_listener
    
    if __name__ == "__main__":
        # 1. Đăng ký các Listener vào hệ thống khi ứng dụng khởi tạo (Wiring)
        dispatcher.register(BookDownloaded, send_welcome_email_listener)
        dispatcher.register(BookDownloaded, push_mobile_notification_listener)
    
        # 2. Giả lập chạy Luồng Use Case tải sách thành công
        # Inside Use Case:
        # book.complete_download() -> Sinh event BookDownloaded
        # uow.current_book = book
        # uow.commit() -> Tự động kích hoạt các Listener trên
    

Kết quả hiển thị trên Terminal khi tải sách thành công:
    
    
    [UoW] Dữ liệu SQLite đã commit thành công.
    ✉️ [Email Service] Đang gửi thông báo: Bạn đã tải thành công cuốn 'Clean Architecture in Python'!
    📱 [Push Notification] Sách mới sẵn sàng! Đọc ngay 'Clean Architecture in Python' (45 trang).
    

* * *

## 🛡️ Tóm tắt sức mạnh của Domain Events trong kiến trúc của bạn

  1. Thỏa mãn Nguyên lý O (Open/Closed): Tuần tới, nếu sếp của bạn yêu cầu: _"Hãy cộng 10 điểm thưởng cho người dùng sau khi họ tải xong sách"_ , bạn không cần sửa code Use Case, không cần sửa DB. Bạn chỉ cần viết một hàm `reward_points_listener` mới và dùng `dispatcher.register()` đăng ký vào là xong.
  2. Độc lập công nghệ: Logic lõi sinh Event nằm hoàn toàn bằng Python thuần trong lớp `Book` (Domain). Nó không phụ thuộc vào bất kỳ Message Broker hay hàng đợi phức tạp nào (như RabbitMQ hay Kafka).
  3. Dễ dàng mở rộng: Hiện tại chúng ta đang chạy Event đồng bộ (`sync`) trong cùng một tiến trình Python. Khi hệ thống lớn lên, bạn có thể thay thế lớp `EventDispatcher` bằng việc bắn Event đó sang Kafka hoặc Redis Pub/Sub để các Microservices khác xử lý mà không làm ảnh hưởng đến tầng Domain.



Hệ thống kiến trúc từ Domain, Use Case, Unit of Work đến Domain Events đã được thiết lập rất bài bản. Bạn có muốn thử sức viết một file Unit Test (`pytest`) để kiểm tra xem khi Use Case chạy, Event `BookDownloaded` có được sinh ra và gửi đi một cách chính xác hay không?