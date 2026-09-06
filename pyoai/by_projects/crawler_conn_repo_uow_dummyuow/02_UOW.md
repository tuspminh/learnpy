# Buổi 2 — Unit of Work Deep Dive

Ở buổi trước ta đã xây được nền tảng:

```text
Application
    ↓
UnitOfWork
    ↓
Repository
    ↓
SQLiteConnectionManager
    ↓
sqlite3
```

Hôm nay ta đào sâu **Unit of Work**, đặc biệt là:

- Transaction boundary
- `__enter__()` / `__exit__()`
- nhiều Repository dùng chung một connection
- `commit()` / `rollback()`
- exception propagation
- Nested UoW
- Fake UoW để unit test

---

# 1. Unit of Work thực chất giải quyết vấn đề gì?

Giả sử crawler tải một truyện:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

Khi lưu database:

```python
with uow:
    uow.novels.add(novel)
    uow.chapters.add(chapter1)
    uow.chapters.add(chapter2)
    uow.chapters.add(chapter3)
```

Ta muốn:

```text
Tất cả thành công
       ↓
    COMMIT
```

hoặc:

```text
Một operation lỗi
       ↓
   ROLLBACK
       ↓
Không lưu gì
```

Đó chính là:

> **Unit of Work = một đơn vị công việc transactional.**

---

# 2. Transaction Boundary

Đây là khái niệm cực kỳ quan trọng.

Transaction boundary:

```text
┌───────────────────────────────┐
│         TRANSACTION           │
│                               │
│  save novel                   │
│  save chapter 1               │
│  save chapter 2               │
│  save chapter 3               │
│                               │
└───────────────────────────────┘
                │
                ▼
             COMMIT
```

Ta thường đặt boundary tại Application Service / Use Case:

```python
def execute(self, novel, chapters):

    with self.uow:
        self.uow.novels.add(novel)

        for chapter in chapters:
            self.uow.chapters.add(chapter)
```

**Không đặt transaction boundary bên trong Repository.**

Sai:

```python
class SQLiteNovelRepository:

    def add(self, novel):
        self.conn.execute(...)
        self.conn.commit()
```

Vì khi đó:

```text
Repository
   ↓
commit()
```

phá vỡ khả năng atomic transaction giữa nhiều repository.

---

# 3. Một UoW phải dùng chung connection

Đây là điểm quan trọng nhất trong thiết kế hôm nay.

Sai:

```python
class SQLiteNovelRepository:

    def __init__(self):
        self.conn = sqlite3.connect(...)
```

và:

```python
class SQLiteChapterRepository:

    def __init__(self):
        self.conn = sqlite3.connect(...)
```

Ta sẽ có:

```text
NovelRepository
     ↓
Connection A

ChapterRepository
     ↓
Connection B
```

Không tốt.

Ta muốn:

```text
                 UnitOfWork
                     │
                Connection
                 /       \
                /         \
               ▼           ▼
         NovelRepo     ChapterRepo
```

Tức là:

```text
NovelRepository ──┐
                  ├── SAME connection
ChapterRepository ┘
```

---

# 4. SQLiteUnitOfWork chuẩn hơn

Ta viết:

```python
class SQLiteUnitOfWork:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def __enter__(self):
        self.conn = self.connection_manager.connect()

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
```

Điểm quan trọng:

```python
self.conn
```

được truyền vào **tất cả repository**.

---

# 5. `__enter__()` hoạt động thế nào?

Khi:

```python
with uow:
    ...
```

Python gọi:

```python
uow.__enter__()
```

Ví dụ:

```python
def __enter__(self):

    self.conn = self.connection_manager.connect()

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
with uow as work:
```

thì:

```python
work
```

chính là object được trả về từ:

```python
__enter__()
```

Vì vậy ta có thể viết:

```python
with uow as work:
    work.novels.add(novel)
```

---

# 6. `__exit__()` có 3 arguments

Python gọi:

```python
__exit__(
    exc_type,
    exc_value,
    traceback
)
```

Ví dụ không có exception:

```python
with uow:
    uow.novels.add(novel)
```

thì:

```python
exc_type  = None
exc_value = None
traceback = None
```

Do đó:

```python
if exc_type is None:
    self.commit()
```

---

Nếu xảy ra:

```python
with uow:
    uow.novels.add(novel)

    raise ValueError("Something went wrong")
```

thì:

```text
exc_type
    ↓
ValueError

exc_value
    ↓
ValueError("Something went wrong")

traceback
    ↓
traceback object
```

Do đó:

```python
else:
    self.rollback()
```

---

# 7. Exception có bị nuốt không?

Đây là một chi tiết rất dễ sai.

Ví dụ:

```python
def __exit__(self, exc_type, exc_value, traceback):

    if exc_type:
        self.rollback()

    return True
```

`return True` nghĩa là:

> Exception đã được xử lý.

Python sẽ **không propagate exception ra ngoài**.

Ví dụ:

```python
try:
    with uow:
        raise ValueError("ERROR")
except ValueError:
    print("Không chạy")
```

Vì UoW đã nuốt exception.

---

## Thiết kế đúng

Ta thường:

```python
def __exit__(self, exc_type, exc_value, traceback):

    if exc_type is None:
        self.commit()
    else:
        self.rollback()

    return False
```

Hoặc đơn giản:

```python
def __exit__(self, exc_type, exc_value, traceback):

    try:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    finally:
        self.conn.close()

    return False
```

`False` nghĩa là:

> Tôi không xử lý exception. Hãy tiếp tục raise nó.

---

# 8. Thiết kế tốt hơn: luôn đóng connection

Ta nên dùng:

```python
def __exit__(self, exc_type, exc_value, traceback):

    try:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    finally:
        self.conn.close()

    return False
```

Luồng:

```text
             with uow
                 │
                 ▼
             operation
                 │
          ┌──────┴──────┐
          │             │
       success        error
          │             │
       commit        rollback
          │             │
          └──────┬──────┘
                 │
                 ▼
            close conn
                 │
                 ▼
        exception propagate
```

---

# 9. `commit()` có nên nằm trong `__exit__()`?

Có thể.

Nhưng một thiết kế linh hoạt hơn là:

```python
with uow:
    uow.novels.add(novel)
    uow.chapters.add(chapter)

    uow.commit()
```

Lúc này `__exit__()` chỉ rollback khi exception.

Ví dụ:

```python
class SQLiteUnitOfWork:

    def __exit__(self, exc_type, exc_value, traceback):

        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self.conn.close()

        return False
```

Application:

```python
with uow:
    uow.novels.add(novel)
    uow.chapters.add(chapter)

    uow.commit()
```

Ưu điểm:

```text
commit = explicit
```

Nhược điểm:

```text
developer có thể quên commit
```

Với app crawl của bạn, tôi thích **auto-commit khi không có exception** ở tầng Use Case đơn giản.

---

# 10. Nhiều Repository trong một UoW

Đây là kiến trúc mà app truyện của bạn sẽ cần:

```python
class SQLiteUnitOfWork:

    def __enter__(self):

        self.conn = self.connection_manager.connect()

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        self.crawl_states = SQLiteCrawlStateRepository(
            self.conn
        )

        return self
```

Bây giờ:

```python
with uow:

    uow.novels.add(novel)

    uow.chapters.add(chapter)

    uow.crawl_states.update(
        novel.id,
        status="completed",
    )
```

Tất cả cùng thuộc:

```text
ONE transaction
```

---

# 11. Đây chính là lợi ích lớn của UoW

Không có UoW:

```text
save novel
    ↓
commit

save chapter
    ↓
commit

save crawl state
    ↓
commit
```

Có UoW:

```text
              UoW
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
    Novel    Chapter   State
      │        │        │
      └────────┼────────┘
               ▼
            COMMIT
```

---

# 12. FakeUnitOfWork

Bây giờ đến phần cực kỳ hữu ích cho testing.

Ta không muốn unit test phải:

```text
test
 ↓
SQLite
 ↓
database file
 ↓
SQL
```

Unit test Use Case chỉ cần kiểm tra:

```text
Use Case
   ↓
có gọi repository đúng không?
   ↓
có commit không?
```

Ta tạo:

```python
class FakeUnitOfWork:

    def __init__(self, novels):
        self.novels = novels

        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
```

---

# 13. Fake Repository

Ta cần fake repository:

```python
class FakeNovelRepository:

    def __init__(self):
        self.items = []

    def add(self, novel):
        self.items.append(novel)

    def get(self, novel_id):
        for novel in self.items:
            if novel.id == novel_id:
                return novel

        return None
```

Bây giờ:

```python
repo = FakeNovelRepository()

uow = FakeUnitOfWork(repo)

use_case = SaveNovel(uow)
```

Test:

```python
use_case.execute(novel)

assert repo.get(novel.id) == novel
assert uow.committed is True
```

Không cần SQLite.

---

# 14. Test rollback

Ta tạo Use Case cố tình lỗi:

```python
class SaveNovelAndFail:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, novel):

        with self.uow:
            self.uow.novels.add(novel)

            raise RuntimeError("Crawler error")
```

Test:

```python
repo = FakeNovelRepository()

uow = FakeUnitOfWork(repo)

use_case = SaveNovelAndFail(uow)

try:
    use_case.execute(novel)
except RuntimeError:
    pass

assert uow.rolled_back is True
```

Điểm quan trọng:

```text
exception
    ↓
__exit__()
    ↓
rollback()
    ↓
return False
    ↓
exception tiếp tục propagate
```

---

# 15. Nhưng FakeRepository trên chưa rollback thật

Đây là một bài học kiến trúc rất hay.

Fake:

```python
repo.items.append(novel)
```

sau rollback:

```text
items vẫn có novel
```

Trong SQLite:

```text
INSERT
 ↓
ROLLBACK
 ↓
novel biến mất
```

Trong Fake:

```text
INSERT
 ↓
ROLLBACK
 ↓
novel vẫn còn
```

Vậy Fake UoW hiện tại chỉ test được:

```text
rollback() được gọi
```

chứ chưa test được:

```text
transaction semantics
```

Đây là điều **không nên nhầm lẫn**.

---

# 16. Fake UoW nâng cao

Ta có thể snapshot state:

```python
class FakeUnitOfWork:

    def __init__(self, novels):
        self.novels = novels

        self.committed = False
        self.rolled_back = False
        self._snapshot = None

    def __enter__(self):

        self._snapshot = list(
            self.novels.items
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.novels.items[:] = self._snapshot
        self.rolled_back = True
```

Bây giờ:

```text
before
   │
   ▼
snapshot
   │
   ▼
operations
   │
   ├── success → commit
   │
   └── error
         ↓
      rollback
         ↓
    restore snapshot
```

---

# 17. Nested Unit of Work

Một vấn đề khó hơn:

```python
with uow:
    service_a()

    with uow:
        service_b()
```

Đây là **nested transaction**.

SQLite không đơn giản coi mỗi:

```python
with uow:
```

là transaction độc lập.

Nếu `service_b()` rollback:

```text
Outer transaction
       │
       ├── service_a
       │
       └── Inner transaction
                │
                └── rollback
```

Ta phải quyết định semantics.

Có thể dùng:

```text
SAVEPOINT
```

của SQLite.

Ví dụ:

```sql
SAVEPOINT nested_uow;
```

và:

```sql
ROLLBACK TO SAVEPOINT nested_uow;
```

Đây là chủ đề nâng cao và rất đáng học sau khi hiểu UoW cơ bản.

---

# 18. Một nguyên tắc rất quan trọng

**Không để Repository tạo connection.**

Sai:

```python
class SQLiteNovelRepository:

    def add(self, novel):

        conn = sqlite3.connect(...)

        conn.execute(...)
        conn.commit()
```

Đúng:

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn

    def add(self, novel):

        self.conn.execute(...)
```

Connection ownership thuộc:

```text
UnitOfWork
```

Transaction ownership cũng thuộc:

```text
UnitOfWork
```

Repository chỉ chịu trách nhiệm:

```text
Persistence operations
```

---

# 19. Kiến trúc hoàn chỉnh

Sau buổi này, ta có:

```text
                   USE CASE
                      │
                      ▼
               ┌──────────────┐
               │ UnitOfWork   │
               └──────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Novels      Chapters    CrawlState
       Repository  Repository  Repository
          │           │           │
          └───────────┼───────────┘
                      │
                SAME CONNECTION
                      │
                      ▼
          SQLiteConnectionManager
                      │
                      ▼
                   SQLite
```

Còn testing:

```text
                   USE CASE
                      │
                      ▼
                FakeUnitOfWork
                      │
             ┌────────┴────────┐
             ▼                 ▼
       FakeNovelRepo      FakeChapterRepo
```

Và File:

```text
                   USE CASE
                      │
                      ▼
              DummyUnitOfWork
                      │
                      ▼
             FileNovelRepository
                      │
                      ▼
                   JSON
```

---

# 20. Bài tập Buổi 2

Hãy tự xây project nhỏ:

```text
novel_app/
├── domain/
│   └── novel.py
│
├── application/
│   ├── unit_of_work.py
│   └── save_novel.py
│
├── infrastructure/
│   ├── sqlite_connection.py
│   ├── sqlite_novel_repository.py
│   └── sqlite_uow.py
│
└── tests/
    ├── fake_repository.py
    └── test_save_novel.py
```

Test được 3 case:

### Case 1 — Success

```text
UseCase
   ↓
add novel
   ↓
commit
```

### Case 2 — Exception

```text
UseCase
   ↓
add novel
   ↓
exception
   ↓
rollback
```

### Case 3 — Multiple repositories

```text
uow.novels.add()
uow.chapters.add()
uow.crawl_states.update()
        ↓
     COMMIT
```

---

## Kiến thức cần nhớ

Nếu chỉ nhớ **5 điều** sau buổi này:

```text
1. Connection Manager tạo/configure connection.

2. Unit of Work sở hữu connection.

3. Unit of Work sở hữu transaction boundary.

4. Các Repository trong cùng UoW phải dùng SAME connection.

5. Repository không commit/rollback.
```

Với app crawler của bạn, đây là nền móng rất quan trọng trước khi chúng ta chuyển sang **`Repository + UoW + Dependency Injection + CLI`**.