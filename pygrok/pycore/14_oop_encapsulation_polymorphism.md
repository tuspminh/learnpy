**Bài 14: OOP Phần 3 – Encapsulation & Polymorphism**

Đây là 2 tính chất còn lại trong 4 tính chất cốt lõi của OOP:
1. **Encapsulation** (Đóng gói)
2. **Polymorphism** (Đa hình)

(Kế thừa đã học ở Bài 13, Abstraction sẽ được đề cập nhẹ trong bài này)

---

### 1. Encapsulation (Đóng gói)

Đóng gói nghĩa là **che giấu dữ liệu** bên trong object và chỉ cho phép truy cập thông qua các method được kiểm soát.

#### 1.1. Các mức độ truy cập trong Python

| Cách viết      | Ý nghĩa              | Quy ước |
|----------------|----------------------|--------|
| `self.ten`     | Public               | Ai cũng truy cập được |
| `self._ten`    | Protected            | Nên coi là nội bộ (vẫn truy cập được) |
| `self.__ten`   | Private              | Python name mangling, khó truy cập từ bên ngoài |

```python
class TaiKhoan:
    def __init__(self, chu_tk, so_du):
        self.chu_tk = chu_tk  # public
        self._loai = "Tiết kiệm"  # protected
        self.__so_du = so_du  # private

    def xem_so_du(self):
        return self.__so_du

    def nap_tien(self, so_tien):
        if so_tien > 0:
            self.__so_du += so_tien
        else:
            print("Số tiền không hợp lệ")


tk = TaiKhoan("An", 1000)
print(tk.chu_tk)  # An
print(tk._loai)  # vẫn truy cập được (nhưng không nên)
# print(tk.__so_du)        # lỗi AttributeError
print(tk.xem_so_du())  # 1000  → cách truy cập đúng
```

#### 1.2. Getter & Setter truyền thống

```python
class HocSinh:
    def __init__(self, ten, diem):
        self.__ten = ten
        self.__diem = diem

    def get_diem(self):
        return self.__diem

    def set_diem(self, diem_moi):
        if 0 <= diem_moi <= 10:
            self.__diem = diem_moi
        else:
            print("Điểm phải nằm trong khoảng 0 - 10")
```

#### 1.3. Cách hiện đại: `@property` (Khuyến nghị)

```python
class HocSinh:
    def __init__(self, ten, diem):
        self.__ten = ten
        self.diem = diem  # gọi setter

    @property
    def diem(self):  # getter
        return self.__diem

    @diem.setter
    def diem(self, value):  # setter
        if 0 <= value <= 10:
            self.__diem = value
        else:
            raise ValueError("Điểm phải từ 0 đến 10")

    @property
    def ten(self):
        return self.__ten


hs = HocSinh("An", 8.5)
print(hs.diem)  # 8.5 (gọi getter)
hs.diem = 9.0  # gọi setter
# hs.diem = 15            # → ValueError
print(hs.ten)
```

**Lợi ích của Encapsulation:**
- Kiểm soát được dữ liệu đầu vào
- Dễ dàng thay đổi cách lưu trữ bên trong mà không ảnh hưởng code bên ngoài
- Bảo vệ dữ liệu quan trọng (số dư, mật khẩu…)

---

### 2. Polymorphism (Đa hình)

Đa hình nghĩa là **cùng một giao diện** (method) nhưng **hành vi khác nhau** tùy thuộc vào đối tượng cụ thể.

#### 2.1. Đa hình qua kế thừa (Method Overriding)

```python
class DongVat:
    def keu(self):
        print("Động vật kêu")


class Cho(DongVat):
    def keu(self):
        print("Gâu gâu")


class Meo(DongVat):
    def keu(self):
        print("Meo meo")


class Vit(DongVat):
    def keu(self):
        print("Quác quác")


# Đa hình thể hiện ở đây
danh_sach = [Cho(), Meo(), Vit(), DongVat()]

for dv in danh_sach:
    dv.keu()  # cùng method keu() nhưng kết quả khác nhau
```

#### 2.2. Duck Typing (Kiểu “vịt” – đặc trưng của Python)

> “Nếu nó đi như vịt và kêu như vịt, thì nó là vịt.”

Python không bắt buộc phải kế thừa cùng một class cha. Chỉ cần object có method phù hợp là được.

```python
class CaSi:
    def bieu_dien(self):
        print("Ca sĩ đang hát")


class NguoiMau:
    def bieu_dien(self):
        print("Người mẫu đang catwalk")


class DienVien:
    def bieu_dien(self):
        print("Diễn viên đang diễn")


def to_chuc_su_kien(nguoi):
    nguoi.bieu_dien()  # không quan tâm là class gì


to_chuc_su_kien(CaSi())
to_chuc_su_kien(NguoiMau())
to_chuc_su_kien(DienVien())
```

#### 2.3. Ví dụ thực tế – Tính diện tích các hình

```python
class HinhHoc:
    def dien_tich(self):
        pass


class HinhChuNhat(HinhHoc):
    def __init__(self, dai, rong):
        self.dai = dai
        self.rong = rong

    def dien_tich(self):
        return self.dai * self.rong


class HinhTron(HinhHoc):
    def __init__(self, ban_kinh):
        self.ban_kinh = ban_kinh

    def dien_tich(self):
        return 3.14159 * self.ban_kinh**2


class HinhTamGiac(HinhHoc):
    def __init__(self, day, chieu_cao):
        self.day = day
        self.chieu_cao = chieu_cao

    def dien_tich(self):
        return 0.5 * self.day * self.chieu_cao


hinh = [HinhChuNhat(5, 4), HinhTron(3), HinhTamGiac(6, 4)]

for h in hinh:
    print(f"Diện tích: {h.dien_tich():.2f}")
```

---

### 3. Tóm tắt 4 tính chất OOP

| Tính chất          | Ý nghĩa ngắn gọn                                      | Đã học ở bài |
|--------------------|-------------------------------------------------------|--------------|
| **Encapsulation**  | Che giấu dữ liệu, kiểm soát truy cập                  | Bài 14       |
| **Inheritance**    | Class con kế thừa class cha                           | Bài 13       |
| **Polymorphism**   | Cùng giao diện – hành vi khác nhau                    | Bài 14       |
| **Abstraction**    | Ẩn chi tiết phức tạp, chỉ hiện những gì cần thiết     | Đang dùng    |

---

### Bài tập Bài 14

**Bài 1: Encapsulation**  
Viết class `TaiKhoanNganHang` với:
- Thuộc tính private `__so_du`
- Dùng `@property` và `@setter` để đọc/ghi số dư
- Chỉ cho phép nạp/rút khi số tiền > 0 và đủ điều kiện

**Bài 2: Encapsulation**  
Viết class `SinhVien` với thuộc tính private `__diem`.  
Khi gán điểm phải kiểm tra nằm trong 0–10, nếu sai thì báo lỗi.

**Bài 3: Polymorphism**  
Tạo class cha `NhanVien` có method `tinh_luong()`.  
Tạo 3 class con: `LapTrinhVien`, `KeToan`, `ThucTapSinh` với cách tính lương khác nhau.  
Duyệt danh sách nhân viên và in lương của từng người.

**Bài 4: Polymorphism + Duck Typing**  
Viết hàm `hien_thi_thong_tin(obj)` có thể nhận bất kỳ object nào miễn là object đó có method `hien_thi()`.  
Tạo 3 class khác nhau (`Sach`, `SinhVien`, `SanPham`) đều có method `hien_thi()` và thử gọi hàm trên.

**Bài 5 (nâng cao):**  
Thiết kế class `GiaoDich` (số tiền, mô tả).  
Dùng Encapsulation để bảo vệ số tiền.  
Tạo 2 class con `Thu` và `Chi` (Polymorphism) có cách hiển thị khác nhau.  
Viết chương trình quản lý thu chi đơn giản.

---

Làm xong gửi code + kết quả.  
Tôi sẽ chữa bài và mở **Bài 15: Các chủ đề OOP nâng cao (Magic Methods, Class Method, Static Method…)**.

Nắm vững Encapsulation và Polymorphism là bạn đã hiểu bản chất của OOP. Cứ làm kỹ nhé!