# DDD Deep Dive — Buổi 36

# CQRS — Command Query Responsibility Segregation

Sau khi đã học:

```text
Domain
Subdomain
Bounded Context
Entity
Value Object
Aggregate
Repository
Unit of Work
Domain Service
Application Service
Domain Event
Outbox
```

thì **CQRS** là bước rất tự nhiên tiếp theo.

CQRS giúp chúng ta trả lời một câu hỏi quan trọng:

> **Tại sao cách chúng ta ghi dữ liệu và cách chúng ta đọc dữ liệu nhất thiết phải giống nhau?**

Câu trả lời là: **không nhất thiết.**

---

# 1. CQRS là gì?

CQRS = **Command Query Responsibility Segregation**

Ý tưởng cốt lõi:

```text
Command → thay đổi State

Query   → đọc State
```

Tách hai trách nhiệm:

```text
             Application
                 │
        ┌────────┴────────┐
        │                 │
     Command             Query
        │                 │
        ▼                 ▼
   Write Model        Read Model
```

### Command

Ví dụ:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
```

Command có thể:

```text
CREATE
UPDATE
DELETE
```

### Query

Ví dụ:

```text
GetStoryList
GetChapterList
GetCrawlerDashboard
GetReadingPage
```

Query:

> **Không làm thay đổi business state.**

---

# 2. CRUD truyền thống

Một ứng dụng CRUD thông thường:

```text
                Controller
                    │
                    ▼
                Service
                    │
                    ▼
                Repository
                    │
                    ▼
                  SQLite
```

Cả đọc và ghi đều sử dụng cùng Model:

```text
Story
Chapter
CrawlerJob
```

Ví dụ:

```python
story = story_repository.get(story_id)
```

Sau đó UI lấy trực tiếp:

```python
story.title
story.status
story.chapters
```

Ban đầu rất đơn giản.

---

# 3. Nhưng hệ thống lớn sẽ xuất hiện vấn đề

Ví dụ Dashboard cần hiển thị:

```text
Crawler Dashboard
──────────────────────────────────

Source       Running   Success   Failed
──────────────────────────────────
Site A          3        120       2
Site B          1         85       0
Site C          8        300      12
```

Để lấy được màn hình này từ Domain Model, có thể phải:

```text
CrawlerSource
     ↓
CrawlerJob
     ↓
Story
     ↓
Chapter
     ↓
aggregate nhiều dữ liệu
     ↓
group
     ↓
count
     ↓
calculate
```

Không cần thiết.

Dashboard chỉ cần:

```text
SELECT ...
GROUP BY ...
```

---

# 4. CQRS giải quyết vấn đề đó

Ta tách:

```text
WRITE SIDE
────────────────────

Command
   ↓
Use Case
   ↓
Domain
   ↓
Aggregate
   ↓
Repository
   ↓
Write DB
```

và:

```text
READ SIDE
────────────────────

Query
   ↓
Read Model
   ↓
Read Repository
   ↓
SQLite
```

Sơ đồ:

```text
                       Application
                            │
              ┌─────────────┴─────────────┐
              │                           │
          COMMAND                       QUERY
              │                           │
              ▼                           ▼
          Write Side                  Read Side
              │                           │
           Domain                    Read Model
              │                           │
          Aggregate                 SQL Query
              │                           │
              ▼                           ▼
          Write DB                   Read DB
```

---

# 5. Command là gì?

Command là một **ý định thay đổi hệ thống**.

Ví dụ:

```python
CreateStory(
    title="Đấu Phá Thương Khung"
)
```

hoặc:

```python
AddChapter(
    story_id=story_id,
    chapter_number=100,
    title="Chương 100",
    content="..."
)
```

Command thường mang tính:

> **Do something**

Ví dụ:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
CompleteCrawler
```

---

# 6. Query là gì?

Query là yêu cầu lấy dữ liệu:

```python
GetStoryList()
```

hoặc:

```python
GetReadingPage(
    story_id=story_id,
    chapter_number=100
)
```

Query mang tính:

> **Give me something**

Ví dụ:

```text
GetStoryList
GetChapterList
GetReadingPage
GetCrawlerDashboard
```

---

# 7. Command vs Query

| Command           | Query                         |
| ----------------- | ----------------------------- |
| Thay đổi state    | Đọc state                     |
| Có side effect    | Không side effect             |
| Có business rule  | Thường không có business rule |
| Đi qua Domain     | Có thể không cần Domain       |
| Có transaction    | Thường read-only              |
| Có thể phát Event | Không nên                     |
| Write Model       | Read Model                    |

Mental model:

```text
Command = DO

Query = GET
```

---

# 8. Một nguyên tắc quan trọng

Command:

```python
AddChapter(...)
```

không nên trả về:

```python
[
    chapter,
    story,
    crawler,
    statistics,
    ...
]
```

Nó chỉ cần trả kết quả cần thiết:

```python
AddChapterResult(
    chapter_id=chapter_id
)
```

Sau đó UI muốn dữ liệu gì:

```text
Query
```

Ví dụ:

```text
AddChapter
    ↓
chapter_id

GetReadingPage(chapter_id)
    ↓
ReadingPage
```

---

# 9. Write Model là gì?

Write Model là model phục vụ **business behavior và consistency**.

Ví dụ:

```text
Story Aggregate
```

có thể:

```python
story.add_chapter(chapter)
story.rename(title)
story.publish()
```

Write Model quan tâm:

```text
Business Rule
Invariant
Aggregate
Entity
Value Object
Transaction
Domain Event
```

---

# 10. Read Model là gì?

Read Model được tối ưu cho việc **đọc**.

Ví dụ Dashboard:

```python
@dataclass
class CrawlerDashboard:

    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_chapters: int
```

Nó không cần:

```text
Entity
Aggregate
Invariant
Business behavior
```

Nó chỉ cần:

```text
Dữ liệu UI cần.
```

---

# 11. Read Model không nhất thiết là Entity

Đây là điểm rất quan trọng.

Write Model:

```python
class Story:
    ...
```

Read Model:

```python
@dataclass(frozen=True)
class StoryListItem:

    id: str
    title: str
    chapter_count: int
    latest_chapter: int
    updated_at: str
```

Hai object có mục đích hoàn toàn khác nhau.

---

# 12. Không nên ép Read Model thành Domain Entity

Sai tư duy:

```text
UI
 ↓
Story Entity
 ↓
tính chapter_count
 ↓
tính latest chapter
 ↓
tính status
```

CQRS:

```text
UI
 ↓
StoryListItem
```

Query trực tiếp dữ liệu cần thiết.

---

# 13. Ví dụ hệ thống đọc truyện

Hệ thống của chúng ta:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

Command Side:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
UpdateReadingProgress
```

Query Side:

```text
StoryList
ChapterList
ReadingPage
CrawlerDashboard
ReadingHistory
```

---

# 14. Write Side

Ví dụ:

```text
AddChapter
    ↓
AddChapterUseCase
    ↓
Story Aggregate
    ↓
story.add_chapter(...)
    ↓
ChapterAdded
    ↓
UnitOfWork
    ↓
SQLite
```

Ở đây Domain bảo vệ invariant.

Ví dụ:

```python
story.add_chapter(chapter)
```

có thể kiểm tra:

```text
Chapter number > 0
Chapter không duplicate
Story còn active
```

---

# 15. Read Side

Dashboard không cần:

```python
CrawlerJob.start()
CrawlerJob.pause()
```

Nó chỉ cần:

```text
SELECT
    source_id,
    COUNT(*) ...
```

Ví dụ:

```python
class CrawlerDashboardQuery:

    def __init__(self, conn):
        self.conn = conn

    def execute(self):
        ...
```

---

# 16. Query Model có thể rất phẳng

Domain Model:

```text
Story
 ├── StoryId
 ├── StoryTitle
 ├── SourceId
 └── Status
```

Read Model:

```text
StoryListItem
 ├── id
 ├── title
 ├── source_name
 ├── chapter_count
 ├── latest_chapter
 └── updated_at
```

Có thể lấy bằng:

```sql
SELECT
    s.id,
    s.title,
    src.name,
    COUNT(c.id) AS chapter_count,
    MAX(c.number) AS latest_chapter,
    s.updated_at
FROM stories s
JOIN sources src
    ON src.id = s.source_id
LEFT JOIN chapters c
    ON c.story_id = s.id
GROUP BY s.id;
```

Không cần hydrate Aggregate.

---

# 17. Đây chính là sức mạnh của CQRS

Write Model:

```text
tối ưu cho business logic
```

Read Model:

```text
tối ưu cho query
```

Hai bên không còn bị ép phải giống nhau.

---

# 18. CQRS không nhất thiết có 2 database

Đây là một hiểu nhầm phổ biến.

CQRS **không bắt buộc**:

```text
Write DB ≠ Read DB
```

Bạn hoàn toàn có thể:

```text
          SQLite
         /      \
        /        \
 Write Model    Read Model
```

Cùng một database.

Đây thường là lựa chọn tốt cho application hiện tại của bạn.

---

# 19. CQRS mức đơn giản

```text
                SQLite
              /        \
             /          \
        Write Side     Read Side
           │              │
        Domain         SQL Query
```

Không cần:

```text
Kafka
Redis
Microservices
Replication
```

---

# 20. CQRS mức nâng cao

Khi hệ thống lớn:

```text
             Command
                ↓
           Write Database
                ↓
         Domain Events
                ↓
              Outbox
                ↓
             Message Bus
                ↓
          Read Model Builder
                ↓
           Read Database
```

Lúc này:

```text
Write DB
```

và:

```text
Read DB
```

có thể hoàn toàn khác nhau.

Ví dụ:

```text
PostgreSQL
    ↓
Events
    ↓
Elasticsearch
```

cho search.

Hoặc:

```text
PostgreSQL
    ↓
Events
    ↓
Redis
```

cho dashboard/cache.

---

# 21. CQRS + Domain Event

Đây là chỗ Buổi 35 kết nối trực tiếp với Buổi 36.

Ta có:

```text
Command
   ↓
Aggregate
   ↓
Domain Event
   ↓
Outbox
   ↓
Worker
   ↓
Read Model
```

Ví dụ:

```text
AddChapter
    ↓
Story.add_chapter()
    ↓
ChapterAdded
    ↓
Outbox
    ↓
Worker
    ↓
UpdateStoryList
    ↓
UpdateChapterList
    ↓
UpdateStatistics
```

---

# 22. Read Model có thể là Projection

Một khái niệm quan trọng:

> **Projection**

Projection là quá trình biến Event/Write State thành Read Model.

Ví dụ:

```text
ChapterAdded
       ↓
StoryListProjection
       ↓
chapter_count += 1
```

Hoặc:

```text
ChapterAdded
       ↓
LatestChapterProjection
       ↓
latest_chapter = 100
```

---

# 23. Ví dụ Projection

```python
class StoryListProjection:

    def handle(self, event: ChapterAdded):

        # update read model

        ...
```

Event:

```text
ChapterAdded
```

Read Model:

```text
story_list
```

---

# 24. Read Model có thể được denormalize

Database bình thường:

```text
stories
chapters
sources
```

Read Model:

```text
story_list
```

có thể chứa:

```text
story_id
title
source_name
chapter_count
latest_chapter
latest_chapter_title
updated_at
```

Dữ liệu bị lặp:

```text
source_name
```

Nhưng query nhanh hơn.

Đây là:

> **Denormalization**

---

# 25. Vì sao CQRS phù hợp với domain phức tạp?

Không phải vì:

> "CQRS nhanh hơn CRUD."

Mà vì:

> **Write và Read có nhu cầu thiết kế khác nhau.**

Write cần:

```text
Consistency
Invariant
Transaction
Business Rule
Aggregate
```

Read cần:

```text
Performance
Filtering
Sorting
Pagination
Projection
UI-specific shape
Reporting
```

Một model khó tối ưu tốt cho cả hai.

---

# 26. Ví dụ cực kỳ rõ

Write:

```python
story.add_chapter(chapter)
```

cần kiểm tra:

```text
Story status
Chapter number
Duplicate
Business invariant
```

Read:

```text
GET /stories
```

chỉ cần:

```text
id
title
chapter_count
latest_chapter
```

Không cần toàn bộ Domain Model.

---

# 27. Query có thể bypass Domain

Điều này hoàn toàn hợp lệ.

Ví dụ:

```python
class StoryListQuery:

    def __init__(self, conn):
        self.conn = conn

    def execute(self):
        rows = self.conn.execute(
            """
            SELECT ...
            FROM stories
            """
        )

        return [
            StoryListItem(...)
            for row in rows
        ]
```

Không cần:

```python
Story(...)
```

Không cần:

```python
StoryRepository.get(...)
```

Không cần:

```python
Aggregate
```

vì đây là **read side**.

---

# 28. CQRS không có nghĩa "mọi Query đều phải có class"

Đừng biến CQRS thành ceremony.

Ví dụ một query rất đơn giản:

```python
def get_story_count(conn):
    return conn.execute(
        "SELECT COUNT(*) FROM stories"
    ).fetchone()[0]
```

Có thể hoàn toàn hợp lý.

CQRS là **separation of responsibility**, không phải bắt buộc tạo 100 class.

---

# 29. Command cũng không nhất thiết là class

Có thể:

```python
@dataclass(frozen=True)
class AddChapterCommand:
    story_id: UUID
    number: int
    title: str
    content: str
```

Nhưng cũng có thể sử dụng function/use case trực tiếp.

Điều quan trọng là boundary:

```text
Command
   ↓
Use Case
```

---

# 30. Một cấu trúc Python phù hợp

Với project của bạn:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── events.py
    │   │
    │   └── crawler/
    │
    ├── application/
    │   │
    │   ├── commands/
    │   │   ├── create_story.py
    │   │   ├── add_chapter.py
    │   │   ├── start_crawler.py
    │   │   └── pause_crawler.py
    │   │
    │   ├── queries/
    │   │   ├── story_list.py
    │   │   ├── chapter_list.py
    │   │   └── crawler_dashboard.py
    │   │
    │   └── ports/
    │
    ├── infrastructure/
    │   └── sqlite/
    │
    └── interface/
        └── cli/
```

---

# 31. Một cách tổ chức khác

Nếu application lớn hơn:

```text
application/
    commands/
    queries/

read_model/
    models.py
    repositories.py
    projections.py
```

Ví dụ:

```text
read_model/
    ├── story_list.py
    ├── chapter_list.py
    ├── crawler_dashboard.py
    └── reading_page.py
```

Điều này rất phù hợp với roadmap của chúng ta.

---

# 32. Command Flow

Ví dụ:

```text
CLI
 ↓
AddChapterCommand
 ↓
AddChapterUseCase
 ↓
StoryRepository
 ↓
Story Aggregate
 ↓
ChapterAdded
 ↓
Outbox
 ↓
Commit
```

---

# 33. Query Flow

```text
CLI
 ↓
GetChapterListQuery
 ↓
ReadRepository
 ↓
SQL
 ↓
ChapterListItem
```

Không đi qua:

```text
Aggregate
```

nếu không cần.

---

# 34. Hai flow cạnh nhau

Đây là sơ đồ quan trọng nhất của Buổi 36:

```text
                 ┌───────────────┐
                 │      CLI      │
                 └───────┬───────┘
                         │
             ┌───────────┴───────────┐
             │                       │
          COMMAND                  QUERY
             │                       │
             ▼                       ▼
        Use Case                Query Handler
             │                       │
             ▼                       ▼
          Domain                Read Model
             │                       │
        Aggregate                  SQL
             │                       │
             ▼                       ▼
       Write Repository        Read Repository
             │                       │
             └──────────┬────────────┘
                        ▼
                      SQLite
```

Đây chính là **CQRS đơn giản**.

---

# 35. CQRS + Outbox

Khi thêm kiến thức Buổi 35:

```text
                         COMMAND
                            │
                            ▼
                       USE CASE
                            │
                            ▼
                        AGGREGATE
                            │
                     Domain Event
                            │
                            ▼
                         OUTBOX
                            │
                         COMMIT
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
```

Đây là kiến trúc rất mạnh.

---

# 36. Eventual Consistency

Nếu Read Model được cập nhật bằng Event:

```text
AddChapter
    ↓
Write DB
    ↓
COMMIT
    ↓
Outbox
    ↓
Worker
    ↓
Read Model
```

sẽ có một khoảng thời gian:

```text
Write DB = mới
Read DB  = cũ
```

Ví dụ:

```text
10:00:00.000
Chapter 101 được lưu

10:00:00.100
Worker xử lý Event

10:00:00.200
Read Model cập nhật
```

Đây là:

> **Eventual Consistency**

---

# 37. Với SQLite cùng DB thì sao?

Nếu Read Model sử dụng cùng SQLite:

```text
stories
chapters
story_list
```

thì có thể cập nhật read model ngay trong cùng transaction nếu thiết kế phù hợp.

Khi đó:

```text
Write
 +
Read projection
```

có thể rất gần strong consistency.

Nhưng nếu dùng:

```text
Outbox → Worker
```

thì read model vẫn có eventual consistency.

---

# 38. CQRS không đồng nghĩa Event Sourcing

Đây là một hiểu nhầm rất phổ biến.

CQRS:

```text
Command ≠ Query
```

Event Sourcing:

```text
State được xây dựng từ Event history
```

Hai khái niệm khác nhau.

Có thể:

```text
CQRS
+
CRUD persistence
```

mà không có Event Sourcing.

Hoặc:

```text
CQRS
+
Event Sourcing
```

---

# 39. Kiến trúc chúng ta đang hướng tới

Sau 35 buổi:

```text
                    ┌──────────────┐
                    │     CLI      │
                    └──────┬───────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
             COMMAND               QUERY
                 │                   │
                 ▼                   ▼
             Use Case            Query Handler
                 │                   │
                 ▼                   ▼
              Domain            Read Model
                 │                   │
             Aggregate              SQL
                 │                   │
                 ▼                   ▼
            Repository         Read Repository
                 │                   │
                 ▼                   ▼
              SQLite             SQLite
                 │
                 ▼
              Outbox
                 │
                 ▼
              Worker
                 │
                 ▼
            Projections
                 │
                 └──────────→ Read Model
```

Đây là nền móng rất tốt để sau này xây **crawler dashboard**, **reading UI**, và **search**.

---

# 40. Bài tập Buổi 36

Hãy lấy hệ thống đọc truyện và phân loại:

### Commands

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
CompleteCrawler
UpdateReadingProgress
```

### Queries

```text
GetStoryList
GetStoryDetail
GetChapterList
GetReadingPage
GetCrawlerDashboard
GetReadingHistory
```

Sau đó tự hỏi:

> **Cái nào thay đổi business state?**

→ Command.

> **Cái nào chỉ lấy dữ liệu?**

→ Query.

---

# 41. Bài tập quan trọng hơn

Thiết kế:

```text
CrawlerDashboard
```

Dashboard cần:

```text
Source
Running Jobs
Completed Jobs
Failed Jobs
Last Crawl
Stories Found
Chapters Found
```

Đừng bắt đầu bằng:

```python
CrawlerJobRepository
```

rồi load hàng nghìn `CrawlerJob`.

Hãy thiết kế:

```text
CrawlerDashboardQuery
        ↓
Read Model
        ↓
SQL
        ↓
CrawlerDashboard
```

Ví dụ output:

```python
@dataclass(frozen=True)
class CrawlerDashboard:

    total_sources: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    stories_found: int
    chapters_found: int
```

Đây sẽ là nền tảng trực tiếp cho **Buổi 40 — CQRS thực chiến**.

---

# 42. Mental Model cần nhớ

Đừng nhớ CQRS bằng định nghĩa dài.

Chỉ cần nhớ:

```text
              CQRS

        ┌───────────────┐
        │               │
     COMMAND          QUERY
        │               │
      WRITE            READ
        │               │
     DOMAIN          READ MODEL
        │               │
   BUSINESS RULE       SQL
        │               │
    TRANSACTION       FAST
```

Và đặc biệt:

> **Command nói với hệ thống "hãy làm điều gì đó".**

> **Query hỏi hệ thống "cho tôi dữ liệu".**

---

## Preview Buổi 37

Buổi tiếp theo chúng ta sẽ đi sâu vào **Command Model**:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
```

và xây dựng flow chuẩn:

```text
Command
   ↓
Command Handler / Use Case
   ↓
Aggregate
   ↓
Repository
   ↓
Unit of Work
   ↓
Domain Event
   ↓
Outbox
```

Sau Buổi 37, bạn sẽ thấy rất rõ **Command khác Application Service/Use Case như thế nào**, một điểm thường gây nhầm lẫn khi học DDD + CQRS.
