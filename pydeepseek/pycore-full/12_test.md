Chào bạn! Bạn đã vượt qua Bài 11 về Iterator và Generator - tuyệt vời! Bây giờ chúng ta bước vào **Bài 12: Unit Test và Debug** - đây là kỹ năng phân biệt lập trình viên nghiệp dư và chuyên nghiệp. Code không test = code không hoàn chỉnh!

---

# 📘 BÀI 12: UNIT TEST VÀ DEBUG

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Viết và chạy **Unit Test** với `unittest`
- Sử dụng **pytest** - framework test hiện đại
- Hiểu **Test-Driven Development (TDD)**
- Debug code với **pdb** (Python Debugger)
- Sử dụng **logging** để theo dõi ứng dụng
- Viết test cho các tình huống edge cases
- Đo độ phủ code (coverage)

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Tại sao cần Unit Test?

**Lợi ích của Unit Test:**
- ✅ Phát hiện lỗi sớm
- ✅ Đảm bảo code hoạt động đúng
- ✅ Tài liệu sống (documentation)
- ✅ Dễ dàng refactor mà không sợ phá vỡ
- ✅ Tăng độ tin cậy của code

**Các loại test:**
1. **Unit Test**: Kiểm tra từng function/class riêng lẻ
2. **Integration Test**: Kiểm tra tương tác giữa các thành phần
3. **System Test**: Kiểm tra toàn bộ hệ thống
4. **Acceptance Test**: Kiểm tra user requirements

---

### 1.2. unittest - Test Framework tích hợp sẵn

```python
import unittest


# Code cần test
def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x):
        self.result += x
        return self.result

    def subtract(self, x):
        self.result -= x
        return self.result


# Test Class
class TestMathFunctions(unittest.TestCase):
    """Test các hàm toán học"""

    # Setup - Chạy trước mỗi test
    def setUp(self):
        self.calc = Calculator()
        print(f"\n🔄 Setup for test: {self._testMethodName}")

    # Teardown - Chạy sau mỗi test
    def tearDown(self):
        print(f"🧹 Teardown for test: {self._testMethodName}")

    # Test add function
    def test_add_positive_numbers(self):
        self.assertEqual(add(3, 5), 8)
        self.assertEqual(add(10, 20), 30)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-3, -5), -8)
        self.assertEqual(add(-10, 5), -5)

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)
        self.assertEqual(add(0, 0), 0)

    # Test divide function
    def test_divide_positive(self):
        self.assertEqual(divide(10, 2), 5)
        self.assertEqual(divide(15, 3), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

    # Test Calculator class
    def test_calculator_add(self):
        self.calc.add(5)
        self.assertEqual(self.calc.result, 5)
        self.calc.add(3)
        self.assertEqual(self.calc.result, 8)

    def test_calculator_subtract(self):
        self.calc.add(10)
        self.calc.subtract(3)
        self.assertEqual(self.calc.result, 7)


# Các assertion methods thường dùng:
# assertEqual(a, b)      - a == b
# assertNotEqual(a, b)   - a != b
# assertTrue(x)          - bool(x) is True
# assertFalse(x)         - bool(x) is False
# assertIs(a, b)         - a is b
# assertIsNone(x)        - x is None
# assertIn(a, b)         - a in b
# assertRaises(Error)    - Exception được raise
# assertAlmostEqual(a, b) - a ≈ b (cho float)

if __name__ == "__main__":
    # Chạy tất cả tests
    unittest.main()

    # Chạy với verbosity cao hơn
    # unittest.main(verbosity=2)
```

---

### 1.3. pytest - Framework test hiện đại

```python
# Cài đặt: pip install pytest

# Code cần test
def is_prime(n):
    """Kiểm tra số nguyên tố"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def factorial(n):
    """Tính giai thừa"""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n == 0:
        return 1
    return n * factorial(n - 1)


def process_data(data):
    """Xử lý dữ liệu"""
    if not data:
        return []
    return [x * 2 for x in data if x > 0]


# File: test_math.py (pytest sẽ tự động tìm file test_*.py)
import pytest


def test_is_prime():
    """Test số nguyên tố"""
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(1) == False
    assert is_prime(0) == False
    assert is_prime(17) == True
    assert is_prime(18) == False


def test_is_prime_edge_cases():
    """Test edge cases cho số nguyên tố"""
    assert is_prime(-5) == False
    assert is_prime(100) == False


def test_factorial():
    """Test giai thừa"""
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    assert factorial(10) == 3628800


def test_factorial_negative():
    """Test giai thừa với số âm"""
    with pytest.raises(ValueError):
        factorial(-1)


def test_process_data():
    """Test xử lý dữ liệu"""
    assert process_data([1, -2, 3, -4, 5]) == [2, 6, 10]
    assert process_data([]) == []
    assert process_data([-1, -2, -3]) == []


# Fixtures trong pytest
@pytest.fixture
def sample_data():
    """Tạo dữ liệu mẫu cho test"""
    return [1, 2, 3, 4, 5]


def test_process_with_fixture(sample_data):
    """Test với fixture"""
    result = process_data(sample_data)
    assert result == [2, 4, 6, 8, 10]


# Parametrize - Chạy nhiều test cases
@pytest.mark.parametrize(
    "input,expected",
    [
        (2, True),
        (3, True),
        (4, False),
        (1, False),
        (0, False),
        (17, True),
        (18, False),
    ],
)
def test_is_prime_parametrize(input, expected):
    """Test với nhiều input parameters"""
    assert is_prime(input) == expected


# Skip test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass


# Expected failure
@pytest.mark.xfail(reason="Known bug")
def test_known_bug():
    assert 1 == 2


# Chạy test: pytest test_math.py -v
# Chạy với coverage: pytest --cov=. test_math.py
```

---

### 1.4. Test-Driven Development (TDD)

**Vòng đời TDD: Red → Green → Refactor**

```python
# Bước 1: Viết test trước (RED - test sẽ fail)
def test_calculate_discount():
    # Chưa có function calculate_discount
    assert calculate_discount(100, 0.1) == 90
    assert calculate_discount(200, 0.2) == 160
    assert calculate_discount(50, 0) == 50
    assert calculate_discount(100, 1.0) == 0


# Bước 2: Viết code tối thiểu để pass test (GREEN)
def calculate_discount(price, discount):
    """Tính giá sau giảm giá"""
    return price * (1 - discount)


# Bước 3: Refactor - Cải thiện code (REFACTOR)
def calculate_discount(price, discount):
    """Tính giá sau giảm giá với validation"""
    if price < 0:
        raise ValueError("Price must be >= 0")
    if not 0 <= discount <= 1:
        raise ValueError("Discount must be between 0 and 1")
    return price * (1 - discount)


# Bước 4: Thêm test cho edge cases
def test_calculate_discount_errors():
    with pytest.raises(ValueError):
        calculate_discount(-100, 0.1)
    with pytest.raises(ValueError):
        calculate_discount(100, -0.1)
    with pytest.raises(ValueError):
        calculate_discount(100, 1.1)
```

---

### 1.5. Debug với pdb (Python Debugger)

```python
import pdb


def buggy_function(x, y):
    result = 0
    for i in range(x):
        result += i * y  # Bug: có thể bị lỗi
    return result


def debug_example():
    a = 10
    b = 0

    # Đặt breakpoint
    # pdb.set_trace()  # Cách cũ

    # Cách mới (Python 3.7+)
    breakpoint()  # Tương đương pdb.set_trace()

    result = buggy_function(a, b)
    print(f"Result: {result}")


# Các lệnh trong pdb:
# n (next)     - Chạy đến dòng tiếp theo
# s (step)     - Bước vào function
# c (continue) - Tiếp tục chạy đến breakpoint tiếp theo
# q (quit)     - Thoát debugger
# p variable   - In giá trị variable
# pp variable  - Pretty print variable
# l            - Hiển thị code xung quanh
# w            - Hiển thị stack trace
# up/down      - Di chuyển trong stack
# b line_num   - Đặt breakpoint tại dòng
# clear        - Xóa breakpoint

# Debug trong pytest:
# pytest --pdb test_file.py  # Vào pdb khi test fail


# Ví dụ debug nâng cao
def debug_with_conditional():
    data = [1, 2, 3, 4, 5]

    for item in data:
        # Chỉ dừng khi item == 3
        if item == 3:
            breakpoint()
        print(f"Processing {item}")


debug_with_conditional()
```

---

### 1.6. Logging - Theo dõi ứng dụng

```python
import logging
from logging.handlers import RotatingFileHandler


# CẤU HÌNH LOGGING
def setup_logging():
    """Cấu hình logging cho ứng dụng"""

    # Tạo logger
    logger = logging.getLogger("my_app")
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler - Rotating
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# SỬ DỤNG LOGGING
logger = setup_logging()


class UserService:
    def __init__(self):
        self.users = {}
        logger.info("UserService initialized")

    def create_user(self, user_id, name):
        """Tạo user mới"""
        logger.debug(f"Creating user: {user_id}, {name}")

        if user_id in self.users:
            logger.warning(f"User {user_id} already exists!")
            raise ValueError(f"User {user_id} already exists")

        self.users[user_id] = {"id": user_id, "name": name, "created_at": "2024-01-01"}

        logger.info(f"User {user_id} created successfully")
        return self.users[user_id]

    def get_user(self, user_id):
        """Lấy thông tin user"""
        logger.debug(f"Getting user: {user_id}")

        if user_id not in self.users:
            logger.error(f"User {user_id} not found")
            raise KeyError(f"User {user_id} not found")

        return self.users[user_id]

    def delete_user(self, user_id):
        """Xóa user"""
        logger.info(f"Deleting user: {user_id}")

        if user_id not in self.users:
            logger.error(f"User {user_id} not found for deletion")
            raise KeyError(f"User {user_id} not found")

        del self.users[user_id]
        logger.info(f"User {user_id} deleted successfully")


# Sử dụng
service = UserService()
try:
    service.create_user(1, "Alice")
    service.create_user(2, "Bob")
    service.create_user(1, "Duplicate")  # Warning
    user = service.get_user(3)  # Error
except Exception as e:
    logger.exception(f"Error occurred: {e}")
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống Test hoàn chỉnh

```python
import unittest
import json
from datetime import datetime
from typing import Dict, List, Any


# ============ CODE ĐỂ TEST ============
class Task:
    """Class đại diện cho một task"""

    def __init__(self, task_id: int, title: str, status: str = "pending"):
        self.id = task_id
        self.title = title
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def complete(self):
        """Đánh dấu task hoàn thành"""
        if self.status == "completed":
            raise ValueError("Task already completed")
        self.status = "completed"
        self.updated_at = datetime.now()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển thành dict"""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TaskManager:
    """Quản lý các task"""

    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1

    def add_task(self, title: str) -> Task:
        """Thêm task mới"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        task = Task(self.next_id, title.strip())
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """Lấy task theo ID"""
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def complete_task(self, task_id: int) -> Task:
        """Hoàn thành task"""
        task = self.get_task(task_id)
        task.complete()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Xóa task"""
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        return True

    def get_all_tasks(self) -> List[Task]:
        """Lấy tất cả tasks"""
        return list(self.tasks.values())

    def get_pending_tasks(self) -> List[Task]:
        """Lấy các task pending"""
        return [t for t in self.tasks.values() if t.status == "pending"]

    def get_completed_tasks(self) -> List[Task]:
        """Lấy các task completed"""
        return [t for t in self.tasks.values() if t.status == "completed"]


# ============ TEST CODE ============
class TestTask(unittest.TestCase):
    """Test class Task"""

    def setUp(self):
        """Setup cho mỗi test"""
        self.task = Task(1, "Test Task", "pending")

    def test_task_creation(self):
        """Test tạo task"""
        self.assertEqual(self.task.id, 1)
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.status, "pending")
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_complete(self):
        """Test hoàn thành task"""
        self.task.complete()
        self.assertEqual(self.task.status, "completed")
        self.assertNotEqual(self.task.updated_at, self.task.created_at)

    def test_task_complete_already_completed(self):
        """Test hoàn thành task đã completed"""
        self.task.complete()
        with self.assertRaises(ValueError):
            self.task.complete()

    def test_task_to_dict(self):
        """Test chuyển task thành dict"""
        task_dict = self.task.to_dict()
        self.assertEqual(task_dict["id"], 1)
        self.assertEqual(task_dict["title"], "Test Task")
        self.assertEqual(task_dict["status"], "pending")
        self.assertIn("created_at", task_dict)
        self.assertIn("updated_at", task_dict)


class TestTaskManager(unittest.TestCase):
    """Test class TaskManager"""

    def setUp(self):
        """Setup cho mỗi test"""
        self.manager = TaskManager()
        self.task1 = self.manager.add_task("Task 1")
        self.task2 = self.manager.add_task("Task 2")

    def test_add_task(self):
        """Test thêm task"""
        task = self.manager.add_task("New Task")
        self.assertEqual(task.id, 3)
        self.assertEqual(task.title, "New Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(len(self.manager.get_all_tasks()), 3)

    def test_add_task_empty_title(self):
        """Test thêm task với title rỗng"""
        with self.assertRaises(ValueError):
            self.manager.add_task("")
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_get_task(self):
        """Test lấy task"""
        task = self.manager.get_task(1)
        self.assertEqual(task.title, "Task 1")
        self.assertEqual(task.id, 1)

    def test_get_task_not_found(self):
        """Test lấy task không tồn tại"""
        with self.assertRaises(KeyError):
            self.manager.get_task(999)

    def test_complete_task(self):
        """Test hoàn thành task"""
        self.manager.complete_task(1)
        task = self.manager.get_task(1)
        self.assertEqual(task.status, "completed")

    def test_delete_task(self):
        """Test xóa task"""
        result = self.manager.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

        # Xóa task không tồn tại
        result = self.manager.delete_task(999)
        self.assertFalse(result)

    def test_get_all_tasks(self):
        """Test lấy tất cả tasks"""
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)

    def test_get_pending_tasks(self):
        """Test lấy pending tasks"""
        self.manager.complete_task(1)
        pending = self.manager.get_pending_tasks()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, 2)

    def test_get_completed_tasks(self):
        """Test lấy completed tasks"""
        self.manager.complete_task(1)
        completed = self.manager.get_completed_tasks()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].id, 1)


# ============ TEST VỚI PYTESST ============
import pytest


@pytest.fixture
def task_manager():
    """Fixture cho TaskManager"""
    manager = TaskManager()
    manager.add_task("Test 1")
    manager.add_task("Test 2")
    return manager


def test_manager_tasks_count(task_manager):
    """Test số lượng tasks"""
    assert len(task_manager.get_all_tasks()) == 2


@pytest.mark.parametrize(
    "title,expected_len",
    [
        ("New Task", 3),
        ("  Trimmed  ", 3),
        ("A" * 100, 3),
    ],
)
def test_add_task_various_titles(task_manager, title, expected_len):
    """Test thêm task với nhiều title khác nhau"""
    task_manager.add_task(title)
    assert len(task_manager.get_all_tasks()) == expected_len


@pytest.mark.parametrize(
    "invalid_title",
    [
        "",
        "   ",
        None,
    ],
)
def test_add_task_invalid_titles(task_manager, invalid_title):
    """Test thêm task với title không hợp lệ"""
    with pytest.raises(ValueError):
        task_manager.add_task(invalid_title)


class TestIntegration:
    """Test tích hợp"""

    def test_task_workflow(self, task_manager):
        """Test luồng làm việc hoàn chỉnh"""
        # Thêm task
        task = task_manager.add_task("New Task")
        assert len(task_manager.get_all_tasks()) == 3

        # Hoàn thành task
        task_manager.complete_task(task.id)
        assert task.status == "completed"

        # Kiểm tra pending/completed
        assert len(task_manager.get_pending_tasks()) == 2
        assert len(task_manager.get_completed_tasks()) == 1

        # Xóa task
        task_manager.delete_task(task.id)
        assert len(task_manager.get_all_tasks()) == 2


# Chạy test: pytest -v test_file.py
# Chạy với coverage: pytest --cov=. --cov-report=html test_file.py
```

---

### Ví dụ 2: Mocking và Testing API

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime


# ============ CODE ĐỂ TEST ============
class APIClient:
    """Client gọi API"""

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def get_user(self, user_id):
        """Lấy thông tin user"""
        try:
            response = self.session.get(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Error: {str(e)}")

    def create_user(self, user_data):
        """Tạo user mới"""
        try:
            response = self.session.post(f"{self.base_url}/users", json=user_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Error: {str(e)}")


# ============ TEST VỚI MOCKING ============
class TestAPIClient(unittest.TestCase):
    """Test APIClient với mocking"""

    def setUp(self):
        self.client = APIClient("https://api.example.com", "test-api-key")

    @patch("requests.Session.get")
    def test_get_user_success(self, mock_get):
        """Test get user thành công"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
        }
        mock_get.return_value = mock_response

        # Call function
        result = self.client.get_user(1)

        # Assert
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["email"], "alice@example.com")
        mock_get.assert_called_once_with("https://api.example.com/users/1")

    @patch("requests.Session.get")
    def test_get_user_not_found(self, mock_get):
        """Test get user không tìm thấy"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        # Call function và assert
        with self.assertRaises(Exception) as context:
            self.client.get_user(999)

        self.assertIn("API Error", str(context.exception))

    @patch("requests.Session.post")
    def test_create_user_success(self, mock_post):
        """Test create user thành công"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com",
        }
        mock_post.return_value = mock_response

        # Call function
        user_data = {"name": "Bob", "email": "bob@example.com"}
        result = self.client.create_user(user_data)

        # Assert
        self.assertEqual(result["id"], 2)
        self.assertEqual(result["name"], "Bob")
        mock_post.assert_called_once_with(
            "https://api.example.com/users", json=user_data
        )


# ============ MOCKING VỚI PATCH TRONG PYTEST ============
import pytest
from unittest.mock import patch, Mock


def test_api_with_patch():
    """Test API với patch decorator"""
    client = APIClient("https://api.example.com", "test-key")

    with patch("requests.Session.get") as mock_get:
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test User"}
        mock_get.return_value = mock_response

        # Test
        result = client.get_user(1)
        assert result["name"] == "Test User"


# ============ TEST VỚI REAL API (Integration Test) ============
import pytest
import os


@pytest.mark.integration
class TestRealAPI:
    """Integration test với real API"""

    def test_real_api(self):
        """Test với real API (cần API key)"""
        api_key = os.environ.get("TEST_API_KEY")
        if not api_key:
            pytest.skip("No API key provided")

        client = APIClient("https://jsonplaceholder.typicode.com", api_key)

        # Test get user
        user = client.get_user(1)
        assert user["id"] == 1
        assert "name" in user
        assert "email" in user

        # Test create user (mock để không thay đổi data thật)
        # Sử dụng mocks cho create user trong integration test

    def test_real_api_404(self):
        """Test với API real - 404"""
        client = APIClient("https://jsonplaceholder.typicode.com", "dummy-key")

        with pytest.raises(Exception):
            client.get_user(999999)


# Chạy integration test: pytest -m integration
```

---

### Ví dụ 3: Debugging nâng cao

```python
import pdb
import traceback
import sys
from functools import wraps


# ============ DEBUG DECORATORS ============
def debug_on_error(func):
    """Decorator: Vào debug mode khi function raise error"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(f"🔍 Debugging {func.__name__}...")
            print(f"Args: {args}")
            print(f"Kwargs: {kwargs}")
            print("-" * 40)

            # Enter debugger
            import pdb

            pdb.post_mortem(sys.exc_info()[2])
            raise

    return wrapper


def trace_calls(func):
    """Decorator: Trace function calls"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        indent = "  " * wrapper.call_depth
        print(f"{indent}➡️ Calling {func.__name__}{args[1:] if args else ''}")

        wrapper.call_depth += 1
        try:
            result = func(*args, **kwargs)
            print(f"{indent}✅ {func.__name__} -> {result}")
            return result
        except Exception as e:
            print(f"{indent}❌ {func.__name__} -> {e}")
            raise
        finally:
            wrapper.call_depth -= 1

    wrapper.call_depth = 0
    return wrapper


# ============ VÍ DỤ DEBUG ============
@debug_on_error
def complex_function(x, y):
    """Hàm phức tạp có thể lỗi"""
    result = []
    for i in range(x):
        result.append(i / y)  # Nếu y = 0 sẽ lỗi
    return result


@trace_calls
def fibonacci(n):
    """Fibonacci với trace"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@trace_calls
def factorial(n):
    """Factorial với trace"""
    if n == 0:
        return 1
    return n * factorial(n - 1)


# ============ POST-MORTEM DEBUGGING ============
def post_mortem_debug():
    """Debug sau khi có lỗi"""
    try:
        data = [1, 2, 3]
        print(data[5])  # IndexError
    except Exception:
        print("💥 An error occurred. Entering post-mortem debug...")
        import pdb

        pdb.pm()  # Post-mortem debug


# ============ INTERACTIVE DEBUGGING ============
def interactive_debug():
    """Debug tương tác"""
    x = 10
    y = 0

    # Set breakpoint
    breakpoint()  # Python 3.7+

    try:
        result = x / y
    except ZeroDivisionError:
        print("Oops! Can't divide by zero")
        # Enter debugger at error point
        import pdb

        pdb.set_trace()
        result = None

    print(f"Result: {result}")


# ============ EXCEPTION LOGGING ============
def log_exception(func):
    """Log exception chi tiết"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Exception in {func.__name__}")
            print(f"   Error: {e}")
            print(f"   Type: {type(e).__name__}")
            print("   Stack trace:")
            traceback.print_exc()
            raise

    return wrapper


# ============ SỬ DỤNG ============
# Test debug_on_error
print("=== TEST DEBUG_ON_ERROR ===")
# complex_function(5, 0)  # Comment out để test

# Test trace_calls
print("\n=== TEST TRACE CALLS ===")
print(fibonacci(5))
print(factorial(5))


# Test exception logging
@log_exception
def buggy_math(x, y):
    return x / y


# try:
#     buggy_math(10, 0)
# except:
#     pass

# ============ DEBUGGING TIPS ============
print("\n=== DEBUGGING TIPS ===")
print("""
1. pdb Commands:
   - n (next): Execute next line
   - s (step): Step into function
   - c (continue): Continue execution
   - p variable: Print variable value
   - pp variable: Pretty print variable
   - l: Show code around current line
   - w: Show stack trace
   - up/down: Move in stack
   - b line: Set breakpoint
   - clear: Clear breakpoints

2. Quick Debug:
   - print() statements (simple but effective)
   - logging module for production
   - assert statements for invariants
   - breakpoint() for interactive debugging

3. Common Issues:
   - Division by zero
   - Index out of range
   - Type errors
   - NoneType errors
   - Circular imports

4. Best Practices:
   - Write tests before fixing bugs
   - Reproduce the bug in isolation
   - Use version control (git bisect)
   - Read the error message carefully
   - Check assumptions with assert
""")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết unit tests cho hàm `is_palindrome(text)`:
- Test chuỗi đối xứng
- Test chuỗi không đối xứng
- Test chuỗi rỗng
- Test với case insensitive

**Bài 2:** Tạo class `Calculator` và viết unit tests:
- `add(a, b)`
- `subtract(a, b)`
- `multiply(a, b)`
- `divide(a, b)`
- Test edge cases: 0, negative, division by zero

**Bài 3:** Viết test cho function `get_student_grade(score)`:
- 90-100: A
- 80-89: B
- 70-79: C
- 60-69: D
- < 60: F
- Test tất cả các cases

**Bài 4:** Sử dụng pytest với fixtures để test `UserManager` class.

**Bài 5:** Sử dụng mocking để test function gọi API.

**Bài 6:** Viết test cho function xử lý file CSV.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Xây dựng test suite cho một API client với mocking.

**Bài 8:** Viết integration tests cho database operations.

**Bài 9:** Tạo decorator để log performance và debug.

**Bài 10:** Xây dựng CI/CD pipeline với test tự động.

---

## 🏗️ MINI-PROJECT: TEST SUITE COMPLETE

```python
"""
Xây dựng test suite cho ứng dụng Todo List:

1. UNIT TESTS:
   - Test Task class
   - Test TaskManager class
   - Test validators
   - Test helpers

2. INTEGRATION TESTS:
   - Test database operations
   - Test API endpoints
   - Test file I/O

3. TEST COVERAGE:
   - Đạt 90%+ coverage
   - Test tất cả branches
   - Test edge cases

4. MOCKING:
   - Mock database
   - Mock external APIs
   - Mock file system

5. CI/CD:
   - Tự động chạy test khi push
   - Báo cáo coverage
   - Notify when tests fail
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE TEST/DEBUG CHUYÊN NGHIỆP

- [ ] Mỗi function có ít nhất 1 test
- [ ] Test bao gồm cả happy path và edge cases
- [ ] Sử dụng fixtures cho setup/teardown
- [ ] Mock external dependencies
- [ ] Test names clear and descriptive
- [ ] Test độc lập (không phụ thuộc lẫn nhau)
- [ ] Có logging trong production code
- [ ] Sử dụng debugger khi cần

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo property-based testing với Hypothesis
from hypothesis import given, strategies as st


@given(st.integers())
def test_abs_property(x):
    """Test property của abs function"""
    assert abs(x) >= 0
    assert abs(x) == abs(-x)
    assert abs(x) == x if x >= 0 else -x


# Chạy 100 tests với dữ liệu ngẫu nhiên
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Công cụ | Mục đích | Cách dùng |
|---------|----------|-----------|
| **unittest** | Framework test built-in | `class Test(unittest.TestCase)` |
| **pytest** | Framework test hiện đại | Function `test_*` |
| **pdb** | Debugger interactive | `breakpoint()` |
| **logging** | Log ứng dụng | `logger.info()` |
| **mock** | Mock dependencies | `@patch` |

---

**Chúc mừng bạn đã hoàn thành toàn bộ 12 bài học! Bạn đã có nền tảng vững chắc để trở thành lập trình viên Python chuyên nghiệp.** 🎉🎉🎉

**Đây là hành trình của bạn:**
1. ✅ Biến & Kiểu dữ liệu
2. ✅ Cấu trúc điều khiển
3. ✅ Cấu trúc dữ liệu (List, Tuple, Set, Dict)
4. ✅ Hàm (Function)
5. ✅ Xử lý ngoại lệ
6. ✅ OOP - Lớp và Đối tượng
7. ✅ Kế thừa và Đa hình
8. ✅ Decorator và Closure
9. ✅ Module và Package
10. ✅ File I/O và Serialization
11. ✅ Iterator và Generator
12. ✅ Unit Test và Debug

**Bạn đã sẵn sàng cho các dự án thực tế!** 🚀