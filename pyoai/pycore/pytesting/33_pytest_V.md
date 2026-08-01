# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 33: Pytest (Phần 5) – Mock chuyên nghiệp với `unittest.mock` + pytest

> **Mock là kỹ thuật quan trọng nhất khi viết Unit Test cho hệ thống lớn.**

Trong dự án thực tế, một class hiếm khi hoạt động độc lập.

Ví dụ:

```
OrderService

      |
      |
      +---- Database
      |
      +---- Payment API
      |
      +---- Email Service
      |
      +---- Redis Cache
```

Nếu test `OrderService`, bạn **không muốn**:

* Gọi Payment API thật.
* Gửi Email thật.
* Ghi Database thật.
* Chờ Redis thật.

Bạn thay thế bằng:

```
Fake Dependency
       |
       |
     Mock
```

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Mock trong pytest.
* Thành thạo `Mock`.
* Thành thạo `MagicMock`.
* Biết `patch`.
* Biết `patch.object`.
* Mock Repository.
* Mock API.
* Mock Database.
* Mock Async Function.
* Kiểm tra lời gọi.
* Thiết kế Unit Test theo Clean Architecture.

---

# Roadmap Pytest

```
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

Buổi 34+
Integration Testing
```

---

# Phần I

# Mock là gì?

Mock là:

> Một object giả lập hành vi của object thật.

Ví dụ:

Code thật:

```python
class EmailService:
    def send(self, email): ...
```

Trong production:

```
EmailService

     |
     |
SMTP Server
```

Trong test:

```
EmailService

     |
     |
Mock EmailService
```

---

# Phần II

# Mock đầu tiên

Import:

```python
from unittest.mock import Mock
```

Tạo:

```python
email = Mock()
```

Bây giờ:

```python
email.send()
```

hoạt động.

Không cần class thật.

---

Ví dụ:

```python
from unittest.mock import Mock


service = Mock()

service.send.return_value = True


result = service.send("abc@gmail.com")


assert result is True
```

---

# Phần III

# return_value

Đây là kỹ thuật dùng nhiều nhất.

Ví dụ:

Repository thật:

```python
class UserRepository:
    def find(self, id): ...
```

---

Test:

```python
repo = Mock()

repo.find.return_value = {"id": 1, "name": "Alice"}
```

---

Khi:

```python
repo.find(1)
```

Trả về:

```python
{"id": 1, "name": "Alice"}
```

---

# Phần IV

# side_effect

Dùng khi muốn:

* Throw Exception.
* Trả dữ liệu động.

---

## Exception

```python
repo.save.side_effect = Exception("Database error")
```

---

Test:

```python
with pytest.raises(Exception):
    repo.save()
```

---

## Function

```python
def fake_save(data):

    return data
```

---

```python
repo.save.side_effect = fake_save
```

---

# Phần V

# Kiểm tra Mock được gọi

Đây là điểm mạnh của Mock.

---

## assert_called

```python
mock.send.assert_called()
```

---

## assert_called_once

```python
mock.send.assert_called_once()
```

---

## assert_called_with

```python
mock.send.assert_called_with("hello")
```

---

Ví dụ:

```python
email.send("test@gmail.com")


email.send.assert_called_once_with("test@gmail.com")
```

---

# Phần VI

# call_count

Ví dụ:

```python
queue.push("A")
queue.push("B")
```

Test:

```python
assert queue.push.call_count == 2
```

---

# Phần VII

# Mock Repository Pattern

Đây là phần rất quan trọng.

Kiến trúc:

```
Controller

    |

Service

    |

Repository

    |

Database
```

---

Ví dụ:

## UserService

```python
class UserService:
    def __init__(self, repository):
        self.repository = repository

    def get_name(self, id):

        user = self.repository.find(id)

        return user["name"]
```

---

Test:

```python
from unittest.mock import Mock


def test_get_user():

    repo = Mock()

    repo.find.return_value = {"name": "Alice"}

    service = UserService(repo)

    result = service.get_name(1)

    assert result == "Alice"
```

---

Không có:

* SQLite.
* MySQL.
* PostgreSQL.

Test cực nhanh.

---

# Phần VIII

# Kiểm tra Repository được gọi

Bổ sung:

```python
repo.find.assert_called_once_with(1)
```

Bây giờ test kiểm tra:

1. Kết quả đúng.
2. Service gọi Repository đúng.

---

# Phần IX

# MagicMock

`MagicMock` là Mock có hỗ trợ magic method.

Ví dụ:

```python
from unittest.mock import MagicMock


file = MagicMock()


file.__enter__.return_value = file
```

Dùng được:

```python
with file:
    pass
```

---

Các magic method:

```
__len__

__iter__

__getitem__

__enter__

__exit__
```

---

# Phần X

# Mock File

Ví dụ code:

```python
def read_config():

    with open("config.txt") as f:
        return f.read()
```

---

Test:

```python
from unittest.mock import mock_open, patch


def test_file():

    m = mock_open(read_data="hello")

    with patch("builtins.open", m):
        result = read_config()

    assert result == "hello"
```

---

# Phần XI

# Mock HTTP Request

Code:

```python
import requests


def get_user():

    r = requests.get("https://api.com")

    return r.json()
```

---

Test:

```python
def test_api():

    response = Mock()

    response.json.return_value = {"name": "Bob"}

    with patch("requests.get", return_value=response):
        result = get_user()

    assert result["name"] == "Bob"
```

---

Không gọi Internet.

---

# Phần XII

# Patch đúng nơi sử dụng

Đây là lỗi phổ biến nhất.

Ví dụ:

module:

```
service.py
```

Có:

```python
from requests import get
```

---

Sai:

```python
patch("requests.get")
```

---

Đúng:

```python
patch("service.get")
```

---

Nguyên tắc:

> Patch nơi object được sử dụng, không phải nơi nó được khai báo.

---

# Phần XIII

# Mock Database

Ví dụ:

```python
class UserRepository:
    def __init__(self, db):

        self.db = db
```

---

Test:

```python
db = Mock()


db.execute.return_value = [("Alice",)]


repo = UserRepository(db)
```

---

Không cần:

* SQLite.
* PostgreSQL.

---

# Phần XIV

# Mock Redis

Ví dụ:

Production:

```python
cache.get("user:1")
```

Test:

```python
cache = Mock()


cache.get.return_value = {"name": "Alice"}
```

---

---

# Phần XV

# Mock Celery / Queue

Ví dụ:

Task:

```python
send_email.delay(user_id)
```

Test:

```python
task = Mock()


task.delay.assert_called_once()
```

---

Không chạy worker thật.

---

# Phần XVI

# Async Mock

Python hiện đại dùng nhiều:

* FastAPI.
* AsyncIO.
* HTTPX.
* aiohttp.

---

Dùng:

```python
from unittest.mock import AsyncMock
```

---

Ví dụ:

```python
api = AsyncMock()


api.fetch.return_value = {"id": 1}
```

---

Test:

```python
result = await api.fetch()
```

---

Kiểm tra:

```python
api.fetch.assert_awaited_once()
```

---

# Phần XVII

# Kết hợp Fixture + Mock

Đây là phong cách chuyên nghiệp.

`conftest.py`

```python
import pytest
from unittest.mock import Mock


@pytest.fixture
def repository():

    return Mock()
```

---

Test:

```python
def test_service(repository):

    service = UserService(repository)
```

---

Ưu điểm:

Mọi test dùng chung Mock.

---

# Phần XVIII

# Mock vs Fake vs Stub

Ba khái niệm thường nhầm.

---

## Stub

Trả dữ liệu cố định.

Ví dụ:

```python
repo.find.return_value = user
```

---

## Mock

Kiểm tra hành vi.

Ví dụ:

```python
repo.find.assert_called()
```

---

## Fake

Implementation đơn giản.

Ví dụ:

```
Real Database

      ↓

MemoryDatabase
```

---

# Phần XIX

# Khi nào Mock?

Nên Mock:

✅ HTTP API
✅ Database
✅ Redis
✅ Message Queue
✅ Email
✅ File System
✅ Payment Gateway

---

Không nên Mock:

❌ Hàm tính toán đơn giản
❌ Business Logic
❌ Pure Function

---

# Phần XX

# Mini Project

## Test Story Crawler Service

Kiến trúc:

```
ChapterService

      |

ChapterRepository

      |

HttpDownloader
```

---

Production:

```
HttpDownloader

↓

requests

↓

Website
```

---

Test:

```
ChapterService

      |

Mock Repository

      |

Mock Downloader
```

---

Test case:

## 1. Download chapter thành công

Mock:

```python
downloader.fetch.return_value = html
```

Kiểm tra:

```python
repository.save.assert_called_once()
```

---

## 2. Website lỗi

Mock:

```python
downloader.fetch.side_effect =
TimeoutError
```

Kiểm tra:

Service xử lý lỗi.

---

## 3. Chapter trùng

Mock:

```python
repository.exists.return_value = True
```

Kiểm tra:

Không lưu lại.

---

# Bài tập thực hành

## Bài 1

Mock:

```python
UserRepository
```

Test:

```python
UserService
```

---

## Bài 2

Mock:

```python
requests.get()
```

---

## Bài 3

Mock:

```python
open()
```

---

## Bài 4

Mock:

```python
RedisClient
```

---

## Bài 5

Mock:

```python
async API
```

dùng:

```python
AsyncMock
```

---

# Tổng kết Buổi 33

Bạn đã học:

✅ Mock là gì
✅ Mock Object
✅ return_value
✅ side_effect
✅ assert_called
✅ call_count
✅ MagicMock
✅ mock_open
✅ HTTP Mock
✅ Database Mock
✅ Repository Mock
✅ AsyncMock
✅ Patch đúng namespace
✅ Fixture + Mock

---

# Góc lập trình viên chuyên nghiệp

Một Unit Test tốt trong kiến trúc hiện đại:

```
              Unit Test

                  |

             Service Layer

                  |

          Mock Dependencies

                  |

        Không DB
        Không API
        Không File
```

Ví dụ:

```
OrderService

       |
       |
Mock PaymentGateway

       |
       |
Mock EmailSender
```

Bạn chỉ kiểm tra:

> "OrderService có thực hiện đúng nghiệp vụ không?"

Đó chính là tinh thần của:

* Clean Architecture
* SOLID
* Dependency Injection
* Hexagonal Architecture
* Domain Driven Design

---

# Chuẩn bị Buổi 34

Buổi tiếp theo:

# Pytest (Phần 6) – Integration Testing

Chúng ta sẽ học:

* Unit Test vs Integration Test.
* Test Database thật.
* SQLite Test Database.
* Transaction Rollback.
* Test Repository.
* Test API.
* Test FastAPI.
* Test Service + Repository.
* Tổ chức bộ test chuyên nghiệp.

Đây là bước chuyển từ **viết test đơn lẻ** sang **xây dựng hệ thống kiểm thử cho dự án thật**.
