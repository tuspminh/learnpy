# Buổi 34. Context Manager trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Context Manager là gì.
> * Hiểu tại sao nên dùng `with`.
> * Thành thạo giao thức Context Manager (`__enter__()` và `__exit__()`).
> * Tự xây dựng Context Manager bằng class.
> * Sử dụng `contextlib.contextmanager`.
> * Hiểu cách xử lý ngoại lệ trong Context Manager.
> * Áp dụng Context Manager vào quản lý file, database, lock và tài nguyên hệ thống.

> **Lưu ý**
>
> Bạn đã học về **Exception**, **Iterator**, **Generator** và **Closure**. Buổi này sẽ kết nối các kiến thức đó để hiểu một trong những cơ chế quan trọng nhất của Python.

---

# 1. Context Manager là gì?

Context Manager là một đối tượng giúp:

* Chuẩn bị tài nguyên trước khi sử dụng.
* Tự động dọn dẹp tài nguyên sau khi sử dụng.

Ví dụ:

```python
with open("data.txt") as f:
    print(f.read())
```

Bạn không cần viết:

```python
f.close()
```

Python sẽ tự động đóng file.

---

# 2. Vì sao cần Context Manager?

Không dùng Context Manager:

```python
f = open("data.txt")

data = f.read()

f.close()
```

Nếu xảy ra lỗi:

```python
f = open("data.txt")

raise Exception()

f.close()
```

↓

`f.close()` sẽ không được gọi.

File vẫn mở.

---

# 3. Dùng `try...finally`

Trước khi có `with`, người ta thường viết:

```python
f = open("data.txt")

try:
    print(f.read())

finally:
    f.close()
```

`finally` luôn chạy.

Đây chính là ý tưởng mà `with` tự động hóa.

---

# 4. Câu lệnh `with`

```python
with open("data.txt") as f:
    print(f.read())
```

Python thực hiện gần tương đương:

```python
f = open("data.txt")

try:
    print(f.read())

finally:
    f.close()
```

`with` giúp mã ngắn gọn, dễ đọc và an toàn hơn.

---

# 5. Context Manager Protocol

Một Context Manager phải triển khai:

```python
__enter__()

__exit__()
```

Đây gọi là **Context Manager Protocol**.

---

# 6. `__enter__()`

Ví dụ:

```python
class Demo:
    def __enter__(self):
        print("Enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("Exit")
```

Sử dụng:

```python
with Demo():
    print("Inside")
```

Output:

```text
Enter
Inside
Exit
```

---

# 7. `__exit__()`

```python
def __exit__(self, exc_type, exc, tb):
    print("Cleaning...")
```

Luôn được gọi:

* Có lỗi.
* Không có lỗi.

---

# 8. Thứ tự hoạt động

```text
with Demo() as d

↓

__enter__()

↓

Khối with

↓

__exit__()
```

---

# 9. Giá trị của `as`

```python
class Demo:
    def __enter__(self):
        return "Hello"

    def __exit__(self, *args):
        pass
```

```python
with Demo() as value:
    print(value)
```

Output:

```text
Hello
```

Giá trị sau `as` chính là giá trị được trả về từ `__enter__()`.

---

# 10. Xử lý ngoại lệ

```python
class Demo:
    def __enter__(self):
        print("Open")

    def __exit__(self, exc_type, exc, tb):

        print(exc_type)
        print(exc)

        return False
```

```python
with Demo():
    1 / 0
```

Output:

```text
Open

<class 'ZeroDivisionError'>

division by zero
```

---

# 11. `return True` trong `__exit__()`

Nếu:

```python
return True
```

Python sẽ:

```text
Nuốt Exception
```

Ví dụ:

```python
class IgnoreError:
    def __enter__(self):
        pass

    def __exit__(self, *args):
        return True
```

```python
with IgnoreError():
    1 / 0

print("Continue")
```

Output:

```text
Continue
```

Không có lỗi được lan truyền ra ngoài.

> Chỉ nên trả về `True` khi bạn thực sự muốn xử lý hoàn toàn ngoại lệ.

---

# 12. Tự xây dựng File Manager

```python
class FileManager:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename)
        return self.file

    def __exit__(self, exc_type, exc, tb):
        self.file.close()
```

Sử dụng:

```python
with FileManager("data.txt") as f:
    print(f.read())
```

---

# 13. Database Connection

```python
class Database:
    def __enter__(self):

        print("Connect DB")

        return self

    def __exit__(self, *args):

        print("Close DB")
```

```python
with Database():
    print("Query...")
```

Output:

```text
Connect DB

Query...

Close DB
```

---

# 14. Lock

Ví dụ:

```python
from threading import Lock

lock = Lock()

with lock:
    print("Critical Section")
```

Sau khi kết thúc:

```text
lock.release()
```

được gọi tự động.

---

# 15. `contextlib.contextmanager`

Không cần viết class.

```python
from contextlib import contextmanager


@contextmanager
def demo():

    print("Enter")

    yield

    print("Exit")
```

Sử dụng:

```python
with demo():
    print("Hello")
```

Output:

```text
Enter

Hello

Exit
```

---

# 16. `yield` trong Context Manager

Trong `@contextmanager`:

```python
yield
```

chia hàm thành hai phần:

Trước `yield`:

```text
__enter__()
```

Sau `yield`:

```text
__exit__()
```

---

# 17. Trả giá trị

```python
@contextmanager
def demo():

    yield "Python"
```

```python
with demo() as value:
    print(value)
```

↓

```text
Python
```

---

# 18. Xử lý Exception

```python
from contextlib import contextmanager


@contextmanager
def demo():

    try:
        yield

    finally:
        print("Cleanup")
```

Dù có lỗi:

```python
with demo():
    1 / 0
```

↓

```text
Cleanup
```

vẫn được in ra trước khi ngoại lệ được lan truyền.

---

# 19. Context Manager lồng nhau

```python
with open("a.txt") as a:
    with open("b.txt") as b:
        pass
```

Có thể viết gọn:

```python
with open("a.txt") as a, open("b.txt") as b:
    pass
```

---

# 20. `ExitStack`

Nếu số lượng Context Manager thay đổi động:

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(name)) for name in names]
```

`ExitStack` rất hữu ích khi không biết trước có bao nhiêu tài nguyên cần quản lý.

---

# 21. Những lỗi thường gặp

## Sai 1

Quên đóng tài nguyên:

```python
f = open("file.txt")
```

Không có:

```python
f.close()
```

---

## Sai 2

Viết `__enter__()` nhưng quên:

```python
return self
```

Khi đó:

```python
with Demo() as d:
```

↓

`d` sẽ là `None`.

---

## Sai 3

`__exit__()` không nhận đủ tham số

Đúng:

```python
def __exit__(
    self,
    exc_type,
    exc,
    tb
):
```

hoặc:

```python
def __exit__(self, *args):
```

---

## Sai 4

Luôn `return True`

Điều này làm che giấu lỗi, khiến việc gỡ lỗi khó khăn.

---

# 22. Best Practices

## ✔ Luôn dùng `with`

Đúng:

```python
with open("data.txt") as f:
    ...
```

Sai:

```python
f = open(...)
...
f.close()
```

---

## ✔ Chỉ `return True` nếu thực sự xử lý ngoại lệ

Nếu không, hãy:

```python
return False
```

hoặc không trả về gì (`None`).

---

## ✔ Dùng `@contextmanager` cho trường hợp đơn giản

Nếu chỉ cần quản lý một tài nguyên với ít logic, `@contextmanager` sẽ ngắn gọn hơn class.

---

## ✔ Dùng Class khi có nhiều trạng thái

Ví dụ:

* Connection Pool.
* Transaction.
* Cache.
* Resource Manager.

---

# 23. Mini Project - Timer Context Manager

```python
import time


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {elapsed:.6f}s")
```

Sử dụng:

```python
with Timer():
    total = sum(range(1_000_000))
```

---

# 24. Mini Project - Temporary Directory

Sử dụng:

```python
import tempfile

with tempfile.TemporaryDirectory() as path:
    print(path)
```

Sau khi kết thúc:

```text
Thư mục tạm được xóa tự động.
```

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Context Manager là gì.
* Câu lệnh `with`.
* Giao thức `__enter__()` và `__exit__()`.
* Giá trị trả về của `__enter__()`.
* Xử lý ngoại lệ trong `__exit__()`.
* `contextlib.contextmanager`.
* `ExitStack`.
* Quản lý file, database, lock và tài nguyên hệ thống.

---

# Sơ đồ hoạt động của `with`

```text
        with Resource() as r
                │
                ▼
          __enter__()
                │
                ▼
      Khối lệnh trong with
                │
                ▼
    Có lỗi? ─────────► Có
       │               │
       │               ▼
       │        __exit__(exc)
       │               │
       ▼               │
 Không lỗi             │
       │               │
       └──────► __exit__(None)
                    │
                    ▼
             Giải phóng tài nguyên
```

---

# So sánh hai cách tạo Context Manager

| Tiêu chí         | Class       | `@contextmanager` |
| ---------------- | ----------- | ----------------- |
| Dễ viết          | Trung bình  | Rất dễ            |
| Nhiều trạng thái | ✔           | ✖                 |
| Tái sử dụng      | ✔           | ✔                 |
| Logic đơn giản   | Được        | Rất phù hợp       |
| Logic phức tạp   | Rất phù hợp | Có thể khó đọc    |

---

# Bài tập thực hành

### Bài 1

Viết `PrintContext`:

```python
with PrintContext():
    print("Hello")
```

Kết quả:

```text
Begin
Hello
End
```

---

### Bài 2

Viết `Timer` Context Manager để đo thời gian thực thi của một khối lệnh.

---

### Bài 3

Viết `ChangeDirectory(path)`:

```python
with ChangeDirectory("/tmp"):
    print(os.getcwd())
```

Sau khi thoát `with`, thư mục làm việc phải được khôi phục về ban đầu.

---

### Bài 4

Viết Context Manager bằng `@contextmanager` để mở file, đọc nội dung và luôn đóng file trong khối `finally`.

---

### Bài 5

Sử dụng `ExitStack` để mở danh sách nhiều file có tên trong một danh sách và in dòng đầu tiên của mỗi file.

---

### Bài 6 (Thử thách)

Xây dựng một **Transaction Context Manager** giả lập:

* Khi vào `with`: in `BEGIN TRANSACTION`.
* Nếu khối lệnh thành công: in `COMMIT`.
* Nếu có ngoại lệ: in `ROLLBACK`.
* Sau cùng luôn in `DISCONNECT`.

Mục tiêu là mô phỏng cách các thư viện ORM và driver cơ sở dữ liệu quản lý giao dịch.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 35**, chúng ta sẽ học **Typing** trong Python Intermediate, bao gồm:

* Type Hint (`int`, `str`, `list`, `dict`, ...).
* `Optional`, `Union`, `Any`.
* `TypeAlias`, `Literal`.
* `Callable`.
* `TypeVar` và Generic cơ bản.
* Kiểm tra kiểu bằng các công cụ như `mypy`.
* Các nguyên tắc viết mã có kiểu rõ ràng để tăng khả năng bảo trì và giảm lỗi trong các dự án Python lớn.
