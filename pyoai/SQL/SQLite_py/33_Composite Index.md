# Buổi 33 — Composite Index Deep Dive

Đây là một trong những buổi **quan trọng nhất của phần Index**.

Buổi 31: biết Index là gì.
Buổi 32: hiểu B-Tree hoạt động ở mức khái niệm.
Buổi 33: học cách **thiết kế một Index có nhiều column**.

Đặc biệt với project crawler/Novel Reader, bạn sẽ gặp Composite Index liên tục.

---

# 1. Composite Index là gì?

Index bình thường:

```sql
CREATE INDEX idx_chapters_novel
ON chapters(novel_id);
```

Chỉ có một column.

Composite Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Có **nhiều column trong cùng một index**.

Mental model:

```text
Single Index

(novel_id)


Composite Index

(novel_id, chapter_number)
```

---

# 2. Ví dụ thực tế

Bảng:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL
);
```

Dữ liệu:

```text
id   novel_id   chapter_number
--------------------------------
1       1             1
2       1             2
3       1             3
4       1             4
5       2             1
6       2             2
7       2             3
8       3             1
9       3             2
```

Ta tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Hãy hình dung index được sắp xếp:

```text
(1, 1)
(1, 2)
(1, 3)
(1, 4)

(2, 1)
(2, 2)
(2, 3)

(3, 1)
(3, 2)
```

**Không phải:**

```text
novel_id
---------
1
1
1
1
2
2
2
3
3
```

rồi một cấu trúc độc lập khác cho `chapter_number`.

Nó là một cấu trúc có thứ tự theo **tuple**:

```text
(novel_id, chapter_number)
```

---

# 3. Quy tắc quan trọng nhất: Leftmost Prefix

Nếu có:

```sql
(novel_id, chapter_number)
```

thì column đầu tiên là:

```text
novel_id
```

SQLite có thể tận dụng index cho các pattern bắt đầu từ:

```text
novel_id
```

Ví dụ:

```sql
WHERE novel_id = ?
```

✅

Hoặc:

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

✅

Hoặc:

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

✅ rất phù hợp.

Nhưng:

```sql
WHERE chapter_number = ?
```

❌ không tương đương.

Đây gọi là:

> **Leftmost-prefix principle**

---

# 4. Tại sao?

Index:

```text
(novel_id, chapter_number)
```

được sắp xếp như:

```text
(1,1)
(1,2)
(1,3)
(1,4)

(2,1)
(2,2)
(2,3)

(3,1)
(3,2)
```

Nếu muốn:

```text
novel_id = 2
```

ta có thể tìm vùng:

```text
(2,1)
(2,2)
(2,3)
```

rất tự nhiên.

Nhưng nếu muốn:

```text
chapter_number = 2
```

thì giá trị `2` xuất hiện ở:

```text
(1,2)
(2,2)
(3,2)
```

nằm rải rác giữa nhiều `novel_id`.

Index không được tổ chức chính để tìm `chapter_number` độc lập.

---

# 5. Ví dụ giống danh bạ

Hãy tưởng tượng một danh bạ được sắp xếp:

```text
Họ → Tên
```

Ví dụ:

```text
An → Bình
An → Nam
An → Tuấn

Bình → An
Bình → Minh

Dũng → An
Dũng → Hùng
```

Bạn hỏi:

> Tìm tất cả người có họ `An`.

Rất dễ.

```text
An
 ↓
Bình
Nam
Tuấn
```

Nhưng bạn hỏi:

> Tìm tất cả người có tên `An`.

Khó hơn rất nhiều vì:

```text
Bình → An
Dũng → An
Hùng → An
...
```

Tên không phải phần đầu của thứ tự.

Composite Index cũng giống vậy.

---

# 6. Thứ tự column cực kỳ quan trọng

Hai index:

```sql
(novel_id, chapter_number)
```

và:

```sql
(chapter_number, novel_id)
```

**không giống nhau.**

Index A:

```text
(novel_id, chapter_number)
```

phù hợp với:

```sql
WHERE novel_id = ?
```

Index B:

```text
(chapter_number, novel_id)
```

phù hợp với:

```sql
WHERE chapter_number = ?
```

Do đó:

> Không chỉ hỏi "cần index những column nào?"
> Phải hỏi thêm "column nào đứng trước?"

---

# 7. Query thực tế của Novel Reader

Một query rất phổ biến:

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

Ta có:

```text
WHERE
    novel_id

ORDER BY
    chapter_number
```

Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

là một ứng viên rất tự nhiên.

Mental model:

```text
(novel_id, chapter_number)
       │          │
       │          └── ORDER BY
       └───────────── WHERE
```

---

# 8. Single Index vs Composite Index

Ta có hai index:

```sql
CREATE INDEX idx_novel
ON chapters(novel_id);

CREATE INDEX idx_chapter
ON chapters(chapter_number);
```

So với:

```sql
CREATE INDEX idx_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Không thể kết luận composite index luôn tốt hơn.

Phải nhìn vào workload.

Nếu query chủ yếu:

```sql
WHERE novel_id = ?
ORDER BY chapter_number
```

thì:

```text
(novel_id, chapter_number)
```

rất phù hợp.

---

# 9. Composite Index không phải hai Index

Đây là lỗi tư duy phổ biến.

```sql
CREATE INDEX idx_test
ON chapters(novel_id, chapter_number);
```

**không có nghĩa:**

```text
Index A: novel_id

+
Index B: chapter_number
```

Mà là:

```text
Một B-tree:

(novel_id, chapter_number)
```

Thứ tự trong tuple là một phần bản chất của index.

---

# 10. Query 1 — Chỉ column đầu

Index:

```text
(novel_id, chapter_number)
```

Query:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

✅ Đây là pattern rất tốt.

Vì:

```text
novel_id
    ↓
chapter_number
```

Index bắt đầu bằng `novel_id`.

---

# 11. Query 2 — Cả hai column

```sql
SELECT *
FROM chapters
WHERE novel_id = ?
  AND chapter_number = ?;
```

✅ Rất phù hợp.

Ví dụ:

```text
novel_id = 10
chapter_number = 500
```

SQLite có thể định vị gần:

```text
(10, 500)
```

---

# 12. Query 3 — Chỉ column thứ hai

```sql
SELECT *
FROM chapters
WHERE chapter_number = ?;
```

Với:

```text
(novel_id, chapter_number)
```

⚠️ Không phải workload lý tưởng cho index này.

Nếu application thường xuyên có query:

```sql
WHERE chapter_number = ?
```

thì có thể cần:

```sql
CREATE INDEX idx_chapters_chapter
ON chapters(chapter_number);
```

Nhưng đừng vội tạo. Hãy đo workload trước.

---

# 13. Query 4 — Range ở column thứ hai

```sql
SELECT *
FROM chapters
WHERE novel_id = ?
  AND chapter_number >= ?;
```

Ví dụ:

```text
novel_id = 10
chapter_number >= 500
```

Index:

```text
(novel_id, chapter_number)
```

rất phù hợp:

```text
novel 10
    ↓
chapter >= 500
```

Đây là một pattern cực kỳ quan trọng:

```text
Equality
   ↓
Range
```

Ví dụ:

```sql
WHERE novel_id = ?
  AND chapter_number >= ?
```

---

# 14. Equality → Range

Đây là mental model bạn nên ghi nhớ:

```text
(novel_id, chapter_number)
       │          │
       │          └── RANGE
       └───────────── EQUALITY
```

Ví dụ:

```sql
WHERE novel_id = 10
  AND chapter_number >= 500
```

SQLite có thể tìm:

```text
novel_id = 10
       ↓
chapter_number >= 500
```

rất tự nhiên.

---

# 15. Query 5 — Hai range

Ví dụ:

```sql
SELECT *
FROM chapters
WHERE novel_id >= ?
  AND chapter_number >= ?;
```

Đây là trường hợp phức tạp hơn.

Khi thiết kế composite index, **range condition có thể ảnh hưởng khả năng tận dụng các column đứng sau nó**.

Do đó không nên suy luận đơn giản:

```text
2 conditions
→ 2 columns
→ chắc chắn index dùng hoàn hảo
```

Query planner và cấu trúc index mới quyết định thực tế.

---

# 16. Một quy tắc thiết kế thực dụng

Khi thiết kế composite index, thường bắt đầu suy nghĩ:

```text
Equality columns
        ↓
Range columns
        ↓
ORDER BY columns
```

Ví dụ query:

```sql
SELECT ...
FROM chapters
WHERE novel_id = ?
  AND chapter_number >= ?
ORDER BY chapter_number
LIMIT 20;
```

ứng viên:

```text
(novel_id, chapter_number)
```

Đây là một heuristic thiết kế rất hữu ích.

Nhưng không phải công thức tuyệt đối cho mọi query; cần kiểm chứng bằng `EXPLAIN QUERY PLAN` và benchmark.

---

# 17. Composite Index + ORDER BY

Query:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number ASC;
```

Index:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(
    novel_id,
    chapter_number
);
```

Index vốn đã có thứ tự:

```text
novel_id
   ↓
chapter_number ASC
```

nên có thể giúp SQLite tránh một số công việc sort.

Đây là lý do composite index cực kỳ quan trọng cho pagination của chapter.

---

# 18. DESC thì sao?

Query:

```sql
ORDER BY chapter_number DESC
```

SQLite có khả năng scan index theo hướng ngược lại trong nhiều trường hợp.

Vì vậy đừng vội tạo riêng:

```text
(novel_id, chapter_number DESC)
```

chỉ vì query có `DESC`.

Hãy kiểm tra query plan và workload thực tế.

---

# 19. Composite Index + LIMIT

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

Index:

```text
(novel_id, chapter_number)
```

có thể cho phép SQLite:

```text
tìm novel
   ↓
đi theo chapter_number
   ↓
lấy 20 rows
```

thay vì:

```text
lấy rất nhiều rows
   ↓
sort
   ↓
chỉ giữ 20
```

Đây là một trong những workload quan trọng nhất của app đọc truyện.

---

# 20. UNIQUE cũng có thể tạo composite structure

Ta đã học:

```sql
UNIQUE(novel_id, chapter_number)
```

Ví dụ:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,

    UNIQUE (
        novel_id,
        chapter_number
    )
);
```

Nó đảm bảo:

```text
Novel 1 + Chapter 1
```

không xuất hiện hai lần.

Đồng thời cấu trúc uniqueness này cũng có thể phục vụ một số query theo prefix.

Do đó trước khi tạo:

```sql
CREATE INDEX ...
```

hãy kiểm tra constraint/index hiện có.

---

# 21. Một lỗi rất phổ biến

Bạn có:

```sql
UNIQUE(novel_id, chapter_number)
```

sau đó lại:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Có khả năng bạn vừa tạo **index dư thừa**.

Hãy kiểm tra:

```sql
PRAGMA index_list(chapters);
```

---

# 22. Composite Index với 3 column

Không chỉ có:

```text
(A, B)
```

Có thể:

```text
(A, B, C)
```

Ví dụ:

```sql
CREATE INDEX idx_chapters_lookup
ON chapters(
    novel_id,
    chapter_number,
    id
);
```

Mental model:

```text
A
 ↓
B
 ↓
C
```

Leftmost prefix:

```text
A
A + B
A + B + C
```

là các prefix tự nhiên.

Nhưng:

```text
B
B + C
```

không tương đương.

---

# 23. Ví dụ với Novel

Index:

```text
(source, status, updated_at)
```

Có thể phục vụ workload kiểu:

```sql
WHERE source = ?
```

hoặc:

```sql
WHERE source = ?
  AND status = ?
```

hoặc:

```sql
WHERE source = ?
  AND status = ?
ORDER BY updated_at DESC
```

Nhưng không nên kỳ vọng nó tương đương với:

```sql
WHERE status = ?
```

---

# 24. Chọn thứ tự column thế nào?

Đừng dùng quy tắc máy móc:

> "Column có selectivity cao nhất luôn đứng đầu."

Thực tế thiết kế composite index phụ thuộc vào **query workload**, predicates, sorting, join, cardinality và planner.

Cách thực dụng hơn:

```text
Query thực tế
      ↓
WHERE conditions
      ↓
JOIN conditions
      ↓
ORDER BY
      ↓
thiết kế candidate index
      ↓
EXPLAIN
      ↓
benchmark
```

---

# 25. Ví dụ thiết kế cho Crawler

Giả sử dashboard thường chạy:

```sql
SELECT
    id,
    title,
    updated_at
FROM novels
WHERE source = ?
  AND status = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Một candidate index đáng thử:

```sql
CREATE INDEX idx_novels_source_status_updated
ON novels(
    source,
    status,
    updated_at
);
```

Mental model:

```text
(source, status, updated_at)
      │        │       │
      │        │       └── ORDER BY
      │        └────────── filter
      └─────────────────── filter
```

Đây là ví dụ rất điển hình của composite index.

---

# 26. Một ví dụ khác

Query:

```sql
SELECT
    id,
    title
FROM novels
WHERE source = ?
ORDER BY updated_at DESC
LIMIT 20;
```

Index:

```text
(source, updated_at)
```

có thể phù hợp hơn:

```text
(source, status, updated_at)
```

nếu query **không lọc `status`**.

Điều này cho thấy:

> Index phải được thiết kế theo query thật, không phải theo cảm giác.

---

# 27. Đừng tạo quá nhiều Composite Index

Ví dụ bạn có:

```text
(A, B)
(A, C)
(A, D)
(A, E)
(A, F)
```

Database sẽ phải duy trì rất nhiều cấu trúc.

```text
INSERT
 │
 ├── index A+B
 ├── index A+C
 ├── index A+D
 ├── index A+E
 └── index A+F
```

Do đó:

```text
Read performance ↑
Write cost ↑
Storage ↑
```

Một database production cần **index strategy**, không phải index collection.

---

# 28. Kiểm tra bằng EXPLAIN QUERY PLAN

Đây là bài thực hành quan trọng.

Tạo:

```sql
CREATE INDEX idx_chapters_novel_chapter
ON chapters(novel_id, chapter_number);
```

Sau đó:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = 10
ORDER BY chapter_number
LIMIT 20;
```

Quan sát planner.

Sau đó thử:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE chapter_number = 20;
```

So sánh.

Đây là cách bạn bắt đầu **kiểm chứng mental model bằng dữ liệu thực tế**.

---

# 29. Python helper

Ta có thể viết:

```python
def explain_query(conn, sql, params=()):
    rows = conn.execute(
        "EXPLAIN QUERY PLAN " + sql,
        params,
    ).fetchall()

    for row in rows:
        print(dict(row))
```

Sử dụng:

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
    (10, 20),
)
```

Đây sẽ trở thành công cụ quen thuộc trong các buổi optimization sau.

---

# 30. Bài tập lớn — Novel Reader

Cho schema:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    UNIQUE(novel_id, chapter_number)
);
```

Application có 5 query:

### Query A

```sql
WHERE novel_id = ?
```

### Query B

```sql
WHERE novel_id = ?
  AND chapter_number = ?
```

### Query C

```sql
WHERE novel_id = ?
ORDER BY chapter_number
LIMIT 50
```

### Query D

```sql
WHERE novel_id = ?
  AND chapter_number >= ?
ORDER BY chapter_number
LIMIT 50
```

### Query E

```sql
WHERE chapter_number = ?
```

Hãy suy nghĩ:

```text
UNIQUE(novel_id, chapter_number)
```

đã hỗ trợ được query nào?

Query nào cần index riêng?

---

# 31. Câu hỏi rất quan trọng

Giả sử:

```sql
CREATE INDEX idx_a_b
ON chapters(a, b);
```

Hãy phân loại:

| Query                    | Phù hợp với `(a,b)`?          |
| ------------------------ | ----------------------------- |
| `WHERE a = ?`            | ✅                             |
| `WHERE a = ? AND b = ?`  | ✅                             |
| `WHERE a = ? AND b > ?`  | ✅                             |
| `WHERE a = ? ORDER BY b` | ✅ candidate rất tốt           |
| `WHERE b = ?`            | ⚠️ không phải prefix tự nhiên |
| `WHERE b = ? ORDER BY a` | ⚠️ cần phân tích              |
| `WHERE a > ? AND b = ?`  | ⚠️ phức tạp hơn               |

Đừng học theo kiểu:

```text
WHERE có column
→ index dùng được
```

Mà phải học:

```text
Query pattern
      ↓
Index ordering
      ↓
Leftmost prefix
      ↓
Query Planner
```

---

# 32. Mental Model của Buổi 33

Hãy nhớ hình ảnh này:

```text
INDEX
(novel_id, chapter_number)
        │
        ▼
┌────────────────────────────┐
│ novel 1                    │
│   chapter 1                │
│   chapter 2                │
│   chapter 3                │
│                            │
│ novel 2                    │
│   chapter 1                │
│   chapter 2                │
│   chapter 3                │
│                            │
│ novel 3                    │
│   chapter 1                │
└────────────────────────────┘
```

Do đó:

```text
(novel_id, chapter_number)
        │
        ├── novel_id
        │       ↓
        │     filter
        │
        └── chapter_number
                ↓
          filter / range / order
```

---

# 33. Công thức tư duy

Khi gặp query:

```sql
SELECT ...
FROM ...
WHERE ...
ORDER BY ...
LIMIT ...
```

hãy làm:

```text
                 QUERY
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
        WHERE     JOIN    ORDER BY
          │        │        │
          └────────┼────────┘
                   ▼
            Candidate Index
                   │
                   ▼
            Leftmost Prefix
                   │
                   ▼
             EXPLAIN QUERY PLAN
                   │
                   ▼
               Benchmark
```

---

# 34. 3 nguyên tắc phải thuộc

### Nguyên tắc 1

```text
(A, B)
```

không giống:

```text
(B, A)
```

### Nguyên tắc 2

```text
(A, B)
```

tự nhiên hỗ trợ prefix:

```text
A
A + B
```

nhưng không tương đương với index:

```text
B
```

### Nguyên tắc 3

Không thiết kế index dựa trên schema đơn thuần.

Thiết kế dựa trên:

```text
Workload
   ↓
Query
   ↓
Query pattern
   ↓
Index
```

---

# 35. Roadmap tiếp theo

```text
31. Index Fundamentals              ✅
32. B-Tree & SQLite Index Internals  ✅
33. Composite Index Deep Dive        ✅
34. Covering Index                   ← tiếp theo
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

**Buổi 34 — Covering Index** sẽ nối trực tiếp từ hôm nay: thay vì chỉ dùng Index để **tìm row**, chúng ta sẽ học trường hợp **Index đã chứa đủ các column mà query cần**, từ đó có thể giảm việc phải quay lại Table B-tree.
