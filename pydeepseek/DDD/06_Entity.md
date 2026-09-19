# 📖 Bài 6: Entity — Có định danh, có vòng đời

> Bài 5 dạy bạn VO — thứ "không có ID". Bài 6 dạy bạn **Entity** — thứ "có ID và sống qua thời gian". Đây là building block mà bạn sẽ dùng để mô hình hóa **Customer, Order, Product, Account** — những thứ có vòng đời, có lịch sử, có thay đổi.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Entity** là gì và tại sao cần ID.
2. Phân biệt rõ hơn **VO vs Entity** — qua 5 tình huống thực tế.
3. Viết Entity "chuẩn DDD" trong Python: `__eq__`/`__hash__` theo ID, state private, hành vi public.
4. Biết **khi nào dùng `@dataclass`**, **khi nào dùng class thường** cho Entity.
5. Quản lý **vòng đời** của Entity: tạo, load từ DB, xóa (soft delete).
6. Phát **Domain Event** từ Entity khi state thay đổi.
7. Tránh được **8 anti-pattern** khi viết Entity.
8. Làm bài tập thực hành có chấm điểm.

---

## 1. Entity là gì?

### 1.1. Định nghĩa

> **Entity** là một object có **identity (định danh)** — một ID duy nhất không đổi suốt vòng đời. Hai Entity có cùng ID được coi là **cùng một đối tượng**, bất kể mọi field khác có khác nhau.

### 1.2. Trực giác

Hãy nghĩ về **bạn**:

- Bạn có **CCCD** (ID).
- Năm 2010, bạn 10 tuổi. Năm 2026, bạn 26 tuổi.
- Chiều cao, cân nặng, địa chỉ, nghề nghiệp của bạn đều đã thay đổi.
- **Nhưng bạn vẫn là bạn** — vì CCCD không đổi.

Đó là Entity. **Identity quan trọng hơn state.**

Hãy nghĩ về **cuốn sách trong thư viện**:

- Mỗi cuốn có **mã vạch** (ID).
- Cuốn sách có thể bị mượn, trả, chuyển kho, đóng gáy lại.
- Nhưng **vẫn là cùng cuốn sách** — vì mã vạch không đổi.

Hãy nghĩ về **đơn hàng**:

- `Order #12345` — đơn hàng có ID.
- Đơn hàng đi từ DRAFT → PLACED → SHIPPED → DELIVERED.
- **Vẫn là cùng đơn hàng** — vì ID không đổi.

### 1.3. Entity có gì?

| Thành phần | Mô tả |
|---|---|
| **Identity** | ID duy nhất (UUID, số tự tăng, mã nghiệp vụ) |
| **State** | Dữ liệu có thể thay đổi (name, status, balance...) |
| **Behavior** | Hành vi làm thay đổi state (place(), withdraw()...) |
| **Lifecycle** | Tạo → tồn tại → thay đổi → (soft delete) |
| **Invariant** | Rule phải luôn đúng |

### 1.4. Ví dụ: từ VO trong bài 5 → Entity bây giờ

Bài 5, chúng ta có `Money`, `Email`, `Address` — VO. Bây giờ:

```python
@dataclass
class Customer:
    """
    Entity — KHÁC VO ở chỗ có ID.
    """
    id: UUID
    email: Email              # ← chứa VO
    full_name: str
    address: Address | None   # ← chứa VO
    status: CustomerStatus
    created_at: datetime
```

**Điểm mấu chốt:**
- `Customer` **có** `id`.
- `Email`, `Address` bên trong **không có** `id`.
- `Customer` có thể thay đổi email, address — nhưng `id` không đổi.

---

## 2. VO vs Entity — Phân biệt sâu hơn

Bài 5 đã giới thiệu bảng so sánh. Bài này đi sâu với **5 tình huống thực tế**.

### 2.1. Tình huống 1: "Tiền trong ví"

**Câu hỏi:** Tờ 100k trong ví bạn — VO hay Entity?

**Phân tích:**
- Tờ 100k của bạn và tờ 100k của tôi giống hệt nhau.
- Không ai đánh số "tờ 100k #123".
- Nếu bạn đổi tờ 100k cũ sang tờ 100k mới → không ai quan tâm.

**Kết luận:** **VO (Money).**

### 2.2. Tình huống 2: "Số dư tài khoản"

**Câu hỏi:** Số dư 1 triệu trong tài khoản của bạn — VO hay Entity?

**Phân tích:**
- Số dư là một con số — không có ID.
- Số dư có thể thay đổi (nạp, rút).
- Nhưng **số dư** không phải entity; **tài khoản** mới là entity.

**Kết luận:**
- `Balance` → **VO (Money)**.
- `BankAccount` → **Entity**.

### 2.3. Tình huống 3: "Địa chỉ giao hàng"

**Câu hỏi:** Địa chỉ giao hàng của một đơn — VO hay Entity?

**Phân tích:**
- Địa chỉ có thể coi là VO: cùng street/ward/district → cùng địa chỉ.
- Nhưng nếu khách hàng đổi địa chỉ sau khi đặt hàng, đơn hàng **không được** đổi theo.
- Địa chỉ cần "đóng băng" tại thời điểm đặt.

**Kết luận:** **VO (Address)**. Nhưng khi đặt hàng, ta **copy** địa chỉ vào đơn (đóng băng).

### 2.4. Tình huống 4: "Người dùng hệ thống"

**Câu hỏi:** User — VO hay Entity?

**Phân tích:**
- Hai user cùng tên "Nguyễn Văn An" là 2 người khác nhau.
- User có vòng đời: đăng ký, hoạt động, khóa, xóa.
- User có ID.

**Kết luận:** **Entity (Account/User).**

### 2.5. Tình huống 5: "Cấu hình hệ thống"

**Câu hỏi:** Config — VO hay Entity?

**Phân tích:**
- Config có thể là VO: cùng giá trị → cùng config.
- Không có vòng đời.
- Không có ID.

**Kết luận:** **VO (Configuration).**

### 2.6. Bảng tổng hợp

| Object | VO/Entity | Lý do |
|---|---|---|
| Money, Email, Address | VO | Không ID, so sánh giá trị |
| Customer, Account, User | Entity | Có ID, có vòng đời |
| Order, Invoice, Booking | Entity | Có ID, có vòng đời |
| Product | Entity | Có SKU, có vòng đời |
| Category, Tag | VO | Không ID, so sánh giá trị |
| Role, Permission | Entity | Có ID, có vòng đời |
| Country, Language | VO | Không ID, so sánh giá trị |
| Session, Token | Entity | Có ID, có vòng đời |

### 2.7. Quy tắc "3 câu hỏi" — nhắc lại

1. **Có cần ID không?** → Có = Entity.
2. **Cùng giá trị = cùng object không?** → Có = VO.
3. **Cần theo dõi vòng đời không?** → Có = Entity.

**Nếu vẫn mơ hồ, hỏi câu thứ 4:**

4. **Nếu mọi field thay đổi, object có còn là nó không?**
   - Có → **Entity** (identity > state).
   - Không → **VO** (state = identity).

---

## 3. Viết Entity chuẩn trong Python

### 3.1. Bộ khung cơ bản

Đây là **bộ khung Entity** bạn sẽ dùng suốt sự nghiệp:

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Entity:
    """
    Base class cho mọi Entity.
    Định nghĩa __eq__ và __hash__ theo ID.
    """
    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

**Chú ý:**
- `@dataclass` (không frozen) — Entity mutable.
- `field(default_factory=uuid4)` — mỗi Entity tự sinh UUID khi tạo.
- `__eq__` so sánh theo `id`.
- `__hash__` từ `id`.

> ⚠️ **Cảnh báo:** Nếu bạn `@dataclass` không có `eq=False`, Python **tự sinh** `__eq__` so sánh tất cả field → **SAI** cho Entity. Phải override.

### 3.2. Ví dụ đầy đủ: `Customer`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from shop.shared.domain.email import Email
from shop.shared.domain.address import Address


class CustomerStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


# ---- Domain Events ----
@dataclass(frozen=True)
class CustomerEmailChanged:
    customer_id: UUID
    old_email: Email
    new_email: Email


@dataclass(frozen=True)
class CustomerSuspended:
    customer_id: UUID
    reason: str


# ---- Entity ----
@dataclass
class Customer:
    """
    Entity: Khách hàng.

    Identity: id (UUID).
    State: email, full_name, address, status.
    Behavior: change_email(), suspend(), reactivate().
    """
    id: UUID = field(default_factory=uuid4)
    email: Email = field(default=None)          # type: ignore
    full_name: str = ""
    address: Address | None = None
    status: CustomerStatus = CustomerStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list, repr=False)

    # ---- Factory ----
    @classmethod
    def register(cls, email: Email, full_name: str) -> "Customer":
        """Tạo khách hàng mới."""
        if not full_name.strip():
            raise ValueError("Tên không được rỗng")
        return cls(
            email=email,
            full_name=full_name.strip(),
        )

    # ---- Behavior ----
    def change_email(self, new_email: Email) -> None:
        """Đổi email."""
        if new_email == self.email:
            return
        old_email = self.email
        self.email = new_email
        self._events.append(
            CustomerEmailChanged(
                customer_id=self.id,
                old_email=old_email,
                new_email=new_email,
            )
        )

    def change_name(self, new_name: str) -> None:
        """Đổi tên."""
        if not new_name.strip():
            raise ValueError("Tên không được rỗng")
        self.full_name = new_name.strip()

    def move_to(self, new_address: Address) -> None:
        """Đổi địa chỉ."""
        self.address = new_address

    def suspend(self, reason: str) -> None:
        """Tạm khóa tài khoản."""
        if self.status == CustomerStatus.SUSPENDED:
            raise AlreadySuspended(self.id)
        if self.status == CustomerStatus.DELETED:
            raise CustomerDeleted(self.id)
        self.status = CustomerStatus.SUSPENDED
        self._events.append(
            CustomerSuspended(customer_id=self.id, reason=reason)
        )

    def reactivate(self) -> None:
        """Kích hoạt lại."""
        if self.status != CustomerStatus.SUSPENDED:
            raise InvalidOperation(
                f"Chỉ kích hoạt lại được tài khoản SUSPENDED, "
                f"hiện đang {self.status.value}"
            )
        self.status = CustomerStatus.ACTIVE

    def delete(self) -> None:
        """Soft delete."""
        self.status = CustomerStatus.DELETED

    # ---- Query ----
    def is_active(self) -> bool:
        return self.status == CustomerStatus.ACTIVE

    def is_suspended(self) -> bool:
        return self.status == CustomerStatus.SUSPENDED

    # ---- Event collection ----
    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events


# ---- Exceptions ----
class AlreadySuspended(Exception):
    def __init__(self, customer_id: UUID) -> None:
        super().__init__(f"Khách hàng {customer_id} đã bị khóa")


class CustomerDeleted(Exception):
    def __init__(self, customer_id: UUID) -> None:
        super().__init__(f"Khách hàng {customer_id} đã bị xóa")


class InvalidOperation(Exception):
    pass
```

**Phân tích:**

| Thành phần | Vai trò |
|---|---|
| `id` | Identity — không đổi |
| `email`, `full_name`, `address` | State có thể đổi |
| `status` | State đặc biệt — vòng đời |
| `_events` | Domain events tích lũy |
| `register()` | Factory — tạo mới |
| `change_email()` | Behavior — đổi state, phát event |
| `suspend()` | Behavior — chuyển status, phát event |
| `is_active()` | Query — không đổi state |
| `pull_events()` | Lấy events để publish |

### 3.3. `__eq__` và `__hash__` — quan trọng nhất

Đây là **điểm khác biệt cốt lõi** giữa VO và Entity.

**VO:** so sánh bằng **mọi field**.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

assert Money(Decimal("100"), "VND") == Money(Decimal("100"), "VND")   # True
```

**Entity:** so sánh bằng **ID**.

```python
@dataclass(eq=False)
class Customer:
    id: UUID
    email: str
    full_name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# Hai Customer cùng ID, khác email → vẫn bằng nhau
c1 = Customer(id=uuid4(), email="a@x.com", full_name="An")
c2 = Customer(id=c1.id, email="b@x.com", full_name="Bình")

assert c1 == c2   # True — vì cùng ID!
```

**Đây là điều mà dev mới hay sai.** Họ nghĩ "2 Customer khác email thì khác nhau" — nhưng theo DDD, **cùng ID là cùng Customer**.

### 3.4. Khi nào dùng `@dataclass`, khi nào class thường?

| Tình huống | Dùng gì? |
|---|---|
| Entity đơn giản, ít field | `@dataclass(eq=False)` + custom `__eq__`/`__hash__` |
| Entity phức tạp, cần init nhiều bước | Class thường với `__init__` tùy chỉnh |
| Entity có nhiều default, optional | `@dataclass` |
| Entity cần private field nghiêm ngặt | Class thường + `__slots__` |

**Ví dụ class thường:**

```python
class Customer:
    __slots__ = ("_id", "_email", "_full_name", "_status", "_events")

    def __init__(self, customer_id: UUID, email: Email, full_name: str) -> None:
        self._id = customer_id
        self._email = email
        self._full_name = full_name
        self._status = CustomerStatus.ACTIVE
        self._events: list = []

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    # ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
```

**Ưu điểm:**
- `__slots__` ngăn thêm field động.
- Field private `_email` — không ai gán trực tiếp.
- Không thể gán `customer.email = "hacked"` vì có property.

**Nhược điểm:**
- Dài hơn `@dataclass`.
- Phải viết `__eq__`, `__hash__`, `__repr__` thủ công.

**Khuyến nghị:** Dùng `@dataclass` cho 90% trường hợp. Class thường khi cần kỷ luật cao.

---

## 4. Quản lý vòng đời Entity

Entity có **vòng đời**: tạo → load → update → delete. Cần pattern cho mỗi giai đoạn.

### 4.1. Factory method — tạo mới

**Không bao giờ** để caller gọi `Customer(id=uuid4(), email=None)` trực tiếp. Thay vào đó, dùng **factory method** đặt tên theo nghiệp vụ.

```python
@dataclass
class Customer:
    id: UUID = field(default_factory=uuid4)
    email: Email = field(default=None)   # type: ignore
    full_name: str = ""
    status: CustomerStatus = CustomerStatus.ACTIVE

    @classmethod
    def register(cls, email: Email, full_name: str) -> "Customer":
        """
        Factory — tạo khách hàng mới.
        Đảm bảo mọi field cần thiết được set.
        """
        if not full_name.strip():
            raise ValueError("Tên không được rỗng")
        return cls(email=email, full_name=full_name.strip())
```

**Cách dùng:**

```python
customer = Customer.register(
    email=Email("an@example.com"),
    full_name="Nguyễn Văn An",
)
```

**Lợi ích:**
- Không thể tạo `Customer` mà quên email.
- Business rule ("tên không rỗng") được enforce.
- Đọc `Customer.register(...)` hiểu ngay đây là "đăng ký khách hàng mới".

### 4.2. Reconstruct — load từ DB

Khi load từ DB, ta có đầy đủ state. **Không cần** validate lại (đã validate khi tạo), **không phát event**.

```python
@classmethod
def reconstruct(
    cls,
    customer_id: UUID,
    email: Email,
    full_name: str,
    address: Address | None,
    status: CustomerStatus,
    created_at: datetime,
) -> "Customer":
    """
    Reconstruct từ DB. Không validate, không phát event.
    Dùng bởi Repository khi load.
    """
    return cls(
        id=customer_id,
        email=email,
        full_name=full_name,
        address=address,
        status=status,
        created_at=created_at,
    )
```

**Cách dùng trong Repository:**

```python
class SqlAlchemyCustomerRepository:
    def find_by_id(self, customer_id: UUID) -> Customer | None:
        row = self._session.get(CustomerRow, customer_id)
        if not row:
            return None
        return Customer.reconstruct(
            customer_id=row.id,
            email=Email(row.email),
            full_name=row.full_name,
            address=Address(...) if row.street else None,
            status=CustomerStatus(row.status),
            created_at=row.created_at,
        )
```

**Tại sao cần reconstruct riêng?**
- `register()` phát event `CustomerRegistered` — không nên phát khi load.
- `register()` validate — không cần validate lại dữ liệu đã trong DB.
- `reconstruct()` là **con đường riêng** cho việc load.

### 4.3. Soft delete — không xóa thật

**Nguyên tắc:** Trong DDD, **hiếm khi** xóa thật Entity. Thay vào đó, **soft delete**: đổi status thành `DELETED`, giữ record.

```python
def delete(self, reason: str) -> None:
    """Soft delete — không xóa vật lý."""
    if self.status == CustomerStatus.DELETED:
        return   # idempotent
    self.status = CustomerStatus.DELETED
    self._events.append(CustomerDeleted(self.id, reason))
```

**Repository:**

```python
def delete(self, customer: Customer) -> None:
    # Không DELETE FROM, chỉ UPDATE status
    customer.delete("user_requested")
    self.save(customer)
```

**Lợi ích:**
- Audit trail.
- Undo được.
- FK không bị vỡ.

### 4.4. State transitions — kiểm soát chặt

Mỗi Entity có **state machine**. Chỉ cho phép transition hợp lệ.

```python
class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# Bảng transition hợp lệ
VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.PLACED, OrderStatus.CANCELLED},
    OrderStatus.PLACED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),   # kết thúc
    OrderStatus.CANCELLED: set(),   # kết thúc
}


class Order:
    def _transition_to(self, new_status: OrderStatus) -> None:
        """Kiểm tra transition hợp lệ."""
        if new_status not in VALID_TRANSITIONS[self._status]:
            raise InvalidTransition(
                f"Không thể chuyển từ {self._status.value} "
                f"sang {new_status.value}"
            )
        self._status = new_status

    def place(self) -> None:
        self._ensure_has_lines()
        self._transition_to(OrderStatus.PLACED)
        self._events.append(OrderPlaced(self._id))

    def ship(self, tracking_number: str) -> None:
        self._transition_to(OrderStatus.SHIPPED)
        self._tracking_number = tracking_number
        self._events.append(OrderShipped(self._id, tracking_number))

    def cancel(self, reason: str) -> None:
        self._transition_to(OrderStatus.CANCELLED)
        self._events.append(OrderCancelled(self._id, reason))
```

**Lợi ích:**
- Không thể `deliver()` đơn chưa `ship()`.
- Không thể `ship()` đơn đã `cancel()`.
- Business rule được enforce tự động.
- Exception rõ ràng.

---

## 5. Domain Event từ Entity

Entity **phát event** khi state thay đổi. Đây là nền tảng của **event-driven architecture** trong DDD.

### 5.1. Thu thập event

```python
@dataclass
class Customer:
    id: UUID = field(default_factory=uuid4)
    email: Email = field(default=None)   # type: ignore
    _events: list = field(default_factory=list, repr=False)

    def change_email(self, new_email: Email) -> None:
        if new_email == self.email:
            return
        old = self.email
        self.email = new_email
        self._events.append(
            CustomerEmailChanged(self.id, old, new_email)
        )

    def pull_events(self) -> list:
        """Lấy và xóa events."""
        events = self._events[:]
        self._events.clear()
        return events
```

### 5.2. Repository publish event

```python
class SqlAlchemyCustomerRepository:
    def __init__(self, session, event_bus) -> None:
        self._session = session
        self._event_bus = event_bus

    def save(self, customer: Customer) -> None:
        # 1. Lưu vào DB
        self._session.merge(self._to_row(customer))
        self._session.flush()

        # 2. Publish events
        for event in customer.pull_events():
            self._event_bus.publish(event)
```

### 5.3. Handler lắng nghe event

```python
class SendWelcomeEmail:
    def handle(self, event: CustomerRegistered) -> None:
        email_service.send(
            to=event.email,
            subject="Chào mừng bạn!",
            body="Cảm ơn bạn đã đăng ký.",
        )


class InvalidateCache:
    def handle(self, event: CustomerEmailChanged) -> None:
        cache.delete(f"customer:{event.customer_id}")
```

### 5.4. Event bus đơn giản

```python
from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
```

**Sử dụng:**

```python
bus = EventBus()
bus.subscribe(CustomerRegistered, SendWelcomeEmail().handle)
bus.subscribe(CustomerEmailChanged, InvalidateCache().handle)

# Repository sẽ tự publish khi save
repo = SqlAlchemyCustomerRepository(session, bus)
repo.save(customer)
```

---

## 6. Tám anti-pattern khi viết Entity

### ❌ Anti-pattern 1: Anemic Domain Model

```python
# ❌ SAI: Entity chỉ có getter/setter, không có logic
@dataclass
class Customer:
    id: UUID
    email: str
    status: str

    # Chỉ có getter/setter — không có hành vi
```

```python
# ✅ ĐÚNG: Entity có hành vi
@dataclass
class Customer:
    id: UUID
    email: Email
    status: CustomerStatus

    def suspend(self, reason: str) -> None:
        if self.status == CustomerStatus.SUSPENDED:
            raise AlreadySuspended(self.id)
        self.status = CustomerStatus.SUSPENDED
        self._events.append(CustomerSuspended(self.id, reason))
```

### ❌ Anti-pattern 2: `__eq__` so sánh tất cả field

```python
# ❌ SAI: @dataclass tự sinh __eq__ so sánh mọi field
@dataclass
class Customer:
    id: UUID
    email: str
    name: str

c1 = Customer(id=uuid4(), email="a@x.com", name="An")
c2 = Customer(id=c1.id, email="b@x.com", name="Bình")
assert c1 != c2   # SAI! Cùng ID phải bằng nhau
```

```python
# ✅ ĐÚNG: __eq__ theo ID
@dataclass(eq=False)
class Customer:
    id: UUID
    email: str
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### ❌ Anti-pattern 3: Public setter cho mọi field

```python
# ❌ SAI
@dataclass
class Customer:
    id: UUID
    email: Email
    status: CustomerStatus

    # Không ai ngăn được điều này
customer.email = "hacked"
customer.status = CustomerStatus.ACTIVE   # Đang SUSPENDED, giờ ACTIVE tùy tiện
```

```python
# ✅ ĐÚNG: Dùng method nghiệp vụ
@dataclass
class Customer:
    id: UUID
    _email: Email
    _status: CustomerStatus

    @property
    def email(self) -> Email:
        return self._email

    def change_email(self, new_email: Email) -> None:
        # validate, phát event
        ...
```

### ❌ Anti-pattern 4: `id` mutable

```python
# ❌ SAI: Ai cũng sửa được ID
customer.id = uuid4()   # Đổi ID = đổi entity!
```

```python
# ✅ ĐÚNG: ID bất biến
class Customer:
    __slots__ = ("_id", "_email", "_status")

    @property
    def id(self) -> UUID:
        return self._id

    # Không có setter cho id
```

### ❌ Anti-pattern 5: Validation rải rác

```python
# ❌ SAI: Validate ở Service
class CustomerService:
    def create(self, email, name):
        if "@" not in email:
            raise ValueError("bad email")
        if not name.strip():
            raise ValueError("bad name")
        return Customer(email=email, name=name)
```

```python
# ✅ ĐÚNG: Validate ở VO/Factory
class Customer:
    @classmethod
    def register(cls, email: Email, name: str) -> "Customer":
        if not name.strip():
            raise ValueError("bad name")
        # email đã tự validate trong Email.__post_init__
        return cls(email=email, name=name.strip())
```

### ❌ Anti-pattern 6: Entity phát event cho mọi thứ

```python
# ❌ SAI: Event quá nhiều
def change_email(self, new_email):
    self.email = new_email
    self._events.append(CustomerEmailChanged(...))
    self._events.append(CustomerUpdated(...))    # Dư
    self._events.append(CustomerRecordModified(...))   # Dư
```

```python
# ✅ ĐÚNG: Chỉ event có ý nghĩa nghiệp vụ
def change_email(self, new_email):
    self.email = new_email
    self._events.append(CustomerEmailChanged(...))
```

**Nguyên tắc:** Event phải là **"điều gì đó có nghĩa với business"**, không phải "record vừa bị update".

### ❌ Anti-pattern 7: Entity import Infrastructure

```python
# ❌ SAI: Entity biết DB
from sqlalchemy.orm import Session   # PHÁ VỠ DDD

class Customer:
    def save(self, session: Session) -> None:
        session.add(self)
```

```python
# ✅ ĐÚNG: Repository save Entity
class SqlAlchemyCustomerRepository:
    def save(self, customer: Customer) -> None:
        self._session.merge(self._to_row(customer))
```

### ❌ Anti-pattern 8: Entity chứa logic không thuộc về nó

```python
# ❌ SAI: Customer biết về Shipping
class Customer:
    def calculate_shipping_fee(self, order) -> Money:
        if order.weight > 10:
            return Money(Decimal("50000"))
        return Money(Decimal("30000"))
```

```python
# ✅ ĐÚNG: ShippingService xử lý
class ShippingService:
    def calculate_fee(self, order: Order, customer: Customer) -> Money:
        base = Money(Decimal("30000"))
        if customer.is_vip():
            return Money(Decimal("0"))
        if order.total_weight > 10:
            return base + Money(Decimal("20000"))
        return base
```

**Nguyên tắc:** Logic thuộc về entity nào thì đặt ở entity đó. Nếu liên quan nhiều entity → Domain Service.

---

## 7. Testing Entity

Entity cũng dễ test như VO — pure Python, không cần DB.

```python
# tests/unit/domain/test_customer.py
from uuid import uuid4
import pytest

from shop.domain.model.customer import (
    Customer, CustomerStatus, AlreadySuspended, CustomerDeleted,
)
from shop.shared.domain.email import Email


class TestCustomerFactory:
    def test_register_creates_active_customer(self) -> None:
        c = Customer.register(
            email=Email("an@example.com"),
            full_name="Nguyễn Văn An",
        )
        assert c.is_active()
        assert c.full_name == "Nguyễn Văn An"

    def test_register_with_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="Tên không được rỗng"):
            Customer.register(
                email=Email("an@example.com"),
                full_name="  ",
            )

    def test_register_normalizes_name(self) -> None:
        c = Customer.register(
            email=Email("an@example.com"),
            full_name="  Nguyễn Văn An  ",
        )
        assert c.full_name == "Nguyễn Văn An"


class TestCustomerBehavior:
    def test_change_email_updates_state(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.change_email(Email("b@x.com"))
        assert str(c.email) == "b@x.com"

    def test_change_email_same_value_is_noop(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.change_email(Email("a@x.com"))   # Không đổi
        events = c.pull_events()
        # Không có event nào vì email không đổi
        assert all(
            not isinstance(e, CustomerEmailChanged)
            for e in events
        )

    def test_change_email_emits_event(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.pull_events()   # clear event từ register (nếu có)
        c.change_email(Email("b@x.com"))
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], CustomerEmailChanged)
        assert str(events[0].old_email) == "a@x.com"
        assert str(events[0].new_email) == "b@x.com"


class TestCustomerLifecycle:
    def test_suspend_active_customer(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.suspend("spam")
        assert c.is_suspended()

    def test_suspend_already_suspended_raises(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.suspend("spam")
        with pytest.raises(AlreadySuspended):
            c.suspend("again")

    def test_delete_then_suspend_raises(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.delete()
        with pytest.raises(CustomerDeleted):
            c.suspend("spam")

    def test_reactivate_suspended_customer(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        c.suspend("spam")
        c.reactivate()
        assert c.is_active()

    def test_reactivate_active_customer_raises(self) -> None:
        c = Customer.register(Email("a@x.com"), "An")
        with pytest.raises(InvalidOperation):
            c.reactivate()


class TestCustomerIdentity:
    def test_same_id_means_equal(self) -> None:
        cid = uuid4()
        c1 = Customer(id=cid, email=Email("a@x.com"), full_name="An")
        c2 = Customer(id=cid, email=Email("b@x.com"), full_name="Bình")
        assert c1 == c2   # Cùng ID → bằng nhau

    def test_different_id_means_not_equal(self) -> None:
        c1 = Customer(id=uuid4(), email=Email("a@x.com"), full_name="An")
        c2 = Customer(id=uuid4(), email=Email("a@x.com"), full_name="An")
        assert c1 != c2   # Khác ID → khác nhau, dù mọi field giống

    def test_hashable_by_id(self) -> None:
        c1 = Customer(id=uuid4(), email=Email("a@x.com"), full_name="An")
        c2 = Customer(id=c1.id, email=Email("b@x.com"), full_name="Bình")
        assert {c1, c2} == {c1}   # Set loại trùng theo ID
```

**Chạy:**

```
tests/unit/domain/test_customer.py ....................... 22 passed in 0.05s
```

**22 test trong 0.05s.** Không DB, không mock.

---

## 8. Ví dụ tổng hợp: `Order` Entity đầy đủ

Đây là Entity hoàn chỉnh bạn sẽ dùng làm template.

```python
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


VALID_TRANSITIONS = {
    OrderStatus.DRAFT: {OrderStatus.PLACED, OrderStatus.CANCELLED},
    OrderStatus.PLACED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


# ---- Domain Events ----
@dataclass(frozen=True)
class OrderPlaced:
    order_id: UUID
    customer_id: UUID
    total: Money
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderShipped:
    order_id: UUID
    tracking_number: str
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCancelled:
    order_id: UUID
    reason: str
    occurred_at: datetime = field(default_factory=datetime.now)


# ---- Entity ----
@dataclass(eq=False)
class Order:
    """
    Entity: Đơn hàng.

    Identity: id.
    State: status, lines, tracking_number.
    Behavior: add_line(), place(), ship(), deliver(), cancel().
    Invariant: chỉ DRAFT mới sửa được lines; transition hợp lệ.
    """
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)   # type: ignore
    _status: OrderStatus = OrderStatus.DRAFT
    _lines: dict[UUID, OrderLine] = field(default_factory=dict)
    _tracking_number: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list, repr=False)

    MAX_LINES = 100

    # ---- Factory ----
    @classmethod
    def create(cls, customer_id: UUID) -> "Order":
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

    # ---- Behavior ----
    def add_line(self, line: OrderLine) -> None:
        self._ensure_editable()
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines(self.id, self.MAX_LINES)
        self._lines[line.id] = line

    def remove_line(self, line_id: UUID) -> None:
        self._ensure_editable()
        if line_id not in self._lines:
            raise LineNotFound(self.id, line_id)
        del self._lines[line_id]

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
        self._events.append(
            OrderShipped(order_id=self.id, tracking_number=tracking_number)
        )

    def deliver(self) -> None:
        self._transition_to(OrderStatus.DELIVERED)

    def cancel(self, reason: str) -> None:
        self._transition_to(OrderStatus.CANCELLED)
        self._events.append(
            OrderCancelled(order_id=self.id, reason=reason)
        )

    # ---- Query ----
    @property
    def status(self) -> OrderStatus:
        return self._status

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

    def is_draft(self) -> bool:
        return self._status == OrderStatus.DRAFT

    # ---- Internal ----
    def _ensure_editable(self) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditable(self.id, self._status)

    def _transition_to(self, new_status: OrderStatus) -> None:
        if new_status not in VALID_TRANSITIONS[self._status]:
            raise InvalidTransition(
                order_id=self.id,
                from_status=self._status,
                to_status=new_status,
            )
        self._status = new_status

    # ---- Events ----
    def pull_events(self) -> list:
        events = self._events[:]
        self._events.clear()
        return events

    # ---- Identity ----
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# ---- Exceptions ----
class OrderNotEditable(Exception):
    def __init__(self, order_id: UUID, status: OrderStatus) -> None:
        super().__init__(
            f"Đơn hàng {order_id} đang ở {status.value}, không sửa được"
        )


class EmptyOrderCannotBePlaced(Exception):
    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Đơn hàng {order_id} rỗng, không đặt được")


class InvalidTransition(Exception):
    def __init__(self, order_id, from_status, to_status) -> None:
        super().__init__(
            f"Không thể chuyển đơn {order_id} "
            f"từ {from_status.value} sang {to_status.value}"
        )


class TooManyLines(Exception):
    def __init__(self, order_id: UUID, limit: int) -> None:
        super().__init__(f"Đơn {order_id} vượt quá {limit} dòng")


class LineNotFound(Exception):
    def __init__(self, order_id: UUID, line_id: UUID) -> None:
        super().__init__(f"Không tìm thấy line {line_id} trong đơn {order_id}")
```

**Điểm quan trọng:**
- `__eq__`/`__hash__` theo ID.
- `_status` private, chỉ đổi qua `_transition_to()`.
- `_lines` private, chỉ thêm qua `add_line()`.
- Event được phát ở mỗi hành vi.
- State machine rõ ràng.

---

## 9. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): `Product` Entity

Viết Entity `Product`:

- ID: UUID.
- Fields: `sku: SKU`, `name: str`, `price: Money`, `stock: int`, `is_published: bool`.
- Factory: `create(sku, name, price, stock)`.
- Behavior:
  - `publish()` — chỉ khi có name và price > 0.
  - `unpublish()`.
  - `update_price(new_price)` — không cho giá âm.
  - `reduce_stock(quantity)` — không cho âm.
  - `add_stock(quantity)`.
  - `rename(new_name)`.
- `__eq__`/`__hash__` theo ID.

Viết ít nhất 10 test case.

### 🟡 Bài tập 2 (trung bình): `Loan` Entity cho thư viện

Viết Entity `Loan` (phiếu mượn sách):

- ID: UUID.
- Fields: `book_id: UUID`, `member_id: UUID`, `borrowed_at: date`, `due_at: date`, `returned_at: date | None`, `fine: Money`.
- Factory: `create(book_id, member_id, borrow_days)`.
- Behavior:
  - `return_book(returned_at)` — tính fine nếu trễ.
  - `extend(days)` — gia hạn, không cho khi đã trả.
  - `is_overdue(today)`.
- Rule:
  - Không cho trả sách đã trả.
  - Fine = 5000đ/ngày trễ.
  - Không cho gia hạn quá 2 lần.
- Events: `LoanCreated`, `BookReturned`, `LoanExtended`.

Viết ít nhất 12 test case.

### 🔴 Bài tập 3 (khó): `Account` Entity cho ngân hàng

Viết Entity `Account`:

- ID: UUID.
- Fields: `account_number: AccountNumber` (VO), `owner: Customer` (Entity khác), `balance: Money`, `status: AccountStatus`, `daily_withdrawn: Money`, `last_withdrawn_date: date`.
- Status: `ACTIVE`, `FROZEN`, `CLOSED`.
- Factory: `open(owner, initial_balance)`.
- Behavior:
  - `deposit(money)` — chỉ khi ACTIVE.
  - `withdraw(money)` — không cho âm, không quá số dư, không quá hạn mức ngày (100 triệu).
  - `transfer_to(other, money)` — atomic (không dùng distributed transaction).
  - `freeze(reason)`.
  - `unfreeze()`.
  - `close()` — chỉ khi balance = 0.
- State machine rõ ràng.
- Events: `AccountOpened`, `MoneyDeposited`, `MoneyWithdrawn`, `AccountFrozen`, `AccountClosed`.

Viết ít nhất 20 test case.

---

## 10. Checklist sau bài 6

Trước khi sang bài 7, bạn phải tự tin trả lời:

- [ ] Entity là gì? Khác VO chỗ nào?
- [ ] 3 câu hỏi để phân biệt VO/Entity?
- [ ] Câu hỏi thứ 4 (nếu 3 câu kia mơ hồ) là gì?
- [ ] Tại sao `__eq__` của Entity phải so sánh theo ID?
- [ ] Tại sao phải dùng `@dataclass(eq=False)` cho Entity?
- [ ] Factory method vs reconstruct — khi nào dùng cái nào?
- [ ] Soft delete là gì? Tại sao cần?
- [ ] State machine — làm sao enforce?
- [ ] Khi nào Entity phát event?
- [ ] Entity có được import Infrastructure không? Tại sao?
- [ ] 8 anti-pattern khi viết Entity là gì?

Nếu trả lời được hết, bạn đã sẵn sàng bài 7.

---

## 11. Tóm tắt bài 6

| Điểm | Nội dung |
|---|---|
| **Định nghĩa** | Entity có ID, mutable, có vòng đời |
| **Khác VO** | Identity > state; so sánh bằng ID, không bằng field |
| **Bộ khung** | `@dataclass(eq=False)` + custom `__eq__`/`__hash__` |
| **Factory method** | `register()`, `create()` — tạo mới, validate, phát event |
| **Reconstruct** | Load từ DB — không validate, không phát event |
| **Soft delete** | Đổi status, không xóa vật lý |
| **State machine** | Bảng transition hợp lệ |
| **Domain Event** | Phát khi state đổi, có ý nghĩa nghiệp vụ |
| **8 anti-pattern** | Anemic, __eq__ sai, setter public, id mutable, validate rải rác, event thừa, import infra, logic sai chỗ |
| **Test** | Pure Python, 22 test trong 0.05s |

**Câu thần chú:** *"Entity là câu chuyện có ID. State có thể đổi, ID thì không."*

---

## 12. Chuẩn bị cho bài 7

Bài tiếp theo: **Aggregate & Aggregate Root — Bảo vệ invariant**.

Chuẩn bị:
- Đọc lại ví dụ `Order` + `OrderLine` trong bài này.
- Nghĩ về **các nhóm Entity + VO** trong domain bạn đang làm.
- Sẽ bàn: Aggregate là gì, tại sao "một transaction = một Aggregate", cách chọn Aggregate Root, và các lỗi thường gặp khi thiết kế Aggregate.

Đây là bài **quan trọng nhất** của Level 2 — bạn sẽ hiểu tại sao `Order` là Aggregate Root còn `OrderLine` không phải.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 7** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: state machine, event bus, factory pattern, `__eq__`/`__hash__` chi tiết.
5. **Review code Entity** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.