Lệnh **`UPSERT`** (kết hợp giữa **UP**date và IN**SERT**) giải quyết một bài toán rất phổ biến: *Thêm một hàng mới vào cơ sở dữ liệu, nhưng nếu dữ liệu đã tồn tại (bị trùng Khóa chính hoặc Khóa UNIQUE) thì tự động chuyển sang cập nhật dòng đó thay vì quăng lỗi.*

Trong SQLite (từ phiên bản 3.24.0 trở đi), tính năng này được thực hiện thông qua mệnh đề **`ON CONFLICT`**.

---

### **1. Cú pháp cơ bản của `ON CONFLICT**`

Cú pháp tổng quát:

```sql
INSERT INTO ten_bang (cot1, cot2, ...) 
VALUES (val1, val2, ...)
ON CONFLICT(cot_bi_trung) 
DO UPDATE SET cot1 = excluded.cot1, cot2 = excluded.cot2;

```

* **`ON CONFLICT(cot_bi_trung)`**: Chỉ định cột có ràng buộc `PRIMARY KEY` hoặc `UNIQUE` để kiểm tra xung đột.
* **`DO NOTHING`**: Nếu trùng thì bỏ qua, không làm gì cả (không báo lỗi).
* **`DO UPDATE SET ...`**: Nếu trùng thì thực hiện cập nhật.
* **`excluded`**: Từ khóa đại diện cho dữ liệu **mới** mà bạn vừa cố tình `INSERT` vào.

---

### **2. Hai trường hợp sử dụng `ON CONFLICT` thường gặp**

#### **Trường hợp A: `DO NOTHING` (Trùng thì bỏ qua)**

Ví dụ: Thêm khách hàng vào hệ thống theo `email`. Nếu `email` đã tồn tại thì giữ nguyên dữ liệu cũ, không báo lỗi ngắt chương trình.

```python
import sqlite3

conn = sqlite3.connect('thuvien.db')
cursor = conn.cursor()

# Giả sử ma_isbn là UNIQUE
sql_do_nothing = """
INSERT INTO DanhMucSach (ten_sach, tac_gia, gia_thue, ma_isbn)
VALUES (?, ?, ?, ?)
ON CONFLICT(ma_isbn) DO NOTHING;
"""

cursor.execute(sql_do_nothing, ("Đắc Nhân Tâm", "Dale Carnegie", 20000.0, "ISBN005"))
conn.commit()
print(f"Số dòng được thêm/thay đổi: {cursor.rowcount}") # Nếu trùng, rowcount sẽ = 0

```

---

#### **Trường hợp B: `DO UPDATE` (Trùng thì cập nhật - UPSERT thực sự)**

Ví dụ: Khi cào dữ liệu hoặc cập nhật kho hàng: Nếu sách đã có mã `ma_isbn` này rồi thì **cập nhật lại giá thuê** và **tăng số lượng tồn kho lên**, ngược lại thì thêm mới.

```python
sql_upsert = """
INSERT INTO DanhMucSach (ten_sach, tac_gia, gia_thue, ma_isbn)
VALUES (?, ?, ?, ?)
ON CONFLICT(ma_isbn) 
DO UPDATE SET 
    gia_thue = excluded.gia_thue,
    ten_sach = excluded.ten_sach;
"""

# ISBN005 đã có sẵn trong DB, câu lệnh này sẽ UPDATE lại gia_thue thành 25000.0
cursor.execute(sql_upsert, ("Đắc Nhân Tâm (Bìa Cứng)", "Dale Carnegie", 25000.0, "ISBN005"))
conn.commit()
print("Đã thực hiện UPSERT thành công!")
"""
Giải thích:
- excluded.gia_thue chính là số 25000.0
- excluded.ten_sach chính là "Đắc Nhân Tâm (Bìa Cứng)"
- SQLite lấy giá trị mới này ghi đè vào dòng có ma_isbn = 'ISBN005'
"""
"""

```

---

### **3. Cú pháp thay thế ngắn gọn: `INSERT OR REPLACE` / `INSERT OR IGNORE**`

Trước khi lệnh `ON CONFLICT` ra đời, SQLite hỗ trợ cú pháp ngắn hơn (tuy nhiên ít linh hoạt hơn):

* **`INSERT OR IGNORE INTO ...`**: Tương đương với `ON CONFLICT DO NOTHING`.
* **`INSERT OR REPLACE INTO ...`**: Nếu trùng, SQLite sẽ **XÓA (DELETE)** dòng cũ đi và **THÊM (INSERT)** dòng mới vào (Lưu ý: Cách này sẽ làm thay đổi `id` tự tăng nếu `id` là Primary Key).

```python
# Cú pháp ngắn gọn bỏ qua nếu trùng
cursor.execute("INSERT OR IGNORE INTO DanhMucSach (ten_sach, tac_gia, ma_isbn) VALUES (?, ?, ?)", 
               ("Mắt Biếc", "Nguyễn Nhật Ánh", "ISBN003"))

# Cú pháp ngắn gọn ghi đè nếu trùng
cursor.execute("INSERT OR REPLACE INTO DanhMucSach (ten_sach, tac_gia, gia_thue, ma_isbn) VALUES (?, ?, ?, ?)", 
               ("Mắt Biếc (Tái bản)", "Nguyễn Nhật Ánh", 18000.0, "ISBN003"))

```

> **Lời khuyên:** Nên ưu tiên dùng chuẩn **`ON CONFLICT ... DO UPDATE/NOTHING`** vì nó cho phép bạn kiểm soát chính xác cột nào cần sửa mà không làm mất các dữ liệu cũ khác trong cùng một dòng.

---