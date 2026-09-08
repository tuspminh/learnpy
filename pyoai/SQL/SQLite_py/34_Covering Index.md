# Buổi 34 — Covering Index

Buổi này nối trực tiếp với **Composite Index** của Buổi 33.

Ta đã biết:

```text
Query
  ↓
Index
  ↓
tìm row
  ↓
Table
  ↓
lấy dữ liệu
```

Hôm nay học một trường hợp đặc biệt:

> **Index đã chứa toàn bộ dữ liệu mà query cần → SQLite có thể lấy kết quả ngay từ Index mà không cần quay lại Table B-tree.**

Đó là **Covering Index**.

---

# 1. Nhắc lại Index thông thường

Giả sử:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT
);
```

Tạo:

```sql
CREATE INDEX idx_chapters_novel
ON chapters(novel_id);
```

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

Index có:

```text
novel_id
   ↓
row reference
```

Nhưng query cần:

```text
id
chapter_number
title
```

Do đó mental model:

```text
INDEX
  │
  │ tìm rows có novel_id = ?
  ▼
TABLE
  │
  ├── id
  ├── chapter_number
  └── title
```

Tức là:

> Index giúp **tìm**, nhưng table vẫn phải cung cấp dữ liệu.

---

# 2. Covering Index là gì?

Bây giờ tạo:

```sql
CREATE INDEX idx_chapters_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Query:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

Index chứa:

```text
novel_id
chapter_number
title
```

Query cần:

```text
novel_id
chapter_number
title
```

→ Index đã chứa tất cả thông tin cần thiết.

Đây là:

> **Covering Index**

---

# 3. Mental Model

Index thông thường:

```text
Query
 ↓
Index
 ↓
row reference
 ↓
Table
 ↓
result
```

Covering Index:

```text
Query
 ↓
Index
 ↓
result
```

Điểm khác biệt:

```text
             Normal Index       Covering Index
                  │                   │
                  ▼                   ▼
                Index               Index
                  │                   │
                  ▼                   X
                Table              không cần
                  │
                  ▼
                Result
```

---

# 4. Tại sao Covering Index có thể nhanh hơn?

Giả sử query:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

Nếu index chỉ có:

```text
novel_id
```

SQLite:

```text
Index
 ↓
tìm entry
 ↓
đọc Table
 ↓
lấy chapter_number
 ↓
lấy title
```

Có covering index:

```text
Index
 ↓
tìm entry
 ↓
chapter_number
title
 ↓
Result
```

Giảm được việc truy cập Table B-tree.

---

# 5. Đây còn được gọi là Index-Only Scan

Bạn sẽ gặp thuật ngữ:

```text
Index-only scan
```

Ý tưởng:

```text
SQLite chỉ cần đọc Index
```

thay vì:

```text
Index
 +
Table
```

Trong SQLite, `EXPLAIN QUERY PLAN` thường có thể cho biết khi một index đang **cover** query, với dạng thông báo như:

```text
USING COVERING INDEX ...
```

Đây là dấu hiệu rất quan trọng.

---

# 6. Thử với SQLite

Tạo database:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

conn.executescript("""
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT
);

CREATE INDEX idx_chapters_novel
ON chapters(novel_id);
""")
```

Query:

```python
rows = conn.execute(
    """
    EXPLAIN QUERY PLAN
    SELECT
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
    """,
    (10,),
).fetchall()

for row in rows:
    print(dict(row))
```

Sau đó tạo một index khác:

```python
conn.execute("""
    CREATE INDEX idx_chapters_cover
    ON chapters(
        novel_id,
        chapter_number,
        title
    )
""")
```

Chạy lại `EXPLAIN QUERY PLAN`.

Bạn có thể thấy planner lựa chọn index covering phù hợp, ví dụ dạng:

```text
SEARCH chapters USING COVERING INDEX idx_chapters_cover (...)
```

---

# 7. Không phải cứ SELECT column nào cũng cần đưa vào Index

Đây là điểm cực kỳ quan trọng.

Giả sử:

```sql
SELECT
    chapter_number,
    title,
    content
FROM chapters
WHERE novel_id = ?;
```

Bạn có thể nghĩ:

```sql
CREATE INDEX idx_cover
ON chapters(
    novel_id,
    chapter_number,
    title,
    content
);
```

Nhưng:

> **Không nên làm như vậy chỉ để biến query thành covering index.**

Vì `content` có thể rất lớn.

---

# 8. Vấn đề `content`

Novel crawler:

```text
chapter.content
```

có thể:

```text
10 KB
30 KB
50 KB
100 KB
```

Nếu đưa `content` vào Index:

```text
INDEX
├── novel_id
├── chapter_number
├── title
└── content  ← rất lớn
```

Index sẽ phình to.

Hậu quả:

```text
Disk usage ↑
Index pages ↑
INSERT cost ↑
UPDATE cost ↑
DELETE cost ↑
Cache pressure ↑
```

Vì vậy:

> **Covering Index không có nghĩa là nhét tất cả column vào Index.**

---

# 9. Covering Index phải được thiết kế theo Query

Ví dụ UI danh sách chapter chỉ cần:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Candidate:

```sql
CREATE INDEX idx_chapters_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Ở đây:

```text
WHERE
  novel_id

ORDER BY
  chapter_number

SELECT
  chapter_number
  title
```

Index chứa toàn bộ những gì query cần.

```text
(novel_id, chapter_number, title)
```

Đây là một ví dụ **covering index rất tự nhiên**.

---

# 10. Nhưng có một vấn đề

Ta đã có:

```sql
UNIQUE(novel_id, chapter_number)
```

Nếu schema của bạn đã có:

```sql
UNIQUE(
    novel_id,
    chapter_number
)
```

thì cấu trúc uniqueness đó có thể đã hỗ trợ:

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

Nhưng query còn cần:

```text
title
```

nên nó chưa chắc là covering cho query:

```sql
SELECT chapter_number, title ...
```

Muốn cover thêm `title`, ta có thể cân nhắc index:

```text
(novel_id, chapter_number, title)
```

Nhưng phải cân nhắc chi phí duplicate structure.

---

# 11. Đây là một trade-off

Covering Index:

```text
Query performance
        ↑
Table lookup
        ↓
```

nhưng:

```text
Index size
     ↑
Write cost
     ↑
Storage
     ↑
```

Do đó:

```text
Covering Index
      =
Performance optimization
```

không phải:

```text
Covering Index
      =
luôn phải tạo
```

---

# 12. Ví dụ cực thực tế với Novel Reader

UI:

```text
Novel: Tiên Nghịch

Chapter 1    Bước đầu tu tiên
Chapter 2    Vương Lâm
Chapter 3    ...
...
```

Query:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Ta có:

```text
WHERE
novel_id

ORDER BY
chapter_number

SELECT
chapter_number
title
```

Candidate:

```sql
CREATE INDEX idx_chapters_list
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Mental model:

```text
              INDEX
                │
       ┌────────┼──────────┐
       │        │          │
   novel_id  chapter_no   title
       │        │          │
       │        │          │
     WHERE    ORDER BY   SELECT
```

Rất đẹp về mặt query pattern.

---

# 13. Nhưng khi mở chapter thì khác

Khi người dùng click:

```text
Chapter 500
```

UI cần:

```sql
SELECT
    content
FROM chapters
WHERE novel_id = ?
  AND chapter_number = ?;
```

Covering index ở trên **không chứa `content`**.

Nhưng điều này không phải vấn đề.

Index giúp:

```text
novel_id
chapter_number
```

xác định chapter rất nhanh.

Sau đó SQLite lấy:

```text
content
```

từ table.

Đây thường là thiết kế hợp lý hơn việc đưa `content` vào index.

---

# 14. Hai Use Case khác nhau

### Chapter List

```text
SELECT chapter_number, title
```

→ có thể hưởng lợi từ covering index.

### Chapter Reader

```text
SELECT content
```

→ cần đọc content từ table.

Đây là một bài học kiến trúc rất quan trọng:

> **Một index nên phục vụ workload, không phải cố làm mọi query thành covering query.**

---

# 15. Covering Index và `SELECT *`

Ví dụ:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Rất khó để tạo covering index hợp lý nếu table có:

```text
id
novel_id
chapter_number
title
content
created_at
updated_at
...
```

Bạn phải đưa gần như toàn bộ dữ liệu vào index.

Điều này thường không đáng.

Đây là thêm một lý do để tránh:

```sql
SELECT *
```

khi query chỉ cần vài column.

---

# 16. Explicit Columns

Thay vì:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

hãy viết:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

Điều này cho phép index design tốt hơn.

Mental model:

```text
SELECT *
   ↓
khó tối ưu covering

SELECT A, B
   ↓
có thể thiết kế index A/B
```

---

# 17. Covering Index + LIMIT

Đây là combination rất thú vị:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Index:

```text
(novel_id, chapter_number, title)
```

SQLite có thể:

```text
Index
 ↓
novel_id = 10
 ↓
chapter_number sorted
 ↓
title
 ↓
first 50
```

Không cần lấy toàn bộ row từ table cho danh sách này nếu planner chọn covering index.

---

# 18. Covering Index + Pagination

Page 1:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Page tiếp theo với keyset pagination:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
  AND chapter_number > ?
ORDER BY chapter_number
LIMIT 50;
```

Candidate:

```text
(novel_id, chapter_number, title)
```

có thể phục vụ rất tốt workload này.

Đây là lý do Covering Index sẽ kết nối rất đẹp với:

```text
Buổi 44 — Keyset Pagination
```

---

# 19. Covering Index không chỉ dành cho SELECT

Về khái niệm, index có thể giúp nhiều loại query.

Nhưng **covering index** chủ yếu được nói đến khi query có thể lấy các giá trị cần thiết trực tiếp từ index.

Đặc biệt phổ biến với:

```text
SELECT
```

---

# 20. Index chứa row reference

Quay lại Buổi 32.

Index có thể hình dung:

```text
key
 +
row reference
```

Ví dụ:

```text
novel_id = 10
      ↓
row location
```

Nếu query cần:

```text
title
```

nhưng index không chứa title:

```text
Index
 ↓
row reference
 ↓
Table
 ↓
title
```

Nếu index chứa title:

```text
Index
 ↓
title
```

→ có thể cover.

---

# 21. Covering Index không có nghĩa "không bao giờ đọc Table"

Planner vẫn phải quyết định execution plan.

Bạn không nên suy luận:

```text
Index có đủ column
→ SQLite chắc chắn dùng covering index
```

Đúng hơn:

```text
Index có đủ column
       ↓
có khả năng cover query
       ↓
Query Planner đánh giá
       ↓
chọn plan
```

Đây là điểm quan trọng.

---

# 22. Dùng EXPLAIN để kiểm chứng

Query:

```sql
EXPLAIN QUERY PLAN
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Nếu planner chọn covering index, output thường có dạng:

```text
USING COVERING INDEX
```

Đây là bằng chứng thực tế.

Không cần đoán.

---

# 23. Python helper

Ta có thể viết:

```python
def explain_query(conn, sql, params=()):
    rows = conn.execute(
        "EXPLAIN QUERY PLAN " + sql,
        params,
    ).fetchall()

    for row in rows:
        print(tuple(row))
```

Sau đó:

```python
sql = """
    SELECT
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
    ORDER BY chapter_number
    LIMIT 50
"""

explain_query(conn, sql, (10,))
```

Bạn nên tập thói quen:

```text
Thiết kế index
      ↓
EXPLAIN
      ↓
Xác nhận planner
```

---

# 24. So sánh 3 loại

## Index thường

```text
Index
 ↓
Table
 ↓
Result
```

## Composite Index

```text
Index
(A, B, C)
 ↓
query có thể tận dụng nhiều column
```

## Covering Index

```text
Index
(A, B, C)
 ↓
đã chứa toàn bộ dữ liệu query cần
 ↓
Result
```

Điểm quan trọng:

> **Composite Index và Covering Index không phải hai loại index hoàn toàn khác nhau.**

Một Composite Index **có thể đồng thời là Covering Index cho một query cụ thể**.

---

# 25. Ví dụ để phân biệt

Index:

```sql
CREATE INDEX idx_test
ON chapters(
    novel_id,
    chapter_number
);
```

Query:

```sql
SELECT
    chapter_number
FROM chapters
WHERE novel_id = ?;
```

Index có:

```text
novel_id
chapter_number
```

Query cần:

```text
novel_id → WHERE
chapter_number → SELECT
```

→ index có thể cover query này.

---

Index:

```text
(novel_id, chapter_number)
```

Query:

```sql
SELECT
    title
FROM chapters
WHERE novel_id = ?;
```

Index không có:

```text
title
```

→ không covering.

---

# 26. `id` có cần đưa vào Index không?

Ví dụ:

```sql
CREATE INDEX idx_chapters_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

Query cần:

```text
id
chapter_number
title
```

Nhưng index không khai báo `id`.

Ở đây cần hiểu chi tiết SQLite về rowid/table lookup và cách index entry liên hệ tới row. Đừng tự động kết luận rằng chỉ vì `id` là primary key thì mọi query chọn `id` đều được cover theo cách bạn tưởng tượng.

**Muốn xác nhận:** dùng `EXPLAIN QUERY PLAN`.

Đây chính là lý do chúng ta không học optimization chỉ bằng lý thuyết.

---

# 27. Sai lầm: "Càng nhiều column càng tốt"

Ví dụ:

```sql
CREATE INDEX idx_bad
ON chapters(
    novel_id,
    chapter_number,
    title,
    content,
    created_at,
    updated_at
);
```

Nhìn rất "mạnh".

Nhưng thực tế:

```text
Index size       ↑↑
INSERT cost      ↑
UPDATE cost      ↑
DELETE cost      ↑
Disk             ↑
Cache pressure   ↑
```

Trong khi query thực tế có thể chỉ cần:

```text
novel_id
chapter_number
title
```

Do đó:

> **Minimal useful covering index** thường tốt hơn một index khổng lồ.

---

# 28. Covering Index trong Dashboard

Ví dụ dashboard:

```sql
SELECT
    source,
    status,
    updated_at
FROM novels
WHERE source = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Candidate:

```text
(source, updated_at, status)
```

hoặc thứ tự khác tùy workload và predicate/sort thực tế.

Điểm cần nhớ:

> Đừng tự động áp dụng một công thức cứng nhắc. Hãy thiết kế candidate rồi `EXPLAIN`.

---

# 29. Một quy trình thực chiến

Khi muốn tạo Covering Index:

### Bước 1 — Viết query

```sql
SELECT
    A,
    B
FROM table
WHERE C = ?
ORDER BY D
LIMIT 50;
```

### Bước 2 — Xác định:

```text
WHERE → C
ORDER BY → D
SELECT → A, B
```

### Bước 3 — Thiết kế candidate

Ví dụ:

```text
(C, D, A, B)
```

### Bước 4 — EXPLAIN

```sql
EXPLAIN QUERY PLAN ...
```

### Bước 5 — Benchmark

### Bước 6 — Kiểm tra write/storage cost

---

# 30. Novel Reader — Thiết kế thực tế

Giả sử UI có query:

```sql
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Ta có candidate:

```sql
CREATE INDEX idx_chapters_list_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Kiến trúc:

```text
Novel Reader
     │
     ▼
Chapter List Query
     │
     ▼
(novel_id, chapter_number, title)
     │
     ▼
Covering Index
     │
     ▼
50 rows
```

Không cần kéo:

```text
content
```

về application.

Đây là một optimization rất phù hợp với app đọc truyện.

---

# 31. Và đây là điểm kiến trúc rất quan trọng

Không chỉ Index.

Query của Repository cũng phải được thiết kế tốt:

```python
class ChapterRepository:
    def list_for_reader(
        self,
        novel_id: int,
        limit: int = 50,
    ):
        return self._conn.execute(
            """
            SELECT
                chapter_number,
                title
            FROM chapters
            WHERE novel_id = ?
            ORDER BY chapter_number
            LIMIT ?
            """,
            (novel_id, limit),
        ).fetchall()
```

Repository chỉ lấy:

```text
chapter_number
title
```

thay vì:

```text
SELECT *
```

Sau đó index:

```text
(novel_id, chapter_number, title)
```

có cơ hội trở thành covering index.

Đây là cách:

```text
Application Design
+
SQL Design
+
Index Design
```

phối hợp với nhau.

---

# 32. Bài tập thực hành

Tạo:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
```

Insert dữ liệu.

Sau đó chạy query:

```sql
EXPLAIN QUERY PLAN
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = 10
ORDER BY chapter_number
LIMIT 20;
```

### Bước 1

Không có index.

Ghi kết quả.

### Bước 2

Tạo:

```sql
CREATE INDEX idx_chapters_novel
ON chapters(novel_id);
```

EXPLAIN lại.

### Bước 3

Tạo candidate:

```sql
CREATE INDEX idx_chapters_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

EXPLAIN lại.

### Bước 4

So sánh:

```text
SCAN
SEARCH
USING INDEX
USING COVERING INDEX
```

---

# 33. Bài tập tư duy

Cho index:

```text
(A, B, C)
```

Query:

### Query 1

```sql
SELECT B, C
FROM T
WHERE A = ?;
```

### Query 2

```sql
SELECT B
FROM T
WHERE A = ?;
```

### Query 3

```sql
SELECT D
FROM T
WHERE A = ?;
```

### Query 4

```sql
SELECT B, C
FROM T
WHERE B = ?;
```

Hãy tự trả lời:

```text
Query 1 → có khả năng covering?
Query 2 → có khả năng covering?
Query 3 → có khả năng covering?
Query 4 → index có phải prefix tốt?
```

Sau đó dùng:

```sql
EXPLAIN QUERY PLAN
```

để kiểm chứng.

---

# 34. Ba tầng kiến thức bạn đã có

Sau 4 buổi:

```text
Buổi 31
Index Fundamentals
       ↓
Index dùng để tìm nhanh


Buổi 32
B-tree
       ↓
Index được tổ chức như thế nào


Buổi 33
Composite Index
       ↓
Nhiều column + thứ tự column


Buổi 34
Covering Index
       ↓
Index có thể chứa đủ dữ liệu
       ↓
giảm table lookup
```

Đây là một chuỗi kiến thức rất logic.

---

# 35. Mental Model cuối buổi

### Index bình thường

```text
             Query
               │
               ▼
             Index
               │
               ▼
          Row reference
               │
               ▼
             Table
               │
               ▼
            Result
```

### Covering Index

```text
             Query
               │
               ▼
       Covering Index
               │
       ┌───────┴───────┐
       │               │
      key          needed columns
       │               │
       └───────┬───────┘
               ▼
             Result
```

Và:

```text
Covering Index
      ≠
một loại index riêng biệt
```

Mà:

```text
Composite / Index structure
        +
query cần các column nằm trong index
        ↓
Covering Index cho query đó
```

---

# 36. 5 điều cần nhớ

**1.**

> Index thông thường giúp tìm row.

**2.**

> Covering Index có thể cung cấp luôn dữ liệu query cần.

**3.**

> Một Composite Index có thể trở thành Covering Index tùy query.

**4.**

> Không nên đưa column lớn như `content` vào index chỉ để cover query.

**5.**

> Dùng `EXPLAIN QUERY PLAN` để kiểm chứng, không đoán.

---

# Roadmap tiếp theo

```text
31. Index Fundamentals              ✅
32. B-Tree & SQLite Index Internals  ✅
33. Composite Index Deep Dive        ✅
34. Covering Index                   ✅
35. Partial Index                    ← tiếp theo
36. Expression Index
37. Index + LIKE
38. Index + JOIN
39. Index + ORDER BY
40. EXPLAIN QUERY PLAN Deep Dive
41. Query Planner
42. ANALYZE & Statistics
43. N+1 Query
44. Keyset Pagination
45. Query Optimization thực chiến
```

**Buổi 35 — Partial Index** sẽ rất thú vị với crawler: thay vì index toàn bộ `chapters`/`novels`, chúng ta sẽ học cách tạo index **chỉ trên những rows thỏa một điều kiện**, ví dụ chỉ index các chapter chưa crawl hoặc các novel đang `ongoing`.
