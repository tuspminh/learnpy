Version:0.9 StartHTML:0000000105 EndHTML:0000026703 StartFragment:0000000141 EndFragment:0000026667 

# Typing Deep Dive – Buổi 11

# `ParamSpec` Deep Dive (PEP 612) – Typing cho Decorator và Higher-Order Function

> ⭐⭐⭐⭐⭐ **Đây là một trong những PEP quan trọng nhất của Python Typing hiện đại.**
> 
> Trước Python 3.10, việc viết **decorator có type hint chính xác gần như không thể**.
> 
> `ParamSpec` ra đời để giải quyết vấn đề đó.
> 
> Các framework sử dụng rất nhiều:
> 
>   * FastAPI
>   * Typer
>   * Click
>   * Pydantic
>   * SQLAlchemy
>   * Django
>   * pytest
>   * functools
> 


* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * ParamSpec là gì
  * Tại sao Callable chưa đủ
  * Decorator đúng chuẩn
  * args / kwargs typing
  * Generic Function với ParamSpec
  * Factory Decorator
  * Logging Decorator
  * Timing Decorator



* * *

# 1\. Bài toán

Ta muốn viết decorator
    
    
    def logger(func):
        ...

để dùng
    
    
    @logger def add(a: int, b: int) -> int:
        return a + b

* * *

# 2\. Decorator đơn giản
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
            print("Run")
            return func(*args, **kwargs)
    
        return wrapper

Runtime chạy tốt.

Nhưng IDE?

Không biết
    
    
    wrapper
    
    ↓
    
    nhận gì?
    
    ↓
    
    trả gì?

Autocomplete mất.

* * *

# 3\. Dùng Callable

Ta thử
    
    
    from collections.abc import Callable
    
    def logger(
        func: Callable
    ):
        ...

Vẫn quá chung.

* * *

# 4\. Callable với TypeVar

Ví dụ
    
    
    R = TypeVar("R")
    
    def logger(
        func: Callable[..., R]
    ) -> Callable[..., R]:
        ...

Ở đây
    
    
    ...
    
    ↓
    
    mọi tham số

* * *

IDE biết

Return

↓
    
    
    R

Nhưng

Không biết
    
    
    args
    
    kwargs

là gì.

* * *

# 5\. ParamSpec

Import
    
    
    from typing import ParamSpec

Tạo
    
    
    P = ParamSpec("P")

Giống
    
    
    T = TypeVar("T")

Nhưng
    
    
    TypeVar
    
    ↓
    
    Kiểu dữ liệu
    
    ParamSpec
    
    ↓
    
    Danh sách tham số

* * *

# 6\. So sánh

TypeVar
    
    
    T

↓
    
    
    int
    
    str
    
    Book

* * *

ParamSpec
    
    
    P

↓
    
    
    (int, str)
    
    ()
    
    (float)
    
    (str, int, bool)

Không phải kiểu dữ liệu.

Mà là

**toàn bộ chữ ký tham số.**

* * *

# 7\. Decorator chuẩn
    
    
    from collections.abc import Callable from typing import ParamSpec from typing import TypeVar
    
    P = ParamSpec("P")
    
    R = TypeVar("R")
    
    
    def logger(
        func: Callable[P, R]
    ) -> Callable[P, R]:
    
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            print("Run")
    
            return func(*args, **kwargs)
    
        return wrapper

Đây là mẫu decorator chuẩn.

* * *

# 8\. IDE hiểu gì?

Ví dụ
    
    
    @logger def add(
        a: int,
        b: int
    ) -> int:
        return a + b

IDE suy luận
    
    
    P
    
    ↓
    
    (int, int)
    
    R
    
    ↓
    
    int

Decorator

↓

vẫn giữ nguyên
    
    
    (int, int)
    
    ↓
    
    int

* * *

# 9\. Nếu hàm khác
    
    
    @logger def hello(
        name: str
    ) -> None:
        ...

IDE

↓
    
    
    P
    
    ↓
    
    (str)
    
    R
    
    ↓
    
    None

Decorator tự thích nghi.

* * *

# 10\. ParamSpec.args

Ví dụ
    
    
    *args: P.args

Ý nghĩa
    
    
    Toàn bộ positional arguments

* * *

Ví dụ
    
    
    add(
        1,
        2
    )

↓
    
    
    args
    
    ↓
    
    (1,2)

* * *

# 11\. ParamSpec.kwargs

Ví dụ
    
    
    **kwargs: P.kwargs

Ví dụ
    
    
    login(
        username="admin",
        password="123"
    )

↓
    
    
    kwargs
    
    ↓
    
    {
        "username":"admin",
        "password":"123"
    }

* * *

# 12\. Timing Decorator
    
    
    import time
    
    from collections.abc import Callable
    
    from typing import ParamSpec
    
    from typing import TypeVar
    
    P = ParamSpec("P")
    
    R = TypeVar("R")
    
    
    def timer(
        func: Callable[P, R]
    ) -> Callable[P, R]:
    
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            start = time.perf_counter()
    
            result = func(
                *args,
                **kwargs
            )
    
            end = time.perf_counter()
    
            print(end - start)
    
            return result
    
        return wrapper

* * *

# 13\. Logging Decorator
    
    
    def logging(
        func: Callable[P, R]
    ) -> Callable[P, R]:
    
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            print(func.__name__)
    
            return func(
                *args,
                **kwargs
            )
    
        return wrapper

* * *

# 14\. Retry Decorator
    
    
    def retry(
        func: Callable[P, R]
    ) -> Callable[P, R]:
    
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            for _ in range(3):
                try:
                    return func(
                        *args,
                        **kwargs
                    )
                except Exception:
                    pass
    
            raise RuntimeError()
    
        return wrapper

* * *

# 15\. Factory Decorator

Ví dụ
    
    
    @repeat(3)

Triển khai
    
    
    def repeat(
        times: int
    ):
        ...

Typing
    
    
    def repeat(
        times: int
    ):
    
        def decorator(
            func: Callable[P, R]
        ) -> Callable[P, R]:
    
            ...

Hai tầng
    
    
    repeat
    
    ↓
    
    decorator
    
    ↓
    
    wrapper

Đây là cấu trúc rất phổ biến.

* * *

# 16\. Generic với ParamSpec
    
    
    def execute(
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> R:
    
        return func(
            *args,
            **kwargs
        )

Ví dụ
    
    
    execute(
        add,
        1,
        2
    )

IDE

↓
    
    
    P
    
    ↓
    
    (int,int)
    
    R
    
    ↓
    
    int

* * *

# 17\. Áp dụng vào dự án crawler

Ví dụ
    
    
    def retry(
        func: Callable[P, R]
    ) -> Callable[P, R]:

Có thể dùng
    
    
    @retry def download(
        url: str,
        timeout: int
    ) -> str:
        ...

IDE vẫn biết
    
    
    download(
        url:str,
        timeout:int
    )
    
    ↓
    
    str

Không mất type.

* * *

# 18\. functools.wraps

Decorator nên luôn dùng
    
    
    from functools import wraps

Ví dụ
    
    
    from functools import wraps
    
    def logger(
        func: Callable[P, R]
    ) -> Callable[P, R]:
    
        @wraps(func)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            return func(
                *args,
                **kwargs
            )
    
        return wrapper

`wraps()` không chỉ giữ metadata (`__name__`, `__doc__`, `__module__`...) mà còn giúp nhiều công cụ introspection hoạt động chính xác hơn.

* * *

# 19\. ParamSpec vs TypeVar

TypeVar
    
    
    T

↓
    
    
    Một kiểu

* * *

ParamSpec
    
    
    P

↓
    
    
    Danh sách tham số

* * *

TypeVar
    
    
    list[T]

↓
    
    
    int
    
    str
    
    Book

* * *

ParamSpec
    
    
    Callable[P,R]

↓
    
    
    (a,b)
    
    (x)
    
    ()
    
    (*args,**kwargs)

* * *

# 20\. Khi nào dùng ParamSpec?

✔ Decorator

✔ Logging

✔ Retry

✔ Cache

✔ Memoization

✔ Authentication

✔ Authorization

✔ Transaction

✔ Event

✔ Middleware

✔ Dependency Injection

Nói ngắn gọn: **bất cứ khi nào bạn viết một hàm nhận một hàm khác và muốn giữ nguyên chữ ký của hàm đó** , hãy nghĩ đến `ParamSpec`.

* * *

# 21\. Best Practices

✔ Luôn dùng `ParamSpec` cho decorator không thay đổi tham số.

✔ Kết hợp `ParamSpec` với `TypeVar`:
    
    
    P = ParamSpec("P")
    R = TypeVar("R")

✔ Luôn dùng `functools.wraps()`.

✔ Dùng `Callable[P, R]` thay vì `Callable[..., R]` nếu muốn giữ nguyên chữ ký.

❌ Không dùng `Callable[..., Any]` nếu bạn có thể mô tả chính xác hơn bằng `ParamSpec`.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections.abc import Callable from functools import wraps from typing import ParamSpec, TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    
    def logger(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            print(f"Calling {func.__name__}")
            return func(*args, **kwargs)
    
        return wrapper
    
    
    @logger def add(a: int, b: int) -> int:
        return a + b
    
    
    result = add(2, 3)

IDE vẫn biết:
    
    
    add(a: int, b: int) -> int

mặc dù hàm đã được decorator bao bọc.

* * *

# Bài tập

## Bài 1

Viết decorator
    
    
    @timer

đo thời gian chạy của hàm.

Sử dụng:

  * `ParamSpec`
  * `TypeVar`
  * `Callable`
  * `functools.wraps`



* * *

## Bài 2

Viết decorator
    
    
    @retry(3)

Thử gọi lại tối đa 3 lần nếu hàm phát sinh ngoại lệ.

Giữ nguyên type hint của hàm gốc.

* * *

## Bài 3

Viết hàm
    
    
    from collections.abc import Callable from typing import ParamSpec, TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    def invoke(
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        ...

Thử với:

  * `add(int, int) -> int`
  * `greet(str) -> None`
  * `power(int, int = 2) -> int`



Đảm bảo IDE luôn suy luận đúng kiểu trả về.

* * *

# Tổng kết

Đến đây bạn đã làm chủ:

  * `Callable`
  * `TypeVar`
  * `ParamSpec`
  * Typing cho callback
  * Higher-order Function
  * Decorator chuẩn
  * Logging Decorator
  * Timing Decorator
  * Retry Decorator
  * Factory Decorator



Đây là nền tảng để bước sang **Buổi 12:**`**Concatenate**`**(PEP 612)** , nơi bạn sẽ học cách viết các decorator **thêm hoặc thay đổi tham số** (ví dụ tự động chèn `Request`, `Session`, `Logger`, `Context`...), một kỹ thuật được sử dụng rộng rãi trong FastAPI, dependency injection và middleware hiện đại.

