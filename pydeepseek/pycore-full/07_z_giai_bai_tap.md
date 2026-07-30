Chào bạn! Bạn đã hoàn thành Bài 7 về Kế thừa và Đa hình - tuyệt vời! Bây giờ tôi sẽ cung cấp **đáp án chi tiết cho Bài 7** và chúng ta cùng nhau review để bạn hiểu sâu hơn.

---

# 📝 ĐÁP ÁN BÀI 7: KẾ THỪA & ĐA HÌNH

---

## 🎯 BÀI TẬP CƠ BẢN

### Bài 1: Động vật và tiếng kêu

```python
from abc import ABC, abstractmethod


class DongVat(ABC):
    """Lớp cha abstract cho tất cả động vật"""

    def __init__(self, ten, tuoi):
        self.ten = ten
        self.tuoi = tuoi

    @abstractmethod
    def keu(self):
        """Phương thức trừu tượng - bắt buộc override"""
        pass

    def an(self):
        print(f"{self.ten} đang ăn...")

    def ngu(self):
        print(f"{self.ten} đang ngủ...")


class Cho(DongVat):
    def keu(self):
        return f"{self.ten} sủa: Gâu gâu!"

    def an(self):
        # Override thêm
        print(f"{self.ten} đang ăn xương...")


class Meo(DongVat):
    def keu(self):
        return f"{self.ten} kêu: Meo meo!"

    def an(self):
        print(f"{self.ten} đang ăn cá...")


class Ga(DongVat):
    def keu(self):
        return f"{self.ten} gáy: Ò ó o!"

    def an(self):
        print(f"{self.ten} đang ăn thóc...")


# Sử dụng và kiểm tra
cho = Cho("Mực", 3)
meo = Meo("Mimi", 2)
ga = Ga("Gà con", 1)

# Đa hình - gọi cùng phương thức keu() cho mọi loài
dong_vat = [cho, meo, ga]
for dv in dong_vat:
    print(dv.keu())
    dv.an()
    print("-" * 30)
```

---

### Bài 2: Hình học với abstract class

```python
from abc import ABC, abstractmethod
import math


class HinhHoc(ABC):
    """Lớp trừu tượng cho mọi hình học"""

    @abstractmethod
    def tinh_dien_tich(self):
        pass

    @abstractmethod
    def tinh_chu_vi(self):
        pass

    def in_thong_tin(self):
        """Phương thức dùng chung"""
        return (
            f"Diện tích: {self.tinh_dien_tich():.2f}, Chu vi: {self.tinh_chu_vi():.2f}"
        )


class HinhTron(HinhHoc):
    def __init__(self, ban_kinh):
        self.ban_kinh = ban_kinh

    def tinh_dien_tich(self):
        return math.pi * self.ban_kinh**2

    def tinh_chu_vi(self):
        return 2 * math.pi * self.ban_kinh

    def __str__(self):
        return f"Hình tròn bán kính {self.ban_kinh}"


class HinhChuNhat(HinhHoc):
    def __init__(self, dai, rong):
        self.dai = dai
        self.rong = rong

    def tinh_dien_tich(self):
        return self.dai * self.rong

    def tinh_chu_vi(self):
        return 2 * (self.dai + self.rong)

    def __str__(self):
        return f"Hình chữ nhật {self.dai}x{self.rong}"


class HinhTamGiac(HinhHoc):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def tinh_dien_tich(self):
        # Công thức Heron
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def tinh_chu_vi(self):
        return self.a + self.b + self.c

    def __str__(self):
        return f"Hình tam giác ({self.a}, {self.b}, {self.c})"


# Sử dụng
hinh = [HinhTron(5), HinhChuNhat(4, 6), HinhTamGiac(3, 4, 5)]

print("=== BẢNG TÍNH HÌNH HỌC ===")
for h in hinh:
    print(f"{h}: {h.in_thong_tin()}")
    print("-" * 40)
```

---

### Bài 3: Nhân viên và lương

```python
from abc import ABC, abstractmethod


class NhanVien(ABC):
    def __init__(self, ma, ten, luong_co_ban):
        self.ma = ma
        self.ten = ten
        self.luong_co_ban = luong_co_ban

    @abstractmethod
    def tinh_luong(self):
        pass

    def __str__(self):
        return f"{self.ma}: {self.ten} - {self.tinh_luong():,.0f}đ"


class NhanVienBanHang(NhanVien):
    def __init__(self, ma, ten, luong_co_ban, doanh_so, hoa_hong=0.1):
        super().__init__(ma, ten, luong_co_ban)
        self.doanh_so = doanh_so
        self.hoa_hong = hoa_hong

    def tinh_luong(self):
        return self.luong_co_ban + (self.doanh_so * self.hoa_hong)

    def __str__(self):
        return f"{super().__str__()} (Doanh số: {self.doanh_so:,}đ, Hoa hồng: {self.hoa_hong * 100}%)"


class NhanVienVanPhong(NhanVien):
    def __init__(self, ma, ten, luong_co_ban, phu_cap):
        super().__init__(ma, ten, luong_co_ban)
        self.phu_cap = phu_cap

    def tinh_luong(self):
        return self.luong_co_ban + self.phu_cap

    def __str__(self):
        return f"{super().__str__()} (Phụ cấp: {self.phu_cap:,}đ)"


class NhanVienQuanLy(NhanVien):
    def __init__(self, ma, ten, luong_co_ban, nhan_vien_quan_ly=None):
        super().__init__(ma, ten, luong_co_ban)
        self.nhan_vien_quan_ly = nhan_vien_quan_ly or []
        self.thuong_quan_ly = 5000000

    def them_nhan_vien(self, nv):
        self.nhan_vien_quan_ly.append(nv)

    def tinh_luong(self):
        return self.luong_co_ban + self.thuong_quan_ly

    def __str__(self):
        return f"{super().__str__()} (Quản lý {len(self.nhan_vien_quan_ly)} nhân viên)"


# Sử dụng
nv1 = NhanVienBanHang("NV01", "Trần Văn Bán", 8000000, 100000000)
nv2 = NhanVienVanPhong("NV02", "Lê Thị Văn", 9000000, 2000000)
ql = NhanVienQuanLy("QL01", "Phạm Văn Lãnh", 15000000)
ql.them_nhan_vien(nv1)
ql.them_nhan_vien(nv2)

# Đa hình - tính lương
nhan_vien = [nv1, nv2, ql]
print("=== BẢNG LƯƠNG NHÂN VIÊN ===")
for nv in nhan_vien:
    print(nv)
print(f"Tổng quỹ lương: {sum(nv.tinh_luong() for nv in nhan_vien):,.0f}đ")
```

---

### Bài 4: Person và Student

```python
class Person:
    def __init__(self, ho_ten, tuoi, dia_chi):
        self.ho_ten = ho_ten
        self.tuoi = tuoi
        self.dia_chi = dia_chi

    def __str__(self):
        return f"{self.ho_ten}, {self.tuoi} tuổi, {self.dia_chi}"


class Student(Person):
    def __init__(self, ho_ten, tuoi, dia_chi, ma_sv, diem=None):
        super().__init__(ho_ten, tuoi, dia_chi)
        self.ma_sv = ma_sv
        self.diem = diem or []

    def them_diem(self, diem):
        """Thêm điểm vào danh sách"""
        if not (0 <= diem <= 10):
            raise ValueError("Điểm phải từ 0-10")
        self.diem.append(diem)

    def tinh_trung_binh(self):
        """Tính điểm trung bình"""
        if not self.diem:
            return 0
        return sum(self.diem) / len(self.diem)

    def xep_loai(self):
        """Xếp loại học lực"""
        tb = self.tinh_trung_binh()
        if tb >= 9.0:
            return "Xuất sắc"
        elif tb >= 8.0:
            return "Giỏi"
        elif tb >= 6.5:
            return "Khá"
        elif tb >= 5.0:
            return "Trung bình"
        else:
            return "Yếu"

    def __str__(self):
        return f"{super().__str__()} - SV: {self.ma_sv} - TB: {self.tinh_trung_binh():.2f} - {self.xep_loai()}"


# Sử dụng
sv = Student("Nguyễn Văn A", 20, "Hà Nội", "SV001")
sv.them_diem(8.5)
sv.them_diem(9.0)
sv.them_diem(7.5)

print(sv)
```

---

### Bài 5: Xe và tính tiền cầu đường

```python
from abc import ABC, abstractmethod


class Xe(ABC):
    def __init__(self, bien_so, trong_tai):
        self.bien_so = bien_so
        self.trong_tai = trong_tai

    @abstractmethod
    def tinh_tien_cau_duong(self):
        """Tính tiền cầu đường"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.bien_so} ({self.trong_tai} tấn)"


class XeMay(Xe):
    def __init__(self, bien_so, trong_tai, dung_tich):
        super().__init__(bien_so, trong_tai)
        self.dung_tich = dung_tich

    def tinh_tien_cau_duong(self):
        # Xe máy giá cố định
        return 5000

    def __str__(self):
        return f"{super().__str__()} - {self.dung_tich}cc"


class OTo(Xe):
    def __init__(self, bien_so, trong_tai, so_cho):
        super().__init__(bien_so, trong_tai)
        self.so_cho = so_cho

    def tinh_tien_cau_duong(self):
        # Ô tô: 20,000 + 10,000 mỗi tấn
        return 20000 + (self.trong_tai * 10000)

    def __str__(self):
        return f"{super().__str__()} - {self.so_cho} chỗ"


class XeTai(Xe):
    def __init__(self, bien_so, trong_tai, hang_hoa):
        super().__init__(bien_so, trong_tai)
        self.hang_hoa = hang_hoa

    def tinh_tien_cau_duong(self):
        # Xe tải: 30,000 + 15,000 mỗi tấn
        return 30000 + (self.trong_tai * 15000)

    def __str__(self):
        return f"{super().__str__()} - {self.hang_hoa}"


# Sử dụng
xe = [
    XeMay("29A1-123.45", 0.15, 150),
    OTo("30B-789.01", 2.5, 5),
    XeTai("51C-456.78", 8.0, "Hàng hóa"),
]

print("=== PHÍ CẦU ĐƯỜNG ===")
for x in xe:
    print(f"{x}: {x.tinh_tien_cau_duong():,}đ")
```

---

### Bài 6: Tài khoản ngân hàng

```python
from abc import ABC, abstractmethod
from datetime import datetime


class TaiKhoan(ABC):
    def __init__(self, so_tk, chu_tk, so_du=0):
        self.so_tk = so_tk
        self.chu_tk = chu_tk
        self._so_du = so_du
        self.lich_su = []
        self.ngay_tao = datetime.now()

    @property
    def so_du(self):
        return self._so_du

    def nap_tien(self, so_tien, mo_ta=""):
        """Nạp tiền vào tài khoản"""
        if so_tien <= 0:
            raise ValueError("Số tiền phải > 0")
        self._so_du += so_tien
        self._ghi_lich_su("NẠP", so_tien, mo_ta)
        return f"Nạp thành công {so_tien:,}đ"

    def rut_tien(self, so_tien, mo_ta=""):
        """Rút tiền từ tài khoản"""
        if so_tien <= 0:
            raise ValueError("Số tiền phải > 0")
        if so_tien > self._so_du:
            raise ValueError("Số dư không đủ!")
        self._so_du -= so_tien
        self._ghi_lich_su("RÚT", -so_tien, mo_ta)
        return f"Rút thành công {so_tien:,}đ"

    def _ghi_lich_su(self, loai, so_tien, mo_ta):
        """Ghi lịch sử giao dịch"""
        self.lich_su.append(
            {
                "thoi_gian": datetime.now(),
                "loai": loai,
                "so_tien": so_tien,
                "so_du": self._so_du,
                "mo_ta": mo_ta,
            }
        )

    @abstractmethod
    def tinh_phi_giao_dich(self, so_tien):
        """Tính phí giao dịch"""
        pass

    def in_sao_ke(self):
        """In sao kê tài khoản"""
        print(f"\n=== SAO KÊ TÀI KHOẢN {self.so_tk} ===")
        print(f"Chủ tài khoản: {self.chu_tk}")
        print(f"Số dư: {self.so_du:,}đ")
        print("-" * 40)
        for gd in self.lich_su[-10:]:  # 10 giao dịch gần nhất
            print(
                f"{gd['thoi_gian'].strftime('%H:%M %d/%m')} | {gd['loai']:4s} | "
                f"{gd['so_tien']:>10,}đ | Số dư: {gd['so_du']:>10,}đ | {gd['mo_ta']}"
            )

    def __str__(self):
        return f"{self.so_tk}: {self.chu_tk} - {self.so_du:,}đ"


class TaiKhoanTietKiem(TaiKhoan):
    def __init__(self, so_tk, chu_tk, so_du=0, lai_suat=0.05):
        super().__init__(so_tk, chu_tk, so_du)
        self.lai_suat = lai_suat
        self.ngay_tinh_lai = datetime.now()

    def tinh_phi_giao_dich(self, so_tien):
        """Tài khoản tiết kiệm: không phí giao dịch, chỉ tính lãi"""
        return 0

    def tinh_lai(self):
        """Tính lãi suất hàng tháng"""
        self._so_du *= 1 + self.lai_suat / 12
        self._ghi_lich_su("LÃI", self._so_du * self.lai_suat / 12, "Lãi suất")

    def __str__(self):
        return f"{super().__str__()} (Lãi suất: {self.lai_suat * 100}%)"


class TaiKhoanThanhToan(TaiKhoan):
    def __init__(self, so_tk, chu_tk, so_du=0, phi_duy_tri=10000):
        super().__init__(so_tk, chu_tk, so_du)
        self.phi_duy_tri = phi_duy_tri

    def tinh_phi_giao_dich(self, so_tien):
        """Tính phí giao dịch: 0.1% số tiền"""
        return so_tien * 0.001

    def rut_tien(self, so_tien, mo_ta=""):
        """Override: rút tiền có tính phí giao dịch"""
        phi = self.tinh_phi_giao_dich(so_tien)
        tong_rut = so_tien + phi
        if tong_rut > self._so_du:
            raise ValueError(
                f"Số dư không đủ! Cần: {tong_rut:,}đ (bao gồm phí {phi:,}đ)"
            )
        self._so_du -= tong_rut
        self._ghi_lich_su("RÚT", -tong_rut, f"{mo_ta} (phí: {phi:,}đ)")
        return f"Rút {so_tien:,}đ, phí {phi:,}đ"

    def __str__(self):
        return f"{super().__str__()} (Phí duy trì: {self.phi_duy_tri:,}đ/tháng)"


# Sử dụng
tk1 = TaiKhoanTietKiem("TK001", "Nguyễn Văn A", 10000000)
tk2 = TaiKhoanThanhToan("TK002", "Trần Thị B", 5000000)

tk1.nap_tien(2000000, "Chuyển khoản")
tk1.rut_tien(500000, "Rút ATM")

tk2.nap_tien(3000000, "Nhận lương")
tk2.rut_tien(1000000, "Mua sắm")

print(tk1)
print(tk2)
tk1.in_sao_ke()
tk2.in_sao_ke()
```

---

## ⭐ BÀI TẬP NÂNG CAO

### Bài 7: Hệ thống quản lý sách

```python
from abc import ABC
from datetime import datetime


class Sach(ABC):
    """Lớp cơ sở cho mọi loại sách"""

    def __init__(self, ma, ten, tac_gia, nam_xuat_ban):
        self.ma = ma
        self.ten = ten
        self.tac_gia = tac_gia
        self.nam_xuat_ban = nam_xuat_ban
        self.trang_thai = "Có sẵn"

    def muon_sach(self):
        if self.trang_thai == "Đã mượn":
            raise ValueError(f"Sách {self.ma} đã được mượn!")
        self.trang_thai = "Đã mượn"

    def tra_sach(self):
        if self.trang_thai == "Có sẵn":
            raise ValueError(f"Sách {self.ma} đã có sẵn!")
        self.trang_thai = "Có sẵn"

    def __str__(self):
        return f"{self.ma}: {self.ten} - {self.tac_gia} ({self.nam_xuat_ban}) - {self.trang_thai}"


class SachGiaoKhoa(Sach):
    def __init__(self, ma, ten, tac_gia, nam_xuat_ban, mon_hoc, lop):
        super().__init__(ma, ten, tac_gia, nam_xuat_ban)
        self.mon_hoc = mon_hoc
        self.lop = lop

    def __str__(self):
        return f"{super().__str__()} - SGK {self.mon_hoc} lớp {self.lop}"


class SachThamKhao(Sach):
    def __init__(self, ma, ten, tac_gia, nam_xuat_ban, linh_vuc):
        super().__init__(ma, ten, tac_gia, nam_xuat_ban)
        self.linh_vuc = linh_vuc

    def __str__(self):
        return f"{super().__str__()} - Tham khảo {self.linh_vuc}"


class Truyen(Sach):
    def __init__(self, ma, ten, tac_gia, nam_xuat_ban, the_loai, so_chuong):
        super().__init__(ma, ten, tac_gia, nam_xuat_ban)
        self.the_loai = the_loai
        self.so_chuong = so_chuong

    def __str__(self):
        return f"{super().__str__()} - Truyện {self.the_loai} ({self.so_chuong} chương)"


class ThuVien:
    def __init__(self, ten, dia_chi):
        self.ten = ten
        self.dia_chi = dia_chi
        self.danh_sach_sach = []

    def them_sach(self, sach):
        if not isinstance(sach, Sach):
            raise TypeError("Phải là đối tượng Sach")
        # Kiểm tra trùng mã
        for s in self.danh_sach_sach:
            if s.ma == sach.ma:
                raise ValueError(f"Đã tồn tại sách mã {sach.ma}")
        self.danh_sach_sach.append(sach)
        return f"Đã thêm: {sach.ten}"

    def xoa_sach(self, ma_sach):
        for i, s in enumerate(self.danh_sach_sach):
            if s.ma == ma_sach:
                if s.trang_thai == "Đã mượn":
                    raise ValueError(f"Sách {ma_sach} đang được mượn, không thể xóa!")
                del self.danh_sach_sach[i]
                return f"Đã xóa sách {ma_sach}"
        raise ValueError(f"Không tìm thấy sách {ma_sach}")

    def tim_kiem(self, tu_khoa):
        """Tìm kiếm theo tên hoặc tác giả"""
        ket_qua = []
        tu_khoa = tu_khoa.lower()
        for s in self.danh_sach_sach:
            if tu_khoa in s.ten.lower() or tu_khoa in s.tac_gia.lower():
                ket_qua.append(s)
        return ket_qua

    def muon_sach(self, ma_sach):
        for s in self.danh_sach_sach:
            if s.ma == ma_sach:
                s.muon_sach()
                return f"Đã mượn: {s.ten}"
        raise ValueError(f"Không tìm thấy sách {ma_sach}")

    def tra_sach(self, ma_sach):
        for s in self.danh_sach_sach:
            if s.ma == ma_sach:
                s.tra_sach()
                return f"Đã trả: {s.ten}"
        raise ValueError(f"Không tìm thấy sách {ma_sach}")

    def thong_ke(self):
        """Thống kê sách trong thư viện"""
        print(f"\n=== THỐNG KÊ THƯ VIỆN {self.ten} ===")
        print(f"Tổng số sách: {len(self.danh_sach_sach)}")

        # Đếm theo loại
        loai_sach = {}
        for s in self.danh_sach_sach:
            loai = s.__class__.__name__
            loai_sach[loai] = loai_sach.get(loai, 0) + 1

        print("\nPhân loại:")
        for loai, so_luong in loai_sach.items():
            print(f"  - {loai}: {so_luong} cuốn")

        # Đếm theo trạng thái
        dang_muon = sum(1 for s in self.danh_sach_sach if s.trang_thai == "Đã mượn")
        print(f"\nĐang mượn: {dang_muon} cuốn")
        print(f"Có sẵn: {len(self.danh_sach_sach) - dang_muon} cuốn")

    def hien_thi_tat_ca(self):
        """Hiển thị tất cả sách"""
        print(f"\n=== DANH SÁCH SÁCH ({self.ten}) ===")
        for s in self.danh_sach_sach:
            print(s)


# Sử dụng
thu_vien = ThuVien("Thư viện Trung tâm", "Số 1, Đường A, Hà Nội")

# Thêm sách
sgk1 = SachGiaoKhoa("SGK001", "Toán 10", "Nguyễn Văn A", 2023, "Toán", 10)
sgk2 = SachGiaoKhoa("SGK002", "Văn 10", "Trần Thị B", 2023, "Văn", 10)
stk1 = SachThamKhao("STK001", "Chuyên đề Hóa", "Lê Văn C", 2022, "Hóa học")
truyen1 = Truyen("TR001", "Dế Mèn phiêu lưu ký", "Tô Hoài", 1941, "Thiếu nhi", 10)

thu_vien.them_sach(sgk1)
thu_vien.them_sach(sgk2)
thu_vien.them_sach(stk1)
thu_vien.them_sach(truyen1)

# Tìm kiếm
print("\nKết quả tìm kiếm 'toán':")
for s in thu_vien.tim_kiem("toán"):
    print(f"  - {s}")

# Mượn/trả sách
print("\n" + thu_vien.muon_sach("SGK001"))
print(thu_vien.muon_sach("STK001"))
print(thu_vien.tra_sach("SGK001"))

# Thống kê
thu_vien.thong_ke()
thu_vien.hien_thi_tat_ca()
```

---

### Bài 8: Hệ thống thanh toán đa hình

```python
from abc import ABC, abstractmethod
import random
import time


class PhuongThucThanhToan(ABC):
    """Abstract class cho mọi phương thức thanh toán"""

    def __init__(self):
        self.ma_giao_dich = None
        self.thoi_gian = None

    @abstractmethod
    def thanh_toan(self, so_tien):
        """Thực hiện thanh toán"""
        pass

    @abstractmethod
    def hoan_tien(self, so_tien):
        """Hoàn tiền"""
        pass

    def sinh_ma_giao_dich(self):
        """Sinh mã giao dịch ngẫu nhiên"""
        return f"TXN{random.randint(10000, 99999)}"


class ThanhToanTienMat(PhuongThucThanhToan):
    def thanh_toan(self, so_tien):
        self.ma_giao_dich = self.sinh_ma_giao_dich()
        self.thoi_gian = time.strftime("%H:%M:%S")
        print(f"💰 THANH TOÁN TIỀN MẶT")
        print(f"   Số tiền: {so_tien:,}đ")
        print(f"   Mã GD: {self.ma_giao_dich}")
        print(f"   Thời gian: {self.thoi_gian}")
        return True

    def hoan_tien(self, so_tien):
        print(f"💰 HOÀN TIỀN MẶT: {so_tien:,}đ")
        return True


class ThanhToanThe(PhuongThucThanhToan):
    def __init__(self, so_the, ten_chu_the, cvv, ngay_het_han):
        super().__init__()
        self.so_the = so_the
        self.ten_chu_the = ten_chu_the
        self.cvv = cvv
        self.ngay_het_han = ngay_het_han

    def thanh_toan(self, so_tien):
        # Giả lập xác thực
        if self.cvv == "123":  # Mô phỏng lỗi
            raise ValueError("Thẻ không hợp lệ!")

        self.ma_giao_dich = self.sinh_ma_giao_dich()
        self.thoi_gian = time.strftime("%H:%M:%S")
        print(f"💳 THANH TOÁN THẺ TÍN DỤNG")
        print(f"   Thẻ: {self.so_the[-4:]}")
        print(f"   Chủ thẻ: {self.ten_chu_the}")
        print(f"   Số tiền: {so_tien:,}đ")
        print(f"   Mã GD: {self.ma_giao_dich}")
        print(f"   Thời gian: {self.thoi_gian}")
        return True

    def hoan_tien(self, so_tien):
        print(f"💳 HOÀN TIỀN VÀO THẺ: {so_tien:,}đ")
        return True


class ThanhToanQR(PhuongThucThanhToan):
    def __init__(self, ten_ngan_hang="Vietcombank"):
        super().__init__()
        self.ten_ngan_hang = ten_ngan_hang

    def thanh_toan(self, so_tien):
        # Giả lập quét QR
        ma_qr = f"QR{random.randint(1000, 9999)}"
        self.ma_giao_dich = self.sinh_ma_giao_dich()
        self.thoi_gian = time.strftime("%H:%M:%S")
        print(f"📱 THANH TOÁN QR")
        print(f"   Ngân hàng: {self.ten_ngan_hang}")
        print(f"   Mã QR: {ma_qr}")
        print(f"   Số tiền: {so_tien:,}đ")
        print(f"   Mã GD: {self.ma_giao_dich}")
        print(f"   Thời gian: {self.thoi_gian}")
        print("   📸 Đã quét mã QR thành công!")
        return True

    def hoan_tien(self, so_tien):
        print(f"📱 HOÀN TIỀN QR: {so_tien:,}đ")
        return True


class ThanhToanPaypal(PhuongThucThanhToan):
    def __init__(self, email, mat_khau):
        super().__init__()
        self.email = email
        self.mat_khau = mat_khau

    def thanh_toan(self, so_tien):
        # Giả lập đăng nhập PayPal
        if not "@" in self.email:
            raise ValueError("Email PayPal không hợp lệ!")

        self.ma_giao_dich = self.sinh_ma_giao_dich()
        self.thoi_gian = time.strftime("%H:%M:%S")
        print(f"🌐 THANH TOÁN PAYPAL")
        print(f"   Email: {self.email}")
        print(f"   Số tiền: {so_tien:,}đ")
        print(f"   Mã GD: {self.ma_giao_dich}")
        print(f"   Thời gian: {self.thoi_gian}")
        print("   ✅ Đã xác thực PayPal")
        return True

    def hoan_tien(self, so_tien):
        print(f"🌐 HOÀN TIỀN PAYPAL: {so_tien:,}đ")
        return True


# HÀM ĐA HÌNH - Xử lý thanh toán
def xu_ly_thanh_toan(phuong_thuc, so_tien, hoan=False):
    """Xử lý thanh toán với bất kỳ phương thức nào"""
    try:
        if hoan:
            print("\n" + "=" * 50)
            phuong_thuc.hoan_tien(so_tien)
        else:
            print("\n" + "=" * 50)
            print(f"🔔 XỬ LÝ THANH TOÁN")
            phuong_thuc.thanh_toan(so_tien)
            print("   ✅ GIAO DỊCH THÀNH CÔNG!")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False


# Sử dụng
tt1 = ThanhToanTienMat()
tt2 = ThanhToanThe("1234-5678-9012-3456", "NGUYEN VAN A", "123", "12/25")
tt3 = ThanhToanThe("9876-5432-1098-7654", "TRAN THI B", "456", "06/26")
tt4 = ThanhToanQR()
tt5 = ThanhToanPaypal("user@email.com", "password123")

# Thực hiện các giao dịch
phuong_thuc = [tt1, tt3, tt4, tt5]
for p in phuong_thuc:
    xu_ly_thanh_toan(p, random.randint(100000, 1000000))
    time.sleep(1)

# Hoàn tiền
xu_ly_thanh_toan(tt1, 200000, hoan=True)
```

---

### Bài 9: Game đơn giản với nhân vật

```python
from abc import ABC, abstractmethod
import random
import time


class NhanVat(ABC):
    """Lớp trừu tượng cho mọi nhân vật"""

    def __init__(self, ten, mau, sat_thuong, chinh_xac=0.8):
        self.ten = ten
        self.mau_toi_da = mau
        self.mau = mau
        self.sat_thuong = sat_thuong
        self.chinh_xac = chinh_xac
        self.da_chet = False

    @abstractmethod
    def tan_cong(self, dich):
        """Tấn công kẻ địch"""
        pass

    @abstractmethod
    def chieu_dac_biet(self, dich):
        """Chiêu đặc biệt"""
        pass

    def nhan_sat_thuong(self, so_sat_thuong):
        """Nhận sát thương từ đòn tấn công"""
        self.mau -= so_sat_thuong
        if self.mau <= 0:
            self.mau = 0
            self.da_chet = True

    def hoi_mau(self, so_mau):
        """Hồi máu"""
        self.mau = min(self.mau + so_mau, self.mau_toi_da)

    def con_so_du(self):
        return self.mau > 0

    def __str__(self):
        return f"{self.ten}: HP {self.mau}/{self.mau_toi_da}"


class NhanVatChien(NhanVat):
    """Nhân vật chiến binh - Sát thương cận chiến"""

    def __init__(self, ten, mau=100, sat_thuong=15):
        super().__init__(ten, mau, sat_thuong, chinh_xac=0.75)
        self.sat_thuong_dac_biet = 30
        self.chieu_dem = 0

    def tan_cong(self, dich):
        """Tấn công thường"""
        if random.random() > self.chinh_xac:
            return f"{self.ten} tấn công trượt!"

        sat_thuong = self.sat_thuong + random.randint(-5, 5)
        dich.nhan_sat_thuong(sat_thuong)
        self.chieu_dem += 1
        return f"{self.ten} chém {dich.ten} gây {sat_thuong} sát thương!"

    def chieu_dac_biet(self, dich):
        """Chiêu đặc biệt: Bão kiếm"""
        if self.chieu_dem < 3:
            return f"{self.ten} chưa đủ năng lượng! (Cần 3 đòn)"

        # Bão kiếm gây sát thương lớn
        sat_thuong = self.sat_thuong_dac_biet + random.randint(-10, 10)
        dich.nhan_sat_thuong(sat_thuong)
        self.chieu_dem = 0
        return f"⚔️ {self.ten} tung BÃO KIẾM gây {sat_thuong} sát thương!"


class NhanVatPhapSu(NhanVat):
    """Nhân vật pháp sư - Tấn công từ xa"""

    def __init__(self, ten, mau=80, sat_thuong=20):
        super().__init__(ten, mau, sat_thuong, chinh_xac=0.9)
        self.nang_luong = 0
        self.sat_thuong_dac_biet = 40

    def tan_cong(self, dich):
        """Phép thuật cơ bản"""
        if random.random() > self.chinh_xac:
            return f"{self.ten} niệm chú trượt!"

        sat_thuong = self.sat_thuong + random.randint(-8, 8)
        dich.nhan_sat_thuong(sat_thuong)
        self.nang_luong += 1
        return f"🌀 {self.ten} phóng phép cầu lửa gây {sat_thuong} sát thương!"

    def chieu_dac_biet(self, dich):
        """Chiêu đặc biệt: Mưa sao băng"""
        if self.nang_luong < 4:
            return f"{self.ten} chưa đủ ma lực! (Cần 4 phép)"

        # Mưa sao băng nhiều đòn
        tong_sat_thuong = 0
        for i in range(3):
            sat_thuong = self.sat_thuong_dac_biet + random.randint(-5, 15)
            dich.nhan_sat_thuong(sat_thuong)
            tong_sat_thuong += sat_thuong

        self.nang_luong = 0
        return f"🌠 {self.ten} niệm MƯA SAO BĂNG gây {tong_sat_thuong} sát thương!"


class NhanVatCungThu(NhanVat):
    """Nhân vật cung thủ - Tầm xa, chính xác cao"""

    def __init__(self, ten, mau=90, sat_thuong=12):
        super().__init__(ten, mau, sat_thuong, chinh_xac=0.85)
        self.mui_ten = 0
        self.sat_thuong_dac_biet = 25

    def tan_cong(self, dich):
        """Bắn tên thường"""
        if random.random() > self.chinh_xac:
            return f"{self.ten} bắn trượt mục tiêu!"

        sat_thuong = self.sat_thuong + random.randint(-3, 5)
        dich.nhan_sat_thuong(sat_thuong)
        self.mui_ten += 1
        return f"🏹 {self.ten} bắn một mũi tên gây {sat_thuong} sát thương!"

    def chieu_dac_biet(self, dich):
        """Chiêu đặc biệt: Mưa tên"""
        if self.mui_ten < 5:
            return f"{self.ten} cần 5 mũi tên để tung chiêu!"

        # Mưa tên gây sát thương diện rộng
        sat_thuong = self.sat_thuong_dac_biet + random.randint(-5, 15)
        dich.nhan_sat_thuong(sat_thuong)
        self.mui_ten = 0
        return f"🌧️ {self.ten} bắn MƯA TÊN gây {sat_thuong} sát thương!"


class QuaiVat:
    """Quái vật - Kẻ thù trong game"""

    def __init__(self, ten, mau, sat_thuong, loai="Thường"):
        self.ten = ten
        self.mau_toi_da = mau
        self.mau = mau
        self.sat_thuong = sat_thuong
        self.loai = loai
        self.da_chet = False

    def tan_cong(self, dich):
        """Quái vật tấn công"""
        sat_thuong = self.sat_thuong + random.randint(-5, 5)
        dich.nhan_sat_thuong(max(1, sat_thuong))
        return f"👹 {self.ten} tấn công {dich.ten} gây {sat_thuong} sát thương!"

    def nhan_sat_thuong(self, so_sat_thuong):
        self.mau -= so_sat_thuong
        if self.mau <= 0:
            self.mau = 0
            self.da_chet = True

    def con_so_du(self):
        return self.mau > 0

    def __str__(self):
        return f"{self.ten}: HP {self.mau}/{self.mau_toi_da}"


# HÀM ĐA HÌNH - Trận đấu
def tran_dau(nhan_vat, quai_vat):
    """Hàm xử lý trận đấu giữa nhân vật và quái vật"""
    print("\n" + "=" * 50)
    print(f"⚔️ TRẬN CHIẾN: {nhan_vat.ten} VS {quai_vat.ten}")
    print("=" * 50)

    luot = 0
    while nhan_vat.con_so_du() and quai_vat.con_so_du():
        luot += 1
        print(f"\n【Lượt {luot}】")

        # Nhân vật tấn công
        print(f"\n🎯 {nhan_vat.ten}:")
        hanh_dong = random.choice(["tấn công", "chiêu đặc biệt"])

        if hanh_dong == "chiêu đặc biệt":
            print(nhan_vat.chieu_dac_biet(quai_vat))
        else:
            print(nhan_vat.tan_cong(quai_vat))

        if not quai_vat.con_so_du():
            print(f"\n🎉 {quai_vat.ten} đã bị đánh bại!")
            break

        # Quái vật tấn công
        print(f"\n👹 {quai_vat.ten}:")
        print(quai_vat.tan_cong(nhan_vat))

        if not nhan_vat.con_so_du():
            print(f"\n💀 {nhan_vat.ten} đã bị đánh bại!")
            break

        # Hiển thị trạng thái
        print(f"\n📊 Trạng thái:")
        print(f"   {nhan_vat}")
        print(f"   {quai_vat}")

        time.sleep(1.5)

    print("\n" + "=" * 50)
    if nhan_vat.con_so_du():
        print(f"🏆 {nhan_vat.ten} chiến thắng!")
        return nhan_vat
    else:
        print(f"💀 {quai_vat.ten} chiến thắng!")
        return quai_vat


# Sử dụng
chien_binh = NhanVatChien("Thánh Chiến", 120, 18)
phap_su = NhanVatPhapSu("Pháp Sư Tối Thượng", 90, 22)
cung_thu = NhanVatCungThu("Cung Thủ Huyền Thoại", 100, 15)

quai1 = QuaiVat("Boss Orc", 150, 25, "Trùm")
quai2 = QuaiVat("Rồng Lửa", 200, 30, "Trùm Cuối")

# Chọn ngẫu nhiên một nhân vật để chiến đấu
nhan_vat_chon = random.choice([chien_binh, phap_su, cung_thu])
tran_dau(nhan_vat_chon, quai1)
```

---

### Bài 10: Hệ thống quản lý học sinh

```python
from abc import ABC, abstractmethod
from datetime import datetime


class HocSinh(ABC):
    """Lớp trừu tượng cho học sinh"""

    def __init__(self, ho_ten, ngay_sinh, dia_chi, ma_hs):
        self.ho_ten = ho_ten
        self.ngay_sinh = datetime.strptime(ngay_sinh, "%d/%m/%Y")
        self.dia_chi = dia_chi
        self.ma_hs = ma_hs
        self.diem = {}  # {môn: điểm}

    @property
    def tuoi(self):
        today = datetime.now()
        return (
            today.year
            - self.ngay_sinh.year
            - ((today.month, today.day) < (self.ngay_sinh.month, self.ngay_sinh.day))
        )

    def them_diem(self, mon, diem):
        """Thêm điểm cho môn học"""
        if not (0 <= diem <= 10):
            raise ValueError("Điểm phải từ 0-10")
        self.diem[mon] = diem

    def tinh_diem_trung_binh(self):
        """Tính điểm trung bình"""
        if not self.diem:
            return 0
        return sum(self.diem.values()) / len(self.diem)

    @abstractmethod
    def xep_loai(self):
        """Xếp loại học lực theo thang điểm riêng"""
        pass

    @abstractmethod
    def __str__(self):
        pass


class HocSinhCap1(HocSinh):
    """Học sinh cấp 1 - Xếp loại theo điểm trung bình"""

    def __init__(self, ho_ten, ngay_sinh, dia_chi, ma_hs, lop):
        super().__init__(ho_ten, ngay_sinh, dia_chi, ma_hs)
        self.lop = lop

    def xep_loai(self):
        tb = self.tinh_diem_trung_binh()
        if tb >= 9.0:
            return "Xuất sắc"
        elif tb >= 8.0:
            return "Giỏi"
        elif tb >= 6.5:
            return "Khá"
        elif tb >= 5.0:
            return "Trung bình"
        else:
            return "Yếu"

    def __str__(self):
        return (
            f"[Cấp 1] {self.ma_hs}: {self.ho_ten} - Lớp {self.lop} - {self.xep_loai()}"
        )


class HocSinhCap2(HocSinh):
    """Học sinh cấp 2 - Xếp loại có kiểm tra học bạ"""

    def __init__(self, ho_ten, ngay_sinh, dia_chi, ma_hs, lop, hoc_ba=True):
        super().__init__(ho_ten, ngay_sinh, dia_chi, ma_hs)
        self.lop = lop
        self.hoc_ba = hoc_ba  # Có học bạ hay không

    def xep_loai(self):
        if not self.hoc_ba:
            return "Chưa có học bạ"

        tb = self.tinh_diem_trung_binh()
        if tb >= 8.0:
            return "Giỏi"
        elif tb >= 6.5:
            return "Khá"
        elif tb >= 5.0:
            return "Trung bình"
        else:
            return "Yếu"

    def __str__(self):
        hoc_ba_text = "Có học bạ" if self.hoc_ba else "Chưa có học bạ"
        return f"[Cấp 2] {self.ma_hs}: {self.ho_ten} - Lớp {self.lop} - {hoc_ba_text} - {self.xep_loai()}"


class HocSinhCap3(HocSinh):
    """Học sinh cấp 3 - Xếp loại và khối thi"""

    KHOI_THI = ["A", "A1", "B", "C", "D"]

    def __init__(self, ho_ten, ngay_sinh, dia_chi, ma_hs, lop, khoi_thi="A"):
        super().__init__(ho_ten, ngay_sinh, dia_chi, ma_hs)
        self.lop = lop
        if khoi_thi not in self.KHOI_THI:
            raise ValueError(f"Khối thi không hợp lệ! Phải là {self.KHOI_THI}")
        self.khoi_thi = khoi_thi

    def xep_loai(self):
        tb = self.tinh_diem_trung_binh()
        if tb >= 8.0:
            return "Giỏi"
        elif tb >= 6.5:
            return "Khá"
        elif tb >= 5.0:
            return "Trung bình"
        else:
            return "Yếu"

    def tinh_diem_xet_tot_nghiep(self):
        """Tính điểm xét tốt nghiệp đơn giản"""
        if not self.diem:
            return 0
        # Trung bình tất cả môn * 0.7 + 0.3 (điểm ưu tiên giả định)
        return self.tinh_diem_trung_binh() * 0.7 + 0.3

    def __str__(self):
        return f"[Cấp 3] {self.ma_hs}: {self.ho_ten} - Lớp {self.lop} - Khối {self.khoi_thi} - {self.xep_loai()}"


class HeThongQuanLyHocSinh:
    """Hệ thống quản lý học sinh"""

    def __init__(self):
        self.danh_sach_hoc_sinh = []

    def them_hoc_sinh(self, hoc_sinh):
        self.danh_sach_hoc_sinh.append(hoc_sinh)
        return f"Đã thêm học sinh: {hoc_sinh.ho_ten}"

    def tim_kiem(self, tu_khoa):
        """Tìm kiếm học sinh theo tên hoặc mã"""
        ket_qua = []
        tu_khoa = tu_khoa.lower()
        for hs in self.danh_sach_hoc_sinh:
            if tu_khoa in hs.ho_ten.lower() or tu_khoa in hs.ma_hs.lower():
                ket_qua.append(hs)
        return ket_qua

    def thong_ke_theo_cap(self):
        """Thống kê số lượng học sinh theo cấp học"""
        thong_ke = {}
        for hs in self.danh_sach_hoc_sinh:
            cap = hs.__class__.__name__
            thong_ke[cap] = thong_ke.get(cap, 0) + 1
        return thong_ke

    def thong_ke_theo_xep_loai(self):
        """Thống kê xếp loại của học sinh"""
        thong_ke = {}
        for hs in self.danh_sach_hoc_sinh:
            loai = hs.xep_loai()
            thong_ke[loai] = thong_ke.get(loai, 0) + 1
        return thong_ke

    def in_danh_sach(self):
        """In danh sách tất cả học sinh"""
        print("\n" + "=" * 70)
        print("DANH SÁCH HỌC SINH")
        print("=" * 70)
        for hs in sorted(self.danh_sach_hoc_sinh, key=lambda x: x.ma_hs):
            print(hs)
            if hs.diem:
                print(f"   Điểm: {', '.join(f'{m}: {d}' for m, d in hs.diem.items())}")
                print(f"   Điểm TB: {hs.tinh_diem_trung_binh():.2f}")
        print("=" * 70)


# Sử dụng
he_thong = HeThongQuanLyHocSinh()

# Tạo học sinh
hs1 = HocSinhCap1("Nguyễn Văn A", "15/03/2014", "Hà Nội", "HS001", "5A")
hs2 = HocSinhCap1("Trần Thị B", "20/07/2015", "Hà Nội", "HS002", "4B")
hs3 = HocSinhCap2("Lê Văn C", "10/11/2012", "Hà Nội", "HS003", "8A")
hs4 = HocSinhCap2("Phạm Thị D", "05/09/2013", "Hà Nội", "HS004", "7B", hoc_ba=False)
hs5 = HocSinhCap3("Ngô Văn E", "25/12/2008", "Hà Nội", "HS005", "12A", "A")
hs6 = HocSinhCap3("Đỗ Thị F", "30/06/2009", "Hà Nội", "HS006", "11B", "D")

# Thêm điểm
hs1.them_diem("Toán", 9.5)
hs1.them_diem("Tiếng Việt", 8.0)
hs1.them_diem("Khoa học", 7.5)

hs2.them_diem("Toán", 6.0)
hs2.them_diem("Tiếng Việt", 7.5)
hs2.them_diem("Khoa học", 6.5)

hs3.them_diem("Toán", 8.5)
hs3.them_diem("Văn", 7.0)
hs3.them_diem("Anh", 9.0)

hs5.them_diem("Toán", 9.0)
hs5.them_diem("Lý", 8.5)
hs5.them_diem("Hóa", 9.5)

hs6.them_diem("Văn", 8.0)
hs6.them_diem("Sử", 7.5)
hs6.them_diem("Địa", 8.5)

# Thêm vào hệ thống
for hs in [hs1, hs2, hs3, hs4, hs5, hs6]:
    he_thong.them_hoc_sinh(hs)

# In danh sách
he_thong.in_danh_sach()

# Thống kê
print("\n📊 THỐNG KÊ:")
print(f"Theo cấp học: {he_thong.thong_ke_theo_cap()}")
print(f"Theo xếp loại: {he_thong.thong_ke_theo_xep_loai()}")

# Tìm kiếm
print("\n🔍 Tìm kiếm 'Văn':")
for hs in he_thong.tim_kiem("Văn"):
    print(f"   - {hs.ho_ten} ({hs.ma_hs})")
```

---

## 🎯 TỔNG KẾT BÀI 7

### Các khái niệm quan trọng đã áp dụng:

1. **Abstract Class**: Dùng `ABC` và `@abstractmethod` để tạo khuôn mẫu
2. **Kế thừa đơn**: `class Con(Cha):` - tái sử dụng code
3. **`super()`**: Gọi phương thức của lớp cha
4. **Override**: Viết lại phương thức của cha
5. **Đa hình**: Cùng một phương thức, hành vi khác nhau
6. **Composition**: Kết hợp các đối tượng (ví dụ: `ThuVien` chứa `Sach`)
7. **Mixin**: Thêm tính năng mà không cần kế thừa (ví dụ: `CoTheChay`)

### Mẹo hay khi làm bài tập OOP:

1. **Bắt đầu từ Abstract Class** - định nghĩa interface chung
2. **Sử dụng `super()` luôn** - để gọi `__init__` của cha
3. **Tận dụng đa hình** - viết hàm làm việc với lớp cha
4. **Phân biệt rõ ràng**:
   - `is-a` → Inheritance (Dog is an Animal)
   - `has-a` → Composition (Car has an Engine)
5. **DOCUMENTATION** - viết docstring cho tất cả class và method

---

**Bạn đã hoàn thành xuất sắc Bài 7!** 💪

*Sẵn sàng cho Bài 8: Decorator và Closure chưa?* 🚀