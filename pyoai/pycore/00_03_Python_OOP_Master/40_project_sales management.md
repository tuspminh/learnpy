# Python OOP Master — Buổi 40

# Project 2 — Sales Management System

Hôm nay chúng ta xây **Sales Management System** để tổng hợp những Design Pattern đã học.

Project này quan trọng vì nó gần với hệ thống thực tế hơn Library Management.

---

# 1. Mục tiêu

Ta sẽ xây:

```text
Sales System
│
├── Product
├── Customer
├── Order
└── OrderItem
```

Workflow:

```text
Customer
   ↓
Create Order
   ↓
Add Products
   ↓
Calculate Price
   ↓
Apply Discount
   ↓
Complete Order
   ↓
Save
   ↓
Publish Event
```

Các pattern:

| Pattern      | Sử dụng                      |
| ------------ | ---------------------------- |
| Entity       | Product, Customer, Order     |
| Value Object | Money                        |
| Repository   | Persistence                  |
| DI           | Inject dependencies          |
| Builder      | Build Order                  |
| Strategy     | Discount                     |
| Factory      | Payment                      |
| Command      | Create/Cancel/Complete Order |
| Observer     | Order events                 |

---

# 2. Kiến trúc

```text
sales/
│
├── domain/
│   ├── entities/
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── order_item.py
│   │
│   ├── value_objects/
│   │   └── money.py
│   │
│   ├── repositories/
│   │   ├── product_repository.py
│   │   ├── customer_repository.py
│   │   └── order_repository.py
│   │
│   └── strategies/
│       └── discount.py
│
├── application/
│   ├── services/
│   │   └── order_service.py
│   │
│   └── commands/
│       ├── create_order.py
│       ├── cancel_order.py
│       └── complete_order.py
│
├── infrastructure/
│   ├── database.py
│   └── repositories/
│
└── main.py
```

---

# 3. Value Object — Money

Đây là một bước tiến quan trọng so với project Library.

Không nên dùng:

```python
price = 199000
```

khắp hệ thống.

Ta tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "VND"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")

    def add(self, other: "Money") -> "Money":
        self._check_currency(other)

        return Money(
            self.amount + other.amount,
            self.currency,
        )

    def subtract(self, other: "Money") -> "Money":
        self._check_currency(other)

        result = self.amount - other.amount

        if result < 0:
            raise ValueError("Result cannot be negative")

        return Money(result, self.currency)

    def multiply(self, quantity: int) -> "Money":
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        return Money(
            self.amount * quantity,
            self.currency,
        )

    def _check_currency(self, other: "Money"):
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
```

Bây giờ:

```python
price = Money(100_000)

total = price.multiply(3)

print(total)
```

Kết quả:

```text
Money(amount=300000, currency='VND')
```

---

# 4. Product Entity

```python
from dataclasses import dataclass

from domain.value_objects.money import Money


@dataclass
class Product:
    id: int | None
    name: str
    price: Money
    stock: int

    def __post_init__(self):
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")

    def decrease_stock(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if quantity > self.stock:
            raise ValueError("Not enough stock")

        self.stock -= quantity
```

Business rule:

```text
quantity > stock
       ↓
     ERROR
```

Không để Application tự sửa:

```python
product.stock -= quantity
```

mà phải:

```python
product.decrease_stock(quantity)
```

---

# 5. Customer

```python
from dataclasses import dataclass


@dataclass
class Customer:
    id: int | None
    name: str
    email: str
```

---

# 6. OrderItem

```python
from dataclasses import dataclass

from domain.entities.product import Product
from domain.value_objects.money import Money


@dataclass
class OrderItem:
    product_id: int
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)
```

Ví dụ:

```python
item = OrderItem(
    product_id=1,
    product_name="Keyboard",
    unit_price=Money(500_000),
    quantity=2,
)

print(item.subtotal)
```

```text
Money(amount=1000000, currency='VND')
```

---

# 7. Order Entity

Order có lifecycle:

```text
PENDING
   │
   ├── complete()
   │
   ↓
COMPLETED


PENDING
   │
   ├── cancel()
   │
   ↓
CANCELLED
```

Code:

```python
from dataclasses import dataclass, field
from enum import Enum

from domain.entities.order_item import OrderItem
from domain.value_objects.money import Money


class OrderStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    id: int | None
    customer_id: int
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING

    def add_item(self, item: OrderItem):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                "Cannot modify completed/cancelled order"
            )

        self.items.append(item)

    @property
    def subtotal(self) -> Money:
        total = Money(0)

        for item in self.items:
            total = total.add(item.subtotal)

        return total

    def complete(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                "Only pending order can be completed"
            )

        if not self.items:
            raise ValueError(
                "Cannot complete empty order"
            )

        self.status = OrderStatus.COMPLETED

    def cancel(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                "Only pending order can be cancelled"
            )

        self.status = OrderStatus.CANCELLED
```

---

# 8. Tại sao Order có Behavior?

Không nên làm:

```python
order.status = OrderStatus.COMPLETED
```

ở application.

Thay vào đó:

```python
order.complete()
```

Entity tự bảo vệ invariant:

```text
Completed Order
      ↓
Cannot cancel
Cannot add item
Cannot modify
```

Đây chính là **Rich Domain Model**.

---

# 9. Discount Strategy

Đây là nơi Strategy cực kỳ phù hợp.

Ta có:

```text
DiscountStrategy
       │
       ├── NoDiscount
       ├── PercentageDiscount
       └── FixedDiscount
```

Interface:

```python
from abc import ABC, abstractmethod

from domain.value_objects.money import Money


class DiscountStrategy(ABC):

    @abstractmethod
    def calculate(
        self,
        subtotal: Money,
    ) -> Money:
        pass
```

---

# 10. No Discount

```python
class NoDiscount(DiscountStrategy):

    def calculate(self, subtotal: Money) -> Money:
        return Money(0, subtotal.currency)
```

---

# 11. Percentage Discount

```python
class PercentageDiscount(DiscountStrategy):

    def __init__(self, percent: int):
        if not 0 <= percent <= 100:
            raise ValueError(
                "Percent must be between 0 and 100"
            )

        self.percent = percent

    def calculate(self, subtotal: Money) -> Money:
        amount = subtotal.amount * self.percent // 100

        return Money(
            amount,
            subtotal.currency,
        )
```

Ví dụ:

```python
discount = PercentageDiscount(10)

result = discount.calculate(
    Money(1_000_000)
)

print(result)
```

```text
Money(amount=100000, currency='VND')
```

---

# 12. Fixed Discount

```python
class FixedDiscount(DiscountStrategy):

    def __init__(self, amount: Money):
        self.amount = amount

    def calculate(self, subtotal: Money) -> Money:
        if self.amount.amount > subtotal.amount:
            return Money(0, subtotal.currency)

        return self.amount
```

---

# 13. Order Total

Ta có:

```text
Subtotal
   ↓
Discount Strategy
   ↓
Discount
   ↓
Total
```

Có thể thêm vào Order:

```python
def total(
    self,
    discount_strategy: DiscountStrategy,
) -> Money:

    discount = discount_strategy.calculate(
        self.subtotal
    )

    return self.subtotal.subtract(discount)
```

Sử dụng:

```python
total = order.total(
    PercentageDiscount(10)
)
```

---

# 14. Repository

Order Repository:

```python
from abc import ABC, abstractmethod

from domain.entities.order import Order


class OrderRepository(ABC):

    @abstractmethod
    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass
```

Product:

```python
class ProductRepository(ABC):

    @abstractmethod
    def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:
        pass

    @abstractmethod
    def save(self, product: Product) -> None:
        pass
```

---

# 15. Order Service

Bây giờ Application Layer.

```python
class OrderService:

    def __init__(
        self,
        product_repository,
        customer_repository,
        order_repository,
        discount_strategy,
    ):
        self.product_repository = product_repository
        self.customer_repository = customer_repository
        self.order_repository = order_repository
        self.discount_strategy = discount_strategy
```

Notice:

Service không tạo:

```text
SQLite
Repository
Discount
```

Tất cả đều được inject.

---

# 16. Create Order

```python
def create_order(
    self,
    customer_id: int,
    product_id: int,
    quantity: int,
):

    customer = self.customer_repository.get_by_id(
        customer_id
    )

    if customer is None:
        raise ValueError("Customer not found")

    product = self.product_repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError("Product not found")

    product.decrease_stock(quantity)

    item = OrderItem(
        product_id=product.id,
        product_name=product.name,
        unit_price=product.price,
        quantity=quantity,
    )

    order = Order(
        id=None,
        customer_id=customer_id,
    )

    order.add_item(item)

    self.product_repository.save(product)
    self.order_repository.save(order)

    return order
```

---

# 17. Builder

Order có thể trở nên phức tạp:

```text
Customer
Products
Shipping
Discount
Payment
Notes
Coupon
...
```

Builder giúp tách construction.

```python
class OrderBuilder:

    def __init__(self):
        self._customer_id = None
        self._items = []

    def customer(self, customer_id: int):
        self._customer_id = customer_id
        return self

    def add_item(self, item: OrderItem):
        self._items.append(item)
        return self

    def build(self) -> Order:

        if self._customer_id is None:
            raise ValueError(
                "Customer is required"
            )

        if not self._items:
            raise ValueError(
                "Order must contain items"
            )

        order = Order(
            id=None,
            customer_id=self._customer_id,
        )

        for item in self._items:
            order.add_item(item)

        return order
```

Usage:

```python
order = (
    OrderBuilder()
    .customer(10)
    .add_item(item1)
    .add_item(item2)
    .build()
)
```

---

# 18. Command

Bây giờ UI không gọi trực tiếp Service.

Thay vì:

```text
Button
  ↓
order_service.complete_order()
```

ta có:

```text
Button
   ↓
Command
   ↓
Handler/Service
```

Command:

```python
from dataclasses import dataclass


@dataclass
class CompleteOrderCommand:
    order_id: int
```

Handler:

```python
class CompleteOrderHandler:

    def __init__(self, order_service):
        self.order_service = order_service

    def handle(
        self,
        command: CompleteOrderCommand,
    ):
        return self.order_service.complete_order(
            command.order_id
        )
```

UI:

```python
command = CompleteOrderCommand(
    order_id=100
)

handler.handle(command)
```

Đây là kiến trúc gần với CQRS:

```text
Command
   ↓
Handler
   ↓
Application Service
   ↓
Domain
```

---

# 19. Observer

Khi Order hoàn thành:

```text
OrderCompleted
       │
       ├── Logger
       ├── Email
       ├── Metrics
       └── Notification
```

Event:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderCompleted:
    order_id: int
```

Observer:

```python
class OrderObserver:

    def on_order_completed(
        self,
        event: OrderCompleted,
    ):
        pass
```

Logger:

```python
class LoggingObserver(OrderObserver):

    def on_order_completed(
        self,
        event: OrderCompleted,
    ):
        print(
            f"Order {event.order_id} completed"
        )
```

---

# 20. Event Publisher

```python
class EventPublisher:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def publish(self, event):

        for observer in self._observers:
            observer.on_order_completed(event)
```

Composition:

```python
publisher = EventPublisher()

publisher.subscribe(
    LoggingObserver()
)
```

Sau đó:

```python
publisher.publish(
    OrderCompleted(order_id=100)
)
```

---

# 21. Factory

Giả sử hệ thống hỗ trợ:

```text
Payment
   ├── Cash
   ├── BankTransfer
   └── CreditCard
```

Interface:

```python
from abc import ABC, abstractmethod


class Payment(ABC):

    @abstractmethod
    def pay(self, amount: Money):
        pass
```

Implement:

```python
class CashPayment(Payment):

    def pay(self, amount: Money):
        print(
            f"Cash payment: {amount.amount}"
        )
```

```python
class BankTransferPayment(Payment):

    def pay(self, amount: Money):
        print(
            f"Bank transfer: {amount.amount}"
        )
```

Factory:

```python
class PaymentFactory:

    @staticmethod
    def create(payment_type: str) -> Payment:

        if payment_type == "cash":
            return CashPayment()

        if payment_type == "bank":
            return BankTransferPayment()

        raise ValueError(
            f"Unknown payment type: {payment_type}"
        )
```

Usage:

```python
payment = PaymentFactory.create("cash")

payment.pay(Money(500_000))
```

Factory quyết định:

> **Tạo implementation nào?**

Strategy quyết định:

> **Dùng algorithm nào?**

Builder quyết định:

> **Xây object như thế nào?**

---

# 22. Toàn bộ kiến trúc

Đây là phần quan trọng nhất của Buổi 40.

```text
                         UI
                          │
                          ↓
                       Command
                          │
                          ↓
                  Application Service
                          │
             ┌────────────┼────────────┐
             │            │            │
             ↓            ↓            ↓
        Repository     Strategy      Factory
             │            │            │
             ↓            ↓            ↓
           SQLite      Discount      Payment
             │
             ↓
          Database
```

Observer nằm bên cạnh:

```text
Application Service
       │
       ├── Repository
       │
       └── Event Publisher
                │
        ┌───────┼────────┐
        ↓       ↓        ↓
      Logger  Email    Metrics
```

---

# 23. SOLID xuất hiện ở đâu?

## SRP

Mỗi class có trách nhiệm riêng:

```text
Order
    → Domain rules

Repository
    → Persistence

Strategy
    → Discount algorithm

Factory
    → Object creation

Command
    → Request

Observer
    → Event reaction
```

---

## OCP

Thêm discount:

```python
class VipDiscount(DiscountStrategy):
    ...
```

Không cần sửa `Order`.

---

## LSP

Mọi:

```text
DiscountStrategy
```

đều phải có thể thay thế nhau:

```python
NoDiscount()
PercentageDiscount(10)
VipDiscount()
```

---

## ISP

Không tạo interface khổng lồ:

```python
class EverythingRepository:
    save_product()
    save_customer()
    save_order()
    delete_product()
    ...
```

Thay vào đó:

```text
ProductRepository
CustomerRepository
OrderRepository
```

---

## DIP

Application phụ thuộc abstraction:

```text
OrderService
     ↓
OrderRepository
```

không phụ thuộc:

```text
SQLiteOrderRepository
```

---

# 24. Đây là điểm rất quan trọng: Transaction

Ở Library project ta có:

```text
save Book
save Loan
```

Sales còn nghiêm trọng hơn:

```text
Decrease stock
      +
Create Order
      +
Create Order Items
      +
Payment
```

Nếu:

```text
Decrease stock → OK
Create Order   → OK
Payment        → ERROR
```

thì hệ thống có thể bị trạng thái không nhất quán.

Ví dụ:

```text
Stock = 10

Order creation OK
Stock → 8

Payment ERROR

Order không tồn tại
nhưng stock đã giảm
```

Đây là lúc ta bắt đầu cần:

# Unit of Work / Transaction

Kiến trúc nâng cao:

```text
Application Service
       │
       ↓
   UnitOfWork
       │
   ┌───┼────────┐
   ↓   ↓        ↓
Product Order Customer
 Repo   Repo      Repo
       │
       ↓
    SQLite
    BEGIN
      │
      ├── operations
      │
    COMMIT
```

Nếu lỗi:

```text
ROLLBACK
```

Đây là một chủ đề rất đáng học sau Design Pattern.

---

# 25. Test Architecture

Một trong những lợi ích lớn nhất của toàn bộ kiến trúc:

```text
OrderService
      ↓
MemoryRepository
      +
FakePayment
      +
FakeEventPublisher
```

Không cần:

```text
SQLite
Network
Payment Gateway
Email
```

Ví dụ:

```python
class FakeProductRepository:

    def __init__(self):
        self.products = {}

    def get_by_id(self, product_id):
        return self.products.get(product_id)

    def save(self, product):
        self.products[product.id] = product
```

Test:

```python
product = Product(
    id=1,
    name="Keyboard",
    price=Money(500_000),
    stock=10,
)

products = FakeProductRepository()
products.save(product)
```

Service sử dụng fake repository:

```python
service = OrderService(
    product_repository=products,
    customer_repository=customers,
    order_repository=orders,
    discount_strategy=NoDiscount(),
)
```

Đây chính là:

```text
Dependency Injection
        +
Repository
        +
SOLID
        ↓
Testable Architecture
```

---

# 26. Nhìn lại toàn bộ Design Pattern

Sau 9 buổi Design Pattern:

```text
Singleton
    ↓
Factory
    ↓
Builder
    ↓
Strategy
    ↓
Observer
    ↓
Command
    ↓
Repository
```

Ta không còn học Pattern riêng lẻ nữa.

Ta bắt đầu nhìn chúng như **những công cụ giải quyết các loại vấn đề khác nhau**.

| Vấn đề                       | Pattern    |
| ---------------------------- | ---------- |
| Một instance dùng chung      | Singleton  |
| Chọn implementation để tạo   | Factory    |
| Object construction phức tạp | Builder    |
| Nhiều algorithm              | Strategy   |
| Thông báo khi có sự kiện     | Observer   |
| Đóng gói action              | Command    |
| Abstraction persistence      | Repository |

---

# 27. Mapping sang Story Crawler của bạn

Đây là phần mình muốn bạn đặc biệt chú ý.

Sales:

```text
OrderService
    ↓
OrderRepository
    ↓
SQLite
```

Story Crawler:

```text
StoryService
    ↓
StoryRepository
    ↓
SQLite
```

Sales:

```text
DiscountStrategy
    ├── NoDiscount
    ├── PercentageDiscount
    └── VipDiscount
```

Crawler:

```text
RetryStrategy
    ├── NoRetry
    ├── FixedRetry
    └── ExponentialBackoff
```

Sales:

```text
PaymentFactory
```

Crawler:

```text
ParserFactory
    ├── SiteAParser
    ├── SiteBParser
    └── SiteCParser
```

Sales:

```text
OrderCompleted
      ↓
Observer
```

Crawler:

```text
ChapterCompleted
      ↓
Observer
      ├── Dashboard
      ├── Logger
      └── Metrics
```

Sales:

```text
Command
   ↓
CreateOrder
CancelOrder
CompleteOrder
```

Crawler:

```text
Command
   ↓
StartCrawler
PauseCrawler
ResumeCrawler
StopCrawler
RetryChapter
```

Đây là lý do project hôm nay rất quan trọng đối với hệ thống crawler/reader mà bạn đang hướng tới.

---

# 28. Tổng kết toàn bộ khóa OOP

Ta đã đi từ:

```text
Class
 ↓
Object
 ↓
Encapsulation
 ↓
Inheritance
 ↓
Polymorphism
 ↓
Composition
 ↓
SOLID
 ↓
Dependency Injection
 ↓
Repository
 ↓
Design Patterns
 ↓
Architecture
```

Và hiện tại có thể thiết kế:

```text
                Presentation
                     ↓
                  Command
                     ↓
             Application Layer
                     ↓
              Domain Layer
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Repository     Strategy      Events
        ↓
 Infrastructure
        ↓
      SQLite
```

Đây đã vượt xa mức **“học OOP Python”**.

Bạn đang chuyển sang tư duy:

> **Software Architecture bằng Python.**

---

# 29. Bài tập cuối khóa ⭐⭐⭐

Hãy thiết kế hệ thống:

```text
Story Crawler
```

với:

```text
ParserFactory
RetryStrategy
StoryRepository
CrawlerCommand
CrawlerObserver
CrawlerConfigBuilder
Dependency Injection
```

Kiến trúc:

```text
CLI / PySide6
       ↓
Command
       ↓
CrawlerService
       │
       ├── ParserFactory
       │
       ├── RetryStrategy
       │
       ├── StoryRepository
       │
       └── EventPublisher
               │
       ┌───────┼─────────┐
       ↓       ↓         ↓
   Dashboard Logger    Metrics
```

Nếu bạn tự thiết kế được hệ thống này mà **không để UI biết SQLite, không để Crawler biết implementation parser cụ thể, và không để business logic phụ thuộc infrastructure**, thì bạn đã nắm được phần OOP + SOLID + Design Pattern ở mức khá tốt.

### Bước tiếp theo

Sau Buổi 40, hướng hợp lý nhất là chuyển sang **OOP Architecture nâng cao**: **Unit of Work → Service Layer → Specification Pattern → Domain Events → CQRS → Clean Architecture → DDD**, rồi áp dụng toàn bộ vào **Story Crawler/Reader thực tế**.
