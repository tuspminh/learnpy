**DQL (Data Query Language)** là nhánh quan trọng nhất trong SQL, chịu trách nhiệm **truy vấn và rút trích dữ liệu** từ cơ sở dữ liệu. Lệnh duy nhất và mạnh mẽ nhất của DQL chính là **`SELECT`**.

Dưới đây là hướng dẫn chi tiết toàn diện từ cú pháp, thứ tự thực thi đến các kỹ thuật nâng cao với DQL.

---

## 1. Cú pháp tổng quát & Thứ tự thực thi (SQL Execution Order)

Một sai lầm phổ biến của người mới học là nghĩ SQL chạy từ trên xuống dưới theo thứ tự viết code. **Thực tế, SQL Server/Engine thực thi truy vấn theo một thứ tự hoàn toàn khác!**

### Cú pháp viết lệnh (Syntax Order):

```sql
SELECT [DISTINCT] column1, column2, AGGREGATE_FUNCTION(column3)
FROM table_name
[JOIN other_table ON condition]
[WHERE condition]
[GROUP BY column_name]
[HAVING group_condition]
[ORDER BY column_name ASC|DESC]
[LIMIT count OFFSET skip];

```

### Thứ tự thực thi của Database Engine (Execution Order):

hiểu thứ tự này giúp bạn biết lý do tại sao **không thể dùng tên bí danh (Alias) từ `SELECT` trong mệnh đề `WHERE**`, nhưng lại dùng được trong `ORDER BY`.

```
1. FROM & JOIN     --> Tìm và kết nối các bảng lấy dữ liệu gốc
2. WHERE           --> Lọc các dòng dữ liệu chưa gom nhóm
3. GROUP BY        --> Gom nhóm các dòng theo giá trị cột
4. HAVING          --> Lọc các nhóm sau khi gom (dựa trên hàm tổng hợp)
5. SELECT          --> Chọn các cột cần xuất ra, tính toán toán tử/alias
6. DISTINCT        --> Loại bỏ các dòng trùng lặp hoàn toàn
7. ORDER BY        --> Sắp xếp kết quả hiển thị
8. LIMIT / OFFSET  --> Cắt số lượng dòng trả về (Phân trang)

```

---

## 2. Chi tiết từng mệnh đề trong DQL

### 🔹 `SELECT`, `AS` & `DISTINCT`

* **`SELECT`**: Chỉ định các cột muốn hiển thị.
* **`AS` (Alias)**: Đặt tên thay thế cho cột hoặc bảng để code ngắn gọn, dễ đọc.
* **`DISTINCT`**: Loại bỏ bản ghi trùng lặp.

```sql
-- Lấy danh sách các thành phố duy nhất mà khách hàng sinh sống, đổi tên cột hiển thị
SELECT DISTINCT thanh_pho AS "Thành Phố"
FROM khach_hang;

```

---

### 🔹 `FROM` & các loại `JOIN`

Dùng để xác định nguồn dữ liệu. Nếu cần lấy dữ liệu từ nhiều bảng có quan hệ với nhau, ta dùng `JOIN`.

| Loại JOIN | Chức năng |
| --- | --- |
| **`INNER JOIN`** | Lấy các dòng có điều kiện trùng khớp ở **cả 2 bảng**. |
| **`LEFT JOIN`** | Lấy **tất cả dòng bảng bên trái**, nếu bảng bên phải không khớp sẽ điền `NULL`. |
| **`RIGHT JOIN`** | Lấy **tất cả dòng bảng bên phải**, tương tự `LEFT JOIN`. |
| **`FULL JOIN`** | Lấy tất cả dữ liệu của cả 2 bảng, chỗ không khớp điền `NULL`. |

```sql
-- Lấy thông tin đơn hàng cùng tên khách hàng (INNER JOIN)
SELECT dh.ma_don_hang, kh.ho_ten, dh.ngay_dat
FROM don_hang AS dh
INNER JOIN khach_hang AS kh ON dh.khach_hang_id = kh.id;

```

---

### 🔹 `WHERE` - Lọc dữ liệu thô

Dùng để lọc các dòng thỏa mãn điều kiện **trước khi** gom nhóm.

* **Toán tử so sánh**: `=`, `!=` (hoặc `<>`), `>`, `<`, `>=`, `<=`
* **Toán tử logic**: `AND`, `OR`, `NOT`
* **Toán tử tập hợp/khoảng**:
* `IN (...)`: Kiểm tra nằm trong danh sách.
* `BETWEEN a AND b`: Kiểm tra nằm trong khoảng.
* `LIKE '%chuoi%'`: Tìm kiếm chuỗi tương đối (`%` đại diện chuỗi bất kỳ, `_` đại diện 1 ký tự).
* `IS NULL` / `IS NOT NULL`: Kiểm tra dữ liệu rỗng.



```sql
-- Lấy các sản phẩm giá từ 100 đến 500, thuộc danh mục 1 hoặc 3 và có tên chứa chữ 'Phone'
SELECT *
FROM san_pham
WHERE gia BETWEEN 100 AND 500
  AND danh_muc_id IN (1, 3)
  AND ten_san_pham LIKE '%Phone%'
  AND trang_thai IS NOT NULL;

```

---

### 🔹 `GROUP BY` & `HAVING` - Gom nhóm và Lọc nhóm

#### Sự khác biệt cốt lõi giữa `WHERE` và `HAVING`:

* `WHERE`: Lọc **dòng đơn lẻ** trước khi gom nhóm. **Không** dùng được với các hàm tổng hợp như `SUM()`, `AVG()`, `COUNT()`.
* `HAVING`: Lọc **cả nhóm** sau khi gom nhóm. **Luôn** đi kèm hàm tổng hợp.

```sql
-- Thống kê tổng doanh thu theo từng khách hàng, chỉ lấy khách hàng có tổng chi tiêu > 1,000$
SELECT khach_hang_id, SUM(tong_tien) AS tong_chi_tieu, COUNT(*) AS so_don_hang
FROM don_hang
WHERE trang_thai = 'Hoan_thanh'     -- Lọc đơn hàng đã hoàn thành trước
GROUP BY khach_hang_id             -- Gom nhóm theo từng khách hàng
HAVING SUM(tong_tien) > 1000       -- Lọc các nhóm có tổng chi tiêu > 1000
ORDER BY tong_chi_tieu DESC;

```

---

### 🔹 `ORDER BY` & `LIMIT` / `OFFSET`

* **`ORDER BY`**: Sắp xếp kết quả theo cột (`ASC`: Tăng dần - Mặc định, `DESC`: Giảm dần).
* **`LIMIT n OFFSET m`**: Lấy `n` bản ghi, bỏ qua `m` bản ghi đầu (Thường dùng cho tính năng **phân trang**).

```sql
-- Phân trang: Trang 2 (mỗi trang 10 sản phẩm -> Bỏ qua 10 dòng đầu, lấy 10 dòng tiếp theo)
SELECT id, ten_san_pham, gia
FROM san_pham
ORDER BY gia DESC, ten_san_pham ASC
LIMIT 10 OFFSET 10;

```

---

## 3. Các hàm tổng hợp (Aggregate Functions) thường dùng

Các hàm này nhận vào một tập hợp dữ liệu và trả về **một giá trị duy nhất**:

* `COUNT(column)` / `COUNT(*)`: Đếm số lượng dòng.
* `SUM(column)`: Tính tổng giá trị số.
* `AVG(column)`: Tính giá trị trung bình.
* `MAX(column)` / `MIN(column)`: Tìm giá trị lớn nhất / nhỏ nhất.

```sql
SELECT 
    COUNT(*) AS tong_so_nhan_vien,
    AVG(luong) AS luong_trung_binh,
    MAX(luong) AS luong_cao_nhat,
    MIN(luong) AS luong_thap_nhat
FROM nhan_vien;

```

---

## 4. Kỹ thuật DQL Nâng cao

### A. Truy vấn con (Subquery)

Một câu lệnh `SELECT` nằm bên trong một câu lệnh khác.

```sql
-- Lấy danh sách nhân viên có lương cao hơn lương trung bình của toàn công ty
SELECT ho_ten, luong
FROM nhan_vien
WHERE luong > (SELECT AVG(luong) FROM nhan_vien);

```

### B. Mệnh đề điều kiện `CASE WHEN`

Tương tự như cấu trúc `if...else` trong lập trình, dùng để biến đổi dữ liệu trực tiếp khi truy vấn.

```sql
SELECT ho_ten, diem_tb,
    CASE 
        WHEN diem_tb >= 8.5 THEN 'Xuất sắc'
        WHEN diem_tb >= 7.0 THEN 'Khá'
        WHEN diem_tb >= 5.0 THEN 'Trung bình'
        ELSE 'Yếu'
    END AS xep_loai
FROM sinh_vien;

```

### C. CTE (Common Table Expression) với `WITH`

Giúp viết subquery gọn gàng, chia nhỏ logic phức tạp thành các "bảng tạm" dễ đọc hơn.

```sql
WITH DoanhThuKhachHang AS (
    SELECT khach_hang_id, SUM(tong_tien) AS tong_chi_tieu
    FROM don_hang
    GROUP BY khach_hang_id
)
SELECT kh.ho_ten, dt.tong_chi_tieu
FROM DoanhThuKhachHang dt
JOIN khach_hang kh ON dt.khach_hang_id = kh.id
WHERE dt.tong_chi_tieu > 2000;

```

---

## 💡 Tóm tắt mẹo tối ưu DQL cho Developer

1. **Tránh `SELECT ***`: Chỉ SELECT đúng các cột cần thiết để tiết kiệm RAM, Network I/O và tận dụng được Index.
2. **Luôn nhớ thứ tự `WHERE` vs `HAVING**`: Lọc càng sớm càng tốt ở `WHERE` để giảm dữ liệu trước khi gom nhóm `GROUP BY`.
3. **Sử dụng Index**: Tạo Index trên các cột thường xuyên xuất hiện ở mệnh đề `WHERE`, `JOIN`, `ORDER BY` để tăng tốc truy vấn.
