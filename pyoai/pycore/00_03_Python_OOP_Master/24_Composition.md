# Python OOP Master — Buổi 24

# Composition — Hợp thành

> Từ buổi 24, chúng ta chuyển từ **"học các tính năng của class"** sang **"học cách thiết kế class"**.
>
> Đây là bước rất quan trọng. Bạn đã biết:
>
> ```text
> Class
> Object
> Inheritance
> Polymorphism
> ABC
> Magic Method
> Static Method
> Class Method
> Factory
> ```
>
> Bây giờ chúng ta học cách **ghép các object với nhau để xây dựng hệ thống lớn**.

---

# 1. Composition là gì?

**Composition** nghĩa là một object **chứa và sử dụng** các object khác để thực hiện công việc.

Mô hình:

```text
Object A
   │
   ├── Object B
   ├── Object C
   └── Object D
```

Ví dụ:

```text
Car
 ├── Engine
 ├── Transmission
 └── Wheel
```

`Car` không cần kế thừa từ `Engine`.

Nó **có một Engine**.

Đây là quan hệ:

```text
Car HAS-A Engine
```

---

# 2. Composition khác Inheritance

Inheritance:

```text
Dog IS-A Animal
```

Composition:

```text
Car HAS-A Engine
```

Đây là hai cách tư duy hoàn toàn khác nhau.

| Inheritance               | Composition            |
| ------------------------- | ---------------------- |
| IS-A                      | HAS-A                  |
| `Dog(Animal)`             | `Car(Engine)`          |
| Quan hệ kế thừa           | Quan hệ chứa           |
| Coupling thường cao hơn   | Linh hoạt hơn          |
| Dễ tạo hierarchy phức tạp | Dễ thay thế dependency |

---

# 3. Ví dụ đơn giản

```python
class Engine:

    def start(self):
        print("Engine started")


class Car:

    def __init__(self, engine):
        self.engine = engine

    def start(self):
        self.engine.start()
        print("Car started")
```

Sử dụng:

```python
engine = Engine()

car = Car(engine)

car.start()
```

Kết quả:

```text
Engine started
Car started
```

Ở đây:

```python
self.engine
```

là một object `Engine` được `Car` chứa.

Đó chính là Composition.

---

# 4. Tại sao không kế thừa?

Sai thiết kế:

```python
class Car(Engine):
    pass
```

Điều này nói rằng:

```text
Car IS-A Engine
```

Điều này vô nghĩa.

Một chiếc xe **không phải là động cơ**.

Nó **có một động cơ**.

Đúng:

```python
class Car:

    def __init__(self, engine):
        self.engine = engine
```

---

# 5. Composition với nhiều object

```python
class Engine:

    def start(self):
        print("Engine started")


class GPS:

    def locate(self):
        print("Location found")


class MusicPlayer:

    def play(self):
        print("Playing music")


class Car:

    def __init__(
        self,
        engine,
        gps,
        music_player
    ):
        self.engine = engine
        self.gps = gps
        self.music_player = music_player

    def start(self):

        self.engine.start()
        self.gps.locate()
        self.music_player.play()
```

Sử dụng:

```python
car = Car(
    Engine(),
    GPS(),
    MusicPlayer()
)

car.start()
```

---

# 6. Đây chính là Dependency Injection

Bạn có thể nhận ra một điều:

```python
Car(
    Engine(),
    GPS(),
    MusicPlayer()
)
```

Các dependency được truyền vào constructor.

Đây chính là nền tảng của **Dependency Injection**.

Buổi 26 chúng ta sẽ học sâu hơn.

---

# 7. Composition không nhất thiết phải dùng Constructor

Có thể tạo dependency bên trong:

```python
class Car:

    def __init__(self):

        self.engine = Engine()
```

Nhưng cách này tạo coupling mạnh:

```text
Car
 ↓
Engine
```

`Car` quyết định luôn implementation.

---

# 8. Dependency Injection tốt hơn

```python
class Car:

    def __init__(self, engine):

        self.engine = engine
```

Bây giờ:

```python
car = Car(
    Engine()
)
```

Nhưng có thể thay:

```python
class ElectricEngine:

    def start(self):
        print("Electric engine started")
```

```python
car = Car(
    ElectricEngine()
)
```

`Car` không cần thay đổi.

Đây là sức mạnh của Composition.

---

# 9. Programming to Interface

Đây là tư duy cực kỳ quan trọng.

Không nên thiết kế:

```python
class Car:

    def __init__(
        self,
        engine: Engine
    ):
        ...
```

nếu `Car` thực sự chỉ cần:

```python
engine.start()
```

Ta có thể định nghĩa abstraction:

```python
from abc import ABC, abstractmethod


class Engine(ABC):

    @abstractmethod
    def start(self):
        pass
```

Sau đó:

```python
class GasEngine(Engine):

    def start(self):
        print("Gas engine")


class ElectricEngine(Engine):

    def start(self):
        print("Electric engine")
```

`Car`:

```python
class Car:

    def __init__(self, engine: Engine):
        self.engine = engine

    def start(self):
        self.engine.start()
```

---

# 10. Composition + Polymorphism

Đây là một pattern rất mạnh:

```text
             Engine
                ▲
         ┌──────┴──────┐
         │             │
    GasEngine    ElectricEngine
         │             │
         └──────┬──────┘
                │
               Car
```

`Car` không quan tâm engine thật là gì.

```python
car1 = Car(GasEngine())

car2 = Car(ElectricEngine())
```

Cả hai đều hoạt động.

---

# 11. Composition trong dự án Library

Giả sử xây dựng:

```text
Library
```

Library có:

```text
BookRepository
BookService
LibraryLogger
```

Không nên:

```python
class Library(
    BookRepository,
    BookService,
    Logger
):
    ...
```

Thay vào đó:

```python
class Library:

    def __init__(
        self,
        repository,
        service,
        logger
    ):
        self.repository = repository
        self.service = service
        self.logger = logger
```

Đây là Composition.

---

# 12. Ví dụ hoàn chỉnh

```python
class BookRepository:

    def save(self, book):
        print(
            f"Saving: {book}"
        )


class BookService:

    def validate(self, book):

        if not book:
            raise ValueError(
                "Book is required"
            )


class Logger:

    def info(self, message):

        print(
            f"[INFO] {message}"
        )


class Library:

    def __init__(
        self,
        repository,
        service,
        logger
    ):
        self.repository = repository
        self.service = service
        self.logger = logger

    def add_book(self, book):

        self.service.validate(book)

        self.repository.save(book)

        self.logger.info(
            f"Book added: {book}"
        )
```

Sử dụng:

```python
library = Library(
    repository=BookRepository(),
    service=BookService(),
    logger=Logger(),
)

library.add_book(
    "Python OOP"
)
```

Kết quả:

```text
Saving: Python OOP
[INFO] Book added: Python OOP
```

---

# 13. Nhìn vào kiến trúc

Ta có:

```text
Library
   │
   ├── BookRepository
   │
   ├── BookService
   │
   └── Logger
```

`Library` **compose** từ ba object.

Không cần inheritance.

---

# 14. Composition trong Sales Management

Project thứ hai của bạn có:

```text
Customer
Product
Invoice
Inventory
Report
```

Ta có thể thiết kế:

```text
SalesService
   │
   ├── CustomerRepository
   ├── ProductRepository
   ├── Inventory
   └── InvoiceService
```

Ví dụ:

```python
class SalesService:

    def __init__(
        self,
        customer_repo,
        product_repo,
        inventory,
        invoice_service
    ):
        self.customer_repo = customer_repo
        self.product_repo = product_repo
        self.inventory = inventory
        self.invoice_service = invoice_service
```

Đây là Composition.

---

# 15. Composition vs Inheritance

Ví dụ bạn có:

```text
Notification
```

Các loại:

```text
EmailNotification
SMSNotification
PushNotification
```

Đây là:

```text
EmailNotification IS-A Notification
```

→ Inheritance phù hợp.

Nhưng:

```text
Order
 ├── PaymentService
 ├── InventoryService
 └── NotificationService
```

Đây là:

```text
Order HAS-A PaymentService
Order HAS-A InventoryService
Order HAS-A NotificationService
```

→ Composition phù hợp.

---

# 16. "Favor Composition Over Inheritance"

Một nguyên tắc nổi tiếng trong OOP:

> **Favor composition over inheritance.**

Không có nghĩa:

> "Không được dùng inheritance."

Mà có nghĩa:

> Khi cả Composition và Inheritance đều giải quyết được vấn đề, hãy cân nhắc Composition trước.

---

# 17. Tại sao Composition linh hoạt?

Ví dụ:

```python
class FileLogger:

    def log(self, message):
        print("File:", message)


class ConsoleLogger:

    def log(self, message):
        print("Console:", message)
```

Application:

```python
class Application:

    def __init__(self, logger):
        self.logger = logger

    def run(self):
        self.logger.log(
            "Application started"
        )
```

Có thể thay:

```python
Application(
    FileLogger()
)
```

bằng:

```python
Application(
    ConsoleLogger()
)
```

Không sửa `Application`.

---

# 18. Composition + Strategy

Đây là cách Composition kết hợp với Strategy Pattern.

```python
class PaymentStrategy:

    def pay(self, amount):
        raise NotImplementedError
```

Các implementation:

```python
class CashPayment(PaymentStrategy):

    def pay(self, amount):
        print(
            f"Cash: {amount}"
        )
```

```python
class CardPayment(PaymentStrategy):

    def pay(self, amount):
        print(
            f"Card: {amount}"
        )
```

Service:

```python
class Checkout:

    def __init__(
        self,
        payment
    ):
        self.payment = payment

    def checkout(self, amount):

        self.payment.pay(amount)
```

Sử dụng:

```python
checkout = Checkout(
    CardPayment()
)

checkout.checkout(100)
```

---

# 19. Có thể thay Strategy runtime

Đây là ưu điểm rất lớn.

```python
checkout.payment = CashPayment()

checkout.checkout(100)
```

Không cần tạo lại `Checkout`.

Hoặc tốt hơn, tạo method:

```python
class Checkout:

    def __init__(self, payment):
        self.payment = payment

    def set_payment(self, payment):
        self.payment = payment
```

---

# 20. Composition và Test

Composition cực kỳ hữu ích khi Unit Test.

Ví dụ:

```python
class FakeRepository:

    def __init__(self):
        self.saved = []

    def save(self, book):
        self.saved.append(book)
```

Test:

```python
repo = FakeRepository()

library = Library(
    repository=repo,
    service=BookService(),
    logger=Logger()
)

library.add_book("Python")

assert repo.saved == [
    "Python"
]
```

Ta không cần database thật.

Đây là nền tảng của **Dependency Injection + Unit Testing**.

---

# 21. Composition trong Crawler

Đây là ví dụ rất gần với project của bạn.

```text
Crawler
   │
   ├── HTTP Client
   ├── Parser
   ├── Storage
   └── Logger
```

Code:

```python
class Crawler:

    def __init__(
        self,
        http_client,
        parser,
        storage,
        logger
    ):
        self.http_client = http_client
        self.parser = parser
        self.storage = storage
        self.logger = logger

    def crawl(self, url):

        html = self.http_client.get(url)

        data = self.parser.parse(html)

        self.storage.save(data)

        self.logger.info(
            f"Crawled: {url}"
        )
```

Đây là một ví dụ cực kỳ thực tế của Composition.

---

# 22. Kiến trúc

```text
                 Crawler
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
 HTTPClient      Parser       Storage
                                │
                                ▼
                              SQLite
```

Thay SQLite bằng PostgreSQL?

```python
Crawler(
    http_client,
    parser,
    PostgreSQLStorage(),
    logger
)
```

Crawler không cần biết.

---

# 23. Composition không có nghĩa là "chứa dữ liệu"

Điểm quan trọng:

Composition không chỉ là:

```python
self.engine = engine
```

Nó là việc một object **xây dựng hành vi của mình bằng cách hợp thành từ nhiều object khác**.

Ví dụ:

```text
Crawler
 = HTTPClient
 + Parser
 + Storage
 + Logger
```

Hành vi của `Crawler` được tạo nên từ các dependency đó.

---

# 24. Composition sâu

Có thể có:

```text
Application
   │
   └── LibraryService
          │
          ├── BookRepository
          │      └── Database
          │
          └── Logger
```

Tức là Composition có thể tạo thành một **object graph**.

```text
Application
     │
     ▼
LibraryService
  │       │
  ▼       ▼
Repo    Logger
  │
  ▼
Database
```

Đây chính là tư duy kiến trúc phần mềm.

---

# 25. Một ví dụ production-style

```python
from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def save(self, item):
        pass


class SQLiteRepository(Repository):

    def save(self, item):
        print(
            f"SQLite save: {item}"
        )


class Logger:

    def info(self, message):
        print(
            f"[INFO] {message}"
        )


class BookService:

    def __init__(
        self,
        repository: Repository,
        logger: Logger
    ):
        self.repository = repository
        self.logger = logger

    def create_book(self, title):

        if not title:
            raise ValueError(
                "Title is required"
            )

        self.repository.save(title)

        self.logger.info(
            f"Created book: {title}"
        )
```

Sử dụng:

```python
service = BookService(
    repository=SQLiteRepository(),
    logger=Logger()
)

service.create_book(
    "Python OOP"
)
```

Kiến trúc:

```text
BookService
     │
     ├──────────────┐
     ▼              ▼
Repository        Logger
     │
     ▼
SQLiteRepository
```

---

# 26. Composition và SOLID

Composition chuẩn bị trực tiếp cho các buổi:

```text
Buổi 26
Dependency Injection
       ↓
Buổi 27
Single Responsibility
       ↓
Buổi 28
Open/Closed
       ↓
...
Buổi 31
Dependency Inversion
```

Đặc biệt:

```text
Composition
     +
Dependency Injection
     +
Abstraction
     ↓
Loose Coupling
```

Đây là một trong những nền tảng của kiến trúc phần mềm hiện đại.

---

# 27. Khi nào nên dùng Composition?

Hãy nghĩ đến Composition khi:

### 1. Quan hệ là HAS-A

```text
Car HAS-A Engine
```

### 2. Muốn thay implementation

```text
SQLiteRepository
PostgresRepository
MemoryRepository
```

### 3. Muốn Unit Test dễ

```text
RealRepository
FakeRepository
MockRepository
```

### 4. Muốn giảm coupling

```text
Service
   ↓
Interface
```

thay vì:

```text
Service
   ↓
Concrete Class
```

### 5. Class có quá nhiều trách nhiệm

Thay vì:

```text
MegaClass
```

tách thành:

```text
Service
Repository
Logger
Validator
Parser
```

rồi Composition chúng lại.

---

# 28. Khi nào vẫn nên dùng Inheritance?

Inheritance vẫn rất hữu ích khi có quan hệ:

```text
IS-A
```

Ví dụ:

```text
Animal
 ├── Dog
 └── Cat
```

hoặc:

```text
Parser
 ├── HtmlParser
 ├── JsonParser
 └── XmlParser
```

hoặc:

```text
Exception
 ├── BookNotFoundError
 └── DatabaseError
```

Vấn đề không phải:

> "Inheritance xấu."

Mà là:

> **Dùng đúng loại quan hệ.**

---

# 29. Bài tập thực hành

## Bài 1 — Car

Thiết kế:

```text
Car
 ├── Engine
 ├── GPS
 └── MusicPlayer
```

Không dùng inheritance.

---

## Bài 2 — Library

Thiết kế:

```text
LibraryService
 ├── BookRepository
 ├── BookValidator
 └── Logger
```

Constructor nhận tất cả dependency.

---

## Bài 3 — Sales

Thiết kế:

```text
SalesService
 ├── CustomerRepository
 ├── ProductRepository
 ├── Inventory
 └── InvoiceService
```

Yêu cầu:

```python
service.create_invoice(...)
```

không được trực tiếp tạo:

```python
CustomerRepository()
ProductRepository()
Inventory()
```

bên trong `SalesService`.

---

# 30. Bài tập nâng cao — Crawler

Xây dựng:

```text
Crawler
 │
 ├── HttpClient
 ├── Parser
 ├── Storage
 └── Logger
```

Các interface:

```python
class HttpClient:

    def get(self, url):
        ...


class Parser:

    def parse(self, html):
        ...


class Storage:

    def save(self, data):
        ...


class Logger:

    def info(self, message):
        ...
```

`Crawler`:

```python
class Crawler:

    def __init__(
        self,
        http_client,
        parser,
        storage,
        logger
    ):
        ...
```

Yêu cầu:

```python
crawler.crawl(url)
```

thực hiện:

```text
HTTP GET
   ↓
HTML
   ↓
Parser
   ↓
Data
   ↓
Storage
   ↓
Logger
```

---

# 31. Thử thay dependency

Sau khi hoàn thành, hãy thử:

```text
Storage
├── MemoryStorage
├── SQLiteStorage
└── JsonStorage
```

và:

```python
crawler = Crawler(
    http_client,
    parser,
    SQLiteStorage(),
    logger
)
```

sau đó:

```python
crawler = Crawler(
    http_client,
    parser,
    MemoryStorage(),
    logger
)
```

**Không được sửa `Crawler`.**

Nếu làm được điều này, bạn đã bắt đầu hiểu tư duy thiết kế OOP thực sự.

---

# 32. Tư duy quan trọng nhất của buổi 24

Khi thiết kế một class, đừng chỉ hỏi:

> "Class này kế thừa class nào?"

Hãy hỏi trước:

> **"Class này cần những object nào để thực hiện nhiệm vụ?"**

Ví dụ:

```text
Crawler
```

không nhất thiết phải kế thừa:

```text
HttpClient
Parser
Storage
Logger
```

Mà:

```text
Crawler
  HAS-A HttpClient
  HAS-A Parser
  HAS-A Storage
  HAS-A Logger
```

↓

**Composition.**

---

# Tổng kết

### Inheritance

```text
Dog IS-A Animal
```

### Composition

```text
Car HAS-A Engine
```

### Composition mạnh vì:

```text
Loose Coupling
      ↓
Replaceable Components
      ↓
Testable
      ↓
Maintainable
      ↓
Extensible
```

Và quan trọng nhất:

```text
Composition
      ↓
Dependency Injection
      ↓
SOLID
      ↓
Clean Architecture
      ↓
DDD
```

Đây chính là lý do Composition cực kỳ quan trọng trong Python OOP chuyên nghiệp.

> **Buổi 25 — Aggregation** sẽ đi sâu vào một khái niệm rất dễ nhầm với Composition. Chúng ta sẽ phân biệt chính xác:
>
> ```text
> Composition
>     vs
> Aggregation
> ```
>
> thông qua các ví dụ `Library → Book`, `Department → Employee`, `Order → Product`, vòng đời object và cách thiết kế chúng trong project **Library Management System**.
