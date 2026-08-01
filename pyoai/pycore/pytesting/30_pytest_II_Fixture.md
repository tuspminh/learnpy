# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 30: Pytest (Phần 2) – Fixture chuyên nghiệp trong Python Testing

> **Fixture là "trái tim" của pytest.**
>
> Nếu `unittest` dùng `setUp()` / `tearDown()` để chuẩn bị dữ liệu, thì `pytest` dùng **Fixture** với khả năng mạnh hơn rất nhiều.

Trong các dự án thực tế:

* FastAPI
* Django
* SQLAlchemy
* Celery
* Scrapy
* Automation
* Data Pipeline

Fixture xuất hiện gần như mọi nơi.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Fixture là gì.
* Biết tạo Fixture.
* Biết sử dụng Fixture.
* Hiểu Fixture Dependency.
* Hiểu Scope.
* Dùng `yield`.
* Dùng `autouse`.
* Biết `conftest.py`.
* Thiết kế Fixture cho Repository, Database, API Client.
* Viết test theo phong cách chuyên nghiệp.

---

# Phần I

# Vấn đề khi không dùng Fixture

Ví dụ:

```python
def test_add_user():

    user = User("Alice")

    ...


def test_delete_user():

    user = User("Alice")

    ...
```

Lặp lại:

```python
User("Alice")
```

Rất nhiều.

---

Nếu có:

100 test.

↓

100 lần tạo User.

Không tốt.

---

# Fixture giải quyết

Fixture:

> Chuẩn bị môi trường test.

Ví dụ:

```text
Tạo User

↓

Test

↓

Dọn dẹp
```

---

# Phần II

# Fixture đầu tiên

Cài:

```python
import pytest
```

Tạo:

```python
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

Điểm đặc biệt:

Không gọi:

```python
user()
```

Pytest tự inject.

---

# Dependency Injection trong Testing

Đây chính là:

```text
Fixture

↓

Test Function
```

Pytest tự truyền.

---

Ví dụ:

```python
def test_login(client): ...
```

Pytest nhìn thấy:

```text
client
```

↓

Tìm Fixture:

```python
@pytest.fixture
def client():
```

---

# Phần III

# Fixture thay thế setUp()

unittest:

```python
class TestUser:
    def setUp(self):

        self.user = User()
```

---

pytest:

```python
@pytest.fixture
def user():

    return User()
```

---

Test:

```python
def test_name(user):

    assert user.name == "Alice"
```

---

Ngắn hơn.

Dễ đọc hơn.

---

# Phần IV

# Fixture trả về Object

Ví dụ:

Model:

```python
class User:
    def __init__(self, name):
        self.name = name
```

Fixture:

```python
@pytest.fixture
def user():

    return User("Alice")
```

Test:

```python
def test_username(user):

    assert user.name == "Alice"
```

---

# Phần V

# Fixture có thể dùng Fixture khác

Ví dụ:

Database.

```python
@pytest.fixture
def database():

    return Database()
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
def test_create_user(service):

    result = service.create("Bob")

    assert result.name == "Bob"
```

---

Đây chính là Dependency Injection.

---

# Phần VI

# Fixture Scope

Đây là phần rất quan trọng.

Fixture có vòng đời.

---

Mặc định:

```python
scope = "function"
```

---

## 1. Function Scope

```python
@pytest.fixture(scope="function")
def data():

    print("Create")

    return []
```

Mỗi test:

```text
Test A

Create

Test B

Create
```

---

Dùng khi:

* Dữ liệu nhỏ.
* Test độc lập.

---

# 2. Class Scope

```python
@pytest.fixture(scope="class")
def database():

    return Database()
```

Một class dùng chung.

---

# 3. Module Scope

```python
@pytest.fixture(scope="module")
def config():

    return load_config()
```

Một file test dùng chung.

---

# 4. Session Scope

```python
@pytest.fixture(scope="session")
def app():

    return create_app()
```

Toàn bộ lần chạy pytest.

---

Ví dụ:

```text
pytest

|

Session Fixture

|

1000 tests
```

---

# So sánh

| Scope    | Số lần chạy     |
| -------- | --------------- |
| function | Mỗi test        |
| class    | Mỗi class       |
| module   | Mỗi file        |
| session  | Một lần toàn bộ |

---

# Phần VII

# Fixture với yield

Rất quan trọng.

Ví dụ:

Mở database:

```python
@pytest.fixture
def database():

    db = Database()

    yield db

    db.close()
```

Luồng:

```text
Create DB

↓

Test chạy

↓

Close DB
```

---

Tương đương:

```python
setUp()

test()

tearDown()
```

---

# Ví dụ File

```python
@pytest.fixture
def temp_file():

    f = open("data.txt", "w")

    yield f

    f.close()
```

---

# Phần VIII

# autouse=True

Bình thường:

```python
def test_a(db):
```

phải truyền:

```text
db
```

---

Có thể:

```python
@pytest.fixture(autouse=True)
def setup():

    print("prepare")
```

---

Mọi test tự chạy.

Ví dụ:

```python
def test_a():

    pass


def test_b():

    pass
```

Kết quả:

```text
prepare

test_a

prepare

test_b
```

---

Khi nào dùng?

Tốt cho:

* Logging setup.
* Environment.
* Cleanup.

Không nên lạm dụng.

---

# Phần IX

# conftest.py

Đây là kỹ thuật chuyên nghiệp.

Ví dụ:

```text
project/

    tests/

        conftest.py

        test_user.py

        test_book.py
```

---

conftest.py:

```python
import pytest


@pytest.fixture
def user():

    return User("Alice")
```

---

Không cần import.

test_user.py:

```python
def test_name(user):

    assert user.name == "Alice"
```

Pytest tự tìm.

---

# Phần X

# Fixture cho Database

Ví dụ SQLite Memory.

```python
@pytest.fixture
def db():

    conn = sqlite3.connect(":memory:")

    yield conn

    conn.close()
```

---

Ưu điểm:

* Nhanh.
* Không ảnh hưởng dữ liệu thật.

---

# Phần XI

# Fixture cho Repository

```python
@pytest.fixture
def repository(db):

    return BookRepository(db)
```

---

Test:

```python
def test_add_book(repository):

    book = Book("Python")

    repository.add(book)

    result = repository.get(1)

    assert result.title == "Python"
```

---

# Phần XII

# Fixture cho API Client

FastAPI thường dùng:

```python
@pytest.fixture
def client():

    return TestClient(app)
```

---

Test:

```python
def test_home(client):

    response = client.get("/")

    assert response.status_code == 200
```

---

# Phần XIII

# Fixture Factory

Một kỹ thuật nâng cao.

Ví dụ:

Muốn tạo nhiều User.

```python
@pytest.fixture
def make_user():

    def factory(name):

        return User(name)

    return factory
```

---

Dùng:

```python
def test_users(make_user):

    user1 = make_user("Alice")

    user2 = make_user("Bob")
```

---

Rất hay dùng trong:

* Test data generation.
* Database test.

---

# Phần XIV

# Fixture Parameter

Ví dụ:

```python
@pytest.fixture(params=["sqlite", "mysql"])
def database(request):

    return request.param
```

---

Test chạy:

```text
sqlite

mysql
```

---

Đây là nền tảng cho:

pytest parametrize.

---

# Phần XV

# Sai lầm khi dùng Fixture

## Sai

Một fixture khổng lồ:

```python
@pytest.fixture
def everything():
```

Tạo:

* DB
* User
* API
* File
* Cache

Không tốt.

---

## Sai

Scope quá lớn.

Ví dụ:

```python
scope = "session"
```

cho dữ liệu thay đổi.

---

## Sai

Fixture phụ thuộc quá nhiều.

Khó debug.

---

# Phần XVI

# Kiến trúc Testing chuyên nghiệp

Ví dụ dự án:

```text
story_crawler/

├── app/

│   ├── models

│   ├── services

│   ├── repositories

│   └── crawler


└── tests/

    ├── conftest.py

    ├── unit/

    ├── integration/

    └── e2e/
```

---

conftest.py:

```text
Database Fixture

↓

Repository Fixture

↓

Service Fixture

↓

Crawler Fixture
```

---

# Phần XVII

# Mini Project

## Test hệ thống cào truyện

Áp dụng:

* Repository Pattern.
* Clean Architecture.
* Dependency Injection.

---

Cấu trúc:

```
story_app/

tests/

    conftest.py

    test_chapter_service.py

    test_parser.py
```

---

## conftest.py

Tạo:

### Fixture:

`database`

* SQLite memory.

---

### Fixture:

`repository`

* Fake repository.

---

### Fixture:

`service`

* ChapterService.

---

Test:

```python
def test_save_chapter(service):

    chapter = service.save("Chapter 1")

    assert chapter.title == "Chapter 1"
```

---

# Phần XVIII

# Bài tập

## Bài 1

Tạo Fixture:

```python
user()
```

---

## Bài 2

Tạo Fixture:

```python
database()
```

với:

```text
yield
```

---

## Bài 3

Tạo:

```python
repository()
```

phụ thuộc:

```text
database
```

---

## Bài 4

Tạo:

```python
service()
```

phụ thuộc:

```text
repository
```

---

## Bài 5

Tạo:

```python
conftest.py
```

chia sẻ Fixture.

---

# Tổng kết buổi 30

Hôm nay bạn đã học:

✅ Fixture là gì
✅ Dependency Injection trong Test
✅ Fixture cơ bản
✅ Fixture Dependency
✅ Scope:

* function
* class
* module
* session

✅ `yield` Fixture
✅ `autouse`
✅ `conftest.py`
✅ Database Fixture
✅ Repository Fixture
✅ Factory Fixture
✅ Parameter Fixture

---

# Góc lập trình viên chuyên nghiệp

Một trong những lý do pytest mạnh hơn unittest là:

## pytest Fixture = Dependency Injection cho Testing

Ví dụ Clean Architecture:

```
Controller

↓

Service

↓

Repository

↓

Database
```

Trong production:

```
Service
   |
SQLiteRepository
```

Trong test:

```
Service
   |
MockRepository
```

Hoặc:

```
Service
   |
MemoryRepository
```

Chỉ cần thay Fixture.

Không cần sửa code nghiệp vụ.

Đây là lý do pytest kết hợp cực kỳ tốt với:

* SOLID
* Clean Architecture
* DDD
* Repository Pattern
* Hexagonal Architecture

---

# Chuẩn bị Buổi 31

Buổi tiếp theo:

# **Pytest (Phần 3) - Parametrize và Data Driven Testing**

Bạn sẽ học:

* `@pytest.mark.parametrize`
* Test nhiều dữ liệu.
* Test bảng dữ liệu.
* Parametrize nhiều tham số.
* Kết hợp Fixture + Parametrize.
* Test hàng nghìn trường hợp.
* Áp dụng cho:

  * Validator
  * Parser HTML
  * API
  * Repository
  * Crawler

Đây là kỹ thuật giúp giảm hàng trăm test function xuống chỉ còn vài dòng code.
