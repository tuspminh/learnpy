# Buổi 16 — SOLID + Clean Architecture

Đây là buổi **cực kỳ quan trọng** của toàn bộ khóa SOLID.

Từ Buổi 1–15, chúng ta học:

```text
SOLID
DDD
Design Patterns
Testing
Dependency Injection
```

Từ hôm nay, chúng ta ghép tất cả thành **kiến trúc hệ thống hoàn chỉnh**.

Mục tiêu cuối buổi:

```text
Framework
    ↓
Interface Adapter
    ↓
Application / Use Case
    ↓
Domain
```

và quan trọng nhất:

> **Dependency phải hướng vào trong.**

---

# 1. Clean Architecture là gì?

Clean Architecture là cách tổ chức hệ thống sao cho:

* business rule không phụ thuộc framework
* domain không phụ thuộc database
* use case không phụ thuộc UI
* infrastructure có thể thay thế
* testing dễ dàng
* dependency direction rõ ràng

Một cách nhìn đơn giản:

```text
┌─────────────────────────────────────────────┐
│          Frameworks & Drivers                │
│                                             │
│ Flet / FastAPI / CLI / SQLite / HTTP       │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │        Interface Adapters           │   │
│   │                                     │   │
│   │ Controller / Presenter / Gateway    │   │
│   │                                     │   │
│   │   ┌─────────────────────────────┐   │   │
│   │   │          Use Cases          │   │   │
│   │   │                             │   │   │
│   │   │ Application Business Rules  │   │   │
│   │   │                             │   │   │
│   │   │    ┌───────────────────┐    │   │   │
│   │   │    │     Entities      │    │   │   │
│   │   │    │                   │    │   │   │
│   │   │    │ Enterprise Rules  │    │   │   │
│   │   │    └───────────────────┘    │   │   │
│   │   └─────────────────────────────┘   │   │
│   └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

Đây là cách trình bày kinh điển của Clean Architecture.

---

# 2. Bốn vòng chính

Ta tập trung vào 4 nhóm:

```text
1. Entities

2. Use Cases

3. Interface Adapters

4. Frameworks & Drivers
```

---

# 3. Vòng 1 — Entities

Đây là trung tâm.

Entity chứa:

```text
Business Rules
Business Behavior
Business Invariants
```

Ví dụ hệ thống truyện:

```text
Story
Chapter
Author
ReadingProgress
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Story:

    id: int
    title: str
    published: bool = False

    def publish(self) -> None:

        if not self.title.strip():
            raise ValueError(
                "Story must have a title"
            )

        self.published = True
```

Entity không biết:

```text
SQLite
requests
Flet
FastAPI
Typer
```

---

# 4. Entity là business rule cấp thấp nhất

Ví dụ:

```python
story.publish()
```

Rule:

```text
Story không thể publish
nếu không có title
```

Đây là **enterprise business rule**.

Không quan tâm UI là:

```text
CLI
Flet
PySide6
FastAPI
```

Tất cả đều phải tuân theo rule.

---

# 5. Vòng 2 — Use Cases

Use Case mô tả:

> **Application có thể làm gì?**

Ví dụ:

```text
CreateStory
PublishStory
RenameStory
DeleteStory
CrawlStory
ReadChapter
MarkChapterAsRead
```

Ví dụ:

```python
class PublishStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id: int):

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

Use Case điều phối domain.

---

# 6. Entity vs Use Case

Đây là distinction rất quan trọng.

### Entity

```python
story.publish()
```

Nó biết:

> Story publish như thế nào?

### Use Case

```python
PublishStory.execute(123)
```

Nó biết:

> Làm thế nào để thực hiện use case Publish Story?

---

# 7. Vòng 3 — Interface Adapters

Đây là lớp chuyển đổi dữ liệu.

Ví dụ:

```text
HTTP Request
      ↓
Controller
      ↓
Use Case
      ↓
Entity
```

Controller:

```python
class PublishStoryController:

    def __init__(self, use_case):
        self.use_case = use_case

    def handle(self, request):

        story_id = int(request["story_id"])

        return self.use_case.execute(
            story_id
        )
```

Controller không chứa business rule.

Nó chỉ:

```text
input
 ↓
convert
 ↓
use case
```

---

# 8. Presenter

Use Case có thể trả về application data:

```python
@dataclass
class StoryOutput:

    id: int
    title: str
    published: bool
```

Presenter chuyển:

```text
Application Output
        ↓
UI format
```

CLI:

```text
Story #1
Title: Python
Status: Published
```

API:

```json
{
    "id": 1,
    "title": "Python",
    "published": true
}
```

Flet:

```text
Label
Button
Card
```

Domain không cần biết bất kỳ thứ nào trong số này.

---

# 9. Vòng 4 — Frameworks & Drivers

Đây là outermost layer.

Ví dụ:

```text
SQLite
PostgreSQL
requests
BeautifulSoup
Flet
PySide6
FastAPI
Typer
Redis
```

Chúng là **details**.

Ví dụ:

```python
class SQLiteStoryRepository:
    ...
```

SQLite không phải business rule.

Nó chỉ là implementation detail.

---

# 10. Dependency Rule

Đây là **trái tim của Clean Architecture**.

> **Source code dependencies chỉ được hướng vào trong.**

Ví dụ:

```text
Framework
    ↓
Adapter
    ↓
Use Case
    ↓
Entity
```

Không được:

```text
Entity
    ↓
SQLite
```

Không được:

```text
Use Case
    ↓
Flet
```

Không được:

```text
Domain
    ↓
requests
```

---

# 11. Tại sao dependency direction quan trọng?

Giả sử:

```python
class PublishStory:

    def __init__(self):
        self.repo = SQLiteStoryRepository()
```

Ta có:

```text
PublishStory
     ↓
SQLite
```

Nếu đổi database:

```text
SQLite → PostgreSQL
```

phải sửa Use Case.

Đây là coupling.

---

# 12. Dependency Inversion

Ta thay bằng:

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

Use Case:

```python
class PublishStory:

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

Composition:

```python
repository = SQLiteStoryRepository(connection)

use_case = PublishStory(repository)
```

---

# 13. Đây chính là DIP

Nhớ lại Buổi 10:

```text
High-level policy
       ↓
Abstraction
       ↑
Low-level detail
```

Clean Architecture biến nguyên lý này thành architecture.

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

---

# 14. SOLID và Clean Architecture

Bây giờ nhìn lại SOLID:

### SRP

Mỗi layer có responsibility riêng:

```text
Entity
Use Case
Controller
Repository
Presenter
```

---

### OCP

Có thể thêm:

```text
SQLiteRepository
PostgresRepository
MemoryRepository
```

mà không sửa Use Case.

---

### LSP

Các implementation:

```text
SQLiteRepository
PostgresRepository
FakeRepository
```

phải thay thế được abstraction.

---

### ISP

Interface nhỏ:

```python
class StoryReader(Protocol):
    def get_by_id(...):
        ...
```

---

### DIP

Inner layer không phụ thuộc outer layer.

Đây là nguyên lý quan trọng nhất.

---

# 15. Clean Architecture thực chất là DIP ở cấp hệ thống

Một cách hiểu rất mạnh:

> **SOLID DIP áp dụng ở cấp class/module; Clean Architecture mở rộng ý tưởng Dependency Inversion lên toàn hệ thống.**

Ví dụ nhỏ:

```text
UserService
     ↓
UserRepository
```

Architecture lớn:

```text
Framework
     ↓
Adapter
     ↓
Application
     ↓
Domain
```

Cùng một tư tưởng.

---

# 16. Ví dụ kiến trúc xấu

Giả sử CLI crawler:

```python
import sqlite3
import requests
from bs4 import BeautifulSoup


def crawl(url):

    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    title = soup.select_one("h1").text

    conn = sqlite3.connect(
        "stories.db"
    )

    conn.execute(
        "INSERT INTO stories(title) VALUES (?)",
        (title,),
    )

    conn.commit()

    print("Saved:", title)
```

Nhìn tưởng đơn giản.

Nhưng một function chứa:

```text
HTTP
HTML
Business logic
Database
CLI output
```

---

# 17. Phân tích SOLID violation

### SRP

Quá nhiều responsibility.

### DIP

Business logic phụ thuộc:

```text
requests
sqlite3
```

### OCP

Muốn đổi:

```text
SQLite → PostgreSQL
```

phải sửa function.

### Testing

Khó unit test.

### DDD

Business concepts không rõ ràng.

---

# 18. Refactor bước 1 — Domain

```python
from dataclasses import dataclass


@dataclass
class Story:

    title: str

    def __post_init__(self):

        if not self.title.strip():
            raise ValueError(
                "Title cannot be empty"
            )
```

Domain không biết HTTP.

---

# 19. Refactor bước 2 — Parser

```python
class StoryParser:

    def parse(self, html: str) -> Story:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = soup.select_one("h1").text

        return Story(
            title=title
        )
```

Nhưng parser này thuộc infrastructure nếu nó dùng BeautifulSoup.

---

# 20. Refactor bước 3 — HTTP abstraction

```python
class HttpClient(Protocol):

    def get(self, url: str) -> str:
        ...
```

Infrastructure:

```python
class RequestsHttpClient:

    def get(self, url: str) -> str:

        response = requests.get(url)

        response.raise_for_status()

        return response.text
```

---

# 21. Refactor bước 4 — Repository

```python
class StoryRepository(Protocol):

    def save(self, story: Story) -> None:
        ...
```

Infrastructure:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(self, story):

        self.connection.execute(
            """
            INSERT INTO stories(title)
            VALUES (?)
            """,
            (story.title,),
        )

        self.connection.commit()
```

---

# 22. Refactor bước 5 — Use Case

```python
class CrawlStory:

    def __init__(
        self,
        http_client: HttpClient,
        parser: StoryParser,
        repository: StoryRepository,
    ):
        self.http_client = http_client
        self.parser = parser
        self.repository = repository

    def execute(self, url: str):

        html = self.http_client.get(url)

        story = self.parser.parse(html)

        self.repository.save(story)

        return story
```

Đây là application layer.

---

# 23. Architecture bây giờ

```text
                  ┌───────────────┐
                  │      CLI      │
                  └───────┬───────┘
                          ↓
                  ┌───────────────┐
                  │  CrawlStory   │
                  │   Use Case    │
                  └───────┬───────┘
                          ↓
              ┌───────────┴───────────┐
              ↓                       ↓
        HttpClient              StoryRepository
              ↑                       ↑
              │                       │
       RequestsClient          SQLiteRepository

                  Domain
                    ↑
                  Story
```

---

# 24. CLI không được chứa business logic

Sai:

```python
@app.command()
def crawl(url):

    response = requests.get(url)

    ...

    sqlite3.connect(...)

    ...
```

CLI đang làm application.

Đúng:

```python
@app.command()
def crawl(url):

    result = crawl_story.execute(url)

    print(result.title)
```

CLI chỉ là adapter.

---

# 25. Flet cũng chỉ là Adapter

Nếu sau này chuyển sang Flet:

```text
Flet UI
   ↓
Controller / Presenter
   ↓
Use Case
   ↓
Domain
```

Use Case không đổi.

Đây chính là một trong những lợi ích lớn nhất.

---

# 26. PySide6 cũng vậy

```text
PySide6
   ↓
Controller
   ↓
Application
   ↓
Domain
```

Không:

```text
Domain
   ↓
PySide6
```

---

# 27. FastAPI cũng vậy

```text
HTTP
 ↓
FastAPI Endpoint
 ↓
Controller
 ↓
Use Case
 ↓
Domain
```

Domain không biết FastAPI tồn tại.

---

# 28. Một Use Case — nhiều Interface

Ví dụ:

```text
                 PublishStory
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
         CLI        Flet       FastAPI
```

Tất cả đều gọi:

```python
publish_story.execute(...)
```

Business logic chỉ tồn tại một lần.

---

# 29. Đây là Separation of Concerns

```text
CLI
→ presentation

FastAPI
→ HTTP

SQLite
→ persistence

Requests
→ network

BeautifulSoup
→ parsing

Use Case
→ application behavior

Entity
→ domain behavior
```

Mỗi concern nằm đúng boundary.

---

# 30. Project Structure

Một cấu trúc Python thực tế:

```text
src/
└── novel_app/
    │
    ├── domain/
    │   ├── entities/
    │   │   └── story.py
    │   │
    │   ├── value_objects/
    │   │   └── story_title.py
    │   │
    │   ├── repositories/
    │   │   └── story_repository.py
    │   │
    │   └── services/
    │
    ├── application/
    │   ├── use_cases/
    │   │   ├── crawl_story.py
    │   │   └── publish_story.py
    │   │
    │   └── dto/
    │
    ├── adapters/
    │   ├── cli/
    │   ├── http/
    │   └── presenters/
    │
    ├── infrastructure/
    │   ├── database/
    │   │   └── sqlite/
    │   │
    │   ├── crawler/
    │   │
    │   └── http/
    │
    └── composition.py
```

Đây là một cấu trúc tốt để bắt đầu, nhưng **không phải luật bắt buộc**.

---

# 31. Đừng nhầm package structure với architecture

Có thể có:

```text
domain/
application/
infrastructure/
```

nhưng architecture vẫn xấu.

Ví dụ:

```python
# domain/story.py

import sqlite3
```

Folder đúng.

Dependency sai.

Vì vậy:

> **Architecture được xác định bởi dependency, không phải tên folder.**

Đây là một insight cực kỳ quan trọng.

---

# 32. Dependency Graph

Hãy nghĩ bằng graph.

Sai:

```text
Domain → SQLite
Domain → requests
Application → Flet
```

Đúng:

```text
Infrastructure → Application
Infrastructure → Domain
Application → Domain
```

Tức:

```text
        Infrastructure
          ↓       ↓
          ↓       ↓
       Application
            ↓
         Domain
```

---

# 33. Nhưng tại sao Infrastructure "biết" Domain?

Ví dụ:

```python
class SQLiteStoryRepository:

    def save(self, story: Story):
        ...
```

Infrastructure import:

```python
from domain.entities.story import Story
```

Điều này hoàn toàn bình thường.

Infrastructure là outer layer.

Nó có thể phụ thuộc inner layer.

---

# 34. Dependency Injection

Composition Root:

```python
def build_app():

    connection = create_connection()

    repository = SQLiteStoryRepository(
        connection
    )

    http_client = RequestsHttpClient()

    parser = BeautifulSoupStoryParser()

    crawl_story = CrawlStory(
        http_client=http_client,
        parser=parser,
        repository=repository,
    )

    return crawl_story
```

CLI:

```python
crawl_story = build_app()

crawl_story.execute(url)
```

---

# 35. Composition Root cực kỳ quan trọng

Tất cả concrete dependency nên được assemble ở đây:

```text
SQLiteRepository
RequestsClient
BeautifulSoupParser
Flet
Typer
```

Domain không instantiate chúng.

Use Case không instantiate chúng.

```text
Composition Root
       │
       ├── SQLite
       ├── HTTP
       ├── Parser
       └── Use Cases
```

---

# 36. Clean Architecture + Testing

Giờ testing cực kỳ tự nhiên.

### Domain test

```python
def test_story_cannot_have_empty_title():
    ...
```

### Application test

Fake:

```python
class FakeRepository:
    ...
```

### Infrastructure test

```text
SQLite integration test
```

### CLI test

Test adapter.

---

# 37. Test không cần framework thật

Ví dụ:

```python
def test_crawl_story():

    http = FakeHttpClient(
        "<h1>Python</h1>"
    )

    parser = FakeParser()

    repository = FakeRepository()

    use_case = CrawlStory(
        http,
        parser,
        repository,
    )

    story = use_case.execute(
        "https://example.com"
    )

    assert story.title == "Python"
```

Không cần:

```text
Internet
SQLite
CLI
Flet
```

---

# 38. Clean Architecture không có nghĩa nhiều layer vô hạn

Đây là lỗi phổ biến:

```text
Controller
Service
Manager
Handler
Interactor
UseCase
Gateway
Repository
Provider
Factory
Adapter
Mapper
DTO
```

cho một CRUD đơn giản.

Clean Architecture không phải:

> "Càng nhiều abstraction càng clean."

Ngược lại.

Mục tiêu:

> **Boundary rõ ràng với complexity vừa đủ.**

---

# 39. Khi nào nên áp dụng đầy đủ?

Nên cân nhắc khi hệ thống có:

```text
nhiều business rules
nhiều interface
nhiều infrastructure
nhiều integration
domain phức tạp
dự kiến thay đổi lớn
cần test nhiều
```

Ví dụ ứng dụng crawler của bạn:

```text
CLI
Flet
SQLite
Crawler
Plugin
Queue
Worker
TTS
Reader
```

rất phù hợp.

---

# 40. Clean Architecture + Crawler

Ta có:

```text
                   CLI / Flet
                       ↓
                  CrawlStory
                   Use Case
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
          Crawler            Repository
          Protocol           Protocol
              ↑                 ↑
      ┌───────┴──────┐          │
      ↓              ↓          ↓
 SiteACrawler   SiteBCrawler   SQLite
```

Đây chính là architecture mà chúng ta sẽ xây ở Buổi 18.

---

# 41. Framework Independence

Một test rất hay:

> Nếu xóa Flet khỏi project, Domain có compile/test được không?

Nếu:

```text
Có
```

tốt.

Một test khác:

> Nếu đổi SQLite → PostgreSQL, Use Case có phải sửa không?

Nếu:

```text
Không
```

tốt.

Một test nữa:

> Nếu CLI → Flet, Domain có phải sửa không?

Nếu:

```text
Không
```

tốt.

Đó là những dấu hiệu của Clean Architecture.

---

# 42. Business Rules vs Details

Đây là mental model quan trọng nhất.

### Business

```text
Story phải có title
Chapter phải thuộc Story
Không được publish Story rỗng
Chapter phải được publish trước khi đọc
```

### Details

```text
SQLite
PostgreSQL
HTTP
Flet
PySide6
Typer
BeautifulSoup
requests
```

Architecture tốt:

```text
Business
  ↑
  │
Details
```

Business không bị details chi phối.

---

# 43. Một câu hỏi thiết kế cực hữu ích

Khi viết một dòng code, hãy hỏi:

> **Dòng code này thuộc business hay detail?**

Ví dụ:

```python
if story.status != "published":
```

Có thể là business.

```python
cursor.execute(...)
```

chắc chắn là infrastructure.

```python
print("Story published")
```

presentation.

```python
requests.get(...)
```

infrastructure.

Sau đó đặt nó vào đúng boundary.

---

# 44. SOLID → Clean Architecture

Ta có thể tổng hợp:

```text
SRP
 ↓
separation of responsibilities

OCP
 ↓
replaceable adapters

LSP
 ↓
interchangeable implementations

ISP
 ↓
small ports/interfaces

DIP
 ↓
dependency direction
```

Kết quả:

```text
        CLEAN ARCHITECTURE
```

---

# 45. DDD → Clean Architecture

DDD cho:

```text
Entity
Value Object
Aggregate
Domain Service
Repository
```

Clean Architecture cho:

```text
Entities
Use Cases
Interface Adapters
Frameworks & Drivers
```

Chúng không hoàn toàn đồng nghĩa, nhưng kết hợp rất tốt:

```text
DDD Domain
    ↓
Clean Architecture Entities

DDD Application Service / Use Case
    ↓
Clean Architecture Use Cases

Repository / Adapter
    ↓
Interface Adapters / Infrastructure
```

---

# 46. Một architecture hoàn chỉnh

```text
┌──────────────────────────────────────────────┐
│                Frameworks                    │
│                                              │
│ CLI    Flet    FastAPI    SQLite    HTTP    │
│  │       │        │         │        │       │
└──┼───────┼────────┼─────────┼────────┼───────┘
   │       │        │         │        │
   ↓       ↓        ↓         ↓        ↓
┌──────────────────────────────────────────────┐
│             Interface Adapters               │
│                                              │
│ Controllers / Presenters / Gateways         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                 Use Cases                    │
│                                              │
│ CrawlStory / PublishStory / ReadChapter     │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                  Domain                     │
│                                              │
│ Story / Chapter / Value Objects / Rules     │
└──────────────────────────────────────────────┘
```

**Mũi tên dependency của source code phải hướng vào trong.**

---

# 47. Bài tập Buổi 16

## Bài 1 — Phân loại

Cho các thành phần:

```text
Story
SQLiteRepository
FletWindow
PublishStory
StoryTitle
RequestsClient
CLI
StoryPresenter
Chapter
```

Hãy phân loại thành:

```text
Entity
Value Object
Use Case
Interface Adapter
Infrastructure
```

---

## Bài 2 — Tìm dependency violation

Đoạn code:

```python
class Story:

    def save(self):

        connection = sqlite3.connect(
            "story.db"
        )

        connection.execute(...)
```

Hãy giải thích:

1. Vi phạm nguyên lý nào?
2. Vi phạm Dependency Rule thế nào?
3. Refactor thành architecture nào?

---

## Bài 3 — Thiết kế Use Case

Thiết kế:

```text
PublishStory
```

với:

```text
StoryRepository
```

Yêu cầu:

```text
Story không tồn tại → error

Story đã publish → không publish lại

Story hợp lệ → publish

save()
```

---

# 48. Bài tập lớn — Clean Architecture cho Story App

Thiết kế:

```text
CLI
 ↓
Use Case
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository
```

Use cases:

```text
CreateStory
GetStory
RenameStory
PublishStory
DeleteStory
```

Domain:

```text
Story
StoryTitle
```

Infrastructure:

```text
SQLiteStoryRepository
```

Testing:

```text
FakeStoryRepository
```

Mục tiêu:

```text
CLI không chứa business logic
Use Case không biết SQLite
Domain không biết CLI
Domain không biết SQLite
```

---

# 49. Checklist Clean Architecture

Khi thiết kế project Python, hãy kiểm tra:

### Domain

```text
[ ] Không import framework
[ ] Không import database
[ ] Không HTTP
[ ] Chứa business rules
[ ] Bảo vệ invariant
```

### Application

```text
[ ] Chứa use cases
[ ] Điều phối domain
[ ] Không biết UI cụ thể
[ ] Không biết SQLite cụ thể
```

### Adapters

```text
[ ] Convert input/output
[ ] Controller
[ ] Presenter
[ ] Gateway
```

### Infrastructure

```text
[ ] SQLite
[ ] HTTP
[ ] Filesystem
[ ] External APIs
[ ] Framework
```

---

# 50. Mental Model cuối buổi

Đừng nhớ Clean Architecture bằng tên 4 vòng.

Hãy nhớ:

```text
                 BUSINESS
                    ↑
                    │
              DOMAIN RULES
                    ↑
                    │
                USE CASE
                    ↑
                    │
               ADAPTERS
                    ↑
                    │
                DETAILS
```

Hoặc đơn giản hơn:

```text
              ┌─────────────┐
              │   Details   │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   Adapter   │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │  Use Case   │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   Domain    │
              └─────────────┘
```

**Dependency đi vào trong.**

---

# Roadmap sau Buổi 16

```text
Phần VI — SOLID trong Clean Architecture

✅ Buổi 16 — SOLID + Clean Architecture

⬜ Buổi 17 — Thiết kế CLI

CLI
 ↓
Application
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository

⬜ Buổi 18 — Thiết kế Crawler

Crawler
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Crawler Plugin

⬜ Buổi 19 — Refactoring thực chiến

CrawlerManager
       ↓
God Object
       ↓
SRP
       ↓
OCP
       ↓
DIP
       ↓
DDD
       ↓
Clean Architecture
```

**Buổi 17 sẽ bắt đầu xây một architecture thật bằng Python**, không chỉ học lý thuyết: `Typer CLI → Application/Use Case → Domain → Repository Protocol → SQLite Repository`, sau đó inject dependency từ Composition Root và viết test bằng `FakeRepository`.
