Chào bạn! Bạn đã nắm vững OOP cơ bản - tuyệt vời! Bây giờ chúng ta bước vào **Bài 7: Kế thừa và Đa hình** - đây là nơi OOP thể hiện sức mạnh thực sự, giúp bạn viết code tái sử dụng và mở rộng một cách chuyên nghiệp!

---

# 📘 BÀI 7: KẾ THỪA VÀ ĐA HÌNH (INHERITANCE & POLYMORPHISM)

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu và áp dụng **Kế thừa (Inheritance)** để tái sử dụng code
- Sử dụng `super()` để gọi phương thức của lớp cha
- Hiểu **Đa hình (Polymorphism)** - cùng 1 interface, nhiều hành vi
- Làm việc với **Abstract Class** và **ABC (Abstract Base Class)**
- Hiểu **Multiple Inheritance** và **Method Resolution Order (MRO)**

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Kế thừa là gì? Tại sao cần?

**Kế thừa = Lớp con nhận tất cả thuộc tính và phương thức từ lớp cha**

```python
# Lớp cha (Parent/Base Class)
class DongVat:
    def __init__(self, ten, tuoi):
        self.ten = ten
        self.tuoi = tuoi

    def an(self):
        print(f"{self.ten} đang ăn...")

    def ngu(self):
        print(f"{self.ten} đang ngủ...")


# Lớp con (Child/Derived Class) - Kế thừa từ DongVat
class Cho(DongVat):
    def sua(self):
        print(f"{self.ten} sủa: Gâu gâu!")

    # Override phương thức của cha
    def an(self):
        print(f"{self.ten} ăn xương...")


class Meo(DongVat):
    def keu(self):
        print(f"{self.ten} kêu: Meo meo!")

    def an(self):
        print(f"{self.ten} ăn cá...")


# Sử dụng
cho = Cho("Buddy", 3)
meo = Meo("Kitty", 2)

cho.an()  # Buddy ăn xương... (override)
cho.ngu()  # Buddy đang ngủ... (kế thừa)
cho.sua()  # Buddy sủa: Gâu gâu!

meo.an()  # Kitty ăn cá...
meo.keu()  # Kitty kêu: Meo meo!
```

**Lợi ích:**
- ✅ **Tái sử dụng code** - không viết lại những gì đã có
- ✅ **Mở rộng dễ dàng** - thêm chức năng mới mà không sửa code cũ
- ✅ **Code có tổ chức** - phân cấp rõ ràng

---

### 1.2. Cú pháp kế thừa và `super()`

```python
class NhanVien:
    """Lớp cha - Nhân viên"""

    def __init__(self, ma, ten, luong_co_ban):
        self.ma = ma
        self.ten = ten
        self.luong_co_ban = luong_co_ban
        self.ngay_vao_lam = "2024-01-01"

    def tinh_luong(self):
        return self.luong_co_ban

    def in_thong_tin(self):
        return f"NV: {self.ma} - {self.ten} - Lương: {self.tinh_luong():,}đ"


class LapTrinhVien(NhanVien):
    """Lớp con - Lập trình viên"""

    def __init__(self, ma, ten, luong_co_ban, ngon_ngu, so_du_an=0):
        # Gọi __init__ của lớp cha
        super().__init__(ma, ten, luong_co_ban)

        # Thêm thuộc tính riêng
        self.ngon_ngu = ngon_ngu
        self.so_du_an = so_du_an
        self.thuong_du_an = 1000000

    def hoan_thanh_du_an(self):
        self.so_du_an += 1

    # Override phương thức của cha
    def tinh_luong(self):
        return super().tinh_luong() + (self.so_du_an * self.thuong_du_an)

    def in_thong_tin(self):
        # Gọi phương thức cha và thêm thông tin riêng
        thong_tin_co_ban = super().in_thong_tin()
        return f"{thong_tin_co_ban} - {self.ngon_ngu} ({self.so_du_an} dự án)"


# Sử dụng
dev = LapTrinhVien("DEV001", "Nguyễn Văn Code", 15000000, "Python", 3)
print(dev.in_thong_tin())
# NV: DEV001 - Nguyễn Văn Code - Lương: 18,000,000đ - Python (3 dự án)
```

**Quy tắc vàng với `super()`:**
- ✅ **Luôn gọi `super().__init__()`** trong `__init__` của lớp con
- ✅ Dùng `super()` để gọi phương thức cha khi override
- ✅ `super()` giúp code **linh hoạt với đa kế thừa**

---

### 1.3. Đa hình (Polymorphism) - Sức mạnh của OOP

**Đa hình = Cùng 1 phương thức nhưng hành vi khác nhau ở các lớp khác nhau**

```python
# Các lớp khác nhau có cùng interface (phương thức)
class Hinh:
    def tinh_dien_tich(self):
        pass


class HinhTron(Hinh):
    def __init__(self, ban_kinh):
        self.ban_kinh = ban_kinh

    def tinh_dien_tich(self):
        return 3.14 * self.ban_kinh**2


class HinhChuNhat(Hinh):
    def __init__(self, dai, rong):
        self.dai = dai
        self.rong = rong

    def tinh_dien_tich(self):
        return self.dai * self.rong


class HinhTamGiac(Hinh):
    def __init__(self, day, cao):
        self.day = day
        self.cao = cao

    def tinh_dien_tich(self):
        return 0.5 * self.day * self.cao


# HÀM ĐA HÌNH - Nhận bất kỳ đối tượng nào có phương thức tinh_dien_tich
def in_dien_tich(hinh):
    """Hàm này KHÔNG quan tâm hình cụ thể là gì"""
    print(f"Diện tích: {hinh.tinh_dien_tich():.2f}")


# Sử dụng - Mọi hình đều có thể truyền vào
hinh1 = HinhTron(5)
hinh2 = HinhChuNhat(4, 6)
hinh3 = HinhTamGiac(10, 8)

in_dien_tich(hinh1)  # Diện tích: 78.50
in_dien_tich(hinh2)  # Diện tích: 24.00
in_dien_tich(hinh3)  # Diện tích: 40.00

# Thậm chí có thể dùng với list
danh_sach_hinh = [hinh1, hinh2, hinh3]
for h in danh_sach_hinh:
    print(h.tinh_dien_tich())
```

**Ví dụ thực tế: Hệ thống thanh toán đa hình**

```python
class PhuongThucThanhToan:
    def thanh_toan(self, so_tien):
        raise NotImplementedError("Phải override phương thức này!")


class ThanhToanTienMat(PhuongThucThanhToan):
    def thanh_toan(self, so_tien):
        print(f"💰 Thanh toán {so_tien:,}đ bằng tiền mặt")
        return True


class ThanhToanTheTinDung(PhuongThucThanhToan):
    def __init__(self, ma_the, cvv):
        self.ma_the = ma_the
        self.cvv = cvv

    def thanh_toan(self, so_tien):
        print(f"💳 Thanh toán {so_tien:,}đ bằng thẻ tín dụng {self.ma_the[-4:]}")
        return True


class ThanhToanQR(PhuongThucThanhToan):
    def thanh_toan(self, so_tien):
        print(f"📱 Quét QR thanh toán {so_tien:,}đ")
        return True


# Hàm xử lý thanh toán đa hình
def xu_ly_thanh_toan(phuong_thuc, so_tien):
    """Hàm này làm việc với BẤT Kỳ phương thức thanh toán nào"""
    if phuong_thuc.thanh_toan(so_tien):
        print("✅ Thanh toán thành công!")
    else:
        print("❌ Thanh toán thất bại!")


# Sử dụng
tt1 = ThanhToanTienMat()
tt2 = ThanhToanTheTinDung("1234-5678-9012-3456", "123")
tt3 = ThanhToanQR()

xu_ly_thanh_toan(tt1, 500000)
xu_ly_thanh_toan(tt2, 1000000)
xu_ly_thanh_toan(tt3, 200000)
```

---

### 1.4. Abstract Class (Lớp trừu tượng) - Khuôn mẫu bắt buộc

**Abstract Class = Không thể tạo object trực tiếp, chỉ để làm khuôn mẫu cho lớp con**

```python
from abc import ABC, abstractmethod


class Hinh(ABC):
    """Lớp trừu tượng - Không thể tạo object từ lớp này"""

    @abstractmethod
    def tinh_dien_tich(self):
        """Phương thức trừu tượng - Bắt buộc lớp con phải override"""
        pass

    @abstractmethod
    def tinh_chu_vi(self):
        pass

    def in_thong_tin(self):
        """Phương thức thông thường - có thể kế thừa trực tiếp"""
        print(f"Diện tích: {self.tinh_dien_tich()}")
        print(f"Chu vi: {self.tinh_chu_vi()}")


class HinhTron(Hinh):
    def __init__(self, ban_kinh):
        self.ban_kinh = ban_kinh

    def tinh_dien_tich(self):
        return 3.14 * self.ban_kinh**2

    def tinh_chu_vi(self):
        return 2 * 3.14 * self.ban_kinh


class HinhVuong(Hinh):
    def __init__(self, canh):
        self.canh = canh

    def tinh_dien_tich(self):
        return self.canh**2

    def tinh_chu_vi(self):
        return 4 * self.canh


# Không thể tạo Hinh()
# h = Hinh()  # TypeError: Can't instantiate abstract class Hinh

# Nhưng có thể tạo các lớp con
tron = HinhTron(5)
vuong = HinhVuong(4)

tron.in_thong_tien()
vuong.in_thong_tien()
```

**Khi nào dùng Abstract Class?**
1. Khi muốn **định nghĩa interface** chung cho các lớp con
2. Khi có **logic chung** nhưng cần **triển khai cụ thể** ở lớp con
3. Khi muốn **bắt buộc** các lớp con phải implement một số phương thức

---

### 1.5. Đa kế thừa (Multiple Inheritance) - MRO

**Đa kế thừa = Một lớp con kế thừa từ nhiều lớp cha**

```python
class Flyable:
    def fly(self):
        print("Đang bay...")

    def move(self):
        print("Bay trên trời")


class Swimmable:
    def swim(self):
        print("Đang bơi...")

    def move(self):
        print("Bơi dưới nước")


class Duck(Flyable, Swimmable):
    """Vịt vừa bay được vừa bơi được"""

    def __init__(self, name):
        self.name = name

    def move(self):
        # Chọn cách di chuyển dựa trên tình huống
        print(f"{self.name} đang đi bộ...")


# Sử dụng
v = Duck("Donald")
v.fly()  # Đang bay... (từ Flyable)
v.swim()  # Đang bơi... (từ Swimmable)
v.move()  # Donald đang đi bộ... (override ở Duck)

# MRO (Method Resolution Order) - Thứ tự tìm phương thức
print(Duck.__mro__)
# (<class '__main__.Duck'>, <class '__main__.Flyable'>,
#  <class '__main__.Swimmable'>, <class 'object'>)
```

**Diamond Problem và cách giải quyết:**

```python
class A:
    def action(self):
        print("A.action")


class B(A):
    def action(self):
        print("B.action")
        super().action()


class C(A):
    def action(self):
        print("C.action")
        super().action()


class D(B, C):
    def action(self):
        print("D.action")
        super().action()


# MRO của D: D → B → C → A
d = D()
d.action()
# D.action
# B.action
# C.action
# A.action

print(D.__mro__)  # (<class '__main__.D'>, <class '__main__.B'>,
#  <class '__main__.C'>, <class '__main__.A'>,
#  <class 'object'>)
```

---

### 1.6. Composition vs Inheritance

**Composition = Thay vì kế thừa, một lớp chứa đối tượng của lớp khác**

```python
# KẾ THỪA - "is-a" relationship
class Dog(Animal):
    pass


# Dog is an Animal (Dog là một loài động vật)


# COMPOSITION - "has-a" relationship
class Car:
    def __init__(self):
        self.engine = Engine()  # Car has an Engine (Xe có động cơ)
        self.wheels = [Wheel() for _ in range(4)]  # Car has 4 wheels


# Ví dụ thực tế:
class CPU:
    def process(self):
        return "Đang xử lý..."


class RAM:
    def load(self):
        return "Đang tải dữ liệu..."


class Computer:
    def __init__(self):
        self.cpu = CPU()  # Composition
        self.ram = RAM()  # Composition

    def start(self):
        print(self.ram.load())
        print(self.cpu.process())
        return "Máy tính đã khởi động!"


# Sử dụng
pc = Computer()
print(pc.start())
```

**Khi nào dùng gì?**
| Kế thừa (Inheritance) | Composition |
|-----------------------|-------------|
| Quan hệ "is-a" | Quan hệ "has-a" |
| Tái sử dụng code từ lớp cha | Tái sử dụng bằng cách kết hợp đối tượng |
| Code ít, dùng nhiều tính năng của cha | Code nhiều hơn, linh hoạt hơn |
| Ví dụ: `Dog extends Animal` | Ví dụ: `Car has Engine` |

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống quản lý nhân viên nâng cao

```python
from abc import ABC, abstractmethod
from datetime import datetime
import random


class NhanVien(ABC):
    """Lớp trừu tượng cho tất cả nhân viên"""

    def __init__(self, ma, ten, ngay_sinh, luong_co_ban):
        self.ma = ma
        self.ten = ten
        self.ngay_sinh = datetime.strptime(ngay_sinh, "%d/%m/%Y")
        self.luong_co_ban = luong_co_ban
        self._da_nghi = False

    @abstractmethod
    def tinh_luong(self):
        """Lớp con bắt buộc phải override"""
        pass

    def nghi_viec(self):
        self._da_nghi = True
        return f"Nhân viên {self.ten} đã nghỉ việc"

    @property
    def tuoi(self):
        today = datetime.now()
        return (
            today.year
            - self.ngay_sinh.year
            - ((today.month, today.day) < (self.ngay_sinh.month, self.ngay_sinh.day))
        )

    def __str__(self):
        status = "Đã nghỉ" if self._da_nghi else "Đang làm"
        return f"{self.ma}: {self.ten} ({self.tuoi} tuổi) - {status}"


class LapTrinhVien(NhanVien):
    def __init__(self, ma, ten, ngay_sinh, luong_co_ban, ngon_ngu, so_du_an=0):
        super().__init__(ma, ten, ngay_sinh, luong_co_ban)
        self.ngon_ngu = ngon_ngu
        self.so_du_an = so_du_an
        self.thuong_du_an = 1000000

    def hoan_thanh_du_an(self):
        self.so_du_an += 1

    def tinh_luong(self):
        return self.luong_co_ban + (self.so_du_an * self.thuong_du_an)

    def __str__(self):
        return f"{super().__str__()} - Dev {self.ngon_ngu} ({self.so_du_an} dự án)"


class KeToan(NhanVien):
    def __init__(self, ma, ten, ngay_sinh, luong_co_ban, so_ho_so=0):
        super().__init__(ma, ten, ngay_sinh, luong_co_ban)
        self.so_ho_so = so_ho_so
        self.thuong_ho_so = 500000

    def hoan_thanh_ho_so(self):
        self.so_ho_so += 1

    def tinh_luong(self):
        return self.luong_co_ban + (self.so_ho_so * self.thuong_ho_so)

    def __str__(self):
        return f"{super().__str__()} - Kế toán ({self.so_ho_so} hồ sơ)"


class QuanLy(NhanVien):
    def __init__(self, ma, ten, ngay_sinh, luong_co_ban, nhan_vien_quan_ly=None):
        super().__init__(ma, ten, ngay_sinh, luong_co_ban)
        self.nhan_vien_quan_ly = nhan_vien_quan_ly or []
        self.phi_quan_ly = 5000000

    def them_nhan_vien(self, nv):
        self.nhan_vien_quan_ly.append(nv)

    def tinh_luong(self):
        return (
            self.luong_co_ban
            + self.phi_quan_ly
            + (sum(nv.tinh_luong() for nv in self.nhan_vien_quan_ly) * 0.05)
        )

    def __str__(self):
        return (
            f"{super().__str__()} - Quản lý ({len(self.nhan_vien_quan_ly)} nhân viên)"
        )


# HÀM ĐA HÌNH - Bảng lương
def in_bang_luong(danh_sach_nv):
    """In bảng lương cho BẤT KỲ loại nhân viên nào"""
    print("=" * 60)
    print(f"{'Mã':<10} {'Tên':<20} {'Lương':>15} {'Loại':<15}")
    print("=" * 60)

    for nv in danh_sach_nv:
        luong = nv.tinh_luong()
        loai = nv.__class__.__name__
        print(f"{nv.ma:<10} {nv.ten[:20]:<20} {luong:>15,}đ {loai:<15}")

    print("=" * 60)
    tong_luong = sum(nv.tinh_luong() for nv in danh_sach_nv)
    print(f"{'TỔNG CỘNG':<30} {tong_luong:>30,}đ")


# Sử dụng
dev1 = LapTrinhVien("DEV001", "Nguyễn Văn Code", "15/03/1995", 15000000, "Python")
dev2 = LapTrinhVien("DEV002", "Trần Thị Bug", "20/07/1998", 12000000, "JavaScript")
ke_toan = KeToan("KT001", "Lê Văn Sổ", "10/11/1990", 10000000)
quan_ly = QuanLy("QL001", "Phạm Thị Leader", "05/09/1988", 20000000)

# Thêm nhân viên vào quản lý
quan_ly.them_nhan_vien(dev1)
quan_ly.them_nhan_vien(dev2)
quan_ly.them_nhan_vien(ke_toan)

# Hoàn thành công việc
dev1.hoan_thanh_du_an()
dev1.hoan_thanh_du_an()
dev2.hoan_thanh_du_an()
ke_toan.hoan_thanh_ho_so()

# In bảng lương
danh_sach = [dev1, dev2, ke_toan, quan_ly]
in_bang_luong(danh_sach)
```

---

### Ví dụ 2: Hệ thống đa phương tiện

```python
from abc import ABC, abstractmethod


class PhuongTien(ABC):
    """Lớp trừu tượng cho mọi phương tiện"""

    def __init__(self, ten, toc_do_toi_da):
        self.ten = ten
        self.toc_do_toi_da = toc_do_toi_da

    @abstractmethod
    def di_chuyen(self):
        pass

    @abstractmethod
    def dong_co(self):
        pass


class PhuongTienDuongBo(PhuongTien):
    def __init__(self, ten, toc_do_toi_da, so_banh):
        super().__init__(ten, toc_do_toi_da)
        self.so_banh = so_banh

    def dong_co(self):
        return "Động cơ đốt trong"


class PhuongTienDuongThuy(PhuongTien):
    def __init__(self, ten, toc_do_toi_da, so_chan_vi):
        super().__init__(ten, toc_do_toi_da)
        self.so_chan_vi = so_chan_vi

    def dong_co(self):
        return "Động cơ tàu thủy"


class PhuongTienBay(PhuongTien):
    def __init__(self, ten, toc_do_toi_da, so_dong_co):
        super().__init__(ten, toc_do_toi_da)
        self.so_dong_co = so_dong_co

    def dong_co(self):
        return "Động cơ phản lực"


# MIXIN - Thêm tính năng mà không cần kế thừa
class CoTheTroi:
    def troi(self):
        print(f"{self.ten} đang trôi nổi trên mặt nước")


class CoTheBay:
    def bay(self):
        print(f"{self.ten} đang bay với tốc độ {self.toc_do_toi_da} km/h")


class CoTheChay:
    def chay(self):
        print(f"{self.ten} đang chạy với tốc độ {self.toc_do_toi_da} km/h")


# Các lớp cụ thể kết hợp nhiều mixin
class XeHoi(PhuongTienDuongBo, CoTheChay):
    def di_chuyen(self):
        self.chay()
        print(f"Xe hơi {self.ten} di chuyển trên đường với {self.so_banh} bánh")


class Thuyen(PhuongTienDuongThuy, CoTheTroi):
    def di_chuyen(self):
        self.troi()
        print(f"Thuyền {self.ten} di chuyển dưới nước")


class MayBay(PhuongTienBay, CoTheBay):
    def di_chuyen(self):
        self.bay()
        print(f"Máy bay {self.ten} bay với {self.so_dong_co} động cơ")


class XeLai(PhuongTienDuongBo, CoTheChay, CoTheTroi):
    def di_chuyen(self):
        print(f"Xe lội nước {self.ten} - Vừa chạy vừa bơi!")


# Sử dụng
xe = XeHoi("Toyota", 180, 4)
thuyen = Thuyen("Sampan", 50, 1)
may_bay = MayBay("Boeing 747", 900, 4)
xe_lai = XeLai("Amphibious", 80, 6)


# HÀM ĐA HÌNH
def thuc_hien_di_chuyen(phuong_tien):
    """Làm việc với BẤT KỲ phương tiện nào có phương thức di_chuyen()"""
    print(f"\n{'=' * 40}")
    print(f"Phương tiện: {phuong_tien.ten}")
    phuong_tien.di_chuyen()
    print(f"Động cơ: {phuong_tien.dong_co()}")


# Chạy đa hình
thuc_hien_di_chuyen(xe)
thuc_hien_di_chuyen(thuyen)
thuc_hien_di_chuyen(may_bay)
thuc_hien_di_chuyen(xe_lai)
```

---

### Ví dụ 3: Hệ thống lọc dữ liệu (Strategy Pattern)

```python
from abc import ABC, abstractmethod


class ChienLuocLoc(ABC):
    """Abstract strategy"""

    @abstractmethod
    def loc_du_lieu(self, du_lieu):
        pass


class LocSoDuong(ChienLuocLoc):
    def loc_du_lieu(self, du_lieu):
        return [x for x in du_lieu if x > 0]


class LocSoAm(ChienLuocLoc):
    def loc_du_lieu(self, du_lieu):
        return [x for x in du_lieu if x < 0]


class LocSoChan(ChienLuocLoc):
    def loc_du_lieu(self, du_lieu):
        return [x for x in du_lieu if x % 2 == 0]


class LocSoLe(ChienLuocLoc):
    def loc_du_lieu(self, du_lieu):
        return [x for x in du_lieu if x % 2 != 0]


class LocTheoKhoang(ChienLuocLoc):
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def loc_du_lieu(self, du_lieu):
        return [x for x in du_lieu if self.min_val <= x <= self.max_val]


class BoLocDuLieu:
    """Context - Sử dụng Strategy Pattern"""

    def __init__(self, chien_luoc):
        self.chien_luoc = chien_luoc

    def thay_doi_chien_luoc(self, chien_luoc_moi):
        self.chien_luoc = chien_luoc_moi

    def loc(self, du_lieu):
        return self.chien_luoc.loc_du_lieu(du_lieu)


# Sử dụng - Đa hình với chiến lược
du_lieu = [-10, -5, 0, 5, 10, 15, 20, 25, 30]

loc = BoLocDuLieu(LocSoDuong())
print(f"Số dương: {loc.loc(du_lieu)}")

loc.thay_doi_chien_luoc(LocSoChan())
print(f"Số chẵn: {loc.loc(du_lieu)}")

loc.thay_doi_chien_luoc(LocTheoKhoang(5, 20))
print(f"Từ 5-20: {loc.loc(du_lieu)}")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Tạo lớp cha `DongVat` và các lớp con `Cho`, `Meo`, `Ga`. Mỗi lớp con override phương thức `keu()`.

**Bài 2:** Tạo lớp cha `HinhHoc` abstract với phương thức `tinh_dien_tich()` và `tinh_chu_vi()`. Tạo 3 lớp con `HinhTron`, `HinhChuNhat`, `HinhTamGiac`.

**Bài 3:** Tạo lớp cha `NhanVien` và 2 lớp con `NhanVienBanHang` (có doanh số, hoa hồng) và `NhanVienVanPhong` (có phụ cấp). Override phương thức `tinh_luong()`.

**Bài 4:** Tạo lớp `Person` và lớp `Student` kế thừa. `Student` có thêm thuộc tính `diem` và phương thức `xep_loai()`.

**Bài 5:** Tạo lớp `Xe` abstract và 3 lớp con `XeMay`, `OTo`, `XeTai`. Mỗi xe có phương thức `tinh_tien_bay()` (tính tiền cầu đường).

**Bài 6:** Tạo lớp `TaiKhoan` và 2 lớp con `TaiKhoanTietKiem` (có lãi suất) và `TaiKhoanThanhToan` (có phí duy trì).

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Xây dựng hệ thống quản lý sách trong thư viện:
- `Sach`: mã, tên, tác giả, năm XB
- `SachGiaoKhoa`: kế thừa từ Sach, thêm môn học, lớp
- `SachThamKhao`: kế thừa từ Sach, thêm lĩnh vực
- `Truyen`: kế thừa từ Sach, thêm thể loại, số chương
- Xây dựng `ThuVien` với các phương thức: thêm, xóa, tìm kiếm

**Bài 8:** Tạo hệ thống thanh toán với các phương thức: `ThanhToanTienMat`, `ThanhToanThe`, `ThanhToanQR`, `ThanhToanPaypal`. Sử dụng abstract class và đa hình.

**Bài 9:** Xây dựng game đơn giản với các lớp:
- `NhanVat`: abstract (tên, máu, sát thương)
- `NhanVatChien`: kế thừa, có chiêu đặc biệt
- `NhanVatPhapSu`: kế thừa, có phép thuật
- `QuaiVat`: có các loại khác nhau
- Hàm `tran_dau(nv1, nv2)` sử dụng đa hình

**Bài 10:** Xây dựng hệ thống quản lý học sinh với:
- Lớp cha `HocSinh`: (tên, tuổi, địa chỉ)
- Lớp con `HocSinhCap1`: có điểm các môn, xếp loại theo thang điểm 10
- Lớp con `HocSinhCap2`: có điểm các môn, xếp loại theo thang điểm 10 và kiểm tra học bạ
- Lớp con `HocSinhCap3`: có điểm các môn, xếp loại theo thang điểm 10 và có khối thi

---

## 🏗️ MINI-PROJECT: HỆ THỐNG QUẢN LÝ RẠP CHIẾU PHIM

```python
"""
Xây dựng hệ thống quản lý rạp chiếu phim với OOP đầy đủ:

1. NGƯỜI (Person) - Abstract class:
   - Họ tên, ngày sinh, CMND
   - Phương thức: __str__

2. KHÁCH HÀNG (Customer) - Kế thừa Person:
   - Thành viên (VIP/Thường)
   - Điểm tích lũy
   - Lịch sử mua vé
   - Phương thức: tinh_diem(), __str__

3. NHÂN VIÊN (Employee) - Kế thừa Person:
   - Mã nhân viên
   - Chức vụ
   - Lương
   - Phương thức: tinh_luong()

4. PHIM (Movie):
   - Tên phim, thể loại, thời lượng, đạo diễn
   - Danh sách diễn viên, ngày khởi chiếu

5. SUẤT CHIẾU (Showtime):
   - Phim, phòng chiếu
   - Thời gian bắt đầu, kết thúc
   - Giá vé, số ghế trống

6. VÉ (Ticket):
   - Mã vé, khách hàng, suất chiếu
   - Ghế ngồi, giá tiền
   - Trạng thái (Đã đặt/Đã thanh toán/Đã hủy)

7. PHÒNG CHIẾU (CinemaRoom):
   - Số phòng, sức chứa
   - Danh sách ghế (Matrix)

8. CHỨC NĂNG:
   - Xem lịch chiếu
   - Đặt vé (chọn ghế)
   - Hủy vé
   - Tính tiền (Vé: 100k, Giảm 10% cho VIP)
   - Thống kê doanh thu theo phim
   - Quản lý khách hàng thân thiết

Yêu cầu: Sử dụng:
- Abstract class
- Kế thừa
- Đa hình
- Composition
- Polymorphic functions
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE OOP NÂNG CAO

- [ ] Sử dụng `@abstractmethod` cho lớp cha khi cần
- [ ] `super()` được gọi đúng cách trong `__init__`
- [ ] Override phương thức cha đúng cách
- [ ] Sử dụng đa hình trong các hàm (không kiểm tra kiểu cụ thể)
- [ ] MRO được hiểu đúng khi dùng đa kế thừa
- [ ] Phân biệt được khi nào dùng Inheritance vs Composition
- [ ] Không tạo object từ abstract class
- [ ] Tên class và method nhất quán

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo hệ thống plugin với abstract class
class Plugin(ABC):
    @abstractmethod
    def run(self):
        pass


class PluginManager:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin):
        if isinstance(plugin, Plugin):
            self.plugins.append(plugin)

    def run_all(self):
        for plugin in self.plugins:
            plugin.run()


# Hãy tạo ít nhất 3 plugins khác nhau
# - Plugin in thời gian
# - Plugin tạo random số
# - Plugin gửi email
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Cú pháp | Ứng dụng |
|-----------|---------|----------|
| **Kế thừa** | `class Con(Cha):` | Tái sử dụng code |
| **super()** | `super().__init__()` | Gọi phương thức cha |
| **Override** | Viết lại phương thức cha | Thay đổi hành vi |
| **Abstract** | `class Cha(ABC):` | Bắt buộc triển khai |
| **@abstractmethod** | `@abstractmethod def method():` | Phương thức bắt buộc |
| **Đa hình** | Cùng tên, khác hành vi | Linh hoạt, mở rộng |
| **Mixin** | `class Con(Cha, Mixin):` | Thêm tính năng |
| **MRO** | `ClassName.__mro__` | Thứ tự tìm method |
| **Composition** | `self.obj = Object()` | Quan hệ "has-a" |

---

**Chúc mừng bạn đã hoàn thành Bài 7! OOP nâng cao là kỹ năng quan trọng để làm việc trong các dự án thực tế.** 💪

*Bài 8 sẽ dạy bạn về Decorator và Closure - bước tiếp theo để code Pythonic hơn!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀