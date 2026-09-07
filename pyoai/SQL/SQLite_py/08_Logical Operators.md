# Buổi 8 — Logical Operators: `AND`, `OR`, `NOT`

Hôm nay chúng ta học phần rất quan trọng của SQL:

```sql
AND
OR
NOT
```

Nếu Buổi 7 giúp bạn biết **từng điều kiện**, thì Buổi 8 giúp bạn **ghép nhiều điều kiện thành business rule**.

Đây là kỹ năng sẽ được sử dụng rất nhiều trong Repository của app crawl truyện.

---

# 1. `AND` — tất cả điều kiện phải đúng

Cú pháp:

```sql
WHERE condition1
  AND condition2
```

Ví dụ:

> Tìm truyện đang `ongoing` và có ít nhất 1000 chapter.

```sql
SELECT id, title, status, chapter_count
FROM novels
WHERE status = 'ongoing'
  AND chapter_count >= 1000;
```

Điều kiện:

```text
status = 'ongoing'
        AND
chapter_count >= 1000
```

Phải **đồng thời đúng cả hai**.

---

# 2. Hình dung bằng bảng chân trị

Với `AND`:

| A     | B     | A AND B |
| ----- | ----- | ------- |
| TRUE  | TRUE  | TRUE    |
| TRUE  | FALSE | FALSE   |
| FALSE | TRUE  | FALSE   |
| FALSE | FALSE | FALSE   |

Chỉ có:

```text
TRUE AND TRUE = TRUE
```

---

# 3. Ví dụ thực tế

Dữ liệu:

```text
id  title                  status       chapter_count
1   Tiên Nghịch             ongoing      2100
2   Phàm Nhân Tu Tiên       completed    2450
3   Đấu Phá Thương Khung    completed    1648
4   Linh Vũ Thiên Hạ        ongoing      3000
5   Test Novel              ongoing      10
```

Query:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing'
  AND chapter_count >= 2000;
```

Kết quả:

```text
Tiên Nghịch
Linh Vũ Thiên Hạ
```

---

# 4. `OR` — chỉ cần một điều kiện đúng

Cú pháp:

```sql
WHERE condition1
   OR condition2
```

Ví dụ:

> Tìm truyện `ongoing` hoặc có ít nhất 2000 chapter.

```sql
SELECT id, title, status, chapter_count
FROM novels
WHERE status = 'ongoing'
   OR chapter_count >= 2000;
```

Với `OR`, chỉ cần **một trong các điều kiện đúng**.

---

# 5. Bảng chân trị của OR

| A     | B     | A OR B |
| ----- | ----- | ------ |
| TRUE  | TRUE  | TRUE   |
| TRUE  | FALSE | TRUE   |
| FALSE | TRUE  | TRUE   |
| FALSE | FALSE | FALSE  |

Chỉ có:

```text
FALSE OR FALSE = FALSE
```

là false.

---

# 6. `AND` vs `OR`

Đây là điểm phải nhớ:

```text
AND → hẹp hơn
OR  → rộng hơn
```

Ví dụ:

```sql
WHERE status = 'ongoing'
  AND chapter_count >= 1000
```

→ phải thỏa **cả hai**.

Trong khi:

```sql
WHERE status = 'ongoing'
   OR chapter_count >= 1000
```

→ chỉ cần thỏa **một trong hai**.

---

# 7. Kết hợp `AND` và `OR`

Đây là nơi bắt đầu nguy hiểm.

Ví dụ:

> Tìm truyện đang ongoing và có ít nhất 1000 chapter, **hoặc** đã completed.

Ta có:

```sql
SELECT *
FROM novels
WHERE status = 'ongoing'
  AND chapter_count >= 1000
   OR status = 'completed';
```

Nhưng **đừng vội viết query như vậy**.

Hãy suy nghĩ business rule trước:

```text
(ongoing AND chapter_count >= 1000)
OR
(completed)
```

Viết rõ bằng parentheses:

```sql
SELECT *
FROM novels
WHERE (
        status = 'ongoing'
        AND chapter_count >= 1000
      )
   OR status = 'completed';
```

Đây là cách nên viết.

---

# 8. Tại sao dấu ngoặc rất quan trọng?

SQL có **operator precedence**.

Trong biểu thức:

```sql
A AND B OR C
```

`AND` được đánh giá trước `OR`.

Về logic nó được hiểu như:

```text
(A AND B) OR C
```

chứ không phải:

```text
A AND (B OR C)
```

Hai biểu thức có thể cho kết quả hoàn toàn khác nhau.

---

# 9. Ví dụ cực kỳ quan trọng

Giả sử yêu cầu:

> Tìm novel thuộc `site_a` và (`ongoing` hoặc `completed`).

Ý định:

```text
source = site_a
AND
(status = ongoing OR status = completed)
```

Viết:

```sql
SELECT *
FROM novels
WHERE source = 'site_a'
  AND (
      status = 'ongoing'
      OR status = 'completed'
  );
```

### Không nên viết mơ hồ:

```sql
WHERE source = 'site_a'
  AND status = 'ongoing'
  OR status = 'completed';
```

SQL hiểu nó là:

```text
(source = site_a AND status = ongoing)
OR
status = completed
```

Như vậy **mọi novel completed**, kể cả từ `site_b`, cũng có thể được lấy.

Đây là một bug business logic rất thực tế.

---

# 10. Quy tắc vàng

Khi kết hợp:

```text
AND + OR
```

hãy ưu tiên viết:

```sql
AND (
    ...
    OR ...
)
```

thay vì dựa vào precedence để người đọc tự suy luận.

---

# 11. `NOT` — phủ định

`NOT` đảo ngược điều kiện.

Ví dụ:

```sql
SELECT *
FROM novels
WHERE NOT status = 'completed';
```

Ý nghĩa:

> Lấy những novel không phải completed.

Tuy nhiên với trường hợp đơn giản, có thể viết:

```sql
WHERE status != 'completed'
```

hoặc:

```sql
WHERE status <> 'completed'
```

---

# 12. NOT với `IN`

Ví dụ:

```sql
SELECT *
FROM novels
WHERE id NOT IN (1, 3, 5);
```

Nghĩa:

```text
id không thuộc {1, 3, 5}
```

Đây là cách rất tự nhiên để dùng `NOT`.

---

# 13. NOT với LIKE

Ví dụ:

> Tìm novel không chứa chữ "Tiên".

```sql
SELECT *
FROM novels
WHERE title NOT LIKE '%Tiên%';
```

---

# 14. NOT với BETWEEN

Ví dụ:

> Tìm novel có số chapter nằm ngoài khoảng 100–500.

```sql
SELECT *
FROM novels
WHERE chapter_count NOT BETWEEN 100 AND 500;
```

---

# 15. NOT với IS NULL

Ví dụ:

```sql
SELECT *
FROM novels
WHERE author IS NOT NULL;
```

Đây là pattern cực kỳ phổ biến.

---

# 16. Các dạng NOT thường gặp

```sql
NOT IN
NOT LIKE
NOT BETWEEN
IS NOT NULL
```

Bạn nên nhớ chúng như những pattern riêng.

---

# 17. Kết hợp ba operator

Ví dụ:

> Tìm novel đang ongoing, có từ 500 chapter trở lên và title không chứa "Test".

```sql
SELECT id, title, chapter_count
FROM novels
WHERE status = 'ongoing'
  AND chapter_count >= 500
  AND title NOT LIKE '%Test%';
```

Logic:

```text
ongoing
   AND
chapter_count >= 500
   AND
title NOT LIKE '%Test%'
```

---

# 18. Một business rule thực tế hơn

Yêu cầu:

> Lấy novel từ `site_a`, đang ongoing, có ít nhất 500 chapter, hoặc novel từ `site_a` đã completed.

Viết theo logic:

```text
source = site_a
AND
(
    ongoing AND chapter_count >= 500
    OR
    completed
)
```

SQL:

```sql
SELECT id, title, status, chapter_count
FROM novels
WHERE source = ?
  AND (
        (
            status = ?
            AND chapter_count >= ?
        )
        OR
        status = ?
      );
```

Python:

```python
cursor.execute(
    """
    SELECT id, title, status, chapter_count
    FROM novels
    WHERE source = ?
      AND (
            (
                status = ?
                AND chapter_count >= ?
            )
            OR
            status = ?
          )
    """,
    (
        "site_a",
        "ongoing",
        500,
        "completed",
    ),
)
```

Đây chính là kiểu query mà Repository thực tế sẽ phải xử lý.

---

# 19. AND với LIKE

Ví dụ search:

> Title chứa "Tiên" và author chứa "Ngữ".

```sql
SELECT id, title, author
FROM novels
WHERE title LIKE ?
  AND author LIKE ?;
```

Python:

```python
keyword_title = "%Tiên%"
keyword_author = "%Ngữ%"

cursor.execute(
    """
    SELECT id, title, author
    FROM novels
    WHERE title LIKE ?
      AND author LIKE ?
    """,
    (keyword_title, keyword_author),
)
```

---

# 20. OR với LIKE

Search box thường cần:

> Tìm keyword trong title **hoặc** author.

```sql
SELECT id, title, author
FROM novels
WHERE title LIKE ?
   OR author LIKE ?;
```

Python:

```python
keyword = "%Tiên%"

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

---

# 21. AND + OR + parentheses

Ví dụ:

> Tìm novel có title chứa `"Tiên"` và:
>
> * đang ongoing, **hoặc**
> * đã completed nhưng có ít nhất 2000 chapter.

Logic:

```text
title LIKE "Tiên"
AND
(
    status = ongoing
    OR
    (
        status = completed
        AND chapter_count >= 2000
    )
)
```

SQL:

```sql
SELECT id, title, status, chapter_count
FROM novels
WHERE title LIKE ?
  AND (
        status = ?
        OR (
            status = ?
            AND chapter_count >= ?
        )
      );
```

Python:

```python
cursor.execute(
    """
    SELECT id, title, status, chapter_count
    FROM novels
    WHERE title LIKE ?
      AND (
            status = ?
            OR (
                status = ?
                AND chapter_count >= ?
            )
          )
    """,
    (
        "%Tiên%",
        "ongoing",
        "completed",
        2000,
    ),
)
```

Đây là level query thực tế mà bạn nên bắt đầu làm quen.

---

# 22. Logic SQL giống logic lập trình

Bạn có thể liên hệ:

### Python

```python
if status == "ongoing" and chapter_count >= 500:
    ...
```

### SQL

```sql
WHERE status = 'ongoing'
  AND chapter_count >= 500
```

Python:

```python
if status == "ongoing" or chapter_count >= 500:
    ...
```

SQL:

```sql
WHERE status = 'ongoing'
   OR chapter_count >= 500
```

Python:

```python
if not is_completed:
    ...
```

SQL:

```sql
WHERE NOT status = 'completed'
```

Tư duy logic tương tự, nhưng SQL có thêm vấn đề **NULL và three-valued logic**.

---

# 23. NULL và AND / OR

Đây là phần nâng cao nhưng bạn nên biết từ sớm.

SQL không chỉ có:

```text
TRUE
FALSE
```

mà còn có:

```text
UNKNOWN
```

Ví dụ:

```sql
author = NULL
```

không cho kết quả TRUE.

Vì vậy:

```sql
WHERE author != 'Nhĩ Căn'
```

không đồng nghĩa với:

```text
author khác Nhĩ Căn
```

cho mọi trường hợp.

Nếu `author` là `NULL`, điều kiện có thể trở thành `UNKNOWN`.

---

# 24. Ví dụ NULL

Giả sử:

```text
id  author
1   Nhĩ Căn
2   Vong Ngữ
3   NULL
```

Query:

```sql
SELECT *
FROM novels
WHERE author != 'Nhĩ Căn';
```

Đừng mặc định rằng row `3` chắc chắn được lấy.

Nếu muốn:

> author khác Nhĩ Căn **hoặc chưa có author**

hãy viết:

```sql
SELECT *
FROM novels
WHERE author != 'Nhĩ Căn'
   OR author IS NULL;
```

Đây là cách diễn đạt business rule rõ ràng.

---

# 25. Truth table cơ bản

SQL có:

```text
TRUE
FALSE
UNKNOWN
```

Ví dụ với `AND`:

| A       | B       | A AND B |
| ------- | ------- | ------- |
| TRUE    | TRUE    | TRUE    |
| TRUE    | FALSE   | FALSE   |
| TRUE    | UNKNOWN | UNKNOWN |
| FALSE   | UNKNOWN | FALSE   |
| UNKNOWN | UNKNOWN | UNKNOWN |

Với `OR`:

| A       | B       | A OR B  |
| ------- | ------- | ------- |
| TRUE    | FALSE   | TRUE    |
| TRUE    | UNKNOWN | TRUE    |
| FALSE   | FALSE   | FALSE   |
| FALSE   | UNKNOWN | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN |

Bạn chưa cần học thuộc toàn bộ bảng này.

Chỉ cần nhớ:

> **NULL có thể làm điều kiện trở thành UNKNOWN.**

---

# 26. Một pattern rất hay trong Repository

Ví dụ function:

```python
def find_novels(
    conn,
    status=None,
    min_chapters=None,
):
    ...
```

Ta có thể xây query động.

Ví dụ nếu:

```python
status="ongoing"
min_chapters=500
```

thì SQL sẽ trở thành:

```sql
WHERE status = ?
  AND chapter_count >= ?
```

Đây là nền tảng của **dynamic query builder**.

Nhưng:

> Không nên ghép giá trị người dùng trực tiếp vào SQL.

Ta chỉ xây **SQL structure**, còn values vẫn parameterized.

---

# 27. Ví dụ dynamic WHERE an toàn

```python
conditions = []
params = []

if status is not None:
    conditions.append("status = ?")
    params.append(status)

if min_chapters is not None:
    conditions.append("chapter_count >= ?")
    params.append(min_chapters)

sql = """
    SELECT id, title, status, chapter_count
    FROM novels
"""

if conditions:
    sql += " WHERE " + " AND ".join(conditions)

cursor.execute(sql, params)
```

Nếu:

```python
status = "ongoing"
min_chapters = 500
```

SQL sẽ là:

```sql
SELECT id, title, status, chapter_count
FROM novels
WHERE status = ?
  AND chapter_count >= ?
```

Parameters:

```text
["ongoing", 500]
```

Đây là kỹ thuật chúng ta sẽ gặp lại khi xây **Repository Pattern**.

---

# 28. Mental Model

Khi nhận một yêu cầu SQL phức tạp, đừng viết SQL ngay.

Hãy chuyển thành **logic tree**.

Ví dụ:

> Truyện từ site A, title chứa Tiên, và (ongoing hoặc completed trên 2000 chapter).

Viết trước:

```text
AND
├── source = A
├── title LIKE "%Tiên%"
└── OR
    ├── status = ongoing
    └── AND
        ├── status = completed
        └── chapter_count > 2000
```

Sau đó mới chuyển thành:

```sql
WHERE source = ?
  AND title LIKE ?
  AND (
        status = ?
        OR (
            status = ?
            AND chapter_count > ?
        )
      )
```

**Đây là kỹ năng quan trọng hơn việc học thuộc cú pháp.**

---

# 29. Bài tập Buổi 8

Giả sử bảng:

```text
novels(
    id,
    source,
    title,
    author,
    status,
    chapter_count
)
```

### Bài 1

Tìm novel:

```text
status = ongoing
AND
chapter_count >= 1000
```

---

### Bài 2

Tìm novel:

```text
status = ongoing
OR
status = completed
```

Dùng `OR`.

---

### Bài 3

Tìm novel:

```text
chapter_count < 100
OR
chapter_count > 2000
```

---

### Bài 4

Tìm novel:

```text
title chứa "Tiên"
AND
author không NULL
```

---

### Bài 5

Tìm novel:

```text
title chứa "Tiên"
AND
(
    ongoing
    OR
    completed với >= 2000 chapter
)
```

Đây là bài quan trọng nhất.

---

### Bài 6 — Phát hiện bug

Query sau:

```sql
SELECT *
FROM novels
WHERE source = 'site_a'
  AND status = 'ongoing'
  OR status = 'completed';
```

Hãy giải thích SQL thực sự hiểu nó như thế nào.

Sau đó sửa lại để đúng ý:

```text
site_a
AND
(ongoing OR completed)
```

---

### Bài 7 — Python

Viết:

```python
def search_novels(
    conn,
    keyword: str,
    status: str | None = None,
):
    ...
```

Yêu cầu:

```text
title chứa keyword
AND
nếu status != None thì lọc thêm status
```

Ví dụ:

```python
search_novels(conn, "Tiên")
```

và:

```python
search_novels(conn, "Tiên", "ongoing")
```

Tất cả giá trị phải sử dụng **parameterized query**.

---

# 30. Tổng kết Buổi 8

```text
AND
 ↓
Tất cả điều kiện phải đúng

OR
 ↓
Ít nhất một điều kiện đúng

NOT
 ↓
Phủ định điều kiện
```

Nhưng kỹ năng quan trọng nhất:

```text
AND + OR
    ↓
parentheses ()
    ↓
biểu diễn business rule rõ ràng
```

Và nhớ:

```sql
-- ❌ dễ gây bug
WHERE A
  AND B
  OR C

-- ✅ rõ ràng
WHERE A
  AND (
      B
      OR C
  )
```

Đến đây bạn đã có khả năng xây `WHERE` khá mạnh:

```text
WHERE
 ├── =
 ├── !=
 ├── >
 ├── <
 ├── >=
 ├── <=
 ├── BETWEEN
 ├── IN
 ├── LIKE
 ├── IS NULL
 │
 └── AND / OR / NOT
```

**Buổi 9 — Aggregate Functions** sẽ chuyển từ câu hỏi **“row nào?”** sang **“toàn bộ tập dữ liệu cho tôi biết điều gì?”** với `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`. Đây là nền tảng trực tiếp để sang `GROUP BY` và `HAVING`.
