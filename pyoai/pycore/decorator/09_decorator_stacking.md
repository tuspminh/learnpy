# Decorator Deep Dive — Buổi 9

# Decorator nhiều lớp (Decorator Stacking)

> Đây là một trong những chủ đề khiến nhiều lập trình viên Python nhầm lẫn nhất.

Rất nhiều người biết viết:
    
    
    @logger
    @timer
    def hello():
        ...

Nhưng không biết:

  * Decorator nào chạy trước? 
  * Wrapper nào chạy trước? 
  * Decorator nào nhận `hello` đầu tiên? 
  * Thứ tự thực thi ra sao? 



Sau buổi này bạn sẽ có thể **đọc được mọi chuỗi decorator trong Flask, FastAPI, Click, Celery...**

* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu:

  * Decorator Stacking 
  * Thứ tự áp dụng decorator 
  * Thứ tự chạy wrapper 
  * Chuỗi wrapper 
  * Decorator lồng nhau 
  * Các lỗi thường gặp 
  * Best Practices 



* * *

# 1\. Decorator nhiều lớp là gì?

Ví dụ
    
    
    @A
    @B
    def hello():
        print("Hello")

Python **không** chạy theo thứ tự từ trên xuống.

Python sẽ dịch thành
    
    
    def hello():
        print("Hello")
    
    hello = A(B(hello))

Đây là điều phải thuộc lòng.

* * *

# 2\. Hai giai đoạn

Decorator có hai giai đoạn.

## Giai đoạn 1

Khi import module

Python tạo wrapper.
    
    
    A(B(hello))

* * *

## Giai đoạn 2

Khi gọi
    
    
    hello()

Python chạy wrapper.

Hai giai đoạn hoàn toàn khác nhau.

* * *

# 3\. Ví dụ đầu tiên

Decorator A
    
    
    def A(func):
    
        def wrapper():
    
            print("A Before")
    
            func()
    
            print("A After")
    
        return wrapper

Decorator B
    
    
    def B(func):
    
        def wrapper():
    
            print("B Before")
    
            func()
    
            print("B After")
    
        return wrapper

Hàm
    
    
    @A
    @B
    def hello():
        print("Hello")

* * *

# 4\. Python dịch
    
    
    hello = A(B(hello))

Bước đầu
    
    
    hello
    
    ↓
    
    Function

* * *

Sau
    
    
    B(hello)
    
    
    wrapper B
    
    ↓
    
    hello

* * *

Tiếp
    
    
    A(wrapper B)
    
    
    wrapper A
    
    ↓
    
    wrapper B
    
    ↓
    
    hello

* * *

Cuối cùng
    
    
    hello
    
    ↓
    
    wrapper A

* * *

# 5\. Luồng thực thi

Khi
    
    
    hello()

Luồng
    
    
    wrapper A
    
    ↓
    
    A Before
    
    ↓
    
    wrapper B
    
    ↓
    
    B Before
    
    ↓
    
    hello
    
    ↓
    
    B After
    
    ↓
    
    A After

Kết quả
    
    
    A Before
    B Before
    Hello
    B After
    A After

* * *

# 6\. Minh họa trực quan
    
    
    hello()
    
    ↓
    
    wrapper A
    
    ┌──────────────────┐
    │ A Before         │
    │                  │
    │ wrapper B        │
    │                  │
    │   B Before       │
    │   hello()        │
    │   B After        │
    │                  │
    │ A After          │
    └──────────────────┘

* * *

# 7\. Ví dụ với tham số
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Logger")
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    def timer(func):
    
        def wrapper(*args, **kwargs):
    
            print("Timer")
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @logger
    @timer
    def add(a, b):
        return a + b

Python dịch
    
    
    add = logger(timer(add))

* * *

Khi
    
    
    add(3, 5)

Kết quả
    
    
    Logger
    Timer

Sau đó mới chạy
    
    
    add

* * *

# 8\. Ba decorator
    
    
    @A
    @B
    @C
    def hello():
        print("Hello")

Python dịch
    
    
    hello = A(B(C(hello)))

Sơ đồ
    
    
    wrapper A
    
    ↓
    
    wrapper B
    
    ↓
    
    wrapper C
    
    ↓
    
    hello

* * *

Kết quả
    
    
    A Before
    
    ↓
    
    B Before
    
    ↓
    
    C Before
    
    ↓
    
    Hello
    
    ↓
    
    C After
    
    ↓
    
    B After
    
    ↓
    
    A After

* * *

# 9\. Ví dụ hoàn chỉnh
    
    
    def A(func):
    
        def wrapper():
    
            print(">>> A Before")
    
            func()
    
            print("<<< A After")
    
        return wrapper
    
    
    def B(func):
    
        def wrapper():
    
            print(">>> B Before")
    
            func()
    
            print("<<< B After")
    
        return wrapper
    
    
    def C(func):
    
        def wrapper():
    
            print(">>> C Before")
    
            func()
    
            print("<<< C After")
    
        return wrapper
    
    
    @A
    @B
    @C
    def hello():
        print("Hello")
    
    
    hello()

Kết quả
    
    
    >>> A Before
    >>> B Before
    >>> C Before
    Hello
    <<< C After
    <<< B After
    <<< A After

* * *

# 10\. Decorator Factory + Stacking

Ví dụ
    
    
    @repeat(2)
    @logger("INFO")
    def hello():
        print("Hello")

Python dịch
    
    
    hello = repeat(2)(
                logger("INFO")(
                    hello
                )
            )

Có hai factory.

Luồng tạo
    
    
    repeat(2)
    
    ↓
    
    decorator
    
    ↓
    
    logger(INFO)
    
    ↓
    
    decorator

Sau đó
    
    
    decorator
    
    ↓
    
    decorator
    
    ↓
    
    hello

* * *

# 11\. Ví dụ thực tế - Timer + Logger
    
    
    import time
    
    
    def timer(func):
    
        def wrapper(*args, **kwargs):
    
            start = time.perf_counter()
    
            result = func(*args, **kwargs)
    
            elapsed = time.perf_counter() - start
    
            print(f"Time: {elapsed:.4f}s")
    
            return result
    
        return wrapper
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Start")
    
            result = func(*args, **kwargs)
    
            print("End")
    
            return result
    
        return wrapper
    
    
    @logger
    @timer
    def work():
    
        time.sleep(1)
    
    
    work()

Ví dụ kết quả
    
    
    Start
    Time: 1.0002s
    End

Giải thích:
    
    
    logger
    
    ↓
    
    timer
    
    ↓
    
    work

`logger` là lớp ngoài cùng, nên in `"Start"` trước và `"End"` sau. `timer` chỉ đo thời gian của `work()` vì nó nằm bên trong `logger`.

* * *

# 12\. Đổi thứ tự
    
    
    @timer
    @logger
    def work():
        time.sleep(1)

Python
    
    
    work = timer(logger(work))

Lúc này
    
    
    timer
    
    ↓
    
    logger
    
    ↓
    
    work

Timer đo thời gian của
    
    
    logger
    
    +
    
    work

Nghĩa là thời gian ghi log cũng được tính.

Đây là lý do:

> **Thứ tự decorator có thể thay đổi hành vi chương trình.**

* * *

# 13\. Ví dụ Cache + Timer
    
    
    import time
    
    
    def cache(func):
        memory = {}
    
        def wrapper(n):
            if n in memory:
                print("Cache hit")
                return memory[n]
    
            result = func(n)
            memory[n] = result
            return result
    
        return wrapper
    
    
    def timer(func):
    
        def wrapper(*args, **kwargs):
    
            start = time.perf_counter()
    
            result = func(*args, **kwargs)
    
            print(
                time.perf_counter() - start
            )
    
            return result
    
        return wrapper

* * *

## Trường hợp 1
    
    
    @cache
    @timer
    def square(n):
        return n * n

Python
    
    
    square = cache(timer(square))

Lần gọi thứ hai:
    
    
    Cache hit

`timer` **không chạy** , vì cache trả kết quả trước khi vào `timer`.

* * *

## Trường hợp 2
    
    
    @timer
    @cache
    def square(n):
        return n * n

Python
    
    
    square = timer(cache(square))

Lần gọi thứ hai:
    
    
    Cache hit
    0.000001

`timer` vẫn chạy, vì nó là lớp ngoài cùng.

Đây là ví dụ kinh điển cho thấy **thứ tự decorator ảnh hưởng trực tiếp đến hành vi của chương trình**.

* * *

# 14\. Ví dụ thực tế - Authentication + Logging
    
    
    LOGGED_IN = True
    
    
    def login_required(func):
    
        def wrapper(*args, **kwargs):
    
            if not LOGGED_IN:
                print("Access denied")
                return
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Request received")
    
            result = func(*args, **kwargs)
    
            print("Request finished")
    
            return result
    
        return wrapper

* * *

## Cách 1
    
    
    @logger
    @login_required
    def dashboard():
        print("Dashboard")

Ngay cả khi chưa đăng nhập, `"Request received"` vẫn được ghi log.

* * *

## Cách 2
    
    
    @login_required
    @logger
    def dashboard():
        print("Dashboard")

Nếu chưa đăng nhập, `logger` sẽ **không chạy**.

Đây là quyết định thiết kế, không phải đúng hay sai tuyệt đối.

* * *

# 15\. Debug chuỗi decorator

Một kỹ thuật rất hữu ích:
    
    
    def debug(name):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                print(f"Enter {name}")
    
                result = func(*args, **kwargs)
    
                print(f"Exit {name}")
    
                return result
    
            return wrapper
    
        return decorator
    
    
    @debug("A")
    @debug("B")
    @debug("C")
    def hello():
        print("Hello")
    
    
    hello()

Kết quả
    
    
    Enter A
    Enter B
    Enter C
    Hello
    Exit C
    Exit B
    Exit A

Rất dễ quan sát thứ tự thực thi.

* * *

# 16\. Mô hình "hành củ" (Onion Model)

Decorator nhiều lớp thường được hình dung như các lớp của củ hành:
    
    
    +--------------------------+
    | Logger                   |
    |  +--------------------+  |
    |  | Timer              |  |
    |  |  +--------------+  |  |
    |  |  | Cache        |  |  |
    |  |  |  hello()     |  |  |
    |  |  +--------------+  |  |
    |  +--------------------+  |
    +--------------------------+

Khi đi vào:
    
    
    Logger
    ↓
    
    Timer
    ↓
    
    Cache
    ↓
    
    hello

Khi đi ra:
    
    
    hello
    ↓
    
    Cache
    ↓
    
    Timer
    ↓
    
    Logger

* * *

# 17\. Quy tắc ghi nhớ

## Quy tắc 1

Decorator gần hàm nhất:
    
    
    @A
    @B
    def hello():

`B` nhận `hello` đầu tiên.

* * *

## Quy tắc 2

Decorator trên cùng là lớp ngoài cùng.
    
    
    @A
    @B
    def hello():

`A` chạy trước khi vào và chạy sau khi ra.

* * *

## Quy tắc 3

Nhớ công thức:
    
    
    @A
    @B
    @C
    def f():
        ...

Luôn tương đương:
    
    
    f = A(B(C(f)))

* * *

# Những lỗi phổ biến

## Sai 1

Cho rằng Python chạy decorator từ trên xuống.

Thực tế:

  * **Áp dụng** từ dưới lên. 
  * **Bao bọc** từ trong ra ngoài. 
  * **Thực thi** theo thứ tự wrapper ngoài → trong → hàm → trong → ngoài. 



* * *

## Sai 2

Không dùng `return`

Nếu wrapper ngoài không trả kết quả:
    
    
    return func(...)

thì toàn bộ chuỗi decorator sẽ mất giá trị trả về.

* * *

## Sai 3

Decorator không hỗ trợ `*args, **kwargs`

Chỉ cần một lớp trong chuỗi không hỗ trợ, cả chuỗi có thể lỗi.

* * *

# Best Practices

✅ Mỗi decorator chỉ nên có **một trách nhiệm** :

  * `@logger`: ghi log. 
  * `@timer`: đo thời gian. 
  * `@cache`: lưu cache. 
  * `@retry`: thử lại. 
  * `@permission`: kiểm tra quyền. 



Không nên gộp quá nhiều chức năng vào một decorator duy nhất.

* * *

# Tổng kết buổi 9

Bạn cần ghi nhớ:

  1. `@A @B @C` tương đương: 


    
    
    f = A(B(C(f)))

  2. Decorator gần hàm nhất nhận hàm trước. 
  3. Decorator trên cùng là wrapper ngoài cùng. 
  4. Thứ tự decorator ảnh hưởng đến kết quả chương trình. 
  5. Hãy hình dung decorator như các lớp của một củ hành (Onion Model). 



* * *

# Bài tập

## Bài 1

Viết ba decorator:

  * `@logger`
  * `@timer`
  * `@repeat(2)`



Áp dụng theo hai thứ tự khác nhau và giải thích sự khác biệt của kết quả.

* * *

## Bài 2

Viết ba decorator:
    
    
    @A
    @B
    @C
    def hello():
        ...

Mỗi decorator in:

  * `"Enter X"`
  * `"Exit X"`



Vẽ lại sơ đồ luồng thực thi của chương trình.

* * *

## Bài 3

Viết một decorator `@transaction` và một decorator `@logger`.

Thử hai cách:
    
    
    @transaction
    @logger
    def save():
        ...

và
    
    
    @logger
    @transaction
    def save():
        ...

Quan sát và giải thích sự khác biệt trong log và luồng thực thi.

* * *

# Chuẩn bị cho buổi 10

Ở **buổi 10** , chúng ta sẽ học về **`functools.wraps`** – một thành phần gần như bắt buộc trong mọi decorator chuyên nghiệp. Bạn sẽ thấy vì sao sau khi bọc một hàm bằng decorator, các thuộc tính như `__name__`, `__doc__`, `__annotations__` và khả năng introspection bị thay đổi, và cách `@functools.wraps` khôi phục toàn bộ metadata của hàm gốc. Đây là kỹ thuật được sử dụng trong hầu hết các framework Python hiện đại như Flask, FastAPI, Click, Celery và Dramatiq.

