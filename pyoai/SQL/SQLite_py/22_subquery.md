# Buổi 22 — Subquery

Hôm nay chúng ta chuyển sang một cách tư duy mới trong SQL:

> **Một câu SQL có thể chứa một câu SQL khác bên trong nó.**

Đó chính là **Subquery**.

Với app crawler truyện, Subquery rất hữu ích cho các bài toán như:

* Novel có chapter hay chưa?
* Novel nào có ít nhất 100 chapter?
* Novel nào có số chapter lớn hơn trung bình?
* Novel nào thuộc một nhóm dữ liệu được tính từ query khác?

---

# 1. Subquery là gì?

Ví dụ đơn giản:

```sql
SELECT *
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Phần:

```sql
SELECT novel_id
FROM chapters
```

là **subquery**.

Query bên ngoài:

```sql
SELECT *
FROM novels
WHERE id IN (...)
```

gọi là **outer query**.

Cấu trúc:

```text
Outer Query
    │
    └── Subquery
            │
            └── kết quả
                  ↓
             Outer Query
```

---

# 2. Ví dụ thực tế đầu tiên

Giả sử:

```text
novels

1 | Tiên Nghịch
2 | Đấu Phá
3 | Phàm Nhân
```

```text
chapters

id | novel_id | chapter_number
--------------------------------
1  | 1        | 1
2  | 1        | 2
3  | 2        | 1
```

Muốn:

> Tìm những Novel **có chapter**.

Ta có thể viết:

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Subquery:

```sql
SELECT novel_id
FROM chapters;
```

trả về:

```text
1
1
2
```

Sau đó outer query:

```sql
WHERE id IN (1, 1, 2)
```

Kết quả:

```text
Tiên Nghịch
Đấu Phá
```

`Phàm Nhân` không có chapter nên không được chọn.

---

# 3. `IN (subquery)`

Đây là dạng Subquery đầu tiên bạn cần nhớ:

```sql
SELECT ...
FROM table_a
WHERE column_a IN (
    SELECT column_b
    FROM table_b
);
```

Ví dụ:

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Mental model:

```text
chapters
    ↓
SELECT novel_id
    ↓
[1, 2]
    ↓
novels.id IN [1, 2]
    ↓
Novel kết quả
```

---

# 4. `NOT IN`

Ngược lại:

> Tìm Novel **chưa từng có Chapter**.

Có thể viết:

```sql
SELECT
    id,
    title
FROM novels
WHERE id NOT IN (
    SELECT novel_id
    FROM chapters
);
```

Kết quả:

```text
Phàm Nhân
```

Tuy nhiên, có một vấn đề quan trọng với `NOT IN` khi subquery có thể chứa `NULL`.

Ví dụ:

```text
SELECT novel_id FROM chapters
```

trả về:

```text
1
2
NULL
```

thì `NOT IN` có thể cho kết quả bất ngờ do **SQL NULL/UNKNOWN**.

Vì vậy trong các bài toán kiểu:

> "Không tồn tại bản ghi liên quan"

thì sau này `NOT EXISTS` thường là lựa chọn an toàn và rõ nghĩa hơn.

Đây cũng chính là lý do Buổi 23 chúng ta học `EXISTS`.

---

# 5. Subquery trong `WHERE`

Đây là nơi phổ biến nhất.

Ví dụ:

> Tìm Novel có chapter số 100.

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
    WHERE chapter_number = 100
);
```

Đọc như tiếng Việt:

> Lấy Novel có `id` nằm trong danh sách `novel_id` của các chapter có `chapter_number = 100`.

---

# 6. Subquery có thể có điều kiện

Ví dụ:

> Tìm Novel có chapter từ 1000 trở lên.

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
    WHERE chapter_number >= 1000
);
```

Subquery:

```sql
SELECT novel_id
FROM chapters
WHERE chapter_number >= 1000;
```

Sau đó outer query lấy Novel tương ứng.

---

# 7. Subquery + DISTINCT

Nếu:

```text
Tiên Nghịch
    ├── chapter 1
    ├── chapter 2
    └── chapter 3
```

subquery:

```sql
SELECT novel_id
FROM chapters;
```

có thể trả:

```text
1
1
1
```

Ta có thể viết:

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT DISTINCT novel_id
    FROM chapters
);
```

Nhưng lưu ý:

```sql
IN (...)
```

không yêu cầu danh sách bên trong phải unique.

Do đó `DISTINCT` **không bắt buộc** trong trường hợp này.

Đây là một điểm nhỏ nhưng quan trọng:

> Đừng thêm `DISTINCT` chỉ vì thấy dữ liệu bị lặp; hãy hiểu operator đang làm gì.

---

# 8. Subquery trả về một giá trị

Subquery không nhất thiết trả về nhiều dòng.

Ví dụ:

> Tìm Novel có số chapter lớn hơn số chapter trung bình.

Trước tiên:

```sql
SELECT AVG(chapter_count)
FROM novels;
```

Giả sử kết quả:

```text
750
```

Ta có:

```sql
SELECT
    id,
    title,
    chapter_count
FROM novels
WHERE chapter_count > (
    SELECT AVG(chapter_count)
    FROM novels
);
```

Subquery:

```sql
SELECT AVG(chapter_count)
FROM novels
```

trả về **một giá trị**.

Outer query:

```sql
WHERE chapter_count > 750
```

---

# 9. Đây là Scalar Subquery

Subquery:

```sql
(
    SELECT AVG(chapter_count)
    FROM novels
)
```

trả về một giá trị duy nhất.

Đây thường được gọi là:

> **Scalar subquery**

Các hàm thường gặp:

```sql
AVG(...)
MAX(...)
MIN(...)
SUM(...)
COUNT(...)
```

Ví dụ:

```sql
SELECT
    id,
    title,
    chapter_count
FROM novels
WHERE chapter_count = (
    SELECT MAX(chapter_count)
    FROM novels
);
```

Ý nghĩa:

> Tìm Novel có số chapter lớn nhất.

---

# 10. Tìm Novel dài nhất

```sql
SELECT
    id,
    title,
    chapter_count
FROM novels
WHERE chapter_count = (
    SELECT MAX(chapter_count)
    FROM novels
);
```

Nếu dữ liệu:

```text
Tiên Nghịch | 2000
Đấu Phá     | 1800
Phàm Nhân   | 1200
```

Subquery:

```sql
SELECT MAX(chapter_count)
FROM novels;
```

→ `2000`

Outer query:

```sql
WHERE chapter_count = 2000
```

→ `Tiên Nghịch`.

---

# 11. Subquery trong `SELECT`

Subquery cũng có thể xuất hiện trong phần `SELECT`.

Ví dụ:

> Lấy Novel và tổng số Novel trong database.

```sql
SELECT
    id,
    title,
    (
        SELECT COUNT(*)
        FROM novels
    ) AS total_novels
FROM novels;
```

Kết quả:

```text
Tiên Nghịch | 10
Đấu Phá     | 10
Phàm Nhân   | 10
...
```

Mỗi dòng đều có:

```text
total_novels = 10
```

Đây là một **scalar subquery trong SELECT**.

---

# 12. Subquery trong `FROM`

Subquery cũng có thể trở thành một bảng tạm cho outer query.

Ví dụ:

```sql
SELECT *
FROM (
    SELECT
        id,
        title,
        chapter_count
    FROM novels
    WHERE chapter_count >= 1000
) AS long_novels;
```

Ở đây:

```sql
(
    SELECT ...
) AS long_novels
```

đóng vai trò như một bảng.

Mental model:

```text
Subquery
    ↓
temporary result
    ↓
AS long_novels
    ↓
Outer Query
```

---

# 13. Tại sao cần subquery trong FROM?

Ví dụ:

> Lọc trước một tập dữ liệu rồi tiếp tục xử lý nó.

```sql
SELECT
    long_novels.title,
    long_novels.chapter_count
FROM (
    SELECT
        id,
        title,
        chapter_count
    FROM novels
    WHERE chapter_count >= 1000
) AS long_novels
ORDER BY chapter_count DESC;
```

Subquery tạo ra tập:

```text
Novel có >= 1000 chapter
```

Outer query tiếp tục:

```text
ORDER BY
```

---

# 14. Subquery + GROUP BY

Ví dụ:

> Tìm các Novel có nhiều chapter hơn mức trung bình.

Nếu bảng `chapters` là nguồn dữ liệu thật:

```sql
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE n.id IN (
    SELECT
        c.novel_id
    FROM chapters AS c
    GROUP BY c.novel_id
    HAVING COUNT(*) > (
        SELECT AVG(chapter_count)
        FROM (
            SELECT
                novel_id,
                COUNT(*) AS chapter_count
            FROM chapters
            GROUP BY novel_id
        ) AS stats
    )
);
```

Query này bắt đầu khá phức tạp.

Điều quan trọng ở đây không phải học thuộc query.

Mà là nhận ra:

```text
Outer Query
    ↓
Subquery
    ↓
GROUP BY
    ↓
Aggregate
    ↓
Another Subquery
```

SQL có thể lồng nhiều tầng.

---

# 15. Nhưng đừng lạm dụng Subquery

Có bài toán viết bằng Subquery được:

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

nhưng cũng có thể viết bằng JOIN:

```sql
SELECT DISTINCT
    n.id,
    n.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id;
```

Hai cách có thể cho cùng tập Novel.

Vậy nên:

> **Subquery không phải lúc nào cũng tốt hơn JOIN.**

Hãy chọn cách thể hiện đúng ý nghĩa nghiệp vụ và dễ bảo trì.

---

# 16. JOIN vs Subquery

So sánh:

### JOIN

```sql
SELECT DISTINCT
    n.id,
    n.title
FROM novels n
INNER JOIN chapters c
    ON c.novel_id = n.id;
```

Ý tưởng:

```text
Novel
  ↓
JOIN
  ↓
Chapter
```

### Subquery

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Ý tưởng:

```text
Tìm tập novel_id từ chapters
              ↓
        lọc novels
```

Mental model:

```text
JOIN
→ "nối dữ liệu"

Subquery
→ "dùng kết quả của query này
   để quyết định query kia"
```

---

# 17. Một cách nhìn rất hay

Hãy đọc:

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
    WHERE chapter_number >= 100
);
```

thành tiếng Việt:

> **Hãy lấy Novel mà ID của nó thuộc tập ID của những Novel có chapter >= 100.**

Đây chính là bản chất của:

```sql
IN (subquery)
```

---

# 18. Subquery trong Python

Không có gì đặc biệt.

Python vẫn dùng parameterized query như bình thường:

```python
rows = conn.execute(
    """
    SELECT
        id,
        title
    FROM novels
    WHERE id IN (
        SELECT novel_id
        FROM chapters
        WHERE chapter_number >= ?
    )
    """,
    (100,),
).fetchall()
```

Quan trọng:

```python
(100,)
```

được truyền cho:

```sql
?
```

trong **subquery**.

---

# 19. Repository thực tế

Ví dụ:

```python
class NovelRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_with_chapters(self):
        return self._conn.execute(
            """
            SELECT
                id,
                title
            FROM novels
            WHERE id IN (
                SELECT novel_id
                FROM chapters
            )
            ORDER BY title
            """
        ).fetchall()

    def list_with_large_chapters(
        self,
        min_chapter: int,
    ):
        return self._conn.execute(
            """
            SELECT
                id,
                title
            FROM novels
            WHERE id IN (
                SELECT novel_id
                FROM chapters
                WHERE chapter_number >= ?
            )
            ORDER BY title
            """,
            (min_chapter,),
        ).fetchall()
```

Application:

```python
novels = repo.list_with_large_chapters(1000)
```

Application không cần biết subquery.

---

# 20. Một pattern cực kỳ hữu ích

### Parent có child

```sql
SELECT *
FROM parent
WHERE id IN (
    SELECT parent_id
    FROM child
);
```

### Parent không có child

```sql
SELECT *
FROM parent
WHERE id NOT IN (
    SELECT parent_id
    FROM child
);
```

Nhưng nhớ:

```text
NOT IN + NULL
```

có thể gây vấn đề.

Sau này:

```text
NOT EXISTS
```

thường là cách tốt hơn.

---

# 21. Subquery + ORDER BY + LIMIT

Ví dụ:

> Tìm Novel có chapter_number lớn nhất.

Có thể viết:

```sql
SELECT
    id,
    title
FROM novels
WHERE id = (
    SELECT novel_id
    FROM chapters
    ORDER BY chapter_number DESC
    LIMIT 1
);
```

Subquery:

```sql
SELECT novel_id
FROM chapters
ORDER BY chapter_number DESC
LIMIT 1
```

trả về:

```text
novel_id = 1
```

Outer query:

```sql
WHERE id = 1
```

---

# 22. Một điểm rất quan trọng: Subquery phải đúng "shape"

Khi dùng:

```sql
WHERE id = (
    SELECT ...
)
```

subquery phải trả về **một giá trị phù hợp**.

Ví dụ:

```sql
WHERE id = (
    SELECT novel_id
    FROM chapters
);
```

Nếu có nhiều chapter, subquery có nhiều dòng.

Đây là cách dùng không phù hợp cho toán tử `=`.

Nếu muốn nhiều giá trị:

```sql
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Mental model:

```text
=
→ một giá trị

IN
→ một tập giá trị
```

Đây là điểm cực kỳ quan trọng.

---

# 23. Các dạng Subquery cần nhớ

| Vị trí    | Ví dụ                        |
| --------- | ---------------------------- |
| `WHERE`   | `WHERE id IN (SELECT ...)`   |
| `WHERE =` | `WHERE x = (SELECT ...)`     |
| `SELECT`  | `SELECT (SELECT COUNT(...))` |
| `FROM`    | `FROM (SELECT ...) AS x`     |

Trong giai đoạn hiện tại, tập trung mạnh nhất vào:

```text
WHERE ... IN (subquery)
```

và:

```text
WHERE ... = (scalar subquery)
```

---

# 24. So sánh 3 cách

Một bài toán:

> Novel nào có Chapter?

### Cách 1 — JOIN

```sql
SELECT DISTINCT
    n.id,
    n.title
FROM novels n
INNER JOIN chapters c
    ON c.novel_id = n.id;
```

### Cách 2 — IN

```sql
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

### Cách 3 — EXISTS

```sql
SELECT
    n.id,
    n.title
FROM novels n
WHERE EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
);
```

Cách thứ ba chính là bài học kế tiếp.

```text
JOIN
   ↓
IN
   ↓
EXISTS
```

Bạn sẽ thấy `EXISTS` đặc biệt phù hợp với câu hỏi:

> **Có tồn tại bản ghi liên quan hay không?**

---

# 25. Bài tập Buổi 22

Dùng:

```text
novels
chapters
tags
novel_tags
```

### Bài 1

Tìm tất cả Novel có ít nhất một Chapter bằng:

```text
IN + subquery
```

---

### Bài 2

Tìm Novel có chapter:

```text
>= 500
```

Dùng:

```sql
WHERE id IN (
    SELECT ...
)
```

---

### Bài 3

Tìm Novel có chapter number lớn nhất.

Gợi ý:

```sql
WHERE id = (
    SELECT ...
    ORDER BY ...
    LIMIT 1
)
```

---

### Bài 4

Tìm Novel có `chapter_count` lớn hơn trung bình.

Dùng scalar subquery:

```sql
WHERE chapter_count > (
    SELECT AVG(...)
    FROM ...
)
```

---

### Bài 5

Viết query lấy:

```text
id
title
total_novels
```

trong đó `total_novels` là tổng số Novel trong database.

Gợi ý:

```sql
SELECT
    ...,
    (
        SELECT COUNT(*)
        FROM novels
    ) AS total_novels
FROM novels;
```

---

### Bài 6 — So sánh

Viết hai query cùng tìm:

> Novel có Chapter.

Một dùng:

```text
INNER JOIN
```

một dùng:

```text
IN + Subquery
```

Sau đó giải thích sự khác nhau về tư duy của hai cách.

---

### Bài 7 — Quan trọng

Giải thích tại sao:

```sql
WHERE id = (
    SELECT novel_id
    FROM chapters
);
```

không phù hợp khi subquery trả về nhiều dòng, trong khi:

```sql
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

lại phù hợp.

---

# 26. Chốt Buổi 22

Bạn cần nắm chắc 4 pattern:

### Một giá trị

```sql
WHERE x = (
    SELECT ...
)
```

### Nhiều giá trị

```sql
WHERE x IN (
    SELECT ...
)
```

### Không thuộc tập

```sql
WHERE x NOT IN (
    SELECT ...
)
```

nhưng cần cảnh giác với `NULL`.

### Subquery trong SELECT

```sql
SELECT
    x,
    (
        SELECT COUNT(*)
        FROM ...
    ) AS total
FROM ...;
```

Và mental model quan trọng nhất:

```text
                 Subquery
                    ↓
             tạo ra kết quả
                    ↓
              Outer Query
                    ↓
              sử dụng kết quả
```

---

## Roadmap

```text
18 JOIN                  ✅
19 INNER JOIN             ✅
20 LEFT JOIN              ✅
21 JOIN nhiều bảng        ✅
22 Subquery               ✅
23 EXISTS                 ← tiếp theo
```

**Buổi 23 — EXISTS** sẽ rất đáng học vì nó giải quyết trực tiếp câu hỏi kiểu:

```sql
SELECT n.*
FROM novels n
WHERE EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
);
```

Từ đó bạn sẽ hiểu sâu sự khác nhau giữa **`JOIN` vs `IN` vs `EXISTS`**, một kiến thức rất quan trọng khi viết SQL cho Repository.
