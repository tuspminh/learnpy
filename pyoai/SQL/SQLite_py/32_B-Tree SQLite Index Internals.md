# Buổi 32 — B-Tree & SQLite Index Internals

Buổi 31 chúng ta biết **Index là gì và khi nào nên tạo Index**.

Buổi 32 đi xuống một tầng thấp hơn:

> **SQLite thực sự tổ chức Index như thế nào để biến việc tìm kiếm từ “quét rất nhiều row” thành “đi qua một cấu trúc có thứ tự”?**

Đây là nền tảng để học rất tốt **Composite Index, Covering Index, Query Planner và EXPLAIN QUERY PLAN** ở các buổi sau.

---

# 1. B-Tree là gì?

SQLite sử dụng cấu trúc **B-tree** cho rất nhiều cấu trúc lưu trữ quan trọng, bao gồm table và index.

Hãy hình dung đơn giản:

```text
                    [50]
                  /      \
             < 50          > 50
             /                \
       [10, 20, 30]       [60, 70, 80]
```

Khi tìm:

```text
70
```

SQLite không cần kiểm tra:

```text
1
2
3
4
5
...
70
```

Nó đi theo cây:

```text
50
 ↓
70
 ↓
FOUND
```

Đây là ý tưởng cốt lõi.

---

# 2. Tại sao không dùng Array?

Giả sử có:

```text
1,000,000 rows
```

Nếu dữ liệu được tổ chức đơn giản:

```text
[1, 2, 3, 4, 5, ... 1000000]
```

Tìm kiếm tuần tự có thể phải kiểm tra rất nhiều phần tử.

Trong trường hợp lý tưởng của binary search:

```text
O(log N)
```

thay vì:

```text
O(N)
```

Nhưng database không đơn giản là một array trong RAM.

Database phải làm việc với:

```text
Disk
Pages
Cache
I/O
Concurrent access
Large datasets
```

Vì vậy B-tree rất phù hợp với database.

---

# 3. Tại sao B-tree phù hợp với Disk?

Đây là điểm rất quan trọng.

Database không thường xuyên đọc từng byte riêng lẻ.

SQLite làm việc theo **page**.

Ví dụ tưởng tượng:

```text
database.db

┌────────────┐
│ Page 1     │
├────────────┤
│ Page 2     │
├────────────┤
│ Page 3     │
├────────────┤
│ Page 4     │
├────────────┤
│ ...        │
└────────────┘
```

Một B-tree tổ chức dữ liệu thành các page.

Mental model:

```text
B-tree
   ↓
Pages
   ↓
Nodes
   ↓
Keys
   ↓
Data / references
```

---

# 4. SQLite Page

SQLite database được chia thành các **database pages**.

Ví dụ:

```text
Page size = 4096 bytes
```

thì database có thể được hình dung:

```text
Page 1     4096 bytes
Page 2     4096 bytes
Page 3     4096 bytes
Page 4     4096 bytes
...
```

Page size thực tế phụ thuộc cấu hình/database; không nên coi 4096 là giá trị cố định.

Kiểm tra:

```sql
PRAGMA page_size;
```

Ví dụ Python:

```python
page_size = conn.execute("PRAGMA page_size").fetchone()[0]

print(page_size)
```

---

# 5. B-tree Node

Một cách đơn giản để hình dung:

```text
                 Root
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
    Interior              Interior
      Page                   Page
        │                     │
      ┌─┴─┐                 ┌─┴─┐
      ▼   ▼                 ▼   ▼
    Leaf Leaf             Leaf Leaf
```

SQLite thực tế có nhiều chi tiết thấp tầng hơn, nhưng mental model này đủ tốt để hiểu query/index.

---

# 6. Root Page

Mỗi B-tree có điểm bắt đầu.

```text
Root
 │
 ├── child
 ├── child
 └── child
```

SQLite bắt đầu traversal từ root rồi đi xuống.

Ví dụ tìm:

```text
novel_id = 5000
```

có thể hình dung:

```text
Root
 ↓
Interior Page
 ↓
Interior Page
 ↓
Leaf Page
 ↓
key = 5000
```

---

# 7. Interior Page và Leaf Page

Có thể đơn giản hóa:

### Interior page

Giúp SQLite **đi hướng nào**.

```text
[100] [500] [900]

<100
100–499
500–899
>=900
```

### Leaf page

Chứa các key cuối cùng và thông tin cần thiết để truy cập dữ liệu.

```text
[101]
[102]
[103]
[104]
...
```

Mental model:

```text
Interior
   ↓
"Đi hướng nào?"

Leaf
   ↓
"Đây là key cần tìm."
```

---

# 8. Index B-tree khác Table B-tree như thế nào?

Đây là phần cực kỳ quan trọng.

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

Table lưu dữ liệu.

Một index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

sẽ tổ chức dữ liệu dựa trên:

```text
novel_id
```

Mental model:

```text
TABLE B-TREE

id
│
├── row 1
├── row 2
├── row 3
└── ...


INDEX B-TREE

novel_id
│
├── 1 → row references
├── 1 → row references
├── 2 → row references
├── 5 → row references
└── ...
```

Index không đơn giản là bản sao của toàn bộ table.

---

# 9. Index có Key

Ví dụ dữ liệu:

```text
id    novel_id    title
1     10          Chapter 1
2     10          Chapter 2
3     20          Chapter 1
4     30          Chapter 1
5     10          Chapter 3
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

có thể hình dung:

```text
Index

novel_id
   │
   ├── 10 → row 1
   ├── 10 → row 2
   ├── 10 → row 5
   ├── 20 → row 3
   └── 30 → row 4
```

Điều này rất hữu ích cho:

```sql
WHERE novel_id = 10
```

SQLite có thể tìm vùng key:

```text
10
10
10
```

thay vì quét toàn bộ table.

---

# 10. Tại sao Index có thể tìm nhanh?

Giả sử có:

```text
1,000,000 keys
```

Một cây cân bằng tốt có thể có chiều cao tương đối nhỏ.

Ví dụ tưởng tượng:

```text
                  Root
             /      |      \
            /       |       \
           A        B        C
         / | \    / | \    / | \
        ...      ...       ...
```

Mỗi lần đi xuống:

```text
Root
 ↓
Page
 ↓
Page
 ↓
Leaf
```

Bạn loại bỏ một lượng lớn không gian tìm kiếm.

Đó là lý do query có thể chuyển từ tư duy:

```text
SCAN 1,000,000 rows
```

sang:

```text
SEARCH
  ↓
index
  ↓
few relevant entries
```

---

# 11. Nhưng B-tree không phải Binary Tree

Đừng nhầm:

```text
Binary Tree
```

với:

```text
B-tree
```

Binary tree thường có:

```text
          50
        /    \
      20      80
```

Mỗi node tối đa 2 nhánh.

B-tree có thể có **nhiều nhánh**:

```text
              [30 | 60]
             /    |     \
            /     |      \
        <30     30-60     >60
```

Điều này rất phù hợp với page-based storage.

---

# 12. B-tree và chiều cao

Giả sử cây có:

```text
1,000,000 entries
```

Không cần:

```text
1,000,000 levels
```

Mà có thể:

```text
Root
 ↓
Level 1
 ↓
Level 2
 ↓
Leaf
```

Chiều cao tương đối thấp.

Đây là một trong những lý do B-tree rất hiệu quả cho database.

---

# 13. B-tree phải được giữ cân bằng

Một cây tìm kiếm nếu bị lệch:

```text
1
 \
  2
   \
    3
     \
      4
       \
        5
```

sẽ mất lợi thế.

B-tree được thiết kế để giữ cấu trúc cân bằng.

Mental model:

```text
INSERT
   ↓
B-tree reorganize
   ↓
maintain balanced structure
```

SQLite xử lý những chi tiết này cho chúng ta.

Bạn chỉ cần:

```sql
CREATE INDEX ...
```

---

# 14. Khi INSERT một Chapter

Ví dụ:

```sql
INSERT INTO chapters (
    novel_id,
    chapter_number,
    title
)
VALUES (
    10,
    100,
    'Chapter 100'
);
```

SQLite phải cập nhật:

```text
TABLE
  +
INDEX
```

Nếu có:

```sql
CREATE INDEX idx_chapters_novel
ON chapters(novel_id);
```

thì entry tương ứng cũng phải được đưa vào index.

Mental model:

```text
INSERT
   │
   ├── Table B-tree
   │
   └── Index B-tree
```

Đây chính là một phần của **write overhead**.

---

# 15. Khi DELETE

Ví dụ:

```sql
DELETE FROM chapters
WHERE id = 500;
```

SQLite phải:

```text
remove row
    ↓
update relevant indexes
```

Nếu table có 8 indexes:

```text
DELETE
 │
 ├── table
 ├── index 1
 ├── index 2
 ├── index 3
 ├── ...
 └── index 8
```

Do đó:

> Tạo quá nhiều index có thể làm write-heavy workload chậm hơn.

---

# 16. Khi UPDATE

Ví dụ:

```sql
UPDATE chapters
SET novel_id = 20
WHERE id = 500;
```

Nếu `novel_id` có index:

```text
old index entry
      ↓
remove/update
      ↓
new index entry
```

Vì vậy index không chỉ ảnh hưởng SELECT.

Nó ảnh hưởng:

```text
INSERT
UPDATE
DELETE
```

---

# 17. Index và `ORDER BY`

Đây là điểm sẽ cực kỳ quan trọng ở các buổi sau.

Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Dữ liệu index có thứ tự theo:

```text
novel_id
    ↓
chapter_number
```

Ví dụ:

```text
novel 1
 ├── chapter 1
 ├── chapter 2
 ├── chapter 3

novel 2
 ├── chapter 1
 ├── chapter 2
 └── chapter 3
```

Vì vậy query:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

có thể tận dụng thứ tự của index.

Đây là lý do:

```text
Index
```

không chỉ giúp:

```text
WHERE
```

mà đôi khi còn giúp:

```text
ORDER BY
```

---

# 18. Index có thứ tự

Đây là mental model rất quan trọng:

```text
Index
↓
sorted structure
```

Ví dụ:

```text
novel_id = 1
    chapter 1
    chapter 2
    chapter 3
    chapter 4

novel_id = 2
    chapter 1
    chapter 2
    chapter 3
```

Do đó index:

```text
(novel_id, chapter_number)
```

không giống:

```text
(chapter_number, novel_id)
```

Thứ tự column cực kỳ quan trọng.

Buổi 33 sẽ đào sâu vấn đề này.

---

# 19. Table Scan vs Index Search

Đây là hai mental model cần thuộc.

### Không có index phù hợp

```text
TABLE
 │
 ├── row 1
 ├── row 2
 ├── row 3
 ├── row 4
 ├── ...
 └── row 1,000,000
```

SQLite có thể phải scan nhiều rows.

### Có index phù hợp

```text
INDEX
 │
 ├── navigate
 ├── navigate
 └── target
       ↓
      TABLE
       ↓
      row
```

---

# 20. Rowid và Index

SQLite có một khái niệm rất quan trọng:

```text
rowid
```

Với bảng thông thường, nếu không phải `WITHOUT ROWID`, SQLite sử dụng rowid làm định danh vật lý/logical key quan trọng của table B-tree.

Đặc biệt:

```sql
id INTEGER PRIMARY KEY
```

có quan hệ đặc biệt với rowid.

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT
);
```

`id` có thể được SQLite sử dụng như key chính của table B-tree.

Đây là lý do:

```sql
SELECT *
FROM novels
WHERE id = ?;
```

thường rất hiệu quả mà bạn không cần tạo:

```sql
CREATE INDEX idx_novels_id
ON novels(id);
```

---

# 21. Index lookup → Table lookup

Ví dụ:

```sql
SELECT
    id,
    title,
    content
FROM chapters
WHERE novel_id = 10;
```

Index chỉ có:

```text
novel_id → row reference
```

SQLite tìm được:

```text
novel_id = 10
```

sau đó truy cập table để lấy:

```text
id
title
content
```

Mental model:

```text
Index
 ↓
"Row cần lấy nằm ở đâu?"
 ↓
Table
 ↓
Full data
```

Đây là lý do index thường **không chứa toàn bộ dữ liệu của table**.

---

# 22. Tại sao `content` là vấn đề?

Novel crawler có:

```text
chapters.content
```

có thể rất lớn:

```text
5 KB
20 KB
50 KB
100 KB
```

Nếu tạo:

```sql
CREATE INDEX ...
ON chapters(content);
```

thì thường là một ý tưởng rất tệ cho workload đọc truyện thông thường.

Vì:

```text
content rất lớn
       ↓
index rất lớn
       ↓
write overhead
       ↓
disk usage
```

Thông thường chúng ta index các column phục vụ lookup/filter/sort, không phải cứ column nào cũng index.

---

# 23. Ví dụ Novel Reader

Giả sử:

```text
novels
chapters
tags
novel_tags
```

Các index hợp lý có thể xuất phát từ workload:

```text
chapters.novel_id
chapters.(novel_id, chapter_number)
novel_tags.novel_id
novel_tags.tag_id
```

Nhưng đừng tạo hàng loạt index chỉ dựa trên schema.

Hãy bắt đầu từ:

```text
Use Case
```

Ví dụ:

> "Mở Novel → hiển thị 50 chapter đầu."

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

Sau đó mới thiết kế:

```text
(novel_id, chapter_number)
```

---

# 24. Một ví dụ với nhiều chapter

Giả sử:

```text
Novel A = 10,000 chapters
Novel B = 20 chapters
Novel C = 5,000 chapters
```

Query:

```sql
WHERE novel_id = A
```

Index:

```text
novel_id
```

có thể giúp SQLite tìm vùng:

```text
Novel A
 ↓
10,000 index entries
```

thay vì:

```text
toàn bộ chapters của tất cả novels
```

Nếu query thêm:

```sql
ORDER BY chapter_number
```

thì composite index:

```text
(novel_id, chapter_number)
```

trở nên đặc biệt thú vị.

---

# 25. SQLite không chỉ có một B-tree

Mental model cấp cao:

```text
SQLite Database
      │
      ├── Table B-tree
      │
      ├── Index B-tree
      │
      ├── Table B-tree
      │
      └── Index B-tree
```

Ví dụ:

```text
novels
 ├── table B-tree
 ├── UNIQUE(url) structure
 └── other indexes

chapters
 ├── table B-tree
 ├── index(novel_id)
 └── index(novel_id, chapter_number)
```

Đây là lý do:

```text
Index nhiều
```

→ database file lớn hơn.

---

# 26. Kiểm tra Index từ Python

Ta có:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
conn.row_factory = sqlite3.Row

conn.execute("""
    CREATE INDEX IF NOT EXISTS
    idx_chapters_novel_id
    ON chapters(novel_id)
""")
```

Kiểm tra:

```python
rows = conn.execute("PRAGMA index_list(chapters)").fetchall()

for row in rows:
    print(dict(row))
```

Xem column:

```python
rows = conn.execute(
    """
    PRAGMA index_info(
        idx_chapters_novel_id
    )
    """
).fetchall()

for row in rows:
    print(dict(row))
```

---

# 27. EXPLAIN QUERY PLAN

Đây là cầu nối giữa:

```text
B-tree
```

và:

```text
Query Planner
```

Ví dụ:

```python
sql = """
    SELECT
        id,
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
"""

rows = conn.execute(
    "EXPLAIN QUERY PLAN " + sql,
    (10,),
).fetchall()

for row in rows:
    print(dict(row))
```

Có thể nhận được dạng:

```text
SEARCH chapters USING INDEX idx_chapters_novel_id
```

Điều đó nói rằng planner đã chọn index.

---

# 28. Nhưng đừng cố đọc EXPLAIN quá sớm

Hiện tại bạn chỉ cần nhớ:

```text
SCAN
```

và:

```text
SEARCH
```

Buổi 40 chúng ta sẽ học:

> **EXPLAIN QUERY PLAN Deep Dive**

Lúc đó chúng ta sẽ đọc query plan một cách có hệ thống.

---

# 29. B-tree và Range Query

Một ưu điểm cực kỳ quan trọng của cấu trúc có thứ tự là range query.

Ví dụ:

```sql
SELECT *
FROM chapters
WHERE chapter_number >= 100
  AND chapter_number < 200;
```

Index có thứ tự giúp database định vị vùng:

```text
100
 ↓
101
102
103
...
199
 ↓
stop
```

thay vì kiểm tra mọi giá trị.

Đây là nền tảng để hiểu:

```text
BETWEEN
>
>=
<
<=
ORDER BY
```

và composite index sau này.

---

# 30. Equality và Range

Hai loại query:

### Equality

```sql
WHERE novel_id = ?
```

### Range

```sql
WHERE chapter_number >= ?
```

B-tree hỗ trợ rất tự nhiên cho cả hai loại pattern này, nhưng với composite index thì thứ tự các column quyết định rất nhiều.

Ví dụ:

```text
(novel_id, chapter_number)
```

rất phù hợp với:

```sql
WHERE novel_id = ?
  AND chapter_number >= ?
```

Đây là bước chuẩn bị cho Buổi 33.

---

# 31. Một cách hình dung cực tốt

Hãy tưởng tượng index:

```text
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

là một danh bạ được sắp xếp:

```text
Novel 1
 ├─ Chapter 1
 ├─ Chapter 2
 ├─ Chapter 3
 └─ Chapter 4

Novel 2
 ├─ Chapter 1
 ├─ Chapter 2
 └─ Chapter 3

Novel 3
 ├─ Chapter 1
 └─ Chapter 2
```

Query:

```sql
WHERE novel_id = 2
```

→ đi tới vùng Novel 2.

Query:

```sql
WHERE novel_id = 2
  AND chapter_number = 3
```

→ đi tới Novel 2 → Chapter 3.

Query:

```sql
WHERE chapter_number = 3
```

→ câu chuyện hoàn toàn khác.

Đó chính là **leftmost-prefix**, chủ đề chính của Buổi 33.

---

# 32. Bài tập thực hành

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
    title TEXT NOT NULL
);
""")
```

Insert dữ liệu:

```python
conn.executemany(
    """
    INSERT INTO chapters (
        novel_id,
        chapter_number,
        title
    )
    VALUES (?, ?, ?)
    """,
    [
        (1, 1, "Chapter 1"),
        (1, 2, "Chapter 2"),
        (1, 3, "Chapter 3"),
        (2, 1, "Chapter 1"),
        (2, 2, "Chapter 2"),
        (3, 1, "Chapter 1"),
    ],
)
```

---

## Bài 1 — Xem plan trước Index

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 1;
```

Quan sát.

---

## Bài 2 — Tạo Index

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Sau đó chạy lại:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 1;
```

So sánh.

---

## Bài 3 — Composite Index

Tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Thử:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 1
ORDER BY chapter_number;
```

Sau đó thử:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE chapter_number = 2;
```

Hãy quan sát sự khác biệt.

---

# 33. Bài tập tư duy quan trọng

Giả sử có:

```sql
CREATE INDEX idx_test
ON chapters(novel_id, chapter_number);
```

Hãy phân loại các query:

### A

```sql
WHERE novel_id = ?
```

### B

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

### C

```sql
WHERE chapter_number = ?
```

### D

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

### E

```sql
WHERE novel_id = ?
  AND chapter_number >= ?
```

Hãy tự dự đoán query nào phù hợp với index trước khi chạy `EXPLAIN`.

Đây là bài tập rất tốt để chuẩn bị cho **Buổi 33**.

---

# 34. Tổng kết Buổi 32

Bạn cần hình thành mental model:

```text
                    SQLite
                       │
                       ▼
                     B-tree
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Table B-tree        Index B-tree
             │                   │
             │                   ▼
             │                  Keys
             │                   │
             │                   ▼
             │             Row references
             │                   │
             └──────────┬────────┘
                        ▼
                     Data
```

Và:

```text
Index
  ↓
sorted structure
  ↓
B-tree
  ↓
pages
  ↓
navigate
  ↓
find key
  ↓
locate row
```

Quan trọng nhất:

> **Index không phải “bản sao dữ liệu để tìm nhanh”. Nó là một cấu trúc dữ liệu có thứ tự, được SQLite duy trì song song với table để hỗ trợ các query pattern phù hợp.**

---

## Roadmap tiếp theo

```text
31. Index Fundamentals              ✅
32. B-Tree & Index Internals        ✅
33. Composite Index Deep Dive       ← tiếp theo
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

**Buổi 33 sẽ là một buổi rất quan trọng:** `Composite Index (A, B, C)`, **leftmost prefix**, thứ tự column, equality → range, và cách thiết kế index cho các query thực tế của `novels / chapters`.
