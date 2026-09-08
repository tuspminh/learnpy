# Buổi 31 — Index Fundamentals

Từ Buổi 30, chúng ta đã biết:

```text
Query
  ↓
EXPLAIN QUERY PLAN
  ↓
SCAN / SEARCH
  ↓
INDEX
```

Hôm nay chúng ta bắt đầu **Part V — Index & Query Optimization**.

Mục tiêu của Buổi 31 không phải học thuộc cú pháp `CREATE INDEX`, mà phải hiểu:

> **Index là gì, tại sao nó giúp query nhanh, khi nào nên tạo index và khi nào index lại làm hệ thống chậm hơn.**

---

# 1. Index là gì?

Hãy tưởng tượng bảng:

```text
novels
┌────┬──────────────────┬─────────────┐
│ id │ title            │ author      │
├────┼──────────────────┼─────────────┤
│ 1  │ Tiên Nghịch      │ Nhĩ Căn     │
│ 2  │ Phàm Nhân Tu Tiên│ Vong Ngữ    │
│ 3  │ Đấu Phá Thương Kh│ Thiên Tằm Thổ│
│... │ ...              │ ...         │
└────┴──────────────────┴─────────────┘
```

Query:

```sql
SELECT *
FROM novels
WHERE title = ?;
```

Nếu không có index trên `title`, SQLite có thể phải tìm bằng cách quét nhiều row.

```text
novels
  ↓
row 1 → không
row 2 → không
row 3 → không
row 4 → không
...
row N → tìm thấy
```

Đây là:

```text
SCAN
```

---

# 2. Khi có INDEX

Ta tạo:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

SQLite có thêm một cấu trúc dữ liệu phục vụ việc tìm kiếm.

```text
              INDEX
                │
                ▼
           title = ?
                │
                ▼
             row id
                │
                ▼
             novels
```

Thay vì phải kiểm tra toàn bộ bảng:

```text
1 → 2 → 3 → 4 → ... → N
```

SQLite có thể tìm qua index rồi đến row cần thiết.

---

# 3. INDEX giống mục lục sách

Đây là analogy rất tốt.

Không có index:

```text
Cuốn sách
───────────────
Trang 1
Trang 2
Trang 3
...
Trang 1000
```

Muốn tìm:

```text
"SQLite"
```

phải đọc từng trang.

Có index:

```text
INDEX

SQLite .......... 527
SQLite .......... 742
SQLite .......... 891
```

→ nhảy thẳng đến vị trí cần tìm.

Database index cũng có ý tưởng tương tự.

---

# 4. Nhưng INDEX không chứa toàn bộ bảng

Một index thường chứa thông tin kiểu:

```text
indexed value
      +
reference đến row
```

Ví dụ:

```text
title index

"Đấu Phá..."       → row 3
"Phàm Nhân..."     → row 2
"Tiên Nghịch"      → row 1
```

Nó giúp SQLite biết:

> "Giá trị này nằm ở đâu?"

---

# 5. Cú pháp CREATE INDEX

Cơ bản:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Tên:

```text
idx_novels_title
```

là tên index.

Column:

```text
title
```

là column được index.

---

# 6. Kiểm tra index

SQLite:

```sql
PRAGMA index_list(novels);
```

Python:

```python
rows = conn.execute("PRAGMA index_list(novels)").fetchall()

for row in rows:
    print(dict(row))
```

Bạn có thể thấy các index đang tồn tại.

---

# 7. Xem index chứa column nào

```sql
PRAGMA index_info(idx_novels_title);
```

Python:

```python
rows = conn.execute("PRAGMA index_info(idx_novels_title)").fetchall()

for row in rows:
    print(dict(row))
```

Đây là kỹ năng rất hữu ích khi debug database.

---

# 8. Index không thay thế Table

Một hiểu lầm nguy hiểm:

> "Có index rồi thì SQLite không cần đọc table."

Không phải lúc nào cũng vậy.

Ví dụ:

```sql
SELECT content
FROM chapters
WHERE novel_id = ?;
```

Index:

```text
novel_id → row
```

có thể giúp tìm row.

Nhưng `content` vẫn nằm trong table.

Mô hình:

```text
INDEX
  │
  │ tìm row
  ▼
TABLE
  │
  │ lấy content
  ▼
Result
```

Sau này khi học **Covering Index**, chúng ta sẽ thấy trường hợp index có thể chứa đủ dữ liệu query cần.

---

# 9. Index và SELECT

Đây là trường hợp dễ thấy nhất.

```sql
SELECT *
FROM novels
WHERE source = ?;
```

Nếu query này được chạy thường xuyên:

```sql
CREATE INDEX idx_novels_source
ON novels(source);
```

có thể giúp SQLite tìm nhanh hơn.

Nhưng phải kiểm tra:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM novels
WHERE source = 'site_a';
```

---

# 10. Index và WHERE

Những query thường có khả năng hưởng lợi:

```sql
WHERE id = ?
```

```sql
WHERE novel_id = ?
```

```sql
WHERE status = ?
```

```sql
WHERE created_at >= ?
```

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

Nhưng:

> **Không phải cứ column xuất hiện trong WHERE là phải tạo index.**

Query planner còn xét:

* số lượng row
* độ chọn lọc của điều kiện
* index hiện có
* ORDER BY
* JOIN
* statistics
* chi phí truy cập

---

# 11. Selectivity

Một khái niệm rất quan trọng:

> **Selectivity — độ chọn lọc của điều kiện.**

Giả sử:

```text
1,000,000 novels
```

Column:

```text
id
```

mỗi ID gần như duy nhất.

Query:

```sql
WHERE id = 123456
```

rất selective.

---

Nhưng:

```text
status
```

chỉ có:

```text
ongoing
completed
```

Query:

```sql
WHERE status = 'ongoing'
```

có thể trả về:

```text
900,000 rows
```

Index trên `status` chưa chắc luôn giúp nhiều.

SQLite có thể quyết định scan table nếu scan rẻ hơn việc dùng index rồi phải truy cập quá nhiều rows.

---

# 12. Đây là lý do EXPLAIN QUERY PLAN quan trọng

Đừng suy nghĩ:

```text
Có index
↓
SQLite chắc chắn dùng index
```

Không.

Có thể:

```text
CREATE INDEX idx_novels_status
ON novels(status);
```

nhưng SQLite vẫn chọn:

```text
SCAN novels
```

Đó có thể là quyết định hợp lý.

---

# 13. Index có thể làm WRITE chậm hơn

Đây là trade-off rất quan trọng.

Không index:

```text
INSERT
  ↓
TABLE
```

Có 3 index:

```text
INSERT
  ├── TABLE
  ├── INDEX 1
  ├── INDEX 2
  └── INDEX 3
```

Mỗi lần INSERT/UPDATE/DELETE, SQLite phải duy trì index liên quan.

Do đó:

```text
INDEX
 ├── READ ↑
 └── WRITE ↓
```

Không phải tuyệt đối trong mọi query, nhưng đây là mental model đúng.

---

# 14. Ví dụ với crawler

Crawler của bạn có thể:

```text
READ:
  tìm novel
  tìm chapter
  tìm status

WRITE:
  INSERT chapter
  UPDATE novel
  UPDATE crawl status
```

Nếu tạo quá nhiều index:

```text
chapters
 ├── idx_novel_id
 ├── idx_chapter_number
 ├── idx_title
 ├── idx_created_at
 ├── idx_updated_at
 ├── idx_content
 └── ...
```

thì INSERT chapter sẽ phải duy trì nhiều cấu trúc index.

Không tốt.

---

# 15. Index trên column có ít giá trị

Ví dụ:

```sql
status TEXT
```

chỉ:

```text
ongoing
completed
```

Index:

```sql
CREATE INDEX idx_novels_status
ON novels(status);
```

không phải vô dụng trong mọi tình huống.

Nhưng nếu:

```text
95% = ongoing
5%  = completed
```

thì query:

```sql
WHERE status = 'ongoing'
```

không chọn lọc nhiều.

SQLite có thể không dùng index.

---

# 16. Index rất hữu ích cho Foreign Key column

Đây là trường hợp cực kỳ quan trọng với project của chúng ta.

Schema:

```text
novels
   │
   │ 1
   │
   │ N
   ▼
chapters
```

Column:

```sql
chapters.novel_id
```

Query:

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

Đây là index rất tự nhiên.

---

# 17. Foreign Key ≠ Index

Nhớ kỹ:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

có nghĩa:

> đảm bảo relationship integrity.

Còn:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

có nghĩa:

> giúp tìm kiếm/join theo `novel_id`.

Hai mục đích khác nhau.

```text
FOREIGN KEY
    ↓
Correctness

INDEX
    ↓
Performance
```

---

# 18. JOIN và INDEX

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

SQLite cần tìm:

```text
chapters.novel_id
```

cho novel đó.

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

rất phù hợp với relationship này.

---

# 19. ORDER BY cũng có thể hưởng lợi từ Index

Query:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

đây là thiết kế tốt hơn index riêng lẻ:

```text
novel_id
```

và:

```text
chapter_number
```

trong nhiều trường hợp workload này.

Ta sẽ đào sâu composite index ở **Buổi 33**.

---

# 20. Index và LIMIT

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

Nếu index phù hợp:

```text
(novel_id, chapter_number)
```

SQLite có thể tìm đúng vùng dữ liệu và lấy 20 rows đầu tiên mà không cần xử lý toàn bộ chapters của novel.

Đây là một trong những lý do index + `LIMIT` rất mạnh.

---

# 21. Index và DELETE

Ví dụ:

```sql
DELETE FROM chapters
WHERE novel_id = ?;
```

Nếu không có index:

```text
SCAN chapters
```

Nếu có:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

SQLite có thể tìm các chapters thuộc novel nhanh hơn.

Điều này đặc biệt đáng chú ý khi:

```sql
ON DELETE CASCADE
```

xóa một Novel có rất nhiều Chapter.

---

# 22. Index và UPDATE

Ví dụ:

```sql
UPDATE chapters
SET content = ?
WHERE novel_id = ?
  AND chapter_number = ?;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

giúp tìm target rows.

Nhưng nếu column được UPDATE chính là column trong index, SQLite còn phải cập nhật index.

---

# 23. Unique Constraint và Index

Ta đã học:

```sql
UNIQUE(novel_id, chapter_number)
```

SQLite cần đảm bảo:

```text
(novel_id, chapter_number)
```

không trùng.

Vì vậy constraint này liên quan trực tiếp đến cấu trúc index bên dưới.

Điều đó dẫn đến một quy tắc:

> **Đừng tạo index dư thừa nếu UNIQUE/PRIMARY KEY đã cung cấp cấu trúc phù hợp.**

Ví dụ không nên tự động thêm một index trùng hoàn toàn với một unique constraint.

---

# 24. Index dư thừa

Ví dụ:

```sql
CREATE UNIQUE INDEX idx_a
ON chapters(novel_id, chapter_number);
```

rồi lại:

```sql
CREATE INDEX idx_b
ON chapters(novel_id, chapter_number);
```

Index thứ hai thường là dư thừa.

Ta có:

```text
idx_a
(novel_id, chapter_number)

idx_b
(novel_id, chapter_number)
```

Hai cấu trúc gần như phục vụ cùng một mục đích.

Hậu quả:

```text
Disk ↑
Write cost ↑
Maintenance ↑
```

---

# 25. Index không phải cache

Index:

```text
≠
RAM cache
```

Nó là một cấu trúc dữ liệu được lưu cùng database và được SQLite sử dụng để tìm dữ liệu hiệu quả hơn.

Đừng nghĩ:

```text
CREATE INDEX
↓
mọi thứ vào RAM
```

Không phải như vậy.

---

# 26. B-Tree — giới thiệu

SQLite thường sử dụng **B-tree** cho các index thông thường.

Hãy tưởng tượng:

```text
                 [50]
               /      \
           [20]        [80]
          /   \        /   \
       [10]  [30]   [60]  [90]
```

Khi tìm:

```text
80
```

không cần duyệt:

```text
10
20
30
40
...
```

mà đi theo cây.

```text
root
 ↓
80
 ↓
found
```

Buổi 32 sẽ đào sâu B-tree.

---

# 27. Vì sao B-tree tốt?

Nếu dữ liệu được tổ chức hợp lý, số bước tìm kiếm tăng chậm hơn rất nhiều so với scan tuyến tính.

Mental model:

```text
SCAN

1 → 2 → 3 → 4 → 5 → ... → N
```

Trong khi index dạng cây:

```text
          root
        /      \
      /          \
    /              \
  node            node
```

→ loại bỏ nhiều vùng không cần tìm ở mỗi bước.

Không cần nhớ chính xác complexity của từng trường hợp ở Buổi 31; chỉ cần hiểu:

> **Index biến việc tìm kiếm từ "duyệt nhiều dữ liệu" thành "đi theo cấu trúc tìm kiếm".**

---

# 28. Một ví dụ thực tế

Giả sử:

```text
chapters = 5,000,000 rows
```

Query:

```sql
SELECT
    id,
    title
FROM chapters
WHERE novel_id = 123;
```

Nếu novel 123 có:

```text
2,000 chapters
```

không có index, SQLite có thể phải xem xét rất nhiều rows để tìm 2,000 rows đó.

Có:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

SQLite có thể tìm trực tiếp vùng index liên quan tới:

```text
novel_id = 123
```

---

# 29. Nhưng dữ liệu nhỏ thì sao?

Nếu:

```text
chapters = 20 rows
```

thì index có thể không mang lại lợi ích đáng kể.

Thậm chí:

```text
index maintenance
```

có thể không đáng.

Do đó:

> **Không tối ưu premature.**

SQLite scan một table 20 rows rất nhanh.

---

# 30. Query workload quan trọng hơn schema đơn thuần

Đừng hỏi:

> "Column nào nên có index?"

Hãy hỏi:

> **"Application thường query database như thế nào?"**

Ví dụ Novel Reader:

```text
GET novel by id
GET chapters by novel_id
GET latest chapter
SEARCH novel by title
GET novels by status
GET novels by source
GET crawler jobs by status
```

Từ workload đó mới thiết kế index.

---

# 31. Tư duy từ Query → Index

Ví dụ query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

Phân tích:

```text
WHERE
    novel_id

ORDER BY
    chapter_number

LIMIT
    50
```

Candidate:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Đây là cách tư duy chúng ta sẽ sử dụng xuyên suốt Part V.

---

# 32. Python kiểm tra Query Plan

Bạn có thể viết helper:

```python
def explain_query(
    conn,
    sql: str,
    params=(),
):
    rows = conn.execute(
        "EXPLAIN QUERY PLAN " + sql,
        params,
    ).fetchall()

    for row in rows:
        print(dict(row))
```

Dùng:

```python
explain_query(
    conn,
    """
    SELECT
        id,
        title
    FROM chapters
    WHERE novel_id = ?
    """,
    (10,),
)
```

Rất hữu ích khi audit repository.

---

# 33. Repository + Performance

Ví dụ:

```python
class ChapterRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_by_novel(
        self,
        novel_id: int,
        limit: int = 50,
    ):
        return self._conn.execute(
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
            (novel_id, limit),
        ).fetchall()
```

Database layer:

```text
Repository
   ↓
SQL
   ↓
Index
   ↓
Query Planner
```

Application không cần biết index tồn tại thế nào.

---

# 34. Một index tốt phải phục vụ query thật

Ví dụ bạn tạo:

```sql
CREATE INDEX idx_novels_author
ON novels(author);
```

nhưng application không bao giờ query:

```sql
WHERE author = ?
```

thì index có thể là:

```text
không cần thiết
```

Đây là index **không có workload justification**.

---

# 35. Một nguyên tắc rất quan trọng

> **Index không phải feature của model. Index là feature của workload.**

Không nên nghĩ:

```text
Novel model
 ├── title → index
 ├── author → index
 ├── source → index
 ├── status → index
 └── url → index
```

chỉ vì các field này "có vẻ quan trọng".

Hãy nghĩ:

```text
Use Cases
   ↓
Queries
   ↓
Query patterns
   ↓
Indexes
```

---

# 36. Index Design Workflow

Từ bây giờ hãy dùng quy trình:

```text
1. Viết query
      ↓
2. Đo / EXPLAIN
      ↓
3. Xác định WHERE / JOIN / ORDER BY
      ↓
4. Thiết kế index
      ↓
5. EXPLAIN lại
      ↓
6. Benchmark
      ↓
7. Kiểm tra write overhead
```

Đây là workflow thực tế.

---

# 37. Bài thực hành lớn

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

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50;
```

### Bước 1

Chạy:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = 10
ORDER BY chapter_number
LIMIT 50;
```

### Bước 2

Tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

### Bước 3

Chạy EXPLAIN lại.

### Bước 4

So sánh.

---

# 38. Bài tập 2 — Search Novel

Query:

```sql
SELECT
    id,
    title,
    author
FROM novels
WHERE title = ?;
```

Tạo:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

Sau đó:

```sql
EXPLAIN QUERY PLAN
...
```

Quan sát sự thay đổi.

---

# 39. Bài tập 3 — JOIN

Query:

```sql
SELECT
    n.title,
    c.chapter_number,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?;
```

Kiểm tra xem:

```text
chapters.novel_id
```

có index chưa.

Nếu chưa:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Sau đó EXPLAIN lại.

---

# 40. Bài tập 4 — Tìm index dư thừa

Chạy:

```sql
PRAGMA index_list(novels);
```

và:

```sql
PRAGMA index_list(chapters);
```

Liệt kê:

```text
index name
columns
unique?
```

Sau đó xác định:

> Có index nào trùng hoặc gần như trùng chức năng không?

---

# 41. Bài tập 5 — Tư duy thiết kế

Với các query:

### Query A

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

### Query B

```sql
SELECT *
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

### Query C

```sql
SELECT *
FROM chapters
WHERE chapter_number = ?;
```

Hãy suy nghĩ:

```text
Index nào?

(novel_id)
(novel_id, chapter_number)
(chapter_number)
```

Không cần trả lời ngay; hãy tự phân tích theo query workload.

---

# 42. Những gì bạn cần nhớ sau Buổi 31

### INDEX là gì?

```text
Cấu trúc dữ liệu giúp SQLite tìm dữ liệu hiệu quả hơn.
```

### INDEX giúp gì?

```text
READ
WHERE
JOIN
ORDER BY
một số DELETE/UPDATE
```

### INDEX có giá không?

Có:

```text
Disk
+
INSERT cost
+
UPDATE cost
+
DELETE cost
+
maintenance
```

### Có phải index nào cũng được SQLite dùng?

**Không.**

### Làm sao biết?

```sql
EXPLAIN QUERY PLAN
```

### Index dựa vào đâu?

```text
Query workload
```

không phải cảm tính.

---

# 43. Mental Model của Buổi 31

Hãy ghi nhớ sơ đồ này:

```text
                    Query
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        WHERE        JOIN       ORDER BY
          │           │           │
          └───────────┼───────────┘
                      ▼
                    INDEX
                      │
                      ▼
                  Query Planner
                      │
              ┌───────┴───────┐
              ▼               ▼
            SEARCH          SCAN
```

Và một nguyên tắc:

```text
Index
  ↓
READ nhanh hơn
  +
WRITE tốn thêm chi phí
```

---

# Part V — Tiến độ

```text
31. Index Fundamentals          ✅ ← hôm nay
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

**Buổi 32** sẽ đi xuống một tầng thấp hơn:

```text
CREATE INDEX
      ↓
   B-Tree
      ↓
   Node / Page
      ↓
   Key
      ↓
   Row reference
      ↓
SQLite tìm dữ liệu như thế nào?
```

Đây là buổi giúp bạn chuyển từ **“biết dùng INDEX”** sang **“hiểu INDEX hoạt động bên trong SQLite”**.
