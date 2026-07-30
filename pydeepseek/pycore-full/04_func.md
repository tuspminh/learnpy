Chào bạn! Bài 3 đã có nhiều kiến thức mới - tôi hy vọng bạn đã thực hành và nắm vững! Bây giờ chúng ta bước vào một trong những chủ đề **QUAN TRỌNG NHẤT**: Hàm (Function).

---

# 📘 BÀI 4: HÀM (FUNCTION) - XƯƠNG SỐNG CỦA LẬP TRÌNH

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu tại sao cần dùng hàm và cách tổ chức code
- Tạo hàm với tham số, đối số, giá trị mặc định
- Phân biệt tham trị và tham chiếu
- Sử dụng `*args` và `**kwargs` - kỹ năng linh hoạt
- Viết hàm với `return` và hiểu scope (phạm vi biến)
- Tạo Lambda function (hàm ẩn danh)

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Hàm là gì? Tại sao cần dùng?

**Hàm = Một khối code được đặt tên, thực hiện một tác vụ cụ thể.**

```python
# KHÔNG dùng hàm (code lặp lại, khó sửa)
print("Tính chu vi hình tròn bán kính 5:")
chu_vi_1 = 2 * 3.14 * 5
print(chu_vi_1)

print("Tính chu vi hình tròn bán kính 10:")
chu_vi_2 = 2 * 3.14 * 10
print(chu_vi_2)


# CÓ dùng hàm (tái sử dụng, dễ bảo trì)
def tinh_chu_vi_hinh_tron(ban_kinh):
    """Tính chu vi hình tròn với bán kính cho trước"""
    return 2 * 3.14 * ban_kinh


print(tinh_chu_vi_hinh_tron(5))
print(tinh_chu_vi_hinh_tron(10))
```

**Lợi ích của hàm:**
- ✅ **Tái sử dụng** code (DRY - Don't Repeat Yourself)
- ✅ **Dễ đọc, dễ bảo trì** (code có tổ chức)
- ✅ **Dễ test** (kiểm tra từng hàm độc lập)
- ✅ **Che giấu chi tiết** (người dùng chỉ cần biết đầu vào - đầu ra)

---

### 1.2. Cú pháp cơ bản

```python
def ten_ham(tham_so1, tham_so2, ...):
    """Docstring - Giải thích chức năng của hàm"""
    # Code thực thi
    return ket_qua  # Có thể có hoặc không

# Gọi hàm
ket_qua = ten_ham(doi_so1, doi_so2, ...)
```

**Ví dụ chi tiết:**
```python
def tinh_binh_phuong(so):
    """Tính bình phương của một số"""
    return so**2


# Gọi hàm
print(tinh_binh_phuong(5))  # 25
print(tinh_binh_phuong(10))  # 100


# Hàm không có return (trả về None)
def in_chao_ho_ten(ten):
    """In ra lời chào - không trả về gì"""
    print(f"Xin chào {ten}!")


in_chao_ho_ten("Nam")  # In: Xin chào Nam!
```

**Docstring - Ghi chú cho hàm:**
```python
def tinh_tong_2_so(a, b):
    """
    Tính tổng của 2 số

    Parameters:
    a (int|float): Số thứ nhất
    b (int|float): Số thứ hai

    Returns:
    int|float: Tổng của a và b

    Example:
    >>> tinh_tong_2_so(3, 5)
    8
    """
    return a + b


# Xem docstring
print(tinh_tong_2_so.__doc__)
help(tinh_tong_2_so)
```

---

### 1.3. Tham số và Đối số (Parameter vs Argument)

**Các loại tham số (Parameter):**

```python
# 1. Tham số bắt buộc (positional arguments)
def tinh_dien_tich_chu_nhat(dai, rong):
    return dai * rong


print(tinh_dien_tich_chu_nhat(5, 3))  # 15


# 2. Tham số mặc định (default parameters)
def chao_ho_ten(ten, loi_chao="Xin chào"):
    print(f"{loi_chao} {ten}!")


chao_ho_ten("Mai")  # Xin chào Mai!
chao_ho_ten("Mai", "Chào buổi sáng")  # Chào buổi sáng Mai!

# 3. Tham số keyword arguments (gọi hàm với tên tham số)
tinh_dien_tich_chu_nhat(rong=3, dai=5)  # 15 (không cần theo thứ tự)


# 4. Số lượng tham số không xác định
def tinh_tong(*args):  # *args = tuple chứa các đối số
    return sum(args)


print(tinh_tong(1, 2, 3))  # 6
print(tinh_tong(1, 2, 3, 4))  # 10


def in_thong_tin(**kwargs):  # **kwargs = dict chứa key-value
    for key, value in kwargs.items():
        print(f"{key}: {value}")


in_thong_tin(ten="An", tuoi=20, que="Hà Nội")
# ten: An
# tuoi: 20
# que: Hà Nội


# 5. Kết hợp tất cả (thứ tự: positional, *args, default, **kwargs)
def ham_phuc_tap(a, b, *args, c=10, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"c={c}")
    print(f"kwargs={kwargs}")
```

---

### 1.4. Scope (Phạm vi biến) - CỰC KỲ QUAN TRỌNG

```python
# Biến toàn cục (global)
x = 100


def ham1():
    # Biến cục bộ (local)
    y = 50
    print(f"Trong hàm: x={x}, y={y}")


ham1()  # Trong hàm: x=100, y=50
# print(y)  # Lỗi: y không tồn tại bên ngoài hàm

# Sửa biến toàn cục trong hàm (cần global)
count = 0


def tang_count():
    global count
    count += 1
    return count


print(tang_count())  # 1
print(tang_count())  # 2
print(tang_count())  # 3

# LEGB Rule: Local → Enclosing → Global → Built-in
x = 100  # Global


def outer():
    x = 50  # Enclosing

    def inner():
        x = 10  # Local
        print(f"inner: {x}")

    inner()
    print(f"outer: {x}")


outer()  # inner: 10, outer: 50
print(f"global: {x}")  # global: 100
```

---

### 1.5. Tham trị vs Tham chiếu (Pass by value vs Pass by reference)

**Quan trọng:** Python truyền tham chiếu (reference) nhưng có sự khác biệt:

```python
# 1. Immutable (int, str, tuple, bool) - Không thay đổi bên ngoài
def sua_so(so):
    so = so + 10
    print(f"Trong hàm: {so}")


n = 5
sua_so(n)  # Trong hàm: 15
print(n)  # 5 (không đổi)


# 2. Mutable (list, dict, set) - Thay đổi được bên ngoài
def them_phan_tu(ds):
    ds.append(99)
    print(f"Trong hàm: {ds}")


my_list = [1, 2, 3]
them_phan_tu(my_list)  # Trong hàm: [1, 2, 3, 99]
print(my_list)  # [1, 2, 3, 99] (đã đổi)


# Để không ảnh hưởng đến gốc, hãy COPY
def xu_ly_khong_anh_huong(ds):
    ds_copy = ds.copy()  # Tạo bản sao
    ds_copy.append(99)
    return ds_copy


my_list2 = [1, 2, 3]
new_list = xu_ly_khong_anh_huong(my_list2)
print(my_list2)  # [1, 2, 3] (không đổi)
print(new_list)  # [1, 2, 3, 99]
```

---

### 1.6. Lambda Function - Hàm 1 dòng

```python
# Cú pháp: lambda tham_so: biểu_thức

# Hàm thường
def binh_phuong(x):
    return x**2


# Lambda tương đương
binh_phuong_lambda = lambda x: x**2

print(binh_phuong_lambda(5))  # 25

# Lambda thường dùng với hàm built-in
ds = [1, 2, 3, 4, 5]

# map: áp dụng hàm cho từng phần tử
ds_binh_phuong = list(map(lambda x: x**2, ds))
print(ds_binh_phuong)  # [1, 4, 9, 16, 25]

# filter: lọc phần tử
ds_chan = list(filter(lambda x: x % 2 == 0, ds))
print(ds_chan)  # [2, 4]

# sorted: sắp xếp theo key
sinh_vien = [
    {"ten": "An", "tuoi": 20},
    {"ten": "Bình", "tuoi": 18},
    {"ten": "Châu", "tuoi": 22},
]
sap_xep = sorted(sinh_vien, key=lambda x: x["tuoi"])
print(sap_xep)  # Sắp xếp theo tuổi tăng dần
```

---

### 1.7. Hàm với khởi tạo mặc định (Mutable Default Argument)

**⚠️ LƯU Ý QUAN TRỌNG:** Không dùng mutable (list, dict) làm tham số mặc định!

```python
# ❌ SAI - Gây lỗi khó tìm
def them_sai(item, ds=[]):  # ds được tạo 1 lần duy nhất
    ds.append(item)
    return ds


print(them_sai(1))  # [1]
print(them_sai(2))  # [1, 2]  <- BẤT NGỜ!
print(them_sai(3))  # [1, 2, 3]


# ✅ ĐÚNG
def them_dung(item, ds=None):
    if ds is None:
        ds = []  # Tạo mới mỗi lần gọi
    ds.append(item)
    return ds


print(them_dung(1))  # [1]
print(them_dung(2))  # [2]  <- Sạch sẽ!
print(them_dung(3))  # [3]
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống xử lý chuỗi

```python
def chuan_hoa_chuoi(chuoi):
    """Chuẩn hóa chuỗi: bỏ khoảng trắng thừa, viết hoa chữ cái đầu"""
    # Bỏ khoảng trắng đầu cuối
    chuoi = chuoi.strip()
    # Viết hoa chữ cái đầu mỗi từ
    return " ".join([tu.capitalize() for tu in chuoi.split()])


def lay_tu_dau(chuoi, so_tu=1):
    """Lấy n từ đầu tiên của chuỗi"""
    cac_tu = chuoi.split()
    return " ".join(cac_tu[:so_tu])


# Test
ho_ten = "  nguyễn   văn   an  "
print(chuan_hoa_chuoi(ho_ten))  # "Nguyễn Văn An"
print(lay_tu_dau(ho_ten, 2))  # "Nguyễn Văn"
```

---

### Ví dụ 2: Công cụ xử lý danh sách

```python
def tinh_thong_ke(ds_so):
    """
    Tính các thống kê cơ bản của một danh sách số

    Returns:
    dict: {"min": min, "max": max, "avg": avg, "sum": sum, "count": count}
    """
    if not ds_so:  # Kiểm tra rỗng
        return None

    return {
        "min": min(ds_so),
        "max": max(ds_so),
        "avg": sum(ds_so) / len(ds_so),
        "sum": sum(ds_so),
        "count": len(ds_so),
    }


def loc_so_theo_dieu_kien(ds, dieu_kien):
    """
    Lọc danh sách theo điều kiện

    Parameters:
    ds: danh sách số
    dieu_kien: function nhận 1 tham số, trả về bool
    """
    return [x for x in ds if dieu_kien(x)]


# Test
so_lieu = [10, 20, 30, 40, 50, 60]
thong_ke = tinh_thong_ke(so_lieu)
print(thong_ke)

# Lọc số chẵn
so_chan = loc_so_theo_dieu_kien(so_lieu, lambda x: x % 2 == 0)
print(so_chan)  # [10, 20, 30, 40, 50, 60] (tất cả đều chẵn)

# Lọc số > 30
so_lon = loc_so_theo_dieu_kien(so_lieu, lambda x: x > 30)
print(so_lon)  # [40, 50, 60]
```

---

### Ví dụ 3: Calculator với decorator (Bonus)

```python
import time


def do_thoi_gian(func):
    """Decorator đo thời gian chạy của hàm"""

    def wrapper(*args, **kwargs):
        start = time.time()
        ket_qua = func(*args, **kwargs)
        end = time.time()
        print(f"Hàm {func.__name__} chạy trong {end - start:.6f} giây")
        return ket_qua

    return wrapper


@do_thoi_gian
def tinh_giai_thua(n):
    """Tính giai thừa"""
    if n == 0:
        return 1
    return n * tinh_giai_thua(n - 1)


print(tinh_giai_thua(10))  # 3628800
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết hàm `kiem_tra_so_nguyen_to(n)` trả về True nếu n là số nguyên tố.

**Bài 2:** Viết hàm `tinh_tong_cac_uoc(n)` tính tổng các ước số dương của n.

**Bài 3:** Viết hàm `doi_so_la_ma(n)` chuyển đổi số từ 1-3999 sang số La Mã.
*Gợi ý:* 4 = IV, 9 = IX, 40 = XL, 90 = XC, 400 = CD, 900 = CM

**Bài 4:** Viết hàm `kiem_tra_chuoi_doi_xung(chuoi)` kiểm tra chuỗi có đối xứng không.
Ví dụ: "radar" → True, "python" → False

**Bài 5:** Viết hàm `tim_ucln(a, b)` tìm ước chung lớn nhất của 2 số (thuật toán Euclid).

**Bài 6:** Viết hàm `tao_tu_dien_tu_2_list(keys, values)` tạo dict từ 2 list.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Viết hàm `tinh_diem_trung_binh(*args, **kwargs)`:
- *args: điểm các môn học (bắt buộc)
- **kwargs: trọng số của từng môn
- Tính điểm trung bình có trọng số
- Nếu không có trọng số, tính trung bình cộng

**Bài 8:** Viết hàm `phan_tich_cau_chuoi(chuoi)` trả về dict:
```python
{
    "so_tu": 5,
    "so_ky_tu": 25,
    "so_nguyen_am": 7,
    "tu_dai_nhat": "programming",
    "tu_ngan_nhat": "is",
}
```

**Bài 9:** Viết hàm `tao_ma_tran(m, n)` tạo ma trận m×n với:
- Hàng i: có số i (bắt đầu từ 1)
- Ví dụ m=3, n=4: [[1,1,1,1], [2,2,2,2], [3,3,3,3]]

**Bài 10:** Viết hàm `giai_he_phuong_trinh(a1, b1, c1, a2, b2, c2)` giải hệ 2 phương trình:
```
a1*x + b1*y = c1
a2*x + b2*y = c2
```
Trả về tuple (x, y) hoặc None nếu vô nghiệm.

---

## 🏗️ MINI-PROJECT: HỆ THỐNG TÍNH TOÁN TÀI CHÍNH CÁ NHÂN

```python
"""
Xây dựng hệ thống quản lý chi tiêu cá nhân với các hàm:

1. them_giao_dich(loai, so_tien, mo_ta)
   - loai: 'thu' hoặc 'chi'
   - Lưu vào danh sách giao dịch

2. tinh_tong_thu()
3. tinh_tong_chi()
4. tinh_so_du()

5. thong_ke_theo_loai(loai_can_thong_ke)
   - Trả về dict: {"ăn uống": 100000, "di lại": 50000, ...}

6. tim_kiem_giao_dich(tu_khoa)
   - Tìm theo mô tả

7. xuat_bao_cao()
   - In ra báo cáo đẹp mắt

Gợi ý cấu trúc giao dịch:
{
    "id": 1,
    "loai": "chi",
    "so_tien": 50000,
    "mo_ta": "Ăn trưa",
    "danh_muc": "ăn uống",
    "ngay": "2026-07-27"
}
"""

# Hãy tự viết code!
```

---

## ✅ KIỂM TRA CODE CHUYÊN NGHIỆP

- [ ] Mỗi hàm có docstring rõ ràng
- [ ] Tên hàm mô tả đúng hành động (động từ)
- [ ] Sử dụng type hints (tùy chọn nhưng khuyến khích)
- [ ] Không có side effect không mong muốn (không sửa biến global)
- [ ] Xử lý trường hợp đặc biệt (input rỗng, None)
- [ ] Hàm đủ ngắn (một chức năng duy nhất)
- [ ] Sử dụng `*args` và `**kwargs` đúng lúc
- [ ] Không dùng mutable default arguments

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Viết function decorator kiểm tra kiểu dữ liệu đầu vào
@type_check(int, int)
def tinh_tong(a, b):
    return a + b


tinh_tong(5, 3)  # ✅ OK
tinh_tong(5, "3")  # ❌ TypeError: b phải là int

# Hãy tự viết decorator type_check!
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Công thức/Ví dụ |
|-----------|-----------------|
| **Hàm cơ bản** | `def ten_ham():` |
| **Return** | `return ket_qua` |
| **Tham số mặc định** | `def ham(a, b=10):` |
| ***args** | `def ham(*args):` → tuple |
| ****kwargs** | `def ham(**kwargs):` → dict |
| **Lambda** | `lambda x: x**2` |
| **Scope** | Local → Enclosing → Global → Built-in |
| **Mutable default** | Dùng `ds=None` thay vì `ds=[]` |

---

**Bây giờ hãy CODE và gửi cho tôi để review!** 💪

*Bài 5 sẽ dạy bạn về Xử lý ngoại lệ (Exception) - cách viết code an toàn, không bị lỗi giữa chừng!*