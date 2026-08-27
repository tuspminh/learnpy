# 📘 Selectolax — Buổi 15: Mini Crawler

Hôm nay chúng ta bắt đầu **Phần IV — Project thực tế**.

Mục tiêu không còn là:

```text
học API Selectolax
```

mà là xây được crawler đầu tiên:

```text
URL
 ↓
HTTPX
 ↓
Fetcher
 ↓
Selectolax
 ↓
Parser
 ↓
Model
 ↓
SQLite
```

Đây chính là phiên bản thu nhỏ của crawler framework mà chúng ta sẽ hoàn thiện ở **Buổi 20**.

---

# 1. Kiến trúc Mini Crawler

Hôm nay chúng ta cố tình giữ architecture đơn giản:

```text
                    Crawler
                       │
                       ▼
                    Fetcher
                       │
                       ▼
                      HTML
                       │
                       ▼
                   Selectolax
                       │
                       ▼
                    Parser
                       │
                       ▼
                     Model
                       │
                       ▼
                  Repository
                       │
                       ▼
                    SQLite
```

Trong đó:

| Component    | Trách nhiệm      |
| ------------ | ---------------- |
| `Fetcher`    | Download HTML    |
| `Parser`     | Parse HTML       |
| `Model`      | Đại diện dữ liệu |
| `Repository` | Lưu dữ liệu      |
| `Crawler`    | Điều phối        |

---

# 2. Project structure

Tạo project:

```text
mini_crawler/
│
├── app/
│   ├── __init__.py
│   │
│   ├── fetcher.py
│   ├── parser.py
│   ├── models.py
│   ├── repository.py
│   └── crawler.py
│
├── tests/
│
├── main.py
│
└── crawler.db
```

Chưa cần tạo quá nhiều layer.

Mục tiêu hôm nay là hiểu **pipeline**.

---

# 3. Cài thư viện

```bash
pip install httpx selectolax
```

SQLite đã có sẵn trong Python:

```python
import sqlite3
```

---

# 4. Fetcher

Fetcher chịu trách nhiệm duy nhất:

```text
URL
 ↓
HTML
```

Tạo `app/fetcher.py`:

```python
import httpx


class Fetcher:

    def __init__(
        self,
        client: httpx.Client,
    ):
        self.client = client

    def fetch(self, url: str) -> str:

        response = self.client.get(url)

        response.raise_for_status()

        return response.text
```

---

# 5. Tại sao không viết `httpx.get()` trực tiếp?

Có thể viết:

```python
response = httpx.get(url)
```

nhưng crawler sẽ khó mở rộng.

Chúng ta muốn:

```text
Crawler
   ↓
Fetcher
   ↓
HTTPX
```

Sau này Fetcher có thể xử lý:

```text
timeout
headers
retry
rate limit
logging
proxy
status code
```

mà `Crawler` không cần quan tâm.

---

# 6. HTTPX Client

Trong `main.py`:

```python
import httpx

client = httpx.Client(
    timeout=10.0,
    headers={
        "User-Agent": (
            "MiniCrawler/1.0"
        )
    },
)
```

Sau đó:

```python
fetcher = Fetcher(client)
```

---

# 7. Parser

Tạo `app/parser.py`:

```python
from selectolax.parser import HTMLParser


class Parser:

    def parse(
        self,
        html: str,
    ) -> HTMLParser:

        if not html.strip():
            raise ValueError(
                "HTML is empty"
            )

        return HTMLParser(html)
```

Parser chỉ làm:

```text
HTML
 ↓
DOM
```

---

# 8. Parser không biết HTTPX

Đây là nguyên tắc quan trọng.

Parser không được biết:

```python
httpx.Client
```

Nó chỉ nhận:

```python
html: str
```

Ví dụ:

```python
parser.parse(html)
```

HTML có thể đến từ:

```text
HTTPX
file
fixture
database
cache
```

Parser không quan tâm.

---

# 9. Model

Hôm nay chúng ta crawl một bài viết đơn giản.

Tạo `app/models.py`:

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    url: str
```

Model:

```text
Article
├── title
├── content
└── url
```

---

# 10. Extract dữ liệu

Có hai cách thiết kế.

### Cách 1

Parser vừa parse vừa extract.

### Cách 2

Parser chỉ parse DOM, extractor extract data.

Vì chúng ta đã học architecture ở Buổi 13, tôi muốn dùng:

```text
Parser
 ↓
DOM
 ↓
Extractor
 ↓
Article
```

Vì vậy project thêm:

```text
app/
├── parser.py
├── extractor.py
└── models.py
```

---

# 11. Extractor

`app/extractor.py`:

```python
from selectolax.parser import HTMLParser

from .models import Article


class ArticleExtractor:

    def extract(
        self,
        tree: HTMLParser,
        url: str,
    ) -> Article:

        title_node = tree.css_first(
            "h1"
        )

        content_node = tree.css_first(
            ".content"
        )

        if title_node is None:
            raise ValueError(
                "Article title not found"
            )

        if content_node is None:
            raise ValueError(
                "Article content not found"
            )

        return Article(
            title=title_node.text(
                strip=True
            ),
            content=content_node.text(
                separator="\n",
                strip=True,
            ),
            url=url,
        )
```

---

# 12. Pipeline lúc này

```text
URL
 │
 ▼
Fetcher
 │
 ▼
HTML
 │
 ▼
Parser
 │
 ▼
HTMLParser
 │
 ▼
ArticleExtractor
 │
 ▼
Article
```

---

# 13. Repository

Bây giờ cần lưu Article.

Tạo:

```text
app/repository.py
```

```python
import sqlite3

from .models import Article


class ArticleRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

    def save(
        self,
        article: Article,
    ) -> None:

        self.connection.execute(
            """
            INSERT INTO articles (
                title,
                content,
                url
            )
            VALUES (?, ?, ?)
            """,
            (
                article.title,
                article.content,
                article.url,
            ),
        )

        self.connection.commit()
```

---

# 14. Tạo database

Chúng ta cần:

```sql
CREATE TABLE articles
```

Có thể tạo một method:

```python
def create_tables(
    connection: sqlite3.Connection,
) -> None:

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE
        )
        """
    )

    connection.commit()
```

---

# 15. Vì sao `url UNIQUE`?

Crawler có thể crawl cùng URL nhiều lần.

Ví dụ:

```text
crawl lần 1
↓
article A

crawl lần 2
↓
article A
```

Nếu không có `UNIQUE`:

```text
database
├── article A
├── article A
├── article A
└── article A
```

Rất dễ duplicate.

---

# 16. Repository chống duplicate

Thay:

```sql
INSERT INTO articles
```

bằng:

```sql
INSERT OR IGNORE INTO articles
```

Ví dụ:

```python
def save(
    self,
    article: Article,
) -> None:

    self.connection.execute(
        """
        INSERT OR IGNORE INTO articles (
            title,
            content,
            url
        )
        VALUES (?, ?, ?)
        """,
        (
            article.title,
            article.content,
            article.url,
        ),
    )

    self.connection.commit()
```

---

# 17. Crawler

Đây là phần quan trọng.

Tạo:

```text
app/crawler.py
```

```python
class Crawler:

    def __init__(
        self,
        fetcher,
        parser,
        extractor,
        repository,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.extractor = extractor
        self.repository = repository
```

---

# 18. `crawl()`

```python
class Crawler:

    def __init__(
        self,
        fetcher,
        parser,
        extractor,
        repository,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.extractor = extractor
        self.repository = repository

    def crawl(self, url: str):

        html = self.fetcher.fetch(url)

        tree = self.parser.parse(html)

        article = self.extractor.extract(
            tree,
            url,
        )

        self.repository.save(article)

        return article
```

Đây chính là:

```text
fetch
 ↓
parse
 ↓
extract
 ↓
save
```

---

# 19. Crawler không biết SQLite

Đây là điều rất quan trọng.

`Crawler` chỉ biết:

```python
repository.save(article)
```

Nó không biết:

```python
sqlite3.connect(...)
```

Điều này cho phép:

```text
Crawler
  │
  ├── SQLiteRepository
  ├── MemoryRepository
  └── PostgreSQLRepository
```

---

# 20. `main.py`

```python
import sqlite3
import httpx

from app.fetcher import Fetcher
from app.parser import Parser
from app.extractor import ArticleExtractor
from app.repository import (
    ArticleRepository,
)
from app.crawler import Crawler


def create_tables(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE
        )
        """
    )

    connection.commit()


def main():

    connection = sqlite3.connect(
        "crawler.db"
    )

    create_tables(connection)

    client = httpx.Client(
        timeout=10.0,
        headers={
            "User-Agent": "MiniCrawler/1.0"
        },
    )

    fetcher = Fetcher(client)

    parser = Parser()

    extractor = ArticleExtractor()

    repository = ArticleRepository(
        connection
    )

    crawler = Crawler(
        fetcher=fetcher,
        parser=parser,
        extractor=extractor,
        repository=repository,
    )

    article = crawler.crawl(
        "https://example.com/article"
    )

    print(article)


if __name__ == "__main__":
    main()
```

---

# 21. Dependency Graph

`main.py` đang làm một việc rất quan trọng:

```text
             main
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    Fetcher  Parser  Extractor
       │       │        │
       ▼       ▼        ▼
     HTTPX Selectolax Article
                         │
                         ▼
                    Repository
                         │
                         ▼
                       SQLite
```

`main` chính là **composition root**.

Nó tạo object và nối chúng lại.

---

# 22. Đây là Dependency Injection

Crawler:

```python
Crawler(
    fetcher,
    parser,
    extractor,
    repository,
)
```

không tự tạo dependency.

Ta inject:

```text
Fetcher
Parser
Extractor
Repository
```

vào.

Đây chính là Dependency Injection mà bạn đã học trong SOLID / Clean Architecture.

---

# 23. Tạo Fake Fetcher để test

Đây là lợi ích rất lớn.

```python
class FakeFetcher:

    def __init__(
        self,
        html: str,
    ):
        self.html = html

    def fetch(self, url: str) -> str:
        return self.html
```

Không cần internet.

---

# 24. Fake Repository

```python
class InMemoryRepository:

    def __init__(self):
        self.articles = []

    def save(self, article):
        self.articles.append(article)
```

Bây giờ:

```text
FakeFetcher
 ↓
Parser
 ↓
Extractor
 ↓
InMemoryRepository
```

Không có:

```text
Internet
SQLite
```

---

# 25. Test toàn bộ crawler

```python
def test_crawler():

    html = """
    <article>

        <h1>
            Python Selectolax
        </h1>

        <div class="content">
            Hello Selectolax
        </div>

    </article>
    """

    fetcher = FakeFetcher(html)

    parser = Parser()

    extractor = ArticleExtractor()

    repository = InMemoryRepository()

    crawler = Crawler(
        fetcher,
        parser,
        extractor,
        repository,
    )

    article = crawler.crawl(
        "https://example.com/article"
    )

    assert article.title == (
        "Python Selectolax"
    )

    assert article.content == (
        "Hello Selectolax"
    )

    assert len(
        repository.articles
    ) == 1
```

Đây là một **integration-style unit test** rất đẹp cho pipeline.

---

# 26. Một điểm kiến trúc cần sửa

Ở project thật, tôi khuyên không đặt:

```python
url
```

trong `ArticleExtractor`.

Extractor chỉ nên:

```text
DOM
 ↓
Article
```

Nhưng Article cần URL.

Có thể thiết kế:

```python
article = extractor.extract(
    tree
)

article.url = url
```

hoặc truyền metadata:

```python
extractor.extract(
    tree,
    url=url,
)
```

Đối với mini project hôm nay, cách thứ hai hoàn toàn ổn.

---

# 27. Content bằng `text()` có hạn chế

Ta đang:

```python
content_node.text(
    separator="\n",
    strip=True,
)
```

Kết quả:

```text
Paragraph 1
Paragraph 2
Paragraph 3
```

Nhưng chúng ta có thể mất:

```text
bold
links
code
headings
images
```

Đây chính là vấn đề chúng ta sẽ giải quyết sâu hơn khi xây **story/chapter crawler**.

---

# 28. Selectolax có thể giữ HTML

Thay vì:

```python
content_node.text()
```

ta có thể lấy:

```python
content_node.html
```

Ví dụ:

```html
<p>Hello</p>
<p><strong>Python</strong></p>
```

giữ nguyên:

```python
html = content_node.html
```

Điều này rất hữu ích nếu application sau này muốn:

```text
HTML
 ↓
clean HTML
 ↓
Markdown
```

Đúng với hướng crawler đọc truyện mà bạn đang xây dựng.

---

# 29. Hai loại Content

Chúng ta nên phân biệt:

### Plain text

```python
content: str
```

Ví dụ:

```text
Hello Python
```

### Raw HTML

```python
content_html: str
```

Ví dụ:

```html
<p>Hello <strong>Python</strong></p>
```

Trong production crawler, thường nên cân nhắc giữ **raw HTML trước**, sau đó mới xử lý thành text/Markdown.

---

# 30. Model tốt hơn

Có thể bắt đầu:

```python
@dataclass
class Article:
    title: str
    content: str
    url: str
```

Sau này:

```python
@dataclass
class Article:
    title: str
    content_html: str
    content_text: str
    url: str
    author: str | None
    published_at: str | None
```

Nhưng **đừng thêm tất cả ngay hôm nay**.

---

# 31. Crawler hiện tại là synchronous

Pipeline:

```text
crawl(url)
```

chạy:

```text
Fetch
 ↓
Parse
 ↓
Extract
 ↓
Save
```

theo tuần tự.

Ví dụ 100 URL:

```text
URL1
 ↓
wait
 ↓
URL2
 ↓
wait
 ↓
URL3
```

Đến Buổi 19 chúng ta sẽ chuyển sang:

```text
asyncio
+
httpx.AsyncClient
+
Selectolax
```

để crawl nhiều URL hiệu quả hơn.

---

# 32. Nhưng đừng async quá sớm

Một lỗi phổ biến:

```text
project mới
 ↓
asyncio
 ↓
10 task
 ↓
queue
 ↓
worker
 ↓
retry
 ↓
rate limiter
```

trong khi chưa hiểu pipeline cơ bản.

Hôm nay chúng ta cố tình:

```text
SYNC
```

để hiểu rõ:

```text
Fetch
Parse
Extract
Persist
```

Sau đó mới async hóa.

---

# 33. Thêm logging

Crawler thực tế cần biết:

```text
START https://...
FETCH
PARSE
EXTRACT
SAVE
DONE
```

Có thể thêm:

```python
import logging

logger = logging.getLogger(__name__)
```

Trong crawler:

```python
def crawl(self, url: str):

    logger.info(
        "Crawling %s",
        url,
    )

    html = self.fetcher.fetch(url)

    logger.debug(
        "Fetched %d bytes",
        len(html),
    )

    tree = self.parser.parse(html)

    article = self.extractor.extract(
        tree,
        url,
    )

    self.repository.save(article)

    logger.info(
        "Saved article: %s",
        article.title,
    )

    return article
```

---

# 34. Error boundary

Một crawler không nên crash toàn bộ chỉ vì một URL lỗi.

Ví dụ:

```python
urls = [
    "https://example.com/1",
    "https://example.com/2",
    "https://example.com/3",
]
```

Nếu URL 2 lỗi:

```text
URL1 ✓
URL2 ✗
URL3 ✓
```

chứ không phải:

```text
URL1 ✓
URL2 ✗
STOP
```

Sau này chúng ta sẽ xây:

```text
Crawler
 ↓
Error handling
 ↓
Retry
 ↓
Failed URL
 ↓
Logging
```

---

# 35. Mini batch crawler

Có thể bắt đầu rất đơn giản:

```python
urls = [
    "...",
    "...",
    "...",
]

for url in urls:

    try:
        crawler.crawl(url)

    except Exception:
        logger.exception(
            "Failed: %s",
            url,
        )
```

Đây là bước đầu tiên để từ:

```text
single URL
```

sang:

```text
multiple URLs
```

---

# 36. Nhưng hôm nay chưa làm pagination

Pagination sẽ thuộc:

```text
Buổi 17
```

Lúc đó:

```text
Page 1
 ↓
Chapter 1
Chapter 2
Chapter 3
 ↓
Page 2
 ↓
Chapter 4
Chapter 5
```

Chúng ta sẽ xây một engine riêng.

---

# 37. Tư duy quan trọng nhất hôm nay

Đừng nghĩ:

> "Tôi đang viết một script scrape."

Hãy nghĩ:

> "Tôi đang xây một pipeline xử lý dữ liệu."

```text
Input
 ↓
Fetcher
 ↓
Raw Data
 ↓
Parser
 ↓
Structured Data
 ↓
Model
 ↓
Persistence
```

Đây là tư duy giúp crawler phát triển từ script thành framework.

---

# 38. Architecture hiện tại

Sau Buổi 15:

```text
mini_crawler/
│
├── app/
│   │
│   ├── fetcher.py
│   │       │
│   │       └── HTTPX
│   │
│   ├── parser.py
│   │       │
│   │       └── Selectolax
│   │
│   ├── extractor.py
│   │
│   ├── models.py
│   │
│   ├── repository.py
│   │       │
│   │       └── SQLite
│   │
│   └── crawler.py
│
├── tests/
│
└── main.py
```

---

# 39. Luồng dữ liệu cuối cùng

```text
                URL
                 │
                 ▼
             Fetcher
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
             Selectolax
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

Đây là **xương sống** của toàn bộ Project thực tế.

---

# 🧪 Bài tập Buổi 15

## Bài 1 — Bắt buộc

Tạo:

```text
Fetcher
Parser
Extractor
Article
Repository
Crawler
```

và chạy pipeline:

```text
URL
 ↓
HTTPX
 ↓
Selectolax
 ↓
Article
 ↓
SQLite
```

---

## Bài 2 — Không dùng Internet

Tạo:

```python
FakeFetcher
```

với HTML:

```html
<article>
    <h1>Python Crawler</h1>

    <div class="content">
        <p>Learn Selectolax.</p>
        <p>Build crawler.</p>
    </div>
</article>
```

Chạy:

```text
FakeFetcher
 ↓
Parser
 ↓
Extractor
 ↓
InMemoryRepository
```

và kiểm tra:

```python
assert article.title == "Python Crawler"
```

---

## Bài 3 — Duplicate

Crawl cùng URL 2 lần:

```python
crawler.crawl(url)
crawler.crawl(url)
```

Database vẫn chỉ có:

```text
1 article
```

---

## Bài 4 — Error

HTML:

```html
<article>
    <div class="content">
        Hello
    </div>
</article>
```

Không có:

```html
<h1>
```

Crawler phải báo:

```text
Article title not found
```

nhưng application không được crash toàn bộ khi xử lý batch URL.

---

# 🎯 Bài tập quan trọng nhất

Tôi muốn bạn **tự viết lại toàn bộ project từ đầu**, không copy code ở trên.

Chỉ cần nhớ pipeline:

```text
Fetcher
   ↓
Parser
   ↓
Extractor
   ↓
Model
   ↓
Repository
```

Nếu bạn tự viết được pipeline này, thì sang **Buổi 16 — Crawl website truyện**, chúng ta sẽ thay:

```text
Article
```

bằng một domain thực tế hơn:

```text
Story
 │
 ├── title
 ├── author
 ├── category
 └── chapters
          │
          ├── Chapter 1
          ├── Chapter 2
          └── Chapter 3
```

và bắt đầu xây đúng kiểu **crawler truyện** mà sau này có thể kết hợp với SQLite, Repository Pattern, asyncio và worker queue.
