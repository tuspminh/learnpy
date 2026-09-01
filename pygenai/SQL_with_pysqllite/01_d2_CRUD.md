Chào mừng bạn đến với **Ngày 2 của Giai đoạn 1**!

Hôm nay chúng ta sẽ học về **CRUD** — 4 thao tác cốt lõi trong bất kỳ hệ thống quản lý dữ liệu nào: **C**reate (Thêm), **R**ead (Đọc), **U**pdate (Sửa), và **D**elete (Xóa).

---

### **Mục tiêu Ngày 2**

1. Thêm dữ liệu an toàn bằng tham số hóa (`?`) để phòng chống lỗi bảo mật **SQL Injection**.
2. Đọc và lấy dữ liệu bằng các phương thức `fetchall()`, `fetchone()`.
3. Cập nhật và xóa dữ liệu có điều kiện (`WHERE`).

---

### **1. CREATE (Thêm dữ liệu với `INSERT INTO`)**

Khi làm việc với Python, **tuyệt đối không** dùng nối chuỗi (f-string) để tạo câu lệnh SQL vì rất dễ bị hack lỗ hổng SQL Injection. Hãy dùng dấu chấm hỏi `?` làm placeholder.

```python
import sqlite3

conn = sqlite3.connect('cuahang.db')
cursor = conn.cursor()

# 1. Thêm 1 sản phẩm (Truyền tuple vào execute)
sql_them_mot = "INSERT INTO SanPham (ten_san_pham, gia, so_luong, ma_sku) VALUES (?, ?, ?, ?)"
cursor.execute(sql_them_mot, ("Bàn phím Cơ", 1500000.0, 10, "KB01"))

# 2. Thêm NHIỀU sản phẩm cùng lúc (Dùng executemany với danh sách các tuple)
danh_sach_sp = [
    ("Chuột Không Dây", 450000.0, 25, "MS01"),
    ("Màn Hình 24 inch", 3200000.0, 5, "MON01"),
    ("Tai Nghe Bluetooth", 850000.0, 15, "HP01")
]
cursor.executemany(sql_them_mot, danh_sach_sp)

# LƯU Ý: Phải commit() thì dữ liệu mới thực sự được ghi vào file .db!
conn.commit()
print("Đã thêm dữ liệu thành công!")

```

---

### **2. READ (Đọc dữ liệu với `SELECT`)**

Để lấy dữ liệu ra khỏi cơ sở dữ liệu, ta thực thi lệnh `SELECT`, sau đó dùng các hàm trích xuất kết quả từ `cursor`:

* **`cursor.fetchall()`**: Lấy **tất cả** các dòng kết quả (trả về danh sách chứa các tuple).
* **`cursor.fetchone()`**: Chỉ lấy **1 dòng** duy nhất (trả về 1 tuple hoặc `None`).

```python
# Lấy toàn bộ sản phẩm
cursor.execute("SELECT id, ten_san_pham, gia, so_luong FROM SanPham")
tat_ca_sp = cursor.fetchall()

print("--- DANH SÁCH SẢN PHẨM ---")
for sp in tat_ca_sp:
    # sp là 1 tuple: (id, ten_san_pham, gia, so_luong)
    print(f"ID: {sp[0]} | Tên: {sp[1]} | Giá: {sp[2]:,.0f} VNĐ | Tồn kho: {sp[3]}")

# Lấy 1 sản phẩm cụ thể theo ID
cursor.execute("SELECT * FROM SanPham WHERE id = ?", (1,))
san_pham_dau = cursor.fetchone()
print("\nSản phẩm ID = 1:", san_pham_dau)

```

---

### **3. UPDATE (Cập nhật dữ liệu)**

Dùng lệnh `UPDATE` để sửa thông tin. **Luôn nhớ kèm theo mệnh đề `WHERE**`, nếu không bạn sẽ sửa sạch dữ liệu toàn bộ các hàng trong bảng!

```python
# Cập nhật giá và số lượng tồn kho của sản phẩm có mã SKU là 'KB01'
sql_cap_nhat = """
UPDATE SanPham 
SET gia = ?, so_luong = ? 
WHERE ma_sku = ?
"""
cursor.execute(sql_cap_nhat, (1350000.0, 12, "KB01"))
conn.commit()

print(f"Số dòng được cập nhật: {cursor.rowcount}")

```

---

### **4. DELETE (Xóa dữ liệu)**

Dùng lệnh `DELETE FROM` để xóa dữ liệu. Tương tự như `UPDATE`, luôn cần `WHERE` để chỉ định đúng hàng cần xóa.

```python
# Xóa sản phẩm có ID = 4
cursor.execute("DELETE FROM SanPham WHERE id = ?", (4,))
conn.commit()

print(f"Số dòng đã xóa: {cursor.rowcount}")

# Đóng kết nối sau khi làm xong
conn.close()

```

---

### **Tóm tắt luồng CRUD chuẩn trong Python**

```python
import sqlite3

with sqlite3.connect('cuahang.db') as conn:
    cursor = conn.cursor()
    # Thực hiện INSERT / UPDATE / DELETE tại đây
    # Khi dùng 'with', Python tự động commit() nếu không có lỗi!

```

---

### **Bài tập thực hành cho Ngày 2**

Hãy viết một script Python hoàn chỉnh làm các việc sau trên file `cuahang.db`:

1. Thêm 3 khách hàng vào bảng `KhachHang` (bảng bạn đã tạo ở bài tập Ngày 1).
2. Viết câu lệnh `SELECT` hiển thị danh sách tất cả khách hàng ra màn hình.
3. Cập nhật số điện thoại cho 1 khách hàng theo `email`.
4. Xóa 1 khách hàng theo `id`.