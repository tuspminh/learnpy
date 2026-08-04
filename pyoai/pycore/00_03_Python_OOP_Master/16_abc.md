# Python OOP Master – Buổi 16

# Abstract Base Class (ABC) – Thiết kế Contract chuyên nghiệp trong Python

> Hôm nay chúng ta học một trong những chủ đề quan trọng nhất của OOP trong Python:
>
> **Abstract Base Class (ABC)**.
>
> Nếu Duck Typing trả lời:
>
> > "Object này có làm được việc không?"
>
> thì ABC trả lời:
>
> > "Object này **bắt buộc** phải có những hành vi nào?"

ABC chính là công cụ để định nghĩa **Contract (Hợp đồng)** giữa các class.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Abstract Base Class là gì.
* Biết cách sử dụng `abc.ABC`.
* Biết `@abstractmethod`.
* Hiểu Contract trong OOP.
* Phân biệt ABC và Duck Typing.
* Hiểu Virtual Subclass.
* Hiểu `__subclasshook__()`.
* Áp dụng ABC vào framework cào truyện.

---

# 1. Contract là gì?

Ví dụ:

Bạn thuê một đơn vị giao hàng.

Bạn không quan tâm:

* họ đi xe máy
* ô tô
* drone

Bạn chỉ yêu cầu:

```text
Phải có:

deliver(package)
```

Đó chính là **Contract**.

---

# 2. Abstract Base Class là gì?

ABC là class:

* không dùng để tạo object
* dùng để định nghĩa interface
* bắt class con phải cài đặt

Ví dụ

```text
Payment

↓

pay()
```

Các class con

```text
CashPayment

CardPayment

QRPayment
```

đều phải có

```python
pay()
```

---

# 3. Module abc

Python có module

```python
abc
```

Ví dụ

```python
from abc import ABC, abstractmethod
```

---

# 4. ABC đầu tiên

```python
from abc import ABC
```

```python
class Animal(ABC):
    pass
```

Đây đã là một Abstract Base Class.

---

# 5. Abstract Method

```python
from abc import ABC
from abc import abstractmethod


class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass
```

---

# 6. Không thể khởi tạo

```python
animal = Animal()
```

Lỗi

```text
TypeError

Can't instantiate abstract class Animal
```

---

# 7. Class con chưa implement

```python
class Dog(Animal):
    pass
```

```python
dog = Dog()
```

Lỗi

```text
TypeError

Can't instantiate abstract class Dog
```

---

# 8. Implement đầy đủ

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

# 9. ABC có thể có method thường

Không phải mọi method đều abstract.

```python
from abc import ABC
from abc import abstractmethod


class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

    def sleep(self):
        print("Sleeping")
```

Class con

```python
class Dog(Animal):
    def speak(self):
        print("Woof")
```

Sử dụng

```python
dog = Dog()

dog.sleep()
```

---

# 10. Abstract Property

```python
from abc import ABC
from abc import abstractmethod


class Employee(ABC):
    @property
    @abstractmethod
    def salary(self):
        pass
```

Class con

```python
class Manager(Employee):
    @property
    def salary(self):
        return 5000
```

---

# 11. Abstract Class Method

```python
class Base(ABC):
    @classmethod
    @abstractmethod
    def create(cls):
        pass
```

---

# 12. Abstract Static Method

```python
class Base(ABC):
    @staticmethod
    @abstractmethod
    def version():
        pass
```

---

# 13. Ví dụ Payment

```python
from abc import ABC
from abc import abstractmethod


class Payment(ABC):
    @abstractmethod
    def pay(self, amount):
        pass
```

```python
class CashPayment(Payment):
    def pay(self, amount):
        print(f"Cash {amount}")


class CardPayment(Payment):
    def pay(self, amount):
        print(f"Card {amount}")
```

```python
def checkout(payment, amount):

    payment.pay(amount)
```

---

# 14. Ví dụ Parser

Đây là ví dụ gần với framework cào truyện.

```python
from abc import ABC
from abc import abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse_chapter(self, html):
        pass
```

```python
class TruyenFullParser(Parser):
    def parse_chapter(self, html):
        return "Chapter"
```

```python
class BachNgocSachParser(Parser):
    def parse_chapter(self, html):
        return "Chapter"
```

Client

```python
def crawl(parser, html):

    return parser.parse_chapter(html)
```

---

# 15. Virtual Subclass

ABC có thể đăng ký class.

```python
from abc import ABC


class Animal(ABC):
    pass
```

```python
class Dog:
    pass
```

Đăng ký

```python
Animal.register(Dog)
```

Kiểm tra

```python
print(issubclass(Dog, Animal))
```

↓

```text
True
```

Mặc dù

```python
Dog
```

không kế thừa

```python
Animal
```

---

# 16. `__subclasshook__()`

ABC có thể tùy chỉnh cách

```python
issubclass()
```

hoạt động.

Ví dụ

```python
from abc import ABCMeta


class Parser(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):

        if any("parse" in B.__dict__ for B in C.__mro__):
            return True

        return NotImplemented
```

Nếu class có

```python
parse()
```

↓

Được xem như subclass.

Đây là nền tảng của **Structural Typing**.

---

# 17. ABC vs Duck Typing

Duck Typing

```python
obj.parse()
```

Nếu lỗi

↓

Exception.

ABC

```python
class Parser(ABC)
```

↓

Lỗi ngay khi lập trình viên quên implement.

ABC giúp phát hiện sai sớm hơn.

---

# 18. ABC vs Protocol

ABC

```python
class Parser(ABC):
```

↓

Nominal Typing

(phải kế thừa)

Protocol

```python
class Parser(Protocol):
```

↓

Structural Typing

(chỉ cần đúng interface)

Chúng ta sẽ học Protocol sâu ở phần `typing`.

---

# 19. Ví dụ hoàn chỉnh

```python
from abc import ABC
from abc import abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, filename):
        pass


class LocalStorage(Storage):
    def save(self, filename):

        print("Local:", filename)


class CloudStorage(Storage):
    def save(self, filename):

        print("Cloud:", filename)


class Backup:
    def backup(self, storage, filename):

        storage.save(filename)


backup = Backup()

storages = [LocalStorage(), CloudStorage()]

for storage in storages:
    backup.backup(storage, "book.txt")
```

---

# 20. ABC trong framework cào truyện

Đây là cách thiết kế rất phù hợp.

```text
BaseCrawler (ABC)
│
├── TruyenFullCrawler
├── TangThuVienCrawler
├── BachNgocSachCrawler
```

```python
from abc import ABC
from abc import abstractmethod


class BaseCrawler(ABC):
    @abstractmethod
    def fetch_book(self, url):
        pass

    @abstractmethod
    def fetch_chapter(self, url):
        pass

    @abstractmethod
    def search(self, keyword):
        pass
```

Mỗi nguồn truyện **bắt buộc** phải triển khai đủ ba phương thức này.

Nếu quên, Python sẽ báo lỗi ngay khi khởi tạo crawler.

---

# 21. ABC trong Repository Pattern

```python
from abc import ABC
from abc import abstractmethod


class Repository(ABC):
    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def delete(self, id):
        pass
```

```python
class SQLiteRepository(Repository): ...
```

```python
class MemoryRepository(Repository): ...
```

Client code chỉ làm việc với `Repository`, không phụ thuộc vào cách lưu trữ cụ thể.

---

# ABC kết hợp với `super()`

Một điểm ít người biết là **abstract method vẫn có thể có phần triển khai**.

```python
from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data):
        print("Start processing")
```

```python
class TextProcessor(BaseProcessor):
    def process(self, data):
        super().process(data)
        print(f"Text: {data}")
```

Kết quả:

```text
Start processing
Text: Hello
```

Điều này hữu ích khi muốn tất cả class con đều thực hiện một bước chung (logging, kiểm tra quyền, thống kê...) trước khi chạy logic riêng.

---

# Best Practices

✅ Dùng ABC khi xây dựng:

* Framework
* Plugin
* Driver
* Repository
* Service
* Parser
* Storage
* Crawler

---

✅ Dùng Duck Typing khi:

* Script nhỏ
* Tiện ích nội bộ
* Prototype
* Các thành phần đơn giản

---

✅ Mỗi abstract method nên mô tả rõ:

* đầu vào
* đầu ra
* ý nghĩa nghiệp vụ

---

✅ Đặt tên lớp cơ sở rõ ràng:

```text
BaseParser

BaseCrawler

Repository

Storage

Payment
```

---

# Những lỗi người mới thường gặp

## Lỗi 1

Quên implement abstract method.

```python
class Dog(Animal):
    pass
```

↓

Không thể tạo object.

---

## Lỗi 2

Dùng ABC cho mọi class.

Không phải class nào cũng cần ABC.

Ví dụ:

```python
class User:
```

Không cần.

---

## Lỗi 3

Lạm dụng nhiều tầng ABC.

Ví dụ

```text
BaseEntity

↓

AbstractEntity

↓

CoreEntity

↓

BusinessEntity
```

Thiết kế này thường phức tạp không cần thiết.

---

## Lỗi 4

Viết abstract method nhưng không có tài liệu.

Ví dụ:

```python
@abstractmethod
def execute(self):
    pass
```

Không ai biết:

* `execute()` làm gì?
* Trả về gì?
* Có thể ném ngoại lệ nào?

Hãy dùng docstring và type hint.

---

# Bài tập

## Bài 1

Viết ABC:

```text
Shape
```

Abstract method:

```python
area()
```

Triển khai:

* Rectangle
* Circle
* Triangle

---

## Bài 2

Viết ABC:

```text
Storage
```

Method:

```python
save(filename)
load(filename)
delete(filename)
```

Triển khai:

* LocalStorage
* MemoryStorage

---

## Bài 3

Thiết kế:

```text
Notification
```

Method:

```python
send(message)
```

Triển khai:

* EmailNotification
* SMSNotification
* PushNotification

Viết:

```python
broadcast(notification, message)
```

---

## Bài 4

Thiết kế `BaseCrawler` cho dự án cào truyện.

Yêu cầu:

```python
fetch_book()

fetch_chapter()

search()

login()  # nếu nguồn yêu cầu đăng nhập
```

Triển khai hai crawler cụ thể.

---

## Bài 5 (Nâng cao)

Thiết kế framework plugin:

```text
Plugin (ABC)
│
├── ImagePlugin
├── AudioPlugin
├── VideoPlugin
```

Mỗi plugin bắt buộc có:

```python
load()

run()

unload()
```

Viết `PluginManager` chỉ làm việc với `Plugin`, không quan tâm plugin cụ thể là gì.

---

# Tóm tắt buổi học

* **Abstract Base Class (ABC)** giúp định nghĩa **contract** giữa lớp cơ sở và các lớp triển khai.
* `@abstractmethod` buộc lớp con phải cài đặt phương thức trước khi có thể tạo đối tượng.
* ABC giúp phát hiện lỗi thiết kế **sớm**, rất phù hợp cho framework, plugin và các hệ thống lớn.
* Python còn hỗ trợ **Virtual Subclass** (`register()`) và `__subclasshook__()` để kết hợp giữa ABC và tư duy Duck Typing.
* Trong các dự án thực tế như **framework cào truyện**, **Repository Pattern** hay **Plugin Architecture**, ABC là lựa chọn rất phù hợp để đảm bảo các thành phần tuân theo cùng một giao diện.

> **Buổi 17** chúng ta sẽ bắt đầu **Phần V – Magic Methods** với `__str__()` và `__repr__()`. Bạn sẽ hiểu cách Python biểu diễn đối tượng, sự khác biệt giữa hai phương thức này và cách làm cho các class của mình dễ debug, dễ ghi log và thân thiện hơn khi làm việc trong CLI hoặc REPL.
