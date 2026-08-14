# Dataclass Deep Dive - Buổi 4

# `field()` Deep Dive (Quan trọng nhất của Dataclass)

> Đây là buổi quan trọng nhất của khóa học.

Nếu chỉ được chọn **một** chủ đề để thành thạo trong `dataclass`, thì đó chính là `field()`.

Hầu hết các dự án Python chuyên nghiệp đều sử dụng `field()` để:

- Thiết lập giá trị mặc định.
- Tránh lỗi với mutable object.
- Loại bỏ field khỏi `repr`.
- Bỏ qua field khi so sánh.
- Lưu metadata.
- Kiểm soát constructor.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- `field()` là gì?
- Khi nào cần dùng?
- `default`
- `default_factory`
- `init`
- `repr`
- `compare`
- `hash`
- `metadata`
- `kw_only`
- Những lỗi rất thường gặp

---

# 1. field() là gì?

`field()` dùng để **cấu hình chi tiết cho từng field**.

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Student:
    id: int
    name: str = field(default="Unknown")
```

Nếu không cần cấu hình gì, bạn chỉ cần:

```text-x-trilium-auto
name: str = "Unknown"
```

Nhưng khi cần nhiều tùy chọn hơn thì phải dùng `field()`.

---

# 2. default

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Student:
    id: int
    age: int = field(default=18)
```

Có thể tạo

```text-x-trilium-auto
Student(1)
```

Kết quả

```text-x-trilium-auto
Student(id=1, age=18)
```

---

Không dùng `field()` cũng được

```text-x-trilium-auto
age: int = 18
```

Hai cách gần như tương đương.

---

# 3. default_factory

Đây là phần quan trọng nhất.

Ví dụ sai

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Book:

    chapters: list[str] = []
```

Python báo lỗi

```text-x-trilium-auto
ValueError:
mutable default <class 'list'>
is not allowed
```

---

## Vì sao?

Nếu Python cho phép

```text-x-trilium-auto
[]
```

thì mọi object sẽ dùng chung một list.

```text-x-trilium-auto
Book A ---------

                |

                v

             []

                ^

                |

Book B ---------
```

Sửa một object sẽ ảnh hưởng object còn lại.

Đây là lỗi kinh điển trong Python.

---

## Cách đúng

```text-x-trilium-auto
from dataclasses import field

chapters: list[str] = field(default_factory=list)
```

Mỗi object

↓

Python gọi

```text-x-trilium-auto
list()
```

để tạo list mới.

```text-x-trilium-auto
Book A

↓

[]

Book B

↓

[]
```

Không còn dùng chung.

---

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Book:

    chapters: list[str] = field(default_factory=list)
```

```text-x-trilium-auto
a = Book()
b = Book()

a.chapters.append("Chapter 1")

print(a.chapters)
print(b.chapters)
```

Kết quả

```text-x-trilium-auto
['Chapter 1']
[]
```

---

# 4. default_factory không chỉ dùng cho list

Có thể dùng

```text-x-trilium-auto
dict
```

```text-x-trilium-auto
settings: dict = field(default_factory=dict)
```

---

Set

```text-x-trilium-auto
tags: set = field(default_factory=set)
```

---

Tuple

```text-x-trilium-auto
point: tuple = field(default_factory=tuple)
```

---

Thậm chí

```text-x-trilium-auto
from uuid import uuid4

id = field(default_factory=uuid4)
```

Mỗi object tự sinh UUID.

---

Hay thời gian hiện tại

```text-x-trilium-auto
from datetime import datetime

created_at = field(default_factory=datetime.now)
```

Mỗi đối tượng sẽ nhận thời điểm được tạo, thay vì dùng chung một giá trị.

---

# 5. init=False

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Student:

    id: int

    score: int = field(init=False)
```

Constructor

```text-x-trilium-auto
Student(1)
```

Không cần truyền

```text-x-trilium-auto
score
```

---

Thường kết hợp với `__post_init__()`.

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Rectangle:

    width: int
    height: int

    area: int = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
```

```text-x-trilium-auto
Rectangle(10,20)
```

Kết quả

```text-x-trilium-auto
area = 200
```

`area` được tính tự động.

---

# 6. repr=False

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class User:

    username: str

    password: str = field(repr=False)
```

In

```text-x-trilium-auto
print(User("admin","123456"))
```

Kết quả

```text-x-trilium-auto
User(username='admin')
```

Không in

```text-x-trilium-auto
password
```

Rất hữu ích cho:

- password
- token
- secret key
- api key

Lưu ý: `repr=False` chỉ **ẩn khi in**, **không mã hóa dữ liệu**.

---

# 7. compare=False

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class User:

    id: int

    last_login: str = field(compare=False)
```

```text-x-trilium-auto
a = User(1,"today")

b = User(1,"yesterday")

print(a == b)
```

Kết quả

```text-x-trilium-auto
True
```

Vì

```text-x-trilium-auto
last_login
```

không được dùng để so sánh.

---

Rất hữu ích với:

- timestamp
- cache
- session
- access_token

---

# 8. hash=False

Ví dụ

```text-x-trilium-auto
field(hash=False)
```

Field này sẽ không tham gia vào phép tính `__hash__`.

Phần này sẽ được giải thích sâu hơn ở buổi về `__hash__` và `frozen`.

---

# 9. metadata

Ví dụ

```text-x-trilium-auto
from dataclasses import field

price = field(
    metadata={
        "unit":"USD",
        "min":0
    }
)
```

Dataclass **không sử dụng** metadata.

Nhưng framework khác có thể dùng.

Ví dụ:

- Validator
- ORM
- Serializer
- GUI Generator
- API Generator

Đọc metadata:

```text-x-trilium-auto
from dataclasses import fields

for f in fields(Product):
    print(f.name, f.metadata)
```

---

# 10. kw_only=True

Python 3.10+

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Config:

    host: str

    port: int = field(kw_only=True)
```

Tạo

```text-x-trilium-auto
Config("localhost", port=3306)
```

Đúng.

Nhưng

```text-x-trilium-auto
Config("localhost",3306)
```

Sai.

Field phải truyền bằng tên.

Rất hữu ích khi có nhiều tham số tùy chọn.

---

# 11. Xem Field object

Ví dụ

```text-x-trilium-auto
from dataclasses import fields

for f in fields(Student):

    print(f)
```

Kết quả

```text-x-trilium-auto
Field(
    name='id',
    type=<class 'int'>,
    default=MISSING,
    ...
)
```

`fields()` trả về thông tin mô tả của từng field.

---

# 12. MISSING

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id:int
```

Field `id`

không có

```text-x-trilium-auto
default
```

Nên

```text-x-trilium-auto
default=MISSING
```

Đây là sentinel object nội bộ của `dataclasses` để phân biệt:

- Không có giá trị mặc định.
- Có giá trị mặc định là `None`.

---

# 13. Không được dùng cả default và default_factory

Sai

```text-x-trilium-auto
field(

default=[],

default_factory=list

)
```

Python báo lỗi.

Chỉ được chọn một trong hai.

---

# 14. Thứ tự field

Sai

```text-x-trilium-auto
@dataclass class Student:

    age: int = 18

    name: str
```

Python báo

```text-x-trilium-auto
TypeError:
non-default argument follows default argument
```

Đúng

```text-x-trilium-auto
@dataclass class Student:

    name: str

    age: int = 18
```

Quy tắc này giống với quy tắc của hàm trong Python: tham số không có mặc định phải đứng trước tham số có mặc định.

---

# 15. Ví dụ thực tế trong dự án crawler

```text-x-trilium-auto
from dataclasses import dataclass, field from datetime import datetime

@dataclass class Chapter:

    id: int

    title: str

    url: str

    downloaded: bool = False

    created_at: datetime = field(
        default_factory=datetime.now
    )

    html: str = field(
        repr=False
    )

    retry_count: int = field(
        compare=False,
        default=0
    )
```

Ý nghĩa:

- `created_at`: tự động lấy thời điểm tạo.
- `html`: không hiện khi in đối tượng vì có thể rất dài.
- `retry_count`: không ảnh hưởng khi so sánh hai `Chapter`.

---

# Tổng kết

| Tùy chọn | Mục đích |
| --- | --- |
| `default=` | Giá trị mặc định |
| `default_factory=` | Tạo giá trị mới cho từng object |
| `init=False` | Không đưa vào constructor |
| `repr=False` | Không hiển thị khi `print()` |
| `compare=False` | Bỏ qua khi so sánh |
| `hash=False` | Bỏ qua khi tính hash |
| `metadata={}` | Lưu thông tin bổ sung |
| `kw_only=True` | Bắt buộc truyền bằng keyword |

---

# Bài tập thực hành

## Bài 1

Tạo dataclass `Library`:

- `name: str`
- `books: list[str] = field(default_factory=list)`

Tạo hai đối tượng và chứng minh rằng mỗi đối tượng có danh sách `books` riêng.

---

## Bài 2

Tạo dataclass `Account`:

- `username`
- `password` (không hiển thị khi `print()`)
- `created_at` (tự động lấy thời gian hiện tại bằng `default_factory`)

In đối tượng và kiểm tra kết quả.

---

## Bài 3

Thiết kế dataclass `CrawlerJob`:

- `url: str`
- `status: str = "PENDING"`
- `retry_count: int = field(compare=False, default=0)`
- `logs: list[str] = field(default_factory=list, repr=False)`
- `created_at: datetime = field(default_factory=datetime.now)`

Tạo hai `CrawlerJob` có cùng `url` và `status` nhưng `retry_count` khác nhau, rồi kiểm tra phép so sánh `==` để xác nhận rằng `retry_count` không ảnh hưởng đến kết quả.

---

## Chuẩn bị cho Buổi 5

Buổi tiếp theo chúng ta sẽ học **Frozen Dataclass Deep Dive**:

- Immutable object là gì?
- `frozen=True` hoạt động như thế nào?
- Tại sao `frozen` lại liên quan đến `__hash__`?
- Cách thay đổi dữ liệu của một đối tượng bất biến bằng `dataclasses.replace()`.
- Ứng dụng trong cache, cấu hình, lập trình hàm (functional programming) và lập trình đa luồng (thread-safe). Đây là một chủ đề rất quan trọng trong các hệ thống Python hiện đại.