# Buổi 4 — SQLite Connection Manager Deep Dive

Hôm nay ta tập trung hoàn toàn vào **Connection Manager** cho app crawl truyện.

Mục tiêu cuối buổi:

```text
Application
    ↓
UnitOfWork
    ↓
SQLiteConnectionManager
    ↓
sqlite3.Connection
    ↓
SQLite
```

Ta sẽ hiểu **connection lifecycle, PRAGMA, WAL, foreign keys, busy timeout, isolation level, thread safety**, và cuối cùng xây một `SQLiteConnectionManager` production-style.

---

# 1. Connection Manager thực sự chịu trách nhiệm gì?

Ở Buổi 1 ta có:

```python
class SQLiteConnectionManager:

    def __init__(self, db_path):
        self.db_path = Path(db_path)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
```

Đây mới chỉ là phiên bản tối thiểu.

Trong app crawler thực tế, Connection Manager nên chịu trách nhiệm:

```text
SQLiteConnectionManager
│
├── database path
├── tạo connection
├── row_factory
├── foreign_keys
├── WAL
├── busy_timeout
├── isolation_level
└── các SQLite configuration
```

Nhưng **không chịu trách nhiệm**:

```text
❌ Repository
❌ Business logic
❌ commit transaction của Use Case
❌ SQL nghiệp vụ
```

---

# 2. Connection lifecycle

Một connection có lifecycle:

```text
create
  ↓
configure
  ↓
use
  ↓
commit / rollback
  ↓
close
```

Trong kiến trúc của chúng ta:

```text
UnitOfWork
    │
    ├── connect()
    │
    ├── Repository sử dụng connection
    │
    ├── commit()
    │    hoặc
    │    rollback()
    │
    └── close()
```

Điều này rất quan trọng:

> **UoW sở hữu lifecycle của connection.**

Connection Manager chỉ **cung cấp connection**.

---

# 3. Không nên tạo global connection

Một thiết kế rất dễ gặp:

```python
conn = sqlite3.connect("novels.db")
```

rồi toàn app dùng:

```text
global conn
```

Ví dụ:

```python
class NovelRepository:

    def __init__(self):
        self.conn = global_conn
```

Không nên.

Vì:

```text
Thread A
   ↓
global connection

Thread B
   ↓
global connection

Crawler worker
   ↓
global connection
```

sẽ nhanh chóng tạo ra vấn đề về:

- concurrency
- transaction boundary
- connection ownership
- lifecycle

---

# 4. Connection per Unit of Work

Thiết kế của chúng ta:

```text
Use Case
   │
   ▼
 UoW
   │
   ▼
connect()
   │
   ▼
Connection
   │
   ├── NovelRepository
   ├── ChapterRepository
   └── CrawlStateRepository
```

Sau khi xong:

```text
commit / rollback
        ↓
      close
```

Do đó:

> **Một UoW thường sở hữu một SQLite connection.**

Đây là mô hình rất phù hợp với app crawler hiện tại.

---

# 5. `row_factory`

Ta đã dùng:

```python
conn.row_factory = sqlite3.Row
```

Nếu không:

```python
row = conn.execute(
    "SELECT id, title FROM novels"
).fetchone()
```

kết quả kiểu:

```python
(1, "Đấu Phá Thương Khung")
```

Truy cập:

```python
row[0]
row[1]
```

Với:

```python
conn.row_factory = sqlite3.Row
```

ta có:

```python
row["id"]
row["title"]
```

Đây là lựa chọn rất tốt cho repository.

---

# 6. `PRAGMA foreign_keys`

SQLite có một điểm rất dễ gây nhầm:

**Foreign key enforcement không tự động luôn bật theo cách nhiều người kỳ vọng.**

Ta nên bật explicit:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

Ví dụ:

```text
novels
   │
   │ 1
   │
   └─────── *
          chapters
```

Chapter:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nếu foreign key enforcement được bật:

```text
DELETE novel
   ↓
SQLite kiểm tra chapters
   ↓
constraint
```

Connection Manager nên cấu hình:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

---

# 7. WAL Mode

Đây là phần rất đáng chú ý với crawler.

SQLite mặc định có journal mode truyền thống.

Ta có thể sử dụng:

```sql
PRAGMA journal_mode = WAL;
```

WAL = **Write-Ahead Logging**.

Mô hình:

```text
Reader
  │
  ├──────────────► Database

Writer
  │
  └──────────────► WAL
```

WAL thường cải thiện concurrency giữa reader và writer.

Đặc biệt app crawler của bạn có thể có:

```text
Crawler Worker
     │
     └── WRITE

Dashboard
     │
     └── READ

Reading Page
     │
     └── READ
```

Đây là scenario rất phù hợp để tìm hiểu WAL.

---

# 8. WAL không biến SQLite thành database server

Đừng hiểu:

```text
WAL
 ↓
SQLite concurrency = PostgreSQL
```

Không phải.

SQLite vẫn có giới hạn concurrency.

Đặc biệt:

```text
many writers
```

không phải workload SQLite lý tưởng.

Nhưng:

```text
many readers
+
one/few writers
```

lại rất phù hợp.

Crawler app của bạn thường gần với mô hình này.

---

# 9. `busy_timeout`

Giả sử:

```text
Worker A
    ↓
WRITE

Worker B
    ↓
WRITE
```

SQLite có thể gặp:

```text
database is locked
```

Ta có thể cấu hình:

```python
conn.execute(
    "PRAGMA busy_timeout = 5000"
)
```

Nghĩa là SQLite chờ khoảng:

```text
5000 ms
```

thay vì lập tức báo lỗi khi database đang bị lock.

---

# 10. `timeout` của sqlite3

Ngoài PRAGMA:

```python
sqlite3.connect(
    db_path,
    timeout=5.0,
)
```

cũng có timeout.

Ví dụ:

```python
conn = sqlite3.connect(
    self.db_path,
    timeout=5.0,
)
```

Ta có thể dùng:

```text
timeout
+
busy_timeout
```

nhưng cần hiểu rõ cấu hình của driver và SQLite thay vì thiết lập một cách tùy tiện.

Đối với project hiện tại, ta có thể thống nhất:

```python
timeout=5.0
```

và cấu hình `busy_timeout` explicit để dễ quan sát behavior.

---

# 11. `isolation_level`

Đây là phần khó hơn.

SQLite có transaction semantics riêng và Python `sqlite3` có tham số:

```python
isolation_level
```

Ví dụ:

```python
sqlite3.connect(
    db_path,
    isolation_level=None,
)
```

`None` nghĩa là **autocommit mode**.

Khi đó:

```python
conn.execute(...)
```

có thể được commit ngay theo semantics autocommit.

Điều này **không phù hợp** nếu ta muốn UoW kiểm soát transaction theo kiểu:

```text
BEGIN
   ↓
many operations
   ↓
COMMIT / ROLLBACK
```

---

# 12. UoW cần transaction boundary

Ta muốn:

```text
with uow:

    uow.novels.add()

    uow.chapters.add()

    uow.crawl_states.update()

        ↓

    COMMIT
```

Do đó không nên vô tình biến connection thành:

```text
autocommit everything
```

vì như vậy UoW mất nhiều ý nghĩa.

---

# 13. Explicit transaction

Ta có thể làm transaction rõ ràng:

```python
class SQLiteUnitOfWork:

    def __enter__(self):

        self.conn = self.connection_manager.connect()

        self.conn.execute("BEGIN")

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        return self
```

Sau đó:

```python
def commit(self):
    self.conn.commit()
```

và:

```python
def rollback(self):
    self.conn.rollback()
```

Flow:

```text
__enter__
   ↓
BEGIN
   ↓
operations
   ↓
__exit__
   ├── COMMIT
   └── ROLLBACK
```

Đây là cách rất dễ hiểu khi học transaction.

---

# 14. Có nên `BEGIN` trong Connection Manager?

**Không.**

Connection Manager:

```text
configure connection
```

UoW:

```text
manage transaction
```

Do đó:

```python
# ConnectionManager
conn = connect()
configure(conn)
return conn
```

còn:

```python
# UoW
conn = manager.connect()
BEGIN
```

Đây là separation of concerns tốt.

---

# 15. Thread safety

Python `sqlite3.connect()` có:

```python
check_same_thread=True
```

mặc định.

Điều đó nghĩa connection thường được dùng trong thread đã tạo nó.

Ví dụ:

```text
Thread A
   │
   └── connection A
```

Không nên:

```text
Thread A
   │
   └── create connection

Thread B
   │
   └── use connection A
```

Cho crawler:

> **Mỗi worker/thread nên có connection riêng.**

Ví dụ:

```text
Worker 1
   ↓
UoW
   ↓
Connection 1

Worker 2
   ↓
UoW
   ↓
Connection 2
```

Không chia sẻ connection giữa workers.

---

# 16. `check_same_thread=False` có phải giải pháp?

Bạn có thể thấy code:

```python
sqlite3.connect(
    db,
    check_same_thread=False,
)
```

Nhưng đừng coi nó là:

> "SQLite thread-safe nên cứ dùng chung connection."

Không.

Nó chỉ bỏ check của Python driver.

Bạn vẫn phải tự đảm bảo synchronization và transaction safety.

Với kiến trúc crawler của chúng ta:

```text
DON'T
shared connection

DO
connection per UoW / worker
```

---

# 17. Production-style Connection Manager

Bây giờ ta xây phiên bản tốt hơn.

```python
from pathlib import Path
import sqlite3


class SQLiteConnectionManager:

    def __init__(
        self,
        db_path: str | Path,
        *,
        timeout: float = 5.0,
    ):
        self.db_path = Path(db_path)
        self.timeout = timeout

    def connect(self) -> sqlite3.Connection:

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
        )

        conn.row_factory = sqlite3.Row

        self._configure(conn)

        return conn

    def _configure(
        self,
        conn: sqlite3.Connection,
    ) -> None:

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        conn.execute(
            "PRAGMA journal_mode = WAL"
        )

        conn.execute(
            "PRAGMA busy_timeout = 5000"
        )
```

---

# 18. Tại sao `_configure()` là private?

Ta không muốn Application làm:

```python
manager._configure(conn)
```

Application chỉ:

```python
conn = manager.connect()
```

Connection Manager tự đảm bảo:

```text
connection returned
       ↓
properly configured
```

Đây là **encapsulation**.

---

# 19. UoW hoàn chỉnh

```python
class SQLiteUnitOfWork:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def __enter__(self):

        self.conn = (
            self.connection_manager.connect()
        )

        self.conn.execute("BEGIN")

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        self.crawl_states = (
            SQLiteCrawlStateRepository(
                self.conn
            )
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        try:

            if exc_type is None:
                self.commit()
            else:
                self.rollback()

        finally:

            self.conn.close()

        return False

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
```

---

# 20. Flow đầy đủ

Bây giờ:

```python
with uow:

    uow.novels.add(novel)

    uow.chapters.add(chapter)

    uow.crawl_states.mark_completed(
        novel.id
    )
```

thực tế:

```text
ConnectionManager
        │
        ▼
   sqlite3.connect()
        │
        ▼
   configure PRAGMA
        │
        ▼
       UoW
        │
        ▼
      BEGIN
        │
        ├── NovelRepository
        ├── ChapterRepository
        └── CrawlStateRepository
                │
                ▼
             COMMIT
                │
                ▼
             CLOSE
```

---

# 21. Một cải tiến: connection chỉ tồn tại trong UoW

Không nên:

```python
manager = SQLiteConnectionManager(...)

conn = manager.connect()

# giữ conn hàng giờ
```

Đặc biệt crawler lâu chạy.

Tốt hơn:

```text
Crawler task
   ↓
create UoW
   ↓
connection
   ↓
transaction
   ↓
commit
   ↓
close
```

Rồi task tiếp theo:

```text
Crawler task 2
   ↓
new UoW
   ↓
new connection
```

Điều này giúp ownership rõ ràng.

---

# 22. Có cần Connection Pool không?

Với app SQLite hiện tại:

**Không cần.**

Bạn có thể nghe đến:

```text
SQLAlchemy connection pool
PostgreSQL pool
asyncpg pool
```

nhưng SQLite embedded database có đặc tính khác.

Kiến trúc hiện tại:

```text
UoW
 ↓
connect
 ↓
use
 ↓
commit/rollback
 ↓
close
```

đã đủ tốt cho giai đoạn này.

Đừng over-engineer.

---

# 23. Crawler architecture

Giờ đặt Connection Manager vào toàn bộ app:

```text
                    CLI / GUI
                       │
                       ▼
                  Application
                       │
                       ▼
                    UseCase
                       │
                       ▼
                  UnitOfWork
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           Novel     Chapter    CrawlState
            Repo       Repo       Repo
             │         │           │
             └─────────┼───────────┘
                       │
                       ▼
             SQLite Connection
                       │
                       ▼
               SQLiteConnection
                  Manager
                       │
                       ▼
                    SQLite
```

---

# 24. Khi crawler chạy nhiều worker

Ví dụ:

```text
Crawler
├── Worker 1
├── Worker 2
├── Worker 3
└── Worker 4
```

Không:

```text
                    SQLite
                      ▲
                      │
                shared connection
              ┌───────┼────────┐
              │       │        │
             W1      W2       W3
```

Mà:

```text
W1 ── UoW ── Connection 1 ──┐
W2 ── UoW ── Connection 2 ──┤
W3 ── UoW ── Connection 3 ──┼── SQLite
W4 ── UoW ── Connection 4 ──┘
```

SQLite vẫn serialize writes ở mức database locking, nhưng connection ownership rõ ràng và an toàn hơn.

---

# 25. Một nuance rất quan trọng: WAL là database-level setting

Ta viết:

```sql
PRAGMA journal_mode = WAL;
```

không nên nghĩ đây chỉ là một option "tạm thời" của connection giống:

```python
row_factory
```

`journal_mode` có persistence/locking semantics ở database level.

Trong thực tế, ta có thể configure nó khi database được initialize.

Ví dụ:

```text
Database initialization
        │
        ├── journal_mode = WAL
        ├── foreign_keys
        └── schema
```

Còn các PRAGMA connection-specific có thể được thiết lập mỗi connection.

Đây là lý do production code nên phân biệt:

```text
Database configuration
vs
Connection configuration
```

---

# 26. Thiết kế tốt hơn nữa

Ta có thể tách:

```text
SQLiteDatabaseInitializer
```

và:

```text
SQLiteConnectionManager
```

Ví dụ:

```text
database/
├── initializer.py
└── connection.py
```

`initializer.py`:

```text
CREATE TABLE
CREATE INDEX
WAL
schema migration
```

`connection.py`:

```text
connect
row_factory
foreign_keys
busy_timeout
```

Kiến trúc này sẽ rất hữu ích khi app crawler của bạn lớn lên.

---

# 27. Database initialization

Ví dụ:

```python
class SQLiteDatabaseInitializer:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def initialize(self):

        conn = self.connection_manager.connect()

        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS novels (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    source TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY,
                    novel_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,

                    FOREIGN KEY (novel_id)
                        REFERENCES novels(id)
                        ON DELETE CASCADE
                );
                """
            )

            conn.commit()

        finally:
            conn.close()
```

Sau này ta có thể nâng cấp thành:

```text
MigrationManager
```

nhưng chưa cần vội.

---

# 28. `ON DELETE CASCADE`

Với app truyện:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

Nếu:

```sql
DELETE FROM novels
WHERE id = ?
```

và foreign key:

```sql
ON DELETE CASCADE
```

thì chapters tương ứng có thể được xóa theo.

Đây là ví dụ Connection Manager bật:

```sql
PRAGMA foreign_keys = ON
```

ảnh hưởng trực tiếp đến correctness của domain persistence.

---

# 29. Checklist Connection Manager

Connection Manager production-style của chúng ta:

```text
SQLiteConnectionManager
│
├── Path handling
│
├── mkdir parent
│
├── sqlite3.connect()
│
├── timeout
│
├── row_factory
│
├── foreign_keys
│
├── busy_timeout
│
└── WAL / database initialization strategy
```

Không chứa:

```text
❌ Novel SQL
❌ Chapter SQL
❌ Business logic
❌ commit của Use Case
❌ rollback của Use Case
```

---

# 30. Kiến trúc sau Buổi 4

Ta đã đi từ:

```text
Repository
```

sang:

```text
Repository
      +
UnitOfWork
      +
Dependency Injection
      +
Connection Manager
```

Kiến trúc hiện tại:

```text
                 Application
                      │
                      ▼
                   UseCase
                      │
                      ▼
               UnitOfWork ABC
                  ▲        ▲
                  │        │
          SQLite UoW    Dummy UoW
              │              │
              ▼              ▼
       SQLite Repository   File Repo
              │
              ▼
       Connection Manager
              │
              ▼
            SQLite
```

---

# Bài tập Buổi 4

Hãy tự viết lại `SQLiteConnectionManager` với API:

```python
manager = SQLiteConnectionManager(
    "data/novels.db",
    timeout=5.0,
)

conn = manager.connect()
```

và đảm bảo:

```python
conn.row_factory == sqlite3.Row
```

đồng thời:

```sql
PRAGMA foreign_keys
```

trả về:

```text
1
```

và:

```sql
PRAGMA journal_mode
```

trả về:

```text
wal
```

Sau đó viết test:

```text
test_connection_creates_database
test_row_factory
test_foreign_keys
test_wal
test_connection_can_execute_sql
```

### Buổi 5

Sau Connection Manager, bước tiếp theo tôi đề xuất là **Repository Deep Dive**:

```text
NovelRepository
     ↓
CRUD
     ↓
Mapping DB Row → Domain Entity
     ↓
Mapping Domain Entity → SQL
     ↓
Query Object
     ↓
Pagination
     ↓
Upsert
     ↓
Bulk Insert
     ↓
N+1 query
     ↓
Repository transaction boundaries
```

Đặc biệt ta sẽ thiết kế `NovelRepository` cho crawler sao cho **Domain hoàn toàn không biết SQLite**, thay vì chỉ viết các class CRUD đơn giản.