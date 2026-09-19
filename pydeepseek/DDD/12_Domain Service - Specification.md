# 📖 Bài 12: Domain Service & Specification

> Bài 11 dạy bạn **Application Service** — điều phối use case. Bài 12 dạy bạn **Domain Service** — nơi đặt logic nghiệp vụ **không thuộc về một Entity/VO nào**. Và **Specification** — pattern giúp **compose business rule** một cách linh hoạt. Đây là 2 công cụ giúp bạn tránh nhét mọi thứ vào Entity, đồng thời giữ được sự rõ ràng của mô hình.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Domain Service** là gì và **không là gì**.
2. Phân biệt **Domain Service** vs **Application Service**.
3. Biết **5 dấu hiệu** cần Domain Service.
4. Biết **khi nào KHÔNG** dùng Domain Service (đừng lạm dụng).
5. Hiểu **Specification pattern** và khi nào dùng.
6. Viết **Specification** có thể compose (`and`, `or`, `not`).
7. Kết hợp **Specification với Repository** để filter.
8. Tránh được **8 anti-pattern** khi dùng Domain Service và Specification.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Domain Service là gì?

### 1.1. Định nghĩa

> **Domain Service** là một **stateless** object chứa **logic nghiệp vụ** không thuộc về một Entity hay Value Object nào. Nó là một phần của **Domain Layer** — không phụ thuộc Infrastructure, không phụ thuộc Application.

### 1.2. Trực giác

Hãy nghĩ về **chuyển tiền**:

- Logic "trừ tiền tài khoản A" thuộc về `Account A` → **method của A**.
- Logic "cộng tiền tài khoản B" thuộc về `Account B` → **method của B**.
- Nhưng logic "**chuyển tiền từ A sang B**" **không thuộc về A, cũng không thuộc về B**. Nó liên quan đến **cả hai**.

→ Đây là chỗ cần **Domain Service**.

Hãy nghĩ về **tính thuế**:

- Logic "tính thuế cho một sản phẩm" có thể thuộc Product.
- Nhưng "tính thuế cho một đơn hàng dựa trên loại khách hàng và khu vực" liên quan đến **Order + Customer + Address + TaxRule**.

→ Đây cũng là chỗ cần **Domain Service**.

### 1.3. Đặc điểm của Domain Service

| Đặc điểm | Ý nghĩa |
|---|---|
| **Stateless** | Không giữ state giữa các lần gọi |
| **Domain Layer** | Không import Infrastructure |
| **Nghiệp vụ thuần** | Không I/O, không DB trực tiếp |
| **Có thể inject Repository** | Qua interface (Protocol) |
| **Có tên nghiệp vụ** | `TransferService`, `PricingService`, `TaxCalculator` |

### 1.4. Domain Service **không** là gì?

| Không là | Lý do |
|---|---|
| **Application Service** | Application điều phối; Domain chứa rule |
| **Utility class** | Không phải `StringUtils`, `DateUtils` |
| **Repository** | Repository là persistence |
| **Factory** | Factory tạo object; Service xử lý logic |
| **Manager** | "Manager" mơ hồ, không phải tên nghiệp vụ |

---

## 2. Domain Service vs Application Service

Đây là **phần quan trọng nhất** của bài. Nhiều dev nhầm lẫn 2 khái niệm này.

### 2.1. Bảng so sánh

| Tiêu chí | Domain Service | Application Service |
|---|---|---|
| **Tầng** | Domain | Application |
| **Trách nhiệm** | Business rule | Orchestration |
| **State** | Stateless | Stateless |
| **Transaction** | Không quản lý | Quản lý UoW |
| **I/O** | Không (chỉ qua Port) | Có thể (qua Port) |
| **Phát event** | Không (Aggregate phát) | Có (qua UoW) |
| **Ai gọi** | Application Service | Presentation |
| **Ví dụ** | `TransferService`, `PricingService` | `PlaceOrderHandler`, `CancelOrderHandler` |
| **Số lượng** | Ít (1-5) | Nhiều (mỗi use case 1) |
| **Test** | Pure Python | Có thể cần UoW fake |

### 2.2. Ví dụ minh họa

**Business rule:** "Chuyển tiền từ A sang B, kiểm tra hạn mức, phí giao dịch, ghi log."

**Cách 1: SAI — nhét tất cả vào Application Service**

```python
# ❌ SAI: Business rule ở Application
class TransferHandler:
    def __init__(self, uow, fee_calculator):
        self._uow = uow
        self._fee_calculator = fee_calculator

    def handle(self, cmd: TransferCommand) -> None:
        with self._uow:
            source = self._uow.accounts.find_by_id(cmd.from_id)
            target = self._uow.accounts.find_by_id(cmd.to_id)

            # ❌ Business rule ở Application!
            if source.balance.amount < cmd.amount.amount:
                raise InsufficientFunds()
            if cmd.amount.amount > 100_000_000:
                raise DailyLimitExceeded()
            fee = self._fee_calculator.calculate(cmd.amount)
            if source.balance.amount < cmd.amount.amount + fee.amount:
                raise InsufficientFundsIncludingFee()

            source.withdraw(cmd.amount)
            source.withdraw(fee)
            target.deposit(cmd.amount)

            self._uow.accounts.save(source)
            self._uow.accounts.save(target)
            self._uow.commit()
```

**Vấn đề:**

- Rule "hạn mức 100 triệu" ở Application → không test được pure.
- Rule "phí giao dịch" ở Application → không tái sử dụng.
- Khó enforce nếu có use case khác cũng chuyển tiền.

**Cách 2: ĐÚNG — dùng Domain Service**

```python
# ✅ ĐÚNG: Business rule ở Domain Service
class TransferService:
    """Domain Service — stateless, không biết DB."""

    MAX_AMOUNT = Money(Decimal("100000000"), "VND")

    def __init__(self, fee_calculator: FeeCalculator) -> None:
        self._fee_calculator = fee_calculator

    def transfer(
        self,
        source: BankAccount,
        target: BankAccount,
        amount: Money,
    ) -> TransferResult:
        # Validate
        if amount.amount <= 0:
            raise InvalidAmount(amount)
        if amount.amount > self.MAX_AMOUNT.amount:
            raise DailyLimitExceeded(amount, self.MAX_AMOUNT)

        # Tính phí
        fee = self._fee_calculator.calculate(amount)
        total_needed = amount + fee

        # Gọi business method của từng Account
        source.withdraw(total_needed)
        target.deposit(amount)

        return TransferResult(
            amount=amount,
            fee=fee,
            occurred_at=datetime.now(),
        )
```

**Application Service mỏng:**

```python
class TransferHandler:
    def __init__(self, uow: UnitOfWork, transfer_service: TransferService) -> None:
        self._uow = uow
        self._transfer_service = transfer_service

    def handle(self, cmd: TransferCommand) -> TransferResult:
        with self._uow:
            source = self._uow.accounts.find_by_id(cmd.from_id)
            target = self._uow.accounts.find_by_id(cmd.to_id)

            if not source or not target:
                raise AccountNotFound()

            result = self._transfer_service.transfer(source, target, cmd.amount)

            self._uow.accounts.save(source)
            self._uow.accounts.save(target)
            self._uow.commit()

        return result
```

**Lợi ích:**

- Rule "hạn mức", "phí" nằm ở Domain Service → test pure.
- Application Service mỏng → dễ đọc.
- Tái sử dụng: use case `BulkTransfer`, `ScheduledTransfer` cũng dùng `TransferService`.

---

## 3. Khi nào cần Domain Service?

### 3.1. Năm dấu hiệu

**1. Logic liên quan đến nhiều Aggregate**

```python
# TransferService — liên quan Account A và Account B
# PricingService — liên quan Order và Customer
# ReservationService — liên quan Book và Member
```

**2. Logic không tự nhiên thuộc về Entity nào**

Nếu bạn thấy mình đang viết:

```python
class Order:
    def calculate_tax_considering_customer_location_and_tax_rules(
        self, customer, tax_rules
    ) -> Money:
        ...
```

→ Tên method đã "kêu cứu". Đây là Domain Service.

**3. Cần tính toán phức tạp, không phụ thuộc state**

```python
class PricingService:
    def calculate_price(
        self,
        product: Product,
        customer: Customer,
        quantity: int,
        promo_code: str | None,
    ) -> Money:
        # Base price
        base = product.price * Decimal(quantity)

        # Customer discount
        if customer.is_vip():
            base = base * Decimal("0.9")

        # Volume discount
        if quantity >= 100:
            base = base * Decimal("0.95")

        # Promo code
        if promo_code:
            base = self._apply_promo(base, promo_code)

        return base
```

**4. Cần algorithm thuần túy**

```python
class TaxCalculator:
    def calculate(self, income: Money, region: str) -> Money:
        # Bảng thuế theo vùng
        ...
```

**5. Logic có thể tái sử dụng ở nhiều use case**

Nếu 2 use case dùng cùng logic → đưa vào Domain Service.

### 3.2. Khi nào KHÔNG dùng Domain Service?

Đây là **cảnh báo quan trọng**. Domain Service **dễ bị lạm dụng**.

**1. Khi logic thuộc về 1 Entity**

```python
# ❌ SAI: Đưa vào Service dù thuộc về Account
class AccountService:
    def withdraw(self, account: BankAccount, amount: Money) -> None:
        if account.balance.amount < amount.amount:
            raise InsufficientFunds()
        account.balance -= amount.amount
```

```python
# ✅ ĐÚNG: Đây là method của Account
class BankAccount:
    def withdraw(self, amount: Money) -> None:
        if self._balance.amount < amount.amount:
            raise InsufficientFunds()
        self._balance = self._balance - amount
```

**2. Khi chỉ là utility**

```python
# ❌ SAI: Đây là utility, không phải Domain Service
class StringService:
    def capitalize(self, s: str) -> str:
        return s.capitalize()
```

**3. Khi chỉ wrap Repository**

```python
# ❌ SAI: Chỉ wrap repo, không có logic
class CustomerService:
    def __init__(self, repo):
        self._repo = repo

    def find_customer(self, customer_id):
        return self._repo.find_by_id(customer_id)
```

**4. Khi logic chỉ dùng 1 lần**

Nếu chỉ có 1 use case dùng → đặt vào Entity hoặc Application Service.

### 3.3. Quy tắc ngón tay

> **Nếu bạn do dự giữa Entity method và Domain Service, hãy thử đặt vào Entity trước.** Chỉ tách ra Service khi thực sự cần (liên quan nhiều Aggregate, hoặc không tự nhiên thuộc về Entity nào).

---

## 4. Ví dụ Domain Service kinh điển

### 4.1. TransferService — chuyển tiền

Đã có ở trên. Điểm mấu chốt: liên quan 2 Account.

### 4.2. PricingService — tính giá

```python
class PricingService:
    """Tính giá cho Order dựa trên Product, Customer, Quantity."""

    def calculate_line_price(
        self,
        product: Product,
        quantity: int,
    ) -> Money:
        return product.price * Decimal(quantity)

    def calculate_total(
        self,
        order: Order,
        customer: Customer,
        products: dict[UUID, Product],
    ) -> Money:
        total = Money(Decimal("0"), "VND")

        for line in order.lines:
            product = products[line.product_id]
            total = total + self.calculate_line_price(product, line.quantity)

        # Customer discount
        if customer.is_vip():
            total = total * Decimal("0.9")

        return total
```

### 4.3. ReservationService — đặt chỗ

```python
class ReservationService:
    """Đặt chỗ — liên quan Book, Member, Loan."""

    def __init__(self, loan_policy: LoanPolicy) -> None:
        self._loan_policy = loan_policy

    def can_borrow(
        self,
        member: Member,
        book: Book,
    ) -> BorrowEligibility:
        # Member có đang nợ sách không?
        if member.has_overdue_loans():
            return BorrowEligibility.NO_OVERDUE_LOANS

        # Book còn không?
        if not book.is_available():
            return BorrowEligibility.BOOK_NOT_AVAILABLE

        # Member có vượt hạn mức không?
        if member.active_loan_count >= self._loan_policy.max_loans:
            return BorrowEligibility.MAX_LOANS_REACHED

        # Có bị phạt không?
        if member.has_unpaid_fines():
            return BorrowEligibility.UNPAID_FINES

        return BorrowEligibility.ELIGIBLE
```

### 4.4. TaxService — tính thuế

```python
class TaxService:
    """Tính thuế dựa trên loại hàng, khu vực, khách hàng."""

    def calculate(self, order: Order, customer: Customer) -> Money:
        region = customer.address.country
        rate = self._get_tax_rate(region)

        # Một số mặt hàng miễn thuế
        taxable_amount = Money(Decimal("0"), "VND")
        for line in order.lines:
            if not self._is_tax_exempt(line.product_category):
                taxable_amount = taxable_amount + line.subtotal

        return taxable_amount * rate

    def _get_tax_rate(self, region: str) -> Decimal:
        return {
            "Việt Nam": Decimal("0.1"),
            "US": Decimal("0.08"),
            "EU": Decimal("0.2"),
        }.get(region, Decimal("0.1"))

    def _is_tax_exempt(self, category: str) -> bool:
        return category in {"food", "medicine", "books"}
```

---

## 5. Specification Pattern

### 5.1. Vấn đề

Giả sử bạn có rule **phức tạp**:

> "Khách hàng đủ điều kiện nhận khuyến mãi nếu:
> - Là ACTIVE, **VÀ**
> - Đã chi trên 5 triệu trong 30 ngày qua, **VÀ**
> - Chưa nhận khuyến mãi nào trong tháng này, **VÀ**
> - (Là VIP, **HOẶC** đăng ký trên 1 năm)"

**Cách viết thông thường:**

```python
def is_eligible_for_promo(customer: Customer) -> bool:
    if customer.status != CustomerStatus.ACTIVE:
        return False
    if customer.spent_last_30_days.amount < 5_000_000:
        return False
    if customer.promos_this_month > 0:
        return False
    if not (customer.is_vip() or customer.months_since_register >= 12):
        return False
    return True
```

**Vấn đề:**

- Không tái sử dụng được (`is_vip()` cũng cần check riêng).
- Không compose được (không kết hợp `AND`, `OR`).
- Khó test từng phần.

### 5.2. Specification là gì?

> **Specification** là một object đóng gói **một điều kiện nghiệp vụ**. Nó có method `is_satisfied_by(candidate) -> bool`. Specifications có thể **compose** bằng `AND`, `OR`, `NOT`.

### 5.3. Bộ khung

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Base class cho mọi Specification."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        ...

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            and self._right.is_satisfied_by(candidate)
        )


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            or self._right.is_satisfied_by(candidate)
        )


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]) -> None:
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
```

### 5.4. Specifications cụ thể

```python
class ActiveCustomerSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.status == CustomerStatus.ACTIVE


class HighSpenderSpec(Specification[Customer]):
    THRESHOLD = Money(Decimal("5000000"), "VND")

    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.spent_last_30_days.amount >= self.THRESHOLD.amount


class NoPromoThisMonthSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.promos_this_month == 0


class VipCustomerSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.is_vip()


class LongTimeCustomerSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.months_since_register >= 12
```

### 5.5. Compose

```python
# "Khách VIP hoặc đăng ký trên 1 năm"
loyal_customer = VipCustomerSpec() | LongTimeCustomerSpec()

# "Đủ điều kiện khuyến mãi"
eligible_for_promo = (
    ActiveCustomerSpec()
    & HighSpenderSpec()
    & NoPromoThisMonthSpec()
    & loyal_customer
)

# Sử dụng
if eligible_for_promo.is_satisfied_by(customer):
    give_promo(customer)
```

**Điều kỳ diệu:** Rule phức tạp được **compose** từ rule đơn giản. Đọc lên như tiếng Anh/Việt.

### 5.6. Named specification

Để tái sử dụng, đặt tên cho composite:

```python
class EligibleForPromoSpec(Specification[Customer]):
    """Khách đủ điều kiện nhận khuyến mãi."""

    def is_satisfied_by(self, customer: Customer) -> bool:
        return (
            ActiveCustomerSpec().is_satisfied_by(customer)
            and HighSpenderSpec().is_satisfied_by(customer)
            and NoPromoThisMonthSpec().is_satisfied_by(customer)
            and (
                VipCustomerSpec().is_satisfied_by(customer)
                or LongTimeCustomerSpec().is_satisfied_by(customer)
            )
        )
```

Hoặc dùng cách compose:

```python
ELIGIBLE_FOR_PROMO = (
    ActiveCustomerSpec()
    & HighSpenderSpec()
    & NoPromoThisMonthSpec()
    & (VipCustomerSpec() | LongTimeCustomerSpec())
)
```

---

## 6. Specification + Repository

Specification đặc biệt hữu ích khi kết hợp với Repository để **filter**.

### 6.1. Repository filter bằng Specification

```python
# domain/repositories/customer_repository.py
from typing import Protocol
from shop.domain.specifications.base import Specification
from shop.domain.model.customer import Customer


class CustomerRepository(Protocol):
    def find_by_id(self, customer_id: UUID) -> Customer | None: ...
    def save(self, customer: Customer) -> None: ...
    def find_satisfying(self, spec: Specification[Customer]) -> list[Customer]: ...
```

### 6.2. In-memory implementation

```python
class InMemoryCustomerRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Customer] = {}

    def find_satisfying(self, spec: Specification[Customer]) -> list[Customer]:
        return [
            c for c in self._store.values()
            if spec.is_satisfied_by(c)
        ]
```

### 6.3. SQLAlchemy implementation

Vấn đề: SQLAlchemy không thể translate `Specification` thành SQL một cách tự động. Ta cần thêm method `to_sql()` cho mỗi spec.

```python
from abc import ABC, abstractmethod
from sqlalchemy import and_, or_, not_


class SqlSpecification(ABC):
    @abstractmethod
    def to_sql(self):
        """Trả về SQLAlchemy expression."""
        ...


class ActiveCustomerSqlSpec(SqlSpecification):
    def to_sql(self):
        return CustomerRow.status == CustomerStatus.ACTIVE.value


class HighSpenderSqlSpec(SqlSpecification):
    def to_sql(self):
        return CustomerRow.spent_last_30_days >= 5_000_000


class AndSqlSpec(SqlSpecification):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def to_sql(self):
        return and_(self._left.to_sql(), self._right.to_sql())
```

**Vấn đề:** Phải viết **2 lần** rule — 1 cho in-memory, 1 cho SQL. Đây là **trade-off** của Specification.

### 6.4. Giải pháp: Chỉ dùng Specification cho logic phức tạp

**Khuyến nghị:**

- Specification cho **rule nghiệp vụ thuần** (business policy, eligibility).
- Query đơn giản → dùng SQL trực tiếp.

Đừng cố biến mọi query thành Specification. Chỉ những rule **phức tạp, thay đổi thường xuyên** mới cần.

### 6.5. Ví dụ thực tế

```python
# Rule nghiệp vụ: khách đủ điều kiện nhận thẻ tín dụng
def is_eligible_for_credit_card(customer: Customer) -> bool:
    return (
        AdultSpec()
        & HasStableIncomeSpec()
        & NoBadDebtSpec()
        & (VipCustomerSpec() | LongTimeCustomerSpec())
    ).is_satisfied_by(customer)


# Khi cần query list eligible customers
customers = customer_repo.find_satisfying(
    AdultSpec()
    & HasStableIncomeSpec()
    & NoBadDebtSpec()
)
```

---

## 7. Kết hợp Domain Service + Specification

**Đôi khi Specification dùng trong Domain Service.**

```python
class LoanEligibilityService:
    """Domain Service — kiểm tra điều kiện vay."""

    def __init__(self, loan_policy: LoanPolicy) -> None:
        self._policy = loan_policy

    def is_eligible(
        self,
        customer: Customer,
        requested_amount: Money,
    ) -> LoanEligibility:
        # Build spec dựa trên policy
        spec = (
            AdultSpec()
            & GoodCreditScoreSpec(self._policy.min_credit_score)
            & HasIncomeSpec(self._policy.min_income)
            & NoActiveLoanSpec()
        )

        if not spec.is_satisfied_by(customer):
            return LoanEligibility.INELIGIBLE_CUSTOMER

        if requested_amount.amount > self._policy.max_loan_amount.amount:
            return LoanEligibility.AMOUNT_EXCEEDS_LIMIT

        return LoanEligibility.ELIGIBLE
```

---

## 8. Tám anti-pattern khi dùng Domain Service / Specification

### ❌ Anti-pattern 1: Domain Service chứa business rule của Entity

```python
# ❌ SAI: Rule thuộc về Account
class AccountService:
    def withdraw(self, account: BankAccount, amount: Money) -> None:
        if account.balance.amount < amount.amount:
            raise InsufficientFunds()
        account._balance = account._balance - amount
```

**Fix:** Đưa vào `BankAccount.withdraw()`.

### ❌ Anti-pattern 2: Domain Service gọi Application

```python
# ❌ SAI: Domain Service biết Application
class PricingService:
    def __init__(self, place_order_handler) -> None:
        self._handler = place_order_handler   # Ngược dependency!
```

**Fix:** Domain Service không biết Application.

### ❌ Anti-pattern 3: Domain Service import Infrastructure

```python
# ❌ SAI
from sqlalchemy.orm import Session

class PricingService:
    def __init__(self, session: Session) -> None:
        self._session = session
```

**Fix:** Chỉ inject Repository Protocol.

### ❌ Anti-pattern 4: Domain Service có state

```python
# ❌ SAI
class PricingService:
    def __init__(self):
        self._cache = {}   # State!
```

**Fix:** Stateless. Nếu cần cache, dùng Infrastructure layer.

### ❌ Anti-pattern 5: Lạm dụng Domain Service

```python
# ❌ SAI: Mọi thứ đều thành Service
class CustomerNameService:
    def format_name(self, customer: Customer) -> str:
        return f"{customer.last_name} {customer.first_name}"

class CustomerEmailService:
    def send_email(self, customer: Customer) -> None:
        ...
```

**Fix:** `format_name` là method của Customer. `send_email` là Application Service (I/O).

### ❌ Anti-pattern 6: Specification quá đơn giản

```python
# ❌ SAI: Spec cho 1 điều kiện
class IsAdultSpec(Specification[Person]):
    def is_satisfied_by(self, p: Person) -> bool:
        return p.age >= 18

# Rồi dùng
if IsAdultSpec().is_satisfied_by(p):
    ...
```

**Fix:** `if p.age >= 18` đơn giản hơn. Chỉ dùng Spec khi cần **compose**.

### ❌ Anti-pattern 7: Specification chứa side effect

```python
# ❌ SAI
class SendEmailIfEligibleSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        if customer.is_vip():
            email_service.send(customer.email)   # Side effect!
            return True
        return False
```

**Fix:** Specification **chỉ trả về bool**. Không side effect.

### ❌ Anti-pattern 8: Specification phụ thuộc state bên ngoài

```python
# ❌ SAI: Phụ thuộc "now"
class ActiveSubscriptionSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.subscription_end > datetime.now()   # Không testable!
```

**Fix:** Inject `now`:

```python
class ActiveSubscriptionSpec(Specification[Customer]):
    def __init__(self, now: datetime) -> None:
        self._now = now

    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.subscription_end > self._now
```

---

## 9. Ví dụ tổng hợp: E-commerce Pricing

### 9.1. Specifications

```python
# domain/specifications/customer_specs.py
class VipCustomerSpec(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.is_vip()


class NewCustomerSpec(Specification[Customer]):
    def __init__(self, days: int = 30) -> None:
        self._days = days

    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.days_since_register <= self._days
```

```python
# domain/specifications/product_specs.py
class OnSaleSpec(Specification[Product]):
    def is_satisfied_by(self, product: Product) -> bool:
        return product.discount_percent > 0


class LowStockSpec(Specification[Product]):
    def is_satisfied_by(self, product: Product) -> bool:
        return product.stock < 10
```

### 9.2. Pricing Service

```python
# domain/services/pricing_service.py
class PricingService:
    """Domain Service — tính giá cho đơn hàng."""

    def __init__(
        self,
        vip_discount: Percentage = Percentage(Decimal("10")),
        bulk_threshold: int = 100,
        bulk_discount: Percentage = Percentage(Decimal("5")),
    ) -> None:
        self._vip_discount = vip_discount
        self._bulk_threshold = bulk_threshold
        self._bulk_discount = bulk_discount

    def calculate_line_price(
        self,
        product: Product,
        quantity: int,
    ) -> Money:
        base = product.price * Decimal(quantity)

        # Bulk discount
        if quantity >= self._bulk_threshold:
            base = base - Money(
                amount=self._bulk_discount.apply_to(base.amount),
                currency=base.currency,
            )

        # Product discount
        if product.discount_percent > 0:
            discount_amount = (
                base.amount * product.discount_percent / Decimal("100")
            )
            base = base - Money(discount_amount, base.currency)

        return base

    def calculate_total(
        self,
        order: Order,
        customer: Customer,
        products: dict[UUID, Product],
    ) -> Money:
        total = Money(Decimal("0"), "VND")

        for line in order.lines:
            product = products[line.product_id]
            total = total + self.calculate_line_price(product, line.quantity)

        # VIP discount
        if VipCustomerSpec().is_satisfied_by(customer):
            total = total - Money(
                amount=self._vip_discount.apply_to(total.amount),
                currency=total.currency,
            )

        return total
```

### 9.3. Application Handler

```python
# application/commands/calculate_cart.py
class CalculateCartHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        pricing_service: PricingService,
    ) -> None:
        self._uow = uow
        self._pricing_service = pricing_service

    def handle(self, cmd: CalculateCartCommand) -> CartTotalDTO:
        customer = self._uow.customers.find_by_id(cmd.customer_id)
        if not customer:
            raise CustomerNotFound()

        products = {
            item_id: self._uow.products.find_by_id(item_id)
            for item_id in cmd.product_ids
        }

        order = Order.create(customer.id)
        for item in cmd.items:
            order.add_line(OrderLine.create(...))

        total = self._pricing_service.calculate_total(order, customer, products)

        return CartTotalDTO(total=str(total))
```

**Điểm mấu chốt:**

- `PricingService` — logic nghiệp vụ phức tạp, không thuộc về Entity nào.
- `VipCustomerSpec` — điều kiện tái sử dụng.
- `CalculateCartHandler` — orchestration mỏng.
- Test `PricingService` pure Python.

### 9.4. Test

```python
# tests/unit/domain/test_pricing_service.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.domain.services.pricing_service import PricingService
from shop.domain.model.product import Product
from shop.shared.domain.money import Money


@pytest.fixture
def service() -> PricingService:
    return PricingService()


class TestPricingService:
    def test_basic_price(self, service) -> None:
        product = Product.create(
            sku="SKU001", name="Book", price=Money(Decimal("100"), "VND"), stock=100
        )
        assert service.calculate_line_price(product, 1) == Money(Decimal("100"), "VND")

    def test_bulk_discount_applied(self, service) -> None:
        product = Product.create(
            sku="SKU001", name="Book", price=Money(Decimal("100"), "VND"), stock=100
        )
        # 100 * 100 = 10000, discount 5% → 9500
        assert service.calculate_line_price(product, 100) == Money(Decimal("9500"), "VND")

    def test_no_bulk_discount_below_threshold(self, service) -> None:
        product = Product.create(
            sku="SKU001", name="Book", price=Money(Decimal("100"), "VND"), stock=100
        )
        assert service.calculate_line_price(product, 99) == Money(Decimal("9900"), "VND")
```

---

## 10. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): TransferService

Viết Domain Service `TransferService` cho ngân hàng:

- `transfer(source: BankAccount, target: BankAccount, amount: Money) -> TransferResult`.
- Rule:
  - Amount > 0.
  - Amount ≤ 100 triệu/ngày.
  - Source phải ACTIVE.
  - Target phải ACTIVE.
  - Phí = 0.1% amount, tối thiểu 10k, tối đa 100k.
- `TransferResult` chứa `amount`, `fee`, `occurred_at`.

Viết ít nhất 10 test.

### 🟡 Bài tập 2 (trung bình): LoanEligibilityService + Specifications

Cho domain "thư viện":

- Entity `Member` (có `status`, `active_loans`, `overdue_count`, `unpaid_fines`, `months_since_register`).
- Entity `Book` (có `status`, `available_copies`).

Viết:

- Specifications:
  - `ActiveMemberSpec`
  - `NoOverdueSpec`
  - `NoUnpaidFinesSpec`
  - `UnderLoanLimitSpec(limit)`
  - `BookAvailableSpec`
  - `LongTimeMemberSpec(months)`

- Domain Service `LoanEligibilityService` với method `can_borrow(member, book) -> LoanEligibility`.

- Compose specs để kiểm tra điều kiện.

Viết ít nhất 15 test, bao gồm test từng spec và test kết hợp.

### 🔴 Bài tập 3 (khó): Pricing Engine hoàn chỉnh

Cho hệ thống e-commerce:

- Product có `base_price`, `category`, `discount_percent`.
- Customer có `tier` (BRONZE, SILVER, GOLD, PLATINUM), `total_spent`, `days_since_register`.
- Order có nhiều lines.
- Promo code có `discount_type` (PERCENT, FIXED), `min_order_value`, `applies_to_category`.

Viết:

1. Specifications:
   - `TierSpec(tier)`
   - `MinOrderValueSpec(amount)`
   - `CategoryMatchSpec(category)`
   - `FirstOrderSpec`
   - `LoyalCustomerSpec(months)`

2. Domain Service `PricingEngine`:
   - Tính base total.
   - Apply bulk discount.
   - Apply category discount.
   - Apply tier discount.
   - Apply promo code (validate min_order_value, applies_to_category).
   - Tính tax dựa trên khu vực.

3. Test:
   - Happy path.
   - Promo không đủ min_order_value → không apply.
   - Promo không đúng category → không apply.
   - Multiple discounts stack đúng thứ tự.
   - VIP customer được giảm thêm.

Viết ít nhất 25 test.

Bonus: Viết `PricingEngine` không dùng `if/else`, chỉ dùng Specification + compose.

---

## 11. Checklist sau bài 12

Trước khi sang bài 13, bạn phải tự tin trả lời:

- [ ] Domain Service là gì? Không là gì?
- [ ] Domain Service vs Application Service?
- [ ] 5 dấu hiệu cần Domain Service?
- [ ] Khi nào KHÔNG dùng Domain Service?
- [ ] Specification pattern là gì?
- [ ] Làm sao compose Specification?
- [ ] Specification + Repository — lợi ích và trade-off?
- [ ] Tại sao Specification không nên có side effect?
- [ ] Tại sao Specification không phụ thuộc `datetime.now()`?
- [ ] 8 anti-pattern khi dùng Domain Service / Specification?

Nếu trả lời được hết, bạn đã sẵn sàng bài 13.

---

## 12. Tóm tắt bài 12

| Điểm | Nội dung |
|---|---|
| **Domain Service** | Stateless, chứa logic không thuộc Entity nào |
| **Khác Application** | Domain chứa rule; Application orchestration |
| **5 dấu hiệu** | Nhiều aggregate, không tự nhiên thuộc Entity, tính toán phức tạp, algorithm, tái sử dụng |
| **Không dùng khi** | Thuộc 1 Entity, utility, wrap repo, dùng 1 lần |
| **Specification** | Đóng gói 1 điều kiện, `is_satisfied_by()` |
| **Compose** | `&`, `\|`, `~` cho AND, OR, NOT |
| **Repository filter** | `find_satisfying(spec)` |
| **Trade-off** | Spec phải viết 2 lần nếu cần SQL |
| **Không side effect** | Spec chỉ trả bool |
| **Không phụ thuộc now** | Inject `now` vào constructor |
| **8 anti-pattern** | Rule sai chỗ, ngược dependency, import Infra, có state, lạm dụng, Spec đơn giản, side effect, phụ thuộc now |

**Câu thần chú:** *"Entity có logic của Entity. Service có logic của nhiều Entity. Specification có điều kiện compose được."*

---

## 13. Chuẩn bị cho bài 13

Bài tiếp theo: **Dependency Injection trong Python**.

Chuẩn bị:
- Đọc lại `bootstrap.py` (bài 10).
- Nghĩ về **cách wire các object** trong project của bạn.
- Sẽ bàn: manual DI, DI container, `dependency-injector`, testing với DI, và các pattern DI trong Python.

Đây là bài **bản lề** giữa Level 3 và Level 4 — bạn sẽ hiểu cách ráp mọi thứ mà không cần framework nặng.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 13** (Dependency Injection) ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Specification + SQLAlchemy, composite pattern, caching specifications.
5. **Review code Domain Service / Specification** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.