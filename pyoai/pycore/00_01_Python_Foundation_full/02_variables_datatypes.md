# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 2: Biến (Variables), Kiểu dữ liệu (Data Types) và Bộ nhớ trong Python

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu biến thực sự là gì (không chỉ biết cách khai báo).
> - Hiểu cách Python quản lý bộ nhớ.
> - Thành thạo các kiểu dữ liệu cơ bản.
> - Biết cách kiểm tra kiểu dữ liệu.
> - Biết ép kiểu đúng cách.
> - Biết quy tắc đặt tên biến theo chuẩn PEP 8.
> - Tránh các lỗi phổ biến của người mới.
> - Làm quen với tư duy lập trình chuyên nghiệp.

---

# 1. Biến là gì?

Rất nhiều tài liệu nói:

> "Biến là nơi lưu dữ liệu."

Cách giải thích này **chưa hoàn toàn chính xác**.

Trong Python:

> **Biến là một tên (name) dùng để tham chiếu (reference) đến một đối tượng (object) trong bộ nhớ.**

Ví dụ:

```text-x-trilium-auto
name = "Garden"
```

Không phải:

```text-x-trilium-auto
name chứa "Garden"
```

Mà là:

```text-x-trilium-auto
name
   │
   ▼
+-----------+
| "Garden"  |
+-----------+
```

Nghĩa là:

- `"Garden"` là một đối tượng trong bộ nhớ.
- `name` chỉ là tên tham chiếu đến đối tượng đó.

Đây là điểm khác biệt rất quan trọng giữa Python và nhiều ngôn ngữ khác.

---

# 2. Mọi thứ trong Python đều là Object

Trong Python:

```text-x-trilium-auto
100
```

là Object.

```text-x-trilium-auto
3.14
```

là Object.

```text-x-trilium-auto
True
```

là Object.

```text-x-trilium-auto
"Hello"
```

là Object.

```text-x-trilium-auto
[1, 2, 3]
```

cũng là Object.

Ngay cả hàm cũng là Object:

```text-x-trilium-auto
print
```

là Object.

Đây là lý do Python rất linh hoạt.

---

# 3. Gán biến (Assignment)

Ví dụ:

```text-x-trilium-auto
age = 20
```

Python thực hiện:

### Bước 1

Tạo Object

```text-x-trilium-auto
20
```

↓

### Bước 2

Cho biến `age` trỏ tới Object đó.

```text-x-trilium-auto
age
 │
 ▼
20
```

---

Nếu:

```text-x-trilium-auto
score = age
```

thì:

```text-x-trilium-auto
age ─┐
     │
     ▼
    20
     ▲
     │
score
```

Lúc này:

Hai biến cùng tham chiếu đến **một đối tượng**.

---

# 4. Gán lại biến

```text-x-trilium-auto
age = 20

age = 30
```

Điều gì xảy ra?

```text-x-trilium-auto
Ban đầu

age

↓

20
```

Sau đó

```text-x-trilium-auto
age

↓

30
```

Đối tượng `20` sẽ không còn được tham chiếu bởi `age`. Nếu không còn biến nào khác tham chiếu đến nó, Python sẽ tự giải phóng bộ nhớ sau này thông qua **Garbage Collector**.

---

# 5. Kiểm tra địa chỉ Object

Dùng:

```text-x-trilium-auto
id()
```

Ví dụ:

```text-x-trilium-auto
x = 100

print(id(x))
```

Ví dụ kết quả:

```text-x-trilium-auto
4372847360
```

Không quan trọng số cụ thể.

Điều quan trọng:

```text-x-trilium-auto
a = 100

b = a

print(id(a))
print(id(b))
```

Kết quả:

```text-x-trilium-auto
1938472

1938472
```

Hai biến đang tham chiếu cùng một object.

---

# 6. Kiểu dữ liệu (Data Types)

Python có rất nhiều kiểu dữ liệu.

Buổi này tập trung các kiểu cơ bản.

## int

```text-x-trilium-auto
age = 20
```

```text-x-trilium-auto
count = 1000
```

---

## float

```text-x-trilium-auto
pi = 3.14159
```

```text-x-trilium-auto
price = 99.9
```

---

## bool

```text-x-trilium-auto
True

False
```

Ví dụ

```text-x-trilium-auto
is_login = True
```

---

## str

```text-x-trilium-auto
name = "Garden"
```

---

# 7. Hàm type()

Kiểm tra kiểu dữ liệu.

```text-x-trilium-auto
name = "Garden"

print(type(name))
```

Kết quả

```text-x-trilium-auto
<class 'str'>
```

---

Ví dụ

```text-x-trilium-auto
print(type(10))
```

```text-x-trilium-auto
<class 'int'>
```

---

```text-x-trilium-auto
print(type(3.14))
```

```text-x-trilium-auto
<class 'float'>
```

---

# 8. Biến động kiểu (Dynamic Typing)

Python là ngôn ngữ **Dynamic Typing**.

Ví dụ

```text-x-trilium-auto
x = 10
```

Sau đó

```text-x-trilium-auto
x = "Hello"
```

Không lỗi.

Điều này rất tiện nhưng cũng đòi hỏi bạn đặt tên biến rõ ràng để tránh nhầm lẫn.

---

# 9. Quy tắc đặt tên biến

Đúng

```text-x-trilium-auto
student_name

total_price

user_age

phone_number
```

Sai

```text-x-trilium-auto
student-name

123abc

for

while
```

---

Theo chuẩn PEP 8

```text-x-trilium-auto
user_name
```

Không nên

```text-x-trilium-auto
UserName
```

hoặc

```text-x-trilium-auto
userName
```

cho tên biến.

---

# 10. Hằng số (Constant)

Python không có từ khóa `const`.

Theo quy ước:

```text-x-trilium-auto
PI = 3.14159

MAX_SIZE = 100
```

Viết IN HOA để nhắc rằng không nên thay đổi giá trị.

---

# 11. Ép kiểu (Type Casting)

## int()

```text-x-trilium-auto
int("100")
```

Ví dụ:

```text-x-trilium-auto
age = int("20")

print(age)
```

Kết quả:

```text-x-trilium-auto
20
```

---

## float()

```text-x-trilium-auto
price = float("19.99")

print(price)
```

---

## str()

```text-x-trilium-auto
score = 100

text = str(score)

print(text)
```

Kết quả:

```text-x-trilium-auto
100
```

---

## bool()

```text-x-trilium-auto
bool(1)
```

```text-x-trilium-auto
True
```

```text-x-trilium-auto
bool(0)
```

```text-x-trilium-auto
False
```

---

# 12. Các giá trị "Falsy"

Trong Python, một số giá trị được xem là **False** khi kiểm tra điều kiện:

```text-x-trilium-auto
False
0
0.0
''
""
[]
{}
()
set()
None
```

Ví dụ:

```text-x-trilium-auto
print(bool(""))
print(bool([]))
print(bool(0))
```

Kết quả:

```text-x-trilium-auto
False
False
False
```

Các giá trị khác thường được xem là **True**.

---

# 13. Đọc dữ liệu từ bàn phím

Dùng:

```text-x-trilium-auto
name = input("Tên của bạn: ")

print(name)
```

Lưu ý:

`input()` luôn trả về **chuỗi (**`**str**`**)**.

Ví dụ:

```text-x-trilium-auto
age = input("Tuổi: ")

print(type(age))
```

Kết quả:

```text-x-trilium-auto
<class 'str'>
```

Nếu muốn tính toán:

```text-x-trilium-auto
age = int(input("Tuổi: "))
```

---

# 14. Ghép chuỗi

Cách 1:

```text-x-trilium-auto
name = "Garden"

print("Xin chào " + name)
```

Cách 2 (khuyến nghị):

```text-x-trilium-auto
name = "Garden"

print(f"Xin chào {name}")
```

Đây gọi là **f-string**, là cách hiện đại và dễ đọc nhất.

---

# 15. Ví dụ thực tế

Giả sử bạn xây dựng ứng dụng quản lý sinh viên:

```text-x-trilium-auto
student_name = "Nguyễn Văn A"
student_age = 20
student_score = 8.5
is_active = True

print(f"Tên: {student_name}")
print(f"Tuổi: {student_age}")
print(f"Điểm: {student_score}")
print(f"Đang học: {is_active}")
```

Đây là cách tổ chức dữ liệu rõ ràng, dễ mở rộng.

---

# 16. Những lỗi phổ biến

### Lỗi 1: Quên ép kiểu

```text-x-trilium-auto
age = input("Tuổi: ")

print(age + 1)
```

Kết quả:

```text-x-trilium-auto
TypeError
```

Đúng:

```text-x-trilium-auto
age = int(input("Tuổi: "))

print(age + 1)
```

---

### Lỗi 2: Đặt tên biến khó hiểu

```text-x-trilium-auto
a = "Garden"
b = 20
c = True
```

Nên viết:

```text-x-trilium-auto
user_name = "Garden"
user_age = 20
is_active = True
```

---

### Lỗi 3: Ghi đè biến

```text-x-trilium-auto
print = "Hello"
```

Sau đó:

```text-x-trilium-auto
print("Python")
```

Sẽ báo lỗi vì bạn đã ghi đè hàm `print`. Tránh đặt tên biến trùng với các hàm dựng sẵn như `print`, `list`, `str`, `type`,...

---

# 17. Bài tập thực hành

## Bài 1

Tạo các biến:

- Họ tên
- Tuổi
- Chiều cao
- Đã tốt nghiệp hay chưa

In ra bằng f-string.

---

## Bài 2

Nhập tên từ bàn phím.

In:

```text-x-trilium-auto
Xin chào, <tên>!
```

---

## Bài 3

Nhập tuổi.

In tuổi sau 10 năm.

---

## Bài 4

Nhập bán kính hình tròn.

Tính diện tích:

```text-x-trilium-auto
S = π × r²
```

*Gợi ý:* Dùng `PI = 3.14159`.

---

## Bài 5

Nhập:

- Tên sản phẩm
- Đơn giá
- Số lượng

In hóa đơn đơn giản:

```text-x-trilium-auto
Tên sản phẩm: ...
Đơn giá: ...
Số lượng: ...
Thành tiền: ...
```

---

# Mini Project: Hồ sơ cá nhân

Viết chương trình `profile.py`:

1. Nhập:
  - Họ tên
  - Tuổi
  - Nghề nghiệp
  - Thành phố
  - Sở thích
2. In ra theo định dạng đẹp bằng f-string, ví dụ:

```text-x-trilium-auto
========== HỒ SƠ CÁ NHÂN ==========
Họ tên      : Nguyễn Văn A
Tuổi        : 25
Nghề nghiệp : Lập trình viên
Thành phố   : TP. Hồ Chí Minh
Sở thích    : Đọc sách, lập trình
===================================
```

---

# Tổng kết buổi 2

Hôm nay bạn đã học được:

- ✅ Bản chất của biến trong Python.
- ✅ Mọi thứ trong Python đều là object.
- ✅ Cách Python quản lý tham chiếu và bộ nhớ.
- ✅ Các kiểu dữ liệu cơ bản: `int`, `float`, `bool`, `str`.
- ✅ Hàm `type()` và `id()`.
- ✅ Ép kiểu với `int()`, `float()`, `str()`, `bool()`.
- ✅ Hàm `input()` và lưu ý về kiểu dữ liệu.
- ✅ Ghép chuỗi với **f-string**.
- ✅ Quy tắc đặt tên biến theo PEP 8.
- ✅ Những lỗi phổ biến và cách tránh.

### Chuẩn bị cho Buổi 3

Ở buổi tiếp theo, chúng ta sẽ học **toàn diện về Input/Output**: các tùy chọn nâng cao của `print()` (`sep`, `end`, `file`, `flush`), định dạng chuỗi, f-string chuyên sâu, đọc dữ liệu từ nhiều nguồn và xây dựng các chương trình tương tác với người dùng theo cách chuyên nghiệp.
