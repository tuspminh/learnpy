# Buổi 2 — `CREATE TABLE` và kiểu dữ liệu SQLite

Hôm nay chúng ta đi sâu vào **thiết kế bảng**. Đây là phần rất quan trọng, vì một database tốt bắt đầu từ schema tốt.

---

# 1. `CREATE TABLE`

Cú pháp cơ bản:

```sql
CREATE TABLE table_name (
    column1 datatype,
    column2 datatype,
    column3 datatype
);
```

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER,
    title TEXT,
    author TEXT
);
```

Ta có:

```text
novels
│
├── id
├── title
└── author
```

---

# 2. SQLite có kiểu dữ liệu hơi khác MySQL/PostgreSQL

SQLite không ép kiểu cứng theo cách bạn có thể đã thấy ở các DBMS khác.

Các storage class chính của SQLite là:

```text
NULL
INTEGER
REAL
TEXT
BLOB
```

Đây là **5 kiểu lưu trữ cơ bản**.

---

## `INTEGER`

Dùng cho số nguyên:

```sql
id INTEGER
```

Ví dụ:

```text
1
2
100
9999
```

Thường dùng cho:

```text
id
chapter_number
view_count
download_count
```

---

## `REAL`

Dùng cho số thực:

```sql
rating REAL
```

Ví dụ:

```text
8.5
9.25
7.0
```

---

## `TEXT`

Dùng cho chuỗi:

```sql
title TEXT
```

Ví dụ:

```text
"Đấu Phá Thương Khung"
"Tiên Nghịch"
"Vong Ngữ"
```

Trong project crawler của bạn, `TEXT` sẽ được dùng rất nhiều:

```text
title
author
url
slug
description
content
status
```

---

## `BLOB`

Dùng cho dữ liệu binary.

Ví dụ:

```text
ảnh
file
binary data
```

Trong app đọc truyện thông thường, bạn có thể ít dùng BLOB vì thường tốt hơn khi lưu:

```text
image_url
```

thay vì nhét toàn bộ ảnh vào SQLite.

---

## `NULL`

`NULL` nghĩa là:

> Không có giá trị.

Nó **không giống**:

```text
0
""
False
```

Ví dụ:

```sql
author TEXT
```

có thể có:

```text
"Vong Ngữ"
```

hoặc:

```text
NULL
```

---

# 3. `PRIMARY KEY`

Đây là constraint cực kỳ quan trọng.

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT
);
```

`id` là định danh duy nhất của mỗi row.

```text
id | title
---+----------------------
1  | Đấu Phá Thương Khung
2  | Tiên Nghịch
3  | Phàm Nhân Tu Tiên
```

Không nên có:

```text
1 | Novel A
1 | Novel B
```

---

# 4. SQLite có một đặc điểm rất quan trọng

Với:

```sql
id INTEGER PRIMARY KEY
```

SQLite có cơ chế đặc biệt liên quan đến `rowid`.

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Khi:

```sql
INSERT INTO novels (title)
VALUES ('Tiên Nghịch');
```

không truyền `id`, SQLite có thể tự cấp:

```text
1 | Tiên Nghịch
```

Tiếp tục:

```sql
INSERT INTO novels (title)
VALUES ('Phàm Nhân Tu Tiên');
```

sẽ có:

```text
1 | Tiên Nghịch
2 | Phàm Nhân Tu Tiên
```

Đây là pattern chúng ta sẽ dùng rất nhiều.

---

# 5. `NOT NULL`

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Nghĩa là:

> `title` bắt buộc phải có giá trị.

Được:

```sql
INSERT INTO novels (title)
VALUES ('Tiên Nghịch');
```

Không được:

```sql
INSERT INTO novels (title)
VALUES (NULL);
```

SQLite sẽ báo lỗi constraint.

---

# 6. `UNIQUE`

`UNIQUE` yêu cầu giá trị không được trùng.

Ví dụ:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE
);
```

Ta có:

```text
id | title       | url
---+-------------+-------------------
1  | Tiên Nghịch | https://site/a
```

Không thể thêm:

```text
2 | Novel B | https://site/a
```

vì URL đã tồn tại.

Trong crawler, `UNIQUE` cực kỳ hữu ích.

Ví dụ:

```sql
url TEXT NOT NULL UNIQUE
```

giúp ngăn crawler lưu cùng một truyện nhiều lần.

---

# 7. `DEFAULT`

Cho giá trị mặc định.

Ví dụ:

```sql
status TEXT NOT NULL DEFAULT 'ongoing'
```

Khi:

```sql
INSERT INTO novels (title)
VALUES ('Tiên Nghịch');
```

SQLite tự hiểu:

```text
title  = Tiên Nghịch
status = ongoing
```

Ta không cần:

```sql
INSERT INTO novels (title, status)
VALUES ('Tiên Nghịch', 'ongoing');
```

---

# 8. `CHECK`

`CHECK` dùng để giới hạn giá trị hợp lệ.

Ví dụ:

```sql
status TEXT NOT NULL
CHECK (status IN ('ongoing', 'completed'))
```

Như vậy:

```text
ongoing
completed
```

hợp lệ.

Nhưng:

```text
abc
unknown
hello
```

không hợp lệ.

Đây chính là một phần của **database-level validation**.

---

# 9. Kết hợp các constraint

Ta có thể viết:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'ongoing'
        CHECK (status IN ('ongoing', 'completed'))
);
```

Đây đã là một schema khá thực tế.

---

# 10. Thiết kế bảng `novels`

Cho app crawler của bạn, ta có thể bắt đầu:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    url TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'ongoing'
);
```

Ví dụ dữ liệu:

```text
id | title                | author      | url       | status
---+----------------------+-------------+-----------+----------
1  | Đấu Phá Thương Khung | Thiên Tằm   | site/a    | completed
2  | Tiên Nghịch          | Nhĩ Căn     | site/b    | ongoing
```

---

# 11. Python tạo schema

```python
import sqlite3


conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        url TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'ongoing'
            CHECK (status IN ('ongoing', 'completed'))
    )
""")

conn.commit()
conn.close()
```

Đây là code chúng ta sẽ tiếp tục phát triển ở các buổi sau.

---

# 12. Thử constraint `NOT NULL`

```python
cursor.execute("""
    INSERT INTO novels (author, url)
    VALUES ('Vong Ngữ', 'https://example.com/a')
""")
```

Lỗi vì:

```text
title = NULL
```

trong khi:

```sql
title TEXT NOT NULL
```

Database tự bảo vệ dữ liệu.

---

# 13. Thử `UNIQUE`

Lần đầu:

```python
cursor.execute("""
    INSERT INTO novels (title, url)
    VALUES ('Tiên Nghịch', 'https://example.com/a')
""")
```

OK.

Lần hai:

```python
cursor.execute("""
    INSERT INTO novels (title, url)
    VALUES ('Novel khác', 'https://example.com/a')
""")
```

Lỗi vì:

```text
url
 ↓
UNIQUE
 ↓
không được trùng
```

---

# 14. Thử `DEFAULT`

```python
cursor.execute("""
    INSERT INTO novels (title, url)
    VALUES ('Tiên Nghịch', 'https://example.com/tien-nghich')
""")
```

Sau đó:

```sql
SELECT * FROM novels;
```

Ta sẽ có:

```text
id | title       | author | url                    | status
---+-------------+--------+------------------------+---------
1  | Tiên Nghịch | NULL   | ...                    | ongoing
```

`status` tự động là:

```text
ongoing
```

---

# 15. `NULL` cần đặc biệt chú ý

Đừng viết:

```sql
WHERE author = NULL
```

Sai về mặt logic SQL.

Phải viết:

```sql
WHERE author IS NULL
```

và:

```sql
WHERE author IS NOT NULL
```

Đây là một lỗi người mới học SQL rất thường gặp.

---

# 16. Schema tốt ≠ chỉ khai báo kiểu dữ liệu

Ví dụ schema yếu:

```sql
CREATE TABLE novels (
    id INTEGER,
    title TEXT,
    url TEXT,
    status TEXT
);
```

Database gần như không bảo vệ gì.

Có thể xảy ra:

```text
id = NULL
title = NULL
url = NULL
status = "abcdef"
```

Schema tốt hơn:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'ongoing'
        CHECK (status IN ('ongoing', 'completed'))
);
```

Bây giờ database tự bảo vệ:

```text
PRIMARY KEY → identity
NOT NULL    → bắt buộc
UNIQUE      → không trùng
DEFAULT     → giá trị mặc định
CHECK       → giới hạn domain
```

Đây là tư duy rất quan trọng:

> **Đừng chỉ validate ở Python. Những invariant quan trọng nên được database bảo vệ nếu có thể.**

---

# 17. Database constraint và Python validation

Ví dụ Python có:

```python
if status not in {"ongoing", "completed"}:
    raise ValueError("Invalid status")
```

Điều này tốt.

Nhưng database cũng nên có:

```sql
CHECK (status IN ('ongoing', 'completed'))
```

Tại sao?

Vì có thể có nhiều nơi ghi database:

```text
CLI
 │
 ├── Repository
 │
 ├── Migration
 │
 ├── Script
 │
 └── Admin tool
```

Nếu chỉ Python kiểm tra, một code path khác có thể phá dữ liệu.

Database constraint là **lớp bảo vệ cuối cùng**.

---

# 18. Một schema thực tế hơn

Cuối buổi, tôi muốn bạn bắt đầu suy nghĩ theo schema này:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    slug TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ongoing'
        CHECK (status IN ('ongoing', 'completed')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    UNIQUE (source, slug)
);
```

Chú ý dòng:

```sql
UNIQUE (source, slug)
```

Đây là **composite UNIQUE constraint**.

Nó có nghĩa:

```text
source + slug
```

phải là duy nhất.

Ví dụ:

```text
source A + tien-nghich   → OK
source B + tien-nghich   → OK
source A + tien-nghich   → trùng
```

Điều này cực kỳ phù hợp khi crawler nhiều website.

---

# 19. Kiến thức cần ghi nhớ

Sau Buổi 2, hãy nhớ mô hình:

```text
CREATE TABLE
      │
      ├── column
      │      │
      │      └── datatype
      │
      └── constraint
             │
             ├── PRIMARY KEY
             ├── NOT NULL
             ├── UNIQUE
             ├── DEFAULT
             └── CHECK
```

Và 5 storage class của SQLite:

```text
NULL
INTEGER
REAL
TEXT
BLOB
```

---

# Bài tập Buổi 2

Tự thiết kế bảng:

```text
novels
chapters
```

### `novels`

Yêu cầu:

```text
id
source
title
author
url
status
```

Trong đó:

* `id` là primary key
* `title` bắt buộc
* `source` bắt buộc
* `url` bắt buộc
* `url` không được trùng
* `status` mặc định là `ongoing`
* `status` chỉ được `ongoing` hoặc `completed`

### `chapters`

Yêu cầu:

```text
id
novel_id
chapter_number
title
url
content
```

Chưa cần `FOREIGN KEY` ở bài này — **Buổi 3 chúng ta sẽ tập trung vào `INSERT` và parameterized query**, sau đó mới sang quan hệ `novels → chapters`.

### Câu hỏi tự kiểm tra

1. `INTEGER PRIMARY KEY` có ý nghĩa gì trong SQLite?
2. `TEXT NOT NULL` khác `TEXT` thế nào?
3. `UNIQUE` dùng để làm gì?
4. `DEFAULT` hoạt động lúc nào?
5. `CHECK` dùng để làm gì?
6. `NULL` khác `""` như thế nào?
7. Tại sao `WHERE author = NULL` sai?
8. Tại sao crawler nên có `UNIQUE` cho URL?

**Buổi 3 → `INSERT` + parameterized query + `executemany()` + `lastrowid` + chống SQL Injection.**
