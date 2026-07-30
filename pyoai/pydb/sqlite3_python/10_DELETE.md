# Khóa học SQLite3 từ Cơ bản đến Chuyên sâu

# Buổi 10: DELETE – Xóa dữ liệu an toàn

> Sau INSERT, SELECT và UPDATE, hôm nay chúng ta sẽ học câu lệnh cuối cùng trong nhóm CRUD:
> 
> - **C**reate → INSERT
> - **R**ead → SELECT
> - **U**pdate → UPDATE
> - **D**elete → DELETE ← Buổi hôm nay

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

- DELETE là gì
- DELETE với WHERE
- DELETE nhiều dòng
- DELETE toàn bộ bảng
- DELETE và DROP khác nhau
- DELETE và TRUNCATE khác nhau
- DELETE trong Python
- rowcount
- Transaction khi DELETE
- Soft Delete
- Các lỗi cực kỳ nguy hiểm

---

# 1. Chuẩn bị dữ liệu

Giả sử bảng

```text-x-trilium-auto
students
```

| id  | name | age | city |
| --- | --- | --- | --- |
| 1   | An  | 20  | Hà Nội |
| 2   | Bình | 22  | Huế |
| 3   | Lan | 19  | Đà Nẵng |
| 4   | Mai | 20  | Huế |
| 5   | Nam | 23  | Hà Nội |

---

# 2. DELETE là gì?

DELETE dùng để

> Xóa dữ liệu khỏi bảng.

Khác với

```text-x-trilium-auto
DROP TABLE
```

DELETE chỉ xóa **dữ liệu**

↓

Bảng vẫn còn.

---

# 3. Cú pháp

```text-x-trilium-auto
DELETE FROM table_name
WHERE condition;
```

Ví dụ

```text-x-trilium-auto
DELETE FROM students
WHERE id = 3;
```

Kết quả

| id  | name |
| --- | --- |
| 1   | An  |
| 2   | Bình |
| 4   | Mai |
| 5   | Nam |

Lan đã bị xóa.

---

# 4. DELETE nhiều dòng

Ví dụ

```text-x-trilium-auto
DELETE FROM students
WHERE city = 'Huế';
```

Kết quả

| id  | name |
| --- | --- |
| 1   | An  |
| 3   | Lan |
| 5   | Nam |

Cả Bình và Mai đều bị xóa.

---

# 5. DELETE với nhiều điều kiện

```text-x-trilium-auto
DELETE FROM students
WHERE city='Huế' AND age>=20;
```

SQLite sẽ xóa tất cả dòng thỏa mãn điều kiện.

---

# 6. DELETE với IN

```text-x-trilium-auto
DELETE FROM students
WHERE id IN (2,4,5);
```

Rất hữu ích khi xóa nhiều bản ghi theo danh sách ID.

---

# 7. DELETE với BETWEEN

```text-x-trilium-auto
DELETE FROM students
WHERE age BETWEEN 18 AND 20;
```

Sẽ xóa tất cả sinh viên từ 18 đến 20 tuổi.

---

# 8. Điều gì xảy ra với AUTOINCREMENT?

Giả sử

Có

```text-x-trilium-auto
1
2
3
4
5
```

Xóa

```text-x-trilium-auto
3
```

Còn

```text-x-trilium-auto
1
2
4
5
```

INSERT thêm

```text-x-trilium-auto
Hoa
```

ID mới sẽ là

```text-x-trilium-auto
6
```

**Không phải**

```text-x-trilium-auto
3
```

SQLite không tái sử dụng ID khi dùng `AUTOINCREMENT`.

---

# 9. DELETE toàn bộ dữ liệu

```text-x-trilium-auto
DELETE FROM students;
```

Điều gì xảy ra?

| id  | name |
| --- | --- |
| (rỗng) | (rỗng) |

Bảng vẫn tồn tại.

---

# 10. DELETE khác DROP TABLE

DELETE

```text-x-trilium-auto
DELETE FROM students;
```

Sau đó

```text-x-trilium-auto
SELECT * FROM students;
```

↓

Vẫn chạy được

↓

Bảng còn.

---

DROP

```text-x-trilium-auto
DROP TABLE students;
```

Sau đó

```text-x-trilium-auto
SELECT * FROM students;
```

↓

Lỗi

```text-x-trilium-auto
no such table
```

Bảng đã bị xóa hoàn toàn.

---

# 11. DELETE khác TRUNCATE

Trong MySQL

Có

```text-x-trilium-auto
TRUNCATE TABLE students;
```

SQLite

❌ Không hỗ trợ `TRUNCATE`.

Thay thế bằng

```text-x-trilium-auto
DELETE FROM students;
```

---

# 12. DELETE bằng Python

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute(
    """
    DELETE
    FROM students
    WHERE id=?
    """,
    (3,)
)

conn.commit()

conn.close()
```

---

# 13. Placeholder

Sai

```text-x-trilium-auto
id = 3

sql = f"""
DELETE FROM students
WHERE id={id}
"""
```

Đúng

```text-x-trilium-auto
cursor.execute(
    """
    DELETE FROM students
    WHERE id=?
    """,
    (3,)
)
```

---

# 14. rowcount

```text-x-trilium-auto
cursor.execute(
    """
    DELETE FROM students
    WHERE city=?
    """,
    ("Huế",)
)

print(cursor.rowcount)
```

Ví dụ

```text-x-trilium-auto
2
```

Nghĩa là

đã xóa

2 dòng.

---

# 15. Không tìm thấy dữ liệu

```text-x-trilium-auto
DELETE FROM students
WHERE id=100;
```

Không báo lỗi.

Chỉ

```text-x-trilium-auto
0 rows deleted
```

Python

```text-x-trilium-auto
print(cursor.rowcount)
```

↓

```text-x-trilium-auto
0
```

---

# 16. Transaction

Ví dụ

```text-x-trilium-auto
DELETE chương truyện

↓

DELETE bình luận

↓

DELETE lịch sử đọc
```

Ba bước

↓

Phải cùng thành công.

Nếu bước thứ hai lỗi

↓

Rollback.

Chúng ta sẽ học kỹ ở phần Transaction.

---

# 17. Soft Delete

Trong thực tế

Rất nhiều hệ thống

KHÔNG xóa thật.

Ví dụ

```text-x-trilium-auto
users
```

| id  | name | deleted |
| --- | --- | --- |
| 1   | An  | 0   |
| 2   | Bình | 1   |

`deleted=1`

↓

Đã xóa

↓

Nhưng dữ liệu vẫn còn.

---

Khi SELECT

```text-x-trilium-auto
SELECT * FROM users
WHERE deleted=0;
```

Người dùng chỉ nhìn thấy dữ liệu chưa bị xóa.

---

# 18. Vì sao dùng Soft Delete?

Ví dụ

Khách hàng

↓

Lỡ xóa truyện.

Nếu xóa thật

↓

Không khôi phục được.

Nếu Soft Delete

↓

Chỉ cần

```text-x-trilium-auto
UPDATE users
SET deleted=0;
```

↓

Khôi phục.

Đây là kỹ thuật rất phổ biến trong các hệ thống doanh nghiệp.

---

# 19. Ví dụ hoàn chỉnh

```text-x-trilium-auto
import sqlite3

conn = sqlite3.connect("student.db")

cursor = conn.cursor()

cursor.execute(
    """
    DELETE
    FROM students
    WHERE city=?
    """,
    ("Huế",)
)

print("Đã xóa:", cursor.rowcount)

conn.commit()

conn.close()
```

---

# 20. Quy trình an toàn

Lập trình viên nhiều kinh nghiệm

Không bao giờ

DELETE ngay.

Bước 1

```text-x-trilium-auto
SELECT * FROM students
WHERE city='Huế';
```

↓

Kiểm tra

↓

Đúng

↓

Mới

```text-x-trilium-auto
DELETE FROM students
WHERE city='Huế';
```

---

# 21. Những lỗi cực kỳ nguy hiểm

## Lỗi 1

Quên WHERE

```text-x-trilium-auto
DELETE FROM students;
```

↓

Toàn bộ dữ liệu

↓

Biến mất.

---

## Lỗi 2

Không commit

```text-x-trilium-auto
conn.commit()
```

↓

Không lưu.

---

## Lỗi 3

Không backup

Database thật

↓

DELETE nhầm

↓

Không cứu được.

---

## Lỗi 4

Không dùng placeholder

Sai

```text-x-trilium-auto
f"..."
```

Đúng

```text-x-trilium-auto
?
```

---

## Lỗi 5

Không kiểm tra rowcount

Ví dụ

```text-x-trilium-auto
if cursor.rowcount == 0:
    print("Không tìm thấy dữ liệu cần xóa")
```

Đây là cách xử lý tốt trong ứng dụng.

---

# 22. Ví dụ thực tế

Dự án crawler truyện của bạn

Người dùng

↓

Xóa

một truyện.

Nếu

DELETE thật

↓

Mất toàn bộ

- chương
- lịch sử đọc
- bookmark

Giải pháp

↓

Soft Delete

```text-x-trilium-auto
UPDATE stories
SET deleted=1 WHERE id=?;
```

Các truy vấn hiển thị truyện sẽ luôn có điều kiện:

```text-x-trilium-auto
SELECT * FROM stories
WHERE deleted=0;
```

---

# Tổng kết buổi 10

Hôm nay bạn đã học:

- DELETE
- WHERE
- DELETE nhiều dòng
- DELETE toàn bộ bảng
- DELETE và DROP
- DELETE và TRUNCATE
- Placeholder
- rowcount
- Soft Delete
- Quy trình DELETE an toàn

---

# Bài tập

## Bài 1

Xóa sinh viên

```text-x-trilium-auto
id = 3
```

---

## Bài 2

Xóa tất cả sinh viên ở

```text-x-trilium-auto
Huế
```

---

## Bài 3

Viết chương trình Python

Xóa

```text-x-trilium-auto
id = 5
```

---

## Bài 4

Sau DELETE

In

```text-x-trilium-auto
cursor.rowcount
```

---

## Bài 5

Thiết kế bảng

```text-x-trilium-auto
stories
```

Có cột

```text-x-trilium-auto
deleted
```

Thực hiện Soft Delete thay vì DELETE thật.

---

# Thử thách

Viết hàm:

```text-x-trilium-auto
def delete_student(student_id: int) -> bool:
    ...
```

Yêu cầu:

- Kết nối SQLite.
- Xóa sinh viên theo `student_id` bằng placeholder (`?`).
- `commit()`.
- Trả về `True` nếu xóa thành công (`rowcount > 0`), ngược lại trả về `False`.
- Đảm bảo đóng kết nối kể cả khi xảy ra lỗi.

---

# Góc lập trình viên chuyên nghiệp

Một nguyên tắc rất quan trọng:

> **"Đừng bao giờ chạy DELETE trực tiếp trên dữ liệu quan trọng khi chưa kiểm tra bằng SELECT."**

Ví dụ:

```text-x-trilium-auto
SELECT * FROM students
WHERE id = 10;
```

Nếu đúng bản ghi cần xóa, mới thực hiện:

```text-x-trilium-auto
DELETE FROM students
WHERE id = 10;
```

Đây là thói quen đơn giản nhưng giúp tránh rất nhiều sự cố trong môi trường sản xuất.

---

# Chuẩn bị cho Buổi 11

Đến đây, bạn đã thành thạo **CRUD**:

- ✅ INSERT
- ✅ SELECT
- ✅ UPDATE
- ✅ DELETE

Từ **Buổi 11**, chúng ta sẽ bước sang phần **truy vấn nâng cao**.

Chủ đề đầu tiên là **SQLite Functions**:

- Hàm số học.
- Hàm chuỗi (`LENGTH`, `UPPER`, `LOWER`, `TRIM`, `SUBSTR`, `REPLACE`...).
- Hàm ngày giờ (`DATE`, `TIME`, `DATETIME`, `STRFTIME`).
- Hàm xử lý `NULL` (`IFNULL`, `COALESCE`, `NULLIF`).
- Cách kết hợp các hàm trong `SELECT`, `UPDATE` và `WHERE`.

Đây là nền tảng để viết các truy vấn mạnh mẽ, ngắn gọn và hiệu quả trong các ứng dụng thực tế.