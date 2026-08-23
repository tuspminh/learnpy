### Buổi 22 — Crawler Port + Plugin Architecture

> Mục tiêu: Thiết kế hệ thống crawler có thể thêm website mới mà không sửa Use Case, đúng tinh thần OCP + DIP.

Đây là buổi quan trọng nhất của project Story Crawler, vì toàn bộ khả năng mở rộng sẽ nằm ở Crawler Port và Plugin.

### 1. Vấn đề thực tế

Giả sử hôm nay bạn hỗ trợ 2 website:

```
source-a.com
source-b.com
```

Sau 3 tháng:

```
source-c.com
source-d.com
source-e.com
```

Nếu kiến trúc ban đầu là:

Python

Chạy

```
if "source-a" in url:
    ...
elif "source-b" in url:
    ...
```

thì mỗi lần thêm source bạn đều phải sửa code cũ.

Đó là vi phạm OCP.

### 2. Kiến trúc mục tiêu

```
                CrawlStory (Use Case)
                        │
                        ▼
                 StoryCrawler Port
                        ▲
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   Source A        Source B        Source C
```

Use Case chỉ biết `StoryCrawler`, không biết từng website.

### 3. Port là gì?

Trong Clean Architecture:

> Port = Interface mô tả capability mà Application cần.

Ở đây Application cần đúng một khả năng:

> "Cho tôi một URL truyện, trả về Story."

Python

Chạy

```
from typing import Protocol
from story_crawler.domain.story import Story
from story_crawler.domain.value_objects import Url


class StoryCrawler(Protocol):

    def can_handle(self, url: Url) -> bool:
        ...

    def crawl(self, url: Url) -> Story:
        ...
```

Đây là Input Port của Infrastructure.

### 4. Vì sao có `can_handle()`?

Application không biết URL thuộc website nào.

Ví dụ:

```
https://source-a.com/story/1
```

Ta hỏi từng plugin:

```
Source A → True
Source B → False
Source C → False
```

Plugin phù hợp sẽ được chọn.

### 5. Thiết kế Plugin

Mỗi website là một plugin độc lập.

```
plugins/
├── source_a/
│   ├── crawler.py
│   ├── parser.py
│   └── metadata.py
│
├── source_b/
│   ├── crawler.py
│   ├── parser.py
│   └── metadata.py
│
└── source_c/
```

Điểm quan trọng:

> Không plugin nào import plugin khác.

### 6. Source A Plugin

Python

Chạy

```
from urllib.parse import urlparse

from story_crawler.domain.story import Story
from story_crawler.domain.value_objects import Url, Source


class SourceACrawler:

    def can_handle(self, url: Url) -> bool:

        return (
            urlparse(url.value).netloc
            == "source-a.com"
        )

    def crawl(self, url: Url) -> Story:

        return Story(
            title="Demo Story A",
            source=Source("source_a"),
            url=url,
        )
```

### 7. Source B Plugin

Python

Chạy

```
class SourceBCrawler:

    def can_handle(self, url: Url) -> bool:

        return (
            urlparse(url.value).netloc
            == "source-b.com"
        )

    def crawl(self, url: Url) -> Story:

        return Story(
            title="Demo Story B",
            source=Source("source_b"),
            url=url,
        )
```

Hai plugin hoàn toàn độc lập.

### 8. Registry Pattern

Application không thể giữ:

Python

Chạy

```
crawler_a
crawler_b
crawler_c
```

Ta tạo Registry.

Python

Chạy

```
class CrawlerRegistry:

    def __init__(self):
        self._crawlers = []

    def register(self, crawler):
        self._crawlers.append(crawler)
```

### 9. Tìm plugin phù hợp

Python

Chạy

```
class CrawlerRegistry:

    ...

    def find(self, url: Url):

        for crawler in self._crawlers:

            if crawler.can_handle(url):
                return crawler

        raise LookupError(
            f"No crawler for {url.value}"
        )
```

Đây chính là Strategy Selection.

### 10. Use Case không đổi

Python

Chạy

```
class CrawlStory:

    def __init__(self, registry, repository):
        self.registry = registry
        self.repository = repository

    def execute(self, url: Url):

        crawler = self.registry.find(url)

        story = crawler.crawl(url)

        self.repository.save(story)

        return story
```

Đây là toàn bộ business orchestration.

Không có:

Python

Chạy

```
if "source-a" ...
```

### 11. Composition Root

Python

Chạy

```
registry = CrawlerRegistry()

registry.register(SourceACrawler())
registry.register(SourceBCrawler())
```

Sau này thêm:

Python

Chạy

```
registry.register(SourceCCrawler())
```

Không sửa `CrawlStory`.

### 12. Plugin Metadata

Mỗi plugin nên có metadata.

Python

Chạy

```
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    domain: str
```

Source A:

Python

Chạy

```
METADATA = PluginMetadata(
    name="Source A",
    version="1.0.0",
    domain="source-a.com",
)
```

Điều này hữu ích cho CLI và quản lý plugin.

### 13. Không hard-code domain

Thay vì:

Python

Chạy

```
return "source-a.com" in url.value
```

Ta dùng metadata.

Python

Chạy

```
class SourceACrawler:

    metadata = METADATA

    def can_handle(self, url: Url):

        return (
            urlparse(url.value).netloc
            == self.metadata.domain
        )
```

Plugin trở nên tự mô tả.

### 14. Parser không thuộc Registry

Sai:

```
Registry
 ├── Parser A
 ├── Parser B
 └── Parser C
```

Đúng:

```
Source A Plugin
 ├── Crawler
 └── Parser
```

Mỗi plugin sở hữu parser của chính nó.

Đây là high cohesion.

### 15. Crawler = Orchestrator của plugin

```
Source A
│
├── HttpClient
├── StoryParser
├── ChapterParser
└── Cleaner
```

Crawler không parse HTML trực tiếp.

Ví dụ:

Python

Chạy

```
class SourceACrawler:

    def __init__(self, http, parser):
        self.http = http
        self.parser = parser

    def crawl(self, url):

        html = self.http.get(url.value)

        return self.parser.parse_story(html, url)
```

### 16. Dependency bên trong plugin

```
SourceACrawler
      │
      ▼
 StoryParser
      │
      ▼
 BeautifulSoup
```

BeautifulSoup không bao giờ đi ra Domain.

### 17. Plugin Contract

Mỗi plugin phải đảm bảo:

|
Method

|

Contract

|
| --- | --- |
|

`can_handle()`

|

Trả `True/False`

|
|

`crawl()`

|

Trả `Story` hợp lệ

|
|

Exception

|

Chỉ raise `CrawlerError` hoặc subclass

|

Đây là LSP.

### 18. Custom Exception

Python

Chạy

```
class CrawlerError(Exception):
    pass


class UnsupportedUrlError(CrawlerError):
    pass


class ParseError(CrawlerError):
    pass
```

Application chỉ cần biết:

Python

Chạy

```
except CrawlerError:
    ...
```

Không cần biết BeautifulSoup lỗi gì.

### 19. Dynamic Plugin Discovery

Hiện tại ta đăng ký thủ công:

Python

Chạy

```
registry.register(SourceACrawler())
```

Sau này có thể tự động.

Ví dụ:

```
plugins/
    source_a/
    source_b/
```

Registry quét folder:

Python

Chạy

```
for plugin in discover_plugins():
    registry.register(plugin)
```

Đây là nền tảng của Plugin Architecture.

### 20. Một Plugin không nên làm gì?

Sai:

Python

Chạy

```
class SourceACrawler:

    def crawl(...):

        self.repository.save(...)
```

Crawler không được biết Repository.

Đúng:

```
Crawler
 ↓
Story
 ↓
Use Case
 ↓
Repository
```

### 21. Sequence Diagram

![](blob\:https://chatgpt.com/bc844831-704f-4e5f-839d-b04b44aa18af)

### 22. Blast Radius

Thêm Source D.

Kiến trúc tốt:

```
Source D
    │
    ▼
SourceDCrawler
    │
    ▼
registry.register(...)
```

Blast radius:

```
2 file
```

Kiến trúc xấu:

```
CrawlerManager
CLI
Tests
Database
Parser
...
```

Blast radius rất lớn.

### 23. Testing Plugin

Ta không test Use Case ở đây.

Ta test từng plugin riêng.

Python

Chạy

```
def test_source_a_can_handle():

    crawler = SourceACrawler()

    assert crawler.can_handle(
        Url("https://source-a.com/story/1")
    )
```

Và:

Python

Chạy

```
assert not crawler.can_handle(
    Url("https://source-b.com/story/1")
)
```

### 24. Testing Registry

Python

Chạy

```
registry = CrawlerRegistry()

registry.register(SourceACrawler())
registry.register(SourceBCrawler())

crawler = registry.find(
    Url("https://source-b.com/story/99")
)

assert isinstance(crawler, SourceBCrawler)
```

Registry được test độc lập.

### 25. Tổng kết

Sau Buổi 22, chúng ta đã hoàn thành Crawler Port của hệ thống.

```
Application
      │
      ▼
StoryCrawler (Port)
      ▲
 ┌────┼────┐
 │    │    │
 ▼    ▼    ▼
A    B    C
```

Mỗi plugin:

* Có metadata

* Có parser riêng

* Có HTTP riêng nếu cần

* Không biết Repository

* Không biết CLI

Đây là nền tảng để sang Buổi 23, nơi chúng ta sẽ xây HTTP Client + HTML Parser thật sự với `requests/httpx` và `BeautifulSoup`, đồng thời giữ nguyên kiến trúc vừa thiết kế.
