# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 38: Pytest (Phần 10) – Testing trong Clean Architecture và Domain Driven Design (DDD)

> Ở các buổi trước chúng ta học **cách viết test**.
>
> Buổi này chúng ta học **cách thiết kế hệ thống để có thể test tốt**.

Một lập trình viên Senior không chỉ hỏi:

> "Code này chạy đúng không?"

Mà còn hỏi:

> "Code này có dễ kiểm thử, dễ thay đổi, dễ mở rộng không?"

Đây chính là tư duy của:

* Clean Architecture.
* Domain Driven Design.
* SOLID.
* Dependency Injection.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Testing trong Clean Architecture.
* Test Domain Model.
* Test Entity.
* Test Value Object.
* Test Aggregate.
* Test Use Case.
* Test Repository Interface.
* Test Dependency Injection.
* Thiết kế test cho hệ thống Enterprise Python.

---

# Roadmap Pytest

```text
Buổi 29
Pytest cơ bản

Buổi 30
Fixture

Buổi 31
Parametrize

Buổi 32
MonkeyPatch

Buổi 33
Mock

Buổi 34
Integration Test

Buổi 35
E2E Test

Buổi 36
Coverage

Buổi 37
Test Design Pattern

Buổi 38
Clean Architecture Testing
```

---

# Phần I

# Vì sao Clean Architecture dễ test?

Kiến trúc truyền thống:

```text
Controller

    |

Database

    |

Business Logic
```

Business Logic phụ thuộc Database.

Kết quả:

```text
Test Business Logic

↓

Phải tạo Database
```

Khó.

---

Clean Architecture:

```text
        Domain

          ↑

       Use Case

          ↑

   Infrastructure

          ↑

     Framework
```

---

Quy tắc:

> Dependency hướng vào trong.

---

Domain không biết:

* Database.
* HTTP.
* File.
* Redis.

Vì vậy:

```text
Domain Test

=

Pure Unit Test
```

---

# Phần II

# Cấu trúc Clean Architecture

Ví dụ:

```text
app/

├── domain/

│   ├── entities/

│   ├── value_objects/

│   └── exceptions/


├── application/

│   ├── use_cases/

│   └── services/


├── infrastructure/

│   ├── database/

│   └── repositories/


└── presentation/

    └── api/
```

---

Test tương ứng:

```text
tests/

├── unit/

│
├── integration/

│
└── e2e/
```

---

Mapping:

| Layer      | Test        |
| ---------- | ----------- |
| Domain     | Unit        |
| Use Case   | Unit + Mock |
| Repository | Integration |
| API        | E2E         |

---

# Phần III

# Test Domain Entity

Domain Entity:

Ví dụ:

```python
class Order:
    def __init__(self):

        self.items = []

    def add_item(self, item):

        self.items.append(item)

    def total(self):

        return sum(x.price for x in self.items)
```

---

Đây là business rule.

Không cần:

* Database.
* API.
* Mock.

---

Test:

```python
def test_order_total():

    order = Order()

    order.add_item(Product(price=100))

    order.add_item(Product(price=50))

    assert order.total() == 150
```

---

Đây là Unit Test thuần.

---

# Phần IV

# Test Value Object

Trong DDD:

Value Object:

* Không có identity.
* Immutable.
* So sánh bằng giá trị.

Ví dụ:

```python
class Email:
    def __init__(self, value):

        if "@" not in value:
            raise ValueError()

        self.value = value
```

---

Test:

```python
def test_valid_email():

    email = Email("a@gmail.com")

    assert email.value == "a@gmail.com"
```

---

Test lỗi:

```python
import pytest


def test_invalid_email():

    with pytest.raises(ValueError):
        Email("abc")
```

---

# Phần V

# Test Entity Business Rule

Ví dụ:

Order:

Quy tắc:

> Không được thanh toán đơn hàng rỗng.

Code:

```python
class Order:
    def checkout(self):

        if not self.items:
            raise Exception("Empty order")
```

---

Test:

```python
def test_empty_order_fail():

    order = Order()

    with pytest.raises(Exception):
        order.checkout()
```

---

Chúng ta đang test:

Business Rule.

---

# Phần VI

# Test Aggregate trong DDD

Aggregate:

Nhóm Entity có boundary.

Ví dụ:

```text
Order Aggregate


Order

 |

+-- OrderItem

 |

+-- Product
```

---

Aggregate chịu trách nhiệm:

* Bảo vệ trạng thái.
* Kiểm tra rule.

---

Ví dụ:

```python
class Order:
    def add_item(self, item):

        if item.quantity <= 0:
            raise Exception()

        self.items.append(item)
```

---

Test:

```python
def test_cannot_add_invalid_item():

    order = Order()

    with pytest.raises(Exception):
        order.add_item(Item(quantity=0))
```

---

# Phần VII

# Test Use Case

Đây là phần quan trọng nhất.

Kiến trúc:

```text
API

 |

Use Case

 |

Repository Interface

```

---

Ví dụ:

Use Case:

```python
class CreateUserUseCase:
    def __init__(self, repository):

        self.repository = repository

    def execute(self, name):

        user = User(name)

        self.repository.save(user)

        return user
```

---

Test:

```python
from unittest.mock import Mock


def test_create_user():

    repo = Mock()

    usecase = CreateUserUseCase(repo)

    user = usecase.execute("Alice")

    assert user.name == "Alice"

    repo.save.assert_called_once()
```

---

Đây là Unit Test chuẩn Clean Architecture.

---

# Phần VIII

# Repository Interface Testing

DDD không phụ thuộc:

```text
SQLite

PostgreSQL

MongoDB
```

---

Domain chỉ biết:

```python
class UserRepository:
    def save(self, user):
        pass
```

---

Infrastructure implement:

```python
class SqlUserRepository(UserRepository): ...
```

---

Test:

## Use Case

Mock interface.

---

## Repository thật

Integration Test.

---

# Phần IX

# Dependency Injection Testing

Dependency Injection:

```python
class Service:
    def __init__(self, repo):

        self.repo = repo
```

---

Không tốt:

```python
class Service:
    def __init__(self):

        self.repo = SqlRepository()
```

---

Vì:

Không thể thay thế.

---

Test tốt:

```python
repo = Mock()


service = Service(repo)
```

---

# Phần X

# Test Event Driven Architecture

DDD thường dùng Domain Event.

Ví dụ:

```text
OrderCreated

        |

Email Service
```

---

Entity:

```python
order.create()
```

phát event:

```python
OrderCreated()
```

---

Test:

```python
def test_order_event():

    order.create()

    assert OrderCreated in events
```

---

---

# Phần XI

# Test Repository Integration

Repository thật:

```python
class SqlUserRepository:
    def save(self, user):

        db.insert(user)
```

---

Test:

```python
def test_save_user(db):

    repo = SqlUserRepository(db)

    user = User("Alice")

    repo.save(user)

    result = repo.find(user.id)

    assert result.name == "Alice"
```

---

Đây là:

```text
Integration Test

Repository

+

Database
```

---

# Phần XII

# Testing Pyramid trong Clean Architecture

Mô hình:

```text
             E2E

        API Workflow


       Integration

 Repository + DB


          Unit

Domain + UseCase
```

---

Tỷ lệ:

```text
Domain

★★★★★


UseCase

★★★★


Repository

★★★


API

★★
```

---

# Phần XIII

# Ví dụ Enterprise Project

Ứng dụng:

## Story Management System

Architecture:

```text
Presentation

 PySide6 / FastAPI


        |

Application

 Use Cases


        |

Domain

 Entity

 Value Object


        |

Infrastructure

 SQLite
```

---

Test:

## Domain

```text
Chapter Entity

Story Entity

Bookmark ValueObject
```

---

## Use Case

```text
AddChapter

DownloadStory

UpdateProgress
```

---

## Infrastructure

```text
SQLiteRepository
```

---

## E2E

```text
User click

↓

Download

↓

Save

↓

Read
```

---

# Phần XIV

# Anti Pattern

## 1. Test Database trong Domain

Sai:

```python
def test_order():

    sqlite.connect()
```

Domain không cần.

---

## 2. Mock mọi thứ

Sai:

```text
Mock Entity

Mock Service

Mock Repository
```

Không còn test logic.

---

## 3. Test implementation

Sai:

```python
assert private_variable == 10
```

---

Đúng:

```python
assert behavior_correct
```

---

# Phần XV

# Mini Project

Thiết kế test cho:

## E-Commerce System

Domain:

```text
Product

Order

Customer
```

---

Use Case:

```text
CreateOrder

PayOrder

CancelOrder
```

---

Repository:

```text
OrderRepository
```

---

Test:

```text
tests/

unit/

 domain/

 application/


integration/

 repository/


e2e/

 order_flow/
```

---

# Bài tập

## Bài 1

Tạo Entity:

```python
BankAccount
```

Rule:

* Không rút quá số dư.

Viết Unit Test.

---

## Bài 2

Tạo Value Object:

```python
Money
```

Test:

* Giá trị hợp lệ.
* Giá trị âm.

---

## Bài 3

Tạo Use Case:

```python
TransferMoney
```

Mock Repository.

---

## Bài 4

Thiết kế Test Architecture cho:

```text
Story Crawler
```

theo Clean Architecture.

---

# Tổng kết Buổi 38

Bạn đã học:

✅ Clean Architecture Testing
✅ DDD Testing
✅ Entity Test
✅ Value Object Test
✅ Aggregate Test
✅ Business Rule Test
✅ Use Case Test
✅ Repository Test
✅ Dependency Injection Test
✅ Domain Event Test
✅ Enterprise Test Architecture

---

# Góc nhìn Senior Python Developer

Kiến trúc tốt giúp test đơn giản.

Một hệ thống tốt:

```text
Domain

↓

Test dễ

↓

Use Case

↓

Test dễ

↓

Infrastructure

↓

Integration Test
```

Nếu một class rất khó test, thường không phải do test khó.

Mà do:

> Thiết kế class chưa tốt.

Đây là lý do các kiến trúc hiện đại như:

* Clean Architecture
* Hexagonal Architecture
* Domain Driven Design

được xây dựng.

---

# Chuẩn bị Buổi 39

**Pytest (Phần 11) – Advanced Fixture Architecture và Test Infrastructure**

Nội dung:

* Fixture scope nâng cao.
* Fixture dependency.
* Dynamic fixture.
* Factory Fixture.
* Database Fixture chuyên nghiệp.
* Test Container.
* Test Environment.
* Quản lý dữ liệu test lớn.
