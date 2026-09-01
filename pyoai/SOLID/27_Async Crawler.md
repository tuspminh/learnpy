# 🚀 Buổi 27 — Async Crawler

Hôm nay chúng ta đưa **Story Crawler System** từ synchronous sang asynchronous.

Đây là buổi rất quan trọng vì nó kết hợp:

* `asyncio`
* `httpx.AsyncClient`
* Dependency Injection
* Protocol
* SOLID
* Crawler Plugin
* Concurrency
* Clean Architecture

Mục tiêu cuối buổi:

```text
CLI
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Async Crawler
 ↓
Async HTTP Client
 ↓
httpx.AsyncClient
```

và quan trọng nhất:

> **Domain/Application không cần biết HTTP đang sync hay async.**

---

# 1. Vì sao Crawler cần Async?

Crawler thường là chương trình **I/O-bound**.

Ví dụ:

```text
Request chapter 1 ────────────────┐
                                  │
Request chapter 2 ────────────────┤
                                  │
Request chapter 3 ────────────────┤
                                  │
Request chapter 4 ────────────────┘
```

Nếu synchronous:

```text
Chapter 1
   ↓
wait 1s
   ↓
Chapter 2
   ↓
wait 1s
   ↓
Chapter 3
   ↓
wait 1s
```

4 request có thể mất khoảng:

```text
4 × 1s = 4s
```

Async:

```text
Chapter 1 ────────┐
Chapter 2 ────────┤
Chapter 3 ────────┼── concurrent
Chapter 4 ────────┘
```

Có thể gần:

```text
~1s
```

nếu server và giới hạn concurrency cho phép.

---

# 2. Nhưng Async không có nghĩa là tạo 1000 thread

Đây là điểm rất quan trọng.

`asyncio` sử dụng:

```text
Event Loop
    ↓
Coroutine
    ↓
await I/O
    ↓
chuyển sang task khác
```

Ví dụ:

```python
async def download():
    response = await client.get(url)
```

Trong lúc:

```python
await client.get(...)
```

đang chờ network, event loop có thể chạy task khác.

---

# 3. Sync Architecture hiện tại

Chúng ta đang có:

```python
class HttpClient(Protocol):

    def get(self, url: str) -> str:
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

    def crawl(self, url):

        html = self.http_client.get(url)

        return self.parser.parse(
            html,
            url,
        )
```

Đây là synchronous.

---

# 4. Async Architecture

Ta tạo abstraction mới:

```python
from typing import Protocol


class AsyncHttpClient(Protocol):

    async def get(
        self,
        url: str,
    ) -> str:
        ...
```

Implementation:

```python
class HttpxAsyncClient:

    def __init__(self, client):
        self.client = client

    async def get(self, url):

        response = await self.client.get(
            url
        )

        response.raise_for_status()

        return response.text
```

---

# 5. Async Crawler

```python
class AsyncSourceACrawler:

    def __init__(
        self,
        http_client,
        parser,
    ):
        self.http_client = http_client
        self.parser = parser

    async def crawl(self, url):

        html = await self.http_client.get(
            url
        )

        return self.parser.parse(
            html,
            url,
        )
```

Điểm khác biệt chủ yếu:

```text
def
```

→

```text
async def
```

và:

```text
await
```

---

# 6. `await` nghĩa là gì?

Không phải:

```text
"đợi và chặn toàn bộ chương trình"
```

Mà gần đúng hơn:

```text
Task A
 ↓
await network
 ↓
nhường event loop
 ↓
Task B chạy
 ↓
Task C chạy
 ↓
network A hoàn thành
 ↓
Task A tiếp tục
```

---

# 7. Ví dụ cơ bản

```python
import asyncio


async def download(name):

    print("start", name)

    await asyncio.sleep(1)

    print("done", name)


async def main():

    await download("A")
    await download("B")
    await download("C")


asyncio.run(main())
```

Thời gian khoảng:

```text
3 seconds
```

Vì chúng ta vẫn chạy tuần tự.

---

# 8. Concurrent execution

Dùng:

```python
asyncio.gather()
```

```python
async def main():

    await asyncio.gather(
        download("A"),
        download("B"),
        download("C"),
    )
```

Bây giờ:

```text
A ──────────┐
B ──────────┤  ~1 second
C ──────────┘
```

---

# 9. Crawler nhiều chapter

Giả sử Story có:

```text
Chapter 1
Chapter 2
Chapter 3
Chapter 4
Chapter 5
```

Ta có:

```python
async def crawl_chapters(
    chapters
):

    results = await asyncio.gather(
        *(
            crawl_chapter(chapter)
            for chapter in chapters
        )
    )

    return results
```

Đây là concurrency cơ bản.

---

# 10. Nhưng có một vấn đề lớn

Nếu story có:

```text
5000 chapters
```

thì:

```python
asyncio.gather(
    *(crawl(...) for ...)
)
```

có thể tạo quá nhiều task/request.

Không nên.

Ta cần:

> **Concurrency limit**

---

# 11. `asyncio.Semaphore`

Ví dụ:

```python
semaphore = asyncio.Semaphore(10)
```

Chỉ cho tối đa:

```text
10 requests
```

đang chạy cùng lúc.

---

# 12. Download có giới hạn

```python
async def download(
    client,
    url,
    semaphore,
):

    async with semaphore:

        return await client.get(url)
```

Nếu có:

```text
1000 chapters
```

và:

```text
Semaphore(10)
```

thì:

```text
Chapter 1-10
      ↓
Chapter 11-20
      ↓
Chapter 21-30
      ↓
...
```

Nhưng bên trong vẫn là asynchronous concurrency.

---

# 13. Vì sao cần giới hạn?

Không chỉ vì máy của chúng ta.

Mà còn vì:

```text
Server
Rate limit
Bandwidth
Connection pool
CPU
Memory
```

và quan trọng:

> Không nên biến crawler thành một HTTP flooder.

---

# 14. HTTPX AsyncClient

Với `httpx`:

```python
import httpx


async with httpx.AsyncClient() as client:

    response = await client.get(
        "https://example.com"
    )

    response.raise_for_status()

    html = response.text
```

Điểm quan trọng:

```text
AsyncClient
```

nên được **reuse**.

Không nên:

```python
async def get(url):

    async with httpx.AsyncClient() as client:
        ...
```

mỗi request lại tạo client.

---

# 15. Tại sao reuse Client?

Một `AsyncClient` có thể quản lý:

```text
Connection Pool
Keep-alive
Connection reuse
Timeout
Headers
Cookies
```

Do đó tốt hơn:

```text
AsyncCrawler
      ↓
AsyncHttpClient
      ↓
ONE AsyncClient
      ↓
many requests
```

thay vì:

```text
request 1 → client 1
request 2 → client 2
request 3 → client 3
```

---

# 16. HTTP Client abstraction

Ta nên giữ Infrastructure phía sau abstraction:

```python
from typing import Protocol


class AsyncHttpClient(Protocol):

    async def get(
        self,
        url: str,
    ) -> str:
        ...
```

Implementation:

```python
class HttpxClient:

    def __init__(self, client):
        self.client = client

    async def get(self, url):

        response = await self.client.get(
            url
        )

        response.raise_for_status()

        return response.text
```

Application không cần biết `httpx`.

---

# 17. Async Parser

Parser thường là CPU-bound nhẹ.

Ví dụ:

```python
class StoryParser:

    def parse(
        self,
        html: str,
        url: Url,
    ) -> Story:
        ...
```

Không nhất thiết phải biến thành:

```python
async def parse(...)
```

Đây là insight quan trọng.

**Không phải cứ async crawler là mọi thứ đều async.**

---

# 18. Async chỉ ở I/O boundary

Một kiến trúc tốt có thể là:

```text
Async Crawler
      │
      ▼
Async HTTP
      │
      ▼
HTML
      │
      ▼
Sync Parser
      │
      ▼
Domain
```

Parser chạy rất nhanh:

```text
HTML → Story
```

không cần `await`.

---

# 19. Async Use Case

Bây giờ có một câu hỏi:

Crawler là:

```python
async def crawl()
```

thì Application phải làm gì?

Use Case cũng cần async:

```python
class CrawlStory:

    async def execute(
        self,
        url,
    ):

        crawler = self.registry.find(
            url
        )

        story = await crawler.crawl(
            url
        )

        await self.repository.save(
            story
        )

        return story
```

---

# 20. Repository cũng có thể Async

Nếu SQLite repository vẫn synchronous:

```python
repository.save(story)
```

thì Application có thể:

```python
story = await crawler.crawl(url)

repository.save(story)
```

Điều này có thể hoàn toàn hợp lý nếu persistence chưa phải bottleneck.

Nhưng nếu muốn toàn bộ pipeline async:

```python
class AsyncStoryRepository(
    Protocol
):

    async def save(
        self,
        story: Story,
    ) -> None:
        ...
```

---

# 21. `aiosqlite`

Infrastructure có thể dùng:

```python
import aiosqlite
```

Ví dụ:

```python
class SQLiteStoryRepository:

    def __init__(self, db):
        self.db = db

    async def save(self, story):

        await self.db.execute(
            """
            INSERT INTO stories
            (title, url)
            VALUES (?, ?)
            """,
            (
                story.title,
                story.url.value,
            ),
        )

        await self.db.commit()
```

---

# 22. Nhưng đừng Async hóa mọi thứ

Đây là một nguyên tắc rất quan trọng:

> **Async là một architectural decision, không phải một từ khóa để rải khắp code.**

Không nên:

```python
async def add(a, b):
    return a + b
```

Chỉ vì project đang dùng asyncio.

Nếu operation không có I/O:

```python
def add(a, b):
    return a + b
```

là tốt hơn.

---

# 23. Async Boundary

Ta có thể thiết kế:

```text
CLI
 │
 ▼
Async Application
 │
 ├── Async Crawler
 │       ↓
 │   Async HTTP
 │
 └── Async Repository
         ↓
      aiosqlite
```

Async boundary bắt đầu từ:

```text
Application
```

và đi xuống Infrastructure.

---

# 24. CLI cũng phải async

Ví dụ:

```python
async def handle_crawl(
    args,
    app,
):

    story = await app.execute(
        Url(args.url)
    )

    print(story.title)

    return 0
```

`main()`:

```python
def main():

    return asyncio.run(
        async_main()
    )
```

và:

```python
async def async_main():

    app = build_application()

    args = parse_args()

    return await handle_crawl(
        args,
        app,
    )
```

---

# 25. Flow mới

```text
main()
  ↓
asyncio.run()
  ↓
async_main()
  ↓
handle_crawl()
  ↓
await app.execute()
  ↓
await crawler.crawl()
  ↓
await http_client.get()
```

Event loop nằm ở ngoài cùng.

---

# 26. Composition Root

Bây giờ Composition Root:

```python
def build_application():

    http_client = HttpxClient(
        httpx.AsyncClient()
    )

    parser = SourceAStoryParser()

    crawler = SourceACrawler(
        http_client,
        parser,
    )

    registry = CrawlerRegistry()

    registry.register(crawler)

    repository = SQLiteStoryRepository(...)

    return CrawlStory(
        registry,
        repository,
    )
```

Nhưng có một vấn đề lifecycle:

```text
AsyncClient
```

phải được close.

---

# 27. Lifecycle Management

Không nên để:

```python
httpx.AsyncClient()
```

sống mãi mà không đóng.

Ta cần:

```python
async with httpx.AsyncClient() as client:
    ...
```

hoặc Application lifecycle rõ ràng:

```python
class App:

    async def start(self):
        ...

    async def close(self):
        ...
```

---

# 28. Một cách đơn giản

Composition Root có thể tạo resource trong async context:

```python
async def run():

    async with httpx.AsyncClient() as client:

        app = build_application(
            client
        )

        return await run_cli(app)
```

Flow:

```text
run()
 │
 ├── create AsyncClient
 │
 ├── build Application
 │
 ├── run CLI
 │
 └── close AsyncClient
```

Đây là lifecycle rất rõ.

---

# 29. Dependency Injection tiếp tục phát huy tác dụng

`build_application()`:

```python
def build_application(
    http_client,
    repository,
):
    ...
```

Production:

```text
HttpxClient
SQLiteRepository
```

Test:

```text
FakeHttpClient
FakeRepository
```

Không sửa Application.

---

# 30. Async Fake

Một Fake async:

```python
class FakeAsyncHttpClient:

    def __init__(self, html):
        self.html = html

    async def get(self, url):

        return self.html
```

Crawler:

```python
html = await self.http_client.get(
    url
)
```

Fake vẫn tương thích.

Đây là LSP + DIP.

---

# 31. Async Application Test

```python
@pytest.mark.asyncio
async def test_crawl_story():

    http = FakeAsyncHttpClient(
        "<html>...</html>"
    )

    parser = FakeParser()

    crawler = SourceACrawler(
        http,
        parser,
    )

    repository = FakeRepository()

    registry = FakeRegistry(
        crawler
    )

    use_case = CrawlStory(
        registry,
        repository,
    )

    result = await use_case.execute(
        Url("https://example.com")
    )

    assert result.title == "Test"
```

Không Internet.

---

# 32. Concurrent Chapters

Bây giờ đến phần quan trọng hơn.

Giả sử:

```python
chapters = [
    chapter1,
    chapter2,
    chapter3,
    chapter4,
]
```

Ta có:

```python
async def crawl_all(
    chapters
):

    return await asyncio.gather(
        *(
            self.crawl_chapter(chapter)
            for chapter in chapters
        )
    )
```

---

# 33. Nhưng thứ tự kết quả?

Một điểm hay của:

```python
asyncio.gather()
```

là kết quả trả về theo **thứ tự awaitables đầu vào**, không nhất thiết theo thứ tự task hoàn thành.

Ví dụ:

```text
Chapter 1 → 3s
Chapter 2 → 1s
Chapter 3 → 2s
```

Có thể hoàn thành:

```text
2
3
1
```

nhưng:

```python
results
```

vẫn:

```text
1
2
3
```

Điều này rất hữu ích khi chapter cần giữ thứ tự.

---

# 34. Semaphore

```python
class ChapterCrawler:

    def __init__(
        self,
        http_client,
        limit=10,
    ):
        self.http_client = http_client

        self.semaphore = (
            asyncio.Semaphore(limit)
        )
```

Sau đó:

```python
async def crawl_one(self, chapter):

    async with self.semaphore:

        html = await self.http_client.get(
            chapter.url
        )

        return self.parse(
            html
        )
```

---

# 35. Architecture lúc này

```text
                  CrawlStory
                      │
                      ▼
               AsyncCrawler
                      │
             ┌────────┴────────┐
             ▼                 ▼
       AsyncHttpClient       Parser
             │
             ▼
       httpx.AsyncClient
```

với nhiều chapter:

```text
AsyncCrawler
     │
     ├── Task 1
     ├── Task 2
     ├── Task 3
     ├── Task 4
     └── ...
          │
          ▼
      Semaphore
          │
          ▼
       HTTP Pool
```

---

# 36. Timeout

Crawler production không thể:

```python
await client.get(url)
```

vô thời hạn.

HTTPX:

```python
timeout = httpx.Timeout(
    10.0
)
```

hoặc:

```python
async with httpx.AsyncClient(
    timeout=10.0
) as client:
    ...
```

Ngoài ra có thể dùng:

```python
asyncio.timeout()
```

ở application boundary khi cần timeout cho cả operation.

---

# 37. Cancellation

Async crawler phải hiểu cancellation.

Ví dụ user:

```text
Ctrl+C
```

hoặc:

```text
Pause
Stop
Shutdown
```

Task có thể bị cancel.

```python
try:

    await crawler.crawl(url)

except asyncio.CancelledError:

    ...
    raise
```

Không nên nuốt `CancelledError` một cách tùy tiện.

---

# 38. Retry

Retry cũng nên nằm ở abstraction phù hợp.

Không nên:

```text
CLI retry
Application retry
Crawler retry
HTTP client retry
```

cùng lúc.

Nếu HTTP retry là infrastructure concern:

```text
HttpClient
 ↓
Retry policy
 ↓
HTTP
```

Nếu retry là business/application policy:

```text
Use Case
 ↓
Retry policy
 ↓
Crawler
```

Phải xác định **reason for change**.

Đây lại là SRP.

---

# 39. Async + SOLID

## SRP

```text
HTTP
Parser
Crawler
Repository
```

vẫn tách biệt.

## OCP

Có thể có:

```text
SyncCrawler
AsyncCrawler
```

hoặc nhiều implementation.

## LSP

Async implementation phải đáp ứng contract async.

## ISP

```text
AsyncHttpClient
AsyncRepository
Crawler
```

interface nhỏ.

## DIP

Application phụ thuộc:

```text
abstraction
```

không phụ thuộc:

```text
httpx
aiosqlite
```

---

# 40. Một cảnh báo quan trọng về LSP

Không thể thay trực tiếp:

```python
class SyncCrawler:

    def crawl(self, url):
        ...
```

bằng:

```python
class AsyncCrawler:

    async def crawl(self, url):
        ...
```

nếu contract ban đầu là synchronous.

Vì:

```python
result = crawler.crawl(url)
```

với async crawler sẽ trả:

```text
coroutine
```

chứ không phải:

```text
Story
```

Do đó:

```text
SyncCrawler
```

và:

```text
AsyncCrawler
```

nên có **contract riêng**.

Ví dụ:

```python
class Crawler(Protocol):

    def crawl(...) -> Story:
        ...
```

và:

```python
class AsyncCrawler(Protocol):

    async def crawl(...) -> Story:
        ...
```

Đây là LSP rất thực tế.

---

# 41. Có nên hỗ trợ cả Sync và Async?

Có thể.

Ví dụ:

```text
Crawler
   │
   ├── SyncCrawler
   │
   └── AsyncCrawler
```

Nhưng đừng cố làm:

```python
def crawl():
    if async:
        ...
```

cho mọi implementation.

Hai execution model khác nhau.

---

# 42. Thiết kế tôi khuyên dùng

Với project Story Crawler của chúng ta:

```text
domain/
    crawler.py

application/
    crawl_story.py

infrastructure/
    http/
        async_client.py
    crawler/
        source_a/
            async_crawler.py

presentation/
    cli.py

composition.py
```

Domain giữ contract business.

Infrastructure quyết định sync/async implementation.

---

# 43. Một phiên bản Protocol

```python
from typing import Protocol


class AsyncCrawler(Protocol):

    def can_handle(
        self,
        url: Url,
    ) -> bool:
        ...

    async def crawl(
        self,
        url: Url,
    ) -> Story:
        ...
```

`can_handle()` không cần async.

Vì nó chỉ kiểm tra:

```text
URL
 ↓
boolean
```

Còn:

```python
crawl()
```

có network → async.

---

# 44. Đây là một thiết kế rất đẹp

```text
can_handle()
    │
    └── synchronous

crawl()
    │
    └── asynchronous
```

Không async hóa những thứ không cần async.

---

# 45. Bài tập thực hành

### Bài 1

Tạo:

```python
class AsyncHttpClient(Protocol):
    async def get(...):
        ...
```

---

### Bài 2

Implement:

```text
HttpxAsyncClient
```

bằng:

```text
httpx.AsyncClient
```

---

### Bài 3

Chuyển:

```text
SourceACrawler
```

thành:

```text
AsyncSourceACrawler
```

---

### Bài 4

Viết:

```python
async def crawl_all(chapters)
```

sử dụng:

```python
asyncio.gather()
```

---

### Bài 5

Thêm:

```python
asyncio.Semaphore(5)
```

để giới hạn tối đa 5 request đồng thời.

---

### Bài 6

Viết:

```text
FakeAsyncHttpClient
```

để test crawler mà không Internet.

---

# 46. Challenge

Hãy xây flow:

```text
CLI
 ↓
asyncio.run()
 ↓
Async CrawlStory
 ↓
AsyncCrawlerRegistry
 ↓
AsyncSourceACrawler
 ↓
AsyncHttpClient
 ↓
httpx.AsyncClient
```

với:

```text
10 chapters
5 concurrent requests
```

và:

```text
Parser vẫn synchronous
```

---

# 47. Kiến thức quan trọng nhất hôm nay

Có 5 điều bạn nên nhớ:

### 1.

```text
asyncio ≠ multi-threading
```

### 2.

Async đặc biệt phù hợp với:

```text
I/O-bound
```

### 3.

Không phải mọi function đều cần:

```python
async def
```

### 4.

`AsyncCrawler` cần **async contract riêng** nếu execution model thay đổi.

### 5.

Nhờ DIP:

```text
Application
      ↓
AsyncCrawler Protocol
      ↑
AsyncSourceACrawler
```

Application không cần biết:

```text
httpx
```

được sử dụng bên dưới.

---

# 48. Architecture sau Buổi 27

```text
                         CLI
                          │
                          ▼
                   asyncio.run()
                          │
                          ▼
                  ┌──────────────┐
                  │ Async UseCase│
                  └──────┬───────┘
                         │
                         ▼
                 AsyncCrawler
                  Interface
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      SourceA Crawler          SourceB Crawler
             │
       ┌─────┴─────┐
       ▼           ▼
 AsyncHTTP       Parser
       │
       ▼
 httpx.AsyncClient
```

Và từ Buổi 28 chúng ta sẽ thêm một thành phần cực kỳ quan trọng:

```text
                    Crawler
                       │
                       ▼
                     Queue
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Worker 1            Worker 2
             │                   │
             └─────────┬─────────┘
                       ▼
                    SQLite
```

# **Buổi 28 — Queue + Worker**

Chúng ta sẽ thiết kế **crawler job queue** theo đúng tư duy architecture:

```text
CLI
 ↓
Application
 ↓
Job
 ↓
Queue Interface
 ↓
Redis Queue
 ↓
Worker
 ↓
Crawler
 ↓
Repository
```

và đặc biệt phân biệt rõ:

**Queue ≠ Worker ≠ Crawler ≠ Use Case**, tránh biến tất cả thành một `CrawlerManager` khổng lồ.
