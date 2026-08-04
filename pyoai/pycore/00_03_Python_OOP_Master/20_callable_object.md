# Python OOP Master – Buổi 20

# Callable Object – `__call__()`

> Đây là một trong những Magic Methods "đỉnh cao" của Python.
>
> Rất nhiều framework nổi tiếng sử dụng `__call__()`:
>
> * Flask
> * Django
> * FastAPI
> * PyTorch (`nn.Module`)
> * Click
> * Jinja2
> * Werkzeug
>
> Sau buổi học này, bạn sẽ hiểu vì sao **object có thể được gọi như một hàm**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Callable Object là gì.
* Hiểu `callable()`.
* Cài đặt `__call__()`.
* Phân biệt function và callable object.
* Biết khi nào nên dùng `__call__()`.
* Áp dụng vào framework cào truyện.

---

# 1. Object cũng có thể là hàm

Thông thường:

```python
def greet(name):
    print(f"Hello {name}")


greet("Alice")
```

Nhưng trong Python, object cũng có thể gọi được:

```python
obj()
```

Điều kiện:

↓

Object phải có

```python
__call__()
```

---

# 2. Magic Method

```python
obj()
```

Python thực chất gọi:

```python
obj.__call__()
```

---

# 3. Ví dụ đầu tiên

```python
class Greeter:
    def __call__(self):

        print("Hello")
```

```python
g = Greeter()

g()
```

Kết quả

```text
Hello
```

---

# 4. Có tham số

```python
class Greeter:
    def __call__(self, name):

        print(f"Hello {name}")
```

```python
g = Greeter()

g("Alice")
```

↓

```text
Hello Alice
```

---

# 5. Có giá trị trả về

```python
class Adder:
    def __call__(self, a, b):
        return a + b
```

```python
add = Adder()

print(add(10, 20))
```

↓

```text
30
```

---

# 6. `callable()`

Python có hàm

```python
callable(obj)
```

để kiểm tra object có gọi được không.

Ví dụ

```python
print(callable(print))
```

↓

```text
True
```

```python
class Test:
    pass


print(callable(Test()))
```

↓

```text
False
```

---

# 7. Có `__call__()`

```python
class Test:
    def __call__(self):
        pass
```

```python
print(callable(Test()))
```

↓

```text
True
```

---

# 8. Function cũng là object

Trong Python

```python
def hello():
    pass
```

Thực ra

```python
hello
```

là object.

Nó có:

```python
hello.__call__
```

Bạn có thể thử:

```python
print(callable(hello))
```

↓

```text
True
```

---

# 9. Class cũng là Callable

```python
class User:
    pass
```

```python
print(callable(User))
```

↓

```text
True
```

Vì:

```python
User()
```

↓

Python gọi metaclass:

```python
type.__call__()
```

rồi tạo object.

---

# 10. Ví dụ Validator

```python
class EmailValidator:
    def __call__(self, email):

        return "@" in email
```

```python
validator = EmailValidator()

print(validator("a@test.com"))

print(validator("abc"))
```

↓

```text
True

False
```

---

# 11. Ví dụ Counter

```python
class Counter:
    def __init__(self):

        self.count = 0

    def __call__(self):

        self.count += 1

        return self.count
```

```python
counter = Counter()

print(counter())

print(counter())

print(counter())
```

↓

```text
1

2

3
```

Đây là điều mà một hàm thông thường khó thực hiện nếu không dùng closure hoặc biến toàn cục.

---

# 12. Ví dụ Logger

```python
class Logger:
    def __call__(self, message):

        print(f"[LOG] {message}")
```

```python
logger = Logger()

logger("Application started")
```

↓

```text
[LOG] Application started
```

---

# 13. Strategy Pattern

Thay vì

```python
strategy.execute(data)
```

ta có thể viết

```python
strategy(data)
```

Ví dụ

```python
class UpperCase:
    def __call__(self, text):
        return text.upper()


class LowerCase:
    def __call__(self, text):
        return text.lower()
```

```python
def process(strategy, text):

    return strategy(text)
```

---

# 14. Middleware

```python
class Middleware:
    def __call__(self, request):

        print("Before")

        print(request)

        print("After")
```

```python
mw = Middleware()

mw("GET /")
```

---

# 15. Decorator Class

Đây là ứng dụng nổi tiếng nhất.

```python
class Repeat:
    def __init__(self, times):

        self.times = times

    def __call__(self, func):

        def wrapper():

            for _ in range(self.times):
                func()

        return wrapper
```

Sử dụng

```python
@Repeat(3)
def hello():

    print("Hello")
```

```python
hello()
```

↓

```text
Hello

Hello

Hello
```

---

# 16. Ví dụ trong framework cào truyện

```python
class CrawlTask:
    def __init__(self, crawler):

        self.crawler = crawler

    def __call__(self, url):

        return self.crawler.fetch(url)
```

Sử dụng

```python
task = CrawlTask(crawler)

book = task(url)
```

Thay vì

```python
task.run(url)
```

API ngắn gọn hơn.

---

# 17. Ví dụ Cache

```python
class Cache:
    def __init__(self):

        self.data = {}

    def __call__(self, key):

        return self.data.get(key)
```

```python
cache = Cache()

cache.data["a"] = 10

print(cache("a"))
```

↓

```text
10
```

---

# 18. Ví dụ hoàn chỉnh

```python
class Multiplier:
    def __init__(self, factor):

        self.factor = factor

    def __call__(self, value):

        return value * self.factor


double = Multiplier(2)

triple = Multiplier(3)

print(double(5))

print(triple(5))
```

↓

```text
10

15
```

---

# 19. Khi nào nên dùng `__call__()`

Rất phù hợp khi object đại diện cho **một hành động**.

Ví dụ:

* Validator
* Filter
* Strategy
* Middleware
* Command
* Rule Engine
* AI Model
* Pipeline
* Task
* Plugin

Không nên dùng cho các entity như:

* User
* Book
* Student
* Product

Các entity chủ yếu biểu diễn dữ liệu, không phải hành vi.

---

# 20. `__call__()` trong PyTorch

Một ví dụ nổi tiếng:

```python
output = model(input)
```

Bạn không gọi:

```python
model.forward(input)
```

Mà:

```python
model(input)
```

Bên trong, `__call__()` sẽ:

1. Chạy các hook trước.
2. Gọi `forward()`.
3. Chạy các hook sau.
4. Trả kết quả.

Đây là lý do API của PyTorch rất tự nhiên.

---

# 21. So sánh các cách gọi

| Cách viết    | Ý nghĩa                             |
| ------------ | ----------------------------------- |
| `func(x)`    | Gọi hàm                             |
| `obj.run(x)` | Gọi phương thức                     |
| `obj(x)`     | Gọi `__call__()`                    |
| `Class()`    | Gọi `type.__call__()` để tạo object |

---

# Best Practices

✅ Dùng `__call__()` khi object đại diện cho **một tác vụ duy nhất**.

---

✅ Giữ `__call__()` ngắn gọn, rõ ràng.

Nếu logic quá phức tạp, hãy tách thành các phương thức riêng.

---

✅ Kết hợp `__call__()` với Dependency Injection rất hiệu quả.

Ví dụ:

```python
class CrawlTask:
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, html):
        return self.parser.parse(html)
```

---

✅ Có thể kết hợp `__call__()` với `__repr__()` để dễ debug:

```python
class Validator:
    def __repr__(self):
        return "EmailValidator()"
```

---

# Những lỗi người mới thường gặp

## Lỗi 1

Dùng `__call__()` thay cho mọi phương thức.

Sai:

```python
user()
```

`User` không phải là một hành động.

---

## Lỗi 2

`__call__()` làm quá nhiều việc.

Ví dụ:

* ghi log
* đọc file
* gửi email
* lưu database

Tốt hơn là tách thành nhiều lớp hoặc phương thức nhỏ.

---

## Lỗi 3

Không kiểm tra đầu vào.

Ví dụ:

```python
class Divider:
    def __call__(self, a, b):
        return a / b
```

Nên xử lý trường hợp `b == 0` nếu phù hợp với nghiệp vụ.

---

## Lỗi 4

Nhầm lẫn giữa Callable Object và Function.

Một callable object **không phải** là function, nhưng có thể được gọi giống function.

---

# Bài tập

## Bài 1

Viết class `Adder`:

```python
add = Adder()

print(add(10, 20))
```

Kết quả:

```text
30
```

---

## Bài 2

Viết class `Power`:

```python
square = Power(2)

cube = Power(3)

print(square(5))

print(cube(5))
```

---

## Bài 3

Viết class `PasswordValidator`:

```python
validator = PasswordValidator()

validator("123456")
```

Trả về `True` nếu mật khẩu có ít nhất 8 ký tự.

---

## Bài 4

Trong framework cào truyện, thiết kế:

```text
ChapterParser
```

```python
parser(html)
```

thay vì:

```python
parser.parse(html)
```

Hãy cài đặt `__call__()` để chuyển tiếp tới `parse()`.

---

## Bài 5 (Nâng cao)

Thiết kế `Pipeline`:

```python
pipeline = Pipeline(
    [
        Strip(),
        Lower(),
        RemoveSpace(),
    ]
)

result = pipeline("  Hello World  ")
```

Yêu cầu:

* Mỗi bước (`Strip`, `Lower`, `RemoveSpace`) đều là **callable object**.
* `Pipeline` cũng là **callable object** và sẽ lần lượt gọi từng bước xử lý.

Đây là mô hình rất phổ biến trong các framework AI, ETL và xử lý văn bản.

---

# Tổng kết buổi học

* `__call__()` biến một object thành **callable object**, cho phép sử dụng cú pháp `obj(...)` như một hàm.
* Hàm (`function`), lớp (`class`) và các object có `__call__()` đều là **callable** trong Python.
* `callable(obj)` giúp kiểm tra một đối tượng có thể được gọi hay không.
* `__call__()` đặc biệt phù hợp cho các đối tượng đại diện cho **hành động** như validator, strategy, middleware, command, parser, pipeline hoặc task.
* Trong các framework hiện đại (Flask, PyTorch, Click...), `__call__()` được sử dụng rộng rãi để tạo API ngắn gọn, tự nhiên và dễ mở rộng.

---

## Kết thúc Phần V – Magic Methods

Đến đây, bạn đã làm chủ những Magic Methods cốt lõi:

* ✅ `__str__()` và `__repr__()`
* ✅ `__add__()`, `__sub__()`, `__eq__()`, `__lt__()`...
* ✅ `__len__()`, `__getitem__()`, `__iter__()`, `__contains__()`...
* ✅ `__call__()`

Đây là nền tảng để xây dựng các class có giao diện tự nhiên, Pythonic và tích hợp tốt với ngôn ngữ.

> **Buổi 21** chúng ta sẽ bắt đầu **Phần VI – Static và Class Method** với **`@staticmethod`**. Bạn sẽ hiểu sự khác biệt giữa *instance method*, *class method* và *static method*, biết khi nào nên dùng từng loại, cũng như cách áp dụng chúng vào các lớp `Model`, `Repository`, `Crawler` và `DatabaseManager` trong framework cào truyện mà bạn đang xây dựng.
