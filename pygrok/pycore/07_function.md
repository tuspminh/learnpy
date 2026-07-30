**Bài 7: Hàm (Function)**

Hàm là một trong những khái niệm **quan trọng nhất** của lập trình.  
Hàm giúp bạn chia chương trình thành các khối nhỏ, dễ đọc, dễ bảo trì và tái sử dụng.

---

### 1. Định nghĩa và gọi hàm cơ bản

```python
def chao_hoi():
    print("Xin chào!")
    print("Chào mừng bạn đến với Python")


# Gọi hàm
chao_hoi()
chao_hoi()
```

---

### 2. Hàm có tham số (Parameter)

```python
def chao_hoi(ten):
    print(f"Xin chào {ten}!")


chao_hoi("An")
chao_hoi("Bình")
```

**Nhiều tham số:**
```python
def gioi_thieu(ten, tuoi, nganh):
    print(f"Tôi tên {ten}, {tuoi} tuổi, học ngành {nganh}")


gioi_thieu("An", 20, "CNTT")
```

---

### 3. Hàm có giá trị trả về (`return`)

```python
def tinh_tong(a, b):
    return a + b


ket_qua = tinh_tong(5, 7)
print(ket_qua)  # 12

print(tinh_tong(10, 20) * 2)  # 60
```

**Trả về nhiều giá trị (thực chất là tuple):**
```python
def tinh_toan(a, b):
    tong = a + b
    hieu = a - b
    tich = a * b
    return tong, hieu, tich


t, h, ti = tinh_toan(10, 3)
print(t, h, ti)  # 13 7 30
```

---

### 4. Tham số mặc định (Default Parameter)

```python
def chao_hoi(ten, loi_chao="Xin chào"):
    print(f"{loi_chao} {ten}!")


chao_hoi("An")  # Xin chào An!
chao_hoi("Bình", "Hello")  # Hello Bình!
```

**Lưu ý:** Tham số có mặc định phải đặt **sau** các tham số không có mặc định.

---

### 5. Keyword Arguments (Đối số theo tên)

```python
def thong_tin(ten, tuoi, thanh_pho):
    print(f"{ten} - {tuoi} tuổi - sống tại {thanh_pho}")


# Gọi theo vị trí
thong_tin("An", 20, "Hà Nội")

# Gọi theo tên (thứ tự không quan trọng)
thong_tin(tuoi=22, thanh_pho="Đà Nẵng", ten="Bình")
```

---

### 6. `*args` và `**kwargs` (Nâng cao nhưng rất hữu ích)

#### `*args` – nhận nhiều đối số vị trí (thành tuple)
```python
def tinh_tong(*args):
    tong = 0
    for so in args:
        tong += so
    return tong


print(tinh_tong(1, 2, 3))  # 6
print(tinh_tong(10, 20, 30, 40))  # 100
```

#### `**kwargs` – nhận nhiều đối số theo tên (thành dictionary)
```python
def in_thong_tin(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")


in_thong_tin(ten="An", tuoi=20, nganh="CNTT")
```

---

### 7. Phạm vi biến (Scope)

```python
x = 100  # biến toàn cục (global)


def demo():
    y = 50  # biến cục bộ (local)
    print(x)  # vẫn truy cập được biến global
    print(y)


demo()
# print(y)      → lỗi vì y chỉ tồn tại trong hàm
```

**Muốn thay đổi biến global bên trong hàm:**
```python
dem = 0


def tang_dem():
    global dem
    dem += 1


tang_dem()
print(dem)  # 1
```

**Khuyến nghị:** Hạn chế dùng `global`. Nên truyền tham số và dùng `return`.

---

### 8. Docstring (Chuỗi mô tả hàm)

```python
def tinh_bmi(can_nang, chieu_cao):
    """
    Tính chỉ số BMI.

    Parameters:
        can_nang (float): Cân nặng (kg)
        chieu_cao (float): Chiều cao (m)

    Returns:
        float: Giá trị BMI
    """
    return can_nang / (chieu_cao**2)


print(tinh_bmi.__doc__)
```

---

### 9. Hàm Lambda (hàm ẩn danh – giới thiệu nhanh)

```python
# Hàm thường
def vuong(x):
    return x**2


# Lambda tương đương
vuong = lambda x: x**2

print(vuong(5))  # 25

# Thường dùng với sorted, map, filter
diem = [("An", 8), ("Bình", 9), ("Chi", 7)]
diem_sap_xep = sorted(diem, key=lambda x: x[1], reverse=True)
print(diem_sap_xep)
```

---

### 10. Một số nguyên tắc viết hàm tốt

- Tên hàm nên là **động từ** hoặc cụm động từ (`tinh_tong`, `kiem_tra_chan_le`)
- Mỗi hàm chỉ nên làm **một việc** chính
- Hàm không nên quá dài (nên dưới 20–30 dòng)
- Nên có `return` rõ ràng
- Nên viết docstring cho hàm quan trọng

---

### Bài tập Bài 7

**Bài 1:**  
Viết hàm `chao_hoi(ten, nam_sinh)` in ra câu chào và tuổi hiện tại (năm 2026).

**Bài 2:**  
Viết hàm `kiem_tra_chan_le(n)` trả về `"Chẵn"` hoặc `"Lẻ"`.

**Bài 3:**  
Viết hàm `tinh_tong_danh_sach(ds)` nhận vào một list số và trả về tổng các phần tử.

**Bài 4:**  
Viết hàm `tim_max_min(ds)` trả về cả giá trị lớn nhất và nhỏ nhất của list (dùng `return` 2 giá trị).

**Bài 5:**  
Viết hàm `tinh_bmi(can_nang, chieu_cao)` trả về BMI.  
Sau đó viết thêm hàm `phan_loai_bmi(bmi)` trả về:
- < 18.5 → “Gầy”
- 18.5 – 24.9 → “Bình thường”
- 25 – 29.9 → “Thừa cân”
- ≥ 30 → “Béo phì”

**Bài 6 (nâng cao):**  
Viết hàm `thong_ke(*args)` nhận bao nhiêu số cũng được, trả về dictionary gồm:
- `"tong"`: tổng
- `"trung_binh"`: trung bình
- `"so_luong"`: số lượng số

---

Làm xong gửi code + kết quả chạy.  
Tôi sẽ chữa bài và mở **Bài 8: Xử lý chuỗi (String)** hoặc **Bài 9: Module & Package** (tùy bạn muốn đi theo hướng nào trước).

Hàm là “viên gạch” để xây dựng chương trình lớn. Cứ làm kỹ bài này nhé!