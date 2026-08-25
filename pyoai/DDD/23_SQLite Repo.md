# DDD Deep Dive — Buổi 23

# SQLite Repository

Hôm nay chúng ta chuyển từ **Repository Interface** sang implementation thực tế:

```text
Domain
   ↓
Repository Interface
   ↑
SQLite Repository
   ↓
SQLite
```

Mục tiêu của buổi này là xây dựng:

```text
SQLiteStoryRepository
SQLiteChapterRepository
```

và đặc biệt hiểu **Domain ↔ Database Mapping**.

---

# 1. Nhắc lại kiến trúc

Ở Buổi 22 ta có:

```python
class StoryRepository(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    def add(
        self,
        story: Story,
    ) -> None:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Application chỉ biết:

```text
StoryRepository
```

không biết:

```text
SQLite
SQL
Connection
Cursor
```

Implementation hôm nay:

```python
class SQLiteStoryRepository:
    ...
```

---

# 2. SQLite Repository có nhiệm vụ gì?

Repository chịu trách nhiệm chuyển đổi:

```text
Database representation
        ↕
Domain representation
```

Ví dụ database:

```text
stories
------------------------------------------------
id | title | source_id | status
------------------------------------------------
1  | One Piece | manga_1 | published
```

Domain:

```python
Story(
    id=StoryId("1"),
    title=StoryTitle("One Piece"),
    source_id=SourceId("manga_1"),
    status=StoryStatus.PUBLISHED,
)
```

Repository là lớp trung gian.

---

# 3. Đây là một điểm cực kỳ quan trọng

Database model **không phải** Domain Model.

Đừng làm:

```python
@dataclass
class Story:
    id: str
    title: str
    source_id: str
    status: str
```

chỉ để cho SQLite dễ lưu.

DDD muốn:

```python
StoryId
StoryTitle
SourceId
StoryStatus
```

đảm bảo business invariant.

---

# 4. Thiết kế database

Ví dụ:

```sql
CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_id TEXT NOT NULL,
    status TEXT NOT NULL
);
```

Chapter:

```sql
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
```

Tạm thời chưa bàn transaction sâu.

Buổi 24 sẽ xử lý phần đó.

---

# 5. Domain Model

Ta giả sử Domain đã có:

```python
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class StoryId:
    value: str


@dataclass(frozen=True)
class StoryTitle:
    value: str


@dataclass(frozen=True)
class SourceId:
    value: str
```

Status:

```python
class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
```

---

# 6. Story Entity

Ví dụ:

```python
class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
        status: StoryStatus,
    ):
        self._id = story_id
        self._title = title
        self._source_id = source_id
        self._status = status
```

Property:

```python
@property
def id(self) -> StoryId:
    return self._id


@property
def title(self) -> StoryTitle:
    return self._title


@property
def source_id(self) -> SourceId:
    return self._source_id


@property
def status(self) -> StoryStatus:
    return self._status
```

Business behavior:

```python
def publish(self) -> None:
    self._status = StoryStatus.PUBLISHED
```

---

# 7. Repository Interface

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    def add(
        self,
        story: Story,
    ) -> None:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

---

# 8. SQLite Repository

Bắt đầu:

```python
import sqlite3


class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self._connection = connection
```

Repository nhận `connection` từ bên ngoài.

Không tự:

```python
sqlite3.connect(...)
```

Đây là **Dependency Injection**.

---

# 9. Vì sao không tự tạo connection?

Không nên:

```python
class SQLiteStoryRepository:

    def __init__(self):
        self.connection = sqlite3.connect(
            "app.db"
        )
```

Vì Repository đang quyết định:

```text
database location
connection lifecycle
transaction lifecycle
```

Sau này Unit of Work sẽ quản lý transaction.

Do đó:

```python
SQLiteStoryRepository(connection)
```

tốt hơn.

---

# 10. `get()`

Ta cần:

```python
def get(
    self,
    story_id: StoryId,
) -> Story | None:
```

SQL:

```sql
SELECT
    id,
    title,
    source_id,
    status
FROM stories
WHERE id = ?
```

Python:

```python
def get(
    self,
    story_id: StoryId,
) -> Story | None:

    cursor = self._connection.execute(
        """
        SELECT
            id,
            title,
            source_id,
            status
        FROM stories
        WHERE id = ?
        """,
        (story_id.value,),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return self._to_domain(row)
```

---

# 11. `_to_domain()`

Đây là một method rất quan trọng:

```python
def _to_domain(
    self,
    row: sqlite3.Row,
) -> Story:
    return Story(
        story_id=StoryId(row["id"]),
        title=StoryTitle(row["title"]),
        source_id=SourceId(row["source_id"]),
        status=StoryStatus(row["status"]),
    )
```

Ta có:

```text
SQLite Row
    ↓
_to_domain()
    ↓
Story
```

---

# 12. Mapping không phải business logic

Repository có thể:

```python
StoryId(row["id"])
StoryTitle(row["title"])
StoryStatus(row["status"])
```

Nhưng không nên:

```python
if story.status == ...:
    ...
```

để thực hiện business rule.

Business behavior thuộc Domain.

---

# 13. Mapping ngược lại

Ta cần:

```text
Story
 ↓
SQLite parameters
```

Tạo:

```python
def _to_row(
    self,
    story: Story,
) -> tuple:
    return (
        story.id.value,
        story.title.value,
        story.source_id.value,
        story.status.value,
    )
```

---

# 14. `add()`

```python
def add(
    self,
    story: Story,
) -> None:

    self._connection.execute(
        """
        INSERT INTO stories (
            id,
            title,
            source_id,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        self._to_row(story),
    )
```

Notice:

```python
story.id.value
```

thay vì:

```python
str(story.id)
```

Ta muốn mapping explicit.

---

# 15. `save()`

```python
def save(
    self,
    story: Story,
) -> None:

    self._connection.execute(
        """
        UPDATE stories
        SET
            title = ?,
            source_id = ?,
            status = ?
        WHERE id = ?
        """,
        (
            story.title.value,
            story.source_id.value,
            story.status.value,
            story.id.value,
        ),
    )
```

---

# 16. Một Repository hoàn chỉnh

```python
import sqlite3


class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self._connection = connection

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:

        cursor = self._connection.execute(
            """
            SELECT
                id,
                title,
                source_id,
                status
            FROM stories
            WHERE id = ?
            """,
            (story_id.value,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._to_domain(row)

    def add(
        self,
        story: Story,
    ) -> None:

        self._connection.execute(
            """
            INSERT INTO stories (
                id,
                title,
                source_id,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            self._to_row(story),
        )

    def save(
        self,
        story: Story,
    ) -> None:

        self._connection.execute(
            """
            UPDATE stories
            SET
                title = ?,
                source_id = ?,
                status = ?
            WHERE id = ?
            """,
            (
                story.title.value,
                story.source_id.value,
                story.status.value,
                story.id.value,
            ),
        )

    @staticmethod
    def _to_domain(
        row: sqlite3.Row,
    ) -> Story:

        return Story(
            story_id=StoryId(row["id"]),
            title=StoryTitle(row["title"]),
            source_id=SourceId(row["source_id"]),
            status=StoryStatus(row["status"]),
        )

    @staticmethod
    def _to_row(
        story: Story,
    ) -> tuple:

        return (
            story.id.value,
            story.title.value,
            story.source_id.value,
            story.status.value,
        )
```

---

# 17. `sqlite3.Row`

Tôi khuyên cấu hình:

```python
connection.row_factory = sqlite3.Row
```

Sau đó:

```python
row["id"]
row["title"]
row["status"]
```

thay vì:

```python
row[0]
row[1]
row[2]
```

Code dễ đọc hơn rất nhiều.

---

# 18. Database setup

Ví dụ:

```python
connection = sqlite3.connect("novel.db")

connection.row_factory = sqlite3.Row

connection.executescript(
    """
    CREATE TABLE IF NOT EXISTS stories (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        source_id TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """
)
```

Sau đó:

```python
repository = SQLiteStoryRepository(
    connection
)
```

---

# 19. Sử dụng Repository

```python
story = Story(
    story_id=StoryId("story-1"),
    title=StoryTitle("One Piece"),
    source_id=SourceId("source-1"),
    status=StoryStatus.DRAFT,
)

repository.add(story)
connection.commit()
```

Sau đó:

```python
loaded = repository.get(
    StoryId("story-1")
)
```

Kết quả:

```python
loaded
```

là **Domain Entity**.

Không phải:

```python
sqlite3.Row
```

---

# 20. Đây là điểm cực kỳ quan trọng

Sau:

```python
loaded = repository.get(...)
```

Application có thể:

```python
loaded.publish()
```

Nó không cần biết:

```text
SQLite
SQL
cursor
row
```

Đây chính là Persistence Ignorance.

---

# 21. `save()` không `commit()`

Một lỗi phổ biến:

```python
def save(self, story):
    self.connection.execute(...)
    self.connection.commit()
```

Tôi **không khuyến nghị**.

Tại sao?

Vì:

```text
Repository
```

không nên quyết định transaction boundary.

Ví dụ Use Case:

```text
1. load Story
2. load Chapter
3. update Story
4. update Chapter
5. commit
```

Nếu `StoryRepository.save()` tự commit:

```text
Story save
 ↓
COMMIT
 ↓
Chapter save
 ↓
ERROR
```

Database có trạng thái dở dang.

---

# 22. Đây chính là lý do có Unit of Work

Buổi 24 chúng ta sẽ có:

```text
Unit of Work
      │
      ├── StoryRepository
      ├── ChapterRepository
      └── ...
      
      ↓

    COMMIT
```

Transaction boundary nằm ở Use Case / UoW.

---

# 23. SQLite Chapter Repository

Domain:

```python
class ChapterNumber:
    def __init__(self, value: int):
        if value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )

        self.value = value
```

Chapter:

```python
class Chapter:

    def __init__(
        self,
        chapter_id: ChapterId,
        story_id: StoryId,
        number: ChapterNumber,
        title: str,
        content: str,
    ):
        self._id = chapter_id
        self._story_id = story_id
        self._number = number
        self._title = title
        self._content = content
```

---

# 24. Chapter Repository Interface

```python
class ChapterRepository(Protocol):

    def get(
        self,
        chapter_id: ChapterId,
    ) -> Chapter | None:
        ...

    def add(
        self,
        chapter: Chapter,
    ) -> None:
        ...

    def save(
        self,
        chapter: Chapter,
    ) -> None:
        ...
```

---

# 25. SQLite Chapter Repository

```python
class SQLiteChapterRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self._connection = connection
```

`get()`:

```python
def get(
    self,
    chapter_id: ChapterId,
) -> Chapter | None:

    cursor = self._connection.execute(
        """
        SELECT
            id,
            story_id,
            chapter_number,
            title,
            content
        FROM chapters
        WHERE id = ?
        """,
        (chapter_id.value,),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return self._to_domain(row)
```

---

# 26. Mapping Chapter

```python
@staticmethod
def _to_domain(
    row: sqlite3.Row,
) -> Chapter:

    return Chapter(
        chapter_id=ChapterId(row["id"]),
        story_id=StoryId(row["story_id"]),
        number=ChapterNumber(
            row["chapter_number"]
        ),
        title=row["title"],
        content=row["content"],
    )
```

Điểm quan trọng:

```python
ChapterNumber(
    row["chapter_number"]
)
```

Nếu database chứa:

```text
chapter_number = -10
```

Domain constructor có thể từ chối.

---

# 27. Đây là một lớp bảo vệ

Database nói:

```text
INTEGER
```

Domain nói:

```text
ChapterNumber
```

Hai thứ không giống nhau.

Database constraint:

```sql
chapter_number INTEGER NOT NULL
```

chỉ đảm bảo:

```text
có giá trị
```

Domain có thể đảm bảo:

```text
chapter_number > 0
```

Đây chính là sự khác biệt giữa:

```text
Database Constraint
```

và:

```text
Domain Invariant
```

---

# 28. Repository không bypass Domain

Không nên:

```python
return Chapter(
    ...
)
```

với những giá trị không hợp lệ rồi sau đó:

```python
chapter._number = ...
```

Repository phải tạo Domain Object thông qua public API/constructor/factory hợp lệ.

---

# 29. Foreign Key

Chapter có:

```text
story_id
```

Database:

```sql
FOREIGN KEY (story_id)
REFERENCES stories(id)
```

SQLite cần:

```python
connection.execute(
    "PRAGMA foreign_keys = ON"
)
```

Đây là Infrastructure concern.

Domain không cần biết SQLite Foreign Key.

---

# 30. Repository không phải ORM

Một số người nghĩ:

```text
Repository = ORM
```

Không đúng.

Repository là:

```text
Domain collection abstraction
```

ORM là:

```text
Persistence technology
```

Ví dụ:

```text
SQLAlchemy
Peewee
Django ORM
```

có thể được sử dụng **bên trong Repository**.

---

# 31. Với raw SQLite

Kiến trúc của chúng ta:

```text
SQLiteStoryRepository
       ↓
sqlite3
       ↓
SQLite
```

Sau này nếu chuyển:

```text
SQLAlchemyStoryRepository
```

thì Application vẫn:

```text
StoryRepository
```

Không đổi.

---

# 32. Mapping Layer

Khi project lớn hơn, không nhất thiết viết mapping ngay trong Repository.

Có thể:

```text
infrastructure/
    persistence/
        sqlite/
            repositories/
                story_repository.py

            mappers/
                story_mapper.py
                chapter_mapper.py
```

Mapper:

```python
class StoryMapper:

    @staticmethod
    def to_domain(row) -> Story:
        ...

    @staticmethod
    def to_persistence(story: Story):
        ...
```

---

# 33. Khi nào cần Mapper riêng?

Project nhỏ:

```text
Repository
 ├── SQL
 ├── mapping
 └── persistence
```

hoàn toàn ổn.

Project lớn:

```text
Repository
     ↓
Mapper
     ↓
Domain
```

sạch hơn.

Đừng over-engineer ngay từ đầu.

---

# 34. Một Repository tốt

```text
SQLiteStoryRepository
│
├── SQL
│
├── Persistence → Domain mapping
│
└── Domain → Persistence mapping
```

Không:

```text
Business rule
```

Không:

```text
Use Case
```

Không:

```text
Transaction orchestration
```

---

# 35. Repository và Business Logic

Sai:

```python
def save(self, story):

    if story.status == StoryStatus.PUBLISHED:
        # gửi notification
        # update crawler
        # ...
```

Repository không nên làm vậy.

Đúng:

```text
Use Case
   ↓
Domain behavior
   ↓
Repository
```

---

# 36. Ví dụ Use Case

```python
class PublishStory:

    def __init__(
        self,
        stories: StoryRepository,
    ):
        self.stories = stories

    def execute(
        self,
        story_id: StoryId,
    ) -> None:

        story = self.stories.get(story_id)

        if story is None:
            raise StoryNotFound(story_id)

        story.publish()

        self.stories.save(story)
```

Repository chỉ:

```text
load
save
```

Domain quyết định:

```text
publish có hợp lệ không?
```

---

# 37. Repository Test

Đây là loại test rất quan trọng.

```python
def test_save_and_get_story():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE stories (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source_id TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    repository = SQLiteStoryRepository(
        connection
    )

    story = Story(
        story_id=StoryId("story-1"),
        title=StoryTitle("One Piece"),
        source_id=SourceId("source-1"),
        status=StoryStatus.DRAFT,
    )

    repository.add(story)
    connection.commit()

    result = repository.get(
        StoryId("story-1")
    )

    assert result is not None
    assert result.id == story.id
    assert result.title == story.title
    assert result.status == story.status
```

---

# 38. Test mapping

Một test quan trọng khác:

```text
Database
   ↓
Repository
   ↓
Domain
```

phải giữ nguyên:

```text
StoryId
StoryTitle
SourceId
StoryStatus
```

Không bị biến thành:

```text
str
str
str
str
```

---

# 39. Test Domain Invariant

Ví dụ:

```python
connection.execute(
    """
    INSERT INTO chapters (
        id,
        story_id,
        chapter_number,
        title,
        content
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        "chapter-1",
        "story-1",
        -1,
        "Bad Chapter",
        "...",
    ),
)
```

Khi:

```python
repository.get(...)
```

Domain constructor:

```python
ChapterNumber(-1)
```

phải reject.

Đây là một test rất hay để hiểu:

```text
Persistence
    ↓
Domain invariant
```

---

# 40. Nhưng đừng phụ thuộc hoàn toàn vào Domain để bảo vệ Database

Database cũng nên có constraint:

```sql
CHECK (chapter_number > 0)
```

Tức là:

```text
Domain
  +
Database
```

cùng bảo vệ dữ liệu.

Nhưng chúng có vai trò khác nhau.

---

# 41. Hai lớp bảo vệ

```text
Application
      ↓
Domain invariant
      ↓
Repository
      ↓
Database constraint
```

Ví dụ:

```text
Domain:
ChapterNumber > 0

Database:
CHECK(chapter_number > 0)
```

Defense in depth.

---

# 42. Một câu hỏi quan trọng

Nếu Repository nhận:

```python
story: Story
```

thì nó có cần validate lại:

```python
if not story.title:
```

không?

Thông thường:

**Không cần.**

Nếu `Story` đã là valid Domain Object thì Repository không nên lặp lại business validation.

---

# 43. Repository Boundary

Ta có:

```text
Domain
───────────────
Story
StoryId
StoryTitle
StoryStatus
───────────────

Infrastructure
───────────────
SQLiteStoryRepository
sqlite3.Row
SQL
Connection
───────────────
```

Boundary:

```text
Domain ←→ Repository
```

Repository là adapter.

---

# 44. Ports & Adapters

Nếu nhìn theo Hexagonal Architecture:

```text
              ┌──────────────┐
              │   Use Case   │
              └──────┬───────┘
                     │
                     ▼
             StoryRepository
                  PORT
                     ▲
                     │
             SQLiteStoryRepository
                  ADAPTER
                     │
                     ▼
                  SQLite
```

Đây chính là:

```text
Port = Repository Interface
Adapter = SQLite Repository
```

---

# 45. Tư duy quan trọng nhất của Buổi 23

Đừng nghĩ:

> "Tôi đang viết code SQLite."

Hãy nghĩ:

> "Tôi đang viết một Adapter để biến SQLite persistence model thành Domain model."

Đó là tư duy DDD/Architecture.

---

# 46. Tổng kết

Sau Buổi 23, flow của chúng ta là:

```text
Use Case
   │
   ▼
StoryRepository
   ▲
   │
SQLiteStoryRepository
   │
   ├── SQL
   ├── Mapping
   │
   ▼
SQLite
```

Khi đọc:

```text
SQLite
   ↓
Row
   ↓
Mapper
   ↓
Story
   ↓
Use Case
```

Khi ghi:

```text
Story
   ↓
Mapper
   ↓
SQL parameters
   ↓
SQLite
```

---

# 47. Checklist Buổi 23

Bạn cần nắm chắc:

```text
□ Repository Interface
□ SQLite Repository
□ Dependency Injection
□ sqlite3.Connection
□ sqlite3.Row
□ SQL parameterization
□ Database → Domain mapping
□ Domain → Database mapping
□ Repository không chứa business logic
□ Repository không tự commit
□ Repository không expose sqlite3.Row
□ Persistence Ignorance
□ Repository = Port
□ SQLite Repository = Adapter
```

---

# 48. Bài tập thực hành

Hãy tự xây dựng package:

```text
src/
└── novel_app/
    ├── domain/
    │   ├── story.py
    │   └── chapter.py
    │
    ├── application/
    │   └── ports/
    │       ├── story_repository.py
    │       └── chapter_repository.py
    │
    └── infrastructure/
        └── sqlite/
            ├── story_repository.py
            └── chapter_repository.py
```

Database:

```sql
stories
chapters
```

Implement:

```python
StoryRepository.get()
StoryRepository.add()
StoryRepository.save()

ChapterRepository.get()
ChapterRepository.add()
ChapterRepository.save()
```

Sau đó viết test:

```text
test_add_story()
test_get_story()
test_save_story()

test_add_chapter()
test_get_chapter()
test_save_chapter()
```

**Thử thách quan trọng:** Trong toàn bộ `application/` và `domain/`, tuyệt đối không import:

```python
sqlite3
```

Nếu bạn làm đúng bài này, bạn đã thực sự hiểu mối quan hệ:

```text
DDD
 ↓
Repository
 ↓
Dependency Inversion
 ↓
Ports & Adapters
 ↓
SQLite
```

**Buổi 24** sẽ là bước tiếp theo rất quan trọng: **Unit of Work** — chúng ta sẽ giải quyết câu hỏi: nếu một Use Case thay đổi cả `Story` và `Chapter`, làm thế nào để **tất cả cùng commit hoặc tất cả rollback** trong một SQLite transaction.
