# 📖 Bài 8: Domain Event — Kể chuyện nghiệp vụ

> Bài 7 dạy bạn **Aggregate** — cụm Entity có consistency boundary. Bài 8 dạy bạn **Domain Event** — thứ kể lại "chuyện gì đã xảy ra" trong domain. Đây là building block biến hệ thống của bạn từ **"một đống object tĩnh"** thành **"một dòng chảy sự kiện sống động"**. Nó cũng là nền tảng của **event-driven architecture**, **CQRS**, và **Event Sourcing**.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Domain Event** là gì và tại sao nó quan trọng.
2. Phân biệt rõ **Domain Event** vs **Integration Event** vs **System Event**.
3. Biết **khi nào phát event**, **khi nào không**.
4. Viết event "chuẩn DDD" trong Python: `frozen=True`, có metadata, có ý nghĩa nghiệp vụ.
5. Xây dựng **Event Bus** đơn giản (in-memory).
6. Viết **Event Handler** để phản ứng với event.
7. Biết cách dùng event để **decouple các Aggregate**.
8. Tránh được **7 anti-pattern** khi dùng event.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Domain Event là gì?

### 1.1. Định nghĩa

> **Domain Event** là một sự kiện **đã xảy ra** trong domain, có **ý nghĩa nghiệp vụ** với các chuyên gia. Nó là **sự thật** — không thể thay đổi, không thể phủ nhận. Tên của nó luôn ở **thì quá khứ**.

### 1.2. Trực giác

Hãy nghĩ về **nhật ký ngân hàng**:

- `Ngày 1/10: Nạp 1 triệu`
- `Ngày 5/10: Rút 500k`
- `Ngày 10/10: Chuyển 200k cho An`
- `Ngày 15/10: Nhận lương 20 triệu`

Mỗi dòng là một **event** — chuyện đã xảy ra, không thể thay đổi. Bạn không "sửa" lịch sử; bạn chỉ thêm event mới.

Hãy nghĩ về **đơn hàng**:

- `OrderPlaced` — đơn đã được đặt.
- `OrderShipped` — đơn đã được gửi.
- `OrderDelivered` — đơn đã được giao.
- `OrderCancelled` — đơn đã bị hủy.

Mỗi event kể **một mẩu chuyện** trong vòng đời của đơn.

### 1.3. Đặc điểm của Domain Event

| Đặc điểm | Ý nghĩa |
|---|---|
| **Quá khứ** | Tên ở thì quá khứ: `OrderPlaced`, không `PlaceOrder` |
| **Bất biến** | Đã xảy ra thì không đổi — `frozen=True` |
| **Có ý nghĩa nghiệp vụ** | Business đọc hiểu ngay |
| **Có metadata** | `event_id`, `occurred_at` |
| **Có payload** | Dữ liệu cần thiết cho handler |

### 1.4. Ví dụ event kinh điển

| Domain | Event |
|---|---|
| E-commerce | `OrderPlaced`, `OrderShipped`, `PaymentReceived`, `ProductRestocked` |
| Banking | `MoneyDeposited`, `MoneyWithdrawn`, `AccountFrozen`, `TransferCompleted` |
| Booking | `BookingConfirmed`, `BookingCancelled`, `CheckInCompleted` |
| Library | `BookBorrowed`, `BookReturned`, `FineCharged` |
| HR | `EmployeeHired`, `EmployeePromoted`, `EmployeeResigned` |

---

## 2. Phân biệt 3 loại event

Đây là phần **rất quan trọng** mà nhiều dev nhầm lẫn.

### 2.1. Domain Event

**Định nghĩa:** Sự kiện **trong domain**, có ý nghĩa **nghiệp vụ**, được phát **trong cùng process**.

**Ví dụ:**

```python
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: Money
```

**Đặc điểm:**

- Được phát bởi **Aggregate**.
- Được xử lý **trong cùng transaction** hoặc **ngay sau commit**.
- **Không** đi qua message broker.
- Tên theo **nghiệp vụ**.

**Ai dùng:**

- Application Service để trigger tiếp hành động.
- Các Aggregate khác (qua event handler) để eventual consistent.
- Audit log nội bộ.

### 2.2. Integration Event

**Định nghĩa:** Sự kiện **giữa các hệ thống**, đi qua **message broker** (Kafka, RabbitMQ), dùng để **tích hợp**.

**Ví dụ:**

```json
{
  "event_type": "order.placed",
  "event_id": "evt_123",
  "occurred_at": "2026-09-19T10:30:00Z",
  "version": "1.0",
  "data": {
    "order_id": "ord_456",
    "customer_id": "cus_789",
    "total": {"amount": "1000000", "currency": "VND"}
  }
}
```

**Đặc điểm:**

- Được phát bởi **outbox pattern** hoặc **integration layer**.
- Đi qua **message broker**.
- **Phải** có schema ổn định (Published Language).
- **Phải** versioned.
- Tên theo **convention của hệ thống**.

**Ai dùng:**

- Hệ thống khác (Analytics, Notification, Billing...).
- Microservices.

### 2.3. System Event

**Định nghĩa:** Sự kiện **kỹ thuật**, không có ý nghĩa nghiệp vụ.

**Ví dụ:**

- `RequestReceived`
- `CacheMissed`
- `DatabaseConnected`
- `CircuitBreakerOpened`

**Đặc điểm:**

- Không thuộc domain.
- Dùng cho monitoring, observability.

### 2.4. Bảng so sánh

| Tiêu chí | Domain Event | Integration Event | System Event |
|---|---|---|---|
| **Ý nghĩa** | Nghiệp vụ | Tích hợp | Kỹ thuật |
| **Phạm vi** | Trong process | Giữa hệ thống | Trong hệ thống |
| **Broker** | Không | Có | Không |
| **Tên** | Theo nghiệp vụ | Theo convention | Theo cơ chế |
| **Ai phát** | Aggregate | Outbox | Framework |
| **Versioning** | Có thể | Bắt buộc | Không |
| **Ví dụ** | `OrderPlaced` | `order.placed.v1` | `CacheMissed` |

> 💡 **Bài học:** Domain Event là **nội bộ**. Integration Event là **ngoại vi**. Đừng nhầm lẫn. Khi cần publish ra ngoài, dùng **outbox pattern** để chuyển Domain Event thành Integration Event.

---

## 3. Khi nào phát event?

### 3.1. Nguyên tắc vàng

> **Phát event khi state của Aggregate thay đổi theo cách có ý nghĩa nghiệp vụ.**

### 3.2. Nên phát event

**1. Khi Aggregate chuyển state**

```python
def place(self) -> None:
    self._transition_to(OrderStatus.PLACED)
    self._events.append(OrderPlaced(...))   # ✅
```

**2. Khi một field quan trọng thay đổi**

```python
def change_email(self, new_email: Email) -> None:
    if new_email == self.email:
        return
    self._email = new_email
    self._events.append(CustomerEmailChanged(...))   # ✅
```

**3. Khi một Entity con được thêm/xóa**

```python
def add_line(self, line: OrderLine) -> None:
    self._lines[line.id] = line
    self._events.append(OrderLineAdded(...))   # ✅
```

**4. Khi một rule nghiệp vụ được kích hoạt**

```python
def mark_overdue(self) -> None:
    if not self._is_overdue():
        raise NotOverdue()
    self._status = InvoiceStatus.OVERDUE
    self._events.append(InvoiceOverdue(...))   # ✅
```

### 3.3. KHÔNG nên phát event

**1. Khi chỉ đọc dữ liệu**

```python
def total(self) -> Money:
    return sum(...)
    # Không phát event ở đây
```

**2. Khi reconstruct từ DB**

```python
@classmethod
def reconstruct(cls, ...) -> "Order":
    # Không phát event khi load từ DB
    return cls(...)
```

**3. Khi không có thay đổi**

```python
def change_email(self, new_email: Email) -> None:
    if new_email == self.email:
        return   # ✅ Không phát event nếu không đổi
    ...
```

**4. Khi event không có ý nghĩa nghiệp vụ**

```python
def update_timestamp(self) -> None:
    self._updated_at = datetime.now()
    # ❌ Không phát CustomerUpdated — vô nghĩa
```

**5. Khi cần chỉ để log kỹ thuật**

```python
def _cache_invalidate(self) -> None:
    # ❌ Không phát CacheInvalidated — đây là system event
    ...
```

### 3.4. Checklist khi quyết định phát event

Hỏi 3 câu:

1. **Business có quan tâm không?** → Nếu không, đừng phát.
2. **Business có gọi tên nó không?** → Nếu business gọi "đơn được đặt", phát `OrderPlaced`.
3. **Có handler nào cần biết không?** → Nếu không, có thể không cần.

---

## 4. Viết Domain Event chuẩn trong Python

### 4.1. Bộ khung

Đây là **bộ khung event** bạn sẽ dùng:

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class cho mọi Domain Event."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)
```

**Điểm mấu chốt:**

- `frozen=True` — event bất biến.
- `event_id` — để trace, deduplicate.
- `occurred_at` — khi event xảy ra.

### 4.2. Event cụ thể

```python
from decimal import Decimal
from shop.shared.domain.money import Money


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    customer_id: UUID = field(default=None)   # type: ignore
    total: Money = field(default=None)   # type: ignore
    line_count: int = 0
```

```python
@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    tracking_number: str = ""
    carrier: str = "GHN"
```

```python
@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    reason: str = ""
    cancelled_by: UUID | None = None
```

### 4.3. Nguyên tắc đặt tên

| Quy tắc | Ví dụ |
|---|---|
| **Thì quá khứ** | `OrderPlaced`, không `PlaceOrder` |
| **Cụ thể** | `CustomerEmailChanged`, không `CustomerUpdated` |
| **Có ngữ cảnh** | `OrderCancelledByCustomer`, không `Cancelled` |
| **Không viết tắt** | `InvoiceIssued`, không `InvIssued` |

### 4.4. Payload — chứa gì?

**Nguyên tắc:** Event chứa **đủ dữ liệu để handler không cần query lại** (nếu có thể).

```python
# ❌ SAI: Payload quá ít → handler phải query lại
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    # Handler phải query Order để biết total, customer...

# ✅ ĐÚNG: Payload đủ dùng
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: Money
    line_count: int
    placed_at: datetime
```

**Nhưng cũng đừng nhồi nhét:**

```python
# ❌ SAI: Payload quá nhiều
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: Money
    lines: list[OrderLine]   # ← Quá nhiều, nên chỉ chứa line_count
    customer_email: str      # ← Không cần, handler query nếu muốn
    customer_name: str
    # ... 20 field khác
```

> 💡 **Nguyên tắc:** Event chứa **dữ liệu nghiệp vụ cần thiết**, không phải **toàn bộ state của Aggregate**. Nếu handler cần thêm, nó tự query.

### 4.5. Aggregate phát event

```python
@dataclass(eq=False)
class Order:
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    _status: OrderStatus = OrderStatus.DRAFT
    _lines: dict[UUID, OrderLine] = field(default_factory=dict)
    _events: list = field(default_factory=list, repr=False)

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced(self.id)
        self._transition_to(OrderStatus.PLACED)
        self._events.append(
            OrderPlaced(
                order_id=self.id,
                customer_id=self.customer_id,
                total=self.total,
                line_count=len(self._lines),
            )
        )

    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
```

**Chú ý:** `_events` private, chỉ pull qua `pull_events()`.

---

## 5. Xây dựng Event Bus

### 5.1. Event Bus đơn giản (in-memory)

```python
from collections import defaultdict
from typing import Callable, TypeVar

T = TypeVar("T", bound=DomainEvent)


class EventBus:
    """
    In-memory event bus.

    - subscribe(event_type, handler): đăng ký handler cho loại event.
    - publish(event): gọi tất cả handler đã đăng ký.
    """
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        for handler in self._handlers[event_type]:
            handler(event)
```

**Cách dùng:**

```python
bus = EventBus()

def on_order_placed(event: OrderPlaced) -> None:
    print(f"Đơn {event.order_id} đã đặt, tổng {event.total}")

bus.subscribe(OrderPlaced, on_order_placed)

# Publish
bus.publish(OrderPlaced(order_id=uuid4(), total=Money(...), ...))
# "Đơn ... đã đặt, tổng ..."
```

### 5.2. Event Bus có priority

```python
from enum import IntEnum


class Priority(IntEnum):
    HIGH = 1
    NORMAL = 2
    LOW = 3


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[tuple[int, Callable]]] = defaultdict(list)

    def subscribe(
        self,
        event_type: type,
        handler: Callable,
        priority: Priority = Priority.NORMAL,
    ) -> None:
        self._handlers[event_type].append((priority, handler))
        self._handlers[event_type].sort(key=lambda x: x[0])

    def publish(self, event: DomainEvent) -> None:
        for _, handler in self._handlers[type(event)]:
            handler(event)
```

### 5.3. Event Bus với error handling

```python
import logging

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self, fail_fast: bool = False) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)
        self._fail_fast = fail_fast

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        errors = []
        for handler in self._handlers[type(event)]:
            try:
                handler(event)
            except Exception as e:
                logger.exception(
                    "Handler %s failed for event %s",
                    handler.__name__,
                    type(event).__name__,
                )
                errors.append(e)
                if self._fail_fast:
                    raise

        if errors and not self._fail_fast:
            logger.warning(
                "%d handler(s) failed for event %s",
                len(errors),
                type(event).__name__,
            )
```

### 5.4. Khi nào publish event?

Có **3 thời điểm** để publish:

**1. Ngay sau khi state thay đổi (trong cùng method)**

```python
def place(self) -> None:
    self._status = OrderStatus.PLACED
    self._events.append(OrderPlaced(...))
    # Chưa publish — chỉ lưu vào list
```

**2. Sau khi commit transaction (khuyến nghị)**

```python
class SqlAlchemyOrderRepository:
    def save(self, order: Order) -> None:
        self._session.merge(to_row(order))
        self._session.flush()
        # Chưa publish — đợi commit

# Trong Unit of Work
class SqlAlchemyUnitOfWork:
    def commit(self) -> None:
        self._session.commit()
        # Publish sau khi commit thành công
        for event in self._collected_events:
            self._event_bus.publish(event)
```

**3. Async (qua outbox pattern)**

```python
# Ghi event vào bảng "outbox" trong cùng transaction
# Một worker riêng đọc bảng outbox và publish ra broker
```

> ⚠️ **Quan trọng:** **KHÔNG** publish event **trước khi commit**. Nếu commit fail, event đã publish → handler thấy dữ liệu "ma".

---

## 6. Event Handler

### 6.1. Handler đơn giản

```python
class SendOrderConfirmationEmail:
    def __init__(self, email_service, customer_repo) -> None:
        self._email_service = email_service
        self._customer_repo = customer_repo

    def handle(self, event: OrderPlaced) -> None:
        customer = self._customer_repo.find_by_id(event.customer_id)
        if not customer:
            return
        self._email_service.send(
            to=customer.email,
            subject=f"Xác nhận đơn {event.order_id}",
            body=f"Đơn của bạn đã được đặt. Tổng: {event.total}",
        )
```

### 6.2. Handler với nhiều dependency

```python
class UpdateInventoryOnOrderPlaced:
    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._event_bus = event_bus

    def handle(self, event: OrderPlaced) -> None:
        with self._uow:
            for line in event.lines:
                product = self._uow.products.find_by_id(line.product_id)
                if product:
                    product.reduce_stock(line.quantity)
                    self._uow.products.save(product)
            self._uow.commit()
```

### 6.3. Handler idempotent

**Handler phải idempotent** — nếu chạy 2 lần với cùng event, kết quả phải như chạy 1 lần.

```python
class SendOrderConfirmationEmail:
    def __init__(self, email_service, sent_events_repo) -> None:
        self._email_service = email_service
        self._sent_events_repo = sent_events_repo

    def handle(self, event: OrderPlaced) -> None:
        # Check đã xử lý chưa
        if self._sent_events_repo.exists(event.event_id):
            return

        # Xử lý
        self._email_service.send(...)

        # Đánh dấu đã xử lý
        self._sent_events_repo.mark(event.event_id)
```

> 💡 **Lý do:** Event bus có thể **retry** khi handler fail. Handler phải chịu được retry.

### 6.4. Handler đăng ký vào bus

```python
def setup_event_handlers(
    bus: EventBus,
    uow: UnitOfWork,
    email_service,
    sent_events_repo,
) -> None:
    bus.subscribe(
        OrderPlaced,
        SendOrderConfirmationEmail(email_service, sent_events_repo).handle,
    )
    bus.subscribe(
        OrderPlaced,
        UpdateInventoryOnOrderPlaced(uow, bus).handle,
    )
    bus.subscribe(
        OrderCancelled,
        RefundPaymentOnOrderCancelled(uow).handle,
    )
```

---

## 7. Dùng Event để decouple các Aggregate

Đây là **lợi ích lớn nhất** của Domain Event.

### 7.1. Vấn đề: 2 Aggregate cần "nói chuyện"

**Không dùng event:**

```python
class PlaceOrderHandler:
    def __init__(self, uow, payment_service, inventory_service) -> None:
        ...

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(...)
            order.place()

            # Coupling chặt: Order biết cả Payment và Inventory
            self._payment_service.charge(order.customer_id, order.total)
            self._inventory_service.reserve(order.id, order.lines)

            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

**Vấn đề:**

- `PlaceOrderHandler` biết quá nhiều.
- Cần 2 service khác.
- Nếu Payment fail → rollback Order.
- Transaction quá lớn.
- Khó test.

### 7.2. Dùng event để decouple

```python
class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(...)
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()   # Chỉ save Order
        return order.id
```

**Event handler riêng:**

```python
class ChargePaymentOnOrderPlaced:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, event: OrderPlaced) -> None:
        # Xử lý trong transaction riêng
        with self._uow:
            payment = Payment.create(
                order_id=event.order_id,
                amount=event.total,
            )
            self._uow.payments.save(payment)
            self._uow.commit()


class ReserveInventoryOnOrderPlaced:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, event: OrderPlaced) -> None:
        with self._uow:
            for line in event.lines:
                product = self._uow.products.find_by_id(line.product_id)
                product.reserve(line.quantity)
                self._uow.products.save(product)
            self._uow.commit()
```

**Lợi ích:**

- `PlaceOrderHandler` **không biết** về Payment, Inventory.
- Mỗi handler là **1 transaction nhỏ**.
- Decoupled hoàn toàn.
- Dễ test.
- Dễ thêm handler mới (không sửa Order).

### 7.3. Khi nào dùng event để decouple?

| Tình huống | Dùng event | Gọi trực tiếp |
|---|---|---|
| Cần atomic giữa 2 aggregate | | ✅ |
| Có thể eventual consistent | ✅ | |
| Handler có thể fail độc lập | ✅ | |
| Nhiều handler cho 1 sự kiện | ✅ | |
| Handler cần chạy async | ✅ | |

---

## 8. Bảy anti-pattern khi dùng Domain Event

### ❌ Anti-pattern 1: Event ở thì hiện tại

```python
# ❌ SAI
@dataclass(frozen=True)
class PlaceOrder(DomainEvent):   # Hiện tại — không phải event!
    ...

# ✅ ĐÚNG
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):   # Quá khứ
    ...
```

### ❌ Anti-pattern 2: Event quá generic

```python
# ❌ SAI: Vô nghĩa
@dataclass(frozen=True)
class OrderUpdated(DomainEvent):
    order_id: UUID
    field_name: str   # "status"? "total"? Không ai biết
    old_value: str
    new_value: str
```

```python
# ✅ ĐÚNG: Cụ thể, có ý nghĩa nghiệp vụ
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: Money
```

### ❌ Anti-pattern 3: Event chứa Entity object

```python
# ❌ SAI: Event chứa cả Order object
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order: Order   # Object thật → serialization khó, coupling chặt
```

```python
# ✅ ĐÚNG: Event chứa dữ liệu cần thiết
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: Money
    line_count: int
```

### ❌ Anti-pattern 4: Publish event trước khi commit

```python
# ❌ SAI
def save(self, order: Order) -> None:
    self._session.merge(to_row(order))
    for event in order.pull_events():
        self._event_bus.publish(event)   # Publish trước commit
    self._session.commit()   # Nếu fail → event đã publish
```

```python
# ✅ ĐÚNG
def commit(self) -> None:
    self._session.commit()
    for event in self._collected_events:
        self._event_bus.publish(event)   # Publish sau commit
```

### ❌ Anti-pattern 5: Event handler gọi sync gây coupling

```python
# ❌ SAI: Handler A gọi trực tiếp Handler B
class OnOrderPlaced:
    def handle(self, event: OrderPlaced) -> None:
        self.email_handler.handle(event)   # Gọi trực tiếp
        self.inventory_handler.handle(event)
```

```python
# ✅ ĐÚNG: Đăng ký nhiều handler, event bus điều phối
bus.subscribe(OrderPlaced, email_handler.handle)
bus.subscribe(OrderPlaced, inventory_handler.handle)
```

### ❌ Anti-pattern 6: Event phát từ ngoài Aggregate

```python
# ❌ SAI: Service phát event
class OrderService:
    def place_order(self, order: Order) -> None:
        order._status = OrderStatus.PLACED
        self._event_bus.publish(OrderPlaced(...))   # Không phải việc của Service
```

```python
# ✅ ĐÚNG: Aggregate phát event
class Order:
    def place(self) -> None:
        self._status = OrderStatus.PLACED
        self._events.append(OrderPlaced(...))   # Aggregate phát
```

### ❌ Anti-pattern 7: Event handler có side effect không idempotent

```python
# ❌ SAI: Gửi email mỗi lần handler chạy
def handle(self, event: OrderPlaced) -> None:
    self._email_service.send(...)   # Nếu retry → gửi nhiều lần
```

```python
# ✅ ĐÚNG: Idempotent
def handle(self, event: OrderPlaced) -> None:
    if self._sent_events.exists(event.event_id):
        return
    self._email_service.send(...)
    self._sent_events.mark(event.event_id)
```

---

## 9. Ví dụ tổng hợp: E-commerce với Event

### 9.1. Domain events

```python
# domain/events/order_events.py
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from shop.shared.domain.money import Money


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    customer_id: UUID = field(default=None)   # type: ignore
    total: Money = field(default=None)   # type: ignore
    line_count: int = 0


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    tracking_number: str = ""


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: UUID = field(default=None)   # type: ignore
    reason: str = ""


@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID = field(default=None)   # type: ignore
    amount: Money = field(default=None)   # type: ignore
```

### 9.2. Aggregate phát event

```python
# domain/model/order.py
@dataclass(eq=False)
class Order:
    # ...
    _events: list = field(default_factory=list, repr=False)

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced(self.id)
        self._transition_to(OrderStatus.PLACED)
        self._events.append(
            OrderPlaced(
                order_id=self.id,
                customer_id=self.customer_id,
                total=self.total,
                line_count=len(self._lines),
            )
        )

    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events
```

### 9.3. Event bus

```python
# infrastructure/messaging/in_memory_bus.py
from collections import defaultdict
from typing import Callable

from shop.domain.events.order_events import DomainEvent


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
```

### 9.4. Handlers

```python
# application/handlers/on_order_placed.py
import logging

logger = logging.getLogger(__name__)


class SendOrderConfirmationEmail:
    def __init__(self, email_service, customer_repo, sent_events_repo) -> None:
        self._email_service = email_service
        self._customer_repo = customer_repo
        self._sent_events_repo = sent_events_repo

    def handle(self, event: OrderPlaced) -> None:
        if self._sent_events_repo.exists(event.event_id):
            return

        customer = self._customer_repo.find_by_id(event.customer_id)
        if not customer:
            logger.warning("Customer %s not found", event.customer_id)
            return

        self._email_service.send(
            to=customer.email,
            subject=f"Xác nhận đơn {event.order_id}",
            body=f"Tổng: {event.total}",
        )
        self._sent_events_repo.mark(event.event_id)


class ReserveInventory:
    def __init__(self, uow) -> None:
        self._uow = uow

    def handle(self, event: OrderPlaced) -> None:
        with self._uow:
            for line in event.lines:
                product = self._uow.products.find_by_id(line.product_id)
                if product:
                    product.reserve(line.quantity)
                    self._uow.products.save(product)
            self._uow.commit()
```

### 9.5. Unit of Work publish event sau commit

```python
# infrastructure/persistence/sqlalchemy/uow.py
class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory, event_bus) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._events: list = []

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session, self)
        self.products = SqlAlchemyProductRepository(self._session)
        return self

    def collect_events(self, events: list) -> None:
        self._events.extend(events)

    def commit(self) -> None:
        self._session.commit()
        # Publish sau khi commit thành công
        for event in self._events:
            self._event_bus.publish(event)
        self._events.clear()

    def __exit__(self, *args) -> None:
        self._session.close()
```

### 9.6. Repository collect event

```python
class SqlAlchemyOrderRepository:
    def __init__(self, session, uow) -> None:
        self._session = session
        self._uow = uow

    def save(self, order: Order) -> None:
        self._session.merge(self._to_row(order))
        self._uow.collect_events(order.pull_events())
```

### 9.7. Application Service

```python
class PlaceOrderHandler:
    def __init__(self, uow) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))
            order.place()
            self._uow.orders.save(order)
            self._uow.commit()   # Order saved + events published
        return order.id
```

### 9.8. Setup toàn bộ

```python
# bootstrap.py
def build_uow(session_factory, event_bus) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory, event_bus)


def build_event_bus(...) -> InMemoryEventBus:
    bus = InMemoryEventBus()
    bus.subscribe(OrderPlaced, SendOrderConfirmationEmail(...).handle)
    bus.subscribe(OrderPlaced, ReserveInventory(...).handle)
    return bus
```

**Điểm mấu chốt:**

- Aggregate phát event vào `_events`.
- Repository collect event khi save.
- UoW publish sau khi commit.
- Handler xử lý (idempotent).
- **Không handler nào biết handler nào.**

---

## 10. Testing Domain Event

```python
# tests/unit/domain/test_order_events.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.domain.model.order import Order
from shop.domain.model.order_line import OrderLine
from shop.domain.model.money import Money
from shop.domain.events.order_events import OrderPlaced


def make_line(price: str = "100", qty: int = 1) -> OrderLine:
    return OrderLine.create(
        product_id=uuid4(),
        unit_price=Money(Decimal(price), "VND"),
        quantity=qty,
    )


class TestOrderEvents:
    def test_place_emits_order_placed(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.pull_events()   # clear

        order.place()

        events = order.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], OrderPlaced)

    def test_order_placed_has_correct_payload(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line("100", 2))
        order.pull_events()

        order.place()

        event = order.pull_events()[0]
        assert event.order_id == order.id
        assert event.customer_id == order.customer_id
        assert event.total == Money(Decimal("200"), "VND")
        assert event.line_count == 1

    def test_pull_events_clears(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        order.pull_events()
        assert order.pull_events() == []

    def test_no_event_when_no_change(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        order.pull_events()   # clear

        # Gọi lại place → raise (đã placed)
        with pytest.raises(Exception):
            order.place()
```

```python
# tests/unit/application/test_event_bus.py
from uuid import uuid4

from shop.domain.events.order_events import OrderPlaced
from shop.infrastructure.messaging.in_memory_bus import InMemoryEventBus


class TestInMemoryEventBus:
    def test_subscribe_and_publish(self) -> None:
        bus = InMemoryEventBus()
        received = []

        bus.subscribe(OrderPlaced, lambda e: received.append(e))

        event = OrderPlaced(order_id=uuid4())
        bus.publish(event)

        assert received == [event]

    def test_multiple_handlers(self) -> None:
        bus = InMemoryEventBus()
        calls = []

        bus.subscribe(OrderPlaced, lambda e: calls.append("h1"))
        bus.subscribe(OrderPlaced, lambda e: calls.append("h2"))

        bus.publish(OrderPlaced(order_id=uuid4()))

        assert calls == ["h1", "h2"]

    def test_handler_not_called_for_other_event(self) -> None:
        bus = InMemoryEventBus()
        calls = []

        bus.subscribe(OrderPlaced, lambda e: calls.append(e))

        # Publish event khác
        bus.publish(SomeOtherEvent())

        assert calls == []
```

---

## 11. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Event cho `Customer`

Viết các Domain Event cho Entity `Customer`:

- `CustomerRegistered`
- `CustomerEmailChanged`
- `CustomerSuspended`
- `CustomerReactivated`
- `CustomerDeleted`

Mỗi event có `event_id`, `occurred_at`, và payload cần thiết.

Sau đó sửa `Customer` để phát event khi mỗi hành vi trên xảy ra.

Viết ít nhất 8 test case.

### 🟡 Bài tập 2 (trung bình): Event Bus với retry

Xây dựng `EventBus` có:

- `subscribe(event_type, handler, max_retries=3)`.
- Khi handler fail → retry tối đa `max_retries` lần.
- Log mỗi lần retry.
- Nếu fail hết → raise `HandlerFailed` (hoặc log + bỏ qua tùy config).
- Có method `publish_all(events)` publish nhiều event.

Viết ít nhất 10 test case, bao gồm test retry và test hết retry.

### 🔴 Bài tập 3 (khó): Full event-driven flow

Cho domain "đặt hàng":

- `Order` Aggregate phát `OrderPlaced`.
- Handler 1: `SendEmailOnOrderPlaced` — gửi email xác nhận.
- Handler 2: `ReserveInventoryOnOrderPlaced` — trừ stock Product.
- Handler 3: `CreatePaymentOnOrderPlaced` — tạo Payment ở trạng thái PENDING.
- Nếu `ReserveInventory` fail → phát `InventoryReservationFailed` → handler `CancelOrderOnInventoryFailed` hủy Order.
- Nếu `CreatePayment` fail → phát `PaymentCreationFailed` → handler `CancelOrderOnPaymentFailed`.

**Yêu cầu:**

1. Code đầy đủ các Aggregate, Event, Handler.
2. Unit of Work publish event sau commit.
3. Idempotent handlers.
4. Viết ít nhất 20 test case, bao gồm test:
   - Happy path: Order placed → tất cả handler chạy thành công.
   - Inventory fail → Order bị hủy.
   - Payment fail → Order bị hủy.
   - Retry handler.
   - Idempotency (chạy 2 lần cùng event).

---

## 12. Checklist sau bài 8

Trước khi sang bài 9, bạn phải tự tin trả lời:

- [ ] Domain Event là gì? Tại sao tên ở thì quá khứ?
- [ ] Domain Event vs Integration Event vs System Event?
- [ ] Khi nào nên phát event? 5 dấu hiệu?
- [ ] Khi nào KHÔNG nên phát event? 5 dấu hiệu?
- [ ] Payload của event chứa gì?
- [ ] Tại sao `frozen=True` cho event?
- [ ] Publish event khi nào — trước hay sau commit? Tại sao?
- [ ] Event handler phải idempotent — tại sao?
- [ ] Event bus hoạt động thế nào?
- [ ] Dùng event để decouple các Aggregate — lợi ích gì?
- [ ] 7 anti-pattern khi dùng event?

Nếu trả lời được hết, bạn đã sẵn sàng bài 9.

---

## 13. Tóm tắt bài 8

| Điểm | Nội dung |
|---|---|
| **Định nghĩa** | Domain Event = sự kiện quá khứ có ý nghĩa nghiệp vụ |
| **3 loại** | Domain Event, Integration Event, System Event |
| **Khi phát** | State đổi, field quan trọng đổi, con thêm/xóa, rule kích hoạt |
| **Không phát** | Đọc, reconstruct, không đổi, vô nghĩa, system event |
| **Bộ khung** | `@dataclass(frozen=True)` + `event_id` + `occurred_at` |
| **Event Bus** | Subscribe + publish, in-memory |
| **Publish** | Sau commit, không trước |
| **Handler** | Idempotent, có thể retry |
| **Decouple** | Event bus điều phối, handler không biết nhau |
| **7 anti-pattern** | Hiện tại, generic, chứa entity, publish trước commit, sync call, phát ngoài aggregate, không idempotent |
| **Test** | Pure Python, dễ test |

**Câu thần chú:** *"Event là sự thật đã xảy ra. Không sửa. Không phủ nhận. Chỉ thêm."*

---

## 14. Chuẩn bị cho bài 9

Bài tiếp theo: **Repository & Unit of Work — Cổng vào persistence**.

Chuẩn bị:
- Đọc lại các Protocol Repository đã viết trong bài 6, 7.
- Nghĩ về **cách lưu Aggregate vào DB** (SQLAlchemy, MongoDB...).
- Sẽ bàn: Repository interface ở Domain, implementation ở Infrastructure, Unit of Work pattern, cách xử lý transaction, cách test với in-memory repo.

Đây là bài **bản lề** giữa Domain và Infrastructure — bạn sẽ hiểu tại sao Repository là `Protocol` ở Domain, và implementation ở Infrastructure.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 9** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Outbox Pattern, Saga, Event Sourcing, Integration Event, Kafka/RabbitMQ.
5. **Review code Event** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.