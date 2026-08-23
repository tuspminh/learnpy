# Buổi 18 — Crawler Architecture

Hôm nay chúng ta áp dụng **OCP + LSP + ISP + DIP** vào một bài toán rất gần với project của bạn:

> **Một hệ thống crawl truyện hỗ trợ nhiều website/source khác nhau.**

Mục tiêu cuối buổi:

```text
CLI
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Crawler Plugin
 ├── Source A
 ├── Source B
 └── Source C
```

Điểm quan trọng:

> **Use Case không được biết Source A, Source B là class nào.**

---

# 1. Bài toán

Giả sử chúng ta có hai website:

```text
source_a.com
source_b.com
```

Mỗi source có HTML khác nhau.

Ví dụ Source A:

```html
<h1 class="story-title">Harry Potter</h1>

<div class="chapter-content">
    ...
</div>
```

Source B:

```html
<h1 id="novel-name">Harry Potter</h1>

<div id="content">
    ...
</div>
```

Nếu viết một crawler khổng lồ:

```python
class Crawler:

    def crawl(self, url):

        if "source-a.com" in url:
            ...

        elif "source-b.com" in url:
            ...

        elif "source-c.com" in url:
            ...
```

ban đầu rất tiện.

Nhưng càng nhiều source:

```text
if source A
elif source B
elif source C
elif source D
elif source E
...
```

thì class càng trở thành **God Object**.

---

# 2. Mục tiêu architecture

Chúng ta muốn:

```text
                 CrawlStory
                     │
                     ↓
               Crawler Protocol
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
      SourceA     SourceB    SourceC
```

Use Case chỉ biết:

```python
crawler.crawl(url)
```

Không biết:

```python
SourceACrawler
SourceBCrawler
```

---

# 3. Đầu tiên: Domain Model

Ta bắt đầu từ domain.

```python
# domain/story.py

from dataclasses import dataclass


@dataclass
class Story:
    title: str
    source: str
    url: str
```

Chapter:

```python
# domain/chapter.py

from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    url: str
    content: str
```

---

# 4. Có nên để crawler trả HTML không?

Ví dụ:

```python
class Crawler:

    def crawl(self, url: str) -> str:
        ...
```

Không tốt nếu Use Case phải hiểu HTML.

Ta muốn crawler chịu trách nhiệm:

```text
website HTML
      ↓
Crawler
      ↓
Domain object
```

Ví dụ:

```python
Story
Chapter
```

---

# 5. Crawler Interface

Tạo:

```python
# domain/crawler.py

from typing import Protocol

from .story import Story


class Crawler(Protocol):

    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...

    def crawl_story(
        self,
        url: str,
    ) -> Story:
        ...
```

Đây là abstraction.

---

# 6. Tại sao có `can_handle()`?

Vì hệ thống có nhiều plugin:

```text
SourceA
SourceB
SourceC
```

Ta cần biết:

```text
URL này thuộc plugin nào?
```

Ví dụ:

```python
crawler.can_handle(
    "https://source-a.com/story/123"
)
```

→ `True`

Còn:

```python
crawler.can_handle(
    "https://source-b.com/story/123"
)
```

→ `False`

---

# 7. Source A

```python
# infrastructure/crawlers/source_a.py

from domain.crawler import Crawler
from domain.story import Story


class SourceACrawler:

    def can_handle(
        self,
        url: str,
    ) -> bool:

        return "source-a.com" in url

    def crawl_story(
        self,
        url: str,
    ) -> Story:

        # request HTML
        # parse HTML

        title = "Harry Potter"

        return Story(
            title=title,
            source="source_a",
            url=url,
        )
```

Lưu ý:

Class không cần:

```python
class SourceACrawler(Crawler):
```

vì chúng ta dùng `Protocol`.

---

# 8. Source B

```python
# infrastructure/crawlers/source_b.py

from domain.story import Story


class SourceBCrawler:

    def can_handle(
        self,
        url: str,
    ) -> bool:

        return "source-b.com" in url

    def crawl_story(
        self,
        url: str,
    ) -> Story:

        # request HTML
        # parse HTML

        title = "Harry Potter"

        return Story(
            title=title,
            source="source_b",
            url=url,
        )
```

Hai class hoàn toàn độc lập.

---

# 9. Đây chính là OCP

Use Case không sửa khi thêm source.

Ban đầu:

```text
SourceA
SourceB
```

Sau đó thêm:

```text
SourceC
```

Ta chỉ tạo:

```python
class SourceCCrawler:
    ...
```

Không sửa:

```text
CrawlStory
```

Không sửa:

```text
Story
```

Không sửa:

```text
CLI
```

Đây là:

> **Open for extension, closed for modification.**

---

# 10. Crawler Registry

Bây giờ cần một object tìm crawler phù hợp.

```python
class CrawlerRegistry:

    def __init__(
        self,
        crawlers: list[Crawler],
    ):
        self.crawlers = crawlers
```

Method:

```python
def find(
    self,
    url: str,
) -> Crawler:

    for crawler in self.crawlers:

        if crawler.can_handle(url):
            return crawler

    raise ValueError(
        f"No crawler found for: {url}"
    )
```

---

# 11. Registry không biết Source cụ thể

Registry chỉ biết:

```text
Crawler
```

Không:

```python
if SourceA:
    ...

elif SourceB:
    ...
```

Đây là một khác biệt cực kỳ quan trọng.

---

# 12. Use Case

Bây giờ:

```python
# application/crawl_story.py

from domain.crawler import Crawler
from domain.story import Story


class CrawlStory:

    def __init__(
        self,
        registry,
    ):
        self.registry = registry

    def execute(
        self,
        url: str,
    ) -> Story:

        crawler = self.registry.find(url)

        return crawler.crawl_story(url)
```

Use Case chỉ biết:

```text
Registry
Crawler
Story
```

Không biết:

```text
SourceA
SourceB
BeautifulSoup
requests
httpx
```

---

# 13. Dependency Direction

Nhìn dependency:

```text
             CrawlStory
                  │
                  ↓
             Crawler
                  ↑
        ┌─────────┴─────────┐
        │                   │
 SourceACrawler      SourceBCrawler
```

Đây là DIP.

High-level:

```text
CrawlStory
```

không phụ thuộc:

```text
SourceACrawler
```

mà phụ thuộc:

```text
Crawler
```

---

# 14. Một lỗi thiết kế thường gặp

Nhiều người sẽ viết:

```python
class CrawlStory:

    def __init__(self):
        self.crawler = SourceACrawler()
```

Đây là:

```text
Application
    ↓
Source A
```

Sai dependency direction.

Nếu muốn thêm Source B:

```python
if source == "b":
    self.crawler = SourceBCrawler()
```

Application lại phải sửa.

OCP bị phá.

---

# 15. Đưa Dependency Injection vào

Đúng:

```python
class CrawlStory:

    def __init__(
        self,
        registry,
    ):
        self.registry = registry
```

Composition Root:

```python
registry = CrawlerRegistry(
    [
        SourceACrawler(),
        SourceBCrawler(),
    ]
)

crawl_story = CrawlStory(
    registry
)
```

Đây là **Dependency Injection**.

---

# 16. Composition Root

Đây là nơi rất quan trọng.

```python
# composition.py

def build_application():

    crawlers = [
        SourceACrawler(),
        SourceBCrawler(),
    ]

    registry = CrawlerRegistry(
        crawlers
    )

    return CrawlStory(
        registry
    )
```

Application không biết crawler nào tồn tại.

Composition Root biết.

---

# 17. CLI

CLI:

```python
@app.command()
def crawl(url: str):

    use_case = build_application()

    story = use_case.execute(url)

    typer.echo(
        f"Crawled: {story.title}"
    )
```

CLI không biết:

```text
Source A
Source B
BeautifulSoup
requests
```

---

# 18. Luồng hoàn chỉnh

Khi chạy:

```bash
novel crawl https://source-a.com/story/123
```

luồng:

```text
CLI
 │
 ↓
CrawlStory
 │
 ↓
CrawlerRegistry
 │
 ├── SourceACrawler.can_handle()
 │       ↓
 │      True
 │
 ↓
SourceACrawler.crawl_story()
 │
 ↓
Story
 │
 ↓
CLI
```

---

# 19. Điều gì xảy ra với Source B?

```bash
novel crawl https://source-b.com/story/999
```

Registry:

```text
SourceA
  ↓
False

SourceB
  ↓
True
```

Sau đó:

```text
SourceBCrawler
      ↓
crawl_story()
```

Use Case không thay đổi.

---

# 20. Đây là Strategy Pattern

Có thể nhìn:

```text
Crawler
  ↑
  │
  ├── SourceA
  ├── SourceB
  └── SourceC
```

như một Strategy.

Algorithm:

```text
crawl story
```

được thực hiện bởi strategy khác nhau.

---

# 21. Nhưng Registry cũng là một Pattern

Registry:

```python
CrawlerRegistry(
    [
        SourceACrawler(),
        SourceBCrawler(),
    ]
)
```

lưu các implementation.

Có thể mở rộng:

```python
registry.register(
    SourceCCrawler()
)
```

---

# 22. Dynamic Registration

```python
class CrawlerRegistry:

    def __init__(self):

        self._crawlers = []

    def register(
        self,
        crawler: Crawler,
    ) -> None:

        self._crawlers.append(
            crawler
        )

    def find(
        self,
        url: str,
    ) -> Crawler:

        for crawler in self._crawlers:

            if crawler.can_handle(url):
                return crawler

        raise LookupError(
            f"No crawler for {url}"
        )
```

Composition:

```python
registry = CrawlerRegistry()

registry.register(
    SourceACrawler()
)

registry.register(
    SourceBCrawler()
)
```

---

# 23. Đây là nền tảng Plugin Architecture

Sau này plugin có thể nằm ở:

```text
plugins/
├── source_a/
├── source_b/
├── source_c/
```

Hoặc package riêng:

```text
novel-crawler-source-a
novel-crawler-source-b
```

Core application không cần sửa.

---

# 24. Nhưng `can_handle()` có một vấn đề

Ví dụ:

```python
return "source-a.com" in url
```

Đây chỉ là demo.

Production nên parse URL:

```python
from urllib.parse import urlparse


def can_handle(self, url: str) -> bool:

    host = urlparse(url).netloc

    return host == "source-a.com"
```

Tránh:

```text
evil-source-a.com
```

match nhầm.

---

# 25. ISP Deep Dive

Bây giờ hãy tưởng tượng chúng ta thiết kế:

```python
class Crawler(Protocol):

    def can_handle(self, url):
        ...

    def crawl_story(self, url):
        ...

    def crawl_chapter(self, url):
        ...

    def login(self):
        ...

    def upload(self):
        ...

    def notify(self):
        ...
```

Đây là **Fat Interface**.

Source A có thể chỉ cần:

```text
crawl_story
crawl_chapter
```

nhưng bị ép phải implement:

```text
login
upload
notify
```

---

# 26. Tách interface

Có thể thiết kế:

```python
class StoryCrawler(Protocol):

    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...

    def crawl_story(
        self,
        url: str,
    ) -> Story:
        ...
```

Chapter:

```python
class ChapterCrawler(Protocol):

    def crawl_chapter(
        self,
        url: str,
    ) -> Chapter:
        ...
```

Authentication:

```python
class Authenticator(Protocol):

    def login(
        self,
        username: str,
        password: str,
    ) -> None:
        ...
```

Notification:

```python
class Notifier(Protocol):

    def notify(
        self,
        message: str,
    ) -> None:
        ...
```

---

# 27. Tại sao ISP quan trọng ở crawler?

Một website có thể:

```text
crawl story
crawl chapter
```

nhưng không cần:

```text
login
upload
notify
```

Website khác:

```text
crawl
login
```

Website khác nữa:

```text
crawl
Cloudflare handling
```

Không nên ép tất cả crawler có cùng một interface khổng lồ.

---

# 28. LSP trong crawler

Giả sử:

```python
class SourceACrawler:
    ...
```

và:

```python
class SourceBCrawler:
    ...
```

Cả hai đều phải thỏa:

```text
Crawler contract
```

Nếu:

```python
SourceBCrawler.crawl_story()
```

luôn:

```python
raise NotImplementedError
```

thì Source B **không phải subtype hợp lệ** của `Crawler`.

Đây là LSP.

---

# 29. `NotImplementedError` là dấu hiệu cảnh báo

Sai:

```python
class SourceBCrawler:

    def crawl_story(self, url):

        raise NotImplementedError
```

Nếu registry coi nó là:

```text
Crawler
```

thì contract bị phá.

Tốt hơn:

> Nếu capability không tồn tại, đừng đưa class đó vào interface yêu cầu capability ấy.

Đây chính là kết hợp:

```text
LSP + ISP
```

---

# 30. Error contract

Crawler cũng cần contract rõ ràng.

Ví dụ:

```python
class Crawler(Protocol):

    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...

    def crawl_story(
        self,
        url: str,
    ) -> Story:
        ...
```

Contract ngầm:

```text
can_handle()
    → True nếu crawler hỗ trợ URL

crawl_story()
    → trả Story hợp lệ
```

Không nên:

```python
return None
```

nếu contract nói:

```python
-> Story
```

---

# 31. Tạo Exception riêng

```python
class CrawlerError(Exception):
    pass
```

Source-specific:

```python
class SourceUnavailableError(
    CrawlerError
):
    pass
```

Parsing:

```python
class ParseError(
    CrawlerError
):
    pass
```

Application không cần biết chi tiết HTML.

---

# 32. Một architecture thực tế hơn

```text
src/novel/
│
├── domain/
│   ├── story.py
│   ├── chapter.py
│   └── crawler.py
│
├── application/
│   └── crawl_story.py
│
├── infrastructure/
│   └── crawlers/
│       ├── source_a.py
│       └── source_b.py
│
├── presentation/
│   └── cli.py
│
└── composition.py
```

---

# 33. Nhưng chúng ta chưa crawl thật

Trong project thực tế, Source A sẽ có:

```text
HTTP Client
HTML Parser
Crawler
```

Ví dụ:

```text
SourceACrawler
    │
    ├── HttpClient
    │
    └── SourceAParser
```

Không nên nhét tất cả vào một class.

---

# 34. Tách HTTP

```python
class HttpClient(Protocol):

    def get(
        self,
        url: str,
    ) -> str:
        ...
```

Implementation:

```python
import requests


class RequestsHttpClient:

    def get(
        self,
        url: str,
    ) -> str:

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.text
```

---

# 35. Tách Parser

```python
class SourceAParser:

    def parse_story(
        self,
        html: str,
        url: str,
    ) -> Story:

        ...
```

Crawler:

```python
class SourceACrawler:

    def __init__(
        self,
        http_client,
        parser,
    ):
        self.http_client = http_client
        self.parser = parser
```

---

# 36. Crawler trở thành Orchestrator

```python
def crawl_story(
    self,
    url: str,
) -> Story:

    html = self.http_client.get(url)

    return self.parser.parse_story(
        html,
        url,
    )
```

Rất đẹp:

```text
Crawler
 ↓
HTTP
 ↓
Parser
 ↓
Domain
```

Crawler không tự làm tất cả.

---

# 37. Đây lại là SRP

`SourceACrawler`:

> Điều phối quá trình crawl Source A.

`HttpClient`:

> HTTP communication.

`SourceAParser`:

> Parse HTML của Source A.

Mỗi component có một responsibility tương đối rõ.

---

# 38. Testing trở nên cực kỳ dễ

Test parser:

```python
def test_parse_story():

    parser = SourceAParser()

    story = parser.parse_story(
        html,
        url,
    )

    assert story.title == "Harry Potter"
```

Không cần internet.

---

# 39. Test crawler

Fake HTTP:

```python
class FakeHttpClient:

    def __init__(self, html):
        self.html = html

    def get(self, url):
        return self.html
```

Sau đó:

```python
crawler = SourceACrawler(
    http_client=FakeHttpClient(html),
    parser=SourceAParser(),
)
```

Không cần network.

Đây chính là DIP + testability.

---

# 40. Test Use Case

Thậm chí không cần HTTP:

```python
class FakeCrawler:

    def can_handle(self, url):
        return True

    def crawl_story(self, url):

        return Story(
            title="Test",
            source="fake",
            url=url,
        )
```

Registry:

```python
registry = CrawlerRegistry(
    [FakeCrawler()]
)
```

Use Case:

```python
use_case = CrawlStory(
    registry
)
```

Test:

```python
story = use_case.execute(
    "https://example.com"
)

assert story.title == "Test"
```

---

# 41. Đây là lý do SOLID liên kết với Testing

Không phải:

```text
SOLID = architecture đẹp
```

mà:

```text
SOLID
 ↓
Low coupling
 ↓
Dependency injection
 ↓
Replaceable components
 ↓
Easy testing
```

Đây mới là giá trị thực tế.

---

# 42. Một thiết kế hoàn chỉnh

```text
                         CLI
                          │
                          ↓
                    CrawlStory
                      Use Case
                          │
                          ↓
                  CrawlerRegistry
                          │
                    Crawler Protocol
                          │
             ┌────────────┴────────────┐
             ↓                         ↓
       SourceACrawler            SourceBCrawler
             │                         │
        ┌────┴────┐               ┌────┴────┐
        ↓         ↓               ↓         ↓
   HttpClient   Parser       HttpClient   Parser
        │         │               │         │
        └────┬────┘               └────┬────┘
             ↓                         ↓
           HTTP                      HTTP
```

Repository song song:

```text
                    CrawlStory
                        │
                        ↓
                     Story
                        │
                        ↓
                 StoryRepository
                        ↑
                        │
                SQLiteRepository
```

---

# 43. Đây là architecture mà chúng ta hướng tới

```text
                       Presentation
                            │
                            ↓
                       Application
                            │
                 ┌──────────┴──────────┐
                 ↓                     ↓
             Crawler Port         Repository Port
                 ↑                     ↑
                 │                     │
          ┌──────┴──────┐              │
          │             │              │
       Source A      Source B        SQLite
```

Domain nằm ở trung tâm:

```text
                     Domain
                       ↑
                       │
          ┌────────────┴────────────┐
          │                         │
       Crawler                  Repository
        Port                       Port
```

---

# 44. SOLID mapping

| Principle | Trong crawler                                    |
| --------- | ------------------------------------------------ |
| **SRP**   | Parser, HTTP, Crawler tách responsibility        |
| **OCP**   | Thêm Source C mà không sửa Use Case              |
| **LSP**   | Mọi Crawler phải tuân contract                   |
| **ISP**   | Tách StoryCrawler, ChapterCrawler, Authenticator |
| **DIP**   | Use Case phụ thuộc Crawler abstraction           |

Đây chính là một ví dụ rất thực tế của việc **SOLID không hoạt động độc lập**.

---

# 45. Bài tập Buổi 18

### Bài 1 — Cơ bản

Tạo:

```text
Crawler Protocol
SourceACrawler
SourceBCrawler
CrawlerRegistry
CrawlStory
```

---

### Bài 2 — OCP

Thêm:

```text
SourceCCrawler
```

mà **không sửa `CrawlStory`**.

---

### Bài 3 — ISP

Tách:

```text
StoryCrawler
ChapterCrawler
Authenticator
Notifier
```

và giải thích vì sao không nên có:

```text
UniversalCrawler
```

---

### Bài 4 — DIP

Tạo:

```text
HttpClient Protocol
RequestsHttpClient
FakeHttpClient
```

Sau đó test `SourceACrawler` mà **không gọi internet**.

---

### Bài 5 — LSP

Tạo một crawler sai:

```python
class BrokenCrawler:

    def can_handle(self, url):
        return True

    def crawl_story(self, url):
        raise NotImplementedError
```

Phân tích:

> Tại sao class này vi phạm LSP mặc dù có đầy đủ method?

---

# 46. Bài tập quan trọng nhất

Hãy thử trả lời câu hỏi này:

> Nếu ngày mai thêm **Source D**, những file nào được phép sửa?

Architecture tốt:

```text
infrastructure/crawlers/source_d.py
composition.py
```

Có thể thêm test:

```text
tests/
```

Nhưng **không được cần sửa**:

```text
CrawlStory
CrawlerRegistry
Story
CLI
```

Nếu bạn phải sửa:

```python
if "source-d.com":
```

trong `CrawlStory`, thì OCP đang bị phá.

---

# 47. Kết luận Buổi 18

Ta đã chuyển từ:

```text
CrawlerManager
     │
     ├── if Source A
     ├── if Source B
     ├── if Source C
     ├── HTTP
     ├── Parsing
     ├── Database
     └── Notification
```

sang:

```text
                    CrawlStory
                         │
                         ↓
                 Crawler Protocol
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
          Source A    Source B   Source C
              │          │          │
            Parser     Parser     Parser
              │          │          │
            HTTP       HTTP       HTTP
```

**Đây là bước rất quan trọng trước Buổi 19.**

Buổi 19 chúng ta sẽ lấy chính một `CrawlerManager` kiểu **God Object** và **refactor từng bước**, không refactor một phát. Ta sẽ đi theo chuỗi:

```text
CrawlerManager
      ↓
nhận diện Code Smell
      ↓
SRP
      ↓
Extract Class
      ↓
Extract Interface
      ↓
OCP
      ↓
Strategy / Registry
      ↓
DIP
      ↓
Dependency Injection
      ↓
DDD
      ↓
Clean Architecture
```

Đây sẽ là buổi quan trọng nhất của toàn bộ phần SOLID vì chúng ta sẽ thấy **từ một đống code thực tế, từng nguyên lý SOLID được dùng để giải quyết một vấn đề cụ thể như thế nào**.
