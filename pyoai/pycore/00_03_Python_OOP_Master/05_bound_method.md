# Python OOP Master – Buổi 5

# Method trong Python OOP (Instance Method, Bound Method và cơ chế hoạt động)

> Đây là một trong những chủ đề mà ngay cả nhiều lập trình viên Python đã đi làm vẫn chưa hiểu rõ. Sau buổi này, bạn sẽ biết **method thực chất là gì**, Python biến một function thành method như thế nào, `self` được truyền ra sao, và vì sao có khái niệm **bound method**.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Function và Method khác nhau như thế nào.
* Hiểu Instance Method.
* Hiểu Bound Method.
* Hiểu Unbound Function.
* Hiểu Python tự truyền `self`.
* Biết cách Python thực thi `object.method()`.
* Biết cách thiết kế method theo chuẩn.

---

# 1. Method là gì?

Một **Method** là **Function nằm bên trong Class**.

Ví dụ:

```python
class Student:
    def hello(self):
        print("Hello")
```

Ở đây:

```python
def hello(self):
```

là **Method**.

---

# 2. Function và Method khác nhau

Ví dụ Function

```python
def hello():
    print("Hello")
```

Gọi

```python
hello()
```

---

Ví dụ Method

```python
class Student:
    def hello(self):
        print("Hello")
```

Gọi

```python
s = Student()

s.hello()
```

---

Khác nhau

Function

```text
hello()
```

Method

```text
object.method()
```

---

# 3. Instance Method

Đây là loại method phổ biến nhất.

Ví dụ

```python
class Dog:
    def bark(self):
        print("Woof")
```

```python
dog = Dog()

dog.bark()
```

Kết quả

```text
Woof
```

---

# 4. self đến từ đâu?

Ta viết

```python
dog.bark()
```

Python thực chất thực hiện

```python
Dog.bark(dog)
```

Nghĩa là

```text
dog

↓

self
```

---

Ví dụ

```python
class Dog:
    def bark(self):
        print(self)
```

```python
dog = Dog()

dog.bark()
```

Ví dụ kết quả

```text
<__main__.Dog object at 0x...>
```

`self` chính là object đang gọi method.

---

# 5. Chứng minh

```python
class Dog:
    def bark(self):
        print(id(self))


dog = Dog()

print(id(dog))

dog.bark()
```

Ví dụ kết quả

```text
140645260576944
140645260576944
```

Hai giá trị giống nhau.

---

# 6. Có thể gọi Method từ Class không?

Có.

Ví dụ

```python
class Dog:
    def bark(self):
        print("Woof")
```

Có thể

```python
dog = Dog()

Dog.bark(dog)
```

Kết quả

```text
Woof
```

---

Nếu

```python
Dog.bark()
```

Sẽ lỗi

```text
TypeError
```

Vì thiếu

```text
self
```

---

# 7. Method thực chất là Function

Điều này rất thú vị.

Ví dụ

```python
class Student:
    def hello(self):
        print("Hello")
```

Kiểm tra

```python
print(Student.hello)
```

Ví dụ kết quả

```text
<function Student.hello at 0x...>
```

Nghĩa là

Trong Class

```text
Method

↓

Function
```

---

# 8. Bound Method

Bây giờ

```python
class Student:
    def hello(self):
        print("Hello")
```

```python
s = Student()

print(s.hello)
```

Ví dụ kết quả

```text
<bound method Student.hello of <Student object at ...>>
```

Khác hẳn.

---

Python đã tạo

```text
Bound Method
```

---

# 9. Bound nghĩa là gì?

Bound

=

Đã gắn với object.

Ví dụ

```text
Function

↓

Student.hello
```

Khi lấy

```python
s.hello
```

Python tạo

```text
Bound Method

↓

self = s
```

Cho nên

```python
s.hello()
```

không cần truyền self.

---

# 10. Minh họa

```text
Student.hello

↓

Function
```

Sau đó

```text
s.hello

↓

Bound Method

↓

self = s
```

---

# 11. Kiểm tra kiểu

```python
class Student:
    def hello(self):
        pass


s = Student()

print(type(Student.hello))
print(type(s.hello))
```

Ví dụ

```text
<class 'function'>

<class 'method'>
```

Đây là sự khác biệt rất quan trọng.

---

# 12. Method gọi Method

```python
class Dog:
    def bark(self):
        print("Woof")

    def greet(self):
        self.bark()
```

```python
dog = Dog()

dog.greet()
```

Kết quả

```text
Woof
```

Không nên viết

```python
Dog.bark(self)
```

trừ khi thật sự cần.

---

# 13. self luôn là object hiện tại

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increase(self):
        self.value += 1

    def display(self):
        print(self.value)
```

```python
c1 = Counter()
c2 = Counter()

c1.increase()
c1.increase()

c2.increase()

c1.display()
c2.display()
```

Kết quả

```text
2
1
```

Mỗi object quản lý trạng thái của riêng mình.

---

# 14. Có thể lưu Method vào biến

```python
class Cat:
    def meow(self):
        print("Meow")
```

```python
cat = Cat()

sound = cat.meow

sound()
```

Kết quả

```text
Meow
```

Vì

```text
sound

↓

Bound Method
```

---

# 15. Method là First-class Object

Method cũng là object.

Ví dụ

```python
class User:
    def hello(self):
        print("Hello")
```

```python
u = User()

methods = [
    u.hello,
]

methods[0]()
```

Kết quả

```text
Hello
```

Điều này được dùng rất nhiều trong:

* Event System
* Callback
* GUI Framework
* Scheduler
* Plugin
* Observer Pattern

---

# 16. Ví dụ hoàn chỉnh

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            print("Không đủ số dư")
            return

        self.balance -= amount

    def display(self):
        print(f"Owner   : {self.owner}")
        print(f"Balance : {self.balance}")
        print("-" * 30)


account = BankAccount("Alice", 1000)

account.display()

account.deposit(500)
account.withdraw(300)

account.display()

operation = account.deposit
operation(200)

account.display()
```

Kết quả

```text
Owner   : Alice
Balance : 1000
------------------------------
Owner   : Alice
Balance : 1200
------------------------------
Owner   : Alice
Balance : 1400
------------------------------
```

---

# 17. Bên trong Python xảy ra điều gì?

Khi viết:

```python
account.deposit(100)
```

Python thực hiện tương đương:

```python
BankAccount.deposit(account, 100)
```

Quy trình:

```text
account.deposit(100)

↓

Tìm deposit trong class

↓

Tạo Bound Method

↓

self = account

↓

Gọi Function

↓

deposit(account, 100)
```

Đây chính là lý do vì sao bạn **không cần truyền `self`** khi gọi method từ object.

---

# 18. Thực hành với `__dict__`

```python
class Demo:
    def hello(self):
        print("Hello")


d = Demo()

print(d.__dict__)
print(Demo.__dict__.keys())
```

Kết quả (rút gọn):

```text
{}
dict_keys([
    '__module__',
    'hello',
    '__dict__',
    '__weakref__',
    '__doc__'
])
```

Lưu ý:

* `hello` nằm trong **Class Namespace**.
* `d` không chứa `hello` trong `__dict__`.
* Khi truy cập `d.hello`, Python tạo **Bound Method** một cách động.

---

# Best Practices

* Luôn gọi method thông qua `self.method()` khi muốn tái sử dụng logic trong cùng class.
* Đặt tên method bằng **snake_case** theo PEP 8.
* Mỗi method chỉ nên thực hiện **một nhiệm vụ rõ ràng**.
* Hạn chế viết method quá dài; nếu trên 30–50 dòng, hãy cân nhắc tách nhỏ.

---

# Những lỗi người mới thường gặp

### Lỗi 1: Quên `self`

```python
class Student:
    def hello():
        print("Hello")
```

Gọi:

```python
Student().hello()
```

Kết quả:

```text
TypeError: hello() takes 0 positional arguments but 1 was given
```

---

### Lỗi 2: Truyền `self` thủ công

Sai:

```python
dog = Dog()
dog.bark(dog)
```

Đúng:

```python
dog.bark()
```

---

### Lỗi 3: Gọi method qua class mà không truyền object

Sai:

```python
Dog.bark()
```

Đúng:

```python
Dog.bark(dog)
```

hoặc đơn giản hơn:

```python
dog.bark()
```

---

# Bài tập

## Bài 1

Viết class `Calculator` với các method:

* `add(a, b)`
* `subtract(a, b)`
* `multiply(a, b)`
* `divide(a, b)`

Tạo object và gọi các method.

---

## Bài 2

Viết class `Circle`

Thuộc tính:

* `radius`

Method:

* `area()`
* `circumference()`

Kiểm tra rằng `self` luôn là object đang gọi.

---

## Bài 3

Viết class `Counter`

* `increase()`
* `decrease()`
* `reset()`
* `display()`

Tạo hai object độc lập và chứng minh trạng thái không bị chia sẻ.

---

## Bài 4

Viết class `MusicPlayer`

Method:

* `play()`
* `pause()`
* `stop()`

Lưu các method vào một danh sách và gọi lần lượt:

```python
actions = [
    player.play,
    player.pause,
    player.stop,
]

for action in actions:
    action()
```

Quan sát rằng mỗi phần tử trong danh sách là một **Bound Method**.

---

## Bài 5 (Nâng cao)

Cho đoạn mã:

```python
class Demo:
    def show(self, message):
        print(f"{self=}")
        print(f"{message=}")


d = Demo()

print(Demo.show)
print(d.show)

Demo.show(d, "Hello")
d.show("World")
```

1. Dự đoán kết quả trước khi chạy.
2. Giải thích sự khác nhau giữa `Demo.show` và `d.show`.
3. Giải thích vì sao `d.show("World")` không cần truyền `self`.

---

# Tóm tắt buổi học

* **Method** thực chất là **function được định nghĩa trong class**.
* Truy cập method qua **class** nhận được một `function`; truy cập qua **object** nhận được một **bound method**.
* `self` không phải từ khóa mà là tham chiếu đến object hiện tại, được Python truyền tự động khi gọi `object.method()`.
* Python thực hiện `object.method(args)` tương đương với `Class.method(object, args)`.
* Hiểu rõ **bound method** là nền tảng để học `@staticmethod`, `@classmethod`, descriptor và cơ chế hoạt động của thuộc tính trong các buổi tiếp theo.

> **Buổi 6** chúng ta sẽ bắt đầu **Encapsulation (Đóng gói)**: tìm hiểu `public`, `_protected`, `__private`, **name mangling**, cách Python bảo vệ dữ liệu (và giới hạn của nó), cùng các quy ước thiết kế class theo chuẩn Python.
