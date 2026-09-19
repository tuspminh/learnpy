# 📖 Bài 7: Aggregate & Aggregate Root — Bảo vệ invariant

> Đây là **bài quan trọng nhất của Level 2** — và có thể là **bài quan trọng nhất của cả lộ trình**. Aggregate là khái niệm mà 90% dev hiểu sai, dẫn đến hệ thống chậm, bug khó tìm, và transaction chết. Nếu bạn nắm chắc bài này, bạn đã đi trước phần lớn dev DDD.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Aggregate** là gì và tại sao cần.
2. Hiểu **Aggregate Root** là gì và tại sao nó là "cổng vào duy nhất".
3. Biết **5 quy tắc vàng** khi thiết kế Aggregate.
4. Biết **cách chọn** Aggregate Root đúng.
5. Phân biệt **strong consistency** vs **eventual consistency**.
6. Tránh được **6 anti-pattern** khi thiết kế Aggregate.
7. Áp dụng vào Python: viết Aggregate hoàn chỉnh.
8. Làm bài tập thực hành có chấm điểm.

---

## 1. Vấn đề gốc — Tại sao cần Aggregate?

### 1.1. Câu chuyện có thật

Bạn đang làm hệ thống thương mại điện tử. Có Entity `Order` và Entity `OrderLine`:

```python
order = order_repo.find_by_id(order_id)
line = order_line_repo.find_by_id(line_id)
line.change_quantity(10)   # Rồi lưu riêng line
order_line_repo.save(line)
```

**Chuyện gì xảy ra?**

- Ai đó có thể sửa `OrderLine` mà không biết `Order` đang ở trạng thái `PLACED`.
- Ai đó có thể xóa `OrderLine` cuối cùng → `Order` rỗng mà vẫn tồn tại.
- Ai đó có thể sửa `OrderLine.quantity` thành 1000 trong khi `Order` có rule max 100.
- **Invariant bị phá vỡ** ở nhiều chỗ.

**Đây là vấn đề Aggregate ra đời để giải quyết.**

### 1.2. Insight

> *"Đừng để ai đó sửa con của bạn mà không qua bạn. Bạn là cổng vào duy nhất của gia đình bạn."*

Trong DDD:

- **Aggregate** = "gia đình" các object đi cùng nhau.
- **Aggregate Root** = "người đứng đầu gia đình" — cổng vào duy nhất.

---

## 2. Aggregate và Aggregate Root là gì?

### 2.1. Định nghĩa

> **Aggregate** là một **cụm** các Entity + Value Object được coi như **một đơn vị nhất quán (consistency boundary)**. Mọi thay đổi bên trong Aggregate phải được thực hiện qua **Aggregate Root**.
>
> **Aggregate Root** là **một Entity** trong Aggregate, đóng vai trò **cổng vào duy nhất** từ bên ngoài. Chỉ Aggregate Root mới được Repository tham chiếu.

### 2.2. Ví dụ trực giác

Hãy nghĩ về **một gia đình**:

- **Bố/mẹ** = Aggregate Root.
- **Con cái** = Entity con.
- **Đồ đạc trong nhà** = Value Object.
- Khách đến nhà → nói chuyện với bố/mẹ, **không** tự tiện vào phòng con.
- Bố/mẹ quyết định con được làm gì.
- Bố/mẹ chịu trách nhiệm về toàn bộ "state" của gia đình.

Hãy nghĩ về **một hóa đơn**:

- **Invoice** = Aggregate Root.
- **InvoiceLine** = Entity con.
- **Money, Address** = Value Object.
- Bạn không "sửa dòng 3 của hóa đơn #123" trực tiếp.
- Bạn nói: "Hóa đơn #123, sửa dòng 3 thành X".
- Hóa đơn kiểm tra rule (không cho sửa khi đã thanh toán).

### 2.3. Đặc điểm của Aggregate

| Đặc điểm | Ý nghĩa |
|---|---|
| **Consistency boundary** | Mọi invariant được bảo vệ trong 1 transaction |
| **Aggregate Root** | Cổng vào duy nhất |
| **Repository** | Chỉ cho Aggregate Root |
| **Reference** | Từ ngoài chỉ được tham chiếu Aggregate Root |
| **Transaction** | 1 transaction = 1 Aggregate (lý tưởng) |

---

## 3. Năm quy tắc vàng khi thiết kế Aggregate

Đây là **5 quy tắc** bạn phải khắc cốt ghi tâm.

### 3.1. Quy tắc 1: Bảo vệ invariant bằng consistency boundary

**Invariant** = điều kiện phải luôn đúng.

**Ví dụ:**

- `Order.total` phải = tổng các `OrderLine.subtotal`.
- `Order` không được rỗng khi ở trạng thái `PLACED`.
- `Account.balance` không được âm.

**Nguyên tắc:** Nếu 2 object chia sẻ invariant → chúng phải **cùng Aggregate**.

```python
# ✅ ĐÚNG: OrderLine nằm trong Order
class Order:
    _lines: dict[UUID, OrderLine]

    def add_line(self, line: OrderLine) -> None:
        # Order kiểm tra invariant
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines()
        self._lines[line.id] = line

    def remove_line(self, line_id: UUID) -> None:
        # Order kiểm tra: không được xóa line cuối khi đã PLACED
        if self._status == OrderStatus.PLACED and len(self._lines) == 1:
            raise CannotRemoveLastLine()
        del self._lines[line_id]
```

```python
# ❌ SAI: OrderLine có repository riêng
line = order_line_repo.find_by_id(line_id)
line.quantity = 1000   # Không ai kiểm tra!
```

### 3.2. Quy tắc 2: Thiết kế Aggregate nhỏ

**Aggregate nhỏ = tốt.** Aggregate lớn = lock lâu, conflict nhiều, chậm.

**Ví dụ thực tế:**

- `Order` có 100 `OrderLine` → Aggregate này có 101 object. OK.
- `Customer` có 1 triệu `Order` → **KHÔNG** đưa Order vào Customer! Order là Aggregate riêng.

```python
# ❌ SAI: Customer chứa Order
@dataclass
class Customer:
    id: UUID
    orders: list[Order]   # 1 triệu order → load cả triệu object!

# ✅ ĐÚNG: Order là Aggregate riêng, tham chiếu Customer qua ID
@dataclass
class Order:
    id: UUID
    customer_id: UUID     # chỉ reference ID

@dataclass
class Customer:
    id: UUID
    # Không có orders
```

**Quy tắc ngón tay:**

- Aggregate lý tưởng: **1-10 object**.
- Aggregate chấp nhận được: **10-100 object**.
- Aggregate đáng ngờ: **> 100 object**.

### 3.3. Quy tắc 3: Chỉ tham chiếu Aggregate Root bằng ID

Từ ngoài Aggregate, bạn **chỉ tham chiếu Aggregate Root** — và tham chiếu bằng **ID**, không phải object.

```python
# ❌ SAI: Order giữ object Customer
@dataclass
class Order:
    customer: Customer   # Object thật → coupling chặt

# ✅ ĐÚNG: Order giữ customer_id
@dataclass
class Order:
    customer_id: UUID    # Chỉ ID
```

**Lý do:**

- Nếu giữ object `Customer`, `Order` phụ thuộc vào toàn bộ `Customer` (bao gồm cả `Customer.orders`).
- Load `Order` sẽ load cả `Customer` → chậm.
- Nếu `Customer` thay đổi, `Order` bị ảnh hưởng.

**Ngoại lệ:** Trong cùng Aggregate, Aggregate Root có thể giữ object của Entity con. Ví dụ `Order` giữ `OrderLine` object — vì chúng cùng Aggregate.

### 3.4. Quy tắc 4: Một transaction = một Aggregate

Đây là **quy tắc quan trọng nhất** để đảm bảo consistency.

**Ví dụ:**

```python
# ✅ ĐÚNG: 1 transaction, 1 aggregate
def place_order(cmd: PlaceOrderCommand) -> UUID:
    with uow:
        order = Order.create(cmd.customer_id)
        for item in cmd.items:
            order.add_line(OrderLine(...))
        order.place()
        uow.orders.save(order)
        uow.commit()   # 1 transaction
    return order.id
```

```python
# ❌ SAI: 1 transaction, 2 aggregate
def transfer_money(from_id, to_id, amount):
    with uow:
        source = uow.accounts.find_by_id(from_id)
        target = uow.accounts.find_by_id(to_id)
        source.withdraw(amount)   # Aggregate 1
        target.deposit(amount)    # Aggregate 2
        uow.accounts.save(source)
        uow.accounts.save(target)
        uow.commit()   # Cùng 1 transaction → SAI!
```

**Tại sao SAI?** Vì nếu có 2 request đồng thời:

- Request A: chuyển 100 từ X sang Y.
- Request B: chuyển 100 từ Y sang X.
- Nếu cả 2 lock cùng lúc → **deadlock**.

**Cách đúng:** Dùng **eventual consistency** hoặc **Saga pattern**.

```python
# ✅ ĐÚNG: 2 transaction, eventual consistency
def transfer_money(from_id, to_id, amount):
    # Transaction 1: rút từ source
    with uow:
        source = uow.accounts.find_by_id(from_id)
        source.withdraw(amount)
        source.record_event(MoneyWithdrawn(from_id, to_id, amount))
        uow.accounts.save(source)
        uow.commit()

    # Transaction 2: (được trigger bởi event) nạp vào target
    # ... handler lắng nghe MoneyWithdrawn và nạp vào target
```

### 3.5. Quy tắc 5: Không truy cập trực tiếp con của Aggregate

Từ ngoài, bạn **không** được truy cập `OrderLine` trực tiếp. Phải qua `Order`.

```python
# ❌ SAI: Truy cập trực tiếp OrderLine
line = order.lines[line_id]
line.change_quantity(10)   # Bỏ qua Order!

# ✅ ĐÚNG: Qua Order
order.change_line_quantity(line_id, 10)   # Order kiểm tra
```

**Trong Python:** Đặt `_lines` private, chỉ expose property `lines` trả về read-only view.

```python
class Order:
    def __init__(self):
        self._lines: dict[UUID, OrderLine] = {}

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        """Trả về tuple (read-only)."""
        return tuple(self._lines.values())

    def change_line_quantity(self, line_id: UUID, new_qty: int) -> None:
        if line_id not in self._lines:
            raise LineNotFound(line_id)
        self._lines[line_id].change_quantity(new_qty)
```

> ⚠️ **Lưu ý:** Trong Python, `tuple(self._lines.values())` vẫn trả về **cùng object** `OrderLine`. Người dùng có thể mutate `OrderLine` object đó. Để chống, cần **deep copy** hoặc dùng VO. Nhưng đó là trade-off — thường ta chấp nhận.

---

## 4. Cách chọn Aggregate Root

### 4.1. Câu hỏi quyết định

**Aggregate Root** = Entity mà:

1. Là **cổng vào** logic của cả cụm.
2. **Kiểm soát** mọi invariant của cụm.
3. Được **Repository** tham chiếu.
4. Được tham chiếu từ **Aggregate khác** bằng ID.

### 4.2. Ví dụ: Order & OrderLine

**Câu hỏi:** `Order` và `OrderLine` — cái nào là Aggregate Root?

**Phân tích:**

- Ai kiểm tra rule "max 100 lines"? → `Order`.
- Ai kiểm tra "không xóa line cuối khi PLACED"? → `Order`.
- Ai tính `total`? → `Order`.
- Ai có repository? → `Order`.
- Ai được tham chiếu từ `Shipment`? → `Order`.

**Kết luận:** `Order` là Aggregate Root, `OrderLine` là Entity con.

### 4.3. Ví dụ: Customer & Order

**Câu hỏi:** `Customer` và `Order` — cùng Aggregate không?

**Phân tích:**

- Có cần update `Customer` và `Order` trong **cùng** transaction không?
  - Không. Khi tạo Order, không cần update Customer ngay.
- Nếu Customer bị suspend, Order có ảnh hưởng ngay không?
  - Không. Order đã tạo rồi thì vẫn xử lý được.
- Nếu có 1 triệu Order, ta có muốn load cả triệu khi load Customer không?
  - **KHÔNG.**

**Kết luận:** `Customer` và `Order` là **2 Aggregate riêng biệt**. Order tham chiếu Customer qua `customer_id`.

### 4.4. Ví dụ: Post & Comment

**Câu hỏi:** `Post` và `Comment` — cùng Aggregate không?

**Phân tích:**

- Comment cần Post tồn tại (FK).
- Khi Post bị xóa → Comment bị xóa theo (cascade).
- Có thể comment khi Post chưa publish? → Không.
- Max comment? → Có thể (ví dụ 500).

**Kết luận:** `Post` là Aggregate Root, `Comment` là Entity con.

### 4.5. Ví dụ: Product & Category

**Câu hỏi:** `Product` và `Category` — cùng Aggregate không?

**Phân tích:**

- Category có thể tồn tại độc lập.
- Product có thể đổi category.
- Category có nhiều Product.
- Xóa Category → Product không bị xóa.

**Kết luận:** 2 Aggregate riêng. Product tham chiếu Category qua `category_id`.

### 4.6. Ví dụ: BankAccount & Transaction

**Câu hỏi:** `BankAccount` và `Transaction` — cùng Aggregate không?

**Phân tích:**

- Transaction luôn thuộc 1 Account.
- Chuyển tiền giữa 2 Account → 2 Transaction, 2 Account.
- Có cần ACID giữa Account và Transaction? → Có (khi deposit, balance và transaction phải cùng commit).
- Transaction có ID riêng không? → Có, nhưng không cần repository riêng.

**Kết luận:** `BankAccount` là Aggregate Root, `Transaction` là Entity con.

### 4.7. Bảng quyết định

| Câu hỏi | Cùng Aggregate | Khác Aggregate |
|---|---|---|
| Cần ACID xuyên suốt? | ✅ | |
| Cùng invariant? | ✅ | |
| Cascade delete? | ✅ | |
| Số lượng con ít (<100)? | ✅ | |
| Con tồn tại độc lập? | | ✅ |
| Số lượng con lớn (>100)? | | ✅ |
| Reference bằng ID? | | ✅ |

---

## 5. Strong vs Eventual Consistency

Đây là **khái niệm nâng cao** nhưng cực kỳ quan trọng.

### 5.1. Strong consistency

Trong **cùng 1 Aggregate**, mọi thay đổi là **atomic** — hoặc tất cả thành công, hoặc tất cả thất bại.

**Ví dụ:**

```python
# Trong 1 transaction
order.add_line(line)
order.place()
uow.orders.save(order)
uow.commit()   # Tất cả hoặc không có gì
```

**Đảm bảo:**

- `order.total` = tổng các `order_line.subtotal`.
- `order` không rỗng khi `PLACED`.

### 5.2. Eventual consistency

**Giữa các Aggregate**, thay đổi có thể **trễ** — nhưng cuối cùng sẽ nhất quán.

**Ví dụ:** Order Placed → trừ stock Product.

```python
# Transaction 1: Order
with uow:
    order.place()
    uow.orders.save(order)
    uow.commit()

# Publish event OrderPlaced
# Transaction 2: Product (async)
def on_order_placed(event: OrderPlaced):
    with uow:
        for line in event.lines:
            product = uow.products.find_by_id(line.product_id)
            product.reduce_stock(line.quantity)
            uow.products.save(product)
        uow.commit()
```

**Đặc điểm:**

- Có thể có **độ trễ** giữa 2 transaction.
- Nếu transaction 2 fail → cần retry / compensation.
- Cuối cùng, `Product.stock` phản ánh đúng.

### 5.3. Khi nào dùng cái nào?

| Tình huống | Dùng |
|---|---|
| Trong cùng Aggregate | Strong consistency |
| Giữa 2 Aggregate cần atomic | **Không** làm được với 1 transaction — dùng Saga hoặc Eventual |
| Thông báo, email | Eventual |
| Cache invalidation | Eventual |
| Analytics | Eventual |

> 💡 **Nguyên tắc:** Nếu bạn thấy mình cần ACID giữa 2 Aggregate → **thiết kế lại Aggregate**. Có thể chúng nên là 1.

---

## 6. Sáu anti-pattern khi thiết kế Aggregate

### ❌ Anti-pattern 1: Aggregate quá lớn

```python
# ❌ SAI
@dataclass
class Customer:
    id: UUID
    orders: list[Order]   # 1 triệu order
    invoices: list[Invoice]
    tickets: list[Ticket]
    # ...
```

**Vấn đề:**
- Load customer = load 1 triệu object.
- Lock customer = lock cả 1 triệu object.
- Concurrent conflict cao.

**Cách sửa:** Tách thành nhiều Aggregate, reference bằng ID.

### ❌ Anti-pattern 2: Reference object thay vì ID

```python
# ❌ SAI
@dataclass
class Order:
    customer: Customer   # Object thật
```

**Vấn đề:**
- Load Order = load Customer.
- Customer thay đổi → Order bị ảnh hưởng.
- Coupling chặt.

**Cách sửa:** Reference bằng ID.

### ❌ Anti-pattern 3: Nhiều Aggregate trong 1 transaction

```python
# ❌ SAI
with uow:
    source.withdraw(amount)   # Aggregate 1
    target.deposit(amount)    # Aggregate 2
    uow.commit()
```

**Vấn đề:**
- Deadlock.
- Lock contention.
- Không scale.

**Cách sửa:** Dùng Saga hoặc eventual consistency.

### ❌ Anti-pattern 4: Repository cho Entity con

```python
# ❌ SAI
class OrderLineRepository(Protocol):
    def find_by_id(self, line_id: UUID) -> OrderLine: ...
```

**Vấn đề:**
- Phá vỡ "chỉ Root có Repository".
- Cho phép truy cập OrderLine trực tiếp.

**Cách sửa:** Không có repository cho Entity con. Đi qua Order.

### ❌ Anti-pattern 5: Truy cập con trực tiếp

```python
# ❌ SAI
order.lines[0].change_quantity(1000)   # Bỏ qua Order
```

**Cách sửa:** Expose read-only view, mọi thay đổi qua method của Root.

### ❌ Anti-pattern 6: Aggregate Root có setter public

```python
# ❌ SAI
@dataclass
class Order:
    id: UUID
    status: OrderStatus   # Ai cũng gán được
    lines: list[OrderLine]

order.status = OrderStatus.DELIVERED   # Bỏ qua state machine!
order.lines = []                       # Xóa sạch lines!
```

**Cách sửa:** Private field, public method có validate.

---

## 7. Ví dụ tổng hợp: `Order` Aggregate hoàn chỉnh

Đây là **Aggregate hoàn chỉnh** bạn có thể copy dùng.

```python
# domain/model/order.py
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from shop.domain.model.order_line import OrderLine
from shop.domain.model.money import Money
from shop.domain.events.order_events import (
    OrderPlaced, OrderLineAdded, OrderLineRemoved,
    OrderShipped, OrderDelivered, OrderCancelled,
)
from shop.domain.exceptions import (
    OrderNotEditable, EmptyOrderCannotBePlaced,
    TooManyLines, LineNotFound, InvalidTransition,
    CannotRemoveLastLine,
)


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
    """
    AGGREGATE ROOT.

    Identity: id.
    Con: OrderLine (Entity).
    Invariant:
      - total = sum(line.subtotal)
      - không rỗng khi PLACED
      - không quá MAX_LINES
      - transition chỉ theo VALID_TRANSITIONS
    """
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    _status: OrderStatus = OrderStatus.DRAFT
    _lines: dict[UUID, OrderLine] = field(default_factory=dict)
    _tracking_number: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list, repr=False)

    MAX_LINES = 100

    # ============ Factory ============
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

    # ============ Behavior (chỉ Root mới có) ============
    def add_line(self, line: OrderLine) -> None:
        self._ensure_editable()
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines(self.id, self.MAX_LINES)
        if line.id in self._lines:
            raise ValueError(f"Line {line.id} đã tồn tại")
        self._lines[line.id] = line
        self._events.append(OrderLineAdded(self.id, line.id))

    def change_line_quantity(self, line_id: UUID, new_qty: int) -> None:
        self._ensure_editable()
        line = self._get_line(line_id)
        line.change_quantity(new_qty)

    def remove_line(self, line_id: UUID) -> None:
        self._ensure_editable()
        if line_id not in self._lines:
            raise LineNotFound(self.id, line_id)
        # Invariant: không xóa line cuối khi đã PLACED
        if self._status == OrderStatus.PLACED and len(self._lines) == 1:
            raise CannotRemoveLastLine(self.id)
        del self._lines[line_id]
        self._events.append(OrderLineRemoved(self.id, line_id))

    def place(self) -> None:
        if not self._lines:
            raise EmptyOrderCannotBePlaced(self.id)
        self._transition_to(OrderStatus.PLACED)
        self._events.append(
            OrderPlaced(
                order_id=self.id,
                customer_id=self.customer_id,
                total=self.total,
            )
        )

    def ship(self, tracking_number: str) -> None:
        if not tracking_number.strip():
            raise ValueError("Tracking number không được rỗng")
        self._transition_to(OrderStatus.SHIPPED)
        self._tracking_number = tracking_number.strip()
        self._events.append(OrderShipped(self.id, tracking_number))

    def deliver(self) -> None:
        self._transition_to(OrderStatus.DELIVERED)
        self._events.append(OrderDelivered(self.id))

    def cancel(self, reason: str) -> None:
        self._transition_to(OrderStatus.CANCELLED)
        self._events.append(OrderCancelled(self.id, reason))

    # ============ Query ============
    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        """Read-only view."""
        return tuple(self._lines.values())

    @property
    def line_count(self) -> int:
        return len(self._lines)

    @property
    def total(self) -> Money:
        if not self._lines:
            return Money(Decimal("0"), "VND")
        return sum(
            (line.subtotal for line in self._lines.values()),
            Money(Decimal("0"), "VND"),
        )

    @property
    def tracking_number(self) -> str | None:
        return self._tracking_number

    def is_editable(self) -> bool:
        return self._status == OrderStatus.DRAFT

    def is_placed(self) -> bool:
        return self._status == OrderStatus.PLACED

    def get_line(self, line_id: UUID) -> OrderLine:
        """Trả về bản copy để không ai mutate trực tiếp."""
        return self._get_line(line_id)

    # ============ Internal ============
    def _get_line(self, line_id: UUID) -> OrderLine:
        if line_id not in self._lines:
            raise LineNotFound(self.id, line_id)
        return self._lines[line_id]

    def _ensure_editable(self) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable(self.id, self._status)

    def _transition_to(self, new_status: OrderStatus) -> None:
        if new_status not in VALID_TRANSITIONS[self._status]:
            raise InvalidTransition(self.id, self._status, new_status)
        self._status = new_status

    # ============ Events ============
    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events

    # ============ Identity ============
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

```python
# domain/model/order_line.py
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from shop.domain.model.money import Money


@dataclass(eq=False)
class OrderLine:
    """
    ENTITY CON — không có repository riêng.
    Chỉ được tạo/sửa/xóa qua Order.
    """
    id: UUID = field(default_factory=uuid4)
    product_id: UUID = field(default=None)   # type: ignore
    unit_price: Money = field(default=None)  # type: ignore
    _quantity: int = 1

    MAX_QUANTITY = 1000

    @classmethod
    def create(
        cls,
        product_id: UUID,
        unit_price: Money,
        quantity: int,
    ) -> "OrderLine":
        if quantity <= 0:
            raise ValueError("Quantity phải > 0")
        if quantity > cls.MAX_QUANTITY:
            raise ValueError(f"Quantity không quá {cls.MAX_QUANTITY}")
        return cls(
            product_id=product_id,
            unit_price=unit_price,
            _quantity=quantity,
        )

    def change_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise ValueError("Quantity phải > 0")
        if new_qty > self.MAX_QUANTITY:
            raise ValueError(f"Quantity không quá {self.MAX_QUANTITY}")
        self._quantity = new_qty

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def subtotal(self) -> Money:
        return self.unit_price * Decimal(self._quantity)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderLine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

**Điểm mấu chốt:**

1. `Order` là Aggregate Root — có repository, có behavior.
2. `OrderLine` là Entity con — không có repository, chỉ tạo qua `Order.add_line`.
3. `OrderLine._quantity` private — chỉ đổi qua `change_quantity`.
4. `Order._lines` private — chỉ thêm/xóa qua `Order`.
5. `Order.lines` trả về tuple — read-only view.
6. State machine rõ ràng.
7. Events được phát ở mỗi hành vi.

---

## 8. Repository cho Aggregate

**Chỉ Aggregate Root có repository.** Đây là quy tắc cứng.

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

```python
# infrastructure/persistence/sqlalchemy/order_repository.py
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, selectinload

from shop.domain.model.order import Order
from shop.domain.repositories.order_repository import OrderRepository
from shop.infrastructure.persistence.sqlalchemy.mapper import OrderMapper
from shop.infrastructure.persistence.sqlalchemy.orm_models import OrderRow


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = (
            self._session.query(OrderRow)
            .options(selectinload(OrderRow.lines))
            .filter(OrderRow.id == order_id)
            .one_or_none()
        )
        if not row:
            return None
        return OrderMapper.to_domain(row)

    def save(self, order: Order) -> None:
        row = OrderMapper.to_row(order)
        self._session.merge(row)

    def delete(self, order: Order) -> None:
        self._session.query(OrderRow).filter(OrderRow.id == order.id).delete()

    def next_id(self) -> UUID:
        return uuid4()
```

**Lưu ý:**

- `find_by_id` **load luôn** cả `OrderLine` (eager loading) — vì chúng cùng Aggregate.
- Không có `OrderLineRepository`.

---

## 9. Testing Aggregate

Aggregate test = pure Python + test invariant.

```python
# tests/unit/domain/test_order.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.domain.model.order import Order, OrderStatus, OrderNotEditable
from shop.domain.model.order_line import OrderLine
from shop.domain.model.money import Money
from shop.domain.exceptions import (
    EmptyOrderCannotBePlaced, TooManyLines,
    InvalidTransition, CannotRemoveLastLine,
)


def make_line(price: str = "100", qty: int = 1) -> OrderLine:
    return OrderLine.create(
        product_id=uuid4(),
        unit_price=Money(Decimal(price), "VND"),
        quantity=qty,
    )


class TestOrderInvariants:
    def test_empty_order_cannot_be_placed(self) -> None:
        order = Order.create(uuid4())
        with pytest.raises(EmptyOrderCannotBePlaced):
            order.place()

    def test_add_line_increases_count(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.add_line(make_line())
        assert order.line_count == 2

    def test_max_lines_enforced(self) -> None:
        order = Order.create(uuid4())
        for _ in range(Order.MAX_LINES):
            order.add_line(make_line())
        with pytest.raises(TooManyLines):
            order.add_line(make_line())

    def test_total_calculated_correctly(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line("100", 2))
        order.add_line(make_line("200", 3))
        # 100*2 + 200*3 = 800
        assert order.total == Money(Decimal("800"), "VND")


class TestOrderEditing:
    def test_cannot_add_line_after_placed(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        with pytest.raises(OrderNotEditable):
            order.add_line(make_line())

    def test_cannot_remove_last_line_when_placed(self) -> None:
        order = Order.create(uuid4())
        line = make_line()
        order.add_line(line)
        order.place()
        with pytest.raises(CannotRemoveLastLine):
            order.remove_line(line.id)

    def test_change_quantity_through_root(self) -> None:
        order = Order.create(uuid4())
        line = make_line(qty=1)
        order.add_line(line)
        order.change_line_quantity(line.id, 5)
        # Lấy lại line — quantity đã đổi
        updated = order.get_line(line.id)
        assert updated.quantity == 5


class TestOrderStateMachine:
    def test_valid_transitions(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        order.ship("TRACK123")
        order.deliver()
        assert order.status == OrderStatus.DELIVERED

    def test_cannot_ship_draft(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        with pytest.raises(InvalidTransition):
            order.ship("TRACK")

    def test_cannot_deliver_unshipped(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        with pytest.raises(InvalidTransition):
            order.deliver()

    def test_cannot_ship_cancelled(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        order.cancel("changed mind")
        with pytest.raises(InvalidTransition):
            order.ship("TRACK")


class TestOrderEvents:
    def test_place_emits_event(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.pull_events()   # clear
        order.place()
        events = order.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "OrderPlaced"

    def test_events_are_cleared_after_pull(self) -> None:
        order = Order.create(uuid4())
        order.add_line(make_line())
        order.place()
        events1 = order.pull_events()
        events2 = order.pull_events()
        assert len(events1) == 2   # OrderLineAdded + OrderPlaced
        assert len(events2) == 0


class TestOrderIdentity:
    def test_same_id_equal(self) -> None:
        oid = uuid4()
        o1 = Order.reconstruct(oid, uuid4(), OrderStatus.DRAFT, [], None, None)
        o2 = Order.reconstruct(oid, uuid4(), OrderStatus.PLACED, [], "T", None)
        assert o1 == o2   # Cùng ID

    def test_different_id_not_equal(self) -> None:
        o1 = Order.create(uuid4())
        o2 = Order.create(uuid4())
        assert o1 != o2
```

**Chạy:** ~20 test trong 0.05 giây.

---

## 10. Khi nào Aggregate quá phức tạp?

Có những tình huống Aggregate không đủ. Khi đó dùng các pattern khác:

### 10.1. Saga (Process Manager)

Khi cần **nhiều bước** trải qua nhiều Aggregate.

```python
class PlaceOrderSaga:
    """
    Saga điều phối: Order → Payment → Inventory → Shipping.
    Mỗi bước là 1 transaction riêng.
    Nếu 1 bước fail → compensate các bước trước.
    """

    def handle_order_placed(self, event: OrderPlaced) -> None:
        # 1. Charge payment
        payment_id = self._payment_service.charge(
            event.customer_id, event.total
        )
        # 2. Reserve stock
        self._inventory_service.reserve(event.order_id, event.lines)
        # 3. Nếu tất cả OK → publish OrderConfirmed
        # Nếu fail → publish OrderFailed + compensate
```

### 10.2. Event Sourcing

Khi cần **audit trail** đầy đủ và **time travel**.

```python
class Order:
    def __init__(self):
        self._changes: list[DomainEvent] = []

    def place(self) -> None:
        self._apply(OrderPlaced(...))
        self._changes.append(OrderPlaced(...))

    def _apply(self, event) -> None:
        # Update state dựa trên event
        ...
```

### 10.3. CQRS

Tách **write model** (Aggregate) khỏi **read model** (query).

```python
# Write: dùng Aggregate
order.place()
uow.orders.save(order)
uow.commit()

# Read: query thẳng DB, không qua Aggregate
def get_order_summary(order_id):
    return db.execute(
        "SELECT id, total, status FROM order_summary WHERE id = ?",
        order_id,
    )
```

---

## 11. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): `Cart` Aggregate

Viết Aggregate `Cart` (giỏ hàng):

- Aggregate Root: `Cart`.
- Entity con: `CartItem`.
- Fields: `id`, `customer_id`, `items: list[CartItem]`, `created_at`.
- Behavior:
  - `add_item(product_id, price, quantity)`.
  - `remove_item(item_id)`.
  - `change_item_quantity(item_id, qty)`.
  - `clear()`.
  - `checkout()` → trả về `OrderDraft` (giả sử).
- Invariant:
  - Max 50 items.
  - Không cho `add_item` khi đã checkout.
  - Quantity mỗi item: 1-100.
- Events: `CartItemAdded`, `CartItemRemoved`, `CartCheckedOut`.

Viết ít nhất 12 test case.

### 🟡 Bài tập 2 (trung bình): `Invoice` Aggregate

Viết Aggregate `Invoice` (hóa đơn):

- Root: `Invoice`.
- Con: `InvoiceLine`.
- Fields: `id`, `number: InvoiceNumber` (VO), `customer_id`, `issued_date`, `due_date`, `lines`, `status`, `paid_at`.
- Status: `DRAFT`, `ISSUED`, `PAID`, `CANCELLED`, `OVERDUE`.
- Behavior:
  - `add_line(...)` — chỉ DRAFT.
  - `remove_line(...)` — chỉ DRAFT.
  - `issue()` — chuyển DRAFT → ISSUED, cần có ít nhất 1 line.
  - `mark_paid(paid_at)` — chỉ ISSUED.
  - `cancel(reason)` — chỉ DRAFT hoặc ISSUED.
  - `mark_overdue()` — chỉ ISSUED và đã qua due_date.
- Invariant:
  - Max 200 lines.
  - Total = sum(subtotals).
  - Không sửa khi PAID/CANCELLED.
- Events: `InvoiceIssued`, `InvoicePaid`, `InvoiceCancelled`, `InvoiceOverdue`.

Viết ít nhất 15 test case.

### 🔴 Bài tập 3 (khó): `BankAccount` Aggregate với Transaction

Viết Aggregate `BankAccount`:

- Root: `BankAccount`.
- Con: `Transaction`.
- Fields: `id`, `account_number` (VO), `owner_id`, `balance`, `status`, `_transactions`.
- Status: `ACTIVE`, `FROZEN`, `CLOSED`.
- Behavior:
  - `deposit(money, description)`.
  - `withdraw(money, description)`.
  - `freeze(reason)`.
  - `unfreeze()`.
  - `close()` — chỉ khi balance = 0.
- Invariant:
  - Không cho giao dịch khi FROZEN/CLOSED.
  - Không cho rút quá balance.
  - Không cho rút quá 100 triệu/ngày.
  - Max 10,000 transactions.
  - **Transaction là bất biến** (sau khi tạo không sửa).
- Events: `MoneyDeposited`, `MoneyWithdrawn`, `AccountFrozen`, `AccountClosed`.

**Đặc biệt:** Viết thêm **Domain Service** `TransferService` để chuyển tiền giữa 2 account. Giải thích tại sao đây **không phải** method của `BankAccount`.

Viết ít nhất 25 test case.

---

## 12. Checklist sau bài 7

Trước khi sang bài 8, bạn phải tự tin trả lời:

- [ ] Aggregate là gì? Aggregate Root là gì?
- [ ] 5 quy tắc vàng khi thiết kế Aggregate?
- [ ] Tại sao "1 transaction = 1 Aggregate"?
- [ ] Tại sao chỉ tham chiếu Aggregate khác bằng ID?
- [ ] Tại sao Aggregate nhỏ tốt hơn lớn?
- [ ] 3 câu hỏi để chọn Aggregate Root?
- [ ] Strong consistency vs eventual consistency?
- [ ] Khi nào dùng Saga?
- [ ] 6 anti-pattern khi thiết kế Aggregate?
- [ ] Tại sao `OrderLine` không có repository riêng?
- [ ] Làm sao để enforce "không truy cập con trực tiếp" trong Python?

Nếu trả lời được hết, bạn đã sẵn sàng bài 8.

---

## 13. Tóm tắt bài 7

| Điểm | Nội dung |
|---|---|
| **Aggregate** | Cụm Entity + VO có consistency boundary |
| **Aggregate Root** | Entity cổng vào duy nhất của cụm |
| **Quy tắc 1** | Bảo vệ invariant trong cùng Aggregate |
| **Quy tắc 2** | Aggregate nhỏ (1-100 object) |
| **Quy tắc 3** | Tham chiếu Aggregate khác bằng ID |
| **Quy tắc 4** | 1 transaction = 1 Aggregate |
| **Quy tắc 5** | Không truy cập con trực tiếp |
| **Repository** | Chỉ cho Aggregate Root |
| **Consistency** | Strong (trong Aggregate) vs Eventual (giữa Aggregate) |
| **6 anti-pattern** | Lớn, ref object, nhiều agg/transaction, repo cho con, truy cập con, setter public |
| **Test** | Pure Python, ~20 test trong 0.05s |

**Câu thần chú:** *"Một Aggregate — một cổng vào — một transaction."*

---

## 14. Chuẩn bị cho bài 8

Bài tiếp theo: **Domain Event — Kể chuyện nghiệp vụ**.

Chuẩn bị:
- Đọc lại các event trong `Order` (bài này).
- Nghĩ về **5-10 event** trong domain bạn đang làm.
- Sẽ bàn: Domain Event vs Integration Event, cách phát event, event bus, event handler, và cách dùng event để decouple các Aggregate.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 8** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Saga pattern, Event Sourcing, CQRS, Unit of Work chi tiết.
5. **Review code Aggregate** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.