# Buổi 46 — CTE (`WITH`) trong SQLite

Sau Part V về **Index & Query Optimization**, chúng ta bước sang:

# Part VI — Advanced SQL

Buổi đầu tiên là **CTE — Common Table Expression**.

CTE cực kỳ quan trọng vì nó giúp bạn viết SQL theo kiểu:

```text
Query lớn
   ↓
chia thành các bước nhỏ
   ↓
WITH ...
   ↓
query cuối
```

Thay vì viết một câu SQL lồng nhau rất khó đọc.

---

# 1. CTE là gì?

CTE viết bằng:

```sql
WITH ...
```

Ví dụ:

```sql
WITH ongoing_novels AS (
    SELECT
        id,
        title,
        status
    FROM novels
    WHERE status = 'ongoing'
)
SELECT *
FROM ongoing_novels;
```

Ta có:

```text
WITH ongoing_novels AS (...)
```

tạo ra một **named result set** để query phía sau sử dụng.

Mental model:

```text
WITH
    ↓
temporary named query
    ↓
main SELECT
```

---

# 2. Tại sao cần CTE?

Không có CTE:

```sql
SELECT
    ...
FROM (
    SELECT
        ...
    FROM (
        SELECT
            ...
        ) ...
    ) ...
```

Query có thể trở thành:

```text
SELECT
  └── FROM
       └── subquery
            └── subquery
                 └── subquery
```

Rất khó đọc.

CTE:

```sql
WITH step1 AS (...),
     step2 AS (...),
     step3 AS (...)
SELECT ...
FROM step3;
```

giống như lập trình:

```python
step1 = ...
step2 = ...
step3 = ...
result = ...
```

---

# 3. Ví dụ đơn giản

Giả sử cần:

> Những novel đang ongoing.

```sql
WITH ongoing_novels AS (
    SELECT
        id,
        title
    FROM novels
    WHERE status = 'ongoing'
)
SELECT
    id,
    title
FROM ongoing_novels;
```

Có thể đọc như:

```text
Bước 1:
lấy ongoing novels

Bước 2:
SELECT từ kết quả đó
```

---

# 4. CTE không phải table thật

Điểm rất quan trọng:

```sql
WITH ongoing_novels AS (...)
```

không có nghĩa:

```text
CREATE TABLE ongoing_novels
```

Nó không tạo một table permanent.

CTE tồn tại trong phạm vi của statement đó.

Ví dụ:

```sql
WITH x AS (
    SELECT 1 AS value
)
SELECT *
FROM x;
```

Sau khi statement kết thúc:

```text
x
```

không tồn tại như một table bình thường.

---

# 5. CTE vs Temporary Table

### CTE

```sql
WITH x AS (...)
SELECT ...
```

Phạm vi:

```text
1 SQL statement
```

### Temporary Table

```sql
CREATE TEMP TABLE x (...);
```

có thể tồn tại trong phạm vi session/connection theo quy tắc của SQLite.

Vì vậy:

```text
CTE
→ query composition

TEMP TABLE
→ intermediate data cần tái sử dụng qua nhiều statements
```

Đừng nhầm hai thứ này.

---

# 6. CTE + WHERE

Ví dụ:

```sql
WITH recent_novels AS (
    SELECT
        id,
        title,
        updated_at
    FROM novels
    WHERE updated_at >= '2026-09-01'
)
SELECT
    id,
    title
FROM recent_novels
WHERE title LIKE 'Tiên%';
```

Ta có:

```text
novels
   ↓
recent_novels
   ↓
title LIKE
   ↓
result
```

---

# 7. CTE + JOIN

Đây là lúc CTE bắt đầu hữu ích hơn.

Giả sử muốn:

> Novel ongoing + số chapter.

```sql
WITH ongoing_novels AS (
    SELECT
        id,
        title
    FROM novels
    WHERE status = 'ongoing'
)
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM ongoing_novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title;
```

Đọc rất tự nhiên:

```text
Bước 1:
lọc ongoing novels

Bước 2:
JOIN chapters

Bước 3:
COUNT chapters
```

---

# 8. CTE + GROUP BY

Một ví dụ thực tế hơn.

Ta muốn:

> Những novel có ít nhất 100 chapters.

```sql
WITH chapter_counts AS (
    SELECT
        novel_id,
        COUNT(*) AS chapter_count
    FROM chapters
    GROUP BY novel_id
)
SELECT
    n.id,
    n.title,
    cc.chapter_count
FROM novels AS n
JOIN chapter_counts AS cc
    ON cc.novel_id = n.id
WHERE cc.chapter_count >= 100;
```

Pipeline:

```text
chapters
   ↓
GROUP BY novel_id
   ↓
chapter_counts
   ↓
JOIN novels
   ↓
WHERE chapter_count >= 100
```

---

# 9. Nếu không dùng CTE

Ta có thể viết:

```sql
SELECT
    n.id,
    n.title,
    cc.chapter_count
FROM novels AS n
JOIN (
    SELECT
        novel_id,
        COUNT(*) AS chapter_count
    FROM chapters
    GROUP BY novel_id
) AS cc
    ON cc.novel_id = n.id
WHERE cc.chapter_count >= 100;
```

Về ý tưởng:

```text
CTE
```

và:

```text
subquery trong FROM
```

có thể biểu diễn cùng một logic.

Nhưng CTE thường dễ đọc hơn khi query phức tạp.

---

# 10. CTE giống biến trong lập trình

Hãy tưởng tượng:

```sql
WITH
    ongoing AS (...),
    popular AS (...),
    recent AS (...)
SELECT ...
```

tương đương conceptually:

```python
ongoing = ...
popular = ...
recent = ...

result = ...
```

Nhưng nhớ:

> CTE là **SQL query expression**, không phải Python variable.

---

# 11. Một statement có nhiều CTE

Cú pháp:

```sql
WITH
    cte1 AS (...),
    cte2 AS (...),
    cte3 AS (...)
SELECT ...
FROM cte3;
```

Ví dụ:

```sql
WITH
    chapter_counts AS (
        SELECT
            novel_id,
            COUNT(*) AS chapter_count
        FROM chapters
        GROUP BY novel_id
    ),

    ongoing_novels AS (
        SELECT
            id,
            title
        FROM novels
        WHERE status = 'ongoing'
    )

SELECT
    n.id,
    n.title,
    cc.chapter_count
FROM ongoing_novels AS n
LEFT JOIN chapter_counts AS cc
    ON cc.novel_id = n.id;
```

---

# 12. CTE có thể tham chiếu CTE trước đó

Ví dụ:

```sql
WITH
    chapter_counts AS (
        SELECT
            novel_id,
            COUNT(*) AS chapter_count
        FROM chapters
        GROUP BY novel_id
    ),

    popular_novels AS (
        SELECT
            novel_id,
            chapter_count
        FROM chapter_counts
        WHERE chapter_count >= 100
    )

SELECT
    n.id,
    n.title,
    p.chapter_count
FROM novels AS n
JOIN popular_novels AS p
    ON p.novel_id = n.id;
```

Pipeline:

```text
chapters
   ↓
chapter_counts
   ↓
popular_novels
   ↓
JOIN novels
```

Đây chính là cách viết SQL theo **pipeline**.

---

# 13. CTE giúp SQL dễ debug hơn

Giả sử query cuối không cho kết quả đúng.

Thay vì debug toàn bộ:

```sql
WITH
    step1 AS (...),
    step2 AS (...),
    step3 AS (...)
SELECT ...
```

ta có thể tạm:

```sql
WITH
    step1 AS (...)
SELECT *
FROM step1;
```

Kiểm tra.

Sau đó:

```sql
WITH
    step1 AS (...),
    step2 AS (...)
SELECT *
FROM step2;
```

Kiểm tra tiếp.

Rất giống debug Python:

```python
step1 = ...
print(step1)

step2 = ...
print(step2)
```

---

# 14. CTE trong app crawler

Đây là ví dụ rất sát với project của bạn.

Crawler dashboard cần:

```text
Novel
- title
- status
- chapter count
- latest chapter
- latest crawl time
```

Ta có thể viết:

```sql
WITH chapter_stats AS (
    SELECT
        novel_id,
        COUNT(*) AS chapter_count,
        MAX(chapter_number) AS latest_chapter
    FROM chapters
    GROUP BY novel_id
)
SELECT
    n.id,
    n.title,
    n.status,
    COALESCE(cs.chapter_count, 0) AS chapter_count,
    cs.latest_chapter
FROM novels AS n
LEFT JOIN chapter_stats AS cs
    ON cs.novel_id = n.id
ORDER BY n.updated_at DESC;
```

Rất dễ đọc.

---

# 15. Tại sao `COALESCE`?

Novel chưa có chapter:

```text
chapter_stats
```

không có row.

Do:

```sql
LEFT JOIN
```

nên:

```text
cs.chapter_count
=
NULL
```

Ta dùng:

```sql
COALESCE(
    cs.chapter_count,
    0
)
```

để biến:

```text
NULL → 0
```

Kết quả:

```text
Novel A | 100
Novel B | 50
Novel C | 0
```

---

# 16. CTE không tự động nhanh hơn

Đây là điểm cực kỳ quan trọng sau Part V.

Đừng nghĩ:

```text
Subquery
 ↓
chậm

CTE
 ↓
nhanh
```

Không có quy tắc như vậy.

CTE chủ yếu giúp:

```text
readability
maintainability
query composition
```

Performance phụ thuộc vào:

```text
query planner
indexes
data size
join strategy
statistics
SQLite version
```

Vẫn phải:

```sql
EXPLAIN QUERY PLAN
```

và benchmark.

---

# 17. CTE không phải "cache"

Ví dụ:

```sql
WITH x AS (
    SELECT ...
)
SELECT ...
FROM x;
```

Không nên tự động hiểu:

```text
x = cached result
```

CTE là một phần của câu SQL.

SQLite có thể lựa chọn cách thực hiện phù hợp, chẳng hạn inline hoặc materialize trong những trường hợp được planner hỗ trợ/khuyến nghị.

Điểm cần nhớ:

> **CTE là công cụ tổ chức query, không phải cơ chế cache.**

---

# 18. `MATERIALIZED` và `NOT MATERIALIZED`

SQLite hỗ trợ các gợi ý materialization cho CTE trong cú pháp:

```sql
WITH x AS MATERIALIZED (
    ...
)
```

hoặc:

```sql
WITH x AS NOT MATERIALIZED (
    ...
)
```

Nhưng đây là **advanced topic**.

Ở giai đoạn này chỉ cần hiểu:

```text
MATERIALIZED
→ có thể buộc cách xử lý intermediate result

NOT MATERIALIZED
→ gợi ý không materialize
```

Không nên sử dụng chúng tùy tiện để "ép nhanh".

---

# 19. CTE trong Python

Không có gì đặc biệt.

Python chỉ gửi SQL:

```python id="zqkq8a"
sql = """
WITH chapter_stats AS (
    SELECT
        novel_id,
        COUNT(*) AS chapter_count,
        MAX(chapter_number) AS latest_chapter
    FROM chapters
    GROUP BY novel_id
)
SELECT
    n.id,
    n.title,
    n.status,
    COALESCE(cs.chapter_count, 0) AS chapter_count,
    cs.latest_chapter
FROM novels AS n
LEFT JOIN chapter_stats AS cs
    ON cs.novel_id = n.id
ORDER BY n.updated_at DESC
"""

rows = conn.execute(sql).fetchall()
```

`sqlite3` không cần API riêng cho CTE.

---

# 20. Repository

Ta có thể đưa query vào:

```python id="r7z9kp"
class NovelQueryRepository:

    def __init__(self, conn):
        self._conn = conn

    def list_dashboard(self):
        return self._conn.execute(
            """
            WITH chapter_stats AS (
                SELECT
                    novel_id,
                    COUNT(*) AS chapter_count,
                    MAX(chapter_number)
                        AS latest_chapter
                FROM chapters
                GROUP BY novel_id
            )
            SELECT
                n.id,
                n.title,
                n.status,
                COALESCE(
                    cs.chapter_count,
                    0
                ) AS chapter_count,
                cs.latest_chapter
            FROM novels AS n
            LEFT JOIN chapter_stats AS cs
                ON cs.novel_id = n.id
            ORDER BY n.updated_at DESC
            """
        ).fetchall()
```

Application:

```python id="m4o9q1"
items = query_repo.list_dashboard()
```

---

# 21. CTE + Parameter

CTE vẫn sử dụng parameter bình thường.

```python id="u5y0j4"
sql = """
WITH ongoing AS (
    SELECT
        id,
        title
    FROM novels
    WHERE source = ?
      AND status = 'ongoing'
)
SELECT
    id,
    title
FROM ongoing
ORDER BY title;
"""

rows = conn.execute(
    sql,
    ("site_a",),
).fetchall()
```

Không được biến parameter thành f-string.

Sai:

```python id="b6yd4c"
f"WHERE source = '{source}'"
```

Đúng:

```python id="3e6e2d"
"WHERE source = ?"
```

---

# 22. CTE + DELETE

CTE không chỉ dùng với SELECT.

Ví dụ SQLite hỗ trợ CTE trước các câu lệnh như:

```sql
WITH ...
DELETE ...
```

Ví dụ conceptual:

```sql
WITH old_chapters AS (
    SELECT id
    FROM chapters
    WHERE ...
)
DELETE FROM chapters
WHERE id IN (
    SELECT id
    FROM old_chapters
);
```

Điều này rất hữu ích cho maintenance.

---

# 23. CTE + UPDATE

Tương tự:

```sql
WITH stale_novels AS (
    SELECT id
    FROM novels
    WHERE status = 'ongoing'
      AND updated_at < ?
)
UPDATE novels
SET status = 'stale'
WHERE id IN (
    SELECT id
    FROM stale_novels
);
```

Pipeline:

```text
find rows
   ↓
stale_novels
   ↓
UPDATE
```

---

# 24. CTE + INSERT

Cũng có thể dùng CTE trong các câu lệnh ghi dữ liệu khi cú pháp statement phù hợp.

Ví dụ conceptually:

```sql
WITH source_rows AS (
    SELECT ...
)
INSERT INTO ...
SELECT ...
FROM source_rows;
```

Đây là một pattern rất mạnh:

```text
SELECT / transform
        ↓
INSERT
```

---

# 25. CTE và transaction

CTE **không phải transaction**.

Hai khái niệm hoàn toàn khác nhau:

```text
CTE
→ tổ chức một SQL statement
```

```text
Transaction
→ đảm bảo atomicity giữa nhiều operations
```

Ví dụ:

```text
BEGIN
    INSERT ...
    UPDATE ...
    DELETE ...
COMMIT
```

có thể chứa các statement dùng CTE.

---

# 26. CTE và Repository Pattern

Đây là điểm quan trọng với architecture bạn đang học.

Không nên sợ query dài:

```python
class NovelQueryRepository:
    ...
```

Repository là nơi thích hợp để encapsulate SQL phức tạp.

Ví dụ:

```text
Application
      ↓
NovelQueryRepository
      ↓
WITH chapter_stats AS (...)
      ↓
SQLite
```

Application không cần biết:

```text
JOIN
GROUP BY
CTE
COALESCE
```

nội bộ hoạt động thế nào.

---

# 27. CTE và CQRS

Đây là chỗ kết nối rất đẹp với những gì bạn đã học.

CQRS:

```text
Command
   ↓
Domain
   ↓
Write Model

Query
   ↓
Read Model
```

Read Model có thể được xây bằng:

```sql
WITH ...
SELECT ...
```

Ví dụ:

```text
CrawlerDashboard
       ↓
NovelQueryRepository
       ↓
CTE
       ↓
JOIN
       ↓
GROUP BY
       ↓
Read Model
```

CTE đặc biệt phù hợp với những query dạng dashboard/report.

---

# 28. CTE vs View

Một câu hỏi quan trọng:

> Khi nào dùng CTE, khi nào dùng VIEW?

### CTE

```sql
WITH x AS (...)
SELECT ...
```

phù hợp với:

```text
một query cụ thể
```

### VIEW

```sql
CREATE VIEW novel_stats AS
SELECT ...
```

phù hợp khi:

```text
logic query được tái sử dụng
nhiều query khác cùng sử dụng
```

Mental model:

```text
CTE
→ local query abstraction

VIEW
→ database-level reusable abstraction
```

---

# 29. Ví dụ VIEW

Ta có:

```sql
CREATE VIEW novel_chapter_stats AS
SELECT
    novel_id,
    COUNT(*) AS chapter_count,
    MAX(chapter_number) AS latest_chapter
FROM chapters
GROUP BY novel_id;
```

Sau đó:

```sql
SELECT
    n.title,
    s.chapter_count,
    s.latest_chapter
FROM novels n
LEFT JOIN novel_chapter_stats s
    ON s.novel_id = n.id;
```

Trong khi CTE:

```sql
WITH chapter_stats AS (...)
SELECT ...
```

chỉ phục vụ statement hiện tại.

---

# 30. CTE vs Subquery

|                                  | CTE           | Subquery |
| -------------------------------- | ------------- | -------- |
| Dễ đọc                           | ⭐⭐⭐⭐⭐         | ⭐⭐⭐      |
| Query nhỏ                        | Có thể hơi dư | Rất tốt  |
| Query lớn                        | Rất tốt       | Dễ rối   |
| Đặt tên intermediate             | ✅             | Alias    |
| Nhiều bước                       | ✅             | Khó đọc  |
| Tái sử dụng qua nhiều statements | ❌             | ❌        |
| Database-level reusable          | ❌             | ❌        |
| VIEW thay thế                    | —             | —        |

Không có:

```text
CTE luôn tốt hơn subquery
```

Mà:

> **Chọn cấu trúc làm query dễ hiểu và phù hợp workload.**

---

# 31. Một query nhiều bước thực tế

Giả sử yêu cầu:

> Tìm 20 novel ongoing, có ít nhất 50 chapter, cập nhật gần đây, hiển thị chapter mới nhất.

Ta có thể chia:

```sql id="4aqgqk"
WITH
    chapter_stats AS (
        SELECT
            novel_id,
            COUNT(*) AS chapter_count,
            MAX(chapter_number)
                AS latest_chapter
        FROM chapters
        GROUP BY novel_id
    ),

    qualified_novels AS (
        SELECT
            n.id,
            n.title,
            n.updated_at,
            cs.chapter_count,
            cs.latest_chapter
        FROM novels AS n
        JOIN chapter_stats AS cs
            ON cs.novel_id = n.id
        WHERE n.status = 'ongoing'
          AND cs.chapter_count >= 50
    )

SELECT
    id,
    title,
    chapter_count,
    latest_chapter
FROM qualified_novels
ORDER BY updated_at DESC
LIMIT 20;
```

Đọc như một chương trình:

```text
chapter_stats
      ↓
qualified_novels
      ↓
ORDER BY
      ↓
LIMIT
```

---

# 32. Nhưng có thể tối ưu hơn

Đừng vội nghĩ:

```text
CTE = optimized
```

Ta vẫn cần:

```sql
EXPLAIN QUERY PLAN
```

và kiểm tra:

```text
SCAN
SEARCH
INDEX
TEMP B-TREE
```

Sau đó:

```text
benchmark
```

Đây là bài học của Buổi 45.

---

# 33. CTE + Index

CTE không thay thế index.

Ví dụ:

```sql
WITH ongoing AS (
    SELECT *
    FROM novels
    WHERE status = 'ongoing'
)
SELECT *
FROM ongoing
WHERE source = ?;
```

Nếu query thực tế cần:

```text
source
+
status
```

thì vẫn phải suy nghĩ về:

```sql
CREATE INDEX ...
ON novels(source, status);
```

hoặc index phù hợp với workload.

CTE chỉ thay đổi **cách tổ chức SQL**, không tự tạo index.

---

# 34. Một lỗi tư duy phổ biến

Đừng nghĩ:

```text
CTE
 ↓
temporary table
 ↓
đã lưu dữ liệu
```

Sai.

Hãy nghĩ:

```text
CTE
 ↓
named query expression
 ↓
part of current SQL statement
```

---

# 35. Mental Model

Đây là cách tôi muốn bạn ghi nhớ CTE:

```text
               SQL phức tạp
                    │
                    ↓
          ┌─────────────────┐
          │      WITH       │
          └────────┬────────┘
                   ↓
             CTE step 1
                   ↓
             CTE step 2
                   ↓
             CTE step 3
                   ↓
             Main Query
                   ↓
                Result
```

Hoặc giống Python:

```text
step1 = ...
step2 = transform(step1)
step3 = transform(step2)

result = query(step3)
```

---

# 36. Bài tập

### Bài 1 — Cơ bản

Viết CTE:

```text
ongoing_novels
```

chứa:

```text
id
title
```

sau đó SELECT từ CTE.

---

### Bài 2 — Chapter count

Viết:

```text
chapter_counts
```

trả:

```text
novel_id
chapter_count
```

Sau đó JOIN với `novels`.

---

### Bài 3 — Qualified novels

Tìm:

```text
ongoing novels
có >= 100 chapters
```

dùng:

```text
CTE
+
GROUP BY
+
COUNT
+
JOIN
```

---

### Bài 4 — Dashboard

Một query trả:

```text
id
title
status
chapter_count
latest_chapter
```

Yêu cầu:

```text
novel không có chapter
→ chapter_count = 0
```

Gợi ý:

```text
WITH
chapter_stats AS (...)
```

*

```text
LEFT JOIN
```

*

```text
COALESCE
```

---

### Bài 5 — Debug CTE

Cho:

```sql
WITH
    a AS (...),
    b AS (...),
    c AS (...)
SELECT ...
FROM c;
```

Hãy giải thích:

```text
a làm gì?
b lấy dữ liệu từ đâu?
c phụ thuộc vào gì?
query cuối sử dụng c thế nào?
```

Mục tiêu là tập suy nghĩ SQL theo **data pipeline** thay vì nhìn SQL như một câu lệnh khổng lồ.

---

# 37. Roadmap Part VI

```text
46  CTE (WITH)                    ← hôm nay
47  Recursive CTE
48  Window Functions
49  Window Functions Deep Dive
50  EXISTS Deep Dive
51  UPSERT
52  RETURNING
```

**Buổi 47 — Recursive CTE** sẽ nâng CTE lên một cấp độ rất thú vị:

```text
category
   ↓
subcategory
   ↓
subcategory
   ↓
...
```

Ta sẽ dùng:

```sql
WITH RECURSIVE
```

để duyệt **cây dữ liệu trong SQLite** — ví dụ category tree, folder tree, comment tree hoặc cấu trúc phân cấp bất kỳ.
