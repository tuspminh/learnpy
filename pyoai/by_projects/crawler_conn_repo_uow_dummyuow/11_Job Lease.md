# Buổi 11 — Job Lease / Visibility Timeout

Ở **Buổi 10**, chúng ta giải quyết:

> Worker nhận tín hiệu shutdown → dừng nhận Job mới → hoàn thành Job hiện tại → ACK → STOPPED.

Nhưng vẫn còn một tình huống nguy hiểm hơn:

```text
Worker
   ↓
claim Job
   ↓
CRAWLING
   ↓
HTTP request
   ↓
💥 Worker crash
```

Lúc này Job/Chapter có thể bị kẹt mãi ở:

```text
CRAWLING
```

Hôm nay chúng ta xây cơ chế **Lease** để giải quyết vấn đề đó.

---

# 1. Bài toán Worker Crash

Giả sử có:

```text
Chapter 100
status = pending
```

Worker A claim:

```text
Chapter 100
status = crawling
worker_id = worker-A
```

Sau đó:

```text
Worker A
    ↓
fetch()
    ↓
💥 process killed
```

Database:

```text
Chapter 100
status = crawling
worker_id = worker-A
```

Nhưng `worker-A` không còn tồn tại.

Nếu hệ thống chỉ nhìn:

```python
status == "crawling"
```

thì nó sẽ nghĩ:

> Chapter này đang được xử lý.

Trong khi thực tế:

> **Không có Worker nào xử lý nữa.**

---

# 2. Lease là gì?

Lease có thể hiểu đơn giản là:

> **Worker chỉ được quyền xử lý Job trong một khoảng thời gian có giới hạn.**

Ví dụ:

```text
Worker A claim Job
       ↓
lease = 60 seconds
       ↓
23:00:00 ───────── 23:01:00
                       ↑
                  lease expired
```

Nếu Worker hoàn thành:

```text
23:00:30
   ↓
COMPLETED
```

thì không vấn đề gì.

Nhưng nếu Worker chết:

```text
23:00:00
   ↓
claim
   ↓
💥 crash
   ↓
23:01:00
   ↓
lease expired
```

Job có thể được reclaim.

---

# 3. Lease khác với status

Đây là điểm rất quan trọng.

Ta có:

```text
status
```

để biểu diễn **business state**:

```text
PENDING
CRAWLING
COMPLETED
FAILED
```

Còn:

```text
lease_until
```

biểu diễn:

> Worker hiện tại còn quyền xử lý đến khi nào?

Hai thứ này **không giống nhau**.

---

# 4. Thiết kế Crawl State

Ta mở rộng bảng:

```sql
CREATE TABLE chapter_crawl_states (
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,

    status TEXT NOT NULL,

    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,

    worker_id TEXT,
    claimed_at TEXT,
    lease_until TEXT,

    started_at TEXT,
    finished_at TEXT,
    updated_at TEXT,

    PRIMARY KEY (novel_id, chapter_number),

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Bây giờ một record có thể như:

```text
novel_id       = 10
chapter_number = 100

status         = crawling

worker_id      = worker-01
claimed_at     = 2026-09-06 23:00:00
lease_until    = 2026-09-06 23:01:00
```

---

# 5. Worker ID

Tại sao cần `worker_id`?

Giả sử:

```text
Worker A
Worker B
Worker C
```

Nếu database chỉ có:

```text
status = crawling
```

thì không biết ai đang xử lý.

Thêm:

```text
worker_id
```

ta có:

```text
Chapter 100 → worker-A
Chapter 101 → worker-B
Chapter 102 → worker-C
```

Worker ID nên được tạo khi Worker khởi động.

Ví dụ:

```python
from uuid import uuid4


worker_id = f"worker-{uuid4()}"
```

Hoặc đơn giản:

```python
worker_id = "worker-01"
```

trong môi trường development.

---

# 6. Claim Job với Lease

Ta không muốn:

```text
SELECT
   ↓
Python kiểm tra
   ↓
UPDATE
```

vì có race condition.

Ta muốn một thao tác atomic.

Ví dụ SQLite:

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

Python:

```python
cursor = conn.execute(
    """
    UPDATE chapter_crawl_states
    SET
        status = 'crawling',
        worker_id = ?,
        claimed_at = CURRENT_TIMESTAMP,
        lease_until = datetime('now', '+60 seconds'),
        updated_at = CURRENT_TIMESTAMP
    WHERE novel_id = ?
      AND chapter_number = ?
      AND status = 'pending'
    """,
    (worker_id, novel_id, chapter_number),
)
```

Sau đó:

```python
if cursor.rowcount == 1:
    return True

return False
```

---

# 7. Tại sao `rowcount` quan trọng?

Giả sử:

```text
Chapter 100 = PENDING
```

Có hai Worker:

```text
Worker A
Worker B
```

Cả hai cùng claim.

Database xử lý:

```text
Worker A
UPDATE ... WHERE status='pending'
```

→ `rowcount = 1`

Chapter:

```text
CRAWLING
```

Sau đó Worker B:

```text
UPDATE ... WHERE status='pending'
```

Điều kiện không còn đúng:

```text
status != pending
```

→

```text
rowcount = 0
```

Kết quả:

```text
Worker A → CLAIMED ✅
Worker B → NOT CLAIMED ❌
```

Đây chính là:

> **Atomic Claim**

---

# 8. Lease expiration

Giả sử:

```text
lease_until = 23:01:00
```

Hiện tại:

```text
23:02:00
```

thì:

```text
lease_until < current_time
```

→ lease hết hạn.

Ta có thể tìm các record:

```sql
SELECT *
FROM chapter_crawl_states
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

Đây là những Job có khả năng:

```text
Worker đã chết
```

hoặc:

```text
Worker bị network/process failure
```

---

# 9. Recovery expired lease

Có thể reset:

```sql
UPDATE chapter_crawl_states
SET
    status = 'pending',
    worker_id = NULL,
    claimed_at = NULL,
    lease_until = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE status = 'crawling'
  AND lease_until < CURRENT_TIMESTAMP;
```

Sau đó:

```text
PENDING
   ↓
Queue
   ↓
Worker mới
```

---

# 10. Nhưng có một vấn đề cực kỳ nguy hiểm

Hãy tưởng tượng:

```text
Lease = 60s
```

Worker A đang xử lý:

```text
23:00:00 claim
```

HTTP request rất chậm.

```text
23:00:59
```

Worker A vẫn đang xử lý.

Lease hết hạn:

```text
23:01:00
```

Recovery process thấy:

```text
lease expired
```

và đưa Job về:

```text
PENDING
```

Worker B claim:

```text
Worker B
   ↓
Chapter 100
```

Bây giờ:

```text
Worker A ────────┐
                 ├── Chapter 100
Worker B ────────┘
```

**Hai Worker cùng xử lý một Chapter.**

Đây chính là lý do chúng ta cần **Heartbeat**.

---

# 11. Lease phải phù hợp với thời gian xử lý

Nếu Chapter thường xử lý:

```text
5–10 seconds
```

có thể lease:

```text
60 seconds
```

Nhưng nếu:

```text
fetch + parse
```

có thể mất:

```text
5 minutes
```

thì lease 60 giây quá ngắn.

Ta có hai hướng:

### Cách 1

Lease rất dài:

```text
10 minutes
```

Nhược điểm:

Worker chết → phải đợi 10 phút mới recovery.

### Cách 2

Lease ngắn + Heartbeat.

```text
lease = 60s

Worker
   ↓
heartbeat
   ↓
extend 60s
   ↓
heartbeat
   ↓
extend 60s
```

Đây là cách production thường linh hoạt hơn.

---

# 12. Heartbeat concept

Worker:

```text
claim
  ↓
lease_until = T + 60s
  ↓
processing
  ↓
heartbeat
  ↓
lease_until = T + 60s
  ↓
processing
  ↓
heartbeat
  ↓
...
```

Nếu Worker sống:

```text
lease luôn được gia hạn
```

Nếu Worker chết:

```text
heartbeat dừng
       ↓
lease hết hạn
       ↓
recovery
```

Buổi 12 chúng ta sẽ đi sâu vào phần này.

---

# 13. Claim và Save phải kiểm tra ownership

Có một lỗi tinh vi khác.

Worker A claim:

```text
worker-A
```

Sau đó lease hết hạn.

Worker B claim:

```text
worker-B
```

Worker A bất ngờ xử lý xong và muốn:

```text
COMPLETED
```

Nếu câu SQL chỉ là:

```sql
UPDATE chapter_crawl_states
SET status = 'completed'
WHERE novel_id = ?
  AND chapter_number = ?;
```

Worker A có thể **ghi đè trạng thái của Worker B**.

❌ Không được.

---

# 14. Ownership check

Phải kiểm tra:

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
worker_id = worker-A
```

Nếu Job hiện thuộc:

```text
worker-B
```

thì:

```text
rowcount = 0
```

→ Worker A không còn quyền hoàn thành Job.

Đây là một ý tưởng rất quan trọng:

> **Lease không chỉ để recovery; nó còn tạo ra ownership.**

---

# 15. State + Lease + Ownership

Ta bắt đầu có mô hình:

```text
Chapter State
│
├── status
│
├── worker_id
│
├── claimed_at
│
└── lease_until
```

Ví dụ:

```text
┌─────────────────────────────────┐
│ Chapter 100                     │
├─────────────────────────────────┤
│ status      = crawling          │
│ worker_id   = worker-A          │
│ claimed_at  = 23:00:00          │
│ lease_until = 23:01:00          │
└─────────────────────────────────┘
```

---

# 16. Một cách thiết kế tốt hơn

Thay vì recovery chỉ dựa trên:

```text
status = crawling
```

ta có:

```text
status = crawling
AND lease_until < now
```

Nghĩa là:

```text
CRAWLING + lease còn hạn
        ↓
đang được xử lý

CRAWLING + lease hết hạn
        ↓
có khả năng orphan
```

---

# 17. Lease không phải Lock

Đây là distinction rất quan trọng.

### Lock

Ý tưởng:

```text
"Không ai khác được đụng vào."
```

### Lease

Ý tưởng:

```text
"Bạn được quyền xử lý trong khoảng thời gian này."
```

Lease có expiration:

```text
23:00 → 23:01
```

Sau đó:

```text
quyền xử lý hết hạn
```

Điều này đặc biệt hữu ích khi Worker có thể:

```text
crash
kill -9
machine failure
network partition
container restart
```

---

# 18. Lease trong kiến trúc của chúng ta

Toàn bộ flow hiện tại:

```text
                   Queue
                     ↓
                  Worker
                     ↓
              ┌──────────────┐
              │    CLAIM     │
              │              │
              │ worker_id    │
              │ lease_until  │
              └──────┬───────┘
                     ↓
                   COMMIT
                     ↓
              HTTP FETCH
                     ↓
                  PARSE
                     ↓
              ┌──────────────┐
              │ SAVE         │
              │              │
              │ Chapter      │
              │ State        │
              └──────┬───────┘
                     ↓
                  COMMIT
                     ↓
                    ACK
```

Nếu Worker crash:

```text
CLAIM
  ↓
lease
  ↓
💥
  ↓
lease expires
  ↓
recovery
  ↓
PENDING
  ↓
Queue
```

---

# 19. Một Service riêng cho Lease

Đừng nhét toàn bộ logic vào Worker.

Ta có thể tạo abstraction:

```python
from abc import ABC, abstractmethod


class ChapterLeaseRepository(ABC):

    @abstractmethod
    def claim(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...

    @abstractmethod
    def renew(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...

    @abstractmethod
    def release(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:
        ...
```

Nhưng ở architecture của chúng ta, có thể gộp vào:

```text
ChapterCrawlStateRepository
```

vì Lease là một phần của crawl state.

Ví dụ:

```python
class ChapterCrawlStateRepository:
    def claim(...):
        ...

    def renew_lease(...):
        ...

    def complete(...):
        ...

    def fail(...):
        ...

    def recover_expired(...):
        ...
```

---

# 20. Repository không quyết định business transition

Nhắc lại nguyên tắc từ Buổi 8.

Không nên để Repository tự quyết định:

```text
PENDING → CRAWLING
```

Business/domain mới quyết định transition.

Repository chủ yếu:

```text
load
save
atomic update
```

Một thiết kế tốt có thể là:

```text
Domain
   ↓
ChapterCrawlState.start()
   ↓
Application
   ↓
Repository
   ↓
SQL atomic claim
```

Trong các trường hợp concurrency, SQL vẫn cần điều kiện atomic để bảo vệ invariant ở database level.

---

# 21. Lease transaction phải ngắn

Claim:

```text
BEGIN
  UPDATE ...
COMMIT
```

Sau đó:

```text
HTTP
```

Không được:

```text
BEGIN
   ↓
CLAIM
   ↓
HTTP 30s
   ↓
SAVE
   ↓
COMMIT
```

Nhắc lại kiến trúc:

```text
Transaction #1
────────────────
CLAIM
COMMIT


Network
────────────────
FETCH
PARSE


Transaction #2
────────────────
SAVE CHAPTER
UPDATE STATE
COMMIT


ACK
```

Đây là kiến trúc rất quan trọng đối với crawler.

---

# 22. Lease timeout bao nhiêu?

Không có một con số cố định.

Ví dụ:

```text
Average processing = 10s
P95 processing     = 30s
```

Có thể:

```text
lease = 60s
```

Nếu:

```text
Average = 30s
P95     = 2min
```

thì:

```text
lease = 3min
```

Hoặc:

```text
lease = 60s
heartbeat mỗi 20s
```

Nguyên tắc:

```text
heartbeat interval
        <
lease duration
```

Ví dụ:

```text
lease = 60s
heartbeat = 20s
```

Nếu Worker chết, hệ thống không cần chờ quá lâu.

---

# 23. Crash Recovery hoàn chỉnh

Giả sử:

```text
Worker A
   ↓
claim Chapter 100
   ↓
lease_until = 23:01
   ↓
HTTP
   ↓
💥 crash
```

Recovery process chạy:

```text
23:02
   ↓
find expired lease
   ↓
Chapter 100
   ↓
reset PENDING
```

Sau đó:

```text
PENDING
   ↓
enqueue
   ↓
Worker B
   ↓
claim
   ↓
fetch
   ↓
save
   ↓
COMMIT
   ↓
ACK
```

Đây là **self-healing workflow**.

---

# 24. Nhưng đừng vội reset mọi `CRAWLING`

Điều kiện phải là:

```sql
WHERE status = 'crawling'
AND lease_until < CURRENT_TIMESTAMP
```

Không phải:

```sql
WHERE status = 'crawling'
```

Nếu không:

```text
Worker A đang chạy bình thường
```

cũng bị recovery process lấy mất.

---

# 25. Job state và Chapter state

Chúng ta tiếp tục phải phân biệt hai thứ:

```text
Job
```

và:

```text
Chapter Crawl State
```

Ví dụ:

```text
Job
────────────────
job_id
retry_count
queue state
```

Trong khi:

```text
ChapterCrawlState
────────────────────
novel_id
chapter_number
status
worker_id
lease_until
```

Quan hệ:

```text
Queue Job
    ↓
Worker
    ↓
Chapter Crawl State
```

Một Job có thể retry nhiều lần.

---

# 26. Toàn bộ reliability model đến Buổi 11

Hiện tại chúng ta đã có:

```text
             Queue
                ↓
             Worker
                ↓
             Atomic Claim
                ↓
              Lease
                ↓
             HTTP/Parse
                ↓
          Transaction
                ↓
              COMMIT
                ↓
               ACK
```

Nếu:

```text
processing error
```

→ Retry.

Nếu:

```text
worker crash
```

→ Lease expires.

Nếu:

```text
lease expires
```

→ Recovery.

Nếu:

```text
ACK thất bại
```

→ Job có thể chạy lại.

Vì vậy:

```text
Lease
+
Retry
+
Idempotency
+
Atomic Claim
+
Transaction
```

tạo thành nền tảng reliability.

---

# 27. Code mẫu: Claim

Một implementation đơn giản:

```python
class SQLiteChapterCrawlStateRepository:

    def __init__(self, conn, lease_seconds: int = 60):
        self.conn = conn
        self.lease_seconds = lease_seconds

    def claim(
        self,
        novel_id: int,
        chapter_number: int,
        worker_id: str,
    ) -> bool:

        cursor = self.conn.execute(
            """
            UPDATE chapter_crawl_states
            SET
                status = 'crawling',
                worker_id = ?,
                claimed_at = CURRENT_TIMESTAMP,
                lease_until = datetime(
                    'now',
                    ?
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE novel_id = ?
              AND chapter_number = ?
              AND status = 'pending'
            """,
            (
                worker_id,
                f"+{self.lease_seconds} seconds",
                novel_id,
                chapter_number,
            ),
        )

        return cursor.rowcount == 1
```

Lưu ý:

```python
f"+{self.lease_seconds} seconds"
```

ở đây chỉ tạo **SQLite datetime modifier**, không phải SQL identifier hay raw user input.

Trong hệ thống thực tế, ta cũng có thể tính `lease_until` ở Python và truyền timestamp parameter vào SQL.

---

# 28. Code mẫu: Complete với ownership

```python
def complete(
    self,
    novel_id: int,
    chapter_number: int,
    worker_id: str,
) -> bool:

    cursor = self.conn.execute(
        """
        UPDATE chapter_crawl_states
        SET
            status = 'completed',
            worker_id = NULL,
            lease_until = NULL,
            finished_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE novel_id = ?
          AND chapter_number = ?
          AND status = 'crawling'
          AND worker_id = ?
        """,
        (
            novel_id,
            chapter_number,
            worker_id,
        ),
    )

    return cursor.rowcount == 1
```

Điểm quan trọng:

```sql
AND worker_id = ?
```

Ngăn Worker cũ ghi đè Worker mới.

---

# 29. Code mẫu: Recovery

```python
def recover_expired(self) -> int:
    cursor = self.conn.execute(
        """
        UPDATE chapter_crawl_states
        SET
            status = 'pending',
            worker_id = NULL,
            claimed_at = NULL,
            lease_until = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE status = 'crawling'
          AND lease_until < CURRENT_TIMESTAMP
        """
    )

    return cursor.rowcount
```

Use Case/Recovery Service:

```python
with uow:
    recovered = uow.crawl_states.recover_expired()
```

Sau đó các chapter `PENDING` có thể được đưa lại Queue.

---

# 30. Tư duy kiến trúc quan trọng nhất

Đừng nghĩ:

> "Lease là một timeout cho Worker."

Hãy nghĩ:

> **Lease là quyền sở hữu tạm thời của Worker đối với một Job.**

```text
Worker A
   │
   │ claim
   ↓
┌─────────────────────┐
│ Chapter 100         │
│ owner = Worker A    │
│ lease_until = T     │
└─────────────────────┘
```

Trong khoảng:

```text
now < lease_until
```

Worker A có quyền xử lý.

Sau:

```text
now >= lease_until
```

quyền đó có thể được thu hồi.

---

# 🧠 Checklist Buổi 11

Sau bài này bạn cần giải thích được:

* [x] Worker crash gây ra vấn đề gì?
* [x] Lease là gì?
* [x] Visibility timeout là gì?
* [x] `lease_until` dùng để làm gì?
* [x] Vì sao cần `worker_id`?
* [x] Vì sao claim phải atomic?
* [x] Vì sao `rowcount == 1` quan trọng?
* [x] Vì sao `complete()` phải kiểm tra `worker_id`?
* [x] Lease hết hạn được recovery thế nào?
* [x] Vì sao lease quá ngắn gây duplicate processing?
* [x] Vì sao cần heartbeat?
* [x] Vì sao transaction không được bao quanh HTTP request?

---

# 🔥 Mental Model của Buổi 10 + 11

Hãy ghi nhớ hai bài này như một cặp:

```text
BUỔI 10
Graceful Shutdown
        ↓
Worker chủ động dừng
        ↓
finish current job
        ↓
ACK
        ↓
STOPPED
```

```text
BUỔI 11
Lease
        ↓
Worker bị chết bất ngờ
        ↓
lease expires
        ↓
Recovery
        ↓
PENDING
        ↓
Worker khác xử lý
```

Nói ngắn gọn:

> **Graceful Shutdown xử lý Worker chết có kiểm soát.**

> **Lease xử lý Worker chết bất ngờ.**

Và ở **Buổi 12 — Heartbeat**, chúng ta sẽ giải quyết trường hợp còn khó hơn:

```text
Worker A
   ↓
claim
   ↓
lease 60s
   ↓
HTTP request 5 phút
   ↓
???
```

→ Làm thế nào để Worker chứng minh rằng **nó vẫn còn sống và vẫn đang sở hữu Job** mà không bị Worker khác reclaim.
