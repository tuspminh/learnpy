# Python OOP Master — Buổi 28

# Open/Closed Principle — OCP

Ở Buổi 27, chúng ta học:

```text
SRP
 ↓
Mỗi class có responsibility rõ ràng
```

Hôm nay đi thêm một bước:

> **Làm sao thêm behavior mới mà không phải sửa code đã ổn định?**

Đó là **Open/Closed Principle — OCP**.

---

# 1. OCP là gì?

OCP nói rằng:

> **Software entities should be open for extension, but closed for modification.**

Hiểu đơn giản:

```text
Open for extension
    ↓
Có thể thêm behavior mới

Closed for modification
    ↓
Không cần sửa code cũ
```

Ví dụ:

```text
Parser
 ├── SiteAParser
 ├── SiteBParser
 └── SiteCParser
```

Khi thêm Site D:

```text
Parser
 ├── SiteAParser
 ├── SiteBParser
 ├── SiteCParser
 └── SiteDParser   ← thêm mới
```

Không cần sửa `Crawler`.

Đó chính là OCP.

---

# 2. Ví dụ vi phạm OCP

Giả sử có:

```python
class PaymentService:

    def pay(self, method, amount):
        if method == "paypal":
            print("PayPal")
        elif method == "stripe":
            print("Stripe")
        elif method == "momo":
            print("MoMo")
```

Khi thêm:

```text
VNPay
```

phải sửa:

```python
def pay(self, method, amount):
    if method == "paypal":
        ...
    elif method == "stripe":
        ...
    elif method == "momo":
        ...
    elif method == "vnpay":
        ...
```

Mỗi lần thêm payment method:

```text
Thêm tính năng
      ↓
Sửa class cũ
```

Đây là dấu hiệu vi phạm OCP.

---

# 3. Vấn đề của `if/elif` quá nhiều

Code:

```python
class PaymentService:

    def pay(self, method, amount):
        if method == "paypal":
            ...
        elif method == "stripe":
            ...
        elif method == "momo":
            ...
        elif method == "vnpay":
            ...
        elif method == "bank":
            ...
```

Ban đầu chỉ có 2 loại:

```text
PayPal
Stripe
```

Sau vài tháng:

```text
PayPal
Stripe
MoMo
VNPay
Bank
Visa
MasterCard
Crypto
...
```

Class ngày càng lớn.

Đây thường là dấu hiệu nên áp dụng:

```text
Polymorphism
+
OCP
+
Strategy
```

---

# 4. Refactor bằng Polymorphism

Tạo abstraction:

```python
from abc import ABC, abstractmethod


class PaymentMethod(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

PayPal:

```python
class PayPalPayment(PaymentMethod):

    def pay(self, amount):
        print(f"PayPal: {amount}")
```

Stripe:

```python
class StripePayment(PaymentMethod):

    def pay(self, amount):
        print(f"Stripe: {amount}")
```

Service:

```python
class PaymentService:

    def __init__(self, payment: PaymentMethod):
        self.payment = payment

    def pay(self, amount):
        self.payment.pay(amount)
```

Sử dụng:

```python
service = PaymentService(
    PayPalPayment()
)

service.pay(100)
```

Hoặc:

```python
service = PaymentService(
    StripePayment()
)

service.pay(100)
```

---

# 5. Thêm implementation mới

Bây giờ cần MoMo.

Chúng ta chỉ thêm:

```python
class MoMoPayment(PaymentMethod):

    def pay(self, amount):
        print(f"MoMo: {amount}")
```

Không sửa:

```python
PaymentService
```

Đây chính là:

```text
OCP
 ↓
Extension
 ↓
Không modification
```

---

# 6. Sơ đồ

```text
                 PaymentMethod
                       ▲
          ┌────────────┼────────────┐
          │            │            │
      PayPal         Stripe        MoMo
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                PaymentService
```

`PaymentService` phụ thuộc abstraction.

Các implementation mới được thêm bên ngoài.

---

# 7. OCP không có nghĩa “không bao giờ sửa code”

Đây là điểm rất quan trọng.

OCP **không có nghĩa**:

> “Code cũ tuyệt đối không được sửa.”

Mà là:

> Với những **variation/extension có thể dự đoán trước**, thiết kế abstraction để thêm implementation mới mà không phải sửa client chính.

Ví dụ:

```text
PaymentMethod
```

là variation point.

```text
Parser
```

là variation point.

```text
Notification
```

là variation point.

---

# 8. OCP + Crawler

Đây là ví dụ quan trọng nhất hôm nay.

Giả sử crawler hỗ trợ:

```text
Site A
Site B
```

Code không tốt:

```python
class Crawler:

    def crawl(self, site, html):

        if site == "site_a":
            # parse Site A
            ...

        elif site == "site_b":
            # parse Site B
            ...
```

Thêm Site C:

```python
elif site == "site_c":
    ...
```

Thêm Site D:

```python
elif site == "site_d":
    ...
```

Crawler ngày càng lớn.

---

# 9. Refactor Parser

Tạo interface:

```python
from abc import ABC, abstractmethod


class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

Site A:

```python
class SiteAParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Story A"
        }
```

Site B:

```python
class SiteBParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Story B"
        }
```

Crawler:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

---

# 10. Thêm Site C

Chỉ cần:

```python
class SiteCParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Story C"
        }
```

Không cần sửa:

```python
Crawler
```

Đây là OCP rất rõ ràng.

---

# 11. OCP + Factory

Buổi 23 chúng ta đã học Factory.

Bây giờ kết hợp:

```text
Factory
   ↓
chọn implementation

Polymorphism
   ↓
thực thi behavior

OCP
   ↓
thêm implementation mới
```

Ví dụ:

```python
class ParserFactory:

    _parsers = {
        "site_a": SiteAParser,
        "site_b": SiteBParser,
    }

    @classmethod
    def create(cls, site):
        return cls._parsers[site]()
```

Sử dụng:

```python
parser = ParserFactory.create("site_a")

crawler = Crawler(parser)

story = crawler.crawl(html)
```

---

# 12. Thêm Site C

Đơn giản:

```python
class SiteCParser(StoryParser):

    def parse(self, html):
        ...
```

và đăng ký:

```python
ParserFactory._parsers["site_c"] = SiteCParser
```

Hoặc tốt hơn, dùng registration:

```python
class ParserFactory:

    _parsers = {}

    @classmethod
    def register(cls, name, parser_cls):
        cls._parsers[name] = parser_cls

    @classmethod
    def create(cls, name):
        try:
            parser_cls = cls._parsers[name]
        except KeyError:
            raise ValueError(
                f"Unknown parser: {name}"
            )

        return parser_cls()
```

Đăng ký:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)

ParserFactory.register(
    "site_b",
    SiteBParser,
)
```

Sau này:

```python
ParserFactory.register(
    "site_c",
    SiteCParser,
)
```

---

# 13. OCP + Plugin Architecture

Đây là nơi OCP trở nên rất mạnh.

Kiến trúc:

```text
                    Parser
                      ▲
        ┌─────────────┼─────────────┐
        │             │             │
     Plugin A      Plugin B      Plugin C
        │             │             │
     Site A          Site B        Site C
```

Core application không cần biết chi tiết:

```text
Site A
Site B
Site C
```

Plugin cung cấp implementation.

Đây chính là nền tảng của **Plugin Architecture**.

---

# 14. Một ví dụ khác — Notification

Không tốt:

```python
class NotificationService:

    def send(self, channel, message):

        if channel == "email":
            ...

        elif channel == "sms":
            ...

        elif channel == "telegram":
            ...
```

Thêm Discord:

```python
elif channel == "discord":
    ...
```

Class phải sửa.

---

## Thiết kế OCP

```python
class Notification:

    def send(self, message):
        raise NotImplementedError
```

Email:

```python
class EmailNotification(Notification):

    def send(self, message):
        print(f"Email: {message}")
```

SMS:

```python
class SMSNotification(Notification):

    def send(self, message):
        print(f"SMS: {message}")
```

Telegram:

```python
class TelegramNotification(Notification):

    def send(self, message):
        print(f"Telegram: {message}")
```

Service:

```python
class NotificationService:

    def __init__(self, notification):
        self.notification = notification

    def send(self, message):
        self.notification.send(message)
```

Thêm Discord:

```python
class DiscordNotification(Notification):

    def send(self, message):
        print(f"Discord: {message}")
```

Không sửa:

```python
NotificationService
```

---

# 15. OCP + Strategy Pattern

Bạn sẽ học Strategy ở **Buổi 35**, nhưng cần biết mối liên hệ từ bây giờ.

Ví dụ:

```text
PaymentService
      │
      ▼
PaymentStrategy
      ▲
 ┌────┼────┐
 │    │    │
Card PayPal Bank
```

Mỗi strategy là một extension.

OCP giúp:

```text
Thêm Strategy
      ↓
Không sửa Service
```

---

# 16. OCP + Dependency Injection

Ba bài gần đây kết hợp rất đẹp:

```text
Buổi 24
Composition
      ↓
Buổi 25
Aggregation
      ↓
Buổi 26
Dependency Injection
      ↓
Buổi 27
SRP
      ↓
Buổi 28
OCP
```

Ví dụ:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser
```

DI cho phép inject:

```python
SiteAParser()
```

hoặc:

```python
SiteBParser()
```

OCP đảm bảo có thể thêm:

```python
SiteCParser()
```

mà không sửa `Crawler`.

---

# 17. OCP + SRP

SRP nói:

> Tách responsibility.

OCP nói:

> Thiết kế để behavior có thể mở rộng.

Ví dụ:

```text
SRP
 ↓
Parser responsibility
 ↓
StoryParser
```

Sau đó:

```text
OCP
 ↓
SiteAParser
SiteBParser
SiteCParser
```

Kết quả:

```text
StoryParser
    ▲
    │
    ├── SiteAParser
    ├── SiteBParser
    └── SiteCParser
```

Đây là cách hai nguyên tắc bổ trợ nhau.

---

# 18. Một lỗi phổ biến: Abstract class nhưng vẫn vi phạm OCP

Có ABC chưa chắc đã có OCP.

Ví dụ:

```python
class Parser(ABC):
    ...
```

nhưng:

```python
class Crawler:

    def crawl(self, parser_type):

        if parser_type == "a":
            parser = SiteAParser()

        elif parser_type == "b":
            parser = SiteBParser()

        elif parser_type == "c":
            parser = SiteCParser()
```

Vẫn có vấn đề.

Vì mỗi parser mới lại buộc sửa `Crawler`.

Tốt hơn:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser
```

Creation responsibility chuyển sang:

```text
Factory / Composition Root
```

---

# 19. Một nguyên tắc rất quan trọng

Đừng hỏi:

> “Tôi có thể áp dụng OCP ở đâu?”

Hãy hỏi:

> **“Trong hệ thống này, cái gì có khả năng thay đổi thường xuyên?”**

Ví dụ crawler:

```text
Site parser
    ↓
thường xuyên thay đổi

Database
    ↓
có thể thay đổi

HTTP client
    ↓
có thể thay đổi

Business rules
    ↓
có thể thay đổi
```

Đó là những nơi nên thiết kế extension point.

---

# 20. Không nên abstraction quá sớm

Sai lầm:

```python
class AbstractAnimalFactoryProviderStrategyManager:
    ...
```

trong khi application chỉ có:

```text
Dog
Cat
```

Không cần tạo 10 abstraction.

OCP không yêu cầu:

> “Mọi thứ đều phải có interface.”

Hãy tạo abstraction ở nơi có **variation thực sự**.

---

# 21. Ví dụ thực tế với Storage

Giả sử:

```text
Storage
 ├── SQLite
 ├── PostgreSQL
 └── JSON
```

Interface:

```python
from abc import ABC, abstractmethod


class StoryStorage(ABC):

    @abstractmethod
    def save(self, story):
        pass
```

SQLite:

```python
class SQLiteStorage(StoryStorage):

    def save(self, story):
        print("Save SQLite")
```

JSON:

```python
class JSONStorage(StoryStorage):

    def save(self, story):
        print("Save JSON")
```

Crawler:

```python
class StoryService:

    def __init__(self, storage):
        self.storage = storage

    def save(self, story):
        self.storage.save(story)
```

Thêm:

```python
class PostgreSQLStorage(StoryStorage):

    def save(self, story):
        print("Save PostgreSQL")
```

`StoryService` không đổi.

---

# 22. OCP ở cấp hệ thống

Một application tốt thường có:

```text
                    Core
                     │
              stable abstractions
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   SQLite Plugin  Site Plugin  HTTP Plugin
```

Core tương đối ổn định.

Các implementation nằm bên ngoài.

Khi thêm:

```text
Site D
```

ta mở rộng:

```text
Plugin D
```

thay vì sửa core.

Đây chính là tinh thần OCP.

---

# 23. Bài tập 1 — Payment

Code:

```python
class PaymentService:

    def pay(self, method, amount):

        if method == "card":
            ...

        elif method == "paypal":
            ...

        elif method == "momo":
            ...
```

Hãy refactor thành:

```text
PaymentMethod
    ▲
    ├── CardPayment
    ├── PayPalPayment
    └── MoMoPayment

PaymentService
```

Yêu cầu:

```python
service = PaymentService(
    CardPayment()
)
```

---

# 24. Bài tập 2 — Parser

Thiết kế:

```text
StoryParser
    ▲
    ├── SiteAParser
    ├── SiteBParser
    └── SiteCParser
```

Sau đó:

```python
crawler = Crawler(
    parser=SiteAParser()
)
```

Crawler không được có:

```python
if site == ...
elif site == ...
```

---

# 25. Bài tập 3 — Storage

Tạo:

```text
StoryStorage
    ▲
    ├── SQLiteStorage
    ├── JSONStorage
    └── MemoryStorage
```

Sau đó:

```python
service = StoryService(
    storage=MemoryStorage()
)
```

Test không cần SQLite.

---

# 26. Bài tập nâng cao — Plugin Parser

Thiết kế:

```text
ParserFactory
       │
       ├── register()
       └── create()
```

Các parser:

```text
SiteAParser
SiteBParser
SiteCParser
```

Có thể:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)
```

và:

```python
parser = ParserFactory.create("site_a")
```

### Yêu cầu quan trọng

Thêm:

```text
SiteDParser
```

không được sửa:

```text
Crawler
Parser
ParserFactory.create()
```

Chỉ cần thêm implementation và registration.

Đây là bài tập rất tốt để chuẩn bị cho **Plugin Architecture** mà bạn đang học ở các track khác.

---

# 27. Công thức tư duy OCP

Khi gặp code:

```python
if type == "A":
    ...
elif type == "B":
    ...
elif type == "C":
    ...
```

hãy tự hỏi:

```text
Các nhánh này có phải những implementation
của cùng một abstraction không?
```

Nếu có:

```text
if/elif
   ↓
Polymorphism
   ↓
Interface / ABC
   ↓
Dependency Injection
   ↓
OCP
```

Đây là một trong những pattern refactoring quan trọng nhất trong OOP.

---

# 28. Tổng kết Buổi 28

### OCP:

```text
Open for Extension
Closed for Modification
```

### Không tốt:

```text
Service
 ├── if A
 ├── if B
 ├── if C
 └── if D
```

Thêm feature:

```text
→ sửa Service
```

### Tốt hơn:

```text
              Interface
                  ▲
       ┌──────────┼──────────┐
       │          │          │
       A          B          C
```

Thêm feature:

```text
D
↓
thêm implementation
```

không cần sửa client.

---

# 29. Chuỗi kiến thức hiện tại

```text
Composition
     ↓
Aggregation
     ↓
Dependency Injection
     ↓
SRP
     ↓
OCP
     ↓
LSP
     ↓
ISP
     ↓
DIP
```

Ở **Buổi 29 — Liskov Substitution Principle (LSP)**, chúng ta sẽ học một vấn đề rất dễ gặp khi dùng **Inheritance + Polymorphism**:

> **Nếu `B` kế thừa `A`, liệu tôi có thể thay `A` bằng `B` ở mọi nơi mà chương trình vẫn đúng không?**

Đây là nơi chúng ta sẽ mổ xẻ các ví dụ kinh điển như **Rectangle/Square**, đồng thời áp dụng LSP vào **Parser, Repository và Crawler**.
