# Phần IV — SQLite Deep Dive

# Buổi 26 — PRAGMA

Hôm nay chúng ta học một đặc điểm rất riêng của SQLite:

> **`PRAGMA` là cơ chế để cấu hình và introspection SQLite.**

Nếu `CREATE TABLE` giúp ta **định nghĩa schema**, thì `PRAGMA` giúp ta **điều khiển và kiểm tra behavior của SQLite**.

Đặc biệt với app crawler của bạn, `PRAGMA` sẽ trở thành một phần của **Connection Manager**.

---

# 1. PRAGMA là gì?

Cú pháp cơ bản:

```sql
PRAGMA pragma_name;
```

hoặc:

```sql
PRAGMA pragma_name = value;
```

Ví dụ:

```sql
PRAGMA foreign_keys = ON;
```

Có thể hiểu:

```text
Python
   ↓
SQLite Connection
   ↓
PRAGMA
   ↓
SQLite configuration / information
```

Một số PRAGMA dùng để:

```text
configuration
inspection
diagnostics
performance tuning
database metadata
```

---

# 2. PRAGMA khác SELECT như thế nào?

Ví dụ:

```sql
SELECT *
FROM novels;
```

đang truy vấn **data của application**.

Trong khi:

```sql
PRAGMA foreign_keys;
```

đang hỏi SQLite:

> "Connection này hiện có bật foreign key enforcement không?"

Tức là:

```text
SELECT
    ↓
Application data

PRAGMA
    ↓
SQLite behavior / metadata
```

---

# 3. PRAGMA quan trọng nhất: `foreign_keys`

Chúng ta đã gặp:

```sql
PRAGMA foreign_keys = ON;
```

SQLite có foreign key nhưng enforcement cần được bật cho connection.

Python:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

Kiểm tra:

```python
row = conn.execute("PRAGMA foreign_keys").fetchone()

print(row[0])
```

Nếu:

```text
1
```

thì:

```text
FOREIGN KEY enforcement = ON
```

---

# 4. PRAGMA là thuộc tính của Connection

Đây là điểm cực kỳ quan trọng.

Bạn có:

```python
conn1 = sqlite3.connect("novel.db")
conn2 = sqlite3.connect("novel.db")
```

Bật:

```python
conn1.execute("PRAGMA foreign_keys = ON")
```

không có nghĩa:

```text
conn2 → automatically ON
```

Vì vậy Connection Manager phải cấu hình **mỗi connection**.

```python
class ConnectionManager:
    def connect(self):
        conn = sqlite3.connect("novel.db")

        conn.execute("PRAGMA foreign_keys = ON")

        return conn
```

Đây là lý do `ConnectionManager` không chỉ đơn giản là:

```python
sqlite3.connect(...)
```

---

# 5. `journal_mode`

SQLite cần cơ chế journal để đảm bảo transaction an toàn.

Kiểm tra:

```sql
PRAGMA journal_mode;
```

SQLite có nhiều journal mode.

Một số mode đáng biết:

```text
DELETE
TRUNCATE
PERSIST
MEMORY
WAL
OFF
```

Trong ứng dụng thực tế, mode chúng ta đặc biệt quan tâm là:

```text
WAL
```

---

# 6. WAL là gì?

WAL:

> **Write-Ahead Logging**

Thay vì ngay lập tức sửa database chính:

```text
novel.db
```

SQLite có thể ghi thay đổi vào:

```text
novel.db-wal
```

sau đó checkpoint về database chính.

Mô hình:

```text
Application
     ↓
   SQLite
     ↓
 novel.db-wal
     ↓
 checkpoint
     ↓
 novel.db
```

WAL sẽ được học riêng ở:

```text
Buổi 28 — WAL
```

Hôm nay chỉ cần biết:

```sql
PRAGMA journal_mode = WAL;
```

---

# 7. Kiểm tra journal mode

Python:

```python
row = conn.execute("PRAGMA journal_mode").fetchone()

print(row[0])
```

Ví dụ:

```text
wal
```

SQLite thường trả kết quả dưới dạng lowercase tùy cách hiển thị, nên khi kiểm tra trong code có thể chuẩn hóa:

```python
mode = row[0].lower()

if mode != "wal":
    ...
```

---

# 8. `synchronous`

Đây là PRAGMA liên quan đến:

> **Mức độ SQLite đảm bảo dữ liệu đã được flush/sync xuống storage.**

Các mode phổ biến:

```text
OFF
NORMAL
FULL
EXTRA
```

Ví dụ:

```sql
PRAGMA synchronous = NORMAL;
```

hoặc:

```sql
PRAGMA synchronous = FULL;
```

---

# 9. `synchronous = FULL`

Tư duy đơn giản:

```text
FULL
 ↓
ưu tiên durability
 ↓
nhiều sync hơn
 ↓
có thể chậm hơn
```

Đây là lựa chọn thiên về an toàn dữ liệu.

---

# 10. `synchronous = NORMAL`

```text
NORMAL
 ↓
cân bằng
 ↓
performance + durability
```

Một cấu hình SQLite + WAL thường gặp:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

Nhưng **không nên học thuộc như công thức bắt buộc**.

Việc chọn `synchronous` phải dựa vào durability requirement của ứng dụng.

---

# 11. `busy_timeout`

Đây là PRAGMA cực kỳ hữu ích khi có concurrency.

Giả sử:

```text
Worker A
   ↓
đang ghi SQLite

Worker B
   ↓
muốn ghi SQLite
```

Worker B có thể gặp:

```text
database is locked
```

Ta có thể cấu hình:

```sql
PRAGMA busy_timeout = 5000;
```

nghĩa là SQLite có thể chờ khoảng:

```text
5000 ms = 5 giây
```

trước khi báo lỗi busy/locked.

Python:

```python
conn.execute("PRAGMA busy_timeout = 5000")
```

---

# 12. `busy_timeout` không giải quyết mọi concurrency problem

Đừng hiểu:

```text
busy_timeout
    ↓
SQLite hết lỗi locking
```

Không phải.

Nó chỉ:

```text
database locked
      ↓
chờ một khoảng thời gian
      ↓
hy vọng lock được giải phóng
```

Nếu transaction giữ lock quá lâu:

```text
Worker A
    ↓
long transaction
    ↓
Worker B
    ↓
wait
    ↓
timeout
    ↓
OperationalError
```

Buổi 29 chúng ta sẽ đào sâu phần này.

---

# 13. `cache_size`

SQLite có page cache.

Có thể xem:

```sql
PRAGMA cache_size;
```

Nó liên quan đến lượng page SQLite giữ trong memory.

Có thể cấu hình:

```sql
PRAGMA cache_size = -64000;
```

Giá trị âm có ý nghĩa theo KB.

Ví dụ:

```text
-64000
   ↓
khoảng 64 MB cache
```

Nhưng đây là tuning nâng cao.

**Không nên tùy tiện tăng cache chỉ vì nghĩ "RAM càng nhiều càng nhanh".**

Buổi 30 sẽ nói về performance và query plan.

---

# 14. `user_version`

Đây là một PRAGMA cực kỳ hữu ích cho **database migration**.

SQLite có:

```sql
PRAGMA user_version;
```

Ban đầu thường:

```text
0
```

Bạn có thể đặt:

```sql
PRAGMA user_version = 1;
```

Sau migration:

```sql
PRAGMA user_version = 2;
```

Mô hình:

```text
Database
   ↓
user_version = 1
   ↓
Migration
   ↓
user_version = 2
```

---

# 15. Tại sao `user_version` quan trọng?

Giả sử app version 1 có:

```sql
novels(
    id,
    title
)
```

Version 2 thêm:

```text
author
```

Version 3 thêm:

```text
status
```

Ta có:

```text
DB v1
 ↓
migration 1 → 2
 ↓
migration 2 → 3
```

Python có thể kiểm tra:

```python
version = conn.execute("PRAGMA user_version").fetchone()[0]

print(version)
```

Sau này ta sẽ xây:

```text
MigrationManager
```

ở phần production SQLite.

---

# 16. `application_id`

SQLite còn có:

```sql
PRAGMA application_id;
```

Nó cho phép ứng dụng đặt một identifier cho database file.

Ý tưởng:

```text
novel.db
   ↓
application_id
   ↓
"database này thuộc Novel Crawler"
```

Điều này hữu ích khi cần nhận diện loại SQLite database.

Không phải PRAGMA bạn cần dùng ngay, nhưng nên biết.

---

# 17. `integrity_check`

Đây là một PRAGMA rất đáng nhớ.

```sql
PRAGMA integrity_check;
```

SQLite kiểm tra integrity của database.

Ví dụ Python:

```python
result = conn.execute("PRAGMA integrity_check").fetchone()

print(result[0])
```

Database bình thường thường trả:

```text
ok
```

---

# 18. `quick_check`

Có:

```sql
PRAGMA quick_check;
```

Tương tự `integrity_check` nhưng nhanh hơn và kiểm tra ít toàn diện hơn.

Có thể hình dung:

```text
quick_check
    ↓
kiểm tra nhanh

integrity_check
    ↓
kiểm tra sâu hơn
```

Đây rất hữu ích cho:

```text
diagnostics
backup verification
maintenance
testing
```

---

# 19. PRAGMA để xem schema

SQLite có các PRAGMA introspection.

Ví dụ:

```sql
PRAGMA table_info(novels);
```

Nó cho biết thông tin column:

```text
cid
name
type
notnull
dflt_value
pk
```

Python:

```python
rows = conn.execute("PRAGMA table_info(novels)").fetchall()

for row in rows:
    print(dict(row))
```

Nếu sử dụng:

```python
conn.row_factory = sqlite3.Row
```

thì rất tiện.

---

# 20. Xem Foreign Key

```sql
PRAGMA foreign_key_list(chapters);
```

Ví dụ:

```python
rows = conn.execute("PRAGMA foreign_key_list(chapters)").fetchall()

for row in rows:
    print(dict(row))
```

Bạn có thể kiểm tra:

```text
chapters.novel_id
       ↓
novels.id
```

---

# 21. Xem index

```sql
PRAGMA index_list(chapters);
```

Ví dụ:

```python
rows = conn.execute("PRAGMA index_list(chapters)").fetchall()
```

Sau đó:

```sql
PRAGMA index_info(index_name);
```

Các PRAGMA này sẽ rất hữu ích khi học:

```text
Buổi 30 — SQLite Performance
```

---

# 22. Xây Connection Manager

Bây giờ ta ghép những gì đã học.

```python
import sqlite3


class ConnectionManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)

        conn.row_factory = sqlite3.Row

        self._configure(conn)

        return conn

    def _configure(
        self,
        conn: sqlite3.Connection,
    ) -> None:

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("PRAGMA busy_timeout = 5000")
```

Đây đã tốt hơn rất nhiều so với:

```python
sqlite3.connect("novel.db")
```

---

# 23. Thêm WAL

Có thể cấu hình:

```python
def _configure(
    self,
    conn: sqlite3.Connection,
) -> None:

    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("PRAGMA journal_mode = WAL")

    conn.execute("PRAGMA synchronous = NORMAL")

    conn.execute("PRAGMA busy_timeout = 5000")
```

Nhưng có một điểm cần nhớ:

> Không phải PRAGMA nào cũng có cùng scope và behavior.

Một số là **connection-level**, một số liên quan đến **database file**, một số thay đổi persistent database configuration.

Đây là lý do không nên copy một danh sách PRAGMA vào code mà không hiểu chúng.

---

# 24. Connection Manager hoàn chỉnh hơn

Ta có thể viết:

```python
import sqlite3


class ConnectionManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)

        conn.row_factory = sqlite3.Row

        self._configure(conn)

        return conn

    def _configure(
        self,
        conn: sqlite3.Connection,
    ) -> None:

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("PRAGMA busy_timeout = 5000")

        conn.execute("PRAGMA journal_mode = WAL")

        conn.execute("PRAGMA synchronous = NORMAL")
```

Sau này Unit of Work sẽ dùng:

```text
UnitOfWork
     ↓
ConnectionManager
     ↓
Connection
```

---

# 25. Kiểm tra configuration

Không nên chỉ:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

mà nên biết cách verify:

```python
def get_foreign_keys_status(
    conn: sqlite3.Connection,
) -> bool:

    row = conn.execute("PRAGMA foreign_keys").fetchone()

    return bool(row[0])
```

---

# 26. Tạo SQLite configuration object

Khi project lớn hơn, ta có thể tách config:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SQLiteConfig:
    db_path: str
    busy_timeout_ms: int = 5000
    enable_wal: bool = True
```

Connection Manager:

```python
class ConnectionManager:
    def __init__(
        self,
        config: SQLiteConfig,
    ):
        self._config = config

    def connect(self) -> sqlite3.Connection:

        conn = sqlite3.connect(self._config.db_path)

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute(f"PRAGMA busy_timeout = {self._config.busy_timeout_ms}")

        if self._config.enable_wal:
            conn.execute("PRAGMA journal_mode = WAL")

        return conn
```

**Lưu ý:** trong code production, với giá trị cấu hình từ bên ngoài, nên tránh ghép chuỗi SQL tùy tiện. Ở đây `busy_timeout_ms` là số nguyên do application kiểm soát; tốt hơn nữa là validate kiểu và phạm vi trước khi đưa vào PRAGMA.

---

# 27. Một nguyên tắc architecture quan trọng

Application code không nên rải:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

ở khắp nơi.

❌ Không tốt:

```text
Repository A
   ↓ PRAGMA

Repository B
   ↓ PRAGMA

Repository C
   ↓ PRAGMA
```

Tốt hơn:

```text
             ConnectionManager
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
       Repo A    Repo B    Repo C
          │         │         │
          └─────────┼─────────┘
                    ↓
                SQLite
```

**Connection configuration thuộc infrastructure layer.**

---

# 28. PRAGMA nào cần nhớ ở thời điểm này?

Không cần học thuộc hàng chục PRAGMA.

Tập trung vào:

```text
PRAGMA foreign_keys
        ↓
Referential integrity

PRAGMA journal_mode
        ↓
Journal / WAL

PRAGMA synchronous
        ↓
Durability / performance

PRAGMA busy_timeout
        ↓
Lock waiting

PRAGMA user_version
        ↓
Migration version

PRAGMA integrity_check
        ↓
Database integrity
```

Và introspection:

```text
PRAGMA table_info(...)
PRAGMA foreign_key_list(...)
PRAGMA index_list(...)
PRAGMA index_info(...)
```

---

# 29. Thực hành

Tạo file:

```text
pragma_demo.py
```

Code:

```python
import sqlite3


conn = sqlite3.connect(":memory:")

conn.row_factory = sqlite3.Row

conn.execute("PRAGMA foreign_keys = ON")

conn.execute("PRAGMA busy_timeout = 5000")

print("foreign_keys:", conn.execute("PRAGMA foreign_keys").fetchone()[0])

print("busy_timeout:", conn.execute("PRAGMA busy_timeout").fetchone()[0])

print("user_version:", conn.execute("PRAGMA user_version").fetchone()[0])

print("integrity:", conn.execute("PRAGMA integrity_check").fetchone()[0])

conn.close()
```

Bạn nên quan sát kết quả.

---

# 30. Bài tập 1 — Foreign Key

Tạo:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    title TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Sau đó:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

Thử insert:

```text
novel_id = 1
```

khi Novel 1 chưa tồn tại.

Quan sát exception.

---

# 31. Bài tập 2 — Introspection

Chạy:

```sql
PRAGMA table_info(novels);
```

và:

```sql
PRAGMA foreign_key_list(chapters);
```

Mục tiêu:

> Không chỉ biết viết schema, mà biết **đọc schema từ SQLite**.

Đây là kỹ năng rất hữu ích cho migration tool và database tooling.

---

# 32. Bài tập 3 — Database version

Chạy:

```python
conn.execute("PRAGMA user_version = 1")

version = conn.execute("PRAGMA user_version").fetchone()[0]

print(version)
```

Sau đó:

```python
conn.execute("PRAGMA user_version = 2")
```

và kiểm tra lại.

Hãy tự trả lời:

> Nếu database đang ở version 1 nhưng application yêu cầu version 3 thì application nên làm gì?

Gợi ý:

```text
version 1
   ↓
migration 1 → 2
   ↓
migration 2 → 3
```

---

# 33. Bài tập 4 — Thiết kế Connection Manager

Viết:

```python
class ConnectionManager: ...
```

với yêu cầu:

```text
connect()
    ↓
sqlite3.Connection
    ↓
row_factory = sqlite3.Row
    ↓
foreign_keys = ON
    ↓
busy_timeout = 5000
    ↓
WAL
```

Sau đó viết:

```python
def check_connection(conn): ...
```

kiểm tra:

```text
foreign_keys
journal_mode
busy_timeout
integrity_check
```

---

# 34. Mental Model của Buổi 26

Hãy nhớ:

```text
SQLite Connection
       │
       ├── PRAGMA foreign_keys
       │       ↓
       │   Relationship integrity
       │
       ├── PRAGMA journal_mode
       │       ↓
       │   Journal / WAL
       │
       ├── PRAGMA synchronous
       │       ↓
       │   Durability
       │
       ├── PRAGMA busy_timeout
       │       ↓
       │   Lock waiting
       │
       ├── PRAGMA user_version
       │       ↓
       │   Migration
       │
       └── PRAGMA integrity_check
               ↓
           Health check
```

Và kiến trúc:

```text
Application
     ↓
Unit of Work
     ↓
Repository
     ↓
ConnectionManager
     ↓
Configured SQLite Connection
     ↓
SQLite
```

---

# Roadmap

```text
Phần IV — SQLite Deep Dive

24. SQLite Type Affinity       ✅
25. Constraints Deep Dive      ✅
26. PRAGMA                    ✅

27. Transaction Deep Dive
    ├── BEGIN
    ├── COMMIT
    ├── ROLLBACK
    ├── SAVEPOINT
    ├── isolation
    ├── atomicity
    └── Python transaction management

28. WAL
29. Locking & Concurrency
30. SQLite Performance
```

**Buổi 27 — Transaction Deep Dive** sẽ là bước rất quan trọng: ta sẽ đi từ `commit()/rollback()` đơn giản sang hiểu thực sự **atomicity, transaction boundary, `BEGIN`, `SAVEPOINT`, nested transaction và tại sao Unit of Work phải sở hữu transaction boundary**.
