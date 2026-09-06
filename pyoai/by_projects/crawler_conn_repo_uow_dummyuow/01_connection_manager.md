Được. Với app **crawl truyện chữ** của bạn, ta nên thiết kế theo hướng:

```text
Application / Use Case
        │
        ▼
    Unit of Work
        │
        ├── NovelRepository
        ├── ChapterRepository
        └── ...
        │
        ▼
 SQLiteConnectionManager
        │
        ▼
      sqlite3
```

Và song song đó, để test hoặc dùng `FileRepository`:

```text
Application
    │
    ▼
DummyUnitOfWork
    │
    └── FileNovelRepository
```

## Buổi học này

Ta sẽ đi theo 6 bước:

1. Vì sao cần `ConnectionManager`
2. Thiết kế `SQLiteConnectionManager`
3. Thiết kế `NovelRepository`
4. Thiết kế `SQLiteUnitOfWork`
5. Transaction: `commit / rollback`
6. `DummyUnitOfWork` cho `FileRepository`

---

# 1. Vì sao không mở SQLite connection trực tiếp trong Repository?

Ví dụ cách đơn giản:

```python
class SQLiteNovelRepository:

    def save(self, novel):
        conn = sqlite3.connect("novels.db")

        conn.execute(...)
        conn.commit()

        conn.close()
```

Ban đầu chạy được.

Nhưng khi Use Case cần:

```text
save novel
save chapter
save crawl state
```

ta có vấn đề.

Nếu mỗi repository tự mở connection:

```text
NovelRepository
    ↓
connection A
    ↓
commit

ChapterRepository
    ↓
connection B
    ↓
commit
```

Có thể xảy ra:

```text
save novel       ✓
save chapter     ✗
```

Novel đã commit nhưng Chapter thất bại.

Ta muốn:

```text
BEGIN
   │
   ├── save novel
   ├── save chapter
   └── save crawl state
        │
        ▼
     COMMIT
```

hoặc nếu bất kỳ thao tác nào lỗi:

```text
BEGIN
   │
   ├── save novel
   ├── save chapter
   └── ERROR
        │
        ▼
     ROLLBACK
```

Đây chính là lý do **Unit of Work** xuất hiện.

---

# 2. Connection Manager

Trước tiên tạo infrastructure:

```text
infrastructure/
    database/
        connection.py
```

Ta muốn API rất đơn giản:

```python
connection = connection_manager.connect()
```

Ví dụ:

```python
import sqlite3
from pathlib import Path


class SQLiteConnectionManager:

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row

        return conn
```

Sử dụng:

```python
manager = SQLiteConnectionManager("novels.db")

conn = manager.connect()

rows = conn.execute(
    "SELECT * FROM novels"
).fetchall()

conn.close()
```

---

# 3. Tại sao dùng `sqlite3.Row`?

Nếu không:

```python
row = cursor.fetchone()

print(row[0])
print(row[1])
```

Khá khó đọc.

Với:

```python
conn.row_factory = sqlite3.Row
```

ta có:

```python
row["id"]
row["title"]
row["author"]
```

Ví dụ database:

```text
novels
-------------------------
id
title
author
source
```

Ta có:

```python
row = conn.execute(
    """
    SELECT id, title, author, source
    FROM novels
    WHERE id = ?
    """,
    (novel_id,),
).fetchone()
```

Sau đó:

```python
print(row["title"])
```

---

# 4. Connection Manager không nên quản lý transaction

Đây là một nguyên tắc quan trọng.

Không nên:

```python
class SQLiteConnectionManager:

    def save(...):
        ...
        conn.commit()
```

Connection Manager chỉ chịu trách nhiệm:

```text
Database connection
        │
        ├── open
        └── configure
```

Còn:

```text
transaction
commit
rollback
```

thuộc về **Unit of Work**.

Kiến trúc:

```text
ConnectionManager
       │
       │ tạo connection
       ▼
     UoW
       │
       ├── transaction
       ├── commit
       └── rollback
```

---

# 5. Domain Repository Interface

Giả sử Domain có:

```python
from abc import ABC, abstractmethod


class NovelRepository(ABC):

    @abstractmethod
    def add(self, novel) -> None:
        ...

    @abstractmethod
    def get(self, novel_id: int):
        ...

    @abstractmethod
    def delete(self, novel_id: int) -> None:
        ...
```

Điểm quan trọng:

**Domain không biết SQLite.**

Không có:

```python
import sqlite3
```

trong Domain.

---

# 6. SQLite Novel Repository

Infrastructure:

```text
infrastructure/
    repositories/
        sqlite_novel_repository.py
```

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn

    def add(self, novel) -> None:
        self.conn.execute(
            """
            INSERT INTO novels (
                id,
                title,
                author,
                source
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                novel.id,
                novel.title,
                novel.author,
                novel.source,
            ),
        )

    def get(self, novel_id: int):
        row = self.conn.execute(
            """
            SELECT id, title, author, source
            FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        ).fetchone()

        if row is None:
            return None

        return row

    def delete(self, novel_id: int) -> None:
        self.conn.execute(
            """
            DELETE FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        )
```

Điểm cực kỳ quan trọng:

Repository **không gọi**:

```python
conn.commit()
```

Repository chỉ:

```python
conn.execute(...)
```

Transaction do UoW quản lý.

---

# 7. Unit of Work

Ta định nghĩa interface:

```python
from abc import ABC, abstractmethod


class UnitOfWork(ABC):

    novels: NovelRepository

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        ...

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...
```

Đây là abstraction mà Application Layer sử dụng.

---

# 8. SQLiteUnitOfWork

Bây giờ kết hợp:

```text
SQLiteConnectionManager
          │
          ▼
 SQLiteUnitOfWork
          │
          ├── SQLiteNovelRepository
          ├── SQLiteChapterRepository
          └── ...
```

Code:

```python
class SQLiteUnitOfWork:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def __enter__(self):
        self.conn = self.connection_manager.connect()

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
```

Bây giờ Application có thể viết:

```python
with uow:
    uow.novels.add(novel)
```

---

# 9. Transaction thật sự hoạt động như thế nào?

Ví dụ:

```python
with uow:
    uow.novels.add(novel1)
    uow.novels.add(novel2)
    uow.novels.add(novel3)
```

Luồng:

```text
with uow
   │
   ▼
__enter__()
   │
   ▼
open connection
   │
   ▼
NovelRepository(conn)
   │
   ├── INSERT novel1
   ├── INSERT novel2
   └── INSERT novel3
   │
   ▼
__exit__()
   │
   ▼
commit()
```

Nếu có exception:

```python
with uow:
    uow.novels.add(novel1)
    uow.novels.add(novel2)

    raise RuntimeError("Crawler error")
```

thì:

```text
INSERT novel1
       │
INSERT novel2
       │
ERROR
       │
       ▼
ROLLBACK
```

Database trở về trạng thái trước transaction.

---

# 10. Cách viết Use Case

Đây mới là phần quan trọng.

Ví dụ:

```python
class SaveNovel:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, novel):
        with self.uow:
            self.uow.novels.add(novel)
```

Application không cần biết:

```text
SQLite
sqlite3
connection
commit
rollback
```

Nó chỉ biết:

```python
self.uow.novels.add(novel)
```

---

# 11. Nhưng FileRepository thì sao?

Đây là tình huống rất hay trong app của bạn.

Bạn có thể có:

```text
SQLiteNovelRepository
```

và:

```text
FileNovelRepository
```

Ví dụ:

```text
data/
    novels/
        novel_001.json
        novel_002.json
```

File repository:

```python
class FileNovelRepository:

    def __init__(self, directory):
        self.directory = Path(directory)

    def add(self, novel):
        path = self.directory / f"{novel.id}.json"

        path.write_text(
            novel.to_json(),
            encoding="utf-8",
        )

    def get(self, novel_id):
        ...
```

Nhưng File không có:

```python
connection.commit()
connection.rollback()
```

Vậy Application có thể dùng UoW như thế nào?

---

# 12. DummyUnitOfWork

Ta tạo:

```python
class DummyUnitOfWork:

    def __init__(self, novel_repository):
        self.novels = novel_repository

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def commit(self):
        pass

    def rollback(self):
        pass
```

Sử dụng:

```python
repo = FileNovelRepository("data/novels")

uow = DummyUnitOfWork(repo)

use_case = SaveNovel(uow)

use_case.execute(novel)
```

Application vẫn giữ nguyên:

```python
with self.uow:
    self.uow.novels.add(novel)
```

---

# 13. Đây chính là Dependency Inversion

Ta có:

```text
              Application
                   │
                   ▼
             UnitOfWork
                   ▲
            ┌──────┴──────┐
            │             │
     SQLiteUnitOfWork  DummyUnitOfWork
            │             │
            ▼             ▼
        SQLite          File
```

Application không phụ thuộc:

```text
SQLite
```

và cũng không phụ thuộc:

```text
File
```

Nó phụ thuộc abstraction:

```python
UnitOfWork
```

Đây chính là **DIP + Repository Pattern + Unit of Work** phối hợp với nhau.

---

# 14. Nhưng Dummy UoW có một vấn đề

Code:

```python
def commit(self):
    pass

def rollback(self):
    pass
```

không thật sự rollback được File.

Ví dụ:

```python
with uow:
    uow.novels.add(novel)

    raise RuntimeError()
```

File có thể đã được ghi:

```text
novel_001.json
```

Nhưng:

```python
rollback()
```

không thể tự động khôi phục.

Điều này cho thấy một điểm kiến trúc quan trọng:

> **Unit of Work không phải lúc nào cũng có cùng mức transaction semantics ở mọi infrastructure.**

SQLite có:

```text
atomic transaction
```

File repository có thể chỉ có:

```text
best-effort transaction
```

hoặc ta phải xây một cơ chế transaction riêng cho filesystem.

---

# 15. Kiến trúc cuối cùng cho Novel App

Tôi đề xuất cấu trúc:

```text
src/
└── novel_app/
    │
    ├── domain/
    │   ├── entities/
    │   │   └── novel.py
    │   │
    │   └── repositories/
    │       └── novel_repository.py
    │
    ├── application/
    │   ├── unit_of_work.py
    │   │
    │   └── use_cases/
    │       └── save_novel.py
    │
    └── infrastructure/
        │
        ├── database/
        │   └── sqlite_connection.py
        │
        ├── repositories/
        │   ├── sqlite_novel_repository.py
        │   └── file_novel_repository.py
        │
        └── unit_of_work/
            ├── sqlite_uow.py
            └── dummy_uow.py
```

Dependency:

```text
                 DOMAIN
                   ▲
                   │
              APPLICATION
                   ▲
                   │
             INFRASTRUCTURE
```

Cụ thể:

```text
Domain
  │
  └── NovelRepository

Application
  │
  └── UnitOfWork
          │
          └── NovelRepository

Infrastructure
  │
  ├── SQLiteNovelRepository
  ├── FileNovelRepository
  │
  ├── SQLiteConnectionManager
  │
  ├── SQLiteUnitOfWork
  └── DummyUnitOfWork
```

## Bài tập của Buổi này

Hãy tự implement 4 class sau:

```python
SQLiteConnectionManager
SQLiteNovelRepository
SQLiteUnitOfWork
DummyUnitOfWork
```

với flow:

```python
use_case = SaveNovel(uow)

use_case.execute(novel)
```

và chạy được cả:

```python
sqlite_uow = SQLiteUnitOfWork(...)
```

lẫn:

```python
dummy_uow = DummyUnitOfWork(...)
```

**Buổi tiếp theo rất đáng học:** chúng ta sẽ làm **Unit of Work Deep Dive**, đặc biệt là `__enter__`, `__exit__`, transaction boundary, nested UoW, nhiều repository dùng chung một connection, và test `commit/rollback` bằng `FakeUnitOfWork`.