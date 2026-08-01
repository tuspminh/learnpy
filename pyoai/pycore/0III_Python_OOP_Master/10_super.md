Đúng vậy. Cảm ơn bạn đã nhắc lại roadmap. Ở câu trả lời trước mình đã **đi trước roadmap** khi đưa nội dung Overriding và Polymorphism vào Buổi 9. Chúng ta sẽ quay lại đúng lộ trình đã thống nhất.

---

# Python OOP Master – Buổi 10

# `super()` Deep Dive – Hiểu đúng về `super()` trong Python

> Nhiều lập trình viên nghĩ rằng `super()` đơn giản là "gọi class cha". Đây là **một quan niệm chưa chính xác**. Thực tế, `super()` là một cơ chế **ủy quyền (delegation)** dựa trên **Method Resolution Order (MRO)**. Hiểu rõ `super()` là chìa khóa để sử dụng Multiple Inheritance và Mixins một cách chính xác.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu bản chất của `super()`.
* Biết cách dùng `super()` trong constructor.
* Biết gọi method của class cha.
* Hiểu vì sao không nên gọi trực tiếp `Parent.method(self)`.
* Hiểu cơ chế hoạt động của `super()`.
* Chuẩn bị nền tảng cho Multiple Inheritance.

---

# 1. `super()` là gì?

Nhiều người nghĩ

```python
super()
```

=

```text
Class cha
```

Điều này **không hoàn toàn đúng**.

Chính xác hơn:

```text
super()

↓

Proxy Object

↓

Tìm class kế tiếp trong MRO
```

Nó **không biết class cha là ai**.

Nó chỉ biết:

> "Trong Method Resolution Order, class tiếp theo là gì?"

---

# 2. Ví dụ đầu tiên

```python
class Animal:
    def hello(self):
        print("Animal")


class Dog(Animal):
    def hello(self):
        super().hello()
        print("Dog")


dog = Dog()
dog.hello()
```

Kết quả

```text
Animal
Dog
```

---

# 3. Điều gì xảy ra?

Khi gọi

```python
dog.hello()
```

Python thực hiện

```text
Dog.hello()

↓

super()

↓

Animal.hello()

↓

print("Animal")

↓

print("Dog")
```

---

# 4. `super()` trong constructor

```python
class Animal:
    def __init__(self):
        print("Animal constructor")


class Dog(Animal):
    def __init__(self):
        super().__init__()
        print("Dog constructor")


dog = Dog()
```

Kết quả

```text
Animal constructor
Dog constructor
```

---

# 5. Constructor có tham số

```python
class Animal:
    def __init__(self, name):
        self.name = name
```

```python
class Dog(Animal):
    def __init__(self, name, breed):

        super().__init__(name)

        self.breed = breed
```

```python
dog = Dog("Lucky", "Golden")

print(dog.name)
print(dog.breed)
```

Kết quả

```text
Lucky
Golden
```

---

# 6. Không dùng `super()`

Có người viết

```python
class Dog(Animal):
    def __init__(self, name):

        Animal.__init__(self, name)
```

Điều này chạy.

Nhưng **không khuyến khích**.

---

# 7. Vì sao?

Giả sử đổi

```text
Animal

↓

Mammal

↓

Dog
```

Nếu gọi

```python
Animal.__init__(self)
```

thì:

```text
Mammal

bị bỏ qua
```

Trong khi

```python
super().__init__()
```

luôn theo đúng MRO.

---

# 8. Ví dụ

```python
class Animal:
    def __init__(self):
        print("Animal")


class Mammal(Animal):
    def __init__(self):

        super().__init__()

        print("Mammal")


class Dog(Mammal):
    def __init__(self):

        super().__init__()

        print("Dog")
```

Kết quả

```text
Animal
Mammal
Dog
```

---

# 9. Gọi trực tiếp

Nếu

```python
class Dog(Mammal):
    def __init__(self):

        Animal.__init__(self)

        print("Dog")
```

Kết quả

```text
Animal
Dog
```

Mammal biến mất.

---

# 10. super() không biết tên class cha

Ví dụ

```python
class A:
    pass


class B(A):
    pass
```

Trong

```python
class B(A):
    def hello(self):

        super()
```

Python không lưu

```text
A
```

Nó chỉ tra

```text
B.mro()
```

---

# 11. MRO

```python
class Animal:
    pass


class Dog(Animal):
    pass
```

```python
print(Dog.mro())
```

Kết quả

```text
[
 Dog,
 Animal,
 object
]
```

Khi

```python
super()
```

ở Dog

↓

Python tìm

```text
Animal
```

---

# 12. super() trả về gì?

```python
class Animal:
    def hello(self):
        print("Animal")
```

```python
class Dog(Animal):
    def show(self):

        s = super()

        print(type(s))
```

Kết quả

```text
<class 'super'>
```

Nó là một object.

---

# 13. Có thể lưu vào biến

```python
class Dog(Animal):
    def hello(self):

        parent = super()

        parent.hello()

        print("Dog")
```

Kết quả

```text
Animal
Dog
```

---

# 14. super() gọi bất kỳ method nào

```python
class Animal:
    def eat(self):
        print("Eating")

    def sleep(self):
        print("Sleeping")
```

```python
class Dog(Animal):
    def run(self):

        super().eat()

        super().sleep()

        print("Running")
```

---

# 15. Gọi Property

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
        return super().category
```

```python
dog = Dog()

print(dog.category)
```

Kết quả

```text
Animal
```

`super()` hoạt động tốt với property vì property là một **descriptor**.

---

# 16. Gọi Magic Method

```python
class Base:
    def __str__(self):
        return "Base"
```

```python
class Child(Base):
    def __str__(self):
        return f"Child -> {super().__str__()}"
```

```python
print(Child())
```

Kết quả

```text
Child -> Base
```

---

# 17. Ví dụ thực tế

```python
class Employee:
    def __init__(self, name):

        self.name = name

        print("Employee initialized")
```

```python
class Manager(Employee):
    def __init__(self, name, department):

        super().__init__(name)

        self.department = department

        print("Manager initialized")
```

```python
manager = Manager("Alice", "IT")

print(manager.name)
print(manager.department)
```

Kết quả

```text
Employee initialized
Manager initialized

Alice
IT
```

---

# 18. Thứ tự thực thi

```text
Manager()

↓

Manager.__init__()

↓

super()

↓

Employee.__init__()

↓

quay lại

↓

Manager.__init__()
```

---

# 19. Cách Python triển khai `super()`

Khi viết

```python
super().hello()
```

Python nội bộ thực hiện gần giống:

```python
super(CurrentClass, self).hello()
```

Ví dụ:

```python
class Dog(Animal):
    def hello(self):
        super().hello()
```

Tương đương:

```python
class Dog(Animal):
    def hello(self):
        super(Dog, self).hello()
```

Từ Python 3, cú pháp không tham số (`super()`) được khuyến khích vì ngắn gọn và ít lỗi hơn.

---

# 20. Ví dụ hoàn chỉnh

```python
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

        print("Vehicle initialized")

    def start(self):
        print(f"{self.brand} is starting...")


class Car(Vehicle):
    def __init__(self, brand, model):

        super().__init__(brand)

        self.model = model

        print("Car initialized")

    def start(self):

        super().start()

        print(f"{self.model} is ready to drive.")


car = Car("Toyota", "Camry")

print()

car.start()
```

Kết quả

```text
Vehicle initialized
Car initialized

Toyota is starting...
Camry is ready to drive.
```

---

# Những trường hợp nên dùng `super()`

✅ Constructor

```python
super().__init__()
```

---

✅ Overriding

```python
super().save()
```

---

✅ Logging

```python
super().close()
```

---

✅ Validation

```python
super().clean()
```

---

# Không nên

Không gọi trực tiếp

```python
Parent.method(self)
```

trừ khi bạn **thực sự** muốn bỏ qua MRO (rất hiếm).

---

# Best Practices

✅ Luôn dùng

```python
super()
```

thay vì

```python
Parent.method(self)
```

---

✅ Constructor luôn nên viết

```python
super().__init__()
```

---

✅ Không giả định class cha sẽ luôn giữ nguyên.

---

# Những lỗi người mới thường gặp

## Lỗi 1

Quên gọi

```python
super().__init__()
```

↓

Thuộc tính của class cha không được khởi tạo.

---

## Lỗi 2

Gọi

```python
Parent.__init__(self)
```

↓

Có thể phá vỡ Multiple Inheritance.

---

## Lỗi 3

Nghĩ rằng

```python
super()
```

=

```text
Class cha
```

Sai.

Thực tế

```text
super()

↓

Class tiếp theo trong MRO
```

---

# Bài tập

## Bài 1

Viết:

```text
Animal

↓

Dog
```

Trong constructor của `Dog`, gọi constructor của `Animal` bằng `super()`.

---

## Bài 2

Viết:

```text
Person

↓

Student
```

Trong `Student`, dùng `super()` để khởi tạo `name` và `age`.

---

## Bài 3

Viết:

```text
Vehicle

↓

Car
```

`Car.start()` gọi:

```python
super().start()
```

sau đó in thêm:

```text
Ready
```

---

## Bài 4

In

```python
print(Dog.mro())
```

Giải thích vì sao `super()` chọn class tiếp theo trong danh sách này.

---

## Bài 5 (Nâng cao)

Viết chuỗi kế thừa:

```text
A

↓

B

↓

C

↓

D
```

Mỗi constructor:

* gọi `super().__init__()`;
* in tên class của mình.

Dự đoán kết quả trước khi chạy, sau đó xác nhận bằng cách thực thi.

---

# Tóm tắt buổi học

* `super()` **không đơn giản là gọi class cha**, mà tạo ra một **proxy object** để tìm phương thức kế tiếp theo **Method Resolution Order (MRO)**.
* `super()` nên được sử dụng trong constructor, method ghi đè, property và cả magic method.
* Tránh gọi trực tiếp `Parent.method(self)` vì có thể bỏ qua các lớp trung gian và làm hỏng cơ chế Multiple Inheritance.
* Việc hiểu đúng `super()` là nền tảng để học **Method Overriding**, **Multiple Inheritance**, **Mixins** và nhiều framework Python hiện đại.

> **Buổi 11** chúng ta sẽ học chuyên sâu về **Method Overriding**: quy tắc ghi đè phương thức, mở rộng hay thay thế hành vi của class cha, nguyên tắc Liskov Substitution liên quan đến overriding và các lỗi thiết kế thường gặp khi ghi đè method.
