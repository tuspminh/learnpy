# OOP Deep Dive - Buổi 12

# Polymorphism (Đa hình), Duck Typing và Triết lý OOP của Python

Đây là một trong những buổi quan trọng nhất của khóa học.

Nếu Inheritance giúp chúng ta **tái sử dụng code**, thì **Polymorphism (Đa hình)** giúp chúng ta **mở rộng hệ thống mà không phải sửa code cũ**.

Đây cũng là nơi Python khác rất nhiều so với Java và C++.

Sau buổi này bạn sẽ hiểu:

- Polymorphism là gì.
- Dynamic Dispatch hoạt động như thế nào.
- Duck Typing.
- EAFP vs LBYL.
- Vì sao Python không thích kiểm tra kiểu dữ liệu.
- Cách áp dụng vào hệ thống plugin crawler của bạn.

---

# Mục tiêu

Sau buổi học này bạn sẽ hiểu:

- Polymorphism
- Dynamic Dispatch
- Duck Typing
- EAFP
- LBYL
- Open/Closed Principle
- Viết code Pythonic

---

# 1. Polymorphism là gì?

Polymorphism có nghĩa là:

> **Cùng một lời gọi, nhưng hành vi khác nhau tùy đối tượng.**

Ví dụ:

```text-x-trilium-auto
dog.speak()

cat.speak()

bird.speak()
```

Đều gọi:

```text-x-trilium-auto
speak()
```

Nhưng:

```text-x-trilium-auto
Dog

↓

Woof
```

```text-x-trilium-auto
Cat

↓

Meow
```

```text-x-trilium-auto
Bird

↓

Tweet
```

---

# 2. Ví dụ cơ bản

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("...")
```

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):
        print("Woof")
```

```text-x-trilium-auto
class Cat(Animal):

    def speak(self):
        print("Meow")
```

Hàm:

```text-x-trilium-auto
def make_sound(animal):

    animal.speak()
```

Sử dụng

```text-x-trilium-auto
make_sound(Dog())

make_sound(Cat())
```

Kết quả

```text-x-trilium-auto
Woof

Meow
```

Hàm không biết:

- Dog
- Cat

Chỉ cần:

```text-x-trilium-auto
speak()
```

---

# 3. Dynamic Dispatch

Khi:

```text-x-trilium-auto
animal.speak()
```

Python không quyết định lúc viết code.

Mà quyết định:

```text-x-trilium-auto
Runtime
```

Quá trình này gọi là:

> Dynamic Dispatch

---

Ví dụ

```text-x-trilium-auto
animal = Dog()

animal.speak()
```

Python tìm:

```text-x-trilium-auto
Dog.speak()
```

không phải

```text-x-trilium-auto
Animal.speak()
```

---

# 4. Open/Closed Principle

Một trong SOLID.

```text-x-trilium-auto
Open for extension

Closed for modification
```

Nghĩa là:

Có thể thêm class mới

Không cần sửa code cũ.

Ví dụ

```text-x-trilium-auto
def make_sound(animal):

    animal.speak()
```

Sau này thêm

```text-x-trilium-auto
class Duck:

    def speak(self):
        print("Quack")
```

Không cần sửa

```text-x-trilium-auto
make_sound()
```

---

# 5. Đây chính là Polymorphism

```text-x-trilium-auto
make_sound()

↓

Dog

↓

Woof
```

```text-x-trilium-auto
make_sound()

↓

Cat

↓

Meow
```

```text-x-trilium-auto
make_sound()

↓

Duck

↓

Quack
```

---

# 6. Java thường làm gì?

Java thích:

```text-x-trilium-auto
if(animal instanceof Dog)
```

Hoặc

```text-x-trilium-auto
Animal animal
```

Python không thích.

---

# 7. Python có Duck Typing

Triết lý nổi tiếng:

> **If it walks like a duck and quacks like a duck, then it is a duck.**

Dịch:

Nếu nó đi như vịt

và kêu như vịt

thì coi nó là vịt.

Không quan trọng nó thuộc class nào.

---

# 8. Ví dụ

```text-x-trilium-auto
class Robot:

    def speak(self):

        print("Beep")
```

Không kế thừa Animal.

Nhưng:

```text-x-trilium-auto
make_sound(Robot())
```

Kết quả

```text-x-trilium-auto
Beep
```

Python không quan tâm:

```text-x-trilium-auto
Robot

↓

Animal?
```

Không.

Chỉ cần:

```text-x-trilium-auto
speak()
```

là đủ.

---

# 9. Đây là sức mạnh của Python

Không cần:

```text-x-trilium-auto
isinstance()
```

Không cần:

```text-x-trilium-auto
issubclass()
```

Chỉ cần:

```text-x-trilium-auto
Có method

↓

Được
```

---

# 10. Ví dụ đời thực

```text-x-trilium-auto
class File:

    def read(self):

        ...
```

```text-x-trilium-auto
class Socket:

    def read(self):

        ...
```

```text-x-trilium-auto
class MemoryBuffer:

    def read(self):

        ...
```

Hàm

```text-x-trilium-auto
def load(source):

    return source.read()
```

Không cần biết:

- File
- Socket
- Buffer

---

# 11. Không cần Interface?

Trong Java

```text-x-trilium-auto
Readable

↓

File

↓

Socket

↓

...
```

Python:

Không cần.

Duck Typing thay thế phần lớn nhu cầu này.

---

# 12. Sai lầm phổ biến

Nhiều người viết:

```text-x-trilium-auto
if isinstance(obj,Dog):

    obj.speak()

elif isinstance(obj,Cat):

    obj.speak()
```

Sai.

Nên:

```text-x-trilium-auto
obj.speak()
```

Nếu đối tượng không hỗ trợ `speak()`, chương trình sẽ báo lỗi (hoặc bạn xử lý ngoại lệ nếu cần).

---

# 13. EAFP

Python thích:

```text-x-trilium-auto
EAFP
```

Viết tắt của

```text-x-trilium-auto
Easier to Ask Forgiveness

than Permission
```

Nghĩa là:

> Cứ thử làm.

Nếu lỗi

thì xử lý.

---

Ví dụ

```text-x-trilium-auto
try:

    obj.speak()

except AttributeError:

    print("Không hỗ trợ")
```

---

# 14. LBYL

Java thích

```text-x-trilium-auto
Look Before You Leap
```

Ví dụ

```text-x-trilium-auto
if hasattr(obj,"speak"):

    obj.speak()
```

Python vẫn hỗ trợ cách này, nhưng trong nhiều tình huống **EAFP** được xem là phong cách Pythonic hơn vì tránh kiểm tra lặp và giảm khả năng race condition.

---

# 15. EAFP vs LBYL

LBYL

```text-x-trilium-auto
Có speak?

↓

Có

↓

Gọi
```

EAFP

```text-x-trilium-auto
Gọi

↓

Có lỗi?

↓

Không

↓

OK
```

---

# 16. Ví dụ Plugin

Hệ thống crawler của bạn

```text-x-trilium-auto
class TruyenFull:

    def fetch(self):
        ...
```

```text-x-trilium-auto
class BachNgocSach:

    def fetch(self):
        ...
```

Crawler

```text-x-trilium-auto
def crawl(source):

    source.fetch()
```

Không cần:

```text-x-trilium-auto
if isinstance(...)
```

Đây là Polymorphism + Duck Typing.

---

# 17. Ví dụ Parser

```text-x-trilium-auto
class HtmlParser:

    def parse(self):
        ...
```

```text-x-trilium-auto
class JsonParser:

    def parse(self):
        ...
```

```text-x-trilium-auto
class XmlParser:

    def parse(self):
        ...
```

Loader

```text-x-trilium-auto
parser.parse()
```

Không cần biết parser nào.

---

# 18. Delegation + Duck Typing

Ví dụ

```text-x-trilium-auto
class Service:

    def __init__(self,logger):

        self.logger=logger
```

Logger có thể là:

```text-x-trilium-auto
ConsoleLogger

FileLogger

DatabaseLogger
```

Miễn có:

```text-x-trilium-auto
log()
```

Service không cần sửa.

---

# 19. Khi nào nên dùng isinstance()?

Có.

Nhưng ít.

Ví dụ:

- Validation đầu vào ở API.
- Kiểm tra các kiểu dữ liệu đặc biệt.
- Tương thích với thư viện cũ.

Không nên dùng `isinstance()` chỉ để quyết định gọi phương thức nào nếu có thể thiết kế bằng đa hình.

---

# 20. So sánh

Java

```text-x-trilium-auto
Interface

↓

Compile Time
```

Python

```text-x-trilium-auto
Duck Typing

↓

Runtime
```

---

# 21. Ưu điểm

Duck Typing giúp:

- Mở rộng plugin dễ dàng.
- Không phụ thuộc vào cây kế thừa.
- Code linh hoạt.
- Dễ kiểm thử (mock object chỉ cần có các phương thức cần thiết).

---

# 22. Nhược điểm

Do kiểm tra ở runtime:

```text-x-trilium-auto
Sai method

↓

Runtime Error
```

Ví dụ

```text-x-trilium-auto
class Robot:

    def beep(self):
        ...
```

```text-x-trilium-auto
make_sound(Robot())
```

Kết quả

```text-x-trilium-auto
AttributeError
```

Đó là lý do những dự án lớn thường kết hợp:

- Type Hint
- Protocol
- ABC
- MyPy/Pyright

để phát hiện lỗi sớm hơn.

---

# 23. Áp dụng vào hệ thống crawler

Thay vì:

```text-x-trilium-auto
if source == "truyenfull":

    ...

elif source == "bachngocsach":

    ...
```

Hãy thiết kế:

```text-x-trilium-auto
class BaseSource:

    def fetch(self):
        ...
```

```text-x-trilium-auto
class TruyenFullSource:

    def fetch(self):
        ...
```

```text-x-trilium-auto
class BachNgocSach:

    def fetch(self):
        ...
```

Crawler:

```text-x-trilium-auto
def crawl(source):

    html = source.fetch()
```

Muốn thêm nguồn mới:

```text-x-trilium-auto
Viết class mới

↓

Không sửa crawl()
```

Đây chính là **Open/Closed Principle**.

---

# 24. Tổng kết

```text-x-trilium-auto
                POLYMORPHISM

                       │

         ┌─────────────┼─────────────┐

         │             │             │

  Dynamic Dispatch  Duck Typing   Runtime

         │

         ▼

 Open for Extension

 Closed for Modification
```

---

# Những điều cần nhớ

- **Polymorphism**: cùng một lời gọi, nhiều cách thực hiện.
- **Duck Typing**: quan tâm hành vi, không quá quan tâm kiểu.
- **Dynamic Dispatch**: Python quyết định phương thức nào sẽ chạy ở runtime.
- **EAFP**: cứ thử thực hiện, xử lý ngoại lệ nếu cần.
- Hạn chế lạm dụng `isinstance()` khi có thể dùng đa hình.

---

# Bài tập thực hành

## Bài 1

Tạo các lớp:

- `Dog`
- `Cat`
- `Duck`
- `Robot`

Mỗi lớp có phương thức:

```text-x-trilium-auto
speak()
```

Viết hàm:

```text-x-trilium-auto
def make_sound(obj):
    ...
```

Không được dùng:

- `isinstance()`
- `type()`

Chỉ gọi:

```text-x-trilium-auto
obj.speak()
```

---

## Bài 2

Thiết kế hệ thống logger:

- `ConsoleLogger`
- `FileLogger`
- `DatabaseLogger`

Mỗi lớp có:

```text-x-trilium-auto
log(message)
```

Viết:

```text-x-trilium-auto
class Service:
    def __init__(self, logger):
        self.logger = logger
```

Trong `Service`, chỉ gọi:

```text-x-trilium-auto
self.logger.log(...)
```

Thử thay đổi logger mà không sửa `Service`.

---

## Bài 3

Viết hai phiên bản của hàm:

```text-x-trilium-auto
def process(obj):
```

- Phiên bản 1 dùng `hasattr()` (LBYL).
- Phiên bản 2 dùng `try/except AttributeError` (EAFP).

So sánh ưu, nhược điểm của từng cách.

---

## Bài 4 (Áp dụng vào dự án crawler)

Thiết kế ba nguồn truyện:

- `TruyenFullSource`
- `BachNgocSachSource`
- `TangThuVienSource`

Mỗi lớp đều có:

```text-x-trilium-auto
fetch()
parse()
```

Viết:

```text-x-trilium-auto
class CrawlService:
    def crawl(self, source):
        html = source.fetch()
        data = source.parse(html)
        return data
```

Yêu cầu:

- Không dùng `if/elif`.
- Không dùng `isinstance()`.
- Chỉ dựa vào **Polymorphism** và **Duck Typing**.

---

# Chuẩn bị cho Buổi 13

Ở buổi tiếp theo, chúng ta sẽ đi sâu vào **Abstract Base Class (ABC)** và `abc` module:

- `ABC` là gì?
- `@abstractmethod` hoạt động như thế nào?
- Khi nào nên dùng ABC thay vì chỉ dựa vào Duck Typing?
- So sánh **ABC**, **Duck Typing** và **Protocol (PEP 544)**.
- Thiết kế `BaseSource`, `Parser`, `Repository` chuẩn cho hệ thống crawler bằng Abstract Base Class.

Đây là bước chuyển từ OOP cơ bản sang thiết kế framework và kiến trúc phần mềm chuyên nghiệp.