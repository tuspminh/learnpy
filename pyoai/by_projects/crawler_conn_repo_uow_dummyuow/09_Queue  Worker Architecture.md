# Buổi 9 — Queue + Worker Architecture

Ở Buổi 8, chúng ta đã có:

```text
ChapterCrawlState
    │
    ├── pending
    ├── crawling
    ├── completed
    └── failed
```

và hiểu:

```text
Idempotency
Atomic Claim
Transaction
Crash Recovery
```

Hôm nay chúng ta đưa **Queue + Worker** vào kiến trúc.

Mục tiêu cuối buổi:

```text
                Crawler
                   │
                   ▼
              Create Jobs
                   │
                   ▼
                 Queue
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Worker 1   Worker 2   Worker 3
        │          │          │
        └──────────┼──────────┘
                   ▼
              Application
                   │
                   ▼
                  UoW
                   │
                   ▼
                SQLite
```

---

# 1. Queue thực sự giải quyết vấn đề gì?

Không có Queue:

```text
Crawler
   │
   ├── crawl chapter 1
   ├── crawl chapter 2
   ├── crawl chapter 3
   ├── crawl chapter 4
   └── ...
```

Crawler phải tự làm tất cả.

Nếu Chapter 3:

```text
timeout
```

thì flow có thể bị ảnh hưởng.

---

Có Queue:

```text
Crawler
   │
   ▼
Queue
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── Chapter 4
 └── Chapter 5
```

Worker:

```text
Worker 1 → Chapter 1
Worker 2 → Chapter 2
Worker 3 → Chapter 3
```

Crawler và Worker được tách khỏi nhau.

---

# 2. Queue không phải là Worker

Đây là distinction rất quan trọng.

## Queue

Có nhiệm vụ:

```text
enqueue
dequeue
ack
retry/requeue
```

## Worker

Có nhiệm vụ:

```text
nhận Job
→ xử lý Job
→ báo success/failure
```

Kiến trúc:

```text
             Queue
          ┌────┴────┐
          │         │
       enqueue    dequeue
          │         │
          ▼         ▼
       Producer   Worker
```

---

# 3. Producer

Producer tạo Job.

Ví dụ:

```python
job = CrawlChapterJob(
    novel_id=10,
    chapter_number=501,
    url="https://example.com/chapter-501",
)
```

rồi:

```python
queue.enqueue(job)
```

Producer không crawl.

Nó chỉ:

```text
Discover work
      ↓
Create Job
      ↓
Enqueue
```

---

# 4. Worker

Worker:

```python
while True:
    job = queue.dequeue()

    if job is None:
        continue

    process(job)
```

Nhưng production worker không đơn giản như vậy.

Ta cần:

```text
dequeue
   ↓
process
   ↓
success → ACK
   ↓
failure → retry
   ↓
max retry → DLQ
```

---

# 5. Job

Chúng ta đã có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlChapterJob:
    novel_id: int
    chapter_number: int
    url: str
```

Tôi khuyên Job **không chứa quá nhiều dữ liệu**.

Không nên:

```python
@dataclass
class Job:
    novel: Novel
    chapter: Chapter
    html: str
    parser: ...
```

Queue chỉ nên vận chuyển thông tin cần thiết để worker tìm và xử lý công việc.

Ví dụ:

```text
novel_id
chapter_number
url
```

là đủ.

---

# 6. Job ID

Production system nên có:

```python
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CrawlChapterJob:
    job_id: UUID
    novel_id: int
    chapter_number: int
    url: str
```

Tạo:

```python
job = CrawlChapterJob(
    job_id=uuid4(),
    novel_id=10,
    chapter_number=501,
    url="...",
)
```

Job có identity riêng.

---

# 7. Queue Interface

Đây là điểm quan trọng với Clean Architecture.

**Application không được phụ thuộc Redis/RQ/Celery.**

Ta định nghĩa abstraction:

```python
from abc import ABC, abstractmethod


class JobQueue(ABC):

    @abstractmethod
    def enqueue(self, job) -> None:
        ...

    @abstractmethod
    def dequeue(self):
        ...

    @abstractmethod
    def ack(self, job) -> None:
        ...

    @abstractmethod
    def reject(self, job) -> None:
        ...
```

Sau này có thể có:

```text
JobQueue
   ↑
   ├── InMemoryJobQueue
   ├── SQLiteJobQueue
   ├── RedisJobQueue
   └── RQJobQueue
```

Application chỉ biết:

```text
JobQueue
```

---

# 8. Tại sao không import Redis trong Application?

Không nên:

```python
# application/
import redis
```

vì Application lúc này biết:

```text
Redis
```

và trở thành infrastructure-dependent.

Thay vào đó:

```text
Application
     │
     ▼
 JobQueue interface
     ▲
     │
RedisJobQueue
```

Dependency direction:

```text
Infrastructure
      │
      ▼
 Application abstraction
```

---

# 9. In-Memory Queue

Để test, chúng ta tạo:

```python
from queue import Queue


class InMemoryJobQueue:

    def __init__(self):
        self._queue = Queue()

    def enqueue(self, job):
        self._queue.put(job)

    def dequeue(self):
        return self._queue.get()

    def ack(self, job):
        self._queue.task_done()

    def reject(self, job):
        self._queue.task_done()
```

Đây là queue rất đơn giản.

Nó hữu ích cho:

```text
unit test
local development
prototype
```

---

# 10. Producer Use Case

Ta không muốn CLI tự:

```python
queue.put(...)
```

Thay vào đó:

```python
class EnqueueChapterCrawl:

    def __init__(self, queue):
        self.queue = queue

    def execute(
        self,
        novel_id: int,
        chapter_number: int,
        url: str,
    ):

        job = CrawlChapterJob(
            job_id=uuid4(),
            novel_id=novel_id,
            chapter_number=chapter_number,
            url=url,
        )

        self.queue.enqueue(job)

        return job
```

Flow:

```text
CLI
 ↓
EnqueueChapterCrawl
 ↓
JobQueue
 ↓
Queue
```

---

# 11. Worker không nên chứa Business Logic

Một Worker tốt:

```text
Worker
   │
   ├── lấy Job
   │
   ├── gọi Application
   │
   └── ACK / Retry
```

Không nên:

```python
class Worker:

    def process(self, job):
        conn = sqlite3.connect(...)
        ...
        conn.execute(...)
        conn.commit()
```

Worker như vậy đã biến thành:

```text
Worker
 + SQL
 + Transaction
 + Business logic
 + HTTP
 + Parser
```

→ rất khó test.

---

# 12. Chapter Crawler Service

Ta tách fetch:

```python
class ChapterCrawler:

    def fetch(
        self,
        job: CrawlChapterJob,
    ) -> Chapter:

        ...
```

Worker:

```python
class ChapterWorker:

    def __init__(
        self,
        crawler,
        save_chapter,
    ):
        self.crawler = crawler
        self.save_chapter = save_chapter

    def process(self, job):

        chapter = self.crawler.fetch(job)

        self.save_chapter.execute(chapter)
```

Rất rõ:

```text
Worker
  ↓
Crawler
  ↓
Chapter
  ↓
SaveChapter UseCase
  ↓
UoW
```

---

# 13. Worker Loop

Ta tạo:

```python
class Worker:

    def __init__(
        self,
        queue,
        processor,
    ):
        self.queue = queue
        self.processor = processor

    def run(self):

        while True:

            job = self.queue.dequeue()

            try:
                self.processor.process(job)

            except Exception:
                self.queue.reject(job)

            else:
                self.queue.ack(job)
```

Đây mới chỉ là skeleton.

Chúng ta sẽ cải tiến nó rất nhiều.

---

# 14. ACK là gì?

ACK:

> Acknowledgement

Worker nói với Queue:

```text
"Tôi đã xử lý Job thành công."
```

Flow:

```text
Queue
  ↓
Worker
  ↓
process
  ↓
success
  ↓
ACK
```

Sau ACK:

```text
Job
  ↓
removed
```

---

# 15. Tại sao không ACK trước khi process?

Sai:

```text
dequeue
 ↓
ACK
 ↓
process
 ↓
CRASH
```

Job đã biến mất.

Database:

```text
Chapter chưa lưu
```

Queue:

```text
Job cũng mất
```

→ mất work.

---

# 16. ACK phải sau transaction

Đây là một nguyên tắc cực kỳ quan trọng:

```text
Job
 ↓
Process
 ↓
DB Transaction
 ↓
COMMIT
 ↓
ACK
```

Không phải:

```text
Job
 ↓
ACK
 ↓
DB Transaction
```

Tức là:

> **ACK chỉ nên xảy ra sau khi side effect chính đã thành công.**

---

# 17. Failure

Nếu:

```text
process
  ↓
exception
```

không ACK.

Ta có thể:

```text
reject
   ↓
requeue
```

Ví dụ:

```text
Job 501
   ↓
Worker
   ↓
HTTP Timeout
   ↓
Retry
```

---

# 18. Retry Count

Job nên có:

```python
@dataclass(frozen=True)
class CrawlChapterJob:
    job_id: UUID
    novel_id: int
    chapter_number: int
    url: str
    retry_count: int = 0
```

Nếu lỗi:

```text
retry_count += 1
```

Ví dụ:

```text
attempt 1 → failed
attempt 2 → failed
attempt 3 → failed
attempt 4 → stop
```

---

# 19. Retry Policy

Tách riêng:

```python
class RetryPolicy:

    def __init__(
        self,
        max_retries: int = 3,
    ):
        self.max_retries = max_retries

    def should_retry(
        self,
        retry_count: int,
    ) -> bool:

        return retry_count < self.max_retries
```

Worker:

```text
Worker
   │
   ▼
Exception
   │
   ▼
RetryPolicy
   │
   ├── yes → requeue
   │
   └── no  → DLQ
```

---

# 20. Dead Letter Queue

DLQ = Dead Letter Queue.

Nếu Job lỗi quá nhiều:

```text
retry 1
retry 2
retry 3
retry 4
...
```

không được retry vô hạn.

Ta chuyển:

```text
Main Queue
     │
     ▼
 retry limit
     │
     ▼
    DLQ
```

Ví dụ:

```text
DLQ
 ├── chapter 103
 ├── chapter 205
 └── chapter 998
```

Sau đó admin có thể kiểm tra.

---

# 21. Tại sao DLQ rất quan trọng?

Ví dụ Chapter 500 có HTML bất thường:

```text
ParserError
```

Nếu cứ retry:

```text
500
500
500
500
500
...
```

worker bị chiếm.

DLQ giúp:

```text
retry vài lần
     ↓
không thành công
     ↓
DLQ
     ↓
worker tiếp tục job khác
```

---

# 22. Retry không nên retry mọi Exception

Đây là một lỗi thiết kế phổ biến.

Ví dụ:

```text
HTTP timeout
```

có thể retry.

Nhưng:

```text
Parser bug
```

thường không nên retry nhiều lần.

Hoặc:

```text
404 Not Found
```

retry có thể vô nghĩa.

Ta cần phân loại lỗi:

```text
Transient Error
Permanent Error
```

---

# 23. Transient Error

Ví dụ:

```text
timeout
connection reset
502
503
429
```

Có thể retry.

---

# 24. Permanent Error

Ví dụ:

```text
404
invalid chapter
malformed source
parser error
```

thường nên:

```text
FAILED
→ DLQ
```

hoặc cần manual review.

---

# 25. Retry Policy tốt hơn

Ví dụ:

```python
class RetryPolicy:

    RETRYABLE = (
        TimeoutError,
        ConnectionError,
    )

    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def should_retry(
        self,
        error: Exception,
        retry_count: int,
    ) -> bool:

        if retry_count >= self.max_retries:
            return False

        return isinstance(
            error,
            self.RETRYABLE,
        )
```

Production sẽ phức tạp hơn, nhưng nguyên tắc là:

```text
Retry Policy
    ↓
error classification
    +
retry count
```

---

# 26. Exponential Backoff

Không nên:

```text
retry
retry
retry
retry
```

ngay lập tức.

Có thể:

```text
attempt 1 → wait 1s
attempt 2 → wait 2s
attempt 3 → wait 4s
attempt 4 → wait 8s
```

Công thức:

```text
delay = base * 2^retry_count
```

Ví dụ:

```python
def backoff(
    retry_count: int,
    base: float = 1.0,
) -> float:

    return base * (2 ** retry_count)
```

Thực tế thường thêm **jitter** để nhiều worker không retry cùng lúc.

---

# 27. Queue/Worker Boundary

Đây là boundary chúng ta muốn:

```text
             Application
                  │
                  ▼
              JobQueue
                  ▲
                  │
         ┌────────┴────────┐
         │                 │
 InMemoryJobQueue     RedisJobQueue
```

Worker:

```text
         Worker
           │
           ▼
        JobQueue
           │
           ▼
          Job
           │
           ▼
     Application UseCase
```

Application không cần biết queue implementation.

---

# 28. Worker và UoW

Worker:

```python
class ChapterWorker:

    def process(self, job):

        chapter = self.crawler.fetch(job)

        self.save_chapter.execute(
            chapter
        )
```

`save_chapter`:

```text
Use Case
   ↓
UoW
   ↓
BEGIN
   ├── UPSERT chapter
   └── update state
   ↓
COMMIT
```

Sau đó Worker:

```text
COMMIT
 ↓
ACK
```

Flow hoàn chỉnh:

```text
Queue
 ↓
Worker
 ↓
Fetch
 ↓
Parse
 ↓
Use Case
 ↓
UoW
 ↓
COMMIT
 ↓
ACK
```

---

# 29. Crash ở đâu?

## Crash trước commit

```text
Fetch
 ↓
Parse
 ↓
DB
 ↓
CRASH
 ↓
ROLLBACK
```

Không ACK.

Job được retry.

---

## Crash sau commit nhưng trước ACK

```text
DB
 ↓
COMMIT ✓
 ↓
CRASH
 ↓
ACK ✗
```

Job được xử lý lại.

Nhưng:

```text
UPSERT
```

đảm bảo không tạo duplicate.

Đây chính là:

# At-Least-Once Processing

---

# 30. At-Least-Once

Job có thể được xử lý:

```text
1 lần
```

hoặc:

```text
2 lần
```

hoặc:

```text
3 lần
```

Nhưng hệ thống đảm bảo:

> Job không dễ dàng bị mất nếu worker crash trước ACK.

Do đó Application phải có:

```text
Idempotency
```

Đây là lý do Buổi 6 chúng ta học UPSERT.

---

# 31. At-Most-Once

Ngược lại:

```text
ACK
 ↓
process
```

Nếu process crash:

```text
Job mất
```

→ At-Most-Once.

Ưu:

```text
ít duplicate
```

Nhược:

```text
có thể mất job
```

Crawler thường ưu tiên:

```text
At-Least-Once
+
Idempotent processing
```

---

# 32. Exactly-Once?

Rất nhiều hệ thống nói:

```text
exactly once
```

nhưng thực tế phải cực kỳ cẩn thận.

Với:

```text
Queue
+
Network
+
Database
+
Worker
```

"exactly once" end-to-end rất khó.

Thực tế thường thiết kế:

```text
At-Least-Once Delivery
        +
Idempotent Consumer
```

→ đạt được hiệu ứng gần với exactly-once cho business operation.

Đây là tư duy production rất quan trọng.

---

# 33. Idempotent Consumer

Worker nhận:

```text
Job 123
```

hai lần:

```text
Worker A → Job 123
Worker B → Job 123
```

Application vẫn phải đảm bảo:

```text
database final state
```

đúng.

Ví dụ:

```sql
UNIQUE(novel_id, chapter_number)
```

và:

```sql
UPSERT
```

giúp bảo vệ dữ liệu.

---

# 34. Job Status và Chapter Status khác nhau

Đừng nhầm:

```text
Job Status
```

với:

```text
Chapter Crawl Status
```

Job:

```text
queued
processing
acked
failed
dead
```

Chapter:

```text
pending
crawling
completed
failed
```

Hai lifecycle khác nhau.

Ví dụ:

```text
Job
   ↓
processing
   ↓
Worker crash
   ↓
Job retry

Chapter state
   ↓
crawling
   ↓
stale
   ↓
pending
```

---

# 35. Một Job không nhất thiết = một Chapter forever

Ví dụ:

```text
CrawlNovelJob
```

có thể tạo:

```text
CrawlChapterJob 1
CrawlChapterJob 2
...
CrawlChapterJob 1000
```

Flow:

```text
CrawlNovel
    ↓
discover chapters
    ↓
create jobs
    ↓
Queue
```

Sau đó worker:

```text
CrawlChapterJob
```

xử lý từng chapter.

Đây là decomposition rất tốt.

---

# 36. Composition Root

Cuối cùng ta nối các implementation:

```python
connection_manager = SQLiteConnectionManager(
    "data/novels.db"
)

uow = SQLiteUnitOfWork(
    connection_manager
)

queue = InMemoryJobQueue()

crawler = ChapterCrawler(...)

save_chapter = SaveChapter(uow)

worker = ChapterWorker(
    crawler=crawler,
    save_chapter=save_chapter,
)
```

Trong production:

```text
InMemoryJobQueue
```

có thể thay:

```text
RedisJobQueue
```

mà Application không đổi.

---

# 37. Toàn bộ kiến trúc hiện tại

```text
                         CLI
                          │
                          ▼
                  Application Layer
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       EnqueueChapter             CrawlChapter
             │                         │
             ▼                         ▼
         JobQueue                   Worker
             │                         │
             ▼                         ▼
           Queue                    Crawler
                                       │
                                       ▼
                                    Chapter
                                       │
                                       ▼
                                  SaveChapter
                                       │
                                       ▼
                                      UoW
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                      Novel         Chapter      CrawlState
                       Repo           Repo           Repo
                                      │
                                      ▼
                               ChapterCrawlState
                                      │
                                      ▼
                                    SQLite
```

---

# 38. Một nguyên tắc kiến trúc cực quan trọng

**Queue không được trở thành trung tâm business logic.**

Không nên:

```text
Queue
 ├── validate chapter
 ├── parse HTML
 ├── update database
 ├── retry business logic
 └── calculate crawl state
```

Queue chỉ:

```text
transport work
```

Worker chỉ:

```text
orchestrate execution
```

Application:

```text
business workflow
```

Domain:

```text
business rules
```

Repository:

```text
persistence
```

---

# 39. Phân chia trách nhiệm

| Component   | Trách nhiệm              |
| ----------- | ------------------------ |
| Job         | Mô tả công việc          |
| Queue       | Vận chuyển công việc     |
| Producer    | Tạo Job                  |
| Worker      | Thực thi Job             |
| RetryPolicy | Quyết định retry         |
| DLQ         | Giữ job thất bại lâu dài |
| Use Case    | Business workflow        |
| UoW         | Transaction              |
| Repository  | Persistence              |
| Domain      | Business rules           |

Đây là boundary mà chúng ta cần giữ rất chặt.

---

# 40. Bài tập Buổi 9

### Bài 1 — InMemory Queue

Implement:

```python
JobQueue
InMemoryJobQueue
```

với:

```text
enqueue()
dequeue()
ack()
reject()
```

---

### Bài 2 — Producer

Implement:

```python
EnqueueChapterCrawl
```

input:

```text
novel_id
chapter_number
url
```

output:

```text
CrawlChapterJob
```

---

### Bài 3 — Worker

Implement:

```python
ChapterWorker
```

flow:

```text
dequeue
 ↓
process
 ↓
success → ack
 ↓
error → retry/reject
```

---

### Bài 4 — Retry

Implement:

```python
RetryPolicy
```

với:

```text
max_retries = 3
```

và chỉ retry:

```text
TimeoutError
ConnectionError
```

---

### Bài 5 — DLQ

Thiết kế:

```text
Main Queue
    │
    ├── success → ACK
    │
    ├── retryable → Retry
    │
    └── max retry → DLQ
```

---

# 41. Bài tập quan trọng nhất

Mô phỏng tình huống:

```text
Job 501
   ↓
Worker
   ↓
fetch
   ↓
save chapter
   ↓
COMMIT ✓
   ↓
CRASH
   ↓
ACK ✗
```

Sau đó Job 501 được xử lý lại.

Hãy chứng minh database cuối cùng chỉ có:

```text
Novel 10
Chapter 501
```

chứ không có:

```text
Chapter 501
Chapter 501
```

Đây là bài tập giúp bạn thực sự hiểu:

```text
At-Least-Once
        +
Idempotency
        +
UPSERT
```

---

# 42. Kiến thức cốt lõi của Buổi 9

Hãy ghi nhớ flow này:

```text
              PRODUCER
                  │
                  ▼
                QUEUE
                  │
                  ▼
                WORKER
                  │
                  ▼
             APPLICATION
                  │
                  ▼
                 UoW
                  │
                  ▼
               SQLite
                  │
               COMMIT
                  │
                  ▼
                 ACK
```

Nếu lỗi:

```text
                 WORKER
                    │
                    ▼
                 ERROR
                    │
              ┌─────┴─────┐
              ▼           ▼
           RETRY          DLQ
```

Và nguyên tắc quan trọng nhất:

> **COMMIT trước, ACK sau.**

Kết hợp với Buổi 6:

> **ACK có thể xảy ra nhiều lần, vì vậy persistence operation phải idempotent.**

Kết hợp với Buổi 8:

> **Worker phải claim công việc một cách atomic để tránh hai worker cùng xử lý một Chapter.**

Đây chính là nền móng để Buổi 10 đi sâu vào **Worker Lifecycle + Graceful Shutdown + Cancellation + Heartbeat + Lease/Visibility Timeout** — đặc biệt quan trọng nếu worker crawl truyện chạy hàng giờ và phải xử lý `SIGTERM`, crash, timeout hoặc restart mà không để chapter bị kẹt ở `crawling`.
