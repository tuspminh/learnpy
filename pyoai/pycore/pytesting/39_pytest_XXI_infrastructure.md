# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 39: Pytest (Phần 11) – Advanced Fixture Architecture và xây dựng Test Infrastructure chuyên nghiệp

> Fixture là một trong những tính năng mạnh nhất của pytest.
>
> Người mới thường dùng fixture để "đỡ phải viết lại code".
>
> Lập trình viên chuyên nghiệp dùng fixture để **xây dựng cả một môi trường kiểm thử hoàn chỉnh**.

Ví dụ một hệ thống thật:

```text
Test Case

    |

Fixture

    |

Create Environment

    |

Database
Redis
API Client
Mock Service
Authentication
```

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu kiến trúc Fixture nâng cao.
* Thành thạo fixture scope.
* Fixture dependency.
* Factory Fixture.
* Dynamic Fixture.
* Database Fixture chuyên nghiệp.
* Test Environment.
* Quản lý dữ liệu test lớn.
* Thiết kế Test Infrastructure.

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

Buổi 39
Advanced Fixture Architecture
```

---

# Phần I

# Fixture thực chất là gì?

Fixture là:

> Một hàm cung cấp dữ liệu hoặc môi trường cho test.

Ví dụ:

```python
import pytest


@pytest.fixture
def user():

    return {"name": "Alice"}
```

---

Sử dụng:

```python
def test_user(user):

    assert user["name"] == "Alice"
```

---

Nhưng trong dự án lớn:

Fixture có thể tạo:

* Database.
* Browser.
* API Client.
* Authentication.
* Temporary File.
* Message Queue.

---

# Phần II

# Fixture Scope

Đây là phần cực kỳ quan trọng.

Fixture có 5 scope:

```text
function

class

module

package

session
```

---

# 1. function scope

Mặc định.

Mỗi test chạy:

```text
Create

↓

Test

↓

Destroy
```

Ví dụ:

```python
@pytest.fixture(scope="function")
def data():

    print("setup")
```

---

Test:

```python
def test_a(data):
    pass


def test_b(data):
    pass
```

Kết quả:

```text
setup

setup
```

---

# 2. class scope

Một lần cho một class.

```python
@pytest.fixture(scope="class")
def browser():

    print("open")
```

---

```python
class TestLogin:
    def test_a(self, browser):
        pass

    def test_b(self, browser):
        pass
```

---

Kết quả:

```text
open

test_a

test_b
```

---

# 3. module scope

Một lần cho một file test.

```python
@pytest.fixture(scope="module")
def connection():

    return connect()
```

---

Dùng khi:

* Database connection.
* API client.

---

# 4. session scope

Một lần cho toàn bộ pytest.

```python
@pytest.fixture(scope="session")
def app():

    start_server()

    yield app

    stop_server()
```

---

Dùng cho:

* Test server.
* Docker container.
* Browser engine.

---

# So sánh

| Scope    | Số lần chạy  |
| -------- | ------------ |
| function | mỗi test     |
| class    | mỗi class    |
| module   | mỗi file     |
| package  | mỗi package  |
| session  | toàn bộ test |

---

# Phần III

# Fixture Dependency

Fixture có thể dùng fixture khác.

Ví dụ:

```python
@pytest.fixture
def database():

    return SQLite()
```

---

Repository:

```python
@pytest.fixture
def repository(database):

    return UserRepository(database)
```

---

Service:

```python
@pytest.fixture
def service(repository):

    return UserService(repository)
```

---

Test:

```python
def test_create(service):

    result = service.create("Alice")
```

---

Luồng:

```text
Test

 |

Service Fixture

 |

Repository Fixture

 |

Database Fixture
```

---

Đây là cách xây dựng Dependency Injection trong test.

---

# Phần IV

# Fixture trong conftest.py

Dự án lớn:

Không đặt fixture trong từng file.

Dùng:

```text
tests/

├── conftest.py

├── unit/

├── integration/
```

---

conftest.py:

```python
import pytest


@pytest.fixture
def database():

    return Database()
```

---

Tất cả test:

```python
def test_x(database): ...
```

đều sử dụng được.

---

# Phần V

# Factory Fixture Pattern

Đây là kỹ thuật rất mạnh.

Vấn đề:

Bạn cần tạo nhiều User:

```python
user1
user2
user3
```

---

Cách cũ:

```python
def create_user():

    return User()
```

---

Factory Fixture:

```python
@pytest.fixture
def user_factory():

    def create(name):

        return User(name=name)

    return create
```

---

Sử dụng:

```python
def test_users(user_factory):

    alice = user_factory("Alice")

    bob = user_factory("Bob")
```

---

Rất phù hợp:

* Database test.
* Entity test.
* Fake data.

---

# Phần VI

# Dynamic Fixture

Ví dụ:

Muốn tạo:

* User thường.
* Admin.
* Manager.

---

Factory:

```python
@pytest.fixture
def user_factory():

    def create(role="user"):

        return User(role=role)

    return create
```

---

Dùng:

```python
admin = user_factory(role="admin")
```

---

# Phần VII

# Database Fixture chuyên nghiệp

Dự án thật:

```text
Application

 |

Repository

 |

Database
```

---

Fixture:

```python
@pytest.fixture
def db():

    engine = create_engine("sqlite:///:memory:")

    create_tables(engine)

    yield engine

    engine.dispose()
```

---

Test:

```python
def test_save(db):

    repo = Repository(db)

    ...
```

---

---

# Phần VIII

# Transaction Fixture

Đây là kỹ thuật production.

Mỗi test:

```text
BEGIN

↓

Test

↓

ROLLBACK
```

---

Ví dụ:

```python
@pytest.fixture
def transaction(db):

    tx = db.begin()

    yield db

    tx.rollback()
```

---

Ưu điểm:

* Test nhanh.
* Dữ liệu sạch.
* Không phải recreate database.

---

# Phần IX

# Fixture cho Authentication

Ứng dụng API:

```text
GET /profile
```

cần login.

---

Không muốn:

```text
Login
Login
Login
```

100 lần.

---

Fixture:

```python
@pytest.fixture
def auth_client(client):

    token = create_token(user_id=1)

    client.headers = {"Authorization": token}

    return client
```

---

Test:

```python
def test_profile(auth_client):

    response = auth_client.get("/profile")

    assert response.status_code == 200
```

---

# Phần X

# Fixture cho External Service

Ví dụ:

Payment API:

```text
Application

↓

Payment Gateway
```

---

Fixture:

```python
@pytest.fixture
def payment_mock():

    payment = Mock()

    payment.charge.return_value = True

    return payment
```

---

Test:

```python
def test_order(payment_mock): ...
```

---

# Phần XI

# Fixture + Docker Test Environment

Dự án lớn thường dùng:

```text
pytest

 |

Docker

 |

PostgreSQL

Redis

RabbitMQ
```

---

Ví dụ:

```text
@pytest.fixture(scope="session")

start postgres container

run tests

stop container
```

---

Công cụ:

* Testcontainers Python.
* Docker Compose.

---

Ví dụ:

```python
from testcontainers.postgres import PostgresContainer
```

---

Tạo database thật:

```text
PostgreSQL Container

↓

Integration Test
```

---

# Phần XII

# Fixture cho Temporary File

Python có sẵn:

```python
tmp_path
```

---

Ví dụ:

```python
def test_file(tmp_path):

    file = tmp_path / "data.txt"

    file.write_text("hello")

    assert file.exists()
```

---

Sau test:

pytest tự xóa.

---

# Phần XIII

# Fixture cho Project Crawler

Áp dụng vào dự án cào truyện.

Kiến trúc:

```text
Crawler App

 |

Database

 |

Parser

 |

Downloader
```

---

conftest.py:

```python
@pytest.fixture
def database():

    return TestDatabase()
```

---

```python
@pytest.fixture
def repository(database):

    return ChapterRepository(database)
```

---

```python
@pytest.fixture
def crawler(repository):

    return CrawlerService(repository)
```

---

Test:

```python
def test_download_story(crawler):

    crawler.start(url)
```

---

Luồng:

```text
Test

↓

Crawler Fixture

↓

Repository Fixture

↓

Database Fixture
```

---

# Phần XIV

# Fixture Anti Pattern

## 1. Fixture quá lớn

Sai:

```python
@pytest.fixture
def everything():

    create_db()

    create_user()

    create_order()

    send_email()
```

---

Vấn đề:

* Khó hiểu.
* Khó debug.

---

Nên:

```text
database

user

order

email
```

---

## 2. Fixture làm quá nhiều việc

Fixture nên:

* Setup.
* Cleanup.

Không nên chứa business logic.

---

## 3. Scope sai

Ví dụ:

Database:

```python
scope = "session"
```

có thể gây:

* Dữ liệu test bị ảnh hưởng.

---

# Phần XV

# Kiến trúc Test Infrastructure chuyên nghiệp

Dự án Enterprise:

```text
tests/

├── conftest.py


├── fixtures/

│   ├── database.py

│   ├── users.py

│   └── api.py


├── factories/

│   ├── user_factory.py


├── builders/

│   └── order_builder.py


├── unit/


├── integration/


└── e2e/
```

---

Đây là cấu trúc thường gặp trong công ty lớn.

---

# Phần XVI

# Mini Project

Thiết kế Test Infrastructure:

## E-Commerce App

Có:

```text
User

Product

Order

Payment
```

---

Tạo:

```text
fixtures:

database

user_factory

product_factory

auth_client


builders:

order_builder
```

---

Test:

```python
def test_create_order(order_builder):

    order = order_builder.build()

    ...
```

---

# Bài tập

## Bài 1

Tạo:

```python
database fixture
```

scope:

```python
session
```

---

## Bài 2

Tạo:

```python
user_factory
```

---

## Bài 3

Tạo:

```python
repository fixture
```

phụ thuộc database.

---

## Bài 4

Thiết kế:

```text
conftest.py
```

cho Story Crawler.

---

## Bài 5

Viết fixture:

```text
authenticated API client
```

---

# Tổng kết Buổi 39

Bạn đã học:

✅ Fixture Scope
✅ Fixture Dependency
✅ conftest.py
✅ Factory Fixture
✅ Dynamic Fixture
✅ Database Fixture
✅ Transaction Fixture
✅ Authentication Fixture
✅ Docker Test Environment
✅ Temporary File Fixture
✅ Test Infrastructure Architecture

---

# Góc nhìn Senior Python Developer

Trong dự án nhỏ:

```text
Fixture = tiện ích
```

Trong dự án lớn:

```text
Fixture = Test Infrastructure
```

Một hệ thống test tốt có kiến trúc gần giống ứng dụng thật:

```text
Production Architecture

        +

Testing Architecture
```

Cả hai phải được thiết kế cẩn thận.

---

# Chuẩn bị Buổi 40

**Pytest (Phần 12) – Advanced Mocking, Contract Test và kiểm thử hệ thống phân tán**

Nội dung:

* Mock nâng cao.
* Spy.
* Stub.
* Fake.
* Contract Testing.
* API Contract.
* Service-to-Service Testing.
* Testing Microservices.
* Message Queue Testing.
* Redis / Celery Testing.
