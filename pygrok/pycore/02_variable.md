**Bài 2: Biến – Kiểu dữ liệu – Toán tử**

Đây là nền tảng quan trọng nhất. Hiểu rõ phần này thì mọi thứ sau sẽ dễ hơn rất nhiều.

---

### 1. Biến (Variable)

Biến là “hộp” chứa dữ liệu. Trong Python bạn **không cần khai báo kiểu** trước.

```python
ten = "Nguyễn Văn A"  # chuỗi
tuoi = 25  # số nguyên
chieu_cao = 1.75  # số thực
da_hoc_python = True  # boolean
```

**Quy tắc đặt tên biến (bắt buộc nhớ):**
- Chỉ dùng chữ cái, số và dấu `_`
- Không bắt đầu bằng số
- Không dùng từ khóa của Python (`if`, `for`, `class`…)
- Nên dùng `snake_case` (chữ thường + gạch dưới)

```python
# Tốt
ho_ten = "An"
diem_trung_binh = 8.5

# Xấu
HoTen = "An"          # không theo chuẩn Python
2ten = "An"           # lỗi
class = "Python"      # từ khóa → lỗi
```

---

### 2. Các kiểu dữ liệu cơ bản

| Kiểu       | Ví dụ                  | Mô tả                          |
|------------|------------------------|--------------------------------|
| `int`      | `10`, `-5`, `0`        | Số nguyên                      |
| `float`    | `3.14`, `-0.5`, `2.0`  | Số thực                        |
| `str`      | `"Hello"`, `'Python'`  | Chuỗi ký tự                    |
| `bool`     | `True`, `False`        | Đúng / Sai                     |
| `NoneType` | `None`                 | Không có giá trị               |

Kiểm tra kiểu dữ liệu:

```python
x = 10
print(type(x))  # <class 'int'>

y = "Python"
print(type(y))  # <class 'str'>
```

---

### 3. Ép kiểu (Type Casting)

```python
a = "123"
b = int(a)  # chuyển chuỗi → số nguyên
c = float(a)  # → số thực
d = str(456)  # số → chuỗi

print(b + 10)  # 133
print(d + "abc")  # 456abc
```

**Lưu ý:** Không phải lúc nào cũng ép được.
```python
int("abc")  # → lỗi ValueError
```

---

### 4. Toán tử quan trọng

#### 4.1. Toán tử số học
```python
a = 10
b = 3

print(a + b)  # 13
print(a - b)  # 7
print(a * b)  # 30
print(a / b)  # 3.333... (luôn ra float)
print(a // b)  # 3     (chia lấy phần nguyên)
print(a % b)  # 1     (chia lấy dư)
print(a**b)  # 1000  (lũy thừa)
```

#### 4.2. Toán tử so sánh (kết quả là `True` / `False`)
```python
x = 5
y = 8

print(x == y)  # False
print(x != y)  # True
print(x < y)  # True
print(x >= y)  # False
```

#### 4.3. Toán tử logic
```python
a = True
b = False

print(a and b)  # False
print(a or b)  # True
print(not a)  # False
```

#### 4.4. Toán tử gán
```python
x = 10
x += 5  # tương đương x = x + 5 → 15
x -= 3  # 12
x *= 2  # 24
x /= 4  # 6.0
```

---

### 5. Một số mẹo hay dùng

```python
# Gán nhiều biến cùng lúc
a, b, c = 1, 2, 3

# Hoán đổi giá trị
x, y = 10, 20
x, y = y, x  # x = 20, y = 10

# Kiểm tra kiểu nhanh
print(isinstance(10, int))  # True
print(isinstance("hi", str))  # True
```

---

### Bài tập Bài 2 (làm hết rồi gửi lại)

**Bài 1:**  
Tạo các biến sau và in ra kiểu dữ liệu của chúng:
- `ten` (chuỗi)
- `tuoi` (số nguyên)
- `diem` (số thực)
- `da_tot_nghiep` (boolean)

**Bài 2:**  
Viết chương trình:
1. Nhập vào 2 số từ bàn phím
2. In ra tổng, hiệu, tích, thương, chia lấy dư, lũy thừa của 2 số đó

**Bài 3:**  
Cho đoạn code sau, đoán kết quả rồi chạy thử để kiểm tra:
```python
a = 15
b = 4
print(a // b)
print(a % b)
print(a**2)
print(a > 10 and b < 5)
print(not (a == 15))
```

**Bài 4 (nâng cao nhẹ):**  
Viết chương trình nhập chiều cao (m) và cân nặng (kg), tính BMI theo công thức:
```
BMI = cân nặng / (chiều cao ** 2)
```
In ra kết quả BMI (làm tròn 2 chữ số thập phân).

---

Làm xong gửi code + kết quả chạy cho tôi.  
Tôi sẽ chữa bài và mở **Bài 3: Câu lệnh điều kiện (if – elif – else)** ngay.

Cứ làm từ từ, hiểu rõ từng phần là được. Gửi bài tập khi sẵn sàng!