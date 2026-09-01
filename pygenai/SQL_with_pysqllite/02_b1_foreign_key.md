Chào mừng bạn đến với **Giai đoạn 2: Thiết kế nhiều bảng, Khóa ngoại (FOREIGN KEY) & Truy vấn Nâng cao**.

Ở Giai đoạn 1, ta chỉ làm việc trên 1 bảng đơn lẻ. Nhưng trong thực tế, các hệ thống đều gồm nhiều bảng liên kết với nhau (ví dụ: `KhachHang` đặt `DonHang`, `DonHang` chứa nhiều `SanPham`).

---

### **Mục tiêu Giai đoạn 2**

1. Hiểu cách thiết kế quan hệ giữa các bảng: **1-N (Một - Nhiều)** và **N-N (Nhiều - Nhiều)**.
2. Thiết lập Khóa ngoại (**`FOREIGN KEY`**) và bật tính năng PRAGMA trong SQLite.
3. Liên kết dữ liệu bằng các phép `JOIN` (`INNER JOIN`, `LEFT JOIN`).
4. Gom nhóm & Báo cáo với `GROUP BY`, `HAVING` và các hàm tổng hợp (`SUM`, `COUNT`, `AVG`).

---

### **Bài 1: Khóa ngoại (FOREIGN KEY) & Thiết kế Bảng**

#### **1. Bật hỗ trợ Foreign Key trong SQLite**

Mặc định vì lý do tương thích ngược, **SQLite tắt tính năng kiểm tra ràng buộc Khóa ngoại**. Mỗi khi kết nối DB trong Python, việc đầu tiên bạn phải làm là bật nó lên bằng lệnh `PRAGMA`:

```python
import sqlite3

conn = sqlite3.connect('cuahang_v2.db')
cursor = conn.cursor()

# BẮT BUỘC: Bật ràng buộc khóa ngoại cho mỗi phiên kết nối
cursor.execute("PRAGMA foreign_keys = ON;")

```

---

#### **2. Thiết kế Quan hệ 1 - N (Một - Nhiều)**

Ví dụ: 1 Khách hàng (`KhachHang`) có thể tạo **nhiều** Đơn hàng (`DonHang`), nhưng 1 Đơn hàng chỉ thuộc về **một** Khách hàng.

* **Bảng chính (Parent):** `KhachHang` (chứa `id` là Primary Key)
* **Bảng phụ (Child):** `DonHang` (chứa `khach_hang_id` tham chiếu tới `KhachHang(id)`)

```python
# 1. Tạo bảng KhachHang
cursor.execute("""
CREATE TABLE IF NOT EXISTS KhachHang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);
""")

# 2. Tạo bảng DonHang có chứa FOREIGN KEY
cursor.execute("""
CREATE TABLE IF NOT EXISTS DonHang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ngay_dat TEXT NOT NULL,
    tong_tien REAL DEFAULT 0,
    khach_hang_id INTEGER,
    FOREIGN KEY (khach_hang_id) REFERENCES KhachHang(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

conn.commit()

```

> **Giải thích `ON DELETE CASCADE`:** Khi xóa 1 khách hàng trong bảng `KhachHang`, tất cả các đơn hàng liên quan của khách hàng đó trong bảng `DonHang` sẽ **tự động bị xóa theo**, giúp tránh dữ liệu rác (đơn hàng mồ côi không biết của ai).

---

#### **3. Thực hành kiểm tra Ràng buộc Khóa ngoại**

Hãy xem điều gì xảy ra nếu ta cố tình thêm một Đơn hàng cho một `khach_hang_id` **không tồn tại** (ví dụ: ID = 99):

```python
# Thêm 1 khách hàng hợp lệ (ID tự động = 1)
cursor.execute("INSERT INTO KhachHang (ho_ten, email) VALUES (?, ?)", ("Nguyễn Văn A", "a@gmail.com"))
conn.commit()

# Thêm đơn hàng cho Khách hàng ID = 1 (Thành công)
cursor.execute("INSERT INTO DonHang (ngay_dat, tong_tien, khach_hang_id) VALUES (?, ?, ?)", 
               ("2026-09-01", 500000.0, 1))
conn.commit()

# Cố tình thêm đơn hàng cho Khách hàng ID = 99 (Sẽ gây LỖI!)
try:
    cursor.execute("INSERT INTO DonHang (ngay_dat, tong_tien, khach_hang_id) VALUES (?, ?, ?)", 
                   ("2026-09-01", 200000.0, 99))
    conn.commit()
except sqlite3.IntegrityError as e:
    print(" Lỗi ràng buộc Khóa ngoại:", e)
    # Output: FOREIGN KEY constraint failed

```

---

### **Các bài tiếp theo trong Giai đoạn 2**

* **Bài 2:** Liên kết bảng với `INNER JOIN` và `LEFT JOIN` (Ghép tên khách hàng vào thông tin đơn hàng).
* **Bài 3:** Thiết kế Quan hệ Nhiều - Nhiều (N - N) bằng Bảng trung gian (Junction Table).
* **Bài 4:** Gom nhóm báo cáo dữ liệu với `GROUP BY`, `HAVING` và các hàm tổng hợp (`COUNT`, `SUM`, `AVG`).

---