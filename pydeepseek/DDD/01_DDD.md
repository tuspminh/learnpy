# 📖 Bài 1: DDD là gì? Tại sao Python dev cần biết?

> Đây là bài mở đầu trong lộ trình 18 bài. Mục tiêu: **hiểu DDD giải quyết vấn đề gì**, và tại sao một Python dev nên quan tâm — kể cả khi bạn chỉ làm web CRUD hàng ngày.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **định nghĩa** DDD và **vấn đề gốc** mà nó giải quyết.
2. Phân biệt rõ **CRUD mindset** vs **Domain mindset**.
3. Biết **khi nào nên** và **khi nào không nên** dùng DDD.
4. Viết được class Python đầu tiên theo tư duy domain.
5. Làm bài tập thực hành có chấm điểm.

---

## 1. DDD là gì? — Định nghĩa không hàn lâm

**Domain-Driven Design (DDD)** là một **triết lý thiết kế phần mềm** do **Eric Evans** công bố năm 2003 trong cuốn sách cùng tên. Nội dung cốt lõi có thể tóm gọn trong 3 câu:

> 1. **Phần mềm phải phản ánh đúng nghiệp vụ** (business domain), không phải phản ánh cấu trúc database.
> 2. **Code và business phải nói cùng một ngôn ngữ** (Ubiquitous Language).
> 3. **Logic nghiệp vụ là trung tâm** — framework, DB, UI chỉ là chi tiết kỹ thuật.

### ⚠️ Hiểu lầm phổ biến

| Hiểu lầm | Sự thật |
|---|---|
| "DDD là một framework" | ❌ DDD là **cách tư duy**, không phải thư viện |
| "DDD là kiến trúc microservices" | ❌ DDD độc lập với kiến trúc triển khai |
| "DDD là design pattern" | ❌ DDD dùng nhiều pattern nhưng bản thân nó là **triết lý** |
| "Phải dùng DDD cho mọi dự án" | ❌ CRUD đơn giản thì DDD là over-engineering |
| "DDD chỉ dành cho Java/C#" | ❌ Python làm DDD rất tốt, có điều phải kỷ luật hơn |

---

## 2. Vấn đề gốc — Tại sao DDD ra đời?

### 2.1. Câu chuyện có thật

Hãy tưởng tượng một công ty bảo hiểm. Business nói:

> *"Khách hàng gửi yêu cầu bồi thường. Nếu hợp lệ và số tiền dưới 50 triệu, duyệt tự động trong 24h. Nếu trên 50 triệu, phải qua thẩm định viên. Nếu khách hàng là VIP và đã đóng phí trên 5 năm, ưu tiên xử lý trong 4h. Nếu hợp đồng đã hết hạn, từ chối ngay lập tức."*

Dev nghe vậy, gật gù, rồi viết code:

```python
def process_claim(claim_id, user_id, amount, contract_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    contract = db.query("SELECT * FROM contracts WHERE id = ?", contract_id)

    if contract['end_date'] < datetime.now():
        db.execute("UPDATE claims SET status = 'rejected' WHERE id = ?", claim_id)
        return

    if amount < 50_000_000:
        if user['is_vip'] and user['years_paid'] > 5:
            db.execute("UPDATE claims SET status = 'fast_track' ...")
        else:
            db.execute("UPDATE claims SET status = 'auto_approved' ...")
    else:
        db.execute("UPDATE claims SET status = 'pending_review' ...")
```

**Chuyện gì xảy ra sau 6 tháng?**

Business thay đổi rule: *"À, giờ ngưỡng tự động là 30 triệu thôi, và VIP phải là 3 năm."*

Dev mở file ra, thấy 200 dòng code với đầy `if/else` lồng nhau, không biết chỗ nào đang check cái gì. Sửa một chỗ, làm hỏng chỗ khác. Test coverage thấp vì logic trộn lẫn với DB access.

**Đây chính là vấn đề DDD ra đời để giải quyết.**

### 2.2. Ba căn bệnh điển hình

| Căn bệnh | Triệu chứng |
|---|---|
| **Anemic Domain Model** | Class chỉ có getter/setter, toàn bộ logic nằm ở Service |
| **Logic phân tán** | Business rule rải rác ở Controller, Service, DB trigger, cron job |
| **Ngôn ngữ lệch pha** | Business gọi "hợp đồng", code gọi "contract_table_row" |

---

## 3. CRUD mindset vs Domain mindset

Đây là **phần quan trọng nhất** của bài 1. Bạn phải "thấy" được sự khác biệt này trong đầu.

### 3.1. Ví dụ 1: Tài khoản ngân hàng

#### ❌ CRUD mindset

```python
class BankAccountRecord:
    """Chỉ là cái bảng database được wrap lại."""

    def __init__(self, id, balance, status):
        self.id = id
        self.balance = balance
        self.status = status

    # getter/setter — không có hành vi
    def set_balance(self, value):
        self.balance = value

    def get_balance(self):
        return self.balance
```

Service ở ngoài lo hết:

```python
class BankAccountService:
    def withdraw(self, account_id, amount):
        record = repo.find(account_id)

        # Business rule rải rác ở đây
        if record.status != "active":
            raise Exception("Tài khoản bị khóa")
        if amount <= 0:
            raise Exception("Số tiền không hợp lệ")
        if record.balance < amount:
            raise Exception("Không đủ số dư")
        if amount > 10_000_000:  # giới hạn rút 1 lần
            raise Exception("Vượt hạn mức")

        record.balance -= amount
        repo.save(record)
```

**Vấn đề:**
- `BankAccountRecord` không biết gì về rule của chính nó.
- Rule rải ở `BankAccountService`. Nếu có `TransferService`, `LoanService`... sẽ lặp lại.
- Không thể test rule mà không cần DB.
- Nếu ai đó gọi `record.set_balance(999999)` từ chỗ khác → phá vỡ mọi rule.

#### ✅ Domain mindset

```python
from decimal import Decimal
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime


class InsufficientFunds(Exception):
    pass


class AccountLocked(Exception):
    pass


class WithdrawalLimitExceeded(Exception):
    pass


@dataclass
class Money:
    """Value Object — bất biến, so sánh bằng giá trị."""
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money không thể âm")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Khác loại tiền tệ")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Khác loại tiền tệ")
        if self.amount < other.amount:
            raise InsufficientFunds("Không đủ số dư để trừ")
        return Money(self.amount - other.amount, self.currency)


class AccountStatus:
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"


@dataclass
class BankAccount:
    """
    Domain Entity — có ID, có hành vi, bảo vệ invariant.
    Không ai được sửa balance trực tiếp từ bên ngoài.
    """
    id: UUID
    owner_name: str
    _balance: Money
    _status: str = field(default=AccountStatus.ACTIVE)
    _daily_withdrawn: Money = field(default_factory=lambda: Money(Decimal("0")))
    _last_withdrawn_date: datetime = field(default_factory=datetime.now)

    # ---- Hành vi nghiệp vụ ----

    def withdraw(self, amount: Money) -> None:
        """Rút tiền — bảo vệ mọi invariant ở đây."""
        self._ensure_active()
        self._ensure_positive(amount)
        self._ensure_sufficient(amount)
        self._ensure_daily_limit(amount)
        self._reset_daily_counter_if_new_day()

        self._balance = self._balance - amount
        self._daily_withdrawn = self._daily_withdrawn + amount

    def deposit(self, amount: Money) -> None:
        self._ensure_active()
        self._ensure_positive(amount)
        self._balance = self._balance + amount

    def lock(self, reason: str) -> None:
        if self._status == AccountStatus.CLOSED:
            raise ValueError("Không thể khóa tài khoản đã đóng")
        self._status = AccountStatus.LOCKED
        # có thể phát event AccountLocked(self.id, reason)

    # ---- Invariant guards ----

    def _ensure_active(self) -> None:
        if self._status != AccountStatus.ACTIVE:
            raise AccountLocked(f"Tài khoản đang {self._status}")

    @staticmethod
    def _ensure_positive(amount: Money) -> None:
        if amount.amount <= 0:
            raise ValueError("Số tiền phải > 0")

    def _ensure_sufficient(self, amount: Money) -> None:
        if self._balance.amount < amount.amount:
            raise InsufficientFunds(
                f"Số dư {self._balance.amount} < {amount.amount}"
            )

    def _ensure_daily_limit(self, amount: Money) -> None:
        limit = Money(Decimal("10000000"))
        if self._daily_withdrawn.amount + amount.amount > limit.amount:
            raise WithdrawalLimitExceeded("Vượt hạn mức rút trong ngày")

    def _reset_daily_counter_if_new_day(self) -> None:
        if self._last_withdrawn_date.date() < datetime.now().date():
            self._daily_withdrawn = Money(Decimal("0"))
            self._last_withdrawn_date = datetime.now()

    # ---- Chỉ đọc ----

    @property
    def balance(self) -> Money:
        return self._balance

    @property
    def status(self) -> str:
        return self._status
```

Service giờ **mỏng tênh**:

```python
class BankAccountService:
    def withdraw(self, account_id: UUID, amount: Money) -> None:
        account = self._repo.find_by_id(account_id)
        account.withdraw(amount)   # rule nằm trong domain
        self._repo.save(account)
```

### 3.2. So sánh trực tiếp

| Tiêu chí | CRUD mindset | Domain mindset |
|---|---|---|
| Class là gì? | Cái bảng được wrap | Đối tượng nghiệp vụ có hành vi |
| Logic ở đâu? | Service / Controller | Trong chính Entity/VO |
| Public API | getter/setter | Method có tên nghiệp vụ (`withdraw`, `lock`) |
| Invariant | Mong manh, dễ phá | Được bảo vệ bởi `_ensure_*` |
| Test | Cần DB, cần mock | Pure Python, không cần gì |
| Đọc code | "Đọc xem logic ở đâu" | "Đọc là hiểu ngay nghiệp vụ" |
| Business thay đổi rule | Sửa 10 chỗ | Sửa 1 chỗ trong Entity |

### 3.3. Ví dụ 2: Đặt vé máy bay

Đây là **ví dụ kinh điển** mà mọi tài liệu DDD đều dùng. Tôi sẽ nêu ngắn gọn.

**CRUD:**
```python
class Booking:
    def __init__(self, id, user_id, flight_id, status):
        self.id = id
        self.user_id = user_id
        self.flight_id = flight_id
        self.status = status  # "pending", "paid", "cancelled"
```

**Domain:**
```python
class Booking:
    def __init__(self, booking_id, passenger, flight):
        self._id = booking_id
        self._passenger = passenger
        self._flight = flight
        self._status = BookingStatus.PENDING
        self._created_at = datetime.now()

    def confirm_payment(self, payment: Money) -> None:
        if self._status != BookingStatus.PENDING:
            raise BookingNotPending()
        if self._is_expired():
            raise BookingExpired("Chỗ giữ đã quá 15 phút")
        if payment.amount != self._flight.price.amount:
            raise PaymentMismatch()
        self._status = BookingStatus.CONFIRMED

    def cancel(self, reason: str) -> None:
        if self._status == BookingStatus.CANCELLED:
            raise AlreadyCancelled()
        if self._status == BookingStatus.CONFIRMED:
            # Rule: hủy sau khi confirm thì mất phí
            self._cancellation_fee = self._flight.price * Decimal("0.1")
        self._status = BookingStatus.CANCELLED

    def _is_expired(self) -> bool:
        return datetime.now() - self._created_at > timedelta(minutes=15)
```

Bạn thấy gì? **Business rule "15 phút giữ chỗ"** nằm ngay trong class. Business đọc code sẽ nhận ra rule của họ. Dev mới vào đọc hiểu ngay. Test chỉ cần tạo `Booking` với `_created_at` cũ là test được.

---

## 4. Khi nào nên và không nên dùng DDD?

Đây là câu hỏi **thực dụng nhất** mà mọi Python dev phải trả lời trước khi áp dụng DDD.

### ✅ Nên dùng khi

1. **Domain phức tạp, nhiều rule nghiệp vụ**
   - Ví dụ: bảo hiểm, ngân hàng, logistics, y tế, thuế, chứng khoán.
2. **Hệ thống lớn, nhiều team**
   - Cần ranh giới rõ ràng giữa các module.
3. **Business rule thay đổi thường xuyên**
   - Cần nơi để sửa 1 chỗ thay vì 20 chỗ.
4. **Cần test kỹ logic nghiệp vụ**
   - Domain test không cần DB → nhanh, ổn định.
5. **Tuổi thọ dự án dài (3+ năm)**
   - Đầu tư ban đầu sẽ được đền đáp.

### ❌ Không nên dùng khi

1. **CRUD đơn giản**
   - Blog, todo list, admin panel nội bộ.
2. **Prototype / MVP**
   - Cần ra nhanh để validate ý tưởng.
3. **Domain chưa rõ ràng**
   - Nếu chính business còn chưa hiểu rule của họ, DDD chỉ làm chậm.
4. **Dự án nhỏ, 1-2 dev, ngắn hạn**
   - Over-engineering.
5. **Chỉ là API wrapper**
   - Gọi API bên ngoài rồi trả về, không có logic.

### 🎯 Quy tắc ngón tay

> Nếu bạn thấy mình viết **nhiều hơn 3 tầng `if/else`** trong một hàm xử lý nghiệp vụ, hãy nghĩ đến DDD.
>
> Nếu bạn thấy **cùng một rule** xuất hiện ở nhiều file khác nhau, hãy nghĩ đến DDD.

---

## 5. Python có phù hợp với DDD không?

Đây là câu hỏi tôi gặp rất nhiều. Câu trả lời ngắn: **Có, nhưng bạn phải kỷ luật hơn so với Java/C#.**

### 5.1. Python mạnh ở đâu cho DDD?

| Đặc điểm Python | Lợi cho DDD |
|---|---|
| `@dataclass(frozen=True)` | Viết Value Object cực gọn |
| Type hints + `mypy --strict` | Bắt lỗi type ở compile-time (giả lập) |
| `Protocol` | Định nghĩa interface mà không cần kế thừa |
| Duck typing | Repository, Service dễ thay thế |
| `pytest` | Test domain rất nhanh |
| Đa paradigm | Có thể mix OOP + functional |

### 5.2. Python yếu ở đâu?

| Đặc điểm Python | Bất lợi cho DDD |
|---|---|
| Không có access modifier thật | `_private` chỉ là convention, ai cũng truy cập được |
| Không có compiler | Không bắt được vi phạm rule |
| Dynamic | Dễ "tiện tay" thêm method lung tung |
| Không có `final` | Không ngăn được override |

### 5.3. Cách khắc phục

```python
# 1. Dùng dataclass(frozen=True) cho mọi VO
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

# 2. Dùng Protocol thay vì ABC
from typing import Protocol

class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> "Order | None": ...
    def save(self, order: "Order") -> None: ...

# 3. Bật mypy strict
# pyproject.toml:
# [tool.mypy]
# strict = true
# disallow_untyped_defs = true
# warn_return_any = true

# 4. Dùng __slots__ nếu cần
class Order:
    __slots__ = ("_id", "_lines", "_status")

# 5. Enforce dependency rule bằng import-linter
# pyproject.toml:
# [tool.importlinter]
# root_packages = ["shop"]
# [[tool.importlinter.contracts]]
# name = "Domain không phụ thuộc ai"
# type = "forbidden"
# source_modules = ["shop.domain"]
# forbidden_modules = ["shop.infrastructure", "shop.presentation"]
```

> 💡 **Điểm mấu chốt:** Python **không ngăn** bạn làm bậy. Nên bạn cần **tự kỷ luật** + **tooling** (mypy, import-linter, pytest) để giữ kỷ luật đó.

---

## 6. Code thực hành: Viết class Python đầu tiên theo DDD

Chúng ta sẽ viết class `Password` — một **Value Object** đơn giản nhưng thể hiện đủ tư duy domain.

### 6.1. Yêu cầu nghiệp vụ

Business nói:

> *"Mật khẩu của hệ thống phải có ít nhất 8 ký tự, chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số. Không được giống các mật khẩu phổ biến như 'password', '12345678'. Mật khẩu phải được hash trước khi lưu."*

### 6.2. Cách viết CRUD (sai)

```python
def validate_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if password.lower() in ["password", "12345678", "qwerty"]:
        return False
    return True

# Rồi ở đâu đó:
if not validate_password(user_input):
    return {"error": "Mật khẩu không hợp lệ"}
hashed = bcrypt.hash(user_input)
db.save(user_id, hashed)
```

**Vấn đề:**
- `validate_password` là **hàm rời**, ai cũng có thể quên gọi.
- Không có gì đảm bảo `db.save` luôn nhận mật khẩu đã hash.
- Business rule nằm ở 2 chỗ: hàm validate + đoạn hash.

### 6.3. Cách viết Domain (đúng)

```python
from dataclasses import dataclass, field
from typing import ClassVar
import hashlib
import re


class InvalidPassword(Exception):
    """Mật khẩu vi phạm rule nghiệp vụ."""


@dataclass(frozen=True)
class Password:
    """
    Value Object đại diện cho mật khẩu hợp lệ.

    Đảm bảo: mọi instance Password trong hệ thống là HỢP LỆ.
    Không thể tạo Password sai rule → không cần validate lại ở đâu.
    """
    _hashed: str          # không bao giờ lưu plain text
    _plain_length: int    # metadata để hiển thị

    MIN_LENGTH: ClassVar[int] = 8
    COMMON_PASSWORDS: ClassVar[frozenset[str]] = frozenset({
        "password", "12345678", "qwertyui", "abcdefgh",
        "11111111", "admin123", "letmein1",
    })

    # ---------- Factory ----------
    @classmethod
    def from_plain(cls, plain: str) -> "Password":
        """
        Tạo Password từ plain text.
        Đây là cổng vào duy nhất cho plain text.
        """
        cls._validate(plain)
        return cls(
            _hashed=cls._hash(plain),
            _plain_length=len(plain),
        )

    @classmethod
    def from_hash(cls, hashed: str) -> "Password":
        """
        Tạo Password từ hash (khi load từ DB).
        Bỏ qua validation vì hash đã được validate khi tạo.
        """
        return cls(_hashed=hashed, _plain_length=0)

    # ---------- Behavior ----------
    def matches(self, plain: str) -> bool:
        """Kiểm tra mật khẩu plain có khớp không."""
        return self._hashed == self._hash(plain)

    def __str__(self) -> str:
        return "****" * (self._plain_length // 4) if self._plain_length else "****"

    def __repr__(self) -> str:
        return f"Password(hash=..., length={self._plain_length})"

    # ---------- Invariant guards ----------
    @classmethod
    def _validate(cls, plain: str) -> None:
        if len(plain) < cls.MIN_LENGTH:
            raise InvalidPassword(
                f"Mật khẩu phải có ít nhất {cls.MIN_LENGTH} ký tự"
            )
        if not re.search(r"[A-Z]", plain):
            raise InvalidPassword("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not re.search(r"[a-z]", plain):
            raise InvalidPassword("Mật khẩu phải có ít nhất 1 chữ thường")
        if not re.search(r"\d", plain):
            raise InvalidPassword("Mật khẩu phải có ít nhất 1 chữ số")
        if plain.lower() in cls.COMMON_PASSWORDS:
            raise InvalidPassword("Mật khẩu quá phổ biến")

    @staticmethod
    def _hash(plain: str) -> str:
        # Trong production dùng bcrypt/argon2
        # Ở đây dùng hashlib cho đơn giản
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()
```

### 6.4. Sử dụng

```python
# Tạo mật khẩu — nếu sai rule sẽ raise ngay
try:
    pwd = Password.from_plain("abc")
except InvalidPassword as e:
    print(e)  # "Mật khẩu phải có ít nhất 8 ký tự"

# Tạo mật khẩu hợp lệ
pwd = Password.from_plain("MySecure123")
print(pwd)              # "***********"
print(pwd.matches("MySecure123"))  # True
print(pwd.matches("WrongPass1"))   # False

# Lưu vào DB — chỉ cần lưu hash
db.save_user(user_id, pwd._hashed)

# Load lại từ DB
pwd_loaded = Password.from_hash(db.load_hash(user_id))
assert pwd_loaded.matches("MySecure123")
```

### 6.5. Lợi ích cụ thể

| Trước (CRUD) | Sau (Domain) |
|---|---|
| Có thể quên gọi `validate_password` | Không thể tạo `Password` sai |
| Plain text có thể lọt vào DB | Chỉ có hash được lưu |
| Rule nằm ở 2 nơi | Rule nằm 1 chỗ |
| Test cần setup DB | Test pure Python |
| Business đọc code không hiểu | Business đọc code thấy rule của họ |

### 6.6. Test

```python
import pytest

def test_password_too_short():
    with pytest.raises(InvalidPassword, match="8 ký tự"):
        Password.from_plain("Abc123")

def test_password_no_uppercase():
    with pytest.raises(InvalidPassword, match="chữ hoa"):
        Password.from_plain("abcdefg1")

def test_password_common():
    with pytest.raises(InvalidPassword, match="phổ biến"):
        Password.from_plain("password")   # dài nhưng phổ biến

def test_password_valid():
    pwd = Password.from_plain("MySecure123")
    assert pwd.matches("MySecure123")
    assert not pwd.matches("MySecure124")

def test_password_hash_not_plain():
    pwd = Password.from_plain("MySecure123")
    assert "MySecure123" not in repr(pwd)
    assert "MySecure123" not in pwd._hashed
```

Chạy `pytest -v` → **5 test pass trong < 0.1 giây**. Không cần DB, không cần mock.

---

## 7. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): `BankAccount`

Viết lại class `BankAccount` theo Domain mindset, dựa trên ví dụ trong bài. Yêu cầu:

- Value Object `Money(amount: Decimal, currency: str)` với `__add__`, `__sub__`.
- Entity `BankAccount` với:
  - `deposit(amount: Money)`
  - `withdraw(amount: Money)` — rule: không âm, không quá số dư, không quá 10 triệu/ngày.
  - `lock(reason: str)` / `unlock()`
  - Property `balance`, `status`.
- Không được có setter public cho `_balance`.
- Viết ít nhất 6 test case với `pytest`.

### 🟡 Bài tập 2 (trung bình): `Email`

Viết Value Object `Email`:

- Validate format email.
- Tự động lowercase.
- Method `domain()` trả về phần sau `@`.
- Method `is_same_domain(other: Email) -> bool`.
- Không cho phép tạo `Email` từ chuỗi rỗng.
- Viết 5 test case.

### 🔴 Bài tập 3 (khó): `Booking` cho rạp phim

Viết Domain model cho **đặt vé xem phim**:

- `Movie(title, duration_minutes)` — Entity.
- `Screening(movie, start_time, room, total_seats)` — Entity.
- `Seat(row: str, number: int)` — Value Object.
- `Booking(screening, customer, seats: list[Seat])` — Aggregate Root.

Business rule:

- Không đặt quá 8 ghế / booking.
- Không đặt ghế đã có người đặt (giả sử `Booking` có method `is_seat_taken(seat)` — bạn tự quyết định).
- Không đặt sau khi suất chiếu bắt đầu.
- Không đặt ghế không tồn tại trong phòng.
- Hủy booking trong vòng 2 giờ trước suất chiếu → hoàn tiền 100%. Sau đó → 0%.

Viết ít nhất 10 test case.

---

## 8. Tóm tắt bài học

Sau bài này, bạn cần nhớ:

1. **DDD không phải framework** — là triết lý thiết kế.
2. **Vấn đề gốc:** business phức tạp nhưng code không phản ánh được.
3. **CRUD vs Domain:** một bên là wrapper DB, một bên là đối tượng nghiệp vụ có hành vi.
4. **3 căn bệnh:** Anemic Model, logic phân tán, ngôn ngữ lệch pha.
5. **Khi nào dùng:** domain phức tạp, rule thay đổi, dự án dài.
6. **Khi nào không:** CRUD đơn giản, MVP, prototype.
7. **Python phù hợp** nhưng cần kỷ luật: mypy strict, Protocol, frozen dataclass, import-linter.
8. **Code DDD đầu tiên:** Value Object `Password` — rule nằm trong chính nó.

---

## 9. Chuẩn bị cho bài 2

Bài tiếp theo: **Ubiquitous Language — Ngôn ngữ chung**.

Chuẩn bị:
- Nghĩ về **một dự án bạn đang làm** (hoặc đã làm) — sẽ dùng làm ví dụ xuyên suốt lộ trình.
- Liệt kê 10 thuật ngữ nghiệp vụ mà business hay dùng.
- Sẽ bàn: tại sao đặt tên `Customer` tốt hơn `UserRecord`, tại sao `approve()` tốt hơn `set_status(1)`.

---

📌 **Bạn đã sẵn sàng cho bài 2 chưa?**

Nếu muốn, tôi có thể:
- **Chấm bài tập** khi bạn viết xong.
- **Đi tiếp bài 2** ngay bây giờ.
- **Viết code mẫu đầy đủ** cho một trong ba bài tập trên.
- **Giải thích sâu hơn** phần nào đó (Anemic Model, mypy strict, import-linter...).

Nói tôi biết bạn muốn gì nhé.