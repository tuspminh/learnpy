# DDD Deep Dive — Buổi 38

# Query Model

Ở Buổi 36 ta học:

```text
Command → Write Model
Query   → Read Model
```

Ở Buổi 37 ta đi sâu vào:

```text
Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Repository
   ↓
Unit of Work
```

Hôm nay chúng ta đi nửa còn lại:

```text
Query
   ↓
Query Handler
   ↓
Read Model
   ↓
SQL
```

Đây là phần cực kỳ quan trọng nếu bạn muốn xây **dashboard crawler, trang đọc truyện, tìm kiếm và các màn hình UI phức tạp**.

---

# 1. Query Model là gì?

Query Model là mô hình dữ liệu được thiết kế để:

> **phục vụ việc đọc dữ liệu.**

Nó không phải Domain Model.

Ví dụ Domain:

```text
Story
 ├── StoryId
 ├── StoryTitle
 ├── SourceId
 └── Status
```

Nhưng UI Story List cần:

```text
StoryListItem
 ├── story_id
 ├── title
 ├── source_name
 ├── chapter_count
 ├── latest_chapter
 └── updated_at
```

Hai model có mục đích khác nhau.

---

# 2. Query Model không cần bảo vệ business invariant

Domain Entity:

```python
story.add_chapter(chapter)
```

có thể phải kiểm tra:

```text
chapter number duplicate?
story có active?
chapter number hợp lệ?
```

Nhưng Read Model:

```python
StoryListItem(
    id="...",
    title="...",
    chapter_count=100,
)
```

không cần các business behavior đó.

Nó chỉ là:

```text
DATA FOR READING
```

---

# 3. Bốn Query Model của hệ thống đọc truyện

Ta sẽ thiết kế:

```text
StoryList
ChapterList
CrawlerDashboard
ReadingPage
```

Mỗi cái phục vụ một use case đọc khác nhau.

---

# 4. StoryList

UI:

```text
Danh sách truyện
──────────────────────────────

Đấu Phá Thương Khung     1200 chương
Phàm Nhân Tu Tiên          850 chương
Tiên Nghịch               1000 chương
```

Read Model:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryListItem:

    story_id: str
    title: str
    source_name: str
    chapter_count: int
    latest_chapter: int
```

Đây không phải:

```python
Story
```

mà là:

```text
StoryListItem
```

---

# 5. Tại sao không trả Story Entity?

Cách truyền thống:

```python
stories = story_repository.list()

for story in stories:
    print(
        story.title,
        len(story.chapters),
    )
```

Có thể gây ra:

```text
1000 stories
     ↓
1000 Story objects
     ↓
load chapters
     ↓
memory lớn
     ↓
N+1 queries
```

CQRS cho phép:

```text
StoryListQuery
       ↓
SQL
       ↓
StoryListItem
```

---

# 6. Query Model có thể rất phẳng

SQL:

```sql
SELECT
    s.id,
    s.title,
    src.name AS source_name,
    COUNT(c.id) AS chapter_count,
    MAX(c.number) AS latest_chapter
FROM stories s
JOIN sources src
    ON src.id = s.source_id
LEFT JOIN chapters c
    ON c.story_id = s.id
GROUP BY
    s.id,
    s.title,
    src.name;
```

Kết quả:

```text
id | title | source | count | latest
```

Sau đó map:

```python
StoryListItem(...)
```

Đây chính là sức mạnh của Query Model.

---

# 7. ChapterList

UI:

```text
Đấu Phá Thương Khung

Chương 1200
Chương 1199
Chương 1198
Chương 1197
...
```

Read Model:

```python
@dataclass(frozen=True)
class ChapterListItem:

    chapter_id: str
    story_id: str
    number: int
    title: str
    published_at: str | None
```

Không cần:

```text
Chapter Entity
Story Aggregate
```

nếu chỉ cần hiển thị danh sách.

---

# 8. CrawlerDashboard

Đây là Query Model rất điển hình.

UI:

```text
Crawler Dashboard
──────────────────────────────────

Sources              10
Running Jobs           3
Completed Jobs       820
Failed Jobs            7

Stories Found       2,500
Chapters Found     85,000
```

Read Model:

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

Một object phục vụ đúng một màn hình.

---

# 9. ReadingPage

Đây là Query Model thú vị nhất.

Trang đọc truyện cần:

```text
Tên truyện
Tên chapter
Chapter number
Content
Previous chapter
Next chapter
```

Ta có:

```python
@dataclass(frozen=True)
class ReadingPage:

    story_id: str
    story_title: str

    chapter_id: str
    chapter_number: int
    chapter_title: str
    content: str

    previous_chapter: int | None
    next_chapter: int | None
```

Notice:

`ReadingPage` không phải Entity.

Nó là **view-specific read model**.

---

# 10. Một Query Model có thể tổng hợp nhiều bảng

Ví dụ:

```text
ReadingPage
```

có thể lấy từ:

```text
stories
chapters
reading_progress
```

SQL có thể:

```sql
SELECT
    s.id,
    s.title,
    c.id,
    c.number,
    c.title,
    c.content
FROM stories s
JOIN chapters c
    ON c.story_id = s.id
WHERE
    s.id = ?
    AND c.number = ?;
```

Thậm chí có thể JOIN thêm:

```text
reading_progress
```

hoặc các bảng khác.

Domain Aggregate không cần biết chuyện này.

---

# 11. Query Handler

Giống Command Handler, Query có Handler.

Ví dụ:

```python
class GetStoryListQueryHandler:

    def __init__(self, repository):
        self.repository = repository

    def execute(self):
        return self.repository.get_story_list()
```

Flow:

```text
GetStoryList
      ↓
Query Handler
      ↓
Read Repository
      ↓
SQL
      ↓
StoryListItem
```

---

# 12. Query không nhất thiết phải đi qua Domain

Đây là nguyên tắc quan trọng nhất của Query Model.

Command:

```text
Command
 ↓
Domain
```

Query:

```text
Query
 ↓
Read Model
```

Không cần:

```text
Query
 ↓
Aggregate
 ↓
Repository
```

---

# 13. Tại sao?

Vì Domain Model được thiết kế để:

```text
behavior
invariant
business rule
consistency
```

Read Model được thiết kế để:

```text
projection
filter
sort
pagination
report
dashboard
```

Hai mục tiêu khác nhau.

---

# 14. Query có thể bypass Repository Domain

Ví dụ Domain Repository:

```python
class StoryRepository(ABC):

    def get(self, story_id):
        ...

    def save(self, story):
        ...
```

Đây là Repository cho Domain.

Read Repository có thể hoàn toàn khác:

```python
class StoryReadRepository:

    def list_stories(self):
        ...

    def get_reading_page(self, story_id, number):
        ...
```

Đừng cố ép:

```text
StoryRepository
```

phục vụ tất cả Query.

---

# 15. Read Repository

Ví dụ:

```python
class StoryReadRepository:

    def __init__(self, connection):
        self.connection = connection

    def list_stories(self):
        rows = self.connection.execute(
            """
            SELECT
                s.id,
                s.title,
                COUNT(c.id)
            FROM stories s
            LEFT JOIN chapters c
                ON c.story_id = s.id
            GROUP BY s.id
            """
        )

        return [
            StoryListItem(
                story_id=row[0],
                title=row[1],
                source_name="...",
                chapter_count=row[2],
                latest_chapter=None,
            )
            for row in rows
        ]
```

---

# 16. Query Model và Pagination

Đây là lợi ích lớn.

Ví dụ:

```text
StoryList
page = 1
size = 20
```

SQL:

```sql
SELECT ...
FROM stories
ORDER BY updated_at DESC
LIMIT ?
OFFSET ?;
```

Không cần:

```python
all_stories = repository.list()
```

rồi:

```python
all_stories[0:20]
```

Nếu có:

```text
1,000,000 stories
```

thì cách thứ hai rất tệ.

---

# 17. Query Model + Filtering

Ví dụ:

```text
Tìm truyện:
- source = site_a
- status = completed
- chapters > 100
```

Query:

```sql
SELECT ...
FROM stories s
WHERE
    s.source_id = ?
    AND s.status = ?
ORDER BY s.updated_at DESC
LIMIT ? OFFSET ?;
```

Read Model rất phù hợp với kiểu query này.

---

# 18. Query Model + Sorting

UI có thể yêu cầu:

```text
sort = latest
sort = chapter_count
sort = title
```

Query layer chịu trách nhiệm:

```text
Query
 ↓
SQL ORDER BY
 ↓
Read Model
```

Domain không cần biết UI muốn sort theo cái gì.

---

# 19. Query DTO

Ta có thể định nghĩa:

```python
@dataclass(frozen=True)
class StoryListQuery:

    page: int = 1
    page_size: int = 20
    search: str | None = None
```

Đây là **Query DTO**.

Nó mô tả:

> Tôi muốn đọc dữ liệu như thế nào.

---

# 20. Query Result

Có thể trả:

```python
@dataclass(frozen=True)
class StoryListResult:

    items: list[StoryListItem]
    page: int
    page_size: int
    total: int
```

UI nhận:

```text
items
total
pagination
```

---

# 21. Query Input và Output

Ta có:

```text
Query
  ↓
Input
```

và:

```text
Read Model
  ↓
Result
```

Ví dụ:

```python
query = StoryListQuery(
    page=2,
    page_size=20,
    search="đấu",
)
```

Result:

```python
StoryListResult(
    items=[...],
    page=2,
    page_size=20,
    total=37,
)
```

---

# 22. Query hoàn chỉnh

```python
@dataclass(frozen=True)
class StoryListQuery:

    page: int = 1
    page_size: int = 20
    search: str | None = None


class StoryListQueryHandler:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        query: StoryListQuery,
    ):
        return self.repository.search(
            search=query.search,
            page=query.page,
            page_size=query.page_size,
        )
```

---

# 23. Kiến trúc Query Side

Ta có:

```text
application/
    queries/
        story_list.py
        chapter_list.py
        crawler_dashboard.py
        reading_page.py
```

và:

```text
read_model/
    models.py
    repositories.py
```

Flow:

```text
CLI / UI
   ↓
Query DTO
   ↓
Query Handler
   ↓
Read Repository
   ↓
SQLite
   ↓
Read Model DTO
```

---

# 24. Query Model không nhất thiết phải có Domain Layer

Ví dụ:

```text
ReadingPage
```

có thể chỉ tồn tại ở:

```text
read_model/
```

vì nó là representation dành cho reading UI.

Không cần:

```text
domain/reading_page.py
```

trừ khi `ReadingPage` thực sự mang business meaning.

---

# 25. Domain Model vs Read Model

So sánh:

| Domain Model     | Read Model       |
| ---------------- | ---------------- |
| Business-centric | UI/query-centric |
| Behavior         | Data             |
| Invariant        | Projection       |
| Aggregate        | DTO              |
| Entity           | Read Model       |
| Value Object     | Primitive/DTO    |
| Transaction      | Query            |
| Consistency      | Performance      |

---

# 26. Một ví dụ rất quan trọng

Domain:

```python
class Story:

    def add_chapter(self, chapter):
        if chapter.number in self._chapters:
            raise DuplicateChapterError()

        self._chapters.append(chapter)
```

Read Model:

```python
@dataclass(frozen=True)
class StoryListItem:

    story_id: str
    title: str
    chapter_count: int
```

Read Model **không cần**:

```python
add_chapter()
```

vì nó không thay đổi state.

---

# 27. Read Model có thể denormalize

Write DB:

```text
stories
chapters
sources
crawler_jobs
```

Read Model:

```text
story_list_projection
```

có thể:

```text
story_id
title
source_name
chapter_count
latest_chapter
last_crawled
```

Dữ liệu được tổng hợp sẵn.

Query:

```sql
SELECT *
FROM story_list_projection;
```

rất nhanh.

---

# 28. Projection

Projection là quá trình:

```text
Write State / Event
        ↓
     Projection
        ↓
     Read Model
```

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
CrawlerCompleted
     ↓
CrawlerDashboardProjection
     ↓
completed_jobs += 1
```

---

# 29. CQRS + Event

Kiến trúc:

```text
                 WRITE SIDE

Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Domain Event
   ↓
Outbox
   ↓
Worker
   │
   ├──────────────┐
   ▼              ▼
StoryList      Dashboard
Projection     Projection
   │              │
   ▼              ▼
Read Model      Read Model
```

Đây chính là cầu nối giữa:

```text
Buổi 35 — Outbox
```

và:

```text
Buổi 40 — CQRS thực chiến
```

---

# 30. Một Read Model có thể phục vụ một màn hình

Đây là tư duy rất hữu ích.

Thay vì:

```text
Một Model cho toàn application
```

ta có:

```text
StoryList
ChapterList
ReadingPage
CrawlerDashboard
```

Mỗi cái được tối ưu cho một nhu cầu.

Ví dụ:

```text
StoryList
→ tối ưu danh sách

ChapterList
→ tối ưu pagination

ReadingPage
→ tối ưu đọc chapter

CrawlerDashboard
→ tối ưu aggregation
```

---

# 31. Query Model có thể khác hoàn toàn Write Model

Write:

```text
Story
Chapter
CrawlerJob
CrawlerSource
User
```

Read:

```text
StoryListItem
ReadingPage
CrawlerDashboard
CrawlerJobStatus
```

Không cần mapping:

```text
Story → StoryListItem
```

theo kiểu 1-1.

Có thể:

```text
Story
Chapter
CrawlerJob
CrawlerSource
    ↓
    JOIN
    ↓
CrawlerDashboard
```

---

# 32. Đây là một tư duy rất quan trọng

Đừng hỏi:

> "Domain Entity nào tương ứng với màn hình này?"

Hãy hỏi:

> **"Màn hình này cần dữ liệu gì?"**

Ví dụ `CrawlerDashboard` cần:

```text
running
completed
failed
stories
chapters
```

Sau đó thiết kế Read Model:

```python
CrawlerDashboard(...)
```

Đây là tư duy CQRS.

---

# 33. Query Model và UI

Ví dụ CLI:

```python
result = handler.execute(
    StoryListQuery(page=1)
)

for item in result.items:
    print(
        item.title,
        item.chapter_count,
    )
```

PySide6 cũng tương tự:

```text
Query
 ↓
StoryListResult
 ↓
QAbstractTableModel
 ↓
QTableView
```

UI không cần biết:

```text
Aggregate
Repository Domain
UnitOfWork
```

---

# 34. Query Model + PySide6

Sau này khi kết hợp với PySide6:

```text
QTableView
    ↓
StoryListViewModel
    ↓
GetStoryListQuery
    ↓
Query Handler
    ↓
Read Repository
    ↓
SQLite
```

Đây là kiến trúc rất phù hợp với app đọc truyện của bạn.

---

# 35. Query Side không cần Unit of Work

Thông thường:

```text
Command
 ↓
Unit of Work
 ↓
Transaction
```

Query:

```text
Query
 ↓
Read Repository
 ↓
SELECT
```

Không cần:

```text
BEGIN
COMMIT
ROLLBACK
```

nếu chỉ đọc.

---

# 36. Query Side không phát Domain Event

Ví dụ:

```text
GetStoryList
```

không nên:

```text
StoryListViewed
```

rồi làm business operation, trừ khi bạn **cố ý** có telemetry/audit riêng.

Nguyên tắc cơ bản:

```text
Query
    ↓
READ ONLY
```

---

# 37. CQRS đơn giản nhất

Không cần Event Bus.

Không cần Outbox.

Không cần database riêng.

Chỉ cần:

```text
                    Application
                         │
              ┌──────────┴──────────┐
              │                     │
           Commands              Queries
              │                     │
              ▼                     ▼
          Domain               Read Model
              │                     │
              ▼                     ▼
        Write Repository      Read Repository
              │                     │
              └──────────┬──────────┘
                         ▼
                       SQLite
```

Đây là CQRS mà chúng ta sẽ triển khai trước.

---

# 38. CQRS nâng cao

Sau đó mới tiến tới:

```text
                    WRITE
                      │
                  Aggregate
                      │
                  Domain Event
                      │
                    Outbox
                      │
                    Worker
                      │
              ┌───────┴────────┐
              ▼                ▼
        Story Projection   Crawler Projection
              │                │
              ▼                ▼
          Read DB          Read DB
              │                │
              └───────┬────────┘
                      ▼
                    QUERY
```

---

# 39. Thiết kế 4 Query Model

Từ giờ hệ thống của chúng ta có thể định nghĩa:

```text
read_model/

├── story_list.py
├── chapter_list.py
├── crawler_dashboard.py
└── reading_page.py
```

### StoryList

```python
@dataclass(frozen=True)
class StoryListItem:
    story_id: str
    title: str
    source_name: str
    chapter_count: int
```

### ChapterList

```python
@dataclass(frozen=True)
class ChapterListItem:
    chapter_id: str
    number: int
    title: str
```

### CrawlerDashboard

```python
@dataclass(frozen=True)
class CrawlerDashboard:
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
```

### ReadingPage

```python
@dataclass(frozen=True)
class ReadingPage:
    story_title: str
    chapter_number: int
    chapter_title: str
    content: str
    previous_chapter: int | None
    next_chapter: int | None
```

---

# 40. Project structure

Sau Buổi 38, project có thể bắt đầu như sau:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   ├── chapter/
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
    │   └── queries/
    │       ├── story_list.py
    │       ├── chapter_list.py
    │       ├── crawler_dashboard.py
    │       └── reading_page.py
    │
    ├── read_model/
    │   ├── models.py
    │   ├── repositories.py
    │   └── projections.py
    │
    ├── infrastructure/
    │   └── sqlite/
    │
    └── interface/
        └── cli/
```

Đây là cấu trúc chúng ta sẽ phát triển ở **Buổi 39**.

---

# 41. Bài tập Buổi 38

Thiết kế 4 Query:

### Query 1

```text
GetStoryListQuery
```

Input:

```text
page
page_size
search
```

Output:

```text
StoryListResult
```

---

### Query 2

```text
GetChapterListQuery
```

Input:

```text
story_id
page
page_size
```

Output:

```text
ChapterListResult
```

---

### Query 3

```text
GetCrawlerDashboardQuery
```

Input:

```text
không cần
```

Output:

```text
CrawlerDashboard
```

---

### Query 4

```text
GetReadingPageQuery
```

Input:

```text
story_id
chapter_number
```

Output:

```text
ReadingPage
```

---

# 42. Bài tập tư duy

Hãy trả lời:

### `Story` có phải Read Model không?

**Không.**

Nó là Domain Entity/Aggregate.

### `StoryListItem` có phải Domain Entity không?

**Không.**

Nó là Read Model.

### Query có cần Aggregate không?

**Không nhất thiết.**

### Query có thể JOIN nhiều bảng không?

**Có.**

### Read Model có thể denormalize không?

**Có.**

### Read Model có thể chỉ phục vụ một màn hình không?

**Có, và đó thường là một thiết kế rất tốt.**

---

# 43. Mental Model của Buổi 38

Hãy nhớ:

```text
                 WRITE SIDE

Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Business Rules
   ↓
Repository
   ↓
Transaction


                  READ SIDE

Query
   ↓
Query Handler
   ↓
Read Repository
   ↓
SQL
   ↓
Read Model
```

Và điểm quan trọng nhất:

> **Write Model được thiết kế để bảo vệ business.**

> **Read Model được thiết kế để phục vụ việc đọc.**

Đừng cố dùng một model để làm cả hai.

---

## Sau Buổi 38

Ta đã có:

```text
DDD
 │
 ├── Domain Model
 │
 ├── Aggregate
 │
 ├── Repository
 │
 ├── Unit of Work
 │
 ├── Domain Event
 │
 └── Outbox
        │
        ▼
       CQRS
      /     \
 Command   Query
    │         │
 Write       Read
 Model       Model
```

**Buổi 39** sẽ bắt đầu phần rất thực chiến: **CQRS với SQLite**, thiết kế cụ thể:

```text
domain/
application/
infrastructure/
read_model/
```

và chúng ta sẽ xây **Write Side + Read Side cùng sử dụng SQLite**, trước khi sang Buổi 40 tách riêng Read Model cho **Crawler Dashboard**.
