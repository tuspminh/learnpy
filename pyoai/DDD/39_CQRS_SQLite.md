# DDD Deep Dive — Buổi 39

# CQRS với SQLite

Hôm nay chúng ta chuyển từ lý thuyết sang **thiết kế kiến trúc thật bằng Python + SQLite**.

Mục tiêu:

```text
Command Side                         Query Side
     │                                   │
     ▼                                   ▼
   Domain                             Read Model
     │                                   │
     ▼                                   ▼
Write Repository                  Read Repository
     │                                   │
     └──────────────┬────────────────────┘
                    ▼
                  SQLite
```

Điểm quan trọng:

> **CQRS không bắt buộc phải có 2 database.**

Ở giai đoạn này, chúng ta dùng **một SQLite database**, nhưng tách rõ **write model** và **read model** ở cấp kiến trúc.

---

# 1. CQRS trong project của chúng ta

Hệ thống đọc truyện:

```text
                         Application
                              │
              ┌───────────────┴───────────────┐
              │                               │
           COMMAND                          QUERY
              │                               │
              ▼                               ▼
        CreateStory                     StoryListQuery
        AddChapter                      ChapterListQuery
        StartCrawler                    ReadingPageQuery
        PauseCrawler                    CrawlerDashboard
              │                               │
              ▼                               ▼
           DOMAIN                        READ MODEL
              │                               │
              ▼                               ▼
      Write Repository                Read Repository
              │                               │
              └───────────────┬───────────────┘
                              ▼
                           SQLite
```

---

# 2. Cấu trúc project

Ta bắt đầu với:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── repository.py
    │   │
    │   └── chapter/
    │       ├── entities.py
    │       └── value_objects.py
    │
    ├── application/
    │   ├── commands/
    │   │   ├── create_story.py
    │   │   └── add_chapter.py
    │   │
    │   └── queries/
    │       ├── story_list.py
    │       └── reading_page.py
    │
    ├── read_model/
    │   ├── models.py
    │   └── repositories.py
    │
    ├── infrastructure/
    │   └── sqlite/
    │       ├── connection.py
    │       ├── schema.py
    │       └── repositories.py
    │
    └── interface/
        └── cli/
```

Hãy chú ý:

```text
domain/
    ↓
business

application/
    ↓
use case

read_model/
    ↓
query representation

infrastructure/
    ↓
SQLite

interface/
    ↓
CLI / GUI / HTTP
```

---

# 3. Write Model và Read Model

Đầu tiên hãy hình dung database:

```text
stories
chapters
crawler_jobs
crawler_sources
```

Đây là dữ liệu phục vụ **write side**.

Query có thể đọc trực tiếp từ những bảng này.

Như vậy:

```text
Write Model
      │
      └──────┐
             ▼
           SQLite
             ▲
             │
Read Model ──┘
```

Đây là **CQRS đơn giản**.

---

# 4. SQLite schema

Ví dụ:

```sql
CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

Chapter:

```sql
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    FOREIGN KEY (story_id)
        REFERENCES stories(id),

    UNIQUE(story_id, number)
);
```

Crawler:

```sql
CREATE TABLE crawler_jobs (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT
);
```

---

# 5. Connection Manager

Ta tạo:

```python
# infrastructure/sqlite/connection.py

import sqlite3


class SQLiteConnection:

    def __init__(self, database: str):
        self.database = database

    def connect(self):
        connection = sqlite3.connect(
            self.database
        )

        connection.row_factory = sqlite3.Row

        return connection
```

Sử dụng:

```python
db = SQLiteConnection("story.db")

connection = db.connect()
```

---

# 6. Domain không biết SQLite

Đây là nguyên tắc quan trọng.

Domain:

```python
class Story:
    ...
```

không được:

```python
import sqlite3
```

Không được:

```python
class Story:

    def save(self):
        sqlite3.connect(...)
```

Nếu làm vậy:

```text
Domain
  ↓
SQLite
```

Domain bị phụ thuộc infrastructure.

Sai dependency direction.

---

# 7. Domain Repository

Trong Domain:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id):
        pass

    @abstractmethod
    def add(self, story):
        pass

    @abstractmethod
    def save(self, story):
        pass
```

Domain chỉ biết:

```text
StoryRepository
```

không biết:

```text
SQLiteStoryRepository
```

---

# 8. SQLite Repository

Infrastructure implement interface:

```python
class SQLiteStoryRepository(StoryRepository):

    def __init__(self, connection):
        self.connection = connection

    def get(self, story_id):
        row = self.connection.execute(
            """
            SELECT
                id,
                title,
                source_id,
                status
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        ).fetchone()

        if row is None:
            return None

        return self._to_domain(row)

    def add(self, story):
        self.connection.execute(
            """
            INSERT INTO stories (
                id,
                title,
                source_id,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(story.id),
                story.title,
                str(story.source_id),
                story.status,
            ),
        )

    def save(self, story):
        self.connection.execute(
            """
            UPDATE stories
            SET title = ?,
                status = ?
            WHERE id = ?
            """,
            (
                story.title,
                story.status,
                str(story.id),
            ),
        )
```

---

# 9. Bây giờ xuất hiện Read Repository

Đây là phần quan trọng của Buổi 39.

Domain Repository:

```python
StoryRepository
```

không nhất thiết phải phục vụ Query.

Ta tạo:

```python
class StoryReadRepository:

    def list_stories(self):
        ...

    def get_reading_page(self, story_id, number):
        ...
```

Đây là repository dành riêng cho **Query Side**.

---

# 10. Read Model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryListItem:

    story_id: str
    title: str
    chapter_count: int
    latest_chapter: int | None
```

Đây là một object phục vụ query.

Nó không có:

```python
add_chapter()
publish()
archive()
```

Nó chỉ chứa data.

---

# 11. StoryReadRepository

```python
class SQLiteStoryReadRepository:

    def __init__(self, connection):
        self.connection = connection

    def list_stories(self):

        rows = self.connection.execute(
            """
            SELECT
                s.id,
                s.title,
                COUNT(c.id) AS chapter_count,
                MAX(c.number) AS latest_chapter
            FROM stories s
            LEFT JOIN chapters c
                ON c.story_id = s.id
            GROUP BY
                s.id,
                s.title
            ORDER BY
                s.updated_at DESC
            """
        ).fetchall()

        return [
            StoryListItem(
                story_id=row["id"],
                title=row["title"],
                chapter_count=row["chapter_count"],
                latest_chapter=row["latest_chapter"],
            )
            for row in rows
        ]
```

Chúng ta vừa có một Query Model thực sự.

---

# 12. Query Handler

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryListQuery:

    page: int = 1
    page_size: int = 20
```

Handler:

```python
class StoryListQueryHandler:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, query):

        return self.repository.list_stories(
            page=query.page,
            page_size=query.page_size,
        )
```

---

# 13. Flow hoàn chỉnh

Khi user muốn xem danh sách truyện:

```text
UI
 │
 ▼
StoryListQuery
 │
 ▼
StoryListQueryHandler
 │
 ▼
SQLiteStoryReadRepository
 │
 ▼
SELECT
 │
 ▼
StoryListItem
 │
 ▼
UI
```

Không có:

```text
Aggregate
Entity
Domain Service
Unit of Work
```

trong flow đọc đơn giản này.

---

# 14. Command Side

Ngược lại:

```text
CLI
 │
 ▼
CreateStoryCommand
 │
 ▼
CreateStoryUseCase
 │
 ▼
Story.create()
 │
 ▼
StoryRepository
 │
 ▼
SQLite
 │
 ▼
COMMIT
```

So sánh:

```text
COMMAND                         QUERY

CreateStoryCommand              StoryListQuery
       ↓                              ↓
Use Case                       Query Handler
       ↓                              ↓
Aggregate                     Read Repository
       ↓                              ↓
Repository                         SQL
       ↓                              ↓
SQLite                         Read Model
```

Đây chính là CQRS.

---

# 15. Không cần hai database

Một người mới học CQRS thường nghĩ:

```text
Write DB
Read DB
```

phải là:

```text
SQLite 1
SQLite 2
```

**Không đúng.**

Có thể bắt đầu:

```text
                SQLite
               /      \
              /        \
      Write Side      Read Side
```

Đây là cách rất hợp lý cho application desktop/local như app đọc truyện.

---

# 16. Khi nào cần Read Database riêng?

Khi hệ thống lớn hơn:

```text
Write DB
   │
   │ Events
   ▼
Projection Worker
   │
   ▼
Read DB
```

Ví dụ:

```text
PostgreSQL
    ↓
Kafka / RabbitMQ
    ↓
Read Projection
    ↓
PostgreSQL / Elasticsearch
```

Nhưng **chưa cần làm ngay**.

---

# 17. SQLite với Read Model

Một thiết kế thực tế:

```text
story.db

┌───────────────────────────┐
│ Write Tables              │
│                           │
│ stories                   │
│ chapters                  │
│ crawler_jobs              │
│ crawler_sources           │
│ users                     │
├───────────────────────────┤
│ Read Tables / Projections │
│                           │
│ story_list_projection     │
│ crawler_dashboard         │
└───────────────────────────┘
```

Đây là bước tiến gần hơn tới CQRS thực tế.

---

# 18. Read Projection là gì?

Ví dụ bảng:

```sql
CREATE TABLE story_list_projection (
    story_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    chapter_count INTEGER NOT NULL,
    latest_chapter INTEGER,
    updated_at TEXT NOT NULL
);
```

Thay vì mỗi lần query phải:

```sql
JOIN stories
JOIN chapters
COUNT()
MAX()
```

ta có thể:

```sql
SELECT *
FROM story_list_projection
ORDER BY updated_at DESC;
```

---

# 19. Hai cấp độ Read Model

### Level 1 — Query trực tiếp

```text
SQLite
   ↓
SELECT + JOIN + GROUP BY
   ↓
DTO
```

### Level 2 — Projection

```text
Domain Event
   ↓
Projection
   ↓
Read Table
   ↓
DTO
```

Chúng ta đang ở **Level 1**, chuẩn bị tiến tới Level 2.

---

# 20. Tại sao chưa cần Projection?

Vì:

```text
1 user
SQLite
desktop app
```

thì:

```sql
JOIN
GROUP BY
COUNT
```

thường đã đủ.

Không nên đưa:

```text
Event Bus
Outbox
Worker
Projection
```

vào mọi ứng dụng chỉ vì đang học CQRS.

DDD tốt không phải là:

> càng nhiều abstraction càng tốt.

Mà là:

> **abstraction phù hợp với complexity.**

---

# 21. Read Model cho ReadingPage

Ví dụ:

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

Repository:

```python
class SQLiteReadingRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_page(
        self,
        story_id,
        chapter_number,
    ):
        ...
```

Query SQL có thể lấy:

```text
story
chapter
previous
next
```

trong một query/read operation.

---

# 22. Query Model rất thích SQL

Đây là một điểm bạn nên nhớ.

Domain Model thích:

```python
story.add_chapter()
story.publish()
job.pause()
```

Read Model thích:

```sql
SELECT
JOIN
GROUP BY
ORDER BY
COUNT
MAX
MIN
LIMIT
OFFSET
```

Không cần cố biến SQL thành Object-Oriented Domain logic.

---

# 23. Một sai lầm phổ biến

Sai:

```python
stories = story_repository.list()

for story in stories:

    chapters = chapter_repository.list(
        story.id
    )

    ...
```

Đây dễ trở thành:

```text
1 query stories
+
N queries chapters
```

N+1.

Query Side nên tận dụng SQL:

```sql
SELECT
    s.id,
    s.title,
    COUNT(c.id),
    MAX(c.number)
FROM stories s
LEFT JOIN chapters c
    ON c.story_id = s.id
GROUP BY s.id;
```

---

# 24. Domain Repository và Read Repository khác nhau

Đừng cố tạo:

```python
class StoryRepository:

    get()
    save()
    add()
    list()
    search()
    dashboard()
    reading_page()
    statistics()
```

Repository sẽ trở thành **God Object**.

Tách:

```text
StoryRepository
    ↓
Domain persistence

StoryReadRepository
    ↓
Query persistence
```

---

# 25. Dependency Direction

Kiến trúc:

```text
             Domain
               ▲
               │
        Application
               ▲
               │
       Infrastructure
               ▲
               │
         Interface
```

Chính xác hơn:

```text
Interface
    ↓
Application
    ↓
Domain

Infrastructure
    └── implements ports
```

Read Side:

```text
Interface
    ↓
Query Handler
    ↓
Read Repository interface
    ↓
SQLite Read Repository
```

---

# 26. Interface cho Read Repository

Nếu muốn Dependency Inversion đầy đủ:

```python
from abc import ABC, abstractmethod


class StoryReadRepository(ABC):

    @abstractmethod
    def list_stories(
        self,
        page: int,
        page_size: int,
    ):
        pass
```

Infrastructure:

```python
class SQLiteStoryReadRepository(
    StoryReadRepository
):
    ...
```

---

# 27. Có cần đặt Read Repository trong Domain?

**Không nhất thiết.**

Đây là điểm khác với Domain Repository.

Có thể tổ chức:

```text
application/
    queries/
        story_list.py

read_model/
    repositories.py

infrastructure/
    sqlite/
        read_repositories.py
```

Vì Read Repository chủ yếu phục vụ Application Query.

---

# 28. Một kiến trúc sạch hơn

Tôi khuyên project của chúng ta dùng:

```text
src/story_app/

├── domain/
│
├── application/
│   ├── commands/
│   └── queries/
│
├── infrastructure/
│   └── sqlite/
│       ├── write_repositories.py
│       └── read_repositories.py
│
├── read_model/
│   ├── models.py
│   └── repositories.py
│
└── interface/
```

Trong đó:

```text
domain/
    business

application/
    use cases + queries

read_model/
    read DTO + read ports

infrastructure/
    SQLite implementation
```

---

# 29. Transaction chỉ nằm ở Write Side

Command:

```python
with uow:

    story = stories.get(story_id)

    story.add_chapter(chapter)

    stories.save(story)

    uow.commit()
```

Query:

```python
result = read_repository.list_stories()
```

Không cần:

```python
with uow:
```

cho query thông thường.

---

# 30. Một SQLite Connection có thể được dùng cho cả hai

Ví dụ composition root:

```python
connection = sqlite3.connect(
    "story.db"
)

write_repository = SQLiteStoryRepository(
    connection
)

read_repository = SQLiteStoryReadRepository(
    connection
)
```

Nhưng application không nên tự tạo connection.

Composition Root mới tạo:

```text
Infrastructure setup
        ↓
Repositories
        ↓
Use Cases
        ↓
CLI
```

---

# 31. Composition Root

Ví dụ:

```python
def build_application():

    connection = sqlite3.connect(
        "story.db"
    )

    story_repository = SQLiteStoryRepository(
        connection
    )

    story_read_repository = (
        SQLiteStoryReadRepository(
            connection
        )
    )

    create_story = CreateStoryUseCase(
        story_repository
    )

    story_list = StoryListQueryHandler(
        story_read_repository
    )

    return {
        "create_story": create_story,
        "story_list": story_list,
    }
```

Đây là Dependency Injection.

---

# 32. CQRS hoàn chỉnh trong SQLite

Ta có:

```text
                         APPLICATION
                              │
              ┌───────────────┴───────────────┐
              │                               │
           COMMAND                          QUERY
              │                               │
              ▼                               ▼
        CreateStory                     StoryListQuery
        AddChapter                      ChapterListQuery
        StartCrawler                    ReadingPageQuery
              │                               │
              ▼                               ▼
           DOMAIN                        READ MODEL
              │                               │
              ▼                               ▼
       Write Repository                Read Repository
              │                               │
              └───────────────┬───────────────┘
                              ▼
                           SQLite
```

Đây là **CQRS thực dụng**.

---

# 33. Đừng tách database quá sớm

Với app đọc truyện chạy local:

```text
PySide6
   ↓
Application
   ↓
SQLite
```

một DB là hợp lý.

Khi crawler trở thành hệ thống lớn:

```text
Crawler Worker
       ↓
Write DB
       ↓
Events
       ↓
Projection
       ↓
Read DB
       ↓
Dashboard
```

lúc đó mới cân nhắc tách.

---

# 34. Bài tập thực hành

Hãy tạo:

```text
read_model/
    models.py
```

và viết:

```python
@dataclass(frozen=True)
class StoryListItem:

    story_id: str
    title: str
    chapter_count: int
    latest_chapter: int | None
```

Tiếp theo:

```text
application/queries/
    story_list.py
```

viết:

```python
@dataclass(frozen=True)
class StoryListQuery:

    page: int = 1
    page_size: int = 20
```

và:

```python
class StoryListQueryHandler:
    ...
```

Cuối cùng:

```text
infrastructure/sqlite/
    read_repositories.py
```

implement:

```python
class SQLiteStoryReadRepository:
    ...
```

---

# 35. Bài tập kiến trúc

Hãy phân loại:

```text
Story
StoryRepository
SQLiteStoryRepository
StoryListQuery
StoryListQueryHandler
StoryListItem
SQLiteStoryReadRepository
CreateStoryCommand
CreateStoryUseCase
```

thành:

```text
Domain
Application
Read Model
Infrastructure
```

Đáp án:

```text
Domain
├── Story
└── StoryRepository

Application
├── StoryListQuery
├── StoryListQueryHandler
├── CreateStoryCommand
└── CreateStoryUseCase

Read Model
└── StoryListItem

Infrastructure
├── SQLiteStoryRepository
└── SQLiteStoryReadRepository
```

---

# 36. Mental Model quan trọng nhất

Sau Buổi 39, hãy nhớ hai đường:

```text
                 WRITE

Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Repository
   ↓
Transaction
   ↓
SQLite
```

và:

```text
                  READ

Query
   ↓
Query Handler
   ↓
Read Repository
   ↓
SQL
   ↓
Read Model
   ↓
UI
```

**Write Side quan tâm business consistency.**

**Read Side quan tâm query efficiency.**

---

# 37. Bước tiếp theo: CQRS thực chiến

Ở **Buổi 40**, chúng ta sẽ không chỉ `SELECT` trực tiếp nữa mà xây:

```text
                 CRAWLER
                    │
                    ▼
              CrawlerJob
                    │
                    ▼
             Domain Event
                    │
                    ▼
             CrawlerCompleted
                    │
                    ▼
               Projection
                    │
                    ▼
        ┌──────────────────────┐
        │ Crawler Dashboard    │
        │                      │
        │ Running:     3       │
        │ Completed: 820       │
        │ Failed:      7       │
        │ Stories:  2,500      │
        │ Chapters: 85,000     │
        └──────────────────────┘
```

Tức là chúng ta sẽ nối toàn bộ những thứ đã học:

```text
DDD
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
 ↓
CQRS
 ↓
Read Model
 ↓
Projection
 ↓
Crawler Dashboard
```

Đó sẽ là **Buổi 40 — CQRS thực chiến**, và là bài tổng hợp rất quan trọng của toàn bộ phần CQRS.
