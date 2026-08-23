# Buổi 19 — Refactoring `CrawlerManager` từ God Object → Clean Architecture

Đây là **buổi thực chiến quan trọng nhất của phần SOLID**.

Hôm nay chúng ta không học thêm một pattern mới. Thay vào đó, chúng ta sẽ lấy một thiết kế **xấu nhưng rất phổ biến trong Python**, sau đó refactor từng bước:

```text
CrawlerManager
      ↓
   God Object
      ↓
     SRP
      ↓
     OCP
      ↓
     DIP
      ↓
     DDD
      ↓
Clean Architecture
```

---

# 1. Bài toán thực tế

Giả sử bạn đang xây hệ thống crawl truyện.

Có:

```text
Source A
Source B
Source C
```

Ban đầu developer viết:

```python
class CrawlerManager:

    def crawl(self, url):
        ...
```

Sau vài tháng, class trở thành:

```text
CrawlerManager
├── HTTP request
├── retry
├── authentication
├── detect source
├── parse story
├── parse chapter
├── clean HTML
├── save database
├── update progress
├── logging
├── notification
└── error handling
```

Đây là **God Object**.

---

# 2. Version 0 — Code ban đầu

Hãy xem một phiên bản thực tế hơn.

```python
import sqlite3
import requests
from bs4 import BeautifulSoup


class CrawlerManager:

    def __init__(self):
        self.connection = sqlite3.connect(
            "stories.db"
        )

    def crawl(self, url):

        # detect source
        if "source-a.com" in url:
            source = "a"

        elif "source-b.com" in url:
            source = "b"

        else:
            raise ValueError(
                "Unsupported source"
            )

        # HTTP
        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        html = response.text

        # parsing
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        if source == "a":

            title = soup.select_one(
                ".story-title"
            ).get_text(strip=True)

            content = soup.select_one(
                ".chapter-content"
            ).get_text()

        elif source == "b":

            title = soup.select_one(
                "#novel-name"
            ).get_text(strip=True)

            content = soup.select_one(
                "#content"
            ).get_text()

        # clean
        content = content.strip()

        # database
        self.connection.execute(
            """
            INSERT INTO stories(
                title,
                source,
                url,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                source,
                url,
                content,
            ),
        )

        self.connection.commit()

        # notification
        print(
            f"Crawled: {title}"
        )
```

Code này **chạy được**.

Nhưng architecture rất tệ.

---

# 3. Tại sao đây là God Object?

Một method `crawl()` đang có:

```text
1. Source detection
2. HTTP
3. Parsing
4. Cleaning
5. Persistence
6. Notification
```

Có quá nhiều responsibility.

Nếu hỏi:

> "Class này thay đổi vì những lý do nào?"

Có thể trả lời:

```text
Website thay đổi
HTTP thay đổi
HTML thay đổi
Database thay đổi
Business rule thay đổi
Notification thay đổi
```

Đây chính là SRP violation.

---

# 4. Code smell đầu tiên — Long Method

Method:

```python
crawl()
```

đang làm quá nhiều việc.

Đây là:

> **Long Method**

Nhưng đừng vội tạo 10 class.

Trước tiên phải hiểu responsibility.

---

# 5. Xác định các responsibility

Ta phân loại:

```text
CrawlerManager
│
├── Source detection
│
├── HTTP communication
│
├── HTML parsing
│
├── Content cleaning
│
├── Persistence
│
└── Notification
```

Có ít nhất 6 responsibility.

---

# 6. Refactoring bước 1 — Extract Method

Trước khi Extract Class, ta có thể tách method.

```python
class CrawlerManager:

    def crawl(self, url):

        source = self._detect_source(url)

        html = self._download(url)

        title, content = self._parse(
            source,
            html,
        )

        content = self._clean(content)

        self._save(
            title,
            source,
            url,
            content,
        )

        self._notify(title)
```

Bây giờ dễ đọc hơn.

Nhưng:

> **SRP vẫn chưa được giải quyết.**

Class vẫn sở hữu tất cả logic.

---

# 7. Refactoring bước 2 — Extract Class

Tách HTTP:

```python
class HttpClient:

    def get(self, url: str) -> str:

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.text
```

`CrawlerManager`:

```python
class CrawlerManager:

    def __init__(
        self,
        http_client,
    ):
        self.http_client = http_client

    def crawl(self, url):

        html = self.http_client.get(url)
```

Ta vừa tạo boundary đầu tiên.

---

# 8. Tại sao đây là DIP?

Trước:

```text
CrawlerManager
      ↓
requests
```

Sau:

```text
CrawlerManager
      ↓
HttpClient
      ↑
      │
RequestsHttpClient
```

High-level module không cần biết:

```text
requests
httpx
urllib
aiohttp
```

Nó chỉ cần:

```text
HttpClient
```

---

# 9. Dùng Protocol

Trong Python:

```python
from typing import Protocol


class HttpClient(Protocol):

    def get(
        self,
        url: str,
    ) -> str:
        ...
```

Implementation:

```python
class RequestsHttpClient:

    def get(self, url: str) -> str:

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.text
```

Không cần inheritance.

---

# 10. Test HTTP mà không cần Internet

Ta có:

```python
class FakeHttpClient:

    def __init__(self, html):
        self.html = html

    def get(self, url):
        return self.html
```

Test:

```python
client = FakeHttpClient(
    "<html>...</html>"
)

crawler = CrawlerManager(
    http_client=client
)
```

Không gọi Internet.

Đây là lợi ích trực tiếp của DIP.

---

# 11. Refactoring bước 3 — Parser

Tiếp theo:

```python
class SourceAParser:

    def parse_story(
        self,
        html: str,
    ):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = soup.select_one(
            ".story-title"
        ).get_text(strip=True)

        content = soup.select_one(
            ".chapter-content"
        ).get_text()

        return title, content
```

Source B:

```python
class SourceBParser:

    def parse_story(
        self,
        html: str,
    ):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = soup.select_one(
            "#novel-name"
        ).get_text(strip=True)

        content = soup.select_one(
            "#content"
        ).get_text()

        return title, content
```

---

# 12. Vấn đề mới

CrawlerManager vẫn có:

```python
if "source-a.com":
    parser = SourceAParser()

elif "source-b.com":
    parser = SourceBParser()
```

Ví dụ:

```python
class CrawlerManager:

    def crawl(self, url):

        if "source-a.com" in url:
            parser = SourceAParser()

        elif "source-b.com" in url:
            parser = SourceBParser()

        ...
```

Chúng ta vừa tách class nhưng **OCP vẫn bị phá**.

---

# 13. Refactoring bước 4 — Strategy

Ta tạo:

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
    ):
        ...
```

Source A:

```python
class SourceACrawler:

    def __init__(
        self,
        http_client,
        parser,
    ):
        self.http_client = http_client
        self.parser = parser

    def can_handle(self, url):

        return "source-a.com" in url

    def crawl_story(self, url):

        html = self.http_client.get(url)

        return self.parser.parse_story(
            html
        )
```

Source B tương tự.

---

# 14. Bây giờ `CrawlerManager` không cần biết Source

Thay vì:

```python
if source_a:
    ...
elif source_b:
    ...
```

ta có:

```python
class CrawlerRegistry:

    def __init__(
        self,
        crawlers,
    ):
        self.crawlers = crawlers

    def find(self, url):

        for crawler in self.crawlers:

            if crawler.can_handle(url):
                return crawler

        raise LookupError(
            "No crawler found"
        )
```

---

# 15. `CrawlerManager` được giảm trách nhiệm

```python
class CrawlerManager:

    def __init__(
        self,
        registry,
    ):
        self.registry = registry

    def crawl(self, url):

        crawler = self.registry.find(
            url
        )

        return crawler.crawl_story(
            url
        )
```

Nhìn lại:

```text
CrawlerManager
├── find crawler
└── execute crawler
```

Đã tốt hơn rất nhiều.

Nhưng tên `CrawlerManager` vẫn không lý tưởng.

---

# 16. Đổi tên thành Use Case

Tên:

```python
CrawlerManager
```

thường là dấu hiệu nguy hiểm.

`Manager` không nói lên responsibility.

Ta đổi thành:

```python
CrawlStory
```

hoặc:

```python
CrawlStoryUseCase
```

```python
class CrawlStory:

    def __init__(
        self,
        registry,
    ):
        self.registry = registry

    def execute(self, url):

        crawler = self.registry.find(
            url
        )

        return crawler.crawl_story(
            url
        )
```

Bây giờ class nói chính xác nó làm gì.

---

# 17. Refactoring bước 5 — Domain Model

Code cũ trả:

```python
title, content
```

Đây là primitive data.

Ta tạo:

```python
from dataclasses import dataclass


@dataclass
class Story:

    title: str
    source: str
    url: str
```

Chapter:

```python
@dataclass
class Chapter:

    title: str
    url: str
    content: str
```

Bây giờ crawler trả:

```python
Story(...)
```

thay vì:

```python
tuple
dict
```

---

# 18. Tại sao đây là DDD?

Ta đang nói bằng ngôn ngữ domain:

```text
Story
Chapter
Crawler
```

thay vì:

```text
dict
tuple
HTML
row
record
```

Domain model trở thành ngôn ngữ chung giữa:

```text
Application
Domain
Infrastructure
```

Đây là **Ubiquitous Language**.

---

# 19. Nhưng `Story` có nên chứa HTML?

Không.

Sai:

```python
@dataclass
class Story:

    html: str
```

HTML là representation của website.

Domain cần:

```text
title
source
url
```

chứ không cần:

```text
BeautifulSoup
HTML DOM
CSS selector
```

---

# 20. Refactoring bước 6 — Repository

Code cũ:

```python
self.connection.execute(...)
```

nằm trong crawler.

Đây là vấn đề lớn.

Crawler không nên biết SQLite.

Tạo:

```python
class StoryRepository(Protocol):

    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

SQLite:

```python
class SQLiteStoryRepository:

    def save(
        self,
        story: Story,
    ) -> None:

        self.connection.execute(
            """
            INSERT INTO stories(
                title,
                source,
                url
            )
            VALUES (?, ?, ?)
            """,
            (
                story.title,
                story.source,
                story.url,
            ),
        )

        self.connection.commit()
```

---

# 21. Use Case orchestration

Bây giờ:

```python
class CrawlStory:

    def __init__(
        self,
        registry,
        repository,
    ):
        self.registry = registry
        self.repository = repository

    def execute(self, url):

        crawler = self.registry.find(
            url
        )

        story = crawler.crawl_story(
            url
        )

        self.repository.save(
            story
        )

        return story
```

Đây là một Use Case rất rõ:

```text
1. tìm crawler
2. crawl
3. lưu story
4. trả kết quả
```

---

# 22. Đây chính là Application Layer

Application layer không nên biết:

```text
BeautifulSoup selector
requests
sqlite3
Typer
```

Nó chỉ orchestration:

```text
Crawler
Repository
Domain
```

---

# 23. Refactoring bước 7 — Content Cleaning

Code cũ:

```python
content = content.strip()
```

Trong project thật, cleaning có thể trở nên rất lớn:

```text
remove ads
remove scripts
remove styles
remove navigation
remove comments
normalize whitespace
extract code blocks
```

Không nên để:

```python
SourceACrawler
```

làm tất cả.

Tạo:

```python
class ContentCleaner(Protocol):

    def clean(
        self,
        content: str,
    ) -> str:
        ...
```

---

# 24. Implementation

```python
class HtmlContentCleaner:

    def clean(
        self,
        content: str,
    ) -> str:

        return content.strip()
```

Sau này:

```text
BeautifulSoupCleaner
MarkdownCleaner
NovelCleaner
```

có thể thay thế.

---

# 25. Source crawler lúc này

```python
class SourceACrawler:

    def __init__(
        self,
        http_client,
        parser,
        cleaner,
    ):
        self.http_client = http_client
        self.parser = parser
        self.cleaner = cleaner

    def can_handle(self, url):

        return "source-a.com" in url

    def crawl_story(self, url):

        html = self.http_client.get(url)

        story = self.parser.parse_story(
            html,
            url,
        )

        story.content = (
            self.cleaner.clean(
                story.content
            )
        )

        return story
```

---

# 26. Nhưng ở đây xuất hiện một vấn đề DDD

Nếu `Story` chỉ có:

```python
title
source
url
```

thì:

```python
story.content
```

không tồn tại.

Điều này buộc chúng ta suy nghĩ:

> `content` thuộc `Story` hay `Chapter`?

Trong hệ thống truyện:

```text
Story
 ├── metadata
 └── Chapters
```

Vậy có thể thiết kế:

```python
@dataclass
class Chapter:

    title: str
    url: str
    content: str
```

và:

```python
@dataclass
class Story:

    title: str
    source: str
    url: str
```

Đây là một ví dụ quan trọng:

> **Refactoring SOLID có thể làm lộ ra vấn đề Domain Model.**

---

# 27. DDD giúp sửa architecture

Ta có:

```text
Story
 ├── title
 ├── source
 └── url

Chapter
 ├── title
 ├── url
 └── content
```

Bây giờ:

```python
class ChapterCrawler(Protocol):

    def crawl_chapter(
        self,
        url: str,
    ) -> Chapter:
        ...
```

và:

```python
class StoryCrawler(Protocol):

    def crawl_story(
        self,
        url: str,
    ) -> Story:
        ...
```

---

# 28. ISP xuất hiện rất tự nhiên

Không phải crawler nào cũng cần:

```text
crawl_story
crawl_chapter
login
upload
notify
```

Thay vào đó:

```text
StoryCrawler
ChapterCrawler
Authenticator
Notifier
```

Một source có thể implement:

```python
class SourceACrawler(
    StoryCrawler,
    ChapterCrawler,
):
    ...
```

Một source khác chỉ:

```python
class SourceBCrawler(
    ChapterCrawler,
):
    ...
```

Không bị ép implement capability không cần thiết.

---

# 29. LSP cũng rõ hơn

Nếu:

```python
class SourceBCrawler:

    def crawl_story(...):
        raise NotImplementedError
```

thì không nên đăng ký nó dưới:

```text
StoryCrawler
```

Nếu nó chỉ crawl chapter:

```text
ChapterCrawler
```

thì dùng interface đó.

ISP giúp tránh LSP violation.

Đây là lý do các nguyên lý SOLID **liên kết với nhau**.

---

# 30. Architecture sau refactoring

Ta đã đi từ:

```text
CrawlerManager
    └── everything
```

đến:

```text
                    CLI
                     │
                     ↓
                 CrawlStory
                 Use Case
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
      Crawler                 Repository
       Port                     Port
          ↑                     ↑
    ┌─────┴─────┐               │
    ↓           ↓               ↓
 SourceA     SourceB          SQLite
    │           │
    ↓           ↓
 HTTP +      HTTP +
 Parser      Parser
```

---

# 31. Clean Architecture

Bây giờ đặt vào các layer:

```text
┌─────────────────────────────────────┐
│         Presentation                │
│                                     │
│              CLI                    │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│         Application                 │
│                                     │
│           CrawlStory                │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│            Domain                  │
│                                     │
│ Story / Chapter / Ports             │
└──────────────────┬──────────────────┘
                   ↑
┌─────────────────────────────────────┐
│          Infrastructure             │
│                                     │
│ SourceA / SourceB / SQLite / HTTP  │
└─────────────────────────────────────┘
```

---

# 32. Dependency Rule

Điểm cực kỳ quan trọng:

```text
Infrastructure
       ↓
    Domain
```

nhưng:

```text
Domain
   ✗
Infrastructure
```

Domain không được import:

```python
import requests
import sqlite3
from bs4 import BeautifulSoup
```

---

# 33. Application cũng không import infrastructure

Không được:

```python
from infrastructure.source_a import (
    SourceACrawler,
)
```

Trong:

```python
application/crawl_story.py
```

Application chỉ:

```python
from domain.crawler import Crawler
from domain.story import Story
```

---

# 34. Composition Root

Tất cả implementation cụ thể được nối tại:

```python
# composition.py

http_client = RequestsHttpClient()

source_a = SourceACrawler(
    http_client=http_client,
    parser=SourceAParser(),
    cleaner=HtmlContentCleaner(),
)

source_b = SourceBCrawler(
    http_client=http_client,
    parser=SourceBParser(),
    cleaner=HtmlContentCleaner(),
)

registry = CrawlerRegistry([
    source_a,
    source_b,
])

repository = SQLiteStoryRepository(
    connection
)

use_case = CrawlStory(
    registry=registry,
    repository=repository,
)
```

Đây là nơi:

> **Dependency Graph được xây dựng.**

---

# 35. Nhìn lại DIP

Ban đầu:

```text
CrawlerManager
 ↓
requests
 ↓
sqlite3
 ↓
BeautifulSoup
```

High-level module bị kéo xuống infrastructure.

Sau refactoring:

```text
              CrawlStory
                  ↓
          ┌───────┴────────┐
          ↓                ↓
       Crawler         Repository
          ↑                ↑
          │                │
     SourceA/B          SQLite
```

Dependency direction được đảo ngược.

Đây chính là **Dependency Inversion Principle**.

---

# 36. OCP xuất hiện ở đâu?

Thêm Source C:

```python
class SourceCCrawler:
    ...
```

Composition:

```python
registry.register(
    SourceCCrawler(...)
)
```

Không sửa:

```text
CrawlStory
CrawlerRegistry
Story
CLI
```

---

# 37. SRP xuất hiện ở đâu?

| Component               | Responsibility          |
| ----------------------- | ----------------------- |
| `CrawlStory`            | Orchestrate use case    |
| `CrawlerRegistry`       | Tìm crawler             |
| `SourceACrawler`        | Crawl Source A          |
| `SourceAParser`         | Parse HTML Source A     |
| `HttpClient`            | HTTP                    |
| `ContentCleaner`        | Clean content           |
| `StoryRepository`       | Persistence abstraction |
| `SQLiteStoryRepository` | SQLite persistence      |
| `CLI`                   | Presentation            |

Không phải:

```text
CrawlerManager
    ↓
làm tất cả
```

---

# 38. Testability

Bây giờ test Use Case:

```python
class FakeCrawler:

    def can_handle(self, url):
        return True

    def crawl_story(self, url):

        return Story(
            title="Test Story",
            source="fake",
            url=url,
        )
```

Fake Repository:

```python
class FakeStoryRepository:

    def __init__(self):
        self.saved = []

    def save(self, story):
        self.saved.append(story)
```

Test:

```python
def test_crawl_story():

    registry = CrawlerRegistry([
        FakeCrawler()
    ])

    repository = FakeStoryRepository()

    use_case = CrawlStory(
        registry,
        repository,
    )

    story = use_case.execute(
        "https://example.com/story"
    )

    assert story.title == "Test Story"

    assert len(
        repository.saved
    ) == 1
```

Không:

```text
SQLite
Internet
BeautifulSoup
Typer
```

---

# 39. Đây là lý do "architecture tốt" không chỉ để đẹp

Architecture ban đầu:

```text
test CrawlerManager
      ↓
SQLite
      ↓
Internet
      ↓
HTML
```

Test chậm và dễ fail.

Architecture mới:

```text
test CrawlStory
      ↓
FakeCrawler
      ↓
FakeRepository
```

Test:

```text
fast
isolated
deterministic
```

---

# 40. Refactoring theo từng bước

Đây là quy trình bạn nên ghi nhớ:

```text
1. God Object
       ↓
2. Identify responsibilities
       ↓
3. Extract Method
       ↓
4. Extract Class
       ↓
5. Introduce abstraction
       ↓
6. Dependency Injection
       ↓
7. Strategy / Registry
       ↓
8. Domain Model
       ↓
9. Repository
       ↓
10. Use Case
       ↓
11. Composition Root
       ↓
12. Clean Architecture
```

**Không nên nhảy thẳng từ God Object sang 30 class.**

---

# 41. Sai lầm rất phổ biến

Sau khi học SOLID, developer dễ đi quá xa:

```text
StoryFactoryFactory
CrawlerFactoryFactory
RepositoryManager
ServiceManager
ManagerFactory
AbstractCrawlerFactory
```

Rồi architecture trở thành:

```text
                    Factory
                       ↓
                Abstract Factory
                       ↓
                  Factory
                       ↓
                   Manager
```

Đây là **over-engineering**.

SOLID không yêu cầu:

> "Mỗi class chỉ có một method."

---

# 42. Khi nào KHÔNG nên tách?

Ví dụ:

```python
def normalize_title(title):
    return title.strip()
```

Không nhất thiết phải tạo:

```python
class TitleNormalizer:
    def normalize(...):
        ...
```

Nếu:

* logic cực nhỏ
* không có lifecycle
* không có dependency
* không cần replace
* không cần test riêng

thì function có thể tốt hơn class.

Python rất mạnh về:

```text
function
composition
duck typing
```

SOLID không có nghĩa:

> "Class càng nhiều càng tốt."

---

# 43. Một nguyên tắc thực tế

Hãy hỏi:

> **"Nếu logic này thay đổi, cái gì sẽ phải thay đổi?"**

Nếu:

```text
Source A HTML thay đổi
```

thì chỉ nên ảnh hưởng:

```text
SourceAParser
```

Nếu:

```text
Database đổi SQLite → PostgreSQL
```

thì chỉ nên ảnh hưởng:

```text
PostgresRepository
Composition Root
```

Nếu:

```text
CLI → REST API
```

thì:

```text
Presentation
```

thay đổi.

Domain:

```text
không đổi
```

Đây chính là **Changeability**.

---

# 44. Architecture tốt đo bằng "blast radius"

Ví dụ:

### Thêm Source C

Xấu:

```text
Source C
 ↓
CrawlerManager
 ↓
Database
 ↓
CLI
 ↓
Tests
```

Rất nhiều file phải sửa.

Tốt:

```text
Source C
 ↓
SourceCCrawler
```

và composition:

```text
registry.register(...)
```

**Blast radius nhỏ.**

---

# 45. Đây mới là bản chất của SOLID

Không phải học thuộc:

```text
S = Single Responsibility
O = Open/Closed
L = Liskov
I = Interface Segregation
D = Dependency Inversion
```

Mà phải nhìn được:

```text
Change
 ↓
What needs modification?
 ↓
How much code is affected?
 ↓
Can we isolate the change?
```

SOLID là một tập các nguyên lý giúp giảm **cost of change**.

---

# 46. Tổng kết Buổi 19

Chúng ta bắt đầu với:

```python
class CrawlerManager:
    ...
```

một God Object chứa:

```text
HTTP
Parsing
Cleaning
Source detection
Database
Notification
```

Sau refactoring:

```text
CLI
 ↓
CrawlStory
 ↓
CrawlerRegistry
 ↓
Crawler Protocol
 ├── SourceA
 ├── SourceB
 └── SourceC

CrawlStory
 ↓
StoryRepository
 ↓
SQLiteRepository
```

Và bên trong crawler:

```text
SourceCrawler
 ├── HttpClient
 ├── Parser
 └── Cleaner
```

---

# 47. Toàn bộ SOLID trong một hình

```text
                         ┌─────────────┐
                         │     CLI     │
                         └──────┬──────┘
                                │
                                ↓
                     ┌──────────────────┐
                     │   CrawlStory     │
                     │    Use Case      │
                     └───────┬──────────┘
                             │
                 ┌───────────┴───────────┐
                 ↓                       ↓
        ┌─────────────────┐    ┌─────────────────┐
        │ Crawler Protocol │    │Repository Port │
        └────────┬────────┘    └────────┬────────┘
                 ↑                      ↑
          ┌──────┴──────┐               │
          │             │               │
          ↓             ↓               ↓
       Source A      Source B        SQLite
          │             │
       ┌──┴──┐       ┌──┴──┐
       ↓     ↓       ↓     ↓
     HTTP  Parser   HTTP  Parser
```

---

# 48. Mapping cuối cùng

```text
SRP
 ↓
Tách God Object

OCP
 ↓
Crawler Plugin / Registry

LSP
 ↓
Crawler phải tuân behavioral contract

ISP
 ↓
StoryCrawler / ChapterCrawler / Authenticator

DIP
 ↓
Use Case → Protocol
             ↑
          Plugin

DDD
 ↓
Story / Chapter / Repository

Clean Architecture
 ↓
Presentation
     ↓
Application
     ↓
Domain
     ↑
Infrastructure
```

---

# 49. Bài tập Buổi 19 — rất quan trọng

Hãy lấy class ban đầu:

```python
class CrawlerManager:

    def crawl(self, url):
        ...
```

và tự thiết kế lại thành tối thiểu:

```text
domain/
    story.py
    chapter.py
    crawler.py
    repository.py

application/
    crawl_story.py

infrastructure/
    http/
    crawlers/
        source_a.py
        source_b.py
    persistence/
        sqlite_story_repository.py

presentation/
    cli.py

composition.py
```

Sau đó kiểm tra 5 câu:

1. **Thêm Source C có phải sửa Use Case không?**
2. **Đổi SQLite sang PostgreSQL có phải sửa Domain không?**
3. **Test Use Case có cần Internet không?**
4. **Test Domain có cần SQLite không?**
5. **CLI có biết `requests`, `sqlite3`, `BeautifulSoup` không?**

Nếu câu trả lời lần lượt là:

```text
Không
Không
Không
Không
Không
```

thì bạn đã đạt được mục tiêu của Buổi 19.

---

# Phần VII — Mini Project

Và bây giờ chúng ta đã có đủ nền tảng để bước sang project lớn:

```text
                    Story Crawler System

                         ┌──────────┐
                         │   CLI    │
                         └────┬─────┘
                              ↓
                       ┌─────────────┐
                       │  Use Case   │
                       └──────┬──────┘
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
       Crawler Interface                 Repository
              ↓                               ↓
       ┌──────┴──────┐                     SQLite
       ↓             ↓
   Source A       Source B
```

**Buổi 20** sẽ không còn là ví dụ nhỏ nữa. Chúng ta sẽ bắt đầu thiết kế **Story Crawler System hoàn chỉnh**, theo kiểu project thực tế: `src/` layout, Domain, Application, Infrastructure, CLI, plugin crawler, Repository, SQLite và Dependency Injection — sau đó mới lần lượt bổ sung test và các source crawler.
