# Buổi 22 — Crawler Port + Plugin Architecture

Sau Buổi 21 chúng ta đã có:

```text
Domain
├── Story
├── Chapter
├── Url
├── Source
└── StoryRepository
```

Hôm nay chúng ta thiết kế phần quan trọng nhất của Story Crawler System:

```text
StoryCrawler
```

Mục tiêu:

```text
Thêm Source C
Thêm Source D
Thêm Source E

↓

Không sửa Use Case
Không sửa Domain
Không sửa Application
```

Đây là nơi:

```text
OCP
+
DIP
+
LSP
+
Plugin Architecture
```

gặp nhau.

---

# 1. Bài toán thực tế

Ban đầu ai cũng viết:

```python
class CrawlerManager:

    def crawl(self, url):

        if "source-a.com" in url:
            ...

        elif "source-b.com" in url:
            ...

        elif "source-c.com" in url:
            ...
```

Sau vài tháng:

```text
if
elif
elif
elif
elif
elif
elif
...
```

Xuất hiện OCP violation.

Mỗi lần thêm source:

```text
CrawlerManager
↓
sửa code
↓
deploy lại
```

---

# 2. Tư duy Plugin

Thay vì:

```text
CrawlerManager biết mọi source
```

ta muốn:

```text
CrawlerManager
      ↓
Crawler Interface
      ↑
      │
Source A
Source B
Source C
Source D
```

Application không cần biết crawler cụ thể.

---

# 3. Port là gì?

Trong Clean Architecture:

```text
Port
=
Abstraction
=
Contract
```

Ví dụ:

```python
class StoryCrawler(Protocol):
    ...
```

đây chính là Port.

---

# 4. StoryCrawler v1

```python
from typing import Protocol

from .story import Story
from .url import Url


class StoryCrawler(Protocol):

    def can_handle(
        self,
        url: Url,
    ) -> bool:
        ...

    def crawl(
        self,
        url: Url,
    ) -> Story:
        ...
```

Contract rất nhỏ.

Chỉ có:

```text
can_handle()
crawl()
```

ISP rất tốt.

---

# 5. Vì sao không dùng ABC?

Hoàn toàn có thể:

```python
from abc import ABC
from abc import abstractmethod


class StoryCrawler(ABC):

    @abstractmethod
    def can_handle(self, url):
        ...

    @abstractmethod
    def crawl(self, url):
        ...
```

Nhưng Python thường hợp với:

```text
Protocol
+
Duck Typing
```

hơn.

---

# 6. Crawler Contract

Một crawler phải đảm bảo:

```text
Input:
    Url

Output:
    Story

Không return:
    dict
    tuple
    str
```

Ví dụ:

Sai:

```python
def crawl(self, url):

    return {
        "title": "...",
    }
```

Đúng:

```python
def crawl(
    self,
    url,
) -> Story:
```

---

# 7. LSP Contract

Giả sử:

```python
class StoryCrawler(Protocol):

    def crawl(
        self,
        url: Url,
    ) -> Story:
        ...
```

Mọi implementation phải trả:

```text
Story
```

Không được:

```python
return None
```

hoặc:

```python
return {}
```

Đó là LSP violation.

---

# 8. Source A

```python
from story_crawler.domain.story import Story
from story_crawler.domain.source import Source


class SourceACrawler:

    def can_handle(
        self,
        url,
    ) -> bool:

        return (
            "source-a.com"
            in url.value
        )

    def crawl(
        self,
        url,
    ) -> Story:

        return Story(
            title="Story A",
            source=Source(
                "source_a"
            ),
            url=url,
        )
```

---

# 9. Source B

```python
class SourceBCrawler:

    def can_handle(
        self,
        url,
    ) -> bool:

        return (
            "source-b.com"
            in url.value
        )

    def crawl(
        self,
        url,
    ) -> Story:

        return Story(
            title="Story B",
            source=Source(
                "source_b"
            ),
            url=url,
        )
```

---

# 10. Crawler Registry

Application cần một nơi tìm crawler.

```python
class CrawlerRegistry:

    def __init__(
        self,
        crawlers,
    ):
        self._crawlers = crawlers
```

---

# 11. Tìm crawler

```python
def find(
    self,
    url,
):

    for crawler in self._crawlers:

        if crawler.can_handle(url):
            return crawler

    raise LookupError(
        "No crawler found"
    )
```

---

# 12. Registry không crawl

Đây là sai lầm rất phổ biến:

```python
class CrawlerRegistry:

    def crawl(self, url):
        ...
```

Registry chỉ:

```text
register
find
```

Không:

```text
HTTP
Parse
Save
```

SRP.

---

# 13. Use Case

```python
class CrawlStory:

    def __init__(
        self,
        registry,
        repository,
    ):
        self.registry = registry
        self.repository = repository
```

---

# 14. Execute

```python
def execute(
    self,
    url,
):

    crawler = self.registry.find(
        url
    )

    story = crawler.crawl(url)

    self.repository.save(
        story
    )

    return story
```

Nhìn kỹ:

```text
CrawlStory
```

không biết:

```text
Source A
Source B
Source C
```

---

# 15. OCP Test

Thêm:

```python
class SourceCCrawler:
    ...
```

Composition:

```python
registry = CrawlerRegistry([
    SourceACrawler(),
    SourceBCrawler(),
    SourceCCrawler(),
])
```

Không sửa:

```text
CrawlStory
Story
Repository
```

OCP đạt.

---

# 16. Nhưng Registry đang có vấn đề

Hiện tại:

```python
for crawler in crawlers
```

Mỗi request:

```text
O(n)
```

Nếu có:

```text
100 source
```

thì sao?

---

# 17. Registry v2

Ta có thể cache.

```python
class CrawlerRegistry:

    def __init__(
        self,
        crawlers,
    ):
        self._crawlers = crawlers
```

---

# 18. Nhưng đừng optimize sớm

Rất nhiều developer làm:

```python
dict
cache
factory
metaclass
singleton
```

ngay từ đầu.

Trong khi:

```text
2 source
3 source
5 source
```

thì:

```python
for crawler
```

là đủ.

Nguyên tắc:

> Make it work → Make it right → Make it fast

---

# 19. Plugin Architecture là gì?

Ta muốn:

```text
core system
```

không phụ thuộc:

```text
source_a
source_b
source_c
```

Cấu trúc:

```text
core
│
├── domain
├── application
│
└── plugin
```

---

# 20. Plugin Folder

Ví dụ:

```text
plugins/
│
├── source_a/
│
├── source_b/
│
└── source_c/
```

Mỗi plugin:

```text
crawl source riêng
```

---

# 21. Plugin Contract

Mọi plugin phải implement:

```python
StoryCrawler
```

Ví dụ:

```python
class SourceACrawler:
    ...
```

---

# 22. Plugin Discovery

Cách đơn giản:

```python
crawlers = [
    SourceACrawler(),
    SourceBCrawler(),
]
```

Hardcode.

---

# 23. Dynamic Discovery

Sau này:

```python
import pkgutil
```

hoặc:

```python
import importlib
```

scan:

```text
plugins/
```

---

# 24. Ví dụ Discovery

```python
for module in pkgutil.iter_modules(
    plugins.__path__
):
    ...
```

Tự động load plugin.

---

# 25. Đây là OCP thực sự

Thêm:

```text
plugins/source_d
```

Core không sửa.

---

# 26. Capability-based Design

Một sai lầm:

```python
class Crawler:

    crawl_story()
    crawl_chapter()
    login()
    upload()
    notify()
```

ISP violation.

---

# 27. Capability nhỏ

```python
StoryCrawler
```

```python
ChapterCrawler
```

```python
Authenticator
```

```python
Notifier
```

---

# 28. Source A

Có thể:

```python
class SourceA(
    StoryCrawler,
    ChapterCrawler,
):
    ...
```

---

# 29. Source B

Có thể chỉ:

```python
class SourceB(
    ChapterCrawler,
):
    ...
```

Không bị ép:

```python
crawl_story()
```

ISP đạt.

---

# 30. LSP và Plugin

Sai:

```python
class SourceBCrawler:

    def crawl(self, url):

        raise NotImplementedError
```

Nếu đăng ký:

```text
StoryCrawler
```

thì sai.

---

# 31. Exception Strategy

Crawler có thể fail.

Ví dụ:

```text
404
timeout
blocked
```

Nên làm gì?

---

# 32. Cách tệ

```python
return None
```

Use Case phải:

```python
if story is None:
```

khắp nơi.

---

# 33. Tốt hơn

```python
raise CrawlError(...)
```

Domain/Application xử lý rõ ràng hơn.

---

# 34. Domain Exception

```python
class CrawlError(
    Exception
):
    pass
```

---

# 35. Infrastructure Exception

```python
class HttpTimeoutError(
    CrawlError
):
    pass
```

```python
class ParsingError(
    CrawlError
):
    pass
```

---

# 36. Retry nằm ở đâu?

Sai:

```python
CrawlStory
```

retry.

Vì:

```text
retry
=
infrastructure concern
```

---

# 37. Retry Decorator

```python
class RetryCrawler:

    def __init__(
        self,
        crawler,
    ):
        self.crawler = crawler
```

---

# 38. Wrapper

```python
def crawl(self, url):

    for _ in range(3):

        try:
            return self.crawler.crawl(
                url
            )

        except CrawlError:
            ...
```

Đây là:

```text
Decorator Pattern
+
OCP
```

---

# 39. Composition

```python
crawler = RetryCrawler(
    SourceACrawler()
)
```

Không sửa SourceA.

---

# 40. Logging cũng vậy

```python
crawler = LoggingCrawler(
    RetryCrawler(
        SourceACrawler()
    )
)
```

---

# 41. Plugin Metadata

Một crawler có thể khai báo:

```python
class SourceACrawler:

    name = "source_a"

    version = "1.0"
```

---

# 42. Registry Info

```python
registry.list()
```

có thể trả:

```text
source_a
source_b
source_c
```

---

# 43. Đây là kiến trúc mở rộng thực tế

```text
Application
        ↓
StoryCrawler
        ↑
        │
 ┌──────┼──────┐
 ↓      ↓      ↓
A      B      C
```

---

# 44. Dependency Direction

Plugin:

```text
Source A
 ↓
StoryCrawler
```

Không phải:

```text
StoryCrawler
 ↓
Source A
```

Đây là DIP.

---

# 45. Blast Radius

Thêm Source D.

Xấu:

```text
Manager
Parser
Database
CLI
Test
```

đều sửa.

Tốt:

```text
SourceD
```

và:

```python
registry.register(...)
```

---

# 46. Unit Test Registry

```python
class FakeCrawler:

    def can_handle(
        self,
        url,
    ):
        return True
```

Test:

```python
crawler = registry.find(url)
```

Không cần:

```text
Internet
SQLite
```

---

# 47. Kiểm tra OCP

Hỏi:

> Thêm crawler mới có phải sửa Use Case không?

Nếu:

```text
Không
```

→ OCP tốt.

---

# 48. Kiểm tra DIP

Hỏi:

> Use Case có import SourceACrawler không?

Nếu:

```text
Không
```

→ DIP tốt.

---

# 49. Kiểm tra LSP

Hỏi:

> Mọi crawler có trả Story không?

Nếu:

```text
Có
```

→ LSP tốt.

---

# 50. Kiểm tra ISP

Hỏi:

> Có crawler nào bị ép implement method không dùng?

Nếu:

```text
Không
```

→ ISP tốt.

---

# Tổng kết Buổi 22

Chúng ta đã xây:

```text
StoryCrawler (Port)
        ↑
        │
 ┌──────┼──────┐
 ↓      ↓      ↓
A      B      C
```

và:

```text
CrawlStory
      ↓
CrawlerRegistry
      ↓
StoryCrawler
```

Đây là nền tảng của:

```text
Plugin Architecture
OCP
DIP
LSP
ISP
```

---

# Buổi 23

Buổi tiếp theo chúng ta sẽ đi vào:

```text
HTTP Client
     ↓
HTML
     ↓
Parser
     ↓
Story
```

và thiết kế:

```text
HttpClient Port
Parser Port
Requests Adapter
BeautifulSoup Adapter
```

để crawler thực sự bắt đầu crawl dữ liệu thật mà vẫn giữ nguyên SOLID và Clean Architecture.
