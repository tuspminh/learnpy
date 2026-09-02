# Python OOP Master — Buổi 26

# Dependency Injection — DI

Buổi 25 chúng ta đã học **Aggregation**:

```text
Crawler
   │
   ├── Repository
   ├── HTTP Client
   └── Parser
```

Các dependency được truyền từ bên ngoài vào.

Hôm nay chúng ta đi sâu vào kỹ thuật đứng phía sau kiến trúc đó:

> **Dependency Injection — DI**

Đây là một trong những kỹ thuật quan trọng nhất để viết Python code **loose coupling, dễ test và dễ mở rộng**.

---

# 1. Dependency là gì?

Trước tiên phải hiểu từ **dependency**.

Ví dụ:

```python
class OrderService:

    def __init__(self):
        self.repository = OrderRepository()
```

`OrderService` cần `OrderRepository`.

Ta nói:

```text
OrderService
      ↓
OrderRepository
```

`OrderRepository` là **dependency** của `OrderService`.

Hay:

```python
class Crawler:

    def __init__(self):
        self.client = HttpClient()
        self.parser = StoryParser()
        self.repository = StoryRepository()
```

Crawler phụ thuộc vào:

```text
HttpClient
StoryParser
StoryRepository
```

---

# 2. Vấn đề khi tự tạo dependency

Code này rất phổ biến:

```python
class Crawler:

    def __init__(self):
        self.client = HttpClient()
        self.parser = StoryParser()
        self.repository = SQLiteStoryRepository()
```

Thoạt nhìn rất tiện.

Nhưng:

```text
Crawler
 ├── HttpClient
 ├── StoryParser
 └── SQLiteStoryRepository
```

`Crawler` biết quá nhiều về implementation.

---

# 3. Vấn đề thứ nhất — Testing

Muốn test `Crawler`.

Ta không muốn test thật:

```text
HTTP
SQLite
Parser
Network
```

Nhưng Crawler lại tự tạo:

```python
SQLiteStoryRepository()
```

Ta rất khó thay thế nó.

---

# 4. Vấn đề thứ hai — thay đổi implementation

Hôm nay:

```python
SQLiteStoryRepository
```

Ngày mai muốn:

```python
PostgresStoryRepository
```

Crawler lại phải sửa:

```python
class Crawler:

    def __init__(self):
        self.repository = PostgresStoryRepository()
```

Điều này làm tăng coupling.

---

# 5. Dependency Injection là gì?

Dependency Injection nghĩa đơn giản là:

> **Thay vì class tự tạo dependency, dependency được cung cấp từ bên ngoài.**

### Không DI

```python
class Crawler:

    def __init__(self):
        self.repository = SQLiteStoryRepository()
```

### Có DI

```python
class Crawler:

    def __init__(self, repository):
        self.repository = repository
```

Bên ngoài:

```python
repository = SQLiteStoryRepository()

crawler = Crawler(repository)
```

Sơ đồ:

```text
             tạo dependency
                   │
                   ▼
        SQLiteStoryRepository
                   │
                   │ inject
                   ▼
                Crawler
```

---

# 6. Constructor Injection

Đây là kiểu DI phổ biến nhất trong Python.

```python
class Crawler:

    def __init__(self, repository):
        self.repository = repository
```

Sử dụng:

```python
repository = SQLiteStoryRepository()

crawler = Crawler(repository)
```

Đây gọi là:

> **Constructor Injection**

Dependency được inject thông qua constructor.

---

# 7. Ví dụ đơn giản

```python
class EmailSender:

    def send(self, message):
        print(f"Sending: {message}")
```

Service:

```python
class UserService:

    def __init__(self, email_sender):
        self.email_sender = email_sender

    def register(self, username):
        print(f"Register {username}")

        self.email_sender.send(
            f"Welcome {username}"
        )
```

Bên ngoài:

```python
sender = EmailSender()

service = UserService(sender)

service.register("alice")
```

Ta có:

```text
EmailSender
      │
      │ inject
      ▼
 UserService
```

`UserService` không cần biết cách tạo `EmailSender`.

---

# 8. DI giúp thay thế implementation

Giả sử có:

```python
class EmailSender:

    def send(self, message):
        print(f"Email: {message}")
```

Sau này có:

```python
class SmsSender:

    def send(self, message):
        print(f"SMS: {message}")
```

Service không cần sửa:

```python
class UserService:

    def __init__(self, sender):
        self.sender = sender

    def notify(self, message):
        self.sender.send(message)
```

Có thể dùng:

```python
service = UserService(
    EmailSender()
)
```

hoặc:

```python
service = UserService(
    SmsSender()
)
```

Đây chính là **polymorphism + DI**.

---

# 9. DI + Abstract Base Class

Bây giờ thiết kế chuyên nghiệp hơn.

```python
from abc import ABC, abstractmethod


class MessageSender(ABC):

    @abstractmethod
    def send(self, message):
        pass
```

Email:

```python
class EmailSender(MessageSender):

    def send(self, message):
        print(f"Email: {message}")
```

SMS:

```python
class SmsSender(MessageSender):

    def send(self, message):
        print(f"SMS: {message}")
```

Service:

```python
class NotificationService:

    def __init__(self, sender: MessageSender):
        self.sender = sender

    def notify(self, message):
        self.sender.send(message)
```

Sử dụng:

```python
service = NotificationService(
    EmailSender()
)

service.notify("Hello")
```

Hoặc:

```python
service = NotificationService(
    SmsSender()
)

service.notify("Hello")
```

---

# 10. Dependency Inversion

Đây chính là nơi DI liên quan tới **SOLID**.

Ta muốn:

```text
High-level
NotificationService
       │
       ▼
   Interface
       ▲
       │
Low-level
EmailSender
SmsSender
```

Thay vì:

```text
NotificationService
       │
       ▼
EmailSender
```

`NotificationService` phụ thuộc abstraction:

```python
MessageSender
```

chứ không phụ thuộc implementation cụ thể.

Đây chính là tư duy của:

> **Dependency Inversion Principle — DIP**

Buổi 31 chúng ta sẽ học DIP rất sâu.

---

# 11. DI và Unit Test

Đây là một trong những lợi ích lớn nhất.

Production:

```python
service = NotificationService(
    EmailSender()
)
```

Test:

```python
class FakeSender:

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)
```

Test:

```python
fake = FakeSender()

service = NotificationService(fake)

service.notify("Hello")

assert fake.messages == ["Hello"]
```

Không cần:

```text
SMTP
Internet
Email Server
```

---

# 12. DI trong Crawler của bạn

Đây là ví dụ rất quan trọng.

Ta có:

```text
Crawler
 │
 ├── HTTP Client
 ├── Parser
 ├── Repository
 └── Logger
```

Thay vì:

```python
class Crawler:

    def __init__(self):
        self.client = HttpClient()
        self.parser = StoryParser()
        self.repository = SQLiteStoryRepository()
        self.logger = Logger()
```

hãy viết:

```python
class Crawler:

    def __init__(
        self,
        client,
        parser,
        repository,
        logger,
    ):
        self.client = client
        self.parser = parser
        self.repository = repository
        self.logger = logger
```

Bên ngoài:

```python
crawler = Crawler(
    client=HttpClient(),
    parser=StoryParser(),
    repository=SQLiteStoryRepository(),
    logger=Logger(),
)
```

Đây là Constructor Injection.

---

# 13. DI giúp thay Parser

Giả sử:

```python
class SiteAParser:
    def parse(self, html):
        ...


class SiteBParser:
    def parse(self, html):
        ...
```

Crawler:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

Site A:

```python
crawler = Crawler(
    SiteAParser()
)
```

Site B:

```python
crawler = Crawler(
    SiteBParser()
)
```

Không cần:

```python
if site == "site_a":
    ...
elif site == "site_b":
    ...
```

Đây là:

```text
DI
 +
Polymorphism
 +
Open/Closed Principle
```

---

# 14. DI theo Interface

Ta có thể định nghĩa:

```python
from abc import ABC, abstractmethod


class Parser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

Implementation:

```python
class SiteAParser(Parser):

    def parse(self, html):
        return {
            "title": "Story A"
        }


class SiteBParser(Parser):

    def parse(self, html):
        return {
            "title": "Story B"
        }
```

Crawler:

```python
class Crawler:

    def __init__(self, parser: Parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

Kiến trúc:

```text
                 Parser
                   ▲
             ┌─────┴─────┐
             │           │
        SiteAParser  SiteBParser
             ▲           ▲
             └─────┬─────┘
                   │
                Crawler
```

---

# 15. DI không nhất thiết cần ABC

Python rất mạnh về **Duck Typing**.

Ta có thể viết:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

Không cần:

```python
Parser
```

Miễn object có:

```python
parse()
```

thì sử dụng được.

Ví dụ:

```python
class FakeParser:

    def parse(self, html):
        return {"title": "Test"}
```

Inject:

```python
crawler = Crawler(
    FakeParser()
)
```

Đây là:

> **Dependency Injection + Duck Typing**

rất tự nhiên trong Python.

---

# 16. Ba kiểu Dependency Injection

Trong thực tế thường gặp:

```text
1. Constructor Injection
2. Setter Injection
3. Method Injection
```

---

## 16.1 Constructor Injection

Phổ biến nhất:

```python
class Service:

    def __init__(self, repository):
        self.repository = repository
```

Dùng khi dependency là **bắt buộc**.

---

## 16.2 Setter Injection

```python
class Service:

    def set_repository(self, repository):
        self.repository = repository
```

Sử dụng:

```python
service = Service()

service.set_repository(repository)
```

Trong Python thường ít ưu tiên hơn Constructor Injection.

---

## 16.3 Method Injection

Dependency chỉ cần cho một operation:

```python
class ReportService:

    def generate(self, repository):
        data = repository.get_data()
        ...
```

`repository` chỉ tồn tại trong method đó.

---

# 17. Khi nào chọn kiểu nào?

| Kiểu        | Khi nào dùng                 |
| ----------- | ---------------------------- |
| Constructor | Dependency bắt buộc          |
| Setter      | Dependency tùy chọn/thay đổi |
| Method      | Chỉ cần cho một operation    |

Trong code production, ưu tiên:

```text
Constructor Injection
```

vì object được tạo ra ở trạng thái hợp lệ.

---

# 18. DI và Default Dependency

Có thể gặp:

```python
class Service:

    def __init__(self, repository=None):
        if repository is None:
            repository = SQLiteRepository()

        self.repository = repository
```

Cách này tiện:

```python
service = Service()
```

nhưng cũng có nhược điểm.

Class vừa:

```text
nhận dependency
```

vừa:

```text
quyết định implementation
```

Do đó nếu xây Clean Architecture nghiêm túc, thường nên để **composition root** quyết định implementation.

---

# 19. Composition Root

Đây là khái niệm rất quan trọng cho những project lớn.

Ta có:

```text
Application
     │
     ▼
Composition Root
     │
     ├── tạo Repository
     ├── tạo HTTP Client
     ├── tạo Parser
     ├── tạo Service
     └── tạo Crawler
```

Ví dụ:

```python
def build_application():

    repository = SQLiteStoryRepository()
    client = HttpClient()
    parser = StoryParser()
    logger = Logger()

    crawler = Crawler(
        client=client,
        parser=parser,
        repository=repository,
        logger=logger,
    )

    return crawler
```

Sau đó:

```python
crawler = build_application()
```

`Crawler` không còn chịu trách nhiệm tạo dependency.

---

# 20. DI trong Clean Architecture

Một kiến trúc điển hình:

```text
┌──────────────────────────────┐
│       Composition Root       │
│                              │
│   tạo tất cả dependencies    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Application Layer      │
│                              │
│          Service             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          Interface           │
│                              │
│       Repository             │
└──────────────┬───────────────┘
               ▲
               │
┌──────────────┴───────────────┐
│       Infrastructure         │
│                              │
│    SQLiteRepository          │
└──────────────────────────────┘
```

Đây chính là kiến trúc mà sau này bạn có thể áp dụng cho app crawler/reading.

---

# 21. DI với Repository Pattern

Ví dụ:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass

    @abstractmethod
    def get(self, story_id):
        pass
```

SQLite:

```python
class SQLiteStoryRepository(StoryRepository):

    def save(self, story):
        print("SQLite save")

    def get(self, story_id):
        print("SQLite get")
```

Service:

```python
class StoryService:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def create_story(self, story):
        self.repository.save(story)
```

Composition root:

```python
repository = SQLiteStoryRepository()

service = StoryService(repository)
```

Quan hệ:

```text
SQLiteStoryRepository
          │
          │ inject
          ▼
     StoryService
```

---

# 22. DI + SQLite / PostgreSQL

Ngày hôm nay:

```python
service = StoryService(
    SQLiteStoryRepository()
)
```

Sau này:

```python
service = StoryService(
    PostgreSQLStoryRepository()
)
```

`StoryService` không đổi.

Đây chính là lợi ích của:

```text
Interface
   +
Polymorphism
   +
Dependency Injection
```

---

# 23. Một ví dụ hoàn chỉnh

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass


class SQLiteStoryRepository(StoryRepository):

    def save(self, story):
        print(f"SQLite: {story}")


class FakeStoryRepository(StoryRepository):

    def __init__(self):
        self.stories = []

    def save(self, story):
        self.stories.append(story)


class StoryService:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def create(self, story):
        self.repository.save(story)
```

Production:

```python
repository = SQLiteStoryRepository()

service = StoryService(repository)

service.create("Python OOP")
```

Testing:

```python
repository = FakeStoryRepository()

service = StoryService(repository)

service.create("Python Testing")

assert repository.stories == [
    "Python Testing"
]
```

Một class:

```python
StoryService
```

không biết:

```text
SQLite
Fake
PostgreSQL
Memory
```

Nó chỉ biết:

```text
StoryRepository
```

Đây là thiết kế tốt.

---

# 24. DI không phải là Framework

Một hiểu lầm phổ biến:

> Dependency Injection = phải dùng framework DI.

Không.

Python thuần đã đủ:

```python
repository = SQLiteRepository()

service = Service(repository)
```

Đó đã là Dependency Injection.

Bạn **không cần** framework.

---

# 25. DI Container

Khi application rất lớn, có thể xuất hiện:

```text
DI Container
```

Ví dụ ý tưởng:

```text
Container
   │
   ├── Repository
   ├── Service
   ├── Parser
   ├── Client
   └── Logger
```

Container chịu trách nhiệm:

```text
create
wire
inject
```

Nhưng **không nên dùng DI container quá sớm**.

Trong Python, explicit wiring thường dễ đọc hơn:

```python
repository = SQLiteRepository()
service = StoryService(repository)
controller = StoryController(service)
```

---

# 26. Nguyên tắc vàng

Khi thiết kế class, hãy hỏi:

> **Class này có nên tự tạo dependency không?**

Nếu dependency là một thành phần bên ngoài:

```python
Repository
HttpClient
Logger
Parser
Database
Clock
EmailSender
```

thì thường nên:

```python
class Service:

    def __init__(self, dependency):
        self.dependency = dependency
```

thay vì:

```python
class Service:

    def __init__(self):
        self.dependency = ConcreteDependency()
```

---

# 27. Bài tập thực hành

## Bài 1 — Payment

Tạo:

```text
PaymentGateway
    ├── PaypalGateway
    └── StripeGateway

PaymentService
```

`PaymentService` phải nhận gateway bằng Constructor Injection:

```python
service = PaymentService(
    StripeGateway()
)
```

và:

```python
service = PaymentService(
    PaypalGateway()
)
```

Không được viết:

```python
class PaymentService:

    def __init__(self):
        self.gateway = StripeGateway()
```

---

# 28. Bài tập 2 — Crawler

Thiết kế:

```text
Crawler
 ├── HttpClient
 ├── Parser
 ├── Repository
 └── Logger
```

Tất cả đều phải được inject:

```python
crawler = Crawler(
    client=...,
    parser=...,
    repository=...,
    logger=...,
)
```

Không dependency nào được Crawler tự tạo.

---

# 29. Bài tập 3 — Test

Tạo:

```text
FakeHttpClient
FakeParser
FakeRepository
FakeLogger
```

Sau đó:

```python
crawler = Crawler(
    client=FakeHttpClient(),
    parser=FakeParser(),
    repository=FakeRepository(),
    logger=FakeLogger(),
)
```

Mục tiêu:

```text
Không Network
Không SQLite
Không File
Không External Service
```

nhưng vẫn test được toàn bộ flow của Crawler.

---

# 30. Bài tập kiến trúc — rất quan trọng

Hãy thiết kế:

```text
CLI
 │
 ▼
CrawlerService
 │
 ├── StoryRepository
 ├── Parser
 ├── HttpClient
 └── Logger
```

Trong đó:

```text
Application
    ↓
Interface
    ↓
Infrastructure
```

Ví dụ:

```text
StoryRepository
       ▲
       │
SQLiteStoryRepository
```

và:

```text
Parser
  ▲
  │
SelectolaxParser
```

Cuối cùng tạo object ở một nơi duy nhất:

```python
def build_crawler():
    ...
```

Đây chính là bước đầu tiên để bạn xây một **Composition Root** thực sự.

---

# 31. Tổng kết Buổi 26

Bạn cần nắm chắc chuỗi tư duy này:

```text
Dependency
     ↓
Class phụ thuộc object khác
     ↓
Không tự tạo dependency
     ↓
Inject từ bên ngoài
     ↓
Dependency Injection
     ↓
Loose Coupling
     ↓
Dễ Testing
     ↓
Polymorphism
     ↓
DIP / SOLID
```

Đặc biệt nhớ:

```python
# Tight coupling
class Service:
    def __init__(self):
        self.repository = SQLiteRepository()
```

vs:

```python
# Loose coupling
class Service:
    def __init__(self, repository):
        self.repository = repository
```

Và kiến trúc thực tế:

```text
              Composition Root
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Repository      Parser      HttpClient
        │            │            │
        └────────────┼────────────┘
                     ▼
                  Crawler
```

**Buổi 27** sẽ chuyển từ kỹ thuật DI sang **SOLID — Single Responsibility Principle (SRP)**: làm thế nào nhận biết một class đang có “quá nhiều trách nhiệm”, và refactor một `Crawler`/`Service` lớn thành kiến trúc sạch hơn.
