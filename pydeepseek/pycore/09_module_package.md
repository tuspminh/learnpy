Chào bạn! Bạn đã vượt qua Bài 8 với Decorator và Closure - tuyệt vời! Bây giờ chúng ta bước vào một chủ đề **CỰC KỲ QUAN TRỌNG** cho các dự án thực tế: **Module và Package**. Đây là cách tổ chức code chuyên nghiệp, tái sử dụng và chia sẻ!

---

# 📘 BÀI 9: MODULE VÀ PACKAGE

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu **Module** và **Package** là gì
- Tạo và import module đúng cách
- Sử dụng `__name__ == "__main__"` để viết script chạy được
- Tạo package với `__init__.py`
- Quản lý dependencies với `pip` và `requirements.txt`
- Hiểu về **virtual environment** (môi trường ảo)
- Tổ chức project chuyên nghiệp theo cấu trúc chuẩn

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Module là gì?

**Module = File Python (.py) chứa code có thể tái sử dụng**

```python
# Tạo file: my_module.py
def hello(name):
    return f"Hello {name}!"


PI = 3.14159


class Calculator:
    def add(self, a, b):
        return a + b
```

**Sử dụng module:**

```python
# File: main.py
import my_module

print(my_module.hello("World"))
print(my_module.PI)
calc = my_module.Calculator()
print(calc.add(3, 5))

# Import cụ thể
from my_module import hello, PI

print(hello("Python"))
print(PI)

# Import với alias
import my_module as mm

print(mm.hello("Alias"))
```

---

### 1.2. `__name__` và `__main__` - Bí mật quan trọng

```python
# my_module.py
def hello(name):
    return f"Hello {name}!"


# Code này chỉ chạy khi file được chạy trực tiếp
if __name__ == "__main__":
    print("Module đang chạy trực tiếp!")
    print(hello("Main"))
    print(f"__name__ = {__name__}")  # __main__

# Khi import, __name__ = 'my_module'
```

**Tại sao cần `if __name__ == "__main__"`:**
- ✅ File có thể vừa là module (để import) vừa là script (để chạy)
- ✅ Code test chỉ chạy khi file được chạy trực tiếp
- ✅ Không chạy code test khi import vào file khác

```python
# utils.py
def tinh_tong(a, b):
    return a + b


def tinh_hieu(a, b):
    return a - b


# Code test - chỉ chạy khi chạy trực tiếp utils.py
if __name__ == "__main__":
    # Test functions
    print("Testing utils.py")
    assert tinh_tong(3, 5) == 8
    assert tinh_hieu(10, 3) == 7
    print("All tests passed!")
```

---

### 1.3. Package là gì?

**Package = Thư mục chứa nhiều module, có file `__init__.py`**

```
my_project/
├── my_package/
│   ├── __init__.py      # Biến thư mục thành package
│   ├── module1.py
│   ├── module2.py
│   └── subpackage/
│       ├── __init__.py
│       └── module3.py
└── main.py
```

**Tạo package:**

```python
# my_package/__init__.py
"""Đây là package của tôi"""

# Export các function quan trọng
from .module1 import function1
from .module2 import function2

__version__ = "1.0.0"
__all__ = ["function1", "function2"]


# my_package/module1.py
def function1():
    return "Function 1 from module1"


# my_package/module2.py
def function2():
    return "Function 2 from module2"


# my_package/subpackage/module3.py
def function3():
    return "Function 3 from subpackage"
```

**Sử dụng package:**

```python
# main.py

# Import toàn bộ package
import my_package

print(my_package.function1())
print(my_package.function2())

# Import specific
from my_package import function1, function2

print(function1())

# Import subpackage
from my_package.subpackage import module3

print(module3.function3())

# Import với alias
import my_package as mp

print(mp.function1())
```

---

### 1.4. Import paths và sys.path

**Cách Python tìm module:**

```python
import sys

# Thứ tự tìm kiếm module
print(sys.path)
# ['/current/directory',
#  '/usr/lib/python3.x',
#  '/usr/lib/python3.x/site-packages', ...]

# Thêm path tùy chỉnh
sys.path.append("/my/custom/path")
import my_custom_module
```

**Relative import (import tương đối):**

```python
# Cấu trúc:
# package/
#   __init__.py
#   module_a.py
#   subpackage/
#       __init__.py
#       module_b.py

# Trong module_b.py:

# Import từ cùng package
from . import module_a  # import module_a trong package hiện tại

# Import từ package cha
from .. import module_a  # import từ package cha

# Import từ package cha, module khác
from ..module_a import some_function
```

---

### 1.5. Virtual Environment (Môi trường ảo)

**Tại sao cần virtual environment:**
- Cách ly dependencies cho từng project
- Tránh xung đột phiên bản
- Dễ dàng chia sẻ và deploy

**Tạo và sử dụng venv:**

```bash
# 1. Tạo virtual environment
python -m venv venv  # Windows/Linux/Mac

# 2. Kích hoạt
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Cài đặt packages
pip install requests pandas numpy

# 4. Xuất danh sách dependencies
pip freeze > requirements.txt

# 5. Cài đặt từ requirements.txt
pip install -r requirements.txt

# 6. Thoát virtual environment
deactivate
```

---

### 1.6. requirements.txt và pyproject.toml

**requirements.txt - Danh sách dependencies:**

```txt
# requirements.txt
requests==2.31.0
pandas>=2.0.0
numpy<2.0.0
flask
beautifulsoup4~=4.12.0

# Dev dependencies
pytest==7.4.0
black==23.0.0
```

**pyproject.toml - Cấu hình project hiện đại:**

```toml
[project]
name = "my_project"
version = "1.0.0"
description = "My awesome Python project"
authors = [
    {name = "Your Name", email = "you@email.com"}
]
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
]
```

---

### 1.7. Cấu trúc project chuyên nghiệp

```
my_project/                        # Project root
├── src/                           # Source code
│   └── my_project/                # Package chính
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── module1.py
│       │   └── module2.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── helpers.py
│       │   └── validators.py
│       └── api/
│           ├── __init__.py
│           ├── client.py
│           └── endpoints.py
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_core/
│   │   ├── test_module1.py
│   │   └── test_module2.py
│   └── test_utils/
│       └── test_helpers.py
├── scripts/                      # Utility scripts
│   ├── setup_db.py
│   └── deploy.py
├── docs/                         # Documentation
│   ├── api.md
│   └── guide.md
├── data/                         # Data files
│   ├── raw/
│   └── processed/
├── config/                       # Configuration
│   ├── config.yaml
│   └── logging.conf
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── pyproject.toml               # Project metadata
├── README.md                    # Project description
├── LICENSE                      # License
└── .gitignore                  # Git ignore
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Xây dựng Package cho xử lý dữ liệu

```python
# Cấu trúc:
# data_processor/
#   __init__.py
#   core/
#       __init__.py
#       processor.py
#   utils/
#       __init__.py
#       validators.py
#       converters.py
#   tests/
#       test_processor.py

# ---------- data_processor/core/processor.py ----------
class DataProcessor:
    """Xử lý dữ liệu cơ bản"""

    def __init__(self, data):
        self.data = data
        self.is_processed = False

    def clean(self):
        """Làm sạch dữ liệu"""
        self.data = [x for x in self.data if x is not None]
        return self

    def normalize(self):
        """Chuẩn hóa dữ liệu"""
        if not self.data:
            return self
        min_val = min(self.data)
        max_val = max(self.data)
        if max_val - min_val == 0:
            return self
        self.data = [(x - min_val) / (max_val - min_val) for x in self.data]
        return self

    def filter(self, threshold):
        """Lọc dữ liệu"""
        self.data = [x for x in self.data if x > threshold]
        return self

    def get_stats(self):
        """Thống kê cơ bản"""
        if not self.data:
            return {}
        return {
            "count": len(self.data),
            "min": min(self.data),
            "max": max(self.data),
            "sum": sum(self.data),
            "avg": sum(self.data) / len(self.data),
        }

    def transform(self, func):
        """Áp dụng hàm biến đổi"""
        self.data = [func(x) for x in self.data]
        return self


# ---------- data_processor/utils/validators.py ----------
def validate_number(value):
    """Kiểm tra số hợp lệ"""
    return isinstance(value, (int, float))


def validate_positive(value):
    """Kiểm tra số dương"""
    return validate_number(value) and value > 0


def validate_in_range(value, min_val, max_val):
    """Kiểm tra trong khoảng"""
    return validate_number(value) and min_val <= value <= max_val


# ---------- data_processor/utils/converters.py ----------
def to_float(value):
    """Chuyển sang float"""
    try:
        return float(value)
    except ValueError, TypeError:
        return None


def to_int(value):
    """Chuyển sang int"""
    try:
        return int(value)
    except ValueError, TypeError:
        return None


# ---------- data_processor/__init__.py ----------
"""
Data Processor Package
Xử lý và biến đổi dữ liệu
"""

from .core.processor import DataProcessor
from .utils import validators, converters

__version__ = "1.0.0"
__all__ = ["DataProcessor", "validators", "converters"]

# ---------- data_processor/tests/test_processor.py ----------
import unittest
from data_processor import DataProcessor


class TestDataProcessor(unittest.TestCase):
    def test_clean(self):
        processor = DataProcessor([1, None, 2, None, 3])
        processor.clean()
        self.assertEqual(processor.data, [1, 2, 3])

    def test_normalize(self):
        processor = DataProcessor([1, 2, 3, 4, 5])
        processor.normalize()
        self.assertEqual(processor.data, [0.0, 0.25, 0.5, 0.75, 1.0])

    def test_filter(self):
        processor = DataProcessor([1, 2, 3, 4, 5])
        processor.filter(3)
        self.assertEqual(processor.data, [4, 5])

    def test_transform(self):
        processor = DataProcessor([1, 2, 3])
        processor.transform(lambda x: x**2)
        self.assertEqual(processor.data, [1, 4, 9])


if __name__ == "__main__":
    unittest.main()

# ---------- main.py (sử dụng package) ----------
from data_processor import DataProcessor, validators, converters

# Dữ liệu mẫu
raw_data = [1, 2, None, 3, 4, 5, None, 6, 7, 8, 9, 10]

# Xử lý dữ liệu
processor = DataProcessor(raw_data)
processor.clean()
processor.filter(3)
processor.normalize()
processor.transform(lambda x: x * 100)

# Kết quả
print("Dữ liệu đã xử lý:", processor.data)
print("Thống kê:", processor.get_stats())

# Sử dụng utils
print("Is 10 valid number?", validators.validate_number(10))
print("Is -5 positive?", validators.validate_positive(-5))
```

---

### Ví dụ 2: Package cho Web API Client

```python
# Cấu trúc:
# api_client/
#   __init__.py
#   client.py
#   errors.py
#   models.py
#   utils.py

# ---------- api_client/errors.py ----------
class APIError(Exception):
    """Base exception for API errors"""

    pass


class ConnectionError(APIError):
    """Connection error"""

    pass


class AuthenticationError(APIError):
    """Authentication failed"""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded"""

    pass


class NotFoundError(APIError):
    """Resource not found"""

    pass


# ---------- api_client/models.py ----------
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool = True

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            created_at=datetime.fromisoformat(data.get("created_at")),
            is_active=data.get("is_active", True),
        )


@dataclass
class Post:
    id: int
    user_id: int
    title: str
    body: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("userId"),
            title=data.get("title"),
            body=data.get("body"),
            created_at=datetime.now(),
        )


# ---------- api_client/client.py ----------
import requests
import time
from typing import Optional, Dict, Any, List
from .errors import *
from .models import User, Post


class APIClient:
    """API Client với retry và rate limiting"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PythonAPIClient/1.0"})
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self._request_count = 0
        self._last_reset = time.time()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Thực hiện request với retry và error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Rate limiting (max 60 requests per minute)
        self._check_rate_limit()

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, timeout=10, **kwargs)
                self._request_count += 1

                # Xử lý status code
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key or credentials")
                elif response.status_code == 404:
                    raise NotFoundError("Resource not found")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    if attempt < max_retries - 1:
                        wait = 2**attempt  # Exponential backoff
                        time.sleep(wait)
                        continue
                    else:
                        raise APIError(f"Server error: {response.status_code}")
                else:
                    raise APIError(f"Request failed: {response.status_code}")

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    time.sleep(wait)
                    continue
                raise ConnectionError(f"Connection error: {str(e)}")

    def _check_rate_limit(self):
        """Kiểm tra rate limit (60 requests/minute)"""
        current_time = time.time()
        if current_time - self._last_reset > 60:
            self._request_count = 0
            self._last_reset = current_time

        if self._request_count >= 60:
            wait = 60 - (current_time - self._last_reset)
            if wait > 0:
                time.sleep(wait + 1)
            self._request_count = 0
            self._last_reset = time.time()

    # Các phương thức API cụ thể
    def get_users(self) -> List[User]:
        """Lấy danh sách users"""
        data = self._make_request("GET", "/users")
        return [User.from_dict(item) for item in data]

    def get_user(self, user_id: int) -> User:
        """Lấy user theo ID"""
        data = self._make_request("GET", f"/users/{user_id}")
        return User.from_dict(data)

    def get_posts(self, user_id: Optional[int] = None) -> List[Post]:
        """Lấy danh sách posts"""
        endpoint = "/posts"
        if user_id:
            endpoint = f"/posts?userId={user_id}"
        data = self._make_request("GET", endpoint)
        return [Post.from_dict(item) for item in data]

    def create_user(self, name: str, email: str) -> User:
        """Tạo user mới"""
        data = self._make_request("POST", "/users", json={"name": name, "email": email})
        return User.from_dict(data)

    def update_user(self, user_id: int, **kwargs) -> User:
        """Cập nhật user"""
        data = self._make_request("PUT", f"/users/{user_id}", json=kwargs)
        return User.from_dict(data)

    def delete_user(self, user_id: int) -> bool:
        """Xóa user"""
        try:
            self._make_request("DELETE", f"/users/{user_id}")
            return True
        except NotFoundError:
            return False


# ---------- api_client/__init__.py ----------
"""
API Client Package
Client cho REST API với đầy đủ tính năng
"""

from .client import APIClient
from .models import User, Post
from .errors import *

__version__ = "1.0.0"
__all__ = ["APIClient", "User", "Post"]

# ---------- main.py (sử dụng package) ----------
from api_client import APIClient, User, Post
from api_client.errors import *


def main():
    # Tạo client
    client = APIClient("https://jsonplaceholder.typicode.com")

    try:
        # Lấy danh sách users
        print("=== GETTING USERS ===")
        users = client.get_users()
        for user in users[:3]:  # Chỉ lấy 3 user đầu
            print(f"User: {user.name} ({user.email})")

        # Lấy posts của user đầu tiên
        if users:
            print(f"\n=== POSTS OF USER {users[0].id} ===")
            posts = client.get_posts(user_id=users[0].id)
            for post in posts[:3]:
                print(f"Post: {post.title}")

        # Tạo user mới
        print("\n=== CREATING USER ===")
        new_user = client.create_user("Nguyen Van A", "a@gmail.com")
        print(f"Created: {new_user.name} ({new_user.id})")

    except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
    except RateLimitError as e:
        print(f"❌ Rate limit: {e}")
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except APIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
```

---

### Ví dụ 3: Utility Package với CLI

```python
# Cấu trúc:
# mytools/
#   __init__.py
#   file_utils.py
#   string_utils.py
#   time_utils.py
#   cli.py
#   __main__.py

# ---------- mytools/file_utils.py ----------
import os
import json
import csv
from typing import List, Dict, Any


def read_json(filepath: str) -> Dict[str, Any]:
    """Đọc file JSON"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str, data: Dict[str, Any], indent: int = 2):
    """Ghi file JSON"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def read_csv(filepath: str) -> List[Dict[str, str]]:
    """Đọc file CSV"""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(filepath: str, data: List[Dict[str, Any]]):
    """Ghi file CSV"""
    if not data:
        return
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def get_file_size(filepath: str) -> int:
    """Lấy kích thước file (bytes)"""
    return os.path.getsize(filepath)


def file_exists(filepath: str) -> bool:
    """Kiểm tra file tồn tại"""
    return os.path.exists(filepath)


# ---------- mytools/string_utils.py ----------
import re
from typing import Optional


def slugify(text: str) -> str:
    """Tạo slug từ chuỗi"""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Cắt chuỗi đến độ dài nhất định"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + suffix


def extract_emails(text: str) -> List[str]:
    """Trích xuất email từ chuỗi"""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.findall(pattern, text)


def is_valid_email(email: str) -> bool:
    """Kiểm tra email hợp lệ"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Kiểm tra số điện thoại (Vietnam)"""
    pattern = r"^(0|84)(3[2-9]|5[6-9]|7[0-9]|8[1-9]|9[0-9])[0-9]{7}$"
    return bool(re.match(pattern, phone))


# ---------- mytools/time_utils.py ----------
from datetime import datetime, timedelta
import time
from typing import Union


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Định dạng datetime"""
    return dt.strftime(fmt)


def parse_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime từ chuỗi"""
    return datetime.strptime(date_str, fmt)


def time_ago(dt: datetime) -> str:
    """Thời gian đã trôi qua"""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if days >= 30:
        return f"{days // 30} tháng trước"
    elif days >= 7:
        return f"{days // 7} tuần trước"
    elif days >= 1:
        return f"{int(days)} ngày trước"
    elif hours >= 1:
        return f"{int(hours)} giờ trước"
    elif minutes >= 1:
        return f"{int(minutes)} phút trước"
    else:
        return "Vừa xong"


def sleep_seconds(seconds: Union[int, float]):
    """Sleep trong seconds"""
    time.sleep(seconds)


# ---------- mytools/cli.py ----------
import argparse
from . import file_utils, string_utils, time_utils


def create_parser():
    """Tạo command line parser"""
    parser = argparse.ArgumentParser(description="Mytools - Công cụ hữu ích cho Python")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # File commands
    file_parser = subparsers.add_parser("file", help="File operations")
    file_parser.add_argument("action", choices=["read", "write", "size", "exists"])
    file_parser.add_argument("path", help="File path")
    file_parser.add_argument("--data", help="Data to write (JSON format)")

    # String commands
    string_parser = subparsers.add_parser("string", help="String operations")
    string_parser.add_argument("action", choices=["slug", "truncate", "emails"])
    string_parser.add_argument("text", help="Input text")
    string_parser.add_argument("--length", type=int, default=100, help="Max length")

    # Time commands
    time_parser = subparsers.add_parser("time", help="Time operations")
    time_parser.add_argument("action", choices=["format", "ago"])
    time_parser.add_argument("datetime", help="Date/Time string")

    return parser


def main():
    """CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "file":
        if args.action == "read":
            data = file_utils.read_json(args.path)
            print(data)
        elif args.action == "size":
            size = file_utils.get_file_size(args.path)
            print(f"Size: {size} bytes")
        elif args.action == "exists":
            exists = file_utils.file_exists(args.path)
            print(f"Exists: {exists}")

    elif args.command == "string":
        if args.action == "slug":
            print(string_utils.slugify(args.text))
        elif args.action == "truncate":
            print(string_utils.truncate(args.text, args.length))
        elif args.action == "emails":
            emails = string_utils.extract_emails(args.text)
            print(f"Found emails: {emails}")

    elif args.command == "time":
        if args.action == "format":
            dt = time_utils.parse_datetime(args.datetime)
            print(time_utils.format_datetime(dt))
        elif args.action == "ago":
            dt = time_utils.parse_datetime(args.datetime)
            print(time_utils.time_ago(dt))
    else:
        parser.print_help()


# ---------- mytools/__main__.py ----------
"""Cho phép chạy package như script: python -m mytools"""

from .cli import main

if __name__ == "__main__":
    main()

# ---------- mytools/__init__.py ----------
"""
MyTools - Bộ công cụ hữu ích cho Python
"""

from .file_utils import *
from .string_utils import *
from .time_utils import *

__version__ = "1.0.0"
__all__ = [
    # file_utils
    "read_json",
    "write_json",
    "read_csv",
    "write_csv",
    "get_file_size",
    "file_exists",
    # string_utils
    "slugify",
    "truncate",
    "extract_emails",
    "is_valid_email",
    "is_valid_phone",
    # time_utils
    "format_datetime",
    "parse_datetime",
    "time_ago",
    "sleep_seconds",
]

# ---------- Sử dụng trong terminal ----------
"""
# Chạy CLI
python -m mytools string slug "Hello World!"
python -m mytools string truncate "Very long text..." --length 10
python -m mytools file size README.md
python -m mytools time ago "2024-01-01 00:00:00"

# Cài đặt package (sau khi có setup.py)
pip install -e .

# Sử dụng trong code
from mytools import slugify, read_json
slug = slugify("Hello World!")
data = read_json("config.json")
"""
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Tạo module `math_utils.py` với các hàm:
- `is_prime(n)`: Kiểm tra số nguyên tố
- `gcd(a, b)`: Ước chung lớn nhất
- `lcm(a, b)`: Bội chung nhỏ nhất
- `fibonacci(n)`: Dãy Fibonacci

**Bài 2:** Tạo module `string_utils.py` với các hàm:
- `reverse(text)`: Đảo ngược chuỗi
- `count_vowels(text)`: Đếm nguyên âm
- `is_palindrome(text)`: Kiểm tra chuỗi đối xứng

**Bài 3:** Tạo package `calculator` với các module:
- `basic.py`: Cộng, trừ, nhân, chia
- `advanced.py`: Lũy thừa, căn bậc 2, sin, cos
- `__init__.py`: Export các hàm chính

**Bài 4:** Tạo module `file_manager.py` với các hàm đọc/ghi file:
- `read_file(path)`: Đọc file text
- `write_file(path, content)`: Ghi file text
- `append_file(path, content)`: Thêm vào file
- `count_lines(path)`: Đếm số dòng

**Bài 5:** Tạo module `data_validator.py` với các hàm kiểm tra:
- `is_valid_email(email)`
- `is_valid_phone(phone)`
- `is_valid_date(date_str)`

**Bài 6:** Tạo package `mytools` với module `__main__.py` để chạy CLI.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Tạo package `database` với:
- `connection.py`: Kết nối database
- `models.py`: Định nghĩa models
- `queries.py`: Các query thường dùng
- `__init__.py`: Export các hàm chính

**Bài 8:** Tạo module `decorators.py` với các decorator:
- `@timer`: Đo thời gian
- `@logger`: Log function calls
- `@retry`: Retry on error
- Có thể import và sử dụng trong nhiều project

**Bài 9:** Tạo package `logging_utils` với:
- `handlers.py`: Custom log handlers
- `formatters.py`: Custom log formatters
- `config.py`: Logging configuration
- Hỗ trợ log ra file, console, JSON

**Bài 10:** Tạo package `config_manager` với:
- `loader.py`: Đọc config từ file (JSON, YAML)
- `validator.py`: Validate config
- `manager.py`: Quản lý config
- Hỗ trợ environment variables override

---

## 🏗️ MINI-PROJECT: XÂY DỰNG THƯ VIỆN TOOLS

```python
"""
Xây dựng thư viện tools với cấu trúc package hoàn chỉnh:

1. Cấu trúc thư mục:
mytools/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── file_utils.py
│   ├── string_utils.py
│   ├── time_utils.py
│   └── math_utils.py
├── web/
│   ├── __init__.py
│   ├── scraper.py
│   └── api_client.py
├── data/
│   ├── __init__.py
│   ├── converter.py
│   └── validator.py
├── cli.py
├── __main__.py
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE

2. Các tính năng:
   - Xử lý file (JSON, CSV, TXT, Excel)
   - Xử lý string (slug, truncate, validate)
   - Xử lý time (format, parse, time_ago)
   - Web scraping (requests + beautifulsoup)
   - API client (with retry, rate limit)
   - Data conversion (dict ↔ JSON ↔ CSV ↔ XML)
   - CLI commands

3. Đóng gói:
   - setup.py để pip install
   - requirements.txt cho dependencies
   - Documentation
   - Unit tests
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE MODULE/PACKAGE CHUYÊN NGHIỆP

- [ ] Có `__init__.py` trong các package
- [ ] Sử dụng `__name__ == "__main__"` cho test code
- [ ] Import đúng cách (absolute/relative imports)
- [ ] Có `requirements.txt` hoặc `pyproject.toml`
- [ ] Có virtual environment cho project
- [ ] Code được tổ chức theo cấu trúc module rõ ràng
- [ ] Có docstring cho package, module, function
- [ ] Sử dụng `__all__` để kiểm soát export

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo package có thể import với tên ngắn:
# install: pip install mytools
# import: import mt
#
# Sau đó có thể dùng:
# mt.file.read_json("data.json")
# mt.string.slugify("Hello World")
# mt.time.time_ago("2024-01-01")
```

---

## 📦 TÓM TẮT LỆNH QUAN TRỌNG

| Lệnh | Mô tả |
|------|-------|
| `python -m venv venv` | Tạo virtual environment |
| `venv\Scripts\activate` | Kích hoạt venv (Windows) |
| `source venv/bin/activate` | Kích hoạt venv (Linux/Mac) |
| `pip install package` | Cài đặt package |
| `pip install -r requirements.txt` | Cài đặt từ requirements |
| `pip freeze > requirements.txt` | Xuất dependencies |
| `python -m mypackage` | Chạy package như script |
| `pip install -e .` | Cài đặt package ở chế độ dev |

---

**Chúc mừng bạn đã hoàn thành Bài 9! Việc tổ chức code thành module và package là kỹ năng không thể thiếu cho dự án thực tế.** 💪

*Bài 10 sẽ dạy bạn về File I/O và Serialization - cách làm việc với dữ liệu bên ngoài!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀