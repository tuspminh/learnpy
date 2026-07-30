# Decorator Deep Dive — Buổi 11

# Class-based Decorator (Decorator được cài đặt bằng Class)

> Từ buổi trước đến giờ, chúng ta đều viết decorator bằng **function**.
> 
> Hôm nay, chúng ta sẽ học một kỹ thuật nâng cao: **viết decorator bằng class**.

Đây là kỹ thuật được sử dụng trong nhiều framework và thư viện Python vì class có thể lưu trạng thái (state) và dễ mở rộng hơn function.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Class-based decorator là gì. 
  * `__call__()` hoạt động như thế nào. 
  * Tại sao class có thể thay thế function. 
  * Lưu trạng thái trong decorator. 
  * So sánh Function Decorator và Class Decorator. 
  * Các ví dụ thực tế. 



* * *

# 1\. Ôn lại: Function Decorator

Decorator quen thuộc:
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Before")
            result = func(*args, **kwargs)
            print("After")
            return result
    
        return wrapper

Sử dụng:
    
    
    @logger
    def hello():
        print("Hello")

Python dịch thành:
    
    
    hello = logger(hello)

* * *

# 2\. Ý tưởng của Class Decorator

Class cũng có thể được gọi như function nếu cài đặt:
    
    
    class Demo:
    
        def __call__(self):
            print("I'm callable")
    
    
    d = Demo()
    
    d()

Kết quả:
    
    
    I'm callable

Có nghĩa là:
    
    
    d()

thực chất là:
    
    
    d.__call__()

* * *

# 3\. Decorator đầu tiên bằng Class
    
    
    class Logger:
    
        def __init__(self, func):
            self.func = func
    
        def __call__(self):
    
            print("Before")
    
            self.func()
    
            print("After")

Sử dụng:
    
    
    @Logger
    def hello():
        print("Hello")

Python dịch:
    
    
    hello = Logger(hello)

Bây giờ:
    
    
    hello()

thực chất là:
    
    
    hello.__call__()

* * *

# 4\. Luồng hoạt động
    
    
    @Logger
    
    ↓
    
    Logger(hello)
    
    ↓
    
    __init__()
    
    ↓
    
    object Logger
    
    ↓
    
    hello()
    
    ↓
    
    __call__()
    
    ↓
    
    hello gốc

* * *

# 5\. Hỗ trợ tham số

Decorator cần hỗ trợ mọi hàm:
    
    
    class Logger:
    
        def __init__(self, func):
            self.func = func
    
        def __call__(self, *args, **kwargs):
    
            print("Before")
    
            result = self.func(*args, **kwargs)
    
            print("After")
    
            return result

Ví dụ:
    
    
    @Logger
    def add(a, b):
        return a + b
    
    print(add(2, 3))

Kết quả:
    
    
    Before
    After
    5

* * *

# 6\. Lưu trạng thái (State)

Đây là ưu điểm lớn nhất của class.

Ví dụ:
    
    
    class Counter:
    
        def __init__(self, func):
    
            self.func = func
            self.count = 0
    
        def __call__(self, *args, **kwargs):
    
            self.count += 1
    
            print("Call:", self.count)
    
            return self.func(*args, **kwargs)
    
    
    @Counter
    def hello():
        print("Hello")
    
    
    hello()
    hello()
    hello()

Kết quả:
    
    
    Call: 1
    Hello
    
    Call: 2
    Hello
    
    Call: 3
    Hello

* * *

# 7\. So sánh với Function Decorator

Function:
    
    
    def counter(func):
    
        count = 0
    
        def wrapper():
    
            nonlocal count
    
            count += 1
    
            print(count)
    
            func()
    
        return wrapper

Class:
    
    
    class Counter:
    
        def __init__(self, func):
            self.count = 0

Class trực quan hơn khi có nhiều biến trạng thái.

* * *

# 8\. Ví dụ Logger nâng cao
    
    
    import time
    
    
    class Logger:
    
        def __init__(self, func):
    
            self.func = func
    
        def __call__(self, *args, **kwargs):
    
            print("=" * 40)
            print("Function:", self.func.__name__)
    
            start = time.perf_counter()
    
            result = self.func(*args, **kwargs)
    
            elapsed = time.perf_counter() - start
    
            print(f"Time: {elapsed:.6f}s")
            print("=" * 40)
    
            return result
    
    
    @Logger
    def calculate():
    
        total = 0
    
        for i in range(100000):
            total += i
    
        return total
    
    
    calculate()

* * *

# 9\. Ví dụ Cache
    
    
    class Cache:
    
        def __init__(self, func):
    
            self.func = func
            self.memory = {}
    
        def __call__(self, x):
    
            if x in self.memory:
                print("Cache hit")
                return self.memory[x]
    
            print("Cache miss")
    
            result = self.func(x)
    
            self.memory[x] = result
    
            return result
    
    
    @Cache
    def square(x):
    
        print("Calculating...")
    
        return x * x
    
    
    print(square(5))
    print(square(5))

Kết quả:
    
    
    Cache miss
    Calculating...
    25
    
    Cache hit
    25

* * *

# 10\. Ví dụ Retry
    
    
    class Retry:
    
        def __init__(self, func):
    
            self.func = func
    
        def __call__(self, *args, **kwargs):
    
            for attempt in range(3):
    
                try:
                    return self.func(*args, **kwargs)
    
                except Exception:
    
                    print(
                        "Retry",
                        attempt + 1
                    )
    
            raise RuntimeError("Failed")

* * *

# 11\. Ví dụ Validation
    
    
    class Positive:
    
        def __init__(self, func):
    
            self.func = func
    
        def __call__(self, a, b):
    
            if a < 0 or b < 0:
                raise ValueError
    
            return self.func(a, b)

* * *

# 12\. Vấn đề với metadata
    
    
    @Logger
    def hello():
        """Hello function"""
        pass

Kiểm tra:
    
    
    print(hello.__class__)

Kết quả:
    
    
    <class '__main__.Logger'>

`hello` **không còn là function**.

Nó là object.

* * *

Kiểm tra:
    
    
    print(hello.__name__)

Lỗi:
    
    
    AttributeError

Vì object `Logger` không có `__name__`.

* * *

# 13\. Khắc phục bằng `functools.update_wrapper`
    
    
    from functools import update_wrapper
    
    
    class Logger:
    
        def __init__(self, func):
    
            self.func = func
    
            update_wrapper(self, func)
    
        def __call__(self, *args, **kwargs):
    
            print("Before")
    
            return self.func(*args, **kwargs)

Bây giờ:
    
    
    @Logger
    def hello():
        """Hello"""
        pass
    
    print(hello.__name__)
    print(hello.__doc__)

Kết quả:
    
    
    hello
    Hello

> **Lưu ý:** `functools.wraps` chỉ dùng được cho function. Với class-based decorator, ta dùng `functools.update_wrapper()`.

* * *

# 14\. So sánh Function và Class Decorator

Tiêu chí| Function Decorator| Class Decorator  
---|---|---  
Cài đặt| Function| Class  
Gọi| `wrapper()`| `__call__()`  
Lưu trạng thái| Closure| Thuộc tính (`self`)  
Metadata| `@wraps`| `update_wrapper`  
Dễ mở rộng| Trung bình| Rất tốt  
  
* * *

# 15\. Ví dụ hoàn chỉnh
    
    
    from functools import update_wrapper
    import time
    
    
    class Benchmark:
    
        def __init__(self, func):
    
            self.func = func
            self.calls = 0
    
            update_wrapper(self, func)
    
        def __call__(self, *args, **kwargs):
    
            self.calls += 1
    
            start = time.perf_counter()
    
            result = self.func(*args, **kwargs)
    
            elapsed = time.perf_counter() - start
    
            print(f"Call : {self.calls}")
            print(f"Time : {elapsed:.6f}s")
    
            return result
    
    
    @Benchmark
    def fibonacci(n):
    
        if n <= 1:
            return n
    
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    
    print(fibonacci(10))

* * *

# 16\. Khi nào nên dùng Class-based Decorator?

Rất phù hợp khi decorator cần:

  * Lưu bộ đếm (`count`). 
  * Lưu cache. 
  * Lưu cấu hình phức tạp. 
  * Quản lý tài nguyên. 
  * Theo dõi thống kê. 
  * Chứa nhiều phương thức hỗ trợ. 



Ví dụ:
    
    
    class Cache:
        ...

sẽ dễ mở rộng hơn:
    
    
    def cache():
        ...

* * *

# Những lỗi phổ biến

## Sai 1

Quên `__call__`
    
    
    class Logger:
        pass

Object sẽ không thể gọi được:
    
    
    hello()

* * *

## Sai 2

Quên `return`
    
    
    result = self.func(...)

Nhưng không:
    
    
    return result

* * *

## Sai 3

Không dùng `*args, **kwargs`

Decorator chỉ hoạt động với một số hàm cụ thể.

* * *

## Sai 4

Quên `update_wrapper()`

Khiến mất metadata (`__name__`, `__doc__`, ...).

* * *

# Tổng kết buổi 11

Bạn cần ghi nhớ:

  1. Class có `__call__()` là **callable**. 
  2. `@DecoratorClass` tương đương: 


    
    
    func = DecoratorClass(func)

  3. Khi gọi: 


    
    
    func()

thực chất là:
    
    
    func.__call__()

  4. Class-based decorator rất mạnh khi cần lưu trạng thái. 
  5. Dùng `functools.update_wrapper()` để giữ metadata. 



* * *

# Bài tập

## Bài 1

Viết class decorator:
    
    
    @Counter
    def hello():
        ...

Yêu cầu:

  * Đếm số lần gọi. 
  * In tổng số lần gọi sau mỗi lần thực thi. 



* * *

## Bài 2

Viết class decorator:
    
    
    @Cache
    def factorial(n):
        ...

Yêu cầu:

  * Lưu kết quả đã tính. 
  * In `"Cache hit"` hoặc `"Cache miss"`. 



* * *

## Bài 3

Viết class decorator:
    
    
    @Benchmark
    def sort_numbers(data):
        ...

Yêu cầu:

  * Đo thời gian chạy. 
  * Đếm số lần gọi. 
  * Giữ nguyên `__name__` và `__doc__` bằng `update_wrapper()`. 



* * *

# Chuẩn bị cho buổi 12

Ở **buổi 12** , chúng ta sẽ học **Decorator Factory nâng cao**. Khác với buổi 8 chỉ giới thiệu mô hình ba tầng cơ bản, buổi học này sẽ đi sâu vào:

  * Kết hợp Decorator Factory với `@wraps`. 
  * Decorator Factory viết bằng class. 
  * Nhiều tham số cấu hình. 
  * Validation tham số. 
  * Các mẫu thiết kế (patterns) được sử dụng trong Flask, FastAPI, Click và Celery. 



Đây là bước chuyển từ "biết viết decorator" sang "thiết kế decorator có khả năng tái sử dụng trong framework".

