**DML (Data Manipulation Language)** là nhóm lệnh dùng để **thao tác trực tiếp với dữ liệu** bên trong các bảng. Nếu DDL giúp bạn xây khung nhà, DQL giúp bạn nhìn vào bên trong, thì DML chính là các công cụ giúp bạn mang đồ đạc vào, sắp xếp lại hoặc bỏ đồ cũ đi.

Nhóm DML gồm 3 lệnh cốt lõi: **`INSERT`**, **`UPDATE`**, **`DELETE`**, cùng kỹ thuật kết hợp **`UPSERT` (MERGE)**.

---

## 1. `INSERT` - Thêm dữ liệu mới

Lệnh `INSERT` dùng để thêm một hoặc nhiều bản ghi (rows) mới vào bảng.

### A. Thêm 1 bản ghi đơn lẻ

Luôn luôn **chỉ định rõ danh sách cột** muốn thêm dữ liệu. Tránh bỏ qua tên cột vì nếu cấu trúc bảng thay đổi sau này, code của bạn sẽ bị vỡ.

```sql
INSERT INTO san_pham (ten_sp, gia, so_luong_kho, danh_muc_id)
VALUES ('Bàn phím cơ', 1500000, 50, 2);

```

### B. Thêm hàng loạt bản ghi (Batch Insert)

Thêm nhiều dòng trong một câu lệnh duy nhất giúp giảm thiểu Network Overhead và tăng tốc độ xử lý lên gấp hàng chục lần so với việc gọi `INSERT` từng dòng riêng lẻ.

```sql
INSERT INTO san_pham (ten_sp, gia, so_luong_kho, danh_muc_id)
VALUES 
    ('Chuột không dây', 450000, 100, 2),
    ('Tai nghe Gaming', 1200000, 30, 2),
    ('Lót chuột RGB', 250000, 200, 2);

```

### C. `INSERT INTO ... SELECT` (Sao chép dữ liệu)

Thêm dữ liệu vào bảng mới dựa trên kết quả truy vấn từ bảng khác.

```sql
-- Sao chép tất cả sản phẩm hết hàng sang bảng lưu trữ tạm
INSERT INTO san_pham_het_hang (san_pham_id, ten_sp, ngay_luu)
SELECT id, ten_sp, CURRENT_TIMESTAMP
FROM san_pham
WHERE so_luong_kho = 0;

```

---

## 2. `UPDATE` - Cập nhật dữ liệu hiện có

Lệnh `UPDATE` dùng để sửa đổi giá trị của một hoặc nhiều cột trong các bản ghi đã tồn tại.

### A. Cú pháp cơ bản

```sql
UPDATE san_pham
SET gia = 1350000,
    so_luong_kho = so_luong_kho + 20
WHERE id = 5;

```

### B. `UPDATE` kết hợp tính toán hoặc Subquery

Bạn có thể cập nhật dữ liệu dựa trên giá trị của bảng khác.

```sql
-- Giảm 10% giá cho tất cả sản phẩm thuộc danh mục 'Sách'
UPDATE san_pham
SET gia = gia * 0.9
WHERE danh_muc_id = (
    SELECT id FROM danh_muc WHERE ten_danh_muc = 'Sách'
);

```

> ⚠️ **CẢNH BÁO TỪ DEVELOPER:**
> * Luôn luôn viết mệnh đề `WHERE` trước khi chạy `UPDATE`. Nếu quên `WHERE`, bạn sẽ **thay đổi toàn bộ dữ liệu của cả bảng**!
> * **Mẹo an toàn:** Hãy đổi chữ `UPDATE ... SET ...` thành `SELECT * FROM ...` và chạy thử với `WHERE` đó trước để kiểm tra xem những dòng nào sẽ bị ảnh hưởng.
> 
> 

---

## 3. `DELETE` - Xóa dữ liệu

Lệnh `DELETE` loại bỏ một hoặc nhiều dòng dữ liệu khỏi bảng dựa trên điều kiện lọc.

### A. Cú pháp cơ bản

```sql
DELETE FROM don_hang
WHERE trang_thai = 'Chờ thanh toán' 
  AND ngay_tao < '2026-01-01';

```

### B. Phân biệt `DELETE` vs `TRUNCATE` vs `DROP`

Đây là câu hỏi phỏng vấn kinh điển dành cho lập trình viên:

| Đặc điểm | `DELETE` (DML) | `TRUNCATE` (DDL) | `DROP` (DDL) |
| --- | --- | --- | --- |
| **Hành động** | Xóa từng dòng theo điều kiện `WHERE` | Xóa **sạch toàn bộ** dữ liệu trong bảng | Xóa **hoàn toàn cấu trúc bảng** và dữ liệu |
| **Tốc độ** | Chậm (Ghi log từng dòng xóa) | Cực nhanh (Giải phóng bộ nhớ trực tiếp) | Rất nhanh |
| **Mệnh đề WHERE** | **Có** hỗ trợ | **Không** hỗ trợ | **Không** hỗ trợ |
| **Khôi phục (Rollback)** | Có thể Rollback trong Transaction | Khó/Không thể Rollback (tùy Hệ DB) | Không thể Rollback |
| **Reset ID Auto-increment** | **Không** reset (ID tiếp theo nối tiếp) | **Có** reset về 1 | Mất luôn bảng |

---

## 4. `UPSERT` / `ON CONFLICT` - Kỹ thuật Nâng cao

Trong thực tế, bạn thường gặp bài toán: *"Nếu bản ghi chưa có thì thêm mới (`INSERT`), nếu đã có rồi (trùng Primary Key hoặc Unique Key) thì cập nhật (`UPDATE`)"*. Kỹ thuật này gọi là **UPSERT**.

### A. Cú pháp chuẩn SQLite / PostgreSQL (`ON CONFLICT`):

```sql
INSERT INTO cau_hinh_user (user_id, dark_mode, ngon_ngu)
VALUES (101, 1, 'vi')
ON CONFLICT(user_id) 
DO UPDATE SET 
    dark_mode = EXCLUDED.dark_mode,
    ngon_ngu = EXCLUDED.ngon_ngu;

```

### B. Cú pháp MySQL (`ON DUPLICATE KEY UPDATE`):

```sql
INSERT INTO cau_hinh_user (user_id, dark_mode, ngon_ngu)
VALUES (101, 1, 'vi')
ON DUPLICATE KEY UPDATE 
    dark_mode = VALUES(dark_mode),
    ngon_ngu = VALUES(ngon_ngu);

```

---

## 🛡️ Nguyên tắc an toàn tuyệt đối khi làm việc với DML

### 1. Luôn đưa các lệnh DML quan trọng vào Transaction

Khi thực hiện xóa hoặc sửa nhiều dữ liệu, hãy bọc chúng trong **Transaction**. Nếu lỡ tay xóa sai, bạn vẫn còn cơ hội cứu dữ liệu bằng `ROLLBACK`.

```sql
BEGIN TRANSACTION;

-- Thao tác DML nguy hiểm
DELETE FROM khach_hang WHERE trang_thai = 'Khong_hoat_dong';

-- Kiểm tra lại số lượng dòng bị ảnh hưởng:
-- Nếu thấy đúng -> COMMIT
COMMIT;

-- Nếu phát hiện xóa nhầm -> ROLLBACK ngay lập tức!
-- ROLLBACK;

```

### 2. Tránh lỗ hổng SQL Injection khi viết ứng dụng

Khi thao tác DML từ ngôn ngữ lập trình (Python, C#, Java, Node.js...), **tuyệt đối không cộng chuỗi SQL**. Luôn dùng **Parameterized Queries / Prepared Statements**.

```python
# ❌ RẤT NGUY HIỂM (Dễ bị SQL Injection)
sql = f"DELETE FROM users WHERE username = '{user_input}'"

# ✅ AN TOÀN (Dùng Tham số hóa)
sql = "DELETE FROM users WHERE username = ?"
cursor.execute(sql, (user_input,))

```

### 3. Xóa/Sửa dữ liệu lớn theo từng đợt (Batching DML)

Nếu bạn cần xóa 10 triệu dòng dữ liệu bằng lệnh `DELETE FROM log WHERE ngay < '2025-01-01';`, câu lệnh sẽ làm khóa bảng (Table Lock), ngốn hết CPU/RAM và làm treo hệ thống.

👉 **Giải pháp:** Chia nhỏ để xóa thành từng đợt (ví dụ: mỗi lần xóa 5,000 dòng trong vòn lặp `WHILE` cho đến khi hết).