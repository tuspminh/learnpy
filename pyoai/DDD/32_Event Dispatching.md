# DDD Deep Dive — Buổi 32

# Event Dispatching

Ở Buổi 31, ta đã có:

```text
Aggregate
   ↓
Domain Event
```

Ví dụ:

```text
story.add_chapter(chapter)
        ↓
   ChapterAdded
```

Nhưng câu hỏi tiếp theo là:

> **Ai nhận `ChapterAdded` và làm gì với nó?**

Đó là nhiệm vụ của **Event Dispatcher / Event Bus**.

---

# 1. Bức tranh tổng thể

Ta muốn:

```text
Aggregate
    │
    │ Domain Event
    ▼
Event Dispatcher
    │
    ├──────────────┐
    ▼              ▼
Handler A       Handler B
    │              │
    ▼              ▼
Search         Notification
```

Ví dụ:

```text
ChapterAdded
      │
      ├── SearchIndexHandler
      ├── StatisticsHandler
      └── NotificationHandler
```

Aggregate **không biết** các Handler này tồn tại.

---

# 2. Event Dispatcher là gì?

Event Dispatcher có nhiệm vụ:

> Nhận một Domain Event và tìm các Handler phù hợp để xử lý nó.

Ví dụ:

```python
dispatcher.dispatch(event)
```

Nếu:

```python
event = ChapterAdded(...)
```

Dispatcher tìm:

```text
ChapterAdded
      ↓
SearchIndexHandler
StatisticsHandler
NotificationHandler
```

rồi gọi từng handler.

---

# 3. Event Bus vs Event Dispatcher

Hai thuật ngữ này thường được dùng khá gần nhau.

Có thể hiểu đơn giản:

### Event Dispatcher

Tập trung vào:

```text
Event
 ↓
Handlers
```

### Event Bus

Là abstraction rộng hơn:

```text
publish
subscribe
dispatch
```

Trong hệ thống in-process nhỏ, chúng ta có thể dùng một class:

```python
EventBus
```

và nó thực hiện cả dispatching.

---

# 4. Event Handler

Handler là object/function phản ứng với một Event.

Ví dụ:

```python
class SearchIndexHandler:

    def handle(
        self,
        event: ChapterAdded,
    ):
        ...
```

Nó chỉ quan tâm:

```text
ChapterAdded
```

---

# 5. Một Event có nhiều Handler

Đây là điểm quan trọng:

```text
ChapterAdded
      │
      ├── Handler 1
      ├── Handler 2
      └── Handler 3
```

Không phải:

```text
ChapterAdded
      ↓
Một handler duy nhất
```

---

# 6. Event Handler Registry

Dispatcher cần biết:

```text
Event Type
     ↓
Handlers
```

Ví dụ:

```python
{
    ChapterAdded: [
        SearchIndexHandler(),
        StatisticsHandler(),
        NotificationHandler(),
    ]
}
```

---

# 7. Thiết kế đơn giản nhất

Ta bắt đầu bằng:

```python
from collections import defaultdict


class EventDispatcher:

    def __init__(self):
        self._handlers = defaultdict(list)
```

---

# 8. Register Handler

```python
def register(
    self,
    event_type,
    handler,
):
    self._handlers[event_type].append(
        handler
    )
```

Sử dụng:

```python
dispatcher.register(
    ChapterAdded,
    search_handler,
)
```

---

# 9. Register nhiều Handler

```python
dispatcher.register(
    ChapterAdded,
    search_handler,
)

dispatcher.register(
    ChapterAdded,
    statistics_handler,
)

dispatcher.register(
    ChapterAdded,
    notification_handler,
)
```

Kết quả:

```text
ChapterAdded
    │
    ├── search_handler
    ├── statistics_handler
    └── notification_handler
```

---

# 10. Dispatch

```python
def dispatch(
    self,
    event,
):

    event_type = type(event)

    handlers = self._handlers.get(
        event_type,
        [],
    )

    for handler in handlers:
        handler.handle(event)
```

Đây là phiên bản cơ bản nhất.

---

# 11. Full Dispatcher

```python
from collections import defaultdict


class EventDispatcher:

    def __init__(self):
        self._handlers = defaultdict(list)

    def register(
        self,
        event_type,
        handler,
    ):
        self._handlers[event_type].append(
            handler
        )

    def dispatch(
        self,
        event,
    ):

        event_type = type(event)

        handlers = self._handlers.get(
            event_type,
            [],
        )

        for handler in handlers:
            handler.handle(event)
```

---

# 12. Event Definition

Ta dùng Event từ Buổi 31:

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ChapterAdded:

    event_id: UUID
    occurred_at: datetime

    story_id: UUID
    chapter_id: UUID
    chapter_number: int
```

---

# 13. Handler

```python
class SearchIndexHandler:

    def handle(
        self,
        event: ChapterAdded,
    ):
        print(
            "Updating search index:",
            event.chapter_id,
        )
```

Statistics:

```python
class StatisticsHandler:

    def handle(
        self,
        event: ChapterAdded,
    ):
        print(
            "Updating statistics:",
            event.story_id,
        )
```

Notification:

```python
class NotificationHandler:

    def handle(
        self,
        event: ChapterAdded,
    ):
        print(
            "Sending notification:",
            event.story_id,
        )
```

---

# 14. Wiring

```python
dispatcher = EventDispatcher()

dispatcher.register(
    ChapterAdded,
    SearchIndexHandler(),
)

dispatcher.register(
    ChapterAdded,
    StatisticsHandler(),
)

dispatcher.register(
    ChapterAdded,
    NotificationHandler(),
)
```

---

# 15. Dispatch Event

```python
event = ChapterAdded(
    event_id=uuid4(),
    occurred_at=datetime.now(),

    story_id=story_id,
    chapter_id=chapter_id,
    chapter_number=10,
)

dispatcher.dispatch(event)
```

Kết quả:

```text
Updating search index: ...
Updating statistics: ...
Sending notification: ...
```

---

# 16. Aggregate không biết Dispatcher

Đây là nguyên tắc quan trọng.

Không làm:

```python
class Story:

    def add_chapter(self, chapter):

        ...

        dispatcher.dispatch(
            ChapterAdded(...)
        )
```

❌

Tại sao?

Vì Domain Entity bây giờ biết:

```text
Event Dispatcher
```

Domain bị coupling với application infrastructure.

---

# 17. Aggregate chỉ record Event

Đúng hơn:

```python
class Story:

    def add_chapter(self, chapter):

        ...

        self._record_event(
            ChapterAdded(...)
        )
```

Sau đó:

```text
Story
 ↓
pending events
```

Application layer quyết định khi nào dispatch.

---

# 18. Flow đúng

```text
Use Case
   │
   ▼
Aggregate
   │
   ├── modify state
   │
   └── record event
   │
   ▼
Repository
   │
   ▼
UnitOfWork
   │
   ▼
Event Dispatcher
   │
   ├── Handler
   ├── Handler
   └── Handler
```

Nhưng hãy chú ý:

> **Thời điểm dispatch trước hay sau commit là một vấn đề khác.**

Ta sẽ xử lý kỹ ở Buổi 34.

---

# 19. Tại sao không dispatch ngay?

Giả sử:

```text
Story
 ↓
ChapterAdded
 ↓
SearchIndexHandler
```

Search index đã update.

Nhưng sau đó:

```text
SQLite COMMIT
     ↓
❌ FAILED
```

Kết quả:

```text
Database
→ Chapter chưa tồn tại

Search index
→ Chapter đã tồn tại
```

Hệ thống không nhất quán.

Đây chính là vấn đề:

```text
Event timing
Transaction consistency
Outbox
```

---

# 20. Nhưng hôm nay chưa giải quyết

Ở Buổi 32, ta chỉ cần hiểu:

```text
Event
 ↓
Dispatcher
 ↓
Handler
```

Còn:

```text
commit
event
retry
outbox
```

sẽ được đào sâu ở:

```text
Buổi 34
Buổi 35
```

---

# 21. Handler có thể là function

Không nhất thiết phải class.

Ví dụ:

```python
def update_search_index(
    event: ChapterAdded,
):
    print(
        "Indexing:",
        event.chapter_id,
    )
```

Dispatcher có thể gọi:

```python
handler(event)
```

thay vì:

```python
handler.handle(event)
```

---

# 22. Function handler

Khi đó:

```python
class EventDispatcher:

    def register(
        self,
        event_type,
        handler,
    ):
        self._handlers[event_type].append(
            handler
        )

    def dispatch(self, event):

        for handler in self._handlers[
            type(event)
        ]:
            handler(event)
```

Đơn giản hơn.

---

# 23. Class Handler hay Function?

### Function

Phù hợp:

```text
logic nhỏ
stateless
```

Ví dụ:

```python
def log_chapter_added(event):
    ...
```

### Class

Phù hợp:

```text
có dependencies
có configuration
cần nhiều method
```

Ví dụ:

```python
class SearchIndexHandler:

    def __init__(
        self,
        search_index,
    ):
        self.search_index = search_index
```

---

# 24. Handler có Dependency

Ví dụ Search Engine:

```python
class SearchIndexHandler:

    def __init__(
        self,
        search_index,
    ):
        self.search_index = search_index

    def handle(
        self,
        event: ChapterAdded,
    ):

        self.search_index.add(
            story_id=event.story_id,
            chapter_id=event.chapter_id,
        )
```

Handler không tự tạo:

```python
Elasticsearch(...)
```

mà nhận dependency.

---

# 25. Dependency Injection

Composition Root:

```python
search_index = ElasticsearchSearchIndex(...)

search_handler = SearchIndexHandler(
    search_index
)

dispatcher.register(
    ChapterAdded,
    search_handler,
)
```

Kiến trúc:

```text
Infrastructure
     ↓
SearchIndex implementation
     ↓
SearchIndexHandler
     ↓
Event Dispatcher
```

---

# 26. Một Event có thể đăng ký động

Ví dụ:

```python
dispatcher.register(
    StoryCreated,
    create_catalog_entry,
)

dispatcher.register(
    StoryCreated,
    notify_admin,
)
```

Sau này thêm:

```python
dispatcher.register(
    StoryCreated,
    warm_cache,
)
```

không cần sửa `StoryCreated`.

Đây là một dạng **Open/Closed Principle** rất tự nhiên.

---

# 27. Event Dispatcher không nên chứa business logic

Không làm:

```python
class EventDispatcher:

    def dispatch(self, event):

        if isinstance(event, ChapterAdded):
            ...
```

rồi:

```python
if ...
elif ...
elif ...
elif ...
```

Đó sẽ trở thành:

```text
God Dispatcher
```

Dispatcher chỉ nên:

```text
lookup
 ↓
invoke
```

---

# 28. Không hard-code handler

Không nên:

```python
def dispatch(event):

    if isinstance(event, ChapterAdded):
        SearchIndexHandler().handle(event)
        StatisticsHandler().handle(event)
        NotificationHandler().handle(event)
```

Vì mỗi lần thêm handler phải sửa Dispatcher.

Tốt hơn:

```text
Registry
 ↓
handlers
```

---

# 29. Generic Dispatcher

Có thể dùng generic typing:

```python
from typing import Protocol, TypeVar, Generic


E = TypeVar("E")


class EventHandler(
    Protocol,
    Generic[E],
):

    def handle(self, event: E) -> None:
        ...
```

Sau đó:

```python
class ChapterAddedHandler:

    def handle(
        self,
        event: ChapterAdded,
    ) -> None:
        ...
```

Python type checker có thể hỗ trợ kiểm tra tốt hơn.

---

# 30. Event registration bằng decorator

Ta có thể tạo:

```python
def event_handler(event_type):

    def decorator(func):

        func._event_type = event_type

        return func

    return decorator
```

Sử dụng:

```python
@event_handler(ChapterAdded)
def update_search(event):
    ...
```

Nhưng **không nên vội dùng decorator** khi kiến trúc cơ bản chưa rõ.

Explicit registration thường dễ debug hơn:

```python
dispatcher.register(
    ChapterAdded,
    update_search,
)
```

---

# 31. In-process Event Bus

Ta có thể đổi tên:

```python
EventDispatcher
```

thành:

```python
InMemoryEventBus
```

Ví dụ API:

```python
bus.subscribe(
    ChapterAdded,
    search_handler,
)

bus.publish(event)
```

Flow:

```text
publish(event)
     ↓
lookup subscribers
     ↓
invoke
```

---

# 32. Dispatcher vs Message Broker

Đừng nhầm:

### In-process Event Bus

```text
Python process
     ↓
EventBus
```

Ví dụ:

```text
EventDispatcher
```

### Message Broker

```text
Process A
    ↓
Redis / RabbitMQ / Kafka
    ↓
Process B
```

Broker có:

```text
network
persistence
retry
consumer groups
delivery semantics
```

Event Dispatcher đơn giản hơn rất nhiều.

---

# 33. Khi nào dùng In-process?

Rất phù hợp khi:

```text
project nhỏ
monolith
modular monolith
ít worker
```

Ví dụ app đọc truyện:

```text
PySide6
    ↓
Application
    ↓
Domain Event
    ↓
In-process Handler
```

Không cần Kafka.

---

# 34. Khi nào cần Message Broker?

Khi cần:

```text
multiple processes
background workers
retry
distributed processing
high throughput
```

Ví dụ:

```text
Crawler Worker
      ↓
Redis
      ↓
Notification Worker
```

Nhưng đó là bước sau.

---

# 35. Event Dispatcher và Aggregate

Aggregate:

```python
story.add_chapter(chapter)
```

sau đó:

```python
events = story.collect_events()
```

Application:

```python
for event in events:
    dispatcher.dispatch(event)
```

Đây là implementation đơn giản.

---

# 36. Nhưng có vấn đề

Giả sử có:

```text
Story Aggregate
ChapterAdded
```

Use Case:

```python
story.add_chapter(chapter)

repo.save(story)

events = story.collect_events()

dispatcher.dispatch(events)
```

Nếu:

```text
repo.save()
```

thành công nhưng:

```text
dispatcher.dispatch()
```

thất bại?

Event có thể mất.

Nếu dispatch trước commit:

```text
dispatch
 ↓
commit fails
```

thì Handler đã phản ứng với một transaction chưa commit.

Đây chính là lý do **Domain Event + Transaction** rất quan trọng.

---

# 37. Error handling cơ bản

Giả sử:

```text
ChapterAdded
   ├── SearchHandler     ✅
   ├── StatisticsHandler ❌
   └── Notification      ?
```

Nếu handler 2 fail thì có tiếp tục handler 3 không?

Có nhiều strategy.

### Strategy A

Dừng ngay:

```text
A ✅
B ❌
C không chạy
```

### Strategy B

Tiếp tục:

```text
A ✅
B ❌
C ✅
```

Không có đáp án tuyệt đối.

Production architecture phải xác định rõ semantics.

---

# 38. Đừng nuốt Exception

Không nên:

```python
try:
    handler.handle(event)
except Exception:
    pass
```

❌

Bạn vừa làm mất lỗi.

Tối thiểu:

```python
try:
    handler.handle(event)
except Exception:
    logger.exception(
        "Event handler failed"
    )
    raise
```

---

# 39. Handler nên idempotent

Đây là khái niệm cực kỳ quan trọng cho những buổi sau.

Ví dụ event:

```text
ChapterAdded(event_id=123)
```

được xử lý 2 lần.

Nếu handler:

```text
send notification
```

thì user nhận 2 notification.

Ta cần thiết kế handler có khả năng:

```text
same event
→ process safely more than once
```

Đây gọi là:

> **Idempotency**

Đặc biệt quan trọng khi có:

```text
retry
worker
outbox
message broker
```

---

# 40. Event ID

Vì vậy Event nên có:

```python
@dataclass(frozen=True)
class DomainEvent:

    event_id: UUID
    occurred_at: datetime
```

Ví dụ:

```text
event_id
= 4c7...
```

Handler/consumer có thể dùng ID này để deduplicate.

---

# 41. Kiến trúc Buổi 32

Hiện tại:

```text
┌──────────────┐
│   Aggregate  │
└──────┬───────┘
       │
       │ record
       ▼
┌──────────────┐
│ Domain Event │
└──────┬───────┘
       │
       │ dispatch
       ▼
┌──────────────────┐
│ Event Dispatcher │
└────────┬─────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
 Handler Handler Handler
```

---

# 42. Project structure

Sau Buổi 32 có thể tổ chức:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── events.py
    │   │
    │   └── shared/
    │       └── events.py
    │
    ├── application/
    │   ├── events/
    │   │   ├── dispatcher.py
    │   │   └── handlers/
    │   │       ├── search.py
    │   │       ├── statistics.py
    │   │       └── notification.py
    │   │
    │   └── story/
    │       └── add_chapter.py
    │
    └── infrastructure/
        ├── search/
        ├── notification/
        └── database/
```

---

# 43. Flow thực tế

Ví dụ `AddChapterUseCase`:

```python
def execute(self, command):

    with self.uow:

        story = self.uow.stories.get(
            command.story_id
        )

        chapter = Chapter.create(...)

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        self.uow.commit()

        events = story.collect_events()

        for event in events:
            self.dispatcher.dispatch(event)
```

**Lưu ý:** Đây chỉ là implementation để minh họa dispatching. Việc đặt dispatch **sau commit** vẫn chưa giải quyết hoàn toàn bài toán mất event nếu process chết giữa `commit()` và `dispatch()`. Đó là vấn đề Outbox ở Buổi 35.

---

# 44. Một kiến trúc tốt hơn về mặt trách nhiệm

Ta có:

```text
Aggregate
    │
    │ records
    ▼
Domain Events
    │
    ▼
Unit of Work
    │
    │ commit
    ▼
Database
    │
    ▼
Dispatcher
    │
    ▼
Handlers
```

Về sau:

```text
Aggregate
    ↓
Domain Event
    ↓
Unit of Work
    ↓
Outbox
    ↓
Worker
    ↓
Handler
```

Đây là hướng production.

---

# 45. Những gì Event Dispatcher KHÔNG làm

Dispatcher không nên:

```text
❌ Business rule
❌ SQL
❌ HTTP
❌ Domain decision
❌ Transaction policy phức tạp
❌ Retry policy phức tạp
```

Nó chủ yếu:

```text
✅ Registry
✅ Find handlers
✅ Invoke handlers
```

---

# 46. Mental model

Nhớ:

```text
Domain Event
→ "Điều gì đã xảy ra?"

Event Dispatcher
→ "Ai cần biết?"

Event Handler
→ "Tôi phải làm gì khi biết?"
```

Ví dụ:

```text
ChapterAdded
→ SearchIndexHandler
→ index chapter
```

---

# 47. Toàn bộ chuỗi DDD hiện tại

Bạn đã đi tới:

```text
Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Business Behavior
   ↓
Domain Event
   ↓
Event Dispatcher
   ↓
Event Handler
```

Đây là một pipeline cực kỳ quan trọng:

```text
Request
   ↓
Decision
   ↓
State Change
   ↓
Fact
   ↓
Reaction
```

---

# 48. Bài tập Buổi 32

Hãy tự xây:

```text
InMemoryEventBus
```

API:

```python
bus.subscribe(
    ChapterAdded,
    search_handler,
)

bus.subscribe(
    ChapterAdded,
    statistics_handler,
)

bus.subscribe(
    StoryPublished,
    notification_handler,
)
```

và:

```python
bus.publish(
    ChapterAdded(...)
)
```

Kỳ vọng:

```text
ChapterAdded
    ↓
SearchHandler
StatisticsHandler
```

Trong khi:

```text
StoryPublished
    ↓
NotificationHandler
```

không được chạy `ChapterAdded` handler.

---

# 49. Bài tập nâng cao

Thiết kế flow:

```text
AddChapterUseCase
        ↓
Story.add_chapter()
        ↓
ChapterAdded
        ↓
UnitOfWork
        ↓
EventDispatcher
        ↓
┌───────────────┬────────────────┐
▼               ▼                ▼
Search          Statistics       Notification
```

Sau đó trả lời 3 câu:

1. **Nếu `SearchIndexHandler` throw exception thì `StatisticsHandler` có chạy tiếp không?**
2. **Nếu database commit thất bại thì `ChapterAdded` có được dispatch không?**
3. **Nếu process chết sau commit nhưng trước dispatch thì chuyện gì xảy ra?**

Câu **3** chính là vấn đề dẫn thẳng tới:

```text
Aggregate
   ↓
Domain Event
   ↓
Transaction
   ↓
Outbox
```

ở **Buổi 34–35**.

### Tóm tắt Buổi 32

```text
Event
  ↓
Dispatcher
  ↓
Handler
```

và nguyên tắc quan trọng:

> **Aggregate chỉ tạo/record Domain Event; nó không gọi Handler. Dispatcher chịu trách nhiệm định tuyến Event đến các Handler phù hợp.**

Buổi tiếp theo **Buổi 33 — Event Handler** sẽ đi sâu vào cách thiết kế Handler, dependency injection, nhiều handler cho một event, handler chain, error handling, idempotency và ví dụ `ChapterAdded → Search / Statistics / Notification`.
