Tính toán **Tổng tích lũy (Running Total)** và **Trung bình động (Moving Average)** là hai bài toán rất phổ biến trong phân tích chuỗi thời gian (Time-series analysis) và báo cáo tài chính.

Trước đây, nếu không có Window Functions, bạn phải dùng `JOIN` chính bảng đó hoặc Subquery rất phức tạp và chậm. Với Window Functions, mọi thứ được giải quyết gọn gàng thông qua mệnh đề **`OVER()`** và cú pháp khung dữ liệu **`ROWS BETWEEN ... AND ...`**.

---

## 🗂️ Dữ liệu mẫu dùng trong bài

Giả sử chúng ta có bảng **`doanh_thu_ngay`**:

| ngay | doanh_thu (VNĐ) |
| --- | --- |
| 2026-08-01 | 100,000 |
| 2026-08-02 | 150,000 |
| 2026-08-03 | 200,000 |
| 2026-08-04 | 120,000 |
| 2026-08-05 | 180,000 |

---

## 1. Tính Tổng Tích Lũy (Running Total)

**Ý nghĩa:** Tính tổng cộng dồn doanh thu từ ngày đầu tiên cho đến ngày hiện tại.

### Cú pháp & Lời giải:

```sql
SELECT 
    ngay,
    doanh_thu,
    SUM(doanh_thu) OVER (
        ORDER BY ngay ASC
    ) AS tong_tich_luy
FROM doanh_thu_ngay;

```

### Kết quả trả về:

| ngay | doanh_thu | tong_tich_luy | Cách tính |
| --- | --- | --- | --- |
| 2026-08-01 | 100,000 | **100,000** | 100,000 |
| 2026-08-02 | 150,000 | **250,000** | 100,000 + 150,000 |
| 2026-08-03 | 200,000 | **450,000** | 250,000 + 200,000 |
| 2026-08-04 | 120,000 | **570,000** | 450,000 + 120,000 |
| 2026-08-05 | 180,000 | **750,000** | 570,000 + 180,000 |

### 💡 Mở rộng: Tính Tổng tích lũy theo từng danh mục (`PARTITION BY`)

Nếu muốn tính tổng tích lũy **riêng cho từng cửa hàng**, bạn chỉ cần thêm `PARTITION BY cua_hang_id`:

```sql
SELECT 
    cua_hang_id,
    ngay,
    doanh_thu,
    SUM(doanh_thu) OVER (
        PARTITION BY cua_hang_id 
        ORDER BY ngay ASC
    ) AS tong_tich_luy_theo_cua_hang
FROM doanh_thu_ngay;

```

---

## 2. Tính Trung Bình Động (Moving Average)

**Ý nghĩa:** Giúp làm mượt sự biến động dữ liệu theo ngày. Ví dụ: **Trung bình động 3 ngày** tính trung bình doanh thu của **ngày hiện tại + 2 ngày liền trước đó**.

Để định hình chính xác "cửa sổ" (window) dữ liệu cần tính, ta bắt buộc phải dùng mệnh đề khung: **`ROWS BETWEEN ... AND ...`**.

### Cú pháp & Lời giải (Trung bình động 3 ngày):

```sql
SELECT 
    ngay,
    doanh_thu,
    AVG(doanh_thu) OVER (
        ORDER BY ngay ASC
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS tb_dong_3_ngay
FROM doanh_thu_ngay;

```

### Kết quả trả về:

| ngay | doanh_thu | tb_dong_3_ngay | Cách tính |
| --- | --- | --- | --- |
| 2026-08-01 | 100,000 | **100,000.00** | Chỉ có 1 ngày: `100,000 / 1` |
| 2026-08-02 | 150,000 | **125,000.00** | Có 2 ngày: `(100,000 + 150,000) / 2` |
| 2026-08-03 | 200,000 | **150,000.00** | Đủ 3 ngày: `(100,000 + 150,000 + 200,000) / 3` |
| 2026-08-04 | 120,000 | **156,666.67** | Đủ 3 ngày: `(150,000 + 200,000 + 120,000) / 3` |
| 2026-08-05 | 180,000 | **166,666.67** | Đủ 3 ngày: `(200,000 + 120,000 + 180,000) / 3` |

---

## 3. Bản đồ từ khóa cho Mệnh đề Khung (`Window Frame Clause`)

Cú pháp đầy đủ của việc định nghĩa cửa sổ tính toán là:
`ROWS BETWEEN <Start> AND <End>`

Các giá trị hay dùng cho `<Start>` và `<End>`:

* **`UNBOUNDED PRECEDING`**: Từ dòng đầu tiên của tập dữ liệu.
* **`N PRECEDING`**: `N` dòng trước dòng hiện tại.
* **`CURRENT ROW`**: Dòng hiện tại đang xét.
* **`N FOLLOWING`**: `N` dòng sau dòng hiện tại.
* **`UNBOUNDED FOLLOWING`**: Cho đến dòng cuối cùng của tập dữ liệu.

### 📌 Các mẫu khung tính toán phổ biến:

| Yêu cầu bài toán | Mệnh đề `ROWS BETWEEN` tương ứng |
| --- | --- |
| **Tổng tích lũy toàn bộ** (Từ đầu đến hiện tại) | `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` *(Mặc định khi có `ORDER BY`)* |
| **Trung bình động 7 ngày** (6 ngày trước + hôm nay) | `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` |
| **Trung bình 3 ngày trung tâm** (1 ngày trước + hôm nay + 1 ngày sau) | `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` |

---

## ⚡ Mẹo tối ưu hóa từ kinh nghiệm thực tế

1. **Phân biệt `ROWS` và `RANGE**`:
* `ROWS`: Đếm chính xác **số dòng**. Dù các dòng có ngày trùng nhau, nó vẫn tính đúng số dòng quy định.
* `RANGE`: Lọc theo **giá trị dữ liệu**. Nếu có 2 dòng trùng ngày, `RANGE` sẽ gộp chung giá trị của cả 2 dòng làm cho kết quả có thể không như mong đợi.
👉 *Lời khuyên:* Nên dùng **`ROWS`** để kết quả ổn định và truy vấn chạy nhanh hơn.


2. **Đảm bảo cột sắp xếp được đính kèm Index**:
* Khi dùng `ORDER BY ngay ASC` trong Window Function, hãy đảm bảo cột `ngay` đã được đánh **Index** để tránh việc Database Engine phải thực hiện thao tác Sort lại trên RAM/Disk.