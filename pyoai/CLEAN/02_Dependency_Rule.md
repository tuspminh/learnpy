# Buổi 2 — Dependency Rule Deep Dive

Buổi 1 chúng ta đã có một tư tưởng nền:

> **Clean Architecture không chủ yếu nói về folder; nó nói về hướng của dependency.**

Hôm nay ta đào thật sâu vào câu này.

---

# 1. Dependency là gì?

Ở mức đơn giản nhất:

```python
import sqlite3
```

Code của bạn phụ thuộc vào `sqlite3`.

Ta có:

```text
MyCode ───────► sqlite3
```

Trong Python, dependency thường xuất hiện qua:

* `import`
* kế thừa
* gọi function
* tạo object
* type annotation
* sử dụng interface/protocol
* sử dụng API của một module khác

Ví dụ:

```python
class StoryService:
    def create(self):
        repository.save(...)
```

`StoryService` phụ thuộc vào `repository`.

---

# 2. Dependency không chỉ là `import`

Đây là điểm rất quan trọng.

Ví dụ:

```python
class StoryService:

    def create(self, repository):
        repository.save(...)
```

Không có:

```python
import repository
```

nhưng vẫn có dependency.

Vì `StoryService` đang giả định:

```text
repository
    └── có method save()
```

Đây gọi là **contractual dependency**.

---

# 3. Dependency graph

Ta có:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository
```

Dependency graph:

```text
StoryService
     │
     ▼
Repository
```

Nếu:

```python
class SQLiteStoryRepository:
    ...
```

thì:

```text
StoryService
     │
     ▼
SQLiteStoryRepository
```

Đây là vấn đề.

Tại sao?

Vì `StoryService` đang biết một **detail cụ thể**.

---

# 4. Stable và Volatile

Hãy chia code thành hai nhóm.

### Stable

```text
Domain
Business Rules
Use Cases
```

### Volatile

```text
SQLite
PostgreSQL
HTTP
FastAPI
PySide6
Flet
Playwright
Redis
```

Ví dụ:

```text
                STABLE
                  │
                  ▼
          Business Rules
                  │
                  ▼
              Use Cases
                  │
                  ▼
               DETAILS
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    SQLite      HTTP       GUI
```

Clean Architecture muốn:

> **Details phụ thuộc vào policy, không phải policy phụ thuộc vào details.**

---

# 5. Policy vs Detail

Đây là một cách nhìn rất mạnh.

## Policy

Là logic quyết định **application phải làm gì**.

Ví dụ:

```text
CreateStory
PublishStory
StartCrawl
PauseCrawl
```

## Detail

Là cách thực hiện.

Ví dụ:

```text
SQLite
PostgreSQL
Redis
HTTPX
Playwright
PySide6
```

Ví dụ:

```text
CreateStory
```

là policy.

Còn:

```text
SQLiteStoryRepository
```

là detail.

---

# 6. Architecture sai

Ta viết:

```python
class CreateStory:

    def execute(self, title):
        repository = SQLiteStoryRepository()

        story = Story(title)

        repository.save(story)
```

Dependency:

```text
CreateStory
     │
     ▼
SQLiteStoryRepository
     │
     ▼
   SQLite
```

Vấn đề:

```text
Policy
  ↓
Detail
```

Policy đang phụ thuộc vào detail.

---

# 7. Dependency Inversion

Dependency Inversion nói rằng:

> **High-level policy không nên phụ thuộc trực tiếp vào low-level detail. Cả hai nên phụ thuộc vào abstraction.**

Ta tạo abstraction:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story):
        ...
```

Sau đó:

```python
class CreateStory:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, title):
        story = Story(title)

        self.repository.save(story)
```

SQLite:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Dependency graph:

```text
                 StoryRepository
                ▲              ▲
                │              │
                │              │
        CreateStory      SQLiteStoryRepository
```

Đây chính là inversion.

---

# 8. Tại sao gọi là "Inversion"?

Ban đầu:

```text
CreateStory
     │
     ▼
SQLite
```

High-level phụ thuộc low-level.

Sau khi inversion:

```text
CreateStory
     │
     ▼
StoryRepository
     ▲
     │
SQLiteStoryRepository
```

Bây giờ:

```text
Policy → abstraction ← Detail
```

Abstraction nằm ở phía policy.

---

# 9. Đây là điểm rất quan trọng

Nhiều người học Clean Architecture sẽ nghĩ:

> "Tạo interface là xong Dependency Inversion."

Không.

Interface chỉ là **công cụ**.

Điều quan trọng là:

```text
Ai sở hữu abstraction?
```

Ví dụ:

```text
infrastructure/
    story_repository.py
```

chứa:

```python
class StoryRepository(Protocol):
    ...
```

và:

```text
application/
    create_story.py
```

import nó.

Architecture vẫn có thể sai.

---

# 10. Abstraction nên thuộc về phía cần nó

Nếu Application cần:

```text
save Story
```

thì Application nên định nghĩa contract:

```python
class StoryRepository(Protocol):

    def save(self, story) -> None:
        ...
```

Infrastructure chỉ implement contract đó:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Dependency:

```text
Application
    │
    ▼
StoryRepository
    ▲
    │
Infrastructure
```

Đây là một nguyên tắc cực kỳ quan trọng.

---

# 11. Python `Protocol`

Python rất phù hợp với kiến trúc này.

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story) -> None:
        ...

    def get(self, story_id: int):
        ...
```

Implementation:

```python
class SQLiteStoryRepository:

    def save(self, story) -> None:
        ...

    def get(self, story_id: int):
        ...
```

Không cần:

```python
class SQLiteStoryRepository(StoryRepository):
```

Đó là sức mạnh của **structural typing**.

---

# 12. Structural Typing

Python `Protocol` hoạt động theo ý tưởng:

> Nếu object có đúng interface mà tôi cần, tôi có thể sử dụng nó.

Ví dụ:

```python
class MemoryRepository:

    def save(self, story):
        print("saved in memory")
```

Use Case:

```python
class CreateStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, title):
        story = Story(title)
        self.repository.save(story)
```

Ta có thể truyền:

```python
CreateStory(MemoryRepository())
```

hoặc:

```python
CreateStory(SQLiteStoryRepository())
```

hoặc:

```python
CreateStory(PostgresStoryRepository())
```

Use Case không đổi.

---

# 13. Constructor Injection

Đây là Dependency Injection cơ bản nhất.

Không nên:

```python
class CreateStory:

    def __init__(self):
        self.repository = SQLiteStoryRepository()
```

Thay vào đó:

```python
class CreateStory:

    def __init__(self, repository):
        self.repository = repository
```

Bên ngoài quyết định implementation:

```python
repository = SQLiteStoryRepository()

use_case = CreateStory(repository)
```

Đây gọi là:

> **Constructor Injection**

---

# 14. Tại sao Injection quan trọng?

Vì object không còn tự quyết định dependency.

Sai:

```text
CreateStory
     │
     └── tự tạo SQLiteRepository
```

Đúng:

```text
Composition Root
       │
       ├── tạo Repository
       │
       └── truyền vào CreateStory
```

Architecture trở nên linh hoạt.

---

# 15. Composition Root

Composition Root là nơi **lắp ráp object graph**.

Ví dụ:

```python
def main():

    repository = SQLiteStoryRepository()

    create_story = CreateStory(
        repository=repository
    )

    ...
```

Ta có:

```text
main.py
  │
  ├── SQLiteStoryRepository
  │
  └── CreateStory
          │
          └── StoryRepository
```

`CreateStory` không cần biết SQLite.

---

# 16. Một ví dụ hoàn chỉnh

## Domain

```python
class Story:

    def __init__(self, title: str):
        if not title.strip():
            raise ValueError("Title cannot be empty")

        self.title = title
```

Domain không biết:

```text
SQLite
FastAPI
PySide6
```

---

## Application

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story: Story) -> None:
        ...


class CreateStory:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, title: str) -> Story:

        story = Story(title)

        self.repository.save(story)

        return story
```

Application biết:

```text
Story
StoryRepository
```

Nhưng không biết SQLite.

---

# 17. Infrastructure

```python
import sqlite3


class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(self, story):
        self.connection.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (story.title,),
        )

        self.connection.commit()
```

Infrastructure biết:

```text
SQLite
SQL
connection
```

Đó là nơi nó nên biết.

---

# 18. Composition Root

```python
import sqlite3


def main():

    connection = sqlite3.connect("story.db")

    repository = SQLiteStoryRepository(
        connection
    )

    create_story = CreateStory(
        repository
    )

    create_story.execute("One Piece")
```

Graph:

```text
                 main
                  │
          ┌───────┴────────┐
          ▼                ▼
     SQLiteRepository   CreateStory
          │                │
          │                ▼
          │         StoryRepository
          │                ▲
          └────────────────┘
```

---

# 19. Control Flow và Dependency Direction

Đây là phần bạn cần đặc biệt chú ý.

Runtime:

```text
main
 ↓
CreateStory
 ↓
StoryRepository
 ↓
SQLiteStoryRepository
 ↓
SQLite
```

Control flow:

```text
OUTER → INNER → OUTER
```

Nhưng dependency:

```text
SQLiteStoryRepository
        ↓
   Application
        ↓
      Domain
```

Conceptually:

```text
Infrastructure
      ↓
Application
      ↓
Domain
```

Hai khái niệm này **không giống nhau**.

---

# 20. Vì sao đây là "Clean"?

Bởi vì business core không biết:

```text
"SQLite tồn tại."
```

Nó chỉ biết:

```text
"Tôi cần một object có khả năng save Story."
```

Đây là abstraction.

---

# 21. Boundary

Boundary là ranh giới giữa hai phần.

Ví dụ:

```text
┌───────────────────────────────┐
│           Application         │
│                               │
│       CreateStory             │
│                               │
│       StoryRepository         │
└───────────────▲───────────────┘
                │
                │ Boundary
                │
┌───────────────┴───────────────┐
│        Infrastructure         │
│                               │
│    SQLiteStoryRepository      │
│                               │
└───────────────────────────────┘
```

Boundary giúp:

> Một bên không cần biết implementation chi tiết của bên kia.

---

# 22. Boundary càng tốt, thay đổi càng rẻ

Ví dụ:

```text
SQLiteStoryRepository
```

thay bằng:

```text
PostgresStoryRepository
```

Nếu contract giữ nguyên:

```python
class StoryRepository(Protocol):

    def save(self, story):
        ...
```

thì:

```text
CreateStory
```

không cần thay đổi.

Đây là mục tiêu của abstraction.

---

# 23. Interface Segregation bắt đầu xuất hiện

Đừng tạo interface khổng lồ:

```python
class StoryRepository(Protocol):

    def create(...): ...
    def update(...): ...
    def delete(...): ...
    def search(...): ...
    def export(...): ...
    def crawl(...): ...
    def download(...): ...
```

Use Case `CreateStory` có thể chỉ cần:

```python
class StoryWriter(Protocol):

    def save(self, story) -> None:
        ...
```

Đây là một tư duy quan trọng:

> **Abstraction nên phục vụ consumer, không phải phục vụ implementation.**

---

# 24. Ví dụ với crawler

Giả sử:

```text
StartCrawl
```

không nên biết:

```text
Playwright
BeautifulSoup
requests
aiohttp
```

Nó chỉ cần:

```python
class StorySource(Protocol):

    def fetch(self, url: str):
        ...
```

Implementation:

```text
PlaywrightStorySource
RequestsStorySource
MockStorySource
```

Graph:

```text
                 StorySource
                ▲      ▲      ▲
                │      │      │
          Playwright  HTTP   Fake
```

Use Case:

```text
StartCrawl
    │
    ▼
StorySource
```

---

# 25. Dependency Rule

Bây giờ ta có thể phát biểu quy tắc quan trọng:

> **Dependencies must point inward.**

Có thể hình dung:

```text
┌───────────────────────────────────┐
│         Infrastructure            │
│                                   │
│  SQLite / HTTP / GUI / CLI        │
│        ↓                          │
│  ┌─────────────────────────────┐  │
│  │       Application            │  │
│  │                              │  │
│  │       Use Cases              │  │
│  │          ↓                   │  │
│  │  ┌───────────────────────┐   │  │
│  │  │        Domain         │   │  │
│  │  │   Business Rules      │   │  │
│  │  └───────────────────────┘   │  │
│  └─────────────────────────────┘  │
└───────────────────────────────────┘
```

**Càng đi vào trong, code càng stable.**

---

# 26. Một architecture sai phổ biến

```text
domain/
    story.py
    repository.py
    sqlite_repository.py
```

Rồi:

```python
# domain/sqlite_repository.py

import sqlite3
```

Đây là dấu hiệu domain đã bị infrastructure kéo vào.

Folder không cứu được architecture.

---

# 27. Architecture đúng hơn

```text
domain/
    entities/
        story.py

application/
    ports/
        story_repository.py

    use_cases/
        create_story.py

infrastructure/
    database/
        sqlite_story_repository.py
```

Điều quan trọng không phải tên folder.

Quan trọng là:

```text
CreateStory
     ↓
StoryRepository
     ↑
SQLiteStoryRepository
```

---

# 28. `ABC` hay `Protocol`?

Python cho phép hai cách phổ biến.

## ABC

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass
```

Implementation:

```python
class SQLiteStoryRepository(StoryRepository):

    def save(self, story):
        ...
```

## Protocol

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story):
        ...
```

Implementation:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Trong Clean Architecture Python, `Protocol` thường rất tiện vì abstraction không cần ép implementation kế thừa.

---

# 29. Nhưng đừng biến mọi thứ thành Protocol

Đây cũng là một trap.

Không phải class nào cũng cần:

```python
SomeProtocol
SomeABC
SomeInterface
```

Nếu bạn có:

```python
class PriceCalculator:

    def calculate(self, price):
        return price * 1.1
```

và chỉ có một implementation, không có boundary thực sự cần abstraction, đừng vội tạo:

```python
PriceCalculatorProtocol
DefaultPriceCalculator
PriceCalculatorFactory
```

Đó là over-engineering.

---

# 30. Dependency Inversion không phải "đảo hết dependency"

Bạn không cần làm:

```text
Everything → Protocol
Everything → Interface
Everything → DI
```

Mục tiêu là:

> **Đảo dependency tại những boundary có giá trị.**

Ví dụ:

```text
Application ↔ Database
```

là boundary rất đáng đảo.

Nhưng:

```text
Story → StoryTitle
```

có thể không cần abstraction.

---

# 31. Test là nơi thấy rõ sức mạnh

Ta tạo Fake:

```python
class FakeStoryRepository:

    def __init__(self):
        self.items = []

    def save(self, story):
        self.items.append(story)
```

Test:

```python
def test_create_story():

    repository = FakeStoryRepository()

    use_case = CreateStory(repository)

    story = use_case.execute("One Piece")

    assert story.title == "One Piece"
    assert repository.items == [story]
```

Không có:

```text
SQLite
database file
SQL
transaction
cleanup
```

Test tập trung vào business behavior.

---

# 32. Một insight rất quan trọng

Clean Architecture không cố làm cho:

```text
SQLite
```

dễ thay thế chỉ vì mục đích thay database.

Nó muốn làm cho:

> **Business logic không quan tâm SQLite tồn tại.**

Đây là sự khác biệt rất lớn.

Nếu ngày mai bạn vẫn dùng SQLite 10 năm thì architecture vẫn có giá trị.

Vì business rules và persistence là hai concern khác nhau.

---

# 33. Bài tập thực hành

## Bài 1 — Phân tích dependency

Cho:

```python
class OrderService:

    def __init__(self):
        self.db = SQLiteDatabase()
        self.mailer = GmailMailer()

    def create_order(self, order):
        self.db.insert(order)
        self.mailer.send(...)
```

Hãy vẽ:

```text
OrderService
      ?
      ?
      ?
```

và xác định:

* High-level policy là gì?
* Low-level details là gì?
* Những dependency nào cần inversion?

---

# 34. Bài 2 — Thiết kế abstraction

Bạn có Use Case:

```text
DownloadChapter
```

Nó cần tải nội dung chapter từ Internet.

Có 3 implementation:

```text
RequestsDownloader
AiohttpDownloader
FakeDownloader
```

Hãy thiết kế `Protocol` cho boundary này.

Gợi ý:

```python
class ???(Protocol):

    def ???(...):
        ...
```

**Không được đưa `requests`, `aiohttp` vào Protocol.**

---

# 35. Bài 3 — Refactor

Code hiện tại:

```python
class RegisterUser:

    def execute(self, username, password):

        if len(username) < 3:
            raise ValueError()

        if len(password) < 8:
            raise ValueError()

        conn = sqlite3.connect("app.db")

        conn.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password),
        )

        conn.commit()
```

Hãy tách thành:

```text
Domain
Application
Infrastructure
```

Mục tiêu:

```text
RegisterUser
     ↓
UserRepository
     ↑
SQLiteUserRepository
```

---

# 36. Bài 4 — Architecture Challenge

Thiết kế dependency cho hệ thống:

```text
Story Crawler
```

Có:

```text
StartCrawl
CrawlChapter
SaveChapter
```

Infrastructure:

```text
Playwright
SQLite
Redis
HTTP
```

Presentation:

```text
CLI
PySide6
FastAPI
```

Bạn hãy vẽ dependency graph.

**Không cần code.**

Mục tiêu là chứng minh bạn hiểu:

```text
Control Flow
```

khác với:

```text
Dependency Direction
```

---

# 37. Checklist tư duy Buổi 2

Trước khi viết một class/service mới, hãy tự hỏi:

```text
1. Đây là policy hay detail?

2. Nó đang phụ thuộc vào cái gì?

3. Dependency đó có ổn định không?

4. Tôi có đang để business logic biết infrastructure không?

5. Boundary nằm ở đâu?

6. Ai cần abstraction?

7. Abstraction nên thuộc về phía nào?

8. Có thực sự cần Protocol/ABC không?

9. Tôi có thể test business logic mà không cần database không?

10. Nếu đổi framework/database, class này có phải sửa không?
```

Nếu bạn trả lời được 10 câu này, bạn đã bắt đầu **tư duy architecture**, thay vì chỉ biết cách tạo folder.

---

## Bài học cốt lõi của Buổi 2

Hãy ghi nhớ sơ đồ này:

```text
                 ┌───────────────┐
                 │    Domain     │
                 │ Business Rule │
                 └───────▲───────┘
                         │
                 ┌───────┴───────┐
                 │  Application   │
                 │   Use Cases    │
                 └───────▲───────┘
                         │
              abstraction│
                         │
                 ┌───────┴───────┐
                 │ Infrastructure │
                 │ SQLite / HTTP  │
                 │ Redis / GUI    │
                 └───────────────┘
```

Và ở boundary:

```text
Application
     │
     ▼
 Protocol
     ▲
     │
Infrastructure
```

**Buổi 3** chúng ta sẽ đi sâu vào **Separation of Concerns + Boundary + Cohesion/Coupling + SRP ở cấp kiến trúc**. Đây là buổi rất quan trọng vì nó giải thích tại sao một class có thể tuân thủ SRP nhưng **toàn bộ hệ thống vẫn có architecture tệ**.
