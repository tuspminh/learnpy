Chào bạn! Tôi thấy bạn rất quyết tâm học liên tục - tinh thần tuyệt vời! 

Trước khi vào Bài 3, tôi muốn nhắc nhẹ: **việc gửi code Bài 1 & 2 để tôi review sẽ giúp bạn tiến bộ nhanh gấp 3 lần** vì tôi có thể chỉ ra lỗi tư duy mà bạn không tự thấy được. Nhưng nếu bạn muốn học tiếp, chúng ta bắt đầu ngay!

---

# 📘 BÀI 3: CẤU TRÚC DỮ LIỆU CƠ BẢN (List, Tuple, Set, Dict)

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Master **4 cấu trúc dữ liệu** quan trọng nhất Python
- Biết khi nào dùng cấu trúc nào
- Sử dụng thành thạo các method (append, pop, keys, values...)
- Viết **List Comprehension** - kỹ năng cực kỳ quan trọng trong Python
- Áp dụng vào bài toán quản lý dữ liệu thực tế

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. List (Danh sách) - Dùng 90% thời gian

**Đặc điểm:** 
- ✅ Có thứ tự, có chỉ số (index)
- ✅ Có thể thay đổi (mutable) - thêm/sửa/xóa được
- ✅ Lưu được nhiều kiểu dữ liệu khác nhau

```python
# Khởi tạo
ds_rong = []
ds_so = [1, 2, 3, 4, 5]
ds_hon_hop = [1, "Python", 3.14, True, [1, 2]]  # List lồng nhau

# Truy xuất (chỉ số bắt đầu từ 0)
print(ds_so[0])  # 1
print(ds_so[-1])  # 5 (lấy từ cuối lên)
print(ds_so[1:4])  # [2, 3, 4] (cắt list - slicing)

# Slicing chi tiết: [start:stop:step]
ds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(ds[::2])  # [0, 2, 4, 6, 8] (bước nhảy 2)
print(ds[::-1])  # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (đảo ngược)
```

**Các method quan trọng (NHỚ THUỘC):**

```python
ds = [1, 2, 3]

# THÊM
ds.append(4)  # Thêm vào cuối: [1, 2, 3, 4]
ds.insert(1, 99)  # Chèn vào vị trí 1: [1, 99, 2, 3, 4]
ds.extend([5, 6])  # Nối list: [1, 99, 2, 3, 4, 5, 6]

# XÓA
ds.pop()  # Xóa và trả về phần tử cuối: trả về 6
ds.pop(2)  # Xóa vị trí 2: trả về 2
ds.remove(99)  # Xóa giá trị 99 (lần đầu tiên)
del ds[0]  # Xóa vị trí 0
ds.clear()  # Xóa toàn bộ

# TÌM KIẾM & SẮP XẾP
ds = [3, 1, 4, 1, 5, 9]
ds.index(4)  # Tìm vị trí của 4: 2
ds.count(1)  # Đếm số lần xuất hiện: 2
ds.sort()  # Sắp xếp tăng dần: [1, 1, 3, 4, 5, 9]
ds.sort(reverse=True)  # Giảm dần: [9, 5, 4, 3, 1, 1]
ds.reverse()  # Đảo ngược thứ tự
sorted(ds)  # Trả về list mới đã sắp xếp (không thay đổi gốc)

# COPING (QUAN TRỌNG)
ds_2 = ds  # ❌ KHÔNG copy, cùng trỏ đến 1 vùng nhớ
ds_2 = ds.copy()  # ✅ Copy nông (shallow copy)
ds_2 = ds[:]  # ✅ Cũng là copy
```

**Duyệt list đúng cách:**
```python
ds = ["a", "b", "c"]

# Cách 1: Duyệt giá trị
for item in ds:
    print(item)

# Cách 2: Duyệt chỉ số (khi cần index)
for i in range(len(ds)):
    print(f"{i}: {ds[i]}")

# Cách 3: Duyệt cả index và value (Pythonic)
for i, value in enumerate(ds):
    print(f"{i}: {value}")
```

---

### 1.2. Tuple (Bộ) - List không thể thay đổi

**Đặc điểm:**
- Giống List nhưng **không thể thay đổi** (immutable) sau khi tạo
- Tốc độ nhanh hơn List
- Dùng cho dữ liệu cố định: ngày tháng, tọa độ, API keys...

```python
# Khởi tạo
toa_do = (10.5, 20.8)
ngay_thang = (2026, 7, 27)
don_hang = ("SP001", "Áo sơ mi", 250000)

# Truy xuất như list (có index)
print(toa_do[0])  # 10.5
print(ngay_thang[1:])  # (7, 27)

# HÀM TẠO TUPLE TỪ LIST
ds = [1, 2, 3]
tuple_tu_ds = tuple(ds)  # (1, 2, 3)

# UNPACKING (GIẢI NÉN) - CỰC KỲ HỮU ÍCH
x, y = toa_do  # x = 10.5, y = 20.8
ma, ten, gia = don_hang  # ma="SP001", ten="Áo sơ mi", gia=250000


# *args trong hàm = tuple
def tinh_tong(*args):
    return sum(args)  # args là tuple


print(tinh_tong(1, 2, 3, 4))  # 10
```

---

### 1.3. Set (Tập hợp) - Không trùng lặp

**Đặc điểm:**
- ✅ Không có thứ tự (không dùng index)
- ✅ **Không chứa phần tử trùng lặp** (đặc tính quan trọng)
- ✅ Hỗ trợ các phép toán tập hợp: hợp, giao, hiệu

```python
# Khởi tạo
tap = {1, 2, 3, 4, 5}
tap_hon_hop = {1, "Python", 3.14}

# Tự động loại bỏ trùng lặp
ds = [1, 2, 2, 3, 3, 3, 4]
tap_duy_nhat = set(ds)  # {1, 2, 3, 4}
ds_khong_trung = list(tap_duy_nhat)  # [1, 2, 3, 4]

# PHÉP TOÁN TẬP HỢP
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

A.union(B)  # {1, 2, 3, 4, 5, 6} (hợp)
A.intersection(B)  # {3, 4} (giao)
A.difference(B)  # {1, 2} (hiệu)
A.symmetric_difference(B)  # {1, 2, 5, 6} (hiệu đối xứng)

# Thêm/Xóa
A.add(7)  # {1, 2, 3, 4, 7}
A.remove(7)  # Bỏ 7 (báo lỗi nếu không có)
A.discard(7)  # Bỏ 7 (không báo lỗi)
A.pop()  # Xóa và trả về phần tử bất kỳ
```

**Ứng dụng thực tế:** Loại bỏ trùng lặp trong danh sách
```python
# Tìm danh sách khách hàng duy nhất đã mua hàng
hoa_don = ["An", "Bình", "An", "Châu", "Bình", "Dũng"]
khach_duy_nhat = list(set(hoa_don))  # ['An', 'Bình', 'Châu', 'Dũng']
```

---

### 1.4. Dictionary (Từ điển) - Cấu trúc quan trọng nhất

**Đặc điểm:**
- Lưu dữ liệu theo cặp **Key - Value** (khóa - giá trị)
- Khóa (key) **không được trùng**, có thể là số hoặc chuỗi
- Giá trị (value) có thể là bất kỳ kiểu dữ liệu nào

```python
# Khởi tạo
sinh_vien = {
    "ma": "SV001",
    "ten": "Nguyễn Văn A",
    "tuoi": 20,
    "diem": [8.5, 9.0, 7.5],  # Giá trị có thể là list
}

# Truy xuất
print(sinh_vien["ma"])  # SV001 (lỗi nếu key không tồn tại)
print(sinh_vien.get("ten"))  # Nguyễn Văn A (trả về None nếu không có)

# Thêm/Sửa
sinh_vien["que"] = "Hà Nội"  # Thêm mới
sinh_vien["tuoi"] = 21  # Sửa giá trị

# Xóa
del sinh_vien["que"]  # Xóa key "que"
diem = sinh_vien.pop("diem")  # Xóa và trả về giá trị

# Lấy các view (QUAN TRỌNG)
keys = sinh_vien.keys()  # dict_keys(['ma', 'ten', 'tuoi'])
values = sinh_vien.values()  # dict_values(['SV001', 'Nguyễn Văn A', 21])
items = sinh_vien.items()  # dict_items([('ma', 'SV001'), ...])

# Duyệt dictionary
for key in sinh_vien:
    print(f"{key}: {sinh_vien[key]}")

for key, value in sinh_vien.items():
    print(f"{key}: {value}")

# Kiểm tra key tồn tại
if "ma" in sinh_vien:
    print("Có mã sinh viên")
```

**Dictionary có thể lồng nhau:**
```python
truong_hoc = {
    "lớp A": {"sĩ_số": 30, "giáo_viên": "Cô Hoa"},
    "lớp B": {"sĩ_số": 28, "giáo_viên": "Thầy Nam"},
}

print(truong_hoc["lớp A"]["giáo_viên"])  # Cô Hoa
```

---

### 1.5. List Comprehension - Vũ khí bí mật của Python

**Giúp viết code ngắn gọn, nhanh hơn thay vì dùng vòng lặp:**

```python
# Cú pháp: [biểu_thức for phần_tử in iterable if điều_kiện]

# Bình thường:
ds = []
for i in range(10):
    ds.append(i**2)

# List Comprehension:
ds = [i**2 for i in range(10)]  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Có điều kiện:
so_chan = [x for x in range(20) if x % 2 == 0]  # [0, 2, 4, ..., 18]

# Biểu thức phức tạp:
nhan_doi = [x * 2 if x % 2 == 0 else x * 3 for x in range(10)]
# [0, 3, 4, 9, 8, 15, 12, 21, 16, 27]

# Lồng nhau:
matrix = [[i * j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Có thể dùng cho Set và Dict:
set_comprehension = {x**2 for x in range(5)}  # {0, 1, 4, 9, 16}
dict_comprehension = {x: x**2 for x in range(5)}  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Quản lý danh sách sinh viên (Dùng List + Dict)

```python
# Hệ thống quản lý sinh viên đơn giản
sinh_vien = []


# Thêm sinh viên
def them_sinh_vien(ma, ten, tuoi):
    sv = {"ma": ma, "ten": ten, "tuoi": tuoi}
    sinh_vien.append(sv)


# Tìm kiếm theo tên (trả về list các sinh viên)
def tim_kiem_theo_ten(ten_tim):
    return [sv for sv in sinh_vien if ten_tim.lower() in sv["ten"].lower()]


# Xóa theo mã
def xoa_theo_ma(ma_can_xoa):
    global sinh_vien
    sinh_vien = [sv for sv in sinh_vien if sv["ma"] != ma_can_xoa]


# Test
them_sinh_vien("SV001", "Nguyễn Văn An", 20)
them_sinh_vien("SV002", "Trần Thị Bình", 21)
them_sinh_vien("SV003", "Lê Văn An", 22)

print(tim_kiem_theo_ten("An"))  # Tìm được SV001 và SV003
print(f"Số lượng sinh viên: {len(sinh_vien)}")
```

---

### Ví dụ 2: Đếm số lần xuất hiện các từ trong văn bản (Dùng Dict)

```python
van_ban = "python java python c++ java python javascript"
tu_dem = {}

for tu in van_ban.split():  # split() tách chuỗi thành list theo khoảng trắng
    tu_dem[tu] = tu_dem.get(tu, 0) + 1

# In ra thống kê
for tu, so_lan in tu_dem.items():
    print(f"'{tu}': {so_lan} lần")

# Output:
# 'python': 3 lần
# 'java': 2 lần
# 'c++': 1 lần
# 'javascript': 1 lần
```

---

### Ví dụ 3: Xử lý dữ liệu bán hàng

```python
# Danh sách đơn hàng (mỗi đơn là dict)
don_hang = [
    {"ma": "DH001", "san_pham": "Áo", "so_luong": 2, "gia": 200000},
    {"ma": "DH002", "san_pham": "Quần", "so_luong": 1, "gia": 350000},
    {"ma": "DH003", "san_pham": "Áo", "so_luong": 3, "gia": 180000},
    {"ma": "DH004", "san_pham": "Giày", "so_luong": 1, "gia": 500000},
]

# Tính tổng doanh thu theo sản phẩm
doanh_thu = {}
for dh in don_hang:
    san_pham = dh["san_pham"]
    thanh_tien = dh["so_luong"] * dh["gia"]
    doanh_thu[san_pham] = doanh_thu.get(san_pham, 0) + thanh_tien

# Sắp xếp sản phẩm theo doanh thu (giảm dần)
xep_hang = sorted(doanh_thu.items(), key=lambda x: x[1], reverse=True)

print("Bảng xếp hạng doanh thu:")
for san_pham, tien in xep_hang:
    print(f"{san_pham}: {tien:,} VNĐ")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Tạo 1 list số từ 1-20. Tính tổng, trung bình cộng, và tìm số lớn nhất, nhỏ nhất.

**Bài 2:** Tạo list chứa tên các tháng trong năm. In ra các tháng có 31 ngày.

**Bài 3:** Cho 2 list: `[1, 2, 3, 4, 5]` và `[3, 4, 5, 6, 7]`. Tìm:
- Phần tử chung (intersection)
- Hợp của 2 list (không trùng)
- Phần tử chỉ có ở list 1

**Bài 4:** Cho chuỗi `"hello world python programming"`. Đếm số lần xuất hiện của từng từ (dùng dict).

**Bài 5:** Cho list số: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`. Dùng list comprehension để tạo list mới chứa bình phương các số chẵn.

**Bài 6:** Nhập họ tên đầy đủ (vd: "Nguyễn Văn An"). Tách thành:
- Họ: "Nguyễn"
- Tên đệm: "Văn"
- Tên: "An"

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Xây dựng từ điển Anh-Việt. Cho phép:
- Thêm từ mới
- Tra từ
- Xóa từ
- Hiển thị tất cả từ

**Bài 8:** Cho list `[1, 2, 2, 3, 3, 3, 4, 4, 4, 4]`. Viết chương trình đếm tần suất xuất hiện của từng số.

**Bài 9:** Tạo ma trận (list lồng nhau) 3x3:
```
[[1, 2, 3],
 [4, 5, 6],
 [7, 8, 9]]
```
In ra: tổng từng hàng, tổng từng cột, tổng đường chéo chính.

**Bài 10:** Viết chương trình quản lý sổ địa chỉ:
- Mỗi contact là 1 dict với: tên, số điện thoại, email
- Các chức năng: thêm, sửa, xóa, tìm kiếm, hiển thị tất cả
- Lưu tất cả contacts trong 1 list

---

## 🏗️ MINI-PROJECT: HỆ THỐNG QUẢN LÝ THƯ VIỆN

```python
"""
Xây dựng hệ thống đơn giản với:
1. Sách được lưu trong list, mỗi sách là dict:
   {
       "ma": "B001",
       "ten": "Nhà giả kim",
       "tac_gia": "Paulo Coelho",
       "nam": 1988,
       "trang_thai": "có sẵn" | "đã mượn"
   }
2. Chức năng:
   - Thêm sách mới
   - Tìm sách theo tên/tác giả
   - Mượn sách (đổi trạng thái)
   - Trả sách
   - Hiển thị tất cả sách
3. Dùng các cấu trúc đã học: list, dict, set, tuple
"""

# Hãy tự code!
```

---

## ✅ KIỂM TRA CODE CHUYÊN NGHIỆP

- [ ] Dùng list comprehension thay vì vòng lặp đơn giản
- [ ] Sử dụng `.get()` với dict thay vì `if key in dict`
- [ ] Dùng `enumerate()` khi cần cả index và value
- [ ] Không dùng biến tên `list`, `dict`, `str` (che mất hàm built-in)
- [ ] Dùng `set()` để loại bỏ trùng lặp

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Sử dụng dict comprehension để tạo từ điển ánh xạ:
# Input: ["a", "b", "c", "a", "b", "a"]
# Output: {"a": 3, "b": 2, "c": 1}

# One-liner sử dụng dict comprehension và .count()
```

---

## 🎯 TÓM TẮT NHANH KHI NÀO DÙNG GÌ

| Cấu trúc | Khi nào dùng | Ví dụ |
|----------|--------------|-------|
| **List** | Cần thứ tự, có thể thay đổi | Danh sách sinh viên |
| **Tuple** | Cần thứ tự, không thay đổi | Tọa độ X,Y |
| **Set** | Cần loại bỏ trùng lặp | Danh sách khách hàng duy nhất |
| **Dict** | Cần ánh xạ key → value | Thông tin chi tiết của sinh viên |

---

**Bây giờ hãy CODE! Bài 3 khó hơn, nhưng cực kỳ quan trọng trong thực tế. Gửi code cho tôi review nhé!** 💪

*P/S: Bài 4 sẽ dạy bạn về Hàm - thành thạo Bài 3 trước khi học tiếp nhé!*