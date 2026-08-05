# 🚀 BUỔI 4: OOP PYTHON - TESTING, TYPE HINTS & ASYNC

Chào mừng đến buổi 4! Hôm nay chúng ta sẽ **chuyên nghiệp hóa** code OOP với testing, type hints và async programming.

---

## 📚 MỤC TIÊU BUỔI 4

1. Thành thạo **Testing OOP Code** với pytest
2. Nắm vững **Type Hints** và **Type Checking**
3. Hiểu sâu về **Async OOP** (async/await)
4. Xây dựng **Production-ready Application**

---

## 🧪 PHẦN 1: TESTING OOP CODE

### 1.1. Unit Testing với Pytest

```python
# test_bank.py - File test cho BankAccount
"""
# Cài đặt: pip install pytest pytest-cov

# Chạy test:
pytest test_bank.py -v
pytest --cov=. test_bank.py  # Với coverage
"""

import pytest
from datetime import datetime
from typing import Optional

class BankAccount:
    """Class cần test"""
    
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance
        self._transactions = []
        self._add_transaction("INIT", balance)
    
    def _add_transaction(self, type_: str, amount: float):
        self._transactions.append({
            'type': type_,
            'amount': amount,
            'balance': self._balance,
            'timestamp': datetime.now()
        })
    
    @property
    def balance(self) -> float:
        return self._balance
    
    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self._add_transaction("DEPOSIT", amount)
        return self._balance
    
    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._add_transaction("WITHDRAW", -amount)
        return self._balance
    
    def transfer(self, target: 'BankAccount', amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds for transfer")
        
        self.withdraw(amount)
        target.deposit(amount)
        self._add_transaction("TRANSFER_OUT", -amount)
        target._add_transaction("TRANSFER_IN", amount)
        return True
    
    def get_transactions(self) -> list:
        return self._transactions.copy()
    
    def __str__(self):
        return f"BankAccount(owner='{self.owner}', balance={self._balance})"


# ========== TESTS ==========

class TestBankAccount:
    """Test suite cho BankAccount"""
    
    def test_initial_balance(self):
        """Test khởi tạo với balance"""
        acc = BankAccount("John", 1000)
        assert acc.balance == 1000
        assert acc.owner == "John"
    
    def test_initial_balance_default(self):
        """Test khởi tạo không có balance"""
        acc = BankAccount("John")
        assert acc.balance == 0.0
    
    def test_deposit(self):
        """Test deposit"""
        acc = BankAccount("John", 1000)
        acc.deposit(500)
        assert acc.balance == 1500
    
    def test_deposit_negative(self):
        """Test deposit với số âm -> raise error"""
        acc = BankAccount("John")
        with pytest.raises(ValueError, match="positive"):
            acc.deposit(-100)
    
    def test_withdraw(self):
        """Test withdraw"""
        acc = BankAccount("John", 1000)
        acc.withdraw(300)
        assert acc.balance == 700
    
    def test_withdraw_insufficient(self):
        """Test withdraw vượt quá balance"""
        acc = BankAccount("John", 100)
        with pytest.raises(ValueError, match="Insufficient"):
            acc.withdraw(200)
    
    def test_transfer(self):
        """Test transfer giữa 2 accounts"""
        acc1 = BankAccount("John", 1000)
        acc2 = BankAccount("Jane", 500)
        
        assert acc1.transfer(acc2, 300) is True
        assert acc1.balance == 700
        assert acc2.balance == 800
    
    def test_transfer_insufficient(self):
        """Test transfer khi không đủ tiền"""
        acc1 = BankAccount("John", 100)
        acc2 = BankAccount("Jane", 500)
        
        with pytest.raises(ValueError, match="Insufficient"):
            acc1.transfer(acc2, 200)
    
    def test_transaction_history(self):
        """Test transaction history"""
        acc = BankAccount("John", 1000)
        acc.deposit(500)
        acc.withdraw(200)
        
        transactions = acc.get_transactions()
        assert len(transactions) == 3
        assert transactions[0]['type'] == "INIT"
        assert transactions[1]['type'] == "DEPOSIT"
        assert transactions[2]['type'] == "WITHDRAW"
        assert transactions[1]['balance'] == 1500

# Fixtures - Setup/Teardown
@pytest.fixture
def account():
    """Tạo account mới cho mỗi test"""
    return BankAccount("Test User", 1000)

@pytest.fixture
def two_accounts():
    """Tạo 2 accounts cho test transfer"""
    acc1 = BankAccount("User1", 1000)
    acc2 = BankAccount("User2", 500)
    return acc1, acc2

class TestBankAccountWithFixtures:
    """Test sử dụng fixtures"""
    
    def test_with_fixture(self, account):
        assert account.balance == 1000
        account.deposit(100)
        assert account.balance == 1100
    
    def test_transfer_fixture(self, two_accounts):
        acc1, acc2 = two_accounts
        acc1.transfer(acc2, 200)
        assert acc1.balance == 800
        assert acc2.balance == 700

# Parameterized tests
@pytest.mark.parametrize("initial,deposit_amount,expected", [
    (0, 100, 100),
    (100, 50, 150),
    (500, 200, 700),
    (1000, 0.5, 1000.5),
])
def test_deposit_param(initial, deposit_amount, expected):
    """Test deposit với nhiều input"""
    acc = BankAccount("Test", initial)
    acc.deposit(deposit_amount)
    assert acc.balance == expected

# Mocking
class TestBankAccountWithMock:
    """Test với mock objects"""
    
    def test_transfer_mock(self, mocker):
        """Mock deposit method của target account"""
        acc1 = BankAccount("John", 1000)
        acc2 = BankAccount("Jane", 500)
        
        # Mock deposit để kiểm tra được gọi
        mock_deposit = mocker.patch.object(acc2, 'deposit')
        mock_deposit.return_value = 800
        
        acc1.transfer(acc2, 300)
        
        # Verify deposit được gọi với amount đúng
        mock_deposit.assert_called_once_with(300)
```

### 1.2. Test Double và Mocking

```python
print("\n=== MOCKING IN TESTS ===")

from unittest.mock import Mock, patch, MagicMock
import requests

class PaymentService:
    """Service gọi API bên ngoài"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.payment.com"
    
    def process_payment(self, amount: float, card_number: str) -> dict:
        """Gọi API thanh toán"""
        response = requests.post(
            f"{self.base_url}/pay",
            json={
                'amount': amount,
                'card': card_number,
                'api_key': self.api_key
            }
        )
        response.raise_for_status()
        return response.json()
    
    def refund(self, transaction_id: str) -> dict:
        """Gọi API hoàn tiền"""
        response = requests.post(
            f"{self.base_url}/refund",
            json={
                'transaction_id': transaction_id,
                'api_key': self.api_key
            }
        )
        response.raise_for_status()
        return response.json()

class PaymentProcessor:
    """Xử lý thanh toán sử dụng PaymentService"""
    
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service
        self.transactions = []
    
    def pay(self, amount: float, card: str) -> bool:
        try:
            result = self.payment_service.process_payment(amount, card)
            self.transactions.append({
                'amount': amount,
                'card': card,
                'status': 'success',
                'id': result.get('id')
            })
            return True
        except Exception as e:
            self.transactions.append({
                'amount': amount,
                'card': card,
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def get_transactions(self):
        return self.transactions.copy()

# ========== TESTS ==========

class TestPaymentProcessor:
    """Test với mocks"""
    
    def test_pay_success(self):
        """Test payment thành công với mock"""
        # Tạo mock service
        mock_service = Mock(spec=PaymentService)
        mock_service.process_payment.return_value = {
            'id': 'txn_123',
            'status': 'success'
        }
        
        processor = PaymentProcessor(mock_service)
        result = processor.pay(100.50, "4111-1111-1111-1111")
        
        assert result is True
        assert len(processor.transactions) == 1
        assert processor.transactions[0]['status'] == 'success'
        mock_service.process_payment.assert_called_once_with(
            100.50, "4111-1111-1111-1111"
        )
    
    def test_pay_failure(self):
        """Test payment thất bại"""
        mock_service = Mock(spec=PaymentService)
        mock_service.process_payment.side_effect = Exception("Payment declined")
        
        processor = PaymentProcessor(mock_service)
        result = processor.pay(100, "invalid")
        
        assert result is False
        assert processor.transactions[0]['status'] == 'failed'
        assert 'Payment declined' in processor.transactions[0]['error']
    
    def test_pay_with_patch(self):
        """Test với patch decorator"""
        with patch('builtins.requests') as mock_requests:
            # Giả lập response
            mock_response = Mock()
            mock_response.json.return_value = {'id': 'txn_123'}
            mock_response.raise_for_status.return_value = None
            mock_requests.post.return_value = mock_response
            
            service = PaymentService("test_key")
            result = service.process_payment(100, "4111")
            
            assert result == {'id': 'txn_123'}
            mock_requests.post.assert_called_once()
    
    def test_refund(self):
        """Test refund với mock"""
        mock_service = Mock(spec=PaymentService)
        mock_service.refund.return_value = {'status': 'refunded'}
        
        processor = PaymentProcessor(mock_service)
        # Thêm transaction thành công
        processor.transactions.append({
            'id': 'txn_123',
            'status': 'success'
        })
        
        # Test refund
        result = mock_service.refund('txn_123')
        assert result == {'status': 'refunded'}
        mock_service.refund.assert_called_once_with('txn_123')
```

### 1.3. Integration Tests

```python
print("\n=== INTEGRATION TESTS ===")

import pytest
import sqlite3
from contextlib import contextmanager

class UserRepository:
    """Repository với database"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER
                )
            """)
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create(self, name: str, email: str, age: int) -> dict:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            return self.get_by_id(user_id)
    
    def get_by_id(self, user_id: int) -> dict:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def get_all(self) -> list:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [dict(row) for row in rows]
    
    def update(self, user_id: int, **kwargs) -> dict:
        with self._get_connection() as conn:
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['name', 'email', 'age']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return self.get_by_id(user_id)
            
            values.append(user_id)
            conn.execute(
                f"UPDATE users SET {', '.join(fields)} WHERE id = ?",
                values
            )
            conn.commit()
            return self.get_by_id(user_id)
    
    def delete(self, user_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0


class TestUserRepository:
    """Integration tests với database thật"""
    
    @pytest.fixture
    def repo(self):
        """Tạo repository với database in-memory cho mỗi test"""
        return UserRepository(":memory:")
    
    def test_create_user(self, repo):
        user = repo.create("John Doe", "john@example.com", 30)
        assert user['id'] is not None
        assert user['name'] == "John Doe"
        assert user['email'] == "john@example.com"
        assert user['age'] == 30
    
    def test_get_user(self, repo):
        created = repo.create("Jane", "jane@example.com", 25)
        retrieved = repo.get_by_id(created['id'])
        assert retrieved == created
    
    def test_get_all(self, repo):
        repo.create("User1", "u1@example.com", 20)
        repo.create("User2", "u2@example.com", 30)
        repo.create("User3", "u3@example.com", 40)
        
        users = repo.get_all()
        assert len(users) == 3
    
    def test_update_user(self, repo):
        user = repo.create("Old Name", "old@example.com", 20)
        
        updated = repo.update(
            user['id'],
            name="New Name",
            age=25
        )
        
        assert updated['name'] == "New Name"
        assert updated['age'] == 25
        assert updated['email'] == "old@example.com"  # Không đổi
    
    def test_delete_user(self, repo):
        user = repo.create("To Delete", "delete@example.com", 30)
        assert repo.delete(user['id']) is True
        
        deleted = repo.get_by_id(user['id'])
        assert deleted is None
    
    def test_unique_email_constraint(self, repo):
        repo.create("User1", "same@email.com", 20)
        
        with pytest.raises(sqlite3.IntegrityError):
            repo.create("User2", "same@email.com", 25)
```

---

## 📝 PHẦN 2: TYPE HINTS

### 2.1. Type Hints Cơ Bản

```python
print("\n=== TYPE HINTS ===")

from typing import List, Dict, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from typing import NewType, TypeVar, Generic

# Các type hints cơ bản
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add_numbers(a: int, b: int) -> int:
    return a + b

def process_items(items: List[str]) -> List[int]:
    return [len(item) for item in items]

def get_user_data(user_id: int) -> Dict[str, Union[str, int]]:
    return {
        'id': user_id,
        'name': 'John',
        'age': 30
    }

def divide(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return a / b

def combine(a: Union[int, str], b: Union[int, str]) -> str:
    return f"{a}{b}"

# Type aliases
UserId = int
UserName = str
UserData = Tuple[UserId, UserName, int]

def get_user_info(user_id: UserId) -> UserData:
    return (user_id, "John Doe", 30)

# NewType - tạo type mới
UserIdType = NewType('UserIdType', int)
EmailAddress = NewType('EmailAddress', str)

def get_user(user_id: UserIdType) -> dict:
    return {'id': user_id}

# Generic Types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    """Generic Stack class"""
    
    def __init__(self):
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> Optional[T]:
        if self._items:
            return self._items.pop()
        return None
    
    def peek(self) -> Optional[T]:
        if self._items:
            return self._items[-1]
        return None
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)

# Demo
print("--- Type Hints Demo ---")
print(greet("World"))
print(add_numbers(10, 20))
print(process_items(["a", "bc", "def"]))

stack = Stack[int]()
stack.push(1)
stack.push(2)
stack.push(3)
print(f"Pop: {stack.pop()}")
print(f"Peek: {stack.peek()}")

stack_str = Stack[str]()
stack_str.push("hello")
stack_str.push("world")
print(f"Pop: {stack_str.pop()}")
```

### 2.2. Advanced Type Hints

```python
print("\n=== ADVANCED TYPE HINTS ===")

from typing import Protocol, TypeVar, overload, Literal, Final, Any
from typing import Optional, Callable, Iterator, Generator, AsyncIterator
from functools import wraps

# Protocol - Structural Subtyping
class Drawable(Protocol):
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "Drawing Circle"

class Square:
    def draw(self) -> str:
        return "Drawing Square"

class Rectangle:
    def draw(self) -> str:
        return "Drawing Rectangle"

def render(shape: Drawable) -> None:
    """Hàm này nhận bất kỳ object nào có method draw()"""
    print(shape.draw())

# Overload - Function overloading với type hints
@overload
def process(value: int) -> int:
    ...

@overload
def process(value: str) -> str:
    ...

@overload
def process(value: list) -> list:
    ...

def process(value):
    if isinstance(value, int):
        return value * 2
    elif isinstance(value, str):
        return value.upper()
    elif isinstance(value, list):
        return [process(v) for v in value]
    return value

# Literal - Cụ thể giá trị
from typing import Literal

def set_status(status: Literal['active', 'inactive', 'pending']) -> str:
    return f"Status set to {status}"

# Final - Không thể override
from typing import final

@final
class FinalClass:
    """Class này không thể được kế thừa"""
    def method(self) -> str:
        return "Method"

# Generator
def fibonacci(limit: int) -> Generator[int, None, None]:
    """Generator với type hints"""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

# Async Generator
import asyncio
from typing import AsyncGenerator

async def async_counter(limit: int) -> AsyncGenerator[int, None]:
    for i in range(limit):
        await asyncio.sleep(0.1)
        yield i

# Self - Class method trả về instance của chính nó
from typing import Self

class Builder:
    def __init__(self, value: int = 0):
        self.value = value
    
    def add(self, amount: int) -> Self:
        self.value += amount
        return self
    
    def multiply(self, factor: int) -> Self:
        self.value *= factor
        return self
    
    def build(self) -> int:
        return self.value

# TypedDict
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: Optional[int]

def create_user(data: UserDict) -> None:
    print(f"Creating user: {data['name']}")

# Demo
print("--- Protocol ---")
render(Circle())
render(Square())
render(Rectangle())

print("\n--- Overload ---")
print(f"process(5): {process(5)}")
print(f"process('hello'): {process('hello')}")
print(f"process([1, 'a', 3]): {process([1, 'a', 3])}")

print("\n--- Literal ---")
print(set_status('active'))
# print(set_status('invalid'))  # Type error

print("\n--- Generator ---")
fib = fibonacci(10)
print(f"Fibonacci: {list(fib)}")

print("\n--- Builder with Self ---")
result = Builder(5).add(3).multiply(2).build()
print(f"Builder result: {result}")
```

### 2.3. Type Checking với MyPy

```python
# file: user_service.py
from typing import Optional, List, Dict
from dataclasses import dataclass
import re

@dataclass
class User:
    """User model với type hints"""
    id: int
    name: str
    email: str
    age: int
    
    def __post_init__(self):
        """Validate sau khi khởi tạo"""
        if self.age < 0:
            raise ValueError("Age must be positive")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValueError("Invalid email")

class UserService:
    """User service với type hints đầy đủ"""
    
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id: int = 1
    
    def create_user(self, name: str, email: str, age: int) -> User:
        """Tạo user mới"""
        user = User(self._next_id, name, email, age)
        self._users[user.id] = user
        self._next_id += 1
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Lấy user theo id"""
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Lấy tất cả users"""
        return list(self._users.values())
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Cập nhật user"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Xóa user"""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def search_by_name(self, name: str) -> List[User]:
        """Tìm user theo tên"""
        return [u for u in self._users.values() if name.lower() in u.name.lower()]

# Type checking với mypy:
# mypy user_service.py
# mypy --strict user_service.py
```

---

## ⚡ PHẦN 3: ASYNC OOP

### 3.1. Async Methods và Class

```python
print("\n=== ASYNC OOP ===")

import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime

class AsyncHTTPClient:
    """HTTP Client với async methods"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._session:
            await self._session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Generic request method"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with self._session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """GET request"""
        return await self._request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict = None) -> Dict:
        """POST request"""
        return await self._request('POST', endpoint, json=data)
    
    async def put(self, endpoint: str, data: Dict = None) -> Dict:
        """PUT request"""
        return await self._request('PUT', endpoint, json=data)
    
    async def delete(self, endpoint: str) -> Dict:
        """DELETE request"""
        return await self._request('DELETE', endpoint)

class AsyncFileProcessor:
    """Xử lý file với async"""
    
    def __init__(self):
        self._buffer = []
    
    async def read_file(self, filepath: str) -> str:
        """Đọc file async"""
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
            return content
    
    async def write_file(self, filepath: str, content: str) -> None:
        """Ghi file async"""
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(content)
    
    async def process_large_file(self, filepath: str, chunk_size: int = 1024) -> int:
        """Xử lý file lớn theo chunks"""
        lines_processed = 0
        async with aiofiles.open(filepath, 'r') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                # Xử lý chunk
                lines_processed += chunk.count('\n')
                await asyncio.sleep(0)  # Yield control
        return lines_processed
    
    async def batch_process(self, files: List[str]) -> Dict[str, int]:
        """Xử lý nhiều files đồng thời"""
        tasks = [self.process_large_file(f) for f in files]
        results = await asyncio.gather(*tasks)
        return dict(zip(files, results))

# Async Class với Internal State
class AsyncQueueProcessor:
    """Xử lý queue với async"""
    
    def __init__(self, max_size: int = 10):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._is_running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start processing"""
        if self._is_running:
            return
        
        self._is_running = True
        self._tasks.append(asyncio.create_task(self._consumer()))
        print("Queue processor started")
    
    async def stop(self):
        """Stop processing"""
        self._is_running = False
        
        # Chờ consumer hoàn thành
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        print("Queue processor stopped")
    
    async def add(self, item: Any):
        """Thêm item vào queue"""
        await self._queue.put(item)
        print(f"Added item: {item}")
    
    async def _consumer(self):
        """Consumer - xử lý items từ queue"""
        while self._is_running:
            try:
                # Timeout để check _is_running
                item = await asyncio.wait_for(self._queue.get(), timeout=0.5)
                
                # Process item
                print(f"Processing: {item}")
                await asyncio.sleep(0.5)  # Giả lập xử lý
                
                self._queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing item: {e}")
    
    @property
    def size(self) -> int:
        return self._queue.qsize()
    
    @property
    def is_running(self) -> bool:
        return self._is_running

# Async Context Manager cho Database
class AsyncDatabase:
    """Async database connection"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None
    
    async def __aenter__(self):
        print(f"Connecting to {self.connection_string}")
        await asyncio.sleep(0.5)  # Giả lập kết nối
        self._connection = f"Connection to {self.connection_string}"
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing connection to {self.connection_string}")
        await asyncio.sleep(0.3)
        self._connection = None
    
    async def query(self, sql: str) -> List[Dict]:
        """Execute query"""
        if not self._connection:
            raise RuntimeError("No connection")
        print(f"Executing: {sql}")
        await asyncio.sleep(0.2)  # Giả lập query
        return [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]

# Demo
async def main():
    print("=== Async OOP Demo ===")
    
    # HTTP Client
    print("\n--- Async HTTP Client ---")
    # async with AsyncHTTPClient("https://jsonplaceholder.typicode.com") as client:
    #     posts = await client.get("/posts/1")
    #     print(f"Post: {posts}")
    
    # File Processor
    print("\n--- Async File Processor ---")
    processor = AsyncFileProcessor()
    # await processor.write_file("test_async.txt", "Hello Async World!")
    # content = await processor.read_file("test_async.txt")
    # print(f"File content: {content}")
    
    # Queue Processor
    print("\n--- Async Queue Processor ---")
    queue = AsyncQueueProcessor()
    await queue.start()
    
    for i in range(5):
        await queue.add(f"Item {i}")
    
    await asyncio.sleep(3)
    await queue.stop()
    
    # Async Database
    print("\n--- Async Database ---")
    async with AsyncDatabase("postgresql://localhost/test") as db:
        results = await db.query("SELECT * FROM users")
        print(f"Query results: {results}")

# Chạy async main
if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2. Async Mixins và Patterns

```python
print("\n=== ASYNC MIXINS ===")

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
import time

class AsyncTimerMixin:
    """Mixin để đo thời gian async operations"""
    
    async def time_async(self, coro, *args, **kwargs):
        """Đo thời gian thực thi async function"""
        start = time.perf_counter()
        result = await coro(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"⏱️ {coro.__name__} took {elapsed:.4f}s")
        return result

class AsyncRetryMixin:
    """Mixin retry cho async operations"""
    
    async def retry_async(self, coro, *args, max_retries=3, delay=1, **kwargs):
        """Retry async operation khi thất bại"""
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                last_error = e
                print(f"Retry {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(delay * attempt)
        
        raise last_error

class AsyncCacheMixin:
    """Mixin cache cho async operations"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}
        self._ttl: int = 60
    
    async def cached_async(self, coro, *args, ttl: Optional[int] = None, **kwargs):
        """Execute async với cache"""
        cache_key = f"{coro.__name__}:{args}:{tuple(kwargs.items())}"
        
        # Check cache
        if cache_key in self._cache:
            if ttl is None:
                ttl = self._ttl
            
            if time.time() - self._cache_time.get(cache_key, 0) < ttl:
                print(f"📦 Cache hit for {coro.__name__}")
                return self._cache[cache_key]
        
        # Execute
        result = await coro(*args, **kwargs)
        self._cache[cache_key] = result
        self._cache_time[cache_key] = time.time()
        print(f"📦 Cache miss for {coro.__name__}")
        return result
    
    def clear_cache(self):
        """Clear cache"""
        self._cache.clear()
        self._cache_time.clear()
        print("🗑️ Cache cleared")

class AsyncLoggerMixin:
    """Mixin logging cho async operations"""
    
    async def log_async(self, message: str, level: str = "INFO"):
        """Async logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    async def info(self, message: str):
        await self.log_async(message, "INFO")
    
    async def error(self, message: str):
        await self.log_async(message, "ERROR")

# Async Service sử dụng Mixins
class AsyncDataService(
    AsyncTimerMixin,
    AsyncRetryMixin,
    AsyncCacheMixin,
    AsyncLoggerMixin
):
    """Data service với các mixins"""
    
    def __init__(self):
        AsyncCacheMixin.__init__(self)
        self._request_count = 0
    
    async def fetch_data(self, user_id: int) -> Dict:
        """Fetch data - giả lập API call"""
        await self.info(f"Fetching data for user {user_id}")
        self._request_count += 1
        
        # Giả lập API call
        await asyncio.sleep(0.5)
        
        if user_id == 999:
            raise ValueError("User not found")
        
        return {
            'user_id': user_id,
            'name': f"User {user_id}",
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_user_data(self, user_id: int) -> Dict:
        """Get user data với cache và retry"""
        # Dùng cached_async (có retry và timer bên ngoài)
        result = await self.cached_async(
            self.retry_async,
            self.fetch_data,
            user_id,
            max_retries=3,
            delay=0.5
        )
        return result
    
    async def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'request_count': self._request_count,
            'cache_size': len(self._cache)
        }

# Demo
async def async_mixin_demo():
    print("=== Async Mixins Demo ===")
    
    service = AsyncDataService()
    
    # Lần 1 - cache miss
    print("\n--- First request ---")
    data = await service.time_async(service.get_user_data, 1)
    print(f"Data: {data}")
    
    # Lần 2 - cache hit
    print("\n--- Second request ---")
    data = await service.get_user_data(1)
    print(f"Data: {data}")
    
    # Lần 3 - user khác
    print("\n--- Different user ---")
    data = await service.get_user_data(2)
    print(f"Data: {data}")
    
    # Test retry với user không tồn tại
    print("\n--- Retry with invalid user ---")
    try:
        data = await service.get_user_data(999)
        print(f"Data: {data}")
    except Exception as e:
        print(f"Failed: {e}")
    
    # Stats
    print("\n--- Stats ---")
    stats = await service.get_stats()
    print(f"Stats: {stats}")
    
    # Clear cache
    print("\n--- Clear cache ---")
    service.clear_cache()

if __name__ == "__main__":
    asyncio.run(async_mixin_demo())
```

---

## 🏗️ PHẦN 4: PRODUCTION APP - BOOK STORE API

```python
print("\n=== PRODUCTION APP: BOOK STORE ===")

import asyncio
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# ============ MODELS ============

@dataclass
class Book:
    """Book model"""
    id: str
    title: str
    author: str
    isbn: str
    price: float
    stock: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        return cls(
            id=data['id'],
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            price=data['price'],
            stock=data['stock'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

@dataclass
class Order:
    """Order model"""
    id: str
    user_id: str
    books: List[Dict]  # List of {book_id, quantity, price}
    total: float
    status: str  # pending, paid, shipped, delivered
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'books': self.books,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# ============ REPOSITORY ============

class BookRepository:
    """Repository for Book operations"""
    
    def __init__(self):
        self._books: Dict[str, Book] = {}
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test data"""
        sample_books = [
            Book(str(uuid.uuid4()), "Clean Code", "Robert Martin", "978-0132350884", 35.99, 10),
            Book(str(uuid.uuid4()), "Python Crash Course", "Eric Matthes", "978-1593279288", 29.99, 15),
            Book(str(uuid.uuid4()), "The Pragmatic Programmer", "Andrew Hunt", "978-0201616224", 40.50, 8),
        ]
        for book in sample_books:
            self._books[book.id] = book
    
    def get_all(self) -> List[Book]:
        return list(self._books.values())
    
    def get_by_id(self, book_id: str) -> Optional[Book]:
        return self._books.get(book_id)
    
    def search(self, query: str) -> List[Book]:
        query = query.lower()
        results = [
            book for book in self._books.values()
            if query in book.title.lower() 
            or query in book.author.lower()
            or query in book.isbn.lower()
        ]
        return results
    
    def create(self, book: Book) -> Book:
        self._books[book.id] = book
        return book
    
    def update(self, book: Book) -> Optional[Book]:
        if book.id not in self._books:
            return None
        book.updated_at = datetime.now()
        self._books[book.id] = book
        return book
    
    def delete(self, book_id: str) -> bool:
        if book_id in self._books:
            del self._books[book_id]
            return True
        return False
    
    def update_stock(self, book_id: str, quantity: int) -> bool:
        book = self.get_by_id(book_id)
        if not book:
            return False
        if book.stock < quantity:
            return False
        book.stock -= quantity
        book.updated_at = datetime.now()
        return True

# ============ SERVICE ============

class BookService:
    """Business logic cho Book Store"""
    
    def __init__(self, book_repo: BookRepository):
        self._book_repo = book_repo
        self._orders: Dict[str, Order] = {}
    
    def get_books(self) -> List[Dict]:
        """Lấy tất cả books"""
        return [book.to_dict() for book in self._book_repo.get_all()]
    
    def get_book(self, book_id: str) -> Optional[Dict]:
        """Lấy book theo id"""
        book = self._book_repo.get_by_id(book_id)
        return book.to_dict() if book else None
    
    def search_books(self, query: str) -> List[Dict]:
        """Tìm kiếm books"""
        return [book.to_dict() for book in self._book_repo.search(query)]
    
    def add_book(self, title: str, author: str, isbn: str, price: float, stock: int) -> Dict:
        """Thêm book mới"""
        book = Book(
            id=str(uuid.uuid4()),
            title=title,
            author=author,
            isbn=isbn,
            price=price,
            stock=stock
        )
        return self._book_repo.create(book).to_dict()
    
    def update_book(self, book_id: str, **kwargs) -> Optional[Dict]:
        """Cập nhật book"""
        book = self._book_repo.get_by_id(book_id)
        if not book:
            return None
        
        for key, value in kwargs.items():
            if hasattr(book, key) and key not in ['id', 'created_at']:
                setattr(book, key, value)
        
        updated = self._book_repo.update(book)
        return updated.to_dict() if updated else None
    
    def delete_book(self, book_id: str) -> bool:
        """Xóa book"""
        return self._book_repo.delete(book_id)
    
    def create_order(self, user_id: str, items: List[Dict]) -> Optional[Dict]:
        """Tạo đơn hàng"""
        # Validate items và tính tổng
        total = 0
        validated_items = []
        
        for item in items:
            book = self._book_repo.get_by_id(item['book_id'])
            if not book:
                raise ValueError(f"Book {item['book_id']} not found")
            
            quantity = item.get('quantity', 1)
            if quantity <= 0:
                raise ValueError(f"Invalid quantity for book {book.id}")
            
            if book.stock < quantity:
                raise ValueError(f"Insufficient stock for book {book.title}")
            
            validated_items.append({
                'book_id': book.id,
                'title': book.title,
                'quantity': quantity,
                'price': book.price,
                'subtotal': book.price * quantity
            })
            total += book.price * quantity
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            books=validated_items,
            total=total,
            status='pending'
        )
        
        # Update stock
        for item in validated_items:
            self._book_repo.update_stock(item['book_id'], item['quantity'])
        
        # Save order
        self._orders[order.id] = order
        
        return order.to_dict()
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Lấy order theo id"""
        order = self._orders.get(order_id)
        return order.to_dict() if order else None
    
    def update_order_status(self, order_id: str, status: str) -> Optional[Dict]:
        """Cập nhật trạng thái order"""
        order = self._orders.get(order_id)
        if not order:
            return None
        
        valid_statuses = ['pending', 'paid', 'shipped', 'delivered']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
        
        order.status = status
        order.updated_at = datetime.now()
        return order.to_dict()

# ============ API HANDLER ============

class BookStoreAPI:
    """REST API Handler cho Book Store"""
    
    def __init__(self, service: BookService):
        self._service = service
    
    async def handle_request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Handle HTTP request"""
        try:
            if method == 'GET' and path == '/books':
                return {'success': True, 'data': self._service.get_books()}
            
            elif method == 'GET' and path.startswith('/books/'):
                book_id = path.split('/')[-1]
                book = self._service.get_book(book_id)
                if book:
                    return {'success': True, 'data': book}
                return {'success': False, 'error': 'Book not found'}, 404
            
            elif method == 'GET' and path.startswith('/search/'):
                query = path.split('/')[-1]
                return {'success': True, 'data': self._service.search_books(query)}
            
            elif method == 'POST' and path == '/books':
                if not data:
                    raise ValueError('Data required')
                book = self._service.add_book(
                    title=data['title'],
                    author=data['author'],
                    isbn=data['isbn'],
                    price=data['price'],
                    stock=data['stock']
                )
                return {'success': True, 'data': book}, 201
            
            elif method == 'PUT' and path.startswith('/books/'):
                book_id = path.split('/')[-1]
                if not data:
                    raise ValueError('Data required')
                book = self._service.update_book(book_id, **data)
                if book:
                    return {'success': True, 'data': book}
                return {'success': False, 'error': 'Book not found'}, 404
            
            elif method == 'DELETE' and path.startswith('/books/'):
                book_id = path.split('/')[-1]
                if self._service.delete_book(book_id):
                    return {'success': True, 'message': 'Book deleted'}
                return {'success': False, 'error': 'Book not found'}, 404
            
            elif method == 'POST' and path == '/orders':
                if not data:
                    raise ValueError('Data required')
                order = self._service.create_order(
                    user_id=data['user_id'],
                    items=data['items']
                )
                return {'success': True, 'data': order}, 201
            
            elif method == 'GET' and path.startswith('/orders/'):
                order_id = path.split('/')[-1]
                order = self._service.get_order(order_id)
                if order:
                    return {'success': True, 'data': order}
                return {'success': False, 'error': 'Order not found'}, 404
            
            elif method == 'PUT' and path.startswith('/orders/'):
                order_id = path.split('/')[-1]
                if not data or 'status' not in data:
                    raise ValueError('Status required')
                order = self._service.update_order_status(order_id, data['status'])
                if order:
                    return {'success': True, 'data': order}
                return {'success': False, 'error': 'Order not found'}, 404
            
            else:
                return {'success': False, 'error': 'Invalid endpoint'}, 404
                
        except Exception as e:
            return {'success': False, 'error': str(e)}, 400

# ============ DEMO ============

async def demo_book_store():
    print("=== Book Store API Demo ===\n")
    
    # Setup
    repo = BookRepository()
    service = BookService(repo)
    api = BookStoreAPI(service)
    
    # 1. Get all books
    print("📚 All books:")
    result = await api.handle_request('GET', '/books')
    for book in result['data'][:3]:
        print(f"  {book['title']} by {book['author']} - ${book['price']}")
    
    # 2. Search
    print("\n🔍 Search for 'Python':")
    result = await api.handle_request('GET', '/search/Python')
    for book in result['data']:
        print(f"  {book['title']}")
    
    # 3. Get book by id
    book_id = repo.get_all()[0].id
    print(f"\n📖 Get book {book_id}:")
    result = await api.handle_request('GET', f'/books/{book_id}')
    print(f"  {result['data']['title']}")
    
    # 4. Add new book
    print("\n➕ Add new book:")
    result = await api.handle_request('POST', '/books', {
        'title': 'Fluent Python',
        'author': 'Luciano Ramalho',
        'isbn': '978-1491946008',
        'price': 49.99,
        'stock': 20
    })
    print(f"  Added: {result['data']['title']}")
    
    # 5. Create order
    print("\n🛒 Create order:")
    result = await api.handle_request('POST', '/orders', {
        'user_id': 'user123',
        'items': [
            {'book_id': book_id, 'quantity': 2}
        ]
    })
    if result['success']:
        order = result['data']
        print(f"  Order created: {order['id']}")
        print(f"  Total: ${order['total']:.2f}")
        print(f"  Status: {order['status']}")
    
    # 6. Update order status
    if result['success']:
        print("\n📦 Update order status:")
        result = await api.handle_request('PUT', f'/orders/{order["id"]}', {
            'status': 'paid'
        })
        print(f"  Status updated: {result['data']['status']}")
    
    # 7. Check stock after order
    print("\n📊 Stock after order:")
    result = await api.handle_request('GET', f'/books/{book_id}')
    print(f"  Book {result['data']['title']} stock: {result['data']['stock']}")

# Run demo
if __name__ == "__main__":
    asyncio.run(demo_book_store())
```

---

## 🎯 BÀI TẬP VỀ NHÀ BUỔI 4

### Bài 1: Test Framework
Xây dựng test framework cho ứng dụng của bạn:
- Unit tests với pytest
- Mock external services
- Test coverage > 80%
- Integration tests với database

### Bài 2: Type Hints Refactor
Refactor dự án cũ với type hints:
- Thêm type hints cho tất cả functions
- Sử dụng Protocols và Generics
- Validate với mypy

### Bài 3: Async API
Xây dựng async REST API:
- Async CRUD operations
- Async database connection
- Request/Response models với Pydantic
- Async middleware

---

## 📌 TỔNG KẾT BUỔI 4

**Bạn đã học được:**
1. ✅ **Testing OOP** với pytest, fixtures, mocks
2. ✅ **Type Hints** từ cơ bản đến nâng cao
3. ✅ **Async OOP** với async/await, mixins
4. ✅ **Production App** với clean architecture

**Key Takeaways:**
- **Testing** là essential - viết test trước (TDD)
- **Type Hints** giúp code self-documenting và safe
- **Async** cho hiệu năng I/O bound operations
- **Clean Architecture** tách biệt concerns

---

**Bạn đã hoàn thành 4 buổi OOP Deep Dive! 🎉**

Bây giờ bạn đã có đủ kiến thức để:
- 🏗️ Thiết kế hệ thống OOP chuyên nghiệp
- 🧪 Viết tests và đảm bảo quality
- 📝 Sử dụng type hints cho code robust
- ⚡ Xây dựng async applications

**Chúc mừng! Bạn đã trở thành Python OOP Developer! 💪🐍**