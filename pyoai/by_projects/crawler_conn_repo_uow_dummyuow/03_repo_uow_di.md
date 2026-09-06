# Buổi 3 — Repository + UoW + Dependency Injection

Hôm nay ta ghép 3 mảnh lại thành một kiến trúc hoàn chỉnh cho **app crawl truyện chữ**:

```text
CLI / GUI
    ↓
Application Service / Use Case
    ↓
Unit of Work
    ↓
Repository
    ↓
SQLite / File
```

Mục tiêu quan trọng nhất:

> **Use Case không biết implementation cụ thể là SQLite hay File.**

---

## 1. Vấn đề của Dependency Injection

Ví dụ viết thẳng:

```python
class SaveNovel:

    def execute(self, novel):
        uow = SQLiteUnitOfWork(...)
        
        with uow:
            uow.novels.add(novel)
```

Use Case bây giờ bị dính SQLite:

```text
SaveNovel
   ↓
SQLiteUnitOfWork
   ↓
SQLite
```

Sau này muốn test:

```text
SaveNovel
   ↓
FakeUnitOfWork
```

sẽ khó.

Hoặc muốn dùng:

```text
FileRepository
```

cũng khó.

---

# 2. Dependency Injection

Ta thay bằng:

```python
class SaveNovel:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, novel):
        with self.uow:
            self.uow.novels.add(novel)
```

Bây giờ `SaveNovel` không tạo dependency.

Nó **nhận dependency từ bên ngoài**.

Đây chính là:

> Dependency Injection.

---

# 3. Constructor Injection

Đây là dạng DI ta sẽ sử dụng nhiều nhất trong project:

```python
class SaveNovel:

    def __init__(self, uow):
        self.uow = uow
```

Bên ngoài:

```python
uow = SQLiteUnitOfWork(...)
use_case = SaveNovel(uow)
```

Hoặc:

```python
uow = FakeUnitOfWork(...)
use_case = SaveNovel(uow)
```

Hoặc:

```python
uow = DummyUnitOfWork(...)
use_case = SaveNovel(uow)
```

Use Case không thay đổi.

---

# 4. Interface cho UnitOfWork

Ta nên định nghĩa abstraction rõ ràng.

```python
from abc import ABC, abstractmethod


class UnitOfWork(ABC):

    novels: object
    chapters: object

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        ...

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...
```

Application chỉ phụ thuộc interface này.

---

# 5. Novel Repository Interface

Domain:

```python
from abc import ABC, abstractmethod


class NovelRepository(ABC):

    @abstractmethod
    def add(self, novel):
        ...

    @abstractmethod
    def get(self, novel_id):
        ...

    @abstractmethod
    def delete(self, novel_id):
        ...
```

Bây giờ:

```text
NovelRepository
       ▲
       │
 ┌─────┴─────────────┐
 │                   │
SQLiteNovelRepo   FileNovelRepo
```

---

# 6. SQLite implementation

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn

    def add(self, novel):

        self.conn.execute(
            """
            INSERT INTO novels
            (
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

    def get(self, novel_id):

        row = self.conn.execute(
            """
            SELECT *
            FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        ).fetchone()

        return row

    def delete(self, novel_id):

        self.conn.execute(
            """
            DELETE FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        )
```

Repository chỉ biết:

```python
self.conn
```

Nó không biết:

```text
UoW
Use Case
CLI
```

---

# 7. File implementation

Giả sử ta lưu:

```text
data/
└── novels/
    ├── 1.json
    ├── 2.json
    └── 3.json
```

```python
from pathlib import Path
import json


class FileNovelRepository:

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def add(self, novel):

        path = self.directory / f"{novel.id}.json"

        data = {
            "id": novel.id,
            "title": novel.title,
            "author": novel.author,
            "source": novel.source,
        }

        path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def get(self, novel_id):

        path = self.directory / f"{novel_id}.json"

        if not path.exists():
            return None

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def delete(self, novel_id):

        path = self.directory / f"{novel_id}.json"

        if path.exists():
            path.unlink()
```

Hai implementation hoàn toàn khác nhau:

```text
SQLiteNovelRepository
        ↓
SQL

FileNovelRepository
        ↓
JSON
```

nhưng cùng interface:

```text
NovelRepository
```

---

# 8. SQLite UoW

```python
class SQLiteUnitOfWork:

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def __enter__(self):

        self.conn = (
            self.connection_manager.connect()
        )

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
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

# 9. Dummy UoW

File repository không có transaction giống SQLite.

Ta tạo adapter đơn giản:

```python
class DummyUnitOfWork:

    def __init__(self, novels):
        self.novels = novels

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

Bây giờ Use Case không quan tâm backend.

---

# 10. Use Case

Đây là phần quan trọng nhất.

```python
class SaveNovel:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, novel):

        with self.uow:
            self.uow.novels.add(novel)
```

Dependency:

```text
SaveNovel
    │
    │ depends on
    ▼
UnitOfWork
```

Không phải:

```text
SaveNovel
    │
    ▼
SQLite
```

---

# 11. Composition Root

Vậy ai quyết định dùng SQLite?

**Không phải Use Case.**

Ta quyết định ở tầng ngoài cùng.

Ví dụ:

```python
def build_sqlite_app():

    connection_manager = (
        SQLiteConnectionManager(
            "novels.db"
        )
    )

    uow = SQLiteUnitOfWork(
        connection_manager
    )

    save_novel = SaveNovel(uow)

    return save_novel
```

Đây gọi là:

> **Composition Root**

Nó là nơi chúng ta "lắp ráp" application.

---

# 12. Flow thực tế

CLI:

```text
python -m novel_app save-novel ...
```

↓

```text
CLI
 │
 ▼
build_app()
 │
 ├── ConnectionManager
 │
 ├── SQLiteUoW
 │
 └── SaveNovel
        │
        ▼
      execute()
        │
        ▼
      UoW
        │
        ▼
    NovelRepository
        │
        ▼
      SQLite
```

---

# 13. Tại sao Composition Root rất quan trọng?

Nếu không có nó, dependency sẽ rải rác:

```text
UseCase
   ├── create SQLite
   ├── create Repository
   ├── create Logger
   ├── create HTTP client
   └── create Config
```

Sau này project sẽ rất khó quản lý.

Ta muốn:

```text
main.py
   │
   ├── Config
   ├── Logger
   ├── Database
   ├── UoW
   └── UseCases
```

Application bên dưới chỉ nhận dependency.

---

# 14. Test Use Case

Ta tạo Fake Repository:

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

Fake UoW:

```python
class FakeUnitOfWork:

    def __init__(self):

        self.novels = FakeNovelRepository()

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

Test:

```python
def test_save_novel():

    uow = FakeUnitOfWork()

    use_case = SaveNovel(uow)

    use_case.execute(novel)

    assert (
        uow.novels.get(novel.id)
        == novel
    )

    assert uow.committed is True
```

Không cần:

```text
SQLite
SQL
database file
```

---

# 15. Test exception

```python
def test_save_novel_rollback():

    uow = FakeUnitOfWork()

    class FailingSaveNovel:

        def __init__(self, uow):
            self.uow = uow

        def execute(self, novel):

            with self.uow:
                self.uow.novels.add(novel)

                raise RuntimeError(
                    "Crawler failed"
                )

    use_case = FailingSaveNovel(uow)

    try:
        use_case.execute(novel)
    except RuntimeError:
        pass

    assert uow.rolled_back is True
```

Ta đang kiểm tra:

```text
exception
    ↓
UoW
    ↓
rollback()
```

---

# 16. Dependency graph

Đây là hình bạn nên ghi nhớ:

```text
                 ┌──────────────┐
                 │     CLI      │
                 └──────┬───────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Composition Root│
               └────────┬────────┘
                        │
                 creates dependencies
                        │
                        ▼
               ┌─────────────────┐
               │    Use Case     │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │   UnitOfWork     │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │   Repository    │
               └────────┬────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           SQLite                File
```

Dependency direction:

```text
Infrastructure
      ↑
Application
      ↑
Domain
```

Infrastructure implement abstraction của Application/Domain.

---

# 17. Một điểm nâng cao: UoW không nhất thiết phải expose Repository implementation

Ta có:

```python
uow.novels
```

Nhưng Application chỉ nên biết:

```python
uow.novels.add()
uow.novels.get()
```

chứ không được làm:

```python
uow.novels.conn.execute(...)
```

Nếu làm vậy:

```text
Application
    ↓
SQLite implementation
```

và Dependency Inversion bị phá vỡ.

---

# 18. Kiến trúc dành cho app crawler của bạn

Tôi khuyên dùng:

```text
application/
│
├── unit_of_work.py
│
├── services/
│   ├── save_novel.py
│   ├── save_chapter.py
│   └── complete_crawl.py
│
└── ports/
    └── ...
```

Infrastructure:

```text
infrastructure/
│
├── database/
│   └── sqlite_connection.py
│
├── repositories/
│   ├── sqlite_novel.py
│   ├── sqlite_chapter.py
│   ├── sqlite_crawl_state.py
│   │
│   └── file_novel.py
│
└── uow/
    ├── sqlite.py
    └── dummy.py
```

Composition:

```text
bootstrap/
└── container.py
```

`container.py` sẽ làm:

```text
Config
  ↓
Logger
  ↓
ConnectionManager
  ↓
SQLiteUoW
  ↓
Use Cases
```

---

# 19. Điều đặc biệt quan trọng với crawler

Crawler thường có workflow:

```text
Fetch
  ↓
Parse
  ↓
Validate
  ↓
Save Novel
  ↓
Save Chapters
  ↓
Update CrawlState
```

Ta có thể gom phần persistence:

```python
with uow:

    uow.novels.add(novel)

    for chapter in chapters:
        uow.chapters.add(chapter)

    uow.crawl_states.mark_completed(
        novel.id
    )
```

Kết quả:

```text
                 Transaction
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
     Novel         Chapters       CrawlState
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                   COMMIT
```

Nếu database lỗi:

```text
Novel ✓
Chapter ✓
Chapter ✗
     ↓
ROLLBACK
```

Không rơi vào trạng thái:

```text
Novel saved
Chapter 1 saved
Chapter 2 saved
Chapter 3 missing
CrawlState = completed
```

Đây chính là giá trị thực tế của **Unit of Work** trong crawler.

---

## Bài tập Buổi 3

Hãy xây 3 implementation:

```text
SQLiteNovelRepository
FileNovelRepository
FakeNovelRepository
```

và 3 UoW:

```text
SQLiteUnitOfWork
DummyUnitOfWork
FakeUnitOfWork
```

Sau đó đảm bảo **một Use Case duy nhất**:

```python
SaveNovel(uow).execute(novel)
```

có thể chạy với cả:

```python
SaveNovel(SQLiteUnitOfWork(...))
```

và:

```python
SaveNovel(DummyUnitOfWork(...))
```

và:

```python
SaveNovel(FakeUnitOfWork(...))
```

### Buổi 4

Tiếp theo ta sẽ làm phần rất quan trọng cho kiến trúc SQLite của app này:

**`SQLiteConnectionManager` Deep Dive**

```text
Connection lifecycle
Connection ownership
PRAGMA
foreign_keys
WAL
busy_timeout
row_factory
isolation_level
thread safety
connection per UoW
connection pooling có cần hay không
```

Sau đó ta sẽ thiết kế một `SQLiteConnectionManager` **production-style** thay vì class `connect()` đơn giản ở Buổi 1.