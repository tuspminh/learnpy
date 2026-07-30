# Buổi 4: DDL (Data Definition Language) – CREATE TABLE, ALTER TABLE, DROP TABLE

> **Mục tiêu buổi học**
> 
> Sau buổi này, bạn sẽ:
> 
> - Hiểu DDL là gì.
> - Thành thạo `CREATE TABLE`.
> - Biết cách đặt tên Database, Table, Column theo chuẩn.
> - Thành thạo `ALTER TABLE`.
> - Biết cách `DROP TABLE`.
> - Hiểu các hạn chế của `ALTER TABLE` trong SQLite.
> - Thiết kế được một bảng đúng chuẩn ngay từ đầu.

---

# 1. SQL được chia thành nhiều nhóm

Không phải tất cả câu lệnh SQL đều giống nhau.

SQL được chia thành nhiều nhóm chức năng.

| Nhóm | Chức năng |
| --- | --- |
| DDL | Tạo, sửa, xóa cấu trúc Database |
| DML | Thêm, sửa, xóa dữ liệu |
| DQL | Truy vấn dữ liệu |
| DCL | Phân quyền |
| TCL | Quản lý Transaction |

Trong buổi hôm nay chúng ta học **DDL**.

---

# 2. DDL là gì?

DDL = **Data Definition Language**

Đây là nhóm câu lệnh dùng để **định nghĩa cấu trúc** của cơ sở dữ liệu.

Ví dụ:

```text-x-trilium-auto
Tạo bảng

Đổi tên bảng

Thêm cột

Xóa bảng
```

DDL **không thao tác trên dữ liệu**, mà thao tác trên **cấu trúc**.

---

# Ví dụ

Giả sử bạn xây một ngôi nhà.

DDL giống như:

- xây phòng ngủ
- xây nhà bếp
- phá phòng khách
- mở rộng tầng

Còn dữ liệu (Data) là:

- bàn
- ghế
- tủ
- giường

---

# 3. CREATE TABLE

Đây là câu lệnh quan trọng nhất.

Cú pháp:

```text-x-trilium-auto
CREATE TABLE table_name (
    column1 datatype,
    column2 datatype,
    ...
);
```

Ví dụ:

```text-x-trilium-auto
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

SQLite sẽ tạo bảng:

```text-x-trilium-auto
students
```

gồm:

| Tên cột | Kiểu |
| --- | --- |
| id  | INTEGER |
| name | TEXT |
| age | INTEGER |

---

# 4. CREATE TABLE IF NOT EXISTS

Đây là cách nên dùng trong thực tế.

```text-x-trilium-auto
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

Nếu bảng đã tồn tại

➡ SQLite sẽ bỏ qua.

Không báo lỗi.

Đây là cách mà hầu hết các dự án Python chuyên nghiệp sử dụng khi khởi tạo cơ sở dữ liệu.

---

# 5. Quy tắc đặt tên

Một số lập trình viên mới thường đặt tên như:

```text-x-trilium-auto
Table1

ABC

Data

MyTable
```

Đây không phải cách đặt tên tốt.

Nên đặt theo ý nghĩa.

Ví dụ:

```text-x-trilium-auto
students

teachers

products

customers

orders
```

---

## Tên cột

Nên dùng:

```text-x-trilium-auto
student_name

birth_date

created_at

phone
```

Không nên:

```text-x-trilium-auto
a

b

c

name1

test
```

---

# Quy ước phổ biến

Dùng:

```text-x-trilium-auto
snake_case
```

Ví dụ:

```text-x-trilium-auto
student_name

phone_number

created_at
```

Không nên:

```text-x-trilium-auto
StudentName

PhoneNumber

CreatedAt
```

---

# 6. Ví dụ thiết kế bảng đúng chuẩn

```text-x-trilium-auto
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    gender TEXT,
    birth_date TEXT,
    phone TEXT,
    email TEXT,
    created_at TEXT
);
```

Đây là cấu trúc rõ ràng và dễ bảo trì.

---

# 7. ALTER TABLE

Sau khi tạo bảng, đôi khi cần thay đổi cấu trúc.

SQLite hỗ trợ:

- đổi tên bảng
- đổi tên cột
- thêm cột

---

## Đổi tên bảng

Ví dụ:

```text-x-trilium-auto
ALTER TABLE students
RENAME TO student;
```

Kết quả:

```text-x-trilium-auto
students
```

↓

```text-x-trilium-auto
student
```

---

## Đổi tên cột

Ví dụ:

```text-x-trilium-auto
ALTER TABLE student
RENAME COLUMN full_name TO name;
```

Kết quả:

```text-x-trilium-auto
full_name
```

↓

```text-x-trilium-auto
name
```

---

## Thêm cột

Ví dụ:

```text-x-trilium-auto
ALTER TABLE student
ADD COLUMN address TEXT;
```

Sau đó bảng sẽ có thêm:

```text-x-trilium-auto
address
```

---

# 8. SQLite KHÔNG hỗ trợ trực tiếp

Nhiều người mới học thường hỏi:

Có thể làm thế này không?

```text-x-trilium-auto
ALTER TABLE student
DROP COLUMN address;
```

Hiện nay các phiên bản SQLite mới đã hỗ trợ `DROP COLUMN`, nhưng trong thực tế bạn vẫn nên cẩn trọng vì còn phụ thuộc vào phiên bản SQLite đang sử dụng và các ràng buộc liên quan.

Ngoài ra, việc thay đổi kiểu dữ liệu của cột hoặc sửa các ràng buộc phức tạp thường **không thể thực hiện trực tiếp** bằng `ALTER TABLE` như trên nhiều DBMS khác.

Trong nhiều trường hợp, quy trình chuẩn là:

1. Tạo bảng mới với cấu trúc mong muốn.
2. Sao chép dữ liệu từ bảng cũ sang bảng mới.
3. Xóa bảng cũ.
4. Đổi tên bảng mới.

Chúng ta sẽ thực hành quy trình này ở các buổi nâng cao.

---

# 9. DROP TABLE

Nếu muốn xóa bảng.

```text-x-trilium-auto
DROP TABLE students;
```

Sau khi chạy.

Bảng biến mất hoàn toàn.

⚠ **Lưu ý:**

Toàn bộ dữ liệu cũng bị xóa.

Không thể hoàn tác nếu không có bản sao lưu.

---

## Cách an toàn

```text-x-trilium-auto
DROP TABLE IF EXISTS students;
```

Nếu bảng không tồn tại

SQLite không báo lỗi.

---

# 10. Ví dụ thực tế

Tạo bảng sản phẩm

```text-x-trilium-auto
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    price REAL,
    stock INTEGER
);
```

Sau vài tháng.

Bạn muốn thêm:

```text-x-trilium-auto
category
```

Chỉ cần:

```text-x-trilium-auto
ALTER TABLE products
ADD COLUMN category TEXT;
```

---

# 11. Thực hành bằng Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    price REAL,
    stock INTEGER
)
""")

conn.commit()
conn.close()

print("Tạo bảng thành công!")
```

---

# 12. Thêm cột bằng Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE products
ADD COLUMN category TEXT
""")

conn.commit()
conn.close()
```

---

# 13. Kiểm tra cấu trúc bảng

SQLite cung cấp lệnh:

```text-x-trilium-auto
PRAGMA table_info(products);
```

Ví dụ kết quả:

| cid | name | type | notnull | dflt_value | pk  |
| --- | --- | --- | --- | --- | --- |
| 0   | id  | INTEGER | 0   | NULL | 1   |
| 1   | product_name | TEXT | 0   | NULL | 0   |
| 2   | price | REAL | 0   | NULL | 0   |
| 3   | stock | INTEGER | 0   | NULL | 0   |
| 4   | category | TEXT | 0   | NULL | 0   |

Đây là cách rất hữu ích để kiểm tra cấu trúc bảng trong quá trình phát triển.

---

# 14. Sơ đồ tổng kết DDL

```text-x-trilium-auto
DDL

│

├── CREATE TABLE

├── ALTER TABLE

│      ├── RENAME TABLE
│      ├── RENAME COLUMN
│      └── ADD COLUMN

└── DROP TABLE
```

---

# Những lỗi thường gặp

### 1. Quên `IF NOT EXISTS`

```text-x-trilium-auto
CREATE TABLE students(...)
```

Nếu chạy lần hai sẽ báo:

```text-x-trilium-auto
table students already exists
```

Giải pháp:

```text-x-trilium-auto
CREATE TABLE IF NOT EXISTS students(...)
```

---

### 2. Đặt tên cột không rõ nghĩa

Không nên:

```text-x-trilium-auto
a
b
c
```

Nên:

```text-x-trilium-auto
full_name
email
created_at
```

---

### 3. Thiết kế bảng thiếu kế hoạch

Ví dụ:

```text-x-trilium-auto
name

name2

name3
```

Đây là dấu hiệu của thiết kế chưa tốt.

Nên dành thời gian phân tích dữ liệu trước khi tạo bảng.

---

# Tổng kết buổi 4

Bạn đã học:

- DDL là gì.
- `CREATE TABLE`.
- `CREATE TABLE IF NOT EXISTS`.
- Quy tắc đặt tên bảng và cột.
- `ALTER TABLE` để đổi tên bảng, đổi tên cột, thêm cột.
- `DROP TABLE`.
- `PRAGMA table_info()` để xem cấu trúc bảng.
- Những hạn chế của `ALTER TABLE` trong SQLite và cách xử lý trong thực tế.

---

# Bài tập thực hành

## Bài 1

Tạo cơ sở dữ liệu `library.db` và tạo bảng `books`:

```text-x-trilium-auto
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price REAL,
    stock INTEGER
);
```

---

## Bài 2

Thêm một cột mới:

```text-x-trilium-auto
published_year
```

có kiểu `INTEGER`.

---

## Bài 3

Đổi tên cột:

```text-x-trilium-auto
title
```

thành:

```text-x-trilium-auto
book_title
```

---

## Bài 4

Đổi tên bảng:

```text-x-trilium-auto
books
```

thành:

```text-x-trilium-auto
library_books
```

---

## Bài 5 (Thử thách)

Thiết kế cơ sở dữ liệu cho một **hệ thống quản lý bán hàng** gồm ít nhất 5 bảng:

- `customers`
- `products`
- `orders`
- `order_items`
- `categories`

Với mỗi bảng, hãy:

1. Liệt kê các cột.
2. Chọn kiểu dữ liệu phù hợp.
3. Xác định khóa chính (`PRIMARY KEY`).
4. Giải thích ngắn gọn lý do thiết kế.

> **Buổi 5** chúng ta sẽ chuyển sang nhóm lệnh **DML (Data Manipulation Language)**, bắt đầu với câu lệnh `INSERT INTO`. Bạn sẽ học nhiều cách thêm dữ liệu, chèn nhiều dòng cùng lúc và sử dụng Python để thêm dữ liệu an toàn bằng truy vấn có tham số (`parameterized query`). Đây là bước đầu tiên để xây dựng các ứng dụng Python làm việc với cơ sở dữ liệu.