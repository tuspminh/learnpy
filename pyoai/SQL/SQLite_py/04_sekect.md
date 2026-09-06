# Buổi 4 — `SELECT`: Truy vấn dữ liệu với SQLite + Python

Hôm nay chúng ta bắt đầu phần **cốt lõi nhất của SQL**: đọc dữ liệu.

Sau buổi này bạn sẽ làm được:

```text
SELECT
  ↓
FROM
  ↓
WHERE
  ↓
ORDER BY
  ↓
LIMIT
  ↓
OFFSET
```

Và cuối buổi có thể viết các query gần với `NovelRepository`.

---

# 1. `SELECT` dùng để làm gì?

`SELECT` dùng để **đọc dữ liệu** từ database.

Ví dụ:

```sql
SELECT *
FROM novels;
```

Nghĩa là:

> Lấy tất cả các column và tất cả các row trong `novels`.

Giả sử:

```text
novels

id | title                | author
---+----------------------+----------------
1  | Đấu Phá Thương Khung | Thiên Tằm
2  | Tiên Nghịch          | Nhĩ Căn
3  | Phàm Nhân Tu Tiên    | Vong Ngữ
```

Query:

```sql
SELECT *
FROM novels;
```

Kết quả:

```text
1 | Đấu Phá Thương Khung | Thiên Tằm
2 | Tiên Nghịch          | Nhĩ Căn
3 | Phàm Nhân Tu Tiên    | Vong Ngữ
```

---

# 2. `SELECT *` nghĩa là gì?

Dấu:

```sql
*
```

nghĩa là:

> tất cả các column.

Ví dụ:

```sql
SELECT *
FROM novels;
```

tương đương ý tưởng với:

```sql
SELECT id, title, author
FROM novels;
```

Nhưng trong code production, **không nên mặc định dùng `SELECT *`** nếu bạn chỉ cần một vài column.

Ví dụ tốt hơn:

```sql
SELECT id, title
FROM novels;
```

Lợi ích:

* rõ ràng hơn
* chỉ lấy dữ liệu cần thiết
* giảm dữ liệu truyền qua database layer
* query ổn định hơn khi schema thay đổi

---

# 3. Chọn một column

```sql
SELECT title
FROM novels;
```

Kết quả:

```text
Đấu Phá Thương Khung
Tiên Nghịch
Phàm Nhân Tu Tiên
```

Hai column:

```sql
SELECT id, title
FROM novels;
```

Kết quả:

```text
1 | Đấu Phá Thương Khung
2 | Tiên Nghịch
3 | Phàm Nhân Tu Tiên
```

---

# 4. `SELECT` từ Python

```python
cursor.execute("""
    SELECT id, title, author
    FROM novels
""")

rows = cursor.fetchall()

for row in rows:
    print(row)
```

Kết quả:

```text
(1, 'Đấu Phá Thương Khung', 'Thiên Tằm')
(2, 'Tiên Nghịch', 'Nhĩ Căn')
(3, 'Phàm Nhân Tu Tiên', 'Vong Ngữ')
```

---

# 5. `WHERE`

Đây là phần cực kỳ quan trọng.

`WHERE` dùng để **lọc row**.

Ví dụ:

```sql
SELECT *
FROM novels
WHERE id = 2;
```

Kết quả:

```text
2 | Tiên Nghịch | Nhĩ Căn
```

Ta có:

```text
SELECT
   ↓
FROM novels
   ↓
WHERE id = 2
```

Nghĩa là:

> Từ bảng `novels`, lấy những row có `id = 2`.

---

# 6. `WHERE` với Python

Không nên:

```python
novel_id = 2

cursor.execute(
    f"SELECT * FROM novels WHERE id = {novel_id}"
)
```

Hãy dùng parameter:

```python
novel_id = 2

cursor.execute(
    """
    SELECT id, title, author
    FROM novels
    WHERE id = ?
    """,
    (novel_id,),
)

row = cursor.fetchone()
```

---

# 7. Tìm theo title

```sql
SELECT id, title, author
FROM novels
WHERE title = 'Tiên Nghịch';
```

Python:

```python
title = "Tiên Nghịch"

cursor.execute(
    """
    SELECT id, title, author
    FROM novels
    WHERE title = ?
    """,
    (title,),
)

row = cursor.fetchone()
```

Đây là pattern rất quan trọng cho Repository:

```python
def find_by_title(title):
    ...
```

---

# 8. `WHERE` với số

Ví dụ:

```sql
SELECT *
FROM chapters
WHERE chapter_number = 100;
```

Hoặc:

```sql
SELECT *
FROM chapters
WHERE chapter_number > 100;
```

Hoặc:

```sql
SELECT *
FROM chapters
WHERE chapter_number >= 100;
```

Các toán tử cơ bản:

```text
=       bằng
!=      khác
>       lớn hơn
<       nhỏ hơn
>=      lớn hơn hoặc bằng
<=      nhỏ hơn hoặc bằng
```

---

# 9. `ORDER BY`

Giả sử:

```text
id | chapter_number | title
---+----------------+--------
1  | 3              | Chương 3
2  | 1              | Chương 1
3  | 2              | Chương 2
```

Query:

```sql
SELECT *
FROM chapters
ORDER BY chapter_number;
```

Kết quả:

```text
1 | 1 | Chương 1
2 | 2 | Chương 2
3 | 3 | Chương 3
```

Mặc định:

```sql
ORDER BY chapter_number ASC
```

`ASC` = tăng dần.

---

# 10. `DESC`

Muốn giảm dần:

```sql
SELECT *
FROM chapters
ORDER BY chapter_number DESC;
```

Kết quả:

```text
3 | 3 | Chương 3
2 | 2 | Chương 2
1 | 1 | Chương 1
```

Trong crawler:

```sql
SELECT *
FROM chapters
ORDER BY chapter_number DESC;
```

có thể dùng để lấy chapter mới nhất trước.

---

# 11. Kết hợp `WHERE` + `ORDER BY`

Ví dụ:

```sql
SELECT id, chapter_number, title
FROM chapters
WHERE novel_id = 10
ORDER BY chapter_number DESC;
```

Đọc theo tư duy:

```text
FROM chapters
      ↓
WHERE novel_id = 10
      ↓
lọc chapter của novel 10
      ↓
ORDER BY chapter_number DESC
      ↓
sắp xếp mới → cũ
```

Đây đã là một query thực tế.

---

# 12. `LIMIT`

`LIMIT` giới hạn số row trả về.

```sql
SELECT *
FROM novels
LIMIT 10;
```

Nghĩa là:

> Lấy tối đa 10 row.

Ví dụ:

```sql
SELECT id, title
FROM novels
ORDER BY id DESC
LIMIT 20;
```

Nghĩa là:

> Lấy 20 novel có ID lớn nhất.

---

# 13. `LIMIT` rất quan trọng khi làm pagination

Ví dụ bạn có:

```text
10000 novels
```

Không nên lúc nào cũng:

```sql
SELECT *
FROM novels;
```

rồi lấy toàn bộ 10000 record về Python.

Thay vào đó:

```sql
SELECT id, title
FROM novels
ORDER BY id DESC
LIMIT 20;
```

Chỉ lấy 20.

---

# 14. `OFFSET`

`OFFSET` bỏ qua một số row đầu tiên.

```sql
SELECT id, title
FROM novels
ORDER BY id
LIMIT 20
OFFSET 20;
```

Ý nghĩa:

```text
20 row đầu
    ↓
BỎ QUA

row 21 → row 40
    ↓
TRẢ VỀ
```

---

# 15. Pagination

Giả sử:

```text
page_size = 20
```

Trang 1:

```sql
LIMIT 20 OFFSET 0
```

Trang 2:

```sql
LIMIT 20 OFFSET 20
```

Trang 3:

```sql
LIMIT 20 OFFSET 40
```

Công thức:

```text
offset = (page - 1) * page_size
```

Python:

```python
page = 3
page_size = 20

offset = (page - 1) * page_size
```

Kết quả:

```text
offset = 40
```

Query:

```python
cursor.execute(
    """
    SELECT id, title
    FROM novels
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """,
    (page_size, offset),
)
```

---

# 16. Một điểm quan trọng: luôn có `ORDER BY` khi pagination

Không nên:

```sql
SELECT *
FROM novels
LIMIT 20
OFFSET 20;
```

Mà nên:

```sql
SELECT *
FROM novels
ORDER BY id
LIMIT 20
OFFSET 20;
```

Vì pagination cần một **thứ tự ổn định**.

Nếu không có `ORDER BY`, thứ tự row trả về không nên được coi là thứ tự ổn định mà application có thể dựa vào.

---

# 17. `fetchone()`

Khi query dự kiến chỉ có một row:

```python
cursor.execute(
    """
    SELECT id, title
    FROM novels
    WHERE id = ?
    """,
    (10,),
)

row = cursor.fetchone()
```

Nếu tồn tại:

```text
(10, 'Tiên Nghịch')
```

Nếu không tồn tại:

```python
None
```

Đây là pattern rất quan trọng:

```python
row = cursor.fetchone()

if row is None:
    # không tìm thấy
    ...
```

---

# 18. `fetchall()`

Nếu muốn tất cả kết quả:

```python
cursor.execute("""
    SELECT id, title
    FROM novels
    ORDER BY id
""")

rows = cursor.fetchall()
```

Kết quả:

```python
[
    (1, "Novel A"),
    (2, "Novel B"),
    (3, "Novel C"),
]
```

---

# 19. So sánh `fetchone()` và `fetchall()`

```text
fetchone()
    ↓
một row
    ↓
row hoặc None
```

Trong khi:

```text
fetchall()
    ↓
nhiều row
    ↓
list
```

Ví dụ Repository:

```python
def get_by_id(novel_id):
    ...
```

thường:

```python
fetchone()
```

Còn:

```python
def list_novels():
    ...
```

thường:

```python
fetchall()
```

---

# 20. `sqlite3.Row` — chuẩn bị cho Repository

Mặc định:

```python
row = cursor.fetchone()

print(row)
```

có dạng:

```text
(1, 'Tiên Nghịch', 'Nhĩ Căn')
```

Muốn truy cập:

```python
row[0]
row[1]
row[2]
```

không đẹp.

Ta có thể dùng:

```python
conn.row_factory = sqlite3.Row
```

Ví dụ:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("""
    SELECT id, title, author
    FROM novels
    WHERE id = ?
""", (1,))

row = cursor.fetchone()

print(row["id"])
print(row["title"])
print(row["author"])
```

Kết quả:

```text
1
Tiên Nghịch
Nhĩ Căn
```

Đây là cách rất hữu ích khi mapping:

```text
SQLite Row
    ↓
Domain Model
```

Sau này Repository của chúng ta sẽ sử dụng pattern này.

---

# 21. Query thực tế cho Novel Repository

Giả sử:

```text
novels
```

có:

```text
id
source
title
author
url
status
created_at
updated_at
```

### Lấy novel theo ID

```sql
SELECT
    id,
    source,
    title,
    author,
    url,
    status,
    created_at,
    updated_at
FROM novels
WHERE id = ?;
```

---

### Lấy novel theo URL

```sql
SELECT
    id,
    source,
    title,
    author,
    url,
    status
FROM novels
WHERE url = ?;
```

---

### Lấy novel đang crawl

```sql
SELECT
    id,
    title,
    author,
    status
FROM novels
WHERE status = 'ongoing';
```

---

### Lấy 20 novel mới nhất

```sql
SELECT
    id,
    title,
    author
FROM novels
ORDER BY id DESC
LIMIT 20;
```

---

# 22. Query chapter thực tế

Giả sử:

```text
chapters
──────────────
id
novel_id
chapter_number
title
url
content
```

Lấy toàn bộ chapter của novel:

```sql
SELECT
    id,
    novel_id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number ASC;
```

Lấy chapter mới nhất:

```sql
SELECT
    id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number DESC
LIMIT 1;
```

Đây là query mà sau này `ChapterRepository` sẽ sử dụng.

---

# 23. Một lỗi rất quan trọng: SQL Injection

Đừng:

```python
novel_id = user_input

cursor.execute(
    f"""
    SELECT *
    FROM novels
    WHERE id = {novel_id}
    """
)
```

Hãy:

```python
cursor.execute(
    """
    SELECT *
    FROM novels
    WHERE id = ?
    """,
    (novel_id,),
)
```

Pattern:

```text
SQL structure
     +
parameters
     ↓
execute()
```

---

# 24. Thứ tự tư duy của một `SELECT`

Khi gặp query:

```sql
SELECT title
FROM novels
WHERE status = 'ongoing'
ORDER BY id DESC
LIMIT 20;
```

Hãy đọc nó như:

```text
FROM
 ↓
chọn nguồn dữ liệu

WHERE
 ↓
lọc

ORDER BY
 ↓
sắp xếp

LIMIT
 ↓
giới hạn

SELECT
 ↓
chọn column trả về
```

Về mặt **cú pháp**, SQL viết:

```text
SELECT
FROM
WHERE
ORDER BY
LIMIT
```

Nhưng khi tư duy về dữ liệu, việc xử lý logic có thể hình dung bắt đầu từ:

```text
FROM → WHERE → ORDER BY → LIMIT → SELECT
```

Cách tư duy này rất hữu ích khi query phức tạp.

---

# 25. Mini Project Buổi 4

Tạo database:

```text
novel.db
```

Table:

```sql
CREATE TABLE IF NOT EXISTS novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT NOT NULL DEFAULT 'ongoing'
);
```

Insert khoảng 10 novel.

Sau đó viết Python thực hiện 5 chức năng:

### ① Lấy tất cả

```python
def get_all_novels():
    ...
```

### ② Lấy theo ID

```python
def get_novel_by_id(novel_id):
    ...
```

### ③ Lấy novel đang `ongoing`

```python
def get_ongoing_novels():
    ...
```

### ④ Lấy 5 novel mới nhất

```python
def get_latest_novels(limit=5):
    ...
```

### ⑤ Pagination

```python
def get_novels(page=1, page_size=5):
    ...
```

Trong đó:

```python
offset = (page - 1) * page_size
```

và SQL:

```sql
SELECT id, title, author, status
FROM novels
ORDER BY id DESC
LIMIT ? OFFSET ?;
```

---

# 26. Bài tập tư duy

Cho bảng:

```text
chapters
```

```text
id
novel_id
chapter_number
title
```

Hãy tự viết SQL cho:

**A.** Lấy chapter số 100 của novel ID = 5.

**B.** Lấy 10 chapter mới nhất của novel ID = 5.

**C.** Lấy chapter từ 100 → 120.

**D.** Lấy chapter thứ 3 trong pagination, mỗi trang 20 chapter.

**E.** Lấy chapter có `chapter_number` lớn nhất của novel ID = 5.

---

# 27. Những gì bạn cần nắm sau Buổi 4

```text
SELECT
│
├── *
├── column1, column2
│
├── FROM
│
├── WHERE
│
├── ORDER BY
│     ├── ASC
│     └── DESC
│
├── LIMIT
│
└── OFFSET
```

Python:

```text
cursor.execute()
       ↓
fetchone()
       ↓
row / None
```

hoặc:

```text
cursor.execute()
       ↓
fetchall()
       ↓
list[rows]
```

Và đặc biệt:

```python
conn.row_factory = sqlite3.Row
```

sẽ là một công cụ quan trọng khi chúng ta bước vào **Repository Pattern**.

---

## Mốc kiến thức hiện tại

Bạn đã đi qua:

```text
Buổi 1
Connection / Cursor / Transaction
        ↓
Buổi 2
CREATE TABLE / Constraints
        ↓
Buổi 3
INSERT / Parameters / executemany()
        ↓
Buổi 4
SELECT / WHERE / ORDER BY / LIMIT / OFFSET
```

**Buổi 5** sẽ học **`UPDATE`**: cập nhật dữ liệu an toàn, `WHERE`, `rowcount`, transaction, cập nhật một/nhiều row, và đặc biệt là cách tránh lỗi kinh điển **`UPDATE` nhầm toàn bộ bảng**.
