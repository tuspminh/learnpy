# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 19: OOP - Phần 4: Kế thừa (Inheritance), `super()`, Method Overriding, Multiple Inheritance và MRO

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của kế thừa trong OOP.
> - Phân biệt Base Class và Derived Class.
> - Thành thạo `super()`.
> - Hiểu Method Overriding.
> - Hiểu Multiple Inheritance và MRO.
> - Biết cách thiết kế hệ thống nhiều lớp theo chuẩn thực tế.
> - Biết khi nào nên và không nên sử dụng kế thừa.

---

# 1. Vì sao cần Kế thừa?

Giả sử bạn xây dựng hệ thống quản lý nhân viên.

Không dùng kế thừa:

```text-x-trilium-auto
class Programmer:

    def __init__(self, name, age):
        self.name = name
        self.age = age


class Designer:

    def __init__(self, name, age):
        self.name = name
        self.age = age


class Manager:

    def __init__(self, name, age):
        self.name = name
        self.age = age
```

Bạn thấy ngay:

- `name` lặp.
- `age` lặp.
- Sau này thêm `email` phải sửa ở cả 3 class.

Đây gọi là **code duplication**.

---

# 2. Giải pháp

Tạo lớp cha:

```text-x-trilium-auto
Employee
```

```text-x-trilium-auto
name

age

email
```

↓

```text-x-trilium-auto
Programmer

Designer

Manager
```

Mỗi lớp con chỉ bổ sung phần riêng của mình.

---

# 3. Class cha (Base Class)

```text-x-trilium-auto
class Employee:

    def __init__(self, name, age):

        self.name = name

        self.age = age

    def introduce(self):

        print(f"Tôi là {self.name}")
```

---

# 4. Class con (Derived Class)

```text-x-trilium-auto
class Programmer(Employee):

    pass
```

Lập tức:

```text-x-trilium-auto
p = Programmer("An", 25)

p.introduce()
```

Hoạt động ngay.

Programmer **thừa hưởng** toàn bộ:

- Attribute
- Method

từ Employee.

---

# 5. Minh họa

```text-x-trilium-auto
          Employee
          /      \
         /        \
Programmer      Designer
```

Programmer có:

```text-x-trilium-auto
name

age

introduce()
```

mặc dù không tự khai báo.

---

# 6. Thêm dữ liệu cho lớp con

Ví dụ:

```text-x-trilium-auto
class Programmer(Employee):

    def __init__(self, name, age, language):

        self.language = language
```

Sai!

Vì:

```text-x-trilium-auto
name

age
```

không được khởi tạo.

---

# 7. `super()`

Đúng phải là:

```text-x-trilium-auto
class Programmer(Employee):

    def __init__(self, name, age, language):

        super().__init__(name, age)

        self.language = language
```

Bây giờ:

```text-x-trilium-auto
p = Programmer("An", 25, "Python")
```

Có:

```text-x-trilium-auto
print(p.name)

print(p.language)
```

---

# 8. `super()` thực chất làm gì?

Python gọi:

```text-x-trilium-auto
Employee.__init__(...)
```

thay bạn.

Nhưng:

```text-x-trilium-auto
super()
```

an toàn hơn nhiều khi có kế thừa nhiều cấp hoặc đa kế thừa.

Đây là cách nên dùng trong Python hiện đại.

---

# 9. Method Overriding

Lớp con có thể ghi đè phương thức của lớp cha.

```text-x-trilium-auto
class Animal:

    def speak(self):

        print("Animal")
```

---

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):

        print("Gâu gâu")
```

---

```text-x-trilium-auto
dog = Dog()

dog.speak()
```

Kết quả:

```text-x-trilium-auto
Gâu gâu
```

Python dùng phiên bản của lớp con.

---

# 10. Gọi cả phương thức của lớp cha

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):

        super().speak()

        print("Gâu gâu")
```

Kết quả:

```text-x-trilium-auto
Animal

Gâu gâu
```

---

# 11. Ví dụ thực tế

```text-x-trilium-auto
class Vehicle:

    def start(self):

        print("Khởi động xe")
```

---

```text-x-trilium-auto
class Car(Vehicle):

    def start(self):

        super().start()

        print("Khởi động động cơ ô tô")
```

---

# 12. `isinstance()`

Kiểm tra:

```text-x-trilium-auto
isinstance(car, Car)
```

↓

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
isinstance(car, Vehicle)
```

↓

```text-x-trilium-auto
True
```

Vì:

Car là Vehicle.

---

# 13. `issubclass()`

```text-x-trilium-auto
issubclass(Car, Vehicle)
```

↓

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
issubclass(Vehicle, Car)
```

↓

```text-x-trilium-auto
False
```

---

# 14. Kế thừa nhiều cấp (Multilevel Inheritance)

```text-x-trilium-auto
Animal

↓

Mammal

↓

Dog
```

Ví dụ:

```text-x-trilium-auto
class Animal:

    def eat(self):

        print("Ăn")
```

---

```text-x-trilium-auto
class Mammal(Animal):

    pass
```

---

```text-x-trilium-auto
class Dog(Mammal):

    pass
```

Dog có:

```text-x-trilium-auto
dog.eat()
```

---

# 15. Đa kế thừa (Multiple Inheritance)

```text-x-trilium-auto
class Fly:

    def fly(self):

        print("Bay")
```

---

```text-x-trilium-auto
class Swim:

    def swim(self):

        print("Bơi")
```

---

```text-x-trilium-auto
class Duck(Fly, Swim):

    pass
```

Sử dụng:

```text-x-trilium-auto
duck.fly()

duck.swim()
```

---

# 16. Diamond Problem

```text-x-trilium-auto
        A
       / \
      B   C
       \ /
        D
```

Nếu:

```text-x-trilium-auto
A.run()
```

và:

```text-x-trilium-auto
B.run()

C.run()
```

thì:

```text-x-trilium-auto
D.run()
```

sẽ gọi cái nào?

Python giải quyết bằng:

## MRO

(Method Resolution Order)

---

# 17. Xem MRO

```text-x-trilium-auto
print(D.__mro__)
```

Hoặc:

```text-x-trilium-auto
help(D)
```

Ví dụ:

```text-x-trilium-auto
D

↓

B

↓

C

↓

A
```

Python tìm Method theo thứ tự này.

---

# 18. `super()` với Multiple Inheritance

Ví dụ:

```text-x-trilium-auto
class A:

    def hello(self):

        print("A")
```

---

```text-x-trilium-auto
class B(A):

    def hello(self):

        super().hello()

        print("B")
```

---

```text-x-trilium-auto
class C(B):

    def hello(self):

        super().hello()

        print("C")
```

---

Kết quả:

```text-x-trilium-auto
A

B

C
```

`super()` không chỉ gọi lớp cha trực tiếp, mà còn tuân theo **MRO**, giúp chuỗi lời gọi hoạt động chính xác trong hệ thống nhiều lớp.

---

# 19. Composition hay Inheritance?

Ví dụ:

Xe có động cơ.

Sai:

```text-x-trilium-auto
Car

↓

Engine
```

Xe **không phải là** động cơ.

Đúng:

```text-x-trilium-auto
Car

↓

has-a

↓

Engine
```

Đây gọi là:

**Composition**

```text-x-trilium-auto
class Engine:

    def start(self):
        print("Engine started")


class Car:

    def __init__(self):

        self.engine = Engine()
```

Composition thường linh hoạt hơn kế thừa khi mô hình là **"có một" (has-a)** thay vì **"là một" (is-a)**.

---

# 20. Khi nào nên dùng kế thừa?

Dùng khi:

```text-x-trilium-auto
Dog

là

Animal
```

```text-x-trilium-auto
Cat

là

Animal
```

Không dùng:

```text-x-trilium-auto
Car

là

Engine
```

Vì:

Car chỉ **có** Engine.

---

# 21. Ví dụ thực tế

## Nhân viên

```text-x-trilium-auto
Employee
```

↓

```text-x-trilium-auto
Programmer

Manager

Designer
```

---

## Hệ thống tài khoản

```text-x-trilium-auto
User
```

↓

```text-x-trilium-auto
Admin

Customer

Moderator
```

---

## Thanh toán

```text-x-trilium-auto
Payment
```

↓

```text-x-trilium-auto
Visa

Paypal

BankTransfer
```

---

## Thiết bị

```text-x-trilium-auto
Device
```

↓

```text-x-trilium-auto
Laptop

Phone

Tablet
```

---

# 22. Những lỗi phổ biến

## Lỗi 1

Quên:

```text-x-trilium-auto
super().__init__()
```

Khi đó các thuộc tính của lớp cha sẽ không được khởi tạo.

---

## Lỗi 2

Sao chép toàn bộ code của lớp cha vào lớp con.

Đây là điều kế thừa giúp tránh.

---

## Lỗi 3

Lạm dụng kế thừa.

Có những hệ thống:

```text-x-trilium-auto
Animal

↓

Dog

↓

Husky

↓

WhiteHusky

↓

...
```

Quá nhiều cấp.

Khó bảo trì.

---

## Lỗi 4

Không hiểu MRO.

Dẫn đến:

```text-x-trilium-auto
super()
```

hoạt động "khó hiểu".

Hãy luôn nhớ:

```text-x-trilium-auto
super()

↓

MRO
```

---

# 23. Bài tập thực hành

## Bài 1

Viết:

```text-x-trilium-auto
Animal
```

Có:

```text-x-trilium-auto
eat()

sleep()
```

Tạo:

```text-x-trilium-auto
Dog

Cat
```

Kế thừa từ `Animal` và thêm phương thức `speak()` riêng.

---

## Bài 2

Viết:

```text-x-trilium-auto
Employee
```

↓

```text-x-trilium-auto
Manager

Developer
```

Ghi đè:

```text-x-trilium-auto
work()
```

---

## Bài 3

Tạo:

```text-x-trilium-auto
Vehicle
```

↓

```text-x-trilium-auto
Car

Bike
```

Thêm:

```text-x-trilium-auto
start()
```

và dùng `super()` để gọi phương thức của lớp cha trước khi bổ sung hành vi riêng.

---

## Bài 4

Tạo:

```text-x-trilium-auto
Person
```

↓

```text-x-trilium-auto
Student
```

↓

```text-x-trilium-auto
GraduateStudent
```

Kiểm tra:

```text-x-trilium-auto
isinstance()

issubclass()
```

---

## Bài 5

Tạo:

```text-x-trilium-auto
Fly

Swim
```

↓

```text-x-trilium-auto
Duck
```

Thực hành Multiple Inheritance và xem:

```text-x-trilium-auto
Duck.__mro__
```

---

## Bài 6

Viết lại bài toán:

```text-x-trilium-auto
Car

Engine
```

bằng **Composition** thay vì kế thừa.

---

# Mini Project: Hệ thống Quản lý Nhân sự

Thiết kế:

## Lớp cha: `Employee`

Thuộc tính:

- `id`
- `name`
- `salary`

Phương thức:

- `work()`
- `show_info()`

---

## Lớp con:

### `Developer`

Thêm:

- `programming_language`

Ghi đè:

```text-x-trilium-auto
work()
```

---

### `Designer`

Thêm:

- `design_tool`

Ghi đè:

```text-x-trilium-auto
work()
```

---

### `Manager`

Thêm:

- `department`

Ghi đè:

```text-x-trilium-auto
work()
```

---

**Yêu cầu mở rộng:**

- Tạo danh sách gồm nhiều loại nhân viên khác nhau.
- Duyệt qua danh sách và gọi `work()` để quan sát hành vi khác nhau của từng đối tượng.

---

# Tổng kết buổi 19

Bạn đã học:

- ✅ Inheritance.
- ✅ Base Class và Derived Class.
- ✅ `super()`.
- ✅ Method Overriding.
- ✅ `isinstance()`.
- ✅ `issubclass()`.
- ✅ Multilevel Inheritance.
- ✅ Multiple Inheritance.
- ✅ MRO.
- ✅ Composition vs Inheritance.

---

# Góc lập trình viên chuyên nghiệp

Trong các framework Python hiện đại:

- **Django**: `CreateView`, `ListView`, `DetailView` đều kế thừa từ các lớp cơ sở.
- **PySide6**: `QMainWindow`, `QDialog`, `QWidget` tạo thành cây kế thừa lớn.
- **FastAPI** và nhiều thư viện khác thường kết hợp **Composition** với **Dependency Injection** thay vì lạm dụng kế thừa.

Một nguyên tắc quan trọng là:

> **Ưu tiên Composition hơn Inheritance khi có thể.**

Kế thừa rất mạnh, nhưng nếu dùng không đúng sẽ khiến hệ thống khó mở rộng và khó bảo trì.

---

# Chuẩn bị cho Buổi 20

Ở **Buổi 20**, chúng ta sẽ học trụ cột thứ ba của OOP:

# **Đa hình (Polymorphism)**

Bạn sẽ học:

- Khái niệm Polymorphism.
- Duck Typing – triết lý đặc trưng của Python.
- Ghi đè phương thức trong đa hình.
- `abc` và **Abstract Base Class (ABC)**.
- `@abstractmethod`.
- `Protocol` và **Structural Typing** (Python hiện đại).
- Xây dựng hệ thống plugin và cổng thanh toán theo chuẩn thiết kế phần mềm.

Đây là một trong những chủ đề giúp bạn viết mã **linh hoạt, mở rộng dễ dàng và tuân theo các nguyên tắc thiết kế hiện đại** trong Python.
