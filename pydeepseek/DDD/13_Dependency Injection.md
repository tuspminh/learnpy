# 📖 Bài 13: Dependency Injection trong Python

> Đây là **bài cuối của Level 3** — và là bài **bản lề** giữa kiến trúc và thực thi. Bạn đã có Domain, Application, Infrastructure, Presentation. Giờ câu hỏi là: **ráp chúng lại thế nào?** Dependency Injection (DI) là câu trả lời. Nhưng DI trong Python **khác hẳn** Java/C# — không cần Spring, không cần `@Inject`. Python có cách **Pythonic** hơn nhiều.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Dependency Injection** là gì và **tại sao cần**.
2. Phân biệt **DI** vs **Dependency Inversion Principle** (DIP).
3. Biết **4 cách DI** trong Python: constructor, setter, method, và manual.
4. Hiểu **Composition Root** — nơi ráp mọi thứ.
5. Biết khi nào dùng **DI container**, khi nào dùng **manual DI**.
6. Sử dụng **`dependency-injector`** library (nếu cần).
7. **Test** với DI — fake, stub, mock.
8. Tránh được **8 anti-pattern** khi dùng DI.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Dependency Injection là gì?

### 1.1. Định nghĩa

> **Dependency Injection** là kỹ thuật **truyền dependency** (object mà class cần) **từ bên ngoài** vào, thay vì để class **tự tạo** dependency đó.

### 1.2. Trực giác

Hãy tưởng tượng **một cái máy pha cà phê**.

**Cách 1: Máy tự trồng cà phê (KHÔNG DI)**

- Máy pha cà phê phải tự trồng cà phê, tự rang, tự xay, rồi mới pha.
- Muốn đổi loại cà phê → phải sửa máy.
- Muốn test máy → phải trồng cà phê thật.

**Cách 2: Máy nhận cà phê từ ngoài (CÓ DI)**

- Máy pha cà phê nhận **hạt cà phê** từ ngoài (ai đó đưa vào).
- Muốn đổi loại → đưa hạt khác vào, không sửa máy.
- Muốn test → đưa hạt giả vào.

DI chính là **cách 2**.

### 1.3. Ví dụ code

**KHÔNG DI:**

```python
class OrderService:
    def __init__(self) -> None:
        # Tự tạo dependency — coupling chặt
        self._session = create_session()
        self._repo = SqlAlchemyOrderRepository(self._session)
        self._email_sender = SmtpEmailSender(...)

    def place_order(self, order: Order) -> None:
        self._repo.save(order)
        self._email_sender.send(...)
```

**CÓ DI:**

```python
class OrderService:
    def __init__(
        self,
        repo: OrderRepository,        # ← nhận từ ngoài
        email_sender: EmailSender,     # ← nhận từ ngoài
    ) -> None:
        self._repo = repo
        self._email_sender = email_sender

    def place_order(self, order: Order) -> None:
        self._repo.save(order)
        self._email_sender.send(...)
```

### 1.4. Lợi ích

| Lợi ích | Ý nghĩa |
|---|---|
| **Testable** | Inject fake, không cần DB/HTTP |
| **Decoupled** | `OrderService` không biết SQLAlchemy |
| **Flexible** | Đổi impl mà không sửa code |
| **Explicit** | Dependency rõ ràng ở constructor |
| **SOLID** | Tuân thủ Dependency Inversion |

---

## 2. DI vs DIP — Phân biệt

Nhiều dev nhầm 2 khái niệm này.

### 2.1. Dependency Inversion Principle (DIP)

**Định nghĩa:** Module cấp cao **không** phụ thuộc module cấp thấp. Cả hai phụ thuộc **abstraction**. Abstraction **không** phụ thuộc chi tiết. Chi tiết phụ thuộc abstraction.

**Ví dụ:**

```python
# ❌ SAI: OrderService (cao) phụ thuộc SqlAlchemyOrderRepository (thấp)
class OrderService:
    def __init__(self) -> None:
        self._repo = SqlAlchemyOrderRepository()   # Cụ thể!

# ✅ ĐÚNG: OrderService phụ thuộc OrderRepository (abstraction)
class OrderService:
    def __init__(self, repo: OrderRepository) -> None:   # Trừu tượng
        self._repo = repo
```

### 2.2. Dependency Injection (DI)

**Định nghĩa:** Kỹ thuật **truyền** dependency vào. DI là **cách thực hiện** DIP.

### 2.3. So sánh

| Tiêu chí | DIP | DI |
|---|---|---|
| **Là gì** | Nguyên lý thiết kế | Kỹ thuật implementation |
| **Ai đề xuất** | Uncle Bob (SOLID) | Martin Fowler |
| **Nói về** | Phụ thuộc abstraction | Truyền dependency |
| **Ở tầng** | Kiến trúc | Code |
| **Bắt buộc?** | Khuyến nghị | Tùy chọn |

**Tóm tắt:** DIP là **mục tiêu** (phụ thuộc abstraction). DI là **cách** (truyền từ ngoài). Bạn có thể dùng DIP mà không cần DI (dùng Factory). Nhưng DI là cách phổ biến nhất để thực hiện DIP.

---

## 3. Bốn cách DI trong Python

### 3.1. Constructor Injection (Khuyến nghị)

Truyền dependency qua `__init__`.

```python
class PlaceOrderHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        pricing_service: PricingService,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._pricing_service = pricing_service
        self._event_bus = event_bus

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        ...
```

**Ưu điểm:**

- Dependency **rõ ràng** — đọc `__init__` biết hết.
- **Immutable** — không đổi được sau khi tạo.
- **Testable** — dễ inject fake.

**Nhược điểm:**

- Constructor dài nếu nhiều dependency (>5 → dấu hiệu tách class).

**Khi nào dùng:** 95% trường hợp. **Đây là cách khuyến nghị.**

### 3.2. Setter Injection

Truyền dependency qua setter sau khi tạo.

```python
class PlaceOrderHandler:
    def set_uow(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def set_pricing_service(self, service: PricingService) -> None:
        self._pricing_service = service
```

**Nhược điểm:**

- Object **không hoàn chỉnh** sau khi tạo → nguy hiểm.
- Dependency **có thể đổi** → khó trace.

**Khi nào dùng:** Hầu như **không bao giờ** trong DDD. Có thể dùng cho circular dependency (nhưng nên tránh).

### 3.3. Method Injection

Truyền dependency qua tham số method.

```python
class OrderCalculator:
    def calculate(
        self,
        order: Order,
        pricing_service: PricingService,   # ← inject qua method
    ) -> Money:
        return pricing_service.calculate_total(order)
```

**Khi nào dùng:** Khi dependency **chỉ cần cho 1 method** và **thay đổi theo lần gọi**.

**Ví dụ thực tế:**

```python
class EmailService:
    def send(
        self,
        to: str,
        subject: str,
        body: str,
        transport: EmailTransport,   # ← inject transport
    ) -> None:
        transport.send(...)
```

### 3.4. Manual DI (Composition Root)

Không có framework. Tự ráp trong 1 file.

```python
# bootstrap.py
def build_place_order_handler() -> PlaceOrderHandler:
    session_factory = sessionmaker(bind=engine)
    event_bus = InMemoryEventBus()
    uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    pricing_service = PricingService()
    return PlaceOrderHandler(uow, pricing_service, event_bus)
```

**Ưu điểm:**

- **Explicit** — đọc là hiểu.
- **Không phụ thuộc thư viện**.
- **Dễ debug** — stack trace rõ.
- **Pythonic**.

**Nhược điểm:**

- Nhiều boilerplate nếu project lớn.

**Khuyến nghị:** Manual DI cho **90% dự án Python**. Chỉ dùng framework khi thực sự cần.

### 3.5. Bảng chọn cách DI

| Tình huống | Cách DI |
|---|---|
| Đa số trường hợp | Constructor |
| Dependency optional | Constructor với default |
| Dependency per-call | Method |
| Circular (tránh) | Setter |
| Ráp toàn bộ app | Manual DI (bootstrap) |
| App rất lớn (>100 handler) | DI container |

---

## 4. Composition Root — Nơi ráp mọi thứ

### 4.1. Định nghĩa

> **Composition Root** là **một chỗ duy nhất** trong app nơi mọi object được ráp lại. Đây là nơi **duy nhất** biết về mọi tầng.

### 4.2. Nguyên tắc

1. **Một chỗ duy nhất** — thường là `bootstrap.py` hoặc `main.py`.
2. **Không import ngược** — Composition Root import mọi thứ; không ai import nó (trừ entry point).
3. **Gần entry point** — gần `main()`, gần `app = FastAPI()`.
4. **Không phải Service Locator** — không phải object nào cũng gọi được.

### 4.3. Ví dụ: FastAPI + Manual DI

```python
# bootstrap.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shop.application.commands.place_order import PlaceOrderHandler
from shop.application.commands.cancel_order import CancelOrderHandler
from shop.application.queries.order_summary import OrderSummaryQuery
from shop.domain.services.pricing_service import PricingService
from shop.infrastructure.email.smtp_sender import SmtpEmailSender
from shop.infrastructure.messaging.in_memory_bus import InMemoryEventBus
from shop.infrastructure.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork


class Container:
    """Composition Root — ráp mọi thứ."""

    def __init__(self, db_url: str, smtp_config: dict) -> None:
        # Infrastructure
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.event_bus = InMemoryEventBus()
        self.email_sender = SmtpEmailSender(**smtp_config)

        # Domain Services
        self.pricing_service = PricingService()

        # Setup event handlers
        self._setup_events()

    def _setup_events(self) -> None:
        from shop.application.handlers.on_order_placed import (
            SendOrderConfirmationEmail,
            ReserveInventory,
        )
        from shop.domain.events.order_events import OrderPlaced

        self.event_bus.subscribe(
            OrderPlaced,
            SendOrderConfirmationEmail(self.email_sender).handle,
        )
        self.event_bus.subscribe(
            OrderPlaced,
            ReserveInventory(self.make_uow()).handle,
        )

    # ---- Factories ----
    def make_uow(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory, self.event_bus)

    def make_place_order_handler(self) -> PlaceOrderHandler:
        return PlaceOrderHandler(
            uow=self.make_uow(),
            pricing_service=self.pricing_service,
        )

    def make_cancel_order_handler(self) -> CancelOrderHandler:
        return CancelOrderHandler(uow=self.make_uow())

    def make_order_summary_query(self) -> OrderSummaryQuery:
        return OrderSummaryQuery(session=self.session_factory())
```

```python
# presentation/api/main.py
from fastapi import FastAPI

from shop.bootstrap import Container
from shop.presentation.api.routes import orders


def create_app() -> FastAPI:
    app = FastAPI(title="Shop API")

    container = Container(
        db_url="postgresql://...",
        smtp_config={"host": "...", ...},
    )
    app.state.container = container

    app.include_router(orders.router)
    return app


app = create_app()
```

```python
# presentation/api/dependencies.py
from fastapi import Request
from shop.application.commands.place_order import PlaceOrderHandler


def get_place_order_handler(request: Request) -> PlaceOrderHandler:
    container = request.app.state.container
    return container.make_place_order_handler()
```

```python
# presentation/api/routes/orders.py
from fastapi import APIRouter, Depends

from shop.application.commands.place_order import (
    PlaceOrderCommand, PlaceOrderHandler,
)
from shop.presentation.api.dependencies import get_place_order_handler
from shop.presentation.api.schemas import PlaceOrderRequest


router = APIRouter()


@router.post("/orders", status_code=201)
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
) -> dict:
    cmd = PlaceOrderCommand(...)
    order_id = handler.handle(cmd)
    return {"order_id": str(order_id)}
```

**Điểm mấu chốt:**

- `Container` biết **mọi thứ**.
- `bootstrap.py` **không ai import** (trừ `main.py`).
- Routes **không** biết Infrastructure.
- Mỗi request tạo handler mới (vì UoW per-request).

---

## 5. Khi nào cần DI container?

### 5.1. Manual DI đủ cho hầu hết

**Manual DI tốt khi:**

- Project < 50 handler.
- Dependency đơn giản.
- Team nhỏ.
- Muốn explicit, dễ debug.

**Manual DI yếu khi:**

- Project > 100 handler.
- Nhiều config phức tạp (nhiều môi trường).
- Cần lifecycle management (singleton, request scope).
- Nhiều module.

### 5.2. DI container là gì?

**DI container** = thư viện tự động hóa việc ráp dependency.

**Ví dụ với `dependency-injector`:**

```python
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Infrastructure
    engine = providers.Singleton(
        create_engine,
        url=config.db_url,
    )

    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
    )

    event_bus = providers.Singleton(InMemoryEventBus)

    email_sender = providers.Singleton(
        SmtpEmailSender,
        host=config.smtp.host,
        port=config.smtp.port,
    )

    # Unit of Work
    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
        event_bus=event_bus,
    )

    # Domain Services
    pricing_service = providers.Singleton(PricingService)

    # Application Handlers
    place_order_handler = providers.Factory(
        PlaceOrderHandler,
        uow=uow,
        pricing_service=pricing_service,
    )
```

**Sử dụng:**

```python
# main.py
container = Container()
container.config.from_yaml("config.yaml")
container.wire(modules=[...])

handler = container.place_order_handler()
```

### 5.3. So sánh

| Tiêu chí | Manual DI | DI Container |
|---|---|---|
| **Setup** | Đơn giản | Phức tạp ban đầu |
| **Explicit** | ✅ Rõ ràng | ⚠️ Magic |
| **Debug** | ✅ Dễ | ⚠️ Khó |
| **Boilerplate** | Nhiều | Ít |
| **Lifecycle** | Tự quản | Framework quản |
| **Test** | ✅ Dễ | ⚠️ Phải hiểu framework |
| **Học** | Không cần | Cần thời gian |
| **Phù hợp** | < 50 handler | > 100 handler |

### 5.4. Khuyến nghị

> **Bắt đầu với Manual DI.** Chỉ chuyển sang DI container khi:
> - Project lớn (>100 handler).
> - Cần lifecycle management phức tạp.
> - Team đã quen DI framework.
>
> **Đừng dùng DI container chỉ vì "nghe nói nó tốt".**

---

## 6. Testing với DI

DI giúp test **cực dễ**. Đây là **lợi ích lớn nhất** của DI.

### 6.1. Fake dependencies

```python
# tests/fakes/email_sender.py
class FakeEmailSender:
    """Fake EmailSender — lưu lại email đã gửi, không gửi thật."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})
```

```python
# tests/fakes/uow.py
from shop.infrastructure.persistence.in_memory.uow import InMemoryUnitOfWork


class FakeUnitOfWork(InMemoryUnitOfWork):
    """Fake UoW cho test — thêm tracking."""

    def __init__(self) -> None:
        super().__init__()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True
```

### 6.2. Test với DI

```python
# tests/unit/application/test_place_order.py
from decimal import Decimal
from uuid import uuid4

import pytest

from shop.application.commands.place_order import (
    PlaceOrderCommand, PlaceOrderHandler, OrderItemInput,
)
from shop.domain.model.customer import Customer
from shop.shared.domain.email import Email
from tests.fakes.uow import FakeUnitOfWork


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def handler(uow: FakeUnitOfWork) -> PlaceOrderHandler:
    return PlaceOrderHandler(uow=uow, pricing_service=PricingService())


def test_place_order_commits(uow: FakeUnitOfWork, handler: PlaceOrderHandler) -> None:
    # Arrange
    customer = Customer.register(Email("an@example.com"), "An")
    uow.customers.save(customer)

    cmd = PlaceOrderCommand(
        customer_id=customer.id,
        items=[
            OrderItemInput(
                product_id=uuid4(),
                unit_price_amount=Decimal("100"),
                unit_price_currency="VND",
                quantity=2,
            ),
        ],
    )

    # Act
    order_id = handler.handle(cmd)

    # Assert
    assert uow.committed is True
    order = uow.orders.find_by_id(order_id)
    assert order is not None
```

**Điểm hay:**

- **Không cần DB** — dùng InMemory UoW.
- **Không cần SMTP** — dùng FakeEmailSender.
- **Test nhanh** — millisecond.
- **Test rõ ràng** — không mock phức tạp.

### 6.3. Test với Dependency Override

```python
# tests/e2e/test_api.py
from fastapi.testclient import TestClient

from shop.presentation.api.main import create_app
from shop.presentation.api.dependencies import get_place_order_handler
from tests.fakes.uow import FakeUnitOfWork


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    # Override dependency
    def fake_place_order_handler():
        uow = FakeUnitOfWork()
        return PlaceOrderHandler(uow=uow)

    app.dependency_overrides[get_place_order_handler] = fake_place_order_handler

    return TestClient(app)


def test_place_order_endpoint(client: TestClient) -> None:
    response = client.post("/orders", json={...})
    assert response.status_code == 201
```

**FastAPI hỗ trợ `dependency_overrides`** — cực mạnh cho test.

---

## 7. Ví dụ tổng hợp: Full DI setup

### 7.1. Domain

```python
# domain/services/pricing_service.py
class PricingService:
    def calculate_total(self, order: Order) -> Money:
        return sum(
            (line.subtotal for line in order.lines),
            Money(Decimal("0"), "VND"),
        )
```

```python
# domain/repositories/order_repository.py
class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def save(self, order: Order) -> None: ...
```

### 7.2. Application

```python
# application/uow.py
class UnitOfWork(Protocol):
    orders: OrderRepository
    customers: CustomerRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *args) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

```python
# application/commands/place_order.py
class PlaceOrderHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        pricing_service: PricingService,
    ) -> None:
        self._uow = uow
        self._pricing_service = pricing_service

    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self._uow:
            customer = self._uow.customers.find_by_id(cmd.customer_id)
            if not customer:
                raise CustomerNotFound()

            order = Order.create(cmd.customer_id)
            for item in cmd.items:
                order.add_line(OrderLine.create(...))

            order.place()

            self._uow.orders.save(order)
            self._uow.commit()
        return order.id
```

### 7.3. Infrastructure

```python
# infrastructure/persistence/sqlalchemy/uow.py
class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory, event_bus) -> None:
        ...

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        ...
```

```python
# infrastructure/persistence/in_memory/uow.py
class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.orders = InMemoryOrderRepository()
        self.customers = InMemoryCustomerRepository()

    # ...
```

### 7.4. Presentation

```python
# presentation/api/routes/orders.py
@router.post("/orders", status_code=201)
def place_order(
    request: PlaceOrderRequest,
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
) -> dict:
    cmd = PlaceOrderCommand(...)
    return {"order_id": str(handler.handle(cmd))}
```

### 7.5. Composition Root

```python
# bootstrap.py
class Container:
    def __init__(self, db_url: str, environment: str = "production") -> None:
        self._environment = environment

        if environment == "test":
            self._setup_test()
        else:
            self._setup_production(db_url)

    def _setup_test(self) -> None:
        self.uow_factory = InMemoryUnitOfWork

    def _setup_production(self, db_url: str) -> None:
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.event_bus = InMemoryEventBus()

        def make_uow():
            return SqlAlchemyUnitOfWork(self.session_factory, self.event_bus)

        self.uow_factory = make_uow

    def make_place_order_handler(self) -> PlaceOrderHandler:
        return PlaceOrderHandler(
            uow=self.uow_factory(),
            pricing_service=PricingService(),
        )
```

### 7.6. Test

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from shop.bootstrap import Container
from shop.presentation.api.main import create_app


@pytest.fixture
def container() -> Container:
    return Container(db_url="", environment="test")


@pytest.fixture
def client(container: Container) -> TestClient:
    app = create_app()
    app.state.container = container
    return TestClient(app)
```

**Điểm hay:**

- Test dùng `environment="test"` → InMemory UoW.
- Production dùng `environment="production"` → SQLAlchemy.
- **Cùng code**, khác config.

---

## 8. Tám anti-pattern khi dùng DI

### ❌ Anti-pattern 1: Service Locator

```python
# ❌ SAI: Service Locator
class OrderService:
    def place_order(self, order: Order) -> None:
        repo = ServiceLocator.get(OrderRepository)   # Không rõ dependency!
        repo.save(order)
```

**Vấn đề:**

- Dependency **ẩn** — không thấy trong constructor.
- Khó test — phải setup ServiceLocator.
- Khó debug.

**Fix:** Constructor Injection.

### ❌ Anti-pattern 2: Tự new Infrastructure

```python
# ❌ SAI: Tự tạo
class PlaceOrderHandler:
    def __init__(self) -> None:
        self._uow = SqlAlchemyUnitOfWork(...)   # Tự new!
```

**Fix:** Inject từ ngoài.

### ❌ Anti-pattern 3: Inject quá nhiều dependency

```python
# ❌ SAI: 10 dependency
class PlaceOrderHandler:
    def __init__(
        self,
        uow, pricing, tax, email, sms, logger, cache,
        metrics, audit, feature_flag,
    ) -> None:
        ...
```

**Fix:** Tách class. Nếu handler cần 10 dependency → nó làm quá nhiều.

### ❌ Anti-pattern 4: Inject concrete class

```python
# ❌ SAI: Inject SqlAlchemyOrderRepository
class PlaceOrderHandler:
    def __init__(self, repo: SqlAlchemyOrderRepository) -> None:
        self._repo = repo
```

**Fix:** Inject Protocol.

```python
# ✅ ĐÚNG
class PlaceOrderHandler:
    def __init__(self, repo: OrderRepository) -> None:
        ...
```

### ❌ Anti-pattern 5: Dùng DI container cho mọi thứ

```python
# ❌ SAI: Container cho cả utility
container.register(StringUtils, StringUtils)
container.register(DateUtils, DateUtils)
```

**Fix:** Utility dùng trực tiếp, không cần DI.

### ❌ Anti-pattern 6: DI container ở Domain

```python
# ❌ SAI: Domain biết container
from dependency_injector import containers

class Order:
    def place(self) -> None:
        repo = get_container().order_repo()   # Phá vỡ DDD!
```

**Fix:** Domain không biết DI container.

### ❌ Anti-pattern 7: Circular dependency

```python
# ❌ SAI
class A:
    def __init__(self, b: "B") -> None:
        self._b = b

class B:
    def __init__(self, a: A) -> None:
        self._a = a
```

**Fix:** Tách interface, dùng event, hoặc refactor.

### ❌ Anti-pattern 8: Global mutable state

```python
# ❌ SAI: Global
db_session = None   # Global!

def set_db(session):
    global db_session
    db_session = session

class OrderService:
    def place_order(self):
        db_session.add(order)   # Dùng global!
```

**Fix:** Inject qua constructor.

---

## 9. Ví dụ nâng cao: DI với nhiều environment

### 9.1. Config cho nhiều môi trường

```python
# bootstrap.py
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    db_url: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        import os
        return cls(
            environment=os.getenv("ENV", "production"),
            db_url=os.getenv("DB_URL", ""),
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
        )


class Container:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

        if config.environment == "test":
            self._setup_test()
        elif config.environment == "development":
            self._setup_development()
        else:
            self._setup_production()

    def _setup_test(self) -> None:
        self.uow_factory = InMemoryUnitOfWork
        self.email_sender = FakeEmailSender()

    def _setup_development(self) -> None:
        self.engine = create_engine("sqlite:///dev.db")
        self.session_factory = sessionmaker(bind=self.engine)
        self.event_bus = InMemoryEventBus()

        def make_uow():
            return SqlAlchemyUnitOfWork(self.session_factory, self.event_bus)

        self.uow_factory = make_uow
        self.email_sender = ConsoleEmailSender()   # In ra console

    def _setup_production(self) -> None:
        self.engine = create_engine(self._config.db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.event_bus = InMemoryEventBus()

        def make_uow():
            return SqlAlchemyUnitOfWork(self.session_factory, self.event_bus)

        self.uow_factory = make_uow
        self.email_sender = SmtpEmailSender(
            host=self._config.smtp_host,
            port=self._config.smtp_port,
            username=self._config.smtp_username,
            password=self._config.smtp_password,
        )
```

### 9.2. Sử dụng

```python
# main.py
from shop.bootstrap import AppConfig, Container

config = AppConfig.from_env()
container = Container(config)

# Chạy app
app = create_app(container)
```

**Điểm hay:**

- **Cùng code** — khác config.
- Test dùng `ENV=test` → InMemory.
- Dev dùng `ENV=development` → SQLite + Console email.
- Prod dùng `ENV=production` → Postgres + SMTP.

---

## 10. Bài tập về nhà

### 🟢 Bài tập 1 (dễ): Refactor sang DI

Cho class không dùng DI:

```python
class UserService:
    def __init__(self) -> None:
        self._session = create_session()
        self._repo = SqlAlchemyUserRepository(self._session)
        self._hasher = BcryptHasher()
        self._email = SmtpEmailSender(host="smtp.gmail.com")

    def register(self, email: str, password: str) -> None:
        hashed = self._hasher.hash(password)
        user = User(email=email, password=hashed)
        self._repo.save(user)
        self._email.send(email, "Welcome", "Thanks for signing up")
```

Refactor:

1. Constructor Injection.
2. Inject Protocol (`UserRepository`, `PasswordHasher`, `EmailSender`).
3. Viết `FakeEmailSender`, `FakePasswordHasher` cho test.
4. Viết ít nhất 5 test.

### 🟡 Bài tập 2 (trung bình): Composition Root

Cho project hiện tại, viết `Container` class với:

- 3 môi trường: test, development, production.
- Config từ environment variables.
- Factory methods cho: `make_place_order_handler`, `make_cancel_order_handler`, `make_order_query`.
- Setup event handlers.

Viết test:
- Container với `ENV=test` → dùng InMemory.
- Container với `ENV=development` → dùng SQLite.
- Factory trả về đúng type.

Viết ít nhất 8 test.

### 🔴 Bài tập 3 (khó): Full DI với FastAPI

Cho hệ thống e-commerce:

- Domain: Order, Customer, Product.
- Application: PlaceOrderHandler, CancelOrderHandler, các Query.
- Infrastructure: SQLAlchemy UoW, InMemory UoW, SMTP, Fake Email.
- Presentation: FastAPI routes.

**Yêu cầu:**

1. `AppConfig` đọc từ env vars.
2. `Container` với 3 môi trường.
3. FastAPI `dependency_overrides` cho test.
4. Test:
   - Unit test handler (không cần HTTP).
   - Integration test API (dùng TestClient).
   - E2E test (bootstrap thật, override DB).
5. **Không dùng** bất kỳ DI framework nào — chỉ manual DI.

Bonus: So sánh với version dùng `dependency-injector`. Viết 1 file `bootstrap_with_framework.py` và so sánh LOC, readability.

---

## 11. Checklist sau bài 13

Trước khi sang Level 4, bạn phải tự tin trả lời:

- [ ] DI là gì? Tại sao cần?
- [ ] DI vs DIP khác nhau thế nào?
- [ ] 4 cách DI trong Python? Cách nào khuyến nghị?
- [ ] Composition Root là gì? Đặt ở đâu?
- [ ] Khi nào dùng DI container? Khi nào không?
- [ ] Test với DI thế nào? Fake, stub, mock?
- [ ] Làm sao hỗ trợ nhiều môi trường (test, dev, prod)?
- [ ] `dependency_overrides` của FastAPI dùng làm gì?
- [ ] Service Locator là gì? Tại sao anti-pattern?
- [ ] 8 anti-pattern khi dùng DI?

Nếu trả lời được hết, bạn đã hoàn thành Level 3 và sẵn sàng cho Level 4.

---

## 12. Tóm tắt bài 13

| Điểm | Nội dung |
|---|---|
| **DI** | Truyền dependency từ ngoài vào |
| **DIP** | Nguyên lý phụ thuộc abstraction |
| **Constructor Injection** | Khuyến nghị, rõ ràng, testable |
| **Method Injection** | Khi dependency per-call |
| **Setter Injection** | Tránh (trừ circular) |
| **Manual DI** | Tự ráp trong bootstrap — khuyến nghị |
| **Composition Root** | 1 chỗ duy nhất ráp mọi thứ |
| **DI container** | Chỉ dùng khi project lớn (>100 handler) |
| **Test** | Fake dependencies, `dependency_overrides` |
| **Nhiều env** | Config từ env vars, setup khác nhau |
| **8 anti-pattern** | Service Locator, tự new, quá nhiều dep, concrete class, container cho util, container trong Domain, circular, global state |

**Câu thần chú:** *"Đừng tự tạo dependency. Hãy nhận nó từ ngoài. Ráp mọi thứ ở 1 chỗ duy nhất."*

---

## 13. Chúc mừng — Bạn đã hoàn thành Level 3!

Level 3 gồm 4 bài:

- **Bài 10:** Layered Architecture — 4 tầng.
- **Bài 11:** Application Service & CQRS — write/read tách biệt.
- **Bài 12:** Domain Service & Specification — logic không thuộc Entity.
- **Bài 13:** Dependency Injection — ráp mọi thứ.

Giờ bạn đã có đủ công cụ để xây dựng **hệ thống DDD hoàn chỉnh**.

---

## 14. Chuẩn bị cho Level 4 — Strategic DDD

Level 4 gồm 3 bài:

- **Bài 14:** Context Mapping — quan hệ giữa các Bounded Context.
- **Bài 15:** Event Storming — khám phá domain cùng business.
- **Bài 16:** Chiến lược chọn Bounded Context — khi nào tách, khi nào gộp.

Level 4 chuyển từ **tactical** (code) sang **strategic** (tổ chức hệ thống lớn).

Chuẩn bị:
- Đọc lại bài 4 (Bounded Context).
- Nghĩ về **hệ thống lớn** bạn từng làm: có bao nhiêu context?
- Sẽ bàn: Context Map, ACL, Shared Kernel, event storming workshop.

---

📌 **Bạn muốn tôi làm gì tiếp?**

1. **Chấm bài tập** khi bạn viết xong.
2. **Đi tiếp bài 14** (Context Mapping) — bắt đầu Level 4.
3. **Viết code mẫu đầy đủ** cho một trong ba bài tập.
4. **Đào sâu** một phần: `dependency-injector` chi tiết, FastAPI DI, config management.
5. **Review code DI** của bạn — nếu bạn gửi code, tôi sẽ chỉ ra anti-pattern và cách sửa.

Nói tôi biết bạn muốn gì nhé.