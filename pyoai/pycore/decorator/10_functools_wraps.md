# Decorator Deep Dive — Buổi 10

# `functools.wraps` — Decorator chuyên nghiệp

> Đây là buổi học mà **99% decorator trong các framework Python đều sử dụng**.

Nếu bạn đọc mã nguồn của:

  * Flask 
  * FastAPI 
  * Django 
  * Click 
  * Celery 
  * Dramatiq 
  * Typer 



Bạn sẽ gần như luôn thấy:
    
    
    from functools import wraps

và
    
    
    @wraps(func)

Nếu không hiểu `wraps`, bạn sẽ rất khó đọc source code của các framework.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Metadata của function là gì. 
  * Vì sao decorator làm mất metadata. 
  * `functools.wraps` hoạt động như thế nào. 
  * `__wrapped__`
  * `inspect.unwrap`
  * `update_wrapper`
  * Best Practices. 



* * *

# 1\. Function có rất nhiều Metadata

Một function không chỉ là code.

Ví dụ
    
    
    def add(a: int, b: int) -> int:
        """Return sum"""
        return a + b

Python lưu rất nhiều thông tin.
    
    
    print(add.__name__)
    
    
    add

* * *
    
    
    print(add.__doc__)
    
    
    Return sum

* * *
    
    
    print(add.__annotations__)
    
    
    {
        'a': int,
        'b': int,
        'return': int
    }

* * *
    
    
    print(add.__module__)

Ví dụ
    
    
    __main__

* * *
    
    
    print(add.__qualname__)
    
    
    add

* * *
    
    
    print(add.__defaults__)

Nếu có default value.

* * *

Python còn lưu:

  * source 
  * signature 
  * annotations 
  * module 
  * docstring 
  * name 
  * closure 
  * ... 



Đây gọi là **Function Metadata**.

* * *

# 2\. Decorator phá hỏng Metadata

Decorator
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Start")
    
            result = func(*args, **kwargs)
    
            print("End")
    
            return result
    
        return wrapper

Áp dụng
    
    
    @logger
    def add(a, b):
        """Calculate sum"""
        return a + b

Kiểm tra
    
    
    print(add.__name__)

Kết quả
    
    
    wrapper

Không phải
    
    
    add

* * *

Docstring
    
    
    print(add.__doc__)

Kết quả
    
    
    None

Đã mất.

* * *

# 3\. Vì sao?

Sau decorator
    
    
    add
    
    ↓
    
    wrapper

Biến
    
    
    add

không còn trỏ tới function gốc nữa.

Nó trỏ sang
    
    
    wrapper

Cho nên Python chỉ biết
    
    
    wrapper

* * *

# 4\. Hậu quả

Ví dụ
    
    
    help(add)

Kết quả
    
    
    Help on function wrapper

Không phải
    
    
    Help on function add

* * *

IDE

Auto Complete

Swagger

FastAPI

Click

Sphinx

đều dựa vào metadata.

Nếu metadata sai

↓

Tool hoạt động sai.

* * *

# 5\. functools.wraps

Giải pháp
    
    
    from functools import wraps

Sửa
    
    
    from functools import wraps
    
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print("Start")
    
            result = func(*args, **kwargs)
    
            print("End")
    
            return result
    
        return wrapper

Chỉ thêm đúng
    
    
    @wraps(func)

* * *

# 6\. Kết quả
    
    
    @logger
    def add(a, b):
        """Calculate sum"""
        return a + b

Bây giờ
    
    
    print(add.__name__)
    
    
    add

* * *
    
    
    print(add.__doc__)
    
    
    Calculate sum

* * *
    
    
    print(add.__module__)
    
    
    __main__

Đã được giữ nguyên.

* * *

# 7\. wraps làm gì?

Thực ra
    
    
    @wraps(func)

là shortcut của
    
    
    wrapper = update_wrapper(
        wrapper,
        func
    )

Nó copy metadata.

* * *

# 8\. update_wrapper

Có thể viết
    
    
    from functools import update_wrapper
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            return func(*args, **kwargs)
    
        update_wrapper(
            wrapper,
            func
        )
    
        return wrapper

Kết quả giống hệt.

* * *

# 9\. wraps copy gì?

Ví dụ
    
    
    print(add.__name__)

Đúng.

* * *
    
    
    print(add.__doc__)

Đúng.

* * *
    
    
    print(add.__annotations__)

Đúng.

* * *
    
    
    print(add.__module__)

Đúng.

* * *
    
    
    print(add.__qualname__)

Đúng.

* * *

Không chỉ copy vài thuộc tính.

Nó copy khá nhiều metadata quan trọng.

* * *

# 10\. **wrapped**

Đây là tính năng rất hay.

Ví dụ
    
    
    from functools import wraps
    
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print("Logging")
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @logger
    def hello():
        print("Hello")

Bây giờ
    
    
    hello.__wrapped__()

Kết quả
    
    
    Hello

Bypass decorator.

* * *

# 11\. Minh họa

Không dùng wraps
    
    
    wrapper
    
    ↓
    
    hello

Python không biết.

* * *

Có wraps
    
    
    wrapper
    
    ↓
    
    __wrapped__
    
    ↓
    
    hello

Đã có liên kết.

* * *

# 12\. inspect.unwrap

Ví dụ
    
    
    from functools import wraps
    import inspect
    
    
    def A(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
        return wrapper
    
    
    def B(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @A
    @B
    def hello():
        pass

Lấy function gốc
    
    
    original = inspect.unwrap(hello)
    
    print(original.__name__)

Kết quả
    
    
    hello

* * *

# 13\. inspect.signature

Ví dụ
    
    
    import inspect
    
    
    @logger
    def add(a: int, b: int):
        return a + b
    
    
    print(
        inspect.signature(add)
    )

Có wraps
    
    
    (a: int, b: int)

Không wraps
    
    
    (*args, **kwargs)

Rất khác nhau.

* * *

# 14\. Ví dụ thực tế — Logger
    
    
    from functools import wraps
    
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print(
                f"Call {func.__name__}"
            )
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @logger
    def multiply(a, b):
        """Multiply numbers"""
        return a * b
    
    
    print(multiply.__name__)
    print(multiply.__doc__)
    print(multiply(3, 4))

Kết quả
    
    
    multiply
    Multiply numbers
    Call multiply
    12

* * *

# 15\. Ví dụ thực tế — Timer
    
    
    from functools import wraps
    import time
    
    
    def timer(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            start = time.perf_counter()
    
            result = func(*args, **kwargs)
    
            print(
                time.perf_counter() - start
            )
    
            return result
    
        return wrapper
    
    
    @timer
    def slow():
    
        """Sleep 1 second"""
    
        time.sleep(1)
    
    
    print(slow.__doc__)

Kết quả
    
    
    Sleep 1 second

* * *

# 16\. Ví dụ thực tế — Retry
    
    
    from functools import wraps
    
    
    def retry(times):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                last = None
    
                for _ in range(times):
    
                    try:
                        return func(*args, **kwargs)
    
                    except Exception as e:
                        last = e
    
                raise last
    
            return wrapper
    
        return decorator

Đây chính là cách viết trong nhiều thư viện.

* * *

# 17\. Ví dụ hoàn chỉnh — Debug Decorator
    
    
    from functools import wraps
    import inspect
    
    
    def debug(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print("=" * 40)
            print("Function :", func.__name__)
            print("Signature:", inspect.signature(func))
            print("Args     :", args)
            print("Kwargs   :", kwargs)
    
            result = func(*args, **kwargs)
    
            print("Return   :", result)
            print("=" * 40)
    
            return result
    
        return wrapper
    
    
    @debug
    def power(base: int, exp: int = 2):
        """Power function"""
        return base ** exp
    
    
    power(5)

Ví dụ kết quả
    
    
    ========================================
    Function : power
    Signature: (base: int, exp: int = 2)
    Args     : (5,)
    Kwargs   : {}
    Return   : 25
    ========================================

* * *

# 18\. Ví dụ hoàn chỉnh — Plugin Registry
    
    
    from functools import wraps
    
    PLUGINS = {}
    
    
    def plugin(name):
    
        def decorator(func):
    
            PLUGINS[name] = func
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                print(f"Plugin: {name}")
    
                return func(*args, **kwargs)
    
            return wrapper
    
        return decorator
    
    
    @plugin("hello")
    def hello():
        """Hello plugin"""
        print("Hello World")
    
    
    hello()
    
    print(hello.__name__)
    print(hello.__doc__)

Kết quả
    
    
    Plugin: hello
    Hello World
    hello
    Hello plugin

Đây là mẫu thường thấy trong các hệ thống plugin.

* * *

# 19\. wraps và Decorator Stacking

Ví dụ
    
    
    from functools import wraps
    
    
    def A(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
        return wrapper
    
    
    def B(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @A
    @B
    def hello():
        pass

Chuỗi `__wrapped__`
    
    
    hello (wrapper A)
          │
          ▼
    __wrapped__
          │
          ▼
    wrapper B
          │
          ▼
    __wrapped__
          │
          ▼
    hello gốc

Nhờ vậy, `inspect.unwrap()` có thể lần theo toàn bộ chuỗi để tìm được hàm ban đầu.

* * *

# Khi nào KHÔNG nên dùng `@wraps`?

Gần như **không có lý do** để bỏ qua nó trong các decorator thông thường.

Chỉ một số trường hợp đặc biệt như:

  * Muốn cố tình che giấu hàm gốc. 
  * Tạo proxy động với metadata riêng. 
  * Viết framework đặc biệt có cách introspection riêng. 



Đối với ứng dụng thông thường:

> **Luôn dùng`@wraps`.**

* * *

# Mẫu Decorator chuyên nghiệp

Từ bây giờ, đây sẽ là mẫu mặc định của bạn:
    
    
    from functools import wraps
    
    
    def decorator(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            # Before
    
            result = func(*args, **kwargs)
    
            # After
    
            return result
    
        return wrapper

Hầu hết decorator trong hệ sinh thái Python đều tuân theo cấu trúc này.

* * *

# Tổng kết buổi 10

Bạn cần ghi nhớ:

  1. Decorator làm mất metadata của hàm gốc nếu không xử lý. 
  2. `@wraps(func)` sao chép metadata quan trọng từ hàm gốc sang wrapper. 
  3. `wraps` thực chất sử dụng `functools.update_wrapper()`. 
  4. `__wrapped__` giúp truy cập hoặc khôi phục hàm gốc. 
  5. `inspect.unwrap()` có thể lần ngược qua nhiều lớp decorator. 
  6. Luôn sử dụng `@wraps` trong các decorator chuyên nghiệp. 



* * *

# Bài tập

## Bài 1

Viết decorator `@logger` có sử dụng `@wraps`.

Kiểm tra:
    
    
    print(func.__name__)
    print(func.__doc__)
    print(func.__annotations__)

đều giữ nguyên sau khi decorator được áp dụng.

* * *

## Bài 2

Viết hai decorator:

  * `@timer`
  * `@logger`



Cả hai đều dùng `@wraps`.

Sau đó kiểm tra:
    
    
    import inspect
    
    print(inspect.signature(my_function))
    print(my_function.__name__)
    print(my_function.__doc__)

Đảm bảo metadata vẫn chính xác sau khi xếp chồng decorator.

* * *

## Bài 3

Viết ba decorator:
    
    
    @A
    @B
    @C
    def hello():
        ...

Mỗi decorator đều dùng `@wraps`.

Sau đó:

  * In `hello.__wrapped__`. 
  * Dùng `inspect.unwrap(hello)` để lấy hàm gốc. 
  * Chứng minh rằng hàm gốc vẫn giữ nguyên `__name__`, `__doc__` và `signature`. 



* * *

# Roadmap tiếp theo

Bạn đã hoàn thành **Phần II – Decorator cơ bản** :

  * ✅ Buổi 6: Decorator đầu tiên 
  * ✅ Buổi 7: Decorator có tham số 
  * ✅ Buổi 8: Decorator trả về giá trị 
  * ✅ Buổi 9: Decorator nhiều lớp 
  * ✅ Buổi 10: `functools.wraps`



Tiếp theo sẽ là **Phần III – Decorator nâng cao** , nơi chúng ta đi sâu vào cách xây dựng các decorator mạnh mẽ và những kỹ thuật được sử dụng trong các framework Python hiện đại. Chúng ta sẽ bắt đầu với **Decorator cho Method** , phân tích sự khác biệt giữa decorator áp dụng cho hàm thông thường và phương thức của lớp, cũng như vai trò của tham số `self` và `cls`.

