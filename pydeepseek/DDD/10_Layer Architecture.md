# 📖 Bài 10: Layered Architecture trong Python

> Chúc mừng bạn đã hoàn thành Level 2 — bạn đã có đủ **building blocks** (VO, Entity, Aggregate, Event, Repository, UoW). Giờ là lúc **lắp ráp chúng** thành một kiến trúc hoàn chỉnh. Bài này dạy bạn **4 tầng**, **dependency rule**, và cách **enforce** kiến trúc đó bằng tooling.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Layered Architecture** là gì và tại sao cần.
2. Nắm rõ **4 tầng**: Presentation, Application, Domain, Infrastructure.
3. Hiểu **Dependency Rule** — mũi tên chỉ đi vào Domain.
4. Biết **khi nào dùng gì** ở mỗi tầng.
5. Phân biệt **Layered** vs **Hexagonal** vs **Clean** vs **Onion**.
6. Tổ chức **project Python** đúng chuẩn.
7. **Enforce** kiến trúc bằng `import-linter` để không ai phá vỡ.
8. Tránh được **8 anti-pattern** về kiến trúc.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Tại sao cần kiến trúc phân tầng?

### 1.1. Vấn đề khi không có kiến trúc

Hãy tưởng tượng một project Python **không có kiến trúc**:

```
shop_app/
├── models.py          # SQLAlchemy models
├── views.py           # FastAPI routes, gọi trực tiếp models
├── services.py        # Logic trộn lẫn với SQL
├── utils.py           # Hàm linh tinh
└── main.py
```

**Chuyện gì xảy ra sau 6 tháng?**

- `services.py` dài 3000 dòng.
- Business rule nằm rải rác ở `views.py`, `services.py`, và trigger DB.
- Muốn đổi từ Postgres sang MongoDB → phải sửa **mọi file**.
- Muốn test 1 rule → phải setup DB, seed data, mock HTTP.
- Dev mới mất 2 tuần mới hiểu luồng đi.

**Đây là vấn đề Layered Architecture ra đời để giải quyết.**

### 1.2. Insight

> *"Chia để trị. Mỗi tầng có trách nhiệm riêng. Tầng trên biết tầng dưới, tầng dưới không biết tầng trên."*

---

## 2. Bốn tầng của Layered Architecture

### 2.1. Sơ đồ tổng quan

```
┌─────────────────────────────────────────────┐
│  1. Presentation Layer                      │
│     (FastAPI, CLI, gRPC)                    │
│     - Parse request                         │
│     - Gọi Application Service               │
│     - Format response                       │
└──────────────────┬──────────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────────┐
│  2. Application Layer                       │
│     (Use Cases, Handlers)                   │
│     - Orchestration                         │
│     - Transaction (UoW)                     │
│     - Không chứa business rule              │
└──────────────────┬──────────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────────┐
│  3. DOMAIN Layer  ⭐ TRÁI TIM                │
│     (Entities, VO, Aggregates, Events)      │
│     - Business rule                         │
│     - Không biết gì về DB, HTTP, UI         │
└──────────────────▲──────────────────────────┘
                   │ implements
                   │
┌──────────────────┴──────────────────────────┐
│  4. Infrastructure Layer                    │
│     (SQLAlchemy, Redis, Stripe, SMTP)       │
│     - Implementation kỹ thuật               │
│     - Phụ thuộc Domain (implements)         │
└─────────────────────────────────────────────┘
```

**Quy tắc vàng:** Mũi tên **chỉ đi vào Domain**. Domain không bao giờ biết ai ở ngoài.

### 2.2. Tầng 1: Presentation

**Trách nhiệm:**

- Nhận request từ user (HTTP, CLI, WebSocket...).
- Parse input → Command/Query object.
- Gọi Application Service.
- Format output (JSON, HTML, text).
- Handle HTTP status, error response.

**Không được:**

- Chứa business rule.
- Gọi Domain trực tiếp (trừ khi cần DTO).
- Gọi Infrastructure (trừ khi cần DI).

**Ví dụ:**

```python
# presentation/api/routes/orders.py
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status

from shop.application.commands.place_order import (
    PlaceOrderCommand, PlaceOrderHandler, OrderItemInput,
)
from shop.application.exceptions import CustomerNotFound
from shop.presentation.api.dependencies import get_place_order_handler
from shop.presentation.api.schemas import (
    PlaceOrderRequest, PlaceOrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=PlaceOrderResponse, status_code=201)
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
) -> PlaceOrderResponse:
    # 1. Parse request → Command
    cmd = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[
            OrderItemInput(
                product_id=item.product_id,
                unit_price_amount=Decimal(item.price),
                unit_price_currency="VND",
                quantity=item.quantity,
            )
            for item in request.items
        ],
    )

    # 2. Gọi Application Service
    try:
        order_id = handler.handle(cmd)
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 3. Format response
    return PlaceOrderResponse(order_id=order_id)
```

**Chú ý:**

- Route **không** biết `Order` là gì.
- Route **không** biết SQLAlchemy.
- Route chỉ parse → gọi → format.

### 2.3. Tầng 2: Application

**Trách nhiệm:**

- **Orchestration** — điều phối các Domain object.
- Quản lý **transaction** (UoW).
- Phát **event** (thường sau commit).
- Authorization check (nếu không phải domain rule).
- Không chứa **business rule cốt lõi**.

**Không được:**

- Chứa rule nghiệp vụ (đẩy vào Domain).
- Import Infrastructure (chỉ import Domain + Port).
- Import Presentation.

**Ví dụ:**

```python
# application/commands/place_order.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shop.application.uow import UnitOfWork
from shop.application.exceptions import CustomerNotFound
from shop.domain.model.order import Order
from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money


@dataclass(frozen=True)
class OrderItemInput:
    product_id: UUID
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]


class PlaceOrderHandler:
    """
    Application Service — điều phối use case.

    - Mở transaction (UoW).
    - Load Customer từ Repository.
    - Tạo Order (Domain).
    - Gọi business method (Order.place()).
    - Save.
    - Commit (UoW publish event).
    """
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            # 1. Load customer
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            # 2. Tạo Order (business logic nằm trong Domain)
            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(
                    OrderLine.create(
                        product_id=item.product_id,
                        unit_price=Money(
                            item.unit_price_amount,
                            item.unit_price_currency,
                        ),
                        quantity=item.quantity,
                    )
                )

            # 3. Gọi business method
            order.place()

            # 4. Save
            self._uow.orders.save(order)

            # 5. Commit
            self._uow.commit()

        return order.id
```

**Chú ý:**

- Handler **mỏng** — chủ yếu là orchestration.
- Business rule nằm trong `Order.place()`, `OrderLine.create()`.
- Handler biết Domain, không biết Infrastructure.

### 2.4. Tầng 3: Domain ⭐

**Trách nhiệm:**

- Chứa **toàn bộ business rule**.
- Định nghĩa **Entity, VO, Aggregate, Event, Repository Protocol**.
- Độc lập tuyệt đối với framework, DB, UI.

**Không được:**

- Import bất cứ gì ngoài stdlib và chính nó.
- Biết về FastAPI, SQLAlchemy, Redis, SMTP...

**Ví dụ:**

```python
# domain/model/order.py
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money
from shop.domain.events.order_events import OrderPlaced
from shop.domain.exceptions import EmptyOrderCannotBePlaced


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"


@dataclass(eq=False)
class Order:
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    _status: OrderStatus = OrderStatus.DRAFT
    _lines: dict[UUID, OrderLine] = field(default_factory=dict)
    _events: list = field(default_factory=list, repr=False)

    def place(self) -> None:
        """Business method — không biết gì ngoài domain."""
        if not self._lines:
            raise EmptyOrderCannotBePlaced(self.id)
        self._status = OrderStatus.PLACED
        self._events.append(
            OrderPlaced(
                order_id=self.id,
                customer_id=self.customer_id,
                total=self.total,
                line_count=len(self._lines),
            )
        )

    @property
    def total(self) -> Money:
        return sum(
            (line.subtotal for line in self._lines.values()),
            Money(Decimal("0"), "VND"),
        )
```

**Dấu hiệu Domain đúng:**

- `from shop.domain...` — chỉ import từ Domain.
- `import stdlib` — `dataclasses`, `uuid`, `datetime`, `enum`, `decimal`.
- **Không có** `import fastapi`, `import sqlalchemy`, `import redis`, `import httpx`.

### 2.5. Tầng 4: Infrastructure

**Trách nhiệm:**

- **Implement** các Port của Domain (Repository, EmailSender...).
- Xử lý chi tiết kỹ thuật: DB, HTTP, cache, message queue...
- Mapping giữa Domain và ORM/external.

**Không được:**

- Chứa business rule.
- Import Presentation.
- Bị import bởi Domain.

**Ví dụ:**

```python
# infrastructure/persistence/sqlalchemy/order_repository.py
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from shop.domain.model.order import Order
from shop.domain.repositories.order_repository import OrderRepository
from shop.infrastructure.persistence.sqlalchemy.mappers.order_mapper import (
    OrderMapper,
)
from shop.infrastructure.persistence.sqlalchemy.orm_models import OrderRow


class SqlAlchemyOrderRepository:
    """
    IMPLEMENTS OrderRepository (Protocol ở Domain).

    Domain không biết class này tồn tại.
    """
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderRow, order_id)
        return OrderMapper.to_domain(row) if row else None

    def save(self, order: Order) -> None:
        self._session.merge(OrderMapper.to_row(order))

    def delete(self, order: Order) -> None:
        row = self._session.get(OrderRow, order.id)
        if row:
            self._session.delete(row)

    def next_id(self) -> UUID:
        return uuid4()
```

**Chú ý:**

- `SqlAlchemyOrderRepository` **implements** `OrderRepository` (Protocol) — không cần kế thừa, chỉ cần cùng signature.
- Import cả Domain và SQLAlchemy.
- Không ai ở Domain import ngược lại.

---

## 3. Dependency Rule — Nguyên tắc vàng

### 3.1. Phát biểu

> **Dependency chỉ đi vào Domain.** Tầng ngoài phụ thuộc tầng trong. Tầng trong không biết tầng ngoài.

```
Presentation → Application → Domain ← Infrastructure
```

**Không bao giờ:**

- Domain import Application.
- Domain import Infrastructure.
- Domain import Presentation.
- Application import Infrastructure.
- Application import Presentation.
- Infrastructure import Presentation.

### 3.2. Tại sao quan trọng?

**1. Domain testable mà không cần DB/HTTP.**

```python
# Test thuần Python
def test_order_place_emits_event():
    order = Order.create(uuid4())
    order.add_line(...)
    order.place()
    assert order.status == OrderStatus.PLACED
```

Không cần Postgres, không cần FastAPI, không cần network.

**2. Đổi Infrastructure không ảnh hưởng Domain.**

Đổi từ SQLAlchemy sang MongoDB → viết lại Repository impl. Domain **không đổi 1 dòng**.

**3. Domain có thể tái sử dụng.**

Cùng Domain dùng cho web, CLI, mobile backend, batch job.

**4. Dễ hiểu, dễ review.**

Business rule nằm 1 chỗ. Không ai phải đọc 3000 dòng `services.py`.

### 3.3. Vấn đề: Repository Protocol ở đâu?

Đây là câu hỏi **kinh điển**. Repository Protocol nên ở **Domain** hay **Application**?

**Trả lời:** Ở **Domain**.

**Lý do:**

- Repository là **khái niệm nghiệp vụ** ("tôi cần lưu Order").
- Domain cần biết interface để Application gọi.
- Implementation ở Infrastructure.

```python
# domain/repositories/order_repository.py
from typing import Protocol
from uuid import UUID
from shop.domain.model.order import Order


class OrderRepository(Protocol):
    """
    Interface — ở Domain.

    Không import gì ngoài Domain.
    """
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
```

```python
# infrastructure/persistence/sqlalchemy/order_repository.py
# IMPLEMENTS Protocol ở Domain
class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        ...
```

### 3.4. Port và Adapter

Đây là **ngôn ngữ của Hexagonal Architecture** (bài sau sẽ học sâu).

- **Port** = interface mà Domain/Application định nghĩa. Ví dụ: `OrderRepository`, `EmailSender`.
- **Adapter** = implementation ở Infrastructure. Ví dụ: `SqlAlchemyOrderRepository`, `SmtpEmailSender`.

**Ví dụ Port:**

```python
# application/ports/email_sender.py
from typing import Protocol


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...
```

**Ví dụ Adapter:**

```python
# infrastructure/email/smtp_sender.py
import smtplib

from shop.application.ports.email_sender import EmailSender


class SmtpEmailSender:
    """Adapter cho EmailSender, dùng SMTP."""

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def send(self, to: str, subject: str, body: str) -> None:
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.sendmail(
                from_addr=self._username,
                to_addrs=to,
                msg=f"Subject: {subject}\n\n{body}",
            )
```

**Fake Adapter cho test:**

```python
# tests/fakes/email_sender.py
class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})
```

Test không cần SMTP thật.

---

## 4. Cấu trúc project Python đầy đủ

Đây là **cấu trúc chuẩn** cho project DDD Python (đã giới thiệu ở bài 9, giờ làm đầy đủ).

```
shop/
├── pyproject.toml
├── README.md
├── .importlinter
├── src/
│   └── shop/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── domain/                          # ⭐ TẦNG 3
│       │   ├── __init__.py
│       │   ├── model/
│       │   │   ├── __init__.py
│       │   │   ├── order.py
│       │   │   ├── order_line.py
│       │   │   ├── customer.py
│       │   │   └── product.py
│       │   ├── events/
│       │   │   ├── __init__.py
│       │   │   └── order_events.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── pricing_service.py
│       │   ├── repositories/                # Protocol
│       │   │   ├── __init__.py
│       │   │   ├── order_repository.py
│       │   │   └── customer_repository.py
│       │   └── exceptions.py
│       │
│       ├── application/                     # TẦNG 2
│       │   ├── __init__.py
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   └── place_order.py
│       │   ├── queries/
│       │   │   ├── __init__.py
│       │   │   └── order_summary.py
│       │   ├── handlers/
│       │   │   ├── __init__.py
│       │   │   └── on_order_placed.py
│       │   ├── ports/                       # Interface cho external
│       │   │   ├── __init__.py
│       │   │   └── email_sender.py
│       │   ├── uow.py                       # UnitOfWork Protocol
│       │   ├── dto.py
│       │   └── exceptions.py
│       │
│       ├── infrastructure/                  # TẦNG 4
│       │   ├── __init__.py
│       │   ├── persistence/
│       │   │   ├── __init__.py
│       │   │   ├── sqlalchemy/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── orm_models.py
│       │   │   │   ├── mappers/
│       │   │   │   │   ├── __init__.py
│       │   │   │   │   └── order_mapper.py
│       │   │   │   ├── repositories.py
│       │   │   │   └── uow.py
│       │   │   └── in_memory/
│       │   │       ├── __init__.py
│       │   │       ├── repositories.py
│       │   │       └── uow.py
│       │   ├── email/
│       │   │   ├── __init__.py
│       │   │   └── smtp_sender.py
│       │   └── messaging/
│       │       ├── __init__.py
│       │       └── in_memory_bus.py
│       │
│       ├── presentation/                    # TẦNG 1
│       │   ├── __init__.py
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   ├── main.py
│       │   │   ├── dependencies.py
│       │   │   ├── schemas.py
│       │   │   └── routes/
│       │   │       ├── __init__.py
│       │   │       └── orders.py
│       │   └── cli/
│       │       ├── __init__.py
│       │       └── main.py
│       │
│       └── bootstrap.py                     # Composition Root
│
└── tests/
    ├── unit/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    ├── integration/
    │   └── persistence/
    ├── e2e/
    │   └── api/
    └── fakes/
```

**Điểm mấu chốt:**

- Mỗi tầng là 1 folder con của `shop/`.
- Domain **không** import gì ngoài stdlib và chính nó.
- Application import Domain + Ports.
- Infrastructure import Domain + Application (để implement Port) + external libs.
- Presentation import Application + Domain (chỉ DTO).
- `bootstrap.py` ở gốc — ráp mọi thứ.

---

## 5. Enforce kiến trúc bằng `import-linter`

### 5.1. Tại sao cần?

Python **không ngăn** bạn import bừa. Compiler không có. Chỉ có **kỷ luật team** — và kỷ luật dễ vỡ.

`import-linter` là **người gác cổng** tự động.

### 5.2. Cấu hình

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["shop"]

# ---- Contract 1: Domain không phụ thuộc ai ----
[[tool.importlinter.contracts]]
name = "Domain không phụ thuộc ai"
type = "forbidden"
source_modules = ["shop.domain"]
forbidden_modules = [
    "shop.application",
    "shop.infrastructure",
    "shop.presentation",
]

# ---- Contract 2: Application không phụ thuộc Infrastructure/Presentation ----
[[tool.importlinter.contracts]]
name = "Application không phụ thuộc Infrastructure/Presentation"
type = "forbidden"
source_modules = ["shop.application"]
forbidden_modules = [
    "shop.infrastructure",
    "shop.presentation",
]

# ---- Contract 3: Infrastructure không phụ thuộc Presentation ----
[[tool.importlinter.contracts]]
name = "Infrastructure không phụ thuộc Presentation"
type = "forbidden"
source_modules = ["shop.infrastructure"]
forbidden_modules = ["shop.presentation"]

# ---- Contract 4: Tầng ----
[[tool.importlinter.contracts]]
name = "Layered architecture"
type = "layers"
layers = [
    "shop.presentation",
    "shop.application",
    "shop.domain",
]
```

### 5.3. Chạy

```bash
pip install import-linter
lint-imports
```

Output khi OK:

```
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 42 files, 156 dependencies.
-----------------------------------

Domain không phụ thuộc ai KEPT
Application không phụ thuộc Infrastructure/Presentation KEPT
Infrastructure không phụ thuộc Presentation KEPT
Layered architecture KEPT
```

Output khi vi phạm:

```
Domain không phụ thuộc ai BROKEN

Contracts: 1 broken, 3 kept.

-------------
Broken contracts
-------------

Domain không phụ thuộc ai
-------------------------

shop.domain.model.order is not allowed to import shop.infrastructure.persistence:

-   shop.domain.model.order:1:0
    -> shop.infrastructure.persistence.sqlalchemy
```

**Fix ngay.** Đây là sức mạnh của tooling.

### 5.4. Các loại contract khác

**Independence contract:**

```toml
[[tool.importlinter.contracts]]
name = "Commands không import Queries"
type = "independence"
modules = [
    "shop.application.commands",
    "shop.application.queries",
]
```

**Forbidden contract:**

```toml
[[tool.importlinter.contracts]]
name = "Không ai import ORM trực tiếp trừ Infrastructure"
type = "forbidden"
source_modules = [
    "shop.domain",
    "shop.application",
    "shop.presentation",
]
forbidden_modules = ["sqlalchemy"]
```

**Layers contract:**

```toml
[[tool.importlinter.contracts]]
name = "Layered"
type = "layers"
layers = [
    "shop.presentation",
    "shop.application",
    "shop.domain",
]
```

---

## 6. Composition Root — Nơi ráp mọi thứ

### 6.1. Vấn đề

Nếu ai cũng `new` object, sẽ có coupling:

```python
# ❌ SAI: Presentation tự new Infrastructure
@router.post("/orders")
def place_order(request):
    session = create_session()                          # Infrastructure
    repo = SqlAlchemyOrderRepository(session)            # Infrastructure
    uow = SqlAlchemyUnitOfWork(session, event_bus)       # Infrastructure
    handler = PlaceOrderHandler(uow)
    handler.handle(...)
```

Presentation giờ **biết** Infrastructure → vi phạm Dependency Rule.

### 6.2. Composition Root

**Composition Root** là **1 chỗ duy nhất** ráp mọi thứ. Thường nằm ở `bootstrap.py` hoặc `main.py`.

```python
# bootstrap.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shop.application.commands.place_order import PlaceOrderHandler
from shop.application.handlers.on_order_placed import (
    SendOrderConfirmationEmail,
    ReserveInventory,
)
from shop.infrastructure.email.smtp_sender import SmtpEmailSender
from shop.infrastructure.messaging.in_memory_bus import InMemoryEventBus
from shop.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyCustomerRepository,
    SqlAlchemyOrderRepository,
)
from shop.infrastructure.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork


def bootstrap(db_url: str, smtp_config: dict) -> dict:
    """
    Composition Root — ráp mọi thứ.

    Đây là chỗ DUY NHẤT biết tất cả các tầng.
    """
    # Infrastructure
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    event_bus = InMemoryEventBus()
    email_sender = SmtpEmailSender(
        host=smtp_config["host"],
        port=smtp_config["port"],
        username=smtp_config["username"],
        password=smtp_config["password"],
    )

    # Setup event handlers
    event_bus.subscribe(
        OrderPlaced,
        SendOrderConfirmationEmail(email_sender).handle,
    )
    event_bus.subscribe(
        OrderPlaced,
        ReserveInventory(lambda: SqlAlchemyUnitOfWork(session_factory, event_bus)).handle,
    )

    # Application handlers
    def make_place_order_handler() -> PlaceOrderHandler:
        uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
        return PlaceOrderHandler(uow)

    return {
        "place_order_handler_factory": make_place_order_handler,
        "event_bus": event_bus,
    }
```

### 6.3. FastAPI dùng Composition Root

```python
# presentation/api/main.py
from fastapi import FastAPI

from shop.bootstrap import bootstrap
from shop.presentation.api.routes import orders


def create_app() -> FastAPI:
    app = FastAPI(title="Shop API")

    # Bootstrap container
    container = bootstrap(
        db_url="postgresql://user:pass@localhost/shop",
        smtp_config={...},
    )
    app.state.container = container

    app.include_router(orders.router)
    return app


app = create_app()
```

```python
# presentation/api/dependencies.py
from fastapi import Request
from shop.application.commands.place_order import PlaceOrderHandler


def get_place_order_handler(request: Request) -> PlaceOrderHandler:
    """Lấy handler từ container — không tự new."""
    container = request.app.state.container
    return container["place_order_handler_factory"]()
```

**Điểm mấu chốt:**

- Presentation **không** biết Infrastructure.
- Presentation **chỉ** gọi `container["place_order_handler_factory"]()`.
- Composition Root ráp.

---

## 7. So sánh các kiến trúc

Layered không phải kiến trúc duy nhất. Còn có Hexagonal, Clean, Onion. Chúng **giống nhau** ở tinh thần, **khác nhau** ở chi tiết.

### 7.1. Bảng so sánh

| Tiêu chí | Layered | Hexagonal | Clean | Onion |
|---|---|---|---|---|
| **Số tầng** | 4 (Pres, App, Domain, Infra) | 3 (Domain, App, Adapters) | 4 (Entities, Use Cases, Interface Adapters, Frameworks) | 4 (Domain Model, Domain Services, App Services, Infra) |
| **Khái niệm chính** | Tầng | Ports & Adapters | Use Cases | Domain Services |
| **Domain ở đâu** | Giữa | Trung tâm | Trung tâm | Trung tâm |
| **Hướng dependency** | Vào Domain | Vào Domain | Vào Domain | Vào Domain |
| **Ai đề xuất** | Fowler | Cockburn (2005) | Uncle Bob (2012) | Palermo (2008) |

### 7.2. Hexagonal Architecture (Ports & Adapters)

```
              ┌───────────────────────┐
   ┌──────────┤                       ├──────────┐
   │          │                       │          │
   │  HTTP    │      DOMAIN           │   SQL    │
   │  Adapter │    (Business)         │  Adapter │
   │          │                       │          │
   └──────────┤                       ├──────────┘
              │     PORTS             │
              └───────────────────────┘
   ┌──────────┐                       ┌──────────┐
   │          │                       │          │
   │  CLI     │                       │  Redis   │
   │  Adapter │                       │  Adapter │
   │          │                       │          │
   └──────────┘                       └──────────┘
```

**Điểm chính:** Domain ở trung tâm. Mọi thứ khác là **adapter** kết nối qua **port**.

**Port** = interface. **Adapter** = implementation.

### 7.3. Clean Architecture

```
        ┌─────────────────────────────────┐
        │   Frameworks & Drivers          │
        │   (FastAPI, SQLAlchemy)         │
        │  ┌───────────────────────────┐  │
        │  │ Interface Adapters        │  │
        │  │ (Controllers, Gateways)   │  │
        │  │  ┌───────────────────┐    │  │
        │  │  │  Use Cases        │    │  │
        │  │  │  ┌───────────┐    │    │  │
        │  │  │  │ Entities  │    │    │  │
        │  │  │  └───────────┘    │    │  │
        │  │  └───────────────────┘    │  │
        │  └───────────────────────────┘  │
        └─────────────────────────────────┘
```

**Điểm chính:** Có **4 vòng**. Vòng trong không biết vòng ngoài.

### 7.4. Onion Architecture

```
        ┌─────────────────────────────────┐
        │  Infrastructure                 │
        │  ┌───────────────────────────┐  │
        │  │ Application Services      │  │
        │  │  ┌───────────────────┐    │  │
        │  │  │ Domain Services   │    │  │
        │  │  │  ┌───────────┐    │    │  │
        │  │  │  │  Domain   │    │    │  │
        │  │  │  │  Model    │    │    │  │
        │  │  │  └───────────┘    │    │  │
        │  │  └───────────────────┘    │  │
        │  └───────────────────────────┘  │
        └─────────────────────────────────┘
```

**Điểm chính:** Domain ở lõi. Mỗi lớp vỏ bọc lấy lõi.

### 7.5. Kết luận

**4 kiến trúc này thực chất là 1.** Chúng đều nói: **Domain ở trung tâm, dependency đi vào trong**.

Trong thực tế:

- **Layered** = dễ hiểu nhất, phù hợp team mới.
- **Hexagonal** = nhấn mạnh ports/adapters.
- **Clean** = nhấn mạnh use cases.
- **Onion** = nhấn mạnh domain services.

**Khuyến nghị:** Dùng **Layered** làm nền tảng, thêm **Ports & Adapters** khi cần. Đừng cố phân biệt cứng nhắc.

---

## 8. Tám anti-pattern về kiến trúc

### ❌ Anti-pattern 1: Domain import Infrastructure

```python
# ❌ SAI
# domain/model/order.py
from sqlalchemy.orm import Session   # PHÁ VỠ

class Order:
    def save(self, session: Session) -> None:
        session.add(self)
```

**Fix:** Repository ở Infrastructure, Domain không biết.

### ❌ Anti-pattern 2: Presentation gọi Domain trực tiếp

```python
# ❌ SAI: Route gọi Domain
@router.post("/orders")
def place_order(request):
    order = Order.create(request.customer_id)   # Domain trực tiếp
    order.add_line(...)
    order.place()
    session.add(order)   # Infrastructure trực tiếp
```

**Fix:** Qua Application Handler.

### ❌ Anti-pattern 3: Application chứa business rule

```python
# ❌ SAI
class PlaceOrderHandler:
    def handle(self, cmd) -> UUID:
        if cmd.total > 1_000_000:   # Business rule ở Application!
            raise TooExpensive()
        ...
```

**Fix:** Đẩy vào Domain.

```python
# ✅ ĐÚNG
class Order:
    def place(self) -> None:
        if self.total.amount > 1_000_000:   # Business rule ở Domain
            raise TooExpensive()
        ...
```

### ❌ Anti-pattern 4: ORM model = Domain model

```python
# ❌ SAI
class Order(Base):   # SQLAlchemy + Domain
    __tablename__ = "orders"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    # Domain methods + ORM columns trộn
```

**Fix:** Tách 2 class.

### ❌ Anti-pattern 5: Không có Composition Root

```python
# ❌ SAI: Mỗi route tự new
@router.post("/orders")
def place_order(request):
    session = create_session()
    repo = SqlAlchemyOrderRepository(session)
    handler = PlaceOrderHandler(repo)
    ...
```

**Fix:** Bootstrap 1 lần.

### ❌ Anti-pattern 6: Cross-layer import

```python
# ❌ SAI: Application import Infrastructure
# application/commands/place_order.py
from shop.infrastructure.persistence.sqlalchemy.order_repository import (
    SqlAlchemyOrderRepository,
)
```

**Fix:** Application import Protocol ở Domain.

### ❌ Anti-pattern 7: Circular dependency

```python
# ❌ SAI
# domain/model/order.py
from shop.application.commands.place_order import PlaceOrderCommand   # Ngược!

class Order:
    def place(self, cmd: PlaceOrderCommand) -> None:
        ...
```

**Fix:** Domain không biết Command.

### ❌ Anti-pattern 8: Test infrastructure trong domain test

```python
# ❌ SAI: Domain test cần DB
def test_order_place():
    session = create_session()   # Infrastructure!
    repo = SqlAlchemyOrderRepository(session)
    ...
```

**Fix:** Domain test pure Python.

```python
# ✅ ĐÚNG
def test_order_place():
    order = Order.create(uuid4())
    order.add_line(OrderLine.create(...))
    order.place()
    assert order.status == OrderStatus.PLACED
```

---

## 9. Ví dụ tổng hợp: 1 request đi qua 4 tầng

Hãy theo dõi 1 request `POST /orders`:

```
1. HTTP request đến FastAPI
   ▼
2. Presentation: route parse → PlaceOrderCommand
   ▼
3. Application: PlaceOrderHandler
   - Mở UoW
   - Load Customer từ Repository (interface)
   ▼
4. Domain: Customer, Order, OrderLine
   - Order.place() kiểm tra invariant
   - Phát OrderPlaced event
   ▼
5. Application: UoW.commit()
   - Repository.save() (interface)
   ▼
6. Infrastructure: SqlAlchemyOrderRepository
   - Mapper to_row()
   - Session.merge()
   - Session.commit()
   - Publish event
   ▼
7. Infrastructure: Event handler
   - SendOrderConfirmationEmail (SMTP)
   - ReserveInventory (SQLAlchemy)
   ▼
8. Presentation: format response JSON
```

**Chú ý:**

- Domain ở bước 4 — **không biết** FastAPI, SQLAlchemy, SMTP.
- Application điều phối.
- Infrastructure implement.
- Presentation format.

---

## 10. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Tổ chức project

Cho project hiện tại (từ bài 9), tổ chức lại thành **4 tầng**:

- `domain/`, `application/`, `infrastructure/`, `presentation/`.
- Setup `import-linter` với 3 contract:
  1. Domain không phụ thuộc ai.
  2. Application không phụ thuộc Infra/Pres.
  3. Infrastructure không phụ thuộc Presentation.

Chạy `lint-imports` → pass.

### 🟡 Bài tập 2 (trung bình): Composition Root

Viết `bootstrap.py` cho project:

- Nhận config (db_url, smtp_config).
- Tạo engine, session_factory, event_bus, email_sender.
- Đăng ký event handlers.
- Trả về `dict` container.

Sửa FastAPI để dùng container:

- Không tự new.
- Chỉ lấy từ `app.state.container`.

Viết ít nhất 5 test cho bootstrap (không cần HTTP).

### 🔴 Bài tập 3 (khó): Chuyển từ Monolith sang Layered

Cho project **monolith đơn giản**:

```python
# app.py
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()
engine = create_engine("sqlite:///shop.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String)
    status = Column(String)
    total = Column(Integer)


@app.post("/orders")
def create_order(customer_id: str, items: list[dict]):
    session = Session()
    # ... business logic trộn
    order = OrderModel(
        customer_id=customer_id,
        status="PENDING",
        total=sum(i["price"] * i["qty"] for i in items),
    )
    session.add(order)
    session.commit()
    return {"id": order.id}
```

**Yêu cầu:**

1. Refactor thành 4 tầng.
2. Tách Domain model, ORM model.
3. Viết Repository + UoW.
4. Viết Application Handler.
5. Composition Root.
6. Setup `import-linter` chặn vi phạm.
7. Viết ít nhất 15 test (unit + integration + e2e).

Bonus: Thêm Event `OrderPlaced` + handler gửi email.

---

## 11. Checklist sau bài 10

Trước khi sang bài 11, bạn phải tự tin trả lời:

- [ ] 4 tầng của Layered Architecture là gì?
- [ ] Mỗi tầng có trách nhiệm gì?
- [ ] Dependency Rule phát biểu thế nào?
- [ ] Tại sao Domain không được import Infrastructure?
- [ ] Repository Protocol ở tầng nào? Tại sao?
- [ ] Port và Adapter là gì?
- [ ] Composition Root là gì? Tại sao cần?
- [ ] Layered vs Hexagonal vs Clean vs Onion — khác nhau chỗ nào? Giống nhau chỗ nào?
- [ ] `import-linter` giúp gì?
- [ ] 8 anti-pattern về kiến trúc là gì?

Nếu trả lời được hết, bạn đã sẵn sàng bài 11.

---

## 12. Tóm tắt bài 10

| Điểm | Nội dung |
|---|---|
| **Layered** | 4 tầng: Presentation, Application, Domain, Infrastructure |
| **Presentation** | Parse request, format response |
| **Application** | Orchestration, transaction |
| **Domain** | Business rule — trung tâm |
| **Infrastructure** | Implementation: DB, HTTP, cache |
| **Dependency Rule** | Mũi tên chỉ đi vào Domain |
| **Port** | Interface ở Domain/Application |
| **Adapter** | Implementation ở Infrastructure |
| **Composition Root** | 1 chỗ ráp mọi thứ |
| **Enforce** | `import-linter` với contracts |
| **Hexagonal** | Ports & Adapters — cùng tinh thần |
| **Clean/Onion** | Biến thể của cùng ý tưởng |
| **8 anti-pattern** | Domain import Infra, Pres gọi Domain, business rule ở App, ORM = Domain, không CR, cross-layer, circular, test infra trong domain |

**Câu thần chú:** *"Dependency đi vào Domain. Domain không biết ai ở ngoài."*

---

## 13. Chuẩn bị cho bài 11

Bài tiếp theo: **Application Service & CQRS**.

Chuẩn bị:
- Đọc lại `PlaceOrderHandler` (bài 10) và `OrderSummaryQuery` (bài 9).
- Nghĩ về **Command vs Query** trong domain bạn đang làm.
- Sẽ bàn: CQRS là gì, khi nào cần, Command handler vs Query handler, read model riêng, và các biến thể CQRS.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 11** (CQRS) ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Hexagonal vs Clean, DI container, monorepo, modular monolith.
5. **Review kiến trúc** project của bạn — nếu bạn gửi cấu trúc thư mục, tôi sẽ chỉ ra chỗ vi phạm.

Nói tôi biết bạn muốn gì nhé.