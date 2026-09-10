Chào bạn! Với vai trò là một lập trình viên Python, tôi sẽ hướng dẫn bạn xây dựng một dự án chuẩn theo **Domain-Driven Design (DDD)** và đóng gói nó bằng **uv** — công cụ quản lý dự án Python cực kỳ nhanh và hiện đại.

---

## 1. Cơ cấu thư mục chuẩn DDD (Clean Architecture / Hexagonal)

Nòng cốt của DDD là chia rẽ rõ ràng giữa **Nghiệp vụ cốt lõi (Domain)** và **Kỹ thuật/Hạ tầng (Infrastructure)**.

```text
my_ddd_lib/
├── pyproject.toml               # Cấu hình dự án & đóng gói
├── README.md
├── src/
│   └── my_ddd_lib/              # Package chính
│       ├── __init__.py
│       ├── domain/              # Cốt lõi nghiệp vụ (Không phụ thuộc thư viện ngoài)
│       │   ├── __init__.py
│       │   ├── models.py        # Entities, Value Objects, Aggregates
│       │   ├── exceptions.py    # Domain Errors
│       │   └── repositories.py  # Interfaces (Abstract Classes)
│       ├── application/         # Use Cases / Application Services
│       │   ├── __init__.py
│       │   └── services.py
│       └── infrastructure/     # Triển khai kỹ thuật (DB, API, Storage...)
│           ├── __init__.py
│           └── repositories.py  # Concrete Implementations
└── tests/
    ├── __init__.py
    ├── test_domain.py
    └── test_application.py

```

---

## 2. Khởi tạo dự án với `uv`

Mở terminal và thực hiện các bước sau:

```bash
# 1. Khởi tạo cấu trúc dự án dạng library (sử dụng src-layout)
uv init --lib my_ddd_lib
cd my_ddd_lib

# 2. Tạo môi trường ảo và kích hoạt
uv venv
source .venv/bin/activate  # Trên Linux/macOS
# .venv\Scripts\activate   # Trên Windows

# 3. Cài đặt các công cụ phát triển nếu cần (ví dụ: pytest)
uv add --dev pytest

```

---

## 3. Viết Mã Nguồn Theo Chuẩn DDD

### Bước 3.1: Domain Layer (`src/my_ddd_lib/domain/models.py`)

Định nghĩa Entities và Value Objects. Domain layer **hoàn toàn độc lập** với thế giới bên ngoài.

```python
from dataclasses import dataclass
from uuid import UUID, uuid4


class DomainException(Exception):
    """Lỗi nghiệp vụ cơ sở"""

    pass


class InsufficientBalanceError(DomainException):
    pass


@dataclass(frozen=True)
class Money:
    """Value Object: Bất biến (Immutable)"""

    amount: float
    currency: str = "VND"


class BankAccount:
    """Aggregate Root / Entity"""

    def __init__(self, account_id: UUID, balance: Money):
        self.id = account_id
        self.balance = balance

    def deposit(self, money: Money) -> None:
        if money.amount <= 0:
            raise DomainException("Số tiền gửi phải lớn hơn 0")
        self.balance = Money(self.balance.amount + money.amount, self.balance.currency)

    def withdraw(self, money: Money) -> None:
        if money.amount > self.balance.amount:
            raise InsufficientBalanceError("Số dư không đủ")
        self.balance = Money(self.balance.amount - money.amount, self.balance.currency)
```

### Bước 3.2: Domain Repositories (`src/my_ddd_lib/domain/repositories.py`)

Định nghĩa giao diện lưu trữ (Interface/Abstract Class).

```python
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from my_ddd_lib.domain.models import BankAccount


class AccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, account_id: UUID) -> Optional[BankAccount]:
        pass

    @abstractmethod
    def save(self, account: BankAccount) -> None:
        pass
```

### Bước 3.3: Application Layer (`src/my_ddd_lib/application/services.py`)

Điều phối luồng công việc (Use Cases), không chứa logic nghiệp vụ cốt lõi.

```python
from uuid import UUID
from my_ddd_lib.domain.models import Money
from my_ddd_lib.domain.repositories import AccountRepository


class TransferService:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def transfer(self, from_id: UUID, to_id: UUID, amount: float) -> None:
        from_acc = self.account_repo.get_by_id(from_id)
        to_acc = self.account_repo.get_by_id(to_id)

        if not from_acc or not to_acc:
            raise ValueError("Tài khoản không tồn tại")

        transfer_money = Money(amount)
        from_acc.withdraw(transfer_money)
        to_acc.deposit(transfer_money)

        self.account_repo.save(from_acc)
        self.account_repo.save(to_acc)
```

### Bước 3.4: Infrastructure Layer (`src/my_ddd_lib/infrastructure/repositories.py`)

Triển khai kỹ thuật cụ thể (In-memory, PostgreSQL, MongoDB, v.v.).

```python
from typing import Dict, Optional
from uuid import UUID
from my_ddd_lib.domain.models import BankAccount
from my_ddd_lib.domain.repositories import AccountRepository


class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self._store: Dict[UUID, BankAccount] = {}

    def get_by_id(self, account_id: UUID) -> Optional[BankAccount]:
        return self._store.get(account_id)

    def save(self, account: BankAccount) -> None:
        self._store[account.id] = account
```

---

## 4. Cấu hình Cấu trúc Export Package (`src/my_ddd_lib/__init__.py`)

Giúp người dùng thư viện dễ dàng import các thành phần chính:

```python
from my_ddd_lib.domain.models import BankAccount, Money
from my_ddd_lib.application.services import TransferService
from my_ddd_lib.infrastructure.repositories import InMemoryAccountRepository

__all__ = [
    "BankAccount",
    "Money",
    "TransferService",
    "InMemoryAccountRepository",
]
```

---

## 5. Cấu hình Đóng gói với `pyproject.toml`

`uv` sử dụng chuẩn PEP 621 trong file `pyproject.toml`. Kiểm tra nội dung file:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-ddd-lib"
version = "0.1.0"
description = "Thư viện Python xây dựng theo chuẩn Domain-Driven Design"
readme = "README.md"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/my_ddd_lib"]

```

---

## 6. Kiểm thử & Đóng gói sản phẩm bằng `uv`

### Kiểm thử bằng `pytest`

Tạo file test đơn giản `tests/test_domain.py`:

```python
from uuid import uuid4
from my_ddd_lib import BankAccount, Money


def test_deposit():
    acc = BankAccount(account_id=uuid4(), balance=Money(100))
    acc.deposit(Money(50))
    assert acc.balance.amount == 150
```

Chạy test với `uv`:

```bash
uv run pytest

```

### Build gói thư viện (Wheel & Source Distribution)

Chạy lệnh đóng gói:

```bash
uv build

```

Sau khi chạy xong, thư mục `dist/` sẽ được tạo ra chứa 2 file:

* `my_ddd_lib-0.1.0-py3-none-any.whl` (Wheel file)
* `my_ddd_lib-0.1.0.tar.gz` (Source distribution)

---

## 7. Xuất bản hoặc Cài đặt Thư viện

* **Cài đặt thử nghiệm nội bộ:**
```bash
uv pip install dist/my_ddd_lib-0.1.0-py3-none-any.whl

```


* **Xuất bản lên PyPI bằng `uv`:**
```bash
uv publish --token <YOUR_PYPI_TOKEN>

```