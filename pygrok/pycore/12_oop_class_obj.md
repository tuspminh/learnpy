**Bài 12: Lập trình hướng đối tượng (OOP) – Phần 1: Class & Object**

Đây là bước ngoặt quan trọng. Từ đây bạn sẽ học cách tổ chức code theo hướng **đối tượng** – cách viết chương trình chuyên nghiệp và dễ mở rộng nhất hiện nay.

---

### 1. Lập trình hướng đối tượng là gì?

Thay vì chỉ nghĩ về **hàm** và **dữ liệu** riêng lẻ, OOP nghĩ về **đối tượng** trong thực tế.

Ví dụ thực tế:
- Đối tượng **Xe hơi**: có thuộc tính (màu, hãng, vận tốc) và hành vi (chạy, phanh, bóp còi)
- Đối tượng **Học sinh**: có thuộc tính (tên, tuổi, điểm) và hành vi (học bài, thi cử, chào hỏi)

**Class** = khuôn mẫu (bản thiết kế)  
**Object** = thực thể cụ thể được tạo ra từ khuôn mẫu đó

---

### 2. Tạo Class và Object đầu tiên

```python
class HocSinh:
    pass  # class trống


# Tạo object (thể hiện)
hs1 = HocSinh()
hs2 = HocSinh()

print(hs1)  # <__main__.HocSinh object at 0x...>
print(type(hs1))  # <class '__main__.HocSinh'>
```

---

### 3. Thuộc tính (Attribute) và Phương thức (Method)

```python
class HocSinh:
    def __init__(self, ten, tuoi, diem):
        self.ten = ten
        self.tuoi = tuoi
        self.diem = diem

    def gioi_thieu(self):
        print(f"Tôi tên {self.ten}, {self.tuoi} tuổi, điểm {self.diem}")

    def xep_loai(self):
        if self.diem >= 8:
            return "Giỏi"
        elif self.diem >= 6.5:
            return "Khá"
        elif self.diem >= 5:
            return "Trung bình"
        else:
            return "Yếu"
```

**Giải thích:**
- `__init__` là **constructor** – hàm đặc biệt tự động chạy khi tạo object
- `self` đại diện cho **chính object hiện tại** (bắt buộc phải có)
- `self.ten`, `self.tuoi`… là **thuộc tính** của object
- `gioi_thieu()`, `xep_loai()` là **phương thức** (hàm nằm trong class)

---

### 4. Tạo và sử dụng Object

```python
hs1 = HocSinh("An", 18, 8.5)
hs2 = HocSinh("Bình", 19, 6.8)

hs1.gioi_thieu()  # Tôi tên An, 18 tuổi, điểm 8.5
print(hs1.xep_loai())  # Giỏi

hs2.gioi_thieu()
print(hs2.xep_loai())  # Khá

# Truy cập thuộc tính trực tiếp
print(hs1.ten)  # An
print(hs2.diem)  # 6.8

# Thay đổi thuộc tính
hs1.diem = 9.0
print(hs1.xep_loai())  # Giỏi
```

---

### 5. `self` hoạt động như thế nào?

Khi bạn gọi:
```python
hs1.gioi_thieu()
```

Python thực chất gọi:
```python
HocSinh.gioi_thieu(hs1)
```

Vì vậy tham số đầu tiên của mọi method phải là `self`.

---

### 6. Thuộc tính lớp (Class Attribute) vs Thuộc tính đối tượng

```python
class HocSinh:
    so_luong = 0  # thuộc tính của class (dùng chung)

    def __init__(self, ten, diem):
        self.ten = ten  # thuộc tính của object
        self.diem = diem
        HocSinh.so_luong += 1


hs1 = HocSinh("An", 8)
hs2 = HocSinh("Bình", 7)
hs3 = HocSinh("Chi", 9)

print(HocSinh.so_luong)  # 3
print(hs1.so_luong)  # 3 (vẫn truy cập được)
```

---

### 7. Ví dụ hoàn chỉnh hơn

```python
class TaiKhoanNganHang:
    def __init__(self, chu_tai_khoan, so_du=0):
        self.chu_tai_khoan = chu_tai_khoan
        self.so_du = so_du

    def nap_tien(self, so_tien):
        if so_tien > 0:
            self.so_du += so_tien
            print(f"Nạp thành công {so_tien}. Số dư mới: {self.so_du}")
        else:
            print("Số tiền nạp phải lớn hơn 0")

    def rut_tien(self, so_tien):
        if so_tien > self.so_du:
            print("Không đủ tiền trong tài khoản")
        elif so_tien <= 0:
            print("Số tiền rút không hợp lệ")
        else:
            self.so_du -= so_tien
            print(f"Rút thành công {so_tien}. Số dư còn lại: {self.so_du}")

    def xem_so_du(self):
        print(f"Tài khoản của {self.chu_tai_khoan} hiện có: {self.so_du} VNĐ")


# Sử dụng
tk1 = TaiKhoanNganHang("Nguyễn Văn A", 1000)
tk1.xem_so_du()
tk1.nap_tien(500)
tk1.rut_tien(200)
tk1.rut_tien(2000)  # không đủ tiền
```

---

### 8. Một số quy tắc quan trọng

| Quy tắc | Giải thích |
|---------|-----------|
| Tên class viết **PascalCase** | `HocSinh`, `TaiKhoanNganHang` |
| Tên method viết **snake_case** | `gioi_thieu`, `nap_tien` |
| Luôn có `self` làm tham số đầu tiên của method | Bắt buộc |
| `__init__` không được `return` giá trị | Chỉ dùng để khởi tạo |
| Nên khởi tạo tất cả thuộc tính trong `__init__` | Để code rõ ràng |

---

### Bài tập Bài 12

**Bài 1:**  
Tạo class `XeHoi` có:
- Thuộc tính: `hang`, `mau`, `van_toc` (mặc định = 0)
- Method: `tang_toc(gia_tri)`, `giam_toc(gia_tri)`, `in_thong_tin()`

**Bài 2:**  
Tạo class `HinhChuNhat` có:
- Thuộc tính: `chieu_dai`, `chieu_rong`
- Method: `dien_tich()`, `chu_vi()`, `hien_thi()`

**Bài 3:**  
Tạo class `SinhVien` có:
- Thuộc tính: `ma_sv`, `ho_ten`, `diem_toan`, `diem_van`, `diem_anh`
- Method: `diem_trung_binh()`, `xep_loai()`, `hien_thi_thong_tin()`

**Bài 4:**  
Tạo class `TaiKhoan` (giống ví dụ ngân hàng ở trên) và bổ sung thêm:
- Method `chuyen_tien(tai_khoan_nhan, so_tien)`
- Kiểm tra đầy đủ điều kiện hợp lệ

**Bài 5 (nâng cao):**  
Tạo class `HocSinh` và viết chương trình quản lý danh sách học sinh:
- Thêm học sinh
- Hiển thị danh sách
- Tìm học sinh theo tên
- Sắp xếp theo điểm trung bình

---

Làm xong gửi code + kết quả.  
Tôi sẽ chữa bài và mở **Bài 13: OOP Phần 2 – Inheritance (Kế thừa)**.

OOP là nền tảng để bạn viết được các dự án lớn sau này. Cứ làm kỹ bài này nhé!