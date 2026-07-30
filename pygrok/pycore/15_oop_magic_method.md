**Bài 15: OOP Nâng cao – Magic Methods, Class Method, Static Method**

Đây là bài giúp code OOP của bạn trở nên **chuyên nghiệp và “Pythonic”** hơn rất nhiều.

---

### 1. Magic Methods (Dunder Methods)

Magic Methods là các method đặc biệt có tên dạng `__ten__`.  
Chúng cho phép object của bạn hoạt động với các toán tử và hàm có sẵn của Python.

#### 1.1. `__str__` và `__repr__` (quan trọng nhất)

```python
class HocSinh:
    def __init__(self, ten, diem):
        self.ten = ten
        self.diem = diem

    def __str__(self):
        # Dành cho người dùng (print)
        return f"Học sinh {self.ten} - Điểm: {self.diem}"

    def __repr__(self):
        # Dành cho lập trình viên (debug)
        return f"HocSinh('{self.ten}', {self.diem})"


hs = HocSinh("An", 8.5)
print(hs)  # gọi __str__ → Học sinh An - Điểm: 8.5
print(repr(hs))  # gọi __repr__ → HocSinh('An', 8.5)
```

#### 1.2. Các Magic Method hay dùng

```python
class DiemSo:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):  # ==
        return self.value == other.value

    def __lt__(self, other):  # <
        return self.value < other.value

    def __add__(self, other):  # +
        return DiemSo(self.value + other.value)

    def __len__(self):  # len()
        return 1

    def __getitem__(self, index):  # obj[index]
        return self.value


d1 = DiemSo(8)
d2 = DiemSo(7)

print(d1 == d2)  # False
print(d1 > d2)  # True (Python tự suy ra từ __lt__)
print(d1 + d2)  # dùng __add__
```

**Một số Magic Method phổ biến:**

| Magic Method     | Tương ứng với          |
|------------------|------------------------|
| `__str__`        | `print(obj)`           |
| `__repr__`       | `repr(obj)`            |
| `__len__`        | `len(obj)`             |
| `__eq__`         | `==`                   |
| `__lt__`, `__gt__`| `<`, `>`              |
| `__add__`        | `+`                    |
| `__getitem__`    | `obj[key]`             |
| `__setitem__`    | `obj[key] = value`     |
| `__call__`       | `obj()`                |
| `__enter__`, `__exit__` | `with obj:`     |

---

### 2. `@classmethod`

Method thuộc về **class**, không thuộc về object.  
Tham số đầu tiên là `cls` (class) thay vì `self`.

**Ứng dụng phổ biến nhất:** Tạo factory method (tạo object theo nhiều cách khác nhau).

```python
class HocSinh:
    so_luong = 0

    def __init__(self, ten, diem):
        self.ten = ten
        self.diem = diem
        HocSinh.so_luong += 1

    @classmethod
    def from_string(cls, chuoi):
        """Tạo object từ chuỗi 'Tên-Điểm'"""
        ten, diem = chuoi.split("-")
        return cls(ten.strip(), float(diem))

    @classmethod
    def so_hoc_sinh(cls):
        return cls.so_luong


hs1 = HocSinh("An", 8.5)
hs2 = HocSinh.from_string("Bình - 7.5")  # dùng classmethod

print(hs2.ten, hs2.diem)
print(HocSinh.so_hoc_sinh())  # 2
```

---

### 3. `@staticmethod`

Method **không cần** `self` cũng không cần `cls`.  
Nó giống như hàm bình thường nhưng được đặt trong class để dễ tổ chức.

```python
class ToanHoc:
    @staticmethod
    def cong(a, b):
        return a + b

    @staticmethod
    def la_so_nguyen_to(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True


print(ToanHoc.cong(3, 5))  # 8
print(ToanHoc.la_so_nguyen_to(17))  # True
```

---

### 4. So sánh 3 loại Method

| Loại              | Tham số đầu tiên | Cần object? | Mục đích chính                     |
|-------------------|------------------|-------------|------------------------------------|
| Instance Method   | `self`           | Có          | Thao tác trên dữ liệu của object   |
| Class Method      | `cls`            | Không       | Thao tác liên quan đến class       |
| Static Method     | Không có         | Không       | Hàm tiện ích liên quan đến class   |

```python
class ViDu:
    def instance_method(self):
        print("Instance method", self)

    @classmethod
    def class_method(cls):
        print("Class method", cls)

    @staticmethod
    def static_method():
        print("Static method")


obj = ViDu()
obj.instance_method()
ViDu.class_method()
ViDu.static_method()
```

---

### 5. Ví dụ tổng hợp đẹp

```python
class TaiKhoan:
    lai_suat = 0.05  # thuộc tính class

    def __init__(self, chu_tk, so_du):
        self.chu_tk = chu_tk
        self.so_du = so_du

    def __str__(self):
        return f"Tài khoản {self.chu_tk}: {self.so_du:,.0f} VNĐ"

    def __repr__(self):
        return f"TaiKhoan('{self.chu_tk}', {self.so_du})"

    def nap_tien(self, so_tien):
        self.so_du += so_tien

    @classmethod
    def thay_doi_lai_suat(cls, lai_suat_moi):
        cls.lai_suat = lai_suat_moi

    @staticmethod
    def kiem_tra_so_tien(so_tien):
        return so_tien > 0


tk = TaiKhoan("An", 10_000_000)
print(tk)  # dùng __str__

TaiKhoan.thay_doi_lai_suat(0.06)
print(TaiKhoan.lai_suat)

print(TaiKhoan.kiem_tra_so_tien(5000))  # True
```

---

### Bài tập Bài 15

**Bài 1:**  
Viết class `Diem` có thuộc tính `x`, `y`.  
Triển khai các magic method: `__str__`, `__repr__`, `__add__` (cộng 2 điểm), `__eq__`.

**Bài 2:**  
Viết class `SinhVien` với:
- `__str__` và `__repr__`
- `@classmethod` để tạo sinh viên từ chuỗi `"Mã-Tên-Điểm"`
- `@staticmethod` để kiểm tra điểm có hợp lệ (0–10) không

**Bài 3:**  
Viết class `HinhChuNhat` với:
- Method tính diện tích, chu vi
- Magic method `__str__`, `__eq__` (so sánh diện tích), `__lt__`

**Bài 4:**  
Viết class `NganHang` quản lý nhiều tài khoản.  
Dùng `@classmethod` để thay đổi lãi suất chung.  
Dùng `@staticmethod` để kiểm tra số tiền hợp lệ.

**Bài 5 (nâng cao):**  
Viết class `Vector` (2D) hỗ trợ:
- Cộng, trừ 2 vector (`__add__`, `__sub__`)
- Nhân vector với một số (`__mul__`)
- So sánh độ dài (`__lt__`, `__eq__`)
- `__str__` và `__repr__`
- `@staticmethod` tính khoảng cách giữa 2 vector

---

Làm xong gửi code + kết quả.  
Tôi sẽ chữa bài và mở **Bài 16: Làm việc với JSON & CSV** (xử lý dữ liệu thực tế rất quan trọng).

Nắm được Magic Methods + classmethod + staticmethod sẽ giúp code của bạn trông chuyên nghiệp hẳn lên. Cứ làm kỹ nhé!