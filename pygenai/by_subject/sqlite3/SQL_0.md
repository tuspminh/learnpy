Để làm chủ SQL (Structured Query Language), bạn cần hiểu rằng các lệnh SQL được chia thành **5 nhóm chính** dựa trên mục đích sử dụng.

Dưới đây là tổng hợp chi tiết từ cơ bản đến nâng cao của từng nhóm lệnh kèm ví dụ cụ thể.

---

## 1. DQL (Data Query Language) - Nhóm lệnh truy vấn dữ liệu

DQL chỉ gồm duy nhất lệnh `SELECT`, nhưng đây là lệnh **quan trọng và phức tạp nhất** trong SQL.

### Mệnh đề đầy đủ của `SELECT`:

```sql
SELECT columns
FROM table_name
JOIN other_table ON condition
WHERE condition
GROUP BY column
HAVING group_condition
ORDER BY column ASC|DESC
LIMIT count OFFSET skip;

```

### Chi tiết các mệnh đề:

* **`SELECT`**: Chọn các cột cần lấy (`*` để lấy tất cả cột).
* **`WHERE`**: Lọc dữ liệu theo điều kiện.
* Các toán tử hay dùng: `=`, `!=`, `>`, `<`, `BETWEEN a AND b`, `IN ('val1', 'val2')`, `LIKE '%keyword%'`.


* **`ORDER BY`**: Sắp xếp kết quả (`ASC` - tăng dần, `DESC` - giảm dần).
* **`GROUP BY`**: Nhóm các hàng có cùng giá trị (thường đi kèm hàm tổng hợp: `COUNT()`, `SUM()`, `AVG()`, `MAX()`, `MIN()`).
* **`HAVING`**: Lọc điều kiện **sau khi** đã `GROUP BY` (khác với `WHERE` là lọc trước khi nhóm).
* **`LIMIT` / `OFFSET**`: Phân trang (lấy bao nhiêu dòng / bỏ qua bao nhiêu dòng).

#### Ví dụ nâng cao với DQL:

```sql
-- Lấy top 5 lớp có điểm trung bình lớn hơn 7.0, sắp xếp giảm dần
SELECT lop, AVG(diem_tb) AS diem_trung_binh, COUNT(*) AS so_luong_sv
FROM sinh_vien
WHERE trang_thai = 'Dang_hoc'
GROUP BY lop
HAVING diem_trung_binh > 7.0
ORDER BY diem_trung_binh DESC
LIMIT 5;

```

---

## 2. DML (Data Manipulation Language) - Nhóm lệnh thao tác dữ liệu

DML dùng để thêm, sửa, xóa các bản ghi (rows) trong bảng.

| Lệnh | Ý nghĩa | Cú pháp mẫu |
| --- | --- | --- |
| **`INSERT`** | Thêm bản ghi mới | `INSERT INTO table (col1, col2) VALUES (val1, val2);` |
| **`UPDATE`** | Cập nhật bản ghi | `UPDATE table SET col1 = val1 WHERE condition;` |
| **`DELETE`** | Xóa bản ghi | `DELETE FROM table WHERE condition;` |

#### Ví dụ cụ thể:

```sql
-- 1. Thêm nhiều bản ghi cùng lúc
INSERT INTO sinh_vien (ten, tuoi, lop) 
VALUES 
    ('Nguyễn Văn A', 20, 'CNTT1'),
    ('Trần Thị B', 21, 'CNTT2');

-- 2. Cập nhật (⚠️ BẮT BUỘC có WHERE, nếu không sẽ sửa TOÀN BỘ bảng)
UPDATE sinh_vien 
SET tuoi = 22, lop = 'CNTT3' 
WHERE id = 1;

-- 3. Xóa (⚠️ BẮT BUỘC có WHERE, nếu không sẽ xóa SẠCH bảng)
DELETE FROM sinh_vien 
WHERE tuoi < 18;

```

---

## 3. DDL (Data Definition Language) - Nhóm lệnh định nghĩa cấu trúc

DDL dùng để tạo, thay đổi hoặc xóa cấu trúc của Database, Table, Index...

### Các lệnh chính:

* **`CREATE`**: Tạo mới bảng, CSDL, Index.
```sql
CREATE TABLE lophoc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_lop TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

```


* **`ALTER`**: Sửa đổi cấu trúc bảng đã tồn tại (Thêm/Sửa/Xóa cột).
```sql
-- Thêm cột email vào bảng
ALTER TABLE sinh_vien ADD COLUMN email TEXT;

-- Đổi tên cột (Trợ giúp trong một số hệ DB nâng cao)
ALTER TABLE sinh_vien RENAME COLUMN ten TO ho_ten;

```


* **`DROP`**: Xóa hoàn toàn bảng/CSDL khỏi hệ thống (Không thể phục hồi!).
```sql
DROP TABLE IF EXISTS sinh_vien;

```


* **`TRUNCATE`**: Xóa toàn bộ dữ liệu trong bảng nhưng giữ lại cấu trúc (Nhanh hơn `DELETE` rất nhiều). *(Lưu ý: SQLite không có lệnh TRUNCATE, dùng `DELETE FROM table;` thay thế).*

---

## 4. TCL (Transaction Control Language) - Nhóm lệnh quản lý giao dịch

TCL đảm bảo tính toàn vẹn dữ liệu (Tính chất ACID). Đặc biệt hữu ích trong các hệ thống tài chính/ngân hàng.

* **`BEGIN TRANSACTION`** (hoặc `BEGIN`): Đánh dấu điểm bắt đầu của một giao dịch.
* **`COMMIT`**: Xác nhận lưu vĩnh viễn tất cả thay đổi từ đầu Transaction xuống đĩa cứng.
* **`ROLLBACK`**: Hủy bỏ toàn bộ thao tác trong Transaction, đưa CSDL về trạng thái trước khi `BEGIN`.
* **`SAVEPOINT`**: Tạo điểm mốc trong Transaction để có thể `ROLLBACK` về từng phần.

#### Ví dụ mô phỏng chuyển tiền ngân hàng:

```sql
BEGIN TRANSACTION;

-- Trừ tiền tài khoản A
UPDATE tai_khoan SET so_du = so_du - 1000 WHERE id = 'A';

-- Cộng tiền tài khoản B
UPDATE tai_khoan SET so_du = so_du + 1000 WHERE id = 'B';

-- Nếu 2 câu lệnh trên chạy OK mà không lỗi:
COMMIT;

-- Nếu có bất kỳ lỗi nào xảy ra ở giữa:
-- ROLLBACK;

```

---

## 5. DCL (Data Control Language) - Nhóm lệnh phân quyền

*(Dùng phổ biến trong các CSDL Server như MySQL, PostgreSQL, SQL Server. SQLite chạy dưới dạng file cục bộ nên bỏ qua nhóm này).*

* **`GRANT`**: Cấp quyền truy cập/thao tác cho User.
```sql
GRANT SELECT, INSERT ON sinh_vien TO 'dev_user';

```


* **`REVOKE`**: Thu hồi quyền đã cấp.
```sql
REVOKE INSERT ON sinh_vien FROM 'dev_user';

```



---

## 💡 Bảng tóm tắt các phép nối Bảng (JOIN) phổ biến

Khi làm việc với `SELECT`, kỹ thuật kết nối dữ liệu giữa nhiều bảng (JOIN) là trọng tâm:

| Loại JOIN | Ý nghĩa |
| --- | --- |
| **`INNER JOIN`** | Chỉ lấy các dòng có dữ liệu trùng khớp ở **cả 2 bảng**. |
| **`LEFT JOIN`** | Lấy **tất cả dòng ở bảng bên trái**, khớp được với bảng bên phải thì lấy, không khớp thì điền `NULL`. |
| **`RIGHT JOIN`** | Lấy **tất cả dòng ở bảng bên phải** (tương tự Left Join nhưng ngược lại). |
| **`FULL JOIN`** | Lấy tất cả dữ liệu ở cả 2 bảng, chỗ nào không khớp thì điền `NULL`. |
