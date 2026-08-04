# Python OOP Master – Buổi 21

# `@staticmethod` – Phương thức tĩnh trong Python

> Đây là một chủ đề mà rất nhiều lập trình viên mới học OOP thường nhầm lẫn.
>
> Câu hỏi phổ biến là:
>
> * Khi nào dùng method thường?
> * Khi nào dùng `@staticmethod`?
> * Khi nào dùng `@classmethod`?
>
> Hôm nay chúng ta sẽ giải quyết hoàn toàn phần đầu tiên: **`@staticmethod`**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu `@staticmethod` là gì.
* Phân biệt Instance Method và Static Method.
* Biết khi nào nên dùng `@staticmethod`.
* Tránh lạm dụng static method.
* Áp dụng vào framework cào truyện.

---

# 1. Ba loại phương thức trong class

Trong Python, một class có ba loại phương thức chính:

| Loại            | Tham số đầu tiên | Truy cập                   |
| --------------- | ---------------- | -------------------------- |
| Instance Method | `self`           | Object                     |
| Class Method    | `cls`            | Class                      |
| Static Method   | Không có         | Không cần object hay class |

Ví dụ:

```python
class Example:
    def instance_method(self): ...

    @classmethod
    def class_method(cls): ...

    @staticmethod
    def static_method(): ...
```

---

# 2. Instance Method

Đây là loại quen thuộc nhất.

```python
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello {self.name}")
```

```python
user = User("Alice")

user.greet()
```

↓

```text
Hello Alice
```

`greet()` cần dùng:

```python
self.name
```

nên phải là **Instance Method**.

---

# 3. Static Method là gì?

Static Method:

* không có `self`
* không có `cls`
* chỉ là một hàm được đặt trong namespace của class

Ví dụ

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b
```

Sử dụng

```python
print(Math.add(3, 5))
```

↓

```text
8
```

---

# 4. Có thể gọi từ object

```python
math = Math()

print(math.add(2, 3))
```

↓

```text
5
```

Tuy nhiên, **khuyến nghị** nên gọi qua class:

```python
Math.add(2, 3)
```

để thể hiện rõ đây là phương thức không phụ thuộc trạng thái của object.

---

# 5. Không truy cập được `self`

Sai:

```python
class User:
    @staticmethod
    def hello():
        print(self.name)
```

↓

```text
NameError
```

Không có:

```python
self
```

---

# 6. Không truy cập được `cls`

Sai:

```python
class User:
    @staticmethod
    def create():
        return cls()
```

↓

```text
NameError
```

Không có:

```python
cls
```

---

# 7. Khi nào dùng Static Method?

Một quy tắc đơn giản:

Nếu method:

* không dùng `self`
* không dùng `cls`

↓

Có thể là `@staticmethod`.

---

# 8. Ví dụ Validator

```python
class EmailValidator:
    @staticmethod
    def is_valid(email):

        return "@" in email
```

Sử dụng

```python
print(EmailValidator.is_valid("a@test.com"))
```

↓

```text
True
```

Không cần tạo object.

---

# 9. Ví dụ String Helper

```python
class StringUtil:
    @staticmethod
    def slug(text):

        return text.lower().replace(" ", "-")
```

```python
print(StringUtil.slug("Python Master"))
```

↓

```text
python-master
```

---

# 10. Ví dụ Parser Helper

Trong framework cào truyện

```python
class HtmlUtil:
    @staticmethod
    def clean(html):

        return html.strip()
```

Parser

```python
html = HtmlUtil.clean(html)
```

---

# 11. Ví dụ Money

```python
class Money:
    @staticmethod
    def format(amount):

        return f"{amount:,.0f} đ"
```

```python
print(Money.format(1234567))
```

↓

```text
1,234,567 đ
```

---

# 12. Ví dụ Hash

```python
import hashlib


class HashUtil:
    @staticmethod
    def md5(text):

        return hashlib.md5(text.encode()).hexdigest()
```

Sử dụng

```python
print(HashUtil.md5("python"))
```

---

# 13. Ví dụ Path

```python
class PathUtil:
    @staticmethod
    def chapter_file(id):

        return f"chapter_{id}.json"
```

↓

```python
filename = PathUtil.chapter_file(5)
```

---

# 14. Ví dụ Repository

```python
class BookRepository:
    @staticmethod
    def validate(book):

        return book.title != ""
```

Lưu ý:

Nếu sau này việc kiểm tra cần dùng dữ liệu của repository (ví dụ danh sách sách hiện có), phương thức này **không còn phù hợp** là `@staticmethod`.

---

# 15. Ví dụ trong framework cào truyện

```python
class UrlUtil:
    @staticmethod
    def normalize(url):

        return url.rstrip("/")
```

Crawler

```python
url = UrlUtil.normalize(url)
```

---

# 16. Static Method hay Function?

Nhiều người hỏi:

Tại sao không viết

```python
def slug(text): ...
```

thay vì

```python
class StringUtil:
```

Câu trả lời:

Nếu hàm:

* chỉ liên quan đến một class
* có ý nghĩa nghiệp vụ của class

↓

Đặt thành `@staticmethod` là hợp lý.

Nếu là hàm dùng chung toàn dự án, hãy cân nhắc đặt trong một module riêng.

Ví dụ:

```
utils/
    string_utils.py
    path_utils.py
    hash_utils.py
```

---

# 17. Static Method và kế thừa

```python
class Base:
    @staticmethod
    def hello():
        print("Hello")
```

```python
class Child(Base):
    pass
```

```python
Child.hello()
```

↓

```text
Hello
```

Static method cũng được kế thừa như các phương thức khác.

---

# 18. Ví dụ hoàn chỉnh

```python
import re


class PasswordUtil:
    @staticmethod
    def strong(password):

        if len(password) < 8:
            return False

        return bool(re.search(r"\d", password))


print(PasswordUtil.strong("abc12345"))

print(PasswordUtil.strong("abcdef"))
```

↓

```text
True

False
```

---

# 19. So sánh ba loại method

```python
class Demo:
    value = 100

    def instance(self):
        return self.value

    @classmethod
    def cls_method(cls):
        return cls.value

    @staticmethod
    def static():
        return "Hello"
```

| Method   | Dùng `self` | Dùng `cls` | Truy cập trạng thái object | Truy cập thuộc tính class       |
| -------- | ----------- | ---------- | -------------------------- | ------------------------------- |
| Instance | ✅           | ❌          | ✅                          | ✅                               |
| Class    | ❌           | ✅          | ❌                          | ✅                               |
| Static   | ❌           | ❌          | ❌                          | ❌ (trừ khi gọi rõ `Demo.value`) |

> **Lưu ý:** Static method vẫn có thể truy cập thuộc tính lớp bằng cách ghi rõ tên lớp (`Demo.value`), nhưng điều này làm giảm tính linh hoạt khi kế thừa. Ở buổi sau, bạn sẽ thấy `@classmethod` phù hợp hơn cho các trường hợp cần làm việc với chính lớp.

---

# 20. Những lỗi người mới thường gặp

## Lỗi 1

Dùng `@staticmethod` cho mọi method.

Sai:

```python
class User:
    @staticmethod
    def rename(name):

        self.name = name
```

Không có `self`.

---

## Lỗi 2

Method cần dùng dữ liệu object nhưng vẫn khai báo static.

Ví dụ:

```python
@staticmethod
def save():
```

trong khi cần:

```python
self.filename
```

↓

Nên dùng Instance Method.

---

## Lỗi 3

Biến mọi hàm tiện ích thành static method.

Nếu hàm không liên quan chặt chẽ đến class:

```python
calculate_crc()

parse_yaml()

compress()
```

↓

Nên đặt ở module riêng thay vì nhồi vào một lớp `Utils` khổng lồ.

---

## Lỗi 4

Gọi static method qua object khi không cần.

```python
util = StringUtil()

util.slug("abc")
```

Đúng nhưng dễ gây hiểu nhầm.

Nên:

```python
StringUtil.slug("abc")
```

---

# Best Practices

✅ Dùng `@staticmethod` khi:

* không cần `self`
* không cần `cls`
* logic gắn với nghiệp vụ của class

---

✅ Đặt tên rõ ràng:

```python
EmailValidator.is_valid()

UrlUtil.normalize()

Money.format()
```

---

✅ Nếu method có khả năng cần kế thừa hoặc tạo object của lớp trong tương lai, hãy cân nhắc `@classmethod` thay vì `@staticmethod`.

---

# Bài tập

## Bài 1

Viết class:

```text
MathUtil
```

Có các static method:

```python
add()

subtract()

multiply()

divide()
```

---

## Bài 2

Viết:

```text
FileUtil
```

Static methods:

```python
extension(filename)

basename(filename)

is_image(filename)
```

---

## Bài 3

Viết:

```text
UrlUtil
```

Static methods:

```python
normalize()

join()

is_http()
```

---

## Bài 4

Trong framework cào truyện, viết:

```text
ChapterUtil
```

Static methods:

```python
chapter_filename(id)

chapter_slug(title)

chapter_path(book_id, chapter_id)
```

---

## Bài 5 (Nâng cao)

Thiết kế:

```text
SqlBuilder
```

Static methods:

```python
select(table)

insert(table)

update(table)

delete(table)
```

Ví dụ:

```python
SqlBuilder.select("books")
```

↓

```sql
SELECT * FROM books;
```

Đây sẽ là nền tảng hữu ích khi bạn xây dựng `DatabaseManager` bằng `sqlite3` thuần.

---

# Tổng kết buổi học

* `@staticmethod` tạo ra một phương thức **không phụ thuộc** vào object (`self`) hay class (`cls`).
* Static method phù hợp với các thao tác tiện ích gắn với nghiệp vụ của một lớp, như kiểm tra dữ liệu, chuẩn hóa chuỗi, định dạng đường dẫn...
* Không nên lạm dụng `@staticmethod`; nếu phương thức cần truy cập trạng thái của object hoặc của lớp, hãy dùng instance method hoặc class method.
* Trong các dự án lớn, hãy cân nhắc giữa việc đặt logic trong static method hay trong một module tiện ích để giữ thiết kế rõ ràng.

> **Buổi 22** chúng ta sẽ học **`@classmethod`** — cách làm việc với chính lớp (`cls`), xây dựng **alternative constructor**, hỗ trợ kế thừa đúng cách và chuẩn bị cho **Factory Pattern** ở Buổi 23. Đây là kỹ thuật được dùng rất nhiều trong `pathlib`, `datetime`, `dict.fromkeys()`, `dataclass` và nhiều thư viện chuẩn của Python.
