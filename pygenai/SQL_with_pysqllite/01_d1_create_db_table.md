Chào mừng bạn đến với **Ngày 1 của Giai đoạn 1**! Hồi này, chúng ta sẽ bắt đầu từ những nét bút đầu tiên: cách mở một kết nối kết nối cơ sở dữ liệu (Database), tạo bảng bằng các ràng buộc chuẩn và chuẩn bị sẵn sàng môi trường làm việc.

---

### **Mục tiêu Ngày 1**

1. Nắm rõ cách `sqlite3` kết nối và tạo file `.db`.
2. Hiểu 5 kiểu dữ liệu cốt lõi của SQLite.
3. Viết câu lệnh `CREATE TABLE` chuẩn chỉnh với các ràng buộc (Constraints) căn bản.

---

### **1. Các kiểu dữ liệu cốt lõi trong SQLite**

Không giống như các hệ quản trị CSDL lớn (MySQL, PostgreSQL) có hàng chục kiểu dữ liệu phức tạp, SQLite quy về 5 kiểu cơ bản:

| Kiểu dữ liệu | Mô tả | Ví dụ |
| --- | --- | --- |
| **`NULL`** | Giá trị rỗng hoặc không xác định | `None` trong Python |
| **`INTEGER`** | Số nguyên (1, 2, 4, 8 bytes tùy độ lớn) | `1`, `42`, `-100` |
| **`REAL`** | Số thực (dấu phẩy động 8-byte) | `3.14`, `10.5` |
| **`TEXT`** | Chuỗi văn bản (mã hóa UTF-8 hoặc UTF-16) | `'Nguyễn Văn A'` |
| **`BLOB`** | Dữ liệu nhị phân thô (ảnh, file ghi âm, file nén...) | File binary |

---

### **2. Các ràng buộc dữ liệu (Constraints)**

Khi tạo cột trong bảng, ta gắn thêm ràng buộc để đảm bảo dữ liệu nhập vào không bị sai lệch:

* **`PRIMARY KEY`**: Đánh dấu cột làm Khóa chính (định danh duy nhất cho mỗi dòng).
* **`AUTOINCREMENT`**: Chỉ dùng cho cột `INTEGER PRIMARY KEY` để số tự động tăng (1, 2, 3...) khi thêm dòng mới.
* **`NOT NULL`**: Bắt buộc cột này phải có dữ liệu, không được để trống.
* **`UNIQUE`**: Giá trị trong cột này không được trùng lặp (ví dụ: Email, Số điện thoại).
* **`DEFAULT`**: Giá trị mặc định nếu người dùng không nhập.

---

### **3. Thực hành Code Python: Khởi tạo & Tạo Bảng**

Chúng ta sẽ tạo một bài toán thực tế: **Quản lý Sản phẩm (Products)**.

Hãy tạo file `ngay_1.py` và gõ đoạn code dưới đây:

```python
import sqlite3

# Step 1: Kết nối tới file database. 
# Nếu file 'cuahang.db' chưa có, SQLite sẽ tự động tạo mới file này.
conn = sqlite3.connect('cuahang.db')

# Step 2: Tạo đối tượng cursor để gửi lệnh SQL
cursor = conn.cursor()

# Step 3: Đánh câu lệnh SQL tạo bảng 'SanPham'
sql_tao_bang = """
CREATE TABLE IF NOT EXISTS SanPham (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_san_pham TEXT NOT NULL,
    gia REAL NOT NULL,
    so_luong INTEGER DEFAULT 0,
    ma_sku TEXT UNIQUE
);
"""

# Step 4: Thực thi câu lệnh
cursor.execute(sql_tao_bang)

# Step 5: Lưu thay đổi vào database
conn.commit()

print("Đã khởi tạo Database và tạo bảng 'SanPham' thành công!")

# Step 6: Đóng kết nối khi hoàn thành
conn.close()

```

---

### **Bài tập thực hành nhỏ cho Ngày 1**

Bạn hãy tự viết thêm một đoạn code Python (hoặc sửa file `ngay_1.py` trên) để tạo thêm một bảng tên là `KhangHang` (Khách hàng) với các yêu cầu sau:

1. `id`: Số nguyên, Khóa chính, tự động tăng.
2. `ho_ten`: Chuỗi, bắt buộc phải nhập (`NOT NULL`).
3. `email`: Chuỗi, không được trùng nhau (`UNIQUE`).
4. `so_dien_thoai`: Chuỗi, được phép để trống.