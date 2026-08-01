# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 12: Làm chủ Decorator từ Cơ bản đến Chuyên nghiệp (Phần 1)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu Decorator là gì và vì sao Python có Decorator.
> - Hiểu mối liên hệ giữa Function, Closure và Decorator.
> - Tự viết Decorator từ đầu.
> - Biết cách trang trí (decorate) một hàm.
> - Thành thạo Decorator có và không có tham số.
> - Hiểu `functools.wraps`.
> - Biết các ứng dụng thực tế như logging, đo thời gian thực thi, kiểm tra quyền, cache,...

---

# 1. Decorator là gì?

Decorator là một trong những tính năng mạnh nhất của Python.

Nó cho phép:

> **Thêm chức năng mới vào một hàm mà không cần sửa mã nguồn của hàm đó.**

Hãy tưởng tượng:

Có một hàm:

```text-x-trilium-auto
def login():
    print("Đăng nhập...")
```

Sau này muốn:

- Ghi log
- Kiểm tra quyền
- Đo thời gian
- Cache
- Retry khi lỗi

Bạn có muốn sửa hàm `login()` mỗi lần không?

Không.

Decorator giải quyết vấn đề này.

---

# 2. Ví dụ thực tế

Bạn có:

```text-x-trilium-auto
def transfer_money():
    print("Chuyển tiền thành công")
```

Ngân hàng muốn:

Trước khi chuyển tiền phải:

✔ Kiểm tra đăng nhập

✔ Kiểm tra OTP

✔ Ghi log

✔ Ghi lịch sử

Sau khi chuyển:

✔ Gửi Email

✔ Gửi SMS

Nếu sửa trực tiếp:

```text-x-trilium-auto
def transfer_money():

    check_login()

    check_otp()

    save_log()

    print("Chuyển tiền")

    send_email()

    send_sms()
```

Hàm ngày càng dài.

Decorator giúp tách các chức năng này ra.

---

# 3. Ôn lại First-class Function

Python cho phép:

```text-x-trilium-auto
def hello():
    print("Hello")

x = hello

x()
```

Hàm là một object.

Có thể:

- Gán cho biến
- Truyền vào hàm
- Trả về từ hàm khác

Decorator dựa trên chính khả năng này.

---

# 4. Ôn lại Closure

Ví dụ:

```text-x-trilium-auto
def outer():

    def inner():
        print("Hello")

    return inner

f = outer()

f()
```

Decorator thực chất chính là:

> **Closure + Function**

---

# 5. Decorator đầu tiên

```text-x-trilium-auto
def decorator(func):

    def wrapper():
        print("Trước")

        func()

        print("Sau")

    return wrapper
```

Hàm cần trang trí:

```text-x-trilium-auto
def hello():
    print("Hello")
```

Áp dụng:

```text-x-trilium-auto
hello = decorator(hello)

hello()
```

Kết quả:

```text-x-trilium-auto
Trước

Hello

Sau
```

---

# 6. Giải thích từng bước

Ban đầu:

```text-x-trilium-auto
hello

↓

Function
```

Sau khi:

```text-x-trilium-auto
hello = decorator(hello)
```

Python tạo:

```text-x-trilium-auto
wrapper

↓

gọi hello()

↓

trả về wrapper
```

Bây giờ:

```text-x-trilium-auto
hello

↓

wrapper
```

không còn trỏ tới hàm cũ nữa.

---

# 7. Cú pháp @

Python cho phép viết ngắn hơn.

Thay vì:

```text-x-trilium-auto
hello = decorator(hello)
```

viết:

```text-x-trilium-auto
@decorator
def hello():
    print("Hello")
```

Hai cách hoàn toàn giống nhau.

---

# 8. Decorator có tham số

Ví dụ:

```text-x-trilium-auto
def greet(name):
    print(name)
```

Decorator:

```text-x-trilium-auto
def decorator(func):

    def wrapper(name):

        print("Start")

        func(name)

        print("End")

    return wrapper
```

Sử dụng:

```text-x-trilium-auto
@decorator
def greet(name):
    print(name)

greet("Python")
```

---

# 9. Vấn đề

Nếu hàm có:

```text-x-trilium-auto
def add(a, b):
```

hoặc:

```text-x-trilium-auto
def login(username, password):
```

thì sao?

Decorator không biết có bao nhiêu tham số.

Giải pháp:

# *args

# **kwargs

---

# 10. Decorator tổng quát

```text-x-trilium-auto
def decorator(func):

    def wrapper(*args, **kwargs):

        print("Start")

        result = func(*args, **kwargs)

        print("End")

        return result

    return wrapper
```

Đây là mẫu Decorator chuẩn.

Có thể áp dụng cho mọi hàm.

---

# 11. Ví dụ

```text-x-trilium-auto
@decorator
def add(a, b):
    return a + b

print(add(10,20))
```

Kết quả

```text-x-trilium-auto
Start

End

30
```

---

# 12. Tại sao phải return?

Sai

```text-x-trilium-auto
def wrapper(*args, **kwargs):

    func(*args, **kwargs)
```

Nếu:

```text-x-trilium-auto
result = add(10,20)
```

thì:

```text-x-trilium-auto
result

↓

None
```

Đúng:

```text-x-trilium-auto
result = func(*args, **kwargs)

return result
```

---

# 13. functools.wraps

Ví dụ:

```text-x-trilium-auto
@decorator
def hello():
    """Hello Function"""
```

In:

```text-x-trilium-auto
print(hello.__name__)
```

Kết quả:

```text-x-trilium-auto
wrapper
```

Không phải:

```text-x-trilium-auto
hello
```

Docstring cũng mất.

---

Giải pháp

```text-x-trilium-auto
from functools import wraps
```

```text-x-trilium-auto
from functools import wraps

def decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        return func(*args, **kwargs)

    return wrapper
```

Bây giờ:

```text-x-trilium-auto
print(hello.__name__)
```

Kết quả

```text-x-trilium-auto
hello
```

Đây là cách viết chuẩn trong mọi dự án Python.

---

# 14. Ví dụ: Logger

```text-x-trilium-auto
from functools import wraps

def logger(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        print(f"Đang gọi {func.__name__}")

        result = func(*args, **kwargs)

        print("Hoàn thành")

        return result

    return wrapper
```

Sử dụng

```text-x-trilium-auto
@logger
def login():
    print("Đăng nhập")
```

Kết quả

```text-x-trilium-auto
Đang gọi login

Đăng nhập

Hoàn thành
```

---

# 15. Ví dụ: Đo thời gian

```text-x-trilium-auto
import time
from functools import wraps

def timer(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()

        print(end - start)

        return result

    return wrapper
```

---

Ví dụ

```text-x-trilium-auto
@timer
def download():

    time.sleep(2)
```

Kết quả

```text-x-trilium-auto
2.001
```

Ứng dụng:

- Benchmark
- AI
- Database
- API

---

# 16. Ví dụ: Kiểm tra quyền

```text-x-trilium-auto
is_admin = False

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not is_admin:

            print("Không có quyền")

            return

        return func(*args, **kwargs)

    return wrapper
```

---

# 17. Ví dụ: Retry

```text-x-trilium-auto
import time

def retry(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        for _ in range(3):

            try:
                return func(*args, **kwargs)

            except Exception:

                time.sleep(1)

        raise RuntimeError()

    return wrapper
```

Ứng dụng:

- API
- Database
- Network

---

# 18. Decorator nhiều lớp

```text-x-trilium-auto
@logger

@timer

def work():
    ...
```

Python thực hiện:

```text-x-trilium-auto
timer

↓

logger

↓

work
```

Thứ tự của Decorator rất quan trọng vì mỗi Decorator sẽ bọc kết quả của Decorator phía dưới nó.

---

# 19. Những lỗi phổ biến

## Lỗi 1

Quên return

```text-x-trilium-auto
func()
```

Đúng

```text-x-trilium-auto
return func()
```

---

## Lỗi 2

Không dùng wraps

Khi debug:

```text-x-trilium-auto
__name__
```

bị sai.

---

## Lỗi 3

Decorator không hỗ trợ tham số

Sai

```text-x-trilium-auto
def wrapper():
```

Đúng

```text-x-trilium-auto
def wrapper(*args, **kwargs):
```

Đây là mẫu nên ưu tiên nếu muốn Decorator có thể tái sử dụng cho nhiều hàm.

---

# 20. Ví dụ thực tế

## Log API

```text-x-trilium-auto
@logger
def get_users():
    ...
```

---

## Đo tốc độ AI

```text-x-trilium-auto
@timer
def predict():
    ...
```

---

## Kiểm tra đăng nhập

```text-x-trilium-auto
@login_required
def profile():
    ...
```

---

## Kiểm tra quyền

```text-x-trilium-auto
@admin_required
def delete_user():
    ...
```

Đây là những mẫu Decorator bạn sẽ gặp rất nhiều khi làm việc với Flask, FastAPI và Django.

---

# 21. Bài tập thực hành

## Bài 1

Viết Decorator:

```text-x-trilium-auto
@logger
```

In:

```text-x-trilium-auto
Start

...

End
```

---

## Bài 2

Viết Decorator:

```text-x-trilium-auto
@timer
```

Đo thời gian chạy của hàm.

---

## Bài 3

Viết Decorator:

```text-x-trilium-auto
@uppercase
```

Nếu hàm trả về chuỗi:

```text-x-trilium-auto
hello
```

thì Decorator trả về:

```text-x-trilium-auto
HELLO
```

---

## Bài 4

Viết Decorator:

```text-x-trilium-auto
@repeat
```

Cho hàm chạy 3 lần.

---

## Bài 5

Viết Decorator:

```text-x-trilium-auto
@require_positive
```

Nếu đối số đầu tiên nhỏ hơn 0 thì báo lỗi và không gọi hàm.

---

## Bài 6

Viết Decorator:

```text-x-trilium-auto
@logger
@timer
```

Áp dụng đồng thời cho một hàm và quan sát thứ tự thực thi.

---

# Mini Project: Hệ thống ghi log cho ứng dụng

Xây dựng một hệ thống log bằng Decorator.

Yêu cầu:

- Viết `@logger` để ghi tên hàm và thời điểm gọi.
- Viết `@timer` để đo thời gian thực thi.
- Áp dụng cho các hàm như:
  - `login()`
  - `logout()`
  - `calculate_salary()`
  - `read_file()`
- Sử dụng `functools.wraps` để giữ nguyên metadata của hàm.

> **Thử thách nâng cao:** Ghi log ra tệp văn bản thay vì chỉ in ra màn hình.

---

# Tổng kết buổi 12

Bạn đã học:

- ✅ Decorator là gì.
- ✅ Mối liên hệ giữa Function, Closure và Decorator.
- ✅ Tự xây dựng Decorator.
- ✅ Cú pháp `@`.
- ✅ Decorator tổng quát với `*args` và `**kwargs`.
- ✅ `functools.wraps`.
- ✅ Logger Decorator.
- ✅ Timer Decorator.
- ✅ Decorator kiểm tra quyền.
- ✅ Decorator Retry.
- ✅ Nhiều Decorator lồng nhau.

---

# Góc lập trình viên chuyên nghiệp

Decorator là một trong những đặc trưng nổi bật của Python và được sử dụng rất rộng rãi trong các framework hiện đại:

- **Flask** dùng `@app.route` để đăng ký URL với hàm xử lý.
- **FastAPI** dùng `@app.get`, `@app.post`,... để khai báo API.
- **Django** có các Decorator như `@login_required` để kiểm tra đăng nhập.
- Thư viện chuẩn Python cung cấp các Decorator quan trọng như `@property`, `@staticmethod`, `@classmethod`, `@lru_cache`.

Điểm chung của chúng là **thêm hành vi mới mà không cần sửa mã nguồn của hàm gốc**, giúp mã nguồn dễ mở rộng và tuân theo nguyên tắc **Open/Closed Principle** trong thiết kế phần mềm.

---

# Chuẩn bị cho Buổi 13

Ở **Buổi 13**, chúng ta sẽ học **Decorator nâng cao**:

- Decorator có tham số (Decorator Factory).
- Decorator cho Class.
- Decorator bất đồng bộ (`async def`).
- Các Decorator tích hợp: `@property`, `@staticmethod`, `@classmethod`.
- `functools.lru_cache`.
- Tự xây dựng hệ thống phân quyền và cache bằng Decorator.

Sau buổi này, bạn sẽ có đủ nền tảng để đọc và hiểu mã nguồn của các framework Python hiện đại cũng như tự thiết kế các Decorator phục vụ dự án của mình.
