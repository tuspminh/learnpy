# Buổi 23 — HTTP Client + HTML Parser

Hôm nay chúng ta nối **Crawler Plugin** với Internet thật.

Nhưng mục tiêu không phải chỉ là:

```python
requests.get(url)
BeautifulSoup(...)
```

Mà là học cách đặt chúng **đúng vị trí trong architecture**.

Kiến trúc sau buổi này:

```text
CLI
 │
 ▼
CrawlStory
 │
 ▼
CrawlerRegistry
 │
 ▼
SourceACrawler
 │
 ├── HttpClient
 │      ↓
 │   requests/httpx
 │
 └── StoryParser
        ↓
    BeautifulSoup
```

Điểm quan trọng:

> `requests` và `BeautifulSoup` là Infrastructure. Chúng không được lan vào Domain/Application.

---

# 1. Vấn đề của cách viết trực tiếp

Một người mới thường viết:

```python
class SourceACrawler:

    def crawl(self, url):

        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = soup.select_one(
            "h1"
        ).text

        return Story(...)
```

Code này chạy được.

Nhưng có vấn đề.

`SourceACrawler` đang biết quá nhiều:

```text
HTTP
HTML
BeautifulSoup
CSS selector
Domain
```

Cohesion thấp.

---

# 2. Tách HTTP Client

Tạo abstraction:

```python
from typing import Protocol


class HttpClient(Protocol):

    def get(self, url: str) -> str:
        ...
```

Đây là một **Port**.

Application/plugin không cần biết HTTP library nào được sử dụng.

---

# 3. Requests implementation

```python
import requests


class RequestsHttpClient:

    def get(self, url: str) -> str:

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.text
```

Dependency:

```text
RequestsHttpClient
        ↓
     requests
```

Chỉ Infrastructure biết `requests`.

---

# 4. Tại sao không inject `requests.Session` trực tiếp?

Không nên:

```python
class SourceACrawler:

    def __init__(self, session):
        self.session = session
```

nếu `session` là object đặc thù của `requests`.

Ta muốn:

```text
SourceACrawler
      ↓
HttpClient
      ↑
RequestsHttpClient
```

Dependency hướng vào abstraction.

Đây là **DIP**.

---

# 5. HttpClient nên làm gì?

Chỉ:

```text
GET
POST
timeout
headers
response
```

Không nên:

```text
parse HTML
extract Story
save database
```

Ví dụ tốt:

```python
html = http.get(url)
```

Không phải:

```python
story = http.get_story(url)
```

Vì `get_story()` thuộc crawler/parser, không thuộc HTTP.

---

# 6. Parser cũng là abstraction

Tạo:

```python
from typing import Protocol

from story_crawler.domain.story import Story
from story_crawler.domain.value_objects import Url


class StoryParser(Protocol):

    def parse(
        self,
        html: str,
        url: Url,
    ) -> Story:
        ...
```

Bây giờ:

```text
Crawler
 ├── HttpClient
 └── StoryParser
```

---

# 7. Source A Parser

```python
from bs4 import BeautifulSoup

from story_crawler.domain.story import Story
from story_crawler.domain.value_objects import (
    Source,
    Url,
)


class SourceAStoryParser:

    def parse(
        self,
        html: str,
        url: Url,
    ) -> Story:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title_element = soup.select_one(
            "h1.story-title"
        )

        if title_element is None:
            raise ValueError(
                "Story title not found"
            )

        title = title_element.get_text(
            strip=True
        )

        return Story(
            title=title,
            source=Source("source_a"),
            url=url,
        )
```

---

# 8. Parser có nhiệm vụ gì?

Parser:

```text
HTML
 ↓
Domain Object
```

Ví dụ:

```text
HTML
 ↓
BeautifulSoup
 ↓
title
 ↓
Story
```

Parser **không**:

```text
save database
download image
retry request
print console
```

---

# 9. Crawler bây giờ rất sạch

```python
class SourceACrawler:

    def __init__(
        self,
        http_client,
        parser,
    ):
        self.http = http_client
        self.parser = parser

    def can_handle(self, url):

        return (
            urlparse(url.value).netloc
            == "source-a.com"
        )

    def crawl(self, url):

        html = self.http.get(
            url.value
        )

        return self.parser.parse(
            html,
            url,
        )
```

Nhìn vào đây ta thấy responsibility rất rõ:

```text
SourceACrawler
    ↓
orchestrate

HttpClient
    ↓
download

Parser
    ↓
parse
```

---

# 10. Đây chính là SRP

Không phải:

```text
Crawler làm mọi thứ
```

mà:

```text
Crawler
 ├── điều phối

HttpClient
 ├── HTTP

Parser
 ├── HTML parsing
```

Mỗi thành phần có một responsibility tương đối rõ.

---

# 11. Dependency Graph

```text
SourceACrawler
      │
 ┌────┴────┐
 ↓         ↓
HttpClient Parser
 ↑         ↑
 │         │
Requests   SourceAParser
```

Infrastructure implementation:

```text
RequestsHttpClient
SourceAStoryParser
```

---

# 12. Test Crawler mà không cần Internet

Đây là lợi ích rất lớn.

Ta tạo Fake HTTP:

```python
class FakeHttpClient:

    def __init__(self, html):
        self.html = html

    def get(self, url):
        return self.html
```

HTML:

```python
HTML = """
<html>
<body>
    <h1 class="story-title">
        Test Story
    </h1>
</body>
</html>
"""
```

---

# 13. Test Parser

```python
def test_parser():

    parser = SourceAStoryParser()

    story = parser.parse(
        HTML,
        Url(
            "https://source-a.com/story/1"
        ),
    )

    assert story.title == "Test Story"
```

Không có:

```text
Internet
requests
database
```

---

# 14. Test Crawler

```python
def test_crawler():

    http = FakeHttpClient(HTML)

    parser = SourceAStoryParser()

    crawler = SourceACrawler(
        http_client=http,
        parser=parser,
    )

    story = crawler.crawl(
        Url(
            "https://source-a.com/story/1"
        )
    )

    assert story.title == "Test Story"
```

Đây là **Dependency Injection**.

---

# 15. Fake vs Mock

Trong trường hợp này:

```python
FakeHttpClient
```

là một **Fake**.

Nó có behavior thực tế đơn giản:

```python
def get(url):
    return html
```

Không cần `unittest.mock`.

---

# 16. Khi nào dùng Mock?

Ví dụ muốn kiểm tra:

> `Crawler` có gọi HTTP đúng một lần không?

Có thể:

```python
from unittest.mock import Mock

http = Mock()

http.get.return_value = HTML
```

Sau đó:

```python
crawler.crawl(url)

http.get.assert_called_once_with(
    url.value
)
```

Mock hữu ích khi muốn kiểm tra interaction.

---

# 17. Parser không nên phụ thuộc HTTP

Sai:

```python
class StoryParser:

    def parse(self, url):
        html = requests.get(url)
```

Parser phải nhận:

```python
html
```

chứ không phải URL rồi tự tải.

Đúng:

```python
parser.parse(
    html,
    url,
)
```

Đây là separation of concerns.

---

# 18. Parser không nên phụ thuộc Repository

Sai:

```python
class StoryParser:

    def parse(self, html):

        story = ...

        repository.save(story)

        return story
```

Parser chỉ:

```text
HTML
 ↓
Story
```

---

# 19. Parser không nên xử lý retry

Sai:

```python
class Parser:

    def parse(self, html):

        try:
            ...
        except:
            time.sleep(5)
            ...
```

Retry thuộc HTTP/client layer hoặc application infrastructure.

Parser không biết Internet.

---

# 20. HTTP Error

Ta không nên để:

```python
requests.exceptions.HTTPError
```

chạy xuyên toàn hệ thống.

Tạo abstraction exception:

```python
class HttpError(Exception):
    pass


class HttpTimeoutError(HttpError):
    pass


class HttpNotFoundError(HttpError):
    pass
```

Infrastructure chuyển exception.

Ví dụ:

```python
class RequestsHttpClient:

    def get(self, url):

        try:

            response = requests.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

            return response.text

        except requests.Timeout as exc:

            raise HttpTimeoutError(
                url
            ) from exc
```

---

# 21. Tại sao translate exception?

Nếu Application phải viết:

```python
except requests.Timeout:
```

thì:

```text
Application
    ↓
requests
```

Dependency bị kéo vào trong.

Sai dependency direction.

Ta muốn:

```text
Application
    ↓
HttpError
    ↑
RequestsHttpClient
```

---

# 22. Parser Error

Tương tự:

```python
class ParserError(Exception):
    pass


class StoryNotFoundError(ParserError):
    pass


class InvalidStoryPageError(ParserError):
    pass
```

Parser:

```python
if title_element is None:

    raise StoryNotFoundError(
        "Cannot find story title"
    )
```

Application không cần biết BeautifulSoup.

---

# 23. Crawler Error Boundary

Crawler có thể chuyển:

```text
HttpError
ParserError
```

thành:

```python
CrawlerError
```

Ví dụ:

```python
class CrawlerError(Exception):
    pass
```

và:

```python
def crawl(self, url):

    try:

        html = self.http.get(
            url.value
        )

        return self.parser.parse(
            html,
            url,
        )

    except (HttpError, ParserError) as exc:

        raise CrawlerError(
            f"Failed to crawl {url.value}"
        ) from exc
```

---

# 24. Nhưng có nên bắt mọi Exception?

**Không.**

Đừng:

```python
except Exception:
    raise CrawlerError(...)
```

một cách mù quáng.

Vì:

```text
Programming bug
```

khác:

```text
Expected infrastructure failure
```

Ví dụ:

```python
AttributeError
```

có thể là bug trong code parser.

Không nên che nó thành:

```text
CrawlerError
```

---

# 25. Một lỗi kiến trúc phổ biến

```python
class SourceACrawler:

    def crawl(self, url):

        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = ...

        sqlite3.connect(...)

        print(...)

        return ...
```

Một class đang làm:

```text
HTTP
Parsing
Domain creation
Persistence
Presentation
```

Đây là:

> **God Object**

---

# 26. Sau refactor

```text
SourceACrawler
     │
     ├── HttpClient
     │
     └── StoryParser

CrawlStory
     │
     └── StoryRepository
```

Database nằm ngoài:

```text
SQLiteRepository
```

CLI nằm ngoài:

```text
CLI
```

---

# 27. Dependency Injection hoàn chỉnh

Composition Root:

```python
http = RequestsHttpClient()

parser = SourceAStoryParser()

source_a = SourceACrawler(
    http_client=http,
    parser=parser,
)

registry = CrawlerRegistry()

registry.register(source_a)
```

Sau đó:

```python
use_case = CrawlStory(
    registry=registry,
    repository=repository,
)
```

---

# 28. Một điểm rất quan trọng: cùng HttpClient

Không nhất thiết mỗi plugin tạo một `RequestsHttpClient`.

Có thể:

```text
Composition Root
       │
       ▼
 RequestsHttpClient
       │
 ┌─────┼─────┐
 ↓     ↓     ↓
 A     B     C
```

Điều này cho phép centralize:

```text
timeout
headers
cookies
proxy
retry
rate limit
logging
session
```

---

# 29. Nhưng đừng tạo `UniversalCrawlerClient`

Một sai lầm khác:

```python
class UniversalCrawlerClient:
    def download(...)
    def parse(...)
    def save(...)
    def notify(...)
    def login(...)
```

Đây là **Fat Interface**.

Chúng ta đang học ISP.

Tốt hơn:

```text
HttpClient
Parser
Repository
Notifier
Authenticator
```

---

# 30. HTTP Client nâng cao

Sau này có thể:

```python
class HttpClient(Protocol):

    def get(
        self,
        url: str,
        *,
        timeout: float = 10,
    ) -> str:
        ...
```

Implementation:

```text
RequestsHttpClient
HttpxClient
AsyncHttpClient
CachedHttpClient
RetryHttpClient
```

Application không cần sửa.

---

# 31. OCP xuất hiện lần nữa

Hiện tại:

```text
HttpClient
   ↑
RequestsHttpClient
```

Sau này:

```text
HttpClient
   ↑
 ┌─┴────────────┐
 ↓              ↓
Requests      Httpx
```

Crawler không đổi.

Tương tự:

```text
StoryParser
   ↑
 ┌─┴──────────────┐
 ↓                ↓
SourceAParser   SourceBParser
```

---

# 32. Plugin hoàn chỉnh

Sau Buổi 23:

```text
Source A Plugin
│
├── crawler.py
├── parser.py
└── metadata.py
```

Crawler:

```text
      SourceACrawler
            │
       ┌────┴────┐
       ↓         ↓
 HttpClient   Parser
       ↓         ↓
   HTTP       HTML
```

---

# 33. Code architecture hiện tại

```text
src/story_crawler/

domain/
├── story.py
├── chapter.py
├── crawler.py
└── repository.py

application/
├── crawl_story.py
└── crawler_registry.py

infrastructure/
├── http/
│   └── requests_client.py
│
├── crawler/
│   └── source_a/
│       ├── crawler.py
│       └── parser.py
│
└── persistence/
    └── sqlite_repository.py

presentation/
└── cli.py

composition.py
```

Đây là cấu trúc rất tốt cho project hiện tại.

---

# 34. Bài tập Buổi 23

## Bài 1 — HttpClient

Tạo:

```text
infrastructure/http/
├── client.py
└── requests_client.py
```

`client.py`:

```python
class HttpClient(Protocol):
    def get(self, url: str) -> str:
        ...
```

---

## Bài 2 — Parser

Tạo:

```text
source_a/
├── crawler.py
└── parser.py
```

Parser phải lấy:

```html
<h1 class="story-title">
    My Story
</h1>
```

và tạo:

```python
Story(...)
```

---

## Bài 3 — Fake HTTP

Tạo:

```python
class FakeHttpClient:
    ...
```

Không sử dụng Internet.

---

## Bài 4 — Test Parser

Test:

```text
HTML
 ↓
Parser
 ↓
Story
```

---

## Bài 5 — Test Crawler

Test:

```text
FakeHttp
 ↓
Crawler
 ↓
Parser
 ↓
Story
```

Không SQLite.

Không Internet.

---

# 35. Challenge quan trọng

Hãy tạo:

```python
class FakeHttpClient:
    def get(self, url):
        return """
        <h1 class="story-title">
            Test Story
        </h1>
        """
```

Sau đó chạy:

```text
CrawlStory
    ↓
CrawlerRegistry
    ↓
SourceACrawler
    ↓
FakeHttpClient
    ↓
SourceAParser
    ↓
Story
    ↓
FakeRepository
```

Toàn bộ flow phải chạy được **không có Internet và không có SQLite**.

Nếu làm được, bạn đã chứng minh được:

```text
DIP
+
Dependency Injection
+
SRP
+
ISP
+
OCP
+
Testability
```

đang thực sự hoạt động.

---

# 36. Điều cần nhớ hôm nay

Đừng nghĩ:

> "Tôi dùng `Protocol` nên tôi đã áp dụng DIP."

Không.

DIP thực sự nằm ở **dependency direction**:

```text
        Application
             ↓
         abstraction
             ↑
       Infrastructure
```

Và Plugin Architecture thực sự tốt khi:

```text
Thêm plugin
     ↓
Không sửa Use Case
     ↓
Không sửa Domain
     ↓
Không sửa Repository
```

Đó mới là **OCP + DIP trong thực tế**.

---

## Tiếp theo — Buổi 24

Chúng ta sẽ xây **SQLite Repository thật**, nhưng lần này không chỉ `INSERT`/`SELECT`.

Ta sẽ thiết kế:

```text
StoryRepository
       ↑
SQLiteStoryRepository
       │
       ├── save()
       ├── get_by_url()
       ├── update()
       ├── exists()
       └── transaction
```

và quan trọng hơn:

```text
Domain Entity
      ↕
Repository
      ↕
SQLite Row
```

để hiểu sâu **Repository Pattern + DIP + Unit of Work + Domain/Database mapping**.
