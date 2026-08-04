# Buổi 5 — Connection Registry (SQLite) & Database Lifecycle

> Đây là buổi thay thế **Connection Pool**.
>
> SQLite **không phải** MySQL/PostgreSQL, vì vậy Connection Pool truyền thống không mang lại nhiều lợi ích. Thay vào đó, chúng ta sẽ xây dựng một **Connection Registry** (hay Connection Cache), phù hợp với kiến trúc SQLite và framework plugin của chúng ta.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu vì sao SQLite không cần Connection Pool truyền thống.
* Xây dựng `ConnectionRegistry`.
* Quản lý vòng đời (lifecycle) của Connection.
* Ngăn mở trùng Connection.
* Tự động đóng Connection khi ứng dụng kết thúc.
* Chuẩn bị cho đa luồng (thread-safe) ở các buổi sau.

---

# 1. Connection Pool là gì?

Trong MySQL hoặc PostgreSQL:

```text
Application
      │
      ▼
Connection Pool
      │
 ┌────┼────┐
 │    │    │
Conn1 Conn2 Conn3
 │    │    │
 MySQL Server
```

Mỗi request lấy một connection từ pool rồi trả lại.

Lý do:

* Mở TCP Connection tốn thời gian.
* Xác thực người dùng.
* Bắt tay (handshake).
* Quản lý session.

---

# 2. SQLite khác hoàn toàn

SQLite không có server.

```text
Application

↓

sqlite3

↓

story.db
```

Không có:

* TCP
* Authentication
* Session
* Network

Việc mở Connection nhanh hơn rất nhiều.

Nhưng nếu mở liên tục:

```python
sqlite3.connect(...)
sqlite3.connect(...)
sqlite3.connect(...)
```

thì vẫn:

* Tốn tài nguyên.
* Tăng nguy cơ khóa file (`database is locked`).
* Khó quản lý transaction.

---

# 3. Giải pháp của chúng ta

Không dùng Pool.

Ta dùng:

```text
DatabaseManager

↓

Connection Registry

↓

SQLiteConnection
```

Một file SQLite chỉ có **một đối tượng `SQLiteConnection`** trong một tiến trình.

Ví dụ:

```text
manager.db

↓

SQLiteConnection #1
```

```text
truyenfull.db

↓

SQLiteConnection #2
```

```text
wikidich.db

↓

SQLiteConnection #3
```

---

# 4. Trạng thái của Connection

Mỗi Connection có vòng đời:

```text
CREATED

↓

OPEN

↓

ACTIVE

↓

IDLE

↓

CLOSED
```

Giải thích:

* **CREATED**: đối tượng đã được tạo nhưng chưa mở file.
* **OPEN**: đã kết nối tới SQLite.
* **ACTIVE**: đang thực hiện SQL.
* **IDLE**: đang mở nhưng không có truy vấn.
* **CLOSED**: đã đóng.

---

# 5. Bổ sung trạng thái vào SQLiteConnection

Tạo `Enum`:

```python
from enum import Enum


class ConnectionState(Enum):
    CREATED = "created"

    OPEN = "open"

    ACTIVE = "active"

    IDLE = "idle"

    CLOSED = "closed"
```

Trong constructor:

```python
self.state = ConnectionState.CREATED
```

---

# 6. Khi mở

```python
def open(self):

    ...

    self.state = ConnectionState.OPEN
```

---

# 7. Khi execute

```python
def execute(...):

    self.state = ConnectionState.ACTIVE

    ...

    self.state = ConnectionState.IDLE
```

Bây giờ có thể biết Connection nào đang bận.

---

# 8. Khi đóng

```python
def close(self):

    ...

    self.state = ConnectionState.CLOSED
```

---

# 9. Registry

Hiện tại

```python
self.connections = {}
```

Ta đổi thành

```python
{
    "manager": SQLiteConnection,
    "truyenfull": SQLiteConnection,
    "wikidich": SQLiteConnection,
}
```

Đây chính là Registry.

---

# 10. Thêm exists()

```python
def exists(self, name):

    return name in self.connections
```

Ví dụ

```python
manager.exists("manager")
```

↓

```python
True
```

---

# 11. remove()

```python
def remove(self, name):

    if name not in self.connections:
        return

    self.connections[name].close()

    del self.connections[name]
```

Khác với `close()` ở chỗ:

* Đóng Connection.
* Xóa khỏi Registry.

---

# 12. count()

```python
def count(self):

    return len(self.connections)
```

Ví dụ

```python
print(manager.count())
```

↓

```text
3
```

---

# 13. names()

```python
def names(self):

    return sorted(self.connections.keys())
```

Kết quả:

```python
["manager", "truyenfull", "wikidich"]
```

---

# 14. status()

```python
def status(self):

    result = {}

    for name, db in self.connections.items():
        result[name] = db.state.value

    return result
```

Ví dụ

```python
print(manager.status())
```

↓

```python
{"manager": "idle", "truyenfull": "active", "wikidich": "idle"}
```

---

# 15. CLI Test

Trong `app.py`

```python
manager.open("manager")

manager.open("truyenfull")

manager.open("wikidich")

print(manager.count())

print(manager.names())

print(manager.status())
```

Kết quả

```text
3

['manager', 'truyenfull', 'wikidich']

{
    'manager': 'idle',
    'truyenfull': 'idle',
    'wikidich': 'idle'
}
```

---

# 16. Tự động đóng khi chương trình kết thúc

Python có module:

```python
import atexit
```

Đăng ký:

```python
atexit.register(manager.close_all)
```

Khi chương trình kết thúc:

```text
CTRL+C

↓

close_all()

↓

mọi SQLite đều được đóng
```

Đây là cách rất phổ biến trong các ứng dụng CLI.

---

# 17. Thread Safety

Hiện tại:

```python
self.connections
```

chưa được bảo vệ.

Nếu nhiều Thread:

```text
Thread A

↓

open("manager")


Thread B

↓

open("manager")
```

có thể cùng tạo hai Connection.

Ở các buổi sau, chúng ta sẽ dùng:

```python
threading.Lock()
```

để đảm bảo mỗi database chỉ được mở một lần.

---

# 18. Những điểm cần cải tiến

Phiên bản hiện tại vẫn còn một số hạn chế:

## Không nên để `execute()` chuyển trạng thái về `IDLE` ngay lập tức

Nếu Repository lấy `cursor` và tiếp tục đọc dữ liệu, trạng thái `ACTIVE` có thể vẫn còn phù hợp. Sau này ta sẽ quản lý trạng thái ở mức transaction hoặc context manager.

## Bổ sung thông tin thống kê

Có thể thêm:

```python
self.query_count = 0
self.last_used_at = None
self.opened_at = None
```

Điều này giúp:

* Theo dõi hiệu năng.
* Phát hiện Connection lâu không dùng.
* Ghi log.

## Không dùng Singleton

Nhiều ví dụ trên Internet biến `DatabaseManager` thành Singleton.

Trong framework của chúng ta **không làm vậy** vì:

* Khó viết unit test.
* Khó thay thế bằng mock.
* Khó chạy nhiều môi trường (test, production) trong cùng tiến trình.

Ta sẽ truyền `DatabaseManager` vào Repository bằng dependency injection ở các buổi sau.

---

# API sau buổi 5

```python
manager.open()

manager.get()

manager.exists()

manager.remove()

manager.count()

manager.names()

manager.status()

manager.close()

manager.close_all()
```

---

# Bài tập thực hành

## Bài 1

Tạo `ConnectionState` bằng `Enum` và tích hợp vào `SQLiteConnection`.

## Bài 2

Bổ sung các phương thức cho `DatabaseManager`:

* `exists()`
* `remove()`
* `count()`
* `names()`
* `status()`

## Bài 3

Đăng ký:

```python
import atexit

atexit.register(manager.close_all)
```

và xác minh rằng khi chương trình kết thúc, tất cả Connection đều được đóng.

## Bài 4 (khuyến khích)

Thêm các thuộc tính:

```python
opened_at
last_used_at
query_count
```

và cập nhật chúng mỗi khi thực hiện truy vấn.

---

# Kết quả sau buổi 5

Đến thời điểm này, bạn đã xây dựng được một tầng quản lý kết nối có kiến trúc khá hoàn chỉnh:

```text
                    Repository
                         │
                         ▼
                 DatabaseManager
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
 SQLiteConnection  SQLiteConnection  SQLiteConnection
    manager.db      truyenfull.db      wikidich.db
         │               │               │
         └───────────────┴───────────────┘
                    sqlite3
```

Mỗi file SQLite chỉ có một kết nối trong một tiến trình, được quản lý tập trung, có trạng thái rõ ràng và có thể kiểm thử hoàn toàn bằng CLI.

---

# Chuẩn bị cho Buổi 6

Theo roadmap, buổi tiếp theo là **Transaction**.

Đây sẽ là một trong những buổi quan trọng nhất vì chúng ta sẽ xây dựng:

* `begin()`
* `commit()`
* `rollback()`
* Context Manager cho transaction (`with db.transaction():`)
* Tự động rollback khi có ngoại lệ
* Giao dịch nhiều bước (ví dụ: thêm truyện + thêm tác giả + thêm thể loại) theo nguyên tắc **all-or-nothing**.

Sau buổi 6, tầng dữ liệu của framework sẽ đủ mạnh để bắt đầu xây dựng **BaseModel** và **BaseRepository** ở các phần tiếp theo.
