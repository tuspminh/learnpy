**DDL (Data Definition Language)** là nhóm lệnh SQL dùng để **định nghĩa, khởi tạo và thay đổi cấu trúc** của các đối tượng trong cơ sở dữ liệu (Database, Table, Index, View, Trigger...). Khác với DML tác động lên dữ liệu (dòng), DDL tác động trực tiếp lên schema (cột, kiểu dữ liệu, khóa, ràng buộc).

---

## 1. Các lệnh DDL cốt lõi

### 🔹 `CREATE` - Tạo mới cấu trúc

Lệnh `CREATE` dùng để khởi tạo Database, Table, Index, hoặc View.

#### Tạo Bảng (Table) kèm Ràng buộc (Constraints):

```sql
CREATE TABLE nhan_vien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    email VARCHAR(100) UNIQUE,
    tuoi INT CHECK (tuoi >= 18),
    luong DECIMAL(10, 2) DEFAULT 10000000.00,
    phong_ban_id INT,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phong_ban_id) REFERENCES phong_ban(id) ON DELETE SET NULL
);

```

#### Tạo Index (Index) để tăng tốc truy vấn:

```sql
CREATE INDEX idx_nhanvien_email ON nhan_vien(email);

```

#### Tạo View (Bảng ảo dựa trên truy vấn SELECT):

```sql
CREATE VIEW v_nhan_vien_luong_cao AS
SELECT ho_ten, luong 
FROM nhan_vien 
WHERE luong > 20000000;

```

---

### 🔹 `ALTER` - Thay đổi cấu trúc hiện có

Dùng khi cần thay đổi bảng đã tồn tại mà không muốn làm mất dữ liệu hiện có.

```sql
-- 1. Thêm cột mới
ALTER TABLE nhan_vien ADD COLUMN so_dien_thoai VARCHAR(15);

-- 2. Đổi tên cột (SQLite / PostgreSQL / MySQL 8.0+)
ALTER TABLE nhan_vien RENAME COLUMN ho_ten TO ten_day_du;

-- 3. Xóa cột
ALTER TABLE nhan_vien DROP COLUMN so_dien_thoai;

-- 4. Đổi tên bảng
ALTER TABLE nhan_vien RENAME TO nhan_su;

```

---

### 🔹 `DROP` - Xóa bỏ hoàn toàn đối tượng

Lệnh `DROP` xóa vĩnh viễn đối tượng bao gồm cấu trúc và toàn bộ dữ liệu bên trong khỏi hệ thống (Không thể khôi phục).

```sql
-- Xóa bảng (dùng IF EXISTS để tránh báo lỗi nếu bảng không tồn tại)
DROP TABLE IF EXISTS nhan_vien;

-- Xóa Index / View
DROP INDEX IF EXISTS idx_nhanvien_email;
DROP VIEW IF EXISTS v_nhan_vien_luong_cao;

```

---

### 🔹 `TRUNCATE` - Xóa sạch dữ liệu, giữ lại khung bảng

Lệnh `TRUNCATE` xóa toàn bộ dòng dữ liệu và reset lại các cột tự tăng (`AUTO_INCREMENT`). Nó là lệnh DDL nên xử lý ở cấp độ bộ nhớ đĩa cứng, chạy nhanh hơn nhiều so với `DELETE` (DML).

```sql
TRUNCATE TABLE nhan_vien;

```

*(Lưu ý: SQLite không có lệnh `TRUNCATE TABLE`, bạn dùng `DELETE FROM nhan_vien;` để thay thế).*

---

## 2. Bảng tổng hợp các Ràng buộc (Constraints) trong DDL

Ràng buộc giúp duy trì tính toàn vẹn dữ liệu (Data Integrity) ngay từ bước định nghĩa cấu trúc:

| Ràng buộc | Cú pháp mẫu | Ý nghĩa |
| --- | --- | --- |
| **`PRIMARY KEY`** | `id INT PRIMARY KEY` | Khóa chính, định danh duy nhất cho mỗi dòng, tự động gán `NOT NULL` và `UNIQUE`. |
| **`FOREIGN KEY`** | `FOREIGN KEY (fk_id) REFERENCES table(id)` | Khóa ngoại, thiết lập mối quan hệ và duy trì toàn vẹn tham chiếu giữa các bảng. |
| **`NOT NULL`** | `ten TEXT NOT NULL` | Bắt buộc cột phải chứa dữ liệu, không được để trống (`NULL`). |
| **`UNIQUE`** | `email VARCHAR(255) UNIQUE` | Đảm bảo giá trị trong cột không được trùng lặp giữa các dòng. |
| **`CHECK`** | `CHECK (tuoi >= 18)` | Lọc quy tắc hợp lệ cho dữ liệu trước khi cho phép chèn hoặc sửa. |
| **`DEFAULT`** | `trang_thai TEXT DEFAULT 'Active'` | Tự động điền giá trị mặc định nếu không có dữ liệu truyền vào. |

---

## 3. Các quy tắc quan trọng khi chạy DDL trên Production

* **Tự động COMMIT (Implicit Commit):** Trên hầu hết hệ CSDL (như MySQL, Oracle), lệnh DDL sẽ tự động thực thi `COMMIT` ngay lập tức và **không thể `ROLLBACK**` được kể cả khi nằm trong khối lệnh Transaction. *(Trừ PostgreSQL và SQLite có hỗ trợ Transactional DDL).*
* **Tránh Lock bảng trên DB lớn:** Khi chạy `ALTER TABLE` trên các bảng chứa hàng triệu dòng, DB Engine sẽ thực hiện khóa bảng (Exclusive Lock). Việc này khiến mọi thao tác ghi/đọc của ứng dụng bị treo (Downtime).
* **Quản lý bằng Migration Tool:** Không bao giờ gõ trực tiếp lệnh DDL bằng tay trên Production. Luôn quản lý cấu trúc DB bằng mã nguồn thông qua các công cụ **Database Migration** như:
* **Python:** Alembic (SQLAlchemy), Django Migrations.
* **Node.js:** Prisma, TypeORM, Knex.
* **Độc lập:** Flyway, Liquibase.