# Buổi 38 — Index + JOIN

Hôm nay chúng ta nối hai mảng kiến thức rất quan trọng:

```text
JOIN
+
INDEX
```

Mục tiêu là hiểu được:

* Vì sao `FOREIGN KEY` nên thường đi kèm index ở bảng con.
* SQLite thực hiện JOIN như thế nào ở mức khái niệm.
* Vì sao `chapters(novel_id)` cực kỳ quan trọng.
* Composite Index `(novel_id, chapter_number)` hỗ trợ JOIN + ORDER BY ra sao.
* `INNER JOIN` và `LEFT JOIN` ảnh hưởng thế nào đến index.
* JOIN nhiều bảng và nhiều index.
* Cách dùng `EXPLAIN QUERY PLAN` để nhìn JOIN thực tế.
* Thiết kế Repository cho app crawler/reader.

---

# 1. Bài toán cơ bản: Novel → Chapters

Ta có:

```text
novels
────────────────
id
title
```

và:

```text
chapters
────────────────
id
novel_id
chapter_number
title
content
```

Quan hệ:

```text
novels
   │
   │ 1
   │
   │ N
   ▼
chapters
```

Query:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number,
    c.title
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id;
```

Điều kiện JOIN là:

```sql
c.novel_id = n.id
```

Vậy câu hỏi:

> SQLite tìm các `chapters` tương ứng với mỗi `novel` bằng cách nào?

---

# 2. Nếu không có index

Giả sử:

```text
novels   = 10,000 rows
chapters = 1,000,000 rows
```

Nếu SQLite phải scan toàn bộ `chapters` để tìm chapters của từng novel, chi phí có thể rất lớn.

Mental model đơn giản:

```text
Novel 1
   ↓
scan chapters 1,000,000 rows

Novel 2
   ↓
scan chapters 1,000,000 rows

Novel 3
   ↓
scan chapters 1,000,000 rows

...
```

Đây là điều chúng ta muốn tránh.

---

# 3. Index trên Foreign Key

Tạo:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Bây giờ:

```text
novel.id
   ↓
index chapters.novel_id
   ↓
matching chapters
```

Mental model:

```text
             novels
                │
             n.id = 10
                │
                ▼
       chapters.novel_id
                │
                ▼
          B-tree Index
          ├── 10 → chapter
          ├── 10 → chapter
          ├── 10 → chapter
          └── ...
```

Đây là một trong những index quan trọng nhất của schema crawler.

---

# 4. FOREIGN KEY ≠ INDEX

Đây là kiến thức phải nhớ.

Bạn có:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nó đảm bảo:

```text
novel_id phải tham chiếu novel hợp lệ
```

Nhưng nó không đồng nghĩa:

```text
novel_id đã có index
```

Hai thứ phục vụ hai mục đích:

```text
FOREIGN KEY
    ↓
Data Integrity


INDEX
    ↓
Query Performance
```

---

# 5. Schema đúng cho app truyện

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
);
```

Ở đây:

```text
UNIQUE(novel_id, chapter_number)
```

đã tạo một cấu trúc index hỗ trợ uniqueness.

Vì vậy không nên vội tạo thêm:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

nếu nó hoàn toàn trùng với cấu trúc UNIQUE hiện có.

Đây là một điểm chúng ta đã học ở Buổi 33.

---

# 6. JOIN + Index

Query:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number,
    c.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Mental model:

```text
novels
   │
   │ n.id
   ▼
chapters.novel_id
   │
   ▼
Index
   │
   ▼
matching rows
```

---

# 7. SQLite thường dùng Nested Loop Join

Ở mức khái niệm, SQLite thường thực hiện JOIN bằng kiểu:

> **Nested Loop Join**

Ví dụ:

```text
for each row in novels:
    tìm rows tương ứng trong chapters
```

Nếu có index:

```text
for each novel:
    lookup chapters.novel_id
```

thì lookup có thể hiệu quả hơn rất nhiều so với scan toàn bộ `chapters`.

---

# 8. Minh họa

Có:

```text
novels

id
──
1
2
3
```

và:

```text
chapters

novel_id
────────
1
1
1
2
2
3
3
3
```

Query:

```sql
ON c.novel_id = n.id
```

SQLite về mặt khái niệm:

```text
n.id = 1
    ↓
index lookup
    ↓
chapter 1
chapter 2
chapter 3

n.id = 2
    ↓
index lookup
    ↓
chapter 4
chapter 5

n.id = 3
    ↓
index lookup
    ↓
chapter 6
chapter 7
chapter 8
```

---

# 9. Tại sao index nên nằm ở `chapters.novel_id`?

Vì quan hệ:

```text
novel 1
   ↓
many chapters
```

`novels.id` đã là:

```sql
PRIMARY KEY
```

nên SQLite đã có cấu trúc phù hợp để tìm Novel theo ID.

Phía cần tìm nhiều rows là:

```text
chapters.novel_id
```

Do đó:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

thường rất hữu ích.

Mental model:

```text
Parent PK
      │
      │ lookup
      ▼
Child FK Index
      │
      ▼
many rows
```

---

# 10. Query chỉ lấy chapters của một novel

Ví dụ:

```sql
SELECT
    c.id,
    c.chapter_number,
    c.title
FROM chapters AS c
WHERE c.novel_id = ?
ORDER BY c.chapter_number;
```

Candidate:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Index này không chỉ giúp:

```text
WHERE novel_id = ?
```

mà còn:

```text
ORDER BY chapter_number
```

Đây là lý do Composite Index cực kỳ quan trọng.

---

# 11. JOIN + ORDER BY

Query thực tế:

```sql
SELECT
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id
WHERE n.id = ?
ORDER BY c.chapter_number;
```

Candidate:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Mental model:

```text
WHERE
novel_id = ?
      ↓
INDEX
(novel_id, chapter_number)
      ↓
chapters đã theo chapter_number
      ↓
ORDER BY
```

Đây là một query pattern cực kỳ phù hợp với app đọc truyện.

---

# 12. Đây là lý do `(novel_id, chapter_number)` mạnh

Index:

```text
(novel_id, chapter_number)
```

có thứ tự:

```text
novel 1:
    chapter 1
    chapter 2
    chapter 3
    chapter 4

novel 2:
    chapter 1
    chapter 2
    chapter 3

novel 3:
    chapter 1
    chapter 2
```

Nếu query:

```sql
WHERE novel_id = 2
ORDER BY chapter_number
```

thì dữ liệu cần tìm đã nằm thành một vùng có thứ tự.

---

# 13. Nếu chỉ có `(chapter_number, novel_id)`?

Index:

```sql
CREATE INDEX idx_wrong
ON chapters(
    chapter_number,
    novel_id
);
```

Dữ liệu có dạng:

```text
chapter 1 → novel 1
chapter 1 → novel 2
chapter 1 → novel 3

chapter 2 → novel 1
chapter 2 → novel 2
...
```

Không còn grouping tự nhiên theo novel.

Nhớ:

```text
(A, B) ≠ (B, A)
```

---

# 14. JOIN nhiều bảng

Giả sử:

```text
novels
   │
   ├── chapters
   │
   └── novel_tags
          │
          ▼
         tags
```

Query:

```sql
SELECT
    n.title,
    c.chapter_number,
    t.name AS tag_name
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id
JOIN novel_tags AS nt
    ON nt.novel_id = n.id
JOIN tags AS t
    ON t.id = nt.tag_id;
```

Bây giờ có nhiều JOIN condition:

```text
c.novel_id = n.id
nt.novel_id = n.id
t.id = nt.tag_id
```

Mỗi quan hệ có workload riêng.

---

# 15. Index cần thiết ở đâu?

### `novels.id`

```sql
PRIMARY KEY
```

đã có cấu trúc hỗ trợ.

### `chapters.novel_id`

Nên cân nhắc:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

hoặc:

```text
UNIQUE(novel_id, chapter_number)
```

đã có supporting structure nếu query phù hợp.

### `novel_tags.novel_id`

Nên có index/PK phù hợp.

Ví dụ:

```sql
PRIMARY KEY (novel_id, tag_id)
```

### `novel_tags.tag_id`

Nhưng:

```text
(novel_id, tag_id)
```

không tương đương:

```text
(tag_id, novel_id)
```

Nếu query thường xuyên:

```sql
WHERE tag_id = ?
```

thì cần cân nhắc index bắt đầu bằng:

```text
tag_id
```

Ví dụ:

```sql
CREATE INDEX idx_novel_tags_tag
ON novel_tags(tag_id);
```

---

# 16. Đây là Leftmost Prefix trong JOIN

Có:

```sql
PRIMARY KEY(novel_id, tag_id)
```

Index này tự nhiên hỗ trợ:

```sql
WHERE novel_id = ?
```

Nhưng không nên mặc định rằng nó tối ưu:

```sql
WHERE tag_id = ?
```

Vì:

```text
(novel_id, tag_id)
```

có `novel_id` là leading column.

Nếu query:

```text
find all novels having tag X
```

thì:

```sql
WHERE tag_id = ?
```

có thể cần:

```sql
CREATE INDEX idx_novel_tags_tag
ON novel_tags(tag_id);
```

---

# 17. Many-to-Many cần nhìn hai chiều

Đây là nguyên tắc rất quan trọng.

Schema:

```text
novel_tags

novel_id
tag_id
```

Bạn có hai workload:

### Novel → Tags

```sql
WHERE novel_id = ?
```

### Tag → Novels

```sql
WHERE tag_id = ?
```

Do đó:

```text
(novel_id, tag_id)
```

và:

```text
(tag_id, novel_id)
```

có thể đều có lý do tồn tại.

Ví dụ:

```sql
PRIMARY KEY(novel_id, tag_id);

CREATE INDEX idx_novel_tags_tag_novel
ON novel_tags(tag_id, novel_id);
```

Đây là một pattern rất phổ biến trong junction table.

---

# 18. JOIN + WHERE

Query:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id
WHERE n.status = 'ongoing'
  AND c.chapter_number >= 1000;
```

Có hai điều kiện:

```text
novels.status
chapters.chapter_number
```

và JOIN:

```text
chapters.novel_id = novels.id
```

Index không nên được chọn chỉ dựa vào một câu query đơn giản.

Ta cần nhìn workload.

---

# 19. Có nên index `novels.status`?

Không nhất thiết.

Nếu:

```text
status = ongoing/completed
```

chỉ có hai giá trị, selectivity thấp.

Index:

```sql
CREATE INDEX idx_novels_status
ON novels(status);
```

có thể không mang lại lợi ích lớn.

Planner có thể vẫn chọn scan.

Đây là kiến thức từ Buổi 31.

---

# 20. Có nên index `chapters.chapter_number`?

Nếu query luôn:

```sql
WHERE novel_id = ?
AND chapter_number >= ?
```

thì:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

thường hợp lý hơn:

```sql
CREATE INDEX idx_chapter_number
ON chapters(chapter_number);
```

Bởi workload thực tế có:

```text
novel_id
+
chapter_number
```

---

# 21. JOIN + Composite Index

Query:

```sql
SELECT
    c.id,
    c.chapter_number,
    c.title
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id
WHERE n.id = ?
ORDER BY c.chapter_number
LIMIT 50;
```

Candidate:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Đây là một ví dụ hoàn hảo để hiểu:

```text
JOIN condition
      +
WHERE
      +
ORDER BY
      ↓
Composite Index
```

---

# 22. LEFT JOIN

Query:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

vẫn có thể rất hữu ích.

Mental model:

```text
for each novel:
    tìm chapters matching novel.id
```

Nếu không có:

```text
chapters
```

thì LEFT JOIN vẫn trả:

```text
novel + NULL
```

---

# 23. LEFT JOIN không có nghĩa "không cần index"

Sai lầm:

```text
LEFT JOIN
   ↓
không cần index
```

Không đúng.

`LEFT JOIN` vẫn cần tìm:

```text
chapters.novel_id = novels.id
```

Index ở phía right table vẫn có thể rất hữu ích.

---

# 24. LEFT JOIN + tìm novels không có chapter

Query:

```sql
SELECT
    n.id,
    n.title
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
WHERE c.id IS NULL;
```

Đây là:

```text
Novel
   ↓
LEFT JOIN
   ↓
không có child
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

có thể giúp SQLite tìm nhanh xem child tồn tại hay không.

---

# 25. JOIN + COUNT

Query:

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY n.id, n.title;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

rất phù hợp với quan hệ:

```text
novel.id
   ↓
chapters.novel_id
   ↓
COUNT
```

Đây chính là query dashboard crawler.

---

# 26. Nếu có nhiều chapters

Ví dụ:

```text
Novel A
  5,000 chapters

Novel B
  2 chapters

Novel C
  800 chapters
```

Query:

```sql
COUNT(c.id)
```

phải xử lý child rows.

Index không làm phép `COUNT` biến mất, nhưng có thể giúp tìm đúng tập child rows hiệu quả hơn.

---

# 27. JOIN + Covering Index

Giả sử query:

```sql
SELECT
    c.novel_id,
    c.chapter_number,
    c.title
FROM chapters AS c
WHERE c.novel_id = ?
ORDER BY c.chapter_number
LIMIT 50;
```

Candidate:

```sql
CREATE INDEX idx_chapters_list_cover
ON chapters(
    novel_id,
    chapter_number,
    title
);
```

Đây có thể là:

```text
Composite
+
Covering
```

cho query phù hợp.

Nếu query còn:

```text
content
```

thì:

```sql
SELECT
    chapter_number,
    title,
    content
```

index trên:

```text
novel_id
chapter_number
title
```

không còn cover toàn bộ dữ liệu cần thiết.

Và chúng ta **không nên vội đưa `content` vào index**.

---

# 28. Vì sao không index `content`?

Chapter content có thể rất lớn:

```text
10 KB
50 KB
100 KB
...
```

Nếu:

```sql
CREATE INDEX ...
ON chapters(
    novel_id,
    chapter_number,
    title,
    content
);
```

index có thể phình rất lớn.

Hậu quả:

```text
Index size ↑
Disk I/O ↑
Cache pressure ↑
INSERT cost ↑
UPDATE cost ↑
```

Đây là trade-off của Covering Index từ Buổi 34.

---

# 29. JOIN + EXPLAIN QUERY PLAN

Đây là kỹ năng quan trọng nhất.

Query:

```sql
EXPLAIN QUERY PLAN
SELECT
    n.id,
    n.title,
    c.chapter_number,
    c.title
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id
WHERE n.id = ?
ORDER BY c.chapter_number;
```

Nếu có index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

hãy chạy lại:

```sql
EXPLAIN QUERY PLAN
...
```

Bạn muốn quan sát:

```text
SCAN
```

hay:

```text
SEARCH
```

và index nào được sử dụng.

---

# 30. Đừng đọc EXPLAIN chỉ để tìm chữ INDEX

Bạn cần đặt câu hỏi:

```text
1. SQLite scan table nào?
2. SQLite search table nào?
3. Index nào được dùng?
4. JOIN order là gì?
5. Có temporary sorting không?
6. Có temporary B-tree không?
7. Có full scan lớn không?
```

Ví dụ planner có thể cho thấy dạng:

```text
SEARCH n USING INTEGER PRIMARY KEY
SEARCH c USING INDEX idx_chapters_novel_chapter
```

Điều này cho ta mental model:

```text
novels
  ↓
PK lookup
  ↓
chapters
  ↓
index lookup
```

---

# 31. JOIN Order rất quan trọng

SQL viết:

```sql
FROM novels n
JOIN chapters c
```

không có nghĩa đơn giản rằng SQLite bắt buộc phải thực hiện:

```text
novels → chapters
```

theo đúng thứ tự văn bản.

Query planner có thể chọn execution strategy phù hợp dựa trên:

```text
statistics
indexes
constraints
estimated cost
```

Đây là chủ đề chúng ta sẽ học sâu hơn ở:

> **Buổi 41 — Query Planner**

---

# 32. SQL Order vs Execution Order

Bạn viết:

```sql
SELECT ...
FROM novels n
JOIN chapters c
WHERE ...
```

Nhưng planner có thể quyết định:

```text
logical query
      ↓
query planner
      ↓
execution plan
```

Do đó:

> Đừng nhìn SQL rồi tự kết luận SQLite sẽ chạy từng dòng theo đúng thứ tự đó.

---

# 33. Một ví dụ cực kỳ quan trọng

Query:

```sql
SELECT
    n.title,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?;
```

Có index:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Nếu:

```text
n.id = 100
```

SQLite có thể làm:

```text
1. tìm novel 100
       ↓
2. lấy id = 100
       ↓
3. index lookup chapters.novel_id = 100
       ↓
4. lấy matching chapters
```

Đây là một query rất đẹp.

---

# 34. Nếu thiếu index child FK

Mental model có thể trở nên:

```text
1. tìm novel 100
       ↓
2. scan chapters
       ↓
3. check novel_id = 100
```

Nếu:

```text
chapters = 10,000,000
```

thì đây là vấn đề.

---

# 35. Index + JOIN + Pagination

App reader thường không lấy toàn bộ chapter.

Query:

```sql
SELECT
    c.id,
    c.chapter_number,
    c.title
FROM chapters AS c
WHERE c.novel_id = ?
ORDER BY c.chapter_number
LIMIT 50 OFFSET 1000;
```

Candidate:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Index giúp:

```text
WHERE
+
ORDER BY
```

Nhưng:

```text
OFFSET 1000
```

vẫn có vấn đề khi offset cực lớn.

Đó là lý do Buổi 44 sẽ học:

> **Keyset Pagination**

---

# 36. JOIN + Keyset

Sau này ta sẽ viết:

```sql
SELECT
    c.id,
    c.chapter_number,
    c.title
FROM chapters AS c
WHERE c.novel_id = ?
  AND c.chapter_number > ?
ORDER BY c.chapter_number
LIMIT 50;
```

Index:

```sql
(novel_id, chapter_number)
```

Đây là sự kết hợp cực kỳ mạnh:

```text
JOIN / relationship
+
Composite Index
+
Keyset Pagination
```

---

# 37. Repository thực tế

Ta có:

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

Candidate index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

---

# 38. Repository JOIN

Ví dụ cần hiển thị:

```text
Novel title
Chapter number
Chapter title
```

Repository:

```python
class ChapterRepository:
    def list_with_novel(
        self,
        novel_id: int,
        limit: int = 50,
    ):
        return self._conn.execute(
            """
            SELECT
                c.id,
                n.title AS novel_title,
                c.chapter_number,
                c.title AS chapter_title
            FROM chapters AS c
            INNER JOIN novels AS n
                ON n.id = c.novel_id
            WHERE c.novel_id = ?
            ORDER BY c.chapter_number
            LIMIT ?
            """,
            (novel_id, limit),
        ).fetchall()
```

Ở đây:

```text
WHERE c.novel_id = ?
```

đã giới hạn chapters.

Index:

```text
(novel_id, chapter_number)
```

rất đáng cân nhắc.

---

# 39. Có cần index `novels.id` không?

Không cần tạo:

```sql
CREATE INDEX idx_novels_id
ON novels(id);
```

nếu:

```sql
id INTEGER PRIMARY KEY
```

Vì `INTEGER PRIMARY KEY` đã có cấu trúc đặc biệt gắn với rowid.

Đây là một ví dụ của:

> **Redundant Index**

---

# 40. JOIN Indexing Checklist

Khi gặp:

```sql
A
JOIN B
ON B.a_id = A.id
```

hãy nghĩ:

```text
A.id
   ↓
PRIMARY KEY / UNIQUE?
   ↓
B.a_id
   ↓
INDEX?
```

Đặc biệt:

```text
Parent PK
+
Child FK Index
```

là một pattern rất phổ biến.

---

# 41. Với Many-to-Many

Query:

```sql
SELECT
    n.id,
    n.title
FROM novels n
JOIN novel_tags nt
    ON nt.novel_id = n.id
JOIN tags t
    ON t.id = nt.tag_id
WHERE t.name = ?;
```

Ta cần nhìn:

```text
t.name
nt.tag_id
nt.novel_id
n.id
```

Candidate indexes:

```sql
CREATE UNIQUE INDEX ...
ON tags(name);
```

`tags.name` nếu đã `UNIQUE` thì không cần index trùng.

Junction:

```sql
PRIMARY KEY(novel_id, tag_id)
```

và có thể:

```sql
CREATE INDEX idx_novel_tags_tag_novel
ON novel_tags(tag_id, novel_id);
```

nếu workload thường bắt đầu từ:

```text
tag → novels
```

---

# 42. Hai chiều của JOIN

Một lỗi thiết kế phổ biến:

```text
Tôi có PK(novel_id, tag_id)
→ vậy mọi query novel_tags đều nhanh.
```

Không đúng.

PK:

```text
(novel_id, tag_id)
```

rất phù hợp với:

```text
novel → tags
```

nhưng query:

```text
tag → novels
```

có thể cần:

```text
(tag_id, novel_id)
```

Đây chính là:

> **Index phải phản ánh hướng truy cập dữ liệu.**

---

# 43. Index không phải "cho table", mà là "cho workload"

Đây là tư duy quan trọng.

Đừng hỏi:

> "Bảng này có cần index không?"

Hãy hỏi:

> "Query nào thường xuyên chạy trên bảng này?"

Ví dụ:

```text
chapters
```

có thể có:

```text
Query A:
WHERE novel_id = ?


Query B:
WHERE novel_id = ?
ORDER BY chapter_number


Query C:
WHERE novel_id = ?
AND chapter_number > ?


Query D:
JOIN novels
ON chapters.novel_id = novels.id
```

Một index:

```text
(novel_id, chapter_number)
```

có thể phục vụ nhiều workload.

---

# 44. Nhưng đừng tạo mọi index

Ví dụ:

```sql
CREATE INDEX idx1 ON chapters(novel_id);
CREATE INDEX idx2 ON chapters(chapter_number);
CREATE INDEX idx3 ON chapters(novel_id, chapter_number);
CREATE INDEX idx4 ON chapters(chapter_number, novel_id);
```

Không nên tạo tất cả chỉ vì "có thể dùng".

Bạn phải xem:

```text
queries
+
frequency
+
data distribution
+
EXPLAIN
+
write workload
```

---

# 45. Crawler Architecture

Đây là nơi kiến thức hôm nay kết nối với project của bạn:

```text
Application
     │
     ▼
NovelRepository
ChapterRepository
     │
     ▼
Unit of Work
     │
     ▼
SQLite Connection
     │
     ▼
SQLite
```

Query:

```text
Novel
  ↓
chapters.novel_id
  ↓
Composite Index
  ↓
Chapter list
```

---

# 46. Schema đề xuất

Với crawler:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('ongoing', 'completed')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL
        CHECK (chapter_number > 0),
    title TEXT NOT NULL,
    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
);
```

Và supporting structures:

```text
novels.id
    ↓
PRIMARY KEY

chapters(novel_id, chapter_number)
    ↓
UNIQUE constraint
```

Nếu query workload phù hợp, UNIQUE structure này có thể đã đủ cho:

```text
WHERE novel_id = ?
ORDER BY chapter_number
```

Đây là lý do phải kiểm tra index hiện có trước khi tạo index mới.

---

# 47. Kiểm tra bằng PRAGMA

Trước khi tạo index:

```sql
PRAGMA index_list(chapters);
```

Ví dụ bạn thấy:

```text
sqlite_autoindex_chapters_1
```

hoặc index tương ứng với:

```text
UNIQUE(novel_id, chapter_number)
```

thì phải suy nghĩ:

> Tôi có thật sự cần thêm `(novel_id, chapter_number)` nữa không?

Thông thường không.

---

# 48. Khi nào vẫn cần `chapters(novel_id)`?

Nếu đã có:

```text
UNIQUE(novel_id, chapter_number)
```

thì index composite có leading column:

```text
novel_id
```

đã có thể hỗ trợ nhiều query chỉ lọc:

```sql
WHERE novel_id = ?
```

Do đó một index riêng:

```sql
(novel_id)
```

có thể là redundant.

Đây là một ví dụ cực hay về:

> **Leftmost Prefix + Redundant Index**

---

# 49. EXPLAIN trước khi tạo index

Quy trình:

```text
Query
  ↓
EXPLAIN QUERY PLAN
  ↓
Hiểu bottleneck
  ↓
Kiểm tra index hiện tại
  ↓
Thiết kế index
  ↓
EXPLAIN lại
  ↓
Benchmark
```

Không:

```text
JOIN
 ↓
CREATE INDEX mọi FK
```

một cách máy móc.

---

# 50. Công thức Index + JOIN

Ghi nhớ:

```text
JOIN
ON child.fk = parent.pk
        │
        ▼
Parent PK/UNIQUE
        +
Child FK Index
```

Với app truyện:

```text
novels.id
    +
chapters.novel_id
```

và nếu cần sort chapter:

```text
(novel_id, chapter_number)
```

Mental model:

```text
Novel
  │
  │ id
  ▼
Chapter Index
  │
  ├── novel_id
  └── chapter_number
          │
          ▼
      Chapter list
```

---

# 51. Bài tập thực hành

Tạo database:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id),

    UNIQUE(novel_id, chapter_number)
);
```

Thêm:

```text
100 novels
100,000 chapters
```

---

## Bài 1 — JOIN cơ bản

Viết:

```sql
SELECT
    n.title,
    c.chapter_number,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

Sau đó:

```sql
EXPLAIN QUERY PLAN
```

---

## Bài 2 — Tìm chapters của một novel

```sql
SELECT
    c.chapter_number,
    c.title
FROM chapters c
WHERE c.novel_id = ?
ORDER BY c.chapter_number;
```

Kiểm tra query plan.

---

## Bài 3 — Tạo index

Nếu cần:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Sau đó EXPLAIN lại.

---

## Bài 4 — LEFT JOIN

Viết:

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
GROUP BY n.id, n.title;
```

Kiểm tra plan.

---

# 52. Bài tập Many-to-Many

Tạo:

```text
novels
tags
novel_tags
```

với:

```sql
PRIMARY KEY(novel_id, tag_id)
```

Sau đó viết hai query:

### Query A

```text
Novel → Tags
```

### Query B

```text
Tag → Novels
```

Hãy trả lời:

> Có cần cùng một index cho cả hai query không?

---

# 53. Bài tập khó

Query:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.status = 'ongoing'
  AND c.chapter_number >= 1000
ORDER BY c.chapter_number
LIMIT 50;
```

Hãy suy nghĩ:

```text
1. JOIN column nào?
2. WHERE column nào?
3. ORDER BY column nào?
4. Index nào ở novels?
5. Index nào ở chapters?
6. Có composite index không?
7. Có cần status index không?
8. EXPLAIN QUERY PLAN cho biết gì?
```

**Không cần đoán đáp án ngay.** Đây là bài tập để luyện tư duy Query Planner.

---

# 54. Bài tập Python

Viết:

```python
class NovelRepository:
    def list_with_latest_chapter(self, limit: int = 50): ...
```

Mục tiêu:

```text
Novel
  ↓
latest chapter
```

Gợi ý bạn sẽ phải suy nghĩ về:

```sql
JOIN
+
MAX()
```

hoặc:

```sql
subquery
```

hoặc sau này:

```sql
window function
```

Đây là một bài toán tốt để luyện cách chọn query.

---

# 55. Tổng kết Buổi 38

Điểm quan trọng nhất:

### 1. FK không đồng nghĩa Index

```text
FK → integrity
Index → performance
```

### 2. JOIN thường cần lookup theo FK

```text
parent.id
    ↓
child.fk
```

### 3. Child FK thường là candidate cho index

```sql
CREATE INDEX
ON chapters(novel_id);
```

### 4. Composite Index thường tốt hơn khi có ORDER BY

```sql
(novel_id, chapter_number)
```

cho:

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

### 5. Many-to-Many phải nhìn cả hai hướng

```text
(novel_id, tag_id)
```

khác:

```text
(tag_id, novel_id)
```

### 6. Không index mù quáng

```text
Query
 ↓
EXPLAIN
 ↓
Index
 ↓
EXPLAIN
 ↓
Benchmark
```

---

# Mental Model

```text
                    JOIN
                     │
                     ▼
             ON child.fk = parent.pk
                     │
          ┌──────────┴──────────┐
          │                     │
     parent.pk              child.fk
          │                     │
     PK / UNIQUE              INDEX
          │                     │
          └──────────┬──────────┘
                     ▼
                 MATCHING
                   ROWS
                     │
                     ▼
                ORDER / WHERE
                     │
                     ▼
                   RESULT
```

Với app crawler:

```text
novels
   │
   │ id
   ▼
chapters
   │
   ├── novel_id
   └── chapter_number
          │
          ▼
(novel_id, chapter_number)
          │
          ▼
Chapter List
```

---

# Roadmap

```text
31. Index Fundamentals              ✅
32. B-Tree & SQLite Index Internals  ✅
33. Composite Index Deep Dive        ✅
34. Covering Index                   ✅
35. Partial Index                    ✅
36. Expression Index                 ✅
37. Index + LIKE                    ✅
38. Index + JOIN                    ✅
39. Index + ORDER BY                ← tiếp theo
40. EXPLAIN QUERY PLAN Deep Dive
41. Query Planner
42. ANALYZE & Statistics
43. N+1 Query
44. Keyset Pagination
45. Query Optimization thực chiến
```

**Buổi 39 — Index + ORDER BY** sẽ đi sâu vào một câu hỏi rất quan trọng: **tại sao SQLite đôi khi có thể lấy dữ liệu đã được sắp xếp trực tiếp từ B-tree mà không cần sort**, khi nào xuất hiện `USE TEMP B-TREE FOR ORDER BY`, thứ tự column ASC/DESC, Composite Index + `WHERE` + `ORDER BY`, và cách thiết kế index cho các màn hình **Novel List / Chapter List / Latest Chapters** của app đọc truyện.
