# 📖 Bài 4: Bounded Context — Chia để trị

> Bài này dạy bạn **cách chia hệ thống lớn thành nhiều context độc lập**. Đây là bài bản lề: từ đây bạn bước từ **tactical DDD** (Entity, VO, Aggregate) sang **strategic DDD** (Bounded Context, Context Map). Nếu không hiểu bài này, bạn sẽ cố nhồi mọi thứ vào một model khổng lồ — và dự án sẽ chết.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Bounded Context** là gì và tại sao nó là **khái niệm quan trọng nhất** của DDD.
2. Nhận diện được **cùng một từ, nghĩa khác nhau** ở từng context.
3. Biết **khi nào tách**, **khi nào gộp** context.
4. Biết 5 pattern tích hợp giữa các context (Shared Kernel, ACL, Conformist...).
5. Áp dụng vào Python: **mỗi context là một package riêng biệt**.
6. Vẽ được **Context Map** cho một hệ thống thực tế.

---

## 1. Vấn đề gốc — Tại sao cần Bounded Context?

### 1.1. Câu chuyện có thật

Một công ty thương mại điện tử có hệ thống như sau:

- **Team Sales:** nói về "Customer" — người có thể mua hàng, có credit limit.
- **Team Shipping:** nói về "Customer" — người nhận hàng, có địa chỉ giao.
- **Team Support:** nói về "Customer" — người có ticket, có SLA.
- **Team Billing:** nói về "Customer" — người phải trả tiền, có payment method.

Một dev giỏi (nhưng chưa hiểu DDD) quyết định: *"Customer là Customer, tôi làm 1 class Customer duy nhất cho cả hệ thống!"*

```python
class Customer:
    # Từ Sales
    credit_limit: Money
    total_purchases: Money

    # Từ Shipping
    shipping_address: Address
    preferred_carrier: str

    # Từ Support
    support_tier: str
    open_tickets: list[Ticket]
    sla_hours: int

    # Từ Billing
    payment_methods: list[PaymentMethod]
    outstanding_balance: Money
    tax_id: str

    # Từ Marketing
    email_opt_in: bool
    segments: list[str]

    # ... và 40 field khác
```

**Chuyện gì xảy ra sau 1 năm?**

- Class có **60+ field**, không ai hiểu hết.
- Sales đổi credit limit rule → ảnh hưởng Shipping (vì chung class).
- Support thêm field mới → Billing phải migrate DB.
- Migration DB: **không thể** vì mọi team dùng chung bảng `customers`.
- Deploy: 1 team thay đổi → cả hệ thống phải deploy lại.
- **Ai cũng sợ sửa Customer.**

**Đây chính là vấn đề Bounded Context ra đời để giải quyết.**

### 1.2. Insight quan trọng

> *"Cùng một từ có thể có nghĩa khác nhau ở những ngữ cảnh khác nhau. Và điều đó **không phải là vấn đề** — đó là **thực tế**. Vấn đề là chúng ta cố gắng đồng nhất hóa chúng."*

**"Customer" không phải là một khái niệm duy nhất.** Nó là **5 khái niệm khác nhau**, mỗi cái sống trong một ngữ cảnh riêng.

**Bounded Context** = một **ranh giới rõ ràng** trong đó một **model** có nghĩa **nhất quán**.

---

## 2. Bounded Context là gì?

### 2.1. Định nghĩa

> **Bounded Context** là một **ranh giới rõ ràng** (thường là ranh giới của một team hoặc một module) trong đó một **domain model cụ thể** được định nghĩa và áp dụng nhất quán.
>
> Bên trong context: mọi người nói cùng ngôn ngữ, mọi khái niệm có nghĩa rõ ràng.
> Bên ngoài context: cùng từ đó có thể có nghĩa khác.

### 2.2. Bốn tính chất của Bounded Context

| Tính chất | Ý nghĩa |
|---|---|
| **Ranh giới rõ ràng** | Có điểm vào/ra xác định, không mơ hồ |
| **Ngôn ngữ nhất quán bên trong** | Trong context, "Customer" chỉ có 1 nghĩa |
| **Model riêng biệt** | Có class `Customer` riêng, không share với context khác |
| **Team sở hữu** | Có 1 team chịu trách nhiệm (Conway's Law) |

### 2.3. Ví dụ: cùng từ, nghĩa khác

**"Product" trong 4 context:**

| Context | "Product" nghĩa là gì? | Field cần |
|---|---|---|
| **Catalog** | Mặt hàng để bán | `sku`, `name`, `description`, `images`, `categories` |
| **Inventory** | Mặt hàng để đếm | `sku`, `quantity_on_hand`, `warehouse_location` |
| **Pricing** | Mặt hàng để tính giá | `sku`, `base_price`, `discount_rules`, `tax_class` |
| **Shipping** | Mặt hàng để đóng gói | `sku`, `weight`, `dimensions`, `fragile` |

→ **4 class `Product` khác nhau** ở **4 package khác nhau**, dù cùng tên.

**"Order" trong 3 context:**

| Context | "Order" nghĩa là gì? |
|---|---|
| **Sales** | Đơn khách hàng đặt, có line items, có tổng tiền |
| **Fulfillment** | Đơn cần đóng gói, có warehouse tasks |
| **Billing** | Đơn cần thu tiền, có invoice, có payment status |

**"Flight" trong 2 context:**

| Context | "Flight" nghĩa là gì? |
|---|---|
| **Booking** | Chuyến bay khách đặt, có ghế còn trống |
| **Operations** | Chuyến bay vật lý, có crew, fuel, lịch bay |

---

## 3. Cách xác định Bounded Context

### 3.1. 5 dấu hiệu nên tách context

**1. Cùng từ, nghĩa khác nhau**

Nếu 2 nhóm người dùng cùng từ nhưng hiểu khác → cần tách.

```
Sales nói "Order" = đơn khách đặt
Fulfillment nói "Order" = đơn cần đóng gói
→ Tách thành SalesContext.Order và FulfillmentContext.Order
```

**2. Nhóm người dùng khác nhau**

Nếu 2 nhóm user khác nhau (customer vs admin vs shipper) → có thể tách.

**3. Tốc độ thay đổi khác nhau**

Nếu Catalog đổi 10 lần/ngày, Billing đổi 1 lần/tháng → nên tách. Đừng để code chậm chạp kéo code nhanh chậm lại.

**4. Team ownership khác nhau**

Nếu 2 team sở hữu 2 phần → nên tách. Team A không nên chờ Team B deploy.

**5. Yêu cầu phi chức năng khác nhau**

Billing cần ACID, Analytics cần throughput cao → tách.

### 3.2. 3 dấu hiệu KHÔNG nên tách

**1. Cần transaction ACID xuyên suốt**

Nếu business nói *"Chuyển tiền giữa 2 tài khoản phải atomic"* → 2 tài khoản nằm cùng context.

**2. Team quá nhỏ (< 5 người)**

Với team 3 người, tách 5 context là tự sát. 1-2 context là đủ.

**3. Domain chưa rõ ràng**

Nếu chính business còn chưa hiểu rule → tách sớm chỉ tạo ma sát. Đợi đến khi hiểu rồi tách.

### 3.3. Quy tắc ngón tay

> **Nếu 2 khái niệm cần được cập nhật trong CÙNG 1 transaction** → cùng context.
>
> **Nếu 2 khái niệm có thể eventual consistent** → có thể tách.

---

## 4. Bounded Context trong Python

### 4.1. Nguyên tắc: Mỗi context là một package riêng

```
bookstore/
├── src/
│   └── bookstore/
│       ├── catalog/              # ← Bounded Context 1
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── presentation/
│       │
│       ├── order/                # ← Bounded Context 2
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── presentation/
│       │
│       ├── payment/              # ← Bounded Context 3
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── presentation/
│       │
│       └── shared/               # ← Shared kernel (cẩn thận!)
│           └── money.py
```

**Điểm mấu chốt:**

- Mỗi context có **model riêng**.
- **KHÔNG** import class `Product` từ `catalog` sang `order`.
- Nếu cần dữ liệu, dùng **DTO qua API/event**, không share class.

### 4.2. Ví dụ: `Product` ở 2 context

**Catalog context:**

```python
# catalog/domain/model/product.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from decimal import Decimal

from catalog.domain.model.money import Money


@dataclass
class Product:
    """
    Product trong Catalog context.

    Trách nhiệm: thể hiện mặt hàng để BÁN.
    """
    id: UUID
    sku: str
    name: str
    description: str
    price: Money
    images: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    is_published: bool = False

    def publish(self) -> None:
        if not self.name:
            raise ValueError("Không thể publish sản phẩm không có tên")
        self.is_published = True

    def update_price(self, new_price: Money) -> None:
        if new_price.amount <= 0:
            raise ValueError("Giá phải > 0")
        self.price = new_price
```

**Order context:**

```python
# order/domain/model/order_line.py
from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal

from order.domain.model.money import Money


@dataclass(frozen=True)
class ProductSnapshot:
    """
    Snapshot của Product tại thời điểm đặt hàng.

    KHÔNG phải Product của Catalog.
    Chỉ chứa những gì Order cần biết.
    """
    sku: str
    name: str          # để hiển thị trên hóa đơn
    unit_price: Money  # giá tại thời điểm đặt


@dataclass
class OrderLine:
    product_snapshot: ProductSnapshot
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.product_snapshot.unit_price * self.quantity
```

**Chú ý:**

- `ProductSnapshot` **không có** `description`, `images`, `categories`.
- **Không share class** giữa 2 context.
- **Có 2 class `Money` khác nhau** (mỗi context tự định nghĩa) — điều này **đúng**, không phải trùng lặp.

> 💡 **Tại sao không share `Money`?** Vì Catalog có thể cần `compare_to()`, Order có thể cần `allocate_proportionally()`. Để chúng phát triển độc lập. Nếu 2 context thực sự cần **cùng** `Money` không đổi → đưa vào **Shared Kernel**.

### 4.3. Giao tiếp giữa các context

**Cách 1: Đồng bộ (sync) — qua API**

```python
# order/infrastructure/catalog_client.py
import httpx

from order.domain.model.product_snapshot import ProductSnapshot
from order.domain.model.money import Money


class CatalogClient:
    """Client gọi API của Catalog context."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def get_product_snapshot(self, sku: str) -> ProductSnapshot:
        response = httpx.get(f"{self._base_url}/products/{sku}")
        response.raise_for_status()
        data = response.json()
        return ProductSnapshot(
            sku=data["sku"],
            name=data["name"],
            unit_price=Money(Decimal(data["price"]), data["currency"]),
        )
```

**Cách 2: Bất đồng bộ (async) — qua event**

```python
# catalog/domain/events/product_events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ProductPriceChanged(DomainEvent):
    sku: str = ""
    old_price: Decimal = Decimal("0")
    new_price: Decimal = Decimal("0")
    currency: str = "VND"
```

```python
# order/infrastructure/handlers/product_price_changed_handler.py
class ProductPriceChangedHandler:
    """Order lắng nghe event từ Catalog để cập nhật cache giá."""

    def __init__(self, price_cache) -> None:
        self._cache = price_cache

    def handle(self, event: ProductPriceChanged) -> None:
        self._cache.update(event.sku, event.new_price, event.currency)
```

**Cách 3: Chia sẻ database (KHÔNG khuyến nghị)**

Chỉ dùng khi 2 context thực sự không thể tách DB. Nhưng đây là **anti-pattern** — sẽ gây coupling chặt.

---

## 5. Context Mapping — 5 pattern tích hợp

Khi có nhiều Bounded Context, chúng cần giao tiếp. Có 5 pattern chính:

### 5.1. Shared Kernel

**Ý tưởng:** 2 context chia sẻ một phần model chung.

```
┌─────────────┐     ┌─────────────┐
│  Catalog    │     │   Order     │
│             │     │             │
│      ┌──────┴─────┴──────┐      │
│      │  Shared Kernel    │      │
│      │  - Money          │      │
│      │  - SKU            │      │
│      └──────┬─────┬──────┘      │
│             │     │             │
└─────────────┘     └─────────────┘
```

**Ví dụ:**

```python
# shared/domain/money.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Shared Kernel — dùng chung giữa nhiều context.
    CẢNH BÁO: thay đổi class này ảnh hưởng MỌI context.
    """
    amount: Decimal
    currency: str = "VND"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Khác loại tiền tệ")
        return Money(self.amount + other.amount, self.currency)
```

**Khi nào dùng:** Rất hạn chế. Chỉ khi khái niệm thực sự không đổi (Money, DateRange, UUID).

**Nguy hiểm:** 2 team phải coordinate mọi thay đổi. Chỉ dùng cho team nhỏ.

### 5.2. Customer / Supplier

**Ý tưởng:** Context A (supplier) cung cấp dữ liệu cho Context B (customer). B phụ thuộc A.

```
┌──────────┐   upstream   ┌──────────┐
│ Catalog  │ ───────────▶ │  Order   │
│(supplier)│              │(customer)│
└──────────┘              └──────────┘
```

**Ví dụ:** Order cần lấy giá từ Catalog.

```python
class CatalogClient:
    def get_price(self, sku: str) -> Money:
        ...
```

**Khi nào dùng:** Khi B thực sự cần dữ liệu từ A, và A có thể đáp ứng yêu cầu của B.

### 5.3. Conformist

**Ý tưởng:** B chấp nhận model của A **nguyên xi**, không cố gắng chuyển đổi.

```
┌──────────┐              ┌──────────┐
│ Catalog  │ ───────────▶ │Analytics │
│(upstream)│              │(downstr.)│
└──────────┘              └──────────┘
      │                          │
      │                          │
      └─── dùng model của A ─────┘
```

**Ví dụ:** Analytics chấp nhận model của Catalog vì team Analytics không đủ sức thương lượng.

**Khi nào dùng:** Khi A không quan tâm B, và B thấy model của A chấp nhận được.

**Nguy hiểm:** B mất tự chủ. Nếu A đổi, B phải đổi theo.

### 5.4. Anti-Corruption Layer (ACL) — Quan trọng nhất

**Ý tưởng:** B tự bảo vệ khỏi model của A bằng cách **dịch** model A thành model B.

```
┌──────────┐              ┌──────────────────────┐
│ Catalog  │ ───────────▶ │  ACL  ──▶  Order     │
│(upstream)│              │  (dịch)   (model B)  │
└──────────┘              └──────────────────────┘
```

**Ví dụ:**

```python
# order/infrastructure/acl/catalog_acl.py
from decimal import Decimal
from order.domain.model.product_snapshot import ProductSnapshot
from order.domain.model.money import Money
from order.infrastructure.catalog_client import CatalogClient


class CatalogACL:
    """
    Anti-Corruption Layer — dịch model của Catalog sang model của Order.

    Mục đích: Order KHÔNG bị ảnh hưởng khi Catalog đổi schema.
    """

    def __init__(self, client: CatalogClient) -> None:
        self._client = client

    def fetch_product_snapshot(self, sku: str) -> ProductSnapshot:
        raw = self._client.get_raw_product(sku)   # dict thô

        # Dịch thủ công
        return ProductSnapshot(
            sku=raw["product_code"],          # Catalog dùng "product_code"
            name=raw["display_name"],          # Catalog dùng "display_name"
            unit_price=Money(
                amount=Decimal(raw["price"]["value"]),
                currency=raw["price"]["currency_code"],
            ),
        )
```

**Khi nào dùng:** **Hầu hết mọi trường hợp** khi downstream cần tự bảo vệ. Đây là **pattern quan trọng nhất** của context mapping.

**Lợi ích:**
- Catalog đổi `product_code` thành `sku` → chỉ sửa ACL.
- Catalog đổi cấu trúc `price` từ số → object → chỉ sửa ACL.
- Order context không bị ảnh hưởng gì.

### 5.5. Published Language

**Ý tưởng:** Định nghĩa một **ngôn ngữ chuẩn** để trao đổi giữa các context.

**Ví dụ:** Dùng JSON Schema hoặc Protobuf.

```protobuf
// events/product_price_changed.proto
message ProductPriceChanged {
  string sku = 1;
  string currency = 2;
  string old_price = 3;
  string new_price = 4;
  int64 occurred_at = 5;
}
```

**Khi nào dùng:** Khi có nhiều consumer, cần format ổn định.

### 5.6. Bảng tổng hợp

| Pattern | Quan hệ | Khi nào dùng |
|---|---|---|
| **Shared Kernel** | Bình đẳng | Ít, team nhỏ, khái niệm không đổi |
| **Customer/Supplier** | Upstream-Downstream | Downstream cần dữ liệu |
| **Conformist** | Upstream-Downstream | Downstream yếu, chấp nhận model upstream |
| **ACL** | Upstream-Downstream | Downstream muốn tự bảo vệ |
| **Published Language** | Nhiều consumer | Cần format chuẩn |

---

## 6. Context Map — Vẽ bản đồ hệ thống

**Context Map** là sơ đồ các context + quan hệ giữa chúng.

### 6.1. Ví dụ: Hệ thống thương mại điện tử

```
                        ┌─────────────┐
                        │   Catalog   │
                        │   (san phẩm)│
                        └──────┬──────┘
                               │
                        Published Language
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌─────────────┐ ┌────────────┐ ┌─────────────┐
        │   Order     │ │ Inventory  │ │  Pricing    │
        │ (đơn hàng)  │ │ (kho)      │ │ (giá)       │
        └──────┬──────┘ └────────────┘ └─────────────┘
               │
               │ ACL
               │
               ▼
        ┌─────────────┐
        │  Payment    │
        │ (thanh toán)│
        └─────────────┘

        ┌─────────────┐
        │  Shipping   │  ← Đọc Order qua ACL
        │ (giao hàng) │
        └─────────────┘
```

### 6.2. Ví dụ: Hệ thống ngân hàng

```
        ┌─────────────┐
        │  Customer   │  Shared Kernel: CustomerId, Money
        │  (KYC)      │
        └──────┬──────┘
               │
               │ Customer/Supplier
               │
    ┌──────────┼──────────┬─────────────┐
    │          │          │             │
    ▼          ▼          ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌─────────────┐
│Account │ │  Loan  │ │  Card  │ │ Transaction │
│(tài    │ │(vay)   │ │(thẻ)   │ │(giao dịch)  │
│khoản)  │ └────────┘ └────────┘ └─────────────┘
└────────┘
    │
    │ ACL
    ▼
┌─────────────┐
│  Reporting  │
│  (báo cáo)  │
└─────────────┘
```

### 6.3. Cách vẽ context map

**Bước 1:** Liệt kê tất cả context.

**Bước 2:** Với mỗi cặp context, xác định:
- Ai upstream, ai downstream?
- Pattern nào? (ACL, Conformist, Shared Kernel...)

**Bước 3:** Vẽ.

**Bước 4:** Đánh dấu **team ownership** — team nào sở hữu context nào.

**Bước 5:** Đánh dấu **hotspots** — chỗ nào còn mơ hồ, cần bàn thêm.

---

## 7. Áp dụng vào Python: Multi-context project

### 7.1. Cấu trúc project

```
shop/
├── pyproject.toml
├── src/
│   └── shop/
│       ├── __init__.py
│       │
│       ├── shared/                       # ← Shared Kernel (rất nhỏ)
│       │   ├── __init__.py
│       │   └── domain/
│       │       ├── money.py
│       │       └── ids.py
│       │
│       ├── catalog/                      # ← Bounded Context 1
│       │   ├── __init__.py
│       │   ├── domain/
│       │   │   ├── model/
│       │   │   │   ├── product.py
│       │   │   │   └── category.py
│       │   │   ├── services/
│       │   │   ├── repositories/
│       │   │   └── events/
│       │   ├── application/
│       │   │   ├── commands/
│       │   │   └── queries/
│       │   ├── infrastructure/
│       │   │   └── persistence/
│       │   └── presentation/
│       │       └── api/
│       │
│       ├── order/                        # ← Bounded Context 2
│       │   ├── domain/
│       │   │   ├── model/
│       │   │   │   ├── order.py
│       │   │   │   ├── order_line.py
│       │   │   │   └── product_snapshot.py
│       │   │   └── services/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   │   ├── acl/
│       │   │   │   └── catalog_acl.py    # ← ACL
│       │   │   └── persistence/
│       │   └── presentation/
│       │
│       └── payment/                      # ← Bounded Context 3
│           ├── domain/
│           ├── application/
│           ├── infrastructure/
│           └── presentation/
│
└── tests/
    ├── shared/
    ├── catalog/
    ├── order/
    └── payment/
```

### 7.2. Quy tắc import

**Trong cùng context:** tự do.

```python
# order/application/commands/place_order.py
from shop.order.domain.model.order import Order
from shop.order.domain.repositories.order_repository import OrderRepository
```

**Giữa các context:** **CHỈ** qua ACL hoặc Shared Kernel.

```python
# ✅ ĐÚNG: order dùng ACL để gọi catalog
from shop.order.infrastructure.acl.catalog_acl import CatalogACL

# ✅ ĐÚNG: order dùng Shared Kernel
from shop.shared.domain.money import Money

# ❌ SAI: import trực tiếp domain của catalog
from shop.catalog.domain.model.product import Product   # PHÁ VỠ!
```

### 7.3. Enforce bằng import-linter

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["shop"]

# Quy tắc 1: Không ai import domain của context khác
[[tool.importlinter.contracts]]
name = "Catalog domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.order", "shop.payment"]
forbidden_modules = ["shop.catalog.domain"]

[[tool.importlinter.contracts]]
name = "Order domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.catalog", "shop.payment"]
forbidden_modules = ["shop.order.domain"]

[[tool.importlinter.contracts]]
name = "Payment domain không bị import bởi context khác"
type = "forbidden"
source_modules = ["shop.catalog", "shop.order"]
forbidden_modules = ["shop.payment.domain"]

# Quy tắc 2: Shared Kernel chỉ chứa model đơn giản
[[tool.importlinter.contracts]]
name = "Shared kernel không import context nào"
type = "forbidden"
source_modules = ["shop.shared"]
forbidden_modules = ["shop.catalog", "shop.order", "shop.payment"]
```

**Từ giờ, nếu ai đó viết:**

```python
from shop.catalog.domain.model.product import Product   # trong order/
```

→ `make check` **fail ngay**.

### 7.4. ACL đầy đủ

```python
# order/infrastructure/acl/catalog_acl.py
from decimal import Decimal

from shop.order.domain.model.product_snapshot import ProductSnapshot
from shop.shared.domain.money import Money


class CatalogACL:
    """
    Anti-Corruption Layer — bảo vệ Order khỏi model của Catalog.

    Trách nhiệm:
    - Gọi API/client của Catalog.
    - Dịch response thô sang model của Order.
    - Nếu Catalog đổi schema → chỉ sửa file này.
    """

    def __init__(self, http_client) -> None:
        self._client = http_client

    def fetch_product_snapshot(self, sku: str) -> ProductSnapshot:
        # Gọi HTTP
        raw = self._client.get(f"http://catalog-api/products/{sku}")

        # Dịch thủ công — không dùng dict trực tiếp
        return ProductSnapshot(
            sku=raw["product_code"],
            name=raw["display_name"],
            unit_price=Money(
                amount=Decimal(raw["price"]["amount"]),
                currency=raw["price"]["currency"],
            ),
        )

    def fetch_products_bulk(self, skus: list[str]) -> dict[str, ProductSnapshot]:
        raw_list = self._client.post(
            "http://catalog-api/products/bulk",
            json={"skus": skus},
        )
        return {
            item["product_code"]: self._to_snapshot(item)
            for item in raw_list
        }

    def _to_snapshot(self, raw: dict) -> ProductSnapshot:
        return ProductSnapshot(
            sku=raw["product_code"],
            name=raw["display_name"],
            unit_price=Money(
                amount=Decimal(raw["price"]["amount"]),
                currency=raw["price"]["currency"],
            ),
        )
```

### 7.5. Application handler dùng ACL

```python
# order/application/commands/place_order.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shop.order.domain.model.order import Order
from shop.order.domain.model.money import Money
from shop.order.domain.repositories.order_repository import OrderRepository
from shop.order.infrastructure.acl.catalog_acl import CatalogACL


@dataclass(frozen=True)
class OrderItemInput:
    sku: str
    quantity: int


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]


class PlaceOrderHandler:
    def __init__(
        self,
        order_repo: OrderRepository,
        catalog_acl: CatalogACL,
    ) -> None:
        self._order_repo = order_repo
        self._catalog_acl = catalog_acl

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        order = Order.create(customer_id=cmd.customer_id)

        for item in cmd.items:
            # Dùng ACL — không import gì từ catalog.domain
            snapshot = self._catalog_acl.fetch_product_snapshot(item.sku)
            order.add_product(snapshot, item.quantity)

        self._order_repo.save(order)
        return order.id
```

**Điểm mấu chốt:** `PlaceOrderHandler` **không biết** Catalog có class `Product` nào. Nó chỉ biết `ProductSnapshot` của chính nó.

---

## 8. Khi nào tách, khi nào gộp? — Case study

### 8.1. Case study 1: Hệ thống blog

**Câu hỏi:** Có nên tách `Blog` và `Comment` thành 2 context?

**Phân tích:**

- Cùng team viết, cùng tốc độ thay đổi.
- Comment **cần** Post tồn tại (không thể comment vào post không có).
- Không cần eventual consistent — comment phải hiện ngay.
- Team nhỏ (2-3 người).

**Kết luận:** **Không tách.** `Post` là Aggregate Root, `Comment` là Entity con.

### 8.2. Case study 2: Hệ thống thương mại điện tử

**Câu hỏi:** Có nên tách `Catalog` và `Order` thành 2 context?

**Phân tích:**

- Catalog đổi hàng ngày (thêm sản phẩm, sửa giá).
- Order đổi chậm (rule đặt hàng ổn định).
- Catalog có 5 người, Order có 3 người.
- Order **cần** snapshot giá tại thời điểm đặt → không cần real-time.
- Có thể eventual consistent.

**Kết luận:** **Tách.** Order dùng ACL để lấy snapshot.

### 8.3. Case study 3: Hệ thống ngân hàng

**Câu hỏi:** Có nên tách `Account` và `Transaction` thành 2 context?

**Phân tích:**

- Transaction luôn gắn với Account.
- Chuyển tiền giữa 2 account phải atomic.
- Nếu tách, cần distributed transaction — phức tạp.
- Cùng team có thể quản lý cả 2.

**Kết luận:** **Không tách.** `Account` là Aggregate Root, `Transaction` là Entity con.

### 8.4. Bảng quyết định

| Câu hỏi | Tách | Gộp |
|---|---|---|
| Cùng từ, nghĩa khác? | ✅ | |
| Team khác nhau? | ✅ | |
| Tốc độ thay đổi khác? | ✅ | |
| Cần ACID xuyên suốt? | | ✅ |
| Team < 5 người? | | ✅ |
| Domain chưa rõ? | | ✅ |
| Eventual consistent OK? | ✅ | |

---

## 9. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Xác định context cho hệ thống bệnh viện

Cho hệ thống quản lý bệnh viện, xác định 4-5 Bounded Context. Với mỗi context:

- Tên context.
- Trách nhiệm chính (1-2 câu).
- 5 khái niệm cốt lõi.
- Team nào sở hữu (giả định).

**Gợi ý:** Nghĩ đến: Khám bệnh, Xét nghiệm, Dược, Thanh toán, Hồ sơ bệnh án.

### 🟡 Bài tập 2 (trung bình): Cùng từ, nghĩa khác

Cho 5 từ sau, với mỗi từ hãy liệt kê **3 context khác nhau** và nghĩa của từ đó trong mỗi context:

1. `User`
2. `Ticket`
3. `Payment`
4. `Report`
5. `Notification`

Ví dụ với `Ticket`:

- **Support context:** Yêu cầu hỗ trợ của khách hàng.
- **Event context:** Vé vào sự kiện.
- **Travel context:** Vé máy bay/tàu.

### 🔴 Bài tập 3 (khó): Vẽ Context Map + code

Cho hệ thống **"đặt vé xem phim"** với các context:

- `Movies` (danh mục phim)
- `Cinemas` (rạp, phòng, ghế)
- `Showtimes` (suất chiếu)
- `Bookings` (đặt vé)
- `Payments` (thanh toán)
- `Notifications` (thông báo)

**Yêu cầu:**

1. Vẽ Context Map (ASCII hoặc dùng [Mermaid](https://mermaid.live/)).
2. Với mỗi cặp context có quan hệ, xác định pattern (ACL, Shared Kernel, Conformist...).
3. Code Python cho ít nhất:
   - `Bookings` context với Aggregate `Booking`.
   - `Movies` context với Aggregate `Movie`.
   - ACL từ `Bookings` sang `Movies` và `Showtimes`.
4. Viết ít nhất 15 test cho domain.
5. Setup `import-linter` chặn import giữa các context.

---

## 10. Tóm tắt bài 4

| Điểm | Nội dung |
|---|---|
| **Bounded Context** | Ranh giới trong đó một model có nghĩa nhất quán |
| **Vấn đề gốc** | Cùng từ có nghĩa khác ở context khác — không nên ép đồng nhất |
| **Dấu hiệu tách** | Cùng từ khác nghĩa, team khác, tốc độ khác, ownership khác |
| **Dấu hiệu gộp** | Cần ACID, team nhỏ, domain chưa rõ |
| **5 pattern tích hợp** | Shared Kernel, Customer/Supplier, Conformist, ACL, Published Language |
| **ACL là quan trọng nhất** | Bảo vệ downstream khỏi upstream |
| **Python: 1 context = 1 package** | Không import chéo `domain` |
| **Enforce bằng import-linter** | Ngăn vi phạm ngay từ đầu |
| **Context Map** | Sơ đồ hóa quan hệ giữa các context |

**Câu thần chú:** *"Đừng cố làm một model khổng lồ. Hãy để mỗi context có model của riêng nó."*

---

## 11. Chuẩn bị cho bài 5

Bài tiếp theo: **Value Object — Bất biến là sức mạnh**.

Chuẩn bị:
- Đọc lại phần Value Object trong bài 1 (Password).
- Nghĩ về **3-5 VO** trong domain bạn đang làm.
- Sẽ bàn: `frozen=True` chi tiết, khi nào VO, khi nào Entity, các method magic (`__add__`, `__eq__`, `__hash__`), và cách viết VO "chuẩn DDD".

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 5** ngay.
3. **Viết code mẫu đầy đủ** cho bài tập 3 (đặt vé xem phim) — đây là bài tập lớn, tôi có thể code từng file.
4. **Đào sâu** một phần: ACL chi tiết, Shared Kernel khi nào dùng, Event-driven giữa context.
5. **Vẽ Context Map** cho domain bạn đang làm — nếu bạn cho tôi biết domain đó là gì.

Nói tôi biết bạn muốn gì nhé.