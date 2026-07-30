Chào bạn! Bạn đã vượt qua 5 bài nền tảng xuất sắc! Bây giờ chúng ta bước vào một trong những khái niệm **QUAN TRỌNG NHẤT** trong lập trình: **Lập trình Hướng đối tượng (OOP)**. Đây là thứ sẽ giúp bạn viết code có tổ chức như các dự án thực tế!

---

# 📘 BÀI 6: OOP - LỚP VÀ ĐỐI TƯỢNG (CLASS & OBJECT)

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu OOP là gì và tại sao nó quan trọng
- Tạo `Class` và `Object` (thể hiện của class)
- Sử dụng `__init__()` - phương thức khởi tạo
- Phân biệt `instance method`, `class method`, `static method`
- Hiểu về `encapsulation` (đóng gói) với `property`
- Sử dụng các magic methods: `__str__`, `__repr__`, `__len__`

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. OOP là gì? Tại sao phải học?

**OOP = Lập trình hướng đối tượng** - cách tổ chức code giống như thế giới thực:

- **Class (Lớp)**: Bản thiết kế (khuôn mẫu) - như bản vẽ của một ngôi nhà
- **Object (Đối tượng)**: Thể hiện cụ thể - như ngôi nhà thật được xây từ bản vẽ

```python
# Class = Bản thiết kế "Sinh viên"
class SinhVien:
    pass


# Object = Các sinh viên cụ thể
sv1 = SinhVien()  # Thể hiện 1
sv2 = SinhVien()  # Thể hiện 2
```

**Lợi ích của OOP:**
- ✅ **Code có tổ chức**, dễ đọc, dễ bảo trì
- ✅ **Tái sử dụng** code qua kế thừa
- ✅ **Mô hình hóa** thế giới thực vào code
- ✅ **Dễ mở rộng** - thêm chức năng không phá vỡ code cũ

---

### 1.2. Tạo Class cơ bản

```python
class SinhVien:
    """Lớp đại diện cho một sinh viên"""

    # Thuộc tính của lớp (class attribute) - Dùng chung cho tất cả
    truong = "Đại học Bách Khoa"
    so_luong_sv = 0

    def __init__(self, ma, ten, tuoi):
        """Phương thức khởi tạo - chạy khi tạo object"""
        # Instance attributes - Riêng cho từng object
        self.ma = ma
        self.ten = ten
        self.tuoi = tuoi
        self.diem = []  # Danh sách điểm

        # Tăng số lượng sinh viên
        SinhVien.so_luong_sv += 1

    def them_diem(self, diem):
        """Thêm điểm cho sinh viên"""
        self.diem.append(diem)

    def tinh_trung_binh(self):
        """Tính điểm trung bình"""
        if len(self.diem) == 0:
            return 0
        return sum(self.diem) / len(self.diem)

    def in_thong_tin(self):
        """In thông tin sinh viên"""
        print(f"Mã: {self.ma}")
        print(f"Tên: {self.ten}")
        print(f"Tuổi: {self.tuoi}")
        print(f"Trường: {self.truong}")
        print(f"Điểm TB: {self.tinh_trung_binh():.2f}")


# Tạo object từ class
sv1 = SinhVien("SV001", "Nguyễn Văn An", 20)
sv2 = SinhVien("SV002", "Trần Thị Bình", 21)

# Sử dụng object
sv1.them_diem(8.5)
sv1.them_diem(9.0)
sv1.in_thong_tin()

print(f"Tổng số sinh viên: {SinhVien.so_luong_sv}")  # 2
```

---

### 1.3. `self` là gì? Tại sao phải có?

**`self` = Tham chiếu đến object hiện tại**

```python
class Dog:
    def __init__(self, name):
        self.name = name  # self.name = thuộc tính của object này

    def bark(self):
        print(f"{self.name} says: Woof!")


# Khi gọi: self chính là dog1
dog1 = Dog("Buddy")
dog1.bark()  # Python chuyển thành Dog.bark(dog1)

# Vậy dog1 là self trong phương thức bark()
```

**Quy tắc vàng:**
- ✅ **Luôn có `self` là tham số đầu tiên** trong mọi instance method
- ✅ **Dùng `self.ten_thuoc_tinh`** để truy cập thuộc tính của object
- ✅ **Không bao giờ tự truyền giá trị cho `self`** - Python làm việc đó

---

### 1.4. Instance Method vs Class Method vs Static Method

```python
class HinhTron:
    """Lớp hình tròn"""

    # Class attribute (thuộc tính dùng chung)
    PI = 3.14159
    hinh = "Tròn"

    def __init__(self, ban_kinh):
        # Instance attribute (thuộc tính riêng)
        self.ban_kinh = ban_kinh

    # INSTANCE METHOD - Cần self, truy cập được dữ liệu object
    def tinh_dien_tich(self):
        return self.PI * self.ban_kinh**2

    def tinh_chu_vi(self):
        return 2 * self.PI * self.ban_kinh

    # CLASS METHOD - Dùng @classmethod, nhận class (cls) thay vì self
    @classmethod
    def tao_hinh_tron_tu_duong_kinh(cls, duong_kinh):
        """Tạo hình tròn từ đường kính (Factory method)"""
        ban_kinh = duong_kinh / 2
        return cls(ban_kinh)

    @classmethod
    def thay_doi_PI(cls, pi_moi):
        """Thay đổi giá trị PI dùng chung"""
        cls.PI = pi_moi

    # STATIC METHOD - Không cần self hay cls, như hàm thường
    @staticmethod
    def la_hinh_tron(hinh_dang):
        """Kiểm tra có phải hình tròn không"""
        return hinh_dang == "Tròn"

    @staticmethod
    def tinh_dien_tich_tu_ban_kinh(r):
        """Tính diện tích mà không cần tạo object"""
        return HinhTron.PI * r**2


# SỬ DỤNG
# 1. Instance method: cần tạo object
ht = HinhTron(5)
print(ht.tinh_dien_tich())  # 78.53975

# 2. Class method: gọi trực tiếp qua class
ht2 = HinhTron.tao_hinh_tron_tu_duong_kinh(10)
print(ht2.ban_kinh)  # 5.0

# 3. Static method: gọi trực tiếp
print(HinhTron.la_hinh_tron("Vuông"))  # False
print(HinhTron.tinh_dien_tich_tu_ban_kinh(5))  # 78.53975
```

**Khi nào dùng gì?**
| Loại method | Khi nào dùng | Ví dụ |
|-------------|--------------|-------|
| **Instance** | Cần truy cập dữ liệu của object | `tinh_dien_tich()` |
| **Class** | Tạo object theo cách đặc biệt | `tao_tu_duong_kinh()` |
| **Static** | Không cần object hay class | `la_hinh_tron()` |

---

### 1.5. Encapsulation (Đóng gói) và Property

**Encapsulation = Che giấu dữ liệu, chỉ cho truy cập qua các phương thức**

```python
class TaiKhoanNganHang:
    def __init__(self, so_tk, chu_tk, so_du=0):
        self.so_tk = so_tk
        self.chu_tk = chu_tk
        self.__so_du = so_du  # Private attribute (__ = bắt đầu bằng 2 gạch dưới)
        self.__pin = "0000"
        self.__da_khoa = False

    # GETTER - Đọc dữ liệu
    @property
    def so_du(self):
        """Lấy số dư (chỉ đọc)"""
        return self.__so_du

    @property
    def da_khoa(self):
        return self.__da_khoa

    # SETTER - Sửa dữ liệu (có kiểm tra)
    @da_khoa.setter
    def da_khoa(self, trang_thai):
        """Khóa hoặc mở khóa tài khoản (có kiểm tra)"""
        if not isinstance(trang_thai, bool):
            raise ValueError("Trạng thái khóa phải là True/False")
        self.__da_khoa = trang_thai

    # Phương thức thay đổi dữ liệu
    def nap_tien(self, so_tien):
        """Nạp tiền vào tài khoản"""
        if self.__da_khoa:
            raise ValueError("Tài khoản đã bị khóa!")
        if so_tien <= 0:
            raise ValueError("Số tiền nạp phải > 0")
        self.__so_du += so_tien
        return f"Nạp thành công {so_tien}đ. Số dư: {self.__so_du}đ"

    def rut_tien(self, so_tien):
        """Rút tiền từ tài khoản"""
        if self.__da_khoa:
            raise ValueError("Tài khoản đã bị khóa!")
        if so_tien <= 0:
            raise ValueError("Số tiền rút phải > 0")
        if so_tien > self.__so_du:
            raise ValueError("Số dư không đủ!")
        self.__so_du -= so_tien
        return f"Rút thành công {so_tien}đ. Số dư: {self.__so_du}đ"

    def doi_pin(self, pin_cu, pin_moi):
        """Đổi mã PIN"""
        if pin_cu != self.__pin:
            raise ValueError("PIN cũ không đúng!")
        if len(pin_moi) != 4 or not pin_moi.isdigit():
            raise ValueError("PIN mới phải là 4 chữ số!")
        self.__pin = pin_moi
        return "Đổi PIN thành công!"


# Sử dụng
tk = TaiKhoanNganHang("123456", "Nguyễn Văn A", 1000000)

# Đọc dữ liệu qua property (không cần dấu () )
print(f"Số dư: {tk.so_du}đ")

# Sửa dữ liệu qua setter
tk.da_khoa = True
print(f"Tài khoản đã khóa: {tk.da_khoa}")  # True

# Thử rút tiền (sẽ lỗi)
try:
    tk.rut_tien(100000)
except ValueError as e:
    print(f"Lỗi: {e}")  # Lỗi: Tài khoản đã bị khóa!
```

**Quy ước đặt tên trong Python:**
- `_ten` → Protected (không nên truy cập từ bên ngoài)
- `__ten` → Private (Python sẽ đổi tên thành `_Class__ten`)
- `__ten__` → Magic method (đừng tự đặt)

---

### 1.6. Magic Methods (Phương thức đặc biệt)

```python
class SinhVien:
    def __init__(self, ma, ten, tuoi):
        self.ma = ma
        self.ten = ten
        self.tuoi = tuoi

    # __str__: Được gọi khi print() hoặc str()
    def __str__(self):
        return f"Sinh viên: {self.ten} ({self.ma})"

    # __repr__: Đại diện cho lập trình viên
    def __repr__(self):
        return f"SinhVien('{self.ma}', '{self.ten}', {self.tuoi})"

    # __len__: Được gọi khi len()
    def __len__(self):
        return len(self.ten)

    # __eq__: So sánh bằng (==)
    def __eq__(self, other):
        if not isinstance(other, SinhVien):
            return False
        return self.ma == other.ma

    # __lt__: So sánh nhỏ hơn (dùng để sắp xếp)
    def __lt__(self, other):
        return self.ten < other.ten

    # __add__: Cộng 2 đối tượng (+)
    def __add__(self, other):
        if isinstance(other, SinhVien):
            return self.tuoi + other.tuoi
        return self.tuoi + other

    # __contains__: Kiểm tra 'in'
    def __contains__(self, item):
        return item in self.ten


# Sử dụng
sv1 = SinhVien("SV001", "Nguyễn Văn An", 20)
sv2 = SinhVien("SV002", "Trần Thị Bình", 21)

print(sv1)  # Sinh viên: Nguyễn Văn An (SV001) - dùng __str__
print(repr(sv1))  # SinhVien('SV001', 'Nguyễn Văn An', 20) - dùng __repr__

print(len(sv1))  # 13 (số ký tự trong tên)

print(sv1 == sv2)  # False (so sánh mã)
print(sv1 < sv2)  # True (so sánh tên)

print(sv1 + sv2)  # 41 (cộng tuổi)
print("An" in sv1)  # True (kiểm tra trong tên)
```

**Các magic methods thông dụng:**
| Method | Khi gọi | Ví dụ |
|--------|---------|-------|
| `__init__` | Khởi tạo object | `SinhVien()` |
| `__str__` | `print(obj)` | `print(sv)` |
| `__repr__` | `repr(obj)` | `repr(sv)` |
| `__len__` | `len(obj)` | `len(sv)` |
| `__eq__` | `==` | `sv1 == sv2` |
| `__lt__` | `<` | `sv1 < sv2` |
| `__add__` | `+` | `sv1 + sv2` |
| `__contains__` | `in` | `"An" in sv1` |

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống quản lý nhân viên

```python
from datetime import datetime


class NhanVien:
    """Lớp cơ sở cho tất cả nhân viên"""

    so_luong = 0

    def __init__(self, ma, ten, ngay_sinh, luong_co_ban):
        self.ma = ma
        self.ten = ten
        self.ngay_sinh = datetime.strptime(ngay_sinh, "%d/%m/%Y")
        self.luong_co_ban = luong_co_ban
        self.ngay_vao_lam = datetime.now()
        self._da_nghi = False
        NhanVien.so_luong += 1

    @property
    def tuoi(self):
        """Tính tuổi từ ngày sinh"""
        today = datetime.now()
        return (
            today.year
            - self.ngay_sinh.year
            - ((today.month, today.day) < (self.ngay_sinh.month, self.ngay_sinh.day))
        )

    @property
    def da_nghi(self):
        return self._da_nghi

    def nghi_viec(self):
        """Nhân viên nghỉ việc"""
        self._da_nghi = True
        NhanVien.so_luong -= 1
        return f"Nhân viên {self.ten} đã nghỉ việc"

    def tinh_luong(self):
        """Tính lương (sẽ được override ở lớp con)"""
        return self.luong_co_ban

    def __str__(self):
        status = "Đã nghỉ" if self.da_nghi else "Đang làm"
        return f"{self.ma}: {self.ten} ({self.tuoi} tuổi) - {status}"


class LapTrinhVien(NhanVien):
    """Lớp lập trình viên"""

    def __init__(self, ma, ten, ngay_sinh, luong_co_ban, ngon_ngu, so_du_an=0):
        super().__init__(ma, ten, ngay_sinh, luong_co_ban)
        self.ngon_ngu = ngon_ngu
        self.so_du_an = so_du_an
        self.thuong_du_an = 1000000

    def hoan_thanh_du_an(self):
        """Tăng số dự án khi hoàn thành"""
        self.so_du_an += 1

    def tinh_luong(self):
        """Override: Lương = lương cơ bản + thưởng dự án"""
        return self.luong_co_ban + (self.so_du_an * self.thuong_du_an)

    def __str__(self):
        return (
            f"{super().__str__()} - Lập trình {self.ngon_ngu} ({self.so_du_an} dự án)"
        )


class KeToan(NhanVien):
    """Lớp kế toán"""

    def __init__(self, ma, ten, ngay_sinh, luong_co_ban, phong_ban):
        super().__init__(ma, ten, ngay_sinh, luong_co_ban)
        self.phong_ban = phong_ban
        self._phu_cap = 2000000

    def tinh_luong(self):
        return self.luong_co_ban + self._phu_cap

    def __str__(self):
        return f"{super().__str__()} - Kế toán phòng {self.phong_ban}"


# Sử dụng
dev1 = LapTrinhVien("DEV001", "Nguyễn Văn Code", "15/03/1995", 15000000, "Python")
dev2 = LapTrinhVien("DEV002", "Trần Thị Bug", "20/07/1998", 12000000, "JavaScript")
ke_toan = KeToan("KT001", "Lê Văn Sổ", "10/11/1990", 10000000, "Kế toán")

# Làm việc
dev1.hoan_thanh_du_an()
dev1.hoan_thanh_du_an()
dev2.hoan_thanh_du_an()

# Hiển thị
print(dev1)
print(f"Lương DEV1: {dev1.tinh_luong():,}đ")
print(ke_toan)
print(f"Lương kế toán: {ke_toan.tinh_luong():,}đ")
print(f"Tổng số nhân viên: {NhanVien.so_luong}")
```

---

### Ví dụ 2: Hệ thống đặt hàng

```python
class SanPham:
    def __init__(self, ma, ten, gia, so_luong=0):
        self.ma = ma
        self.ten = ten
        self.gia = gia
        self.so_luong = so_luong

    def cap_nhat_so_luong(self, so_luong_moi):
        """Cập nhật số lượng tồn kho"""
        if so_luong_moi < 0:
            raise ValueError("Số lượng không thể âm")
        self.so_luong = so_luong_moi

    def __str__(self):
        return f"{self.ma}: {self.ten} - {self.gia:,}đ (còn {self.so_luong})"


class DonHang:
    """Lớp đơn hàng"""

    def __init__(self, ma_don, khach_hang):
        self.ma_don = ma_don
        self.khach_hang = khach_hang
        self.danh_sach_san_pham = []
        self.ngay_tao = datetime.now()
        self.da_thanh_toan = False

    def them_san_pham(self, san_pham, so_luong=1):
        """Thêm sản phẩm vào đơn hàng"""
        if not isinstance(san_pham, SanPham):
            raise TypeError("Phải là đối tượng SanPham")
        if san_pham.so_luong < so_luong:
            raise ValueError(f"Không đủ hàng! Chỉ còn {san_pham.so_luong}")

        # Kiểm tra xem sản phẩm đã có trong đơn chưa
        for item in self.danh_sach_san_pham:
            if item["san_pham"].ma == san_pham.ma:
                item["so_luong"] += so_luong
                san_pham.so_luong -= so_luong
                return f"Đã cập nhật số lượng {san_pham.ten}: {item['so_luong']}"

        # Thêm mới
        self.danh_sach_san_pham.append({"san_pham": san_pham, "so_luong": so_luong})
        san_pham.so_luong -= so_luong
        return f"Đã thêm {san_pham.ten} x {so_luong}"

    def tinh_tong_tien(self):
        """Tính tổng tiền đơn hàng"""
        return sum(
            item["san_pham"].gia * item["so_luong"] for item in self.danh_sach_san_pham
        )

    def thanh_toan(self):
        """Thanh toán đơn hàng"""
        if len(self.danh_sach_san_pham) == 0:
            raise ValueError("Đơn hàng trống, không thể thanh toán!")
        self.da_thanh_toan = True
        return f"Đã thanh toán {self.tinh_tong_tien():,}đ"

    def __str__(self):
        status = "Đã TT" if self.da_thanh_toan else "Chưa TT"
        result = f"ĐƠN HÀNG {self.ma_don} - {self.khach_hang} - {status}\n"
        result += "=" * 40 + "\n"
        for item in self.danh_sach_san_pham:
            sp = item["san_pham"]
            sl = item["so_luong"]
            thanh_tien = sp.gia * sl
            result += f"{sp.ten} x {sl} = {thanh_tien:,}đ\n"
        result += "=" * 40 + "\n"
        result += f"TỔNG CỘNG: {self.tinh_tong_tien():,}đ"
        return result


# Sử dụng
sp1 = SanPham("SP001", "Áo sơ mi", 250000, 10)
sp2 = SanPham("SP002", "Quần jean", 350000, 5)
sp3 = SanPham("SP003", "Giày thể thao", 500000, 3)

don = DonHang("DH001", "Nguyễn Văn A")
print(don.them_san_pham(sp1, 2))
print(don.them_san_pham(sp2, 1))
print(don.them_san_pham(sp3, 1))

print(don)
print(don.thanh_toan())
print(don)
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Tạo class `HinhChuNhat` với:
- Thuộc tính: chiều dài, chiều rộng
- Phương thức: tính diện tích, chu vi
- `__str__`: in ra thông tin

**Bài 2:** Tạo class `PhanSo` với:
- Thuộc tính: tử số, mẫu số
- Phương thức: tối giản, cộng, trừ, nhân, chia
- Magic methods: `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__str__`

**Bài 3:** Tạo class `NhanVien` với:
- Thuộc tính: mã, tên, lương
- Property: `thue` (lương > 10tr → 10%, > 20tr → 20%, còn lại 5%)
- Phương thức: `tinh_luong_net()` (lương - thuế)

**Bài 4:** Tạo class `Sach` và `ThuVien`:
- `Sach`: mã, tên, tác giả, năm XB, trạng thái
- `ThuVien`: chứa danh sách sách
- Phương thức: thêm, xóa, tìm kiếm, mượn, trả

**Bài 5:** Tạo class `TaiKhoan` và `NganHang`:
- `TaiKhoan`: số TK, chủ TK, số dư, lịch sử giao dịch
- `NganHang`: quản lý nhiều tài khoản
- Phương thức: tạo TK, gửi tiền, rút tiền, chuyển khoản, xem lịch sử

**Bài 6:** Tạo class `HocSinh` và `LopHoc`:
- `HocSinh`: tên, điểm các môn, tính TB
- `LopHoc`: danh sách học sinh
- Phương thức: thêm HS, xóa HS, xếp loại, in danh sách theo điểm

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Tạo class `DangKyMonHoc`:
- `MonHoc`: mã, tên, số tín chỉ
- `SinhVien`: mã, tên, danh sách môn đã đăng ký
- `HeThongQuanLy`: quản lý sinh viên và môn học
- Yêu cầu: đăng ký môn, hủy đăng ký, kiểm tra tiên quyết, tính học phí

**Bài 8:** Tạo class `DoThi` (Graph) và `Dinh` (Vertex):
- Dùng OOP để biểu diễn đồ thị
- Phương thức: thêm cạnh, BFS, DFS, tìm đường đi ngắn nhất

**Bài 9:** Tạo class `Calendar` và `Event`:
- `Event`: tên, thời gian bắt đầu, kết thúc, mô tả
- `Calendar`: quản lý các event
- Phương thức: thêm, sửa, xóa, tìm kiếm, kiểm tra trùng lịch

**Bài 10:** Xây dựng hệ thống `ChatBot` đơn giản:
- Class `User`: tên, lịch sử chat
- Class `Bot`: có các rule và responses
- Phương thức: nhận tin nhắn, xử lý, trả lời
- Lưu lịch sử chat của từng user

---

## 🏗️ MINI-PROJECT: HỆ THỐNG QUẢN LÝ KHÁCH SẠN

```python
"""
Xây dựng hệ thống quản lý khách sạn với OOP:

1. KHÁCH SẠN (Hotel):
   - Tên, địa chỉ, số sao
   - Danh sách phòng
   - Danh sách đặt phòng
   
2. PHÒNG (Room):
   - Số phòng, loại phòng (Đơn/Đôi/VIP)
   - Giá/đêm, trạng thái (Trống/Đã đặt/Đang ở)
   - Tiện nghi (list)

3. KHÁCH HÀNG (Customer):
   - CMND, tên, số điện thoại
   - Lịch sử đặt phòng

4. ĐẶT PHÒNG (Booking):
   - Mã đặt, khách hàng, phòng
   - Ngày nhận, ngày trả
   - Tổng tiền, trạng thái (Chờ/Đã cọc/Đã nhận/Đã trả)

5. CÁC CHỨC NĂNG:
   - Tìm phòng trống theo loại & thời gian
   - Đặt phòng
   - Check-in, Check-out
   - Tính tiền
   - Thống kê doanh thu theo tháng
   - Quản lý khách hàng thân thiết

Yêu cầu: Sử dụng đầy đủ các khái niệm OOP đã học
"""

# Code của bạn ở đây
```

---

## ✅ KIỂM TRA CODE OOP CHUYÊN NGHIỆP

- [ ] Tên class viết hoa theo PascalCase (ví dụ: `SinhVien`)
- [ ] Tên method viết thường, snake_case
- [ ] Có `__init__` để khởi tạo đầy đủ thuộc tính
- [ ] Sử dụng `@property` cho các thuộc tính tính toán
- [ ] Dùng `self` đúng cách trong các instance method
- [ ] Phân biệt được khi nào dùng classmethod vs staticmethod
- [ ] Có `__str__` hoặc `__repr__` để dễ debug
- [ ] Class có mục đích duy nhất (Single Responsibility Principle)
- [ ] Code có docstring giải thích từng class và method

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo một lớp đặc biệt: Immutable (không thể thay đổi sau khi tạo)
class ImmutablePoint:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    # Không cho phép thay đổi thuộc tính
    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise AttributeError(f"Không thể thay đổi {name}")
        super().__setattr__(name, value)


# Test
p = ImmutablePoint(3, 4)
print(p.x, p.y)  # 3 4
# p.x = 5  # AttributeError: Không thể thay đổi x
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Cú pháp/Cách dùng | Ví dụ |
|-----------|-------------------|-------|
| **Class** | `class TenClass:` | `class SinhVien:` |
| **Init** | `def __init__(self, ...):` | Khởi tạo object |
| **Instance method** | `def method(self):` | Cần self, truy cập dữ liệu object |
| **Class method** | `@classmethod def method(cls):` | Nhận class, tạo factory |
| **Static method** | `@staticmethod def method():` | Không cần self/cls |
| **Property** | `@property def ten(self):` | Getter |
| **Setter** | `@ten.setter def ten(self, val):` | Setter có kiểm tra |
| **Private** | `__thuoc_tinh` | Che giấu dữ liệu |
| **Magic methods** | `__str__`, `__eq__`, `__add__` | Đặc biệt cho class |

---

**Chúc mừng bạn đã bước vào thế giới OOP! Đây là bước ngoặt từ lập trình cơ bản lên chuyên nghiệp.** 💪

*Bài 7 sẽ dạy bạn về Kế thừa và Đa hình - sức mạnh thực sự của OOP!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀