**Bài 13: OOP Phần 2 – Inheritance (Kế thừa)**

Kế thừa là một trong 4 tính chất cốt lõi của OOP (cùng với Đóng gói, Đa hình, Trừu tượng).  
Nó cho phép class mới **tái sử dụng** code của class đã có, giúp code ngắn gọn và dễ mở rộng hơn.

---

### 1. Kế thừa là gì?

- **Class cha (Parent / Base / Superclass)**: class gốc
- **Class con (Child / Derived / Subclass)**: class kế thừa từ class cha

Class con sẽ **có tất cả** thuộc tính và method của class cha, đồng thời có thể bổ sung hoặc ghi đè thêm.

---

### 2. Cú pháp cơ bản

```python
class DongVat:  # Class cha
    def __init__(self, ten):
        self.ten = ten

    def keu(self):
        print("Động vật đang kêu")

    def an(self):
        print(f"{self.ten} đang ăn")


class Cho(DongVat):  # Class con kế thừa DongVat
    def keu(self):  # Ghi đè (override) method
        print(f"{self.ten} đang sủa: Gâu gâu!")


class Meo(DongVat):
    def keu(self):
        print(f"{self.ten} đang kêu: Meo meo!")


# Sử dụng
c = Cho("Lu")
c.an()  # kế thừa từ DongVat → Lu đang ăn
c.keu()  # dùng version của class Cho → Lu đang sủa: Gâu gâu!

m = Meo("Miu")
m.an()
m.keu()
```

---

### 3. Hàm `super()` – Gọi lại class cha

Khi bạn muốn **giữ lại** hành vi của class cha và chỉ bổ sung thêm, dùng `super()`.

```python
class DongVat:
    def __init__(self, ten):
        self.ten = ten
        print(f"Khởi tạo Động vật: {self.ten}")

    def thong_tin(self):
        print(f"Tên: {self.ten}")


class Cho(DongVat):
    def __init__(self, ten, giong):
        super().__init__(ten)  # gọi __init__ của class cha
        self.giong = giong
        print(f"Giống chó: {self.giong}")

    def thong_tin(self):
        super().thong_tin()  # gọi method của class cha
        print(f"Giống: {self.giong}")


c = Cho("Lu", "Corgi")
c.thong_tin()
```

**Kết quả:**
```
Khởi tạo Động vật: Lu
Giống chó: Corgi
Tên: Lu
Giống: Corgi
```

---

### 4. Ví dụ thực tế hơn – Hệ thống nhân viên

```python
class NhanVien:
    def __init__(self, ma_nv, ho_ten, luong_co_ban):
        self.ma_nv = ma_nv
        self.ho_ten = ho_ten
        self.luong_co_ban = luong_co_ban

    def tinh_luong(self):
        return self.luong_co_ban

    def hien_thi(self):
        print(f"Mã: {self.ma_nv} | Tên: {self.ho_ten} | Lương: {self.tinh_luong()}")


class LapTrinhVien(NhanVien):
    def __init__(self, ma_nv, ho_ten, luong_co_ban, ngon_ngu, thuong=0):
        super().__init__(ma_nv, ho_ten, luong_co_ban)
        self.ngon_ngu = ngon_ngu
        self.thuong = thuong

    def tinh_luong(self):  # ghi đè
        return self.luong_co_ban + self.thuong

    def hien_thi(self):
        super().hien_thi()
        print(f"Ngôn ngữ: {self.ngon_ngu}")


class KeToan(NhanVien):
    def __init__(self, ma_nv, ho_ten, luong_co_ban, chung_chi):
        super().__init__(ma_nv, ho_ten, luong_co_ban)
        self.chung_chi = chung_chi

    def hien_thi(self):
        super().hien_thi()
        print(f"Chứng chỉ: {self.chung_chi}")


# Sử dụng
nv1 = LapTrinhVien("LT01", "An", 15000000, "Python", 3000000)
nv2 = KeToan("KT01", "Bình", 12000000, "CPA")

nv1.hien_thi()
print("-" * 40)
nv2.hien_thi()
```

---

### 5. Kiểm tra quan hệ kế thừa

```python
print(isinstance(nv1, LapTrinhVien))  # True
print(isinstance(nv1, NhanVien))  # True (vì kế thừa)
print(isinstance(nv1, KeToan))  # False

print(issubclass(LapTrinhVien, NhanVien))  # True
print(issubclass(KeToan, LapTrinhVien))  # False
```

---

### 6. Kế thừa nhiều lớp (Multiple Inheritance)

Python hỗ trợ kế thừa từ nhiều class cùng lúc:

```python
class A:
    def method(self):
        print("A")


class B:
    def method(self):
        print("B")


class C(A, B):  # ưu tiên A trước B
    pass


c = C()
c.method()  # in ra "A"
```

**Lưu ý:** Nên hạn chế dùng multiple inheritance nếu chưa thực sự cần (dễ phức tạp).

---

### 7. Khi nào nên dùng Kế thừa?

**Nên dùng khi:**
- Có quan hệ **“là một”** (is-a): Chó **là một** Động vật, LậpTrìnhViên **là một** NhânViên
- Muốn tái sử dụng code logic chung

**Không nên dùng khi:**
- Chỉ muốn dùng lại một vài hàm → nên dùng **composition** (kết hợp) thay vì kế thừa
- Quan hệ kiểu “có một” (has-a)

---

### 8. Tóm tắt nhanh

| Khái niệm              | Ý nghĩa                                      |
|------------------------|----------------------------------------------|
| Class cha              | Class gốc được kế thừa                       |
| Class con              | Class nhận di sản từ class cha               |
| Override               | Ghi đè method của class cha                  |
| `super()`              | Gọi method/constructor của class cha         |
| `isinstance()`         | Kiểm tra object có thuộc class không         |
| `issubclass()`         | Kiểm tra quan hệ kế thừa giữa 2 class        |

---

### Bài tập Bài 13

**Bài 1:**  
Tạo class `PhuongTien` có thuộc tính `ten`, `van_toc` và method `chay()`.  
Tạo 2 class con `XeMay` và `OTo` kế thừa từ `PhuongTien`, mỗi class ghi đè method `chay()` khác nhau.

**Bài 2:**  
Tạo class `Nguoi` (họ tên, năm sinh).  
Tạo class `SinhVien` kế thừa `Nguoi`, bổ sung thêm `ma_sv`, `diem_tb`.  
Tạo class `GiangVien` kế thừa `Nguoi`, bổ sung thêm `ma_gv`, `hoc_vi`.

**Bài 3:**  
Mở rộng bài Nhân viên ở trên:
- Thêm class `ThucTapSinh` kế thừa `NhanVien` (lương = lương cơ bản * 0.5)
- Tạo danh sách chứa nhiều loại nhân viên khác nhau và in thông tin + lương của từng người

**Bài 4:**  
Viết class `HinhHoc` có method `dien_tich()` và `chu_vi()` (chưa có nội dung cụ thể).  
Tạo 2 class con `HinhChuNhat` và `HinhTron` kế thừa và triển khai đầy đủ 2 method trên.

**Bài 5 (nâng cao):**  
Thiết kế hệ thống thư viện đơn giản:
- Class `TaiLieu` (mã, tên, năm xuất bản)
- Class `Sach` kế thừa `TaiLieu` (thêm tác giả, số trang)
- Class `TapChi` kế thừa `TaiLieu` (thêm số phát hành)
- Viết method `hien_thi()` phù hợp cho từng loại

---

Làm xong gửi code + kết quả.  
Tôi sẽ chữa bài và mở **Bài 14: OOP Phần 3 – Encapsulation & Polymorphism**.

Kế thừa giúp code của bạn “thông minh” và tái sử dụng tốt hơn rất nhiều. Cứ làm kỹ nhé!