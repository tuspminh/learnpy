# Python OOP Master – Buổi 11

# Method Overriding (Ghi đè phương thức) – Deep Dive

> **Method Overriding** là khả năng class con **định nghĩa lại** một phương thức đã có trong class cha. Đây là nền tảng của **Polymorphism**, nhiều **Design Pattern** (Strategy, Template Method, Factory Method...) và các framework như Django, Flask, SQLAlchemy.

> **Lưu ý:** Overriding khác hoàn toàn với Overloading. Python **không hỗ trợ Method Overloading theo cách Java/C++**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Method Overriding.
* Biết khi nào nên Override.
* Biết cách mở rộng hành vi bằng `super()`.
* Hiểu Dynamic Dispatch.
* Hiểu quan hệ giữa Overriding và Polymorphism.
* Biết các lỗi thiết kế thường gặp.

---

# 1. Overriding là gì?

Class cha

```python
class Animal:
    def speak(self):
        print("Unknown")
```

Class con

```python
class Dog(Animal):
    def speak(self):
        print("Woof")
```

Khi gọi

```python
dog = Dog()

dog.speak()
```

Kết quả

```text
Woof
```

Method của class con đã **ghi đè** method của class cha.

---

# 2. Điều gì xảy ra?

Python tìm method theo MRO

```text
Dog

↓

Animal

↓

object
```

Ngay khi tìm thấy

```python
Dog.speak
```

Python dừng lại.

Không tiếp tục tìm

```python
Animal.speak
```

---

# 3. Ví dụ trực quan

```python
class Animal:
    def eat(self):
        print("Eating")

    def speak(self):
        print("Unknown")


class Dog(Animal):
    def speak(self):
        print("Woof")


dog = Dog()

dog.eat()
dog.speak()
```

Kết quả

```text
Eating
Woof
```

`eat()` được kế thừa.

`speak()` được override.

---

# 4. Có bắt buộc phải gọi `super()` không?

Không.

Ví dụ

```python
class Animal:
    def speak(self):
        print("Animal")


class Dog(Animal):
    def speak(self):
        print("Dog")
```

Hoàn toàn hợp lệ.

---

# 5. Khi nào nên gọi `super()`?

Nếu muốn **mở rộng hành vi** thay vì thay thế hoàn toàn.

```python
class Animal:
    def speak(self):
        print("Animal sound")


class Dog(Animal):
    def speak(self):

        super().speak()

        print("Woof")
```

Kết quả

```text
Animal sound
Woof
```

---

# 6. Thay thế hoàn toàn

```python
class Animal:
    def start(self):
        print("Start")


class Car(Animal):
    def start(self):
        print("Electric Start")
```

Không gọi

```python
super()
```

vì logic cũ không còn cần.

---

# 7. Dynamic Dispatch

Đây là cơ chế cực kỳ quan trọng.

```python
class Animal:
    def speak(self):
        print("Unknown")


class Dog(Animal):
    def speak(self):
        print("Woof")


animal = Dog()

animal.speak()
```

Kết quả

```text
Woof
```

Mặc dù biến tên là

```text
animal
```

Python vẫn gọi

```text
Dog.speak()
```

Không gọi

```text
Animal.speak()
```

---

# 8. Vì sao?

Python quyết định method tại runtime.

Không phải compile time.

Đó gọi là

```text
Dynamic Dispatch
```

---

# 9. Ví dụ

```python
class Bird:
    def move(self):
        print("Flying")


class Fish:
    def move(self):
        print("Swimming")
```

```python
animals = [Bird(), Fish()]

for animal in animals:
    animal.move()
```

Kết quả

```text
Flying
Swimming
```

Đây chính là nền tảng của Polymorphism.

---

# 10. Overriding Constructor

```python
class Person:
    def __init__(self, name):

        self.name = name
```

```python
class Student(Person):
    def __init__(self, name, student_id):

        super().__init__(name)

        self.student_id = student_id
```

---

# 11. Overriding Property

Property cũng override được.

```python
class Animal:
    @property
    def category(self):
        return "Animal"
```

```python
class Dog(Animal):
    @property
    def category(self):
        return "Dog"
```

```python
dog = Dog()

print(dog.category)
```

Kết quả

```text
Dog
```

---

# 12. Overriding Class Method

```python
class Base:
    @classmethod
    def name(cls):
        print("Base")
```

```python
class Child(Base):
    @classmethod
    def name(cls):
        print("Child")
```

---

# 13. Overriding Static Method

```python
class Base:
    @staticmethod
    def hello():
        print("Base")
```

```python
class Child(Base):
    @staticmethod
    def hello():
        print("Child")
```

Hoàn toàn hợp lệ.

---

# 14. Overriding Magic Method

```python
class Animal:
    def __str__(self):
        return "Animal"
```

```python
class Dog(Animal):
    def __str__(self):
        return "Dog"
```

```python
print(Dog())
```

Kết quả

```text
Dog
```

---

# 15. Ví dụ thực tế

```python
class FileStorage:
    def save(self, filename):

        print("Saving")

        print(filename)
```

```python
class CloudStorage(FileStorage):
    def save(self, filename):

        super().save(filename)

        print("Upload to cloud")
```

```python
storage = CloudStorage()

storage.save("image.png")
```

Kết quả

```text
Saving
image.png
Upload to cloud
```

---

# 16. Ví dụ Logger

```python
class Logger:
    def log(self, message):
        print(message)
```

```python
class TimeLogger(Logger):
    def log(self, message):

        super().log(message)

        print("Saved")
```

---

# 17. Overriding và LSP

Ví dụ sai

```python
class Bird:
    def fly(self):
        print("Flying")
```

```python
class Penguin(Bird):
    def fly(self):
        raise Exception("Cannot fly")
```

Thiết kế này vi phạm **Liskov Substitution Principle (LSP)**.

`Penguin` là `Bird`, nhưng lại không thể thực hiện hành vi mà `Bird` cam kết.

Giải pháp tốt hơn là thiết kế lại hệ thống, ví dụ tách `FlyingBird` khỏi `Bird`.

---

# 18. Những gì có thể Override

Có thể

* Method
* Property
* Static Method
* Class Method
* Magic Method

Không thể override trực tiếp

* Biến instance (instance attribute)

Ví dụ

```python
class A:
    def __init__(self):
        self.value = 1
```

```python
class B(A):
    def __init__(self):

        super().__init__()

        self.value = 2
```

Đây là gán lại giá trị, không phải override.

---

# 19. Overriding ≠ Overloading

Sai

```python
class Demo:
    def hello(self):
        print("A")

    def hello(self, name):
        print(name)
```

Kết quả

Method đầu bị ghi đè.

Python chỉ giữ

```python
hello(name)
```

---

# 20. Ví dụ hoàn chỉnh

```python
class Employee:
    def __init__(self, name):
        self.name = name

    def calculate_salary(self):
        return 0

    def display(self):
        print("-" * 30)
        print(f"Name   : {self.name}")
        print(f"Salary : {self.calculate_salary()}")


class FullTimeEmployee(Employee):
    def calculate_salary(self):
        return 20_000_000


class PartTimeEmployee(Employee):
    def calculate_salary(self):
        return 8_000_000


class Freelancer(Employee):
    def calculate_salary(self):
        return 12_500_000


employees = [
    FullTimeEmployee("Alice"),
    PartTimeEmployee("Bob"),
    Freelancer("Charlie"),
]

for employee in employees:
    employee.display()
```

Kết quả

```text
------------------------------
Name   : Alice
Salary : 20000000
------------------------------
Name   : Bob
Salary : 8000000
------------------------------
Name   : Charlie
Salary : 12500000
```

`display()` không cần biết đối tượng là kiểu nào. Nó chỉ gọi `self.calculate_salary()`, và Python sẽ tự chọn phiên bản phù hợp.

---

# 21. Sơ đồ hoạt động

```text
display()

↓

self.calculate_salary()

↓

FullTimeEmployee ?

↓

PartTimeEmployee ?

↓

Freelancer ?

↓

Gọi đúng method theo object thực tế
```

Đây chính là nền tảng của Polymorphism.

---

# Best Practices

✅ Chỉ override khi thực sự cần thay đổi hành vi.

✅ Nếu class cha có logic quan trọng, hãy gọi:

```python
super().method()
```

trước hoặc sau phần mở rộng của class con.

✅ Giữ cùng tên method và cùng ý nghĩa nghiệp vụ.

---

# Những lỗi người mới thường gặp

## Lỗi 1

Quên gọi

```python
super()
```

khi class cha có logic quan trọng.

---

## Lỗi 2

Override nhưng đổi ý nghĩa method.

Ví dụ

```python
withdraw()
```

ở class cha dùng để rút tiền.

Class con lại biến thành:

```python
withdraw()

↓

xóa tài khoản
```

Đây là thiết kế rất nguy hiểm.

---

## Lỗi 3

Thay đổi kiểu dữ liệu trả về.

Ví dụ

Cha

```python
calculate()

↓

int
```

Con

```python
calculate()

↓

dict
```

Dễ làm hỏng code đang sử dụng class cha.

---

# Bài tập

## Bài 1

Viết

```text
Animal

↓

Dog

↓

Cat
```

Override

```python
speak()
```

---

## Bài 2

Viết

```text
Vehicle

↓

Car
```

Override

```python
start()
```

và gọi

```python
super().start()
```

---

## Bài 3

Viết

```text
Employee

↓

Manager
```

Override property

```python
title
```

---

## Bài 4

Override

```python
__str__()
```

để khi

```python
print(object)
```

hiển thị thông tin đẹp hơn.

---

## Bài 5 (Nâng cao)

Thiết kế hệ thống thanh toán:

```text
Payment
│
├── CashPayment
├── CardPayment
└── QRPayment
```

Class `Payment` có:

```python
process(amount)
```

Mỗi class con override `process()` theo cách riêng.

Viết hàm:

```python
def checkout(payment, amount):
    payment.process(amount)
```

Thử truyền vào từng loại thanh toán và quan sát rằng `checkout()` không cần biết đối tượng cụ thể là gì.

---

# Tóm tắt buổi học

* **Method Overriding** cho phép class con định nghĩa lại hành vi của class cha.
* Python sử dụng **Dynamic Dispatch**, nên phương thức được gọi phụ thuộc vào **kiểu thực tế của object tại runtime**, không phải tên biến.
* `super()` giúp **mở rộng** hành vi của class cha thay vì thay thế hoàn toàn.
* Có thể override method, property, class method, static method và magic method.
* Overriding là nền tảng trực tiếp của **Polymorphism** và nhiều design pattern trong OOP.

> **Buổi 12** chúng ta sẽ học **Multiple Inheritance (Đa kế thừa)**: cách Python xử lý nhiều class cha, thuật toán **C3 Linearization**, Method Resolution Order (MRO) nâng cao, vấn đề **Diamond Problem** và cách `super()` phối hợp giữa nhiều lớp kế thừa. Đây là một trong những chủ đề OOP nâng cao quan trọng nhất của Python.
