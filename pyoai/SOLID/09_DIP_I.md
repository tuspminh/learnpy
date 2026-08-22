# SOLID Deep Dive — Buổi 9

# DIP — Dependency Inversion Principle

Đây là **buổi cuối của 5 nguyên lý SOLID**, và cũng là buổi quan trọng nhất về mặt kiến trúc.

Nếu các buổi trước giúp bạn biết cách thiết kế **class/interface**, thì DIP giúp bạn trả lời câu hỏi lớn hơn:

> **Các module trong toàn hệ thống nên phụ thuộc vào nhau theo hướng nào?**

---

# 1. DIP là gì?

DIP = **Dependency Inversion Principle**

Có hai ý chính:

> **High-level modules should not depend on low-level modules. Both should depend on abstractions.**

Và:

> **Abstractions should not depend on details. Details should depend on abstractions.**

Dịch theo cách dễ hiểu:

```text
Module nghiệp vụ
      ↓
không nên phụ thuộc trực tiếp
      ↓
Database / HTTP / File / Redis / SMTP...
```

Thay vào đó:

```text
        Abstraction
        /         \
       ↑           ↑
High-level     Low-level
module         module
```

---

# 2. Ví dụ kinh điển

Code không tốt:

```python
class MySQLDatabase:

    def save(self, data):
        print("save to mysql")


class UserService:

    def __init__(self):
        self.database = MySQLDatabase()

    def create_user(self, user):
        self.database.save(user)
```

Dependency:

```text
UserService
     ↓
MySQLDatabase
```

`UserService` biết quá nhiều về infrastructure.

---

# 3. Vấn đề nằm ở đâu?

Giả sử sau này muốn đổi:

```text
MySQL
→ PostgreSQL
```

phải sửa:

```python
class UserService:
```

Hoặc:

```text
MySQL
→ SQLite
```

lại sửa.

Hoặc:

```text
MySQL
→ MongoDB
```

lại sửa.

High-level business logic đang bị khóa vào detail.

---

# 4. Đảo ngược dependency

Tạo abstraction:

```python
from typing import Protocol


class UserRepository(Protocol):

    def save(self, user):
        ...
```

Business:

```python
class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user):
        self.repository.save(user)
```

Infrastructure:

```python
class MySQLUserRepository:

    def save(self, user):
        print("save to mysql")
```

Dependency:

```text
             UserRepository
              ↑          ↑
              │          │
      UserService    MySQLRepository
```

Điểm quan trọng:

```text
UserService
      ↓
UserRepository
```

chứ không còn:

```text
UserService
      ↓
MySQLRepository
```

---

# 5. "Inversion" nghĩa là gì?

Ban đầu:

```text
High-level
    ↓
Low-level
```

Ví dụ:

```text
UserService
    ↓
MySQL
```

Sau DIP:

```text
High-level
    ↓
Abstraction
    ↑
Low-level
```

Ví dụ:

```text
             UserRepository
              ↑          ↑
              │          │
        UserService    MySQL
```

Dependency direction đã được đảo ngược.

---

# 6. DIP không đồng nghĩa với Dependency Injection

Đây là một điểm cực kỳ quan trọng.

Hai khái niệm:

```text
Dependency Inversion
```

và:

```text
Dependency Injection
```

**không phải cùng một thứ.**

---

# 7. Dependency Injection là kỹ thuật

DI trả lời:

> Dependency được đưa vào object như thế nào?

Ví dụ:

```python
class UserService:

    def __init__(self, repository):
        self.repository = repository
```

Dependency được inject từ bên ngoài.

Đây là:

> Constructor Injection.

---

# 8. DIP là nguyên lý kiến trúc

DIP trả lời:

> Module nào phụ thuộc module nào?

Ví dụ:

```text
UserService
    ↓
UserRepository
```

chứ không:

```text
UserService
    ↓
MySQLRepository
```

DI có thể giúp chúng ta thực hiện DIP.

Nhưng:

```text
DI ≠ DIP
```

---

# 9. Constructor Injection

Đây là kiểu DI tôi khuyến nghị dùng nhiều nhất trong Python.

```python
class OrderService:

    def __init__(self, repository):
        self.repository = repository
```

Composition:

```python
repository = SqliteOrderRepository()
service = OrderService(repository)
```

Dependency graph:

```text
Composition Root
       │
       ├── SqliteOrderRepository
       │
       └── OrderService
```

---

# 10. Không tự tạo dependency bên trong

Tránh:

```python
class OrderService:

    def __init__(self):
        self.repository = SqliteOrderRepository()
```

Tốt hơn:

```python
class OrderService:

    def __init__(self, repository):
        self.repository = repository
```

Vì:

```text
Before:

OrderService
    ↓
new SqliteRepository()
```

Sau:

```text
Composition Root
       ↓
OrderService(repository)
```

---

# 11. Composition Root

Đây là khái niệm cực kỳ quan trọng.

> **Composition Root là nơi toàn bộ dependency được wire lại với nhau.**

Ví dụ:

```python
def main():

    database = SqliteDatabase("app.db")

    repository = SqliteUserRepository(database)

    service = UserService(repository)

    controller = UserController(service)

    controller.run()
```

Đây là nơi biết:

```text
SQLite
UserRepository
UserService
Controller
```

Business code không cần biết cách tạo infrastructure.

---

# 12. Architecture

Một ứng dụng có thể có:

```text
                 Composition Root
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
    Controller      UseCase       Repository
         │              │              │
         └──────────────┼──────────────┘
                        ↓
                   Application
                        ↓
                    Domain
```

Infrastructure được wire ở ngoài cùng.

---

# 13. DIP + Clean Architecture

Đây chính là nền tảng của Clean Architecture.

```text
┌─────────────────────────────┐
│       Presentation          │
├─────────────────────────────┤
│       Application           │
├─────────────────────────────┤
│          Domain             │
└─────────────────────────────┘
              ↑
              │
      dependencies point
        toward inside
              │
┌─────────────────────────────┐
│       Infrastructure        │
└─────────────────────────────┘
```

Infrastructure:

```text
SQLite
PostgreSQL
Redis
HTTP
Filesystem
```

không được trở thành dependency trực tiếp của Domain.

---

# 14. Ví dụ Repository

Không tốt:

```python
import sqlite3


class CreateStoryUseCase:

    def execute(self, story):

        conn = sqlite3.connect("stories.db")

        conn.execute(
            "INSERT INTO stories ..."
        )

        conn.commit()
```

Use case đang biết:

```text
sqlite3
SQL
connection
transaction
database file
```

Đây là violation DIP.

---

# 15. Áp dụng DIP

Application định nghĩa port:

```python
from typing import Protocol


class StoryWriter(Protocol):

    def save(self, story) -> None:
        ...
```

Use case:

```python
class CreateStoryUseCase:

    def __init__(self, writer: StoryWriter):
        self.writer = writer

    def execute(self, story):
        self.writer.save(story)
```

Infrastructure:

```python
class SqliteStoryRepository:

    def save(self, story):
        ...
```

Dependency:

```text
             StoryWriter
             ↑         ↑
             │         │
     CreateUseCase   SQLite
```

---

# 16. DIP + ISP

Bạn có thể thấy ngay mối quan hệ:

```text
ISP
 ↓
interface nhỏ
 ↓
DIP
 ↓
high-level phụ thuộc interface
```

Ví dụ:

```python
class StoryReader(Protocol):

    def get(self, story_id):
        ...
```

Use case:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

DIP đảm bảo:

```text
GetStoryUseCase
      ↓
StoryReader
```

ISP đảm bảo:

```text
StoryReader
      ↓
chỉ chứa capability cần thiết
```

---

# 17. DIP + OCP

Giả sử:

```text
StoryReader
```

có implementations:

```text
SQLiteStoryReader
PostgresStoryReader
RedisStoryReader
HttpStoryReader
```

Use case:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

Không cần sửa.

Thêm:

```text
MongoStoryReader
```

cũng không cần sửa use case.

Đây là:

```text
DIP + OCP
```

---

# 18. DIP + LSP

Các implementation:

```text
SQLiteStoryReader
PostgresStoryReader
RedisStoryReader
```

đều phải tuân contract:

```text
StoryReader
```

Nếu một implementation:

```python
def get(self, story_id):
    raise NotImplementedError
```

thì nó không thực sự thay thế được abstraction.

DIP cho dependency direction.

LSP đảm bảo substitution behavior.

---

# 19. DIP + SRP

Ví dụ:

```python
class CreateStoryUseCase:
```

chỉ nên chịu trách nhiệm:

```text
business operation
```

Không nên đồng thời:

```text
business logic
+
SQL
+
filesystem
+
HTTP
+
logging infrastructure
```

DIP giúp tách những trách nhiệm này ra.

---

# 20. DIP + tất cả SOLID

Có thể nhìn toàn bộ như sau:

```text
SRP
 ↓
class có trách nhiệm rõ ràng

OCP
 ↓
dễ mở rộng

LSP
 ↓
implementation thay thế được

ISP
 ↓
interface đúng nhu cầu client

DIP
 ↓
dependency đúng hướng
```

Đây là lý do SOLID không phải 5 nguyên lý độc lập.

Chúng hỗ trợ lẫn nhau.

---

# 21. DIP không có nghĩa "mọi thứ đều phải là Protocol"

Đây là một hiểu lầm rất phổ biến.

Không cần:

```python
class StringServiceProtocol(Protocol):
    ...
```

cho mọi class.

Nếu dependency là:

```python
class PasswordHasher:
    ...
```

và:

```text
không có lý do thay thế
```

thì abstraction có thể không cần thiết.

DIP không yêu cầu:

> "Protocol everywhere."

---

# 22. Khi nào nên tạo abstraction?

Một abstraction thường có giá trị khi:

### 1. Có nhiều implementation

```text
SQLite
PostgreSQL
Redis
```

### 2. Infrastructure boundary

```text
HTTP
DB
Filesystem
Queue
Email
```

### 3. Cần test isolation

```text
Real DB
vs
Fake DB
```

### 4. Business logic không nên biết implementation

Ví dụ:

```text
Payment
Storage
Messaging
Clock
```

---

# 23. Ví dụ Clock

Code không tốt:

```python
from datetime import datetime


class OrderService:

    def create(self):

        created_at = datetime.now()
```

Business logic phụ thuộc trực tiếp vào system clock.

Test khó:

```text
"Thời gian hiện tại là bao nhiêu?"
```

---

# 24. Áp dụng DIP cho Clock

```python
from datetime import datetime
from typing import Protocol


class Clock(Protocol):

    def now(self) -> datetime:
        ...
```

Use case:

```python
class OrderService:

    def __init__(self, clock: Clock):
        self.clock = clock

    def create(self):
        created_at = self.clock.now()
```

Production:

```python
class SystemClock:

    def now(self):
        return datetime.now()
```

Test:

```python
class FakeClock:

    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value
```

Đây là một ví dụ DIP cực kỳ đẹp.

---

# 25. DIP cho HTTP

Không tốt:

```python
import requests


class UserService:

    def get_user(self, user_id):

        response = requests.get(
            f"https://example.com/users/{user_id}"
        )

        return response.json()
```

Business/application phụ thuộc trực tiếp vào:

```text
requests
HTTP
URL
JSON
```

---

# 26. Tách abstraction

```python
class UserGateway(Protocol):

    def get_user(self, user_id):
        ...
```

Service:

```python
class UserService:

    def __init__(self, gateway: UserGateway):
        self.gateway = gateway

    def get_user(self, user_id):
        return self.gateway.get_user(user_id)
```

Infrastructure:

```python
class HttpUserGateway:

    def get_user(self, user_id):
        ...
```

Dependency:

```text
UserService
     ↓
UserGateway
     ↑
HttpUserGateway
```

---

# 27. DIP cho filesystem

Không tốt:

```python
class ReportService:

    def save(self, report):

        with open("report.txt", "w") as f:
            f.write(report)
```

Tạo abstraction:

```python
class ReportWriter(Protocol):

    def write(self, content: str) -> None:
        ...
```

Service:

```python
class ReportService:

    def __init__(self, writer: ReportWriter):
        self.writer = writer

    def save(self, report):
        self.writer.write(report)
```

Implementation:

```python
class FileReportWriter:

    def write(self, content):
        with open("report.txt", "w") as f:
            f.write(content)
```

---

# 28. DIP cho Queue

Đặc biệt phù hợp với hệ thống crawler của bạn.

Application:

```python
class TaskQueue(Protocol):

    def enqueue(self, task):
        ...

    def dequeue(self):
        ...
```

Worker:

```python
class CrawlWorker:

    def __init__(self, queue: TaskQueue):
        self.queue = queue

    def run(self):

        while True:
            task = self.queue.dequeue()
            self.process(task)
```

Implementation:

```text
RedisQueue
SqliteQueue
MemoryQueue
RabbitMQQueue
```

Worker không biết implementation.

---

# 29. DIP cho Crawler

Ví dụ:

```python
class StoryCrawler(Protocol):

    def crawl(self, url):
        ...
```

Worker:

```python
class CrawlStoryUseCase:

    def __init__(self, crawler: StoryCrawler):
        self.crawler = crawler

    def execute(self, url):
        return self.crawler.crawl(url)
```

Plugin:

```python
class NovelSiteCrawler:

    def crawl(self, url):
        ...
```

Dependency:

```text
CrawlStoryUseCase
       ↓
StoryCrawler
       ↑
NovelSiteCrawler
```

Đây chính là DIP + Plugin Architecture.

---

# 30. Composition Root cho crawler

Ví dụ CLI:

```python
def main():

    queue = RedisTaskQueue(...)

    crawler = SiteACrawler(...)

    use_case = CrawlStoryUseCase(
        crawler=crawler,
        queue=queue,
    )

    use_case.execute(url)
```

Toàn bộ dependency wiring nằm tại đây.

---

# 31. Factory không phải Composition Root

Ví dụ:

```python
class CrawlerFactory:

    def create(self):
        return SiteACrawler(...)
```

Factory chỉ tạo object.

Composition Root quyết định:

```text
object nào
+
dependency nào
+
configuration nào
```

Factory có thể được sử dụng bên trong Composition Root.

---

# 32. Service Locator — cẩn thận

Một cách thường thấy:

```python
container.get("user_service")
```

ở mọi nơi.

Ví dụ:

```python
class UserService:

    def execute(self):

        repo = container.get("repository")
```

Đây thường là:

> **Service Locator anti-pattern**

Vì dependency bị ẩn.

---

# 33. Dependency explicit tốt hơn

Không tốt:

```python
class UserService:

    def execute(self):
        repo = container.get(...)
```

Tốt:

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

Bây giờ nhìn constructor là biết:

```text
UserService
    ↓
repo
```

Dependency trở thành explicit.

---

# 34. Dependency Injection Container có cần thiết?

Với Python project nhỏ:

```python
repo = SqliteRepository()
service = UserService(repo)
```

là đủ.

Không cần:

```text
huge DI framework
```

Ngay cả project lớn, Composition Root bằng Python thuần thường đã rất mạnh.

---

# 35. DI bằng function

Không nhất thiết dependency phải là class.

Ví dụ:

```python
from typing import Callable


class UserService:

    def __init__(
        self,
        send_email: Callable[[str, str], None],
    ):
        self.send_email = send_email
```

Production:

```python
service = UserService(send_email=smtp_send)
```

Test:

```python
service = UserService(send_email=fake_send)
```

Đây vẫn là Dependency Injection.

---

# 36. DIP không chỉ áp dụng cho database

Đây là danh sách rất quan trọng:

```text
Database
Filesystem
HTTP
Redis
Queue
Email
Clock
Random generator
UUID generator
Logger
Configuration
Authentication
Payment gateway
Search engine
Cache
Message broker
```

Tất cả đều có thể là infrastructure/detail.

---

# 37. Ví dụ Random

Không tốt:

```python
import random


class PasswordService:

    def generate(self):
        return random.randint(1, 100)
```

Có thể abstraction:

```python
class RandomGenerator(Protocol):

    def randint(self, start, end):
        ...
```

Sau đó:

```python
class PasswordService:

    def __init__(self, random_generator):
        self.random = random_generator
```

Test deterministic.

---

# 38. DIP và Deterministic Testing

Đây là một lợi ích cực lớn.

Thay:

```text
system clock
random
network
database
```

bằng:

```text
FakeClock
FakeRandom
FakeGateway
FakeRepository
```

Test trở nên:

```text
deterministic
fast
isolated
```

---

# 39. Nhưng đừng abstraction hóa mọi thứ

Ví dụ:

```python
class IntegerAdder(Protocol):

    def add(self, a, b):
        ...
```

rồi:

```python
class PythonIntegerAdder:
    ...
```

Đây là abstraction vô nghĩa.

Không có:

```text
boundary
variation
substitution need
testing benefit
```

thì abstraction chỉ tạo ceremony.

---

# 40. Abstraction phải "earn its place"

Một câu rất đáng nhớ:

> **Don't abstract because you can. Abstract because there is a meaningful boundary.**

Ví dụ:

```text
Business
    ↓
Database
```

là boundary rõ ràng.

Nhưng:

```text
UserService
    ↓
UserValidator
```

không nhất thiết cần Protocol nếu chỉ có một implementation và không có boundary đáng kể.

---

# 41. Dependency Graph

Hãy tập nhìn project bằng graph.

Ví dụ không tốt:

```text
CLI
 ↓
Service
 ↓
SQLite
 ↓
Filesystem
 ↓
HTTP
```

Business logic bị kéo xuống infrastructure.

Sau DIP:

```text
             Composition Root
              /      |      \
             ↓       ↓       ↓
           CLI    Service  SQLite
                    ↓
               Abstractions
                    ↑
                SQLite
```

---

# 42. Clean Architecture nhìn từ DIP

Có thể nhớ bằng một câu:

> **Dependencies point toward policy, not toward details.**

Ví dụ:

```text
        Framework
            ↓
      Infrastructure
            ↓
       Application
            ↓
          Domain
```

Dependency compile/import thực tế nên hướng vào trong:

```text
Infrastructure
      ↓
Application
      ↓
Domain
```

Domain không import:

```python
import sqlite3
import requests
import redis
```

---

# 43. Một architecture Python thực tế

Ví dụ project:

```text
src/
└── app/
    │
    ├── domain/
    │   ├── entities/
    │   └── value_objects/
    │
    ├── application/
    │   ├── use_cases/
    │   └── ports/
    │
    ├── infrastructure/
    │   ├── database/
    │   ├── http/
    │   └── queue/
    │
    └── presentation/
        └── cli/
```

Dependency:

```text
presentation
      ↓
application
      ↓
domain

infrastructure
      ↓
application
      ↓
domain
```

---

# 44. Port & Adapter

DIP thường dẫn chúng ta tới kiến trúc:

```text
        Adapter
           ↓
       Port
           ↑
       Adapter
```

Ví dụ:

```text
                StoryReader
                  ↑
          ┌───────┴────────┐
          │                │
      SQLite             HTTP
      Adapter            Adapter
```

`StoryReader` là:

> Port

Implementation là:

> Adapter

---

# 45. Hexagonal Architecture

Có thể hình dung:

```text
             ┌─────────────┐
             │    CLI      │
             └──────┬──────┘
                    ↓
        ┌─────────────────────┐
        │     Application     │
        │                     │
        │      Domain         │
        └─────────────────────┘
          ↑        ↑       ↑
          │        │       │
       SQLite     HTTP    Redis
       Adapter   Adapter  Adapter
```

DIP chính là một trong những nền tảng tư tưởng của kiến trúc này.

---

# 46. Một lỗi rất phổ biến

Nhiều developer nghĩ:

```python
class UserService:

    def __init__(self, repository: UserRepository):
        ...
```

là đã có DIP.

Chưa chắc.

Nếu:

```python
UserRepository
```

là class infrastructure:

```python
class UserRepository:

    def __init__(self):
        self.connection = sqlite3.connect(...)
```

thì abstraction vẫn có thể nằm sai boundary.

Cần nhìn:

> **Ai sở hữu abstraction?**

---

# 47. Application-owned abstraction

Tốt hơn:

```text
application/
    ports/
        user_repository.py
```

```python
class UserRepository(Protocol):
    ...
```

Infrastructure:

```text
infrastructure/
    sqlite/
        user_repository.py
```

implement abstraction.

Dependency:

```text
application
      ↑
infrastructure
```

---

# 48. DIP trong một câu

Nếu phải nhớ **một câu duy nhất**:

> **Business logic không nên biết detail; detail phải thích nghi với business abstraction.**

Ví dụ:

```text
Business:
    "Tôi cần lưu Story."

Không quan tâm:
    SQLite?
    PostgreSQL?
    Redis?
    HTTP?
    Memory?
```

Business chỉ định nghĩa:

```python
class StoryWriter(Protocol):

    def save(self, story):
        ...
```

Infrastructure thích nghi với nó.

---

# 49. Bài tập 1 — Refactoring DIP

Cho code:

```python
import sqlite3


class UserService:

    def create_user(self, name):

        conn = sqlite3.connect("users.db")

        conn.execute(
            "INSERT INTO users(name) VALUES (?)",
            (name,),
        )

        conn.commit()
        conn.close()
```

Hãy refactor thành:

```text
UserService
      ↓
UserRepository
      ↑
SQLiteUserRepository
```

Yêu cầu:

* `UserService` không import `sqlite3`
* `UserService` không biết SQL
* Repository là `Protocol`
* SQLite nằm trong infrastructure

---

# 50. Bài tập 2 — DIP + Test

Sau khi refactor, tạo:

```python
class FakeUserRepository:
    ...
```

Test:

```python
def test_create_user():
    ...
```

Test không được:

```text
tạo database thật
```

và không được:

```text
import sqlite3
```

---

# 51. Bài tập 3 — Clock

Refactor:

```python
from datetime import datetime


class SubscriptionService:

    def activate(self, subscription):
        subscription.activated_at = datetime.now()
```

thành:

```text
SubscriptionService
       ↓
Clock
       ↑
SystemClock
```

Sau đó tạo:

```text
FakeClock
```

để test chính xác timestamp.

---

# 52. Bài tập 4 — Crawler

Cho:

```python
class CrawlWorker:

    def __init__(self):
        self.queue = RedisQueue()
        self.crawler = SiteACrawler()
        self.repository = SqliteStoryRepository()
```

Đây là một **DIP smell**.

Hãy refactor thành:

```text
CrawlWorker
   ↓
TaskQueue
StoryCrawler
StoryWriter
```

và:

```text
Composition Root
       ↓
RedisQueue
SiteACrawler
SqliteStoryRepository
       ↓
CrawlWorker
```

---

# 53. Bài tập 5 — Phân biệt DI và DIP

Giải thích hai đoạn:

### A

```python
class Service:

    def __init__(self, repository):
        self.repository = repository
```

### B

```python
class Service:

    def __init__(self):
        self.repository = SqliteRepository()
```

Câu hỏi:

1. A có DI không?
2. B có DI không?
3. A có đảm bảo DIP không?
4. Nếu `repository` là concrete infrastructure class thì sao?

---

# 54. Bài tập tổng hợp SOLID

Thiết kế:

```text
Story Application
```

Có:

```text
CLI
UseCase
Repository
Crawler
Queue
SQLite
HTTP
```

Yêu cầu:

```text
Domain
Application
Infrastructure
Presentation
```

Áp dụng:

```text
SRP
OCP
LSP
ISP
DIP
```

Dependency graph phải thể hiện rõ.

---

# 55. SOLID hoàn chỉnh

Sau 9 buổi:

```text
             SOLID
               │
 ┌─────────────┼──────────────┐
 │             │              │
SRP           OCP            LSP
 │             │              │
 │             │              │
 └─────────────┼──────────────┘
               ↓
              ISP
               ↓
              DIP
               ↓
       Architecture Design
```

Điểm quan trọng nhất:

```text
SOLID
  ↓
không phải 5 checklist
  ↓
mà là cách suy nghĩ về coupling
  ↓
responsibility
  ↓
abstraction
  ↓
dependency
  ↓
change
```

---

# 56. Roadmap tiếp theo

Bạn đã hoàn thành:

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive + Refactoring
✅ Buổi 4 — OCP
✅ Buổi 5 — LSP
✅ Buổi 6 — LSP Deep Dive
✅ Buổi 7 — ISP
✅ Buổi 8 — ISP Deep Dive
✅ Buổi 9 — DIP
```

**Nhưng chưa nên dừng ở đây.**

Bước tiếp theo tôi khuyên là một phần **SOLID thực chiến**, nơi chúng ta không học thêm principle mà lấy một codebase Python "rối" rồi refactor từng bước:

```text
Phần IV — SOLID Architecture & Refactoring

Buổi 10 — SOLID Code Smells
Buổi 11 — Detecting SRP Violations
Buổi 12 — OCP Refactoring Patterns
Buổi 13 — LSP Violations thực tế
Buổi 14 — ISP + Protocol Design
Buổi 15 — DIP + Dependency Injection
Buổi 16 — Composition Root
Buổi 17 — SOLID + Repository Pattern
Buổi 18 — SOLID + Service Layer
Buổi 19 — SOLID + Clean Architecture
Buổi 20 — SOLID + Plugin Architecture
Buổi 21 — SOLID + Testing
Buổi 22 — Refactoring một codebase xấu
Buổi 23 — SOLID Architecture cho Crawler
Buổi 24 — Final Project
```

**Buổi 10 nên bắt đầu bằng `SOLID Code Smells`**, vì lúc này bạn đã biết đủ 5 nguyên lý; mục tiêu tiếp theo là học cách **nhìn một đoạn Python code và nhận ra ngay nó đang vi phạm SRP/OCP/LSP/ISP/DIP ở đâu**.
