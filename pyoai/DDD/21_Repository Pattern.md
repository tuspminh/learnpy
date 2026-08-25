# DDD Deep Dive — Buổi 21

# Repository Pattern

Hôm nay chúng ta bước sang **Phần V — Repository**.

Đây là phần cực kỳ quan trọng vì nó nối:

```text
DDD Domain
    ↓
Application
    ↓
Persistence
    ↓
SQLite
```

Trong hệ thống đọc truyện của bạn, chúng ta đã có Aggregate:

```text
Story
Chapter
CrawlerSource
CrawlerJob
User
ReadingProgress
```

Bây giờ câu hỏi là:

> **Làm thế nào để lấy một Aggregate từ database mà Domain không cần biết database là SQLite?**

Câu trả lời là:

```text
Repository
```

---

# 1. Repository là gì?

Repository là abstraction đại diện cho việc:

> **truy cập và lưu trữ Aggregate trong persistence system.**

Ví dụ:

```python
story = story_repository.get(story_id)
```

hoặc:

```python
story_repository.save(story)
```

Application không cần biết:

```text
SELECT ...
INSERT ...
UPDATE ...
sqlite3.Connection
```

---

# 2. Mental Model

Hãy hình dung Repository như một collection:

```text
Repository
    ↓
"Collection of Aggregates"
```

Ví dụ:

```python
story = story_repository.get(story_id)
```

gần giống như:

```python
story = stories[story_id]
```

Application chỉ quan tâm:

```text
Story
```

chứ không quan tâm:

```text
SQLite row
```

---

# 3. Repository không phải Database

Đây là điểm đầu tiên cần phân biệt.

Không nên nghĩ:

```text
Repository = Database
```

Repository là:

```text
Domain-oriented abstraction
```

Database là:

```text
Persistence mechanism
```

Ví dụ:

```text
StoryRepository
       ↓
SQLiteStoryRepository
       ↓
SQLite
```

---

# 4. Repository không phải DAO

Repository và DAO có vẻ rất giống nhau nhưng mục đích khác nhau.

### DAO

DAO thường hướng về persistence:

```python
story_dao.insert(...)
story_dao.update(...)
story_dao.select_by_id(...)
```

Nó thường gần database.

### Repository

Repository hướng về:

```text
Domain Aggregate
```

Ví dụ:

```python
story_repository.get(story_id)
```

---

# 5. DAO tư duy từ Database

DAO:

```text
Database
   ↓
Table
   ↓
Row
   ↓
DAO
```

Ví dụ:

```python
row = dao.find_by_id("story-1")
```

Kết quả có thể là:

```python
{
    "id": "story-1",
    "title": "One Piece",
    "status": "published",
}
```

---

# 6. Repository tư duy từ Domain

Repository:

```text
Domain
   ↓
Aggregate
   ↓
Repository
   ↓
Persistence
```

Ví dụ:

```python
story = repository.get(
    StoryId("story-1")
)
```

Kết quả:

```python
Story(...)
```

chứ không phải:

```python
dict
```

---

# 7. So sánh

| DAO                   | Repository                     |
| --------------------- | ------------------------------ |
| Database-oriented     | Domain-oriented                |
| Table/row             | Aggregate                      |
| CRUD                  | Domain-oriented operations     |
| SQL gần abstraction   | SQL ẩn bên dưới                |
| Có thể trả dict/model | Thường trả Domain object       |
| Infrastructure        | Domain/Application abstraction |

Không phải mọi project cần Repository.

Nhưng trong DDD, Repository rất hữu ích khi Domain cần persistence abstraction.

---

# 8. Repository thường dành cho Aggregate Root

Đây là nguyên tắc quan trọng.

Ta có:

```text
Story Aggregate
    Root = Story
```

thì:

```python
StoryRepository
```

Ta có:

```text
Chapter Aggregate
    Root = Chapter
```

thì:

```python
ChapterRepository
```

---

# 9. Không tạo Repository cho mọi Entity

Ví dụ:

```text
Order Aggregate
├── Order
└── OrderItem
```

Nếu:

```text
Order = Aggregate Root
OrderItem = Entity bên trong
```

thì thường chỉ có:

```python
OrderRepository
```

không phải:

```python
OrderRepository
OrderItemRepository
```

---

# 10. Áp dụng vào hệ thống đọc truyện

Chúng ta đã thiết kế:

```text
Story Aggregate
Chapter Aggregate
CrawlerSource Aggregate
CrawlerJob Aggregate
User Aggregate
ReadingProgress Aggregate
```

Do đó có thể có:

```python
StoryRepository
ChapterRepository
CrawlerSourceRepository
CrawlerJobRepository
UserRepository
ReadingProgressRepository
```

---

# 11. Repository abstraction

Ví dụ:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id):
        pass

    @abstractmethod
    def save(self, story):
        pass
```

Đây là interface.

Nó không biết:

```text
SQLite
PostgreSQL
MySQL
MongoDB
```

---

# 12. Tại sao cần abstraction?

Hãy tưởng tượng Application viết:

```python
class PublishStory:

    def execute(self, story_id):
        story = sqlite_repository.get(story_id)

        story.publish()

        sqlite_repository.save(story)
```

Application bây giờ phụ thuộc:

```text
SQLite
```

Không tốt.

---

# 13. Dependency Inversion

Ta muốn:

```text
Application
    ↓
StoryRepository
    ↑
SQLiteStoryRepository
```

Chứ không:

```text
Application
    ↓
SQLiteStoryRepository
    ↓
SQLite
```

Repository interface là abstraction.

Infrastructure implement abstraction.

---

# 14. Domain không biết SQLite

Domain:

```python
class Story:

    def publish(self):
        ...
```

Không có:

```python
import sqlite3
```

Không có:

```python
cursor.execute(...)
```

Không có:

```python
connection.commit()
```

Domain chỉ biết business.

---

# 15. Persistence Ignorance

Một khái niệm quan trọng:

> Domain model không nên bị thiết kế xoay quanh persistence mechanism.

Ví dụ xấu:

```python
class Story:
    table_name = "stories"

    def save(self):
        ...
```

Domain object đang biết:

```text
Database
Table
Persistence
```

---

# 16. Domain Model đúng hơn

```python
class Story:

    def publish(self):
        if self.status == StoryStatus.ARCHIVED:
            raise DomainError(
                "Cannot publish archived story"
            )

        self.status = StoryStatus.PUBLISHED
```

Story chỉ biết:

```text
Business rule
```

---

# 17. Repository chịu trách nhiệm Persistence

```python
repository.save(story)
```

Repository biết:

```text
How to save Story
```

Domain biết:

```text
What a valid Story is
```

Đây là separation rất quan trọng.

---

# 18. Repository giống Collection

Martin Fowler thường mô tả Repository theo hướng:

> một abstraction giống collection của domain objects.

Ví dụ:

```python
stories = StoryRepository()

story = stories.get(story_id)
```

Tưởng tượng phía sau:

```text
StoryRepository
      ↓
┌────────────────────────┐
│ Story 1                │
│ Story 2                │
│ Story 3                │
└────────────────────────┘
```

Application không cần biết collection nằm:

```text
RAM
SQLite
PostgreSQL
API
```

---

# 19. Repository API nên đơn giản

Ví dụ:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id: StoryId) -> Story | None:
        ...

    @abstractmethod
    def add(self, story: Story) -> None:
        ...

    @abstractmethod
    def save(self, story: Story) -> None:
        ...

    @abstractmethod
    def remove(self, story: Story) -> None:
        ...
```

Nhưng đừng vội biến Repository thành:

```python
get_by_xxx()
get_by_yyy()
get_by_zzz()
find_by_a()
find_by_b()
find_by_c()
...
```

Repository API nên phản ánh nhu cầu domain/application.

---

# 20. Một Repository CRUD khổng lồ là dấu hiệu xấu

Ví dụ:

```python
class StoryRepository:

    def get(...)
    def get_all(...)
    def get_by_title(...)
    def get_by_source(...)
    def get_by_status(...)
    def get_by_author(...)
    def get_by_category(...)
    def get_by_created_at(...)
    def search(...)
    def filter(...)
    def sort(...)
    def paginate(...)
```

Repository bắt đầu biến thành:

```text
Generic Query Service
```

không còn rõ ràng nữa.

---

# 21. `get()` nên trả Aggregate

Ví dụ:

```python
story = repository.get(
    StoryId("story-1")
)
```

Kết quả:

```python
Story(
    id=...,
    title=...,
    status=...
)
```

Application sau đó có thể:

```python
story.publish()
```

Đây chính là điểm Repository khác DAO.

---

# 22. Repository không chứa Business Rule

Ví dụ không nên:

```python
class StoryRepository:

    def publish(self, story_id):
        ...
```

Tại sao?

`publish` là behavior của:

```text
Story
```

Không phải:

```text
Repository
```

Đúng hơn:

```python
story = repo.get(story_id)

story.publish()

repo.save(story)
```

---

# 23. Repository làm gì?

Repository chủ yếu xử lý:

```text
Aggregate
    ↕
Persistence
```

Ví dụ:

```text
get
add
save
remove
```

và các query cần thiết.

---

# 24. Repository không làm gì?

Không nên:

```text
Business validation
Business state transition
Domain policy
Business workflow
```

Ví dụ:

```python
repository.publish_story(...)
```

thường là dấu hiệu application/domain logic đang bị đẩy xuống persistence.

---

# 25. Flow chuẩn

Use Case:

```python
def execute(story_id):
    story = story_repository.get(story_id)

    story.publish()

    story_repository.save(story)
```

Ta có:

```text
Application
     ↓
Repository.get()
     ↓
Aggregate
     ↓
Domain behavior
     ↓
Repository.save()
```

---

# 26. Repository có nên thuộc Domain không?

Đây là một chủ đề có nhiều cách tổ chức.

Trong DDD + Clean Architecture, thường ta đặt abstraction ở phía trong:

```text
Domain
Application
```

và implementation ở:

```text
Infrastructure
```

Ví dụ:

```text
domain/
    repositories/
        story_repository.py

infrastructure/
    persistence/
        sqlite_story_repository.py
```

Hoặc nếu Repository chỉ phục vụ Application Use Case:

```text
application/
    ports/
        story_repository.py
```

Điều quan trọng hơn vị trí file là:

> **Dependency phải hướng vào abstraction, không hướng vào SQLite.**

---

# 27. Interface thuộc về ai?

Ví dụ:

```python
class StoryRepository(ABC):
    ...
```

Nếu Application cần:

```python
story_repository.get(...)
story_repository.save(...)
```

thì Application cần abstraction này.

Do đó có thể đặt:

```text
application/
    ports/
        story_repository.py
```

Nếu Repository là một domain concept mạnh, có thể đặt trong:

```text
domain/
    repositories/
```

Không nên đặt interface trong:

```text
infrastructure/sqlite/
```

rồi bắt Domain import ngược ra Infrastructure.

---

# 28. Sai Dependency

```text
domain
   ↓
infrastructure
   ↓
sqlite
```

Domain bị kéo vào Infrastructure.

---

# 29. Đúng Dependency

```text
           Domain
              ↑
        Application
              ↑
        Infrastructure
              │
            SQLite
```

Hoặc nhìn theo source dependency:

```text
Infrastructure
      ↓
Application abstraction
      ↓
Domain
```

Infrastructure phụ thuộc vào phía trong.

---

# 30. Repository và Aggregate Boundary

Repository cũng giúp chúng ta enforce Aggregate boundary.

Ví dụ:

```python
story = story_repo.get(story_id)
```

Bạn lấy:

```text
Story Aggregate
```

không lấy:

```text
Story + mọi Aggregate liên quan
```

Ví dụ không nên:

```python
story = repository.get(story_id)

story.crawler_job
story.user
story.reading_progress
story.chapters
```

nếu những object đó là Aggregate riêng.

---

# 31. Repository + Reference by ID

Ta đã thiết kế:

```python
class Chapter:
    story_id: StoryId
```

Khi load Chapter:

```python
chapter = chapter_repo.get(chapter_id)
```

Repository không cần load:

```text
Story
```

vào Chapter.

Đây chính là một lợi ích rất lớn của Aggregate boundary.

---

# 32. Ví dụ Domain

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: str
    title: str
    status: str

    def publish(self):
        if self.status == "archived":
            raise ValueError(
                "Archived story cannot be published"
            )

        self.status = "published"
```

Repository:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id: str) -> Story | None:
        ...

    @abstractmethod
    def save(self, story: Story) -> None:
        ...
```

---

# 33. In-memory Repository

Trước khi viết SQLite, hãy viết InMemory Repository.

Đây là kỹ thuật rất tốt để test.

```python
class InMemoryStoryRepository(StoryRepository):

    def __init__(self):
        self._stories = {}

    def get(self, story_id):
        return self._stories.get(story_id)

    def save(self, story):
        self._stories[story.id] = story
```

---

# 34. Application không quan tâm implementation

```python
repo = InMemoryStoryRepository()

story = Story(
    id="1",
    title="One Piece",
    status="draft",
)

repo.save(story)

story = repo.get("1")
story.publish()

repo.save(story)
```

Application không cần biết:

```text
InMemory
```

hay:

```text
SQLite
```

---

# 35. Đây là lý do Repository cực kỳ hữu ích cho Testing

Production:

```text
StoryRepository
      ↑
SQLiteStoryRepository
```

Test:

```text
StoryRepository
      ↑
InMemoryStoryRepository
```

Cùng abstraction.

---

# 36. Test Use Case

Ví dụ:

```python
def test_publish_story():
    repo = InMemoryStoryRepository()

    story = Story(
        id="1",
        title="One Piece",
        status="draft",
    )

    repo.save(story)

    use_case = PublishStory(repo)

    use_case.execute("1")

    saved = repo.get("1")

    assert saved.status == "published"
```

Không cần SQLite.

Không cần temporary database.

Test rất nhanh.

---

# 37. Application Service

```python
class PublishStory:

    def __init__(
        self,
        stories: StoryRepository,
    ):
        self.stories = stories

    def execute(self, story_id: str):
        story = self.stories.get(story_id)

        if story is None:
            raise StoryNotFound()

        story.publish()

        self.stories.save(story)
```

Dependency:

```text
PublishStory
      ↓
StoryRepository
```

không:

```text
PublishStory
      ↓
SQLiteStoryRepository
```

---

# 38. Dependency Injection

Ta có thể inject:

```python
use_case = PublishStory(
    stories=SQLiteStoryRepository(...)
)
```

Production.

Test:

```python
use_case = PublishStory(
    stories=InMemoryStoryRepository()
)
```

Đây chính là:

```text
Dependency Inversion
+
Dependency Injection
```

---

# 39. SQLite Repository sẽ làm gì?

Đến Buổi 23 chúng ta mới implement đầy đủ.

Nhưng concept:

```python
class SQLiteStoryRepository(StoryRepository):

    def __init__(self, connection):
        self._connection = connection

    def get(self, story_id):
        ...

    def save(self, story):
        ...
```

Repository sẽ:

```text
SQLite Row
   ↓
Domain Object
```

và:

```text
Domain Object
   ↓
SQLite Row
```

---

# 40. Mapping

Đây là một trách nhiệm quan trọng của Infrastructure.

Database:

```text
id
title
status
source_id
```

Domain:

```python
Story(
    id=StoryId(...),
    title=StoryTitle(...),
    status=StoryStatus(...),
    source_id=SourceId(...),
)
```

Repository thực hiện mapping.

---

# 41. Không để database row chảy vào Domain

Không nên:

```python
story = Story(**row)
```

nếu `row` là raw SQLite row và domain yêu cầu Value Object.

Tốt hơn:

```python
return Story(
    id=StoryId(row["id"]),
    title=StoryTitle(row["title"]),
    status=StoryStatus(row["status"]),
    source_id=SourceId(row["source_id"]),
)
```

Repository/mapper chuyển đổi:

```text
Persistence Model
       ↓
Domain Model
```

---

# 42. Repository và Transaction

Một điều rất quan trọng:

> Repository không nhất thiết tự `commit()`.

Ví dụ không nên:

```python
def save(self, story):
    self.connection.execute(...)
    self.connection.commit()
```

Nếu Repository tự commit thì rất khó phối hợp nhiều Repository.

---

# 43. Tại sao?

Giả sử:

```python
story_repo.save(story)
chapter_repo.save(chapter)
```

Nếu `story_repo.save()` tự commit:

```text
save story
 ↓
COMMIT

save chapter
 ↓
ERROR
```

Database đã commit Story nhưng Chapter thất bại.

Không atomic.

---

# 44. Vì vậy Repository thường không quản lý transaction boundary

Thay vào đó:

```text
Unit of Work
      ↓
BEGIN
      ↓
Repository 1
Repository 2
Repository 3
      ↓
COMMIT
```

Đây là lý do Buổi 24 sẽ học:

```text
Unit of Work
```

---

# 45. Repository + Unit of Work

Mental model:

```text
             Use Case
                 │
                 ↓
          Unit of Work
          ┌──────┴──────┐
          ↓             ↓
     StoryRepository  ChapterRepository
          ↓             ↓
          └──────┬──────┘
                 ↓
               SQLite
```

Transaction thuộc:

```text
Unit of Work
```

chứ không phải từng Repository riêng lẻ.

---

# 46. Repository API nên phản ánh Aggregate

Ví dụ:

```python
class ChapterRepository(ABC):

    @abstractmethod
    def get(self, chapter_id: ChapterId):
        ...

    @abstractmethod
    def add(self, chapter: Chapter):
        ...

    @abstractmethod
    def save(self, chapter: Chapter):
        ...
```

Không:

```python
save_chapter_content(...)
update_chapter_title(...)
set_chapter_status(...)
```

nếu đó là behavior của Chapter.

---

# 47. Repository vs Service

Một câu hỏi thường gặp:

> Nếu Repository có `get()` và `save()`, còn Service có business logic, vậy khác nhau thế nào?

### Repository

```text
Persistence
```

### Domain Service

```text
Domain logic không thuộc một Entity/Aggregate cụ thể
```

### Application Service

```text
Use-case orchestration
```

Ba thứ khác nhau.

---

# 48. Ví dụ

### Repository

```python
story_repo.get(story_id)
```

### Domain

```python
story.publish()
```

### Application Service

```python
story = repo.get(id)
story.publish()
repo.save(story)
```

Rất rõ ràng:

```text
Repository → data access
Domain → business behavior
Application → orchestration
```

---

# 49. Repository không phải Generic CRUD Repository

Bạn có thể thấy:

```python
class Repository[T]:
    def get(...)
    def add(...)
    def update(...)
    def delete(...)
```

và:

```python
GenericRepository[Story]
GenericRepository[Chapter]
```

Có thể dùng trong CRUD app.

Nhưng trong DDD, đừng quá nhanh chóng tạo:

```python
BaseRepository[T]
```

rồi ép mọi Aggregate vào cùng một CRUD API.

---

# 50. Vì sao?

Các Aggregate có nhu cầu khác nhau.

Ví dụ:

```text
StoryRepository
```

có thể cần:

```python
get_by_source(...)
```

trong khi:

```text
CrawlerJobRepository
```

có thể cần:

```python
get_running_jobs(...)
```

và:

```text
ReadingProgressRepository
```

có thể cần:

```python
get_for_user_and_story(...)
```

Domain khác nhau → Repository abstraction có thể khác nhau.

---

# 51. Repository không nhất thiết phải có `update()`

Một pattern rất đẹp:

```python
story = repo.get(id)

story.rename("New title")

repo.save(story)
```

Thay vì:

```python
repo.update_title(id, "New title")
```

Vì:

```text
rename()
```

là business behavior của Aggregate.

---

# 52. Repository cũng không nhất thiết có `create()`

Có thể:

```python
story = Story.create(...)
repo.add(story)
```

Domain factory:

```python
Story.create(...)
```

Repository:

```python
repo.add(...)
```

Responsibility rõ ràng.

---

# 53. Naming

Một convention tốt:

```python
story_repository.get(...)
story_repository.add(...)
story_repository.save(...)
story_repository.remove(...)
```

hoặc:

```python
get_by_id(...)
add(...)
save(...)
delete(...)
```

Điều quan trọng nhất là consistency.

---

# 54. Repository và Not Found

Một câu hỏi thiết kế:

```python
story = repo.get(id)
```

Nếu không tồn tại?

Có thể:

```python
return None
```

hoặc:

```python
raise StoryNotFound()
```

Không có một câu trả lời duy nhất.

Trong Application Layer, cách:

```python
story = repo.get(id)

if story is None:
    raise StoryNotFound(id)
```

thường rất rõ ràng.

---

# 55. Query Repository

Nếu cần màn hình:

```text
Dashboard
    ↓
Danh sách 1000 stories
```

có nên load 1000 Aggregate đầy đủ không?

Không nhất thiết.

Đây là lúc ta phân biệt:

```text
Repository
```

và:

```text
Query / Read Model
```

Ví dụ:

```python
StoryListItem(
    id=...,
    title=...,
    chapter_count=...,
)
```

Không nhất thiết phải:

```text
Story Aggregate × 1000
```

---

# 56. Đây là dấu hiệu CQRS bắt đầu xuất hiện

Write side:

```text
Aggregate
Repository
```

Read side:

```text
Query
Projection
DTO
```

Ví dụ:

```text
StoryRepository
```

dùng cho:

```text
Business operation
```

Còn:

```text
StoryListQuery
```

dùng cho:

```text
Dashboard
```

Không ép một Repository làm cả hai.

---

# 57. Repository và SQLite trong dự án của bạn

Kiến trúc dự kiến:

```text
src/
└── app/
    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── repository.py
    │   │
    │   └── chapter/
    │       ├── entities.py
    │       ├── value_objects.py
    │       └── repository.py
    │
    ├── application/
    │   └── use_cases/
    │
    └── infrastructure/
        └── sqlite/
            ├── story_repository.py
            └── chapter_repository.py
```

Đây sẽ là nền tảng rất tốt cho project crawler/reading của bạn.

---

# 58. Repository dependency graph

```text
                Application
                     │
                     ↓
             StoryRepository
                     ↑
                     │
        SQLiteStoryRepository
                     │
                     ↓
                  SQLite
```

Application chỉ biết:

```python
StoryRepository
```

Infrastructure biết:

```python
SQLiteStoryRepository
```

---

# 59. Một ví dụ hoàn chỉnh

Domain:

```python
class Story:

    def __init__(self, story_id, title):
        self.id = story_id
        self.title = title
        self.status = "draft"

    def publish(self):
        if self.status == "archived":
            raise DomainError(
                "Cannot publish archived story"
            )

        self.status = "published"
```

Repository:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id):
        ...

    @abstractmethod
    def save(self, story):
        ...
```

Use Case:

```python
class PublishStory:

    def __init__(self, stories):
        self.stories = stories

    def execute(self, story_id):
        story = self.stories.get(story_id)

        if story is None:
            raise StoryNotFound(story_id)

        story.publish()

        self.stories.save(story)
```

Infrastructure:

```python
class SQLiteStoryRepository(StoryRepository):

    def __init__(self, connection):
        self.connection = connection

    def get(self, story_id):
        ...

    def save(self, story):
        ...
```

Ta có:

```text
PublishStory
     ↓
StoryRepository
     ↑
SQLiteStoryRepository
     ↓
SQLite
```

---

# 60. Điều quan trọng nhất của Buổi 21

Đừng học Repository như:

> "Một class để viết SQL."

Đó là cách hiểu quá nông.

Hãy hiểu:

> **Repository là abstraction giúp Application làm việc với Aggregate như một collection mà không phụ thuộc persistence mechanism.**

Mental model:

```text
             Application
                  │
                  ↓
            Repository
                  │
                  ↓
             Aggregate
                  │
                  ↓
             Persistence
                  │
                  ↓
              SQLite
```

Và đặc biệt nhớ:

```text
Repository ≠ DAO
Repository ≠ Database
Repository ≠ Service
Repository ≠ Unit of Work
```

Mỗi thứ có responsibility riêng.

---

# Bài tập Buổi 21

## Bài 1 — Thiết kế Interface

Viết:

```python
class StoryRepository(ABC):
    ...
```

với các operation hợp lý cho:

```text
Story Aggregate
```

Không dùng:

```text
SQLite
SQL
sqlite3
```

trong interface.

---

## Bài 2 — InMemory Repository

Implement:

```python
class InMemoryStoryRepository(
    StoryRepository
):
    ...
```

và test:

```python
story = Story(...)

repo.add(story)

result = repo.get(story.id)

assert result == story
```

---

## Bài 3 — Phân biệt DAO và Repository

Cho hai API:

```python
dao.find_by_id(...)
dao.update_row(...)
dao.insert_row(...)
```

và:

```python
repository.get(...)
repository.save(...)
repository.add(...)
```

Hãy giải thích tại sao API thứ hai mang tư duy DDD hơn.

---

## Bài 4 — Thiết kế cho hệ thống đọc truyện

Hãy viết interface cho:

```text
StoryRepository
ChapterRepository
CrawlerJobRepository
ReadingProgressRepository
```

Nhưng **chưa implement SQLite**.

---

## Bài 5 — Câu hỏi quan trọng nhất

Giải thích tại sao đoạn code này có vấn đề:

```python
class SQLiteStoryRepository:

    def save(self, story):
        self.conn.execute(...)
        self.conn.commit()
```

Đặc biệt hãy liên hệ với Buổi 19:

```text
Aggregate
    ↓
Transaction Boundary
    ↓
Unit of Work
```

Nếu bạn hiểu được câu này, bạn đã sẵn sàng sang **Buổi 22 — Repository Interface + Dependency Inversion**, nơi chúng ta sẽ thiết kế interface thật sự cho project Python của bạn và quyết định **interface nên nằm ở Domain hay Application Layer**.
