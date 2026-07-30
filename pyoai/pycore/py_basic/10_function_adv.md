# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 10: Làm chủ Hàm (Functions) - Phần 2: Tham số nâng cao, `*args`, `**kwargs`, Lambda và First-class Functions

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Thành thạo mọi cách truyền tham số trong Python.
> - Hiểu Default Arguments hoạt động như thế nào.
> - Phân biệt Positional và Keyword Arguments.
> - Thành thạo `*args` và `**kwargs`.
> - Biết cách Unpacking khi gọi hàm.
> - Hiểu hàm là First-class Object.
> - Biết sử dụng Lambda đúng cách.
> - Tránh những lỗi phổ biến mà ngay cả lập trình viên có kinh nghiệm cũng thường gặp.

---

# 1. Ôn tập buổi trước

Ở buổi 9 chúng ta đã học:

```text-x-trilium-auto
def add(a, b):
    return a + b
```

Trong buổi này, chúng ta sẽ đi sâu vào cách Python truyền tham số cho hàm.

---

# 2. Default Arguments (Tham số mặc định)

Ví dụ:

```text-x-trilium-auto
def greet(name, message="Xin chào"):
    print(f"{message}, {name}")
```

Gọi hàm:

```text-x-trilium-auto
greet("An")
```

Kết quả:

```text-x-trilium-auto
Xin chào, An
```

Hoặc:

```text-x-trilium-auto
greet("An", "Chào buổi sáng")
```

Kết quả:

```text-x-trilium-auto
Chào buổi sáng, An
```

---

## Vì sao cần tham số mặc định?

Ví dụ thực tế:

```text-x-trilium-auto
def connect(host="localhost", port=3306):
    print(host, port)
```

Nếu không truyền gì:

```text-x-trilium-auto
connect()
```

Kết quả:

```text-x-trilium-auto
localhost 3306
```

Đây là cách rất nhiều thư viện Python hoạt động.

---

# 3. Lỗi nguy hiểm: Mutable Default Arguments

Đây là một trong những lỗi nổi tiếng nhất của Python.

Sai:

```text-x-trilium-auto
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("Táo"))
print(add_item("Cam"))
```

Nhiều người nghĩ kết quả sẽ là:

```text-x-trilium-auto
['Táo']
['Cam']
```

Nhưng thực tế:

```text-x-trilium-auto
['Táo']
['Táo', 'Cam']
```

**Vì sao?**

Giá trị mặc định chỉ được tạo **một lần** khi định nghĩa hàm, không phải mỗi lần gọi hàm.

---

## Cách đúng

```text-x-trilium-auto
def add_item(item, items=None):
    if items is None:
        items = []

    items.append(item)
    return items
```

Đây là cách viết chuẩn trong Python.

---

# 4. Positional Arguments

Python truyền theo vị trí.

```text-x-trilium-auto
def student(name, age):
    print(name, age)

student("An", 20)
```

Ở đây:

```text-x-trilium-auto
name = "An"
age = 20
```

---

# 5. Keyword Arguments

Có thể truyền theo tên.

```text-x-trilium-auto
student(age=20, name="An")
```

Kết quả giống hệt.

Ưu điểm:

- Dễ đọc.
- Không cần nhớ thứ tự.
- Rất phổ biến trong các thư viện.

Ví dụ:

```text-x-trilium-auto
print("Python", end="***")
```

`end=` chính là một keyword argument.

---

# 6. Kết hợp Positional và Keyword

Đúng:

```text-x-trilium-auto
student("An", age=20)
```

Sai:

```text-x-trilium-auto
student(name="An", 20)
```

Lý do:

> Positional arguments phải đứng trước keyword arguments.

---

# 7. Positional-only Parameters (`/`)

Python 3.8+ hỗ trợ:

```text-x-trilium-auto
def divide(a, b, /):
    return a / b
```

Được:

```text-x-trilium-auto
divide(10, 2)
```

Không được:

```text-x-trilium-auto
divide(a=10, b=2)
```

Lỗi:

```text-x-trilium-auto
TypeError
```

Ứng dụng:

- Thiết kế API rõ ràng.
- Tránh người dùng phụ thuộc vào tên tham số.

---

# 8. Keyword-only Parameters (`*`)

```text-x-trilium-auto
def create_user(name, *, age, city):
    print(name, age, city)
```

Đúng:

```text-x-trilium-auto
create_user("An", age=20, city="Hà Nội")
```

Sai:

```text-x-trilium-auto
create_user("An", 20, "Hà Nội")
```

---

# 9. `*args`

Dùng khi không biết trước có bao nhiêu đối số.

```text-x-trilium-auto
def total(*numbers):
    print(numbers)
```

Gọi:

```text-x-trilium-auto
total(1, 2, 3)
```

Kết quả:

```text-x-trilium-auto
(1, 2, 3)
```

Lưu ý:

`numbers` là một **tuple**.

---

## Ví dụ

```text-x-trilium-auto
def total(*numbers):
    s = 0

    for n in numbers:
        s += n

    return s

print(total(10, 20, 30))
```

Kết quả:

```text-x-trilium-auto
60
```

---

# 10. `**kwargs`

Dùng để nhận nhiều keyword arguments.

```text-x-trilium-auto
def profile(**info):
    print(info)
```

Gọi:

```text-x-trilium-auto
profile(name="An", age=20, city="Đà Nẵng")
```

Kết quả:

```text-x-trilium-auto
{
    'name': 'An',
    'age': 20,
    'city': 'Đà Nẵng'
}
```

`info` là một **dictionary**.

---

# 11. Kết hợp tất cả

```text-x-trilium-auto
def demo(a, b=10, *args, **kwargs):
    print(a)
    print(b)
    print(args)
    print(kwargs)
```

Ví dụ:

```text-x-trilium-auto
demo(
    1,
    2,
    3,
    4,
    name="An",
    age=20
)
```

Kết quả:

```text-x-trilium-auto
a = 1
b = 2
args = (3, 4)
kwargs = {'name': 'An', 'age': 20}
```

---

# 12. Unpacking với `*`

```text-x-trilium-auto
numbers = [10, 20]

def add(a, b):
    return a + b

print(add(*numbers))
```

Python hiểu:

```text-x-trilium-auto
add(10, 20)
```

---

# 13. Unpacking với `**`

```text-x-trilium-auto
student = {
    "name": "An",
    "age": 20
}

def show(name, age):
    print(name, age)

show(**student)
```

Python hiểu:

```text-x-trilium-auto
show(name="An", age=20)
```

---

# 14. Hàm là First-class Object

Trong Python, hàm cũng là một đối tượng.

```text-x-trilium-auto
def hello():
    print("Hello")

x = hello

x()
```

Kết quả:

```text-x-trilium-auto
Hello
```

Điều này mở ra rất nhiều kỹ thuật mạnh như callback, decorator và dependency injection mà chúng ta sẽ học ở các buổi sau.

---

# 15. Truyền hàm vào hàm

```text-x-trilium-auto
def square(x):
    return x * x

def calculate(fn, value):
    return fn(value)

print(calculate(square, 5))
```

Kết quả:

```text-x-trilium-auto
25
```

Đây là nền tảng của lập trình hàm (Functional Programming).

---

# 16. Lambda Function

Thông thường:

```text-x-trilium-auto
def square(x):
    return x * x
```

Có thể viết:

```text-x-trilium-auto
square = lambda x: x * x

print(square(5))
```

Kết quả:

```text-x-trilium-auto
25
```

---

## Lambda nhiều tham số

```text-x-trilium-auto
add = lambda a, b: a + b

print(add(10, 20))
```

---

# 17. Khi nào nên dùng Lambda?

Nên:

```text-x-trilium-auto
numbers = [3, 1, 5, 2]

print(sorted(numbers, key=lambda x: -x))
```

Hoặc:

```text-x-trilium-auto
students = [
    {"name": "An", "score": 8},
    {"name": "Bình", "score": 9},
]

students.sort(key=lambda student: student["score"])
```

Không nên:

```text-x-trilium-auto
lambda x:
    ...
```

với logic quá dài hoặc nhiều điều kiện. Khi đó hãy dùng `def`.

---

# 18. Những lỗi phổ biến

## Lỗi 1: Dùng list làm giá trị mặc định

Sai:

```text-x-trilium-auto
def func(data=[]):
    ...
```

Đúng:

```text-x-trilium-auto
def func(data=None):
    if data is None:
        data = []
```

---

## Lỗi 2: Nhầm `*args` và `**kwargs`

```text-x-trilium-auto
*args
```

→ Tuple.

```text-x-trilium-auto
**kwargs
```

→ Dictionary.

---

## Lỗi 3: Lạm dụng Lambda

Không nên viết một biểu thức lambda quá dài và khó đọc.

Nếu hàm có nhiều dòng hoặc cần giải thích, hãy dùng `def`.

---

# 19. Ví dụ thực tế

## Hàm ghi log

```text-x-trilium-auto
def log(message, level="INFO"):
    print(f"[{level}] {message}")

log("Kết nối thành công")
log("Không tìm thấy tệp", level="ERROR")
```

---

## Hàm tính tổng

```text-x-trilium-auto
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4, 5))
```

---

## Tạo người dùng

```text-x-trilium-auto
def create_user(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

create_user(
    name="An",
    age=20,
    city="Hồ Chí Minh"
)
```

---

# 20. Bài tập thực hành

## Bài 1

Viết hàm:

```text-x-trilium-auto
def greet(name, message="Xin chào"):
    ...
```

Thử gọi với và không truyền `message`.

---

## Bài 2

Viết hàm:

```text-x-trilium-auto
def average(*numbers):
    ...
```

Trả về điểm trung bình của tất cả các số.

---

## Bài 3

Viết hàm:

```text-x-trilium-auto
def show_profile(**info):
    ...
```

In toàn bộ thông tin người dùng.

---

## Bài 4

Cho:

```text-x-trilium-auto
data = [5, 8]
```

Dùng `*` để truyền vào hàm:

```text-x-trilium-auto
def multiply(a, b):
    return a * b
```

---

## Bài 5

Cho:

```text-x-trilium-auto
student = {
    "name": "Lan",
    "age": 21
}
```

Dùng `**` để truyền vào một hàm nhận `name` và `age`.

---

## Bài 6

Sắp xếp danh sách sinh viên theo điểm bằng `sorted()` và `lambda`.

---

## Bài 7

Viết hàm:

```text-x-trilium-auto
def calculate(operation, a, b):
    ...
```

Trong đó `operation` là một hàm (`add`, `subtract`, `multiply` hoặc `divide`).

---

# Mini Project: Hệ thống quản lý nhân viên

Viết chương trình gồm các hàm:

- `create_employee(**info)`
- `calculate_salary(hours, rate=50000)`
- `print_employee(employee)`
- `print_report(*employees)`

Yêu cầu:

1. Tạo nhiều nhân viên bằng `**kwargs`.
2. Tính lương với mức lương mặc định hoặc do người dùng chỉ định.
3. In thông tin từng nhân viên.
4. In báo cáo tổng hợp bằng `*args`.

---

# Tổng kết buổi 10

Bạn đã học được:

- ✅ Default Arguments.
- ✅ Positional và Keyword Arguments.
- ✅ Positional-only (`/`) và Keyword-only (`*`) Parameters.
- ✅ `*args`.
- ✅ `**kwargs`.
- ✅ Unpacking với `*` và `**`.
- ✅ Hàm là First-class Object.
- ✅ Truyền hàm vào hàm.
- ✅ Lambda Function.
- ✅ Các lỗi phổ biến và cách tránh.

---

# Góc lập trình viên chuyên nghiệp

Những kỹ thuật trong buổi học này xuất hiện ở hầu hết các framework và thư viện Python hiện đại:

- **Flask/FastAPI** sử dụng `**kwargs` và keyword arguments để định nghĩa route và dependency.
- **Pandas** thường nhận nhiều keyword arguments để điều khiển hành vi của hàm.
- `**sorted()**`**,** `**min()**`**,** `**max()**` và nhiều API chuẩn của Python nhận callback thông qua tham số `key`, nơi lambda được sử dụng rất nhiều.
- **Decorator** (sẽ học sau) thường dựa trên `*args` và `**kwargs` để viết các hàm bọc (wrapper) có thể làm việc với mọi kiểu tham số.

Việc thành thạo các kỹ thuật này sẽ giúp bạn đọc và viết mã nguồn của các dự án Python chuyên nghiệp dễ dàng hơn.

## Chuẩn bị cho Buổi 11

Ở buổi tiếp theo, chúng ta sẽ học **Scope, Namespace và Closure** một cách chuyên sâu. Bạn sẽ hiểu:

- LEGB Rule.
- Local, Enclosing, Global và Built-in Scope.
- `global` và `nonlocal`.
- Closure hoạt động như thế nào.
- Ứng dụng của Closure trong callback, decorator và lập trình hàm.

Đây là một trong những chủ đề giúp bạn hiểu sâu cách Python thực thi chương trình và là nền tảng trước khi bước vào **Decorator** và **OOP nâng cao**.
