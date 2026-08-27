# Buổi 15 — SOLID + DDD

Đây là buổi rất quan trọng vì chúng ta bắt đầu nối 3 mảnh ghép:

```text
SOLID
  +
DDD
  +
Architecture
```

Mục tiêu không phải học DDD như một danh sách pattern, mà hiểu:

> **SOLID giúp thiết kế object và dependency tốt; DDD giúp mô hình hóa business domain tốt.**

Khi kết hợp đúng, ta có architecture rất mạnh cho các hệ thống phức tạp.

---

# 1. DDD là gì?

DDD — Domain-Driven Design.

Ý tưởng cốt lõi:

> **Đặt domain/business logic ở trung tâm của hệ thống.**

Ví dụ hệ thống quản lý truyện:

```text
                    Story Domain
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Story          Chapter       Source
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                    Business Rules
```

Thay vì bắt đầu bằng:

```text
SQLite
FastAPI
PySide6
requests
BeautifulSoup
```

ta bắt đầu bằng:

```text
Story
Chapter
Author
Source
Crawl
ReadingProgress
```

Đây chính là tư duy DDD.

---

# 2. SOLID và DDD giải quyết hai vấn đề khác nhau

### SOLID

Quan tâm:

```text
Code structure
Dependency
Coupling
Responsibility
Extension
Substitution
Interfaces
```

### DDD

Quan tâm:

```text
Business domain
Business concepts
Business rules
Entities
Value Objects
Aggregates
Domain Services
Boundaries
```

Có thể hình dung:

```text
DDD
 ↓
"What does the business mean?"
 ↓
Domain Model
```

Trong khi:

```text
SOLID
 ↓
"How should this model be structured?"
 ↓
Maintainable Design
```

---

# 3. Domain Layer

Ta bắt đầu bằng:

```text
Domain
```

Domain chứa:

```text
Entity
Value Object
Aggregate
Domain Service
Domain Rule
Domain Event
Repository Interface
```

Nhưng **không nên phụ thuộc vào infrastructure**.

Ví dụ Domain không nên biết:

```python
import sqlite3
import requests
from PySide6.QtWidgets import ...
```

Đó là dependency direction rất quan trọng.

---

# 4. Dependency Direction

Architecture:

```text
Infrastructure
      │
      ↓
Application
      │
      ↓
Domain
```

Dependency thực tế nên hướng:

```text
Infrastructure
       ↓
Application
       ↓
Domain
```

Domain không import ngược:

```text
Domain
   ❌
   ↓
SQLite
HTTP
Flet
PySide6
```

---

# 5. Vì sao điều này liên quan DIP?

DIP nói:

> High-level policy không nên phụ thuộc low-level detail.

Ví dụ:

```text
Business Rule
     ↓
SQLite
```

là thiết kế không tốt.

Thay bằng:

```text
Business Rule
     ↓
Repository abstraction
     ↑
SQLite implementation
```

Ta đảo dependency.

```text
Domain
  ↑
Repository Interface
  ↑
SQLiteRepository
```

Thực tế module dependency:

```text
SQLiteRepository
      ↓
Repository Interface
      ↑
    Domain
```

---

# 6. Entity

Entity có identity.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Story:

    id: int
    title: str
```

Hai object:

```python
Story(1, "A")
Story(2, "A")
```

có cùng title nhưng là **hai Story khác nhau**.

Identity:

```text
id = 1
id = 2
```

---

# 7. Entity + SRP

Một Entity không nên trở thành:

```text
Story
 ├── database
 ├── HTTP
 ├── HTML parsing
 ├── file system
 ├── email
 └── UI
```

Ví dụ xấu:

```python
class Story:

    def save_to_sqlite(self):
        ...

    def crawl(self):
        ...

    def send_email(self):
        ...
```

Entity đang có quá nhiều responsibility.

---

# 8. Entity nên chứa gì?

Entity nên chứa:

```text
identity
state
business behavior
invariants
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Story:

    id: int
    title: str

    def rename(self, title: str) -> None:

        title = title.strip()

        if not title:
            raise ValueError(
                "Title cannot be empty"
            )

        self.title = title
```

Đây là business behavior.

---

# 9. Value Object

Value Object không có identity riêng.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryTitle:

    value: str
```

Hai:

```python
StoryTitle("Harry Potter")
```

và:

```python
StoryTitle("Harry Potter")
```

được coi là cùng value.

---

# 10. Value Object + SOLID

Value Object thường giúp SRP.

Thay vì:

```python
class Story:

    def __init__(self, title):
        if not title:
            ...
        if len(title) > 500:
            ...
```

ta có:

```python
@dataclass(frozen=True)
class StoryTitle:

    value: str

    def __post_init__(self):

        value = self.value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty"
            )

        if len(value) > 500:
            raise ValueError(
                "Title too long"
            )
```

`StoryTitle` chịu trách nhiệm về:

```text
Title validity
```

Đó là SRP.

---

# 11. Aggregate

Aggregate là một boundary của domain model.

Ví dụ:

```text
Story
 ├── Chapter
 ├── Chapter
 └── Chapter
```

Có thể thiết kế:

```text
Story Aggregate
       │
       ├── Story
       │
       └── Chapters
```

`Story` có thể là Aggregate Root.

---

# 12. Aggregate Root

Client không nên tùy tiện thay đổi object bên trong Aggregate.

Thay vì:

```python
story.chapters[0].title = "..."
```

có thể:

```python
story.rename_chapter(
    chapter_id=1,
    title="..."
)
```

Aggregate Root kiểm soát invariant.

---

# 13. Aggregate + Encapsulation

Ví dụ:

```python
class Story:

    def __init__(self, story_id, title):
        self.id = story_id
        self.title = title
        self._chapters = []

    def add_chapter(self, chapter):
        self._chapters.append(chapter)
```

Business rule:

```python
def add_chapter(self, chapter):

    if chapter.story_id != self.id:
        raise ValueError(
            "Chapter belongs to another story"
        )

    self._chapters.append(chapter)
```

Aggregate bảo vệ invariant.

---

# 14. Aggregate + SRP

Một Aggregate không có nghĩa:

> "Nhét tất cả business logic vào một class."

Aggregate có một responsibility lớn hơn:

> **Bảo vệ consistency boundary của domain.**

Nếu Aggregate trở thành:

```text
God Object
```

thì ta đã đi quá xa.

---

# 15. Domain Service

Có những business rule không tự nhiên thuộc về một Entity.

Ví dụ:

```text
Story
Author
Ranking
```

Business rule:

> Tính ranking của Story dựa trên nhiều object.

Không nhất thiết:

```python
class Story:
    def calculate_ranking(...):
        ...
```

Có thể:

```python
class StoryRankingService:

    def calculate(
        self,
        story,
        statistics,
    ):
        ...
```

Đây là Domain Service.

---

# 16. Domain Service + SRP

Domain Service chứa:

```text
business logic
```

nhưng không chứa:

```text
database
HTTP
UI
```

Ví dụ tốt:

```python
class ChapterNumberingService:

    def next_number(self, chapters):
        if not chapters:
            return 1

        return max(
            chapter.number
            for chapter in chapters
        ) + 1
```

---

# 17. Repository

Repository đại diện cho persistence boundary.

Ví dụ:

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

Domain/Application biết:

```text
StoryRepository
```

không cần biết:

```text
SQLite
PostgreSQL
MongoDB
```

---

# 18. Repository không phải DAO đơn thuần

Đây là distinction quan trọng.

DAO thường thiên về:

```text
database operation
```

Ví dụ:

```python
execute_sql()
fetch_one()
fetch_all()
```

Repository nên thể hiện:

```text
domain-oriented persistence
```

Ví dụ:

```python
story_repository.get_by_id(...)
```

thay vì:

```python
db.execute(
    "SELECT ..."
)
```

---

# 19. Application Service

Application Service điều phối use case.

Ví dụ:

```python
class CreateStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story: Story,
    ):
        self.repository.save(story)
```

Nó không nhất thiết chứa business rule phức tạp.

Nó chủ yếu:

```text
orchestration
transaction boundary
dependency coordination
```

---

# 20. Domain vs Application

Đây là chỗ người mới học DDD thường nhầm.

### Domain

Hỏi:

> Business rule là gì?

Ví dụ:

```python
story.rename(...)
```

### Application

Hỏi:

> Làm thế nào để thực hiện use case?

Ví dụ:

```python
CreateStory.execute(...)
```

---

# 21. Ví dụ

Business rule:

```python
class Story:

    def publish(self):

        if not self.title:
            raise ValueError(
                "Cannot publish"
            )

        self.status = "published"
```

Đây là Domain.

Application:

```python
class PublishStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id):

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

Đây là Application.

---

# 22. Infrastructure

Infrastructure implement abstraction.

Ví dụ:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, story_id):
        ...

    def save(self, story):
        ...
```

Infrastructure biết:

```text
SQLite
SQL
connection
transaction
```

Domain không biết những thứ đó.

---

# 23. Architecture tổng thể

```text
┌─────────────────────────────────────┐
│          Infrastructure             │
│                                     │
│ SQLiteRepository                    │
│ HTTPClient                          │
│ BeautifulSoupParser                 │
│ FileStorage                         │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│           Application               │
│                                     │
│ CreateStory                         │
│ PublishStory                        │
│ CrawlStory                          │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│              Domain                 │
│                                     │
│ Story                               │
│ Chapter                             │
│ StoryTitle                          │
│ StoryRepository                     │
│ Domain Services                     │
└─────────────────────────────────────┘
```

---

# 24. SOLID nằm ở đâu?

### SRP

```text
Entity
Value Object
Domain Service
Application Service
Repository
```

mỗi loại có responsibility riêng.

### OCP

Thêm:

```text
PostgresRepository
MongoRepository
```

không sửa application logic.

### LSP

```text
SQLiteRepository
MemoryRepository
PostgresRepository
```

đều phải thay thế được `StoryRepository`.

### ISP

Repository interface nhỏ:

```python
get_by_id()
save()
```

không phải:

```text
20 methods
```

### DIP

Application phụ thuộc:

```text
Repository abstraction
```

không phụ thuộc:

```text
SQLite
```

---

# 25. DDD + DIP

Đây là điểm quan trọng nhất hôm nay.

Sai:

```python
class CreateStory:

    def __init__(self):
        self.repository = SQLiteStoryRepository()
```

Application đang phụ thuộc Infrastructure.

Đúng:

```python
class CreateStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository
```

Infrastructure:

```python
class SQLiteStoryRepository:
    ...
```

Composition Root nối chúng:

```python
repository = SQLiteStoryRepository(connection)

use_case = CreateStory(repository)
```

---

# 26. Composition Root

Composition Root là nơi application được "lắp ráp".

Ví dụ:

```python
def build_application():

    connection = create_database()

    repository = SQLiteStoryRepository(
        connection
    )

    crawler = HttpCrawler()

    return Application(
        repository=repository,
        crawler=crawler,
    )
```

Đây là nơi biết:

```text
SQLite
HTTP
filesystem
implementation
```

Domain/Application không cần biết.

---

# 27. Đây chính là Dependency Direction

```text
                  Composition Root
                         │
             ┌───────────┴───────────┐
             ↓                       ↓
      SQLiteRepository          HttpCrawler
             │                       │
             ↓                       ↓
      Repository Protocol       Crawler Protocol
             │                       │
             └───────────┬───────────┘
                         ↓
                    Application
                         ↓
                       Domain
```

Dependency đi từ detail vào abstraction.

---

# 28. DDD + Testing

Đây là lợi ích lớn.

Domain:

```python
def test_story_cannot_publish_without_title():
    ...
```

Không cần:

```text
SQLite
HTTP
network
```

Application:

```python
FakeRepository
```

Infrastructure:

```text
Integration Test
```

Architecture tự nhiên tạo test boundary.

---

# 29. Domain Model không phải ORM Model

Đây là vấn đề cực kỳ quan trọng.

Không nên mặc định:

```python
class Story(SQLAlchemyModel):
    ...
```

là Domain Model.

ORM model thường phản ánh:

```text
database structure
```

Domain model phản ánh:

```text
business meaning
```

Hai thứ có thể giống nhau trong hệ thống đơn giản.

Nhưng không nhất thiết phải giống nhau.

---

# 30. Ví dụ

Database:

```text
stories
----------------
id
title
created_at
updated_at
status
deleted_at
```

Domain:

```python
@dataclass
class Story:

    id: int
    title: StoryTitle
    status: StoryStatus
```

Infrastructure mapping:

```text
Database Row
     ↓
ORM / Mapper
     ↓
Domain Story
```

Đây là separation rất quan trọng.

---

# 31. SOLID + DDD + Clean Architecture

Ba thứ bắt đầu hội tụ:

```text
              Domain
                ↑
                │
          Application
                ↑
                │
         Infrastructure
```

DDD cho ta:

```text
Domain Model
```

SOLID cho ta:

```text
Dependency rules
```

Clean Architecture cho ta:

```text
Architectural boundaries
```

---

# 32. Ví dụ với ứng dụng crawler của bạn

Ta có domain:

```text
Story
Chapter
Source
Author
```

Use Cases:

```text
CrawlStory
CrawlChapter
PublishStory
UpdateStory
MarkChapterRead
```

Interfaces:

```text
StoryRepository
ChapterRepository
Crawler
```

Infrastructure:

```text
SQLiteStoryRepository
SQLiteChapterRepository
SiteACrawler
SiteBCrawler
```

Architecture:

```text
CLI
 ↓
Application
 ↓
Domain
 ↑
Interfaces
 ↑
Infrastructure
```

---

# 33. Crawler không nên là Domain

Ví dụ:

```python
class Story:

    def crawl(self):
        requests.get(...)
```

Đây là thiết kế không tốt.

Vì:

```text
Story
```

là domain concept.

Còn:

```text
HTTP
website
BeautifulSoup
network
```

là infrastructure concern.

Tách:

```text
Story
   ↑
CrawlStory
   ↑
Crawler
   ↑
SiteCrawler
```

---

# 34. Một architecture tốt hơn

```text
CLI
 │
 ↓
CrawlStoryUseCase
 │
 ├──── StoryRepository
 │
 └──── Crawler
          ↑
          │
    ┌─────┴─────┐
    │           │
 SiteACrawler SiteBCrawler
```

Domain:

```text
Story
Chapter
StoryTitle
```

Infrastructure:

```text
SQLite
HTTP
BeautifulSoup
```

---

# 35. Domain Rule

Ví dụ:

> Chapter number phải lớn hơn 0.

Không nên để rule này chỉ nằm trong UI:

```python
if chapter_number <= 0:
    show_error(...)
```

Vì CLI có thể bypass.

API có thể bypass.

Crawler có thể bypass.

Rule phải nằm ở domain boundary.

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

---

# 36. Invariant

Invariant là điều kiện phải luôn đúng.

Ví dụ:

```text
Story
```

phải:

```text
title != empty
```

```text
Chapter
```

phải:

```text
number > 0
```

Aggregate:

```text
Chapter.story_id == Story.id
```

Invariant nên được bảo vệ ở domain layer.

---

# 37. SOLID + Invariant

Một Entity tốt:

```text
không cho phép state invalid
```

Ví dụ xấu:

```python
story.title = ""
```

rồi hy vọng:

```text
Validator
```

sẽ sửa sau.

Tốt hơn:

```python
story.rename("")
```

ném exception ngay.

Domain tự bảo vệ invariant.

---

# 38. Domain Service không nên thành God Service

Sai:

```python
class StoryDomainService:

    def crawl(self):
        ...

    def save(self):
        ...

    def send_email(self):
        ...

    def parse_html(self):
        ...

    def publish(self):
        ...
```

Đây chỉ là:

```text
God Service
```

đổi tên thành Domain Service.

Tên gọi không cứu được architecture.

---

# 39. DDD + ISP

Repository:

```python
class StoryReader(Protocol):

    def get_by_id(self, story_id):
        ...
```

Writer:

```python
class StoryWriter(Protocol):

    def save(self, story):
        ...
```

Use case chỉ cần read:

```python
class GetStory:

    def __init__(
        self,
        repository: StoryReader,
    ):
        ...
```

Không cần phụ thuộc:

```text
save
delete
update
search
bulk_insert
```

Đây là ISP.

---

# 40. DDD + OCP

Ví dụ crawler:

```python
class Crawler(Protocol):

    def crawl(self, url) -> Story:
        ...
```

Có:

```text
SiteACrawler
SiteBCrawler
SiteCCrawler
```

Thêm site mới:

```text
SiteDCrawler
```

không cần sửa:

```text
CrawlStoryUseCase
```

Đây là OCP.

---

# 41. DDD + LSP

Nếu:

```text
Crawler
```

có contract:

```text
crawl(url) → Story
```

thì:

```text
SiteACrawler
SiteBCrawler
```

phải thực sự đáp ứng contract.

Nếu:

```python
SiteBCrawler.crawl()
```

lại trả:

```text
None
```

trong trường hợp bình thường, trong khi contract yêu cầu `Story`, thì có thể vi phạm LSP.

---

# 42. DDD + DIP

Đây là mối liên hệ quan trọng nhất:

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

Domain/Application định nghĩa abstraction.

Infrastructure implement abstraction.

```text
StoryRepository
       ↑
       │
SQLiteStoryRepository
```

Business logic không phụ thuộc database.

---

# 43. Một ví dụ hoàn chỉnh

### Domain

```python
@dataclass(frozen=True)
class StoryTitle:

    value: str

    def __post_init__(self):

        if not self.value.strip():
            raise ValueError(
                "Empty title"
            )
```

```python
@dataclass
class Story:

    id: int
    title: StoryTitle

    def rename(
        self,
        title: StoryTitle,
    ) -> None:

        self.title = title
```

---

### Repository contract

```python
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

---

### Application

```python
class RenameStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository

    def execute(
        self,
        story_id: int,
        title: StoryTitle,
    ):

        story = self.repository.get_by_id(
            story_id
        )

        if story is None:
            raise ValueError(
                "Story not found"
            )

        story.rename(title)

        self.repository.save(story)
```

---

### Infrastructure

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, story_id):
        ...

    def save(self, story):
        ...
```

Architecture:

```text
CLI
 ↓
RenameStory
 ↓
StoryRepository
 ↑
SQLiteStoryRepository
```

---

# 44. Test

Fake:

```python
class FakeStoryRepository:

    def __init__(self):
        self.stories = {}

    def get_by_id(self, story_id):
        return self.stories.get(story_id)

    def save(self, story):
        self.stories[story.id] = story
```

Test:

```python
def test_rename_story():

    repo = FakeStoryRepository()

    story = Story(
        id=1,
        title=StoryTitle("Old"),
    )

    repo.save(story)

    use_case = RenameStory(repo)

    use_case.execute(
        1,
        StoryTitle("New"),
    )

    result = repo.get_by_id(1)

    assert result.title.value == "New"
```

Không cần SQLite.

---

# 45. Tất cả SOLID đã hội tụ

Nhìn lại:

```text
Story
 │
 ├── SRP
 │
 └── business behavior
```

```text
StoryRepository
 │
 ├── ISP
 ├── DIP
 └── OCP
```

```text
SQLiteStoryRepository
 │
 └── LSP
```

```text
RenameStory
 │
 ├── DIP
 ├── SRP
 └── Testability
```

DDD cung cấp:

```text
Entity
Value Object
Repository
Domain Rule
```

SOLID cung cấp:

```text
responsibility
abstraction
substitution
dependency direction
```

---

# 46. Mental Model quan trọng nhất

Từ giờ khi thiết kế hệ thống, đừng bắt đầu bằng:

> "Tôi cần class nào?"

Hãy bắt đầu bằng:

### Bước 1

```text
Business concept là gì?
```

### Bước 2

```text
Business rule là gì?
```

### Bước 3

```text
Invariant là gì?
```

### Bước 4

```text
Object nào sở hữu behavior?
```

### Bước 5

```text
Use case nào cần thực hiện?
```

### Bước 6

```text
Use case cần dependency nào?
```

### Bước 7

```text
Dependency nào thuộc infrastructure?
```

### Bước 8

```text
Boundary/Protocol nào cần thiết?
```

---

# 47. Công thức thiết kế

Một công thức rất hữu ích:

```text
Business Requirement
        ↓
Domain Rule
        ↓
Entity / Value Object / Domain Service
        ↓
Use Case
        ↓
Port / Protocol
        ↓
Infrastructure Adapter
```

Ví dụ:

```text
"Người dùng không thể đọc chapter chưa publish"
                    ↓
             Domain Rule
                    ↓
               Chapter
                    ↓
          ReadChapterUseCase
                    ↓
          ChapterRepository
                    ↓
       SQLiteChapterRepository
```

---

# 48. Đừng over-engineer

DDD + SOLID rất dễ dẫn tới:

```text
Story
StoryEntity
StoryDTO
StoryModel
StoryDomainModel
StoryRepository
StoryRepositoryImpl
StoryService
StoryDomainService
StoryFactory
StoryMapper
StoryValidator
```

cho một CRUD đơn giản.

Đó **không phải mục tiêu**.

Nếu application chỉ có:

```text
create
read
update
delete
```

thì architecture đơn giản có thể tốt hơn.

DDD phát huy mạnh khi:

```text
business rules phức tạp
nhiều invariant
nhiều use case
nhiều actor
domain thay đổi thường xuyên
```

---

# 49. Khi nào DDD + SOLID đáng dùng?

| Hệ thống                      | Mức độ                  |
| ----------------------------- | ----------------------- |
| Script 100 dòng               | ❌                       |
| CLI nhỏ                       | thường không cần đầy đủ |
| CRUD đơn giản                 | có thể không cần        |
| Desktop app vừa               | ⭐⭐                      |
| Crawler framework             | ⭐⭐⭐⭐                    |
| E-commerce                    | ⭐⭐⭐⭐⭐                   |
| Banking                       | ⭐⭐⭐⭐⭐                   |
| Workflow phức tạp             | ⭐⭐⭐⭐⭐                   |
| Hệ thống nhiều business rules | ⭐⭐⭐⭐⭐                   |

---

# 50. Tổng kết Buổi 15

Ta đã nối:

```text
                 DDD
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Entity      Value      Aggregate
               Object
       │          │          │
       └──────────┼──────────┘
                  ↓
            Domain Rules
                  ↓
            Application
                  ↓
              Protocol
                  ↓
           Infrastructure
```

và SOLID nằm xuyên suốt:

```text
SRP → responsibility
OCP → extension
LSP → substitution
ISP → small contracts
DIP → dependency direction
```

### Câu quan trọng nhất của buổi này:

> **DDD quyết định business model; SOLID giúp tổ chức model và dependency để nó có thể thay đổi mà không phá vỡ hệ thống.**

Và với Python, cách triển khai thường rất tự nhiên:

```text
Entity       → class / dataclass
Value Object → frozen dataclass
Contract     → Protocol
Behavior     → method / function
Use Case     → class
Repository   → Protocol
Infrastructure → concrete implementation
DI           → constructor injection
Testing      → Fake / Stub / Mock
```

---

## Roadmap hoàn thành Phần V

```text
✅ Buổi 12 — SOLID + Design Patterns
✅ Buổi 13 — SOLID + Python
✅ Buổi 14 — SOLID + Testing
✅ Buổi 15 — SOLID + DDD
```

### Phần VI — SOLID trong Clean Architecture

```text
⬜ Buổi 16 — SOLID + Clean Architecture

Entities
Use Cases
Interface Adapters
Frameworks & Drivers

⬜ Buổi 17 — CLI
CLI
 ↓
Application
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository

⬜ Buổi 18 — Crawler
Crawler
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Crawler Plugin

⬜ Buổi 19 — Refactoring
CrawlerManager
 ↓
từng bước refactor
 ↓
Clean Architecture
```

**Buổi 16 sẽ là bước chuyển rất lớn:** chúng ta sẽ không còn học từng nguyên lý SOLID riêng lẻ nữa mà sẽ **đặt chúng vào Clean Architecture**, đặc biệt là 4 vòng `Entities → Use Cases → Interface Adapters → Frameworks & Drivers`, và phân tích chính xác **dependency rule** bằng Python.
