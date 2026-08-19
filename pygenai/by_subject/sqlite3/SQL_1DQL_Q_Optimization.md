Tối ưu hóa câu lệnh `SELECT` (**SQL Query Optimization**) là kỹ năng cốt lõi giúp ứng dụng xử lý dữ liệu lớn nhanh hơn, giảm tải CPU, RAM và Disk I/O cho máy chủ cơ sở dữ liệu.

Dưới đây là tổng hợp các kỹ thuật tối ưu hóa từ mức cơ bản đến nâng cao mà mọi lập trình viên cần nắm vững.

---

## 1. Viết điều kiện tìm kiếm chuẩn SARGable (Search Argument Able)

Một câu lệnh **SARGable** cho phép Database Engine tận dụng tối đa chỉ mục (**Index**). Bất kỳ phép biến đổi hoặc dùng hàm trên cột ở mệnh đề `WHERE` đều làm mất tác dụng của Index, khiến DB phải quét toàn bộ bảng (**Full Table Scan**).

### ❌ Tránh (Không SARGable):

```sql
-- Dùng hàm trên cột indexed 'ngay_tao' -> Vô hiệu hóa Index
SELECT * FROM don_hang WHERE YEAR(ngay_tao) = 2026;

-- Thực hiện toán toán trên cột indexed 'gia'
SELECT * FROM san_pham WHERE gia / 2 < 50000;

```

### ✅ Nên dùng (SARGable):

```sql
-- Chuyển hàm sang khoảng giá trị cố định
SELECT * FROM don_hang 
WHERE ngay_tao >= '2026-01-01' AND ngay_tao < '2027-01-01';

-- Chuyển toán tử sang vế phải
SELECT * FROM san_pham WHERE gia < 100000;

```

---

## 2. Kiểm soát phạm vi dữ liệu xuất ra

### 🚫 Tránh `SELECT *`

* **Vấn đề:** Tốn băng thông truyền tải qua mạng, ngốn bộ nhớ RAM, và loại bỏ cơ hội sử dụng **Covering Index** (Index chứa đủ tất cả các cột được yêu cầu mà không cần truy xuất lại đĩa cứng - Table Access).
* **Khắc phục:** Chỉ liệt kê đúng các cột cần dùng:
```sql
SELECT id, ten_san_pham, gia FROM san_pham;

```



### 🎯 Lọc dữ liệu trước khi gom nhóm (`WHERE` vs `HAVING`)

* Đẩy toàn bộ điều kiện lọc dòng thô vào `WHERE` thay vì để sang `HAVING`. Mệnh đề `WHERE` giảm bớt số bản ghi phải xử lý trước khi thực hiện phép gom nhóm `GROUP BY`.

---

## 3. Tối ưu hóa Tìm kiếm chuỗi & Phép toán Logic

### 🔍 Tìm kiếm `LIKE` đúng cách

* **Ký tự `%` ở đầu chuỗi (`LIKE '%abc'`)**: Vô hiệu hóa B-Tree Index vì DB không biết điểm bắt đầu để tìm kiếm.
* **Ký tự `%` ở cuối chuỗi (`LIKE 'abc%'`)**: Vẫn tận dụng được Index (**Index Range Scan**).

### 🔄 Thay thế `OR` bằng `UNION ALL` hoặc `IN`

Mệnh đề `OR` nối giữa 2 cột khác nhau thường khiến DB Engine từ bỏ Index trên cả 2 cột.

```sql
-- ❌ Tránh: Dễ bị Full Table Scan
SELECT * FROM nhan_vien WHERE ma_phong = 'IT' OR chuc_vu = 'Manager';

-- ✅ Tối ưu: Tận dụng Index trên cả 2 cột riêng biệt
SELECT * FROM nhan_vien WHERE ma_phong = 'IT'
UNION ALL
SELECT * FROM nhan_vien WHERE chuc_vu = 'Manager' AND ma_phong != 'IT';

```

---

## 4. Tối ưu Subquery & Phép Nối (JOIN)

### ⚡ Dùng `EXISTS` thay cho `IN` với Subquery

* `IN` có thể tải toàn bộ tập kết quả của Subquery vào bộ nhớ trước khi so sánh.
* `EXISTS` cơ chế dừng ngay lập tức (**Short-circuiting**) khi tìm thấy bản ghi đầu tiên thỏa mãn.

```sql
-- ❌ Chậm hơn trên tập dữ liệu lớn
SELECT * FROM khach_hang 
WHERE id IN (SELECT khach_hang_id FROM don_hang);

-- ✅ Nhanh hơn
SELECT kh.* FROM khach_hang kh
WHERE EXISTS (
    SELECT 1 FROM don_hang dh WHERE dh.khach_hang_id = kh.id
);

```

### 🔗 Đánh Index trên các cột `JOIN`

* Luôn đảm bảo tất cả các cột làm khóa ngoại hoặc dùng trong mệnh đề `ON` (`JOIN tableB ON tableA.fk_id = tableB.id`) đều đã được đánh Index.

---

## 5. Tối ưu Phân trang lớn (Pagination Optimization)

Khi dùng `LIMIT 20 OFFSET 100000`, DB bắt buộc phải đọc và bỏ qua 100,000 dòng đầu tiên trước khi lấy 20 dòng tiếp theo -> Cực kỳ chậm.

### Kỹ thuật Keyset / Seek Pagination (Khuyên dùng):

Dựa vào ID hoặc Timestamp của bản ghi cuối cùng ở trang trước:

```sql
-- ❌ Càng trang sau càng chậm
SELECT * FROM bai_viet ORDER BY id DESC LIMIT 20 OFFSET 100000;

-- ✅ Tốc độ tức thì (O(1)) không phụ thuộc vị trí trang
SELECT * FROM bai_viet 
WHERE id < 100000  -- id cuối cùng thu được ở trang trước
ORDER BY id DESC 
LIMIT 20;

```

---

## 6. Sử dụng `EXPLAIN` để đọc Kế hoạch thực thi (Execution Plan)

Trước khi quyết định tối ưu, hãy chạy lệnh **`EXPLAIN`** (hoặc `EXPLAIN ANALYZE`) trước câu lệnh `SELECT` để biết DB Engine đang xử lý như thế nào.

```sql
EXPLAIN SELECT * FROM san_pham WHERE danh_muc_id = 5;

```

| Chỉ số cần chú ý | Giá trị Tốt (Tối ưu) | Giá trị Xấu (Cần sửa) |
| --- | --- | --- |
| **`type` / Scan Type** | `const`, `eq_ref`, `ref`, `range` | `ALL` (Full Table Scan) |
| **`possible_keys`** | Liệt kê các Index khả thi | `NULL` |
| **`key`** | Tên Index thực sự được sử dụng | `NULL` |
| **`rows`** | Số dòng dự kiến cần quét (Càng nhỏ càng tốt) | Quét gần như toàn bộ tổng số dòng của bảng |
| **`Extra`** | `Using index` (Covering Index) | `Using filesort`, `Using temporary` |

---

## 📌 Checklist nhanh dành cho Lập trình viên

1. 🔲 Đã loại bỏ `SELECT *` chưa?
2. 🔲 Có cột nào ở `WHERE` đang bị bọc bởi hàm (`YEAR()`, `LOWER()`, `SUBSTRING()`) không?
3. 🔲 Cột dùng để `JOIN` và lọc ở `WHERE` đã được đánh Index chưa?
4. 🔲 Cụm tìm kiếm `LIKE` có bị dính `%` ở đầu không?
5. 🔲 Đã kiểm tra qua lệnh `EXPLAIN` xem có bị `Full Table Scan` hay `filesort` không?