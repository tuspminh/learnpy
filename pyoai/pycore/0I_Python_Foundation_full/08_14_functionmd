# Giai đoạn 1 – Python Foundation

# Buổi 14. Hàm (Function)

> Hàm là một trong những khái niệm quan trọng nhất trong lập trình. Một lập trình viên Python chuyên nghiệp không viết một chương trình dài hàng nghìn dòng code trong một file, mà chia nhỏ chương trình thành các **hàm có trách nhiệm rõ ràng**.

Trong thực tế:

* Flask/FastAPI sử dụng rất nhiều function.
* Django View là function hoặc class.
* Các thư viện Python đều được xây dựng từ hàng nghìn function.
* Code sạch (Clean Code) phụ thuộc rất nhiều vào cách thiết kế hàm.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Function là gì.
* Biết cách định nghĩa và gọi hàm.
* Hiểu parameter và argument.
* Biết `return`.
* Hiểu hàm trả về dữ liệu.
* Biết giá trị mặc định.
* Hiểu nhiều loại argument.
* Biết cách thiết kế hàm theo chuẩn PEP8.
* Biết khi nào nên tạo hàm.

---

# 1. Hàm là gì?

Hàm là một khối lệnh thực hiện một nhiệm vụ cụ thể.

Ví dụ:

Không dùng hàm:

```python
print("Hello Python")
print("Hello Python")
print("Hello Python")
```

Lặp lại code.

---

Dùng hàm:

```python
def hello():
    print("Hello Python")
```

Gọi:

```python
hello()
hello()
hello()
```

Kết quả:

```text
Hello Python
Hello Python
Hello Python
```

---

# 2. Vì sao cần Function?

## Vấn đề khi không dùng hàm

Ví dụ chương trình tính diện tích:

```python
width = 10
height = 5

area = width * height

print(area)


width = 20
height = 8

area = width * height

print(area)
```

Lặp code.

---

Dùng hàm:

```python
def calculate_area(width, height):
    return width * height


print(calculate_area(10, 5))
print(calculate_area(20, 8))
```

Code:

* Ngắn hơn.
* Dễ đọc.
* Dễ sửa.
* Dễ kiểm thử.

---

# 3. Cú pháp tạo hàm

Cấu trúc:

```python
def ten_ham():
    câu_lệnh
```

Ví dụ:

```python
def say_hello():
    print("Hello")
```

---

Gọi hàm:

```python
say_hello()
```

---

# 4. Quy tắc đặt tên hàm (PEP8)

Python sử dụng:

```
snake_case
```

Đúng:

```python
def calculate_total():
    pass
```

Sai:

```python
def CalculateTotal():
    pass
```

Sai:

```python
def calculate-total():
    pass
```

---

Tên hàm nên là động từ:

Tốt:

```python
def calculate_price():
    pass
```

```python
def get_user():
    pass
```

```python
def save_file():
    pass
```

Không nên:

```python
def price():
    pass
```

---

# 5. Function không có tham số

Ví dụ:

```python
def show_menu():
    print("1. Add")
    print("2. Delete")
    print("3. Exit")


show_menu()
```

---

# 6. Function có tham số (Parameter)

Tham số là dữ liệu truyền vào hàm.

Ví dụ:

```python
def greet(name):
    print("Hello", name)


greet("An")
```

Kết quả:

```text
Hello An
```

---

Ở đây:

```python
def greet(name):
```

`name` là parameter.

---

Khi gọi:

```python
greet("An")
```

`"An"` là argument.

---

# 7. Parameter và Argument

Ví dụ:

```python
def add(a, b):
    print(a + b)


add(10, 20)
```

Phân tích:

```python
a, b
```

là parameter.

```python
10, 20
```

là argument.

---

# 8. Return

`return` trả kết quả ra ngoài hàm.

Ví dụ:

```python
def add(a, b):
    return a + b


result = add(10, 20)

print(result)
```

Kết quả:

```text
30
```

---

# 9. Không có return

Ví dụ:

```python
def add(a, b):
    print(a + b)


result = add(10, 20)

print(result)
```

Kết quả:

```text
30
None
```

Vì hàm không trả về gì.

Python tự trả:

```python
None
```

---

# 10. Return kết thúc hàm

Ví dụ:

```python
def test():
    print("A")

    return

    print("B")


test()
```

Kết quả:

```text
A
```

Code sau `return` không chạy.

---

# 11. Trả về nhiều giá trị

Python dùng Tuple.

Ví dụ:

```python
def calculate(a, b):
    return a + b, a - b


result = calculate(10, 5)

print(result)
```

Kết quả:

```text
(15, 5)
```

---

Unpacking:

```python
add, sub = calculate(10, 5)

print(add)
print(sub)
```

Kết quả:

```text
15
5
```

---

# 12. Giá trị mặc định (Default Parameter)

Ví dụ:

```python
def greet(name="Guest"):
    print("Hello", name)


greet()
```

Kết quả:

```text
Hello Guest
```

---

```python
greet("An")
```

Kết quả:

```text
Hello An
```

---

# 13. Quy tắc Default Parameter

Sai:

```python
def test(a=10, b):
    pass
```

Lỗi:

```text
SyntaxError
```

---

Đúng:

```python
def test(a, b=10):
    pass
```

Tham số mặc định phải đứng sau tham số thường.

---

# 14. Keyword Argument

Có thể truyền theo tên.

Ví dụ:

```python
def student(name, age):
    print(name, age)


student(
    age=20,
    name="An"
)
```

Kết quả:

```text
An 20
```

---

Ưu điểm:

Code dễ đọc hơn.

---

# 15. Positional Argument

Truyền theo vị trí.

```python
def student(name, age):
    print(name, age)


student("An", 20)
```

Python hiểu:

```
name = "An"
age = 20
```

---

# 16. Kết hợp positional và keyword

Đúng:

```python
student(
    "An",
    age=20
)
```

---

Sai:

```python
student(
    name="An",
    20
)
```

Lỗi:

```
SyntaxError
```

---

# 17. `*args`

Dùng khi không biết trước số lượng tham số.

Ví dụ:

```python
def total(*numbers):
    result = 0

    for n in numbers:
        result += n

    return result


print(total(1, 2, 3))
```

Kết quả:

```text
6
```

---

Bên trong:

```python
numbers
```

là Tuple.

---

Ví dụ:

```python
def show(*args):
    print(type(args))


show(1,2,3)
```

Kết quả:

```text
<class 'tuple'>
```

---

# 18. `**kwargs`

Nhận nhiều keyword argument.

Ví dụ:

```python
def info(**data):
    print(data)


info(
    name="An",
    age=20
)
```

Kết quả:

```python
{
'name':'An',
'age':20
}
```

---

Bên trong:

```python
data
```

là Dictionary.

---

# 19. Function có thể nhận Function

Trong Python, function là object.

Ví dụ:

```python
def hello():
    print("Hello")


x = hello

x()
```

Kết quả:

```text
Hello
```

---

Đây là nền tảng cho:

* Decorator.
* Callback.
* Functional Programming.

---

# 20. Function lồng nhau

```python
def outer():

    def inner():
        print("Inner")

    inner()


outer()
```

Kết quả:

```text
Inner
```

---

# 21. Docstring

Hàm chuyên nghiệp nên có mô tả.

Ví dụ:

```python
def add(a, b):
    """
    Cộng hai số.

    Args:
        a: số thứ nhất
        b: số thứ hai

    Returns:
        Tổng của a và b
    """

    return a + b
```

Xem:

```python
print(add.__doc__)
```

---

# 22. Thiết kế hàm tốt

## Một hàm chỉ nên làm một việc

Không tốt:

```python
def process_user():
    # đọc database
    # kiểm tra password
    # gửi email
    # tạo file
    pass
```

Nên:

```python
def get_user():
    pass


def check_password():
    pass


def send_email():
    pass
```

---

## Hàm nên ngắn

Tốt:

```python
def calculate_tax(price):
    return price * 0.1
```

---

Không nên:

```python
def process():
    # 200 dòng code
    pass
```

---

# 23. Ví dụ thực tế

## Hệ thống tính tiền đơn hàng

```python
def calculate_total(price, quantity):
    return price * quantity


def apply_discount(total, discount):
    return total - discount


price = 100000
quantity = 3

total = calculate_total(price, quantity)

final_price = apply_discount(
    total,
    20000
)

print(final_price)
```

Kết quả:

```text
280000
```

---

# 24. Bài tập thực hành

## Bài 1

Viết hàm:

```python
def hello(name):
```

In:

```
Xin chào <name>
```

---

## Bài 2

Viết hàm tính diện tích hình chữ nhật:

```python
def rectangle_area(width, height):
```

Trả về diện tích.

---

## Bài 3

Viết hàm kiểm tra số chẵn:

```python
def is_even(number):
```

Trả về:

```python
True
```

hoặc

```python
False
```

---

## Bài 4

Viết hàm:

```python
def find_max(a, b, c):
```

Tìm số lớn nhất.

Không dùng:

```python
max()
```

---

## Bài 5

Viết hàm tính tổng bất kỳ số lượng số:

Ví dụ:

```python
sum_all(1,2,3,4,5)
```

Kết quả:

```
15
```

Dùng:

```python
*args
```

---

# Tổng kết Buổi 14

Bạn đã học:

✅ Function là gì
✅ Cách tạo và gọi hàm
✅ Parameter và Argument
✅ Return
✅ Default Parameter
✅ Keyword Argument
✅ Positional Argument
✅ `*args`
✅ `**kwargs`
✅ Function như một object
✅ Docstring
✅ Nguyên tắc thiết kế hàm chuẩn PEP8

---

## Kiến thức chuẩn bị cho Buổi 15

Buổi tiếp theo:

# Buổi 15. Scope (Phạm vi biến)

Chúng ta sẽ học:

* Local Scope
* Global Scope
* LEGB Rule
* `global`
* `nonlocal`
* Namespace
* Cách Python tìm kiếm biến

Đây là kiến thức rất quan trọng để hiểu:

* Closure
* Decorator
* Class
* Framework design trong Python.
