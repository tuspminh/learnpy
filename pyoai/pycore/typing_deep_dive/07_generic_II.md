Version:0.9 StartHTML:0000000105 EndHTML:0000029740 StartFragment:0000000141 EndFragment:0000029704 

# Typing Deep Dive – Buổi 7

# Generic Deep Dive (Phần 2) – Type Inference, Generic Method, Generic Dataclass và Generic Protocol

> Đây là buổi học giúp bạn chuyển từ **"biết Generic"** sang **"làm chủ Generic"**.
> 
> Sau buổi này, bạn sẽ hiểu cách các framework như **SQLAlchemy 2.0** , **Pydantic** , **FastAPI** và các thư viện hiện đại sử dụng Generic để xây dựng API mạnh mẽ.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ hiểu:

  * Type Inference hoạt động như thế nào.
  * Generic Method.
  * Generic Dataclass.
  * Generic Type Alias.
  * Generic Protocol.
  * Generic Repository thực tế.
  * Các lỗi thường gặp khi dùng Generic.



* * *

# 1\. Ôn lại TypeVar
    
    
    from typing import TypeVar
    
    T = TypeVar("T")

`T` không phải biến.

Nó là **biến đại diện cho một kiểu**.

Ví dụ
    
    
    def identity(value: T) -> T:
        return value

Nếu gọi
    
    
    identity(100)

IDE suy luận
    
    
    T = int

Nếu gọi
    
    
    identity("Python")

IDE suy luận
    
    
    T = str

Đây gọi là

> **Type Inference**

* * *

# 2\. Type Inference hoạt động như thế nào?

Ví dụ
    
    
    T = TypeVar("T")
    
    
    def echo(value: T) -> T:
        return value

Gọi
    
    
    x = echo(10)

IDE suy luận:
    
    
    value = int
    
    ↓
    
    T = int
    
    ↓
    
    return = int

* * *

Nếu
    
    
    book = Book()
    
    x = echo(book)

IDE:
    
    
    Book
    
    ↓
    
    T = Book

Không cần khai báo
    
    
    echo[Book](...)

Python tự suy luận.

* * *

# 3\. Generic Method

Không chỉ class mới Generic.

Method cũng Generic.

Ví dụ
    
    
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Converter:
    
        def convert(
            self,
            value: T
        ) -> T:
            return value

Mỗi lần gọi
    
    
    convert()

IDE lại suy luận
    
    
    T

mới.

* * *

Ví dụ
    
    
    converter = Converter()
    
    converter.convert(10)
    
    converter.convert("Python")
    
    converter.convert(Book())

Đều hợp lệ.

* * *

# 4\. Generic Method trong Generic Class

Ví dụ
    
    
    from typing import Generic from typing import TypeVar
    
    T = TypeVar("T")
    U = TypeVar("U")
    
    
    class Box(Generic[T]):
    
        def __init__(self, value: T):
            self.value = value
    
        def map(
            self,
            func
        ) -> U:
            ...

Ở đây
    
    
    Class
    
    ↓
    
    Generic[T]
    
    Method
    
    ↓
    
    Generic[U]

Hai TypeVar độc lập.

Đây là nền tảng của các thư viện xử lý dữ liệu (functional programming).

* * *

# 5\. Generic Dataclass

Ví dụ
    
    
    from dataclasses import dataclass from typing import Generic from typing import TypeVar
    
    T = TypeVar("T")
    
    
    @dataclass class Result(Generic[T]):
        value: T

* * *

Sử dụng
    
    
    Result[int](100)

IDE
    
    
    value
    
    ↓
    
    int

* * *
    
    
    Result[str]("Hello")

↓
    
    
    value
    
    ↓
    
    str

* * *

Đây là kỹ thuật rất phổ biến trong

  * API Response
  * Event
  * Message Queue
  * DTO



* * *

# 6\. Ví dụ thực tế
    
    
    @dataclass class ApiResponse(Generic[T]):
    
        success: bool
    
        data: T

Có thể dùng
    
    
    ApiResponse[User]

hoặc
    
    
    ApiResponse[Book]

Không cần tạo
    
    
    UserResponse
    
    BookResponse
    
    NovelResponse

* * *

# 7\. Generic Type Alias

Python 3.12
    
    
    type Cache[T] = dict[
        str,
        T
    ]

Ví dụ
    
    
    user_cache: Cache[User]

↓
    
    
    dict[
        str,
        User
    ]

* * *

Hoặc
    
    
    type Page[T] = list[T]

Sử dụng
    
    
    Page[int]
    
    Page[str]
    
    Page[Book]

* * *

# 8\. Generic Protocol

Đây là phần cực kỳ mạnh.

Ví dụ
    
    
    from typing import Protocol from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Serializer(
        Protocol[T]
    ):
    
        def dump(
            self,
            obj: T
        ) -> str:
            ...

* * *

Có thể triển khai
    
    
    class UserSerializer:
    
        def dump(
            self,
            obj: User
        ) -> str:
            ...

IDE hiểu
    
    
    T
    
    ↓
    
    User

* * *

# 9\. Generic Repository thực tế

Ví dụ
    
    
    from typing import Generic from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Repository(
        Generic[T]
    ):
    
        def save(
            self,
            obj: T
        ):
            ...
    
        def get(
            self,
            id: int
        ) -> T:
            ...

* * *

Sử dụng
    
    
    user_repo = Repository[User]()

↓
    
    
    save()
    
    ↓
    
    User

* * *
    
    
    novel_repo = Repository[Novel]()

↓
    
    
    Novel

* * *

Đây chính là

Repository Pattern

trong các dự án lớn.

* * *

# 10\. Generic Service
    
    
    T = TypeVar("T")
    
    
    class Service(
        Generic[T]
    ):
    
        def __init__(
            self,
            repo: Repository[T]
        ):
            self.repo = repo
    
        def get(
            self,
            id: int
        ) -> T:
    
            return self.repo.get(id)

* * *

Có thể dùng
    
    
    Service[User]

Hoặc
    
    
    Service[Book]

Không cần viết lại logic.

* * *

# 11\. Generic Factory

Ví dụ
    
    
    T = TypeVar("T")
    
    
    class Factory(
        Generic[T]
    ):
    
        def create(self) -> T:
            ...

Đây là cách nhiều framework triển khai Dependency Injection.

* * *

# 12\. Generic Event

Ví dụ
    
    
    @dataclass class Event(Generic[T]):
    
        payload: T

Có thể có
    
    
    Event[User]
    
    Event[Book]
    
    Event[Novel]

Rất phù hợp với hệ thống Event Bus.

* * *

# 13\. TypeVar không phải object

Sai lầm phổ biến
    
    
    print(T)

Không có ý nghĩa trong logic chương trình.

`TypeVar` chỉ dành cho trình kiểm tra kiểu.

Nó không mang theo giá trị kiểu cụ thể khi chương trình chạy.

* * *

# 14\. Lỗi phổ biến số 1

Sai
    
    
    def first(
        items: list[T]
    ):
        return items[0]

Không khai báo kiểu trả về.

Đúng
    
    
    def first(
        items: list[T]
    ) -> T:
    
        return items[0]

* * *

# 15\. Lỗi phổ biến số 2

Sai
    
    
    T = TypeVar("T")
    
    
    def copy(
        value: T
    ) -> int:
        ...

Đầu vào
    
    
    T

Nhưng đầu ra
    
    
    int

Không còn Generic.

Nếu hàm có mục tiêu giữ nguyên kiểu dữ liệu, kiểu trả về cũng nên là `T`.

* * *

# 16\. Lỗi phổ biến số 3

Viết
    
    
    Repository

thay vì
    
    
    Repository[T]

Điều này làm mất thông tin kiểu.

IDE không thể suy luận.

* * *

# 17\. Generic trong dự án crawler

Ví dụ
    
    
    Novel
    
    Chapter
    
    Author
    
    Category

Ta không cần
    
    
    NovelRepository
    
    AuthorRepository
    
    CategoryRepository

Mà chỉ cần
    
    
    Repository[T]

Tương tự
    
    
    Service[T]
    
    
    Cache[T]
    
    
    ApiResponse[T]
    
    
    Event[T]

Toàn bộ dự án sẽ nhất quán.

* * *

# 18\. Tư duy Generic

Khi viết một class, hãy tự hỏi:

> **Logic này có phụ thuộc vào kiểu dữ liệu cụ thể không?**

Nếu **không** , hãy cân nhắc Generic.

Ví dụ:

  * `Stack[T]` ✔
  * `Queue[T]` ✔
  * `Repository[T]` ✔
  * `Cache[T]` ✔
  * `ApiResponse[T]` ✔



Ngược lại, nếu class chỉ dành riêng cho `Novel` và chứa các quy tắc nghiệp vụ đặc thù (ví dụ tính trạng thái hoàn thành, xử lý chương truyện), thì không nên ép Generic chỉ để "tổng quát hóa".

* * *

# 19\. Best Practices

✔ Dùng Generic để loại bỏ mã lặp.

✔ Kết hợp Generic với `dataclass`, `Protocol` và các mẫu thiết kế (Repository, Service, Factory...).

✔ Để trình kiểm tra kiểu suy luận kiểu tự động, chỉ chỉ định `Repository[User]`, `Stack[int]`... khi tạo đối tượng hoặc khai báo biến.

✔ Chỉ dùng Generic khi hành vi thực sự độc lập với kiểu dữ liệu.

❌ Không dùng Generic chỉ vì "thấy hiện đại". Generic làm API mạnh hơn, nhưng cũng phức tạp hơn; hãy áp dụng khi nó mang lại lợi ích rõ ràng.

* * *

# Bài tập

## Bài 1

Viết Generic Dataclass
    
    
    Box[T]

Có
    
    
    value: T

Thử
    
    
    Box[int]
    
    Box[str]
    
    Box[float]

* * *

## Bài 2

Viết
    
    
    ApiResponse[T]

Có
    
    
    success: bool
    
    data: T

Tạo
    
    
    ApiResponse[User]
    
    ApiResponse[Book]

* * *

## Bài 3

Viết
    
    
    Repository[T]

Có các phương thức
    
    
    save(obj: T)
    
    get(id: int) -> T
    
    delete(id: int)

Sau đó tạo:
    
    
    user_repo = Repository[User]()
    book_repo = Repository[Book]()

Quan sát IDE tự suy luận kiểu của `save()` và `get()`.

* * *

# Tổng kết Buổi 6–7

Đến đây bạn đã nắm được nền tảng Generic:

  * `TypeVar`
  * Generic Function
  * Generic Class
  * Generic Method
  * Generic Dataclass
  * Generic Protocol
  * Generic Type Alias
  * Type Inference
  * Generic Repository
  * Generic Service



Đây là khoảng **60–70%** kiến thức Generic mà các lập trình viên Python sử dụng hằng ngày.

**Buổi 8** sẽ bước vào phần khó nhất của Generic:

  * `TypeVar(bound=...)`
  * Constrained `TypeVar`
  * Covariance (`covariant=True`)
  * Contravariance (`contravariant=True`)
  * Invariance
  * Tại sao `list[Dog]` **không phải** là `list[Animal]`
  * Vì sao `Sequence` lại hỗ trợ covariance còn `list` thì không



Đây là những khái niệm quan trọng để hiểu thiết kế của `typing` và đọc mã nguồn của các thư viện Python hiện đại.

