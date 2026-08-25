# DDD Deep Dive — Buổi 22

# Repository Interface + Dependency Inversion

Buổi 21 chúng ta đã hiểu:

```text
Repository
    ↓
Aggregate
    ↓
Persistence
```

Hôm nay đi sâu hơn vào câu hỏi quan trọng:

> **Repository Interface nằm ở đâu và ai được phép phụ thuộc vào ai?**

Đây chính là nơi **DDD + Clean Architecture + SOLID/DIP** gặp nhau.

---

# 1. Bài toán

Giả sử chúng ta có:

```text
Story
StoryRepository
SQLiteStoryRepository
```

Một người mới học rất dễ viết:

```python
class StoryService:

    def __init__(self):
        self.repo = SQLiteStoryRepository()
```

Nhìn đơn giản nhưng kiến trúc đã có vấn đề.

Dependency:

```text
StoryService
      ↓
SQLiteStoryRepository
      ↓
sqlite3
```

Application đã biết Infrastructure.

---

# 2. Vấn đề nằm ở đâu?

`StoryService` đang cần:

> "Một nơi có thể lưu và lấy Story."

Nhưng code lại yêu cầu:

> "Tôi cần SQLiteStoryRepository."

Đây là hai yêu cầu hoàn toàn khác nhau.

Application cần **abstraction**.

Không cần biết implementation.

---

# 3. Dependency Inversion

Ta muốn:

```text
Application
     ↓
StoryRepository
     ↑
SQLiteStoryRepository
```

Trong đó:

```text
StoryRepository
```

là abstraction.

`SQLiteStoryRepository` phụ thuộc vào abstraction.

---

# 4. Interface

Python không có `interface` keyword giống Java/C#.

Ta thường dùng:

```python
from abc import ABC, abstractmethod
```

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
```

Đây là **Repository Interface**.

---

# 5. Interface không phải Implementation

Interface:

```python
class StoryRepository(ABC):
    ...
```

Không biết:

```text
SQLite
PostgreSQL
Redis
HTTP API
File
Memory
```

Implementation:

```python
class SQLiteStoryRepository(StoryRepository):
    ...
```

biết SQLite.

---

# 6. Dependency Graph

Ta có:

```text
                StoryRepository
                 ▲          ▲
                 │          │
                 │          │
     SQLiteStoryRepository   │
                            │
                  InMemoryStoryRepository
```

Application:

```text
PublishStory
      ↓
StoryRepository
```

Infrastructure:

```text
SQLiteStoryRepository
      ↓
SQLite
```

---

# 7. Dependency Inversion Principle

DIP có hai ý quan trọng.

### High-level module không nên phụ thuộc low-level module.

Thay vì:

```text
Application
    ↓
SQLite
```

ta có:

```text
Application
    ↓
Abstraction
    ↑
SQLite
```

### Abstraction không phụ thuộc detail.

```text
StoryRepository
```

không biết:

```text
SQLite
```

Trong khi:

```text
SQLiteStoryRepository
```

phụ thuộc:

```text
StoryRepository
```

---

# 8. Interface thuộc về phía cần nó

Đây là nguyên tắc rất quan trọng:

> **Abstraction nên nằm gần code sử dụng abstraction đó.**

Application cần:

```python
StoryRepository
```

vì vậy có thể đặt:

```text
application/
    ports/
        story_repository.py
```

hoặc nếu Repository được xem là một phần của domain contract:

```text
domain/
    repositories/
        story_repository.py
```

---

# 9. Đừng đặt interface ở Infrastructure

Một cấu trúc không tốt:

```text
infrastructure/
    repositories/
        story_repository.py
        sqlite_story_repository.py
```

rồi:

```text
application
      ↓
infrastructure.story_repository
```

Khi đó Application đang phụ thuộc Infrastructure.

Sai dependency direction.

---

# 10. Cấu trúc tốt

Ví dụ:

```text
src/
└── app/
    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   └── value_objects.py
    │   │
    │   └── ...
    │
    ├── application/
    │   ├── ports/
    │   │   └── story_repository.py
    │   │
    │   └── use_cases/
    │       └── publish_story.py
    │
    └── infrastructure/
        └── persistence/
            └── sqlite/
                └── story_repository.py
```

Dependency:

```text
infrastructure
      ↓
application
      ↓
domain
```

---

# 11. Nhưng có một tranh luận quan trọng

Trong DDD, bạn sẽ gặp hai cách phổ biến.

### Cách 1

Repository interface nằm trong:

```text
domain/
    repositories/
```

### Cách 2

Repository interface nằm trong:

```text
application/
    ports/
```

Cả hai đều có thể hợp lý.

Đừng biến vị trí file thành "giáo điều".

Điều quan trọng là:

```text
Domain/Application
        ↓
    abstraction
        ↑
Infrastructure
```

---

# 12. Khi nào đặt trong Domain?

Nếu Repository là một phần của domain model contract:

```text
StoryRepository
ChapterRepository
```

và Domain thực sự cần khái niệm này, có thể:

```text
domain/
    repositories/
        story_repository.py
```

Ví dụ:

```python
class StoryRepository(ABC):
    ...
```

---

# 13. Khi nào đặt trong Application?

Nếu Repository chỉ là dependency của Use Case:

```text
PublishStory
CreateChapter
UpdateReadingProgress
```

thì:

```text
application/
    ports/
        story_repository.py
```

rất hợp lý.

Application nói:

> "Use Case này cần một object có khả năng load/save Story."

---

# 14. Với project đọc truyện của bạn

Tôi đề xuất cấu trúc:

```text
src/
└── novel_app/
    ├── domain/
    │   ├── story/
    │   ├── chapter/
    │   ├── crawler/
    │   └── reading/
    │
    ├── application/
    │   ├── ports/
    │   │   ├── story_repository.py
    │   │   ├── chapter_repository.py
    │   │   ├── crawler_job_repository.py
    │   │   └── reading_progress_repository.py
    │   │
    │   └── use_cases/
    │
    └── infrastructure/
        └── persistence/
            └── sqlite/
```

Lý do:

```text
Domain
    = business rules

Application
    = use cases + required ports

Infrastructure
    = implementation
```

Rất hợp với Clean Architecture.

---

# 15. Repository Interface

Ví dụ:

```python
from abc import ABC, abstractmethod


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

---

# 16. Type rõ ràng

DDD + Python nên tận dụng type hints.

Ví dụ:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    @abstractmethod
    def add(
        self,
        story: Story,
    ) -> None:
        ...

    @abstractmethod
    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Interface lúc này trở thành contract rất rõ.

---

# 17. `ABC` không phải điều quan trọng nhất

Bạn có thể dùng:

```python
class StoryRepository(Protocol):
    ...
```

thay vì:

```python
class StoryRepository(ABC):
    ...
```

Đây là một chủ đề rất đáng học trong Python.

---

# 18. `Protocol`

Python hỗ trợ structural typing:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Implementation không nhất thiết phải:

```python
class SQLiteStoryRepository(StoryRepository):
```

miễn là nó có đúng interface.

---

# 19. Structural Typing

Ví dụ:

```python
class InMemoryStoryRepository:

    def get(self, story_id):
        ...

    def save(self, story):
        ...
```

Application:

```python
class PublishStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository
```

Python type checker có thể hiểu:

```text
InMemoryStoryRepository
        ↓
matches
        ↓
StoryRepository Protocol
```

Đây là phong cách rất Pythonic.

---

# 20. ABC vs Protocol

### ABC

```python
class StoryRepository(ABC):
```

Mang tính:

```text
Nominal interface
```

Implementation thường khai báo:

```python
class SQLiteStoryRepository(
    StoryRepository
):
```

### Protocol

```python
class StoryRepository(Protocol):
```

Mang tính:

```text
Structural interface
```

Không cần kế thừa.

---

# 21. DDD project Python nên chọn cái nào?

Cả hai đều được.

Nếu muốn:

```text
Explicit contract
Strict inheritance
Runtime enforcement
```

có thể dùng `ABC`.

Nếu muốn:

```text
Pythonic
Structural typing
Loose coupling
```

có thể dùng `Protocol`.

Với project Python hiện đại, tôi thường ưu tiên:

```python
Protocol
```

cho các port/interface.

---

# 22. Ví dụ với Protocol

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

# 23. Use Case

```python
class PublishStory:

    def __init__(
        self,
        stories: StoryRepository,
    ):
        self.stories = stories

    def execute(self, story_id: StoryId):
        story = self.stories.get(story_id)

        if story is None:
            raise StoryNotFound(story_id)

        story.publish()

        self.stories.save(story)
```

Điểm quan trọng:

`PublishStory` không biết:

```text
SQLite
```

---

# 24. Dependency Injection

Production:

```python
repository = SQLiteStoryRepository(
    connection
)

use_case = PublishStory(repository)
```

Test:

```python
repository = InMemoryStoryRepository()

use_case = PublishStory(repository)
```

Cùng Use Case.

---

# 25. Đây là DIP + DI

Hai khái niệm khác nhau.

### Dependency Inversion

Quyết định kiến trúc:

```text
High-level
    ↓
Abstraction
    ↑
Low-level
```

### Dependency Injection

Cách cung cấp dependency:

```python
use_case = PublishStory(repository)
```

Thay vì:

```python
class PublishStory:

    def __init__(self):
        self.repository = SQLiteStoryRepository()
```

---

# 26. Constructor Injection

Đây là cách tôi khuyến nghị.

```python
class PublishStory:

    def __init__(
        self,
        stories: StoryRepository,
    ):
        self.stories = stories
```

Dependency nhìn thấy rõ ngay trong constructor.

---

# 27. Tránh Service Locator

Không nên:

```python
repository = Container.resolve(
    StoryRepository
)
```

rồi bên trong Use Case:

```python
class PublishStory:

    def execute(self, story_id):
        repo = Container.resolve(...)
```

Dependency bị ẩn.

Constructor Injection tốt hơn:

```python
PublishStory(repository)
```

---

# 28. Repository Interface không chứa SQLite

Interface:

```python
class StoryRepository(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Không:

```python
import sqlite3
```

Không:

```python
sqlite3.Connection
```

Không:

```python
cursor
```

Không:

```python
SQL string
```

---

# 29. Infrastructure Implementation

```python
class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...
```

Infrastructure biết:

```text
sqlite3
SQL
connection
cursor
row
```

Application không biết.

---

# 30. Mapping

Đây là nơi Repository trở nên quan trọng.

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

Repository mapping:

```text
SQLite Row
    ↓
Mapper
    ↓
Story
```

---

# 31. Đừng để SQLite Row leak

Không:

```python
class StoryRepository:

    def get(self, story_id):
        return cursor.fetchone()
```

Application sẽ nhận:

```text
sqlite3.Row
```

Domain architecture bị phá vỡ.

Đúng:

```python
row = cursor.fetchone()

if row is None:
    return None

return Story(
    id=StoryId(row["id"]),
    title=StoryTitle(row["title"]),
    status=StoryStatus(row["status"]),
    source_id=SourceId(row["source_id"]),
)
```

---

# 32. Repository Interface và Domain Object

Repository trả:

```python
Story
```

không trả:

```python
StoryDTO
```

không trả:

```python
sqlite3.Row
```

không trả:

```python
dict
```

Nếu đây là Repository dành cho Aggregate.

---

# 33. Nhưng Query thì khác

Nếu bạn cần:

```text
Dashboard
```

và muốn:

```text
title
chapter_count
last_updated
```

không nhất thiết load Aggregate.

Có thể tạo:

```python
@dataclass
class StoryListItem:
    id: StoryId
    title: str
    chapter_count: int
    last_updated: datetime
```

Đây là:

```text
Read Model / DTO
```

không phải Aggregate.

---

# 34. Repository chỉ nên quản lý Aggregate

Một nguyên tắc rất hữu ích:

```text
Repository
    ↓
Aggregate Root
```

Ví dụ:

```python
StoryRepository
    ↓
Story

ChapterRepository
    ↓
Chapter

CrawlerJobRepository
    ↓
CrawlerJob
```

---

# 35. Interface cho Chapter

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

Chapter là Aggregate Root trong thiết kế Buổi 20.

---

# 36. Interface cho ReadingProgress

```python
class ReadingProgressRepository(Protocol):

    def get(
        self,
        user_id: UserId,
        story_id: StoryId,
    ) -> ReadingProgress | None:
        ...

    def save(
        self,
        progress: ReadingProgress,
    ) -> None:
        ...
```

Notice điều thú vị:

Repository không nhất thiết phải có API CRUD giống nhau.

---

# 37. Repository API nên phản ánh Domain

Ví dụ ReadingProgress có unique:

```text
User + Story
```

thì:

```python
get(user_id, story_id)
```

tự nhiên hơn:

```python
get(progress_id)
```

Nếu business identity của Progress thực sự là:

```text
(user_id, story_id)
```

thì Repository nên thể hiện điều đó.

---

# 38. Đừng ép tất cả Repository cùng Interface

Không nên:

```python
class BaseRepository[T]:
    ...
```

rồi ép:

```text
StoryRepository
ChapterRepository
UserRepository
ReadingProgressRepository
```

phải giống hệt nhau nếu domain của chúng khác nhau.

DDD ưu tiên:

```text
Domain meaning
```

hơn:

```text
Generic abstraction
```

---

# 39. Interface Segregation

Liên hệ SOLID — ISP.

Một Use Case chỉ cần:

```python
get()
save()
```

thì không nên bị ép phụ thuộc:

```python
get()
save()
delete()
search()
paginate()
export()
bulk_update()
...
```

Đây là lý do interface nhỏ thường tốt hơn.

---

# 40. Ví dụ xấu

```python
class Repository(Protocol):

    def get(self, id): ...
    def save(self, entity): ...
    def delete(self, entity): ...
    def search(self, query): ...
    def paginate(self, page): ...
    def export(self): ...
```

Một Use Case chỉ cần:

```text
get
save
```

nhưng lại phụ thuộc cả đống API.

---

# 41. Ví dụ tốt

```python
class StoryReader(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...
```

và:

```python
class StoryWriter(Protocol):

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Hoặc gộp nếu use case thực sự cần cả hai.

---

# 42. Interface thuộc Use Case

Ví dụ:

```text
PublishStory
```

cần:

```text
get
save
```

ta có thể tạo:

```python
class StoryRepository(Protocol):
    def get(...): ...
    def save(...): ...
```

Đây là interface tối thiểu cần thiết.

---

# 43. Composition Root

Một khái niệm rất quan trọng tiếp theo:

> **Ở đâu chúng ta nối abstraction với implementation?**

Ví dụ:

```text
Application
    ↓
StoryRepository
```

và:

```text
SQLiteStoryRepository
```

Ở đâu chúng ta nối chúng?

Tại:

```text
Composition Root
```

---

# 44. Composition Root

Ví dụ CLI:

```python
def main():
    connection = create_connection()

    story_repo = SQLiteStoryRepository(
        connection
    )

    use_case = PublishStory(
        story_repo
    )

    use_case.execute(story_id)
```

Đây là nơi biết cả:

```text
Application
+
Infrastructure
```

---

# 45. Domain không làm composition

Không:

```python
class Story:
    def __init__(self):
        self.repository = SQLiteStoryRepository()
```

Không.

Domain không được biết Infrastructure.

---

# 46. Application cũng không tự tạo Infrastructure

Không:

```python
class PublishStory:

    def __init__(self):
        self.repo = SQLiteStoryRepository()
```

Application đang quyết định implementation.

Không tốt.

---

# 47. Composition Root quyết định

```text
CLI
 ↓
create SQLite
 ↓
create SQLiteStoryRepository
 ↓
inject into PublishStory
```

Hoặc GUI:

```text
PySide6
 ↓
create dependencies
 ↓
inject Use Cases
```

Hoặc test:

```text
Test
 ↓
create InMemoryRepository
 ↓
inject Use Case
```

---

# 48. Đây là Dependency Direction hoàn chỉnh

```text
                 ┌─────────────┐
                 │   Domain    │
                 └──────▲──────┘
                        │
                 ┌──────┴──────┐
                 │ Application │
                 └──────▲──────┘
                        │
                 ┌──────┴──────┐
                 │Infrastructure│
                 └─────────────┘
```

Dependency source code hướng vào trong.

---

# 49. Với project của bạn

Ta có:

```text
CLI
PySide6
    │
    ↓
Application Use Cases
    │
    ↓
Repository Protocol
    ↑
    │
SQLite Repository
    │
    ↓
SQLite
```

Đây chính là kiến trúc mà chúng ta sẽ dùng để phát triển app đọc truyện.

---

# 50. Repository và Test

Production:

```python
repo = SQLiteStoryRepository(connection)
```

Test:

```python
repo = InMemoryStoryRepository()
```

Use Case không thay đổi:

```python
use_case = PublishStory(repo)
```

Đây là một trong những lợi ích lớn nhất của DIP.

---

# 51. Test mà không SQLite

```python
def test_publish_story():
    repo = InMemoryStoryRepository()

    story = Story(
        id=StoryId("story-1"),
        title=StoryTitle("One Piece"),
        status=StoryStatus.DRAFT,
    )

    repo.add(story)

    use_case = PublishStory(repo)

    use_case.execute(story.id)

    result = repo.get(story.id)

    assert result.status == StoryStatus.PUBLISHED
```

Test:

```text
Domain
+
Application
```

không cần:

```text
SQLite
File
Network
```

---

# 52. Một lỗi thiết kế thường gặp

Đừng làm:

```python
class StoryRepository(Protocol):

    def get(
        self,
        story_id: StoryId,
    ) -> Story:
        ...

    def save(
        self,
        story: Story,
    ) -> None:
        ...

    def execute_sql(
        self,
        sql: str,
    ):
        ...
```

Nếu có:

```python
execute_sql()
```

thì abstraction đã leak persistence detail.

---

# 53. Một lỗi khác

Đừng làm:

```python
class StoryRepository(Protocol):

    def save(
        self,
        story: Story,
        connection: sqlite3.Connection,
    ):
        ...
```

Interface bây giờ đã biết SQLite.

Sai.

---

# 54. Transaction sẽ xử lý ở Buổi 24

Interface hiện tại:

```python
class StoryRepository(Protocol):

    def get(...): ...
    def save(...): ...
```

Không cần:

```python
commit()
rollback()
```

trong từng Repository.

Buổi 24 chúng ta sẽ đưa transaction lên:

```text
Unit of Work
```

---

# 55. Repository + UoW

Sau này sẽ có:

```python
with uow:
    story = uow.stories.get(story_id)

    story.publish()

    uow.stories.save(story)

    uow.commit()
```

Architecture:

```text
Application
      ↓
UnitOfWork
      ↓
Repository
      ↓
SQLite
```

---

# 56. Một vấn đề tinh tế: Repository có nên expose query?

Ví dụ:

```python
get_by_title(...)
```

Có thể có.

Nhưng phải hỏi:

> Use Case thực sự cần query này không?

Ví dụ:

```python
CreateStory
```

cần kiểm tra title trùng:

```python
repository.exists_by_title(title)
```

thì abstraction có thể cung cấp:

```python
def exists_by_title(
    self,
    title: StoryTitle,
) -> bool:
    ...
```

Điều này vẫn domain-oriented.

---

# 57. Không phải mọi query đều phải trả Aggregate

Ví dụ:

```python
exists_by_title(...)
```

chỉ trả:

```text
bool
```

Hoàn toàn hợp lý.

Repository abstraction không phải lúc nào cũng:

```text
get Aggregate
```

nhưng các API của nó vẫn nên phục vụ domain/application.

---

# 58. Domain-oriented Query

Ví dụ:

```python
story_repository.exists(
    StoryId(...)
)
```

hoặc:

```python
story_repository.exists_with_title(
    StoryTitle(...)
)
```

Tốt hơn:

```python
story_repository.execute_sql(
    "SELECT ..."
)
```

---

# 59. Quy tắc vàng

Khi thiết kế Repository Interface, hãy hỏi:

> **Nếu ngày mai tôi thay SQLite bằng PostgreSQL, interface này có cần thay đổi không?**

Nếu:

```text
YES
```

có khả năng abstraction đang leak infrastructure.

Ví dụ xấu:

```python
save(
    story,
    sqlite_connection
)
```

Ví dụ tốt:

```python
save(story)
```

---

# 60. Một câu hỏi khó hơn

> Nếu ngày mai thay SQLite bằng HTTP API thì sao?

Ví dụ:

```text
RemoteStoryRepository
```

```python
class RemoteStoryRepository:

    def get(self, story_id):
        response = requests.get(...)

    def save(self, story):
        requests.put(...)
```

Application vẫn:

```python
story = repo.get(id)
story.publish()
repo.save(story)
```

Nếu Application không cần thay đổi thì abstraction tốt.

---

# 61. Đây chính là Persistence Ignorance

Application không biết:

```text
SQLite
PostgreSQL
HTTP
Memory
```

Domain cũng không biết.

Chỉ Composition Root biết:

```text
"Trong môi trường này chúng ta dùng SQLite."
```

---

# 62. Tổng kết Buổi 22

Chúng ta đã xây dựng:

```text
                    ┌─────────────┐
                    │   Domain    │
                    └──────▲──────┘
                           │
                    ┌──────┴──────┐
                    │ Application │
                    │             │
                    │ Repository  │
                    │ Interface   │
                    └──────▲──────┘
                           │
                    ┌──────┴──────────┐
                    │ Infrastructure  │
                    │                 │
                    │ SQLiteRepository│
                    └──────┬──────────┘
                           │
                         SQLite
```

Điểm cốt lõi:

```text
Application
     ↓
Abstraction
     ↑
Infrastructure
```

---

# 63. Checklist thiết kế Repository Interface

Trước khi viết interface, kiểm tra:

```text
□ Không import sqlite3
□ Không chứa SQL
□ Không chứa Connection
□ Không chứa Cursor
□ Không trả sqlite3.Row
□ Không chứa business logic
□ API hướng về Aggregate
□ Interface đủ nhỏ
□ Use Case phụ thuộc abstraction
□ Implementation phụ thuộc abstraction
□ Transaction không bị khóa vào Repository
```

---

# 64. Bài tập Buổi 22

### Bài 1

Viết:

```python
class StoryRepository(Protocol):
    ...
```

cho:

```text
Story Aggregate
```

---

### Bài 2

Viết:

```python
class ChapterRepository(Protocol):
    ...
```

cho:

```text
Chapter Aggregate
```

---

### Bài 3

Viết Use Case:

```python
class PublishStory:
    ...
```

với dependency:

```python
StoryRepository
```

**Không được import `sqlite3`.**

---

### Bài 4 — phát hiện Dependency Inversion violation

Đoạn code:

```python
class PublishStory:

    def __init__(self):
        self.repo = SQLiteStoryRepository(
            sqlite3.connect("app.db")
        )
```

Hãy chỉ ra **từng dependency violation**.

---

### Bài 5 — nâng cao

Thiết kế:

```text
application/
    ports/
        story_repository.py

infrastructure/
    sqlite/
        story_repository.py
```

sao cho:

```text
SQLiteStoryRepository
```

implement:

```text
StoryRepository
```

nhưng:

```text
StoryRepository
```

không biết SQLite.

---

## Kiến thức cần nhớ trước Buổi 23

Buổi 23 chúng ta sẽ thực sự viết:

```text
SQLiteStoryRepository
SQLiteChapterRepository
```

và xử lý bài toán khó hơn:

```text
SQLite Row
    ↓
Domain Entity
    ↓
Value Object
```

đặc biệt:

```text
StoryId
StoryTitle
SourceId
StoryStatus
```

sẽ được **map hai chiều**:

```text
Database
   ↓
Domain

Domain
   ↓
Database
```

Sau đó chúng ta sẽ đi tới **Buổi 24 — Unit of Work**, nơi Repository và SQLite transaction thực sự được kết nối với nhau.
