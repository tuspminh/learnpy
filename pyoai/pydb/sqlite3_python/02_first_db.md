# Buổi 2: Tạo Database đầu tiên - Table, Row, Column và Kiểu dữ liệu trong SQLite

Đây là buổi học đầu tiên bạn **thực sự làm việc với SQLite**.

Sau buổi này, bạn sẽ có thể:

- ✅ Tạo một Database
- ✅ Tạo Table
- ✅ Hiểu Row, Column
- ✅ Hiểu Primary Key
- ✅ Hiểu AUTOINCREMENT
- ✅ Hiểu các kiểu dữ liệu của SQLite
- ✅ Tạo Database bằng cả **DB Browser** và **Python**

---

# Mục tiêu của buổi học

Cuối buổi bạn sẽ biết:

```text-x-trilium-auto
student.db
      │
      ├── students
      ├── classes
      └── scores
```

Đây chính là nền tảng cho toàn bộ khóa học.

---

# 1. Database là gì?

Trong SQLite,

**Database chỉ là một file.**

Ví dụ:

```text-x-trilium-auto
student.db
```

hoặc

```text-x-trilium-auto
shop.db
```

hoặc

```text-x-trilium-auto
hospital.db
```

Khác với MySQL hay PostgreSQL, SQLite **không cần cài đặt Server**.

Bạn chỉ cần tạo một file:

```text-x-trilium-auto
student.db
```

là đã có một Database hoàn chỉnh.

---

# 2. Bên trong Database có gì?

Một Database giống như một chiếc tủ hồ sơ.

```text-x-trilium-auto
student.db
│
├── students
├── classes
├── scores
├── teachers
└── subjects
```

Trong Database có rất nhiều **Table (bảng)**.

---

# 3. Table là gì?

Table giống như một bảng Excel.

Ví dụ:

```text-x-trilium-auto
Students
```

| ID  | Tên | Tuổi |
| --- | --- | --- |
| 1   | An  | 20  |
| 2   | Bình | 21  |
| 3   | Lan | 19  |

Đây là một Table.

---

# 4. Column là gì?

Column là **cột**.

Ví dụ

| ID  | Tên | Tuổi |
| --- | --- | --- |

Có ba Column

```text-x-trilium-auto
ID

Tên

Tuổi
```

Column dùng để mô tả dữ liệu.

---

# 5. Row là gì?

Row là **một dòng dữ liệu**.

Ví dụ

| ID  | Tên | Tuổi |
| --- | --- | --- |
| 1   | An  | 20  |

Đây là một Row.

Một dòng tương ứng với **một sinh viên**.

Ví dụ

| ID  | Tên | Tuổi |
| --- | --- | --- |
| 1   | An  | 20  |
| 2   | Bình | 21  |
| 3   | Lan | 19  |

Có **3 Row**.

---

# Minh họa trực quan

```text-x-trilium-auto
              COLUMN
      +----+--------+------+
ROW → | 1  |  An    | 20   |
ROW → | 2  | Bình   | 21   |
ROW → | 3  | Lan    | 19   |
      +----+--------+------+
        ID   NAME   AGE
```

---

# 6. Mỗi Column cần có kiểu dữ liệu

Ví dụ

| Tên cột | Kiểu |
| --- | --- |
| id  | INTEGER |
| name | TEXT |
| age | INTEGER |
| salary | REAL |

SQLite cần biết kiểu dữ liệu để lưu trữ hiệu quả.

---

# 7. Các kiểu dữ liệu cơ bản

SQLite rất linh hoạt nhưng chúng ta sẽ dùng các kiểu phổ biến sau.

## INTEGER

Lưu số nguyên.

Ví dụ

```text-x-trilium-auto
1

20

1000

-15
```

---

## REAL

Lưu số thực.

Ví dụ

```text-x-trilium-auto
3.14

7.8

100.99
```

---

## TEXT

Lưu chuỗi.

Ví dụ

```text-x-trilium-auto
An

Nguyễn Văn A

Python
```

---

## BLOB

Lưu dữ liệu nhị phân.

Ví dụ

- hình ảnh
- file PDF
- âm thanh

Thông thường, trong ứng dụng thực tế người ta hay lưu **đường dẫn file** thay vì lưu cả file vào CSDL.

---

## NULL

Không có dữ liệu.

Ví dụ

```text-x-trilium-auto
Tên: An

Số điện thoại: NULL
```

Nghĩa là chưa biết số điện thoại.

---

# 8. PRIMARY KEY là gì?

Đây là khái niệm cực kỳ quan trọng.

Ví dụ

| ID  | Tên |
| --- | --- |
| 1   | An  |
| 2   | Bình |
| 3   | Lan |

ID dùng để phân biệt từng sinh viên.

Không thể có

| ID  | Tên |
| --- | --- |
| 1   | An  |
| 1   | Lan |

Điều này gây nhầm lẫn.

Do đó

```text-x-trilium-auto
PRIMARY KEY
```

có hai nhiệm vụ:

- Không được trùng.
- Không được để trống (`NULL`).

---

# Ví dụ thực tế

Bạn có hai người đều tên:

```text-x-trilium-auto
Nguyễn Văn An
```

Nếu tìm theo tên sẽ không biết là ai.

Nhưng nếu có:

```text-x-trilium-auto
Mã sinh viên

10001

10002
```

thì sẽ xác định chính xác.

Đó chính là vai trò của `PRIMARY KEY`.

---

# 9. AUTOINCREMENT là gì?

Ví dụ

```text-x-trilium-auto
ID
```

Bạn không muốn mỗi lần thêm sinh viên lại phải tự nhập ID.

SQLite có thể tự tăng.

Ví dụ

```text-x-trilium-auto
1
2
3
4
5
6
```

Đó là

```text-x-trilium-auto
AUTOINCREMENT
```

---

# 10. Tạo Database bằng DB Browser

### Bước 1

Mở chương trình.

### Bước 2

```text-x-trilium-auto
New Database
```

---

### Bước 3

Đặt tên

```text-x-trilium-auto
student.db
```

---

### Bước 4

Lưu.

Đến đây bạn đã có Database đầu tiên.

---

# 11. Tạo Database bằng Python

Điều tuyệt vời của SQLite là chỉ cần kết nối đến một file chưa tồn tại, SQLite sẽ tự tạo file đó.

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

print("Đã tạo database thành công!")

conn.close()
```

Khi chạy chương trình, bạn sẽ thấy xuất hiện file:

```text-x-trilium-auto
student.db
```

---

# 12. Tạo bảng đầu tiên

Trong SQL:

```text-x-trilium-auto
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

Ý nghĩa:

```text-x-trilium-auto
students
```

là tên bảng.

```text-x-trilium-auto
id
```

là mã sinh viên.

```text-x-trilium-auto
INTEGER
```

kiểu số nguyên.

```text-x-trilium-auto
PRIMARY KEY
```

khóa chính.

```text-x-trilium-auto
AUTOINCREMENT
```

tự tăng.

```text-x-trilium-auto
name
```

kiểu chuỗi.

```text-x-trilium-auto
age
```

kiểu số nguyên.

---

# 13. Tạo bảng bằng Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
)
""")

conn.commit()

conn.close()

print("Tạo bảng thành công!")
```

---

# 14. Kiểm tra bảng vừa tạo

Mở **DB Browser for SQLite**:

- Chọn **Open Database**
- Mở `student.db`
- Chọn tab **Database Structure**

Bạn sẽ thấy:

```text-x-trilium-auto
students
```

Nếu mở bảng, cấu trúc sẽ giống:

| id  | INTEGER |
| --- | --- |
| name | TEXT |
| age | INTEGER |

---

# 15. Mô hình trực quan

```text-x-trilium-auto
student.db
        │
        ▼
+--------------------+
| students           |
+--------------------+
| id                 |
| name               |
| age                |
+--------------------+
```

Hiện tại bảng chưa có dữ liệu.

---

# 16. Một số lỗi thường gặp

## Lỗi 1: Quên `commit()`

```text-x-trilium-auto
conn.commit()
```

Nếu không gọi `commit()`, các thay đổi như tạo bảng, thêm hoặc sửa dữ liệu có thể không được lưu xuống file.

---

## Lỗi 2: Tạo lại bảng đã tồn tại

Nếu chạy lại:

```text-x-trilium-auto
CREATE TABLE students (...)
```

SQLite sẽ báo lỗi:

```text-x-trilium-auto
table students already exists
```

Để tránh lỗi này, bạn có thể dùng:

```text-x-trilium-auto
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

---

## Lỗi 3: Quên đóng kết nối

```text-x-trilium-auto
conn.close()
```

Nên đóng kết nối sau khi hoàn thành công việc để giải phóng tài nguyên.

---

# Tổng kết buổi 2

Bạn đã học được:

- Database trong SQLite là một **file** `**.db**`.
- Bên trong Database có nhiều **Table**.
- Hiểu rõ **Table**, **Row**, **Column**.
- Biết các kiểu dữ liệu cơ bản: `INTEGER`, `REAL`, `TEXT`, `BLOB`, `NULL`.
- Hiểu vai trò của `PRIMARY KEY`.
- Hiểu cách hoạt động của `AUTOINCREMENT`.
- Tạo Database và Table bằng cả SQL và Python.

---

# Bài tập thực hành

### Bài 1

Tạo Database:

```text-x-trilium-auto
company.db
```

---

### Bài 2

Tạo bảng:

```text-x-trilium-auto
employees
```

gồm:

| Cột | Kiểu dữ liệu |
| --- | --- |
| id  | INTEGER PRIMARY KEY AUTOINCREMENT |
| name | TEXT |
| age | INTEGER |
| salary | REAL |

---

### Bài 3

Tạo Database:

```text-x-trilium-auto
library.db
```

với bảng:

```text-x-trilium-auto
books
```

gồm:

- id
- title
- author
- price

Hãy tự chọn kiểu dữ liệu phù hợp cho từng cột.

---

### Bài 4 (Thử thách)

Thiết kế cơ sở dữ liệu cho một cửa hàng điện thoại với **3 bảng**:

- `customers`
- `products`
- `orders`

Chỉ cần xác định các cột chính và kiểu dữ liệu. Chúng ta chưa cần liên kết các bảng ở giai đoạn này.

---

## Kiến thức mở rộng

Trong các buổi sau, chúng ta sẽ không chỉ học cú pháp mà còn tìm hiểu **tại sao SQLite được thiết kế như vậy**, cách tối ưu cơ sở dữ liệu và các thực hành tốt trong phát triển phần mềm.

**Buổi 3** sẽ đi sâu vào **hệ thống kiểu dữ liệu (Storage Class và Type Affinity)** của SQLite. Đây là một điểm rất đặc biệt khiến SQLite khác với hầu hết các hệ quản trị cơ sở dữ liệu khác và cũng là nguyên nhân của nhiều lỗi khó hiểu nếu không nắm vững.