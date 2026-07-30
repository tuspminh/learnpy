Version:0.9 StartHTML:0000000105 EndHTML:0000027841 StartFragment:0000000141 EndFragment:0000027805 

# Typing Deep Dive – Buổi 10

# `Callable` Deep Dive (PEP 484) – Typing cho Function, Lambda, Callback và Higher-Order Function

> ⭐⭐⭐⭐⭐ Đây là một trong những chủ đề quan trọng nhất của `typing`.
> 
> Nếu **Generic** là nền tảng của kiểu dữ liệu, thì **Callable** là nền tảng của **Functional Programming** trong Python.
> 
> Hầu hết các thư viện lớn đều sử dụng `Callable`:
> 
>   * asyncio
>   * concurrent.futures
>   * threading
>   * click
>   * typer
>   * FastAPI
>   * SQLAlchemy events
>   * PySide6 signals/slots (callback)
>   * Decorator Framework
> 


* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Callable là gì
  * Cú pháp Callable
  * Typing cho lambda
  * Typing callback
  * Higher-order Function
  * Function Factory
  * Strategy Pattern
  * Dependency Injection bằng Callable



* * *

# 1\. Function cũng là object

Trong Python
    
    
    def hello():
        print("Hello")

Ta có thể
    
    
    print(type(hello))

Kết quả
    
    
    <class 'function'>

Function cũng là object.

Có thể

  * truyền vào hàm khác
  * lưu vào list
  * lưu vào dict
  * trả về từ hàm



* * *

# 2\. Higher-Order Function

Ví dụ
    
    
    def greet():
        print("Hello")
    
    
    def execute(func):
        func()
    
    
    execute(greet)

Ở đây
    
    
    greet
    
    ↓
    
    Function

được truyền vào
    
    
    execute()

* * *

# 3\. Vấn đề

IDE không biết
    
    
    def execute(func):
        func()

`func`

là gì?

* * *

# 4\. Callable

Import
    
    
    from collections.abc import Callable

(Từ Python 3.9+, nên ưu tiên `collections.abc.Callable`; `typing.Callable` vẫn hoạt động để tương thích.)

* * *

Viết
    
    
    from collections.abc import Callable
    
    
    def execute(
        func: Callable
    ):
        func()

Nhưng
    
    
    Callable

quá chung.

* * *

# 5\. Cú pháp đầy đủ
    
    
    Callable[
        [tham số],
        kiểu_trả_về
    ]

Ví dụ
    
    
    Callable[
        [],
        None
    ]

Có nghĩa
    
    
    Function
    
    ↓
    
    không tham số
    
    ↓
    
    return None

* * *

# 6\. Ví dụ
    
    
    from collections.abc import Callable
    
    
    def greet():
        print("Hello")
    
    
    def execute(
        func: Callable[
            [],
            None
        ]
    ):
        func()

IDE hiểu
    
    
    func
    
    ↓
    
    Function()
    
    ↓
    
    None

* * *

# 7\. Một tham số

Ví dụ
    
    
    def print_name(
        name: str
    ):
        print(name)

Typing
    
    
    Callable[
        [str],
        None
    ]

* * *

Ví dụ
    
    
    from collections.abc import Callable
    
    
    def execute(
        func: Callable[
            [str],
            None
        ]
    ):
        func("Alice")

* * *

# 8\. Hai tham số

Ví dụ
    
    
    def add(
        a: int,
        b: int
    ) -> int:
        return a + b

Typing
    
    
    Callable[
        [int, int],
        int
    ]

* * *

# 9\. Lambda

Lambda cũng là Callable.
    
    
    square = lambda x: x * x

Typing
    
    
    from collections.abc import Callable
    
    square: Callable[
        [int],
        int
    ]

* * *

# 10\. Callback

Đây là nơi Callable được dùng nhiều nhất.

Ví dụ
    
    
    from collections.abc import Callable
    
    
    def download(
        on_finish: Callable[
            [],
            None
        ]
    ):
        ...

Sau khi download
    
    
    on_finish()

* * *

Người dùng
    
    
    download(
        lambda: print("Done")
    )

IDE kiểm tra được lambda phù hợp với callback.

* * *

# 11\. Callback có dữ liệu

Ví dụ
    
    
    def download(
        callback: Callable[
            [str],
            None
        ]
    ):
        ...

Sau khi tải xong
    
    
    callback(
        "chapter.html"
    )

Người dùng
    
    
    download(
        lambda filename:
            print(filename)
    )

* * *

# 12\. Higher-order Function

Ví dụ
    
    
    from collections.abc import Callable
    
    
    def apply(
        func: Callable[
            [int],
            int
        ],
        value: int
    ) -> int:
    
        return func(value)

* * *

Sử dụng
    
    
    apply(
        lambda x: x * 2,
        5
    )

↓
    
    
    10

* * *

# 13\. Function trả về Function

Ví dụ
    
    
    from collections.abc import Callable
    
    
    def make_multiplier(
        n: int
    ) -> Callable[
        [int],
        int
    ]:
        def multiply(x: int) -> int:
            return x * n
    
        return multiply

* * *

Dùng
    
    
    double = make_multiplier(2)
    
    print(double(5))

↓
    
    
    10

* * *

# 14\. Strategy Pattern

Ví dụ
    
    
    from collections.abc import Callable
    
    Operation = Callable[
        [int, int],
        int
    ]

Hai chiến lược
    
    
    def add(a: int, b: int) -> int:
        return a + b
    
    
    def multiply(a: int, b: int) -> int:
        return a * b

Hàm dùng chiến lược
    
    
    def calculate(
        op: Operation,
        a: int,
        b: int
    ) -> int:
        return op(a, b)

* * *

# 15\. Dependency Injection

Ví dụ
    
    
    class UserService:
    
        def __init__(
            self,
            logger: Callable[
                [str],
                None
            ]
        ):
            self.logger = logger

Dùng
    
    
    service = UserService(print)

`print` phù hợp vì có thể nhận một chuỗi và không cần dùng giá trị trả về trong trường hợp này.

* * *

# 16\. Event System
    
    
    from collections.abc import Callable
    
    Listener = Callable[
        [str],
        None
    ]

Danh sách
    
    
    listeners: list[
        Listener
    ] = []

Thêm
    
    
    listeners.append(
        lambda msg:
            print(msg)
    )

Phát sự kiện
    
    
    for listener in listeners:
        listener("Hello")

* * *

# 17\. Crawler Project

Ví dụ
    
    
    ProgressCallback = Callable[
        [int],
        None
    ]

Crawler
    
    
    def crawl(
        callback: ProgressCallback
    ):
        ...

Khi crawl
    
    
    callback(50)

UI
    
    
    crawl(
        lambda percent:
            progress.setValue(percent)
    )

Đây là cách phổ biến để tách phần xử lý khỏi giao diện.

* * *

# 18\. Callable lồng nhau

Ví dụ
    
    
    Callable[
        [
            Callable[
                [int],
                int
            ]
        ],
        None
    ]

Có nghĩa
    
    
    Hàm
    
    ↓
    
    nhận
    
    1 function
    
    ↓
    
    trả None

Ví dụ
    
    
    def register(
        func: Callable[
            [int],
            int
        ]
    ):
        ...

* * *

# 19\. Callable với Generic
    
    
    from collections.abc import Callable from typing import TypeVar
    
    T = TypeVar("T")
    
    
    def process(
        func: Callable[
            [T],
            T
        ],
        value: T
    ) -> T:
    
        return func(value)

Ví dụ
    
    
    process(
        lambda x: x * 2,
        10
    )

↓
    
    
    20

Hoặc
    
    
    process(
        str.upper,
        "python"
    )

↓
    
    
    "PYTHON"

Một hàm duy nhất có thể làm việc với nhiều kiểu khác nhau nhờ `TypeVar`.

* * *

# 20\. Những hạn chế của Callable

Ví dụ
    
    
    Callable[
        [int, str],
        bool
    ]

Mô tả được:

  * số lượng tham số
  * kiểu tham số
  * kiểu trả về



Nhưng **không mô tả được** :

  * `*args`
  * `**kwargs`
  * giữ nguyên chữ ký (signature) của một hàm khác
  * decorator không thay đổi tham số



Đây là lý do Python bổ sung:

  * `ParamSpec`
  * `Concatenate`



Chúng ta sẽ học ở các buổi tiếp theo.

* * *

# 21\. Best Practices

✔ Ưu tiên `collections.abc.Callable` trong Python hiện đại.

✔ Tạo alias cho các callback dùng nhiều lần:
    
    
    from collections.abc import Callable
    
    type ProgressCallback = Callable[[int], None]

✔ Dùng `Callable` cho callback, strategy và dependency injection.

✔ Kết hợp `Callable` với `TypeVar` để viết API tổng quát.

❌ Không dùng `Callable` khi bạn cần mô tả một đối tượng có nhiều phương thức; khi đó `Protocol` thường phù hợp hơn.

* * *

# Bài tập

## Bài 1

Tạo
    
    
    Operation = Callable[
        [int, int],
        int
    ]

Viết:

  * `add`
  * `subtract`
  * `multiply`



Sau đó viết:
    
    
    def calculate(
        op: Operation,
        a: int,
        b: int
    ):
        ...

* * *

## Bài 2

Viết
    
    
    ProgressCallback = Callable[
        [int],
        None
    ]

Hàm
    
    
    def download(
        callback:
            ProgressCallback
    ):
        ...

Giả lập tiến trình:
    
    
    10
    
    20
    
    30
    
    ...
    
    100

và gọi callback mỗi lần cập nhật.

* * *

## Bài 3

Viết Generic Function
    
    
    T = TypeVar("T")
    
    
    def transform(
        func: Callable[
            [T],
            T
        ],
        value: T
    ) -> T:
        ...

Thử với:

  * `int`
  * `str`
  * `float`



Quan sát IDE suy luận kiểu trả về.

* * *

# Tổng kết

Sau buổi này bạn đã nắm được:

  * `Callable`
  * Callback
  * Lambda typing
  * Higher-order Function
  * Function Factory
  * Strategy Pattern
  * Dependency Injection với `Callable`
  * Kết hợp `Callable` và `TypeVar`



Đây là nền tảng cần thiết để bước sang phần **Decorator chuyên nghiệp**.

**Buổi 11** sẽ học `**ParamSpec**`**(PEP 612)** — một trong những tính năng mạnh nhất của `typing`. Bạn sẽ hiểu cách viết decorator mà **không làm mất chữ ký hàm** , cách bảo toàn kiểu của `*args` và `**kwargs`, và vì sao các framework hiện đại phụ thuộc rất nhiều vào `ParamSpec`.

