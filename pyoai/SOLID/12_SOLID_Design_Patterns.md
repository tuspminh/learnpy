Đúng. Theo roadmap bạn vừa chốt, **Buổi 12 không còn là DIP Deep Dive** nữa mà chuyển sang **Phần V — SOLID kết hợp**, tức là sau khi học riêng từng nguyên lý, chúng ta bắt đầu học cách **phối hợp SOLID với Design Patterns**.

Từ đây tôi sẽ bám đúng roadmap này.

# Phần V — SOLID kết hợp

## Buổi 12 — SOLID + Design Patterns

Đây là một buổi rất quan trọng vì cần hiểu:

> **SOLID là nguyên lý thiết kế, Design Pattern là giải pháp thiết kế thường gặp.**

Không phải:

```text
SOLID = Design Pattern
```

mà là:

```text
SOLID
  ↓
Principles
  ↓
Design decisions
  ↓
Design Patterns
  ↓
Architecture
```

---

# 1. Vì sao phải kết hợp SOLID với Design Patterns?

Ví dụ ta có:

```python
class PaymentService:

    def pay(self, method, amount):
        if method == "paypal":
            ...

        elif method == "stripe":
            ...

        elif method == "momo":
            ...
```

Ta đã thấy vấn đề OCP.

Nhưng OCP chỉ nói:

> Hãy thiết kế để extension không cần sửa core.

Nó không nói chính xác phải làm thế nào.

Một cách giải quyết là:

```text
Strategy Pattern
```

---

# 2. SOLID và Pattern có quan hệ thế nào?

Có thể hình dung:

```text
              SOLID
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
      SRP      OCP      DIP
       │        │        │
       ↓        ↓        ↓
   Strategy   Factory   Adapter
              │
              ↓
          Repository
```

Một Pattern có thể đồng thời hỗ trợ nhiều nguyên lý.

---

# 3. Strategy + OCP

Ví dụ ban đầu:

```python
class PaymentService:

    def pay(self, method, amount):

        if method == "stripe":
            return self.pay_stripe(amount)

        elif method == "momo":
            return self.pay_momo(amount)
```

Mỗi payment method mới:

```text
sửa PaymentService
```

Đây là điểm không tốt.

---

## Refactor

```python
from typing import Protocol


class PaymentStrategy(Protocol):

    def pay(self, amount: int) -> None:
        ...
```

Implementation:

```python
class StripePayment:

    def pay(self, amount: int) -> None:
        print(f"Stripe: {amount}")
```

```python
class MomoPayment:

    def pay(self, amount: int) -> None:
        print(f"Momo: {amount}")
```

Service:

```python
class PaymentService:

    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def pay(self, amount: int):
        self.strategy.pay(amount)
```

Sử dụng:

```python
service = PaymentService(
    StripePayment()
)

service.pay(100)
```

---

# 4. Strategy đang giúp nguyên lý nào?

### OCP

Thêm:

```python
class PaypalPayment:
    ...
```

không cần sửa:

```python
PaymentService
```

### DIP

`PaymentService` phụ thuộc:

```text
PaymentStrategy
```

thay vì:

```text
StripePayment
```

### SRP

`PaymentService` không còn chịu trách nhiệm:

```text
Stripe logic
Momo logic
Paypal logic
```

Nó chỉ điều phối payment.

---

# 5. Một Pattern có thể phục vụ nhiều SOLID

Đây là insight rất quan trọng.

Không nên học:

```text
Strategy = OCP
Factory = OCP
Adapter = DIP
```

một cách máy móc.

Thực tế:

```text
Strategy
   ↓
OCP + SRP + DIP
```

tùy cách sử dụng.

Pattern chỉ là **công cụ**.

---

# 6. Factory + DIP

Ví dụ:

```python
class OrderService:

    def create_payment(self, method):

        if method == "stripe":
            return StripePayment()

        if method == "momo":
            return MomoPayment()
```

Service đang biết concrete classes.

Ta có:

```python
class PaymentFactory(Protocol):

    def create(self, method: str):
        ...
```

Service:

```python
class OrderService:

    def __init__(self, factory: PaymentFactory):
        self.factory = factory

    def pay(self, method, amount):

        payment = self.factory.create(method)

        payment.pay(amount)
```

Dependency:

```text
OrderService
      ↓
PaymentFactory
      ↓
Payment implementation
```

Factory giúp đưa responsibility tạo object ra ngoài.

---

# 7. Factory + SRP

Nếu không có Factory:

```python
OrderService
```

phải làm:

```text
business logic
+
object creation
```

Sau khi refactor:

```text
OrderService
    ↓
business logic

PaymentFactory
    ↓
object creation
```

Ta có:

```text
SRP
```

---

# 8. Adapter + DIP

Giả sử application cần:

```python
class EmailSender(Protocol):

    def send(self, to, message):
        ...
```

Nhưng thư viện bên ngoài có:

```python
class SendGridClient:

    def send_email(
        self,
        recipient,
        body,
    ):
        ...
```

Interface không tương thích.

Không sửa:

```text
SendGridClient
```

Ta tạo Adapter:

```python
class SendGridAdapter:

    def __init__(self, client):
        self.client = client

    def send(self, to, message):
        self.client.send_email(
            recipient=to,
            body=message,
        )
```

Architecture:

```text
Application
     ↓
 EmailSender
     ↑
SendGridAdapter
     ↓
SendGrid
```

Đây là một ví dụ rất rõ của:

```text
DIP + Adapter
```

---

# 9. Repository + DIP

Ví dụ domain/application cần:

```python
class UserRepository(Protocol):

    def get_by_id(self, user_id):
        ...

    def save(self, user):
        ...
```

Infrastructure:

```python
class SQLiteUserRepository:

    def get_by_id(self, user_id):
        ...

    def save(self, user):
        ...
```

Application:

```python
class CreateUser:

    def __init__(self, repo: UserRepository):
        self.repo = repo
```

Dependency:

```text
Application
     ↓
UserRepository
     ↑
SQLiteUserRepository
```

Repository Pattern ở đây trở thành một **abstraction boundary**.

---

# 10. Observer + OCP

Ví dụ:

```text
UserRegistered
```

Khi user đăng ký:

```text
send email
send notification
write audit log
update analytics
```

Code xấu:

```python
def register(user):

    save_user(user)

    send_email(user)

    send_notification(user)

    write_log(user)

    update_analytics(user)
```

Mỗi notification mới lại sửa `register()`.

---

## Observer

```python
class EventListener(Protocol):

    def handle(self, event):
        ...
```

Các listener:

```python
class SendWelcomeEmail:

    def handle(self, event):
        ...
```

```python
class WriteAuditLog:

    def handle(self, event):
        ...
```

Publisher:

```python
class EventBus:

    def __init__(self):
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def publish(self, event):
        for listener in self.listeners:
            listener.handle(event)
```

Bây giờ:

```text
UserRegistered
       ↓
   EventBus
    / | \
   /  |  \
Email Log Analytics
```

Thêm listener mới mà không sửa business logic.

Đây là:

```text
OCP
+
SRP
+
DIP
```

---

# 11. Command + SRP

Thay vì:

```python
if command == "create":
    ...

elif command == "delete":
    ...

elif command == "update":
    ...
```

Ta có:

```python
class Command(Protocol):

    def execute(self):
        ...
```

Implementation:

```python
class CreateUserCommand:

    def execute(self):
        ...
```

```python
class DeleteUserCommand:

    def execute(self):
        ...
```

Mỗi command có một responsibility.

---

# 12. Command + OCP

Thêm:

```python
class ExportUserCommand:
    ...
```

không cần sửa command infrastructure.

```text
Command
   ↑
   ├── Create
   ├── Delete
   ├── Update
   └── Export
```

---

# 13. Template Method

Template Method phù hợp khi:

```text
algorithm structure ổn định
```

nhưng:

```text
một số bước thay đổi
```

Ví dụ crawler:

```text
fetch
  ↓
parse
  ↓
validate
  ↓
save
```

Algorithm:

```python
class Crawler:

    def run(self, url):

        html = self.fetch(url)

        data = self.parse(html)

        self.validate(data)

        self.save(data)
```

Các bước cụ thể có thể được override.

---

# 14. Template Method và OCP

Core algorithm:

```text
run()
```

được giữ ổn định.

Các implementation mở rộng:

```text
fetch()
parse()
validate()
save()
```

Điều này hỗ trợ:

```text
OCP
```

nhưng cần cẩn thận LSP.

Nếu subclass override:

```python
def parse(self, html):
    raise NotImplementedError
```

thì có thể tạo hierarchy xấu.

---

# 15. Đây chính là nơi LSP quay trở lại

Ví dụ:

```python
class BaseCrawler:

    def run(self):
        data = self.parse()
        return data
```

Subclass:

```python
class SiteCrawler(BaseCrawler):

    def parse(self):
        raise NotImplementedError
```

Nếu object:

```python
BaseCrawler
```

không thực sự có behavior hợp lệ thì abstraction có vấn đề.

Do đó:

```text
Pattern
  ↓
SOLID principle
  ↓
Trade-off
```

không thể áp dụng pattern máy móc.

---

# 16. Repository + Strategy

Hai pattern cũng có thể kết hợp.

Ví dụ:

```text
StoryRepository
```

có nhiều storage:

```text
SQLite
PostgreSQL
MongoDB
Memory
```

Ta có:

```text
StoryRepository
      ↑
 ┌────┼─────┬─────┐
 ↓    ↓     ↓     ↓
SQLite PG   Mongo Memory
```

Đây vừa là:

```text
Repository
+
Strategy-like polymorphism
+
DIP
+
OCP
```

---

# 17. Design theo Capability

Đừng bắt đầu bằng:

> "Tôi cần dùng Pattern nào?"

Hãy bắt đầu bằng:

> "Tôi có vấn đề dependency nào?"

Ví dụ:

```text
Problem:
Application phụ thuộc SQLite
```

→ DIP

```text
Problem:
Nhiều implementation thay thế
```

→ Strategy

```text
Problem:
Object creation phức tạp
```

→ Factory

```text
Problem:
External API không tương thích
```

→ Adapter

```text
Problem:
Persistence abstraction
```

→ Repository

```text
Problem:
Một event có nhiều subscriber
```

→ Observer

```text
Problem:
Operation cần encapsulate
```

→ Command

```text
Problem:
Algorithm skeleton cố định
```

→ Template Method

---

# 18. Bảng tư duy

| Problem                  | Pattern         | SOLID   |
| ------------------------ | --------------- | ------- |
| nhiều algorithm          | Strategy        | OCP     |
| object creation phức tạp | Factory         | SRP/DIP |
| API không tương thích    | Adapter         | DIP     |
| persistence boundary     | Repository      | DIP     |
| event subscribers        | Observer        | OCP/SRP |
| encapsulate operation    | Command         | SRP/OCP |
| algorithm skeleton       | Template Method | OCP/LSP |

Đây **không phải mapping cứng**.

Một pattern có thể liên quan nhiều nguyên lý.

---

# 19. Ví dụ kết hợp tất cả

Hãy tưởng tượng app crawler của bạn:

```text
CLI
 ↓
CrawlStoryUseCase
 ↓
CrawlerRegistry
 ↓
Crawler
 ↓
HTTP
 ↓
Parser
 ↓
Repository
 ↓
SQLite
```

Ta có thể áp dụng:

```text
Strategy
    ↓
Crawler implementations

Factory
    ↓
Create crawler

Adapter
    ↓
HTTP clients / external APIs

Repository
    ↓
Persistence

Observer
    ↓
crawl events

Command
    ↓
CLI operations

Template Method
    ↓
crawler pipeline
```

Và SOLID:

```text
SRP
 ↓
mỗi component một responsibility

OCP
 ↓
thêm crawler/plugin

LSP
 ↓
crawler implementation thay thế được nhau

ISP
 ↓
interface nhỏ

DIP
 ↓
application không phụ thuộc infrastructure
```

---

# 20. Architecture tổng thể

```text
                         CLI
                          │
                          ↓
                  ┌───────────────┐
                  │    Command    │
                  └───────┬───────┘
                          ↓
                  CrawlStoryUseCase
                          │
            ┌─────────────┼─────────────┐
            ↓             ↓             ↓
      CrawlerRegistry  Repository    EventBus
            │             ↑             │
            ↓             │             ↓
        Strategy          │          Observer
            │             │
      ┌─────┼─────┐       │
      ↓     ↓     ↓       │
   SiteA  SiteB  SiteC    │
                          │
                    SQLiteAdapter
```

Đây là lúc SOLID bắt đầu trở thành **architecture thinking**, thay vì chỉ là những quy tắc dành cho class.

---

# 21. Nguyên tắc quan trọng nhất của Buổi 12

Đừng học theo kiểu:

```text
"Muốn OCP → Strategy"
"Muốn DIP → Adapter"
"Muốn SRP → Factory"
```

Hãy học:

```text
Problem
   ↓
Identify responsibility
   ↓
Identify variation
   ↓
Identify dependency
   ↓
Define boundary
   ↓
Choose pattern
```

Pattern là **phương tiện**, không phải mục tiêu.

---

# 22. Bài tập lớn

Thiết kế:

```text
Notification System
```

Yêu cầu:

```text
Email
Telegram
Discord
SMS
```

Hệ thống phải:

1. Thêm channel mới mà không sửa `NotificationService`.
2. `NotificationService` không biết concrete implementation.
3. External API được bọc bằng Adapter.
4. Có Registry.
5. Có Factory.
6. Có event `NotificationSent`.
7. Có Observer để ghi audit log.

Kiến trúc mục tiêu:

```text
NotificationService
        │
        ↓
NotificationChannel
        ↑
 ┌──────┼────────┐
 ↓      ↓        ↓
Email Telegram Discord
 │
Adapter
 │
External API

NotificationRegistry
        ↓
NotificationFactory

NotificationService
        ↓
EventBus
   ├── AuditLogger
   ├── Metrics
   └── Analytics
```

---

# 23. Bài tập nâng cao

Sau khi hoàn thành, hãy trả lời từng câu:

### SRP

`NotificationService` có bao nhiêu responsibility?

### OCP

Thêm WhatsApp cần sửa những file nào?

### LSP

`DiscordNotification` có thực sự thay thế `NotificationChannel` không?

### ISP

`NotificationChannel` có đang quá lớn không?

### DIP

`NotificationService` có import:

```python
StripeNotification
```

hay không?

### Architecture

Concrete implementation nằm ở đâu?

---

# 24. Mental model của Phần V

Từ đây, bạn nên bắt đầu nhìn code theo chuỗi:

```text
                 SOLID
                   ↓
              Boundaries
                   ↓
             Abstractions
                   ↓
             Polymorphism
                   ↓
          Design Patterns
                   ↓
              Components
                   ↓
             Architecture
```

Và đây là điểm chuyển rất quan trọng:

> **SOLID không phải mục tiêu cuối cùng. SOLID là công cụ để tạo ra những boundary tốt.**

Sau đó các boundary đó mới được tổ chức thành **Clean Architecture / Hexagonal Architecture / DDD Architecture**.

---

## Roadmap hiện tại

```text
PHẦN I — Foundation
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive
✅ Buổi 4 — OCP
✅ Buổi 5 — OCP Deep Dive
✅ Buổi 6 — LSP
✅ Buổi 7 — LSP Deep Dive
✅ Buổi 8 — ISP
✅ Buổi 9 — ISP Deep Dive
✅ Buổi 10 — DIP
✅ Buổi 11 — DIP Deep Dive

PHẦN V — SOLID kết hợp
➡️ Buổi 12 — SOLID + Design Patterns
⬜ Buổi 13 — SOLID + Python
⬜ Buổi 14 — SOLID + Testing
⬜ Buổi 15 — SOLID + DDD

PHẦN VI — SOLID trong Clean Architecture
⬜ Buổi 16 — Clean Architecture
⬜ Buổi 17 — CLI + Repository + SQLite
⬜ Buổi 18 — Crawler + Plugin
⬜ Buổi 19 — Refactoring CrawlerManager
```

**Buổi 13** sẽ đi sâu vào một điểm rất quan trọng đối với Python: **SOLID trong một ngôn ngữ dynamic/duck-typed** — đặc biệt là `Protocol` vs `ABC`, first-class function, higher-order function, composition và tại sao Python thường không cần xây những inheritance hierarchy lớn như Java/C#.
