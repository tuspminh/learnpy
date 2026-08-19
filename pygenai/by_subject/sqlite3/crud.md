Chào bạn! Rất vui được đồng hành cùng bạn trên hành trình học Python.

**SQLite3** là thư viện tuyệt vời vì nó được tích hợp sẵn trong Python (không cần `pip install`), lưu dữ liệu trực tiếp dưới dạng một file duy nhất `.db` gọn nhẹ, cực kỳ phù hợp cho ứng dụng nhỏ, prototype hoặc phần mềm desktop.

Dưới đây là hướng dẫn từng bước về **CRUD** (Create, Read, Update, Delete) chuẩn lập trình viên.

---

## 1. Quy trình cơ bản làm việc với SQLite3

Một luồng làm việc chuẩn gồm 4 bước:

1. Kết nối cơ sở dữ liệu (`sqlite3.connect`).
2. Tạo đối tượng điều khiển `cursor`.
3. Thực thi câu lệnh SQL (`cursor.execute`).
4. Lưu thay đổi (`conn.commit`) và đóng kết nối (`conn.close`).

> ⚠️ **Lưu ý quan trọng từ Developer:** Luôn sử dụng dấu hỏi `?` làm placeholder khi truyền dữ liệu vào câu lệnh SQL thay vì nối chuỗi. Cách này giúp phòng chống triệt để lỗ hổng bảo mật **SQL Injection**.

---

## 2. Chi tiết thao tác CRUD

### **C - Create (Thêm dữ liệu)**

Sử dụng câu lệnh `INSERT INTO`.

```python
import sqlite3

# 1. Kết nối (nếu file chưa tồn tại, Python sẽ tự tạo mới)
conn = sqlite3.connect('quan_ly_hoc_sinh.db')
cursor = conn.cursor()

# Tạo bảng mẫu
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sinh_vien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten TEXT NOT NULL,
        tuoi INTEGER,
        lop TEXT
    )
''')

# Thêm dữ liệu (Create)
def them_sinh_vien(ten, tuoi, lop):
    sql = "INSERT INTO sinh_vien (ten, tuoi, lop) VALUES (?, ?, ?)"
    cursor.execute(sql, (ten, tuoi, lop))
    conn.commit()  # Bắt buộc commit để lưu dữ liệu xuống disk
    print(f"✅ Đã thêm sinh viên: {ten}")

```

---

### **R - Read (Đọc dữ liệu)**

Sử dụng `SELECT`. Bạn dùng `fetchall()` để lấy tất cả bản ghi hoặc `fetchone()` để lấy 1 bản ghi đầu tiên.

```python
def xem_danh_sach():
    cursor.execute("SELECT * FROM sinh_vien")
    danh_sach = cursor.fetchall()
    
    print("\n--- DANH SÁCH SINH VIÊN ---")
    if not danh_sach:
        print("Chưa có dữ liệu.")
        return

    for sv in danh_sach:
        # sv là một tuple: (id, ten, tuoi, lop)
        print(f"ID: {sv[0]} | Tên: {sv[1]} | Tuổi: {sv[2]} | Lớp: {sv[3]}")

```

---

### **U - Update (Cập nhật dữ liệu)**

Sử dụng `UPDATE ... SET ... WHERE ...`.

```python
def cap_nhat_lop(sv_id, lop_moi):
    sql = "UPDATE sinh_vien SET lop = ? WHERE id = ?"
    cursor.execute(sql, (lop_moi, sv_id))
    conn.commit()
    print(f"🔄 Đã cập nhật lớp cho sinh viên ID {sv_id}")

```

---

### **D - Delete (Xóa dữ liệu)**

Sử dụng `DELETE FROM ... WHERE ...`.

```python
def xoa_sinh_vien(sv_id):
    # Lưu ý: Tham số thứ 2 là tuple nên nếu chỉ có 1 phần tử cần có dấu phẩy (sv_id,)
    sql = "DELETE FROM sinh_vien WHERE id = ?"
    cursor.execute(sql, (sv_id,))
    conn.commit()
    print(f"🗑️ Đã xóa sinh viên ID {sv_id}")

```

---

## 3. Code hoàn chỉnh chạy thử ngay

Bạn có thể copy đoạn code dưới đây vào file `crud_demo.py` và chạy trực tiếp:

```python
import sqlite3

# Kết nối CSDLV
conn = sqlite3.connect('quan_ly_hoc_sinh.db')
cursor = conn.cursor()

# 1. Khởi tạo bảng
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sinh_vien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten TEXT NOT NULL,
        tuoi INTEGER,
        lop TEXT
    )
''')
conn.commit()

# --- CHẠY THỬ CÁC THAO TÁC CRUD ---

# CREATE
cursor.execute("INSERT INTO sinh_vien (ten, tuoi, lop) VALUES (?, ?, ?)", ("Nguyễn Văn A", 20, "CNTT1"))
cursor.execute("INSERT INTO sinh_vien (ten, tuoi, lop) VALUES (?, ?, ?)", ("Trần Thị B", 21, "CNTT2"))
conn.commit()

# READ (Trước khi sửa/xóa)
print("--- LẦN 1: ĐỌC DỮ LIỆU BAN ĐẦU ---")
cursor.execute("SELECT * FROM sinh_vien")
for sv in cursor.fetchall():
    print(sv)

# UPDATE (Đổi lớp cho sinh viên ID = 1)
cursor.execute("UPDATE sinh_vien SET lop = ? WHERE id = ?", ("Kế Toán", 1))
conn.commit()

# DELETE (Xóa sinh viên ID = 2)
cursor.execute("DELETE FROM sinh_vien WHERE id = ?", (2,))
conn.commit()

# READ (Sau khi sửa/xóa)
print("\n--- LẦN 2: ĐỌC DỮ LIỆU SAU KHỦNG CẬP NHẬT VÀ XÓA ---")
cursor.execute("SELECT * FROM sinh_vien")
for sv in cursor.fetchall():
    print(sv)

# Đóng kết nối
conn.close()

```