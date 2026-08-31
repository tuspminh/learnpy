# DDD Deep Dive — Buổi 30

# Use Case Architecture

Đây là **buổi tổng hợp rất quan trọng** của phần VI.

Sau Buổi 30, ta sẽ ghép lại toàn bộ kiến thức đã học:

```text
DDD
├── Strategic
│   ├── Subdomain
│   ├── Bounded Context
│   └── Context Mapping
│
├── Tactical
│   ├── Entity
│   ├── Value Object
│   ├── Aggregate
│   ├── Repository
│   ├── Unit of Work
│   └── Domain Service
│
└── Application
    └── Use Case
```

Mục tiêu hôm nay là xây kiến trúc:

```text
CLI
 ↓
Use Case
 ↓
Domain
 ↓
Repository
 ↓
SQLite
```

nhưng theo cách **DDD + Clean Architecture**, không phải chỉ đơn giản gọi SQL từ CLI.

---

# 1. Kiến trúc mục tiêu

Ta sẽ xây một hệ thống nhỏ quản lý truyện:

```text
                    CLI
                     │
                     ▼
              Application Layer
                     │
              CreateStoryUseCase
              AddChapterUseCase
              PublishStoryUseCase
                     │
                     ▼
                Domain Layer
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Story      Chapter    ValueObject
          │
          ▼
       Repository
          │
          ▼
     Infrastructure
          │
          ▼
        SQLite
```

Điểm quan trọng:

```text
CLI không biết SQL
Domain không biết SQLite
Repository interface không biết SQLite
Use Case không biết CLI
```

---

# 2. Project structure

Ta bắt đầu với:

```text
src/
└── story_app/
    │
    ├── domain/
    │   ├── story/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   ├── exceptions.py
    │   │   └── repositories.py
    │   │
    │   └── shared/
    │
    ├── application/
    │   └── story/
    │       ├── commands.py
    │       ├── results.py
    │       ├── create_story.py
    │       ├── add_chapter.py
    │       └── publish_story.py
    │
    ├── infrastructure/
    │   ├── database/
    │   │   ├── connection.py
    │   │   └── schema.sql
    │   │
    │   └── repositories/
    │       └── sqlite_story_repository.py
    │
    └── interfaces/
        └── cli/
            └── main.py
```

Đây chưa phải cấu trúc duy nhất.

Điều quan trọng là **dependency direction**.

---

# 3. Dependency Rule

Ta muốn:

```text
interfaces
     ↓
application
     ↓
domain

infrastructure
     ↓
domain/application abstractions
```

Không muốn:

```text
domain
   ↓
sqlite
```

hoặc:

```text
domain
   ↓
click
```

hoặc:

```text
application
   ↓
PySide6
```

---

# 4. Domain Layer

Bắt đầu từ Domain.

Ta có:

```text
Story
 ├── StoryId
 ├── StoryTitle
 ├── SourceId
 ├── status
 └── chapters
```

---

# 5. StoryId

```python
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class StoryId:
    value: UUID

    @classmethod
    def generate(cls) -> "StoryId":
        return cls(uuid4())
```

`StoryId` là Value Object.

---

# 6. StoryTitle

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryTitle:

    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError(
                "Story title cannot be empty"
            )

        object.__setattr__(
            self,
            "value",
            value,
        )
```

Domain tự bảo vệ invariant.

---

# 7. StoryStatus

Dùng Enum:

```python
from enum import Enum


class StoryStatus(Enum):

    DRAFT = "draft"
    PUBLISHED = "published"
```

---

# 8. Story Entity

```python
class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: StoryTitle,
        source_id: str,
        status: StoryStatus = StoryStatus.DRAFT,
    ):
        self.id = story_id
        self.title = title
        self.source_id = source_id
        self.status = status
```

---

# 9. Factory method

Không để Application phải biết cách khởi tạo Entity quá sâu.

Ta thêm:

```python
class Story:

    @classmethod
    def create(
        cls,
        title: StoryTitle,
        source_id: str,
    ) -> "Story":

        return cls(
            story_id=StoryId.generate(),
            title=title,
            source_id=source_id,
        )
```

Application chỉ cần:

```python
Story.create(...)
```

---

# 10. Business behavior

```python
class Story:

    ...

    def publish(self):

        if self.status == StoryStatus.PUBLISHED:
            raise StoryAlreadyPublished()

        self.status = StoryStatus.PUBLISHED
```

Đây là Domain logic.

Không phải:

```python
story.status = "published"
```

từ CLI.

---

# 11. Add Chapter

Story là Aggregate Root.

Vì vậy:

```python
story.add_chapter(chapter)
```

thay vì:

```python
story.chapters.append(chapter)
```

Ví dụ:

```python
class Story:

    def add_chapter(self, chapter):

        if self.has_chapter_number(
            chapter.number
        ):
            raise ChapterAlreadyExists()

        self._chapters.append(chapter)
```

---

# 12. Aggregate Boundary

Ta có:

```text
Story Aggregate
│
├── Story
├── Chapter
├── StoryTitle
├── StoryId
└── ChapterNumber
```

Bên ngoài không trực tiếp thay đổi:

```python
story._chapters
```

Mọi thay đổi phải thông qua Root:

```python
story.add_chapter(...)
```

---

# 13. Repository Interface

Domain cần persistence abstraction.

Ví dụ:

```python
from abc import ABC, abstractmethod


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

Domain không biết:

```text
SQLite
PostgreSQL
MongoDB
```

---

# 14. Unit of Work

Ta cần transaction boundary.

```python
from abc import ABC, abstractmethod


class UnitOfWork(ABC):

    stories: StoryRepository

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        ...

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...
```

---

# 15. Application Layer

Bây giờ mới đến Use Case.

Ví dụ:

```text
CreateStoryUseCase
```

Application Layer sẽ:

```text
1. nhận command
2. tạo domain object
3. gọi repository
4. commit transaction
5. trả result
```

---

# 16. Command

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateStoryCommand:

    title: str
    source_id: str
```

Đây là Application DTO.

---

# 17. Result

```python
@dataclass(frozen=True)
class CreateStoryResult:

    story_id: str
```

---

# 18. CreateStoryUseCase

```python
class CreateStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(
        self,
        command: CreateStoryCommand,
    ) -> CreateStoryResult:

        title = StoryTitle(command.title)

        story = Story.create(
            title=title,
            source_id=command.source_id,
        )

        with self.uow:

            self.uow.stories.add(story)

            self.uow.commit()

        return CreateStoryResult(
            story_id=str(story.id.value)
        )
```

---

# 19. Ai làm gì?

Trong đoạn trên:

```python
title = StoryTitle(command.title)
```

Domain Value Object.

```python
story = Story.create(...)
```

Domain Entity.

```python
self.uow.stories.add(story)
```

Repository.

```python
self.uow.commit()
```

Transaction.

```python
CreateStoryResult(...)
```

Application DTO.

---

# 20. AddChapter Use Case

Command:

```python
@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    chapter_number: int
    title: str
    content: str
```

Result:

```python
@dataclass(frozen=True)
class AddChapterResult:

    story_id: str
    chapter_id: str
```

---

# 21. Use Case

```python
class AddChapterUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(
        self,
        command: AddChapterCommand,
    ) -> AddChapterResult:

        story_id = StoryId(
            UUID(command.story_id)
        )

        with self.uow:

            story = self.uow.stories.get(
                story_id
            )

            if story is None:
                raise StoryNotFound(
                    command.story_id
                )

            chapter = Chapter.create(
                number=ChapterNumber(
                    command.chapter_number
                ),
                title=ChapterTitle(
                    command.title
                ),
                content=command.content,
            )

            story.add_chapter(chapter)

            self.uow.stories.save(story)

            self.uow.commit()

        return AddChapterResult(
            story_id=str(story.id.value),
            chapter_id=str(chapter.id.value),
        )
```

---

# 22. Điều rất quan trọng

Use Case **không tự implement**:

```text
chapter number phải > 0
```

Nó gọi:

```python
ChapterNumber(...)
```

Domain bảo vệ rule.

Use Case cũng không tự làm:

```python
story.status = "published"
```

Nó gọi:

```python
story.publish()
```

---

# 23. PublishStory Use Case

```python
@dataclass(frozen=True)
class PublishStoryCommand:

    story_id: str
```

Result:

```python
@dataclass(frozen=True)
class PublishStoryResult:

    story_id: str
    status: str
```

Use Case:

```python
class PublishStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(
        self,
        command: PublishStoryCommand,
    ) -> PublishStoryResult:

        story_id = StoryId(
            UUID(command.story_id)
        )

        with self.uow:

            story = self.uow.stories.get(
                story_id
            )

            if story is None:
                raise StoryNotFound(
                    command.story_id
                )

            story.publish()

            self.uow.stories.save(story)

            self.uow.commit()

        return PublishStoryResult(
            story_id=str(story.id.value),
            status=story.status.value,
        )
```

---

# 24. Infrastructure

Bây giờ mới xuất hiện SQLite.

```text
Infrastructure
```

chịu trách nhiệm:

```text
sqlite3
connection
SQL
mapping
transactions
```

---

# 25. SQLite connection

```python
import sqlite3


def create_connection(
    database: str,
) -> sqlite3.Connection:

    connection = sqlite3.connect(
        database
    )

    connection.row_factory = sqlite3.Row

    return connection
```

---

# 26. SQLite Repository

```python
class SQLiteStoryRepository:

    def __init__(
        self,
        connection,
    ):
        self.connection = connection
```

Implement interface:

```python
class SQLiteStoryRepository(
    StoryRepository
):
    ...
```

---

# 27. Mapping Domain → Database

Ví dụ database:

```sql
CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_id TEXT NOT NULL,
    status TEXT NOT NULL
);
```

Repository:

```python
def add(self, story: Story) -> None:

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
            str(story.id.value),
            story.title.value,
            story.source_id,
            story.status.value,
        ),
    )
```

Đây là Infrastructure logic.

---

# 28. Mapping Database → Domain

Khi đọc:

```python
row = self.connection.execute(
    """
    SELECT *
    FROM stories
    WHERE id = ?
    """,
    (str(story_id.value),),
).fetchone()
```

Sau đó reconstruct:

```python
return Story(
    story_id=StoryId(
        UUID(row["id"])
    ),
    title=StoryTitle(
        row["title"]
    ),
    source_id=row["source_id"],
    status=StoryStatus(
        row["status"]
    ),
)
```

Database row không phải Domain Entity.

---

# 29. SQLite Unit of Work

```python
class SQLiteUnitOfWork:

    def __init__(self, connection):
        self.connection = connection

        self.stories = SQLiteStoryRepository(
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

        if exc_type:
            self.rollback()

        self.connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()
```

Trong project thực tế, lifecycle connection/UoW có thể thiết kế tinh tế hơn; ở đây mục tiêu là hiểu kiến trúc.

---

# 30. CLI

CLI chỉ làm nhiệm vụ:

```text
parse input
↓
create command
↓
call use case
↓
display result/error
```

Ví dụ:

```python
def create_story(
    title: str,
    source_id: str,
):

    command = CreateStoryCommand(
        title=title,
        source_id=source_id,
    )

    result = use_case.execute(command)

    print(
        f"Created story: {result.story_id}"
    )
```

CLI không:

```text
SQL
Entity persistence
transaction
business rule
```

---

# 31. Full Flow

Khi user chạy:

```bash
story create \
    --title "Đấu Phá Thương Khung" \
    --source novel
```

flow:

```text
CLI
 │
 │ CreateStoryCommand
 ▼
CreateStoryUseCase
 │
 ▼
StoryTitle
 │
 ▼
Story.create()
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

---

# 32. Dependency Injection

CLI cần tạo dependencies:

```python
connection = create_connection(
    "stories.db"
)

uow = SQLiteUnitOfWork(
    connection
)

use_case = CreateStoryUseCase(
    uow
)
```

Sau đó:

```python
result = use_case.execute(
    command
)
```

---

# 33. Composition Root

Đoạn:

```python
connection = ...
uow = ...
use_case = ...
```

nên nằm ở một nơi gọi là:

> **Composition Root**

Ví dụ:

```text
interfaces/cli/bootstrap.py
```

hoặc:

```text
main.py
```

Nó là nơi wiring:

```text
Interface
    ↓
Use Case
    ↓
Repository implementation
    ↓
Database
```

---

# 34. Domain không tạo Repository

Không làm:

```python
class Story:

    def __init__(self):

        self.repo = SQLiteStoryRepository()
```

❌

Domain không biết infrastructure.

---

# 35. Use Case không tự tạo SQLite

Không:

```python
class CreateStoryUseCase:

    def execute(...):

        connection = sqlite3.connect(
            "story.db"
        )
```

❌

Use Case nhận dependency từ bên ngoài:

```python
class CreateStoryUseCase:

    def __init__(self, uow):
        self.uow = uow
```

---

# 36. Đây chính là Dependency Inversion

```text
                  ┌─────────────────┐
                  │  Application    │
                  │                 │
                  │ CreateStoryUC   │
                  └────────┬────────┘
                           │
                           ▼
                  StoryRepository
                    <<interface>>
                           ▲
                           │
                  ┌────────┴────────┐
                  │ SQLiteRepository│
                  └─────────────────┘
```

Application phụ thuộc abstraction.

Infrastructure implement abstraction.

---

# 37. Testing

Đây là lúc kiến trúc bắt đầu phát huy sức mạnh.

Ta có thể tạo Fake Repository:

```python
class FakeStoryRepository:

    def __init__(self):
        self.items = {}

    def add(self, story):
        self.items[story.id] = story

    def get(self, story_id):
        return self.items.get(story_id)

    def save(self, story):
        self.items[story.id] = story
```

Không cần SQLite.

---

# 38. Fake Unit of Work

```python
class FakeUnitOfWork:

    def __init__(self):

        self.stories = (
            FakeStoryRepository()
        )

        self.committed = False

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
```

---

# 39. Test Use Case

```python
def test_create_story():

    uow = FakeUnitOfWork()

    use_case = CreateStoryUseCase(uow)

    result = use_case.execute(
        CreateStoryCommand(
            title="Story A",
            source_id="source-1",
        )
    )

    assert result.story_id
    assert uow.committed
```

Không:

```text
SQLite
filesystem
CLI
PySide6
```

---

# 40. Test Domain riêng

```python
def test_story_publish():

    story = Story.create(
        title=StoryTitle("Story A"),
        source_id="source-1",
    )

    story.publish()

    assert (
        story.status
        == StoryStatus.PUBLISHED
    )
```

Domain test cực nhanh.

---

# 41. Test Infrastructure riêng

SQLite repository có integration test:

```text
SQLiteStoryRepository
        ↓
real SQLite
```

Ta không cần đưa SQLite vào unit test của Domain.

---

# 42. Testing Pyramid

```text
             E2E
            /   \
         Integration
        /           \
      Unit          Unit
```

DDD architecture giúp:

```text
Domain → unit test
Use Case → unit test
Repository → integration test
CLI → interface test
```

---

# 43. Error Handling

Giả sử:

```python
story.publish()
```

ném:

```python
StoryAlreadyPublished
```

Use Case không cần:

```python
print("Error!")
```

CLI xử lý:

```python
try:

    result = use_case.execute(
        command
    )

except StoryAlreadyPublished as exc:

    print(f"Error: {exc}")
```

---

# 44. PySide6 sau này

Điểm hay là nếu đổi CLI thành PySide6:

```text
CLI
 ↓
CreateStoryUseCase
```

đổi thành:

```text
PySide6
 ↓
CreateStoryUseCase
```

Use Case không đổi.

---

# 45. REST API sau này

Thêm:

```text
FastAPI
 ↓
CreateStoryUseCase
```

Domain không đổi.

Repository có thể vẫn:

```text
SQLite
```

hoặc:

```text
PostgreSQL
```

---

# 46. Crawler Worker

Project đọc truyện của bạn còn có Worker:

```text
Crawler Worker
      ↓
StartCrawlerUseCase
      ↓
CrawlerJob
      ↓
Repository
      ↓
SQLite
```

Cũng không cần thay Domain khi Worker thay đổi.

---

# 47. Kiến trúc hoàn chỉnh

```text
                 ┌──────────────┐
                 │     CLI      │
                 └──────┬───────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Application      │
              │                  │
              │ Use Cases        │
              │ Commands         │
              │ Results          │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Domain           │
              │                  │
              │ Entity           │
              │ Value Object     │
              │ Aggregate        │
              │ Domain Service   │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Abstractions     │
              │                  │
              │ Repository       │
              │ UnitOfWork       │
              └────────┬─────────┘
                       ▲
                       │
              ┌────────┴─────────┐
              │ Infrastructure   │
              │                  │
              │ SQLite           │
              │ httpx            │
              │ Redis            │
              └──────────────────┘
```

---

# 48. Một điều chỉnh quan trọng về "Repository thuộc Domain"

Trong DDD + Clean Architecture, bạn sẽ gặp hai cách tổ chức:

### Cách A

```text
domain/
    repositories.py
```

Interface Repository thuộc Domain.

### Cách B

```text
application/
    ports/
        repositories.py
```

Interface thuộc Application.

Cả hai đều có thể hợp lý tùy kiến trúc.

Điều quan trọng nhất không phải vị trí file.

Mà là:

```text
Domain/Application
        ↓
abstraction
        ↑
Infrastructure
```

và Domain không phụ thuộc database implementation.

---

# 49. DDD + Clean Architecture

Hai thứ này không giống nhau.

### DDD

Tập trung vào:

```text
Business Model
Entity
Value Object
Aggregate
Domain Service
Bounded Context
```

### Clean Architecture

Tập trung vào:

```text
Dependency direction
Separation of concerns
Dependency inversion
Framework independence
```

Kết hợp:

```text
DDD
+
Clean Architecture
```

cho ta:

```text
Business model mạnh
+
Dependency sạch
```

---

# 50. Kiến trúc project hoàn chỉnh hơn

Khi project lớn lên, tôi khuyên chuyển sang:

```text
src/
└── story_app/

    ├── domain/
    │   ├── story/
    │   │   ├── entity.py
    │   │   ├── value_objects.py
    │   │   ├── services.py
    │   │   ├── exceptions.py
    │   │   └── repository.py
    │   │
    │   ├── crawler/
    │   ├── reading/
    │   └── user/
    │
    ├── application/
    │   ├── story/
    │   │   ├── commands.py
    │   │   ├── results.py
    │   │   ├── create.py
    │   │   ├── add_chapter.py
    │   │   └── publish.py
    │   │
    │   ├── crawler/
    │   └── reading/
    │
    ├── infrastructure/
    │   ├── sqlite/
    │   │   ├── connection.py
    │   │   ├── uow.py
    │   │   └── repositories/
    │   │
    │   ├── crawler/
    │   └── filesystem/
    │
    └── interfaces/
        ├── cli/
        ├── pyside6/
        └── api/
```

Đây là cấu trúc rất phù hợp để sau này ghép với:

```text
PySide6
SQLite
Crawler
httpx
Redis
Worker
```

---

# 51. Quy tắc vàng

Khi viết code, hãy tự hỏi:

### Câu 1

> Đây có phải business rule không?

Nếu có:

```text
Domain
```

### Câu 2

> Rule thuộc tự nhiên về một Entity?

Nếu có:

```text
Entity
```

### Câu 3

> Rule liên quan nhiều Domain Object?

Nếu có:

```text
Domain Service
```

### Câu 4

> Đây là workflow của một Use Case?

Nếu có:

```text
Application Service
```

### Câu 5

> Đây là persistence?

Nếu có:

```text
Repository
```

### Câu 6

> Đây là HTTP/SQLite/Redis/FileSystem?

Nếu có:

```text
Infrastructure
```

---

# 52. Flow chuẩn

Cuối cùng hãy ghi nhớ flow này:

```text
User
 │
 ▼
Interface
 │
 │ Command
 ▼
Application
 │
 │ Use Case
 ▼
Domain
 │
 ├── Entity
 ├── Value Object
 ├── Aggregate
 └── Domain Service
 │
 ▼
Repository abstraction
 │
 ▼
Unit of Work
 │
 ▼
Infrastructure
 │
 ▼
SQLite
```

Chiều ngược lại:

```text
SQLite
  │
  ▼
Repository
  │
  ▼
Domain Entity
  │
  ▼
Use Case
  │
  ▼
Result DTO
  │
  ▼
CLI / PySide6 / API
```

---

# 53. Sau 30 buổi, bạn đã có một DDD foundation khá đầy đủ

```text
PART I — Foundation
    ↓
Strategic DDD
    ↓
Entity / Value Object
    ↓
Aggregate
    ↓
Repository / UoW
    ↓
Domain Service
    ↓
Application Service
    ↓
Use Case Architecture
```

Bạn đã đi từ:

```text
"Class nào chứa data?"
```

sang:

```text
"Business model nên được tổ chức thế nào?"
```

và cuối cùng:

```text
"Use Case đi xuyên qua architecture như thế nào?"
```

---

# Bài tập tổng kết Buổi 30

Thiết kế Use Case:

```text
CompleteCrawlerJobUseCase
```

Requirement:

```text
CrawlerJob
    ↓
RUNNING
    ↓
COMPLETED
```

Input:

```python
CompleteCrawlerJobCommand(
    job_id,
    chapter_count,
)
```

Flow:

```text
CLI
 ↓
Command
 ↓
CompleteCrawlerJobUseCase
 ↓
CrawlerJobRepository.get()
 ↓
CrawlerJob.complete()
 ↓
Repository.save()
 ↓
UoW.commit()
 ↓
Result
```

Bạn cần xác định:

```text
1. CompleteCrawlerJobCommand
2. CompleteCrawlerJobResult
3. CompleteCrawlerJobUseCase
4. CrawlerJob.complete()
5. CrawlerJobRepository
6. UnitOfWork
7. SQLiteCrawlerJobRepository
8. CLI command
```

Đặc biệt hãy để ý:

```python
job.status = "completed"
```

không nên nằm trong CLI/Use Case nếu đây là **business state transition**.

Nên:

```python
job.complete(chapter_count)
```

Đó chính là tư duy DDD quan trọng nhất của toàn bộ phần này:

> **Application điều phối — Domain quyết định — Repository lưu trữ — Infrastructure giao tiếp với thế giới bên ngoài.**
