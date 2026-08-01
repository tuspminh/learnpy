# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 40: Pytest (Phần 12) – Advanced Mocking, Spy, Stub, Fake, Contract Testing và kiểm thử hệ thống phân tán

> Đây là một trong những chủ đề quan trọng nhất đối với lập trình viên Python chuyên nghiệp.
>
> Sau buổi này, bạn sẽ hiểu cách các công ty lớn như Google, Microsoft, Netflix, Spotify, Uber... xây dựng hệ thống kiểm thử cho các dịch vụ (services) độc lập.

---

# Mục tiêu buổi học

Sau buổi học này bạn sẽ:

* Hiểu rõ sự khác nhau giữa Mock, Stub, Fake và Spy.
* Thành thạo Advanced Mocking.
* Hiểu Contract Testing.
* Test Message Queue.
* Test Redis.
* Test Celery/Dramatiq.
* Test Event Driven Architecture.
* Kiểm thử Microservices.
* Thiết kế hệ thống test cho ứng dụng phân tán.

---

# Roadmap

```text
Buổi 29-39
✓ Foundation Testing

Buổi 40
✓ Advanced Mocking
✓ Contract Testing
✓ Distributed Testing

Buổi 41
Performance Testing

Buổi 42
Security Testing
```

---

# Phần I

# Kiến trúc của hệ thống hiện đại

Ngày nay đa số hệ thống không còn như thế này:

```text
GUI

 |

Database
```

Mà là:

```text
Frontend

    |

API Gateway

    |

-----------------------

Order Service

Payment Service

User Service

Notification Service

-----------------------

Redis

RabbitMQ

PostgreSQL
```

Một request có thể đi qua:

* API
* Redis
* RabbitMQ
* Celery
* Database
* Email

Làm thế nào để test?

---

# Phần II

# Phân biệt Mock, Stub, Fake, Spy

Đây là phần thường gây nhầm lẫn nhất.

---

## 1. Stub

Stub chỉ trả dữ liệu có sẵn.

Ví dụ:

```python
repo = Mock()

repo.find.return_value = User("Alice")
```

Không quan tâm:

* Có được gọi không.
* Gọi bao nhiêu lần.

Chỉ cần:

```text
find()

↓

Alice
```

---

## 2. Mock

Mock kiểm tra hành vi.

Ví dụ:

```python
repo.save.assert_called_once()
```

Mock trả lời:

```text
Service

↓

save()

↓

Có gọi không?
```

---

## 3. Fake

Fake là implementation thật nhưng đơn giản.

Ví dụ:

Production:

```text
PostgreSQL
```

Test:

```text
MemoryRepository
```

Code:

```python
class MemoryUserRepository:
    def __init__(self):

        self.users = {}

    def save(self, user):

        self.users[user.id] = user

    def find(self, id):

        return self.users[id]
```

Không Mock.

Không Database.

Nhưng vẫn có logic.

---

## 4. Spy

Spy là object thật nhưng theo dõi hành vi.

Ví dụ:

```python
service = MagicMock(wraps=RealService())
```

Spy:

* Gọi code thật.
* Ghi nhận lời gọi.

Ví dụ:

```python
service.process()

service.process.assert_called_once()
```

---

# So sánh

| Kiểu | Có logic? | Theo dõi lời gọi? | Dùng khi               |
| ---- | --------- | ----------------- | ---------------------- |
| Stub | Không     | Không             | Trả dữ liệu            |
| Mock | Không     | Có                | Kiểm tra hành vi       |
| Fake | Có        | Không             | Thay thế hệ thống thật |
| Spy  | Có        | Có                | Theo dõi code thật     |

---

# Phần III

# Advanced Mock với autospec

Một lỗi rất phổ biến:

```python
repo = Mock()

repo.savee()
```

Test vẫn chạy.

Trong khi:

```python
savee()
```

không tồn tại.

---

Giải pháp:

```python
from unittest.mock import create_autospec
```

Ví dụ:

```python
repo = create_autospec(UserRepository)
```

Bây giờ:

```python
repo.savee()
```

sẽ báo lỗi ngay.

Đây là cách nên dùng trong các dự án lớn vì nó giúp phát hiện lỗi đánh máy và sai API sớm.

---

# Phần IV

# Mock nhiều giá trị liên tiếp

Ví dụ:

```python
api.fetch()
```

Lần 1:

```text
Timeout
```

Lần 2:

```text
Success
```

---

Dùng:

```python
api.fetch.side_effect = [TimeoutError(), {"name": "Alice"}]
```

Test:

```python
with pytest.raises(TimeoutError):
    api.fetch()

result = api.fetch()

assert result["name"] == "Alice"
```

Rất hữu ích khi kiểm thử cơ chế retry.

---

# Phần V

# Spy thực tế

Giả sử:

```python
class Calculator:
    def add(self, a, b):

        return a + b
```

---

Spy:

```python
from unittest.mock import MagicMock

real = Calculator()

spy = MagicMock(wraps=real)

assert spy.add(2, 3) == 5

spy.add.assert_called_once_with(2, 3)
```

Khác với Mock:

Spy vẫn chạy code thật.

---

# Phần VI

# Fake Repository trong Clean Architecture

Repository Interface:

```python
class UserRepository:
    def save(self, user): ...

    def find(self, id): ...
```

---

Fake:

```python
class FakeUserRepository:
    def __init__(self):

        self.data = {}

    def save(self, user):

        self.data[user.id] = user

    def find(self, id):

        return self.data[id]
```

---

Test:

```python
repo = FakeUserRepository()

service = UserService(repo)

service.register("Alice")

assert repo.find(1).name == "Alice"
```

Đây là kỹ thuật được sử dụng rất nhiều trong DDD và Clean Architecture.

---

# Phần VII

# Contract Testing

Đây là kỹ thuật cực kỳ quan trọng trong Microservices.

Ví dụ:

```text
Order Service

↓

Payment Service
```

Order Service kỳ vọng Payment Service trả:

```json
{
  "status":"paid",
  "transaction_id":"abc123"
}
```

Nếu Payment Service đổi thành:

```json
{
  "result":"ok"
}
```

Order Service có thể bị lỗi dù từng service đều đã pass test.

Contract Testing giúp phát hiện điều này.

---

# Consumer Contract

Ví dụ:

```python
response = payment.pay()

assert "status" in response
assert "transaction_id" in response
```

Nếu contract thay đổi, test sẽ fail ngay.

---

# Phần VIII

# API Schema Testing

Ví dụ FastAPI:

```python
response = client.get("/users/1")

data = response.json()

assert isinstance(data["id"], int)

assert isinstance(data["name"], str)
```

Nâng cao hơn:

Có thể dùng:

* JSON Schema
* Pydantic Model

Ví dụ:

```python
UserResponse.model_validate(data)
```

Nếu API trả sai schema, test sẽ thất bại.

---

# Phần IX

# Message Queue Testing

Ví dụ:

```text
User Register

↓

RabbitMQ

↓

Email Worker
```

Unit Test:

Mock Queue:

```python
queue.publish.assert_called_once()
```

---

Integration:

Fake Queue.

---

E2E:

Queue thật.

---

# Phần X

# Testing Celery

Task:

```python
@app.task
def send_email(): ...
```

Test logic:

```python
send_email.run()
```

Thay vì:

```python
send_email.delay()
```

Điều này giúp test nghiệp vụ mà không cần worker.

---

Kiểm tra enqueue:

```python
task.delay.assert_called_once()
```

---

# Phần XI

# Redis Testing

Production:

```text
Redis
```

---

Unit Test:

```python
cache = Mock()
```

---

Integration:

Có thể dùng Redis thật trong Docker hoặc thư viện giả lập như:

```text
fakeredis
```

Ví dụ:

```python
import fakeredis

redis = fakeredis.FakeRedis()

redis.set("user", "Alice")

assert redis.get("user") == b"Alice"
```

`fakeredis` rất phù hợp để kiểm thử mà không cần cài Redis thật.

---

# Phần XII

# Event Driven Testing

Ví dụ:

```text
Order Created

↓

Publish Event

↓

Inventory

↓

Email

↓

Analytics
```

Test:

```python
publisher.publish.assert_called_once()
```

Hoặc:

```python
event = publisher.publish.call_args[0][0]

assert event.type == "OrderCreated"
```

Không chỉ kiểm tra có publish mà còn kiểm tra nội dung event.

---

# Phần XIII

# Kiểm thử dự án Story Crawler

Giả sử hệ thống:

```text
Crawler

↓

Downloader

↓

Parser

↓

Repository

↓

Redis Cache

↓

Notification
```

---

### Unit Test

Mock:

* Downloader
* Redis
* Notification

Chỉ test:

```text
CrawlerService
```

---

### Integration

Test:

```text
Repository

+

SQLite
```

---

### E2E

```text
Start Crawl

↓

Download HTML

↓

Parse

↓

Save

↓

Cache

↓

Open Reader
```

---

# Phần XIV

# Kiến trúc Test cho Microservices

```text
tests/

├── unit/

├── integration/

├── contract/

├── component/

├── e2e/
```

Ý nghĩa:

| Thư mục     | Mục đích                                          |
| ----------- | ------------------------------------------------- |
| unit        | Kiểm tra từng class/hàm                           |
| integration | Kiểm tra nhiều thành phần cùng hoạt động          |
| contract    | Đảm bảo giao tiếp giữa các service                |
| component   | Kiểm tra một service hoàn chỉnh với phụ thuộc gần |
| e2e         | Kiểm tra toàn hệ thống                            |

Đây là cấu trúc thường thấy trong các hệ thống enterprise.

---

# Phần XV

# Những sai lầm phổ biến

## 1. Mock mọi thứ

Sai:

```text
Mock Service

↓

Mock Repository

↓

Mock Entity
```

Kết quả:

Không còn kiểm tra nghiệp vụ thật.

---

## 2. Không có Contract Test

API thay đổi.

Service khác hỏng.

Không ai biết.

---

## 3. Dùng Mock thay cho Fake

Nhiều trường hợp:

```text
Fake Repository
```

đơn giản hơn rất nhiều.

---

## 4. Không dùng autospec

Có thể vô tình gọi sai tên phương thức mà test vẫn xanh.

---

# Phần XVI

# Mini Project

Giả sử xây dựng hệ thống:

```text
Story Crawler

↓

FastAPI

↓

SQLite

↓

Redis

↓

Celery

↓

Email
```

Chiến lược test:

| Thành phần     | Loại test                   |
| -------------- | --------------------------- |
| Parser         | Unit Test                   |
| CrawlerService | Unit + Mock Downloader      |
| Repository     | Integration                 |
| Redis Cache    | Integration với `fakeredis` |
| Celery Task    | Test `.run()` và enqueue    |
| REST API       | E2E                         |
| Schema API     | Contract Test               |

---

# Bài tập thực hành

### Bài 1

Viết `FakeUserRepository` đầy đủ với:

* `save()`
* `find()`
* `delete()`

---

### Bài 2

Dùng `create_autospec()` để mock một `BookRepository`.

Thử gọi sai tên phương thức và quan sát lỗi.

---

### Bài 3

Viết Spy cho lớp:

```python
class Calculator:
    def multiply(self, a, b):
        return a * b
```

Kiểm tra:

* Kết quả trả về.
* `assert_called_once_with()`.

---

### Bài 4

Viết Contract Test cho API:

```json
{
    "id": 1,
    "title": "Python",
    "price": 100
}
```

Kiểm tra:

* Đầy đủ trường.
* Kiểu dữ liệu chính xác.

---

### Bài 5

Thiết kế kiến trúc test cho ứng dụng:

```text
PySide6 GUI

↓

FastAPI

↓

SQLite

↓

Redis

↓

Celery

↓

Crawler
```

Phân loại rõ:

* Unit.
* Integration.
* Contract.
* Component.
* E2E.

---

# Tổng kết Buổi 40

Bạn đã học:

* ✅ Phân biệt Mock, Stub, Fake và Spy.
* ✅ `create_autospec()` và Advanced Mocking.
* ✅ Spy với `wraps`.
* ✅ Fake Repository.
* ✅ Contract Testing.
* ✅ API Schema Testing.
* ✅ Message Queue Testing.
* ✅ Redis Testing với `fakeredis`.
* ✅ Celery Task Testing.
* ✅ Event Driven Testing.
* ✅ Kiến trúc kiểm thử cho Microservices.

---

# Góc nhìn Senior Python Developer

Qua 12 buổi về Pytest (từ Buổi 29 đến Buổi 40), bạn đã đi từ:

```text
assert x == y
```

đến việc xây dựng hệ thống kiểm thử cho các ứng dụng có:

* Clean Architecture.
* Domain-Driven Design.
* REST API.
* Message Queue.
* Redis.
* Celery.
* Microservices.

Đây là nền tảng mà các kỹ sư Python sử dụng để phát triển và bảo trì những hệ thống lớn.

---

# Chuẩn bị Buổi 41

**Pytest (Phần 13) – Performance Testing, Benchmarking và Profiling**

Chúng ta sẽ học:

* Performance Test là gì.
* Benchmark với `pytest-benchmark`.
* Đo thời gian thực thi.
* Đo lượng bộ nhớ sử dụng.
* So sánh hiệu năng giữa các phiên bản thuật toán.
* Profiling bằng `cProfile` và `line_profiler`.
* Benchmark cho Parser, Crawler và Repository.
* Thiết lập Performance Regression Test trong CI/CD.

Đây là bước chuyển từ **"code chạy đúng"** sang **"code chạy nhanh và ổn định"**.
