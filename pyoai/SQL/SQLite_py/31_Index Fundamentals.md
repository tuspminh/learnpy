Bạn vừa học Buổi 31 rồi, nên mình sẽ **dạy lại Buổi 31 theo kiểu deep dive**, tập trung vào bản chất và thực hành với project Novel Reader.

# Buổi 31 — Index Fundamentals — Deep Dive

## 1. Vấn đề mà Index giải quyết

Giả sử database có:

```text
chapters
10,000,000 rows
```

Bạn chạy:

```sql
SELECT *
FROM chapters
WHERE novel_id = 123;
```

Nếu không có index phù hợp, SQLite có thể phải kiểm tra rất nhiều rows:

```text
chapter 1       novel_id = 1     ❌
chapter 2       novel_id = 99    ❌
chapter 3       novel_id = 123   ✅
chapter 4       novel_id = 8     ❌
...
chapter 10M
```

Đây là:

```text
SCAN
```

Vấn đề không phải SQL sai.

Vấn đề là:

> **SQLite không có cấu trúc phụ trợ đủ tốt để tìm `novel_id = 123`.**

---

# 2. Index giống mục lục

Hãy tưởng tượng một cuốn sách 10.000 trang.

Không có mục lục:

```text
Trang 1
Trang 2
Trang 3
...
Trang 10000
```

Tìm:

```text
SQLite
```

→ phải tìm rất nhiều trang.

Có mục lục:

```text
SQLite → trang 7312
```

→ đi thẳng tới khu vực cần tìm.

Database Index cũng có ý tưởng tương tự:

```text
Table
        +
Index
```

Index giúp database **định vị dữ liệu** nhanh hơn.

---

# 3. Tạo Index

Ví dụ:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Đọc tên:

```text
CREATE INDEX
    idx_chapters_novel_id
ON
    chapters(novel_id)
```

Có nghĩa:

> Tạo một index tên `idx_chapters_novel_id` cho column `novel_id` của bảng `chapters`.

---

# 4. Sau khi có Index

Query:

```sql
SELECT *
FROM chapters
WHERE novel_id = 123;
```

SQLite có thể thực hiện theo hướng:

```text
              INDEX
                │
                │ novel_id = 123
                ▼
          vị trí các rows
                │
                ▼
             TABLE
                │
                ▼
             result
```

Thay vì:

```text
TABLE
 ↓
SCAN toàn bộ
```

---

# 5. Kiểm tra bằng EXPLAIN QUERY PLAN

Đây là công cụ bạn cần sử dụng rất nhiều từ Part V.

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 123;
```

Nếu chưa có index, có thể thấy:

```text
SCAN chapters
```

Sau đó:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Chạy lại:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 123;
```

có thể thấy dạng:

```text
SEARCH chapters USING INDEX idx_chapters_novel_id
```

Mental model:

```text
SCAN
 ↓
nhiều dữ liệu

SEARCH
 ↓
tìm qua cấu trúc phù hợp
```

---

# 6. Nhưng đừng hiểu SEARCH = luôn nhanh

Đây là điểm quan trọng.

SQLite query planner có thể quyết định:

```text
SCAN
```

ngay cả khi bạn đã tạo index.

Ví dụ:

```text
1,000 rows

status:
ongoing    950
completed   50
```

Query:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing';
```

Index:

```sql
CREATE INDEX idx_novels_status
ON novels(status);
```

SQLite có thể nhận thấy:

> Gần như toàn bộ table đều phải lấy.

Trong trường hợp đó scan table có thể hợp lý hơn.

Vì vậy:

> **INDEX không có nghĩa SQLite bắt buộc phải dùng INDEX.**

---

# 7. Selectivity

Đây là khái niệm cần nhớ.

**Selectivity** nói đơn giản là:

> Điều kiện lọc được bao nhiêu dữ liệu.

Ví dụ:

```text
1,000,000 rows
```

Query:

```sql
WHERE id = 123456
```

Nếu `id` unique:

```text
1 row
```

→ rất selective.

Trong khi:

```sql
WHERE status = 'ongoing'
```

có thể:

```text
900,000 rows
```

→ ít selective.

Mental model:

```text
Điều kiện càng loại bỏ nhiều rows
→ càng selective
→ index thường càng có giá trị
```

Nhưng query planner vẫn là nơi quyết định execution plan thực tế.

---

# 8. Index không miễn phí

Đây là điều cực kỳ quan trọng.

Giả sử:

```text
chapters
```

có:

```text
5 indexes
```

Khi:

```sql
INSERT INTO chapters ...
```

SQLite không chỉ cập nhật table.

Nó còn phải duy trì các index liên quan.

```text
INSERT
  │
  ├── table
  ├── index A
  ├── index B
  ├── index C
  ├── index D
  └── index E
```

Do đó:

```text
Index
 ├── READ performance ↑
 └── WRITE cost ↑
```

Ngoài ra:

```text
Disk usage ↑
```

---

# 9. Đây là lý do không tạo index mọi column

Ví dụ schema:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

Không nên lập tức làm:

```sql
CREATE INDEX idx_title ...
CREATE INDEX idx_author ...
CREATE INDEX idx_source ...
CREATE INDEX idx_status ...
CREATE INDEX idx_description ...
CREATE INDEX idx_created_at ...
CREATE INDEX idx_updated_at ...
```

Chỉ vì:

> "Index sẽ nhanh hơn."

Không.

Hãy hỏi:

```text
Application thực sự query như thế nào?
```

---

# 10. Query Workload

Giả sử Novel Reader có các use case:

```text
1. Lấy novel theo ID
2. Lấy chapters theo novel_id
3. Lấy chapter theo novel_id + chapter_number
4. Lấy chapter mới nhất
5. Tìm novel theo title
6. Lọc novel theo status
```

Ta có thể suy ra các query:

```sql
WHERE id = ?
```

```sql
WHERE novel_id = ?
```

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

```sql
WHERE novel_id = ?
ORDER BY chapter_number DESC
LIMIT 1
```

Đây mới là cơ sở để thiết kế index.

---

# 11. Index cho Foreign Key

Schema:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,

    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Query thường xuyên:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Đây là một index rất hợp lý.

---

# 12. Foreign Key không tự động đồng nghĩa với Index

Đừng nhầm:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

với:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Hai thứ giải quyết hai vấn đề:

```text
FOREIGN KEY
     ↓
Data Integrity

INDEX
     ↓
Query Performance
```

---

# 13. Index cho JOIN

Query:

```sql
SELECT
    n.title,
    c.chapter_number
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?;
```

SQLite phải tìm các:

```text
chapters.novel_id
```

phù hợp.

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

rất hữu ích cho workload này.

---

# 14. Index cho ORDER BY

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

Một index rất đáng chú ý:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Tại sao?

Query có:

```text
WHERE
    novel_id

ORDER BY
    chapter_number
```

Index có cùng cấu trúc:

```text
novel_id
    ↓
chapter_number
```

Đây là tiền đề của **Composite Index**, sẽ học sâu ở Buổi 33.

---

# 15. Index và LIMIT

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 20;
```

Nếu index:

```sql
(novel_id, chapter_number)
```

phù hợp, SQLite có thể tìm đúng vùng dữ liệu rồi lấy 20 rows cần thiết.

Điều này đặc biệt hữu ích với Novel Reader.

---

# 16. Primary Key

Với:

```sql
id INTEGER PRIMARY KEY
```

SQLite có cơ chế đặc biệt liên quan đến `rowid`.

Do đó thường không cần:

```sql
CREATE INDEX idx_novels_id
ON novels(id);
```

Đây có thể là index dư thừa.

---

# 17. UNIQUE cũng cần chú ý

Ví dụ:

```sql
url TEXT NOT NULL UNIQUE
```

SQLite phải đảm bảo:

```text
url không trùng
```

nên uniqueness được hỗ trợ bởi cấu trúc nội bộ phù hợp.

Do đó không nên vô thức tạo thêm:

```sql
CREATE INDEX idx_novels_url
ON novels(url);
```

nếu đã có UNIQUE tương ứng.

---

# 18. Composite UNIQUE

Ta có:

```sql
UNIQUE(novel_id, chapter_number)
```

Nó đảm bảo:

```text
Novel 1 → Chapter 1
Novel 1 → Chapter 2
Novel 2 → Chapter 1
Novel 2 → Chapter 2
```

nhưng không cho:

```text
Novel 1 → Chapter 1
Novel 1 → Chapter 1
```

Cấu trúc này cũng có thể phục vụ các query phù hợp với prefix:

```sql
WHERE novel_id = ?
```

hoặc:

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

---

# 19. Một Index có thứ tự

Giả sử:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Mental model:

```text
novel_id
   │
   ├── chapter 1
   ├── chapter 2
   ├── chapter 3
   └── chapter 4
```

Rồi:

```text
novel 2
   ├── chapter 1
   ├── chapter 2
   └── chapter 3
```

Do đó:

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

là một query pattern rất tự nhiên cho index này.

---

# 20. Nhưng `chapter_number` đơn độc thì sao?

Query:

```sql
SELECT *
FROM chapters
WHERE chapter_number = 100;
```

Index:

```text
(novel_id, chapter_number)
```

không phải lựa chọn tương đương với:

```text
(chapter_number)
```

vì column đầu tiên của composite index là:

```text
novel_id
```

Đây là nguyên tắc:

> **Leftmost prefix**

Ta sẽ dành cả Buổi 33 để đào sâu vấn đề này.

---

# 21. Index và DELETE

Query:

```sql
DELETE FROM chapters
WHERE novel_id = ?;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

giúp SQLite xác định các rows cần xử lý hiệu quả hơn trong nhiều trường hợp.

Điều này rất đáng chú ý khi:

```sql
ON DELETE CASCADE
```

và một Novel có hàng chục nghìn chapters.

---

# 22. Index và UPDATE

Query:

```sql
UPDATE chapters
SET content = ?
WHERE novel_id = ?
  AND chapter_number = ?;
```

Index:

```sql
(novel_id, chapter_number)
```

giúp tìm row cần update.

Nhưng nếu bạn update chính column nằm trong index:

```sql
UPDATE chapters
SET chapter_number = ?
...
```

SQLite còn phải cập nhật index tương ứng.

---

# 23. Index dư thừa

Giả sử:

```sql
UNIQUE(novel_id, chapter_number)
```

và bạn lại tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Trong nhiều trường hợp đây là cấu trúc dư thừa.

Trước khi tạo index:

```text
Đã có constraint/index tương đương chưa?
```

hãy kiểm tra:

```sql
PRAGMA index_list(chapters);
```

---

# 24. Xem index bằng SQLite

```sql
PRAGMA index_list(chapters);
```

Sau đó:

```sql
PRAGMA index_info(idx_chapters_novel_id);
```

Bạn có thể dùng:

```python
rows = conn.execute("PRAGMA index_list(chapters)").fetchall()

for row in rows:
    print(dict(row))
```

Và:

```python
rows = conn.execute("PRAGMA index_info(idx_chapters_novel_id)").fetchall()

for row in rows:
    print(dict(row))
```

Đây là kỹ năng rất phù hợp với Connection Manager mà chúng ta đã xây dựng ở các buổi trước.

---

# 25. Đừng nhầm Index với Cache

Index:

```text
≠
cache
```

Index là một **data structure phục vụ truy vấn**.

Không phải:

```text
CREATE INDEX
↓
mọi dữ liệu được đưa vào RAM
```

SQLite vẫn quản lý việc đọc page từ database/storage/cache theo cơ chế riêng.

---

# 26. SELECT * và Index

Giả sử:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Bạn có index:

```text
novel_id
```

SQLite có thể dùng index để tìm rows.

Nhưng sau đó vẫn cần lấy:

```text
id
chapter_number
title
content
```

từ table.

Mental model:

```text
INDEX
 ↓
tìm row
 ↓
TABLE
 ↓
lấy dữ liệu
```

Buổi 34 sẽ học:

> **Covering Index**

khi index có thể chứa đủ những dữ liệu mà query cần trong một số trường hợp.

---

# 27. Index cho Search

Query:

```sql
SELECT id, title
FROM novels
WHERE title = ?;
```

Có thể tạo:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Nhưng search thực tế thường là:

```sql
WHERE title LIKE '%Tiên%'
```

Đây là câu chuyện khác.

Index B-tree thông thường không phải giải pháp hoàn hảo cho mọi dạng substring search.

Sau này:

```text
LIKE
FTS5
Expression Index
```

sẽ được đào sâu.

---

# 28. Một ví dụ quan trọng

Hai query:

```sql
WHERE title = 'Tiên Nghịch'
```

và:

```sql
WHERE title LIKE '%Tiên%'
```

không nên được xem là cùng một workload.

Query đầu:

```text
exact lookup
```

Query sau:

```text
substring search
```

Do đó:

```text
Index design
```

phụ thuộc rất nhiều vào **pattern của query**.

---

# 29. N+1 và Index

Index có thể làm N+1 nhanh hơn.

Nhưng:

> **Index không giải quyết N+1 về mặt kiến trúc.**

Ví dụ:

```python
novels = get_novels()

for novel in novels:
    get_chapters(novel.id)
```

Có index:

```text
1 query
+
100 indexed queries
=
101 queries
```

Không có index:

```text
1 query
+
100 scans
```

Index giúp từng query tốt hơn, nhưng vấn đề N+1 vẫn tồn tại.

Đây là lý do Part V sau này có riêng:

```text
43. N+1 Query
```

---

# 30. Python + EXPLAIN

Ta có thể xây helper:

```python
def explain_query(conn, sql, params=()):
    rows = conn.execute(
        "EXPLAIN QUERY PLAN " + sql,
        params,
    ).fetchall()

    for row in rows:
        print(dict(row))
```

Ví dụ:

```python
explain_query(
    conn,
    """
    SELECT
        id,
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
    ORDER BY chapter_number
    LIMIT ?
    """,
    (10, 50),
)
```

Điều này rất phù hợp để làm tool debug nội bộ cho project.

---

# 31. Một nguyên tắc quan trọng hơn cả INDEX

Đừng bắt đầu bằng:

```text
"Index nào tốt?"
```

Hãy bắt đầu:

```text
"Application của tôi query database thế nào?"
```

Sau đó:

```text
Use case
   ↓
SQL query
   ↓
Query pattern
   ↓
Index
   ↓
EXPLAIN
   ↓
Benchmark
```

---

# 32. Workflow chuẩn

Từ hôm nay, khi gặp query chậm:

### Bước 1

Viết query chính xác.

### Bước 2

Chạy:

```sql
EXPLAIN QUERY PLAN
```

### Bước 3

Xem:

```text
SCAN?
SEARCH?
INDEX nào?
```

### Bước 4

Phân tích:

```text
WHERE
JOIN
ORDER BY
LIMIT
```

### Bước 5

Thiết kế index.

### Bước 6

EXPLAIN lại.

### Bước 7

Benchmark.

### Bước 8

Kiểm tra write overhead.

---

# 33. Bài tập thực chiến

Tạo:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT
);
```

Sau đó insert một lượng dữ liệu đủ lớn.

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = 100
ORDER BY chapter_number
LIMIT 50;
```

### Trước index

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = 100
ORDER BY chapter_number
LIMIT 50;
```

Ghi lại kết quả.

### Tạo index

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

### Sau index

Chạy lại:

```sql
EXPLAIN QUERY PLAN
...
```

So sánh.

---

# 34. Bài tập tư duy

Cho:

```text
1,000,000 novels
```

và:

```text
status:
ongoing   = 950,000
completed = 50,000
```

Query:

```sql
WHERE status = 'ongoing'
```

Câu hỏi:

> Index `status` có chắc chắn giúp query nhanh hơn không?

**Không.**

Vì:

```text
950,000 / 1,000,000
```

rows được chọn.

Query planner có thể thấy scan toàn table hợp lý hơn.

---

# 35. Bài tập thiết kế Index

Cho query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 20;
```

Bạn có ba lựa chọn:

```text
A. (novel_id)

B. (chapter_number)

C. (novel_id, chapter_number)
```

Hãy tự trả lời:

> Vì sao C phù hợp nhất với query pattern này?

Gợi ý:

```text
WHERE
   ↓
novel_id

ORDER BY
   ↓
chapter_number
```

---

# 36. Mental Model quan trọng nhất

Bạn nên ghi lại:

```text
                 Application
                     │
                     ▼
                    Query
                     │
             ┌───────┼───────┐
             ▼       ▼       ▼
           WHERE    JOIN   ORDER BY
             │       │       │
             └───────┼───────┘
                     ▼
                   INDEX
                     │
                     ▼
              Query Planner
                │       │
                ▼       ▼
             SEARCH    SCAN
```

Và:

```text
INDEX
  │
  ├── READ ↑
  ├── JOIN ↑
  ├── một số ORDER BY ↑
  ├── một số UPDATE/DELETE ↑
  │
  ├── WRITE cost ↑
  └── DISK usage ↑
```

---

# 37. Checklist khi tạo một Index

Trước khi viết:

```sql
CREATE INDEX ...
```

hãy hỏi 7 câu:

```text
1. Query nào cần index này?
2. Query đó chạy thường xuyên không?
3. WHERE/JOIN column nào?
4. ORDER BY có liên quan không?
5. Đã có index/UNIQUE tương tự chưa?
6. Index này có làm INSERT/UPDATE/DELETE tốn thêm đáng kể không?
7. EXPLAIN QUERY PLAN có chứng minh lợi ích không?
```

Nếu không trả lời được câu 1:

> **Chưa nên tạo index.**

---

# 38. Part V hiện tại

```text
31. Index Fundamentals          ✅
32. B-Tree & SQLite Index
    Internals
33. Composite Index Deep Dive
34. Covering Index
35. Partial Index
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

### Buổi 32

Chúng ta sẽ đi sâu hơn rất nhiều:

```text
CREATE INDEX
      ↓
     B-Tree
      ↓
Root Page
      ↓
Interior Page
      ↓
Leaf Page
      ↓
Key
      ↓
Row reference
```

và đặc biệt giải thích **tại sao B-Tree giúp SQLite tìm kiếm hiệu quả hơn việc scan toàn bộ table**.
