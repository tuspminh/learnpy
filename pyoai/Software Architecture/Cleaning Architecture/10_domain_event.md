# Clean Architecture Deep Dive

# Buổi 10: Domain Event - Giao tiếp giữa các Aggregate mà không tạo Coupling

Đây là buổi cuối cùng của **Phase 1: Domain Modeling**.

Sau buổi này, bạn sẽ thấy vì sao các hệ thống lớn như:

  * Amazon 
  * Netflix 
  * Uber 
  * GitHub 
  * Shopify 



đều sử dụng Event rất nhiều.

Đặc biệt với dự án **app cào truyện bằng Python** của bạn, Domain Event sẽ là nền tảng để kết hợp với:

  * Celery 
  * Dramatiq 
  * Redis 
  * Plugin Architecture 
  * Event Bus 



* * *

# Roadmap tổng thể khóa học

Đây là roadmap đầy đủ mà chúng ta sẽ đi.
    
    
    PHASE 1 — Domain Modeling (Đã học)
    
    Buổi 1  Giới thiệu Clean Architecture
    Buổi 2  Coupling & Cohesion
    Buổi 3  SOLID trong Clean Architecture
    Buổi 4  Dependency Rule
    Buổi 5  Architectural Boundary
    Buổi 6  Entity
    Buổi 7  Value Object
    Buổi 8  Domain Service
    Buổi 9  Aggregate & Aggregate Root
    Buổi 10 Domain Event   ← Hôm nay

Sau đó chúng ta sẽ bước sang phần thực chiến.
    
    
    PHASE 2 — Application Layer
    
    Buổi 11 DTO
    Buổi 12 Use Case
    Buổi 13 Input Port
    Buổi 14 Output Port
    Buổi 15 Repository Pattern
    Buổi 16 Unit of Work
    Buổi 17 Dependency Injection
    Buổi 18 CQRS cơ bản
    Buổi 19 Validation Strategy
    Buổi 20 Transaction

* * *
    
    
    PHASE 3 — Infrastructure
    
    Buổi 21 ORM
    Buổi 22 SQLite Adapter
    Buổi 23 HTTP Adapter
    Buổi 24 Cache Adapter
    Buổi 25 Plugin Adapter
    Buổi 26 Message Queue
    Buổi 27 Logging
    Buổi 28 Configuration
    Buổi 29 Background Worker
    Buổi 30 Infrastructure Testing

* * *
    
    
    PHASE 4 — Presentation
    
    Buổi 31 CLI
    Buổi 32 PySide6
    Buổi 33 REST API
    Buổi 34 Presenter
    Buổi 35 Controller
    Buổi 36 ViewModel

* * *
    
    
    PHASE 5 — Thực chiến
    
    Buổi 37-60
    
    Xây dựng hoàn chỉnh
    
    Story Crawler Platform
    
    theo đúng Clean Architecture.

* * *

# Chúng ta đã có gì?

Hiện nay Domain gồm:
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Value Object
    
    ↓
    
    Domain Service
    
    ↓
    
    Aggregate

Còn thiếu một thứ.

Làm sao để các Aggregate nói chuyện với nhau?

* * *

# Ví dụ

Giả sử.

Story được publish.
    
    
    story.publish()

Sau khi publish.

Cần làm tiếp:

  * Gửi email 
  * Xóa cache 
  * Tạo log 
  * Cập nhật search index 
  * Thông báo websocket 
  * Thông báo plugin 
  * Thêm vào recommendation 



Nếu viết.
    
    
    class Story:
    
        def publish(self):
    
            self.status = "published"
    
            send_email()
    
            redis.delete()
    
            websocket.send()
    
            logger.info()
    
            celery.delay()

Entity biết quá nhiều.

Sai.

* * *

# Một cách khác

Viết.
    
    
    class PublishStoryUseCase:
    
        def execute(self):
    
            story.publish()
    
            email.send()
    
            redis.clear()
    
            websocket.send()
    
            recommendation.update()

Lúc đầu.

Ổn.

Sau vài năm.
    
    
    PublishStoryUseCase
    
    ↓
    
    3000 dòng

God UseCase.

* * *

# Domain Event sinh ra để giải quyết

Ý tưởng.

Story chỉ nói.
    
    
    "Tôi đã publish."

Còn ai muốn làm gì.

Tự đăng ký.

* * *

# Domain Event là gì?

Định nghĩa.

> Domain Event là một sự kiện đã xảy ra trong Domain.

Ví dụ.
    
    
    StoryPublished
    
    ChapterAdded
    
    StoryArchived
    
    StoryCompleted
    
    UserRegistered
    
    BookBorrowed

Lưu ý.

Đây là:

> Đã xảy ra.

Không phải:
    
    
    PublishStoryCommand

* * *

# Event khác Command

Command.
    
    
    PublishStory

Nghĩa là.

"Hãy publish."

* * *

Event.
    
    
    StoryPublished

Nghĩa là.

"Đã publish."

Khác nhau hoàn toàn.

* * *

# Event đầu tiên
    
    
    from dataclasses import dataclass
    from datetime import datetime
    
    
    @dataclass(frozen=True)
    class StoryPublished:
    
        story_id: int
    
        published_at: datetime

Đây là Domain Event.

* * *

# Entity tạo Event
    
    
    class Story:
    
        def publish(self):
    
            self.is_published = True

Thêm.
    
    
    self.events.append(
    
        StoryPublished(...)
    )

Entity không gửi Event.

Chỉ tạo Event.

* * *

# Base Entity

Thường.
    
    
    class Entity:
    
        def __init__(self):
    
            self._events = []

Có.
    
    
    def add_event(self, event):
    
        self._events.append(event)

Có.
    
    
    def pull_events(self):
    
        ...

Đây là pattern rất phổ biến.

* * *

# Ví dụ hoàn chỉnh
    
    
    class Story:
    
        def publish(self):
    
            self.is_published = True
    
            self.add_event(
    
                StoryPublished(
    
                    self.id,
    
                    datetime.now()
                )
            )

Entity dừng ở đây.

Không gửi Email.

* * *

# UseCase

UseCase.
    
    
    story.publish()
    
    repo.save(story)
    
    bus.publish(
    
        story.pull_events()
    )

UseCase chỉ publish Event.

* * *

# Event Bus

Event đi đâu?
    
    
    Story
    
    ↓
    
    UseCase
    
    ↓
    
    Event Bus
    
    ↓
    
    Handlers

* * *

# Event Handler

Ví dụ.
    
    
    class EmailHandler:
    
        def handle(
    
            self,
    
            event
        ):
    
            ...

* * *

Một Handler khác.
    
    
    class CacheHandler:
    
        def handle(
    
            self,
    
            event
        ):
    
            ...

* * *

Một Handler khác.
    
    
    class LoggerHandler:
    
        def handle(
    
            self,
    
            event
        ):
    
            ...

Không ai biết nhau.

* * *

# Luồng
    
    
    Story.publish()
    
    ↓
    
    StoryPublished Event
    
    ↓
    
    EventBus
    
    ↓
    
    EmailHandler
    
    ↓
    
    CacheHandler
    
    ↓
    
    LoggerHandler
    
    ↓
    
    SearchHandler

Muốn thêm.

Analytics.

Chỉ thêm Handler.

Không sửa Story.

* * *

# Ví dụ app cào truyện

Story vừa tải xong.

Event.
    
    
    StoryDownloaded

Handler.
    
    
    SaveSQLite
    
    UpdateSearchIndex
    
    GenerateEPUB
    
    NotifyGUI
    
    UpdateStatistics
    
    Recommendation

Story không biết.

* * *

# Một Event khác
    
    
    @dataclass(frozen=True)
    class ChapterAdded:
    
        story_id: int
    
        chapter_number: int

Story.
    
    
    def add_chapter(...):
    
        ...
    
        self.add_event(
    
            ChapterAdded(...)
        )

* * *

# Event Handler

Ví dụ.
    
    
    class UpdateProgress:
    
        def handle(
    
            self,
    
            event
        ):
    
            ...

* * *

Ví dụ.
    
    
    class NotifyPlugin:
    
        def handle(
    
            self,
    
            event
        ):
    
            ...

* * *

# Event không trả dữ liệu

Sai.
    
    
    x = event.handle(...)

Event không giống function.

Event chỉ.
    
    
    Fire
    
    ↓
    
    Forget

* * *

# Event có nhiều Listener

Ví dụ.
    
    
    StoryPublished
    
    ↓
    
    Email
    
    ↓
    
    Redis
    
    ↓
    
    Search
    
    ↓
    
    Analytics
    
    ↓
    
    Plugin
    
    ↓
    
    GUI

Một Event.

Nhiều Handler.

* * *

# Event trong Celery

Thay vì.
    
    
    email.send()

Handler.
    
    
    celery.send_email.delay(...)

Rất đẹp.

* * *

# Event trong Dramatiq
    
    
    handler
    
    ↓
    
    dramatiq.actor.send(...)

* * *

# Event trong Redis

Handler.
    
    
    StoryPublished
    
    ↓
    
    Redis Pub/Sub

* * *

# Event trong Plugin

Plugin.
    
    
    Plugin A
    
    Plugin B
    
    Plugin C

Đăng ký.
    
    
    StoryPublished

Không cần sửa Core.

* * *

# Event Bus đơn giản
    
    
    class EventBus:
    
        def __init__(self):
    
            self.handlers = {}

Đăng ký.
    
    
    def subscribe(
    
        event,
    
        handler
    ):

Publish.
    
    
    def publish(
    
        event
    ):

Đây là Observer Pattern.

* * *

# Domain Event vs Integration Event

Đây là điểm rất nhiều tài liệu bỏ qua.

## Domain Event

Chỉ tồn tại bên trong Domain.

Ví dụ.
    
    
    StoryPublished

* * *

## Integration Event

Gửi ra ngoài.

Ví dụ.
    
    
    RabbitMQ
    
    Kafka
    
    Redis
    
    Webhook

Thường.
    
    
    Domain Event
    
    ↓
    
    Integration Event

* * *

# Thiết kế trong app cào truyện
    
    
    domain/
    
    events/
    
    ├── story_published.py
    
    ├── chapter_added.py
    
    ├── story_completed.py
    
    ├── plugin_installed.py
    
    └── crawl_finished.py

Application.
    
    
    application/
    
    event_bus/
    
    handlers/

Infrastructure.
    
    
    Redis
    
    Celery
    
    Dramatiq

* * *

# Những sai lầm phổ biến

## Sai 1

Entity gửi Email.

Sai.

* * *

## Sai 2

Entity gọi Celery.

Sai.

* * *

## Sai 3

Entity gọi Redis.

Sai.

* * *

## Sai 4

Event chứa Business Logic.

Sai.

Event chỉ là dữ liệu.

* * *

## Sai 5

Event Handler sửa Entity trực tiếp.

Không nên.

Nếu cần thay đổi Domain, hãy thông qua UseCase hoặc một transaction phù hợp để giữ tính nhất quán.

* * *

# Mô hình hoàn chỉnh Domain Layer
    
    
                    Aggregate Root
    
                          │
    
            ┌─────────────┴─────────────┐
    
            │                           │
    
        Entity                     Value Object
    
            │
    
            ▼
    
    Business Rule
    
            │
    
            ▼
    
    Domain Service
    
            │
    
            ▼
    
    Generate Domain Event

Sau đó.
    
    
    UseCase
    
    ↓
    
    Repository
    
    ↓
    
    Commit Transaction
    
    ↓
    
    Publish Event
    
    ↓
    
    Handlers

Đây là một điểm rất quan trọng: **Domain Event chỉ nên được phát ra sau khi transaction thành công**. Nếu publish trước khi lưu thành công, bạn có thể gửi email hoặc cập nhật cache cho một thay đổi thực tế chưa tồn tại trong database.

* * *

# Checklist

Một Domain Event tốt:

  * Mô tả điều **đã xảy ra**. 
  * Immutable (`frozen=True`). 
  * Chỉ chứa dữ liệu cần thiết. 
  * Không có Business Logic. 
  * Không biết Email, Redis, Celery, GUI. 
  * Có thể có nhiều Handler. 
  * Được publish sau khi transaction thành công. 



* * *

# Bài tập

## Bài 1

Thiết kế các Domain Event cho app cào truyện:

  * `StoryCreated`
  * `StoryDownloaded`
  * `StoryCompleted`
  * `StoryPublished`
  * `ChapterAdded`
  * `PluginInstalled`



Mỗi Event chỉ chứa các trường dữ liệu cần thiết.

* * *

## Bài 2

Thiết kế một `EventBus` đơn giản hỗ trợ:

  * `subscribe(event_type, handler)`
  * `publish(event)`
  * Một Event có thể được nhiều Handler xử lý. 



Không cần tích hợp Celery hay Redis.

* * *

## Bài 3

Với chức năng "tải truyện", hãy liệt kê:

  * Những Event nào sẽ phát sinh? 
  * Những Handler nào sẽ lắng nghe? 
  * Handler nào nên chạy đồng bộ? 
  * Handler nào nên chuyển sang Celery/Dramatiq chạy nền? 



* * *

# Kết thúc Phase 1

Đến đây bạn đã hoàn thành **toàn bộ Domain Layer** :

  * ✅ Buổi 1: Clean Architecture Overview 
  * ✅ Buổi 2: Coupling & Cohesion 
  * ✅ Buổi 3: SOLID 
  * ✅ Buổi 4: Dependency Rule 
  * ✅ Buổi 5: Architectural Boundary 
  * ✅ Buổi 6: Entity 
  * ✅ Buổi 7: Value Object 
  * ✅ Buổi 8: Domain Service 
  * ✅ Buổi 9: Aggregate & Aggregate Root 
  * ✅ Buổi 10: Domain Event 



Bạn đã có nền tảng để thiết kế một Domain Model mạnh, nhất quán và dễ mở rộng.

* * *

# Roadmap tiếp theo (Phase 2)

Từ **Buổi 11** , chúng ta sẽ chuyển sang **Application Layer** và đi sâu vào cách biến Domain thành một ứng dụng hoàn chỉnh:
    
    
    PHASE 2 — Application Layer
    
    Buổi 11 DTO (Input/Output Models)
    Buổi 12 Use Case (Application Service)
    Buổi 13 Input Port
    Buổi 14 Output Port
    Buổi 15 Repository Pattern (Ports & Adapters)
    Buổi 16 Unit of Work
    Buổi 17 Dependency Injection
    Buổi 18 CQRS cơ bản
    Buổi 19 Validation Strategy
    Buổi 20 Transaction Management

Đây là giai đoạn chúng ta sẽ bắt đầu xây dựng **bộ khung hoàn chỉnh cho ứng dụng cào truyện** , nơi Domain Layer vừa học sẽ được kết nối với Repository, Plugin, SQLite, PySide6 và các thành phần Infrastructure theo đúng tinh thần của Clean Architecture.

