# 📘 Selectolax — Buổi 20: Final Project

Hôm nay chúng ta **ghép toàn bộ kiến thức của 19 buổi trước** thành một crawler framework có kiến trúc gần với project thực tế.

Mục tiêu không phải viết một script:

```python
requests.get(...)
BeautifulSoup(...)
sqlite3.connect(...)
```

mà xây một framework:

```text
                CLI
                 │
                 ▼
          Application Service
                 │
                 ▼
           Crawl Engine
                 │
        ┌────────┴────────┐
        ▼                 ▼
    AsyncFetcher      ParserRegistry
        │                 │
      HTTPX           Plugin Parser
                          │
                     ┌────┼────┐
                     ▼    ▼    ▼
                   SiteA SiteB SiteC
                     │
                     ▼
                  Selectolax
                     │
                     ▼
                Domain Model
                     │
                     ▼
                Repository
                     │
                     ▼
                   SQLite
```

---

# 1. Mục tiêu Final Project

Framework của chúng ta phải hỗ trợ:

* HTTP async bằng `httpx`
* HTML parsing bằng `selectolax`
* concurrency bằng `asyncio`
* pagination
* crawl nhiều chapter
* retry
* timeout
* plugin parser
* SQLite
* Repository Pattern
* logging
* CLI
* testable architecture

Và quan trọng:

> **Site-specific code không được trộn vào crawler core.**

---

# 2. Project structure

Đây là cấu trúc tôi đề xuất:

```text
story_crawler/
│
├── pyproject.toml
│
├── src/
│   └── crawler/
│       │
│       ├── domain/
│       │   ├── models.py
│       │   └── repositories.py
│       │
│       ├── application/
│       │   └── crawl_story.py
│       │
│       ├── infrastructure/
│       │   │
│       │   ├── http/
│       │   │   └── fetcher.py
│       │   │
│       │   ├── parser/
│       │   │   ├── base.py
│       │   │   ├── registry.py
│       │   │   ├── site_a.py
│       │   │   └── site_b.py
│       │   │
│       │   └── database/
│       │       └── sqlite.py
│       │
│       ├── cli/
│       │   └── main.py
│       │
│       └── main.py
│
└── tests/
    ├── fixtures/
    │   ├── site_a_story.html
    │   └── site_a_chapter.html
    │
    ├── test_parser.py
    ├── test_fetcher.py
    └── test_crawler.py
```

Đây chính là tinh thần:

```text
Domain
Application
Infrastructure
CLI
```

---

# 3. Domain Model

Bắt đầu từ dữ liệu.

## Story

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int | None
    title: str
    author: str | None
    url: str
```

## Chapter

```python
@dataclass
class Chapter:
    id: int | None
    story_id: int
    title: str
    url: str
    content: str
    number: int
```

Đây là **domain model**.

Nó không biết:

```text
HTTPX
Selectolax
SQLite
asyncio
```

---

# 4. Repository Interface

Trong:

```text
domain/repositories.py
```

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story: Story) -> int:
        ...


class ChapterRepository(ABC):

    @abstractmethod
    def save(self, chapter: Chapter) -> int:
        ...
```

Domain chỉ biết:

```text
Repository
```

không biết database cụ thể.

---

# 5. SQLite Repository

Infrastructure:

```text
infrastructure/database/sqlite.py
```

```python
import sqlite3


class SQLiteChapterRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(self, chapter):

        cursor = self.connection.execute(
            """
            INSERT INTO chapters
            (
                story_id,
                title,
                url,
                content,
                number
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chapter.story_id,
                chapter.title,
                chapter.url,
                chapter.content,
                chapter.number,
            ),
        )

        self.connection.commit()

        return cursor.lastrowid
```

Repository xử lý:

```text
Domain Model
      ↓
SQLite
```

---

# 6. Parser Interface

Đây là phần quan trọng nhất của plugin architecture.

```python
from abc import ABC, abstractmethod


class StoryParser(ABC):

    @abstractmethod
    def supports(self, url: str) -> bool:
        ...

    @abstractmethod
    def parse_story(self, tree, url):
        ...

    @abstractmethod
    def parse_chapter_links(self, tree):
        ...

    @abstractmethod
    def parse_next_page(self, tree):
        ...


class ChapterParser(ABC):

    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url,
        story_id,
    ):
        ...
```

---

# 7. Tại sao Parser nhận `tree`?

Không nên:

```python
parser.parse(url)
```

rồi parser tự:

```python
httpx.get(url)
```

Vì như vậy parser sẽ phụ thuộc network.

Tốt hơn:

```text
Fetcher
   ↓
HTML
   ↓
Selectolax
   ↓
Parser
```

Parser chỉ làm:

```text
HTML DOM → Model
```

---

# 8. Site A Parser

Ví dụ HTML:

```html
<article class="story">
    <h1 class="title">My Story</h1>

    <div class="author">
        John
    </div>
</article>
```

Parser:

```python
class SiteAParser(StoryParser):

    def supports(self, url: str) -> bool:
        return "site-a.com" in url

    def parse_story(self, tree, url):

        title_node = tree.css_first(
            "h1.title"
        )

        author_node = tree.css_first(
            ".author"
        )

        return Story(
            id=None,
            title=title_node.text(
                strip=True
            ),
            author=(
                author_node.text(
                    strip=True
                )
                if author_node
                else None
            ),
            url=url,
        )
```

---

# 9. Parse chapter

Ví dụ:

```html
<article class="chapter">
    <h1 class="chapter-title">
        Chapter 1
    </h1>

    <div class="chapter-content">
        <p>Hello world</p>
        <p>This is the story.</p>
    </div>
</article>
```

Parser:

```python
class SiteAChapterParser:

    def parse_chapter(
        self,
        tree,
        url,
        story_id,
        number,
    ):

        title = tree.css_first(
            "h1.chapter-title"
        )

        content = tree.css_first(
            ".chapter-content"
        )

        return Chapter(
            id=None,
            story_id=story_id,
            title=title.text(
                strip=True
            ),
            url=url,
            content=content.text(
                separator="\n",
                strip=True,
            ),
            number=number,
        )
```

---

# 10. Parser Registry

Ta không muốn:

```python
if "site-a.com":
    ...
elif "site-b.com":
    ...
elif "site-c.com":
    ...
```

trong crawler.

Thay vào đó:

```python
class ParserRegistry:

    def __init__(self, parsers):
        self.parsers = parsers

    def get(self, url):

        for parser in self.parsers:

            if parser.supports(url):
                return parser

        raise ValueError(
            f"No parser for {url}"
        )
```

---

# 11. Đăng ký plugin

```python
registry = ParserRegistry(
    [
        SiteAParser(),
        SiteBParser(),
        SiteCParser(),
    ]
)
```

Crawler không cần biết:

```text
SiteAParser
SiteBParser
SiteCParser
```

ngoài registry.

---

# 12. AsyncFetcher

```python
import httpx


class AsyncFetcher:

    def __init__(
        self,
        client,
        max_retries=3,
    ):
        self.client = client
        self.max_retries = max_retries

    async def fetch(self, url):

        for attempt in range(
            self.max_retries
        ):

            try:

                response = (
                    await self.client.get(url)
                )

                response.raise_for_status()

                return response.text

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
            ):

                if attempt == (
                    self.max_retries - 1
                ):
                    raise

                await asyncio.sleep(
                    2 ** attempt
                )
```

Retry:

```text
attempt 1
 ↓
1 second
 ↓
attempt 2
 ↓
2 seconds
 ↓
attempt 3
```

---

# 13. HTTP Client

Application entry point:

```python
async with httpx.AsyncClient(
    timeout=10.0,
    headers={
        "User-Agent": (
            "StoryCrawler/1.0"
        )
    },
) as client:

    fetcher = AsyncFetcher(
        client
    )
```

Một client được tái sử dụng.

---

# 14. HTML Parser

Ta có thể tách Selectolax thành component riêng:

```python
from selectolax.parser import HTMLParser


class HTMLDocumentParser:

    def parse(self, html: str):
        return HTMLParser(html)
```

Crawler không cần trực tiếp gọi:

```python
HTMLParser(...)
```

---

# 15. Chapter Crawler

Đây là component orchestration.

```python
class ChapterCrawler:

    def __init__(
        self,
        fetcher,
        html_parser,
        parser_registry,
        repository,
    ):
        self.fetcher = fetcher
        self.html_parser = html_parser
        self.registry = parser_registry
        self.repository = repository
```

---

# 16. Crawl một chapter

```python
async def crawl(
    self,
    chapter_url,
    story_id,
    number,
):

    html = await self.fetcher.fetch(
        chapter_url
    )

    tree = self.html_parser.parse(
        html
    )

    parser = self.registry.get(
        chapter_url
    )

    chapter = parser.parse_chapter(
        tree,
        chapter_url,
        story_id,
        number,
    )

    self.repository.save(
        chapter
    )

    return chapter
```

Đây chính là pipeline:

```text
URL
 ↓
HTTPX
 ↓
HTML
 ↓
Selectolax
 ↓
Parser
 ↓
Chapter
 ↓
Repository
 ↓
SQLite
```

---

# 17. Concurrency

Không crawl:

```python
for chapter in chapters:
    await crawler.crawl(...)
```

vì:

```text
Chapter 1
 ↓
wait
 ↓
Chapter 2
 ↓
wait
 ↓
Chapter 3
```

Thay vào đó:

```python
tasks = [
    crawler.crawl(
        chapter.url,
        story_id,
        chapter.number,
    )
    for chapter in chapters
]

results = await asyncio.gather(
    *tasks
)
```

---

# 18. Nhưng phải giới hạn concurrency

```python
class ChapterCrawler:

    def __init__(
        self,
        ...,
        concurrency=5,
    ):
        ...

        self.semaphore = (
            asyncio.Semaphore(
                concurrency
            )
        )
```

Sau đó:

```python
async def crawl(...):

    async with self.semaphore:

        html = await self.fetcher.fetch(
            chapter_url
        )

    ...
```

---

# 19. Pagination

Parser chịu trách nhiệm tìm:

```text
next page
```

Ví dụ:

```html
<a class="next"
   href="/story?page=2">
    Next
</a>
```

Parser:

```python
def parse_next_page(
    self,
    tree,
):

    node = tree.css_first(
        "a.next"
    )

    if node is None:
        return None

    return node.attributes.get(
        "href"
    )
```

Trong thực tế cần resolve URL tương đối bằng `urljoin()`.

---

# 20. Pagination crawler

```python
async def crawl_pages(
    self,
    start_url,
):

    url = start_url

    while url:

        html = await self.fetcher.fetch(
            url
        )

        tree = self.html_parser.parse(
            html
        )

        parser = self.registry.get(
            url
        )

        chapters = (
            parser.parse_chapter_links(
                tree
            )
        )

        for chapter in chapters:
            yield chapter

        url = parser.parse_next_page(
            tree
        )
```

---

# 21. Vì sao dùng `async generator`?

Thay vì đợi:

```text
Page 1
Page 2
Page 3
Page 4
...
```

mới trả kết quả.

Ta có thể:

```text
Page 1
 ↓
yield chapter
 ↓
yield chapter
 ↓
yield chapter

Page 2
 ↓
yield chapter
```

Consumer:

```python
async for chapter in crawler.crawl_pages(
    story_url
):
    print(chapter)
```

---

# 22. Worker Pool

Với 10.000 chapter:

```text
Không nên:

10,000 tasks
```

Ta dùng:

```text
                 Queue
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Worker 1   Worker 2   Worker 3
        │          │          │
        └──────────┼──────────┘
                   ▼
                HTTPX
```

---

# 23. Queue

```python
queue = asyncio.Queue(
    maxsize=100
)
```

`maxsize` giúp tạo **backpressure**.

Nếu crawler producer quá nhanh:

```text
Producer
   ↓
Queue full
   ↓
Producer waits
```

Không tiếp tục tạo vô hạn dữ liệu.

---

# 24. Producer

```python
async def producer(
    queue,
    paginator,
):

    async for chapter in paginator:

        await queue.put(
            chapter
        )

    for _ in range(worker_count):
        await queue.put(None)
```

`None` đóng vai trò sentinel.

---

# 25. Worker

```python
async def worker(
    queue,
    crawler,
    story_id,
):

    while True:

        chapter = await queue.get()

        try:

            if chapter is None:
                return

            await crawler.crawl(
                chapter.url,
                story_id,
                chapter.number,
            )

        finally:

            queue.task_done()
```

---

# 26. Chạy worker

```python
workers = [
    asyncio.create_task(
        worker(
            queue,
            crawler,
            story_id,
        )
    )
    for _ in range(5)
]
```

Sau đó:

```python
await producer(
    queue,
    paginator,
)

await queue.join()

await asyncio.gather(
    *workers
)
```

---

# 27. Toàn bộ Crawl Engine

Ta có:

```text
                     CrawlEngine
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
          Pagination                Queue
              │                       │
              │                ┌──────┼──────┐
              │                ▼      ▼      ▼
              │               W1     W2     W3
              │                │      │      │
              └────────────────┼──────┼──────┘
                               ▼
                           Fetcher
                               │
                             HTTPX
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
                           Chapter
                               │
                               ▼
                           Repository
                               │
                               ▼
                            SQLite
```

Đây chính là crawler framework.

---

# 28. SQLite schema

Ví dụ:

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    url TEXT NOT NULL UNIQUE
);
```

Chapter:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    story_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,

    FOREIGN KEY (
        story_id
    )
    REFERENCES stories(id)
);
```

Index:

```sql
CREATE INDEX idx_chapters_story
ON chapters(story_id);
```

---

# 29. Upsert

Crawler có thể chạy lại.

Không muốn:

```text
Chapter 1
Chapter 1
Chapter 1
Chapter 1
```

Ta có:

```sql
UNIQUE(url)
```

và:

```sql
INSERT ... ON CONFLICT ...
```

Ví dụ:

```sql
INSERT INTO chapters (
    story_id,
    number,
    title,
    url,
    content
)
VALUES (?, ?, ?, ?, ?)

ON CONFLICT(url)
DO UPDATE SET
    title = excluded.title,
    content = excluded.content;
```

Điều này rất quan trọng đối với crawler thực tế.

---

# 30. Logging

Không dùng:

```python
print("Downloading...")
```

Trong production-style project.

Dùng:

```python
import logging

logger = logging.getLogger(
    __name__
)
```

Ví dụ:

```python
logger.info(
    "Crawling chapter: %s",
    url,
)
```

Lỗi:

```python
logger.exception(
    "Failed to crawl %s",
    url,
)
```

---

# 31. Logging architecture

```text
Crawler
 ↓
logging
 ↓
Console
```

Sau này có thể:

```text
logging
 ├── console
 ├── file
 └── rotating file
```

---

# 32. CLI

Ví dụ:

```bash
crawler crawl \
    https://site-a.com/story/123
```

Hoặc:

```bash
crawler crawl \
    https://site-a.com/story/123 \
    --workers 5
```

Hoặc:

```bash
crawler crawl \
    https://site-a.com/story/123 \
    --database stories.db
```

CLI chỉ làm nhiệm vụ:

```text
CLI
 ↓
parse arguments
 ↓
build dependencies
 ↓
Application
```

Không chứa scraping logic.

---

# 33. Application Service

Ví dụ:

```python
class CrawlStoryUseCase:

    def __init__(
        self,
        crawler,
    ):
        self.crawler = crawler

    async def execute(
        self,
        url,
    ):

        return await self.crawler.crawl(
            url
        )
```

CLI:

```text
CLI
 ↓
CrawlStoryUseCase
 ↓
Crawler
```

Đây chính là tư duy Clean Architecture mà bạn đã học.

---

# 34. Dependency Injection

Không viết:

```python
class Crawler:

    def __init__(self):

        self.client = (
            httpx.AsyncClient()
        )

        self.db = sqlite3.connect(
            "crawler.db"
        )

        self.parser = SiteAParser()
```

Đây là **hard dependency**.

Thay vào đó:

```python
class Crawler:

    def __init__(
        self,
        fetcher,
        parser_registry,
        repository,
    ):
        self.fetcher = fetcher
        self.registry = parser_registry
        self.repository = repository
```

Bên ngoài inject:

```text
Composition Root
       │
       ├── HTTPX
       ├── Fetcher
       ├── Registry
       ├── Repository
       └── Crawler
```

---

# 35. Composition Root

Đây là nơi lắp toàn bộ hệ thống.

```python
async def build_application():

    client = httpx.AsyncClient(
        timeout=10
    )

    fetcher = AsyncFetcher(
        client
    )

    parser_registry = ParserRegistry(
        [
            SiteAParser(),
            SiteBParser(),
        ]
    )

    connection = sqlite3.connect(
        "stories.db"
    )

    repository = (
        SQLiteChapterRepository(
            connection
        )
    )

    crawler = ChapterCrawler(
        fetcher=fetcher,
        html_parser=HTMLDocumentParser(),
        parser_registry=parser_registry,
        repository=repository,
    )

    return crawler
```

---

# 36. Testing

Kiến trúc này có một lợi ích cực lớn:

**Không cần Internet để test parser.**

Fixture:

```html
<article>
    <h1 class="title">
        Chapter 1
    </h1>

    <div class="content">
        <p>Hello</p>
        <p>World</p>
    </div>
</article>
```

Test:

```python
def test_parse_chapter():

    tree = HTMLParser(
        html
    )

    chapter = parser.parse_chapter(
        tree,
        "https://site-a.com/ch1",
        1,
        1,
    )

    assert chapter.title == (
        "Chapter 1"
    )

    assert "Hello" in chapter.content
```

---

# 37. Fake Fetcher

Test crawler không cần HTTP.

```python
class FakeFetcher:

    async def fetch(self, url):

        return """
        <h1 class="title">
            Chapter 1
        </h1>

        <div class="content">
            Hello
        </div>
        """
```

Sau đó:

```python
crawler = ChapterCrawler(
    fetcher=FakeFetcher(),
    ...
)
```

Đây là sức mạnh của Dependency Injection.

---

# 38. Test Pyramid

Crawler framework:

```text
                 E2E
                /   \
               /     \
            Integration
             /       \
            /         \
        Unit Tests
```

Nhiều nhất:

```text
Parser tests
Model tests
Repository tests
```

Ít hơn:

```text
HTTP integration tests
```

Rất ít:

```text
Real website E2E tests
```

---

# 39. Một nguyên tắc cực kỳ quan trọng

**Parser test không nên gọi Internet.**

Sai:

```python
def test_parser():

    html = requests.get(
        "https://website.com"
    )
```

Đúng:

```text
fixture.html
 ↓
Selectolax
 ↓
Parser
 ↓
assert
```

Nhanh và deterministic.

---

# 40. Error handling

Crawler thực tế sẽ gặp:

```text
404
403
429
500
502
503
Timeout
Connection error
Broken HTML
Missing selector
Empty content
```

Không để:

```python
except Exception:
    pass
```

Đây là anti-pattern.

---

# 41. Tạo exception riêng

```python
class CrawlerError(Exception):
    pass


class FetchError(CrawlerError):
    pass


class ParserError(CrawlerError):
    pass


class UnsupportedSiteError(
    CrawlerError
):
    pass
```

Sau đó:

```text
CrawlerError
 ├── FetchError
 ├── ParserError
 └── UnsupportedSiteError
```

---

# 42. Defensive parsing

Đừng:

```python
title = tree.css_first(
    ".title"
).text()
```

vì:

```text
css_first()
 ↓
None
 ↓
AttributeError
```

Tốt hơn:

```python
node = tree.css_first(
    ".title"
)

if node is None:
    raise ParserError(
        "Missing title"
    )

title = node.text(
    strip=True
)
```

---

# 43. Crawler state

Production crawler thường cần:

```text
PENDING
RUNNING
SUCCESS
FAILED
SKIPPED
```

Ví dụ:

```python
from enum import Enum


class CrawlStatus(Enum):

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
```

Sau này database có thể lưu trạng thái chapter.

---

# 44. Retry + status

Một chapter:

```text
PENDING
   ↓
RUNNING
   ↓
HTTP 500
   ↓
RETRY
   ↓
HTTP 200
   ↓
SUCCESS
```

Nếu hết retry:

```text
FAILED
```

Đây là nền tảng để sau này xây:

* resume
* retry failed
* dashboard
* pause/resume
* crawl queue

---

# 45. Final architecture

Sau toàn bộ khóa Selectolax:

```text
                    ┌─────────────┐
                    │     CLI     │
                    └──────┬──────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Application     │
                  │ Use Case        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Crawl Engine   │
                  └────────┬────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Pagination       Queue       Registry
                            │             │
                       ┌────┼────┐     ┌──┼──┐
                       ▼    ▼    ▼     ▼  ▼  ▼
                      W1   W2   W3    A  B  C
                       │    │    │
                       └────┼────┘
                            ▼
                      AsyncFetcher
                            │
                          HTTPX
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
                       Domain Model
                            │
                            ▼
                        Repository
                            │
                            ▼
                          SQLite
```

---

# 46. Đây chính là sự kết hợp các kiến thức bạn đã học

Bạn đã đi qua:

```text
Selectolax
   │
   ├── CSS Selector
   ├── DOM Traversal
   ├── Performance
   ├── Error Handling
   └── Testing
```

Sau đó:

```text
HTTPX
   +
Asyncio
   +
SQLite
   +
Repository
   +
Clean Architecture
   +
Plugin Architecture
```

Kết quả:

```text
                 Production-style
                    Crawler
```

---

# 47. Bài tập Final Project

Tôi khuyên bạn **đừng copy toàn bộ code ở trên rồi coi như hoàn thành**.

Hãy tự xây theo 5 phase.

### Phase 1 — Core

```text
Story
Chapter
Repository
SQLite
```

### Phase 2 — Parser

```text
Parser Interface
ParserRegistry
SiteAParser
```

### Phase 3 — HTTP

```text
AsyncFetcher
HTTPX
Timeout
Retry
```

### Phase 4 — Async crawler

```text
Pagination
asyncio
Semaphore
Queue
Worker
```

### Phase 5 — Production

```text
CLI
Logging
Error handling
Testing
Configuration
```

---

# 48. Definition of Done

Project được xem là hoàn thành khi chạy được:

```bash
crawler crawl \
    https://site-a.com/story/123
```

và:

```text
CLI
 ↓
CrawlStoryUseCase
 ↓
Crawler
 ↓
Pagination
 ↓
Queue
 ↓
Workers
 ↓
HTTPX
 ↓
Selectolax
 ↓
SiteAParser
 ↓
Story / Chapter
 ↓
SQLite Repository
 ↓
stories.db
```

Database:

```text
stories
 ├── id
 ├── title
 ├── author
 └── url

chapters
 ├── id
 ├── story_id
 ├── number
 ├── title
 ├── url
 └── content
```

---

# 🎓 Tổng kết toàn bộ khóa Selectolax

Bạn bắt đầu từ:

```python
tree.css_first(".title")
```

và kết thúc ở:

```text
                   Selectolax
                       │
                       ▼
                Parser Plugin
                       │
                       ▼
                 Domain Model
                       │
                       ▼
                  Repository
                       │
                       ▼
                    SQLite

HTTPX ────────────────┐
                       │
Asyncio ───────────────┤
                       ▼
                  Crawl Engine
                       │
                  Worker Pool
                       │
                  Pagination
                       │
                    Retry
                       │
                    Queue
```

**Điểm quan trọng nhất của Buổi 20 không phải Selectolax nữa, mà là cách biến Selectolax thành một component trong một hệ thống crawler có kiến trúc tốt.**

Và từ đây, nếu ghép với những thứ bạn đã học trước đó, project truyện của bạn có thể tiến tới kiến trúc:

```text
PySide6 Dashboard
        │
        ▼
Crawler Manager
        │
        ▼
Job Queue
        │
        ▼
Async Crawler Workers
        │
        ▼
Plugin Parsers
        │
        ▼
SQLite / Story DB
```

Đó sẽ là bước rất tự nhiên để nối **Selectolax + HTTPX + Asyncio + SQLite + Repository + Clean Architecture + PySide6** thành một ứng dụng crawler/reader hoàn chỉnh.
