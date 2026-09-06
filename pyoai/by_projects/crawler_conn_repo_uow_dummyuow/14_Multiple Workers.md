# Buổi 14 — Multiple Workers

Ở Buổi 13, chúng ta đã giải quyết:

```text
Worker crash
    ↓
Heartbeat mất
    ↓
Lease expired
    ↓
Recovery
    ↓
Requeue
    ↓
Worker khác xử lý
```

Bây giờ chúng ta nâng cấp từ:

```text
Queue
  ↓
Worker A
```

thành:

```text
             ┌── Worker A
             │
Queue ───────┼── Worker B
             │
             ├── Worker C
             │
             └── Worker D
```

Đây là bước rất quan trọng vì từ thời điểm có **nhiều Worker**, concurrency trở thành vấn đề trung tâm.

---

# 1. Tại sao cần Multiple Workers?

Một Worker xử lý tuần tự:

```text
Job 1 → 2s
Job 2 → 3s
Job 3 → 2s
Job 4 → 4s

Tổng ≈ 11s
```

Nếu 4 Worker:

```text
Worker A → Job 1 → 2s
Worker B → Job 2 → 3s
Worker C → Job 3 → 2s
Worker D → Job 4 → 4s

Tổng ≈ 4s
```

Về lý thuyết throughput tăng.

Nhưng:

> **Không phải cứ thêm Worker là hệ thống nhanh hơn.**

Đây chính là bài học quan trọng nhất hôm nay.

---

# 2. Architecture

Ta có:

```text
                    ┌─────────────┐
                    │    Queue    │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
         Worker A      Worker B      Worker C
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                     SQLite Database
```

Mỗi Worker phải có:

```text
worker_id riêng
connection riêng
UoW riêng
job ownership riêng
```

Ví dụ:

```text
worker-A
worker-B
worker-C
```

---

# 3. Nguyên tắc số 1: Không share SQLite connection

Đây là kiến thức từ Buổi 4.

Không:

```python
conn = sqlite3.connect("crawler.db")

worker_a.conn = conn
worker_b.conn = conn
worker_c.conn = conn
```

❌

Thay vào đó:

```text
Worker A
   ↓
Connection A

Worker B
   ↓
Connection B

Worker C
   ↓
Connection C
```

Ví dụ:

```python
def create_worker(db_manager):
    return Worker(
        uow_factory=lambda: SQLiteUnitOfWork(
            db_manager
        )
    )
```

Mỗi UoW tạo connection của riêng nó.

---

# 4. Worker ID

Mỗi Worker cần identity:

```python
from uuid import uuid4


worker_id = f"worker-{uuid4()}"
```

Ví dụ:

```text
worker-7c8...
worker-2ab...
worker-91d...
```

Hoặc khi chạy process:

```text
crawler-worker-01
crawler-worker-02
crawler-worker-03
```

Worker ID rất quan trọng vì database cần biết:

```text
Chapter 100
    ↓
đang thuộc Worker nào?
```

---

# 5. Race Condition

Đây là vấn đề lớn nhất.

Giả sử:

```text
Job:
Chapter 100
status = pending
```

Có:

```text
Worker A
Worker B
```

Cả hai cùng muốn lấy Chapter 100.

Nếu code:

```python
state = repo.get(100)

if state.status == "pending":
    repo.update_status(100, "crawling")
```

thì có race condition.

---

# 6. Race Condition xảy ra như thế nào?

Timeline:

```text
Worker A                    Worker B

SELECT chapter 100
status=pending

                            SELECT chapter 100
                            status=pending

UPDATE → crawling

                            UPDATE → crawling
```

Kết quả:

```text
Worker A nghĩ:
"I own Chapter 100"

Worker B cũng nghĩ:
"I own Chapter 100"
```

💥

Hai Worker cùng crawl một Chapter.

---

# 7. SELECT → UPDATE là nguy hiểm

Pattern:

```text
SELECT
  ↓
if pending:
  ↓
UPDATE
```

không atomic.

Khoảng thời gian:

```text
SELECT
   ↓
   ↓ ← race window
   ↓
UPDATE
```

là nơi Worker khác có thể chen vào.

---

# 8. Atomic Claim

Đây chính là lý do Buổi 8 chúng ta đã thiết kế:

```sql
UPDATE chapter_crawl_states
SET
    status = 'crawling',
    worker_id = ?,
    claimed_at = CURRENT_TIMESTAMP,
    lease_until = datetime('now', '+60 seconds'),
    updated_at = CURRENT_TIMESTAMP
WHERE novel_id = ?
  AND chapter_number = ?
  AND status = 'pending';
```

Sau đó:

```python
cursor = conn.execute(...)
```

kiểm tra:

```python
if cursor.rowcount == 1:
    # Successfully claimed
else:
    # Someone else owns it
```

Đây là điểm cực kỳ quan trọng.

---

# 9. Atomic Claim với Multiple Workers

Giả sử:

```text
Chapter 100 = pending
```

Hai Worker đồng thời:

```text
Worker A ─────┐
              ├── UPDATE ... WHERE status='pending'
Worker B ─────┘
```

Database đảm bảo chỉ một UPDATE thành công.

Ví dụ:

```text
Worker A → rowcount = 1
Worker B → rowcount = 0
```

Kết quả:

```text
Chapter 100
worker_id = Worker A
status = crawling
```

Worker B:

```text
"Không claim được"
```

→ lấy Job khác.

---

# 10. Queue và Database là hai lớp khác nhau

Đừng nhầm:

```text
Queue
```

với:

```text
Chapter Crawl State
```

Queue trả:

```text
Job
```

Database quản lý:

```text
Ownership
State
Lease
Retry
```

Ví dụ:

```text
Queue
 └── CrawlChapterJob(100)

          ↓

Worker A

          ↓

DB claim

          ↓

Chapter 100
worker_id=A
status=crawling
```

Queue không phải source of truth cho ownership.

---

# 11. Worker loop

Worker đơn giản:

```python
class Worker:

    def __init__(
        self,
        worker_id,
        queue,
        processor,
    ):
        self.worker_id = worker_id
        self.queue = queue
        self.processor = processor

    def run(self):
        while True:
            job = self.queue.dequeue()

            if job is None:
                continue

            self.process(job)
```

Nhưng `process()` phải claim trước.

---

# 12. Claim trước khi HTTP

Đúng:

```text
Job
 ↓
CLAIM
 ↓
COMMIT
 ↓
HTTP
 ↓
PARSE
 ↓
SAVE
 ↓
COMMIT
 ↓
ACK
```

Sai:

```text
Job
 ↓
HTTP
 ↓
CLAIM
```

Tại sao?

Nếu 5 Worker cùng lấy cùng một Job:

```text
Worker A → HTTP
Worker B → HTTP
Worker C → HTTP
Worker D → HTTP
```

rồi mới tranh nhau claim.

Bạn đã tạo:

```text
duplicate HTTP requests
```

---

# 13. Nhưng Claim transaction phải ngắn

Không:

```text
BEGIN
 ↓
CLAIM
 ↓
HTTP request
 ↓
10 seconds
 ↓
parse
 ↓
save
 ↓
COMMIT
```

Đây là thiết kế tệ.

Vì transaction mở trong thời gian HTTP:

```text
DB transaction
████████████████████████████
         HTTP
```

Trong khi SQLite chỉ có concurrency write hạn chế.

Đúng:

```text
BEGIN
 ↓
CLAIM
 ↓
COMMIT

HTTP
 ↓
PARSE

BEGIN
 ↓
SAVE
 ↓
COMPLETE
 ↓
COMMIT
```

---

# 14. SQLite và Multiple Writers

Đây là nơi SQLite bắt đầu trở nên thú vị.

SQLite hỗ trợ nhiều readers tốt.

Nhưng với writes:

```text
Worker A → WRITE
Worker B → WRITE
Worker C → WRITE
```

có contention.

Trong một thời điểm nhất định, chỉ có một writer có thể thực hiện ghi.

Do đó:

```text
10 Worker
```

không có nghĩa:

```text
10x database write performance
```

---

# 15. WAL giúp gì?

Chúng ta đã bật:

```sql
PRAGMA journal_mode = WAL;
```

WAL giúp:

```text
Reader
Reader
Reader
Reader
```

có thể hoạt động đồng thời tốt hơn trong khi writer ghi.

Nhưng:

> **WAL không biến SQLite thành database có nhiều writer đồng thời.**

Vẫn phải cẩn thận với:

```text
write contention
```

---

# 16. Busy Timeout

Khi Worker A đang ghi:

```text
Worker A
   ↓
WRITE
```

Worker B cũng muốn ghi:

```text
Worker B
   ↓
WRITE
```

SQLite có thể gặp:

```text
database is locked
```

Vì vậy Connection Manager đã có:

```python
sqlite3.connect(
    db_path,
    timeout=5.0,
)
```

và:

```sql
PRAGMA busy_timeout = 5000;
```

SQLite sẽ chờ một khoảng thời gian thay vì fail ngay lập tức.

---

# 17. Worker concurrency không chỉ là Thread

Có thể chạy:

### Threads

```text
Process
 ├── Thread A
 ├── Thread B
 ├── Thread C
 └── Thread D
```

### Processes

```text
Process A
Process B
Process C
Process D
```

### Containers

```text
Container A
Container B
Container C
```

Architecture của chúng ta nên không phụ thuộc vào cách deploy:

```text
Worker
```

chỉ cần:

```text
Queue
+
UoW
+
Repository
+
Processor
```

---

# 18. Multiple Worker với Thread

Demo:

```python
import threading


workers = []

for i in range(4):
    worker = Worker(
        worker_id=f"worker-{i}",
        queue=queue,
        processor=processor,
    )

    thread = threading.Thread(
        target=worker.run,
        daemon=True,
    )

    workers.append(thread)
    thread.start()
```

Ta có:

```text
Thread 1 → Worker 1
Thread 2 → Worker 2
Thread 3 → Worker 3
Thread 4 → Worker 4
```

Nhưng nhớ:

> Không share SQLite connection giữa các Worker.

---

# 19. Connection Factory

Thiết kế tốt hơn:

```python
class SQLiteUnitOfWork:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def __enter__(self):
        self.conn = self.connection_manager.connect()

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        self.crawl_states = (
            SQLiteChapterCrawlStateRepository(
                self.conn
            )
        )

        return self
```

Mỗi lần:

```python
with uow_factory() as uow:
```

→ connection mới.

---

# 20. Processor

Một processor tốt:

```python
class ChapterProcessor:

    def __init__(
        self,
        uow_factory,
        crawler,
        worker_id,
    ):
        self.uow_factory = uow_factory
        self.crawler = crawler
        self.worker_id = worker_id
```

Claim:

```python
def claim(self, job):
    with self.uow_factory() as uow:
        return uow.crawl_states.claim(
            novel_id=job.novel_id,
            chapter_number=job.chapter_number,
            worker_id=self.worker_id,
        )
```

Nếu:

```python
False
```

thì Worker không sở hữu Job.

---

# 21. Full processing flow

```python
def process(self, job):

    claimed = self.claim(job)

    if not claimed:
        return

    try:
        chapter = self.crawler.fetch(job)

        with self.uow_factory() as uow:
            uow.chapters.save(chapter)

            success = uow.crawl_states.complete(
                novel_id=job.novel_id,
                chapter_number=job.chapter_number,
                worker_id=self.worker_id,
            )

            if not success:
                raise OwnershipLost()

    except Exception as exc:
        self.fail(job, exc)
        raise
```

Điểm quan trọng:

```text
CLAIM
 ↓
COMMIT
 ↓
HTTP
 ↓
SAVE + COMPLETE
 ↓
COMMIT
 ↓
ACK
```

---

# 22. Zombie Worker trong Multiple Workers

Đây là case nguy hiểm nhất.

Timeline:

```text
Worker A
   ↓
claim
   ↓
lease = 60s
   ↓
HTTP request
```

Worker A bị treo.

Sau 60s:

```text
Recovery
   ↓
lease expired
```

Worker B:

```text
claim
   ↓
worker_id = B
```

Sau đó Worker A tỉnh lại:

```text
Worker A
   ↓
complete()
```

Nếu SQL không check owner:

💥 Worker A có thể ghi đè Worker B.

---

# 23. Ownership Check

Completion:

```sql
UPDATE chapter_crawl_states
SET
    status = 'completed',
    finished_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE novel_id = ?
  AND chapter_number = ?
  AND status = 'crawling'
  AND worker_id = ?;
```

Worker A:

```text
worker_id = A
```

nhưng DB:

```text
worker_id = B
```

→

```text
rowcount = 0
```

Worker A không thể complete.

Đây là một **fencing mechanism** đơn giản.

---

# 24. Fencing Token

Ở hệ thống phân tán lớn, ownership thường dùng:

```text
fencing token
```

Ví dụ:

```text
claim #1 → token 10
claim #2 → token 11
```

Worker A:

```text
token = 10
```

Worker B:

```text
token = 11
```

Nếu A trở thành zombie:

```text
token 10
```

thì DB chỉ chấp nhận:

```text
token >= current token
```

Trong hệ thống hiện tại:

```text
worker_id
```

đã giúp giải quyết phần lớn vấn đề ownership.

Fencing token sẽ là một chủ đề nâng cao hơn.

---

# 25. Multiple Workers và throughput

Giả sử:

```text
HTTP = 1s
DB = 0.05s
```

Một Worker:

```text
≈ 1 job/s
```

4 Worker:

```text
≈ 4 job/s
```

nếu HTTP là bottleneck.

Nhưng nếu:

```text
HTTP = 0.01s
DB = 0.5s
```

thì database mới là bottleneck.

Thêm Worker:

```text
1 → 2 → 4 → 8 → 16
```

có thể làm hệ thống:

```text
chậm hơn
```

vì write contention tăng.

---

# 26. Bottleneck Analysis

Hệ thống crawler:

```text
Queue
  ↓
Claim
  ↓
HTTP
  ↓
Parse
  ↓
SQLite
```

Bottleneck có thể nằm ở:

```text
HTTP
Network
CPU
SQLite
Disk
Parser
Remote website
```

Do đó cần đo:

```text
claim latency
fetch latency
parse latency
save latency
```

Chứ không đoán.

Observability sẽ học ở Phase X.

---

# 27. Ví dụ thực tế

1000 chapters.

### 1 Worker

```text
1 chapter = 2s

1000 × 2
= 2000s
≈ 33 phút
```

### 5 Worker

Lý thuyết:

```text
2000 / 5
= 400s
≈ 6.7 phút
```

Nhưng thực tế:

```text
HTTP
+
SQLite contention
+
remote server rate limit
```

có thể thành:

```text
8 phút
```

hoặc:

```text
15 phút
```

hoặc thậm chí:

```text
30 phút
```

nếu remote server bắt đầu throttle.

---

# 28. Đừng tạo Worker vô hạn

Sai:

```python
for i in range(100):
    create_worker()
```

Không có nghĩa:

```text
100 Worker = 100x performance
```

Phải xác định:

```text
concurrency budget
```

Ví dụ:

```text
HTTP concurrency = 8
DB writers = controlled
```

---

# 29. Worker Pool

Architecture:

```text
WorkerManager
      │
      ├── Worker 1
      ├── Worker 2
      ├── Worker 3
      └── Worker 4
```

WorkerManager chịu trách nhiệm:

```text
start
stop
join
monitor
```

Worker chỉ chịu trách nhiệm:

```text
process Job
```

Tách responsibilities:

```text
WorkerManager
      ↓
lifecycle

Worker
      ↓
job processing
```

---

# 30. WorkerManager đơn giản

```python
class WorkerManager:

    def __init__(
        self,
        worker_factory,
        count: int,
    ):
        self.worker_factory = worker_factory
        self.count = count
        self.workers = []
        self.threads = []

    def start(self):
        for i in range(self.count):
            worker = self.worker_factory(
                worker_id=f"worker-{i}"
            )

            thread = threading.Thread(
                target=worker.run,
            )

            self.workers.append(worker)
            self.threads.append(thread)

            thread.start()

    def join(self):
        for thread in self.threads:
            thread.join()
```

Sau này có thể mở rộng:

```text
health check
restart
metrics
shutdown
```

---

# 31. Queue phải thread-safe

Nếu nhiều Worker dùng cùng queue:

```text
Worker A ─┐
Worker B ─┤
Worker C ─┼── Queue
Worker D ─┘
```

Queue phải đảm bảo:

```text
dequeue atomic
```

Python:

```python
queue.Queue
```

đã cung cấp thread-safety.

Không tự làm:

```python
self.items.pop(0)
```

mà không synchronization.

---

# 32. SQLite Queue sẽ khó hơn

Nếu Queue nằm trong SQLite:

```text
Worker A ─┐
Worker B ─┤
Worker C ─┼── SQLite jobs
Worker D ─┘
```

thì `dequeue` phải atomic.

Không được:

```sql
SELECT *
FROM jobs
WHERE status = 'pending'
LIMIT 1;
```

rồi:

```sql
UPDATE jobs
SET status = 'processing'
WHERE id = ?;
```

vì:

```text
Worker A → SELECT job 1
Worker B → SELECT job 1
```

Hai Worker cùng lấy Job 1.

---

# 33. Queue Claim cũng phải atomic

Đây là pattern giống Chapter Claim:

```text
Job Queue
   ↓
atomic claim
   ↓
Worker ownership
```

Một lần nữa:

> **Concurrency control phải nằm trong database statement/transaction, không dựa vào Python `if`.**

Đây sẽ là trọng tâm của **Buổi 25 — SQLite Queue Atomic Claim**.

---

# 34. Multiple Workers + Lease

Bây giờ hệ thống hoàn chỉnh hơn:

```text
                 Queue
                   ↓
       ┌───────────┼───────────┐
       ↓           ↓           ↓
   Worker A    Worker B    Worker C
       ↓           ↓           ↓
      CLAIM       CLAIM       CLAIM
       ↓           ↓           ↓
      LEASE       LEASE       LEASE
       ↓           ↓           ↓
   HEARTBEAT   HEARTBEAT   HEARTBEAT
       ↓           ↓           ↓
     PROCESS     PROCESS     PROCESS
       ↓           ↓           ↓
      SAVE        SAVE        SAVE
       ↓           ↓           ↓
    COMPLETE    COMPLETE    COMPLETE
```

Database đảm bảo:

```text
1 Chapter
    ↓
1 active owner
```

tại một thời điểm.

---

# 35. Một Worker có thể xử lý nhiều Job?

Có.

```text
Worker A
 ↓
Job 1
 ↓
Job 2
 ↓
Job 3
 ↓
Job 4
```

Đây là:

```text
sequential worker
```

Hoặc một Worker có thể có concurrency nội bộ:

```text
Worker A
 ├── Task 1
 ├── Task 2
 ├── Task 3
 └── Task 4
```

Nhưng đây là một vấn đề khác:

> **Worker Concurrency Control**

và nằm ở **Buổi 15**.

Hôm nay chỉ tập trung:

```text
Multiple Workers
```

---

# 36. 3 tầng concurrency

Bạn nên phân biệt:

### Level 1 — Multiple Worker

```text
Worker A
Worker B
Worker C
```

### Level 2 — Worker internal concurrency

```text
Worker A
 ├── Task 1
 ├── Task 2
 └── Task 3
```

### Level 3 — Database concurrency

```text
Reader
Writer
Writer
Writer
```

Ba thứ này khác nhau.

---

# 37. Anti-pattern

## ❌ Global SQLite connection

```python
conn = sqlite3.connect(...)
```

dùng cho toàn bộ Worker.

---

## ❌ SELECT rồi UPDATE

```python
state = get()

if state.pending:
    update()
```

---

## ❌ Transaction bao quanh HTTP

```python
with uow:
    claim()
    requests.get(...)
    save()
```

---

## ❌ ACK trước COMMIT

```text
SAVE
 ↓
ACK
 ↓
COMMIT
```

---

## ❌ 100 Worker vì "càng nhiều càng nhanh"

Concurrency phải dựa trên bottleneck.

---

# 38. Architecture hiện tại

Sau Buổi 14:

```text
                        ┌──────────────┐
                        │     Queue    │
                        └──────┬───────┘
                               │
               ┌───────────────┼───────────────┐
               ↓               ↓               ↓
           Worker A        Worker B        Worker C
               │               │               │
               ↓               ↓               ↓
             Claim           Claim           Claim
               │               │               │
               ↓               ↓               ↓
             Lease           Lease           Lease
               │               │               │
               ↓               ↓               ↓
           Heartbeat       Heartbeat       Heartbeat
               │               │               │
               └───────────────┼───────────────┘
                               ↓
                             SQLite
                               ↑
                               │
                         RecoveryService
```

Các nguyên tắc bảo vệ:

```text
Atomic Claim
     +
Worker ID
     +
Lease
     +
Heartbeat
     +
Ownership Check
     +
Crash Recovery
     +
Idempotency
```

---

# 🧠 39. Mental Model

Hãy nhớ câu này:

> **Queue quyết định Job nào cần làm; Database quyết định Worker nào đang sở hữu Job.**

Và:

> **Multiple Workers không giải quyết bằng cách "thêm Thread", mà giải quyết bằng ownership + atomicity + transaction + concurrency control.**

Flow:

```text
Queue
  ↓
Worker nhận Job
  ↓
Atomic Claim
  ↓
Worker trở thành Owner
  ↓
Lease
  ↓
Heartbeat
  ↓
Process
  ↓
Ownership-checked Complete
  ↓
COMMIT
  ↓
ACK
```

Nếu Worker chết:

```text
Heartbeat mất
  ↓
Lease expired
  ↓
Recovery
  ↓
Worker khác
```

---

# 📝 Bài tập Buổi 14

### Bài 1 — Chạy 3 Worker

Tạo:

```text
worker-1
worker-2
worker-3
```

và 20 Job.

Quan sát:

```text
worker-1 → chapter 1
worker-2 → chapter 2
worker-3 → chapter 3
...
```

Không có hai Worker cùng sở hữu một Chapter.

---

### Bài 2 — Test Atomic Claim

Cho:

```text
Worker A
Worker B
```

cùng claim:

```text
novel_id = 1
chapter_number = 100
```

Assert:

```text
A → True
B → False
```

hoặc ngược lại.

Quan trọng là:

```text
exactly one == True
```

---

### Bài 3 — Zombie Worker

Mô phỏng:

```text
Worker A
    ↓
claim
    ↓
lease expire

Worker B
    ↓
reclaim
    ↓
complete

Worker A
    ↓
complete
```

Kết quả:

```text
B → success
A → OwnershipLost
```

---

### Bài 4 — Benchmark

Chạy:

```text
1 Worker
2 Workers
4 Workers
8 Workers
```

đo:

```text
total processing time
jobs/second
SQLite lock errors
```

Bạn sẽ thấy một bài học rất quan trọng:

```text
1 → 2 → 4
```

thường cải thiện.

Nhưng:

```text
4 → 8 → 16
```

không nhất thiết cải thiện.

---

# 🔜 Buổi 15 — Worker Concurrency Control

Ở Buổi 15 chúng ta sẽ đi sâu hơn một cấp:

```text
Multiple Workers
       ↓
Worker Concurrency
       ↓
Concurrency Limit
       ↓
Semaphore
       ↓
HTTP concurrency
       ↓
DB concurrency
       ↓
Per-host concurrency
```

Đặc biệt với **crawler**, đây là vấn đề rất thực tế:

```text
10 Workers
×
mỗi Worker 10 concurrent requests
=
100 HTTP requests
```

có thể biến một crawler nhanh thành một crawler **tự bóp chết chính nó** — hoặc bị website throttle/rate-limit.
