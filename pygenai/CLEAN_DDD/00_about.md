Clean Architecture và Domain-Driven Design (DDD) kết hợp với nhau nhằm xây dựng hệ thống lấy **nghiệp vụ cốt lõi (Domain)** làm trung tâm, tách rời hoàn toàn khỏi framework, cơ sở dữ liệu và các yếu tố kỹ thuật bên ngoài.

---

## Các khái niệm cốt lõi

### Domain-Driven Design (DDD)

DDD tập trung mô hình hóa bài toán nghiệp vụ phức tạp thành mã nguồn thông qua các thành phần:

* **Entity**: Đối tượng có danh tính riêng (`id`) phân biệt và có vòng đời thay đổi theo thời gian (ví dụ: `Order`, `Customer`).
* **Value Object**: Đối tượng bất biến (Immutable), không có `id`, được định nghĩa hoàn toàn bởi giá trị của các thuộc tính (ví dụ: `Money`, `Address`).
* **Aggregate & Aggregate Root**: Cụm các Entity và Value Object đi liền với nhau. Aggregate Root là Entity chính quản lý tính toàn vẹn dữ liệu cho cả cụm.
* **Domain Event**: Sự kiện quan trọng vừa xảy ra trong nghiệp vụ (ví dụ: `OrderPlacedEvent`).

### Clean Architecture

Sắp xếp mã nguồn thành các lớp đồng tâm với **Quy tắc phụ thuộc (Dependency Rule)**: Mã ở lớp bên trong không được phép biết đến mã ở lớp bên ngoài.

1. **Domain Layer (Lõi trong cùng)**: Chứa Entities, Value Objects và Domain Exceptions. Không import bất kỳ thư viện ngoài nào (FastAPI, SQLAlchemy, v.v.).
2. **Application Layer (Use Cases)**: Chứa logic điều hướng nghiệp vụ (ví dụ: `CreateOrderUseCase`), DTOs và khai báo các Interface/Abstract Class (như `OrderRepository`).
3. **Infrastructure Layer**: Cài đặt thực tế các Interface từ lớp Application (SQLAlchemy ORM, Redis, Service gửi Mail, External APIs).
4. **Presentation / API Layer**: FastAPI/Flask Router, CLI, nhận Request, validate dữ liệu đầu vào và chuyển cho Use Case.

---

## Minh họa triển khai bằng Python

### 1. Domain Layer (`domain/order.py`)

```python
from dataclasses import dataclass
from typing import List
import uuid

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "VND"

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Money

class Order:
    """Aggregate Root quản lý toàn bộ logic nghiệp vụ đơn hàng"""
    def __init__(self, order_id: str = None):
        self.id = order_id or str(uuid.uuid4())
        self.items: List[OrderItem] = []
        self.is_paid: bool = False

    def add_item(self, product_id: str, quantity: int, unit_price: Money) -> None:
        if self.is_paid:
            raise ValueError("Không thể chỉnh sửa đơn hàng đã thanh toán")
        self.items.append(OrderItem(product_id, quantity, unit_price))

    @property
    def total_amount(self) -> Money:
        total = sum(item.quantity * item.unit_price.amount for item in self.items)
        return Money(amount=total)

```

### 2. Application Layer (`application/use_cases.py`)

```python
from abc import ABC, abstractmethod
from domain.order import Order, Money

class OrderRepository(ABC):
    """Interface định nghĩa các thao tác lưu trữ (Inversion of Control)"""
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

class CreateOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    def execute(self, product_id: str, quantity: int, price: float) -> str:
        order = Order()
        order.add_item(product_id, quantity, Money(price))
        self.order_repo.save(order)
        return order.id

```

### 3. Infrastructure Layer (`infrastructure/repositories.py`)

```python
from domain.order import Order
from application.use_cases import OrderRepository

class SQLAlchemyOrderRepository(OrderRepository):
    """Cài đặt thực tế việc tương tác với Database"""
    def __init__(self, db_session):
        self.session = db_session

    def save(self, order: Order) -> None:
        # Chuyển đổi Domain Entity thành ORM Model và commit vào DB
        print(f"Lưu đơn hàng {order.id} với tổng tiền {order.total_amount.amount} VND vào DB.")

```

---

## Nguyên tắc thực hành trong Python

* **Dependency Inversion**: Lớp Application giữ Interface `OrderRepository`, lớp Infrastructure cài đặt `SQLAlchemyOrderRepository`. Nhờ đó, việc đổi cơ sở dữ liệu không làm ảnh hưởng đến logic nghiệp vụ.
* **Dataclasses gốc**: Sử dụng `dataclass` tiêu chuẩn của Python cho Domain Entities nhằm tránh phụ thuộc vào thư viện ngoài. Dùng `Pydantic` ở lớp Presentation/API để kiểm tra tính hợp lệ của Request.
* **Tính dễ kiểm thử (Testability)**: Lớp Domain và Application hoàn toàn không cần mock Database khi viết Unit Test, giúp chạy test nhanh và chính xác.