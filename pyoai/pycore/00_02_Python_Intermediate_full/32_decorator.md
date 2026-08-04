# Buổi 32. Decorator trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu vì sao Python có Decorator.
> * Hiểu khái niệm **First-class Function**.
> * Hiểu **Higher-order Function**.
> * Hiểu Decorator hoạt động như thế nào.
> * Thành thạo cú pháp `@decorator`.
> * Sử dụng `*args`, `**kwargs`.
> * Bảo toàn metadata bằng `functools.wraps`.
> * Viết các Decorator thực tế.
>
> **Lưu ý**
>
> Bạn đã học một khóa **Decorator Deep Dive** rất chi tiết trước đây. Buổi này là phiên bản **Python Intermediate**, tập trung vào cách sử dụng Decorator hiệu quả trong các dự án Python thông thường.

---

# 1. Decorator là gì?

Decorator là **một hàm nhận vào một hàm khác và trả về một hàm mới**.

Nói đơn giản:

```text
Function

↓

Decorator

↓

Function mới
```

Function mới vẫn làm việc cũ, nhưng được bổ sung thêm chức năng.

Ví dụ:

```text
login()

↓

Decorator

↓

Logging

↓

Timing

↓

Permission
```

---

# 2. Vì sao cần Decorator?

Không dùng Decorator:

```python
def download():
    print("Start")

    print("Downloading...")

    print("End")
```

Nếu có 100 hàm đều cần:

* ghi log
* đo thời gian
* kiểm tra quyền

thì sẽ phải lặp lại rất nhiều mã.

Decorator giúp tái sử dụng các chức năng đó.

---

# 3. Function là First-class Object

Trong Python, hàm cũng là đối tượng.

Có thể:

* gán cho biến,
* truyền làm tham số,
* trả về từ hàm.

Ví dụ:

```python
def hello():
    print("Hello")


x = hello

x()
```

Output:

```text
Hello
```

Không cần dấu `()` khi gán.

---

# 4. Hàm là tham số

```python
def greet():
    print("Hello")


def run(func):
    func()


run(greet)
```

Output:

```text
Hello
```

Đây là nền tảng của Decorator.

---

# 5. Hàm trả về hàm

```python
def outer():

    def inner():
        print("Inner")

    return inner
```

Sử dụng:

```python
f = outer()

f()
```

Output:

```text
Inner
```

---

# 6. Decorator đầu tiên

```python
def decorator(func):

    def wrapper():
        print("Before")

        func()

        print("After")

    return wrapper
```

Áp dụng:

```python
def hello():
    print("Hello")


hello = decorator(hello)

hello()
```

Output:

```text
Before
Hello
After
```

---

# 7. Cú pháp `@`

Thay vì:

```python
hello = decorator(hello)
```

Python hỗ trợ:

```python
@decorator
def hello():
    print("Hello")
```

Hai cách hoàn toàn tương đương.

---

# 8. Decorator với tham số

Sai:

```python
def hello(name):
    print(name)
```

Decorator cũ:

```python
def wrapper():
```

sẽ báo lỗi.

Cần:

```python
def decorator(func):

    def wrapper(name):

        print("Before")

        func(name)

        print("After")

    return wrapper
```

---

# 9. `*args`, `**kwargs`

Cách tốt nhất:

```python
def decorator(func):

    def wrapper(*args, **kwargs):

        print("Before")

        result = func(*args, **kwargs)

        print("After")

        return result

    return wrapper
```

Decorator này hoạt động với gần như mọi hàm.

---

# 10. Giá trị trả về

Ví dụ:

```python
def add(a, b):
    return a + b
```

Decorator:

```python
def decorator(func):

    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)

        return result

    return wrapper
```

Nếu quên `return result`, hàm được Decorator bọc sẽ luôn trả về `None`.

---

# 11. `functools.wraps`

Không dùng:

```python
@decorator
def hello():
    pass


print(hello.__name__)
```

Output:

```text
wrapper
```

Không còn tên hàm gốc.

---

Dùng:

```python
from functools import wraps


def decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        return func(*args, **kwargs)

    return wrapper
```

Bây giờ:

```python
print(hello.__name__)
```

↓

```text
hello
```

`wraps()` cũng giữ lại `__doc__`, `__annotations__` và nhiều metadata khác.

---

# 12. Decorator đo thời gian

```python
import time
from functools import wraps


def timer(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()

        print(f"Elapsed: {end - start:.6f}s")

        return result

    return wrapper
```

Sử dụng:

```python
@timer
def work():
    time.sleep(1)


work()
```

---

# 13. Decorator Logging

```python
from functools import wraps


def log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        print(f"Call {func.__name__}")

        return func(*args, **kwargs)

    return wrapper
```

---

# 14. Decorator kiểm tra quyền

```python
is_admin = False


def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not is_admin:
            raise PermissionError("Permission denied")

        return func(*args, **kwargs)

    return wrapper
```

---

# 15. Decorator Cache đơn giản

```python
from functools import wraps


def cache(func):

    data = {}

    @wraps(func)
    def wrapper(x):

        if x not in data:
            data[x] = func(x)

        return data[x]

    return wrapper
```

---

# 16. Decorator Factory

Decorator có tham số.

```python
def repeat(times):

    def decorator(func):

        def wrapper():

            for _ in range(times):
                func()

        return wrapper

    return decorator
```

Sử dụng:

```python
@repeat(3)
def hello():
    print("Hello")
```

Output:

```text
Hello
Hello
Hello
```

---

# 17. Nhiều Decorator

```python
@timer
@log
def download(): ...
```

Tương đương:

```python
download = timer(log(download))
```

Thứ tự rất quan trọng.

---

# 18. Decorator tích hợp sẵn

## `@staticmethod`

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b
```

---

## `@classmethod`

```python
class User:
    total = 0

    @classmethod
    def count(cls):
        return cls.total
```

---

## `@property`

```python
class Person:
    @property
    def name(self):
        return "Alice"
```

Sử dụng:

```python
p = Person()

print(p.name)
```

Không cần:

```python
p.name()
```

---

# 19. Decorator trong Flask

```python
@app.route("/")
def home():
    return "Hello"
```

`@app.route()` chính là một Decorator.

---

# 20. Decorator trong Click

```python
@click.command()
def main(): ...
```

---

# 21. Decorator trong Pytest

```python
@pytest.fixture
def db(): ...
```

---

# 22. Decorator trong Dataclass

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
```

---

# 23. Những lỗi thường gặp

## Sai 1: Quên trả về `wrapper`

```python
def decorator(func):

    def wrapper():
        pass
```

Thiếu:

```python
return wrapper
```

---

## Sai 2: Quên gọi hàm gốc

```python
def wrapper():

    print("Before")
```

Không có:

```python
func()
```

---

## Sai 3: Quên trả về kết quả

```python
result = func()

print(result)
```

Thiếu:

```python
return result
```

---

## Sai 4: Không dùng `wraps`

Làm mất metadata của hàm gốc, ảnh hưởng đến debug, tài liệu và introspection.

---

# 24. Best Practices

## ✔ Luôn dùng `functools.wraps`

```python
@wraps(func)
```

---

## ✔ Dùng `*args`, `**kwargs`

Để Decorator hoạt động với nhiều loại hàm.

---

## ✔ Decorator chỉ nên có một trách nhiệm

Ví dụ:

* Logging.
* Timing.
* Cache.
* Retry.
* Authentication.

Không nên trộn quá nhiều chức năng trong cùng một Decorator.

---

## ✔ Đặt tên rõ ràng

Ví dụ:

```text
timer
cache
retry
log_calls
require_admin
```

---

# 25. Mini Project - Utility Decorators

Cấu trúc:

```text
project/

├── decorators.py
└── main.py
```

`decorators.py`

Viết các Decorator:

* `@timer`
* `@log`
* `@retry`
* `@cache`

`main.py`

```python
@timer
@log
def download():
    print("Downloading...")
```

Mỗi Decorator đảm nhận một nhiệm vụ riêng, có thể kết hợp với nhau.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Decorator là gì.
* First-class Function.
* Higher-order Function.
* Cú pháp `@decorator`.
* `*args`, `**kwargs`.
* `functools.wraps`.
* Decorator Factory.
* Kết hợp nhiều Decorator.
* Các Decorator tích hợp sẵn (`@staticmethod`, `@classmethod`, `@property`).
* Ứng dụng Decorator trong Flask, Click, Pytest và Dataclass.

---

# Sơ đồ hoạt động của Decorator

```text
        hello()
           │
           ▼
    @decorator
           │
           ▼
     wrapper()
           │
     Before Logic
           │
           ▼
     hello() gốc
           │
           ▼
      After Logic
           │
           ▼
      Trả kết quả
```

---

# Bài tập thực hành

### Bài 1

Viết Decorator `@uppercase` để chuyển kết quả trả về của hàm thành chữ hoa.

Ví dụ:

```python
@uppercase
def greet():
    return "hello"
```

Kết quả:

```text
HELLO
```

---

### Bài 2

Viết Decorator `@timer` sử dụng `time.perf_counter()` để đo thời gian thực thi của hàm.

---

### Bài 3

Viết Decorator `@retry(times=3)`.

Nếu hàm phát sinh ngoại lệ thì tự động thử lại tối đa `times` lần.

---

### Bài 4

Viết Decorator `@require_role("admin")`.

Nếu người dùng không có quyền phù hợp thì phát sinh `PermissionError`.

---

### Bài 5

Viết Decorator `@log_args` để ghi ra:

* tên hàm,
* giá trị `args`,
* giá trị `kwargs`.

Ví dụ:

```text
Call add
args=(2, 3)
kwargs={}
```

---

### Bài 6 (Thử thách)

Xây dựng một thư viện nhỏ `decorators.py` gồm các Decorator:

* `@timer`
* `@log`
* `@retry`
* `@cache`
* `@validate_types`

Mỗi Decorator phải:

* sử dụng `functools.wraps`,
* hỗ trợ `*args`, `**kwargs`,
* có thể kết hợp với các Decorator khác,
* hoạt động đúng với các hàm có hoặc không có giá trị trả về.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 33**, chúng ta sẽ học **Closure** – nền tảng quan trọng phía sau Decorator, bao gồm:

* Lexical Scope.
* Free Variable.
* Closure là gì.
* Cách Python lưu trạng thái của Closure.
* `nonlocal`.
* Kiểm tra `__closure__`.
* Ứng dụng Closure trong Factory Function, Callback, Cache và Event Handler.

Closure sẽ giúp bạn hiểu sâu hơn cơ chế hoạt động của Decorator và nhiều mẫu thiết kế (design patterns) trong Python.
