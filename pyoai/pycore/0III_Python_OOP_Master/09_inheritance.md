# Python OOP Master – Buổi 9

# Inheritance (Kế thừa) – Single Inheritance, `super()`, Overriding và MRO cơ bản

> **Inheritance (Kế thừa)** là một trong bốn trụ cột của OOP. Tuy nhiên, trong Python, kế thừa không chỉ đơn thuần là "con thừa hưởng cha", mà còn liên quan đến **Method Resolution Order (MRO)**, `super()`, **Descriptor**, **Multiple Inheritance** và nhiều cơ chế nội bộ khác.

Buổi này sẽ tập trung vào **Single Inheritance (kế thừa đơn)**. Các buổi tiếp theo sẽ đi sâu vào Multiple Inheritance và MRO nâng cao.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Inheritance là gì.
* Biết tạo class kế thừa.
* Hiểu `is-a relationship`.
* Hiểu Constructor Inheritance.
* Hiểu Method Overriding.
* Hiểu `super()`.
* Hiểu cách Python tìm method.
* Biết khi nào nên và không nên dùng kế thừa.

---

# 1. Inheritance là gì?

Inheritance là khả năng:

> Một class có thể **kế thừa** thuộc tính và phương thức từ class khác.

Ví dụ

```text
Animal
│
├── name
├── age
└── speak()

        ▲
        │

Dog
Cat
Bird
```

Dog không cần viết lại:

* name
* age
* speak()

---

# 2. Cú pháp

```python
class Parent:
    pass


class Child(Parent):
    pass
```

Child sẽ có toàn bộ public/protected members của Parent.

---

# 3. Ví dụ đầu tiên

```python
class Animal:
    def eat(self):
        print("Eating...")


class Dog(Animal):
    pass


dog = Dog()

dog.eat()
```

Kết quả

```text
Eating...
```

Dog không định nghĩa `eat()`.

Python tự tìm trong `Animal`.

---

# 4. Object Diagram

```text
Dog Object

↓

Dog Class

↓

Animal Class

↓

object
```

Mọi class Python đều kế thừa từ

```python
object
```

---

# 5. Kiểm tra

```python
class Animal:
    pass


class Dog(Animal):
    pass


print(issubclass(Dog, Animal))

dog = Dog()

print(isinstance(dog, Animal))
print(isinstance(dog, Dog))
```

Kết quả

```text
True
True
True
```

---

# 6. Quan hệ "is-a"

Dog

**is an**

Animal

Điều này gọi là

```text
IS-A Relationship
```

Ví dụ đúng

```text
Dog

is an Animal
```

```text
Cat

is an Animal
```

Sai

```text
Engine

is a Car
```

Động cơ không phải là xe.

Đó là

```text
HAS-A
```

sẽ học ở Composition.

---

# 7. Constructor có được kế thừa không?

Có.

```python
class Animal:
    def __init__(self):
        print("Animal constructor")


class Dog(Animal):
    pass


dog = Dog()
```

Kết quả

```text
Animal constructor
```

---

# 8. Constructor riêng

```python
class Animal:
    def __init__(self):
        print("Animal")


class Dog(Animal):
    def __init__(self):
        print("Dog")
```

Kết quả

```text
Dog
```

Constructor cha **không được gọi**.

---

# 9. super()

Muốn gọi constructor cha

```python
class Animal:
    def __init__(self):
        print("Animal")


class Dog(Animal):
    def __init__(self):
        super().__init__()

        print("Dog")
```

Kết quả

```text
Animal
Dog
```

---

# 10. Constructor có tham số

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

Sử dụng

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

# 11. Method Overriding

Class con có thể ghi đè method.

```python
class Animal:
    def speak(self):
        print("Unknown")
```

```python
class Dog(Animal):
    def speak(self):
        print("Woof")
```

```python
dog = Dog()

dog.speak()
```

Kết quả

```text
Woof
```

---

# 12. Gọi method cha

```python
class Animal:
    def speak(self):
        print("Animal")
```

```python
class Dog(Animal):
    def speak(self):

        super().speak()

        print("Dog")
```

Kết quả

```text
Animal
Dog
```

---

# 13. Python tìm method như thế nào?

```python
dog.speak()
```

Python tìm

```text
Dog

↓

Animal

↓

object
```

Đây gọi là

```text
Method Resolution Order
```

(MRO)

---

# 14. Kiểm tra MRO

```python
class Animal:
    pass


class Dog(Animal):
    pass


print(Dog.__mro__)
```

Kết quả

```text
(
Dog,
Animal,
object
)
```

Hoặc:

```python
print(Dog.mro())
```

Kết quả:

```text
[<class '__main__.Dog'>,
 <class '__main__.Animal'>,
 <class 'object'>]
```

---

# 15. Ví dụ hoàn chỉnh

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name} is eating.")

    def speak(self):
        print("Unknown sound")


class Dog(Animal):
    def __init__(self, name, breed):

        super().__init__(name)

        self.breed = breed

    def speak(self):
        print("Woof Woof")


dog = Dog("Lucky", "Golden Retriever")

dog.eat()
dog.speak()

print(dog.breed)
```

Kết quả

```text
Lucky is eating.
Woof Woof
Golden Retriever
```

---

# 16. Overriding Constructor

```python
class Vehicle:
    def __init__(self):
        print("Vehicle")


class Car(Vehicle):
    def __init__(self):

        super().__init__()

        print("Car")
```

Kết quả

```text
Vehicle
Car
```

---

# 17. Gọi nhiều method cha

```python
class Animal:
    def eat(self):
        print("Eating")

    def sleep(self):
        print("Sleeping")
```

```python
class Dog(Animal):
    def play(self):
        print("Playing")
```

```python
dog = Dog()

dog.eat()
dog.sleep()
dog.play()
```

Kết quả

```text
Eating
Sleeping
Playing
```

---

# 18. Overriding không phải Overloading

Python

Có:

```text
Method Overriding
```

Không hỗ trợ trực tiếp:

```text
Method Overloading
```

Sai

```python
class Demo:
    def hello(self): ...

    def hello(self, name): ...
```

Method đầu sẽ bị ghi đè.

---

# 19. Khi nào nên dùng kế thừa?

Nên

```text
Animal

↓

Dog
```

```text
Shape

↓

Rectangle
```

```text
Employee

↓

Manager
```

Không nên

```text
Car

↓

Engine
```

Engine không phải Car.

Đó là

```text
Composition
```

---

# 20. Ví dụ thực tế

```python
class Employee:
    def __init__(self, name):
        self.name = name

    def calculate_salary(self):
        raise NotImplementedError


class FullTimeEmployee(Employee):
    def calculate_salary(self):
        return 20_000_000


class PartTimeEmployee(Employee):
    def calculate_salary(self):
        return 8_000_000


employees = [
    FullTimeEmployee("Alice"),
    PartTimeEmployee("Bob"),
]

for employee in employees:
    print(employee.name, employee.calculate_salary())
```

Kết quả

```text
Alice 20000000
Bob 8000000
```

Đây là nền tảng của **Polymorphism**, sẽ học ở các buổi sau.

---

# 21. `super()` thực chất là gì?

Nhiều người nghĩ:

```python
super()
```

nghĩa là:

> "Gọi class cha"

Điều này **không hoàn toàn đúng**.

Thực tế:

```text
super()

↓

Tìm class tiếp theo

trong MRO
```

Ví dụ với kế thừa đơn:

```text
Dog

↓

Animal

↓

object
```

thì `super()` sẽ tìm đến `Animal`.

Trong Multiple Inheritance, `super()` **không nhất thiết** gọi class cha trực tiếp mà gọi **class tiếp theo trong MRO**. Đây là lý do `super()` rất quan trọng trong thiết kế class có nhiều lớp kế thừa.

---

# Best Practices

✅ Chỉ dùng kế thừa khi tồn tại quan hệ **IS-A**.

✅ Luôn gọi `super().__init__()` nếu class cha có khởi tạo quan trọng.

✅ Không sao chép code từ class cha xuống class con.

✅ Overriding chỉ khi thực sự cần thay đổi hành vi.

---

# Những lỗi người mới thường gặp

## Lỗi 1: Quên gọi `super().__init__()`

```python
class Animal:
    def __init__(self):
        self.name = "Unknown"


class Dog(Animal):
    def __init__(self):
        self.breed = "Golden"


dog = Dog()

print(dog.name)
```

Lỗi:

```text
AttributeError
```

Vì `name` chưa bao giờ được khởi tạo.

---

## Lỗi 2: Kế thừa sai quan hệ

Sai

```text
Car

↓

Engine
```

Đúng

```text
Car

HAS-A

Engine
```

---

## Lỗi 3: Ghi đè method nhưng quên giữ logic của class cha

Nếu method cha thực hiện kiểm tra hoặc ghi log quan trọng, việc ghi đè hoàn toàn có thể làm mất logic đó. Hãy cân nhắc gọi:

```python
super().method_name()
```

---

# Bài tập

## Bài 1

Viết class:

```text
Animal
```

Method:

* `eat()`
* `sleep()`

Tạo:

```text
Dog
Cat
```

Kế thừa từ `Animal`.

---

## Bài 2

Viết class:

```text
Person
```

Constructor:

* `name`
* `age`

Viết class:

```text
Student
```

Thêm:

* `student_id`

Sử dụng `super().__init__()`.

---

## Bài 3

Viết class:

```text
Shape
```

Method:

```python
area()
```

Sau đó tạo:

* `Rectangle`
* `Circle`

Ghi đè `area()`.

---

## Bài 4

In ra:

```python
print(ClassName.mro())
```

Cho:

* `Dog`
* `Cat`
* `Student`

Giải thích thứ tự MRO.

---

## Bài 5 (Nâng cao)

Thiết kế hệ thống:

```text
Employee
│
├── FullTimeEmployee
├── PartTimeEmployee
└── Freelancer
```

Yêu cầu:

* Class cha có:

  * `name`
  * `calculate_salary()`
* Mỗi class con ghi đè `calculate_salary()` theo cách riêng.
* Viết một hàm:

```python
def print_salary(employee): ...
```

Hàm này nhận **bất kỳ đối tượng** nào kế thừa `Employee` và in tên cùng mức lương. Đây là bước chuẩn bị cho **đa hình (Polymorphism)**.

---

# Tóm tắt buổi học

* **Inheritance** cho phép class con tái sử dụng thuộc tính và phương thức của class cha.
* Chỉ nên dùng kế thừa khi có quan hệ **IS-A**.
* `super()` giúp gọi constructor hoặc method của lớp tiếp theo trong **MRO**, không chỉ đơn thuần là "class cha".
* **Method Overriding** cho phép class con thay đổi hành vi của class cha.
* Python tra cứu method theo **Method Resolution Order (MRO)**, bắt đầu từ class hiện tại, sau đó đến các class cha và cuối cùng là `object`.

> **Buổi 10** chúng ta sẽ học **Polymorphism (Đa hình)**: Duck Typing, ABC (Abstract Base Class), `abc.ABC`, `@abstractmethod`, Protocol (`typing.Protocol`) và cách xây dựng hệ thống mở rộng mà không cần phụ thuộc vào kiểu cụ thể. Đây là một trong những tư tưởng cốt lõi giúp Python linh hoạt hơn nhiều ngôn ngữ OOP truyền thống.
