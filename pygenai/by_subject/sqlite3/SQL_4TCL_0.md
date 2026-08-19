**TCL (Transaction Control Language)** là nhóm lệnh SQL dùng để quản lý các **giao dịch (Transactions)** trong cơ sở dữ liệu. Nhóm lệnh này giúp đảm bảo nguyên tắc **ACID** (đặc biệt là tính *Atomicity - Nguyên tố*: Tất cả cùng thành công hoặc tất cả cùng thất bại) khi bạn thực thi một chuỗi các lệnh DML (`INSERT`, `UPDATE`, `DELETE`).

---

## 1. Các lệnh TCL cốt lõi

| Lệnh | Cú pháp | Ý nghĩa |
| --- | --- | --- |
| **`BEGIN TRANSACTION`** | `BEGIN;` hoặc `START TRANSACTION;` | Mở một giao dịch thủ công, tạm dừng chế độ tự động lưu (Autocommit). |
| **`COMMIT`** | `COMMIT;` | Xác nhận lưu vĩnh viễn tất cả thay đổi trong giao dịch xuống đĩa cứng. |
| **`ROLLBACK`** | `ROLLBACK;` | Hủy bỏ toàn bộ thao tác trong giao dịch, hoàn tác CSDL về trạng thái ban đầu. |
| **`SAVEPOINT`** | `SAVEPOINT point_name;` | Tạo một cột mốc tạm thời trong giao dịch để có thể quay về khi cần. |
| **`ROLLBACK TO`** | `ROLLBACK TO point_name;` | Khôi phục dữ liệu về đúng thời điểm đã tạo `SAVEPOINT`. |
| **`RELEASE SAVEPOINT`** | `RELEASE SAVEPOINT point_name;` | Xóa bỏ một `SAVEPOINT` đã tạo. |

---

## 2. Kịch bản thực tế: Giao dịch chuyển tiền ngân hàng

Bài toán chuyển tiền từ **Tài khoản A** sang **Tài khoản B** yêu cầu bắt buộc cả 2 câu lệnh `UPDATE` phải thành công. Nếu câu lệnh thứ 2 gặp sự cố (mất điện, sập mạng, lỗi logic), câu lệnh 1 phải được khôi phục lại ngay lập tức.

```sql
-- 1. Bắt đầu giao dịch
BEGIN TRANSACTION;

-- Bước A: Trừ 5,000,000đ từ tài khoản A
UPDATE tai_khoan 
SET so_du = so_du - 5000000 
WHERE id = 'TK_A' AND so_du >= 5000000;

-- Bước B: Cộng 5,000,000đ vào tài khoản B
UPDATE tai_khoan 
SET so_du = so_du + 5000000 
WHERE id = 'TK_B';

-- Kiểm tra nếu cả 2 bước đều hợp lệ:
COMMIT;

-- Nếu có bất kỳ bước nào thất bại hoặc dữ liệu không hợp lệ:
-- ROLLBACK;

```

---

## 3. Kỹ thuật chia nhỏ Giao dịch với `SAVEPOINT`

`SAVEPOINT` cho phép bạn hủy một phần của giao dịch thay vì hủy bỏ toàn bộ quá trình xử lý phức tạp.

```sql
BEGIN TRANSACTION;

-- Thao tác 1: Chèn đơn hàng mới
INSERT INTO don_hang (id, khach_hang_id, tong_tien) VALUES (1001, 5, 2000000);

-- Tạo mốc lưu tạm 1
SAVEPOINT sp_don_hang_created;

-- Thao tác 2: Thêm chi tiết đơn hàng
INSERT INTO chi_tiet_don_hang (don_hang_id, san_pham_id, so_luong) VALUES (1001, 101, 2);

-- Tạo mốc lưu tạm 2
SAVEPOINT sp_chi_tiet_created;

-- Thao tác 3: Thử áp mã giảm giá (Nếu mã này không hợp lệ, ta chỉ muốn hủy bước này)
UPDATE don_hang SET tong_tien = tong_tien - 500000 WHERE id = 1001 AND ma_giam_gia = 'INVALID';

-- Phát hiện lỗi mã giảm giá -> Hủy thao tác áp mã, quay lại mốc 'sp_chi_tiet_created'
ROLLBACK TO sp_chi_tiet_created;

-- Xác nhận đơn hàng và chi tiết vẫn được lưu an toàn
COMMIT;

```

---

## 4. Quản lý TCL trong Python (`sqlite3`)

Thư viện `sqlite3` trong Python mặc định chạy ở chế độ **Implicit Transaction** (Giao dịch ngầm). Nó tự động thực thi `BEGIN` trước câu lệnh DML đầu tiên, bạn chỉ cần điều khiển việc `COMMIT` hoặc `ROLLBACK`.

### Code mô phỏng xử lý an toàn bằng Python:

```python
import sqlite3

conn = sqlite3.connect('ngan_hang.db')
cursor = conn.cursor()

try:
    # sqlite3 tự động bắt đầu Transaction tại đây
    cursor.execute("UPDATE tai_khoan SET so_du = so_du - 5000000 WHERE id = 'A'")
    cursor.execute("UPDATE tai_khoan SET so_du = so_du + 5000000 WHERE id = 'B'")
    
    # Nếu không có lỗi nào phát sinh -> Lưu vĩnh viễn
    conn.commit()
    print("✅ Chuyển tiền thành công!")

except Exception as e:
    # Nếu gặp bất kỳ lỗi nào -> Hủy bỏ toàn bộ thao tác
    conn.rollback()
    print(f"❌ Giao dịch thất bại, đã Rollback: {e}")

finally:
    conn.close()

```

---

## ⚡ Các nguyên tắc vàng khi làm việc với TCL

1. **Giữ Transaction ngắn nhất có thể:** Tránh để các tác vụ nặng (như gọi API bên ngoài, gửi email, đọc/ghi file) nằm bên trong khối `BEGIN...COMMIT`. Việc giữ giao dịch lâu sẽ gây khóa bảng/khóa dòng (**Locking**), làm ngẽn các truy vấn khác.
2. **Luôn đi kèm với khối `try...except` (hoặc `try...catch`):** Khi viết code ứng dụng, luôn đặt `conn.rollback()` ở phần xử lý ngoại lệ để bảo vệ dữ liệu.
3. **Lưu ý lệnh DDL tự động Commit:** Trên hầu hết hệ CSDL (như MySQL, Oracle), chạy các lệnh DDL (`CREATE`, `ALTER`, `DROP`) ở giữa một giao dịch sẽ **ngay lập tức ép thực hiện `COMMIT**` các lệnh DML trước đó và không thể `ROLLBACK` được nữa.