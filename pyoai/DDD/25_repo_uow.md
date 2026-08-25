# DDD Deep Dive — Buổi 25

# Repository + Unit of Work

Hôm nay chúng ta **ghép toàn bộ kiến thức từ Buổi 21 → 24** thành một flow hoàn chỉnh.

Đây là buổi rất quan trọng vì từ đây bạn không còn học Repository và Unit of Work như hai pattern riêng lẻ nữa, mà bắt đầu nhìn chúng như **một hệ thống persistence architecture hoàn chỉnh**.

---

# 1. Bức tranh tổng thể

Đến thời điểm này chúng ta có:

```text
                 Interface / CLI
                       │
                       ▼
                  Application
                       │
                       ▼
                    Use Case
                       │
                       ▼
                 Unit of Work
                  │         │
                  ▼         ▼
            StoryRepository ChapterRepository
                  │         │
                  └────┬────┘
                       ▼
               SQLite Repository
                       │
                       ▼
                    SQLite
```

Còn Domain:

```text
Story
Chapter
StoryId
StoryTitle
ChapterNumber
StoryStatus
```

nằm bên trong Application/Domain boundary và **không biết SQLite tồn tại**.

---

# 2. Flow chuẩn

Ví dụ:

> Thêm chapter vào một story.

Ta muốn:

```text
CLI
 ↓
AddChapter Use Case
 ↓
UnitOfWork
 ↓
StoryRepository.get()
 ↓
Story.add_chapter()
 ↓
StoryRepository.save()
 ↓
ChapterRepository.add()
 ↓
UnitOfWork.commit()
 ↓
SQLite
```

Nếu có lỗi:

```text
Exception
   ↓
UnitOfWork.rollback()
   ↓
Database trở về trạng thái trước transaction
```

---

# 3. Domain Model

Ta bắt đầu với Domain.

## StoryId

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryId:
    value: str
```

## ChapterId

```python
@dataclass(frozen=True)
class ChapterId:
    value: str
```

## StoryTitle

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        if not self.value.strip():
            raise ValueError(
                "Story title cannot be empty"
            )
```

---

# 4. ChapterNumber

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )
```

Như vậy:

```python
ChapterNumber(10)
```

hợp lệ.

Nhưng:

```python
ChapterNumber(-1)
```

bị reject.

---

# 5. StoryStatus

```python
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
```

---

# 6. Chapter Entity

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
        if not title.strip():
            raise ValueError(
                "Chapter title cannot be empty"
            )

        self._id = chapter_id
        self._story_id = story_id
        self._number = number
        self._title = title
        self._content = content

    @property
    def id(self):
        return self._id

    @property
    def story_id(self):
        return self._story_id

    @property
    def number(self):
        return self._number

    @property
    def title(self):
        return self._title

    @property
    def content(self):
        return self._content
```

---

# 7. Story Aggregate

Giả sử Story là Aggregate Root.

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
        self._chapters: list[Chapter] = []
```

---

# 8. Business Behavior

Không làm:

```python
story.chapters.append(chapter)
```

Mà:

```python
story.add_chapter(chapter)
```

Ví dụ:

```python
def add_chapter(
    self,
    chapter: Chapter,
) -> None:

    if chapter.story_id != self._id:
        raise ValueError(
            "Chapter belongs to another story"
        )

    self._chapters.append(chapter)
```

---

# 9. Publish Story

```python
def publish(self) -> None:

    if self._status == StoryStatus.PUBLISHED:
        raise ValueError(
            "Story is already published"
        )

    self._status = StoryStatus.PUBLISHED
```

Đây là Domain behavior.

Repository không làm việc này.

---

# 10. Repository Interface

Application cần:

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

Chapter:

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

# 11. Unit of Work Interface

```python
class UnitOfWork(Protocol):

    stories: StoryRepository
    chapters: ChapterRepository

    def __enter__(self):
        ...

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

---

# 12. SQLite Repository

Ta có:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self._connection = connection
```

`get()`:

```python
def get(
    self,
    story_id: StoryId,
) -> Story | None:

    row = self._connection.execute(
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
    ).fetchone()

    if row is None:
        return None

    return Story(
        story_id=StoryId(row["id"]),
        title=StoryTitle(row["title"]),
        source_id=SourceId(row["source_id"]),
        status=StoryStatus(row["status"]),
    )
```

---

# 13. SQLite Story `add()`

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
        (
            story.id.value,
            story.title.value,
            story.source_id.value,
            story.status.value,
        ),
    )
```

---

# 14. SQLite Story `save()`

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

Notice:

**Không có `commit()`.**

---

# 15. SQLite Chapter Repository

```python
class SQLiteChapterRepository:

    def __init__(self, connection):
        self._connection = connection
```

`add()`:

```python
def add(
    self,
    chapter: Chapter,
) -> None:

    self._connection.execute(
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
            chapter.id.value,
            chapter.story_id.value,
            chapter.number.value,
            chapter.title,
            chapter.content,
        ),
    )
```

---

# 16. SQLite Unit of Work

```python
class SQLiteUnitOfWork:

    def __init__(self, connection):
        self._connection = connection

        self.stories = SQLiteStoryRepository(
            connection
        )

        self.chapters = SQLiteChapterRepository(
            connection
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is not None:
            self.rollback()

        return False

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()
```

Đây là phần quan trọng nhất:

```text
ONE UoW
    ↓
ONE connection
    ↓
StoryRepository
ChapterRepository
    ↓
ONE transaction
```

---

# 17. Use Case: Add Chapter

Bây giờ mới thực sự thấy giá trị của toàn bộ kiến trúc.

```python
class AddChapter:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

Method:

```python
def execute(
    self,
    story_id: StoryId,
    chapter: Chapter,
) -> None:

    with self.uow:

        story = self.uow.stories.get(
            story_id
        )

        if story is None:
            raise StoryNotFound(
                story_id
            )

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        self.uow.chapters.add(chapter)

        self.uow.commit()
```

---

# 18. Phân tích từng bước

## Bước 1

```python
with self.uow:
```

Bắt đầu business transaction boundary.

---

## Bước 2

```python
story = self.uow.stories.get(story_id)
```

Repository load Aggregate.

---

## Bước 3

```python
story.add_chapter(chapter)
```

Domain quyết định:

> Chapter có hợp lệ không?

Không phải Repository.

---

## Bước 4

```python
self.uow.stories.save(story)
```

Repository persistence.

---

## Bước 5

```python
self.uow.chapters.add(chapter)
```

Repository persistence.

---

## Bước 6

```python
self.uow.commit()
```

Transaction commit.

---

# 19. Dependency Flow

Điều quan trọng là:

```text
AddChapter
    ↓
UnitOfWork
    ↓
StoryRepository
ChapterRepository
```

Nhưng:

```text
AddChapter
```

không biết:

```text
SQLite
```

và:

```text
Story
```

cũng không biết:

```text
UnitOfWork
```

---

# 20. Exception Flow

Giả sử:

```python
self.uow.chapters.add(chapter)
```

ném:

```python
sqlite3.IntegrityError
```

Flow:

```text
Story.save()
     ↓
Chapter.add()
     ↓
IntegrityError
     ↓
__exit__()
     ↓
rollback()
     ↓
Exception propagate
```

---

# 21. Atomicity thực tế

Giả sử database ban đầu:

```text
Story:
status = draft

Chapter:
không tồn tại
```

Use Case:

```text
Story → published
Chapter → INSERT
```

Nếu thành công:

```text
Story = published
Chapter = exists
```

Nếu thất bại:

```text
Story = draft
Chapter = does not exist
```

Không có trạng thái:

```text
Story = published
Chapter = missing
```

nếu transaction boundary được thiết kế đúng.

---

# 22. Một chi tiết quan trọng về Aggregate

Ở Buổi 17 ta nói:

```python
story.add_chapter(chapter)
```

Nhưng ở persistence:

```text
StoryRepository
ChapterRepository
```

lại lưu riêng.

Điều này **không nhất thiết mâu thuẫn**.

Aggregate boundary là boundary của **business consistency**, không nhất thiết database phải lưu thành một row/document duy nhất.

Ví dụ:

```text
Story Aggregate
    │
    ├── Story row
    │
    └── Chapter rows
```

Repository có thể sử dụng nhiều bảng để persist một Aggregate.

---

# 23. Một cách khác

Ta có thể thiết kế:

```text
StoryRepository
    ↓
Story
    +
Chapters
```

và:

```text
ChapterRepository
```

không tồn tại nếu Chapter là Entity nội bộ của Story Aggregate.

Đây là một điểm rất quan trọng.

Nếu:

```text
Chapter
```

**không phải Aggregate Root**, thì Application không nên:

```python
chapter_repository.get(...)
```

để trực tiếp thao tác nó.

---

# 24. Quay lại thiết kế của project

Ở Buổi 20 chúng ta đã phân tích:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

Một thiết kế có thể là:

```text
Story Aggregate
    └── Chapter

CrawlerJob Aggregate
    └── ...

CrawlerSource Aggregate

ReadingProgress Aggregate

User Aggregate
```

Nếu vậy:

```text
StoryRepository
```

có thể chịu trách nhiệm cả:

```text
Story
Chapter
```

---

# 25. Khi đó Use Case sẽ khác

Thay vì:

```python
uow.stories.save(story)
uow.chapters.add(chapter)
```

có thể:

```python
with uow:
    story = uow.stories.get(story_id)

    story.add_chapter(chapter)

    uow.stories.save(story)

    uow.commit()
```

Repository xử lý persistence của cả Aggregate.

Đây là hướng DDD thuần hơn nếu Chapter là child entity.

---

# 26. Nhưng database vẫn có thể có hai bảng

Ví dụ:

```text
stories
chapters
```

Repository:

```text
StoryRepository
      ↓
stories
chapters
```

Không có vấn đề gì.

Database schema:

```text
          Story Aggregate
                │
       ┌────────┴────────┐
       ▼                 ▼
   stories            chapters
```

---

# 27. Một nguyên tắc cực kỳ quan trọng

> **Repository nên được thiết kế quanh Aggregate Root, không phải quanh database table.**

Sai tư duy:

```text
stories table
    ↓
StoryRepository

chapters table
    ↓
ChapterRepository
```

Đây là tư duy database-first.

DDD:

```text
Story Aggregate
       ↓
StoryRepository
```

Sau đó mới:

```text
StoryRepository
       ↓
stories + chapters tables
```

---

# 28. Đây là điểm rất dễ nhầm

Repository:

```text
không phải
```

```text
Table Gateway
```

Repository:

```text
không phải
```

```text
DAO
```

Repository là:

> abstraction của collection/aggregate persistence trong domain/application.

---

# 29. Repository + UoW

Có thể hình dung:

```text
Repository
    =
"Where/how do I retrieve this Aggregate?"

Unit of Work
    =
"When do all changes become permanent?"
```

---

# 30. Một Use Case hoàn chỉnh

Ví dụ Publish Story:

```python
class PublishStory:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(
        self,
        story_id: StoryId,
    ) -> None:

        with self.uow:

            story = self.uow.stories.get(
                story_id
            )

            if story is None:
                raise StoryNotFound(
                    story_id
                )

            story.publish()

            self.uow.stories.save(story)

            self.uow.commit()
```

---

# 31. Use Case không SQL

Nhìn vào:

```python
PublishStory
```

ta không thấy:

```text
SELECT
UPDATE
INSERT
sqlite3
cursor
commit SQL
```

Ta chỉ thấy:

```text
load
business behavior
save
commit
```

Đây là một Use Case rất sạch.

---

# 32. Đây chính là lợi ích của DDD

Business code:

```python
story.publish()
```

thay vì:

```python
UPDATE stories
SET status = 'published'
WHERE id = ?
```

Câu thứ hai mô tả database.

Câu thứ nhất mô tả business.

DDD ưu tiên câu thứ nhất.

---

# 33. Application Service không nên làm business logic

Ví dụ:

```python
class PublishStory:

    def execute(...):

        if story.status == "draft":
            story.status = "published"
```

Không tốt.

Nên:

```python
story.publish()
```

Application:

```text
orchestrate
```

Domain:

```text
decide
```

Repository:

```text
persist
```

UoW:

```text
coordinate transaction
```

---

# 34. Bốn trách nhiệm

Hãy nhớ bảng này:

| Thành phần       | Trách nhiệm       |
| ---------------- | ----------------- |
| Entity/Aggregate | Business behavior |
| Use Case         | Orchestration     |
| Repository       | Persistence       |
| Unit of Work     | Transaction       |

Ví dụ:

```text
Story.publish()
```

→ Domain

```text
PublishStory.execute()
```

→ Application

```text
stories.save(story)
```

→ Repository

```text
uow.commit()
```

→ UoW

---

# 35. Testing Architecture

Ta có ba cấp độ.

### Domain test

```text
Story
 ↓
publish()
```

Không database.

### Application test

```text
Use Case
 ↓
Fake Repository / Fake UoW
```

Không SQLite.

### Integration test

```text
Use Case
 ↓
SQLite UoW
 ↓
SQLite :memory:
```

Có database.

---

# 36. Integration Test thực tế

```python
def test_add_chapter_commits():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_schema(connection)

    uow = SQLiteUnitOfWork(connection)

    story = make_story()
    chapter = make_chapter(
        story_id=story.id
    )

    uow.stories.add(story)
    uow.commit()

    use_case = AddChapter(uow)

    use_case.execute(
        story.id,
        chapter,
    )

    result = uow.chapters.get(
        chapter.id
    )

    assert result is not None
```

---

# 37. Integration Test rollback

```python
def test_add_chapter_rolls_back():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_schema(connection)

    uow = SQLiteUnitOfWork(connection)

    story = make_story()

    uow.stories.add(story)
    uow.commit()

    chapter = make_chapter(
        story_id=story.id
    )

    try:
        with uow:
            story = uow.stories.get(
                story.id
            )

            story.add_chapter(chapter)

            uow.stories.save(story)

            raise RuntimeError(
                "failure"
            )
    except RuntimeError:
        pass

    result = uow.stories.get(
        story.id
    )

    assert result.status == (
        StoryStatus.DRAFT
    )
```

---

# 38. Một vấn đề mới: `save()` hay Dirty Tracking?

Ta đang dùng:

```python
story = repo.get(id)

story.publish()

repo.save(story)
```

Repository không biết:

```text
Story đã thay đổi gì?
```

Nó chỉ UPDATE toàn bộ fields.

Điều này hoàn toàn ổn với project nhỏ.

DDD không yêu cầu:

```text
Unit of Work phải có dirty tracking.
```

---

# 39. ORM thường có Dirty Tracking

Ví dụ ORM có thể:

```text
load entity
 ↓
change entity
 ↓
UnitOfWork detects change
 ↓
UPDATE
```

Nhưng với raw SQLite:

```text
load
 ↓
modify
 ↓
save
```

là cách đơn giản và rõ ràng.

---

# 40. Đừng copy ORM một cách mù quáng

Nếu dùng SQLite raw SQL, không cần xây ngay:

```text
Identity Map
Dirty Tracking
Change Tracker
Lazy Loading
Proxy
Unit of Work Registry
```

Đó có thể là over-engineering.

Ta chỉ cần:

```text
Repository
+
UnitOfWork
+
Transaction
```

---

# 41. Một điểm tinh tế: UoW lifecycle

Nếu:

```python
uow = SQLiteUnitOfWork(connection)
```

và dùng nhiều lần:

```python
with uow:
    ...

with uow:
    ...
```

có thể hoạt động, nhưng cần cẩn thận với:

```text
connection lifecycle
transaction state
repository lifecycle
```

Ở project lớn, có thể tạo một UoW mới cho mỗi business operation.

Ví dụ:

```python
def create_uow():
    connection = create_connection()

    return SQLiteUnitOfWork(
        connection
    )
```

---

# 42. Composition Root

CLI:

```python
def main():

    connection = create_connection()

    uow = SQLiteUnitOfWork(
        connection
    )

    use_case = PublishStory(uow)

    use_case.execute(
        StoryId("story-1")
    )
```

GUI:

```text
PySide6
   ↓
Application Container
   ↓
Use Cases
```

Crawler worker:

```text
Crawler
   ↓
Application Use Case
   ↓
UoW
```

Tất cả dùng cùng Application architecture.

---

# 43. Đây là lợi ích lớn cho project đọc truyện

Bạn có thể có:

```text
CLI
PySide6
Crawler Worker
REST API
```

nhưng tất cả đều gọi:

```text
Application Use Cases
```

Ví dụ:

```text
CLI ───────────┐
PySide6 ───────┤
Crawler ───────┼──→ AddChapter
REST API ──────┘
```

`AddChapter` không cần biết caller là ai.

---

# 44. Kiến trúc hoàn chỉnh

```text
                    ┌──────────┐
                    │   CLI    │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ PySide6  │
                    └────┬─────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Application  │
                 │               │
                 │   Use Cases   │
                 └───────┬───────┘
                         │
                         ▼
                  ┌────────────┐
                  │    UoW     │
                  └─────┬──────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       StoryRepository      ChapterRepository
             │                     │
             └──────────┬──────────┘
                        ▼
                     SQLite
```

---

# 45. DDD + Clean Architecture

Đến đây bạn có thể thấy rõ:

```text
Domain
    ↓
Application
    ↓
Infrastructure
```

Trong đó:

```text
Application
    ↓
Repository Interface
    ↑
Infrastructure
```

và:

```text
Application
    ↓
UoW Interface
    ↑
SQLite UoW
```

Đây chính là Dependency Inversion.

---

# 46. Những lỗi cần tránh

### Lỗi 1

Repository tự commit:

```python
repo.save()
repo.commit()
```

❌

---

### Lỗi 2

Use Case viết SQL:

```python
connection.execute(...)
```

❌

---

### Lỗi 3

Domain biết UoW:

```python
class Story:
    def save(self, uow):
        ...
```

❌

---

### Lỗi 4

UoW chứa business logic:

```python
uow.publish_story(...)
```

❌

---

### Lỗi 5

Repository trả `sqlite3.Row`

```python
return row
```

❌

---

### Lỗi 6

Repository được thiết kế theo table thay vì Aggregate.

❌

---

# 47. Bốn câu hỏi khi thiết kế

Mỗi khi viết code, hãy hỏi:

### 1. Ai quyết định business rule?

```text
Domain
```

### 2. Ai điều phối use case?

```text
Application
```

### 3. Ai lưu Aggregate?

```text
Repository
```

### 4. Ai quyết định commit?

```text
Unit of Work
```

Nếu bạn trả lời được bốn câu này, architecture sẽ rõ ràng hơn rất nhiều.

---

# 48. Bài tập lớn Buổi 25

Hãy xây mini project:

```text
novel_app/
├── domain/
│   ├── story.py
│   ├── chapter.py
│   └── value_objects.py
│
├── application/
│   ├── ports/
│   │   ├── story_repository.py
│   │   └── unit_of_work.py
│   │
│   └── use_cases/
│       ├── create_story.py
│       ├── publish_story.py
│       └── add_chapter.py
│
└── infrastructure/
    └── sqlite/
        ├── story_repository.py
        ├── chapter_repository.py
        └── unit_of_work.py
```

---

# 49. Use Case 1 — Create Story

Flow:

```text
CreateStory
    ↓
Story(...)
    ↓
uow.stories.add()
    ↓
commit()
```

---

# 50. Use Case 2 — Publish Story

Flow:

```text
PublishStory
    ↓
get Story
    ↓
story.publish()
    ↓
save Story
    ↓
commit
```

---

# 51. Use Case 3 — Add Chapter

Flow:

```text
AddChapter
    ↓
get Story
    ↓
story.add_chapter()
    ↓
save
    ↓
commit
```

Nếu Chapter là Entity nội bộ của Story Aggregate, hãy thử thiết kế:

```text
StoryRepository
    ↓
Story + Chapters
```

thay vì:

```text
StoryRepository
ChapterRepository
```

Đây là bài tập **Aggregate Design** rất đáng làm.

---

# 52. Bài tập rollback

Tạo một lỗi giả:

```python
raise RuntimeError("database failure")
```

sau:

```python
story.publish()
```

nhưng trước:

```python
commit()
```

Kiểm tra:

```text
status
```

vẫn phải là:

```text
DRAFT
```

---

# 53. Bài tập Integration

Dùng:

```python
sqlite3.connect(":memory:")
```

Không dùng database thật.

Test toàn bộ:

```text
Use Case
 ↓
UoW
 ↓
Repository
 ↓
SQLite
```

Đây là một integration test rất tốt.

---

# 54. Mental Model cuối Buổi 25

Hãy nhớ hình ảnh này:

```text
             BUSINESS
                │
                ▼
             Aggregate
                │
                ▼
             Use Case
                │
                ▼
          Unit of Work
                │
        ┌───────┴────────┐
        ▼                ▼
    Repository       Repository
        │                │
        └───────┬────────┘
                ▼
             Database
```

Và trách nhiệm:

```text
Aggregate
    → business rules

Use Case
    → orchestration

Repository
    → persistence

Unit of Work
    → transaction
```

---

# 55. Kết thúc Phần V — Repository

Bạn vừa đi qua:

```text
21. Repository Pattern
        ↓
22. Repository Interface
        ↓
23. SQLite Repository
        ↓
24. Unit of Work
        ↓
25. Repository + Unit of Work
```

Đến đây bạn đã có nền tảng khá đầy đủ để xây:

```text
Domain
   +
Application
   +
SQLite Infrastructure
```

mà không để database "xâm nhập" vào Domain.

### Bước tiếp theo

Phần tiếp theo nên đi vào **Domain Service, Domain Event và Specification**, vì đây là lúc chúng ta giải quyết các business rule **không thuộc về một Entity/Aggregate duy nhất**. Đây cũng là bước nối rất tự nhiên từ Tactical DDD hiện tại sang các pattern DDD nâng cao.
