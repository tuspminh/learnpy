# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 13: Decorator Nâng cao - Decorator Factory, Class Decorator, Async Decorator và các Decorator tích hợp

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Thành thạo Decorator có tham số (Decorator Factory).
> - Hiểu Decorator áp dụng cho Class.
> - Biết cách viết Decorator cho `async def`.
> - Thành thạo các Decorator tích hợp: `@property`, `@staticmethod`, `@classmethod`.
> - Biết sử dụng `functools.lru_cache`.
> - Xây dựng các Decorator thực tế cho logging, phân quyền và cache.

---

# 1. Ôn tập

Buổi trước, chúng ta đã viết:

```text-x-trilium-auto
from functools import wraps

def logger(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Start")
        result = func(*args, **kwargs)
        print("End")
        return result

    return wrapper
```

Sử dụng:

```text-x-trilium-auto
@logger
def hello():
    print("Hello")
```

Thực chất Python sẽ chuyển thành:

```text-x-trilium-auto
hello = logger(hello)
```

---

# 2. Decorator có tham số (Decorator Factory)

Giả sử muốn:

```text-x-trilium-auto
@repeat(3)
def hello():
    print("Hello")
```

Kết quả:

```text-x-trilium-auto
Hello
Hello
Hello
```

Decorator thông thường không làm được điều này.

---

## Cấu trúc

Decorator Factory gồm **3 lớp hàm**:

```text-x-trilium-auto
repeat(3)
        ↓
 decorator(func)
        ↓
 wrapper()
```

---

## Ví dụ hoàn chỉnh

```text-x-trilium-auto
from functools import wraps

def repeat(times):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            result = None

            for _ in range(times):
                result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
```

Sử dụng:

```text-x-trilium-auto
@repeat(3)
def hello():
    print("Hello")

hello()
```

Kết quả:

```text-x-trilium-auto
Hello
Hello
Hello
```

---

# 3. Decorator kiểm tra quyền

```text-x-trilium-auto
from functools import wraps

current_role = "user"

def require_role(role):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if current_role != role:
                print("Không có quyền.")
                return

            return func(*args, **kwargs)

        return wrapper

    return decorator
```

Áp dụng:

```text-x-trilium-auto
@require_role("admin")
def delete_user():
    print("Đã xóa người dùng")
```

Nếu:

```text-x-trilium-auto
current_role = "user"
```

Kết quả:

```text-x-trilium-auto
Không có quyền.
```

---

# 4. Decorator ghi log theo mức độ

```text-x-trilium-auto
def log(level):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            print(f"[{level}] Đang chạy {func.__name__}")

            return func(*args, **kwargs)

        return wrapper

    return decorator
```

Sử dụng:

```text-x-trilium-auto
@log("INFO")
def login():
    print("Login")
```

Kết quả:

```text-x-trilium-auto
[INFO] Đang chạy login
Login
```

---

# 5. Class Decorator

Decorator không chỉ áp dụng cho hàm.

Có thể áp dụng cho Class.

Ví dụ:

```text-x-trilium-auto
def add_version(cls):

    cls.version = "1.0"

    return cls
```

Áp dụng:

```text-x-trilium-auto
@add_version
class App:
    pass

print(App.version)
```

Kết quả:

```text-x-trilium-auto
1.0
```

---

## Ví dụ khác

```text-x-trilium-auto
def author(name):

    def decorator(cls):

        cls.author = name

        return cls

    return decorator
```

Sử dụng:

```text-x-trilium-auto
@author("Garden Dau")
class Project:
    pass

print(Project.author)
```

---

# 6. Async Decorator

Trong các ứng dụng hiện đại như FastAPI, AsyncIO, aiohttp..., chúng ta thường cần Decorator cho hàm bất đồng bộ.

Sai:

```text-x-trilium-auto
def decorator(func):

    def wrapper():
        func()
```

Nếu:

```text-x-trilium-auto
async def hello():
    ...
```

Sẽ không hoạt động đúng.

---

## Cách đúng

```text-x-trilium-auto
from functools import wraps

def logger(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):

        print("Start")

        result = await func(*args, **kwargs)

        print("End")

        return result

    return wrapper
```

Sử dụng:

```text-x-trilium-auto
@logger
async def fetch_data():
    ...
```

Điểm khác biệt là `wrapper` cũng phải là `async def` và dùng `await` khi gọi hàm gốc.

---

# 7. `@property`

Đây là Decorator tích hợp cực kỳ quan trọng.

Không dùng:

```text-x-trilium-auto
class Student:

    def get_name(self):
        return self._name
```

Phải gọi:

```text-x-trilium-auto
student.get_name()
```

---

Dùng `@property`:

```text-x-trilium-auto
class Student:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
```

Bây giờ:

```text-x-trilium-auto
student = Student("An")

print(student.name)
```

Không cần:

```text-x-trilium-auto
student.get_name()
```

Đây là cách viết rất phổ biến trong Python hiện đại.

---

# 8. Property Setter

Có thể kiểm tra dữ liệu trước khi gán.

```text-x-trilium-auto
class Student:

    def __init__(self):
        self._age = 0

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):

        if value < 0:
            raise ValueError("Tuổi không hợp lệ.")

        self._age = value
```

Sử dụng:

```text-x-trilium-auto
student = Student()

student.age = 20

print(student.age)
```

---

# 9. `@staticmethod`

Ví dụ:

```text-x-trilium-auto
class Math:

    @staticmethod
    def add(a, b):
        return a + b
```

Gọi:

```text-x-trilium-auto
Math.add(10, 20)
```

Không cần tạo đối tượng.

Dùng khi hàm **không sử dụng** `self` hoặc `cls`.

---

# 10. `@classmethod`

```text-x-trilium-auto
class Student:

    total = 0

    @classmethod
    def increase(cls):

        cls.total += 1
```

Sử dụng:

```text-x-trilium-auto
Student.increase()

print(Student.total)
```

`cls` là chính lớp (class), không phải đối tượng.

---

# 11. So sánh

| Decorator | Đối tượng đầu tiên | Dùng khi |
| --- | --- | --- |
| Hàm thường | `self` | Làm việc với đối tượng |
| `@classmethod` | `cls` | Làm việc với lớp |
| `@staticmethod` | Không có | Hàm tiện ích |

---

# 12. `functools.lru_cache`

Đây là Decorator giúp cache kết quả.

Ví dụ:

```text-x-trilium-auto
from functools import lru_cache

@lru_cache
def fibonacci(n):

    if n <= 1:
        return n

    return fibonacci(n-1) + fibonacci(n-2)
```

Gọi:

```text-x-trilium-auto
print(fibonacci(40))
```

Không có cache:

- Rất chậm.

Có cache:

- Nhanh hơn rất nhiều.

---

# 13. Ứng dụng thực tế

### API

```text-x-trilium-auto
@app.get("/users")
```

### Flask

```text-x-trilium-auto
@app.route("/")
```

### Django

```text-x-trilium-auto
@login_required
```

### Cache

```text-x-trilium-auto
@lru_cache
```

### ORM

```text-x-trilium-auto
@property
```

Decorator xuất hiện ở hầu hết các framework Python hiện đại.

---

# 14. Decorator chồng nhiều lớp

```text-x-trilium-auto
@logger
@timer
@retry
def download():
    ...
```

Python sẽ thực hiện theo thứ tự:

```text-x-trilium-auto
download
   ↓
retry
   ↓
timer
   ↓
logger
```

Mỗi Decorator nhận về hàm đã được Decorator phía dưới bọc lại.

---

# 15. Những lỗi phổ biến

## Lỗi 1

Quên `await`

Sai:

```text-x-trilium-auto
result = func()
```

Đúng:

```text-x-trilium-auto
result = await func()
```

trong Async Decorator.

---

## Lỗi 2

Quên `@wraps`

Dẫn đến:

```text-x-trilium-auto
__name__

__doc__
```

bị thay đổi thành của `wrapper`.

---

## Lỗi 3

Nhầm `staticmethod` và `classmethod`

Quy tắc:

- Cần truy cập hoặc thay đổi biến của lớp → `@classmethod`.
- Chỉ là hàm tiện ích, không cần `self` hay `cls` → `@staticmethod`.

---

# 16. Ví dụ thực tế

## Cache kết quả tính toán

```text-x-trilium-auto
@lru_cache
def factorial(n):
    ...
```

---

## Kiểm tra đăng nhập

```text-x-trilium-auto
@login_required
def dashboard():
    ...
```

---

## Kiểm tra vai trò

```text-x-trilium-auto
@require_role("admin")
def delete():
    ...
```

---

## Đo thời gian

```text-x-trilium-auto
@timer
def train_ai():
    ...
```

---

# 17. Bài tập thực hành

### Bài 1

Viết:

```text-x-trilium-auto
@repeat(5)
```

để chạy hàm 5 lần.

---

### Bài 2

Viết:

```text-x-trilium-auto
@require_role("manager")
```

kiểm tra quyền truy cập.

---

### Bài 3

Tạo `@property` cho thuộc tính:

```text-x-trilium-auto
balance
```

không cho phép số âm.

---

### Bài 4

Tạo:

```text-x-trilium-auto
class Calculator
```

với:

```text-x-trilium-auto
@staticmethod
```

để tính tổng, hiệu, tích, thương.

---

### Bài 5

Tạo:

```text-x-trilium-auto
class Employee
```

dùng:

```text-x-trilium-auto
@classmethod
```

để đếm số lượng nhân viên đã tạo.

---

### Bài 6

Dùng:

```text-x-trilium-auto
@lru_cache
```

để tối ưu hàm Fibonacci và so sánh tốc độ với phiên bản không dùng cache.

---

# Mini Project: Hệ thống API giả lập

Xây dựng một ứng dụng nhỏ với các yêu cầu:

1. Decorator `@logger(level)` ghi log mức INFO/ERROR.
2. Decorator `@timer` đo thời gian xử lý.
3. Decorator `@require_role(role)` kiểm tra quyền truy cập.
4. Dùng `@property` để quản lý thuộc tính `balance` của tài khoản.
5. Dùng `@classmethod` để đếm tổng số tài khoản.
6. Dùng `@staticmethod` cho các phép tính phí giao dịch.

---

# Tổng kết buổi 13

Bạn đã học:

- ✅ Decorator Factory (Decorator có tham số).
- ✅ Class Decorator.
- ✅ Async Decorator.
- ✅ `@property`.
- ✅ `@property.setter`.
- ✅ `@staticmethod`.
- ✅ `@classmethod`.
- ✅ `functools.lru_cache`.
- ✅ Decorator trong các framework hiện đại.
- ✅ Những lỗi phổ biến và cách tránh.

---

# Góc lập trình viên chuyên nghiệp

Nếu bạn mở mã nguồn của **FastAPI**, **Flask**, **Django**, **Typer**, **Click**, hay thậm chí nhiều thư viện AI và Machine Learning, bạn sẽ thấy Decorator xuất hiện ở khắp nơi.

Điều quan trọng không chỉ là biết **cách dùng** Decorator, mà còn hiểu:

- Vì sao cần `*args` và `**kwargs`.
- Khi nào nên dùng Decorator Factory.
- Khi nào nên dùng `@property`, `@classmethod`, `@staticmethod`.
- Cách bảo toàn metadata bằng `@wraps`.
- Cách viết Decorator tương thích với cả hàm đồng bộ và bất đồng bộ.

Nắm vững những kiến thức này sẽ giúp bạn đọc mã nguồn của các thư viện lớn và tự xây dựng các công cụ tái sử dụng cho dự án của mình.

## Chuẩn bị cho Buổi 14

Ở **Buổi 14**, chúng ta sẽ chuyển sang một chủ đề rất quan trọng trước khi học OOP chuyên sâu:

# **Iterator, Iterable, Generator và** `**yield**`

Đây là nền tảng của:

- `for` hoạt động như thế nào.
- `range()`.
- `enumerate()`.
- `zip()`.
- Đọc file theo dòng.
- Xử lý dữ liệu lớn.
- Streaming dữ liệu.
- `async for` và lập trình bất đồng bộ.

Sau buổi này, bạn sẽ hiểu cách Python xử lý dữ liệu theo từng phần thay vì tải toàn bộ vào bộ nhớ, một kỹ năng rất quan trọng khi làm việc với dữ liệu lớn, web scraping, AI và các hệ thống hiệu năng cao.
