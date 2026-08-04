# Buổi 6 — Transaction Manager & Unit of Work (SQLite)

> Đây là một trong những buổi quan trọng nhất của toàn bộ framework.
>
> Sau buổi này, framework sẽ có khả năng đảm bảo **tính toàn vẹn dữ liệu (Data Integrity)**. Nếu một bước thất bại, **toàn bộ thay đổi sẽ được hoàn tác (rollback)**.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu Transaction là gì.
* Biết khi nào cần Transaction.
* Xây dựng Transaction API cho `SQLiteConnection`.
* Viết Context Manager cho Transaction.
* Hiểu nền tảng của **Unit of Work Pattern**.
* Test hoàn toàn bằng CLI.

---

# 1. Transaction là gì?

Giả sử crawler lưu một truyện mới.

Các bước:

```text
Thêm Author

↓

Thêm Story

↓

Thêm Categories

↓

Thêm Chapters
```

Nếu bước cuối lỗi:

```text
Author ✓

Story ✓

Category ✓

Chapter ✗
```

Database sẽ trở thành:

```text
Story tồn tại

Nhưng không có Chapter
```

Đây là dữ liệu **không nhất quán (Inconsistent Data).**

---

# 2. Có Transaction

```text
BEGIN

↓

Author

↓

Story

↓

Category

↓

Chapter

↓

COMMIT
```

Nếu Chapter lỗi

```text
BEGIN

↓

Author

↓

Story

↓

Category

↓

Chapter ERROR

↓

ROLLBACK
```

Kết quả

```text
Không có Author

Không có Story

Không có Category
```

Mọi thứ quay về trạng thái ban đầu.

---

# 3. API mong muốn

Repository sẽ dùng như sau:

```python
with db.transaction():
    ...

    db.execute(...)

    db.execute(...)

    db.execute(...)
```

Nếu có Exception

↓

Rollback

Nếu không có Exception

↓

Commit

---

# 4. begin()

Trong SQLiteConnection

```python
def begin(self):

    self.connection.execute("BEGIN")
```

---

# 5. commit()

Ta đã có

```python
def commit(self):

    self.connection.commit()
```

---

# 6. rollback()

```python
def rollback(self):

    self.connection.rollback()
```

---

# 7. Context Manager

Đây là cách Pythonic nhất.

```python
from contextlib import contextmanager
```

---

## transaction()

```python
from contextlib import contextmanager


@contextmanager
def transaction(self):

    self.begin()

    try:
        yield

        self.commit()

    except Exception:
        self.rollback()

        raise
```

Đây là API chúng ta sẽ dùng trong toàn bộ framework.

---

# 8. Test đầu tiên

```python
with db.transaction():
    db.execute(...)

    db.execute(...)

    db.execute(...)
```

Không có Exception

↓

Commit

---

# 9. Test lỗi

```python
with db.transaction():
    db.execute(...)

    raise Exception()

    db.execute(...)
```

Kết quả

↓

Rollback

Không có dữ liệu nào được lưu.

---

# 10. Ví dụ thực tế

Crawler:

```python
with db.transaction():
    author_repo.add(author)

    story_repo.add(story)

    category_repo.add_many(...)

    chapter_repo.add_many(...)
```

Nếu

```python
chapter_repo.add_many(...)
```

lỗi

↓

Rollback tất cả.

---

# 11. Vì sao không commit trong execute()?

Đây là lỗi người mới rất hay mắc.

Sai

```python
def execute(...):

    ...

    self.connection.commit()
```

Nếu vậy

```python
execute()

↓

commit
```

mọi Transaction sẽ vô nghĩa.

Repository sẽ không thể rollback.

---

# 12. Quy tắc

execute()

Không bao giờ commit.

Repository

Không commit.

DatabaseManager

Không commit.

Chỉ Transaction

được commit.

---

# 13. Nested Transaction

SQLite

Không hỗ trợ

```text
BEGIN

↓

BEGIN
```

Điều này sẽ gây lỗi.

Ví dụ

```python
with db.transaction():
    ...

    with db.transaction():
        ...
```

↓

Error

---

# 14. Giải pháp trước mắt

Thêm cờ

```python
self.in_transaction = False
```

---

## begin()

```python
def begin(self):

    if self.in_transaction:
        raise RuntimeError("Transaction already started")

    self.connection.execute("BEGIN")

    self.in_transaction = True
```

---

## commit()

```python
def commit(self):

    self.connection.commit()

    self.in_transaction = False
```

---

## rollback()

```python
def rollback(self):

    self.connection.rollback()

    self.in_transaction = False
```

---

# 15. Savepoint

Sau này

ta sẽ hỗ trợ

```text
BEGIN

↓

SAVEPOINT

↓

ROLLBACK TO SAVEPOINT
```

Nhưng chưa cần ở giai đoạn này.

---

# 16. Logging Transaction

Sau này rất hữu ích.

Ví dụ

```text
BEGIN

INSERT Story

INSERT Chapter

INSERT Chapter

COMMIT
```

Hoặc

```text
BEGIN

INSERT Story

ERROR

ROLLBACK
```

Debug cực kỳ dễ.

---

# 17. Unit of Work

Transaction chính là nền tảng.

Sau này ta sẽ có

```text
UnitOfWork

↓

StoryRepository

↓

ChapterRepository

↓

AuthorRepository
```

Tất cả Repository

dùng chung

một Transaction.

---

# 18. CLI Test

Trong app.py

```python
db.execute("""

CREATE TABLE IF NOT EXISTS test(

id INTEGER PRIMARY KEY,

name TEXT

)

""")
```

---

Test thành công

```python
with db.transaction():
    db.execute("INSERT INTO test(name) VALUES(?)", ("A",))

    db.execute("INSERT INTO test(name) VALUES(?)", ("B",))
```

↓

Database

```text
A

B
```

---

Test rollback

```python
try:
    with db.transaction():
        db.execute("INSERT INTO test(name) VALUES(?)", ("C",))

        raise Exception()

except:
    pass
```

Database

```text
A

B
```

Không có

```text
C
```

---

# 19. Cải tiến quan trọng

Phiên bản trên hoạt động, nhưng để đủ tốt cho framework thực tế, chúng ta nên chuẩn bị thêm:

## Sử dụng `BEGIN IMMEDIATE`

Thay vì:

```python
self.connection.execute("BEGIN")
```

có thể dùng:

```python
self.connection.execute("BEGIN IMMEDIATE")
```

Điều này lấy quyền ghi ngay từ đầu, giúp giảm lỗi `database is locked` khi crawler ghi dữ liệu.

## Không dùng cờ `in_transaction` riêng

Thư viện `sqlite3` đã có:

```python
self.connection.in_transaction
```

Nên ưu tiên sử dụng thuộc tính này thay vì tự quản lý một biến trạng thái.

## Transaction Context riêng

Thay vì đặt trực tiếp trong `SQLiteConnection`, về lâu dài có thể tạo:

```text
SQLiteConnection
        │
        ▼
TransactionContext
```

để mã nguồn rõ ràng và dễ mở rộng (ví dụ hỗ trợ Savepoint).

---

# Kiến trúc sau buổi 6

```text
Repository
      │
      ▼
SQLiteConnection
      │
      ├── execute()
      ├── fetchone()
      ├── fetchall()
      ├── transaction()
      ├── begin()
      ├── commit()
      └── rollback()
      │
      ▼
sqlite3
```

---

# Bài tập thực hành

## Bài 1

Bổ sung các phương thức:

* `begin()`
* `transaction()`

cho `SQLiteConnection`.

## Bài 2

Viết hai bài kiểm thử CLI:

1. Transaction thành công → dữ liệu được commit.
2. Transaction phát sinh ngoại lệ → dữ liệu được rollback.

## Bài 3

Thử tạo hai `with db.transaction():` lồng nhau và quan sát hành vi. Ghi lại lý do tại sao chúng ta chưa hỗ trợ nested transaction.

---

# Kết quả sau buổi 6

Đến thời điểm này, tầng truy cập dữ liệu đã có đầy đủ các thành phần cốt lõi:

* Quản lý nhiều file SQLite.
* Wrapper thống nhất cho `sqlite3`.
* Quản lý transaction theo chuẩn Python.
* Tự động commit/rollback.
* Nền tảng cho **Repository Pattern** và **Unit of Work**.

## Chuẩn bị cho Phần II

Từ buổi 7 trở đi, chúng ta sẽ chuyển sang **Model Layer**.

Thay vì tạo ngay `Story`, `Author`, `Chapter`, chúng ta sẽ thiết kế một **`BaseModel`** đủ mạnh để tất cả các model kế thừa. Mục tiêu là mỗi model:

* Có khả năng chuyển đổi giữa đối tượng Python và dữ liệu SQLite.
* Hỗ trợ kiểm tra dữ liệu (validation) cơ bản.
* Dễ mở rộng khi bổ sung trường mới.
* Hoạt động tốt với Repository mà không phụ thuộc vào SQLite trực tiếp.

Đó sẽ là nền móng cho toàn bộ tầng Model của framework.
