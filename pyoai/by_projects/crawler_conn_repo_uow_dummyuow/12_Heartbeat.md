# Buổi 12 — Heartbeat & Lease Renewal

Ở **Buổi 11**, chúng ta đã xây:

```text
PENDING
   ↓
CLAIM
   ↓
CRAWLING
   +
worker_id
   +
lease_until
```

Lease giải quyết Worker crash.

Nhưng xuất hiện một vấn đề:

```text
Worker A
   ↓
claim
   ↓
lease = 60s
   ↓
HTTP request
   ↓
3 phút...
```

Worker **vẫn sống**, nhưng lease đã hết hạn.

Nếu Recovery Service chạy:

```text
lease expired
    ↓
PENDING
    ↓
Worker B claim
```

thì:

```text
Worker A ──────────────┐
                       ├── Chapter 100
Worker B ──────────────┘
```

Hai Worker cùng xử lý một Chapter.

**Heartbeat** ra đời để giải quyết vấn đề này.

---

# 1. Heartbeat là gì?

Heartbeat là tín hiệu định kỳ mà Worker gửi cho hệ thống để nói:

> "Tôi vẫn còn sống và tôi vẫn đang xử lý Job này."

Ví dụ:

```text
Lease = 60s
Heartbeat = mỗi 20s
```

Flow:

```text
00:00  CLAIM
       lease_until = 01:00

00:20  HEARTBEAT
       lease_until = 01:20

00:40  HEARTBEAT
       lease_until = 01:40

01:00  HEARTBEAT
       lease_until = 02:00
```

Worker vẫn sống:

```text
lease_until
     ↑
luôn được đẩy về tương lai
```

---

# 2. Nếu Worker chết thì sao?

Worker:

```text
00:00 CLAIM
00:20 HEARTBEAT
00:40 HEARTBEAT
```

Sau đó:

```text
💥 Worker crash
```

Heartbeat cũng dừng.

Lease:

```text
00:40
  ↓
lease_until = 01:40
```

Đến:

```text
01:40
```

không còn heartbeat.

Recovery:

```text
lease expired
    ↓
reclaim
```

Đây là điểm rất đẹp của mô hình:

```text
Worker sống
    ↓
Heartbeat
    ↓
Lease được gia hạn

Worker chết
    ↓
Heartbeat biến mất
    ↓
Lease hết hạn
    ↓
Recovery
```

---

# 3. Heartbeat không phải health check

Hai khái niệm này dễ nhầm.

### Worker health check

Trả lời:

> Worker có sống không?

Ví dụ:

```text
worker-A = alive
```

### Job heartbeat

Trả lời:

> Worker có còn đang xử lý **Job cụ thể này** không?

Ví dụ:

```text
worker-A
   ↓
job-123
   ↓
heartbeat
```

Trong crawler của chúng ta, thứ quan trọng hơn là:

```text
Job ownership
```

chứ không chỉ Worker process còn sống.

---

# 4. Schema

Ta đã có:

```sql id="1qwbcs"
worker_id
claimed_at
lease_until
```

Không nhất thiết phải thêm cột `last_heartbeat`.

Nhưng trong production, mình khuyến nghị thêm:

```sql id="oyh6m4"
last_heartbeat_at TEXT
```

Bảng:

```sql id="wmok7p"
CREATE TABLE chapter_crawl_states (
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,

    status TEXT NOT NULL,

    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,

    worker_id TEXT,
    claimed_at TEXT,
    lease_until TEXT,
    last_heartbeat_at TEXT,

    started_at TEXT,
    finished_at TEXT,
    updated_at TEXT,

    PRIMARY KEY (novel_id, chapter_number),

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

---

# 5. Heartbeat SQL

Worker A:

```text id="prl8sk"
worker_id = worker-A
```

Heartbeat:

```sql id="7n9bhy"
UPDATE chapter_crawl_states
SET
    lease_until = datetime('now', '+60 seconds'),
    last_heartbeat_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE novel_id = ?
  AND chapter_number = ?
  AND status = 'crawling'
  AND worker_id = ?;
```

Python:

```python id="v3k2zj"
def renew_lease(
    self,
    novel_id: int,
    chapter_number: int,
    worker_id: str,
) -> bool:

    cursor = self.conn.execute(
        """
        UPDATE chapter_crawl_states
        SET
            lease_until = datetime(
                'now',
                '+60 seconds'
            ),
            last_heartbeat_at = CURRENT_TIMESTAMP,
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

---

# 6. Tại sao phải kiểm tra `worker_id`?

Giả sử:

```text id="cvq1r8"
Worker A
   ↓
claim Job
```

Lease hết hạn:

```text id="jij3da"
Worker A
   ↓
💥
```

Worker B reclaim:

```text id="ck3l5x"
worker-B
   ↓
claim Job
```

Sau đó Worker A bất ngờ sống lại và gửi heartbeat.

Nếu SQL chỉ:

```sql id="m9gzp4"
WHERE novel_id = ?
AND chapter_number = ?
```

Worker A có thể gia hạn lease của Worker B.

❌ Sai.

Phải:

```sql id="ykb6s4"
AND worker_id = ?
```

Kết quả:

```text id="t6f6ll"
Worker A → rowcount = 0
Worker B → vẫn sở hữu Job
```

---

# 7. Heartbeat chính là ownership check

Ta có:

```text id="u4z5m9"
worker_id = worker-A
```

Heartbeat:

```text id="dly9hq"
UPDATE ...
WHERE worker_id = worker-A
```

Nếu thành công:

```text id="7w1kcb"
rowcount = 1
```

→ Worker A vẫn sở hữu Job.

Nếu:

```text id="h9j56p"
rowcount = 0
```

→ Có vấn đề.

Có thể:

* Job đã complete
* Job đã fail
* Lease đã bị reclaim
* Worker không còn owner

Worker **không nên tiếp tục coi mình là owner**.

---

# 8. Heartbeat interval

Giả sử:

```text id="h3j77v"
lease = 60 seconds
```

Không nên heartbeat:

```text id="iqs3jm"
59 seconds
```

vì nếu có delay:

```text
heartbeat
   ↓
network delay
   ↓
lease expired
```

Thông thường có thể chọn:

```text id="yls6pk"
lease duration = 60s
heartbeat      = 20s
```

hoặc:

```text id="4i5w4s"
lease duration = 120s
heartbeat      = 30s
```

Quy tắc thực tế:

```text
heartbeat interval << lease duration
```

Ví dụ:

```text
20s << 60s
```

---

# 9. Đừng heartbeat quá thường xuyên

Không nên:

```text id="0gkq3q"
lease = 60s

heartbeat
heartbeat
heartbeat
heartbeat
...
```

mỗi 100ms.

Vì heartbeat cũng là DB write.

Với:

```text id="iwubk8"
100 workers
```

mỗi worker heartbeat mỗi 100ms:

```text
100 × 10 = 1000 writes/second
```

SQLite sẽ không thích điều này.

Heartbeat phải đủ thưa để:

```text
giảm DB load
```

nhưng đủ nhanh để:

```text
phát hiện Worker chết
```

---

# 10. Heartbeat Worker

Ta có thể tạo:

```python id="yjmuxb"
import threading


class Heartbeat:
    def __init__(
        self,
        renew,
        interval: float = 20.0,
    ):
        self.renew = renew
        self.interval = interval
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.wait(self.interval):
            self.renew()
```

Điểm hay:

```python id="e4bb5c"
self.stop_event.wait(self.interval)
```

thay vì:

```python id="8rj8xu"
time.sleep(self.interval)
```

Vì `Event.wait()` có thể bị đánh thức ngay khi:

```python id="90ms5c"
stop_event.set()
```

---

# 11. Nhưng heartbeat không nên chạy khi Worker idle

Đây là điểm quan trọng.

Không cần:

```text id="v5jmff"
Worker
   ↓
không có Job
   ↓
heartbeat
```

Heartbeat chỉ cần khi:

```text id="28ghpl"
Worker
   ↓
đang sở hữu Job
```

Vì vậy:

```text id="g0f5tj"
Job
 ↓
start heartbeat
 ↓
process
 ↓
stop heartbeat
```

---

# 12. Flow chuẩn

```text id="b9w3o1"
DEQUEUE
   ↓
CLAIM
   ↓
START HEARTBEAT
   ↓
FETCH
   ↓
PARSE
   ↓
SAVE
   ↓
COMMIT
   ↓
STOP HEARTBEAT
   ↓
ACK
```

Nếu processing thất bại:

```text id="4qf6lz"
DEQUEUE
   ↓
CLAIM
   ↓
START HEARTBEAT
   ↓
FETCH
   ↓
ERROR
   ↓
STOP HEARTBEAT
   ↓
FAIL / RETRY
```

---

# 13. Vấn đề concurrency

Heartbeat chạy ở background thread:

```text id="xujr1h"
Main Worker Thread
        │
        ├── fetch()
        │
        ├── parse()
        │
        └── save()
        
Heartbeat Thread
        │
        ├── renew()
        ├── renew()
        └── renew()
```

Điều này có nghĩa:

> Heartbeat thread cần database connection.

Nhưng chúng ta đã học ở Buổi 4:

> **Không chia sẻ SQLite connection giữa các thread.**

Vì vậy không làm:

```python id="4l6bjm"
heartbeat_thread
      ↓
same sqlite3.Connection
```

❌

---

# 14. Connection per thread

Tốt hơn:

```text id="l7z6g1"
Worker Thread
    ↓
UoW
    ↓
Connection A


Heartbeat Thread
    ↓
UoW
    ↓
Connection B
```

Nhưng điều này tạo ra một vấn đề mới:

```text
Heartbeat
    ↓
database
```

có thể chạy đồng thời với:

```text
Worker
    ↓
database
```

Với SQLite, phải cẩn thận về write contention.

---

# 15. Một thiết kế tốt hơn

Thay vì tạo một thread heartbeat riêng cho mọi Job, có thể để Worker tự heartbeat trong những operation dài.

Ví dụ:

```text id="kqj1be"
fetch()
   ↓
periodically renew
```

Nhưng nếu `fetch()` là một HTTP call blocking:

```python id="2o1f4w"
response = httpx.get(...)
```

thì Worker không có cơ hội heartbeat.

Do đó với những tác vụ thực sự dài:

```text id="j1r7dn"
Worker
   ↓
processing
   ├── heartbeat thread/task
   └── main processing
```

là một lựa chọn hợp lý.

---

# 16. Heartbeat Service

Thay vì để Worker tự viết SQL:

```python id="5f9m2w"
worker.conn.execute(...)
```

ta giữ architecture:

```text id="klrj67"
Worker
   ↓
HeartbeatService
   ↓
ChapterCrawlStateRepository
   ↓
SQLite
```

Ví dụ:

```python id="7ql1or"
class HeartbeatService:
    def __init__(
        self,
        crawl_states,
        novel_id,
        chapter_number,
        worker_id,
    ):
        self.crawl_states = crawl_states
        self.novel_id = novel_id
        self.chapter_number = chapter_number
        self.worker_id = worker_id

    def renew(self) -> bool:
        return self.crawl_states.renew_lease(
            novel_id=self.novel_id,
            chapter_number=self.chapter_number,
            worker_id=self.worker_id,
        )
```

Worker không cần biết SQL.

---

# 17. Heartbeat failure

Giả sử:

```text id="4sks8u"
Worker A
   ↓
Job 100
```

Heartbeat:

```text id="0r8ozk"
renew()
```

nhưng:

```text id="q4flj2"
database unavailable
```

Heartbeat thất bại.

Worker phải làm gì?

Không nên ngay lập tức:

```text
💥 kill worker
```

Có thể là:

```text id="y1y4fr"
temporary DB failure
```

Nhưng nếu heartbeat thất bại liên tục:

```text id="u9p2f5"
heartbeat
   ↓ fail
heartbeat
   ↓ fail
heartbeat
   ↓ fail
```

Worker có nguy cơ đã mất ownership.

---

# 18. Ownership Lost

Ta có thể định nghĩa:

```python id="c4q2z4"
class OwnershipLost(Exception):
    pass
```

Heartbeat:

```python id="2d7t6k"
if not renew():
    raise OwnershipLost()
```

Worker:

```text id="w1g2uo"
Heartbeat
   ↓
renew = False
   ↓
OwnershipLost
   ↓
stop processing
```

Nhưng cần cực kỳ cẩn thận:

> Không phải lúc nào heartbeat failure cũng chứng minh ownership đã mất.

Có thể:

```text
DB timeout
network glitch
temporary lock
```

Do đó production thường cần:

```text
consecutive failures
+
lease deadline
```

thay vì chỉ một heartbeat failure.

---

# 19. Lease deadline mới là authority

Điểm này rất quan trọng.

Giả sử:

```text id="s2j5n3"
lease_until = 12:00:00
```

Heartbeat thất bại lúc:

```text id="a3r8tt"
11:59:40
```

Worker vẫn còn lease đến:

```text id="s8b8n5"
12:00:00
```

Không nhất thiết phải bỏ Job ngay.

Nếu heartbeat tiếp theo thành công:

```text id="g0g3sn"
11:59:50
   ↓
renew
   ↓
12:00:50
```

mọi thứ bình thường.

---

# 20. Khi nào Worker thực sự mất ownership?

Một mô hình đơn giản:

```text id="5saj2v"
now < lease_until
    ↓
vẫn còn lease

now >= lease_until
    ↓
lease expired
```

Nếu Worker không thể renew trước deadline:

```text id="r7m5iz"
OWNERSHIP LOST
```

Lúc này Worker không nên:

```text
SAVE
COMPLETED
```

một cách mù quáng.

---

# 21. Race condition cực kỳ thú vị

Xem tình huống:

```text id="7p9t7n"
Worker A
  lease expires
       ↓
Worker B
  reclaim
       ↓
Worker A
  finish processing
```

Worker A muốn:

```text id="09n1y3"
save Chapter
```

Nếu Chapter đã tồn tại:

```text
UPSERT
```

thì dữ liệu có thể vẫn an toàn.

Nhưng state:

```text id="0xg1jc"
Worker A → COMPLETED
```

không được phép ghi đè:

```text id="0p9m1c"
Worker B → CRAWLING
```

Vì vậy ownership check ở persistence state cực kỳ quan trọng.

---

# 22. Chapter save và state transition

Một flow production hơn:

```text id="5s4w3p"
Worker A
   ↓
fetch
   ↓
parse
   ↓
BEGIN
   ↓
save chapter
   ↓
complete WHERE worker_id = A
   ↓
COMMIT
   ↓
ACK
```

Nếu Worker A không còn ownership:

```text id="w2xv0b"
complete()
   ↓
rowcount = 0
```

→ transaction có thể rollback/không commit business completion tùy thiết kế.

Đây là một trong những lý do chúng ta đã học:

```text
Atomic Claim
+
Ownership
+
Idempotency
+
Transaction
```

---

# 23. Heartbeat và UoW

Một câu hỏi quan trọng:

> Heartbeat có nên dùng UoW không?

Có, nhưng transaction phải **cực kỳ ngắn**:

```text id="jqgk4k"
heartbeat
   ↓
BEGIN
   ↓
UPDATE lease
   ↓
COMMIT
```

Không:

```text id="2lvz5t"
BEGIN
   ↓
heartbeat
   ↓
chờ 20s
   ↓
COMMIT
```

---

# 24. Heartbeat transaction

Mỗi heartbeat:

```text id="a1s6o9"
BEGIN
UPDATE lease
COMMIT
```

Chỉ mất vài milliseconds nếu DB bình thường.

Đây là transaction lý tưởng:

```text
short
small
atomic
```

---

# 25. Một Heartbeat Manager hoàn chỉnh hơn

```python id="1o9b0n"
import threading


class HeartbeatManager:
    def __init__(
        self,
        renew,
        interval: float = 20.0,
    ):
        self.renew = renew
        self.interval = interval

        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join()

    def _run(self):
        while not self.stop_event.wait(self.interval):
            try:
                self.renew()
            except Exception:
                # Production:
                # ghi log + theo dõi consecutive failures
                pass
```

Sử dụng:

```python id="a5a3qt"
heartbeat = HeartbeatManager(
    renew=lambda: crawl_states.renew_lease(
        novel_id=job.novel_id,
        chapter_number=job.chapter_number,
        worker_id=worker_id,
    )
)

heartbeat.start()

try:
    processor.process(job)
finally:
    heartbeat.stop()
```

---

# 26. Nhưng code trên có một vấn đề

Ta đang có:

```text id="9h3h5f"
Main thread
    ↓
processor

Heartbeat thread
    ↓
renew()
```

Nếu:

```text id="x6xk3d"
processor.process()
```

hoàn thành rất nhanh:

```text
5ms
```

thì heartbeat thread có thể chưa chạy lần nào.

Không sao.

Flow:

```text id="4zhz2j"
start heartbeat
   ↓
process
   ↓
COMMIT
   ↓
stop heartbeat
```

Job đã xong trước khi heartbeat cần thiết.

---

# 27. Với Job dài

Ví dụ:

```text id="d0sj44"
Chapter processing = 10 minutes
```

Ta có:

```text id="z7a5np"
Lease = 60s
Heartbeat = 20s
```

Timeline:

```text
00:00 CLAIM
       ↓
       lease 01:00

00:20 heartbeat
       ↓
       lease 01:20

00:40 heartbeat
       ↓
       lease 01:40

01:00 heartbeat
       ↓
       lease 02:00

...
```

Cho tới:

```text
10:00 COMMIT
```

→ ACK.

---

# 28. Heartbeat không thay thế Graceful Shutdown

Hai cơ chế giải quyết hai vấn đề khác nhau.

### Graceful Shutdown

```text id="n7e8q5"
Worker chủ động shutdown
```

→ hoàn thành current job.

### Lease

```text id="w7f9o1"
Worker crash
```

→ Job eventually recover.

### Heartbeat

```text id="i4c5fj"
Worker sống lâu
```

→ chứng minh ownership vẫn còn.

Tóm lại:

```text id="v7b2r9"
Graceful Shutdown
       ↓
controlled termination

Lease
       ↓
failure recovery

Heartbeat
       ↓
lease renewal
```

---

# 29. Ba cơ chế phối hợp

Đây là mental model quan trọng:

```text id="h4oz4j"
                    Worker
                      │
          ┌───────────┼────────────┐
          ↓           ↓            ↓
     Shutdown       Lease      Heartbeat
          │           │            │
          ↓           ↓            ↓
      stop safely   recovery   stay owner
```

---

# 30. Architecture hiện tại

Sau Buổi 12:

```text id="qkz9zr"
                         Queue
                           ↓
                        Worker
                           ↓
                       DEQUEUE
                           ↓
                         CLAIM
                           ↓
                    ┌─────────────┐
                    │ Lease       │
                    │ worker_id   │
                    │ lease_until │
                    └──────┬──────┘
                           ↓
                    Heartbeat
                       ↙     ↘
                 renew       renew
                    ↓          ↓
                    └────┬─────┘
                         ↓
                      FETCH
                         ↓
                       PARSE
                         ↓
                     BEGIN
                         ↓
                   SAVE CHAPTER
                         ↓
                COMPLETE + OWNER
                         ↓
                      COMMIT
                         ↓
                        ACK
```

Nếu Worker crash:

```text id="0m9z4b"
Worker
  ↓
💥
  ↓
heartbeat stops
  ↓
lease expires
  ↓
recovery
  ↓
PENDING
```

---

# 31. Một vấn đề mới: Zombie Worker

Đây là khái niệm rất quan trọng.

Giả sử:

```text id="l9y9p7"
Worker A
   ↓
network partition
```

Worker A nghĩ:

> "Tôi vẫn đang xử lý."

Database lại nghĩ:

> "Lease đã hết."

Worker B:

```text id="m1v5za"
reclaim
   ↓
Worker B
```

Bây giờ Worker A trở thành:

> **Zombie Worker**

Nó vẫn chạy nhưng **không còn quyền sở hữu Job**.

Vì vậy mọi thao tác cuối cùng phải có ownership check:

```sql id="80stqk"
AND worker_id = ?
```

Đây là lớp bảo vệ cuối cùng.

---

# 32. Quy tắc vàng

Đừng tin:

```text id="5f2d2f"
"I am Worker A"
```

Hãy để database xác nhận:

```text id="3fj9os"
worker_id = A
AND
status = crawling
AND
lease valid
```

Worker phải chứng minh quyền sở hữu bằng database state.

---

# 33. Design rule rất quan trọng

Chúng ta có thể rút ra:

```text id="x1ezfr"
CLAIM
  ↓
ownership granted

HEARTBEAT
  ↓
ownership renewed

COMPLETE
  ↓
ownership verified

LEASE EXPIRED
  ↓
ownership revoked
```

Đây gần như là một **distributed lease protocol** đơn giản.

---

# 34. Bảng tổng hợp

| Cơ chế              | Mục đích                        |
| ------------------- | ------------------------------- |
| `worker_id`         | xác định owner                  |
| `claimed_at`        | thời điểm claim                 |
| `lease_until`       | thời điểm quyền hết hạn         |
| Heartbeat           | gia hạn quyền                   |
| `last_heartbeat_at` | quan sát liveness               |
| Atomic claim        | tránh hai Worker claim cùng Job |
| Ownership check     | ngăn zombie Worker              |
| Recovery            | reclaim Job orphan              |
| Idempotency         | chịu được xử lý lại             |

---

# 🧠 Mental Model cần ghi nhớ

Hãy nhớ chuỗi:

```text id="w9e4cm"
CLAIM
  ↓
LEASE
  ↓
HEARTBEAT
  ↓
RENEW
  ↓
PROCESS
  ↓
COMMIT
  ↓
ACK
```

Nếu Worker chết:

```text id="f8o7nq"
CLAIM
  ↓
LEASE
  ↓
💥
  ↓
NO HEARTBEAT
  ↓
LEASE EXPIRED
  ↓
RECOVERY
  ↓
RECLAIM
```

Nếu Worker sống:

```text id="h6y8kd"
CLAIM
  ↓
LEASE
  ↓
HEARTBEAT
  ↓
RENEW
  ↓
HEARTBEAT
  ↓
RENEW
  ↓
...
  ↓
COMMIT
  ↓
ACK
```

---

# 📝 Bài tập Buổi 12

### Bài 1 — `renew_lease()`

Tự implement:

```python
renew_lease(
    novel_id,
    chapter_number,
    worker_id,
)
```

với điều kiện:

```text
status = crawling
AND worker_id = current_worker
```

---

### Bài 2 — Heartbeat Manager

Viết:

```python
HeartbeatManager
```

có:

```text
start()
stop()
_run()
```

và heartbeat mỗi `5 giây`.

---

### Bài 3 — Ownership Lost

Mô phỏng:

```text
Worker A
   ↓
claim
   ↓
lease expires
   ↓
Worker B reclaim
   ↓
Worker A heartbeat
```

Kiểm tra:

```text
Worker A → rowcount = 0
Worker B → vẫn owner
```

---

### Bài 4 — Crash Recovery

Mô phỏng:

```text
Worker A
   ↓
CLAIM
   ↓
💥 crash
```

Sau đó chạy:

```python
recover_expired()
```

và kiểm tra:

```text
CRAWLING
    ↓
PENDING
```

---

# 🔥 Một câu phải nhớ

> **Lease trả lời: "Ai đang có quyền xử lý Job?"**

> **Heartbeat trả lời: "Quyền đó còn hiệu lực không?"**

Và:

```text
Graceful Shutdown → Worker chủ động dừng
Lease             → Worker chết được recovery
Heartbeat         → Worker sống được giữ ownership
```

**Buổi 13** sẽ nối trực tiếp từ đây sang **Crash Recovery**: xây một `RecoveryService` thực sự cho crawler, xử lý `CRAWLING` orphan, expired lease, retry count, requeue và tránh recovery nhầm Job đang chạy.
