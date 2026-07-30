# Domain-Driven Design Deep Dive

# Buổi 12: Domain Event — Sự kiện nghiệp vụ trong Domain

Sau buổi 11 chúng ta đã học:

  * Entity → đối tượng có Identity 
  * Value Object → đối tượng theo giá trị 
  * Aggregate → nhóm object có ranh giới 
  * Aggregate Root → cửa vào bảo vệ Aggregate 
  * Repository → lưu trữ Aggregate 
  * Domain Service → nghiệp vụ liên quan nhiều object 



Nhưng còn một vấn đề:

> Khi một việc quan trọng xảy ra trong Domain, làm sao thông báo cho các phần khác của hệ thống?

Ví dụ:

  * Một truyện mới được crawl. 
  * Một chapter mới được xuất bản. 
  * Một người dùng đọc xong truyện. 
  * Một đơn hàng đã thanh toán. 



Câu trả lời:

# Domain Event

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ Buổi 6: Entity

✅ Buổi 7: Value Object

✅ Buổi 8: Aggregate

✅ Buổi 9: Aggregate Root

✅ Buổi 10: Repository

✅ Buổi 11: Domain Service

✅ **Buổi 12: Domain Event**

⬜ Buổi 13: Factory Pattern trong DDD

⬜ Buổi 14: Specification Pattern

⬜ Buổi 15: CQRS trong DDD

* * *

# 1\. Domain Event là gì?

Định nghĩa:

> Domain Event là một sự kiện có ý nghĩa nghiệp vụ đã xảy ra trong Domain.

Điểm quan trọng:

Event luôn ở quá khứ.

Ví dụ:

Sai:
    
    
    CreateNovel

Đây là command.

Đúng:
    
    
    NovelCreated

Đây là event.

* * *

# 2\. Command vs Event

Đây là phần rất quan trọng.

## Command

Là yêu cầu:
    
    
    PublishChapter

Nghĩa:

> Hãy xuất bản chapter này.

* * *

## Event

Là sự thật:
    
    
    ChapterPublished

Nghĩa:

> Chapter đã được xuất bản.

* * *

So sánh:

Command| Event  
---|---  
Mệnh lệnh| Sự kiện  
Có thể thất bại| Đã xảy ra  
Hiện tại/tương lai| Quá khứ  
"Làm đi"| "Đã xảy ra"  
  
* * *

Ví dụ:
    
    
    User:
    
    "Thanh toán đơn hàng"
    
            |
            |
            v
    
    Command
    
    PayOrder
    
    
            |
            |
            v
    
    Domain xử lý
    
    
            |
            |
            v
    
    Event
    
    OrderPaid

* * *

# 3\. Tại sao cần Domain Event?

Không có Event:

Ví dụ App Cào Truyện.

Crawler:
    
    
    class Crawler:
    
        def crawl(self):
    
            save_database()
    
            update_search()
    
            update_library()
    
            send_notification()

* * *

Vấn đề:

Crawler biết quá nhiều.

Coupling cao.

* * *

Nếu thêm:

  * Recommendation 
  * Statistics 
  * AI Summary 



Crawler lại phải sửa.

* * *

DDD dùng Event:
    
    
    Crawler
    
       |
       |
    NovelCreated Event
    
       |
       |
    +-------------+
    |             |
    Search     Library
    |
    Recommendation
    |
    Statistics

Crawler không cần biết ai nghe.

* * *

# 4\. Domain Event là ngôn ngữ nghiệp vụ

Ví dụ:

Không nên:
    
    
    DataUpdatedEvent

Quá kỹ thuật.

* * *

Nên:
    
    
    NovelPublished
    ChapterAdded
    ReadingCompleted
    PaymentConfirmed

Đây là ngôn ngữ mà Business hiểu.

* * *

# 5\. Cấu trúc một Domain Event

Một Event thường có:

  * Event name 
  * Aggregate ID 
  * Data liên quan 
  * Timestamp 
  * Event ID 



Ví dụ:
    
    
    from dataclasses import dataclass
    from datetime import datetime
    import uuid
    
    
    @dataclass(frozen=True)
    class NovelCreated:
    
        event_id: str
        novel_id: int
        title: str
        occurred_at: datetime

* * *

Sử dụng:
    
    
    event = NovelCreated(
        event_id=str(uuid.uuid4()),
        novel_id=1,
        title="Đấu Phá Thương Khung",
        occurred_at=datetime.now()
    )

* * *

# 6\. Domain Event thuộc Domain Layer

Cấu trúc:
    
    
    domain/
    
        events/
    
            novel_created.py
            chapter_published.py
            reading_completed.py

* * *

Không đặt:
    
    
    infrastructure/events

vì Event là ngôn ngữ nghiệp vụ.

* * *

# 7\. Aggregate phát sinh Event

Ví dụ:

Novel Aggregate.

Rule:

Khi publish truyện:
    
    
    NovelPublished

* * *

Code:
    
    
    class Novel:
    
        def __init__(
            self,
            novel_id,
            title
        ):
            self.id = novel_id
            self.title = title
            self.events = []
    
    
        def publish(self):
    
            self.status = "published"
    
            self.events.append(
                NovelPublished(
                    self.id
                )
            )

* * *

Aggregate ghi nhận:

"Điều gì đã xảy ra?"

* * *

# 8\. Event không thực thi hành động

Sai:
    
    
    class NovelPublished:
    
        def send_email():
            ...

Event chỉ là dữ liệu.

* * *

Đúng:
    
    
    NovelPublished
    
           |
           |
           v
    
    NotificationHandler
    
           |
           |
           v
    
    Send Email

* * *

# 9\. Event Handler

Event Handler nhận Event.

Ví dụ:
    
    
    class SearchIndexHandler:
    
    
        def handle(
            self,
            event: NovelCreated
        ):
    
            print(
                "Index novel",
                event.novel_id
            )

* * *

Khi Event xảy ra:
    
    
    handler.handle(event)

* * *

# 10\. Event Bus

Khi có nhiều Handler:
    
    
    NovelCreated
    
        |
        |
     Event Bus
    
        |
        +------ SearchHandler
    
        |
        +------ LibraryHandler
    
        |
        +------ RecommendationHandler

* * *

Event Bus chịu trách nhiệm:

  * Nhận Event. 
  * Tìm Listener. 
  * Gọi Listener. 



* * *

# 11\. Tự viết Event Bus bằng Python

Ví dụ đơn giản:
    
    
    class EventBus:
    
    
        def __init__(self):
    
            self.handlers = {}
    
    
        def subscribe(
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
    
                handler.handle(event)

* * *

Đăng ký:
    
    
    bus = EventBus()
    
    
    bus.subscribe(
        NovelCreated,
        SearchHandler()
    )

* * *

Publish:
    
    
    bus.publish(
        NovelCreated(...)
    )

* * *

# 12\. Áp dụng vào App Cào Truyện

Đây là kiến trúc rất phù hợp.

* * *

## Crawler Context

Khi crawl xong:
    
    
    NovelCreated(
        novel_id=10,
        title="Truyện A"
    )

* * *

Event Bus:
    
    
    NovelCreated
    
          |
          |
    +-----+-----+------+
    
    Search
    
    Library
    
    Recommendation
    
    Statistics

* * *

# 13\. Ví dụ hoàn chỉnh

## Event
    
    
    @dataclass(frozen=True)
    class ChapterPublished:
    
        chapter_id: int
        novel_id: int
        number: int

* * *

## Chapter Aggregate
    
    
    class Chapter:
    
    
        def __init__(
            self,
            chapter_id,
            number
        ):
    
            self.id = chapter_id
            self.number = number
            self.events = []
    
    
        def publish(self):
    
            self.events.append(
                ChapterPublished(
                    chapter_id=self.id,
                    novel_id=1,
                    number=self.number
                )
            )

* * *

## Search Handler
    
    
    class SearchHandler:
    
    
        def handle(
            self,
            event
        ):
    
            print(
                f"Index chapter {event.number}"
            )

* * *

## Notification Handler
    
    
    class NotificationHandler:
    
    
        def handle(
            self,
            event
        ):
    
            print(
                "Notify readers"
            )

* * *

Kết quả:
    
    
    Chapter.publish()
    
            |
    
    ChapterPublished
    
            |
    
    +----------------+
    |                |
    Search       Notification

* * *

# 14\. Domain Event vs Message Queue

Rất hay bị nhầm.

## Domain Event

Ở Domain:
    
    
    NovelCreated

Ý nghĩa nghiệp vụ.

* * *

## Message Queue

Ở Infrastructure:

Ví dụ:

  * RabbitMQ 
  * Kafka 
  * Redis Stream 



Dùng để vận chuyển.

* * *

Có thể:
    
    
    Domain Event
    
          |
    
    Event Publisher
    
          |
    
    RabbitMQ
    
          |
    
    Consumer

* * *

Domain không cần biết RabbitMQ.

* * *

# 15\. Synchronous vs Asynchronous Event

## Đồng bộ
    
    
    event_bus.publish(event)

Handler chạy ngay.

Ưu:

  * Đơn giản. 



Nhược:

  * Chậm. 



* * *

## Bất đồng bộ
    
    
    Domain Event
    
        |
    
    Queue
    
        |
    
    Worker

Ưu:

  * Scale tốt. 



Nhược:

  * Phức tạp hơn. 



* * *

# 16\. Domain Event và Transaction

Một vấn đề:
    
    
    order.pay()
    
    publish(OrderPaid)

Nếu:

Database save thất bại?

Nhưng Event đã gửi.

Sai trạng thái.

* * *

Giải pháp:

# Transactional Outbox Pattern

* * *

Luồng:
    
    
    Order
    
     |
     |
     Save Order
    
     |
     |
     Save Event vào Outbox Table
    
     |
     |
     Commit Transaction
    
    
    Worker đọc Outbox
    
     |
     |
     Publish Event

* * *

Ví dụ:

Database:
    
    
    orders
    
    outbox_events

* * *

Đây là pattern rất quan trọng trong hệ thống lớn.

* * *

# 17\. Domain Event trong Clean Architecture

Luồng đầy đủ:
    
    
                    User
    
                     |
                     v
    
               Application Service
    
                     |
                     v
    
                Aggregate Root
    
                     |
                     v
    
              Domain Event
    
                     |
                     v
    
                 Event Bus
    
                     |
           +---------+----------+
    
           Search             Email
    
           Statistics         Recommendation

* * *

# 18\. Thiết kế Event cho App Cào Truyện

Tôi đề xuất:

## Source Context
    
    
    SourceAdded
    
    SourceDisabled

* * *

## Crawler Context
    
    
    CrawlStarted
    
    CrawlCompleted
    
    NovelCreated
    
    ChapterCreated
    
    ChapterUpdated

* * *

## Reader Context
    
    
    BookmarkCreated
    
    ReadingStarted
    
    ReadingCompleted

* * *

## Recommendation Context
    
    
    RecommendationGenerated

* * *

# 19\. Những lỗi thường gặp

## Lỗi 1: Event chứa logic

Sai:
    
    
    class OrderPaid:
    
        send_email()

* * *

Event chỉ là data.

* * *

## Lỗi 2: Event đặt tên hiện tại

Sai:
    
    
    UpdateNovel

Đúng:
    
    
    NovelUpdated

* * *

## Lỗi 3: Event quá kỹ thuật

Sai:
    
    
    DatabaseRowInserted

Đúng:
    
    
    NovelCreated

* * *

## Lỗi 4: Dùng Event để thay thế mọi thứ

Không phải:

Mọi method đều tạo Event.

Chỉ tạo Event khi có ý nghĩa nghiệp vụ.

* * *

# 20\. Tổng hợp kiến trúc DDD hiện tại

Sau 12 buổi:
    
    
                        Application
    
                             |
    
                        Domain Layer
    
            ---------------------------------
    
            Entity
    
            Value Object
    
            Aggregate
    
            Aggregate Root
    
            Domain Service
    
            Domain Event
    
            Repository Interface
    
    
                             |
    
                    Infrastructure
    
    
            Database
    
            Message Queue
    
            External API

* * *

# Bài tập

## Bài 1

Thiết kế Domain Event cho:

App Cào Truyện:

  1. Crawl hoàn thành. 
  2. Truyện mới được thêm. 
  3. Chapter mới xuất bản. 
  4. Người dùng đọc xong truyện. 



* * *

## Bài 2

Viết Event Bus đơn giản:

Yêu cầu:
    
    
    subscribe()
    
    publish()

Hỗ trợ:
    
    
    NovelCreated
    
    ChapterPublished

* * *

## Bài 3

Thiết kế luồng:

Khi crawler phát hiện chapter mới:
    
    
    Crawler
    
     ?
    
    Search
    
     ?
    
    Notification
    
     ?
    
    Reader

Sử dụng Domain Event.

* * *

# Tổng kết Buổi 12

Cần nhớ:

  * Domain Event biểu diễn một sự thật nghiệp vụ đã xảy ra. 
  * Event dùng để giảm coupling giữa các Aggregate/Bounded Context. 
  * Aggregate Root thường là nơi phát sinh Event. 
  * Event chỉ chứa dữ liệu, không chứa logic. 
  * Domain Event khác Message Queue. 
  * Event là nền tảng cho kiến trúc Event-Driven và Microservices. 



* * *

Buổi tiếp theo (**Buổi 13**) chúng ta sẽ học **Factory Pattern trong DDD** :

  * Vì sao không nên dùng constructor trực tiếp? 
  * Factory khác Factory Method thông thường thế nào? 
  * Tạo Aggregate phức tạp bằng Factory. 
  * Ví dụ `NovelFactory`, `OrderFactory`, `CrawlerPluginFactory` trong hệ thống cào truyện.

