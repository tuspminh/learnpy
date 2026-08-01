# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 9: Làm chủ Hàm (Functions) - Nền tảng của lập trình chuyên nghiệp (Phần 1)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của hàm (Function).
> - Biết tại sao phải chia chương trình thành các hàm.
> - Thành thạo cách định nghĩa và gọi hàm.
> - Hiểu tham số (Parameters) và đối số (Arguments).
> - Thành thạo `return`.
> - Hiểu phạm vi biến (Scope).
> - Biết cách viết hàm theo chuẩn PEP 8.
> - Áp dụng vào các ví dụ thực tế.

---

# 1. Hàm (Function) là gì?

Hãy tưởng tượng bạn làm trong một quán cà phê.

Có các công việc:

- Pha cà phê
- Pha trà
- Làm bánh
- Thu ngân
- Rửa ly

Mỗi công việc là một **chức năng độc lập**.

Trong lập trình cũng vậy.

Một **Function** là:

> Một khối mã thực hiện **một nhiệm vụ cụ thể**, có thể được gọi và tái sử dụng nhiều lần.

Ví dụ:

```text-x-trilium-auto
print("Hello")
```

`print()` chính là một hàm.

---

# 2. Vì sao cần Function?

Không dùng hàm:

```text-x-trilium-auto
name = "An"
print("Xin chào", name)

name = "Bình"
print("Xin chào", name)

name = "Lan"
print("Xin chào", name)
```

Lặp lại rất nhiều.

Dùng Function:

```text-x-trilium-auto
def say_hello(name):
    print("Xin chào", name)

say_hello("An")
say_hello("Bình")
say_hello("Lan")
```

Ưu điểm:

- Không lặp code.
- Dễ sửa.
- Dễ bảo trì.
- Dễ kiểm thử.
- Có thể tái sử dụng.

---

# 3. Cú pháp

```text-x-trilium-auto
def tên_hàm(tham_số):
    khối_lệnh
```

Ví dụ:

```text-x-trilium-auto
def hello():
    print("Hello Python")
```

Gọi hàm:

```text-x-trilium-auto
hello()
```

Kết quả:

```text-x-trilium-auto
Hello Python
```

---

# 4. Định nghĩa và gọi hàm

```text-x-trilium-auto
def welcome():
    print("Chào mừng đến với Python!")

welcome()
welcome()
welcome()
```

Kết quả:

```text-x-trilium-auto
Chào mừng đến với Python!
Chào mừng đến với Python!
Chào mừng đến với Python!
```

Một hàm có thể được gọi nhiều lần.

---

# 5. Tham số (Parameter)

Ví dụ:

```text-x-trilium-auto
def greet(name):
    print(f"Xin chào {name}")
```

Ở đây:

```text-x-trilium-auto
name
```

là **Parameter**.

---

Gọi hàm:

```text-x-trilium-auto
greet("An")
```

Ở đây:

```text-x-trilium-auto
"An"
```

là **Argument**.

---

## Phân biệt

```text-x-trilium-auto
Khi định nghĩa

↓

Parameter

-------------------

Khi gọi

↓

Argument
```

Ví dụ:

```text-x-trilium-auto
def add(a, b):
    print(a + b)

add(10, 20)
```

| Parameter | Argument |
| --- | --- |
| `a` | `10` |
| `b` | `20` |

---

# 6. Hàm nhiều tham số

```text-x-trilium-auto
def student(name, age, major):
    print(name)
    print(age)
    print(major)

student("An", 20, "CNTT")
```

---

# 7. Hàm không có tham số

```text-x-trilium-auto
def show_menu():
    print("""
1. Đăng nhập
2. Đăng ký
3. Thoát
""")

show_menu()
```

---

# 8. Giá trị trả về (`return`)

Đây là phần rất quan trọng.

Sai:

```text-x-trilium-auto
def add(a, b):
    print(a + b)
```

Đúng:

```text-x-trilium-auto
def add(a, b):
    return a + b
```

Sử dụng:

```text-x-trilium-auto
result = add(5, 7)

print(result)
```

Kết quả:

```text-x-trilium-auto
12
```

---

## Vì sao cần `return`?

Nếu chỉ `print()`:

```text-x-trilium-auto
def add(a, b):
    print(a + b)

x = add(2, 3)

print(x)
```

Kết quả:

```text-x-trilium-auto
5
None
```

Giải thích:

- Hàm in ra `5`.
- Nhưng không trả về gì.
- Python mặc định trả về `None`.

---

# 9. Một hàm chỉ nên làm một việc

Không nên:

```text-x-trilium-auto
def process_student():
    # Nhập dữ liệu
    # Kiểm tra
    # Tính điểm
    # In kết quả
    # Ghi file
```

Nên tách:

```text-x-trilium-auto
def input_student():
    ...

def calculate_score():
    ...

def print_result():
    ...

def save_file():
    ...
```

Đây là nguyên tắc **Single Responsibility Principle (SRP)**.

---

# 10. Biến cục bộ (Local Variable)

```text-x-trilium-auto
def demo():
    x = 100
    print(x)

demo()
```

Hoạt động bình thường.

Nhưng:

```text-x-trilium-auto
print(x)
```

Lỗi:

```text-x-trilium-auto
NameError
```

Vì `x` chỉ tồn tại bên trong hàm.

---

# 11. Biến toàn cục (Global Variable)

```text-x-trilium-auto
language = "Python"

def show():
    print(language)

show()
```

Kết quả:

```text-x-trilium-auto
Python
```

---

Không nên thay đổi biến toàn cục trong hàm.

Ví dụ:

```text-x-trilium-auto
count = 0

def increase():
    global count
    count += 1
```

Mặc dù chạy được, nhưng việc lạm dụng `global` khiến mã khó hiểu và khó kiểm thử. Hãy ưu tiên truyền dữ liệu qua tham số và trả kết quả bằng `return`.

---

# 12. Hàm gọi hàm

```text-x-trilium-auto
def line():
    print("-" * 30)

def title():
    line()
    print("QUẢN LÝ SINH VIÊN")
    line()

title()
```

Kết quả:

```text-x-trilium-auto
------------------------------
QUẢN LÝ SINH VIÊN
------------------------------
```

Đây là cách tổ chức chương trình rất phổ biến.

---

# 13. Docstring

Một hàm nên có mô tả.

```text-x-trilium-auto
def add(a, b):
    """
    Trả về tổng của hai số.
    """
    return a + b
```

Docstring giúp:

- IDE hiển thị hướng dẫn.
- Dễ đọc.
- Dễ tạo tài liệu.

---

# 14. Type Hints

Python không bắt buộc kiểu dữ liệu.

Nhưng nên ghi rõ:

```text-x-trilium-auto
def add(a: int, b: int) -> int:
    return a + b
```

Ý nghĩa:

```text-x-trilium-auto
a: int

↓

a nên là số nguyên
```

```text-x-trilium-auto
-> int

↓

Hàm trả về số nguyên
```

Lưu ý:

Type hint **không ép kiểu**.

Ví dụ:

```text-x-trilium-auto
print(add("10", "20"))
```

Vẫn chạy và trả về:

```text-x-trilium-auto
1020
```

Muốn kiểm tra kiểu dữ liệu khi chạy cần dùng các kỹ thuật hoặc thư viện khác mà chúng ta sẽ học sau.

---

# 15. Đặt tên hàm

Theo PEP 8:

Đúng:

```text-x-trilium-auto
calculate_salary()
```

```text-x-trilium-auto
find_student()
```

```text-x-trilium-auto
save_file()
```

Sai:

```text-x-trilium-auto
DoSomething()
```

```text-x-trilium-auto
ABC()
```

```text-x-trilium-auto
f1()
```

Tên hàm nên là **động từ hoặc cụm động từ** và thể hiện rõ chức năng.

---

# 16. Ví dụ thực tế

## Tính diện tích hình chữ nhật

```text-x-trilium-auto
def area(width: float, height: float) -> float:
    return width * height

print(area(5, 8))
```

---

## Kiểm tra số chẵn

```text-x-trilium-auto
def is_even(number: int) -> bool:
    return number % 2 == 0

print(is_even(10))
```

---

## Chào người dùng

```text-x-trilium-auto
def welcome(name: str):
    print(f"Xin chào {name}")
```

---

# 17. Những lỗi phổ biến

## Lỗi 1

Quên gọi hàm

```text-x-trilium-auto
def hello():
    print("Hello")
```

Không có:

```text-x-trilium-auto
hello()
```

→ Không có gì xảy ra.

---

## Lỗi 2

Quên `return`

```text-x-trilium-auto
def square(x):
    x * x
```

Đúng:

```text-x-trilium-auto
def square(x):
    return x * x
```

---

## Lỗi 3

Tham số không đủ

```text-x-trilium-auto
def add(a, b):
    return a + b

add(5)
```

Lỗi:

```text-x-trilium-auto
TypeError
```

Vì thiếu đối số thứ hai.

---

# 18. Bài tập thực hành

## Bài 1

Viết hàm:

```text-x-trilium-auto
say_hello(name)
```

In:

```text-x-trilium-auto
Xin chào <tên>
```

---

## Bài 2

Viết hàm:

```text-x-trilium-auto
square(number)
```

Trả về bình phương.

---

## Bài 3

Viết hàm:

```text-x-trilium-auto
is_positive(number)
```

Trả về `True` nếu số dương, ngược lại trả về `False`.

---

## Bài 4

Viết hàm:

```text-x-trilium-auto
calculate_bmi(weight, height)
```

Trả về chỉ số BMI.

*Công thức:* BMI = cân nặng (kg) / (chiều cao (m)²).

---

## Bài 5

Viết hàm:

```text-x-trilium-auto
print_line(length)
```

In ra một dòng gồm `length` ký tự `-`.

---

## Bài 6

Viết hàm:

```text-x-trilium-auto
max_of_two(a, b)
```

Trả về số lớn hơn.

(Không dùng hàm `max()`.)

---

## Bài 7

Viết hàm:

```text-x-trilium-auto
count_vowels(text)
```

Đếm số nguyên âm (`a`, `e`, `i`, `o`, `u`) trong chuỗi và trả về kết quả.

---

# Mini Project: Máy tính bỏ túi

Viết chương trình gồm các hàm:

```text-x-trilium-auto
def add(a, b):
    ...

def subtract(a, b):
    ...

def multiply(a, b):
    ...

def divide(a, b):
    ...
```

Sau đó tạo menu:

```text-x-trilium-auto
=====================
1. Cộng
2. Trừ
3. Nhân
4. Chia
5. Thoát
=====================
```

Khi người dùng chọn phép tính:

1. Nhập hai số.
2. Gọi đúng hàm tương ứng.
3. In kết quả.
4. Quay lại menu cho đến khi chọn **Thoát**.

> **Yêu cầu nâng cao**
> 
> - Kiểm tra chia cho 0.
> - Tách riêng hàm hiển thị menu.
> - Tách riêng hàm nhập dữ liệu hợp lệ.

---

# Tổng kết buổi 9

Hôm nay bạn đã học:

- ✅ Khái niệm Function.
- ✅ Cách định nghĩa và gọi hàm.
- ✅ Parameter và Argument.
- ✅ `return`.
- ✅ Biến cục bộ và biến toàn cục.
- ✅ Hàm gọi hàm.
- ✅ Docstring.
- ✅ Type Hints.
- ✅ Quy tắc đặt tên hàm theo PEP 8.
- ✅ Nguyên tắc **Single Responsibility Principle** trong thiết kế hàm.

---

# Góc lập trình viên chuyên nghiệp

Một chương trình lớn có thể chứa hàng nghìn hoặc hàng chục nghìn hàm. Chất lượng của phần mềm phụ thuộc rất nhiều vào cách bạn thiết kế các hàm.

Một số nguyên tắc quan trọng:

- Mỗi hàm chỉ nên làm **một việc**.
- Hàm nên ngắn gọn, dễ đọc.
- Ưu tiên `return` thay vì `print` nếu kết quả cần được sử dụng tiếp.
- Tránh phụ thuộc vào biến toàn cục.
- Viết docstring và type hints cho các hàm quan trọng.

Đây là những thói quen giúp bạn chuyển từ việc "viết được chương trình" sang "viết được phần mềm có thể bảo trì".

## Chuẩn bị cho Buổi 10

Ở **Buổi 10**, chúng ta sẽ học **Hàm nâng cao (Functions - Phần 2)** với các chủ đề rất quan trọng trong Python hiện đại:

- Giá trị mặc định của tham số (Default Arguments).
- Keyword Arguments và Positional Arguments.
- Positional-only và Keyword-only Parameters (`/` và `*`).
- `*args` và `**kwargs`.
- Unpacking (`*` và `**`) khi gọi hàm.
- Lambda Functions.
- Hàm là đối tượng hạng nhất (First-class Functions).

Đây là những kỹ năng được sử dụng thường xuyên trong các thư viện lớn như Flask, FastAPI, Django, Pandas và nhiều framework Python hiện đại khác.
