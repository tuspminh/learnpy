Chào mừng bạn đến với **Bài 2 của Giai đoạn 2**!

Sau khi đã tạo được các bảng liên kết qua Khóa ngoại (`FOREIGN KEY`), hôm nay chúng ta sẽ học cách kết nối dữ liệu từ nhiều bảng lại với nhau thành một bảng kết quả duy nhất bằng phép **`JOIN`**.

---

### **Mục tiêu Bài 2**

1. Phân biệt khi nào dùng **`INNER JOIN`** và **`LEFT JOIN`**.
2. Viết truy vấn lấy dữ liệu từ 2 hoặc nhiều bảng.
3. Áp dụng Alias (bí danh) cho tên bảng để code gọn gàng, tránh xung đột tên cột.

---

### **1. Phân biệt `INNER JOIN` vs `LEFT JOIN**`

Giả sử chúng ta có 2 bảng: `KhachHang` và `DonHang`.

| Phép JOIN | Cách hoạt động | Trường hợp sử dụng |
| --- | --- | --- |
| **`INNER JOIN`** | Chỉ lấy những dòng mà **cả 2 bảng đều có dữ liệu khớp nhau** (phần giao). | Lấy danh sách các đơn hàng kèm thông tin khách mua (chỉ hiện những khách *đã từng mua hàng*). |
| **`LEFT JOIN`** | Lấy **toàn bộ dòng ở bảng bên trái**, nếu bảng bên phải không có dữ liệu tương ứng thì trả về `NULL`. | Lấy *tất cả* khách hàng trong hệ thống, xem ai đã mua gì (ai chưa mua hàng thì thông tin đơn sẽ hiện `NULL`). |

---

### **2. Thực hành Code Python: `INNER JOIN**`

Cú pháp chuẩn:

```sql
SELECT cot1, cot2, ...
FROM BangA
INNER JOIN BangB ON BangA.khoa_chinh = BangB.khoa_ngoai;

```

Nên dùng bí danh (Alias) cho bảng (ví dụ: `KhachHang kh`, `DonHang dh`) để viết ngắn gọn hơn:

```python
import sqlite3

conn = sqlite3.connect('cuahang_v2.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Truy vấn lấy Tên khách hàng, Ngày đặt, và Tổng tiền đơn hàng
sql_inner_join = """
SELECT 
    kh.id AS khach_id,
    kh.ho_ten,
    dh.id AS don_hang_id,
    dh.ngay_dat,
    dh.tong_tien
FROM KhachHang kh
INNER JOIN DonHang dh ON kh.id = dh.khach_hang_id;
"""

cursor.execute(sql_inner_join)
danh_sach_don = cursor.fetchall()

print("--- DANH SÁCH ĐƠN HÀNG (INNER JOIN) ---")
for row in danh_sach_don:
    print(f"Đơn #{row[2]} | Khách: {row[1]} | Ngày: {row[3]} | Tiền: {row[4]:,.0f} VNĐ")

```

---

### **3. Thực hành Code Python: `LEFT JOIN**`

Hãy xem sự khác biệt khi dùng `LEFT JOIN` để liệt kê **tất cả khách hàng**, bao gồm cả những người mới đăng ký chưa phát sinh đơn hàng nào:

```python
sql_left_join = """
SELECT 
    kh.ho_ten,
    kh.email,
    dh.id AS ma_don,
    dh.tong_tien
FROM KhachHang kh
LEFT JOIN DonHang dh ON kh.id = dh.khach_hang_id;
"""

cursor.execute(sql_left_join)
tat_ca_khach = cursor.fetchall()

print("\n--- TOÀN BỘ KHÁCH HÀNG (LEFT JOIN) ---")
for row in tat_ca_khach:
    ten = row[0]
    ma_don = row[2] if row[2] is not None else "Chưa có đơn"
    tong_tien = f"{row[3]:,.0f} VNĐ" if row[3] is not None else "0 VNĐ"
    
    print(f"Khách: {ten} | Mã đơn: {ma_don} | Giá trị: {tong_tien}")

```

---

### **4. Kết hợp `JOIN` với `WHERE` và `ORDER BY**`

Bạn hoàn toàn có thể lọc và sắp xếp dữ liệu sau khi đã `JOIN`:

```python
# Lấy các đơn hàng của khách có tên chứa chữ "Nam", sắp xếp theo tổng tiền giảm dần
sql_nang_cao = """
SELECT 
    kh.ho_ten,
    dh.id,
    dh.tong_tien
FROM KhachHang kh
INNER JOIN DonHang dh ON kh.id = dh.khach_hang_id
WHERE kh.ho_ten LIKE ?
ORDER BY dh.tong_tien DESC;
"""

cursor.execute(sql_nang_cao, ("%Nam%",))
print("\nCác đơn hàng của khách tên 'Nam':", cursor.fetchall())

conn.close()

```

---