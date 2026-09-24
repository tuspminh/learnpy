# 📖 Bài 18: DDD + FastAPI + SQLAlchemy — Project hoàn chỉnh

> Đây là **bài cuối cùng** của lộ trình. Bạn đã học 17 bài — từ DDD là gì, đến Event Sourcing. Giờ là lúc **ghép mọi thứ** vào **1 project thực tế, production-ready**. Chúng ta sẽ xây **hệ thống đặt hàng e-commerce** từ A→Z: Event Storming → Context Map → Code → Test → Deploy.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. **Ghép mọi thứ đã học** vào 1 project hoàn chỉnh.
2. Xây **hệ thống e-commerce** với 2 Bounded Context: Catalog, Order.
3. Áp dụng **tất cả building blocks**: VO, Entity, Aggregate, Event, Repository, UoW.
4. Áp dụng **kiến trúc 4 tầng** + **CQRS** + **DI**.
5. Viết **test đầy đủ**: unit, integration, e2e.
6. Setup **CI/CD** với GitHub Actions.
7. Biết **cách deploy** production.
8. Có **template** để dùng cho dự án thật.

---

## 1. Tổng quan project

### 1.1. Domain: E-commerce đơn giản

**Yêu cầu nghiệp vụ:**

- Khách hàng xem sản phẩm từ Catalog.
- Khách hàng đặt hàng (Place Order).
- Đơn hàng có nhiều lines (mỗi line = sản phẩm + số lượng).
- Đơn hàng có state: DRAFT → PLACED → SHIPPED → DELIVERED / CANCELLED.
- Khi đặt hàng, cần snapshot giá sản phẩm (giá có thể đổi sau).
- Khi đặt hàng, phát event `OrderPlaced` → gửi email + reserve inventory.

### 1.2. Bounded Context

```
┌────────────────┐         ┌────────────────┐
│    Catalog     │         │     Order      │
│  (sản phẩm)    │────────▶│  (đơn hàng)    │
└────────────────┘  ACL    └────────────────┘
                                    │
                                    │ Events
                                    ▼
                          ┌────────────────┐
                          │  Notification  │
                          │  (thông báo)   │
                          └────────────────┘

Shared Kernel: Money, CustomerId
```

**Context:**

1. **Catalog** — quản lý sản phẩm (CRUD).
2. **Order** — Core Domain, phức tạp nhất, áp dụng DDD đầy đủ.
3. **Notification** — gửi email (Generic Domain, đơn giản).

### 1.3. Tech stack

- **Python 3.11+**
- **FastAPI** — presentation
- **SQLAlchemy 2.0** — infrastructure
- **Pydantic v2** — schemas
- **Alembic** — migrations
- **PostgreSQL** — production DB
- **SQLite** — test
- **pytest** — testing
- **mypy strict** — type checking
- **ruff** — linting
- **import-linter** — enforce architecture
- **Docker** — deployment

---

## 2. Cấu trúc project

```
shop/
├── pyproject.toml
├── README.md
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── migrations/                       # Alembic
│   ├── env.py
│   └── versions/
├── src/
│   └── shop/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── shared/                   # Shared Kernel
│       │   ├── __init__.py
│       │   ├── domain/
│       │   │   ├── __init__.py
│       │   │   ├── money.py
│       │   │   └── ids.py
│       │   └── events/
│       │       ├── __init__.py
│       │       └── base.py
│       │
│       ├── catalog/                  # Bounded Context 1
│       │   ├── __init__.py
│       │   ├── domain/
│       │   │   ├── __init__.py
│       │   │   ├── model/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── product.py
│       │   │   │   └── sku.py
│       │   │   ├── repositories/
│       │   │   │   ├── __init__.py
│       │   │   │   └── product_repository.py
│       │   │   ├── events/
│       │   │   │   ├── __init__.py
│       │   │   │   └── product_events.py
│       │   │   └── exceptions.py
│       │   ├── application/
│       │   │   ├── __init__.py
│       │   │   ├── commands/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── create_product.py
│       │   │   │   └── update_price.py
│       │   │   ├── queries/
│       │   │   │   ├── __init__.py
│       │   │   │   └── list_products.py
│       │   │   └── uow.py
│       │   ├── infrastructure/
│       │   │   ├── __init__.py
│       │   │   ├── orm_models.py
│       │   │   ├── mappers.py
│       │   │   ├── repositories.py
│       │   │   ├── uow.py
│       │   │   └── in_memory/
│       │   │       ├── __init__.py
│       │   │       ├── repositories.py
│       │   │       └── uow.py
│       │   └── presentation/
│       │       ├── __init__.py
│       │       ├── routes.py
│       │       └── schemas.py
│       │
│       ├── order/                    # Bounded Context 2 — Core Domain
│       │   ├── __init__.py
│       │   ├── domain/
│       │   │   ├── __init__.py
│       │   │   ├── model/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── order.py
│       │   │   │   ├── order_line.py
│       │   │   │   └── product_snapshot.py
│       │   │   ├── services/
│       │   │   │   ├── __init__.py
│       │   │   │   └── pricing_service.py
│       │   │   ├── repositories/
│       │   │   │   ├── __init__.py
│       │   │   │   └── order_repository.py
│       │   │   ├── events/
│       │   │   │   ├── __init__.py
│       │   │   │   └── order_events.py
│       │   │   └── exceptions.py
│       │   ├── application/
│       │   │   ├── __init__.py
│       │   │   ├── commands/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── place_order.py
│       │   │   │   ├── cancel_order.py
│       │   │   │   └── ship_order.py
│       │   │   ├── queries/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── order_summary.py
│       │   │   │   └── order_detail.py
│       │   │   ├── handlers/
│       │   │   │   ├── __init__.py
│       │   │   │   └── on_order_placed.py
│       │   │   ├── ports/
│       │   │   │   ├── __init__.py
│       │   │   │   └── catalog_port.py
│       │   │   └── uow.py
│       │   ├── infrastructure/
│       │   │   ├── __init__.py
│       │   │   ├── persistence/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── orm_models.py
│       │   │   │   ├── mappers.py
│       │   │   │   ├── repositories.py
│       │   │   │   └── uow.py
│       │   │   ├── acl/
│       │   │   │   ├── __init__.py
│       │   │   │   └── catalog_acl.py
│       │   │   └── in_memory/
│       │   │       ├── __init__.py
│       │   │       ├── repositories.py
│       │   │       └── uow.py
│       │   └── presentation/
│       │       ├── __init__.py
│       │       ├── routes.py
│       │       └── schemas.py
│       │
│       ├── notification/             # Bounded Context 3 — Generic
│       │   ├── __init__.py
│       │   └── email_sender.py
│       │
│       └── bootstrap.py              # Composition Root
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── shared/
    │   ├── catalog/
    │   └── order/
    ├── integration/
    │   ├── catalog/
    │   └── order/
    ├── e2e/
    │   └── api/
    └── fakes/
        ├── __init__.py
        ├── email_sender.py
        └── catalog_client.py
```

---

## 3. Shared Kernel

### 3.1. Money

```python
# shared/domain/money.py
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
            raise ValueError("Currency phải là ISO 4217")
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        if self.amount < other.amount:
            raise ValueError("Kết quả âm")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(factor), self.currency)

    def __radd__(self, other: int) -> "Money":
        if other == 0:
            return self
        return NotImplemented

    def __lt__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount < other.amount

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"Khác tiền tệ: {self.currency} vs {other.currency}")

    def __str__(self) -> str:
        return f"{self.amount:,.0f} {self.currency}"


ZERO_VND = Money(Decimal("0"), "VND")
```

### 3.2. Base Event

```python
# shared/events/base.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)
```

---

## 4. Catalog Context

### 4.1. Domain

```python
# catalog/domain/model/sku.py
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SKU:
    value: str

    _PATTERN = re.compile(r"^[A-Z0-9-]{4,20}$")

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if not self._PATTERN.match(normalized):
            raise ValueError(f"SKU không hợp lệ: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
```

```python
# catalog/domain/model/product.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shop.shared.domain.money import Money
from shop.catalog.domain.model.sku import SKU


@dataclass(eq=False)
class Product:
    id: UUID = field(default_factory=uuid4)
    sku: SKU = field(default=None)   # type: ignore
    name: str = ""
    price: Money = field(default=None)   # type: ignore
    is_published: bool = False

    @classmethod
    def create(cls, sku: SKU, name: str, price: Money) -> "Product":
        if not name.strip():
            raise ValueError("Tên không được rỗng")
        if price.amount <= 0:
            raise ValueError("Giá phải > 0")
        return cls(sku=sku, name=name.strip(), price=price)

    def publish(self) -> None:
        self.is_published = True

    def unpublish(self) -> None:
        self.is_published = False

    def update_price(self, new_price: Money) -> None:
        if new_price.amount <= 0:
            raise ValueError("Giá phải > 0")
        self.price = new_price

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Tên không được rỗng")
        self.name = new_name.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### 4.2. Repository Protocol

```python
# catalog/domain/repositories/product_repository.py
from typing import Protocol
from uuid import UUID

from shop.catalog.domain.model.product import Product
from shop.catalog.domain.model.sku import SKU


class ProductRepository(Protocol):
    def find_by_id(self, product_id: UUID) -> Product | None: ...
    def find_by_sku(self, sku: SKU) -> Product | None: ...
    def save(self, product: Product) -> None: ...
    def next_id(self) -> UUID: ...
```

### 4.3. Application

```python
# catalog/application/uow.py
from types import TracebackType
from typing import Protocol

from shop.catalog.domain.repositories.product_repository import ProductRepository


class UnitOfWork(Protocol):
    products: ProductRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

```python
# catalog/application/commands/create_product.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shop.catalog.application.uow import UnitOfWork
from shop.catalog.domain.model.product import Product
from shop.catalog.domain.model.sku import SKU
from shop.shared.domain.money import Money


@dataclass(frozen=True)
class CreateProductCommand:
    sku: str
    name: str
    price_amount: Decimal
    price_currency: str = "VND"


class SKUAlreadyExists(Exception):
    pass


class CreateProductHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: CreateProductCommand) -> UUID:
        sku = SKU(cmd.sku)
        price = Money(cmd.price_amount, cmd.price_currency)

        with self._uow:
            if self._uow.products.find_by_sku(sku):
                raise SKUAlreadyExists(str(sku))

            product = Product.create(sku=sku, name=cmd.name, price=price)
            self._uow.products.save(product)
            self._uow.commit()

        return product.id
```

### 4.4. Infrastructure

```python
# catalog/infrastructure/orm_models.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Numeric, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CatalogBase(DeclarativeBase):
    pass


class ProductRow(CatalogBase):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    price_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    price_currency: Mapped[str] = mapped_column(String(3))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
```

```python
# catalog/infrastructure/mappers.py
from shop.catalog.domain.model.product import Product
from shop.catalog.domain.model.sku import SKU
from shop.catalog.infrastructure.orm_models import ProductRow
from shop.shared.domain.money import Money


class ProductMapper:
    @staticmethod
    def to_domain(row: ProductRow) -> Product:
        return Product(
            id=row.id,
            sku=SKU(row.sku),
            name=row.name,
            price=Money(row.price_amount, row.price_currency),
            is_published=row.is_published,
        )

    @staticmethod
    def to_row(product: Product) -> ProductRow:
        return ProductRow(
            id=product.id,
            sku=product.sku.value,
            name=product.name,
            price_amount=product.price.amount,
            price_currency=product.price.currency,
            is_published=product.is_published,
        )
```

```python
# catalog/infrastructure/repositories.py
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from shop.catalog.domain.model.product import Product
from shop.catalog.domain.model.sku import SKU
from shop.catalog.infrastructure.mappers import ProductMapper
from shop.catalog.infrastructure.orm_models import ProductRow


class SqlAlchemyProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, product_id: UUID) -> Product | None:
        row = self._session.get(ProductRow, product_id)
        return ProductMapper.to_domain(row) if row else None

    def find_by_sku(self, sku: SKU) -> Product | None:
        row = (
            self._session.query(ProductRow)
            .filter(ProductRow.sku == sku.value)
            .one_or_none()
        )
        return ProductMapper.to_domain(row) if row else None

    def save(self, product: Product) -> None:
        self._session.merge(ProductMapper.to_row(product))

    def next_id(self) -> UUID:
        return uuid4()
```

```python
# catalog/infrastructure/uow.py
from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from shop.catalog.infrastructure.repositories import SqlAlchemyProductRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.products = SqlAlchemyProductRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()

    def commit(self) -> None:
        assert self._session
        self._session.commit()

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()
```

### 4.5. In-memory (cho test)

```python
# catalog/infrastructure/in_memory/repositories.py
from uuid import UUID, uuid4

from shop.catalog.domain.model.product import Product
from shop.catalog.domain.model.sku import SKU


class InMemoryProductRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Product] = {}

    def find_by_id(self, product_id: UUID) -> Product | None:
        return self._store.get(product_id)

    def find_by_sku(self, sku: SKU) -> Product | None:
        for product in self._store.values():
            if product.sku == sku:
                return product
        return None

    def save(self, product: Product) -> None:
        self._store[product.id] = product

    def next_id(self) -> UUID:
        return uuid4()


# catalog/infrastructure/in_memory/uow.py
class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.products = InMemoryProductRepository()

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, *args) -> None:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass
```

### 4.6. Presentation

```python
# catalog/presentation/schemas.py
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    sku: str = Field(min_length=4, max_length=20)
    name: str = Field(min_length=1, max_length=200)
    price_amount: Decimal = Field(gt=0)
    price_currency: str = Field(default="VND", min_length=3, max_length=3)


class CreateProductResponse(BaseModel):
    product_id: UUID
```

```python
# catalog/presentation/routes.py
from fastapi import APIRouter, Depends, HTTPException, status

from shop.catalog.application.commands.create_product import (
    CreateProductCommand,
    CreateProductHandler,
    SKUAlreadyExists,
)
from shop.catalog.presentation.schemas import (
    CreateProductRequest,
    CreateProductResponse,
)
from shop.bootstrap import Container


router = APIRouter(prefix="/catalog/products", tags=["catalog"])


def get_container() -> Container:
    from shop.presentation.api.main import app
    return app.state.container


@router.post("", response_model=CreateProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: CreateProductRequest,
    container: Container = Depends(get_container),
) -> CreateProductResponse:
    handler = container.make_create_product_handler()
    cmd = CreateProductCommand(
        sku=request.sku,
        name=request.name,
        price_amount=request.price_amount,
        price_currency=request.price_currency,
    )
    try:
        product_id = handler.handle(cmd)
    except SKUAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    return CreateProductResponse(product_id=product_id)
```

---

## 5. Order Context — Core Domain

### 5.1. Domain

```python
# order/domain/model/product_snapshot.py
from dataclasses import dataclass

from shop.shared.domain.money import Money


@dataclass(frozen=True)
class ProductSnapshot:
    """Snapshot của Product tại thời điểm đặt hàng."""
    sku: str
    name: str
    unit_price: Money
```

```python
# order/domain/model/order_line.py
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.shared.domain.money import Money


@dataclass(eq=False)
class OrderLine:
    id: UUID = field(default_factory=uuid4)
    snapshot: ProductSnapshot = field(default=None)   # type: ignore
    _quantity: int = 1

    MAX_QUANTITY = 1000

    @classmethod
    def create(cls, snapshot: ProductSnapshot, quantity: int) -> "OrderLine":
        if quantity <= 0:
            raise ValueError("Quantity phải > 0")
        if quantity > cls.MAX_QUANTITY:
            raise ValueError(f"Quantity không quá {cls.MAX_QUANTITY}")
        return cls(snapshot=snapshot, _quantity=quantity)

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def subtotal(self) -> Money:
        return self.snapshot.unit_price * Decimal(self._quantity)

    def change_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise ValueError("Quantity phải > 0")
        if new_qty > self.MAX_QUANTITY:
            raise ValueError(f"Quantity không quá {self.MAX_QUANTITY}")
        self._quantity = new_qty

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderLine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

```python
# order/domain/events/order_events.py
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from shop.shared.events.base import DomainEvent


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    customer_id: UUID = field(default=None)   # type: ignore
    total_amount: str = ""
    total_currency: str = "VND"
    line_count: int = 0


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    tracking_number: str = ""


@dataclass(frozen=True)
class OrderDelivered(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    reason: str = ""
```

```python
# order/domain/exceptions.py
from uuid import UUID


class OrderNotEditable(Exception):
    def __init__(self, order_id: UUID, status: str) -> None:
        super().__init__(f"Order {order_id} ở {status}, không sửa được")
        self.order_id = order_id
        self.status = status


class EmptyOrderCannotBePlaced(Exception):
    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Order {order_id} rỗng")
        self.order_id = order_id


class InvalidTransition(Exception):
    def __init__(self, order_id: UUID, from_status: str, to_status: str) -> None:
        super().__init__(f"Không thể chuyển {from_status} → {to_status}")
        self.order_id = order_id
        self.from_status = from_status
        self.to_status = to_status


class LineNotFound(Exception):
    def __init__(self, order_id: UUID, line_id: UUID) -> None:
        super().__init__(f"Line {line_id} không có trong order {order_id}")
        self.order_id = order_id
        self.line_id = line_id


class TooManyLines(Exception):
    def __init__(self, order_id: UUID, limit: int) -> None:
        super().__init__(f"Order {order_id} vượt quá {limit} lines")
        self.order_id = order_id
        self.limit = limit
```

```python
# order/domain/model/order.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from shop.order.domain.events.order_events import (
    OrderPlaced,
    OrderShipped,
    OrderDelivered,
    OrderCancelled,
)
from shop.order.domain.exceptions import (
    OrderNotEditable,
    EmptyOrderCannotBePlaced,
    InvalidTransition,
    LineNotFound,
    TooManyLines,
)
from shop.order.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money, ZERO_VND


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.PLACED, OrderStatus.CANCELLED},
    OrderStatus.PLACED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


@dataclass(eq=False)
class Order:
    """Aggregate Root."""
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    _status: OrderStatus = OrderStatus.DRAFT
    _lines: dict[UUID, OrderLine] = field(default_factory=dict)
    _tracking_number: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list, repr=False)

    MAX_LINES = 100

    # Factory
    @classmethod
    def create(cls, customer_id: UUID) -> "Order":
        if customer_id is None:
            raise ValueError("customer_id không được None")
        return cls(customer_id=customer_id)

    @classmethod
    def reconstruct(
        cls,
        order_id: UUID,
        customer_id: UUID,
        status: OrderStatus,
        lines: list[OrderLine],
        tracking_number: str | None,
        created_at: datetime,
    ) -> "Order":
        order = cls(
            id=order_id,
            customer_id=customer_id,
            created_at=created_at,
        )
        order._status = status
        order._tracking_number = tracking_number
        for line in lines:
            order._lines[line.id] = line
        return order

    # Behavior
    def add_line(self, line: OrderLine) -> None:
        self._ensure_editable()
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines(self.id, self.MAX_LINES)
        if line.id in self._lines:
            raise ValueError(f"Line {line.id} đã tồn tại")
        self._lines[line.id] = line

    def remove_line(self, line_id: UUID) -> None:
        self._ensure_editable()
        if line_id not in self._lines:
            raise LineNotFound(self.id, line_id)
        del self._lines[line_id]

    def change_line_quantity(self, line_id: UUID, new_qty: int) -> None:
        self._ensure_editable()
        line = self._get_line(line_id)
        line.change_quantity(new_qty)

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced(self.id)
        self._transition_to(OrderStatus.PLACED)
        total = self.total
        self._events.append(OrderPlaced(
            order_id=self.id,
            customer_id=self.customer_id,
            total_amount=str(total.amount),
            total_currency=total.currency,
            line_count=len(self._lines),
        ))

    def ship(self, tracking_number: str) -> None:
        if not tracking_number.strip():
            raise ValueError("Tracking không được rỗng")
        self._transition_to(OrderStatus.SHIPPED)
        self._tracking_number = tracking_number.strip()
        self._events.append(OrderShipped(
            order_id=self.id,
            tracking_number=tracking_number.strip(),
        ))

    def deliver(self) -> None:
        self._transition_to(OrderStatus.DELIVERED)
        self._events.append(OrderDelivered(order_id=self.id))

    def cancel(self, reason: str) -> None:
        self._transition_to(OrderStatus.CANCELLED)
        self._events.append(OrderCancelled(
            order_id=self.id,
            reason=reason,
        ))

    # Query
    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        return tuple(self._lines.values())

    @property
    def total(self) -> Money:
        if not self._lines:
            return ZERO_VND
        return sum((line.subtotal for line in self._lines.values()), ZERO_VND)

    @property
    def tracking_number(self) -> str | None:
        return self._tracking_number

    # Internal
    def _get_line(self, line_id: UUID) -> OrderLine:
        if line_id not in self._lines:
            raise LineNotFound(self.id, line_id)
        return self._lines[line_id]

    def _ensure_editable(self) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable(self.id, self._status.value)

    def _transition_to(self, new_status: OrderStatus) -> None:
        if new_status not in VALID_TRANSITIONS[self._status]:
            raise InvalidTransition(
                self.id, self._status.value, new_status.value
            )
        self._status = new_status

    # Events
    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events

    # Identity
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### 5.2. Repository Protocol

```python
# order/domain/repositories/order_repository.py
from typing import Protocol
from uuid import UUID

from shop.order.domain.model.order import Order


class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def next_id(self) -> UUID: ...
```

### 5.3. Port — Catalog

```python
# order/application/ports/catalog_port.py
from typing import Protocol

from shop.order.domain.model.product_snapshot import ProductSnapshot


class CatalogPort(Protocol):
    """Port để Order lấy Product info từ Catalog."""
    def get_product_snapshot(self, sku: str) -> ProductSnapshot: ...
```

### 5.4. Application

```python
# order/application/uow.py
from types import TracebackType
from typing import Protocol

from shop.order.domain.repositories.order_repository import OrderRepository


class UnitOfWork(Protocol):
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def collect_events(self, events: list) -> None: ...
```

```python
# order/application/commands/place_order.py
from dataclasses import dataclass
from uuid import UUID

from shop.order.application.ports.catalog_port import CatalogPort
from shop.order.application.uow import UnitOfWork
from shop.order.domain.model.order import Order
from shop.order.domain.model.order_line import OrderLine


@dataclass(frozen=True)
class OrderItemInput:
    sku: str
    quantity: int


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]


class PlaceOrderHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        catalog_port: CatalogPort,
    ) -> None:
        self._uow = uow
        self._catalog = catalog_port

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        if not cmd.items:
            raise ValueError("Đơn hàng phải có ít nhất 1 sản phẩm")

        with self._uow:
            order = Order.create(cmd.customer_id)

            for item in cmd.items:
                # Lấy snapshot từ Catalog
                snapshot = self._catalog.get_product_snapshot(item.sku)
                line = OrderLine.create(snapshot, item.quantity)
                order.add_line(line)

            order.place()
            self._uow.orders.save(order)
            self._uow.commit()

        return order.id
```

```python
# order/application/commands/cancel_order.py
@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: UUID
    reason: str


class OrderNotFound(Exception):
    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Order {order_id} không tồn tại")
        self.order_id = order_id


class CancelOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: CancelOrderCommand) -> None:
        with self._uow:
            order = self._uow.orders.find_by_id(cmd.order_id)
            if not order:
                raise OrderNotFound(cmd.order_id)

            order.cancel(cmd.reason)
            self._uow.orders.save(order)
            self._uow.commit()
```

### 5.5. Queries

```python
# order/application/queries/order_summary.py
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class OrderSummaryDTO:
    order_id: UUID
    customer_id: UUID
    total_amount: str
    status: str
    line_count: int
    created_at: str


class OrderSummaryQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT o.id, o.customer_id, o.status, o.created_at,
                       COALESCE(SUM(ol.quantity * ol.price_amount), 0) AS total,
                       COUNT(ol.id) AS line_count
                FROM orders o
                LEFT JOIN order_lines ol ON ol.order_id = o.id
                WHERE o.customer_id = :cid
                GROUP BY o.id, o.customer_id, o.status, o.created_at
                ORDER BY o.created_at DESC
            """),
            {"cid": str(customer_id)},
        ).fetchall()

        return [
            OrderSummaryDTO(
                order_id=row.id,
                customer_id=row.customer_id,
                total_amount=str(row.total),
                status=row.status,
                line_count=row.line_count,
                created_at=str(row.created_at),
            )
            for row in rows
        ]
```

### 5.6. Event Handlers

```python
# order/application/handlers/on_order_placed.py
from shop.order.domain.events.order_events import OrderPlaced


class SendOrderConfirmationEmail:
    def __init__(self, email_sender) -> None:
        self._email_sender = email_sender

    def handle(self, event: OrderPlaced) -> None:
        self._email_sender.send(
            to=f"customer-{event.customer_id}@example.com",
            subject=f"Xác nhận đơn hàng {event.order_id}",
            body=f"Tổng: {event.total_amount} {event.total_currency}",
        )
```

### 5.7. Infrastructure

```python
# order/infrastructure/persistence/orm_models.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class OrderBase(DeclarativeBase):
    pass


class OrderRow(OrderBase):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(20))
    tracking_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    lines: Mapped[list["OrderLineRow"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderLineRow(OrderBase):
    __tablename__ = "order_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"))
    product_sku: Mapped[str] = mapped_column(String(20))
    product_name: Mapped[str] = mapped_column(String(200))
    price_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    price_currency: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int]

    order: Mapped[OrderRow] = relationship(back_populates="lines")
```

```python
# order/infrastructure/persistence/mappers.py
from shop.order.domain.model.order import Order, OrderStatus
from shop.order.domain.model.order_line import OrderLine
from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.order.infrastructure.persistence.orm_models import (
    OrderRow, OrderLineRow,
)
from shop.shared.domain.money import Money


class OrderMapper:
    @staticmethod
    def to_domain(row: OrderRow) -> Order:
        lines = [
            OrderLine(
                id=line.id,
                snapshot=ProductSnapshot(
                    sku=line.product_sku,
                    name=line.product_name,
                    unit_price=Money(line.price_amount, line.price_currency),
                ),
                _quantity=line.quantity,
            )
            for line in row.lines
        ]
        return Order.reconstruct(
            order_id=row.id,
            customer_id=row.customer_id,
            status=OrderStatus(row.status),
            lines=lines,
            tracking_number=row.tracking_number,
            created_at=row.created_at,
        )

    @staticmethod
    def to_row(order: Order) -> OrderRow:
        return OrderRow(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            tracking_number=order.tracking_number,
            created_at=order.created_at,
            lines=[
                OrderLineRow(
                    id=line.id,
                    product_sku=line.snapshot.sku,
                    product_name=line.snapshot.name,
                    price_amount=line.snapshot.unit_price.amount,
                    price_currency=line.snapshot.unit_price.currency,
                    quantity=line.quantity,
                )
                for line in order.lines
            ],
        )
```

```python
# order/infrastructure/persistence/repositories.py
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from shop.order.domain.model.order import Order
from shop.order.infrastructure.persistence.mappers import OrderMapper
from shop.order.infrastructure.persistence.orm_models import OrderRow


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session, uow) -> None:
        self._session = session
        self._uow = uow

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderRow, order_id)
        return OrderMapper.to_domain(row) if row else None

    def save(self, order: Order) -> None:
        self._session.merge(OrderMapper.to_row(order))
        # Collect events từ aggregate
        self._uow.collect_events(order.pull_events())

    def next_id(self) -> UUID:
        return uuid4()
```

```python
# order/infrastructure/persistence/uow.py
from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from shop.order.infrastructure.persistence.repositories import (
    SqlAlchemyOrderRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session], event_bus) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._session: Session | None = None
        self._events: list = []

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session, self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()

    def collect_events(self, events: list) -> None:
        self._events.extend(events)

    def commit(self) -> None:
        assert self._session
        self._session.commit()
        # Publish events SAU commit
        for event in self._events:
            self._event_bus.publish(event)
        self._events.clear()

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()
        self._events.clear()
```

### 5.8. ACL — Catalog

```python
# order/infrastructure/acl/catalog_acl.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from shop.catalog.infrastructure.orm_models import ProductRow
from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.shared.domain.money import Money


class CatalogACL:
    """
    Anti-Corruption Layer — Order đọc Catalog qua ACL.

    Trong project thật, đây có thể là HTTP call.
    Demo này dùng chung DB, đọc qua SQLAlchemy.
    """
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_product_snapshot(self, sku: str) -> ProductSnapshot:
        row = (
            self._session.query(ProductRow)
            .filter(ProductRow.sku == sku.upper())
            .one_or_none()
        )
        if not row:
            raise ProductNotFound(sku)
        if not row.is_published:
            raise ProductNotPublished(sku)

        return ProductSnapshot(
            sku=row.sku,
            name=row.name,
            unit_price=Money(row.price_amount, row.price_currency),
        )


class ProductNotFound(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Sản phẩm {sku} không tồn tại")


class ProductNotPublished(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Sản phẩm {sku} chưa được publish")
```

### 5.9. Presentation

```python
# order/presentation/schemas.py
from uuid import UUID

from pydantic import BaseModel, Field


class OrderItemRequest(BaseModel):
    sku: str
    quantity: int = Field(gt=0, le=1000)


class PlaceOrderRequest(BaseModel):
    customer_id: UUID
    items: list[OrderItemRequest] = Field(min_length=1)


class PlaceOrderResponse(BaseModel):
    order_id: UUID
```

```python
# order/presentation/routes.py
from fastapi import APIRouter, Depends, HTTPException, status

from shop.order.application.commands.place_order import (
    OrderItemInput, PlaceOrderCommand, PlaceOrderHandler,
)
from shop.order.application.commands.cancel_order import (
    CancelOrderCommand, CancelOrderHandler, OrderNotFound,
)
from shop.order.infrastructure.acl.catalog_acl import (
    ProductNotFound, ProductNotPublished,
)
from shop.order.presentation.schemas import (
    PlaceOrderRequest, PlaceOrderResponse,
)
from shop.bootstrap import Container


router = APIRouter(prefix="/orders", tags=["orders"])


def get_container() -> Container:
    from shop.presentation.api.main import app
    return app.state.container


@router.post("", response_model=PlaceOrderResponse, status_code=201)
def place_order(
    request: PlaceOrderRequest,
    container: Container = Depends(get_container),
) -> PlaceOrderResponse:
    handler = container.make_place_order_handler()
    cmd = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[
            OrderItemInput(sku=i.sku, quantity=i.quantity)
            for i in request.items
        ],
    )
    try:
        order_id = handler.handle(cmd)
    except ProductNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProductNotPublished as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PlaceOrderResponse(order_id=order_id)


@router.post("/{order_id}/cancel", status_code=204)
def cancel_order(
    order_id: UUID,
    reason: str,
    container: Container = Depends(get_container),
) -> None:
    handler = container.make_cancel_order_handler()
    try:
        handler.handle(CancelOrderCommand(order_id=order_id, reason=reason))
    except OrderNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 6. Bootstrap — Composition Root

```python
# bootstrap.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shop.catalog.application.commands.create_product import CreateProductHandler
from shop.catalog.infrastructure.uow import (
    SqlAlchemyUnitOfWork as CatalogUoW,
)
from shop.catalog.infrastructure.in_memory.uow import (
    InMemoryUnitOfWork as CatalogInMemoryUoW,
)
from shop.order.application.commands.place_order import PlaceOrderHandler
from shop.order.application.commands.cancel_order import CancelOrderHandler
from shop.order.application.handlers.on_order_placed import (
    SendOrderConfirmationEmail,
)
from shop.order.application.queries.order_summary import OrderSummaryQuery
from shop.order.domain.events.order_events import OrderPlaced
from shop.order.infrastructure.acl.catalog_acl import CatalogACL
from shop.order.infrastructure.persistence.uow import (
    SqlAlchemyUnitOfWork as OrderUoW,
)
from shop.order.infrastructure.in_memory.uow import (
    InMemoryUnitOfWork as OrderInMemoryUoW,
)
from shop.notification.email_sender import ConsoleEmailSender
from shop.shared.events.event_bus import InMemoryEventBus


class Container:
    def __init__(self, db_url: str, environment: str = "production") -> None:
        self._environment = environment
        self._db_url = db_url

        if environment == "test":
            self._setup_test()
        else:
            self._setup_production()

        self._setup_event_handlers()

    def _setup_test(self) -> None:
        self._catalog_uow_factory = CatalogInMemoryUoW
        self._order_uow_factory = OrderInMemoryUoW
        self._email_sender = ConsoleEmailSender()
        self._event_bus = InMemoryEventBus()
        self._session_factory = None

    def _setup_production(self) -> None:
        engine = create_engine(self._db_url)
        self._session_factory = sessionmaker(bind=engine)
        self._event_bus = InMemoryEventBus()
        self._email_sender = ConsoleEmailSender()

        def catalog_uow():
            return CatalogUoW(self._session_factory)

        def order_uow():
            return OrderUoW(self._session_factory, self._event_bus)

        self._catalog_uow_factory = catalog_uow
        self._order_uow_factory = order_uow

    def _setup_event_handlers(self) -> None:
        handler = SendOrderConfirmationEmail(self._email_sender)
        self._event_bus.subscribe(OrderPlaced, handler.handle)

    # ---- Factories ----
    def make_create_product_handler(self) -> CreateProductHandler:
        return CreateProductHandler(uow=self._catalog_uow_factory())

    def make_place_order_handler(self) -> PlaceOrderHandler:
        assert self._session_factory is not None or self._environment == "test"
        if self._environment == "test":
            # Trong test, ACL dùng in-memory khác
            from shop.order.infrastructure.in_memory.catalog_acl import (
                InMemoryCatalogACL,
            )
            catalog_port = InMemoryCatalogACL()
        else:
            session = self._session_factory()
            catalog_port = CatalogACL(session)

        return PlaceOrderHandler(
            uow=self._order_uow_factory(),
            catalog_port=catalog_port,
        )

    def make_cancel_order_handler(self) -> CancelOrderHandler:
        return CancelOrderHandler(uow=self._order_uow_factory())
```

---

## 7. FastAPI App

```python
# presentation/api/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shop.bootstrap import Container
from shop.catalog.presentation.routes import router as catalog_router
from shop.order.presentation.routes import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.container = Container(
        db_url="postgresql://user:pass@localhost/shop",
        environment="production",
    )
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shop API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(catalog_router)
    app.include_router(order_router)
    return app


app = create_app()
```

---

## 8. Tests

### 8.1. Unit test — Domain

```python
# tests/unit/order/test_order.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.order.domain.model.order import Order, OrderStatus
from shop.order.domain.model.order_line import OrderLine
from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.order.domain.exceptions import (
    EmptyOrderCannotBePlaced, OrderNotEditable, InvalidTransition,
)
from shop.shared.domain.money import Money


def make_line(price: str = "100", qty: int = 1) -> OrderLine:
    return OrderLine.create(
        snapshot=ProductSnapshot(
            sku="SKU001",
            name="Book",
            unit_price=Money(Decimal(price), "VND"),
        ),
        quantity=qty,
    )


class TestOrderInvariants:
    def test_empty_order_cannot_be_placed(self) -> None:
        order = Order.create(uuid4())
        with pytest.raises(EmptyOrderCannotBePlaced):
            order.place()

    def test_total_computed_correctly(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line("100", 2))
        order.add_line(make_line("200", 3))
        assert order.total == Money(Decimal("800"), "VND")

    def test_cannot_add_line_after_placed(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        with pytest.raises(OrderNotEditable):
            order.add_line(make_line())

    def test_valid_transition(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        order.ship("TRACK123")
        order.deliver()
        assert order.status == OrderStatus.DELIVERED

    def test_invalid_transition(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        with pytest.raises(InvalidTransition):
            order.ship("TRACK")


class TestOrderEvents:
    def test_place_emits_event(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.pull_events()
        order.place()
        events = order.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "OrderPlaced"
```

### 8.2. Unit test — Application Handler

```python
# tests/unit/order/test_place_order_handler.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.order.application.commands.place_order import (
    OrderItemInput, PlaceOrderCommand, PlaceOrderHandler,
)
from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.order.infrastructure.in_memory.uow import InMemoryUnitOfWork
from shop.shared.domain.money import Money
from tests.fakes.catalog import FakeCatalogPort


class TestPlaceOrderHandler:
    def test_place_order_success(self) -> None:
        # Arrange
        catalog = FakeCatalogPort({
            "SKU001": ProductSnapshot(
                sku="SKU001",
                name="Book",
                unit_price=Money(Decimal("100"), "VND"),
            ),
        })
        uow = InMemoryUnitOfWork()
        handler = PlaceOrderHandler(uow, catalog)

        cmd = PlaceOrderCommand(
            customer_id=uuid4(),
            items=[OrderItemInput(sku="SKU001", quantity=2)],
        )

        # Act
        order_id = handler.handle(cmd)

        # Assert
        order = uow.orders.find_by_id(order_id)
        assert order is not None
        assert order.total == Money(Decimal("200"), "VND")
```

### 8.3. E2E test

```python
# tests/e2e/test_api.py
import pytest
from fastapi.testclient import TestClient

from shop.presentation.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    app.state.container = Container(db_url="", environment="test")
    return TestClient(app)


class TestCatalogAPI:
    def test_create_product(self, client: TestClient) -> None:
        response = client.post("/catalog/products", json={
            "sku": "SKU001",
            "name": "Book",
            "price_amount": "100",
            "price_currency": "VND",
        })
        assert response.status_code == 201
        assert "product_id" in response.json()

    def test_duplicate_sku_returns_409(self, client: TestClient) -> None:
        payload = {
            "sku": "SKU002",
            "name": "Book",
            "price_amount": "100",
            "price_currency": "VND",
        }
        client.post("/catalog/products", json=payload)
        response = client.post("/catalog/products", json=payload)
        assert response.status_code == 409


class TestOrderAPI:
    def test_place_order(self, client: TestClient) -> None:
        # First create a product
        client.post("/catalog/products", json={
            "sku": "SKU003",
            "name": "Book",
            "price_amount": "100",
            "price_currency": "VND",
        })

        response = client.post("/orders", json={
            "customer_id": str(uuid4()),
            "items": [{"sku": "SKU003", "quantity": 2}],
        })
        assert response.status_code == 201
        assert "order_id" in response.json()
```

---

## 9. pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shop"
version = "1.0.0"
description = "DDD E-commerce example"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "pydantic>=2.5",
    "psycopg[binary]>=3.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
    "httpx>=0.26",
    "mypy>=1.7",
    "ruff>=0.1",
    "import-linter>=2.0",
]

[project.scripts]
shop = "shop.__main__:main"

[tool.hatch.build.targets.wheel]
packages = ["src/shop"]

# ---------- mypy ----------
[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
disallow_any_generics = true
disallow_untyped_defs = true
no_implicit_optional = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
ignore_errors = true

# ---------- pytest ----------
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short --strict-markers"

# ---------- coverage ----------
[tool.coverage.run]
source = ["src/shop"]
omit = ["*/tests/*", "*/__main__.py", "*/migrations/*"]

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
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM", "RUF"]
ignore = ["E501", "B008"]

# ---------- import-linter ----------
[tool.importlinter]
root_packages = ["shop"]

[[tool.importlinter.contracts]]
name = "Shared Kernel không import context"
type = "forbidden"
source_modules = ["shop.shared"]
forbidden_modules = ["shop.catalog", "shop.order", "shop.notification"]

[[tool.importlinter.contracts]]
name = "Catalog domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.order", "shop.notification"]
forbidden_modules = ["shop.catalog.domain"]

[[tool.importlinter.contracts]]
name = "Order domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.catalog", "shop.notification"]
forbidden_modules = ["shop.order.domain"]

[[tool.importlinter.contracts]]
name = "Notification domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.catalog", "shop.order"]
forbidden_modules = ["shop.notification"]

[[tool.importlinter.contracts]]
name = "Domain không phụ thuộc Infrastructure/Presentation"
type = "forbidden"
source_modules = ["shop.catalog.domain", "shop.order.domain"]
forbidden_modules = [
    "shop.catalog.infrastructure",
    "shop.order.infrastructure",
    "shop.catalog.presentation",
    "shop.order.presentation",
]
```

---

## 10. Makefile

```makefile
.PHONY: install lint typecheck imports test cov check clean run migrate

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/

imports:
	lint-imports

test:
	pytest

cov:
	pytest --cov=src/shop --cov-report=html --cov-report=term-missing

check: lint typecheck imports test
	@echo "✅ All checks passed!"

run:
	uvicorn shop.presentation.api.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 11. Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source
COPY src/ ./src/
COPY migrations/ ./migrations/

# Run
EXPOSE 8000
CMD ["uvicorn", "shop.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: shop
      POSTGRES_PASSWORD: shop
      POSTGRES_DB: shop
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://shop:shop@db:5432/shop
    ports:
      - "8000:8000"
    depends_on:
      - db
    command: >
      sh -c "alembic upgrade head &&
             uvicorn shop.presentation.api.main:app --host 0.0.0.0 --port 8000"

volumes:
  postgres_data:
```

---

## 12. CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint (ruff)
        run: |
          ruff check src/ tests/
          ruff format --check src/ tests/

      - name: Type check (mypy)
        run: mypy src/

      - name: Architecture (import-linter)
        run: lint-imports

      - name: Test
        run: pytest --cov=src/shop --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
```

---

## 13. Cách chạy

```bash
# 1. Clone repo
git clone <repo>
cd shop

# 2. Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Chạy DB
docker-compose up -d db

# 4. Migrate
alembic upgrade head

# 5. Kiểm tra chất lượng
make check

# 6. Chạy API
make run
# → http://localhost:8000/docs
```

---

## 14. Cách mở rộng project

Bạn có thể thêm:

### 14.1. Thêm context mới

Ví dụ `Payment`:

```
src/shop/payment/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

Thêm import-linter contract.

### 14.2. Thêm Event Sourcing

Chuyển `Order` sang Event Sourced:

- Tạo `event_store`.
- Sửa `Order` thành `EventSourcedAggregate`.
- Thêm snapshot.

### 14.3. Thêm CQRS nặng

- Tạo read model riêng.
- Projection update qua event.
- Query đọc read model.

### 14.4. Thêm Outbox Pattern

- Lưu event vào bảng `outbox` trong cùng transaction.
- Worker publish event ra message queue.
- Đảm bảo không mất event.

### 14.5. Thêm Authentication

- JWT token.
- Middleware check auth.
- Application handler check permission.

---

## 15. Bài tập về nhà — Bài cuối

### 🔴 Bài tập 1: Mở rộng project

Thêm context `Payment`:

**Domain:**

- Aggregate `Payment`.
- Events: `PaymentInitiated`, `PaymentCompleted`, `PaymentFailed`, `Refunded`.
- States: PENDING → COMPLETED / FAILED → REFUNDED.

**Application:**

- Command: `InitiatePayment`, `CompletePayment`, `RefundPayment`.
- Query: `PaymentHistory`.
- Handler: khi `OrderPlaced` → `InitiatePayment`.

**Yêu cầu:**

1. Tuân thủ DDD + 4 tầng.
2. ACL từ Payment → Order.
3. Setup import-linter chặn.
4. Test đầy đủ.
5. Cập nhật CI.

### 🔴 Bài tập 2: Chuyển sang Event Sourcing

Chuyển `Order` aggregate sang Event Sourcing:

1. Viết `EventStore` (in-memory + SQLAlchemy).
2. Chuyển `Order` thành `EventSourcedAggregate`.
3. Thêm `snapshot`.
4. Repository load từ event store.
5. Test:
   - Replay events.
   - Concurrency.
   - Snapshot.

### 🔴 Bài tập 3: Deploy production

1. Setup CI/CD hoàn chỉnh.
2. Deploy lên một platform (Railway, Fly.io, AWS...).
3. Setup database production (Postgres).
4. Setup monitoring (Sentry, Prometheus).
5. Setup logging.
6. Viết `docs/`:
   - Architecture diagram.
   - Context map.
   - API docs.
   - Deployment guide.

Bonus: Setup **Blue-Green Deployment**.

---

## 16. Checklist sau bài 18

Bạn đã có:

- [ ] Project Python với cấu trúc DDD đầy đủ.
- [ ] 2-3 Bounded Context tách biệt.
- [ ] Domain model với VO, Entity, Aggregate, Event.
- [ ] Repository Protocol ở Domain, impl ở Infrastructure.
- [ ] Unit of Work.
- [ ] CQRS (Command + Query).
- [ ] Event bus + Event handler.
- [ ] ACL giữa các context.
- [ ] Composition Root.
- [ ] FastAPI presentation.
- [ ] SQLAlchemy infrastructure.
- [ ] Test đầy đủ (unit + integration + e2e).
- [ ] CI/CD.
- [ ] Docker.
- [ ] Makefile.
- [ ] Enforce bằng import-linter.
- [ ] Type check với mypy strict.
- [ ] Lint với ruff.

**Đây là template production-ready.** Bạn có thể copy để bắt đầu dự án mới.

---

## 17. Tổng kết toàn bộ lộ trình

### 17.1. Những gì bạn đã học

**Level 1 — Nền tảng:**

1. DDD là gì.
2. Ubiquitous Language.
3. Python + DDD.
4. Bounded Context.

**Level 2 — Building Blocks:**

5. Value Object.
6. Entity.
7. Aggregate.
8. Domain Event.
9. Repository + UoW.

**Level 3 — Kiến trúc:**

10. Layered Architecture.
11. Application Service & CQRS.
12. Domain Service & Specification.
13. Dependency Injection.

**Level 4 — Chiến lược:**

14. Context Mapping.
15. Event Storming.
16. Chiến lược chọn Bounded Context.

**Level 5 — Chuyên sâu:**

17. Event Sourcing.
18. Project hoàn chỉnh.

### 17.2. Kỹ năng bạn có

- **Tư duy DDD:** Nhìn hệ thống qua lăng kính domain.
- **Tactical DDD:** VO, Entity, Aggregate, Event, Repository.
- **Strategic DDD:** Bounded Context, Context Map, Event Storming.
- **Kiến trúc:** 4 tầng, CQRS, DI, Hexagonal.
- **Python:** dataclass, Protocol, type hints, async.
- **Tooling:** mypy, ruff, pytest, import-linter.
- **Patterns:** Repository, UoW, ACL, Specification, Saga.
- **Advanced:** Event Sourcing, Snapshot, Projection.

### 17.3. Bước tiếp theo

**1. Áp dụng vào dự án thật.**

- Chọn 1 dự án.
- Bắt đầu với Bounded Context.
- Áp dụng dần tactical DDD.

**2. Đọc sách.**

- "Domain-Driven Design" — Eric Evans.
- "Implementing Domain-Driven Design" — Vaughn Vernon.
- "Architecture Patterns with Python" — Percival & Gregory.
- "Learning Domain-Driven Design" — Vlad Khononov.

**3. Học thêm.**

- Event Sourcing nâng cao.
- Saga pattern.
- CQRS với Kafka.
- Microservices patterns.

**4. Tham gia cộng đồng.**

- DDD Europe.
- Python Discord.
- Local meetups.

---

## 18. Lời kết

Bạn đã đi qua **18 bài học** — từ "DDD là gì" đến "project production-ready". Đây là **hành trình dài** — nhiều người bỏ cuộc giữa chừng. Bạn đã đi hết.

**Nhớ 3 điều:**

1. **DDD không phải đích đến, mà là hành trình.** Không có project nào "hoàn hảo DDD" từ đầu. Cứ cải thiện dần.

2. **Không cần áp dụng mọi thứ.** Chọn những gì phù hợp với dự án. DDD là **công cụ**, không phải **tôn giáo**.

3. **Domain là trung tâm.** Mọi thứ khác (framework, DB, UI) chỉ là **chi tiết kỹ thuật**. Đừng để chúng dominate.

**Câu thần chú cuối cùng:**

> *"Code phải phản ánh nghiệp vụ. Domain là trái tim. Mọi thứ khác là chi tiết."*

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Review project** của bạn — nếu bạn implement, tôi sẽ review.
2. **Đào sâu** một phần: Event Sourcing, Saga, CQRS với Kafka, Microservices.
3. **Viết code mẫu** cho bài tập nào đó.
4. **Giải thích lại** phần nào bạn chưa hiểu.
5. **Đề xuất lộ trình tiếp theo** (sách, khóa học, dự án thực tế).

Chúc mừng bạn đã hoàn thành **18 bài DDD Python**! 🎉

Bạn đã sẵn sàng áp dụng DDD vào dự án thật. Nếu cần hỗ trợ thêm, tôi luôn ở đây.