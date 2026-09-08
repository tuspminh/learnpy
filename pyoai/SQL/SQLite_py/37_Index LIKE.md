# Buổi 37 — Index + LIKE

Hôm nay chúng ta đi vào một vấn đề **rất quan trọng với app đọc/cào truyện**:

```sql
WHERE title LIKE ?
```

Bạn sẽ hiểu:

* `%` và `_`
* `LIKE 'abc%'`
* `LIKE '%abc%'`
* tại sao prefix search có thể dùng B-tree
* tại sao `%keyword%` thường không dùng B-tree hiệu quả
* `LIKE` + Composite Index
* `LIKE` + Python
* case sensitivity
* khi nào dùng B-tree
* khi nào nên chuyển sang **FTS5**

---

# 1. LIKE là gì?

`LIKE` dùng để tìm chuỗi theo pattern.

Ví dụ:

```sql
SELECT *
FROM novels
WHERE title LIKE 'Tiên%';
```

Nghĩa là:

```text
Tiên
Tiên Nghịch
Tiên Hiệp
Tiên Đạo
...
```

---

# 2. Hai wildcard quan trọng

SQLite `LIKE` có hai wildcard chính:

```text
%    → zero hoặc nhiều ký tự
_    → đúng một ký tự
```

Ví dụ:

```sql
LIKE 'Tiên%'
```

match:

```text
Tiên
Tiên Nghịch
Tiên Đạo
Tiên Hiệp
```

---

Ví dụ:

```sql
LIKE '_iên'
```

có thể match:

```text
Tiên
```

vì `_` đại diện cho một ký tự.

---

# 3. Ba kiểu LIKE quan trọng nhất

Giả sử:

```text
title
----------------
Tiên Nghịch
Tiên Đạo
Phàm Nhân Tu Tiên
Đấu Phá Thương Khung
```

### Prefix

```sql
WHERE title LIKE 'Tiên%'
```

Nghĩa:

```text
bắt đầu bằng "Tiên"
```

---

### Suffix

```sql
WHERE title LIKE '%Tiên'
```

Nghĩa:

```text
kết thúc bằng "Tiên"
```

---

### Contains

```sql
WHERE title LIKE '%Tiên%'
```

Nghĩa:

```text
chứa "Tiên" ở bất kỳ vị trí nào
```

Ba pattern này có hiệu năng rất khác nhau.

---

# 4. B-tree rất thích dữ liệu có thứ tự

Nhắc lại Buổi 32.

Index:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

B-tree có dữ liệu được sắp xếp:

```text
...
Đấu ...
Phàm ...
Tiên ...
Tiên Đạo
Tiên Nghịch
Tiên Hiệp
...
```

SQLite có thể tận dụng thứ tự này để tìm một **khoảng**.

Ví dụ:

```text
Tiên%
```

có thể hiểu trực quan là:

```text
"Tất cả chuỗi bắt đầu bằng Tiên"
```

Đây là một vùng có thứ tự trong B-tree.

---

# 5. Prefix Search

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE title LIKE 'Tiên%';
```

Pattern:

```text
Tiên%
^^^^
prefix cố định
```

B-tree có cơ hội rất tốt để hỗ trợ việc tìm vùng này.

Mental model:

```text
B-tree

A
B
C
D
...
Tiên Đạo
Tiên Hiệp
Tiên Nghịch
Tiên ...
...
X
Y
Z
```

Thay vì:

```text
SCAN toàn bộ table
```

SQLite có thể tìm đến vùng:

```text
Tiên...
```

rồi đọc các entries phù hợp.

---

# 6. Nhưng `%Tiên%` thì khác

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE title LIKE '%Tiên%';
```

Pattern:

```text
%Tiên%
^
không biết bắt đầu từ đâu
```

Ví dụ:

```text
Tiên Nghịch
Phàm Nhân Tu Tiên
Đấu Phá...
Cổ Tiên...
```

`Tiên` có thể nằm ở:

```text
vị trí 1
vị trí 5
vị trí 10
vị trí 100
...
```

B-tree không có một prefix cố định để định vị vùng dữ liệu.

Do đó index B-tree thông thường **thường không giúp đáng kể cho `%keyword%`**.

---

# 7. Đây là điểm cần nhớ nhất của Buổi 37

```text
LIKE 'Tiên%'
       ↓
Prefix Search
       ↓
B-tree có thể hữu ích
```

Trong khi:

```text
LIKE '%Tiên%'
       ↓
Contains Search
       ↓
B-tree thông thường không phù hợp
```

Mental model:

```text
'Tiên%'
│
└── biết bắt đầu từ đâu


'%Tiên%'
│
└── không biết bắt đầu từ đâu
```

---

# 8. Suffix Search

Ví dụ:

```sql
WHERE title LIKE '%Nghịch'
```

Tìm:

```text
Tiên Nghịch
...
Nghịch
```

B-tree thông thường không tối ưu trực tiếp cho việc này vì phần đầu là:

```text
%
```

Không có prefix cố định.

---

# 9. Python + LIKE

Đây là cách rất phổ biến:

```python
keyword = "Tiên"

rows = conn.execute(
    """
    SELECT
        id,
        title,
        author
    FROM novels
    WHERE title LIKE ?
    """,
    (f"{keyword}%",),
).fetchall()
```

SQL vẫn:

```sql
LIKE ?
```

Parameter:

```text
Tiên%
```

---

# 10. Không dùng f-string để nhét keyword vào SQL

Sai:

```python
keyword = "Tiên"

sql = f"""
    SELECT *
    FROM novels
    WHERE title LIKE '%{keyword}%'
"""
```

Đừng làm vậy.

Đúng:

```python
keyword = "Tiên"

rows = conn.execute(
    """
    SELECT
        id,
        title
    FROM novels
    WHERE title LIKE ?
    """,
    (f"%{keyword}%",),
).fetchall()
```

Điểm quan trọng:

```text
SQL structure
       ↓
parameter
```

không trộn dữ liệu vào SQL.

---

# 11. LIKE + ORDER BY

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE title LIKE 'Tiên%'
ORDER BY title
LIMIT 50;
```

Index:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Đây là một query pattern rất tự nhiên cho B-tree:

```text
WHERE prefix
      +
ORDER BY same column
```

SQLite có thể tận dụng thứ tự index tùy query plan.

---

# 12. EXPLAIN QUERY PLAN

Đừng đoán.

Chạy:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM novels
WHERE title LIKE 'Tiên%';
```

Sau đó:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

và chạy lại.

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM novels
WHERE title LIKE 'Tiên%';
```

Bạn cần quan sát planner.

Ví dụ về mặt khái niệm:

```text
Before

SCAN novels
```

Sau:

```text
SEARCH novels USING INDEX ...
```

Nhưng **đừng coi đây là kết quả bắt buộc**. Planner còn phụ thuộc SQLite version, collation, `PRAGMA` và query cụ thể.

---

# 13. LIKE + Composite Index

Giả sử:

```text
novels
----------------
source
title
status
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE source = ?
  AND title LIKE 'Tiên%';
```

Candidate:

```sql
CREATE INDEX idx_novels_source_title
ON novels(source, title);
```

Mental model:

```text
(source, title)
       │
       ├── equality
       │
       └── prefix search
```

Đây là pattern rất đáng nhớ:

```text
equality
   ↓
prefix/range
```

---

# 14. Vì sao thứ tự `(source, title)` quan trọng?

Index:

```sql
(source, title)
```

được sắp xếp kiểu:

```text
site_a → Đấu...
site_a → Phàm...
site_a → Tiên...
site_a → Tiên Đạo
site_a → Tiên Nghịch
site_b → Đấu...
site_b → Tiên...
```

Query:

```sql
WHERE source = 'site_a'
  AND title LIKE 'Tiên%'
```

có một vùng rất rõ:

```text
site_a
   └── Tiên...
```

---

# 15. Nếu đảo thành `(title, source)`

```sql
CREATE INDEX idx_novels_title_source
ON novels(title, source);
```

Query:

```sql
WHERE source = ?
  AND title LIKE 'Tiên%';
```

Không nên đơn giản kết luận rằng hai thứ tương đương.

Như đã học ở Buổi 33:

```text
(A, B) ≠ (B, A)
```

Thứ tự column trong Composite Index rất quan trọng.

---

# 16. LIKE + Partial Index

Bây giờ kết hợp Buổi 35.

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE status = 'ongoing'
  AND title LIKE 'Tiên%';
```

Có thể cân nhắc:

```sql
CREATE INDEX idx_ongoing_title
ON novels(title)
WHERE status = 'ongoing';
```

Mental model:

```text
novels
  │
  ├── completed
  │
  └── ongoing
        │
        ▼
    title index
        │
        ▼
     Tiên%
```

Ta đang kết hợp:

```text
Partial Index
+
LIKE Prefix Search
```

---

# 17. LIKE + Partial + Composite

Ví dụ thực tế hơn:

```sql
SELECT
    id,
    title
FROM novels
WHERE status = 'ongoing'
  AND source = ?
  AND title LIKE 'Tiên%'
ORDER BY title
LIMIT 50;
```

Candidate:

```sql
CREATE INDEX idx_ongoing_source_title
ON novels(
    source,
    title
)
WHERE status = 'ongoing';
```

Ta có:

```text
Partial
+
Composite
+
LIKE prefix
+
ORDER BY
```

Đây là kiểu index design mà chúng ta sẽ dần học cách đánh giá ở các buổi tiếp theo.

---

# 18. Case Sensitivity

Một vấn đề rất quan trọng:

```sql
LIKE
```

có behavior liên quan đến case sensitivity trong SQLite.

Đừng thiết kế index dựa trên giả định đơn giản:

```text
LIKE = luôn case-insensitive
```

hoặc:

```text
LIKE = luôn case-sensitive
```

Behavior còn liên quan đến cách SQLite xử lý ASCII/non-ASCII và các thiết lập như `PRAGMA case_sensitive_like`.

Đặc biệt với tiếng Việt:

```text
Tiên
tiên
TIÊN
```

và Unicode là câu chuyện phức tạp hơn ASCII.

---

# 19. Đừng dùng `LOWER()` bừa bãi

Bạn có thể nghĩ:

```sql
WHERE LOWER(title) LIKE LOWER(?)
```

nhưng nhớ lại Buổi 36:

```text
LOWER(title)
```

là một expression.

Nếu muốn tối ưu expression này, có thể phải cân nhắc:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

Nhưng với:

```sql
LOWER(title) LIKE '%tiên%'
```

thì Expression Index vẫn **không biến `%tiên%` thành một prefix search**.

Đây là điểm cực kỳ quan trọng.

```text
Expression Index
       ≠
Full-text search
```

---

# 20. `LOWER(title) LIKE 'tiên%'`

Trường hợp:

```sql
WHERE LOWER(title) LIKE 'tiên%'
```

khác với:

```sql
WHERE LOWER(title) LIKE '%tiên%'
```

Cái đầu có:

```text
prefix cố định
```

Cái sau:

```text
không có prefix cố định
```

Do đó:

```text
LOWER + prefix
```

vẫn là một bài toán có thể cân nhắc B-tree/expression index.

Trong khi:

```text
LOWER + contains
```

thường nên nghĩ tới giải pháp search chuyên dụng.

---

# 21. Khi nào `%keyword%` trở thành vấn đề?

Giả sử app có:

```text
10 triệu novels
```

User nhập:

```text
"tiên"
```

Query:

```sql
WHERE title LIKE '%tiên%'
```

Nếu SQLite phải scan rất nhiều rows:

```text
10,000,000 rows
       ↓
check LIKE
       ↓
check LIKE
       ↓
check LIKE
       ↓
...
```

Đây có thể trở thành bottleneck.

Đặc biệt nếu query còn:

```text
author
description
content
```

thì càng nặng.

---

# 22. Không nên dùng B-tree để làm mọi loại Search

Đây là một tư duy database rất quan trọng:

```text
B-tree
 ↓
Equality
Range
Prefix
Ordering
```

Trong khi:

```text
Full-text search
 ↓
Text search chuyên dụng
```

Không phải cứ:

```sql
LIKE '%keyword%'
```

là phải tìm cách tạo thêm một index B-tree.

---

# 23. FTS5

SQLite có một công cụ rất đáng học:

> **FTS5 — Full-Text Search 5**

Nó được thiết kế cho bài toán tìm kiếm text.

Ví dụ về sau chúng ta có thể xây:

```text
novels
   │
   └── novel_search
          │
          ▼
         FTS5
```

thay vì cố làm:

```sql
LIKE '%keyword%'
```

trên hàng triệu rows.

---

# 24. B-tree vs FTS5

| Nhu cầu               | B-tree |                      FTS5 |
| --------------------- | -----: | ------------------------: |
| `id = ?`              |    ⭐⭐⭐ |                         ❌ |
| `status = ?`          |    ⭐⭐⭐ |                         ❌ |
| `chapter_number > ?`  |    ⭐⭐⭐ |                         ❌ |
| `title LIKE 'Tiên%'`  |    ⭐⭐⭐ |                    Có thể |
| `title LIKE '%Tiên%'` |      ⭐ |                       ⭐⭐⭐ |
| Tìm nhiều từ          |      ⭐ |                       ⭐⭐⭐ |
| Full-text search      |      ❌ |                       ⭐⭐⭐ |
| ORDER BY column       |    ⭐⭐⭐ | Không phải mục tiêu chính |

---

# 25. FTS5 không phải "index LIKE"

Đây là distinction quan trọng.

B-tree:

```text
Index
 ↓
value ordering
 ↓
lookup/range
```

FTS5:

```text
Text
 ↓
tokenization
 ↓
search index
 ↓
matching terms
```

Nó giải quyết bài toán khác.

---

# 26. Search title vs Search content

App đọc truyện có hai loại search rất khác nhau.

### Search title

```sql
WHERE title LIKE 'Tiên%'
```

B-tree rất có thể phù hợp.

### Search nội dung chapter

```text
content chứa "kiếm ý"
```

Nếu database có hàng triệu chapter:

```sql
WHERE content LIKE '%kiếm ý%'
```

thường không phải thiết kế search tốt.

Đây là nơi FTS5 bắt đầu trở nên hấp dẫn.

---

# 27. Python Repository Design

Không nên để UI tự viết:

```python
conn.execute("""
    SELECT ...
    WHERE title LIKE ?
""")
```

Thay vào đó:

```python
class NovelRepository:
    def search_title_prefix(
        self,
        prefix: str,
        limit: int = 50,
    ):
        return self._conn.execute(
            """
            SELECT
                id,
                title,
                author
            FROM novels
            WHERE title LIKE ?
            ORDER BY title
            LIMIT ?
            """,
            (f"{prefix}%", limit),
        ).fetchall()
```

Application:

```text
UI / CLI
   ↓
NovelRepository
   ↓
SQLite
```

---

# 28. Search Repository nên phân biệt loại search

Có thể thiết kế:

```python
class NovelRepository:

    def find_by_exact_title(...):
        ...

    def search_title_prefix(...):
        ...

    def search_title_contains(...):
        ...

    def full_text_search(...):
        ...
```

Tại sao?

Vì:

```text
exact
prefix
contains
full-text
```

là **bốn workload khác nhau**.

Đừng gom tất cả thành:

```python
search(...)
```

rồi bên trong lúc nào cũng:

```sql
LIKE '%keyword%'
```

---

# 29. Một API tốt hơn

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSearch:
    keyword: str
    mode: str = "prefix"
    limit: int = 50
```

Repository:

```python
class NovelRepository:
    def search(self, query: NovelSearch):
        if query.mode == "prefix":
            return self._search_prefix(query)

        if query.mode == "contains":
            return self._search_contains(query)

        raise ValueError("Unsupported search mode")
```

Sau này:

```text
prefix
   ↓
B-tree

contains
   ↓
FTS5 / specialized strategy
```

Đây là nơi kiến thức SQL kết nối với **Strategy Pattern / Repository Pattern** mà bạn đã học trước đây.

---

# 30. Escape `%` và `_`

Có một vấn đề thực tế.

User nhập:

```text
50%
```

Nếu bạn làm:

```python
(f"%{keyword}%",)
```

thì `%` bên trong keyword cũng là wildcard.

Ví dụ:

```text
keyword = "50%"
```

pattern:

```text
%50%%
```

không còn nghĩa là tìm literal `%` nữa.

Nếu cần tìm literal `%` hoặc `_`, phải escape chúng.

SQL có:

```sql
LIKE ? ESCAPE '\'
```

Ví dụ concept:

```sql
WHERE title LIKE ? ESCAPE '\'
```

với pattern đã escape:

```text
%50\%%
```

Đây là một chi tiết nhỏ nhưng rất quan trọng khi xây search API nhận input người dùng.

---

# 31. Hàm escape trong Python

Có thể viết:

```python
def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
```

Sau đó:

```python
keyword = escape_like(user_input)

rows = conn.execute(
    """
    SELECT id, title
    FROM novels
    WHERE title LIKE ? ESCAPE '\\'
    """,
    (f"%{keyword}%",),
).fetchall()
```

Bây giờ:

```text
%
_
```

có thể được tìm như ký tự literal.

---

# 32. Một nuance về `%`

Nếu bạn dùng:

```python
f"%{keyword}%"
```

thì bạn **cố tình yêu cầu contains search**.

Đây là khác biệt:

```python
f"{keyword}%"
```

→ prefix

```python
f"%{keyword}%"
```

→ contains

```python
f"%{keyword}"
```

→ suffix

Có thể ghi nhớ:

```text
keyword%
   ↓
starts with

%keyword
   ↓
ends with

%keyword%
   ↓
contains
```

---

# 33. LIKE + LIMIT

Nếu UI autocomplete:

```text
User gõ:
"Tiê"
```

ta thường chỉ cần:

```sql
SELECT
    id,
    title
FROM novels
WHERE title LIKE ?
ORDER BY title
LIMIT 20;
```

Python:

```python
rows = conn.execute(
    """
    SELECT
        id,
        title
    FROM novels
    WHERE title LIKE ?
    ORDER BY title
    LIMIT ?
    """,
    (f"{prefix}%", 20),
).fetchall()
```

Đây là một workload rất phù hợp với prefix search.

---

# 34. Index cho autocomplete

Query:

```sql
WHERE title LIKE 'Tiê%'
ORDER BY title
LIMIT 20
```

Candidate:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Mental model:

```text
User types
   ↓
"Tiê"
   ↓
"Tiê%"
   ↓
B-tree
   ↓
first 20 matches
```

Đây là một use case tốt hơn nhiều so với:

```sql
LIKE '%Tiê%'
```

nếu UX có thể chấp nhận prefix search.

---

# 35. Một chiến lược UX rất hay

Thay vì:

```text
User gõ:
"nghịch"
```

và luôn chạy:

```sql
LIKE '%nghịch%'
```

có thể UI cho phép:

```text
Search mode:

○ Starts with
○ Contains
○ Full text
```

Khi đó:

```text
Starts with
    ↓
B-tree


Contains
    ↓
FTS / specialized search


Full text
    ↓
FTS5
```

Database và UI cùng hỗ trợ nhau.

---

# 36. B-tree không chỉ dành cho `=`

Sau Buổi 37, đừng có mental model sai:

```text
Index chỉ dùng cho:
WHERE id = ?
```

B-tree có thể hỗ trợ nhiều dạng:

```text
=
>
<
>=
<=
BETWEEN
ORDER BY
prefix LIKE
JOIN
```

với điều kiện phù hợp.

Đây chính là lý do chúng ta học:

```text
31 → 37
```

theo thứ tự.

---

# 37. Tổng hợp các kỹ thuật Index đã học

```text
31 Index Fundamentals
       ↓
32 B-tree
       ↓
33 Composite
       ↓
34 Covering
       ↓
35 Partial
       ↓
36 Expression
       ↓
37 LIKE
```

Bây giờ ta có thể xây một index rất phức tạp:

```sql
CREATE INDEX idx_active_source_lower_title
ON novels(
    source,
    LOWER(title)
)
WHERE is_deleted = 0;
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE is_deleted = 0
  AND source = ?
  AND LOWER(title) LIKE ?
ORDER BY title
LIMIT 50;
```

Nhưng:

> **Đừng vội kết luận index này tối ưu.**

Đây là bài toán mà:

```text
EXPLAIN QUERY PLAN
```

sẽ trả lời.

---

# 38. Mental Model quan trọng nhất

```text
LIKE
 │
 ├── 'abc%'
 │      │
 │      └── Prefix
 │             ↓
 │          B-tree có thể phù hợp
 │
 ├── '%abc'
 │      │
 │      └── Suffix
 │             ↓
 │          B-tree thường không phù hợp
 │
 └── '%abc%'
        │
        └── Contains
               ↓
           B-tree thường không phù hợp
               ↓
              FTS5?
```

---

# 39. Bài tập thực hành

Tạo:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT NOT NULL
        CHECK (
            status IN ('ongoing', 'completed')
        )
);
```

Thêm khoảng 10–20 rows.

---

## Bài 1 — Prefix

Viết:

```sql
WHERE title LIKE 'Tiên%'
```

Sau đó:

```sql
EXPLAIN QUERY PLAN
```

---

## Bài 2 — Contains

Viết:

```sql
WHERE title LIKE '%Tiên%'
```

So sánh query plan.

---

## Bài 3 — Suffix

Viết:

```sql
WHERE title LIKE '%Nghịch'
```

So sánh.

---

## Bài 4 — Index

Tạo:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Sau đó kiểm tra lại:

```sql
EXPLAIN QUERY PLAN
```

với cả:

```sql
LIKE 'Tiên%'
```

và:

```sql
LIKE '%Tiên%'
```

---

# 40. Bài tập Composite

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE source = ?
  AND title LIKE 'Tiên%'
ORDER BY title
LIMIT 20;
```

Hãy thiết kế:

```text
(source, title)
```

Sau đó kiểm tra bằng:

```sql
EXPLAIN QUERY PLAN
```

---

# 41. Bài tập Partial + LIKE

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE status = 'ongoing'
  AND title LIKE 'Tiên%'
ORDER BY title
LIMIT 20;
```

Thiết kế một:

```text
Partial Index
```

phù hợp.

---

# 42. Bài tập Python

Viết:

```python
class NovelRepository:
    def search_title_prefix(
        self,
        prefix: str,
        limit: int = 20,
    ): ...
```

Yêu cầu:

```text
Python
 ↓
parameterized SQL
 ↓
LIKE 'prefix%'
 ↓
ORDER BY title
 ↓
LIMIT
```

Sau đó viết thêm:

```python
def search_title_contains(...):
    ...
```

và hiểu rõ vì sao hai method này có performance characteristic khác nhau.

---

# 43. Bài tập nâng cao — Search Architecture

Thiết kế:

```text
Novel Search
      │
      ├── Exact
      │      ↓
      │    B-tree
      │
      ├── Prefix
      │      ↓
      │    B-tree
      │
      ├── Contains
      │      ↓
      │    ?
      │
      └── Full Text
             ↓
            FTS5
```

Câu hỏi:

> Tại sao không dùng một query duy nhất `LIKE '%keyword%'` cho tất cả loại search?

Đây là câu hỏi rất quan trọng đối với việc thiết kế database cho app đọc truyện.

---

# 44. Công thức Buổi 37

```text
LIKE 'keyword%'
       ↓
PREFIX SEARCH
       ↓
B-tree có thể hữu ích
```

Trong khi:

```text
LIKE '%keyword%'
       ↓
CONTAINS SEARCH
       ↓
B-tree thường không phải công cụ phù hợp
       ↓
FTS5 / search strategy
```

Và:

```text
Composite Index
+
Partial Index
+
Expression Index
+
LIKE
```

có thể kết hợp với nhau, **nhưng phải xác nhận bằng query plan và benchmark**.

---

# Roadmap tiếp theo

```text
31. Index Fundamentals              ✅
32. B-Tree & SQLite Index Internals  ✅
33. Composite Index Deep Dive        ✅
34. Covering Index                   ✅
35. Partial Index                    ✅
36. Expression Index                 ✅
37. Index + LIKE                     ✅
38. Index + JOIN                     ← tiếp theo
39. Index + ORDER BY
40. EXPLAIN QUERY PLAN Deep Dive
41. Query Planner
42. ANALYZE & Statistics
43. N+1 Query
44. Keyset Pagination
45. Query Optimization thực chiến
```

**Buổi 38 — Index + JOIN** sẽ nối trực tiếp kiến thức `JOIN` ở Buổi 18–21 với B-tree: chúng ta sẽ phân tích **index nằm ở bảng nào, vì sao FK nên có index, SQLite tìm bảng nào trước, Nested Loop Join hoạt động thế nào, và tại sao `(novel_id, chapter_number)` lại cực kỳ phù hợp cho truy vấn `Novel → Chapters`.**
