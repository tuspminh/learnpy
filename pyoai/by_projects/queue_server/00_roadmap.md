Được. Với mục tiêu của bạn là **xây dựng crawler framework có crawl-worker**, mình khuyên không học Queue Server theo kiểu “clone Redis” ngay từ đầu. Ta sẽ xây **một message queue server tối giản**, sau đó tăng dần đến kiến trúc gần Redis Queue:

```text
                    ┌─────────────────────┐
                    │     Queue Server    │
                    │                     │
Producer ──────────►│  enqueue()          │
                    │  queue              │
                    │  reserve()          │
                    │  ack()              │
                    │  retry()            │
                    │  timeout()          │
                    └─────────┬───────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │ CrawlWorker │
                       └──────┬──────┘
                              │
                     crawl URL / parse
                              │
                              ▼
                       enqueue next jobs
```

## Roadmap: Queue Server cho Crawl Worker

Ta có thể học theo **15 buổi**:

### Phần I — Queue Core

1. **Buổi 1 — Queue Server là gì?**

   * Queue vs list
   * Producer / Consumer
   * Job
   * Queue server
   * Vì sao crawl worker cần queue

2. **Buổi 2 — In-memory Queue**

   * `deque`
   * FIFO
   * `put()`
   * `get()`
   * nhiều worker

3. **Buổi 3 — TCP Queue Server**

   * `socket`
   * client/server
   * protocol
   * command:

     ```text
     ENQUEUE
     DEQUEUE
     ```

4. **Buổi 4 — Job Model**

   * `Job`
   * `job_id`
   * payload
   * status
   * timestamps

5. **Buổi 5 — Queue Protocol**

   * JSON protocol
   * request/response
   * command routing
   * protocol version

---

### Phần II — Reliability

6. **Buổi 6 — ACK / ACKNOWLEDGE**

   * tại sao `DEQUEUE` chưa đủ
   * worker crash
   * `reserve`
   * `ack`

7. **Buổi 7 — Retry**

   * failed job
   * retry count
   * max retries
   * exponential backoff

8. **Buổi 8 — Visibility Timeout**

   * job đang chạy
   * worker chết
   * job quay lại queue

9. **Buổi 9 — Dead Letter Queue**

   * failed jobs
   * retry exhausted
   * DLQ

10. **Buổi 10 — Priority Queue**

* priority
* crawl chapter trước
* crawl image sau

---

### Phần III — Persistence & Worker

11. **Buổi 11 — SQLite-backed Queue**

* queue persistence
* transaction
* locking
* crash recovery

12. **Buổi 12 — Async Queue Server**

* `asyncio`
* async TCP server
* concurrent clients

13. **Buổi 13 — Crawl Worker**

* worker lifecycle
* polling
* reserve
* execute
* ACK
* retry

14. **Buổi 14 — Queue Management**

* `queue.stats`
* `queue.pause`
* `queue.resume`
* `queue.clear`
* `job.inspect`

15. **Buổi 15 — Mini Queue Server hoàn chỉnh**

* Queue Server
* CLI client
* Crawl Worker
* SQLite
* retry
* timeout
* DLQ

Sau đó mới tiến tới:

```text
                    ┌────────────────────┐
                    │    Queue Server    │
                    │                    │
                    │ SQLite             │
                    │ Queue              │
                    │ Job Registry       │
                    │ Retry              │
                    │ Timeout            │
                    │ DLQ                │
                    └─────────┬──────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        CrawlWorker 1   CrawlWorker 2   CrawlWorker 3
             │                │                │
             ▼                ▼                ▼
          Novel A          Novel B          Novel C
```

## Kiến trúc cuối cùng

Mình đề xuất project có cấu trúc:

```text
queue_server/
│
├── server/
│   ├── server.py
│   ├── protocol.py
│   ├── dispatcher.py
│   └── connection.py
│
├── queue/
│   ├── queue.py
│   ├── job.py
│   ├── scheduler.py
│   └── retry.py
│
├── storage/
│   ├── database.py
│   ├── job_repository.py
│   └── queue_repository.py
│
├── worker/
│   ├── worker.py
│   └── executor.py
│
├── client/
│   └── client.py
│
└── cli.py
```

Quan trọng nhất là **không để CrawlWorker biết cách queue lưu dữ liệu thế nào**.

Worker chỉ cần biết:

```python
job = client.reserve("chapter")

try:
    result = crawl(job)
    client.ack(job.id)
except Exception:
    client.retry(job.id)
```

Đây chính là abstraction mà sau này bạn có thể thay:

```text
                    QueueClient
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     MemoryQueue    SQLiteQueue   RedisQueue
```

Worker không cần sửa.

---

# Buổi 1 — Queue Server là gì?

Trước tiên cần hiểu **vấn đề mà Queue Server giải quyết**.

Giả sử crawler của bạn tìm được 10.000 URL:

```text
https://site.com/book/1/chapter/1
https://site.com/book/1/chapter/2
https://site.com/book/1/chapter/3
...
https://site.com/book/1/chapter/10000
```

Nếu crawler tự xử lý:

```python
for url in urls:
    crawl(url)
```

thì mọi thứ nằm trong **một process**.

Nếu process chết:

```text
crawl URL 1
crawl URL 2
crawl URL 3
crawl URL 4
      X
    crash
```

Ta không có một hệ thống trung tâm quản lý:

```text
pending
running
completed
failed
retry
```

Queue giải quyết vấn đề đó.

---

# 1. Producer

Producer là thành phần **đẩy job vào queue**.

Ví dụ crawler parser phát hiện chapter mới:

```python
queue.enqueue(
    "chapter_crawl",
    {
        "url": "https://example.com/chapter-10"
    }
)
```

Ta có:

```text
Producer
    │
    │ enqueue
    ▼
┌─────────────┐
│    Queue    │
└─────────────┘
```

---

# 2. Consumer

Consumer lấy job từ queue.

Trong hệ thống của bạn, consumer chính là:

```text
CrawlWorker
```

Ví dụ:

```python
job = queue.dequeue()

crawl(job.payload)
```

Kiến trúc:

```text
Producer
   │
   ▼
┌──────────────┐
│ Queue Server │
└──────┬───────┘
       │
       ▼
 CrawlWorker
```

---

# 3. Tại sao cần Queue Server?

Giả sử có 5 worker:

```text
                  Queue
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
      W1           W2         W3
                              ...
```

Queue server đảm bảo:

```text
Job 1 → W1
Job 2 → W2
Job 3 → W3
Job 4 → W1
Job 5 → W2
```

Một job không nên bị hai worker lấy cùng lúc.

Đây chính là một trong những vấn đề quan trọng nhất chúng ta sẽ giải quyết sau này.

---

# 4. Job là gì?

Đừng đưa trực tiếp URL vào queue.

Hãy tạo abstraction:

```python
class Job:
    id
    queue
    payload
    status
    attempts
    created_at
```

Ví dụ:

```text
Job
├── id = "job_123"
├── queue = "chapter"
├── payload
│   ├── url
│   └── book_id
├── status = "pending"
├── attempts = 0
└── created_at
```

Payload có thể là:

```python
{
    "url": "https://example.com/chapter/10",
    "book_id": 100,
    "chapter_id": 500
}
```

Sau này worker có thể nhận nhiều loại job:

```text
chapter_crawl
book_crawl
image_crawl
metadata_crawl
```

Ví dụ:

```text
Queue: chapter

Job:
{
    "type": "chapter_crawl",
    "url": "...",
    "chapter_id": 100
}
```

---

# 5. Job lifecycle

Đây là concept cực kỳ quan trọng.

Một job không chỉ có:

```text
waiting → done
```

Mà nên có:

```text
                 ┌──────────────┐
                 │   PENDING    │
                 └──────┬───────┘
                        │
                     reserve
                        │
                        ▼
                 ┌──────────────┐
                 │   RUNNING    │
                 └──────┬───────┘
                        │
                 ┌──────┴───────┐
                 │              │
                ACK           FAIL
                 │              │
                 ▼              ▼
             COMPLETED        RETRY
                                │
                                ▼
                             PENDING
```

Nếu retry quá nhiều:

```text
FAILED
  │
  │ max_retries
  ▼
 DEAD
```

Đây là nền tảng cho queue server mà chúng ta sẽ xây.

---

# 6. Queue đầu tiên

Trước khi network, SQLite, asyncio..., hãy xây phiên bản đơn giản nhất.

Python có sẵn:

```python
from collections import deque
```

Ta có:

```python
queue = deque()
```

Producer:

```python
queue.append("job-1")
queue.append("job-2")
queue.append("job-3")
```

Queue:

```text
front
  ↓
┌────────┬────────┬────────┐
│ job-1  │ job-2  │ job-3  │
└────────┴────────┴────────┘
                         ↑
                       back
```

Consumer:

```python
job = queue.popleft()
```

Kết quả:

```text
job-1
```

Tiếp:

```python
queue.popleft()
```

→

```text
job-2
```

Đây là FIFO:

```text
First In
   ↓
First Out
```

---

# 7. Nhưng Queue Server khác `deque`

Đây là điểm rất quan trọng.

`deque`:

```text
Process
   │
   └── deque
```

Nếu process chết:

```text
Process X
   │
   └── deque X

       💥
```

Queue mất.

Queue server:

```text
Producer 1 ─┐
Producer 2 ─┼──► Queue Server
Producer 3 ─┘          │
                       │
                 persistent storage
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
             W1       W2       W3
```

Server trở thành **nguồn quản lý queue tập trung**.

---

# 8. Thiết kế API đầu tiên

Ta sẽ hướng tới API:

```python
client.enqueue(
    queue="chapter",
    payload={
        "url": "...",
        "chapter_id": 100,
    }
)
```

Lấy job:

```python
job = client.reserve("chapter")
```

Xác nhận thành công:

```python
client.ack(job.id)
```

Thất bại:

```python
client.fail(job.id)
```

Retry:

```python
client.retry(job.id)
```

Sau này:

```python
client.stats("chapter")
```

có thể trả:

```text
pending:   120
running:    5
completed: 850
failed:      3
```

---

# 9. Tư duy quan trọng cho Crawl Worker

Đừng thiết kế:

```python
worker -> SQLite
worker -> queue table
worker -> update status
worker -> retry logic
```

Worker sẽ trở nên rất khó bảo trì.

Thay vào đó:

```text
                    QueueClient
                        │
             ┌──────────┼──────────┐
             │          │          │
          enqueue     reserve      ack
             │          │          │
             └──────────┼──────────┘
                        │
                   Queue Server
                        │
                      SQLite
```

Worker chỉ quan tâm:

```python
while True:
    job = queue.reserve("chapter")

    if job is None:
        continue

    try:
        crawl(job)
    except Exception:
        queue.retry(job.id)
    else:
        queue.ack(job.id)
```

Đây chính là kiến trúc mình muốn đưa bạn tới.

---

# Bài tập Buổi 1

Tự thiết kế `Job` với các field:

```text
id
queue
payload
status
attempts
created_at
```

và liệt kê các trạng thái:

```text
pending
running
completed
failed
dead
```

Sau đó trả lời 3 câu:

**1.** Vì sao `dequeue()` trực tiếp rồi worker crash có thể làm mất job?

**2.** Vì sao cần `ACK`?

**3.** Trong crawler của bạn, hãy liệt kê ít nhất 5 loại job có thể đưa vào queue.

Ở **Buổi 2**, chúng ta sẽ bắt đầu code thật: xây **In-Memory Queue Server đầu tiên bằng Python**, có `enqueue()`, `reserve()`, `ack()`, nhiều worker và xử lý race condition cơ bản.
