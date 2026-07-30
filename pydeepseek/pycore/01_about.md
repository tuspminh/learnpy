Chào bạn! Tôi thấy bạn đã sẵn sàng bắt tay vào **Bài 1** ngay lập luận. Tuyệt vời!

Vì bạn chưa trả lời 3 câu hỏi về trình độ nền, tôi sẽ giả định bạn là **người mới bắt đầu hoàn toàn** và thiết kế bài học chi tiết, tỉ mỉ nhất.

---

# 📘 BÀI 1: BIẾN, KIỂU DỮ LIỆU & TOÁN TỬ

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu biến là "hộp chứa" dữ liệu trong bộ nhớ
- Phân biệt được 4 kiểu dữ liệu cơ bản: `int`, `float`, `str`, `bool`
- Ép kiểu (chuyển đổi) giữa các kiểu dữ liệu
- Sử dụng thành thạo `print()` và `input()`
- Áp dụng toán tử số học, so sánh, logic

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Biến (Variable) là gì?

Biến là **tên** đại diện cho một vùng nhớ, nơi chứa giá trị.

```python
# Cú pháp: tên_biến = giá_trị
tuoi = 25  # số nguyên
diem_tb = 8.5  # số thực
ten = "Nguyen Van A"  # chuỗi văn bản
sinh_vien = True  # đúng/sai
```

**Quy tắc đặt tên biến:**
- Chỉ gồm chữ cái (a-z, A-Z), chữ số (0-9), dấu gạch dưới `_`
- Không bắt đầu bằng chữ số
- Phân biệt chữ hoa/thường (`age` ≠ `Age`)
- Không trùng với từ khóa của Python (`if`, `for`, `while`, `class`...)

**Quy ước PEP8 (code chuyên nghiệp):**
```python
# ✅ Đúng
ten_khach_hang = "Mai"  # snake_case cho biến thông thường
PI = 3.14  # CHỮ HOA cho hằng số
so_luong_san_pham = 10

# ❌ Sai (không theo chuẩn)
tenKhachHang = "Mai"  # Không dùng camelCase (trừ class)
SoLuong = 10  # Không viết hoa tùy tiện
```

---

### 1.2. Các kiểu dữ liệu cơ bản

| Kiểu | Từ khóa | Ví dụ | Giải thích |
|------|---------|-------|------------|
| **Số nguyên** | `int` | `18`, `-5`, `1000` | Không có dấu thập phân |
| **Số thực** | `float` | `3.14`, `-0.5`, `2.0` | Có dấu thập phân |
| **Chuỗi** | `str` | `"Xin chào"`, `'Python'` | Dấu nháy đơn hoặc kép |
| **Đúng/Sai** | `bool` | `True`, `False` | Chỉ 2 giá trị |

**Kiểm tra kiểu dữ liệu với `type()`:**
```python
print(type(10))  # <class 'int'>
print(type(3.14))  # <class 'float'>
print(type("Hello"))  # <class 'str'>
print(type(True))  # <class 'bool'>
```

---

### 1.3. Nhập - Xuất dữ liệu

**Xuất dữ liệu với `print()`:**
```python
print("Xin chào!")  # In chuỗi
print(2024)  # In số
print("Tuổi:", 25)  # In nhiều giá trị, tự động cách nhau bằng khoảng trắng

# f-string (cách viết hiện đại - khuyến khích dùng)
ten = "Hùng"
nam_sinh = 2000
print(f"Tôi tên là {ten}, sinh năm {nam_sinh}")  # Tôi tên là Hùng, sinh năm 2000
```

**Nhập dữ liệu với `input()`:**
```python
# input() luôn trả về kiểu str (chuỗi)
ten = input("Nhập tên của bạn: ")  # Người dùng nhập "An" → ten = "An"
nam_sinh_str = input(
    "Nhập năm sinh: "
)  # Người dùng nhập "2000" → "2000" (là chuỗi, không phải số!)
```

⚠️ **LƯU Ý QUAN TRỌNG:** Mọi thứ nhập từ bàn phím qua `input()` đều là **chuỗi (str)**. Muốn làm toán, phải ép sang số.

---

### 1.4. Ép kiểu (Type Casting)

Chuyển đổi giữa các kiểu dữ liệu:

```python
# Ép sang số nguyên (int)
so_nguyen = int("123")  # 123
so_nguyen = int(3.9)  # 3 (cắt bỏ phần thập phân, KHÔNG làm tròn)

# Ép sang số thực (float)
so_thuc = float("3.14")  # 3.14
so_thuc = float(5)  # 5.0

# Ép sang chuỗi (str) - mọi thứ đều thành chuỗi
chuoi = str(100)  # "100"
chuoi = str(3.14)  # "3.14"

# Ép sang bool - quy tắc: 0, "", None, [] là False, còn lại là True
bool(0)  # False
bool(1)  # True
bool("")  # False
bool("Python")  # True
```

**Ví dụ thực tế:** Tính tuổi từ năm sinh
```python
ten = input("Tên bạn là gì? ")
nam_sinh_str = input("Bạn sinh năm bao nhiêu? ")

# Ép từ chuỗi sang số nguyên
nam_sinh = int(nam_sinh_str)
tuoi = 2026 - nam_sinh  # Năm hiện tại là 2026

print(f"Chào {ten}, năm nay bạn {tuoi} tuổi!")
```

---

### 1.5. Toán tử trong Python

**Toán tử số học:**
| Toán tử | Ý nghĩa | Ví dụ | Kết quả |
|---------|---------|-------|---------|
| `+` | Cộng | `5 + 3` | `8` |
| `-` | Trừ | `5 - 3` | `2` |
| `*` | Nhân | `5 * 3` | `15` |
| `/` | Chia (luôn trả về float) | `5 / 2` | `2.5` |
| `//` | Chia lấy nguyên | `5 // 2` | `2` |
| `%` | Chia lấy dư (Modulo) | `5 % 2` | `1` |
| `**` | Lũy thừa | `2 ** 3` | `8` |

**Toán tử so sánh:** (trả về `bool`)
```python
==    # bằng (so sánh giá trị)
!=    # khác
>     # lớn hơn
<     # nhỏ hơn
>=    # lớn hơn hoặc bằng
<=    # nhỏ hơn hoặc bằng
```

**Toán tử logic:** (trả về `bool`)
```python
and   # VÀ: cả 2 đều đúng
or    # HOẶC: 1 trong 2 đúng
not   # PHỦ ĐỊNH: đảo ngược True ↔ False
```

**Ví dụ kết hợp:**
```python
tuoi = 20
co_giay_to = True

# Người đủ tuổi (>=18) VÀ có giấy tờ
du_dieu_kien = (tuoi >= 18) and co_giay_to  # True

# Điểm thi: đạt nếu >=5 HOẶC được ưu tiên
diem = 4.5
duoc_uu_tien = False
dau = (diem >= 5) or duoc_uu_tien  # False
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Tính tiền tip nhà hàng

```python
# Bước 1: Nhập thông tin
hoa_don_str = input("Nhập số tiền hóa đơn (VNĐ): ")
phan_tram_tip_str = input("Nhập % tip bạn muốn (vd: 10): ")

# Bước 2: Ép kiểu
hoa_don = float(hoa_don_str)
phan_tram_tip = float(phan_tram_tip_str)

# Bước 3: Tính toán
tien_tip = hoa_don * (phan_tram_tip / 100)
tong_thanh_toan = hoa_don + tien_tip

# Bước 4: In kết quả (làm tròn 2 chữ số thập phân)
print(f"Hóa đơn: {hoa_don:,.0f} VNĐ")
print(f"Tiền tip ({phan_tram_tip}%): {tien_tip:,.0f} VNĐ")
print(f"Tổng cộng: {tong_thanh_toan:,.0f} VNĐ")
```

### Ví dụ 2: Kiểm tra số chẵn/lẻ

```python
so = int(input("Nhập một số nguyên: "))

# % 2: nếu dư 0 là chẵn, dư 1 là lẻ
la_so_chan = so % 2 == 0

print(f"Số {so} là số chẵn? {la_so_chan}")
print(f"Bình phương của {so} là {so**2}")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (Làm trên máy tính của bạn)

### 📌 Bài tập bắt buộc (8 bài)

**Bài 1:** Tạo 3 biến lần lượt là số nguyên, số thực, chuỗi. In ra kiểu dữ liệu của từng biến.

**Bài 2:** Viết chương trình yêu cầu nhập tên và quê quán, sau đó in ra: `"Xin chào [tên], bạn đến từ [quê]!"`

**Bài 3:** Nhập 2 số nguyên từ bàn phím, tính và in ra: tổng, hiệu, tích, thương (số thực), thương nguyên, số dư.

**Bài 4:** Nhập số đo 3 cạnh của hình chữ nhật (chiều dài, chiều rộng), tính và in ra diện tích và chu vi.

**Bài 5:** Viết chương trình kiểm tra một số nhập vào có phải là số âm, số 0 hay số dương (sử dụng so sánh, in ra bool tương ứng).

**Bài 6:** Nhập nhiệt độ (°C), chuyển sang °F theo công thức: `F = C * 9/5 + 32`.

**Bài 7:** Nhập số giây (0-86399), tính và in ra số giờ, phút, giây tương ứng. (Ví dụ: 3661 → 1 giờ 1 phút 1 giây)

**Bài 8:** Giả sử 1 USD = 25,500 VNĐ. Viết chương trình nhập số USD, đổi sang VNĐ và in ra.

---

### ⭐ Bài tập nâng cao (2 bài - thử sức)

**Bài 9:** Nhập số có 2 chữ số (10-99), in ra tổng các chữ số.  
*Gợi ý:* Số 47 → chữ số hàng chục = 47 // 10 = 4, hàng đơn vị = 47 % 10 = 7

**Bài 10:** Nhập 3 số a, b, c. Kiểm tra xem chúng có thể tạo thành 3 cạnh của một tam giác hay không?  
*Gợi ý:* Điều kiện: a + b > c và a + c > b và b + c > a

---

## 🏗️ MINI-PROJECT CUỐI BÀI

**Xây dựng ứng dụng "Máy tính đa năng"**

Yêu cầu:
1. Nhập số thứ nhất
2. Nhập số thứ hai
3. In ra bảng kết quả:

```
PHÉP TÍNH TRÊN 2 SỐ
================================
[10] + [5] = 15
[10] - [5] = 5
[10] * [5] = 50
[10] / [5] = 2.0
[10] // [5] = 2
[10] % [5] = 0
[10] ** [5] = 100000
================================
```

---

## ✅ HƯỚNG DẪN TỰ REVIEW

Sau khi làm xong, hãy tự kiểm tra:
- [ ] Đặt tên biến đúng PEP8 (snake_case)
- [ ] Sử dụng f-string thay vì cộng chuỗi bằng `+`
- [ ] Ép kiểu đúng cách (input → int/float)
- [ ] Code có comment giải thích các bước chính
- [ ] Chạy thử với ít nhất 3 bộ dữ liệu khác nhau

---

## 💬 CÁCH TÔI HỖ TRỢ BẠN

1. **Gửi code của bạn lên** (paste vào đây), tôi sẽ:
   - Review lỗi cú pháp/logic
   - Gợi ý cải thiện code sạch hơn
   - Đề xuất cách viết ngắn gọn hơn (nếu có)

2. **Nếu gặp lỗi:** Copy toàn bộ thông báo lỗi (traceback), tôi sẽ giúp bạn debug chi tiết.

3. **Muốn thử thách hơn:** Yêu cầu thêm bài tập custom, tôi sẽ ra đề riêng theo mục tiêu của bạn.

---

**🔥 Bây giờ, hãy mở PyCharm/VS Code/Notepad lên và CODE NGAY!**  
Sau khi làm xong bài tập, gửi lên đây để tôi review nhé.

Chúc bạn học vui! 💪