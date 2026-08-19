**DCL (Data Control Language)** là nhóm lệnh SQL dùng để **quản lý quyền truy cập và phân quyền bảo mật** đối với các đối tượng trong cơ sở dữ liệu (Database, Table, View, Stored Procedure...).

DCL giúp Quản trị viên CSDL (DBA) quyết định **Ai** (User/Role) được phép làm **Cái gì** (Select, Insert, Update...) trên **Đối tượng nào**.

> ⚠️ **Lưu ý:** DCL áp dụng cho các hệ CSDL Quản trị Client-Server (như MySQL, PostgreSQL, SQL Server, Oracle). CSDL dạng file cục bộ như **SQLite không hỗ trợ DCL** (SQLite quản lý quyền thông qua phân quyền file của Hệ điều hành).

---

## 1. Hai lệnh DCL cốt lõi: `GRANT` và `REVOKE`

### 🔹 Lệnh `GRANT` - Cấp quyền

Lệnh `GRANT` dùng để trao quyền thao tác cho một hoặc nhiều người dùng (Users) hoặc nhóm quyền (Roles).

#### Cú pháp tổng quát:

```sql
GRANT privilege_list 
ON object_name 
TO user_name [WITH GRANT OPTION];

```

* `privilege_list`: Danh sách quyền (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `EXECUTE`, `ALL PRIVILEGES`...).
* `object_name`: Đối tượng được cấp quyền (Tên bảng, Database, View...).
* `user_name`: Tài khoản nhận quyền (`'dev_user'@'localhost'` hoặc `'analyst'@'%'`).
* `WITH GRANT OPTION`: *(Tùy chọn)* Cho phép User này **tiếp tục cấp quyền đó cho người khác**.

#### Ví dụ cụ thể:

```sql
-- 1. Cấp quyền chỉ được ĐỌC (SELECT) trên bảng nhan_vien cho User 'nv_ke_toan'
GRANT SELECT ON csdl_cong_ty.nhan_vien TO 'nv_ke_toan'@'localhost';

-- 2. Cấp quyền ĐỌC và SỬA trên toàn bộ các bảng thuộc Database 'csdl_cong_ty'
GRANT SELECT, UPDATE ON csdl_cong_ty.* TO 'dev_user'@'%';

-- 3. Cấp TOÀN BỘ quyền trên bảng san_pham
GRANT ALL PRIVILEGES ON csdl_cong_ty.san_pham TO 'admin_kho'@'localhost';

```

---

### 🔹 Lệnh `REVOKE` - Thu hồi quyền

Lệnh `REVOKE` dùng để tước bỏ các quyền đã được cấp trước đó của User.

#### Cú pháp tổng quát:

```sql
REVOKE privilege_list 
ON object_name 
FROM user_name;

```

#### Ví dụ cụ thể:

```sql
-- 1. Thu hồi quyền UPDATE trên bảng nhan_vien của User 'dev_user'
REVOKE UPDATE ON csdl_cong_ty.nhan_vien FROM 'dev_user'@'%';

-- 2. Thu hồi TOÀN BỘ quyền trên Database 'csdl_cong_ty'
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'dev_user'@'%';

```

---

## 2. Các cấp độ phân quyền trong DCL (Privilege Levels)

Bạn có thể giới hạn phạm vi quyền từ mức toàn hệ thống xuống đến từng cột dữ liệu cụ thể:

| Cấp độ | Cú pháp `ON ...` | Mô tả | Ví dụ |
| --- | --- | --- | --- |
| **Global (Toàn cục)** | `ON *.*` | Áp dụng cho **tất cả Database** trên Server. | `GRANT SELECT ON *.* TO 'auditor';` |
| **Database** | `ON db_name.*` | Áp dụng cho **mọi bảng** trong 1 Database cụ thể. | `GRANT ALL ON csdl_ban_hang.* TO 'dev';` |
| **Table (Bảng)** | `ON db_name.table_name` | Chỉ áp dụng cho **1 bảng** nhất định. | `GRANT SELECT ON csdl.san_pham TO 'user';` |
| **Column (Cột)** | `ON db_name.table_name(col1, col2)` | Chỉ cho phép thao tác trên **các cột được chỉ định**. | `GRANT UPDATE(ho_ten, so_dien_thoai) ON csdl.nhan_vien TO 'hr_user';` |

---

## 3. Quy trình Quản lý quyền chuẩn: RBAC (Role-Based Access Control)

Tránh cấp quyền trực tiếp cho từng User cá nhân vì rất khó quản lý khi nhân sự thay đổi. Thực hành chuẩn của Developer/DBA là: **Tạo Role (Nhóm quyền) $\rightarrow$ Cấp quyền cho Role $\rightarrow$ Gán User vào Role**.

### Ví dụ quy trình thiết lập phân quyền cho hệ thống Bán hàng:

```sql
-- Bước 1: Tạo các Role tương ứng với vị trí công việc
CREATE ROLE 'role_nhan_vien_cskh';
CREATE ROLE 'role_nha_phat_trien';

-- Bước 2: Cấp quyền tương ứng cho các Role
-- Nhân viên CSKH: Chỉ được xem khách hàng và đơn hàng
GRANT SELECT ON csdl_ban_hang.khach_hang TO 'role_nhan_vien_cskh';
GRANT SELECT, UPDATE(trang_thai) ON csdl_ban_hang.don_hang TO 'role_nhan_vien_cskh';

-- Developer: Được thao tác toàn bộ dữ liệu nhưng không được XÓA bảng
GRANT SELECT, INSERT, UPDATE, DELETE ON csdl_ban_hang.* TO 'role_nha_phat_trien';

-- Bước 3: Tạo User và Gán Role cho User
CREATE USER 'nguyen_van_a'@'%' IDENTIFIED BY 'MatKhauMoi123!';
GRANT 'role_nhan_vien_cskh' TO 'nguyen_van_a'@'%';

-- Bước 4: Kích hoạt Role cho User (Đặc thù trong MySQL / Oracle)
SET DEFAULT ROLE 'role_nhan_vien_cskh' TO 'nguyen_van_a'@'%';

```

---

## 4. Bảng tra cứu các Quyền (Privileges) thường dùng trong SQL

| Tên Quyền | Loại thao tác | Mục đích |
| --- | --- | --- |
| `SELECT` | DQL | Cho phép đọc/truy vấn dữ liệu. |
| `INSERT` | DML | Cho phép chèn thêm bản ghi mới. |
| `UPDATE` | DML | Cho phép chỉnh sửa bản ghi hiện có. |
| `DELETE` | DML | Cho phép xóa bản ghi. |
| `CREATE` | DDL | Cho phép tạo Bảng/Database mới. |
| `DROP` | DDL | Cho phép xóa Bảng/Database. |
| `ALTER` | DDL | Cho phép sửa đổi cấu trúc Bảng. |
| `EXECUTE` | Procedural | Cho phép chạy Stored Procedure / Function. |
| `ALL PRIVILEGES` | Tất cả | Cấp toàn bộ các quyền trên đối tượng. |

---

## 🛡️ 4 Nguyên tắc vàng về Bảo mật DCL cho Developer

1. **Nguyên tắc Quyền Tối Thối (Principle of Least Privilege):** Chỉ cấp đúng những quyền tối thiểu cần thiết để User/Ứng dụng hoàn thành công việc. Không dùng tài khoản `root` / `sa` cho ứng dụng chạy Production.
2. **Cẩn trọng với `WITH GRANT OPTION`:** Hạn chế tối đa việc cấp tùy chọn này vì User có quyền này có thể tự do phân quyền cho các tài khoản nguy hiểm khác.
3. **Luôn nhớ làm tươi bộ nhớ quyền (Trên MySQL):** Sau khi thực hiện các câu lệnh `GRANT`/`REVOKE` hoặc sửa bảng hệ thống `mysql.user`, hãy chạy lệnh:
```sql
FLUSH PRIVILEGES;

```


4. **Tách biệt tài khoản Truy vấn và tài khoản Migration:** Ứng dụng Backend chạy hàng ngày chỉ cần nhóm quyền DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), tài khoản chạy Migration khi Deploy mới cần quyền DDL (`CREATE`, `ALTER`, `DROP`).