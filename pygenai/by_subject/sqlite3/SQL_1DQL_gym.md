Để luyện tập DQL hiệu quả, chúng ta sẽ làm việc trên một **Cơ sở dữ liệu Bán hàng** thực tế gồm 4 bảng dưới đây:

### 🗂️ Cấu trúc dữ liệu mẫu (Schema)

* **`khach_hang`** (`id`, `ten`, `thanh_pho`, `ngay_tham_gia`)
* **`san_pham`** (`id`, `ten_sp`, `danh_muc`, `gia`)
* **`don_hang`** (`id`, `khach_hang_id`, `ngay_dat`, `tong_tien`, `trang_thai`)
* **`chi_tiet_don_hang`** (`id`, `don_hang_id`, `san_pham_id`, `so_luong`, `gia_ban`)

---

## 🟢 Bài 1: Lọc & Sắp xếp dữ liệu (Cơ bản)

**🎯 Mục tiêu:** Củng cố kỹ năng dùng `WHERE`, `BETWEEN`, `LIKE` và `ORDER BY`.

**📝 Đề bài:** Tìm danh sách các sản phẩm thuộc danh mục **'Điện thoại'** có giá từ **5,000,000 đến 20,000,000 VNĐ**. Kết quả cần hiển thị `ten_sp`, `danh_muc`, `gia` và sắp xếp theo giá giảm dần.

**💡 Lời giải SQL:**

```sql
SELECT ten_sp, danh_muc, gia
FROM san_pham
WHERE danh_muc = 'Điện thoại'
  AND gia BETWEEN 5000000 AND 20000000
ORDER BY gia DESC;

```

**🔍 Giải thích:**

* `BETWEEN a AND b`: Kiểm tra giá trị nằm trong khoảng từ `a` đến `b` (bao gồm cả 2 mốc).
* `ORDER BY gia DESC`: Sắp xếp danh sách kết quả theo cột `gia` từ cao xuống thấp.

---

## 🟡 Bài 2: Gom nhóm & Hàm tổng hợp (Trung bình thấp)

**🎯 Mục tiêu:** Phân biệt và kết hợp `WHERE`, `GROUP BY` và `HAVING`.

**📝 Đề bài:** Thống kê tổng số tiền đã chi tiêu và số lượng đơn hàng của từng khách hàng đối với các đơn hàng có trạng thái **'Hoàn thành'**. Chỉ lấy những khách hàng có tổng chi tiêu **lớn hơn 15,000,000 VNĐ**.

**💡 Lời giải SQL:**

```sql
SELECT 
    khach_hang_id,
    COUNT(id) AS so_luong_don,
    SUM(tong_tien) AS tong_chi_tieu
FROM don_hang
WHERE trang_thai = 'Hoàn thành'
GROUP BY khach_hang_id
HAVING SUM(tong_tien) > 15000000
ORDER BY tong_chi_tieu DESC;

```

**🔍 Giải thích:**

* `WHERE trang_thai = 'Hoàn thành'`: Lọc bỏ các đơn bị hủy/đang xử lý **trước khi** tính toán.
* `GROUP BY khach_hang_id`: Gom tất cả các đơn hàng của cùng 1 khách hàng thành 1 nhóm.
* `HAVING SUM(tong_tien) > 15000000`: Lọc điều kiện **sau khi** đã tính tổng chi tiêu theo nhóm.

---

## 🟠 Bài 3: Kết nối nhiều bảng (Trung bình)

**🎯 Mục tiêu:** Thực hành kết nối dữ liệu từ 3-4 bảng qua `INNER JOIN`.

**📝 Đề bài:** Hiển thị thông tin bao gồm: `ten` (tên khách hàng), `ten_sp` (tên sản phẩm), `so_luong`, `gia_ban` của tất cả các sản phẩm đã được mua bởi những khách hàng sống ở thành phố **'Hà Nội'**.

**💡 Lời giải SQL:**

```sql
SELECT 
    kh.ten AS ten_khach_hang,
    sp.ten_sp,
    ct.so_luong,
    ct.gia_ban
FROM khach_hang kh
INNER JOIN don_hang dh ON kh.id = dh.khach_hang_id
INNER JOIN chi_tiet_don_hang ct ON dh.id = ct.don_hang_id
INNER JOIN san_pham sp ON ct.san_pham_id = sp.id
WHERE kh.thanh_pho = 'Hà Nội';

```

**🔍 Giải thích:**

* Dữ liệu bị phân tán ở 4 bảng, ta dùng `JOIN` lần lượt qua các khóa ngoại (`khach_hang_id`, `don_hang_id`, `san_pham_id`) để nối lại thành 1 bảng kết quả duy nhất.

---

## 🔴 Bài 4: Truy vấn con Correlated Subquery & CASE WHEN (Trung bình cao)

**🎯 Mục tiêu:** Sử dụng Subquery kết hợp điều kiện logic phức tạp.

**📝 Đề bài:** Tìm các sản phẩm có giá **cao hơn giá trung bình** của danh mục mà sản phẩm đó thuộc về. Hiển thị: `ten_sp`, `danh_muc`, `gia` và một cột `phan_loai` với quy tắc: nếu giá > 30tr thì ghi 'Cao cấp', ngược lại ghi 'Cận cao cấp'.

**💡 Lời giải SQL:**

```sql
SELECT 
    sp1.ten_sp,
    sp1.danh_muc,
    sp1.gia,
    CASE 
        WHEN sp1.gia > 30000000 THEN 'Cao cấp'
        ELSE 'Cận cao cấp'
    END AS phan_loai
FROM san_pham sp1
WHERE sp1.gia > (
    -- Subquery: Tính giá trung bình của chính danh mục đó
    SELECT AVG(sp2.gia)
    FROM san_pham sp2
    WHERE sp2.danh_muc = sp1.danh_muc
);

```

**🔍 Giải thích:**

* Subquery trong `WHERE` được thực thi với mỗi dòng của câu truy vấn chính: nó lấy giá trung bình của **riêng danh mục** mà dòng đó đang xét (`sp2.danh_muc = sp1.danh_muc`).
* `CASE WHEN`: Phân loại động giá trị trả về dựa trên điều kiện.

---

## 🟣 Bài 5: CTE & Window Functions (Nâng cao)

**🎯 Mục tiêu:** Giải quyết bài toán Top N theo nhóm (Phân hạng nâng cao).

**📝 Đề bài:** Với mỗi **thành phố**, hãy tìm ra **Top 1 khách hàng** có tổng chi tiêu nhiều nhất (chỉ tính đơn hàng 'Hoàn thành'). Hiển thị: `thanh_pho`, `ten_khach_hang`, `tong_chi_tieu`.

**💡 Lời giải SQL:**

```sql
WITH XepHangKhachHang AS (
    SELECT 
        kh.thanh_pho,
        kh.ten AS ten_khach_hang,
        SUM(dh.tong_tien) AS tong_chi_tieu,
        ROW_NUMBER() OVER(
            PARTITION BY kh.thanh_pho 
            ORDER BY SUM(dh.tong_tien) DESC
        ) AS xep_hang
    FROM khach_hang kh
    JOIN don_hang dh ON kh.id = dh.khach_hang_id
    WHERE dh.trang_thai = 'Hoàn thành'
    GROUP BY kh.thanh_pho, kh.id, kh.ten
)
SELECT 
    thanh_pho,
    ten_khach_hang,
    tong_chi_tieu
FROM XepHangKhachHang
WHERE xep_hang = 1;

```

**🔍 Giải thích:**

1. **CTE (`WITH XepHangKhachHang AS ...`)**: Tạo một bảng tạm lưu thông tin tổng chi tiêu của từng khách hàng.
2. **`ROW_NUMBER() OVER (...)`**:
* `PARTITION BY kh.thanh_pho`: Chia dữ liệu thành từng nhóm nhỏ theo từng thành phố.
* `ORDER BY SUM(...) DESC`: Đánh số thứ tự 1, 2, 3... cho các khách hàng trong cùng 1 thành phố theo tổng chi tiêu giảm dần.


3. **Lọc `WHERE xep_hang = 1**`: Lấy ra đúng người đứng đầu ở mỗi thành phố.