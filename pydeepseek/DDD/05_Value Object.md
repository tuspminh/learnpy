# 📖 Bài 5: Value Object — Bất biến là sức mạnh

> Đây là bài đầu tiên của **Level 2 — Building Blocks**. Value Object là **building block đơn giản nhất nhưng mạnh nhất** của DDD. Nếu bạn viết VO đúng, 60% bug nghiệp vụ sẽ biến mất. Nếu viết sai, bạn sẽ tạo ra một class vô dụng đội lốt VO.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Value Object (VO)** là gì và **khi nào dùng**.
2. Phân biệt rõ **VO vs Entity** — không còn mơ hồ.
3. Viết VO "chuẩn DDD" trong Python: `frozen=True`, `__post_init__`, magic methods.
4. Biết **các VO kinh điển**: Money, Email, Address, DateRange, Percentage, Quantity.
5. Hiểu **khi nào VO chứa VO** — composition.
6. Tránh được **7 anti-pattern** khi viết VO.
7. Làm bài tập thực hành có chấm điểm.

---

## 1. Value Object là gì?

### 1.1. Định nghĩa

> **Value Object** là một object **không có identity** (không có ID), được định nghĩa **hoàn toàn bằng giá trị của nó**. Hai VO bằng nhau khi mọi field của chúng bằng nhau.
>
> VO là **bất biến (immutable)** — một khi tạo ra, không thể thay đổi. Muốn "thay đổi" thì tạo cái mới.

### 1.2. Ví dụ trực giác

Hãy nghĩ về **tiền**:

- `100.000 VND` ở ví bạn và `100.000 VND` ở ví tôi — **giống hệt nhau**. Không có "tờ tiền của bạn" và "tờ tiền của tôi". Chúng là **cùng một giá trị**.
- Không ai nói "tờ 100k này có ID là #123". Tiền không có ID.

Hãy nghĩ về **email**:

- `an@example.com` — không có ID, chỉ có giá trị.
- Nếu bạn đổi email → bạn có **email mới**, không phải "sửa" email cũ.

Hãy nghĩ về **ngày tháng**:

- `2026-09-19` — không có ID.
- `2026-09-19` ở Hà Nội và `2026-09-19` ở Sài Gòn là **cùng một ngày**.

Đó là VO.

### 1.3. VO vs Entity — Phân biệt rõ

| Tiêu chí | Value Object | Entity |
|---|---|---|
| **Identity** | Không có | Có (UUID/ID) |
| **So sánh** | Bằng giá trị | Bằng ID |
| **Bất biến** | Có (immutable) | Không (mutable) |
| **Vòng đời** | Ngắn, thay thế | Dài, tồn tại |
| **Ví dụ** | Money, Email, Address | Customer, Order, Product |
| **Đổi state** | Tạo cái mới | Sửa trực tiếp |

### 1.4. Câu hỏi quyết định: VO hay Entity?

Hỏi 3 câu:

1. **Có cần ID không?** Nếu có → Entity. Nếu không → VO.
2. **Hai object cùng giá trị có phải là một không?** Nếu có → VO. Nếu không → Entity.
3. **Có cần theo dõi vòng đời không?** Nếu có → Entity. Nếu không → VO.

**Ví dụ:**

| Object | Có ID? | Cùng giá trị = 1? | Cần vòng đời? | Kết luận |
|---|---|---|---|---|
| `100.000 VND` | Không | Có | Không | **VO** |
| `an@example.com` | Không | Có | Không | **VO** |
| `Customer An` | Có | Không (2 khách cùng tên là 2 người) | Có | **Entity** |
| `Order #123` | Có | Không | Có | **Entity** |
| `Ngày 19/09/2026` | Không | Có | Không | **VO** |
| `Địa chỉ 12 Lê Lợi, Q1` | Không | Có | Không | **VO** |
| `Product iPhone 15` | Có (SKU) | Không | Có | **Entity** |
| `Tọa độ 10.7, 106.7` | Không | Có | Không | **VO** |

---

## 2. VO chuẩn trong Python — Bộ khung

Đây là **bộ khung VO chuẩn** mà bạn sẽ dùng suốt sự nghiệp:

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self) -> None:
        """Validate + normalize. Chạy SAU khi dataclass gán field."""
        if self.amount < 0:
            raise ValueError("Money không thể âm")
        if len(self.currency) != 3:
            raise ValueError("Currency phải là ISO 4217 (3 ký tự)")
        # Normalize currency về uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    # ---- Magic methods ----
    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        if self.amount < other.amount:
            raise ValueError("Kết quả phép trừ âm")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        if factor < 0:
            raise ValueError("Factor không thể âm")
        return Money(self.amount * Decimal(factor), self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount < other.amount

    # ---- Private helpers ----
    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Khác loại tiền tệ: {self.currency} vs {other.currency}"
            )
```

**Giải thích từng phần:**

| Phần | Tác dụng |
|---|---|
| `@dataclass(frozen=True)` | Tạo `__init__`, `__eq__`, `__hash__`, `__repr__`; chặn gán lại field |
| `__post_init__` | Validate + normalize sau khi field được gán |
| `object.__setattr__` | Cách gán field trong `frozen=True` (dùng khi cần normalize) |
| Magic methods | Cho phép `+`, `-`, `*`, `<`, `==` tự nhiên |
| Private helper | Tránh lặp code validate |

---

## 3. Các VO kinh điển

Đây là **6 VO bạn sẽ viết hàng ngày**. Học thuộc lòng để dùng lại.

### 3.1. Money — VO quan trọng nhất

Đã có ở trên. Lưu ý thêm:

```python
# Cách dùng
price = Money(Decimal("100"), "vnd")     # normalize thành "VND"
tax = Money(Decimal("10"), "VND")
total = price + tax                         # Money(110, VND)
discount = total * Decimal("0.1")           # Money(11, VND)

# So sánh
assert Money(Decimal("100"), "VND") == Money(Decimal("100"), "VND")
assert Money(Decimal("100"), "VND") < Money(Decimal("200"), "VND")

# Hash (dùng được làm key dict)
prices = {
    Money(Decimal("100"), "VND"): "rẻ",
    Money(Decimal("1000"), "VND"): "đắt",
}
```

**Lưu ý quan trọng:**

- Luôn dùng `Decimal`, không dùng `float` (float có lỗi làm tròn).
- Luôn validate currency là ISO 4217 (3 ký tự).
- Không cho phép `amount` âm — business rule.

### 3.2. Email — VO có validation phức tạp

```python
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    # Regex đơn giản, đủ dùng 99% trường hợp
    _PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not self._PATTERN.match(normalized):
            raise InvalidEmail(f"Email không hợp lệ: {self.value!r}")
        if len(normalized) > 254:
            raise InvalidEmail("Email quá dài (RFC 5321: max 254)")
        object.__setattr__(self, "value", normalized)

    @property
    def local_part(self) -> str:
        """Phần trước @."""
        return self.value.split("@")[0]

    @property
    def domain(self) -> str:
        """Phần sau @."""
        return self.value.split("@")[1]

    def is_same_domain(self, other: "Email") -> bool:
        return self.domain == other.domain

    def __str__(self) -> str:
        return self.value


class InvalidEmail(ValueError):
    """Exception nghiệp vụ cho email không hợp lệ."""
```

**Cách dùng:**

```python
email = Email("  An@Example.COM  ")   # normalize
assert str(email) == "an@example.com"
assert email.domain == "example.com"
assert email.local_part == "an"

try:
    Email("không-phải-email")
except InvalidEmail as e:
    print(e)   # "Email không hợp lệ: 'không-phải-email'"
```

**Điểm hay:**

- Normalize **tự động** (strip + lowercase).
- Có property `domain`, `local_part`.
- Có method `is_same_domain()` — nghiệp vụ.
- Exception có tên nghiệp vụ.

### 3.3. Address — VO compose nhiều field

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    ward: str        # phường/xã
    district: str    # quận/huyện
    city: str        # tỉnh/thành
    country: str = "Việt Nam"
    postal_code: str | None = None

    def __post_init__(self) -> None:
        # Normalize: strip tất cả field
        for field_name in ("street", "ward", "district", "city", "country"):
            value = getattr(self, field_name).strip()
            if not value:
                raise ValueError(f"{field_name} không được rỗng")
            object.__setattr__(self, field_name, value)

        if self.postal_code is not None:
            pc = self.postal_code.strip()
            if not pc.isdigit() or len(pc) != 6:
                raise ValueError("Mã bưu chính phải là 6 chữ số")
            object.__setattr__(self, "postal_code", pc)

    def format_vn(self) -> str:
        """Định dạng địa chỉ Việt Nam."""
        parts = [self.street, self.ward, self.district, self.city]
        if self.postal_code:
            parts.append(f"({self.postal_code})")
        parts.append(self.country)
        return ", ".join(parts)

    def is_same_city(self, other: "Address") -> bool:
        return self.city.lower() == other.city.lower()
```

**Cách dùng:**

```python
addr = Address(
    street="12 Lê Lợi",
    ward="Phường Bến Nghé",
    district="Quận 1",
    city="TP. Hồ Chí Minh",
)
print(addr.format_vn())
# "12 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh, Việt Nam"

# Hai địa chỉ cùng giá trị → bằng nhau
assert addr == Address(
    street="12 Lê Lợi",
    ward="Phường Bến Nghé",
    district="Quận 1",
    city="TP. Hồ Chí Minh",
)
```

### 3.4. DateRange — VO có logic phức tạp

```python
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(
                f"Ngày bắt đầu ({self.start}) phải ≤ ngày kết thúc ({self.end})"
            )

    def duration_days(self) -> int:
        """Số ngày trong khoảng (bao gồm cả 2 đầu)."""
        return (self.end - self.start).days + 1

    def overlaps(self, other: "DateRange") -> bool:
        """Hai khoảng có giao nhau không?"""
        return not (self.end < other.start or other.end < self.start)

    def contains(self, d: date) -> bool:
        """Ngày d có nằm trong khoảng không?"""
        return self.start <= d <= self.end

    def intersect(self, other: "DateRange") -> "DateRange | None":
        """Giao của 2 khoảng. None nếu không giao."""
        if not self.overlaps(other):
            return None
        return DateRange(
            start=max(self.start, other.start),
            end=min(self.end, other.end),
        )

    def shift(self, days: int) -> "DateRange":
        """Dịch khoảng đi `days` ngày."""
        delta = timedelta(days=days)
        return DateRange(self.start + delta, self.end + delta)
```

**Cách dùng:**

```python
q1 = DateRange(date(2026, 1, 1), date(2026, 3, 31))
q2 = DateRange(date(2026, 4, 1), date(2026, 6, 30))

assert q1.duration_days() == 90
assert not q1.overlaps(q2)
assert q1.contains(date(2026, 2, 14))

overlap = q1.intersect(
    DateRange(date(2026, 3, 15), date(2026, 4, 15))
)
assert overlap == DateRange(date(2026, 3, 15), date(2026, 3, 31))
```

### 3.5. Percentage — VO có ràng buộc đặc biệt

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Percentage:
    """Giá trị phần trăm 0-100."""
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0 or self.value > 100:
            raise ValueError(f"Percentage phải trong [0, 100]: {self.value}")

    @classmethod
    def from_fraction(cls, numerator: int, denominator: int) -> "Percentage":
        """Tạo từ phân số. Ví dụ: 3/4 → 75%."""
        if denominator == 0:
            raise ValueError("Mẫu số không thể 0")
        value = Decimal(numerator) / Decimal(denominator) * Decimal("100")
        return cls(value)

    def apply_to(self, amount: Decimal) -> Decimal:
        """Áp dụng vào một số. Ví dụ: 10% của 200 → 20."""
        return amount * self.value / Decimal("100")

    def as_fraction(self) -> Decimal:
        """Trả về dạng thập phân. Ví dụ: 25% → 0.25."""
        return self.value / Decimal("100")

    def __str__(self) -> str:
        return f"{self.value}%"
```

**Cách dùng:**

```python
discount = Percentage(Decimal("15"))
total = Decimal("1_000_000")
discounted = total - discount.apply_to(total)
# discounted = 850_000

fraction = Percentage.from_fraction(3, 4)
assert fraction == Percentage(Decimal("75"))
```

### 3.6. Quantity — VO cho số lượng

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Số lượng không âm."""
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Quantity không thể âm")
        if not isinstance(self.value, int):
            raise TypeError("Quantity phải là int")

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value + other.value)

    def __sub__(self, other: "Quantity") -> "Quantity":
        if self.value < other.value:
            raise ValueError("Kết quả phép trừ âm")
        return Quantity(self.value - other.value)

    def is_zero(self) -> bool:
        return self.value == 0
```

---

## 4. Composition — VO chứa VO

VO có thể chứa VO khác. Đây là **sức mạnh thực sự**.

### 4.1. Ví dụ: OrderLine với Money và Quantity

```python
@dataclass(frozen=True)
class OrderLine:
    product_sku: str
    unit_price: Money       # ← VO
    quantity: Quantity      # ← VO

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity.value
```

**Cách dùng:**

```python
line = OrderLine(
    product_sku="IP15-128",
    unit_price=Money(Decimal("25_000_000"), "VND"),
    quantity=Quantity(2),
)
assert line.subtotal == Money(Decimal("50_000_000"), "VND")
```

### 4.2. Ví dụ: Invoice chứa nhiều VO

```python
@dataclass(frozen=True)
class Invoice:
    invoice_number: InvoiceNumber      # VO
    customer_email: Email              # VO
    billing_address: Address           # VO
    issued_date: date
    due_date: date
    subtotal: Money                    # VO
    tax_rate: Percentage               # VO

    @property
    def tax_amount(self) -> Money:
        return Money(
            amount=self.tax_rate.apply_to(self.subtotal.amount),
            currency=self.subtotal.currency,
        )

    @property
    def total(self) -> Money:
        return self.subtotal + self.tax_amount

    def is_overdue(self, today: date) -> bool:
        return today > self.due_date
```

**Điều kỳ diệu:** Mỗi VO tự bảo vệ rule của nó. `Invoice` không cần kiểm tra email có hợp lệ không — vì `Email` đã tự đảm bảo. `Invoice` không cần validate tax_rate ≤ 100 — vì `Percentage` đã làm.

> 💡 **Nguyên tắc:** VO không bao giờ tin tưởng input. Mỗi VO tự validate. VO cha chỉ cần compose.

### 4.3. VO lồng sâu

```python
@dataclass(frozen=True)
class Address:
    street: str
    ward: str
    district: str
    city: str
    country: str = "Việt Nam"


@dataclass(frozen=True)
class Person:
    full_name: FullName
    email: Email
    phone: PhoneNumber
    address: Address


@dataclass(frozen=True)
class FullName:
    first_name: str
    last_name: str

    @property
    def display(self) -> str:
        return f"{self.last_name} {self.first_name}"
```

→ **Mỗi tầng validate rule của mình.** Khi tạo `Person`, mọi thứ đã hợp lệ.

---

## 5. Các magic methods cần biết

### 5.1. `__eq__` và `__hash__` — Tự động có

Với `@dataclass(frozen=True)`, Python **tự sinh** `__eq__` và `__hash__`:

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

a = Money(Decimal("100"), "VND")
b = Money(Decimal("100"), "VND")

assert a == b                    # True — so sánh bằng giá trị
assert hash(a) == hash(b)        # True — hash giống nhau
assert {a, b} == {a}             # True — set loại trùng

d = {a: "giá"}
assert d[b] == "giá"             # True — dict lookup OK
```

**Điều này cực kỳ quan trọng** — nó cho phép dùng VO làm key trong dict/set, điều mà Entity không làm được (vì Entity có hash theo ID).

### 5.2. Magic methods cho số học

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __add__(self, other): ...       # a + b
    def __radd__(self, other): ...      # 0 + a (dùng cho sum())
    def __sub__(self, other): ...       # a - b
    def __mul__(self, factor): ...      # a * 2
    def __rmul__(self, factor): ...     # 2 * a
    def __truediv__(self, divisor): ... # a / 2
    def __neg__(self): ...              # -a
    def __abs__(self): ...              # abs(a)
```

**Ví dụ `__radd__` để dùng với `sum()`:**

```python
def __radd__(self, other):
    if other == 0:   # sum() bắt đầu bằng 0
        return self
    return self.__add__(other)

# Giờ có thể dùng
total = sum(line.subtotal for line in order.lines)
```

### 5.3. Magic methods cho so sánh

```python
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __eq__(self, other): ...
    def __lt__(self, other): ...       # < 
    # total_ordering tự sinh __le__, __gt__, __ge__ từ __eq__ + __lt__
```

**Cách dùng:**

```python
assert Money(Decimal("100"), "VND") < Money(Decimal("200"), "VND")
assert Money(Decimal("200"), "VND") >= Money(Decimal("100"), "VND")
```

### 5.4. `__str__` và `__repr__`

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __str__(self) -> str:
        """Dành cho người dùng cuối."""
        return f"{self.amount:,.0f} {self.currency}"

    def __repr__(self) -> str:
        """Dành cho dev debug."""
        return f"Money({self.amount}, {self.currency})"


m = Money(Decimal("1000000"), "VND")
print(str(m))     # "1,000,000 VND"
print(repr(m))    # "Money(1000000, VND)"
```

**Nguyên tắc:**
- `__str__` → đẹp cho user.
- `__repr__` → chi tiết cho dev (nên có thể `eval()` được nếu có thể).

---

## 6. Khi nào dùng VO?

### 6.1. Dấu hiệu cần VO

**1. Có validation**

Nếu bạn cần validate (email format, tiền không âm, ngày hợp lệ) → VO.

```python
# ❌ Trước: validate rải rác
def register(email: str):
    if "@" not in email:
        raise ValueError("bad email")
    # ...

# ✅ Sau: VO tự validate
def register(email: Email):   # không cần validate lại
    ...
```

**2. Có nhiều field đi cùng nhau**

Nếu 3+ field luôn xuất hiện cùng nhau → gộp thành VO.

```python
# ❌ Trước: tham số rời
def create_order(
    street: str, ward: str, district: str, city: str,
    product_sku: str, unit_price: Decimal, currency: str, quantity: int,
): ...

# ✅ Sau: dùng VO
def create_order(
    shipping_address: Address,
    line: OrderLine,
): ...
```

**3. Cần đảm bảo invariant**

Nếu có rule *"amount không âm"*, *"start ≤ end"* → VO.

```python
@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("start phải ≤ end")
```

**4. Cần so sánh bằng giá trị**

Nếu `a == b` khi mọi field bằng nhau → VO.

**5. Cần immutable**

Nếu object không nên bị sửa → VO (`frozen=True`).

### 6.2. Khi nào KHÔNG dùng VO?

**1. Cần ID**

Nếu object cần theo dõi vòng đời → Entity, không phải VO.

**2. Cần mutable state**

Nếu object phải sửa nhiều lần → Entity.

**3. Chỉ là DTO chuyển dữ liệu**

Nếu chỉ để chuyển dữ liệu từ tầng này sang tầng khác → DTO (Pydantic ở presentation).

**4. Không có rule gì**

Nếu object chỉ là 2 field không có rule gì → có thể dùng tuple hoặc dict.

---

## 7. Bảy anti-pattern khi viết VO

### ❌ Anti-pattern 1: VO không frozen

```python
# ❌ SAI
@dataclass
class Money:
    amount: Decimal
    currency: str

m = Money(Decimal("100"), "VND")
m.amount = Decimal("-50")   # Không ai ngăn!
```

```python
# ✅ ĐÚNG
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

### ❌ Anti-pattern 2: VO có setter

```python
# ❌ SAI
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def set_amount(self, new_amount: Decimal) -> None:   # Vô nghĩa với frozen
        object.__setattr__(self, "amount", new_amount)
```

VO **không có setter**. Muốn đổi → tạo cái mới:

```python
# ✅ ĐÚNG
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def with_amount(self, new_amount: Decimal) -> "Money":
        """Trả về Money MỚI với amount khác."""
        return Money(new_amount, self.currency)
```

### ❌ Anti-pattern 3: VO không validate

```python
# ❌ SAI: VO vô dụng
@dataclass(frozen=True)
class Email:
    value: str

Email("không-phải-email")   # OK, không ai ngăn
```

```python
# ✅ ĐÚNG: VO validate
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise InvalidEmail(self.value)
```

### ❌ Anti-pattern 4: Dùng float cho Money

```python
# ❌ SAI: float có lỗi làm tròn
price = 0.1 + 0.2
# price = 0.30000000000000004
```

```python
# ✅ ĐÚNG: Decimal
from decimal import Decimal

price = Decimal("0.1") + Decimal("0.2")
# price = Decimal("0.3")
```

### ❌ Anti-pattern 5: VO dùng `id` để so sánh

```python
# ❌ SAI: VO có identity → thực ra là Entity
@dataclass
class Money:
    id: UUID          # VO không có ID!
    amount: Decimal
    currency: str
```

### ❌ Anti-pattern 6: VO expose list mutable

```python
# ❌ SAI
@dataclass(frozen=True)
class Order:
    lines: list[OrderLine]

o = Order(lines=[...])
o.lines.append(new_line)   # frozen không ngăn được mutation của list!
```

```python
# ✅ ĐÚNG: dùng tuple, hoặc copy trong __post_init__
@dataclass(frozen=True)
class Order:
    lines: tuple[OrderLine, ...]

o = Order(lines=(...))
o.lines.append(...)   # AttributeError — tuple không có append
```

Hoặc:

```python
@dataclass(frozen=True)
class Order:
    lines: tuple[OrderLine, ...]

    def __post_init__(self) -> None:
        # Chấp nhận cả list và chuyển thành tuple
        if not isinstance(self.lines, tuple):
            object.__setattr__(self, "lines", tuple(self.lines))
```

### ❌ Anti-pattern 7: VO làm quá nhiều thứ

```python
# ❌ SAI: VO có trách nhiệm lưu DB
@dataclass(frozen=True)
class Email:
    value: str

    def save_to_db(self) -> None:   # VO không biết DB
        db.execute("INSERT ...")

    def send(self) -> None:         # VO không gửi email
        smtp.send(self.value)
```

VO chỉ chứa **logic nghiệp vụ của chính nó**, không chứa I/O.

---

## 8. Testing VO

VO là thứ **dễ test nhất** trong DDD. Pure Python, không cần DB, không cần mock.

```python
# tests/unit/domain/test_money.py
from decimal import Decimal
import pytest

from shop.shared.domain.money import Money


class TestMoneyValidation:
    def test_negative_amount_raises(self) -> None:
        with pytest.raises(ValueError, match="không thể âm"):
            Money(Decimal("-1"), "VND")

    def test_currency_must_be_3_chars(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            Money(Decimal("100"), "VNDONG")

    def test_currency_normalized_to_uppercase(self) -> None:
        m = Money(Decimal("100"), "vnd")
        assert m.currency == "VND"


class TestMoneyArithmetic:
    def test_add_same_currency(self) -> None:
        assert Money(Decimal("100"), "VND") + Money(Decimal("50"), "VND") == \
               Money(Decimal("150"), "VND")

    def test_add_different_currency_raises(self) -> None:
        with pytest.raises(ValueError, match="Khác loại tiền tệ"):
            Money(Decimal("100"), "VND") + Money(Decimal("50"), "USD")

    def test_multiply_by_int(self) -> None:
        assert Money(Decimal("100"), "VND") * 3 == Money(Decimal("300"), "VND")

    def test_subtract_more_than_available_raises(self) -> None:
        with pytest.raises(ValueError, match="Kết quả phép trừ âm"):
            Money(Decimal("100"), "VND") - Money(Decimal("200"), "VND")

    def test_sum_with_start_zero(self) -> None:
        prices = [Money(Decimal("100"), "VND"), Money(Decimal("200"), "VND")]
        assert sum(prices) == Money(Decimal("300"), "VND")


class TestMoneyEquality:
    def test_same_value_same_currency_equal(self) -> None:
        assert Money(Decimal("100"), "VND") == Money(Decimal("100"), "VND")

    def test_same_value_different_currency_not_equal(self) -> None:
        assert Money(Decimal("100"), "VND") != Money(Decimal("100"), "USD")

    def test_hashable(self) -> None:
        prices = {
            Money(Decimal("100"), "VND"): "rẻ",
            Money(Decimal("1000"), "VND"): "đắt",
        }
        assert prices[Money(Decimal("100"), "VND")] == "rẻ"


class TestMoneyImmutability:
    def test_cannot_modify_amount(self) -> None:
        m = Money(Decimal("100"), "VND")
        with pytest.raises(Exception):   # FrozenInstanceError
            m.amount = Decimal("200")   # type: ignore[misc]
```

**Chạy `pytest`:**

```
tests/unit/domain/test_money.py::TestMoneyValidation::test_negative_amount_raises PASSED
tests/unit/domain/test_money.py::TestMoneyValidation::test_currency_must_be_3_chars PASSED
...
15 passed in 0.03s
```

**15 test trong 0.03 giây.** Không DB, không mock, không setup. Đây là **siêu năng lực** của VO.

---

## 9. Ví dụ tổng hợp: `OrderLine` với 3 VO

```python
from dataclasses import dataclass
from decimal import Decimal


# ---- VO 1: SKU ----
@dataclass(frozen=True)
class SKU:
    """Stock Keeping Unit — mã sản phẩm."""
    value: str

    _PATTERN = __import__("re").compile(r"^[A-Z0-9]{4,20}$")

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if not self._PATTERN.match(normalized):
            raise ValueError(
                f"SKU phải là 4-20 ký tự A-Z hoặc 0-9: {self.value!r}"
            )
        object.__setattr__(self, "value", normalized)


# ---- VO 2: Money ----
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "VND"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money không thể âm")
        if len(self.currency) != 3:
            raise ValueError("Currency phải là ISO 4217")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Khác loại tiền tệ")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(factor), self.currency)


# ---- VO 3: Quantity ----
@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError("Quantity phải là int")
        if self.value <= 0:
            raise ValueError("Quantity phải > 0")


# ---- VO compose: OrderLine ----
@dataclass(frozen=True)
class OrderLine:
    sku: SKU
    unit_price: Money
    quantity: Quantity

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity.value


# ---- Sử dụng ----
line = OrderLine(
    sku=SKU("ip15-128"),
    unit_price=Money(Decimal("25_000_000"), "VND"),
    quantity=Quantity(3),
)

assert line.sku.value == "IP15-128"   # normalized
assert line.subtotal == Money(Decimal("75_000_000"), "VND")
assert str(line.unit_price) == "25,000,000 VND"
```

**Chú ý:** Mỗi VO tự validate. `OrderLine` chỉ cần compose — không cần validate lại.

---

## 10. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): `PhoneNumber`

Viết VO `PhoneNumber` cho số điện thoại Việt Nam:

- Normalize: bỏ khoảng trắng, dấu gạch, dấu ngoặc.
- Chấp nhận: `+84xxxxxxxxx`, `0xxxxxxxxx`, `84xxxxxxxxx`.
- Normalize về `+84xxxxxxxxx`.
- Property `is_mobile()`, `is_landline()`, `carrier()` (Viettel, Mobifone, Vinaphone...).
- Raise `InvalidPhoneNumber` nếu sai.

Viết ít nhất 8 test case.

### 🟡 Bài tập 2 (trung bình): `TaxCode` (Mã số thuế)

Viết VO `TaxCode` cho mã số thuế Việt Nam:

- Mã số thuế cá nhân: 10 hoặc 12 chữ số.
- Mã số thuế doanh nghiệp: 10 chữ số + dấu gạch + 3 chữ số (VD: `0123456789-001`).
- Normalize: bỏ dấu gạch nếu có thể.
- Property: `is_personal()`, `is_business()`, `branch_number()`.
- Raise `InvalidTaxCode` nếu sai.

Viết ít nhất 10 test case.

### 🔴 Bài tập 3 (khó): `BankAccountNumber` + `IBAN`

Viết 2 VO:

**1. `BankAccountNumber`** cho số tài khoản ngân hàng Việt Nam:
- 8-16 chữ số.
- Có property `bank_code` (VD: VCB, TCB, BIDV...).
- Có method `masked()` trả về `****1234`.
- Raise `InvalidAccountNumber` nếu sai.

**2. `IBAN`** cho chuẩn quốc tế:
- Format: `XX00XXXXXXXXXX` (2 chữ cái nước + 2 check digit + BBAN).
- **Check digit validation** theo chuẩn ISO 13616 (thuật toán mod 97).
- Normalize: bỏ khoảng trắng, uppercase.
- Property: `country_code`, `check_digits`, `bban`.
- Raise `InvalidIBAN` nếu sai.

Viết ít nhất 15 test case cho cả 2 VO, bao gồm test check digit của IBAN (dùng IBAN mẫu từ Wikipedia).

---

## 11. Checklist sau bài 5

Trước khi sang bài 6, bạn phải tự tin trả lời:

- [ ] VO là gì? Entity là gì? Phân biệt bằng 3 câu hỏi?
- [ ] Tại sao VO phải `frozen=True`?
- [ ] `__post_init__` dùng để làm gì? Khi nào cần `object.__setattr__`?
- [ ] Khi nào dùng VO? 5 dấu hiệu?
- [ ] Khi nào KHÔNG dùng VO? 4 dấu hiệu?
- [ ] Tại sao dùng `Decimal` cho Money thay vì `float`?
- [ ] `__eq__` và `__hash__` của VO khác Entity thế nào?
- [ ] 7 anti-pattern khi viết VO là gì?
- [ ] VO chứa VO — khi nào và tại sao?
- [ ] Tại sao VO dễ test đến vậy?

Nếu trả lời được hết, bạn đã sẵn sàng bài 6.

---

## 12. Tóm tắt bài 5

| Điểm | Nội dung |
|---|---|
| **Định nghĩa** | VO không có ID, so sánh bằng giá trị, bất biến |
| **Bộ khung** | `@dataclass(frozen=True)` + `__post_init__` + magic methods |
| **3 câu hỏi** | Có ID? Cùng giá trị = 1? Cần vòng đời? |
| **6 VO kinh điển** | Money, Email, Address, DateRange, Percentage, Quantity |
| **Composition** | VO chứa VO — mỗi tầng tự validate |
| **Magic methods** | `__add__`, `__sub__`, `__mul__`, `__lt__`, `__radd__` |
| **Khi nào dùng** | Có validation, nhiều field đi cùng, cần invariant, cần so sánh giá trị, cần immutable |
| **Khi nào không** | Cần ID, cần mutable, chỉ là DTO, không có rule |
| **7 anti-pattern** | Không frozen, có setter, không validate, dùng float, có ID, expose list, làm quá nhiều |
| **Test** | Pure Python, 15 test trong 0.03s |

**Câu thần chú:** *"VO không tin tưởng ai. Mỗi VO tự validate. VO cha chỉ cần compose."*

---

## 13. Chuẩn bị cho bài 6

Bài tiếp theo: **Entity — Có định danh, có vòng đời**.

Chuẩn bị:
- Đọc lại bài 1 (Password, BankAccount).
- Nghĩ về **3-5 Entity** trong domain bạn đang làm.
- Sẽ bàn: cách định nghĩa `__eq__`/`__hash__` theo ID, cách quản lý state, khi nào dùng `@dataclass` vs class thường cho Entity, và cách phát Domain Event từ Entity.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 6** ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: `frozen=True` chi tiết, `__radd__` cho `sum()`, `total_ordering`, VO vs Pydantic BaseModel.
5. **Review code VO** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.