Vai trò này tôi đã lưu vào bộ nhớ từ bài 3 và đang duy trì nhất quán suốt 13 bài học qua — tiếp tục áp dụng nghiêm túc cho toàn bộ hành trình còn lại. Giờ vào bài học nâng cao quan trọng nhất của OOP.

### 📘 Bài 14: OOP nâng cao — Kế thừa, Đa hình, Trừu tượng hóa

Ở Bài 13, bạn đã biết đóng gói dữ liệu + hành vi vào class. Bài này dạy bạn cách xây dựng **hệ thống class có quan hệ cha-con**, tái sử dụng code thông minh hơn — đây chính là kiến trúc đứng sau mọi framework lớn: Django models, PyTorch `nn.Module`, exception hierarchy mà bạn đã dùng ở Bài 10.

---

#### 1. Kế thừa (Inheritance) — tái sử dụng code qua quan hệ cha-con

**Vấn đề thực tế**: giả sử bạn có nhiều loại tài khoản ngân hàng — tài khoản thường, tài khoản tiết kiệm, tài khoản doanh nghiệp — chúng có nhiều điểm chung (đều có `so_du`, đều `nap_tien`/`rut_tien`) nhưng cũng có điểm riêng (tài khoản tiết kiệm có lãi suất, tài khoản doanh nghiệp có hạn mức tín dụng).

python

```python
class TaiKhoan:
    """Class CHA (base class / parent class) - chứa logic CHUNG"""
    def __init__(self, chu_tai_khoan: str, so_du: float = 0):
        self.chu_tai_khoan = chu_tai_khoan
        self._so_du = so_du

    @property
    def so_du(self):
        return self._so_du

    def nap_tien(self, so_tien: float):
        if so_tien <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0")
        self._so_du += so_tien

    def rut_tien(self, so_tien: float):
        if so_tien > self._so_du:
            raise ValueError("Số dư không đủ")
        self._so_du -= so_tien

    def __str__(self):
        return f"[{type(self).__name__}] {self.chu_tai_khoan}: {self._so_du:,.0f} VNĐ"


class TaiKhoanTietKiem(TaiKhoan):
    """Class CON (derived class / child class) - KẾ THỪA mọi thứ từ TaiKhoan"""
    def __init__(self, chu_tai_khoan: str, so_du: float = 0, lai_suat: float = 0.05):
        super().__init__(chu_tai_khoan, so_du)   # gọi constructor của class CHA
        self.lai_suat = lai_suat

    def tinh_lai(self) -> float:
        """Method MỚI - chỉ tài khoản tiết kiệm mới có"""
        return self._so_du * self.lai_suat


tk_thuong = TaiKhoan("An", 5000000)
tk_tiet_kiem = TaiKhoanTietKiem("Bình", 10000000, lai_suat=0.06)

tk_thuong.nap_tien(1000000)         # dùng method KẾ THỪA từ TaiKhoan
tk_tiet_kiem.nap_tien(500000)        # TaiKhoanTietKiem cũng có method này, không cần viết lại!
print(tk_tiet_kiem.tinh_lai())       # 630000.0 - method riêng chỉ class con mới có

print(tk_thuong)        # [TaiKhoan] An: 6,000,000 VNĐ
print(tk_tiet_kiem)     # [TaiKhoanTietKiem] Bình: 10,500,000 VNĐ
```

**Cú pháp quan trọng cần khắc sâu:**

- `class TaiKhoanTietKiem(TaiKhoan):` — dấu ngoặc chứa tên class cha, nghĩa là "kế thừa từ"
- `super().__init__(...)` — gọi constructor của class cha để tái sử dụng logic khởi tạo, tránh viết lại từ đầu
- Class con **tự động có mọi thuộc tính và method** của class cha, **cộng thêm** những gì bạn định nghĩa riêng

**Tại sao dùng `super().__init__()` mà không tự viết `self.chu_tai_khoan = chu_tai_khoan` lại?** Vì nếu sau này logic khởi tạo ở class cha thay đổi (ví dụ thêm validation cho `so_du` âm), mọi class con tự động được cập nhật — đây chính là nguyên tắc DRY (Bài 9) áp dụng ở cấp độ class.

---

#### 2. Override (ghi đè) method — class con thay đổi hành vi kế thừa

python

```python
class TaiKhoanDoanhNghiep(TaiKhoan):
    def __init__(self, chu_tai_khoan: str, so_du: float = 0, han_muc_tin_dung: float = 50_000_000):
        super().__init__(chu_tai_khoan, so_du)
        self.han_muc_tin_dung = han_muc_tin_dung

    def rut_tien(self, so_tien: float):
        """OVERRIDE - ghi đè hành vi rut_tien của class cha"""
        # Tài khoản doanh nghiệp được rút VƯỢT số dư trong hạn mức tín dụng
        if so_tien > self._so_du + self.han_muc_tin_dung:
            raise ValueError("Vượt quá hạn mức tín dụng cho phép")
        self._so_du -= so_tien   # số dư có thể ÂM trong phạm vi hạn mức


tk_dn = TaiKhoanDoanhNghiep("Công ty ABC", 5_000_000, han_muc_tin_dung=20_000_000)
tk_dn.rut_tien(15_000_000)     # OK - vượt số dư nhưng trong hạn mức tín dụng
print(tk_dn)                    # số dư: -10,000,000 VNĐ - hợp lệ với tài khoản doanh nghiệp

tk_thuong = TaiKhoan("An", 5_000_000)
# tk_thuong.rut_tien(15_000_000)   # ❌ ValueError - tài khoản thường KHÔNG có hạn mức
```

Khi class con định nghĩa lại một method đã có ở class cha **với cùng tên**, Python sẽ **ưu tiên chạy phiên bản của class con** — đây gọi là **override**. Đây là cách các loại tài khoản khác nhau có **hành vi khác nhau** cho cùng một hành động (`rut_tien`), dù chúng đều "là một loại `TaiKhoan`".

---

#### 3. Đa hình (Polymorphism) — "nhiều hình dạng, một giao diện"

Đây là khái niệm mạnh nhất của OOP: bạn có thể viết code xử lý **tổng quát cho class cha**, và Python tự động chạy đúng hành vi riêng của **từng class con cụ thể** — không cần biết chính xác đó là loại nào.

python

```python
danh_sach_tai_khoan = [
    TaiKhoan("An", 5_000_000),
    TaiKhoanTietKiem("Bình", 10_000_000, lai_suat=0.06),
    TaiKhoanDoanhNghiep("Công ty ABC", 5_000_000, han_muc_tin_dung=20_000_000),
]

# Vòng lặp KHÔNG cần biết mỗi tài khoản là loại gì cụ thể
# Python tự động gọi ĐÚNG phiên bản __str__ tương ứng với từng object
for tk in danh_sach_tai_khoan:
    print(tk)
```

**Kết quả:**

```
[TaiKhoan] An: 5,000,000 VNĐ
[TaiKhoanTietKiem] Bình: 10,000,000 VNĐ
[TaiKhoanDoanhNghiep] Công ty ABC: 5,000,000 VNĐ
```

**Đây chính là "đa hình"**: cùng viết `print(tk)`, nhưng Python tự động chọn đúng `__str__` tương ứng với loại object thực sự (`TaiKhoan`, `TaiKhoanTietKiem`, hay `TaiKhoanDoanhNghiep`). Code gọi hàm không cần biết chi tiết implementation bên trong — chỉ cần biết "nó là một TaiKhoan, nó biết cách tự in mình ra".

**Ứng dụng thực tế cực kỳ mạnh mẽ** — xử lý một danh sách hỗn hợp nhiều loại tài khoản mà không cần `if/elif` kiểm tra từng loại:

python

```python
def xu_ly_cuoi_ngay(danh_sach_tai_khoan):
    tong_so_du = 0
    for tk in danh_sach_tai_khoan:
        tong_so_du += tk.so_du   # gọi property so_du - hoạt động với MỌI loại tài khoản
        if isinstance(tk, TaiKhoanTietKiem):
            lai = tk.tinh_lai()
            tk.nap_tien(lai)
            print(f"Đã cộng lãi {lai:,.0f} VNĐ cho {tk.chu_tai_khoan}")
    return tong_so_du

tong = xu_ly_cuoi_ngay(danh_sach_tai_khoan)
print(f"Tổng số dư toàn hệ thống: {tong:,.0f} VNĐ")
```

`isinstance(tk, TaiKhoanTietKiem)` kiểm tra "object này có phải là (hoặc kế thừa từ) class `TaiKhoanTietKiem` không" — dùng khi bạn cần xử lý đặc biệt cho một loại con cụ thể trong khi vẫn duyệt chung một danh sách đa hình.

---

#### 4. `isinstance()` vs `type()` — phân biệt quan trọng

python

```python
print(isinstance(tk_tiet_kiem, TaiKhoanTietKiem))   # True
print(isinstance(tk_tiet_kiem, TaiKhoan))            # True - vì TaiKhoanTietKiem LÀ MỘT TaiKhoan (kế thừa)
print(type(tk_tiet_kiem) == TaiKhoan)                 # False - type() kiểm tra CHÍNH XÁC class, không tính kế thừa
```

**Nguyên tắc thực chiến**: luôn dùng `isinstance()` khi kiểm tra loại object trong code thực tế, vì nó tôn trọng quan hệ kế thừa (một `TaiKhoanTietKiem` *là một* `TaiKhoan` về mặt logic, nên nên được nhận diện như vậy).

---

#### 5. Kế thừa nhiều cấp (Multi-level Inheritance)

python

```python
class TaiKhoan:
    def __init__(self, chu_tk, so_du=0):
        self.chu_tk = chu_tk
        self._so_du = so_du

class TaiKhoanTietKiem(TaiKhoan):
    def __init__(self, chu_tk, so_du=0, lai_suat=0.05):
        super().__init__(chu_tk, so_du)
        self.lai_suat = lai_suat

class TaiKhoanTietKiemVIP(TaiKhoanTietKiem):
    """Kế thừa từ TaiKhoanTietKiem, mà TaiKhoanTietKiem lại kế thừa từ TaiKhoan"""
    def __init__(self, chu_tk, so_du=0, lai_suat=0.08, uu_dai=True):
        super().__init__(chu_tk, so_du, lai_suat)   # gọi constructor cấp trực tiếp trên (TaiKhoanTietKiem)
        self.uu_dai = uu_dai

tk_vip = TaiKhoanTietKiemVIP("Chi", 50_000_000)
print(isinstance(tk_vip, TaiKhoan))            # True - kế thừa xuyên qua nhiều cấp
print(isinstance(tk_vip, TaiKhoanTietKiem))    # True
```

Trong thực tế, kế thừa quá 2-3 cấp thường được xem là dấu hiệu thiết kế nên xem lại (dễ gây rối, khó theo dõi luồng logic) — nguyên tắc phổ biến trong ngành là **"ưu tiên composition hơn inheritance"** khi có thể (nhớ lại `GioHang` chứa `SanPham` ở Bài 13 — đó là composition).

---

#### 6. Abstract Base Class (ABC) — bắt buộc class con phải triển khai

Đôi khi bạn muốn định nghĩa một "khuôn mẫu bắt buộc" — class cha không nên được tạo object trực tiếp, chỉ tồn tại để các class con kế thừa và **buộc phải** triển khai một số method cụ thể:

python

```python
from abc import ABC, abstractmethod

class PhuongThucThanhToan(ABC):
    """Abstract class - KHÔNG THỂ tạo object trực tiếp từ class này"""

    @abstractmethod
    def xu_ly_thanh_toan(self, so_tien: float) -> bool:
        """Method trừu tượng - MỌI class con BẮT BUỘC phải viết lại (override)"""
        pass

    def in_bien_lai(self, so_tien: float):
        """Method thường - class con kế thừa mà không cần viết lại nếu không muốn"""
        print(f"Đã thanh toán {so_tien:,.0f} VNĐ qua {type(self).__name__}")


class ThanhToanViDienTu(PhuongThucThanhToan):
    def xu_ly_thanh_toan(self, so_tien: float) -> bool:
        print(f"Đang trừ {so_tien:,.0f} VNĐ từ ví điện tử...")
        return True


class ThanhToanTheNganHang(PhuongThucThanhToan):
    def xu_ly_thanh_toan(self, so_tien: float) -> bool:
        print(f"Đang xử lý giao dịch thẻ ngân hàng: {so_tien:,.0f} VNĐ...")
        return True


# pt = PhuongThucThanhToan()   # ❌ TypeError: Can't instantiate abstract class

vi = ThanhToanViDienTu()
vi.xu_ly_thanh_toan(500000)
vi.in_bien_lai(500000)          # kế thừa method thường, không cần viết lại
```

**Tại sao ABC quan trọng trong thực tế?** Nó đảm bảo **tính nhất quán trong toàn hệ thống** — nếu bạn (hoặc đồng nghiệp) tạo class `ThanhToanCrypto(PhuongThucThanhToan)` mà **quên** viết `xu_ly_thanh_toan`, Python sẽ **báo lỗi ngay khi tạo object**, thay vì để lỗi âm thầm xuất hiện lúc chạy production. Đây chính xác là cơ chế mà framework như Django dùng để định nghĩa "mọi model phải có method X", hay PyTorch dùng để bắt buộc mọi neural network phải triển khai `forward()`.

---

#### 7. Duck Typing — triết lý "kiểu ngầm" đặc trưng của Python

Python có một triết lý gọi là **duck typing**: *"Nếu nó đi như con vịt, kêu như con vịt, thì nó LÀ con vịt"* — nghĩa là Python **không quan tâm object thuộc class gì**, chỉ quan tâm **nó có method/thuộc tính cần dùng hay không**:

python

```python
class VeXeBuyt:
    def xu_ly_thanh_toan(self, so_tien):
        print(f"Trừ {so_tien:,.0f} VNĐ từ thẻ xe buýt")
        return True

# VeXeBuyt KHÔNG kế thừa từ PhuongThucThanhToan, nhưng vẫn "giống" nó về hành vi

def thuc_hien_giao_dich(phuong_thuc, so_tien):
    """Hàm này KHÔNG quan tâm phuong_thuc thuộc class gì
    - chỉ cần nó CÓ method xu_ly_thanh_toan() là chạy được"""
    phuong_thuc.xu_ly_thanh_toan(so_tien)

thuc_hien_giao_dich(ThanhToanViDienTu(), 100000)   # hoạt động
thuc_hien_giao_dich(VeXeBuyt(), 7000)               # CŨNG hoạt động - không cần kế thừa!
```

Đây là điểm khác biệt triết lý so với ngôn ngữ tĩnh như Java (nơi bắt buộc phải kế thừa interface tường minh) — Python linh hoạt hơn, tập trung vào "object có làm được việc cần không" hơn là "object thuộc dòng dõi nào".

---

#### 8. Ví dụ thực chiến tổng hợp — Hệ thống tính phí vận chuyển đa hình

python

```python
from abc import ABC, abstractmethod

class DonViVanChuyen(ABC):
    @abstractmethod
    def tinh_phi(self, khoi_luong_kg: float, khoang_cach_km: float) -> float:
        pass

    def __str__(self):
        return type(self).__name__


class GiaoHangNhanh(DonViVanChuyen):
    def tinh_phi(self, khoi_luong_kg, khoang_cach_km):
        return 20000 + khoi_luong_kg * 5000 + khoang_cach_km * 1000


class GiaoHangTietKiem(DonViVanChuyen):
    def tinh_phi(self, khoi_luong_kg, khoang_cach_km):
        return 10000 + khoi_luong_kg * 3000 + khoang_cach_km * 500


class GiaoHangHoaToc(DonViVanChuyen):
    def tinh_phi(self, khoi_luong_kg, khoang_cach_km):
        return 50000 + khoi_luong_kg * 8000 + khoang_cach_km * 2000


def so_sanh_gia_van_chuyen(khoi_luong, khoang_cach):
    cac_don_vi = [GiaoHangNhanh(), GiaoHangTietKiem(), GiaoHangHoaToc()]
    for dv in cac_don_vi:
        phi = dv.tinh_phi(khoi_luong, khoang_cach)   # đa hình - gọi đúng logic mỗi loại
        print(f"{dv}: {phi:,.0f} VNĐ")

so_sanh_gia_van_chuyen(khoi_luong=2.5, khoang_cach=15)
```

Đây chính là mô hình thiết kế **"Strategy Pattern"** — một trong những mẫu thiết kế phần mềm (design pattern) phổ biến nhất, cho phép **thay đổi thuật toán/chiến lược tại runtime** mà không cần sửa code gọi hàm. Bạn sẽ gặp lại triết lý này ở khắp nơi trong các hệ thống thực tế lớn.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_14.py` xây dựng **hệ thống tính lương đa hình cho các loại nhân viên**:

1. Tạo abstract class `NhanVien` (dùng `ABC`) với:
  - Constructor nhận `ten` (str)
  - Abstract method `tinh_luong() -> float`
  - Method thường `in_phieu_luong()`: in `f"{self.ten}: {self.tinh_luong():,.0f} VNĐ"`
2. Tạo 3 class con kế thừa từ `NhanVien`:
  - `NhanVienChinhThuc`: nhận thêm `luong_co_ban`, `tinh_luong()` trả về `luong_co_ban`
  - `NhanVienThoiViec`: nhận thêm `so_gio_lam`, `luong_theo_gio`, `tinh_luong()` trả về `so_gio_lam * luong_theo_gio`
  - `NhanVienKinhDoanh`: nhận thêm `luong_co_ban`, `doanh_so`, `ty_le_hoa_hong` (mặc định 0.03), `tinh_luong()` trả về `luong_co_ban + doanh_so * ty_le_hoa_hong`
3. Tạo danh sách gồm nhiều loại nhân viên khác nhau, dùng vòng lặp `for` duyệt qua và gọi `in_phieu_luong()` cho mỗi người (minh họa đa hình)
4. Viết hàm `tong_chi_phi_luong(danh_sach_nhan_vien)` tính tổng lương toàn công ty — hàm này không cần biết từng nhân viên thuộc loại nào
5. Thử cố ý tạo object trực tiếp từ `NhanVien()` để tận mắt thấy lỗi `TypeError` (vì là abstract class)
6. Thử thách thêm: dùng `isinstance()` để lọc riêng danh sách chỉ gồm `NhanVienKinhDoanh`, tính tổng hoa hồng đã trả cho nhóm này

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 15: Iterator, Generator, Decorator** — ba khái niệm nâng cao giúp bạn viết code Python hiệu quả về bộ nhớ và "chuẩn Pythonic" ở cấp độ chuyên gia, đồng thời giải thích rõ cơ chế `for` và `range()` mà bạn đã dùng từ Bài 5 thực sự hoạt động như thế nào bên dưới.
