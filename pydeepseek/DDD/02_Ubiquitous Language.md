# 📖 Bài 2: Ubiquitous Language — Ngôn ngữ chung

> Bài này dạy bạn **cách đặt tên** trong code DDD. Nghe thì đơn giản, nhưng đây là kỹ năng mà 90% dev Python làm sai. Sau bài này, bạn sẽ không bao giờ đặt tên `UserRecord`, `process_data`, hay `set_status(1)` nữa.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Ubiquitous Language** là gì và tại sao nó là **nền tảng số 1** của DDD.
2. Nhận diện được **translation gap** — khoảng cách ngôn ngữ giữa business và dev.
3. Biết **quy tắc đặt tên** cho class, method, biến, exception.
4. Xây dựng **glossary** (từ điển nghiệp vụ) cho một domain.
5. Refactor được một đoạn code CRUD thành code DDD chỉ bằng cách đổi tên + tái cấu trúc.

---

## 1. Ubiquitous Language là gì?

**Ubiquitous Language** (tạm dịch: "ngôn ngữ phổ quát") là **ngôn ngữ mà cả team business và team dev cùng dùng**, và **được thể hiện trực tiếp trong code**.

### Định nghĩa đầy đủ

> *"Ubiquitous Language là ngôn ngữ có cấu trúc, được xây dựng xung quanh domain model, và được dùng bởi TẤT CẢ các thành viên trong team — từ chuyên gia nghiệp vụ, đến dev, đến tester — trong MỌI giao tiếp: nói chuyện, viết tài liệu, viết code, đặt tên test."*
>
> — Eric Evans

### 3 tính chất quan trọng

1. **Chung (Shared)** — Không phải "ngôn ngữ của dev" hay "ngôn ngữ của business". Là **một** ngôn ngữ cho cả hai.
2. **Phổ quát (Ubiquitous)** — Có mặt ở mọi nơi: chat, tài liệu, code, test, commit message, ticket.
3. **Sống (Living)** — Không phải từ điển chết. Khi business thay đổi ngôn ngữ, code phải thay đổi theo **ngay lập tức**.

---

## 2. Translation Gap — Kẻ thù số 1

**Translation gap** = khoảng cách giữa cách business nói và cách code thể hiện. Đây là nguyên nhân của **80% bug nghiệp vụ** trong các dự án.

### 2.1. Ví dụ điển hình

Business nói:

> *"Khi khách hàng đặt cọc, nếu căn hộ chưa có ai giữ chỗ, thì giữ chỗ cho khách trong 48 giờ."*

Dev viết code:

```python
class ApartmentRecord:
    def __init__(self, id, status, holder_id, hold_until):
        self.id = id
        self.status = status       # 0 = available, 1 = held, 2 = sold
        self.holder_id = holder_id
        self.hold_until = hold_until

def process_deposit(apt_id, customer_id):
    apt = db.query("SELECT * FROM apartments WHERE id = ?", apt_id)
    if apt.status == 0:
        db.execute(
            "UPDATE apartments SET status = 1, holder_id = ?, hold_until = ? WHERE id = ?",
            customer_id, now() + timedelta(hours=48), apt_id
        )
        return True
    return False
```

**Bạn thấy translation gap ở đâu?**

| Business nói | Code thể hiện | Gap |
|---|---|---|
| "khách hàng" | `customer_id` (int) | Mất khái niệm Customer |
| "đặt cọc" | `process_deposit` | Động từ đúng, nhưng "deposit" có thể bị nhầm với "tiền gửi ngân hàng" |
| "căn hộ chưa có ai giữ chỗ" | `status == 0` | Ma thuật số 0 — không ai hiểu |
| "giữ chỗ 48 giờ" | `timedelta(hours=48)` | Magic number |
| "giữ chỗ" | `status = 1` | Ma thuật số 1 |

**Hậu quả:**
- Business đọc code → không nhận ra nghiệp vụ của họ.
- Dev mới vào → phải hỏi "status 0 là gì?".
- Business đổi rule "60 giờ" → dev phải tìm `timedelta(hours=48)` ở khắp nơi.
- Test viết `assert apt.status == 1` → người đọc không hiểu test đang kiểm tra gì.

### 2.2. Sửa lại bằng Ubiquitous Language

```python
from enum import Enum
from datetime import datetime, timedelta


class ApartmentStatus(Enum):
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    SOLD = "SOLD"


class Apartment:
    """
    Căn hộ — đơn vị nghiệp vụ cơ bản.

    Ubiquitous Language:
      - "giữ chỗ" → hold_for(customer, duration)
      - "còn trống" → is_available()
      - "đã bán" → is_sold()
    """
    HOLD_DURATION = timedelta(hours=48)   # business rule rõ ràng

    def __init__(self, apartment_id: str, status: ApartmentStatus = ApartmentStatus.AVAILABLE):
        self._id = apartment_id
        self._status = status
        self._held_by: str | None = None
        self._hold_expires_at: datetime | None = None

    def hold_for(self, customer_id: str) -> None:
        """Giữ chỗ căn hộ cho khách hàng. Business: 'đặt cọc giữ chỗ 48h'."""
        if not self.is_available():
            raise ApartmentNotAvailable(f"Căn hộ đang ở trạng thái {self._status.value}")
        self._status = ApartmentStatus.HELD
        self._held_by = customer_id
        self._hold_expires_at = datetime.now() + self.HOLD_DURATION

    def is_available(self) -> bool:
        """Căn hộ còn trống?"""
        return self._status == ApartmentStatus.AVAILABLE

    def is_held_by(self, customer_id: str) -> bool:
        return self._status == ApartmentStatus.HELD and self._held_by == customer_id

    def is_sold(self) -> bool:
        return self._status == ApartmentStatus.SOLD

    def release_hold(self) -> None:
        """Hủy giữ chỗ — quay về AVAILABLE."""
        if self._status != ApartmentStatus.HELD:
            raise InvalidOperation("Chỉ có thể hủy giữ chỗ khi đang HELD")
        self._status = ApartmentStatus.AVAILABLE
        self._held_by = None
        self._hold_expires_at = None

    def confirm_purchase(self, customer_id: str) -> None:
        """Chốt mua — từ HELD sang SOLD."""
        if not self.is_held_by(customer_id):
            raise InvalidOperation("Khách hàng này không giữ chỗ căn hộ")
        self._status = ApartmentStatus.SOLD
```

**So sánh:**

| Khía cạnh | Trước | Sau |
|---|---|---|
| Status | `0/1/2` | `ApartmentStatus.AVAILABLE/HELD/SOLD` |
| Hành vi | `process_deposit` (rời) | `apartment.hold_for(customer)` (trong entity) |
| Rule 48h | Magic number | `HOLD_DURATION` — có tên |
| Business đọc code | Không hiểu | Hiểu ngay |
| Test viết | `assert apt.status == 1` | `assert apt.is_held_by(customer_id)` |

**Giờ business đổi "60 giờ"**, dev chỉ sửa 1 dòng:

```python
HOLD_DURATION = timedelta(hours=60)
```

---

## 3. Quy tắc đặt tên trong DDD

Đây là phần **thực dụng nhất**. Tôi chia thành 5 nhóm.

### 3.1. Đặt tên class

#### Quy tắc

1. **Dùng danh từ nghiệp vụ**, không dùng danh từ kỹ thuật.
2. **Số ít** — `Order` chứ không phải `Orders`.
3. **Không có hậu tố kỹ thuật** — không `OrderRecord`, `OrderDTO`, `OrderModel`, `OrderEntity`.
4. **Tên phải có trong glossary** — nếu business không dùng từ đó, đừng dùng.

#### Ví dụ

| ❌ Sai | ✅ Đúng | Lý do |
|---|---|---|
| `UserRecord` | `Customer` | "Record" là từ kỹ thuật |
| `OrderData` | `Order` | "Data" là từ vô nghĩa |
| `OrderEntity` | `Order` | "Entity" là meta-language |
| `OrderModel` | `Order` | "Model" mơ hồ |
| `OrderDTO` | `OrderSummary` | DTO là tên kỹ thuật, đặt theo mục đích |
| `PaymentInfo` | `PaymentMethod` | Cụ thể hóa |
| `DataProcessor` | `InvoiceGenerator` | Nêu rõ đối tượng |
| `Manager`, `Helper`, `Util` | (không dùng) | Quá mơ hồ |

#### Lưu ý về suffix

Trong DDD Python, **hậu tố kỹ thuật chỉ dùng ở tầng Infrastructure/Presentation**, không dùng ở Domain:

```python
# ✅ Domain layer — không suffix
class Order: ...

# ✅ Infrastructure layer — có suffix để phân biệt
class OrderRow(Base): ...              # SQLAlchemy model
class OrderSchema(BaseModel): ...      # Pydantic schema (Presentation)
class SqlAlchemyOrderRepository: ...   # Repository implementation
```

> 💡 **Nguyên tắc:** Trong `domain/`, class không có suffix kỹ thuật. Suffix kỹ thuật chỉ xuất hiện từ `infrastructure/` trở ra.

### 3.2. Đặt tên method

#### Quy tắc

1. **Động từ nghiệp vụ**, không phải `get/set/update/process/handle`.
2. **Thể hiện intent**, không phải cơ chế.
3. **Trả về giá trị hoặc raise exception** — không trả về `bool` để báo lỗi.
4. **Không có tham số ma thuật** — `approve()` chứ không `set_status(2)`.

#### Ví dụ

| ❌ Sai | ✅ Đúng | Lý do |
|---|---|---|
| `set_status(2)` | `approve()` | Nêu intent |
| `update_balance(x)` | `deposit(money)` / `withdraw(money)` | Chia nhỏ theo hành vi |
| `process()` | `charge_customer()` | Cụ thể |
| `handle_payment()` | `record_payment_received(payment)` | Nêu rõ |
| `do_thing()` | (không dùng) | — |
| `get_user()` | `find_customer_by_id(id)` | Nêu rõ tìm cái gì |
| `calc_total()` | `calculate_total()` hoặc property `total` | Đủ chữ |
| `check_valid()` | `is_valid()` | Boolean → prefix `is/has/can` |

#### Bảng chuyển đổi get/set

| Kỹ thuật | Nghiệp vụ |
|---|---|
| `get_balance()` | property `balance` |
| `set_balance(x)` | `deposit(money)` / `withdraw(money)` / `adjust(money, reason)` |
| `get_status()` | property `status` |
| `set_status(s)` | `activate()` / `suspend(reason)` / `close()` |
| `get_total()` | property `total` |
| `update_email(e)` | `change_email(new_email)` |

#### Prefix quy ước

| Prefix | Ý nghĩa | Ví dụ |
|---|---|---|
| `is_` / `has_` / `can_` | Trả về bool | `is_active()`, `has_debt()`, `can_withdraw()` |
| `find_` / `get_` | Truy vấn, không đổi state | `find_by_id(id)` |
| `calculate_` / `compute_` | Tính toán | `calculate_tax()` |
| `ensure_` / `assert_` | Validate invariant (private) | `_ensure_positive(amount)` |
| `record_` | Ghi nhận điều gì đã xảy ra | `record_payment(payment)` |

### 3.3. Đặt tên biến

#### Quy tắc

1. **Tránh viết tắt** — `customer` chứ không `cust`, `amount` chứ không `amt`.
2. **Tránh tiền tố kiểu Hungary** — không `str_name`, `int_count`.
3. **Tránh tên chung chung** — không `data`, `info`, `obj`, `thing`, `item`.
4. **Số nhiều cho collection** — `orders`, `line_items`.
5. **Dùng từ trong glossary** — nếu business gọi là "hợp đồng", biến là `contract`, không phải `agreement`.

#### Ví dụ

| ❌ Sai | ✅ Đúng |
|---|---|
| `data = db.query(...)` | `customers = customer_repo.find_all()` |
| `obj = Order()` | `order = Order(...)` |
| `temp = amount * 0.1` | `tax = amount * TAX_RATE` |
| `arr = []` | `order_lines = []` |
| `flag = True` | `is_first_purchase = True` |
| `n = len(items)` | `line_count = len(order_lines)` |
| `res = process(x)` | `invoice = generate_invoice(order)` |

### 3.4. Đặt tên Exception

#### Quy tắc

1. **Mô tả điều gì sai**, không mô tả cơ chế.
2. **Kết thúc bằng `Error` hoặc `Exception`**.
3. **Thuộc domain** — không dùng `ValueError` ở tầng domain nếu lỗi là nghiệp vụ.
4. **Có ngữ cảnh** — exception tự mô tả được tình huống.

#### Ví dụ

| ❌ Sai | ✅ Đúng |
|---|---|
| `ValueError("invalid")` | `InvalidEmail(email)` |
| `Exception("not found")` | `CustomerNotFound(customer_id)` |
| `RuntimeError("wrong state")` | `OrderNotEditable(current_status)` |
| `Error("limit")` | `DailyWithdrawalLimitExceeded(limit, attempted)` |
| `CustomException("x")` | `InsufficientFunds(required, available)` |

#### Code mẫu

```python
# domain/exceptions.py

class DomainError(Exception):
    """Base exception cho mọi lỗi nghiệp vụ."""


class InvalidEmail(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Email không hợp lệ: {email!r}")
        self.email = email


class InsufficientFunds(DomainError):
    def __init__(self, required: "Money", available: "Money"):
        super().__init__(
            f"Không đủ số dư: cần {required}, chỉ có {available}"
        )
        self.required = required
        self.available = available


class OrderNotEditable(DomainError):
    def __init__(self, current_status: str):
        super().__init__(
            f"Đơn hàng đang ở trạng thái {current_status!r}, không thể sửa"
        )
        self.current_status = current_status
```

### 3.5. Đặt tên test

#### Quy tắc

1. **Tên test là câu mô tả hành vi** — đọc lên hiểu ngay.
2. **Format:** `test_<hành_vi>_<điều_kiện>_<kỳ_vọng>`.
3. **Dùng từ trong Ubiquitous Language** — không `test_process_1`.
4. **Không dùng số** — `test_withdraw_ok_1`, `test_withdraw_ok_2` là dấu hiệu tệ.

#### Ví dụ

| ❌ Sai | ✅ Đúng |
|---|---|
| `test_1()` | `test_withdraw_reduces_balance()` |
| `test_ok()` | `test_deposit_increases_balance()` |
| `test_fail()` | `test_withdraw_more_than_balance_raises_insufficient_funds()` |
| `test_process()` | `test_confirm_payment_changes_status_to_confirmed()` |
| `test_edge_case()` | `test_withdraw_exactly_full_balance_is_allowed()` |

#### Code mẫu

```python
def test_withdraw_reduces_balance():
    account = BankAccount(id=uuid4(), owner="An", _balance=Money(Decimal("100")))
    account.withdraw(Money(Decimal("30")))
    assert account.balance == Money(Decimal("70"))


def test_withdraw_more_than_balance_raises_insufficient_funds():
    account = BankAccount(id=uuid4(), owner="An", _balance=Money(Decimal("100")))
    with pytest.raises(InsufficientFunds):
        account.withdraw(Money(Decimal("150")))


def test_withdraw_exactly_full_balance_is_allowed():
    account = BankAccount(id=uuid4(), owner="An", _balance=Money(Decimal("100")))
    account.withdraw(Money(Decimal("100")))
    assert account.balance == Money(Decimal("0"))
```

> 💡 Đọc 3 test trên **không cần đọc body** — tên đã kể hết câu chuyện. Đây là mục tiêu của Ubiquitous Language trong test.

---

## 4. Xây dựng Glossary (Từ điển nghiệp vụ)

Đây là **bước đầu tiên** của mọi dự án DDD. Trước khi viết code, cả team ngồi lại và viết glossary.

### 4.1. Cấu trúc glossary

Mỗi thuật ngữ gồm:

| Trường | Nội dung |
|---|---|
| **Tên** | Thuật ngữ nghiệp vụ |
| **Định nghĩa** | Business định nghĩa (không phải dev) |
| **Ví dụ** | Ví dụ cụ thể |
| **Không bao gồm** | Những gì KHÔNG thuộc khái niệm này |
| **Từ đồng nghĩa** | Cách gọi khác (nếu có) |
| **Từ liên quan** | Thuật ngữ liên quan |

### 4.2. Ví dụ glossary cho domain "Thư viện"

```markdown
# Glossary — Hệ thống Thư viện

## Member (Thành viên)
- **Định nghĩa:** Người đã đăng ký và có quyền mượn sách từ thư viện.
- **Ví dụ:** Anh Nam, sinh viên MSSV 20201234, đã đăng ký từ 2023.
- **KHÔNG bao gồm:** Người chỉ đọc tại chỗ mà không đăng ký (→ Guest).
- **Từ đồng nghĩa:** Reader, Borrower (KHÔNG dùng — chốt dùng "Member").
- **Liên quan:** Loan, Reservation, Fine.

## Loan (Phiếu mượn)
- **Định nghĩa:** Giao dịch mượn 1 cuốn sách của 1 Member, có ngày mượn + hạn trả.
- **Ví dụ:** Member #123 mượn "Clean Code" từ 1/10 đến 15/10.
- **KHÔNG bao gồm:** Đặt trước sách (→ Reservation).
- **Liên quan:** Book, Member, Return, Overdue, Fine.

## Reservation (Đặt trước)
- **Định nghĩa:** Member đăng ký nhận sách khi sách được trả về.
- **Ví dụ:** Member #123 đặt trước "DDD" vì hiện đang được mượn.
- **KHÔNG bao gồm:** Mượn trực tiếp (→ Loan).
- **Liên quan:** Loan, Book, Hold Queue.

## Fine (Tiền phạt)
- **Định nghĩa:** Số tiền Member phải trả khi trả sách trễ hoặc làm hỏng sách.
- **Ví dụ:** Trả trễ 3 ngày → phạt 15.000đ.
- **KHÔNG bao gồm:** Phí đăng ký thành viên (→ Membership Fee).
- **Liên quan:** Loan, Overdue.

## Overdue (Quá hạn)
- **Định nghĩa:** Trạng thái của Loan khi ngày hiện tại > hạn trả.
- **Ví dụ:** Loan hạn 15/10, hôm nay 18/10 → Overdue 3 ngày.
- **KHÔNG bao gồm:** Sắp đến hạn.
- **Liên quan:** Loan, Fine.
```

### 4.3. Từ vựng bị cấm (Forbidden Words)

Đây là **kỹ thuật mạnh** để giữ Ubiquitous Language sạch:

```markdown
# Từ vựng bị cấm trong code

| Từ bị cấm | Thay bằng | Lý do |
|---|---|---|
| `data`, `info` | (đặt tên cụ thể) | Vô nghĩa |
| `manager`, `helper`, `util` | (đặt tên theo trách nhiệm) | Mơ hồ |
| `process`, `handle`, `do` | động từ cụ thể | Mơ hồ |
| `flag`, `status` (int) | Enum có tên | Ma thuật |
| `Record`, `Entity`, `Model`, `DTO` (trong domain) | (bỏ suffix) | Meta-language |
| `temp`, `tmp`, `x`, `y` | (đặt tên có nghĩa) | Khó đọc |
| `get_*`, `set_*` | property / method nghiệp vụ | Kỹ thuật |
```

---

## 5. Refactor thực hành

Chúng ta sẽ refactor một đoạn code CRUD **thực tế** thành code DDD chỉ bằng cách:

1. Xây glossary.
2. Đổi tên class / method / biến.
3. Chuyển logic từ Service về Entity.

### 5.1. Code gốc (CRUD)

```python
class UserRecord:
    def __init__(self, id, email, pwd, status, created):
        self.id = id
        self.email = email
        self.pwd = pwd
        self.status = status
        self.created = created


class UserService:
    def register(self, email, pwd):
        # validate
        if "@" not in email:
            return {"error": "bad email"}
        if len(pwd) < 8:
            return {"error": "short pwd"}
        # check duplicate
        existing = db.query("SELECT * FROM users WHERE email = ?", email)
        if existing:
            return {"error": "email taken"}
        # hash
        import hashlib
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        # insert
        db.execute(
            "INSERT INTO users (email, pwd, status, created) VALUES (?, ?, 1, ?)",
            email, hashed, now()
        )
        return {"ok": True}

    def login(self, email, pwd):
        user = db.query("SELECT * FROM users WHERE email = ?", email)
        if not user:
            return {"error": "not found"}
        if user.status == 0:
            return {"error": "banned"}
        import hashlib
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        if user.pwd != hashed:
            return {"error": "wrong"}
        return {"ok": True, "user_id": user.id}
```

### 5.2. Bước 1 — Xây glossary

```markdown
# Glossary — User Authentication

## Account
- Người dùng có thể đăng nhập.
- KHÔNG bao gồm: profile, avatar, role (những cái đó là User Profile).

## Credentials
- Cặp (email, password) dùng để xác thực.
- KHÔNG bao gồm: token, session.

## Email
- Địa chỉ email hợp lệ theo RFC 5322 (đơn giản hóa).
- Phải lowercase trước khi lưu.

## Password
- Chuỗi ≥ 8 ký tự, có chữ hoa/thường/số.
- Luôn lưu dưới dạng hash.

## AccountStatus
- ACTIVE: đăng nhập được.
- SUSPENDED: tạm khóa.
- DELETED: đã xóa (soft delete).

## Từ vựng cấm
- `user` → dùng `Account` (tránh nhầm với User Profile sau này).
- `pwd` → dùng `password` (không viết tắt).
- `status = 0/1` → dùng enum.
- `register` → dùng `register_account` (động từ + danh từ).
- `login` → dùng `authenticate` (nghiệp vụ hơn).
```

### 5.3. Bước 2 — Viết lại Domain

```python
# domain/model/email.py
import re
from dataclasses import dataclass


class InvalidEmail(Exception):
    pass


@dataclass(frozen=True)
class Email:
    value: str

    _PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not self._PATTERN.match(normalized):
            raise InvalidEmail(f"Email không hợp lệ: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value
```

```python
# domain/model/password.py
from dataclasses import dataclass
import hashlib
import re


class InvalidPassword(Exception):
    pass


@dataclass(frozen=True)
class Password:
    _hashed: str

    MIN_LENGTH = 8

    @classmethod
    def from_plain(cls, plain: str) -> "Password":
        cls._validate(plain)
        return cls(_hashed=hashlib.sha256(plain.encode()).hexdigest())

    @classmethod
    def from_hash(cls, hashed: str) -> "Password":
        return cls(_hashed=hashed)

    def matches(self, plain: str) -> bool:
        return self._hashed == hashlib.sha256(plain.encode()).hexdigest()

    @classmethod
    def _validate(cls, plain: str) -> None:
        if len(plain) < cls.MIN_LENGTH:
            raise InvalidPassword(f"Password phải ≥ {cls.MIN_LENGTH} ký tự")
        if not re.search(r"[A-Z]", plain):
            raise InvalidPassword("Password phải có chữ hoa")
        if not re.search(r"[a-z]", plain):
            raise InvalidPassword("Password phải có chữ thường")
        if not re.search(r"\d", plain):
            raise InvalidPassword("Password phải có chữ số")
```

```python
# domain/model/account.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from .email import Email
from .password import Password


class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class AccountSuspended(Exception):
    pass


class AccountDeleted(Exception):
    pass


@dataclass
class Account:
    """
    Aggregate Root — đại diện cho người dùng có thể đăng nhập.

    Ubiquitous Language:
      - "đăng ký" → register_account (Application Service)
      - "xác thực" → authenticate(password)
      - "khóa tài khoản" → suspend(reason)
    """
    id: UUID
    email: Email
    password: Password
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def register(cls, email: Email, password: Password) -> "Account":
        return cls(id=uuid4(), email=email, password=password)

    def authenticate(self, plain_password: str) -> None:
        """Xác thực mật khẩu. Raise nếu sai."""
        if self.status == AccountStatus.SUSPENDED:
            raise AccountSuspended("Tài khoản đang bị tạm khóa")
        if self.status == AccountStatus.DELETED:
            raise AccountDeleted("Tài khoản đã bị xóa")
        if not self.password.matches(plain_password):
            raise InvalidCredentials("Email hoặc mật khẩu không đúng")

    def suspend(self, reason: str) -> None:
        if self.status == AccountStatus.DELETED:
            raise AccountDeleted("Không thể khóa tài khoản đã xóa")
        self.status = AccountStatus.SUSPENDED

    def reactivate(self) -> None:
        if self.status != AccountStatus.SUSPENDED:
            raise InvalidOperation("Chỉ kích hoạt lại được tài khoản SUSPENDED")
        self.status = AccountStatus.ACTIVE


class InvalidCredentials(Exception):
    pass


class InvalidOperation(Exception):
    pass
```

```python
# domain/repositories/account_repository.py
from typing import Protocol
from uuid import UUID
from ..model.account import Account
from ..model.email import Email


class AccountRepository(Protocol):
    def find_by_id(self, account_id: UUID) -> Account | None: ...
    def find_by_email(self, email: Email) -> Account | None: ...
    def save(self, account: Account) -> None: ...
```

### 5.4. Bước 3 — Application Service

```python
# application/commands/register_account.py
from dataclasses import dataclass
from ..uow import UnitOfWork
from ...domain.model.account import Account
from ...domain.model.email import Email
from ...domain.model.password import Password


class EmailAlreadyTaken(Exception):
    pass


@dataclass(frozen=True)
class RegisterAccountCommand:
    email: str
    password: str


class RegisterAccountHandler:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, cmd: RegisterAccountCommand) -> str:
        email = Email(cmd.email)
        password = Password.from_plain(cmd.password)

        with self._uow:
            if self._uow.accounts.find_by_email(email):
                raise EmailAlreadyTaken(str(email))
            account = Account.register(email, password)
            self._uow.accounts.save(account)
            self._uow.commit()
        return str(account.id)
```

```python
# application/commands/authenticate.py
@dataclass(frozen=True)
class AuthenticateCommand:
    email: str
    password: str


class AuthenticateHandler:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def handle(self, cmd: AuthenticateCommand) -> str:
        email = Email(cmd.email)
        with self._uow:
            account = self._uow.accounts.find_by_email(email)
            if not account:
                raise InvalidCredentials("Email hoặc mật khẩu không đúng")
            account.authenticate(cmd.password)
        return str(account.id)
```

### 5.5. So sánh trước/sau

| Trước | Sau |
|---|---|
| `UserRecord` | `Account` |
| `user.status == 0` | `AccountStatus.SUSPENDED` |
| `return {"error": "bad email"}` | `raise InvalidEmail(...)` |
| `register(email, pwd)` | `RegisterAccountHandler.handle(RegisterAccountCommand(email, password))` |
| Validate ở Service | Validate ở `Email`/`Password` VO |
| Hash ở Service | Hash ở `Password.from_plain` |
| `login()` | `authenticate()` |
| `status = 1` | `AccountStatus.ACTIVE` |
| Magic string `"email taken"` | Exception `EmailAlreadyTaken` |

**Điều kỳ diệu:** Đọc code sau, business đọc hiểu ngay:

> *"Account đăng ký với email và password. Khi authenticate, nếu SUSPENDED thì raise. Nếu password sai thì raise InvalidCredentials."*

Không cần dịch từ "code" sang "nghiệp vụ" nữa.

---

## 6. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Chuyển đổi enum

Cho code sau:

```python
class OrderRecord:
    def __init__(self, id, status):
        self.id = id
        self.status = status   # 0=draft, 1=placed, 2=shipped, 3=delivered, 4=cancelled

def update_status(order_id, new_status):
    if new_status not in [0, 1, 2, 3, 4]:
        raise ValueError("invalid")
    db.execute("UPDATE orders SET status = ? WHERE id = ?", new_status, order_id)
```

**Yêu cầu:**
1. Tạo enum `OrderStatus`.
2. Đổi `update_status` thành các method nghiệp vụ: `place()`, `ship()`, `deliver()`, `cancel(reason)`.
3. Mỗi method phải kiểm tra transition hợp lệ (ví dụ: không thể ship đơn chưa place).
4. Viết 6 test case.

### 🟡 Bài tập 2 (trung bình): Glossary cho domain "Nhà hàng"

Xây glossary cho hệ thống **đặt bàn nhà hàng**:

- Ít nhất 10 thuật ngữ.
- Mỗi thuật ngữ có: định nghĩa, ví dụ, KHÔNG bao gồm, từ liên quan.
- Có mục **Từ vựng bị cấm** với ít nhất 8 từ.

Sau đó viết code cho 3 class domain chính dựa trên glossary.

### 🔴 Bài tập 3 (khó): Refactor toàn bộ module

Cho module CRUD sau (bạn tự viết lại cho đầy đủ):

```python
class ProductRecord:
    def __init__(self, id, name, price, stock, category):
        ...

class ProductService:
    def create_product(self, name, price, stock, category):
        # validate
        ...

    def update_price(self, product_id, new_price):
        ...

    def add_stock(self, product_id, qty):
        ...

    def remove_stock(self, product_id, qty):
        ...

    def apply_discount(self, product_id, percent):
        ...

    def discontinue(self, product_id):
        ...
```

**Yêu cầu:**
1. Xây glossary cho domain "Product" (ít nhất 8 thuật ngữ).
2. Xác định Value Object, Entity, Aggregate Root.
3. Refactor theo DDD:
   - `Money`, `SKU`, `Category` là VO.
   - `Product` là Aggregate Root.
   - Rule: giá không âm, stock ≥ 0, discount ≤ 50%, không sửa sản phẩm đã discontinue.
4. Viết ít nhất 12 test case.
5. Viết 1 đoạn văn ngắn (5-7 câu) giải thích domain bằng ngôn ngữ nghiệp vụ.

---

## 7. Checklist sau bài 2

Trước khi sang bài 3, bạn phải tự tin trả lời:

- [ ] Ubiquitous Language là gì? Tại sao cần?
- [ ] Translation gap là gì? Cho ví dụ.
- [ ] Tại sao không dùng `Record`, `Model`, `DTO` trong domain layer?
- [ ] Sự khác biệt giữa `set_status(2)` và `approve()`?
- [ ] Khi nào dùng `is_/has_/can_` prefix?
- [ ] Tại sao exception phải mang ngữ cảnh? Cho ví dụ.
- [ ] Tên test phải kể được câu chuyện gì?
- [ ] Glossary gồm những trường nào?
- [ ] Từ vựng bị cấm — cho 5 từ và lý do.

Nếu trả lời được hết, bạn đã sẵn sàng bài 3.

---

## 8. Tóm tắt

| Điểm | Nội dung |
|---|---|
| **Định nghĩa** | Ubiquitous Language = ngôn ngữ chung giữa business và dev, thể hiện trực tiếp trong code |
| **Kẻ thù** | Translation gap — khoảng cách giữa cách nói và cách code |
| **Nguyên tắc class** | Danh từ nghiệp vụ, số ít, không suffix kỹ thuật |
| **Nguyên tắc method** | Động từ nghiệp vụ, nêu intent, không get/set |
| **Nguyên tắc biến** | Không viết tắt, không `data/info/obj` |
| **Nguyên tắc exception** | Có ngữ cảnh, thuộc domain, kết thúc bằng `Error` |
| **Nguyên tắc test** | Tên test kể câu chuyện, dùng từ glossary |
| **Công cụ** | Glossary + Forbidden Words list |
| **Lợi ích** | Business đọc code hiểu ngay, giảm bug, dễ bảo trì |

---

## 9. Chuẩn bị cho bài 3

Bài tiếp theo: **Python + DDD — Những đặc trưng cần biết**.

Chuẩn bị:
- Cài đặt **Python 3.11+**.
- Cài `pytest`, `mypy`, `pydantic`.
- Đọc qua về `@dataclass`, `Protocol`, `frozen=True`.
- Sẽ bàn: Python mạnh/yếu ở đâu cho DDD, setup project chuẩn, cách enforce kỷ luật bằng tooling.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 3** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần nào đó (Translation gap, Exception design, Test naming...).
5. **Xây glossary thực tế** cho domain bạn đang làm việc — nếu bạn cho tôi biết domain đó là gì.

Nói tôi biết bạn muốn gì nhé.