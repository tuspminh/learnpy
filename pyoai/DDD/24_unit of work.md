# DDD Deep Dive — Buổi 24

# Unit of Work — Transaction + Commit + Rollback

Đây là một trong những buổi **quan trọng nhất của Tactical DDD**.

Sau Buổi 23, ta có:

```text
Use Case
    ↓
Repository Interface
    ↓
SQLite Repository
    ↓
SQLite
```

Nhưng xuất hiện một vấn đề lớn:

> Nếu một Use Case cần thay đổi **nhiều Aggregate**, làm sao đảm bảo tất cả thay đổi thành công hoặc tất cả thất bại?

Đó chính là lý do **Unit of Work (UoW)** xuất hiện.

---

# 1. Bài toán thực tế

Giả sử hệ thống đọc truyện có:

```text
Story
Chapter
```

Một Use Case:

> Thêm Chapter mới vào Story.

Có thể cần:

```text
1. Load Story
2. Kiểm tra business rule
3. Thêm Chapter
4. Save Story
5. Save Chapter
6. Commit
```

Nếu xảy ra lỗi ở bước 5:

```text
Story đã save
Chapter chưa save
```

Database trở thành trạng thái không nhất quán.

Ta muốn:

```text
        SUCCESS
           ↓
Story ────────┐
              ├── COMMIT
Chapter ──────┘
```

Hoặc:

```text
        ERROR
           ↓
Story ────────┐
              ├── ROLLBACK
Chapter ──────┘
```

---

# 2. Unit of Work là gì?

Có thể hiểu đơn giản:

> **Unit of Work đại diện cho một business transaction.**

Nó quản lý:

```text
Transaction
    +
Repositories
    +
Commit
    +
Rollback
```

Mô hình:

```text
Application
     ↓
UnitOfWork
     ├── StoryRepository
     ├── ChapterRepository
     └── ...
     
     ↓
   COMMIT
```

---

# 3. Repository và Unit of Work khác nhau

Đây là điểm phải phân biệt thật rõ.

### Repository

Trả lời:

> "Làm thế nào để lấy/lưu Aggregate?"

```text
get()
add()
save()
```

### Unit of Work

Trả lời:

> "Khi nào toàn bộ thay đổi được commit?"

```text
commit()
rollback()
```

---

# 4. Repository không quản lý transaction

Không nên:

```python
class SQLiteStoryRepository:

    def save(self, story):
        self.connection.execute(...)
        self.connection.commit()
```

Vì:

```text
StoryRepository
```

không biết transaction lớn hơn của Use Case.

---

# 5. UoW quản lý transaction

Ta muốn:

```python
with uow:
    story = uow.stories.get(story_id)

    story.publish()

    uow.stories.save(story)

    uow.commit()
```

Nếu:

```python
uow.commit()
```

thành công:

```text
COMMIT
```

Nếu exception:

```text
ROLLBACK
```

---

# 6. Unit of Work Interface

Ta bắt đầu bằng abstraction:

```python
from typing import Protocol


class UnitOfWork(Protocol):

    stories: StoryRepository
    chapters: ChapterRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

Đây là **Application Port**.

Application không biết SQLite.

---

# 7. Context Manager

Ta muốn syntax:

```python
with uow:
    ...
```

Do đó UoW cần:

```python
__enter__()
__exit__()
```

Ví dụ:

```python
class UnitOfWork:

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        ...
```

---

# 8. Ý nghĩa `__exit__`

Python gọi:

```python
with uow:
    ...
```

tương đương về ý tưởng:

```text
__enter__()
    ↓
business operation
    ↓
__exit__()
```

Nếu không có exception:

```text
exc_type = None
```

Nếu có exception:

```text
exc_type != None
```

---

# 9. SQLite UoW

Ta xây:

```python
class SQLiteUnitOfWork:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection
```

Sau đó:

```python
self.stories = SQLiteStoryRepository(
    connection
)

self.chapters = SQLiteChapterRepository(
    connection
)
```

---

# 10. Constructor hoàn chỉnh

```python
class SQLiteUnitOfWork:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

        self.stories = SQLiteStoryRepository(
            connection
        )

        self.chapters = SQLiteChapterRepository(
            connection
        )
```

Ta có:

```text
UoW
 │
 ├── stories
 │
 └── chapters
```

Tất cả dùng **cùng connection**.

Đây là điểm cực kỳ quan trọng.

---

# 11. Tại sao phải cùng connection?

SQLite transaction gắn với connection.

Nếu:

```text
StoryRepository
    ↓
connection A
```

và:

```text
ChapterRepository
    ↓
connection B
```

thì:

```text
COMMIT A
```

không đảm bảo:

```text
COMMIT B
```

Do đó:

```text
UnitOfWork
    ↓
ONE CONNECTION
    ↓
ONE TRANSACTION
```

---

# 12. Implement `__enter__`

Đơn giản:

```python
def __enter__(self):
    return self
```

Nhưng transaction thực sự sẽ bắt đầu khi có database operation.

SQLite có transaction behavior riêng.

Ta có thể chủ động:

```python
self.connection.execute(
    "BEGIN"
)
```

Tuy nhiên cần hiểu transaction mode trước khi áp dụng cứng nhắc.

---

# 13. Implement `commit`

```python
def commit(self) -> None:
    self.connection.commit()
```

---

# 14. Implement `rollback`

```python
def rollback(self) -> None:
    self.connection.rollback()
```

---

# 15. Implement `__exit__`

Một phiên bản cơ bản:

```python
def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
):
    if exc_type is not None:
        self.rollback()
```

Nhưng chú ý:

> **Không nhất thiết tự commit trong `__exit__`.**

Ta muốn:

```python
with uow:
    ...
    uow.commit()
```

rất rõ ràng.

---

# 16. UoW hoàn chỉnh

```python
class SQLiteUnitOfWork:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

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

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()
```

Đây là phiên bản cơ bản.

---

# 17. Sử dụng

```python
with uow:
    story = uow.stories.get(
        story_id
    )

    story.publish()

    uow.stories.save(story)

    uow.commit()
```

Flow:

```text
BEGIN
 ↓
get Story
 ↓
publish
 ↓
save Story
 ↓
COMMIT
```

---

# 18. Khi có exception

```python
with uow:
    story = uow.stories.get(
        story_id
    )

    story.publish()

    uow.stories.save(story)

    raise RuntimeError("Something failed")
```

Python gọi:

```python
__exit__(
    exc_type=RuntimeError,
    ...
)
```

UoW:

```python
self.rollback()
```

Flow:

```text
save
 ↓
ERROR
 ↓
ROLLBACK
```

---

# 19. Exception có bị nuốt không?

Không.

`__exit__()` trả về:

```python
None
```

hoặc:

```python
False
```

thì exception tiếp tục propagate.

Ví dụ:

```python
def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
):
    if exc_type is not None:
        self.rollback()

    return False
```

Đây là cách rõ ràng.

---

# 20. Một lỗi nguy hiểm

Không viết:

```python
def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
):
    if exc_type:
        self.rollback()

    return True
```

Vì:

```python
return True
```

có nghĩa:

> Exception đã được xử lý.

Exception sẽ bị nuốt.

Thông thường UoW không nên làm vậy.

---

# 21. UoW + Use Case

Đây mới là thiết kế chúng ta muốn.

```python
class AddChapter:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

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
                raise StoryNotFound(story_id)

            story.add_chapter(chapter)

            self.uow.stories.save(story)

            self.uow.chapters.add(chapter)

            self.uow.commit()
```

---

# 22. Flow

```text
                 AddChapter
                     │
                     ▼
                UnitOfWork
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       StoryRepo           ChapterRepo
          │                     │
          └──────────┬──────────┘
                     ▼
                  SQLite
                     │
                     ▼
                  COMMIT
```

---

# 23. Nếu Chapter save thất bại?

Ví dụ:

```python
self.uow.stories.save(story)

self.uow.chapters.add(chapter)

raise RuntimeError(...)
```

Kết quả:

```text
Story UPDATE
     ↓
Chapter INSERT
     ↓
ERROR
     ↓
ROLLBACK
```

Database quay về trạng thái trước transaction.

---

# 24. Atomicity

Đây chính là chữ **A** trong ACID:

> Atomicity

Có nghĩa:

```text
ALL
```

hoặc:

```text
NOTHING
```

Ví dụ:

```text
Story UPDATE
Chapter INSERT
ReadingProgress UPDATE
```

hoặc tất cả thành công:

```text
COMMIT
```

hoặc tất cả thất bại:

```text
ROLLBACK
```

---

# 25. Consistency

Transaction phải đưa database từ:

```text
Valid State
```

sang:

```text
Valid State
```

Ví dụ:

```text
Story tồn tại
Chapter thuộc Story
```

Không được để:

```text
Chapter.story_id = "abc"
```

nhưng Story `"abc"` không tồn tại.

---

# 26. Isolation

Nếu có nhiều transaction cùng chạy:

```text
Transaction A
Transaction B
```

chúng không được tạo ra trạng thái đọc/ghi không hợp lệ.

SQLite có cơ chế locking và isolation riêng.

Ở mức DDD:

> Aggregate + Transaction boundary giúp ta xác định **cái gì phải được thay đổi nhất quán cùng nhau**.

---

# 27. Durability

Sau:

```text
COMMIT
```

database đảm bảo dữ liệu đã commit được persist theo cơ chế durability của SQLite/storage.

DDD không trực tiếp giải quyết phần này.

Đây là trách nhiệm của database infrastructure.

---

# 28. Aggregate và UoW

Đây là mối quan hệ rất quan trọng:

```text
Aggregate
    ↓
Consistency Boundary
    ↓
Transaction Boundary
```

Nhưng không phải:

> "Mỗi Aggregate bắt buộc phải có một transaction."

Mà là:

> Transaction nên bảo vệ những thay đổi cần tính nhất quán trong cùng một business operation.

---

# 29. Một Aggregate thường được load/save cùng transaction

Ví dụ:

```python
with uow:
    story = uow.stories.get(story_id)

    story.publish()

    uow.stories.save(story)

    uow.commit()
```

Đây là pattern rất tự nhiên.

---

# 30. Nhiều Aggregate thì sao?

Ví dụ:

```text
Story
ReadingProgress
```

Nếu business operation yêu cầu cả hai phải thay đổi atomic:

```python
with uow:
    story = uow.stories.get(story_id)
    progress = uow.progress.get(
        user_id,
        story_id,
    )

    story.publish()
    progress.reset()

    uow.stories.save(story)
    uow.progress.save(progress)

    uow.commit()
```

UoW bao quanh transaction.

---

# 31. Nhưng đừng lạm dụng

Nếu:

```text
Story
User
Notification
CrawlerJob
ReadingProgress
```

đều bị load vào một transaction cho mọi Use Case:

```text
Transaction
    ├── Story
    ├── User
    ├── Notification
    ├── CrawlerJob
    └── ReadingProgress
```

Aggregate design có thể đang quá coupling.

DDD khuyến khích:

> Transaction càng nhỏ càng tốt, miễn vẫn bảo vệ invariant cần thiết.

---

# 32. UoW không phải Repository

Đừng viết:

```python
class StoryRepository:

    def get(...):
        ...

    def save(...):
        ...

    def commit(...):
        ...

    def rollback(...):
        ...
```

rồi không có UoW.

Khi có nhiều repository:

```text
StoryRepository
ChapterRepository
UserRepository
```

transaction coordination thuộc về:

```text
UnitOfWork
```

---

# 33. UoW là Coordinator

```text
                  UnitOfWork
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    StoryRepo     ChapterRepo   ProgressRepo
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                   Database
```

UoW không chứa business rule.

Nó điều phối persistence transaction.

---

# 34. Interface hoàn chỉnh hơn

Ta có thể định nghĩa:

```python
from typing import Protocol


class UnitOfWork(Protocol):

    stories: StoryRepository
    chapters: ChapterRepository

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

---

# 35. Nhưng có một thiết kế tốt hơn

Thay vì:

```python
uow.commit()
```

ta có thể thiết kế:

```python
with uow:
    ...
    uow.commit()
```

hoặc:

```python
with uow:
    ...
```

và tự commit nếu không exception.

Ví dụ:

```python
def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
):
    if exc_type is not None:
        self.rollback()
    else:
        self.commit()
```

Cách này cũng phổ biến.

---

# 36. Explicit Commit vs Implicit Commit

### Explicit

```python
with uow:
    ...
    uow.commit()
```

Ưu điểm:

```text
transaction boundary rất rõ
```

Nhược:

```text
quên commit
```

### Implicit

```python
with uow:
    ...
```

Nếu không exception:

```text
COMMIT
```

Nếu exception:

```text
ROLLBACK
```

Ưu điểm:

```text
ít boilerplate
```

Nhược:

```text
commit behavior ít explicit hơn
```

---

# 37. Tôi khuyên dùng cách nào?

Trong quá trình học DDD:

```python
with uow:
    ...
    uow.commit()
```

tôi khuyên dùng **explicit commit**.

Lý do:

Bạn sẽ nhìn thấy rõ:

```text
Business operation
        ↓
Commit boundary
```

Sau này có thể refactor thành implicit commit nếu phù hợp.

---

# 38. SQLite Transaction

Đây là phần Infrastructure.

Ví dụ:

```python
connection.execute(
    "BEGIN"
)
```

Sau đó:

```text
INSERT
UPDATE
DELETE
```

và:

```python
connection.commit()
```

hoặc:

```python
connection.rollback()
```

---

# 39. `with connection`

SQLite cũng hỗ trợ:

```python
with connection:
    connection.execute(...)
```

Khi block kết thúc:

```text
success → commit
error   → rollback
```

Nhưng UoW vẫn hữu ích vì nó gom:

```text
Repositories
+
Transaction
```

vào một abstraction phù hợp với Application.

---

# 40. Một UoW thực tế hơn

```python
class SQLiteUnitOfWork:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
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

---

# 41. Composition Root

Ở ngoài cùng:

```python
connection = sqlite3.connect(
    "novel.db"
)

connection.row_factory = sqlite3.Row

uow = SQLiteUnitOfWork(
    connection
)
```

Sau đó:

```python
use_case = AddChapter(uow)
```

Dependency graph:

```text
CLI / GUI
   ↓
SQLite connection
   ↓
SQLiteUnitOfWork
   ↓
AddChapter
```

---

# 42. Test UoW

Dùng SQLite memory:

```python
connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row
```

Setup schema.

Sau đó:

```python
uow = SQLiteUnitOfWork(connection)
```

Test commit:

```python
with uow:
    uow.stories.add(story)
    uow.commit()
```

Sau đó query:

```python
result = uow.stories.get(story.id)

assert result is not None
```

---

# 43. Test rollback

Đây là test cực kỳ quan trọng.

```python
try:
    with uow:
        uow.stories.add(story)

        raise RuntimeError(
            "Something failed"
        )
except RuntimeError:
    pass
```

Sau đó:

```python
result = uow.stories.get(story.id)

assert result is None
```

Nếu test này pass:

> Bạn đã chứng minh transaction boundary đang hoạt động.

---

# 44. Test nhiều Repository

Đây mới là test quan trọng hơn.

```python
try:
    with uow:
        uow.stories.add(story)

        uow.chapters.add(chapter)

        raise RuntimeError()
except RuntimeError:
    pass
```

Sau đó:

```python
assert uow.stories.get(
    story.id
) is None

assert uow.chapters.get(
    chapter.id
) is None
```

Cả hai phải rollback.

---

# 45. Đây là sức mạnh của UoW

Không có UoW:

```text
StoryRepository
    ↓
COMMIT

ChapterRepository
    ↓
COMMIT
```

Có UoW:

```text
StoryRepository ──┐
                  │
ChapterRepository ├── Transaction
                  │
ProgressRepository┘
                  ↓
                COMMIT
```

---

# 46. UoW và Testability

Application chỉ cần:

```python
class AddChapter:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

Test có thể dùng:

```python
FakeUnitOfWork
```

hoặc:

```python
InMemoryUnitOfWork
```

Ví dụ:

```python
class FakeUnitOfWork:

    def __init__(self):
        self.stories = InMemoryStoryRepository()
        self.chapters = InMemoryChapterRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        ...
```

---

# 47. Nhưng InMemory không mô phỏng transaction thật

Đây là điểm cần nhớ.

```text
InMemoryUnitOfWork
```

tốt cho:

```text
Application unit test
```

nhưng:

```text
SQLiteUnitOfWork
```

cần:

```text
Integration test
```

để kiểm tra:

```text
SQL
transaction
rollback
constraints
mapping
```

---

# 48. Unit Test vs Integration Test

### Unit Test

```text
Use Case
   ↓
Fake UoW
```

Nhanh.

### Integration Test

```text
Use Case
   ↓
SQLite UoW
   ↓
SQLite :memory:
```

Kiểm tra toàn bộ persistence path.

DDD project tốt thường cần cả hai.

---

# 49. Một lỗi thiết kế khác

Không nên:

```python
class SQLiteUnitOfWork:

    def add_story(self, story):
        ...

    def add_chapter(self, chapter):
        ...

    def publish_story(self):
        ...
```

UoW không phải Application Service.

UoW chỉ:

```text
Transaction
+
Repositories
```

Business operation:

```text
AddChapter
PublishStory
```

thuộc Application Layer.

---

# 50. Architecture hoàn chỉnh đến Buổi 24

```text
                 Interface / CLI / GUI
                          │
                          ▼
                    Application
                          │
                  ┌───────┴───────┐
                  │    Use Case   │
                  └───────┬───────┘
                          │
                          ▼
                    UnitOfWork
                    │       │
                    ▼       ▼
               StoryRepo  ChapterRepo
                    │       │
                    └───┬───┘
                        ▼
                  SQLite Adapter
                        │
                        ▼
                      SQLite
```

Domain nằm bên trong:

```text
Use Case
   ↓
Domain Entity
   ↓
Business behavior
```

---

# 51. Mối quan hệ DDD quan trọng

Đến đây bạn nên nhìn được:

```text
Aggregate
    ↓
Consistency Boundary

Repository
    ↓
Aggregate Persistence

Unit of Work
    ↓
Transaction Boundary
```

Ba khái niệm này liên kết rất chặt:

```text
Aggregate
    │
    │ persisted by
    ▼
Repository
    │
    │ coordinated by
    ▼
Unit of Work
    │
    │ executes
    ▼
Transaction
```

---

# 52. Một nguyên tắc cực kỳ quan trọng

> **Không phải database transaction quyết định Aggregate boundary.**

Ngược lại, trong thiết kế DDD tốt:

```text
Business invariant
       ↓
Aggregate boundary
       ↓
Consistency requirement
       ↓
Transaction design
```

Đừng bắt đầu bằng:

> "SQLite cho phép transaction như thế nào?"

Hãy bắt đầu bằng:

> "Business operation nào cần atomic?"

---

# 53. Ví dụ hệ thống đọc truyện

Giả sử:

```text
Story
Chapter
ReadingProgress
```

### Đọc Chapter

Có thể:

```text
load Chapter
+
load ReadingProgress
```

Không nhất thiết phải cùng transaction.

### Hoàn thành Chapter

Nếu business yêu cầu:

```text
Chapter completed
+
ReadingProgress updated
```

phải atomic thì:

```text
UoW
 ├── ChapterRepository
 └── ReadingProgressRepository
       ↓
    COMMIT
```

---

# 54. Nhưng Notification thì sao?

Không nên nhất thiết:

```text
Story
+
Chapter
+
Notification
```

cùng một SQLite transaction.

Notification có thể là:

```text
Domain Event
     ↓
Message / Event
     ↓
Notification handler
```

Đây là chủ đề DDD nâng cao sau này.

---

# 55. Tổng kết Buổi 24

Bạn cần ghi nhớ:

```text
Repository
    = Persistence abstraction

Unit of Work
    = Transaction abstraction
```

Repository:

```text
get
add
save
remove
```

UoW:

```text
commit
rollback
repositories
transaction boundary
```

---

# 56. Công thức kiến trúc

```text
Aggregate
      ↓
Repository
      ↓
Unit of Work
      ↓
Transaction
      ↓
Database
```

Nhưng dependency vẫn hướng vào trong:

```text
Application
    ↓
UoW Interface
    ↓
Repository Interface
    ↑
SQLite Implementation
```

---

# 57. Bài tập Buổi 24

## Bài 1 — SQLiteUnitOfWork

Tự implement:

```python
class SQLiteUnitOfWork:

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

    def commit(self):
        ...

    def rollback(self):
        ...
```

---

## Bài 2 — Test rollback

Viết test chứng minh:

```text
Story INSERT
+
Chapter INSERT
+
Exception
```

→ cả hai đều rollback.

---

## Bài 3 — Use Case

Viết:

```python
class AddChapter:
    ...
```

với:

```python
with self.uow:
    ...
```

Use Case phải:

1. Load Story.
2. Kiểm tra Story tồn tại.
3. `story.add_chapter(...)`.
4. Save Story.
5. Add Chapter.
6. Commit.

---

## Bài 4 — câu hỏi kiến trúc

Giải thích tại sao đoạn này **sai**:

```python
class SQLiteStoryRepository:

    def save(self, story):
        self.connection.execute(...)
        self.connection.commit()
```

và tại sao:

```python
with uow:
    story = uow.stories.get(...)
    story.publish()
    uow.stories.save(story)
    uow.commit()
```

tốt hơn.

---

## Bài 5 — nâng cao

Thiết kế:

```text
Story
Chapter
ReadingProgress
```

và trả lời:

> Khi user đánh dấu một chapter là đã đọc, những object nào cần nằm trong cùng transaction? Vì sao?

Đây là bài tập quan trọng vì nó buộc bạn **thiết kế từ business invariant**, thay vì chỉ nghĩ từ database.

---

### Sau Buổi 24, roadmap của chúng ta

```text
21 Repository Pattern
22 Repository Interface
23 SQLite Repository
24 Unit of Work        ← hôm nay
25 Repository + UoW
```

**Buổi 25** sẽ ghép tất cả lại thành một flow hoàn chỉnh:

```text
CLI / Use Case
      ↓
UnitOfWork
      ↓
StoryRepository
      ↓
Story Aggregate
      ↓
Business Behavior
      ↓
Repository.save()
      ↓
UnitOfWork.commit()
      ↓
SQLite
```

và chúng ta sẽ xây một **mini DDD persistence architecture** hoàn chỉnh cho hệ thống đọc truyện.
