# Buổi 10 — Worker Lifecycle & Graceful Shutdown

Hôm nay chúng ta chuyển từ:

```text
Buổi 9
Queue + Worker Architecture
```

sang vấn đề rất quan trọng khi chạy crawler thật:

> **Worker phải khởi động, chạy, dừng và xử lý shutdown như thế nào để không làm mất Job hoặc làm hỏng trạng thái?**

---

# 1. Vấn đề của Worker hiện tại

Ở Buổi 9 ta có:

```python
class Worker:
    def __init__(self, queue, processor):
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

Vấn đề:

```text
while True:
    ...
```

Worker **không có khái niệm shutdown**.

Nếu người dùng nhấn:

```text
Ctrl+C
```

hoặc hệ thống gửi:

```text
SIGTERM
```

worker có thể bị dừng ngay giữa:

```text
fetch
parse
save
commit
ack
```

Đây là điều rất nguy hiểm.

---

# 2. Worker lifecycle

Một Worker production nên có lifecycle rõ ràng:

```text
          ┌──────────┐
          │ STARTING │
          └────┬─────┘
               ↓
          ┌──────────┐
          │ RUNNING  │
          └────┬─────┘
               │
          stop requested
               ↓
         ┌───────────┐
         │ STOPPING  │
         └─────┬─────┘
               ↓
         ┌───────────┐
         │  STOPPED  │
         └───────────┘
```

Ý nghĩa:

### STARTING

Worker:

* khởi tạo dependency
* kết nối queue
* chuẩn bị resources

### RUNNING

Worker:

```text
dequeue
   ↓
process
   ↓
ACK
   ↓
dequeue
```

### STOPPING

Worker:

> Không nhận Job mới nữa, nhưng hoàn thành Job đang xử lý.

### STOPPED

Worker:

* đóng resource
* đóng connection
* kết thúc process/thread.

---

# 3. Graceful shutdown là gì?

Có hai cách:

### Hard shutdown

```text
Worker
   ↓
đang xử lý Chapter 100
   ↓
SIGTERM
   ↓
💥 chết ngay
```

Không tốt.

---

### Graceful shutdown

```text
Worker
   ↓
đang xử lý Chapter 100
   ↓
SIGTERM
   ↓
stop accepting new jobs
   ↓
finish Chapter 100
   ↓
COMMIT
   ↓
ACK
   ↓
STOPPED
```

Đây là cách chúng ta muốn.

---

# 4. `threading.Event`

Python có một primitive rất phù hợp:

```python
threading.Event
```

Ví dụ:

```python
import threading

stop_event = threading.Event()
```

Kiểm tra:

```python
if stop_event.is_set():
    ...
```

Yêu cầu stop:

```python
stop_event.set()
```

---

# 5. Worker đầu tiên có graceful shutdown

Ta sửa Worker:

```python
import threading


class Worker:
    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            job = self.queue.dequeue()

            try:
                self.processor.process(job)
            except Exception:
                self.queue.reject(job)
            else:
                self.queue.ack(job)
```

Nhìn rất đơn giản:

```text
stop_event
     ↓
is_set()
     ↓
False → tiếp tục
True  → dừng
```

Nhưng vẫn còn một bug.

---

# 6. Bug: `dequeue()` blocking

Giả sử Queue:

```python
from queue import Queue

queue = Queue()
```

và:

```python
job = queue.get()
```

`get()` mặc định **blocking**.

Nếu Queue đang rỗng:

```text
Worker
  ↓
dequeue()
  ↓
WAIT...
```

Lúc này:

```python
worker.stop()
```

được gọi.

Nhưng Worker vẫn đang mắc ở:

```python
queue.get()
```

Nó không quay lại vòng:

```python
while not stop_event.is_set():
```

→ không shutdown được.

---

# 7. Dùng timeout

Ta sửa Queue:

```python
from queue import Queue, Empty


class InMemoryJobQueue:
    def __init__(self):
        self._queue = Queue()

    def enqueue(self, job):
        self._queue.put(job)

    def dequeue(self, timeout=1.0):
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def ack(self, job):
        self._queue.task_done()

    def reject(self, job):
        self._queue.task_done()
```

Worker:

```python
class Worker:
    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            job = self.queue.dequeue(timeout=1.0)

            if job is None:
                continue

            try:
                self.processor.process(job)
            except Exception:
                self.queue.reject(job)
            else:
                self.queue.ack(job)
```

Bây giờ:

```text
dequeue()
   ↓
1 second timeout
   ↓
None
   ↓
check stop_event
```

Worker có cơ hội phát hiện shutdown.

---

# 8. Nhưng graceful shutdown còn một yêu cầu

Giả sử:

```text
Queue
 ├── Job A
 ├── Job B
 └── Job C
```

Worker lấy Job A:

```text
Worker
   ↓
Job A
   ↓
processing...
```

Sau đó:

```text
SIGTERM
```

Worker phải:

```text
❌ không lấy Job B
✅ hoàn thành Job A
```

Do đó ta không kiểm tra shutdown **trong lúc processing**.

Ta kiểm tra trước khi lấy Job mới.

```python
while not self.stop_event.is_set():
    job = self.queue.dequeue(timeout=1.0)

    if job is None:
        continue

    self.processor.process(job)
```

Nếu shutdown xảy ra:

```text
processing Job A
       ↓
finish
       ↓
ACK
       ↓
loop
       ↓
stop_event = True
       ↓
exit
```

Đây chính là graceful shutdown.

---

# 9. State của Worker

Ta có thể biểu diễn state rõ ràng:

```python
from enum import StrEnum


class WorkerState(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
```

Worker:

```python
class Worker:
    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor

        self.stop_event = threading.Event()
        self.state = WorkerState.STARTING
```

`run()`:

```python
def run(self):
    self.state = WorkerState.RUNNING

    try:
        while not self.stop_event.is_set():
            job = self.queue.dequeue(timeout=1.0)

            if job is None:
                continue

            self._process(job)

    finally:
        self.state = WorkerState.STOPPED
```

`stop()`:

```python
def stop(self):
    self.state = WorkerState.STOPPING
    self.stop_event.set()
```

---

# 10. Tách `_process()`

Đừng nhồi tất cả logic vào `run()`.

```python
class Worker:
    ...

    def _process(self, job):
        try:
            self.processor.process(job)
        except Exception:
            self.queue.reject(job)
        else:
            self.queue.ack(job)
```

Worker lúc này:

```text
run()
 │
 ├── dequeue
 │
 └── _process()
       ├── processor
       ├── ACK
       └── reject
```

Đây là design dễ test hơn.

---

# 11. `SIGINT` và `SIGTERM`

Trong CLI crawler, thường gặp:

```text
Ctrl+C
   ↓
SIGINT
```

Container/orchestrator thường gửi:

```text
SIGTERM
```

Ta có thể bắt signal:

```python
import signal


def handle_shutdown(signum, frame):
    worker.stop()
```

Sau đó:

```python
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
```

Ví dụ:

```python
worker = Worker(
    queue=queue,
    processor=processor,
)

signal.signal(
    signal.SIGINT,
    lambda signum, frame: worker.stop(),
)

signal.signal(
    signal.SIGTERM,
    lambda signum, frame: worker.stop(),
)

worker.run()
```

Flow:

```text
Ctrl+C
   ↓
SIGINT
   ↓
worker.stop()
   ↓
stop_event.set()
   ↓
finish current job
   ↓
ACK
   ↓
STOPPED
```

---

# 12. Một điểm cực kỳ quan trọng

Graceful shutdown **không có nghĩa là xử lý hết toàn bộ Queue**.

Ví dụ:

```text
Queue = 100.000 jobs

Worker đang xử lý Job 10
```

Shutdown.

Không nên:

```text
"cố xử lý hết 99.990 jobs"
```

vì shutdown có thể trở thành:

```text
shutdown
   ↓
chờ 10 giờ
```

Graceful shutdown nghĩa là:

> **Không nhận Job mới, hoàn thành Job hiện tại một cách an toàn rồi dừng.**

---

# 13. Worker + UoW

Đây là phần cực kỳ quan trọng đối với architecture của chúng ta.

Worker:

```text
Worker
  ↓
Processor
  ↓
Use Case
  ↓
UoW
```

Ví dụ:

```python
class SaveChapter:
    def __init__(self, uow):
        self.uow = uow

    def execute(self, chapter):
        with self.uow:
            self.uow.chapters.save(chapter)
```

Worker:

```python
def _process(self, job):
    try:
        self.processor.process(job)
    except Exception:
        self.queue.reject(job)
    else:
        self.queue.ack(job)
```

Điều quan trọng:

```text
processor
   ↓
UoW
   ↓
COMMIT
   ↓
return successfully
   ↓
ACK
```

Không:

```text
processor
   ↓
ACK
   ↓
UoW
   ↓
COMMIT
```

---

# 14. Một nguyên tắc rất quan trọng

Nhớ câu này:

> **Worker không được ACK dựa trên việc "đã chạy xong function". Worker ACK dựa trên việc "business operation đã persistence thành công".**

Ví dụ:

```python
def process(job):
    chapter = fetch(job)
    save_chapter(chapter)
```

`save_chapter()`:

```python
with uow:
    uow.chapters.save(chapter)
```

Nếu:

```text
COMMIT thành công
```

thì:

```text
process() return
   ↓
ACK
```

Nếu:

```text
COMMIT thất bại
```

thì:

```text
process() raise
   ↓
không ACK
   ↓
retry/requeue
```

---

# 15. Transaction không được kéo dài trong lúc HTTP

Đây là lỗi thiết kế rất dễ mắc.

❌ Sai:

```python
with uow:
    chapter = fetch_from_web(url)

    parse(chapter)

    uow.chapters.save(chapter)
```

Nếu HTTP mất:

```text
30 giây
```

thì SQLite transaction cũng bị giữ:

```text
BEGIN
   ↓
HTTP 30s
   ↓
DB
   ↓
COMMIT
```

Rất tệ.

---

## Đúng

```text
CLAIM
 ↓
COMMIT
 ↓

HTTP FETCH
 ↓
PARSE
 ↓

BEGIN
 ↓
SAVE
 ↓
UPDATE STATE
 ↓
COMMIT
 ↓
ACK
```

Đây sẽ là nền tảng cho **Buổi 11 — Lease / Visibility Timeout**.

---

# 16. Worker hoàn chỉnh phiên bản Buổi 10

```python
import threading
from enum import StrEnum


class WorkerState(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


class Worker:
    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor

        self.stop_event = threading.Event()
        self.state = WorkerState.STARTING

    def stop(self):
        if self.state == WorkerState.RUNNING:
            self.state = WorkerState.STOPPING

        self.stop_event.set()

    def run(self):
        self.state = WorkerState.RUNNING

        try:
            while not self.stop_event.is_set():
                job = self.queue.dequeue(timeout=1.0)

                if job is None:
                    continue

                self._process(job)

        finally:
            self.state = WorkerState.STOPPED

    def _process(self, job):
        try:
            self.processor.process(job)
        except Exception:
            self.queue.reject(job)
        else:
            self.queue.ack(job)
```

Kiến trúc:

```text
                  Worker
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
   stop_event                Queue
        │                       │
        ↓                       ↓
 lifecycle                dequeue(timeout)
                                │
                                ↓
                              Job
                                │
                                ↓
                            Processor
                                │
                                ↓
                              UoW
                                │
                                ↓
                              COMMIT
                                │
                                ↓
                               ACK
```

---

# 17. Một vấn đề vẫn chưa giải quyết

Hãy tưởng tượng:

```text
Worker A
   ↓
claim Chapter 100
   ↓
HTTP request
   ↓
💥 Worker crash
```

Database vẫn có:

```text
chapter 100
status = crawling
```

Nhưng Worker đã chết.

Ai đưa Chapter 100 về lại:

```text
PENDING
```

?

**Chưa có ai.**

Đây chính là vấn đề của Buổi 11.

---

# 18. Từ Worker Lifecycle → Lease

Ta sẽ tiến tới:

```text
PENDING
   ↓
CLAIM
   ↓
CRAWLING
   +
lease_until
   ↓
 ┌───────────────┐
 │               │
 ↓               ↓
SUCCESS        WORKER CRASH
 │               │
 ↓               ↓
COMPLETED     lease expired
                 │
                 ↓
               PENDING
```

Ví dụ database:

```text
chapter_crawl_states
─────────────────────────────
novel_id
chapter_number
status
worker_id
claimed_at
lease_until
retry_count
```

Worker claim:

```text
worker_id = worker-01
lease_until = 23:50:00
```

Nếu Worker chết:

```text
23:50:00
   ↓
lease expired
   ↓
reclaim
```

Đây là **Lease / Visibility Timeout**.

---

# 🧠 Những gì cần nhớ sau Buổi 10

Bạn chỉ cần nhớ 7 điểm:

```text
1. Worker có lifecycle
   STARTING → RUNNING → STOPPING → STOPPED

2. Graceful shutdown
   không nhận job mới
   nhưng hoàn thành job hiện tại

3. threading.Event
   dùng để báo stop

4. Blocking dequeue
   phải có timeout
   để worker có thể nhận shutdown signal

5. ACK sau COMMIT
   không ACK trước persistence

6. Transaction không bao quanh HTTP request

7. Worker crash sau khi claim
   → cần Lease / Visibility Timeout
```

Và câu quan trọng nhất:

> **Graceful shutdown bảo vệ Job đang chạy; Lease/Visibility Timeout bảo vệ Job bị bỏ lại khi Worker chết.**

---

# 📝 Bài tập Buổi 10

### Bài 1 — Shutdown

Viết:

```python
Worker
```

sao cho:

```text
Ctrl+C
   ↓
stop
   ↓
finish current job
   ↓
ACK
   ↓
STOPPED
```

---

### Bài 2 — Worker State

Implement:

```python
WorkerState
```

với:

```text
STARTING
RUNNING
STOPPING
STOPPED
```

và không cho phép transition vô lý.

---

### Bài 3 — Simulate Crash

Mô phỏng:

```text
Worker
 ↓
claim
 ↓
fetch
 ↓
raise RuntimeError
```

Sau đó quan sát:

```text
Chapter = CRAWLING
```

và trả lời:

> Nếu worker chết ở đây thì ai cứu Chapter?

Đây chính là câu hỏi dẫn sang **Buổi 11 — Lease / Visibility Timeout**.
