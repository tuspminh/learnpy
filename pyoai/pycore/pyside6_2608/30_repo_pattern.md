# Phần III — UI Architecture

# Buổi 30 — Repository Pattern

Ở Buổi 29 chúng ta đã xây:

```text
View
   ↓
Controller
   ↓
Service
   ↓
Domain
```

Nhưng Service vẫn cần lưu dữ liệu.

Nếu viết:

```python
class StoryService:

    def __init__(self):
        self.conn = sqlite3.connect("story.db")
```

thì Service đã biết quá nhiều về database.

Hôm nay chúng ta giải quyết vấn đề đó bằng **Repository Pattern**.

---

# 1. Repository là gì?

Mental Model đơn giản nhất:

> **Repository là abstraction đại diện cho việc lưu trữ và truy xuất Domain Object.**

Ví dụ:

```text
StoryService
     │
     ▼
StoryRepository
     │
     ▼
SQLiteStoryRepository
     │
     ▼
SQLite
```

Service chỉ biết:

```python
repository.save(story)
repository.get(story_id)
repository.delete(story_id)
```

Service **không biết**:

```text
SQL
sqlite3.Connection
cursor
table
JOIN
```

---

# 2. Tại sao cần Repository?

Không có Repository:

```text
Controller
    ↓
Service
    ↓
sqlite3
    ↓
SQL
```

Service bị coupling với SQLite.

Sau này muốn:

```text
SQLite
↓
PostgreSQL
```

Service phải sửa.

---

Có Repository:

```text
Controller
    ↓
Service
    ↓
Repository Interface
    ↓
SQLiteRepository
```

Sau này:

```text
                   Repository
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       SQLiteRepository    PostgreSQLRepository
```

Service không cần thay đổi.

---

# 3. Repository không phải Database Manager

Đây là một distinction rất quan trọng.

### Database Manager

Quan tâm:

```text
connection
transaction
commit
rollback
execute
```

Ví dụ:

```python
db.execute(...)
db.commit()
```

### Repository

Quan tâm:

```text
Story
Chapter
User
```

Ví dụ:

```python
story_repository.save(story)
chapter_repository.get(chapter_id)
```

Nói ngắn gọn:

```text
Database Manager
    ↓
database infrastructure

Repository
    ↓
domain/application data access
```

---

# 4. Repository không nên trả raw tuple

Không nên:

```python
row = cursor.fetchone()

return row
```

Service nhận:

```python
(
    1,
    "Harry Potter",
    "J.K Rowling"
)
```

Service phải biết:

```text
column 0 = id
column 1 = title
column 2 = author
```

Đây là coupling với database schema.

Tốt hơn:

```python
return Story(
    id=row["id"],
    title=row["title"],
    author=row["author"],
)
```

Repository chuyển:

```text
Database Row
     ↓
Domain Object
```

---

# 5. Repository Interface

Ta bắt đầu với abstraction:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        ...

    @abstractmethod
    def get(self, story_id):
        ...

    @abstractmethod
    def delete(self, story_id):
        ...

    @abstractmethod
    def list_all(self):
        ...
```

Đây là **Port**.

Implementation:

```text
StoryRepository
       ▲
       │
SQLiteStoryRepository
```

---

# 6. SQLite implementation

Ví dụ:

```python
import sqlite3


class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection
```

Implement:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(self, story):
        self.connection.execute(
            """
            INSERT INTO stories (title)
            VALUES (?)
            """,
            (story.title,),
        )

    def get(self, story_id):
        cursor = self.connection.execute(
            """
            SELECT id, title
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Story(
            id=row[0],
            title=row[1],
        )
```

---

# 7. Nhưng Repository có nên commit?

Đây là câu hỏi rất hay.

Nếu:

```python
repository.save(story)
```

tự:

```python
connection.commit()
```

thì transaction khó kiểm soát.

Ví dụ:

```text
CreateStory
 ├── save Story
 ├── save Metadata
 └── save Chapter
```

Nếu mỗi repository tự commit:

```text
save Story
 ↓
COMMIT

save Metadata
 ↓
COMMIT

save Chapter
 ↓
ERROR
```

Database đã ở trạng thái dở dang.

---

# 8. Transaction Boundary

Tốt hơn:

```text
Application Service
       │
       ▼
   transaction
       │
       ├── repository.save()
       ├── metadata.save()
       └── chapter.save()
       │
       ▼
     commit
```

Repository thực hiện SQL nhưng **không nhất thiết tự commit**.

Đây là lý do Application Layer và Database Manager cần được thiết kế cẩn thận.

---

# 9. Repository và Domain

Ví dụ Domain:

```python
class Story:

    def __init__(
        self,
        title,
        story_id=None,
    ):
        title = title.strip()

        if not title:
            raise ValueError(
                "Title is required"
            )

        self.id = story_id
        self.title = title
```

Repository:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Repository không quyết định:

```text
Title có hợp lệ?
Story có được publish?
Chapter có hợp lệ?
```

Đó là trách nhiệm của Domain.

---

# 10. Repository và Service

Service:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository

    def create_story(self, title):

        story = Story(title)

        if self.repository.exists(title):
            raise ValueError(
                "Story already exists"
            )

        self.repository.save(story)

        return story
```

Repository:

```python
class SQLiteStoryRepository:

    def exists(self, title):
        cursor = self.connection.execute(
            """
            SELECT 1
            FROM stories
            WHERE title = ?
            LIMIT 1
            """,
            (title,),
        )

        return cursor.fetchone() is not None
```

Luồng:

```text
StoryService
     │
     │ exists(title)
     ▼
Repository
     │
     ▼
SQLite
```

---

# 11. Repository Method nên mang ngôn ngữ Domain

Không nên:

```python
repository.execute_sql(
    "SELECT ..."
)
```

Đó không phải abstraction.

Tốt:

```python
repository.get(story_id)
repository.save(story)
repository.delete(story_id)
repository.exists(title)
```

Tên method nên nói:

> **Ứng dụng muốn làm gì với object?**

không phải:

> **Database đang chạy câu SQL nào?**

---

# 12. Generic Repository có tốt không?

Bạn có thể thấy:

```python
class Repository:

    def save(self, obj):
        ...

    def get(self, id):
        ...

    def delete(self, id):
        ...
```

Có vẻ rất tiện.

Nhưng trong DDD/Application Architecture, generic repository thường không phải lúc nào cũng tốt.

Ví dụ:

```python
repository.get(10)
```

Không nói rõ:

```text
get Story?
get Chapter?
get User?
```

Tốt hơn:

```python
story_repository.get(10)
chapter_repository.get(10)
```

Code rõ nghĩa hơn.

---

# 13. Repository per Aggregate

Nếu dùng DDD, một cách phổ biến là:

```text
StoryRepository
ChapterRepository
UserRepository
```

Nhưng cần hiểu:

> Repository thường gắn với **Aggregate**, không đơn giản chỉ với database table.

Ví dụ:

```text
Story
 ├── Chapter
 ├── Chapter
 └── Chapter
```

Nếu `Story` là Aggregate Root, có thể thiết kế:

```python
story_repository.save(story)
```

và việc persistence của chapters có thể được Repository xử lý bên dưới.

Không nhất thiết phải expose:

```python
story_chapter_table.insert(...)
```

cho Application Layer.

---

# 14. Repository không phải ORM

Repository Pattern không đồng nghĩa với:

```text
SQLAlchemy
Django ORM
Peewee
```

Bạn hoàn toàn có thể viết Repository bằng raw SQL:

```python
class SQLiteStoryRepository:

    def save(self, story):
        self.connection.execute(
            "INSERT INTO stories(title) VALUES(?)",
            (story.title,),
        )
```

Đây chính là hướng phù hợp với project của bạn vì bạn đang muốn học:

```text
sqlite3
raw SQL
Repository Pattern
```

---

# 15. Repository + SQLite Manager

Một architecture tốt:

```text
StoryService
      │
      ▼
StoryRepository
      │
      ▼
SQLiteStoryRepository
      │
      ▼
DatabaseManager
      │
      ▼
sqlite3.Connection
```

DatabaseManager:

```python
class DatabaseManager:

    def __init__(self, path):
        self.connection = sqlite3.connect(
            path
        )
```

Repository:

```python
class SQLiteStoryRepository:

    def __init__(self, db):
        self.db = db

    def get(self, story_id):
        cursor = self.db.connection.execute(
            ...
        )
```

---

# 16. Database Manager không nên biết Story

Đây là boundary quan trọng.

DatabaseManager:

```python
class DatabaseManager:

    def execute(self, sql, params=()):
        return self.connection.execute(
            sql,
            params,
        )
```

Nó không nên có:

```python
get_story()
save_story()
delete_story()
```

Nếu có:

```text
DatabaseManager
 ├── get_story
 ├── save_story
 ├── delete_story
 ├── get_chapter
 ├── save_chapter
 └── ...
```

thì DatabaseManager đang biến thành God Object.

---

# 17. Repository chịu trách nhiệm mapping

Database:

```text
id | title
---+------------
1  | Story A
```

Repository:

```text
SQLite Row
    ↓
Story
```

Ví dụ:

```python
def _to_domain(self, row):
    if row is None:
        return None

    return Story(
        story_id=row["id"],
        title=row["title"],
    )
```

và:

```python
def _to_row(self, story):
    return (
        story.title,
    )
```

Đây là **Data Mapping**.

---

# 18. Một Repository hoàn chỉnh hơn

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def get(self, story_id):
        cursor = self.connection.execute(
            """
            SELECT id, title
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        )

        row = cursor.fetchone()

        return self._to_domain(row)

    def exists(self, title):
        cursor = self.connection.execute(
            """
            SELECT 1
            FROM stories
            WHERE title = ?
            LIMIT 1
            """,
            (title,),
        )

        return cursor.fetchone() is not None

    def save(self, story):
        if story.id is None:
            cursor = self.connection.execute(
                """
                INSERT INTO stories(title)
                VALUES(?)
                """,
                (story.title,),
            )

            story.id = cursor.lastrowid

        else:
            self.connection.execute(
                """
                UPDATE stories
                SET title = ?
                WHERE id = ?
                """,
                (
                    story.title,
                    story.id,
                ),
            )

    def delete(self, story_id):
        self.connection.execute(
            """
            DELETE FROM stories
            WHERE id = ?
            """,
            (story_id,),
        )

    @staticmethod
    def _to_domain(row):
        if row is None:
            return None

        return Story(
            story_id=row["id"],
            title=row["title"],
        )
```

---

# 19. `row_factory`

Với SQLite, nên sử dụng:

```python
connection.row_factory = sqlite3.Row
```

Sau đó:

```python
row["id"]
row["title"]
```

thay vì:

```python
row[0]
row[1]
```

Ví dụ:

```python
connection = sqlite3.connect(
    "story.db"
)

connection.row_factory = sqlite3.Row
```

Repository trở nên dễ đọc hơn:

```python
return Story(
    story_id=row["id"],
    title=row["title"],
)
```

---

# 20. Repository và Pagination

Project Story Reader chắc chắn sẽ cần pagination.

Không nên để UI tự viết:

```sql
SELECT ...
LIMIT 20 OFFSET 40
```

Không nên để Service biết SQL.

Repository:

```python
def list(
    self,
    limit=20,
    offset=0,
):
    cursor = self.connection.execute(
        """
        SELECT id, title
        FROM stories
        ORDER BY id
        LIMIT ?
        OFFSET ?
        """,
        (limit, offset),
    )

    return [
        self._to_domain(row)
        for row in cursor.fetchall()
    ]
```

Service:

```python
stories = repository.list(
    limit=20,
    offset=40,
)
```

UI:

```text
Page 3
```

không cần biết SQL.

---

# 21. Search

Tương tự:

```python
repository.search(
    keyword="Harry"
)
```

Repository:

```python
def search(self, keyword):
    cursor = self.connection.execute(
        """
        SELECT id, title
        FROM stories
        WHERE title LIKE ?
        ORDER BY title
        """,
        (f"%{keyword}%",),
    )

    return [
        self._to_domain(row)
        for row in cursor.fetchall()
    ]
```

---

# 22. Filter

Ví dụ:

```python
repository.list(
    status="completed"
)
```

Repository xử lý:

```sql
WHERE status = ?
```

UI không cần biết.

---

# 23. Repository và Query Object

Khi query phức tạp, method:

```python
list(
    status=None,
    author=None,
    keyword=None,
    min_chapters=None,
    ...
)
```

sẽ trở nên xấu.

Có thể tạo:

```python
@dataclass
class StoryQuery:
    keyword: str | None = None
    status: str | None = None
    author_id: int | None = None
    limit: int = 20
    offset: int = 0
```

Repository:

```python
def search(self, query: StoryQuery):
    ...
```

Đây là hướng rất hữu ích cho app lớn.

---

# 24. Repository và Test

Đây là một trong những lý do quan trọng nhất để dùng Repository.

Production:

```text
StoryService
     ↓
SQLiteStoryRepository
```

Test:

```text
StoryService
     ↓
FakeStoryRepository
```

Ví dụ:

```python
class FakeStoryRepository:

    def __init__(self):
        self.items = {}

    def save(self, story):
        self.items[story.id] = story

    def get(self, story_id):
        return self.items.get(story_id)

    def exists(self, title):
        return any(
            story.title == title
            for story in self.items.values()
        )
```

Service test:

```python
def test_create_story():

    repository = FakeStoryRepository()

    service = StoryService(
        repository
    )

    story = service.create_story(
        "Python"
    )

    assert story.title == "Python"
```

Không cần SQLite.

---

# 25. SQLite Repository Test

Ngoài unit test bằng Fake, Repository bản thân nó cần integration test.

Dùng SQLite in-memory:

```python
connection = sqlite3.connect(
    ":memory:"
)
```

Tạo schema:

```python
connection.execute(
    """
    CREATE TABLE stories (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
    """
)
```

Sau đó test:

```python
repository = SQLiteStoryRepository(
    connection
)

story = Story("Python")

repository.save(story)

result = repository.get(
    story.id
)

assert result.title == "Python"
```

Đây là test thực sự cho SQL.

---

# 26. Hai loại test

Architecture của chúng ta cho phép:

```text
Unit Test
Service
   ↓
Fake Repository
```

và:

```text
Integration Test
SQLiteRepository
   ↓
SQLite
```

Không cần test toàn bộ application bằng GUI.

---

# 27. Repository và Dependency Inversion

Ta có:

```text
Application
     ↓
Repository Interface
     ↑
     │
SQLite Repository
```

Đây là Dependency Inversion.

Application không phụ thuộc:

```text
SQLite
```

mà phụ thuộc:

```text
StoryRepository
```

Implementation phụ thuộc abstraction.

---

# 28. Đừng để Interface chỉ để "cho có"

Một interface xấu:

```python
class Repository(ABC):

    @abstractmethod
    def execute(self, sql):
        ...
```

Đây thực chất chỉ là:

```text
Database wrapper
```

Không phải Repository tốt.

Tốt:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id):
        ...

    @abstractmethod
    def save(self, story):
        ...

    @abstractmethod
    def delete(self, story_id):
        ...

    @abstractmethod
    def exists(self, title):
        ...
```

Nó nói bằng **ngôn ngữ Domain**.

---

# 29. Repository không nên expose SQL

Sai:

```python
service.repository.execute(
    """
    SELECT ...
    """
)
```

Nếu Service làm vậy:

```text
Service
   ↓
SQL
```

Repository abstraction đã bị phá vỡ.

Đúng:

```python
service.repository.search(
    keyword
)
```

---

# 30. Repository không nên chứa Business Logic

Ví dụ:

```python
def save(self, story):

    if story.chapter_count < 3:
        raise ValueError(
            "Story must have 3 chapters"
        )
```

Nếu đây là business rule thì không nên nằm ở Repository.

Repository chỉ nên:

```text
load
save
delete
query
map
```

Business rule:

```text
Domain
```

---

# 31. Repository không nên chứa UI Logic

Tuyệt đối tránh:

```python
from PySide6.QtWidgets import QMessageBox
```

trong Repository.

Không:

```python
QMessageBox.warning(...)
```

Repository không biết UI tồn tại.

---

# 32. Repository và Exception

Ví dụ database lỗi:

```python
sqlite3.IntegrityError
```

Không nhất thiết để exception database leak xuyên toàn bộ application.

Có thể translate:

```python
try:
    ...
except sqlite3.IntegrityError as e:
    raise StoryRepositoryError(
        "Cannot save story"
    ) from e
```

Application có thể xử lý:

```python
except StoryRepositoryError:
    ...
```

Tùy mức độ của application mà bạn có cần abstraction exception hay không.

---

# 33. Repository và `None`

Có nhiều cách:

```python
story = repository.get(id)

if story is None:
    ...
```

Hoặc:

```python
raise StoryNotFound(...)
```

Không có một lựa chọn tuyệt đối.

Với use case quan trọng, exception rõ nghĩa thường tốt:

```python
story = repository.get_or_raise(
    story_id
)
```

Ví dụ:

```python
class StoryNotFound(Exception):
    pass
```

---

# 34. Repository API tốt

Ví dụ:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id: int) -> Story | None:
        ...

    @abstractmethod
    def save(self, story: Story) -> None:
        ...

    @abstractmethod
    def delete(self, story_id: int) -> None:
        ...

    @abstractmethod
    def exists(self, title: str) -> bool:
        ...

    @abstractmethod
    def search(
        self,
        keyword: str,
    ) -> list[Story]:
        ...
```

API này khá sạch.

---

# 35. Kiến trúc hiện tại

Sau Buổi 30:

```text
┌──────────────────────────┐
│         PySide6          │
│                          │
│ View                     │
│ Controller / ViewModel   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       Application        │
│                          │
│ StoryService             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Repository Port     │
│                          │
│ StoryRepository          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Infrastructure           │
│                          │
│ SQLiteStoryRepository    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      DatabaseManager     │
└────────────┬─────────────┘
             │
             ▼
          SQLite
```

Đây chính là architecture mà chúng ta sẽ tiếp tục phát triển.

---

# 36. So sánh toàn bộ trách nhiệm

| Thành phần        | Trách nhiệm              |
| ----------------- | ------------------------ |
| View              | Hiển thị UI              |
| Controller        | Điều phối user action    |
| ViewModel         | Quản lý UI state         |
| Service           | Điều phối use case       |
| Domain            | Business rule            |
| Repository        | Persistence abstraction  |
| SQLite Repository | SQL + mapping            |
| Database Manager  | Connection / transaction |
| SQLite            | Storage                  |

Đây là bảng bạn nên ghi nhớ.

---

# 37. Luồng Create Story hoàn chỉnh

```text
User
 │
 │ click Save
 ▼
View
 │
 ▼
Controller
 │
 │ title
 ▼
StoryService
 │
 │ Story(title)
 ▼
Domain
 │
 │ valid
 ▼
StoryRepository
 │
 │ save(story)
 ▼
SQLiteStoryRepository
 │
 │ INSERT
 ▼
DatabaseManager
 │
 ▼
SQLite
```

Không một layer nào cần biết toàn bộ hệ thống.

---

# 38. Bài tập 1 — Phân loại

Phân loại các đoạn code sau:

### A

```python
cursor = connection.execute(
    "SELECT id, title FROM stories"
)
```

### B

```python
repository.get(story_id)
```

### C

```python
story.publish()
```

### D

```python
self.view.show_error(
    "Story not found"
)
```

### E

```python
self.service.create_story(title)
```

### F

```python
connection.commit()
```

Hãy xác định:

```text
View
Controller
Service
Domain
Repository
Database Manager
```

---

# 39. Bài tập 2 — Viết Repository Interface

Viết:

```python
class StoryRepository(ABC):
    ...
```

có:

```text
get()
save()
delete()
exists()
search()
```

Dùng type hints đầy đủ.

---

# 40. Bài tập 3 — SQLite Repository

Tạo:

```python
class SQLiteStoryRepository:
    ...
```

với schema:

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL
)
```

Implement:

```text
get()
save()
delete()
exists()
search()
```

---

# 41. Bài tập 4 — Fake Repository

Viết:

```python
class FakeStoryRepository:
    ...
```

không sử dụng SQLite.

Sau đó test:

```python
service.create_story(
    "Python"
)
```

---

# 42. Bài tập 5 — Tìm lỗi kiến trúc

Cho:

```python
class StoryRepository:

    def save(self, story):

        if len(story.title) < 3:
            QMessageBox.warning(
                None,
                "Error",
                "Title too short",
            )
            return

        self.connection.execute(
            """
            INSERT INTO stories(title)
            VALUES(?)
            """,
            (story.title,),
        )

        self.connection.commit()
```

Tìm ít nhất **4 lỗi architecture**.

---

# 43. Bài tập 6 — Architecture Challenge

Thiết kế:

```text
Story
Chapter
```

Trong đó:

```text
Story
 ├── id
 ├── title
 └── chapters

Chapter
 ├── id
 ├── story_id
 ├── number
 └── content
```

Thiết kế:

```text
StoryRepository
ChapterRepository
```

và quyết định:

> `Chapter` có nên được lưu độc lập hay thông qua `StoryRepository`?

Hãy giải thích lựa chọn của bạn theo **Aggregate Root**.

Đây là bài tập quan trọng vì nó nối trực tiếp **Repository Pattern với DDD**.

---

# 44. Bài tập 7 — Story Reader Architecture

Thiết kế luồng:

```text
User chọn Story
        ↓
StoryListView
        ↓
Controller
        ↓
StoryService
        ↓
StoryRepository
        ↓
SQLite
```

Sau đó mở rộng:

```text
User chọn Chapter
        ↓
ChapterService
        ↓
ChapterRepository
        ↓
SQLite
```

Cuối cùng hãy trả lời:

> Có nên để `StoryService` gọi trực tiếp `ChapterRepository` không?

Câu hỏi này sẽ buộc bạn suy nghĩ về **Aggregate, Service và Use Case boundary**.

---

# 45. Tổng kết Buổi 30

Nếu chỉ nhớ 5 điều, hãy nhớ:

### 1.

```text
Repository ≠ Database Manager
```

### 2.

```text
Service không biết SQL
```

### 3.

```text
Repository nói bằng ngôn ngữ Domain
```

Ví dụ:

```python
repository.get_story(...)
```

thay vì:

```python
repository.execute_sql(...)
```

### 4.

```text
Repository không chứa business rules
```

### 5.

```text
Application
    ↓
Repository Interface
    ↓
Infrastructure Implementation
```

Mental Model:

```text
                 PySide6
                    │
                    ▼
          Controller / ViewModel
                    │
                    ▼
               Service
                    │
                    ▼
             Domain Model
                    │
                    ▼
          Repository Interface
                    ▲
                    │
          SQLite Repository
                    │
                    ▼
             DatabaseManager
                    │
                    ▼
                 SQLite
```

**Buổi 31 — Dependency Injection** sẽ lấy chính kiến trúc này và giải quyết câu hỏi:

> **Ai tạo `StoryService`? Ai tạo `StoryRepository`? Ai tạo `DatabaseManager`? Làm sao inject dependency từ `main.py` xuống mà không tạo dependency ở khắp nơi?**

Chúng ta sẽ xây một **Composition Root** hoàn chỉnh cho PySide6, đồng thời dùng nó để test `Controller → Service → Repository` mà không cần chạy GUI.
