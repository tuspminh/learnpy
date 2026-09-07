# Buổi 13 — `CASE WHEN` trong SQL + SQLite + Python

Hôm nay chúng ta học:

```sql
CASE
    WHEN
    THEN
    ELSE
END
```

Đây là cơ chế **rẽ nhánh logic trong SQL**, tương tự như:

```python
if / elif / else
```

Nhưng thay vì xử lý từng object trong Python, ta có thể để **SQLite phân loại dữ liệu ngay trong query**.

---

# 1. `CASE WHEN` là gì?

Python:

```python
if chapter_count >= 2000:
    category = "long"
elif chapter_count >= 1000:
    category = "medium"
else:
    category = "short"
```

SQL:

```sql
CASE
    WHEN chapter_count >= 2000 THEN 'long'
    WHEN chapter_count >= 1000 THEN 'medium'
    ELSE 'short'
END
```

Mental model:

```text
CASE
  ↓
kiểm tra điều kiện
  ↓
WHEN ?
  ↓
THEN kết quả
  ↓
WHEN ?
  ↓
THEN kết quả
  ↓
ELSE
  ↓
END
```

---

# 2. Syntax cơ bản

```sql
CASE
    WHEN condition THEN result
    WHEN condition THEN result
    ELSE result
END
```

Ví dụ:

```sql
SELECT
    title,
    chapter_count,
    CASE
        WHEN chapter_count >= 2000 THEN 'long'
        WHEN chapter_count >= 1000 THEN 'medium'
        ELSE 'short'
    END AS category
FROM novels;
```

Kết quả:

```text
title                  chapter_count    category
---------------------  -------------    --------
Tiên Nghịch             2100             long
Phàm Nhân Tu Tiên       2450             long
Đấu Phá Thương Khung    1648             medium
Test Novel              10               short
```

---

# 3. `CASE` giống `if / elif / else`

So sánh:

### Python

```python
if status == "ongoing":
    label = "Đang cập nhật"
elif status == "completed":
    label = "Đã hoàn thành"
else:
    label = "Không xác định"
```

### SQL

```sql
CASE
    WHEN status = 'ongoing'
        THEN 'Đang cập nhật'

    WHEN status = 'completed'
        THEN 'Đã hoàn thành'

    ELSE 'Không xác định'
END
```

Có thể nhớ:

```text
Python                SQL
-------------------   ----------------
if                    WHEN
condition             condition
:                     THEN
elif                  WHEN
else                  ELSE
```

---

# 4. `CASE` không thay đổi database

Query:

```sql
SELECT
    title,
    CASE
        WHEN chapter_count >= 2000 THEN 'long'
        ELSE 'short'
    END AS category
FROM novels;
```

Không làm:

```text
UPDATE
INSERT
DELETE
```

Nó chỉ tạo ra một **giá trị tính toán trong result set**.

---

# 5. `CASE` tạo computed column

Ví dụ:

```sql
SELECT
    title,
    chapter_count,
    CASE
        WHEN chapter_count >= 2000 THEN 'long'
        WHEN chapter_count >= 1000 THEN 'medium'
        ELSE 'short'
    END AS length_category
FROM novels;
```

`length_category` không nhất thiết tồn tại trong bảng.

Nó là:

```text
computed column
```

SQLite tính nó khi query chạy.

---

# 6. Thứ tự `WHEN` rất quan trọng

Ví dụ:

```sql
CASE
    WHEN chapter_count >= 1000 THEN 'medium'
    WHEN chapter_count >= 2000 THEN 'long'
    ELSE 'short'
END
```

Sai logic.

Vì:

```text
2500 >= 1000
```

đã đúng.

SQLite sẽ chọn:

```text
medium
```

và không kiểm tra tiếp:

```text
chapter_count >= 2000
```

Do đó nên viết:

```sql
CASE
    WHEN chapter_count >= 2000 THEN 'long'
    WHEN chapter_count >= 1000 THEN 'medium'
    ELSE 'short'
END
```

Mental model:

> **`CASE` chọn nhánh `WHEN` đầu tiên thỏa điều kiện.**

---

# 7. `ELSE` có bắt buộc không?

Không.

Có thể:

```sql
CASE
    WHEN status = 'ongoing' THEN 'Đang đọc'
    WHEN status = 'completed' THEN 'Hoàn thành'
END
```

Nếu không có `WHEN` nào đúng, kết quả sẽ là:

```text
NULL
```

Tuy nhiên trong code thực tế, thường nên cân nhắc:

```sql
ELSE 'unknown'
```

để tránh kết quả bất ngờ.

---

# 8. `CASE` với status

Ví dụ:

```sql
SELECT
    title,
    status,
    CASE
        WHEN status = 'ongoing'
            THEN 'Đang cập nhật'

        WHEN status = 'completed'
            THEN 'Đã hoàn thành'

        ELSE 'Không xác định'
    END AS status_label
FROM novels;
```

Kết quả:

```text
title             status       status_label
----------------  -----------  -------------
Novel A           ongoing      Đang cập nhật
Novel B           completed    Đã hoàn thành
Novel C           ongoing      Đang cập nhật
```

Rất hữu ích khi UI cần hiển thị label thân thiện.

---

# 9. `CASE` với số

Ví dụ phân loại novel:

```sql
SELECT
    title,
    chapter_count,
    CASE
        WHEN chapter_count >= 2000 THEN 'long'
        WHEN chapter_count >= 1000 THEN 'medium'
        WHEN chapter_count >= 500 THEN 'short-medium'
        ELSE 'short'
    END AS length_category
FROM novels;
```

---

# 10. `CASE` với `NULL`

Đây là trường hợp rất thực tế.

Giả sử:

```text
author
------
Nhĩ Căn
NULL
Thần Đông
NULL
```

Ta có:

```sql
SELECT
    title,
    CASE
        WHEN author IS NULL THEN 'Unknown'
        ELSE author
    END AS author_name
FROM novels;
```

Kết quả:

```text
title       author_name
----------  -----------
Novel A     Nhĩ Căn
Novel B     Unknown
Novel C     Thần Đông
Novel D     Unknown
```

Nhớ:

```sql
IS NULL
```

chứ không:

```sql
= NULL
```

---

# 11. `CASE` với nhiều điều kiện

Ta có thể sử dụng:

```sql
AND
OR
```

Ví dụ:

> Novel ongoing và có hơn 2000 chapter → hot.

```sql
SELECT
    title,
    CASE
        WHEN status = 'ongoing'
             AND chapter_count >= 2000
            THEN 'hot'

        WHEN chapter_count >= 1000
            THEN 'popular'

        ELSE 'normal'
    END AS category
FROM novels;
```

---

# 12. `CASE` trong `ORDER BY`

Đây là kỹ thuật rất hữu ích.

Giả sử muốn sắp xếp:

```text
ongoing
completed
```

thay vì alphabet:

```text
completed
ongoing
```

Ta có thể:

```sql
SELECT
    title,
    status
FROM novels
ORDER BY
    CASE
        WHEN status = 'ongoing' THEN 1
        WHEN status = 'completed' THEN 2
        ELSE 3
    END;
```

Kết quả:

```text
ongoing
ongoing
ongoing
completed
completed
```

Tư duy:

```text
ongoing   → 1
completed → 2
unknown   → 3
```

Sau đó SQL sort theo số.

---

# 13. `CASE` trong `ORDER BY` cho crawler

Ví dụ dashboard muốn:

```text
1. Novel đang crawl
2. Novel pending
3. Novel completed
```

Có thể:

```sql
ORDER BY
    CASE status
        WHEN 'crawling' THEN 1
        WHEN 'pending' THEN 2
        WHEN 'completed' THEN 3
        ELSE 4
    END
```

Đây là một dạng `CASE` rất đáng nhớ.

---

# 14. Hai dạng `CASE`

Có **hai kiểu chính**.

## Dạng 1 — Searched CASE

Đây là dạng phổ biến nhất:

```sql
CASE
    WHEN condition THEN result
    WHEN condition THEN result
    ELSE result
END
```

Ví dụ:

```sql
CASE
    WHEN chapter_count >= 2000 THEN 'long'
    WHEN chapter_count >= 1000 THEN 'medium'
    ELSE 'short'
END
```

---

# 15. Dạng 2 — Simple CASE

Có thể viết ngắn hơn khi so sánh **một giá trị**.

```sql
CASE status
    WHEN 'ongoing' THEN 'Đang cập nhật'
    WHEN 'completed' THEN 'Đã hoàn thành'
    ELSE 'Unknown'
END
```

Tương đương:

```sql
CASE
    WHEN status = 'ongoing'
        THEN 'Đang cập nhật'

    WHEN status = 'completed'
        THEN 'Đã hoàn thành'

    ELSE 'Unknown'
END
```

---

# 16. Khi nào dùng Simple CASE?

Nếu logic là:

```text
column == value
```

thì simple CASE rất đẹp:

```sql
CASE status
    WHEN 'ongoing' THEN 'Đang cập nhật'
    WHEN 'completed' THEN 'Đã hoàn thành'
    ELSE 'Unknown'
END
```

Nếu điều kiện phức tạp:

```text
chapter_count >= 2000
AND status = 'ongoing'
```

thì dùng searched CASE:

```sql
CASE
    WHEN status = 'ongoing'
         AND chapter_count >= 2000
        THEN 'hot'
END
```

---

# 17. `CASE` + Aggregate

Đây là nơi `CASE` trở nên **rất mạnh**.

Ví dụ:

> Có bao nhiêu novel ongoing?

Ta đã biết:

```sql
SELECT COUNT(*)
FROM novels
WHERE status = 'ongoing';
```

Nhưng có thể dùng:

```sql
SELECT
    COUNT(
        CASE
            WHEN status = 'ongoing'
            THEN 1
        END
    ) AS ongoing_count
FROM novels;
```

Ý tưởng:

```text
ongoing   → 1
completed → NULL
```

`COUNT` bỏ qua `NULL`.

---

# 18. Conditional aggregation

Đây là thuật ngữ rất quan trọng:

```text
Conditional Aggregation
```

Ví dụ:

```sql
SELECT
    COUNT(*) AS total,
    COUNT(
        CASE
            WHEN status = 'ongoing'
            THEN 1
        END
    ) AS ongoing,
    COUNT(
        CASE
            WHEN status = 'completed'
            THEN 1
        END
    ) AS completed
FROM novels;
```

Kết quả:

```text
total    ongoing    completed
-----    -------    ---------
100      65         35
```

Một query có thể tạo cả dashboard summary.

---

# 19. Một cách viết khác với `SUM`

Ta cũng có:

```sql
SELECT
    SUM(
        CASE
            WHEN status = 'ongoing'
            THEN 1
            ELSE 0
        END
    ) AS ongoing_count
FROM novels;
```

Logic:

```text
ongoing    → 1
completed  → 0
```

Sau đó:

```text
SUM
```

lại.

Đây là pattern rất phổ biến.

---

# 20. Dashboard crawler

Ví dụ muốn một query trả về:

```text
total
ongoing
completed
long_novels
```

Có thể:

```sql
SELECT
    COUNT(*) AS total_novels,

    SUM(
        CASE
            WHEN status = 'ongoing'
            THEN 1
            ELSE 0
        END
    ) AS ongoing_novels,

    SUM(
        CASE
            WHEN status = 'completed'
            THEN 1
            ELSE 0
        END
    ) AS completed_novels,

    SUM(
        CASE
            WHEN chapter_count >= 2000
            THEN 1
            ELSE 0
        END
    ) AS long_novels

FROM novels;
```

Ví dụ:

```text
total_novels       500
ongoing_novels     320
completed_novels   180
long_novels        95
```

Đây là query rất phù hợp cho **Crawler Dashboard**.

---

# 21. `CASE` + `GROUP BY`

Ta có thể kết hợp:

```sql
SELECT
    source,
    SUM(
        CASE
            WHEN status = 'ongoing'
            THEN 1
            ELSE 0
        END
    ) AS ongoing_count
FROM novels
GROUP BY source;
```

Kết quả:

```text
source    ongoing_count
--------  -------------
site_a    80
site_b    45
site_c    20
```

---

# 22. Một ví dụ rất thực tế

Muốn thống kê:

```text
Mỗi source:
- tổng novel
- ongoing
- completed
```

Query:

```sql
SELECT
    source,

    COUNT(*) AS total_novels,

    SUM(
        CASE
            WHEN status = 'ongoing'
            THEN 1
            ELSE 0
        END
    ) AS ongoing_novels,

    SUM(
        CASE
            WHEN status = 'completed'
            THEN 1
            ELSE 0
        END
    ) AS completed_novels

FROM novels

GROUP BY source

ORDER BY total_novels DESC;
```

Đây là một query rất đáng lưu lại.

---

# 23. Python + `sqlite3.Row`

```python
rows = conn.execute(
    """
    SELECT
        source,
        COUNT(*) AS total_novels,

        SUM(
            CASE
                WHEN status = 'ongoing'
                THEN 1
                ELSE 0
            END
        ) AS ongoing_novels,

        SUM(
            CASE
                WHEN status = 'completed'
                THEN 1
                ELSE 0
            END
        ) AS completed_novels

    FROM novels

    GROUP BY source

    ORDER BY total_novels DESC
    """
).fetchall()
```

Sau đó:

```python
for row in rows:
    print(
        row["source"],
        row["total_novels"],
        row["ongoing_novels"],
        row["completed_novels"],
    )
```

---

# 24. Repository

Trong Repository:

```python
class NovelRepository:

    def get_source_statistics(
        self,
    ) -> list[sqlite3.Row]:

        cursor = self._conn.execute(
            """
            SELECT
                source,
                COUNT(*) AS total_novels,

                SUM(
                    CASE
                        WHEN status = 'ongoing'
                        THEN 1
                        ELSE 0
                    END
                ) AS ongoing_novels,

                SUM(
                    CASE
                        WHEN status = 'completed'
                        THEN 1
                        ELSE 0
                    END
                ) AS completed_novels

            FROM novels
            GROUP BY source

            ORDER BY total_novels DESC
            """
        )

        return cursor.fetchall()
```

Application/UI chỉ nhận:

```text
source
total_novels
ongoing_novels
completed_novels
```

---

# 25. `CASE` không phải lúc nào cũng cần thiết

Ví dụ:

> Đếm novel ongoing.

Có thể dùng:

```sql
SELECT COUNT(*)
FROM novels
WHERE status = 'ongoing';
```

Không cần:

```sql
CASE
```

`CASE` đặc biệt hữu ích khi muốn **nhiều điều kiện / nhiều thống kê trong cùng một query**.

Ví dụ:

```text
total
ongoing
completed
long
short
missing_author
```

---

# 26. `CASE` vs Python `if`

Nếu bạn đã lấy dữ liệu về Python:

```python
for novel in novels:
    if novel.chapter_count >= 2000:
        ...
```

thì Python xử lý.

Nhưng nếu mục tiêu là:

> Database hãy phân loại và thống kê dữ liệu.

thì có thể:

```sql
CASE
    WHEN ...
    THEN ...
END
```

Đặc biệt:

```text
GROUP BY
+
CASE
+
COUNT/SUM
```

là tổ hợp rất mạnh.

---

# 27. Mental Model của Buổi 13

Hãy nhớ:

```text
CASE
 │
 ├── WHEN condition
 │      ↓
 │    THEN result
 │
 ├── WHEN condition
 │      ↓
 │    THEN result
 │
 └── ELSE result
        ↓
       END
```

Tương đương:

```text
Python
────────────────────
if
elif
else

SQL
────────────────────
WHEN
WHEN
ELSE
```

---

# 28. Pattern quan trọng nhất

### Phân loại:

```sql
CASE
    WHEN condition THEN 'A'
    WHEN condition THEN 'B'
    ELSE 'C'
END
```

### Đếm có điều kiện:

```sql
SUM(
    CASE
        WHEN condition THEN 1
        ELSE 0
    END
)
```

### Group + conditional aggregation:

```sql
SELECT
    group_column,

    SUM(
        CASE
            WHEN condition THEN 1
            ELSE 0
        END
    ) AS total

FROM table

GROUP BY group_column;
```

Bạn nên thuộc pattern thứ ba.

---

# 29. Bài tập Buổi 13

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

Phân loại novel:

```text
>= 2000 → long
>= 1000 → medium
< 1000  → short
```

---

### Bài 2

Chuyển:

```text
ongoing
completed
```

thành:

```text
Đang cập nhật
Đã hoàn thành
```

---

### Bài 3

Nếu `author IS NULL` thì hiển thị:

```text
Unknown
```

---

### Bài 4

Sắp xếp novel theo thứ tự:

```text
ongoing
completed
```

bằng `CASE` trong `ORDER BY`.

---

### Bài 5

Một query trả về:

```text
total_novels
ongoing_novels
completed_novels
```

---

### Bài 6

Theo từng `source`, trả về:

```text
source
total_novels
ongoing_novels
completed_novels
```

Gợi ý:

```text
GROUP BY
+
SUM(CASE ...)
```

---

### Bài 7 — nâng cao

Theo từng source, tính:

```text
source
total_novels
long_novels
medium_novels
short_novels
```

Trong đó:

```text
long   >= 2000
medium >= 1000
short  < 1000
```

---

### Bài 8 — Python

Viết:

```python
def get_source_statistics(
    conn: sqlite3.Connection,
) -> list[sqlite3.Row]:
    ...
```

Trả về:

```text
source
total_novels
ongoing_novels
completed_novels
long_novels
```

---

# 30. Tổng kết Phần SQL Foundation

Đến đây bạn đã đi qua một chuỗi kiến thức rất quan trọng:

```text
SELECT
  ↓
WHERE
  ↓
Operators
  ↓
AND / OR / NOT
  ↓
Aggregate
  ↓
GROUP BY
  ↓
HAVING
  ↓
DISTINCT
  ↓
CASE WHEN
```

Đặc biệt hãy ghi nhớ 4 câu hỏi:

```text
"Row nào?"
    → WHERE

"Theo từng cái gì?"
    → GROUP BY

"Group nào đạt điều kiện?"
    → HAVING

"Phân loại theo điều kiện?"
    → CASE WHEN
```

Và một pattern cực kỳ quan trọng cho project crawler:

```sql
SELECT
    source,
    COUNT(*) AS total,
    SUM(
        CASE
            WHEN status = 'ongoing'
            THEN 1
            ELSE 0
        END
    ) AS ongoing
FROM novels
GROUP BY source;
```

Bạn sẽ gặp kiểu query này rất nhiều khi xây **dashboard thống kê crawler**.

---

## Roadmap tiếp theo

```text
7   Operators                    ✅
8   AND / OR / NOT               ✅
9   Aggregate                    ✅
10  GROUP BY                     ✅
11  HAVING                       ✅
12  DISTINCT                     ✅
13  CASE WHEN                    ✅

14  FOREIGN KEY
15  One-to-One
16  One-to-Many
17  Many-to-Many
18  JOIN
19  INNER JOIN
20  LEFT JOIN
21  JOIN nhiều bảng
22  Subquery
23  EXISTS
```

**Buổi 14** chúng ta sẽ chuyển sang một phần cực kỳ quan trọng của SQLite: **`FOREIGN KEY` và quan hệ giữa `novels` ↔ `chapters`**. Đây chính là bước đầu tiên để xây database truyện đúng cách thay vì chỉ có những bảng độc lập.
