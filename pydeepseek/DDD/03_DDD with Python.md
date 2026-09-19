# 📖 Bài 3: Python + DDD — Những đặc trưng cần biết

> Bài này chuyển từ **lý thuyết** sang **thực hành setup**. Sau bài này, bạn sẽ có một project DDD Python hoàn chỉnh: cấu trúc thư mục, tooling (mypy, pytest, import-linter), và hiểu rõ **Python mạnh/yếu ở đâu** khi làm DDD.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Python mạnh/yếu** ở đâu cho DDD — và cách khắc phục điểm yếu.
2. Biết các **tính năng Python** dùng cho DDD: `dataclass`, `Protocol`, `Enum`, `typing`.
3. **Setup project DDD Python** đầu tiên từ A→Z.
4. Cấu hình **mypy strict**, **pytest**, **import-linter** để giữ kỷ luật.
5. Chạy được project với **1 lệnh duy nhất**.

---

## 1. Python mạnh ở đâu cho DDD?

### 1.1. `@dataclass(frozen=True)` — Value Object siêu gọn

Java/C# cần 30-50 dòng để viết một Value Object. Python chỉ cần 5-10 dòng.

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money không thể âm")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"Khác loại tiền tệ: {self.currency} vs {other.currency}")
```

**Điều `frozen=True` làm được:**
- Không cho gán lại field → immutable.
- Có `__eq__` và `__hash__` tự động → so sánh bằng giá trị.
- Có `__repr__` tự động → debug dễ.

**Điều `frozen=True` KHÔNG làm được:**
- Không ngăn được các object mutable bên trong (list, dict) bị sửa. Cần tự cẩn thận.

### 1.2. `Protocol` — Interface không cần kế thừa

Java/C# phải khai báo `interface` rồi `implements`. Python có `Protocol` — chỉ cần khai báo **hình dạng**, không cần liên kết cứng.

```python
from typing import Protocol
from uuid import UUID


class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> "Order | None": ...
    def save(self, order: "Order") -> None: ...
    def next_id(self) -> UUID: ...
```

**Lợi ích:**
- Bất kỳ class nào có đúng 3 method trên → tự động thỏa mãn protocol.
- Không cần kế thừa, không cần `register`.
- Test có thể dùng `FakeOrderRepository` mà không cần import gì từ production.

```python
class FakeOrderRepository:
    def __init__(self):
        self._store: dict[UUID, Order] = {}

    def find_by_id(self, order_id: UUID) -> "Order | None":
        return self._store.get(order_id)

    def save(self, order: "Order") -> None:
        self._store[order.id] = order

    def next_id(self) -> UUID:
        return uuid4()

# Không cần kế thừa gì cả!
def process(repo: OrderRepository) -> None:
    ...

process(FakeOrderRepository())   # OK
```

> 💡 **Khi nào dùng `Protocol` vs `ABC`?**
> - `Protocol`: khi muốn **structural typing** — "có hình dạng này là đủ". Dùng cho Repository, Port.
> - `ABC`: khi muốn **nominal typing** — bắt buộc kế thừa. Hiếm dùng trong DDD Python.

### 1.3. `Enum` — Loại bỏ magic number

```python
from enum import Enum


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
```

So sánh:

```python
# ❌ Magic number
if order.status == 2:
    ...

# ✅ Enum
if order.status == OrderStatus.SHIPPED:
    ...
```

### 1.4. Type hints — Tài liệu sống

```python
def withdraw(self, amount: Money) -> None:
    """Rút tiền. Raise InsufficientFunds nếu thiếu."""
    ...
```

Chỉ cần đọc signature là biết:
- Nhận `Money`, không phải int hay str.
- Trả về `None` → tức là hàm thay đổi state, không trả kết quả.
- Có thể raise (ghi trong docstring).

### 1.5. Duck typing — Linh hoạt cho Repository/Service

```python
class InMemoryOrderRepository:
    def find_by_id(self, order_id: UUID): ...
    def save(self, order: Order): ...
    def next_id(self) -> UUID: ...

class SqlAlchemyOrderRepository:
    def find_by_id(self, order_id: UUID): ...
    def save(self, order: Order): ...
    def next_id(self) -> UUID: ...

# Application service không cần biết là cái nào
class PlaceOrderHandler:
    def __init__(self, repo):   # ai cũng được, miễn có 3 method
        self._repo = repo
```

### 1.6. Async/await — Tự nhiên cho I/O

edge-tts, database, HTTP đều async. Python handle rất tốt.

```python
async def synthesize(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    return await communicate.save(...)
```

---

## 2. Python yếu ở đâu cho DDD?

Đây là phần **quan trọng** — bạn phải biết để phòng tránh.

### 2.1. Không có access modifier thật

Trong Java, `private` là thật. Trong Python, `_private` **chỉ là convention**.

```python
class Order:
    def __init__(self):
        self._lines = []

order = Order()
order._lines.append("hacked")   # Python không ngăn!
```

**Cách khắc phục:**

1. **Dùng `__slots__`** để giới hạn thuộc tính:
```python
class Order:
    __slots__ = ("_id", "_lines", "_status")

    def __init__(self, order_id):
        self._id = order_id
        self._lines = []
        self._status = "DRAFT"
```

2. **Dùng `@property`** cho read-only:
```python
class Order:
    def __init__(self):
        self._lines = []

    @property
    def lines(self) -> tuple:
        return tuple(self._lines)   # trả về tuple bất biến
```

3. **Không expose internal** — chỉ expose những gì cần thiết.

4. **Chấp nhận thực tế:** Python không ngăn được. Ta dựa vào **code review + kỷ luật team**.

### 2.2. Không có compiler — không bắt lỗi type

```python
def withdraw(self, amount: int) -> None:
    ...

account.withdraw("hello")   # Python cho qua, runtime mới lỗi
```

**Cách khắc phục:** Dùng **mypy** ở chế độ `strict`.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
disallow_any_generics = true
no_implicit_optional = true
```

Chạy:
```bash
mypy src/
```

Nếu có lỗi type → **fail ngay**. Giống như compiler.

### 2.3. Dynamic — dễ "tiện tay" thêm method

Python cho phép thêm method vào object bất cứ lúc nào:

```python
order = Order(...)
order.hack_method = lambda: print("hacked")   # Python cho!
```

**Cách khắc phục:**
- Dùng `__slots__`.
- Code review nghiêm túc.
- Không dùng `setattr`/`getattr` bừa bãi.

### 2.4. Không có `final` — không ngăn được override

```python
class Order:
    def place(self): ...

class EvilOrder(Order):
    def place(self):   # override, không ai ngăn
        pass
```

**Cách khắc phục:**
- Dùng `@final` (từ `typing`) — chỉ để mypy cảnh báo, không ngăn runtime.
```python
from typing import final

class Order:
    @final
    def place(self) -> None: ...
```

### 2.5. Tổng kết: ma trận mạnh/yếu

| Khía cạnh | Python |
|---|---|
| Viết Value Object | ⭐⭐⭐⭐⭐ (dataclass frozen) |
| Interface | ⭐⭐⭐⭐⭐ (Protocol) |
| Enum | ⭐⭐⭐⭐ |
| Type safety | ⭐⭐ (cần mypy) |
| Encapsulation | ⭐⭐ (convention) |
| Testability | ⭐⭐⭐⭐⭐ (pytest + duck typing) |
| Tooling kỷ luật | ⭐⭐⭐⭐ (mypy, import-linter, ruff) |

**Kết luận:** Python làm DDD **rất tốt** nếu bạn dùng đúng tooling. Điểm yếu có thể khắc phục bằng kỷ luật + mypy.

---

## 3. Setup project DDD Python — Từ A đến Z

Chúng ta sẽ setup project **`bookstore`** — một hệ thống bán sách đơn giản.

### 3.1. Yêu cầu

- Python **3.11+** (cần `X | None` syntax, `tomllib`).
- `pip` hoặc `uv` (tôi khuyến nghị `uv` cho nhanh, nhưng dùng `pip` cũng được).

Kiểm tra:
```bash
python --version
# Python 3.11.x hoặc cao hơn
```

### 3.2. Tạo cấu trúc thư mục

```bash
mkdir bookstore && cd bookstore
mkdir -p src/bookstore/{domain/{model,services,repositories,events},application/{commands,queries},infrastructure/{persistence,external},presentation/cli}
mkdir -p tests/{unit/domain,integration}
```

Kết quả:

```
bookstore/
├── src/
│   └── bookstore/
│       ├── domain/
│       │   ├── model/
│       │   ├── services/
│       │   ├── repositories/
│       │   └── events/
│       ├── application/
│       │   ├── commands/
│       │   └── queries/
│       ├── infrastructure/
│       │   ├── persistence/
│       │   └── external/
│       └── presentation/
│           └── cli/
└── tests/
    ├── unit/
    │   └── domain/
    └── integration/
```

> 💡 **Tại sao `src/bookstore/` thay vì `bookstore/`?**
> - Tránh import nhầm khi test.
> - Best practice của Python packaging hiện đại.

### 3.3. Tạo `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "bookstore"
version = "0.1.0"
description = "Bookstore DDD example"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "mypy>=1.7",
    "ruff>=0.1",
    "import-linter>=2.0",
]

[project.scripts]
bookstore = "bookstore.presentation.cli.main:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/bookstore"]

# ---------- mypy ----------
[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
disallow_any_generics = true
disallow_untyped_defs = true
no_implicit_optional = true
plugins = []

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# ---------- pytest ----------
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"

# ---------- coverage ----------
[tool.coverage.run]
source = ["src/bookstore"]
omit = ["*/tests/*", "*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]

# ---------- ruff ----------
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501"]   # line length do line-length quản lý

# ---------- import-linter ----------
[tool.importlinter]
root_packages = ["bookstore"]

[[tool.importlinter.contracts]]
name = "Domain không phụ thuộc ai"
type = "forbidden"
source_modules = ["bookstore.domain"]
forbidden_modules = [
    "bookstore.application",
    "bookstore.infrastructure",
    "bookstore.presentation",
]

[[tool.importlinter.contracts]]
name = "Application không phụ thuộc Infrastructure/Presentation"
type = "forbidden"
source_modules = ["bookstore.application"]
forbidden_modules = [
    "bookstore.infrastructure",
    "bookstore.presentation",
]

[[tool.importlinter.contracts]]
name = "Presentation không bị import bởi layer khác"
type = "forbidden"
source_modules = [
    "bookstore.domain",
    "bookstore.application",
    "bookstore.infrastructure",
]
forbidden_modules = ["bookstore.presentation"]
```

**Giải thích các phần quan trọng:**

| Phần | Mục đích |
|---|---|
| `[build-system]` | Dùng `hatchling` build backend (hiện đại, nhanh) |
| `[project.scripts]` | Tạo lệnh `bookstore` sau khi `pip install -e .` |
| `[tool.mypy] strict = true` | Bật full strict mode |
| `[[tool.mypy.overrides]]` | Nới lỏng cho test |
| `pythonpath = ["src"]` | pytest tự thêm `src/` vào `sys.path` |
| `[tool.importlinter]` | 3 contract bảo vệ dependency rule |
| `[tool.ruff]` | Linter nhanh thay `flake8` |

### 3.4. Tạo file `__init__.py`

```bash
# Tạo __init__.py rỗng ở mọi folder
find src tests -type d -exec touch {}/__init__.py \;
```

### 3.5. Viết code DDD đầu tiên

#### Domain — Value Object

```python
# src/bookstore/domain/model/money.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money không thể âm")
        if len(self.currency) != 3:
            raise ValueError("Currency phải là ISO 4217 (3 ký tự)")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        if self.amount < other.amount:
            raise ValueError("Kết quả phép trừ âm")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(factor), self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Khác loại tiền tệ: {self.currency} vs {other.currency}"
            )
```

#### Domain — Entity (Aggregate Root)

```python
# src/bookstore/domain/model/book.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .money import Money


@dataclass
class Book:
    """Aggregate Root đại diện cho một cuốn sách."""
    id: UUID
    title: str
    author: str
    price: Money
    stock: int = 0

    @classmethod
    def create(
        cls,
        title: str,
        author: str,
        price: Money,
        stock: int = 0,
    ) -> "Book":
        if not title.strip():
            raise ValueError("Tên sách không được rỗng")
        if not author.strip():
            raise ValueError("Tác giả không được rỗng")
        if stock < 0:
            raise ValueError("Stock không thể âm")
        return cls(
            id=uuid4(),
            title=title.strip(),
            author=author.strip(),
            price=price,
            stock=stock,
        )

    def reduce_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Số lượng phải > 0")
        if quantity > self.stock:
            raise InsufficientStock(self.id, quantity, self.stock)
        self.stock -= quantity

    def add_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Số lượng phải > 0")
        self.stock += quantity


class InsufficientStock(Exception):
    def __init__(self, book_id: UUID, requested: int, available: int):
        super().__init__(
            f"Sách {book_id} không đủ: cần {requested}, còn {available}"
        )
        self.book_id = book_id
        self.requested = requested
        self.available = available
```

#### Domain — Repository Protocol

```python
# src/bookstore/domain/repositories/book_repository.py
from typing import Protocol
from uuid import UUID

from ..model.book import Book


class BookRepository(Protocol):
    def find_by_id(self, book_id: UUID) -> Book | None: ...
    def save(self, book: Book) -> None: ...
    def find_all(self) -> list[Book]: ...
```

#### Application — Command + Handler

```python
# src/bookstore/application/commands/add_book.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from ...domain.model.book import Book
from ...domain.model.money import Money
from ...domain.repositories.book_repository import BookRepository


@dataclass(frozen=True)
class AddBookCommand:
    title: str
    author: str
    price_amount: Decimal
    price_currency: str = "VND"
    stock: int = 0


class AddBookHandler:
    def __init__(self, repo: BookRepository) -> None:
        self._repo = repo

    def handle(self, cmd: AddBookCommand) -> UUID:
        price = Money(cmd.price_amount, cmd.price_currency)
        book = Book.create(
            title=cmd.title,
            author=cmd.author,
            price=price,
            stock=cmd.stock,
        )
        self._repo.save(book)
        return book.id
```

#### Infrastructure — In-memory Repository (cho test)

```python
# src/bookstore/infrastructure/persistence/in_memory.py
from uuid import UUID

from ...domain.model.book import Book


class InMemoryBookRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Book] = {}

    def find_by_id(self, book_id: UUID) -> Book | None:
        return self._store.get(book_id)

    def save(self, book: Book) -> None:
        self._store[book.id] = book

    def find_all(self) -> list[Book]:
        return list(self._store.values())
```

#### Presentation — CLI

```python
# src/bookstore/presentation/cli/main.py
from decimal import Decimal

import click

from ...application.commands.add_book import AddBookCommand, AddBookHandler
from ...infrastructure.persistence.in_memory import InMemoryBookRepository


@click.group()
def cli() -> None:
    """Bookstore CLI — ví dụ DDD Python."""


@cli.command()
@click.argument("title")
@click.argument("author")
@click.option("--price", type=Decimal, required=True, help="Giá sách (VND).")
@click.option("--stock", type=int, default=0, help="Số lượng tồn kho.")
def add(title: str, author: str, price: Decimal, stock: int) -> None:
    """Thêm một cuốn sách mới."""
    repo = InMemoryBookRepository()
    handler = AddBookHandler(repo)
    cmd = AddBookCommand(title=title, author=author, price_amount=price, stock=stock)
    book_id = handler.handle(cmd)
    click.echo(f"✅ Đã thêm sách: {book_id}")


if __name__ == "__main__":
    cli()
```

#### Entry point cho `python -m`

```python
# src/bookstore/__main__.py
from .presentation.cli.main import cli

if __name__ == "__main__":
    cli()
```

### 3.6. Cài đặt và chạy

```bash
# Tạo virtual env (khuyên dùng uv, nhưng pip cũng được)
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Cài dev dependencies
pip install -e ".[dev]"

# Hoặc dùng uv (nhanh hơn nhiều)
# uv venv
# uv pip install -e ".[dev]"
```

Kiểm tra cài đặt:

```bash
bookstore --help
# Usage: bookstore [OPTIONS] COMMAND [ARGS]...
#   Bookstore CLI — ví dụ DDD Python.
# Options:
#   --help  Show this message and exit.
# Commands:
#   add  Thêm một cuốn sách mới.
```

Chạy thử:

```bash
bookstore add "Clean Code" "Robert Martin" --price 250000 --stock 10
# ✅ Đã thêm sách: 3f2a1b4c-...
```

### 3.7. Chạy kiểm tra chất lượng

```bash
# 1. Type check
mypy src/
# Success: no issues found in 8 source files

# 2. Lint
ruff check src/
# All checks passed!

# 3. Format
ruff format src/

# 4. Dependency rule
lint-imports
# ===== Import Linter =====
# ------------
# Domain không phụ thuộc ai KEPT
# Application không phụ thuộc Infrastructure/Presentation KEPT
# Presentation không bị import bởi layer khác KEPT
# ------------
# Contracts: 3 kept, 0 broken.

# 5. Test (chưa có test nào)
pytest
# no tests ran
```

**Đây là lúc để viết test đầu tiên.**

### 3.8. Viết test đầu tiên

```python
# tests/unit/domain/test_money.py
from decimal import Decimal

import pytest

from bookstore.domain.model.money import Money


def test_money_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="không thể âm"):
        Money(Decimal("-1"), "VND")


def test_money_add_same_currency() -> None:
    a = Money(Decimal("100"), "VND")
    b = Money(Decimal("50"), "VND")
    assert a + b == Money(Decimal("150"), "VND")


def test_money_add_different_currency_raises() -> None:
    a = Money(Decimal("100"), "VND")
    b = Money(Decimal("50"), "USD")
    with pytest.raises(ValueError, match="Khác loại tiền tệ"):
        a + b


def test_money_is_immutable() -> None:
    m = Money(Decimal("100"), "VND")
    with pytest.raises(Exception):   # FrozenInstanceError
        m.amount = Decimal("200")   # type: ignore[misc]


def test_money_equality_by_value() -> None:
    assert Money(Decimal("100"), "VND") == Money(Decimal("100"), "VND")
    assert Money(Decimal("100"), "VND") != Money(Decimal("100"), "USD")
```

```python
# tests/unit/domain/test_book.py
from decimal import Decimal
from uuid import uuid4

import pytest

from bookstore.domain.model.book import Book, InsufficientStock
from bookstore.domain.model.money import Money


def test_create_book_with_empty_title_raises() -> None:
    with pytest.raises(ValueError, match="Tên sách"):
        Book.create(title="", author="An", price=Money(Decimal("100")))


def test_create_book_with_negative_stock_raises() -> None:
    with pytest.raises(ValueError, match="Stock"):
        Book.create(title="DDD", author="Evans", price=Money(Decimal("100")), stock=-1)


def test_reduce_stock_decreases_quantity() -> None:
    book = Book.create(title="DDD", author="Evans", price=Money(Decimal("100")), stock=10)
    book.reduce_stock(3)
    assert book.stock == 7


def test_reduce_stock_more_than_available_raises() -> None:
    book = Book.create(title="DDD", author="Evans", price=Money(Decimal("100")), stock=5)
    with pytest.raises(InsufficientStock):
        book.reduce_stock(10)


def test_reduce_stock_with_zero_raises() -> None:
    book = Book.create(title="DDD", author="Evans", price=Money(Decimal("100")), stock=5)
    with pytest.raises(ValueError, match="> 0"):
        book.reduce_stock(0)
```

Chạy:
```bash
pytest
# tests/unit/domain/test_money.py .....   [50%]
# tests/unit/domain/test_book.py .....    [100%]
# 10 passed in 0.05s
```

**Điều kỳ diệu:** 10 test chạy trong **0.05 giây**. Không cần DB, không cần mock, không cần network.

---

## 4. Cấu hình CI (GitHub Actions)

Thêm file `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint (ruff)
        run: ruff check src/ tests/

      - name: Type check (mypy)
        run: mypy src/

      - name: Dependency rule (import-linter)
        run: lint-imports

      - name: Test
        run: pytest --cov=src/bookstore --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
```

**CI sẽ chặn merge nếu:**
- Lint fail.
- Type sai.
- Dependency rule vi phạm.
- Test fail.

**Đây là "compiler" của Python.**

---

## 5. Pre-commit hooks — Tự động hóa

Cài `pre-commit` để tự động chạy kiểm tra trước mỗi commit.

```bash
pip install pre-commit
```

Tạo `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: []

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Cài hooks:
```bash
pre-commit install
```

Từ giờ, mỗi lần `git commit`, hooks sẽ tự chạy. Nếu code sai → commit bị chặn.

---

## 6. Makefile tiện dụng

Tạo `Makefile` để chạy các lệnh nhanh:

```makefile
.PHONY: install lint typecheck imports test cov check clean

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:
	mypy src/

imports:
	lint-imports

test:
	pytest

cov:
	pytest --cov=src/bookstore --cov-report=html --cov-report=term-missing

check: lint typecheck imports test
	@echo "✅ All checks passed!"

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
```

Sau đó chỉ cần:

```bash
make check    # chạy tất cả kiểm tra
make cov      # xem coverage HTML
```

---

## 7. Cấu trúc cuối cùng

Sau bài này, project của bạn trông như thế này:

```
bookstore/
├── .github/workflows/ci.yml       # CI
├── .pre-commit-config.yaml        # Git hooks
├── .gitignore
├── Makefile                        # Lệnh tiện dụng
├── pyproject.toml                  # Config tất cả tool
├── README.md
├── src/
│   └── bookstore/
│       ├── __init__.py
│       ├── __main__.py
│       ├── domain/
│       │   ├── model/
│       │   │   ├── __init__.py
│       │   │   ├── money.py         # VO
│       │   │   └── book.py          # Aggregate Root
│       │   ├── repositories/
│       │   │   └── book_repository.py  # Protocol
│       │   └── services/
│       ├── application/
│       │   └── commands/
│       │       └── add_book.py      # Command + Handler
│       ├── infrastructure/
│       │   └── persistence/
│       │       └── in_memory.py
│       └── presentation/
│           └── cli/
│               └── main.py
└── tests/
    └── unit/
        └── domain/
            ├── test_money.py
            └── test_book.py
```

**Chạy `make check`:**

```
ruff check src/ tests/
All checks passed!

mypy src/
Success: no issues found in 8 source files

lint-imports
Contracts: 3 kept, 0 broken.

pytest
10 passed in 0.05s

✅ All checks passed!
```

---

## 8. Anti-patterns cần tránh khi setup

| ❌ Anti-pattern | ✅ Cách đúng |
|---|---|
| Dùng `setup.py` cũ | Dùng `pyproject.toml` |
| Không có `src/` layout | Luôn dùng `src/package_name/` |
| mypy không strict | `strict = true` |
| Không enforce dependency rule | Dùng `import-linter` |
| Test dùng DB thật | Dùng in-memory cho domain test |
| Để `__pycache__` trong git | Có `.gitignore` |
| Chạy tool thủ công | Dùng `make` hoặc `pre-commit` |
| Không có CI | GitHub Actions chạy mọi push |
| Mix domain với infrastructure | `import-linter` chặn |

### `.gitignore` mẫu

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# Virtual envs
.venv/
venv/
env/

# Test & coverage
.pytest_cache/
.coverage
htmlcov/
.tox/

# Type check
.mypy_cache/

# Lint
.ruff_cache/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
```

---

## 9. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Setup project `library`

Lặp lại toàn bộ quá trình setup cho domain **"thư viện"** với:

- VO: `ISBN`, `Money`, `Email`.
- Entity: `Book`, `Member`.
- Aggregate Root: `Loan` (phiếu mượn).
- Repository Protocol: `BookRepository`, `MemberRepository`, `LoanRepository`.

Chạy được:
- `make check` pass.
- `library --help` hiển thị CLI.
- Ít nhất 10 test.

### 🟡 Bài tập 2 (trung bình): Thêm import-linter contract

Thêm contract để enforce:

1. `bookstore.domain.model` không được import `bookstore.domain.services`.
2. `bookstore.application.commands` không được import `bookstore.application.queries`.

Gợi ý: dùng `type = "forbidden"` với `source_modules` và `forbidden_modules`.

### 🔴 Bài tập 3 (khó): Setup từ đầu không cần template

Xóa toàn bộ project, làm lại từ đầu **chỉ với trí nhớ**. Mục tiêu:

- Tạo được `pyproject.toml` với đủ config.
- Chạy `mypy --strict`, `ruff`, `lint-imports`, `pytest` đều pass.
- Có ít nhất 3 contract import-linter.
- Có CI workflow chạy trên GitHub (nếu bạn có repo).

Thời gian mục tiêu: **30 phút**. Nếu lâu hơn, bạn cần luyện lại.

---

## 10. Tóm tắt bài 3

| Điểm | Nội dung |
|---|---|
| **Python mạnh** | `dataclass(frozen=True)`, `Protocol`, `Enum`, type hints, duck typing |
| **Python yếu** | Không access modifier, không compiler, dynamic, không `final` |
| **Khắc phục** | mypy strict + import-linter + ruff + pre-commit + CI |
| **Cấu trúc** | `src/package/{domain,application,infrastructure,presentation}/` |
| **Config** | `pyproject.toml` chứa mọi tool config |
| **Setup** | `python -m venv .venv && pip install -e ".[dev]"` |
| **Kiểm tra** | `make check` chạy tất cả |
| **Test** | Pure Python, không DB, chạy trong 0.05s |
| **CI** | GitHub Actions chặn merge nếu fail |

**Câu thần chú:** *"Python không ngăn bạn làm bậy, nhưng tooling sẽ."*

---

## 11. Chuẩn bị cho bài 4

Bài tiếp theo: **Bounded Context — Chia để trị**.

Chuẩn bị:
- Đọc lại bài 2 (Ubiquitous Language) — vì Bounded Context là hệ quả tự nhiên của việc có nhiều ngôn ngữ.
- Nghĩ về **hệ thống lớn** bạn từng làm: có bao nhiêu "ngữ cảnh" khác nhau?
- Sẽ bàn: tại sao cùng một từ "Customer" lại có nghĩa khác ở Sales/Shipping/Billing, và làm sao để code phản ánh điều đó.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 4** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: `Protocol` vs `ABC`, `frozen=True` chi tiết, mypy plugin, monorepo setup.
5. **Debug** nếu bạn gặp lỗi khi setup (gửi error message).

Nói tôi biết bạn muốn gì nhé.