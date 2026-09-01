Chào mừng bạn đến với **Bài 4 của Giai đoạn 2**!

Hôm nay chúng ta sẽ hoàn thành Giai đoạn 2 bằng các kỹ thuật **Gom nhóm dữ liệu & Báo cáo thống kê** — phần quan trọng nhất khi làm việc với cơ sở dữ liệu để rút ra các chỉ số kinh doanh (tổng doanh thu, trung bình đơn hàng, số lượng đơn của từng khách...).

---

### **Mục tiêu Bài 4**

1. Nắm vững các hàm tổng hợp: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`.
2. Gom nhóm dữ liệu theo từng đối tượng bằng `GROUP BY`.
3. Lọc dữ liệu *sau khi gom nhóm* bằng `HAVING` (phân biệt rõ với `WHERE`).

---

### **1. Các hàm tổng hợp (Aggregate Functions)**

Các hàm này nhận vào một tập hợp giá trị và trả về một kết quả duy nhất:

* `COUNT(cột)`: Đếm số lượng dòng (không tính `NULL`).
* `SUM(cột)`: Tính tổng giá trị các ô trong cột.
* `AVG(cột)`: Tính giá trị trung bình.
* `MIN(cột)` / `MAX(cột)`: Tìm giá trị nhỏ nhất / lớn nhất.

```python
import sqlite3

conn = sqlite3.connect('cuahang_v2.db')
cursor = conn.cursor()

# Thống kê tổng quan toàn bộ đơn hàng
cursor.execute("""
    SELECT 
        COUNT(id) AS tong_so_don,
        SUM(tong_tien) AS tong_doanh_thu,
        AVG(tong_tien) AS gia_tri_trung_binh,
        MAX(tong_tien) AS don_lon_nhat
    FROM DonHang
""")

stats = cursor.fetchone()
print(f"Tổng số đơn: {stats[0]}")
print(f"Tổng doanh thu: {stats[1]:,.0f} VNĐ")
print(f"Giá trị đơn trung bình: {stats[2]:,.0f} VNĐ")

```

---

### **2. Gom nhóm dữ liệu với `GROUP BY**`

Khi muốn tính toán các hàm tổng hợp **cho từng nhóm đối tượng** (ví dụ: Tổng tiền *của từng khách hàng*, Số sản phẩm *của từng đơn hàng*), bạn dùng `GROUP BY`.

> **Quy tắc vàng:** Tất cả các cột nằm trong `SELECT` (mà không nằm trong hàm tổng hợp) đều **bắt buộc** phải khai báo trong mệnh đề `GROUP BY`.

```python
# Thống kê tổng số đơn và tổng chi tiêu của TỪNG KHÁCH HÀNG
sql_group_by = """
SELECT 
    kh.id,
    kh.ho_ten,
    COUNT(dh.id) AS so_luong_don,
    COALESCE(SUM(dh.tong_tien), 0) AS tong_chi_tieu
FROM KhachHang kh
LEFT JOIN DonHang dh ON kh.id = dh.khach_hang_id
GROUP BY kh.id, kh.ho_ten
ORDER BY tong_chi_tieu DESC;
"""

cursor.execute(sql_group_by)
print("--- THỐNG KÊ CHI TIÊU THEO KHÁCH HÀNG ---")
for row in cursor.fetchall():
    print(f"Khách #{row[0]}: {row[1]} | Đã mua: {row[2]} đơn | Tổng chi: {row[3]:,.0f} VNĐ")

```

*(Lưu ý: Dùng `COALESCE(SUM(...), 0)` để nếu khách chưa mua gì, giá trị trả về là `0` thay vì `NULL`).*

---

### **3. Lọc nhóm với `HAVING` (Khác gì với `WHERE`?)**

Cả `WHERE` và `HAVING` đều dùng để lọc, nhưng vị trí và chức năng hoàn toàn khác nhau:

* **`WHERE`**: Lọc các dòng dữ liệu **trước** khi gom nhóm (không dùng được với các hàm `SUM`, `COUNT`...).
* **`HAVING`**: Lọc kết quả **sau** khi đã gom nhóm bằng `GROUP BY`.

```python
# Tìm những khách hàng VIP đã chi tiêu TỔNG CỘNG trên 1.000.000 VNĐ
sql_having = """
SELECT 
    kh.ho_ten,
    SUM(dh.tong_tien) AS tong_chi_tieu
FROM KhachHang kh
INNER JOIN DonHang dh ON kh.id = dh.khach_hang_id
WHERE dh.ngay_dat >= '2026-01-01'  -- Lọc ngày ĐẶT HÀNG trước (WHERE)
GROUP BY kh.id, kh.ho_ten
HAVING SUM(dh.tong_tien) >= 1000000; -- Lọc TỔNG TIỀN sau khi nhóm (HAVING)
"""

cursor.execute(sql_having)
print("\n--- DANH SÁCH KHÁCH HÀNG VIP ---")
for row in cursor.fetchall():
    print(f"VIP: {row[0]} - Tổng chi tiêu: {row[1]:,.0f} VNĐ")

conn.close()

```

---

### **Tổng kết Giai đoạn 2**

Bạn đã đi qua toàn bộ kiến thức thiết kế và truy vấn nâng cao:

* Ràng buộc Khóa ngoại (`FOREIGN KEY`) và `PRAGMA foreign_keys = ON;`.
* Các phép liên kết bảng (`INNER JOIN`, `LEFT JOIN`).
* Thiết kế Quan hệ Nhiều - Nhiều (N-N) qua Bảng trung gian.
* Gom nhóm & Báo cáo với `GROUP BY`, `HAVING` và các hàm tổng hợp.

---