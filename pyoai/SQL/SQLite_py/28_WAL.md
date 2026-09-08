# Buổi 28 — WAL (Write-Ahead Logging) trong SQLite

Ở Buổi 27, ta đã hiểu **Transaction**. Hôm nay đi sâu vào một cơ chế cực kỳ quan trọng phía dưới transaction của SQLite:

> **WAL — Write-Ahead Logging**

Đây là kiến thức rất quan trọng nếu bạn muốn xây app crawler + SQLite chạy ổn định khi có **nhiều reader, worker, thread/process**.

---

# 1. WAL là gì?

WAL = **Write-Ahead Logging**.

Ở chế độ WAL, SQLite không ghi thay đổi trực tiếp vào database chính ngay lập tức.

Thay vào đó:

```text
Application
     │
     ▼
SQLite
     │
     ├── novel.db
     │
     └── novel.db-wal
```

Các thay đổi mới trước tiên được ghi vào:

```text
novel.db-wal
```

Sau đó SQLite sẽ thực hiện **checkpoint** để đưa dữ liệu từ WAL trở lại database chính.

---

# 2. Chế độ mặc định của SQLite

SQLite truyền thống thường sử dụng journal mode:

```text
DELETE
```

Khi transaction thay đổi dữ liệu, SQLite sử dụng rollback journal.

Mô hình đơn giản:

```text
BEGIN
   │
   ▼
database
   │
   ├── backup dữ liệu cũ
   │
   ▼
thay đổi database
   │
   ▼
COMMIT
   │
   ▼
xóa journal
```

WAL thay đổi mô hình này.

---

# 3. WAL hoạt động như thế nào?

Với WAL:

```text
BEGIN
   │
   ▼
ghi thay đổi
   │
   ▼
novel.db-wal
   │
   ▼
COMMIT
```

Database chính:

```text
novel.db
```

chưa nhất thiết được cập nhật ngay.

Ta có:

```text
novel.db
    +
novel.db-wal
    ↓
logical database state
```

SQLite biết phải đọc dữ liệu từ database chính và WAL để tạo ra trạng thái hiện tại.

---

# 4. Vì sao WAL quan trọng?

Điểm lớn nhất:

> **WAL cho phép reader và writer hoạt động đồng thời tốt hơn.**

Ví dụ crawler của chúng ta:

```text
Crawler Worker
      │
      │ WRITE
      ▼
   SQLite
      ▲
      │ READ
      │
Dashboard
```

Một worker đang ghi chapter:

```text
INSERT chapter
```

Trong khi UI dashboard:

```sql
SELECT ...
FROM novels;
```

WAL giúp hai hoạt động này ít cản trở nhau hơn so với rollback journal truyền thống.

---

# 5. So sánh DELETE Journal và WAL

### Journal mode truyền thống

```text
Reader
  │
  ▼
Database

Writer
  │
  ▼
Database

       ↓

Có thể xảy ra blocking
```

### WAL

```text
Reader ───────────────► novel.db
                           +
                         WAL

Writer ───────────────► novel.db-wal
```

Reader có thể tiếp tục đọc snapshot phù hợp trong khi writer ghi WAL.

Đây là lý do WAL đặc biệt hữu ích cho ứng dụng:

```text
nhiều READ
+
ít WRITE nhưng liên tục
```

Ví dụ:

* crawler
* dashboard
* desktop app
* API server nhỏ
* application có background worker

---

# 6. Bật WAL bằng PRAGMA

Rất đơn giản:

```python
import sqlite3

conn = sqlite3.connect("novel.db")

conn.execute("PRAGMA journal_mode = WAL")
```

Kiểm tra:

```python
row = conn.execute("PRAGMA journal_mode").fetchone()

print(row)
```

Thường sẽ nhận:

```text
('wal',)
```

---

# 7. WAL là database-level, không phải transaction-level

Một điểm rất quan trọng.

Ta không làm:

```python
BEGIN

PRAGMA journal_mode = WAL

INSERT ...

COMMIT
```

theo kiểu cấu hình transaction.

Thông thường ta cấu hình WAL trong **Connection Manager**.

Ví dụ:

```python
class ConnectionManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self._db_path)

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("PRAGMA journal_mode = WAL")

        conn.execute("PRAGMA busy_timeout = 5000")

        conn.execute("PRAGMA synchronous = NORMAL")

        return conn
```

Kiến trúc:

```text
ConnectionManager
       │
       ├── foreign_keys
       ├── journal_mode = WAL
       ├── busy_timeout
       └── synchronous
              │
              ▼
          Connection
              │
              ▼
          Repository
```

Đây chính là lý do Buổi 26 học `PRAGMA`.

---

# 8. Khi bật WAL sẽ xuất hiện file gì?

Ví dụ database:

```text
novel.db
```

Khi WAL đang hoạt động, có thể thấy:

```text
novel.db
novel.db-wal
novel.db-shm
```

### `novel.db`

Database chính.

### `novel.db-wal`

Write-Ahead Log.

Chứa các thay đổi chưa được checkpoint vào database chính.

### `novel.db-shm`

Shared-memory file hỗ trợ các connection phối hợp khi sử dụng WAL.

---

# 9. WAL không có nghĩa là database chỉ tồn tại trong `.db-wal`

Đây là hiểu lầm phổ biến.

Không phải:

```text
novel.db = cũ
novel.db-wal = database mới
```

Mà đúng hơn:

```text
novel.db
    +
WAL
    ↓
trạng thái database hiện tại
```

Khi checkpoint hoàn thành, dữ liệu trong WAL được chuyển vào database chính.

---

# 10. Checkpoint là gì?

Checkpoint là quá trình:

```text
novel.db-wal
      │
      │ checkpoint
      ▼
novel.db
```

Nói đơn giản:

> **Checkpoint đưa dữ liệu từ WAL trở lại database chính.**

---

# 11. Có thể thực hiện checkpoint bằng Python

SQLite cung cấp:

```sql
PRAGMA wal_checkpoint;
```

Python:

```python
result = conn.execute("PRAGMA wal_checkpoint").fetchone()

print(result)
```

Có thể chỉ định mode:

```sql
PRAGMA wal_checkpoint(PASSIVE);
```

hoặc:

```sql
PRAGMA wal_checkpoint(FULL);
```

hoặc:

```sql
PRAGMA wal_checkpoint(RESTART);
```

hoặc:

```sql
PRAGMA wal_checkpoint(TRUNCATE);
```

---

# 12. Các checkpoint mode

Có thể hình dung:

```text
PASSIVE
   │
   ▼
cố checkpoint nếu có thể
```

```text
FULL
   │
   ▼
checkpoint nhiều hơn
nhưng có thể chờ reader
```

```text
RESTART
   │
   ▼
checkpoint + cố restart WAL
```

```text
TRUNCATE
   │
   ▼
checkpoint + truncate WAL file
```

Đừng quá lo các mode này ở giai đoạn hiện tại.

Điều quan trọng nhất cần nhớ:

> **Checkpoint ≠ COMMIT.**

---

# 13. COMMIT khác CHECKPOINT

Đây là điểm cực kỳ quan trọng.

### COMMIT

Kết thúc transaction:

```text
BEGIN
  │
 INSERT
 UPDATE
  │
 COMMIT
```

Nó xác nhận transaction đã commit.

### CHECKPOINT

Di chuyển dữ liệu từ:

```text
WAL → database
```

Hai khái niệm khác nhau.

Có thể:

```text
COMMIT
   ↓
data nằm trong WAL
   ↓
sau đó mới CHECKPOINT
   ↓
database chính được cập nhật
```

---

# 14. WAL và nhiều Reader

Giả sử:

```text
Reader A
Reader B
Reader C
```

cùng đọc database.

Trong WAL mode, mỗi reader có thể đọc một **snapshot**.

Ví dụ:

```text
Database version 10

Reader A
    ↓
snapshot version 10

Writer
    ↓
version 11

Reader B
    ↓
snapshot version 11
```

Reader A có thể tiếp tục thấy snapshot mà nó đang đọc trong khi writer tạo dữ liệu mới.

Đây là một trong những ưu điểm lớn của WAL.

---

# 15. Nhưng WAL không biến SQLite thành database server

Đừng hiểu:

> WAL = SQLite không còn lock.

Sai.

WAL vẫn có giới hạn.

Đặc biệt:

> **SQLite vẫn chỉ có một writer tại một thời điểm.**

Ví dụ:

```text
Worker A ── WRITE ──┐
                    │
                    ▼
                  SQLite
                    ▲
                    │
Worker B ── WRITE ──┘
```

Hai writer không thực sự cùng commit song song.

Một writer có thể phải chờ writer khác.

Vì vậy:

```text
WAL ≠ unlimited concurrency
```

---

# 16. WAL rất phù hợp với crawler

Hãy tưởng tượng app của chúng ta:

```text
                ┌── Worker 1
                │
Crawler ────────┼── Worker 2
                │
                └── Worker 3
                        │
                        ▼
                     SQLite
                        ▲
                        │
                    Dashboard
```

Dashboard liên tục:

```sql
SELECT ...
```

Worker liên tục:

```sql
INSERT INTO chapters ...
```

WAL rất phù hợp với mô hình:

```text
many readers
+
single/multiple competing writers
```

vì nó cải thiện khả năng reader tiếp tục hoạt động trong lúc writer ghi.

---

# 17. Nhưng transaction vẫn phải ngắn

WAL không sửa được thiết kế transaction tồi.

Ví dụ **không nên**:

```python
with uow:
    crawl_chapter_from_internet()

    crawl_another_chapter()

    time.sleep(5)

    save_to_database()
```

Nếu transaction mở quá lâu:

```text
BEGIN
  │
  ├── HTTP
  ├── HTTP
  ├── sleep
  ├── parsing
  └── database write
       │
       ▼
     COMMIT
```

Đây là thiết kế không tốt.

---

# 18. Thiết kế tốt

Crawler:

```text
HTTP
 │
 ▼
Download
 │
 ▼
Parse
 │
 ▼
Validate
 │
 ▼
Prepare data
 │
 ▼
BEGIN
 │
 ├── INSERT
 ├── UPDATE
 └── INSERT
 │
 ▼
COMMIT
```

Transaction chỉ bao quanh phần database.

Ví dụ:

```python
chapter = crawl_chapter(url)

data = parse_chapter(chapter)

with UnitOfWork(conn) as uow:
    uow.chapters.add(data)
```

Tốt hơn rất nhiều.

---

# 19. WAL + Unit of Work

Kiến trúc của chúng ta lúc này trở thành:

```text
             Application
                  │
                  ▼
            Unit of Work
                  │
          transaction boundary
                  │
                  ▼
             Repository
                  │
                  ▼
             Connection
                  │
        ┌─────────┴─────────┐
        │                   │
   PRAGMA WAL          PRAGMA FK
        │                   │
        └─────────┬─────────┘
                  ▼
               SQLite
```

Đây là kiến trúc rất đáng nhớ.

---

# 20. Connection Manager hoàn chỉnh hơn

Ví dụ:

```python
import sqlite3


class ConnectionManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self._db_path,
            timeout=5.0,
        )

        conn.row_factory = sqlite3.Row

        self._configure(conn)

        return conn

    def _configure(
        self,
        conn: sqlite3.Connection,
    ) -> None:

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("PRAGMA journal_mode = WAL")

        conn.execute("PRAGMA busy_timeout = 5000")

        conn.execute("PRAGMA synchronous = NORMAL")
```

Như vậy repository không cần biết:

```sql
PRAGMA journal_mode = WAL
```

Repository chỉ quan tâm:

```python
conn.execute(...)
```

---

# 21. Một điểm rất quan trọng: mỗi connection có cấu hình riêng

Đặc biệt:

```sql
PRAGMA foreign_keys = ON
```

là **per connection**.

Vì vậy:

```python
conn1 = manager.connect()
conn2 = manager.connect()
conn3 = manager.connect()
```

Connection Manager phải đảm bảo mỗi connection được cấu hình đúng.

Đây là lý do không nên rải:

```python
conn.execute("PRAGMA ...")
```

lung tung trong application.

---

# 22. Test WAL

Tạo database:

```python
import sqlite3

conn = sqlite3.connect("test.db")

conn.execute("PRAGMA journal_mode = WAL")

mode = conn.execute("PRAGMA journal_mode").fetchone()[0]

print(mode)

conn.close()
```

Kết quả:

```text
wal
```

---

# 23. Kiểm tra file WAL

Sau khi thực hiện ghi:

```python
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
    """
)

conn.execute("INSERT INTO novels(title) VALUES (?)", ("Tiên Nghịch",))

conn.commit()
```

Trong lúc WAL đang tồn tại, filesystem có thể xuất hiện:

```text
test.db
test.db-wal
test.db-shm
```

Kích thước WAL thay đổi theo hoạt động ghi/checkpoint.

Không nên tự ý xóa:

```text
test.db-wal
test.db-shm
```

trong khi database đang được sử dụng.

Hãy để SQLite quản lý chúng.

---

# 24. WAL không phải backup

Một hiểu lầm khác:

> "`novel.db-wal` là backup database."

Không.

WAL là một thành phần của cơ chế journaling/recovery và concurrency.

Không nên coi:

```text
novel.db-wal
```

là file backup độc lập.

Backup database nên sử dụng cơ chế backup phù hợp của SQLite, nội dung này sẽ nằm ở phần production sau.

---

# 25. WAL + `synchronous`

Ở Buổi 26 ta đã gặp:

```sql
PRAGMA synchronous = NORMAL;
```

Một cấu hình thường thấy:

```python
conn.execute("PRAGMA journal_mode = WAL")

conn.execute("PRAGMA synchronous = NORMAL")
```

Ý tưởng:

```text
WAL
 +
synchronous
 ↓
trade-off giữa
performance ↔ durability
```

Không nên hiểu:

```text
NORMAL = unsafe
FULL = always necessary
```

Mà cần hiểu đây là **durability/performance trade-off**.

---

# 26. Một kiến trúc crawler thực tế

Ví dụ:

```text
                    ┌──────────────┐
                    │   PySide6    │
                    │  Dashboard   │
                    └──────┬───────┘
                           │
                         READ
                           │
                           ▼
                    ┌──────────────┐
                    │   SQLite     │
                    │     WAL      │
                    └──────┬───────┘
                           ▲
                           │ WRITE
                    ┌──────┴───────┐
                    │    Worker    │
                    └──────┬───────┘
                           │
                        HTTP crawl
```

Database:

```text
novel.db
novel.db-wal
novel.db-shm
```

Application:

```text
ConnectionManager
       ↓
UnitOfWork
       ↓
Repository
       ↓
SQLite
```

Đây chính là nền tảng để sang bài tiếp theo học **Locking & Concurrency**.

---

# 27. Những điều cần nhớ sau Buổi 28

### ① WAL là gì?

```text
Write-Ahead Logging
```

### ② WAL ghi thay đổi ở đâu?

```text
novel.db-wal
```

### ③ WAL có lợi ích gì?

Đặc biệt cải thiện khả năng:

```text
Reader ↔ Writer
```

hoạt động đồng thời.

### ④ WAL có cho phép nhiều writer đồng thời không?

**Không.**

SQLite vẫn có giới hạn về writer concurrency.

### ⑤ Checkpoint là gì?

```text
WAL → database chính
```

### ⑥ COMMIT có giống CHECKPOINT không?

**Không.**

```text
COMMIT    = kết thúc transaction
CHECKPOINT = chuyển dữ liệu WAL → database
```

### ⑦ WAL có phải backup không?

**Không.**

### ⑧ WAL nên cấu hình ở đâu?

```text
ConnectionManager
```

không phải Repository.

---

# 28. Bài tập thực hành

## Bài 1 — Bật WAL

Viết:

```python
class ConnectionManager: ...
```

với:

```text
foreign_keys = ON
journal_mode = WAL
busy_timeout = 5000
synchronous = NORMAL
```

---

## Bài 2 — Kiểm tra mode

Viết:

```python
def get_journal_mode(conn): ...
```

Kết quả mong muốn:

```text
wal
```

---

## Bài 3 — WAL + transaction

Viết chương trình:

```text
BEGIN
   ↓
INSERT novel
   ↓
INSERT chapter
   ↓
COMMIT
```

Sau đó kiểm tra database.

---

## Bài 4 — Rollback

Tạo transaction:

```text
BEGIN
   ↓
INSERT novel
   ↓
INSERT chapter hợp lệ
   ↓
INSERT chapter sai FK
   ↓
ROLLBACK
```

Kiểm tra:

```sql
SELECT * FROM novels;
SELECT * FROM chapters;
```

Kỳ vọng:

```text
Không có dữ liệu transaction đó.
```

---

## Bài 5 — Checkpoint

Thử:

```python
conn.execute("PRAGMA wal_checkpoint(FULL)")
```

Sau đó quan sát:

```text
test.db
test.db-wal
test.db-shm
```

và ghi nhận sự thay đổi kích thước file.

---

# 29. Câu hỏi tư duy

Hãy tự trả lời 5 câu này trước khi sang Buổi 29:

**1.** Vì sao WAL giúp Reader ít bị Writer chặn hơn?

**2.** WAL có cho phép 10 Worker cùng `INSERT` vào SQLite tại chính xác cùng một thời điểm không?

**3.** `COMMIT` và `CHECKPOINT` khác nhau thế nào?

**4.** Tại sao `PRAGMA journal_mode = WAL` nên nằm trong `ConnectionManager`?

**5.** Vì sao đoạn code này là thiết kế tồi?

```text
BEGIN
 ↓
HTTP request
 ↓
parse HTML
 ↓
sleep
 ↓
INSERT
 ↓
COMMIT
```

Nếu trả lời được 5 câu trên, bạn đã nắm được phần cốt lõi của **WAL**.

---

## Roadmap hiện tại

```text
PART IV — SQLite Deep Dive

24. Type Affinity              ✅
25. Constraints Deep Dive      ✅
26. PRAGMA                     ✅
27. Transaction Deep Dive      ✅
28. WAL                        ✅  ← hôm nay
29. Locking & Concurrency      ⬅ tiếp theo
30. SQLite Performance
```

**Buổi 29** sẽ nối trực tiếp từ WAL sang vấn đề thực tế hơn:

```text
Thread
Process
     │
     ▼
SQLite
     │
     ├── database is locked
     ├── database is busy
     ├── timeout
     ├── writer contention
     └── concurrency
```

và chúng ta sẽ mô phỏng **nhiều crawler worker cùng ghi SQLite bằng Python**.
