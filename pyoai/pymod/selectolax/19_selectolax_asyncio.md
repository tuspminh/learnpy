# 📘 Selectolax — Buổi 19: Selectolax + Asyncio

Hôm nay chúng ta đưa crawler từ:

```text
HTTPX
 ↓
Selectolax
 ↓
Parser
 ↓
SQLite
```

sang:

```text
                 Asyncio
                    │
                    ▼
              Async HTTPX
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Chapter 1  Chapter 2  Chapter 3
          │         │         │
          └─────────┼─────────┘
                    ▼
                Selectolax
                    │
                    ▼
                  Parser
                    │
                    ▼
                 SQLite
```

Mục tiêu hôm nay không phải chỉ là "biến `def` thành `async def`", mà là hiểu **đâu nên async, đâu không nên async**.

---

# 1. Vì sao crawler cần Asyncio?

Giả sử có 100 chapter.

Crawler tuần tự:

```text
Chapter 1
  ↓ 1s
Chapter 2
  ↓ 1s
Chapter 3
  ↓ 1s
...
```

100 chapter ≈ 100 giây nếu mỗi request mất khoảng 1 giây.

Asyncio cho phép:

```text
Chapter 1 ────────┐
Chapter 2 ────────┤
Chapter 3 ────────┤
Chapter 4 ────────┤──→ HTTP server
Chapter 5 ────────┤
...
```

Trong lúc Chapter 1 đang **chờ network**, event loop có thể xử lý Chapter 2, 3, 4...

Đây là lý do async rất phù hợp với crawler.

---

# 2. Nhưng Selectolax có cần async không?

**Không.**

Selectolax xử lý:

```text
HTML string
 ↓
DOM
 ↓
CSS selector
 ↓
text
```

Đây là CPU-bound operation tương đối nhanh.

Không có:

```python
await tree.css_first(...)
```

Sai:

```python
title = await tree.css_first(...)
```

Đúng:

```python
title = tree.css_first(
    ".story-title"
)
```

---

# 3. Chỉ phần I/O cần async

Đây là tư duy quan trọng:

```text
HTTPX
  ↓
NETWORK I/O
  ↓
async

Selectolax
  ↓
CPU
  ↓
sync

SQLite
  ↓
blocking I/O
  ↓
cẩn thận
```

Pipeline:

```text
                async
                  │
                  ▼
               HTTPX
                  │
                  ▼
                HTML
                  │
                  ▼
             Selectolax
               sync
                  │
                  ▼
               Parser
               sync
                  │
                  ▼
               SQLite
```

---

# 4. HTTPX AsyncClient

HTTPX có:

```python
httpx.AsyncClient
```

Ví dụ:

```python
import httpx


async def fetch(url: str) -> str:

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url
        )

        response.raise_for_status()

        return response.text
```

Điểm quan trọng:

```python
await client.get(...)
```

---

# 5. Không tạo Client mỗi request

Không nên:

```python
async def fetch(url):

    async with httpx.AsyncClient() as client:
        return (
            await client.get(url)
        )
```

rồi gọi:

```text
100 lần
 ↓
100 AsyncClient
```

Điều này làm mất lợi ích connection pooling.

Tốt hơn:

```text
Crawler
   │
   ▼
AsyncClient
   │
   ├── request 1
   ├── request 2
   ├── request 3
   └── request 4
```

---

# 6. AsyncFetcher

Tạo:

```text
infrastructure/
└── http/
    └── async_fetcher.py
```

```python
import httpx


class AsyncFetcher:

    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client

    async def fetch(
        self,
        url: str,
    ) -> str:

        response = await self.client.get(
            url
        )

        response.raise_for_status()

        return response.text
```

---

# 7. HTTPX Client lifecycle

Ở application:

```python
async with httpx.AsyncClient(
    timeout=10.0
) as client:

    fetcher = AsyncFetcher(
        client
    )

    ...
```

Khi kết thúc:

```text
AsyncClient
 ↓
close connections
```

---

# 8. Asyncio `gather`

Giả sử:

```python
urls = [
    "https://example.com/chapter/1",
    "https://example.com/chapter/2",
    "https://example.com/chapter/3",
]
```

Tạo tasks:

```python
tasks = [
    fetcher.fetch(url)
    for url in urls
]
```

Chạy:

```python
results = await asyncio.gather(
    *tasks
)
```

Luồng:

```text
             gather()
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
   Task 1    Task 2    Task 3
      │         │         │
      ▼         ▼         ▼
   HTTP      HTTP      HTTP
      │         │         │
      └─────────┼─────────┘
                ▼
             results
```

---

# 9. Nhưng `gather()` có một vấn đề

Nếu:

```text
10,000 chapters
```

ta không nên:

```python
tasks = [
    fetcher.fetch(url)
    for url in 10_000_urls
]

await asyncio.gather(
    *tasks
)
```

Bạn vừa tạo:

```text
10,000 tasks
```

Điều này có thể gây:

* quá nhiều connection
* memory pressure
* server overload
* rate limiting
* timeout hàng loạt

Chúng ta cần **concurrency limit**.

---

# 10. `asyncio.Semaphore`

Ví dụ:

```python
semaphore = asyncio.Semaphore(
    5
)
```

Nghĩa là:

```text
tối đa 5 coroutine
```

được vào vùng critical section.

---

# 11. Async fetch có Semaphore

```python
async def fetch_with_limit(
    fetcher,
    semaphore,
    url,
):

    async with semaphore:

        return await fetcher.fetch(
            url
        )
```

Tạo:

```python
semaphore = asyncio.Semaphore(5)

tasks = [
    fetch_with_limit(
        fetcher,
        semaphore,
        url,
    )
    for url in urls
]

results = await asyncio.gather(
    *tasks
)
```

---

# 12. Hình dung

Có 20 chapter:

```text
20 tasks
   │
   ▼
Semaphore(5)
   │
   ├── Chapter 1
   ├── Chapter 2
   ├── Chapter 3
   ├── Chapter 4
   └── Chapter 5
        ↓
     hoàn thành
        ↓
   ├── Chapter 6
   ├── Chapter 7
   └── ...
```

Luôn chỉ có tối đa:

```text
5 requests
```

đồng thời.

---

# 13. Async Chapter Crawler

Ta có parser từ Buổi 18:

```python
class Parser:
    ...
```

Bây giờ:

```python
class AsyncChapterCrawler:

    def __init__(
        self,
        fetcher,
        html_parser,
        parser_registry,
        repository,
    ):
        self.fetcher = fetcher
        self.html_parser = html_parser
        self.parser_registry = (
            parser_registry
        )
        self.repository = repository
```

---

# 14. `crawl_chapter`

```python
async def crawl_chapter(
    self,
    url: str,
    story_id: int,
):

    html = await self.fetcher.fetch(
        url
    )

    tree = self.html_parser.parse(
        html
    )

    parser = (
        self.parser_registry
        .get_parser(url)
    )

    chapter = parser.parse_chapter(
        tree,
        url,
        story_id,
    )

    self.repository.save(
        chapter
    )

    return chapter
```

Notice:

```text
fetch
```

async.

Nhưng:

```text
Selectolax
Parser
Repository
```

vẫn sync.

---

# 15. Đây là điểm dễ sai

Bạn có thể nghĩ:

```python
await parser.parse_chapter(...)
```

Không.

Parser:

```python
def parse_chapter(...):
```

vẫn synchronous.

Đây là thiết kế tốt.

---

# 16. Async orchestration

Ví dụ:

```python
async def crawl_many(
    crawler,
    urls,
    story_id,
):

    tasks = [
        crawler.crawl_chapter(
            url,
            story_id,
        )
        for url in urls
    ]

    return await asyncio.gather(
        *tasks
    )
```

Đây là phiên bản đơn giản.

Nhưng chưa có giới hạn concurrency.

---

# 17. Thêm Semaphore

```python
async def crawl_one(
    crawler,
    semaphore,
    url,
    story_id,
):

    async with semaphore:

        return await crawler.crawl_chapter(
            url,
            story_id,
        )
```

Sau đó:

```python
semaphore = asyncio.Semaphore(
    5
)

tasks = [
    crawl_one(
        crawler,
        semaphore,
        url,
        story_id,
    )
    for url in urls
]

results = await asyncio.gather(
    *tasks
)
```

---

# 18. Tốt hơn: Semaphore nằm ở đâu?

Không nên để mỗi caller tự tạo:

```python
Semaphore(5)
```

Nên configuration thuộc crawler/application:

```python
class AsyncChapterCrawler:

    def __init__(
        self,
        ...,
        concurrency: int = 5,
    ):
        self.semaphore = (
            asyncio.Semaphore(
                concurrency
            )
        )
```

---

# 19. Crawler hoàn chỉnh

```python
class AsyncChapterCrawler:

    def __init__(
        self,
        fetcher,
        html_parser,
        parser_registry,
        repository,
        concurrency=5,
    ):
        self.fetcher = fetcher
        self.html_parser = html_parser
        self.parser_registry = (
            parser_registry
        )
        self.repository = repository

        self.semaphore = (
            asyncio.Semaphore(
                concurrency
            )
        )
```

---

# 20. Crawl một chapter

```python
async def crawl_chapter(
    self,
    url,
    story_id,
):

    async with self.semaphore:

        html = await self.fetcher.fetch(
            url
        )

    tree = self.html_parser.parse(
        html
    )

    parser = (
        self.parser_registry
        .get_parser(url)
    )

    chapter = parser.parse_chapter(
        tree,
        url,
        story_id,
    )

    self.repository.save(
        chapter
    )

    return chapter
```

Chú ý:

Semaphore chỉ bao quanh network:

```text
Semaphore
    │
    ▼
 HTTP request
    │
    ▼
  release
    │
    ▼
Selectolax
```

Đây thường là cách hợp lý hơn so với giữ semaphore trong toàn bộ quá trình parse/save.

---

# 21. Nhưng SQLite lại là vấn đề

Ta đang làm:

```text
5 async tasks
    │
    ├── fetch
    ├── parse
    ├── save SQLite
    │
    ├── fetch
    ├── parse
    └── save SQLite
```

`sqlite3` Python là synchronous.

Nếu:

```python
self.repository.save(
    chapter
)
```

thực hiện operation lâu, nó block event loop.

---

# 22. Có nên biến SQLite thành async?

Có nhiều lựa chọn.

Nhưng project của chúng ta đang chủ động học:

```text
sqlite3
```

nên **không nhất thiết phải thay repository bằng async database ngay**.

Có thể:

```text
Async HTTP
      ↓
Selectolax
      ↓
Sync SQLite
```

với concurrency vừa phải.

---

# 23. `asyncio.to_thread`

Nếu operation blocking đáng kể:

```python
await asyncio.to_thread(
    repository.save,
    chapter,
)
```

Python sẽ đưa operation synchronous sang thread.

Luồng:

```text
Event Loop
    │
    ▼
to_thread()
    │
    ▼
Thread
    │
    ▼
SQLite
```

---

# 24. Nhưng đừng lạm dụng

Không nên:

```python
await asyncio.to_thread(
    tree.css_first,
    ".title"
)
```

Selectolax parse nhanh, không đáng.

Chỉ cân nhắc `to_thread()` cho operation blocking thực sự.

---

# 25. SQLite concurrency

Một vấn đề khác:

```text
Task 1 → SQLite write
Task 2 → SQLite write
Task 3 → SQLite write
Task 4 → SQLite write
```

Không nên cho hàng chục coroutine cùng write vào SQLite một cách tùy tiện.

Một kiến trúc đơn giản:

```text
Async workers
      │
      ▼
Chapter results
      │
      ▼
Single persistence path
      │
      ▼
SQLite
```

---

# 26. Database Writer

Có thể dùng:

```python
asyncio.Queue
```

Kiến trúc:

```text
Crawler 1 ─┐
Crawler 2 ─┤
Crawler 3 ─┤
Crawler 4 ─┤
            ▼
       asyncio.Queue
            │
            ▼
       DB Writer
            │
            ▼
          SQLite
```

Đây là kiến trúc rất hay.

---

# 27. Nhưng hôm nay chưa cần quá phức tạp

Ở Buổi 19, chúng ta tập trung:

```text
Async HTTP
+
Concurrency
+
Selectolax
```

Database queue sẽ là một bước nâng cao trong Final Project.

---

# 28. Async Story Crawler

Bây giờ:

```text
Story URL
 ↓
fetch
 ↓
parse story
 ↓
save story
 ↓
chapter links
 ↓
async crawl
```

Code:

```python
async def crawl_story(
    self,
    url,
):

    html = await self.fetcher.fetch(
        url
    )

    tree = self.html_parser.parse(
        html
    )

    parser = (
        self.registry.get_parser(url)
    )

    story = parser.parse_story(
        tree,
        url,
    )

    story_id = (
        self.story_repository.save(
            story
        )
    )

    return story_id, story
```

---

# 29. Crawl chapters

```python
async def crawl_chapters(
    self,
    story_id,
    chapters,
):

    tasks = [
        self.chapter_crawler
        .crawl_chapter(
            chapter.url,
            story_id,
        )
        for chapter in chapters
    ]

    return await asyncio.gather(
        *tasks
    )
```

Nếu:

```text
chapters = 100
```

thì tạo 100 coroutine.

Semaphore sẽ giới hạn HTTP concurrency.

---

# 30. Complete flow

```python
async def crawl(
    self,
    story_url,
):

    story_id, story = (
        await self.crawl_story(
            story_url
        )
    )

    chapters = story.chapters

    await self.crawl_chapters(
        story_id,
        chapters,
    )
```

---

# 31. Pagination + Asyncio

Đây mới là phần thú vị.

Ta có:

```text
Page 1
 ↓
Chapter links
 ↓
Page 2
 ↓
Chapter links
 ↓
Page 3
```

Pagination bản thân nó thường **tuần tự**:

```text
Page 1 → Page 2 → Page 3
```

vì:

```text
Page 2 URL
```

có thể chỉ biết sau khi parse Page 1.

Nhưng chapter trong cùng một page:

```text
Chapter 1
Chapter 2
Chapter 3
...
```

có thể chạy concurrent.

---

# 32. Kiến trúc tối ưu

```text
Pagination
    │
    ▼
 Page 1
    │
    ├── Chapter 1 ─┐
    ├── Chapter 2 ─┤
    ├── Chapter 3 ─┤
    └── Chapter 4 ─┘
                   │
                   ▼
                workers

    ↓

 Page 2
    │
    ├── Chapter 5
    ├── Chapter 6
    └── Chapter 7
```

Không nhất thiết phải:

```text
Page 1
 ↓
crawl toàn bộ chapter
 ↓
Page 2
```

mà có thể thiết kế queue pipeline sau này.

---

# 33. Async Pagination

```python
async def paginate(
    self,
    start_url,
):

    url = start_url
    visited = set()

    while url:

        if url in visited:
            break

        visited.add(url)

        html = await self.fetcher.fetch(
            url
        )

        tree = self.html_parser.parse(
            html
        )

        parser = (
            self.registry.get_parser(
                url
            )
        )

        chapters = (
            parser.parse_chapter_links(
                tree,
                url,
            )
        )

        for chapter in chapters:
            yield chapter

        url = parser.parse_next_page(
            tree,
            url,
        )
```

---

# 34. Async generator

Đây là kiến thức rất quan trọng.

```python
async def paginate(...):
    ...
    yield chapter
```

Đây là:

> **Async Generator**

Consume:

```python
async for chapter in paginator.paginate(
    story_url
):
    ...
```

---

# 35. Async generator vs coroutine

Coroutine:

```python
async def fetch():
    return html
```

Gọi:

```python
html = await fetch()
```

Async generator:

```python
async def paginate():

    yield chapter
```

Consume:

```python
async for chapter in paginate():
    ...
```

---

# 36. Kết hợp Pagination + Concurrent Chapter Crawl

Có thể:

```python
async def crawl_story(
    self,
    story_url,
):

    tasks = []

    async for chapter in (
        self.paginator.paginate(
            story_url
        )
    ):

        task = asyncio.create_task(
            self.chapter_crawler
            .crawl_chapter(
                chapter.url,
                story_id,
            )
        )

        tasks.append(task)

    await asyncio.gather(
        *tasks
    )
```

Nhưng lại có vấn đề:

Nếu 10.000 chapter:

```text
10,000 Task
```

Không tốt.

---

# 37. Đây là lúc Worker Pool xuất hiện

Thay vì:

```text
10,000 tasks
```

ta có:

```text
                 Queue
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    Worker 1    Worker 2    Worker 3
       │           │           │
       └───────────┼───────────┘
                   ▼
                Chapter
```

Ví dụ:

```python
queue = asyncio.Queue()
```

---

# 38. Producer

```python
async def producer(
    queue,
    paginator,
):

    async for chapter in paginator.paginate(
        story_url
    ):

        await queue.put(
            chapter
        )
```

---

# 39. Worker

```python
async def worker(
    queue,
    crawler,
    story_id,
):

    while True:

        chapter = await queue.get()

        try:

            await crawler.crawl_chapter(
                chapter.url,
                story_id,
            )

        finally:

            queue.task_done()
```

---

# 40. N workers

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

Kết quả:

```text
                 Queue
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
       W1         W2         W3
        │          │          │
        ▼          ▼          ▼
      HTTP       HTTP       HTTP
```

Đây là kiến trúc **worker pool**.

---

# 41. Worker Pool vs Semaphore

Hai kỹ thuật khác nhau.

### Semaphore

```text
Tasks
 │
 ▼
Semaphore(5)
```

Giới hạn concurrency.

### Worker Pool

```text
Queue
 │
 ├── Worker 1
 ├── Worker 2
 ├── Worker 3
 ├── Worker 4
 └── Worker 5
```

Giới hạn số worker và rất phù hợp với workload lớn.

---

# 42. Khi nào dùng cái nào?

Crawler nhỏ:

```text
100 chapter
```

→ Semaphore + gather đủ.

Crawler lớn:

```text
100,000 chapter
```

→ Queue + Worker Pool tốt hơn.

Final Project của chúng ta sẽ hướng tới worker pool.

---

# 43. Rate Limiting

Concurrency:

```text
5 requests cùng lúc
```

không có nghĩa:

```text
5 requests / second
```

Ví dụ server trả response cực nhanh, 5 workers có thể tạo:

```text
5
5
5
5
5
...
```

rất nhanh.

Có thể cần:

```text
rate limiter
```

Ví dụ:

```text
max 2 requests / second
```

Đây là một khái niệm khác với concurrency.

---

# 44. Timeout

Async HTTPX:

```python
timeout = httpx.Timeout(
    10.0
)

client = httpx.AsyncClient(
    timeout=timeout
)
```

Có thể cấu hình riêng:

```python
httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)
```

---

# 45. Retry

Retry vẫn nằm ở:

```text
AsyncFetcher
```

Không nằm trong:

```text
Selectolax
Parser
```

Architecture:

```text
AsyncChapterCrawler
       │
       ▼
 AsyncFetcher
       │
       ├── timeout
       ├── retry
       ├── status
       └── HTTPX
```

---

# 46. Không retry mọi lỗi

Ví dụ:

```text
500 → retry
502 → retry
503 → retry
504 → retry
```

thường hợp lý.

Nhưng:

```text
404
```

thường không cần retry nhiều lần.

Và:

```text
400
```

thường là lỗi request.

---

# 47. Backoff

Không nên:

```text
retry ngay
retry ngay
retry ngay
```

Mà:

```text
attempt 1
 ↓
0.5s
 ↓
attempt 2
 ↓
1s
 ↓
attempt 3
 ↓
2s
```

Đây là:

> Exponential Backoff

---

# 48. Async retry concept

Ví dụ:

```python
await asyncio.sleep(
    delay
)
```

Không dùng:

```python
time.sleep(
    delay
)
```

trong async code.

Sai:

```python
time.sleep(2)
```

vì nó block event loop.

Đúng:

```python
await asyncio.sleep(2)
```

---

# 49. Selectolax trong async crawler

Đây là điểm cần ghi nhớ:

```python
async def crawl(url):

    html = await fetch(url)

    tree = HTMLParser(html)

    title = tree.css_first(
        ".title"
    )

    return title.text(strip=True)
```

Không cần:

```python
await HTMLParser(...)
```

Không cần:

```python
await tree.css(...)
```

Selectolax vẫn synchronous.

---

# 50. Architecture sau Buổi 19

```text
                         Application
                              │
                              ▼
                        StoryCrawler
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               Pagination          Chapter Queue
                    │                   │
                    ▼                   ▼
               AsyncFetcher        Worker Pool
                    │                   │
                    ▼                   ▼
                 HTTPX             AsyncFetcher
                    │                   │
                    ▼                   ▼
                  HTML                HTML
                    │                   │
                    ▼                   ▼
                Selectolax          Selectolax
                    │                   │
                    ▼                   ▼
                  Parser              Parser
                    │                   │
                    └─────────┬─────────┘
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

# 51. Điều gì đã async?

| Thành phần           | Async? |
| -------------------- | ------ |
| HTTPX request        | ✅      |
| Fetcher              | ✅      |
| Pagination fetch     | ✅      |
| Chapter crawler      | ✅      |
| `asyncio.Queue`      | ✅      |
| Worker               | ✅      |
| Selectolax           | ❌      |
| CSS selector         | ❌      |
| Domain model         | ❌      |
| Parser               | ❌      |
| `sqlite3` repository | ❌      |

Đây là bảng rất đáng nhớ.

---

# 52. Một nguyên tắc architecture

> **Async không phải là một tính năng phải lan xuống toàn bộ hệ thống.**

Ví dụ:

```text
AsyncFetcher
      ↓
HTML
      ↓
Parser
```

Parser không cần biết:

```text
asyncio
await
Task
Queue
```

Điều này làm parser:

* dễ test
* dễ tái sử dụng
* đơn giản
* không phụ thuộc infrastructure

---

# 53. Test Async Fetcher

Với pytest:

```python
@pytest.mark.asyncio
async def test_fetch():

    html = await fetcher.fetch(
        "https://example.com"
    )

    assert "<html" in html
```

Trong unit test thực tế, nên mock HTTP thay vì gọi Internet.

---

# 54. Test async crawler

Có thể fake fetcher:

```python
class FakeAsyncFetcher:

    async def fetch(self, url):

        return {
            "chapter/1": chapter_html
        }[url]
```

Parser vẫn dùng thật:

```text
FakeFetcher
 ↓
HTML
 ↓
Selectolax
 ↓
Parser
```

Không cần network.

---

# 55. Bài tập 1 — AsyncFetcher

Viết:

```python
class AsyncFetcher:
    ...
```

có:

```text
AsyncClient
timeout
raise_for_status
```

---

# 56. Bài tập 2 — Concurrent crawl

Tạo 10 URL giả.

Chạy:

```python
await asyncio.gather(...)
```

để crawl đồng thời.

---

# 57. Bài tập 3 — Semaphore

Giới hạn:

```python
concurrency=3
```

Test đảm bảo:

```text
max 3 requests
```

đồng thời.

---

# 58. Bài tập 4 — Async Pagination

Viết:

```python
async def paginate():
    ...
    yield chapter
```

và consume:

```python
async for chapter in paginator.paginate(
    story_url
):
    print(chapter.url)
```

---

# 59. Bài tập 5 — Worker Pool

Tạo:

```text
asyncio.Queue
```

và:

```text
5 workers
```

Pipeline:

```text
Producer
   ↓
Queue
   ↓
Worker 1
Worker 2
Worker 3
Worker 4
Worker 5
```

---

# 60. Bài tập 6 — Async + Selectolax

Viết:

```python
async def parse_url(url):

    html = await fetcher.fetch(
        url
    )

    tree = HTMLParser(html)

    node = tree.css_first(
        ".title"
    )

    return node.text(
        strip=True
    )
```

Bạn phải hiểu rõ:

```text
await
```

chỉ nằm ở network.

---

# 🎯 Tổng kết Buổi 19

Chúng ta đã đi từ:

```text
Synchronous Crawler
```

sang:

```text
Async Crawler
```

với:

```text
HTTPX AsyncClient
        ↓
AsyncFetcher
        ↓
asyncio
        ↓
Concurrency
        ↓
Selectolax
        ↓
Parser Plugin
        ↓
Repository
        ↓
SQLite
```

Điểm quan trọng nhất cần nhớ:

### ① HTTPX → async

```python
await client.get(url)
```

### ② Selectolax → sync

```python
tree = HTMLParser(html)
```

### ③ Parser → sync

```python
story = parser.parse_story(...)
```

### ④ Giới hạn concurrency

```python
asyncio.Semaphore(5)
```

### ⑤ Nhiều task lớn → Queue + Worker Pool

```text
Producer
   ↓
asyncio.Queue
   ↓
Workers
```

### ⑥ SQLite → phải cẩn thận với blocking/concurrent writes

---

# 🚀 Buổi 20 — Final Project

Sau 19 buổi, chúng ta đã có gần đủ các mảnh ghép:

```text
                 ┌───────────────────┐
                 │   Crawler Core    │
                 └─────────┬─────────┘
                           │
                    Parser Registry
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Site A         Site B        Site C
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                     Selectolax
                           │
                           ▼
                    Domain Models
                     │         │
                   Story     Chapter
                     │         │
                     └────┬────┘
                          ▼
                     Repository
                          │
                          ▼
                        SQLite

                    Async HTTPX
                          │
                          ▼
                    Worker Pool
                          │
                          ▼
                    Crawl Engine
```

**Buổi 20 sẽ ghép toàn bộ thành một `production-style crawler framework` hoàn chỉnh**, bao gồm cấu trúc package, `Fetcher`, `ParserRegistry`, plugin parser, pagination, async worker pool, retry/timeout, SQLite Repository, logging, configuration và CLI.
