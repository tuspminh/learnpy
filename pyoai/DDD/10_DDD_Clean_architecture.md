# DDD Deep Dive — Buổi 10

# DDD + Clean Architecture

Đây là một buổi **rất quan trọng**, vì từ đây chúng ta sẽ ghép những thứ đã học:

```text
DDD
+
Clean Architecture
+
Dependency Inversion
+
Ports & Adapters
+
Python
```

Mục tiêu cuối buổi:

> Bạn có thể nhìn một hệ thống Python và tự thiết kế được **Domain → Use Case → Port → Adapter → Interface** mà không để framework/database làm ô nhiễm Domain.

---

# 1. Trước tiên: DDD và Clean Architecture không phải một thứ

Đây là điểm cần phân biệt rõ.

## DDD trả lời:

> **Hệ thống cần model business như thế nào?**

DDD quan tâm:

```text
Subdomain
Bounded Context
Entity
Value Object
Aggregate
Domain Event
Domain Service
Ubiquitous Language
Context Map
```

---

## Clean Architecture trả lời:

> **Code nên được tổ chức và phụ thuộc như thế nào?**

Clean Architecture quan tâm:

```text
Dependency Rule
Dependency Inversion
Use Case
Boundary
Interface Adapter
Infrastructure
```

---

# 2. Hai cái bổ sung cho nhau

Có thể hình dung:

```text
DDD
│
├── Business Model
├── Bounded Context
├── Entity
├── Aggregate
└── Domain Rule
          │
          ↓
Clean Architecture
│
├── Dependency Direction
├── Use Case
├── Port
├── Adapter
└── Infrastructure Boundary
```

DDD giúp chúng ta biết:

> **Xây cái gì.**

Clean Architecture giúp chúng ta biết:

> **Đặt nó ở đâu và phụ thuộc thế nào.**

---

# 3. DDD nằm ở đâu trong Clean Architecture?

Câu trả lời ngắn:

> **Domain Model của DDD nằm ở trung tâm Clean Architecture.**

Ví dụ:

```text
        ┌───────────────────────────┐
        │       Interface           │
        │ CLI / API / PySide6       │
        └────────────┬──────────────┘
                     ↓
        ┌───────────────────────────┐
        │       Application         │
        │        Use Cases          │
        └────────────┬──────────────┘
                     ↓
        ┌───────────────────────────┐
        │          Domain           │
        │ Entity / VO / Aggregate   │
        │ Domain Rules / Events      │
        └────────────▲──────────────┘
                     │
        ┌────────────┴──────────────┐
        │      Infrastructure       │
        │ SQLite / HTTP / Redis     │
        └───────────────────────────┘
```

---

# 4. Clean Architecture của Robert C. Martin

Mô hình kinh điển:

```text
          Frameworks & Drivers
                  ↓
        Interface Adapters
                  ↓
          Application
                  ↓
              Entities
```

Nếu diễn đạt theo DDD:

```text
Outer
────────────────────────────
Framework
Database
HTTP
GUI
Redis
────────────────────────────
Adapters
────────────────────────────
Application
Use Cases
────────────────────────────
Domain
Entities
Value Objects
Aggregates
Rules
────────────────────────────
Inner
```

Nguyên tắc:

> **Source code dependencies chỉ hướng vào trong.**

---

# 5. Dependency Rule

Đây là nguyên tắc quan trọng nhất của Clean Architecture:

> **Nothing in an inner circle can know anything about something in an outer circle.**

Nói theo Python:

Domain không được import:

```python
from sqlalchemy import ...
```

Domain không được import:

```python
from PySide6 import ...
```

Domain không được import:

```python
import requests
```

Domain không được import:

```python
import redis
```

---

# 6. Ví dụ sai

```python
from sqlalchemy.orm import DeclarativeBase


class Story(DeclarativeBase):
    ...
```

Nếu `Story` là Domain Entity thì đây là vấn đề.

Tại sao?

Vì Domain bây giờ phụ thuộc:

```text
Domain
   ↓
SQLAlchemy
```

Domain không còn độc lập.

---

# 7. Ví dụ đúng

Domain:

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int
    title: str

    def rename(self, title: str) -> None:
        title = title.strip()

        if not title:
            raise ValueError("Title cannot be empty")

        self.title = title
```

SQLAlchemy model nằm ngoài:

```text
infrastructure/
    persistence/
        models.py
```

---

# 8. Domain Entity ≠ ORM Model

Đây là nguyên tắc rất quan trọng khi học DDD.

Domain:

```python
@dataclass
class Story:
    id: int
    title: str
```

ORM:

```python
class StoryModel(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True)
    title = Column(String)
```

Hai object này có thể đại diện cho cùng dữ liệu nhưng:

> **không nhất thiết phải là cùng một model.**

---

# 9. Mapping

Ta cần mapper:

```text
Domain Entity
     ↕
Persistence Model
```

Ví dụ:

```python
def to_domain(model: StoryModel) -> Story:
    return Story(
        id=model.id,
        title=model.title,
    )
```

và:

```python
def to_model(story: Story) -> StoryModel:
    return StoryModel(
        id=story.id,
        title=story.title,
    )
```

---

# 10. Tại sao phải mapping?

Bởi vì hai thế giới có mục đích khác nhau.

### Domain

Quan tâm:

```text
Business behavior
Invariant
Identity
State
```

### Database

Quan tâm:

```text
Primary key
Foreign key
Index
NULL
Transaction
SQL
```

Nếu ép hai thứ thành một model:

> Persistence concerns dễ xâm nhập Domain.

---

# 11. Ports & Adapters

Đây là một cách nhìn khác của cùng tư tưởng.

Hay còn gọi:

> **Hexagonal Architecture**

Mô hình:

```text
                  Adapter
                     │
                     ↓
              ┌─────────────┐
              │             │
Adapter ─────→│   Domain    │←──── Adapter
              │             │
              └─────────────┘
                     ↑
                   Port
```

Domain/Application ở giữa.

Bên ngoài là:

```text
CLI
GUI
HTTP
Database
Redis
Crawler
Email
```

---

# 12. Port là gì?

Port là:

> **Contract mà hệ thống cung cấp hoặc yêu cầu.**

Có hai loại chính:

```text
Driving Port
Driven Port
```

---

# 13. Driving Port

Driving Port là cổng để bên ngoài **điều khiển hệ thống**.

Ví dụ:

```text
CLI
HTTP API
PySide6
```

gọi:

```text
PublishStory
```

Ta có:

```text
CLI
 ↓
Driving Port
 ↓
Use Case
```

---

# 14. Driven Port

Driven Port là cổng mà Application/Domain **yêu cầu bên ngoài cung cấp khả năng**.

Ví dụ:

```text
StoryRepository
NotificationSender
Crawler
Clock
EventBus
```

Sơ đồ:

```text
Application
    │
    ├──── StoryRepository ────→ Database
    │
    ├──── NotificationSender ─→ Email
    │
    └──── Crawler ────────────→ Crawler Plugin
```

---

# 15. Ví dụ Port

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(self, story_id: int) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...
```

Đây là:

```text
Driven Port
```

---

# 16. Adapter

Adapter là implementation hoặc lớp chuyển đổi để kết nối hệ thống với bên ngoài.

Ví dụ:

```text
StoryRepository
       ↑
       │
SQLiteStoryRepository
```

SQLite Repository là adapter.

---

# 17. Một Adapter khác

```text
NotificationSender
       ↑
       │
TelegramNotificationAdapter
```

Hoặc:

```text
Crawler
   ↑
   │
NovelABCAdapter
```

---

# 18. Ports & Adapters trong hệ thống đọc truyện

Hãy nhìn toàn bộ:

```text
                   ┌─────────────┐
                   │     CLI     │
                   └──────┬──────┘
                          │
                          ↓
                  Driving Adapter
                          │
                          ↓
                    ┌───────────┐
                    │ Use Case  │
                    └─────┬─────┘
                          │
              ┌───────────┼───────────┐
              ↓           ↓           ↓
           StoryRepo   Crawler    EventBus
              ↑           ↑           ↑
              │           │           │
           SQLite      Plugin       Redis
```

---

# 19. Một cách hiểu cực kỳ dễ nhớ

### Driving side

```text
Bên ngoài
   ↓
Hệ thống
```

Ví dụ:

```text
CLI
API
GUI
```

### Driven side

```text
Hệ thống
   ↓
Bên ngoài
```

Ví dụ:

```text
Database
Email
Redis
External API
```

---

# 20. Use Case nằm ở đâu?

Use Case thuộc:

```text
Application Layer
```

Ví dụ:

```python
class PublishStory:
    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, story_id: int):
        story = self.repository.get(story_id)

        if story is None:
            raise StoryNotFound(story_id)

        story.publish()

        self.repository.save(story)
```

Use Case:

```text
không chứa SQL
không chứa HTTP
không chứa PySide6
```

---

# 21. Use Case không phải Domain Service

Hai khái niệm rất dễ nhầm.

## Application Use Case

Điều phối:

```text
Load
 ↓
Call domain
 ↓
Save
 ↓
Publish event
```

## Domain Service

Chứa business logic không thuộc tự nhiên về một Entity.

Ví dụ:

```python
class ReadingProgressPolicy:
    def can_mark_completed(
        self,
        current_page: int,
        total_pages: int,
    ) -> bool:
        return current_page >= total_pages
```

---

# 22. Domain Service không gọi database

Không nên:

```python
class StoryDomainService:

    def __init__(self, sqlite):
        self.sqlite = sqlite
```

Domain Service không nên biết:

```text
SQLite
HTTP
Redis
```

Nếu cần external dependency, phải xem lại boundary và abstraction.

---

# 23. Clean Architecture + DDD

Một cấu trúc rất hợp lý:

```text
src/
└── catalog/
    │
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── aggregates/
    │   ├── services/
    │   ├── events/
    │   └── repositories/
    │
    ├── application/
    │   ├── commands/
    │   ├── queries/
    │   ├── ports/
    │   └── services/
    │
    ├── infrastructure/
    │   ├── persistence/
    │   ├── messaging/
    │   ├── external/
    │   └── adapters/
    │
    └── interface/
        ├── cli/
        ├── api/
        └── gui/
```

---

# 24. Nhưng có một nuance

Không có một "folder structure chuẩn DDD" duy nhất.

Bạn có thể đặt:

```text
StoryRepository
```

ở:

```text
domain/repositories.py
```

hoặc:

```text
application/ports/
```

tùy vào việc repository phục vụ Domain hay Application.

Điều quan trọng không phải tên folder.

Điều quan trọng là:

> **Dependency direction và boundary.**

---

# 25. Thiết kế hệ thống đọc truyện

Chúng ta đã xác định các Context:

```text
Crawling
Catalog
Reading
User
Notification
```

Mỗi Context có architecture riêng.

Ví dụ:

```text
src/
├── crawling/
├── catalog/
├── reading/
├── user/
└── notification/
```

---

# 26. Catalog Context

```text
catalog/
│
├── domain/
│   ├── entities/
│   │   └── story.py
│   ├── value_objects/
│   │   ├── story_id.py
│   │   └── story_title.py
│   ├── events/
│   │   └── story_published.py
│   └── repositories/
│       └── story_repository.py
│
├── application/
│   ├── commands/
│   │   └── publish_story.py
│   └── queries/
│       └── get_story.py
│
├── infrastructure/
│   └── persistence/
│       └── sqlite_story_repository.py
│
└── interface/
    ├── cli/
    └── api/
```

---

# 27. Crawling Context

```text
crawling/
│
├── domain/
│   ├── entities/
│   │   └── crawl_job.py
│   ├── value_objects/
│   └── repositories/
│
├── application/
│   ├── commands/
│   │   └── crawl_story.py
│   └── ports/
│       └── crawler.py
│
├── infrastructure/
│   └── crawlers/
│       ├── novel_abc.py
│       └── novel_xyz.py
│
└── interface/
    └── cli/
```

---

# 28. Crawler Plugin

Application định nghĩa:

```python
from typing import Protocol


class Crawler(Protocol):

    def crawl(self, url: str) -> CrawlResult:
        ...
```

Plugin:

```python
class NovelABCPlugin:

    def crawl(self, url: str) -> CrawlResult:
        ...
```

Dependency:

```text
Application
     ↓
Crawler Protocol
     ↑
NovelABCPlugin
```

Đây chính là DIP.

---

# 29. Context Communication

Crawling không import trực tiếp:

```python
from catalog.domain.entities import Story
```

Đây là boundary violation.

Thay vào đó:

```text
Crawling
    │
    │ Published Event
    ↓
Catalog
```

Ví dụ:

```python
@dataclass(frozen=True)
class ChapterDiscovered:
    source_id: str
    external_story_id: str
    external_chapter_id: str
    title: str
    url: str
```

---

# 30. Tại sao không dùng chung `Story`?

Vì:

```text
Crawling Story
```

có thể có ý nghĩa:

> Story trên website nguồn.

Trong Catalog:

> Story đã được hệ thống quản lý.

Trong Reading:

> Story mà người dùng đang đọc.

Cùng tên:

```text
Story
```

nhưng khác meaning.

Đây chính là bài học từ **Bounded Context**.

---

# 31. Domain Event làm cầu nối

Ví dụ:

```text
Crawling Context
       │
       │ ChapterDiscovered
       ↓
Catalog Context
       │
       │ ChapterPublished
       ↓
Notification Context
```

Mỗi Context có model riêng.

```text
Không shared Entity
```

nhưng:

```text
Shared Contract
```

---

# 32. Context Map + Clean Architecture

Bây giờ ghép hai tầng:

```text
                SYSTEM
                   │
     ┌─────────────┼─────────────┐
     ↓             ↓             ↓
 Crawling       Catalog       Reading
 Context        Context        Context
     │             │             │
     │             │             │
   Domain        Domain        Domain
     │             │             │
 Application    Application   Application
     │             │             │
Infrastructure Infrastructure Infrastructure
```

Communication giữa Context:

```text
Context A
    │
    │ Port / Event / API
    ↓
Context B
```

---

# 33. Đây mới là kiến trúc DDD hoàn chỉnh

Bạn không chỉ có:

```text
Entity
```

mà có:

```text
Strategic DDD
    ↓
Bounded Context
    ↓
Context Map
    ↓
Tactical DDD
    ↓
Entity / Aggregate / VO
    ↓
Clean Architecture
    ↓
Ports / Adapters
    ↓
Infrastructure
```

---

# 34. Dependency Graph hoàn chỉnh

```text
                  ┌─────────────┐
                  │     CLI     │
                  └──────┬──────┘
                         ↓
                  ┌─────────────┐
                  │  Use Case   │
                  └──────┬──────┘
                         ↓
              ┌─────────────────────┐
              │       Domain        │
              │ Entity / Aggregate  │
              │ VO / Rules / Events │
              └─────────▲───────────┘
                        │
                 implements
                        │
              ┌─────────┴───────────┐
              │   Infrastructure    │
              │ SQLite / HTTP / etc │
              └─────────────────────┘
```

---

# 35. Composition Root

Bây giờ chúng ta hoàn thiện wiring:

```python
connection = create_connection()

repository = SQLiteStoryRepository(
    connection
)

publish_story = PublishStory(
    repository
)

cli = StoryCLI(
    publish_story
)
```

Dependency được lắp ở ngoài cùng.

Domain không biết wiring.

---

# 36. Dependency Injection không phải Framework

Đừng nghĩ phải dùng:

```text
FastAPI DI
Dependency Injector
Dishka
```

mới gọi là Dependency Injection.

Python thuần:

```python
service = PublishStory(repository)
```

đã là Dependency Injection.

---

# 37. Test Architecture

Một ưu điểm cực lớn.

## Domain test

```python
def test_story_can_publish():
    story = Story(
        id=1,
        title="One Piece",
    )

    story.publish()

    assert story.published
```

Không cần:

```text
SQLite
PySide6
HTTP
```

---

# 38. Application test

```python
repository = InMemoryStoryRepository()

story = Story(
    id=1,
    title="One Piece",
)

repository.save(story)

use_case = PublishStory(repository)

use_case.execute(1)

assert story.published
```

Không cần database thật.

---

# 39. Infrastructure test

Lúc này mới test:

```text
SQLiteStoryRepository
```

với SQLite.

Tức là:

```text
Domain tests
    ↓
Application tests
    ↓
Infrastructure tests
    ↓
Integration tests
```

Mỗi layer test đúng responsibility.

---

# 40. Một nguyên tắc rất quan trọng

> **Không phải mọi class đều cần interface.**

Sai lầm phổ biến:

```text
IStoryService
IStoryMapper
IStoryValidator
IStoryFactory
IStoryRepository
IStoryManager
IStoryProvider
```

Mọi thứ đều interface.

DDD/Clean Architecture không yêu cầu như vậy.

Hãy tạo abstraction khi:

```text
Có boundary
Có dependency cần đảo chiều
Có nhiều implementation
Có external system
Có lý do testing
```

---

# 41. Khi nào nên tạo Port?

Ví dụ:

```text
Database
External API
Crawler
Message Broker
Clock
File System
Email
```

Đây thường là nơi abstraction rất hữu ích.

---

# 42. Khi nào không cần Port?

Ví dụ:

```python
class StoryTitle:
    ...
```

Không cần:

```text
IStoryTitle
```

hoặc:

```python
class StoryFactory:
    ...
```

không nhất thiết phải có:

```text
IStoryFactory
```

---

# 43. Clean Architecture không phải nhiều layer

Một hiểu nhầm:

> "Clean Architecture = càng nhiều layer càng tốt."

Không.

Một project nhỏ có thể chỉ cần:

```text
domain/
application/
infrastructure/
```

Một CLI đơn giản thậm chí có thể:

```text
domain/
application/
cli/
```

Architecture phải phù hợp complexity.

---

# 44. DDD cũng không phải "mọi project đều phải Aggregate"

Nếu application chỉ:

```text
CRUD đơn giản
```

thì không cần cố tạo:

```text
Aggregate
Domain Event
Domain Service
Repository
Factory
Specification
```

DDD nên được áp dụng mạnh ở:

> **Core Domain có business complexity.**

---

# 45. Đây là lý do Subdomain quan trọng

Buổi 6 chúng ta đã học:

```text
Core
Supporting
Generic
```

Core Domain:

```text
DDD sâu
Architecture nghiêm
```

Generic:

```text
Không cần over-engineer
```

Ví dụ:

```text
Authentication
```

có thể dùng library.

Trong khi:

```text
Crawler orchestration
Story ingestion
Reading progress
```

có thể là business-specific.

---

# 46. Một project Python thực tế

Ví dụ:

```text
story-reader/
│
├── pyproject.toml
│
├── src/
│   └── story_reader/
│       │
│       ├── crawling/
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── interface/
│       │
│       ├── catalog/
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── interface/
│       │
│       ├── reading/
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── interface/
│       │
│       └── notification/
│           ├── domain/
│           ├── application/
│           ├── infrastructure/
│           └── interface/
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

# 47. Tư duy kiến trúc cuối cùng

Khi thiết kế một feature mới, đừng bắt đầu bằng:

> "Tôi cần tạo file nào?"

Hãy hỏi:

### Câu 1

```text
Business concept là gì?
```

### Câu 2

```text
Nó thuộc Bounded Context nào?
```

### Câu 3

```text
Business rule nằm ở đâu?
```

### Câu 4

```text
Use Case là gì?
```

### Câu 5

```text
Use Case cần external dependency nào?
```

### Câu 6

```text
Port nào cần được định nghĩa?
```

### Câu 7

```text
Adapter nào implement Port?
```

### Câu 8

```text
Interface nào gọi Use Case?
```

Đây là tư duy thiết kế thay vì tư duy tạo file.

---

# 48. Case Study: `PublishStory`

Hãy đi từ business xuống code.

### Business

> Một Story chỉ được publish nếu có title.

↓

### Domain

```python
story.publish()
```

↓

### Application

```python
PublishStory.execute(story_id)
```

↓

### Port

```python
StoryRepository
```

↓

### Adapter

```python
SQLiteStoryRepository
```

↓

### Interface

```text
CLI
PySide6
FastAPI
```

↓

### Composition Root

```python
repository = SQLiteStoryRepository(...)
use_case = PublishStory(repository)
```

---

# 49. Sơ đồ hoàn chỉnh

```text
                        USER
                         │
                         ↓
                 ┌──────────────┐
                 │ CLI / GUI/API│
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │   Use Case   │
                 │ PublishStory │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │    Domain    │
                 │    Story     │
                 └──────┬───────┘
                        │
                        │ Port
                        ↓
                 ┌──────────────┐
                 │ Repository   │
                 │  Interface   │
                 └──────▲───────┘
                        │
                     Adapter
                        │
                        ↓
                 ┌──────────────┐
                 │    SQLite    │
                 └──────────────┘
```

Đây là kiến trúc mà bạn cần có thể **tự vẽ từ đầu** sau khi hoàn thành phần này.

---

# 50. Tổng kết Phần Strategic DDD

Chúng ta đã hoàn thành:

```text
Buổi 6 — Subdomain
        ↓
Core / Supporting / Generic

Buổi 7 — Bounded Context
        ↓
Boundary + Ubiquitous Language

Buổi 8 — Context Mapping
        ↓
Relationship giữa Context

Buổi 9 — Domain Architecture
        ↓
Domain / Application / Infrastructure / Interface

Buổi 10 — DDD + Clean Architecture
        ↓
Ports / Adapters / Dependency Rule
```

Bạn có thể ghi nhớ toàn bộ bằng chuỗi:

```text
BUSINESS
   ↓
SUBDOMAIN
   ↓
BOUNDED CONTEXT
   ↓
CONTEXT MAP
   ↓
DOMAIN MODEL
   ↓
USE CASE
   ↓
PORT
   ↓
ADAPTER
   ↓
INFRASTRUCTURE
   ↓
INTERFACE
```

---

# Bài tập tổng kết

Hãy thiết kế feature:

> **"Crawler phát hiện chapter mới → Catalog lưu chapter → Notification gửi thông báo."**

Bạn cần tự xác định:

```text
1. Bounded Context nào tham gia?

2. Context nào Upstream / Downstream?

3. Published Language là gì?

4. Domain Event là gì?

5. Use Case nào?

6. Port nào?

7. Adapter nào?

8. Domain Entity nào?

9. Infrastructure nào?

10. Dependency graph ra sao?
```

Nếu làm đúng bài này, bạn đã bắt đầu chuyển từ **học thuật DDD** sang **thiết kế hệ thống Python thực tế**.

### Roadmap tiếp theo

Sau Buổi 10, phần tiếp theo nên đi sâu vào **Tactical DDD**:

```text
Buổi 11 — Entity Deep Dive
Buổi 12 — Value Object Deep Dive
Buổi 13 — Aggregate
Buổi 14 — Aggregate Boundary
Buổi 15 — Aggregate Root
Buổi 16 — Repository trong DDD
Buổi 17 — Domain Service
Buổi 18 — Domain Event
Buổi 19 — Factory
Buổi 20 — Specification
...
```

Đặc biệt, **Aggregate → Aggregate Root → Repository → Domain Event** sẽ là chuỗi rất quan trọng trước khi chúng ta xây project Python DDD hoàn chỉnh.
