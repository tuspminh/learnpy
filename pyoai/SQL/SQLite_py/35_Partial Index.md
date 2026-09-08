# Buổi 35 — Partial Index

Hôm nay chúng ta học một kỹ thuật rất thực tế của SQLite:

> **Partial Index = Index chỉ chứa một phần rows của table, dựa trên một điều kiện `WHERE`.**

Nếu Composite Index giúp ta tối ưu **nhiều column**, thì Partial Index giúp ta tối ưu **một tập con rows**.

Đặc biệt với app crawler, Partial Index rất hữu ích.

---

# 1. Index bình thường

Giả sử:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

Ta tạo index:

```sql
CREATE INDEX idx_novels_status
ON novels(status);
```

Index này về cơ bản phục vụ toàn bộ table:

```text
novels
│
├── ongoing
├── ongoing
├── completed
├── ongoing
├── completed
├── completed
└── ongoing
```

---

# 2. Partial Index

Bây giờ giả sử crawler thường xuyên cần:

```sql
SELECT
    id,
    title,
    updated_at
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at DESC;
```

Ta có thể tạo:

```sql
CREATE INDEX idx_novels_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Đây là:

> **Partial Index**

Mental model:

```text
                novels
                   │
          ┌────────┴────────┐
          │                 │
      ongoing            completed
          │
          ▼
     Partial Index
```

Index chỉ chứa rows:

```text
status = 'ongoing'
```

---

# 3. So sánh

### Full Index

```sql
CREATE INDEX idx_novels_updated
ON novels(updated_at);
```

Phạm vi:

```text
ALL ROWS
```

### Partial Index

```sql
CREATE INDEX idx_novels_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Phạm vi:

```text
status = 'ongoing'
```

---

# 4. Tại sao Partial Index có thể tốt hơn?

Giả sử:

```text
10,000,000 novels
```

Trong đó:

```text
9,900,000 completed
100,000 ongoing
```

Query crawler:

```sql
WHERE status = 'ongoing'
```

Full index:

```text
10,000,000 rows
```

Partial index:

```text
100,000 rows
```

Mental model:

```text
Full Index

10,000,000 rows
████████████████████████████


Partial Index

100,000 rows
█
```

Partial index nhỏ hơn có thể:

* giảm storage
* giảm index maintenance
* giảm số page phải đọc
* giảm cache pressure

Nhưng vẫn phải đo bằng workload thực tế.

---

# 5. Syntax

Cú pháp:

```sql
CREATE INDEX index_name
ON table_name(column1, column2)
WHERE condition;
```

Ví dụ:

```sql
CREATE INDEX idx_novels_ongoing_updated
ON novels(updated_at)
WHERE status = 'ongoing';
```

Điểm đặc biệt:

```sql
WHERE status = 'ongoing'
```

nằm **sau danh sách column của index**.

---

# 6. Partial Index không phải WHERE của Query

Có hai `WHERE` khác nhau.

Index:

```sql
CREATE INDEX idx_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Query:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at DESC;
```

Index `WHERE`:

```text
quy định row nào được đưa vào index
```

Query `WHERE`:

```text
quy định row nào query muốn lấy
```

---

# 7. Mental Model

```text
CREATE INDEX
ON novels(updated_at)
WHERE status = 'ongoing';

              │
              ▼

         Table novels
              │
       ┌──────┴──────┐
       │             │
   ongoing        completed
       │
       ▼
    INDEX
```

Không phải:

```text
Table
 ↓
Full Index
 ↓
lọc ongoing
```

mà:

```text
Table
 ↓
lọc ngay khi xây index
 ↓
chỉ rows phù hợp
 ↓
Index
```

---

# 8. Ví dụ với Crawler

Giả sử `novels`:

```text
id
title
source
status
updated_at
```

Crawler worker thường lấy:

```text
novel đang ongoing
```

Query:

```sql
SELECT
    id,
    title,
    source,
    updated_at
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at;
```

Candidate:

```sql
CREATE INDEX idx_novels_ongoing_updated
ON novels(
    updated_at
)
WHERE status = 'ongoing';
```

Nếu query pattern đúng và planner chọn index, đây là một ứng viên rất tốt.

---

# 9. Partial Index + Composite Index

Partial Index không chỉ có một column.

Ta có:

```sql
CREATE INDEX idx_novels_ongoing_source_updated
ON novels(
    source,
    updated_at
)
WHERE status = 'ongoing';
```

Index này có:

```text
condition:
status = 'ongoing'

keys:
(source, updated_at)
```

Mental model:

```text
Partial condition
       │
       ▼
status = ongoing
       │
       ▼
┌─────────────────────┐
│ source              │
│ updated_at          │
└─────────────────────┘
```

---

# 10. Ví dụ query

```sql
SELECT
    id,
    title,
    updated_at
FROM novels
WHERE status = 'ongoing'
  AND source = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Candidate:

```sql
CREATE INDEX idx_ongoing_source_updated
ON novels(
    source,
    updated_at
)
WHERE status = 'ongoing';
```

Đây là sự kết hợp:

```text
Partial Index
+
Composite Index
```

Rất mạnh khi workload phù hợp.

---

# 11. Partial Index + Covering Index

Bây giờ kết hợp với Buổi 34.

Query:

```sql
SELECT
    source,
    title,
    updated_at
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at DESC
LIMIT 50;
```

Ta có thể cân nhắc:

```sql
CREATE INDEX idx_ongoing_cover
ON novels(
    updated_at,
    source,
    title
)
WHERE status = 'ongoing';
```

Nếu planner chọn và index chứa đủ các column cần thiết, nó có thể vừa là:

```text
Partial Index
+
Composite Index
+
Covering Index
```

Một index có thể đồng thời mang nhiều đặc tính.

---

# 12. Nhưng đừng lạm dụng

Ví dụ:

```sql
CREATE INDEX idx1
ON novels(...)
WHERE status = 'ongoing';

CREATE INDEX idx2
ON novels(...)
WHERE status = 'completed';

CREATE INDEX idx3
ON novels(...)
WHERE source = 'site_a';

CREATE INDEX idx4
ON novels(...)
WHERE source = 'site_b';

CREATE INDEX idx5
ON novels(...)
WHERE author IS NOT NULL;
```

Bạn đang tạo rất nhiều index.

Hậu quả:

```text
INSERT
  ↓
nhiều index phải cập nhật

UPDATE
  ↓
nhiều index phải cập nhật

DELETE
  ↓
nhiều index phải cập nhật
```

Vì vậy:

> Partial Index là optimization theo workload, không phải thứ phải dùng ở mọi nơi.

---

# 13. Partial Index và `status`

Đây là ví dụ rất phù hợp để hiểu một nuance.

Ta có:

```text
status:
ongoing
completed
```

Nếu dữ liệu:

```text
50% ongoing
50% completed
```

Partial index:

```sql
WHERE status = 'ongoing'
```

chỉ giảm index xuống khoảng một nửa.

Có thể vẫn hữu ích, nhưng lợi ích không quá lớn.

Nếu:

```text
1% ongoing
99% completed
```

thì Partial Index có thể hấp dẫn hơn rất nhiều.

---

# 14. Selectivity

Ta đã học selectivity ở Buổi 31.

Partial Index thêm một lớp nữa:

```text
Column selectivity
+
Partial condition
```

Ví dụ:

```text
10,000,000 rows

ongoing = 100,000
```

thì:

```text
Partial Index
100,000 rows
```

rất nhỏ so với:

```text
Full Index
10,000,000 rows
```

Nhưng:

> "Nhỏ hơn" không tự động có nghĩa "nhanh hơn".

Planner vẫn phải đánh giá cost.

---

# 15. SQLite phải biết query phù hợp với Partial Index

Đây là điểm rất quan trọng.

Bạn tạo:

```sql
CREATE INDEX idx_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Query:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at;
```

Rất phù hợp.

Nhưng query:

```sql
SELECT *
FROM novels
WHERE status = 'completed'
ORDER BY updated_at;
```

không thể dùng Partial Index này để tìm `completed`.

Vì index chỉ chứa:

```text
ongoing
```

---

# 16. Query không có condition

Index:

```sql
CREATE INDEX idx_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Query:

```sql
SELECT *
FROM novels
ORDER BY updated_at;
```

Không có:

```text
status = 'ongoing'
```

nên Partial Index không đại diện cho toàn bộ table.

SQLite không thể coi nó như một index đầy đủ cho query này.

---

# 17. Đây là điểm khác với Full Index

Full index:

```sql
CREATE INDEX idx_updated
ON novels(updated_at);
```

phạm vi:

```text
mọi status
```

Partial:

```sql
CREATE INDEX idx_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

phạm vi:

```text
chỉ ongoing
```

Mental model:

```text
Full Index
┌───────────────────────┐
│ ongoing               │
│ completed             │
│ ongoing               │
│ completed             │
│ ...                   │
└───────────────────────┘


Partial Index
┌───────────────────────┐
│ ongoing               │
│ ongoing               │
│ ongoing               │
└───────────────────────┘
```

---

# 18. Partial Index và UPDATE

Đây là phần rất thú vị.

Có:

```sql
CREATE INDEX idx_ongoing
ON novels(updated_at)
WHERE status = 'ongoing';
```

Novel:

```text
status = ongoing
```

nằm trong index.

Sau đó:

```sql
UPDATE novels
SET status = 'completed'
WHERE id = ?;
```

Row không còn thỏa:

```text
status = 'ongoing'
```

nữa.

SQLite phải cập nhật index tương ứng.

Mental model:

```text
ongoing
   │
   ▼
IN INDEX
   │
   │ UPDATE status
   ▼
completed
   │
   ▼
REMOVE FROM INDEX
```

Ngược lại:

```text
completed
   │
   │ UPDATE
   ▼
ongoing
   │
   ▼
ADD TO INDEX
```

Do đó Partial Index vẫn có write-maintenance cost.

---

# 19. Đây là lý do phải hiểu workload

Crawler có thể thường xuyên:

```text
ongoing → completed
```

Nếu vậy Partial Index trên `status='ongoing'` sẽ phải cập nhật khi trạng thái thay đổi.

Nhưng nếu:

```text
status
```

gần như ổn định và query ongoing rất nhiều:

```text
Partial Index
```

có thể rất phù hợp.

---

# 20. Partial Index với NULL

Một use case hay:

```text
chapters
```

có:

```text
crawled_at
```

Một số chapter chưa crawl:

```text
crawled_at IS NULL
```

Ta có:

```sql
CREATE INDEX idx_chapters_pending
ON chapters(novel_id, chapter_number)
WHERE crawled_at IS NULL;
```

Crawler query:

```sql
SELECT
    id,
    novel_id,
    chapter_number
FROM chapters
WHERE crawled_at IS NULL
ORDER BY novel_id, chapter_number
LIMIT 100;
```

Đây là một ứng dụng **rất thực tế**.

---

# 21. Crawler Queue bằng Partial Index

Ta có:

```text
chapters
────────────────────
id
novel_id
chapter_number
title
content
crawled_at
```

Trạng thái:

```text
crawled_at IS NULL
```

= chưa crawl.

Partial index:

```sql
CREATE INDEX idx_pending_chapters
ON chapters(
    novel_id,
    chapter_number
)
WHERE crawled_at IS NULL;
```

Mental model:

```text
              chapters
                  │
          ┌───────┴────────┐
          │                │
    crawled_at NULL    crawled_at != NULL
          │
          ▼
    Partial Index
          │
          ▼
    Pending Queue
```

Đây chính là kiểu thiết kế có thể dùng cho crawler worker.

---

# 22. Một use case còn tốt hơn

Giả sử:

```text
crawl_status
```

có:

```text
pending
crawling
success
failed
```

Worker thường lấy:

```sql
WHERE crawl_status = 'pending'
```

Ta có:

```sql
CREATE INDEX idx_pending_chapters
ON chapters(
    novel_id,
    chapter_number
)
WHERE crawl_status = 'pending';
```

Nếu `pending` chỉ chiếm một phần nhỏ dữ liệu, index này rất đáng cân nhắc.

---

# 23. Partial Index không thay thế constraint

Ví dụ:

```sql
CREATE INDEX idx_pending
ON chapters(novel_id)
WHERE crawl_status = 'pending';
```

Không có nghĩa:

```text
crawl_status chỉ được là pending
```

Index chỉ phục vụ query.

Validation vẫn nên dùng:

```sql
CHECK (
    crawl_status IN (
        'pending',
        'crawling',
        'success',
        'failed'
    )
)
```

Hai khái niệm:

```text
Constraint
   ↓
Correctness


Index
   ↓
Performance
```

Đây là một nguyên tắc bạn đã gặp ở Buổi 25.

---

# 24. Partial Index vs CHECK

### CHECK

```sql
CHECK (
    status IN ('ongoing', 'completed')
)
```

Mục đích:

```text
Đảm bảo dữ liệu hợp lệ
```

### Partial Index

```sql
CREATE INDEX ...
WHERE status = 'ongoing';
```

Mục đích:

```text
Tối ưu query
```

Không được nhầm hai thứ.

---

# 25. Partial Index vs WHERE trong Query

Query:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing';
```

`WHERE` ở query:

```text
lọc kết quả
```

Partial Index:

```sql
CREATE INDEX ...
WHERE status = 'ongoing';
```

`WHERE` ở index:

```text
lọc rows được lưu trong index
```

Mental model:

```text
TABLE
  │
  ├── all rows
  │
  ▼
PARTIAL INDEX
  │
  └── chỉ rows thỏa condition


QUERY
  │
  ▼
tìm trong index
  │
  ▼
result
```

---

# 26. Partial Index + Python

Ví dụ migration:

```python
conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_pending_chapters
    ON chapters(
        novel_id,
        chapter_number
    )
    WHERE crawl_status = 'pending'
""")
```

Query Repository:

```python
class ChapterRepository:
    def get_pending(self, limit: int = 100):
        return self._conn.execute(
            """
            SELECT
                id,
                novel_id,
                chapter_number
            FROM chapters
            WHERE crawl_status = 'pending'
            ORDER BY novel_id, chapter_number
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
```

Repository không cần biết:

```text
"query này dùng Partial Index"
```

Đây là trách nhiệm của database/query planner.

---

# 27. Dùng EXPLAIN QUERY PLAN

Đây là phần thực hành bắt buộc.

Tạo:

```sql
CREATE INDEX idx_pending_chapters
ON chapters(
    novel_id,
    chapter_number
)
WHERE crawl_status = 'pending';
```

Sau đó:

```sql
EXPLAIN QUERY PLAN
SELECT
    id,
    novel_id,
    chapter_number
FROM chapters
WHERE crawl_status = 'pending'
  AND novel_id = ?
ORDER BY chapter_number
LIMIT 100;
```

Quan sát:

```text
USING INDEX ...
```

hoặc plan thực tế mà SQLite lựa chọn.

Điểm quan trọng:

> Không đoán planner. Hãy hỏi planner.

---

# 28. Kiểm tra index

```sql
PRAGMA index_list(chapters);
```

Bạn sẽ thấy index.

Thông tin chi tiết:

```sql
PRAGMA index_info(idx_pending_chapters);
```

SQLite còn cung cấp metadata để kiểm tra schema/index.

---

# 29. Một lỗi thiết kế phổ biến

Bạn có:

```sql
CREATE INDEX idx_pending
ON chapters(novel_id)
WHERE crawl_status = 'pending';
```

Nhưng query:

```sql
SELECT *
FROM chapters
WHERE crawl_status IN ('pending', 'failed')
  AND novel_id = ?;
```

Partial index chỉ chứa:

```text
pending
```

không chứa:

```text
failed
```

Do đó không thể kỳ vọng index phục vụ toàn bộ query như một full index.

Nếu workload thực tế là:

```text
pending OR failed
```

có thể thiết kế:

```sql
CREATE INDEX idx_pending_failed
ON chapters(novel_id)
WHERE crawl_status IN ('pending', 'failed');
```

Nhưng chỉ khi đó thực sự là workload cần tối ưu.

---

# 30. Một ví dụ với `is_deleted`

Giả sử soft delete:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    is_deleted INTEGER NOT NULL DEFAULT 0
);
```

Application gần như luôn query:

```sql
SELECT
    id,
    title
FROM novels
WHERE is_deleted = 0;
```

Có thể cân nhắc:

```sql
CREATE INDEX idx_active_novels
ON novels(title)
WHERE is_deleted = 0;
```

Nhưng phải xem query thật sự cần gì.

Nếu query thường:

```sql
WHERE is_deleted = 0
ORDER BY title
```

thì:

```text
(title)
```

có thể phù hợp.

---

# 31. Partial Index và Soft Delete

Đây là pattern phổ biến:

```text
Table
│
├── active
└── deleted
       │
       └── thường ít truy cập
```

Partial Index:

```sql
CREATE INDEX idx_active_novels
ON novels(updated_at)
WHERE is_deleted = 0;
```

Nếu phần lớn query chỉ quan tâm active records, đây là một candidate tốt.

---

# 32. Partial Index + Composite Index

Ví dụ:

```sql
CREATE INDEX idx_active_source_updated
ON novels(
    source,
    updated_at
)
WHERE is_deleted = 0;
```

Query:

```sql
SELECT
    id,
    title,
    updated_at
FROM novels
WHERE is_deleted = 0
  AND source = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Ta đang kết hợp:

```text
Partial condition
        +
Composite keys
```

Đây là pattern rất đáng nhớ.

---

# 33. Partial Index + Covering Index

Tiếp tục:

```sql
CREATE INDEX idx_active_source_updated_cover
ON novels(
    source,
    updated_at,
    title
)
WHERE is_deleted = 0;
```

Query:

```sql
SELECT
    source,
    updated_at,
    title
FROM novels
WHERE is_deleted = 0
  AND source = ?
ORDER BY updated_at DESC
LIMIT 50;
```

Candidate này có thể đồng thời là:

```text
Partial
+
Composite
+
Covering
```

Nếu query planner chọn nó.

---

# 34. Nhưng hãy nhớ một điều

Không phải:

```text
Partial
+
Composite
+
Covering
=
luôn nhanh nhất
```

Mà:

```text
Candidate
    ↓
EXPLAIN
    ↓
Benchmark
    ↓
Workload
    ↓
Decision
```

Đây là tư duy optimization mà chúng ta sẽ dùng xuyên suốt Part V.

---

# 35. So sánh Full vs Partial

| Đặc điểm          | Full Index      | Partial Index             |
| ----------------- | --------------- | ------------------------- |
| Rows              | Tất cả          | Một subset                |
| Storage           | Lớn hơn         | Có thể nhỏ hơn            |
| Write maintenance | Nhiều hơn       | Có thể ít hơn             |
| Query scope       | Rộng            | Hẹp                       |
| Điều kiện `WHERE` | Không có        | Bắt buộc                  |
| Phù hợp           | Query tổng quát | Query trên subset ổn định |
| Crawler queue     | Có thể          | ⭐ Rất phù hợp             |
| Soft delete       | Có thể          | ⭐ Phù hợp                 |

---

# 36. Bài tập thực hành

Tạo bảng:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    crawl_status TEXT NOT NULL
        CHECK (
            crawl_status IN (
                'pending',
                'crawling',
                'success',
                'failed'
            )
        )
);
```

Tạo dữ liệu:

```text
100,000 chapters
```

Trong đó:

```text
success = 95,000
pending = 4,000
failed  = 1,000
```

---

## Bài 1

Tạo full index:

```sql
CREATE INDEX idx_chapters_status
ON chapters(crawl_status);
```

Sau đó tạo partial:

```sql
CREATE INDEX idx_pending
ON chapters(novel_id, chapter_number)
WHERE crawl_status = 'pending';
```

So sánh hai index.

---

## Bài 2

Query worker:

```sql
SELECT
    id,
    novel_id,
    chapter_number
FROM chapters
WHERE crawl_status = 'pending'
ORDER BY novel_id, chapter_number
LIMIT 100;
```

Hãy dùng:

```sql
EXPLAIN QUERY PLAN
```

để kiểm tra.

---

## Bài 3

Thử:

```sql
WHERE crawl_status = 'success'
```

Partial index `pending` có phù hợp không?

---

## Bài 4

Thiết kế Partial Index cho:

```text
novels đang ongoing
```

Query:

```sql
SELECT
    id,
    title,
    updated_at
FROM novels
WHERE status = 'ongoing'
ORDER BY updated_at DESC
LIMIT 50;
```

---

## Bài 5

Thiết kế Partial + Composite Index cho:

```text
source = ?
status = ongoing
ORDER BY updated_at DESC
```

---

# 37. Bài tập kiến trúc — Crawler Worker

Hãy thiết kế:

```text
                  SQLite
                     │
                 chapters
                     │
             crawl_status
                     │
        ┌────────────┴────────────┐
        │                         │
     pending                    success
        │
        ▼
 Partial Index
        │
        ▼
  Worker lấy job
        │
        ▼
    HTTP Crawl
        │
        ▼
     UPDATE
   pending → success
```

Câu hỏi:

> Tại sao Partial Index rất hợp với mô hình này?

Gợi ý:

```text
pending thường là subset nhỏ
+
worker query pending thường xuyên
+
success chiếm phần lớn table
```

---

# 38. Một nuance rất quan trọng

Partial Index không chỉ dùng cho:

```sql
WHERE status = 'pending'
```

Có thể dùng condition phức tạp hơn.

Ví dụ:

```sql
CREATE INDEX idx_large_pending
ON chapters(novel_id, chapter_number)
WHERE crawl_status = 'pending'
  AND chapter_number >= 1000;
```

Nhưng càng phức tạp:

```text
Index design
    ↓
Query matching
    ↓
Planner behavior
```

càng cần kiểm chứng kỹ.

Không nên tạo partial index chỉ vì SQL "trông hợp lý".

---

# 39. Mental Model toàn bộ Index đến hiện tại

```text
                    INDEX
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
     Single       Composite       Partial
        │             │             │
      (A)           (A,B)       WHERE condition
                      │
                      ▼
                 Covering
```

Một index cụ thể có thể:

```text
Composite
    +
Partial
    +
Covering
```

Ví dụ:

```sql
CREATE INDEX idx_pending_chapter_list
ON chapters(
    novel_id,
    chapter_number,
    title
)
WHERE crawl_status = 'pending';
```

Index này:

```text
Composite
        +
Partial
        +
có thể Covering cho query phù hợp
```

---

# 40. Công thức của Buổi 35

Hãy ghi nhớ:

```text
Partial Index
=
Index
+
WHERE condition
```

Ví dụ:

```sql
CREATE INDEX idx_pending
ON chapters(novel_id, chapter_number)
WHERE crawl_status = 'pending';
```

Mental model:

```text
                 chapters
                     │
             WHERE pending
                     │
                     ▼
              ┌────────────┐
              │   INDEX    │
              │            │
              │ novel_id   │
              │ chapter_no │
              └────────────┘
```

Và nguyên tắc quan trọng nhất:

> **Partial Index phù hợp khi query thường xuyên truy cập một subset rows tương đối ổn định và có ý nghĩa trong workload.**

---

# Roadmap

```text
31. Index Fundamentals              ✅
32. B-Tree & SQLite Index Internals  ✅
33. Composite Index Deep Dive        ✅
34. Covering Index                   ✅
35. Partial Index                    ✅
36. Expression Index                 ← tiếp theo
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

**Buổi 36 — Expression Index** sẽ nâng level thêm một bước: chúng ta sẽ học cách index **kết quả của một biểu thức**, ví dụ `LOWER(title)`, `trim(title)`, hoặc một phép tính trên column, để tối ưu những query mà index thông thường không xử lý trực tiếp.
