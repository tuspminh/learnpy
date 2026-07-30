# Buổi 8: ORDER BY, LIMIT và OFFSET - Sắp xếp & Phân trang dữ liệu

> Đây là buổi học cực kỳ thực tế.
> 
> Gần như **mọi phần mềm quản lý**, **website**, **ứng dụng desktop** đều sử dụng:
> 
> - Sắp xếp dữ liệu
> - Phân trang dữ liệu
> - Hiển thị Top N
> 
> Ba câu lệnh quan trọng nhất là:
> 
> - `ORDER BY`
> - `LIMIT`
> - `OFFSET`

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ thành thạo:

- ORDER BY
- ASC
- DESC
- Sắp xếp nhiều cột
- LIMIT
- OFFSET
- Phân trang (Pagination)
- ORDER BY trong Python
- LIMIT với placeholder

---

# 1. Chuẩn bị dữ liệu

Bảng `students`

| id  | name | age | city | salary |
| --- | --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội | 8000 |
| 2   | Bình | 22  | Huế | 9500 |
| 3   | Lan | 19  | Đà Nẵng | 7000 |
| 4   | Mai | 20  | Huế | 8500 |
| 5   | Nam | 23  | Hà Nội | 12000 |
| 6   | Hoa | 21  | Huế | 9000 |

---

# 2. ORDER BY là gì?

Không có `ORDER BY`

```text-x-trilium-auto
SELECT * FROM students;
```

SQLite thường trả kết quả theo thứ tự lưu trữ hiện tại.

⚠ **Lưu ý**

Không nên **phụ thuộc** vào thứ tự này.

Trong SQL, nếu không có `ORDER BY` thì **thứ tự kết quả không được đảm bảo**.

---

# 3. ORDER BY tăng dần

```text-x-trilium-auto
SELECT * FROM students
ORDER BY age;
```

Mặc định

```text-x-trilium-auto
ASC
```

(tăng dần)

Kết quả

| name | age |
| --- | --- |
| Lan | 19  |
| An  | 20  |
| Mai | 20  |
| Hoa | 21  |
| Bình | 22  |
| Nam | 23  |

---

# 4. ASC

Viết đầy đủ

```text-x-trilium-auto
SELECT * FROM students
ORDER BY age ASC;
```

Giống hệt

```text-x-trilium-auto
ORDER BY age;
```

---

# 5. DESC

Muốn lớn → nhỏ

```text-x-trilium-auto
SELECT * FROM students
ORDER BY salary DESC;
```

Kết quả

| name | salary |
| --- | --- |
| Nam | 12000 |
| Bình | 9500 |
| Hoa | 9000 |
| Mai | 8500 |
| An  | 8000 |
| Lan | 7000 |

---

# 6. Sắp xếp theo chuỗi

```text-x-trilium-auto
SELECT * FROM students
ORDER BY name;
```

Kết quả

```text-x-trilium-auto
An
Bình
Hoa
Lan
Mai
Nam
```

SQLite sắp xếp theo thứ tự từ điển (collation mặc định).

---

# 7. Sắp xếp nhiều cột

Ví dụ

```text-x-trilium-auto
SELECT * FROM students
ORDER BY city,
         age;
```

SQLite thực hiện như sau:

Bước 1

Sắp xếp theo

```text-x-trilium-auto
city
```

Nếu trùng

↓

Bước 2

Sắp xếp tiếp theo

```text-x-trilium-auto
age
```

---

Ví dụ kết quả

| city | name | age |
| --- | --- | --- |
| Đà Nẵng | Lan | 19  |
| Hà Nội | An  | 20  |
| Hà Nội | Nam | 23  |
| Huế | Mai | 20  |
| Huế | Hoa | 21  |
| Huế | Bình | 22  |

---

# 8. ASC và DESC cùng lúc

```text-x-trilium-auto
SELECT * FROM students
ORDER BY city ASC,
         salary DESC;
```

Trong mỗi thành phố

↓

Người lương cao đứng trước.

Ví dụ với Huế:

| name | salary |
| --- | --- |
| Bình | 9500 |
| Hoa | 9000 |
| Mai | 8500 |

---

# 9. LIMIT

Muốn lấy

2 dòng đầu tiên

```text-x-trilium-auto
SELECT * FROM students
LIMIT 2;
```

Kết quả

|An|  
|Bình|

---

# 10. LIMIT sau ORDER BY

Ví dụ

Top 3 lương cao nhất

```text-x-trilium-auto
SELECT * FROM students
ORDER BY salary DESC LIMIT 3;
```

Kết quả

|Nam|  
|Bình|  
|Hoa|

Đây là cách rất phổ biến để lấy "Top N".

---

# 11. OFFSET

OFFSET nghĩa là

> Bỏ qua bao nhiêu dòng đầu.

Ví dụ

```text-x-trilium-auto
SELECT * FROM students
LIMIT 2
OFFSET 2;
```

SQLite sẽ:

Bỏ

```text-x-trilium-auto
2 dòng đầu
```

↓

Lấy tiếp

```text-x-trilium-auto
2 dòng
```

Kết quả

|Lan|  
|Mai|

---

# 12. Pagination (Phân trang)

Đây là ứng dụng thực tế nhất.

Giả sử

Mỗi trang

```text-x-trilium-auto
10 dòng
```

---

Trang 1

```text-x-trilium-auto
LIMIT 10 OFFSET 0
```

---

Trang 2

```text-x-trilium-auto
LIMIT 10 OFFSET 10
```

---

Trang 3

```text-x-trilium-auto
LIMIT 10 OFFSET 20
```

---

Công thức

```text-x-trilium-auto
OFFSET =
(page - 1) × page_size
```

Ví dụ

Trang

```text-x-trilium-auto
5
```

Mỗi trang

```text-x-trilium-auto
20
```

↓

```text-x-trilium-auto
OFFSET = (5 - 1) × 20

= 80
```

SQL

```text-x-trilium-auto
LIMIT 20 OFFSET 80;
```

---

# 13. LIMIT với placeholder

Trong Python

```text-x-trilium-auto
page_size = 10 offset = 20

cursor.execute(
    """
    SELECT *
    FROM students
    LIMIT ?
    OFFSET ?
    """,
    (page_size, offset)
)
```

Đây là cách nên dùng khi xây dựng chức năng phân trang.

---

# 14. Ví dụ hoàn chỉnh

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute(
    """
    SELECT
        id,
        name,
        age
    FROM students
    ORDER BY age DESC
    LIMIT 3
    """
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

---

# 15. Hàm phân trang

Ví dụ

```text-x-trilium-auto
def get_students(page, page_size):

    offset = (page - 1) * page_size

    ...
```

SQL

```text-x-trilium-auto
SELECT
    id,
    name,
    age
FROM students
ORDER BY id
LIMIT ?
OFFSET ?;
```

Đây là nền tảng của:

- Website
- API
- PySide6 TableView
- Qt Model
- Flet DataTable

---

# 16. Thứ tự thực thi

Nhiều người nghĩ

SQLite thực hiện

```text-x-trilium-auto
LIMIT

↓

ORDER BY
```

Không đúng.

Thứ tự logic đơn giản có thể hình dung là:

```text-x-trilium-auto
FROM

↓

WHERE

↓

SELECT

↓

ORDER BY

↓

LIMIT/OFFSET
```

Vì vậy:

```text-x-trilium-auto
SELECT * FROM students
ORDER BY salary DESC LIMIT 3;
```

nghĩa là:

1. Lấy dữ liệu từ bảng.
2. Sắp xếp theo `salary DESC`.
3. Sau đó mới lấy 3 dòng đầu tiên.

---

# 17. Những lỗi rất thường gặp

## Lỗi 1

Viết

```text-x-trilium-auto
LIMIT
```

trước

```text-x-trilium-auto
ORDER BY
```

Sai

```text-x-trilium-auto
SELECT * FROM students
LIMIT 3 ORDER BY salary;
```

Đúng

```text-x-trilium-auto
SELECT * FROM students
ORDER BY salary
LIMIT 3;
```

---

## Lỗi 2

Không có ORDER BY

```text-x-trilium-auto
SELECT * FROM students
LIMIT 10;
```

Có thể

mỗi lần

thứ tự khác nhau.

Nên

```text-x-trilium-auto
ORDER BY id
```

hoặc

```text-x-trilium-auto
ORDER BY created_at
```

---

## Lỗi 3

OFFSET âm

```text-x-trilium-auto
OFFSET -5
```

Không hợp lệ.

---

## Lỗi 4

Phân trang sai

Sai

```text-x-trilium-auto
OFFSET = page × size
```

Đúng

```text-x-trilium-auto
(page - 1) × size
```

---

# 18. Một ví dụ thực tế

Hệ thống quản lý truyện (đúng với dự án của bạn)

Bảng

```text-x-trilium-auto
stories
```

Hiển thị

50 truyện mới nhất

```text-x-trilium-auto
SELECT
    id,
    title,
    author
FROM stories
ORDER BY updated_at DESC LIMIT 50;
```

---

Khi người dùng

bấm

```text-x-trilium-auto
Trang 2
```

↓

```text-x-trilium-auto
LIMIT 50
OFFSET 50;
```

Đây chính là cách các website đọc truyện và ứng dụng quản lý dữ liệu hoạt động.

---

# Tổng kết buổi 8

Bạn đã học:

- `ORDER BY`
- `ASC`
- `DESC`
- Sắp xếp theo nhiều cột
- `LIMIT`
- `OFFSET`
- Phân trang dữ liệu
- Top N
- Placeholder trong `LIMIT` và `OFFSET`
- Cách xây dựng chức năng phân trang trong Python

---

# Bài tập

## Bài 1

Hiển thị tất cả sinh viên theo:

- tuổi tăng dần
- tuổi giảm dần

---

## Bài 2

Hiển thị

5 sinh viên

lương cao nhất.

---

## Bài 3

Hiển thị

3 sinh viên

bắt đầu từ dòng thứ 4.

(Hãy dùng `LIMIT` và `OFFSET`.)

---

## Bài 4

Viết hàm

```text-x-trilium-auto
def get_students(page: int, page_size: int):
    ...
```

Yêu cầu:

- Tính `offset`.
- Truy vấn:

```text-x-trilium-auto
SELECT
    id,
    name,
    age
FROM students
ORDER BY id
LIMIT ?
OFFSET ?;
```

- Trả về `list[tuple]`.

---

## Bài 5 (Thử thách)

Viết hàm:

```text-x-trilium-auto
def get_top_salary(limit: int):
    ...
```

Yêu cầu:

- Trả về `limit` sinh viên có mức lương cao nhất.
- Sử dụng:

```text-x-trilium-auto
ORDER BY salary DESC LIMIT ?;
```

---

# Góc lập trình viên chuyên nghiệp

Trong các ứng dụng thực tế:

- **Luôn** kết hợp `ORDER BY` với `LIMIT` để có kết quả ổn định.
- Khi phân trang, hãy sắp xếp theo một cột có giá trị duy nhất hoặc gần như duy nhất (ví dụ `id`, `created_at`) để tránh việc dữ liệu bị "nhảy trang" khi có bản ghi mới được thêm.
- Với bảng rất lớn (hàng triệu dòng), `OFFSET` lớn có thể chậm. Khi học đến phần tối ưu và Index, chúng ta sẽ tìm hiểu kỹ thuật **Keyset Pagination (Seek Pagination)** để giải quyết vấn đề này.

Ở **Buổi 9**, chúng ta sẽ học `**UPDATE**` — cách cập nhật dữ liệu an toàn, sử dụng `WHERE` để tránh sửa nhầm toàn bộ bảng, và thực hành cập nhật dữ liệu bằng Python theo đúng chuẩn của các ứng dụng chuyên nghiệp.