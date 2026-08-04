# Buổi 3 — Xây dựng DatabaseManager (Phần 1)

> Đây là buổi quan trọng nhất của toàn bộ framework.
>
> Nếu `DatabaseManager` được thiết kế tốt, các tầng **Repository**, **Plugin**, **Crawler**, **Reader** sau này sẽ rất đơn giản.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu trách nhiệm của `DatabaseManager`
* Thiết kế API của `DatabaseManager`
* Quản lý nhiều SQLite cùng lúc
* Tự động tạo database
* Mỗi database chỉ có **một connection**
* Có thể test hoàn toàn bằng CLI

> Hôm nay **chưa tạo bảng**, chỉ xây dựng lớp quản lý kết nối.

---

# 1. Vai trò của DatabaseManager

Hãy xem kiến trúc.

```text
CLI

↓

Repository

↓

DatabaseManager

↓

sqlite3

↓

manager.db
truyenfull.db
wikidich.db
...
```

Repository **không được phép** gọi

```python
sqlite3.connect(...)
```

Repository chỉ được phép gọi

```python
db = database_manager.get_database(...)
```

---

# 2. Trách nhiệm

DatabaseManager chỉ làm đúng các việc sau:

✓ mở database

✓ đóng database

✓ cache connection

✓ trả connection

✓ tạo database mới

✓ kiểm tra database tồn tại

✓ liệt kê database đang mở

KHÔNG làm

✗ execute SQL

✗ insert

✗ update

✗ delete

✗ transaction

✗ migration

Những việc đó sẽ học ở buổi sau.

---

# 3. Thiết kế API

Đây là API mà chúng ta hướng tới.

```python
manager = DatabaseManager()

manager.open("manager")

manager.open("truyenfull")

manager.open("wikidich")

conn = manager.get("manager")

manager.close("manager")

manager.close_all()
```

API rất nhỏ.

Đó là dấu hiệu của một thiết kế tốt.

---

# 4. Cấu trúc thư mục

Sau buổi này sẽ có:

```text
story_framework/
│
├── app.py
│
├── settings.py
│
├── framework/
│
│   └── db/
│
│       ├── __init__.py
│
│       ├── database_manager.py
│
│       └── sqlite_connection.py
│
└── databases/
```

---

# 5. settings.py

Mọi đường dẫn nên nằm ở đây.

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent

DATABASE_DIR = BASE_DIR / "databases"

DATABASE_DIR.mkdir(exist_ok=True)
```

Lợi ích

Mai sau đổi thư mục

```text
database/

↓

storage/database/
```

chỉ sửa đúng một nơi.

---

# 6. sqlite_connection.py

Lớp này chỉ đại diện cho **một SQLite**.

```python
import sqlite3

from pathlib import Path


class SQLiteConnection:
    def __init__(self, path: Path):

        self.path = path

        self.connection = None
```

Ban đầu chỉ có hai thuộc tính.

---

## Hàm open()

```python
def open(self):

    if self.connection is None:
        self.connection = sqlite3.connect(self.path)

    return self.connection
```

Nếu đã mở rồi

sẽ không mở lại.

---

## Hàm close()

```python
def close(self):

    if self.connection:
        self.connection.close()

        self.connection = None
```

Rất đơn giản.

---

# 7. DatabaseManager

Khởi tạo.

```python
from pathlib import Path

from framework.db.sqlite_connection import SQLiteConnection


class DatabaseManager:
    def __init__(self, database_dir: Path):

        self.database_dir = database_dir

        self.connections = {}
```

connections

là cache.

Ví dụ

```python
{
    "manager": SQLiteConnection,
    "truyenfull": SQLiteConnection,
    "wikidich": SQLiteConnection,
}
```

---

# 8. Tạo đường dẫn database

```python
def make_path(self, name):

    return self.database_dir / f"{name}.db"
```

Ví dụ

```python
make_path("manager")
```

↓

```text
databases/manager.db
```

---

# 9. open()

Đây là hàm quan trọng nhất.

```python
def open(self, name):

    if name in self.connections:
        return self.connections[name]

    path = self.make_path(name)

    db = SQLiteConnection(path)

    db.open()

    self.connections[name] = db

    return db
```

Điều gì xảy ra?

Lần đầu

```python
manager.open("truyenfull")
```

↓

```text
sqlite3.connect(...)
```

Lần thứ hai

```python
manager.open("truyenfull")
```

↓

trả object cũ.

Không connect nữa.

---

# 10. get()

```python
def get(self, name):

    return self.connections.get(name)
```

Nếu chưa mở

trả về

```python
None
```

---

# 11. close()

```python
def close(self, name):

    db = self.connections.get(name)

    if db:
        db.close()

        del self.connections[name]
```

---

# 12. close_all()

```python
def close_all(self):

    for db in self.connections.values():
        db.close()

    self.connections.clear()
```

---

# 13. list_database()

```python
def list_database(self):

    return list(self.connections.keys())
```

Ví dụ

```python
["manager", "truyenfull", "wikidich"]
```

---

# 14. Kiểm tra hoạt động

```python
manager.open("manager")

manager.open("truyenfull")

manager.open("wikidich")
```

Cache

```text
connections

↓

manager

↓

SQLiteConnection

↓

sqlite3.Connection
```

và

```text
connections

↓

truyenfull

↓

SQLiteConnection

↓

sqlite3.Connection
```

---

# 15. CLI Test

Tạm thời viết trong `app.py`

```python
from settings import DATABASE_DIR
from framework.db.database_manager import DatabaseManager

manager = DatabaseManager(DATABASE_DIR)

manager.open("manager")
manager.open("truyenfull")
manager.open("wikidich")

print(manager.list_database())

manager.close("manager")

print(manager.list_database())

manager.close_all()

print(manager.list_database())
```

Kết quả mong muốn:

```text
['manager', 'truyenfull', 'wikidich']

['truyenfull', 'wikidich']

[]
```

---

# 16. Vì sao phải cache connection?

Nếu mỗi Repository đều làm:

```python
sqlite3.connect(...)
```

thì:

```text
StoryRepository

↓

connect()

↓

close()


ChapterRepository

↓

connect()

↓

close()


AuthorRepository

↓

connect()

↓

close()
```

Một thao tác đọc truyện có thể mở/đóng kết nối hàng chục lần.

Với `DatabaseManager`:

```text
DatabaseManager

↓

connect()

↓

cache

↓

Repository dùng chung
```

Chỉ mở **một lần**.

---

# 17. Những điểm sẽ cải tiến ở các buổi sau

Phiên bản hôm nay là nền tảng. Trong các buổi tiếp theo, chúng ta sẽ bổ sung:

* `sqlite3.Row` để truy cập dữ liệu theo tên cột.
* Bật `PRAGMA foreign_keys = ON`.
* Thiết lập `journal_mode = WAL` để tăng hiệu năng đọc/ghi.
* `busy_timeout` để tránh lỗi khi nhiều tiến trình cùng truy cập.
* Context Manager (`with DatabaseManager...`).
* Quản lý transaction.
* Migration và khởi tạo schema tự động.
* Thread-safe nếu crawler chạy đa luồng.

Chúng ta **không thêm tất cả ngay hôm nay** để mỗi buổi chỉ tập trung vào một khái niệm.

---

# Bài tập thực hành

## Bài 1

Tạo hai file:

```text
framework/db/sqlite_connection.py

framework/db/database_manager.py
```

và cài đặt đầy đủ các phương thức:

* `open()`
* `close()`

cho `SQLiteConnection`.

## Bài 2

Hoàn thiện `DatabaseManager` với các phương thức:

* `make_path()`
* `open()`
* `get()`
* `close()`
* `close_all()`
* `list_database()`

## Bài 3

Viết chương trình trong `app.py` để:

1. Mở `manager.db`
2. Mở `truyenfull.db`
3. Mở `wikidich.db`
4. In danh sách database đang mở.
5. Đóng `manager.db`.
6. Đóng tất cả.
7. Kiểm tra xem các file `.db` đã được tạo trong thư mục `databases/`.

---

# Kết quả sau buổi 3

Bạn đã xây dựng được tầng đầu tiên của framework:

```text
Repository
      │
      ▼
DatabaseManager
      │
      ▼
SQLiteConnection
      │
      ▼
sqlite3.Connection
```

Đây sẽ là nền móng để mọi thành phần khác sử dụng.

Ở **Buổi 4**, chúng ta sẽ nâng cấp `SQLiteConnection` thành một **SQLite Wrapper** chuyên nghiệp với các khả năng:

* Thực thi SQL (`execute`, `executemany`, `executescript`)
* Truy vấn (`fetchone`, `fetchall`)
* Quản lý transaction (`commit`, `rollback`)
* Trả kết quả dưới dạng `sqlite3.Row`
* Áp dụng các `PRAGMA` tối ưu (`foreign_keys`, `WAL`, `busy_timeout`)

Sau buổi 4, `Repository` sẽ không còn phải làm việc trực tiếp với `sqlite3.Connection` nữa mà sẽ sử dụng một API thống nhất, sạch và dễ kiểm thử.
