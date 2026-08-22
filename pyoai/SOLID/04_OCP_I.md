# SOLID Deep Dive — Buổi 4

# Open/Closed Principle — OCP

Hôm nay chúng ta chuyển sang chữ **O**:

> **Open/Closed Principle — Open for extension, closed for modification.**

Đây là principle rất quan trọng nếu bạn muốn xây dựng những hệ thống như **crawler plugin, worker, CLI framework, payment system, notification system**.

---

# 1. OCP là gì?

Phát biểu kinh điển:

> **Software entities should be open for extension but closed for modification.**

Hiểu đơn giản:

> **Cho phép hệ thống mở rộng behavior mới mà hạn chế phải sửa code đã ổn định.**

Ví dụ bạn có:

```python
class DiscountService:

    def calculate(self, customer_type, price):
        if customer_type == "normal":
            return price

        if customer_type == "vip":
            return price * 0.9

        if customer_type == "premium":
            return price * 0.8

        return price
```

Ban đầu:

```text
normal
vip
premium
```

Không vấn đề.

Nhưng requirement mới:

```text
gold
silver
student
employee
new_user
black_friday
christmas
...
```

Bạn phải liên tục sửa:

```python
DiscountService
```

Đây là dấu hiệu OCP có vấn đề.

---

# 2. “Open” nghĩa là gì?

Open không có nghĩa:

> Class phải cho phép mọi thứ thay đổi.

Mà là:

> **Hệ thống có một điểm mở rộng rõ ràng để thêm behavior mới.**

Ví dụ:

```text
DiscountService
       ↓
DiscountStrategy
       ↑
 ┌─────┼──────┬────────┐
 ↓     ↓      ↓        ↓
Normal VIP   Premium  Student
```

Muốn thêm:

```text
EmployeeDiscount
```

ta thêm:

```python
class EmployeeDiscount:
    ...
```

thay vì sửa logic trung tâm.

---

# 3. “Closed” nghĩa là gì?

Không có nghĩa:

> Code không bao giờ được sửa.

Điều này rất quan trọng.

Nếu business rule thay đổi:

```text
VIP discount:
10%
→
15%
```

thì đương nhiên code phải thay đổi.

“Closed for modification” có nghĩa:

> **Đối với một loại variation đã được xác định, code ổn định không cần liên tục bị sửa mỗi khi thêm implementation mới.**

---

# 4. OCP giải quyết vấn đề gì?

OCP chủ yếu giải quyết:

```text
Change
+
Variation
+
Extension
```

Ví dụ:

```text
Notification
```

Hiện tại:

```text
Email
```

Ngày mai:

```text
Telegram
Discord
Slack
SMS
Webhook
```

Thiết kế tệ:

```python
class NotificationService:

    def send(self, channel, message):

        if channel == "email":
            ...

        elif channel == "telegram":
            ...

        elif channel == "discord":
            ...

        elif channel == "slack":
            ...
```

Mỗi channel mới:

```text
→ sửa NotificationService
```

OCP hướng chúng ta tới:

```text
Notification
     ↓
   abstraction
     ↑
 ┌───┼────┬──────┐
 ↓   ↓    ↓      ↓
Email Telegram Discord Slack
```

---

# 5. OCP không có nghĩa là “không dùng if”

Đây là một hiểu lầm phổ biến.

Không phải:

```python
if ...
```

→ vi phạm OCP.

Ví dụ:

```python
def is_valid_age(age):
    if age < 0:
        return False

    if age > 150:
        return False

    return True
```

Không có lý do phải biến nó thành:

```text
AgeValidator
NegativeAgeValidator
MaximumAgeValidator
...
```

OCP chỉ đáng quan tâm khi có **một axis of variation** mà ta dự kiến sẽ mở rộng.

---

# 6. Axis of Variation

Đây là khái niệm rất quan trọng.

Giả sử:

```python
def send_notification(channel, message):
    if channel == "email":
        ...
    elif channel == "telegram":
        ...
    elif channel == "discord":
        ...
```

Axis of variation là:

```text
channel
```

Có thể có:

```text
Email
Telegram
Discord
Slack
```

Do đó ta nên tạo abstraction quanh:

```text
Notification Channel
```

---

# 7. Ví dụ thực tế — Payment

Code ban đầu:

```python
class PaymentService:

    def pay(self, method, amount):

        if method == "cash":
            return self.pay_cash(amount)

        elif method == "bank":
            return self.pay_bank(amount)

        elif method == "card":
            return self.pay_card(amount)

        elif method == "paypal":
            return self.pay_paypal(amount)
```

Mỗi lần thêm:

```text
Stripe
MoMo
VNPay
Apple Pay
Google Pay
```

phải sửa `PaymentService`.

Đây là kiến trúc dễ trở thành:

```text
if/elif hell
```

---

# 8. Strategy Pattern

Một giải pháp kinh điển là **Strategy Pattern**.

Ta tạo abstraction:

```python
from abc import ABC, abstractmethod


class PaymentStrategy(ABC):

    @abstractmethod
    def pay(self, amount: float) -> None:
        ...
```

Sau đó:

```python
class CashPayment(PaymentStrategy):

    def pay(self, amount: float) -> None:
        print(f"Pay cash: {amount}")
```

```python
class CardPayment(PaymentStrategy):

    def pay(self, amount: float) -> None:
        print(f"Pay card: {amount}")
```

```python
class BankPayment(PaymentStrategy):

    def pay(self, amount: float) -> None:
        print(f"Pay bank: {amount}")
```

Context:

```python
class PaymentService:

    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def pay(self, amount: float):
        self.strategy.pay(amount)
```

Bây giờ:

```python
service = PaymentService(
    CardPayment()
)

service.pay(100)
```

---

# 9. OCP đã xuất hiện ở đâu?

Khi muốn thêm:

```python
class PaypalPayment(PaymentStrategy):

    def pay(self, amount: float) -> None:
        print(f"Pay PayPal: {amount}")
```

Ta không cần sửa:

```python
PaymentService
```

Ta chỉ thêm:

```text
PaypalPayment
```

Đó chính là:

```text
Extension
   ↓
new implementation
   ↓
existing code unchanged
```

---

# 10. Nhưng Strategy chưa giải quyết hoàn toàn

Có một vấn đề.

Ta vẫn phải viết:

```python
if method == "card":
    strategy = CardPayment()

elif method == "bank":
    strategy = BankPayment()

elif method == "paypal":
    strategy = PaypalPayment()
```

Ví dụ:

```python
class PaymentFactory:

    def create(self, method):

        if method == "card":
            return CardPayment()

        if method == "bank":
            return BankPayment()

        if method == "paypal":
            return PaypalPayment()

        raise ValueError(...)
```

Khi thêm PayPal:

```text
→ Factory phải sửa.
```

Điều này không nhất thiết là vấn đề.

Nhưng nếu loại variation này xuất hiện rất thường xuyên, ta có thể đi xa hơn.

---

# 11. Registry Pattern

Thay vì:

```python
if method == ...
```

ta có registry:

```python
PAYMENT_METHODS = {
    "cash": CashPayment,
    "card": CardPayment,
    "bank": BankPayment,
}
```

Factory:

```python
class PaymentFactory:

    def create(self, method):
        try:
            payment_class = PAYMENT_METHODS[method]
        except KeyError:
            raise ValueError(
                f"Unknown payment method: {method}"
            )

        return payment_class()
```

Thêm implementation:

```python
class PaypalPayment(PaymentStrategy):

    def pay(self, amount):
        print(f"Pay PayPal: {amount}")
```

và đăng ký:

```python
PAYMENT_METHODS["paypal"] = PaypalPayment
```

---

# 12. Plugin Architecture

Bây giờ hãy nhìn xa hơn.

Thay vì hard-code:

```python
PAYMENT_METHODS["paypal"] = PaypalPayment
```

ta có thể cho plugin tự đăng ký.

Ví dụ:

```python
class PaymentRegistry:

    def __init__(self):
        self._strategies = {}

    def register(self, name, strategy):
        self._strategies[name] = strategy

    def create(self, name):
        strategy = self._strategies[name]
        return strategy()
```

Plugin:

```python
registry.register(
    "paypal",
    PaypalPayment,
)
```

Core system không cần biết:

```text
Paypal
Stripe
MoMo
VNPay
```

được viết ở đâu.

Đây chính là tư duy:

```text
Core
 ↓
Extension Point
 ↓
Plugin
```

---

# 13. Đây chính là kiến trúc crawler

Rất gần với project crawler của bạn.

Giả sử ban đầu:

```python
class Crawler:

    def crawl(self, source, url):

        if source == "a":
            ...

        elif source == "b":
            ...

        elif source == "c":
            ...
```

Khi có:

```text
Source A
Source B
Source C
...
Source 50
```

thì:

```text
Crawler
```

trở thành một đống:

```text
if/elif
```

OCP gợi ý:

```text
CrawlerPlugin
      ↑
 ┌────┼─────┬─────┐
 ↓    ↓     ↓     ↓
SiteA SiteB SiteC SiteD
```

---

# 14. Thiết kế crawler plugin

Ví dụ:

```python
from abc import ABC, abstractmethod


class CrawlerPlugin(ABC):

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    def crawl(self, url: str):
        ...
```

Plugin:

```python
class SiteAPlugin(CrawlerPlugin):

    def can_handle(self, url: str) -> bool:
        return "site-a.com" in url

    def crawl(self, url: str):
        ...
```

Plugin khác:

```python
class SiteBPlugin(CrawlerPlugin):

    def can_handle(self, url: str) -> bool:
        return "site-b.com" in url

    def crawl(self, url: str):
        ...
```

Core:

```python
class Crawler:

    def __init__(self, plugins):
        self.plugins = plugins

    def crawl(self, url):
        for plugin in self.plugins:
            if plugin.can_handle(url):
                return plugin.crawl(url)

        raise ValueError(
            f"No plugin for {url}"
        )
```

Bây giờ thêm site:

```python
class SiteCPlugin(CrawlerPlugin):
    ...
```

Không cần sửa `Crawler`.

Đây là OCP rất rõ.

---

# 15. OCP và Polymorphism

Có thể xem OCP thường được xây dựng từ:

```text
Abstraction
     +
Polymorphism
     +
Composition
```

Ví dụ:

```text
PaymentService
      ↓
PaymentStrategy
      ↑
 ┌────┼─────┐
 ↓    ↓     ↓
Card Cash  Bank
```

`PaymentService` không cần biết implementation cụ thể.

Nó chỉ biết:

```python
strategy.pay(amount)
```

Đây chính là polymorphism.

---

# 16. ABC hay Protocol?

Trong Python hiện đại, chúng ta có hai cách phổ biến.

## ABC

```python
from abc import ABC, abstractmethod


class PaymentStrategy(ABC):

    @abstractmethod
    def pay(self, amount):
        ...
```

Implementation:

```python
class CardPayment(PaymentStrategy):

    def pay(self, amount):
        ...
```

ABC cung cấp:

```text
Explicit inheritance
Runtime enforcement
Nominal interface
```

---

## Protocol

Python còn có:

```python
from typing import Protocol


class PaymentStrategy(Protocol):

    def pay(self, amount: float) -> None:
        ...
```

Implementation không cần kế thừa:

```python
class CardPayment:

    def pay(self, amount: float) -> None:
        ...
```

Python nhìn theo:

```text
CardPayment
    ↓
có method pay()
    ↓
phù hợp Protocol
```

Đây là:

> **Structural typing**

rất phù hợp với triết lý:

> **If it quacks like a duck, it is a duck.**

---

# 17. OCP với Protocol

Ví dụ:

```python
from typing import Protocol


class Notifier(Protocol):

    def send(self, message: str) -> None:
        ...
```

Email:

```python
class EmailNotifier:

    def send(self, message: str) -> None:
        print("Email:", message)
```

Telegram:

```python
class TelegramNotifier:

    def send(self, message: str) -> None:
        print("Telegram:", message)
```

Use case:

```python
class CrawlStoryUseCase:

    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def execute(self):
        ...
```

Use case không cần biết:

```text
EmailNotifier
TelegramNotifier
DiscordNotifier
```

Nó chỉ biết:

```text
Notifier
```

---

# 18. Một điểm cực kỳ quan trọng

OCP không nói:

> “Tất cả mọi thứ phải dùng interface.”

Không.

Ví dụ:

```python
class Story:

    def __init__(self, title):
        self.title = title
```

Không cần:

```text
IStory
StoryInterface
AbstractStory
DefaultStory
BaseStory
```

Nếu `Story` không có variation cần extension thì abstraction đó không đem lại giá trị.

---

# 19. OCP và YAGNI

Có một nguyên tắc rất quan trọng:

> **You Aren't Gonna Need It.**

Đừng thiết kế:

```text
PaymentStrategy
PaymentFactory
PaymentRegistry
PaymentPluginLoader
PaymentPluginManager
PaymentExtensionPoint
```

nếu hiện tại chỉ có:

```text
Card
```

và không có lý do thực tế để mở rộng.

Một thiết kế tốt:

```text
Current requirement
+
Known variation
+
Reasonable extension point
```

Không phải:

```text
Imagine every possible future requirement
```

---

# 20. OCP và modification

Một câu hỏi nâng cao:

> “Nếu tôi thêm plugin, tôi vẫn phải sửa registry. Vậy có vi phạm OCP không?”

Không nhất thiết.

Ví dụ:

```python
registry.register(
    "site-a",
    SiteAPlugin,
)
```

Đây là **configuration/composition**, không phải sửa core behavior.

Ta phân biệt:

```text
Core logic
     ↓
không sửa

Composition/configuration
     ↓
có thể thay đổi
```

Đây là một tư duy rất quan trọng trong architecture.

---

# 21. OCP không phải “zero modification”

Không thể có hệ thống:

```text
never modify any code
```

Thực tế:

```text
Bug fix
Requirement change
Business rule change
Refactoring
```

vẫn cần sửa code.

OCP chỉ giúp:

> **Một loại extension mới không buộc chúng ta sửa những phần core đã ổn định.**

---

# 22. Ví dụ: Discount Engine

Thiết kế xấu:

```python
class DiscountService:

    def calculate(self, customer_type, price):

        if customer_type == "normal":
            return price

        elif customer_type == "vip":
            return price * 0.9

        elif customer_type == "student":
            return price * 0.8

        elif customer_type == "employee":
            return price * 0.7

        raise ValueError(...)
```

Refactor:

```python
from typing import Protocol


class DiscountStrategy(Protocol):

    def calculate(self, price: float) -> float:
        ...
```

VIP:

```python
class VipDiscount:

    def calculate(self, price: float) -> float:
        return price * 0.9
```

Student:

```python
class StudentDiscount:

    def calculate(self, price: float) -> float:
        return price * 0.8
```

Context:

```python
class DiscountService:

    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def calculate(self, price: float) -> float:
        return self.strategy.calculate(price)
```

---

# 23. Nhưng có một vấn đề mới

Nếu client phải tự làm:

```python
if customer_type == "vip":
    strategy = VipDiscount()

elif customer_type == "student":
    strategy = StudentDiscount()
```

thì `if/elif` chỉ bị **đẩy ra ngoài**.

Đây là một dấu hiệu quan trọng.

Khi refactor OCP, đừng chỉ:

> “Di chuyển `if` sang class khác.”

Hãy hỏi:

> **Ai sở hữu variation?**

Đây là vấn đề architecture sâu hơn.

---

# 24. Registry hoàn chỉnh hơn

```python
class DiscountRegistry:

    def __init__(self):
        self._strategies = {}

    def register(self, name, strategy):
        self._strategies[name] = strategy

    def get(self, name):
        try:
            return self._strategies[name]
        except KeyError:
            raise ValueError(
                f"Unknown discount: {name}"
            )
```

Composition:

```python
registry = DiscountRegistry()

registry.register(
    "vip",
    VipDiscount(),
)

registry.register(
    "student",
    StudentDiscount(),
)
```

Use case:

```python
strategy = registry.get("vip")

price = strategy.calculate(100)
```

---

# 25. OCP trong crawler framework

Đây là phần bạn nên đặc biệt chú ý.

Ta có:

```text
Crawler Framework
```

Core:

```text
CrawlerEngine
CrawlerPlugin
CrawlerRegistry
```

Plugin:

```text
NovelSourceA
NovelSourceB
NovelSourceC
```

Kiến trúc:

```text
                    ┌───────────────────┐
                    │   CrawlerEngine   │
                    └─────────┬─────────┘
                              │
                              ↓
                    ┌───────────────────┐
                    │  CrawlerRegistry  │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
        ┌─────────┐      ┌─────────┐      ┌─────────┐
        │ Site A  │      │ Site B  │      │ Site C  │
        │ Plugin  │      │ Plugin  │      │ Plugin  │
        └─────────┘      └─────────┘      └─────────┘
```

Core không cần:

```text
if site == A
if site == B
if site == C
```

Đây là **OCP + Plugin Architecture**.

---

# 26. SRP vs OCP

Hai principle đầu tiên khác nhau:

### SRP hỏi:

> **Class này có quá nhiều responsibility không?**

### OCP hỏi:

> **Khi thêm variation mới, tôi có phải sửa code ổn định không?**

Ví dụ:

```text
SRP
 ↓
tách responsibility
```

Trong khi:

```text
OCP
 ↓
tạo extension point
```

Hai principle bổ sung cho nhau.

---

# 27. Ví dụ kết hợp SRP + OCP

Không tốt:

```python
class NotificationService:

    def send(self, channel, message):

        if channel == "email":
            ...

        elif channel == "telegram":
            ...

        elif channel == "discord":
            ...
```

Vấn đề:

```text
SRP
+
OCP
```

Refactor:

```text
NotificationService
        ↓
Notifier
        ↑
 ┌──────┼────────┐
 ↓      ↓        ↓
Email Telegram Discord
```

Bây giờ:

### SRP

Mỗi notifier tập trung vào notification mechanism của nó.

### OCP

Thêm notifier mới mà không sửa core notification logic.

---

# 28. Một heuristic tìm OCP violation

Khi code có:

```python
if type == ...
elif type == ...
elif type == ...
```

hoặc:

```python
match value:
    case "a":
        ...
    case "b":
        ...
    case "c":
        ...
```

đừng lập tức nói:

> “Vi phạm OCP!”

Hãy hỏi:

### Câu 1

Các case này có khả năng tăng lên không?

### Câu 2

Các case có behavior khác nhau không?

### Câu 3

Một case mới có thường xuyên được thêm không?

### Câu 4

Mỗi lần thêm case có phải sửa core logic không?

### Câu 5

Có một abstraction tự nhiên nào đại diện cho variation này không?

Nếu câu trả lời chủ yếu là **có**, OCP có thể giúp ích.

---

# 29. Bài tập Buổi 4

Cho code:

```python
class FileExporter:

    def export(self, format, data):

        if format == "json":
            return self.export_json(data)

        elif format == "csv":
            return self.export_csv(data)

        elif format == "xml":
            return self.export_xml(data)

        elif format == "yaml":
            return self.export_yaml(data)

        else:
            raise ValueError(
                f"Unsupported format: {format}"
            )

    def export_json(self, data):
        ...

    def export_csv(self, data):
        ...

    def export_xml(self, data):
        ...

    def export_yaml(self, data):
        ...
```

## Bài 1

Xác định **axis of variation**.

## Bài 2

Giải thích tại sao code này có vấn đề với OCP.

## Bài 3

Thiết kế abstraction:

```python
class ???:
    ...
```

## Bài 4

Viết:

```text
JsonExporter
CsvExporter
XmlExporter
YamlExporter
```

## Bài 5

Thiết kế:

```text
ExporterRegistry
```

để có thể:

```python
registry.register("json", JsonExporter())
registry.register("csv", CsvExporter())
```

## Bài 6 — Deep Dive

Thêm:

```text
MarkdownExporter
```

và chứng minh rằng:

```text
FileExporter
```

không cần sửa.

---

# 30. Bài tập nâng cao — Crawler

Thiết kế:

```text
CrawlerPlugin
```

với:

```python
class CrawlerPlugin(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str) -> Story:
        ...
```

Sau đó tạo:

```text
SiteAPlugin
SiteBPlugin
SiteCPlugin
```

và:

```text
CrawlerRegistry
CrawlerEngine
```

Yêu cầu:

```text
CrawlerEngine
```

**không được biết cụ thể Site A/B/C.**

---

# 31. Kiến thức cần nhớ

Sau Buổi 4, hãy giữ mental model này:

```text
                 OCP
                  │
                  ↓
        Identify variation
                  │
                  ↓
        Create extension point
                  │
                  ↓
             Abstraction
                  │
                  ↓
           Polymorphism
                  │
                  ↓
             Extension
```

Và đặc biệt:

> **OCP không phải “không bao giờ sửa code”.**

Nó là:

> **Thiết kế để những loại thay đổi có thể dự đoán được được xử lý bằng extension thay vì liên tục sửa core logic.**

---

## Một câu hỏi rất quan trọng cho buổi sau

Giả sử ta có:

```python
class Bird:

    def fly(self):
        ...
```

sau đó:

```python
class Penguin(Bird):

    def fly(self):
        raise NotImplementedError
```

Thiết kế này nhìn qua có vẻ hợp lý vì:

```text
Penguin IS-A Bird
```

nhưng client viết:

```python
def make_bird_fly(bird: Bird):
    bird.fly()
```

lại có thể crash.

**Tại sao?**

Đây chính là vấn đề của **Liskov Substitution Principle — LSP**, và là nội dung của **Buổi 5**.
