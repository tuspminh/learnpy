# Python OOP Master — Buổi 38

# Repository Pattern

Hôm nay chúng ta học **Repository Pattern** — một Pattern cực kỳ quan trọng khi xây application có database.

Đặc biệt nó liên quan trực tiếp đến những thứ bạn đã học:

```text
SOLID
Clean Architecture
DDD
SQLite3
Repository Interface
CQRS
Story Crawler
```

Mục tiêu cuối buổi là bạn có thể thiết kế:

```text
Application
     ↓
Repository Interface
     ↓
SQLite Repository
```

thay vì:

```text
Application
     ↓
sqlite3
     ↓
SQL
```

---

# 1. Repository Pattern là gì?

Repository Pattern tạo ra một abstraction đại diện cho việc:

> **Truy cập và quản lý collection của Domain Entity mà không để Domain/Application phụ thuộc trực tiếp vào cách dữ liệu được lưu trữ.**

Nói đơn giản:

```text
Repository
    =
"cánh cửa" đi vào database
```

Ví dụ:

```python
story_repository.get_by_id(10)
```

Application không cần biết bên dưới là:

```text
SQLite
PostgreSQL
MySQL
MongoDB
API
Memory
```

---

# 2. Bài toán nếu không dùng Repository

Ví dụ Story Service:

```python
import sqlite3


class StoryService:

    def get_story(self, story_id):

        conn = sqlite3.connect("stories.db")

        cursor = conn.execute(
            """
            SELECT id, title, author
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        )

        row = cursor.fetchone()

        conn.close()

        return row
```

Code này chạy được.

Nhưng `StoryService` bây giờ biết:

```text
sqlite3
SQL
connection
cursor
table name
column name
```

Business/Application layer bị dính database.

---

# 3. Vấn đề lớn hơn

Sau này bạn muốn chuyển:

```text
SQLite
   ↓
PostgreSQL
```

phải sửa:

```python
StoryService
```

Hoặc muốn test:

```python
StoryService
```

thì phải có SQLite.

Đây là coupling.

---

# 4. Repository giải quyết

Ta tạo interface:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, story_id):
        pass

    @abstractmethod
    def save(self, story):
        pass
```

Application:

```python
class StoryService:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def get_story(self, story_id):
        return self.repository.get_by_id(
            story_id
        )
```

Bây giờ:

```text
StoryService
     ↓
StoryRepository
     ↑
     ├── SQLiteStoryRepository
     ├── PostgreSQLStoryRepository
     └── MemoryStoryRepository
```

---

# 5. Đây chính là DIP

Bạn đã học DIP ở Buổi 31.

Không tốt:

```text
StoryService
      ↓
SQLiteStoryRepository
```

Tốt:

```text
StoryService
      ↓
StoryRepository
      ↑
SQLiteStoryRepository
```

Application phụ thuộc abstraction.

Infrastructure implement abstraction.

---

# 6. Repository Interface

Ví dụ đầy đủ hơn:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, story_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def add(self, story):
        pass

    @abstractmethod
    def update(self, story):
        pass

    @abstractmethod
    def delete(self, story_id):
        pass
```

Đây là contract.

---

# 7. Entity

Ta có Domain Entity:

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int | None
    title: str
    author: str
```

Repository làm việc với:

```text
Story
```

chứ không nhất thiết trả về:

```text
sqlite3.Row
```

Đây là điểm rất quan trọng.

---

# 8. SQLite Repository

```python
import sqlite3


class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, story_id):

        cursor = self.connection.execute(
            """
            SELECT id, title, author
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
            author=row[2],
        )
```

Repository chuyển:

```text
Database Row
     ↓
Domain Entity
```

---

# 9. Mapping là gì?

Đây là một khái niệm rất quan trọng.

Database:

```text
stories
--------------------------------
id | title | author
10 | Python | Minh
```

Domain:

```python
Story(
    id=10,
    title="Python",
    author="Minh",
)
```

Repository thực hiện mapping:

```text
Persistence Model
        ↓
     Mapping
        ↓
Domain Model
```

---

# 10. Không nên để sqlite Row lan ra ngoài

Không tốt:

```python
row = cursor.fetchone()

return row
```

Sau đó Application:

```python
row["title"]
```

Bây giờ Application biết:

```text
sqlite3.Row
```

Domain bị rò rỉ persistence detail.

Tốt:

```python
return Story(
    id=row["id"],
    title=row["title"],
    author=row["author"],
)
```

---

# 11. Repository là abstraction của Persistence

Ta có:

```text
Application
    ↓
Repository
    ↓
Persistence
```

Repository che giấu:

```text
SQL
Connection
Cursor
Transaction
Table
Column
```

Application chỉ thấy:

```python
story = repository.get_by_id(10)
```

---

# 12. Memory Repository

Đây là nơi Repository Pattern trở nên cực kỳ hữu ích cho testing.

```python
class MemoryStoryRepository:

    def __init__(self):
        self._stories = {}

    def get_by_id(self, story_id):
        return self._stories.get(story_id)

    def add(self, story):
        self._stories[story.id] = story

    def delete(self, story_id):
        self._stories.pop(
            story_id,
            None,
        )
```

Test:

```python
repository = MemoryStoryRepository()

repository.add(
    Story(
        id=1,
        title="Python",
        author="Minh",
    )
)

story = repository.get_by_id(1)
```

Không cần SQLite.

---

# 13. Đây chính là Testability

Application:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository
```

Production:

```python
service = StoryService(
    SQLiteStoryRepository(connection)
)
```

Test:

```python
service = StoryService(
    MemoryStoryRepository()
)
```

Application không thay đổi.

---

# 14. Fake Repository

Có thể tạo Fake:

```python
class FakeStoryRepository:

    def __init__(self):
        self.saved = []

    def add(self, story):
        self.saved.append(story)

    def get_by_id(self, story_id):

        for story in self.saved:
            if story.id == story_id:
                return story

        return None
```

Test:

```python
repo = FakeStoryRepository()

service = StoryService(repo)

service.create_story(
    ...
)
```

Ta có thể kiểm tra:

```python
assert len(repo.saved) == 1
```

---

# 15. Repository + Unit Test

Ví dụ:

```python
def test_get_story():

    repository = MemoryStoryRepository()

    repository.add(
        Story(
            id=1,
            title="Python",
            author="Minh",
        )
    )

    service = StoryService(
        repository
    )

    story = service.get_story(1)

    assert story.title == "Python"
```

Test này không cần:

```text
SQLite
filesystem
database setup
SQL
```

Rất nhanh.

---

# 16. Repository có nên chứa Business Logic?

Đây là điểm rất quan trọng.

Repository nên tập trung vào:

```text
Persistence
Query
Save
Update
Delete
Mapping
```

Không nên chứa business rule như:

```python
if story.author == ...:
    ...
```

hoặc:

```python
if story.is_valid_for_publishing():
    ...
```

Business logic nên nằm ở:

```text
Domain
Application Service
```

tùy loại logic.

---

# 17. Repository vs Service

Rất dễ nhầm.

### Repository

```text
Lấy/lưu dữ liệu
```

Ví dụ:

```python
repository.get_by_id(10)
repository.save(story)
repository.delete(10)
```

### Service

```text
Điều phối business/use case
```

Ví dụ:

```python
service.publish_story(10)
```

Service có thể:

```text
1. lấy Story
2. kiểm tra rule
3. thay đổi state
4. save Story
5. phát Domain Event
```

---

# 18. Ví dụ Service

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository

    def publish(self, story_id):

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        story.publish()

        self.repository.save(story)
```

Repository:

```text
get
save
```

Service:

```text
business workflow
```

---

# 19. Repository vs DAO

Repository và DAO cũng dễ nhầm.

### DAO

Data Access Object.

Thường gần database:

```text
DAO
 ↓
SQL
 ↓
Table
```

Ví dụ:

```python
story_dao.find_by_id(10)
```

### Repository

Thường ở abstraction cao hơn:

```text
Repository
 ↓
Domain Entity
```

Ví dụ:

```python
story_repository.get_by_id(10)
```

Repository thường nói bằng ngôn ngữ domain hơn.

---

# 20. Repository vs ORM

Repository không phải ORM.

ORM:

```text
SQLAlchemy
Django ORM
```

là công nghệ persistence.

Repository:

```text
StoryRepository
```

là architectural abstraction.

Có thể dùng:

```text
Repository
   ↓
SQLAlchemy
```

hoặc:

```text
Repository
   ↓
sqlite3
```

hoặc:

```text
Repository
   ↓
PostgreSQL driver
```

---

# 21. Repository với SQLite raw SQL

Với project của bạn, hoàn toàn có thể:

```text
StoryRepository
       ↓
SQLiteStoryRepository
       ↓
sqlite3
       ↓
Raw SQL
```

Ví dụ:

```python
class SQLiteStoryRepository:

    def __init__(self, db):
        self.db = db

    def get_by_id(self, story_id):

        row = self.db.fetchone(
            """
            SELECT id, title, author
            FROM stories
            WHERE id = ?
            """,
            (story_id,),
        )

        if row is None:
            return None

        return Story(
            id=row["id"],
            title=row["title"],
            author=row["author"],
        )
```

Đây hoàn toàn hợp lý.

Không bắt buộc phải dùng ORM.

---

# 22. Database Manager

Bạn từng thiết kế kiến trúc:

```text
DatabaseManager
        ↓
Repository
```

Ví dụ:

```python
class DatabaseManager:

    def __init__(self, path):
        self.connection = sqlite3.connect(
            path
        )

    def execute(self, sql, params=()):
        return self.connection.execute(
            sql,
            params,
        )
```

Repository:

```python
class SQLiteStoryRepository:

    def __init__(self, db):
        self.db = db
```

Architecture:

```text
StoryService
     ↓
StoryRepository
     ↓
SQLiteStoryRepository
     ↓
DatabaseManager
     ↓
sqlite3
```

---

# 23. Connection không nên bị tạo tùy tiện

Không nên:

```python
class SQLiteStoryRepository:

    def get_by_id(self, story_id):

        conn = sqlite3.connect(
            "stories.db"
        )

        ...
```

Mỗi method tự tạo connection sẽ khó quản lý:

```text
transaction
lifecycle
testing
connection configuration
```

Tốt hơn:

```python
db = DatabaseManager(...)

repo = SQLiteStoryRepository(db)
```

Dependency được inject.

---

# 24. Transaction

Repository thường có liên quan đến transaction.

Ví dụ:

```python
def save(self, story):

    self.db.execute(
        """
        UPDATE stories
        SET title = ?, author = ?
        WHERE id = ?
        """,
        (
            story.title,
            story.author,
            story.id,
        ),
    )
```

Commit có thể được quản lý bởi:

```text
Unit of Work
DatabaseManager
Application Service
```

Không nên tùy tiện commit trong mọi method nếu một use case cần nhiều repository operation nằm trong cùng transaction.

Đây là nơi **Unit of Work** sau này trở nên quan trọng.

---

# 25. Repository + Unit of Work

Có thể có:

```text
Application
     ↓
UnitOfWork
 ┌───┴───────────┐
 ↓               ↓
StoryRepository ChapterRepository
```

Ví dụ:

```python
with unit_of_work:

    story = (
        unit_of_work.stories
        .get_by_id(1)
    )

    chapter = (
        unit_of_work.chapters
        .get_by_id(10)
    )

    ...
```

Nếu tất cả thành công:

```text
COMMIT
```

Nếu lỗi:

```text
ROLLBACK
```

Đây là hướng nâng cao.

---

# 26. Repository trong DDD

Trong DDD, Repository thường được dùng cho **Aggregate Root**.

Ví dụ:

```text
Story
 ├── Chapter
 ├── Chapter
 └── Chapter
```

Nếu `Story` là Aggregate Root:

```python
class StoryRepository:
    ...
```

Application có thể:

```python
story = repository.get_by_id(
    story_id
)
```

rồi thao tác trên Aggregate:

```python
story.add_chapter(chapter)
```

sau đó:

```python
repository.save(story)
```

---

# 27. Repository không phải CRUD bắt buộc

Đây là một lỗi phổ biến.

Nhiều người định nghĩa:

```python
create()
read()
update()
delete()
```

cho mọi Repository.

Không nhất thiết.

Repository nên phản ánh nhu cầu của domain/application.

Ví dụ:

```python
class StoryRepository:

    def get_by_id(self, story_id):
        ...

    def find_by_source(self, source):
        ...

    def find_published(self):
        ...

    def save(self, story):
        ...
```

Không nhất thiết phải có:

```python
update()
delete()
```

nếu domain không cần.

---

# 28. Query nên nằm ở Repository

Ví dụ:

```python
repository.find_published()
```

Repository xử lý:

```sql
SELECT ...
FROM stories
WHERE status = 'published'
```

Application không nên viết:

```python
repository.execute_sql(
    "SELECT ..."
)
```

Nếu Application bắt đầu viết SQL:

```text
Architecture abstraction bị phá vỡ.
```

---

# 29. Query Model và CQRS

Bạn đã học CQRS.

Trong CQRS, có thể tách:

```text
Command side
    ↓
Repository
```

và:

```text
Query side
    ↓
Read Model
```

Ví dụ:

```text
                  Application
                  /         \
                 ↓           ↓
            Command        Query
               ↓              ↓
          Repository      ReadModel
               ↓              ↓
            SQLite         SQLite
```

Read Model có thể trả về DTO thay vì Domain Entity.

---

# 30. Repository vs Read Model

Repository:

```python
story = repository.get_by_id(10)
```

thường lấy Domain Entity.

Read Model:

```python
story = story_list_query.get_story(10)
```

có thể trả:

```python
StoryListItemDTO(
    id=10,
    title="...",
    chapter_count=100,
)
```

Đây là hai mục đích khác nhau.

---

# 31. Story Crawler của bạn

Một architecture phù hợp:

```text
                    Application
                        │
                  StoryService
                        │
                        ↓
                StoryRepository
                        ↑
                        │
              SQLiteStoryRepository
                        │
                        ↓
                DatabaseManager
                        │
                        ↓
                     SQLite
```

Crawler:

```text
Crawler
   ↓
StoryService
   ↓
StoryRepository
   ↓
SQLite
```

Crawler không cần biết SQL.

---

# 32. Nhiều database theo source

Bạn từng muốn:

```text
stories_site_a.db
stories_site_b.db
stories_site_c.db
```

Có thể:

```text
DatabaseManager
       ↓
┌──────┼────────┐
↓      ↓        ↓
SiteA  SiteB    SiteC
 DB     DB       DB
```

Repository:

```text
SiteAStoryRepository
SiteBStoryRepository
SiteCStoryRepository
```

hoặc tốt hơn, nếu schema giống nhau:

```text
SQLiteStoryRepository
        ↑
        │
DatabaseManager(site_a.db)

SQLiteStoryRepository
        ↑
        │
DatabaseManager(site_b.db)
```

Cùng implementation, khác dependency.

---

# 33. Đây là DI

```python
db_a = DatabaseManager(
    "site_a.db"
)

repo_a = SQLiteStoryRepository(
    db_a
)
```

và:

```python
db_b = DatabaseManager(
    "site_b.db"
)

repo_b = SQLiteStoryRepository(
    db_b
)
```

Không cần:

```text
SiteARepository
SiteBRepository
SiteCRepository
```

nếu behavior persistence giống nhau.

---

# 34. Repository Factory

Có thể dùng Factory:

```python
class RepositoryFactory:

    @staticmethod
    def create_story_repository(
        source,
    ):

        db = DatabaseManager(
            f"{source}.db"
        )

        return SQLiteStoryRepository(db)
```

Sử dụng:

```python
repo = RepositoryFactory.create_story_repository(
    "site_a"
)
```

Kết hợp:

```text
Factory
   ↓
Repository
   ↓
Database
```

---

# 35. Repository + Strategy

Đây là chỗ cần phân biệt.

Không nên nói:

```text
SQLiteRepository = Strategy
```

Repository có nhiệm vụ:

> abstraction của persistence access.

Strategy có nhiệm vụ:

> thay thế algorithm/behavior.

Ví dụ:

```text
StoryRepository
    ↓
Persistence abstraction
```

Trong khi:

```text
RetryStrategy
    ↓
Algorithm
```

Hai khái niệm khác nhau.

---

# 36. Interface bằng Protocol

Python không bắt buộc dùng ABC.

Có thể:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get_by_id(
        self,
        story_id: int,
    ) -> Story | None:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

SQLite:

```python
class SQLiteStoryRepository:

    def get_by_id(self, story_id):
        ...

    def save(self, story):
        ...
```

Memory:

```python
class MemoryStoryRepository:

    def get_by_id(self, story_id):
        ...

    def save(self, story):
        ...
```

Không cần inheritance.

---

# 37. ABC hay Protocol?

| ABC                                | Protocol               |
| ---------------------------------- | ---------------------- |
| Explicit inheritance               | Structural typing      |
| Runtime abstraction mạnh hơn       | Pythonic               |
| Contract rõ                        | Flexible               |
| Phù hợp framework/domain interface | Rất tốt cho DI/testing |
| `class X(Repository)`              | Chỉ cần đúng method    |

Trong Python application hiện đại:

> **Protocol là lựa chọn rất đáng cân nhắc cho Repository Interface.**

---

# 38. Repository Generic

Khi hệ thống lớn, có thể tạo generic abstraction:

```python
from typing import Protocol, TypeVar, Generic


T = TypeVar("T")


class Repository(
    Protocol[T]
):

    def get_by_id(
        self,
        entity_id: int,
    ) -> T | None:
        ...

    def save(
        self,
        entity: T,
    ) -> None:
        ...
```

Sau đó:

```python
Repository[Story]
```

hoặc:

```python
Repository[User]
```

Tuy nhiên đừng generic hóa quá sớm.

Domain-specific repository thường dễ đọc hơn.

---

# 39. Generic Repository có phải luôn tốt?

Không.

Một interface:

```python
class GenericRepository:
    ...
```

đôi khi trở thành:

```text
get()
save()
delete()
find()
query()
```

nhưng không diễn đạt được domain.

DDD thường thích:

```python
StoryRepository
UserRepository
OrderRepository
```

hơn là một GenericRepository khổng lồ.

---

# 40. Một Repository tốt

Ví dụ:

```python
class StoryRepository(Protocol):

    def get_by_id(
        self,
        story_id: int,
    ) -> Story | None:
        ...

    def find_by_source(
        self,
        source: str,
    ) -> list[Story]:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Tên method nói bằng ngôn ngữ domain.

Đây là điểm quan trọng.

---

# 41. Anti-pattern: Repository trả SQL

Không nên:

```python
repo.query(
    """
    SELECT *
    FROM stories
    """
)
```

rồi Application tự xử lý.

Điều đó làm Repository trở thành:

```text
SQL wrapper
```

thay vì:

```text
Domain persistence abstraction
```

---

# 42. Anti-pattern: Repository chứa tất cả logic

Không nên:

```python
class StoryRepository:

    def publish_story(self):
        ...

    def calculate_rating(self):
        ...

    def send_notification(self):
        ...

    def crawl_story(self):
        ...
```

Repository đang làm quá nhiều việc.

Repository:

```text
Persistence
```

Application/Domain:

```text
Business logic
```

---

# 43. Luồng chuẩn

Một use case:

```text
User
 ↓
Controller / CLI / GUI
 ↓
Application Service
 ↓
Repository
 ↓
Database
```

Ví dụ:

```text
PySide6
   ↓
PublishStoryCommand
   ↓
StoryService
   ↓
StoryRepository
   ↓
SQLite
```

Đây là nơi Command Pattern của Buổi 37 kết hợp rất đẹp với Repository.

---

# 44. Command + Repository

Ví dụ:

```python
class DeleteStoryCommand:

    def __init__(
        self,
        service,
        story_id,
    ):
        self.service = service
        self.story_id = story_id

    def execute(self):
        self.service.delete_story(
            self.story_id
        )
```

Service:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository

    def delete_story(self, story_id):

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        self.repository.delete(
            story_id
        )
```

Flow:

```text
UI
 ↓
Command
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

---

# 45. Observer + Repository

Sau khi save:

```text
StoryService
     ↓
Repository.save()
     ↓
StorySaved Event
     ↓
Observer
 ├── Dashboard
 ├── Logger
 └── Metrics
```

Bây giờ ba Pattern:

```text
Command
Repository
Observer
```

đã bắt đầu ghép thành một architecture thực tế.

---

# 46. Architecture tổng hợp

```text
                         PySide6
                            │
                            ↓
                         Command
                            │
                            ↓
                    Application Service
                            │
             ┌──────────────┴──────────────┐
             ↓                             ↓
       Repository                      Domain
             │                             │
             ↓                             ↓
          SQLite                       Domain Event
                                           │
                                           ↓
                                      Observer
                                           │
                              ┌────────────┼────────────┐
                              ↓            ↓            ↓
                          Dashboard      Logger       Metrics
```

Đây chính là hướng kiến trúc rất phù hợp cho Story Crawler/Reader của bạn.

---

# 47. Khi nào Repository Pattern đáng dùng?

Nên dùng khi:

```text
Database phức tạp
      ↓
nhiều use case
      ↓
cần testing
      ↓
Clean Architecture
      ↓
DDD
      ↓
nhiều persistence implementation
```

Đặc biệt:

```text
SQLite
PostgreSQL
Memory Fake
```

cần thay thế cho nhau.

---

# 48. Khi nào KHÔNG cần Repository?

Một script cực nhỏ:

```python
import sqlite3

conn = sqlite3.connect("app.db")

rows = conn.execute(
    "SELECT * FROM users"
).fetchall()
```

Nếu chỉ có:

```text
100 dòng script
```

thì Repository có thể là overengineering.

Đừng tạo:

```text
Entity
Repository
Service
Factory
UnitOfWork
CQRS
```

cho một script đơn giản.

---

# 49. Repository Pattern và OOP

Repository là ví dụ rất rõ của:

```text
Abstraction
Encapsulation
Polymorphism
Dependency Injection
Composition
```

Ví dụ:

```text
StoryService
      ↓
StoryRepository
      ↑
 ┌────┴─────┐
 ↓          ↓
SQLite     Memory
```

Đây chính là polymorphism.

---

# 50. Bài tập 1 — Basic Repository

Tạo:

```text
User
UserRepository
MemoryUserRepository
```

Interface:

```python
get_by_id()
save()
delete()
```

Test toàn bộ bằng Memory Repository.

---

# 51. Bài tập 2 — SQLite Repository

Tạo:

```text
Story
StoryRepository
SQLiteStoryRepository
DatabaseManager
```

Database:

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT
);
```

Implement:

```text
get_by_id()
get_all()
save()
delete()
```

---

# 52. Bài tập 3 — Mapping ⭐

Không được trả:

```python
sqlite3.Row
```

Repository phải trả:

```python
Story
```

Kiểm tra:

```python
story = repo.get_by_id(1)

assert isinstance(
    story,
    Story,
)
```

---

# 53. Bài tập 4 — Dependency Injection ⭐

Tạo:

```python
class StoryService:
    def __init__(self, repository):
        ...
```

Sau đó chạy cùng Service với:

```text
MemoryStoryRepository
SQLiteStoryRepository
```

Không sửa `StoryService`.

---

# 54. Bài tập 5 — Crawler Architecture ⭐⭐⭐

Thiết kế:

```text
Crawler
   ↓
StoryService
   ↓
StoryRepository
   ↓
SQLite
```

Crawler không được chứa:

```text
sqlite3.connect()
SELECT
INSERT
UPDATE
DELETE
```

Tất cả persistence logic phải nằm dưới Repository.

---

# 55. Bài tập 6 — Tổng hợp ⭐⭐⭐⭐

Kết hợp các Pattern đã học:

```text
Factory
Builder
Strategy
Observer
Command
Repository
```

Architecture:

```text
                         PySide6
                            │
                            ↓
                         Command
                            │
                            ↓
                    Application Service
                            │
           ┌────────────────┼────────────────┐
           ↓                ↓                ↓
       Parser           Retry            Repository
       Strategy         Strategy              │
                                              ↓
                                            SQLite
                            │
                            ↓
                           Event
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
          Dashboard       Logger        Metrics
```

Đây là một bài tập tổng hợp rất gần production architecture.

---

# 56. Tổng kết Buổi 38

Repository Pattern:

> **Tách logic truy cập persistence khỏi application/domain logic bằng một abstraction.**

Công thức:

```text
Application
     ↓
Repository Interface
     ↓
Infrastructure Repository
     ↓
Database
```

Ví dụ:

```text
StoryService
     ↓
StoryRepository
     ↑
SQLiteStoryRepository
     ↓
sqlite3
```

---

# 57. Sáu Pattern đã học

| Buổi   | Pattern        | Câu hỏi                                                     |
| ------ | -------------- | ----------------------------------------------------------- |
| 32     | Singleton      | Có bao nhiêu instance?                                      |
| 33     | Factory        | Tạo object nào?                                             |
| 34     | Builder        | Xây object thế nào?                                         |
| 35     | Strategy       | Dùng algorithm nào?                                         |
| 36     | Observer       | Ai cần biết event?                                          |
| 37     | Command        | Thực hiện action nào?                                       |
| **38** | **Repository** | **Lưu/lấy dữ liệu thế nào mà không phụ thuộc persistence?** |

Có thể nhớ:

```text
Singleton  → Instance
Factory    → Creation
Builder    → Construction
Strategy   → Behavior
Observer   → Notification
Command    → Action
Repository → Persistence
```

---

# 58. Kiến trúc chúng ta đang tiến tới

Sau 38 buổi, các mảnh ghép bắt đầu kết nối:

```text
                         UI / CLI
                            │
                            ↓
                         Command
                            │
                            ↓
                    Application Service
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          Strategy       Repository      Domain
             │              │              │
             │              ↓              ↓
             │           SQLite          Events
             │                             │
             └──────────────┬──────────────┘
                            ↓
                        Observer
                            │
                  ┌─────────┼─────────┐
                  ↓         ↓         ↓
               Logger    Dashboard  Metrics
```

Đây không còn chỉ là học từng Pattern riêng lẻ nữa — chúng ta đang học cách **kết hợp Pattern để xây architecture**.

## Tiếp theo — Buổi 39

**Project 1 — Library Management System**

Chúng ta sẽ bắt đầu project thực chiến và sử dụng những Pattern đã học:

```text
Entity
Repository
Service
Factory
Builder
Strategy
Command
Observer
DI
```

để xây một **Library Management System** theo hướng gần với **Clean Architecture + SOLID + DDD**.
