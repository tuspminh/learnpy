# Buổi 36 — Expression Index

Hôm nay chúng ta học một loại index rất quan trọng khi query **không tìm trực tiếp theo giá trị của column**, mà tìm theo **biểu thức được tính từ column**.

Ví dụ:

```sql
WHERE LOWER(title) = ?
```

hoặc:

```sql
WHERE TRIM(title) = ?
```

hoặc:

```sql
ORDER BY LENGTH(title)
```

Index thông thường trên `title` không nhất thiết giải quyết được các query này.

---

# 1. Vấn đề của Expression

Giả sử:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Dữ liệu:

```text
Tiên Nghịch
TIÊN NGHỊCH
tiên nghịch
Phàm Nhân Tu Tiên
```

Ta muốn tìm không phân biệt hoa thường:

```sql
SELECT id, title
FROM novels
WHERE LOWER(title) = LOWER(?);
```

Ví dụ:

```python
keyword = "TIÊN NGHỊCH"
```

Query:

```sql
WHERE LOWER(title) = LOWER(?)
```

Vấn đề nằm ở:

```text
title
  ↓
LOWER(title)
  ↓
so sánh
```

Index bình thường:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

được xây trên:

```text
title
```

chứ không phải:

```text
LOWER(title)
```

---

# 2. Expression Index là gì?

SQLite cho phép tạo index trên **expression**:

```sql
CREATE INDEX idx_novels_lower_title
ON novels(LOWER(title));
```

Bây giờ index được xây dựa trên:

```text
LOWER(title)
```

Mental model:

```text
Normal Index

title
  ↓
B-tree


Expression Index

title
  ↓
LOWER(title)
  ↓
B-tree
```

---

# 3. Syntax

Cú pháp:

```sql
CREATE INDEX index_name
ON table_name(expression);
```

Ví dụ:

```sql
CREATE INDEX idx_novels_lower_title
ON novels(LOWER(title));
```

Đây là:

> **Expression Index**

---

# 4. Query tương ứng

Index:

```sql
CREATE INDEX idx_novels_lower_title
ON novels(LOWER(title));
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE LOWER(title) = ?;
```

Python:

```python
keyword = "tiên nghịch"

rows = conn.execute(
    """
    SELECT
        id,
        title
    FROM novels
    WHERE LOWER(title) = ?
    """,
    (keyword.lower(),),
).fetchall()
```

Điểm quan trọng:

```text
Index expression
       =
Query expression
```

---

# 5. Vì sao Index thường không đủ?

Có:

```sql
CREATE INDEX idx_title
ON novels(title);
```

Query:

```sql
WHERE LOWER(title) = ?
```

Hai thứ khác nhau:

```text
Index:
title

Query:
LOWER(title)
```

Mental model:

```text
B-tree chứa:

"Tiên Nghịch"
"TIÊN NGHỊCH"
"tiên nghịch"
```

không giống với B-tree chứa:

```text
"tiên nghịch"
"tiên nghịch"
"tiên nghịch"
```

Expression Index giải quyết vấn đề bằng cách index chính expression đó.

---

# 6. Ví dụ với `LOWER()`

Tạo:

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
```

Index:

```sql
CREATE INDEX idx_authors_lower_name
ON authors(LOWER(name));
```

Query:

```sql
SELECT *
FROM authors
WHERE LOWER(name) = ?;
```

Python:

```python
name = "nhĩ căn"

row = conn.execute(
    """
    SELECT id, name
    FROM authors
    WHERE LOWER(name) = ?
    """,
    (name.lower(),),
).fetchone()
```

---

# 7. Expression Index không thay đổi dữ liệu

Điều này rất quan trọng.

```sql
CREATE INDEX idx_authors_lower_name
ON authors(LOWER(name));
```

Không biến:

```text
Nhĩ Căn
```

thành:

```text
nhĩ căn
```

trong table.

Table vẫn:

```text
name
---------
Nhĩ Căn
```

Index giữ giá trị expression:

```text
LOWER(name)
-----------
nhĩ căn
```

Mental model:

```text
TABLE
name = "Nhĩ Căn"

       │
       ▼
LOWER(name)
       │
       ▼
INDEX
"nhĩ căn"
```

---

# 8. `TRIM()`

Một use case khác:

```text
" Tiên Nghịch "
```

và:

```text
"Tiên Nghịch"
```

Muốn tìm bỏ whitespace đầu/cuối:

```sql
WHERE TRIM(title) = ?
```

Ta có:

```sql
CREATE INDEX idx_novels_trim_title
ON novels(TRIM(title));
```

Query:

```sql
SELECT id, title
FROM novels
WHERE TRIM(title) = ?;
```

---

# 9. `LENGTH()`

Expression Index cũng có thể dùng expression tính toán.

Ví dụ:

```sql
CREATE INDEX idx_novels_title_length
ON novels(LENGTH(title));
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE LENGTH(title) > ?;
```

Hoặc:

```sql
SELECT
    id,
    title
FROM novels
ORDER BY LENGTH(title);
```

Tuy nhiên:

> Không phải expression nào cũng nên index.

Đây chỉ là ví dụ để hiểu cơ chế.

---

# 10. Expression Index + toán học

Ví dụ chapters:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL
);
```

Có thể tạo expression:

```sql
CREATE INDEX idx_chapter_number_plus_one
ON chapters(chapter_number + 1);
```

Query:

```sql
SELECT *
FROM chapters
WHERE chapter_number + 1 = ?;
```

Nhưng đây thường **không phải thiết kế tốt**.

Tại sao?

Vì nếu query thường xuyên:

```sql
WHERE chapter_number = ?
```

thì index bình thường:

```sql
CREATE INDEX idx_chapter_number
ON chapters(chapter_number);
```

đơn giản hơn.

---

# 11. Nguyên tắc quan trọng

Expression Index nên xuất hiện khi:

```text
Query thường xuyên
       +
Expression ổn định
       +
Expression khó tránh
       +
Workload đủ lớn
```

Không phải:

```text
"SQLite cho phép index expression"
        ↓
"index tất cả expression"
```

---

# 12. Expression Index + Composite Index

Expression không nhất thiết đứng một mình.

Ví dụ:

```sql
CREATE INDEX idx_source_lower_title
ON novels(
    source,
    LOWER(title)
);
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE source = ?
  AND LOWER(title) = ?;
```

Ta có:

```text
Composite Index
      │
      ├── source
      │
      └── LOWER(title)
```

Điều này kết hợp kiến thức Buổi 33.

---

# 13. Leftmost Prefix vẫn áp dụng

Index:

```sql
CREATE INDEX idx_source_lower_title
ON novels(
    source,
    LOWER(title)
);
```

Có thể hỗ trợ tự nhiên cho:

```sql
WHERE source = ?
```

và:

```sql
WHERE source = ?
  AND LOWER(title) = ?
```

Nhưng không nên coi nó như index riêng trên:

```sql
LOWER(title)
```

Mental model:

```text
(source, LOWER(title))
   │             │
   │             └── expression
   └─────────────── leading column
```

---

# 14. Expression Index + ORDER BY

Expression Index cũng có thể hữu ích cho:

```sql
ORDER BY LOWER(title);
```

Ví dụ:

```sql
CREATE INDEX idx_novels_lower_title
ON novels(LOWER(title));
```

Query:

```sql
SELECT
    id,
    title
FROM novels
ORDER BY LOWER(title)
LIMIT 50;
```

Index đã được sắp xếp theo:

```text
LOWER(title)
```

nên nó có thể phù hợp với ordering này.

Nhưng một lần nữa:

> Phải dùng `EXPLAIN QUERY PLAN` để kiểm chứng.

---

# 15. Đây là điểm cực kỳ quan trọng

Expression Index:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

không có nghĩa:

```sql
WHERE title = ?
```

và:

```sql
WHERE LOWER(title) = ?
```

là giống nhau.

Chúng là hai query pattern khác nhau.

```text
Index:
LOWER(title)

Query:
title
```

không phải match trực tiếp như:

```text
Index:
LOWER(title)

Query:
LOWER(title)
```

---

# 16. Expression phải phù hợp

Ví dụ index:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

Query:

```sql
WHERE LOWER(title) = ?
```

Phù hợp.

Nhưng nếu query:

```sql
WHERE UPPER(title) = ?
```

thì expression là:

```text
UPPER(title)
```

khác:

```text
LOWER(title)
```

Không nên kỳ vọng index `LOWER(title)` phục vụ trực tiếp query này.

---

# 17. Expression Index và `COALESCE`

Một use case rất thực tế:

```text
author có thể NULL
```

Query:

```sql
WHERE COALESCE(author, '') = ?;
```

Có thể tạo:

```sql
CREATE INDEX idx_author_normalized
ON novels(COALESCE(author, ''));
```

Query:

```sql
SELECT
    id,
    title,
    author
FROM novels
WHERE COALESCE(author, '') = ?;
```

Index expression:

```text
COALESCE(author, '')
```

---

# 18. Nhưng có một thiết kế tốt hơn trong nhiều trường hợp

Nếu business rule nói:

> Author không được NULL.

Thì tốt hơn:

```sql
author TEXT NOT NULL
```

thay vì tạo Expression Index để xử lý NULL.

Đây là bài học kiến trúc:

```text
Data invariant
     ↓
Constraint
```

không phải:

```text
Data invariant
     ↓
Index
```

Index chủ yếu phục vụ:

```text
Performance
```

---

# 19. Expression Index và `CASE`

SQLite có thể index expression phức tạp hơn.

Ví dụ:

```sql
CREATE INDEX idx_status_priority
ON novels(
    CASE
        WHEN status = 'ongoing' THEN 1
        WHEN status = 'completed' THEN 2
        ELSE 3
    END
);
```

Sau đó:

```sql
SELECT
    id,
    title,
    status
FROM novels
ORDER BY
    CASE
        WHEN status = 'ongoing' THEN 1
        WHEN status = 'completed' THEN 2
        ELSE 3
    END;
```

Đây là một ví dụ rất hay vì nó kết hợp:

```text
Buổi 13
CASE WHEN

+

Buổi 36
Expression Index
```

Nhưng nếu chỉ có:

```text
ongoing
completed
```

và bảng không lớn, index này có thể không đáng.

---

# 20. Expression Index vs Generated Column

Đây là một khái niệm nâng cao rất đáng biết.

Thay vì:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

ta có thể thiết kế một generated column trong những trường hợp phù hợp:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT
        GENERATED ALWAYS AS (LOWER(title)) STORED
);
```

Sau đó:

```sql
CREATE INDEX idx_normalized_title
ON novels(normalized_title);
```

Mental model:

### Expression Index

```text
title
 ↓
LOWER(title)
 ↓
Index
```

### Generated Column + Index

```text
title
 ↓
normalized_title
 ↓
Index
```

Generated column có thể hữu ích khi application cũng cần truy cập giá trị đã chuẩn hóa như một column thực tế.

---

# 21. Khi nào dùng Expression Index?

### Dùng Expression Index khi:

```text
Query thường xuyên dùng expression
+
Không muốn thay đổi schema bằng generated column
+
Expression có giá trị cho query optimization
```

Ví dụ:

```sql
WHERE LOWER(title) = ?
```

→

```sql
CREATE INDEX ...
ON novels(LOWER(title));
```

---

# 22. Khi nào dùng Generated Column?

Nếu application thường xuyên cần:

```python
novel.normalized_title
```

thì generated column có thể làm thiết kế rõ ràng hơn:

```text
title
   ↓
normalized_title
   ↓
query/index/application
```

Đặc biệt nếu expression là một phần có ý nghĩa trong domain/read model.

---

# 23. Python Repository

Ví dụ:

```python
class NovelRepository:
    def find_by_title(self, title: str):
        normalized = title.strip().lower()

        return self._conn.execute(
            """
            SELECT
                id,
                title,
                author
            FROM novels
            WHERE LOWER(TRIM(title)) = ?
            """,
            (normalized,),
        ).fetchall()
```

Index tương ứng:

```sql
CREATE INDEX idx_novels_normalized_title
ON novels(LOWER(TRIM(title)));
```

Ở đây có:

```text
Python
  ↓
strip()
lower()
  ↓
SQL
  ↓
LOWER(TRIM(title))
  ↓
Expression Index
```

---

# 24. Một nuance quan trọng với Python

Bạn có thể normalize parameter:

```python
normalized = title.strip().lower()
```

nhưng phía database vẫn:

```sql
LOWER(TRIM(title))
```

Tức là:

```text
Python:
"  TIÊN NGHỊCH  "
        ↓
"tiên nghịch"


Database:
" Tiên Nghịch "
        ↓
"tiên nghịch"
```

Hai bên tạo ra cùng giá trị để so sánh.

---

# 25. Kiểm tra bằng EXPLAIN QUERY PLAN

Trước index:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM novels
WHERE LOWER(title) = ?;
```

Có thể thấy dạng:

```text
SCAN novels
```

Sau:

```sql
CREATE INDEX idx_novels_lower_title
ON novels(LOWER(title));
```

thử lại:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM novels
WHERE LOWER(title) = ?;
```

Bạn muốn kiểm tra xem planner có chọn expression index hay không.

Mental model:

```text
Before

LOWER(title)
     ↓
   SCAN


After

LOWER(title)
     ↓
Expression Index
     ↓
  SEARCH
```

Đây chính là kỹ năng chúng ta sẽ đào sâu ở **Buổi 40 — EXPLAIN QUERY PLAN Deep Dive**.

---

# 26. Expression Index + Partial Index

Và đây là phần thú vị nhất.

Ta hoàn toàn có thể kết hợp:

```text
Expression
+
Partial
```

Ví dụ chỉ index title của novel đang active:

```sql
CREATE INDEX idx_active_lower_title
ON novels(LOWER(title))
WHERE is_deleted = 0;
```

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE is_deleted = 0
  AND LOWER(title) = ?;
```

Ta có:

```text
Expression Index
        +
Partial Index
```

---

# 27. Expression + Composite + Partial

Có thể đi xa hơn:

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
  AND LOWER(title) = ?;
```

Index này đồng thời có:

```text
Composite
+
Expression
+
Partial
```

Đây là ví dụ tốt để thấy các kỹ thuật index không tồn tại độc lập.

---

# 28. Nhưng đừng biến database thành "rừng index"

Ví dụ không nên tùy tiện tạo:

```sql
CREATE INDEX ...
ON novels(LOWER(title));

CREATE INDEX ...
ON novels(UPPER(title));

CREATE INDEX ...
ON novels(TRIM(title));

CREATE INDEX ...
ON novels(LENGTH(title));

CREATE INDEX ...
ON novels(REPLACE(title, ' ', ''));
```

Nếu application chỉ có:

```text
100 novels
```

thì những index này có thể chẳng mang lại lợi ích đáng kể.

Ngược lại:

```text
10,000,000 rows
+
query cực kỳ thường xuyên
+
expression có tính ổn định
```

thì câu chuyện khác.

---

# 29. Quy trình thiết kế Expression Index

Hãy dùng quy trình này:

```text
1. Xác định query thực tế
          ↓
2. Tìm expression
          ↓
3. EXPLAIN QUERY PLAN
          ↓
4. Tạo Expression Index
          ↓
5. EXPLAIN lại
          ↓
6. Benchmark
          ↓
7. Đánh giá write/storage cost
```

Không nên:

```text
Expression xuất hiện
       ↓
CREATE INDEX ngay
```

---

# 30. So sánh ba cách

Giả sử cần tìm title không phân biệt hoa thường.

### Cách 1 — Full scan

```sql
WHERE LOWER(title) = ?
```

Không có index phù hợp:

```text
SCAN
```

---

### Cách 2 — Expression Index

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

```text
LOWER(title)
      ↓
Expression Index
      ↓
SEARCH
```

---

### Cách 3 — Generated Column

```text
title
 ↓
normalized_title
 ↓
index
```

Cách 3 có thể phù hợp khi normalized value cũng có ý nghĩa đối với application/schema.

---

# 31. Liên hệ với app đọc truyện

Trong app của bạn, một số expression có thể xuất hiện:

### Tìm title không phân biệt hoa thường

```sql
LOWER(title)
```

### Chuẩn hóa whitespace

```sql
TRIM(title)
```

### Chuẩn hóa author

```sql
LOWER(TRIM(author))
```

### Custom ordering

```sql
CASE ...
END
```

### Query active records

```text
Expression + Partial
```

Nhưng hãy nhớ:

> Không phải cứ có thể tạo Expression Index là nên tạo.

---

# 32. Bài tập thực hành

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
        ),
    is_deleted INTEGER NOT NULL DEFAULT 0
);
```

Thêm dữ liệu:

```text
Tiên Nghịch
TIÊN NGHỊCH
  Tiên Nghịch
Phàm Nhân Tu Tiên
PHÀM NHÂN TU TIÊN
```

---

## Bài 1 — LOWER

Query:

```sql
SELECT id, title
FROM novels
WHERE LOWER(title) = ?;
```

Tạo Expression Index phù hợp.

---

## Bài 2 — TRIM + LOWER

Query:

```sql
SELECT id, title
FROM novels
WHERE LOWER(TRIM(title)) = ?;
```

Thiết kế:

```text
Expression Index
```

phù hợp.

---

## Bài 3 — Composite Expression Index

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE source = ?
  AND LOWER(title) = ?;
```

Thiết kế index:

```text
(source, LOWER(title))
```

---

## Bài 4 — Partial + Expression

Chỉ tìm active novels:

```sql
SELECT
    id,
    title
FROM novels
WHERE is_deleted = 0
  AND LOWER(title) = ?;
```

Thiết kế:

```text
Partial
+
Expression
```

---

## Bài 5 — EXPLAIN

Trước index:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM novels
WHERE LOWER(title) = ?;
```

Sau index:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

Chạy lại `EXPLAIN QUERY PLAN`.

So sánh:

```text
SCAN
vs
SEARCH USING INDEX
```

---

# 33. Bài tập nâng cao

Cho query:

```sql
SELECT
    id,
    title,
    source
FROM novels
WHERE is_deleted = 0
  AND source = ?
  AND LOWER(TRIM(title)) = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Hãy thử thiết kế:

```text
Partial
+
Composite
+
Expression
```

Gợi ý tư duy:

```text
WHERE
 │
 ├── is_deleted = 0
 │
 ├── source = ?
 │
 └── LOWER(TRIM(title)) = ?
 │
 ▼
INDEX
```

Sau đó mới cân nhắc:

```text
ORDER BY updated_at
```

và dùng `EXPLAIN QUERY PLAN` để kiểm chứng.

**Đừng cố nhồi mọi column vào index ngay lập tức.** Đây chính là vấn đề chúng ta sẽ học sâu hơn ở các buổi `EXPLAIN`, Query Planner và Optimization.

---

# 34. Mental Model của Buổi 36

```text
Normal Index

column
  ↓
B-tree
```

Expression Index:

```text
column
  ↓
expression
  ↓
B-tree
```

Ví dụ:

```sql
CREATE INDEX idx_lower_title
ON novels(LOWER(title));
```

Query:

```sql
WHERE LOWER(title) = ?
```

---

# 35. Kết nối với các buổi trước

Bây giờ kiến thức Index của chúng ta đã trở thành:

```text
31  Index Fundamentals
       ↓
32  B-Tree
       ↓
33  Composite Index
       ↓
34  Covering Index
       ↓
35  Partial Index
       ↓
36  Expression Index
```

Và một index có thể kết hợp nhiều ý tưởng:

```text
                    INDEX
                      │
        ┌─────────────┼──────────────┐
        │             │              │
    Composite       Partial       Expression
        │             │              │
        └─────────────┼──────────────┘
                      │
                 Covering?
                      │
                      ▼
                Query Planner
                      │
                      ▼
                    EXPLAIN
```

### 5 điều cần nhớ

1. **Expression Index index kết quả của expression**, không phải trực tiếp column.
2. `INDEX ON LOWER(title)` phù hợp với query dùng `LOWER(title)`.
3. Expression Index có thể kết hợp với **Composite** và **Partial Index**.
4. Không phải expression nào cũng đáng index.
5. **EXPLAIN QUERY PLAN + benchmark** mới là cơ sở quyết định.

---

## Tiếp theo: Buổi 37 — Index + LIKE

Đây sẽ là buổi cực kỳ thực tế cho **app tìm kiếm truyện**:

```sql
WHERE title LIKE 'Tiên%'
```

vs

```sql
WHERE title LIKE '%Tiên%'
```

Chúng ta sẽ tìm hiểu **vì sao một dạng LIKE có thể sử dụng B-tree index còn dạng kia thường không**, vấn đề prefix search, `%`, `_`, case sensitivity, và khi nào nên chuyển sang **FTS5** thay vì cố ép B-tree index.
