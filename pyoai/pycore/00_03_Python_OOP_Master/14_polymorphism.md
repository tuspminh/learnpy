# Python OOP Master – Buổi 14

# Polymorphism (Đa hình) – Linh hồn của OOP trong Python

> Sau khi đã học:
>
> * ✅ Class
> * ✅ Object
> * ✅ Property
> * ✅ Descriptor
> * ✅ Inheritance
> * ✅ `super()`
> * ✅ Overriding
> * ✅ Multiple Inheritance
> * ✅ Mixins
>
> thì hôm nay chúng ta học **Polymorphism** – một trong **4 trụ cột của OOP**.
>
> Nếu **Inheritance** giúp tái sử dụng code thì **Polymorphism** giúp **mở rộng hệ thống mà không phải sửa code cũ**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Polymorphism là gì.
* Hiểu Dynamic Dispatch.
* Biết lợi ích của đa hình.
* Tránh lạm dụng `if...elif...else`.
* Thiết kế code mở rộng tốt.
* Chuẩn bị cho Duck Typing và ABC.

---

# 1. Polymorphism là gì?

**Polymorphism** có nghĩa là:

> **Một interface – nhiều cách thực thi (One Interface, Many Implementations).**

Ví dụ

```text
Animal

↓

speak()
```

Có nhiều cách thực hiện

```text
Dog

↓

Woof
```

```text
Cat

↓

Meow
```

```text
Duck

↓

Quack
```

Cùng một lời gọi:

```python
animal.speak()
```

Nhưng kết quả khác nhau.

Đó là Polymorphism.

---

# 2. Ví dụ đầu tiên

```python
class Animal:
    def speak(self):
        print("Unknown")


class Dog(Animal):
    def speak(self):
        print("Woof")


class Cat(Animal):
    def speak(self):
        print("Meow")
```

```python
animals = [
    Dog(),
    Cat(),
]

for animal in animals:
    animal.speak()
```

Kết quả

```text
Woof
Meow
```

---

# 3. Không cần biết kiểu cụ thể

Quan sát

```python
for animal in animals:
    animal.speak()
```

Không có

```python
if isinstance(animal, Dog):
```

Không có

```python
if isinstance(animal, Cat):
```

Đây là sức mạnh của Polymorphism.

---

# 4. Không dùng Polymorphism

Nhiều người mới viết

```python
class Dog:
    def bark(self):
        print("Woof")


class Cat:
    def meow(self):
        print("Meow")
```

Sau đó

```python
if isinstance(animal, Dog):
    animal.bark()

elif isinstance(animal, Cat):
    animal.meow()
```

Code ngày càng dài khi thêm loại mới.

---

# 5. Dùng Polymorphism

```python
class Animal:
    def speak(self):
        raise NotImplementedError
```

```python
class Dog(Animal):
    def speak(self):
        print("Woof")


class Cat(Animal):
    def speak(self):
        print("Meow")
```

```python
def make_sound(animal):

    animal.speak()
```

Sử dụng

```python
make_sound(Dog())

make_sound(Cat())
```

---

# 6. Dynamic Dispatch

Python quyết định

```python
animal.speak()
```

ở runtime.

Ví dụ

```python
animal = Dog()
```

↓

```python
animal.speak()
```

↓

Python gọi

```python
Dog.speak()
```

Không gọi

```python
Animal.speak()
```

---

# 7. Ví dụ thực tế

```python
class Payment:
    def pay(self, amount):
        raise NotImplementedError
```

```python
class CashPayment(Payment):
    def pay(self, amount):

        print(f"Cash: {amount}")


class CardPayment(Payment):
    def pay(self, amount):

        print(f"Card: {amount}")
```

```python
def checkout(payment, amount):

    payment.pay(amount)
```

```python
checkout(CashPayment(), 500)

checkout(CardPayment(), 500)
```

Kết quả

```text
Cash: 500
Card: 500
```

---

# 8. Thêm loại mới

```python
class QRPayment(Payment):
    def pay(self, amount):

        print(f"QR: {amount}")
```

Không cần sửa

```python
checkout()
```

Chỉ cần

```python
checkout(QRPayment(), 500)
```

Đây là nguyên lý

```text
Open for Extension

Closed for Modification
```

chúng ta sẽ học kỹ ở phần **SOLID**.

---

# 9. Ví dụ về Shape

```python
class Shape:
    def area(self):
        raise NotImplementedError
```

```python
class Rectangle(Shape):
    def __init__(self, width, height):

        self.width = width

        self.height = height

    def area(self):

        return self.width * self.height
```

```python
class Circle(Shape):
    def __init__(self, radius):

        self.radius = radius

    def area(self):

        import math

        return math.pi * self.radius**2
```

```python
shapes = [Rectangle(5, 3), Circle(10)]

for shape in shapes:
    print(shape.area())
```

---

# 10. Đa hình với Property

```python
class Employee:
    @property
    def salary(self):
        raise NotImplementedError
```

```python
class Manager(Employee):
    @property
    def salary(self):
        return 3000
```

```python
class Staff(Employee):
    @property
    def salary(self):
        return 1500
```

```python
employees = [Manager(), Staff()]

for employee in employees:
    print(employee.salary)
```

---

# 11. Đa hình với Magic Method

```python
class Dog:
    def __str__(self):

        return "Dog"
```

```python
class Cat:
    def __str__(self):

        return "Cat"
```

```python
animals = [Dog(), Cat()]

for animal in animals:
    print(animal)
```

Python gọi

```python
__str__()
```

khác nhau.

---

# 12. Ví dụ Logger

```python
class Logger:
    def log(self, message):

        raise NotImplementedError
```

```python
class ConsoleLogger(Logger):
    def log(self, message):

        print(message)
```

```python
class FileLogger(Logger):
    def log(self, message):

        print(f"Save {message}")
```

```python
def write_log(logger):

    logger.log("Hello")
```

---

# 13. Ví dụ Notification

```python
class Notification:
    def send(self, message):

        raise NotImplementedError
```

```python
class Email(Notification):
    def send(self, message):

        print("Email:", message)
```

```python
class SMS(Notification):
    def send(self, message):

        print("SMS:", message)
```

```python
class Push(Notification):
    def send(self, message):

        print("Push:", message)
```

```python
notifications = [Email(), SMS(), Push()]

for notify in notifications:
    notify.send("Hello")
```

---

# 14. Polymorphism trong Framework

Ví dụ Flask

```python
response.render()
```

Có thể là

```text
HTML
```

hoặc

```text
JSON
```

---

SQLAlchemy

```python
session.commit()
```

↓

Database khác nhau.

---

Django

```python
Model.save()
```

↓

Override.

---

# 15. Polymorphism và Dependency Injection

Ví dụ

```python
class UserService:
    def __init__(self, logger):

        self.logger = logger
```

Có thể truyền

```python
ConsoleLogger()
```

hoặc

```python
FileLogger()
```

Không cần sửa

```python
UserService
```

---

# 16. Ví dụ hoàn chỉnh

```python
class Payment:
    def pay(self, amount):
        raise NotImplementedError


class CashPayment(Payment):
    def pay(self, amount):
        print(f"Cash payment: {amount}")


class CardPayment(Payment):
    def pay(self, amount):
        print(f"Card payment: {amount}")


class QRPayment(Payment):
    def pay(self, amount):
        print(f"QR payment: {amount}")


class Checkout:
    def process(self, payment, amount):

        payment.pay(amount)


checkout = Checkout()

payments = [
    CashPayment(),
    CardPayment(),
    QRPayment(),
]

for payment in payments:
    checkout.process(payment, 1000)
```

Kết quả

```text
Cash payment: 1000
Card payment: 1000
QR payment: 1000
```

---

# 17. Sơ đồ

```text
             Payment
                 │
      ┌──────────┼──────────┐
      │          │          │
 CashPayment CardPayment QRPayment
      │          │          │
      └──────────┼──────────┘
                 │
         payment.pay()
```

Một lời gọi

```python
payment.pay()
```

Nhiều cách thực hiện.

---

# 18. Polymorphism vs Inheritance

Inheritance

```text
Mục tiêu

↓

Tái sử dụng code
```

Polymorphism

```text
Mục tiêu

↓

Mở rộng hành vi
```

Hai khái niệm liên quan nhưng không giống nhau.

---

# 19. Khi nào nên dùng?

Rất phù hợp với:

* Payment
* Storage
* Export
* Logger
* Notification
* Parser
* Scraper
* Authentication
* Database Driver
* AI Model
* Cache Backend

Đây đều là các thành phần có nhiều cách triển khai nhưng cùng một giao diện.

---

# 20. Những lỗi người mới thường gặp

## Lỗi 1

Viết

```python
if type(obj) == Dog:
```

Thay vì

```python
obj.speak()
```

---

## Lỗi 2

Lạm dụng

```python
isinstance()
```

Nếu phải kiểm tra kiểu ở nhiều nơi, có thể thiết kế của bạn chưa tận dụng được Polymorphism.

---

## Lỗi 3

Mỗi class dùng tên method khác nhau

```python
Dog

↓

bark()
```

```python
Cat

↓

meow()
```

Nên thống nhất

```python
speak()
```

để client code không cần quan tâm kiểu cụ thể.

---

# 21. Bài toán thực tế (Ứng dụng vào dự án cào truyện)

Trong dự án **app cào truyện** mà bạn đang học, Polymorphism rất hữu ích.

```python
class BaseParser:
    def parse(self, html):
        raise NotImplementedError
```

```python
class TruyenFullParser(BaseParser):
    def parse(self, html):
        print("Parsing TruyenFull")
```

```python
class BachNgocSachParser(BaseParser):
    def parse(self, html):
        print("Parsing BachNgocSach")
```

```python
def crawl(parser, html):
    return parser.parse(html)
```

Khi muốn hỗ trợ website mới:

```python
class TangThuVienParser(BaseParser):
    def parse(self, html):
        print("Parsing TangThuVien")
```

Không cần sửa hàm `crawl()`. Đây chính là sức mạnh của Polymorphism kết hợp với nguyên tắc **Open/Closed**.

---

# Best Practices

✅ Thiết kế các class có **cùng tên phương thức** nếu chúng đại diện cho cùng một hành vi.

✅ Để client code làm việc với **interface/hành vi**, không làm việc với kiểu cụ thể.

✅ Tránh `if/elif` để phân nhánh theo kiểu đối tượng nếu có thể giải quyết bằng Polymorphism.

---

# Bài tập

## Bài 1

Tạo:

```text
Animal
```

Các class:

* Dog
* Cat
* Duck

Override:

```python
speak()
```

Viết:

```python
def make_sound(animal):
    animal.speak()
```

---

## Bài 2

Thiết kế hệ thống thanh toán:

* CashPayment
* CardPayment
* QRPayment
* BankTransferPayment

Viết:

```python
checkout(payment, amount)
```

Không dùng `if`.

---

## Bài 3

Thiết kế:

```text
Storage
```

Các class:

* LocalStorage
* S3Storage
* FTPStorage

Method:

```python
save(filename)
```

Viết:

```python
backup(storage)
```

---

## Bài 4

Thiết kế:

```text
Notification
```

Các class:

* EmailNotification
* SMSNotification
* PushNotification

Viết:

```python
broadcast(notifications, message)
```

Nhận danh sách các đối tượng và gửi thông báo.

---

## Bài 5 (Nâng cao)

Thiết kế kiến trúc cho dự án **app cào truyện**:

```text
BaseSource
    │
    ├── TruyenFullSource
    ├── BachNgocSachSource
    ├── TangThuVienSource
    └── ...
```

Mỗi class triển khai:

```python
fetch_chapter(url)
```

Viết một hàm:

```python
def download(source, url):
    return source.fetch_chapter(url)
```

Yêu cầu:

* Không dùng `if source_name == ...`.
* Khi thêm nguồn truyện mới, không cần sửa hàm `download()`.

---

# Tóm tắt buổi học

* **Polymorphism** là khả năng **một giao diện, nhiều cách triển khai**.
* Python thực hiện đa hình thông qua **Dynamic Dispatch**: phương thức được chọn theo kiểu thực tế của đối tượng tại runtime.
* Polymorphism giúp loại bỏ nhiều câu lệnh `if/elif`, làm mã nguồn dễ mở rộng và tuân theo nguyên tắc **Open/Closed**.
* Đây là nền tảng cho các kiến trúc và framework hiện đại, đặc biệt hữu ích trong các hệ thống plugin, parser, storage, payment và dự án cào truyện.

> **Buổi 15** chúng ta sẽ học **Duck Typing** – một triết lý đặc trưng của Python: *"If it walks like a duck and quacks like a duck, then it is a duck."* Bạn sẽ thấy rằng trong nhiều trường hợp, Python **không cần kế thừa** vẫn có thể đạt được đa hình một cách tự nhiên và linh hoạt.
