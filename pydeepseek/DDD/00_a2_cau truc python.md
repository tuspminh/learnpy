# 🐍 Cấu trúc DDD áp dụng trong lập trình Python

Sau khi đã có roadmap, giờ ta đi vào **cấu trúc cụ thể** — tức là **cây thư mục, file nào chứa gì, dependency đi theo hướng nào**, và **code mẫu từng layer**. Đây là phần "xương sống" bạn sẽ dùng cho mọi project DDD Python.

---

## 1. Nguyên tắc gốc — Dependency Rule

Trước khi nhìn cấu trúc, phải khắc cốt nguyên tắc:

```
        ┌─────────────────────────────────────────┐
        │  Presentation (FastAPI, CLI, gRPC)      │
        └────────────────┬────────────────────────┘
                         │ depends on
                         ▼
        ┌─────────────────────────────────────────┐
        │  Application (Use Cases, Handlers)      │
        └────────────────┬────────────────────────┘
                         │ depends on
                         ▼
        ┌─────────────────────────────────────────┐
        │  DOMAIN  (Entities, VO, Events,         │
        │           Aggregates, Repo Protocol)    │  ← TRÁI TIM
        └────────────────▲────────────────────────┘
                         │ implements
        ┌────────────────┴────────────────────────┐
        │  Infrastructure (DB, HTTP, Email, MQ)   │
        └─────────────────────────────────────────┘
```

> **Quy tắc vàng:** Mũi tên **chỉ đi vào Domain**, không bao giờ đi ra.
> Domain **không biết** FastAPI, không biết SQLAlchemy, không biết Redis.

Trong Python điều này dễ bị phá vỡ vì không có compiler. → Dùng `import-linter` để enforce.

---

## 2. Cấu trúc thư mục chuẩn (chuẩn "Cosmic Python")

Đây là cấu trúc tôi dùng cho **99% project DDD Python**:

```
shop/
├── pyproject.toml
├── src/
│   └── shop/
│       ├── __init__.py
│       │
│       ├── domain/                    # ⭐ TRÁI TIM
│       │   ├── __init__.py
│       │   ├── model/
│       │   │   ├── __init__.py
│       │   │   ├── order.py           # Aggregate Root
│       │   │   ├── order_line.py      # Entity con
│       │   │   ├── customer.py        # Entity
│       │   │   ├── money.py           # Value Object
│       │   │   └── email.py           # Value Object
│       │   ├── events/
│       │   │   ├── __init__.py
│       │   │   └── order_events.py    # Domain Events
│       │   ├── services/
│       │   │   └── pricing_service.py # Domain Service
│       │   ├── repositories/          # CHỈ Protocol
│       │   │   ├── __init__.py
│       │   │   ├── order_repository.py
│       │   │   └── customer_repository.py
│       │   ├── specs/                 # Specification
│       │   │   └── order_specs.py
│       │   └── exceptions.py
│       │
│       ├── application/               # ORCHESTRATION
│       │   ├── __init__.py
│       │   ├── commands/
│       │   │   ├── place_order.py     # Command + Handler
│       │   │   └── cancel_order.py
│       │   ├── queries/
│       │   │   └── order_summary.py   # Query + DTO
│       │   ├── dto.py
│       │   ├── ports/                 # Interface cho external
│       │   │   ├── email_sender.py
│       │   │   └── payment_gateway.py
│       │   └── uow.py                 # Unit of Work Protocol
│       │
│       ├── infrastructure/            # KỸ THUẬT
│       │   ├── __init__.py
│       │   ├── persistence/
│       │   │   ├── sqlalchemy/
│       │   │   │   ├── orm_models.py  # Bảng DB
│       │   │   │   ├── mapper.py      # Domain ↔ ORM
│       │   │   │   ├── repositories.py
│       │   │   │   └── uow.py
│       │   │   └── in_memory/         # Cho test
│       │   │       ├── repositories.py
│       │   │       └── uow.py
│       │   ├── email/
│       │   │   └── smtp_sender.py
│       │   ├── payment/
│       │   │   └── stripe_gateway.py
│       │   └── messaging/
│       │       └── in_memory_bus.py
│       │
│       ├── presentation/              # GIAO TIẾP
│       │   ├── __init__.py
│       │   ├── api/
│       │   │   ├── main.py            # FastAPI app
│       │   │   ├── routes/
│       │   │   │   └── orders.py
│       │   │   ├── schemas.py         # Pydantic request/response
│       │   │   └── dependencies.py    # DI cho FastAPI
│       │   └── cli/
│       │       └── commands.py
│       │
│       └── bootstrap.py               # Composition Root
│
└── tests/
    ├── unit/
    │   └── domain/
    ├── integration/
    │   └── infrastructure/
    └── e2e/
        └── api/
```

> 💡 **Tại sao dùng `src/shop/`** thay vì `shop/`? Để tránh import nhầm package khi test. Đây là best practice Python hiện đại.

---

## 3. Chi tiết từng Layer

### 3.1. Domain Layer — không phụ thuộc ai

#### Value Object

```python
# domain/model/money.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money không thể âm")
        if len(self.currency) != 3:
            raise ValueError("Currency phải là ISO 4217")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        return Money(self.amount * factor, self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
```

→ **Không import gì ngoài stdlib.** Đây là dấu hiệu VO đúng.

#### Entity + Aggregate Root

```python
# domain/model/order.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from shop.domain.model.money import Money
from shop.domain.events.order_events import (
    OrderPlaced, OrderLineAdded, OrderLineRemoved, OrderCancelled,
)
from shop.domain.exceptions import (
    OrderNotEditable, EmptyOrderCannotBePlaced, InvalidQuantity,
)


class OrderLine:
    """Entity con — KHÔNG có repository riêng."""
    def __init__(self, line_id: UUID, product_id: UUID, price: Money, quantity: int):
        if quantity <= 0:
            raise InvalidQuantity()
        self._id = line_id
        self._product_id = product_id
        self._price = price
        self._quantity = quantity

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def subtotal(self) -> Money:
        return self._price * Decimal(self._quantity)

    def change_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise InvalidQuantity()
        self._quantity = new_qty


class Order:
    """AGGREGATE ROOT — cổng vào duy nhất."""
    MAX_LINES = 50

    def __init__(self, order_id: UUID, customer_id: UUID):
        self._id = order_id
        self._customer_id = customer_id
        self._lines: dict[UUID, OrderLine] = {}
        self._status = "DRAFT"
        self._events: list = []
        self._created_at = datetime.now()

    # ---------- Identity ----------
    @property
    def id(self) -> UUID:
        return self._id

    # ---------- Behavior ----------
    def add_product(self, product_id: UUID, price: Money, quantity: int) -> UUID:
        self._ensure_editable()
        if len(self._lines) >= self.MAX_LINES:
            raise ValueError("Vượt quá số line tối đa")

        line_id = uuid4()
        self._lines[line_id] = OrderLine(line_id, product_id, price, quantity)
        self._events.append(OrderLineAdded(self._id, line_id))
        return line_id

    def remove_line(self, line_id: UUID) -> None:
        self._ensure_editable()
        if line_id not in self._lines:
            raise ValueError(f"Line {line_id} không tồn tại")
        del self._lines[line_id]
        self._events.append(OrderLineRemoved(self._id, line_id))

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced()
        self._status = "PLACED"
        self._events.append(OrderPlaced(self._id, self._customer_id, self.total))

    def cancel(self, reason: str) -> None:
        if self._status == "CANCELLED":
            raise ValueError("Đã cancel rồi")
        self._status = "CANCELLED"
        self._events.append(OrderCancelled(self._id, reason))

    # ---------- Query ----------
    @property
    def total(self) -> Money:
        return sum(
            (line.subtotal for line in self._lines.values()),
            Money(Decimal("0"), "USD"),
        )

    @property
    def status(self) -> str:
        return self._status

    # ---------- Internal ----------
    def _ensure_editable(self) -> None:
        if self._status != "DRAFT":
            raise OrderNotEditable()

    # ---------- Event collection ----------
    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
```

#### Repository Protocol (chỉ interface)

```python
# domain/repositories/order_repository.py
from typing import Protocol
from uuid import UUID
from shop.domain.model.order import Order

class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def next_id(self) -> UUID: ...
```

> ⚠️ **Chú ý:** file này **chỉ chứa `Protocol`**. Không có code SQL. Không có `import sqlalchemy`.

#### Domain Event

```python
# domain/events/order_events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from shop.domain.model.money import Money

@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = None
    customer_id: UUID = None
    total: Money = None

@dataclass(frozen=True)
class OrderLineAdded(DomainEvent):
    order_id: UUID = None
    line_id: UUID = None
```

---

### 3.2. Application Layer — orchestration, không chứa business rule

#### Unit of Work Protocol

```python
# application/uow.py
from typing import Protocol
from shop.domain.repositories.order_repository import OrderRepository

class UnitOfWork(Protocol):
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *args) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

#### Command + Handler

```python
# application/commands/place_order.py
from dataclasses import dataclass
from uuid import UUID
from shop.application.uow import UnitOfWork
from shop.domain.model.order import Order
from shop.domain.model.money import Money

@dataclass(frozen=True)
class OrderItemDTO:
    product_id: UUID
    price: Money
    quantity: int

@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemDTO]

class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order(self._uow.orders.next_id(), cmd.customer_id)
            for item in cmd.items:
                order.add_product(item.product_id, item.price, item.quantity)
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

#### Port (interface cho external service)

```python
# application/ports/email_sender.py
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...
```

#### Query — có thể đi thẳng DB

```python
# application/queries/order_summary.py
from dataclasses import dataclass
from uuid import UUID
from typing import Protocol

@dataclass(frozen=True)
class OrderSummaryDTO:
    order_id: UUID
    total: str
    status: str

class OrderSummaryReader(Protocol):
    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]: ...
```

→ **Query không cần Aggregate.** Chỉ cần DTO cho UI.

---

### 3.3. Infrastructure Layer — implementation cụ thể

#### ORM Model (khác Domain Model!)

```python
# infrastructure/persistence/sqlalchemy/orm_models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, String
from uuid import UUID

class Base(DeclarativeBase):
    pass

class OrderRow(Base):
    __tablename__ = "orders"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    customer_id: Mapped[UUID]
    status: Mapped[str] = mapped_column(String(20))
    lines: Mapped[list["OrderLineRow"]] = relationship(cascade="all, delete-orphan")

class OrderLineRow(Base):
    __tablename__ = "order_lines"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[UUID]
    price_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int]
```

> 🔑 **Nguyên tắc:** ORM model **KHÁC** Domain model. Đừng gộp chung (sẽ phá vỡ mọi thứ).

#### Mapper (chuyển đổi 2 chiều)

```python
# infrastructure/persistence/sqlalchemy/mapper.py
from shop.domain.model.order import Order, OrderLine
from shop.domain.model.money import Money
from .orm_models import OrderRow, OrderLineRow

def to_domain(row: OrderRow) -> Order:
    order = Order(row.id, row.customer_id)
    for line_row in row.lines:
        order.add_product(
            line_row.product_id,
            Money(line_row.price_amount, line_row.currency),
            line_row.quantity,
        )
    order._status = row.status  # hack — hoặc dùng method reconstruct
    order.pull_events()         # bỏ event cũ
    return order

def to_row(order: Order) -> OrderRow:
    return OrderRow(
        id=order.id,
        customer_id=order._customer_id,
        status=order.status,
        lines=[
            OrderLineRow(
                id=line.id,
                product_id=line._product_id,
                price_amount=line._price.amount,
                currency=line._price.currency,
                quantity=line._quantity,
            )
            for line in order._lines.values()
        ],
    )
```

#### Repository implementation

```python
# infrastructure/persistence/sqlalchemy/repositories.py
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from shop.domain.model.order import Order
from shop.domain.repositories.order_repository import OrderRepository
from .orm_models import OrderRow
from .mapper import to_domain, to_row

class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderRow, order_id)
        return to_domain(row) if row else None

    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))

    def next_id(self) -> UUID:
        return uuid4()
```

#### Unit of Work

```python
# infrastructure/persistence/sqlalchemy/uow.py
from sqlalchemy.orm import Session
from .repositories import SqlAlchemyOrderRepository

class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session: Session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session)
        return self

    def __exit__(self, exc_type, *args):
        if exc_type:
            self.rollback()
        self._session.close()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
```

#### In-memory (cho test)

```python
# infrastructure/persistence/in_memory/uow.py
from copy import deepcopy
from uuid import UUID, uuid4
from shop.domain.model.order import Order

class InMemoryOrderRepository:
    def __init__(self):
        self._store: dict[UUID, Order] = {}

    def find_by_id(self, order_id: UUID) -> Order | None:
        return deepcopy(self._store.get(order_id))

    def save(self, order: Order) -> None:
        self._store[order.id] = deepcopy(order)

    def next_id(self) -> UUID:
        return uuid4()

class InMemoryUnitOfWork:
    def __init__(self):
        self.orders = InMemoryOrderRepository()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def commit(self): ...
    def rollback(self): ...
```

---

### 3.4. Presentation Layer — FastAPI

```python
# presentation/api/schemas.py
from pydantic import BaseModel
from uuid import UUID

class OrderItemSchema(BaseModel):
    product_id: UUID
    price: str       # "10.00"
    currency: str    # "USD"
    quantity: int

class PlaceOrderRequest(BaseModel):
    customer_id: UUID
    items: list[OrderItemSchema]

class PlaceOrderResponse(BaseModel):
    order_id: UUID
```

```python
# presentation/api/routes/orders.py
from decimal import Decimal
from fastapi import APIRouter, Depends, status
from shop.application.commands.place_order import (
    PlaceOrderCommand, PlaceOrderHandler, OrderItemDTO,
)
from shop.domain.model.money import Money
from shop.presentation.api.dependencies import get_place_order_handler
from .schemas import PlaceOrderRequest, PlaceOrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=PlaceOrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
) -> PlaceOrderResponse:
    cmd = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[
            OrderItemDTO(
                product_id=i.product_id,
                price=Money(Decimal(i.price), i.currency),
                quantity=i.quantity,
            )
            for i in request.items
        ],
    )
    order_id = handler.handle(cmd)
    return PlaceOrderResponse(order_id=order_id)
```

```python
# presentation/api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from shop.application.commands.place_order import PlaceOrderHandler
from shop.infrastructure.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork

_session_factory: sessionmaker | None = None

def configure(session_factory: sessionmaker) -> None:
    global _session_factory
    _session_factory = session_factory

def get_place_order_handler() -> PlaceOrderHandler:
    uow = SqlAlchemyUnitOfWork(_session_factory)
    return PlaceOrderHandler(uow)
```

---

### 3.5. Composition Root — nơi mọi thứ ráp lại

```python
# bootstrap.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shop.presentation.api.dependencies import configure

def bootstrap(db_url: str) -> None:
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    configure(session_factory)
```

```python
# presentation/api/main.py
from fastapi import FastAPI
from shop.bootstrap import bootstrap
from shop.presentation.api.routes import orders

bootstrap("postgresql://user:pass@localhost/shop")
app = FastAPI(title="Shop API")
app.include_router(orders.router)
```

---

## 4. Luồng đi của một request

```
HTTP POST /orders
       │
       ▼
[FastAPI route]                          ← presentation
       │ parse request → PlaceOrderCommand
       ▼
[PlaceOrderHandler.handle]               ← application
       │ mở UoW
       │ tạo Order, add_product, place
       ▼
[Order / OrderLine]                      ← DOMAIN (business rule)
       │ phát event
       ▼
[SqlAlchemyOrderRepository.save]         ← infrastructure
       │ map Domain → ORM
       │ session.commit()
       ▼
[EventBus.publish]                       ← application hoặc infra
       │
       ▼
[SendOrderConfirmationEmail]             ← event handler
```

**Chú ý:** Domain ở giữa, **không import gì** từ FastAPI/SQLAlchemy/Redis.

---

## 5. Kiểm tra dependency bằng `import-linter`

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["shop"]

[[tool.importlinter.contracts]]
name = "Domain không phụ thuộc ai"
type = "forbidden"
source_modules = ["shop.domain"]
forbidden_modules = [
    "shop.application",
    "shop.infrastructure",
    "shop.presentation",
]

[[tool.importlinter.contracts]]
name = "Application không phụ thuộc Infrastructure hay Presentation"
type = "forbidden"
source_modules = ["shop.application"]
forbidden_modules = ["shop.infrastructure", "shop.presentation"]

[[tool.importlinter.contracts]]
name = "Presentation không bị import bởi layer khác"
type = "forbidden"
source_modules = ["shop.domain", "shop.application", "shop.infrastructure"]
forbidden_modules = ["shop.presentation"]
```

Chạy:
```bash
pip install import-linter
lint-imports
```

Nếu ai đó lỡ `from sqlalchemy import ...` trong `domain/` → **build fail ngay**.

---

## 6. Quy tắc viết code trong từng layer

| Layer | Được import | KHÔNG được import | Nhiệm vụ |
|-------|-------------|-------------------|----------|
| **Domain** | stdlib, chính nó | Mọi thứ khác | Business rule |
| **Application** | Domain, stdlib | Infra, Presentation | Orchestration |
| **Infrastructure** | Domain, Application, libs | Presentation | Implementation |
| **Presentation** | Application, Domain (chỉ DTO), libs | Infrastructure trực tiếp | HTTP/CLI |

---

## 7. Checklist khi tạo project DDD Python

- [ ] Dùng `src/shop/` layout
- [ ] `mypy --strict` bật trong pyproject
- [ ] Domain không có import nào ngoài stdlib
- [ ] Repository là `Protocol`, không phải ABC
- [ ] ORM Model **KHÁC** Domain Model
- [ ] Có `InMemoryUnitOfWork` cho test
- [ ] `import-linter` chạy trong CI
- [ ] Application handler **không** gọi trực tiếp DB — luôn qua UoW
- [ ] Event được `pull_events()` sau khi save
- [ ] Query đi thẳng read model, không qua Aggregate

---

## 8. Anti-patterns thường gặp của Python dev

| ❌ Anti-pattern | ✅ Cách đúng |
|----------------|--------------|
| Dùng chung SQLAlchemy model cho Domain | Tách 2 model + mapper |
| Domain import `sqlalchemy` | Repository Protocol ở Domain |
| Aggregate Root có setter public | Chỉ có method behavior |
| `OrderLine` có repository riêng | Chỉ AR có repository |
| Application handler chứa `if/else` business | Đẩy rule vào Domain |
| Dùng `@dataclass` cho Entity (không cần) | Class thường + `__eq__` theo ID |
| VO không `frozen=True` | Luôn `frozen=True` |
| Pydantic schema lọt vào Domain | Pydantic chỉ ở Presentation |

---

## 9. Bạn muốn đi tiếp phần nào?

1. **Code đầy đủ 1 project hoàn chỉnh** (shop với Order + Customer + Payment) — tôi viết từng file.
2. **So sánh với Clean Architecture / Hexagonal** — khi nào dùng cái nào.
3. **Event Sourcing structure** — cấu trúc khác gì so với CRUD-based.
4. **Testing strategy** trong DDD Python — unit, integration, e2e.
5. **Chuyển từ monolith sang microservices** — khi nào, cấu trúc ra sao.

👉 Nói tôi biết bạn muốn phần nào, tôi sẽ viết chi tiết với code Python đầy đủ.