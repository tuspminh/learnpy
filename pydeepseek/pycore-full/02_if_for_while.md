Xin chào! Bạn đã hoàn thành Bài 1 rồi à? Tuyệt vời! Trước khi vào Bài 2, tôi khuyến khích bạn **gửi code Bài 1** lên để tôi review nhé - việc này giúp tôi biết bạn đang ở đâu và điều chỉnh tốc độ cho phù hợp.

Nhưng nếu bạn muốn tiếp tục luôn, chúng ta sang Bài 2 ngay!

---

# 📘 BÀI 2: CẤU TRÚC ĐIỀU KHIỂN (IF, FOR, WHILE)

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Ra quyết định bằng `if/elif/else`
- Lặp lại công việc với `for` và `while`
- Sử dụng `break`, `continue`, `pass` điều khiển vòng lặp
- Kết hợp cấu trúc điều khiển để giải quyết bài toán thực tế

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Câu lệnh điều kiện `if/elif/else`

**Cú pháp cơ bản:**
```python
if điều_kiện_1:
    # Code thực thi nếu điều_kiện_1 đúng
elif điều_kiện_2:
    # Code thực thi nếu điều_kiện_2 đúng
else:
    # Code thực thi nếu tất cả điều kiện đều sai
```

⚠️ **QUAN TRỌNG:** Python dùng **thụt lề (indentation)** để xác định khối code. Mặc định là 4 khoảng trắng.

**Ví dụ thực tế:**
```python
tuoi = int(input("Nhập tuổi của bạn: "))

if tuoi < 18:
    print("Bạn là trẻ em/thiếu niên")
elif tuoi < 60:
    print("Bạn là người trưởng thành")
else:
    print("Bạn là người cao tuổi")
```

**Viết gọn với toán tử 3 ngôi (Ternary):**
```python
# Cú pháp: giá_trị_đúng if điều_kiện else giá_trị_sai
tuoi = 20
trang_thai = "Đủ tuổi" if tuoi >= 18 else "Chưa đủ tuổi"
print(trang_thai)  # Đủ tuổi
```

---

### 1.2. Vòng lặp `for` (Biết trước số lần lặp)

**Duyệt qua một tập hợp (list, range, string...):**
```python
# Lặp qua range(start, stop, step)
for i in range(5):  # 0, 1, 2, 3, 4
    print(f"Lần lặp {i}")

for i in range(2, 10, 2):  # 2, 4, 6, 8
    print(i)

# Lặp qua chuỗi
ten = "Python"
for ky_tu in ten:
    print(ky_tu)  # P, y, t, h, o, n

# Lặp qua list
mon_hoc = ["Toán", "Lý", "Hóa"]
for mon in mon_hoc:
    print(f"Môn học: {mon}")
```

**Lấy cả chỉ số và giá trị với `enumerate()`:**
```python
danh_sach = ["a", "b", "c"]
for index, value in enumerate(danh_sach):
    print(f"Vị trí {index}: {value}")
```

---

### 1.3. Vòng lặp `while` (Không biết trước số lần lặp)

**Cú pháp:**
```python
while điều_kiện:
    # Code thực thi khi điều_kiện còn đúng
```

**Ví dụ:**
```python
# Đếm ngược từ 5 về 1
count = 5
while count > 0:
    print(count)
    count -= 1  # Giảm dần để tránh vòng lặp vô hạn
print("Hết!")

# Nhập đến khi nhận được số dương
so = -1
while so <= 0:
    so = int(input("Nhập số dương: "))
print(f"Bạn đã nhập: {so}")
```

---

### 1.4. Điều khiển vòng lặp: `break`, `continue`, `pass`

| Lệnh | Tác dụng | Ví dụ |
|------|----------|-------|
| `break` | **Thoát hẳn** vòng lặp | Dừng khi tìm thấy kết quả |
| `continue` | **Bỏ qua lần lặp hiện tại**, sang lần tiếp theo | Bỏ qua số chẵn |
| `pass` | **Không làm gì** (giữ chỗ) | Dành chỗ cho code sau |

```python
# break: tìm số đầu tiên chia hết cho 7 trong khoảng 1-100
for i in range(1, 101):
    if i % 7 == 0:
        print(f"Số đầu tiên chia hết cho 7: {i}")
        break  # Tìm thấy rồi, thoát!

# continue: in ra các số lẻ từ 1-10
for i in range(1, 11):
    if i % 2 == 0:
        continue  # Bỏ qua số chẵn
    print(i)  # 1, 3, 5, 7, 9


# pass: giữ chỗ cho function sẽ viết sau
def ham_se_viet_sau():
    pass  # Chưa viết nội dung nhưng không bị lỗi cú pháp
```

---

### 1.5. Lặp lồng nhau (Nested loops)

```python
# Bảng cửu chương 2-5
for i in range(2, 6):
    print(f"\nBảng cửu chương {i}:")
    for j in range(1, 11):
        print(f"{i} x {j} = {i * j}")
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống xếp loại học sinh

```python
diem = float(input("Nhập điểm trung bình (0-10): "))

if diem < 0 or diem > 10:
    print("Điểm không hợp lệ!")
elif diem >= 9.0:
    xep_loai = "Xuất sắc"
elif diem >= 8.0:
    xep_loai = "Giỏi"
elif diem >= 6.5:
    xep_loai = "Khá"
elif diem >= 5.0:
    xep_loai = "Trung bình"
else:
    xep_loai = "Yếu"

print(f"Điểm {diem} - Xếp loại: {xep_loai}")
```

---

### Ví dụ 2: Máy ATM đơn giản (Mô phỏng 3 lần rút)

```python
so_du = 1000000  # Số dư ban đầu
so_lan_rut = 0

while so_lan_rut < 3:
    so_tien = int(input("Nhập số tiền cần rút: "))
    
    if so_tien <= 0:
        print("Số tiền phải lớn hơn 0!")
        continue  # Không tính là lần rút
        
    if so_tien % 50000 != 0:
        print("Chỉ rút được bội số của 50,000đ!")
        continue
        
    if so_tien > so_du:
        print(f"Không đủ tiền! Số dư hiện tại: {so_du:,}đ")
    else:
        so_du -= so_tien
        so_lan_rut += 1
        print(f"Rút thành công! Số dư còn lại: {so_du:,}đ")
        
print("Hết lượt rút. Cảm ơn bạn đã sử dụng dịch vụ!")
```

---

### Ví dụ 3: Kiểm tra số nguyên tố

```python
n = int(input("Nhập số cần kiểm tra: "))

if n < 2:
    print(f"{n} KHÔNG phải số nguyên tố")
else:
    la_nguyen_to = True
    # Chỉ cần kiểm tra đến căn bậc 2 của n
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            la_nguyen_to = False
            break  # Tìm thấy ước số, không cần kiểm tra tiếp

    if la_nguyen_to:
        print(f"{n} LÀ số nguyên tố")
    else:
        print(f"{n} KHÔNG phải số nguyên tố")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Nhập 2 số và phép toán (`+`, `-`, `*`, `/`). In ra kết quả hoặc báo lỗi nếu phép toán không hợp lệ.

**Bài 2:** Nhập năm sinh, tính tuổi và phân loại:
- `0-5`: "Trẻ sơ sinh"
- `6-12`: "Học sinh cấp 1"
- `13-15`: "Học sinh cấp 2"
- `16-18`: "Học sinh cấp 3"
- `19-22`: "Sinh viên"
- `>=23`: "Người đi làm"

**Bài 3:** In ra tất cả số chẵn từ 1 đến 50 (dùng `for`).

**Bài 4:** In ra tổng các số từ 1 đến `n` (n nhập từ bàn phím) sử dụng `while`.

**Bài 5:** Nhập một chuỗi, đếm xem có bao nhiêu nguyên âm (`a, e, i, o, u`).

**Bài 6:** In ra hình tam giác vuông bằng dấu `*` với chiều cao nhập từ bàn phím.
```
Ví dụ n = 5:
*
**
***
****
*****
```

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Nhập 3 số, in ra số lớn nhất và số nhỏ nhất **mà không dùng hàm `max()`/`min()`**.

**Bài 8:** In ra dãy Fibonacci đến số thứ n.  
*Gợi ý:* F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)

**Bài 9:** Nhập 1 số nguyên dương, in ra các ước số của nó.

**Bài 10:** Trò chơi "Đoán số": Máy tính chọn ngẫu nhiên 1 số từ 1-100, bạn đoán đến khi đúng. Mỗi lần sai, máy báo "lớn hơn" hoặc "nhỏ hơn". Đếm số lần đoán.

---

## 🏗️ MINI-PROJECT: HỆ THỐNG ĐĂNG NHẬP CƠ BẢN

```python
"""
Yêu cầu:
1. Người dùng có 3 lần đăng nhập
2. Tài khoản mặc định: username="admin", password="123456"
3. Nếu đăng nhập đúng → chào mừng và hỏi "Tiếp tục? (y/n)"
4. Nếu sai → giảm số lần thử, báo lỗi
5. Sau 3 lần sai → khóa tài khoản
6. Dùng vòng lặp while và if/else
"""

# Code của bạn viết ở đây
```

---

## ✅ KIỂM TRA CODE CHUYÊN NGHIỆP

Sau khi làm xong, hãy tự kiểm tra:
- [ ] Thụt lề đều 4 khoảng trắng (không dùng Tab)
- [ ] Có xử lý input rỗng/không hợp lệ
- [ ] Sử dụng `break` đúng lúc (không lạm dụng)
- [ ] Không có vòng lặp vô hạn (kiểm tra điều kiện `while`)
- [ ] Tên biến mô tả rõ ràng (`so_lan_thu` thay vì `i`)

---

## 🔥 THỬ THÁCH BẠN (Bonus)

**Thử thách:** Viết chương trình vẽ hình kim cương với độ cao nhập vào (số lẻ):
```
Ví dụ n = 5:
  *
 ***
*****
 ***
  *
```
*Gợi ý:* Chia làm 2 nửa: trên và dưới.

---

## 💬 CÁCH TÔI HỖ TRỢ

1. **Gửi code bài tập** → Tôi review:
   - Sửa lỗi logic
   - Tối ưu code (rút gọn nhưng vẫn dễ đọc)
   - Đề xuất cách viết Pythonic hơn

2. **Gặp lỗi không hiểu** → Copy paste lỗi, tôi giải thích tận gốc.

3. **Muốn thêm đề** → Tôi ra thêm bài tập theo mục tiêu của bạn.

---

**Hãy bắt tay vào code ngay! Nhớ gửi bài tập Bài 1 + Bài 2 cho tôi review nhé.** 💪

*Bài 3 sẵn sàng khi bạn hoàn thành Bài 2 - chúng ta sẽ học về List, Tuple, Set, Dict!*