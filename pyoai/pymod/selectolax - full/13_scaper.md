# 📘 Selectolax — Buổi 13: Thiết kế Scraper

Đây là buổi **rất quan trọng**. Từ buổi này, chúng ta không còn học Selectolax như một thư viện đơn lẻ nữa, mà bắt đầu thiết kế một **scraping system có kiến trúc**.

Mục tiêu:

```text
HTTP
 ↓
Parser
 ↓
Extractor
 ↓
Model
 ↓
Repository
```

và quan trọng nhất:

> **Mỗi component chỉ có một trách nhiệm.**

---

# 1. Vấn đề của scraper nhỏ

Ban đầu chúng ta thường viết:

```python
import httpx
from selectolax.parser import HTMLParser


def scrape(url):
    response = httpx.get(url)

    tree = HTMLParser(response.text)

    title = tree.css_first("h1")
    content = tree.css_first(".content")

    return {
        "title": title.text(strip=True),
        "content": content.text(strip=True),
    }
```

Nhìn rất ổn.

Nhưng sau đó bắt đầu thêm:

```text
download
retry
headers
parse
extract
validate
save SQLite
logging
pagination
error handling
```

và cuối cùng:

```python
def scrape(url):
    ...
    300 dòng code
```

Đây là lúc cần architecture.

---

# 2. Kiến trúc chúng ta muốn

```text
                    Scraper
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       Parser       Extractor    Repository
          │            │            │
          ▼            ▼            ▼
      Selectolax     Article      SQLite
```

Chi tiết hơn:

```text
URL
 │
 ▼
HTTP Client
 │
 ▼
HTML
 │
 ▼
Parser
 │
 ▼
DOM
 │
 ▼
Extractor
 │
 ▼
Article
 │
 ▼
Repository
 │
 ▼
SQLite
```

---

# 3. Sáu thành phần

Trong scraper thực tế, chúng ta có thể chia:

```text
1. HTTP Client
2. Parser
3. Extractor
4. Model
5. Repository
6. Application Service
```

Hôm nay tập trung vào:

```text
Parser
Extractor
Model
Repository
Separation of Concerns
```

---

# 4. Parser là gì?

Parser chịu trách nhiệm:

```text
HTML string
     ↓
DOM
```

Ví dụ:

```python
from selectolax.parser import HTMLParser


class HTMLDocumentParser:

    def parse(self, html: str) -> HTMLParser:
        return HTMLParser(html)
```

Parser **không nên biết Article là gì**.

Nó chỉ biết:

```text
HTML → DOM
```

---

# 5. Parser không nên extract title

Không nên:

```python
class HTMLDocumentParser:

    def parse(self, html):

        tree = HTMLParser(html)

        title = tree.css_first("h1")

        return {
            "title": title.text()
        }
```

Tại sao?

Parser đang làm hai việc:

```text
HTML parsing
+
Article extraction
```

Vi phạm separation of concerns.

---

# 6. Extractor là gì?

Extractor chịu trách nhiệm:

```text
DOM
 ↓
Domain data
```

Ví dụ:

```python
class ArticleExtractor:

    def extract(self, tree):
        ...
```

Nó biết:

```text
h1 → title
.author → author
.content → content
```

Nhưng không cần biết:

```text
HTML được download bằng HTTPX hay file?
```

---

# 7. Model là gì?

Model đại diện cho dữ liệu mà application quan tâm.

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    author: str | None = None
```

Model không cần biết:

```text
Selectolax
HTTPX
CSS selector
SQLite
```

Đây là điểm cực kỳ quan trọng.

---

# 8. Repository là gì?

Repository chịu trách nhiệm:

```text
Article
 ↓
Database
```

Ví dụ:

```python
class ArticleRepository:

    def save(self, article: Article):
        ...
```

Nó có thể lưu:

```text
SQLite
PostgreSQL
MariaDB
MongoDB
```

Extractor không cần biết.

---

# 9. Separation of Concerns

Ta có:

```text
Parser
→ parse HTML

Extractor
→ extract Article

Model
→ represent Article

Repository
→ persist Article
```

Mỗi component có một concern.

---

# 10. Pipeline hoàn chỉnh

```text
                   URL
                    │
                    ▼
                HTTPX
                    │
                    ▼
                  HTML
                    │
                    ▼
                 Parser
                    │
                    ▼
                   DOM
                    │
                    ▼
                Extractor
                    │
                    ▼
                 Article
                    │
                    ▼
               Repository
                    │
                    ▼
                 SQLite
```

Đây là kiến trúc chúng ta sẽ tiếp tục mở rộng ở các buổi sau.

---

# 11. Bắt đầu từ Model

Tạo:

```text
scraper/
├── models/
│   └── article.py
```

`article.py`:

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    author: str | None = None
```

---

# 12. Parser

```text
scraper/
├── parsers/
│   └── html.py
```

```python
from selectolax.parser import HTMLParser


class HTMLParserService:

    def parse(self, html: str) -> HTMLParser:

        if not html:
            raise ValueError(
                "HTML cannot be empty"
            )

        return HTMLParser(html)
```

---

# 13. Đặt tên

Có một vấn đề:

```python
from selectolax.parser import HTMLParser
```

và:

```python
class HTMLParser:
```

trùng tên.

Không nên.

Tốt hơn:

```python
class HTMLDocumentParser:
```

hoặc:

```python
class SelectolaxParser:
```

Ví dụ:

```python
from selectolax.parser import HTMLParser


class SelectolaxParser:

    def parse(self, html: str):
        return HTMLParser(html)
```

---

# 14. Extractor

```text
scraper/
├── extractors/
│   └── article.py
```

```python
from selectolax.parser import HTMLParser

from scraper.models.article import Article


class ArticleExtractor:

    def extract(
        self,
        tree: HTMLParser,
    ) -> Article:

        title_node = tree.css_first(
            "h1"
        )

        content_node = tree.css_first(
            ".content"
        )

        title = (
            title_node.text(strip=True)
            if title_node
            else None
        )

        content = (
            content_node.text(strip=True)
            if content_node
            else None
        )

        if not title:
            raise ValueError(
                "Missing title"
            )

        if not content:
            raise ValueError(
                "Missing content"
            )

        return Article(
            title=title,
            content=content,
        )
```

---

# 15. Lưu ý: Extractor không download

Không viết:

```python
class ArticleExtractor:

    def extract(self, url):

        response = httpx.get(url)

        tree = HTMLParser(
            response.text
        )

        ...
```

Bởi vì Extractor lúc này phụ thuộc vào:

```text
HTTPX
+
Selectolax
+
Article
```

Quá nhiều responsibility.

---

# 16. Extractor chỉ nhận DOM

Đúng:

```python
article = extractor.extract(
    tree
)
```

Nó không cần biết:

```text
tree đến từ đâu
```

Có thể là:

```text
HTTP response
file HTML
database
test fixture
```

Đây chính là khả năng test rất mạnh.

---

# 17. Repository

```text
scraper/
└── repositories/
    └── article.py
```

Ví dụ interface:

```python
from abc import ABC, abstractmethod

from scraper.models.article import Article


class ArticleRepository(ABC):

    @abstractmethod
    def save(
        self,
        article: Article,
    ) -> None:
        ...
```

---

# 18. Tại sao interface?

Ta có:

```text
ArticleExtractor
       │
       ▼
    Article
       │
       ▼
ArticleRepository
```

Extractor/application không cần biết database cụ thể.

Sau này:

```text
ArticleRepository
       │
       ├── SQLiteArticleRepository
       ├── PostgreSQLArticleRepository
       └── MemoryArticleRepository
```

---

# 19. SQLite implementation

```python
import sqlite3

from scraper.models.article import Article


class SQLiteArticleRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(
        self,
        article: Article,
    ) -> None:

        self.connection.execute(
            """
            INSERT INTO articles
            (title, content, author)
            VALUES (?, ?, ?)
            """,
            (
                article.title,
                article.content,
                article.author,
            ),
        )

        self.connection.commit()
```

Repository biết SQLite.

Nhưng:

```text
Extractor
```

không biết SQLite.

---

# 20. Memory Repository

Đây là thứ rất hữu ích cho testing.

```python
class InMemoryArticleRepository:

    def __init__(self):
        self.articles = []

    def save(
        self,
        article: Article,
    ) -> None:
        self.articles.append(article)
```

Bây giờ:

```text
Production
→ SQLiteRepository

Test
→ InMemoryRepository
```

Không cần database thật.

---

# 21. Application Service

Bây giờ cần một component orchestration.

```text
HTTP
 ↓
Parser
 ↓
Extractor
 ↓
Repository
```

Đây không phải trách nhiệm của Parser.

Không phải Extractor.

Không phải Repository.

Ta tạo:

```text
ScrapeArticleUseCase
```

---

# 22. Use Case

```python
class ScrapeArticleUseCase:

    def __init__(
        self,
        parser,
        extractor,
        repository,
    ):
        self.parser = parser
        self.extractor = extractor
        self.repository = repository
```

Method:

```python
def execute(self, html: str):

    tree = self.parser.parse(html)

    article = self.extractor.extract(
        tree
    )

    self.repository.save(
        article
    )

    return article
```

Pipeline:

```text
HTML
 ↓
Parser
 ↓
DOM
 ↓
Extractor
 ↓
Article
 ↓
Repository
```

---

# 23. Đây chính là Orchestration

Use case không làm parsing.

Nó chỉ điều phối:

```text
Parser
Extractor
Repository
```

Đây là:

> **Orchestration**

---

# 24. Toàn bộ hệ thống

```text
                 ScrapeArticleUseCase
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
        Parser       Extractor      Repository
           │             │             │
       Selectolax      Article        SQLite
```

Đây là separation of concerns rất rõ.

---

# 25. Thêm HTTP

HTTP cũng nên tách riêng.

```text
scraper/
├── clients/
│   └── http.py
```

```python
import httpx


class HTTPClient:

    def __init__(
        self,
        client: httpx.Client,
    ):
        self.client = client

    def get(self, url: str) -> str:

        response = self.client.get(url)

        response.raise_for_status()

        return response.text
```

---

# 26. Bây giờ Use Case nhận URL

```python
class ScrapeArticleUseCase:

    def __init__(
        self,
        http_client,
        parser,
        extractor,
        repository,
    ):
        self.http_client = http_client
        self.parser = parser
        self.extractor = extractor
        self.repository = repository
```

Execute:

```python
def execute(self, url):

    html = self.http_client.get(url)

    tree = self.parser.parse(html)

    article = self.extractor.extract(
        tree
    )

    self.repository.save(article)

    return article
```

---

# 27. Architecture hoàn chỉnh

```text
                        URL
                         │
                         ▼
                    HTTPClient
                         │
                         ▼
                        HTML
                         │
                         ▼
                  SelectolaxParser
                         │
                         ▼
                        DOM
                         │
                         ▼
                  ArticleExtractor
                         │
                         ▼
                      Article
                         │
                         ▼
                ArticleRepository
                         │
                         ▼
                       SQLite
```

---

# 28. Đây là điều chúng ta muốn tránh

Một file:

```text
scraper.py
```

chứa:

```text
HTTP
retry
headers
parser
selectors
cleaning
validation
database
logging
pagination
```

```text
1000 lines
```

Khó:

```text
test
debug
maintain
change
reuse
```

---

# 29. Architecture tốt hơn

```text
scraper/
│
├── clients/
│   └── http.py
│
├── parsers/
│   └── selectolax.py
│
├── extractors/
│   └── article.py
│
├── models/
│   └── article.py
│
├── repositories/
│   ├── base.py
│   └── sqlite.py
│
└── services/
    └── scrape_article.py
```

Đây là một cấu trúc rất tốt để bắt đầu.

---

# 30. Dependency Direction

Hãy nhìn hướng dependency:

```text
Service
  │
  ├── Parser
  ├── Extractor
  └── Repository
```

Repository:

```text
SQLite
```

là implementation detail.

Ta muốn:

```text
Domain/Application
        ↓
Interface
        ↓
Infrastructure
```

Thay vì:

```text
Article
 ↓
SQLite
 ↓
Selectolax
```

---

# 31. Tại sao điều này quan trọng?

Hôm nay:

```text
SQLite
```

Ngày mai:

```text
PostgreSQL
```

Nếu Use Case viết:

```python
sqlite3.connect(...)
```

thì phải sửa Use Case.

Nếu dùng Repository:

```python
repository.save(article)
```

thì Use Case không cần thay đổi.

---

# 32. Thay database

Production:

```python
repository = SQLiteArticleRepository(
    connection
)
```

Testing:

```python
repository = InMemoryArticleRepository()
```

Use Case vẫn:

```python
use_case = ScrapeArticleUseCase(
    http_client=http_client,
    parser=parser,
    extractor=extractor,
    repository=repository,
)
```

---

# 33. Thay HTTP

Production:

```python
HTTPClient(httpx_client)
```

Testing:

```python
FakeHTTPClient()
```

Ví dụ:

```python
class FakeHTTPClient:

    def __init__(self, html):
        self.html = html

    def get(self, url):
        return self.html
```

Test không cần internet.

---

# 34. Đây là Dependency Injection

Ta không viết:

```python
class Scraper:

    def __init__(self):

        self.client = httpx.Client()

        self.parser = SelectolaxParser()

        self.extractor = ArticleExtractor()

        self.repository = SQLiteRepository()
```

Vì class tự tạo tất cả dependency.

Thay vào đó:

```python
class ScrapeArticleUseCase:

    def __init__(
        self,
        http_client,
        parser,
        extractor,
        repository,
    ):
        ...
```

Dependency được **inject từ bên ngoài**.

---

# 35. Đây chính là nền tảng SOLID

Bạn đã học SOLID, nên có thể nhìn architecture này dưới góc đó.

### SRP

```text
Parser
→ parse

Extractor
→ extract

Repository
→ persist
```

### DIP

Use Case phụ thuộc abstraction:

```text
Repository
```

thay vì:

```text
sqlite3
```

### OCP

Có thể thêm:

```text
PostgreSQLRepository
```

mà không sửa Use Case.

---

# 36. Scraper theo Site

Đây là vấn đề lớn hơn.

Giả sử chúng ta scrape:

```text
site-a.com
site-b.com
site-c.com
```

Selectors khác nhau.

Không nên:

```python
if site == "a":
    ...

elif site == "b":
    ...

elif site == "c":
    ...
```

100 site:

```text
100 if/elif
```

sẽ thành nightmare.

---

# 37. Tách Site Extractor

```text
extractors/
├── base.py
├── site_a.py
├── site_b.py
└── site_c.py
```

Ví dụ:

```python
class SiteAArticleExtractor:

    def extract(self, tree):
        ...
```

Site B:

```python
class SiteBArticleExtractor:

    def extract(self, tree):
        ...
```

Cùng trả:

```python
Article
```

---

# 38. Đây là abstraction rất mạnh

```text
Site A HTML
    ↓
SiteAExtractor
    ↓
Article
```

```text
Site B HTML
    ↓
SiteBExtractor
    ↓
Article
```

Application layer không quan tâm site cụ thể.

---

# 39. Extractor Interface

```python
from abc import ABC, abstractmethod


class ArticleExtractor(ABC):

    @abstractmethod
    def extract(self, tree):
        ...
```

Sau đó:

```python
class SiteAExtractor(
    ArticleExtractor
):
    ...
```

---

# 40. Một hệ thống scraper lớn

```text
                         Scraper App
                              │
                         Use Case
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
          HTTP Client                    Repository
               │                             │
               ▼                             ▼
             HTML                          SQLite
               │
               ▼
             Parser
               │
               ▼
              DOM
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
     SiteA   SiteB    SiteC
   Extractor Extractor Extractor
       │       │        │
       └───────┼────────┘
               ▼
             Article
```

Đây là architecture có khả năng mở rộng.

---

# 41. Đừng tạo abstraction quá sớm

Tuy nhiên, có một nguyên tắc:

> **Không phải cái gì cũng cần interface.**

Nếu project chỉ có:

```text
1 website
1 extractor
1 SQLite
```

thì:

```python
class ArticleRepository(ABC):
```

có thể hơi nhiều.

Bạn có thể bắt đầu:

```text
Parser
Extractor
Repository
```

bằng class bình thường.

Khi cần thay implementation hoặc test phức tạp → thêm abstraction.

---

# 42. Một architecture thực dụng

Với project hiện tại của bạn, tôi khuyên:

```text
scraper/
│
├── model.py
├── parser.py
├── extractor.py
├── repository.py
└── service.py
```

Đừng ngay lập tức tạo:

```text
20 folders
30 interfaces
15 factories
```

Architecture tốt không phải architecture nhiều class nhất.

---

# 43. Version đầu tiên

### `model.py`

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    author: str | None = None
```

### `parser.py`

```python
from selectolax.parser import HTMLParser


def parse(html: str) -> HTMLParser:
    return HTMLParser(html)
```

### `extractor.py`

```python
from .model import Article


def extract_article(tree) -> Article:

    title_node = tree.css_first("h1")
    content_node = tree.css_first(".content")

    if not title_node:
        raise ValueError("Missing title")

    if not content_node:
        raise ValueError(
            "Missing content"
        )

    return Article(
        title=title_node.text(
            strip=True
        ),
        content=content_node.text(
            strip=True
        ),
    )
```

---

# 44. Repository

```python
class ArticleRepository:

    def save(
        self,
        article: Article,
    ):
        raise NotImplementedError
```

Sau đó SQLite:

```python
class SQLiteArticleRepository(
    ArticleRepository
):

    def save(self, article):
        ...
```

---

# 45. Service

```python
class ArticleScraper:

    def __init__(
        self,
        parser,
        extractor,
        repository,
    ):
        self.parser = parser
        self.extractor = extractor
        self.repository = repository

    def process(self, html):

        tree = self.parser.parse(html)

        article = self.extractor.extract(
            tree
        )

        self.repository.save(article)

        return article
```

Rất dễ đọc:

```text
parse
 ↓
extract
 ↓
save
```

---

# 46. Một điều đặc biệt quan trọng

**Không để Repository nhận DOM.**

Sai:

```python
repository.save(tree)
```

Repository phải nhận:

```python
repository.save(article)
```

Bởi vì:

```text
DOM
→ presentation/source representation

Article
→ application/domain representation
```

---

# 47. Không để Extractor nhận Model ORM

Nếu dùng SQLAlchemy sau này, đừng:

```python
extractor.extract()
→ SQLAlchemyArticle
```

Tốt hơn:

```text
Selectolax
 ↓
Article
 ↓
Repository
 ↓
ORM / SQL
```

Như vậy domain model không phụ thuộc database.

---

# 48. Separation of Concerns nhìn bằng dữ liệu

```text
HTML
 │
 │ Parser
 ▼
DOM
 │
 │ Extractor
 ▼
Article
 │
 │ Repository
 ▼
Database Row
```

Mỗi bước chuyển đổi một representation.

Đây là một cách rất tốt để thiết kế scraper.

---

# 49. Bài tập chính

Hãy tạo project:

```text
selectolax_scraper/
│
├── app/
│   ├── model.py
│   ├── parser.py
│   ├── extractor.py
│   ├── repository.py
│   └── service.py
│
└── main.py
```

HTML:

```html
<article>
    <h1>Python Selectolax</h1>

    <div class="author">
        Garden
    </div>

    <div class="content">
        <p>Selectolax is fast.</p>
        <p>It is useful for scraping.</p>
    </div>
</article>
```

Kết quả:

```python
Article(
    title="Python Selectolax",
    content=(
        "Selectolax is fast.\n"
        "It is useful for scraping."
    ),
    author="Garden",
)
```

---

# 50. Bài tập nâng cao

Tạo:

```text
FakeHTTPClient
InMemoryArticleRepository
```

Sau đó pipeline hoàn toàn không cần:

```text
Internet
SQLite
```

nhưng vẫn chạy:

```text
FakeHTTP
 ↓
Parser
 ↓
Extractor
 ↓
Article
 ↓
MemoryRepository
```

Nếu làm được bài này, bạn đã bắt đầu hiểu **Dependency Injection + Separation of Concerns** chứ không chỉ Selectolax.

---

# 51. Bài tập cuối — Site A / Site B

Tạo:

```text
extractors/
├── base.py
├── site_a.py
└── site_b.py
```

Site A:

```html
<h1 class="article-title">
    Python
</h1>

<div class="article-body">
    Hello
</div>
```

Site B:

```html
<h1 class="post-title">
    Python
</h1>

<div class="post-content">
    Hello
</div>
```

Hai extractor:

```text
SiteAExtractor
SiteBExtractor
```

nhưng đều trả:

```python
Article(
    title="Python",
    content="Hello",
)
```

Đây chính là bước chuẩn bị cho **plugin architecture / multi-site scraper** sau này.

---

# 🧠 Tổng kết Buổi 13

Kiến trúc quan trọng nhất hôm nay:

```text
                HTML
                  │
                  ▼
               Parser
                  │
                  ▼
                 DOM
                  │
                  ▼
              Extractor
                  │
                  ▼
               Article
                  │
                  ▼
             Repository
                  │
                  ▼
               SQLite
```

Và:

```text
Parser
→ "HTML này có cấu trúc DOM gì?"

Extractor
→ "Dữ liệu Article nằm ở đâu?"

Model
→ "Article của application gồm những gì?"

Repository
→ "Lưu Article ở đâu?"

Service / Use Case
→ "Các bước này được phối hợp như thế nào?"
```

Điểm quan trọng nhất:

> **Selectolax chỉ nên xuất hiện ở tầng parsing/extraction. Đừng để toàn bộ application phụ thuộc trực tiếp vào DOM.**

---

## 🔜 Buổi 14 — Testing Selectolax

Chúng ta sẽ lấy chính architecture hôm nay để viết test:

```text
tests/
│
├── fixtures/
│   ├── article.html
│   ├── missing_title.html
│   └── changed_layout.html
│
├── test_parser.py
├── test_selector.py
└── test_extractor.py
```

Học:

* HTML fixture
* Test Selectolax parser
* Test CSS selector
* Test extractor
* Test missing data
* Test fallback selector
* Regression test khi website đổi HTML
* **Không cần internet để test scraper**

Đây sẽ là bước rất quan trọng để biến scraper từ một script thành một **project có thể bảo trì lâu dài**.
