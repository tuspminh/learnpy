Chào bạn! Tôi là một lập trình viên Python. Rất vui được đồng hành cùng bạn học về `enum.Enum`.

Trong Python, **Enum** (viết tắt của *Enumeration* - kiểu dữ liệu liệt kê) được sử dụng để định nghĩa một tập hợp các hằng số có tên cố định. Dùng Enum giúp code của bạn rõ ràng, dễ đọc, tránh dùng các chuỗi (string) hoặc số (int) "ma thuật" (magic values) rải rác trong chương trình.

---

### 1. Khai báo và Sử dụng Cơ bản

Để dùng Enum, bạn import module `enum` có sẵn trong Python:

```python
from enum import Enum


class TrangThaiDonHang(Enum):
    CHO_XU_LY = 1
    DANG_GIAO = 2
    DA_GIAO = 3
    DA_HUY = 4


# Sử dụng Enum
trang_thai = TrangThaiDonHang.DANG_GIAO

# Lấy thông tin
print(trang_thai)  # TrangThaiDonHang.DANG_GIAO
print(trang_thai.name)  # 'DANG_GIAO' (Tên của hằng số)
print(trang_thai.value)  # 2            (Giá trị của hằng số)
```

---

### 2. Ưu điểm chính của Enum

* **So sánh an toàn:** So sánh trực tiếp bằng toán tử `is` hoặc `==`.
* **Tránh lỗi chính tả:** Nếu gõ sai tên (ví dụ `TrangThaiDonHang.DANG_GIAOO`), Python sẽ báo lỗi `AttributeError` ngay lập tức thay vì chạy sai logic ngầm như khi dùng string.
* **Duyệt qua các giá trị:** Có thể lặp qua tất cả thành viên trong Enum dễ dàng.

```python
# Lặp qua tất cả các giá trị
for tt in TrangThaiDonHang:
    print(f"{tt.name} -> {tt.value}")
```

---

### 3. Một số Kỹ thuật Nâng cao Rất Hay Dùng

#### Giá trị là Chuỗi (String Enums)

Giá trị không nhất thiết phải là số. Trong làm ứng dụng web hoặc API, giá trị Enum thường là string:

```python
class VaiTro(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

#### Tự động gán giá trị với `auto()`

Nếu bạn không quan tâm đến giá trị cụ thể mà chỉ cần các thành viên phân biệt với nhau, hãy dùng `auto()`:

```python
from enum import Enum, auto


class HuongDi(Enum):
    BAC = auto()  # Giá trị tự động là 1
    NAM = auto()  # Giá trị tự động là 2
    DONG = auto()  # Giá trị tự động là 3
    TAY = auto()  # Giá trị tự động là 4
```

#### Ép lỗi trùng lặp với decorator `@unique`

Mặc định, Enum cho phép nhiều tên có cùng một giá trị (alias). Nếu muốn đảm bảo mỗi giá trị là duy nhất, hãy thêm `@unique`:

```python
from enum import Enum, unique


@unique
class MaLoi(Enum):
    NOT_FOUND = 404
    SERVER_ERROR = 500
    # BAD_REQUEST = 404  # Sẽ báo ValueError ngay vì trùng giá trị 404
```

---

### 4. Truy xuất Enum từ Giá trị hoặc Tên

```python
# Lấy Enum từ giá trị (value)
tt = TrangThaiDonHang(2)
print(tt)  # TrangThaiDonHang.DANG_GIAO

# Lấy Enum từ tên (name)
tt_name = TrangThaiDonHang["DA_GIAO"]
print(tt_name)  # TrangThaiDonHang.DA_GIAO
```