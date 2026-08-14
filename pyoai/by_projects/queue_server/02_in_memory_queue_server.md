# Buổi 2 — Xây In-Memory Queue Server

Hôm nay chúng ta bắt đầu **code Queue Server thật**, nhưng chưa dùng TCP, SQLite hay Redis.

Mục tiêu là hiểu thật chắc **cơ chế bên trong của queue** trước khi đưa nó lên network.

---

# 1. Kiến trúc Buổi 2

Ta xây 3 thành phần:

```text
Producer
    │
    │ enqueue()
    ▼
┌──────────────────┐
│  InMemoryQueue   │
│                  │
│ pending          │
│ reserved         │
│ completed        │
└────────┬─────────┘
         │
         │ reserve()
         ▼
      Worker
         │
         │
     ┌───┴────┐
     │        │
    ack      fail
     │        │
     ▼        ▼
 completed   pending
```

Điểm quan trọng:

> `reserve()` **không xóa job khỏi hệ thống**.

Nó chuyển job:

```text
PENDING
   ↓
RUNNING
```

Sau đó worker:

```text
RUNNING
   ↓
ACK
   ↓
COMPLETED
```

Nếu worker thất bại:

```text
RUNNING
   ↓
FAIL
   ↓
PENDING
```

---

# 2. Job Model

Trước tiên tạo `Job`.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class Job:
    queue: str
    payload: Any

    id: str = field(default_factory=lambda: str(uuid4()))

    status: str = "pending"

    attempts: int = 0

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

Ví dụ:

```python
job = Job(
    queue="chapter",
    payload={
        "url": "https://example.com/chapter/1",
        "book_id": 10,
    },
)
```

Job sẽ giống:

```text
Job
├── id
├── queue
├── payload
├── status
├── attempts
└── created_at
```

---

# 3. Vì sao dùng `dataclass`?

Thay vì:

```python
class Job:
    def __init__(
        self,
        queue,
        payload,
        id,
        status,
        attempts,
        created_at,
    ):
        ...
```

`dataclass` giúp chúng ta tập trung vào **data model**.

Đây cũng phù hợp với architecture mà bạn đang học về:

```text
Model
Repository
Database Manager
Worker
```

Sau này `Job` có thể trở thành domain model dùng chung cho:

```text
Queue Server
    │
    ├── SQLite Repository
    │
    ├── Queue Client
    │
    └── Crawl Worker
```

---

# 4. Queue cơ bản

Bây giờ xây:

```python
from collections import deque


class InMemoryQueue:
    def __init__(self):
        self._pending = deque()
        self._running = {}
        self._completed = {}
```

Ta có:

```text
_pending

┌────────┬────────┬────────┐
│ Job 1  │ Job 2  │ Job 3  │
└────────┴────────┴────────┘


_running

{
    job_id: Job
}


_completed

{
    job_id: Job
}
```

---

# 5. enqueue()

```python
def enqueue(self, job: Job) -> str:
    job.status = "pending"

    self._pending.append(job)

    return job.id
```

Hoàn chỉnh:

```python
class InMemoryQueue:
    def __init__(self):
        self._pending = deque()
        self._running = {}
        self._completed = {}

    def enqueue(self, job: Job) -> str:
        job.status = "pending"

        self._pending.append(job)

        return job.id
```

Sử dụng:

```python
queue = InMemoryQueue()

job = Job(
    queue="chapter",
    payload={
        "url": "https://example.com/chapter/1"
    }
)

job_id = queue.enqueue(job)

print(job_id)
```

---

# 6. reserve()

Đây là phần quan trọng nhất.

Ta **không làm**:

```python
job = self._pending.popleft()
```

rồi bỏ job đi.

Thay vào đó:

```python
def reserve(self):
    if not self._pending:
        return None

    job = self._pending.popleft()

    job.status = "running"
    job.attempts += 1

    self._running[job.id] = job

    return job
```

Toàn bộ flow:

```text
_pending
   │
   │ popleft()
   ▼
 Job
   │
   ├── status = running
   ├── attempts += 1
   │
   ▼
_running[job.id]
```

---

# 7. ACK

Worker crawl thành công:

```python
def ack(self, job_id: str) -> bool:
    job = self._running.pop(job_id, None)

    if job is None:
        return False

    job.status = "completed"

    self._completed[job.id] = job

    return True
```

Flow:

```text
RUNNING
   │
   │ ack()
   ▼
COMPLETED
```

---

# 8. FAIL

Nếu crawl thất bại, tạm thời đưa job về queue:

```python
def fail(self, job_id: str) -> bool:
    job = self._running.pop(job_id, None)

    if job is None:
        return False

    job.status = "pending"

    self._pending.append(job)

    return True
```

Flow:

```text
RUNNING
   │
   │ fail()
   ▼
PENDING
```

**Lưu ý:** đây mới chỉ là retry cơ bản.

Buổi sau chúng ta sẽ xây:

```text
attempts
max_attempts
retry_delay
backoff
```

---

# 9. Queue hoàn chỉnh phiên bản 1

```python
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class Job:
    queue: str
    payload: Any

    id: str = field(default_factory=lambda: str(uuid4()))

    status: str = "pending"

    attempts: int = 0

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class InMemoryQueue:

    def __init__(self):
        self._pending = deque()
        self._running = {}
        self._completed = {}

    def enqueue(self, job: Job) -> str:
        job.status = "pending"

        self._pending.append(job)

        return job.id

    def reserve(self) -> Job | None:
        if not self._pending:
            return None

        job = self._pending.popleft()

        job.status = "running"
        job.attempts += 1

        self._running[job.id] = job

        return job

    def ack(self, job_id: str) -> bool:
        job = self._running.pop(job_id, None)

        if job is None:
            return False

        job.status = "completed"

        self._completed[job.id] = job

        return True

    def fail(self, job_id: str) -> bool:
        job = self._running.pop(job_id, None)

        if job is None:
            return False

        job.status = "pending"

        self._pending.append(job)

        return True
```

---

# 10. Test Queue

Tạo:

```python
queue = InMemoryQueue()
```

Thêm 3 jobs:

```python
for i in range(3):
    job = Job(
        queue="chapter",
        payload={
            "url": f"https://example.com/chapter/{i + 1}"
        },
    )

    queue.enqueue(job)
```

Trạng thái:

```text
pending:

Job 1
Job 2
Job 3
```

---

# 11. Worker lấy Job

```python
job = queue.reserve()

print(job)
```

Ta có:

```text
pending:

Job 2
Job 3


running:

Job 1
```

Job 1:

```python
job.status
```

→

```text
running
```

---

# 12. Worker hoàn thành

```python
queue.ack(job.id)
```

Bây giờ:

```text
pending:

Job 2
Job 3


running:

empty


completed:

Job 1
```

---

# 13. Test failure

Lấy Job 2:

```python
job = queue.reserve()

print(job.id)
```

Giả sử crawl thất bại:

```python
queue.fail(job.id)
```

Ta lại có:

```text
pending:

Job 3
Job 2
```

Đây là một vấn đề thú vị.

Job 2 được đưa **cuối queue**.

Điều này có thể phù hợp với crawler:

```text
Job 3
Job 2 retry
```

Nhưng đôi khi ta muốn retry ngay.

Đây là một quyết định về **queue semantics** mà sau này chúng ta sẽ thiết kế thành:

```text
retry_policy
```

---

# 14. Tạo Crawl Worker đơn giản

Bây giờ đưa queue vào crawler.

```python
class CrawlWorker:

    def __init__(self, queue: InMemoryQueue):
        self.queue = queue

    def run_once(self):
        job = self.queue.reserve()

        if job is None:
            return

        try:
            self.process(job)

        except Exception:
            self.queue.fail(job.id)

        else:
            self.queue.ack(job.id)

    def process(self, job: Job):
        print(
            f"Crawling: {job.payload['url']}"
        )
```

Sử dụng:

```python
queue = InMemoryQueue()

queue.enqueue(
    Job(
        queue="chapter",
        payload={
            "url": "https://example.com/chapter/1"
        },
    )
)

worker = CrawlWorker(queue)

worker.run_once()
```

Flow:

```text
             enqueue
Producer ─────────────► Queue
                         │
                         │ reserve
                         ▼
                      Worker
                         │
                         │ crawl
                         ▼
                    ┌────┴────┐
                    │         │
                  success    error
                    │         │
                   ACK       FAIL
                    │         │
                    ▼         ▼
                completed   pending
```

---

# 15. Nhưng code trên có một lỗi kiến trúc

Hiện tại:

```python
queue = InMemoryQueue()
```

được truyền trực tiếp vào worker.

Điều này khiến Worker phụ thuộc vào implementation cụ thể:

```text
CrawlWorker
    │
    ▼
InMemoryQueue
```

Chúng ta muốn:

```text
CrawlWorker
    │
    ▼
QueueClient / Queue Interface
    │
    ├── InMemoryQueue
    ├── SQLiteQueue
    └── RedisQueue
```

Đây sẽ là chủ đề quan trọng ở các buổi sau.

---

# 16. Vấn đề lớn hơn: nhiều Worker

Giả sử:

```python
worker1.run_once()
worker2.run_once()
```

Ta muốn:

```text
Job 1 → Worker 1
Job 2 → Worker 2
```

chứ không phải:

```text
Job 1 → Worker 1
Job 1 → Worker 2   ❌
```

Với một process Python đơn giản, chúng ta chưa gặp vấn đề nghiêm trọng.

Nhưng khi chuyển sang:

```text
TCP
   +
multiple clients
   +
multiple threads
   +
asyncio
```

race condition bắt đầu xuất hiện.

Ví dụ:

```text
Worker A                    Worker B
   │                           │
   │ check queue               │
   │                           │
   │           check queue     │
   │                           │
   │ pop Job 1                 │
   │                           │
   │           pop Job 1 ❌     │
```

Do đó Queue Server phải có **atomic operation**.

---

# 17. `threading.Lock`

Ngay từ bây giờ hãy hiểu concept này.

```python
from threading import Lock


class InMemoryQueue:

    def __init__(self):
        self._pending = deque()
        self._running = {}
        self._completed = {}

        self._lock = Lock()
```

`reserve()`:

```python
def reserve(self) -> Job | None:

    with self._lock:

        if not self._pending:
            return None

        job = self._pending.popleft()

        job.status = "running"
        job.attempts += 1

        self._running[job.id] = job

        return job
```

Bây giờ operation:

```text
check
 +
pop
 +
status update
 +
running insert
```

được xem như **một critical section**.

---

# 18. Tại sao Lock quan trọng?

Không có Lock:

```text
Worker A             Worker B

check queue
                     check queue

pop()
                     pop()

update
                     update
```

Có Lock:

```text
Worker A
   │
   ├── acquire
   │
   ├── check
   ├── pop
   ├── update
   │
   └── release
             │
             ▼
         Worker B
             │
             ├── acquire
             ├── check
             ├── pop
             └── release
```

Đây chính là nền tảng của **concurrency control**.

---

# 19. Queue cần những operation nào?

Đến cuối hệ thống, Queue Server của chúng ta sẽ có API gần như:

```text
enqueue()
reserve()
ack()
fail()
retry()
delete()
inspect()
stats()
```

Và sau này:

```text
pause()
resume()
clear()
```

Đối với crawler:

```text
Queue
├── novel
├── book
├── chapter
├── content
├── image
└── metadata
```

Ví dụ:

```python
queue.enqueue(
    Job(
        queue="image",
        payload={
            "url": image_url,
            "chapter_id": chapter_id,
        },
    )
)
```

---

# 20. Một điểm rất quan trọng: `reserve()` ≠ `dequeue()`

Trong các queue đơn giản:

```text
dequeue()
    ↓
remove job
```

Nhưng Queue Server đáng tin cậy:

```text
reserve()
    ↓
PENDING
    ↓
RUNNING
```

Job vẫn tồn tại.

Sau đó:

```text
ACK
 ↓
COMPLETED
```

Nếu worker chết:

```text
RUNNING
   │
   │ timeout
   ▼
PENDING
```

Đây chính là nền tảng của:

> **Reliable Job Queue**

và cũng là lý do chúng ta không nên chỉ dùng `queue.Queue` rồi nghĩ rằng đã có Redis Queue.

---

# 21. Phiên bản kiến trúc sau Buổi 2

```text
                  Producer
                      │
                      │ enqueue()
                      ▼
              ┌─────────────────┐
              │ InMemoryQueue   │
              │                 │
              │ ┌─────────────┐ │
              │ │   pending   │ │
              │ └──────┬──────┘ │
              │        │         │
              │     reserve      │
              │        ▼         │
              │ ┌─────────────┐ │
              │ │   running   │ │
              │ └──────┬──────┘ │
              │        │         │
              │       ACK        │
              │        ▼         │
              │ ┌─────────────┐ │
              │ │  completed  │ │
              │ └─────────────┘ │
              └────────┬────────┘
                       │
                 ┌─────┴─────┐
                 ▼           ▼
              Worker 1    Worker 2
```

## Những gì bạn cần nắm chắc hôm nay

| Khái niệm   | Ý nghĩa                              |
| ----------- | ------------------------------------ |
| Producer    | Đưa Job vào queue                    |
| Consumer    | Lấy Job ra xử lý                     |
| Job         | Đơn vị công việc                     |
| Pending     | Job đang chờ                         |
| Running     | Worker đang xử lý                    |
| Completed   | Xử lý thành công                     |
| `enqueue()` | Đưa job vào queue                    |
| `reserve()` | Nhận quyền xử lý job                 |
| `ack()`     | Xác nhận thành công                  |
| `fail()`    | Báo thất bại                         |
| Lock        | Bảo vệ operation khỏi race condition |

### Bài tập

Hãy tự mở rộng `InMemoryQueue` thêm:

```python
def size(self) -> int:
    ...


def running_count(self) -> int:
    ...


def completed_count(self) -> int:
    ...
```

và thêm:

```python
def get_job(self, job_id: str) -> Job | None:
    ...
```

**Buổi 3** chúng ta sẽ chuyển từ:

```text
CrawlWorker
     │
     ▼
InMemoryQueue
```

sang:

```text
CrawlWorker
     │
     │ TCP
     ▼
┌──────────────────┐
│   Queue Server   │
│                  │
│ socket server    │
│ protocol         │
│ dispatcher       │
└──────────────────┘
```

và tự xây **protocol kiểu Redis đơn giản**:

```text
ENQUEUE
RESERVE
ACK
FAIL
STATS
```

Đây là bước rất quan trọng vì từ đây Queue của bạn bắt đầu trở thành **một service độc lập**, có thể phục vụ nhiều `crawl-worker` process khác nhau.
