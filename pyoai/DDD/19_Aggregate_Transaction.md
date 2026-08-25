# DDD Deep Dive — Buổi 19

# Aggregate + Transaction

Đây là một trong những bài quan trọng nhất của phần Aggregate.

Ở Buổi 18, chúng ta đã học:

> **Aggregate boundary được quyết định bởi consistency requirement.**

Hôm nay chúng ta đi thêm một bước:

```text
Aggregate
    ↓
Consistency Boundary
    ↓
Transaction Boundary
    ↓
Database Transaction
```

Đặc biệt, chúng ta sẽ dùng **SQLite + Python** để thấy Aggregate ảnh hưởng trực tiếp đến cách viết Repository và transaction như thế nào.

---

# 1. Transaction là gì?

Ở mức đơn giản:

```text
BEGIN
   ↓
Operation 1
   ↓
Operation 2
   ↓
COMMIT
```

Nếu xảy ra lỗi:

```text
BEGIN
   ↓
Operation 1
   ↓
Operation 2
   ↓
ERROR
   ↓
ROLLBACK
```

Mục tiêu:

> Các thay đổi thuộc cùng một đơn vị consistency phải được commit một cách atomic.

---

# 2. Aggregate liên quan gì đến Transaction?

Đây là mental model quan trọng:

```text
Aggregate
    ↓
Consistency Boundary
    ↓
Transaction Boundary
```

Một Aggregate thường là đơn vị mà ta muốn đảm bảo:

```text
"trạng thái bên trong nó luôn hợp lệ"
```

Ví dụ:

```text
Story
├── Story
├── Chapter
└── Chapter
```

Invariant:

```text
Không có hai Chapter cùng number.
```

Khi gọi:

```python
story.add_chapter(chapter)
```

ta muốn:

```text
check invariant
+
persist change
```

được thực hiện một cách nhất quán.

---

# 3. Ví dụ đơn giản

Giả sử:

```python
story.add_chapter(
    chapter_number=10,
    title="Chapter 10",
)
```

Domain:

```text
Story
    ↓
check chapter number
    ↓
add chapter
```

Persistence:

```text
BEGIN
    INSERT chapter
COMMIT
```

Nếu INSERT thất bại:

```text
ROLLBACK
```

Aggregate không được để database rơi vào trạng thái mà domain không chấp nhận.

---

# 4. Atomicity

Atomicity nghĩa là:

> Một transaction được xem như một đơn vị: hoặc tất cả thay đổi thành công, hoặc không thay đổi gì.

Ví dụ:

```text
BEGIN

INSERT Story
INSERT Chapter 1
INSERT Chapter 2

COMMIT
```

Nếu:

```text
INSERT Chapter 2
```

thất bại:

```text
ROLLBACK
```

thì:

```text
Story
Chapter 1
```

cũng không được lưu.

---

# 5. Nhưng có một điểm rất quan trọng

Không phải:

> "Mọi thứ liên quan đến một use case phải nằm trong một transaction."

Mà phải suy nghĩ:

> **Những thay đổi nào cần atomic để bảo vệ invariant?**

Đây là khác biệt giữa:

```text
Application transaction
```

và:

```text
Aggregate consistency
```

---

# 6. Aggregate không đồng nghĩa với toàn bộ Use Case

Ví dụ use case:

```text
Publish Story
```

có thể thực hiện:

```text
1. Publish Story
2. Gửi notification
3. Update search index
4. Clear cache
```

Không nhất thiết phải:

```text
BEGIN

publish story
send notification
update search index
clear cache

COMMIT
```

Đây là thiết kế rất tệ.

---

# 7. Vì sao?

Notification:

```text
Email
```

không phải database transaction của Story.

Search index:

```text
Elasticsearch
```

cũng không nhất thiết thuộc transaction của Story.

Cache:

```text
Redis
```

cũng không.

Thay vào đó:

```text
Story Aggregate
      ↓
COMMIT
      ↓
Domain Event
      ↓
Notification
      ↓
Search Index
      ↓
Cache
```

Đây là hướng đi mà sau này chúng ta sẽ gặp ở:

```text
Domain Events
Outbox Pattern
Event-driven architecture
```

---

# 8. Aggregate Transaction Boundary

Giả sử:

```text
Story Aggregate
```

có:

```text
Story
Chapter
```

và invariant:

```text
chapter_number unique
```

Khi:

```python
story.add_chapter(chapter)
```

thì transaction có thể là:

```text
BEGIN
    UPDATE stories ...
    INSERT chapters ...
COMMIT
```

Nếu cả hai thay đổi phải atomic.

---

# 9. Aggregate quá lớn → Transaction quá lớn

Đây là một lý do khác khiến Aggregate lớn nguy hiểm.

Ví dụ:

```text
Story
├── Chapter × 10,000
├── Comment × 50,000
└── Rating × 100,000
```

Transaction:

```text
BEGIN
    UPDATE ...
    INSERT ...
    INSERT ...
    INSERT ...
    ...
COMMIT
```

Transaction trở nên:

```text
large
slow
contentious
```

---

# 10. SQLite đặc biệt nhạy với điều này

SQLite có concurrency model khác PostgreSQL/MySQL.

Nếu transaction ghi:

```text
BEGIN
   ↓
WRITE
   ↓
WRITE
   ↓
WRITE
   ↓
COMMIT
```

thì khoảng thời gian transaction giữ lock càng lâu, khả năng contention càng cao.

Vì vậy Aggregate design và transaction duration rất quan trọng.

---

# 11. SQLite transaction cơ bản

Python:

```python
import sqlite3

conn = sqlite3.connect("app.db")

try:
    conn.execute("BEGIN")

    conn.execute(
        """
        INSERT INTO stories(id, title)
        VALUES (?, ?)
        """,
        ("story-1", "My Story"),
    )

    conn.execute(
        """
        INSERT INTO chapters(id, story_id, number)
        VALUES (?, ?, ?)
        """,
        ("chapter-1", "story-1", 1),
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

Mental model:

```text
BEGIN
 ↓
Domain operation
 ↓
Persistence
 ↓
COMMIT
```

---

# 12. Python có context manager

Có thể viết:

```python
with sqlite3.connect("app.db") as conn:
    conn.execute(...)
    conn.execute(...)
```

Nếu thành công:

```text
COMMIT
```

Nếu exception:

```text
ROLLBACK
```

Điều này rất tiện.

---

# 13. Nhưng DDD không nên viết transaction trong Entity

Không nên:

```python
class Story:

    def add_chapter(self, chapter):
        with sqlite3.connect(...) as conn:
            ...
```

Tại sao?

Vì Domain Model bây giờ biết:

```text
SQLite
SQL
Connection
Transaction
```

Domain bị phụ thuộc Infrastructure.

---

# 14. Boundary đúng

Nên là:

```text
Application
    ↓
Repository
    ↓
Infrastructure
    ↓
SQLite
```

Domain:

```text
Story
Chapter
```

không biết SQLite.

---

# 15. Domain Model

Ví dụ:

```python
class Story:
    def __init__(self, story_id, title):
        self.id = story_id
        self.title = title
        self._chapters = []

    def add_chapter(self, chapter):
        if any(
            c.number == chapter.number
            for c in self._chapters
        ):
            raise ValueError(
                "Duplicate chapter number"
            )

        self._chapters.append(chapter)
```

Domain bảo vệ:

```text
duplicate chapter
```

---

# 16. Repository

```python
class StoryRepository:
    def get(self, story_id) -> Story:
        ...

    def save(self, story: Story) -> None:
        ...
```

Repository không nên quyết định:

```text
business rule
```

Nó chỉ chịu trách nhiệm persistence.

---

# 17. Application Layer

Use case:

```python
class AddChapter:
    def __init__(self, stories):
        self.stories = stories

    def execute(self, story_id, chapter):
        story = self.stories.get(story_id)

        story.add_chapter(chapter)

        self.stories.save(story)
```

Ở đây:

```text
Application
```

orchestrates.

---

# 18. Transaction ở đâu?

Có một số cách.

Một cách phổ biến:

```text
Application Service
        ↓
Unit of Work
        ↓
Repositories
        ↓
Database
```

Ví dụ:

```python
with unit_of_work:
    story = story_repository.get(story_id)

    story.add_chapter(chapter)

    story_repository.save(story)

    unit_of_work.commit()
```

---

# 19. Unit of Work

Unit of Work có thể hiểu là:

> "Tập hợp các thay đổi cần được commit cùng nhau."

Ví dụ:

```python
class UnitOfWork:
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc, tb):
        ...
```

Application:

```python
with uow:
    story = uow.stories.get(story_id)

    story.add_chapter(chapter)

    uow.commit()
```

---

# 20. SQLite Unit of Work đơn giản

Ví dụ:

```python
class SQLiteUnitOfWork:

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.connection.rollback()
        else:
            self.connection.commit()
```

Sử dụng:

```python
with SQLiteUnitOfWork(conn):
    ...
```

---

# 21. Nhưng hãy cẩn thận

Không nên để Domain biết:

```python
SQLiteUnitOfWork
```

Domain chỉ biết:

```text
business
```

Application biết:

```text
Unit of Work abstraction
```

Infrastructure cung cấp:

```text
SQLiteUnitOfWork
```

---

# 22. Dependency direction

Ta muốn:

```text
Presentation
     ↓
Application
     ↓
Domain
```

và:

```text
Infrastructure
     ↑
Application / Domain abstraction
```

Hay nhìn theo dependency:

```text
Infrastructure ─────→ Domain
Application   ─────→ Domain
Interface     ─────→ Application
```

Domain không phụ thuộc SQLite.

---

# 23. Aggregate + Unit of Work

Một flow tốt:

```text
HTTP / CLI
    ↓
Use Case
    ↓
UnitOfWork
    ↓
Repository.get()
    ↓
Aggregate
    ↓
Business behavior
    ↓
Repository.save()
    ↓
COMMIT
```

Đây là kiến trúc cực kỳ phổ biến trong DDD.

---

# 24. Một vấn đề lớn: "save entire Aggregate"

Giả sử:

```python
story.add_chapter(chapter)
```

Repository:

```python
save(story)
```

có thể phải persistence:

```text
Story
Chapter 1
Chapter 2
Chapter 3
...
```

Nếu có:

```text
10,000 chapters
```

thì mỗi lần save có thể rất nặng.

Đây là một trong những dấu hiệu:

> Aggregate có thể đang quá lớn.

---

# 25. Aggregate và ORM

Nếu dùng ORM:

```python
session.add(story)
session.commit()
```

có vẻ rất tiện.

Nhưng cần hiểu:

```text
ORM object graph
```

không đồng nghĩa:

```text
DDD Aggregate
```

ORM relationship:

```python
story.chapters
```

không tự động có nghĩa:

```text
Chapter thuộc Story Aggregate
```

---

# 26. Với Raw SQLite

Trong dự án của bạn, nếu dùng raw SQL:

```text
Domain
Application
Infrastructure
    ↓
SQLite Repository
```

thì Aggregate boundary càng dễ nhìn thấy.

Ví dụ:

```python
class SQLiteStoryRepository:
    ...
```

và:

```python
class SQLiteChapterRepository:
    ...
```

nếu Story và Chapter là hai Aggregate.

---

# 27. Hai Aggregate trong một Use Case?

Có.

Ví dụ:

```text
User
ReadingProgress
```

Use case:

```text
UpdateReadingProgress
```

có thể cần:

```text
UserRepository
ReadingProgressRepository
```

Nhưng không có nghĩa:

```text
User + ReadingProgress
```

phải cùng Aggregate.

---

# 28. Khi hai Aggregate cùng thay đổi

Ví dụ:

```text
User
ReadingProgress
```

User có thể:

```text
status = ACTIVE
```

ReadingProgress:

```text
chapter_id = 100
```

Một use case có thể:

```text
UPDATE User
UPDATE ReadingProgress
```

trong cùng transaction.

Điều này **có thể** xảy ra.

Nhưng:

> Hai Aggregate vẫn là hai Aggregate.

---

# 29. Đây là điểm rất quan trọng

**Aggregate boundary và transaction boundary thường gần nhau nhưng không phải lúc nào cũng giống nhau.**

Ví dụ:

```text
Aggregate A
Aggregate B
```

có thể được xử lý trong:

```text
Transaction X
```

nhưng business invariant của từng Aggregate vẫn phải được bảo vệ độc lập.

---

# 30. Strong consistency giữa hai Aggregate

Nếu bạn thường xuyên cần:

```text
A + B
```

phải thay đổi atomically:

```text
BEGIN
    update A
    update B
COMMIT
```

hãy đặt câu hỏi:

> Có phải A và B thực sự nên là một Aggregate?

Không phải lúc nào câu trả lời là "có".

Nhưng đây là một **red flag** đáng xem xét.

---

# 31. Eventual consistency

Nếu không cần atomic:

```text
A
 ↓
event
 ↓
B
```

có thể tốt hơn.

Ví dụ:

```text
Story Published
       ↓
StoryPublished
       ↓
Notification
```

Story commit trước.

Notification xử lý sau.

Nếu notification thất bại:

```text
Story vẫn Published
```

Điều này có thể hoàn toàn đúng về business.

---

# 32. Atomicity vs Eventual Consistency

### Strong consistency

```text
A + B
   ↓
same transaction
```

Ưu điểm:

```text
simple consistency
```

Nhược điểm:

```text
coupling
large transaction
contention
```

### Eventual consistency

```text
A
 ↓
Event
 ↓
B
```

Ưu điểm:

```text
loose coupling
scalability
```

Nhược điểm:

```text
temporary inconsistency
retry
failure handling
```

---

# 33. SQLite transaction modes

SQLite có:

```sql
BEGIN DEFERRED;
BEGIN IMMEDIATE;
BEGIN EXCLUSIVE;
```

Trong đó:

### DEFERRED

```sql
BEGIN;
```

thường là deferred transaction.

SQLite chưa lập tức acquire write lock.

### IMMEDIATE

```sql
BEGIN IMMEDIATE;
```

yêu cầu bắt đầu transaction với write intent.

Điều này hữu ích khi bạn biết transaction sẽ ghi.

### EXCLUSIVE

```sql
BEGIN EXCLUSIVE;
```

mạnh hơn và hạn chế concurrency hơn.

Trong ứng dụng thông thường, không nên tùy tiện dùng `EXCLUSIVE`.

---

# 34. SQLite và concurrency

Một pattern phổ biến:

```text
Reader A
Reader B
Reader C

Writer
```

SQLite có thể cho phép nhiều readers đồng thời, nhưng writer có giới hạn nghiêm ngặt hơn.

Vì vậy:

> **Transaction nên ngắn.**

Đặc biệt:

```text
Không làm network I/O
Không crawl website
Không sleep
Không xử lý nặng
```

bên trong database transaction.

---

# 35. Sai lầm cực kỳ phổ biến

Không làm:

```python
with transaction:
    chapter = crawler.fetch(url)
    time.sleep(5)
    parse(chapter)
    save(chapter)
```

Nếu crawler mất:

```text
10 seconds
```

thì database transaction cũng kéo dài:

```text
10 seconds
```

Rất tệ.

---

# 36. Đúng hơn

Tách:

```text
Network
   ↓
Parse
   ↓
Domain
   ↓
Short DB Transaction
```

Ví dụ:

```python
chapter_data = crawler.fetch(url)

chapter = Chapter.create(
    ...
)

with uow:
    repository.save(chapter)
```

Transaction chỉ bao quanh persistence.

---

# 37. Aggregate không phải transaction lock

Một Aggregate:

```text
Story
```

không có nghĩa:

```text
SELECT ... FOR UPDATE
```

Aggregate là **domain concept**.

Database lock là **infrastructure/concurrency mechanism**.

Có thể dùng lock để thực thi consistency, nhưng hai khái niệm không đồng nhất.

---

# 38. Optimistic Concurrency

Một kỹ thuật rất quan trọng.

Aggregate có:

```python
version: int
```

Ví dụ:

```text
Story
id = 1
version = 5
```

Khi update:

```sql
UPDATE stories
SET title = ?,
    version = 6
WHERE id = ?
  AND version = 5;
```

Nếu:

```text
rowcount == 0
```

thì có thể có concurrent modification.

---

# 39. Vì sao Aggregate cần concurrency control?

Giả sử:

```text
Version 5
```

User A load:

```text
Story version 5
```

User B cũng load:

```text
Story version 5
```

A save:

```text
5 → 6
```

B cũng muốn:

```text
5 → 6
```

Nếu không kiểm tra:

```text
B có thể overwrite thay đổi của A.
```

---

# 40. Optimistic concurrency flow

```text
DB
Story version = 5
       ↓
A loads version 5
B loads version 5

A UPDATE WHERE version=5
       ↓
version = 6

B UPDATE WHERE version=5
       ↓
0 rows affected
       ↓
Concurrency conflict
```

Đây là cách rất phổ biến để bảo vệ Aggregate.

---

# 41. Python example

```python
def save(story):
    cursor = conn.execute(
        """
        UPDATE stories
        SET title = ?,
            version = ?
        WHERE id = ?
          AND version = ?
        """,
        (
            story.title,
            story.version + 1,
            story.id.value,
            story.version,
        ),
    )

    if cursor.rowcount != 1:
        raise ConcurrencyError(
            "Story was modified by another transaction"
        )
```

Sau khi thành công:

```python
story.version += 1
```

---

# 42. Aggregate + optimistic locking

Mental model:

```text
Aggregate
   │
   └── version
         ↓
Repository
         ↓
UPDATE ... WHERE version = old_version
```

Điều này cực kỳ hữu ích khi:

```text
Aggregate
```

có nhiều concurrent writers.

---

# 43. SQLite + Aggregate

Với hệ thống của bạn:

```text
CLI
Flet / PySide6
Crawler
Worker
```

có thể có nhiều process/thread cùng truy cập SQLite.

Ví dụ:

```text
Crawler Worker A
Crawler Worker B
Crawler Worker C
        ↓
      SQLite
```

Aggregate design tốt giúp giới hạn:

```text
transaction scope
```

và optimistic locking giúp xử lý:

```text
concurrent update
```

---

# 44. Một thiết kế đáng suy nghĩ cho Chapter

Nếu Chapter là Aggregate riêng:

```python
@dataclass
class Chapter:
    id: ChapterId
    story_id: StoryId
    number: int
    title: str
    content: str
    version: int
```

Database:

```sql
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL,

    UNIQUE(story_id, number)
);
```

Ở đây:

```text
Aggregate invariant
```

có thể là:

```text
Chapter.number > 0
```

và database:

```text
UNIQUE(story_id, number)
```

bảo vệ uniqueness.

---

# 45. Nếu Chapter thuộc Story Aggregate

Khi đó domain có thể:

```python
story.add_chapter(chapter)
```

và Repository:

```text
StoryRepository
```

persistence:

```text
BEGIN

UPDATE stories ...

INSERT chapter ...

COMMIT
```

Aggregate boundary:

```text
Story
└── Chapter
```

---

# 46. Nếu Chapter là Aggregate riêng

Application:

```python
chapter = Chapter.create(
    story_id=story_id,
    number=10,
    ...
)

with uow:
    uow.chapters.add(chapter)
```

Persistence:

```text
BEGIN
INSERT chapter
COMMIT
```

Đây là transaction nhỏ hơn rất nhiều.

---

# 47. Đây chính là trade-off Buổi 18 → 19

### Design A

```text
Story
└── Chapter
```

Ưu:

```text
strong consistency
simple invariant
```

Nhược:

```text
large aggregate
large load
large transaction
concurrency
```

### Design B

```text
Story

Chapter
└── story_id
```

Ưu:

```text
small aggregate
small transaction
better concurrency
```

Nhược:

```text
cross-aggregate consistency
more orchestration
eventual consistency may be needed
```

---

# 48. Một nguyên tắc rất đáng nhớ

> **Don't make a transaction bigger just because two things are related.**

Quan hệ:

```text
Story → Chapter
```

không tự động yêu cầu:

```text
same transaction
```

Chỉ business invariant mới quyết định mức consistency cần thiết.

---

# 49. Transaction Script vs DDD Aggregate

Một số code kiểu:

```python
def add_chapter(story_id, number):
    with conn:
        if exists(story_id, number):
            raise ValueError()

        insert_chapter(...)
```

hoàn toàn có thể đúng.

DDD không yêu cầu:

```text
Aggregate
Repository
UnitOfWork
```

cho mọi dòng code.

Nếu domain đơn giản, Transaction Script có thể đủ.

DDD hữu ích khi business rules trở nên phức tạp.

---

# 50. Khi nào Aggregate thực sự đáng giá?

Khi có:

```text
Business behavior
+
Invariant
+
Lifecycle
+
Consistency
```

Ví dụ:

```python
story.publish()
story.archive()
story.add_chapter()
story.rename()
```

thay vì chỉ:

```sql
UPDATE stories SET ...
```

Aggregate giúp business rule có nơi cư trú rõ ràng.

---

# 51. Kiến trúc hoàn chỉnh

Với Python + SQLite:

```text
                 Interface
             CLI / PySide6
                    │
                    ↓
              Application
                    │
              ┌─────┴─────┐
              │           │
           Use Case    UnitOfWork
              │           │
              ↓           ↓
             Domain     Repository
              │           │
         ┌────┴────┐      │
         │         │      │
      Aggregate   VO      │
                           ↓
                     Infrastructure
                           │
                         SQLite
```

Đây chính là cầu nối giữa:

```text
DDD
```

và:

```text
Clean Architecture
```

mà bạn đã học ở phần trước.

---

# 52. Quy tắc thực hành

Khi implement một Use Case, hãy suy nghĩ theo thứ tự:

```text
1. Load Aggregate
       ↓
2. Execute domain behavior
       ↓
3. Aggregate remains valid
       ↓
4. Save Aggregate
       ↓
5. Commit transaction
```

Không:

```text
1. UPDATE database
2. UPDATE database
3. UPDATE database
4. rồi mới nghĩ business rule
```

---

# 53. Một flow hoàn chỉnh

Ví dụ:

```python
def execute(command):
    with uow:
        story = uow.stories.get(command.story_id)

        chapter = Chapter.create(
            number=command.number,
            title=command.title,
        )

        story.add_chapter(chapter)

        uow.stories.save(story)
```

Flow:

```text
Command
  ↓
Use Case
  ↓
UoW BEGIN
  ↓
Repository GET
  ↓
Story Aggregate
  ↓
story.add_chapter()
  ↓
Repository SAVE
  ↓
COMMIT
```

---

# 54. Nhưng nếu Chapter là Aggregate riêng?

Flow sẽ thành:

```python
def execute(command):
    with uow:
        chapter = Chapter.create(
            story_id=command.story_id,
            number=command.number,
            title=command.title,
        )

        uow.chapters.add(chapter)
```

và database:

```sql
UNIQUE(story_id, number)
```

có thể bảo vệ uniqueness.

Đây là một ví dụ tuyệt vời về việc **Aggregate Design thay đổi Application Layer và Repository Layer**.

---

# 55. Những điều cần nhớ sau Buổi 19

Nếu chỉ nhớ 8 ý, hãy nhớ:

### 1.

```text
Aggregate = consistency boundary
```

### 2.

```text
Aggregate thường là transaction boundary
```

nhưng không phải tuyệt đối.

### 3.

```text
Transaction càng lớn
→ concurrency càng khó
```

### 4.

```text
Aggregate càng lớn
→ transaction càng dễ lớn
```

### 5.

```text
Aggregate khác nhau
→ reference bằng ID
```

### 6.

```text
Domain không biết SQLite
```

### 7.

```text
Unit of Work
```

là một abstraction hữu ích để quản lý transaction.

### 8.

```text
Strong consistency
```

không phải lúc nào cũng cần; có thể dùng:

```text
Eventual consistency
```

khi business cho phép.

---

# Bài tập Buổi 19

Hãy thiết kế transaction cho hệ thống đọc truyện.

## Bài 1

Use case:

```text
Add Chapter
```

Thiết kế 2 version:

### Version A

```text
Story
└── Chapter
```

### Version B

```text
Story

Chapter
└── story_id
```

Viết flow transaction cho cả hai.

---

## Bài 2

Use case:

```text
Update Reading Progress
```

Bạn có:

```text
User Aggregate
ReadingProgress Aggregate
```

Hãy quyết định:

```text
Có cần cùng transaction không?
```

và giải thích tại sao.

---

## Bài 3

Use case:

```text
Publish Story
```

Sau khi publish:

```text
→ gửi notification
→ cập nhật search index
→ clear cache
```

Hãy thiết kế:

```text
Transaction
    ↓
Domain Event
    ↓
Notification
    ↓
Search
    ↓
Cache
```

và xác định cái gì **không nên nằm trong database transaction của Story**.

---

## Bài 4 — SQLite

Thiết kế:

```text
SQLiteUnitOfWork
StoryRepository
ChapterRepository
```

với flow:

```text
BEGIN
    ↓
load Aggregate
    ↓
domain behavior
    ↓
save
    ↓
COMMIT
```

và xử lý:

```text
ROLLBACK
```

khi có exception.

---

### Bài quan trọng nhất

Hãy trả lời câu này:

> **Nếu `Story` và `Chapter` có quan hệ 1:N, tại sao ta không mặc định cho `Chapter` vào `Story Aggregate`?**

Nếu bạn trả lời được câu này bằng các khái niệm:

```text
Invariant
Consistency
Transaction
Concurrency
Aggregate Size
Lifecycle
Reference by ID
```

thì bạn đã nắm được **cốt lõi của Aggregate Design**.

Buổi tiếp theo **Buổi 20 — Aggregate Design Workshop** chúng ta sẽ lấy chính 6 domain object:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

và **tự tay phân chia chúng thành Aggregate**, sau đó thiết kế luôn:

```text
Aggregate Root
Entity
Value Object
Reference by ID
Repository
Transaction Boundary
```

thành một domain model hoàn chỉnh cho hệ thống đọc truyện.
