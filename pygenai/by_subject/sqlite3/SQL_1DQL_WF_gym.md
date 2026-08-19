Dưới đây là **3 bài tập DQL nâng cao** tập trung vào các **Window Functions** phổ biến nhất (`RANK`, `DENSE_RANK`, `LEAD`, `LAG`). Các bài tập này mô phỏng trực tiếp các bài toán phân tích dữ liệu (Data Analysis) trong doanh nghiệp.

---

### 🗂️ Dữ liệu giả định cho các bài tập

* **`doanh_thu_nhan_vien`** (`id`, `ten_nhan_vien`, `phong_ban`, `thang`, `nam`, `doanh_thu`)
* **`don_hang`** (`id`, `khach_hang_id`, `ngay_dat`, `tong_tien`)

---

## 🟢 Bài 1: Phân biệt `RANK()` và `DENSE_RANK()` (Xếp hạng có đồng hạng)

**🎯 Mục tiêu:** Hiểu sự khác biệt cốt lõi giữa `RANK()` và `DENSE_RANK()` khi xử lý các giá trị bằng nhau.

**📝 Đề bài:**
Xếp hạng doanh thu của từng nhân viên trong **tháng 8/2026** theo từng **phòng ban**. Hiển thị: `phong_ban`, `ten_nhan_vien`, `doanh_thu`, cùng 2 cột xếp hạng:

1. `xep_hang_rank`: Dùng hàm `RANK()`.
2. `xep_hang_dense`: Dùng hàm `DENSE_RANK()`.

Sắp xếp kết quả theo `phong_ban` và `doanh_thu` giảm dần.

**💡 Lời giải SQL:**

```sql
SELECT 
    phong_ban,
    ten_nhan_vien,
    doanh_thu,
    RANK() OVER (
        PARTITION BY phong_ban 
        ORDER BY doanh_thu DESC
    ) AS xep_hang_rank,
    DENSE_RANK() OVER (
        PARTITION BY phong_ban 
        ORDER BY doanh_thu DESC
    ) AS xep_hang_dense
FROM doanh_thu_nhan_vien
WHERE thang = 8 AND nam = 2026
ORDER BY phong_ban, doanh_thu DESC;

```

**🔍 Giải thích sự khác biệt:**
Giả sử phòng Kinh Doanh có 4 nhân viên với doanh thu lần lượt là: `100tr, 80tr, 80tr, 60tr`.

* **`RANK()`** sẽ xếp hạng: `1, 2, 2, 4` (bỏ qua hạng 3 do có 2 người đồng hạng 2).
* **`DENSE_RANK()`** sẽ xếp hạng: `1, 2, 2, 3` (không bỏ qua số thứ tự, hạng tiếp theo vẫn là 3).

---

## 🟡 Bài 2: Phân tích khoảng cách giữa các đơn hàng với `LAG()`

**🎯 Mục tiêu:** Lấy dữ liệu của dòng ngay phía trước trong cùng một tập dữ liệu đã sắp xếp.

**📝 Đề bài:**
Đối với mỗi khách hàng, hãy tính số ngày chênh lệch giữa **lần mua hàng hiện tại** và **lần mua hàng ngay trước đó**. Hiển thị: `khach_hang_id`, `ngay_dat` (lần này), `ngay_dat_truoc` (lần trước), và `so_ngay_cach_nhau`.

*(Lưu ý: Chỉ xét các khách hàng có từ 2 đơn hàng trở lên và câu lệnh tính chênh lệch ngày bên dưới dùng chuẩn SQLite `julianday()`; nếu dùng PostgreSQL bạn có thể trừ trực tiếp 2 ngày).*

**💡 Lời giải SQL:**

```sql
WITH LichSuMuaHang AS (
    SELECT 
        khach_hang_id,
        ngay_dat,
        LAG(ngay_dat, 1) OVER (
            PARTITION BY khach_hang_id 
            ORDER BY ngay_dat ASC
        ) AS ngay_dat_truoc
    FROM don_hang
)
SELECT 
    khach_hang_id,
    ngay_dat,
    ngay_dat_truoc,
    CAST(julianday(ngay_dat) - julianday(ngay_dat_truoc) AS INTEGER) AS so_ngay_cach_nhau
FROM LichSuMuaHang
WHERE ngay_dat_truoc IS NOT NULL
ORDER BY khach_hang_id, ngay_dat;

```

**🔍 Giải thích:**

* `LAG(ngay_dat, 1)`: Lấy giá trị của cột `ngay_dat` ở **1 dòng phía trước** (đã gom theo từng `khach_hang_id` và xếp tăng dần theo `ngay_dat`).
* Đối với đơn hàng đầu tiên của mỗi khách hàng, `ngay_dat_truoc` sẽ mang giá trị `NULL`.
* Mệnh đề `WHERE ngay_dat_truoc IS NOT NULL` giúp loại bỏ đơn hàng đầu tiên, chỉ giữ lại các lần mua từ lần thứ 2 trở đi.

---

## 🔴 Bài 3: Tính tỷ lệ Tăng trưởng Doanh thu theo tháng (MoM Growth Rate) với `LAG()` & `LEAD()`

**🎯 Mục tiêu:** Kết hợp CTE, Window Function và công thức toán học để tính toán chỉ số tăng trưởng chuỗi thời gian (Time-series Analysis).

**📝 Đề bài:**
Lập báo cáo doanh thu theo từng tháng trong năm 2026 của toàn công ty. Hiển thị các thông tin:

1. `thang`
2. `doanh_thu_hien_tai`: Tổng doanh thu của tháng đó.
3. `doanh_thu_thang_truoc`: Doanh thu của tháng liền trước (dùng `LAG`).
4. `doanh_thu_thang_sau`: Doanh thu dự kiến của tháng tiếp theo (dùng `LEAD`).
5. `phan_tram_tang_truong`: Tỷ lệ tăng/giảm doanh thu so với tháng trước (tính theo %).

Công thức tính Tăng trưởng MoM:


$$\text{Tăng trưởng \%} = \frac{\text{Doanh thu hiện tại} - \text{Doanh thu tháng trước}}{\text{Doanh thu tháng trước}} \times 100$$

**💡 Lời giải SQL:**

```sql
WITH DoanhThuTheoThang AS (
    -- Bước 1: Tính tổng doanh thu từng tháng
    SELECT 
        thang,
        SUM(doanh_thu) AS doanh_thu_hien_tai
    FROM doanh_thu_nhan_vien
    WHERE nam = 2026
    GROUP BY thang
),
DoanhThuChiTiet AS (
    -- Bước 2: Dùng LAG và LEAD để lấy doanh thu tháng trước & tháng sau
    SELECT 
        thang,
        doanh_thu_hien_tai,
        LAG(doanh_thu_hien_tai, 1) OVER (ORDER BY thang ASC) AS doanh_thu_thang_truoc,
        LEAD(doanh_thu_hien_tai, 1) OVER (ORDER BY thang ASC) AS doanh_thu_thang_sau
    FROM DoanhThuTheoThang
)
-- Bước 3: Tính phần trăm tăng trưởng
SELECT 
    thang,
    doanh_thu_hien_tai,
    doanh_thu_thang_truoc,
    doanh_thu_thang_sau,
    ROUND(
        (doanh_thu_hien_tai - doanh_thu_thang_truoc) * 100.0 / doanh_thu_thang_truoc, 
        2
    ) AS phan_tram_tang_truong
FROM DoanhThuChiTiet
ORDER BY thang ASC;

```

**🔍 Giải thích:**

* `LEAD(doanh_thu_hien_tai, 1)`: Lấy giá trị của **1 dòng phía sau** (tháng tương lai).
* Việc chia nhỏ query bằng 2 CTE (`DoanhThuTheoThang` -> `DoanhThuChiTiet`) giúp câu lệnh rõ ràng, tránh việc phải lặp lại các phép tính phức tạp trong mệnh đề `SELECT` cuối cùng.