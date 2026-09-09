Chào mừng bạn đến với **Ngày 3 của Giai đoạn 1**!

Hôm nay chúng ta sẽ kết thúc Giai đoạn 1 bằng việc làm chủ **Mệnh đề truy vấn & Lọc dữ liệu nâng cao**. Trong thực tế, bạn hiếm khi lấy toàn bộ bảng dữ liệu ra mà chỉ muốn lọc đúng những gì cần thiết (ví dụ: tìm sản phẩm có giá dưới 1 triệu, sắp xếp theo tên hoặc phân trang kết quả).

---

### **Mục tiêu Ngày 3**

1. Lọc dữ liệu bằng mệnh đề `WHERE` kết hợp với toán tử so sánh & toán tử logic.
2. Tìm kiếm chuỗi tương đối bằng toán tử `LIKE` và ký tự đại diện (`%`, `_`).
3. Sắp xếp kết quả với `ORDER BY` và giới hạn/phân trang bằng `LIMIT` & `OFFSET`.

---

### **1. Lọc nâng cao với `WHERE` & Toán tử Logic**

Bạn có thể kết hợp nhiều điều kiện lọc bằng các toán tử:

* `AND` (tất cả điều kiện phải đúng)
* `OR` (chỉ cần một điều kiện đúng)
* `BETWEEN v1 AND v2` (nằm trong khoảng từ `v1` đến `v2`)
* `IN (v1, v2, ...)` (nằm trong một danh sách cụ thể)

```python
import sqlite3

conn = sqlite3.connect('cuahang.db')
cursor = conn.cursor()

# 1. Tìm sản phẩm có giá từ 500.000 đến 2.000.000 VNĐ
sql_khoang_gia = "SELECT * FROM SanPham WHERE gia BETWEEN ? AND ?"
cursor.execute(sql_khoang_gia, (500000, 2000000))
print("Sản phẩm giá từ 500k - 2 triệu:", cursor.fetchall())

# 2. Tìm sản phẩm có mã SKU nằm trong danh sách
sql_danh_sach = "SELECT * FROM SanPham WHERE ma_sku IN ('KB01', 'MS01')"
cursor.execute(sql_danh_sach)
print("Sản phẩm thuộc nhóm SKU chọn lọc:", cursor.fetchall())

```

---

### **2. Tìm kiếm chuỗi linh hoạt với `LIKE**`

Toán tử `LIKE` thường dùng cho tính năng **ô tìm kiếm** trên website/ứng dụng. Nguồn sức mạnh của `LIKE` đến từ 2 ký tự đại diện:

* `%` : Đại diện cho 0, 1 hoặc nhiều ký tự bất kỳ.
* `_` : Đại diện cho **đúng 1** ký tự bất kỳ.

```python
# Tìm tất cả sản phẩm có tên chứa chữ "Bàn" (ví dụ: "Bàn phím", "Bàn ăn", "Cái Bàn")
tu_khoa = "%Bàn%"
sql_tim_kiem = "SELECT * FROM SanPham WHERE ten_san_pham LIKE ?"
cursor.execute(sql_tim_kiem, (tu_khoa,))

ds_tim_kiem = cursor.fetchall()
print("Kết quả tìm kiếm từ khóa 'Bàn':")
for sp in ds_tim_kiem:
    print(f"- {sp[1]} (Giá: {sp[2]:,.0f} VNĐ)")

```

---

### **3. Sắp xếp dữ liệu với `ORDER BY**`

Mặc định SQLite sẽ sắp xếp dữ liệu theo thứ tự chèn vào. Bạn có thể thay đổi bằng `ORDER BY`:

* `ASC` : Tăng dần (mặc định nếu không viết gì).
* `DESC` : Giảm dần.

```python
# Lấy danh sách sản phẩm, sắp xếp theo GIẢM DẦN của giá (đắt nhất lên đầu)
sql_sap_xep = "SELECT ten_san_pham, gia FROM SanPham ORDER BY gia DESC"
cursor.execute(sql_sap_xep)

print("\nDanh sách sản phẩm từ giá cao đến thấp:")
for ten, gia in cursor.fetchall():
    print(f"{ten}: {gia:,.0f} VNĐ")

```

---

### **4. Giới hạn & Phân trang với `LIMIT` và `OFFSET**`

Khi bảng có hàng nghìn dòng, bạn chỉ nên lấy một lượng nhỏ dữ liệu mỗi lần.

* `LIMIT n` : Chỉ lấy tối đa `n` dòng.
* `OFFSET k` : Bỏ qua `k` dòng đầu tiên rồi mới lấy.

> **Công thức phân trang (Page Size = `N`, Page Number = `P` bắt đầu từ 1):**
> `LIMIT N OFFSET (P - 1) * N`

```python
page_size = 2   # Mỗi trang hiển thị 2 sản phẩm
page_num = 1    # Đang xem trang 1

offset_val = (page_num - 1) * page_size

sql_phan_trang = """
SELECT id, ten_san_pham, gia 
FROM SanPham 
ORDER BY id ASC 
LIMIT ? OFFSET ?
"""

cursor.execute(sql_phan_trang, (page_size, offset_val))
print(f"\n--- Trang {page_num} ---")
for sp in cursor.fetchall():
    print(f"ID {sp[0]}: {sp[1]} - {sp[2]:,.0f} VNĐ")

conn.close()

```

---

### **Tổng kết Giai đoạn 1**

Chúc mừng bạn! Bạn đã nắm trọn vẹn nền tảng SQL với SQLite3 trong Python:

* Kết nối Database & Quản lý bảng (`CREATE TABLE`).
* Thao tác dữ liệu chuẩn CRUD (`INSERT`, `SELECT`, `UPDATE`, `DELETE`).
* Lọc dữ liệu (`WHERE`, `LIKE`), Sắp xếp (`ORDER BY`), Phân trang (`LIMIT / OFFSET`).

---