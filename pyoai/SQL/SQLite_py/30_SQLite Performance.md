# Buổi 30 — SQLite Performance & Query Optimization

Đây là **buổi cuối của Part IV — SQLite Deep Dive**.

Từ Buổi 24 đến 29, chúng ta đã học cách SQLite **lưu dữ liệu, bảo vệ dữ liệu, transaction và concurrency**.

Hôm nay chuyển sang câu hỏi:

> **SQLite chạy chậm vì đâu, và làm sao biết chính xác query nào đang chậm?**

Ta sẽ tập trung vào tư duy **đo → phân tích → tối ưu**, không tối ưu theo cảm tính.

---

# 1. Performance không chỉ là "query nhanh"

Một hệ thống SQLite có thể chậm ở nhiều tầng:

```text id="f4c9v8"
Application
     │
     ▼
Python
     │
     ▼
sqlite3
     │
     ▼
SQL Query
     │
     ├── Scan quá nhiều rows
     ├── Index không phù hợp
     ├── JOIN lớn
     ├── N+1 query
     ├── Transaction quá nhỏ
     ├── Transaction quá lớn
     └── Lock contention
     │
     ▼
SQLite
     │
     ▼
Disk
```

Vì vậy:

```text id="v9p2qd"
SQLite performance
≠
chỉ thêm INDEX
```

---

# 2. Quy tắc số 1: Đừng đoán

Một sai lầm phổ biến:

```text
"Query này chắc chậm."
```

rồi lập tức:

```sql
CREATE INDEX ...
```

Không nên.

Quy trình tốt:

```text id="h6m1cn"
Measure
   ↓
Inspect
   ↓
Understand
   ↓
Optimize
   ↓
Measure again
```

SQLite cung cấp công cụ cực kỳ quan trọng:

```sql
EXPLAIN QUERY PLAN
```

---

# 3. EXPLAIN QUERY PLAN

Ví dụ:

```sql id="a1v7yz"
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 10;
```

SQLite có thể cho biết query đang sử dụng:

```text
SCAN chapters
```

hoặc:

```text
SEARCH chapters USING INDEX ...
```

Đây là một trong những thứ bạn cần học cách đọc.

---

# 4. SCAN là gì?

Nếu SQLite thực hiện:

```text id="k8bq5m"
SCAN chapters
```

thì có thể hiểu đơn giản là:

> SQLite phải duyệt nhiều hoặc toàn bộ bảng để tìm dữ liệu.

Ví dụ:

```sql id="7d8h2x"
SELECT *
FROM chapters
WHERE novel_id = 100;
```

Nếu bảng có:

```text id="t9x8js"
1,000,000 chapters
```

mà không có index phù hợp, SQLite có thể phải kiểm tra rất nhiều rows.

---

# 5. SEARCH là gì?

Nếu có index:

```sql id="1o9r0p"
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

thì:

```sql id="s6qk9c"
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 100;
```

có thể cho:

```text
SEARCH chapters USING INDEX idx_chapters_novel_id
```

Ý tưởng:

```text id="4gy1wf"
Không index:

1 → 2 → 3 → 4 → ... → 1,000,000

Có index:

index
  ↓
novel_id = 100
  ↓
các rows phù hợp
```

---

# 6. INDEX là gì?

Hãy tưởng tượng bảng:

```text id="9l9z6k"
chapters
--------------------------------
id
novel_id
chapter_number
title
content
```

Query:

```sql id="0o9g8m"
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Nếu không có index:

```text id="kmf9k7"
SQLite
  ↓
scan chapters
  ↓
kiểm tra từng row
```

Nếu có:

```sql id="u3w6br"
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

SQLite có cấu trúc phụ trợ để tìm `novel_id` nhanh hơn.

---

# 7. Nhưng INDEX không miễn phí

Index giúp:

```text id="0ck8vf"
SELECT
UPDATE
DELETE
```

nhanh hơn trong nhiều trường hợp.

Nhưng index cũng phải:

```text id="1a9j9c"
INSERT
UPDATE
DELETE
```

được cập nhật.

Nghĩa là:

```text id="d2gjh7"
INDEX
  ├── tăng tốc READ
  └── tăng chi phí WRITE
```

Ngoài ra index chiếm disk space.

Vì vậy:

> Không tạo index cho mọi column.

---

# 8. Index đầu tiên của project

Với schema:

```sql id="n4q6w2"
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

```sql id="5f5t1a"
SELECT *
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

Index hợp lý:

```sql id="l8s6y3"
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Đây là một **composite index**.

---

# 9. Composite Index

Index:

```sql id="q3c7mb"
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

có hai phần:

```text id="y9z0qv"
(novel_id, chapter_number)
       ↑
    column 1

                    ↑
                column 2
```

Thứ tự rất quan trọng.

---

# 10. Quy tắc Leftmost Prefix

Index:

```text id="qpj8oa"
(novel_id, chapter_number)
```

rất hữu ích cho:

```sql id="sj5x20"
WHERE novel_id = ?
```

và:

```sql id="w9q3hx"
WHERE novel_id = ?
ORDER BY chapter_number
```

Nhưng không nhất thiết hữu ích tương tự cho:

```sql id="p5uj6h"
WHERE chapter_number = ?
```

Bởi index được tổ chức theo:

```text id="tdk7p2"
novel_id
   ↓
chapter_number
```

Không phải:

```text id="i3tq4a"
chapter_number
   ↓
novel_id
```

---

# 11. Đây là lý do thứ tự column trong composite index quan trọng

Hai index:

```sql id="7p6a6z"
(novel_id, chapter_number)
```

và:

```sql id="8r3p8y"
(chapter_number, novel_id)
```

**không giống nhau**.

Khi thiết kế index, hãy nhìn vào query thực tế.

---

# 12. Query thường gặp của Novel Reader

Ta có:

```sql id="yb3k5p"
SELECT
    id,
    chapter_number,
    title,
    content
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT ? OFFSET ?;
```

Index:

```sql id="f1j9ks"
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

rất phù hợp với pattern:

```text id="qg7w1z"
WHERE novel_id
       +
ORDER BY chapter_number
```

Đây là cách tư duy quan trọng:

> **Thiết kế index dựa trên query workload, không dựa trên cảm giác.**

---

# 13. Primary Key đã có index chưa?

Với:

```sql id="4d0r6q"
id INTEGER PRIMARY KEY
```

SQLite có cơ chế đặc biệt cho rowid.

Do đó thường không cần tự tạo:

```sql
CREATE INDEX idx_novels_id
ON novels(id);
```

Đây thường là index dư thừa.

---

# 14. UNIQUE cũng liên quan đến index

Ví dụ:

```sql id="20v4p5"
url TEXT NOT NULL UNIQUE
```

SQLite cần cơ chế để đảm bảo uniqueness.

Vì vậy không nên tùy tiện tạo thêm:

```sql id="8p1s7v"
CREATE INDEX idx_novels_url
ON novels(url);
```

nếu schema đã có UNIQUE phù hợp.

---

# 15. Composite UNIQUE cũng rất quan trọng

Ta có:

```sql id="ax8t9g"
UNIQUE(novel_id, chapter_number)
```

SQLite cần hỗ trợ uniqueness của cặp:

```text id="l9o7up"
(novel_id, chapter_number)
```

Do đó query:

```sql id="9xw6e2"
WHERE novel_id = ?
  AND chapter_number = ?
```

cũng có thể hưởng lợi từ cấu trúc đó.

Đây là một ví dụ về việc:

> Constraint và performance đôi khi giao nhau.

---

# 16. N+1 Query

Đây là một trong những lỗi performance quan trọng nhất.

Ví dụ:

```python id="j0f9qn"
novels = get_all_novels()

for novel in novels:
    chapters = get_chapters(novel.id)
```

Nếu có:

```text id="m4c1ps"
100 novels
```

ta có:

```text id="7x2qz8"
1 query
+
100 queries
=
101 queries
```

Đây là:

> **N+1 Query Problem**

---

# 17. Tại sao N+1 nguy hiểm?

Không chỉ vì SQLite query chậm.

Mà vì:

```text id="k9s4hc"
Python
 ↓
sqlite3
 ↓
SQLite
 ↓
Python
 ↓
sqlite3
 ↓
SQLite
```

lặp đi lặp lại.

Nếu:

```text id="m8j1xn"
1 query = 0.5 ms
```

thì:

```text
1000 queries
```

vẫn có overhead đáng kể.

---

# 18. Cách cải thiện N+1

Thay vì:

```python id="1u6d8c"
for novel in novels:
    get_chapters(novel.id)
```

có thể dùng JOIN:

```sql id="x0q4ks"
SELECT
    n.id AS novel_id,
    n.title AS novel_title,
    c.id AS chapter_id,
    c.chapter_number,
    c.title AS chapter_title
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
ORDER BY n.id, c.chapter_number;
```

Hoặc aggregate:

```sql id="3v7k2h"
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
GROUP BY n.id, n.title;
```

---

# 19. Nhưng đừng biến mọi thứ thành một JOIN khổng lồ

Sai lầm ngược lại:

```text id="n2s6wl"
N+1
  ↓
"JOIN tất cả!"
```

Một query khổng lồ có thể:

```text
khó đọc
khó test
khó maintain
nhiều row multiplication
```

Hãy chọn query theo **use case**.

Ví dụ Dashboard cần:

```text id="4v7h6r"
Novel
Chapter count
Tag count
Status
```

thì một query aggregate phù hợp.

Reading page chỉ cần:

```text id="u0w8q4"
Chapter content
```

thì không cần JOIN 5 bảng.

---

# 20. SELECT * có thể gây lãng phí

Ví dụ:

```sql id="p6q0v1"
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Nếu `content` rất lớn:

```text id="z8t4qk"
content = hàng chục KB
```

nhưng UI chỉ cần:

```text id="d3q1m5"
id
chapter_number
title
```

thì:

```sql id="s1w9hp"
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?;
```

tốt hơn.

Đặc biệt với crawler:

```text content có thể rất lớn
```

---

# 21. Covering Index

Đây là một khái niệm nâng cao.

Ví dụ query:

```sql id="8y6q9d"
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

Ta có:

```sql id="2j7b4k"
CREATE INDEX idx_chapters_list
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Index chứa luôn các column cần để trả kết quả.

Trong một số trường hợp SQLite có thể thực hiện **covering index scan**, giảm việc phải truy cập table.

`EXPLAIN QUERY PLAN` giúp xác định điều này.

Không nên mặc định rằng "covering index luôn tốt"; index rộng hơn cũng làm tăng chi phí ghi và kích thước database.

---

# 22. EXPLAIN QUERY PLAN thực hành

Trước index:

```sql id="6d5v0m"
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM chapters
WHERE novel_id = 10;
```

Có thể:

```text id="v3y1je"
SCAN chapters
```

Sau:

```sql id="gr2j6k"
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

chạy lại:

```sql id="jj3f4p"
EXPLAIN QUERY PLAN
SELECT
    id,
    title
FROM chapters
WHERE novel_id = 10;
```

Có thể thấy:

```text id="b6j7px"
SEARCH chapters USING INDEX idx_chapters_novel_id
```

Đây là cách học performance đúng:

```text
before
   ↓
change
   ↓
after
```

---

# 23. Đừng chỉ nhìn vào thời gian

Ví dụ:

```text id="u4p5qt"
Query A: 10 ms
Query B: 12 ms
```

Không nhất thiết A tốt hơn về lâu dài.

Hãy xem:

```text
EXPLAIN QUERY PLAN
```

và workload.

Một query:

```text id="0k8w9s"
10 ms × 10 lần/phút
```

khác hoàn toàn:

```text id="2s8f4c"
10 ms × 100,000 lần/phút
```

---

# 24. Pagination

Ta đã học:

```sql id="4l6c7v"
SELECT ...
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT ?
OFFSET ?;
```

Đây là pagination truyền thống.

Ví dụ:

```text id="e7j8g2"
page = 1
LIMIT 50 OFFSET 0

page = 2
LIMIT 50 OFFSET 50

page = 1000
LIMIT 50 OFFSET 49950
```

OFFSET lớn có thể trở nên kém hiệu quả vì database phải đi qua nhiều rows trước khi trả phần cần thiết.

---

# 25. Keyset Pagination

Với chapter, ta có:

```text id="5o3h9w"
chapter_number
```

Thay vì:

```sql id="5g1m3n"
LIMIT 50 OFFSET 50000
```

có thể:

```sql id="4k0j9v"
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
  AND chapter_number > ?
ORDER BY chapter_number
LIMIT 50;
```

Ví dụ:

```text id="p3x8sd"
last_chapter = 50000
```

query:

```sql
WHERE novel_id = 1
  AND chapter_number > 50000
```

Đây gọi là:

> **Keyset / Cursor Pagination**

Rất phù hợp với dữ liệu tuần tự như chapter.

---

# 26. Novel Reader rất hợp với Keyset Pagination

Ví dụ:

```text id="t1j7x0"
Chapter 1
Chapter 2
...
Chapter 100000
```

Người đọc đang ở:

```text id="f4j6cw"
chapter 5000
```

Muốn lấy 20 chapter tiếp:

```sql id="0j3w9z"
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
  AND chapter_number > ?
ORDER BY chapter_number
LIMIT 20;
```

Index:

```sql id="a5h7k2"
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Đây là một cặp thiết kế rất đẹp:

```text id="r8z2cq"
Query pattern
     +
Composite index
     +
Keyset pagination
```

---

# 27. COUNT có thể tốn tài nguyên

Ví dụ:

```sql id="4k9x2m"
SELECT COUNT(*)
FROM chapters
WHERE novel_id = ?;
```

Nếu dashboard gọi hàng trăm lần:

```text id="e1z4qh"
Dashboard refresh
      ↓
COUNT chapters
      ↓
COUNT chapters
      ↓
COUNT chapters
```

thì cần suy nghĩ về workload.

Không phải `COUNT(*)` luôn chậm; SQLite có thể xử lý nhiều trường hợp rất tốt. Nhưng trên bảng lớn và với điều kiện lọc, nó vẫn có thể cần duyệt nhiều dữ liệu.

---

# 28. Đừng vội lưu `chapter_count`

Có người thấy COUNT nhiều nên thêm:

```sql id="k9x3r4"
novels.chapter_count
```

Sau đó phải đồng bộ:

```text id="m8f4v2"
INSERT chapter
    ↓
chapter_count += 1

DELETE chapter
    ↓
chapter_count -= 1
```

Bây giờ có nguy cơ:

```text id="q5t7az"
chapters = 100
chapter_count = 99
```

Đây là **denormalization**.

Có thể làm khi cần performance và có chiến lược đồng bộ rõ ràng, nhưng không nên làm quá sớm.

---

# 29. INSERT performance

Crawler thường có workload:

```text id="q3y8n1"
INSERT rất nhiều chapters
```

Không nên:

```python id="3p6s8k"
for chapter in chapters:
    conn.execute(...)
    conn.commit()
```

Nếu mỗi row một transaction:

```text id="1m9x2v"
INSERT
COMMIT

INSERT
COMMIT

INSERT
COMMIT
...
```

rất nhiều overhead.

---

# 30. Batch transaction

Tốt hơn:

```python id="k1v4s7"
with conn:
    for chapter in chapters:
        conn.execute(
            """
            INSERT INTO chapters(
                novel_id,
                chapter_number,
                title,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chapter.novel_id,
                chapter.number,
                chapter.title,
                chapter.content,
            ),
        )
```

Hoặc dùng:

```python id="8s4m2p"
conn.executemany(
    """
    INSERT INTO chapters(
        novel_id,
        chapter_number,
        title,
        content
    )
    VALUES (?, ?, ?, ?)
    """,
    rows,
)
conn.commit()
```

---

# 31. `executemany()` + transaction

Đây là pattern rất hữu ích:

```python id="r5c9x0"
rows = [
    (1, 1, "Chapter 1", "..."),
    (1, 2, "Chapter 2", "..."),
    (1, 3, "Chapter 3", "..."),
]

conn.executemany(
    """
    INSERT INTO chapters(
        novel_id,
        chapter_number,
        title,
        content
    )
    VALUES (?, ?, ?, ?)
    """,
    rows,
)

conn.commit()
```

So với:

```text id="4t7h9p"
commit từng row
```

thường hiệu quả hơn đáng kể.

---

# 32. Nhưng đừng tạo transaction khổng lồ

Như Buổi 29:

```text id="z0r5j7"
1,000,000 rows
+
ONE transaction
```

không nhất thiết tốt.

Có thể batch:

```text id="7c5m1p"
500
500
500
...
```

Con số tối ưu phải benchmark.

---

# 33. Index và INSERT

Một crawler có:

```text id="v4r8k2"
10 indexes
```

sẽ phải cập nhật nhiều index khi INSERT.

Ví dụ:

```text id="f2m9s5"
INSERT chapter
      │
      ├── table
      ├── index 1
      ├── index 2
      ├── index 3
      └── index 4
```

Vì vậy:

> Chỉ tạo những index phục vụ workload thực tế.

---

# 34. Index cho foreign key

Ta có:

```sql id="j8v3q1"
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Điều này đảm bảo integrity.

Nhưng không có nghĩa SQLite tự động tạo index:

```sql id="5f7r2n"
chapters(novel_id)
```

Do đó thường nên cân nhắc:

```sql id="3m6k8x"
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Đặc biệt khi query:

```sql
WHERE novel_id = ?
```

rất thường xuyên.

---

# 35. JOIN cũng cần index

Ví dụ:

```sql id="8n2v5p"
SELECT ...
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

Column:

```text id="x7q3k1"
chapters.novel_id
```

là candidate rất tự nhiên cho index.

```sql id="3h9m6a"
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Điều này đặc biệt quan trọng khi:

```text id="j2p6v8"
novels = 10,000
chapters = 10,000,000
```

---

# 36. Nhưng hãy kiểm tra Query Plan

Không nên chỉ nói:

> "JOIN thì phải tạo index."

Hãy kiểm tra:

```sql id="k3m7s1"
EXPLAIN QUERY PLAN
SELECT
    n.id,
    n.title,
    c.chapter_number
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?;
```

SQLite query planner sẽ quyết định cách thực thi dựa trên schema, statistics và query.

---

# 37. ANALYZE

SQLite có:

```sql id="j4q8x2"
ANALYZE;
```

Mục đích là thu thập statistics về database để query planner có thêm thông tin khi lựa chọn execution plan.

Sau khi database lớn hoặc workload thay đổi đáng kể, statistics có thể hữu ích.

Không phải query nào cũng cần chạy `ANALYZE` thủ công liên tục.

---

# 38. `PRAGMA optimize`

SQLite có:

```sql id="m8r1c4"
PRAGMA optimize;
```

Đây là một cơ chế SQLite cung cấp để hỗ trợ tối ưu hóa/query planner maintenance trong các phiên bản hiện đại.

Trong application thực tế, có thể cân nhắc gọi:

```python id="w2n5k7"
conn.execute("PRAGMA optimize")
```

ở những thời điểm thích hợp.

Không cần gọi sau từng query.

---

# 39. Performance của Python cũng quan trọng

Đôi khi vấn đề không phải SQLite.

Ví dụ:

```python id="z4m8p1"
rows = cursor.fetchall()

for row in rows:
    ...
```

Nếu:

```text id="d7q3v9"
1,000,000 rows
```

thì Python phải giữ và xử lý lượng dữ liệu khổng lồ.

Nếu chỉ cần xử lý từng row:

```python id="q5k1x6"
for row in cursor:
    process(row)
```

có thể phù hợp hơn.

Hoặc tốt hơn:

```sql id="a8v2m5"
WHERE ...
LIMIT ...
```

để giảm dữ liệu ngay tại DB.

---

# 40. Đừng đưa quá nhiều dữ liệu từ DB lên Python

Không tốt:

```sql id="x1c8v4"
SELECT *
FROM chapters;
```

sau đó:

```python
rows = cursor.fetchall()

filtered = [row for row in rows if row["novel_id"] == novel_id]
```

Nếu database có hàng triệu rows, bạn đang làm filtering sai tầng.

Tốt hơn:

```sql id="s6q4n8"
SELECT ...
FROM chapters
WHERE novel_id = ?;
```

> **Để database làm việc mà database giỏi.**

---

# 41. Một query nên được tối ưu từ WHERE

Hãy nhìn:

```sql id="p3w7k9"
SELECT ...
FROM chapters
WHERE novel_id = ?
  AND chapter_number >= ?
ORDER BY chapter_number
LIMIT 50;
```

Ta thấy:

```text id="b2f6m0"
WHERE
 ├── novel_id
 └── chapter_number

ORDER BY
 └── chapter_number
```

Candidate:

```sql id="x9k4v2"
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Đây là cách suy nghĩ về composite index.

---

# 42. Một lỗi phổ biến: function trên indexed column

Ví dụ:

```sql id="m7c3x1"
WHERE LOWER(title) = ?
```

Nếu index đơn giản:

```sql
CREATE INDEX idx_novels_title
ON novels(title);
```

thì query trên không nhất thiết tận dụng index đó theo cách bạn mong muốn, vì đang áp dụng function lên column.

Đây là lý do phải hiểu query planner thay vì chỉ tạo index.

---

# 43. LIKE và Index

Query:

```sql id="v1q8r5"
WHERE title LIKE 'Tiên%'
```

có khả năng được tối ưu bằng index trong những điều kiện phù hợp.

Nhưng:

```sql id="j6s2n9"
WHERE title LIKE '%Tiên%'
```

thường khó tận dụng B-tree index thông thường để tìm prefix, vì wildcard nằm đầu chuỗi.

Nếu app cần full-text search:

```text id="c4v7x1"
SQLite FTS5
```

có thể là hướng phù hợp hơn.

FTS5 sẽ là chủ đề nâng cao về sau nếu cần cho Novel Reader.

---

# 44. Performance checklist cho Novel DB

Khi query:

```sql id="t8k3m5"
SELECT ...
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number;
```

hãy hỏi:

### 1. Query có đúng không?

```text
logic
```

### 2. Có trả quá nhiều dữ liệu không?

```text
SELECT *
```

### 3. Có index phù hợp không?

```text
(novel_id, chapter_number)
```

### 4. Query plan là gì?

```sql
EXPLAIN QUERY PLAN
```

### 5. Có N+1 không?

```text
Python loop → query → query → query
```

### 6. Có pagination không?

```text
LIMIT
```

### 7. Có transaction hợp lý không?

### 8. Có quá nhiều index không?

---

# 45. Schema được tối ưu bước đầu

Một phiên bản khá tốt cho project:

```sql id="x4c8m1"
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    url TEXT NOT NULL,
    status TEXT NOT NULL
        DEFAULT 'ongoing'
        CHECK (
            status IN ('ongoing', 'completed')
        ),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    UNIQUE(source, url)
);

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

    UNIQUE(novel_id, chapter_number)
);

CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Điểm đáng chú ý:

```text id="s8w2p6"
novel_id
    ↓
FK integrity

(novel_id, chapter_number)
    ↓
UNIQUE
    +
query performance
```

---

# 46. Performance Architecture

Sau 30 buổi, architecture của chúng ta đã tiến khá xa:

```text id="m5x9c2"
Application
     │
     ▼
Unit of Work
     │
     ├── transaction
     │
     ▼
Repository
     │
     ├── SQL
     ├── query
     └── mapping
     │
     ▼
Connection Manager
     │
     ├── WAL
     ├── FK
     ├── timeout
     └── synchronous
     │
     ▼
SQLite
     │
     ├── Tables
     ├── Constraints
     ├── Indexes
     └── Query Planner
```

Đây chính là nền tảng tốt cho phần Repository/UoW mà bạn đang học song song.

---

# 47. Công thức Performance cần nhớ

Hãy ghi lại công thức này:

```text id="9v3k8a"
SQLite Performance
=
Correct Query
+
Correct Index
+
Small Result Set
+
Avoid N+1
+
Short/Batch Transactions
+
Query Plan
+
Measure
```

Không phải:

```text id="k6m1z4"
Performance = thêm thật nhiều INDEX
```

---

# 48. 10 quy tắc vàng

### 1.

> **Measure before optimize.**

### 2.

Dùng:

```sql
EXPLAIN QUERY PLAN
```

để xem SQLite thực sự làm gì.

### 3.

Index dựa trên **query workload**.

### 4.

Composite index chú ý **thứ tự column**.

### 5.

Tránh N+1 Query.

### 6.

Không dùng `SELECT *` nếu không cần.

### 7.

Pagination cho dữ liệu lớn.

### 8.

Crawler bulk insert → transaction + `executemany()`.

### 9.

Không tạo quá nhiều index.

### 10.

Sau khi tối ưu phải **đo lại**.

---

# 49. Bài tập thực hành tổng hợp

## Bài 1 — EXPLAIN

Chạy:

```sql
EXPLAIN QUERY PLAN
SELECT *
FROM chapters
WHERE novel_id = 10;
```

Sau đó tạo:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Chạy lại.

So sánh plan.

---

## Bài 2 — Composite Index

Tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Kiểm tra:

```sql
EXPLAIN QUERY PLAN
SELECT
    chapter_number,
    title
FROM chapters
WHERE novel_id = 10
ORDER BY chapter_number;
```

---

## Bài 3 — N+1

Viết Python cố tình tạo:

```text
1 query lấy novels
+
N query lấy chapters
```

Sau đó refactor thành một query JOIN hoặc query aggregate.

---

## Bài 4 — Pagination

Viết:

```python
def get_chapters(
    novel_id: int,
    page: int,
    page_size: int,
): ...
```

sử dụng:

```sql
LIMIT ?
OFFSET ?
```

Sau đó viết phiên bản:

```python
def get_chapters_after(
    novel_id: int,
    last_chapter: int,
    limit: int,
): ...
```

sử dụng keyset pagination.

---

## Bài 5 — Bulk insert

Tạo:

```text
10,000 chapters
```

so sánh:

```text
A. commit từng row
B. executemany + transaction
```

Đo thời gian.

Bạn sẽ thấy sự khác biệt rất rõ.

---

# 50. Mini Project — Performance Audit

Lấy database Novel của chúng ta.

Viết 5 query:

```text id="d1q7n3"
1. Get novel
2. Get chapters
3. Get latest chapter
4. Count chapters
5. Search novels
```

Với mỗi query:

```text
Query
 ↓
EXPLAIN QUERY PLAN
 ↓
Index
 ↓
EXPLAIN QUERY PLAN
 ↓
Benchmark
```

Tạo bảng ghi chú:

| Query          | Trước | Index                        | Sau | N+1? |
| -------------- | ----: | ---------------------------- | --: | ---- |
| Get novel      |     ? | PK                           |   ? | No   |
| Get chapters   |     ? | `(novel_id, chapter_number)` |   ? | No   |
| Latest chapter |     ? | composite                    |   ? | No   |
| Count chapters |     ? | novel_id                     |   ? | No   |
| Search novel   |     ? | tùy pattern                  |   ? | No   |

Đây mới là cách học SQLite performance như một developer thực tế.

---

# 51. Hoàn thành Part IV 🎯

Bạn đã hoàn thành:

```text
PART IV — SQLite Deep Dive

24. Type Affinity              ✅
25. Constraints Deep Dive      ✅
26. PRAGMA                     ✅
27. Transaction Deep Dive      ✅
28. WAL                        ✅
29. Locking & Concurrency      ✅
30. SQLite Performance         ✅
```

Và từ đây bạn đã có một mental model khá hoàn chỉnh:

```text
                 SQLite
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Schema      Transaction  Query
        │           │           │
        ▼           ▼           ▼
 Constraints       WAL        Index
        │           │           │
        ▼           ▼           ▼
     Foreign       Lock       Query
      Key       Concurrency    Plan
```

---

# Tiếp theo — Part V: Index & Query Optimization

Phần IV vừa học performance ở mức nền tảng. **Part V sẽ đào sâu riêng về Index và Query Planner**, thay vì chỉ giới thiệu.

```text
PART V — Index & Query Optimization

31. Index Fundamentals
32. B-Tree & SQLite Index Internals
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

**Buổi 31** sẽ bắt đầu từ câu hỏi rất quan trọng:

> **SQLite thực sự lưu một INDEX như thế nào, và tại sao B-Tree giúp tìm dữ liệu nhanh hơn SCAN?**

Đó sẽ là cầu nối từ việc **“biết tạo index”** sang **“thực sự hiểu index”**.
