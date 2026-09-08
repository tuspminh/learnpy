s# Phần IV — SQLite Deep Dive

# Buổi 25 — Constraints Deep Dive

Ở Buổi 24, ta học **Type Affinity**.

Hôm nay đi vào phần quan trọng hơn:

> **Database Constraint — dùng database để bảo vệ tính đúng đắn của dữ liệu.**

Đây là nền tảng để sau này thiết kế:

```text
Entity
   ↓
Domain Invariant
   ↓
Database Constraint
```

đặc biệt hữu ích cho app **crawler truyện + SQLite + Repository + Unit of Work** của bạn.

---

# 1. Constraint là gì?

Constraint = một **quy tắc mà database bắt buộc dữ liệu phải tuân theo**.

Ví dụ:

```text
Novel phải có title
Novel URL không được trùng
Chapter phải thuộc một Novel
Chapter number > 0
Một Novel không được có chapter 1 hai lần
```

Nếu chỉ kiểm tra bằng Python:

```python
if not title:
    raise ValueError(...)
```

thì vẫn có khả năng một đoạn code khác ghi trực tiếp vào database và phá vỡ invariant.

Database constraint tạo thêm một lớp bảo vệ:

```text
Application
    ↓
Validation
    ↓
Repository
    ↓
SQLite Constraint
    ↓
Database
```

---

# 2. Sáu constraint quan trọng

Trong SQLite, chúng ta đặc biệt quan tâm:

```text
PRIMARY KEY
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
DEFAULT
```

Có thể chia thành:

```text
Identity
├── PRIMARY KEY

Required
├── NOT NULL

Uniqueness
├── UNIQUE

Value rule
├── CHECK

Relationship
├── FOREIGN KEY

Default value
└── DEFAULT
```

---

# 3. PRIMARY KEY

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

`id` xác định một row.

```text
Novel
┌────┬─────────────┐
│ id │ title       │
├────┼─────────────┤
│ 1  │ Tiên Nghịch │
│ 2  │ Phàm Nhân   │
│ 3  │ Đấu Phá     │
└────┴─────────────┘
```

Không được có:

```text
id = 1
id = 1
```

---

# 4. `INTEGER PRIMARY KEY` đặc biệt trong SQLite

Đây là một điểm rất quan trọng.

```sql
id INTEGER PRIMARY KEY
```

không chỉ là một constraint thông thường.

Trong SQLite, `INTEGER PRIMARY KEY` gắn với `rowid`.

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Insert:

```python
cursor = conn.execute(
    """
    INSERT INTO novels(title)
    VALUES (?)
    """,
    ("Tiên Nghịch",),
)

print(cursor.lastrowid)
```

SQLite tự cấp:

```text
1
```

---

# 5. PRIMARY KEY và NULL

Với:

```sql
id INTEGER PRIMARY KEY
```

ta thường không cần tự truyền `id`.

```sql
INSERT INTO novels(title)
VALUES ('Tiên Nghịch');
```

SQLite tạo ID.

Đây là pattern rất phù hợp với app của chúng ta:

```text
Python
   ↓
INSERT novel
   ↓
SQLite generate id
   ↓
lastrowid
   ↓
insert chapters
```

---

# 6. NOT NULL

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Không được:

```sql
INSERT INTO novels(title)
VALUES (NULL);
```

SQLite sẽ báo lỗi:

```text
NOT NULL constraint failed
```

Trong Python:

```python
try:
    conn.execute(
        "INSERT INTO novels(title) VALUES (?)",
        (None,),
    )
except sqlite3.IntegrityError as exc:
    print(exc)
```

---

# 7. NOT NULL không có nghĩa "không rỗng"

Đây là một lỗi tư duy rất phổ biến.

```sql
title TEXT NOT NULL
```

chặn:

```sql
NULL
```

nhưng không chặn:

```text
''
'   '
```

Ví dụ:

```sql
INSERT INTO novels(title)
VALUES ('');
```

vẫn có thể hợp lệ.

Nếu business rule là:

> title phải có ít nhất một ký tự thực sự

thì có thể dùng:

```sql
title TEXT NOT NULL
    CHECK (length(trim(title)) > 0)
```

Đây là ví dụ rất hay về:

```text
NOT NULL
+
CHECK
```

---

# 8. UNIQUE

Ví dụ crawler:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL
);
```

Không thể có:

```text
url = https://site.com/tien-nghich
url = https://site.com/tien-nghich
```

SQLite sẽ báo:

```text
UNIQUE constraint failed
```

Điều này cực kỳ hữu ích cho crawler.

Thay vì:

```python
if repository.exists(url):
    ...
else:
    insert(...)
```

ta vẫn nên có:

```sql
url TEXT NOT NULL UNIQUE
```

vì kiểm tra Python riêng lẻ có thể gặp race condition.

---

# 9. UNIQUE là database invariant

Ví dụ:

```text
Crawler A
   ↓
check URL chưa tồn tại

Crawler B
   ↓
check URL chưa tồn tại
```

Cả hai cùng thấy:

```text
không tồn tại
```

rồi cùng insert.

Nếu chỉ dựa vào Python:

```text
duplicate
```

Nhưng nếu database có:

```sql
UNIQUE(url)
```

thì database vẫn bảo vệ được invariant.

```text
Crawler A ─┐
           ├──→ SQLite UNIQUE → chỉ một row hợp lệ
Crawler B ─┘
```

Đây là lý do constraint không nên chỉ được xem là "validation".

---

# 10. UNIQUE nhiều column

Đây là một trong những constraint quan trọng nhất với schema truyện.

Ta có:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,

    UNIQUE(novel_id, chapter_number)
);
```

Ý nghĩa:

> Trong cùng một novel, chapter_number không được trùng.

Cho phép:

```text
Novel 1 → Chapter 1
Novel 1 → Chapter 2

Novel 2 → Chapter 1
Novel 2 → Chapter 2
```

Nhưng không cho:

```text
Novel 1 → Chapter 1
Novel 1 → Chapter 1
```

---

# 11. Vì sao không `UNIQUE(chapter_number)`?

Nếu viết:

```sql
UNIQUE(chapter_number)
```

thì:

```text
Novel A → chapter 1
Novel B → chapter 1
```

sẽ bị coi là duplicate.

Sai business rule.

Ta cần:

```sql
UNIQUE(novel_id, chapter_number)
```

Đây là **composite uniqueness**.

---

# 12. CHECK

`CHECK` dùng để biểu diễn điều kiện dữ liệu.

Ví dụ:

```sql
chapter_number INTEGER NOT NULL
    CHECK (chapter_number > 0)
```

Không cho:

```text
0
-1
-100
```

---

## Status

```sql
status TEXT NOT NULL
    CHECK (
        status IN ('ongoing', 'completed')
    )
```

Không cho:

```text
'abc'
'finished'
'unknown'
```

---

# 13. CHECK nhiều điều kiện

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    status TEXT NOT NULL
        CHECK (
            status IN ('ongoing', 'completed')
        )
);
```

Ta đang chuyển business rule thành database rule:

```text
title không rỗng
        ↓
CHECK

status phải hợp lệ
        ↓
CHECK
```

---

# 14. CHECK và NULL

Đây là phần khá tinh tế.

`CHECK` không đơn giản chỉ có:

```text
TRUE / FALSE
```

SQLite có logic ba giá trị:

```text
TRUE
FALSE
NULL/UNKNOWN
```

Ví dụ:

```sql
CHECK (chapter_number > 0)
```

Nếu:

```text
chapter_number = NULL
```

thì biểu thức:

```text
NULL > 0
```

không phải FALSE mà là UNKNOWN.

Vì vậy nếu muốn bắt buộc có giá trị:

```sql
chapter_number INTEGER NOT NULL
    CHECK (chapter_number > 0)
```

nên kết hợp:

```text
NOT NULL
+
CHECK
```

---

# 15. FOREIGN KEY

Ta đã học ở Buổi 14.

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nó đảm bảo:

```text
chapters.novel_id
       ↓
phải tham chiếu
       ↓
novels.id tồn tại
```

Ví dụ:

```text
novels
id
1
2

chapters
novel_id
1   ← OK
2   ← OK
99  ← ERROR
```

---

# 16. FOREIGN KEY cần bật trong SQLite

Nhớ kỹ:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

Nếu không cấu hình đúng connection, bạn có thể tưởng rằng FK đang bảo vệ database trong khi thực tế không như mong đợi.

Connection Manager của chúng ta nên làm việc này:

```python
class ConnectionManager:
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect("novel.db")

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")

        return conn
```

Buổi 26 chúng ta sẽ học `PRAGMA` thật sâu.

---

# 17. DEFAULT

Ví dụ:

```sql
status TEXT NOT NULL DEFAULT 'ongoing'
```

Khi:

```sql
INSERT INTO novels(title)
VALUES ('Tiên Nghịch');
```

SQLite tự dùng:

```text
status = ongoing
```

`DEFAULT` không phải validation.

Nó chỉ nói:

> Nếu INSERT không cung cấp giá trị thì dùng giá trị này.

---

# 18. DEFAULT + CHECK

Hai cái có thể phối hợp:

```sql
status TEXT NOT NULL
    DEFAULT 'ongoing'
    CHECK (
        status IN ('ongoing', 'completed')
    )
```

Có nghĩa:

```text
Không truyền status
        ↓
ongoing

Truyền completed
        ↓
OK

Truyền abc
        ↓
CHECK fail
```

---

# 19. Constraint có thể kết hợp

Đây mới là tư duy quan trọng.

Ví dụ:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL
        CHECK (chapter_number > 0),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
);
```

Mỗi constraint có một trách nhiệm:

```text
PRIMARY KEY
    ↓
Identity

NOT NULL
    ↓
Required

CHECK
    ↓
Value invariant

FOREIGN KEY
    ↓
Relationship integrity

UNIQUE
    ↓
Uniqueness
```

---

# 20. Constraint không thay thế Domain Model

Đây là điểm cực kỳ quan trọng với kiến trúc mà chúng ta đang học.

Ví dụ:

```python
@dataclass
class Chapter:
    novel_id: int
    chapter_number: int
    title: str
```

Domain có thể validate:

```python
if chapter_number <= 0:
    raise ValueError(...)
```

Database cũng có:

```sql
CHECK (chapter_number > 0)
```

Có vẻ như đang kiểm tra hai lần.

Đúng.

Và đó là điều tốt.

---

# 21. Defense in Depth

Kiến trúc tốt:

```text
                Domain
                  │
           Business rules
                  │
                  ▼
              Application
                  │
            Use Case
                  │
                  ▼
             Repository
                  │
                  ▼
               SQLite
                  │
          Database constraints
```

Nếu một bug lọt qua:

```text
Domain
```

database vẫn có thể chặn.

Đây là:

> **Defense in Depth**

---

# 22. Một schema production-style cho app của bạn

Ta có thể bắt đầu với:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,

    source TEXT NOT NULL
        CHECK (length(trim(source)) > 0),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    author TEXT,

    url TEXT NOT NULL UNIQUE,

    status TEXT NOT NULL
        DEFAULT 'ongoing'
        CHECK (
            status IN ('ongoing', 'completed')
        ),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
) STRICT;
```

Và:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL
        CHECK (chapter_number > 0),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    content TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
) STRICT;
```

Đây là một schema khá tốt để tiếp tục phát triển.

---

# 23. Constraint violation trong Python

Tất cả constraint violation thường được `sqlite3` báo thông qua:

```python
sqlite3.IntegrityError
```

Ví dụ:

```python
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
        (999, 1, "Chapter 1"),
    )

except sqlite3.IntegrityError as exc:
    print(exc)
```

Có thể nhận:

```text
FOREIGN KEY constraint failed
```

---

# 24. Repository nên xử lý thế nào?

Ví dụ:

```python
class ChapterRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(
        self,
        novel_id: int,
        chapter_number: int,
        title: str,
    ) -> int:

        cursor = self._conn.execute(
            """
            INSERT INTO chapters(
                novel_id,
                chapter_number,
                title
            )
            VALUES (?, ?, ?)
            """,
            (
                novel_id,
                chapter_number,
                title,
            ),
        )

        return cursor.lastrowid
```

Repository không cần tự kiểm tra mọi thứ:

```python
if duplicate:
    ...
```

Database vẫn có:

```sql
UNIQUE(novel_id, chapter_number)
```

---

# 25. Nhưng có nên bắt `IntegrityError` rồi đổi thành Domain Exception?

Trong architecture lớn, có thể.

Ví dụ:

```python
class DuplicateChapterError(Exception):
    pass
```

Repository:

```python
try:
    cursor = self._conn.execute(...)
except sqlite3.IntegrityError as exc:
    raise DuplicateChapterError(...) from exc
```

Khi đó Application layer không cần biết:

```text
sqlite3.IntegrityError
```

Nó chỉ biết:

```text
DuplicateChapterError
```

Đây là chủ đề chúng ta sẽ gặp sâu hơn khi học:

```text
Repository Pattern
Unit of Work
Clean Architecture
DDD
```

---

# 26. Một lỗi thiết kế thường gặp

❌ Không tốt:

```python
if not repository.exists(url):
    repository.create(url)
```

và database:

```sql
url TEXT
```

Không có:

```sql
UNIQUE(url)
```

Tốt hơn:

```python
repository.create(url)
```

và database:

```sql
url TEXT NOT NULL UNIQUE
```

Application có thể kiểm tra trước để UX tốt hơn, nhưng **database vẫn là lớp bảo vệ cuối cùng**.

---

# 27. Constraint matrix

Hãy học thuộc bảng này:

| Constraint  | Bảo vệ điều gì?             |
| ----------- | --------------------------- |
| PRIMARY KEY | Identity                    |
| NOT NULL    | Không được thiếu giá trị    |
| UNIQUE      | Không được trùng            |
| CHECK       | Giá trị phải thỏa điều kiện |
| FOREIGN KEY | Quan hệ phải hợp lệ         |
| DEFAULT     | Giá trị mặc định            |

Ví dụ với `Chapter`:

```text
id
 ↓
PRIMARY KEY

novel_id
 ↓
NOT NULL + FOREIGN KEY

chapter_number
 ↓
NOT NULL + CHECK

title
 ↓
NOT NULL + CHECK

(novel_id, chapter_number)
 ↓
UNIQUE
```

Đây chính là cách tôi muốn bạn bắt đầu **thiết kế database từ invariant**, thay vì chỉ nghĩ đến column.

---

# 28. Tư duy quan trọng: Column → Rule

Đừng chỉ hỏi:

> "Bảng này có những column nào?"

Hãy hỏi:

> "Dữ liệu này phải luôn đúng theo những quy tắc nào?"

Ví dụ:

### Novel

```text
Novel phải có title
Novel URL không được trùng
Status chỉ có ongoing/completed
```

↓

```sql
title TEXT NOT NULL

url TEXT NOT NULL UNIQUE

status TEXT NOT NULL
CHECK (...)
```

### Chapter

```text
Chapter phải thuộc Novel
Chapter number > 0
Một Novel không có chapter number trùng
```

↓

```sql
novel_id INTEGER NOT NULL

FOREIGN KEY (...)

CHECK (chapter_number > 0)

UNIQUE(novel_id, chapter_number)
```

Đây là cách thiết kế schema chuyên nghiệp hơn rất nhiều.

---

# 29. Bài tập thực hành

## Bài 1 — Novel

Viết schema:

```text
novels

id
source
title
url
status
```

Yêu cầu:

```text
id        → PK
source    → bắt buộc
title     → bắt buộc, không rỗng
url       → bắt buộc, unique
status    → ongoing/completed
```

---

## Bài 2 — Chapter

Thiết kế:

```text
chapters

id
novel_id
chapter_number
title
content
```

Yêu cầu:

```text
id
    → PRIMARY KEY

novel_id
    → NOT NULL + FOREIGN KEY

chapter_number
    → NOT NULL + CHECK > 0

title
    → NOT NULL + không rỗng

(novel_id, chapter_number)
    → UNIQUE
```

---

# 30. Bài tập quan trọng nhất

Cho các business rule:

```text
R1: Novel phải có title

R2: URL novel không được trùng

R3: Status chỉ có ongoing/completed

R4: Chapter phải thuộc một Novel

R5: Chapter number > 0

R6: Một Novel không có hai chapter cùng number
```

Hãy tự map:

```text
R1 → ?
R2 → ?
R3 → ?
R4 → ?
R5 → ?
R6 → ?
```

Đáp án:

```text
R1 → NOT NULL + CHECK
R2 → UNIQUE
R3 → CHECK
R4 → FOREIGN KEY + NOT NULL
R5 → CHECK
R6 → UNIQUE(novel_id, chapter_number)
```

Nếu bạn hiểu được bài này, bạn đã bắt đầu chuyển từ:

```text
"Học SQL"
```

sang:

```text
"Thiết kế database"
```

---

# 31. Tổng kết Buổi 25

Mental model cần nhớ:

```text
Constraint
    │
    ├── PRIMARY KEY
    │      → Tôi là ai?
    │
    ├── NOT NULL
    │      → Tôi bắt buộc phải có
    │
    ├── UNIQUE
    │      → Tôi không được trùng
    │
    ├── CHECK
    │      → Tôi phải thỏa điều kiện
    │
    ├── FOREIGN KEY
    │      → Tôi phải thuộc quan hệ hợp lệ
    │
    └── DEFAULT
           → Nếu không cung cấp thì dùng giá trị này
```

Và kiến trúc:

```text
Domain
   ↓
Business Invariant
   ↓
Application Validation
   ↓
Repository
   ↓
Database Constraint
   ↓
SQLite
```

---

## Roadmap tiếp tục

```text
Phần IV — SQLite Deep Dive

24. SQLite Type Affinity       ✅
25. Constraints Deep Dive      ✅

26. PRAGMA
    ├── foreign_keys
    ├── journal_mode
    ├── synchronous
    ├── busy_timeout
    ├── cache_size
    ├── user_version
    └── integrity_check

27. Transaction Deep Dive
28. WAL
29. Locking & Concurrency
30. SQLite Performance
```

**Buổi 26 — PRAGMA** sẽ là bước rất đáng học: ta sẽ không chỉ biết `PRAGMA foreign_keys = ON`, mà sẽ xây một **SQLite Connection Manager chuẩn**, cấu hình `foreign_keys`, `journal_mode`, `synchronous`, `busy_timeout`, kiểm tra integrity và chuẩn bị nền móng cho **Unit of Work**.
