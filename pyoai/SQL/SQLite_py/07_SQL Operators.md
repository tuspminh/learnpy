# Buổi 7 — SQL Operators

Hôm nay chúng ta bắt đầu **Phần II — SQL thực chiến**.

Mục tiêu không chỉ là nhớ cú pháp, mà phải biết chọn operator nào để viết các truy vấn thực tế cho app crawl truyện.

```text
WHERE
  ↓
Operator
  ↓
lọc dữ liệu
```

Các operator hôm nay:

```sql
=
!=
>
<
>=
<=
BETWEEN
IN
LIKE
IS NULL
```

---

# 1. Chuẩn bị database

Giả sử bảng `novels`:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT NOT NULL DEFAULT 'ongoing',
    chapter_count INTEGER DEFAULT 0
);
```

Dữ liệu:

```text
id  title                  author              status       chapter_count
1   Tiên Nghịch             Nhĩ Căn             ongoing      2100
2   Phàm Nhân Tu Tiên       Vong Ngữ            completed    2450
3   Đấu Phá Thương Khung    Thiên Tằm Thổ Đậu   completed    1648
4   Linh Vũ Thiên Hạ        Vũ Phong            ongoing      3000
5   Test Novel              NULL                ongoing      10
```

---

# 2. `=` — bằng

Dùng để tìm giá trị bằng một giá trị cụ thể.

```sql
SELECT *
FROM novels
WHERE status = 'ongoing';
```

Kết quả:

```text
Tiên Nghịch
Linh Vũ Thiên Hạ
Test Novel
```

Với Python:

```python
cursor.execute(
    """
    SELECT id, title, status
    FROM novels
    WHERE status = ?
    """,
    ("ongoing",),
)
```

### Tìm novel theo ID

```sql
SELECT *
FROM novels
WHERE id = 3;
```

---

# 3. `!=` — khác

Ví dụ:

```sql
SELECT *
FROM novels
WHERE status != 'completed';
```

Nghĩa là:

> Lấy các novel có status khác `completed`.

Có thể viết:

```sql
WHERE status <> 'completed'
```

Trong SQL, `<>` cũng có nghĩa là **khác**.

---

# 4. `>` — lớn hơn

Ví dụ:

```sql
SELECT *
FROM novels
WHERE chapter_count > 2000;
```

Lấy những novel có hơn 2000 chapter.

Kết quả:

```text
Tiên Nghịch
Phàm Nhân Tu Tiên
Linh Vũ Thiên Hạ
```

---

# 5. `<` — nhỏ hơn

```sql
SELECT *
FROM novels
WHERE chapter_count < 100;
```

Kết quả:

```text
Test Novel
```

---

# 6. `>=` — lớn hơn hoặc bằng

```sql
SELECT *
FROM novels
WHERE chapter_count >= 2000;
```

Khác với:

```sql
chapter_count > 2000
```

Ví dụ:

```text
2000 >= 2000 → TRUE
2000 >  2000 → FALSE
```

---

# 7. `<=` — nhỏ hơn hoặc bằng

```sql
SELECT *
FROM novels
WHERE chapter_count <= 100;
```

---

# 8. So sánh số

Đây là nơi operator rất hữu ích trong app crawler.

Ví dụ:

> Tìm những truyện có ít nhất 1000 chapter.

```sql
SELECT id, title, chapter_count
FROM novels
WHERE chapter_count >= 1000;
```

Hoặc:

> Tìm truyện có từ 100 đến 500 chapter.

Có thể viết:

```sql
WHERE chapter_count >= 100
  AND chapter_count <= 500
```

Nhưng SQL có operator tốt hơn cho trường hợp này:

```sql
BETWEEN
```

---

# 9. `BETWEEN`

Cú pháp:

```sql
column BETWEEN value1 AND value2
```

Ví dụ:

```sql
SELECT *
FROM novels
WHERE chapter_count BETWEEN 100 AND 500;
```

Nó tương đương về logic với:

```sql
WHERE chapter_count >= 100
  AND chapter_count <= 500
```

### Điểm rất quan trọng

`BETWEEN` là **inclusive**.

Tức là:

```text
100 → được lấy
500 → được lấy
```

Có nghĩa:

```text
100 <= chapter_count <= 500
```

---

# 10. BETWEEN với Python

```python
cursor.execute(
    """
    SELECT id, title, chapter_count
    FROM novels
    WHERE chapter_count BETWEEN ? AND ?
    """,
    (100, 500),
)
```

Không viết:

```python
f"WHERE chapter_count BETWEEN {minimum} AND {maximum}"
```

Hãy tiếp tục sử dụng parameterized query.

---

# 11. `IN`

`IN` dùng khi muốn kiểm tra:

> Giá trị có nằm trong một tập giá trị hay không?

Ví dụ:

```sql
SELECT *
FROM novels
WHERE status IN ('ongoing', 'completed');
```

Ở ví dụ này tất nhiên gần như toàn bộ dữ liệu hợp lệ đều được lấy.

Một ví dụ hữu ích hơn:

```sql
SELECT *
FROM novels
WHERE id IN (1, 3, 5);
```

Nghĩa là:

```text
id = 1
OR id = 3
OR id = 5
```

---

# 12. IN vs nhiều OR

Hai câu này tương đương:

```sql
WHERE id = 1
   OR id = 3
   OR id = 5
```

và:

```sql
WHERE id IN (1, 3, 5)
```

`IN` thường dễ đọc hơn.

---

# 13. IN với Python

Đây là chỗ người mới rất dễ mắc lỗi.

Không làm:

```python
ids = [1, 3, 5]

cursor.execute(
    """
    SELECT *
    FROM novels
    WHERE id IN (?)
    """,
    (ids,),
)
```

`sqlite3` không tự biến list thành:

```sql
IN (1, 3, 5)
```

Cách đúng là tạo số lượng placeholder tương ứng:

```python
ids = [1, 3, 5]

placeholders = ",".join("?" for _ in ids)

sql = f"""
    SELECT id, title
    FROM novels
    WHERE id IN ({placeholders})
"""

cursor.execute(sql, ids)
```

SQL thực tế trở thành:

```sql
SELECT id, title
FROM novels
WHERE id IN (?, ?, ?)
```

và values:

```text
1, 3, 5
```

### Đây là một trường hợp đặc biệt

Ở đây ta dùng f-string để tạo **SQL structure**, không phải đưa dữ liệu người dùng trực tiếp vào SQL.

```python
f"IN ({placeholders})"
```

an toàn vì `placeholders` chỉ được tạo từ chuỗi `"?"`.

---

# 14. `NOT IN`

Có thể kết hợp với `NOT`:

```sql
SELECT *
FROM novels
WHERE id NOT IN (1, 3, 5);
```

Nghĩa:

> Lấy tất cả novel ngoại trừ ID 1, 3, 5.

Chúng ta sẽ học `NOT` kỹ hơn ở **Buổi 8**.

---

# 15. `LIKE`

`LIKE` dùng để tìm kiếm chuỗi theo pattern.

Ví dụ:

```sql
SELECT *
FROM novels
WHERE title LIKE '%Tiên%';
```

Tìm các title chứa:

```text
Tiên
```

---

# 16. Hai wildcard quan trọng

SQLite `LIKE` có hai wildcard thường dùng:

### `%`

Đại diện cho:

> zero hoặc nhiều ký tự

Ví dụ:

```sql
LIKE '%Tiên%'
```

Có thể match:

```text
Tiên Nghịch
Phàm Nhân Tu Tiên
Tiên Hiệp ...
```

---

### `_`

Đại diện cho:

> đúng một ký tự

Ví dụ:

```sql
LIKE 'Tiên _ghịch'
```

có thể match một chuỗi có đúng một ký tự ở vị trí `_`.

---

# 17. Các kiểu LIKE phổ biến

### Bắt đầu bằng

```sql
WHERE title LIKE 'Tiên%'
```

Ví dụ:

```text
Tiên Nghịch
Tiên Hiệp ...
```

---

### Kết thúc bằng

```sql
WHERE title LIKE '%Tu Tiên'
```

---

### Chứa

```sql
WHERE title LIKE '%Tiên%'
```

Đây là pattern rất hay dùng cho search box.

---

# 18. LIKE với Python

```python
keyword = "Tiên"

cursor.execute(
    """
    SELECT id, title
    FROM novels
    WHERE title LIKE ?
    """,
    (f"%{keyword}%",),
)
```

Ở đây:

```python
f"%{keyword}%"
```

được tạo **trước khi truyền vào parameter**.

SQL vẫn là:

```sql
WHERE title LIKE ?
```

Đây là cách tốt.

---

# 19. Search nhiều column

Ví dụ người dùng nhập:

```text
tiên
```

Muốn tìm trong:

```text
title
author
```

Ta có thể:

```sql
SELECT id, title, author
FROM novels
WHERE title LIKE ?
   OR author LIKE ?;
```

Python:

```python
keyword = "%tiên%"

cursor.execute(
    """
    SELECT id, title, author
    FROM novels
    WHERE title LIKE ?
       OR author LIKE ?
    """,
    (keyword, keyword),
)
```

`OR` chúng ta sẽ học sâu hơn ở Buổi 8.

---

# 20. `IS NULL`

Đây là một operator cực kỳ quan trọng.

Giả sử:

```text
id  title              author
1   Tiên Nghịch         Nhĩ Căn
2   Test Novel          NULL
```

Muốn tìm novel chưa có author:

```sql
SELECT *
FROM novels
WHERE author IS NULL;
```

---

# 21. Không được viết `= NULL`

Sai:

```sql
WHERE author = NULL;
```

Sai về logic SQL.

Đúng:

```sql
WHERE author IS NULL;
```

Tương tự:

```sql
WHERE author IS NOT NULL;
```

---

# 22. Tại sao NULL đặc biệt?

`NULL` không có nghĩa:

```text
""
```

và cũng không có nghĩa:

```text
0
```

Nó có nghĩa gần với:

> Không có giá trị / unknown / missing value.

Ví dụ:

```text
author = NULL
```

không phải là một chuỗi rỗng.

Ta có:

```text
NULL
""
0
```

là ba khái niệm khác nhau.

---

# 23. `IS NULL` trong app crawl

Điều này rất thực tế.

Crawler có thể lấy được:

```text
title = "Tiên Nghịch"
author = NULL
```

Sau này crawler bổ sung metadata.

Ta có thể tìm:

```sql
SELECT id, title
FROM novels
WHERE author IS NULL;
```

Sau đó crawl lại metadata.

---

# 24. Tổng hợp Operators

| Operator      | Ý nghĩa           |
| ------------- | ----------------- |
| `=`           | bằng              |
| `!=`          | khác              |
| `<>`          | khác              |
| `>`           | lớn hơn           |
| `<`           | nhỏ hơn           |
| `>=`          | lớn hơn hoặc bằng |
| `<=`          | nhỏ hơn hoặc bằng |
| `BETWEEN`     | nằm trong khoảng  |
| `IN`          | thuộc tập giá trị |
| `LIKE`        | pattern matching  |
| `IS NULL`     | giá trị NULL      |
| `IS NOT NULL` | không NULL        |

---

# 25. Kết hợp với SELECT

Một query thực tế:

```sql
SELECT id, title, author, chapter_count
FROM novels
WHERE chapter_count >= 1000
ORDER BY chapter_count DESC
LIMIT 20;
```

Ta đang kết hợp kiến thức:

```text
SELECT
WHERE
>=
ORDER BY
DESC
LIMIT
```

Đây chính là lúc SQL bắt đầu trở thành công cụ thực chiến.

---

# 26. Một query thực tế cho Novel Repository

Ví dụ:

> Tìm các novel đang ongoing có ít nhất 500 chapter.

```sql
SELECT id, title, author, chapter_count
FROM novels
WHERE status = ?
  AND chapter_count >= ?
ORDER BY chapter_count DESC;
```

Python:

```python
cursor.execute(
    """
    SELECT id, title, author, chapter_count
    FROM novels
    WHERE status = ?
      AND chapter_count >= ?
    ORDER BY chapter_count DESC
    """,
    ("ongoing", 500),
)
```

---

# 27. Một query khác

> Tìm novel có title chứa "Tiên", chưa có author.

```sql
SELECT id, title, author
FROM novels
WHERE title LIKE ?
  AND author IS NULL;
```

Python:

```python
cursor.execute(
    """
    SELECT id, title, author
    FROM novels
    WHERE title LIKE ?
      AND author IS NULL
    """,
    ("%Tiên%",),
)
```

---

# 28. Một lỗi rất quan trọng với NULL

Xét:

```sql
WHERE author != 'Nhĩ Căn'
```

Bạn có thể nghĩ nó lấy:

```text
author = NULL
```

nhưng SQL `NULL` có logic đặc biệt.

Điều kiện so sánh với `NULL` không đơn giản là `TRUE/FALSE`; nó liên quan đến **UNKNOWN**.

Vì vậy nếu muốn:

> author khác Nhĩ Căn **hoặc chưa có author**

hãy viết rõ:

```sql
WHERE author != 'Nhĩ Căn'
   OR author IS NULL;
```

Đây là một điểm rất quan trọng khi làm SQL thực tế.

---

# 29. Mental model

Khi gặp yêu cầu:

> "Tìm truyện..."

hãy chuyển câu tiếng Việt thành:

```text
Tìm cái gì?
    ↓
SELECT

Ở đâu?
    ↓
FROM

Điều kiện?
    ↓
WHERE

So sánh kiểu gì?
    ↓
operator
```

Ví dụ:

> Tìm truyện có 100–500 chapter.

```text
SELECT
    ↓
FROM novels
    ↓
WHERE chapter_count
    ↓
BETWEEN 100 AND 500
```

---

# 30. Bài tập Buổi 7

Giả sử:

```sql
novels(
    id,
    title,
    author,
    status,
    chapter_count
)
```

### Bài 1

Tìm novel có:

```text
id = 10
```

---

### Bài 2

Tìm novel có:

```text
chapter_count > 1000
```

---

### Bài 3

Tìm novel có:

```text
chapter_count từ 100 đến 500
```

Dùng `BETWEEN`.

---

### Bài 4

Tìm các novel có:

```text
id = 1, 5, 10, 20
```

Dùng `IN`.

---

### Bài 5

Tìm title chứa:

```text
"Tiên"
```

Dùng `LIKE`.

---

### Bài 6

Tìm các novel chưa có author.

Dùng:

```sql
IS NULL
```

---

### Bài 7 — Python

Viết:

```python
def search_novels(
    conn: sqlite3.Connection,
    keyword: str,
):
    ...
```

Tìm title chứa `keyword`.

Ví dụ:

```python
search_novels(conn, "Tiên")
```

phải tương đương với:

```sql
WHERE title LIKE '%Tiên%'
```

nhưng vẫn phải sử dụng **parameterized query**.

---

### Bài 8 — Repository thinking

Viết SQL cho yêu cầu:

> Lấy 20 novel đang `ongoing`, có từ 500 chapter trở lên, title chứa `"Tiên"`, sắp xếp theo số chapter giảm dần.

Mục tiêu:

```text
WHERE
    =
    >=
    LIKE

ORDER BY
DESC

LIMIT
```

---

# 31. Checklist cần nhớ

Sau Buổi 7, bạn cần phân biệt được:

```text
=           → bằng
!=          → khác
> <         → so sánh
>= <=       → so sánh có bằng
BETWEEN     → khoảng
IN          → một trong nhiều giá trị
LIKE        → tìm theo pattern
IS NULL     → kiểm tra NULL
```

Và đặc biệt:

```text
❌ author = NULL

✅ author IS NULL
```

```text
❌ SQL f-string với dữ liệu

✅ SQL + ?
```

---

## Vị trí của chúng ta trong roadmap

```text
Phần I — SQL Foundation
────────────────────────
1  SQL + SQLite + Python
2  CREATE TABLE
3  INSERT
4  SELECT
5  UPDATE
6  DELETE
       ↓
Phần II — SQL thực chiến
────────────────────────
7  Operators             ← HÔM NAY
8  Logical Operators
9  Aggregate
10 GROUP BY
11 HAVING
12 DISTINCT
13 CASE WHEN
```

**Buổi 8** chúng ta sẽ học `AND`, `OR`, `NOT` thật kỹ, đặc biệt là **độ ưu tiên của AND/OR và lỗi logic khi thiếu dấu ngoặc** — phần này cực kỳ quan trọng khi viết `WHERE` phức tạp.
