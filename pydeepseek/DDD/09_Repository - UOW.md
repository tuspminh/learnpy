# 📖 Bài 9: Repository & Unit of Work — Cổng vào persistence

> Đây là **bài cuối của Level 2** — và là **bài bản lề** giữa Domain và Infrastructure. Repository là khái niệm mà nhiều Python dev hiểu sai nhất: họ tưởng Repository chỉ là "cái wrapper quanh ORM". Sai. Repository là **abstraction của Domain**, giúp Domain **không biết gì về DB**. Unit of Work là **transaction boundary**, giúp nhiều Repository commit cùng lúc.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Repository** là gì và tại sao nó quan trọng.
2. Phân biệt **Repository** vs **DAO** vs **ORM**.
3. Viết Repository interface ở Domain (dùng `Protocol`).
4. Viết Repository implementation ở Infrastructure (SQLAlchemy, in-memory).
5. Hiểu **Unit of Work** pattern và tại sao cần.
6. Xử lý **transaction** đúng cách.
7. Biết **mapping** giữa Domain model và ORM model.
8. Tránh được **8 anti-pattern** khi dùng Repository/UoW.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Repository là gì?

### 1.1. Định nghĩa

> **Repository** là một **abstraction** giúp Domain **không biết gì về persistence**. Nó cung cấp **interface giống collection** để truy xuất Aggregate, nhưng ẩn đi toàn bộ chi tiết DB (SQL, ORM, connection...).

### 1.2. Trực giác

Hãy tưởng tượng bạn là **thủ thư**. Bạn có một **tủ sách** (Aggregate Store).

- Muốn lấy sách: bạn nói "cho tôi sách mã X".
- Muốn cất sách: bạn nói "cất sách này".
- Bạn **không cần biết** sách được sắp xếp thế nào, có bao nhiêu ngăn, đánh số ra sao.

Repository chính là **thủ thư** — cung cấp interface đơn giản, che giấu toàn bộ logic lưu trữ.

### 1.3. Đặc điểm

| Đặc điểm | Ý nghĩa |
|---|---|
| **Abstraction của Domain** | Interface ở Domain, impl ở Infrastructure |
| **Collection-like** | `find_by_id`, `save`, `delete` — như list/dict |
| **Chỉ cho Aggregate Root** | Không có Repository cho Entity con |
| **1 Aggregate = 1 Repository** | Tương ứng 1-1 |
| **Không leak DB** | Không có `Session`, `query`, `Connection` |
| **Không chứa business logic** | Chỉ đọc/ghi |

### 1.4. Repository vs DAO vs ORM

Đây là **3 khái niệm khác nhau** mà nhiều dev nhầm.

| Tiêu chí | Repository | DAO | ORM |
|---|---|---|---|
| **Tầng** | Domain | Infrastructure | Infrastructure |
| **Đơn vị** | Aggregate | Table | Table/Row |
| **Interface** | Collection-like | CRUD methods | Query builder |
| **Ai dùng** | Domain | Application | Infrastructure |
| **Ví dụ** | `OrderRepository` | `OrderDAO` | SQLAlchemy Session |
| **Ngôn ngữ** | Nghiệp vụ | Kỹ thuật | Kỹ thuật |
| **Số lượng** | Ít (chỉ Root) | Nhiều (mọi table) | 1 (cho toàn DB) |

**Ví dụ cụ thể:**

```python
# ❌ DAO — thao tác trên table
class OrderDAO:
    def insert(self, row: dict) -> None: ...
    def update(self, order_id: int, fields: dict) -> None: ...
    def select_by_customer(self, customer_id: int) -> list[dict]: ...

# ✅ Repository — thao tác trên Aggregate
class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def find_by_customer(self, customer_id: UUID) -> list[Order]: ...

# ✅ ORM — công cụ kỹ thuật
session.query(OrderRow).filter(...).all()
```

> 💡 **Bài học:** Đừng expose ORM ra Domain. Đừng để Domain gọi `session.query()`. Repository là **cửa duy nhất** cho persistence.

---

## 2. Repository interface ở Domain

### 2.1. Dùng `Protocol`, không dùng `ABC`

Trong Python, dùng `Protocol` (structural typing) thay vì `ABC` (nominal typing).

```python
# domain/repositories/order_repository.py
from typing import Protocol
from uuid import UUID

from shop.domain.model.order import Order


class OrderRepository(Protocol):
    """
    Repository cho Aggregate Order.

    Đây là INTERFACE — không có code SQL, không có import ORM.
    Implementation nằm ở infrastructure layer.
    """
    def find_by_id(self, order_id: UUID) -> Order | None:
        """Trả về Order hoặc None nếu không tìm thấy."""
        ...

    def save(self, order: Order) -> None:
        """Lưu Order (insert hoặc update)."""
        ...

    def delete(self, order: Order) -> None:
        """Xóa Order."""
        ...

    def next_id(self) -> UUID:
        """Sinh ID mới cho Order."""
        ...

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        """Tìm tất cả Order của một customer."""
        ...
```

**Điểm mấu chốt:**

- **Không có** `import sqlalchemy`.
- **Không có** `Session`.
- **Không có** `query`.
- Chỉ có **method nghiệp vụ**: `find_by_id`, `save`.
- Trả về **Domain object** (`Order`), không phải dict/row.

### 2.2. Method naming

**Repository method nên dùng ngôn ngữ collection.**

| Nên dùng | Không nên dùng |
|---|---|
| `find_by_id` | `select_order` |
| `find_all` | `get_all_orders` |
| `find_by_customer` | `query_orders_by_customer` |
| `save` | `insert_or_update` |
| `delete` | `remove_from_db` |
| `next_id` | `generate_uuid` |

### 2.3. Trả về gì?

| Tình huống | Nên | Không nên |
|---|---|---|
| Tìm 1, có thể null | `Order \| None` | `raise NotFound` |
| Tìm nhiều | `list[Order]` | Generator, Cursor |
| Đếm | `int` | SQL count string |

```python
# ✅ Tốt
def find_by_id(self, order_id: UUID) -> Order | None: ...

# ❌ Không nên
def find_by_id(self, order_id: UUID) -> Order:
    # raise NotFound nếu không có — caller không biết phải handle
    ...
```

**Lý do:** Caller muốn tự quyết định có raise hay không.

### 2.4. Ví dụ: `CustomerRepository`

```python
# domain/repositories/customer_repository.py
from typing import Protocol
from uuid import UUID

from shop.domain.model.customer import Customer
from shop.shared.domain.email import Email


class CustomerRepository(Protocol):
    def find_by_id(self, customer_id: UUID) -> Customer | None: ...
    def find_by_email(self, email: Email) -> Customer | None: ...
    def save(self, customer: Customer) -> None: ...
    def delete(self, customer: Customer) -> None: ...
    def next_id(self) -> UUID: ...
    def exists_with_email(self, email: Email) -> bool: ...
```

---

## 3. Repository implementation ở Infrastructure

### 3.1. In-memory (cho test)

Đây là implementation **đơn giản nhất** — dùng cho test.

```python
# infrastructure/persistence/in_memory/order_repository.py
from copy import deepcopy
from uuid import UUID, uuid4

from shop.domain.model.order import Order


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Order] = {}

    def find_by_id(self, order_id: UUID) -> Order | None:
        order = self._store.get(order_id)
        # Deep copy để tránh caller mutate trực tiếp store
        return deepcopy(order) if order else None

    def save(self, order: Order) -> None:
        self._store[order.id] = deepcopy(order)

    def delete(self, order: Order) -> None:
        self._store.pop(order.id, None)

    def next_id(self) -> UUID:
        return uuid4()

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        return [
            deepcopy(o) for o in self._store.values()
            if o.customer_id == customer_id
        ]
```

**Lưu ý:**

- **Deep copy** khi find/save để tránh leak.
- **Không có transaction** — mọi thứ atomic vì in-memory.
- **Không có commit** — không cần.

### 3.2. SQLAlchemy — ORM model tách biệt

**Quy tắc vàng:** ORM model **KHÁC** Domain model.

```python
# infrastructure/persistence/sqlalchemy/orm_models.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OrderRow(Base):
    """ORM model cho bảng 'orders'. KHÁC Domain model."""
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


class OrderLineRow(Base):
    __tablename__ = "order_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[UUID]
    unit_price_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    unit_price_currency: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int]

    order: Mapped[OrderRow] = relationship(back_populates="lines")
```

**Chú ý:**
- `OrderRow` có `status: str`, không phải `OrderStatus` (enum).
- `Money` được **flatten** thành 2 cột: `unit_price_amount` + `unit_price_currency`.
- ORM quan tâm **cấu trúc bảng**, không quan tâm nghiệp vụ.

### 3.3. Mapper — chuyển đổi 2 chiều

```python
# infrastructure/persistence/sqlalchemy/mappers/order_mapper.py
from shop.domain.model.order import Order, OrderStatus
from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money
from shop.infrastructure.persistence.sqlalchemy.orm_models import (
    OrderRow, OrderLineRow,
)


class OrderMapper:
    """Chuyển đổi giữa Domain model và ORM model."""

    @staticmethod
    def to_domain(row: OrderRow) -> Order:
        """ORM Row → Domain Order."""
        order = Order.reconstruct(
            order_id=row.id,
            customer_id=row.customer_id,
            status=OrderStatus(row.status),
            lines=[
                OrderLine(
                    id=line.id,
                    product_id=line.product_id,
                    unit_price=Money(
                        amount=line.unit_price_amount,
                        currency=line.unit_price_currency,
                    ),
                    _quantity=line.quantity,
                )
                for line in row.lines
            ],
            tracking_number=row.tracking_number,
            created_at=row.created_at,
        )
        return order

    @staticmethod
    def to_row(order: Order) -> OrderRow:
        """Domain Order → ORM Row."""
        return OrderRow(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            tracking_number=order.tracking_number,
            created_at=order.created_at,
            lines=[
                OrderLineRow(
                    id=line.id,
                    product_id=line.product_id,
                    unit_price_amount=line.unit_price.amount,
                    unit_price_currency=line.unit_price.currency,
                    quantity=line.quantity,
                )
                for line in order.lines
            ],
        )
```

**Chú ý:**

- `to_domain`: dùng `reconstruct` — không validate, không phát event.
- `to_row`: flatten `Money` thành 2 cột.
- `OrderStatus` enum ↔ `str`.

### 3.4. SQLAlchemy Repository

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
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderRow, order_id)
        return OrderMapper.to_domain(row) if row else None

    def save(self, order: Order) -> None:
        row = OrderMapper.to_row(order)
        self._session.merge(row)

    def delete(self, order: Order) -> None:
        row = self._session.get(OrderRow, order.id)
        if row:
            self._session.delete(row)

    def next_id(self) -> UUID:
        return uuid4()

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        rows = (
            self._session.query(OrderRow)
            .filter(OrderRow.customer_id == customer_id)
            .all()
        )
        return [OrderMapper.to_domain(row) for row in rows]
```

---

## 4. Unit of Work

### 4.1. Vấn đề

Giả sử bạn cần save 2 Aggregate trong cùng 1 transaction:

```python
order_repo = SqlAlchemyOrderRepository(session)
customer_repo = SqlAlchemyCustomerRepository(session)

order_repo.save(order)
customer_repo.save(customer)
# Ai commit? Ai rollback?
# Nếu save customer fail → order đã save → inconsistent
```

**Repository không nên tự commit.** Commit là **transaction boundary** — thuộc về một abstraction khác: **Unit of Work**.

### 4.2. Unit of Work là gì?

> **Unit of Work** là abstraction quản lý **transaction** và **tập hợp các Repository** liên quan. Nó đảm bảo mọi thay đổi hoặc commit cùng nhau, hoặc rollback cùng nhau.

### 4.3. Interface

```python
# application/uow.py
from types import TracebackType
from typing import Protocol

from shop.domain.repositories.customer_repository import CustomerRepository
from shop.domain.repositories.order_repository import OrderRepository


class UnitOfWork(Protocol):
    orders: OrderRepository
    customers: CustomerRepository

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...

    def commit(self) -> None:
        """Commit transaction."""
        ...

    def rollback(self) -> None:
        """Rollback transaction."""
        ...
```

**Điểm mấu chốt:**

- UoW **chứa** các Repository như attribute.
- UoW có `commit()`, `rollback()`.
- UoW hỗ trợ context manager (`__enter__`/`__exit__`).

### 4.4. In-memory UoW (cho test)

```python
# infrastructure/persistence/in_memory/uow.py
from types import TracebackType

from shop.infrastructure.persistence.in_memory.customer_repository import (
    InMemoryCustomerRepository,
)
from shop.infrastructure.persistence.in_memory.order_repository import (
    InMemoryOrderRepository,
)


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.orders = InMemoryOrderRepository()
        self.customers = InMemoryCustomerRepository()

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # In-memory không cần cleanup
        pass

    def commit(self) -> None:
        # In-memory tự động "commit" — không cần làm gì
        pass

    def rollback(self) -> None:
        # In-memory cần restore snapshot — phức tạp, thường bỏ qua
        pass
```

**Lưu ý:** In-memory UoW **không** rollback thật. Nếu test cần rollback, dùng SQLite in-memory với SQLAlchemy.

### 4.5. SQLAlchemy UoW

```python
# infrastructure/persistence/sqlalchemy/uow.py
from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from shop.infrastructure.persistence.sqlalchemy.customer_repository import (
    SqlAlchemyCustomerRepository,
)
from shop.infrastructure.persistence.sqlalchemy.order_repository import (
    SqlAlchemyOrderRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        event_bus,
    ) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._session: Session | None = None
        self._events: list = []

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session)
        self.customers = SqlAlchemyCustomerRepository(self._session)
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
        """Repository gọi method này khi save."""
        self._events.extend(events)

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()
        # Publish events SAU khi commit thành công
        for event in self._events:
            self._event_bus.publish(event)
        self._events.clear()

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()
        self._events.clear()
```

**Điểm mấu chốt:**

- `__enter__` mở session, tạo Repository.
- `__exit__` rollback nếu có exception, close session.
- `commit()` commit session, **sau đó** publish event.
- Repository gọi `collect_events()` khi save.

### 4.6. Repository tích hợp UoW

```python
class SqlAlchemyOrderRepository:
    def __init__(
        self,
        session: Session,
        uow: "SqlAlchemyUnitOfWork",
    ) -> None:
        self._session = session
        self._uow = uow

    def save(self, order: Order) -> None:
        row = OrderMapper.to_row(order)
        self._session.merge(row)
        # Collect events từ Aggregate
        self._uow.collect_events(order.pull_events())

    # ... các method khác
```

**Chú ý:**

- Repository **không** commit.
- Repository **không** publish event.
- Repository **collect** event vào UoW.
- UoW publish sau commit.

---

## 5. Dùng Repository + UoW trong Application Service

### 5.1. Application Handler

```python
# application/commands/place_order.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shop.application.uow import UnitOfWork
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
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            # 1. Kiểm tra customer tồn tại
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            # 2. Tạo Order
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
            order.place()

            # 3. Save
            self._uow.orders.save(order)

            # 4. Commit (UoW tự publish event)
            self._uow.commit()

        return order.id
```

**Điểm mấu chốt:**

- `with self._uow:` — mở transaction.
- Nếu exception → `__exit__` rollback.
- `commit()` — commit + publish event.
- Handler **không biết** là SQLAlchemy hay in-memory.

### 5.2. Query Handler — có thể đi thẳng DB

**Query không cần Aggregate, không cần UoW.**

```python
# application/queries/order_summary.py
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class OrderSummaryDTO:
    order_id: UUID
    customer_id: UUID
    total_amount: str
    status: str
    line_count: int


class OrderSummaryQuery:
    """Query — đọc thẳng DB, không qua Domain."""
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute(
            """
            SELECT
                o.id AS order_id,
                o.customer_id,
                SUM(l.unit_price_amount * l.quantity) AS total_amount,
                o.status,
                COUNT(l.id) AS line_count
            FROM orders o
            LEFT JOIN order_lines l ON l.order_id = o.id
            WHERE o.customer_id = :cid
            GROUP BY o.id, o.customer_id, o.status
            """,
            {"cid": str(customer_id)},
        ).fetchall()

        return [
            OrderSummaryDTO(
                order_id=row.order_id,
                customer_id=row.customer_id,
                total_amount=str(row.total_amount),
                status=row.status,
                line_count=row.line_count,
            )
            for row in rows
        ]
```

> 💡 **Nguyên tắc:** Write qua Aggregate + UoW. Read qua Query trực tiếp DB. Đây là CQRS nhẹ.

---

## 6. Transaction — Commit khi nào?

### 6.1. Nguyên tắc

> **1 transaction = 1 Aggregate** (lý tưởng).

**Nhưng thực tế:** 1 UoW có thể save nhiều Aggregate nếu cần ACID.

```python
# ✅ OK nếu cần ACID
with uow:
    uow.orders.save(order)
    uow.customers.save(customer)   # Cùng transaction
    uow.commit()

# ⚠️ Thường nên tách
with uow:
    uow.orders.save(order)
    uow.commit()

# Rồi event handler save customer
```

### 6.2. Rollback khi nào?

`__exit__` tự rollback nếu có exception:

```python
try:
    with uow:
        uow.orders.save(order)
        raise SomeError()   # ← Exception
        uow.commit()   # Không chạy
except SomeError:
    pass
# __exit__ gọi rollback
```

### 6.3. Save point — khi cần

Nếu cần partial rollback:

```python
with uow:
    uow.orders.save(order)
    # ...
    uow.savepoint("after_order")   # Không bắt buộc
    try:
        uow.payments.save(payment)
    except:
        uow.rollback_to("after_order")
    uow.commit()
```

**Khuyến nghị:** Tránh save point. Nếu cần → tách Aggregate.

---

## 7. Testing Repository + UoW

### 7.1. Unit test với in-memory

```python
# tests/unit/application/test_place_order.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.application.commands.place_order import (
    PlaceOrderCommand, PlaceOrderHandler, OrderItemInput,
)
from shop.domain.model.customer import Customer, CustomerStatus
from shop.shared.domain.email import Email
from shop.infrastructure.persistence.in_memory.uow import InMemoryUnitOfWork


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


def test_place_order_creates_order(uow: InMemoryUnitOfWork) -> None:
    # Arrange
    customer = Customer.register(Email("an@example.com"), "An")
    uow.customers.save(customer)
    uow.commit()

    handler = PlaceOrderHandler(uow)
    cmd = PlaceOrderCommand(
        customer_id=customer.id,
        items=[
            OrderItemInput(
                product_id=uuid4(),
                unit_price_amount=Decimal("100"),
                unit_price_currency="VND",
                quantity=2,
            ),
        ],
    )

    # Act
    order_id = handler.handle(cmd)

    # Assert
    order = uow.orders.find_by_id(order_id)
    assert order is not None
    assert order.status.value == "PLACED"
    assert order.total.amount == Decimal("200")


def test_place_order_with_unknown_customer_raises(uow: InMemoryUnitOfWork) -> None:
    handler = PlaceOrderHandler(uow)
    cmd = PlaceOrderCommand(
        customer_id=uuid4(),
        items=[],
    )
    with pytest.raises(CustomerNotFound):
        handler.handle(cmd)
```

**Đặc điểm:**

- **Không cần DB.**
- **Không cần mock.**
- **Chạy nhanh** (~milliseconds).
- Test **application layer** end-to-end (trừ DB).

### 7.2. Integration test với SQLite in-memory

```python
# tests/integration/test_sqlalchemy_order_repository.py
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shop.domain.model.order import Order
from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money
from shop.infrastructure.persistence.sqlalchemy.orm_models import Base
from shop.infrastructure.persistence.sqlalchemy.order_repository import (
    SqlAlchemyOrderRepository,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_save_and_find_order(session) -> None:
    repo = SqlAlchemyOrderRepository(session)

    order = Order.create(customer_id=uuid4())
    order.add_line(OrderLine.create(
        product_id=uuid4(),
        unit_price=Money(Decimal("100"), "VND"),
        quantity=2,
    ))
    order.place()

    repo.save(order)
    session.commit()

    loaded = repo.find_by_id(order.id)
    assert loaded is not None
    assert loaded.id == order.id
    assert loaded.status.value == "PLACED"
    assert loaded.total.amount == Decimal("200")
```

**Đặc điểm:**

- Dùng SQLite in-memory — nhanh, không cần setup.
- Test **mapping** thật sự.
- Chậm hơn in-memory thuần nhưng vẫn nhanh.

---

## 8. Tám anti-pattern khi dùng Repository/UoW

### ❌ Anti-pattern 1: Repository expose ORM

```python
# ❌ SAI: Domain biết ORM
class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> "OrderRow | None": ...
    def save(self, order: "OrderRow") -> None: ...
```

```python
# ✅ ĐÚNG: Domain model
class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
```

### ❌ Anti-pattern 2: Repository cho Entity con

```python
# ❌ SAI
class OrderLineRepository(Protocol):
    def find_by_id(self, line_id: UUID) -> OrderLine: ...
```

**Lý do:** Entity con chỉ được truy cập qua Aggregate Root.

### ❌ Anti-pattern 3: Repository chứa business logic

```python
# ❌ SAI
class OrderRepository:
    def save(self, order: Order) -> None:
        if order.total.amount > 1_000_000:
            order.status = "NEED_APPROVAL"   # Business logic!
        self._session.merge(...)
```

```python
# ✅ ĐÚNG
class Order:
    def place(self) -> None:
        if self.total.amount > 1_000_000:
            self._status = OrderStatus.NEED_APPROVAL
```

### ❌ Anti-pattern 4: Repository tự commit

```python
# ❌ SAI
class SqlAlchemyOrderRepository:
    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))
        self._session.commit()   # Repository không nên commit!
```

```python
# ✅ ĐÚNG: UoW commit
class SqlAlchemyOrderRepository:
    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))
        # Không commit — UoW sẽ commit
```

### ❌ Anti-pattern 5: Không tách ORM model và Domain model

```python
# ❌ SAI: Dùng chung class
class Order(Base):   # SQLAlchemy + Domain
    __tablename__ = "orders"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    # Domain methods + ORM columns trộn
    def place(self) -> None: ...
```

**Vấn đề:**

- Domain phụ thuộc SQLAlchemy.
- Không thể test pure Python.
- Migration schema ảnh hưởng Domain.

```python
# ✅ ĐÚNG: 2 class riêng
class Order:   # Domain
    ...

class OrderRow(Base):   # ORM
    ...
```

### ❌ Anti-pattern 6: Publish event trong Repository

```python
# ❌ SAI
class SqlAlchemyOrderRepository:
    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))
        for event in order.pull_events():
            self._event_bus.publish(event)   # Publish trước commit
```

```python
# ✅ ĐÚNG: UoW collect event, publish sau commit
class SqlAlchemyOrderRepository:
    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))
        self._uow.collect_events(order.pull_events())

class SqlAlchemyUnitOfWork:
    def commit(self) -> None:
        self._session.commit()
        for event in self._events:
            self._event_bus.publish(event)
```

### ❌ Anti-pattern 7: Query phức tạp trong Repository

```python
# ❌ SAI: Repository có query join phức tạp cho báo cáo
class OrderRepository:
    def get_sales_report(self, from_date, to_date) -> list[dict]:
        return self._session.execute("""
            SELECT ...
            FROM orders
            JOIN order_lines ...
            JOIN products ...
            JOIN customers ...
            JOIN ...
        """).fetchall()
```

```python
# ✅ ĐÚNG: Tách query ra read model
class SalesReportQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(self, from_date, to_date) -> list[SalesReportDTO]:
        ...
```

### ❌ Anti-pattern 8: UoW trong Domain

```python
# ❌ SAI: Domain biết UoW
class Order:
    def place(self, uow: UnitOfWork) -> None:
        self._status = OrderStatus.PLACED
        uow.orders.save(self)   # Domain gọi UoW!
```

```python
# ✅ ĐÚNG: Application Service điều phối
class PlaceOrderHandler:
    def handle(self, cmd) -> UUID:
        with self._uow:
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()
```

---

## 9. Ví dụ tổng hợp: Full stack Repository + UoW

### 9.1. Domain

```python
# domain/repositories/order_repository.py
from typing import Protocol
from uuid import UUID
from shop.domain.model.order import Order


class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def delete(self, order: Order) -> None: ...
    def next_id(self) -> UUID: ...
```

### 9.2. Application UoW Protocol

```python
# application/uow.py
from types import TracebackType
from typing import Protocol
from shop.domain.repositories.order_repository import OrderRepository
from shop.domain.repositories.customer_repository import CustomerRepository


class UnitOfWork(Protocol):
    orders: OrderRepository
    customers: CustomerRepository

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

### 9.3. Application Handler

```python
# application/commands/place_order.py
class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))
            order.place()

            self._uow.orders.save(order)
            self._uow.commit()

        return order.id
```

### 9.4. Infrastructure UoW

```python
# infrastructure/persistence/sqlalchemy/uow.py
class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory, event_bus) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._session = None
        self._events = []

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session, self)
        self.customers = SqlAlchemyCustomerRepository(self._session, self)
        return self

    def __exit__(self, exc_type, *args) -> None:
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()

    def collect_events(self, events: list) -> None:
        self._events.extend(events)

    def commit(self) -> None:
        self._session.commit()
        for event in self._events:
            self._event_bus.publish(event)
        self._events.clear()

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()
        self._events.clear()
```

### 9.5. Composition Root

```python
# bootstrap.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shop.infrastructure.messaging.in_memory_bus import InMemoryEventBus
from shop.infrastructure.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork


def build_uow(db_url: str) -> SqlAlchemyUnitOfWork:
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    event_bus = InMemoryEventBus()
    setup_event_handlers(event_bus)
    return SqlAlchemyUnitOfWork(session_factory, event_bus)
```

### 9.6. CLI/Presentation

```python
# presentation/cli/main.py
@click.command()
@click.argument("customer_id")
def place_order(customer_id: str) -> None:
    uow = build_uow("postgresql://...")
    handler = PlaceOrderHandler(uow)
    cmd = PlaceOrderCommand(
        customer_id=UUID(customer_id),
        items=[...],
    )
    order_id = handler.handle(cmd)
    click.echo(f"Đã đặt đơn: {order_id}")
```

---

## 10. Khi nào dùng gì?

| Tình huống | Dùng |
|---|---|
| Save/load 1 Aggregate | Repository |
| Save nhiều Aggregate trong 1 transaction | UoW |
| Query báo cáo phức tạp | Query riêng, không qua Repository |
| Test application layer | In-memory UoW |
| Test mapping | SQLite in-memory + SQLAlchemy |
| Production | SQLAlchemy UoW + Postgres/MySQL |

---

## 11. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Repository cho `Product`

Viết:

- `ProductRepository` Protocol ở Domain.
- `InMemoryProductRepository` ở Infrastructure.
- 5 method: `find_by_id`, `save`, `delete`, `next_id`, `find_by_sku`.

Viết ít nhất 6 test.

### 🟡 Bài tập 2 (trung bình): SQLAlchemy Repository

Cho Entity `Book`:

- Fields: `id`, `isbn`, `title`, `author`, `price (Money)`, `stock`, `created_at`.

Viết:

- `BookRow` (ORM model).
- `BookMapper` với `to_domain`, `to_row`.
- `SqlAlchemyBookRepository`.

Test với SQLite in-memory:
- Save + load.
- Update + load.
- Delete.
- Money được map đúng (amount + currency).

Viết ít nhất 10 test.

### 🔴 Bài tập 3 (khó): Full UoW + Event

Cho hệ thống e-commerce:

- Aggregates: `Order`, `Customer`, `Product`, `Payment`.
- Events: `OrderPlaced`, `PaymentReceived`, `StockReserved`.
- Handler: `PlaceOrderHandler` phát `OrderPlaced`, handler `CreatePaymentOnOrderPlaced` tạo Payment, handler `ReserveStockOnOrderPlaced` trừ stock Product.

**Yêu cầu:**

1. UoW Protocol với 4 Repository.
2. In-memory UoW cho test.
3. SQLAlchemy UoW cho production.
4. Repository collect event, UoW publish sau commit.
5. Test:
   - Happy path: Place order → tất cả handler chạy.
   - Fail path: 1 handler fail → rollback.
   - Idempotency: chạy handler 2 lần.
   - Rollback: exception giữa chừng.

Viết ít nhất 20 test.

---

## 12. Checklist sau bài 9

Trước khi sang bài 10, bạn phải tự tin trả lời:

- [ ] Repository là gì? Khác DAO chỗ nào?
- [ ] Tại sao Repository interface ở Domain, impl ở Infrastructure?
- [ ] Tại sao dùng `Protocol` thay `ABC`?
- [ ] Repository method nên đặt tên thế nào?
- [ ] `find_by_id` trả về `Order | None` hay raise? Tại sao?
- [ ] Unit of Work là gì? Tại sao cần?
- [ ] Khi nào commit? Khi nào rollback?
- [ ] Tại sao Repository không nên commit?
- [ ] Tại sao publish event sau commit?
- [ ] ORM model và Domain model — tách hay gộp? Tại sao?
- [ ] Mapper làm gì? Có mấy chiều?
- [ ] 8 anti-pattern khi dùng Repository/UoW?

Nếu trả lời được hết, bạn đã hoàn thành Level 2.

---

## 13. Tóm tắt bài 9

| Điểm | Nội dung |
|---|---|
| **Repository** | Abstraction cho persistence, interface ở Domain |
| **Khác DAO** | Repository làm việc với Aggregate, DAO với Table |
| **Protocol** | Dùng structural typing, không cần kế thừa |
| **Method** | `find_by_id`, `save`, `delete`, `next_id` |
| **ORM model** | Tách riêng khỏi Domain model |
| **Mapper** | Chuyển đổi 2 chiều: `to_domain`, `to_row` |
| **UoW** | Transaction boundary + chứa Repository |
| **Commit** | UoW commit, Repository không commit |
| **Publish event** | Sau commit, không trước |
| **Query** | Read model riêng, không qua Repository |
| **Test** | In-memory UoW (unit), SQLite (integration) |
| **8 anti-pattern** | Expose ORM, repo cho con, business logic, tự commit, không tách model, publish trong repo, query phức tạp, UoW trong Domain |

**Câu thần chú:** *"Repository là cửa vào persistence của Aggregate. UoW là transaction boundary. Domain không biết cả hai."*

---

## 14. Chúc mừng — Bạn đã hoàn thành Level 2!

Bạn đã đi qua **5 building blocks** quan trọng nhất của DDD:

1. **Value Object** (bài 5) — không có ID, so sánh giá trị.
2. **Entity** (bài 6) — có ID, có vòng đời.
3. **Aggregate** (bài 7) — cụm có consistency boundary.
4. **Domain Event** (bài 8) — kể chuyện nghiệp vụ.
5. **Repository + UoW** (bài 9) — cổng vào persistence.

Giờ bạn có đủ công cụ để mô hình hóa **hầu hết domain nghiệp vụ**.

---

## 15. Chuẩn bị cho Level 3

Bài tiếp theo: **Bài 10: Layered Architecture trong Python**.

Chuẩn bị:
- Đọc lại cấu trúc project từ bài 3.
- Nghĩ về **cách tổ chức code** thành 4 tầng: Presentation, Application, Domain, Infrastructure.
- Sẽ bàn: dependency rule, cách enforce bằng import-linter, và các biến thể (Hexagonal, Clean, Onion).

Level 3 sẽ đi sâu vào **kiến trúc** — cách tổ chức các building block đã học thành hệ thống hoàn chỉnh.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 10** (Level 3) ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: SQLAlchemy mapper chi tiết, Alembic migration, connection pool, transaction isolation.
5. **Review code Repository/UoW** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.