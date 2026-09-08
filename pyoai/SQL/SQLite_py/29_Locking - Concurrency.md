# Buổi 29 — SQLite Locking & Concurrency

Ở Buổi 28 ta đã học:

```text
WAL
 ↓
Reader/Writer concurrency tốt hơn
```

Nhưng có một sự thật cực kỳ quan trọng:

> **WAL không loại bỏ SQLite locking.**

Nếu app crawler của bạn có nhiều Worker cùng ghi database, sớm muộn bạn sẽ gặp:

```text
sqlite3.OperationalError:
database is locked
```

Hôm nay chúng ta hiểu **vì sao**, **khi nào xảy ra**, và **thiết kế thế nào để tránh**.

---

# 1. SQLite concurrency là gì?

Giả sử app của bạn có:

```text
Crawler
 ├── Worker 1
 ├── Worker 2
 ├── Worker 3
 └── Worker 4

Dashboard
 └── Reader
```

Tất cả cùng truy cập:

```text
novel.db
```

Ta có:

```text
             SQLite
               │
       ┌───────┼────────┐
       │       │        │
    Worker1 Worker2  Dashboard
       │       │        │
       └───────┴────────┘
               │
            novel.db
```

Đây chính là **concurrency**.

---

# 2. SQLite có nhiều connection được không?

**Có.**

Ví dụ:

```python
conn1 = sqlite3.connect("novel.db")
conn2 = sqlite3.connect("novel.db")
conn3 = sqlite3.connect("novel.db")
```

Ba connection có thể cùng tồn tại.

```text
conn1 ──┐
conn2 ──┼──► novel.db
conn3 ──┘
```

Nhưng điều đó **không có nghĩa** ba connection có thể ghi đồng thời tùy ý.

---

# 3. Quy tắc quan trọng nhất

Hãy nhớ:

> **SQLite cho phép nhiều reader, nhưng writer vẫn bị giới hạn.**

Đặc biệt với WAL:

```text
Reader 1 ──────── READ
Reader 2 ──────── READ
Reader 3 ──────── READ

Writer ────────── WRITE
```

nhiều reader có thể hoạt động tốt trong khi writer ghi WAL.

Nhưng:

```text
Writer 1 ──┐
Writer 2 ──┼──► SQLite
Writer 3 ──┘
```

không phải ba writer cùng ghi transaction độc lập vào SQLite tại cùng một thời điểm.

SQLite vẫn phải **serialize việc ghi**.

---

# 4. Vì sao xảy ra `database is locked`?

Ví dụ:

```text
Worker A
   │
   ▼
BEGIN
   │
   ▼
WRITE
   │
   │
   │   Worker B
   │      │
   │      ▼
   │     WRITE
   │
   ▼
COMMIT
```

Worker B có thể phải chờ Worker A.

Nếu không thể lấy được lock:

```text
sqlite3.OperationalError:
database is locked
```

---

# 5. Ví dụ đơn giản

Tạo database:

```python
import sqlite3

conn = sqlite3.connect("novel.db")

conn.execute("""
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

conn.commit()
conn.close()
```

Bây giờ tạo hai connection:

```python
conn1 = sqlite3.connect("novel.db")
conn2 = sqlite3.connect("novel.db")
```

Worker 1:

```python
conn1.execute("BEGIN")

conn1.execute(
    """
    INSERT INTO novels(title)
    VALUES (?)
    """,
    ("Novel A",),
)
```

Worker 1 chưa:

```python
conn1.commit()
```

Trong lúc đó Worker 2:

```python
conn2.execute(
    """
    INSERT INTO novels(title)
    VALUES (?)
    """,
    ("Novel B",),
)
```

Có thể gặp:

```text
database is locked
```

---

# 6. Vì sao transaction dài nguy hiểm?

Đây là lỗi thiết kế rất phổ biến:

```python
conn.execute("BEGIN")

crawl_from_web()

parse_html()

time.sleep(10)

conn.execute(...)

conn.commit()
```

Transaction tồn tại trong thời gian:

```text
10+ seconds
```

Trong khoảng đó writer khác có thể phải chờ.

---

# 7. Transaction ngắn

Thiết kế tốt:

```text
HTTP
 ↓
Parse
 ↓
Validate
 ↓
Prepare
 ↓
BEGIN
 ↓
INSERT/UPDATE
 ↓
COMMIT
```

Ví dụ:

```python
chapter = crawl_chapter(url)

data = parse_chapter(chapter)

with UnitOfWork(conn) as uow:
    uow.chapters.add(data)
```

Transaction chỉ bao quanh database work.

---

# 8. `timeout` trong sqlite3

Python:

```python
sqlite3.connect(
    "novel.db",
    timeout=5.0,
)
```

nghĩa là connection có thể chờ một khoảng thời gian khi database đang bận trước khi báo lỗi.

Ví dụ:

```python
conn = sqlite3.connect(
    "novel.db",
    timeout=5.0,
)
```

Không nên hiểu:

> timeout = giải quyết concurrency.

Không.

Nó chỉ giúp:

```text
Writer B
   │
   ▼
Database busy
   │
   ▼
chờ
   │
   ├── Writer A COMMIT
   │
   ▼
B tiếp tục
```

Nếu Writer A giữ lock quá lâu:

```text
Writer B
   │
   ▼
wait 5s
   │
   ▼
database is locked
```

---

# 9. `busy_timeout`

Ta cũng có:

```sql
PRAGMA busy_timeout = 5000;
```

Python:

```python
conn.execute("PRAGMA busy_timeout = 5000")
```

Ý nghĩa:

```text
database busy
      │
      ▼
wait up to 5000 ms
      │
      ├── lock released → continue
      │
      └── still locked → error
```

---

# 10. `timeout` và `busy_timeout`

Ta thường cấu hình:

```python
conn = sqlite3.connect(
    "novel.db",
    timeout=5.0,
)

conn.execute("PRAGMA busy_timeout = 5000")
```

Nhưng trong thiết kế thực tế cần hiểu rõ rằng đây là **cơ chế chờ**, không phải giải pháp cho transaction architecture.

Quan trọng hơn vẫn là:

```text
short transaction
+
reasonable writer concurrency
```

---

# 11. WAL giải quyết vấn đề gì?

WAL rất tốt cho:

```text
Reader
   ↕
Writer
```

Ví dụ:

```text
Dashboard
   │
 SELECT
   │
   ▼
SQLite WAL
   ▲
   │
 INSERT
   │
Crawler
```

Reader ít bị writer block hơn.

Nhưng WAL không biến:

```text
Worker 1
Worker 2
Worker 3
Worker 4
```

thành bốn writer SQLite độc lập.

---

# 12. SQLite có một Writer tại một thời điểm

Đây là mental model rất quan trọng:

```text
             SQLite
               │
        ┌──────┴──────┐
        │             │
      Readers       Writer
      nhiều          1
```

Vì vậy nếu bạn có:

```text
20 crawler workers
```

không có nghĩa:

```text
20 concurrent SQLite writers
```

---

# 13. Nhưng 20 Worker vẫn có thể tồn tại

Ví dụ:

```text
Worker 1 ── HTTP ──┐
Worker 2 ── HTTP ──┤
Worker 3 ── HTTP ──┤
Worker 4 ── HTTP ──┤
                   ▼
                Database
```

Đây lại là thiết kế tốt.

Bởi phần lớn thời gian worker đang:

```text
HTTP
parse
CPU
```

chứ không phải:

```text
WRITE SQLite
```

Ta có thể tổ chức:

```text
20 concurrent HTTP workers
           │
           ▼
      prepare data
           │
           ▼
   short DB transactions
```

---

# 14. Đây là kiến trúc crawler tôi muốn bạn nhớ

```text
              HTTP Workers
        ┌──────┬──────┬──────┐
        ▼      ▼      ▼      ▼
      fetch  fetch  fetch  fetch
        │      │      │      │
        └──────┴──────┴──────┘
                   │
                 parse
                   │
               prepare
                   │
                   ▼
             SQLite Writer
                   │
                   ▼
               UnitOfWork
                   │
                   ▼
                SQLite WAL
```

Thay vì:

```text
20 workers
   │
   ├── WRITE
   ├── WRITE
   ├── WRITE
   └── WRITE
```

ta có thể kiểm soát việc ghi.

---

# 15. Pattern: Single Writer

Một pattern rất phù hợp với SQLite:

```text
Workers
 ├── Worker 1
 ├── Worker 2
 ├── Worker 3
 └── Worker 4
        │
        ▼
      Queue
        │
        ▼
   DB Writer
        │
        ▼
     SQLite
```

Ví dụ:

```text
HTTP workers
      │
      ▼
 queue.Queue
      │
      ▼
Database Writer
      │
      ▼
SQLite
```

Lúc này:

```text
N workers
+
1 DB writer
```

SQLite rất dễ chịu.

---

# 16. Python example

Worker:

```python
queue.put(
    {
        "novel_id": novel_id,
        "chapter_number": number,
        "title": title,
        "content": content,
    }
)
```

Database writer:

```python
while True:
    chapter = queue.get()

    with UnitOfWork(conn) as uow:
        uow.chapters.add(chapter)

    queue.task_done()
```

Kiến trúc:

```text
Worker
  │
  ▼
Queue
  │
  ▼
DB Writer
  │
  ▼
UoW
  │
  ▼
SQLite
```

---

# 17. Tại sao Single Writer tốt?

Giảm:

```text
writer contention
database is locked
```

và đơn giản hóa:

```text
transaction management
error handling
retry
batching
```

Ví dụ DB writer có thể gom:

```text
chapter 1
chapter 2
chapter 3
chapter 4
```

thành một transaction:

```sql
BEGIN;

INSERT chapter 1;
INSERT chapter 2;
INSERT chapter 3;
INSERT chapter 4;

COMMIT;
```

---

# 18. Nhưng không phải lúc nào cũng cần Single Writer

Nếu application nhỏ:

```text
1 GUI
+
1 crawler worker
```

thì:

```text
WAL
+
short transactions
+
busy_timeout
```

thường đã đủ.

Không nên over-engineering.

---

# 19. Thread và SQLite

Python `sqlite3` có khái niệm:

```python
check_same_thread = True
```

mặc định.

Ví dụ:

```python
conn = sqlite3.connect("novel.db")
```

Connection thường được tạo ở thread nào thì nên sử dụng ở thread đó.

Đây là lý do pattern:

```text
1 connection
      │
      ├── Thread A
      ├── Thread B
      └── Thread C
```

không phải cách thiết kế tốt.

---

# 20. Tốt hơn: mỗi thread có connection riêng

Mô hình:

```text
Thread A ── Connection A ──┐
Thread B ── Connection B ──┼──► SQLite
Thread C ── Connection C ──┘
```

Mỗi worker có connection riêng.

Ví dụ:

```python
def worker():
    conn = sqlite3.connect(
        "novel.db",
        timeout=5.0,
    )

    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("PRAGMA journal_mode = WAL")

    # work...

    conn.close()
```

Hoặc tốt hơn nữa, dùng `ConnectionManager`.

---

# 21. Không nên dùng một global connection cho mọi thread

Ví dụ:

```python
conn = sqlite3.connect("novel.db")


def worker_a():
    conn.execute(...)


def worker_b():
    conn.execute(...)


def worker_c():
    conn.execute(...)
```

Đây là thiết kế dễ gây vấn đề.

Tốt hơn:

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

---

# 22. Process cũng tương tự

Nếu dùng:

```python
ProcessPoolExecutor
```

thì **không truyền một SQLite connection đang mở** từ process cha cho các worker process.

Không làm kiểu:

```python
conn = sqlite3.connect("novel.db")

executor.submit(worker, conn)
```

Thay vào đó process tự tạo connection của nó:

```python
def worker(...):
    conn = manager.connect()

    ...
    
    conn.close()
```

---

# 23. Locking trong WAL

Mental model đơn giản:

```text
WAL

Readers
   │
   ├── snapshot
   ├── snapshot
   └── snapshot

Writer
   │
   ▼
 WAL
```

Nhưng khi writer cạnh tranh:

```text
Writer A
   │
   ▼
WRITE
   │
   ├──────────────► COMMIT

Writer B
   │
   ▼
WAIT
```

Nếu chờ quá lâu:

```text
database is locked
```

---

# 24. Một nguyên nhân rất nguy hiểm: transaction mở quên commit

Ví dụ:

```python
conn.execute("BEGIN")

conn.execute("INSERT INTO novels(title) VALUES (?)", ("Novel A",))

# quên commit
```

Connection vẫn có transaction đang mở.

Có thể gây ra:

```text
lock lâu
↓
writer khác chờ
↓
database is locked
```

Vì vậy UoW/context manager rất quan trọng.

---

# 25. UoW giúp quản lý transaction

Ta đã xây ở Buổi 27:

```python
class UnitOfWork:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn.execute("BEGIN")
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
```

Sử dụng:

```python
with UnitOfWork(conn) as uow:
    uow.novels.add(...)

    uow.chapters.add(...)
```

Khi thoát block:

```text
success
   ↓
COMMIT
```

hoặc:

```text
exception
   ↓
ROLLBACK
```

---

# 26. Retry có nên dùng không?

Có thể.

Ví dụ:

```python
import time
import sqlite3


def write_with_retry(conn, operation, retries=3):

    for attempt in range(retries):
        try:
            operation(conn)
            conn.commit()
            return

        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower():
                raise

            if attempt == retries - 1:
                raise

            time.sleep(0.1 * (attempt + 1))
```

Nhưng:

> Retry không phải thuốc chữa cho transaction architecture tồi.

Nếu transaction của bạn giữ lock 30 giây:

```text
retry
retry
retry
```

không giải quyết được vấn đề gốc.

---

# 27. Exponential backoff

Thay vì:

```text
0.1
0.1
0.1
0.1
```

có thể:

```text
0.1
0.2
0.4
0.8
...
```

Ví dụ:

```python
delay = 0.1

for attempt in range(5):
    try:
        ...
        break

    except sqlite3.OperationalError:
        time.sleep(delay)
        delay *= 2
```

Trong production nên kết hợp:

```text
retry limit
+
backoff
+
jitter
```

Nhưng trước hết phải thiết kế transaction đúng.

---

# 28. Một anti-pattern rất nguy hiểm

```python
with uow:
    for chapter in chapters:
        crawl_from_web(chapter.url)

        uow.chapters.add(chapter)
```

Sai ở chỗ:

```text
transaction
  │
  ├── HTTP
  ├── HTTP
  ├── HTTP
  ├── HTTP
  └── COMMIT
```

Transaction có thể kéo dài hàng chục giây.

---

# 29. Tốt hơn

```python
chapters = []

for url in urls:
    html = download(url)

    chapter = parse(html)

    chapters.append(chapter)


with UnitOfWork(conn) as uow:
    for chapter in chapters:
        uow.chapters.add(chapter)
```

Mô hình:

```text
HTTP
 ↓
Parse
 ↓
Prepare
 ↓
BEGIN
 ↓
Batch writes
 ↓
COMMIT
```

---

# 30. Nhưng batch quá lớn cũng không tốt

Không nên:

```text
1.000.000 chapters
       ↓
ONE TRANSACTION
```

Có thể chia:

```text
batch 1 → 500
batch 2 → 500
batch 3 → 500
...
```

Ví dụ:

```text
100–1000 rows / transaction
```

**không phải con số cố định**; phải benchmark theo workload thực tế.

---

# 31. SQLite concurrency trong app Novel

Giả sử:

```text
PySide6 GUI
      │
      ├── Read novels
      ├── Read chapters
      └── Show crawler status

Crawler
      │
      ├── Worker 1
      ├── Worker 2
      └── Worker 3
```

Tôi sẽ thiết kế:

```text
                PySide6
                   │
              Read Connection
                   │
                   ▼
              SQLite WAL
                   ▲
                   │
              Write Queue
                   ▲
                   │
             DB Writer
                   ▲
                   │
        ┌──────────┼──────────┐
        │          │          │
     Worker 1   Worker 2   Worker 3
```

Đây là architecture rất phù hợp cho project crawler của bạn.

---

# 32. Connection Manager + Worker

Ví dụ:

```python
class ConnectionManager:
    def __init__(self, db_path):
        self._db_path = db_path

    def connect(self):
        conn = sqlite3.connect(
            self._db_path,
            timeout=5.0,
        )

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("PRAGMA journal_mode = WAL")

        conn.execute("PRAGMA busy_timeout = 5000")

        return conn
```

Worker:

```python
def worker(manager, job):

    conn = manager.connect()

    try:
        result = crawl(job)

        with UnitOfWork(conn) as uow:
            uow.chapters.add(result)

    finally:
        conn.close()
```

Điểm quan trọng:

```text
worker
 ↓
own connection
 ↓
short transaction
 ↓
close
```

---

# 33. Ba tầng bảo vệ concurrency

Một SQLite application tốt thường có:

```text
1. WAL
       ↓
2. Short transactions
       ↓
3. busy_timeout / retry
```

Không nên chỉ dựa vào:

```text
retry
```

mà bỏ qua hai tầng đầu.

---

# 34. Thứ tự ưu tiên

Nếu gặp:

```text
database is locked
```

hãy kiểm tra theo thứ tự:

### ① Transaction có quá dài không?

```text
BEGIN
   ↓
HTTP?
sleep?
CPU?
   ↓
COMMIT
```

Nếu có → sửa trước.

### ② Có nhiều writer không?

```text
10 workers
   ↓
10 writers
```

Cân nhắc single writer/queue.

### ③ Có bật WAL chưa?

```sql
PRAGMA journal_mode = WAL;
```

### ④ Có busy timeout không?

```sql
PRAGMA busy_timeout = 5000;
```

### ⑤ Có retry hợp lý không?

Sau cùng mới thêm retry/backoff.

---

# 35. Mental Model cực kỳ quan trọng

Hãy ghi nhớ:

```text
SQLite
│
├── Many Readers
│
└── Writer serialization
```

Và:

```text
WAL
│
├── Reader ↔ Writer tốt hơn
│
└── Không biến SQLite thành multi-writer DB
```

Và:

```text
Concurrency tốt
=
WAL
+
short transaction
+
controlled writers
+
busy timeout
+
reasonable retry
```

---

# 36. Tổng kết Buổi 29

Sau hôm nay bạn cần hiểu được:

| Khái niệm            | Ý nghĩa                                           |
| -------------------- | ------------------------------------------------- |
| Reader               | Đọc DB                                            |
| Writer               | Thay đổi DB                                       |
| Lock                 | Cơ chế bảo vệ dữ liệu                             |
| `database is locked` | Không lấy được quyền ghi trong thời gian cho phép |
| `timeout`            | Thời gian connection chờ                          |
| `busy_timeout`       | SQLite chờ khi DB busy                            |
| WAL                  | Cải thiện reader/writer concurrency               |
| Single Writer        | Một luồng/process chuyên ghi DB                   |
| Short Transaction    | Giảm thời gian giữ lock                           |
| Retry                | Thử lại khi contention tạm thời                   |

---

# 37. Bài tập thực hành

### Bài 1 — Hai writer

Tạo:

```text
Connection A
Connection B
```

Cho A:

```text
BEGIN
INSERT
sleep(5)
COMMIT
```

Cho B đồng thời INSERT.

Quan sát hiện tượng.

---

### Bài 2 — WAL

Bật:

```sql
PRAGMA journal_mode = WAL;
```

Sau đó chạy lại bài 1.

So sánh Reader/Writer behavior.

---

### Bài 3 — Timeout

Thử:

```python
sqlite3.connect(
    "novel.db",
    timeout=0.1,
)
```

và:

```python
sqlite3.connect(
    "novel.db",
    timeout=5.0,
)
```

Quan sát sự khác biệt.

---

### Bài 4 — Thread

Tạo:

```text
Thread 1
Thread 2
Thread 3
Thread 4
```

Mỗi thread:

```text
crawl giả lập
    ↓
INSERT chapter
```

Mỗi thread tự tạo connection.

Quan sát lock contention.

---

### Bài 5 — Single Writer

Thiết kế:

```text
Worker 1 ─┐
Worker 2 ─┤
Worker 3 ─┼──► Queue ──► DB Writer ──► SQLite
Worker 4 ─┘
```

Đây là bài cực kỳ đáng làm vì nó kết nối trực tiếp với project crawler của bạn.

---

# 38. Roadmap tiếp theo

Ta đã hoàn thành:

```text
24. SQLite Type Affinity          ✅
25. Constraints Deep Dive         ✅
26. PRAGMA                        ✅
27. Transaction Deep Dive         ✅
28. WAL                           ✅
29. Locking & Concurrency         ✅
```

Tiếp theo:

```text
30. SQLite Performance
```

Ở **Buổi 30**, chúng ta sẽ chuyển từ:

```text
"SQLite có chạy được không?"
```

sang:

```text
"Làm sao để SQLite chạy nhanh?"
```

với:

```text
EXPLAIN QUERY PLAN
INDEX
Covering Index
Composite Index
Query optimization
N+1 Query
Pagination
COUNT
INSERT performance
executemany()
Transaction batching
WAL performance
```

và đặc biệt sẽ áp dụng trực tiếp vào schema:

```text
novels
chapters
tags
novel_tags
```

của **Novel Crawler/Reader**.
