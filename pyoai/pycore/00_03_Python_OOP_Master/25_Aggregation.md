# Python OOP Master — Buổi 25

## Aggregation — Quan hệ HAS-A nhưng **không sở hữu vòng đời**

Buổi 24 chúng ta đã học **Composition**:

```text
Car
 └── Engine
```

Hôm nay học **Aggregation** — một khái niệm rất quan trọng khi thiết kế hệ thống OOP lớn.

---

# 1. Aggregation là gì?

**Aggregation** là quan hệ:

> Một object có/đang sử dụng object khác, nhưng object bên trong có thể tồn tại độc lập.

Ví dụ:

```text
Department
 ├── Employee
 ├── Employee
 └── Employee
```

`Department` có các `Employee`.

Nhưng nếu `Department` bị xóa:

```text
Department X
```

thì:

```text
Employee A
Employee B
Employee C
```

**không nhất thiết bị xóa theo**.

Đó chính là Aggregation.

---

# 2. Composition vs Aggregation

Đây là phần quan trọng nhất của bài.

|                             | Composition    | Aggregation             |
| --------------------------- | -------------- | ----------------------- |
| Quan hệ                     | HAS-A          | HAS-A                   |
| Sở hữu object               | Mạnh           | Yếu                     |
| Lifecycle                   | Phụ thuộc      | Độc lập                 |
| Object con tồn tại độc lập? | Thường không   | Có                      |
| Ví dụ                       | `Car → Engine` | `Department → Employee` |
| Ownership                   | Parent sở hữu  | Parent chỉ tham chiếu   |

Có thể hình dung:

### Composition

```text
Car
 │
 └── Engine
```

`Car` tạo/quản lý `Engine`.

### Aggregation

```text
Employee A ─────┐
Employee B ─────┼──> Department
Employee C ─────┘
```

`Department` chỉ tập hợp các `Employee`.

---

# 3. Ví dụ cơ bản

```python
class Employee:
    def __init__(self, name):
        self.name = name


class Department:
    def __init__(self, name, employees):
        self.name = name
        self.employees = employees

    def show_employees(self):
        for employee in self.employees:
            print(employee.name)
```

Sử dụng:

```python
employees = [
    Employee("Alice"),
    Employee("Bob"),
    Employee("Charlie"),
]

department = Department(
    "IT",
    employees,
)

department.show_employees()
```

Output:

```text
Alice
Bob
Charlie
```

Điểm quan trọng:

```python
employees = [
    Employee("Alice"),
    Employee("Bob"),
]
```

được tạo **bên ngoài** `Department`.

Sau đó truyền vào:

```python
Department("IT", employees)
```

Do đó `Department` không phải owner tuyệt đối của `Employee`.

---

# 4. Object vẫn tồn tại độc lập

Ví dụ:

```python
alice = Employee("Alice")
bob = Employee("Bob")

employees = [alice, bob]

department = Department(
    "IT",
    employees,
)
```

Sau đó:

```python
del department
```

thì:

```python
alice
bob
```

vẫn có thể được sử dụng:

```python
print(alice.name)
print(bob.name)
```

Output:

```text
Alice
Bob
```

Đây là đặc điểm quan trọng của Aggregation.

---

# 5. Composition thì khác

Ví dụ Composition:

```python
class Engine:
    def start(self):
        print("Engine started")


class Car:
    def __init__(self):
        self.engine = Engine()
```

Ở đây:

```python
car = Car()
```

`Car` tạo:

```python
Engine()
```

bên trong.

Mối quan hệ:

```text
Car
 └── Engine
```

`Engine` là một phần cấu thành của `Car`.

---

# 6. Aggregation không nhất thiết tạo object bên trong

Aggregation thường có dạng:

```python
class Department:
    def __init__(self, employees):
        self.employees = employees
```

Trong khi Composition thường:

```python
class Car:
    def __init__(self):
        self.engine = Engine()
```

So sánh:

### Composition

```python
class Car:
    def __init__(self):
        self.engine = Engine()
```

### Aggregation

```python
class Department:
    def __init__(self, employees):
        self.employees = employees
```

Có thể nhớ:

> **Composition: tôi tạo và sở hữu.**

> **Aggregation: tôi nhận và sử dụng.**

Đây là quy tắc thực hành rất hữu ích.

---

# 7. Ví dụ Order và Product

Đây là ví dụ rất gần với project **Sales Management** sau này.

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
```

Tạo Product:

```python
laptop = Product("Laptop", 2000)
mouse = Product("Mouse", 50)
```

Order:

```python
class Order:
    def __init__(self, products):
        self.products = products

    def total(self):
        return sum(
            product.price
            for product in self.products
        )
```

Sử dụng:

```python
products = [
    laptop,
    mouse,
]

order = Order(products)

print(order.total())
```

Output:

```text
2050
```

Ở đây:

```text
Product
   ↑
   │
Order
```

`Order` đang tham chiếu tới các `Product`.

Nhưng `Product` không nhất thiết thuộc về duy nhất một `Order`.

---

# 8. Một Product có thể được nhiều object sử dụng

Ví dụ:

```python
laptop = Product("Laptop", 2000)

order_1 = Order([laptop])
order_2 = Order([laptop])
```

Cả hai:

```text
Order 1 ──┐
          ├──> Laptop
Order 2 ──┘
```

đều tham chiếu tới cùng một object:

```python
laptop
```

Điều này rất phù hợp với Aggregation.

---

# 9. Aggregation trong hệ thống Crawler

Đây mới là phần quan trọng đối với project của bạn.

Giả sử có:

```text
Crawler
 ├── HttpClient
 ├── Parser
 ├── Repository
 └── Logger
```

Có thể có những object thuộc **Composition**:

```python
class Crawler:
    def __init__(self):
        self.client = HttpClient()
```

Crawler tự tạo client.

Nhưng Repository có thể được **Aggregation**:

```python
repository = StoryRepository(db)

crawler = Crawler(repository)
```

Ví dụ:

```python
class Crawler:
    def __init__(self, repository):
        self.repository = repository

    def crawl(self):
        stories = ...
        self.repository.save(stories)
```

Repository tồn tại độc lập:

```text
StoryRepository
       ↑
       │
    Crawler
```

Có thể sử dụng repository ở nơi khác:

```python
repository = StoryRepository(db)

crawler = Crawler(repository)

dashboard = Dashboard(repository)

report = ReportService(repository)
```

Ta có:

```text
             ┌──> Crawler
             │
Repository ──┼──> Dashboard
             │
             └──> ReportService
```

Đây là một ví dụ rất điển hình của **Aggregation + Dependency Injection**.

---

# 10. Aggregation và Dependency Injection

Hai khái niệm này thường đi cùng nhau.

Ví dụ:

```python
class StoryRepository:
    def save(self, story):
        print("Saving story")


class Crawler:
    def __init__(self, repository):
        self.repository = repository
```

Inject:

```python
repository = StoryRepository()

crawler = Crawler(repository)
```

`Crawler` không tạo:

```python
StoryRepository()
```

mà nhận object từ bên ngoài.

Điều này giúp:

```text
Crawler
   ↓
Repository
```

ít phụ thuộc hơn.

---

# 11. Aggregation + Interface

Thiết kế tốt hơn:

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
        print("Save to SQLite")
```

Crawler:

```python
class Crawler:
    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def save_story(self, story):
        self.repository.save(story)
```

Sử dụng:

```python
repository = SQLiteStoryRepository()

crawler = Crawler(repository)

crawler.save_story("Story A")
```

Sơ đồ:

```text
             StoryRepository
                    ▲
                    │
          SQLiteStoryRepository
                    │
                    │
                 Crawler
```

Đây chính là nền tảng cho:

* Dependency Injection
* DIP
* Clean Architecture
* Repository Pattern
* Testing

mà bạn sẽ học tiếp.

---

# 12. Aggregation + Testing

Đây là lợi ích cực lớn.

Ta có:

```python
class FakeRepository:
    def __init__(self):
        self.items = []

    def save(self, story):
        self.items.append(story)
```

Test:

```python
fake_repository = FakeRepository()

crawler = Crawler(fake_repository)

crawler.save_story("Story A")

assert fake_repository.items == ["Story A"]
```

Không cần:

```text
SQLite
Database
Network
File
```

Test vẫn chạy được.

Đây chính là lý do kiến trúc:

```text
Dependency Injection
        +
Aggregation
        +
Interface
```

rất quan trọng.

---

# 13. Một ví dụ lớn hơn

Hãy xây một hệ thống Library.

```python
class Book:
    def __init__(self, title):
        self.title = title


class Library:
    def __init__(self, books):
        self.books = books

    def list_books(self):
        for book in self.books:
            print(book.title)
```

Tạo Book:

```python
book1 = Book("Python")
book2 = Book("Clean Architecture")
book3 = Book("DDD")
```

Tạo Library:

```python
books = [
    book1,
    book2,
    book3,
]

library = Library(books)
```

Ta có:

```text
Book 1 ─────┐
Book 2 ─────┼──> Library
Book 3 ─────┘
```

Library tập hợp Book.

Nhưng:

```python
book1
book2
book3
```

có thể được sử dụng ở nơi khác.

---

# 14. Composition + Aggregation cùng lúc

Một class thực tế có thể sử dụng **cả hai**.

Ví dụ:

```python
class Library:
    def __init__(self, books, logger):
        self.books = books
        self.logger = logger
```

Trong đó:

```text
Library
 ├── books
 └── logger
```

Nhưng ownership có thể khác nhau.

Ví dụ:

```python
logger = Logger()

library = Library(
    books,
    logger,
)
```

`Logger` được tạo bên ngoài.

Đây là Aggregation/Dependency Injection.

Trong khi một object nội bộ có thể được tạo bên trong:

```python
class Library:
    def __init__(self, books, logger):
        self.books = books
        self.logger = logger
        self.validator = BookValidator()
```

Ta có:

```text
Library
 ├── books ─────── Aggregation
 ├── logger ────── Aggregation
 └── validator ─── Composition
```

Đây là cách tư duy thiết kế class thực tế.

---

# 15. Không nên quá ám ảnh việc phân loại

Trong UML, Composition và Aggregation có ý nghĩa khá cụ thể.

Nhưng trong Python thực tế, không nên cố gắng phân loại mọi quan hệ thành:

```text
Composition
Aggregation
Association
```

một cách máy móc.

Điều quan trọng hơn là trả lời:

### Câu hỏi 1

Object này có tạo object kia không?

### Câu hỏi 2

Object này có sở hữu lifecycle của object kia không?

### Câu hỏi 3

Object kia có thể tồn tại độc lập không?

### Câu hỏi 4

Object kia có thể được chia sẻ cho nhiều object khác không?

### Câu hỏi 5

Có nên inject dependency từ bên ngoài không?

Nếu trả lời được 5 câu này, bạn sẽ thiết kế class tốt hơn rất nhiều.

---

# 16. Association vs Aggregation vs Composition

Có thể hình dung ba mức:

```text
Association
    │
    │ biết / sử dụng
    ▼

Aggregation
    │
    │ tập hợp
    ▼

Composition
    │
    │ sở hữu mạnh
    ▼
```

Ví dụ:

### Association

```python
teacher.teach(student)
```

Teacher biết Student.

---

### Aggregation

```python
department.employees
```

Department tập hợp Employee.

---

### Composition

```python
car.engine
```

Car sở hữu thành phần Engine.

---

# 17. Quy tắc nhớ nhanh

Hãy nhớ:

```text
Inheritance
    IS-A

Composition
    HAS-A + strong ownership

Aggregation
    HAS-A + weak ownership
```

Ví dụ:

```text
Dog IS-A Animal
Car HAS-A Engine
Department HAS-A Employee
```

---

# 18. Khi nào dùng Aggregation?

Aggregation rất phù hợp khi:

### 1. Object được tạo bên ngoài

```python
repository = Repository()

service = Service(repository)
```

### 2. Object có thể sống độc lập

```python
employee
department
```

### 3. Dependency có thể được chia sẻ

```text
Repository
 ├── Service
 ├── Crawler
 └── Dashboard
```

### 4. Muốn Dependency Injection

```python
Service(repository)
```

### 5. Muốn dễ testing

```python
Service(FakeRepository())
```

---

# 19. Anti-pattern

Không nên:

```python
class Crawler:

    def __init__(self):
        self.repository = SQLiteRepository()
        self.client = HttpxClient()
        self.parser = SelectolaxParser()
```

Class này biết quá nhiều implementation cụ thể.

Sau này sẽ khó:

```text
Testing
    ↓
Mock dependency

Change DB
    ↓
Change Repository

Change HTTP client
    ↓
Change Crawler
```

Thiết kế tốt hơn:

```python
class Crawler:

    def __init__(
        self,
        repository,
        client,
        parser,
    ):
        self.repository = repository
        self.client = client
        self.parser = parser
```

Bên ngoài quyết định implementation:

```python
crawler = Crawler(
    repository=SQLiteRepository(),
    client=HttpxClient(),
    parser=StoryParser(),
)
```

Đây là tư duy kiến trúc rất quan trọng.

---

# 20. Bài tập

## Bài 1 — Department

Xây dựng:

```text
Employee
Department
```

Yêu cầu:

```python
employee1 = Employee("Alice")
employee2 = Employee("Bob")

department = Department(
    "IT",
    [employee1, employee2],
)
```

Có:

```python
department.list_employees()
```

---

## Bài 2 — Library

Xây dựng:

```text
Book
Library
```

Một `Book` có thể tồn tại độc lập.

```python
book = Book("Python")

library = Library([book])
```

Sau đó:

```python
del library

print(book.title)
```

vẫn phải hoạt động.

---

# 21. Bài tập nâng cao — Crawler

Thiết kế:

```text
Crawler
   ↓
StoryRepository
```

Tạo interface:

```python
class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass
```

Tạo:

```text
SQLiteStoryRepository
FakeStoryRepository
```

Sau đó:

```python
crawler = Crawler(
    repository=SQLiteStoryRepository()
)
```

và test:

```python
crawler = Crawler(
    repository=FakeStoryRepository()
)
```

Mục tiêu:

```text
             StoryRepository
                  ▲
          ┌───────┴────────┐
          │                │
      SQLiteRepo       FakeRepo
          ▲                ▲
          └───────┬────────┘
                  │
               Crawler
```

Nếu bạn làm được bài này, bạn đã bắt đầu chuyển từ **OOP syntax** sang **OOP architecture**.

---

# 22. Tổng kết Buổi 25

```text
Aggregation
    ↓
HAS-A
    ↓
Object được tham chiếu
    ↓
Object có lifecycle độc lập
    ↓
Có thể chia sẻ
    ↓
Dependency Injection
    ↓
Loose Coupling
    ↓
Testing
```

So sánh nhanh:

```text
Inheritance
    Car IS-A Vehicle

Composition
    Car HAS-A Engine
    Car sở hữu Engine

Aggregation
    Department HAS-A Employee
    Employee tồn tại độc lập
```

Và trong project crawler của bạn:

```text
Crawler
   │
   ├── Repository  ← Aggregation / DI
   ├── HTTP Client ← Aggregation / DI
   └── Parser      ← Aggregation / DI
```

Đây là nền tảng rất quan trọng trước khi sang **Buổi 26 — Dependency Injection**, nơi chúng ta sẽ biến tư duy “truyền dependency từ bên ngoài” thành một kỹ thuật thiết kế hoàn chỉnh.
