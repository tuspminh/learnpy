**Bài 9: Module & Package**

Khi chương trình ngày càng lớn, bạn không thể viết hết code trong một file.  
Module và Package giúp bạn **tổ chức code** thành các phần riêng biệt, dễ quản lý và tái sử dụng.

---

### 1. Module là gì?

Module là một file Python (đuôi `.py`) chứa các hàm, biến, class…

Python có sẵn rất nhiều module (Standard Library). Bạn cũng có thể tự tạo module của riêng mình.

---

### 2. Cách import module

#### 2.1. Import toàn bộ module
```python
import math

print(math.sqrt(16))  # 4.0
print(math.pi)  # 3.141592653589793
print(math.ceil(4.2))  # 5
print(math.floor(4.8))  # 4
```

#### 2.2. Đặt tên ngắn (alias)
```python
import math as m

print(m.sqrt(25))
print(m.factorial(5))  # 120
```

#### 2.3. Import trực tiếp hàm/biến
```python
from math import sqrt, pi, ceil

print(sqrt(36))
print(pi)
print(ceil(3.1))
```

#### 2.4. Import tất cả (không khuyến khích)
```python
from math import *  # ít dùng, dễ bị trùng tên
```

---

### 3. Một số module chuẩn hay dùng

#### 3.1. `random` – Số ngẫu nhiên
```python
import random

print(random.randint(1, 10))  # số nguyên ngẫu nhiên từ 1 đến 10
print(random.random())  # số thực từ 0.0 đến 1.0
print(random.choice(["An", "Bình", "Chi"]))
print(random.sample(range(1, 50), 5))  # lấy 5 số không trùng

ds = [1, 2, 3, 4, 5]
random.shuffle(ds)  # xáo trộn list
print(ds)
```

#### 3.2. `datetime` – Ngày giờ
```python
from datetime import datetime, date, timedelta

now = datetime.now()
print(now)
print(now.year, now.month, now.day)
print(now.strftime("%d/%m/%Y %H:%M:%S"))

hom_nay = date.today()
print(hom_nay)

# Cộng trừ ngày
ngay_mai = hom_nay + timedelta(days=1)
print(ngay_mai)
```

#### 3.3. `os` – Tương tác với hệ điều hành
```python
import os

print(os.getcwd())  # thư mục hiện tại
print(os.listdir())  # liệt kê file/thư mục
# os.mkdir("thu_muc_moi")             # tạo thư mục
# os.remove("file.txt")               # xóa file
```

#### 3.4. `sys` – Thông tin hệ thống
```python
import sys

print(sys.version)  # phiên bản Python
print(sys.platform)  # hệ điều hành
```

---

### 4. Tự tạo module của bạn

**Bước 1:** Tạo file `toan_hoc.py`

```python
# File: toan_hoc.py


def cong(a, b):
    return a + b


def tru(a, b):
    return a - b


def nhan(a, b):
    return a * b


def chia(a, b):
    if b == 0:
        return "Không thể chia cho 0"
    return a / b


PI = 3.14159
```

**Bước 2:** Tạo file khác và import

```python
# File: main.py
import toan_hoc

print(toan_hoc.cong(10, 5))
print(toan_hoc.PI)

from toan_hoc import tru, nhan

print(tru(10, 3))
print(nhan(4, 5))
```

---

### 5. `if __name__ == "__main__"` (rất quan trọng)

Khi bạn chạy trực tiếp một file, Python gán `__name__ = "__main__"`.  
Khi file đó bị import, `__name__` sẽ là tên module.

```python
# File: toan_hoc.py


def cong(a, b):
    return a + b


if __name__ == "__main__":
    # Đoạn này chỉ chạy khi chạy trực tiếp file toan_hoc.py
    print("Đang chạy trực tiếp module toan_hoc")
    print(cong(5, 7))
```

**Tại sao cần?**  
Để tránh code test chạy lung tung khi module bị import.

---

### 6. Package (Gói)

Package là **thư mục** chứa nhiều module, có file `__init__.py` (có thể để trống).

Cấu trúc ví dụ:
```
my_package/
│
├── __init__.py
├── so_hoc.py
└── chuoi_hoc.py
```

Cách dùng:
```python
from my_package.so_hoc import cong
from my_package import chuoi_hoc
```

---

### 7. Cài thư viện bên thứ ba (pip)

Python có hàng trăm nghìn thư viện bên ngoài.

```bash
# Cài thư viện
pip install requests
pip install numpy
pip install pandas

# Xem thư viện đã cài
pip list

# Gỡ thư viện
pip uninstall requests
```

**Ví dụ dùng thư viện `requests`:**
```python
import requests

response = requests.get("https://api.github.com")
print(response.status_code)
```

---

### 8. Nguyên tắc tốt khi dùng Module

- Chỉ import những gì cần dùng
- Đặt tên module rõ ràng, dùng `snake_case`
- Tránh dùng `from module import *`
- Nên viết `if __name__ == "__main__":` trong mọi module
- Tách chức năng thành nhiều module nhỏ thay vì một file khổng lồ

---

### Bài tập Bài 9

**Bài 1:**  
Dùng module `math` để tính:
- Căn bậc hai của 144
- Giai thừa của 6
- Làm tròn lên và làm tròn xuống của 4.7

**Bài 2:**  
Viết chương trình dùng `random` để:
- Random một số từ 1 đến 100
- Random một phần tử trong list `["Táo", "Cam", "Chuối", "Xoài"]`
- Xáo trộn một list bất kỳ

**Bài 3:**  
Dùng `datetime` để in ra:
- Ngày giờ hiện tại
- Ngày giờ theo định dạng `Ngày dd/mm/yyyy - Giờ hh:mm:ss`
- Ngày của 7 ngày sau

**Bài 4:**  
Tự tạo module tên `xu_ly_chuoi.py` gồm các hàm:
- `chuan_hoa_ten(ten)`: xóa khoảng trắng thừa + title case
- `dem_tu(chuoi)`: đếm số từ trong chuỗi
- `lat_chuoi(chuoi)`: đảo ngược chuỗi

Sau đó viết file `main.py` import và sử dụng các hàm trên.

**Bài 5 (nâng cao):**  
Viết chương trình đoán số hoàn chỉnh:
- Dùng `random.randint(1, 100)`
- Cho người chơi đoán tối đa 7 lần
- Báo “Lớn hơn” / “Nhỏ hơn”
- Hết lượt thì báo số đúng

---

Làm xong gửi code + kết quả.  
Tôi sẽ chữa bài và mở **Bài 10: Xử lý File (Đọc & Ghi file)**.

Module giúp code của bạn chuyên nghiệp và có tổ chức hơn rất nhiều. Cứ làm kỹ nhé!