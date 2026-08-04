# Buổi 35. Typing trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Type Hint là gì.
> * Phân biệt Dynamic Typing và Static Typing.
> * Thành thạo Type Annotation.
> * Sử dụng `Optional`, `Union`, `Any`.
> * Biết dùng `Literal`, `TypeAlias`.
> * Thành thạo `Callable`.
> * Hiểu Generic cơ bản (`TypeVar`).
> * Biết sử dụng `mypy` để kiểm tra kiểu.
> * Viết code Python dễ đọc, dễ bảo trì.

> **Lưu ý**
>
> Đây là buổi **Python Intermediate**. Chúng ta sẽ học cách **sử dụng** Type Hint trong dự án thực tế. Các chủ đề nâng cao như Protocol, Generic nâng cao, ParamSpec, Self, TypeGuard... sẽ thuộc lộ trình Python Advanced.

---

# 1. Vì sao cần Typing?

Python là ngôn ngữ **Dynamic Typing**.

Ví dụ:

```python
x = 10
x = "Hello"
x = [1, 2, 3]
```

Điều này rất linh hoạt nhưng cũng dễ gây lỗi.

Ví dụ:

```python
def add(a, b):
    return a + b


print(add(1, "2"))
```

Lỗi chỉ xuất hiện khi chạy:

```text
TypeError: unsupported operand type(s)
```

Typing giúp phát hiện nhiều lỗi **trước khi chạy chương trình**.

---

# 2. Type Hint là gì?

Type Hint là cách **chú thích kiểu dữ liệu**.

```python
name: str = "Alice"

age: int = 20

price: float = 99.5

active: bool = True
```

Đây chỉ là **gợi ý**.

Python **không ép kiểu**.

Ví dụ:

```python
x: int = "Hello"

print(x)
```

Python vẫn chạy.

---

# 3. Type Annotation cho hàm

```python
def add(a: int, b: int) -> int:
    return a + b
```

Ý nghĩa:

```text
a : int

b : int

↓

return int
```

---

# 4. Kiểu dữ liệu cơ bản

```python
name: str

age: int

height: float

is_admin: bool

data: bytes
```

---

# 5. Collection

List

```python
numbers: list[int] = [1, 2, 3]
```

Dictionary

```python
scores: dict[str, int] = {"Alice": 95, "Bob": 88}
```

Tuple

```python
point: tuple[int, int] = (10, 20)
```

Set

```python
tags: set[str] = {"python", "typing"}
```

> Từ Python 3.9 trở lên, ưu tiên dùng `list[int]`, `dict[str, int]` thay vì `typing.List`, `typing.Dict`.

---

# 6. `Any`

```python
from typing import Any

value: Any
```

Có thể là:

```python
10

"Python"

[]

{}
```

`Any` gần như tắt kiểm tra kiểu.

Chỉ dùng khi thật cần.

---

# 7. `Union`

```python
from typing import Union


def square(x: Union[int, float]) -> float:
    return x * x
```

Python 3.10+

```python
def square(x: int | float) -> float:
    return x * x
```

Đây là cú pháp được khuyến nghị hiện nay.

---

# 8. `Optional`

```python
from typing import Optional


def find(name: str) -> Optional[int]: ...
```

Nghĩa là:

```python
int | None
```

Python 3.10+

```python
def find(name: str) -> int | None: ...
```

---

# 9. `Literal`

Giới hạn giá trị.

```python
from typing import Literal

Color = Literal["red", "green", "blue"]
```

```python
def paint(color: Color): ...
```

Sai:

```python
paint("yellow")
```

Các công cụ kiểm tra kiểu sẽ cảnh báo.

---

# 10. `TypeAlias`

```python
from typing import TypeAlias

UserId: TypeAlias = int

ProductId: TypeAlias = int
```

Dễ đọc hơn:

```python
def load_user(user_id: UserId): ...
```

---

# 11. `Callable`

```python
from typing import Callable

Operation = Callable[[int, int], int]
```

```python
def calculate(func: Operation):
    print(func(2, 3))
```

---

# 12. `TypeVar`

Generic cơ bản.

```python
from typing import TypeVar

T = TypeVar("T")
```

```python
def first(items: list[T]) -> T:
    return items[0]
```

Ví dụ:

```python
first([1, 2, 3])
```

↓

```text
int
```

```python
first(["A", "B"])
```

↓

```text
str
```

Một hàm có thể làm việc với nhiều kiểu mà vẫn giữ được thông tin kiểu.

---

# 13. Generic đơn giản

```python
from typing import TypeVar

T = TypeVar("T")


def identity(x: T) -> T:
    return x
```

```python
identity(10)
```

↓

```text
int
```

```python
identity("Python")
```

↓

```text
str
```

---

# 14. Alias cho kiểu phức tạp

```python
JsonDict: TypeAlias = dict[str, str | int | float]
```

Thay vì:

```python
def save(
    data: dict[
        str,
        str | int | float
    ]
):
```

Bạn có thể viết:

```python
def save(
    data: JsonDict
):
```

---

# 15. `cast()`

Đôi khi bạn biết rõ kiểu hơn công cụ kiểm tra.

```python
from typing import cast

value = cast(int, get_value())
```

`cast()` **không chuyển đổi dữ liệu**.

Nó chỉ giúp công cụ kiểm tra kiểu hiểu ý định của bạn.

---

# 16. `typing.TYPE_CHECKING`

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import User
```

Đoạn mã này chỉ phục vụ kiểm tra kiểu, không được thực thi khi chạy chương trình.

---

# 17. Kiểm tra bằng `mypy`

Cài đặt:

```bash
pip install mypy
```

Ví dụ:

```python
def add(a: int, b: int) -> int:
    return a + b


add(1, "2")
```

Chạy:

```bash
mypy app.py
```

Kết quả:

```text
error:
Argument 2 has incompatible type "str"
```

---

# 18. Docstring và Type Hint

```python
def divide(a: float, b: float) -> float:
    """
    Chia hai số thực.
    """
    return a / b
```

Không cần mô tả lại kiểu trong Docstring nếu Type Hint đã đủ rõ ràng.

---

# 19. Những lỗi thường gặp

## Sai 1

Lạm dụng `Any`

```python
value: Any
```

↓

Mất lợi ích của Typing.

---

## Sai 2

Không cập nhật Type Hint khi đổi logic.

Ví dụ:

```python
def get_user() -> dict:
```

Sau này đổi trả về `User` nhưng quên sửa Type Hint.

---

## Sai 3

Nhầm `Optional`

Sai:

```python
name: Optional[str]
```

không có nghĩa là tham số **không bắt buộc**.

Nó có nghĩa là:

```python
str | None
```

Nếu muốn tham số không bắt buộc:

```python
def hello(name: str = "Guest"): ...
```

Hoặc:

```python
def hello(name: str | None = None): ...
```

---

## Sai 4

Không kiểm tra `None`

```python
def get_name() -> str | None: ...


name = get_name()

print(name.upper())
```

Có thể gây:

```text
AttributeError
```

Đúng:

```python
if name is not None:
    print(name.upper())
```

---

# 20. Best Practices

## ✔ Luôn thêm Type Hint cho hàm công khai

```python
def load_user(
    user_id: int
) -> User:
```

---

## ✔ Ưu tiên cú pháp Python 3.10+

Đúng:

```python
int | None
```

Thay vì:

```python
Optional[int]
```

---

## ✔ Hạn chế `Any`

Chỉ dùng khi:

* thư viện bên thứ ba chưa có kiểu,
* dữ liệu thực sự không xác định.

---

## ✔ Dùng TypeAlias

Giúp mã dễ đọc hơn.

---

## ✔ Chạy `mypy` định kỳ

Giúp phát hiện lỗi sớm trong các dự án lớn.

---

# 21. Mini Project - Student Manager

Cấu trúc:

```text
student_manager/

├── models.py
├── service.py
└── main.py
```

`models.py`

```python
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    score: float
```

`service.py`

```python
def find_student(student_id: int) -> Student | None: ...
```

Toàn bộ hàm đều phải có Type Hint.

---

# 22. Mini Project - JSON Loader

Viết:

```python
JsonValue = str | int | float | bool | None

JsonDict = dict[str, JsonValue]
```

Sau đó:

```python
def load_json(path: str) -> JsonDict: ...
```

Mục tiêu là mô tả dữ liệu JSON rõ ràng bằng Type Hint.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Type Hint.
* Type Annotation.
* Collection Generic (`list[int]`, `dict[str, int]`, ...).
* `Any`.
* `Union` và cú pháp `|`.
* `Optional`.
* `Literal`.
* `TypeAlias`.
* `Callable`.
* `TypeVar`.
* `cast()`.
* `TYPE_CHECKING`.
* Kiểm tra kiểu bằng `mypy`.

---

# Sơ đồ Typing

```text
Typing
│
├── Primitive Types
│      ├── int
│      ├── str
│      ├── float
│      └── bool
│
├── Collections
│      ├── list[int]
│      ├── dict[str, int]
│      └── tuple[int, int]
│
├── Special
│      ├── Any
│      ├── Literal
│      ├── TypeAlias
│      ├── Callable
│      └── TypeVar
│
└── Tools
       ├── mypy
       └── cast()
```

---

# Bài tập thực hành

### Bài 1

Viết hàm:

```python
def average(
    numbers: list[float]
) -> float:
```

trả về giá trị trung bình.

---

### Bài 2

Viết `TypeAlias`:

```python
Email = str
Phone = str
```

Sau đó dùng trong lớp `Contact`.

---

### Bài 3

Viết hàm:

```python
def execute(
    func: Callable[[int], int],
    value: int
) -> int:
```

và thử truyền nhiều hàm khác nhau.

---

### Bài 4

Viết Generic:

```python
T = TypeVar("T")

def last(
    items: list[T]
) -> T:
```

---

### Bài 5

Viết:

```python
Mode = Literal["read", "write", "append"]
```

Sau đó dùng trong:

```python
def open_file(path: str, mode: Mode): ...
```

---

### Bài 6 (Thử thách)

Xây dựng một **Repository** có Type Hint đầy đủ:

```python
class Repository[T]: ...
```

Trong buổi này chỉ cần mô phỏng:

* `add(item)`
* `get(id)`
* `remove(id)`
* `list_all()`

Mục tiêu là áp dụng toàn bộ kiến thức Typing đã học để làm cho API rõ ràng, an toàn và dễ bảo trì.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 36**, chúng ta sẽ học **Dataclass** trong Python Intermediate, bao gồm:

* Vì sao cần `@dataclass`.
* Các tham số như `init`, `repr`, `eq`, `order`, `frozen`.
* `field()` và `default_factory`.
* `__post_init__()`.
* `asdict()`, `astuple()`, `replace()`.
* So sánh Dataclass với Class thông thường và `NamedTuple`.
* Ứng dụng Dataclass trong Model, DTO và cấu hình (Configuration Objects).
