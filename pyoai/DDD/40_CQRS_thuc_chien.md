# DDD Deep Dive — Buổi 40

# CQRS thực chiến: Crawler Dashboard bằng Read Model riêng

Đây là buổi **tổng hợp rất quan trọng**.

Từ đầu khóa đến giờ chúng ta đã đi qua:

```text
Entity
Value Object
Aggregate
Repository
Unit of Work
Domain Service
Application Service
Domain Event
Outbox
CQRS
Read Model
```

Hôm nay ghép tất cả lại thành một hệ thống:

```text
Crawler
   ↓
CrawlerJob Aggregate
   ↓
Domain Event
   ↓
Outbox
   ↓
Projection Worker
   ↓
Crawler Dashboard Read Model
   ↓
UI
```

---

# 1. Bài toán

Giả sử crawler của chúng ta có:

```text
10 nguồn truyện
3 crawler đang chạy
820 job hoàn thành
7 job thất bại
2,500 truyện
85,000 chapter
```

Dashboard muốn hiển thị:

```text
┌──────────────────────────────────────────┐
│              CRAWLER DASHBOARD            │
├──────────────────────────────────────────┤
│                                          │
│ Running Jobs       3                    │
│ Completed Jobs  820                     │
│ Failed Jobs       7                     │
│                                          │
│ Stories Found   2,500                    │
│ Chapters Found 85,000                    │
│                                          │
└──────────────────────────────────────────┘
```

Câu hỏi:

> Có nên mỗi lần mở Dashboard lại query toàn bộ `crawler_jobs`, `stories`, `chapters` rồi `COUNT()`?

Có thể.

Nhưng nếu hệ thống lớn hơn, ta có thể tạo một **Read Model riêng**:

```text
crawler_dashboard
```

---

# 2. Kiến trúc tổng thể

Hệ thống:

```text
                         WRITE SIDE

                    StartCrawlerCommand
                           │
                           ▼
                  StartCrawlerUseCase
                           │
                           ▼
                     CrawlerJob
                      Aggregate
                           │
                           ▼
                   CrawlerStarted
                           │
                           ▼
                         Outbox
                           │
                           ▼
                    Projection Worker
                           │
                           ▼
                         READ DB
                           │
                           ▼
                 CrawlerDashboard
                           │
                           ▼
                          UI
```

---

# 3. Tại sao cần Read Model riêng?

Nếu Dashboard query trực tiếp:

```sql
SELECT COUNT(*)
FROM crawler_jobs
WHERE status = 'running';
```

thì đơn giản.

Nhưng Dashboard có thể cần:

```text
running jobs
completed jobs
failed jobs
stories found
chapters found
average crawl duration
last crawl time
success rate
jobs by source
chapters per hour
```

Query sẽ ngày càng phức tạp.

Ta có thể tạo:

```text
crawler_dashboard
```

để lưu dữ liệu đã được tổng hợp.

---

# 4. Read Model không phải Aggregate

Ví dụ:

```python
@dataclass(frozen=True)
class CrawlerDashboard:

    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    stories_found: int
    chapters_found: int
```

Nó không có:

```python
dashboard.start_job()
dashboard.complete_job()
```

Đây chỉ là:

```text
Projection Data
```

---

# 5. Read Model Database

Có thể tạo bảng:

```sql
CREATE TABLE crawler_dashboard (
    id INTEGER PRIMARY KEY CHECK (id = 1),

    running_jobs INTEGER NOT NULL,
    completed_jobs INTEGER NOT NULL,
    failed_jobs INTEGER NOT NULL,

    stories_found INTEGER NOT NULL,
    chapters_found INTEGER NOT NULL,

    updated_at TEXT NOT NULL
);
```

Chúng ta chỉ cần **một record**:

```text
id = 1
```

Ví dụ:

```text
id | running | completed | failed | stories | chapters
1  |    3    |    820    |   7    |  2500   |  85000
```

---

# 6. Projection là gì?

Projection là quá trình:

```text
Domain Event
     ↓
Projection
     ↓
Read Model
```

Ví dụ:

```text
CrawlerStarted
     ↓
running_jobs += 1
```

và:

```text
CrawlerCompleted
     ↓
running_jobs -= 1
completed_jobs += 1
```

và:

```text
CrawlerFailed
     ↓
running_jobs -= 1
failed_jobs += 1
```

---

# 7. Domain Event

Ta đã học Domain Event ở Buổi 31.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlerStarted:

    job_id: str
    source_id: str
```

Crawler completed:

```python
@dataclass(frozen=True)
class CrawlerCompleted:

    job_id: str
    source_id: str
    stories_found: int
    chapters_found: int
```

Crawler failed:

```python
@dataclass(frozen=True)
class CrawlerFailed:

    job_id: str
    source_id: str
    reason: str
```

---

# 8. Event phải diễn tả chuyện đã xảy ra

Đúng:

```text
CrawlerStarted
CrawlerCompleted
CrawlerFailed
```

Không nên:

```text
StartCrawler
CompleteCrawler
FailCrawler
```

Vì:

```text
StartCrawler
```

là **Command**.

Trong khi:

```text
CrawlerStarted
```

là **Event**.

Nhớ:

```text
Command → muốn làm gì

Event → chuyện gì đã xảy ra
```

---

# 9. Aggregate tạo Event

Ví dụ:

```python
class CrawlerJob:

    def start(self):

        if self.status != "pending":
            raise InvalidCrawlerStateError()

        self.status = "running"

        self._events.append(
            CrawlerStarted(
                job_id=self.id,
                source_id=self.source_id,
            )
        )
```

Aggregate không biết:

```text
Dashboard
SQLite projection
PySide6
```

Đây là điểm cực kỳ quan trọng.

---

# 10. Aggregate chỉ phát Event

```text
CrawlerJob
    │
    └── CrawlerStarted
```

Sau đó Application/Infrastructure xử lý:

```text
CrawlerStarted
       ↓
Outbox
       ↓
Projection
```

---

# 11. Outbox

Chúng ta đã học Outbox ở Buổi 35.

Database:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    processed_at TEXT
);
```

Transaction:

```text
BEGIN
   │
   ├── UPDATE crawler_jobs
   │
   └── INSERT outbox
            │
COMMIT       │
             ▼
        Event persisted
```

Điểm quan trọng:

> Crawler state và Domain Event được lưu **cùng transaction**.

---

# 12. Tại sao cần Outbox?

Nếu làm:

```text
UPDATE crawler_jobs
COMMIT

publish event
```

có thể xảy ra:

```text
UPDATE thành công
       ↓
COMMIT thành công
       ↓
publish event lỗi
```

Kết quả:

```text
Database đúng
Dashboard không update
```

Outbox giải quyết vấn đề đó.

---

# 13. Projection Worker

Worker đọc:

```text
outbox
```

và:

```text
event
 ↓
handler
 ↓
projection
```

Ví dụ:

```python
class CrawlerStartedProjection:

    def handle(
        self,
        event: CrawlerStarted,
    ):
        ...
```

---

# 14. Event Dispatcher

Ta có thể xây một dispatcher đơn giản:

```python
class EventDispatcher:

    def __init__(self):
        self._handlers = {}

    def register(self, event_type, handler):
        self._handlers.setdefault(
            event_type,
            []
        ).append(handler)

    def dispatch(self, event):

        for handler in self._handlers.get(
            type(event),
            [],
        ):
            handler.handle(event)
```

Registration:

```python
dispatcher.register(
    CrawlerStarted,
    crawler_dashboard_projection,
)

dispatcher.register(
    CrawlerCompleted,
    crawler_dashboard_projection,
)
```

---

# 15. Projection Handler

```python
class CrawlerDashboardProjection:

    def __init__(self, connection):
        self.connection = connection

    def handle(self, event):

        if isinstance(event, CrawlerStarted):
            self._started(event)

        elif isinstance(event, CrawlerCompleted):
            self._completed(event)

        elif isinstance(event, CrawlerFailed):
            self._failed(event)
```

---

# 16. CrawlerStarted Projection

```python
def _started(self, event):

    self.connection.execute(
        """
        UPDATE crawler_dashboard
        SET running_jobs = running_jobs + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """
    )
```

Kết quả:

```text
Before

running = 3


CrawlerStarted


After

running = 4
```

---

# 17. CrawlerCompleted Projection

```python
def _completed(self, event):

    self.connection.execute(
        """
        UPDATE crawler_dashboard
        SET
            running_jobs = running_jobs - 1,
            completed_jobs = completed_jobs + 1,
            stories_found =
                stories_found + ?,
            chapters_found =
                chapters_found + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """,
        (
            event.stories_found,
            event.chapters_found,
        ),
    )
```

---

# 18. CrawlerFailed Projection

```python
def _failed(self, event):

    self.connection.execute(
        """
        UPDATE crawler_dashboard
        SET
            running_jobs = running_jobs - 1,
            failed_jobs = failed_jobs + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """
    )
```

---

# 19. Đây chính là CQRS

Write Side:

```text
CrawlerJob
    ↓
status = COMPLETED
```

Read Side:

```text
CrawlerCompleted
    ↓
crawler_dashboard
    ↓
completed_jobs += 1
```

Hai bên có model khác nhau.

---

# 20. Query Dashboard

Bây giờ UI không cần query:

```text
crawler_jobs
stories
chapters
```

nữa.

Chỉ cần:

```sql
SELECT
    running_jobs,
    completed_jobs,
    failed_jobs,
    stories_found,
    chapters_found
FROM crawler_dashboard
WHERE id = 1;
```

---

# 21. Read Repository

```python
class CrawlerDashboardReadRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_dashboard(self):

        row = self.connection.execute(
            """
            SELECT
                running_jobs,
                completed_jobs,
                failed_jobs,
                stories_found,
                chapters_found
            FROM crawler_dashboard
            WHERE id = 1
            """
        ).fetchone()

        return CrawlerDashboard(
            running_jobs=row["running_jobs"],
            completed_jobs=row["completed_jobs"],
            failed_jobs=row["failed_jobs"],
            stories_found=row["stories_found"],
            chapters_found=row["chapters_found"],
        )
```

---

# 22. Query Handler

```python
class GetCrawlerDashboardHandler:

    def __init__(self, repository):
        self.repository = repository

    def execute(self):

        return self.repository.get_dashboard()
```

UI:

```python
dashboard = handler.execute()

print(
    dashboard.running_jobs
)
```

---

# 23. Toàn bộ Flow

Khi crawler bắt đầu:

```text
StartCrawlerCommand
        ↓
StartCrawlerUseCase
        ↓
CrawlerJob.start()
        ↓
CrawlerStarted
        ↓
Outbox
        ↓
COMMIT
        ↓
Projection Worker
        ↓
CrawlerDashboardProjection
        ↓
running_jobs += 1
```

Khi crawler hoàn thành:

```text
CompleteCrawlerCommand
        ↓
CompleteCrawlerUseCase
        ↓
CrawlerJob.complete()
        ↓
CrawlerCompleted
        ↓
Outbox
        ↓
COMMIT
        ↓
Projection
        ↓
Dashboard
```

---

# 24. Eventual Consistency

Đây là khái niệm rất quan trọng.

Giả sử:

```text
10:00:00.000
CrawlerCompleted
```

Write DB cập nhật ngay:

```text
status = completed
```

Nhưng Projection Worker xử lý sau:

```text
10:00:00.050
```

Trong khoảng:

```text
10:00:00.000
→
10:00:00.050
```

Dashboard có thể vẫn hiển thị:

```text
Running = 3
```

thay vì:

```text
Running = 2
```

Đây là:

> **Eventual Consistency**

---

# 25. Có phải đây là bug?

Không nhất thiết.

Nếu business cho phép:

```text
delay vài milliseconds
```

thì hoàn toàn ổn.

Đây là trade-off của CQRS + asynchronous projection.

---

# 26. Với app SQLite desktop thì sao?

Bạn có thể không cần asynchronous projection.

Có thể:

```text
Command
 ↓
Transaction
 ↓
Domain Event
 ↓
Projection
 ↓
Commit
```

hoặc xử lý projection ngay trong process.

Khi đó:

```text
Write
 ↓
Projection
 ↓
Read Model
```

gần như đồng bộ.

Đơn giản hơn rất nhiều.

---

# 27. Production Architecture

Khi hệ thống lớn:

```text
                  WRITE

Crawler
   ↓
Application
   ↓
Aggregate
   ↓
Write DB
   ↓
Outbox
   ↓
Worker
   ↓
Event
   ↓
Projection
   ↓
READ DB
   ↓
Dashboard
```

Read DB có thể là:

```text
SQLite
PostgreSQL
Redis
Elasticsearch
```

tùy nhu cầu.

---

# 28. Một Event có thể có nhiều Projection

Ví dụ:

```text
ChapterAdded
      │
      ├───────────────┐
      ▼               ▼
StoryList          SearchIndex
Projection         Projection
      │               │
      ▼               ▼
Read DB          Elasticsearch
```

Đồng thời:

```text
ChapterAdded
      │
      ├── Notification Projection
      │
      └── Statistics Projection
```

Đây chính là sức mạnh của Event-driven CQRS.

---

# 29. CrawlerCompleted có thể có nhiều Consumer

```text
                 CrawlerCompleted
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Dashboard      Statistics    Notification
      Projection     Projection      Handler
```

Aggregate không cần biết ba consumer này tồn tại.

Đây chính là **loose coupling**.

---

# 30. Idempotency

Đây là vấn đề production cực kỳ quan trọng.

Giả sử worker nhận:

```text
CrawlerCompleted(event_id=123)
```

xử lý thành công.

Nhưng worker crash trước khi đánh dấu:

```text
processed_at
```

Sau đó restart.

Event `123` được xử lý lại.

Nếu:

```sql
completed_jobs += 1
```

thì:

```text
1 event
→
2 lần increment
```

Dashboard sai.

---

# 31. Projection phải Idempotent

Ta có thể tạo:

```sql
CREATE TABLE processed_events (
    event_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL
);
```

Worker:

```text
event
 ↓
check event_id
 ↓
đã xử lý?
 ├── YES → skip
 └── NO
      ↓
   projection
      ↓
   mark processed
```

---

# 32. Transaction của Projection

Có thể:

```text
BEGIN
   │
   ├── UPDATE crawler_dashboard
   │
   └── INSERT processed_events
   │
COMMIT
```

Nếu projection lỗi:

```text
ROLLBACK
```

Do đó:

```text
Dashboard update
+
Processed marker
```

được atomic.

---

# 33. Outbox Worker

Pseudo-code:

```python
while True:

    events = outbox.get_unprocessed()

    for event in events:

        try:
            dispatcher.dispatch(event)

            outbox.mark_processed(
                event.id
            )

        except Exception:
            log.exception(
                "Projection failed"
            )
```

Trong production sẽ cần thêm:

```text
retry
backoff
dead-letter
locking
idempotency
metrics
```

Nhưng architecture cơ bản là như vậy.

---

# 34. CQRS không có nghĩa là Event Sourcing

Hai khái niệm này rất dễ nhầm.

CQRS:

```text
Write Model
+
Read Model
```

Event Sourcing:

```text
Events
   ↓
source of truth
```

Ta đang làm:

```text
SQLite state
+
Domain Events
+
Read Model
```

Không phải Event Sourcing.

---

# 35. Database vẫn là source of truth

Trong kiến trúc hiện tại:

```text
crawler_jobs
stories
chapters
```

là state chính.

Event:

```text
CrawlerCompleted
```

chỉ dùng để:

```text
notify
project
update read model
```

Không phải source of truth.

---

# 36. Khi nào Event Sourcing xuất hiện?

Nếu kiến trúc:

```text
CrawlerJob
   ↓
CrawlerStarted
CrawlerPaused
CrawlerResumed
CrawlerCompleted
   ↓
Event Store
```

và state hiện tại được reconstruct:

```text
Events
 ↓
Replay
 ↓
CrawlerJob
```

đó mới là Event Sourcing.

Đây là một chủ đề khác và chưa cần đưa vào project hiện tại.

---

# 37. Cấu trúc project hoàn chỉnh

Sau Buổi 40:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   ├── chapter/
    │   └── crawler/
    │
    ├── application/
    │   ├── commands/
    │   │   ├── create_story.py
    │   │   ├── add_chapter.py
    │   │   ├── start_crawler.py
    │   │   └── complete_crawler.py
    │   │
    │   └── queries/
    │       ├── story_list.py
    │       ├── chapter_list.py
    │       ├── reading_page.py
    │       └── crawler_dashboard.py
    │
    ├── read_model/
    │   ├── models.py
    │   ├── repositories.py
    │   └── projections/
    │       └── crawler_dashboard.py
    │
    ├── infrastructure/
    │   └── sqlite/
    │       ├── connection.py
    │       ├── schema.py
    │       ├── write_repositories.py
    │       ├── read_repositories.py
    │       └── outbox.py
    │
    └── interface/
        ├── cli/
        └── ui/
```

---

# 38. Architecture cuối cùng

Đây là kiến trúc chúng ta đã xây dựng qua 40 buổi:

```text
                           INTERFACE
                      CLI / PySide6 / HTTP
                               │
                               ▼
                         APPLICATION
                               │
              ┌────────────────┴────────────────┐
              │                                 │
           COMMAND                            QUERY
              │                                 │
              ▼                                 ▼
          Use Case                        Query Handler
              │                                 │
              ▼                                 ▼
          AGGREGATE                       READ MODEL
              │                                 │
              ▼                                 ▼
       Domain Repository                 Read Repository
              │                                 │
              ▼                                 ▼
          WRITE DB                         READ DB
              │
              ▼
          DOMAIN EVENT
              │
              ▼
            OUTBOX
              │
              ▼
           WORKER
              │
              ▼
          PROJECTION
              │
              ▼
           READ DB
```

---

# 39. Điều quan trọng nhất cần hiểu

Không phải:

```text
CQRS = hai database
```

Mà:

```text
CQRS = tách mô hình ghi và mô hình đọc
```

Có thể:

```text
Write Model ──┐
              ├── SQLite
Read Model ───┘
```

Hoặc:

```text
Write Model → PostgreSQL

Read Model → PostgreSQL
```

Hoặc:

```text
Write Model → PostgreSQL

Read Model → Elasticsearch
```

---

# 40. So sánh toàn bộ hệ thống

| Thành phần          | Nhiệm vụ                        |
| ------------------- | ------------------------------- |
| Entity              | Identity + behavior             |
| Value Object        | Value + validation              |
| Aggregate           | Consistency boundary            |
| Repository          | Persistence abstraction         |
| Unit of Work        | Transaction                     |
| Domain Service      | Domain logic không thuộc Entity |
| Application Service | Orchestration                   |
| Command             | User intent                     |
| Domain Event        | Something happened              |
| Outbox              | Reliable event persistence      |
| Query               | Read request                    |
| Read Model          | Data optimized for reading      |
| Projection          | Event → Read Model              |
| Worker              | Xử lý event                     |
| UI                  | Hiển thị                        |

---

# 41. Mental Model cuối cùng

Hãy ghi nhớ sơ đồ này:

```text
                    USER INTENT
                         │
                         ▼
                      COMMAND
                         │
                         ▼
                     USE CASE
                         │
                         ▼
                     AGGREGATE
                         │
                    Business Rule
                         │
                         ▼
                    WRITE DB
                         │
                    Domain Event
                         │
                         ▼
                       OUTBOX
                         │
                         ▼
                       WORKER
                         │
                         ▼
                    PROJECTION
                         │
                         ▼
                     READ MODEL
                         │
                         ▼
                       QUERY
                         │
                         ▼
                         UI
```

Đây là một trong những **mental model quan trọng nhất của DDD + CQRS**.

---

# 42. Bài tập tổng hợp

Hãy thiết kế flow cho:

### `StartCrawler`

```text
StartCrawlerCommand
        ↓
?
        ↓
CrawlerJob
        ↓
?
        ↓
SQLite
```

### `CrawlerCompleted`

```text
CrawlerCompleted
        ↓
?
        ↓
crawler_dashboard
```

### Dashboard

```text
GetCrawlerDashboardQuery
        ↓
?
        ↓
CrawlerDashboard
        ↓
PySide6
```

Bạn nên tự điền các thành phần còn thiếu trước khi xem đáp án.

---

# 43. Đáp án

### StartCrawler

```text
StartCrawlerCommand
        ↓
StartCrawlerUseCase
        ↓
CrawlerJob.start()
        ↓
CrawlerStarted
        ↓
Outbox
        ↓
SQLite transaction
```

### CrawlerCompleted

```text
CrawlerCompleted
        ↓
CrawlerDashboardProjection
        ↓
crawler_dashboard
```

### Dashboard

```text
GetCrawlerDashboardQuery
        ↓
GetCrawlerDashboardHandler
        ↓
CrawlerDashboardReadRepository
        ↓
SQLite
        ↓
CrawlerDashboard
        ↓
PySide6
```

---

## 🎯 Kết thúc Phần VIII — CQRS

Bạn đã đi từ:

```text
DDD
 ↓
Strategic DDD
 ↓
Tactical DDD
 ↓
Aggregate
 ↓
Repository
 ↓
Unit of Work
 ↓
Domain Service
 ↓
Application Service
 ↓
Domain Event
 ↓
Outbox
 ↓
CQRS
 ↓
Command Model
 ↓
Query Model
 ↓
Read Model
 ↓
Projection
 ↓
Crawler Dashboard
```

Ở mức này, bạn không còn chỉ học **DDD pattern riêng lẻ** nữa mà đã bắt đầu hiểu cách chúng **kết hợp thành một kiến trúc thực tế**.

Phần tiếp theo hợp lý nhất là đi vào **DDD nâng cao / Production DDD**: **Factory, Specification, Domain Policy, Domain Event nâng cao, Saga/Process Manager, Concurrency, Optimistic Locking, Aggregate consistency và Testing DDD**.
