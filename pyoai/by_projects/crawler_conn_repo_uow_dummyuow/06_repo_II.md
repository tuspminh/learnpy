# Buổi 6 — NovelRepository + ChapterRepository + Aggregate + Transaction

Hôm nay chúng ta chuyển từ **Repository đơn lẻ** sang một vấn đề rất quan trọng trong app crawl truyện:

> **Một Novel có rất nhiều Chapter, và việc lưu Novel + Chapter phải được thực hiện một cách nhất quán.**

Đây chính là nơi **Repository + Unit of Work + Aggregate + Transaction** bắt đầu kết hợp với nhau.

---

# 1. Bài toán thực tế

Giả sử crawler lấy được:

```text
Novel
 ├── title = "Đấu Phá Thương Khung"
 ├── author = "Thiên Tằm Thổ Đậu"
 │
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── ...
 └── Chapter 100
```

Crawler muốn lưu:

```text
Novel
   ↓
Chapters
   ↓
CrawlState
```

Nếu lưu thành công Novel nhưng Chapter bị lỗi:

```text
Novel INSERT       ✓
Chapter 1 INSERT   ✓
Chapter 2 INSERT   ✓
Chapter 3 INSERT   ✗
```

Database sẽ trở thành:

```text
Novel tồn tại
Chapter 1 tồn tại
Chapter 2 tồn tại
Chapter 3 mất
```

Đây là trạng thái không mong muốn.

Ta muốn:

```text
BEGIN

INSERT Novel
INSERT Chapter 1
INSERT Chapter 2
INSERT Chapter 3
...

COMMIT
```

hoặc:

```text
BEGIN

INSERT Novel
INSERT Chapter 1
INSERT Chapter 2
INSERT Chapter 3
✗ ERROR

ROLLBACK
```

Kết quả:

```text
Không có gì được lưu
```

Đây chính là lý do chúng ta cần **Unit of Work**.

---

# 2. Kiến trúc hôm nay

Ta sẽ có:

```text
                    Application
                         │
                         ▼
                 SaveNovelWithChapters
                         │
                         ▼
                    UnitOfWork
                  ┌──────┼──────┐
                  ▼      ▼      ▼
               novels chapters crawl_state
                  │      │
                  └──┬───┘
                     │
                     ▼
                SQLite Connection
                     │
                     ▼
                   SQLite
```

Quan trọng:

> `NovelRepository` và `ChapterRepository` phải dùng **cùng một connection** trong cùng một UoW.

---

# 3. Thiết kế database

Trước tiên:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,

    UNIQUE(source, source_id)
);
```

Chapter:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE(novel_id, chapter_number)
);
```

Điểm rất quan trọng:

```sql
UNIQUE(source, source_id)
```

giúp xác định:

> Novel nào trên một website là novel nào.

Và:

```sql
UNIQUE(novel_id, chapter_number)
```

giúp đảm bảo:

> Một novel không thể có hai Chapter 10.

---

# 4. Domain Model

## Novel

```python
from dataclasses import dataclass


@dataclass
class Novel:
    id: int | None
    source: str
    source_id: str
    title: str
    author: str | None
```

---

## Chapter

```python
from dataclasses import dataclass


@dataclass
class Chapter:
    id: int | None
    novel_id: int
    chapter_number: int
    title: str
    content: str
```

---

# 5. NovelRepository

Interface:

```python
from abc import ABC, abstractmethod


class NovelRepository(ABC):

    @abstractmethod
    def add(self, novel: Novel) -> int:
        ...

    @abstractmethod
    def get(self, novel_id: int) -> Novel | None:
        ...

    @abstractmethod
    def get_by_source_id(
        self,
        source: str,
        source_id: str,
    ) -> Novel | None:
        ...
```

Ta có thêm:

```python
get_by_source_id()
```

vì crawler thường không tìm Novel bằng database ID.

Crawler biết:

```text
source = "site_a"
source_id = "12345"
```

---

# 6. ChapterRepository

Interface:

```python
class ChapterRepository(ABC):

    @abstractmethod
    def add(self, chapter: Chapter) -> int:
        ...

    @abstractmethod
    def get(
        self,
        novel_id: int,
        chapter_number: int,
    ) -> Chapter | None:
        ...

    @abstractmethod
    def upsert(self, chapter: Chapter) -> int:
        ...

    @abstractmethod
    def add_many(
        self,
        chapters: list[Chapter],
    ) -> None:
        ...

    @abstractmethod
    def list_by_novel(
        self,
        novel_id: int,
    ) -> list[Chapter]:
        ...
```

Ở đây có một method rất đáng chú ý:

```python
upsert()
```

và:

```python
add_many()
```

Hai method này cực kỳ hữu ích cho crawler.

---

# 7. SQLiteNovelRepository

Repository không tạo connection.

Nó nhận connection từ bên ngoài:

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn
```

---

## add()

```python
def add(self, novel: Novel) -> int:
    cursor = self.conn.execute(
        """
        INSERT INTO novels (
            source,
            source_id,
            title,
            author
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            novel.source,
            novel.source_id,
            novel.title,
            novel.author,
        ),
    )

    return cursor.lastrowid
```

Chú ý:

```python
self.conn.execute(...)
```

nhưng:

```python
self.conn.commit()
```

**không xuất hiện.**

Vì commit thuộc về UoW.

---

# 8. get_by_source_id()

```python
def get_by_source_id(
    self,
    source: str,
    source_id: str,
) -> Novel | None:

    row = self.conn.execute(
        """
        SELECT
            id,
            source,
            source_id,
            title,
            author
        FROM novels
        WHERE source = ?
          AND source_id = ?
        """,
        (source, source_id),
    ).fetchone()

    if row is None:
        return None

    return Novel(
        id=row["id"],
        source=row["source"],
        source_id=row["source_id"],
        title=row["title"],
        author=row["author"],
    )
```

---

# 9. ChapterRepository implementation

```python
class SQLiteChapterRepository:

    def __init__(self, conn):
        self.conn = conn
```

---

## add()

```python
def add(self, chapter: Chapter) -> int:

    cursor = self.conn.execute(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            chapter.novel_id,
            chapter.chapter_number,
            chapter.title,
            chapter.content,
        ),
    )

    return cursor.lastrowid
```

---

# 10. `add_many()` — cực kỳ quan trọng

Crawler thường không crawl một chapter.

Ví dụ:

```text
Chapter 1
Chapter 2
Chapter 3
...
Chapter 100
```

Không nên:

```python
for chapter in chapters:
    repository.add(chapter)
```

nếu repository cần tối ưu bulk operation.

Ta có thể dùng:

```python
def add_many(
    self,
    chapters: list[Chapter],
) -> None:

    self.conn.executemany(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                chapter.novel_id,
                chapter.chapter_number,
                chapter.title,
                chapter.content,
            )
            for chapter in chapters
        ],
    )
```

Điểm quan trọng:

```text
Repository
    ↓
executemany()
    ↓
SQLite
```

thay vì:

```text
Python loop
    ↓
INSERT
    ↓
INSERT
    ↓
INSERT
    ↓
...
```

---

# 11. UPSERT Chapter

Đây là một trong những phần quan trọng nhất đối với crawler.

Giả sử crawler chạy lần đầu:

```text
Chapter 1
Chapter 2
Chapter 3
```

Sau đó crawl lại.

Nếu chỉ:

```sql
INSERT
```

thì:

```text
Chapter 1 → duplicate
Chapter 2 → duplicate
Chapter 3 → duplicate
```

Nhưng database đã có:

```sql
UNIQUE(novel_id, chapter_number)
```

nên INSERT sẽ lỗi.

Ta dùng:

```sql
INSERT INTO chapters (
    novel_id,
    chapter_number,
    title,
    content
)
VALUES (?, ?, ?, ?)

ON CONFLICT(novel_id, chapter_number)
DO UPDATE SET
    title = excluded.title,
    content = excluded.content;
```

---

# 12. `upsert()`

```python
def upsert(self, chapter: Chapter) -> None:

    self.conn.execute(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title,
            content
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(novel_id, chapter_number)
        DO UPDATE SET
            title = excluded.title,
            content = excluded.content
        """,
        (
            chapter.novel_id,
            chapter.chapter_number,
            chapter.title,
            chapter.content,
        ),
    )
```

Bây giờ crawler có thể chạy:

```text
crawl()
crawl()
crawl()
crawl()
```

mà không tạo duplicate.

Đây gọi là:

# Idempotent Operation

---

# 13. Idempotent là gì?

Một operation gọi nhiều lần nhưng kết quả cuối cùng tương đương gọi một lần.

Ví dụ:

```python
save_chapter(chapter)
```

gọi:

```text
1 lần
```

database:

```text
Chapter 10
```

Gọi:

```text
10 lần
```

database vẫn:

```text
Chapter 10
```

chứ không phải:

```text
Chapter 10
Chapter 10
Chapter 10
...
```

Đây là đặc tính cực kỳ quan trọng trong crawler.

Vì crawler thực tế có thể:

```text
retry
resume
restart
crawl lại
download lại
```

---

# 14. UoW chứa nhiều Repository

Đây là điểm quan trọng.

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
```

Ta có:

```text
UoW
 │
 ├── conn
 │
 ├── novels
 │      └── same conn
 │
 └── chapters
        └── same conn
```

Không phải:

```text
NovelRepository → connection A

ChapterRepository → connection B
```

---

# 15. Vì sao phải cùng connection?

Giả sử:

```python
with uow:
    novel_id = uow.novels.add(novel)

    uow.chapters.add_many(chapters)
```

Ta muốn:

```text
BEGIN
  Novel INSERT
  Chapter INSERT
COMMIT
```

Tất cả phải thuộc **cùng transaction**.

Nếu:

```text
Novel → Connection A
Chapter → Connection B
```

thì transaction không còn là một transaction duy nhất.

Đây là lý do:

> **UoW là nơi kết hợp nhiều Repository thành một transaction boundary.**

---

# 16. UoW hoàn chỉnh

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

# 17. Use Case

Bây giờ ta có thể viết:

```python
class SaveNovelWithChapters:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        novel: Novel,
        chapters: list[Chapter],
    ):

        with self.uow:

            novel_id = self.uow.novels.add(
                novel
            )

            for chapter in chapters:
                chapter.novel_id = novel_id

            self.uow.chapters.add_many(
                chapters
            )
```

Flow:

```text
SaveNovelWithChapters
        │
        ▼
     UoW
        │
        ├── NovelRepository
        │
        └── ChapterRepository
                │
                ▼
             SQLite
```

---

# 18. Nhưng có một vấn đề

Đoạn này:

```python
novel_id = self.uow.novels.add(novel)
```

chỉ phù hợp khi Novel chưa tồn tại.

Crawler thực tế thường gặp:

```text
Novel đã tồn tại
```

Ví dụ:

```text
source = "site_a"
source_id = "12345"
```

Crawler chạy lại.

Ta cần:

```text
get existing novel
        │
        ├── tồn tại → update
        │
        └── chưa tồn tại → insert
```

---

# 19. Đây chính là Repository + UPSERT

Ta có thể thêm:

```python
def upsert(self, novel: Novel) -> int:
    ...
```

SQL:

```sql
INSERT INTO novels (
    source,
    source_id,
    title,
    author
)
VALUES (?, ?, ?, ?)

ON CONFLICT(source, source_id)
DO UPDATE SET
    title = excluded.title,
    author = excluded.author
RETURNING id;
```

Với SQLite hiện đại, `RETURNING` rất tiện.

---

# 20. Novel UPSERT

```python
def upsert(self, novel: Novel) -> int:

    row = self.conn.execute(
        """
        INSERT INTO novels (
            source,
            source_id,
            title,
            author
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(source, source_id)
        DO UPDATE SET
            title = excluded.title,
            author = excluded.author

        RETURNING id
        """,
        (
            novel.source,
            novel.source_id,
            novel.title,
            novel.author,
        ),
    ).fetchone()

    return row["id"]
```

Bây giờ Use Case trở nên đơn giản:

```python
class SaveNovelWithChapters:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        novel: Novel,
        chapters: list[Chapter],
    ):

        with self.uow:

            novel_id = self.uow.novels.upsert(
                novel
            )

            for chapter in chapters:
                chapter.novel_id = novel_id

            self.uow.chapters.add_many(
                chapters
            )
```

---

# 21. Nhưng `add_many()` chưa idempotent

Nếu:

```python
add_many(chapters)
```

thì crawl lại sẽ lỗi:

```text
UNIQUE constraint failed
```

Ta cần:

```python
upsert_many()
```

SQL:

```sql
INSERT INTO chapters (
    novel_id,
    chapter_number,
    title,
    content
)
VALUES (?, ?, ?, ?)

ON CONFLICT(novel_id, chapter_number)
DO UPDATE SET
    title = excluded.title,
    content = excluded.content
```

---

# 22. `upsert_many()`

```python
def upsert_many(
    self,
    chapters: list[Chapter],
) -> None:

    self.conn.executemany(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title,
            content
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(novel_id, chapter_number)
        DO UPDATE SET
            title = excluded.title,
            content = excluded.content
        """,
        [
            (
                chapter.novel_id,
                chapter.chapter_number,
                chapter.title,
                chapter.content,
            )
            for chapter in chapters
        ],
    )
```

Bây giờ:

```text
Crawler
   │
   ▼
upsert Novel
   │
   ▼
upsert Chapters
```

hoàn toàn có thể chạy lại.

---

# 23. Aggregate là gì?

Đây là phần DDD quan trọng.

Ta có:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 └── Chapter ...
```

Có thể coi:

```text
Novel
```

là **Aggregate Root**.

```text
          Novel
        Aggregate Root
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
   Chapter Chapter Chapter
```

Trong cách thiết kế này:

> Novel là entry point để thao tác với các Chapter thuộc Novel.

---

# 24. Nhưng Repository có nên là `NovelRepository` hay `ChapterRepository`?

Đây là câu hỏi thiết kế rất hay.

Có hai hướng.

### Cách A

```text
NovelRepository
ChapterRepository
```

Phù hợp khi Chapter có lifecycle độc lập và crawler cần thao tác trực tiếp với Chapter.

### Cách B

```text
NovelRepository
```

và Novel aggregate chứa:

```python
novel.chapters
```

Repository lưu cả aggregate.

Ví dụ:

```python
novel = Novel(
    ...
    chapters=[...]
)
```

rồi:

```python
novel_repository.save(novel)
```

Đây là hướng DDD thuần aggregate hơn.

---

# 25. Với app crawler của chúng ta

Ở giai đoạn hiện tại, tôi khuyên dùng:

```text
NovelRepository
ChapterRepository
```

và:

```text
UnitOfWork
    ├── novels
    └── chapters
```

vì crawler có nhu cầu:

```text
crawl 1 novel
crawl 1 chapter
resume chapter 500
update chapter
bulk save chapters
```

Nếu ép mọi thứ qua:

```text
NovelRepository.save(novel)
```

sẽ dễ làm Repository trở nên quá lớn.

---

# 26. Transaction boundary

Một crawler operation có thể là:

```text
BEGIN
 │
 ├── UPSERT novel
 │
 ├── UPSERT chapters
 │
 ├── UPDATE crawl_state
 │
 └── COMMIT
```

Nếu lỗi:

```text
BEGIN
 │
 ├── UPSERT novel ✓
 │
 ├── Chapter 1 ✓
 │
 ├── Chapter 2 ✓
 │
 ├── Chapter 3 ✗
 │
 ▼
ROLLBACK
```

Database quay lại:

```text
trước transaction
```

Đây chính là sức mạnh của UoW.

---

# 27. Một ví dụ crawler thực tế

Crawler:

```python
novel = Novel(
    id=None,
    source="site_a",
    source_id="123",
    title="Novel A",
    author="Author A",
)

chapters = [
    Chapter(
        id=None,
        novel_id=0,
        chapter_number=1,
        title="Chapter 1",
        content="...",
    ),
    Chapter(
        id=None,
        novel_id=0,
        chapter_number=2,
        title="Chapter 2",
        content="...",
    ),
]
```

Use Case:

```python
use_case.execute(
    novel,
    chapters,
)
```

Transaction:

```text
BEGIN
    │
    ├── Novel UPSERT
    │      ↓
    │    novel_id = 10
    │
    ├── Chapter 1 UPSERT
    │
    ├── Chapter 2 UPSERT
    │
    └── COMMIT
```

---

# 28. Crawl lại

Lần thứ hai:

```text
BEGIN
    │
    ├── Novel UPSERT
    │      ↓
    │    novel_id = 10
    │
    ├── Chapter 1 UPSERT
    │
    ├── Chapter 2 UPSERT
    │
    └── COMMIT
```

Không có duplicate.

Database vẫn:

```text
Novel 10

Chapter 1
Chapter 2
```

---

# 29. Đây là nền tảng của Resume Crawler

Giả sử crawler có:

```text
1000 chapters
```

Đã lưu:

```text
1 → 500
```

Crawler crash.

Lần sau:

```text
resume from 501
```

Hoặc crawler không biết chính xác:

```text
crawl 1 → 1000
```

nhưng sử dụng:

```sql
UPSERT
```

thì:

```text
1 → 500
```

được update/skip về mặt dữ liệu,

```text
501 → 1000
```

được thêm.

Đây là một trong những lý do database crawler phải được thiết kế theo hướng **idempotent**.

---

# 30. Một nguyên tắc cực kỳ quan trọng

Repository:

```text
Persistence logic
```

Use Case:

```text
Application logic
```

Domain:

```text
Business rules
```

UoW:

```text
Transaction boundary
```

Ví dụ:

```text
┌──────────────────────────────┐
│          Use Case            │
│                              │
│  Save Novel + Chapters       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│             UoW              │
│                              │
│       Transaction            │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
 NovelRepository   ChapterRepository
       │                │
       └───────┬────────┘
               ▼
            SQLite
```

---

# 31. Sai lầm cần tránh

## ❌ Repository tự commit

```python
def add(self, novel):
    self.conn.execute(...)
    self.conn.commit()
```

Không.

---

## ❌ Mỗi Repository tự tạo connection

```python
class NovelRepository:

    def __init__(self):
        self.conn = sqlite3.connect(...)
```

Không.

---

## ❌ ChapterRepository commit riêng

```python
novel_repo.add(novel)
novel_repo.commit()

chapter_repo.add(chapter)
```

Phá transaction boundary.

---

## ❌ Dùng một connection global

```python
GLOBAL_CONN = sqlite3.connect(...)
```

Đặc biệt nguy hiểm khi crawler có worker/thread.

---

## ❌ Crawler tự viết SQL

```python
crawler:
    conn.execute(...)
```

Crawler không nên biết SQLite.

---

# 32. Kiến trúc hiện tại

Sau 6 buổi, hệ thống của chúng ta đã hình thành:

```text
                  CLI
                   │
                   ▼
              Application
                   │
                   ▼
                UseCase
                   │
                   ▼
                 UoW
            ┌──────┼──────┐
            ▼      ▼      ▼
         Novel  Chapter CrawlState
          Repo    Repo      Repo
            │      │        │
            └──────┼────────┘
                   ▼
          SQLiteConnection
              Manager
                   │
                   ▼
                SQLite
```

Đây đã là nền tảng khá tốt cho một crawler thực tế.

---

# 33. Bài tập Buổi 6

Hãy tự implement 4 phần sau.

### Bài 1

Viết:

```python
SQLiteChapterRepository.upsert()
```

với:

```text
UNIQUE(novel_id, chapter_number)
```

---

### Bài 2

Viết:

```python
SQLiteChapterRepository.upsert_many()
```

sử dụng:

```python
executemany()
```

---

### Bài 3

Hoàn thiện:

```python
SQLiteUnitOfWork
```

có:

```python
self.novels
self.chapters
```

và:

```python
commit()
rollback()
```

---

### Bài 4 — quan trọng nhất

Viết Use Case:

```python
SaveNovelWithChapters
```

đảm bảo:

```text
UPSERT Novel
       ↓
lấy novel_id
       ↓
gán novel_id cho Chapters
       ↓
UPSERT MANY Chapters
       ↓
COMMIT
```

và test tình huống:

```text
Chapter 1 ✓
Chapter 2 ✓
Chapter 3 ✗
```

để chứng minh:

```text
ROLLBACK
```

đã hoạt động.

---

# 34. Kiến thức cần nhớ sau Buổi 6

Nếu chỉ nhớ **7 điều**, hãy nhớ:

```text
1. Novel + Chapters thường được xử lý trong cùng transaction.

2. NovelRepository và ChapterRepository dùng cùng connection.

3. UoW là transaction boundary.

4. Repository không commit/rollback.

5. Crawler nên ưu tiên idempotent operation.

6. SQLite UPSERT rất phù hợp cho crawler.

7. Bulk operation → executemany().
```

Và đặc biệt:

```text
Crawler
   ↓
Use Case
   ↓
Unit of Work
   ↓
Repositories
   ↓
SQLite
```

**Crawler không nên trực tiếp điều khiển transaction.**

Buổi tiếp theo nên đi vào **Buổi 7 — CrawlStateRepository + Resume/Retry/Checkpoint**, nơi ta thiết kế trạng thái crawl như `pending → crawling → completed/failed`, checkpoint chapter cuối cùng và cơ chế resume sau khi crawler crash.
