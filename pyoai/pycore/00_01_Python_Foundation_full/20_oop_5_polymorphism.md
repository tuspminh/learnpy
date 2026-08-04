# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 20: OOP - Phần 5: Đa hình (Polymorphism), Duck Typing, Abstract Base Class (ABC), Protocol và Thiết kế hệ thống mở rộng

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của Đa hình (Polymorphism).
> - Hiểu triết lý **Duck Typing** của Python.
> - Thành thạo **Abstract Base Class (ABC)** và `@abstractmethod`.
> - Hiểu **Protocol** (Structural Typing) trong Python hiện đại.
> - Biết khi nào dùng Duck Typing, ABC hay Protocol.
> - Thiết kế hệ thống plugin và thanh toán có khả năng mở rộng.

---

# 1. Đa hình (Polymorphism) là gì?

**Polymorphism** có nghĩa là:

> **Nhiều đối tượng khác nhau có thể được sử dụng thông qua cùng một giao diện (interface), nhưng mỗi đối tượng có cách thực hiện riêng.**

Ví dụ ngoài đời:

Điều khiển TV.

Bạn chỉ cần bấm nút:

```text-x-trilium-auto
Power
```

Nhưng:

- TV Sony bật theo cách của Sony.
- TV Samsung bật theo cách của Samsung.
- TV LG bật theo cách của LG.

Người dùng chỉ biết:

```text-x-trilium-auto
Power()
```

Đó chính là đa hình.

---

# 2. Ví dụ đơn giản

```text-x-trilium-auto
class Dog:

    def speak(self):
        print("Gâu gâu")


class Cat:

    def speak(self):
        print("Meo meo")


class Duck:

    def speak(self):
        print("Cạp cạp")
```

Sử dụng:

```text-x-trilium-auto
animals = [
    Dog(),
    Cat(),
    Duck()
]

for animal in animals:
    animal.speak()
```

Kết quả:

```text-x-trilium-auto
Gâu gâu
Meo meo
Cạp cạp
```

Mặc dù:

- Dog khác Cat
- Cat khác Duck

Nhưng đều có:

```text-x-trilium-auto
speak()
```

---

# 3. Không cần biết kiểu dữ liệu

Đây chính là điểm mạnh.

Ta chỉ cần:

```text-x-trilium-auto
obj.speak()
```

Không cần:

```text-x-trilium-auto
if isinstance(obj, Dog):
    ...

elif isinstance(obj, Cat):
    ...
```

Đây là tư duy OOP đúng.

---

# 4. Duck Typing

Python nổi tiếng với câu nói:

> **"If it walks like a duck and quacks like a duck, then it's a duck."**

Có nghĩa:

Không quan trọng Object thuộc lớp nào.

Chỉ cần:

```text-x-trilium-auto
object.run()
```

được.

Ví dụ:

```text-x-trilium-auto
class Human:

    def walk(self):
        print("Người đi")


class Robot:

    def walk(self):
        print("Robot đi")


class Dog:

    def walk(self):
        print("Chó chạy")
```

Ta có thể viết:

```text-x-trilium-auto
def start(obj):
    obj.walk()
```

Sau đó:

```text-x-trilium-auto
start(Human())
start(Robot())
start(Dog())
```

Không cần quan tâm chúng có chung lớp cha hay không.

---

# 5. Lợi ích của Duck Typing

Ví dụ:

```text-x-trilium-auto
def save(file):
    file.write("Hello")
```

Nếu:

```text-x-trilium-auto
file
```

có:

```text-x-trilium-auto
write()
```

thì hoạt động.

Có thể là:

- File thật
- File trong bộ nhớ
- Socket
- Network stream

Đây là lý do rất nhiều API của Python linh hoạt.

---

# 6. Hạn chế của Duck Typing

Nếu:

```text-x-trilium-auto
class Person:
    pass
```

Gọi:

```text-x-trilium-auto
start(Person())
```

Lỗi:

```text-x-trilium-auto
AttributeError
```

Vì:

```text-x-trilium-auto
walk()
```

không tồn tại.

Ta cần cơ chế kiểm soát tốt hơn.

---

# 7. Abstract Base Class (ABC)

Python cung cấp module:

```text-x-trilium-auto
from abc import ABC, abstractmethod
```

Ví dụ:

```text-x-trilium-auto
from abc import ABC, abstractmethod


class Animal(ABC):

    @abstractmethod
    def speak(self):
        pass
```

Đây là **lớp trừu tượng (Abstract Class)**.

Không thể tạo đối tượng:

```text-x-trilium-auto
Animal()
```

Sẽ sinh lỗi.

---

# 8. Lớp con bắt buộc phải cài đặt

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):
        print("Gâu")
```

Đúng.

Nhưng:

```text-x-trilium-auto
class Cat(Animal):
    pass
```

Sai.

Python báo lỗi khi tạo đối tượng:

```text-x-trilium-auto
Cat()
```

Vì chưa triển khai:

```text-x-trilium-auto
speak()
```

---

# 9. Ví dụ thực tế

Hệ thống thanh toán:

```text-x-trilium-auto
from abc import ABC, abstractmethod


class Payment(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

Các cổng thanh toán:

```text-x-trilium-auto
class Visa(Payment):

    def pay(self, amount):
        print(f"Thanh toán Visa: {amount}")
```

```text-x-trilium-auto
class PayPal(Payment):

    def pay(self, amount):
        print(f"Thanh toán PayPal: {amount}")
```

Ta có thể xử lý:

```text-x-trilium-auto
payments = [
    Visa(),
    PayPal()
]

for payment in payments:
    payment.pay(100)
```

---

# 10. Lợi ích của ABC

ABC đảm bảo:

- Mọi lớp con đều có cùng giao diện.
- Giảm lỗi do quên cài đặt phương thức.
- Dễ mở rộng.

---

# 11. Protocol (Python hiện đại)

Từ Python 3.8+, có:

```text-x-trilium-auto
from typing import Protocol
```

Ví dụ:

```text-x-trilium-auto
from typing import Protocol


class Flyer(Protocol):

    def fly(self):
        ...
```

Lớp:

```text-x-trilium-auto
class Bird:

    def fly(self):
        print("Bird")
```

Không cần kế thừa.

Nhưng:

```text-x-trilium-auto
Bird()
```

vẫn được xem là phù hợp với `Flyer` vì có phương thức `fly()`.

Đây gọi là **Structural Typing**.

---

# 12. Protocol khác ABC thế nào?

## ABC

```text-x-trilium-auto
class Dog(Animal):
```

Phải kế thừa.

---

## Protocol

Không cần:

```text-x-trilium-auto
class Bird:
```

Chỉ cần:

```text-x-trilium-auto
fly()
```

là đủ.

---

# 13. Ví dụ Plugin

Ta định nghĩa:

```text-x-trilium-auto
from typing import Protocol


class Plugin(Protocol):

    def run(self):
        ...
```

Plugin:

```text-x-trilium-auto
class TranslatePlugin:

    def run(self):
        print("Translate")
```

```text-x-trilium-auto
class OCRPlugin:

    def run(self):
        print("OCR")
```

Hệ thống:

```text-x-trilium-auto
def execute(plugin: Plugin):
    plugin.run()
```

Rất dễ mở rộng.

---

# 14. Polymorphism trong thực tế

Ví dụ:

```text-x-trilium-auto
payments = [

    Visa(),

    PayPal(),

    BankTransfer(),

    Crypto()
]
```

Sau đó:

```text-x-trilium-auto
for payment in payments:
    payment.pay(100)
```

Không cần:

```text-x-trilium-auto
if ...

elif ...

elif ...
```

---

# 15. Không nên lạm dụng `isinstance()`

Sai:

```text-x-trilium-auto
if isinstance(obj, Dog):
    ...

elif isinstance(obj, Cat):
    ...
```

Đúng:

```text-x-trilium-auto
obj.speak()
```

Đó mới là Polymorphism.

---

# 16. Ví dụ AI hiện đại

Các mô hình AI:

```text-x-trilium-auto
GPT

Gemini

Claude

Llama
```

Đều có:

```text-x-trilium-auto
generate(prompt)
```

Ứng dụng chỉ cần:

```text-x-trilium-auto
model.generate(...)
```

Không quan tâm bên trong.

Đó là Polymorphism.

---

# 17. Ví dụ Database

```text-x-trilium-auto
MySQL

PostgreSQL

SQLite
```

Đều có:

```text-x-trilium-auto
connect()
```

Ứng dụng chỉ cần:

```text-x-trilium-auto
db.connect()
```

---

# 18. Ví dụ Cloud

```text-x-trilium-auto
AWS

Azure

Google Cloud
```

Đều có:

```text-x-trilium-auto
upload()
```

Chương trình:

```text-x-trilium-auto
storage.upload(file)
```

---

# 19. Ví dụ GUI

Trong **PySide6**:

```text-x-trilium-auto
Button

Label

TextBox
```

Đều:

```text-x-trilium-auto
show()
hide()
```

---

# 20. Ví dụ Game

```text-x-trilium-auto
Zombie

Boss

Player
```

Đều:

```text-x-trilium-auto
update()
draw()
```

Game loop:

```text-x-trilium-auto
for obj in objects:
    obj.update()
```

---

# 21. Những lỗi phổ biến

## Lỗi 1

Lạm dụng:

```text-x-trilium-auto
if type(...)
```

Thay vào đó hãy gọi phương thức chung của đối tượng.

---

## Lỗi 2

ABC quá nhiều.

Không phải class nào cũng cần Abstract.

---

## Lỗi 3

Duck Typing không kiểm tra giao diện.

Nếu dùng trong dự án lớn, hãy cân nhắc ABC hoặc Protocol.

---

# 22. Khi nào dùng gì?

| Trường hợp | Giải pháp |
| --- | --- |
| Script nhỏ | Duck Typing |
| Thư viện | Protocol |
| Hệ thống lớn | ABC |
| Framework | ABC + Protocol |
| Plugin | Protocol |
| API nội bộ | ABC hoặc Protocol |

---

# 23. Bài tập thực hành

## Bài 1

Viết:

```text-x-trilium-auto
Animal
```

là Abstract Class.

Có:

```text-x-trilium-auto
eat()

speak()
```

Tạo:

- Dog
- Cat
- Cow

Triển khai `speak()` khác nhau.

---

## Bài 2

Viết hệ thống:

```text-x-trilium-auto
Payment
```

↓

- Visa
- PayPal
- BankTransfer

Duyệt danh sách và gọi:

```text-x-trilium-auto
pay()
```

---

## Bài 3

Tạo:

```text-x-trilium-auto
Plugin
```

Protocol.

Viết:

- OCRPlugin
- TranslatePlugin
- SpeechPlugin

---

## Bài 4

Viết:

```text-x-trilium-auto
Shape
```

↓

- Circle
- Rectangle
- Triangle

Đều có:

```text-x-trilium-auto
area()
```

Viết hàm:

```text-x-trilium-auto
print_area(shape)
```

không dùng:

```text-x-trilium-auto
isinstance()
```

---

## Bài 5

Thiết kế:

```text-x-trilium-auto
Database
```

↓

- SQLite
- PostgreSQL
- MySQL

Đều có:

```text-x-trilium-auto
connect()

close()
```

---

## Bài 6

Xây dựng hệ thống:

```text-x-trilium-auto
AIModel
```

↓

- GPT
- Claude
- Gemini

Đều có:

```text-x-trilium-auto
generate(prompt)
```

Viết hàm:

```text-x-trilium-auto
chat(model, prompt)
```

để gọi bất kỳ mô hình nào.

---

# Mini Project: Hệ thống Thanh toán Thương mại điện tử

Thiết kế:

### Abstract Class

```text-x-trilium-auto
PaymentGateway
```

Phương thức:

- `pay(amount)`
- `refund(amount)`

### Các lớp con

- `VisaGateway`
- `PayPalGateway`
- `MomoGateway`
- `BankTransferGateway`

Yêu cầu:

- Mỗi lớp có cách xử lý riêng.
- Viết hàm:

```text-x-trilium-auto
process_payment(gateway, amount)
```

chỉ gọi:

```text-x-trilium-auto
gateway.pay(amount)
```

không dùng:

```text-x-trilium-auto
if ...
```

**Mở rộng:**

- Thêm lớp `CryptoGateway` mà không cần sửa `process_payment()`.
- Ghi log giao dịch sau mỗi lần thanh toán.

---

# Tổng kết buổi 20

Hôm nay bạn đã học:

- ✅ Polymorphism.
- ✅ Duck Typing.
- ✅ Abstract Base Class (ABC).
- ✅ `@abstractmethod`.
- ✅ Protocol.
- ✅ Structural Typing.
- ✅ Thiết kế Plugin.
- ✅ Thiết kế Payment Gateway.
- ✅ Viết mã mở rộng mà không cần sửa logic hiện có.

---

# Góc lập trình viên chuyên nghiệp

Đa hình là nền tảng của nhiều nguyên tắc thiết kế phần mềm, đặc biệt là **Open/Closed Principle (OCP)**:

> **Mở để mở rộng, đóng để sửa đổi.**

Khi bạn viết một hàm như:

```text-x-trilium-auto
def process_payment(gateway, amount):
    gateway.pay(amount)
```

bạn có thể thêm `CryptoGateway`, `ApplePayGateway` hay bất kỳ cổng thanh toán mới nào mà **không cần sửa** `process_payment()`. Đây là cách các framework và hệ thống lớn được xây dựng để dễ mở rộng theo thời gian.

---

# Chuẩn bị cho Buổi 21

Ở **Buổi 21**, chúng ta sẽ học trụ cột cuối cùng của OOP:

# **Trừu tượng (Abstraction) và Thiết kế hướng đối tượng**

Bạn sẽ học:

- Abstraction là gì và khác gì với Encapsulation.
- Interface trong Python.
- Nguyên tắc **SOLID** (giới thiệu tổng quan).
- Composition nâng cao.
- Dependency Injection.
- Thiết kế hệ thống theo hướng module.
- Refactor một dự án từ mã thủ tục sang kiến trúc OOP.

Đây sẽ là buổi học giúp bạn chuyển từ **biết dùng OOP** sang **biết thiết kế phần mềm** theo tư duy của một lập trình viên Python chuyên nghiệp.
