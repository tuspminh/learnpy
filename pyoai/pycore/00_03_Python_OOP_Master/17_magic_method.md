# Python OOP Master – Buổi 17

# Magic Methods (Phần 1) – `__str__()` và `__repr__()`

> Đây là buổi đầu tiên trong phần **Magic Methods (Dunder Methods)**.
>
> Magic Methods là lý do khiến các object trong Python có thể hoạt động tự nhiên như:
>
> ```python
> len(obj)
> obj + other
> obj[0]
> print(obj)
> for x in obj:
> ```
>
> Tất cả đều được Python chuyển thành các lời gọi tới các **Magic Method**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Magic Method là gì.
* Hiểu cơ chế hoạt động của `print()`.
* Phân biệt `__str__()` và `__repr__()`.
* Biết khi nào nên cài đặt từng phương thức.
* Viết class thân thiện với người dùng và lập trình viên.
* Áp dụng vào dự án quản lý truyện.

---

# 1. Magic Method là gì?

Magic Method (hay **Dunder Method**) là các phương thức có dạng:

```python
__method_name__()
```

Ví dụ:

```python
__init__()

__str__()

__repr__()

__len__()

__iter__()

__getitem__()

__call__()

__add__()
```

Python sẽ **tự động gọi** các phương thức này khi bạn sử dụng cú pháp quen thuộc.

Ví dụ:

```python
len(obj)
```

Python thực chất gọi:

```python
obj.__len__()
```

---

# 2. Ví dụ đầu tiên

```python
class User:
    def __init__(self, name):
        self.name = name


user = User("Alice")

print(user)
```

Kết quả:

```text
<__main__.User object at 0x104fc2b90>
```

Đây **không phải lỗi**.

Python đang hiển thị biểu diễn mặc định của object.

---

# 3. Python làm gì khi `print(obj)`?

Khi viết:

```python
print(user)
```

Python thực hiện:

```python
print(str(user))
```

và:

```python
str(user)
```

sẽ gọi:

```python
user.__str__()
```

Nếu không có `__str__()`, Python sẽ dùng `__repr__()`.

Nếu cũng không có `__repr__()`, Python dùng biểu diễn mặc định từ lớp `object`.

---

# 4. `__str__()`

`__str__()` dùng để:

* hiển thị cho **người dùng cuối**
* dễ đọc
* đẹp
* ngắn gọn

Ví dụ:

```python
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User(name={self.name})"


user = User("Alice")

print(user)
```

Kết quả:

```text
User(name=Alice)
```

---

# 5. `__repr__()`

`__repr__()` dành cho:

* lập trình viên
* debug
* logging
* REPL

Ví dụ:

```python
class User:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"User('{self.name}')"


user = User("Alice")

print(repr(user))
```

Kết quả:

```text
User('Alice')
```

---

# 6. Khác nhau

Ví dụ:

```python
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"User(name='{self.name}')"
```

```python
user = User("Alice")

print(user)

print(str(user))

print(repr(user))
```

Kết quả

```text
Alice
Alice
User(name='Alice')
```

---

# 7. Khi chỉ có `__repr__()`

```python
class User:
    def __repr__(self):
        return "User Object"
```

```python
user = User()

print(user)
```

Kết quả

```text
User Object
```

Python dùng `__repr__()` vì không có `__str__()`.

---

# 8. Khi chỉ có `__str__()`

```python
class User:
    def __str__(self):
        return "User"
```

```python
user = User()

print(user)

print(repr(user))
```

Kết quả

```text
User
<__main__.User object at 0x...>
```

`repr(user)` **không dùng** `__str__()`.

---

# 9. REPL và Notebook

Trong Python Shell:

```python
user
```

Python gọi:

```python
repr(user)
```

Không gọi:

```python
str(user)
```

Đó là lý do `__repr__()` rất quan trọng khi debug.

---

# 10. List dùng `__repr__()`

Ví dụ

```python
class User:
    def __repr__(self):
        return "User"
```

```python
users = [
    User(),
    User(),
]
```

```python
print(users)
```

Kết quả

```text
[User, User]
```

Nếu không có `__repr__()`:

```text
[
 <User object at ...>,
 <User object at ...>
]
```

---

# 11. Ví dụ Book

```python
class Book:
    def __init__(self, title, author):

        self.title = title
        self.author = author

    def __str__(self):

        return f"{self.title} - {self.author}"

    def __repr__(self):

        return f"Book(title={self.title!r}, author={self.author!r})"
```

```python
book = Book("Clean Code", "Robert Martin")

print(book)

print(repr(book))
```

Kết quả

```text
Clean Code - Robert Martin

Book(title='Clean Code', author='Robert Martin')
```

---

# 12. Sử dụng `!r`

Trong f-string

```python
{value!r}
```

tương đương

```python
repr(value)
```

Ví dụ

```python
name = "Alice"

print(f"{name}")

print(f"{name!r}")
```

Kết quả

```text
Alice

'Alice'
```

---

# 13. `repr()` nên có gì?

Theo khuyến nghị của Python:

Một `repr()` tốt nên:

* rõ ràng
* đầy đủ
* giúp debug
* nếu có thể, tạo lại object

Ví dụ

```python
User("Alice")
```

tốt hơn

```python
User Object
```

---

# 14. Ví dụ Repository

```python
class Repository:
    def __init__(self):

        self.items = []

    def __repr__(self):

        return f"Repository(items={len(self.items)})"
```

```python
repo = Repository()

print(repo)
```

↓

```text
Repository(items=0)
```

---

# 15. Ví dụ trong dự án cào truyện

```python
class Chapter:
    def __init__(
        self,
        id,
        title,
        url,
    ):
        self.id = id
        self.title = title
        self.url = url

    def __str__(self):

        return self.title

    def __repr__(self):

        return f"Chapter(id={self.id}, title={self.title!r})"
```

```python
chapter = Chapter(1, "Chương 1", "/chuong-1")

print(chapter)

print(repr(chapter))
```

---

# 16. Logging

```python
logger.info("%r", chapter)
```

↓

Python gọi

```python
repr(chapter)
```

Nếu dùng

```python
logger.info("%s", chapter)
```

↓

Python gọi

```python
str(chapter)
```

---

# 17. Dataclass

Khi dùng `dataclass`

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str

    age: int
```

Python tự sinh

```python
__repr__()
```

Kết quả

```text
User(name='Alice', age=20)
```

Đây là một trong những lý do `dataclass` rất tiện.

---

# 18. Ví dụ hoàn chỉnh

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"User(username={self.username!r}, email={self.email!r})"


users = [
    User("alice", "a@example.com"),
    User("bob", "b@example.com"),
]

print(users)

for user in users:
    print(user)
```

Kết quả

```text
[
 User(username='alice', email='a@example.com'),
 User(username='bob', email='b@example.com')
]

alice
bob
```

---

# 19. Best Practices

## `__str__()`

Dùng cho:

* CLI
* GUI
* Người dùng
* Báo cáo
* In ra màn hình

Nên:

* ngắn
* dễ đọc
* không quá nhiều thông tin

---

## `__repr__()`

Dùng cho:

* Debug
* Logging
* REPL
* Danh sách object
* IDE

Nên:

* đầy đủ
* rõ ràng
* ưu tiên dùng `!r`

---

# 20. Những lỗi người mới thường gặp

## Lỗi 1

`__str__()` không trả về chuỗi

```python
def __str__(self):
    return 123
```

Lỗi:

```text
TypeError:
__str__ returned non-string
```

---

## Lỗi 2

`__repr__()` quá sơ sài

```python
def __repr__(self):
    return "User"
```

Không hữu ích khi debug.

---

## Lỗi 3

Đưa dữ liệu nhạy cảm vào `__repr__()`

Sai:

```python
class User:
    def __repr__(self):
        return f"User(password={self.password})"
```

Có thể làm lộ mật khẩu trong log.

---

## Lỗi 4

`__str__()` quá dài

Ví dụ:

```python
return json.dumps(self.__dict__)
```

Không phù hợp để hiển thị cho người dùng.

---

# Bài tập

## Bài 1

Viết class:

```text
Student
```

Có:

* id
* name
* age

Viết:

```python
__str__()

__repr__()
```

---

## Bài 2

Viết:

```text
Book
```

Có:

* title
* author
* price

Hiển thị:

```text
Python Master - David
```

và

```text
Book(title='Python Master', author='David', price=20)
```

---

## Bài 3

Viết:

```text
Product
```

Tạo list:

```python
products = [...]
```

In list để quan sát `__repr__()`.

---

## Bài 4

Trong dự án cào truyện, thiết kế:

```text
Novel
```

```text
Chapter
```

```text
Author
```

Viết `__str__()` và `__repr__()` hợp lý cho từng class.

---

## Bài 5 (Nâng cao)

Viết class:

```text
CrawlerTask
```

Thuộc tính:

* id
* source
* url
* status
* retry_count

Yêu cầu:

* `__str__()` chỉ hiển thị:

```text
Task #15 [RUNNING]
```

* `__repr__()` hiển thị đầy đủ:

```text
CrawlerTask(
    id=15,
    source='TruyenFull',
    url='...',
    status='RUNNING',
    retry_count=2
)
```

Sau đó:

* đưa các `CrawlerTask` vào `list`
* in list
* ghi log bằng `%r`
* in ra màn hình bằng `print(task)`

Quan sát sự khác biệt giữa `__str__()` và `__repr__()`.

---

# Tổng kết buổi học

* **Magic Methods** là các phương thức đặc biệt giúp đối tượng tích hợp tự nhiên với cú pháp của Python.
* `__str__()` dành cho **người dùng cuối**, còn `__repr__()` dành cho **lập trình viên**, phục vụ debug và logging.
* Khi gọi `print(obj)`, Python ưu tiên `__str__()`. Nếu không có, nó sẽ dùng `__repr__()`.
* `repr(obj)` và các môi trường như REPL, danh sách (`list`) hay nhiều hệ thống logging thường sử dụng `__repr__()`.
* Một `__repr__()` tốt nên rõ ràng, đầy đủ và nếu có thể, biểu diễn đối tượng theo cách có thể tái tạo lại.

> **Buổi 18** chúng ta sẽ học **Operator Overloading** với các magic methods như `__add__()`, `__sub__()`, `__mul__()`, `__truediv__()`, `__eq__()`, `__lt__()`... Bạn sẽ biết cách tạo các đối tượng có thể cộng, trừ, so sánh và hoạt động giống như các kiểu dữ liệu có sẵn của Python.
