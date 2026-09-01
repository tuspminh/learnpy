Dưới đây là phần hướng dẫn chi tiết bổ sung cho các câu lệnh SQL quản lý cấu trúc bảng (`ALTER TABLE`, `DROP TABLE`) và mở rộng các kỹ thuật với `UPDATE`, `DELETE`, `ALIAS (AS)`, `fetchmany()` để hoàn thiện trọn vẹn Giai đoạn 1.

---

### **1. Quản lý Cấu trúc Bảng (`ALTER TABLE` & `DROP TABLE`)**

Khi hệ thống phát triển, bạn sẽ cần thay đổi cấu trúc bảng mà không muốn xóa đi làm lại từ đầu.

* **`ALTER TABLE`**: Dùng để đổi tên bảng hoặc thêm cột mới vào bảng hiện có.
* **`DROP TABLE`**: Dùng để xóa bỏ hoàn toàn một bảng khỏi database.

```python
import sqlite3

conn = sqlite3.connect('thuvien.db')
cursor = conn.cursor()

# 1. Thêm một cột mới vào bảng hiện có (VD: thêm cột 'trang_thai' với giá trị mặc định là 'Co san')
cursor.execute("""
    ALTER TABLE Sach 
    ADD COLUMN trang_thai TEXT DEFAULT 'Co san'
""")

# 2. Đổi tên bảng (VD: đổi tên bảng 'Sach' thành 'DanhMucSach')
cursor.execute("ALTER TABLE Sach RENAME TO DanhMucSach")

# 3. Xóa hoàn toàn một bảng nếu không dùng nữa (Dùng IF EXISTS để tránh lỗi nếu bảng không tồn tại)
cursor.execute("DROP TABLE IF EXISTS BangTam")

conn.commit()
conn.close()

```

> **Lưu ý riêng của SQLite:** SQLite không hỗ trợ lệnh `ALTER TABLE ... DROP COLUMN` (xóa cột) trực tiếp ở các phiên bản cũ hoặc chỉ hỗ trợ giới hạn từ SQLite v3.35.0+.

---

### **2. Cập nhật & Xóa dữ liệu Nâng cao (`UPDATE` & `DELETE`)**

Bổ sung các kỹ thuật biến đổi dữ liệu dựa trên giá trị hiện tại hoặc xóa theo điều kiện phức tạp.

#### **Cập nhật dữ liệu dựa trên giá trị cũ (`UPDATE`)**

Bạn có thể tăng/giảm giá trị hoặc nối chuỗi trực tiếp trong câu lệnh `UPDATE`.

```python
# Tăng giá thuê của tất cả sách do "Nguyễn Nhật Ánh" viết thêm 10%
cursor.execute("""
    UPDATE DanhMucSach 
    SET gia_thue = gia_thue * 1.10 
    WHERE tac_gia = ?
""", ("Nguyễn Nhật Ánh",))

# Đổi trạng thái mượn sách dựa trên ID
cursor.execute("""
    UPDATE DanhMucSach 
    SET trang_thai = 'Da mươn' 
    WHERE id = ?
""", (2,))

conn.commit()

```

#### **Xóa toàn bộ hoặc theo điều kiện (`DELETE`)**

```python
# Xóa tất cả các cuốn sách có năm xuất bản trước năm 1950
cursor.execute("DELETE FROM DanhMucSach WHERE nam_xuat_ban < ?", (1950,))

# XÓA TOÀN BỘ DỮ LIỆU TRONG BẢNG (Giữ lại cấu trúc bảng, khác với DROP TABLE)
# cursor.execute("DELETE FROM DanhMucSach")

conn.commit()

```

---

### **3. Đặt bí danh cho Cột/Bảng (`AS` - Alias) & `fetchmany()**`

#### **Đổi tên hiển thị với `AS` (Alias)**

`AS` giúp kết quả trả về có tên cột dễ hiểu hơn hoặc hỗ trợ tính toán trực tiếp khi `SELECT`.

```python
# Tính tổng giá trị và đổi tên cột hiển thị
sql_alias = """
    SELECT 
        ten_sach AS TieuDe, 
        gia_thue AS GiaHienTai,
        gia_thue * 1.1 AS GiaNiemYet
    FROM DanhMucSach
"""
cursor.execute(sql_alias)

# Lấy dữ liệu dạng danh sách các tuple
for row in cursor.fetchall():
    print(f"Tiêu đề: {row[0]} | Giá hiện tại: {row[1]} | Giá niêm yết: {row[2]}")

```

#### **Trích xuất từng phần với `fetchmany(size)**`

Nếu bảng có 100.000 dòng, dùng `fetchall()` sẽ làm tràn RAM. `fetchmany(n)` giúp bạn lấy từng đợt `n` kết quả để xử lý an toàn.

```python
cursor.execute("SELECT * FROM DanhMucSach")

# Lấy 2 dòng đầu tiên
dot_1 = cursor.fetchmany(2)
print("Đợt 1:", dot_1)

# Lấy tiếp 2 dòng tiếp theo
dot_2 = cursor.fetchmany(2)
print("Đợt 2:", dot_2)

```

---