# 📖 Bài 11: Application Service & CQRS

> Bài 10 dạy bạn **kiến trúc 4 tầng**. Bài 11 đi sâu vào **tầng Application** — nơi orchestration diễn ra. Bạn sẽ học **CQRS** (Command Query Responsibility Segregation) — tách write model khỏi read model. Đây là kỹ thuật giúp hệ thống **scale** và **đơn giản hóa** cùng lúc, nhưng cũng là **con dao hai lưỡi** nếu dùng sai chỗ.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Application Service** là gì và **không là gì**.
2. Phân biệt rõ **Command** vs **Query**.
3. Hiểu **CQRS** là gì và tại sao cần.
4. Biết **khi nào dùng**, **khi nào không dùng** CQRS.
5. Viết **Command Handler** đúng chuẩn (mỏng, orchestration).
6. Viết **Query Handler** đúng chuẩn (đọc thẳng DB, không qua Domain).
7. Biết 3 mức độ CQRS: **single DB**, **read replica**, **event-sourced**.
8. Tránh được **8 anti-pattern** khi dùng Application Service / CQRS.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Application Service là gì?

### 1.1. Định nghĩa

> **Application Service** là một class/function **điều phối** các Domain object để thực hiện **một use case** cụ thể. Nó **không chứa business rule** — chỉ orchestration: mở transaction, load Aggregate, gọi method, save, commit.

### 1.2. Trực giác

Hãy nghĩ về **nhạc trưởng**:

- Nhạc trưởng **không chơi** nhạc cụ nào.
- Nhạc trưởng **điều phối** các nhạc công (Domain).
- Nhạc trưởng biết **khi nào** vĩ cầm vào, **khi nào** trống đánh.
- Nhạc trưởng **không viết** nốt nhạc.

Application Service chính là nhạc trưởng. Domain là nhạc công.

### 1.3. Đặc điểm

| Đặc điểm | Ý nghĩa |
|---|---|
| **Orchestration** | Điều phối, không chứa logic |
| **Mỏng** | 10-30 dòng/handler |
| **1 use case / handler** | `PlaceOrderHandler`, `CancelOrderHandler` |
| **Transaction boundary** | Mở/commit UoW |
| **Không biết Infrastructure** | Chỉ biết Port (interface) |
| **Không biết Presentation** | Trả về DTO hoặc ID, không HTTP |

### 1.4. Application Service **không** là gì?

| Không là | Lý do |
|---|---|
| **Business logic** | Đó là Domain |
| **Repository** | Đó là Infrastructure |
| **Controller** | Đó là Presentation |
| **Model** | Đó là Domain |
| **Transaction manager** | Đó là UoW |
| **Validation phức tạp** | Đó là Domain |

**Câu hỏi test:** Nếu Application Service có `if/else` phức tạp về nghiệp vụ → **SAI**. Đẩy vào Domain.

---

## 2. Command vs Query

Đây là **phân biệt cốt lõi** của CQRS.

### 2.1. Định nghĩa

> **Command** = thao tác **thay đổi** state. Không trả về dữ liệu (chỉ trả về ID hoặc void).
>
> **Query** = thao tác **đọc** state. Không thay đổi gì. Trả về dữ liệu.

### 2.2. Bảng so sánh

| Tiêu chí | Command | Query |
|---|---|---|
| **Mục đích** | Thay đổi state | Đọc state |
| **Trả về** | ID / void | DTO / list DTO |
| **Transaction** | Cần UoW | Không cần |
| **Đi qua Domain** | Có (Aggregate) | Không (đọc thẳng DB) |
| **Side effect** | Có (event, email...) | Không |
| **Idempotent** | Không (thường) | Có |
| **Validation** | Qua Domain | Qua schema |
| **Ví dụ** | `PlaceOrder`, `CancelOrder` | `GetOrderSummary`, `ListOrders` |

### 2.3. Tại sao phải tách?

**Lý do 1: Trách nhiệm rõ ràng.**

```python
# ❌ SAI: Trộn lẫn
class OrderService:
    def place_order(self, ...) -> Order:   # Command trả về Order?
        ...
    def get_order(self, ...) -> Order:     # Query trả về Entity?
        ...
```

**Lý do 2: Query tối ưu khác Command.**

- Command cần **invariant**, chạy qua Domain.
- Query cần **tốc độ**, đọc thẳng DB với JOIN, aggregation.

**Lý do 3: Scale độc lập.**

- Write: ít, cần ACID, dùng Postgres.
- Read: nhiều, cần cache, dùng read replica hoặc Elasticsearch.

**Lý do 4: Không trả Entity ra ngoài.**

Nếu Query trả Entity → client có thể mutate → phá vỡ Domain.

### 2.4. Nguyên tắc

> **"Hỏi không được thay đổi câu trả lời."** — Bertrand Meyer (CQS)

Command **không** trả dữ liệu (trừ ID). Query **không** thay đổi state.

**Kiểm tra:**

```python
# ❌ SAI: Command trả về dữ liệu
def place_order(cmd) -> Order:   # Trả về cả Order!
    ...

# ✅ ĐÚNG: Command trả về ID
def place_order(cmd) -> UUID:
    ...
```

---

## 3. CQRS là gì?

### 3.1. Định nghĩa

> **CQRS** (Command Query Responsibility Segregation) = **tách biệt** mô hình ghi (write model) và mô hình đọc (read model). Không chỉ tách method — mà tách **cả class, cả schema, đôi khi cả database**.

### 3.2. Ba mức độ CQRS

CQRS có **3 mức độ**, từ đơn giản đến phức tạp:

**Mức 1: Tách class (CQRS nhẹ)**

- Cùng DB, cùng schema.
- Chỉ tách **class**: `PlaceOrderHandler` vs `OrderSummaryQuery`.
- Đây là mức **khuyến nghị** cho 90% dự án.

**Mức 2: Tách read model (CQRS vừa)**

- Cùng DB, **khác bảng/view**.
- Write: bảng `orders`, `order_lines` (normalized).
- Read: view `order_summary` (denormalized).
- Update read model qua trigger hoặc event handler.

**Mức 3: Tách database (CQRS nặng)**

- Write: Postgres.
- Read: Elasticsearch / MongoDB / Redis.
- Sync qua event bus (async).
- **Eventual consistent**.

### 3.3. Sơ đồ 3 mức độ

```
MỨC 1: CQRS nhẹ
┌──────────┐         ┌──────────┐
│ Command  │         │  Query   │
│ Handler  │         │ Handler  │
└────┬─────┘         └────┬─────┘
     │                    │
     └────────┬───────────┘
              ▼
         ┌────────┐
         │   DB   │
         └────────┘

MỨC 2: CQRS vừa
┌──────────┐         ┌──────────┐
│ Command  │         │  Query   │
│ Handler  │         │ Handler  │
└────┬─────┘         └────┬─────┘
     │                    │
     ▼                    ▼
┌─────────┐         ┌──────────┐
│ Tables  │─event──▶│  Views   │
└─────────┘         └──────────┘
     │                    │
     └────────┬───────────┘
              ▼
         ┌────────┐
         │   DB   │
         └────────┘

MỨC 3: CQRS nặng
┌──────────┐         ┌──────────┐
│ Command  │         │  Query   │
│ Handler  │         │ Handler  │
└────┬─────┘         └────┬─────┘
     │                    │
     ▼                    ▼
┌─────────┐  event  ┌──────────┐
│Postgres │────────▶│Elastic / │
│         │  bus    │  Mongo   │
└─────────┘         └──────────┘
```

### 3.4. Khi nào dùng CQRS?

**Dùng khi:**

- Read và write có **tần suất rất khác nhau** (VD: 1000 read/1 write).
- Read cần **JOIN phức tạp**, write cần **invariant chặt**.
- Cần **scale read** độc lập (read replica, cache).
- UI cần **view riêng** (denormalized).
- Có **nhiều loại read** khác nhau cho cùng data.

**KHÔNG dùng khi:**

- CRUD đơn giản.
- Read và write tương đương.
- Team nhỏ, chưa cần scale.
- Chưa có vấn đề performance.

> ⚠️ **Cảnh báo:** CQRS nặng (mức 3) **rất phức tạp**. Nó cần event bus, eventual consistency, retry, idempotency. Đừng dùng nếu chưa cần.

---

## 4. Viết Command Handler

### 4.1. Bộ khung

```python
# application/commands/place_order.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from shop.application.uow import UnitOfWork
from shop.application.exceptions import CustomerNotFound
from shop.domain.model.order import Order
from shop.domain.model.order_line import OrderLine
from shop.shared.domain.money import Money


# ---- Command ----
@dataclass(frozen=True)
class OrderItemInput:
    product_id: UUID
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]


# ---- Handler ----
class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            # 1. Load aggregate cần thiết
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            # 2. Tạo aggregate
            order = Order.create(cmd.customer_id)

            # 3. Gọi business method
            for item in cmd.items:
                order.add_line(
                    OrderLine.create(
                        product_id=item.product_id,
                        unit_price=Money(
                            item.unit_price_amount,
                            item.unit_price_currency,
                        ),
                        quantity=item.quantity,
                    )
                )
            order.place()

            # 4. Save
            self._uow.orders.save(order)

            # 5. Commit
            self._uow.commit()

        return order.id
```

**Điểm mấu chốt:**

- Command là **dataclass frozen** — bất biến.
- Handler **mỏng** (~20 dòng).
- Business rule trong `Order.place()`.
- Trả về **ID**, không trả Order.
- Commit trong UoW.

### 4.2. Command không có logic

```python
# ❌ SAI: Command có logic
@dataclass
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]

    def validate(self) -> None:   # Validation ở Command?
        if not self.items:
            raise ValueError("Empty")

    def total(self) -> Decimal:   # Tính toán ở Command?
        return sum(i.price * i.quantity for i in self.items)
```

```python
# ✅ ĐÚNG: Command chỉ là data
@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]
```

### 4.3. Handler không chứa business rule

```python
# ❌ SAI: Business rule ở Handler
class PlaceOrderHandler:
    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        # Business rule ở đây!
        if len(cmd.items) > 100:
            raise TooManyItems()

        if sum(i.quantity for i in cmd.items) > 1000:
            raise TooManyTotalQuantity()

        if customer.is_suspended():
            raise CustomerSuspended()

        order = Order.create(cmd.customer_id)
        ...
```

```python
# ✅ ĐÚNG: Business rule ở Domain
class Order:
    MAX_LINES = 100

    def add_line(self, line: OrderLine) -> None:
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines(self.id)
        self._lines[line.id] = line
```

Handler chỉ còn orchestration:

```python
class PlaceOrderHandler:
    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))
            order.place()

            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

### 4.4. Handler có thể gọi nhiều Repository

```python
class TransferMoneyHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: TransferCommand) -> None:
        with self._uow:
            source = self._uow.accounts.find_by_id(cmd.from_account_id)
            target = self._uow.accounts.find_by_id(cmd.to_account_id)

            if not source or not target:
                raise AccountNotFound()

            # Business rule: TransferService (domain service)
            self._uow.transfer_service.transfer(
                source, target, cmd.amount
            )

            self._uow.accounts.save(source)
            self._uow.accounts.save(target)
            self._uow.commit()
```

**Chú ý:** Transfer logic nằm trong `TransferService` (Domain Service), không ở Handler.

---

## 5. Viết Query Handler

### 5.1. Bộ khung

Query **không** đi qua Domain. Đọc thẳng DB.

```python
# application/queries/order_summary.py
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


# ---- DTO ----
@dataclass(frozen=True)
class OrderSummaryDTO:
    order_id: UUID
    customer_id: UUID
    total_amount: str
    status: str
    line_count: int
    created_at: str


# ---- Query ----
class OrderSummaryQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT
                    o.id AS order_id,
                    o.customer_id,
                    COALESCE(
                        SUM(l.unit_price_amount * l.quantity), 0
                    ) AS total_amount,
                    o.status,
                    COUNT(l.id) AS line_count,
                    o.created_at
                FROM orders o
                LEFT JOIN order_lines l ON l.order_id = o.id
                WHERE o.customer_id = :cid
                GROUP BY o.id, o.customer_id, o.status, o.created_at
                ORDER BY o.created_at DESC
            """),
            {"cid": str(customer_id)},
        ).fetchall()

        return [
            OrderSummaryDTO(
                order_id=row.order_id,
                customer_id=row.customer_id,
                total_amount=str(row.total_amount),
                status=row.status,
                line_count=row.line_count,
                created_at=str(row.created_at),
            )
            for row in rows
        ]
```

**Điểm mấu chốt:**

- Query **không** qua Domain.
- **Không** dùng UoW (không cần transaction).
- Đọc thẳng DB bằng raw SQL hoặc ORM query.
- Trả về **DTO** — không phải Entity.
- DTO **frozen** — bất biến.

### 5.2. DTO không phải Domain

```python
# ❌ SAI: Query trả Entity
def get_order(self, order_id: UUID) -> Order:
    return self._session.get(OrderRow, order_id)
    # Client có thể mutate Order!
```

```python
# ✅ ĐÚNG: Query trả DTO
@dataclass(frozen=True)
class OrderDetailDTO:
    order_id: UUID
    status: str
    total: str
    lines: list[LineDTO]
```

### 5.3. Query tối ưu

**1. Dùng raw SQL cho query phức tạp.**

ORM query thường không đủ tốt cho JOIN nhiều bảng.

```python
rows = session.execute(text("""
    SELECT o.id, c.name, SUM(...)
    FROM orders o
    JOIN customers c ON c.id = o.customer_id
    GROUP BY o.id, c.name
""")).fetchall()
```

**2. Denormalize khi cần.**

Nếu query quá chậm, tạo **read model** (bảng riêng, view materialized).

```sql
CREATE MATERIALIZED VIEW order_summary AS
SELECT
    o.id AS order_id,
    o.customer_id,
    SUM(l.unit_price_amount * l.quantity) AS total,
    o.status,
    COUNT(l.id) AS line_count
FROM orders o
LEFT JOIN order_lines l ON l.order_id = o.id
GROUP BY o.id, o.customer_id, o.status;
```

**3. Cache khi cần.**

```python
class CachedOrderSummaryQuery:
    def __init__(self, session: Session, cache: Cache) -> None:
        self._session = session
        self._cache = cache

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        cache_key = f"order_summary:{customer_id}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        result = self._fetch_from_db(customer_id)
        self._cache.set(cache_key, result, ttl=300)
        return result
```

### 5.4. Query trả list vs phân trang

**Không bao giờ** trả **tất cả** rows. Luôn **phân trang**.

```python
@dataclass(frozen=True)
class PageDTO:
    items: list[OrderSummaryDTO]
    total: int
    page: int
    page_size: int


class OrderSummaryQuery:
    def by_customer(
        self,
        customer_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PageDTO:
        offset = (page - 1) * page_size

        # Đếm tổng
        total = self._session.execute(
            text("SELECT COUNT(*) FROM orders WHERE customer_id = :cid"),
            {"cid": str(customer_id)},
        ).scalar() or 0

        # Lấy trang
        rows = self._session.execute(
            text("""
                SELECT ... FROM orders WHERE customer_id = :cid
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"cid": str(customer_id), "limit": page_size, "offset": offset},
        ).fetchall()

        return PageDTO(
            items=[OrderSummaryDTO(...) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )
```

---

## 6. Tổ chức code CQRS

### 6.1. Cấu trúc thư mục

```
application/
├── __init__.py
├── commands/               # Write
│   ├── __init__.py
│   ├── place_order.py
│   ├── cancel_order.py
│   └── ship_order.py
├── queries/                # Read
│   ├── __init__.py
│   ├── order_summary.py
│   ├── order_detail.py
│   └── customer_orders.py
├── dto.py                  # Shared DTOs
├── uow.py                  # UnitOfWork Protocol
├── ports/                  # External interfaces
│   ├── __init__.py
│   ├── email_sender.py
│   └── payment_gateway.py
└── exceptions.py
```

**Quy tắc:**

- `commands/` — mỗi file là 1 Command + Handler.
- `queries/` — mỗi file là 1 Query + DTO.
- `commands/` **không** import `queries/`, và ngược lại.
- Enforce bằng `import-linter`:

```toml
[[tool.importlinter.contracts]]
name = "Commands không import Queries"
type = "independence"
modules = [
    "shop.application.commands",
    "shop.application.queries",
]
```

### 6.2. Mediator Pattern (tùy chọn)

Nhiều người dùng **Mediator** để dispatch Command/Query.

**Không dùng Mediator:**

```python
# presentation/api/routes/orders.py
@router.post("/orders")
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
):
    cmd = PlaceOrderCommand(...)
    order_id = handler.handle(cmd)
    return {"order_id": order_id}
```

**Dùng Mediator:**

```python
# presentation/api/routes/orders.py
@router.post("/orders")
def place_order(
    request: PlaceOrderRequest,
    mediator: Mediator = Depends(get_mediator),
):
    cmd = PlaceOrderCommand(...)
    order_id = mediator.send(cmd)
    return {"order_id": order_id}
```

**Mediator đơn giản:**

```python
# application/mediator.py
from typing import Any, Callable


class Mediator:
    def __init__(self) -> None:
        self._handlers: dict[type, Callable] = {}

    def register(self, command_type: type, handler: Callable) -> None:
        self._handlers[command_type] = handler

    def send(self, command: Any) -> Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise NoHandlerFor(type(command))
        return handler.handle(command)
```

**Ưu / nhược:**

| Mediator | Không Mediator |
|---|---|
| Presentation không cần biết Handler | Presentation biết Handler |
| Thêm 1 lớp gián tiếp | Đơn giản, trực tiếp |
| Dễ thêm cross-cutting (logging, metrics) | Mỗi route tự handle |
| Khó debug hơn | Dễ debug |

**Khuyến nghị:** Với dự án nhỏ, **không cần Mediator**. Với dự án lớn (>50 commands), Mediator đáng dùng.

---

## 7. CQRS nâng cao: Read Model riêng

### 7.1. Vấn đề

Khi write model (normalized) và read model (denormalized) khác nhau **nhiều**, query trở nên phức tạp. Giải pháp: **tách read model**.

### 7.2. Ví dụ: Order Summary read model

**Write model (normalized):**

```
orders: id, customer_id, status, created_at
order_lines: id, order_id, product_id, unit_price, quantity
products: id, name, sku
customers: id, name, email
```

**Read model (denormalized):**

```
order_summary:
  order_id, customer_id, customer_name, total, line_count, status, created_at
```

**Sync qua event handler:**

```python
# infrastructure/read_model/order_summary_projector.py
class OrderSummaryProjector:
    """
    Event handler — update read model khi write model thay đổi.
    """
    def __init__(self, session: Session) -> None:
        self._session = session

    def on_order_placed(self, event: OrderPlaced) -> None:
        self._session.execute(
            text("""
                INSERT INTO order_summary
                (order_id, customer_id, total, line_count, status, created_at)
                VALUES (:oid, :cid, :total, :lines, 'PLACED', :now)
            """),
            {
                "oid": str(event.order_id),
                "cid": str(event.customer_id),
                "total": str(event.total.amount),
                "lines": event.line_count,
                "now": event.occurred_at,
            },
        )
        self._session.commit()

    def on_order_shipped(self, event: OrderShipped) -> None:
        self._session.execute(
            text("UPDATE order_summary SET status = 'SHIPPED' WHERE order_id = :oid"),
            {"oid": str(event.order_id)},
        )
        self._session.commit()
```

**Query đọc trực tiếp read model:**

```python
class OrderSummaryQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT order_id, customer_id, total, line_count, status, created_at
                FROM order_summary
                WHERE customer_id = :cid
                ORDER BY created_at DESC
            """),
            {"cid": str(customer_id)},
        ).fetchall()

        return [OrderSummaryDTO(...) for row in rows]
```

**Điểm mấu chốt:**

- Query **cực nhanh** — đọc 1 bảng duy nhất.
- Write model vẫn normalized → invariant tốt.
- Read model denormalized → fast query.
- Sync qua event → eventual consistency.

### 7.3. Eventual consistency

**Đặc điểm:**

- Sau khi `PlaceOrder` commit, read model **có thể chưa** update ngay.
- Trễ thường **vài chục ms** đến **vài giây**.
- UI cần handle: **"đang cập nhật..."**.

**Ví dụ:**

```python
# Client: place order
order_id = api.place_order(...)
# Client: ngay lập tức query
summary = api.get_order_summary(order_id)   # Có thể chưa có!
```

**Cách xử lý:**

1. **Optimistic UI** — client tự thêm summary dự kiến.
2. **Polling** — client retry sau 500ms.
3. **Version check** — client biết version mới nhất.
4. **Đừng dùng CQRS mức 2 nếu UI cần strong consistency.**

### 7.4. Khi nào dùng read model riêng?

| Tình huống | Dùng |
|---|---|
| Query đơn giản, 1-2 bảng | ❌ Không cần |
| Query JOIN 5+ bảng, chậm | ✅ |
| Read nhiều hơn write 100x | ✅ |
| UI cần data denormalized | ✅ |
| Cần search full-text | ✅ |
| Cần strong consistency | ❌ |

---

## 8. Tám anti-pattern khi dùng Application Service / CQRS

### ❌ Anti-pattern 1: Handler chứa business rule

```python
# ❌ SAI
class PlaceOrderHandler:
    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        if len(cmd.items) > 100:
            raise TooManyItems()
        if sum(i.quantity for i in cmd.items) > 1000:
            raise TooManyTotalQuantity()
        ...
```

```python
# ✅ ĐÚNG
class Order:
    MAX_LINES = 100
    MAX_TOTAL_QUANTITY = 1000

    def add_line(self, line: OrderLine) -> None:
        if len(self._lines) >= self.MAX_LINES:
            raise TooManyLines(self.id)
        if self._total_quantity + line.quantity > self.MAX_TOTAL_QUANTITY:
            raise TooManyTotalQuantity(self.id)
        self._lines[line.id] = line
```

### ❌ Anti-pattern 2: Command trả về Entity

```python
# ❌ SAI
def place_order(cmd: PlaceOrderCommand) -> Order:
    ...
    return order   # Trả về Entity!
```

```python
# ✅ ĐÚNG
def place_order(cmd: PlaceOrderCommand) -> UUID:
    ...
    return order.id
```

### ❌ Anti-pattern 3: Query thay đổi state

```python
# ❌ SAI
class OrderQuery:
    def get_order(self, order_id: UUID) -> OrderDTO:
        order = self._session.get(OrderRow, order_id)
        order.view_count += 1   # Side effect!
        self._session.commit()
        return OrderDTO(...)
```

```python
# ✅ ĐÚNG: Query không side effect
class OrderQuery:
    def get_order(self, order_id: UUID) -> OrderDTO:
        row = self._session.get(OrderRow, order_id)
        return OrderDTO(...)
```

Nếu cần tracking → Command riêng: `IncrementViewCountCommand`.

### ❌ Anti-pattern 4: Query qua Domain

```python
# ❌ SAI: Query qua Aggregate
class OrderQuery:
    def get_summary(self, order_id: UUID) -> OrderSummaryDTO:
        order = self._order_repo.find_by_id(order_id)   # Load cả aggregate
        return OrderSummaryDTO(
            order_id=order.id,
            total=str(order.total),
            ...
        )
```

```python
# ✅ ĐÚNG: Query đọc thẳng DB
class OrderQuery:
    def get_summary(self, order_id: UUID) -> OrderSummaryDTO:
        row = self._session.execute(
            text("SELECT ... FROM order_summary WHERE order_id = :oid"),
            {"oid": str(order_id)},
        ).fetchone()
        return OrderSummaryDTO(...)
```

### ❌ Anti-pattern 5: Handler quá lớn

```python
# ❌ SAI: Handler 200 dòng
class PlaceOrderHandler:
    def handle(self, cmd):
        # 200 dòng orchestration + business rule + validation
        ...
```

```python
# ✅ ĐÚNG: Chia nhỏ
class PlaceOrderHandler:
    def __init__(self, uow, pricing_service):
        self._uow = uow
        self._pricing = pricing_service

    def handle(self, cmd):
        with self._uow:
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))

            # Delegation cho domain service
            self._pricing.apply_discounts(order, customer)

            order.place()
            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

### ❌ Anti-pattern 6: Query trả Entity

```python
# ❌ SAI
def get_orders(self, customer_id) -> list[Order]:
    return [OrderMapper.to_domain(row) for row in rows]
```

Client có thể mutate. Và performance kém (load cả aggregate).

```python
# ✅ ĐÚNG
def get_orders(self, customer_id) -> list[OrderSummaryDTO]:
    ...
```

### ❌ Anti-pattern 7: Dùng CQRS khi không cần

```python
# ❌ SAI: CQRS cho CRUD đơn giản
class CreateTodoHandler:
    def handle(self, cmd: CreateTodoCommand) -> UUID:
        ...
class GetTodoQuery:
    def get(self, todo_id) -> TodoDTO:
        ...
class ListTodosQuery:
    ...
```

Nếu chỉ CRUD → dùng 1 service là đủ:

```python
class TodoService:
    def create(self, ...) -> UUID: ...
    def get(self, ...) -> Todo: ...
```

### ❌ Anti-pattern 8: Eventual consistency nhưng UI mong đợi immediate

```python
# Client
order_id = place_order(...)
summary = get_order_summary(order_id)   # ❌ Có thể None
```

**Fix:**

- Return summary ngay trong response của command.
- Hoặc client retry.
- Hoặc không dùng CQRS mức 2 cho case này.

---

## 9. Ví dụ tổng hợp: E-commerce CQRS

### 9.1. Commands

```python
# application/commands/place_order.py
@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[OrderItemInput]


class PlaceOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound(cmd.customer_id)

            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))
            order.place()

            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

```python
# application/commands/cancel_order.py
@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: UUID
    reason: str
    cancelled_by: UUID


class CancelOrderHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, cmd: CancelOrderCommand) -> None:
        with self._uow:
            order = self._uow.orders.find_by_id(cmd.order_id)
            if not order:
                raise OrderNotFound(cmd.order_id)

            order.cancel(cmd.reason, cmd.cancelled_by)

            self._uow.orders.save(order)
            self._uow.commit()
```

### 9.2. Queries

```python
# application/queries/order_summary.py
@dataclass(frozen=True)
class OrderSummaryDTO:
    order_id: UUID
    total: str
    status: str
    created_at: str


class OrderSummaryQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_customer(self, customer_id: UUID) -> list[OrderSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT order_id, total, status, created_at
                FROM order_summary
                WHERE customer_id = :cid
                ORDER BY created_at DESC
            """),
            {"cid": str(customer_id)},
        ).fetchall()
        return [OrderSummaryDTO(...) for row in rows]
```

```python
# application/queries/order_detail.py
@dataclass(frozen=True)
class OrderLineDTO:
    product_name: str
    quantity: int
    unit_price: str
    subtotal: str


@dataclass(frozen=True)
class OrderDetailDTO:
    order_id: UUID
    customer_name: str
    status: str
    total: str
    lines: list[OrderLineDTO]


class OrderDetailQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, order_id: UUID) -> OrderDetailDTO | None:
        # Query 1: header
        header = self._session.execute(
            text("""
                SELECT o.id, o.status, c.name AS customer_name
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                WHERE o.id = :oid
            """),
            {"oid": str(order_id)},
        ).fetchone()

        if not header:
            return None

        # Query 2: lines
        lines = self._session.execute(
            text("""
                SELECT p.name, l.quantity, l.unit_price_amount,
                       l.unit_price_amount * l.quantity AS subtotal
                FROM order_lines l
                JOIN products p ON p.id = l.product_id
                WHERE l.order_id = :oid
            """),
            {"oid": str(order_id)},
        ).fetchall()

        return OrderDetailDTO(
            order_id=header.id,
            customer_name=header.customer_name,
            status=header.status,
            total=str(sum(l.subtotal for l in lines)),
            lines=[OrderLineDTO(...) for l in lines],
        )
```

### 9.3. Composition Root

```python
# bootstrap.py
def build_container(db_url: str) -> dict:
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    event_bus = InMemoryEventBus()

    def make_uow():
        return SqlAlchemyUnitOfWork(session_factory, event_bus)

    def make_session():
        return session_factory()

    return {
        "place_order_handler": lambda: PlaceOrderHandler(make_uow()),
        "cancel_order_handler": lambda: CancelOrderHandler(make_uow()),
        "order_summary_query": lambda: OrderSummaryQuery(make_session()),
        "order_detail_query": lambda: OrderDetailQuery(make_session()),
    }
```

### 9.4. Presentation

```python
# presentation/api/routes/orders.py
@router.post("/orders", status_code=201)
def place_order(
    request: PlaceOrderRequest,
    container: dict = Depends(get_container),
) -> dict:
    handler = container["place_order_handler"]()
    cmd = PlaceOrderCommand(
        customer_id=request.customer_id,
        items=[...],
    )
    order_id = handler.handle(cmd)
    return {"order_id": order_id}


@router.get("/orders/{order_id}")
def get_order(
    order_id: UUID,
    container: dict = Depends(get_container),
) -> OrderDetailDTO:
    query = container["order_detail_query"]()
    result = query.get(order_id)
    if not result:
        raise HTTPException(404)
    return result
```

---

## 10. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Tách Command và Query

Cho service hiện tại:

```python
class OrderService:
    def place_order(self, customer_id, items) -> Order: ...
    def cancel_order(self, order_id, reason) -> None: ...
    def get_order(self, order_id) -> Order: ...
    def list_orders(self, customer_id) -> list[Order]: ...
```

Tách thành:

- `PlaceOrderCommand` + `PlaceOrderHandler`.
- `CancelOrderCommand` + `CancelOrderHandler`.
- `GetOrderQuery` + `OrderDetailDTO`.
- `ListOrdersQuery` + `OrderSummaryDTO`.

Đảm bảo:

- Command trả về ID/void.
- Query trả về DTO (không trả Entity).
- Query không dùng UoW.

### 🟡 Bài tập 2 (trung bình): Read Model riêng

Cho domain "blog":

- Write model: `posts`, `comments`, `users`.
- Read model: `post_summary` (denormalized).

Viết:

- `CreatePostHandler`, `PublishPostHandler`.
- `PostSummaryProjector` — event handler update read model.
- `PostSummaryQuery` — đọc từ read model.
- `PostDetailQuery` — đọc từ write model (JOIN).

Test:

- Happy path: Create post → projector chạy → query trả kết quả.
- Update: Publish post → projector update status.

Viết ít nhất 12 test.

### 🔴 Bài tập 3 (khó): Full CQRS với Event Sourcing

Cho hệ thống "ngân hàng":

**Write side:**

- Aggregate `BankAccount` (Event Sourced).
- Commands: `OpenAccount`, `Deposit`, `Withdraw`, `Transfer`.
- Events: `AccountOpened`, `MoneyDeposited`, `MoneyWithdrawn`, `TransferCompleted`.

**Read side:**

- Read model `account_balance` (bảng đơn giản).
- Read model `transaction_history` (list giao dịch).
- Projectors sync qua event.

**Yêu cầu:**

1. Event store (in-memory + SQLAlchemy).
2. Aggregate reconstruct từ events.
3. Projectors update read model.
4. Queries đọc thẳng read model.
5. Test:
   - Reconstruct aggregate từ event history.
   - Projector update đúng.
   - Query trả đúng.
   - Idempotency.

Viết ít nhất 25 test.

---

## 11. Checklist sau bài 11

Trước khi sang bài 12, bạn phải tự tin trả lời:

- [ ] Application Service là gì? Không là gì?
- [ ] Command vs Query khác nhau thế nào?
- [ ] Tại sao Command không trả Entity?
- [ ] Tại sao Query không đi qua Domain?
- [ ] CQRS là gì? Có mấy mức độ?
- [ ] Khi nào dùng CQRS? Khi nào không?
- [ ] Read model riêng là gì? Sync thế nào?
- [ ] Eventual consistency là gì? UI xử lý ra sao?
- [ ] Mediator pattern — nên dùng không?
- [ ] 8 anti-pattern khi dùng Application/CQRS?

Nếu trả lời được hết, bạn đã sẵn sàng bài 12.

---

## 12. Tóm tắt bài 11

| Điểm | Nội dung |
|---|---|
| **Application Service** | Orchestration, không chứa business rule |
| **Command** | Thay đổi state, trả ID/void, cần UoW |
| **Query** | Đọc state, trả DTO, không cần UoW |
| **CQRS mức 1** | Tách class, cùng DB |
| **CQRS mức 2** | Tách read model, sync qua event |
| **CQRS mức 3** | Tách DB (Postgres + Elastic) |
| **Khi nào dùng** | Read/write tần suất khác, JOIN phức tạp, scale |
| **Khi nào không** | CRUD đơn giản, team nhỏ |
| **Read model** | Denormalized, update qua projector |
| **Eventual consistency** | Trễ vài ms-giây, UI phải handle |
| **Mediator** | Optional, cho dự án lớn |
| **8 anti-pattern** | Business rule ở Handler, Command trả Entity, Query side effect, Query qua Domain, Handler quá lớn, Query trả Entity, CQRS không cần, UI chờ eventual |

**Câu thần chú:** *"Write qua Domain, Read thẳng DB. Tách hai con đường, mỗi con tối ưu cho mục đích của nó."*

---

## 13. Chuẩn bị cho bài 12

Bài tiếp theo: **Domain Service & Specification**.

Chuẩn bị:
- Đọc lại `TransferService` (bài 10).
- Nghĩ về **logic nghiệp vụ không thuộc về 1 Entity nào**.
- Sẽ bàn: Domain Service là gì, khi nào cần, Specification pattern để compose rule, và sự khác biệt giữa Domain Service vs Application Service.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 12** (Domain Service & Specification) ngay.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: Event Sourcing, Mediator, read model sync, eventual consistency handling.
5. **Review code Command/Query** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.