Để hình dung rõ nhất cách thiết kế CSDL bằng DDL, chúng ta sẽ cùng đi qua bài toán thực tế: **Xây dựng CSDL cho Hệ thống Quản lý Bán hàng Online**.

---

## 1. Phân tích Bài toán & Mối quan hệ giữa các Thực thể

Mô hình bán hàng của chúng ta gồm 5 thực thể chính:

1. **Danh mục (`danh_muc`)**: Phân loại sản phẩm (ví dụ: Điện thoại, Thời trang).
2. **Sản phẩm (`san_pham`)**: Các mặt hàng bán trên hệ thống.
3. **Khách hàng (`khach_hang`)**: Người mua hàng.
4. **Đơn hàng (`don_hang`)**: Thông tin đơn mua của khách.
5. **Chi tiết đơn hàng (`chi_tiet_don_hang`)**: Lưu danh sách sản phẩm nằm trong đơn hàng.

### 🔗 Mối quan hệ giữa các bảng:

* **Quan hệ $1 - N$ (Một - Nhiều):**
* Một **Danh mục** có *nhiều* **Sản phẩm** $\rightarrow$ Đặt khóa ngoại `danh_muc_id` ở bảng `san_pham`.
* Một **Khách hàng** có *nhiều* **Đơn hàng** $\rightarrow$ Đặt khóa ngoại `khach_hang_id` ở bảng `don_hang`.


* **Quan hệ $N - N$ (Nhiều - Nhiều):**
* Một **Đơn hàng** chứa *nhiều* **Sản phẩm**, và một **Sản phẩm** xuất hiện trong *nhiều* **Đơn hàng**.
* $\rightarrow$ Cần tách ra một **Bảng trung gian** là `chi_tiet_don_hang` chứa 2 khóa ngoại trỏ về 2 bảng gốc.



---

## 2. Mã DDL Khởi tạo CSDL Hoàn chỉnh

Dưới đây là kịch bản SQL DDL chuẩn hóa, bao gồm Khóa chính (`PRIMARY KEY`), Khóa ngoại (`FOREIGN KEY`), các Ràng buộc dữ liệu (`CHECK`, `UNIQUE`, `NOT NULL`) và hành vi của Khóa ngoại (`ON DELETE`).

```sql
-- 1. BẢNG DANH MỤC SẢN PHẨM
CREATE TABLE danh_muc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_danh_muc VARCHAR(100) NOT NULL UNIQUE
);

-- 2. BẢNG KHÁCH HÀNG
CREATE TABLE khach_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    so_dien_thoai VARCHAR(15),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. BẢNG SẢN PHẨM (Có khóa ngoại trỏ tới bảng danh_muc)
CREATE TABLE san_pham (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    danh_muc_id INT NOT NULL,
    ten_sp VARCHAR(150) NOT NULL,
    gia DECIMAL(12, 2) NOT NULL CHECK (gia >= 0),
    so_luong_kho INT NOT NULL DEFAULT 0 CHECK (so_luong_kho >= 0),
    
    -- Định nghĩa Khóa ngoại
    CONSTRAINT fk_sanpham_danhmuc 
        FOREIGN KEY (danh_muc_id) 
        REFERENCES danh_muc(id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

-- 4. BẢNG ĐƠN HÀNG (Có khóa ngoại trỏ tới bảng khach_hang)
CREATE TABLE don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    khach_hang_id INT NOT NULL,
    ngay_dat DATETIME DEFAULT CURRENT_TIMESTAMP,
    tong_tien DECIMAL(12, 2) DEFAULT 0 CHECK (tong_tien >= 0),
    trang_thai VARCHAR(20) DEFAULT 'Cho_xu_ly' 
        CHECK (trang_thai IN ('Cho_xu_ly', 'Da_thanh_toan', 'Huy')),
    
    -- Định nghĩa Khóa ngoại
    CONSTRAINT fk_donhang_khachhang 
        FOREIGN KEY (khach_hang_id) 
        REFERENCES khach_hang(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- 5. BẢNG CHI TIẾT ĐƠN HÀNG (Giải quyết quan hệ N-N giữa don_hang và san_pham)
CREATE TABLE chi_tiet_don_hang (
    don_hang_id INT NOT NULL,
    san_pham_id INT NOT NULL,
    so_luong INT NOT NULL CHECK (so_luong > 0),
    don_gia DECIMAL(12, 2) NOT NULL CHECK (don_gia >= 0),
    
    -- Khóa chính phức hợp (Composite Primary Key)
    PRIMARY KEY (don_hang_id, san_pham_id),
    
    -- Định nghĩa các Khóa ngoại
    CONSTRAINT fk_chitiet_donhang 
        FOREIGN KEY (don_hang_id) REFERENCES don_hang(id) ON DELETE CASCADE,
    CONSTRAINT fk_chitiet_sanpham 
        FOREIGN KEY (san_pham_id) REFERENCES san_pham(id) ON DELETE RESTRICT
);

```

---

## 3. Giải thích các Điểm kỹ thuật cốt lõi trong DDL

### 🔑 Khóa chính Phức hợp (Composite Primary Key)

Ở bảng `chi_tiet_don_hang`, ta khai báo `PRIMARY KEY (don_hang_id, san_pham_id)`. Sự kết hợp giữa 2 cột này đảm bảo một sản phẩm **không thể bị chèn 2 lần vào cùng 1 đơn hàng** (nếu mua thêm thì cập nhật cột `so_luong`).

### 🛡️ Hành vi của Khóa ngoại (`ON DELETE`)

* **`ON DELETE CASCADE`** (Dùng cho `don_hang` $\rightarrow$ `chi_tiet_don_hang`):
* Nếu một **Đơn hàng** bị xóa, toàn bộ các dòng **Chi tiết đơn hàng** thuộc về nó sẽ **tự động bị xóa theo**.


* **`ON DELETE RESTRICT`** (Dùng cho `danh_muc` $\rightarrow$ `san_pham`):
* **Ngăn không cho xóa** Danh mục nếu vẫn còn Sản phẩm thuộc danh mục đó trong CSDL. Điều này tránh việc dữ liệu sản phẩm bị "mồ côi" không thuộc về danh mục nào.



### 📐 Ràng buộc Logic (`CHECK` & `DEFAULT`)

* `CHECK (gia >= 0)`: Đảm bảo không ai có thể chèn giá sản phẩm âm vào CSDL.
* `DEFAULT CURRENT_TIMESTAMP`: Tự động điền ngày giờ hiện tại khi tạo bản ghi mới mà không cần truyền giá trị thủ công.

---

## 4. Chạy thử nghiệm kiểm tra Khóa ngoại

Bạn có thể chèn dữ liệu mẫu để thấy Ràng buộc toàn vẹn hoạt động:

```sql
-- 1. Chèn Danh mục & Khách hàng
INSERT INTO danh_muc (ten_danh_muc) VALUES ('Điện thoại');
INSERT INTO khach_hang (ho_ten, email) VALUES ('Nguyễn Văn A', 'a@gmail.com');

-- 2. Chèn Sản phẩm (Sử dụng danh_muc_id = 1)
INSERT INTO san_pham (danh_muc_id, ten_sp, gia, so_luong_kho) 
VALUES (1, 'iPhone 15', 20000000, 10);

-- ❌ LỖI KHÓA NGOẠI: Chèn sản phẩm với danh_muc_id = 999 (Chưa tồn tại)
-- System sẽ chặn lại: FOREIGN KEY constraint failed!
INSERT INTO san_pham (danh_muc_id, ten_sp, gia) 
VALUES (999, 'Máy tính bảng', 10000000);

```