# Buổi 3: Hệ thống kiểu dữ liệu của SQLite (Storage Class & Type Affinity)

Đây là một trong những buổi **quan trọng nhất** của khóa học.

Rất nhiều lập trình viên đã dùng MySQL hoặc SQL Server khi chuyển sang SQLite thường gặp lỗi vì nghĩ rằng SQLite kiểm tra kiểu dữ liệu rất chặt chẽ. Thực tế **SQLite linh hoạt hơn rất nhiều**.

Sau buổi này, bạn sẽ hiểu:

- SQLite lưu dữ liệu như thế nào.
- Vì sao một cột `INTEGER` vẫn có thể lưu chuỗi.
- Storage Class là gì.
- Type Affinity là gì.
- Sự khác nhau giữa SQLite và các DBMS khác.
- Khi nào nên tận dụng sự linh hoạt và khi nào cần kiểm soát dữ liệu.

---

# Mục tiêu buổi học

Bạn sẽ hiểu sự khác biệt giữa:

```text-x-trilium-auto
Kiểu dữ liệu khai báo
        ≠
Kiểu dữ liệu thực tế được lưu
```

Đây là điểm đặc biệt nhất của SQLite.

---

# 1. Ôn tập

Buổi trước chúng ta tạo bảng:

```text-x-trilium-auto
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER
);
```

Bạn có thể nghĩ rằng:

- `id` chỉ nhận số.
- `name` chỉ nhận chuỗi.
- `age` chỉ nhận số.

Điều này **không hoàn toàn đúng** trong SQLite.

---

# 2. So sánh với MySQL

Ví dụ trong MySQL:

```text-x-trilium-auto
age INTEGER
```

Nếu thêm:

```text-x-trilium-auto
"hai mươi"
```

MySQL thường sẽ báo lỗi hoặc chuyển đổi theo quy tắc của nó.

SQLite thì khác.

---

# 3. SQLite dùng Dynamic Typing

SQLite **không gắn kiểu dữ liệu với cột**, mà **gắn kiểu dữ liệu với giá trị**.

Ví dụ:

```text-x-trilium-auto
age
```

có thể chứa:

```text-x-trilium-auto
20
```

hoặc

```text-x-trilium-auto
"20"
```

hoặc

```text-x-trilium-auto
20.5
```

thậm chí:

```text-x-trilium-auto
"Hello"
```

Điều này nghe có vẻ kỳ lạ nhưng là thiết kế có chủ đích của SQLite.

---

# 4. Storage Class

SQLite chỉ có **5 kiểu lưu trữ thực tế**.

## INTEGER

Lưu số nguyên.

Ví dụ:

```text-x-trilium-auto
1
100
-25
```

---

## REAL

Lưu số thực.

Ví dụ:

```text-x-trilium-auto
3.14
99.99
```

---

## TEXT

Lưu chuỗi.

Ví dụ:

```text-x-trilium-auto
An
Python
Hello
```

---

## BLOB

Lưu dữ liệu nhị phân.

Ví dụ:

- hình ảnh
- file PDF
- video
- âm thanh

---

## NULL

Không có giá trị.

---

# Sơ đồ

```text-x-trilium-auto
SQLite Storage Class

INTEGER

REAL

TEXT

BLOB

NULL
```

Toàn bộ SQLite chỉ dùng 5 kiểu này để lưu dữ liệu.

---

# 5. Type Affinity là gì?

Đây là khái niệm khiến nhiều người nhầm lẫn.

Ví dụ:

```text-x-trilium-auto
age INTEGER
```

Nhiều người nghĩ:

> Cột này chỉ chứa INTEGER.

Thực tế:

SQLite hiểu:

> Tôi **ưu tiên** lưu kiểu INTEGER nếu có thể.

Từ khóa **ưu tiên** chính là **Affinity**.

---

# 6. Ví dụ đầu tiên

Tạo bảng:

```text-x-trilium-auto
CREATE TABLE demo(
    value INTEGER
);
```

Sau đó:

```text-x-trilium-auto
INSERT INTO demo VALUES (100);
```

Kết quả:

```text-x-trilium-auto
100
```

Kiểu lưu:

```text-x-trilium-auto
INTEGER
```

---

Tiếp tục:

```text-x-trilium-auto
INSERT INTO demo VALUES ("200");
```

SQLite thấy:

```text-x-trilium-auto
"200"
```

có thể chuyển thành số.

Nó sẽ lưu thành:

```text-x-trilium-auto
INTEGER
```

---

Tiếp:

```text-x-trilium-auto
INSERT INTO demo VALUES ("ABC");
```

Lần này:

Không thể chuyển thành số.

SQLite sẽ lưu:

```text-x-trilium-auto
TEXT
```

Mặc dù cột được khai báo là:

```text-x-trilium-auto
INTEGER
```

---

# 7. Kiểm tra kiểu dữ liệu thực tế

SQLite có hàm:

```text-x-trilium-auto
typeof()
```

Ví dụ:

```text-x-trilium-auto
SELECT value, typeof(value)
FROM demo;
```

Kết quả:

| value | typeof |
| --- | --- |
| 100 | integer |
| 200 | integer |
| ABC | text |

Điều này cho thấy kiểu lưu trữ thực tế phụ thuộc vào **giá trị**, không chỉ phụ thuộc vào kiểu khai báo.

---

# 8. Năm loại Type Affinity

SQLite chia các kiểu khai báo thành 5 nhóm.

## INTEGER Affinity

Ví dụ:

```text-x-trilium-auto
INTEGER
INT
BIGINT
SMALLINT
```

Đều thuộc nhóm INTEGER.

---

## TEXT Affinity

Ví dụ:

```text-x-trilium-auto
TEXT
VARCHAR
CHAR
CLOB
```

Đều được ưu tiên lưu dạng TEXT.

---

## REAL Affinity

Ví dụ:

```text-x-trilium-auto
REAL
FLOAT
DOUBLE
```

---

## BLOB Affinity

Ví dụ:

```text-x-trilium-auto
BLOB
```

---

## NUMERIC Affinity

Đây là nhóm đặc biệt.

Ví dụ:

```text-x-trilium-auto
NUMERIC

BOOLEAN

DATE

DATETIME

DECIMAL
```

SQLite không có kiểu `BOOLEAN` hoặc `DATE` riêng. Chúng thường thuộc nhóm NUMERIC và cách lưu phụ thuộc vào giá trị.

---

# 9. Ví dụ với NUMERIC

```text-x-trilium-auto
CREATE TABLE product(
    price NUMERIC
);
```

Thêm:

```text-x-trilium-auto
INSERT INTO product VALUES ("99.5");
```

SQLite chuyển thành:

```text-x-trilium-auto
REAL
```

---

Thêm:

```text-x-trilium-auto
INSERT INTO product VALUES ("100");
```

SQLite chuyển thành:

```text-x-trilium-auto
INTEGER
```

---

Thêm:

```text-x-trilium-auto
INSERT INTO product VALUES ("Laptop");
```

SQLite lưu:

```text-x-trilium-auto
TEXT
```

---

# 10. BOOLEAN trong SQLite

SQLite **không có kiểu BOOLEAN thực sự**.

Thông thường:

```text-x-trilium-auto
0 = False

1 = True
```

Ví dụ:

```text-x-trilium-auto
CREATE TABLE users(
    is_active INTEGER
);
```

Dữ liệu:

| is_active |
| --- |
| 1   |
| 0   |

Trong Python:

```text-x-trilium-auto
if is_active == 1:
    print("Đang hoạt động")
else:
    print("Đã khóa")
```

---

# 11. DATE và DATETIME

SQLite cũng **không có kiểu DATE riêng**.

Có ba cách lưu phổ biến.

## Cách 1

TEXT

```text-x-trilium-auto
2026-07-08
```

Đây là cách được khuyến nghị vì dễ đọc và chuẩn ISO 8601.

---

## Cách 2

INTEGER

```text-x-trilium-auto
1751961600
```

Đây là Unix Timestamp (số giây tính từ 01/01/1970 UTC).

---

## Cách 3

REAL

Lưu dưới dạng Julian Day (ít dùng trong ứng dụng thông thường).

---

# 12. Ví dụ thực tế

Bảng sản phẩm:

| id  | name | price |
| --- | --- | --- |
| 1   | Laptop | 20000 |
| 2   | Chuột | 500 |

Trong Python:

```text-x-trilium-auto
price = 20000
```

SQLite lưu:

```text-x-trilium-auto
INTEGER
```

Nếu:

```text-x-trilium-auto
price = 20000.5
```

SQLite lưu:

```text-x-trilium-auto
REAL
```

---

# 13. Khi nào nên dùng kiểu dữ liệu nào?

| Dữ liệu | Kiểu khuyến nghị |
| --- | --- |
| ID  | INTEGER PRIMARY KEY |
| Tên | TEXT |
| Địa chỉ | TEXT |
| Tuổi | INTEGER |
| Lương | REAL |
| Ngày sinh | TEXT (YYYY-MM-DD) |
| Ngày tạo | TEXT hoặc INTEGER (Timestamp) |
| Ảnh | BLOB (hoặc lưu đường dẫn trong TEXT) |

---

# 14. Một số lưu ý quan trọng

- Đừng lạm dụng tính linh hoạt của SQLite. Nếu cột `age` dành cho tuổi, hãy luôn lưu số nguyên.
- Với ngày tháng, ưu tiên dùng định dạng ISO (`YYYY-MM-DD` hoặc `YYYY-MM-DD HH:MM:SS`) để dễ sắp xếp và truy vấn.
- Nếu cần ràng buộc dữ liệu, hãy sử dụng các **Constraint** (`CHECK`, `NOT NULL`, `UNIQUE`,...) mà chúng ta sẽ học ở các buổi sau.

---

# Tổng kết buổi 3

Bạn đã học được:

- SQLite sử dụng **Dynamic Typing**.
- Chỉ có **5 Storage Class**: `INTEGER`, `REAL`, `TEXT`, `BLOB`, `NULL`.
- **Type Affinity** là sự ưu tiên kiểu dữ liệu, không phải ràng buộc tuyệt đối.
- SQLite không có kiểu `BOOLEAN` và `DATE` riêng như nhiều DBMS khác.
- Hàm `typeof()` giúp kiểm tra kiểu dữ liệu thực tế của từng giá trị.

---

# Bài tập thực hành

## Bài 1

Tạo bảng:

```text-x-trilium-auto
CREATE TABLE demo(
    value INTEGER
);
```

Chèn lần lượt:

```text-x-trilium-auto
100
```

```text-x-trilium-auto
'200'
```

```text-x-trilium-auto
'ABC'
```

Sau đó chạy:

```text-x-trilium-auto
SELECT value, typeof(value)
FROM demo;
```

Quan sát kiểu dữ liệu thực tế của từng dòng.

---

## Bài 2

Tạo bảng:

```text-x-trilium-auto
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    is_active INTEGER
);
```

Thêm 3 người dùng với giá trị `is_active` là `1` hoặc `0`.

---

## Bài 3

Tạo bảng:

```text-x-trilium-auto
CREATE TABLE events(
    id INTEGER PRIMARY KEY,
    event_name TEXT,
    event_date TEXT
);
```

Thêm ít nhất 3 sự kiện với ngày theo định dạng:

```text-x-trilium-auto
YYYY-MM-DD
```

Ví dụ:

```text-x-trilium-auto
2026-07-08
```

---

## Bài 4 (Thử thách)

Tạo bảng `products` gồm các cột:

- `id`
- `name`
- `price`
- `stock`
- `created_at`

Hãy tự chọn kiểu dữ liệu phù hợp cho từng cột và giải thích ngắn gọn vì sao bạn chọn kiểu đó.

---

### Chuẩn bị cho buổi 4

Ở **Buổi 4**, chúng ta sẽ bắt đầu học **DDL (Data Definition Language)** với các câu lệnh quan trọng nhất:

- `CREATE TABLE`
- `ALTER TABLE`
- `DROP TABLE`

Đồng thời, bạn sẽ học cách thiết kế bảng đúng chuẩn ngay từ đầu để tránh phải sửa đổi nhiều về sau. Đây là nền tảng cho mọi cơ sở dữ liệu quan hệ chuyên nghiệp.