# OOP Deep Dive – Buổi 23

# Callable Objects & Context Manager Deep Dive – `__call__()`, `with`, `__enter__()`, `__exit__()`

> Đây là một trong những chủ đề quan trọng nhất của Python OOP.
>
> Sau buổi này, bạn sẽ hiểu vì sao những đoạn code như sau lại hoạt động:

```python
with open("data.txt") as f:
    data = f.read()
```

hay

```python
session = requests.Session()

response = session(url)
```

hoặc

```python
app = FastAPI()

app()
```

Hay tại sao nhiều framework có thể biến **object thành function**.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Object Callable
* `__call__()`
* Context Manager
* `with`
* `__enter__()`
* `__exit__()`
* Exception Handling trong Context Manager
* Context Manager lồng nhau
* `contextlib`
* `ExitStack`
* Async Context Manager (`__aenter__`, `__aexit__`)

---

# 1. Object có thể gọi như function?

Ví dụ

```python
print("Hello")
```

Ta đều biết:

```python
print
```

là function.

Nhưng Python không yêu cầu thứ được gọi phải là function.

Nó chỉ cần **callable**.

---

# 2. Callable là gì?

Thử

```python
callable(print)
```

↓

```text
True
```

---

```python
callable(len)
```

↓

```text
True
```

---

```python
callable(123)
```

↓

```text
False
```

---

# 3. Tự tạo Callable Object

```python
class Greeter:

    def __call__(self):

        print("Hello")
```

---

```python
g = Greeter()

g()
```

↓

```text
Hello
```

Python thực chất gọi

```python
g.__call__()
```

---

# 4. Có tham số

```python
class Adder:

    def __call__(

        self,

        a,

        b

    ):

        return a+b
```

---

```python
adder = Adder()

print(adder(2,3))
```

↓

```text
5
```

---

# 5. Tại sao dùng `__call__()`?

Ví dụ

```python
class Counter:

    def __init__(self):

        self.count=0

    def __call__(self):

        self.count+=1

        return self.count
```

---

```python
c = Counter()

print(c())
print(c())
print(c())
```

↓

```text
1
2
3
```

Một function bình thường không tự giữ trạng thái như object (trừ khi dùng closure hoặc kỹ thuật khác).

---

# 6. Decorator Class

Bạn đã học Decorator.

Có thể viết

```python
class Timer:

    def __call__(

        self,

        func

    ):

        ...
```

Lúc này

```python
@Timer()
def hello():
    ...
```

Hoạt động.

Decorator không nhất thiết phải là function.

---

# 7. `with`

Ví dụ

```python
with open("a.txt") as f:

    print(f.read())
```

Điều gì xảy ra?

---

# 8. Python làm gì?

Thực chất

```python
with obj as x:
```

gần tương đương:

```python
manager = obj

x = manager.__enter__()

try:

    ...

finally:

    manager.__exit__()
```

Đây là ý tưởng cốt lõi của `with`.

---

# 9. Context Manager

Một Context Manager cần

```python
__enter__()

__exit__()
```

---

# 10. Ví dụ đơn giản

```python
class Demo:

    def __enter__(self):

        print("Open")

        return self

    def __exit__(

        self,

        exc_type,

        exc,

        tb

    ):

        print("Close")
```

---

```python
with Demo():

    print("Working")
```

↓

```text
Open

Working

Close
```

---

# 11. `__enter__()`

Có nhiệm vụ:

* mở resource
* khởi tạo
* trả object

Ví dụ

```python
def __enter__(self):

    return self
```

---

# 12. `__exit__()`

Có nhiệm vụ

* đóng file
* đóng socket
* rollback transaction
* release lock

---

Ví dụ

```python
def __exit__(

    self,

    exc_type,

    exc,

    tb

):

    print("Cleanup")
```

---

# 13. Exception

```python
with Demo():

    raise ValueError
```

Python vẫn gọi

```python
__exit__()
```

↓

Đảm bảo cleanup.

Đây là lý do `with` rất hữu ích khi làm việc với tài nguyên.

---

# 14. Ba tham số

```python
exc_type

exc

tb
```

Ví dụ

```python
print(exc_type)
```

↓

```text
<class 'ValueError'>
```

---

# 15. Chặn Exception

Nếu

```python
__exit__()
```

trả về

```python
True
```

Python sẽ:

Không ném exception ra ngoài.

Ví dụ

```python
def __exit__(

    self,

    exc_type,

    exc,

    tb

):

    print(exc)

    return True
```

---

```python
with Demo():

    raise ValueError("Error")
```

↓

Không crash.

⚠️ Chỉ nên làm điều này khi bạn thực sự muốn xử lý hoàn toàn ngoại lệ. Nếu không, hãy trả về `False` (hoặc không trả gì).

---

# 16. File hoạt động thế nào?

```python
with open(...) as f:
```

↓

```text
__enter__()

↓

File Object

↓

Read

↓

__exit__()

↓

Close File
```

Đó là lý do file luôn được đóng.

---

# 17. SQLite

```python
with sqlite3.connect(...) as conn:
```

↓

Có thể:

* commit
* rollback
* close

Tự động (tùy theo API của `sqlite3`).

---

# 18. Tự làm Transaction

```python
class Transaction:

    def __enter__(self):

        print("BEGIN")

        return self

    def __exit__(

        self,

        exc_type,

        exc,

        tb

    ):

        if exc:

            print("ROLLBACK")

        else:

            print("COMMIT")
```

---

```python
with Transaction():

    print("Insert...")
```

↓

```text
BEGIN

Insert...

COMMIT
```

---

Nếu có lỗi

↓

```text
BEGIN

ROLLBACK
```

---

# 19. Context Manager lồng nhau

```python
with A():

    with B():

        ...
```

↓

Thực thi

```text
Enter A

Enter B

Work

Exit B

Exit A
```

Đây là nguyên tắc LIFO (Last In, First Out).

---

# 20. `contextlib`

Python có

```python
from contextlib import contextmanager
```

Cho phép viết Context Manager bằng generator.

Ví dụ

```python
from contextlib import contextmanager

@contextmanager
def demo():

    print("Open")

    try:
        yield

    finally:
        print("Close")
```

---

```python
with demo():

    print("Working")
```

↓

```text
Open

Working

Close
```

---

# 21. `ExitStack`

Khi không biết trước sẽ mở bao nhiêu tài nguyên.

Ví dụ

```python
from contextlib import ExitStack

with ExitStack() as stack:

    files = [

        stack.enter_context(open(f))

        for f in filenames

    ]
```

Rất hữu ích khi số lượng file hoặc kết nối được quyết định tại runtime.

---

# 22. Async Context Manager

Trong asyncio

```python
async with session:
```

Python gọi

```python
__aenter__()

__aexit__()
```

Đây là phiên bản bất đồng bộ của Context Manager.

---

# 23. Áp dụng vào hệ thống crawler

Ví dụ

```python
with HttpClient() as client:

    client.fetch(...)
```

↓

Tự động

* mở session
* đóng session

---

Hoặc

```python
with Database() as db:
```

↓

* mở connection
* commit / rollback
* close

---

# 24. Crawler Worker

```python
with Worker() as worker:

    worker.run()
```

↓

* Start Worker
* Run
* Stop Worker

Không cần nhớ gọi `start()` và `stop()` thủ công.

---

# 25. Sơ đồ

```text
             with

              │

      __enter__()

              │

              ▼

      Resource Ready

              │

              ▼

          User Code

              │

              ▼

      __exit__()

              │

              ▼

      Release Resource
```

---

# 26. Callable + Context Manager

Một object có thể vừa:

```python
__call__()
```

vừa

```python
__enter__()

__exit__()
```

Ví dụ

```python
client()

with client:
```

Hai cơ chế này độc lập và có thể kết hợp.

---

# 27. Tổng kết

| Magic Method   | Được gọi khi          |
| -------------- | --------------------- |
| `__call__()`   | `obj()`               |
| `__enter__()`  | Bắt đầu `with`        |
| `__exit__()`   | Kết thúc `with`       |
| `__aenter__()` | `async with`          |
| `__aexit__()`  | Kết thúc `async with` |

---

# Điều quan trọng nhất cần nhớ

Context Manager không chỉ giúp mã nguồn đẹp hơn mà còn **đảm bảo tài nguyên luôn được giải phóng**, ngay cả khi có ngoại lệ.

Đây là lý do bạn sẽ thấy `with` xuất hiện khắp nơi trong Python:

* File
* Database
* Lock
* Thread
* Network
* HTTP Session
* Transaction
* Temporary Directory

---

# Bài tập thực hành

## Bài 1

Viết lớp `Logger`:

```python
with Logger():
    print("Hello")
```

Kết quả:

```text
=== START ===
Hello
=== END ===
```

---

## Bài 2

Viết lớp `Connection`:

* `__enter__()` in:

```text
Connect Database
```

* `__exit__()` in:

```text
Disconnect Database
```

Kiểm tra cả trường hợp có và không có ngoại lệ.

---

## Bài 3

Viết lớp `Multiplier`:

```python
m = Multiplier(5)

print(m(10))
```

↓

```text
50
```

Yêu cầu triển khai bằng `__call__()`.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế các lớp:

* `HttpClient`
* `DatabaseSession`
* `CrawlerWorker`

Để hỗ trợ API sau:

```python
with HttpClient() as client:
    html = client.fetch(url)

with DatabaseSession() as db:
    db.save(novel)

with CrawlerWorker() as worker:
    worker.crawl(source)
```

Hãy xác định rõ:

* `__enter__()` sẽ chuẩn bị tài nguyên gì.
* `__exit__()` sẽ giải phóng hoặc hoàn tất những gì.
* Khi có ngoại lệ, lớp nào nên rollback, lớp nào chỉ cần cleanup.

---

# Chuẩn bị cho Buổi 24

Buổi tiếp theo sẽ đi vào **Attribute Access Protocol** — một trong những cơ chế mạnh nhất của Python:

* `__getattribute__()`
* `__getattr__()`
* `__setattr__()`
* `__delattr__()`
* `__dir__()`
* `__slots__()`

Sau buổi này, bạn sẽ hiểu cách:

* ORM ánh xạ cột thành thuộc tính.
* Proxy Object hoạt động.
* Lazy Loading.
* Validation tự động khi gán giá trị.
* Giảm đáng kể bộ nhớ của hàng triệu object bằng `__slots__()`.

Đây là nền tảng của rất nhiều framework lớn như Django ORM, SQLAlchemy, Pydantic và các thư viện tối ưu hiệu năng.
