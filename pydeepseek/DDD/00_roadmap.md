# 🐍 Lộ trình học Domain-Driven Design với Python

Chào bạn! Tôi sẽ đóng vai một **Python Developer** đã có kinh nghiệm với DDD, dẫn dắt bạn từ con số 0 đến khi có thể tự thiết kế hệ thống DDD hoàn chỉnh.

---

## 📋 Tổng quan lộ trình

Lộ trình chia thành **5 cấp độ** với **18 bài học**, mỗi bài có **lý thuyết + code Python thực hành**:

| Cấp độ | Chủ đề | Bài học | Thời lượng |
|--------|--------|---------|------------|
| 🟢 **Level 1** | Nền tảng DDD | Bài 1–4 | 1–2 tuần |
| 🟡 **Level 2** | Building Blocks | Bài 5–9 | 2–3 tuần |
| 🟠 **Level 3** | Kiến trúc & Patterns | Bài 10–13 | 2–3 tuần |
| 🔴 **Level 4** | Chiến lược (Strategic) | Bài 14–16 | 2 tuần |
| ⚫ **Level 5** | Chuyên sâu | Bài 17–18 | 2–4 tuần |

---

# 🟢 LEVEL 1 — NỀN TẢNG DDD

## 📖 Bài 1: DDD là gì? Tại sao Python dev cần biết?

### Mục tiêu
- Hiểu DDD giải quyết vấn đề gì.
- Phân biệt **CRUD mindset** vs **Domain mindset**.

### Lý thuyết
DDD ra đời bởi **Eric Evans (2003)** để giải quyết vấn đề: **"Phần mềm ngày càng phức tạp nhưng không phản ánh đúng nghiệp vụ."**

**Ví dụ kinh điển:** Hệ thống đặt vé máy bay.

```python
# ❌ CRUD mindset - chỉ là bảng dữ liệu
class Booking:
    def __init__(self, id, user_id, flight_id, status):
        self.id = id
        self.user_id = user_id
        self.flight_id = flight_id
        self.status = status  # "pending", "paid", "cancelled"
```

```python
# ✅ Domain mindset - có hành vi, có rule
from datetime import datetime, timedelta

class Booking:
    def __init__(self, booking_id, passenger, flight):
        self._id = booking_id
        self._passenger = passenger
        self._flight = flight
        self._status = BookingStatus.PENDING
        self._created_at = datetime.now()

    def confirm_payment(self, payment):
        if self._status != BookingStatus.PENDING:
            raise DomainError("Chỉ có thể thanh toán booking đang pending")
        if self._is_expired():
            raise DomainError("Booking đã hết hạn giữ chỗ")
        if payment.amount != self._flight.price:
            raise DomainError("Số tiền không khớp")
        self._status = BookingStatus.CONFIRMED

    def _is_expired(self):
        return datetime.now() - self._created_at > timedelta(minutes=15)
```

> 💡 **Insight:** DDD không phải là framework, không phải là thư viện. Nó là **cách tư duy** về phần mềm.

### Bài tập
Viết lại class `BankAccount` theo 2 phong cách: CRUD vs Domain. Chú ý các rule: không cho rút quá số dư, không cho nạp số âm.

---

## 📖 Bài 2: Ubiquitous Language — Ngôn ngữ chung

### Mục tiêu
- Hiểu tầm quan trọng của việc **đặt tên đúng theo nghiệp vụ**.
- Tránh "translation gap" giữa business và code.

### Lý thuyết
**Ubiquitous Language** = ngôn ngữ mà **cả team business và team dev** đều dùng, và **được thể hiện trực tiếp trong code**.

**Ví dụ sai:**
```python
class UserRecord:              # "Record" là từ kỹ thuật
    def update_status(self, s): # "status" là gì? update cái gì?
        ...
```

**Ví dụ đúng:**
```python
class Customer:                          # Ngôn ngữ nghiệp vụ
    def suspend_membership(self):        # Hành vi rõ ràng
        if self._has_unpaid_invoices():
            raise CannotSuspendWithDebt()
        self._membership_status = MembershipStatus.SUSPENDED
```

### Nguyên tắc
1. Nếu business gọi là "đơn hàng", code phải là `Order`, không phải `PurchaseRecord`.
2. Nếu business nói "duyệt", code phải là `approve()`, không phải `set_status(1)`.
3. Khi business thay đổi ngôn ngữ → **refactor code ngay**.

### Bài tập
Cho một domain **"thư viện"**. Liệt kê 15 thuật ngữ nghiệp vụ (Member, Loan, Fine, Reservation, Overdue...) và viết docstring mô tả từng cái. Sau đó code class cho mỗi thuật ngữ.

---

## 📖 Bài 3: Python + DDD — Những đặc trưng cần biết

### Mục tiêu
- Biết Python có gì **mạnh** và **yếu** khi làm DDD.
- Setup project DDD đầu tiên.

### Python mạnh ở đâu?
- **Dataclass** → viết Value Object cực gọn.
- **Type hints** → thể hiện ý định rõ ràng.
- **Protocol** → định nghĩa interface mà không cần kế thừa.
- **Duck typing** → linh hoạt cho Repository, Service.

### Python yếu ở đâu?
- **Không có access modifier thật** (`_private` chỉ là convention).
- **Không có compile-time check** → dễ vi phạm invariant.
- **Dynamic** → dễ "tiện tay" thêm method lung tung.

### Setup project
```bash
mkdir ddd-shop && cd ddd-shop
python -m venv .venv
source .venv/bin/activate
pip install pytest mypy pydantic
```

Cấu trúc:
```
ddd-shop/
├── src/
│   └── shop/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
├── tests/
├── pyproject.toml
└── README.md
```

Cài **mypy** và bật strict mode trong `pyproject.toml`:
```toml
[tool.mypy]
strict = true
```

> 💡 **Tip:** Strict mypy là "người bạn thân" của DDD trong Python — nó bắt lỗi type để bạn tập trung vào domain.

### Bài tập
Setup project `library-ddd/` với cấu trúc trên, cấu hình mypy strict, viết 1 test "hello world" chạy được.

---

## 📖 Bài 4: Bounded Context — Chia để trị

### Mục tiêu
- Hiểu tại sao **một model không thể dùng cho mọi thứ**.
- Biết cách chia hệ thống lớn thành các context.

### Lý thuyết
Cùng một từ **"Customer"** nhưng ý nghĩa khác nhau ở từng context:

| Context | "Customer" nghĩa là gì? |
|---------|------------------------|
| **Sales** | Người có thể mua hàng, có credit limit |
| **Shipping** | Người nhận hàng, có địa chỉ giao |
| **Support** | Người có ticket, có SLA |
| **Billing** | Người phải trả tiền, có payment method |

→ **Đừng cố làm 1 class `Customer` khổng lồ.** Hãy tách thành nhiều context.

### Ví dụ: Hệ thống E-commerce

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Catalog    │    │    Order     │    │   Payment    │
│  (sản phẩm)  │    │  (đơn hàng)  │    │ (thanh toán) │
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │
       └───────── Domain Events ───────────────┘
```

Mỗi context có:
- Model riêng
- Database riêng (lý tưởng)
- Team riêng
- Ngôn ngữ riêng

### Trong code Python
```python
# catalog/domain/product.py
@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: Money
    category: str

# order/domain/product.py  ← KHÁC HOÀN TOÀN
@dataclass(frozen=True)
class Product:
    sku: str
    name: str             # chỉ cần name để hiển thị
    unit_price: Money     # giá tại thời điểm đặt
```

> 💡 Cùng tên `Product` nhưng 2 context khác nhau → **2 class khác nhau**. Đây là điều đúng đắn, không phải trùng lặp.

### Bài tập
Cho hệ thống **"Bệnh viện"**. Xác định 4–5 bounded context (Khám bệnh, Xét nghiệm, Dược, Thanh toán...). Với mỗi context, liệt kê 5 khái niệm cốt lõi.

---

# 🟡 LEVEL 2 — BUILDING BLOCKS

## 📖 Bài 5: Value Object — Bất biến là sức mạnh

### Mục tiêu
- Phân biệt Entity vs Value Object.
- Viết Value Object chuẩn trong Python.

### Lý thuyết
**Value Object (VO)** = đối tượng **không có identity**, so sánh bằng **giá trị**.

- `Money(100, "USD")` == `Money(100, "USD")` → bằng nhau.
- Không có "Money #1" và "Money #2".

### Code Python chuẩn
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)   # frozen → immutable
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money không thể âm")
        if self.currency not in {"USD", "VND", "EUR"}:
            raise ValueError(f"Currency {self.currency} không hỗ trợ")

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        return Money(self.amount * factor, self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Không thể cộng 2 loại tiền khác nhau")

# Sử dụng
price = Money(Decimal("100.00"), "USD")
tax = Money(Decimal("10.00"), "USD")
total = price + tax  # Money(110.00, USD)

# Frozen → không thể sửa
price.amount = 200  # ❌ FrozenInstanceError
```

### Value Object phức tạp hơn: Email
```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.value):
            raise InvalidEmail(self.value)
        object.__setattr__(self, "value", self.value.lower())

    def domain(self) -> str:
        return self.value.split("@")[1]
```

### Khi nào dùng VO?
- Khi so sánh bằng giá trị (Money, Email, Address, DateRange, Coordinates).
- Khi cần validate (Email, PhoneNumber).
- Khi cần immutable (Config, Color, Measurement).

### Bài tập
Viết các VO sau (kèm validation + method hữu ích):
1. `Address(street, city, country, zip_code)`
2. `DateRange(start, end)` — có `overlaps(other)`, `duration_days()`
3. `PhoneNumber(value)` — validate format VN
4. `Percentage(value)` — 0–100, có `apply_to(money)`

---

## 📖 Bài 6: Entity — Có định danh, có vòng đời

### Mục tiêu
- Hiểu Entity khác gì VO.
- Quản lý vòng đời và identity.

### Lý thuyết
**Entity** = có **identity** (ID), tồn tại qua thời gian, có thể thay đổi trạng thái.

**Điểm mấu chốt:** Hai Entity cùng ID → coi là **cùng một đối tượng**, dù mọi field khác nhau.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4

class Entity:
    def __init__(self, id: UUID):
        self._id = id

    @property
    def id(self) -> UUID:
        return self._id

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._id == other._id

    def __hash__(self):
        return hash(self._id)
```

### Entity ví dụ: Customer
```python
from datetime import datetime

class Customer(Entity):
    def __init__(self, customer_id: UUID, email: Email, name: str):
        super().__init__(customer_id)
        self._email = email
        self._name = name
        self._status = CustomerStatus.ACTIVE
        self._created_at = datetime.now()
        self._events: list = []

    # Hành vi — không phải setter
    def change_email(self, new_email: Email) -> None:
        if new_email == self._email:
            return
        self._email = new_email
        self._events.append(CustomerEmailChanged(self.id, new_email))

    def suspend(self, reason: str) -> None:
        if self._status == CustomerStatus.SUSPENDED:
            raise AlreadySuspended()
        self._status = CustomerStatus.SUSPENDED
        self._events.append(CustomerSuspended(self.id, reason))

    def activate(self) -> None:
        if self._status == CustomerStatus.ACTIVE:
            raise AlreadyActive()
        self._status = CustomerStatus.ACTIVE
```

### Entity vs VO — Bảng so sánh

| Tiêu chí | Entity | Value Object |
|----------|--------|--------------|
| Identity | Có (UUID/ID) | Không |
| So sánh | Bằng ID | Bằng giá trị |
| Mutable | Có (state thay đổi) | Không (immutable) |
| Vòng đời | Dài | Ngắn, thay thế |
| Ví dụ | Customer, Order | Money, Email |

### Bài tập
Viết Entity `BankAccount` với:
- `deposit(money)` 
- `withdraw(money)` — không cho âm
- `transfer_to(other_account, money)` 
- Phát ra event `MoneyDeposited`, `MoneyWithdrawn`

---

## 📖 Bài 7: Aggregate & Aggregate Root — Bảo vệ invariant

### Mục tiêu
- Hiểu **Aggregate** là gì và tại sao cần.
- Xác định Aggregate Root đúng.

### Lý thuyết
**Aggregate** = một **cụm Entity + VO** được coi như **một đơn vị nhất quán (consistency boundary)**.

**Aggregate Root (AR)** = Entity **cổng vào duy nhất** của Aggregate.

**Quy tắc vàng:**
1. Chỉ AR được truy cập từ bên ngoài.
2. Chỉ AR có Repository.
3. Mọi thay đổi trong Aggregate phải đi qua AR.
4. **Một transaction = một Aggregate**.

### Ví dụ kinh điển: Order & OrderLine

```python
# ❌ SAI: OrderLine được truy cập trực tiếp
order_line = order_line_repo.find(line_id)
order_line.change_quantity(10)  # Vi phạm invariant!

# ✅ ĐÚNG: đi qua Order (Aggregate Root)
order = order_repo.find(order_id)
order.change_line_quantity(line_id, 10)  # Order kiểm tra invariant
```

### Code hoàn chỉnh

```python
class Order(Entity):   # Aggregate Root
    MAX_LINES = 50

    def __init__(self, order_id: UUID, customer_id: UUID):
        super().__init__(order_id)
        self._customer_id = customer_id
        self._lines: dict[UUID, OrderLine] = {}  # private!
        self._status = OrderStatus.DRAFT

    # Cổng vào duy nhất
    def add_product(self, product_id: UUID, price: Money, quantity: int) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable()
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines()
        
        line_id = uuid4()
        self._lines[line_id] = OrderLine(line_id, product_id, price, quantity)

    def change_line_quantity(self, line_id: UUID, new_quantity: int) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable()
        if line_id not in self._lines:
            raise LineNotFound()
        self._lines[line_id].change_quantity(new_quantity)

    def remove_line(self, line_id: UUID) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable()
        self._lines.pop(line_id, None)

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced()
        self._status = OrderStatus.PLACED
        self._events.append(OrderPlaced(self.id))

    @property
    def total(self) -> Money:
        return sum(
            (line.subtotal for line in self._lines.values()),
            Money(Decimal("0"), "USD"),
        )


class OrderLine(Entity):   # Không phải AR → không có repo
    def __init__(self, line_id, product_id, price, quantity):
        super().__init__(line_id)
        self._product_id = product_id
        self._price = price
        self._quantity = quantity

    def change_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise InvalidQuantity()
        if new_qty > 100:
            raise TooManyItems()
        self._quantity = new_qty

    @property
    def subtotal(self) -> Money:
        return self._price * Decimal(self._quantity)
```

### Cách xác định Aggregate
1. Cái gì **phải nhất quán ngay lập tức**? → cùng aggregate.
2. Cái gì có thể **eventually consistent**? → aggregate khác.
3. **Nhỏ là tốt** — aggregate lớn = lock lâu, conflict nhiều.

### Bài tập
Thiết kế aggregate cho **"Blog"**:
- `Post` (AR) chứa `Comment`
- Rule: không quá 500 comment, không comment khi post chưa publish
- Comment không được sửa trực tiếp, chỉ xóa qua Post

---

## 📖 Bài 8: Domain Event — Kể chuyện nghiệp vụ

### Mục tiêu
- Hiểu Domain Event là gì.
- Phát và xử lý event trong Python.

### Lý thuyết
**Domain Event** = "chuyện gì đó **đã xảy ra**" trong domain, có ý nghĩa với business.

Đặt tên ở **thì quá khứ**: `OrderPlaced`, `PaymentReceived`, `CustomerSuspended`.

### Code Python

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: UUID = field(default_factory=uuid4)

@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = None
    customer_id: UUID = None
    total: Money = None
```

### Thu thập event trong Aggregate

```python
class AggregateRoot(Entity):
    def __init__(self, id):
        super().__init__(id)
        self._events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events
```

### Repository tự động publish

```python
class OrderRepository:
    def __init__(self, session, event_bus):
        self._session = session
        self._bus = event_bus

    def save(self, order: Order) -> None:
        self._session.add(order)
        self._session.flush()
        for event in order.pull_events():
            self._bus.publish(event)
```

### Event Handler

```python
class SendOrderConfirmationEmail:
    def handle(self, event: OrderPlaced) -> None:
        customer = customer_repo.find(event.customer_id)
        email_service.send(customer.email, f"Đơn {event.order_id} đã được đặt")
```

> 💡 **Domain Event vs Integration Event:**
> - Domain Event: nội bộ, trong 1 process.
> - Integration Event: public ra ngoài, qua message broker (Kafka, RabbitMQ).

### Bài tập
Trong aggregate `BankAccount`, phát event `MoneyDeposited` và `MoneyWithdrawn`. Viết handler gửi SMS khi số dư < 100k.

---

## 📖 Bài 9: Repository & Unit of Work

### Mục tiêu
- Định nghĩa Repository interface ở Domain.
- Triển khai với SQLAlchemy ở Infrastructure.

### Lý thuyết
**Repository** = abstraction che giấu persistence, giúp Domain không biết gì về DB.

**Nguyên tắc:**
- Interface ở **Domain**.
- Implementation ở **Infrastructure**.
- **Chỉ cho Aggregate Root**.

### Interface (Domain)

```python
from typing import Protocol
from uuid import UUID

class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def next_id(self) -> UUID: ...
```

> 💡 Dùng `Protocol` thay vì `ABC` — Pythonic hơn, không cần kế thừa.

### Implementation (Infrastructure) với SQLAlchemy

```python
from sqlalchemy.orm import Session

class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = self._session.get(OrderModel, order_id)
        return self._to_domain(row) if row else None

    def save(self, order: Order) -> None:
        model = self._to_model(order)
        self._session.merge(model)
        self._session.flush()

    def _to_domain(self, row) -> Order:
        # mapping DB row → domain object
        ...

    def _to_model(self, order: Order):
        # mapping domain → DB row
        ...
```

### Unit of Work

```python
class UnitOfWork(Protocol):
    orders: OrderRepository
    customers: CustomerRepository
    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *args) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

### Dùng trong Application Service

```python
class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order(uow.orders.next_id(), cmd.customer_id)
            for item in cmd.items:
                order.add_product(item.product_id, item.price, item.qty)
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

### Bài tập
- Viết `InMemoryOrderRepository` (dùng dict) để test.
- Viết test cho `PlaceOrderHandler` với in-memory UoW.

---

# 🟠 LEVEL 3 — KIẾN TRÚC & PATTERNS

## 📖 Bài 10: Layered Architecture trong Python

### Mục tiêu
- Hiểu 4 tầng và dependency rule.
- Tổ chức project Python chuẩn.

### Sơ đồ dependency

```
Presentation → Application → Domain ← Infrastructure
```

> Domain **không phụ thuộc ai**. Infrastructure phụ thuộc Domain (implements interface).

### Ví dụ cấu trúc

```
shop/
├── domain/
│   ├── model/
│   │   ├── order.py
│   │   ├── customer.py
│   │   └── money.py
│   ├── events/
│   ├── repositories/       # Protocol
│   └── exceptions.py
│
├── application/
│   ├── commands/
│   │   └── place_order.py
│   ├── queries/
│   └── dto.py
│
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlalchemy/
│   │   └── in_memory/
│   ├── messaging/
│   └── external/
│
└── presentation/
    ├── api/
    │   └── fastapi/
    └── cli/
```

### Kiểm soát dependency bằng import-linter

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["shop"]

[[tool.importlinter.contracts]]
name = "Domain không phụ thuộc ai"
type = "forbidden"
source_modules = ["shop.domain"]
forbidden_modules = ["shop.application", "shop.infrastructure", "shop.presentation"]
```

### Bài tập
Setup project `shop/` với 4 layer trên, viết `import-linter` để enforce.

---

## 📖 Bài 11: Application Service & CQRS

### Mục tiêu
- Phân biệt Command vs Query.
- Viết Application Service mỏng.

### Lý thuyết
- **Command** = thay đổi state (Write).
- **Query** = đọc state (Read).
- **CQRS** = Command Query Responsibility Segregation.

### Command

```python
@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemDTO]
```

### Handler

```python
class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus):
        self._uow = uow
        self._bus = event_bus

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order(self._uow.orders.next_id(), cmd.customer_id)
            for item in cmd.items:
                order.add_product(item.product_id, item.price, item.quantity)
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()

        for event in order.pull_events():
            self._bus.publish(event)

        return order.id
```

### Query — có thể bỏ qua domain, query trực tiếp DB

```python
class OrderSummaryQuery:
    def __init__(self, session: Session):
        self._session = session

    def execute(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute("""
            SELECT o.id, o.total, o.status, o.created_at
            FROM orders o WHERE o.customer_id = :cid
        """, {"cid": customer_id})
        return [OrderSummaryDTO(**row) for row in rows]
```

> 💡 Query **không cần** đi qua Aggregate — chỉ cần DTO cho UI. Đây là "read model".

### Bài tập
Viết:
- Command `CancelOrderCommand` + handler.
- Query `GetTopSellingProductsQuery` trả về DTO.

---

## 📖 Bài 12: Domain Service & Specification

### Mục tiêu
- Biết khi nào logic không thuộc Entity/VO.
- Viết Specification pattern.

### Domain Service
Khi logic **liên quan nhiều aggregate** hoặc **không thuộc về 1 entity nào**.

```python
class TransferService:
    """Chuyển tiền giữa 2 tài khoản."""
    def __init__(self, account_repo: AccountRepository):
        self._repo = account_repo

    def transfer(self, from_id: UUID, to_id: UUID, amount: Money) -> None:
        source = self._repo.find_by_id(from_id)
        target = self._repo.find_by_id(to_id)

        # Rule nghiệp vụ: không chuyển nếu vi phạm hạn mức ngày
        if self._exceeds_daily_limit(source, amount):
            raise DailyLimitExceeded()

        source.withdraw(amount)
        target.deposit(amount)

        self._repo.save(source)
        self._repo.save(target)
```

> ⚠️ **Cảnh báo:** Không nên quá lạm dụng Domain Service. Nếu có thể đặt trong Entity → ưu tiên Entity.

### Specification

```python
from abc import ABC, abstractmethod

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool: ...

    def __and__(self, other):
        return AndSpec(self, other)

    def __or__(self, other):
        return OrSpec(self, other)


class PremiumCustomer(Specification):
    def is_satisfied_by(self, customer) -> bool:
        return customer.total_spent > Money(Decimal("1000"), "USD")


class ActiveCustomer(Specification):
    def is_satisfied_by(self, customer) -> bool:
        return customer.status == CustomerStatus.ACTIVE


# Kết hợp
eligible = ActiveCustomer() & PremiumCustomer()
if eligible.is_satisfied_by(customer):
    give_discount(customer)
```

### Bài tập
Viết `Specification` cho **"Order có thể hủy"**:
- Đang ở trạng thái DRAFT hoặc PLACED.
- Chưa quá 1 giờ kể từ khi placed.

---

## 📖 Bài 13: Dependency Injection trong Python

### Mục tiêu
- Không dùng framework nặng, dùng **manual DI**.
- Testable code.

### Manual DI — đơn giản nhất

```python
# composition_root.py
def build_container(config):
    session = create_session(config.db_url)
    event_bus = InMemoryEventBus()

    order_repo = SqlAlchemyOrderRepository(session)
    customer_repo = SqlAlchemyCustomerRepository(session)

    uow = SqlAlchemyUnitOfWork(session, order_repo, customer_repo)
    place_order_handler = PlaceOrderHandler(uow, event_bus)

    return {
        "place_order": place_order_handler,
    }


# main.py
container = build_container(config)
container["place_order"].handle(PlaceOrderCommand(...))
```

### Test với in-memory

```python
def test_place_order():
    uow = InMemoryUnitOfWork()
    bus = FakeEventBus()
    handler = PlaceOrderHandler(uow, bus)

    cmd = PlaceOrderCommand(
        customer_id=uuid4(),
        items=[OrderItemDTO(product_id=uuid4(), price=Money(Decimal("10"), "USD"), quantity=2)]
    )
    order_id = handler.handle(cmd)

    order = uow.orders.find_by_id(order_id)
    assert order.status == OrderStatus.PLACED
    assert bus.published[0].__class__ is OrderPlaced
```

> 💡 Python mạnh ở đây: không cần `@Inject`, không cần Spring. **Function composition** là đủ.

### Bài tập
Viết `composition_root.py` cho shop project. Test handler với in-memory.

---

# 🔴 LEVEL 4 — STRATEGIC DDD

## 📖 Bài 14: Context Mapping

### Mục tiêu
- Biết các pattern tích hợp giữa các Bounded Context.

### Các pattern chính

| Pattern | Khi nào dùng |
|---------|--------------|
| **Shared Kernel** | 2 team chia sẻ model chung (rủi ro cao) |
| **Customer/Supplier** | 1 context phụ thuộc context kia |
| **Conformist** | Context downstream chấp nhận model upstream |
| **Anti-Corruption Layer (ACL)** | Downstream tự bảo vệ khỏi model upstream |
| **Published Language** | Chuẩn chung (JSON schema, Protobuf) |
| **Open Host Service** | Cung cấp API công khai cho nhiều consumer |
| **Separate Ways** | Không tích hợp — mỗi context tự lo |

### ACL — quan trọng nhất

```python
# order/infrastructure/catalog_acl.py
class CatalogACL:
    """Chuyển đổi model từ Catalog context sang Order context."""

    def __init__(self, catalog_client: CatalogClient):
        self._client = catalog_client

    def get_product_snapshot(self, sku: str) -> OrderProductSnapshot:
        dto = self._client.get_product(sku)   # dữ liệu thô từ context khác
        return OrderProductSnapshot(
            sku=dto["sku"],
            name=dto["display_name"],
            unit_price=Money(Decimal(dto["price"]), dto["currency"]),
        )
```

→ Order context **không bị ảnh hưởng** nếu Catalog đổi schema.

### Bài tập
Vẽ context map cho hệ thống **"Ví điện tử"**: Wallet, User, Transaction, Notification, Fraud Detection. Chỉ định pattern cho từng cặp.

---

## 📖 Bài 15: Event Storming

### Mục tiêu
- Biết cách khám phá domain cùng business.

### Các sticky notes chính
- 🟧 **Domain Event** (quá khứ): `Order Placed`
- 🟦 **Command** (hành động): `Place Order`
- 🟨 **Aggregate**: `Order`
- 🟪 **Actor**: `Customer`
- 🟩 **Policy**: "Khi X thì Y"
- 🟥 **Hotspot**: vấn đề chưa rõ

### Quy trình
1. **Big Picture** — vẽ toàn cảnh, mọi event theo thời gian.
2. **Process Level** — thêm command, actor, policy.
3. **Design Level** — thêm aggregate, bounded context.

### Ví dụ đơn giản (text-based)

```
Actor: Customer
  │
  ├─ Command: Place Order
  │     ↓
  │   Aggregate: Order
  │     ↓
  │   Event: Order Placed
  │     ↓
  │   Policy: "Khi Order Placed → gửi email xác nhận"
  │     ↓  │   Command: Send Confirmation Email
  │     ↓
  │   Event: Email Sent
```

### Bài tập
Chạy event storming (một mình cũng được) cho domain **"đặt vé xem phim"**. Liệt kê ít nhất 15 events theo trình tự thời gian.

---

## 📖 Bài 16: Chiến lược chọn Bounded Context

### Mục tiêu
- Biết **khi nào tách**, **khi nào gộp** context.

### Dấu hiệu nên tách
1. Cùng từ nhưng nghĩa khác nhau.
2. 2 nhóm người dùng khác nhau.
3. Thay đổi với tốc độ khác nhau.
4. Team ownership khác nhau.

### Dấu hiệu không nên tách
1. Cần transaction ACID xuyên suốt → cùng context.
2. Team nhỏ (< 5 người) → 1 context có thể đủ.
3. Chưa rõ domain → đừng tách sớm.

### Ví dụ: Monolith vs Microservices

**Monolith modular** (khuyến nghị cho hầu hết team):
```
shop/
├── catalog/        ← module, có thể tách sau
├── order/
├── payment/
└── shared/         ← shared kernel cẩn thận
```

**Microservices** (chỉ khi cần):
- Mỗi context = 1 service.
- Giao tiếp qua events (Kafka, RabbitMQ).
- **Không** share database.

### Bài tập
Cho hệ thống **"quản lý trường học"**. Vẽ 3–4 bounded context. Với mỗi context, chỉ định:
- Team nào sở hữu?
- Database riêng hay chung?
- Giao tiếp qua gì?

---

# ⚫ LEVEL 5 — CHUYÊN SÂU

## 📖 Bài 17: Event Sourcing với Python

### Mục tiêu
- Hiểu Event Sourcing.
- Implement đơn giản.

### Lý thuyết
Thay vì lưu **state hiện tại**, lưu **chuỗi event**.

```
Traditional:  Account(id=1, balance=100)
Event Sourcing: [Opened(0), Deposited(50), Deposited(70), Withdrawn(20)]
```

### Code

```python
class EventSourcedAggregate:
    def __init__(self, id):
        self._id = id
        self._version = 0
        self._changes: list[DomainEvent] = []

    @classmethod
    def from_history(cls, id, events: list[DomainEvent]):
        obj = cls.__new__(cls)
        obj._id = id
        obj._version = 0
        obj._changes = []
        for event in events:
            obj._apply(event)
            obj._version += 1
        return obj

    def _apply(self, event: DomainEvent) -> None:
        handler = getattr(self, f"_on_{type(event).__name__}", None)
        if handler:
            handler(event)

    def _raise(self, event: DomainEvent) -> None:
        self._apply(event)
        self._changes.append(event)
        self._version += 1

    def pull_changes(self):
        changes = self._changes[:]
        self._changes.clear()
        return changes


class BankAccount(EventSourcedAggregate):
    def __init__(self, account_id):
        super().__init__(account_id)
        self._balance = Money(Decimal("0"), "USD")

    def deposit(self, amount: Money) -> None:
        if amount.amount <= 0:
            raise ValueError("Phải > 0")
        self._raise(MoneyDeposited(self.id, amount))

    def withdraw(self, amount: Money) -> None:
        if amount.amount > self._balance.amount:
            raise InsufficientFunds()
        self._raise(MoneyWithdrawn(self.id, amount))

    # Event handlers
    def _on_MoneyDeposited(self, event):
        self._balance = self._balance + event.amount

    def _on_MoneyWithdrawn(self, event):
        self._balance = self._balance - event.amount
```

### Event Store

```python
class EventStore:
    def __init__(self, session):
        self._session = session

    def append(self, aggregate_id, events, expected_version):
        for e in events:
            self._session.add(EventRow(
                aggregate_id=aggregate_id,
                version=expected_version + 1,
                event_type=type(e).__name__,
                payload=json.dumps(asdict(e), default=str),
            ))
            expected_version += 1

    def load(self, aggregate_id) -> list[DomainEvent]:
        rows = self._session.query(EventRow).filter_by(
            aggregate_id=aggregate_id
        ).order_by(EventRow.version).all()
        return [deserialize(row) for row in rows]
```

### Ưu / nhược
| Ưu | Nhược |
|----|-------|
| Audit log tự nhiên | Phức tạp |
| Time travel, replay | Schema evolution khó |
| Event-driven dễ | Query khó → cần CQRS |
| Debug tốt | Team phải hiểu mới làm được |

### Bài tập
Viết `Order` theo Event Sourcing: `OrderCreated`, `ProductAdded`, `OrderPlaced`, `OrderCancelled`. Replay để có state.

---

## 📖 Bài 18: Tích hợp — DDD + FastAPI + SQLAlchemy (project hoàn chỉnh)

### Mục tiêu
- Ghép mọi thứ thành **project thực tế**.

### Cấu trúc cuối cùng

```
shop/
├── domain/
│   ├── model/
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── money.py
│   ├── events/
│   ├── repositories/       # Protocol
│   └── exceptions.py
│
├── application/
│   ├── commands/
│   │   ├── place_order.py
│   │   └── cancel_order.py
│   ├── queries/
│   └── ports/              # interface cho email, payment...
│
├── infrastructure/
│   ├── persistence/
│   │   ├── models.py       # SQLAlchemy ORM
│   │   ├── mapper.py       # Domain ↔ ORM
│   │   ├── repositories.py
│   │   └── uow.py
│   ├── email/
│   │   └── smtp.py
│   └── messaging/
│       └── in_memory_bus.py
│
├── presentation/
│   └── api/
│       ├── main.py         # FastAPI app
│       ├── routes/
│       └── dependencies.py
│
└── composition_root.py
```

### FastAPI route

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class PlaceOrderRequest(BaseModel):
    customer_id: UUID
    items: list[OrderItemRequest]

@router.post("/orders")
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
):
    cmd = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[OrderItemDTO(**i.dict()) for i in request.items],
    )
    order_id = handler.handle(cmd)
    return {"order_id": order_id}
```

### End-to-end test

```python
def test_place_order_end_to_end(client):
    # Arrange
    customer_id = client.post("/customers", json={...}).json()["id"]

    # Act
    response = client.post("/orders", json={
        "customer_id": customer_id,
        "items": [{"product_id": str(uuid4()), "price": "10.00", "quantity": 2}],
    })

    # Assert
    assert response.status_code == 201
    order_id = response.json()["order_id"]
    detail = client.get(f"/orders/{order_id}").json()
    assert detail["status"] == "PLACED"
```

### Bài tập cuối khóa
Xây dựng project hoàn chỉnh **"Hệ thống đặt hàng"** với:
- ✅ 2 Bounded Context: `catalog`, `order`
- ✅ Aggregate `Order` với invariant
- ✅ Domain Events + Event Bus
- ✅ Repository pattern + SQLAlchemy
- ✅ CQRS: Command (write) + Query (read)
- ✅ FastAPI presentation
- ✅ Test coverage ≥ 80% cho domain layer
- ✅ import-linter bảo vệ dependency rule

---

# 🎯 Tổng kết lộ trình

```
Level 1 ──→ Level 2 ──→ Level 3 ──→ Level 4 ──→ Level 5
Nền tảng    Building    Kiến trúc   Chiến lược  Chuyên sâu
            Blocks      & Patterns
   4 bài       5 bài       4 bài       3 bài       2 bài
```

## 📚 Sách nên đọc
1. **"Domain-Driven Design"** — Eric Evans (cuốn gốc, khó nhưng phải đọc).
2. **"Implementing Domain-Driven Design"** — Vaughn Vernon (thực dụng hơn).
3. **"Architecture Patterns with Python"** — Percival & Gregory (**BẮT BUỘC** cho Python dev, có free online tại cosmicpython.com).
4. **"Learning Domain-Driven Design"** — Vlad Khononov (nhập môn tốt).

## 🛠️ Tools Python cho DDD
- **pydantic** — validate DTO, VO
- **SQLAlchemy** — ORM cho Infrastructure
- **FastAPI** — presentation layer
- **dependency-injector** — nếu cần DI framework (không bắt buộc)
- **import-linter** — enforce dependency rule
- **mypy strict** — type safety
- **pytest** — test

---

## 🚀 Bạn muốn bắt đầu từ đâu?

Tôi có thể:
1. **Viết code chi tiết** cho một bài cụ thể (VD: "Bài 7 — Aggregate với ví dụ đầy đủ").
2. **Cho bài tập + review** khi bạn làm xong.
3. **Đi sâu vào 1 chủ đề** (Event Sourcing, CQRS, ACL...).
4. **Hướng dẫn build 1 project hoàn chỉnh** từ đầu đến cuối.

👉 Nói cho tôi biết bạn **đang ở level nào** và **muốn học bài nào trước** — tôi sẽ dạy chi tiết bài đó với đầy đủ code Python, ví dụ, và bài tập.