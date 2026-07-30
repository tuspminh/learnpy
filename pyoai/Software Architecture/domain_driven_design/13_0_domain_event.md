# Domain-Driven Design Deep Dive

# Buổi 13 (Roadmap cập nhật): Domain Event trong DDD

Sau buổi 12, chúng ta đã học:

  * Entity 
  * Value Object 
  * Aggregate 
  * Aggregate Root 
  * Repository 
  * Application Layer 
  * Use Case 
  * Domain Service 



Bây giờ chúng ta học một khái niệm rất quan trọng trong DDD hiện đại:

# Domain Event

* * *

# 1\. Vấn đề: Sau khi một nghiệp vụ xảy ra thì sao?

Ví dụ:

Người dùng publish một truyện.

Luồng đơn giản:
    
    
    User
    
     |
    
    PublishNovelUseCase
    
     |
    
    Novel.publish()
    
     |
    
    Database

Nhưng thực tế:

Khi truyện được publish:

Cần:

  * Cập nhật tìm kiếm. 
  * Gửi thông báo. 
  * Cập nhật thống kê. 
  * Xóa cache. 
  * Gửi email. 



* * *

Cách làm tệ:
    
    
    class PublishNovelUseCase:
    
    
        def execute(self):
    
            novel.publish()
    
    
            search.update()
    
    
            notification.send()
    
    
            cache.clear()
    
    
            statistics.update()

* * *

Vấn đề:

Use Case biết quá nhiều.
    
    
    PublishNovelUseCase
    
        |
        |
        + Search
        + Notification
        + Cache
        + Statistics

Coupling rất cao.

* * *

DDD giải quyết bằng:

# Domain Event

* * *

# 2\. Domain Event là gì?

Định nghĩa:

> Domain Event là một sự kiện quan trọng trong nghiệp vụ đã xảy ra trong Domain.

Điểm quan trọng:

Event dùng thì quá khứ.

Ví dụ:

Đúng:
    
    
    NovelCreated
    NovelPublished
    ChapterAdded
    PaymentCompleted

Sai:
    
    
    CreateNovel
    PublishNovel
    AddChapter

Vì đó là Command.

* * *

# 3\. Command vs Event

Đây là phần rất quan trọng.

* * *

## Command

Là yêu cầu làm một việc.

Ví dụ:
    
    
    PublishNovelCommand

Ý nghĩa:

> Hãy publish truyện này.

* * *

## Event

Là thông báo việc đã xảy ra.

Ví dụ:
    
    
    NovelPublishedEvent

Ý nghĩa:

> Truyện đã được publish.

* * *

So sánh:

| Command| Event  
---|---|---  
Ý nghĩa| Yêu cầu| Thông báo  
Thì| Hiện tại/tương lai| Quá khứ  
Có thể thất bại| Có| Không  
Người xử lý| Một nơi| Nhiều nơi  
  
* * *

Ví dụ:
    
    
    Command:
    
    PublishNovel
    
    
            |
            v
    
    
    Domain
    
    
            |
            v
    
    
    Event:
    
    NovelPublished

* * *

# 4\. Domain Event thuộc Layer nào?

Domain Event thuộc:
    
    
    Domain Layer

vì nó biểu diễn một sự kiện nghiệp vụ.

* * *

Cấu trúc:
    
    
    domain/
    
        events/
    
            novel_created.py
            novel_published.py
            chapter_added.py

* * *

# 5\. Ví dụ Domain Event đơn giản
    
    
    from dataclasses import dataclass
    from datetime import datetime
    
    
    @dataclass
    class NovelPublished:
    
        novel_id: str
        published_at: datetime

* * *

Event chỉ chứa dữ liệu.

Không chứa:
    
    
    send_email()

* * *

Sai:
    
    
    class NovelPublished:
    
        def send_email():
            ...

* * *

Event chỉ nói:

"Điều gì đã xảy ra?"

* * *

# 6\. Aggregate phát sinh Domain Event

Ví dụ:

Novel Aggregate:
    
    
    class Novel:
    
    
        def __init__(
            self,
            id,
            title
        ):
            self.id = id
            self.title = title
            self.status = "draft"
            self.events = []
    
    
        def publish(self):
    
            if self.status == "published":
                raise Exception(
                    "Already published"
                )
    
    
            self.status = "published"
    
    
            self.events.append(
                NovelPublished(
                    self.id,
                    datetime.now()
                )
            )

* * *

Khi gọi:
    
    
    novel.publish()

Không chỉ đổi trạng thái.

Nó tạo event:
    
    
    NovelPublished

* * *

# 7\. Tại sao Event nằm trong Aggregate?

Vì Aggregate là nơi biết:

  * Rule nghiệp vụ. 
  * Khi nào trạng thái thay đổi hợp lệ. 



Ví dụ:

Không phải ai cũng được tạo:
    
    
    NovelPublished

* * *

Sai:
    
    
    event = NovelPublished(
        novel_id
    )

ở ngoài.

* * *

Đúng:
    
    
    novel.publish()

Aggregate quyết định.

* * *

# 8\. Event Dispatcher

Bây giờ có Event rồi.

Ai nhận Event?

Cần:
    
    
    Event Bus

* * *

Kiến trúc:
    
    
    Aggregate
    
       |
       |
    Domain Event
    
       |
       |
    Event Bus
    
       |
       +------------+
       |            |
       v            v
    
    Search      Notification
    

* * *

# 9\. Event Bus đơn giản bằng Python
    
    
    class EventBus:
    
    
        def __init__(self):
    
            self.handlers = {}
    
    
        def register(
            self,
            event_type,
            handler
        ):
    
            self.handlers.setdefault(
                event_type,
                []
            ).append(handler)
    
    
    
        def publish(
            self,
            event
        ):
    
            handlers = self.handlers.get(
                type(event),
                []
            )
    
    
            for handler in handlers:
    
                handler(event)

* * *

# 10\. Event Handler

Ví dụ:

Khi publish truyện:

Cập nhật Search Index.
    
    
    class UpdateSearchIndexHandler:
    
    
        def __call__(
            self,
            event
        ):
    
            print(
                "Update search:",
                event.novel_id
            )

* * *

Đăng ký:
    
    
    event_bus.register(
        NovelPublished,
        UpdateSearchIndexHandler()
    )

* * *

Khi event xảy ra:
    
    
    event_bus.publish(
        event
    )

* * *

Kết quả:
    
    
    Update search: abc123

* * *

# 11\. Domain Event trong Application Layer

Thông thường:

Aggregate tạo Event.

Application thu thập và publish.

Ví dụ:
    
    
    class PublishNovelUseCase:
    
    
        def execute(
            self,
            novel_id
        ):
    
            novel = (
                repository.get_by_id(
                    novel_id
                )
            )
    
    
            novel.publish()
    
    
            repository.save(
                novel
            )
    
    
            for event in novel.events:
    
                event_bus.publish(
                    event
                )

* * *

Luồng:
    
    
    Use Case
    
     |
     v
    
    Repository
    
     |
     v
    
    Novel Aggregate
    
     |
     v
    
    NovelPublished Event
    
     |
     v
    
    Event Bus
    
     |
     +---- Search
     |
     +---- Notification
     |
     +---- Statistics

* * *

# 12\. Domain Event trong App Cào Truyện

Đây là phần rất sát với dự án của bạn.

* * *

## Event: NovelCreated

Khi crawler tạo truyện mới.
    
    
    @dataclass
    class NovelCreated:
    
        novel_id: str
        source_id: str

Handler:
    
    
    NovelCreated
    
     |
     +--> Download Cover
     |
     +--> Create Search Index
     |
     +--> Notify Admin

* * *

## Event: ChapterAdded

Khi crawl thêm chapter.
    
    
    @dataclass
    class ChapterAdded:
    
        novel_id: str
        chapter_id: str

Handler:
    
    
    ChapterAdded
    
     |
     +--> Update Reading Cache
     |
     +--> Update Chapter Count

* * *

## Event: CrawlFinished

Crawler hoàn thành.
    
    
    @dataclass
    class CrawlFinished:
    
        source_id: str
        total: int

Handler:
    
    
    CrawlFinished
    
     |
     +--> Statistics
     |
     +--> Dashboard Update

* * *

# 13\. Domain Event và Plugin Architecture

Dự án crawler của bạn có thể dùng Event rất tốt.

Ví dụ:

Plugin:
    
    
    TruyenFullPlugin
    
           |
           |
     crawl()
    
           |
           v
    
    ChapterDownloaded

* * *

Các module khác không cần biết plugin nào:
    
    
    ChapterDownloaded
    
          |
          + Search
          |
          + Database
          |
          + UI Update

* * *

# 14\. Event giúp giảm Coupling

Không dùng Event:
    
    
    Crawler
    
     |
     + Database
     |
     + UI
     |
     + Notification

Crawler biết quá nhiều.

* * *

Dùng Event:
    
    
    Crawler
    
     |
     |
    ChapterDownloaded
    
     |
     + Database Handler
     |
     + UI Handler
     |
     + Notification Handler

* * *

Crawler chỉ biết:

"Tôi đã tải xong chapter."

* * *

# 15\. Domain Event vs Message Queue

Hai khái niệm liên quan nhưng khác nhau.

* * *

## Domain Event

Trong phạm vi ứng dụng:
    
    
    Python Process
    
    NovelPublished

* * *

## Message Queue

Giữa các hệ thống:
    
    
    Service A
    
       |
    
    RabbitMQ/Kafka
    
       |
    
    Service B

* * *

Sau này có thể kết hợp:
    
    
    Domain Event
    
          |
    
    Outbox Pattern
    
          |
    
    RabbitMQ
    
          |
    
    Other Service

* * *

# 16\. Event Sourcing (giới thiệu)

DDD nâng cao có:

# Event Sourcing

Thay vì lưu trạng thái:
    
    
    Novel
    
    status = published

Lưu lịch sử:
    
    
    NovelCreated
    
    ChapterAdded
    
    NovelPublished

Sau đó dựng lại trạng thái.

* * *

Ví dụ:
    
    
    Event 1:
    
    NovelCreated
    
    
    Event 2:
    
    ChapterAdded
    
    
    Event 3:
    
    NovelPublished

* * *

State hiện tại:
    
    
    Novel = Published

* * *

# 17\. Outbox Pattern (giới thiệu)

Một vấn đề:
    
    
    save_database()
    
    publish_event()

Nếu:

  * Database thành công. 
  * Event lỗi. 



Hệ thống sai trạng thái.

* * *

Outbox:
    
    
    Transaction
    
     + Novel
     + Event
    
           |
    
     Database
    
           |
    
     Event Publisher

* * *

Đây là pattern production rất quan trọng.

* * *

# 18\. Cấu trúc thư mục
    
    
    domain/
    
    ├── novels/
    │
    │   ├── entities/
    │   │
    │   ├── aggregates/
    │   │
    │   └── events/
    │
    │       ├── novel_created.py
    │       ├── novel_published.py
    │       └── chapter_added.py
    
    
    application/
    
    ├── use_cases/
    │
    └── event_handlers/
    
    
    infrastructure/
    
    ├── event_bus/
    │
    └── message_queue/

* * *

# 19\. Những lỗi thường gặp

## Lỗi 1: Event làm thay Command

Sai:
    
    
    NovelPublished()

để yêu cầu publish.

* * *

Đúng:
    
    
    novel.publish()

sau đó tạo:
    
    
    NovelPublished

* * *

## Lỗi 2: Event chứa logic

Sai:
    
    
    class NovelPublished:
    
        send_mail()

* * *

Event chỉ là dữ liệu.

* * *

## Lỗi 3: Dùng Event cho mọi thứ

Không cần:
    
    
    TitleChanged
    NameChanged
    VariableChanged

Event phải là business event quan trọng.

* * *

# 20\. Kiến trúc sau Buổi 13

Hiện tại chúng ta có:
    
    
    Presentation
    
            |
            v
    
    Application Layer
    
     + Use Case
     + DTO
     + Event Handler
    
            |
            v
    
    Domain Layer
    
     + Entity
     + Value Object
     + Aggregate
     + Repository Interface
     + Domain Service
     + Domain Event
    
            |
            v
    
    Infrastructure
    
     + Database
     + Event Bus
     + Message Queue

* * *

# Bài tập

## Bài 1

Thiết kế Event cho:

  1. Người dùng bookmark chapter. 
  2. Crawler tải xong truyện. 
  3. Admin xóa nguồn crawl. 



* * *

## Bài 2

Viết:
    
    
    @dataclass
    class ChapterAdded:

bao gồm:

  * chapter_id 
  * novel_id 
  * created_at 



* * *

## Bài 3

Thiết kế Event Flow:

Khi crawler thêm chapter:
    
    
    Crawler
       |
       ?
       |
    Search
    Notification
    Database
    UI

* * *

# Tổng kết Buổi 13

Cần nhớ:

✅ Domain Event biểu diễn việc đã xảy ra.  
✅ Event dùng thì quá khứ.  
✅ Aggregate là nơi phát sinh Event.  
✅ Event giảm coupling giữa các module.  
✅ Command khác Event.  
✅ Handler xử lý phản ứng sau Event.  
✅ Event rất phù hợp với hệ thống crawler/plugin.

* * *

Buổi tiếp theo theo roadmap:

# Buổi 14: Factory Pattern trong DDD (bản cập nhật)

Nội dung:

  * Vì sao không nên tạo Aggregate bằng constructor? 
  * Factory Method. 
  * Factory Object. 
  * Aggregate Factory. 
  * Factory kết hợp Dependency Injection. 
  * Áp dụng: 
    * `NovelFactory`
    * `CrawlerPluginFactory`
    * `SourceFactory` trong App Cào Truyện.

