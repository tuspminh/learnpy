# Python OOP Master – Buổi 15

# Duck Typing – Triết lý OOP đặc trưng của Python

> Đây là một trong những chủ đề quan trọng nhất để chuyển từ tư duy OOP của Java/C# sang tư duy Python.
>
> Trong Java, bạn thường nghĩ:
>
> > **"Object này có phải là Animal không?"**
>
> Trong Python, bạn nên nghĩ:
>
> > **"Object này có làm được việc mình cần không?"**
>
> Đó chính là **Duck Typing**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Duck Typing là gì.
* Hiểu sự khác biệt giữa Duck Typing và Inheritance.
* Biết khi nào nên dùng Duck Typing.
* Biết khi nào nên dùng Abstract Base Class (ABC).
* Hiểu EAFP và LBYL.
* Áp dụng Duck Typing vào framework cào truyện của bạn.

---

# 1. Duck Typing là gì?

Tên gọi xuất phát từ câu nói nổi tiếng:

> **If it walks like a duck, swims like a duck, and quacks like a duck, then it is probably a duck.**

Trong Python:

> **Nếu object có các phương thức mình cần thì dùng được, không quan tâm nó thuộc class nào.**

---

# 2. Ví dụ đầu tiên

```python
class Duck:
    def speak(self):
        print("Quack")


class Person:
    def speak(self):
        print("Hello")


def make_sound(obj):
    obj.speak()


duck = Duck()
person = Person()

make_sound(duck)
make_sound(person)
```

Kết quả

```text
Quack
Hello
```

Hàm `make_sound()` không quan tâm object là gì.

Nó chỉ cần:

```python
obj.speak()
```

---

# 3. Không cần kế thừa

Ví dụ

```python
class Dog:
    def speak(self):
        print("Woof")


class Cat:
    def speak(self):
        print("Meow")
```

Không class nào kế thừa nhau.

Nhưng vẫn dùng được.

```python
def make_sound(obj):
    obj.speak()


make_sound(Dog())
make_sound(Cat())
```

Đây chính là Duck Typing.

---

# 4. So sánh với Inheritance

Inheritance

```text
Animal
│
├── Dog
└── Cat
```

Duck Typing

```text
Dog

Cat

Robot

Person

Radio
```

Miễn là có

```python
speak()
```

đều hoạt động.

---

# 5. Python quan tâm hành vi

Python không hỏi

```python
isinstance(obj, Animal)
```

Python chỉ thử

```python
obj.speak()
```

Nếu thành công

↓

OK

Nếu thất bại

↓

Exception

---

# 6. Ví dụ

```python
class Robot:
    def speak(self):
        print("Beep")


class Radio:
    def speak(self):
        print("Music")


def talk(obj):
    obj.speak()


talk(Robot())
talk(Radio())
```

---

# 7. Nếu object không có method?

```python
class Car:
    pass


talk(Car())
```

Lỗi

```text
AttributeError:
'Car' object has no attribute 'speak'
```

Đây là hành vi bình thường.

---

# 8. EAFP

Python khuyến khích:

```text
EAFP

↓

Easier to Ask Forgiveness than Permission
```

Có nghĩa

> Cứ làm.

Nếu lỗi

↓

Bắt Exception.

---

# 9. Ví dụ EAFP

```python
def talk(obj):

    try:
        obj.speak()

    except AttributeError:
        print("Cannot speak")
```

```python
talk(Dog())
talk(Car())
```

Kết quả

```text
Woof
Cannot speak
```

---

# 10. LBYL

Ngược lại

```text
LBYL

↓

Look Before You Leap
```

Ví dụ

```python
if hasattr(obj, "speak"):
    obj.speak()
```

Python ít khuyến khích hơn.

---

# 11. So sánh

EAFP

```python
try:
    obj.save()
except AttributeError:
    ...
```

LBYL

```python
if hasattr(obj, "save"):
    obj.save()
```

Pythonic hơn

↓

EAFP

---

# 12. Duck Typing trong thư viện chuẩn

Ví dụ

```python
def save(file):

    file.write("Hello")
```

Không kiểm tra

```python
isinstance(file, TextIO)
```

Chỉ cần object có

```python
write()
```

---

# 13. Ví dụ StringIO

```python
from io import StringIO

buffer = StringIO()

buffer.write("Hello")

print(buffer.getvalue())
```

`StringIO` không phải file thật.

Nhưng có

```python
write()
```

nên hoạt động.

---

# 14. Ví dụ Logger

```python
class ConsoleLogger:
    def log(self, msg):
        print(msg)


class FileLogger:
    def log(self, msg):
        print("Save:", msg)


def process(logger):

    logger.log("Hello")
```

Không cần

```python
class Logger
```

---

# 15. Duck Typing trong Parser

Ví dụ

```python
class HtmlParser:
    def parse(self):
        print("HTML")


class JsonParser:
    def parse(self):
        print("JSON")
```

```python
def load(parser):

    parser.parse()
```

Không quan tâm parser thuộc loại nào.

---

# 16. Duck Typing trong dự án cào truyện

Đây là nơi Duck Typing phát huy sức mạnh.

```python
class TruyenFullParser:
    def parse_chapter(self, html):
        return "Chapter"


class BachNgocSachParser:
    def parse_chapter(self, html):
        return "Chapter"
```

```python
def crawl(parser, html):

    return parser.parse_chapter(html)
```

Không cần

```python
BaseParser
```

Miễn có

```python
parse_chapter()
```

---

# 17. Khi nào Duck Typing không đủ?

Ví dụ

Bạn có đội ngũ 20 lập trình viên.

Có hàng trăm plugin.

Nếu ai cũng tự đặt tên

```python
parse()
```

```python
load()
```

```python
run()
```

↓

Khó kiểm soát.

Khi đó cần

* Abstract Base Class
* Protocol (`typing.Protocol`)
* Interface rõ ràng

Đây là nội dung của **Buổi 16**.

---

# 18. Duck Typing và `isinstance()`

Người mới thường viết

```python
if isinstance(parser, HtmlParser):
    ...
```

Sau đó

```python
elif isinstance(parser, JsonParser):
    ...
```

Khi thêm parser mới

↓

Sửa code.

Duck Typing

```python
parser.parse()
```

Không cần sửa.

---

# 19. Ví dụ hoàn chỉnh

```python
class PDFExporter:
    def export(self, data):
        print("Export PDF:", data)


class CSVExporter:
    def export(self, data):
        print("Export CSV:", data)


class JSONExporter:
    def export(self, data):
        print("Export JSON:", data)


def export_data(exporter, data):
    exporter.export(data)


data = {"name": "Alice", "age": 20}

exporters = [
    PDFExporter(),
    CSVExporter(),
    JSONExporter(),
]

for exporter in exporters:
    export_data(exporter, data)
```

Kết quả

```text
Export PDF: {'name': 'Alice', 'age': 20}
Export CSV: {'name': 'Alice', 'age': 20}
Export JSON: {'name': 'Alice', 'age': 20}
```

---

# 20. Duck Typing vs Inheritance vs ABC

| Tiêu chí               | Duck Typing | Inheritance | ABC   |
| ---------------------- | ----------- | ----------- | ----- |
| Cần kế thừa            | ❌           | ✅           | ✅     |
| Kiểm tra kiểu          | ❌           | Có thể      | Có    |
| Linh hoạt              | ⭐⭐⭐⭐⭐       | ⭐⭐⭐         | ⭐⭐⭐⭐  |
| An toàn                | ⭐⭐⭐         | ⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐ |
| Pythonic               | ⭐⭐⭐⭐⭐       | ⭐⭐⭐         | ⭐⭐⭐⭐  |
| Phù hợp plugin         | ⭐⭐⭐⭐⭐       | ⭐⭐⭐         | ⭐⭐⭐⭐⭐ |
| Dễ kiểm soát dự án lớn | ⭐⭐          | ⭐⭐⭐         | ⭐⭐⭐⭐⭐ |

---

# 21. Duck Typing và Protocol (Giới thiệu)

Ngày nay, Python hiện đại thường kết hợp Duck Typing với `typing.Protocol`.

Ví dụ:

```python
from typing import Protocol


class Parser(Protocol):
    def parse(self, text: str) -> dict: ...
```

Bất kỳ class nào có phương thức:

```python
parse(text)
```

đều được type checker chấp nhận, **không cần kế thừa** `Parser`.

Đây là **Structural Typing**, sẽ được học sâu ở phần `typing`.

---

# Best Practices

✅ Thiết kế các class có **cùng hành vi** với cùng tên phương thức.

✅ Viết hàm làm việc với **hành vi**, không với **kiểu cụ thể**.

✅ Ưu tiên EAFP khi thao tác với đối tượng trong Python.

✅ Với dự án nhỏ và vừa, Duck Typing thường đủ mạnh.

✅ Với dự án lớn hoặc framework công khai, kết hợp Duck Typing với **ABC** hoặc **Protocol** để có hợp đồng (contract) rõ ràng.

---

# Những lỗi người mới thường gặp

## Lỗi 1: Lạm dụng `isinstance()`

```python
if isinstance(storage, LocalStorage):
    ...
elif isinstance(storage, S3Storage):
    ...
```

Nên thiết kế:

```python
storage.save(file)
```

---

## Lỗi 2: Mỗi class dùng tên phương thức khác nhau

```python
Dog.bark()

Cat.meow()

Duck.quack()
```

Client code sẽ phải kiểm tra kiểu.

Tốt hơn:

```python
Dog.speak()

Cat.speak()

Duck.speak()
```

---

## Lỗi 3: Bắt quá nhiều Exception

Không nên:

```python
try:
    obj.save()
except Exception:
    pass
```

Hãy bắt đúng ngoại lệ mong đợi:

```python
except AttributeError:
    ...
```

---

# Bài tập

## Bài 1

Viết các class:

* `Dog`
* `Cat`
* `Robot`

Mỗi class có:

```python
speak()
```

Viết:

```python
def make_sound(obj): ...
```

Không dùng `isinstance()`.

---

## Bài 2

Thiết kế:

* `PDFExporter`
* `CSVExporter`
* `ExcelExporter`

Mỗi class có:

```python
export(data)
```

Viết:

```python
export_all(exporters, data)
```

Nhận danh sách exporter và xuất dữ liệu.

---

## Bài 3

Thiết kế:

* `LocalStorage`
* `CloudStorage`
* `MemoryStorage`

Mỗi class có:

```python
save(filename)
```

Viết:

```python
backup(storage, filename)
```

Không kiểm tra kiểu.

---

## Bài 4

Thiết kế hệ thống parser cho ứng dụng cào truyện:

* `TruyenFullParser`
* `TangThuVienParser`
* `BachNgocSachParser`

Mỗi parser có:

```python
parse_chapter(html)
```

Viết:

```python
crawl(parser, html)
```

để xử lý mọi parser mà không cần kế thừa `BaseParser`.

---

## Bài 5 (Nâng cao)

Viết một hàm:

```python
def execute(worker):
    worker.run()
```

Tạo các class:

* `ThreadWorker`
* `ProcessWorker`
* `AsyncWorker`

Mỗi class đều có `run()`.

Thêm một class `BrokenWorker` không có `run()` và xử lý theo phong cách **EAFP** bằng `try/except AttributeError`.

---

# Tóm tắt buổi học

* **Duck Typing** là triết lý cốt lõi của Python: *"Không quan trọng đối tượng là gì, quan trọng là nó làm được gì."*
* Duck Typing cho phép đạt được **đa hình mà không cần kế thừa**, chỉ cần các đối tượng cung cấp cùng một hành vi.
* Python khuyến khích phong cách **EAFP (Easier to Ask Forgiveness than Permission)** thay vì kiểm tra trước bằng `hasattr()` hoặc `isinstance()`.
* Duck Typing rất phù hợp với các hệ thống plugin, parser, exporter, storage và đặc biệt hữu ích trong kiến trúc **framework cào truyện** mà bạn đang xây dựng.
* Tuy nhiên, trong các dự án lớn hoặc thư viện công khai, Duck Typing thường được kết hợp với **Abstract Base Class (ABC)** hoặc **Protocol** để định nghĩa hợp đồng rõ ràng và tăng khả năng kiểm tra tĩnh.

> **Buổi 16** chúng ta sẽ học **Abstract Base Class (ABC)** một cách chuyên sâu: `abc.ABC`, `@abstractmethod`, hợp đồng (contract), virtual subclass, `__subclasshook__`, và cách kết hợp ABC với Duck Typing để xây dựng các framework Python chuyên nghiệp.
