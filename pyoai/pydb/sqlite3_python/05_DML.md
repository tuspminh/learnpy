# Buổi 5: DML - INSERT INTO (Thêm dữ liệu)

> Đây là buổi học đầu tiên chúng ta **làm việc với dữ liệu thật**.
> 
> Những buổi trước chúng ta chỉ xây dựng "ngôi nhà" (Database và Table).
> 
> Hôm nay chúng ta sẽ bắt đầu **đưa dữ liệu vào ngôi nhà đó**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ thành thạo:

- INSERT là gì
- Thêm một dòng dữ liệu
- Thêm nhiều dòng dữ liệu
- Chỉ định tên cột khi INSERT
- Giá trị NULL
- Giá trị mặc định (DEFAULT)
- AUTOINCREMENT hoạt động thế nào
- INSERT bằng Python
- executemany()
- Những lỗi rất hay gặp

---

# 1. DML là gì?

DML (Data Manipulation Language)

Là nhóm câu lệnh dùng để thao tác dữ liệu.

Bao gồm

```text-x-trilium-auto
INSERT

UPDATE

DELETE
```

Hôm nay học

```text-x-trilium-auto
INSERT
```

---

# 2. Chuẩn bị Database

Giả sử ta có bảng

```text-x-trilium-auto
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

Hiện tại

```text-x-trilium-auto
students
```

là bảng rỗng.

---

# 3. INSERT là gì?

INSERT dùng để thêm dữ liệu.

Giống như thêm một dòng mới vào Excel.

Ví dụ

Trước

| id  | name | age |
| --- | --- | --- |
| (rỗng) |     | (rỗng) |

Sau

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 20  |

---

# 4. Cú pháp chuẩn

```text-x-trilium-auto
INSERT INTO table_name (
    column1,
    column2
)
VALUES (
    value1,
    value2
);
```

Ví dụ

```text-x-trilium-auto
INSERT INTO students(
    name,
    age
)
VALUES(
    'An',
    20
);
```

Kết quả

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 20  |

Lưu ý

Không cần nhập

```text-x-trilium-auto
id
```

vì

```text-x-trilium-auto
AUTOINCREMENT
```

tự tạo.

---

# 5. Có bắt buộc ghi tên cột không?

Không.

Bạn có thể viết

```text-x-trilium-auto
INSERT INTO students
VALUES(
    NULL,
    'Bình',
    21
);
```

SQLite hiểu

```text-x-trilium-auto
NULL
```

ở cột id

↓

tự sinh id.

Kết quả

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 20  |
| 2   | Bình | 21  |

---

## Nhưng...

Trong lập trình chuyên nghiệp

**KHÔNG NÊN** viết như trên.

Vì sao?

Giả sử sau này bảng thành

```text-x-trilium-auto
id

name

email

age
```

Thì câu lệnh

```text-x-trilium-auto
INSERT INTO students
VALUES(...)
```

sẽ hỏng.

Do số lượng cột thay đổi.

---

## Luôn luôn viết

```text-x-trilium-auto
INSERT INTO students(
    name,
    age
)
VALUES(
    'Lan',
    19
);
```

Đây là chuẩn của hầu hết dự án lớn.

---

# 6. INSERT nhiều dòng

SQLite cho phép

```text-x-trilium-auto
INSERT INTO students(
    name,
    age
)
VALUES
('Mai',20),
('Hoa',22),
('Nam',18);
```

Kết quả

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 20  |
| 2   | Bình | 21  |
| 3   | Lan | 19  |
| 4   | Mai | 20  |
| 5   | Hoa | 22  |
| 6   | Nam | 18  |

Nhanh hơn nhiều so với viết nhiều câu lệnh `INSERT`.

---

# 7. NULL

Giả sử

```text-x-trilium-auto
CREATE TABLE employees(
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT
);
```

Có người chưa có số điện thoại

```text-x-trilium-auto
INSERT INTO employees(
    name,
    phone
)
VALUES(
    'An',
    NULL
);
```

Kết quả

| name | phone |
| --- | --- |
| An  | NULL |

NULL có nghĩa là **chưa có giá trị**, khác với chuỗi rỗng (`''`).

---

# 8. DEFAULT

Tạo bảng

```text-x-trilium-auto
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    active INTEGER DEFAULT 1
);
```

Thêm

```text-x-trilium-auto
INSERT INTO users(
    username
)
VALUES(
    'admin'
);
```

SQLite tự thêm

```text-x-trilium-auto
active=1
```

Kết quả

| username | active |
| --- | --- |
| admin | 1   |

---

# 9. AUTOINCREMENT hoạt động thế nào?

Ví dụ

```text-x-trilium-auto
1

2

3

4
```

Nếu xóa

```text-x-trilium-auto
3
```

rồi thêm người mới

ID mới sẽ là

```text-x-trilium-auto
5
```

không phải

```text-x-trilium-auto
3
```

SQLite **không tái sử dụng** ID khi dùng `AUTOINCREMENT`.

---

# 10. INSERT bằng Python

Đây là cách cơ bản.

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute("""
INSERT INTO students(
    name,
    age
)
VALUES(
    'An',
    20
)
""")

conn.commit()

conn.close()
```

Sau khi chạy

Database có thêm

```text-x-trilium-auto
An
```

---

# 11. Đừng nối chuỗi SQL

Nhiều người mới học viết

```text-x-trilium-auto
name = "An"

sql = f"""
INSERT INTO students(name)
VALUES('{name}')
"""
```

Có vẻ đúng.

Nhưng đây là **thói quen rất nguy hiểm**.

Ví dụ

```text-x-trilium-auto
name = "'; DROP TABLE students;--"
```

Có thể dẫn đến tấn công SQL Injection trên nhiều hệ quản trị cơ sở dữ liệu.

Trong SQLite với `sqlite3.execute()` mặc định, một câu lệnh không thể chứa nhiều lệnh SQL nên ví dụ trên không trực tiếp xóa bảng. Tuy nhiên, **nối chuỗi SQL vẫn là cách làm sai** vì dễ gây lỗi cú pháp và không an toàn khi chuyển sang các DBMS khác.

---

# 12. Cách đúng

SQLite hỗ trợ placeholder

```text-x-trilium-auto
cursor.execute(
    """
    INSERT INTO students(
        name,
        age
    )
    VALUES(?,?)
    """,
    ("An",20)
)
```

Dấu

```text-x-trilium-auto
?
```

là placeholder.

Đây là cách **duy nhất bạn nên dùng trong ứng dụng thực tế**.

---

# 13. Thêm nhiều dòng bằng Python

Thay vì

```text-x-trilium-auto
cursor.execute(...)
cursor.execute(...)
cursor.execute(...)
```

Hãy dùng

```text-x-trilium-auto
students = [
    ("An",20),
    ("Bình",21),
    ("Lan",19),
]
```

Sau đó

```text-x-trilium-auto
cursor.executemany(
    """
    INSERT INTO students(
        name,
        age
    )
    VALUES(?,?)
    """,
    students
)

conn.commit()
```

`executemany()` giúp mã nguồn ngắn gọn và hiệu quả hơn khi chèn nhiều bản ghi.

---

# 14. lastrowid

Sau khi INSERT

SQLite biết ID vừa tạo.

```text-x-trilium-auto
cursor.execute(
    """
    INSERT INTO students(
        name,
        age
    )
    VALUES(?,?)
    """,
    ("Nam",22)
)

print(cursor.lastrowid)
```

Ví dụ

```text-x-trilium-auto
7
```

Đây là ID của bản ghi vừa được thêm.

---

# 15. Tổng kết INSERT

```text-x-trilium-auto
INSERT

↓

Tạo Row mới

↓

SQLite tự sinh PRIMARY KEY

↓

commit()

↓

Lưu xuống file
```

---

# Những lỗi rất thường gặp

## Quên commit()

```text-x-trilium-auto
conn.commit()
```

Không gọi `commit()` thì dữ liệu có thể không được lưu.

---

## Thiếu dấu nháy

Sai

```text-x-trilium-auto
VALUES(
An,
20
)
```

Đúng

```text-x-trilium-auto
VALUES(
'An',
20
)
```

---

## Sai số lượng cột

Sai

```text-x-trilium-auto
INSERT INTO students(
name
)
VALUES(
'An',
20
);
```

Một cột nhưng hai giá trị.

SQLite sẽ báo lỗi.

---

## Không dùng placeholder

Sai

```text-x-trilium-auto
sql = f"..."
```

Đúng

```text-x-trilium-auto
cursor.execute(sql, values)
```

---

# Tổng kết buổi 5

Hôm nay bạn đã học được:

- DML là gì.
- `INSERT INTO`.
- Thêm một dòng và nhiều dòng dữ liệu.
- Vì sao nên luôn chỉ định tên cột.
- `NULL`.
- `DEFAULT`.
- `AUTOINCREMENT`.
- `cursor.execute()`.
- `cursor.executemany()`.
- `cursor.lastrowid`.
- Vì sao phải dùng placeholder (`?`) thay vì nối chuỗi SQL.

---

# Bài tập

## Bài 1

Tạo bảng

```text-x-trilium-auto
CREATE TABLE books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price REAL
);
```

Thêm 5 quyển sách.

---

## Bài 2

Viết chương trình Python

- kết nối SQLite
- thêm một sinh viên
- commit
- close

---

## Bài 3

Sử dụng `executemany()` để thêm 20 sinh viên.

---

## Bài 4

Sau mỗi lần INSERT

In ra

```text-x-trilium-auto
cursor.lastrowid
```

để xem ID vừa sinh.

---

# Thử thách

Viết hàm Python:

```text-x-trilium-auto
def add_student(name: str, age: int):
    ...
```

Yêu cầu:

- Kết nối SQLite.
- Thêm sinh viên bằng placeholder (`?`).
- `commit()`.
- Trả về `id` vừa được tạo (`cursor.lastrowid`).
- Đảm bảo luôn đóng kết nối ngay cả khi xảy ra lỗi (gợi ý: dùng `try/finally` hoặc `with` khi chúng ta học ở các buổi sau).

---

## Chuẩn bị cho buổi 6

Ở **Buổi 6**, chúng ta sẽ học câu lệnh được sử dụng nhiều nhất trong SQL: `**SELECT**`.

Bạn sẽ học cách:

- Đọc dữ liệu từ bảng.
- Chỉ lấy các cột cần thiết.
- Đặt bí danh (`AS`) cho cột.
- Biểu thức trong `SELECT`.
- Hàm `DISTINCT`.
- Và cách lấy dữ liệu bằng Python với `fetchone()`, `fetchmany()` và `fetchall()` (chúng ta sẽ còn tìm hiểu sâu hơn ở phần Python của khóa học). Đây là bước đầu tiên để xây dựng các chức năng tìm kiếm và hiển thị dữ liệu trong ứng dụng.