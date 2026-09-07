# Phần IV — SQLite Deep Dive

## Buổi 24 — SQLite Type Affinity

Đây là buổi rất quan trọng nếu bạn muốn dùng **SQLite + Python ở mức production**.

Ở các buổi trước, ta đã nói SQLite có các storage class:

```text
NULL
INTEGER
REAL
TEXT
BLOB
```

Nhưng có một điều dễ gây nhầm:

> **SQLite không áp dụng kiểu dữ liệu của column theo cách nghiêm ngặt như PostgreSQL hay một số hệ CSDL khác.**

Khái niệm đứng sau đó là **Type Affinity**.

---

# 1. Type Affinity là gì?

Trong SQLite, khi bạn khai báo:

```sql
CREATE TABLE novels (
    id INTEGER,
    title TEXT,
    chapter_count INTEGER,
    rating REAL
);
```

ta thường nghĩ:

```text
id            → INTEGER
title         → TEXT
chapter_count → INTEGER
rating        → REAL
```

Nhưng chính xác hơn, SQLite gán cho mỗi column một **type affinity**.

Có 5 affinity chính:

```text
INTEGER
TEXT
REAL
NUMERIC
BLOB
```

Affinity có thể hiểu đơn giản là:

> "Đây là kiểu dữ liệu mà SQLite ưu tiên sử dụng khi lưu giá trị vào column."

Nó **không hoàn toàn giống kiểu dữ liệu strict**.

---

# 2. Storage Class vs Type Affinity

Đây là điểm quan trọng nhất của buổi học.

## Storage Class

Storage class nói về **giá trị thực tế đang được lưu**:

```text
NULL
INTEGER
REAL
TEXT
BLOB
```

Ví dụ:

```sql
INSERT INTO novels (chapter_count)
VALUES (100);
```

Giá trị `100` có storage class:

```text
INTEGER
```

---

## Type Affinity

Type affinity thuộc về **column**.

Ví dụ:

```sql
CREATE TABLE novels (
    chapter_count INTEGER
);
```

Column `chapter_count` có:

```text
INTEGER affinity
```

Có thể hình dung:

```text
Column
   │
   │ type affinity
   ↓
INTEGER affinity
   │
   │ SQLite cố gắng chuyển đổi giá trị phù hợp
   ↓
Stored value
   │
   ↓
INTEGER / REAL / TEXT / ...
```

---

# 3. SQLite khác PostgreSQL ở đâu?

Ví dụ PostgreSQL:

```sql
CREATE TABLE novels (
    chapter_count INTEGER
);
```

Sau đó:

```sql
INSERT INTO novels (chapter_count)
VALUES ('abc');
```

Thông thường database sẽ từ chối.

Nhưng SQLite có cơ chế type affinity linh hoạt hơn.

Ví dụ:

```sql
CREATE TABLE test (
    value INTEGER
);
```

Thử:

```sql
INSERT INTO test(value)
VALUES ('123');
```

SQLite có thể chuyển:

```text
'123'
```

thành:

```text
123
```

và lưu dưới dạng INTEGER.

---

# 4. Ví dụ trực tiếp với Python

```python
import sqlite3

conn = sqlite3.connect(":memory:")

conn.execute("""
    CREATE TABLE test (
        value INTEGER
    )
""")

conn.execute(
    "INSERT INTO test(value) VALUES (?)",
    ("123",)
)

row = conn.execute("""
    SELECT value, typeof(value)
    FROM test
""").fetchone()

print(row)
```

Kết quả có thể là:

```text
(123, 'integer')
```

Điều đáng chú ý:

Python truyền vào:

```python
"123"
```

là `str`.

Nhưng SQLite lưu:

```text
123
```

với storage class:

```text
integer
```

---

# 5. `typeof()` — công cụ cực kỳ quan trọng

SQLite có function:

```sql
typeof(value)
```

Dùng để kiểm tra **storage class thực tế**.

Ví dụ:

```sql
SELECT typeof(123);
```

→

```text
integer
```

---

```sql
SELECT typeof(12.5);
```

→

```text
real
```

---

```sql
SELECT typeof('hello');
```

→

```text
text
```

---

```sql
SELECT typeof(NULL);
```

→

```text
null
```

---

## Python

```python
row = conn.execute("""
    SELECT
        typeof(123),
        typeof(12.5),
        typeof('hello'),
        typeof(NULL)
""").fetchone()

print(row)
```

---

# 6. INTEGER Affinity

Ví dụ:

```sql
CREATE TABLE test (
    value INTEGER
);
```

SQLite sẽ ưu tiên lưu giá trị số nguyên dưới dạng INTEGER.

```sql
INSERT INTO test VALUES (100);
INSERT INTO test VALUES ('200');
INSERT INTO test VALUES (300.5);
```

Kiểm tra:

```sql
SELECT value, typeof(value)
FROM test;
```

Có thể thấy:

```text
100   integer
200   integer
300.5 real
```

Điểm cần nhớ:

> INTEGER affinity không có nghĩa mọi giá trị bắt buộc phải là INTEGER.

---

# 7. TEXT Affinity

Ví dụ:

```sql
CREATE TABLE test (
    value TEXT
);
```

Insert:

```sql
INSERT INTO test VALUES (123);
INSERT INTO test VALUES (12.5);
INSERT INTO test VALUES ('hello');
```

SQLite có xu hướng chuyển dữ liệu thành TEXT.

Kiểm tra:

```sql
SELECT value, typeof(value)
FROM test;
```

Có thể nhận:

```text
'123'   text
'12.5'  text
'hello' text
```

---

# 8. REAL Affinity

Ví dụ:

```sql
CREATE TABLE test (
    value REAL
);
```

Insert:

```sql
INSERT INTO test VALUES (10);
INSERT INTO test VALUES ('20');
INSERT INTO test VALUES (12.5);
```

SQLite có xu hướng lưu dưới dạng REAL:

```text
10     real
20     real
12.5   real
```

---

# 9. NUMERIC Affinity

NUMERIC hơi đặc biệt.

Ví dụ:

```sql
CREATE TABLE test (
    value NUMERIC
);
```

SQLite cố gắng xác định giá trị phù hợp.

Ví dụ:

```sql
INSERT INTO test VALUES ('100');
INSERT INTO test VALUES ('12.5');
INSERT INTO test VALUES ('hello');
```

Kết quả có thể:

```text
100    integer
12.5   real
hello  text
```

NUMERIC rất hữu ích khi column có thể chứa dữ liệu số ở nhiều dạng.

---

# 10. BLOB Affinity

Nếu khai báo:

```sql
CREATE TABLE test (
    value BLOB
);
```

SQLite ít cố gắng chuyển đổi dữ liệu.

BLOB thường được dùng cho dữ liệu binary:

```text
image
audio
PDF
raw bytes
```

Ví dụ Python:

```python
data = b"\x01\x02\x03\x04"

conn.execute(
    "INSERT INTO test(value) VALUES (?)",
    (data,)
)
```

---

# 11. Cách SQLite xác định affinity

Đây là phần hơi advanced.

SQLite không yêu cầu bạn phải viết đúng 5 tên:

```text
INTEGER
TEXT
REAL
NUMERIC
BLOB
```

Bạn có thể khai báo:

```sql
VARCHAR(255)
```

hoặc:

```sql
BOOLEAN
```

hoặc:

```sql
DATETIME
```

hoặc:

```sql
DECIMAL(10,2)
```

SQLite sẽ **suy ra affinity từ tên type declaration**.

---

# 12. Ví dụ `VARCHAR(255)`

```sql
CREATE TABLE test (
    name VARCHAR(255)
);
```

SQLite coi column này có:

```text
TEXT affinity
```

`255` không tạo ra giới hạn 255 ký tự theo kiểu strict.

Đây là một khác biệt quan trọng.

Trong SQLite:

```sql
VARCHAR(255)
```

không đồng nghĩa với:

```text
maximum 255 characters
```

---

# 13. `BOOLEAN` trong SQLite

Bạn có thể viết:

```sql
CREATE TABLE novels (
    is_completed BOOLEAN
);
```

Nhưng SQLite không có storage class BOOLEAN riêng.

Thông thường:

```text
TRUE  → 1
FALSE → 0
```

Ví dụ:

```sql
INSERT INTO novels(is_completed)
VALUES (TRUE);
```

Kiểm tra:

```sql
SELECT is_completed, typeof(is_completed)
FROM novels;
```

Có thể nhận:

```text
1 | integer
```

Trong Python:

```python
bool_value = bool(row["is_completed"])
```

---

# 14. `DATE` và `DATETIME`

SQLite cũng không có storage class:

```text
DATE
DATETIME
TIMESTAMP
```

theo nghĩa storage class riêng.

Bạn thường lưu datetime dưới dạng:

### TEXT

```text
2026-09-08 10:30:00
```

### INTEGER

Unix timestamp:

```text
1788863400
```

### REAL

Julian day number.

Trong ứng dụng Python + SQLite, tôi thường khuyên:

```text
TEXT
```

với format ISO 8601.

Ví dụ:

```sql
created_at TEXT NOT NULL
```

Python:

```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

value = now.isoformat()
```

Ví dụ:

```text
2026-09-08T03:30:00+00:00
```

---

# 15. Một vấn đề rất dễ gặp trong app crawler

Giả sử bạn thiết kế:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    chapter_number INTEGER NOT NULL
);
```

Bạn nghĩ:

```text
chapter_number
      ↓
INTEGER
```

Sau đó crawler nhận dữ liệu:

```python
chapter_number = "100"
```

SQLite có thể chuyển thành:

```text
100
```

Điều này thường tốt.

Nhưng nếu crawler nhận:

```python
chapter_number = "100abc"
```

thì SQLite có thể lưu dưới dạng TEXT thay vì báo lỗi strict như bạn mong đợi.

Đây là lý do:

> **SQLite type affinity không thay thế validation ở application/domain layer.**

---

# 16. Database constraint và application validation

Đây là tư duy rất quan trọng đối với architecture mà chúng ta đang học.

Ví dụ:

```text
Crawler
   ↓
Application validation
   ↓
Repository
   ↓
SQLite constraints
```

Không nên nghĩ:

```text
SQLite sẽ validate tất cả.
```

Mà nên chia trách nhiệm:

### Python / Domain

Kiểm tra:

```text
chapter_number >= 1
title không rỗng
URL hợp lệ
status hợp lệ
```

### SQLite

Đảm bảo invariant ở database:

```sql
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
PRIMARY KEY
```

Ví dụ:

```sql
chapter_number INTEGER NOT NULL
    CHECK (chapter_number > 0)
```

Đây mạnh hơn rất nhiều so với chỉ:

```sql
chapter_number INTEGER
```

---

# 17. Type Affinity + CHECK

Đây là cách rất tốt để tăng độ an toàn.

Ví dụ:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    chapter_number INTEGER NOT NULL
        CHECK (chapter_number > 0),

    title TEXT NOT NULL
);
```

Bây giờ database có thêm invariant:

```text
chapter_number > 0
```

---

## Status

Thay vì:

```sql
status TEXT
```

ta có:

```sql
status TEXT NOT NULL
    CHECK (
        status IN ('ongoing', 'completed')
    )
```

Điều này chúng ta đã dùng ở các buổi trước.

---

# 18. Một ví dụ rất đáng nhớ

Hãy thử:

```sql
CREATE TABLE test (
    value INTEGER
);
```

Sau đó:

```sql
INSERT INTO test(value) VALUES ('123');
INSERT INTO test(value) VALUES ('abc');
```

Kiểm tra:

```sql
SELECT
    value,
    typeof(value)
FROM test;
```

Bạn có thể nhận:

```text
123   integer
abc   text
```

Đây chính là bản chất của affinity.

Column:

```text
INTEGER affinity
```

không đồng nghĩa:

```text
mọi value bắt buộc INTEGER
```

---

# 19. Đây là nơi SQLite khác tư duy "strict schema"

Ta có:

```text
PostgreSQL
    ↓
type declaration
    ↓
strict typing
```

Trong khi SQLite thiên về:

```text
SQLite
    ↓
type affinity
    ↓
attempt conversion
    ↓
storage class
```

Có thể hình dung:

```text
            Column
              │
              ▼
        Type Affinity
              │
              ▼
       SQLite conversion
              │
              ▼
       Storage Class
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
   INTEGER   REAL   TEXT
```

---

# 20. Nhưng SQLite vẫn rất mạnh

Không nên hiểu rằng:

> "SQLite không strict nên không an toàn."

Không phải.

SQLite vẫn có:

```text
PRIMARY KEY
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
```

và còn có:

```text
STRICT TABLE
```

Đây là một tính năng rất đáng chú ý.

---

# 21. STRICT Tables

SQLite hiện đại hỗ trợ:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL
) STRICT;
```

`STRICT` làm schema chặt chẽ hơn.

Ví dụ:

```sql
INSERT INTO chapters (
    chapter_number,
    title
)
VALUES (
    'abc',
    'Chapter 1'
);
```

có thể bị từ chối thay vì âm thầm lưu TEXT.

Đây là lựa chọn rất đáng cân nhắc cho các schema mới nếu bạn muốn SQLite có behavior gần với strict typing hơn.

---

# 22. Khi nào nên dùng STRICT?

Với app của bạn, tôi nghiêng về:

```sql
CREATE TABLE novels (
    ...
) STRICT;
```

và:

```sql
CREATE TABLE chapters (
    ...
) STRICT;
```

đặc biệt với:

```text
id
chapter_number
created_at
updated_at
status
```

Tuy nhiên, vẫn cần:

```text
Python validation
+
SQLite constraints
```

`STRICT` không thay thế business validation.

---

# 23. Thiết kế schema crawler tốt hơn

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    url TEXT NOT NULL UNIQUE,

    status TEXT NOT NULL
        CHECK (status IN ('ongoing', 'completed')),

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

    title TEXT NOT NULL,
    content TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
) STRICT;
```

Đây đã khá gần một schema production.

---

# 24. Python `sqlite3` và type conversion

Một chiều khác cũng rất quan trọng:

```text
Python → SQLite
```

và:

```text
SQLite → Python
```

Ví dụ:

```python
conn.execute(
    "INSERT INTO chapters(chapter_number) VALUES (?)",
    (100,)
)
```

Python:

```text
int
```

SQLite:

```text
INTEGER
```

Khi đọc:

```python
row = conn.execute("""
    SELECT chapter_number
    FROM chapters
""").fetchone()
```

Python thường nhận:

```python
int
```

---

## Một số mapping phổ biến

```text
Python              SQLite

None       →        NULL
int        →        INTEGER
float      →        REAL
str        →        TEXT
bytes      →        BLOB
```

Đây là nền tảng rất quan trọng cho các buổi sau về `sqlite3`.

---

# 25. Một bài thực hành rất quan trọng

Hãy chạy chương trình này:

```python
import sqlite3

conn = sqlite3.connect(":memory:")

conn.execute("""
    CREATE TABLE test (
        integer_value INTEGER,
        text_value TEXT,
        real_value REAL,
        numeric_value NUMERIC,
        blob_value BLOB
    )
""")

conn.execute("""
    INSERT INTO test VALUES (?, ?, ?, ?, ?)
""", (
    "123",
    123,
    "12.5",
    "100",
    b"hello",
))

row = conn.execute("""
    SELECT
        integer_value,
        typeof(integer_value),

        text_value,
        typeof(text_value),

        real_value,
        typeof(real_value),

        numeric_value,
        typeof(numeric_value),

        blob_value,
        typeof(blob_value)

    FROM test
""").fetchone()

print(row)

conn.close()
```

Hãy quan sát:

```text
Python type
     ↓
SQLite affinity
     ↓
SQLite storage class
```

---

# 26. Bài tập nâng cao

## Bài 1

Tạo:

```sql
CREATE TABLE test (
    value INTEGER
);
```

Thử insert:

```text
100
100.5
'100'
'100.5'
'abc'
NULL
```

Sau đó:

```sql
SELECT value, typeof(value)
FROM test;
```

Tự ghi lại kết quả.

---

## Bài 2

Tạo:

```sql
CREATE TABLE test (
    value TEXT
);
```

Thử:

```text
100
100.5
'abc'
NULL
```

Quan sát `typeof()`.

---

## Bài 3

Tạo bảng:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    chapter_number INTEGER NOT NULL
);
```

Hãy thử:

```text
chapter_number = 100
chapter_number = '100'
chapter_number = 'abc'
```

Sau đó giải thích:

> Tại sao `INTEGER` không đảm bảo tuyệt đối rằng mọi dữ liệu đều là integer?

---

# 27. Bài tập architecture

Đây mới là bài quan trọng nhất.

Thiết kế:

```text
Crawler
   ↓
ChapterParser
   ↓
Chapter Entity
   ↓
Repository
   ↓
SQLite
```

Với các invariant:

```text
chapter_number > 0
title != ""
novel_id phải tồn tại
mỗi novel không có chapter_number trùng
```

Hãy xác định invariant nào nằm ở đâu:

| Invariant                         |          Python |                  SQLite |
| --------------------------------- | --------------: | ----------------------: |
| chapter_number > 0                |               ✅ |                   CHECK |
| title không rỗng                  |               ✅ | NOT NULL + có thể CHECK |
| novel_id tồn tại                  | có thể validate |             FOREIGN KEY |
| chapter_number unique trong novel | có thể kiểm tra |                  UNIQUE |
| status hợp lệ                     | có thể validate |                   CHECK |

Đây chính là tư duy **defense in depth**:

```text
Domain validation
       +
Database constraints
       +
SQLite type enforcement
```

---

# 28. Những điều cần nhớ sau Buổi 24

Nếu chỉ nhớ **6 điểm**, hãy nhớ:

### 1.

SQLite có:

```text
Storage Class
NULL
INTEGER
REAL
TEXT
BLOB
```

### 2.

Column có:

```text
Type Affinity
```

chứ không đơn giản là strict type như nhiều DBMS khác.

### 3.

`INTEGER` affinity không có nghĩa:

```text
mọi value bắt buộc INTEGER
```

### 4.

Dùng:

```sql
typeof(column)
```

để kiểm tra storage class thực tế.

### 5.

SQLite không có storage class riêng cho:

```text
BOOLEAN
DATE
DATETIME
```

### 6.

Với application thực tế:

```text
Python validation
       +
SQLite constraints
       +
STRICT table nếu phù hợp
```

là cách thiết kế tốt.

---

# Roadmap tiếp theo

```text
Phần IV — SQLite Deep Dive

24. SQLite Type Affinity       ✅

25. Constraints Deep Dive
    ├── PRIMARY KEY
    ├── UNIQUE
    ├── NOT NULL
    ├── CHECK
    ├── FOREIGN KEY
    ├── Constraint interaction
    └── Design invariant

26. PRAGMA

27. Transaction Deep Dive

28. WAL

29. Locking & Concurrency

30. SQLite Performance
```

**Buổi 25 sẽ rất quan trọng:** ta sẽ đi sâu vào **Constraints**, không chỉ học cú pháp mà sẽ học cách dùng `PRIMARY KEY + UNIQUE + NOT NULL + CHECK + FOREIGN KEY` để biến **business invariant thành database invariant**.
