Chào bạn! Tôi sẽ hướng dẫn bạn về **Class Decorator** trong Python một cách có hệ thống, từ cơ bản đến nâng cao.

## 1. Class Decorator là gì?

**Class Decorator** là một lớp (class) dùng để trang trí (wrap) một hàm hoặc một lớp khác. Nó hoạt động tương tự function decorator nhưng sử dụng `__call__` magic method.

## 2. Cấu trúc cơ bản

```python
class MyDecorator:
    def __init__(self, func):
        self.func = func
        print(f"Đang trang trí hàm: {func.__name__}")
    
    def __call__(self, *args, **kwargs):
        print("Trước khi chạy hàm")
        result = self.func(*args, **kwargs)
        print("Sau khi chạy hàm")
        return result

# Sử dụng
@MyDecorator
def say_hello(name):
    print(f"Hello {name}!")

say_hello("Python")
```

## 3. Decorator với tham số

```python
class RepeatDecorator:
    def __init__(self, times=2):
        self.times = times
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            for _ in range(self.times):
                func(*args, **kwargs)
        return wrapper

@RepeatDecorator(times=3)
def greet(name):
    print(f"Xin chào {name}")

greet("Học viên")  # In ra 3 lần
```

## 4. Decorator cho Class (Class Decorator)

Trang trí cả một class:

```python
class AddMethodDecorator:
    def __init__(self, cls):
        self.cls = cls
        print(f"Đang trang trí class: {cls.__name__}")
    
    def __call__(self, *args, **kwargs):
        # Tạo instance
        instance = self.cls(*args, **kwargs)
        # Thêm method mới
        instance.new_method = lambda: "Đây là method mới được thêm"
        return instance
    
    # Thêm method vào class
    def __getattr__(self, name):
        return getattr(self.cls, name)

@AddMethodDecorator
class Person:
    def __init__(self, name):
        self.name = name
    
    def say_hello(self):
        return f"Hello, I'm {self.name}"

# Sử dụng
p = Person("John")
print(p.say_hello())  # Hello, I'm John
print(p.new_method())  # Đây là method mới được thêm
```

## 5. Class Decorator với State (lưu trạng thái)

```python
class CounterDecorator:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Lần gọi thứ: {self.count}")
        return self.func(*args, **kwargs)

@CounterDecorator
def process_data(data):
    print(f"Xử lý: {data}")

process_data("A")  # Lần gọi thứ: 1
process_data("B")  # Lần gọi thứ: 2
```

## 6. Kết hợp nhiều decorator

```python
class TimerDecorator:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        import time
        start = time.time()
        result = self.func(*args, **kwargs)
        print(f"Thời gian: {time.time() - start:.4f}s")
        return result

class LogDecorator:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        print(f"Calling {self.func.__name__} with {args}")
        return self.func(*args, **kwargs)

@TimerDecorator
@LogDecorator
def slow_function():
    import time
    time.sleep(0.5)
    print("Done!")

slow_function()
```

## 7. Decorator cho method trong class

```python
class Validator:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, instance, *args, **kwargs):
        # Kiểm tra instance
        if not hasattr(instance, 'is_active') or not instance.is_active:
            raise ValueError("Instance không hoạt động")
        return self.func(instance, *args, **kwargs)

class User:
    def __init__(self, name, is_active=True):
        self.name = name
        self.is_active = is_active
    
    @Validator
    def update_profile(self, new_name):
        self.name = new_name
        print(f"Updated to {new_name}")

# Sử dụng
user = User("Alice")
user.update_profile("Bob")  # OK

user.is_active = False
user.update_profile("Charlie")  # Raise ValueError
```

## 8. Bảo toàn metadata với functools.wraps

```python
from functools import wraps
import functools

class PreserveDecorator:
    def __init__(self, func):
        self.func = func
        # Bảo toàn metadata
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        print(f"Running {self.func.__name__}")
        return self.func(*args, **kwargs)

@PreserveDecorator
def important_function():
    """Đây là hàm quan trọng"""
    pass

print(important_function.__name__)    # important_function
print(important_function.__doc__)     # Đây là hàm quan trọng
```

## 9. Ứng dụng thực tế: Caching

```python
class CacheDecorator:
    def __init__(self, func):
        self.func = func
        self.cache = {}
    
    def __call__(self, *args, **kwargs):
        # Tạo key từ arguments
        key = str(args) + str(kwargs)
        
        if key in self.cache:
            print(f"Lấy từ cache: {key}")
            return self.cache[key]
        
        print(f"Tính toán mới: {key}")
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result

@CacheDecorator
def expensive_function(x, y):
    print("Đang tính toán...")
    return x ** y

print(expensive_function(2, 10))  # Tính toán mới
print(expensive_function(2, 10))  # Lấy từ cache
```

## 10. Bài tập thực hành

```python
# Bài tập 1: Tạo decorator kiểm tra kiểu dữ liệu
class TypeChecker:
    def __init__(self, expected_type):
        self.expected_type = expected_type
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Kiểm tra tất cả arguments
            for arg in args:
                if not isinstance(arg, self.expected_type):
                    raise TypeError(f"Expected {self.expected_type}, got {type(arg)}")
            return func(*args, **kwargs)
        return wrapper

# Bài tập 2: Tạo decorator retry
class RetryDecorator:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < self.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Lần thử {attempts} thất bại: {e}")
            raise Exception(f"Thất bại sau {self.max_retries} lần thử")
        return wrapper

# Test thử
@RetryDecorator(max_retries=2)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("Random error!")
    return "Success!"

print(unstable_function())
```

## Tổng kết

**Khi nào dùng Class Decorator:**
- Cần lưu trữ state giữa các lần gọi
- Cần nhiều method và properties
- Code phức tạp cần tổ chức rõ ràng
- Cần tương tác với các thành phần khác của class

**Ưu điểm:**
- Giữ được state (trạng thái)
- Dễ dàng mở rộng
- Code sạch và tổ chức tốt

**Nhược điểm:**
- Phức tạp hơn function decorator
- Có thể khó hiểu với người mới

Bạn muốn tôi giải thích thêm phần nào hoặc làm ví dụ cụ thể hơn không?