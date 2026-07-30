# Buổi 6: DQL - SELECT (Truy vấn dữ liệu)

> Đây là buổi học quan trọng nhất từ đầu khóa đến giờ.
> 
> **90% các câu lệnh SQL trong công việc hằng ngày đều là** `**SELECT**`**.**
> 
> Nếu INSERT là "ghi dữ liệu", thì SELECT là "đọc dữ liệu".

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ thành thạo:

- SELECT là gì
- SELECT *
- Chọn một hoặc nhiều cột
- AS (Alias)
- DISTINCT
- Biểu thức trong SELECT
- LIMIT
- ORDER BY (giới thiệu, học sâu ở buổi sau)
- SELECT trong Python
- fetchone()
- fetchall()

---

# 1. DQL là gì?

DQL = Data Query Language

Nhóm câu lệnh dùng để **đọc dữ liệu**.

Trong SQLite, câu lệnh quan trọng nhất là:

```text-x-trilium-auto
SELECT
```

---

# 2. Chuẩn bị dữ liệu

Giả sử bảng:

```text-x-trilium-auto
CREATE TABLE students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    city TEXT
);
```

Có dữ liệu

| id  | name | age | city |
| --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội |
| 2   | Bình | 22  | Huế |
| 3   | Lan | 19  | Đà Nẵng |
| 4   | Mai | 20  | Huế |

---

# 3. SELECT *

Câu lệnh đơn giản nhất

```text-x-trilium-auto
SELECT * FROM students;
```

Dấu

```text-x-trilium-auto
*
```

nghĩa là

> Lấy tất cả các cột.

Kết quả

| id  | name | age | city |
| --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội |
| 2   | Bình | 22  | Huế |
| 3   | Lan | 19  | Đà Nẵng |
| 4   | Mai | 20  | Huế |

---

## SELECT * có nên dùng không?

Trong quá trình học

✔ Được.

Trong dự án thực tế

❌ Hạn chế.

Ví dụ

Bảng có

```text-x-trilium-auto
30 cột
```

Nhưng bạn chỉ cần

```text-x-trilium-auto
name
```

Việc lấy cả 30 cột sẽ:

- Tốn bộ nhớ
- Tốn thời gian truyền dữ liệu
- Làm chương trình chậm hơn

---

# 4. Chọn một cột

```text-x-trilium-auto
SELECT name
FROM students;
```

Kết quả

| name |
| --- |
| An  |
| Bình |
| Lan |
| Mai |

---

# 5. Chọn nhiều cột

```text-x-trilium-auto
SELECT
    name,
    city
FROM students;
```

Kết quả

| name | city |
| --- | --- |
| An  | Hà Nội |
| Bình | Huế |
| Lan | Đà Nẵng |
| Mai | Huế |

---

# 6. Alias (AS)

Đôi khi tên cột quá dài.

Ví dụ

```text-x-trilium-auto
SELECT
    name AS student_name,
    city AS address
FROM students;
```

Kết quả

| student_name | address |
| --- | --- |
| An  | Hà Nội |

Tên cột chỉ đổi **trong kết quả truy vấn**, không làm thay đổi cấu trúc bảng.

---

# 7. AS có bắt buộc không?

Không.

Hai câu sau giống nhau:

```text-x-trilium-auto
SELECT name AS student_name
FROM students;
```

và

```text-x-trilium-auto
SELECT name student_name
FROM students;
```

Tuy nhiên, nên dùng `AS` để câu lệnh rõ ràng và dễ đọc.

---

# 8. DISTINCT

Giả sử

| city |
| --- |
| Huế |
| Huế |
| Hà Nội |
| Huế |
| Đà Nẵng |

Nếu

```text-x-trilium-auto
SELECT city
FROM students;
```

Kết quả sẽ có giá trị lặp.

Nếu

```text-x-trilium-auto
SELECT DISTINCT city
FROM students;
```

Kết quả

| city |
| --- |
| Huế |
| Hà Nội |
| Đà Nẵng |

`DISTINCT` loại bỏ các dòng trùng lặp trong kết quả truy vấn.

---

# 9. DISTINCT nhiều cột

```text-x-trilium-auto
SELECT DISTINCT
    city,
    age
FROM students;
```

Lúc này SQLite sẽ loại bỏ các **cặp (**`**city**`**,** `**age**`**)** trùng nhau, chứ không xét riêng từng cột.

---

# 10. Biểu thức trong SELECT

Bạn có thể tính toán trực tiếp.

```text-x-trilium-auto
SELECT
    name,
    age + 1 AS next_year_age
FROM students;
```

Kết quả

| name | next_year_age |
| --- | --- |
| An  | 21  |
| Bình | 23  |

SQLite tính toán trước khi trả kết quả.

---

# 11. Nối chuỗi

```text-x-trilium-auto
SELECT
    'Xin chào ' || name
FROM students;
```

Kết quả

| Kết quả |
| --- |
| Xin chào An |
| Xin chào Bình |

Trong SQLite:

```text-x-trilium-auto
||
```

là toán tử nối chuỗi.

---

# 12. Hàm LENGTH()

```text-x-trilium-auto
SELECT
    name,
    LENGTH(name)
FROM students;
```

Ví dụ

| name | LENGTH(name) |
| --- | --- |
| An  | 2   |
| Bình | 4   |

Chúng ta sẽ học kỹ các hàm ở buổi 11.

---

# 13. LIMIT

Muốn lấy 2 dòng đầu tiên

```text-x-trilium-auto
SELECT * FROM students
LIMIT 2;
```

Kết quả

| id  | name |
| --- | --- |
| 1   | An  |
| 2   | Bình |

`LIMIT` rất hữu ích khi xem thử dữ liệu hoặc phân trang.

---

# 14. ORDER BY (Giới thiệu)

Ví dụ

```text-x-trilium-auto
SELECT * FROM students
ORDER BY age;
```

SQLite sắp xếp theo tuổi tăng dần.

Chúng ta sẽ học chi tiết ở buổi 8.

---

# 15. SELECT trong Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM students
""")
```

Lúc này

SQLite **chưa trả dữ liệu ngay**.

Bạn phải gọi một trong các hàm `fetch...()`.

---

# 16. fetchone()

```text-x-trilium-auto
row = cursor.fetchone()

print(row)
```

Ví dụ

```text-x-trilium-auto
(1, 'An', 20, 'Hà Nội')
```

Gọi lần thứ hai

```text-x-trilium-auto
row = cursor.fetchone()
```

sẽ lấy dòng tiếp theo

```text-x-trilium-auto
(2, 'Bình', 22, 'Huế')
```

Con trỏ (cursor) di chuyển từng dòng một.

---

# 17. fetchall()

```text-x-trilium-auto
rows = cursor.fetchall()

print(rows)
```

Kết quả

```text-x-trilium-auto
[
    (1,'An',20,'Hà Nội'),
    (2,'Bình',22,'Huế'),
    (3,'Lan',19,'Đà Nẵng')
]
```

Kiểu dữ liệu

```text-x-trilium-auto
list
```

bên trong là

```text-x-trilium-auto
tuple
```

---

# 18. Duyệt kết quả

```text-x-trilium-auto
rows = cursor.fetchall()

for row in rows:
    print(row)
```

Hoặc

```text-x-trilium-auto
for id_, name, age, city in rows:
    print(name, age)
```

---

# 19. Ví dụ hoàn chỉnh

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    name,
    age
FROM students
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

Kết quả

```text-x-trilium-auto
(1, 'An', 20)
(2, 'Bình', 22)
(3, 'Lan', 19)
```

---

# 20. Sơ đồ hoạt động

```text-x-trilium-auto
Python

↓

execute()

↓

SQLite

↓

SELECT

↓

Result Set

↓

fetchone()

hoặc

fetchall()

↓

Python
```

---

# Những lỗi thường gặp

## 1. Quên fetch

Sai

```text-x-trilium-auto
cursor.execute("SELECT * FROM students")

print(cursor)
```

Bạn chỉ in ra đối tượng `Cursor`, không phải dữ liệu.

Đúng

```text-x-trilium-auto
rows = cursor.fetchall()
```

---

## 2. SELECT *

Không nên

```text-x-trilium-auto
SELECT *
```

khi chỉ cần

```text-x-trilium-auto
SELECT name
```

---

## 3. Đóng kết nối quá sớm

Sai

```text-x-trilium-auto
conn.close()

rows = cursor.fetchall()
```

Luôn lấy dữ liệu trước khi đóng kết nối.

---

# Tổng kết buổi 6

Bạn đã học được:

- DQL là gì.
- `SELECT *`.
- Chọn một hoặc nhiều cột.
- `AS` để đặt bí danh.
- `DISTINCT` để loại bỏ kết quả trùng lặp.
- Biểu thức và nối chuỗi trong `SELECT`.
- `LIMIT`.
- Giới thiệu `ORDER BY`.
- `fetchone()`.
- `fetchall()`.
- Quy trình lấy dữ liệu bằng Python.

---

# Bài tập

## Bài 1

Viết câu lệnh lấy:

- tất cả sinh viên
- chỉ tên sinh viên
- tên và tuổi sinh viên

---

## Bài 2

Sử dụng

```text-x-trilium-auto
DISTINCT
```

để lấy danh sách các thành phố không trùng.

---

## Bài 3

Viết câu lệnh

```text-x-trilium-auto
SELECT
    name,
    age + 5 FROM students;
```

Đặt tên cột mới là `age_after_5_years`.

---

## Bài 4

Viết chương trình Python:

- Kết nối `student.db`.
- Thực hiện `SELECT id, name, age FROM students`.
- In từng dòng ra màn hình bằng vòng lặp `for`.

---

## Bài 5 (Thử thách)

Viết hàm:

```text-x-trilium-auto
def get_all_students():
    ...
```

Yêu cầu:

- Trả về `list[tuple]` chứa tất cả sinh viên.
- Không in trực tiếp trong hàm.
- Đóng kết nối sau khi hoàn thành.
- Sử dụng `SELECT` chỉ lấy các cột `id`, `name`, `age` (không dùng `SELECT *`).

---

# Góc lập trình viên chuyên nghiệp

Ngay từ bây giờ hãy hình thành các thói quen tốt:

- ✅ Chỉ lấy những cột thực sự cần.
- ✅ Đặt bí danh (`AS`) khi giúp câu lệnh rõ nghĩa.
- ✅ Dùng `LIMIT` khi kiểm tra dữ liệu lớn.
- ✅ Tách phần truy vấn SQL và phần xử lý kết quả trong Python để mã nguồn dễ bảo trì.

Ở **Buổi 7**, chúng ta sẽ học `**WHERE**` — trái tim của việc tìm kiếm dữ liệu. Bạn sẽ biết cách lọc dữ liệu theo điều kiện, kết hợp nhiều điều kiện với `AND`, `OR`, `NOT`, sử dụng `LIKE`, `IN`, `BETWEEN`, và nhiều kỹ thuật truy vấn thực tế khác. Đây là một trong những chủ đề được sử dụng nhiều nhất trong mọi ứng dụng làm việc với cơ sở dữ liệu.