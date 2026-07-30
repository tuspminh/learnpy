# Decorator Deep Dive — Buổi 7

# Decorator hỗ trợ mọi loại hàm với `*args`, `**kwargs` và `return`

Đây là buổi học đánh dấu bước chuyển từ **Decorator "đồ chơi"** sang **Decorator chuyên nghiệp**.

Decorator của buổi trước:
    
    
    def decorator(func):
    
        def wrapper():
            print("Before")
    
            func()
    
            print("After")
    
        return wrapper

Có một vấn đề cực lớn:

Nó chỉ hoạt động với
    
    
    def hello():
        pass

Nhưng Python có rất nhiều loại hàm:
    
    
    def add(a, b):
        ...
    
    
    def save(user, age, city):
        ...
    
    
    def login(username, password, remember=False):
        ...
    
    
    def api(*args, **kwargs):
        ...

Decorator phải hỗ trợ **tất cả**.

Đó là mục tiêu của hôm nay.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu

  * Vì sao wrapper bị lỗi 
  * Positional Argument 
  * Keyword Argument 
  * `*args`
  * `**kwargs`
  * Truyền tiếp tham số 
  * Trả về giá trị (`return`) 
  * Decorator chuẩn của Python 



* * *

# 1\. Vấn đề của Decorator cũ

Decorator cũ
    
    
    def logger(func):
    
        def wrapper():
            print("Start")
    
            func()
    
            print("End")
    
        return wrapper

Hàm
    
    
    @logger
    def add(a, b):
        return a + b

Gọi
    
    
    add(2, 3)

Lỗi
    
    
    TypeError:
    wrapper() takes 0 positional arguments
    but 2 were given

* * *

## Vì sao?

Sau decorator
    
    
    add
    
    ↓
    
    wrapper

Python thực tế gọi
    
    
    wrapper(2, 3)

Trong khi
    
    
    def wrapper():

không nhận tham số.

* * *

# 2\. Cách sửa

Wrapper cũng phải nhận tham số.
    
    
    def logger(func):
    
        def wrapper(a, b):
    
            print("Start")
    
            func(a, b)
    
            print("End")
    
        return wrapper

Bây giờ
    
    
    @logger
    def add(a, b):
        return a + b

chạy được.

* * *

Nhưng...

Nếu
    
    
    def add(a, b, c):

thì sao?

Lại phải sửa.

Không ổn.

* * *

# 3\. *args

Python có cú pháp
    
    
    def hello(*args):
        print(args)

Gọi
    
    
    hello()
    
    
    ()

* * *
    
    
    hello(1)
    
    
    (1,)

* * *
    
    
    hello(1, 2, 3)
    
    
    (1, 2, 3)

`args`

là tuple.

* * *

# 4\. Ví dụ
    
    
    def show(*args):
    
        for item in args:
            print(item)
    
    
    show(
        "Python",
        "Decorator",
        "Closure",
    )

Kết quả
    
    
    Python
    Decorator
    Closure

* * *

# 5\. **kwargs

Tương tự
    
    
    def hello(**kwargs):
        print(kwargs)

Gọi
    
    
    hello(name="Alice", age=20)

Kết quả
    
    
    {
        'name':'Alice',
        'age':20
    }

kwargs là dictionary.

* * *

# 6\. Ví dụ
    
    
    def profile(**kwargs):
    
        for k, v in kwargs.items():
            print(k, "=", v)
    
    
    profile(
        name="Alice",
        age=20,
        city="HCM",
    )
    
    
    name = Alice
    age = 20
    city = HCM

* * *

# 7\. Kết hợp
    
    
    def show(*args, **kwargs):
    
        print(args)
    
        print(kwargs)
    
    
    show(
        1,
        2,
        3,
        name="Alice",
        age=20,
    )

Kết quả
    
    
    (1,2,3)
    
    {
    'name':'Alice',
    'age':20
    }

* * *

# 8\. Decorator chuẩn

Bây giờ
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Before")
    
            func(*args, **kwargs)
    
            print("After")
    
        return wrapper

Đây chính là mẫu decorator mà gần như mọi framework Python đều sử dụng.

* * *

# 9\. Truyền tiếp tham số

Đây là phần cực kỳ quan trọng.
    
    
    func(*args, **kwargs)

không phải
    
    
    func(args, kwargs)

Hai cái hoàn toàn khác.

* * *

Ví dụ
    
    
    def add(a, b):
        print(a, b)
    
    
    values = (2, 3)

Sai
    
    
    add(values)

Lỗi

Đúng
    
    
    add(*values)

Python sẽ biến
    
    
    *values

thành
    
    
    add(2, 3)

* * *

# 10\. Ví dụ kwargs
    
    
    def hello(name, age):
        print(name, age)
    
    
    user = {
        "name": "Alice",
        "age": 20,
    }

Đúng
    
    
    hello(**user)

Python biến thành
    
    
    hello(
        name="Alice",
        age=20,
    )

* * *

# 11\. Return

Decorator cũ
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Start")
    
            func(*args, **kwargs)
    
            print("End")
    
        return wrapper

Nếu
    
    
    @logger
    def add(a, b):
        return a + b
    
    
    print(add(2,3))

Kết quả
    
    
    Start
    End
    None

Sai.

* * *

## Vì sao?

Wrapper không trả kết quả.
    
    
    func(...)

bị bỏ đi.

* * *

# 12\. Decorator đúng
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Start")
    
            result = func(*args, **kwargs)
    
            print("End")
    
            return result
    
        return wrapper

* * *

Thử
    
    
    @logger
    def add(a, b):
        return a + b
    
    print(add(2,3))
    
    
    Start
    End
    5

Đây là mẫu chuẩn.

* * *

# 13\. Ví dụ Logging
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print(f"Calling {func.__name__}")
    
            result = func(*args, **kwargs)
    
            print(f"Finished {func.__name__}")
    
            return result
    
        return wrapper
    
    
    @logger
    def multiply(a, b):
        return a * b
    
    
    answer = multiply(6, 7)
    
    print(answer)

Kết quả
    
    
    Calling multiply
    Finished multiply
    42

* * *

# 14\. Ví dụ Timer
    
    
    import time
    
    
    def timer(func):
    
        def wrapper(*args, **kwargs):
    
            start = time.perf_counter()
    
            result = func(*args, **kwargs)
    
            end = time.perf_counter()
    
            print(
                f"Elapsed: {end-start:.6f}s"
            )
    
            return result
    
        return wrapper
    
    
    @timer
    def slow_add(a, b):
    
        time.sleep(1)
    
        return a + b
    
    
    print(slow_add(5, 9))

Ví dụ
    
    
    Elapsed: 1.000821s
    14

* * *

# 15\. Ví dụ Validation
    
    
    def positive_only(func):
    
        def wrapper(*args, **kwargs):
    
            for value in args:
                if value < 0:
                    raise ValueError(
                        "Negative number"
                    )
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @positive_only
    def area(width, height):
        return width * height
    
    
    print(area(5, 8))
    
    
    40
    
    
    area(-5,8)
    
    
    ValueError

* * *

# 16\. Ví dụ Cache (đơn giản)
    
    
    def cache(func):
    
        memory = {}
    
        def wrapper(*args):
    
            if args in memory:
                print("Cache hit")
                return memory[args]
    
            print("Cache miss")
    
            result = func(*args)
    
            memory[args] = result
    
            return result
    
        return wrapper
    
    
    @cache
    def square(x):
        print("Calculating...")
        return x * x
    
    
    print(square(5))
    print(square(5))

Kết quả
    
    
    Cache miss
    Calculating...
    25
    
    Cache hit
    25

Đây chính là ý tưởng của `functools.lru_cache`.

* * *

# 17\. Ví dụ Retry
    
    
    def retry(func):
    
        def wrapper(*args, **kwargs):
    
            for attempt in range(3):
    
                try:
                    return func(*args, **kwargs)
    
                except Exception:
    
                    print(
                        "Retry",
                        attempt + 1
                    )
    
            raise RuntimeError(
                "Failed"
            )
    
        return wrapper

* * *

# 18\. Ví dụ hoàn chỉnh — Debug Decorator
    
    
    import time
    
    
    def debug(func):
    
        def wrapper(*args, **kwargs):
    
            print("=" * 40)
            print("Function :", func.__name__)
            print("Args     :", args)
            print("Kwargs   :", kwargs)
    
            start = time.perf_counter()
    
            result = func(*args, **kwargs)
    
            elapsed = time.perf_counter() - start
    
            print("Result   :", result)
            print(f"Time     : {elapsed:.6f}s")
            print("=" * 40)
    
            return result
    
        return wrapper
    
    
    @debug
    def divide(a, b):
        return a / b
    
    
    divide(20, 5)

Ví dụ
    
    
    ========================================
    Function : divide
    Args     : (20, 5)
    Kwargs   : {}
    Result   : 4.0
    Time     : 0.000003s
    ========================================

Đây là mẫu debug decorator rất hữu ích trong quá trình phát triển ứng dụng.

* * *

# 19\. Luồng thực thi

Khi gọi
    
    
    add(2,3)

Luồng
    
    
    add
    
    ↓
    
    wrapper
    
    ↓
    
    args=(2,3)
    
    ↓
    
    func(*args)
    
    ↓
    
    add gốc
    
    ↓
    
    return 5
    
    ↓
    
    wrapper
    
    ↓
    
    return 5
    
    ↓
    
    print()

* * *

# Mẫu Decorator chuẩn

Đây là mẫu mà bạn sẽ thấy trong rất nhiều thư viện:
    
    
    def decorator(func):
    
        def wrapper(*args, **kwargs):
    
            # Before
    
            result = func(*args, **kwargs)
    
            # After
    
            return result
    
        return wrapper

Hãy ghi nhớ mẫu này. Từ đây trở đi, gần như mọi decorator chúng ta viết chỉ khác nhau ở phần "Before" và "After".

* * *

# Những lỗi phổ biến

## Sai 1
    
    
    func(args)

Đúng
    
    
    func(*args)

* * *

## Sai 2

Quên
    
    
    return result

* * *

## Sai 3
    
    
    func(kwargs)

Đúng
    
    
    func(**kwargs)

* * *

## Sai 4
    
    
    wrapper(args, kwargs)

Đúng
    
    
    wrapper(*args, **kwargs)

* * *

# Tổng kết buổi 7

Bạn cần nắm chắc:

  1. `*args` gom tất cả tham số vị trí thành một tuple. 
  2. `**kwargs` gom tất cả tham số theo tên thành một dictionary. 
  3. Decorator chuyên nghiệp luôn khai báo: 


    
    
    def wrapper(*args, **kwargs):

  4. Luôn chuyển tiếp tham số bằng: 


    
    
    func(*args, **kwargs)

  5. Luôn lưu và trả về kết quả: 


    
    
    result = func(*args, **kwargs)
    return result

  6. Đây là nền tảng của hầu hết decorator trong các framework như Flask, FastAPI, Django, Click, Celery và Dramatiq. 



* * *

# Bài tập

## Bài 1

Viết decorator `@count_calls`:
    
    
    @count_calls
    def hello(name):
        print(f"Hello {name}")

Mỗi lần gọi phải in ra số lần hàm đã được thực thi:
    
    
    Call #1
    Hello Alice
    
    Call #2
    Hello Bob

_Gợi ý:_ dùng **Closure** và `nonlocal`.

* * *

## Bài 2

Viết decorator `@trace`:
    
    
    @trace
    def power(a, b):
        return a ** b

Yêu cầu in:

  * Tên hàm 
  * `args`
  * `kwargs`
  * Giá trị trả về 



* * *

## Bài 3

Viết decorator `@exception_handler`:
    
    
    @exception_handler
    def divide(a, b):
        return a / b

Nếu có ngoại lệ:

  * In tên ngoại lệ. 
  * Trả về `None`. 
  * Không làm chương trình bị dừng. 



* * *

# Chuẩn bị cho buổi 8

Ở **buổi 8** , chúng ta sẽ học **Decorator Factory (Decorator có tham số)** , ví dụ:
    
    
    @repeat(3)
    def hello():
        print("Hello")

hoặc:
    
    
    @retry(times=5)
    def download():
        ...

Đây là bước nâng cao đầu tiên và cũng là mẫu được sử dụng rất nhiều trong các framework Python hiện đại. Chúng ta sẽ phân tích kỹ vì sao cần **ba tầng hàm lồng nhau** , luồng thực thi của từng tầng, và cách xây dựng các decorator có cấu hình linh hoạt.

