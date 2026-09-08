# Phần IV — SQLite Deep Dive

# Buổi 27 — Transaction Deep Dive

Đây là một trong những buổi **quan trọng nhất** của toàn bộ phần SQLite.

Ở các buổi trước, ta đã dùng:

```python
conn.commit()
conn.rollback()
```

nhưng hôm nay sẽ hiểu **transaction thực sự hoạt động thế nào**, và đặc biệt:

> **Tại sao Unit of Work phải sở hữu transaction boundary?**

---

# 1. Transaction là gì?

Transaction là một nhóm thao tác database được SQLite xem như **một đơn vị công việc logic**.

Ví dụ crawler lưu một Novel:

```text id="tx1"
INSERT Novel
    ↓
INSERT Chapter 1
    ↓
INSERT Chapter 2
    ↓
INSERT Chapter 3
```

Ta muốn:

```text id="tx2"
Tất cả thành công
        ↓
      COMMIT
```

hoặc:

```text id="tx3"
Một thao tác thất bại
        ↓
     ROLLBACK
        ↓
Không lưu thay đổi của transaction
```

---

# 2. Atomicity

Đây là chữ **A** trong ACID.

```text id="acid1"
Atomicity
Consistency
Isolation
Durability
```

Atomicity có thể hiểu:

> Transaction xảy ra như một đơn vị: thành công toàn bộ hoặc rollback toàn bộ.

Ví dụ:

```text id="tx4"
BEGIN
 │
 ├── INSERT novel
 ├── INSERT chapter 1
 ├── INSERT chapter 2
 └── INSERT chapter 3
 │
 └── COMMIT
```

Nếu chapter 3 lỗi:

```text id="tx5"
BEGIN
 │
 ├── INSERT novel       ✓
 ├── INSERT chapter 1   ✓
 ├── INSERT chapter 2   ✓
 ├── INSERT chapter 3   ✗
 │
 └── ROLLBACK
```

Kết quả:

```text id="tx6"
Novel       → không lưu
Chapter 1   → không lưu
Chapter 2   → không lưu
```

Đó là atomicity.

---

# 3. Transaction boundary

Một khái niệm cực kỳ quan trọng:

> **Transaction boundary = điểm bắt đầu và kết thúc của một transaction.**

Ví dụ:

```text id="tx7"
BEGIN
   │
   │  create novel
   │  create chapters
   │  update metadata
   │
COMMIT
```

Toàn bộ phần giữa:

```text id="tx8"
BEGIN → COMMIT
```

là một transaction.

---

# 4. BEGIN

SQL cơ bản:

```sql id="tx9"
BEGIN;
```

Sau đó:

```sql id="tx10"
INSERT ...
UPDATE ...
DELETE ...
```

Cuối cùng:

```sql id="tx11"
COMMIT;
```

hoặc:

```sql id="tx12"
ROLLBACK;
```

---

# 5. Python

Ví dụ:

```python id="tx13"
conn.execute("BEGIN")

try:
    conn.execute(
        "INSERT INTO novels(title) VALUES (?)",
        ("Tiên Nghịch",),
    )

    conn.execute(
        """
        INSERT INTO chapters(
            novel_id,
            chapter_number,
            title
        )
        VALUES (?, ?, ?)
        """,
        (1, 1, "Chương 1"),
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

Flow:

```text id="tx14"
BEGIN
 ↓
INSERT
 ↓
INSERT
 ↓
COMMIT

      hoặc

BEGIN
 ↓
INSERT
 ↓
ERROR
 ↓
ROLLBACK
```

---

# 6. `commit()` thực sự làm gì?

Trước:

```python id="tx15"
conn.execute(...)
```

thay đổi có thể vẫn nằm trong transaction chưa commit.

Khi:

```python id="tx16"
conn.commit()
```

SQLite xác nhận:

> "Các thay đổi của transaction này được chấp nhận."

---

# 7. `rollback()` thực sự làm gì?

```python id="tx17"
conn.rollback()
```

nói với SQLite:

> "Hủy các thay đổi chưa commit của transaction hiện tại."

Ví dụ:

```python id="tx18"
conn.execute(
    "INSERT INTO novels(title) VALUES (?)",
    ("Novel A",),
)

conn.execute(
    "INSERT INTO novels(title) VALUES (?)",
    ("Novel B",),
)

conn.rollback()
```

Sau đó:

```sql id="tx19"
SELECT *
FROM novels;
```

Hai Novel vừa insert sẽ không còn trong database.

---

# 8. Transaction không phải backup

Đây là một hiểu nhầm cần tránh.

Transaction:

```text id="tx20"
BEGIN
  ↓
changes
  ↓
ROLLBACK
```

chỉ rollback **các thay đổi chưa commit trong transaction**.

Nếu:

```python id="tx21"
conn.execute(...)
conn.commit()
```

sau đó:

```python id="tx22"
conn.rollback()
```

thì không thể dùng rollback để "undo" transaction đã commit.

```text id="tx23"
COMMIT
   ↓
transaction kết thúc
   ↓
ROLLBACK sau đó
   ↓
không undo transaction cũ
```

---

# 9. Một transaction có thể chứa nhiều loại operation

Không chỉ INSERT.

Ví dụ:

```text id="tx24"
BEGIN
 │
 ├── INSERT novel
 ├── UPDATE novel
 ├── INSERT chapters
 ├── DELETE old chapter
 └── UPDATE crawler state
 │
COMMIT
```

Đây là lý do transaction rất phù hợp với **use case**, chứ không chỉ với một câu SQL.

---

# 10. Transaction và Use Case

Giả sử use case:

```text id="tx25"
CreateNovelWithChapters
```

Business operation:

```text id="tx26"
1. Create Novel
2. Create Chapter 1
3. Create Chapter 2
4. Create Chapter 3
```

Ta muốn transaction bao quanh **toàn bộ use case**:

```text id="tx27"
BEGIN
 │
 │ CreateNovel
 │ AddChapter
 │ AddChapter
 │ AddChapter
 │
COMMIT
```

Không nên:

```text id="tx28"
INSERT Novel
COMMIT

INSERT Chapter 1
COMMIT

INSERT Chapter 2
COMMIT

INSERT Chapter 3
ERROR
```

Bởi vì database lúc này có:

```text id="tx29"
Novel
Chapter 1
Chapter 2
```

nhưng thiếu Chapter 3.

Nếu business yêu cầu tất cả phải cùng thành công, thiết kế này sai.

---

# 11. Đây chính là lý do Unit of Work xuất hiện

Ta đã học:

```text id="uow1"
Application
     ↓
Unit of Work
     ↓
Repository
     ↓
SQLite
```

Unit of Work có nhiệm vụ:

> Gom nhiều thao tác repository vào **một transaction boundary**.

Ví dụ:

```python id="uow2"
with uow:
    novel = uow.novels.add(...)
    uow.chapters.add(...)
    uow.chapters.add(...)
    uow.chapters.add(...)
```

Khi block kết thúc:

```text id="uow3"
Không exception
     ↓
COMMIT
```

Nếu exception:

```text id="uow4"
Exception
     ↓
ROLLBACK
```

---

# 12. UoW là transaction coordinator

Mental model:

```text id="uow5"
             Unit of Work
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
 NovelRepository     ChapterRepository
        │                   │
        └─────────┬─────────┘
                  ↓
             Connection
                  ↓
               SQLite
```

UoW sở hữu:

```text id="uow6"
transaction lifecycle
```

Repository chỉ tập trung vào:

```text id="uow7"
database operations
```

---

# 13. Context Manager

Python có một pattern rất phù hợp:

```python id="ctx1"
with uow:
    ...
```

Ví dụ đơn giản:

```python id="ctx2"
class UnitOfWork:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn.execute("BEGIN")
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
```

Flow:

```text id="ctx3"
with uow:
    │
    ├── __enter__()
    │       ↓
    │      BEGIN
    │
    ├── repository operations
    │
    └── __exit__()
            │
       ┌────┴────┐
       ↓         ↓
   no error    error
       ↓         ↓
    COMMIT    ROLLBACK
```

Đây chính là pattern ta sẽ sử dụng rất nhiều.

---

# 14. Một vấn đề: SQLite tự bắt đầu transaction

Với Python `sqlite3`, transaction behavior không phải lúc nào cũng giống việc bạn tự viết:

```sql
BEGIN;
```

Ở code đơn giản, khi thực hiện các thao tác ghi, `sqlite3` có thể tự mở transaction tùy theo cấu hình isolation level.

Vì vậy khi xây architecture rõ ràng, ta cần **chủ động quyết định transaction boundary**, thay vì để mỗi repository tự commit.

Đây là lý do UoW rất hữu ích.

---

# 15. Sai lầm lớn: Repository tự commit

Ví dụ:

```python id="bad1"
class NovelRepository:
    def add(self, title):
        self._conn.execute(
            "INSERT INTO novels(title) VALUES (?)",
            (title,),
        )

        self._conn.commit()
```

❌ Không tốt nếu muốn Unit of Work quản lý transaction.

Vì:

```text id="bad2"
Repository
   ↓
COMMIT
```

transaction bị kết thúc ngay trong repository.

Sau đó ChapterRepository:

```text id="bad3"
ChapterRepository
   ↓
COMMIT
```

UoW không còn kiểm soát được toàn bộ operation.

---

# 16. Repository tốt hơn

```python id="good1"
class NovelRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, title):
        cursor = self._conn.execute(
            """
            INSERT INTO novels(title)
            VALUES (?)
            """,
            (title,),
        )

        return cursor.lastrowid
```

Không:

```python id="good2"
self._conn.commit()
```

Repository chỉ:

```text id="good3"
execute SQL
   ↓
return result
```

Còn:

```text id="good4"
commit / rollback
```

do UoW quản lý.

---

# 17. Đây là nguyên tắc cực kỳ quan trọng

> **Repository không nên quyết định transaction boundary khi Unit of Work đang quản lý transaction.**

Sai:

```text id="bad3"
Repository A → commit
Repository B → commit
Repository C → commit
```

Tốt:

```text id="good5"
Unit of Work
    ↓
BEGIN
    ↓
Repository A
    ↓
Repository B
    ↓
Repository C
    ↓
COMMIT
```

---

# 18. Transaction với crawler

Giả sử crawler lấy được:

```text id="crawl1"
Novel:
Tiên Nghịch

Chapters:
1
2
3
4
5
```

Ta thực hiện:

```text id="crawl2"
BEGIN
 │
 ├── insert novel
 │
 ├── insert chapter 1
 ├── insert chapter 2
 ├── insert chapter 3
 ├── insert chapter 4
 └── insert chapter 5
 │
COMMIT
```

Nếu chapter 4 bị duplicate:

```text id="crawl3"
BEGIN
 │
 ├── novel ✓
 ├── chapter 1 ✓
 ├── chapter 2 ✓
 ├── chapter 3 ✓
 ├── chapter 4 ✗
 │
 └── ROLLBACK
```

Toàn bộ transaction bị hủy.

---

# 19. Nhưng có phải lúc nào cũng rollback tất cả?

Không.

Đây là một quyết định **business/use-case**.

Ví dụ crawler có thể muốn:

```text id="crawl4"
Chapter 1 ✓
Chapter 2 ✓
Chapter 3 duplicate
Chapter 4 ✓
Chapter 5 ✓
```

Nếu business cho phép:

> Chapter duplicate thì bỏ qua, các chapter khác vẫn lưu.

thì không nhất thiết rollback toàn bộ transaction.

Có thể dùng:

```text id="savepoint1"
SAVEPOINT
```

Đây là nội dung rất quan trọng tiếp theo.

---

# 20. SAVEPOINT

`SAVEPOINT` cho phép tạo một điểm rollback **bên trong transaction**.

Ví dụ:

```sql id="sp1"
BEGIN;

INSERT INTO novels(title)
VALUES ('Tiên Nghịch');

SAVEPOINT chapter_batch;

INSERT INTO chapters(...);
INSERT INTO chapters(...);

ROLLBACK TO chapter_batch;

RELEASE chapter_batch;

COMMIT;
```

Khác biệt:

```text id="sp2"
ROLLBACK
```

→ rollback toàn transaction.

Trong khi:

```text id="sp3"
ROLLBACK TO savepoint
```

→ rollback về savepoint, nhưng transaction bên ngoài vẫn tiếp tục.

---

# 21. Mental model của SAVEPOINT

```text id="sp4"
BEGIN
 │
 │ Novel
 │
 ├── SAVEPOINT chapters
 │      │
 │      ├── Chapter 1
 │      ├── Chapter 2
 │      └── Chapter 3
 │
 │      ROLLBACK TO chapters
 │
 │ vẫn còn trong transaction
 │
 └── COMMIT
```

---

# 22. SAVEPOINT ≠ nested transaction thực sự

Đây là một điểm advanced.

SQLite không tạo ra transaction độc lập lồng trong transaction như:

```text id="sp5"
Transaction A
    └── Transaction B
```

Thay vào đó:

```text id="sp6"
Transaction
    └── SAVEPOINT
          └── SAVEPOINT
```

SAVEPOINT tạo **transactional checkpoints** bên trong transaction.

---

# 23. Python sử dụng SAVEPOINT

```python id="sp7"
conn.execute("BEGIN")

try:
    conn.execute(
        """
        INSERT INTO novels(title)
        VALUES (?)
        """,
        ("Tiên Nghịch",),
    )

    conn.execute("SAVEPOINT chapters")

    try:
        conn.execute(
            """
            INSERT INTO chapters(
                novel_id,
                chapter_number,
                title
            )
            VALUES (?, ?, ?)
            """,
            (1, 1, "Chapter 1"),
        )

        conn.execute(
            """
            INSERT INTO chapters(
                novel_id,
                chapter_number,
                title
            )
            VALUES (?, ?, ?)
            """,
            (1, 1, "Duplicate"),
        )

        conn.execute("RELEASE chapters")

    except Exception:
        conn.execute("ROLLBACK TO chapters")

        conn.execute("RELEASE chapters")

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

---

# 24. `ROLLBACK TO` chưa kết thúc transaction

Đây là điểm cần nhớ.

```sql id="sp8"
ROLLBACK TO chapters;
```

không tương đương:

```sql id="sp9"
ROLLBACK;
```

Sau:

```sql id="sp10"
ROLLBACK TO chapters;
```

transaction vẫn đang hoạt động.

Bạn có thể tiếp tục:

```sql id="sp11"
INSERT ...
```

rồi:

```sql id="sp12"
COMMIT;
```

---

# 25. `RELEASE SAVEPOINT`

Sau khi hoàn thành savepoint:

```sql id="sp13"
RELEASE chapters;
```

xóa savepoint đó.

Nhưng:

> `RELEASE SAVEPOINT` không đồng nghĩa với commit toàn transaction nếu vẫn còn transaction bên ngoài.

Mental model:

```text id="sp14"
BEGIN
  │
  ├── SAVEPOINT A
  │      │
  │      └── RELEASE A
  │
  └── COMMIT
```

---

# 26. Transaction + SAVEPOINT trong Repository?

Cẩn thận.

Không nên để mỗi repository tự tạo transaction:

```text id="bad4"
NovelRepository
    ↓ BEGIN

ChapterRepository
    ↓ BEGIN

TagRepository
    ↓ BEGIN
```

Architecture sẽ trở nên rất khó kiểm soát.

Thay vào đó:

```text id="good6"
Use Case
   ↓
Unit of Work
   ↓
BEGIN
   │
   ├── NovelRepository
   ├── ChapterRepository
   └── TagRepository
   │
   ↓
COMMIT
```

Nếu cần partial rollback, UoW/application service có thể quản lý savepoint.

---

# 27. Transaction Isolation

Một phần của ACID là:

```text id="iso1"
Isolation
```

Nói đơn giản:

> Các transaction đồng thời không nên nhìn thấy trạng thái trung gian của nhau theo cách phá vỡ tính nhất quán.

Ví dụ:

```text id="iso2"
Transaction A
   ↓
UPDATE chapter

Transaction B
   ↓
SELECT chapter
```

Việc B nhìn thấy gì trước/sau commit phụ thuộc vào transaction model và locking behavior.

SQLite có mô hình concurrency khác với PostgreSQL/MySQL.

Đây sẽ là cầu nối tới:

```text id="iso3"
Buổi 29 — Locking & Concurrency
```

---

# 28. Durability

Chữ cuối:

```text id="acid4"
D — Durability
```

Sau:

```sql id="acid5"
COMMIT;
```

SQLite phải đảm bảo dữ liệu đã commit được bảo toàn theo durability guarantees/configuration.

Và đây chính là nơi Buổi 26:

```text id="acid6"
PRAGMA synchronous
PRAGMA journal_mode
```

liên quan trực tiếp đến transaction.

```text id="acid7"
Transaction
    ↓
COMMIT
    ↓
Journal / WAL
    ↓
Durability
```

---

# 29. Transaction + Constraint

Bây giờ ghép Buổi 25 với Buổi 27.

```text id="combo1"
BEGIN
  ↓
INSERT Novel
  ↓
INSERT Chapter
  ↓
FOREIGN KEY
  ↓
UNIQUE
  ↓
CHECK
  ↓
COMMIT
```

Nếu constraint fail:

```text id="combo2"
Constraint violation
       ↓
Exception
       ↓
ROLLBACK
```

Đây là lý do:

```text id="combo3"
Constraints
+
Transactions
```

là hai chủ đề phải hiểu cùng nhau.

---

# 30. Transaction trong Unit of Work

Ta có thể xây một UoW đơn giản:

```python id="uow8"
class SQLiteUnitOfWork:
    def __init__(self, connection):
        self.conn = connection

    def __enter__(self):
        self.conn.execute("BEGIN")
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
```

Sử dụng:

```python id="uow9"
with SQLiteUnitOfWork(conn) as uow:
    uow.conn.execute(
        """
        INSERT INTO novels(title)
        VALUES (?)
        """,
        ("Tiên Nghịch",),
    )

    uow.conn.execute(
        """
        INSERT INTO novels(title)
        VALUES (?)
        """,
        ("Phàm Nhân Tu Tiên",),
    )
```

Không lỗi:

```text id="uow10"
BEGIN
 ↓
INSERT
 ↓
INSERT
 ↓
COMMIT
```

Có lỗi:

```text id="uow11"
BEGIN
 ↓
INSERT
 ↓
ERROR
 ↓
ROLLBACK
```

---

# 31. Nhưng UoW thật sẽ tốt hơn

Sau này ta không muốn:

```python id="uow12"
uow.conn.execute(...)
```

ở Application.

Ta muốn:

```python id="uow13"
with uow:
    novel = uow.novels.add(...)
    uow.chapters.add(...)
```

Kiến trúc:

```text id="uow14"
Application Service
       ↓
       UoW
       │
       ├── novels
       │      ↓
       │   NovelRepository
       │
       └── chapters
              ↓
          ChapterRepository
                  ↓
              Connection
                  ↓
                SQLite
```

Đây chính là nền móng cho phần:

```text id="uow15"
Phần IX — Unit of Work
```

---

# 32. Một quy tắc vàng

Hãy nhớ câu này:

> **Transaction boundary nên bao quanh một business operation có tính atomic.**

Ví dụ:

```text id="rule1"
CreateNovelWithInitialChapters
```

→ một transaction.

Nhưng:

```text id="rule2"
Download 10.000 chapters
```

không nhất thiết phải là một transaction khổng lồ.

Có thể chia:

```text id="rule3"
Batch 1
BEGIN
...
COMMIT

Batch 2
BEGIN
...
COMMIT

Batch 3
BEGIN
...
COMMIT
```

Transaction quá lớn có thể gây:

```text id="rule4"
long lock
memory pressure
poor concurrency
large rollback cost
```

Đây sẽ liên quan trực tiếp tới WAL và locking.

---

# 33. Sai lầm: transaction quá dài

❌ Ví dụ:

```text id="bad5"
BEGIN

download chapter 1
download chapter 2
download chapter 3
...
download chapter 1000

COMMIT
```

Nếu download HTTP nằm bên trong transaction:

```text id="bad6"
BEGIN
  ↓
HTTP request
  ↓
HTTP request
  ↓
HTTP request
  ↓
...
  ↓
COMMIT
```

thì database transaction có thể giữ lâu trong khi application đang chờ network.

Đây là thiết kế rất dễ gây locking problem.

Tốt hơn:

```text id="good7"
HTTP crawl
    ↓
parse
    ↓
prepare data
    ↓
BEGIN
    ↓
short DB writes
    ↓
COMMIT
```

Đây là một nguyên tắc cực kỳ quan trọng cho crawler.

---

# 34. Transaction Boundary trong crawler

Một flow tốt hơn:

```text id="crawler_tx"
             HTTP
              ↓
           Crawl
              ↓
            Parse
              ↓
       Build Chapter objects
              ↓
        BEGIN TRANSACTION
              ↓
       INSERT/UPDATE SQLite
              ↓
             COMMIT
```

Không nên:

```text id="crawler_bad"
BEGIN
  ↓
HTTP
  ↓
parse
  ↓
HTTP
  ↓
parse
  ↓
HTTP
  ↓
...
  ↓
COMMIT
```

---

# 35. Bài tập thực hành 1

Tạo database:

```sql id="ex1"
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id),

    UNIQUE (novel_id, chapter_number)
);
```

Viết Python:

```text id="ex2"
BEGIN
  ↓
insert novel
  ↓
insert chapter 1
  ↓
insert chapter 2
  ↓
insert chapter 2 lần nữa
  ↓
ROLLBACK
```

Sau đó kiểm tra:

```sql id="ex3"
SELECT *
FROM novels;
```

và:

```sql id="ex4"
SELECT *
FROM chapters;
```

Kỳ vọng:

```text id="ex5"
novels   → 0 rows
chapters → 0 rows
```

---

# 36. Bài tập 2 — SAVEPOINT

Thử:

```text id="ex6"
BEGIN

insert novel

SAVEPOINT chapters

insert chapter 1
insert chapter 2
insert duplicate chapter

ROLLBACK TO chapters

RELEASE chapters

insert chapter 3

COMMIT
```

Sau đó kiểm tra.

Bạn cần suy luận:

```text id="ex7"
Novel      → ?
Chapter 1  → ?
Chapter 2  → ?
Duplicate  → ?
Chapter 3  → ?
```

Đây là bài tập rất tốt để hiểu SAVEPOINT.

---

# 37. Bài tập 3 — UoW

Viết:

```python id="ex8"
class SQLiteUnitOfWork: ...
```

Yêu cầu:

```text id="ex9"
with uow:
    ...
```

Nếu:

```text id="ex10"
không exception
```

→ `commit()`

Nếu:

```text id="ex11"
có exception
```

→ `rollback()`

---

# 38. Bài tập 4 — Repository

Viết:

```python id="ex12"
class NovelRepository: ...
```

và:

```python id="ex13"
class ChapterRepository: ...
```

**Không được `commit()` bên trong repository.**

Sau đó:

```python id="ex14"
with uow:
    novel_id = uow.novels.add(...)
    uow.chapters.add(...)
    uow.chapters.add(...)
```

Đây là bước đầu tiên để bạn thực sự hiểu:

```text id="ex15"
Repository
+
Unit of Work
+
Transaction
```

---

# 39. Tổng kết Buổi 27

Mental model quan trọng nhất:

```text id="summary1"
Transaction
    │
    ├── BEGIN
    │
    ├── SQL operations
    │
    ├── Constraint checks
    │
    ├── COMMIT
    │      hoặc
    │   ROLLBACK
    │
    └── SAVEPOINT
           ↓
       partial rollback
```

Và architecture:

```text id="summary2"
Use Case
   ↓
Unit of Work
   ↓
BEGIN
   ↓
Repository A
Repository B
Repository C
   ↓
COMMIT
   │
   └── exception → ROLLBACK
```

Đặc biệt nhớ:

> **Repository thực hiện persistence operation; Unit of Work quyết định transaction boundary.**

Và với crawler:

> **Không giữ transaction trong lúc chờ HTTP/network. Hãy crawl/parse trước, sau đó mở transaction ngắn để ghi SQLite.**

---

# Roadmap

```text id="roadmap1"
Phần IV — SQLite Deep Dive

24. SQLite Type Affinity       ✅
25. Constraints Deep Dive      ✅
26. PRAGMA                     ✅
27. Transaction Deep Dive      ✅

28. WAL
    ├── Write-Ahead Logging
    ├── WAL file
    ├── checkpoint
    ├── reader/writer concurrency
    └── WAL + Python

29. Locking & Concurrency
    ├── database locked
    ├── busy_timeout
    ├── read/write lock
    ├── multiple workers
    └── crawler concurrency

30. SQLite Performance
    ├── EXPLAIN QUERY PLAN
    ├── indexes
    ├── query optimization
    ├── batch insert
    └── production tuning
```

**Buổi 28 — WAL** sẽ nối trực tiếp `Transaction → Journal → WAL → Concurrency`. Đây là phần đặc biệt quan trọng nếu app crawler sau này có **nhiều worker cùng đọc/ghi SQLite**.
