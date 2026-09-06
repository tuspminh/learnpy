Được. Với những gì chúng ta đã học trong phiên này, mình đề xuất **đóng khung toàn bộ khóa học thành một roadmap duy nhất**, để từ đây mỗi khi bạn chỉ cần nói `10`, `11`, `12`... thì chúng ta tiếp tục đúng bài, không lan sang chủ đề khác.

# 🗺️ ROADMAP — SQLite + UoW + Queue/Worker cho Novel Crawler

## 🎯 Mục tiêu cuối cùng

Xây dựng được kiến trúc persistence + crawling có khả năng:

```text
                    ┌──────────────┐
                    │     CLI      │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Application  │
                    └──────┬───────┘
                           ↓
                 ┌────────────────────┐
                 │   Use Cases        │
                 └─────────┬──────────┘
                           ↓
              ┌─────────────────────────┐
              │ Unit of Work            │
              └────────────┬────────────┘
                           ↓
             ┌──────────────────────────┐
             │ Repository               │
             ├──────────┬───────────────┤
             │ Novel    │ Chapter       │
             │ Crawl   │ CrawlState    │
             └──────────┴───────────────┘
                           ↓
                ┌─────────────────┐
                │ SQLite          │
                └─────────────────┘


Crawler
   ↓
Job
   ↓
Queue
   ↓
Worker × N
   ↓
Fetch → Parse → Validate
   ↓
Use Case
   ↓
UoW
   ↓
SQLite
```

Mục tiêu không chỉ là **biết dùng SQLite**, mà là hiểu cách thiết kế một **persistence + crawling infrastructure có tính production**.

---

# PHẦN I — SQLite Foundation

### Buổi 1 — SQLite Connection Manager + UoW + Dummy UoW

Đã học ✅

```text
Connection Manager
       ↓
Connection
       ↓
Unit of Work
       ↓
Repository
```

Nắm được:

* `sqlite3.Connection`
* `row_factory`
* Connection lifecycle
* UoW cơ bản
* Dummy UoW
* File Repository
* Repository abstraction

---

### Buổi 2 — Unit of Work Deep Dive

Đã học ✅

```text
with uow:
    repo_a.save()
    repo_b.save()
```

Nắm được:

* Transaction boundary
* `commit`
* `rollback`
* `__enter__`
* `__exit__`
* exception propagation
* shared connection
* nhiều repository trong cùng transaction

Nguyên tắc:

> **UoW sở hữu transaction, Repository không sở hữu transaction.**

---

### Buổi 3 — Repository + UoW + Dependency Injection

Đã học ✅

```text
Use Case
   ↓
UnitOfWork
   ↓
Repository
```

Nắm được:

* Dependency Injection
* Composition Root
* Interface
* Concrete implementation
* Fake UoW
* Fake Repository
* Testable architecture

---

# PHẦN II — SQLite Infrastructure Deep Dive

### Buổi 4 — SQLite Connection Manager Deep Dive

Đã học ✅

Nội dung:

* `row_factory`
* `foreign_keys`
* WAL
* `busy_timeout`
* connection timeout
* `isolation_level`
* `check_same_thread`
* connection lifecycle
* connection per worker

Kiến trúc:

```text
SQLiteConnectionManager
          ↓
      Connection
          ↓
        UoW
```

---

### Buổi 5 — NovelRepository Deep Dive

Đã học ✅

Nội dung:

* Entity → Row
* Row → Entity
* Mapper
* CRUD
* `exists`
* UPSERT
* Pagination
* Keyset pagination
* Bulk insert
* `executemany`
* N+1 problem
* JOIN
* parameterized SQL

Quan trọng:

> Repository là abstraction của persistence, **không phải CRUD wrapper đơn thuần**.

---

# PHẦN III — Novel Aggregate & Crawling Persistence

### Buổi 6 — Novel + Chapter Repository

Đã học / nền tảng đã triển khai ✅

Mô hình:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 └── ...
```

Tập trung vào:

* `NovelRepository`
* `ChapterRepository`
* Aggregate boundary
* transaction giữa Novel + Chapter
* bulk insert
* Chapter UPSERT
* idempotent crawling

Mục tiêu:

```text
crawl lại
   ↓
không tạo duplicate
   ↓
UPSERT
```

---

### Buổi 7 — Crawl State / Checkpoint

Đã học ✅

Từ:

```text
last_chapter_number
```

tiến tới:

```text
CrawlState
```

Mục tiêu:

* biết crawler đang ở đâu
* resume crawler
* checkpoint
* recovery sau crash
* phát hiện chapter chưa crawl

Nhưng nhận ra:

```text
last_chapter_number
```

không đủ khi có nhiều worker.

---

# PHẦN IV — Chapter State Machine

### Buổi 8 — Chapter Status + Atomic Claim

Đã học ✅

State machine:

```text
             ┌──────────────┐
             │    PENDING   │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │   CRAWLING   │
             └──────┬───────┘
               ┌────┴────┐
               ↓         ↓
        ┌───────────┐ ┌────────┐
        │ COMPLETED │ │ FAILED │
        └───────────┘ └────┬───┘
                            ↓
                         PENDING
```

Nắm được:

* Chapter state
* Retry
* Atomic claim
* `rowcount`
* race condition
* stale `CRAWLING`
* idempotency

Atomic claim:

```sql
UPDATE chapter_crawl_states
SET status = 'crawling'
WHERE novel_id = ?
  AND chapter_number = ?
  AND status = 'pending';
```

Nguyên tắc:

> **Không đọc rồi mới update. Phải claim atomically.**

---

# PHẦN V — Queue & Worker

### Buổi 9 — Queue + Worker Architecture

Đã học ✅

Kiến trúc:

```text
Producer
   ↓
 Queue
   ↓
Worker
   ↓
Processor
   ↓
Use Case
   ↓
UoW
   ↓
SQLite
```

Đã học:

* Job
* Job ID
* Queue abstraction
* `enqueue`
* `dequeue`
* `ack`
* `reject`
* InMemory Queue
* Worker loop
* ACK semantics
* retry
* exponential backoff
* DLQ
* at-least-once processing
* idempotent consumer

Nguyên tắc cực kỳ quan trọng:

```text
DB COMMIT
    ↓
   ACK
```

**Không ACK trước khi persistence thành công.**

---

# PHẦN VI — Worker Reliability

## ⭐ Buổi 10 — Worker Lifecycle & Graceful Shutdown

**Sắp học**

```text
STARTING
    ↓
 RUNNING
    ↓
 STOPPING
    ↓
 STOPPED
```

Học:

* Worker lifecycle
* `threading.Event`
* graceful shutdown
* SIGINT
* SIGTERM
* stop signal
* finish current job
* không nhận job mới khi stopping

---

## Buổi 11 — Job Lease / Visibility Timeout

**Sắp học**

Vấn đề:

```text
Worker A
   ↓
claim job
   ↓
CRASH 💥
```

Job bị kẹt:

```text
CRAWLING
```

Giải pháp:

```text
lease_until
worker_id
claimed_at
```

Nếu:

```text
lease_until < NOW()
```

→ job có thể được reclaim.

---

## Buổi 12 — Heartbeat

Worker chạy lâu:

```text
Worker
  ↓
fetch chapter
  ↓
parse
  ↓
10 phút...
```

Lease có thể hết hạn.

Heartbeat:

```text
Worker
  ↓
heartbeat
  ↓
extend lease
  ↓
heartbeat
  ↓
extend lease
```

Học:

* heartbeat
* lease renewal
* long-running job
* worker liveness
* stale worker detection

---

## Buổi 13 — Crash Recovery

Mô phỏng:

```text
Worker
   ↓
claim
   ↓
fetch
   ↓
💥 CRASH
```

Sau đó:

```text
Recovery process
       ↓
find expired leases
       ↓
PENDING
       ↓
Queue
```

Học:

* crash recovery
* stale jobs
* orphan jobs
* retry after crash
* recovery worker

---

# PHẦN VII — Multi Worker & Concurrency

## Buổi 14 — Multiple Workers

```text
             Queue
          /    |    \
         ↓     ↓     ↓
      Worker Worker Worker
         ↓     ↓     ↓
             SQLite
```

Học:

* nhiều worker
* race condition
* atomic claim
* SQLite concurrency
* connection per worker
* writer contention

---

## Buổi 15 — Worker Concurrency Control

Không phải:

```text
100 workers = 100x performance
```

Học:

* concurrency limit
* worker pool
* semaphore
* max concurrent requests
* database write bottleneck
* HTTP bottleneck

Mục tiêu:

```text
HTTP concurrency ≠ DB concurrency
```

---

## Buổi 16 — Backpressure

Khi producer nhanh hơn consumer:

```text
Producer
   ↓↓↓↓↓↓↓↓↓
 Queue
   ↓
 Worker
```

Queue phình to.

Học:

* backpressure
* bounded queue
* queue size
* producer throttling
* consumer pressure
* crawl rate limiting

---

# PHẦN VIII — Retry & Failure Handling

## Buổi 17 — Retry Architecture

Phân biệt:

```text
Transient Error
      ↓
    Retry
```

và:

```text
Permanent Error
      ↓
   No Retry
```

Ví dụ:

```text
Timeout       → retry
ConnectionError → retry
429           → retry
503           → retry

404           → thường không retry
ParserError   → thường không retry
Invalid HTML  → thường không retry
```

---

## Buổi 18 — Exponential Backoff + Jitter

```text
Retry 1 → 1s
Retry 2 → 2s
Retry 3 → 4s
Retry 4 → 8s
```

Thêm:

```text
jitter
```

để tránh:

```text
100 workers
   ↓
cùng retry
   ↓
cùng lúc
```

→ thundering herd.

---

## Buổi 19 — Dead Letter Queue

```text
             Queue
               ↓
             Worker
          ↙         ↘
       success      failure
         ↓             ↓
        ACK          Retry
                        ↓
                   max retry
                        ↓
                       DLQ
```

Học:

* DLQ
* poison message
* permanent failure
* manual inspection
* replay DLQ

---

# PHẦN IX — Transaction & Queue Integration

## Buổi 20 — Transaction Boundary trong Worker

Đây là một bài **rất quan trọng**.

Không làm:

```text
BEGIN
  ↓
HTTP request
  ↓
Parse
  ↓
30 seconds
  ↓
INSERT
COMMIT
```

Vì transaction bị giữ quá lâu.

Thiết kế tốt:

```text
BEGIN
  ↓
CLAIM
  ↓
COMMIT

HTTP FETCH
  ↓
PARSE
  ↓

BEGIN
  ↓
SAVE CHAPTER
UPDATE STATE
  ↓
COMMIT
  ↓
ACK
```

Nguyên tắc:

> **Database transaction phải ngắn.**

---

## Buổi 21 — Idempotent Consumer Deep Dive

Giả sử:

```text
DB COMMIT
    ↓
💥 Worker crash
    ↓
ACK chưa thực hiện
```

Queue đưa Job lại:

```text
Job chạy lần 2
```

Không được tạo:

```text
Chapter duplicate
```

Giải pháp:

* unique constraint
* UPSERT
* deterministic key
* idempotent state transition
* safe retry

---

## Buổi 22 — Exactly Once vs At Least Once

Hiểu rõ:

```text
At-most-once
```

vs

```text
At-least-once
```

vs

```text
Exactly-once
```

Thực tế crawler thường chọn:

```text
At-least-once delivery
          +
Idempotent consumer
```

thay vì cố xây exactly-once end-to-end.

---

# PHẦN X — Queue Implementation

## Buổi 23 — InMemory Queue

Đã có nền tảng từ Buổi 9.

Tiếp tục hoàn thiện:

```python
InMemoryJobQueue
```

với:

* blocking
* timeout
* shutdown
* retry
* DLQ

---

## Buổi 24 — SQLite Job Queue

Xây Queue bằng SQLite:

```text
jobs
────────────────────
id
status
payload
retry_count
available_at
claimed_at
worker_id
```

Đây là bài rất phù hợp với project hiện tại.

---

## Buổi 25 — SQLite Queue Atomic Claim

Thiết kế:

```text
PENDING
   ↓
atomic claim
   ↓
PROCESSING
```

Tập trung:

* concurrent workers
* atomic UPDATE
* lease
* retry
* transaction

---

# PHẦN XI — Redis / RQ Integration

## Buổi 26 — Redis Queue Architecture

Chuyển:

```text
SQLite Queue
```

sang:

```text
Redis Queue
```

nhưng Application không thay đổi:

```text
Application
    ↓
 JobQueue
    ↓
 ┌─────────────┐
 │ SQLite      │
 │ Redis       │
 │ RQ          │
 └─────────────┘
```

---

## Buổi 27 — RQ Integration

Áp dụng kiến thức bạn đã học về **Redis Queue (RQ)**.

```text
Producer
   ↓
RQ
   ↓
RQ Worker
   ↓
Application
   ↓
UoW
   ↓
SQLite
```

Học:

* enqueue
* worker
* retry
* job result
* failed job
* timeout
* monitoring

---

# PHẦN XII — Production Crawler Architecture

## Buổi 28 — Fetch → Parse → Persist Pipeline

Hoàn chỉnh pipeline:

```text
        URL
         ↓
      Fetcher
         ↓
       HTML
         ↓
      Parser
         ↓
      Chapter
         ↓
     Validator
         ↓
      UseCase
         ↓
        UoW
         ↓
     Repository
         ↓
       SQLite
```

Tách rõ:

```text
Fetcher ≠ Parser ≠ Repository
```

---

## Buổi 29 — Plugin Parser Architecture

Áp dụng kiến trúc đã học về Selectolax:

```text
Parser
   │
   ├── SiteAParser
   ├── SiteBParser
   ├── SiteCParser
   └── ...
```

Crawler không biết parser cụ thể.

---

## Buổi 30 — Multi-source Novel Crawler

Hoàn thiện:

```text
             Crawler
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
    Site A   Site B   Site C
       ↓        ↓        ↓
     Parser   Parser   Parser
       └────────┼────────┘
                ↓
          Common Domain
                ↓
               UoW
                ↓
             SQLite
```

---

# PHẦN XIII — Observability

## Buổi 31 — Logging cho Worker

Áp dụng kiến thức **Logging Deep Dive** bạn vừa học.

Log:

```text
job_id
novel_id
chapter_number
worker_id
retry_count
duration
status
error
```

Ví dụ:

```text
INFO  job started
INFO  chapter fetched
INFO  chapter saved
INFO  job acked

WARNING retrying job

ERROR job failed
```

---

## Buổi 32 — Structured Logging

Thay vì:

```text
"Failed to crawl chapter"
```

hướng tới:

```text
{
    "event": "chapter_crawl_failed",
    "job_id": "...",
    "novel_id": 10,
    "chapter": 25,
    "retry": 2,
    "error": "TimeoutError"
}
```

---

## Buổi 33 — Metrics

Theo dõi:

```text
jobs_total
jobs_success
jobs_failed
jobs_retry
queue_size
crawl_duration
http_error_rate
db_error_rate
```

---

## Buổi 34 — Worker Monitoring

Dashboard:

```text
Workers
────────────────────
Worker 1   RUNNING
Worker 2   RUNNING
Worker 3   IDLE
Worker 4   STOPPED

Queue
────────────────────
Pending:    120
Processing:  8
Failed:     4
DLQ:        2
```

---

# PHẦN XIV — Testing Architecture

## Buổi 35 — Fake UoW + Fake Repository

Kiểm tra Use Case mà không cần SQLite.

```text
Use Case
   ↓
Fake UoW
   ↓
Fake Repository
```

---

## Buổi 36 — Testing Transaction

Test:

```text
success
   → commit

exception
   → rollback
```

---

## Buổi 37 — Testing Worker

Test:

```text
job
 ↓
worker
 ↓
processor
 ↓
ACK
```

và:

```text
processor error
      ↓
    retry
```

---

## Buổi 38 — Testing Concurrency

Test:

```text
Worker A ──┐
           ├── claim
Worker B ──┘
```

Chỉ **một worker** được claim chapter.

---

# PHẦN XV — Final Architecture

## Buổi 39 — Production Architecture Review

Review toàn bộ:

```text
                 CLI / GUI
                    ↓
               Application
                    ↓
               Use Cases
                    ↓
             Domain Model
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   UnitOfWork              JobQueue
        ↓                       ↓
   Repository                Queue
        ↓                       ↓
      SQLite                 Worker
                                ↓
                             Fetcher
                                ↓
                              Parser
```

---

## Buổi 40 — Final Project

### 🚀 Production-style Novel Crawler

Mục tiêu:

```text
Novel Crawler System
```

có:

* SQLite Connection Manager
* Unit of Work
* Novel Repository
* Chapter Repository
* Crawl State
* Chapter State Machine
* Job Queue
* Worker
* Retry
* Backoff
* DLQ
* Lease
* Heartbeat
* Crash Recovery
* Multiple Workers
* Plugin Parser
* Logging
* Metrics
* Testing
* CLI

---

# 🧭 Bản đồ kiến thức cần ghi nhớ

Thay vì nhớ 40 bài rời rạc, bạn chỉ cần nhớ **8 tầng**:

```text
                    ┌──────────────────┐
                    │    CLI / GUI     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   Application    │
                    │    Use Case      │
                    └────────┬─────────┘
                             ↓
              ┌─────────────────────────────┐
              │          Domain             │
              │ Novel / Chapter / State     │
              └─────────────┬───────────────┘
                            ↓
              ┌─────────────────────────────┐
              │       Unit of Work          │
              │     Transaction Boundary    │
              └─────────────┬───────────────┘
                            ↓
              ┌─────────────────────────────┐
              │        Repository           │
              │ Novel / Chapter / Crawl     │
              └─────────────┬───────────────┘
                            ↓
              ┌─────────────────────────────┐
              │          SQLite             │
              │ Connection / Transaction    │
              └─────────────────────────────┘
```

Song song với persistence:

```text
Producer
   ↓
  Job
   ↓
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
 Repository
```

Và reliability:

```text
            Worker
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
     Retry   Lease   Heartbeat
       ↓       ↓        ↓
      DLQ   Recovery  Liveness
```

---

# ⭐ 10 nguyên tắc xuyên suốt khóa học

Đây là phần mình muốn bạn **ghi nhớ hơn cả tên từng bài**:

### 1. Repository không commit

```text
Repository
    ↓
execute SQL
```

Không:

```text
repository.commit()
```

---

### 2. UoW sở hữu transaction

```text
UoW
 ├── repository A
 ├── repository B
 └── repository C
```

→ cùng connection
→ cùng transaction.

---

### 3. Connection Manager không phải UoW

```text
Connection Manager
        ↓
     Connection
        ↓
       UoW
```

Mỗi component có trách nhiệm riêng.

---

### 4. Worker không biết SQL

Worker chỉ biết:

```text
Job → Processor
```

Không:

```python
worker.conn.execute(...)
```

---

### 5. ACK sau COMMIT

```text
process
   ↓
save
   ↓
COMMIT
   ↓
ACK
```

---

### 6. Concurrent worker phải atomic claim

Không:

```text
SELECT
   ↓
UPDATE
```

một cách tách rời.

Mà:

```text
atomic UPDATE ... WHERE status = 'pending'
```

---

### 7. Transaction không bao quanh HTTP request

Sai:

```text
BEGIN
 ↓
HTTP
 ↓
Parse
 ↓
DB
 ↓
COMMIT
```

Đúng:

```text
CLAIM → COMMIT

HTTP → PARSE

SAVE → COMMIT → ACK
```

---

### 8. At-least-once + idempotency

Đừng cố giả định:

```text
job chỉ chạy đúng một lần
```

Hãy thiết kế:

```text
job có thể chạy nhiều lần
       ↓
database vẫn đúng
```

---

### 9. Retry phải có giới hạn

```text
retry
retry
retry
retry
retry
```

❌

Phải có:

```text
retry
  ↓
max retry
  ↓
DLQ
```

---

### 10. Application phụ thuộc abstraction

```text
Application
      ↓
    JobQueue
      ↑
 ┌────┼──────┐
 ↓    ↓      ↓
Memory SQLite Redis
```

Thay infrastructure mà không phá Application.

---

# 📌 Trạng thái hiện tại

Bạn đã đi đến:

```text
Buổi 1  ✅
Buổi 2  ✅
Buổi 3  ✅
Buổi 4  ✅
Buổi 5  ✅
Buổi 6  ✅
Buổi 7  ✅
Buổi 8  ✅
Buổi 9  ✅

───────────────
HIỆN TẠI
───────────────

Buổi 10  ⬜ Worker Lifecycle
Buổi 11  ⬜ Lease / Visibility Timeout
Buổi 12  ⬜ Heartbeat
Buổi 13  ⬜ Crash Recovery
...
Buổi 40  ⬜ Final Project
```

**Từ giờ mình đề xuất không mở thêm topic ngoài roadmap này.** Nếu bạn nói `10`, mình sẽ hiểu là **Buổi 10 — Worker Lifecycle & Graceful Shutdown**; `11` là Lease; `12` là Heartbeat... và cứ thế đi tuần tự đến Final Project.
