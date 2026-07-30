# Buổi 1: Làm quen với SQLite3 và Cơ sở dữ liệu quan hệ

Chào mừng bạn đến với buổi học đầu tiên!

Trong buổi này, mục tiêu của chúng ta **không phải học viết SQL**, mà là **hiểu bản chất** của cơ sở dữ liệu quan hệ (Relational Database). Khi hiểu được bản chất, việc học SQL sau này sẽ trở nên rất dễ dàng.

---

# Mục tiêu của buổi học

Sau buổi này, bạn sẽ hiểu được:

- Database là gì?
- Hệ quản trị cơ sở dữ liệu (DBMS) là gì?
- SQLite là gì?
- SQL là gì?
- Cơ sở dữ liệu quan hệ hoạt động như thế nào?
- Tại sao phải dùng Database thay vì Excel hoặc file TXT?
- Khi nào nên dùng SQLite?
- Kiến trúc của SQLite.
- Cài đặt các công cụ cần thiết.

---

# 1. Database (Cơ sở dữ liệu) là gì?

Hiểu đơn giản:

> Database là nơi lưu trữ dữ liệu có tổ chức để có thể tìm kiếm, sửa, xóa và cập nhật nhanh chóng.

Ví dụ:

Bạn có một cửa hàng.

Bạn cần lưu:

- Khách hàng
- Sản phẩm
- Đơn hàng
- Nhân viên

Nếu chỉ ghi vào giấy:

```text-x-trilium-auto
Nguyễn Văn A
0909123456
Đã mua Laptop

Trần Văn B
0988111222
Đã mua Chuột
```

Sau vài nghìn khách hàng...

👉 Gần như không thể tìm kiếm nhanh.

---

## Nếu dùng Excel

Ví dụ:

| Tên | Điện thoại | Sản phẩm |
| --- | --- | --- |
| An  | 0909 | Laptop |
| Bình | 0988 | Chuột |

Excel khá tốt.

Nhưng nếu có:

- 500.000 khách
- 50.000 đơn hàng
- 100 nhân viên

thì Excel sẽ bắt đầu chậm và khó quản lý.

---

## Database sinh ra để giải quyết vấn đề này

Database có thể:

- Lưu hàng triệu bản ghi
- Tìm kiếm cực nhanh
- Bảo vệ dữ liệu
- Tránh trùng lặp
- Nhiều người cùng truy cập
- Sao lưu dữ liệu

---

# Ví dụ đời thực

Một ngân hàng có:

```text-x-trilium-auto
20 triệu khách hàng
```

Nếu lưu bằng Excel...

Có thể mất hàng giờ để tìm kiếm.

Nếu lưu trong Database...

Chỉ mất vài phần nghìn giây.

---

# 2. DBMS là gì?

DBMS = Database Management System

Tiếng Việt:

> Hệ quản trị cơ sở dữ liệu.

Nó giống như một người quản lý kho.

Ví dụ:

Kho hàng

```text-x-trilium-auto
Kho
 │
 │
 ├── Máy tính
 ├── Chuột
 ├── Bàn phím
 └── Màn hình
```

Bạn không tự đi vào kho.

Bạn nhờ người quản lý.

Ví dụ:

```text-x-trilium-auto
Cho tôi Laptop Dell
```

Người quản lý tìm giúp.

DBMS cũng vậy.

Bạn không thao tác trực tiếp trên file dữ liệu.

Bạn gửi câu lệnh SQL.

DBMS sẽ:

- tìm dữ liệu
- lưu dữ liệu
- sửa dữ liệu
- xóa dữ liệu

---

# Một số DBMS nổi tiếng

| Tên | Miễn phí | Doanh nghiệp |
| --- | --- | --- |
| SQLite | ✅   | ⭐⭐⭐ |
| MySQL | ✅   | ⭐⭐⭐⭐ |
| PostgreSQL | ✅   | ⭐⭐⭐⭐⭐ |
| MariaDB | ✅   | ⭐⭐⭐⭐ |
| SQL Server | Có bản miễn phí | ⭐⭐⭐⭐⭐ |
| Oracle | Có bản miễn phí | ⭐⭐⭐⭐⭐ |

---

# 3. SQLite là gì?

SQLite là một DBMS siêu nhỏ.

Đặc biệt:

Không có Server.

Ví dụ:

MySQL

```text-x-trilium-auto
Python

↓

MySQL Server

↓

Database
```

SQLite

```text-x-trilium-auto
Python

↓

student.db
```

Không cần server.

Không cần cài đặt phức tạp.

Không cần tạo user.

Không cần password.

Chỉ cần:

```text-x-trilium-auto
student.db
```

Là xong.

---

# SQLite lưu dữ liệu ở đâu?

Toàn bộ Database nằm trong **một file**.

Ví dụ:

```text-x-trilium-auto
student.db
```

Hoặc

```text-x-trilium-auto
shop.db
```

Hoặc

```text-x-trilium-auto
hospital.db
```

File này có thể:

- copy
- gửi email
- backup
- lưu USB

rất tiện.

---

# 4. SQL là gì?

SQL

Structured Query Language

Là ngôn ngữ để giao tiếp với Database.

Ví dụ:

Bạn nói với Database:

```text-x-trilium-auto
Lấy tất cả sinh viên.
```

SQL sẽ là:

```text-x-trilium-auto
SELECT * FROM students;
```

Bạn muốn thêm sinh viên:

```text-x-trilium-auto
INSERT INTO students ...
```

Muốn sửa:

```text-x-trilium-auto
UPDATE ...
```

Muốn xóa:

```text-x-trilium-auto
DELETE ...
```

---

# 5. Cơ sở dữ liệu quan hệ là gì?

Đây là phần quan trọng nhất của buổi học.

Ví dụ:

Một trường học.

Có:

Sinh viên

| ID  | Tên |
| --- | --- |
| 1   | An  |
| 2   | Bình |

Lớp học

| ID  | Tên lớp |
| --- | --- |
| 1   | Python |
| 2   | Java |

Điểm

| StudentID | ClassID | Điểm |
| --- | --- | --- |
| 1   | 1   | 9   |
| 2   | 2   | 8   |

Đây gọi là **cơ sở dữ liệu quan hệ**.

Vì:

Bảng Điểm liên kết với:

- Sinh viên
- Lớp học

thông qua các khóa (ID).

---

# Ví dụ trực quan

```text-x-trilium-auto
Students
+----+-------+
|ID  |Name   |
+----+-------+
|1   |An     |
|2   |Bình   |
+----+-------+

Classes
+----+----------+
|ID  |ClassName |
+----+----------+
|1   |Python    |
|2   |Java      |
+----+----------+

Scores
+-----------+---------+-------+
|StudentID  |ClassID  |Score  |
+-----------+---------+-------+
|1          |1        |9.5    |
|2          |2        |8.0    |
+-----------+---------+-------+
```

Quan hệ:

```text-x-trilium-auto
Students
      │
      │
      ▼
Scores
      ▲
      │
Classes
```

Đây chính là lý do gọi là **Relational Database**.

---

# 6. SQLite hoạt động như thế nào?

```text-x-trilium-auto
Python Program
       │
       ▼
sqlite3 module
       │
       ▼
SQLite Engine
       │
       ▼
student.db
```

Python gửi SQL.

SQLite thực hiện.

Dữ liệu được ghi xuống file.

---

# 7. Khi nào nên dùng SQLite?

SQLite rất phù hợp cho:

- Ứng dụng Desktop (Tkinter, PySide6, PyQt)
- Công cụ quản lý cá nhân
- Ứng dụng Offline
- Mobile (Android, iOS)
- IoT
- Raspberry Pi
- Lưu cấu hình
- Lưu cache
- Học SQL
- Dự án nhỏ và vừa

---

# Khi nào không nên dùng SQLite?

Không phù hợp nếu:

- Website có hàng nghìn người truy cập đồng thời.
- Hệ thống ngân hàng lớn.
- Mạng xã hội.
- Sàn thương mại điện tử quy mô lớn.
- Hệ thống phân tán nhiều máy chủ.

Những trường hợp này thường dùng các DBMS như MySQL, PostgreSQL hoặc SQL Server.

---

# 8. Ưu điểm của SQLite

- Miễn phí.
- Mã nguồn mở.
- Không cần cài đặt server.
- Chỉ có một file `.db`.
- Nhẹ (chỉ vài MB).
- Rất nhanh với ứng dụng đơn lẻ.
- Có sẵn trong Python (`sqlite3` là thư viện chuẩn).

---

# 9. Nhược điểm của SQLite

- Chỉ có một tiến trình ghi dữ liệu tại một thời điểm.
- Không tối ưu cho nhiều người dùng ghi đồng thời.
- Ít tính năng quản trị hơn các DBMS lớn.
- Không phù hợp với hệ thống có lưu lượng truy cập rất cao.

---

# 10. Chuẩn bị môi trường

## Python

Kiểm tra phiên bản:

```text-x-trilium-auto
python --version
```

Hoặc:

```text-x-trilium-auto
python3 --version
```

---

## Kiểm tra thư viện sqlite3

```text-x-trilium-auto
import sqlite3

print(sqlite3.sqlite_version)
```

Ví dụ kết quả:

```text-x-trilium-auto
3.46.1
```

Nếu in ra được phiên bản thì môi trường đã sẵn sàng.

---

## Cài DB Browser for SQLite

Đây là công cụ đồ họa giúp:

- Tạo cơ sở dữ liệu.
- Tạo bảng.
- Thực thi SQL.
- Xem dữ liệu trực quan.
- Sao lưu và xuất dữ liệu.

Chúng ta sẽ sử dụng công cụ này xuyên suốt khóa học cùng với Python để vừa hiểu SQL vừa hiểu cách lập trình làm việc với cơ sở dữ liệu.

---

# Tổng kết buổi 1

Bạn đã nắm được:

- Khái niệm cơ sở dữ liệu (Database).
- Vai trò của hệ quản trị cơ sở dữ liệu (DBMS).
- SQLite là gì và vì sao nó phù hợp cho học tập và ứng dụng desktop.
- SQL là ngôn ngữ dùng để làm việc với cơ sở dữ liệu.
- Khái niệm cơ sở dữ liệu quan hệ và cách các bảng liên kết với nhau.
- Kiến trúc hoạt động của SQLite.
- Những trường hợp nên và không nên sử dụng SQLite.

---

# Bài tập thực hành

### Bài 1

Tự cài đặt Python (nếu chưa có) và chạy:

```text-x-trilium-auto
import sqlite3

print("SQLite version:", sqlite3.sqlite_version)
```

---

### Bài 2

Cài đặt **DB Browser for SQLite** và mở chương trình để làm quen với giao diện (chưa cần tạo cơ sở dữ liệu).

---

### Bài 3

Vẽ sơ đồ cho một hệ thống quản lý thư viện gồm các bảng:

- `Books`
- `Authors`
- `Publishers`
- `Borrowers`
- `Loans`

Hãy suy nghĩ xem bảng nào sẽ liên kết với bảng nào.

---

### Bài 4 (Thử thách)

Thiết kế trên giấy cơ sở dữ liệu cho một cửa hàng điện thoại. Liệt kê ít nhất 5 bảng cần có (ví dụ: `Customers`, `Products`, `Orders`, ...), và mô tả ngắn gọn vai trò của từng bảng.

Ở **Buổi 2**, chúng ta sẽ bắt đầu thực hành với SQLite bằng cách **tạo cơ sở dữ liệu đầu tiên**, tạo bảng (`CREATE TABLE`), tìm hiểu kiểu dữ liệu của SQLite và cách tổ chức dữ liệu theo đúng chuẩn. Đây sẽ là buổi học đầu tiên có thực hành SQL và Python.