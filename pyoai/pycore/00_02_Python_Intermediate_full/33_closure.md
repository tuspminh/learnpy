# Buổi 33. Closure trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu **Lexical Scope (Phạm vi từ vựng)**.
> * Hiểu **Free Variable**.
> * Hiểu **Closure** là gì.
> * Biết Python lưu trạng thái của Closure như thế nào.
> * Thành thạo `nonlocal`.
> * Biết kiểm tra `__closure__`.
> * Hiểu mối liên hệ giữa **Closure** và **Decorator**.
> * Ứng dụng Closure trong Factory Function, Callback, Cache và Event Handler.

> **Lưu ý**
>
> Bạn đã học một khóa **Decorator Deep Dive**, nên buổi này sẽ tập trung vào **nền tảng phía sau Decorator**, giúp bạn hiểu tại sao Decorator hoạt động được.

---

# 1. Closure là gì?

Closure là:

> **Một hàm bên trong (inner function) ghi nhớ các biến của hàm bên ngoài (outer function), ngay cả khi hàm bên ngoài đã kết thúc.**

Ví dụ:

```python
def outer():
    message = "Hello"

    def inner():
        print(message)

    return inner
```

Sử dụng:

```python
func = outer()

func()
```

Kết quả:

```text
Hello
```

Điều đặc biệt là:

* `outer()` đã kết thúc.
* Biến `message` đáng lẽ phải bị hủy.
* Nhưng `inner()` vẫn nhớ được giá trị của `message`.

Đó chính là **Closure**.

---

# 2. Vì sao Closure tồn tại?

Thông thường:

```python
def demo():
    x = 10
```

Sau khi `demo()` kết thúc:

```text
x
↓

Bị hủy
```

Nhưng nếu có Closure:

```python
def demo():
    x = 10

    def inner():
        return x

    return inner
```

Python sẽ giữ lại:

```text
x = 10
```

vì `inner()` vẫn đang sử dụng nó.

---

# 3. Lexical Scope

Python tìm biến theo thứ tự:

```text
Local
↓

Enclosing
↓

Global
↓

Built-in
```

Đây gọi là quy tắc **LEGB**.

Ví dụ:

```python
x = "Global"


def outer():
    x = "Outer"

    def inner():
        print(x)

    inner()
```

Kết quả:

```text
Outer
```

Python tìm thấy `x` ở phạm vi **Enclosing** nên không cần tìm tiếp.

---

# 4. Free Variable

Ví dụ:

```python
def outer():
    name = "Alice"

    def inner():
        print(name)

    return inner
```

Ở đây:

```text
name
```

không phải biến cục bộ của `inner()`.

Nó được gọi là **Free Variable**.

---

# 5. Closure hoạt động thế nào?

```python
def make_printer(text):

    def printer():
        print(text)

    return printer
```

```python
hello = make_printer("Hello")
python = make_printer("Python")

hello()
python()
```

Kết quả:

```text
Hello
Python
```

Mỗi Closure có **một trạng thái riêng**.

---

# 6. Closure lưu trạng thái

Ví dụ:

```python
def counter():
    count = 0

    def increment():
        return count

    return increment
```

Mặc dù `counter()` kết thúc, biến `count` vẫn tồn tại bên trong Closure.

---

# 7. Thay đổi biến với `nonlocal`

Sai:

```python
def counter():
    count = 0

    def increment():
        count += 1
```

Lỗi:

```text
UnboundLocalError
```

Vì Python nghĩ `count` là biến cục bộ của `increment()`.

---

# 8. `nonlocal`

Đúng:

```python
def counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment
```

Sử dụng:

```python
c = counter()

print(c())
print(c())
print(c())
```

Kết quả:

```text
1
2
3
```

---

# 9. `global` và `nonlocal`

`global`:

```python
x = 10


def func():
    global x
    x += 1
```

Sửa biến toàn cục.

---

`nonlocal`:

```python
def outer():
    x = 10

    def inner():
        nonlocal x
```

Sửa biến của hàm bao ngoài gần nhất.

---

# 10. Kiểm tra Closure

```python
def outer():
    x = 100

    def inner():
        return x

    return inner
```

```python
f = outer()

print(f.__closure__)
```

Kết quả:

```text
(<cell at ...>,)
```

---

# 11. Xem giá trị bên trong Closure

```python
print(f.__closure__[0].cell_contents)
```

Kết quả:

```text
100
```

Python lưu biến trong các **cell object**.

---

# 12. Closure nhiều biến

```python
def person(name, age):

    def show():
        print(name, age)

    return show
```

```python
p = person("Alice", 20)

p()
```

Kết quả:

```text
Alice 20
```

---

# 13. Factory Function

Closure thường được dùng để tạo hàm.

Ví dụ:

```python
def multiply(n):

    def calc(x):
        return x * n

    return calc
```

Sử dụng:

```python
double = multiply(2)
triple = multiply(3)

print(double(5))
print(triple(5))
```

Kết quả:

```text
10
15
```

---

# 14. Callback

```python
def callback(msg):

    def run():
        print(msg)

    return run
```

```python
cb = callback("Finished")

cb()
```

---

# 15. Cache đơn giản

```python
def cache():

    data = {}

    def get(key):

        return data.get(key)

    return get
```

Closure giúp lưu `data` mà không cần biến toàn cục.

---

# 16. Closure và Decorator

Decorator thực chất là:

```python
def decorator(func):

    def wrapper(*args, **kwargs):

        print("Before")

        result = func(*args, **kwargs)

        print("After")

        return result

    return wrapper
```

Ở đây:

```text
wrapper
```

chính là một **Closure**.

Nó ghi nhớ:

```text
func
```

---

# 17. Decorator Factory

```python
def repeat(times):

    def decorator(func):

        def wrapper():

            for _ in range(times):
                func()

        return wrapper

    return decorator
```

Ở đây có hai Closure:

* `decorator()` nhớ `times`.
* `wrapper()` nhớ `func`.

---

# 18. Closure trong GUI

Ví dụ:

```python
def click_handler(name):

    def on_click():
        print(name)

    return on_click
```

Mỗi nút bấm sẽ có một Closure riêng.

---

# 19. Closure trong Event

```python
buttons = []

for i in range(3):
    buttons.append(lambda: print(i))
```

Kết quả:

```text
2
2
2
```

Đây là lỗi **Late Binding**.

---

# 20. Cách sửa Late Binding

```python
buttons = []

for i in range(3):
    buttons.append(lambda i=i: print(i))
```

Hoặc dùng Closure:

```python
def make_handler(i):

    def handler():
        print(i)

    return handler
```

---

# 21. Những lỗi thường gặp

## Sai 1

Quên `nonlocal`

```python
count += 1
```

↓

```text
UnboundLocalError
```

---

## Sai 2

Nhầm `global` với `nonlocal`.

---

## Sai 3

Không hiểu Late Binding.

---

# 22. Best Practices

## ✔ Dùng Closure khi cần lưu trạng thái nhỏ

Ví dụ:

* Counter.
* Cache.
* Callback.
* Factory.

---

## ✔ Không lạm dụng Closure

Nếu trạng thái phức tạp:

```text
20 biến

15 phương thức
```

→ dùng Class sẽ rõ ràng hơn.

---

## ✔ Dùng `nonlocal` thay vì `global`

Nếu chỉ cần sửa biến trong hàm bao ngoài.

---

## ✔ Đặt tên hàm rõ ràng

Ví dụ:

```text
make_logger
make_counter
make_multiplier
make_handler
```

---

# 23. Mini Project - Counter Factory

Cấu trúc:

```text
counter_factory/
│
└── main.py
```

Yêu cầu:

Viết:

```python
counter = make_counter()
```

Mỗi lần gọi:

```python
print(counter())
```

Kết quả:

```text
1
2
3
4
5
```

Không dùng biến toàn cục và không dùng class.

---

# 24. Mini Project - Logger Factory

Viết:

```python
info = make_logger("INFO")
error = make_logger("ERROR")
```

Kết quả:

```python
info("Start")
error("Database")
```

In ra:

```text
[INFO] Start
[ERROR] Database
```

Mỗi hàm logger là một Closure ghi nhớ mức log (`INFO`, `ERROR`).

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Lexical Scope và quy tắc LEGB.
* Free Variable.
* Closure là gì.
* Cách Python lưu trạng thái của Closure.
* `nonlocal`.
* Kiểm tra `__closure__`.
* Late Binding và cách khắc phục.
* Mối quan hệ giữa Closure và Decorator.
* Ứng dụng Closure trong Factory Function, Callback, Cache và Event Handler.

---

# Sơ đồ hoạt động của Closure

```text
outer()
│
├── x = 10
│
├── inner()
│     │
│     └── sử dụng x
│
└── return inner
        │
        ▼
Closure giữ lại:
    x = 10
```

---

# So sánh Closure và Class

| Tiêu chí          | Closure                      | Class                           |
| ----------------- | ---------------------------- | ------------------------------- |
| Lưu trạng thái    | ✔                            | ✔                               |
| Dễ viết           | ✔                            | Trung bình                      |
| Nhiều phương thức | ✖                            | ✔                               |
| Dữ liệu phức tạp  | ✖                            | ✔                               |
| Phù hợp           | Callback, Factory, Decorator | Hệ thống lớn, mô hình đối tượng |

**Quy tắc kinh nghiệm:**

* Chỉ cần **1–2 hàm và một ít trạng thái** → dùng **Closure**.
* Có **nhiều trạng thái hoặc nhiều hành vi** → dùng **Class**.

---

# Bài tập thực hành

### Bài 1

Viết `make_multiplier(n)` trả về một Closure nhân số đầu vào với `n`.

Ví dụ:

```python
double = make_multiplier(2)
print(double(8))
```

Kết quả:

```text
16
```

---

### Bài 2

Viết `make_counter()` sử dụng `nonlocal` để đếm số lần gọi.

---

### Bài 3

Viết `make_cache()` lưu kết quả của các phép tính đơn giản (ví dụ bình phương của một số) bằng Closure thay vì biến toàn cục.

---

### Bài 4

Viết `make_prefix(prefix)` trả về một hàm thêm tiền tố vào chuỗi.

Ví dụ:

```python
warning = make_prefix("[WARNING]")

print(warning("Disk Full"))
```

Kết quả:

```text
[WARNING] Disk Full
```

---

### Bài 5

Sửa đoạn mã sau để tránh lỗi **Late Binding**:

```python
handlers = []

for i in range(5):
    handlers.append(lambda: print(i))
```

Để kết quả lần lượt là:

```text
0
1
2
3
4
```

---

### Bài 6 (Thử thách)

Xây dựng một **Rate Limiter** bằng Closure:

* `make_rate_limiter(limit)`
* Cho phép gọi tối đa `limit` lần.
* Các lần gọi vượt quá giới hạn sẽ trả về:

```text
Rate limit exceeded
```

Không sử dụng biến toàn cục hoặc class.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 34**, chúng ta sẽ học **Context Manager** – một trong những tính năng quan trọng nhất của Python để quản lý tài nguyên an toàn và tự động. Nội dung sẽ bao gồm:

* Khái niệm Context Manager.
* Câu lệnh `with`.
* Giao thức `__enter__()` và `__exit__()`.
* Xây dựng Context Manager bằng class.
* Sử dụng `contextlib.contextmanager`.
* Quản lý file, database connection, lock và các tài nguyên khác một cách an toàn.
