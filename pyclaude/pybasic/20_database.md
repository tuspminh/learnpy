Vai trò này tôi đã lưu vào bộ nhớ từ trước và đang duy trì xuyên suốt toàn bộ hành trình của chúng ta — sẽ tiếp tục áp dụng đầy đủ như bạn yêu cầu. Vào bài 20.

### 📘 Bài 20: Cơ sở dữ liệu (SQLite, ORM cơ bản)

Đến giờ, mọi dữ liệu trong các bài học đều chỉ tồn tại **trong RAM** khi chương trình chạy — tắt chương trình là mất hết. Bài học này giải quyết vấn đề cốt lõi: **lưu trữ dữ liệu bền vững (persistent)**, tồn tại qua nhiều lần chạy chương trình, nhiều người dùng truy cập đồng thời — nền tảng của mọi ứng dụng thực tế từ e-commerce đến ngân hàng.

---

#### 1. Tại sao không dùng file JSON/CSV cho mọi thứ?

Ở Bài 11 (mà ta đã bỏ qua, nhưng khái niệm này cần biết), bạn có thể lưu dữ liệu vào file JSON/CSV. Vậy tại sao cần cơ sở dữ liệu (database)?

python

```python
# Cách "ngây thơ" - đọc/ghi toàn bộ file JSON mỗi lần cần 1 thao tác nhỏ
import json

def them_don_hang(don_hang_moi):
    with open("don_hang.json", "r") as f:
        du_lieu = json.load(f)          # phải đọc TOÀN BỘ file vào RAM
    du_lieu.append(don_hang_moi)
    with open("don_hang.json", "w") as f:
        json.dump(du_lieu, f)            # phải ghi lại TOÀN BỘ file
```

**Vấn đề nghiêm trọng của cách này ở quy mô thực tế:**

- Nếu file có 1 triệu đơn hàng, mỗi lần thêm 1 đơn phải đọc/ghi lại toàn bộ 1 triệu bản ghi → **cực kỳ chậm**
- Nếu 2 người dùng ghi file **đồng thời** → dữ liệu bị ghi đè, mất mát (race condition)
- Không có cách nào **tìm kiếm nhanh** (ví dụ "tìm đơn hàng có giá > 1 triệu") mà không quét toàn bộ file
- Không đảm bảo được **tính nhất quán** dữ liệu (ví dụ chuyển tiền giữa 2 tài khoản phải "hoặc thành công cả hai, hoặc thất bại cả hai")

Cơ sở dữ liệu quan hệ (SQL database) giải quyết triệt để cả 4 vấn đề trên bằng cơ chế được tối ưu hàng chục năm qua.

---

#### 2. SQLite là gì và tại sao học nó đầu tiên?

**SQLite** là một cơ sở dữ liệu SQL **không cần server riêng** — toàn bộ database chỉ là **một file duy nhất** trên máy (`.db` hoặc `.sqlite3`). Python có sẵn module `sqlite3` (built-in, không cần `pip install`).

**Vì sao SQLite phù hợp để học đầu tiên (và vẫn dùng trong thực tế production ở quy mô nhỏ-vừa):**

- Không cần cài đặt server phức tạp (khác với PostgreSQL, MySQL cần server riêng)
- Đủ mạnh cho ứng dụng vừa và nhỏ — nhiều app di động, công cụ nội bộ dùng SQLite thẳng trong production
- Là bước đệm hoàn hảo để hiểu SQL trước khi chuyển sang PostgreSQL/MySQL cho hệ thống lớn hơn (khác biệt chủ yếu ở cách kết nối, cú pháp SQL gần như giống nhau)

---

#### 3. Kết nối và tạo bảng (Table)

python

```python
import sqlite3

# Kết nối tới file database - tự động TẠO MỚI nếu chưa tồn tại
ket_noi = sqlite3.connect("cua_hang.db")
cursor = ket_noi.cursor()    # cursor là "con trỏ" thực thi lệnh SQL

# Tạo bảng - SQL DDL (Data Definition Language)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS san_pham (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten TEXT NOT NULL,
        gia REAL NOT NULL,
        ton_kho INTEGER DEFAULT 0
    )
""")

ket_noi.commit()   # LƯU thay đổi vào file - BẮT BUỘC, nếu quên sẽ mất thay đổi
ket_noi.close()     # đóng kết nối khi xong việc
```

**Giải thích cú pháp SQL cốt lõi:**

- `PRIMARY KEY AUTOINCREMENT`: cột `id` tự tăng, là khóa định danh duy nhất cho mỗi dòng — tương tự index của list nhưng bền vững và không đổi
- `NOT NULL`: cột này **bắt buộc** phải có giá trị, không được để trống
- `DEFAULT 0`: giá trị mặc định nếu không truyền khi thêm dòng mới
- `IF NOT EXISTS`: tránh lỗi nếu bảng đã tồn tại từ lần chạy trước

**Các kiểu dữ liệu SQLite chính**: `INTEGER`, `REAL` (số thực), `TEXT` (chuỗi), `BLOB` (dữ liệu nhị phân như ảnh).

---

#### 4. Thêm dữ liệu (INSERT) — và lỗ hổng bảo mật nghiêm trọng cần tránh

python

```python
import sqlite3

ket_noi = sqlite3.connect("cua_hang.db")
cursor = ket_noi.cursor()

# ❌ CỰC KỲ NGUY HIỂM - SQL Injection - KHÔNG BAO GIỜ làm thế này
ten_sp_tu_input = "Laptop'; DROP TABLE san_pham; --"   # input độc hại
cursor.execute(f"INSERT INTO san_pham (ten, gia) VALUES ('{ten_sp_tu_input}', 100)")
# Câu lệnh trên có thể XÓA TOÀN BỘ BẢNG nếu người dùng nhập chuỗi có chủ đích phá hoại!
```

python

```python
# ✅ ĐÚNG - dùng placeholder "?" để tham số hóa câu lệnh (parameterized query)
cursor.execute(
    "INSERT INTO san_pham (ten, gia, ton_kho) VALUES (?, ?, ?)",
    ("Laptop Dell XPS", 28500000, 5)
)
ket_noi.commit()

# Thêm nhiều dòng cùng lúc - hiệu quả hơn gọi execute() nhiều lần
danh_sach_sp = [
    ("Chuột không dây", 350000, 42),
    ("Bàn phím cơ", 1250000, 15),
    ("Màn hình 27inch", 5900000, 8),
]
cursor.executemany(
    "INSERT INTO san_pham (ten, gia, ton_kho) VALUES (?, ?, ?)",
    danh_sach_sp
)
ket_noi.commit()
```

**Đây là nguyên tắc bảo mật SỐNG CÒN**: **SQL Injection** là một trong những lỗ hổng bảo mật nguy hiểm và phổ biến nhất trong lịch sử phần mềm — kẻ tấn công chèn mã SQL độc hại qua input (form đăng nhập, ô tìm kiếm...) để đọc/xóa/sửa dữ liệu trái phép. **Luôn luôn dùng placeholder `?`**, không bao giờ dùng f-string hay `+` để nối chuỗi SQL trực tiếp từ input người dùng — không có ngoại lệ, dù là ứng dụng nhỏ hay lớn.

---

#### 5. Truy vấn dữ liệu (SELECT)

python

```python
cursor.execute("SELECT * FROM san_pham")
tat_ca_sp = cursor.fetchall()    # trả về LIST các tuple, mỗi tuple là 1 dòng
print(tat_ca_sp)
# [(1, 'Laptop Dell XPS', 28500000.0, 5), (2, 'Chuột không dây', 350000.0, 42), ...]

cursor.execute("SELECT * FROM san_pham WHERE gia > ?", (1000000,))
sp_dat_tien = cursor.fetchall()

cursor.execute("SELECT * FROM san_pham WHERE id = ?", (1,))
mot_sp = cursor.fetchone()        # chỉ lấy 1 dòng, trả về None nếu không tìm thấy

# Sắp xếp và giới hạn kết quả
cursor.execute("SELECT ten, gia FROM san_pham ORDER BY gia DESC LIMIT 3")
top_3_dat_nhat = cursor.fetchall()
```

**Truy cập dữ liệu theo tên cột (thay vì phải nhớ vị trí index)** — kỹ thuật giúp code dễ đọc hơn nhiều:

python

```python
ket_noi.row_factory = sqlite3.Row    # thiết lập TRƯỚC khi tạo cursor
cursor = ket_noi.cursor()

cursor.execute("SELECT * FROM san_pham WHERE id = ?", (1,))
sp = cursor.fetchone()
print(sp["ten"])         # 'Laptop Dell XPS' - truy cập như dict, rõ nghĩa hơn sp[1]
print(sp["gia"])          # 28500000.0
print(dict(sp))            # {'id': 1, 'ten': 'Laptop Dell XPS', 'gia': 28500000.0, 'ton_kho': 5}
```

---

#### 6. Cập nhật (UPDATE) và Xóa (DELETE)

python

```python
# UPDATE - luôn nhớ mệnh đề WHERE, nếu không sẽ sửa TOÀN BỘ bảng!
cursor.execute(
    "UPDATE san_pham SET ton_kho = ton_kho - ? WHERE id = ?",
    (2, 1)   # giảm tồn kho 2 đơn vị cho sản phẩm id=1
)
ket_noi.commit()

# DELETE - tương tự, WHERE là bắt buộc để tránh xóa nhầm toàn bộ dữ liệu
cursor.execute("DELETE FROM san_pham WHERE ton_kho = 0")
ket_noi.commit()

print(f"Số dòng bị ảnh hưởng: {cursor.rowcount}")   # kiểm tra thao tác có thực sự áp dụng
```

**⚠️ Cảnh báo cực kỳ quan trọng**: quên `WHERE` trong `UPDATE`/`DELETE` là một trong những **lỗi thảm khốc nhất** trong lịch sử vận hành hệ thống thực tế — nó sẽ áp dụng thay đổi lên **MỌI dòng** trong bảng. Luôn kiểm tra kỹ mệnh đề `WHERE` trước khi chạy, đặc biệt trên dữ liệu production.

---

#### 7. `with` — Quản lý kết nối an toàn (kết nối lại kiến thức exception ở Bài 10)

python

```python
import sqlite3

def them_san_pham(ten, gia, ton_kho):
    """Dùng context manager để tự động commit/rollback và đóng kết nối."""
    with sqlite3.connect("cua_hang.db") as ket_noi:
        cursor = ket_noi.cursor()
        try:
            cursor.execute(
                "INSERT INTO san_pham (ten, gia, ton_kho) VALUES (?, ?, ?)",
                (ten, gia, ton_kho)
            )
            ket_noi.commit()
            return cursor.lastrowid   # trả về id của dòng vừa tạo
        except sqlite3.IntegrityError as e:
            print(f"Lỗi ràng buộc dữ liệu: {e}")
            ket_noi.rollback()   # hoàn tác nếu có lỗi - đảm bảo tính nhất quán
            return None
```

**`rollback()`** là khái niệm cực kỳ quan trọng: nếu một thao tác gồm nhiều bước (ví dụ trừ tiền tài khoản A, cộng tiền tài khoản B) mà giữa đường gặp lỗi, `rollback()` sẽ **hoàn tác toàn bộ**, đưa database về trạng thái trước khi thao tác bắt đầu — đảm bảo không bao giờ có tình huống "trừ tiền A nhưng chưa cộng được B" (mất tiền giữa đường). Đây gọi là tính chất **Atomicity** trong nguyên lý **ACID** của database (Atomicity, Consistency, Isolation, Durability) — kiến thức nền tảng khi làm việc với hệ thống tài chính thực tế.

---

#### 8. ORM — Object-Relational Mapping (giới thiệu khái niệm qua SQLAlchemy)

Viết SQL thô (raw SQL) như trên hoạt động tốt, nhưng ở quy mô lớn, dev thường dùng **ORM** — công cụ cho phép thao tác database bằng **Python object** thay vì viết câu lệnh SQL trực tiếp. **SQLAlchemy** là ORM phổ biến nhất trong hệ sinh thái Python 2026.

python

```python
# Cài: pip install sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class SanPham(Base):    # mỗi class = 1 bảng, mỗi instance = 1 dòng dữ liệu
    __tablename__ = "san_pham"
    id = Column(Integer, primary_key=True)
    ten = Column(String, nullable=False)
    gia = Column(Float, nullable=False)
    ton_kho = Column(Integer, default=0)

engine = create_engine("sqlite:///cua_hang_orm.db")
Base.metadata.create_all(engine)     # tự động tạo bảng từ class - không cần viết CREATE TABLE

Session = sessionmaker(bind=engine)
session = Session()

# Thêm dữ liệu - viết Python thuần, không cần SQL
sp_moi = SanPham(ten="Tai nghe Bluetooth", gia=890000, ton_kho=20)
session.add(sp_moi)
session.commit()

# Truy vấn - cú pháp Python, ORM tự chuyển thành SQL phía sau
sp_dat_tien = session.query(SanPham).filter(SanPham.gia > 500000).all()
for sp in sp_dat_tien:
    print(f"{sp.ten}: {sp.gia:,} VNĐ")     # truy cập thuộc tính như object thường
```

**So sánh Raw SQL vs ORM:**

| Tiêu chí | Raw SQL (`sqlite3`) | ORM (SQLAlchemy) |
| --- | --- | --- |
| Kiểm soát chi tiết | Cao — viết đúng câu lệnh muốn | Trung bình — phụ thuộc ORM sinh SQL |
| Tốc độ học | Nhanh — chỉ cần biết SQL cơ bản | Chậm hơn — cần học thêm API của ORM |
| Chuyển đổi database khác | Phải sửa lại SQL | Gần như tự động (đổi `connection string`) |
| Phù hợp với | Project nhỏ, script, học SQL nền tảng | Project lớn, team nhiều người, framework như Django/FastAPI |

**Lời khuyên thực chiến**: hiểu SQL thô trước (như phần 1-7 của bài này) là **bắt buộc**, vì ORM về bản chất vẫn sinh ra SQL phía sau — không hiểu SQL thì rất khó debug khi ORM "làm gì đó lạ" hoặc tối ưu hiệu năng truy vấn chậm. Sau khi vững SQL, học ORM sẽ nhanh và hiệu quả hơn nhiều.

---

#### 9. Ví dụ thực chiến tổng hợp — Hệ thống quản lý tồn kho hoàn chỉnh

python

```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "kho_hang.db"

@contextmanager
def ket_noi_db():
    """Context manager tùy chỉnh - đảm bảo kết nối luôn được đóng đúng cách."""
    ket_noi = sqlite3.connect(DB_PATH)
    ket_noi.row_factory = sqlite3.Row
    try:
        yield ket_noi
    finally:
        ket_noi.close()


def khoi_tao_db():
    with ket_noi_db() as ket_noi:
        ket_noi.execute("""
            CREATE TABLE IF NOT EXISTS san_pham (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten TEXT NOT NULL,
                gia REAL NOT NULL,
                ton_kho INTEGER DEFAULT 0
            )
        """)
        ket_noi.commit()


def them_san_pham(ten: str, gia: float, ton_kho: int) -> int:
    with ket_noi_db() as ket_noi:
        cursor = ket_noi.execute(
            "INSERT INTO san_pham (ten, gia, ton_kho) VALUES (?, ?, ?)",
            (ten, gia, ton_kho)
        )
        ket_noi.commit()
        return cursor.lastrowid


def xuat_kho(sp_id: int, so_luong: int) -> bool:
    """Xuất kho, đảm bảo không xuất quá số lượng tồn (áp dụng nguyên tắc Atomicity)."""
    with ket_noi_db() as ket_noi:
        sp = ket_noi.execute("SELECT ton_kho FROM san_pham WHERE id = ?", (sp_id,)).fetchone()
        if sp is None or sp["ton_kho"] < so_luong:
            return False
        ket_noi.execute(
            "UPDATE san_pham SET ton_kho = ton_kho - ? WHERE id = ?",
            (so_luong, sp_id)
        )
        ket_noi.commit()
        return True


def bao_cao_ton_kho() -> list[dict]:
    with ket_noi_db() as ket_noi:
        rows = ket_noi.execute("SELECT * FROM san_pham ORDER BY ton_kho ASC").fetchall()
        return [dict(row) for row in rows]


# Sử dụng
khoi_tao_db()
id_moi = them_san_pham("Ổ cứng SSD 1TB", 1850000, 30)
print(f"Đã thêm sản phẩm với id={id_moi}")

thanh_cong = xuat_kho(id_moi, 5)
print(f"Xuất kho: {'Thành công' if thanh_cong else 'Thất bại - không đủ tồn kho'}")

for sp in bao_cao_ton_kho():
    print(f"{sp['ten']:<20} | Tồn: {sp['ton_kho']:>4} | Giá: {sp['gia']:>12,.0f} VNĐ")
```

Lưu ý cách dùng `@contextmanager` — kỹ thuật decorator (nhắc lại Bài 15 mà ta đã bỏ qua, nhưng đây là ví dụ thực tế của nó) để tạo context manager tùy chỉnh, đảm bảo kết nối database **luôn** được đóng dù có lỗi hay không — áp dụng triệt để nguyên tắc quản lý tài nguyên đã học từ `finally` ở Bài 10.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_20.py` xây dựng **hệ thống quản lý đơn hàng có 2 bảng liên kết**:

sql

```sql
-- Bảng khach_hang
CREATE TABLE khach_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- Bảng don_hang - LIÊN KẾT tới khach_hang qua khoa_ngoai (foreign key)
CREATE TABLE don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    khach_hang_id INTEGER NOT NULL,
    tong_tien REAL NOT NULL,
    trang_thai TEXT DEFAULT 'cho_xu_ly',
    FOREIGN KEY (khach_hang_id) REFERENCES khach_hang(id)
);
```

Yêu cầu:

1. Viết hàm `khoi_tao_db()` tạo cả 2 bảng trên (dùng placeholder `?`, không f-string)
2. Viết hàm `them_khach_hang(ten, email)` — xử lý riêng lỗi `sqlite3.IntegrityError` nếu email bị trùng (do có `UNIQUE`)
3. Viết hàm `tao_don_hang(khach_hang_id, tong_tien)` thêm đơn hàng mới
4. Viết hàm `lay_don_hang_theo_khach(khach_hang_id)` dùng **JOIN** để lấy thông tin đơn hàng kèm tên khách hàng:

sql

```sql
   SELECT don_hang.*, khach_hang.ten, khach_hang.email
   FROM don_hang
   JOIN khach_hang ON don_hang.khach_hang_id = khach_hang.id
   WHERE khach_hang.id = ?
```

5. Viết hàm `cap_nhat_trang_thai(don_hang_id, trang_thai_moi)` — nhớ mệnh đề `WHERE`!
6. Thử nghiệm: tạo 2 khách hàng, mỗi khách 2 đơn hàng, cập nhật trạng thái 1 đơn, in báo cáo đầy đủ
7. Thử thách thêm: cố ý thêm khách hàng với email đã tồn tại để quan sát `IntegrityError` được bắt đúng cách, không làm crash chương trình

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 21: Testing (unittest, pytest)** — kỹ năng viết code tự động kiểm tra tính đúng đắn của chương trình, thay vì chỉ kiểm tra bằng mắt qua `print()` như từ đầu đến giờ — đây là ranh giới rõ rệt nhất giữa "code cho vui" và "code chuyên nghiệp sẵn sàng đưa vào production".
