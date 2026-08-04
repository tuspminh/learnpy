# Buổi 4 — Xây dựng SQLite Wrapper chuyên nghiệp

> Đây là buổi biến `sqlite3.Connection` thành một lớp wrapper có thể tái sử dụng cho toàn bộ framework.

Sau buổi này, **Repository sẽ không còn biết đến `sqlite3.Connection` nữa**, mà chỉ làm việc với `SQLiteConnection`.

---

# Mục tiêu

Sau buổi học bạn sẽ xây dựng được:

* `execute()`
* `executemany()`
* `executescript()`
* `fetchone()`
* `fetchall()`
* `commit()`
* `rollback()`
* `cursor()`
* `last_insert_id`
* `row_factory`
* PRAGMA tối ưu SQLite

---

# 1. Vì sao cần Wrapper?

Rất nhiều project viết như sau:

```python
conn = sqlite3.connect("story.db")

cursor = conn.cursor()

cursor.execute(sql)

rows = cursor.fetchall()

conn.commit()

conn.close()
```

Đoạn code này sẽ lặp lại ở:

* StoryRepository
* ChapterRepository
* AuthorRepository
* BookmarkRepository
* HistoryRepository

Đây là **code trùng lặp (duplication)**.

Thay vào đó:

```text
Repository

↓

SQLiteConnection

↓

sqlite3
```

Repository chỉ gọi:

```python
db.execute(...)
db.fetchall(...)
db.fetchone(...)
```

---

# 2. Kiến trúc mới

```text
DatabaseManager
        │
        ▼
SQLiteConnection
        │
        ▼
sqlite3.Connection
        │
        ▼
sqlite3.Cursor
```

Chỉ có `SQLiteConnection` được phép làm việc trực tiếp với `Cursor`.

---

# 3. Khởi tạo Connection

Cập nhật phương thức `open()`:

```python
import sqlite3


def open(self):

    if self.connection is not None:
        return self.connection

    self.connection = sqlite3.connect(self.path)

    self.connection.row_factory = sqlite3.Row

    return self.connection
```

---

## Vì sao dùng `sqlite3.Row`?

Không dùng:

```python
row[0]
row[1]
row[2]
```

Mà dùng:

```python
row["title"]

row["author"]

row["cover"]
```

Code sẽ dễ đọc hơn rất nhiều.

---

# 4. cursor()

```python
def cursor(self):

    return self.connection.cursor()
```

Repository sẽ không phải tự tạo cursor nữa.

---

# 5. execute()

Đây là hàm được dùng nhiều nhất.

```python
def execute(self, sql, params=None):

    if params is None:
        params = ()

    cur = self.cursor()

    cur.execute(sql, params)

    return cur
```

Ví dụ:

```python
db.execute("DELETE FROM story WHERE id=?", (10,))
```

---

# 6. executemany()

Ví dụ thêm 1000 chương.

Không nên:

```python
for chapter in chapters:
    execute(...)
```

Hãy dùng:

```python
def executemany(self, sql, values):

    cur = self.cursor()

    cur.executemany(sql, values)

    return cur
```

Ví dụ:

```python
db.executemany("INSERT INTO chapter(title) VALUES(?)", [("A",), ("B",), ("C",)])
```

---

# 7. executescript()

SQLite hỗ trợ chạy cả file SQL.

Ví dụ:

```sql
CREATE TABLE story(...);

CREATE TABLE chapter(...);

CREATE INDEX ...;
```

Ta cần:

```python
def executescript(self, script):

    cur = self.cursor()

    cur.executescript(script)

    return cur
```

Sau này dùng để:

* tạo schema
* migration
* test

---

# 8. fetchone()

Repository không cần gọi:

```python
cursor.fetchone()
```

Ta bọc lại:

```python
def fetchone(self, sql, params=None):

    cur = self.execute(sql, params)

    return cur.fetchone()
```

Ví dụ:

```python
row = db.fetchone("SELECT * FROM story WHERE id=?", (5,))
```

---

# 9. fetchall()

```python
def fetchall(self, sql, params=None):

    cur = self.execute(sql, params)

    return cur.fetchall()
```

Ví dụ

```python
stories = db.fetchall("SELECT * FROM story")
```

---

# 10. commit()

```python
def commit(self):

    self.connection.commit()
```

---

# 11. rollback()

```python
def rollback(self):

    self.connection.rollback()
```

---

# 12. last_insert_id

SQLite rất hay dùng.

```python
INSERT INTO story ...
```

làm sao biết id vừa tạo?

```python
cursor.lastrowid
```

Ta bọc:

```python
@property
def last_insert_id(self):

    cur = self.cursor()

    return cur.lastrowid
```

> **Lưu ý:** Cách trên chưa chính xác vì `lastrowid` thuộc về **cursor vừa thực hiện lệnh INSERT**, không phải một cursor mới. Thiết kế tốt hơn là để `execute()` trả về `cursor`, sau đó Repository lấy:
>
> ```python
> cursor = db.execute(sql, params)
> story_id = cursor.lastrowid
> ```
>
> Hoặc `SQLiteConnection` lưu lại cursor cuối cùng để cung cấp `last_insert_id`.

---

# 13. Tối ưu SQLite

Ngay sau khi mở connection:

```python
self.connection.execute("PRAGMA foreign_keys = ON")
```

Để bật Foreign Key.

---

## WAL

```python
self.connection.execute("PRAGMA journal_mode=WAL")
```

Giúp:

* đọc nhanh hơn
* ghi ổn định hơn

---

## Busy Timeout

```python
self.connection.execute("PRAGMA busy_timeout = 5000")
```

Nếu database đang bị khóa

SQLite sẽ đợi

```text
5 giây
```

thay vì báo lỗi ngay.

---

## Một phiên bản `open()` hoàn chỉnh hơn

```python
def open(self):

    if self.connection is not None:
        return self.connection

    self.connection = sqlite3.connect(self.path)

    self.connection.row_factory = sqlite3.Row

    self.connection.execute("PRAGMA foreign_keys = ON")

    self.connection.execute("PRAGMA journal_mode=WAL")

    self.connection.execute("PRAGMA busy_timeout = 5000")

    return self.connection
```

---

# 14. Test CLI

Trong `app.py`

```python
db = manager.open("manager")

db.execute("""

CREATE TABLE IF NOT EXISTS test(

id INTEGER PRIMARY KEY,

name TEXT

)

""")

db.execute("INSERT INTO test(name) VALUES(?)", ("Python",))

db.commit()

rows = db.fetchall("SELECT * FROM test")

for row in rows:
    print(row["id"], row["name"])
```

Kết quả

```text
1 Python
```

---

# 15. API cuối cùng của SQLiteConnection

```python
db.open()

db.close()

db.cursor()

db.execute()

db.executemany()

db.executescript()

db.fetchone()

db.fetchall()

db.commit()

db.rollback()
```

Đây là API mà toàn bộ Repository sẽ dùng.

---

# 16. Một số cải tiến nên chuẩn bị

Để wrapper đủ mạnh cho framework lâu dài, chúng ta sẽ bổ sung trong các buổi sau:

| Tính năng          | Mục đích                                        |
| ------------------ | ----------------------------------------------- |
| `execute_scalar()` | Lấy một giá trị như `COUNT(*)`                  |
| `table_exists()`   | Kiểm tra bảng đã tồn tại                        |
| `begin()`          | Bắt đầu transaction rõ ràng                     |
| `in_transaction`   | Kiểm tra trạng thái transaction                 |
| Logging SQL        | Ghi log khi debug                               |
| Context Manager    | `with SQLiteConnection(...)` tự commit/rollback |

Các tính năng này sẽ được thêm dần để giữ mỗi buổi học tập trung.

---

# Bài tập thực hành

## Bài 1

Hoàn thiện `SQLiteConnection` với các phương thức:

* `cursor()`
* `execute()`
* `executemany()`
* `executescript()`
* `fetchone()`
* `fetchall()`
* `commit()`
* `rollback()`

## Bài 2

Cập nhật `open()` để:

* Bật `sqlite3.Row`
* Bật `PRAGMA foreign_keys = ON`
* Bật `PRAGMA journal_mode = WAL`
* Thiết lập `PRAGMA busy_timeout = 5000`

## Bài 3

Tạo bảng `test`, chèn vài bản ghi và kiểm tra:

* `fetchone()`
* `fetchall()`
* `lastrowid` từ cursor trả về bởi `execute()`

---

# Kết quả sau buổi 4

Bạn đã xây dựng xong tầng truy cập SQLite cơ bản:

```text
Repository
      │
      ▼
SQLiteConnection
      │
      ├── execute()
      ├── fetchone()
      ├── fetchall()
      ├── executemany()
      ├── commit()
      └── rollback()
      │
      ▼
sqlite3
```

Đây là nền tảng để Repository hoạt động mà không phụ thuộc trực tiếp vào `sqlite3`.

## Chuẩn bị cho Buổi 5

Theo roadmap ban đầu, buổi 5 là **Connection Pool (SQLite)**. Tuy nhiên, vì SQLite hoạt động khác với các hệ quản trị CSDL dạng client/server, chúng ta sẽ không xây dựng một connection pool theo kiểu truyền thống. Thay vào đó, chúng ta sẽ thiết kế một **Connection Registry**:

* Mỗi file database chỉ có **một connection** trong một tiến trình.
* `DatabaseManager` chịu trách nhiệm tạo và tái sử dụng connection.
* Hỗ trợ nhiều database mở đồng thời (`manager.db`, `truyenfull.db`, `wikidich.db`, ...).
* Chuẩn bị cho môi trường đa luồng và plugin mà không tạo kết nối dư thừa.

Thiết kế này phù hợp với SQLite hơn, đơn giản hơn và vẫn đáp ứng tốt nhu cầu của framework.
