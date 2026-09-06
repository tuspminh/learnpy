# Buổi 5 — NovelRepository Deep Dive

Hôm nay ta đi sâu vào **Repository Pattern** cho app crawl truyện chữ.

Mục tiêu là xây được:

```text
Domain Entity
    ↓
NovelRepository (interface)
    ↑
SQLiteNovelRepository
```

và hiểu rõ:

- Entity ↔ database row
- CRUD
- Query
- Upsert
- Pagination
- Bulk insert
- tránh N+1 query
- Repository không được chứa business logic
- Repository + UoW phối hợp thế nào

---

# 1. Repository thực chất là gì?

Đừng hiểu Repository đơn giản là:

```python
repository = CRUD wrapper
```

Ý tưởng sâu hơn:

> Repository tạo ra một abstraction để Domain/Application làm việc với collection của Domain Entity mà không cần biết persistence mechanism.

Ví dụ Application:

```python
novel = uow.novels.get(novel_id)
```

Application không cần biết:

```text
SQLite?
JSON?
PostgreSQL?
Memory?
```

Nó chỉ biết:

```text
NovelRepository
```

---

# 2. Entity trước

Giả sử Domain:

```python
from dataclasses import dataclass


@dataclass
class Novel:
    id: int | None
    title: str
    author: str | None
    source: str
```

Ví dụ:

```python
novel = Novel(
    id=1,
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    source="site_a",
)
```

Domain hoàn toàn không có:

```python
import sqlite3
```

Đây là nguyên tắc quan trọng.

---

# 3. Database Model

SQLite:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    source TEXT NOT NULL
);
```

Mapping:

```text
Novel.id
    ↓
novels.id

Novel.title
    ↓
novels.title

Novel.author
    ↓
novels.author

Novel.source
    ↓
novels.source
```

---

# 4. Repository Interface

Domain:

```python
from abc import ABC, abstractmethod


class NovelRepository(ABC):

    @abstractmethod
    def add(self, novel: Novel) -> None:
        ...

    @abstractmethod
    def get(self, novel_id: int) -> Novel | None:
        ...

    @abstractmethod
    def delete(self, novel_id: int) -> None:
        ...

    @abstractmethod
    def list(self) -> list[Novel]:
        ...
```

Đây là abstraction.

Không có:

```text
SQL
SQLite
cursor
connection
```

---

# 5. Mapping Row → Entity

Đây là một trong những nhiệm vụ quan trọng nhất của Repository.

SQLite trả về:

```python
row
```

Ví dụ:

```python
row["id"]
row["title"]
row["author"]
row["source"]
```

Nhưng Application muốn:

```python
Novel(...)
```

Ta tạo mapper:

```python
def row_to_novel(row) -> Novel:

    return Novel(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        source=row["source"],
    )
```

---

# 6. Tại sao nên có mapper riêng?

Không nên viết lặp:

```python
def get(...):

    return Novel(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        source=row["source"],
    )
```

rồi:

```python
def list(...):

    return [
        Novel(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            source=row["source"],
        )
        for row in rows
    ]
```

Sẽ bị duplicate.

Ta tạo:

```python
class NovelMapper:

    @staticmethod
    def to_domain(row) -> Novel:
        return Novel(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            source=row["source"],
        )
```

---

# 7. Mapping Entity → SQL parameters

Chiều ngược lại:

```python
def novel_to_params(novel: Novel):
    return (
        novel.id,
        novel.title,
        novel.author,
        novel.source,
    )
```

Ta có:

```text
              Mapper
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
   DB Row              Novel Entity
       │                   │
       └────── mapping ────┘
```

---

# 8. `add()`

Repository:

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn

    def add(self, novel: Novel) -> None:

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
```

Chú ý:

```python
?
```

và:

```python
(novel.id, ...)
```

Không nối string:

```python
# BAD
sql = f"""
INSERT INTO novels VALUES (
    {novel.id},
    '{novel.title}'
)
"""
```

---

# 9. `get()`

```python
def get(
    self,
    novel_id: int,
) -> Novel | None:

    row = self.conn.execute(
        """
        SELECT
            id,
            title,
            author,
            source
        FROM novels
        WHERE id = ?
        """,
        (novel_id,),
    ).fetchone()

    if row is None:
        return None

    return NovelMapper.to_domain(row)
```

Flow:

```text
novel_id
   ↓
SQL
   ↓
sqlite3.Row
   ↓
NovelMapper
   ↓
Novel
```

---

# 10. `list()`

```python
def list(self) -> list[Novel]:

    rows = self.conn.execute(
        """
        SELECT
            id,
            title,
            author,
            source
        FROM novels
        ORDER BY id
        """
    ).fetchall()

    return [
        NovelMapper.to_domain(row)
        for row in rows
    ]
```

---

# 11. `delete()`

```python
def delete(self, novel_id: int) -> None:

    self.conn.execute(
        """
        DELETE FROM novels
        WHERE id = ?
        """,
        (novel_id,),
    )
```

Nhưng có một câu hỏi:

> `delete()` có nên commit không?

**Không.**

Repository:

```text
execute
```

UoW:

```text
commit / rollback
```

---

# 12. Repository không quản lý transaction

Sai:

```python
def delete(self, novel_id):

    self.conn.execute(...)

    self.conn.commit()
```

Đúng:

```python
def delete(self, novel_id):

    self.conn.execute(...)
```

Application:

```python
with uow:

    uow.novels.delete(novel_id)

    uow.chapters.delete_for_novel(
        novel_id
    )
```

UoW:

```text
COMMIT
```

---

# 13. `exists()`

Crawler thường xuyên cần:

> Truyện này đã tồn tại chưa?

Đừng:

```python
novel = repo.get(novel_id)

if novel:
    ...
```

nếu bạn chỉ cần biết existence.

Ta tạo:

```python
def exists(self, novel_id: int) -> bool:

    row = self.conn.execute(
        """
        SELECT 1
        FROM novels
        WHERE id = ?
        LIMIT 1
        """,
        (novel_id,),
    ).fetchone()

    return row is not None
```

Database chỉ cần trả:

```text
1
```

thay vì toàn bộ entity.

---

# 14. Query theo source

Crawler của bạn có nhiều nguồn:

```text
site_a
site_b
site_c
```

Ta có:

```python
def find_by_source(
    self,
    source: str,
) -> list[Novel]:

    rows = self.conn.execute(
        """
        SELECT
            id,
            title,
            author,
            source
        FROM novels
        WHERE source = ?
        ORDER BY id
        """,
        (source,),
    ).fetchall()

    return [
        NovelMapper.to_domain(row)
        for row in rows
    ]
```

---

# 15. Query theo title

```python
def search_title(
    self,
    keyword: str,
) -> list[Novel]:

    rows = self.conn.execute(
        """
        SELECT
            id,
            title,
            author,
            source
        FROM novels
        WHERE title LIKE ?
        ORDER BY title
        """,
        (f"%{keyword}%",),
    ).fetchall()

    return [
        NovelMapper.to_domain(row)
        for row in rows
    ]
```

Ở đây có một vấn đề hiệu năng nếu database rất lớn.

```sql
LIKE '%keyword%'
```

khó tận dụng index thông thường.

Sau này nếu cần search mạnh hơn, ta có thể nghiên cứu:

```text
SQLite FTS5
```

---

# 16. Upsert

Crawler có pattern rất phổ biến:

```text
crawl novel
    ↓
nếu chưa có → INSERT
nếu có       → UPDATE
```

Thay vì:

```python
if repo.exists(id):
    repo.update(novel)
else:
    repo.add(novel)
```

ta có thể dùng SQLite UPSERT.

Ví dụ:

```sql
INSERT INTO novels (
    id,
    title,
    author,
    source
)
VALUES (?, ?, ?, ?)

ON CONFLICT(id)
DO UPDATE SET
    title = excluded.title,
    author = excluded.author,
    source = excluded.source;
```

Repository:

```python
def upsert(self, novel: Novel):

    self.conn.execute(
        """
        INSERT INTO novels (
            id,
            title,
            author,
            source
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(id)
        DO UPDATE SET
            title = excluded.title,
            author = excluded.author,
            source = excluded.source
        """,
        (
            novel.id,
            novel.title,
            novel.author,
            novel.source,
        ),
    )
```

Crawler sẽ rất thích API:

```python
uow.novels.upsert(novel)
```

---

# 17. Nhưng `upsert()` có phải business logic?

Không.

Repository quyết định:

```text
SQL implementation
```

Còn business rule:

> "Nếu novel đã hoàn thành thì không được overwrite"

lại là Domain/Application logic.

Ví dụ:

```python
if novel.status == "completed":
    raise NovelAlreadyCompleted()
```

không nên nhét vào SQLite repository.

Repository chỉ biết persistence.

---

# 18. Pagination

App dashboard có thể có:

```text
1 2 3 4 5 ...
```

Không nên:

```python
repo.list()
```

rồi Python:

```python
rows[100:120]
```

Nếu database có 1 triệu truyện thì rất lãng phí.

Ta query:

```sql
LIMIT ?
OFFSET ?
```

Repository:

```python
def list_paginated(
    self,
    limit: int,
    offset: int,
) -> list[Novel]:

    rows = self.conn.execute(
        """
        SELECT
            id,
            title,
            author,
            source
        FROM novels
        ORDER BY id
        LIMIT ?
        OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

    return [
        NovelMapper.to_domain(row)
        for row in rows
    ]
```

---

# 19. Pagination tốt hơn với Keyset Pagination

`OFFSET` có thể trở nên chậm khi offset lớn:

```text
OFFSET 900000
```

Với crawler/dashboard lớn, ta có thể dùng:

```sql
WHERE id > ?
ORDER BY id
LIMIT ?
```

Repository:

```python
def list_after(
    self,
    last_id: int | None,
    limit: int,
) -> list[Novel]:

    if last_id is None:

        rows = self.conn.execute(
            """
            SELECT id, title, author, source
            FROM novels
            ORDER BY id
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    else:

        rows = self.conn.execute(
            """
            SELECT id, title, author, source
            FROM novels
            WHERE id > ?
            ORDER BY id
            LIMIT ?
            """,
            (last_id, limit),
        ).fetchall()

    return [
        NovelMapper.to_domain(row)
        for row in rows
    ]
```

Đây gọi là:

> **Keyset / cursor pagination.**

Rất hữu ích cho dashboard crawler.

---

# 20. Bulk Insert

Crawler có thể tải:

```text
500 chapters
```

Không nên:

```python
for chapter in chapters:
    repo.add(chapter)
```

nếu implementation gây quá nhiều overhead.

SQLite hỗ trợ:

```python
executemany()
```

Ví dụ:

```python
def add_many(self, novels):

    self.conn.executemany(
        """
        INSERT INTO novels (
            id,
            title,
            author,
            source
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                novel.id,
                novel.title,
                novel.author,
                novel.source,
            )
            for novel in novels
        ],
    )
```

Vẫn để UoW quyết định:

```text
COMMIT
```

---

# 21. N+1 Query

Một lỗi rất phổ biến:

```python
novels = repo.list()

for novel in novels:

    chapters = chapter_repo.find_by_novel(
        novel.id
    )
```

Nếu có:

```text
100 novels
```

thì:

```text
1 query lấy novels
+
100 queries lấy chapters
=
101 queries
```

Đây là:

> **N+1 Query Problem**

---

# 22. Cách cải thiện

Thay vì:

```text
SELECT novels

SELECT chapters WHERE novel_id = 1
SELECT chapters WHERE novel_id = 2
SELECT chapters WHERE novel_id = 3
...
```

có thể dùng JOIN:

```sql
SELECT
    n.id,
    n.title,
    c.id,
    c.title
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?;
```

Hoặc batch query:

```sql
SELECT *
FROM chapters
WHERE novel_id IN (?, ?, ?, ...);
```

Nhưng cần nhớ:

> Repository nên expose API phù hợp với use case, không phải expose mọi SQL query.

---

# 23. Repository không phải ORM

Ta đang dùng:

```text
sqlite3
+
raw SQL
```

Repository vẫn rất hữu ích.

Nó tạo abstraction:

```text
Application
    ↓
NovelRepository
    ↓
SQL
```

thay vì:

```text
Application
    ↓
conn.execute(...)
    ↓
SQL
```

Đây chính là lý do Repository Pattern phù hợp với kiến trúc Clean Architecture/DDD mà bạn đang học.

---

# 24. Repository + UoW

Đây là cặp đôi:

```text
UnitOfWork
│
├── novels
├── chapters
└── crawl_states
```

Repository:

```text
NovelRepository
     ↓
persist Novel
```

UoW:

```text
transaction boundary
```

Ví dụ:

```python
with uow:

    novel = uow.novels.get(novel_id)

    if novel is None:
        raise NovelNotFound()

    uow.novels.upsert(novel)

    uow.chapters.add_many(chapters)

    uow.crawl_states.mark_completed(
        novel.id
    )
```

Tất cả:

```text
ONE transaction
```

---

# 25. Một `NovelRepository` tương đối hoàn chỉnh

```python
class SQLiteNovelRepository:

    def __init__(self, conn):
        self.conn = conn

    def add(self, novel):
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

    def get(self, novel_id):

        row = self.conn.execute(
            """
            SELECT
                id,
                title,
                author,
                source
            FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        ).fetchone()

        if row is None:
            return None

        return NovelMapper.to_domain(row)

    def exists(self, novel_id):

        row = self.conn.execute(
            """
            SELECT 1
            FROM novels
            WHERE id = ?
            LIMIT 1
            """,
            (novel_id,),
        ).fetchone()

        return row is not None

    def upsert(self, novel):

        self.conn.execute(
            """
            INSERT INTO novels (
                id,
                title,
                author,
                source
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(id)
            DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                source = excluded.source
            """,
            (
                novel.id,
                novel.title,
                novel.author,
                novel.source,
            ),
        )

    def delete(self, novel_id):

        self.conn.execute(
            """
            DELETE FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        )
```

---

# 26. Kiến trúc hoàn chỉnh lúc này

```text
                 Domain
                   │
                   ▼
           ┌─────────────────┐
           │ Novel Entity    │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │NovelRepository  │
           │   interface     │
           └────────┬────────┘
                    ▲
                    │
          ┌─────────┴──────────┐
          │                    │
          ▼                    ▼
 SQLiteNovelRepository   FileNovelRepository
          │
          ▼
      sqlite3.Row
          │
          ▼
     NovelMapper
          │
          ▼
        Novel
```

UoW:

```text
SQLiteUoW
    │
    ├── NovelRepository
    ├── ChapterRepository
    └── CrawlStateRepository
             │
             ▼
       SAME connection
```

---

# 27. Một nguyên tắc rất quan trọng cho project

Repository **không nên trở thành God Class**.

Đừng biến:

```python
NovelRepository
```

thành:

```text
500 methods
```

như:

```text
find_by_title()
find_by_author()
find_by_source()
find_by_status()
find_by_status_and_source()
find_by_author_and_source()
find_by_title_and_status()
...
```

Khi query bắt đầu phức tạp, ta sẽ học:

```text
Query Object
Specification
Read Model
CQRS
```

Đặc biệt app dashboard crawler sau này sẽ rất phù hợp với **Read Model**.

---

# 28. Bài tập Buổi 5

Hãy xây `SQLiteNovelRepository` có tối thiểu:

```text
add()
get()
exists()
delete()
upsert()
list_paginated()
```

và:

```text
NovelMapper.to_domain()
```

Database:

```sql
novels
---------
id
title
author
source
```

Sau đó test:

```text
✓ add novel
✓ get novel
✓ get missing novel
✓ exists
✓ delete
✓ upsert
✓ pagination
```

Quan trọng nhất:

```text
Repository
    ❌ không commit
    ❌ không rollback

UoW
    ✅ commit
    ✅ rollback
```

---

## Bước tiếp theo — Buổi 6

Tôi đề xuất chuyển sang **Repository nâng cao cho crawler**:

```text
Buổi 6
NovelRepository + ChapterRepository
        ↓
Aggregate boundary
        ↓
Novel + Chapters
        ↓
transaction
        ↓
bulk insert
        ↓
UPSERT chapter
        ↓
idempotent crawling
        ↓
"crawl lại không tạo duplicate"
```

Đây sẽ là buổi rất quan trọng vì chúng ta bắt đầu kết nối **DDD Aggregate + Repository + UoW + SQLite** vào workflow crawl truyện thực tế.