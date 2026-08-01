# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 23: Exception Handling & Logging (Phần 2) - `raise`, Custom Exception, Exception Chaining và Context Manager (`with`)

> **Đây là buổi học đánh dấu bước chuyển từ "người sử dụng Exception" sang "người thiết kế hệ thống Exception".**

Trong các dự án lớn như:

* Django
* FastAPI
* SQLAlchemy
* Requests
* Celery
* PySide6

bạn sẽ thấy lập trình viên **ít khi bắt Exception chung chung**, mà họ thường:

* Chủ động `raise` Exception.
* Tự định nghĩa Exception riêng.
* Dùng Exception Chaining.
* Sử dụng Context Manager để quản lý tài nguyên.

Đó là nội dung của buổi hôm nay.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu `raise`
* Tự tạo Exception
* Hiểu Exception Chaining
* Hiểu Context Manager
* Thành thạo `with`
* Biết cách quản lý File, Database, Lock...
* Biết cách thiết kế Exception chuyên nghiệp

---

# Phần I

# Chủ động tạo Exception (`raise`)

## 1. Vì sao cần `raise`?

Không phải Exception chỉ xuất hiện từ Python.

Lập trình viên cũng có thể tạo Exception.

Ví dụ:

```python
age = -5
```

Python thấy bình thường.

Nhưng nghiệp vụ nói:

> Tuổi không được âm.

Ta cần:

```python
raise ValueError("Age must be >= 0")
```

---

## 2. Ví dụ

```python
age = int(input())

if age < 0:
    raise ValueError("Tuổi không hợp lệ.")

print(age)
```

Nếu nhập:

```
-10
```

↓

```
ValueError:
Tuổi không hợp lệ.
```

---

# 3. `raise` dừng chương trình

```python
print("A")

raise RuntimeError("Oops")

print("B")
```

Kết quả:

```
A

RuntimeError
```

`B` không bao giờ chạy.

---

# 4. raise trong hàm

```python
def divide(a, b):

    if b == 0:
        raise ZeroDivisionError("Không được chia cho 0.")

    return a / b
```

Đây là cách thư viện Python hoạt động.

---

# Phần II

# Tạo Custom Exception

---

## 5. Tại sao cần?

Ví dụ:

Hệ thống ngân hàng.

Không muốn:

```python
ValueError
```

Muốn:

```python
InsufficientBalanceError
```

Dễ đọc hơn rất nhiều.

---

## 6. Tạo Exception

```python
class InsufficientBalanceError(Exception):
    pass
```

Sử dụng:

```python
raise InsufficientBalanceError("Không đủ tiền.")
```

---

## 7. Ví dụ Wallet

```python
class InsufficientBalanceError(Exception):
    pass


class Wallet:
    def __init__(self):

        self.balance = 100

    def withdraw(self, amount):

        if amount > self.balance:
            raise InsufficientBalanceError("Không đủ tiền.")

        self.balance -= amount
```

---

## 8. Bắt Custom Exception

```python
try:
    wallet.withdraw(500)

except InsufficientBalanceError as e:
    print(e)
```

Kết quả:

```
Không đủ tiền.
```

---

# Phần III

# Exception Hierarchy

Python:

```
BaseException
        │
Exception
        │
 ├── ValueError
 ├── TypeError
 ├── RuntimeError
 ├── OSError
 └── ...
```

Ta có thể:

```
Exception
      │
BusinessError
      │
 ├── PaymentError
 ├── LoginError
 ├── OrderError
 └── ...
```

Đây là cách thiết kế Exception trong doanh nghiệp.

---

# Phần IV

# Exception Chaining

---

## 9. Ví dụ

```python
try:
    int("abc")

except ValueError as e:
    raise RuntimeError("Lỗi xử lý dữ liệu")
```

Python sẽ hiển thị:

```
During handling...
```

---

## 10. raise from

Đúng hơn:

```python
try:
    int("abc")

except ValueError as e:
    raise RuntimeError("Không đọc được tuổi") from e
```

Python giữ nguyên nguyên nhân gốc.

Đây gọi là:

**Exception Chaining**

---

## 11. Lợi ích

Ví dụ:

```
JSON Error

↓

API Error

↓

Application Error
```

Ta biết lỗi gốc từ đâu.

---

# Phần V

# Context Manager

---

## 12. Vì sao cần?

Ví dụ:

```python
file = open("data.txt")

content = file.read()

file.close()
```

Nếu:

```python
file.read()
```

bị lỗi.

↓

```
close()

không chạy
```

Có thể gây rò rỉ tài nguyên.

---

## 13. finally

```python
file = open("data.txt")

try:
    print(file.read())

finally:
    file.close()
```

Hoạt động.

Nhưng dài.

---

# 14. with

Python có:

```python
with open("data.txt") as file:
    print(file.read())
```

Không cần:

```python
close()
```

Python tự làm.

---

## 15. Cơ chế

Khi gặp:

```python
with ...
```

Python gọi:

```
__enter__()

↓

code

↓

__exit__()
```

---

# Phần VI

# Tự tạo Context Manager

---

## 16. Ví dụ

```python
class MyContext:
    def __enter__(self):

        print("Open")

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        print("Close")
```

Sử dụng:

```python
with MyContext():
    print("Hello")
```

Kết quả:

```
Open

Hello

Close
```

---

## 17. Nếu có Exception?

```python
with MyContext():
    raise ValueError
```

↓

```
Open

Close

ValueError
```

`__exit__()` vẫn chạy.

---

## 18. Ý nghĩa các tham số

```python
def __exit__(

    self,

    exc_type,

    exc_value,

    traceback
):
```

Nếu:

Không lỗi

↓

```
None
```

Có lỗi

↓

```
ValueError

division by zero

traceback
```

---

## 19. Chặn Exception

```python
def __exit__(...):

    return True
```

Exception sẽ bị chặn.

Thông thường **không nên lạm dụng** việc này vì có thể làm mất dấu lỗi.

---

# Phần VII

# Ví dụ thực tế

---

## Database

```python
with Session() as db:
    ...
```

Ra khỏi:

```
with
```

↓

```
close()
```

---

## Lock

```python
with lock:
    shared_data += 1
```

Tự:

```
acquire()

↓

release()
```

---

## ThreadPool

```python
with ThreadPoolExecutor() as executor:
    ...
```

Ra khỏi:

↓

```
shutdown()
```

---

## Temporary Directory

```python
with tempfile.TemporaryDirectory() as temp_dir:
    ...
```

Ra khỏi:

↓

```
Xóa thư mục
```

---

# Phần VIII

# contextlib

Python có module:

```python
from contextlib import contextmanager
```

Ví dụ:

```python
from contextlib import contextmanager


@contextmanager
def timer():

    print("Start")

    try:
        yield

    finally:
        print("End")
```

Sử dụng:

```python
with timer():
    print("Working...")
```

Đây là cách tạo Context Manager bằng generator, rất phổ biến trong các thư viện hiện đại.

---

# Phần IX

# Những lỗi phổ biến

## Sai

```python
except:
    pass
```

---

## Sai

```python
raise Exception()
```

Thay vì:

```python
raise PaymentError()
```

---

## Sai

```python
open()

...

quên close()
```

---

## Sai

Không dùng:

```python
with
```

---

# Phần X

# Bài tập

## Bài 1

Viết:

```python
safe_divide(a, b)
```

Nếu:

```
b == 0
```

↓

```
raise ZeroDivisionError
```

---

## Bài 2

Tạo:

```python
class InvalidAgeError(Exception):
```

Dùng cho:

```
age < 0
```

---

## Bài 3

Viết:

```python
Wallet
```

Có:

```
deposit()

withdraw()
```

Tạo:

```
InsufficientBalanceError
```

---

## Bài 4

Viết:

```python
class LoggerContext
```

Khi:

```
with
```

↓

```
Start

...

End
```

---

## Bài 5

Viết:

```python
class TimerContext
```

Đo thời gian chạy của một khối mã bằng `time.perf_counter()`.

---

## Bài 6

Viết Context Manager quản lý file log:

* Mở file khi vào `with`.
* Ghi dữ liệu.
* Đóng file khi thoát.

---

# Mini Project

# Hệ thống ATM

Thiết kế:

```
BankAccount
```

Custom Exception:

```
InvalidAmountError

↓

InsufficientBalanceError
```

Có:

```
deposit()

withdraw()

transfer()
```

Yêu cầu:

* `raise` đúng loại Exception.
* Dùng `try/except` ở giao diện CLI.
* Ghi log các giao dịch thành công và thất bại vào file bằng Context Manager.

**Mở rộng:**

* Tạo `TransactionContext` để tự động ghi log khi bắt đầu và kết thúc mỗi giao dịch.
* Dùng Exception Chaining (`raise ... from ...`) khi chuyển đổi lỗi từ tầng lưu trữ sang tầng nghiệp vụ.

---

# Tổng kết buổi 23

Hôm nay bạn đã học:

* ✅ `raise`
* ✅ Custom Exception
* ✅ Exception Hierarchy
* ✅ Exception Chaining (`raise ... from ...`)
* ✅ Context Manager
* ✅ `with`
* ✅ `__enter__`
* ✅ `__exit__`
* ✅ `contextlib.contextmanager`
* ✅ Thiết kế hệ thống xử lý lỗi chuyên nghiệp

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án Python hiện đại:

* **SQLAlchemy** sử dụng Context Manager để quản lý `Session`.
* **Requests** và nhiều thư viện mạng dùng Exception chuyên biệt (`Timeout`, `ConnectionError`, ...).
* **PySide6** thường chuyển các lỗi tầng thấp thành Exception nghiệp vụ để giao diện có thể hiển thị thông báo thân thiện.
* **Celery**, **FastAPI**, **Django** đều định nghĩa hệ thống Custom Exception riêng thay vì chỉ dùng `ValueError` hay `RuntimeError`.

Một nguyên tắc quan trọng là:

> **Hãy phát sinh (raise) Exception ở nơi phát hiện lỗi, và xử lý (except) Exception ở nơi biết cách khắc phục hoặc thông báo cho người dùng.**

Điều này giúp mã nguồn rõ ràng, dễ kiểm thử và dễ bảo trì.

---

# Chuẩn bị cho Buổi 24

Ở **Buổi 24**, chúng ta sẽ bắt đầu **Logging chuyên nghiệp** – một kỹ năng không thể thiếu khi xây dựng ứng dụng thực tế.

Bạn sẽ học:

* Logging là gì và vì sao không nên dùng `print()`.
* Module `logging`.
* Logger, Handler, Formatter.
* Các mức log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
* Ghi log ra console và file.
* `RotatingFileHandler` và `TimedRotatingFileHandler`.
* Thiết kế hệ thống log cho CLI, Web API, ứng dụng GUI và các tiến trình chạy nền.

Đây là bước giúp chương trình của bạn **dễ theo dõi, dễ vận hành và dễ gỡ lỗi** trong môi trường production.
