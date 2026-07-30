# Decorator Deep Dive — Buổi 12

# Decorator Factory nâng cao (Professional Decorator Factory)

> **Lưu ý nhỏ về roadmap:** Ở buổi 8 chúng ta đã học **Decorator Factory cơ bản** (3 tầng hàm). Buổi 12 sẽ đi sâu vào **Decorator Factory nâng cao** : thiết kế chuyên nghiệp, validate tham số, nhiều cấu hình, kết hợp `@wraps`, và các mẫu thường gặp trong framework.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Decorator Factory chuyên nghiệp 
  * Factory nhiều tham số 
  * Factory có giá trị mặc định 
  * Validate tham số 
  * Decorator Factory dùng Class 
  * Best Practices 
  * Cách Flask/FastAPI/Click sử dụng Factory 



* * *

# 1\. Ôn lại Decorator Factory

Buổi 8:
    
    
    from functools import wraps
    
    def repeat(times):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                for _ in range(times):
                    func(*args, **kwargs)
    
            return wrapper
    
        return decorator

Có ba tầng:
    
    
    Factory
    
    ↓
    
    Decorator
    
    ↓
    
    Wrapper

* * *

# 2\. Factory có nhiều tham số

Decorator không nhất thiết chỉ có một tham số.

Ví dụ
    
    
    @retry(times=5, delay=1)

Python hiểu
    
    
    func = retry(
        times=5,
        delay=1
    )(func)

* * *

Factory
    
    
    from functools import wraps
    import time
    
    def retry(times, delay):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                last = None
    
                for attempt in range(times):
    
                    try:
                        return func(*args, **kwargs)
    
                    except Exception as e:
    
                        print(
                            f"Retry {attempt+1}"
                        )
    
                        last = e
    
                        time.sleep(delay)
    
                raise last
    
            return wrapper
    
        return decorator

* * *

# 3\. Ví dụ
    
    
    counter = 0
    
    
    @retry(times=3, delay=1)
    def unstable():
    
        global counter
    
        counter += 1
    
        if counter < 3:
            raise RuntimeError()
    
        print("Success")
    
    
    unstable()

Ví dụ kết quả
    
    
    Retry 1
    Retry 2
    Success

* * *

# 4\. Giá trị mặc định

Factory thường có default.
    
    
    def retry(
        times=3,
        delay=0
    ):
        ...

Có thể gọi
    
    
    @retry()

hoặc
    
    
    @retry(delay=2)

hoặc
    
    
    @retry(times=10)

Đây là cách hầu hết framework thiết kế API.

* * *

# 5\. Keyword-only Argument

Nên ép người dùng truyền theo tên.
    
    
    def retry(
        *,
        times=3,
        delay=0
    ):
        ...

Bây giờ

Sai
    
    
    @retry(5,2)

Đúng
    
    
    @retry(
        times=5,
        delay=2
    )

API rõ ràng hơn.

* * *

# 6\. Validate tham số

Không nên tin dữ liệu người dùng.

Ví dụ
    
    
    from functools import wraps
    
    def repeat(times):
    
        if times <= 0:
            raise ValueError(
                "times > 0"
            )
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                result = None
    
                for _ in range(times):
    
                    result = func(
                        *args,
                        **kwargs
                    )
    
                return result
    
            return wrapper
    
        return decorator

* * *

Sai
    
    
    @repeat(-5)

Lỗi ngay khi import module.

Điều này rất tốt.

* * *

# 7\. Validate kiểu dữ liệu
    
    
    def repeat(times):
    
        if not isinstance(
            times,
            int
        ):
            raise TypeError
    
        if times <= 0:
            raise ValueError

Đây là cách viết chuyên nghiệp.

* * *

# 8\. Factory nhiều cấu hình

Ví dụ
    
    
    @logger(
        level="INFO",
        show_time=True,
        show_args=False
    )

Decorator
    
    
    from functools import wraps
    import time
    
    def logger(
        *,
        level="INFO",
        show_time=True,
        show_args=True
    ):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                print(
                    f"[{level}] {func.__name__}"
                )
    
                if show_args:
                    print(args, kwargs)
    
                start = time.perf_counter()
    
                result = func(
                    *args,
                    **kwargs
                )
    
                if show_time:
    
                    elapsed = (
                        time.perf_counter()
                        - start
                    )
    
                    print(
                        f"{elapsed:.6f}s"
                    )
    
                return result
    
            return wrapper
    
        return decorator

* * *

# 9\. Ví dụ sử dụng
    
    
    @logger(
        level="DEBUG",
        show_args=True,
        show_time=True
    )
    def add(a, b):
    
        return a + b
    
    
    print(add(3, 5))

Ví dụ
    
    
    [DEBUG] add
    (3, 5) {}
    0.000004s
    8

* * *

# 10\. Decorator Factory bằng Class

Factory cũng có thể trả về object.
    
    
    from functools import update_wrapper
    
    
    class Repeat:
    
        def __init__(self, times):
    
            self.times = times
    
        def __call__(self, func):
    
            update_wrapper(self, func)
    
            self.func = func
    
            return self
    
        def __get__(self, instance, owner):
            # Chuẩn bị cho buổi Method Decorator
            if instance is None:
                return self
    
            return lambda *args, **kwargs: self(instance, *args, **kwargs)
    
        def __call_instance(self, *args, **kwargs):
            result = None
    
            for _ in range(self.times):
                result = self.func(*args, **kwargs)
    
            return result

Ý tưởng chính:
    
    
    Repeat(3)
    
    ↓
    
    object
    
    ↓
    
    object(func)
    
    ↓
    
    callable object

> Trong thực tế, class-based factory thường được cài đặt phức tạp hơn để hỗ trợ cả function và method.

* * *

# 11\. Factory trả về Factory

Hoàn toàn hợp lệ.
    
    
    def config(level):
    
        def logger(show_args):
    
            def decorator(func):
    
                ...
    
            return decorator
    
        return logger

Ví dụ
    
    
    @config("DEBUG")(True)

Ít dùng nhưng Python cho phép.

* * *

# 12\. Decorator Factory kết hợp Stacking
    
    
    @retry(times=3)
    @logger(level="INFO")
    def download():
        ...

Python dịch
    
    
    download = retry(
        times=3
    )(
        logger(
            level="INFO"
        )(
            download
        )
    )

Nếu viết từng bước
    
    
    logger_decorator = logger(level="INFO")
    
    retry_decorator = retry(times=3)
    
    download = logger_decorator(download)
    
    download = retry_decorator(download)

Đây là cách bạn nên "dịch trong đầu" khi đọc source code framework.

* * *

# 13\. Ví dụ thực tế - Permission
    
    
    from functools import wraps
    
    CURRENT_ROLE = "admin"
    
    
    def permission(*roles):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                if CURRENT_ROLE not in roles:
                    raise PermissionError
    
                return func(*args, **kwargs)
    
            return wrapper
    
        return decorator

Sử dụng
    
    
    @permission(
        "admin",
        "manager"
    )
    def delete():
        print("Deleted")

* * *

# 14\. Ví dụ thực tế - Timeout
    
    
    from functools import wraps
    import time
    
    
    def timeout(seconds):
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                print(
                    f"Timeout = {seconds}"
                )
    
                return func(*args, **kwargs)
    
            return wrapper
    
        return decorator

Sau này khi học Threading và AsyncIO, bạn có thể thay phần `print` bằng logic timeout thực sự.

* * *

# 15\. Ví dụ thực tế - Benchmark
    
    
    from functools import wraps
    import time
    
    
    def benchmark(*, rounds=5):
    
        if rounds <= 0:
            raise ValueError
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                total = 0
    
                result = None
    
                for _ in range(rounds):
    
                    start = time.perf_counter()
    
                    result = func(
                        *args,
                        **kwargs
                    )
    
                    total += (
                        time.perf_counter()
                        - start
                    )
    
                print(
                    "Average:",
                    total / rounds
                )
    
                return result
    
            return wrapper
    
        return decorator

* * *

# 16\. Ví dụ thực tế - Registry

Đây là mẫu mà Flask, Click, Typer đều dùng.
    
    
    COMMANDS = {}
    
    
    def command(name):
    
        def decorator(func):
    
            COMMANDS[name] = func
    
            return func
    
        return decorator
    
    
    @command("start")
    def start():
        print("Start")
    
    
    @command("stop")
    def stop():
        print("Stop")

Sau khi import
    
    
    print(COMMANDS)

Kết quả
    
    
    {
        "start": start,
        "stop": stop
    }

Đây là ý tưởng cốt lõi của:

  * Flask Route 
  * Click Command 
  * Celery Task 
  * Dramatiq Actor 



* * *

# 17\. Mẫu chuyên nghiệp

Đây là template bạn nên ghi nhớ.
    
    
    from functools import wraps
    
    
    def factory(
        *,
        option=True,
        timeout=5
    ):
    
        if timeout <= 0:
            raise ValueError
    
        def decorator(func):
    
            @wraps(func)
            def wrapper(*args, **kwargs):
    
                # Before
    
                result = func(
                    *args,
                    **kwargs
                )
    
                # After
    
                return result
    
            return wrapper
    
        return decorator

Đây là mẫu xuất hiện rất nhiều trong các thư viện Python.

* * *

# 18\. Những lỗi phổ biến

## Sai 1

Không validate tham số.
    
    
    @repeat(-10)

Lỗi chỉ xuất hiện khi chạy, thay vì phát hiện ngay lúc import.

* * *

## Sai 2

Không dùng `@wraps`.

Mất metadata của hàm gốc.

* * *

## Sai 3

Dùng quá nhiều positional argument.

Khó đọc:
    
    
    @logger(
        "INFO",
        True,
        False,
        10
    )

Nên dùng:
    
    
    @logger(
        level="INFO",
        show_time=True,
        show_args=False,
        timeout=10
    )

* * *

## Sai 4

Viết một decorator làm quá nhiều việc.

Thay vì:

  * logger 
  * timer 
  * retry 
  * cache 



gộp thành một decorator khổng lồ, hãy tách nhỏ và dùng **Decorator Stacking**.

* * *

# Best Practices

✅ Dùng keyword-only argument (`*`) cho các tham số cấu hình.

✅ Validate tham số ngay trong factory.

✅ Luôn dùng `@wraps`.

✅ Mỗi decorator chỉ nên có một trách nhiệm.

✅ Thiết kế API rõ ràng, dễ đọc.

* * *

# Tổng kết buổi 12

Bạn cần ghi nhớ:

  1. Decorator Factory có thể nhận nhiều tham số cấu hình. 
  2. Nên dùng keyword-only argument để API rõ ràng. 
  3. Validate tham số ngay trong factory. 
  4. Kết hợp `@wraps` để giữ metadata. 
  5. Có thể kết hợp nhiều factory bằng Decorator Stacking. 
  6. Đây là mô hình được dùng phổ biến trong Flask, FastAPI, Click, Celery và Dramatiq. 



* * *

# Bài tập

## Bài 1

Viết decorator:
    
    
    @retry(
        times=5,
        delay=1
    )
    def download():
        ...

Yêu cầu:

  * Validate `times > 0`. 
  * Validate `delay >= 0`. 
  * Dùng `@wraps`. 



* * *

## Bài 2

Viết decorator:
    
    
    @benchmark(
        rounds=10
    )
    def sort_data():
        ...

Yêu cầu:

  * Đo thời gian trung bình. 
  * In số vòng chạy. 
  * Trả về kết quả của lần chạy cuối. 



* * *

## Bài 3

Xây dựng một mini framework đăng ký lệnh:
    
    
    @command("start")
    def start():
        ...
    
    @command("stop")
    def stop():
        ...

Yêu cầu:

  * Lưu tất cả hàm vào một dictionary `COMMANDS`. 
  * Viết hàm `run_command(name)` để tìm và thực thi lệnh theo tên. 
  * Dùng `@wraps` nếu bạn bọc thêm logic vào các command. 



* * *

# Chuẩn bị cho buổi 13

Ở **buổi 13** , chúng ta sẽ học **Method Decorator** – một chủ đề rất quan trọng nhưng cũng dễ gây nhầm lẫn. Bạn sẽ hiểu:

  * Vì sao decorator cho method khác decorator cho function. 
  * Vai trò của `self` và `cls`. 
  * Decorator hoạt động với instance method, `@classmethod` và `@staticmethod`. 
  * Thứ tự giữa `@classmethod`, `@staticmethod` và decorator tự viết. 
  * Cơ chế descriptor đứng sau việc gọi method trong Python. 



Đây là nền tảng để hiểu cách Django ORM, Flask views và nhiều framework Python triển khai các decorator trên phương thức của lớp.

