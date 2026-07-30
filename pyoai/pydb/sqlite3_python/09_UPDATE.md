# Buổi 9: UPDATE - Cập nhật dữ liệu

> Đây là buổi học **cực kỳ quan trọng**.
> 
> Trong thực tế, `UPDATE` là câu lệnh nguy hiểm nhất sau `DELETE`.
> 
> Chỉ cần quên một từ `WHERE`, bạn có thể làm hỏng toàn bộ dữ liệu của hệ thống.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ thành thạo:

- UPDATE là gì
- SET
- WHERE trong UPDATE
- Cập nhật nhiều cột
- Biểu thức trong UPDATE
- UPDATE bằng Python
- Placeholder (`?`)
- `cursor.rowcount`
- Transaction khi UPDATE
- Những lỗi rất nguy hiểm

---

# 1. Chuẩn bị dữ liệu

Bảng

```text-x-trilium-auto
students
```

| id  | name | age | city | salary |
| --- | --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội | 8000 |
| 2   | Bình | 22  | Huế | 9500 |
| 3   | Lan | 19  | Đà Nẵng | 7000 |
| 4   | Mai | 20  | Huế | 8500 |

---

# 2. UPDATE là gì?

Nếu

INSERT

↓

Thêm dòng mới

thì

UPDATE

↓

Sửa dòng đã tồn tại.

Giống như Excel.

Trước

| Name |
| --- |
| An  |

Sau

| Name |
| --- |
| Nguyễn Văn An |

---

# 3. Cú pháp

```text-x-trilium-auto
UPDATE table_name
SET column = value WHERE condition;
```

---

Ví dụ

```text-x-trilium-auto
UPDATE students
SET age = 21 WHERE id = 1;
```

Kết quả

| id  | name | age |
| --- | --- | --- |
| 1   | An  | 21  |

Chỉ dòng có

```text-x-trilium-auto
id = 1
```

được cập nhật.

---

# 4. Vai trò của WHERE

Đây là phần quan trọng nhất.

Ví dụ

```text-x-trilium-auto
UPDATE students
SET city = 'Hồ Chí Minh' WHERE id = 3;
```

Kết quả

| id  | city |
| --- | --- |
| 3   | Hồ Chí Minh |

Chỉ một dòng bị thay đổi.

---

# 5. Quên WHERE

Đây là lỗi kinh điển.

```text-x-trilium-auto
UPDATE students
SET city = 'Hồ Chí Minh';
```

Điều gì xảy ra?

SQLite sẽ cập nhật

**toàn bộ bảng**.

| id  | city |
| --- | --- |
| 1   | Hồ Chí Minh |
| 2   | Hồ Chí Minh |
| 3   | Hồ Chí Minh |
| 4   | Hồ Chí Minh |

⚠ Đây là một trong những lỗi nghiêm trọng nhất trong SQL.

---

# 6. UPDATE nhiều cột

```text-x-trilium-auto
UPDATE students
SET
    age = 21,
    city = 'Đà Nẵng' WHERE id = 1;
```

Kết quả

| id  | age | city |
| --- | --- | --- |
| 1   | 21  | Đà Nẵng |

---

# 7. UPDATE bằng biểu thức

Ví dụ

Tăng lương

1000

```text-x-trilium-auto
UPDATE students
SET salary = salary + 1000;
```

Kết quả

| name | salary |
| --- | --- |
| An  | 9000 |
| Bình | 10500 |
| Lan | 8000 |
| Mai | 9500 |

SQLite tính:

```text-x-trilium-auto
salary mới

=

salary cũ

+

1000
```

---

# 8. UPDATE theo điều kiện

Ví dụ

Tăng lương

người ở Huế

```text-x-trilium-auto
UPDATE students
SET salary = salary + 500 WHERE city = 'Huế';
```

Kết quả

| name | salary |
| --- | --- |
| Bình | 10000 |
| Mai | 9000 |

---

# 9. UPDATE với nhiều điều kiện

```text-x-trilium-auto
UPDATE students
SET salary = salary + 1000 WHERE city='Huế' AND age>=20;
```

Chỉ những người thỏa mãn **cả hai điều kiện** mới được cập nhật.

---

# 10. UPDATE với IN

```text-x-trilium-auto
UPDATE students
SET city='TP.HCM' WHERE id IN (2,4);
```

Kết quả

| id  | city |
| --- | --- |
| 2   | TP.HCM |
| 4   | TP.HCM |

---

# 11. UPDATE với BETWEEN

```text-x-trilium-auto
UPDATE students
SET salary = salary + 500 WHERE age BETWEEN 20 AND 22;
```

---

# 12. UPDATE bằng Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute(
    """
    UPDATE students
    SET age = ?
    WHERE id = ?
    """,
    (21, 1)
)

conn.commit()

conn.close()
```

---

# 13. Placeholder

Sai

```text-x-trilium-auto
age = 21 id = 1

sql = f"""
UPDATE students
SET age={age}
WHERE id={id}
"""
```

Đừng nối chuỗi SQL.

---

Đúng

```text-x-trilium-auto
cursor.execute(
    """
    UPDATE students
    SET age=?
    WHERE id=?
    """,
    (21,1)
)
```

---

# 14. cursor.rowcount

Sau UPDATE

SQLite biết

đã sửa bao nhiêu dòng.

```text-x-trilium-auto
cursor.execute(
    """
    UPDATE students
    SET city=?
    WHERE city=?
    """,
    ("Huế","Đà Nẵng")
)

print(cursor.rowcount)
```

Ví dụ

```text-x-trilium-auto
1
```

Nghĩa là

đã cập nhật

1 dòng.

---

# 15. UPDATE không tìm thấy dữ liệu

Ví dụ

```text-x-trilium-auto
UPDATE students
SET age=30 WHERE id=100;
```

Không lỗi.

Nhưng

```text-x-trilium-auto
0 row updated
```

Trong Python

```text-x-trilium-auto
print(cursor.rowcount)
```

↓

```text-x-trilium-auto
0
```

Bạn có thể dùng `rowcount` để kiểm tra xem bản ghi có tồn tại hay không.

---

# 16. Transaction

Trong thực tế

Ví dụ

```text-x-trilium-auto
Cập nhật lương

↓

Ghi log

↓

Cập nhật thống kê
```

Ba bước

phải cùng thành công.

Nếu một bước lỗi

↓

Rollback.

Đây chính là Transaction mà chúng ta sẽ học chuyên sâu ở Buổi 18.

---

# 17. Quy trình an toàn

Lập trình viên giàu kinh nghiệm thường làm như sau:

Bước 1

```text-x-trilium-auto
SELECT * FROM students
WHERE id=3;
```

Kiểm tra

↓

Đúng dữ liệu

↓

Mới UPDATE.

Đặc biệt với dữ liệu quan trọng.

---

# 18. Ví dụ hoàn chỉnh

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute(
    """
    UPDATE students
    SET salary = salary + ?
    WHERE city = ?
    """,
    (1000, "Huế")
)

print("Đã cập nhật:", cursor.rowcount)

conn.commit()

conn.close()
```

---

# 19. Sơ đồ hoạt động

```text-x-trilium-auto
UPDATE

↓

WHERE

↓

Tìm các dòng phù hợp

↓

SET

↓

Thay đổi dữ liệu

↓

commit()

↓

Ghi xuống file
```

---

# Những lỗi rất nguy hiểm

## Lỗi 1

Không có

```text-x-trilium-auto
WHERE
```

Sai

```text-x-trilium-auto
UPDATE students
SET salary=0;
```

Hậu quả

↓

Mọi người

↓

Lương = 0

---

## Lỗi 2

Không commit

```text-x-trilium-auto
conn.commit()
```

Quên

↓

Không lưu.

---

## Lỗi 3

Nối chuỗi SQL

Sai

```text-x-trilium-auto
f"..."
```

Đúng

```text-x-trilium-auto
?
```

---

## Lỗi 4

Không kiểm tra rowcount

Nếu

```text-x-trilium-auto
rowcount=0
```

Có thể

- Sai ID
- Sai điều kiện
- Không có dữ liệu

Ứng dụng nên xử lý trường hợp này (ví dụ thông báo "Không tìm thấy sinh viên cần cập nhật").

---

# 20. Một ví dụ thực tế

Hệ thống đọc truyện.

Người dùng đọc xong

↓

Cập nhật

```text-x-trilium-auto
last_read_chapter
```

SQL

```text-x-trilium-auto
UPDATE reading_progress
SET last_read_chapter = 125 WHERE user_id = 1 AND story_id = 99;
```

Đây là thao tác rất phổ biến trong các ứng dụng.

---

# Tổng kết buổi 9

Hôm nay bạn đã học:

- UPDATE
- SET
- WHERE
- Cập nhật một cột
- Cập nhật nhiều cột
- Biểu thức trong UPDATE
- Placeholder
- rowcount
- Transaction (giới thiệu)
- Quy trình UPDATE an toàn

---

# Bài tập

## Bài 1

Đổi tên

```text-x-trilium-auto
An
```

thành

```text-x-trilium-auto
Nguyễn Văn An
```

---

## Bài 2

Tăng lương

500

cho tất cả sinh viên

ở

```text-x-trilium-auto
Huế
```

---

## Bài 3

Đổi thành phố

```text-x-trilium-auto
Đà Nẵng
```

thành

```text-x-trilium-auto
Hồ Chí Minh
```

---

## Bài 4

Viết chương trình Python

cập nhật

tuổi

của

```text-x-trilium-auto
id = 2
```

---

## Bài 5

Sau UPDATE

In ra

```text-x-trilium-auto
cursor.rowcount
```

---

## Bài 6 (Thử thách)

Viết hàm:

```text-x-trilium-auto
def increase_salary(city: str, amount: float) -> int:
    ...
```

Yêu cầu:

- Tăng lương cho tất cả sinh viên thuộc `city` thêm `amount`.
- Sử dụng placeholder (`?`).
- `commit()`.
- Trả về số dòng đã được cập nhật (`cursor.rowcount`).
- Đảm bảo đóng kết nối ngay cả khi có lỗi (gợi ý: `try/finally` hoặc `with`).

---

# Góc lập trình viên chuyên nghiệp

Có một nguyên tắc rất nổi tiếng trong SQL:

> **"Không bao giờ chạy UPDATE trên dữ liệu thật nếu chưa chạy SELECT với cùng điều kiện WHERE."**

Ví dụ:

```text-x-trilium-auto
SELECT * FROM students
WHERE city = 'Huế';
```

Nếu kết quả đúng như mong muốn, bạn mới đổi `SELECT *` thành:

```text-x-trilium-auto
UPDATE students
SET salary = salary + 500 WHERE city = 'Huế';
```

Thói quen này đã giúp rất nhiều lập trình viên tránh những sự cố nghiêm trọng khi làm việc với cơ sở dữ liệu sản xuất.

---

## Chuẩn bị cho Buổi 10

Ở **Buổi 10**, chúng ta sẽ học câu lệnh `**DELETE**`:

- Xóa một dòng.
- Xóa nhiều dòng.
- `DELETE` kết hợp `WHERE`.
- `DELETE` trong Python.
- Sự khác nhau giữa `DELETE` và `DROP TABLE`.
- Những lỗi nguy hiểm khi xóa dữ liệu.
- Giới thiệu về **Soft Delete** (đánh dấu xóa) – kỹ thuật được rất nhiều hệ thống thực tế sử dụng để tránh mất dữ liệu vĩnh viễn.