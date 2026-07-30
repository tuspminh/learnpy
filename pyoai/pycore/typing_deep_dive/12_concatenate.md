Version:0.9 StartHTML:0000000105 EndHTML:0000028098 StartFragment:0000000141 EndFragment:0000028062 

# Typing Deep Dive – Buổi 12

# `Concatenate` Deep Dive (PEP 612) – Typing cho Decorator thay đổi tham số

> ⭐⭐⭐⭐⭐ **Đây là phần nâng cao của**`**ParamSpec**`**.**
> 
> Nếu `ParamSpec` giúp **giữ nguyên** danh sách tham số của hàm,  
> thì `**Concatenate**` giúp **thêm** , **chèn** hoặc **thay đổi** danh sách tham số đó một cách an toàn về kiểu.
> 
> Đây là kỹ thuật được sử dụng trong:
> 
>   * FastAPI Dependency Injection
>   * SQLAlchemy Session
>   * Django Middleware
>   * Flask Context
>   * Logging Framework
>   * Authentication
>   * Authorization
>   * RPC Framework
> 


* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * `Concatenate` là gì
  * Khi nào dùng `Concatenate`
  * Decorator thêm tham số
  * Inject Context
  * Inject Logger
  * Inject Database Session
  * Middleware typing
  * Dependency Injection typing



* * *

# 1\. Ôn lại ParamSpec

Ta có decorator:
    
    
    from collections.abc import Callable from typing import ParamSpec, TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    
    def logger(
        func: Callable[P, R]
    ) -> Callable[P, R]:
        ...

Điều này có nghĩa:
    
    
    Input
    
    ↓
    
    Callable[P, R]
    
    ↓
    
    Output
    
    ↓
    
    Callable[P, R]

Không thay đổi tham số.

* * *

# 2\. Bài toán

Giả sử
    
    
    def save_user(
        name: str
    ):
        ...

Ta muốn decorator
    
    
    @inject_db

Sau khi decorate

Runtime thực sự gọi
    
    
    save_user(
        session,
        name
    )

Có nghĩa là decorator tự động thêm
    
    
    DatabaseSession

làm tham số đầu tiên.

* * *

# 3\. Callable không làm được
    
    
    Callable[P, R]

Không thể nói

> "Thêm một Session vào đầu danh sách tham số."

Đó là lý do có
    
    
    Concatenate

* * *

# 4\. Import
    
    
    from typing import Concatenate

* * *

# 5\. Cú pháp
    
    
    Callable[
        Concatenate[
            Session,
            P
        ],
        R
    ]

Ý nghĩa
    
    
    Function
    
    ↓
    
    (Session, P...)
    
    ↓
    
    R

* * *

# 6\. Ví dụ đầu tiên

Giả sử
    
    
    class Session:
        ...

Decorator
    
    
    from collections.abc import Callable from typing import Concatenate from typing import ParamSpec from typing import TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    
    def inject_session(
        func: Callable[
            Concatenate[
                Session,
                P
            ],
            R
        ]
    ):
        ...

Nghĩa là

Hàm gốc phải có
    
    
    Session
    
    ↓
    
    tham số đầu tiên

* * *

# 7\. Runtime

Ví dụ
    
    
    def save(
        session: Session,
        name: str
    ):
        ...

Decorator
    
    
    @inject_session

Người dùng

chỉ gọi
    
    
    save("Alice")

Decorator

tự thêm
    
    
    Session()

↓
    
    
    save(
        Session(),
        "Alice"
    )

* * *

# 8\. Ví dụ hoàn chỉnh
    
    
    from collections.abc import Callable from functools import wraps from typing import Concatenate from typing import ParamSpec from typing import TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    
    class Session:
        pass
    
    
    def inject_session(
        func: Callable[
            Concatenate[
                Session,
                P
            ],
            R
        ]
    ) -> Callable[P, R]:
    
        @wraps(func)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
    
            session = Session()
    
            return func(
                session,
                *args,
                **kwargs
            )
    
        return wrapper

Đây là mẫu rất phổ biến trong Dependency Injection.

* * *

# 9\. IDE hiểu gì?

Nếu
    
    
    @inject_session def save(
        session: Session,
        name: str
    ):
        ...

Người dùng
    
    
    save("Alice")

IDE

↓
    
    
    name:str
    
    ↓
    
    OK

Không cần truyền Session.

* * *

# 10\. Inject Logger
    
    
    class Logger:
    
        def info(
            self,
            msg: str
        ):
            ...

Decorator
    
    
    Callable[
        Concatenate[
            Logger,
            P
        ],
        R
    ]

Runtime

↓
    
    
    func(
        logger,
        *args,
        **kwargs
    )

* * *

# 11\. Inject Context
    
    
    class Context:
    
        user: str
    
        ip: str

Decorator

↓
    
    
    Callable[
        Concatenate[
            Context,
            P
        ],
        R
    ]

Runtime

↓
    
    
    context = Context()
    
    func(
        context,
        *args,
        **kwargs
    )

* * *

# 12\. Inject Request

FastAPI

tư duy tương tự
    
    
    Request

↓

Inject

↓

Endpoint
    
    
    def endpoint(
        request,
        ...
    )

`Concatenate` cho phép mô tả chính xác kiểu của mẫu thiết kế này.

* * *

# 13\. Middleware

Ví dụ
    
    
    def middleware(
        func
    ):
        ...

Decorator

thêm
    
    
    Request

↓
    
    
    handler(
        request,
        ...
    )

Typing

↓
    
    
    Callable[
        Concatenate[
            Request,
            P
        ],
        R
    ]

* * *

# 14\. Generic Dependency Injection
    
    
    class Database:
        ...

Decorator
    
    
    Callable[
        Concatenate[
            Database,
            P
        ],
        R
    ]

Có thể inject
    
    
    Database
    
    Logger
    
    Config
    
    Cache
    
    Redis
    
    Session

* * *

# 15\. Nhiều tham số

Ví dụ
    
    
    Callable[
        Concatenate[
            Session,
            Logger,
            P
        ],
        R
    ]

Có nghĩa
    
    
    Function
    
    ↓
    
    Session
    
    ↓
    
    Logger
    
    ↓
    
    P...
    
    ↓
    
    Return

* * *

# 16\. Ví dụ thực tế
    
    
    def download(
        session,
        logger,
        url,
        timeout
    ):
        ...

Decorator

↓

Người dùng
    
    
    download(
        url,
        timeout
    )

Decorator tự thêm
    
    
    Session()
    
    Logger()

* * *

# 17\. Crawler Project

Ví dụ
    
    
    def fetch(
        client,
        url
    ):
        ...

Decorator

↓

Inject
    
    
    HttpClient

Người dùng
    
    
    fetch(url)

Decorator

↓
    
    
    fetch(
        client,
        url
    )

* * *

# 18\. SQLAlchemy

Rất nhiều project

có
    
    
    Session

Decorator

↓
    
    
    @transaction

Runtime

↓
    
    
    session = Session()
    
    func(
        session,
        ...
    )

Ý tưởng typing tương tự như ví dụ với `Concatenate`.

* * *

# 19\. So sánh

## ParamSpec
    
    
    Callable[
        P,
        R
    ]

↓

Không đổi tham số.

* * *

## Concatenate
    
    
    Callable[
        Concatenate[
            Session,
            P
        ],
        R
    ]

↓

Thêm
    
    
    Session

vào đầu danh sách tham số.

* * *

# 20\. Những hạn chế

`Concatenate`

chỉ thêm tham số

ở **đầu** danh sách.

Không thể
    
    
    thêm giữa
    
    hoặc
    
    thêm cuối

Đây là giới hạn thiết kế của PEP 612.

* * *

# 21\. Best Practices

✔ Dùng `ParamSpec` khi decorator giữ nguyên chữ ký.

✔ Dùng `Concatenate` khi decorator tự động chèn tham số vào đầu.

✔ Kết hợp với `functools.wraps`.

✔ Áp dụng cho Dependency Injection, Middleware và Context Injection.

❌ Không dùng `Concatenate` nếu decorator thay đổi chữ ký theo cách phức tạp hơn (ví dụ bỏ bớt hoặc đổi vị trí tham số). Khi đó có thể cần thiết kế API khác.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections.abc import Callable from functools import wraps from typing import Concatenate, ParamSpec, TypeVar
    
    P = ParamSpec("P")
    R = TypeVar("R")
    
    
    class Logger:
        def info(self, msg: str) -> None:
            print(msg)
    
    
    def inject_logger(
        func: Callable[Concatenate[Logger, P], R],
    ) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            logger = Logger()
            return func(logger, *args, **kwargs)
    
        return wrapper
    
    
    @inject_logger def greet(logger: Logger, name: str) -> None:
        logger.info(f"Hello {name}")
    
    
    greet("Alice")

Người dùng chỉ truyền:
    
    
    greet("Alice")

Decorator sẽ tự tạo `Logger` và gọi:
    
    
    greet(Logger(), "Alice")

* * *

# Bài tập

## Bài 1

Viết:
    
    
    class Logger:
        ...

Tạo decorator:
    
    
    @inject_logger

Sử dụng `Concatenate`.

* * *

## Bài 2

Viết:
    
    
    class Session:
        ...

Tạo:
    
    
    @transaction

Inject `Session` vào đầu tham số.

* * *

## Bài 3

Áp dụng cho dự án crawler:

Tạo:
    
    
    class HttpClient:
        ...

Decorator:
    
    
    @inject_client

để các hàm:
    
    
    def download(
        client: HttpClient,
        url: str,
    ) -> str:
        ...

có thể được gọi đơn giản:
    
    
    download("https://example.com")

mà vẫn giữ type hint chính xác.

* * *

# Tổng kết

Sau 12 buổi, bạn đã nắm được gần như toàn bộ nền tảng hiện đại của `typing`:

  * Type Hint
  * Union / Optional / Literal
  * Any / object / Never
  * Type Alias
  * Generic
  * TypeVar
  * Self
  * Callable
  * ParamSpec
  * Concatenate



Đây là khoảng **85–90%** kiến thức `typing` mà các lập trình viên Python chuyên nghiệp sử dụng hằng ngày.

**Buổi 13** sẽ bắt đầu với nhóm chủ đề nâng cao còn lại:

  * `TypeGuard` (PEP 647)
  * `TypeIs` (PEP 742, Python 3.13+)
  * Type Narrowing
  * Viết hàm kiểm tra kiểu mà IDE có thể hiểu



Đây là nền tảng để xây dựng các API kiểm tra dữ liệu và parser có type-safe rất mạnh.

