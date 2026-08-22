# SOLID Deep Dive — Buổi 12

# DIP Deep Dive — Dependency Inversion trong kiến trúc Python

Bạn đang nhảy thẳng tới **Buổi 12**, nên tôi sẽ tiếp tục đúng roadmap và xem đây là bài **DIP Deep Dive**, tập trung vào kiến trúc thực tế.

Roadmap phần DIP:

```text
Buổi 11 — DIP
    ↓
Buổi 12 — DIP Deep Dive
    ├── Constructor Injection
    ├── Method Injection
    ├── Factory Injection
    ├── Composition Root
    ├── Abstract Factory
    ├── Protocol
    ├── Testing
    ├── Mock / Fake
    ├── Port & Adapter
    └── Clean Architecture
```

---

# 1. Nhắc lại DIP

DIP:

> High-level modules should not depend on low-level modules. Both should depend on abstractions.

Và:

> Abstractions should not depend on details. Details should depend on abstractions.

Ví dụ **vi phạm DIP**:

```python
class UserService:

    def __init__(self):
        self.repo = SQLiteUserRepository()

    def get_user(self, user_id):
        return self.repo.get_by_id(user_id)
```

Dependency:

```text
UserService
    ↓
SQLiteUserRepository
    ↓
SQLite
```

`UserService` biết quá nhiều về infrastructure.

---

# 2. Dependency Inversion

Ta đảo dependency:

```text
                UserRepository
                      ↑
             ┌────────┴────────┐
             │                 │
      SQLiteRepository   PostgresRepository
```

Application:

```text
UserService
     ↓
UserRepository
```

Không còn:

```text
UserService
     ↓
SQLite
```

Đây chính là **Dependency Inversion**.

---

# 3. DIP không phải DI

Hai khái niệm rất dễ nhầm.

## DIP

Là **nguyên lý kiến trúc**:

```text
High-level
    ↓
Abstraction
    ↑
Low-level
```

## Dependency Injection

Là **kỹ thuật truyền dependency**:

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

DI là một cách rất phổ biến để thực hiện DIP.

Nhưng:

> **DI ≠ DIP**

---

# 4. Constructor Injection

Đây là dạng quan trọng nhất.

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

Composition:

```python
repo = SQLiteUserRepository()

service = UserService(repo)
```

Dependency graph:

```text
Composition Root
       │
       ├── SQLiteUserRepository
       │
       └── UserService
                ↓
             repo
```

---

# 5. Tại sao Constructor Injection tốt?

Dependency trở thành:

```text
explicit
```

Nhìn constructor:

```python
def __init__(
    self,
    repo,
):
```

ta biết:

> `UserService` cần repository để hoạt động.

Không cần đọc implementation bên trong.

---

# 6. Constructor Injection và Invariant

Constructor Injection còn đảm bảo:

```text
Object được tạo
    ↓
Dependency đã tồn tại
    ↓
Object ở trạng thái hợp lệ
```

Ví dụ:

```python
class UserService:

    def __init__(self, repo):
        if repo is None:
            raise ValueError("repo required")

        self.repo = repo
```

Không có trạng thái:

```text
UserService
    ↓
repo = None
```

---

# 7. Method Injection

Đôi khi dependency chỉ cần cho một operation.

Ví dụ:

```python
class ReportService:

    def generate(self, exporter, data):
        return exporter.export(data)
```

Gọi:

```python
service.generate(
    PdfExporter(),
    data,
)
```

Dependency:

```text
generate()
    ↓
exporter
```

---

# 8. Khi nào dùng Method Injection?

Khi dependency:

```text
không phải dependency của toàn object
```

mà chỉ cần:

```text
một operation cụ thể
```

Ví dụ:

```python
class ImageService:

    def process(self, storage, image):
        ...
```

Nếu chỉ một method cần `storage`, không nhất thiết phải:

```python
ImageService(storage)
```

---

# 9. Constructor vs Method Injection

|             | Constructor | Method    |
| ----------- | ----------- | --------- |
| Scope       | object      | operation |
| Dependency  | persistent  | temporary |
| Explicit    | rất cao     | cao       |
| Thường dùng | ⭐⭐⭐⭐⭐       | ⭐⭐⭐       |
| Test        | dễ          | dễ        |

Quy tắc thực tế:

> Dependency là requirement của object → Constructor Injection.

> Dependency chỉ cần cho một operation → Method Injection có thể phù hợp.

---

# 10. Factory Injection

Một số trường hợp không cần dependency là object.

Ta cần:

> **một factory có khả năng tạo object.**

Ví dụ:

```python
class OrderService:

    def __init__(self, payment_factory):
        self.payment_factory = payment_factory
```

Sau đó:

```python
payment = self.payment_factory.create(
    order.payment_method
)
```

Dependency:

```text
OrderService
      ↓
PaymentFactory
      ↓
PaymentGateway
```

---

# 11. Tại sao Factory Injection cần thiết?

Giả sử:

```python
class OrderService:

    def create_payment(self, method):

        if method == "card":
            return StripePayment()

        if method == "momo":
            return MomoPayment()
```

Service đang biết infrastructure.

Ta có thể đưa việc tạo object ra ngoài:

```python
class OrderService:

    def __init__(self, payment_factory):
        self.payment_factory = payment_factory
```

Bây giờ:

```python
payment = self.payment_factory.create(method)
```

---

# 12. Factory cũng có thể vi phạm DIP

Đừng nghĩ:

```text
Factory = automatically good
```

Ví dụ:

```python
class PaymentFactory:

    def create(self, method):

        if method == "stripe":
            return StripePayment()

        elif method == "momo":
            return MomoPayment()
```

Nếu factory nằm trong application layer:

```text
Application
    ↓
Factory
    ↓
Stripe
```

thì dependency vẫn có thể sai.

Cần xem **factory thuộc layer nào**.

---

# 13. Composition Root

Đây là một trong những khái niệm quan trọng nhất của DIP.

> **Composition Root là nơi application graph được lắp ráp.**

Ví dụ:

```python
def create_application():

    repo = SQLiteUserRepository()

    service = UserService(repo)

    return service
```

Ở đây:

```text
create_application()
```

biết:

```text
SQLiteUserRepository
UserService
```

Điều này **không xấu**.

Ngược lại, đây chính là nơi phù hợp để biết implementation cụ thể.

---

# 14. Tại sao Composition Root quan trọng?

Ta muốn:

```text
Business
    ↓
Abstraction
```

nhưng ở đâu đó phải có:

```text
Abstraction
    ↑
Concrete implementation
```

Nếu không:

```text
Ai tạo SQLiteUserRepository?
```

Composition Root trả lời câu hỏi đó.

---

# 15. Dependency Graph

Ví dụ:

```text
main.py
   │
   ├── SQLiteUserRepository
   │
   ├── UserService
   │       ↓
   │   UserRepository
   │
   └── UserController
           ↓
       UserService
```

`main.py` biết mọi thứ.

Nhưng:

```text
UserService
```

không cần biết:

```text
SQLite
```

Đây là dependency direction tốt.

---

# 16. Nguyên tắc rất quan trọng

> **Concrete dependencies nên được đẩy ra ngoài rìa hệ thống.**

Ví dụ:

```text
                APPLICATION
                     │
                     ↓
                abstraction
                     ↑
                     │
              INFRASTRUCTURE
```

Infrastructure nằm ở edge.

---

# 17. Protocol

Python rất phù hợp với DIP nhờ `Protocol`.

```python
from typing import Protocol


class UserRepository(Protocol):

    def get_by_id(self, user_id: int):
        ...

    def save(self, user):
        ...
```

Service:

```python
class UserService:

    def __init__(
        self,
        repo: UserRepository,
    ):
        self.repo = repo
```

SQLite:

```python
class SQLiteUserRepository:

    def get_by_id(self, user_id):
        ...

    def save(self, user):
        ...
```

Không cần:

```python
class SQLiteUserRepository(UserRepository):
```

Đây là **structural typing**.

---

# 18. DIP + Duck Typing

Thậm chí abstraction có thể chỉ tồn tại conceptually.

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

Miễn:

```python
repo.get_by_id(...)
repo.save(...)
```

hoạt động.

Python vốn đã có:

> **Duck Typing**

`Protocol` giúp chúng ta biến contract ngầm thành contract rõ ràng hơn cho type checker.

---

# 19. DIP + ABC

Có thể dùng:

```python
from abc import ABC, abstractmethod


class UserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id):
        ...
```

Sau đó:

```python
class SQLiteUserRepository(UserRepository):

    def get_by_id(self, user_id):
        ...
```

ABC phù hợp khi bạn muốn:

```text
explicit inheritance
+
runtime abstract contract
```

Nhưng với Python application architecture:

> `Protocol` thường rất linh hoạt.

---

# 20. Abstraction nên thuộc về ai?

Đây là câu hỏi cực kỳ quan trọng.

Sai lầm phổ biến:

```text
infrastructure/
    repository_interface.py
```

rồi application phụ thuộc abstraction do infrastructure định nghĩa.

Trong nhiều kiến trúc tốt hơn:

```text
application/
    ports.py
```

hoặc:

```text
domain/
    repositories.py
```

Application/domain nói:

> "Tôi cần capability này."

Infrastructure nói:

> "Tôi cung cấp capability này."

---

# 21. Port & Adapter

Đây chính là cách nhìn rất mạnh.

```text
             Application
                  │
               Port
                  ↑
                  │
             Adapter
```

Ví dụ:

```text
UserRepository
```

là Port.

```text
SQLiteUserRepository
```

là Adapter.

```text
PostgresUserRepository
```

cũng là Adapter.

---

# 22. Architecture

Ta có:

```text
                    Application
                         │
                         ↓
                  UserRepository
                         ↑
              ┌──────────┴──────────┐
              │                     │
      SQLiteUserRepository   PostgresUserRepository
```

Dependency:

```text
Application → abstraction
Infrastructure → abstraction
```

Không phải:

```text
Application → Infrastructure
```

Đó chính là DIP.

---

# 23. Testing — Đây là nơi DIP phát huy sức mạnh

Code không tốt:

```python
class UserService:

    def __init__(self):
        self.repo = SQLiteUserRepository()
```

Test:

```text
UserService
    ↓
SQLite
    ↓
database
```

Test trở nên khó.

---

# 24. Với DIP

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

Test:

```python
fake_repo = FakeUserRepository()

service = UserService(fake_repo)
```

Không cần SQLite.

Không cần file database.

Không cần infrastructure.

---

# 25. Fake

Ví dụ:

```python
class FakeUserRepository:

    def __init__(self):
        self.users = {}

    def get_by_id(self, user_id):
        return self.users.get(user_id)

    def save(self, user):
        self.users[user.id] = user
```

Test:

```python
def test_create_user():

    repo = FakeUserRepository()

    service = UserService(repo)

    service.create_user(
        user_id=1,
        name="Alice",
    )

    user = repo.get_by_id(1)

    assert user.name == "Alice"
```

Đây là một test rất sạch.

---

# 26. Fake vs Mock

Đừng lạm dụng Mock.

### Fake

Có implementation đơn giản:

```text
FakeRepository
```

### Mock

Kiểm tra interaction:

```text
repo.save(...)
```

Ví dụ conceptual:

```python
mock_repo.save.assert_called_once()
```

Fake thường phù hợp khi muốn test behavior.

Mock phù hợp khi interaction chính là thứ cần kiểm tra.

---

# 27. DIP làm giảm Test Coupling

Không có DIP:

```text
Test
 ↓
Service
 ↓
SQLite
 ↓
Database
```

Có DIP:

```text
Test
 ↓
Service
 ↓
Fake Repository
```

Test phụ thuộc ít hơn vào infrastructure.

---

# 28. Một lỗi phổ biến: Service Locator

Ví dụ:

```python
class UserService:

    def create_user(self):
        repo = container.get(
            "UserRepository"
        )
```

Nghe có vẻ dependency injection.

Nhưng dependency bị ẩn.

Constructor:

```python
UserService()
```

không cho biết:

```text
UserService cần UserRepository
```

Đây là:

> **Hidden Dependency**

---

# 29. Constructor Injection tốt hơn Service Locator

Tốt:

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo
```

Nhìn signature là biết:

```text
UserService
    requires
UserRepository
```

Dependency rõ ràng.

---

# 30. Container có phải xấu?

Không.

Dependency Injection Container có thể hữu ích trong hệ thống lớn.

Nhưng:

```text
Container
```

nên nằm ở:

```text
Composition Root
```

thay vì business logic.

Business code không nên:

```python
container.get(...)
```

ở khắp nơi.

---

# 31. DIP trong Clean Architecture

Đây là nơi DIP trở nên cực kỳ quan trọng.

Ví dụ:

```text
┌───────────────────────────────┐
│        Presentation           │
│                               │
│ Controller / CLI / Flet       │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│        Application            │
│                               │
│ Use Cases                     │
│ Ports                         │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│           Domain              │
│                               │
│ Entity / Value Object         │
│ Business Rules                │
└───────────────────────────────┘
                ↑
                │
┌───────────────┴───────────────┐
│       Infrastructure          │
│                               │
│ SQLite / HTTP / Redis / FS    │
└───────────────────────────────┘
```

Điểm quan trọng:

```text
Infrastructure
       ↓
implements
       ↓
Application abstraction
```

---

# 32. Ví dụ Clean Architecture

Domain:

```python
class User:

    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
```

Application port:

```python
from typing import Protocol


class UserRepository(Protocol):

    def get_by_id(self, user_id: int) -> User | None:
        ...

    def save(self, user: User) -> None:
        ...
```

Use case:

```python
class CreateUser:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, user_id, name):
        user = User(user_id, name)

        self.repo.save(user)

        return user
```

Infrastructure:

```python
class SQLiteUserRepository:

    def save(self, user):
        ...

    def get_by_id(self, user_id):
        ...
```

Composition Root:

```python
repo = SQLiteUserRepository()

use_case = CreateUser(repo)
```

---

# 33. Dependency Direction

Điều quan trọng nhất:

```text
BEFORE

Application
     ↓
SQLite
```

Sau DIP:

```text
Application
     ↓
UserRepository
     ↑
SQLite
```

Mũi tên dependency đã đảo.

Đó là lý do gọi là:

> **Dependency Inversion**

---

# 34. DIP không phải "mọi class đều phải có interface"

Đây là một anti-pattern.

Sai:

```python
class UserNameFormatterInterface:
    ...

class UserNameFormatter:
    ...
```

chỉ vì:

> "SOLID yêu cầu abstraction."

Không.

Hãy hỏi:

```text
Có variation không?
Có boundary không?
Có dependency cần đảo không?
Có testability cần cải thiện không?
```

Nếu không:

```python
def format_name(name):
    return name.strip().title()
```

có thể hoàn toàn đủ.

---

# 35. DIP và Abstraction Boundary

Một abstraction tốt thường nằm ở boundary:

```text
HTTP
Database
Filesystem
Queue
Payment
Email
Crawler
```

Ví dụ:

```text
UserService
    ↓
UserRepository
```

```text
OrderService
    ↓
PaymentGateway
```

```text
CrawlerUseCase
    ↓
HttpClient
```

```text
ExportService
    ↓
FileStorage
```

---

# 36. Một ví dụ lớn hơn

Code xấu:

```python
class CrawlStoryUseCase:

    def __init__(self):
        self.db = SQLiteDatabase()
        self.http = RequestsClient()
        self.parser = BeautifulSoupParser()

    def execute(self, url):

        html = self.http.get(url)

        story = self.parser.parse(html)

        self.db.save(story)

        return story
```

Use case đang biết:

```text
SQLite
requests
BeautifulSoup
```

Đây là high-level code phụ thuộc details.

---

# 37. Sau DIP

Ports:

```python
class HttpClient(Protocol):

    def get(self, url: str) -> str:
        ...
```

```python
class StoryParser(Protocol):

    def parse(self, html: str):
        ...
```

```python
class StoryRepository(Protocol):

    def save(self, story):
        ...
```

Use case:

```python
class CrawlStoryUseCase:

    def __init__(
        self,
        http: HttpClient,
        parser: StoryParser,
        repo: StoryRepository,
    ):
        self.http = http
        self.parser = parser
        self.repo = repo

    def execute(self, url):

        html = self.http.get(url)

        story = self.parser.parse(html)

        self.repo.save(story)

        return story
```

Bây giờ:

```text
UseCase
 ├── HttpClient
 ├── StoryParser
 └── StoryRepository
```

Không biết implementation.

---

# 38. Composition Root

Cuối cùng:

```python
def create_app():

    http = RequestsHttpClient()

    parser = BeautifulSoupStoryParser()

    repo = SQLiteStoryRepository()

    use_case = CrawlStoryUseCase(
        http=http,
        parser=parser,
        repo=repo,
    )

    return use_case
```

Đây là nơi duy nhất cần biết concrete implementation.

---

# 39. Đây là kiến trúc rất mạnh cho project của bạn

Có thể tổ chức crawler framework:

```text
src/
└── crawler/
    ├── domain/
    │   ├── entities/
    │   └── value_objects/
    │
    ├── application/
    │   ├── use_cases/
    │   └── ports/
    │
    ├── infrastructure/
    │   ├── http/
    │   ├── database/
    │   └── parser/
    │
    └── composition/
        └── bootstrap.py
```

Dependency:

```text
domain
  ↑
application
  ↑
composition
  ↑
infrastructure
```

Nhưng xét theo **dependency import**, infrastructure implementation có thể import abstraction của application:

```text
application
    ↑
infrastructure
```

và composition root kết nối chúng.

---

# 40. DIP + OCP

Hai nguyên lý này phối hợp rất mạnh.

OCP:

```text
Thêm implementation
không sửa core
```

DIP:

```text
Core không phụ thuộc implementation
```

Kết hợp:

```text
                  Abstraction
                 ↑           ↑
                 │           │
          Implementation A  B
                 ↑
                 │
             Core logic
```

---

# 41. DIP + ISP

ISP:

> Interface nên nhỏ.

DIP:

> High-level module nên phụ thuộc abstraction.

Nếu abstraction quá lớn:

```python
class Crawler(Protocol):

    def crawl(): ...
    def parse(): ...
    def download(): ...
    def login(): ...
    def upload(): ...
    def notify(): ...
```

DIP vẫn có thể đúng về hướng dependency nhưng abstraction quá lớn.

ISP giúp:

```text
Crawler
Parser
Downloader
Authenticator
Notifier
```

Kết hợp:

```text
DIP + ISP
```

sẽ tạo boundary tốt hơn.

---

# 42. DIP + SRP

Nếu class:

```text
UserService
```

vừa:

```text
business logic
database
email
logging
HTTP
```

thì DIP một mình không giải quyết hết.

SRP giúp tách responsibility.

Sau đó DIP giúp đảo dependency.

```text
SRP
 ↓
separate concerns
 ↓
DIP
 ↓
invert dependencies
```

---

# 43. DIP + LSP

Nếu bạn inject:

```python
repo: UserRepository
```

thì implementation:

```text
SQLiteRepository
PostgresRepository
FakeRepository
```

phải thực sự thay thế được abstraction.

Đó chính là LSP.

Vậy SOLID bắt đầu kết nối thành một hệ thống:

```text
SRP
 ↓
separate responsibility

OCP
 ↓
isolate variation

LSP
 ↓
safe substitution

ISP
 ↓
small contracts

DIP
 ↓
invert dependency
```

---

# 44. Một Mental Model hoàn chỉnh

Khi thiết kế:

```text
1. What changes?
       ↓
2. Separate responsibility
       ↓
3. Identify variation
       ↓
4. Define small contract
       ↓
5. Depend on abstraction
       ↓
6. Inject implementation
       ↓
7. Compose at the boundary
```

Đây là cách SOLID phối hợp.

---

# 45. Checklist DIP

Khi review một class, hãy hỏi:

### Dependency có explicit không?

```python
def __init__(self, repo)
```

hay hidden:

```python
container.get(...)
```

### High-level có biết infrastructure không?

```python
SQLiteUserRepository()
```

Nếu có, cần xem lại.

### Abstraction nằm ở đâu?

```text
domain/application?
infrastructure?
```

### Dependency direction là gì?

```text
business → infrastructure
```

hay:

```text
business → abstraction
infrastructure → abstraction
```

### Có thực sự cần abstraction?

Đừng tạo interface chỉ vì SOLID.

---

# 46. Bài tập 1

Code:

```python
class OrderService:

    def __init__(self):
        self.payment = StripePayment()

    def pay(self, amount):
        return self.payment.charge(amount)
```

Hãy refactor thành:

```text
OrderService
      ↓
PaymentGateway
      ↑
StripePayment
```

Sử dụng `Protocol`.

---

# 47. Bài tập 2

Code:

```python
class ReportService:

    def __init__(self):
        self.db = SQLiteDatabase()

    def generate(self):
        data = self.db.fetch()
        return self.build_report(data)
```

Thiết kế:

```text
ReportService
      ↓
ReportDataSource
      ↑
SQLiteDataSource
PostgresDataSource
FakeDataSource
```

---

# 48. Bài tập 3 — Crawler

Refactor:

```python
class Crawler:

    def crawl(self, url):

        client = RequestsClient()

        html = client.get(url)

        parser = BeautifulSoup(html)

        db = SQLiteDatabase()

        db.save(parser.parse())
```

thành:

```text
CrawlUseCase
    ↓
HttpClient
    ↑
RequestsClient

CrawlUseCase
    ↓
StoryParser
    ↑
BeautifulSoupParser

CrawlUseCase
    ↓
StoryRepository
    ↑
SQLiteStoryRepository
```

---

# 49. Bài tập 4 — Composition Root

Tạo:

```python
def create_crawler_app():
    ...
```

Nó phải là nơi duy nhất biết:

```text
RequestsClient
BeautifulSoupParser
SQLiteStoryRepository
```

`CrawlUseCase` không được import trực tiếp ba implementation trên.

---

# 50. Bài tập 5 — Testing

Viết:

```python
class FakeHttpClient:
    ...
```

```python
class FakeStoryParser:
    ...
```

```python
class FakeStoryRepository:
    ...
```

Sau đó test:

```text
CrawlUseCase
```

mà **không cần**:

```text
Internet
SQLite
BeautifulSoup
```

Đây là bài tập quan trọng nhất của Buổi 12.

---

# 51. Tổng kết toàn bộ SOLID

Sau Buổi 12, bạn có thể nhìn SOLID như sau:

```text
                    SOLID
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
       SRP           OCP           LSP
        │             │             │
   responsibility  variation   substitution
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                 ISP + DIP
                      │
             ┌────────┴────────┐
             ↓                 ↓
        small contracts    dependency
                           direction
```

---

# 52. Công thức thiết kế thực chiến

Nếu bắt đầu một Python application mới, hãy thử tư duy:

```text
                 BUSINESS
                    │
                    ↓
              Use Case / Service
                    │
            ┌───────┼────────┐
            ↓       ↓        ↓
           Port    Port      Port
            ↑       ↑        ↑
            │       │        │
         Adapter  Adapter  Adapter
            │       │        │
          SQLite    HTTP    Redis
```

Đây là một trong những hình thái kiến trúc quan trọng nhất bạn cần nắm nếu muốn đi tiếp sang:

* Clean Architecture
* Hexagonal Architecture
* Ports & Adapters
* DDD
* Repository Pattern
* Plugin Architecture
* Testable Architecture

---

# 53. Ba câu cần nhớ

Nếu chỉ nhớ ba câu sau:

> **DIP không nói "hãy dùng interface".**

> **DIP nói high-level policy không nên phụ thuộc vào low-level details.**

Và quan trọng nhất:

> **Hãy đẩy concrete implementation ra ngoài boundary và để business logic phụ thuộc vào abstraction.**

Mental model:

```text
❌ BAD

Business
   ↓
SQLite
   ↓
Database


✅ GOOD

             Repository
             ↑        ↑
             │        │
          Business   SQLite
```

---

## Roadmap đã hoàn thành

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive

✅ Buổi 4 — OCP
✅ Buổi 5 — OCP Deep Dive
✅ Buổi 6 — OCP thực chiến

⬜ Buổi 7 — LSP
⬜ Buổi 8 — LSP Deep Dive

⬜ Buổi 9 — ISP
⬜ Buổi 10 — ISP Deep Dive

✅ Buổi 11 — DIP
✅ Buổi 12 — DIP Deep Dive
```

**Điểm tiếp theo hợp lý là Buổi 7 — LSP**, rồi sau khi hoàn thành 5 nguyên lý chúng ta có thể làm một **SOLID Capstone**: lấy một codebase Python kiểu `God Service + if/elif + concrete DB + fat interface`, sau đó refactor toàn bộ theo **SRP → OCP → LSP → ISP → DIP** để thấy 5 nguyên lý phối hợp với nhau như thế nào.
