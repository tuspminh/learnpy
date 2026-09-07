# Buổi 10 — `GROUP BY` trong SQL + SQLite + Python

Hôm nay chúng ta học một trong những phần **quan trọng nhất của SQL thực tế**:

```sql
GROUP BY
```

Nếu `WHERE` trả lời:

> “Lấy những dòng nào?”

thì `GROUP BY` trả lời:

> **“Chia các dòng thành những nhóm nào để tính thống kê?”**

---

# 1. Ôn lại Aggregate

Buổi 9 ta đã học:

```sql
COUNT()
SUM()
AVG()
MIN()
MAX()
```

Ví dụ:

```sql
SELECT COUNT(*)
FROM novels;
```

Kết quả:

```text
5
```

Đây là thống kê **toàn bộ bảng**.

Nhưng giả sử ta muốn biết:

```text
Có bao nhiêu truyện ongoing?
Có bao nhiêu truyện completed?
```

Ta cần:

```sql
GROUP BY
```

---

# 2. `GROUP BY` là gì?

Giả sử bảng:

```text
novels

id | title                  | status
---+------------------------+----------
1  | Tiên Nghịch             | ongoing
2  | Phàm Nhân Tu Tiên       | completed
3  | Đấu Phá Thương Khung    | completed
4  | Linh Vũ Thiên Hạ        | ongoing
5  | Test Novel              | ongoing
```

Ta viết:

```sql
SELECT status, COUNT(*)
FROM novels
GROUP BY status;
```

Kết quả:

```text
status      COUNT(*)
----------- --------
completed   2
ongoing     3
```

SQL đã thực hiện về mặt ý tưởng:

```text
novels
   │
   ├── ongoing
   │      ├── row 1
   │      ├── row 4
   │      └── row 5
   │
   └── completed
          ├── row 2
          └── row 3
```

Sau đó:

```text
ongoing    → COUNT = 3
completed  → COUNT = 2
```

---

# 3. Công thức tư duy

Hãy nhớ:

```text
GROUP BY column
+
Aggregate Function
```

Ví dụ:

```sql
SELECT status, COUNT(*)
FROM novels
GROUP BY status;
```

Có thể đọc thành:

> Nhóm các novel theo `status`, sau đó đếm số novel trong mỗi nhóm.

---

# 4. `GROUP BY` + `COUNT()`

Đây là trường hợp phổ biến nhất.

### Đếm theo status

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
completed    2
ongoing      3
```

### Python

```python
cursor = conn.execute(
    """
    SELECT
        status,
        COUNT(*) AS total
    FROM novels
    GROUP BY status
    """
)

rows = cursor.fetchall()

for row in rows:
    print(row["status"], row["total"])
```

Nếu dùng:

```python
conn.row_factory = sqlite3.Row
```

thì rất tiện:

```python
row["status"]
row["total"]
```

---

# 5. `GROUP BY` không nhất thiết phải đi với `COUNT`

Có thể kết hợp với tất cả aggregate.

## `SUM`

Ví dụ tổng số chapter theo status:

```sql
SELECT
    status,
    SUM(chapter_count) AS total_chapters
FROM novels
GROUP BY status;
```

Kết quả có thể:

```text
status       total_chapters
-----------  --------------
completed    4098
ongoing      5110
```

---

# 6. `AVG`

Tính số chapter trung bình theo status:

```sql
SELECT
    status,
    AVG(chapter_count) AS average_chapters
FROM novels
GROUP BY status;
```

Ví dụ:

```text
status       average_chapters
-----------  ----------------
completed    2049.0
ongoing      1703.3
```

---

# 7. `MIN` và `MAX`

```sql
SELECT
    status,
    MIN(chapter_count) AS min_chapters,
    MAX(chapter_count) AS max_chapters
FROM novels
GROUP BY status;
```

Kết quả:

```text
status       min    max
-----------  -----  -----
completed    1648   2450
ongoing      10     3000
```

---

# 8. Một query có nhiều Aggregate

Đây là pattern rất thực tế.

```sql
SELECT
    status,
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters,
    AVG(chapter_count) AS average_chapters,
    MIN(chapter_count) AS min_chapters,
    MAX(chapter_count) AS max_chapters
FROM novels
GROUP BY status;
```

Ta nhận được:

```text
status
total_novels
total_chapters
average_chapters
min_chapters
max_chapters
```

cho **từng status**.

Đây chính là kiểu query rất hữu ích cho dashboard.

---

# 9. `GROUP BY source`

Giả sử bảng novel có:

```text
source
------
site_a
site_b
site_c
```

Ta muốn biết mỗi website có bao nhiêu truyện:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source;
```

Ví dụ:

```text
source      total
----------  -----
site_a      120
site_b      85
site_c      43
```

Trong crawler project, query này cực kỳ hữu ích.

---

# 10. `GROUP BY author`

Muốn biết mỗi tác giả có bao nhiêu truyện:

```sql
SELECT
    author,
    COUNT(*) AS total_novels
FROM novels
GROUP BY author;
```

Ví dụ:

```text
author          total_novels
--------------  ------------
Nhĩ Căn         5
Thần Đông       7
Đường Gia Tam   3
```

---

# 11. `GROUP BY novel_id`

Đây là pattern **rất quan trọng** đối với database truyện.

Giả sử:

```text
chapters

id | novel_id | chapter_number
---+----------+---------------
1  | 10       | 1
2  | 10       | 2
3  | 10       | 3
4  | 20       | 1
5  | 20       | 2
6  | 30       | 1
```

Muốn biết mỗi novel có bao nhiêu chapter:

```sql
SELECT
    novel_id,
    COUNT(*) AS chapter_count
FROM chapters
GROUP BY novel_id;
```

Kết quả:

```text
novel_id    chapter_count
----------  -------------
10          3
20          2
30          1
```

Đây là một query bạn sẽ sử dụng rất nhiều trong app crawler.

---

# 12. `GROUP BY` nhiều column

Ta không chỉ group theo một column.

Ví dụ:

```text
source | status
-------+----------
site_a | ongoing
site_a | ongoing
site_a | completed
site_b | ongoing
site_b | ongoing
site_b | completed
```

Ta có thể:

```sql
SELECT
    source,
    status,
    COUNT(*) AS total
FROM novels
GROUP BY source, status;
```

Kết quả:

```text
source   status       total
-------  -----------  -----
site_a   completed    1
site_a   ongoing      2
site_b   completed    1
site_b   ongoing      2
```

Tư duy:

```text
GROUP BY source, status
```

nghĩa là nhóm theo **tổ hợp**:

```text
(site_a, ongoing)
(site_a, completed)
(site_b, ongoing)
(site_b, completed)
```

---

# 13. `WHERE` + `GROUP BY`

Đây là điểm cực kỳ quan trọng.

Giả sử ta chỉ muốn thống kê những novel:

```text
status = ongoing
```

trước khi group.

Ta viết:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source;
```

Logic:

```text
FROM
 ↓
WHERE
 ↓
GROUP BY
 ↓
COUNT
```

Tức là:

```text
Tất cả novels
      ↓
lọc ongoing
      ↓
chia theo source
      ↓
đếm từng nhóm
```

---

# 14. Thứ tự tư duy của SQL

Ví dụ:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source;
```

Đừng chỉ đọc từ trên xuống.

Hãy tư duy:

```text
FROM
 ↓
lấy bảng novels

WHERE
 ↓
lọc ongoing

GROUP BY
 ↓
chia thành từng source

COUNT
 ↓
đếm từng nhóm

SELECT
 ↓
trả source + total
```

Đây là tư duy SQL rất quan trọng.

---

# 15. `GROUP BY` + `ORDER BY`

Ta có thể sắp xếp kết quả sau khi group.

Ví dụ:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
GROUP BY source
ORDER BY total DESC;
```

Kết quả:

```text
source    total
--------  -----
site_a    120
site_b    85
site_c    43
```

Rất phù hợp với dashboard:

> Website nào có nhiều truyện nhất?

---

# 16. `GROUP BY` + `LIMIT`

Ví dụ:

> Top 5 tác giả có nhiều truyện nhất.

```sql
SELECT
    author,
    COUNT(*) AS total
FROM novels
GROUP BY author
ORDER BY total DESC
LIMIT 5;
```

Pattern:

```text
GROUP BY
   ↓
COUNT
   ↓
ORDER BY DESC
   ↓
LIMIT
```

---

# 17. Quy tắc cực kỳ quan trọng của `GROUP BY`

Khi dùng:

```sql
GROUP BY status
```

thì những column xuất hiện trong `SELECT` thường phải thuộc một trong hai nhóm:

### Nhóm 1 — Có trong GROUP BY

```sql
SELECT status
FROM novels
GROUP BY status;
```

OK.

### Nhóm 2 — Được aggregate

```sql
SELECT
    status,
    COUNT(*)
FROM novels
GROUP BY status;
```

OK.

---

## Ví dụ không nên viết

```sql
SELECT
    status,
    title,
    COUNT(*)
FROM novels
GROUP BY status;
```

Vấn đề:

```text
status → group
title  → không group
COUNT  → aggregate
```

Một nhóm `ongoing` có thể có rất nhiều `title`.

Vậy SQL phải chọn title nào?

```text
Tiên Nghịch?
Linh Vũ Thiên Hạ?
Test Novel?
```

Không có ý nghĩa rõ ràng.

**Quy tắc thực hành:**

> Nếu một column không nằm trong `GROUP BY`, hãy cân nhắc xem nó có cần được aggregate hay không.

---

# 18. `GROUP BY` không làm thay đổi dữ liệu

Một hiểu lầm phổ biến:

```sql
GROUP BY
```

không làm database thay đổi.

Nó chỉ tạo ra **result set** mới.

Ví dụ:

```sql
SELECT
    status,
    COUNT(*)
FROM novels
GROUP BY status;
```

Không hề:

```text
INSERT
UPDATE
DELETE
```

Database vẫn giữ nguyên.

---

# 19. So sánh `COUNT(*)` và `GROUP BY`

### Không GROUP BY

```sql
SELECT COUNT(*)
FROM novels;
```

Kết quả:

```text
5
```

Một con số cho toàn bảng.

### Có GROUP BY

```sql
SELECT
    status,
    COUNT(*)
FROM novels
GROUP BY status;
```

Kết quả:

```text
ongoing     3
completed   2
```

Nhiều kết quả — **mỗi group một kết quả**.

---

# 20. Python Repository

Trong kiến trúc của app crawler, ta có thể viết:

```python
class NovelRepository:

    def count_by_status(self) -> list[sqlite3.Row]:
        cursor = self._conn.execute(
            """
            SELECT
                status,
                COUNT(*) AS total
            FROM novels
            GROUP BY status
            ORDER BY total DESC
            """
        )

        return cursor.fetchall()
```

Sử dụng:

```python
rows = repo.count_by_status()

for row in rows:
    print(
        row["status"],
        row["total"],
    )
```

---

# 21. Query thống kê crawler

Ví dụ dashboard muốn hiển thị:

```text
Nguồn        Số truyện    Tổng chapter
-----------  -----------  -------------
site_a       120          245000
site_b       85           180000
site_c       43           92000
```

Có thể:

```sql
SELECT
    source,
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters
FROM novels
GROUP BY source
ORDER BY total_novels DESC;
```

Đây chính là cách SQL bắt đầu trở thành **công cụ phân tích dữ liệu**, chứ không chỉ CRUD.

---

# 22. Một pattern cần ghi nhớ

Khi gặp yêu cầu:

> “Thống kê theo X”

hãy nghĩ ngay:

```sql
GROUP BY X
```

Ví dụ:

| Yêu cầu                                | SQL                       |
| -------------------------------------- | ------------------------- |
| Bao nhiêu truyện theo status?          | `GROUP BY status`         |
| Bao nhiêu truyện theo source?          | `GROUP BY source`         |
| Bao nhiêu truyện theo author?          | `GROUP BY author`         |
| Bao nhiêu chapter theo novel?          | `GROUP BY novel_id`       |
| Bao nhiêu truyện theo source + status? | `GROUP BY source, status` |

---

# 23. Công thức SQL thực chiến

Một pattern rất đáng thuộc:

```sql
SELECT
    group_column,
    AGGREGATE(...)
FROM table
WHERE condition
GROUP BY group_column
ORDER BY ...
LIMIT ...;
```

Ví dụ:

```sql
SELECT
    source,
    COUNT(*) AS total
FROM novels
WHERE status = 'ongoing'
GROUP BY source
ORDER BY total DESC
LIMIT 5;
```

Đọc:

> Lấy các novel đang ongoing → nhóm theo source → đếm → sắp xếp giảm dần → lấy 5 source đầu.

---

# 24. Bài tập Buổi 10

Giả sử:

```text
novels

id | source | title | author | status | chapter_count
```

Hãy tự viết SQL cho các yêu cầu sau.

### Bài 1

Đếm số novel theo `status`.

```text
ongoing     ?
completed   ?
```

---

### Bài 2

Đếm số novel theo `source`.

---

### Bài 3

Tính tổng `chapter_count` theo `source`.

---

### Bài 4

Tính chapter trung bình theo `status`.

---

### Bài 5

Tìm source có nhiều novel nhất.

---

### Bài 6

Tìm 5 author có nhiều novel nhất.

---

### Bài 7

Chỉ xét:

```text
status = 'ongoing'
```

sau đó đếm số novel theo `source`.

---

### Bài 8 — quan trọng

Với:

```text
chapters

id
novel_id
chapter_number
title
content
```

hãy viết query:

> Mỗi novel có bao nhiêu chapter?

Kết quả:

```text
novel_id    total_chapters
---------   --------------
1           1200
2           850
3           430
```

---

# 25. Bài tập Python

Viết:

```python
def count_novels_by_status(
    conn: sqlite3.Connection,
) -> list[sqlite3.Row]:
    ...
```

Query phải trả về:

```text
status | total
```

Sau đó viết:

```python
def count_chapters_by_novel(
    conn: sqlite3.Connection,
) -> list[sqlite3.Row]:
    ...
```

trả về:

```text
novel_id | total_chapters
```

---

# 26. Mental Model của Buổi 10

Hãy nhớ sơ đồ này:

```text
                 GROUP BY
                    │
                    ▼
              Chia thành nhóm
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Group A   Group B   Group C
          │         │         │
          ▼         ▼         ▼
       COUNT      COUNT      COUNT
       SUM        SUM        SUM
       AVG        AVG        AVG
       MIN        MIN        MIN
       MAX        MAX        MAX
```

Và pipeline:

```text
FROM
  ↓
WHERE
  ↓
GROUP BY
  ↓
AGGREGATE
  ↓
ORDER BY
  ↓
LIMIT
```

---

## Roadmap hiện tại

```text
7   Operators                    ✅
8   AND / OR / NOT               ✅
9   COUNT / SUM / AVG / MIN/MAX  ✅
10  GROUP BY                     ← hôm nay
11  HAVING
12  DISTINCT
13  CASE WHEN
```

**Buổi 11** chúng ta sẽ học `HAVING` — phần rất dễ nhầm với `WHERE`.

Ví dụ:

```sql
WHERE
```

lọc **row trước khi GROUP BY**,

còn:

```sql
HAVING
```

lọc **group sau khi GROUP BY**.

Đây là một trong những điểm phân biệt quan trọng nhất của SQL.
