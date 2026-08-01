# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 32: Pytest (Phần 4) – MonkeyPatch chuyên nghiệp trong Python Testing

> **MonkeyPatch là công cụ giúp chúng ta "bẻ hướng" hành vi của chương trình trong lúc chạy test mà không thay đổi code thật.**

Trong dự án thực tế, bạn thường gặp:

* API Key nằm trong biến môi trường.
* File cấu hình.
* Thời gian hiện tại.
* Đường dẫn hệ thống.
* Hàm gọi mạng.
* Hàm random.
* Dependency bên ngoài.

Bạn **không muốn sửa code production**, nhưng muốn kiểm thử nhiều tình huống.

Đó là lúc dùng:

# `monkeypatch`

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu MonkeyPatch.
* Biết khác biệt Mock và MonkeyPatch.
* Thay đổi biến môi trường.
* Patch function.
* Patch object attribute.
* Patch module.
* Patch file system.
* Patch thời gian.
* Test configuration.
* Áp dụng vào dự án thực tế.

---

# Roadmap Pytest

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
Mock trong pytest

Buổi 34+
Testing nâng cao
```

---

# Phần I

# MonkeyPatch là gì?

Tên:

```
Monkey + Patch
```

Ý nghĩa:

> Thay đổi tạm thời một phần của chương trình trong thời gian test.

Ví dụ:

Production:

```python
import os


def get_api_key():

    return os.environ["API_KEY"]
```

---

Trong máy thật:

```text
API_KEY=secret123
```

Nhưng test:

Không muốn dùng key thật.

Ta thay:

```text
API_KEY=test_key
```

bằng MonkeyPatch.

---

# Phần II

# Fixture monkeypatch có sẵn

Pytest tự cung cấp:

```python
def test_x(monkeypatch):
```

Không cần import.

Ví dụ:

```python
def test_env(monkeypatch):

    monkeypatch.setenv("API_KEY", "fake_key")

    assert os.environ["API_KEY"] == "fake_key"
```

---

# Phần III

# setenv()

Đây là ứng dụng phổ biến nhất.

Ví dụ:

File:

```python
config.py
```

```python
import os


API_KEY = os.getenv("API_KEY")
```

---

Test:

```python
def test_api_key(monkeypatch):

    monkeypatch.setenv("API_KEY", "12345")

    import config

    assert config.API_KEY == "12345"
```

---

Ứng dụng:

* API key.
* Database URL.
* Secret.
* Environment config.

---

# Phần IV

# delenv()

Xóa biến môi trường.

Ví dụ:

```python
def test_missing_key(monkeypatch):

    monkeypatch.delenv("API_KEY", raising=False)
```

---

Test:

```python
assert get_api_key() is None
```

---

# Phần V

# setattr()

Thay đổi attribute.

Ví dụ:

Class:

```python
class Config:
    DEBUG = False
```

---

Test:

```python
def test_debug(monkeypatch):

    config = Config()

    monkeypatch.setattr(config, "DEBUG", True)

    assert config.DEBUG
```

---

# Phần VI

# Patch Function

Ví dụ:

Production:

```python
import requests


def get_user():

    response = requests.get("https://api.com/user")

    return response.json()
```

---

Không muốn gọi Internet.

Ta patch:

```python
def test_get_user(monkeypatch):

    def fake_get(url):

        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)
```

---

Khi chạy:

```python
requests.get()
```

sẽ gọi:

```python
fake_get()
```

---

# Phần VII

# Fake Object

Ví dụ:

```python
class FakeResponse:
    def json(self):

        return {"name": "Alice"}
```

---

Test:

```python
def test_user(monkeypatch):

    monkeypatch.setattr(requests, "get", lambda url: FakeResponse())

    result = get_user()

    assert result["name"] == "Alice"
```

---

# Phần VIII

# MonkeyPatch vs Mock

Đây là câu hỏi rất thường gặp.

---

## Mock

Thuộc:

```python
unittest.mock
```

Mạnh về:

* Theo dõi call.
* assert_called.
* return_value.
* side_effect.

Ví dụ:

```python
mock.assert_called_once()
```

---

## MonkeyPatch

Thuộc:

```python
pytest
```

Mạnh về:

* Thay đổi môi trường.
* Thay attribute.
* Thay function.
* Thay config.

---

So sánh:

|                    | Mock  | MonkeyPatch |
| ------------------ | ----- | ----------- |
| Theo dõi gọi       | ⭐⭐⭐⭐⭐ | ⭐           |
| Thay function      | ⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐       |
| Environment        | ❌     | ⭐⭐⭐⭐⭐       |
| Attribute          | ⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐       |
| pytest integration | Tốt   | Rất tốt     |

---

# Phần IX

# Patch Module Function

Ví dụ:

```python
utils.py


def now():

    return datetime.now()
```

---

app.py:

```python
from utils import now


def greeting():

    return str(now())
```

---

Test:

```python
def test_time(monkeypatch):

    monkeypatch.setattr("utils.now", lambda: "2026-01-01")

    assert greeting() == "2026-01-01"
```

---

# Phần X

# Patch Random

Ví dụ:

```python
import random


def create_code():

    return random.randint(1000, 9999)
```

---

Test:

```python
def test_code(monkeypatch):

    monkeypatch.setattr(random, "randint", lambda a, b: 1234)

    assert create_code() == 1234
```

---

Ứng dụng:

* OTP.
* Token.
* Game.
* Sampling.

---

# Phần XI

# Patch DateTime

Đây là tình huống rất thực tế.

Ví dụ:

```python
from datetime import datetime


def is_expired():

    now = datetime.now()

    ...
```

---

Test ngày cố định.

```python
class FakeDate:
    @classmethod
    def now(cls):

        return datetime(2026, 1, 1)
```

---

Patch:

```python
monkeypatch.setattr(module, "datetime", FakeDate)
```

---

Kết quả:

Test không phụ thuộc thời gian thật.

---

# Phần XII

# Patch Path

Ví dụ:

```python
from pathlib import Path


def config_exists():

    return Path("config.json").exists()
```

---

Test:

```python
def test_exists(monkeypatch):

    monkeypatch.setattr(Path, "exists", lambda self: True)

    assert config_exists()
```

---

Ứng dụng:

* File.
* Folder.
* Cache.
* Upload.

---

# Phần XIII

# MonkeyPatch working directory

Ví dụ:

```python
def test_folder(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)
```

---

Sau đó:

```python
open("data.txt")
```

sẽ tạo trong:

```text
tmp
```

---

# Phần XIV

# Kết hợp Fixture + MonkeyPatch

Ví dụ:

```python
@pytest.fixture
def fake_api(monkeypatch):

    monkeypatch.setenv("API_URL", "http://fake")
```

---

Test:

```python
def test_api(fake_api): ...
```

---

# Phần XV

# Mini Project

## Test ứng dụng Crawler

Giả sử:

```text
CrawlerService

↓

Config

↓

HTTP Client

↓

Parser
```

---

Production:

```python
API_URL=
https://website.com
```

---

Test:

MonkeyPatch:

```python
API_URL=
http://fake-server
```

---

Patch:

HTTP Client:

```python
client.get()
```

thành:

```python
fake_get()
```

---

Test:

* Không gọi Internet.
* Không dùng website thật.
* Không cần API key thật.

---

# Phần XVI

# Ví dụ hoàn chỉnh

## Code thật

```python
# service.py

import os
import requests


def fetch_book():

    url = os.getenv("BOOK_API")

    response = requests.get(url)

    return response.json()
```

---

## Test

```python
import service


class Response:
    def json(self):

        return {"title": "Python"}


def test_fetch(monkeypatch):

    monkeypatch.setenv("BOOK_API", "fake-url")

    monkeypatch.setattr(service.requests, "get", lambda url: Response())

    result = service.fetch_book()

    assert result["title"] == "Python"
```

---

Đây là phong cách test thực tế.

---

# Phần XVII

# Sai lầm khi dùng MonkeyPatch

## Sai

Patch quá sâu:

```python
monkeypatch.setattr(builtins, "print", fake)
```

Không nên.

---

## Sai

Patch logic nghiệp vụ.

Ví dụ:

```text
calculate_price()
```

Không nên.

---

## Sai

Không reset.

May mắn:

pytest tự reset sau test.

---

# Phần XVIII

# Khi nào dùng MonkeyPatch?

Dùng cho:

✅ Environment variables
✅ Config
✅ Time
✅ Random
✅ File system
✅ HTTP client
✅ OS interaction

---

Không ưu tiên cho:

❌ Business logic
❌ Algorithm
❌ Pure function

---

# Bài tập thực hành

## Bài 1

Patch:

```python
os.getenv()
```

---

## Bài 2

Patch:

```python
random.randint()
```

---

## Bài 3

Patch:

```python
datetime.now()
```

---

## Bài 4

Patch:

```python
requests.get()
```

---

## Bài 5

Test:

```python
ConfigLoader
```

với:

* Có ENV.
* Không có ENV.

---

# Tổng kết Buổi 32

Bạn đã học:

✅ MonkeyPatch là gì
✅ `setenv()`
✅ `delenv()`
✅ `setattr()`
✅ Patch function
✅ Patch module
✅ Patch random
✅ Patch datetime
✅ Patch filesystem
✅ Patch HTTP
✅ Kết hợp Fixture + MonkeyPatch
✅ So sánh Mock vs MonkeyPatch

---

# Góc lập trình viên chuyên nghiệp

Trong hệ thống Python hiện đại:

```
Production Code
        |
        |
Dependency
        |
        |
----------------
|              |
Real          Fake
(DB/API)      (Test)
```

MonkeyPatch giúp tạo:

```
Production Environment
        |
        |
Test Environment
```

mà không sửa code.

Đây là kỹ thuật rất quan trọng khi xây dựng:

* Web API.
* Crawler.
* Automation.
* AI Agent.
* Microservice.
* CLI Tool.

---

# Chuẩn bị Buổi 33

Buổi tiếp theo:

# **Pytest (Phần 5) – Mock trong pytest: unittest.mock + pytest**

Bạn sẽ học:

* `Mock` trong pytest.
* `MagicMock`.
* `patch`.
* Mock Repository.
* Mock HTTP Client.
* Mock Database.
* Mock Async Function.
* Mock API.
* Mock Queue (Celery/Dramatiq).

Đây sẽ là buổi kết hợp toàn bộ:

**Fixture + Parametrize + MonkeyPatch + Mock**

để tạo bộ test chuyên nghiệp cho dự án Python thực tế.
