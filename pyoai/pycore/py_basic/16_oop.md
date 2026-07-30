# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 16: Lập trình hướng đối tượng (OOP) - Phần 1: Class, Object, Attribute, Method và `self`

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu OOP là gì và vì sao cần OOP.
> - Phân biệt Class và Object.
> - Hiểu Attribute (thuộc tính) và Method (phương thức).
> - Hiểu sâu về `self`.
> - Thành thạo hàm khởi tạo `__init__()`.
> - Biết cách thiết kế Class theo tư duy thực tế.
> - Bắt đầu tư duy như một Software Engineer thay vì chỉ là người viết script.

---

# 1. Vì sao cần OOP?

Giả sử bạn quản lý sinh viên.

Nếu không dùng OOP:

```text-x-trilium-auto
student1_name = "An"
student1_age = 20
student1_score = 9.5

student2_name = "Bình"
student2_age = 21
student2_score = 8.8

student3_name = "Lan"
student3_age = 19
student3_score = 9.2
```

Khi có:

- 100 sinh viên
- 10.000 sinh viên
- 1.000.000 sinh viên

Bạn sẽ có hàng triệu biến.

Không thể quản lý.

---

## Giải pháp

Ta gom dữ liệu và hành vi lại.

Ví dụ:

```text-x-trilium-auto
Sinh viên

Tên

Tuổi

Điểm

Đăng ký môn học()

Đóng học phí()

In bảng điểm()
```

Đó chính là **Object**.

---

# 2. OOP là gì?

OOP (Object-Oriented Programming)

Là cách lập trình dựa trên:

> **Đối tượng (Object)**

Mỗi Object gồm:

```text-x-trilium-auto
Dữ liệu

+

Hành vi
```

Ví dụ:

Một chiếc xe.

Dữ liệu:

```text-x-trilium-auto
Màu

Hãng

Tốc độ

Biển số
```

Hành vi:

```text-x-trilium-auto
Khởi động()

Phanh()

Tăng tốc()

Rẽ()
```

---

# 3. Class là gì?

Class là:

> **Bản thiết kế (Blueprint).**

Ví dụ:

```text-x-trilium-auto
Bản thiết kế

↓

Xe Honda Civic
```

Từ một bản thiết kế có thể tạo:

```text-x-trilium-auto
Xe số 1

Xe số 2

Xe số 3

...
```

---

Python:

```text-x-trilium-auto
class Car:
    pass
```

Đây mới chỉ là bản thiết kế.

Chưa có chiếc xe nào.

---

# 4. Object là gì?

Object là:

> Một thực thể được tạo từ Class.

Ví dụ:

```text-x-trilium-auto
class Car:
    pass

car1 = Car()

car2 = Car()
```

Bây giờ:

```text-x-trilium-auto
Car

↓

car1

↓

car2
```

là hai Object khác nhau.

---

# 5. Kiểm tra Object

```text-x-trilium-auto
print(type(car1))
```

Kết quả:

```text-x-trilium-auto
<class '__main__.Car'>
```

---

Kiểm tra:

```text-x-trilium-auto
print(isinstance(car1, Car))
```

Kết quả:

```text-x-trilium-auto
True
```

---

# 6. Attribute (Thuộc tính)

Ví dụ:

```text-x-trilium-auto
class Car:
    pass

car = Car()

car.brand = "Toyota"
car.color = "White"
car.speed = 120
```

In:

```text-x-trilium-auto
print(car.brand)
```

Kết quả:

```text-x-trilium-auto
Toyota
```

---

Có thể:

```text-x-trilium-auto
print(car.__dict__)
```

Kết quả:

```text-x-trilium-auto
{
    'brand':'Toyota',
    'color':'White',
    'speed':120
}
```

`__dict__` giúp xem tất cả thuộc tính của đối tượng.

---

# 7. Tại sao không nên tạo Attribute như trên?

Cách trên:

```text-x-trilium-auto
car.brand = "Toyota"
```

dễ gây lỗi:

```text-x-trilium-auto
car.spedd = 100
```

Viết sai tên thuộc tính nhưng Python vẫn tạo thuộc tính mới.

Đúng hơn là dùng `__init__()`.

---

# 8. Hàm khởi tạo `__init__()`

Đây là phương thức đặc biệt.

```text-x-trilium-auto
class Car:

    def __init__(self):
        print("Đã tạo xe")
```

Khi:

```text-x-trilium-auto
car = Car()
```

Python tự gọi:

```text-x-trilium-auto
__init__()
```

---

# 9. Khởi tạo dữ liệu

```text-x-trilium-auto
class Car:

    def __init__(self):

        self.brand = "Toyota"

        self.color = "White"

        self.speed = 0
```

Tạo:

```text-x-trilium-auto
car = Car()

print(car.brand)
```

Kết quả:

```text-x-trilium-auto
Toyota
```

---

# 10. `self` là gì?

Đây là phần khiến người mới học bối rối nhất.

Ví dụ:

```text-x-trilium-auto
class Student:

    def hello(self):

        print("Hello")
```

Tạo:

```text-x-trilium-auto
student = Student()

student.hello()
```

Python thực chất làm:

```text-x-trilium-auto
Student.hello(student)
```

Nghĩa là:

```text-x-trilium-auto
self
```

chính là:

```text-x-trilium-auto
student
```

---

# 11. Chứng minh

```text-x-trilium-auto
class Student:

    def show(self):

        print(self)
```

```text-x-trilium-auto
student = Student()

print(student)

student.show()
```

Hai kết quả giống hệt nhau.

`self` chính là tham chiếu đến đối tượng hiện tại.

---

# 12. Truyền dữ liệu vào `__init__`

```text-x-trilium-auto
class Student:

    def __init__(self, name, age):

        self.name = name

        self.age = age
```

Tạo:

```text-x-trilium-auto
student = Student("An",20)
```

Bây giờ:

```text-x-trilium-auto
print(student.name)
```

Kết quả:

```text-x-trilium-auto
An
```

---

# 13. Method

Method chính là Function nằm trong Class.

Ví dụ:

```text-x-trilium-auto
class Dog:

    def bark(self):

        print("Gâu gâu")
```

Sử dụng:

```text-x-trilium-auto
dog = Dog()

dog.bark()
```

---

# 14. Method sử dụng Attribute

```text-x-trilium-auto
class Student:

    def __init__(self,name):

        self.name=name

    def hello(self):

        print(f"Xin chào {self.name}")
```

Kết quả:

```text-x-trilium-auto
Xin chào An
```

---

# 15. Nhiều Object

```text-x-trilium-auto
class Student:

    def __init__(self,name):

        self.name=name
```

```text-x-trilium-auto
s1 = Student("An")

s2 = Student("Bình")

s3 = Student("Lan")
```

Mỗi Object có dữ liệu riêng.

```text-x-trilium-auto
print(s1.name)

print(s2.name)
```

---

# 16. Ví dụ thực tế: Tài khoản ngân hàng

```text-x-trilium-auto
class BankAccount:

    def __init__(self, owner, balance):

        self.owner = owner

        self.balance = balance

    def deposit(self, amount):

        self.balance += amount

    def withdraw(self, amount):

        if amount <= self.balance:
            self.balance -= amount
        else:
            print("Không đủ tiền.")

    def show_balance(self):

        print(f"Số dư: {self.balance:,}")
```

Sử dụng:

```text-x-trilium-auto
acc = BankAccount("An", 10_000_000)

acc.deposit(500_000)

acc.withdraw(2_000_000)

acc.show_balance()
```

---

# 17. Ví dụ thực tế: Giỏ hàng

```text-x-trilium-auto
class ShoppingCart:

    def __init__(self):

        self.items = []

    def add(self, item):

        self.items.append(item)

    def remove(self, item):

        self.items.remove(item)

    def show(self):

        print(self.items)
```

Sử dụng:

```text-x-trilium-auto
cart = ShoppingCart()

cart.add("Laptop")

cart.add("Chuột")

cart.show()
```

---

# 18. Những lỗi phổ biến

## Lỗi 1

Quên `self`

Sai:

```text-x-trilium-auto
class Student:

    def hello():
        pass
```

Lỗi khi gọi:

```text-x-trilium-auto
student.hello()
```

Đúng:

```text-x-trilium-auto
def hello(self):
```

---

## Lỗi 2

Quên `self.`

Sai:

```text-x-trilium-auto
class Student:

    def __init__(self):

        name="An"
```

Đúng:

```text-x-trilium-auto
self.name="An"
```

---

## Lỗi 3

Không dùng `__init__`

Sai:

```text-x-trilium-auto
student.name="An"
```

Đúng:

```text-x-trilium-auto
Student("An")
```

Khởi tạo dữ liệu ngay khi tạo đối tượng giúp mã nguồn rõ ràng và ít lỗi hơn.

---

# 19. Ví dụ hiện đại

## Người dùng

```text-x-trilium-auto
class User:

    def __init__(self, username, email):

        self.username = username
        self.email = email
```

---

## Sản phẩm

```text-x-trilium-auto
class Product:

    def __init__(self, name, price):

        self.name = name
        self.price = price
```

---

## API Response

```text-x-trilium-auto
class ApiResponse:

    def __init__(self, data):

        self.data = data
```

Các lớp như vậy xuất hiện rất nhiều trong web backend, ứng dụng desktop và mobile.

---

# 20. Bài tập thực hành

## Bài 1

Tạo Class:

```text-x-trilium-auto
Person
```

Có:

```text-x-trilium-auto
name

age
```

và Method:

```text-x-trilium-auto
introduce()
```

---

## Bài 2

Tạo Class:

```text-x-trilium-auto
Rectangle
```

Có:

```text-x-trilium-auto
width

height
```

Method:

```text-x-trilium-auto
area()

perimeter()
```

---

## Bài 3

Tạo Class:

```text-x-trilium-auto
Book
```

Có:

```text-x-trilium-auto
title

author

price
```

Method:

```text-x-trilium-auto
show_info()
```

---

## Bài 4

Tạo Class:

```text-x-trilium-auto
Employee
```

Có:

```text-x-trilium-auto
name

salary
```

Method:

```text-x-trilium-auto
increase_salary(percent)
```

---

## Bài 5

Tạo Class:

```text-x-trilium-auto
BankAccount
```

Có:

```text-x-trilium-auto
deposit()

withdraw()

transfer()
```

Trong `transfer()`, hãy chuyển tiền từ tài khoản này sang tài khoản khác.

---

## Bài 6

Viết chương trình quản lý danh sách sinh viên:

- Tạo nhiều đối tượng `Student`.
- Lưu vào một `list`.
- In thông tin của tất cả sinh viên bằng vòng lặp `for`.

---

# Mini Project: Hệ thống Quản lý Thư viện

Xây dựng các lớp sau:

### `Book`

Thuộc tính:

- `title`
- `author`
- `price`
- `quantity`

Phương thức:

- `show_info()`

### `Library`

Thuộc tính:

- `books` (danh sách sách)

Phương thức:

- `add_book(book)`
- `remove_book(title)`
- `find_book(title)`
- `show_books()`

**Yêu cầu mở rộng:**

- Tìm kiếm không phân biệt chữ hoa/chữ thường.
- Hiển thị số lượng còn lại của từng cuốn sách.

---

# Tổng kết buổi 16

Hôm nay bạn đã học:

- ✅ OOP là gì.
- ✅ Class.
- ✅ Object.
- ✅ Attribute.
- ✅ Method.
- ✅ `self`.
- ✅ `__init__()`.
- ✅ Tạo và quản lý nhiều đối tượng.
- ✅ Thiết kế các lớp theo bài toán thực tế.

---

# Góc lập trình viên chuyên nghiệp

Trong các framework Python hiện đại như:

- Django
- FastAPI
- SQLAlchemy
- PySide6
- Tkinter
- Flet

hầu hết mọi thứ đều là **Object**.

Ví dụ:

```text-x-trilium-auto
user = User(...)
request = Request(...)
response = Response(...)
session = Session(...)
```

Hiểu rõ **Class**, **Object** và **self** là nền móng để học các chủ đề nâng cao như kế thừa, đa hình, ORM, GUI và thiết kế kiến trúc phần mềm.

---

# Chuẩn bị cho Buổi 17

Ở **Buổi 17**, chúng ta sẽ học **OOP - Phần 2** với các nội dung rất quan trọng:

- Class Attribute và Instance Attribute.
- Class Method (`@classmethod`).
- Static Method (`@staticmethod`).
- Magic Methods (`__str__`, `__repr__`, `__len__`, `__eq__`, ...).
- Data Class (`@dataclass`).
- Thực hành thiết kế các lớp theo chuẩn Python hiện đại.

Đây là bước chuyển từ việc "biết tạo class" sang "thiết kế class chuyên nghiệp", giúp mã nguồn dễ đọc, dễ bảo trì và phù hợp với các dự án thực tế.
