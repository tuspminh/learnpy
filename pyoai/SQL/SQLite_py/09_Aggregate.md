# Buổi 9 — Aggregate Functions

Hôm nay chúng ta chuyển sang một cách tư duy mới.

Các buổi trước chủ yếu hỏi:

> **“Lấy những row nào?”**

Ví dụ:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing';
```

Aggregate lại hỏi:

> **“Tập dữ liệu này có bao nhiêu? Tổng bao nhiêu? Trung bình bao nhiêu? Lớn nhất/nhỏ nhất là bao nhiêu?”**

5 hàm quan trọng:

```sql
COUNT()
SUM()
AVG()
MIN()
MAX()
```

---

# 1. Chuẩn bị dữ liệu

Giả sử:

```text
novels
------------------------------------------------
id   title                  status       chapters
1    Tiên Nghịch             ongoing      2100
2    Phàm Nhân Tu Tiên       completed    2450
3    Đấu Phá Thương Khung    completed    1648
4    Linh Vũ Thiên Hạ        ongoing      3000
5    Test Novel              ongoing      10
```

---

# 2. COUNT() — đếm

Cơ bản nhất:

```sql
SELECT COUNT(*)
FROM novels;
```

Kết quả:

```text
5
```

Nghĩa:

> Có 5 row trong `novels`.

---

# 3. COUNT(*) vs COUNT(column)

Đây là điểm rất quan trọng.

```sql
SELECT COUNT(*)
FROM novels;
```

→ đếm **row**.

Trong khi:

```sql
SELECT COUNT(author)
FROM novels;
```

→ đếm các row có `author` **không phải NULL**.

Ví dụ:

```text
id   author
1    Nhĩ Căn
2    Vong Ngữ
3    NULL
4    Vũ Phong
5    NULL
```

```sql
COUNT(*)
```

→ `5`

Nhưng:

```sql
COUNT(author)
```

→ `3`

---

# 4. Quy tắc nhớ COUNT

```text
COUNT(*)
    ↓
đếm row

COUNT(column)
    ↓
đếm giá trị không NULL
```

Đây là khác biệt cực kỳ quan trọng khi database có nhiều `NULL`.

---

# 5. COUNT với WHERE

Ví dụ:

> Có bao nhiêu novel đang ongoing?

```sql
SELECT COUNT(*)
FROM novels
WHERE status = 'ongoing';
```

Kết quả:

```text
3
```

Python:

```python
cursor.execute(
    """
    SELECT COUNT(*)
    FROM novels
    WHERE status = ?
    """,
    ("ongoing",),
)

count = cursor.fetchone()[0]
print(count)
```

---

# 6. COUNT trong app crawl truyện

Ví dụ:

> Có bao nhiêu novel đã crawl?

```sql
SELECT COUNT(*)
FROM novels
WHERE status = 'completed';
```

Hoặc:

> Có bao nhiêu chapter?

```sql
SELECT COUNT(*)
FROM chapters;
```

Đây chính là dữ liệu cho dashboard:

```text
Crawler Dashboard

Novel:    1,250
Chapter:  125,430
Ongoing:    720
Completed:  530
```

---

# 7. SUM() — tính tổng

`SUM()` cộng các giá trị số.

Ví dụ:

```sql
SELECT SUM(chapter_count)
FROM novels;
```

Với dữ liệu:

```text
2100
2450
1648
3000
10
```

tổng là:

```text
9208
```

---

# 8. SUM với WHERE

Ví dụ:

> Tổng số chapter của các novel đang ongoing.

```sql
SELECT SUM(chapter_count)
FROM novels
WHERE status = 'ongoing';
```

Tính:

```text
2100 + 3000 + 10
```

→ `5110`

---

# 9. SUM trong app crawler

Ví dụ dashboard:

```text
Total novels:        1,250
Total chapters:    125,430
```

SQL:

```sql
SELECT SUM(chapter_count)
FROM novels;
```

Tuy nhiên trong hệ thống thực tế, nếu `chapter_count` được lưu trong `novels`, bạn phải đảm bảo nó luôn đồng bộ với bảng `chapters`.

Đây là một vấn đề **data consistency** mà sau này chúng ta sẽ gặp khi thiết kế Repository/UoW.

---

# 10. AVG() — trung bình

Ví dụ:

```sql
SELECT AVG(chapter_count)
FROM novels;
```

Nếu có:

```text
2100
2450
1648
3000
10
```

thì SQL tính trung bình:

```text
(2100 + 2450 + 1648 + 3000 + 10) / 5
```

≈

```text
1841.6
```

---

# 11. AVG và NULL

Giả sử:

```text
chapter_count
-------------
100
200
NULL
300
```

```sql
SELECT AVG(chapter_count)
FROM novels;
```

Không phải:

```text
(100 + 200 + 0 + 300) / 4
```

mà NULL được **bỏ qua** trong phép aggregate này.

Tức là:

```text
(100 + 200 + 300) / 3
```

→ `200`

Đây là lý do phải hiểu rõ `NULL`.

---

# 12. MIN() — giá trị nhỏ nhất

```sql
SELECT MIN(chapter_count)
FROM novels;
```

Kết quả:

```text
10
```

Ví dụ:

> Novel nào có số chapter thấp nhất?

Trước tiên:

```sql
SELECT MIN(chapter_count)
FROM novels;
```

Sau đó có thể tìm row:

```sql
SELECT id, title, chapter_count
FROM novels
WHERE chapter_count = (
    SELECT MIN(chapter_count)
    FROM novels
);
```

Ở đây chúng ta vừa chạm tới **subquery**.

Chúng ta sẽ học kỹ hơn ở phần Relationships/Advanced SQL.

---

# 13. MAX() — giá trị lớn nhất

```sql
SELECT MAX(chapter_count)
FROM novels;
```

Kết quả:

```text
3000
```

Muốn tìm novel có nhiều chapter nhất:

```sql
SELECT id, title, chapter_count
FROM novels
WHERE chapter_count = (
    SELECT MAX(chapter_count)
    FROM novels
);
```

---

# 14. 5 Aggregate Functions

Hãy ghi nhớ bảng này:

| Function  | Ý nghĩa    |
| --------- | ---------- |
| `COUNT()` | Đếm        |
| `SUM()`   | Tổng       |
| `AVG()`   | Trung bình |
| `MIN()`   | Nhỏ nhất   |
| `MAX()`   | Lớn nhất   |

Mental model:

```text
COUNT → bao nhiêu?
SUM   → tổng bao nhiêu?
AVG   → trung bình?
MIN   → nhỏ nhất?
MAX   → lớn nhất?
```

---

# 15. Có thể dùng nhiều Aggregate trong một query

Ví dụ:

```sql
SELECT
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters,
    AVG(chapter_count) AS avg_chapters,
    MIN(chapter_count) AS min_chapters,
    MAX(chapter_count) AS max_chapters
FROM novels;
```

Kết quả có thể là:

```text
total_novels | total_chapters | avg_chapters | min_chapters | max_chapters
5            | 9208           | 1841.6       | 10           | 3000
```

Đây là một query cực kỳ hữu ích cho dashboard.

---

# 16. `AS` — đặt tên kết quả

Thay vì:

```sql
SELECT COUNT(*)
FROM novels;
```

ta có:

```sql
SELECT COUNT(*) AS total_novels
FROM novels;
```

Kết quả:

```text
total_novels
------------
5
```

Với nhiều aggregate:

```sql
SELECT
    COUNT(*) AS total_novels,
    SUM(chapter_count) AS total_chapters,
    AVG(chapter_count) AS average_chapters,
    MIN(chapter_count) AS minimum_chapters,
    MAX(chapter_count) AS maximum_chapters
FROM novels;
```

`AS` giúp code Python dễ đọc hơn.

---

# 17. Đọc kết quả bằng sqlite3.Row

Nếu sử dụng:

```python
conn.row_factory = sqlite3.Row
```

ta có:

```python
cursor.execute(
    """
    SELECT
        COUNT(*) AS total_novels,
        SUM(chapter_count) AS total_chapters,
        AVG(chapter_count) AS average_chapters,
        MIN(chapter_count) AS minimum_chapters,
        MAX(chapter_count) AS maximum_chapters
    FROM novels
    """
)

row = cursor.fetchone()

print(row["total_novels"])
print(row["total_chapters"])
print(row["average_chapters"])
print(row["minimum_chapters"])
print(row["maximum_chapters"])
```

Cách này rất phù hợp để sau này tạo **Query Model / Dashboard DTO**.

---

# 18. Aggregate + WHERE

Aggregate có thể kết hợp với `WHERE`.

Ví dụ:

> Thống kê các novel completed.

```sql
SELECT
    COUNT(*) AS total,
    SUM(chapter_count) AS total_chapters,
    AVG(chapter_count) AS average_chapters,
    MIN(chapter_count) AS min_chapters,
    MAX(chapter_count) AS max_chapters
FROM novels
WHERE status = 'completed';
```

Logic:

```text
FROM novels
     ↓
WHERE status = completed
     ↓
Aggregate
     ↓
COUNT / SUM / AVG / MIN / MAX
```

---

# 19. Aggregate không nhất thiết phải trả về nhiều row

Đây là điểm khác biệt lớn.

Query bình thường:

```sql
SELECT id, title
FROM novels;
```

có thể trả:

```text
1 Tiên Nghịch
2 Phàm Nhân Tu Tiên
3 Đấu Phá Thương Khung
...
```

Nhưng:

```sql
SELECT COUNT(*)
FROM novels;
```

trả:

```text
5
```

Một query aggregate không có `GROUP BY` thường trả về **một row kết quả**.

---

# 20. Aggregate + Python

Ví dụ function:

```python
def count_novels(
    conn: sqlite3.Connection,
) -> int:

    cursor = conn.execute(
        """
        SELECT COUNT(*)
        FROM novels
        """
    )

    return cursor.fetchone()[0]
```

Sử dụng:

```python
total = count_novels(conn)

print(total)
```

---

# 21. Repository Query

Trong kiến trúc Repository, đây có thể là:

```python
class NovelRepository:

    def count(self) -> int:
        cursor = self._conn.execute(
            """
            SELECT COUNT(*)
            FROM novels
            """
        )

        return cursor.fetchone()[0]
```

Application:

```python
total = novel_repository.count()
```

Application không cần biết:

```sql
SELECT COUNT(*)
```

được viết như thế nào.

---

# 22. Aggregate cho Dashboard

Một Query Repository rất thực tế:

```python
def get_statistics(self):
    cursor = self._conn.execute(
        """
        SELECT
            COUNT(*) AS total_novels,
            SUM(chapter_count) AS total_chapters,
            AVG(chapter_count) AS average_chapters,
            MIN(chapter_count) AS min_chapters,
            MAX(chapter_count) AS max_chapters
        FROM novels
        """
    )

    return cursor.fetchone()
```

Application:

```python
stats = repository.get_statistics()

print(stats["total_novels"])
print(stats["total_chapters"])
```

Đây chính là bước đầu để sau này xây:

```text
Crawler Dashboard
────────────────────────
Novels
Chapters
Average
Largest novel
Smallest novel
```

---

# 23. Một vấn đề quan trọng: Aggregate với bảng rỗng

Giả sử:

```text
novels = empty
```

### COUNT

```sql
SELECT COUNT(*)
FROM novels;
```

→ `0`

### SUM

```sql
SELECT SUM(chapter_count)
FROM novels;
```

→ có thể là `NULL`

### AVG

```sql
SELECT AVG(chapter_count)
FROM novels;
```

→ `NULL`

### MIN / MAX

→ `NULL`

Điều này rất quan trọng trong Python.

Không nên mặc định:

```python
total = row["total_chapters"] + 1
```

nếu `total_chapters` có thể là `None`.

---

# 24. `COALESCE()` xử lý NULL

Ví dụ:

```sql
SELECT COALESCE(SUM(chapter_count), 0)
FROM novels;
```

Nếu không có dữ liệu:

```text
SUM → NULL
COALESCE → 0
```

Có thể đặt alias:

```sql
SELECT
    COUNT(*) AS total_novels,
    COALESCE(SUM(chapter_count), 0) AS total_chapters
FROM novels;
```

`COALESCE()` chúng ta sẽ học kỹ hơn sau, nhưng hiện tại chỉ cần nhớ:

```text
COALESCE(value, fallback)
```

---

# 25. Một lỗi tư duy quan trọng

Giả sử:

```sql
SELECT
    COUNT(*),
    title
FROM novels;
```

Bạn có thể nghĩ:

> "COUNT tất cả novel rồi lấy title."

Nhưng aggregate và non-aggregate column không nên được trộn tùy tiện như vậy.

Nếu muốn:

> mỗi status có bao nhiêu novel

thì đó không phải bài toán aggregate đơn thuần nữa.

Ta cần:

```text
GROUP BY
```

Ví dụ:

```sql
SELECT
    status,
    COUNT(*) AS total
FROM novels
GROUP BY status;
```

Đây chính là **Buổi 10**.

---

# 26. Aggregate + GROUP BY

Hãy nhìn trước một chút:

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
-------------------
ongoing      3
completed    2
```

Tức là:

```text
COUNT()
```

không chỉ dùng để thống kê toàn bộ bảng.

Nó có thể thống kê:

```text
COUNT theo status
COUNT theo source
COUNT theo author
COUNT theo novel
```

Đó là sức mạnh của:

```text
GROUP BY + Aggregate
```

---

# 27. Một ví dụ cực thực tế với chapters

Giả sử:

```text
chapters
-----------------------------------------
id  novel_id  chapter_number
1   10        1
2   10        2
3   10        3
4   20        1
5   20        2
```

Muốn biết novel `10` có bao nhiêu chapter:

```sql
SELECT COUNT(*)
FROM chapters
WHERE novel_id = ?;
```

Python:

```python
cursor.execute(
    """
    SELECT COUNT(*)
    FROM chapters
    WHERE novel_id = ?
    """,
    (10,),
)

count = cursor.fetchone()[0]
```

---

# 28. Aggregate + Repository cho Chapter

Ta có thể có:

```python
class ChapterRepository:

    def count_by_novel(
        self,
        novel_id: int,
    ) -> int:

        cursor = self._conn.execute(
            """
            SELECT COUNT(*)
            FROM chapters
            WHERE novel_id = ?
            """,
            (novel_id,),
        )

        return cursor.fetchone()[0]
```

Application:

```python
count = chapters.count_by_novel(novel_id)
```

Đây là một **query method**, khác với CRUD đơn thuần.

---

# 29. Aggregate và Query Model

Một ngày nào đó Dashboard cần:

```text
NovelStatistics

total_novels
total_chapters
average_chapters
max_chapters
min_chapters
```

Đây không nhất thiết phải là Domain Entity.

Nó có thể là:

```python
from dataclasses import dataclass


@dataclass
class NovelStatistics:
    total_novels: int
    total_chapters: int
    average_chapters: float | None
    min_chapters: int | None
    max_chapters: int | None
```

Repository:

```text
SQL
 ↓
Aggregate
 ↓
NovelStatistics
 ↓
Dashboard
```

Đây là kiến thức sẽ rất hữu ích khi chúng ta học **Query Model / CQRS** sau này.

---

# 30. Mental Model quan trọng

Hãy phân biệt:

### SELECT thông thường

```text
row → row → row → row
```

### Aggregate

```text
row
row
row
row
 ↓
COUNT / SUM / AVG / MIN / MAX
 ↓
summary
```

Ví dụ:

```text
100 novels
     ↓
COUNT()
     ↓
100
```

hoặc:

```text
100 novels
     ↓
SUM(chapter_count)
     ↓
125430
```

---

# 31. Bài tập Buổi 9

Giả sử:

```text
novels(
    id,
    title,
    author,
    status,
    chapter_count
)
```

### Bài 1

Đếm tổng số novel:

```sql
COUNT()
```

---

### Bài 2

Đếm số novel đang `ongoing`.

---

### Bài 3

Tính tổng số chapter của tất cả novel.

---

### Bài 4

Tính số chapter trung bình.

---

### Bài 5

Tìm số chapter nhỏ nhất và lớn nhất.

---

### Bài 6

Viết một query duy nhất trả về:

```text
total_novels
total_chapters
average_chapters
min_chapters
max_chapters
```

Sử dụng `AS`.

---

### Bài 7 — Python

Viết:

```python
def get_novel_statistics(
    conn: sqlite3.Connection,
):
    ...
```

Trả về:

```text
total_novels
total_chapters
average_chapters
min_chapters
max_chapters
```

Khuyến khích dùng:

```python
conn.row_factory = sqlite3.Row
```

để truy cập:

```python
row["total_novels"]
```

---

### Bài 8 — Chapter

Viết:

```python
def count_chapters(
    conn: sqlite3.Connection,
    novel_id: int,
) -> int:
    ...
```

Query phải đếm số chapter của một novel.

---

### Bài 9 — Tư duy

Giải thích sự khác nhau:

```sql
COUNT(*)
```

và:

```sql
COUNT(author)
```

đặc biệt khi `author` có `NULL`.

---

# 32. Tổng kết

Sau Buổi 9:

```text
COUNT()
   ↓
Có bao nhiêu?

SUM()
   ↓
Tổng bao nhiêu?

AVG()
   ↓
Trung bình?

MIN()
   ↓
Nhỏ nhất?

MAX()
   ↓
Lớn nhất?
```

Bạn cũng cần nhớ:

```text
COUNT(*)      → đếm row
COUNT(column) → đếm non-NULL
```

và:

```text
Aggregate
   ↓
thường tạo summary
   ↓
không còn đơn thuần lấy từng row
```

Roadmap hiện tại:

```text
Buổi 7  Operators
    ↓
Buổi 8  AND / OR / NOT
    ↓
Buổi 9  COUNT / SUM / AVG / MIN / MAX  ← HÔM NAY
    ↓
Buổi 10 GROUP BY
    ↓
Buổi 11 HAVING
    ↓
Buổi 12 DISTINCT
    ↓
Buổi 13 CASE WHEN
```

**Buổi 10 — `GROUP BY`** sẽ là bước rất quan trọng: chúng ta sẽ học cách biến `COUNT()` từ **“có bao nhiêu novel?”** thành **“mỗi source có bao nhiêu novel?”, “mỗi status có bao nhiêu novel?”, “mỗi novel có bao nhiêu chapter?”**.
