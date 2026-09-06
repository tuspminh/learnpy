# Buổi 13 — Crash Recovery

Ở **Buổi 11–12**, chúng ta đã xây được:

```text
CLAIM
  ↓
LEASE
  ↓
HEARTBEAT
  ↓
PROCESS
  ↓
COMMIT
  ↓
ACK
```

Nhưng nếu Worker chết bất ngờ:

```text
Worker A
   ↓
CLAIM Chapter 100
   ↓
HEARTBEAT
   ↓
💥 CRASH
```

thì hệ thống cần một cơ chế **tự phát hiện và phục hồi Job bị bỏ lại**.

Đó là nội dung của hôm nay.

---

# 1. Crash Recovery là gì?

Crash Recovery là quá trình:

```text
Worker chết
    ↓
Job bị orphan
    ↓
phát hiện Job
    ↓
kiểm tra lease
    ↓
reset/requeue
    ↓
Worker khác xử lý
```

Ví dụ:

```text
Chapter 100

status      = crawling
worker_id   = worker-A
lease_until = 23:00:00
```

Hiện tại:

```text
23:05:00
```

và Worker A đã chết.

Recovery Service phát hiện:

```text
lease_until < NOW()
```

→ Job đã orphan.

---

# 2. Tại sao không chỉ dùng `status`?

Nếu database có:

```text
status = crawling
```

ta không biết:

```text
Worker vẫn chạy?
```

hay:

```text
Worker đã crash?
```

Vì vậy:

```text
status
+
lease_until
```

mới cho ta thông tin đầy đủ.

```text
CRAWLING
   +
lease còn hạn
       ↓
đang được xử lý

CRAWLING
   +
lease hết hạn
       ↓
có khả năng orphan
```

---

# 3. Recovery Service

Không nên để Worker tự recovery chính mình.

Ta tạo một component riêng:

```text
RecoveryService
```

Kiến trúc:

```text
             RecoveryService
                    ↓
        ChapterCrawlStateRepository
                    ↓
                 SQLite
```

Nhiệm vụ:

1. tìm expired lease
2. kiểm tra retry limit
3. reset state
4. tạo/requeue Job
5. ghi log
6. xử lý failure nếu retry đã vượt giới hạn

---

# 4. Tách Recovery khỏi Worker

Worker:

```text
Queue
 ↓
Worker
 ↓
process
```

Recovery:

```text
Scheduler
   ↓
RecoveryService
   ↓
Database
   ↓
Requeue
```

Hai process có thể chạy độc lập:

```text
                 SQLite
                   ↑
          ┌────────┴────────┐
          │                 │
       Worker          Recovery
          │                 │
          ↓                 ↓
        Queue           scan lease
```

Đây là thiết kế tốt hơn nhiều so với:

```text
Worker
 ├── process
 ├── retry
 ├── heartbeat
 ├── recovery
 ├── scheduler
 └── ...
```

tránh tạo **God Worker**.

---

# 5. Query expired jobs

Cơ bản:

```sql
SELECT
    novel_id,
    chapter_number,
    status,
    worker_id,
    lease_until,
    retry_count
FROM chapter_crawl_states
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

Ví dụ kết quả:

```text
novel  chapter  worker      lease
────────────────────────────────────
10     100      worker-A    23:00
10     101      worker-C    23:01
```

Recovery Service biết:

```text
100 → orphan
101 → orphan
```

---

# 6. Recovery không được reset mù quáng

Không làm:

```python
for state in crawling_states:
    state.status = PENDING
```

❌

Phải kiểm tra:

```text
status = crawling
AND lease_until < now
```

Nếu lease còn hiệu lực:

```text
23:05
lease_until = 23:06
```

→ không đụng vào.

---

# 7. Recovery state transition

Ta có:

```text
CRAWLING
   │
   │ lease expired
   ↓
PENDING
```

Nhưng còn:

```text
retry_count
```

Ví dụ:

```text
retry_count = 2
```

Recovery:

```text
retry_count = 3
```

Sau đó Queue lại Job.

---

# 8. Retry limit

Giả sử:

```python
MAX_RETRIES = 3
```

Flow:

```text
attempt 1
   ↓
crash
   ↓
recovery

attempt 2
   ↓
crash
   ↓
recovery

attempt 3
   ↓
crash
   ↓
recovery

attempt 4
   ↓
❌ không retry
   ↓
DLQ / permanent failure
```

Điểm quan trọng:

> **Crash cũng phải được tính là một attempt/retry.**

Không chỉ exception từ processor mới tăng retry count.

---

# 9. Recovery + retry

Ví dụ:

```text
Chapter 100
retry_count = 2
lease expired
```

Recovery:

```text
retry_count = 3
```

Nếu:

```text
3 < MAX_RETRIES
```

→ requeue.

Nếu:

```text
3 >= MAX_RETRIES
```

→ DLQ / FAILED.

---

# 10. Domain model

Ta có thể đưa logic retry vào domain:

```python id="v6d3fk"
from dataclasses import dataclass
from enum import StrEnum


class ChapterStatus(StrEnum):
    PENDING = "pending"
    CRAWLING = "crawling"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ChapterCrawlState:
    novel_id: int
    chapter_number: int

    status: ChapterStatus

    retry_count: int = 0
    error_message: str | None = None

    worker_id: str | None = None
```

Thêm:

```python id="8l9sqf"
def can_retry(self, max_retries: int) -> bool:
    return self.retry_count < max_retries
```

---

# 11. Nhưng recovery không nên load từng record rồi save từng record

Cách này:

```text
SELECT 1000 rows
       ↓
Python loop
       ↓
UPDATE row 1
UPDATE row 2
UPDATE row 3
...
```

có thể tạo rất nhiều round-trip.

Tốt hơn:

```sql
UPDATE ...
WHERE status = 'crawling'
AND lease_until < CURRENT_TIMESTAMP
```

để atomic reset.

---

# 12. Atomic Recovery

Ví dụ:

```sql id="ppv7su"
UPDATE chapter_crawl_states
SET
    status = 'pending',
    worker_id = NULL,
    claimed_at = NULL,
    lease_until = NULL,
    last_heartbeat_at = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

Nhưng có một vấn đề:

> Chúng ta chưa tăng `retry_count`.

Có thể:

```sql id="1s8kl3"
UPDATE chapter_crawl_states
SET
    status = 'pending',
    retry_count = retry_count + 1,
    worker_id = NULL,
    claimed_at = NULL,
    lease_until = NULL,
    last_heartbeat_at = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

---

# 13. Vấn đề MAX_RETRIES

Nếu:

```text
retry_count = 3
MAX_RETRIES = 3
```

không nên:

```text
3 → 4 → PENDING
```

vì như vậy đã vượt giới hạn.

Có thể dùng:

```sql id="v0xqkt"
UPDATE chapter_crawl_states
SET
    status = CASE
        WHEN retry_count + 1 >= ?
            THEN 'failed'
        ELSE 'pending'
    END,

    retry_count = retry_count + 1,

    worker_id = NULL,
    claimed_at = NULL,
    lease_until = NULL,

    updated_at = CURRENT_TIMESTAMP

WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

Đây là một transactionally safe operation.

---

# 14. Nhưng DLQ thì sao?

`FAILED` và `DLQ` là hai khái niệm có thể tách:

```text
Chapter state
    ↓
FAILED
```

còn:

```text
Queue state
    ↓
DLQ
```

Ví dụ:

```text
Chapter
status = failed
```

và:

```text
Job
status = dead
```

Điều này giúp:

```text
Domain state
```

không bị trộn với:

```text
Queue infrastructure state
```

---

# 15. Recovery Service

Một version đơn giản:

```python id="q0m5dj"
class RecoveryService:
    def __init__(
        self,
        uow,
        queue,
        max_retries: int = 3,
    ):
        self.uow = uow
        self.queue = queue
        self.max_retries = max_retries

    def recover(self):
        with self.uow:
            states = self.uow.crawl_states.find_expired()

            for state in states:
                if state.retry_count >= self.max_retries:
                    state.mark_failed(
                        "maximum retries exceeded"
                    )
                else:
                    state.retry()
                    self.uow.crawl_states.save(state)
```

Nhưng code này vẫn chưa hoàn hảo.

Vì:

```text
DB transaction
     ↓
queue.enqueue()
```

đang bị trộn với nhau.

Đây là vấn đề **DB transaction + Queue transaction**.

---

# 16. Đây là vấn đề cực kỳ quan trọng

Giả sử:

```text
BEGIN
 ↓
reset state → PENDING
 ↓
COMMIT
 ↓
enqueue Job
```

Nếu:

```text
enqueue()
```

thất bại:

```text
Database:
PENDING

Queue:
không có Job
```

Chapter bị:

```text
PENDING
```

nhưng không ai xử lý.

Ngược lại nếu:

```text
enqueue Job
 ↓
COMMIT thất bại
```

Queue đã có Job nhưng database vẫn:

```text
CRAWLING
```

Đây là một dạng:

> **Dual-write problem**

---

# 17. Đừng giải quyết dual-write bằng transaction giả

Không thể:

```text
SQLite transaction
+
Redis transaction
```

một cách đơn giản rồi giả định:

```text
atomic across both
```

Đây là lý do các hệ thống production thường dùng:

* Outbox Pattern
* transactional queue
* message broker semantics
* reconciliation
* idempotent enqueue

Sau này chúng ta có thể học **Outbox Pattern** nếu muốn mở rộng roadmap.

---

# 18. Với SQLite Queue thì dễ hơn

Nếu Queue cũng nằm trong SQLite:

```text
SQLite
 ├── chapter_crawl_states
 └── jobs
```

thì có thể:

```text
BEGIN

reset chapter
+
insert job

COMMIT
```

Hai thao tác nằm trong cùng transaction.

Đây là một lợi thế lớn của SQLite Queue.

```text
id="1q4l8a"
Chapter State
      +
Job Queue
      ↓
same transaction
```

Không có dual-write giữa hai hệ thống.

---

# 19. Recovery với SQLite Job Queue

Nếu chúng ta có:

```text
jobs
────────────────────
job_id
novel_id
chapter_number
status
available_at
retry_count
```

Recovery có thể:

```sql
BEGIN;

UPDATE chapter_crawl_states
SET
    status = 'pending',
    ...
WHERE
    status = 'crawling'
    AND lease_until < CURRENT_TIMESTAMP;

INSERT INTO jobs (...)
SELECT ...
FROM chapter_crawl_states
WHERE status = 'pending'
  AND ...;

COMMIT;
```

Nhưng phải thiết kế cẩn thận để không tạo duplicate Job.

---

# 20. Idempotent Requeue

Ví dụ Chapter 100 đã có Job:

```text
job-123
```

Recovery chạy lần nữa.

Không được tạo:

```text
job-456
```

rồi:

```text
job-789
```

→ duplicate vô hạn.

Có thể tạo unique key:

```sql id="g6n9pz"
UNIQUE (
    novel_id,
    chapter_number,
    ...
)
```

hoặc dùng:

```text
job identity
```

deterministic.

Ví dụ:

```text
crawl:novel-10:chapter-100
```

---

# 21. Job ID và Chapter Identity

Đây là hai thứ khác nhau.

### Chapter identity

```text id="j9k0lq"
(novel_id, chapter_number)
```

### Job identity

```text id="kq9k9a"
job_id = UUID
```

Nếu Job bị retry:

```text
job-123
```

có thể tiếp tục retry.

Hoặc hệ thống có thể tạo:

```text
job-456
```

nhưng persistence vẫn dựa trên:

```text
(novel_id, chapter_number)
```

để idempotent.

---

# 22. Recovery không nhất thiết phải enqueue ngay

Một design khác:

```text
Recovery
   ↓
state = PENDING
```

Queue worker tự tìm:

```text
PENDING
```

hoặc scheduler định kỳ enqueue.

Nhưng với Queue architecture của chúng ta, rõ ràng hơn nếu:

```text
Recovery
   ↓
reset state
   ↓
requeue
```

và đảm bảo requeue idempotent.

---

# 23. Recovery chạy định kỳ

Ví dụ:

```text
mỗi 30 giây
```

scheduler:

```python id="6hs5tq"
import time


while True:
    recovery.recover()
    time.sleep(30)
```

Nhưng đây chỉ là demo.

Production nên có:

```text
Recovery Worker
```

hoặc scheduler framework.

---

# 24. Recovery phải idempotent

Đây là nguyên tắc quan trọng.

Nếu chạy:

```text
recover()
```

2 lần:

```text
recover()
recover()
```

thì kết quả cuối cùng phải không bị phá.

Ví dụ:

```text
CRAWLING + expired
```

Lần 1:

```text
PENDING
```

Lần 2:

```text
không còn CRAWLING
```

→ không làm gì.

Điều kiện:

```sql id="xx7h8q"
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP
```

giúp đạt tính chất này.

---

# 25. Race giữa Worker và Recovery

Đây là một race condition quan trọng.

Giả sử:

```text
Worker A
   ↓
heartbeat
```

cùng lúc:

```text
Recovery
   ↓
find expired
```

Có thể xảy ra:

```text
Recovery đọc lease expired
```

nhưng:

```text
Worker A vừa renew lease
```

Nếu thiết kế không atomic, Recovery có thể reclaim nhầm.

---

# 26. Recovery phải atomic

Không:

```text
SELECT expired
    ↓
Python wait
    ↓
UPDATE
```

vì khoảng giữa:

```text
SELECT
   ↓
UPDATE
```

có thể xảy ra heartbeat.

Tốt hơn:

```sql id="y8g9p6"
UPDATE chapter_crawl_states
SET ...
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

SQLite sẽ thực hiện UPDATE dựa trên trạng thái tại thời điểm statement chạy.

Đây là lý do:

> **Concurrency protection nên nằm càng gần database càng tốt.**

---

# 27. Ownership và Recovery

Một Worker cũ:

```text
worker-A
```

không được phép:

```text
complete()
```

sau khi recovery đã reclaim.

Vì:

```sql id="q4n3e6"
AND worker_id = ?
```

nên:

```text
Worker A → rowcount 0
```

Trong khi:

```text
Worker B
```

đã trở thành owner.

---

# 28. Crash Recovery hoàn chỉnh

Bây giờ flow của chúng ta:

```text id="7g5t2e"
                 Queue
                   ↓
                Worker A
                   ↓
                 CLAIM
                   ↓
                LEASE
                   ↓
               HEARTBEAT
                   ↓
                  💥
                CRASH
                   ↓
            Heartbeat stops
                   ↓
             Lease expires
                   ↓
          Recovery Service
                   ↓
            atomic recovery
                   ↓
          retry_count + 1
                   ↓
        ┌──────────┴─────────┐
        ↓                    ↓
    retryable             max retry
        ↓                    ↓
     PENDING               FAILED
        ↓
      Queue
        ↓
    Worker B
```

---

# 29. `started_at` và `claimed_at`

Ta nên phân biệt:

```text
claimed_at
```

với:

```text
started_at
```

Ví dụ:

```text
claim
  ↓
prepare
  ↓
fetch
```

`claimed_at`:

> thời điểm Worker nhận ownership.

`started_at`:

> thời điểm processing thực sự bắt đầu.

Trong hệ thống đơn giản có thể dùng một timestamp.

Trong production monitoring:

```text
claimed_at
started_at
last_heartbeat_at
finished_at
```

có giá trị rất lớn.

---

# 30. Tính thời gian Job

Có thể tính:

```text
processing_duration
```

từ:

```text
finished_at - started_at
```

và:

```text
lease_duration
```

từ:

```text
lease_until - claimed_at
```

Sau này rất hữu ích cho metrics:

```text
P50
P95
P99
```

---

# 31. Recovery không chỉ dành cho crash

Lease expiration còn xử lý:

### Process bị kill

```text
kill -9
```

### Container restart

```text
container restart
```

### Machine crash

```text
server down
```

### Network partition

```text
worker ↔ database
```

### Deadlock / hung worker

```text
Worker sống
nhưng không progress
```

Lease + heartbeat giúp phân biệt:

```text
alive and progressing
```

với:

```text
stale/orphan
```

---

# 32. Một khái niệm mới: Progress

Heartbeat chỉ nói:

> "Tôi vẫn sống."

Nhưng không chứng minh:

> "Tôi đang tiến triển."

Ví dụ Worker:

```text
heartbeat
heartbeat
heartbeat
heartbeat
```

nhưng:

```text
HTTP request bị treo
```

Worker vẫn renew lease mãi.

Đây là một vấn đề nâng cao.

Sau này có thể có:

```text
progress
last_progress_at
```

hoặc timeout riêng cho processing.

---

# 33. Heartbeat ≠ Progress

Nhớ:

```text
Heartbeat
    ↓
Worker alive
```

Trong khi:

```text
Progress
    ↓
Job actually moving forward
```

Ví dụ crawler:

```text
fetch started
response received
parsed
validated
saved
```

Mỗi bước có thể cập nhật progress.

Nhưng **không cần over-engineer ngay**.

Hiện tại:

```text
Heartbeat + Lease
```

đã đủ cho architecture cơ bản.

---

# 34. Recovery Repository API

Một interface đẹp:

```python id="tw4k0y"
from abc import ABC, abstractmethod


class ChapterCrawlStateRepository(ABC):

    @abstractmethod
    def claim(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...

    @abstractmethod
    def renew_lease(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...

    @abstractmethod
    def complete(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...

    @abstractmethod
    def recover_expired(
        self,
        max_retries: int,
    ) -> list:
        ...
```

Infrastructure:

```text id="6f9w7d"
ChapterCrawlStateRepository
          ↑
          │
SQLiteChapterCrawlStateRepository
```

Application:

```text id="7d0i0u"
RecoveryService
      ↓
ChapterCrawlStateRepository
```

---

# 35. Recovery Service tốt hơn

Ta có thể để repository trả về những state vừa được recover:

```python id="hm08ry"
class RecoveryService:

    def __init__(
        self,
        uow,
        queue,
        max_retries=3,
    ):
        self.uow = uow
        self.queue = queue
        self.max_retries = max_retries

    def execute(self):
        with self.uow:
            recovered = (
                self.uow.crawl_states
                .recover_expired(
                    max_retries=self.max_retries
                )
            )

        for state in recovered:
            self.queue.enqueue(
                self._make_job(state)
            )
```

Nhưng vẫn tồn tại:

```text
COMMIT
 ↓
enqueue
```

dual-write.

Đây sẽ là chủ đề kiến trúc nâng cao sau này.

---

# 36. Một giải pháp thực dụng cho crawler hiện tại

Nếu dùng:

```text
SQLite + SQLite Job Queue
```

thì ta có thể làm:

```text
BEGIN
   ↓
recover state
   ↓
insert/requeue job
   ↓
COMMIT
```

Tất cả cùng một database.

Đây là lý do mình khuyến nghị trong giai đoạn học hiện tại:

> **Xây SQLite Job Queue trước khi chuyển sang Redis/RQ.**

Nó giúp bạn hiểu transaction và concurrency thật sâu.

---

# 37. Recovery và `UoW`

Recovery cũng phải tuân thủ nguyên tắc:

```text
RecoveryService
       ↓
      UoW
       ↓
crawl_state_repository
```

Không:

```python id="f8k3r4"
RecoveryService
    ↓
sqlite3.connect()
    ↓
SQL
```

Application không được biết SQLite cụ thể.

---

# 38. Test Crash Recovery

Đây là test rất quan trọng.

Setup:

```text
Chapter 100
status = crawling
worker_id = worker-A
lease_until = quá khứ
retry_count = 0
```

Chạy:

```python id="u6h4v4"
recovery.execute()
```

Assert:

```text
status == pending
retry_count == 1
worker_id is None
lease_until is None
```

---

# 39. Test max retry

Setup:

```text
retry_count = 2
MAX_RETRIES = 3
```

Recovery:

```text
retry_count = 3
status = failed
```

Không:

```text
retry_count = 4
```

---

# 40. Test active lease

Setup:

```text
status = crawling
lease_until = tương lai
```

Recovery:

```python id="94ksvn"
recovery.execute()
```

Assert:

```text
status == crawling
worker_id vẫn giữ nguyên
```

Đây là test chống:

> **false recovery**

---

# 41. Test ownership

Setup:

```text
worker-A
```

Sau recovery:

```text
worker-B
```

Worker A gọi:

```python id="m3w9xq"
complete(..., worker_id="worker-A")
```

Assert:

```text
False
```

Worker B:

```python id="z9s8yd"
complete(..., worker_id="worker-B")
```

→

```text
True
```

Đây là test chống **zombie worker**.

---

# 42. Bức tranh reliability hiện tại

Chúng ta đã xây được:

```text id="o3k4m5"
                    ┌───────────────┐
                    │     Queue     │
                    └───────┬───────┘
                            ↓
                         Worker
                            ↓
                         CLAIM
                            ↓
                          LEASE
                            ↓
                       HEARTBEAT
                            ↓
                          PROCESS
                            ↓
                          COMMIT
                            ↓
                           ACK
```

Failure:

```text id="j9s0gf"
Worker crash
     ↓
Heartbeat stops
     ↓
Lease expires
     ↓
Recovery
     ↓
Retry
     ↓
Queue
     ↓
Worker B
```

Protection:

```text id="8c2qbd"
Atomic Claim
      +
Lease
      +
Heartbeat
      +
Ownership Check
      +
Idempotency
      +
Transaction
      +
Recovery
```

Đây đã bắt đầu giống một **distributed job processing system thực sự**.

---

# 🧠 43. Mental Model của Buổi 10 → 13

Bạn nên nhớ chuỗi này:

```text
Buổi 10
Graceful Shutdown
       ↓
Worker chủ động chết
       ↓
finish current job
       ↓
ACK
```

```text
Buổi 11
Lease
       ↓
Worker có quyền xử lý
       ↓
quyền có expiration
```

```text
Buổi 12
Heartbeat
       ↓
Worker vẫn sống
       ↓
renew lease
```

```text
Buổi 13
Crash Recovery
       ↓
Worker chết
       ↓
heartbeat biến mất
       ↓
lease expired
       ↓
recover
       ↓
retry
```

---

# ⭐ 44. Công thức reliability

Hãy ghi nhớ:

```text id="4s9h2k"
Atomic Claim
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
      +
Transaction
```

Không có một thành phần nào đủ một mình.

Ví dụ:

```text
Lease nhưng không ownership check
```

→ zombie Worker có thể ghi đè.

```text
Heartbeat nhưng không lease
```

→ không có expiration.

```text
Recovery nhưng không idempotency
```

→ có thể tạo duplicate.

```text
ACK trước COMMIT
```

→ có thể mất Job.

---

# 📝 Bài tập Buổi 13

### Bài 1 — `recover_expired()`

Implement:

```python
recover_expired(max_retries=3)
```

Yêu cầu:

```text
CRAWLING
+
lease expired
        ↓
retry_count += 1
```

Nếu chưa vượt giới hạn:

```text
PENDING
```

Nếu vượt:

```text
FAILED
```

---

### Bài 2 — Không recovery Job đang chạy

Test:

```text
CRAWLING
lease_until = tương lai
```

Recovery phải:

```text
không thay đổi
```

---

### Bài 3 — Zombie Worker

Mô phỏng:

```text
Worker A
   ↓
claim
   ↓
lease expires

Worker B
   ↓
reclaim

Worker A
   ↓
complete()
```

Kết quả mong muốn:

```text
Worker A → FAIL
Worker B → SUCCESS
```

---

### Bài 4 — Crash Simulation

Mô phỏng:

```text
Worker A
   ↓
CLAIM
   ↓
HEARTBEAT
   ↓
💥 crash
```

Sau đó:

```text
RecoveryService
   ↓
find expired
   ↓
PENDING
   ↓
requeue
   ↓
Worker B
```

---

# 🔥 Một câu phải nhớ

> **Crash Recovery không cố ngăn Worker chết. Nó thiết kế hệ thống sao cho Worker chết cũng không làm Job chết theo.**

Và architecture của chúng ta hiện tại là:

```text
Worker sống
    ↓
Heartbeat
    ↓
Lease

Worker chết
    ↓
Heartbeat biến mất
    ↓
Lease expired
    ↓
Recovery
    ↓
Retry
    ↓
Worker khác
```

**Buổi 14** sẽ chuyển sang bài tiếp theo trong roadmap: **Multiple Workers — chạy nhiều Worker đồng thời**, tập trung vào race condition, atomic claim, SQLite writer contention và tại sao tăng số Worker không đồng nghĩa với tăng hiệu năng.
