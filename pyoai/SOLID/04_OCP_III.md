# SOLID Deep Dive — Buổi 6

# OCP thực chiến — Refactoring từ `if/elif` → Strategy → Registry → Plugin

Buổi này chúng ta sẽ **không học thêm định nghĩa**. Mục tiêu là nhìn một codebase có vấn đề, xác định **variation point**, rồi refactor từng bước.

---

# 1. Bài toán thực tế

Giả sử chúng ta xây ứng dụng **crawl truyện**.

Có nhiều website:

```text
site-a.com
site-b.com
site-c.com
```

Ban đầu developer viết:

```python
def crawl(url: str):
    if "site-a.com" in url:
        return crawl_site_a(url)

    elif "site-b.com" in url:
        return crawl_site_b(url)

    elif "site-c.com" in url:
        return crawl_site_c(url)

    raise ValueError("Unsupported website")
```

Có vẻ rất đơn giản.

Nhưng sau vài tháng:

```text
Site A
Site B
Site C
Site D
Site E
Site F
...
```

hàm trở thành:

```python
def crawl(url):

    if "site-a.com" in url:
        ...

    elif "site-b.com" in url:
        ...

    elif "site-c.com" in url:
        ...

    elif "site-d.com" in url:
        ...

    elif "site-e.com" in url:
        ...

    elif "site-f.com" in url:
        ...
```

Đây chính là lúc cần suy nghĩ về OCP.

---

# 2. Phân tích trước khi refactor

Đừng vội tạo `ABC`.

Hãy hỏi:

> Cái gì thay đổi?

Câu trả lời:

```text
Crawler implementation
```

Cụ thể:

```text
Site A
Site B
Site C
...
```

Cái gì ổn định?

```text
crawl(url)
```

về mặt application flow.

Ta có:

```text
                 Crawl Application
                        │
                        ↓
                   CrawlerRouter
                        │
              ┌─────────┼─────────┐
              ↓         ↓         ↓
           Site A     Site B    Site C
```

---

# 3. Xác định Variation Point

Variation point:

```text
Which crawler handles this URL?
```

Không phải:

```text
HTTP request
```

Không phải:

```text
database
```

Không phải:

```text
HTML parser
```

Mà là:

```text
Crawler implementation
```

---

# 4. Bước 1 — Extract interface

Ta bắt đầu bằng một abstraction nhỏ.

```python
from typing import Protocol


class Crawler(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str):
        ...
```

Đây là **capability interface**.

Crawler phải có hai khả năng:

```text
can_handle()
crawl()
```

---

# 5. Bước 2 — Tách Site A

Code cũ:

```python
def crawl_site_a(url):
    ...
```

Ta chuyển thành:

```python
class SiteACrawler:

    def can_handle(self, url: str) -> bool:
        return "site-a.com" in url

    def crawl(self, url: str):
        print(f"Crawling Site A: {url}")
```

Site B:

```python
class SiteBCrawler:

    def can_handle(self, url: str) -> bool:
        return "site-b.com" in url

    def crawl(self, url: str):
        print(f"Crawling Site B: {url}")
```

---

# 6. Bước 3 — Router

Bây giờ cần một object chịu trách nhiệm:

> URL này thuộc crawler nào?

```python
class CrawlerRouter:

    def __init__(self, crawlers):
        self._crawlers = list(crawlers)

    def resolve(self, url: str) -> Crawler:
        for crawler in self._crawlers:
            if crawler.can_handle(url):
                return crawler

        raise ValueError(
            f"No crawler found for: {url}"
        )
```

Sử dụng:

```python
router = CrawlerRouter([
    SiteACrawler(),
    SiteBCrawler(),
])
```

Sau đó:

```python
crawler = router.resolve(url)

crawler.crawl(url)
```

---

# 7. So sánh hai kiến trúc

### Trước

```text
crawl()
 │
 ├── Site A
 ├── Site B
 ├── Site C
 └── Site D
```

Thêm Site D:

```text
modify crawl()
```

---

### Sau

```text
CrawlerRouter
      │
      ├── SiteACrawler
      ├── SiteBCrawler
      └── SiteCCrawler
```

Thêm Site D:

```python
SiteDCrawler()
```

và đăng ký nó.

`CrawlerRouter` không thay đổi.

Đây chính là OCP.

---

# 8. Nhưng vẫn còn một vấn đề

Ta đang viết:

```python
router = CrawlerRouter([
    SiteACrawler(),
    SiteBCrawler(),
    SiteCCrawler(),
])
```

Mỗi khi thêm plugin:

```python
SiteDCrawler()
```

ta vẫn phải sửa composition code.

Điều này **không nhất thiết là vi phạm OCP**.

Vì:

```text
Composition Root
```

là nơi chịu trách nhiệm lắp ráp application.

---

# 9. Composition Root

Ví dụ:

```python
def create_application():

    crawlers = [
        SiteACrawler(),
        SiteBCrawler(),
        SiteCCrawler(),
    ]

    router = CrawlerRouter(crawlers)

    return router
```

Đây là nơi:

```text
object graph
```

được xây dựng.

Đừng cố làm cho **mọi file** đều không bao giờ thay đổi.

OCP không yêu cầu điều đó.

---

# 10. Bước 4 — Registry

Nếu muốn dynamic registration:

```python
class CrawlerRegistry:

    def __init__(self):
        self._crawlers = []

    def register(self, crawler: Crawler):
        self._crawlers.append(crawler)

    def all(self):
        return list(self._crawlers)
```

Đăng ký:

```python
registry = CrawlerRegistry()

registry.register(SiteACrawler())
registry.register(SiteBCrawler())
```

Router:

```python
router = CrawlerRouter(
    registry.all()
)
```

---

# 11. Registry không chỉ là Dictionary

Registry có thể dùng:

```python
dict
```

hoặc:

```python
list
```

hoặc:

```python
set
```

Tùy cách lookup.

Ví dụ nếu crawler có key:

```python
class CrawlerRegistry:

    def __init__(self):
        self._items = {}

    def register(self, name, crawler):
        self._items[name] = crawler

    def get(self, name):
        return self._items[name]
```

---

# 12. Khi nào dùng List?

Nếu routing dựa trên:

```python
can_handle(url)
```

thì:

```python
list[Crawler]
```

rất tự nhiên:

```python
for crawler in crawlers:
    if crawler.can_handle(url):
        return crawler
```

---

# 13. Khi nào dùng Dictionary?

Nếu URL đã xác định được key:

```text
site-a
site-b
site-c
```

thì:

```python
{
    "site-a": SiteACrawler(),
    "site-b": SiteBCrawler(),
}
```

hiệu quả hơn.

Ví dụ:

```python
crawler = registry.get("site-a")
```

---

# 14. Một lỗi thiết kế phổ biến

Đừng biến Registry thành:

```python
class CrawlerRegistry:

    def get(self, url):

        if "site-a" in url:
            return SiteACrawler()

        elif "site-b" in url:
            return SiteBCrawler()
```

Bạn chỉ chuyển:

```text
if/elif
```

từ:

```text
CrawlerRouter
```

sang:

```text
CrawlerRegistry
```

OCP **chưa được giải quyết**.

---

# 15. Registry đúng nghĩa

Registry phải biết:

```text
registered implementations
```

chứ không biết:

```text
business logic của từng implementation
```

Ví dụ:

```python
registry.register(
    SiteACrawler()
)
```

Registry không cần biết:

```text
Site A parse HTML thế nào
Site B login ra sao
Site C pagination thế nào
```

---

# 16. Bước 5 — Plugin

Bây giờ chúng ta muốn:

```text
Core
+
Crawler plugins
```

Core:

```text
crawler_core/
    router.py
    registry.py
    protocol.py
```

Plugin:

```text
crawler_site_a/
    crawler.py
```

Plugin B:

```text
crawler_site_b/
    crawler.py
```

Kiến trúc:

```text
                 Core
                  │
          Crawler Protocol
             ↑    ↑    ↑
             │    │    │
          Plugin Plugin Plugin
            A      B      C
```

---

# 17. Plugin không nhất thiết phải là package riêng

Có thể đơn giản:

```text
plugins/
    site_a.py
    site_b.py
    site_c.py
```

Load:

```python
from plugins.site_a import SiteACrawler
```

Nhưng đây vẫn là **explicit plugin registration**.

---

# 18. Plugin discovery

Mức cao hơn:

```text
Application
    ↓
discover plugins
    ↓
load plugins
    ↓
register
    ↓
run
```

Ví dụ conceptual API:

```python
plugins = discover_plugins()

for plugin in plugins:
    registry.register(plugin)
```

Lúc này core không biết cụ thể:

```text
Site A
Site B
Site C
```

---

# 19. OCP đạt đến mức nào?

Ta có:

```text
                    Core
                     │
             ┌───────┴───────┐
             ↓               ↓
          Registry          Router
             ↑
       Plugin Discovery
             ↑
      ┌──────┼──────┐
      ↓      ↓      ↓
    Site A Site B Site C
```

Thêm:

```text
Site D
```

chỉ cần:

```text
Plugin D
```

Core không đổi.

Đây là **OCP ở cấp architecture**.

---

# 20. Nhưng đừng đi quá xa

Nếu ứng dụng chỉ có:

```text
2 crawler
```

thì plugin system hoàn chỉnh có thể là quá mức.

Ví dụ:

```text
entry points
dynamic discovery
metadata
plugin lifecycle
dependency management
version compatibility
```

cho hai crawler là over-engineering.

---

# 21. OCP Trade-off

Ta có:

```text
Simple
   │
   │
   ├── if/elif
   │
   ├── Strategy
   │
   ├── Registry
   │
   └── Plugin Architecture
   │
Complex
```

Không phải:

```text
Plugin Architecture = tốt nhất
```

Mà:

> **Chọn mức abstraction phù hợp với mức volatility.**

---

# 22. Refactoring thực tế

Bắt đầu:

```python
def crawl(url):

    if "site-a.com" in url:
        ...

    elif "site-b.com" in url:
        ...

    elif "site-c.com" in url:
        ...
```

### Bước 1

Extract:

```python
Crawler
```

### Bước 2

Tách:

```python
SiteACrawler
SiteBCrawler
SiteCCrawler
```

### Bước 3

Tạo:

```python
CrawlerRouter
```

### Bước 4

Tạo:

```python
CrawlerRegistry
```

### Bước 5

Nếu cần:

```text
Plugin Architecture
```

---

# 23. Một nguyên tắc refactoring quan trọng

**Không refactor tất cả một lần.**

Thay vì:

```text
1000 dòng
   ↓
500 dòng abstraction
```

hãy đi:

```text
if/elif
   ↓
extract function
   ↓
extract class
   ↓
introduce Protocol
   ↓
Strategy
   ↓
Registry
   ↓
Plugin
```

Mỗi bước phải giữ behavior cũ.

---

# 24. Testing sau refactoring

Trước tiên viết test:

```python
def test_site_a_crawler():
    crawler = SiteACrawler()

    assert crawler.can_handle(
        "https://site-a.com/story"
    )
```

Router:

```python
def test_router_selects_site_a():

    router = CrawlerRouter([
        SiteACrawler(),
        SiteBCrawler(),
    ])

    crawler = router.resolve(
        "https://site-a.com/story"
    )

    assert isinstance(
        crawler,
        SiteACrawler
    )
```

---

# 25. Test OCP

Một test rất hay:

```text
Nếu thêm SiteC:
```

ta chỉ cần:

```python
class SiteCCrawler:
    ...
```

và:

```python
router = CrawlerRouter([
    SiteACrawler(),
    SiteBCrawler(),
    SiteCCrawler(),
])
```

Router test cũ vẫn chạy.

Đây là một dấu hiệu kiến trúc tốt.

---

# 26. Một insight sâu hơn

OCP không chỉ giảm:

```text
code modification
```

Nó giảm:

```text
blast radius
```

Ví dụ:

```text
Site A bug
```

Code xấu:

```text
CrawlerService
 ├── Site A
 ├── Site B
 ├── Site C
 ├── DB
 ├── Parser
 └── Notification
```

Thay đổi Site A có thể ảnh hưởng cả service.

Code tốt:

```text
SiteACrawler
```

thay đổi chủ yếu nằm trong:

```text
SiteACrawler
```

Blast radius nhỏ hơn.

---

# 27. OCP và Deployment

Plugin architecture còn có lợi ích:

```text
Core release
```

không nhất thiết phải thay đổi khi:

```text
Plugin release
```

Ví dụ:

```text
crawler-core 1.5
crawler-site-a 2.1
crawler-site-b 1.8
```

Đây là lý do OCP rất quan trọng trong hệ thống extensible.

---

# 28. OCP và Team Development

Một hệ thống có:

```text
Core team
Crawler team A
Crawler team B
Crawler team C
```

có thể cho phép mỗi team làm:

```text
Plugin
```

mà không đụng:

```text
Core
```

OCP lúc này trở thành **boundary giữa team**.

---

# 29. OCP không chỉ là code design

Đây là insight cần nhớ:

```text
OCP
 ↓
Class design
 ↓
Module design
 ↓
Package design
 ↓
Architecture
 ↓
Deployment boundary
```

OCP có thể áp dụng ở nhiều tầng.

---

# 30. Checklist OCP thực chiến

Khi review code, hãy hỏi:

### Change

```text
Cái gì thường xuyên thay đổi?
```

### Volatility

```text
Thay đổi đó có độc lập không?
```

### Boundary

```text
Có thể cô lập nó không?
```

### Extension Point

```text
Có thể thêm implementation mà không sửa core không?
```

### Abstraction

```text
Abstraction có thực sự cần không?
```

### Complexity

```text
Abstraction này có đáng giá không?
```

### Testing

```text
Thêm implementation mới có phá core test không?
```

---

# 31. Bài tập cuối buổi — Refactoring lớn

Hãy bắt đầu với code:

```python
class NotificationService:

    def send(self, channel, message):

        if channel == "email":
            print(f"Sending email: {message}")

        elif channel == "telegram":
            print(f"Sending telegram: {message}")

        elif channel == "discord":
            print(f"Sending discord: {message}")

        elif channel == "sms":
            print(f"Sending SMS: {message}")
```

Yêu cầu refactor thành:

```text
NotificationService
        │
        ↓
NotificationChannel
        ↑
 ┌──────┼───────┬──────┐
 ↓      ↓       ↓      ↓
Email Telegram Discord SMS
```

Sau đó thêm:

```text
WhatsApp
```

với yêu cầu:

> **Không sửa `NotificationService`.**

---

# 32. Bài tập nâng cao

Sau khi làm xong Strategy, tiếp tục:

```text
NotificationRegistry
```

API mong muốn:

```python
registry.register(
    "email",
    EmailNotification()
)
```

và:

```python
channel = registry.get("email")
channel.send(message)
```

Cuối cùng thiết kế:

```text
Notification Plugin System
```

với:

```text
notification_core
notification_email
notification_telegram
notification_discord
```

---

# 33. Điều cần nhớ sau Buổi 6

Nếu chỉ nhớ **5 điều**, hãy nhớ:

### 1.

> OCP không cấm sửa code.

### 2.

> Hãy tìm **variation point**, không phải tìm `if`.

### 3.

> Strategy là một công cụ thực hiện OCP, không phải bản thân OCP.

### 4.

> Registry giúp quản lý extension; Plugin giúp mở rộng hệ thống ở mức architecture.

### 5.

> **Đừng abstraction trước khi có evidence về volatility.**

Mental model cuối cùng:

```text
              CHANGE
                 ↓
           VOLATILITY
                 ↓
        VARIATION POINT
                 ↓
         EXTENSION POINT
                 ↓
            ABSTRACTION
                 ↓
      ┌──────────┼──────────┐
      ↓          ↓          ↓
   Strategy    Registry    Plugin
```

---

## Roadmap

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive

✅ Buổi 4 — OCP
✅ Buổi 5 — OCP Deep Dive
✅ Buổi 6 — OCP thực chiến

⬜ Buổi 7 — LSP
⬜ Buổi 8 — LSP Deep Dive
⬜ Buổi 9 — ISP
⬜ Buổi 10 — ISP Deep Dive
⬜ Buổi 11 — DIP
⬜ Buổi 12 — DIP Deep Dive
```

**Buổi 7 sẽ chuyển sang LSP**, nhưng chúng ta sẽ học LSP theo hướng rất khác OCP: thay vì tập trung vào **“có mở rộng được không?”**, ta sẽ tập trung vào **“subtype có thực sự thay thế được base type mà không phá vỡ behavior của chương trình hay không?”**.
