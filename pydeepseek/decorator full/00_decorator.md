Xin chào! Tôi sẽ hướng dẫn bạn về Decorator trong Python ở mức độ **Deep Dive**, từ cơ bản đến nâng cao, với các ví dụ thực tế.

## Mục lục
1. [Cơ bản về Decorator](#1-cơ-bản-về-decorator)
2. [Decorator với tham số](#2-decorator-với-tham-số)
3. [Nested Decorator](#3-nested-decorator)
4. [Class-based Decorator](#4-class-based-decorator)
5. [Decorator với arguments linh hoạt](#5-decorator-với-arguments-linh-hoạt)
6. [Functools.wraps - Bảo toàn metadata](#6-functoolswraps---bảo-toàn-metadata)
7. [Decorator nâng cao - Stateful Decorator](#7-decorator-nâng-cao---stateful-decorator)
8. [Decorator cho phương thức (Method Decorator)](#8-decorator-cho-phương-thức-method-decorator)
9. [Decorator với tham số động](#9-decorator-với-tham-số-động)
10. [Thực hành - Xây dựng hệ thống caching](#10-thực-hành---xây-dựng-hệ-thống-caching)

---

## 1. Cơ bản về Decorator

Decorator là một function nhận vào một function và trả về một function đã được "trang trí" thêm tính năng.

### Ví dụ cơ bản nhất:

```python
# Decorator đơn giản
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Đang gọi hàm: {func.__name__}")
        print(f"Arguments: {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"Kết quả: {result}")
        return result
    return wrapper

# Sử dụng decorator
@logger
def add(a, b):
    return a + b

# Tương đương với: add = logger(add)

add(5, 3)
# Output:
# Đang gọi hàm: add
# Arguments: (5, 3), {}
# Kết quả: 8
```

---

## 2. Decorator với tham số

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hello(name):
    print(f"Hello {name}!")

say_hello("Python")
# Output: Hello Python! (in ra 3 lần)
```

---

## 3. Nested Decorator

```python
def uppercase(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

def exclamation(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result + "!!!"
    return wrapper

@exclamation
@uppercase
def greet(name):
    return f"Hello {name}"

print(greet("World"))  # HELLO WORLD!!!
# Thực hiện từ dưới lên: uppercase trước, exclamation sau
```

---

## 4. Class-based Decorator

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Hàm {self.func.__name__} được gọi lần thứ {self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()  # Hàm say_hi được gọi lần thứ 1
say_hi()  # Hàm say_hi được gọi lần thứ 2
```

---

## 5. Decorator với arguments linh hoạt

```python
import time
from functools import wraps

def timer(unit='seconds'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            elapsed = end - start
            
            if unit == 'milliseconds':
                elapsed *= 1000
                
            print(f"{func.__name__} took {elapsed:.4f} {unit}")
            return result
        return wrapper
    return decorator

@timer(unit='milliseconds')
def slow_function():
    time.sleep(0.1)
    return "Done"

slow_function()  # slow_function took 100.1234 milliseconds
```

---

## 6. Functools.wraps - Bảo toàn metadata

```python
from functools import wraps

def my_decorator(func):
    # KHÔNG dùng wraps
    def wrapper(*args, **kwargs):
        """Wrapper docstring"""
        return func(*args, **kwargs)
    return wrapper

def my_decorator_with_wraps(func):
    @wraps(func)  # Bảo toàn tên, docstring, annotations, ...
    def wrapper(*args, **kwargs):
        """Wrapper docstring"""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def add(a, b):
    """Add two numbers"""
    return a + b

@my_decorator_with_wraps
def multiply(a, b):
    """Multiply two numbers"""
    return a * b

print(add.__name__)      # wrapper (mất tên)
print(add.__doc__)       # Wrapper docstring (mất docstring)

print(multiply.__name__) # multiply (giữ tên)
print(multiply.__doc__)  # Multiply two numbers (giữ docstring)
```

---

## 7. Decorator nâng cao - Stateful Decorator

```python
from functools import wraps

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Xóa các calls cũ hơn period
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) >= self.max_calls:
                raise Exception(f"Rate limit exceeded. Max {self.max_calls} calls per {self.period} seconds")
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

# Sử dụng
@RateLimiter(max_calls=3, period=5)
def api_call(data):
    return f"Processing {data}"

# Gọi nhanh 4 lần - lần thứ 4 sẽ raise exception
```

---

## 8. Decorator cho phương thức (Method Decorator)

```python
from functools import wraps

def require_login(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'is_logged_in') or not self.is_logged_in:
            raise PermissionError("User not logged in")
        return func(self, *args, **kwargs)
    return wrapper

class UserService:
    def __init__(self):
        self.is_logged_in = False
    
    def login(self):
        self.is_logged_in = True
    
    @require_login
    def get_profile(self):
        return {"name": "John", "age": 30}
    
    @require_login
    def update_profile(self, data):
        print(f"Updating profile with {data}")

# Sử dụng
service = UserService()
# service.get_profile()  # Lỗi: User not logged in

service.login()
profile = service.get_profile()  # OK
```

---

## 9. Decorator với tham số động

```python
from functools import wraps
import logging

def log_level(level=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Lấy log level từ context nếu không có
            actual_level = level or getattr(wrapper, '_log_level', 'INFO')
            
            logger = logging.getLogger(func.__module__)
            log_method = getattr(logger, actual_level.lower(), logger.info)
            
            log_method(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            log_method(f"Finished {func.__name__}")
            return result
        return wrapper
    return decorator

@log_level('DEBUG')
def process_data(data):
    return data * 2

# Có thể thay đổi level động
process_data = log_level('ERROR')(process_data.__wrapped__)
```

---

## 10. Thực hành - Xây dựng hệ thống caching

Đây là ví dụ tổng hợp với nhiều kỹ thuật decorator nâng cao:

```python
from functools import wraps, lru_cache
import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable

class AdvancedCache:
    """Hệ thống cache với nhiều tính năng nâng cao"""
    
    def __init__(self, 
                 max_size: Optional[int] = None,
                 ttl: Optional[int] = None,
                 prefix: str = ""):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.prefix = prefix
        self.hits = 0
        self.misses = 0
    
    def _get_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Tạo cache key từ function và arguments"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"{self.prefix}{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _clean_expired(self):
        """Xóa các entries đã hết hạn"""
        now = time.time()
        expired = [k for k, v in self.cache.items() 
                  if v.get('expiry') and v['expiry'] < now]
        for k in expired:
            del self.cache[k]
    
    def _enforce_max_size(self):
        """Đảm bảo cache không vượt quá max_size"""
        if self.max_size and len(self.cache) > self.max_size:
            # Xóa các entry cũ nhất (dựa trên thời gian truy cập)
            sorted_items = sorted(self.cache.items(), 
                                key=lambda x: x[1]['last_access'])
            for key, _ in sorted_items[:len(self.cache) - self.max_size]:
                del self.cache[key]
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo key
            key = self._get_key(func.__name__, args, kwargs)
            
            # Xóa cache hết hạn
            self._clean_expired()
            
            # Kiểm tra cache
            if key in self.cache:
                entry = self.cache[key]
                # Kiểm tra TTL
                if self.ttl and (time.time() - entry['timestamp'] > self.ttl):
                    del self.cache[key]
                else:
                    self.hits += 1
                    entry['last_access'] = time.time()
                    return entry['value']
            
            # Cache miss - gọi hàm
            self.misses += 1
            result = func(*args, **kwargs)
            
            # Lưu vào cache
            self.cache[key] = {
                'value': result,
                'timestamp': time.time(),
                'last_access': time.time(),
                'expiry': time.time() + self.ttl if self.ttl else None
            }
            
            self._enforce_max_size()
            return result
        
        # Thêm các method để thống kê
        wrapper.get_stats = lambda: {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
        
        wrapper.clear_cache = lambda: self.cache.clear()
        
        return wrapper

# Sử dụng ví dụ
@AdvancedCache(max_size=10, ttl=5)
def expensive_computation(x: int) -> int:
    """Hàm tính toán tốn kém"""
    print(f"Computing for {x}...")
    time.sleep(2)  # Giả lập công việc nặng
    return x * x

# Test
print(expensive_computation(5))  # Computing... 25
print(expensive_computation(5))  # Lấy từ cache -> 25
print(expensive_computation(6))  # Computing... 36

# Xem thống kê
print(expensive_computation.get_stats())
# {'hits': 1, 'misses': 2, 'hit_rate': 0.333, 'cache_size': 2}

# Đợi TTL hết
time.sleep(6)
print(expensive_computation(5))  # Computing lại vì cache đã hết hạn
```

---

## 11. Decorator Pattern - Ví dụ thực tế: Validation

```python
from functools import wraps
from typing import Any, Type, Union, get_type_hints
import inspect

def validate_types(func):
    """Decorator tự động validate kiểu dữ liệu dựa trên type hints"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Lấy type hints
        hints = get_type_hints(func)
        
        # Lấy tên tham số
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Validate từng tham số
        for param_name, value in bound_args.arguments.items():
            if param_name in hints:
                expected_type = hints[param_name]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Parameter '{param_name}' must be of type {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        result = func(*args, **kwargs)
        
        # Validate return type
        if 'return' in hints:
            expected_return = hints['return']
            if not isinstance(result, expected_return):
                raise TypeError(
                    f"Return value must be of type {expected_return.__name__}, "
                    f"got {type(result).__name__}"
                )
        
        return result
    return wrapper

@validate_types
def process_user(name: str, age: int, email: str = None) -> dict:
    return {"name": name, "age": age, "email": email}

# Test
process_user("Alice", 30)  # OK
# process_user("Bob", "25")  # TypeError
# process_user(123, 30)  # TypeError
```

---

## 12. Decorator với Context Manager

```python
from contextlib import contextmanager
from functools import wraps
import time

def timing_decorator(func):
    """Decorator đo thời gian với context manager"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with timeit() as timer:
            result = func(*args, **kwargs)
        print(f"{func.__name__} took {timer.elapsed:.4f} seconds")
        return result
    return wrapper

@contextmanager
def timeit():
    """Context manager đo thời gian"""
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        timer = type('Timer', (), {})()
        timer.elapsed = end - start
        yield timer

@timing_decorator
def heavy_computation():
    time.sleep(0.5)
    return "Done"

heavy_computation()
```

---

## Tổng kết và Best Practices

### ✅ Khi nào nên dùng Decorator:
1. **Logging và Debugging** - Ghi log function calls
2. **Performance Monitoring** - Đo thời gian thực thi
3. **Authentication/Authorization** - Kiểm tra quyền truy cập
4. **Caching** - Lưu trữ kết quả
5. **Validation** - Kiểm tra dữ liệu đầu vào
6. **Retry Logic** - Tự động thử lại khi thất bại
7. **Transaction Management** - Quản lý transaction database

### ❌ Khi nào không nên dùng Decorator:
- Logic quá phức tạp làm code khó đọc
- Cần performance tối ưu (decorator tạo thêm overhead)
- Debugging khó khăn (nếu không dùng functools.wraps)

### 📝 Tips quan trọng:
1. **Luôn dùng `@wraps`** để bảo toàn metadata
2. **Giữ decorator đơn giản** và chuyên biệt
3. **Sử dụng type hints** để tăng tính rõ ràng
4. **Document decorator** của bạn rõ ràng
5. **Test decorator** riêng biệt

---

## Bài tập thực hành

### Bài 1: Retry Decorator
```python
# TODO: Tạo decorator retry tự động thử lại khi có lỗi
@retry(max_attempts=3, delay=1, exceptions=(ConnectionError,))
def unstable_network_call():
    # Code giả lập lỗi
    pass
```

### Bài 2: Memoization với LRU Cache
```python
# TODO: Tạo decorator cache với LRU và TTL
@lru_cache(maxsize=100, ttl=60)
def fibonacci(n):
    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)
```

### Bài 3: Decorator với Dependency Injection
```python
# TODO: Tạo decorator inject dependencies
@inject('database', 'logger')
def process_user_data(db, logger, user_id):
    pass
```

Bạn có muốn tôi đi sâu vào phần nào hơn không? Hoặc bạn có thể đặt câu hỏi về trường hợp sử dụng cụ thể nào đó! 🚀