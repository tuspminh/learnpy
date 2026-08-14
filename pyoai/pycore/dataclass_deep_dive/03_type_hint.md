# Dataclass Deep Dive - Buổi 3

# Type Hint Deep Dive trong Dataclass

> Đây là một trong những buổi quan trọng nhất của khóa học.

Nhiều người nghĩ:

> Dataclass cần Type Hint để kiểm tra kiểu dữ liệu.

**Điều này chưa đúng.**

Thực tế, **Type Hint chính là cách Dataclass biết đâu là field của class**.

Nếu không hiểu buổi này, bạn sẽ rất khó hiểu `field()`, `InitVar`, `ClassVar`, `Generic`, `Pydantic`, `SQLAlchemy 2.0`...

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Dataclass đọc Type Hint như thế nào
- `__annotations__` là gì
- Field được tạo ra ra sao
- `ClassVar`
- `InitVar`
- `Optional`
- `Union`
- `Literal`
- `Annotated`
- `Generic`
- `Self`
- Forward Reference

---

# 1. Type Hint không phải để kiểm tra kiểu dữ liệu

Nhiều người nghĩ

```text-x-trilium-auto
@dataclass class Student:
    id: int
```

Python sẽ ép

```text-x-trilium-auto
Student("abc")
```

báo lỗi.

Không.

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id: int
```

```text-x-trilium-auto
s = Student("abc")

print(s)
```

Kết quả

```text-x-trilium-auto
Student(id='abc')
```

Không có lỗi.

## Vì sao?

Python **không kiểm tra type hint khi chạy (runtime)**.

Type Hint chủ yếu phục vụ:

- IDE (VS Code, PyCharm)
- mypy
- pyright
- pylint
- dataclass
- Pydantic
- FastAPI

---

# 2. Dataclass lấy thông tin field ở đâu?

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id: int
    name: str
    age: int
```

Python tạo

```text-x-trilium-auto
Student.__annotations__
```

Thử xem

```text-x-trilium-auto
print(Student.__annotations__)
```

Kết quả

```text-x-trilium-auto
{
    'id': int,
    'name': str,
    'age': int
}
```

Đây chính là nguồn dữ liệu mà `@dataclass` sử dụng.

---

# 3. **annotations** là gì?

Mọi class có type hint đều có

```text-x-trilium-auto
__annotations__
```

Ví dụ

```text-x-trilium-auto
class Book:
    title: str
    pages: int
```

```text-x-trilium-auto
print(Book.__annotations__)
```

Kết quả

```text-x-trilium-auto
{
    "title": str,
    "pages": int
}
```

Dataclass chỉ việc đọc dictionary này.

---

# 4. Không có Type Hint thì sao?

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:

    id = 0

    name = ""
```

Tạo object

```text-x-trilium-auto
Student()
```

Kết quả

```text-x-trilium-auto
Student()
```

Không có field nào cả.

Xem

```text-x-trilium-auto
print(Student.__annotations__)
```

Kết quả

```text-x-trilium-auto
{}
```

---

# 5. Field được tạo từ annotation

Ví dụ

```text-x-trilium-auto
@dataclass class Student:

    id: int

    name: str
```

Dataclass hiểu

```text-x-trilium-auto
Field 1

↓

id
```

```text-x-trilium-auto
Field 2

↓

name
```

Nếu viết

```text-x-trilium-auto
id = 0
```

thì chỉ là

Class Variable

không phải dataclass field.

---

# 6. Optional

Ví dụ

```text-x-trilium-auto
from typing import Optional

@dataclass class Student:

    id: int

    nickname: Optional[str]
```

Ý nghĩa

```text-x-trilium-auto
nickname

↓

str

hoặc

None
```

Ví dụ

```text-x-trilium-auto
Student(1, None)

Student(1, "Tom")
```

Đều hợp lệ về mặt type hint.

---

# 7. Union

Python cũ

```text-x-trilium-auto
from typing import Union

Union[int, str]
```

Python mới

```text-x-trilium-auto
int | str
```

Ví dụ

```text-x-trilium-auto
@dataclass class Config:

    value: int | str
```

Có thể

```text-x-trilium-auto
Config(100)

Config("hello")
```

---

# 8. List

```text-x-trilium-auto
from typing import List

@dataclass class Book:

    chapters: list[str]
```

Ví dụ

```text-x-trilium-auto
Book(
    ["A", "B", "C"]
)
```

Dataclass không tạo list.

Nó chỉ lưu.

---

# 9. Dictionary

```text-x-trilium-auto
@dataclass class Config:

    settings: dict[str, str]
```

Ví dụ

```text-x-trilium-auto
Config({

    "host":"localhost",

    "port":"3306"

})
```

---

# 10. Tuple

```text-x-trilium-auto
@dataclass class Point:

    coordinate: tuple[int, int]
```

Ví dụ

```text-x-trilium-auto
Point((10,20))
```

---

# 11. Literal

```text-x-trilium-auto
from typing import Literal
```

Ví dụ

```text-x-trilium-auto
@dataclass class Novel:

    status: Literal[
        "ONGOING",
        "COMPLETED"
    ]
```

IDE sẽ cảnh báo nếu viết

```text-x-trilium-auto
Novel("STOP")
```

Mặc dù Python runtime vẫn không chặn nếu không dùng công cụ kiểm tra kiểu.

---

# 12. Forward Reference

Một class tham chiếu đến chính nó.

Ví dụ

```text-x-trilium-auto
from __future__ import annotations

from dataclasses import dataclass

@dataclass class Node:

    value: int

    next: Node | None
```

Hoặc

```text-x-trilium-auto
@dataclass class Node:

    value: int

    next: "Node"
```

Dùng để xây dựng:

- Linked List
- Tree
- AST

---

# 13. Self

Python 3.11

```text-x-trilium-auto
from typing import Self
```

Ví dụ

```text-x-trilium-auto
@dataclass class User:

    name: str

    def clone(self) -> Self:
        return User(self.name)
```

IDE hiểu

```text-x-trilium-auto
clone()

↓

User
```

---

# 14. Generic

Ví dụ

```text-x-trilium-auto
from typing import Generic from typing import TypeVar

T = TypeVar("T")
```

```text-x-trilium-auto
@dataclass class Box(Generic[T]):

    value: T
```

Có thể

```text-x-trilium-auto
Box[int](100)

Box[str]("hello")

Box[list[int]]([1,2,3])
```

Sau này sẽ học sâu ở buổi Generic Dataclass.

---

# 15. Annotated

Python

```text-x-trilium-auto
from typing import Annotated
```

Ví dụ

```text-x-trilium-auto
from typing import Annotated

Age = Annotated[
    int,
    "0-150"
]
```

```text-x-trilium-auto
@dataclass class Student:

    age: Age
```

Dataclass bỏ qua metadata này.

Nhưng

- FastAPI
- Pydantic
- các framework khác

có thể sử dụng để kiểm tra hoặc sinh tài liệu API.

---

# 16. ClassVar

Đây là phần cực kỳ quan trọng.

Ví dụ

```text-x-trilium-auto
from typing import ClassVar

@dataclass class Student:

    school: ClassVar[str] = "ABC School"

    id: int

    name: str
```

Tạo object

```text-x-trilium-auto
Student(1,"An")
```

In

```text-x-trilium-auto
print(Student.__annotations__)
```

Kết quả

```text-x-trilium-auto
{

'school': ClassVar[str],

'id': int,

'name': str

}
```

Nhưng

```text-x-trilium-auto
print(Student(1,"An"))
```

Kết quả

```text-x-trilium-auto
Student(id=1,name='An')
```

Không có

```text-x-trilium-auto
school
```

Vì

`ClassVar`

không phải dataclass field.

Nó là biến dùng chung cho cả lớp.

---

# 17. Nhìn trực quan

```text-x-trilium-auto
Annotation
        │
        ▼
dataclass đọc

id:int
name:str

↓

Field
```

Trong khi

```text-x-trilium-auto
ClassVar

↓

Không tạo field
```

---

# 18. Ví dụ thực tế dự án crawler

```text-x-trilium-auto
from dataclasses import dataclass from typing import ClassVar

@dataclass class Novel:

    BASE_URL: ClassVar[str] = "https://example.com"

    id: int

    title: str

    author: str
```

Kết quả

```text-x-trilium-auto
Novel(
    1,
    "Tiên Nghịch",
    "Nhĩ Căn"
)
```

In

```text-x-trilium-auto
Novel(
    id=1,
    title='Tiên Nghịch',
    author='Nhĩ Căn'
)
```

Không in

```text-x-trilium-auto
BASE_URL
```

Vì đó là thông tin dùng chung cho mọi `Novel`, không phải dữ liệu của từng đối tượng.

---

# 19. Dataclass không kiểm tra kiểu

Ví dụ

```text-x-trilium-auto
Novel(

"id",

100,

True
)
```

Python vẫn tạo object.

Nếu muốn kiểm tra kiểu dữ liệu lúc chạy, bạn có thể:

- Tự kiểm tra trong `__post_init__()`.
- Dùng thư viện như **Pydantic**.
- Dùng các công cụ kiểm tra tĩnh như **mypy** hoặc **pyright**.

---

# Tổng kết

| Kiểu | Ý nghĩa |
| --- | --- |
| `int` | Số nguyên |
| `str` | Chuỗi |
| `float` | Số thực |
| `bool` | Boolean |
| `Optional[T]` | Có thể là `T` hoặc `None` |
| `T1 \\| T2` | Một trong nhiều kiểu |
| `list[T]` | Danh sách |
| `dict[K, V]` | Từ điển |
| `tuple[...]` | Bộ giá trị |
| `Literal[...]` | Giá trị cố định |
| `Annotated[...]` | Kiểu kèm metadata |
| `Self` | Trả về chính kiểu của lớp |
| `Generic[T]` | Kiểu tổng quát |
| `ClassVar[T]` | Biến của lớp, **không phải field** |
| `"Node"` | Forward Reference |

---

# Bài tập thực hành

## Bài 1

Tạo dataclass `Novel`:

```text-x-trilium-auto
id: int title: str author: str tags: list[str]
```

Khởi tạo một đối tượng với ít nhất 3 thẻ (`tags`) và in ra.

---

## Bài 2

Tạo dataclass `CrawlerConfig`:

- `base_url: ClassVar[str]`
- `timeout: int`
- `headers: dict[str, str]`

Kiểm tra:

- `print(CrawlerConfig.__annotations__)`
- `print(CrawlerConfig(...))`

Giải thích vì sao `base_url` không xuất hiện trong kết quả in của đối tượng.

---

## Bài 3

Xây dựng cấu trúc cây thư mục bằng dataclass:

```text-x-trilium-auto
from __future__ import annotations

@dataclass class Folder:
    name: str
    children: list["Folder"]
```

Tạo cấu trúc:

```text-x-trilium-auto
root
├── docs
│   ├── python
│   └── sqlite
└── images
```

Đây là ví dụ điển hình về **Forward Reference** và sẽ là nền tảng cho các cấu trúc cây (Tree) chúng ta sẽ học sâu hơn ở các buổi sau.

---

## Chuẩn bị cho Buổi 4

Buổi tiếp theo là `**field()**` **Deep Dive** – phần quan trọng nhất của `dataclass`. Chúng ta sẽ tìm hiểu:

- `field()`
- `default`
- `default_factory`
- `init`
- `repr`
- `compare`
- `hash`
- `metadata`
- `kw_only`

Đây là kiến thức được sử dụng rất nhiều trong các dự án thực tế và các framework hiện đại.