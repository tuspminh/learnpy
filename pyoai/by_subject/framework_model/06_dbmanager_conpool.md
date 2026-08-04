# Buổi 6 — DatabaseManager & Connection Manager Deep Dive

> Đây là buổi cực kỳ quan trọng trong series xây dựng framework cào truyện. Từ buổi này trở đi, chúng ta sẽ kết nối toàn bộ những gì đã xây dựng (Model → Metadata → SQL Builder) với SQLite.

Đối với dự án của bạn (**1 database chung + nhiều database riêng cho từng nguồn truyện**), DatabaseManager sẽ là trái tim của toàn bộ hệ thống.

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được kiến trúc như sau:

```text
                      Application
                            │
                            ▼
                     Repository Layer
                            │
                            ▼
                    DatabaseManager
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
 ConnectionManager     TransactionManager    DatabaseRegistry
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                         sqlite3
                            │
        ┌───────────────────┼────────────────────┐
        ▼                                        ▼
   global.db                           truyenfull.db
                                       tangthuvien.db
                                       bachngocsach.db
```

Đây là kiến trúc mà chúng ta sẽ dùng cho toàn bộ framework.

---

# Phần 1. Tại sao cần DatabaseManager?

Nhiều người viết:

```python
conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute(...)

conn.commit()

conn.close()
```

Lặp đi lặp lại hàng nghìn lần.

Không thể mở rộng.

---

Giải pháp

```
Repository

↓

DatabaseManager

↓

SQLite
```

Repository không bao giờ gọi `sqlite3.connect()` trực tiếp.

---

# DatabaseManager có nhiệm vụ gì?

Một DatabaseManager tốt nên quản lý:

* Connection
* Cursor
* Transaction
* Commit
* Rollback
* Context Manager
* Multi Database
* Logging
* SQL Execute
* Thread Safety

---

# Thiết kế tổng quát

```text
DatabaseManager

├── connect()

├── close()

├── execute()

├── executemany()

├── query()

├── begin()

├── commit()

├── rollback()

├── transaction()

└── connection
```

---

# Phần 2. Connection

Đầu tiên

```python
class DatabaseManager:
    def __init__(self, path):

        self.path = path

        self.connection = None
```

---

Kết nối

```python
import sqlite3


class DatabaseManager:
    def connect(self):

        if self.connection is None:
            self.connection = sqlite3.connect(self.path)
```

---

Đóng

```python
def close(self):

    if self.connection:
        self.connection.close()

        self.connection = None
```

---

Sử dụng

```python
db = DatabaseManager("global.db")

db.connect()
```

---

# Lazy Connection

Không mở ngay.

Mở khi cần.

```python
def get_connection(self):

    if self.connection is None:
        self.connect()

    return self.connection
```

Đây là cách phần lớn ORM hoạt động.

---

# Phần 3. Cursor

Không muốn

```python
cursor = conn.cursor()
```

mọi nơi.

DatabaseManager

```python
def cursor(self):

    return self.get_connection().cursor()
```

---

Repository

```python
cursor = db.cursor()
```

---

# Phần 4. Execute

Thay vì

```python
cursor.execute(sql)
```

Viết

```python
db.execute(sql)
```

---

```python
def execute(self, sql, params=()):

    cursor = self.cursor()

    cursor.execute(sql, params)

    return cursor
```

---

Ví dụ

```python
db.execute("SELECT * FROM novel")
```

---

# Query

```python
def query(self, sql, params=()):

    return self.execute(sql, params).fetchall()
```

---

Ví dụ

```python
rows = db.query("SELECT * FROM novel")
```

---

# Query One

```python
def query_one(self, sql, params=()):

    return self.execute(sql, params).fetchone()
```

---

# executemany

Cho insert hàng loạt.

```python
db.executemany(sql, values)
```

---

```python
def executemany(self, sql, rows):

    cur = self.cursor()

    cur.executemany(sql, rows)
```

---

# Phần 5. Transaction

SQLite

```sql
BEGIN
```

↓

execute

↓

```sql
COMMIT
```

---

Hoặc

↓

```sql
ROLLBACK
```

---

DatabaseManager

```python
def begin(self):

    self.execute("BEGIN")
```

---

Commit

```python
def commit(self):

    self.connection.commit()
```

---

Rollback

```python
def rollback(self):

    self.connection.rollback()
```

---

# Vì sao cần Transaction?

Ví dụ

```
Insert Novel

↓

Insert Chapter

↓

Insert Author
```

Nếu Chapter lỗi.

Novel đã lưu.

Database hỏng.

---

Transaction

```
BEGIN

↓

Novel

↓

Chapter

↓

Lỗi

↓

ROLLBACK
```

Không còn dữ liệu dở dang.

---

# Context Manager

Python

```python
with db.transaction():
    ...
```

Tự động:

```
BEGIN

↓

COMMIT
```

Nếu lỗi

↓

```
ROLLBACK
```

---

Ví dụ

```python
from contextlib import contextmanager


@contextmanager
def transaction(self):

    try:
        self.begin()

        yield

        self.commit()

    except:
        self.rollback()

        raise
```

---

Sử dụng

```python
with db.transaction():
    repo.save(...)
```

Đây là cách chuyên nghiệp.

---

# Phần 6. Row Factory

SQLite mặc định

```python
row[0]
```

Khó đọc.

---

Đổi

```python
connection.row_factory = sqlite3.Row
```

---

Kết quả

```python
row["title"]
```

Rõ ràng hơn.

---

DatabaseManager

```python
conn = sqlite3.connect(...)

conn.row_factory = sqlite3.Row
```

---

# Phần 7. Multi Database

Đây là phần quan trọng với framework cào truyện.

Bạn muốn

```text
global.db
```

quản lý

* nguồn truyện
* lịch crawl
* plugin
* settings

---

Mỗi nguồn

```text
truyenfull.db

bachngocsach.db

tangthuvien.db
```

riêng.

---

Ta cần Registry.

```python
class DatabaseRegistry: ...
```

---

Registry

```python
class DatabaseRegistry:
    databases = {}
```

---

Đăng ký

```python
DatabaseRegistry.databases["global"] = DatabaseManager(...)
```

---

Lấy

```python
DatabaseRegistry.get("global")
```

↓

DatabaseManager.

---

Ví dụ

```python
DatabaseRegistry.register("truyenfull", DatabaseManager(...))
```

---

Repository

```python
db = DatabaseRegistry.get("truyenfull")
```

Không cần biết file nằm ở đâu.

---

# Phần 8. Thread Local Connection

Một lỗi phổ biến:

```
Thread A

↓

Connection

↑

Thread B
```

SQLite mặc định không an toàn khi nhiều thread dùng chung một kết nối.

---

Giải pháp

Mỗi thread

↓

một connection.

---

```python
import threading

local = threading.local()
```

---

```python
local.connection
```

sẽ khác nhau giữa các thread.

---

DatabaseManager

```python
self.local = threading.local()
```

---

Kết nối

```python
if not hasattr(

    self.local,

    "connection"

):
```

↓

tạo mới.

---

Đây là cách nhiều ORM xử lý.

---

# Phần 9. Connection Pool?

SQLite không thực sự cần Connection Pool như PostgreSQL hay MySQL.

Vì:

* file local
* mở nhanh

Nhưng ta vẫn nên có

```text
DatabaseManager

↓

Connection Factory

↓

thread local
```

Đủ cho desktop app và crawler.

---

# Logging SQL

Ví dụ

```python
db.execute(sql, params)
```

In

```text
SQL:

SELECT *

PARAMS:

()
```

Debug rất dễ.

---

# Đo thời gian SQL

```python
start = perf_counter()

...

elapsed = ...
```

Log

```text
12 ms
```

Giúp tìm truy vấn chậm.

---

# Kiến trúc sau Buổi 6

```text
                     Repository

                          │

                          ▼

                  DatabaseManager

       ┌──────────────────┼─────────────────┐

       ▼                  ▼                 ▼

 Connection         Transaction       SQL Execute

       │                  │                 │

       └──────────────────┼─────────────────┘

                          ▼

                   sqlite3.Connection

                          │

                          ▼

             SQLite Database Files

      global.db

      truyenfull.db

      tangthuvien.db
```

---

# Dành riêng cho Framework Cào Truyện

Đây là kiến trúc mình khuyến nghị:

```text
database/

│

├── global.db

│

├── sources/

│      ├── truyenfull.db
│      ├── tangthuvien.db
│      ├── bachngocsach.db
│      └── ...
│

└── cache/

       search.db
```

Trong đó:

**global.db**

* plugin
* source
* crawler_job
* crawler_history
* settings
* user
* bookshelf
* reading_history

Mỗi database nguồn:

* novel
* chapter
* author
* category
* tag
* image_cache

Kiến trúc này rất phù hợp với yêu cầu ban đầu của dự án: **một database quản lý chung và một database riêng cho từng nguồn truyện**.

---

# Những điểm nên cải tiến so với phiên bản đầu

1. **Không tự động `commit()` trong `execute()`**. Hãy để transaction hoặc Repository quyết định thời điểm commit.

2. **Không để Repository gọi `cursor()` trực tiếp**. Chỉ nên dùng:

   * `execute()`
   * `query_one()`
   * `query_all()`
   * `executemany()`

3. **Bọc toàn bộ thao tác ghi trong transaction**:

```python
with db.transaction():
    novel_repo.save(novel)
    chapter_repo.save_many(chapters)
```

4. **Thêm lớp cấu hình** để quản lý đường dẫn database thay vì ghi cứng chuỗi `"global.db"`.

---

# Bài tập thực hành

## Bài 1

Viết `DatabaseManager` với các phương thức:

* `connect()`
* `close()`
* `get_connection()`
* `execute()`
* `query_one()`
* `query_all()`
* `executemany()`

---

## Bài 2

Viết context manager:

```python
with db.transaction():
    ...
```

tự động:

* `BEGIN`
* `COMMIT`
* `ROLLBACK`

---

## Bài 3

Xây dựng `DatabaseRegistry` hỗ trợ:

```python
register(name, db)

get(name)

remove(name)

list()
```

---

## Bài 4

Cấu hình kiến trúc nhiều database:

```text
database/
    global.db
    sources/
        truyenfull.db
        tangthuvien.db
        bachngocsach.db
```

và khởi tạo registry tương ứng.

---

## Bài 5

Thêm logging cho `execute()`:

* SQL
* Parameters
* Thời gian thực thi (ms)

để phục vụ debug và tối ưu hiệu năng.

---

# Buổi tiếp theo

**Buổi 7 — Repository Pattern Deep Dive**

Đây là buổi chúng ta sẽ xây dựng tầng Repository hoàn chỉnh, bao gồm:

* `BaseRepository<T>`
* CRUD tự động từ metadata
* Mapping `sqlite3.Row` ↔ `Model`
* `find_by_id()`
* `find_one()`
* `find_all()`
* `insert()`
* `update()`
* `delete()`
* `save()` (tự quyết định INSERT hay UPDATE)
* Generic Repository với `TypeVar` và `Generic`
* Repository chuyên biệt cho từng model (`NovelRepository`, `ChapterRepository`)

Sau buổi này, framework của bạn sẽ có tầng truy cập dữ liệu sạch, mở rộng tốt và sẵn sàng tích hợp với hệ thống crawler và ứng dụng đọc truyện.
