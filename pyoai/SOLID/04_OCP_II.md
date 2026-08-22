# SOLID Deep Dive — Buổi 5

# OCP Deep Dive — Variation Point & Thiết kế hệ thống mở rộng

Ở Buổi 4, chúng ta đã biết OCP:

> **Software entities should be open for extension, but closed for modification.**

Nhưng nếu chỉ hiểu là:

> “Đừng dùng `if/elif`, hãy dùng Strategy.”

thì **chưa đủ sâu**.

Buổi này chúng ta sẽ đi vào câu hỏi quan trọng nhất:

> **Làm thế nào xác định một điểm trong hệ thống nên được thiết kế để mở rộng?**

---

# 1. OCP thực chất không phải "cấm sửa code"

Đây là hiểu lầm đầu tiên cần loại bỏ.

OCP **không nói**:

```text
❌ Code đã viết thì không được sửa.
```

Nếu hiểu như vậy thì gần như không thể phát triển phần mềm.

OCP nói về:

```text
Một phần ổn định
        +
Một phần thường xuyên thay đổi
```

Ta muốn:

```text
phần ổn định
      ↓
không phải sửa
      ↑
phần thay đổi
      ↓
extension
```

---

# 2. Stable Core và Variable Behavior

Hãy lấy ví dụ ứng dụng đọc truyện.

Core:

```text
ReadStoryUseCase
```

Nghiệp vụ:

```text
1. nhận story
2. lấy chapter
3. kiểm tra chapter
4. lưu kết quả
```

Nhưng nguồn truyện có thể thay đổi:

```text
SiteA
SiteB
SiteC
SiteD
```

Ta có:

```text
                Core
                 │
        ┌────────┴────────┐
        ↓                 ↓
     stable            variable
   business             source
     logic
```

OCP muốn **variable behavior** nằm sau một extension point.

---

# 3. Variation Point

Đây là khái niệm quan trọng nhất của Buổi 5.

> **Variation Point là nơi behavior của hệ thống có khả năng thay đổi.**

Ví dụ:

```python id="b8tq2w"
class StoryCrawler:

    def crawl(self, url):
        ...
```

Có thể có:

```text
SiteA crawler
SiteB crawler
SiteC crawler
```

Ta có:

```text
StoryCrawler
     ↑
     ├── SiteACrawler
     ├── SiteBCrawler
     └── SiteCCrawler
```

`StoryCrawler` chính là một **variation point**.

---

# 4. Không phải mọi chỗ khác nhau đều là Variation Point

Ví dụ:

```python id="g2v6m7"
x = 10
y = 20
```

Hai giá trị khác nhau không có nghĩa:

```text
x
y
```

là variation point.

Variation point có ý nghĩa khi:

```text
behavior có khả năng thay đổi
+
thay đổi có tính hệ thống
```

---

# 5. Tìm Variation Point bằng câu hỏi

Khi thiết kế hệ thống, hãy hỏi:

### Câu 1

> Cái gì có khả năng thay đổi?

Ví dụ:

```text
database
payment provider
crawler source
file format
notification channel
```

### Câu 2

> Nó thay đổi độc lập với phần còn lại không?

Ví dụ:

```text
SQLite → PostgreSQL
```

không nên buộc:

```text
Business logic
```

phải thay đổi.

### Câu 3

> Chúng ta có khả năng thêm implementation mới không?

Nếu:

```text
SiteA
SiteB
```

sau này có:

```text
SiteC
SiteD
```

thì đây là variation point rất rõ.

---

# 6. Ví dụ `if/elif`

Code:

```python id="j5smn5"
def calculate_shipping(order, method):

    if method == "standard":
        return order.total * 0.05

    elif method == "express":
        return order.total * 0.15

    elif method == "overnight":
        return order.total * 0.30
```

Có một variation point:

```text
shipping method
```

Behavior thay đổi theo:

```text
standard
express
overnight
```

---

# 7. Vấn đề với `if/elif`

Hiện tại:

```text
calculate_shipping()
        │
        ├── standard
        ├── express
        └── overnight
```

Thêm:

```text
drone
```

phải sửa:

```python id="6fhfqi"
elif method == "drone":
    ...
```

Đây là dấu hiệu OCP violation **nếu shipping method thực sự là một axis of variation**.

---

# 8. Strategy

Ta tách behavior:

```python id="2m6z1e"
from typing import Protocol


class ShippingStrategy(Protocol):

    def calculate(self, order) -> float:
        ...
```

Implementation:

```python id="8w9g6p"
class StandardShipping:

    def calculate(self, order):
        return order.total * 0.05
```

```python id="3y9q4g"
class ExpressShipping:

    def calculate(self, order):
        return order.total * 0.15
```

```python id="m6p1uj"
class OvernightShipping:

    def calculate(self, order):
        return order.total * 0.30
```

Core:

```python id="f0s1av"
class ShippingCalculator:

    def __init__(self, strategy: ShippingStrategy):
        self.strategy = strategy

    def calculate(self, order):
        return self.strategy.calculate(order)
```

---

# 9. Điều gì đã thay đổi?

Trước:

```text id="5xq0l3"
ShippingCalculator
      │
      ├── standard
      ├── express
      └── overnight
```

Sau:

```text id="4gr8zt"
                ShippingStrategy
                ↑       ↑       ↑
                │       │       │
           Standard Express Overnight
                │       │       │
                └───────┼───────┘
                        ↓
                ShippingCalculator
```

Core không cần biết implementation cụ thể.

---

# 10. Nhưng Strategy không phải lúc nào cũng tốt

Đây là điểm rất quan trọng.

Nếu chỉ có:

```python id="trqz6v"
if method == "standard":
    return 10
else:
    return 20
```

và behavior:

```text
không bao giờ mở rộng
```

thì tạo:

```text
ShippingStrategy
StandardShipping
ExpressShipping
```

có thể là **over-engineering**.

OCP phải được áp dụng dựa trên **changeability**, không phải vì "SOLID yêu cầu".

---

# 11. Predicting Change

Một kỹ năng quan trọng của architect:

> **Không chỉ nhìn code hiện tại, mà phải dự đoán nơi thay đổi có khả năng xảy ra.**

Ví dụ:

```text
PaymentProvider
```

thường có:

```text
Stripe
PayPal
Momo
VNPay
```

Đây là variation point có xác suất cao.

Trong khi:

```text
Order.total
```

không nhất thiết cần abstraction.

---

# 12. Stable vs Volatile

Một cách suy nghĩ rất hữu ích:

```text
Stable
------
Domain rules
Entity invariants
Value Objects
Core business policies


Volatile
--------
Database
HTTP API
Payment provider
Crawler website
UI framework
File format
External service
```

Không phải lúc nào cũng tuyệt đối, nhưng đây là heuristic tốt.

---

# 13. OCP và External Systems

Ví dụ:

```text
PaymentService
```

Không nên:

```python id="6p3s2f"
class PaymentService:

    def pay(self, provider, amount):

        if provider == "stripe":
            ...

        elif provider == "paypal":
            ...

        elif provider == "momo":
            ...
```

Tốt hơn:

```text
PaymentGateway
       ↑
 ┌─────┼──────┐
 ↓     ↓      ↓
Stripe PayPal Momo
```

---

# 14. Registry Pattern

Strategy giải quyết:

> "Behavior nào?"

Registry giải quyết:

> "Tìm implementation nào?"

Ví dụ:

```python id="p0x4em"
strategies = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
    "overnight": OvernightShipping(),
}
```

Sau đó:

```python id="k4f8e6"
strategy = strategies[method]

return strategy.calculate(order)
```

Không còn:

```text
if/elif/elif/elif
```

---

# 15. Registry + Factory

Ta có thể tách registry:

```python id="r6s9v8"
class ShippingRegistry:

    def __init__(self):
        self._strategies = {}

    def register(self, name, strategy):
        self._strategies[name] = strategy

    def get(self, name):
        return self._strategies[name]
```

Composition:

```python id="x1x0kn"
registry.register(
    "standard",
    StandardShipping(),
)

registry.register(
    "express",
    ExpressShipping(),
)
```

Thêm:

```python id="xps4gf"
registry.register(
    "drone",
    DroneShipping(),
)
```

Core không cần sửa.

---

# 16. Function-based Strategy

Python không nhất thiết phải dùng class.

Strategy có thể là function:

```python id="g7m9jc"
def standard_shipping(order):
    return order.total * 0.05
```

```python id="2y5d6p"
def express_shipping(order):
    return order.total * 0.15
```

Registry:

```python id="v7f0v2"
strategies = {
    "standard": standard_shipping,
    "express": express_shipping,
}
```

Đây là một cách rất Pythonic.

---

# 17. OCP + Duck Typing

Ta không nhất thiết cần:

```python id="b9by9n"
class StandardShipping(ShippingStrategy):
```

Chỉ cần object có:

```python id="3kjfgi"
calculate(order)
```

Ví dụ:

```python id="qkq6x1"
class DroneShipping:

    def calculate(self, order):
        return 100
```

Nếu dùng `Protocol`:

```python id="2w4k7m"
class ShippingStrategy(Protocol):

    def calculate(self, order) -> float:
        ...
```

`DroneShipping` tự nhiên phù hợp.

---

# 18. OCP + ABC

ABC:

```python id="qf6xas"
from abc import ABC, abstractmethod


class ShippingStrategy(ABC):

    @abstractmethod
    def calculate(self, order):
        ...
```

Implementation:

```python id="o1t7cb"
class ExpressShipping(ShippingStrategy):

    def calculate(self, order):
        return order.total * 0.15
```

ABC hữu ích khi bạn muốn:

```text
explicit inheritance
+
runtime enforcement
```

Nhưng không phải lúc nào cũng cần.

---

# 19. Protocol vs ABC trong OCP

### ABC

```text
nominal typing
```

Class phải:

```python id="w9u7h0"
class X(ShippingStrategy):
```

### Protocol

```text
structural typing
```

Chỉ cần:

```python id="n7m4v2"
class X:

    def calculate(...):
        ...
```

Python thường rất hợp với:

```text
Protocol + composition
```

cho extension point.

---

# 20. OCP + Dependency Injection

Strategy:

```python id="6x5f2v"
class ShippingService:

    def __init__(self, strategy):
        self.strategy = strategy
```

Composition Root:

```python id="g5v2e1"
service = ShippingService(
    strategy=ExpressShipping()
)
```

Core không biết:

```text
ExpressShipping
```

Đây là:

```text
OCP
+
DIP
+
DI
```

---

# 21. Runtime Extension

OCP trở nên rất mạnh khi extension xảy ra lúc runtime.

Ví dụ:

```python id="t1h8c0"
registry.register(
    "site_a",
    SiteACrawler(),
)
```

Sau đó plugin:

```python id="j2j0eg"
registry.register(
    "site_b",
    SiteBCrawler(),
)
```

Core:

```text
không sửa
```

Plugin:

```text
được thêm
```

---

# 22. Plugin Architecture

Ví dụ crawler:

```text id="4f8g2j"
CrawlerCore
    │
    └── CrawlerPlugin
            ↑
       ┌────┼────┐
       │    │    │
     SiteA SiteB SiteC
```

Core định nghĩa:

```python id="w4f5jr"
class CrawlerPlugin(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str):
        ...
```

Mỗi plugin:

```python id="t5x0z8"
class SiteACrawler:

    def can_handle(self, url):
        return "site-a.com" in url

    def crawl(self, url):
        ...
```

---

# 23. Đây mới là OCP thực sự

Khi SiteD xuất hiện:

```text
SiteD
```

ta không sửa:

```text
CrawlerCore
```

mà thêm:

```text
SiteDCrawler
```

Dependency:

```text id="m2yq72"
              CrawlerPlugin
             ↑      ↑      ↑
            A       B      C
```

Core đóng.

Extension mở.

---

# 24. Conditional Logic không phải lúc nào cũng vi phạm OCP

Ví dụ:

```python id="9m1e3k"
if user.is_admin:
    ...
```

Không nhất thiết là OCP violation.

Tại sao?

Vì:

```text
admin
normal user
```

có thể là **business rule cố định**.

Không phải variation point.

---

# 25. Một `if` không tự động là Code Smell

Đây là nguyên tắc rất quan trọng:

```text
if ≠ bad
```

Ví dụ:

```python id="wj7qpr"
if age < 18:
    raise UnderAgeError
```

Hoàn toàn bình thường.

Nhưng:

```python id="z7x2m3"
if provider == "stripe":
    ...
elif provider == "paypal":
    ...
elif provider == "momo":
    ...
elif provider == "vnpay":
    ...
elif provider == "new_provider":
    ...
```

có thể là variation point.

---

# 26. Conditional Complexity

Code smell bắt đầu rõ khi:

```text
if/elif
    ↓
tăng liên tục
    ↓
mỗi nhánh có logic riêng
    ↓
mỗi lần thêm behavior phải sửa core
```

Ví dụ:

```python id="9c1f3x"
if type == "pdf":
    parse_pdf()

elif type == "epub":
    parse_epub()

elif type == "mobi":
    parse_mobi()

elif type == "docx":
    parse_docx()
```

Đây là ứng viên rất tốt cho Strategy/Registry.

---

# 27. Dictionary Dispatch

Không phải lúc nào cần class.

```python id="4h6v8f"
PARSERS = {
    "pdf": parse_pdf,
    "epub": parse_epub,
    "mobi": parse_mobi,
}
```

Sau đó:

```python id="z4a6kx"
parser = PARSERS[file_type]

return parser(path)
```

Đây là một dạng:

> **OCP bằng function registry**

---

# 28. Nhưng dictionary dispatch chưa chắc đã giải quyết OCP hoàn toàn

Nếu:

```python id="c6y9w4"
PARSERS = {
    "pdf": parse_pdf,
    "epub": parse_epub,
}
```

nằm trong core và mỗi lần thêm parser phải sửa dictionary:

```python id="9g0x0h"
PARSERS["mobi"] = parse_mobi
```

thì core vẫn phải modification.

Muốn extension thực sự:

```text
registry
+
registration mechanism
```

phải cho phép plugin đăng ký từ bên ngoài.

---

# 29. Extension Point

Đây là khái niệm tiếp theo.

Một **extension point** là nơi hệ thống cho phép thêm behavior.

Ví dụ:

```python id="9d2e8j"
registry.register(
    "mobi",
    MobiParser(),
)
```

`register()` chính là một extension mechanism.

---

# 30. Explicit Extension

Ví dụ:

```python id="f3u0x5"
def configure(registry):

    registry.register("pdf", PdfParser())
    registry.register("epub", EpubParser())
```

Plugin:

```python id="x8y0b4"
def configure(registry):

    registry.register("mobi", MobiParser())
```

Application:

```python id="p7u8r1"
configure(core_registry)
configure(plugin_registry)
```

---

# 31. OCP và Configuration

Ví dụ:

```yaml id="c6b8j1"
parsers:
  - pdf
  - epub
  - mobi
```

Application đọc configuration rồi load implementation.

Đây cũng có thể là extension mechanism.

Nhưng cần cẩn thận:

```text
configuration
≠
architecture
```

Config chỉ thay đổi data/configuration.

Không phải mọi config đều cần OCP.

---

# 32. OCP và Plugin Discovery

Ở mức cao hơn:

```text
Application
     ↓
discover plugins
     ↓
load plugin
     ↓
register capability
     ↓
use capability
```

Ví dụ Python package có thể cung cấp plugin entry points.

Kiến trúc:

```text
Core
 ↓
Plugin Discovery
 ↓
Plugin A
Plugin B
Plugin C
```

Đây là nền tảng cho các hệ thống extensible lớn.

---

# 33. OCP trong Crawler Architecture

Đây là ví dụ sát với project của bạn.

Core:

```python id="h3d4u8"
class CrawlStoryUseCase:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self, url):
        return self.crawler.crawl(url)
```

Plugin:

```python id="1b6b8a"
class SiteACrawler:

    def crawl(self, url):
        ...
```

SiteB:

```python id="7w8r5v"
class SiteBCrawler:

    def crawl(self, url):
        ...
```

Core không cần:

```python id="r8n1tg"
if "site-a" in url:
    ...
elif "site-b" in url:
    ...
```

---

# 34. Nhưng cần thêm Router

Thực tế crawler thường cần:

```text
URL
 ↓
Which crawler?
 ↓
Crawler
```

Ta có:

```python id="4y4h3n"
class CrawlerPlugin(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str):
        ...
```

Router:

```python id="q7f4z0"
class CrawlerRouter:

    def __init__(self, plugins):
        self.plugins = plugins

    def resolve(self, url):
        for plugin in self.plugins:
            if plugin.can_handle(url):
                return plugin

        raise ValueError("No crawler found")
```

Thêm SiteC:

```text
SiteCCrawler
```

không sửa router.

Đây là OCP tốt.

---

# 35. Nhưng Router vẫn có vòng lặp

Một số người sẽ nói:

> "Có `for` rồi, vậy không OCP?"

Không.

Router không biết:

```text
SiteA
SiteB
SiteC
```

Nó chỉ biết abstraction:

```text
CrawlerPlugin
```

Vòng lặp là **stable algorithm**:

```text
tìm plugin phù hợp
```

Danh sách plugin là **extension data**.

Đây là distinction rất quan trọng.

---

# 36. OCP không có nghĩa "không có conditional"

Ví dụ:

```python id="5x6s0f"
for plugin in plugins:
    if plugin.can_handle(url):
        return plugin
```

Conditional này không nhất thiết vi phạm OCP.

Vì khi thêm plugin:

```text
không sửa algorithm
```

chỉ thêm object.

---

# 37. OCP và Algorithm Stability

Một thiết kế tốt thường có:

```text
Stable algorithm
        ↓
Extension points
        ↓
Variable implementations
```

Ví dụ:

```text
CrawlerRouter
    ↓
stable

CrawlerPlugin
    ↓
variable

SiteA/B/C
    ↓
extensions
```

---

# 38. OCP và Factory

Factory đơn giản:

```python id="azp9w5"
def create_parser(file_type):

    if file_type == "pdf":
        return PdfParser()

    if file_type == "epub":
        return EpubParser()
```

Thêm parser:

```text
sửa factory
```

OCP chưa tốt.

Có thể chuyển sang registry:

```python id="7d7i1u"
PARSERS = {}

def register(name, parser):
    PARSERS[name] = parser
```

Factory:

```python id="s2r9d4"
def create_parser(name):
    return PARSERS[name]()
```

---

# 39. Nhưng Factory có thể vẫn cần sửa

Đây là một insight quan trọng:

> **Factory Pattern không tự động đảm bảo OCP.**

Nếu factory chứa:

```python id="5c4x1k"
if type == ...
elif type == ...
elif type == ...
```

thì factory vẫn là variation hotspot.

Pattern chỉ hữu ích khi nó đặt extension point đúng chỗ.

---

# 40. OCP và Abstract Factory

Abstract Factory phù hợp khi một variation tạo ra **một family of related objects**.

Ví dụ:

```text
DatabaseFactory
      │
      ├── create_connection()
      ├── create_repository()
      └── create_transaction()
```

SQLite:

```text
SQLiteFactory
```

PostgreSQL:

```text
PostgresFactory
```

Đây là OCP ở cấp độ object family.

---

# 41. OCP và Template Method

Ví dụ:

```python id="8i1qz8"
class DataImporter:

    def import_data(self):
        data = self.read()
        data = self.parse(data)
        return self.save(data)

    def read(self):
        raise NotImplementedError

    def parse(self, data):
        raise NotImplementedError

    def save(self, data):
        raise NotImplementedError
```

Algorithm:

```text
read
 ↓
parse
 ↓
save
```

ổn định.

Các bước:

```text
read
parse
save
```

là extension points.

Đây là Template Method.

---

# 42. Strategy vs Template Method

### Strategy

```text
toàn bộ behavior có thể thay đổi
```

```text
Context
   ↓
Strategy
```

### Template Method

```text
algorithm ổn định
+
một số bước thay đổi
```

```text
Template
 ├── stable step
 ├── extension point
 └── stable step
```

Đây là hai cách thực hiện OCP khác nhau.

---

# 43. OCP không phải "Pattern Collector"

Một codebase không tốt:

```text
Strategy
Factory
AbstractFactory
TemplateMethod
Registry
Adapter
Decorator
Plugin
```

tất cả chỉ để xử lý:

```python id="t0l9z7"
if x == 1:
    ...
else:
    ...
```

Đây là:

> **Pattern overuse**

SOLID không yêu cầu bạn sử dụng Design Pattern.

SOLID yêu cầu:

> **Thiết kế dependency và variation hợp lý.**

---

# 44. Khi nào KHÔNG nên áp dụng OCP?

Đây là phần rất quan trọng.

Không nên abstraction hóa khi:

### 1. Không có variation

```text
chỉ có một behavior
```

### 2. Behavior rất ổn định

```text
không có lý do thay đổi
```

### 3. Abstraction phức tạp hơn vấn đề

```text
10 classes
cho 5 dòng code
```

### 4. YAGNI

> You Aren't Gonna Need It.

Đừng xây plugin architecture cho thứ chưa cần plugin.

---

# 45. OCP và YAGNI

Có một tension:

```text
OCP
↔
YAGNI
```

OCP:

> chuẩn bị extension point.

YAGNI:

> đừng xây thứ chưa cần.

Giải pháp:

> **Abstract những variation có bằng chứng, không abstract mọi khả năng tưởng tượng.**

---

# 46. Heuristic thực tế

Tôi thường dùng quy trình:

```text
1. Identify change
        ↓
2. Determine volatility
        ↓
3. Find clients affected
        ↓
4. Find variation point
        ↓
5. Choose simplest extension mechanism
        ↓
6. Measure complexity
```

Không phải:

```text
if/elif
 ↓
Strategy ngay
```

---

# 47. Bài tập 1

Cho:

```python id="aqa4x1"
def calculate_discount(customer_type, price):

    if customer_type == "normal":
        return price

    elif customer_type == "vip":
        return price * 0.9

    elif customer_type == "premium":
        return price * 0.8
```

Hãy trả lời:

1. Đây có phải OCP violation không?
2. `customer_type` có phải variation point?
3. Có nên dùng Strategy không?
4. Nếu có thêm `employee`, kiến trúc nên thay đổi thế nào?

---

# 48. Bài tập 2 — Parser

Cho:

```python id="f4p5f3"
def parse(file_type, path):

    if file_type == "pdf":
        return parse_pdf(path)

    elif file_type == "epub":
        return parse_epub(path)

    elif file_type == "mobi":
        return parse_mobi(path)
```

Thiết kế:

```text id="9o2m3q"
Parser
   ↑
PdfParser
EpubParser
MobiParser
```

Sau đó thiết kế:

```text
ParserRegistry
```

để thêm:

```text
DocxParser
```

mà không sửa core.

---

# 49. Bài tập 3 — Crawler

Thiết kế:

```text id="c5d6t9"
CrawlerPlugin
```

với:

```python id="h3m8s1"
can_handle(url)
crawl(url)
```

Sau đó:

```text
SiteACrawler
SiteBCrawler
SiteCCrawler
```

và:

```text
CrawlerRouter
```

Yêu cầu:

> Thêm `SiteDCrawler` mà không sửa `CrawlerRouter`.

---

# 50. Bài tập 4 — Phát hiện Over-engineering

Cho:

```python id="m3r6j1"
class NameFormatter(Protocol):

    def format(self, name: str) -> str:
        ...
```

Implementation:

```python id="e8x1w4"
class DefaultNameFormatter:

    def format(self, name):
        return name.strip().title()
```

Chỉ có duy nhất một implementation và không có requirement mở rộng.

Câu hỏi:

> Có nên áp dụng OCP ở đây không?

Hãy giải thích dựa trên:

```text
volatility
variation
complexity
YAGNI
```

---

# 51. Bài tập 5 — Architecture Challenge

Thiết kế kiến trúc:

```text
Novel Reader
```

Hệ thống có:

```text
PDF
EPUB
MOBI
TXT
```

Mỗi format có parser riêng.

Yêu cầu:

```text
Core reader
    ↓
Parser abstraction
    ↑
PDF
EPUB
MOBI
TXT
```

Sau đó:

> Thêm `DOCX` mà **không sửa core reader**.

Hãy xác định:

* Stable core
* Variation point
* Extension point
* Abstraction
* Implementation
* Registry
* Composition Root

---

# 52. Tư duy quan trọng nhất của Buổi 5

Đừng nhớ:

> "`if/elif` = OCP violation."

Hãy nhớ:

> **OCP violation xảy ra khi một thay đổi thuộc một variation point buộc chúng ta phải sửa một module vốn nên ổn định.**

Công thức:

```text
Change
  ↓
Variation
  ↓
Extension Point
  ↓
Abstraction
  ↓
Implementation
```

---

# 53. OCP Deep Dive — Mental Model

Khi nhìn một đoạn code, hãy tự hỏi:

```text
┌─────────────────────────────┐
│ Cái gì thường xuyên thay đổi?│
└──────────────┬──────────────┘
               ↓
       Variation Point
               ↓
       Có nên isolate nó?
               ↓
       Abstraction / Protocol
               ↓
        Extension Mechanism
               ↓
       Strategy / Registry /
       Plugin / Factory...
```

**Đây mới là tư duy OCP.**

---

### Roadmap hiện tại

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive

✅ Buổi 4 — OCP
▶️ Buổi 5 — OCP Deep Dive

⬜ Buổi 6 — OCP thực chiến
⬜ Buổi 7 — LSP
⬜ Buổi 8 — LSP Deep Dive
⬜ Buổi 9 — ISP
⬜ Buổi 10 — ISP Deep Dive
⬜ Buổi 11 — DIP
⬜ Buổi 12 — DIP Deep Dive
```

**Buổi 6** chúng ta sẽ không học thêm lý thuyết OCP mà sẽ làm một bài **refactoring lớn từ code xấu → OCP architecture**, sử dụng `if/elif → Strategy → Registry → Plugin`, sau đó áp dụng trực tiếp vào **crawler architecture**.
