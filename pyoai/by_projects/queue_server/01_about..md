

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
