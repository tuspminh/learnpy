Version:0.9 StartHTML:0000000105 EndHTML:0000027474 StartFragment:0000000141 EndFragment:0000027438 

# Typing Deep Dive – Buổi 3

# Union, Optional, Literal và kiểu dữ liệu có điều kiện

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Thành thạo `Union` và cú pháp `|`
>   * Hiểu đúng về `Optional`
>   * Biết khi nào dùng `Literal`
>   * Phân biệt `None`, `Optional`, `Union`
>   * Thiết kế API rõ ràng, hạn chế lỗi nhờ kiểu dữ liệu
> 


* * *

# 1\. Union là gì?

Có nhiều trường hợp một biến **có thể thuộc nhiều kiểu khác nhau**.

Ví dụ:

  * ID có thể là `int` hoặc `str`
  * Giá trị có thể là `int` hoặc `float`
  * Hàm có thể trả về `User` hoặc `None`



Đó là lúc dùng **Union**.

* * *

## Python < 3.10
    
    
    from typing import Union
    
    UserId = Union[int, str]

* * *

## Python 3.10+
    
    
    UserId = int | str

Đây là cú pháp hiện đại.

* * *

## Ví dụ
    
    
    def print_id(user_id: int | str) -> None:
        print(user_id)

Có thể gọi:
    
    
    print_id(100)
    
    print_id("admin")

IDE không báo lỗi.

* * *

# 2\. Union có thể có nhiều kiểu
    
    
    Number = int | float

Ví dụ
    
    
    def square(x: Number) -> Number:
        return x * x

Gọi
    
    
    square(10)
    
    square(2.5)

* * *

Union nhiều kiểu
    
    
    JsonValue = (
        str
        | int
        | float
        | bool
    )

* * *

# 3\. Union của Collection

Ví dụ
    
    
    def process(
        data: list[int] | tuple[int, ...]
    ):
        ...

Có thể truyền
    
    
    [1,2,3]
    
    (1,2,3)

* * *

Hoặc
    
    
    dict[str, int] | None

* * *

# 4\. isinstance với Union

Ví dụ
    
    
    def double(value: int | str):
        if isinstance(value, int):
            return value * 2
    
        return value * 2

IDE sẽ hiểu
    
    
    if
    ↓
    
    value là int

Sau `else`
    
    
    value là str

Đây gọi là

> Type Narrowing

* * *

# 5\. Optional là gì?

Rất nhiều người hiểu sai.

Họ nghĩ
    
    
    Optional[int]

nghĩa là

> Có thể truyền hoặc không truyền.

Sai.

* * *

`Optional[int]`

chỉ có nghĩa
    
    
    int | None

Không hơn.

* * *

Ví dụ
    
    
    from typing import Optional
    
    age: Optional[int]

Tương đương
    
    
    age: int | None

* * *

# 6\. Optional KHÔNG phải tham số mặc định

Sai lầm phổ biến
    
    
    def hello(name: Optional[str]):
        ...

Điều này KHÔNG có nghĩa
    
    
    hello()

được phép.

Muốn bỏ tham số

phải có default.
    
    
    def hello(
        name: str | None = None
    ):
        ...

Bây giờ mới được
    
    
    hello()

* * *

# 7\. None

`None`

là một object.
    
    
    print(type(None))

Kết quả
    
    
    <class 'NoneType'>

Nó không phải
    
    
    False
    
    0
    
    ""
    
    []

Mà là object riêng.

* * *

# 8\. Ví dụ Optional
    
    
    def find_user(
        user_id: int
    ) -> str | None:
        ...

Nếu tìm thấy
    
    
    "Alice"

Nếu không
    
    
    None

Đây là thiết kế rất phổ biến.

* * *

# 9\. Type Narrowing với None

Ví dụ
    
    
    def welcome(
        name: str | None
    ):
        if name is None:
            print("Guest")
            return
    
        print(name.upper())

Sau dòng
    
    
    if name is None:

IDE biết

Ở phần dưới
    
    
    name
    
    ↓
    
    str

Không còn là `str | None`.

* * *

# 10\. Literal

Đây là phần cực kỳ hữu ích.

Ví dụ
    
    
    mode = "read"

Thực tế

Mode chỉ có thể là
    
    
    read
    
    write
    
    append

Không phải mọi chuỗi.

* * *

Ta dùng
    
    
    from typing import Literal
    
    Mode = Literal[
        "read",
        "write",
        "append"
    ]

* * *

Ví dụ
    
    
    def open_file(
        mode: Mode
    ):
        ...

Được phép
    
    
    open_file("read")
    
    open_file("write")

Không được
    
    
    open_file("delete")

IDE báo lỗi.

* * *

# 11\. Literal với số

Ví dụ
    
    
    Level = Literal[
        1,
        2,
        3,
        4,
        5
    ]
    
    
    def set_level(
        level: Level
    ):
        ...

Không thể
    
    
    set_level(100)

* * *

# 12\. Literal với bool
    
    
    Literal[True]

Hoặc
    
    
    Literal[False]

Ít dùng nhưng hữu ích trong một số API đặc biệt.

* * *

# 13\. Literal với trạng thái

Ví dụ dự án crawler
    
    
    Status = Literal[
        "pending",
        "running",
        "success",
        "failed",
        "paused"
    ]
    
    
    def update_status(
        status: Status
    ):
        ...

Nếu viết
    
    
    update_status("error")

IDE báo ngay.

* * *

# 14\. Union + Literal

Ví dụ
    
    
    Status = Literal[
        "running",
        "done"
    ]
    
    def update(
        status: Status | None
    ):
        ...

Có nghĩa
    
    
    running
    
    done
    
    None

* * *

# 15\. Literal vs Enum

Có người hỏi

Dùng
    
    
    Literal

hay
    
    
    Enum

### Literal
    
    
    Literal[
        "red",
        "green",
        "blue"
    ]

Đơn giản.

Không tạo object mới.

* * *

### Enum
    
    
    from enum import Enum
    
    class Color(Enum):
        RED = "red"
        GREEN = "green"

Mạnh hơn.

Có method.

Có behavior.

Có thể mở rộng.

* * *

Quy tắc

Nếu chỉ kiểm tra vài giá trị

→ `Literal`

Nếu có logic

→ `Enum`

* * *

# 16\. Ví dụ thực tế

Thiết kế API
    
    
    SortOrder = Literal[
        "asc",
        "desc"
    ]
    
    
    def get_users(
        order: SortOrder
    ):
        ...

IDE sẽ tự gợi ý
    
    
    asc
    
    desc

Đây là trải nghiệm rất tốt.

* * *

# 17\. Ví dụ trong dự án crawler
    
    
    SourceType = Literal[
        "truyenfull",
        "bachngocsach",
        "metruyen",
    ]
    
    
    def create_source(
        source: SourceType
    ):
        ...

Không thể viết
    
    
    create_source(
        "facebook"
    )

IDE phát hiện lỗi trước khi chạy.

* * *

# 18\. So sánh

Kiểu| Ý nghĩa  
---|---  
`int | str`| Có thể là `int` hoặc `str`  
`int | None`| Có thể là `int` hoặc `None`  
`Optional[int]`| Tương đương `int | None`  
`Literal["read"]`| Chỉ đúng giá trị `"read"`  
`Literal[1,2,3]`| Chỉ nhận 1, 2 hoặc 3  
  
* * *

# 19\. Best Practices

✔ Dùng cú pháp `|` thay cho `Union[...]` trong Python 3.10+.

✔ Chỉ dùng `Optional[T]` hoặc `T | None` khi giá trị thực sự có thể là `None`.

✔ Dùng `Literal` cho các tập giá trị hữu hạn (mode, status, order, role, action...).

✔ Dùng `Enum` khi các giá trị có thêm hành vi hoặc phương thức.

❌ Không dùng `Optional` để biểu thị "tham số không bắt buộc". Tham số không bắt buộc cần có giá trị mặc định (`=`).

* * *

# Bài tập thực hành

## Bài 1

Viết hàm:
    
    
    def parse_id(user_id):
        ...

Yêu cầu:

  * `user_id` có thể là `int` hoặc `str`.
  * Nếu là `int` thì trả về chuỗi `"ID: <giá trị>"`.
  * Nếu là `str` thì chuyển về chữ hoa trước khi trả về.



* * *

## Bài 2

Viết hàm:
    
    
    def find_book(book_id):
        ...

Yêu cầu:

  * Trả về `str | None`.
  * Nếu `book_id > 0` trả về `"Python Deep Dive"`.
  * Nếu không thì trả về `None`.



Sau đó xử lý kết quả bằng cách kiểm tra `is None` trước khi sử dụng.

* * *

## Bài 3

Định nghĩa:
    
    
    Status = Literal[
        "pending",
        "running",
        "success",
        "failed"
    ]

Viết hàm:
    
    
    def set_status(status: Status) -> None:
        print(status)

Thử gọi với:
    
    
    set_status("pending")   # hợp lệ set_status("failed")    # hợp lệ set_status("error")     # IDE/mypy nên báo lỗi

Quan sát cách `Literal` giúp phát hiện lỗi ngay trong quá trình lập trình.

* * *

Ở **Buổi 4** , chúng ta sẽ đi sâu vào một trong những chủ đề dễ gây nhầm lẫn nhất của `typing`: `**Any**`**,**`**object**`**,**`**Never**`**,**`**NoReturn**`**và tư duy "top type" / "bottom type"**. Đây là nền tảng để hiểu vì sao lạm dụng `Any` có thể làm mất tác dụng của toàn bộ hệ thống type hint.

