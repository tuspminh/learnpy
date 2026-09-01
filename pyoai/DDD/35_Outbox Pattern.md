# DDD Deep Dive — Buổi 35

# Outbox Pattern

Đây là một trong những buổi quan trọng nhất của phần **Domain Event**.

Sau Buổi 34, ta đã thấy vấn đề:

```text
Aggregate
   ↓
Domain Event
   ↓
???
   ↓
External System
```

Nếu dispatch event trực tiếp, có thể **mất event** hoặc **side effect xảy ra nhưng transaction rollback**.

Outbox giải quyết vấn đề đó bằng cách:

```text
Aggregate
    ↓
Domain Event
    ↓
Outbox
    ↓
COMMIT
    ↓
Worker
    ↓
Event Handler
    ↓
External System
```

---

# 1. Outbox Pattern là gì?

**Outbox Pattern** là kỹ thuật lưu Domain Event vào một bảng `outbox` **trong cùng database transaction với Aggregate**.

Ví dụ:

```text
SQLite Transaction
┌──────────────────────────────┐
│                              │
│ Story                        │
│ Chapter                      │
│ OutboxEvent                  │
│                              │
└──────────────┬───────────────┘
               │
             COMMIT
               │
               ▼
             Outbox
               │
               ▼
             Worker
```

Điểm quan trọng nhất:

> **Aggregate state và Outbox Event được commit cùng nhau.**

---

# 2. Vấn đề mà Outbox giải quyết

Không có Outbox:

```text
BEGIN
 ↓
Save Chapter
 ↓
COMMIT
 ↓
💥 process crash
 ↓
Dispatch Event
```

Event không được dispatch.

Database:

```text
Chapter = exists
```

Event:

```text
lost
```

---

Có Outbox:

```text
BEGIN
 ↓
Save Chapter
 ↓
Save Outbox Event
 ↓
COMMIT
 ↓
💥 process crash
```

Database vẫn có:

```text
Chapter
Outbox Event
```

Worker khởi động lại:

```text
Outbox
 ↓
pending event
 ↓
process
```

Event không bị mất.

---

# 3. Kiến trúc tổng thể

Hãy nhớ architecture này:

```text
                 APPLICATION
                      │
                      ▼
                ┌───────────┐
                │ Aggregate │
                └─────┬─────┘
                      │
                Domain Event
                      │
                      ▼
              ┌───────────────┐
              │ Unit of Work  │
              └───────┬───────┘
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
          Aggregate          Outbox
              │                │
              └───────┬────────┘
                      │
                    COMMIT
                      │
                      ▼
                   Worker
                      │
                      ▼
               Event Handler
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Search      Notify      Statistics
```

---

# 4. Thiết kế Outbox Table

Bắt đầu đơn giản:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    processed_at TEXT
);
```

Ý nghĩa:

| Column         | Ý nghĩa              |
| -------------- | -------------------- |
| `id`           | Event ID             |
| `event_type`   | Loại Event           |
| `payload`      | Dữ liệu Event        |
| `occurred_at`  | Event xảy ra lúc nào |
| `processed_at` | Đã xử lý lúc nào     |

---

# 5. Ví dụ dữ liệu

Giả sử:

```text
ChapterAdded
```

Outbox:

```text
id:
evt-001

event_type:
ChapterAdded

payload:
{
    "story_id": "story-1",
    "chapter_id": "chapter-10",
    "chapter_number": 10
}
```

Database:

```text
outbox
──────────────────────────────────────────────
evt-001 | ChapterAdded | {...} | 2026-08-31
```

---

# 6. Domain Event

Trước tiên xây Event:

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

`frozen=True` giúp Event immutable.

---

# 7. Event có thể có Interface chung

Ta có thể tạo:

```python
from abc import ABC


class DomainEvent(ABC):
    pass
```

Sau đó:

```python
@dataclass(frozen=True)
class ChapterAdded(DomainEvent):

    event_id: UUID
    occurred_at: datetime
    story_id: UUID
    chapter_id: UUID
    chapter_number: int
```

---

# 8. Aggregate lưu Domain Events

Ví dụ:

```python
class Story:

    def __init__(self, story_id):
        self.id = story_id
        self._events = []

    def add_chapter(self, chapter):

        # business rules...

        self._events.append(
            ChapterAdded(
                event_id=uuid4(),
                occurred_at=datetime.now(),
                story_id=self.id,
                chapter_id=chapter.id,
                chapter_number=chapter.number,
            )
        )

    def collect_events(self):
        events = self._events.copy()
        self._events.clear()
        return events
```

Aggregate:

```text
Story
 ├── state
 └── pending domain events
```

---

# 9. Tại sao Aggregate không tự ghi Outbox?

Không nên:

```python
class Story:

    def add_chapter(self, chapter):

        ...

        sqlite.execute(
            "INSERT INTO outbox ..."
        )
```

Vì Domain đang biết:

```text
SQLite
SQL
Outbox table
Persistence
```

→ vi phạm Persistence Ignorance.

Aggregate chỉ nên biết:

```text
"I produced ChapterAdded."
```

Application/Unit of Work quyết định:

```text
"Event này được persistence như thế nào?"
```

---

# 10. Outbox Repository

Ta định nghĩa interface:

```python
from typing import Protocol


class OutboxRepository(Protocol):

    def add(self, event: DomainEvent) -> None:
        ...

    def get_pending(self, limit: int = 100):
        ...

    def mark_processed(self, event_id):
        ...
```

Domain/Application không cần biết SQLite cụ thể.

---

# 11. SQLite Outbox Repository

Infrastructure:

```python
class SQLiteOutboxRepository:

    def __init__(self, conn):
        self._conn = conn

    def add(self, event):
        self._conn.execute(
            """
            INSERT INTO outbox (
                id,
                event_type,
                payload,
                occurred_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(event.event_id),
                type(event).__name__,
                serialize_event(event),
                event.occurred_at.isoformat(),
            ),
        )
```

Điểm quan trọng:

```text
SQLiteOutboxRepository
```

chỉ sử dụng **connection hiện tại**.

Nó không tự:

```python
conn.commit()
```

---

# 12. Tại sao không commit trong Repository?

Vì:

```text
Repository
```

không sở hữu transaction.

Transaction thuộc:

```text
Unit of Work
```

Sai:

```python
def add(self, event):
    self.conn.execute(...)
    self.conn.commit()
```

Đúng:

```text
Repository
 ↓
execute SQL

UnitOfWork
 ↓
commit
```

---

# 13. Unit of Work

Ta có:

```python
class SQLiteUnitOfWork:

    def __init__(self, conn):
        self.conn = conn

        self.stories = SQLiteStoryRepository(
            conn
        )

        self.outbox = SQLiteOutboxRepository(
            conn
        )

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
```

---

# 14. AddChapterUseCase

Flow:

```python
class AddChapterUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, command):

        story = self.uow.stories.get(
            command.story_id
        )

        chapter = Chapter.create(
            ...
        )

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        for event in story.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()
```

Đây chính là phần quan trọng nhất.

---

# 15. Transaction thực tế

Database nhìn thấy:

```sql
BEGIN;

UPDATE stories
SET ...
WHERE id = ?;

INSERT INTO chapters (...);

INSERT INTO outbox (
    id,
    event_type,
    payload,
    occurred_at
)
VALUES (...);

COMMIT;
```

Tất cả nằm trong **một transaction**.

---

# 16. Nếu Chapter save thất bại

Ví dụ:

```text
BEGIN
 ↓
Save Story
 ↓
Save Chapter ❌
 ↓
ROLLBACK
```

Outbox cũng rollback.

Kết quả:

```text
Story       unchanged
Chapter     not created
Outbox      no event
```

Đúng.

---

# 17. Nếu Outbox insert thất bại

```text
BEGIN
 ↓
Save Story       ✅
 ↓
Save Chapter     ✅
 ↓
Save Outbox      ❌
 ↓
ROLLBACK
```

Kết quả:

```text
Story      rollback
Chapter    rollback
Outbox     rollback
```

Đây là transactional consistency.

---

# 18. Nếu COMMIT thành công

```text
Story       ✅
Chapter     ✅
Outbox      ✅
```

Sau đó worker có thể xử lý:

```text
Outbox
 ↓
ChapterAdded
 ↓
Handlers
```

---

# 19. Worker

Worker rất đơn giản ở mức concept:

```python
while True:

    events = outbox.get_pending()

    for event in events:

        dispatcher.dispatch(event)

        outbox.mark_processed(
            event.id
        )
```

Nhưng implementation production phức tạp hơn.

---

# 20. Deserialize Event

Outbox lưu:

```text
event_type
payload
```

Ví dụ:

```json
{
    "story_id": "story-1",
    "chapter_id": "chapter-10",
    "chapter_number": 10
}
```

Worker cần biến nó trở lại:

```python
ChapterAdded(...)
```

Ta cần Event Registry.

---

# 21. Event Registry

Ví dụ:

```python
EVENT_TYPES = {
    "ChapterAdded": ChapterAdded,
    "CrawlerCompleted": CrawlerCompleted,
}
```

Sau đó:

```python
event_cls = EVENT_TYPES[row["event_type"]]
```

rồi:

```python
event = deserialize(
    event_cls,
    row["payload"],
)
```

---

# 22. Không nên dùng `eval()`

Tuyệt đối tránh:

```python
eval(row["payload"])
```

Đặc biệt khi payload đến từ database/message có thể bị thao túng.

Dùng explicit registry:

```python
EVENT_TYPES = {
    "ChapterAdded": ChapterAdded,
}
```

an toàn và rõ ràng hơn.

---

# 23. Trạng thái Outbox

Ở phiên bản production, chỉ có:

```text
processed_at
```

thường chưa đủ.

Ta có thể thiết kế:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'pending',

    attempts INTEGER NOT NULL DEFAULT 0,

    next_attempt_at TEXT,

    processed_at TEXT,

    last_error TEXT
);
```

---

# 24. State Machine

Outbox:

```text
        ┌─────────┐
        │ pending │
        └────┬────┘
             │
             ▼
       ┌────────────┐
       │ processing │
       └─────┬──────┘
             │
       ┌─────┴─────┐
       ▼           ▼
   succeeded     failed
       │           │
       │           ▼
       │         retry
       │           │
       │           └──────→ processing
       │
       ▼
    processed
```

Có thể đơn giản hóa thành:

```text
pending → processed
pending → failed
failed → pending
```

---

# 25. Retry

Giả sử:

```text
NotificationHandler
```

gọi API.

API:

```text
500 Internal Server Error
```

Không nên:

```text
event = failed
DONE
```

Có thể retry:

```text
Attempt 1
   ↓
fail
   ↓
wait
   ↓
Attempt 2
   ↓
fail
   ↓
wait
   ↓
Attempt 3
```

---

# 26. Exponential Backoff

Ví dụ:

```text
attempt 1 → 1s
attempt 2 → 2s
attempt 3 → 4s
attempt 4 → 8s
attempt 5 → 16s
```

Công thức đơn giản:

```python
delay = 2 ** attempts
```

Thực tế thường thêm jitter để tránh nhiều worker retry đồng thời.

---

# 27. Dead Letter

Có những event không bao giờ xử lý được.

Ví dụ:

```text
payload corrupted
```

hoặc:

```text
event version không còn support
```

Sau:

```text
5 attempts
```

ta có:

```text
failed
```

hoặc đưa vào:

```text
dead letter
```

Ví dụ:

```text
outbox_dead_letter
```

---

# 28. At-Least-Once Delivery

Đây là một khái niệm rất quan trọng.

Worker:

```text
1. lấy event
2. dispatch
3. mark processed
```

Nếu:

```text
dispatch = success
```

nhưng process crash trước:

```text
mark processed
```

thì event vẫn pending.

Worker sau đó chạy lại.

Event được xử lý:

```text
lần 2
```

Vì vậy:

> **Outbox thường dẫn tới at-least-once processing.**

---

# 29. Handler phải Idempotent

Ví dụ Search:

```text
ChapterAdded
```

lần 1:

```text
index chapter-10
```

lần 2:

```text
index chapter-10
```

Nếu `index` là upsert:

```text
chapter-10 → same document
```

thì không sao.

Đây là một Handler tốt.

---

# 30. Notification khó hơn

Nếu:

```text
ChapterAdded
 ↓
Send email
```

retry có thể:

```text
Email #1
Email #2
```

User nhận duplicate.

Có thể dùng:

```text
event_id
```

làm idempotency key:

```text
notification_id = event_id
```

Database:

```sql
CREATE TABLE processed_notifications (
    event_id TEXT PRIMARY KEY
);
```

---

# 31. Concurrency

Giả sử có:

```text
Worker A
Worker B
```

Cả hai cùng đọc:

```text
event-001
```

Nếu không locking:

```text
Worker A → process
Worker B → process
```

Event chạy hai lần.

Do đó cần cơ chế claim/locking.

---

# 32. SQLite và Concurrency

Với SQLite, ta phải đặc biệt chú ý:

```text
single writer
```

SQLite hỗ trợ nhiều reader nhưng việc ghi đồng thời có giới hạn.

Với hệ thống nhỏ:

```text
1 Outbox Worker
```

có thể là lựa chọn đơn giản và hợp lý.

Khi hệ thống lớn hơn:

```text
PostgreSQL
Redis
RabbitMQ
Kafka
```

có thể phù hợp hơn tùy yêu cầu.

---

# 33. Worker đơn giản cho hệ thống đọc truyện

Với project hiện tại của bạn, ta có thể bắt đầu:

```text
SQLite
   │
   ▼
Outbox
   │
   ▼
Python Worker
   │
   ▼
Dispatcher
   │
   ├── SearchIndexHandler
   ├── StatisticsHandler
   └── NotificationHandler
```

Chưa cần Kafka hay RabbitMQ.

Điều quan trọng là **hiểu pattern trước**.

---

# 34. Polling

Worker có thể polling:

```python
while True:

    events = outbox.get_pending(
        limit=50
    )

    if not events:
        time.sleep(1)
        continue

    for event in events:
        process(event)
```

Đây là:

> **Polling Publisher**

---

# 35. Polling không phải vấn đề

Với app đọc truyện nhỏ:

```text
poll mỗi 1 giây
```

hoàn toàn có thể đủ.

Đừng vội:

```text
Kafka
RabbitMQ
Celery
Redis Streams
```

nếu application chưa cần.

DDD không yêu cầu hệ thống phải phức tạp.

---

# 36. Outbox + RQ

Với kiến trúc bạn đang học Redis/RQ, có thể kết hợp:

```text
SQLite
   ↓
Outbox
   ↓
Outbox Publisher
   ↓
Redis
   ↓
RQ Worker
   ↓
Handler
```

Nhưng cần nhớ:

> RQ không thay thế Outbox.

Outbox đảm bảo:

```text
Database state
+
Event
```

được lưu atomically.

RQ đảm nhiệm:

```text
background job execution
```

Hai vấn đề khác nhau.

---

# 37. Outbox + Celery

Tương tự:

```text
Aggregate
 ↓
Outbox
 ↓
Publisher
 ↓
Celery
 ↓
Worker
```

Celery giúp:

```text
retry
worker
scheduling
distributed execution
```

nhưng vẫn không tự giải quyết:

```text
DB commit
+
event publishing
```

atomicity.

---

# 38. Outbox + Redis

Có thể:

```text
SQLite
 ↓
Outbox
 ↓
Publisher
 ↓
Redis
 ↓
Worker
```

Một lần nữa:

```text
Outbox = reliability
Redis = messaging/queue infrastructure
```

---

# 39. Outbox không phải Domain Layer

Cực kỳ quan trọng về architecture.

Không nên:

```text
domain/
    outbox.py
```

nếu `outbox.py` chứa:

```text
SQLite
SQL
database schema
```

Một cách tổ chức:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   └── events.py
    │   │
    │   └── common/
    │
    ├── application/
    │   ├── use_cases/
    │   └── ports/
    │       └── outbox.py
    │
    └── infrastructure/
        └── persistence/
            └── sqlite/
                └── outbox.py
```

---

# 40. Dependency Direction

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

Thực tế dependency direction:

```text
Infrastructure
      ↓
Application interfaces
      ↓
Domain
```

Infrastructure implement interface mà Application/Domain yêu cầu.

Ví dụ:

```python
class OutboxRepository(Protocol):
    ...
```

Application biết interface.

Infrastructure:

```python
class SQLiteOutboxRepository:
    ...
```

implement interface đó.

---

# 41. Toàn bộ flow của hệ thống đọc truyện

Giả sử crawler tải chapter mới.

```text
Crawler
   ↓
AddChapterUseCase
   ↓
Story.add_chapter()
   ↓
ChapterAdded
   ↓
UnitOfWork
   ├── save Story
   ├── save Chapter
   └── save Outbox
          ↓
       COMMIT
          ↓
      Outbox Worker
          ↓
     Event Dispatcher
          │
     ┌────┼───────────┐
     ▼    ▼           ▼
  Search Stats    Notification
```

Crawler hoàn toàn không cần biết:

```text
Search
Notification
Statistics
```

---

# 42. Đây là Loose Coupling thực sự

Không có Event:

```text
Crawler
 ├── Search
 ├── Notification
 ├── Statistics
 └── Dashboard
```

Crawler trở thành God Component.

Có Outbox:

```text
Crawler
   ↓
Domain Event
   ↓
Outbox
```

Các thành phần khác subscribe/reaction độc lập.

---

# 43. Outbox và Clean Architecture

Ta có:

```text
Interface
     ↓
Application
     ↓
Domain
     ↑
Infrastructure
```

Outbox flow:

```text
Domain
  ↓
Domain Event
  ↓
Application
  ↓
Outbox Port
  ↓
Infrastructure
  ↓
SQLite
```

Worker:

```text
SQLite
  ↓
Outbox Repository
  ↓
Application Event Dispatcher
  ↓
Handlers
```

---

# 44. Outbox và Unit of Work

Đây là một cặp rất tự nhiên:

```text
UnitOfWork
 ├── Repository
 ├── Repository
 └── OutboxRepository
```

Tất cả dùng cùng:

```text
DB Connection
```

và:

```text
Transaction
```

Ví dụ:

```python
with uow:

    story = uow.stories.get(story_id)

    story.add_chapter(chapter)

    uow.stories.save(story)

    events = story.collect_events()

    for event in events:
        uow.outbox.add(event)

    uow.commit()
```

---

# 45. Một lỗi thiết kế rất phổ biến

Sai:

```python
story.add_chapter(chapter)

uow.commit()

dispatcher.dispatch_all()
```

Không có Outbox.

Có failure window:

```text
COMMIT
 ↓
💥
 ↓
dispatch
```

Event mất.

---

# 46. Một lỗi khác

Sai:

```python
story.add_chapter(chapter)

dispatcher.dispatch_all()

uow.commit()
```

Có nguy cơ:

```text
Notification sent
 ↓
COMMIT fails
```

Database nói:

```text
Chapter không tồn tại
```

Notification nói:

```text
Chapter đã tồn tại
```

❌

---

# 47. Thiết kế đúng

```text
story.add_chapter()
       ↓
Domain Event
       ↓
uow.outbox.add()
       ↓
uow.commit()
       ↓
Worker
       ↓
Handler
```

Đây là mental model cần nhớ.

---

# 48. Outbox Event có cần giữ toàn bộ Aggregate không?

**Không.**

Đừng serialize:

```python
Story
    ├── Chapter 1
    ├── Chapter 2
    ├── Chapter 3
    ├── metadata
    └── ...
```

Event nên chứa dữ liệu cần thiết:

```python
ChapterAdded(
    story_id,
    chapter_id,
    chapter_number,
)
```

Nếu Handler cần thêm data:

```text
Handler
 ↓
Repository
 ↓
load required data
```

hoặc Event có thêm dữ liệu phù hợp.

---

# 49. Event Versioning

Đây là vấn đề production quan trọng.

Hôm nay:

```json
{
    "story_id": "...",
    "chapter_id": "...",
    "chapter_number": 10
}
```

Ngày mai Event thay đổi:

```json
{
    "story_id": "...",
    "chapter_id": "...",
    "chapter_number": 10,
    "title": "..."
}
```

Worker có thể phải xử lý cả Event cũ.

Có thể thêm:

```text
event_version
```

Ví dụ:

```text
ChapterAdded
version = 1
```

hoặc:

```text
ChapterAdded.v1
ChapterAdded.v2
```

---

# 50. Event Schema

Production Outbox có thể:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_version INTEGER NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,

    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,

    next_attempt_at TEXT,
    processed_at TEXT,
    last_error TEXT
);
```

Đây là thiết kế tốt hơn nhiều so với bảng ban đầu.

---

# 51. Idempotency Key

Event:

```text
event_id = evt-123
```

Handler:

```text
event_id
   ↓
check processed
   ↓
process only once logically
```

Một hệ thống production nên có chiến lược rõ ràng cho:

```text
event_id
correlation_id
causation_id
```

Đặc biệt khi hệ thống bắt đầu có nhiều event chain.

---

# 52. Correlation ID

Ví dụ:

```text
User request
   ↓
AddChapter
   ↓
ChapterAdded
   ↓
Notification
```

Có thể giữ:

```text
correlation_id = request-123
```

Log:

```text
request-123
    AddChapter
    ChapterAdded
    Notification
```

Rất hữu ích để trace một workflow.

---

# 53. Causation ID

Ví dụ:

```text
CrawlerCompleted
```

gây ra:

```text
StoryUpdated
```

thì:

```text
StoryUpdated.causation_id
    = CrawlerCompleted.event_id
```

Ta có:

```text
CrawlerCompleted
      │
      └── causes
              ↓
        StoryUpdated
```

Đây là kỹ thuật observability nâng cao.

---

# 54. Outbox không có nghĩa là Eventual Consistency ở mọi nơi

Ví dụ:

```text
Story
Chapter
```

vẫn có thể:

```text
strong consistency
```

trong một Aggregate/transaction.

Còn:

```text
Search
Notification
Statistics
```

có thể:

```text
eventual consistency
```

Đây là một thiết kế có chủ đích.

---

# 55. Khi nào nên dùng Outbox?

Rất phù hợp khi:

```text
Database transaction
        +
Event/message
```

phải đáng tin cậy.

Ví dụ:

* gửi notification;
* cập nhật search index;
* publish message;
* đồng bộ sang service khác;
* tạo background job;
* cập nhật read model;
* trigger workflow.

---

# 56. Khi nào chưa cần Outbox?

Ứng dụng nhỏ:

```text
CRUD
 ↓
SQLite
```

không có:

```text
event
worker
external system
```

thì không cần cố nhét Outbox vào.

DDD không phải:

> "Càng nhiều pattern càng tốt."

Mà là:

> **Dùng pattern để giải quyết complexity thực tế.**

---

# 57. Bài tập lớn — triển khai Outbox

Với project đọc truyện của bạn, hãy xây:

```text
domain/
    events.py

application/
    ports/
        outbox.py

infrastructure/
    sqlite/
        outbox.py

worker/
    outbox_worker.py
```

Flow:

```text
Story.add_chapter()
        ↓
ChapterAdded
        ↓
collect_events()
        ↓
OutboxRepository.add()
        ↓
SQLite COMMIT
        ↓
OutboxWorker
        ↓
Dispatcher
        ↓
Handlers
```

---

# 58. Phiên bản đầu tiên nên đơn giản

Đừng ngay lập tức xây:

```text
Kafka
Redis
RQ
Celery
distributed lock
dead letter queue
```

Hãy bắt đầu:

```text
SQLite
 +
Outbox
 +
Python Worker
 +
Event Dispatcher
```

Sau khi chạy ổn mới nâng cấp.

---

# 59. Roadmap nâng cấp

### Level 1

```text
SQLite
 ↓
Outbox
 ↓
Worker
```

### Level 2

```text
retry
attempts
last_error
```

### Level 3

```text
idempotency
locking
concurrency
```

### Level 4

```text
Redis/RQ
```

### Level 5

```text
RabbitMQ/Kafka
```

### Level 6

```text
distributed event architecture
```

Đây là cách học tốt hơn nhiều so với việc nhảy thẳng vào Kafka.

---

# 60. Tổng kết Phần VII

Chúng ta đã hoàn thành:

```text
Buổi 31
Domain Event
      ↓
Buổi 32
Event Dispatcher
      ↓
Buổi 33
Event Handler
      ↓
Buổi 34
Event + Transaction
      ↓
Buổi 35
Outbox Pattern
```

Toàn bộ kiến trúc:

```text
                         DOMAIN
                           │
                     ┌─────▼─────┐
                     │ Aggregate │
                     └─────┬─────┘
                           │
                     Domain Event
                           │
                           ▼
                    APPLICATION
                           │
                     Unit of Work
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        Aggregate State             Outbox
              │                         │
              └────────────┬────────────┘
                           │
                         COMMIT
                           │
                           ▼
                    INFRASTRUCTURE
                           │
                         SQLite
                           │
                           ▼
                    Outbox Worker
                           │
                           ▼
                    Event Dispatcher
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Search       Statistics   Notification
```

## 5 điều cần nhớ

**1.**

```text
Aggregate + Outbox Event
```

phải được lưu trong **cùng transaction**.

**2.**

Không dispatch external side effect trước commit.

**3.**

Không dispatch trực tiếp sau commit nếu event có thể bị mất khi process crash.

**4.**

Outbox thường dẫn đến:

```text
at-least-once delivery
```

→ Handler nên **idempotent**.

**5.**

Outbox giải quyết:

```text
"Database đã commit nhưng Event bị mất"
```

chứ không tự giải quyết:

```text
retry
duplicate
locking
dead letter
external API failure
```

---

## Bài tập cuối Phần VII

Hãy tự thiết kế flow cho:

```text
CrawlerCompleted
```

với yêu cầu:

```text
Crawler
   ↓
CrawlerCompleted
   ↓
Outbox
   ↓
SQLite COMMIT
   ↓
Worker
   ↓
Dispatcher
   ├── UpdateCrawlerStatistics
   ├── UpdateDashboard
   ├── SendNotification
   └── ScheduleNextCrawl
```

Và trả lời 4 câu:

1. **Nếu `CrawlerCompleted` được tạo nhưng SQLite rollback thì Outbox có Event không?**
2. **Nếu SQLite commit thành công rồi worker crash thì Event có mất không?**
3. **Nếu Worker xử lý thành công nhưng crash trước `mark_processed()` thì điều gì xảy ra?**
4. **Handler nào cần idempotency mạnh nhất: Statistics, Dashboard, Notification hay ScheduleNextCrawl? Vì sao?**

Đây là bài tập rất tốt để kiểm tra xem bạn đã thực sự hiểu **Domain Event + Transaction + Outbox**, thay vì chỉ nhớ sơ đồ.
