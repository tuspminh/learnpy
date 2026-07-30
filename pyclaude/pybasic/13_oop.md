Vai trò này tôi đã ghi nhớ từ đầu hành trình và đang duy trì nhất quán qua 12 bài học — tiếp tục áp dụng nghiêm túc. Giờ ta bước vào bài học đánh dấu **bước chuyển đổi tư duy lớn nhất** của toàn khóa học.

### 📘 Bài 13: Lập trình hướng đối tượng (OOP) — Nền tảng

Từ Bài 1 đến Bài 12, bạn viết code theo tư duy **thủ tục (procedural)**: dữ liệu (dict, list) và hành vi (hàm xử lý dữ liệu đó) tách biệt hoàn toàn với nhau. OOP thay đổi hoàn toàn cách tiếp cận: **gộp dữ liệu và hành vi liên quan đến nó vào một đơn vị duy nhất gọi là object**. Đây là nền tảng của hầu hết framework lớn bạn sẽ dùng: Django, FastAPI, PyTorch, pandas — tất cả đều xây dựng trên OOP.

---

#### 1. Vấn đề OOP giải quyết — nhìn từ code bạn đã viết

Nhớ lại Bài 8, bạn xử lý khách hàng dưới dạng dict:

python

```python
khach_hang_1 = {"ten": "An", "so_du": 5000000}
khach_hang_2 = {"ten": "Bình", "so_du": 200000}

def rut_tien(khach_hang, so_tien):
    if so_tien > khach_hang["so_du"]:
        print("Số dư không đủ")
    else:
        khach_hang["so_du"] -= so_tien
```

**Vấn đề**: dữ liệu (`khach_hang`) và hành vi (`rut_tien`) tồn tại **tách biệt**, không có gì ràng buộc chúng lại với nhau. Không gì ngăn cản ai đó viết `khach_hang["so_du"] = -999999999` trực tiếp, bỏ qua hoàn toàn logic kiểm tra. Khi hệ thống lớn dần với hàng chục hàm xử lý khách hàng nằm rải rác khắp codebase, việc quản lý tính đúng đắn dữ liệu trở nên cực kỳ khó khăn.

**OOP giải quyết bằng cách "đóng gói" (encapsulation)**: dữ liệu và hành vi liên quan sống chung trong một đơn vị gọi là **object**, được định nghĩa bởi một **class** (khuôn mẫu/bản thiết kế).

---

#### 2. Class và Object — khái niệm cốt lõi

**Class** là **khuôn mẫu (blueprint)**, **Object** (hay **instance**) là **một thực thể cụ thể** được tạo ra từ khuôn mẫu đó.

**Ẩn dụ dễ hiểu**: `class KhachHang` giống như bản vẽ thiết kế một căn nhà — nó định nghĩa "nhà có bao nhiêu phòng, cửa ở đâu", nhưng bản vẽ không phải là căn nhà thật. Mỗi khi bạn xây một căn nhà theo bản vẽ đó, bạn có một **object** — căn nhà cụ thể, có địa chỉ riêng, màu sơn riêng.

python

```python
class KhachHang:
    def __init__(self, ten, so_du):
        """__init__ là CONSTRUCTOR - tự động chạy khi tạo object mới"""
        self.ten = ten        # self.ten là THUỘC TÍNH (attribute) của object
        self.so_du = so_du

    def rut_tien(self, so_tien):
        """Đây là PHƯƠNG THỨC (method) - hành vi gắn liền với object"""
        if so_tien > self.so_du:
            print(f"{self.ten}: Số dư không đủ")
        else:
            self.so_du -= so_tien
            print(f"{self.ten}: Đã rút {so_tien:,} VNĐ, còn lại {self.so_du:,} VNĐ")


# Tạo OBJECT (instance) từ CLASS - gọi là "khởi tạo" (instantiate)
khach_1 = KhachHang("An", 5000000)
khach_2 = KhachHang("Bình", 200000)

khach_1.rut_tien(1000000)   # An: Đã rút 1,000,000 VNĐ, còn lại 4,000,000 VNĐ
khach_2.rut_tien(500000)     # Bình: Số dư không đủ
```

Nhận thấy sự khác biệt căn bản: giờ **dữ liệu** (`ten`, `so_du`) và **hành vi** (`rut_tien`) **sống chung** trong object `khach_1`, không tách biệt như dict + hàm rời rạc nữa.

---

#### 3. Giải phẫu `self` — điều gây khó hiểu nhất với người mới

python

```python
class KhachHang:
    def __init__(self, ten, so_du):
        self.ten = ten
        self.so_du = so_du
```

`self` là tham số **đại diện cho chính object đang được xử lý**. Khi bạn gọi `khach_1.rut_tien(1000000)`, Python **tự động** truyền `khach_1` vào làm `self` — bạn không cần (và không nên) truyền tay tham số này:

python

```python
# Những gì thực sự xảy ra "dưới lớp vỏ" khi bạn gọi:
khach_1.rut_tien(1000000)

# Về bản chất tương đương với (Python tự làm việc này cho bạn):
KhachHang.rut_tien(khach_1, 1000000)
```

`self.ten = ten` nghĩa là: *"gắn giá trị `ten` được truyền vào làm thuộc tính `ten` của object hiện tại"*. Đây là lý do mỗi object có `ten`, `so_du` **riêng biệt**, không lẫn với object khác — dù chúng đều được tạo từ cùng một class.

python

```python
print(khach_1.ten)     # 'An'
print(khach_2.ten)     # 'Bình'
print(khach_1.so_du)   # 4000000 (đã bị trừ sau rút tiền)
print(khach_2.so_du)   # 200000 (không đổi vì rút thất bại)
```

---

#### 4. Thuộc tính instance vs thuộc tính class

python

```python
class KhachHang:
    # Thuộc tính CLASS - CHIA SẺ giữa MỌI object, khai báo ngoài __init__
    LOAI_TIEN = "VNĐ"
    so_luong_khach_da_tao = 0   # dùng để đếm tổng số khách hàng đã tạo

    def __init__(self, ten, so_du):
        # Thuộc tính INSTANCE - RIÊNG BIỆT cho mỗi object
        self.ten = ten
        self.so_du = so_du
        KhachHang.so_luong_khach_da_tao += 1   # tăng biến class mỗi khi tạo object mới


khach_1 = KhachHang("An", 5000000)
khach_2 = KhachHang("Bình", 200000)

print(khach_1.LOAI_TIEN)                    # 'VNĐ' - dùng chung
print(KhachHang.so_luong_khach_da_tao)       # 2 - đếm được tổng số object đã tạo
```

**Ứng dụng thực tế phổ biến của thuộc tính class**: đếm số lượng instance đã tạo (như ví dụ trên), lưu cấu hình chung (ví dụ `TY_GIA_MAC_DINH` cho mọi đối tượng tiền tệ), hoặc định nghĩa hằng số liên quan đến class.

---

#### 5. Phương thức đặc biệt (Dunder methods / Magic methods)

Python có các phương thức đặc biệt bắt đầu và kết thúc bằng dấu gạch dưới đôi (`__ten__`), cho phép object của bạn tương tác với các hàm/ toán tử có sẵn của Python một cách tự nhiên:

python

```python
class DonHang:
    def __init__(self, ma_don, tong_tien):
        self.ma_don = ma_don
        self.tong_tien = tong_tien

    def __str__(self):
        """Định nghĩa cách object hiển thị khi dùng print() hoặc str()"""
        return f"Đơn hàng {self.ma_don}: {self.tong_tien:,} VNĐ"

    def __repr__(self):
        """Định nghĩa cách object hiển thị trong debug/console - nên chứa đủ info để tái tạo object"""
        return f"DonHang(ma_don='{self.ma_don}', tong_tien={self.tong_tien})"

    def __eq__(self, don_hang_khac):
        """Định nghĩa hành vi khi so sánh 2 object bằng =="""
        return self.ma_don == don_hang_khac.ma_don


don_1 = DonHang("DH001", 500000)
print(don_1)              # Đơn hàng DH001: 500,000 VNĐ (tự động gọi __str__)

don_2 = DonHang("DH001", 700000)
print(don_1 == don_2)     # True - vì __eq__ so sánh theo ma_don, không phải toàn bộ object
```

**Nếu không định nghĩa `__str__`**, `print(don_1)` sẽ in ra thứ khó hiểu như `<__main__.DonHang object at 0x7f8b1c0a4d90>` — địa chỉ bộ nhớ, không có ý nghĩa với người dùng. Đây là lý do **hầu như mọi class chuyên nghiệp đều định nghĩa `__str__`** để object hiển thị có ý nghĩa.

---

#### 6. Encapsulation — bảo vệ dữ liệu qua "quy ước" đặt tên

Python không có `private`/`public` như Java/C++ theo nghĩa chặt (bắt buộc bằng compiler), nhưng có **quy ước** rất được tôn trọng trong cộng đồng:

python

```python
class TaiKhoanNganHang:
    def __init__(self, so_du_ban_dau):
        self._so_du = so_du_ban_dau   # dấu gạch dưới đơn: "protected" - quy ước không dùng từ ngoài class

    def xem_so_du(self):
        return self._so_du

    def nap_tien(self, so_tien):
        if so_tien <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0")
        self._so_du += so_tien

    def rut_tien(self, so_tien):
        if so_tien > self._so_du:
            raise ValueError("Số dư không đủ")
        self._so_du -= so_tien


tk = TaiKhoanNganHang(1000000)
tk.nap_tien(500000)
print(tk.xem_so_du())   # 1500000

# tk._so_du = -999999999   # ⚠️ VẪN thực hiện được (Python không cấm cứng),
                            # nhưng dấu "_" là TÍN HIỆU RÕ RÀNG: "Đừng làm vậy, đây là nội bộ class"
```

**Quy ước đặt tên trong Python:**

- `ten_bien` — public, ai cũng dùng được thoải mái
- `_ten_bien` — "protected" theo quy ước, chỉ nên dùng bên trong class (hoặc class con)
- `__ten_bien` — "private" mạnh hơn, Python thực sự đổi tên phía sau (gọi là **name mangling**) để khó truy cập từ ngoài

python

```python
class VD:
    def __init__(self):
        self.__bi_mat = "dữ liệu nhạy cảm"

obj = VD()
# print(obj.__bi_mat)          # ❌ AttributeError
print(obj._VD__bi_mat)          # 'dữ liệu nhạy cảm' - vẫn truy cập được nếu biết tên đã bị "mangled"
```

**Nguyên tắc thực chiến**: dùng `_ten_bien` là đủ trong hầu hết trường hợp thực tế — nó truyền đạt rõ ý định "đây là nội bộ" cho đồng nghiệp đọc code, mà không cần cơ chế phức tạp của `__ten_bien` (thường chỉ cần khi thiết kế thư viện công khai lớn).

---

#### 7. Property — kiểm soát truy cập thuộc tính "trông như bình thường"

Đây là kỹ thuật Pythonic tinh tế, giúp bạn thêm logic kiểm tra khi đọc/gán thuộc tính, nhưng người dùng vẫn thấy nó "như thuộc tính bình thường" (không cần gọi `()` như method):

python

```python
class SanPham:
    def __init__(self, ten, gia):
        self.ten = ten
        self._gia = gia   # lưu giá trị thật ở biến "protected"

    @property
    def gia(self):
        """Getter - cho phép đọc sp.gia như thuộc tính bình thường"""
        return self._gia

    @gia.setter
    def gia(self, gia_moi):
        """Setter - kiểm tra tính hợp lệ TRƯỚC KHI cho phép gán giá trị mới"""
        if gia_moi < 0:
            raise ValueError("Giá sản phẩm không thể âm")
        self._gia = gia_moi


sp = SanPham("Áo thun", 150000)
print(sp.gia)          # 150000 - gọi như thuộc tính, KHÔNG cần sp.gia()

sp.gia = 200000         # gọi setter, tự động validate
print(sp.gia)           # 200000

# sp.gia = -50000       # ❌ ValueError: Giá sản phẩm không thể âm
```

**Đây chính là cách các thư viện chuyên nghiệp bảo vệ tính đúng đắn dữ liệu mà không phá vỡ cú pháp trực quan** — người dùng class `SanPham` không cần biết có logic kiểm tra ẩn bên trong, họ chỉ thấy `sp.gia = 200000` như gán biến thông thường, nhưng Python tự động chạy validation.

---

#### 8. Ví dụ thực chiến tổng hợp — Hệ thống quản lý giỏ hàng OOP

python

```python
class SanPham:
    def __init__(self, ten: str, gia: float):
        self.ten = ten
        self._gia = gia

    @property
    def gia(self):
        return self._gia

    @gia.setter
    def gia(self, gia_moi):
        if gia_moi < 0:
            raise ValueError("Giá không thể âm")
        self._gia = gia_moi

    def __str__(self):
        return f"{self.ten} - {self._gia:,.0f} VNĐ"


class GioHang:
    def __init__(self, ten_khach: str):
        self.ten_khach = ten_khach
        self._danh_sach_sp = []   # protected - khuyến khích dùng method để thao tác

    def them_san_pham(self, san_pham: SanPham, so_luong: int = 1):
        if so_luong <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
        self._danh_sach_sp.append((san_pham, so_luong))

    def tinh_tong_tien(self) -> float:
        return sum(sp.gia * sl for sp, sl in self._danh_sach_sp)

    def __str__(self):
        dong = [f"Giỏ hàng của {self.ten_khach}:"]
        for sp, sl in self._danh_sach_sp:
            dong.append(f"  - {sp} x{sl}")
        dong.append(f"Tổng: {self.tinh_tong_tien():,.0f} VNĐ")
        return "\n".join(dong)


ao = SanPham("Áo thun", 150000)
quan = SanPham("Quần jean", 450000)

gio = GioHang("Nguyễn Văn An")
gio.them_san_pham(ao, so_luong=2)
gio.them_san_pham(quan, so_luong=1)

print(gio)
```

**Kết quả:**

```
Giỏ hàng của Nguyễn Văn An:
  - Áo thun - 150,000 VNĐ x2
  - Quần jean - 450,000 VNĐ x1
Tổng: 750,000 VNĐ
```

Lưu ý cách `GioHang` **chứa** các object `SanPham` bên trong nó — đây gọi là quan hệ **"composition"** (một object được xây dựng từ các object khác), một mẫu thiết kế cực kỳ phổ biến trong OOP thực tế mà bạn sẽ gặp liên tục.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_13.py` xây dựng hệ thống **quản lý tài khoản ngân hàng OOP**:

1. Tạo class `TaiKhoan` với:
  - Constructor nhận `chu_tai_khoan` (str), `so_du_ban_dau` (float, mặc định 0)
  - Thuộc tính class `LAI_SUAT_NAM = 0.05` (dùng chung cho mọi tài khoản)
  - Thuộc tính class đếm `tong_so_tai_khoan_da_tao`, tự tăng mỗi khi tạo object mới
  - Property `so_du` với getter, và setter raise `ValueError` nếu gán giá trị âm
  - Method `nap_tien(so_tien)`: raise `ValueError` nếu `so_tien <= 0`
  - Method `rut_tien(so_tien)`: raise `ValueError` nếu vượt số dư hoặc `so_tien <= 0`
  - Method `tinh_lai_hang_nam()`: trả về số dư × `LAI_SUAT_NAM`
  - `__str__`: trả về chuỗi dạng `"Tài khoản của {chu_tai_khoan}: {so_du:,.0f} VNĐ"`
2. Tạo 3 object `TaiKhoan` khác nhau, thực hiện vài giao dịch nạp/rút, in thông tin bằng `print()` (tận dụng `__str__`)
3. In ra `TaiKhoan.tong_so_tai_khoan_da_tao` để xác nhận đếm đúng số lượng object đã tạo
4. Thử thách thêm: bọc một lệnh rút tiền vượt số dư trong `try/except ValueError` (kết hợp kiến thức Bài 10) để xử lý lỗi một cách chuyên nghiệp, không để chương trình crash

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 14: OOP nâng cao — Kế thừa, Đa hình, Trừu tượng hóa** — nơi bạn học cách xây dựng hệ thống class có quan hệ cha-con, tái sử dụng code hiệu quả hơn nữa, và hiểu tại sao các framework lớn như Django xây dựng toàn bộ kiến trúc dựa trên khái niệm này.
