# DDD Deep Dive — Buổi 31

# Domain Event

Đây là bước chuyển rất quan trọng từ **DDD tactical cơ bản** sang kiến trúc có khả năng mở rộng.

Ta đã có:

```text
Entity
Value Object
Aggregate
Repository
Unit of Work
Domain Service
Application Service
Use Case
```

Bây giờ thêm:

```text
Domain Event
```

Mục tiêu của buổi này:

```text
Aggregate
   ↓
Domain Event
   ↓
Application xử lý Event
```

---

# 1. Domain Event là gì?

**Domain Event là một sự kiện nghiệp vụ đã xảy ra trong Domain.**

Ví dụ:

```text
StoryCreated
ChapterAdded
StoryPublished
CrawlerStarted
CrawlerCompleted
ReadingProgressUpdated
```

Điểm quan trọng nhất:

> **Domain Event mô tả một điều đã xảy ra.**

Ví dụ:

```text
ChapterAdded
```

nghĩa là:

> Một Chapter đã được thêm vào Story.

Không phải:

```text
AddChapter
```

vì `AddChapter` mang ý nghĩa **yêu cầu thực hiện hành động**.

---

# 2. Event vs Command

Đây là distinction cực kỳ quan trọng.

## Command

Command:

> "Hãy làm việc này."

Ví dụ:

```text
AddChapter
PublishStory
StartCrawler
CompleteCrawler
```

Thường dùng:

```python
AddChapterCommand(...)
```

---

## Event

Event:

> "Việc này đã xảy ra."

Ví dụ:

```text
ChapterAdded
StoryPublished
CrawlerStarted
CrawlerCompleted
```

---

# 3. So sánh

```text
Command
──────────────
"Do this"
   ↓
AddChapterCommand
   ↓
Use Case
```

Trong khi:

```text
Event
──────────────
"This happened"
   ↓
ChapterAdded
   ↓
Handlers
```

---

# 4. Command có thể bị từ chối

Ví dụ:

```text
PublishStoryCommand
```

Có thể xảy ra:

```text
Command
   ↓
Story.publish()
   ↓
❌ StoryAlreadyPublished
```

Không có event:

```text
StoryPublished
```

---

# 5. Event chỉ xuất hiện khi hành động thành công

Ví dụ:

```python
story.publish()
```

Nếu thành công:

```text
StoryPublished
```

Nếu thất bại:

```text
StoryAlreadyPublished
```

thì không có:

```text
StoryPublished
```

---

# 6. Event dùng past tense

Nên:

```text
StoryCreated
ChapterAdded
StoryPublished
CrawlerStarted
CrawlerCompleted
```

Không nên:

```text
CreateStory
AddChapter
PublishStory
StartCrawler
```

Những tên này phù hợp với **Command**.

---

# 7. Tại sao Domain Event hữu ích?

Không có Domain Event:

```text
ChapterAdded
    ↓
Use Case
    ├── update search
    ├── update statistics
    ├── send notification
    └── ...
```

Use Case ngày càng phình to.

Ví dụ:

```python
class AddChapterUseCase:

    def execute(self, command):

        story.add_chapter(chapter)

        update_search_index(story)

        update_statistics(story)

        send_notification(story)

        update_cache(story)

        ...
```

Đây là dấu hiệu coupling tăng.

---

# 8. Với Domain Event

Ta có:

```text
AddChapterUseCase
       ↓
story.add_chapter()
       ↓
ChapterAdded
       ↓
      Event
       │
       ├── SearchIndexHandler
       ├── StatisticsHandler
       ├── NotificationHandler
       └── CacheHandler
```

Use Case không cần biết tất cả consumer.

---

# 9. Domain Event không phải log

Ví dụ:

```python
logger.info(
    "Chapter added"
)
```

đây chỉ là logging.

Domain Event có semantic:

```python
ChapterAdded(...)
```

Nó là một **domain fact** có thể được xử lý bởi hệ thống.

---

# 10. Domain Event không phải Database Event

Không nên nhầm:

```text
SQLite trigger
```

với:

```text
Domain Event
```

Database event:

> Có thay đổi xảy ra trong database.

Domain Event:

> Có một sự kiện nghiệp vụ xảy ra.

Ví dụ:

```text
INSERT INTO chapters
```

không nhất thiết có nghĩa:

```text
ChapterAdded
```

Domain có thể có nhiều logic trước khi xác định rằng Chapter thực sự được thêm hợp lệ.

---

# 11. Event phải immutable

Một Domain Event mô tả **quá khứ**.

Ví dụ:

```python
ChapterAdded(
    story_id="story-1",
    chapter_id="chapter-10",
    number=10,
)
```

Sau khi tạo event, không nên:

```python
event.number = 11
```

Vì:

> Event mô tả một fact đã xảy ra.

---

# 12. Python implementation

Ta có thể dùng:

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
```

Base class:

```python
@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime
```

`frozen=True` giúp event immutable.

---

# 13. StoryCreated

```python
@dataclass(frozen=True)
class StoryCreated(DomainEvent):

    story_id: UUID
    title: str
    source_id: str
```

Ví dụ:

```python
event = StoryCreated(
    occurred_at=datetime.now(),
    story_id=story.id.value,
    title=story.title.value,
    source_id=story.source_id,
)
```

---

# 14. ChapterAdded

```python
@dataclass(frozen=True)
class ChapterAdded(DomainEvent):

    story_id: UUID
    chapter_id: UUID
    chapter_number: int
```

Event này không cần chứa toàn bộ `Chapter`.

Thông thường chỉ chứa dữ liệu cần thiết để consumer xử lý.

---

# 15. CrawlerStarted

```python
@dataclass(frozen=True)
class CrawlerStarted(DomainEvent):

    job_id: UUID
    source_id: str
    started_at: datetime
```

---

# 16. CrawlerCompleted

```python
@dataclass(frozen=True)
class CrawlerCompleted(DomainEvent):

    job_id: UUID
    source_id: str
    chapter_count: int
    completed_at: datetime
```

---

# 17. Event không phải Entity

`Story`:

```text
Entity
identity
lifecycle
behavior
```

`ChapterAdded`:

```text
Event
immutable fact
occurred_at
```

Ví dụ:

```text
Story
id = 123
```

có lifecycle.

Nhưng:

```text
ChapterAdded
```

là một fact:

> Chapter 10 đã được thêm.

---

# 18. Event không có lifecycle như Entity

Không làm:

```python
event.update()
event.delete()
```

Thông thường Event:

```text
created
→ stored/dispatched
→ consumed
```

---

# 19. Domain Event nằm ở đâu?

Ví dụ:

```text
domain/
└── events/
    ├── base.py
    ├── story.py
    ├── chapter.py
    └── crawler.py
```

Hoặc tổ chức theo bounded context:

```text
domain/
└── story/
    ├── events.py
    ├── entities.py
    └── value_objects.py
```

Cả hai đều được.

Tôi thường thích **co-locate event với domain concept** khi project chưa quá lớn.

---

# 20. Aggregate tạo Event

Đây là điểm quan trọng.

Ví dụ `Story`:

```python
class Story:

    def __init__(self, ...):

        self._events = []
```

Khi tạo Story:

```python
@classmethod
def create(
    cls,
    title: StoryTitle,
    source_id: str,
):

    story = cls(
        story_id=StoryId.generate(),
        title=title,
        source_id=source_id,
    )

    story._events.append(
        StoryCreated(
            occurred_at=datetime.now(),
            story_id=story.id.value,
            title=title.value,
            source_id=source_id,
        )
    )

    return story
```

---

# 21. Aggregate tạo Event vì sao?

Vì Aggregate biết:

```text
"Business action này đã thực sự xảy ra."
```

Ví dụ:

```python
story.publish()
```

`Story` biết:

```text
Publish thành công
```

nên nó có thể tạo:

```text
StoryPublished
```

---

# 22. Ví dụ `add_chapter`

```python
def add_chapter(
    self,
    chapter: Chapter,
):

    if self.has_chapter_number(
        chapter.number
    ):
        raise ChapterAlreadyExists()

    self._chapters.append(chapter)

    self._events.append(
        ChapterAdded(
            occurred_at=datetime.now(),
            story_id=self.id.value,
            chapter_id=chapter.id.value,
            chapter_number=chapter.number.value,
        )
    )
```

Flow:

```text
story.add_chapter()
        │
        ├── validate
        │
        ├── modify state
        │
        └── create ChapterAdded
```

---

# 23. Nhưng Event chưa được dispatch

Đây là một điểm rất quan trọng.

Sau:

```python
story.add_chapter(chapter)
```

ta có:

```text
Story
 ├── state changed
 │
 └── pending events
      └── ChapterAdded
```

Event chưa nhất thiết được gửi ngay.

Đây là vấn đề chúng ta sẽ đào sâu ở:

```text
Buổi 32 — Event Dispatching
```

và đặc biệt:

```text
Buổi 34 — Domain Event + Transaction
Buổi 35 — Outbox Pattern
```

---

# 24. Aggregate cần expose events

Không cho bên ngoài:

```python
story._events.append(...)
```

Thay vào đó:

```python
class AggregateRoot:

    def __init__(self):
        self._domain_events = []

    def _record_event(
        self,
        event: DomainEvent,
    ):
        self._domain_events.append(event)

    def collect_events(self):
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

---

# 25. Sử dụng

```python
story.add_chapter(chapter)

events = story.collect_events()
```

Kết quả:

```text
[
    ChapterAdded(...)
]
```

---

# 26. Tại sao `collect_events()`?

Để Aggregate kiểm soát event lifecycle.

Trước:

```text
_events
    ↓
[Event A, Event B]
```

Sau:

```python
events = story.collect_events()
```

thì:

```text
Aggregate
    ↓
_events = []
```

Các event đã được lấy ra để Application/Event Dispatcher xử lý.

---

# 27. Một Aggregate có thể tạo nhiều Event

Ví dụ:

```python
story.publish()
```

có thể tạo:

```text
StoryPublished
```

Sau đó Application có thể gây ra những event khác.

Một command:

```text
AddChapter
```

có thể tạo:

```text
ChapterAdded
```

Không nên suy nghĩ:

```text
1 Command = 1 Event
```

Đây không phải quy tắc bắt buộc.

---

# 28. Event có nên chứa Entity?

Thông thường **không nên**:

```python
ChapterAdded(
    chapter=chapter
)
```

vì như vậy event bị coupling với Entity.

Thường tốt hơn:

```python
ChapterAdded(
    story_id=...,
    chapter_id=...,
    chapter_number=...,
)
```

Event mang dữ liệu cần thiết.

---

# 29. Event nên chứa bao nhiêu dữ liệu?

Nguyên tắc:

> Chứa đủ information để consumer hiểu event và thực hiện công việc của nó, nhưng tránh nhúng cả Domain Model vào event.

Ví dụ:

```python
ChapterAdded(
    story_id=...,
    chapter_id=...,
    chapter_number=...,
)
```

Search handler có thể cần:

```text
story_id
chapter_id
```

Statistics handler cần:

```text
story_id
chapter_number
```

---

# 30. Event vs DTO

Hai thứ đều có thể là:

```python
@dataclass(frozen=True)
```

nhưng semantic khác nhau.

### DTO

Dùng truyền data:

```text
Use Case
 ↓
Result DTO
 ↓
Interface
```

### Domain Event

Mô tả:

```text
Something happened
```

---

# 31. Event vs Command vs DTO

Hãy nhớ:

```text
Command
→ Request

DTO
→ Data transfer

Event
→ Fact
```

Ví dụ:

```text
AddChapterCommand
        ↓
"Please add chapter 10"
```

Domain:

```text
ChapterAdded
        ↓
"Chapter 10 has been added"
```

Result:

```text
AddChapterResult
        ↓
"Here is the result of your request"
```

---

# 32. Ví dụ hoàn chỉnh

Command:

```python
@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    number: int
    title: str
    content: str
```

Use Case:

```python
def execute(
    self,
    command: AddChapterCommand,
):

    with self.uow:

        story = self.uow.stories.get(
            StoryId(UUID(command.story_id))
        )

        chapter = Chapter.create(
            number=ChapterNumber(
                command.number
            ),
            title=ChapterTitle(
                command.title
            ),
            content=command.content,
        )

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        self.uow.commit()

        events = story.collect_events()
```

Ở đây:

```text
Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Domain Event
```

---

# 33. Tách Event khỏi Use Case

Một thiết kế tốt hơn:

```python
story.add_chapter(chapter)

self.uow.stories.save(story)

self.uow.commit()
```

Unit of Work có thể thu thập events từ Aggregate.

Ví dụ:

```text
UnitOfWork
    │
    ├── Repository
    │
    └── Domain Events
```

Sau đó:

```text
commit
  ↓
dispatch events
```

Nhưng **thời điểm dispatch chính xác** là vấn đề rất quan trọng.

Chúng ta chưa quyết định ở buổi này.

---

# 34. Event Handler là gì?

Giả sử:

```text
ChapterAdded
```

Có 3 consumer:

```text
ChapterAdded
     │
     ├── SearchIndexHandler
     ├── StatisticsHandler
     └── NotificationHandler
```

Mỗi handler thực hiện một reaction.

Ví dụ:

```python
class SearchIndexHandler:

    def handle(
        self,
        event: ChapterAdded,
    ):
        ...
```

Đây là nội dung chính của **Buổi 33**.

---

# 35. Event giúp giảm coupling

Không có Event:

```text
AddChapterUseCase
 │
 ├── Search
 ├── Notification
 ├── Statistics
 ├── Cache
 └── ...
```

Coupling:

```text
HIGH
```

Có Event:

```text
AddChapterUseCase
       │
       ▼
ChapterAdded
       │
       ├── Search
       ├── Notification
       ├── Statistics
       └── Cache
```

Use Case chỉ quan tâm:

```text
Chapter đã được thêm.
```

---

# 36. Nhưng Event không phải "magic"

Một lỗi thường gặp là nghĩ:

```text
Event
 ↓
mọi thứ tự động giải quyết
```

Không.

Ta vẫn cần:

```text
Event Dispatcher
Event Handler
Error handling
Transaction strategy
Retry
Idempotency
Outbox
```

Các vấn đề này sẽ xuất hiện ở những buổi tiếp theo.

---

# 37. In-process Domain Event

Ở giai đoạn đầu, Event có thể chỉ chạy trong process:

```text
Python process
    │
    ▼
Event Dispatcher
    │
    ├── Handler A
    ├── Handler B
    └── Handler C
```

Không cần:

```text
Kafka
RabbitMQ
Redis Streams
```

Đây gọi là **in-process event**.

---

# 38. Sau này có thể chuyển thành asynchronous

Kiến trúc có thể tiến hóa:

### Level 1

```text
Aggregate
 ↓
Event
 ↓
Handler
```

### Level 2

```text
Aggregate
 ↓
Event Bus
 ↓
Handler
```

### Level 3

```text
Aggregate
 ↓
Outbox
 ↓
Worker
 ↓
Message Broker
 ↓
External System
```

Buổi 35 sẽ đi tới Level 3.

---

# 39. Ví dụ hệ thống đọc truyện

Khi crawler lấy được chapter:

```text
Crawler
   ↓
CrawlerCompleted
```

Handler có thể:

```text
CrawlerCompleted
      │
      ├── Update Story
      ├── Update Statistics
      ├── Update Search Index
      └── Notify User
```

---

# 40. Một Event có thể có nhiều Handler

Ví dụ:

```text
ChapterAdded
```

### Handler 1

```text
UpdateSearchIndex
```

### Handler 2

```text
UpdateStoryStatistics
```

### Handler 3

```text
NotifySubscriber
```

### Handler 4

```text
UpdateCache
```

Aggregate không cần biết những handler này tồn tại.

Đây chính là sức mạnh của Domain Event.

---

# 41. Domain Event không nên phụ thuộc Infrastructure

Không:

```python
@dataclass(frozen=True)
class ChapterAdded:

    redis_client: Redis
    smtp: SMTP
```

❌

Event phải thuộc Domain.

Nó không biết:

```text
Redis
SMTP
SQLite
httpx
PySide6
```

---

# 42. Event cũng không nên tự xử lý

Không:

```python
class ChapterAdded:

    def handle(self):
        redis.set(...)
        send_email(...)
```

❌

Event chỉ là:

```text
fact
```

Handler mới thực hiện reaction.

---

# 43. Một cách thiết kế tốt

```text
domain/
    events.py

application/
    event_handlers/
        chapter_added.py

infrastructure/
    search/
    notification/
```

Ví dụ:

```text
Domain
   │
   ▼
ChapterAdded
   │
   ▼
Application Handler
   │
   ├── Search Port
   └── Notification Port
          │
          ▼
Infrastructure
```

---

# 44. Domain Event và Bounded Context

Điều này sẽ trở nên cực kỳ hữu ích khi project lớn.

Ví dụ:

```text
Reading Context
```

phát ra:

```text
ChapterAdded
```

Catalog Context có thể quan tâm:

```text
ChapterAdded
```

Notification Context cũng có thể quan tâm.

Nhưng mỗi Context có cách hiểu riêng.

```text
Reading Context
→ ChapterAdded

Search Context
→ IndexChapter

Notification Context
→ NotifyNewChapter
```

Event có thể trở thành cầu nối giữa các context.

---

# 45. Nhưng đừng biến mọi thứ thành Event

Không phải mọi method đều cần event.

Ví dụ:

```python
story.change_title(...)
```

không nhất thiết phải tạo:

```text
StoryTitleChanged
```

nếu không có consumer/business requirement cần nó.

Hãy tạo Event khi:

> Một business fact có ý nghĩa với phần khác của hệ thống.

---

# 46. Quy tắc nhận diện Event

Hỏi:

> "Nếu chuyện này xảy ra, có thành phần nào khác cần biết không?"

Nếu:

```text
Có
```

→ Domain Event là ứng viên tốt.

Ví dụ:

```text
ChapterAdded
```

Search cần biết.

Notification cần biết.

Statistics cần biết.

→ Event rất hợp lý.

---

# 47. Event naming

Tốt:

```text
StoryCreated
ChapterAdded
StoryPublished
CrawlerStarted
CrawlerCompleted
ReadingProgressUpdated
```

Tránh:

```text
StoryEvent1
ChapterEvent
ProcessChapter
DoSomething
```

Tên Event phải nói được:

> **Điều gì đã xảy ra?**

---

# 48. Event có timestamp

Thông thường:

```python
@dataclass(frozen=True)
class ChapterAdded(DomainEvent):

    occurred_at: datetime
    story_id: UUID
    chapter_id: UUID
    chapter_number: int
```

`occurred_at` hữu ích cho:

```text
logging
debugging
audit
ordering
outbox
```

---

# 49. Event ID

Khi đi tới production, nên cân nhắc:

```python
@dataclass(frozen=True)
class DomainEvent:

    event_id: UUID
    occurred_at: datetime
```

Ví dụ:

```python
event_id=uuid4()
```

Event ID đặc biệt quan trọng khi cần:

```text
idempotency
deduplication
outbox
retry
```

Buổi 35 chúng ta sẽ dùng nó rất nhiều.

---

# 50. Kiến trúc cuối buổi

Hiện tại ta có:

```text
                    Use Case
                       │
                       ▼
                  Aggregate
                       │
                 business action
                       │
                       ▼
                Domain Event
                       │
                       ▼
                Event Dispatcher
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Handler   Handler   Handler
```

Nhưng ở Buổi 31, ta mới tập trung vào:

```text
Aggregate
    ↓
Domain Event
```

---

# 51. Mental model quan trọng nhất

Hãy nhớ 3 câu:

```text
Command
→ "Hãy làm X."

Entity/Aggregate
→ "Tôi quyết định X có được phép hay không."

Event
→ "X đã xảy ra."
```

Ví dụ hệ thống đọc truyện:

```text
AddChapterCommand
        ↓
Story.add_chapter()
        ↓
ChapterAdded
```

Đây là flow DDD rất đẹp.

---

# 52. Bài tập Buổi 31

Thiết kế 4 Domain Event cho hệ thống đọc truyện:

```text
StoryCreated
ChapterAdded
StoryPublished
CrawlerCompleted
```

Mỗi Event hãy xác định:

```text
1. event_id
2. occurred_at
3. các field cần thiết
```

Ví dụ:

```python
@dataclass(frozen=True)
class ChapterAdded(DomainEvent):

    event_id: UUID
    occurred_at: datetime

    story_id: UUID
    chapter_id: UUID
    chapter_number: int
```

Sau đó trả lời câu hỏi:

> Khi `story.add_chapter(chapter)` thành công, **Aggregate có nên gọi trực tiếp `SearchIndexHandler` không?**

Đáp án là **không**.

Đúng hơn:

```text
Story
 ↓
ChapterAdded
 ↓
Event Dispatcher
 ↓
SearchIndexHandler
```

Và **Buổi 32** chúng ta sẽ xây chính phần còn thiếu:

```text
Event Dispatcher
       │
       ├── register()
       ├── dispatch()
       └── Handler
```

từ một dispatcher đơn giản trong Python đến **in-process Event Bus**.
