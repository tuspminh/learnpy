# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 34: Pytest (Phần 6) – Integration Testing chuyên nghiệp trong Python

> **Unit Test kiểm tra từng bộ phận riêng lẻ.**
>
> **Integration Test kiểm tra các bộ phận khi kết hợp với nhau.**

Trong dự án thật, code không chỉ là:

```text
Function → Result
```

mà là:

```text
API

 ↓

Service

 ↓

Repository

 ↓

Database

 ↓

External System
```

Integration Testing giúp trả lời câu hỏi:

> "Các thành phần có làm việc đúng với nhau không?"

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Integration Test.
* Phân biệt Unit Test và Integration Test.
* Thiết kế Integration Test.
* Test Repository với Database thật.
* Test SQLite Memory.
* Test Transaction.
* Test API.
* Test Service + Repository.
* Tổ chức thư mục test chuyên nghiệp.

---

# Roadmap Testing

```text
Buổi 29
✓ Pytest cơ bản

Buổi 30
✓ Fixture

Buổi 31
✓ Parametrize

Buổi 32
✓ MonkeyPatch

Buổi 33
✓ Mock

Buổi 34
✓ Integration Testing

Buổi 35+
Advanced Testing
```

---

# Phần I

# Unit Test vs Integration Test

## Unit Test

Mục tiêu:

Test một đơn vị nhỏ.

Ví dụ:

```python
def calculate_price():
```

Test:

```python
assert calculate_price(100) == 120
```

Không cần:

* Database.
* Network.
* File.

---

## Integration Test

Kiểm tra:

```text
Service

+

Repository

+

Database
```

---

Ví dụ:

```text
create_user()

      |

UserRepository

      |

SQLite
```

---

# So sánh

|          | Unit Test | Integration Test |
| -------- | --------- | ---------------- |
| Phạm vi  | Nhỏ       | Lớn              |
| Tốc độ   | Rất nhanh | Chậm hơn         |
| Database | Mock      | Thật             |
| API      | Mock      | Có thể thật      |
| Mục đích | Logic     | Kết nối          |

---

# Phần II

# Khi nào cần Integration Test?

Không cần test mọi thứ.

Nên test:

✅ Repository
✅ Database query
✅ API endpoint
✅ Authentication flow
✅ Message Queue
✅ File storage
✅ External integration

---

Ví dụ:

Bạn viết:

```python
repository.save(user)
```

Unit Test:

```python
Mock Database
```

Nhưng vẫn có thể lỗi:

* SQL sai.
* Schema sai.
* Migration sai.

Integration Test phát hiện.

---

# Phần III

# Cấu trúc dự án Test chuyên nghiệp

Ví dụ:

```
project/

├── app/

│   ├── models/

│   ├── services/

│   ├── repositories/

│   └── api/


└── tests/

    ├── unit/

    │
    ├── integration/

    │
    └── e2e/
```

---

Ví dụ:

```
tests/

├── unit/

│   └── test_price.py


├── integration/

│   ├── test_repository.py

│   └── test_database.py


└── e2e/

    └── test_user_flow.py
```

---

# Phần IV

# Integration Test với SQLite Memory

Đây là cách phổ biến nhất.

Fixture:

```python
import pytest
import sqlite3


@pytest.fixture
def database():

    conn = sqlite3.connect(":memory:")

    yield conn

    conn.close()
```

---

Database tồn tại:

```text
Test bắt đầu

↓

Tạo DB

↓

Test

↓

Xóa DB
```

---

# Phần V

# Tạo Schema

Ví dụ:

```python
def create_tables(db):

    db.execute(
        """
        CREATE TABLE users(
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """
    )
```

---

Fixture hoàn chỉnh:

```python
@pytest.fixture
def database():

    conn = sqlite3.connect(":memory:")

    create_tables(conn)

    yield conn

    conn.close()
```

---

# Phần VI

# Test Repository thật

Repository:

```python
class UserRepository:
    def __init__(self, db):

        self.db = db

    def save(self, user):

        self.db.execute(
            """
            INSERT INTO users(name)
            VALUES(?)
            """,
            (user.name,),
        )

        self.db.commit()
```

---

Test:

```python
def test_save_user(database):

    repo = UserRepository(database)

    user = User("Alice")

    repo.save(user)

    row = database.execute("SELECT name FROM users").fetchone()

    assert row[0] == "Alice"
```

---

Đây là Integration Test.

Vì:

```text
Repository

+

SQLite
```

---

# Phần VII

# Fixture Repository

Không muốn lặp:

```python
repo = UserRepository(db)
```

---

conftest.py

```python
@pytest.fixture
def repository(database):

    return UserRepository(database)
```

---

Test:

```python
def test_save(repository): ...
```

---

# Phần VIII

# Transaction Testing

Database cần dữ liệu sạch.

Ví dụ:

Test 1:

```text
Insert Alice
```

Test 2:

```text
Insert Bob
```

Không được:

```text
Alice + Bob
```

---

Giải pháp:

Rollback.

---

Fixture:

```python
@pytest.fixture
def transaction(database):

    database.execute("BEGIN")

    yield database

    database.rollback()
```

---

Mỗi test:

```text
BEGIN

↓

TEST

↓

ROLLBACK
```

---

# Phần IX

# Integration Test Service + Repository

Kiến trúc:

```
UserService

      |

UserRepository

      |

SQLite
```

---

Service:

```python
class UserService:
    def __init__(self, repo):
        self.repo = repo

    def register(self, name):

        user = User(name)

        self.repo.save(user)

        return user
```

---

Test:

```python
def test_register(service):

    user = service.register("Alice")

    assert user.name == "Alice"
```

---

Ở đây:

Không Mock Repository.

---

# Phần X

# Integration Test API

Ví dụ FastAPI.

Cấu trúc:

```
Client

 ↓

API Router

 ↓

Service

 ↓

Database
```

---

Dùng:

```python
from fastapi.testclient import TestClient
```

---

Fixture:

```python
@pytest.fixture
def client():

    return TestClient(app)
```

---

Test:

```python
def test_create_user(client):

    response = client.post("/users", json={"name": "Alice"})

    assert response.status_code == 200
```

---

# Phần XI

# Test HTTP thật với Test Server

Ví dụ:

```text
pytest

↓

Start server

↓

Request

↓

Response
```

---

Dùng cho:

* FastAPI.
* Flask.
* Django.

---

# Phần XII

# Integration Test Crawler

Áp dụng vào dự án cào truyện.

Kiến trúc:

```
CrawlerService

      |

Parser

      |

Repository

      |

SQLite
```

---

Unit Test:

```text
Parser

Mock HTML
```

---

Integration Test:

```text
HTML thật

↓

Parser

↓

Repository

↓

SQLite
```

---

Test:

```python
def test_save_chapter(repository):

    chapter = parser.parse(html)

    repository.save(chapter)

    result = repository.find(chapter.id)

    assert result.title == "Chapter 1"
```

---

# Phần XIII

# Integration Test với External API

Có 3 cách.

---

## Cách 1

Gọi API thật.

Ưu:

* Chính xác.

Nhược:

* Chậm.
* Không ổn định.

---

## Cách 2

Mock.

Dùng Unit Test.

---

## Cách 3

Fake Server.

Ví dụ:

```
Test

↓

Fake API

↓

Response
```

---

Thường dùng:

* WireMock.
* HTTPX Mock.
* Responses.

---

# Phần XIV

# Test Pyramid

Một kiến trúc test tốt:

```
          E2E
        /     \

    Integration

   /             \

       Unit
```

---

Tỷ lệ phổ biến:

```
70%
Unit Test

20%
Integration

10%
E2E
```

---

# Phần XV

# Sai lầm thường gặp

## Sai 1

Tất cả đều Integration Test.

Hậu quả:

* Chậm.
* Khó debug.

---

## Sai 2

Không có Database Test.

SQL lỗi không biết.

---

## Sai 3

Dùng Database Production.

Rất nguy hiểm.

---

## Sai 4

Không reset dữ liệu.

Test phụ thuộc nhau.

---

# Phần XVI

# Mini Project

## Xây bộ Integration Test cho Story App

Cấu trúc:

```
tests/

integration/

├── test_database.py

├── test_repository.py

├── test_service.py
```

---

## Test Database

Kiểm tra:

* Tạo bảng.
* Insert.
* Query.

---

## Test Repository

Kiểm tra:

* Save chapter.
* Find chapter.
* Delete chapter.

---

## Test Service

Kiểm tra:

* Download.
* Parse.
* Save.

---

# Phần XVII

# Bài tập

## Bài 1

Tạo:

```python
SQLite Memory Database
```

---

## Bài 2

Viết:

```python
UserRepository
```

---

## Bài 3

Integration Test:

```python
save_user()
```

---

## Bài 4

Integration Test:

```python
find_user()
```

---

## Bài 5

Tạo:

```
Service

+

Repository

+

Database
```

và test toàn bộ.

---

# Tổng kết Buổi 34

Bạn đã học:

✅ Integration Test là gì
✅ Unit vs Integration
✅ Test Pyramid
✅ SQLite Memory Test
✅ Database Fixture
✅ Repository Integration Test
✅ Service Integration Test
✅ API Integration Test
✅ Transaction Rollback
✅ Fake External Service
✅ Tổ chức test chuyên nghiệp

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án lớn:

```text
                 CI/CD

                    |

              Run Tests

                    |

      ----------------------------

      Unit        Integration     E2E

       |              |             |

     1s             30s           5m
```

Developer chạy:

* Unit Test liên tục.

CI chạy:

* Unit + Integration.

Release chạy:

* E2E.

---

Đây là cách các team Python chuyên nghiệp xây dựng hệ thống ổn định.

---

# Chuẩn bị Buổi 35

Buổi tiếp theo:

# **Pytest (Phần 7) – End-to-End Testing và Functional Testing**

Bạn sẽ học:

* E2E Test là gì.
* Functional Test.
* Test workflow người dùng.
* Test API từ đầu đến cuối.
* Test CLI Application.
* Test GUI Application.
* Selenium / Playwright.
* Pytest trong CI/CD.

Đây là tầng kiểm thử cao nhất mô phỏng cách người dùng thật sử dụng phần mềm.
