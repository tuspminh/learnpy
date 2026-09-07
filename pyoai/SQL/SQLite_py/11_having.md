# Buổi 11 — `HAVING` trong SQL + SQLite + Python

Hôm nay ta học:

```sql
HAVING
```

Đây là phần **rất quan trọng** vì nó liên quan trực tiếp đến sự khác nhau giữa:

```sql
WHERE
```

và:

```sql
HAVING
```

Nếu hiểu được hai câu này, bạn đã bắt đầu nắm được tư duy SQL khá sâu.

---

# 1. Vấn đề mà `HAVING` giải quyết

Buổi 10 ta đã biết:

```sql
SELECT
    status,
    COUNT(*) AS total
FROM novels
GROUP BY status;
```

Kết quả:

```text
status       total
-----------  -----
completed    20
ongoing      50
```

Bây giờ yêu cầu:

> Chỉ lấy những status có **ít nhất 30 novel**.

Ta không thể viết:

```sql
WHERE COUNT(*) >= 30
```

❌ Sai.

Vì `COUNT(*)` là aggregate được tính **sau khi các row được gom nhóm**.

Ta cần:

```sql
HAVING COUNT(*) >= 30
```

---

# 2. `HAVING` là gì?

`HAVING` dùng để:

> **lọc các group sau khi `GROUP BY` đã tạo ra các nhóm.**

Ví dụ:

```sql
SELECT
    status,
    COUNT(*) AS total
FROM novels
GROUP BY status
HAVING COUNT(*) >= 30;
```

Tư duy:

```text
novels
   ↓
GROUP BY status
   ↓
tạo các group
   ↓
COUNT(*)
   ↓
HAVING COUNT(*) >= 30
   ↓
chỉ giữ group đạt điều kiện
```

---

# 3. `WHERE` vs `HAVING`

Đây là kiến thức phải nhớ.

## `WHERE`

Lọc **row**.

```sql
SELECT *
FROM novels
WHERE status = 'ongoing';
```

Nó hỏi:

> Row nào được tham gia vào query?

---

## `HAVING`

Lọc **group**.

```sql
SELECT
    status,
    COUNT(*) AS total
FROM novels
GROUP BY status
HAVING COUNT(*) >= 30;
```

Nó hỏi:

> Group nào được giữ lại?

---

# 4. So sánh trực quan

```text
WHERE
  ↓
lọc ROW
  ↓
GROUP BY
  ↓
tạo GROUP
  ↓
HAVING
  ↓
lọc GROUP
```

Đây là mental model quan trọng nhất của Buổi 11.

---

# 5. Ví dụ đơn giản

Giả sử:

```text
novels

id | status
---+----------
1  | ongoing
2  | ongoing
3  | ongoing
4  | completed
5  | completed
```

Query:

```sql
SELECT
    status,
    COUNT(*) AS total
FROM novels
GROUP BY status;
```

Kết quả:

```text
ongoing     3
completed   2
```

Thêm:

```sql
HAVING COUNT(*) >= 3;
```

Kết quả:

```text
ongoing     3
```

`completed` bị loại vì:

```text
2 < 3
```

---

# 6. `HAVING` thường đi với Aggregate

Đây là pattern phổ biến:

```sql
SELECT
    column,
    COUNT(*) AS total
FROM table
GROUP BY column
HAVING COUNT(*) > 10;
```

Ví dụ:

> Tìm các tác giả có ít nhất 5 truyện.

```sql
SELECT
    author,
    COUNT(*) AS total_novels
FROM novels
GROUP BY author
HAVING COUNT(*) >= 5;
```

Kết quả:

```text
author       total_novels
-----------  ------------
Nhĩ Căn      8
Thần Đông    6
```

---

# 7. `HAVING` với `SUM`

Ví dụ:

> Tìm các source có tổng số chapter lớn hơn 100.000.

```sql
SELECT
    source,
    SUM(chapter_count) AS total_chapters
FROM novels
GROUP BY source
HAVING SUM(chapter_count) > 100000;
```

Đây là một query rất thực tế cho crawler dashboard.

---

# 8. `HAVING` với `AVG`

Ví dụ:

> Tìm những source có số chapter trung bình mỗi novel trên 1.000.

```sql
SELECT
    source,
    AVG(chapter_count) AS average_chapters
FROM novels
GROUP BY source
HAVING AVG(chapter_count) > 1000;
```

---

# 9. `HAVING` với `MIN` / `MAX`

Ví dụ:

> Source nào có novel dài nhất trên 5.000 chapter?

```sql
SELECT
    source,
    MAX(chapter_count) AS max_chapters
FROM novels
GROUP BY source
HAVING MAX(chapter_count) > 5000;
```

---

# 10. `HAVING` + `WHERE`

Đây là phần rất quan trọng.

Ta hoàn toàn có thể dùng cả hai.

Ví dụ:

> Trong các novel `ongoing`, tìm những source có ít nhất 20 novel.

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source
HAVING COUNT(*) >= 20;
```

Pipeline:

```text
Tất cả novels
      ↓
WHERE status = ongoing
      ↓
chỉ còn ongoing novels
      ↓
GROUP BY source
      ↓
đếm từng source
      ↓
HAVING COUNT(*) >= 20
      ↓
chỉ giữ source có >= 20
```

---

# 11. Đây là lỗi rất hay gặp

Giả sử muốn:

> Tìm source có ít nhất 20 novel.

Một người mới có thể viết:

```sql
SELECT
    source,
    COUNT(*)
FROM novels
WHERE COUNT(*) >= 20
GROUP BY source;
```

❌ Sai.

`WHERE` không dùng để lọc aggregate như `COUNT(*)`.

Đúng:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING COUNT(*) >= 20;
```

---

# 12. Vì sao `WHERE COUNT(*)` không hợp lý?

Hãy nhìn pipeline:

```text
WHERE
 ↓
row filtering
 ↓
GROUP BY
 ↓
COUNT
 ↓
HAVING
```

Khi `WHERE` đang chạy thì:

```text
COUNT(*)
```

chưa được tính theo group.

Vì vậy:

```sql
WHERE COUNT(*) >= 20
```

không đúng mục đích.

`HAVING` mới là nơi phù hợp.

---

# 13. `HAVING` có bắt buộc phải có `GROUP BY` không?

Thông thường khi học và thiết kế query, hãy nhớ:

```text
GROUP BY + HAVING
```

là cặp rất tự nhiên.

Ví dụ:

```sql
SELECT
    status,
    COUNT(*)
FROM novels
GROUP BY status
HAVING COUNT(*) > 10;
```

Tuy nhiên SQL/SQLite có thể cho phép một số dạng `HAVING` không có `GROUP BY`.

Ví dụ:

```sql
SELECT COUNT(*) AS total
FROM novels
HAVING COUNT(*) > 10;
```

Ý nghĩa:

```text
toàn bộ bảng
   ↓
một aggregate result
   ↓
HAVING
```

Nếu có hơn 10 row thì trả kết quả.

Nhưng ở giai đoạn này, hãy tập trung vào pattern:

```text
GROUP BY
   +
HAVING
```

---

# 14. Có thể dùng alias trong `HAVING`

Ví dụ:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING total >= 20;
```

SQLite hỗ trợ kiểu viết này.

Tuy nhiên để code SQL dễ portable sang các hệ quản trị khác, tôi khuyên bạn quen với:

```sql
HAVING COUNT(*) >= 20
```

hơn là phụ thuộc vào alias trong `HAVING`.

---

# 15. `HAVING` nhiều điều kiện

Ta có thể dùng:

```sql
AND
OR
```

Ví dụ:

> Source có ít nhất 20 novel và tổng chapter trên 100.000.

```sql
SELECT
    source,
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters
FROM novels
GROUP BY source
HAVING COUNT(*) >= 20
   AND SUM(chapter_count) > 100000;
```

---

# 16. `HAVING` + `ORDER BY`

Ví dụ:

> Tìm source có ít nhất 20 novel, rồi xếp theo số novel giảm dần.

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING COUNT(*) >= 20
ORDER BY total DESC;
```

Pipeline:

```text
WHERE
 ↓
GROUP BY
 ↓
AGGREGATE
 ↓
HAVING
 ↓
ORDER BY
```

---

# 17. `HAVING` + `ORDER BY` + `LIMIT`

Ví dụ:

> Top 5 source có ít nhất 20 novel.

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING COUNT(*) >= 20
ORDER BY total DESC
LIMIT 5;
```

Đây là query rất thực tế.

---

# 18. Python + SQLite

Với `sqlite3.Row`:

```python
conn.row_factory = sqlite3.Row

cursor = conn.execute(
    """
    SELECT
        source,
        COUNT(*) AS total
    FROM novels
    GROUP BY source
    HAVING COUNT(*) >= ?
    ORDER BY total DESC
    """,
    (20,),
)

rows = cursor.fetchall()

for row in rows:
    print(
        row["source"],
        row["total"],
    )
```

Lưu ý:

```python
(20,)
```

là parameter của SQL.

Không nên:

```python
f"HAVING COUNT(*) >= {minimum}"
```

dù trong ví dụ đơn giản nó có thể chạy.

Hãy quen với parameterized query.

---

# 19. Repository thực tế

Ta có thể viết:

```python
class NovelRepository:

    def find_sources_with_min_novels(
        self,
        minimum: int,
    ) -> list[sqlite3.Row]:

        cursor = self._conn.execute(
            """
            SELECT
                source,
                COUNT(*) AS total
            FROM novels
            GROUP BY source
            HAVING COUNT(*) >= ?
            ORDER BY total DESC
            """,
            (minimum,),
        )

        return cursor.fetchall()
```

Sử dụng:

```python
rows = repo.find_sources_with_min_novels(20)

for row in rows:
    print(row["source"], row["total"])
```

Điểm hay:

```text
Application
     ↓
find_sources_with_min_novels(20)
     ↓
Repository
     ↓
SQL
```

Application không cần biết chi tiết SQL.

---

# 20. Ví dụ thực tế với crawler

Giả sử database:

```text
novels
├── source
├── title
├── author
├── status
└── chapter_count
```

Dashboard muốn:

### Source nào có nhiều novel?

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
ORDER BY total DESC;
```

### Source nào có ít nhất 100 novel?

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING COUNT(*) >= 100;
```

### Source nào có ít nhất 100 novel ongoing?

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source
HAVING COUNT(*) >= 100;
```

### Source nào có ít nhất 100 novel và tổng chapter > 1 triệu?

```sql
SELECT
    source,
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters
FROM novels
GROUP BY source
HAVING COUNT(*) >= 100
   AND SUM(chapter_count) > 1000000;
```

Đây đã là những query có tính **phân tích dữ liệu thực tế**.

---

# 21. Một cách tư duy cực mạnh

Khi đọc yêu cầu tiếng Việt, hãy xác định:

### Nếu nói:

> "những dòng nào..."

→ `WHERE`

### Nếu nói:

> "theo từng..."

→ `GROUP BY`

### Nếu nói:

> "những nhóm có..."

→ `HAVING`

Ví dụ:

> Những source có ít nhất 50 truyện.

Phân tích:

```text
source
   ↓
GROUP BY source

có ít nhất 50
   ↓
HAVING COUNT(*) >= 50
```

SQL:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
HAVING COUNT(*) >= 50;
```

---

# 22. Bảng ghi nhớ

| Thành phần | Lọc cái gì?     | Thời điểm tư duy  |
| ---------- | --------------- | ----------------- |
| `WHERE`    | Row             | Trước `GROUP BY`  |
| `GROUP BY` | Tạo nhóm        | Sau `WHERE`       |
| Aggregate  | Tính trên group | Sau grouping      |
| `HAVING`   | Group           | Sau aggregate     |
| `ORDER BY` | Kết quả         | Sau khi có result |
| `LIMIT`    | Số kết quả      | Cuối              |

Mental model:

```text
FROM
 ↓
WHERE       ← lọc ROW
 ↓
GROUP BY    ← tạo GROUP
 ↓
AGGREGATE   ← COUNT/SUM/AVG...
 ↓
HAVING      ← lọc GROUP
 ↓
ORDER BY
 ↓
LIMIT
```

---

# 23. Bài tập Buổi 11

Giả sử:

```text
novels

id
source
title
author
status
chapter_count
```

### Bài 1

Tìm các `status` có ít nhất 10 novel.

---

### Bài 2

Tìm các `source` có ít nhất 20 novel.

---

### Bài 3

Tìm các `author` có ít nhất 5 novel.

---

### Bài 4

Tìm các source có tổng chapter lớn hơn `100000`.

---

### Bài 5

Tìm các source có chapter trung bình trên `1000`.

---

### Bài 6

Chỉ xét:

```text
status = 'ongoing'
```

Tìm source có ít nhất 20 novel.

---

### Bài 7

Tìm source thỏa cả hai điều kiện:

```text
ít nhất 20 novel
AND
tổng chapter > 100000
```

---

### Bài 8 — quan trọng

Viết query:

> Top 5 author có ít nhất 10 novel, sắp xếp theo số novel giảm dần.

---

### Bài 9 — Python

Viết:

```python
def find_large_sources(
    conn: sqlite3.Connection,
    minimum: int,
) -> list[sqlite3.Row]:
    ...
```

Yêu cầu:

```text
source
total
```

và chỉ trả về những source có:

```text
COUNT(*) >= minimum
```

---

# 24. Bài tập tư duy

Cho query:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source
HAVING COUNT(*) >= 20
ORDER BY total DESC
LIMIT 5;
```

Hãy tự giải thích từng bước:

```text
FROM novels
      ↓
?
      ↓
?
      ↓
?
      ↓
?
      ↓
?
```

Nếu bạn giải thích được query này bằng tiếng Việt mà **không cần nhìn tài liệu**, thì `WHERE → GROUP BY → HAVING` đã bắt đầu thành phản xạ.

---

## Roadmap

```text
7   Operators                    ✅
8   AND / OR / NOT               ✅
9   COUNT / SUM / AVG / MIN/MAX  ✅
10  GROUP BY                     ✅
11  HAVING                       ← hôm nay
12  DISTINCT
13  CASE WHEN
```

**Buổi 12 — `DISTINCT`** sẽ giải quyết một nhu cầu rất thường gặp:

> “Lấy danh sách các giá trị **không trùng nhau**.”

Ví dụ:

```sql
SELECT DISTINCT source
FROM novels;
```

→ lấy danh sách các website nguồn duy nhất.
