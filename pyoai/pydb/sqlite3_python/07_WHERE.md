# Buổi 7: WHERE – Trái tim của việc truy vấn dữ liệu

> **Đây là một trong những buổi quan trọng nhất của khóa học.**
> 
> Nếu `SELECT` giúp bạn lấy dữ liệu thì `**WHERE**` **giúp bạn lấy đúng dữ liệu mình cần**.
> 
> Thực tế, hơn **95% câu lệnh SELECT trong các ứng dụng đều có WHERE**.

---

# Mục tiêu buổi học

Sau buổi này, bạn sẽ thành thạo:

- WHERE là gì
- Toán tử so sánh
- AND
- OR
- NOT
- IN
- BETWEEN
- LIKE
- IS NULL
- IS NOT NULL
- WHERE trong Python
- Placeholder (`?`) trong WHERE

---

# 1. Chuẩn bị dữ liệu

Giả sử chúng ta có bảng:

| id  | name | age | city | salary |
| --- | --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội | 8000 |
| 2   | Bình | 22  | Huế | 9500 |
| 3   | Lan | 19  | Đà Nẵng | 7000 |
| 4   | Mai | 20  | Huế | 8500 |
| 5   | Nam | 23  | Hà Nội | 12000 |

---

# 2. WHERE là gì?

Không có WHERE

```text-x-trilium-auto
SELECT * FROM students;
```

Kết quả:

👉 Lấy **toàn bộ** dữ liệu.

Có WHERE

```text-x-trilium-auto
SELECT * FROM students
WHERE age = 20;
```

Kết quả:

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 20  |
| 4   | Mai | 20  |

SQLite sẽ:

```text-x-trilium-auto
Đọc từng dòng
        │
        ▼
Kiểm tra điều kiện
        │
        ▼
Đúng → Trả về
Sai  → Bỏ qua
```

---

# 3. Toán tử "="

```text-x-trilium-auto
SELECT * FROM students
WHERE city = 'Huế';
```

Kết quả

| name | city |
| --- | --- |
| Bình | Huế |
| Mai | Huế |

---

# 4. Khác (!= hoặc <>)

SQLite hỗ trợ

```text-x-trilium-auto
<>
```

và

```text-x-trilium-auto
!=
```

Ví dụ

```text-x-trilium-auto
SELECT * FROM students
WHERE city <> 'Huế';
```

Kết quả

|An|  
|Lan|  
|Nam|

---

# 5. Lớn hơn

```text-x-trilium-auto
SELECT * FROM students
WHERE salary > 9000;
```

Kết quả

|Bình|  
|Nam|

---

# 6. Nhỏ hơn

```text-x-trilium-auto
SELECT * FROM students
WHERE age < 21;
```

Kết quả

|An|  
|Lan|  
|Mai|

---

# 7. >= và <=

```text-x-trilium-auto
SELECT * FROM students
WHERE salary >= 8500;
```

Kết quả

|Bình|  
|Mai|  
|Nam|

---

# 8. AND

Muốn tìm

- ở Huế
- tuổi 20

```text-x-trilium-auto
SELECT * FROM students
WHERE city='Huế' AND age=20;
```

Kết quả

|Mai|

Cả hai điều kiện phải đúng.

```text-x-trilium-auto
Huế? ── Có
          │
Tuổi 20? ─ Có
          │
      Trả về
```

---

# 9. OR

```text-x-trilium-auto
SELECT * FROM students
WHERE city='Huế' OR city='Hà Nội';
```

Kết quả

|An|  
|Bình|  
|Mai|  
|Nam|

Chỉ cần **một** điều kiện đúng.

---

# 10. NOT

```text-x-trilium-auto
SELECT * FROM students
WHERE NOT city='Huế';
```

Kết quả

|An|  
|Lan|  
|Nam|

---

# 11. IN

Thay vì

```text-x-trilium-auto
WHERE city='Huế' OR city='Hà Nội' OR city='Đà Nẵng'
```

Viết gọn

```text-x-trilium-auto
SELECT * FROM students
WHERE city IN(
    'Huế',
    'Hà Nội',
    'Đà Nẵng'
);
```

Dễ đọc hơn rất nhiều.

---

# 12. BETWEEN

Tìm sinh viên

18 đến 20 tuổi

```text-x-trilium-auto
SELECT * FROM students
WHERE age BETWEEN 18 AND 20;
```

Kết quả

|An|  
|Lan|  
|Mai|

**Lưu ý:**

`BETWEEN` **bao gồm cả hai đầu mút**.

Nghĩa là:

```text-x-trilium-auto
18 ≤ age ≤ 20
```

---

# 13. LIKE

Đây là câu lệnh tìm kiếm theo mẫu.

## Bắt đầu bằng

```text-x-trilium-auto
SELECT * FROM students
WHERE name LIKE 'A%';
```

Kết quả

|An|

---

## Kết thúc bằng

```text-x-trilium-auto
WHERE name LIKE '%n';
```

Kết quả

|An|  
|Bình|  
|Nam|

---

## Chứa

```text-x-trilium-auto
WHERE name LIKE '%a%';
```

Kết quả

|Lan|  
|Nam|  
|Mai|

---

# 14. Ký tự đại diện

`%`

Nghĩa là

```text-x-trilium-auto
0 hoặc nhiều ký tự
```

Ví dụ

```text-x-trilium-auto
A%
```

khớp

```text-x-trilium-auto
A

An

Anh

Anh Tuấn
```

---

`_`

Nghĩa là

```text-x-trilium-auto
đúng một ký tự
```

Ví dụ

```text-x-trilium-auto
WHERE name LIKE '_n';
```

Khớp

```text-x-trilium-auto
An
```

Không khớp

```text-x-trilium-auto
Nam
```

vì có 3 ký tự.

---

# 15. NULL

Sai

```text-x-trilium-auto
WHERE phone = NULL
```

Không bao giờ đúng.

Đúng

```text-x-trilium-auto
WHERE phone IS NULL;
```

---

Muốn tìm

đã có số điện thoại

```text-x-trilium-auto
WHERE phone IS NOT NULL;
```

---

# 16. Kết hợp nhiều điều kiện

```text-x-trilium-auto
SELECT * FROM students
WHERE city='Huế' AND salary>8000 AND age<25;
```

Hoàn toàn hợp lệ.

---

# 17. Dùng ngoặc

Ví dụ

```text-x-trilium-auto
SELECT * FROM students
WHERE
(
    city='Huế'
    OR city='Hà Nội'
)
AND age>=20;
```

Nếu không dùng ngoặc, kết quả có thể khác do thứ tự ưu tiên của các toán tử logic.

---

# 18. WHERE trong Python

Sai

```text-x-trilium-auto
city = "Huế"

sql = f"""
SELECT *
FROM students
WHERE city='{city}'
"""
```

Đây vẫn là nối chuỗi SQL.

---

# 19. Cách đúng

```text-x-trilium-auto
city = "Huế"

cursor.execute(
    """
    SELECT *
    FROM students
    WHERE city=?
    """,
    (city,)
)
```

Dấu

```text-x-trilium-auto
?
```

là placeholder.

---

# 20. Nhiều placeholder

```text-x-trilium-auto
cursor.execute(
    """
    SELECT *
    FROM students
    WHERE age>=?
    AND city=?
    """,
    (20, "Huế")
)
```

SQLite sẽ thay đúng giá trị theo thứ tự.

---

# 21. Ví dụ hoàn chỉnh

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
    WHERE age>=?
    """,
    (20,)
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

---

# 22. Sơ đồ hoạt động

```text-x-trilium-auto
SELECT

↓

FROM students

↓

WHERE

↓

Kiểm tra từng dòng

↓

Điều kiện đúng?

↓

Có

↓

Đưa vào Result Set

↓

fetchall()
```

---

# Những lỗi rất thường gặp

## Lỗi 1

Sai

```text-x-trilium-auto
WHERE age=NULL
```

Đúng

```text-x-trilium-auto
WHERE age IS NULL
```

---

## Lỗi 2

Quên dấu nháy

Sai

```text-x-trilium-auto
WHERE city=Huế
```

Đúng

```text-x-trilium-auto
WHERE city='Huế'
```

---

## Lỗi 3

Nối chuỗi SQL

Sai

```text-x-trilium-auto
f"...{city}..."
```

Đúng

```text-x-trilium-auto
WHERE city=?
```

---

## Lỗi 4

Quên dấu phẩy khi chỉ có một tham số

Sai

```text-x-trilium-auto
("Huế")
```

Đây chỉ là một chuỗi.

Đúng

```text-x-trilium-auto
("Huế",)
```

Đây mới là tuple một phần tử mà `sqlite3` mong đợi.

---

# Tổng kết buổi 7

Hôm nay bạn đã học:

- `WHERE`
- `=`
- `!=`
- `<>`
- `>`
- `<`
- `>=`
- `<=`
- `AND`
- `OR`
- `NOT`
- `IN`
- `BETWEEN`
- `LIKE`
- `%`
- `_`
- `IS NULL`
- `IS NOT NULL`
- Placeholder (`?`) trong truy vấn có điều kiện

Đến thời điểm này, bạn đã có thể viết được phần lớn các câu lệnh truy vấn cơ bản dùng trong ứng dụng thực tế.

---

# Bài tập

## Bài 1

Lấy tất cả sinh viên:

- tuổi lớn hơn 20
- sống ở Hà Nội

---

## Bài 2

Lấy tất cả sinh viên có tên bắt đầu bằng

```text-x-trilium-auto
N
```

---

## Bài 3

Lấy tất cả sinh viên có tuổi

```text-x-trilium-auto
18 đến 22
```

bằng `BETWEEN`.

---

## Bài 4

Lấy tất cả sinh viên ở:

- Huế
- Hà Nội

bằng `IN`.

---

## Bài 5

Viết hàm Python:

```text-x-trilium-auto
def find_students(city: str, min_age: int):
    ...
```

Yêu cầu:

- Sử dụng placeholder (`?`).
- Truy vấn:

```text-x-trilium-auto
SELECT id, name, age
FROM students
WHERE city = ?
AND age >= ?;
```

- Trả về kết quả dưới dạng `list[tuple]`.
- Không in trực tiếp trong hàm.

---

# Góc lập trình viên chuyên nghiệp

Khi viết SQL, hãy ưu tiên:

- Viết điều kiện rõ ràng, dễ đọc.
- Dùng `IN` thay cho nhiều `OR` khi lọc theo danh sách giá trị.
- Dùng `BETWEEN` cho khoảng giá trị liên tục.
- Luôn dùng placeholder (`?`) trong Python, kể cả với các truy vấn `SELECT`.
- Thêm ngoặc khi kết hợp `AND` và `OR` để tránh hiểu nhầm và lỗi logic.

Ở **Buổi 8**, chúng ta sẽ học `**ORDER BY**`, `LIMIT` và `OFFSET` một cách chuyên sâu, đồng thời xây dựng chức năng **sắp xếp và phân trang** dữ liệu giống như trong các ứng dụng quản lý và website thực tế. Đây là nền tảng để hiển thị danh sách dữ liệu một cách hiệu quả và chuyên nghiệp.