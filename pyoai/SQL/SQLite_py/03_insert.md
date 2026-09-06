# Buổi 3 — `INSERT`, Parameterized Query và `executemany()`

Hôm nay chúng ta tập trung vào **đưa dữ liệu từ Python vào SQLite một cách đúng và an toàn**.

Sau buổi này bạn phải thành thạo:

```text
INSERT
   ↓
?
   ↓
Parameterized Query
   ↓
lastrowid
   ↓
executemany()
   ↓
Transaction
```

---

# 1. `INSERT INTO`

SQL cơ bản:

```sql
INSERT INTO novels (title, author)
VALUES ('Tiên Nghịch', 'Nhĩ Căn');
```

Cấu trúc:

```text
INSERT INTO
    ↓
table
    ↓
(columns)
    ↓
VALUES
    ↓
(values)
```

Ví dụ table:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT
);
```

Insert:

```sql
INSERT INTO novels (title, author)
VALUES ('Tiên Nghịch', 'Nhĩ Căn');
```

SQLite sẽ tạo:

```text
id | title       | author
---+-------------+-------
1  | Tiên Nghịch | Nhĩ Căn
```

---

# 2. `INSERT` từ Python

Ta có:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO novels (title, author)
    VALUES ('Tiên Nghịch', 'Nhĩ Căn')
""")

conn.commit()
conn.close()
```

Về mặt kỹ thuật chạy được.

Nhưng **không nên viết SQL kiểu này khi dữ liệu đến từ biến Python**.

---

# 3. Vấn đề với string interpolation

Giả sử:

```python
title = "Tiên Nghịch"
author = "Nhĩ Căn"
```

Một người mới có thể viết:

```python
cursor.execute(
    f"""
    INSERT INTO novels (title, author)
    VALUES ('{title}', '{author}')
    """
)
```

Đây là cách **không nên dùng**.

Không chỉ vì SQL Injection.

Nó còn dễ hỏng khi dữ liệu chứa dấu `'`.

Ví dụ:

```python
title = "Novel John's Story"
```

SQL được tạo ra có thể trở thành:

```sql
INSERT INTO novels (title)
VALUES ('Novel John's Story');
```

Dấu `'` trong `John's` phá cú pháp SQL.

---

# 4. Parameterized Query

Đây là cách đúng:

```python
title = "Tiên Nghịch"
author = "Nhĩ Căn"

cursor.execute("""
    INSERT INTO novels (title, author)
    VALUES (?, ?)
""", (title, author))
```

Ở đây:

```text
SQL
 │
 ├── ?
 └── ?
      │
      ▼
parameters
```

Python/SQLite sẽ xử lý việc truyền giá trị vào đúng cách.

---

# 5. Vì sao dùng `?`

Ví dụ:

```python
cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)
```

Mapping:

```text
?  ← "Tiên Nghịch"
?  ← "Nhĩ Căn"
```

Thứ tự phải tương ứng:

```text
SQL                 parameters

title = ?      ←    "Tiên Nghịch"
author = ?     ←    "Nhĩ Căn"
```

---

# 6. Parameter phải là tuple

Ví dụ một parameter:

```python
cursor.execute(
    "INSERT INTO novels (title) VALUES (?)",
    ("Tiên Nghịch",),
)
```

Chú ý:

```python
("Tiên Nghịch",)
```

có dấu phẩy.

Bởi vì:

```python
("Tiên Nghịch")
```

chỉ là string được đặt trong dấu ngoặc.

Còn:

```python
("Tiên Nghịch",)
```

là tuple một phần tử.

---

# 7. Không dùng `?` để thay tên column

Điều này:

```python
cursor.execute(
    "SELECT * FROM ?",
    ("novels",),
)
```

không hoạt động như bạn mong muốn.

Parameter dùng cho **values**, không phải SQL identifiers.

Ví dụ đúng:

```python
cursor.execute(
    "SELECT * FROM novels WHERE id = ?",
    (novel_id,),
)
```

Ở đây:

```text
novels
```

là SQL structure.

Còn:

```text
novel_id
```

là data.

---

# 8. Parameterized query và SQL Injection

Giả sử user nhập:

```text
' OR 1=1 --
```

Nếu bạn nối chuỗi SQL:

```python
username = user_input

sql = f"""
SELECT *
FROM users
WHERE username = '{username}'
"""
```

SQL có thể bị thay đổi ý nghĩa.

Parameterized query:

```python
cursor.execute(
    """
    SELECT *
    FROM users
    WHERE username = ?
    """,
    (username,),
)
```

thì giá trị user nhập được coi là **data**, không phải một phần của SQL command.

Vì vậy:

> **Parameterized query phải trở thành thói quen mặc định khi làm việc với dữ liệu động.**

---

# 9. `lastrowid`

Đây là tính năng rất quan trọng khi làm Repository.

Giả sử:

```python
cursor.execute("""
    INSERT INTO novels (title, author)
    VALUES (?, ?)
""", ("Tiên Nghịch", "Nhĩ Căn"))
```

Ta muốn biết `id` SQLite vừa tạo.

Dùng:

```python
novel_id = cursor.lastrowid
```

Ví dụ:

```python
cursor.execute("""
    INSERT INTO novels (title, author)
    VALUES (?, ?)
""", ("Tiên Nghịch", "Nhĩ Căn"))

novel_id = cursor.lastrowid

print(novel_id)
```

Kết quả:

```text
1
```

---

# 10. Tại sao `lastrowid` quan trọng?

Sau này chúng ta có:

```text
novels
   │
   └── id = 10
         │
         ├── chapter 1
         ├── chapter 2
         └── chapter 3
```

Khi tạo novel:

```python
cursor.execute("""
    INSERT INTO novels (title)
    VALUES (?)
""", (title,))

novel_id = cursor.lastrowid
```

Sau đó dùng `novel_id` để tạo chapter:

```python
cursor.execute("""
    INSERT INTO chapters (
        novel_id,
        chapter_number,
        title
    )
    VALUES (?, ?, ?)
""", (
    novel_id,
    1,
    "Chương 1",
))
```

Đây chính là cầu nối:

```text
INSERT novel
     ↓
lastrowid
     ↓
novel_id
     ↓
INSERT chapters
```

Sau này sẽ trở thành logic Repository rất quan trọng.

---

# 11. `executemany()`

Giả sử muốn insert 3 novels.

Cách thứ nhất:

```python
cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)

cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Phàm Nhân Tu Tiên", "Vong Ngữ"),
)

cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Đấu Phá Thương Khung", "Thiên Tằm Thổ Đậu"),
)
```

Chạy được nhưng dài.

---

# 12. Dùng `executemany()`

Ta có:

```python
novels = [
    ("Tiên Nghịch", "Nhĩ Căn"),
    ("Phàm Nhân Tu Tiên", "Vong Ngữ"),
    ("Đấu Phá Thương Khung", "Thiên Tằm Thổ Đậu"),
]
```

Sau đó:

```python
cursor.executemany(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    novels,
)
```

SQLite sẽ thực hiện insert cho từng tuple.

---

# 13. Hình dung `executemany()`

Dữ liệu:

```text
[
    ("Tiên Nghịch", "Nhĩ Căn"),
    ("Phàm Nhân Tu Tiên", "Vong Ngữ"),
    ("Đấu Phá Thương Khung", "Thiên Tằm Thổ Đậu")
]
```

SQL:

```sql
INSERT INTO novels (title, author)
VALUES (?, ?);
```

Conceptually:

```text
            ┌── row 1
            ├── row 2
SQL template┼── row 3
            └── ...
```

Rất phù hợp khi crawler lấy được một batch dữ liệu.

---

# 14. `commit()` sau batch

Ví dụ:

```python
cursor.executemany(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    novels,
)

conn.commit()
```

Không nên:

```python
for novel in novels:
    cursor.execute(...)
    conn.commit()
```

một cách tùy tiện.

Vì khi batch lớn:

```text
1000 records
```

mà commit từng record:

```text
INSERT
COMMIT

INSERT
COMMIT

INSERT
COMMIT

...
```

thường sẽ kém hiệu quả hơn so với gom trong transaction phù hợp.

Ta muốn:

```text
BEGIN
 │
 ├── INSERT
 ├── INSERT
 ├── INSERT
 ├── ...
 │
 ▼
COMMIT
```

---

# 15. Transaction + `executemany()`

Ví dụ:

```python
import sqlite3


conn = sqlite3.connect("novel.db")
cursor = conn.cursor()

novels = [
    ("Tiên Nghịch", "Nhĩ Căn"),
    ("Phàm Nhân Tu Tiên", "Vong Ngữ"),
    ("Đấu Phá Thương Khung", "Thiên Tằm Thổ Đậu"),
]

try:
    cursor.executemany(
        """
        INSERT INTO novels (title, author)
        VALUES (?, ?)
        """,
        novels,
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
```

Luồng:

```text
                ┌── success ──→ COMMIT
                │
BEGIN → INSERT ─┤
                │
                └── error ────→ ROLLBACK
```

Đây chính là tư duy transaction mà sau này Unit of Work sẽ đóng gói.

---

# 16. `rowcount`

Sau khi insert:

```python
cursor.executemany(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    novels,
)
```

Có thể xem:

```python
print(cursor.rowcount)
```

Ví dụ:

```text
3
```

Tùy loại statement và driver/version, ý nghĩa `rowcount` có một số chi tiết cần lưu ý, nên đừng dùng nó như một nguồn sự thật tuyệt đối cho mọi loại query.

---

# 17. `INSERT OR IGNORE`

SQLite hỗ trợ:

```sql
INSERT OR IGNORE
```

Ví dụ bảng:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
);
```

Ta insert:

```python
cursor.execute(
    """
    INSERT OR IGNORE INTO novels (title, url)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "https://example.com/tien-nghich"),
)
```

Nếu URL đã tồn tại:

```text
UNIQUE violation
       ↓
     IGNORE
```

Không tạo record mới.

Nhưng **đừng lạm dụng `OR IGNORE`**, vì nó có thể khiến một số constraint violation bị âm thầm bỏ qua.

Sau này chúng ta sẽ học `ON CONFLICT` kỹ hơn.

---

# 18. Một ví dụ crawler thực tế

Giả sử parser trả về:

```python
novel = {
    "title": "Tiên Nghịch",
    "author": "Nhĩ Căn",
    "url": "https://example.com/tien-nghich",
}
```

Repository có thể thực hiện:

```python
cursor.execute(
    """
    INSERT INTO novels (title, author, url)
    VALUES (?, ?, ?)
    """,
    (
        novel["title"],
        novel["author"],
        novel["url"],
    ),
)

novel_id = cursor.lastrowid
```

Sau đó:

```python
print(novel_id)
```

Ví dụ:

```text
42
```

Application layer có thể biết:

```text
Novel được tạo với ID = 42
```

---

# 19. Một lỗi rất thường gặp

Sai:

```python
cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    "Tiên Nghịch",
    "Nhĩ Căn",
)
```

`execute()` nhận parameter sequence như một đối số.

Đúng:

```python
cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)
```

---

# 20. Một lỗi khác

Sai:

```python
cursor.execute(
    "INSERT INTO novels (title) VALUES (?)",
    ("Tiên Nghịch")
)
```

Vì:

```python
("Tiên Nghịch")
```

là `str`.

Đúng:

```python
cursor.execute(
    "INSERT INTO novels (title) VALUES (?)",
    ("Tiên Nghịch",),
)
```

---

# 21. `INSERT` nhiều records — pattern nên nhớ

Đây là pattern bạn nên thuộc:

```python
rows = [
    ("Novel A", "Author A"),
    ("Novel B", "Author B"),
    ("Novel C", "Author C"),
]

cursor.executemany(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    rows,
)

conn.commit()
```

---

# 22. Mini project cuối Buổi 3

Viết chương trình:

```text
novel_db.py
```

Tạo:

```sql
CREATE TABLE IF NOT EXISTS novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    url TEXT NOT NULL UNIQUE
);
```

Sau đó:

```python
novels = [
    (
        "Đấu Phá Thương Khung",
        "Thiên Tằm Thổ Đậu",
        "https://example.com/dau-pha",
    ),
    (
        "Phàm Nhân Tu Tiên",
        "Vong Ngữ",
        "https://example.com/pham-nhan",
    ),
    (
        "Tiên Nghịch",
        "Nhĩ Căn",
        "https://example.com/tien-nghich",
    ),
]
```

Insert bằng:

```python
executemany()
```

Sau đó:

```python
cursor.execute("SELECT * FROM novels")

for row in cursor.fetchall():
    print(row)
```

Kết quả mong muốn:

```text
(1, 'Đấu Phá Thương Khung', 'Thiên Tằm Thổ Đậu', ...)
(2, 'Phàm Nhân Tu Tiên', 'Vong Ngữ', ...)
(3, 'Tiên Nghịch', 'Nhĩ Căn', ...)
```

---

# 23. Bài tập nâng cao

Sau khi insert thành công, hãy thử insert lại:

```python
(
    "Tiên Nghịch bản sao",
    "Someone",
    "https://example.com/tien-nghich",
)
```

Bạn sẽ gặp:

```text
UNIQUE constraint failed
```

Hãy tự giải thích:

```text
url
 ↓
UNIQUE
 ↓
URL đã tồn tại
 ↓
INSERT thất bại
```

Đây là một bài tập rất quan trọng vì nó nối:

```text
Buổi 2
Constraint
    ↓
Buổi 3
INSERT
    ↓
Transaction
```

---

# 24. Tổng kết Buổi 3

Bạn cần nắm chắc:

```text
INSERT INTO
      ↓
Parameterized Query
      ↓
?
      ↓
lastrowid
      ↓
executemany()
      ↓
commit()
      ↓
rollback()
```

Đặc biệt hãy hình thành **3 thói quen**:

### ① Luôn parameterize dữ liệu

```python
cursor.execute(
    "INSERT INTO novels (title) VALUES (?)",
    (title,),
)
```

### ② Batch insert dùng `executemany()`

```python
cursor.executemany(sql, rows)
```

### ③ Ghi dữ liệu phải suy nghĩ về transaction

```text
BEGIN
 ↓
operations
 ↓
COMMIT

hoặc

ROLLBACK
```

---

## Chuẩn bị cho Buổi 4

Buổi tiếp theo chúng ta sẽ học **`SELECT` thật kỹ**:

```sql
SELECT
FROM
WHERE
ORDER BY
LIMIT
OFFSET
```

Sau đó sẽ chuyển từ:

```text
"lấy toàn bộ database"
```

sang các truy vấn thực tế như:

```sql
-- Tìm novel theo ID
SELECT ...

-- Tìm novel theo title
SELECT ...

-- Lấy 20 novel mới nhất
SELECT ...

-- Tìm chapter của một novel
SELECT ...

-- Phân trang danh sách chapter
SELECT ...
LIMIT ...
OFFSET ...
```

Đây là lúc SQL bắt đầu trở nên thực sự hữu ích cho **Novel Repository**.
