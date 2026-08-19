Sử dụng **Context Manager (`with`)** là điểm phân biệt giữa một lập trình viên Python mới bắt đầu và một lập trình viên có kinh nghiệm. Nó giúp code gọn gàng, tự động hóa xử lý và ngăn ngừa rò rỉ bộ nhớ.

---

## 💡 Điểm mấu chốt bạn cần biết về SQLite3 trong Python

Có một **hiểu lầm rất phổ biến**: Nhiều người nghĩ `with sqlite3.connect(...) as conn:` sẽ tự động đóng connection.

Thực tế trong thư viện `sqlite3` mặc định của Python:

* `with conn:` quản lý **Transaction** (Giao dịch): Tự động `commit()` khi thành công và tự động `rollback()` khi có lỗi (Exception).
* `with conn:` **KHÔNG** tự động đóng (close) connection!

Dưới đây là 2 cách dùng chuẩn nhất từ cơ bản đến nâng cao.

---

## 1. Cách cơ bản: Quản lý Transaction tự động

Với cách này, bạn không cần gọi `conn.commit()` hay lo lắng về `conn.rollback()` khi có lỗi xảy ra.

```python
import sqlite3

conn = sqlite3.connect('quan_ly_hoc_sinh.db')

try:
    # 'with conn' sẽ tự động COMMIT nếu thành công, ROLLBACK nếu gặp lỗi
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sinh_vien (ten, tuoi, lop) VALUES (?, ?, ?)", ("Phạm Văn D", 22, "CNTT3"))
        
        # Cố tình tạo câu lệnh lỗi để test rollback (sai tên bảng)
        # cursor.execute("INSERT INTO bang_khong_ton_tai VALUES (1)")

    print("✅ Thao tác thành công, dữ liệu đã được commit!")

except sqlite3.Error as e:
    print(f"❌ Có lỗi xảy ra, toàn bộ giao dịch đã được ROLLBACK: {e}")

finally:
    # Cần tự đóng connection ở khối finally
    conn.close()

```

---

## 2. Cách cao cấp (Chuẩn Pythonic): Tự động COMMIT + Tự động CLOSE

Để vừa tự động **Commit/Rollback**, vừa tự động **Đóng connection** khi thoát khối lệnh mà không cần `try...finally`, ta kết hợp với `contextlib.closing`.

```python
import sqlite3
from contextlib import closing

# contextlib.closing giúp tự động gọi conn.close() khi thoát khối with ngoài
with closing(sqlite3.connect('quan_ly_hoc_sinh.db')) as conn:
    # with conn giúp tự động commit / rollback transaction
    with conn:
        with conn.cursor() as cursor:  # Tự động đóng cursor
            cursor.execute("SELECT * FROM sinh_vien")
            print("--- DANH SÁCH SINH VIÊN ---")
            for sv in cursor.fetchall():
                print(sv)

# Tới đây, cả connection và cursor đều đã được đóng an toàn!

```

---

## 3. Viết Helper Function tái sử dụng (Khuyên dùng cho dự án)

Bạn có thể tự đóng gói thành một hàm helper bằng `yield` để dùng cho toàn bộ dự án:

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_cursor(db_name='quan_ly_hoc_sinh.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        yield cursor  # Trả cursor cho nơi gọi sử dụng
        conn.commit() # Tự động commit nếu không lỗi
    except Exception as e:
        conn.rollback() # Tự động rollback nếu có lỗi
        raise e
    finally:
        cursor.close()
        conn.close()   # Tự động đóng kết nối

# --- CÁCH SỬ DỤNG CỰC KỲ NGẮN GỌN ---

# 1. Thêm dữ liệu
with get_db_cursor() as cur:
    cur.execute("INSERT INTO sinh_vien (ten, tuoi, lop) VALUES (?, ?, ?)", ("Lê Thị E", 19, "Kế Toán"))

# 2. Đọc dữ liệu
with get_db_cursor() as cur:
    cur.execute("SELECT * FROM sinh_vien")
    print(cur.fetchall())

```

---

## 📊 So sánh Trước & Sau khi dùng `with`

| Thao tác | Cách truyền thống (Không `with`) | Cách hiện đại (Dùng `with`) |
| --- | --- | --- |
| **Commit** | Phải gọi `conn.commit()` thủ công | **Tự động** khi ra khỏi khối `with` |
| **Bảo vệ dữ liệu** | Phải tự viết `try...except...conn.rollback()` | **Tự động Rollback** nếu gặp Exception |
| **Đóng kết nối** | Phải nhớ gọi `conn.close()` ở cuối | Tự động khi dùng `contextlib` hoặc Helper |
| **Độ an toàn** | Dễ rò rỉ tài nguyên / hỏng dữ liệu | An toàn tuyệt đối |