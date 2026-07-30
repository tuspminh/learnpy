Chào bạn! Bạn đã vượt qua Bài 7 với những bài tập OOP nâng cao - tuyệt vời! Bây giờ chúng ta bước vào một chủ đề **CỰC KỲ THÚ VỊ** và **RẤT PYTHONIC**: **Decorator và Closure**. Đây là thứ sẽ làm code của bạn trở nên thanh lịch và mạnh mẽ hơn rất nhiều!

---

# 📘 BÀI 8: DECORATOR VÀ CLOSURE

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu **Closure** là gì và tại sao nó quan trọng
- Tạo và sử dụng **Decorator** để "trang trí" hàm
- Viết decorator với tham số (parameterized decorator)
- Sử dụng `functools.wraps` để giữ metadata
- Áp dụng decorator vào thực tế: logging, timing, validation
- Hiểu sâu về **higher-order functions**

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Higher-Order Functions (Hàm bậc cao)

**Hàm bậc cao = Hàm có thể:**
1. Nhận hàm khác làm tham số
2. Trả về một hàm

```python
# 1. Nhận hàm làm tham số
def ap_dung_ham(func, value):
    """Áp dụng hàm lên giá trị"""
    return func(value)


def binh_phuong(x):
    return x**2


print(ap_dung_ham(binh_phuong, 5))  # 25


# 2. Trả về hàm
def tao_ham_nhan(n):
    """Tạo hàm nhân với n"""

    def ham_nhan(x):
        return x * n

    return ham_nhan


nhan_doi = tao_ham_nhan(2)
nhan_ba = tao_ham_nhan(3)

print(nhan_doi(5))  # 10
print(nhan_ba(5))  # 15
```

---

### 1.2. Closure (Bao đóng) - Trái tim của Decorator

**Closure = Hàm ghi nhớ biến từ phạm vi bao ngoài, ngay cả khi đã thoát khỏi phạm vi đó**

```python
def ngoai_ham(message):
    """Hàm bên ngoài"""

    def trong_ham():
        """Hàm bên trong - closure"""
        print(message)  # Ghi nhớ message từ ngoài

    return trong_ham


# Tạo closure
hello = ngoai_ham("Xin chào!")
goodbye = ngoai_ham("Tạm biệt!")

# Gọi closure - vẫn nhớ message
hello()  # Xin chào!
goodbye()  # Tạm biệt!

# Kiểm tra closure
print(hello.__closure__)  # (<cell at 0x...: str object at 0x...>,)
print(hello.__closure__[0].cell_contents)  # Xin chào!
```

**Ví dụ thực tế với closure:**

```python
# 1. Counter sử dụng closure
def tao_bo_dem():
    """Tạo bộ đếm với closure"""
    count = 0

    def bo_dem():
        nonlocal count  # Khai báo để sửa biến từ phạm vi bao ngoài
        count += 1
        return count

    return bo_dem


# Tạo 2 bộ đếm độc lập
dem1 = tao_bo_dem()
dem2 = tao_bo_dem()

print(dem1())  # 1
print(dem1())  # 2
print(dem1())  # 3
print(dem2())  # 1 (bộ đếm riêng)
print(dem2())  # 2


# 2. Tính trung bình động với closure
def tao_trung_binh_dong():
    """Tính trung bình động của các giá trị"""
    values = []

    def trung_binh(value):
        values.append(value)
        return sum(values) / len(values)

    return trung_binh


avg = tao_trung_binh_dong()
print(avg(10))  # 10.0
print(avg(20))  # 15.0
print(avg(30))  # 20.0
print(avg(40))  # 25.0
```

---

### 1.3. Decorator là gì?

**Decorator = Hàm bậc cao nhận một hàm, "trang trí" thêm chức năng, và trả về hàm mới**

```python
# Cú pháp cơ bản
def my_decorator(func):
    def wrapper():
        print("Trước khi gọi hàm")
        func()  # Gọi hàm gốc
        print("Sau khi gọi hàm")

    return wrapper


@my_decorator
def say_hello():
    print("Hello World!")


# Khi gọi say_hello(), thực tế đang gọi wrapper()
say_hello()
# Trước khi gọi hàm
# Hello World!
# Sau khi gọi hàm
```

**Decorator với tham số:**

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Trước khi gọi hàm")
        result = func(*args, **kwargs)
        print("Sau khi gọi hàm")
        return result

    return wrapper


@my_decorator
def add(a, b):
    return a + b


print(add(3, 5))  # 8 (vẫn in ra log)
```

**Quan trọng:** Cú pháp `@decorator` tương đương với:

```python
# Cách viết này:
@my_decorator
def my_function():
    pass


# Tương đương với:
def my_function():
    pass


my_function = my_decorator(my_function)
```

---

### 1.4. Decorator với tham số (Parameterized Decorator)

```python
def repeat(times):
    """Decorator lặp lại hàm n lần"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def say_hi(name):
    print(f"Hi {name}!")


say_hi("An")
# Hi An!
# Hi An!
# Hi An!
```

---

### 1.5. functools.wraps - Giữ metadata của hàm

**Vấn đề:** Decorator làm mất thông tin của hàm gốc

```python
def simple_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@simple_decorator
def my_function():
    """Đây là hàm của tôi"""
    print("Hello")


print(my_function.__name__)  # wrapper (mất tên)
print(my_function.__doc__)  # None (mất docstring)
```

**Giải pháp: `functools.wraps`**

```python
from functools import wraps


def good_decorator(func):
    @wraps(func)  # Giữ lại metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@good_decorator
def my_good_function():
    """Đây là hàm tốt với decorator"""
    print("Hello")


print(my_good_function.__name__)  # my_good_function (giữ tên)
print(my_good_function.__doc__)  # Đây là hàm tốt với decorator (giữ docstring)
```

---

### 1.6. Decorator lồng nhau (Nested Decorators)

```python
from functools import wraps
import time


def timer(func):
    """Đo thời gian chạy"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__} chạy trong {end - start:.4f}s")
        return result

    return wrapper


def logger(func):
    """Ghi log khi gọi hàm"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"📝 Gọi hàm {func.__name__} với args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"📝 Kết quả: {result}")
        return result

    return wrapper


@timer
@logger
def slow_function(n):
    """Hàm chạy chậm"""
    time.sleep(0.5)
    return n**2


# Áp dụng từ dưới lên: logger → timer
slow_function(5)
# 📝 Gọi hàm slow_function với args=(5,), kwargs={}
# 📝 Kết quả: 25
# ⏱️ slow_function chạy trong 0.5002s
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống Decorator cho Web API

```python
from functools import wraps
import time
import json
from typing import Any, Callable


# 1. Decorator kiểm tra quyền
def require_auth(func):
    """Yêu cầu xác thực trước khi gọi API"""

    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.get("is_authenticated", False):
            return {"error": "Unauthorized"}, 401
        return func(user, *args, **kwargs)

    return wrapper


# 2. Decorator kiểm tra vai trò
def require_role(required_role):
    """Yêu cầu vai trò cụ thể"""

    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.get("role") != required_role:
                return {"error": f"Requires {required_role} role"}, 403
            return func(user, *args, **kwargs)

        return wrapper

    return decorator


# 3. Decorator validate input
def validate_input(schema):
    """Validate dữ liệu đầu vào theo schema"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Giả lập validate
            print(f"✅ Validating input with schema: {schema}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# 4. Decorator cache
def cache(timeout=60):
    """Cache kết quả của hàm"""

    def decorator(func):
        cache_data = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo key từ args
            key = str(args) + str(kwargs)

            # Kiểm tra cache
            if key in cache_data:
                value, timestamp = cache_data[key]
                if time.time() - timestamp < timeout:
                    print(f"💾 Cache hit for {func.__name__}")
                    return value

            # Gọi hàm và lưu cache
            result = func(*args, **kwargs)
            cache_data[key] = (result, time.time())
            print(f"💾 Cache miss for {func.__name__}")
            return result

        # Thêm method để xóa cache
        wrapper.clear_cache = cache_data.clear
        return wrapper

    return decorator


# 5. Decorator retry
def retry(max_attempts=3, delay=1):
    """Thử lại khi hàm gặp lỗi"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            raise last_error

        return wrapper

    return decorator


# 6. Decorator logging chi tiết
def api_logger(func):
    """Log chi tiết API call"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("\n" + "=" * 50)
        print(f"🚀 API CALL: {func.__name__}")
        print(f"📦 Args: {args}")
        print(f"📦 Kwargs: {kwargs}")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            print(f"✅ Success in {elapsed:.3f}s")
            print(f"📤 Result: {result}")
            print("=" * 50)
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed in {elapsed:.3f}s")
            print(f"💥 Error: {e}")
            print("=" * 50)
            raise

    return wrapper


# SỬ DỤNG
class User:
    def __init__(self, name, role="user", authenticated=False):
        self.name = name
        self.role = role
        self.is_authenticated = authenticated

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "is_authenticated": self.is_authenticated,
        }


@api_logger
@cache(timeout=30)
def get_user_data(user_id):
    """Lấy dữ liệu user từ database (giả lập)"""
    time.sleep(0.5)  # Giả lập truy vấn chậm
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
    }


@api_logger
@require_auth
@require_role("admin")
def delete_user(admin_user, user_id):
    """Xóa user (yêu cầu admin)"""
    return {"status": "deleted", "user_id": user_id}


@api_logger
@retry(max_attempts=3)
@validate_input({"name": str, "age": int})
def create_user(user_data):
    """Tạo user mới với retry và validate"""
    # Giả lập lỗi ngẫu nhiên
    if user_data.get("age") < 0:
        raise ValueError("Age must be positive")
    if user_data.get("age") > 150:
        raise ValueError("Age too high")

    return {"status": "created", "user": user_data}


# Test
print("\n=== TEST CACHE ===")
get_user_data(1)
get_user_data(1)  # Cache hit
get_user_data(2)

print("\n=== TEST AUTH ===")
admin = User("Admin", "admin", True)
user = User("User", "user", True)
guest = User("Guest", "guest", False)

print(delete_user(admin.to_dict(), 5))  # Success
# print(delete_user(user.to_dict(), 5))  # Forbidden
# print(delete_user(guest.to_dict(), 5)) # Unauthorized

print("\n=== TEST RETRY ===")
print(create_user({"name": "John", "age": 30}))
# print(create_user({"name": "Invalid", "age": -10}))  # ValueError
```

---

### Ví dụ 2: Decorator cho Performance và Debugging

```python
from functools import wraps
import time
import tracemalloc
from typing import Any, Callable


def performance_logger(func):
    """Log hiệu suất: thời gian và bộ nhớ"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Đo bộ nhớ
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]

        # Đo thời gian
        start_time = time.perf_counter()

        # Gọi hàm
        result = func(*args, **kwargs)

        # Kết thúc đo
        end_time = time.perf_counter()
        end_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # Log kết quả
        print(f"\n📊 PERFORMANCE: {func.__name__}")
        print(f"   ⏱️  Time: {end_time - start_time:.6f}s")
        print(f"   💾 Memory: {(end_memory - start_memory) / 1024:.2f} KB")

        return result

    return wrapper


def debug(func):
    """Debug function: in ra input và output"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n🔍 DEBUG: {func.__name__}")
        print(f"   📥 args: {args}")
        print(f"   📥 kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"   📤 result: {result}")
        return result

    return wrapper


def deprecated(message=None):
    """Đánh dấu hàm đã deprecated"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warn_msg = message or f"{func.__name__} is deprecated!"
            print(f"⚠️ WARNING: {warn_msg}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# SỬ DỤNG
@performance_logger
def fibonacci_recursive(n):
    """Fibonacci đệ quy (chậm)"""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


@debug
@performance_logger
def fibonacci_with_cache(n, cache={}):
    """Fibonacci với cache (nhanh)"""
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = fibonacci_with_cache(n - 1) + fibonacci_with_cache(n - 2)
    return cache[n]


@deprecated("Use fibonacci_with_cache instead")
def old_fibonacci(n):
    """Hàm cũ, không nên dùng"""
    return fibonacci_recursive(n)


# Test
print("\n=== FIBONACCI ===")
fibonacci_recursive(30)  # Chậm
fibonacci_with_cache(40)  # Nhanh
old_fibonacci(10)  # Warning

# Cache re-use
print("\n=== CACHE RE-USE ===")
fibonacci_with_cache(41)  # Nhanh hơn nhiều
```

---

### Ví dụ 3: Decorator cho Validation và Type Checking

```python
from functools import wraps
from typing import Any, Callable, get_type_hints


def type_check(func):
    """Kiểm tra kiểu dữ liệu đầu vào dựa trên type hints"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Lấy type hints
        hints = get_type_hints(func)

        # Kiểm tra args
        for i, (arg_name, arg_type) in enumerate(hints.items()):
            if arg_name == "return":
                continue
            if i < len(args):
                value = args[i]
                if not isinstance(value, arg_type):
                    raise TypeError(
                        f"Argument '{arg_name}' must be {arg_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

        # Kiểm tra kwargs
        for arg_name, value in kwargs.items():
            if arg_name in hints and hints[arg_name] != "return":
                if not isinstance(value, hints[arg_name]):
                    raise TypeError(
                        f"Argument '{arg_name}' must be {hints[arg_name].__name__}, "
                        f"got {type(value).__name__}"
                    )

        return func(*args, **kwargs)

    return wrapper


def validate_range(min_val=None, max_val=None):
    """Validate giá trị trong khoảng"""

    def decorator(func):
        @wraps(func)
        def wrapper(value, *args, **kwargs):
            if min_val is not None and value < min_val:
                raise ValueError(f"Value {value} must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Value {value} must be <= {max_val}")
            return func(value, *args, **kwargs)

        return wrapper

    return decorator


def validate_not_empty(func):
    """Validate chuỗi/collection không rỗng"""

    @wraps(func)
    def wrapper(value, *args, **kwargs):
        if not value:
            raise ValueError(f"Value cannot be empty")
        return func(value, *args, **kwargs)

    return wrapper


# SỬ DỤNG
@type_check
def process_data(name: str, age: int, score: float):
    return f"Name: {name}, Age: {age}, Score: {score}"


@validate_range(min_val=0, max_val=100)
def set_score(score):
    return f"Score set to {score}"


@validate_not_empty
def set_username(username):
    return f"Username: {username}"


# Test
print(process_data("John", 25, 95.5))
# print(process_data("John", "25", 95.5))  # TypeError

print(set_score(85))
# print(set_score(105))  # ValueError

print(set_username("john_doe"))
# print(set_username(""))  # ValueError
```

---

### Ví dụ 4: Class Decorator

```python
from functools import wraps


# 1. Decorator cho method trong class
def log_method_call(func):
    """Log khi method được gọi"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"🔵 Calling {func.__name__} on {self.__class__.__name__}")
        return func(self, *args, **kwargs)

    return wrapper


def singleton(cls):
    """Decorator tạo Singleton pattern"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def add_method(cls):
    """Thêm method vào class"""

    def new_method(self):
        return f"This is a new method added to {self.__class__.__name__}"

    cls.new_method = new_method
    return cls


# SỬ DỤNG
@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        print(f"Creating connection to {url}")

    @log_method_call
    def query(self, sql):
        return f"Executing: {sql}"

    @log_method_call
    def close(self):
        return "Connection closed"


@add_method
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, I'm {self.name}"


# Test
print("\n=== SINGLETON ===")
db1 = DatabaseConnection("localhost")
db2 = DatabaseConnection("localhost")
print(f"Same object? {db1 is db2}")  # True

print("\n=== METHOD DECORATOR ===")
print(db1.query("SELECT * FROM users"))
print(db1.close())

print("\n=== ADD METHOD ===")
user = User("John")
print(user.greet())
print(user.new_method())
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết decorator `timer` đo thời gian chạy của hàm. In ra tên hàm và thời gian.

**Bài 2:** Viết decorator `logger` in ra tên hàm, tham số và kết quả khi gọi.

**Bài 3:** Viết decorator `retry` thử lại hàm 3 lần nếu có lỗi.

**Bài 4:** Viết decorator `validate_type` kiểm tra kiểu dữ liệu của tham số.

**Bài 5:** Viết decorator `memoize` cache kết quả của hàm dựa trên tham số.

**Bài 6:** Viết closure `counter` đếm số lần hàm được gọi.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Viết decorator `require_permission` kiểm tra quyền trước khi gọi hàm.

**Bài 8:** Viết decorator `rate_limit` giới hạn số lần gọi hàm trong 1 khoảng thời gian.

**Bài 9:** Viết decorator `retry_with_backoff` thử lại với exponential backoff.

**Bài 10:** Tạo hệ thống plugin sử dụng decorator để đăng ký hàm.

---

## 🏗️ MINI-PROJECT: HỆ THỐNG API WITH DECORATORS

```python
"""
Xây dựng hệ thống API đơn giản với nhiều decorator:

1. DECORATORS:
   - @route(path) - Đăng ký API endpoint
   - @method(http_method) - GET, POST, PUT, DELETE
   - @require_auth - Yêu cầu xác thực
   - @rate_limit(requests, per_seconds) - Giới hạn request
   - @validate(schema) - Validate input
   - @response(status_code) - Định nghĩa status code

2. API FRAMEWORK:
   - Class API nhận và xử lý request
   - Đăng ký routes từ decorator
   - Xử lý request và response

3. USE CASE:
   - Tạo 5-7 APIs với các decorator khác nhau
   - Test với các request
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE DECORATOR CHUYÊN NGHIỆP

- [ ] Sử dụng `@wraps` từ `functools` để giữ metadata
- [ ] Decorator hoạt động với `*args` và `**kwargs`
- [ ] Decorator lồng nhau hoạt động đúng thứ tự
- [ ] Closure được sử dụng đúng cách
- [ ] Kiểm tra `__name__` và `__doc__` của hàm được giữ
- [ ] Decorator với tham số (parameterized) hoạt động

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Viết decorator có thể được gọi cả có và không có tham số
# Ví dụ:
@double
def func1(x):
    return x * 10


@double(3)
def func2(x):
    return x * 10


# Cả 2 đều hoạt động!
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Cú pháp | Ứng dụng |
|-----------|---------|----------|
| **Closure** | Hàm ghi nhớ biến từ phạm vi bao ngoài | Counter, caching, stateful function |
| **Higher-order function** | `def outer(): def inner(): return inner` | Tạo hàm, decorator |
| **Decorator** | `@decorator def func():` | Log, timing, auth, validation |
| **Parameterized decorator** | `@decorator(arg)` | Cấu hình linh hoạt |
| **@wraps** | `@wraps(func)` | Giữ metadata của hàm |
| **Nested decorator** | `@dec1 @dec2 def func():` | Kết hợp nhiều chức năng |

---

**Chúc mừng bạn đã hoàn thành Bài 8! Decorator là một trong những tính năng Pythonic nhất của Python.** 💪

*Bài 9 sẽ dạy bạn về Module và Package - cách tổ chức code trong dự án lớn!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀