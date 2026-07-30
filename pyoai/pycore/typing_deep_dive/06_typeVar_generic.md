Version:0.9 StartHTML:0000000105 EndHTML:0000032466 StartFragment:0000000141 EndFragment:0000032430 

# Typing Deep Dive – Buổi 6

# Generic Programming - TypeVar và Generic (Phần 1)

> **Buổi học quan trọng nhất của khóa học**
> 
> Nếu **Protocol** là linh hồn của typing thì **Generic** chính là trái tim.
> 
> Hầu hết các framework hiện đại đều dùng Generic:
> 
>   * SQLAlchemy 2.0
>   * Pydantic
>   * FastAPI
>   * Django
>   * asyncio
>   * collections
>   * Repository Pattern
>   * Dependency Injection
>   * Event Bus
>   * Plugin System
> 


* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu

  * Generic là gì
  * Generic giải quyết vấn đề gì
  * TypeVar
  * Generic Function
  * Generic Class
  * Generic Collection
  * Tư duy lập trình Generic



* * *

# 1\. Generic là gì?

Hãy xem ví dụ.

Ta muốn viết hàm lấy phần tử đầu tiên.

Cho list int
    
    
    def first(items: list[int]) -> int:
        return items[0]

Dùng
    
    
    numbers = [1, 2, 3]
    
    print(first(numbers))

Không có vấn đề.

* * *

Nhưng bây giờ
    
    
    names = [
        "Alice",
        "Bob",
        "Tom"
    ]

Muốn dùng
    
    
    first(names)

Không được.

IDE báo
    
    
    Expected list[int]
    
    Got list[str]

Ta phải viết thêm
    
    
    def first_str(
        items: list[str]
    ) -> str:
        return items[0]

* * *

Rồi lại
    
    
    Book
    
    
    def first_book(
        items: list[Book]
    ) -> Book:
        return items[0]

* * *

Rồi
    
    
    User
    
    
    def first_user(
        items: list[User]
    ) -> User:
        return items[0]

* * *

Bạn sẽ phát hiện

Code giống hệt nhau.

Chỉ khác kiểu.

Đây chính là lúc Generic xuất hiện.

* * *

# 2\. TypeVar

Generic bắt đầu bằng
    
    
    from typing import TypeVar

Tạo một biến kiểu
    
    
    T = TypeVar("T")

Đây KHÔNG phải biến runtime.

Nó là

> Type Variable

* * *

Ví dụ
    
    
    from typing import TypeVar
    
    T = TypeVar("T")

Có thể hiểu
    
    
    T
    
    ↓
    
    Một kiểu bất kỳ

* * *

# 3\. Generic Function đầu tiên
    
    
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    def first(
        items: list[T]
    ) -> T:
        return items[0]

Đây là Generic Function.

* * *

# 4\. IDE suy luận kiểu

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    x = first(numbers)

IDE hiểu
    
    
    list[int]
    
    ↓
    
    T = int
    
    ↓
    
    return int

Nên
    
    
    x
    
    ↓
    
    int

* * *

Nếu
    
    
    names = [
        "Alice",
        "Bob"
    ]
    
    name = first(names)

IDE suy luận
    
    
    T
    
    ↓
    
    str

Return
    
    
    str

* * *

Nếu
    
    
    books: list[Book]
    
    book = first(books)

IDE hiểu
    
    
    Book

Hoàn toàn tự động.

* * *

# 5\. Đây là sức mạnh của Generic

Một hàm
    
    
    first()

Có thể làm việc với
    
    
    int
    
    str
    
    Book
    
    User
    
    Novel
    
    Chapter
    
    Image
    
    ...

Không cần viết lại.

* * *

# 6\. TypeVar hoạt động như thế nào?

Ví dụ
    
    
    T = TypeVar("T")

IDE tưởng tượng
    
    
    int
    
    ↓
    
    T = int

Sau đó
    
    
    first([1, 2, 3])

Biến thành
    
    
    def first(
        items: list[int]
    ) -> int:
        ...

* * *

Nếu
    
    
    first(["A"])

IDE tưởng tượng
    
    
    def first(
        items: list[str]
    ) -> str:
        ...

* * *

Thực tế

Python không sinh code mới.

Chỉ là

Static Type Checker

suy luận.

* * *

# 7\. Generic với nhiều tham số

Ví dụ
    
    
    from typing import TypeVar
    
    K = TypeVar("K")
    
    V = TypeVar("V")

Viết
    
    
    def get_first_item(
        data: dict[K, V]
    ) -> tuple[K, V]:
    
        return next(
            iter(data.items())
        )

Ví dụ
    
    
    scores = {
        "Alice": 90
    }
    
    k, v = get_first_item(scores)

IDE hiểu
    
    
    K
    
    ↓
    
    str
    
    V
    
    ↓
    
    int

* * *

# 8\. Generic Identity Function

Ví dụ
    
    
    T = TypeVar("T")
    
    
    def identity(
        value: T
    ) -> T:
        return value

Dùng
    
    
    identity(10)

↓
    
    
    int

* * *
    
    
    identity("Python")

↓
    
    
    str

* * *
    
    
    identity(Book())

↓
    
    
    Book

* * *

# 9\. Generic Class

Ví dụ
    
    
    from typing import Generic from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Box(
        Generic[T]
    ):
        ...

Đây là Generic Class.

* * *

Thêm constructor
    
    
    class Box(
        Generic[T]
    ):
    
        def __init__(
            self,
            value: T
        ):
            self.value = value

* * *

Dùng
    
    
    box = Box(10)

IDE hiểu
    
    
    Box[int]

* * *
    
    
    box = Box("Python")

↓
    
    
    Box[str]

* * *

# 10\. IDE theo dõi toàn bộ kiểu
    
    
    box = Box(10)
    
    value = box.value

IDE biết
    
    
    value
    
    ↓
    
    int

* * *

Nếu
    
    
    box = Box(Book())

↓
    
    
    value
    
    ↓
    
    Book

* * *

# 11\. Generic Repository

Đây là ví dụ cực kỳ quan trọng.
    
    
    class Repository:
    
        def get(self):
            ...

Không biết
    
    
    get()
    
    ↓
    
    trả về gì?

* * *

Ta dùng Generic
    
    
    T = TypeVar("T")
    
    
    class Repository(
        Generic[T]
    ):
    
        def get(
            self,
            id: int
        ) -> T:
            ...

* * *

Sử dụng
    
    
    user_repo = Repository[User]()

IDE hiểu
    
    
    get()
    
    ↓
    
    User

* * *
    
    
    book_repo = Repository[Book]()

↓
    
    
    Book

* * *

Không cần tạo
    
    
    UserRepository
    
    BookRepository
    
    NovelRepository
    
    ChapterRepository

Nếu logic giống nhau.

* * *

# 12\. Generic Stack

Ví dụ
    
    
    from typing import Generic from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Stack(
        Generic[T]
    ):
    
        def __init__(self):
            self.items: list[T] = []
    
        def push(
            self,
            item: T
        ):
            self.items.append(item)
    
        def pop(self) -> T:
            return self.items.pop()

* * *

Dùng
    
    
    stack = Stack[int]()
    
    stack.push(10)
    
    stack.push(20)
    
    x = stack.pop()

IDE
    
    
    x
    
    ↓
    
    int

* * *

Nếu
    
    
    stack = Stack[str]()

↓
    
    
    push()
    
    ↓
    
    chỉ nhận str

* * *

# 13\. Generic không tồn tại Runtime

Ví dụ
    
    
    stack = Stack[int]()

Runtime
    
    
    print(type(stack))

Kết quả
    
    
    <class '__main__.Stack'>

Không có
    
    
    Stack<int>

hay
    
    
    Stack<str>

Đó chỉ là thông tin dành cho type checker.

* * *

# 14\. Generic và DRY

Generic giúp tuân theo nguyên tắc:

> **Don't Repeat Yourself**

Thay vì:
    
    
    UserRepository
    
    BookRepository
    
    NovelRepository
    
    ImageRepository
    
    CommentRepository

Ta có
    
    
    Repository[T]

* * *

# 15\. Ứng dụng vào dự án crawler

Ví dụ model
    
    
    @dataclass class Novel:
        id: int
        title: str

Repository
    
    
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

Sử dụng
    
    
    novel_repo = Repository[Novel]()

↓
    
    
    save()
    
    ↓
    
    Novel

IDE autocomplete cực mạnh.

* * *

# 16\. TypeVar Naming Convention

Thông thường
    
    
    T

Type

* * *
    
    
    K

Key

* * *
    
    
    V

Value

* * *
    
    
    KT
    
    VT

Key Type

Value Type

* * *
    
    
    T_co
    
    T_contra

Covariant

Contravariant

(sẽ học sau)

* * *

# 17\. Best Practices

✔ Luôn dùng `TypeVar` để viết API tổng quát thay vì tạo nhiều hàm/lớp giống nhau.

✔ Đặt tên `T`, `K`, `V` theo quy ước nếu không có ý nghĩa đặc biệt.

✔ Kết hợp `Generic[T]` với `dataclass`, `Repository`, `Service` để tạo các thành phần tái sử dụng.

✔ Hiểu rằng Generic chỉ phục vụ kiểm tra kiểu; nó không tạo lớp mới ở runtime.

* * *

# Tổng kết

Sau buổi này bạn đã hiểu:

  * TypeVar là gì.
  * Generic Function.
  * Generic Class.
  * Generic Repository.
  * Generic Stack.
  * IDE suy luận kiểu như thế nào.
  * Vì sao Generic là nền tảng của các framework Python hiện đại.



Đây mới chỉ là phần mở đầu. Những khả năng mạnh hơn như **ràng buộc (**`**bound**`**)** , **đa hình nâng cao** , **variance** , `**ParamSpec**`, `**TypeVarTuple**`... sẽ được học ở các buổi tiếp theo.

* * *

# Bài tập

## Bài 1

Viết Generic Function:
    
    
    T = TypeVar("T")
    
    def last(items: list[T]) -> T:
        ...

Lấy phần tử cuối của danh sách.

* * *

## Bài 2

Viết Generic Class:
    
    
    Box[T]

Có:

  * `set(value)`
  * `get()`



IDE phải suy luận đúng kiểu của `get()`.

* * *

## Bài 3

Viết Generic Queue
    
    
    Queue[T]

Có các phương thức:

  * `enqueue(item)`
  * `dequeue()`
  * `peek()`
  * `is_empty()`



Sử dụng `list[T]` làm vùng lưu trữ và kiểm tra bằng IDE rằng `dequeue()` và `peek()` luôn trả về đúng kiểu `T`.

* * *

**Buổi 7** sẽ đi sâu vào **Generic nâng cao** , bao gồm:

  * Generic Method
  * Generic Type Alias
  * Generic Protocol
  * Generic Dataclass
  * Generic Repository thực tế
  * Cơ chế suy luận kiểu (Type Inference)
  * Những lỗi phổ biến khi sử dụng Generic trong dự án lớn.

