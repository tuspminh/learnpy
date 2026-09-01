# Buổi 28 — Queue + Worker

Hôm nay chúng ta đưa Story Crawler từ **Async Crawler** lên kiến trúc có **Queue + Worker**.

Đây là bước rất quan trọng vì từ đây project bắt đầu có dáng dấp một hệ thống production:

```text
CLI
 ↓
Application
 ↓
Job
 ↓
Queue
 ↓
Worker
 ↓
Crawler
 ↓
Repository
```

Và ta sẽ tiếp tục dùng SOLID để giữ architecture không biến thành một `CrawlerManager` khổng lồ.

---

# 1. Queue giải quyết vấn đề gì?

Ở Buổi 27:

```text
CLI
 ↓
CrawlStory
 ↓
AsyncCrawler
 ↓
HTTP
```

CLI phải chờ crawler hoàn thành.

Nếu có:

```text
100 stories
```

ta có thể muốn:

```text
CLI
 ↓
submit 100 jobs
 ↓
Queue
 ↓
Worker 1 ──┐
Worker 2 ──┤
Worker 3 ──┤
Worker 4 ──┘
```

CLI không cần trực tiếp xử lý toàn bộ công việc.

---

# 2. Queue là gì?

Queue là nơi lưu các **job đang chờ xử lý**.

Ví dụ:

```text
Queue

┌──────────────────────┐
│ CrawlStory #101      │
├──────────────────────┤
│ CrawlStory #102      │
├──────────────────────┤
│ CrawlStory #103      │
├──────────────────────┤
│ CrawlStory #104      │
└──────────────────────┘
```

Worker lấy job:

```text
Queue
  │
  ├── pop → Worker 1
  ├── pop → Worker 2
  └── pop → Worker 3
```

---

# 3. Queue không phải Worker

Đây là distinction cực kỳ quan trọng.

### Queue

```text
Nhận
Lưu
Phân phối
```

### Worker

```text
Nhận Job
Execute Job
Success / Failure
```

### Crawler

```text
Crawl website
Parse data
```

Không được trộn chúng.

---

# 4. Job là gì?

Job là một đơn vị công việc.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlStoryJob:

    url: str
```

Nó chỉ nói:

> Hãy crawl story này.

Job **không tự crawl**.

---

# 5. Job không nên chứa dependency

Không nên:

```python
@dataclass
class CrawlStoryJob:

    url: str
    crawler: Crawler
    repository: Repository
    http_client: HttpClient
```

Vì Job lúc này biết quá nhiều.

Đúng hơn:

```python
@dataclass(frozen=True)
class CrawlStoryJob:

    url: str
```

Dependency nằm ở Worker/Application.

---

# 6. Queue Interface

Đây là nơi SOLID + DIP xuất hiện.

```python
from typing import Protocol


class JobQueue(Protocol):

    async def enqueue(
        self,
        job,
    ) -> None:
        ...

    async def dequeue(self):
        ...
```

Application phụ thuộc:

```text
JobQueue
```

không phụ thuộc:

```text
Redis
RabbitMQ
SQLite
Memory Queue
```

---

# 7. In-Memory Queue

Đầu tiên đừng dùng Redis.

Hãy hiểu abstraction bằng một implementation đơn giản.

```python
import asyncio


class InMemoryJobQueue:

    def __init__(self):
        self._queue = asyncio.Queue()

    async def enqueue(self, job):

        await self._queue.put(job)

    async def dequeue(self):

        return await self._queue.get()

    def task_done(self):

        self._queue.task_done()
```

---

# 8. Producer

Producer là thành phần đưa Job vào Queue.

Ví dụ:

```python
class CrawlJobProducer:

    def __init__(self, queue):
        self.queue = queue

    async def submit(self, url):

        job = CrawlStoryJob(
            url=url
        )

        await self.queue.enqueue(job)
```

Flow:

```text
CLI
 ↓
Producer
 ↓
Job
 ↓
Queue
```

---

# 9. Worker

Worker lấy Job:

```python
class Worker:

    def __init__(
        self,
        queue,
        handler,
    ):
        self.queue = queue
        self.handler = handler
```

Worker loop:

```python
async def run(self):

    while True:

        job = await self.queue.dequeue()

        await self.handler.handle(job)

        self.queue.task_done()
```

Nhưng implementation production cần xử lý shutdown và exception. Chúng ta sẽ làm ngay sau đây.

---

# 10. Job Handler

Worker không nên biết cách crawl.

Đây là lỗi:

```python
class Worker:

    async def run(self):

        job = await self.queue.dequeue()

        crawler = ...
        html = ...
        parser = ...
        repository = ...
```

Worker đang trở thành God Object.

Thay vào đó:

```text
Worker
 ↓
JobHandler
 ↓
Use Case
```

---

# 11. Job Handler

```python
class CrawlStoryJobHandler:

    def __init__(
        self,
        use_case,
    ):
        self.use_case = use_case

    async def handle(self, job):

        return await self.use_case.execute(
            job.url
        )
```

Worker chỉ biết:

```text
Job
 ↓
Handler
```

---

# 12. Kiến trúc

Bây giờ:

```text
                CLI
                 │
                 ▼
              Producer
                 │
                 ▼
               Queue
                 │
                 ▼
              Worker
                 │
                 ▼
             JobHandler
                 │
                 ▼
             Use Case
                 │
                 ▼
             Crawler
```

Đây là separation rất tốt.

---

# 13. Một Worker

```python
async def worker_loop(
    queue,
    handler,
):

    while True:

        job = await queue.dequeue()

        try:

            await handler.handle(job)

        except Exception as exc:

            print(
                f"Job failed: {exc}"
            )

        finally:

            queue.task_done()
```

Nhưng `except Exception` ở đây mới chỉ là bản đơn giản.

---

# 14. Vì sao phải `finally`?

Giả sử:

```text
Queue
 ↓
Worker
 ↓
Job
 ↓
Exception
```

Nếu không:

```python
queue.task_done()
```

thì Queue có thể nghĩ:

```text
job vẫn chưa hoàn thành
```

và:

```python
await queue.join()
```

có thể chờ mãi.

Do đó:

```python
try:
    ...
finally:
    queue.task_done()
```

là pattern rất quan trọng.

---

# 15. Nhiều Worker

Ví dụ:

```python
workers = [
    asyncio.create_task(
        worker_loop(queue, handler)
    )
    for _ in range(5)
]
```

Ta có:

```text
             Queue
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
    Worker1 Worker2 Worker3 ...
```

Đây chính là **worker concurrency**.

---

# 16. Worker khác với Async Crawler

Đừng nhầm:

```text
Worker concurrency
```

với:

```text
HTTP concurrency
```

Ví dụ:

```text
3 Workers
```

mỗi Worker có:

```text
AsyncCrawler
```

và crawler có:

```text
Semaphore(10)
```

thì tổng concurrency có thể rất lớn.

Phải thiết kế cẩn thận.

---

# 17. Một kiến trúc đơn giản hơn

Ban đầu tôi khuyên:

```text
1 Worker
   ↓
Async Crawler
   ↓
Semaphore(10)
```

Tức là:

```text
Queue
 ↓
Worker
 ↓
AsyncCrawler
 ↓
10 concurrent HTTP requests
```

Đây là architecture dễ kiểm soát.

Sau này mới scale:

```text
Worker 1
Worker 2
Worker 3
```

---

# 18. Queue + Asyncio

Nếu tất cả nằm trong **một process**:

```python
asyncio.Queue
```

là đủ.

Ví dụ:

```text
Producer
   ↓
asyncio.Queue
   ↓
Worker
```

Nhưng nếu muốn:

```text
Process 1
Process 2
Process 3
```

hoặc:

```text
Server A
Server B
Server C
```

thì `asyncio.Queue` không đủ.

---

# 19. Lúc này cần Redis

Architecture:

```text
CLI
 ↓
Application
 ↓
Redis Queue
 ↓
Worker 1
Worker 2
Worker 3
```

Redis trở thành Infrastructure.

Application chỉ biết:

```python
JobQueue
```

---

# 20. Redis Queue Interface

Ta giữ nguyên:

```python
class JobQueue(Protocol):

    async def enqueue(
        self,
        job,
    ) -> None:
        ...

    async def dequeue(self):
        ...
```

Implementation:

```text
RedisJobQueue
```

không làm thay đổi Application.

Đây là:

> **Dependency Inversion + Open/Closed Principle**

---

# 21. Serialization

Có một vấn đề mới.

Memory Queue:

```python
await queue.enqueue(job)
```

có thể truyền trực tiếp object.

Redis thì:

```text
Process A
```

không thể đưa Python object trực tiếp cho:

```text
Process B
```

Ta cần serialization.

Ví dụ JSON:

```json
{
    "type": "crawl_story",
    "url": "https://example.com/story/1"
}
```

---

# 22. Job Envelope

Tôi khuyên dùng:

```python
@dataclass(frozen=True)
class Job:

    id: str
    type: str
    payload: dict
```

Ví dụ:

```python
Job(
    id="abc123",
    type="crawl_story",
    payload={
        "url": "https://example.com/1"
    },
)
```

Queue xử lý:

```text
Job
 ↓
serialize
 ↓
Redis
 ↓
deserialize
 ↓
Job
```

---

# 23. Vì sao cần Job ID?

Ví dụ:

```text
job_id = 8f31...
```

Dùng để:

```text
tracking
logging
retry
deduplication
debugging
```

Sau này CLI có thể:

```bash
crawler job-status 8f31...
```

---

# 24. Job Status

Một Job production thường có:

```text
PENDING
RUNNING
SUCCESS
FAILED
RETRYING
```

Ví dụ:

```text
PENDING
   ↓
RUNNING
   ↓
SUCCESS
```

hoặc:

```text
PENDING
   ↓
RUNNING
   ↓
FAILED
   ↓
RETRYING
   ↓
RUNNING
```

---

# 25. Retry

Crawler rất dễ gặp:

```text
Timeout
ConnectionError
HTTP 429
HTTP 503
```

Ta không muốn:

```text
Job fail
→ bỏ luôn
```

Có thể:

```text
attempt = 1
 ↓
failure
 ↓
retry
 ↓
attempt = 2
```

---

# 26. Nhưng Retry không phải vô hạn

Ví dụ:

```python
MAX_RETRIES = 3
```

Flow:

```text
Attempt 1
   ↓ fail
Attempt 2
   ↓ fail
Attempt 3
   ↓ fail
FAILED
```

Không:

```text
retry forever
```

---

# 27. Exponential Backoff

Không nên:

```text
retry
retry
retry
retry
```

ngay lập tức.

Dùng:

```text
1s
2s
4s
8s
```

Ví dụ:

```python
delay = 2 ** attempt
```

Production thường còn thêm **jitter** để tránh nhiều worker retry cùng lúc.

---

# 28. Dead Letter Queue

Nếu Job thất bại quá nhiều:

```text
Queue
 ↓
Worker
 ↓
retry x3
 ↓
FAILED
 ↓
Dead Letter Queue
```

DLQ giúp giữ lại những Job cần điều tra.

Ví dụ:

```text
dead_letter_queue
```

chứa:

```text
job_id
error
attempts
payload
timestamp
```

---

# 29. Ack

Queue production cần hiểu concept:

> **Acknowledgement**

Worker:

```text
dequeue
 ↓
process
 ↓
success
 ↓
ACK
```

Nếu:

```text
dequeue
 ↓
process
 ↓
worker crash
```

thì Job không nên biến mất vĩnh viễn.

Đây là vấn đề lớn của distributed worker.

---

# 30. At-least-once

Một queue phổ biến có semantics:

```text
At-least-once delivery
```

Nghĩa là Job có thể được xử lý:

```text
1 lần
```

hoặc:

```text
nhiều lần
```

Do đó Job Handler nên hướng tới:

> **Idempotency**

---

# 31. Idempotency

Ví dụ:

```text
crawl story #123
```

chạy 2 lần.

Kết quả database vẫn nên:

```text
1 story
```

thay vì:

```text
2 duplicate stories
```

Repository có thể dùng:

```sql
UNIQUE(url)
```

và:

```text
UPSERT
```

Đây là một phần cực kỳ quan trọng của crawler architecture.

---

# 32. Queue không đảm bảo business correctness

Queue chỉ đảm bảo:

```text
Job delivery
```

Nó không đảm bảo:

```text
Story không duplicate
Chapter đúng thứ tự
Parser đúng
Domain invariant đúng
```

Các vấn đề đó thuộc các tầng khác.

---

# 33. Queue + Repository

Architecture:

```text
Queue
 ↓
Worker
 ↓
Use Case
 ↓
Repository
```

Nếu Job chạy lại:

```text
Use Case
 ↓
Repository
 ↓
UPSERT
```

Domain/application vẫn chịu trách nhiệm business behavior.

---

# 34. Queue + Crawler

Không nên:

```text
Queue
 ↓
Crawler
 ↓
Database
```

Tốt hơn:

```text
Queue
 ↓
Worker
 ↓
JobHandler
 ↓
Use Case
 ↓
Crawler
 ↓
Repository
```

Worker không biết business logic.

---

# 35. DIP ở đây cực kỳ rõ

High-level:

```text
CrawlStory
```

không phụ thuộc:

```text
Redis
```

Nó phụ thuộc:

```text
JobQueue
Crawler
Repository
```

Infrastructure:

```text
RedisJobQueue
HttpxAsyncClient
SQLiteRepository
```

phụ thuộc abstraction.

---

# 36. ISP

Không tạo:

```python
class QueueInterface:

    enqueue()
    dequeue()
    retry()
    ack()
    delete()
    purge()
    inspect()
    metrics()
    shutdown()
```

Nếu Producer chỉ cần:

```python
enqueue()
```

thì interface nên nhỏ:

```python
class JobProducer(Protocol):

    async def enqueue(
        self,
        job,
    ) -> None:
        ...
```

Worker cần:

```python
class JobConsumer(Protocol):

    async def dequeue(self):
        ...

    async def ack(self, job):
        ...
```

Đây là ISP.

---

# 37. Producer và Consumer

Architecture tốt:

```text
Producer
   ↓
JobProducer
   ↓
Queue
   ↑
JobConsumer
   ↑
Worker
```

Producer không cần biết:

```text
dequeue
ack
retry
```

Worker không cần biết:

```text
CLI
submit command
```

---

# 38. Worker abstraction

Ta có thể định nghĩa:

```python
class JobHandler(Protocol):

    async def handle(
        self,
        job,
    ) -> None:
        ...
```

Worker:

```python
class Worker:

    def __init__(
        self,
        consumer,
        handler,
    ):
        self.consumer = consumer
        self.handler = handler
```

Worker generic.

---

# 39. Worker không biết CrawlStory

Đây là điểm rất đẹp.

Worker có thể xử lý:

```text
CrawlStoryJob
DownloadImageJob
GenerateAudioJob
SendNotificationJob
```

Miễn là có handler.

```text
Worker
 ↓
JobRouter
 ├── CrawlStoryHandler
 ├── DownloadImageHandler
 └── NotifyHandler
```

Đây là OCP.

---

# 40. Job Router

```python
class JobRouter:

    def __init__(self, handlers):
        self.handlers = handlers

    async def handle(self, job):

        handler = self.handlers[
            job.type
        ]

        return await handler.handle(
            job
        )
```

Registry:

```python
handlers = {
    "crawl_story": CrawlStoryJobHandler(
        crawl_story
    ),
}
```

Thêm Job type:

```text
download_image
```

chỉ cần:

```python
handlers[
    "download_image"
] = DownloadImageHandler(...)
```

Không sửa Worker.

OCP.

---

# 41. Architecture hoàn chỉnh

```text
                         CLI
                          │
                          ▼
                     Producer
                          │
                          ▼
                  ┌───────────────┐
                  │     Queue     │
                  │ Redis / Memory│
                  └───────┬───────┘
                          │
                          ▼
                       Worker
                          │
                          ▼
                     Job Router
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      CrawlStoryHandler         OtherHandler
             │
             ▼
        CrawlStory
             │
       ┌─────┴─────┐
       ▼           ▼
   Crawler      Repository
       │             │
       ▼             ▼
  Async HTTP      SQLite
```

---

# 42. Test Architecture

Điều hay nhất là ta vẫn test được từng tầng.

### Queue

```text
InMemoryQueue
```

test:

```text
enqueue
 ↓
dequeue
```

### Worker

```text
FakeConsumer
FakeHandler
```

test:

```text
job
 ↓
handler
```

### Application

```text
FakeCrawler
FakeRepository
```

### Crawler

```text
FakeHTTP
Real Parser
```

### Repository

```text
SQLite :memory:
```

---

# 43. Worker Test

Ví dụ:

```python
class FakeHandler:

    def __init__(self):
        self.jobs = []

    async def handle(self, job):
        self.jobs.append(job)
```

Test:

```python
async def test_worker():

    queue = InMemoryJobQueue()

    handler = FakeHandler()

    job = CrawlStoryJob(
        url="https://example.com"
    )

    await queue.enqueue(job)
```

Sau đó Worker lấy Job.

Test cần có cơ chế shutdown để không chạy infinite loop.

---

# 44. Worker cần graceful shutdown

Đây là production concern.

Không nên chỉ:

```python
while True:
```

Mà nên hỗ trợ:

```text
START
 ↓
RUNNING
 ↓
STOP REQUEST
 ↓
finish current job
 ↓
SHUTDOWN
```

Ví dụ:

```python
self._running = True
```

và:

```python
async def stop(self):
    self._running = False
```

Nhưng thực tế cần xử lý task đang block trên `dequeue()`; có thể dùng cancellation hoặc sentinel tùy queue implementation.

---

# 45. Cancellation

Khi shutdown:

```python
worker_task.cancel()
```

Worker:

```python
try:
    ...
except asyncio.CancelledError:
    raise
```

Không nên:

```python
except Exception:
    pass
```

vì cancellation cần được truyền đi đúng cách.

---

# 46. Backpressure

Giả sử Producer:

```text
100,000 jobs/sec
```

nhưng Worker chỉ xử lý:

```text
100 jobs/sec
```

Queue sẽ phình to.

Đó là:

> Backpressure problem.

Các giải pháp:

```text
bounded queue
rate limiting
producer throttling
worker scaling
batching
```

---

# 47. Async Crawler + Queue

Ta có hai cấp concurrency:

```text
Queue
 ↓
Workers
 ↓
AsyncCrawler
 ↓
HTTP concurrency
```

Ví dụ:

```text
5 Workers
×
10 HTTP requests
```

có thể tạo khoảng:

```text
50 concurrent HTTP operations
```

Không nên vô tình tăng lên hàng trăm/hàng nghìn.

---

# 48. Quy tắc thiết kế

Tôi khuyên architecture ban đầu:

```text
1 Worker
 ↓
AsyncCrawler
 ↓
Semaphore(10)
```

Sau đó benchmark.

Nếu cần scale:

```text
2 Workers
 ↓
Semaphore(10)
```

Nếu vẫn chưa đủ:

```text
5 Workers
 ↓
Semaphore(10)
```

Scale dựa trên measurement, không đoán.

---

# 49. Queue + SOLID tổng hợp

### SRP

```text
Job
Producer
Queue
Worker
Router
Handler
Crawler
Repository
```

mỗi component có responsibility rõ.

### OCP

Thêm:

```text
JobHandler
Crawler Plugin
Queue implementation
```

không sửa core.

### LSP

```text
RedisQueue
InMemoryQueue
```

phải đáp ứng contract.

### ISP

```text
Producer
Consumer
Handler
```

interface nhỏ.

### DIP

```text
Application
 ↓
Abstractions
 ↑
Infrastructure
```

---

# 50. Bài tập Buổi 28

## Bài 1

Tạo:

```python
@dataclass(frozen=True)
class CrawlStoryJob:
    url: str
```

---

## Bài 2

Tạo:

```python
class JobProducer(Protocol):

    async def enqueue(self, job):
        ...
```

---

## Bài 3

Implement:

```text
InMemoryJobQueue
```

bằng:

```text
asyncio.Queue
```

---

## Bài 4

Tạo:

```text
CrawlStoryJobHandler
```

Handler gọi:

```text
CrawlStory Use Case
```

---

## Bài 5

Tạo:

```text
Worker
```

với:

```text
Queue
 ↓
Job
 ↓
Handler
```

---

## Bài 6

Tạo:

```text
JobRouter
```

hỗ trợ:

```text
crawl_story
```

---

# 51. Challenge lớn

Xây flow hoàn chỉnh:

```text
$ crawler crawl URL
```

↓

```text
CrawlStoryJob
```

↓

```text
JobQueue
```

↓

```text
Worker
```

↓

```text
JobRouter
```

↓

```text
CrawlStoryHandler
```

↓

```text
CrawlStory
```

↓

```text
AsyncCrawler
```

↓

```text
HTTP
```

↓

```text
Parser
```

↓

```text
Story
```

↓

```text
Repository
```

↓

```text
SQLite
```

---

# 52. Production architecture

Sau Buổi 28, project của chúng ta đã tiến tới:

```text
                         ┌──────────┐
                         │   CLI    │
                         └────┬─────┘
                              │
                              ▼
                         ┌─────────┐
                         │Producer │
                         └────┬────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Job Queue      │
                    │ Redis / Memory   │
                    └────────┬─────────┘
                             │
                  ┌──────────┼──────────┐
                  ▼          ▼          ▼
              Worker 1   Worker 2   Worker 3
                  │          │          │
                  └──────────┼──────────┘
                             ▼
                         Job Router
                             │
                             ▼
                       Use Case
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
              AsyncCrawler        Repository
                   │                   │
                   ▼                   ▼
              HTTP Client            SQLite
```

Đây chính là nền móng rất tốt cho một **production-style Story Crawler Framework**.

---

# 53. Điểm cần nhớ nhất

Nếu chỉ nhớ 6 câu của Buổi 28:

> **1. Job là dữ liệu mô tả công việc.**

> **2. Queue lưu và phân phối Job.**

> **3. Worker thực thi Job.**

> **4. Handler chứa logic xử lý loại Job cụ thể.**

> **5. Crawler không phải Worker.**

> **6. Queue không nên xâm nhập vào Domain/Application logic.**

Và architecture quan trọng nhất:

```text
Queue
 ↓
Worker
 ↓
Handler
 ↓
Use Case
 ↓
Domain / Ports
 ↓
Infrastructure
```

Đây là nền tảng để sang bước tiếp theo: **thiết kế Queue + Worker thực sự với Redis**, bao gồm **ACK, retry, visibility timeout, dead-letter queue, job status, idempotency và graceful shutdown**.
