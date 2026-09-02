# Python OOP Master — Buổi 31

## Dependency Inversion Principle — DIP

Hôm nay chúng ta hoàn thành **5 nguyên lý SOLID**.

```text
S — Single Responsibility
O — Open/Closed
L — Liskov Substitution
I — Interface Segregation
D — Dependency Inversion
```

Trong 5 nguyên lý, **DIP đặc biệt quan trọng** vì nó kết nối trực tiếp với những thứ bạn đã học:

```text
Composition
    ↓
Dependency Injection
    ↓
Interface
    ↓
DIP
    ↓
Clean Architecture
    ↓
DDD
```

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Dependency là gì?
* Dependency Inversion là gì?
* DIP khác DI như thế nào?
* High-level module / Low-level module
* Tại sao `Service → SQLiteRepository` là coupling xấu?
* Cách đảo dependency
* DIP + ABC
* DIP + Protocol
* DIP + Dependency Injection
* DIP + Repository Pattern
* DIP + Clean Architecture
* DIP trong project crawler/reader của bạn

---

# 2. Dependency là gì?

Giả sử:

```python
class OrderService:

    def __init__(self):
        self.repository = SQLiteOrderRepository()
```

`OrderService` phụ thuộc vào:

```text
SQLiteOrderRepository
```

Ta có:

```text
OrderService
      ↓
SQLiteOrderRepository
```

`OrderService` là **high-level module**.

`SQLiteOrderRepository` là **low-level module**.

---

# 3. High-level và Low-level

Hiểu đơn giản:

### High-level module

Chứa:

```text
business logic
application logic
use case
```

Ví dụ:

```text
OrderService
Crawler
ReadingService
PaymentService
```

### Low-level module

Chứa implementation kỹ thuật:

```text
SQLite
HTTP
Redis
File
Email
API
```

Ví dụ:

```text
SQLiteOrderRepository
HttpxClient
RedisCache
FileStorage
SMTPEmailSender
```

---

# 4. Thiết kế xấu

Ví dụ:

```python
class OrderService:

    def __init__(self):
        self.repository = SQLiteOrderRepository()

    def create_order(self, order):
        self.repository.save(order)
```

Dependency:

```text
OrderService
     │
     ↓
SQLiteOrderRepository
     │
     ↓
SQLite
```

Vấn đề:

`OrderService` biết quá nhiều về infrastructure.

Nó biết:

```text
SQLite
```

Nếu ngày mai chuyển sang:

```text
PostgreSQL
```

phải sửa `OrderService`.

Nếu chuyển sang:

```text
MongoDB
```

lại sửa.

Nếu test:

```text
MemoryRepository
```

cũng phải sửa.

---

# 5. DIP nói gì?

Dependency Inversion Principle:

> **High-level modules should not depend on low-level modules. Both should depend on abstractions.**

Và:

> **Abstractions should not depend on details. Details should depend on abstractions.**

Hiểu đơn giản:

Thay vì:

```text
High-level
    ↓
Low-level
```

hãy thiết kế:

```text
High-level
    ↓
Abstraction
    ↑
Low-level
```

Đây chính là **Dependency Inversion**.

---

# 6. Đảo dependency

Trước:

```text
OrderService
     ↓
SQLiteOrderRepository
```

Sau:

```text
             OrderRepository
              ↑          ↑
              │          │
      OrderService   SQLiteRepository
```

Hoặc nhìn theo dependency:

```text
OrderService
     ↓
OrderRepository
     ↑
SQLiteOrderRepository
```

`OrderService` không còn phụ thuộc trực tiếp vào SQLite.

---

# 7. Viết abstraction

```python
from abc import ABC, abstractmethod


class OrderRepository(ABC):

    @abstractmethod
    def save(self, order):
        pass
```

SQLite:

```python
class SQLiteOrderRepository(OrderRepository):

    def save(self, order):
        print("Save order to SQLite")
```

Service:

```python
class OrderService:

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order):
        self.repository.save(order)
```

Bây giờ:

```text
OrderService
     ↓
OrderRepository
     ↑
SQLiteOrderRepository
```

Đây chính là DIP.

---

# 8. DIP và DI khác nhau

Hai khái niệm này rất dễ nhầm.

## Dependency Injection

Là **cách truyền dependency vào object**.

Ví dụ:

```python
class OrderService:

    def __init__(self, repository):
        self.repository = repository
```

Ta inject:

```python
repository = SQLiteOrderRepository()

service = OrderService(repository)
```

Đây là:

```text
DI
```

---

## Dependency Inversion

Là **nguyên tắc thiết kế dependency**.

Thay vì:

```text
Service → SQLite
```

ta muốn:

```text
Service → Abstraction ← SQLite
```

Đây là:

```text
DIP
```

---

# 9. Quan hệ

Có thể nhớ:

```text
DIP
 ↓
Xác định dependency nên hướng về abstraction

DI
 ↓
Cách cung cấp implementation cho abstraction
```

Ví dụ:

```text
DIP:
OrderService → OrderRepository

DI:
OrderService(SQLiteOrderRepository())
```

---

# 10. Composition Root

Đây là nơi rất quan trọng.

Application có thể wiring:

```python
repository = SQLiteOrderRepository()

service = OrderService(
    repository=repository
)
```

Ta gọi nơi này là:

```text
Composition Root
```

Nó chịu trách nhiệm:

```text
create objects
+
connect dependencies
```

Business logic không cần tự tạo infrastructure.

---

# 11. Thiết kế tốt

```text
                    Application
                         │
                         ↓
                  OrderService
                         │
                         ↓
                 OrderRepository
                         ↑
                         │
              SQLiteOrderRepository
                         │
                         ↓
                      SQLite
```

Dependency direction:

```text
Application
    ↓
Abstraction
    ↑
Infrastructure
```

---

# 12. Ví dụ Payment

Thiết kế xấu:

```python
class PaymentService:

    def __init__(self):
        self.gateway = StripePaymentGateway()

    def pay(self, amount):
        self.gateway.pay(amount)
```

Ta có:

```text
PaymentService
      ↓
StripePaymentGateway
```

Nếu chuyển sang:

```text
PayPal
MoMo
VNPay
```

phải sửa `PaymentService`.

---

# 13. Áp dụng DIP

Abstraction:

```python
from abc import ABC, abstractmethod


class PaymentGateway(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

Stripe:

```python
class StripePaymentGateway(PaymentGateway):

    def pay(self, amount):
        print(f"Stripe: {amount}")
```

MoMo:

```python
class MoMoPaymentGateway(PaymentGateway):

    def pay(self, amount):
        print(f"MoMo: {amount}")
```

Service:

```python
class PaymentService:

    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway

    def pay(self, amount):
        self.gateway.pay(amount)
```

Composition Root:

```python
gateway = StripePaymentGateway()

service = PaymentService(gateway)

service.pay(100)
```

Hoặc:

```python
gateway = MoMoPaymentGateway()

service = PaymentService(gateway)
```

Không cần sửa:

```python
PaymentService
```

---

# 14. Đây chính là sức mạnh của DIP

Thêm:

```python
class PayPalGateway(PaymentGateway):

    def pay(self, amount):
        print(f"PayPal: {amount}")
```

Không cần sửa:

```text
PaymentService
```

Ta có:

```text
                 PaymentGateway
                 ↑      ↑      ↑
                 │      │      │
              Stripe   MoMo   PayPal
                 ↑
                 │
          PaymentService
```

Kết hợp:

```text
OCP + LSP + DIP
```

---

# 15. DIP và OCP

Ở Buổi 28:

```text
OCP
```

chúng ta muốn mở rộng:

```text
Stripe
MoMo
PayPal
```

mà không sửa:

```text
PaymentService
```

DIP cung cấp nền tảng:

```text
PaymentService
      ↓
PaymentGateway
```

Các implementation:

```text
Stripe
MoMo
PayPal
```

phụ thuộc vào abstraction.

Do đó:

```text
DIP
 ↓
OCP
```

hỗ trợ lẫn nhau.

---

# 16. DIP và LSP

Ta có:

```python
class PaymentGateway(ABC):
    ...
```

và:

```text
StripePaymentGateway
MoMoPaymentGateway
PayPalPaymentGateway
```

DIP nói:

```text
PaymentService
    ↓
PaymentGateway
```

LSP nói:

```text
StripePaymentGateway
MoMoPaymentGateway
PayPalPaymentGateway
```

phải thực sự thay thế được:

```text
PaymentGateway
```

Do đó:

```text
DIP + LSP
```

đi cùng nhau.

---

# 17. DIP và ISP

Ở Buổi 30 ta đã tách:

```text
StoryReader
StoryWriter
StoryDeleter
```

Bây giờ DIP giúp:

```text
ReadingService
       ↓
StoryReader
       ↑
SQLiteStoryRepository
```

thay vì:

```text
ReadingService
       ↓
SQLiteStoryRepository
```

Vậy:

```text
ISP
 ↓
Interface nhỏ
 ↓
DIP
 ↓
High-level phụ thuộc interface
```

---

# 18. Áp dụng vào Story Crawler

Đây là phần quan trọng nhất đối với project của bạn.

Ta có:

```text
Crawler
```

Crawler cần:

```text
HTTP Client
Parser
Repository
Logger
```

Thiết kế xấu:

```python
class Crawler:

    def __init__(self):
        self.client = HttpxClient()
        self.parser = SiteAParser()
        self.repository = SQLiteStoryRepository()
        self.logger = FileLogger()
```

Crawler đang phụ thuộc trực tiếp vào:

```text
Httpx
SiteA
SQLite
File
```

Đây là coupling rất mạnh.

---

# 19. Thiết kế theo DIP

Tạo abstraction:

```python
class HttpClient(ABC):

    @abstractmethod
    def get(self, url):
        pass
```

Parser:

```python
class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

Repository:

```python
class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass
```

Logger:

```python
class Logger(ABC):

    @abstractmethod
    def info(self, message):
        pass
```

Crawler:

```python
class Crawler:

    def __init__(
        self,
        client: HttpClient,
        parser: StoryParser,
        repository: StoryRepository,
        logger: Logger,
    ):
        self.client = client
        self.parser = parser
        self.repository = repository
        self.logger = logger
```

Bây giờ:

```text
                    Crawler
                  /    |    \
                 /     |     \
                ↓      ↓      ↓
          HttpClient Parser Repository
             ↑         ↑         ↑
           HTTPX     SiteA     SQLite
```

---

# 20. Composition Root

Infrastructure được wiring ở bên ngoài:

```python
def build_crawler():

    client = HttpxClient()
    parser = SiteAParser()
    repository = SQLiteStoryRepository()
    logger = FileLogger()

    return Crawler(
        client=client,
        parser=parser,
        repository=repository,
        logger=logger,
    )
```

Đây là một Composition Root đơn giản.

Crawler không biết:

```text
HttpxClient
SQLiteStoryRepository
FileLogger
```

được tạo thế nào.

---

# 21. Testing trở nên rất dễ

Ta tạo Fake:

```python
class FakeRepository(StoryRepository):

    def __init__(self):
        self.items = []

    def save(self, story):
        self.items.append(story)
```

Fake HTTP client:

```python
class FakeHttpClient(HttpClient):

    def __init__(self, html):
        self.html = html

    def get(self, url):
        return self.html
```

Fake parser:

```python
class FakeParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Test Story"
        }
```

Fake logger:

```python
class FakeLogger(Logger):

    def info(self, message):
        pass
```

Test:

```python
crawler = Crawler(
    client=FakeHttpClient("<html>"),
    parser=FakeParser(),
    repository=FakeRepository(),
    logger=FakeLogger(),
)
```

Không cần:

```text
Internet
SQLite
real website
real logger
```

Đây là một trong những lợi ích lớn nhất của DIP.

---

# 22. DIP + Clean Architecture

Đây là lúc các kiến thức trước bắt đầu kết nối.

Clean Architecture thường hướng dependency vào trong:

```text
                Infrastructure
                     ↓
            ┌─────────────────┐
            │   Application   │
            └─────────────────┘
                     ↓
               Domain
```

Nhưng dependency source code cần hướng:

```text
Infrastructure
      ↓
Application abstraction
      ↓
Domain
```

Ví dụ:

```text
infrastructure/
    sqlite_repository.py

application/
    interfaces/
        story_repository.py

domain/
    story.py
```

Infrastructure implement interface:

```python
class SQLiteStoryRepository(StoryRepository):
    ...
```

Application chỉ biết:

```python
StoryRepository
```

---

# 23. Dependency direction

Không nên:

```text
Domain
  ↓
SQLite
```

Mà:

```text
Domain
  ↑
Application
  ↑
Infrastructure
```

Hoặc chính xác hơn về dependency source:

```text
Infrastructure
      ↓
Application abstraction
      ↓
Domain
```

Điểm quan trọng:

> **Database là detail. Business rule không nên phụ thuộc database.**

---

# 24. Ví dụ Domain

Domain entity:

```python
class Story:

    def __init__(self, title):
        if not title:
            raise ValueError("Title required")

        self.title = title
```

Domain không cần:

```python
import sqlite3
```

Không cần:

```python
import httpx
```

Không cần:

```python
import PySide6
```

Business rule đứng độc lập.

---

# 25. Application Layer

```python
class CreateStoryUseCase:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, title):
        story = Story(title)

        self.repository.save(story)

        return story
```

Use case phụ thuộc:

```text
StoryRepository
```

không phụ thuộc:

```text
SQLiteStoryRepository
```

---

# 26. Infrastructure Layer

```python
class SQLiteStoryRepository(StoryRepository):

    def __init__(self, connection):
        self.connection = connection

    def save(self, story):
        self.connection.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (story.title,)
        )

        self.connection.commit()
```

Infrastructure biết:

```text
SQLite
```

nhưng:

```text
CreateStoryUseCase
```

không cần biết SQLite.

---

# 27. Toàn bộ flow

```text
                  UI / CLI
                     │
                     ↓
             CreateStoryUseCase
                     │
                     ↓
              StoryRepository
                     ↑
                     │
          SQLiteStoryRepository
                     │
                     ↓
                   SQLite
```

Dependency:

```text
UseCase → abstraction
Infrastructure → abstraction
```

Đây chính là DIP.

---

# 28. DIP + Repository Pattern

Repository Pattern thường được dùng để tạo abstraction:

```text
Business/Application
        ↓
Repository Interface
        ↑
Concrete Repository
```

Ví dụ:

```python
class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass

    @abstractmethod
    def get(self, story_id):
        pass
```

Concrete:

```python
class SQLiteStoryRepository(StoryRepository):
    ...
```

hoặc:

```python
class PostgreSQLStoryRepository(StoryRepository):
    ...
```

hoặc:

```python
class MemoryStoryRepository(StoryRepository):
    ...
```

Application không cần thay đổi.

---

# 29. DIP + Database

Đây là một tư duy quan trọng:

Không nên:

```text
Business Logic
      ↓
SQLite
```

Mà:

```text
Business Logic
      ↓
Repository
      ↑
SQLite
```

Ngày mai đổi:

```text
SQLite
```

thành:

```text
PostgreSQL
```

business logic không cần biết.

---

# 30. DIP + HTTPX

Crawler:

```python
class HttpClient(Protocol):

    def get(self, url: str) -> str:
        ...
```

Implementation:

```python
class HttpxClient:

    def get(self, url: str) -> str:
        ...
```

Crawler:

```python
class Crawler:

    def __init__(self, client: HttpClient):
        self.client = client
```

Test:

```python
class FakeHttpClient:

    def get(self, url: str) -> str:
        return "<html>test</html>"
```

Ta có:

```text
Crawler
  ↓
HttpClient
  ↑
HttpxClient

Crawler
  ↓
HttpClient
  ↑
FakeHttpClient
```

Rất sạch.

---

# 31. DIP + Protocol

Trong Python hiện đại, không nhất thiết phải tạo rất nhiều ABC.

Ví dụ:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

SQLite:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

Memory:

```python
class MemoryStoryRepository:

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

Use case:

```python
class StoryService:

    def __init__(self, repository: StoryRepository):
        self.repository = repository
```

Đây là DIP theo kiểu structural typing.

---

# 32. DIP không có nghĩa “mọi thứ đều phải interface”

Đây là lỗi rất phổ biến khi mới học SOLID.

Không nên biến:

```python
class StringFormatter:
    ...
```

thành:

```text
IStringFormatter
StringFormatter
IStringFormatterFactory
IStringFormatterProvider
```

chỉ vì DIP.

Hãy tìm **dependency boundary thực sự cần đảo**.

Ví dụ:

```text
Database
HTTP API
Message Queue
File System
Clock
External Service
```

thường là các boundary đáng quan tâm.

---

# 33. DIP và Stable Core

Một cách tư duy rất hay:

```text
Stable Business Rules
        ↑
        │
     Abstraction
        ↑
        │
   Volatile Details
```

Business logic thường:

```text
thay đổi ít
```

Infrastructure:

```text
thay đổi nhiều
```

Ví dụ:

```text
SQLite
↓
PostgreSQL
↓
Redis
↓
API
```

Business rule:

```text
Story
Chapter
Crawler policy
Reading rule
```

không nên bị kéo theo những thay đổi infrastructure.

---

# 34. Dependency Inversion trong project thực tế

Một kiến trúc phù hợp với project crawler/reader:

```text
src/
└── app/
    │
    ├── domain/
    │   ├── entities/
    │   │   ├── story.py
    │   │   └── chapter.py
    │   │
    │   └── services/
    │
    ├── application/
    │   ├── use_cases/
    │   │
    │   └── ports/
    │       ├── story_repository.py
    │       ├── http_client.py
    │       └── story_parser.py
    │
    └── infrastructure/
        ├── sqlite/
        │   └── story_repository.py
        │
        ├── http/
        │   └── httpx_client.py
        │
        └── parsers/
            ├── site_a.py
            ├── site_b.py
            └── site_c.py
```

Dependency:

```text
infrastructure
      ↓
application ports
      ↓
domain
```

---

# 35. Composition Root cuối cùng

Ví dụ:

```python
def build_application():

    repository = SQLiteStoryRepository(...)
    client = HttpxClient(...)
    parser = SiteAParser(...)

    crawler = Crawler(
        client=client,
        parser=parser,
        repository=repository,
    )

    return crawler
```

Điều này rất quan trọng:

```text
Infrastructure wiring
```

nằm ở:

```text
Composition Root
```

không nằm trong:

```text
Domain
Application
Use Case
```

---

# 36. DIP và Dependency Injection Container

Khi project lớn, bạn có thể dùng DI container.

Nhưng Python không bắt buộc.

Plain Python:

```python
repository = SQLiteRepository()

service = StoryService(repository)
```

đã là Dependency Injection.

Không cần:

```text
DI framework
```

trừ khi project thật sự cần.

---

# 37. Một lỗi thiết kế phổ biến

Code:

```python
class StoryService:

    def __init__(
        self,
        repository=None,
    ):
        self.repository = (
            repository
            or SQLiteStoryRepository()
        )
```

Có vẻ tiện.

Nhưng nó làm:

```text
StoryService
      ↓
SQLiteStoryRepository
```

vẫn tồn tại.

Nếu muốn DIP rõ ràng:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository
```

Composition Root chịu trách nhiệm:

```python
service = StoryService(
    SQLiteStoryRepository()
)
```

---

# 38. So sánh DI và DIP

|                    | DI                    | DIP                           |
| ------------------ | --------------------- | ----------------------------- |
| Bản chất           | Technique             | Design Principle              |
| Mục tiêu           | Cung cấp dependency   | Đảo hướng dependency          |
| Ví dụ              | Constructor injection | Service → abstraction         |
| Liên quan          | Wiring                | Architecture                  |
| Có thể dùng riêng? | Có                    | Cần abstraction để đạt đầy đủ |

Nhớ:

```text
DI = HOW
DIP = WHERE dependency should point
```

---

# 39. SOLID hoàn chỉnh

Đến đây:

```text
S — SRP
    ↓
Một trách nhiệm rõ ràng

O — OCP
    ↓
Mở rộng không sửa core

L — LSP
    ↓
Subclass phải thay thế được abstraction

I — ISP
    ↓
Interface nhỏ, cohesive

D — DIP
    ↓
High-level phụ thuộc abstraction
```

Có thể kết nối:

```text
SRP
 ↓
Component nhỏ
 ↓
ISP
 ↓
Interface nhỏ
 ↓
DIP
 ↓
High-level → abstraction
 ↓
DI
 ↓
Implementation được inject
 ↓
LSP
 ↓
Implementation phải tuân contract
 ↓
OCP
 ↓
Dễ mở rộng
```

---

# 40. Ví dụ SOLID hoàn chỉnh

Ta xây:

```text
StoryCrawler
```

### Abstractions

```python
class HttpClient(Protocol):

    def get(self, url: str) -> str:
        ...


class StoryParser(Protocol):

    def parse(self, html: str):
        ...


class StoryRepository(Protocol):

    def save(self, story):
        ...
```

Crawler:

```python
class StoryCrawler:

    def __init__(
        self,
        client: HttpClient,
        parser: StoryParser,
        repository: StoryRepository,
    ):
        self.client = client
        self.parser = parser
        self.repository = repository

    def crawl(self, url):
        html = self.client.get(url)

        story = self.parser.parse(html)

        self.repository.save(story)

        return story
```

Infrastructure:

```python
class HttpxClient:
    ...
```

```python
class SiteAParser:
    ...
```

```python
class SQLiteStoryRepository:
    ...
```

Composition:

```python
crawler = StoryCrawler(
    client=HttpxClient(),
    parser=SiteAParser(),
    repository=SQLiteStoryRepository(),
)
```

Ta có:

```text
                    StoryCrawler
                  /      |       \
                 ↓       ↓        ↓
           HttpClient Parser Repository
              ↑         ↑         ↑
            HTTPX     SiteA      SQLite
```

Đây là một thiết kế SOLID cơ bản nhưng rất thực tế.

---

# 41. Kiểm tra 5 nguyên lý trên kiến trúc này

### SRP

`StoryCrawler`:

```text
orchestrate crawling
```

không tự:

```text
HTTP
SQL
HTML parsing
```

✅

### OCP

Thêm:

```text
SiteBParser
```

không sửa Crawler.

✅

### LSP

`SiteAParser`, `SiteBParser` tuân cùng contract.

✅

### ISP

Crawler chỉ cần:

```text
get()
parse()
save()
```

không phụ thuộc interface khổng lồ.

✅

### DIP

Crawler phụ thuộc:

```text
abstraction
```

không phụ thuộc:

```text
HTTPX
SQLite
```

✅

---

# 42. Bài tập 1 — Refactor

Cho code:

```python
class OrderService:

    def __init__(self):
        self.repository = SQLiteOrderRepository()

    def create(self, order):
        self.repository.save(order)
```

Hãy refactor theo DIP.

Yêu cầu:

```text
OrderService
    ↓
OrderRepository
    ↑
SQLiteOrderRepository
```

---

# 43. Bài tập 2 — Payment

Thiết kế:

```text
PaymentService
       ↓
PaymentGateway
       ↑
 ┌─────┼─────┐
 ↓     ↓     ↓
Stripe MoMo PayPal
```

Sau đó:

```python
PaymentService(MoMoPaymentGateway())
```

phải hoạt động mà không sửa `PaymentService`.

---

# 44. Bài tập 3 — Crawler

Thiết kế:

```text
Crawler
   ↓
HttpClient
Parser
Repository
Logger
```

với:

```text
HttpxClient
SiteAParser
SQLiteRepository
FileLogger
```

Tất cả implementation phải được inject từ bên ngoài.

---

# 45. Bài tập 4 — Testing

Tạo:

```text
FakeHttpClient
FakeParser
FakeRepository
FakeLogger
```

Sau đó test:

```python
crawler = Crawler(
    client=FakeHttpClient(...),
    parser=FakeParser(),
    repository=FakeRepository(),
    logger=FakeLogger(),
)
```

Không được:

```text
Internet
SQLite
File system
```

---

# 46. Bài tập 5 — Architecture Challenge

Thiết kế hoàn chỉnh:

```text
                 UI / CLI
                    │
                    ↓
              CrawlStoryUseCase
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   HttpClient     Parser     Repository
        ↑           ↑           ↑
     HTTPX        SiteA      SQLite
                   SiteB
                   SiteC
```

Yêu cầu:

* Domain không import SQLite
* Domain không import HTTPX
* Use case không tạo SQLiteRepository
* Use case không tạo HttpxClient
* Parser có thể thay thế
* Repository có thể thay thế
* Có Fake implementation cho test
* Wiring nằm trong Composition Root

Nếu làm được bài này, bạn đã bắt đầu tư duy ở mức **architecture**, không chỉ OOP syntax.

---

# 47. Một câu cực kỳ quan trọng

Hãy nhớ:

```text
❌ Business → Detail

✅ Business → Abstraction ← Detail
```

Ví dụ:

```text
❌
StoryService → SQLite

✅
StoryService → StoryRepository ← SQLite
```

Hoặc:

```text
❌
Crawler → HTTPX

✅
Crawler → HttpClient ← HTTPX
```

Hoặc:

```text
❌
PaymentService → Stripe

✅
PaymentService → PaymentGateway ← Stripe
```

---

# 48. Tổng kết toàn bộ SOLID

Bạn đã hoàn thành phần **SOLID Foundation**:

```text
┌────────────────────────────────────┐
│              SOLID                 │
├────────────────────────────────────┤
│ S  Single Responsibility           │
│ O  Open/Closed                     │
│ L  Liskov Substitution             │
│ I  Interface Segregation           │
│ D  Dependency Inversion            │
└────────────────────────────────────┘
```

Và quan trọng hơn, bạn đã học được chuỗi tư duy:

```text
Composition
      ↓
Aggregation
      ↓
Dependency Injection
      ↓
SRP
      ↓
OCP
      ↓
LSP
      ↓
ISP
      ↓
DIP
```

Trong project crawler/reader:

```text
                    Application
                         │
                         ↓
                      Crawler
                  ┌──────┼──────┐
                  ↓      ↓      ↓
             HttpClient Parser Repository
                  ↑      ↑      ↑
                HTTPX   SiteA  SQLite
                        SiteB
                        SiteC
```

Đây chính là nền tảng để bước sang phần tiếp theo:

## **Phần IX — Design Patterns**

```text
Buổi 32 — Singleton
Buổi 33 — Factory
Buổi 34 — Builder
Buổi 35 — Strategy
Buổi 36 — Observer
Buổi 37 — Command
Buổi 38 — Repository Pattern
```

Đặc biệt **Buổi 32 — Singleton** sẽ rất thú vị vì chúng ta sẽ phân tích cả **Singleton truyền thống, Singleton trong Python, module singleton, thread-safety và vì sao Singleton thường bị lạm dụng**.
