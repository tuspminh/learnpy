# DDD Deep Dive — Buổi 9

# Domain Architecture

Ở Buổi 8 chúng ta đã có:

```text
Domain
   ↓
Subdomain
   ↓
Bounded Context
   ↓
Context Map
```

Bây giờ chuyển sang câu hỏi:

> **Sau khi đã xác định boundary, chúng ta tổ chức code như thế nào?**

Hôm nay học:

```text
Buổi 9 — Domain Architecture
├── Domain Layer
├── Application Layer
├── Infrastructure Layer
├── Interface Layer
├── Dependency Direction
└── Dependency Inversion
```

---

# 1. Domain Architecture là gì?

Domain Architecture là cách chúng ta tổ chức hệ thống sao cho:

> **Business rules nằm ở trung tâm và không bị phụ thuộc vào framework, database, UI hay external service.**

Hãy hình dung:

```text
                 DOMAIN
                   │
            Business Rules
                   │
        ┌──────────┴──────────┐
        │                     │
   Application          Infrastructure
        │                     │
        └──────────┬──────────┘
                   │
               Interface
```

Nhưng sơ đồ này mới chỉ là hình thức.

Điều quan trọng nhất là:

> **Dependency phải đi theo đúng hướng.**

---

# 2. Bốn Layer

Trong roadmap của chúng ta:

```text
┌───────────────────────────────┐
│       Interface Layer         │
│ CLI / API / PySide6 / Flet   │
├───────────────────────────────┤
│      Infrastructure Layer     │
│ SQLite / HTTP / File / Redis │
├───────────────────────────────┤
│       Application Layer       │
│ Use Cases / Orchestration     │
├───────────────────────────────┤
│          Domain Layer         │
│ Entity / VO / Rule / Service  │
└───────────────────────────────┘
```

Nhưng đừng hiểu đơn giản:

> "Layer trên gọi layer dưới."

DDD/Clean Architecture quan trọng hơn ở **dependency direction**.

---

# 3. Domain Layer

Domain Layer là trái tim của hệ thống.

Nó chứa:

```text
Entity
Value Object
Aggregate
Domain Service
Domain Rule
Domain Event
Repository Interface
```

Ví dụ hệ thống đọc truyện:

```text
domain/
├── story.py
├── chapter.py
├── value_objects.py
├── rules.py
└── repositories.py
```

---

# 4. Domain không nên biết framework

Ví dụ Domain:

```python
from sqlalchemy import Column
```

hoặc:

```python
from PySide6.QtCore import QObject
```

hoặc:

```python
import fastapi
```

là dấu hiệu không tốt.

Domain nên có thể chạy:

```python
story.publish()
```

mà không cần:

```text
SQLite
FastAPI
PySide6
Redis
HTTP
```

---

# 5. Ví dụ Domain Entity

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int
    title: str
    published: bool = False

    def publish(self) -> None:
        if not self.title.strip():
            raise ValueError("Story must have a title")

        self.published = True
```

Đây là Domain Model.

Không có:

```text
SQLite
ORM
HTTP
UI
```

---

# 6. Domain chứa Business Rule

Ví dụ:

> Không được publish Story không có title.

Rule này thuộc:

```text
Domain
```

không thuộc:

```text
UI
Database
API
```

Sai:

```python
def publish_story(story):
    if not story.title:
        show_error("Title required")
```

UI đang biết business rule.

Đúng:

```python
story.publish()
```

và Domain tự bảo vệ invariant.

---

# 7. Domain Layer không phải "data model"

Một lỗi phổ biến:

```python
@dataclass
class Story:
    id: int
    title: str
    author: str
```

rồi mọi logic:

```text
service.py
```

Domain trở thành:

> Anemic Domain Model.

DDD muốn behavior nằm gần data/business concept khi phù hợp.

Ví dụ:

```python
story.rename("One Piece")
story.publish()
story.add_genre("Adventure")
```

thay vì:

```python
story_service.rename(story, ...)
story_service.publish(story)
story_service.add_genre(story, ...)
```

---

# 8. Repository Interface thuộc Domain

Đây là điểm rất quan trọng.

Nhiều người nghĩ:

```text
Repository = Infrastructure
```

Không hoàn toàn.

**Repository implementation** thuộc Infrastructure.

Nhưng:

**Repository abstraction/interface** có thể thuộc Domain.

Ví dụ:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id: int) -> Story | None:
        ...

    @abstractmethod
    def save(self, story: Story) -> None:
        ...
```

Domain nói:

> Tôi cần khả năng lưu Story.

Domain không nói:

> Hãy lưu bằng SQLite.

---

# 9. Infrastructure Layer

Infrastructure chứa implementation cụ thể.

Ví dụ:

```text
infrastructure/
├── sqlite/
│   └── story_repository.py
├── http/
│   └── crawler_client.py
├── filesystem/
│   └── file_storage.py
└── messaging/
    └── event_bus.py
```

Infrastructure biết:

```text
SQLite
HTTP
Redis
Filesystem
External API
```

---

# 10. SQLite Repository

Domain:

```python
class StoryRepository(ABC):
    ...
```

Infrastructure:

```python
class SQLiteStoryRepository(StoryRepository):

    def __init__(self, connection):
        self.connection = connection

    def get(self, story_id: int):
        ...
    
    def save(self, story):
        ...
```

Ta có:

```text
Domain
   ↑
   │ implements
   │
SQLite Repository
```

---

# 11. Application Layer

Application Layer chứa:

> **Use Case / Application Service**

Nó điều phối Domain.

Ví dụ:

```text
application/
├── commands/
│   ├── publish_story.py
│   └── create_story.py
└── queries/
    └── get_story.py
```

---

# 12. Application không phải Domain

Ví dụ:

> "Publish Story"

Use Case:

```python
class PublishStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id: int):
        story = self.repository.get(story_id)

        if story is None:
            raise ValueError("Story not found")

        story.publish()

        self.repository.save(story)
```

Application đang:

```text
Load
 ↓
Call domain behavior
 ↓
Save
```

Đây là orchestration.

---

# 13. Domain quyết định "được phép hay không"

Application:

```python
story.publish()
```

Domain:

```python
def publish(self):
    if not self.title:
        raise InvalidStory(...)
```

Domain quyết định:

> Có được publish không?

Application quyết định:

> Khi publish thì cần gọi những bước nào?

---

# 14. Đây là distinction cực kỳ quan trọng

### Domain

```text
Business rule
```

### Application

```text
Use case orchestration
```

Ví dụ:

```text
Application:
    tìm Story
        ↓
    gọi publish()
        ↓
    lưu Story
```

Trong khi:

```text
Domain:
    Story có title?
        ↓
    Có → publish
    Không → reject
```

---

# 15. Interface Layer

Interface Layer là nơi hệ thống giao tiếp với bên ngoài.

Ví dụ:

```text
interface/
├── cli/
├── api/
├── gui/
└── workers/
```

Trong project của bạn có thể:

```text
CLI
PySide6
Flet
FastAPI
```

---

# 16. Ví dụ CLI

```python
def publish_command(story_id: int):
    use_case.execute(story_id)
```

CLI không nên:

```python
if not story.title:
    ...
```

vì đây là business rule.

CLI chỉ:

```text
Input
 ↓
Use Case
 ↓
Output
```

---

# 17. PySide6 cũng là Interface Layer

Ví dụ:

```text
PySide6
   ↓
PublishStory.execute()
```

UI không nên trực tiếp:

```text
SQLite
```

và cũng không nên tự implement:

```text
business rules
```

---

# 18. Dependency Direction

Đây là phần quan trọng nhất Buổi 9.

Giả sử:

```text
Interface
    ↓
Application
    ↓
Domain
```

Nhìn thì đơn giản.

Nhưng:

```text
Application
```

cần Repository.

Repository implementation nằm:

```text
Infrastructure
```

Nếu Application import trực tiếp:

```python
from infrastructure.sqlite import SQLiteStoryRepository
```

thì:

```text
Application
    ↓
Infrastructure
```

Domain Architecture bắt đầu bị đảo ngược.

---

# 19. Dependency Inversion

Thay vì:

```text
Application
    ↓
SQLite
```

Ta muốn:

```text
Application
    ↓
Repository Interface
    ↑
SQLite Repository
```

Đây chính là:

> **Dependency Inversion Principle.**

---

# 20. Hình dung

```text
                 Application
                      │
                      │ depends on
                      ↓
              StoryRepository
                 (interface)
                      ↑
                      │ implements
                      │
             SQLiteStoryRepository
```

Application không biết SQLite.

---

# 21. Code

Domain:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def get(self, story_id: int):
        ...

    @abstractmethod
    def save(self, story):
        ...
```

Application:

```python
class PublishStory:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, story_id: int):
        story = self.repository.get(story_id)

        if story is None:
            raise ValueError("Story not found")

        story.publish()
        self.repository.save(story)
```

Infrastructure:

```python
class SQLiteStoryRepository(StoryRepository):

    def get(self, story_id: int):
        ...

    def save(self, story):
        ...
```

---

# 22. Dependency Graph

Ta có:

```text
PySide6
   │
   ↓
PublishStory
   │
   ↓
StoryRepository
   ↑
   │
SQLiteStoryRepository
```

Đây là kiến trúc rất tốt.

---

# 23. Tại sao Interface ở phía Domain?

Vì Domain/Application nói:

> "Tôi cần một StoryRepository."

Infrastructure trả lời:

> "Tôi có SQLiteStoryRepository."

Đây chính là Dependency Inversion.

---

# 24. Không phải Interface = Python ABC

Một nuance quan trọng.

Trong DDD/Clean Architecture, "interface" ở đây là:

> **Abstraction / Port**

Không nhất thiết phải là:

```python
ABC
```

Có thể dùng:

```python
Protocol
```

Ví dụ Python hiện đại:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(self, story_id: int) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...
```

---

# 25. ABC vs Protocol

### ABC

```python
class StoryRepository(ABC):
    ...
```

Implementation phải:

```python
class SQLiteStoryRepository(StoryRepository):
    ...
```

### Protocol

```python
class StoryRepository(Protocol):
    ...
```

Class không cần kế thừa trực tiếp:

```python
class SQLiteStoryRepository:
    def get(...):
        ...

    def save(...):
        ...
```

Python kiểm tra theo structural typing.

---

# 26. Application Layer cũng có Port

Không chỉ Repository.

Ví dụ crawler cần:

```text
CrawlerPort
```

Domain/Application:

```python
class Crawler(Protocol):

    def crawl(self, url: str) -> CrawlResult:
        ...
```

Infrastructure:

```python
class NovelCrawler:
    def crawl(self, url):
        ...
```

---

# 27. External Service

Ví dụ Notification:

```python
class NotificationSender(Protocol):

    def send(self, message: str) -> None:
        ...
```

Infrastructure:

```python
class TelegramNotificationSender:
    ...
```

hoặc:

```python
class EmailNotificationSender:
    ...
```

Application không biết:

```text
Telegram
SMTP
HTTP
```

---

# 28. Domain Architecture thực tế

Một Context có thể:

```text
context/
│
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── events/
│   └── repositories.py
│
├── application/
│   ├── commands/
│   ├── queries/
│   └── services/
│
├── infrastructure/
│   ├── persistence/
│   ├── http/
│   └── messaging/
│
└── interface/
    ├── cli/
    ├── api/
    └── gui/
```

---

# 29. Dependency Rule

Quy tắc cốt lõi:

> **Dependency phải hướng vào trong, về phía Domain.**

Ví dụ:

```text
┌─────────────────────────────┐
│        Interface            │
│ CLI / API / PySide6         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       Application           │
│ Use Cases                   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│          Domain             │
│ Entities / Rules / Ports    │
└─────────────────────────────┘

Infrastructure
       ↑
       │ implements ports
       │
     Domain
```

---

# 30. Infrastructure nằm "ngoài" Domain

Một cách hình dung khác:

```text
             ┌───────────────────────┐
             │     Interface         │
             │                       │
             │ CLI / GUI / API       │
             └───────────┬───────────┘
                         │
                         ↓
             ┌───────────────────────┐
             │    Application        │
             │                       │
             │      Use Cases        │
             └───────────┬───────────┘
                         │
                         ↓
             ┌───────────────────────┐
             │       Domain          │
             │                       │
             │ Entity / Rule / Port  │
             └───────────▲───────────┘
                         │
                         │ implements
             ┌───────────┴───────────┐
             │    Infrastructure     │
             │                       │
             │ SQLite / HTTP / Redis │
             └───────────────────────┘
```

---

# 31. Tại sao Domain phải độc lập?

Vì business logic có thể tồn tại lâu hơn technology.

Hôm nay:

```text
SQLite
```

Ngày mai:

```text
PostgreSQL
```

Ngày kia:

```text
MongoDB
```

Domain không nên phải viết lại:

```python
class Story:
    ...
```

---

# 32. Tương tự với UI

Hôm nay:

```text
PySide6
```

Ngày mai:

```text
FastAPI
```

hoặc:

```text
CLI
```

Business rule vẫn:

```python
story.publish()
```

Không thay đổi.

---

# 33. Đây là lý do chúng ta tách Application

Giả sử có:

```text
CLI
PySide6
FastAPI
```

Cả ba đều cần:

```text
PublishStory
```

Ta không muốn:

```text
CLI → Domain
PySide6 → Domain
FastAPI → Domain
```

và mỗi interface tự orchestration khác nhau.

Thay vào đó:

```text
CLI ────────┐
PySide6 ────┼──→ Application
FastAPI ────┘
                 ↓
               Domain
```

Use Case được tái sử dụng.

---

# 34. Ví dụ hoàn chỉnh

## Domain

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int
    title: str
    published: bool = False

    def publish(self) -> None:
        if not self.title.strip():
            raise ValueError("Title is required")

        if self.published:
            raise ValueError("Story already published")

        self.published = True
```

Repository port:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(self, story_id: int) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...
```

---

# 35. Application

```python
class PublishStory:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, story_id: int) -> None:
        story = self.repository.get(story_id)

        if story is None:
            raise ValueError("Story not found")

        story.publish()

        self.repository.save(story)
```

Application không biết:

```text
SQLite
```

---

# 36. Infrastructure

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def get(self, story_id: int):
        ...

    def save(self, story):
        ...
```

Infrastructure chịu trách nhiệm:

```text
SQL
connection
mapping
transaction
```

---

# 37. Interface

CLI:

```python
def publish_command(story_id: int):
    use_case.execute(story_id)
```

PySide6:

```python
def on_publish_clicked():
    use_case.execute(story_id)
```

FastAPI:

```python
@app.post("/stories/{story_id}/publish")
def publish_story(story_id: int):
    use_case.execute(story_id)
```

Ba interface:

```text
CLI
PySide6
FastAPI
```

cùng gọi:

```text
PublishStory
```

---

# 38. Composition Root

Một khái niệm quan trọng tiếp theo.

Ai tạo implementation?

Ví dụ:

```python
repository = SQLiteStoryRepository(connection)

use_case = PublishStory(repository)
```

Nơi wiring dependency này thường được gọi là:

> **Composition Root**

Ví dụ:

```text
main.py
```

hoặc:

```text
bootstrap.py
```

---

# 39. Composition Root

```text
                Composition Root
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
SQLiteRepository              PublishStory
          │                         │
          └─────────────→───────────┘
```

Application không tự tạo:

```python
SQLiteStoryRepository(...)
```

Đây là nguyên tắc cực kỳ quan trọng.

---

# 40. Code xấu

```python
class PublishStory:

    def execute(self, story_id):
        repository = SQLiteStoryRepository()
        story = repository.get(story_id)
        ...
```

Bây giờ Application bị khóa vào:

```text
SQLite
```

Test cũng khó.

---

# 41. Code tốt

```python
class PublishStory:

    def __init__(self, repository):
        self.repository = repository
```

Composition Root:

```python
repository = SQLiteStoryRepository(connection)

use_case = PublishStory(repository)
```

Dependency được inject từ bên ngoài.

---

# 42. Testing trở nên dễ

Fake repository:

```python
class InMemoryStoryRepository:

    def __init__(self):
        self.items = {}

    def get(self, story_id):
        return self.items.get(story_id)

    def save(self, story):
        self.items[story.id] = story
```

Test:

```python
repository = InMemoryStoryRepository()

story = Story(
    id=1,
    title="One Piece",
)

repository.save(story)

use_case = PublishStory(repository)

use_case.execute(1)

assert story.published is True
```

Không cần SQLite.

---

# 43. Đây là sức mạnh của Dependency Inversion

```text
Production
    ↓
SQLiteRepository

Test
    ↓
InMemoryRepository

Development
    ↓
FakeRepository
```

Application không thay đổi.

---

# 44. Domain Architecture và SOLID

Bạn đã học SOLID trước đó, nên có thể kết nối:

### SRP

```text
Entity
Use Case
Repository
Adapter
```

mỗi thứ có responsibility riêng.

### OCP

Có thể thêm:

```text
PostgresRepository
```

mà không sửa Use Case.

### DIP

```text
Use Case
    ↓
Repository abstraction
    ↑
SQLiteRepository
```

Đây chính là DIP.

---

# 45. Domain Architecture và DDD

DDD cung cấp:

```text
Entity
Value Object
Aggregate
Domain Service
Repository
Domain Event
Bounded Context
```

Architecture cung cấp:

```text
Domain Layer
Application Layer
Infrastructure
Interface
Dependency Direction
```

Chúng hỗ trợ nhau.

---

# 46. Một nhầm lẫn phổ biến

> "DDD = chia folder domain/application/infrastructure."

Không.

Bạn có thể có:

```text
domain/
application/
infrastructure/
```

nhưng nếu:

```text
domain
```

chỉ chứa:

```text
SQLAlchemy Models
```

thì đó không phải Domain Model đúng nghĩa.

DDD bắt đầu từ:

```text
Business
```

sau đó mới đến:

```text
Architecture
```

---

# 47. Project Python cho hệ thống đọc truyện

Một Context:

```text
src/
└── catalog/
    ├── domain/
    │   ├── entities/
    │   │   └── story.py
    │   ├── value_objects/
    │   ├── services/
    │   ├── events/
    │   └── repositories.py
    │
    ├── application/
    │   ├── commands/
    │   │   ├── create_story.py
    │   │   └── publish_story.py
    │   └── queries/
    │       └── get_story.py
    │
    ├── infrastructure/
    │   ├── persistence/
    │   │   └── sqlite_story_repository.py
    │   └── external/
    │
    └── interface/
        ├── cli/
        └── api/
```

Đây là **một Bounded Context** có cấu trúc bên trong.

---

# 48. Toàn hệ thống

Sau này có thể:

```text
src/
└── app/
    │
    ├── crawling/
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── interface/
    │
    ├── catalog/
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── interface/
    │
    ├── reading/
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── interface/
    │
    └── user/
        ├── domain/
        ├── application/
        ├── infrastructure/
        └── interface/
```

Đây là:

> **DDD + Modular Architecture**

---

# 49. Một nguyên tắc rất quan trọng

Đừng tổ chức project kiểu:

```text
src/
├── models/
├── services/
├── repositories/
├── controllers/
└── utils/
```

cho toàn bộ hệ thống nếu bạn muốn boundary theo DDD.

Vì lúc đó:

```text
models/
```

chứa model của tất cả context:

```text
Story
User
Chapter
CrawlerJob
ReadingProgress
```

và boundary rất dễ bị phá vỡ.

---

# 50. Tổ chức theo Bounded Context trước

Tốt hơn:

```text
src/
├── crawling/
├── catalog/
├── reading/
└── user/
```

Sau đó bên trong mỗi Context:

```text
domain/
application/
infrastructure/
interface/
```

Đây gọi là:

> **Package by Feature / Package by Context**

thay vì:

> Package by Technical Layer toàn hệ thống.

---

# 51. Architecture cuối cùng

Hãy ghi nhớ mô hình này:

```text
                    SYSTEM
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    Crawling         Catalog        Reading
    Context          Context        Context
        │              │              │
        ├─ domain      ├─ domain      ├─ domain
        ├─ application ├─ application ├─ application
        ├─ infra       ├─ infra       ├─ infra
        └─ interface   └─ interface   └─ interface
```

Mỗi Context là một mini domain system.

---

# 52. Bài tập Buổi 9

## Bài 1 — Dependency

Cho:

```text
PySide6
SQLite
PublishStory
Story
StoryRepository
```

Hãy vẽ dependency graph.

Mục tiêu:

```text
PySide6
    ↓
PublishStory
    ↓
StoryRepository
    ↑
SQLiteRepository
```

---

## Bài 2 — Phân loại

Cho các class:

```text
Story
PublishStory
SQLiteStoryRepository
StoryRepository
PublishStoryCommand
StoryView
```

Hãy xác định:

```text
Domain
Application
Infrastructure
Interface
```

---

## Bài 3 — Tìm lỗi kiến trúc

Đoạn code:

```python
class PublishStory:

    def execute(self, story_id):
        repo = SQLiteStoryRepository()
        story = repo.get(story_id)

        if not story.title:
            return False

        story.published = True
        repo.save(story)

        return True
```

Có ít nhất **4 vấn đề kiến trúc**.

Hãy tìm chúng.

Gợi ý:

```text
DIP
Business Rule
Entity Behavior
Infrastructure Coupling
```

---

## Bài 4 — Refactoring

Refactor thành:

```text
Story
StoryRepository
PublishStory
SQLiteStoryRepository
CLI
```

với dependency:

```text
CLI
 ↓
PublishStory
 ↓
StoryRepository
 ↑
SQLiteStoryRepository
```

---

# 53. Bài tập nâng cao

Hãy thiết kế structure cho:

> **Crawling Context**

Yêu cầu:

```text
CrawlerJob
CrawlerPlugin
Source
CrawlResult
```

và:

```text
CrawlerPlugin
```

phải có thể thay đổi implementation:

```text
NovelABCPlugin
NovelXYZPlugin
```

mà Application không cần biết implementation cụ thể.

Gợi ý architecture:

```text
crawling/
├── domain/
├── application/
├── infrastructure/
└── interface/
```

---

# 54. Tổng kết Buổi 9

Bạn cần nắm chắc:

```text
Domain
    ↓
Business Rules

Application
    ↓
Use Case / Orchestration

Infrastructure
    ↓
Technical Implementation

Interface
    ↓
External Entry Point
```

Và quan trọng nhất:

```text
Application
      ↓
   Abstraction
      ↑
Infrastructure
```

chứ không phải:

```text
Application
      ↓
   SQLite
```

---

# 55. Chuỗi tư duy hoàn chỉnh

Sau 9 buổi:

```text
                 BUSINESS
                    │
                    ↓
                 DOMAIN
                    │
              ┌─────┴─────┐
              ↓           ↓
         Subdomain    Business Rules
              │
              ↓
       Bounded Context
              │
              ↓
        Context Mapping
              │
              ↓
       Domain Architecture
              │
       ┌──────┼──────┐
       ↓      ↓      ↓
    Domain  App   Infrastructure
              │
              ↓
          Interface
```

**Buổi 10** sẽ là bước nối rất quan trọng: **DDD + Clean Architecture**. Chúng ta sẽ phân biệt chính xác **DDD là gì, Clean Architecture là gì, chúng giao nhau ở đâu, Ports & Adapters hoạt động thế nào**, rồi thiết kế hẳn một **project Python theo DDD + Clean Architecture + Bounded Context** cho hệ thống crawler/đọc truyện.
