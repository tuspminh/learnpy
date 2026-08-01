# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 28: Testing (Phần 3) - Làm chủ `unittest.mock` từ cơ bản đến chuyên nghiệp

> **Đây là một trong những buổi quan trọng nhất của toàn bộ khóa học Python.**

Nếu bạn hỏi:

> **Kỹ năng nào phân biệt Junior và Senior trong việc viết Unit Test?**

Câu trả lời gần như luôn là:

> **Mock**

Trong các dự án:

* FastAPI
* Django
* Flask
* PySide6
* Scrapy
* Celery
* AI Agent
* Microservice

**Mock xuất hiện ở khắp nơi.**

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Mock là gì.
* Biết khi nào cần Mock.
* Thành thạo `Mock`.
* Thành thạo `MagicMock`.
* Thành thạo `patch()`.
* Thành thạo `patch.object()`.
* Thành thạo `patch.dict()`.
* Biết `return_value`.
* Biết `side_effect`.
* Kiểm tra lời gọi hàm.
* Mock File.
* Mock HTTP.
* Mock Database.
* Mock Repository.

---

# Roadmap phần Testing

```text
Phần I. unittest
✓ Buổi 26
✓ Buổi 27

Phần II. Mock
✓ Buổi 28

Phần III. pytest
Buổi 29 -> 33

Phần IV. Testing nâng cao
Buổi 34 -> 39
```

---

# Phần I

# Mock là gì?

Ví dụ:

```python
def download():
    requests.get(...)
```

Nếu test:

↓

Python sẽ gọi Internet thật.

Không tốt.

Ta thay bằng:

```text
Internet giả
```

Đó chính là Mock.

---

## Mock là "diễn viên đóng thế"

Ví dụ phim:

```text
Tom Cruise

↓

Cascadeur
```

Trong test:

```text
Database

↓

Mock Database
```

---

# Vì sao cần Mock?

Giả sử:

```python
user = service.login(...)
```

Trong hàm này:

```text
Login

↓

SQLite

↓

Redis

↓

HTTP API

↓

Email
```

Nếu test thật:

* chậm
* cần Internet
* cần DB
* khó lặp lại

Mock giải quyết tất cả.

---

# Phần II

# Mock đầu tiên

```python
from unittest.mock import Mock

database = Mock()

database.get_user.return_value = "Alice"

print(database.get_user())
```

Kết quả:

```text
Alice
```

Không có:

Database thật.

---

# Phần III

# return_value

Ví dụ:

```python
api = Mock()

api.fetch.return_value = {"name": "John"}
```

Sau đó:

```python
result = api.fetch()
```

↓

```python
{"name": "John"}
```

---

## Thực tế

Repository:

```python
repo.find_user.return_value = User(...)
```

Service:

Không biết.

Tưởng:

Repository thật.

---

# Phần IV

# side_effect

Có khi:

Không muốn:

```python
return_value
```

Muốn:

Exception.

Ví dụ.

```python
repo.save.side_effect = ValueError
```

Khi gọi:

```python
repo.save()
```

↓

```text
ValueError
```

---

## side_effect với hàm

```python
def fake_add(a, b):

    return a + b + 100
```

```python
mock = Mock()

mock.add.side_effect = fake_add

print(mock.add(2, 3))
```

↓

```text
105
```

---

## side_effect với danh sách

```python
mock.read.side_effect = [1, 2, 3]
```

↓

Lần gọi:

```text
1
```

↓

```text
2
```

↓

```text
3
```

---

# Phần V

# assert_called

Mock nhớ:

Ai gọi nó.

Ví dụ.

```python
api.send("hello")
```

Test.

```python
api.send.assert_called()
```

---

## assert_called_once

```python
api.send.assert_called_once()
```

---

## assert_called_with

```python
api.send.assert_called_with("hello")
```

---

## assert_any_call

```python
mock.send("A")

mock.send("B")

mock.send.assert_any_call("A")
```

---

## call_count

```python
print(mock.send.call_count)
```

↓

```text
2
```

---

# call_args

```python
mock.send("hello", 123)
```

↓

```python
print(mock.send.call_args)
```

↓

```text
call(
    "hello",
    123
)
```

---

# call_args_list

```python
A

B

C
```

↓

```python
mock.send.call_args_list
```

↓

```text
[
 call("A"),
 call("B"),
 call("C")
]
```

---

# Phần VI

# MagicMock

Mock:

↓

Không có magic method.

Ví dụ.

```python
mock = Mock()

len(mock)
```

↓

Lỗi.

---

MagicMock.

```python
from unittest.mock import MagicMock

mock = MagicMock()

print(len(mock))
```

↓

OK.

---

## Magic Method

Có:

```python
__len__

__iter__

__getitem__

__enter__

__exit__
```

Đều hoạt động.

---

# Phần VII

# patch()

Đây là kỹ thuật dùng nhiều nhất.

Ví dụ.

```python
import requests

requests.get(...)
```

Không muốn gọi thật.

---

```python
from unittest.mock import patch
```

---

Ví dụ.

```python
with patch("requests.get") as mock_get:
    mock_get.return_value.status_code = 200

    ...
```

Không gọi Internet.

---

# Decorator

```python
@patch("requests.get")
def test(mock_get): ...
```

---

# Phần VIII

# patch.object()

Ví dụ.

```python
class User:
    def login(self): ...
```

Test.

```python
with patch.object(User, "login"):
    ...
```

---

# Phần IX

# patch.dict()

Ví dụ.

```python
os.environ
```

Không muốn sửa thật.

```python
with patch.dict(os.environ, {"DEBUG": "1"}):
    ...
```

Ra khỏi:

↓

Khôi phục.

---

# Phần X

# Mock File

Ví dụ.

```python
open("config.json")
```

Không muốn tạo file.

Python có:

```python
mock_open
```

Ví dụ.

```python
from unittest.mock import mock_open
from unittest.mock import patch

m = mock_open(read_data="hello")

with patch("builtins.open", m):
    with open("a.txt") as f:
        print(f.read())
```

↓

```text
hello
```

---

# Phần XI

# Mock HTTP

Ví dụ.

```python
requests.get(...)
```

↓

```python
response = Mock()

response.status_code = 200

response.json.return_value = {"name": "Alice"}
```

Sau đó.

```python
mock_get.return_value = response
```

Service nghĩ:

Đang gọi API thật.

---

# Phần XII

# Mock Repository

Giả sử.

```python
BookService
```

↓

```python
BookRepository
```

Trong test.

```python
repo = Mock()
```

↓

```python
repo.find.return_value = Book(...)
```

↓

```python
service = BookService(repo)
```

Đây là cách kiểm thử trong:

* Clean Architecture
* DDD

---

# Phần XIII

# Mock datetime

Ví dụ.

```python
datetime.now()
```

Không muốn:

Thời gian thay đổi.

↓

Patch.

```python
@patch("module.datetime")
```

Trả về:

```python
2026-01-01
```

---

# Phần XIV

# Mock Exception

```python
repo.save.side_effect = IOError
```

↓

Test.

```python
with self.assertRaises(
    IOError
):
```

---

# Phần XV

# Những lỗi phổ biến

## Sai

Mock:

Mọi thứ.

↓

Test vô nghĩa.

---

## Sai

Patch sai namespace.

Ví dụ:

```python
patch("requests.get")
```

Trong khi module của bạn đã:

```python
from requests import get
```

Lúc này phải patch:

```python
patch("your_module.get")
```

**Nguyên tắc quan trọng:**

> **Patch nơi đối tượng được sử dụng, không phải nơi nó được định nghĩa.**

Đây là lỗi phổ biến nhất khi học `patch()`.

---

## Sai

Không kiểm tra:

```python
assert_called_with()
```

---

## Sai

Mock:

Logic.

Chỉ Mock:

* Database
* HTTP
* Redis
* SMTP
* File
* Queue

Không Mock:

Business Logic.

---

# Phần XVI

# Thực hành

## Bài 1

Mock.

```python
Repository
```

↓

```python
find_user()
```

---

## Bài 2

Mock.

```python
requests.get()
```

↓

```python
status = 200
```

---

## Bài 3

Mock.

```python
open()
```

↓

Đọc:

```text
config.json
```

---

## Bài 4

Dùng:

```python
assert_called_once()
```

---

## Bài 5

Patch.

```python
datetime.now()
```

↓

Ngày cố định.

---

## Bài 6

Mock.

```python
SQLite Repository
```

↓

Test.

```python
BookService
```

---

# Mini Project

# Kiểm thử Service bằng Mock

Đây là ví dụ rất sát với các dự án **Repository Pattern**, **Clean Architecture**, **DDD** và **ứng dụng cào truyện** mà bạn đã học.

## Cấu trúc

```text
story_app/
│
├── services/
│   └── chapter_service.py
├── repositories/
│   └── chapter_repository.py
├── downloaders/
│   └── http_downloader.py
└── tests/
    └── test_chapter_service.py
```

## `ChapterService`

```text
download_chapter()

↓

Repository.save()

↓

Logger.info()
```

### Yêu cầu kiểm thử

* Mock `ChapterRepository`.
* Mock `HttpDownloader`.
* Kiểm tra:

  * Downloader được gọi đúng URL.
  * Repository được gọi đúng dữ liệu.
  * Logger ghi đúng thông điệp.
* Mô phỏng lỗi mạng bằng:

```python
side_effect = TimeoutError
```

và kiểm tra Service xử lý ngoại lệ đúng.

**Lưu ý:** Không gọi HTTP thật và không ghi SQLite thật.

---

# Tổng kết buổi 28

Hôm nay bạn đã học:

* ✅ `Mock`
* ✅ `MagicMock`
* ✅ `return_value`
* ✅ `side_effect`
* ✅ `assert_called*`
* ✅ `call_args`
* ✅ `patch()`
* ✅ `patch.object()`
* ✅ `patch.dict()`
* ✅ `mock_open`
* ✅ Mock HTTP
* ✅ Mock Repository
* ✅ Mock File
* ✅ Mock Exception

---

# Góc lập trình viên chuyên nghiệp

Một quy tắc rất quan trọng khi thiết kế kiến trúc để dễ kiểm thử là:

> **Dependency Injection (DI)**

Ví dụ:

```python
class BookService:
    def __init__(self, repository):
        self.repository = repository
```

Thay vì tự tạo:

```python
class BookService:
    def __init__(self):
        self.repository = SQLiteBookRepository()  # Khó test
```

Cách thứ nhất giúp bạn truyền vào:

* Repository thật khi chạy ứng dụng.
* Mock Repository khi chạy Unit Test.

Đây là nền tảng của **Clean Architecture**, **DDD**, **Hexagonal Architecture** và hầu hết các framework hiện đại.

---

# Chuẩn bị cho Buổi 29

Ở **Buổi 29**, chúng ta sẽ bắt đầu học **pytest** – framework kiểm thử phổ biến nhất trong hệ sinh thái Python.

Bạn sẽ học:

* Vì sao nhiều dự án chuyển từ `unittest` sang `pytest`.
* Cách cài đặt và chạy `pytest`.
* Viết test không cần kế thừa `TestCase`.
* Assertion thông minh của `pytest`.
* Tổ chức thư mục kiểm thử.
* So sánh `pytest` với `unittest`.
* Áp dụng `pytest` cho các module, Repository và Service trong các dự án Python hiện đại.

Sau đó, chúng ta sẽ tiếp tục với **Fixture**, **Parametrize**, **MonkeyPatch**, **Plugin**, **Async Testing** và tích hợp `pytest` vào CI/CD.
