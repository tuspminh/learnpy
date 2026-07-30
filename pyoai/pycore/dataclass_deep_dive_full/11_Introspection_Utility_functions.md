# Dataclass Deep Dive - Buổi 11

# Dataclass Introspection & Utility Functions Deep Dive

> Đây là buổi học về **các API quan trọng nhất của module** `**dataclasses**`.

Nếu các buổi trước giúp bạn **định nghĩa dataclass**, thì buổi này giúp bạn **làm việc với dataclass ở runtime**.

Đây là kiến thức được dùng rất nhiều trong:

- ORM
- Serializer
- JSON API
- Config Loader
- CLI Framework
- Plugin System
- Dependency Injection
- Crawler Framework (dự án của bạn)

---

# Mục tiêu

Sau buổi này bạn sẽ thành thạo:

- `fields()`
- `Field`
- `asdict()`
- `astuple()`
- `replace()`
- `is_dataclass()`
- `make_dataclass()`

---

# 1. `fields()`

Đây là API quan trọng nhất.

```text-x-trilium-auto
from dataclasses import dataclass, fields

@dataclass class User:
    id: int
    name: str
    age: int
```

```text-x-trilium-auto
for f in fields(User):
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

---

## Ý nghĩa

`fields()`

↓

Trả về metadata của dataclass.

Không phải giá trị.

---

# 2. Field object

Ví dụ

```text-x-trilium-auto
for f in fields(User):

    print(f.name)
    print(f.type)
    print(f.default)
```

Kết quả

```text-x-trilium-auto
id
<class 'int'>
MISSING

name
<class 'str'>
MISSING
```

---

## Các thuộc tính quan trọng

```text-x-trilium-auto
name

type

default

default_factory

repr

compare

hash

metadata

kw_only
```

Bạn đã học tất cả ở các buổi trước.

---

# 3. Ví dụ thực tế

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import fields

@dataclass class Book:

    title:str

    pages:int
```

Sinh SQL

```text-x-trilium-auto
cols=[]

for f in fields(Book):

    cols.append(
        f"{f.name} TEXT"
    )

print(cols)
```

Đây chính là nền tảng để xây dựng ORM.

---

# 4. `asdict()`

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import asdict

@dataclass class User:

    id:int

    name:str
```

```text-x-trilium-auto
u=User(1,"Alice")

print(
    asdict(u)
)
```

Kết quả

```text-x-trilium-auto
{
'id':1,

'name':'Alice'
}
```

---

## Có gì đặc biệt?

Không phải

```text-x-trilium-auto
u.__dict__
```

mà

```text-x-trilium-auto
asdict()
```

làm việc cả với:

- nested dataclass
- slots
- frozen

---

# 5. Nested Dataclass

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Address:

    city:str

    street:str
```

```text-x-trilium-auto
@dataclass class User:

    name:str

    address:Address
```

```text-x-trilium-auto
u=User(

"Alice",

Address(

"HCM",

"ABC"

)

)
```

```text-x-trilium-auto
print(
    asdict(u)
)
```

Kết quả

```text-x-trilium-auto
{
'name':'Alice',

'address':{

'city':'HCM',

'street':'ABC'

}
}
```

Đệ quy rất tiện lợi.

---

# 6. `astuple()`

Giống

```text-x-trilium-auto
asdict()
```

nhưng

↓

Tuple

```text-x-trilium-auto
from dataclasses import astuple

print(

astuple(u)

)
```

Kết quả

```text-x-trilium-auto
(
1,

'Alice'
)
```

---

Nested

↓

cũng recursive.

---

# 7. `replace()`

Bạn đã gặp ở buổi Frozen.

Ví dụ

```text-x-trilium-auto
from dataclasses import replace

u=User(

1,

"Alice"

)
```

```text-x-trilium-auto
u2=replace(

u,

name="Bob"

)
```

Kết quả

```text-x-trilium-auto
User(
id=1,
name='Bob'
)
```

Object cũ

↓

không đổi.

---

# 8. replace() không phải deepcopy

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Team:

    members:list
```

```text-x-trilium-auto
a=Team(["A"])

b=replace(a)
```

```text-x-trilium-auto
b.members.append("B")
```

Kết quả

```text-x-trilium-auto
print(a.members)
```

```text-x-trilium-auto
['A','B']
```

Vì

↓

shallow copy.

Nếu cần bản sao hoàn toàn độc lập với các đối tượng lồng nhau, hãy dùng:

```text-x-trilium-auto
import copy

team2 = copy.deepcopy(team1)
```

---

# 9. `is_dataclass()`

Ví dụ

```text-x-trilium-auto
from dataclasses import is_dataclass

print(

is_dataclass(User)

)
```

↓

```text-x-trilium-auto
True
```

---

Object

```text-x-trilium-auto
u=User(
1,
"Alice"
)

print(

is_dataclass(u)

)
```

↓

```text-x-trilium-auto
True
```

---

Class thường

```text-x-trilium-auto
class A:
    ...
```

↓

```text-x-trilium-auto
False
```

---

# 10. `make_dataclass()`

Đây là API cực kỳ hay.

Ví dụ

```text-x-trilium-auto
from dataclasses import make_dataclass

Person=make_dataclass(

"Person",

[

("id",int),

("name",str)

]

)
```

Tạo object

```text-x-trilium-auto
p=Person(
1,
"Alice"
)

print(p)
```

↓

```text-x-trilium-auto
Person(
id=1,
name='Alice'
)
```

Không cần viết class.

---

# 11. Khi nào dùng?

Ví dụ

Plugin đọc schema

↓

Sinh model runtime.

Ví dụ

```text-x-trilium-auto
JSON Schema

↓

Dataclass

↓

Object
```

---

# 12. Crawler Project

Giả sử plugin trả

```text-x-trilium-auto
Novel

title

author

views

rating
```

Plugin khác

```text-x-trilium-auto
Novel

title

author

status

category
```

Có thể

↓

Sinh dataclass runtime.

---

# 13. `fields()` + `asdict()`

Ví dụ serializer

```text-x-trilium-auto
def serialize(obj):

    result={}

    for f in fields(obj):

        result[f.name]=getattr(
            obj,
            f.name
        )

    return result
```

Thực chất

↓

đây gần giống

```text-x-trilium-auto
asdict()
```

---

# 14. `fields()` + `metadata`

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import field

@dataclass class Product:

    price:int=field(

        metadata={

            "unit":"USD"

        }

    )
```

Đọc

```text-x-trilium-auto
for f in fields(Product):

    print(

        f.metadata

    )
```

↓

```text-x-trilium-auto
{
'unit':'USD'
}
```

Framework validator thường làm như vậy.

---

# 15. Tạo JSON

```text-x-trilium-auto
import json

print(

json.dumps(

asdict(u),

indent=4

)

)
```

↓

```text-x-trilium-auto
{
    "id":1,
    "name":"Alice"
}
```

---

# 16. Tạo CSV

```text-x-trilium-auto
import csv

with open(
    "user.csv",
    "w",
    newline=""
) as f:

    writer=csv.DictWriter(

        f,

        fieldnames=asdict(u).keys()

    )

    writer.writeheader()

    writer.writerow(
        asdict(u)
    )
```

---

# 17. Clone Object

```text-x-trilium-auto
new_user=replace(

old_user,

name="New"

)
```

Rất hay dùng.

---

# 18. DTO Mapper

Ví dụ

Database

↓

Dataclass

↓

JSON

```text-x-trilium-auto
SQLite

↓

User

↓

asdict()

↓

JSON API
```

---

# 19. Debug

```text-x-trilium-auto
print(

asdict(chapter)

)
```

Nhanh hơn

```text-x-trilium-auto
print(

chapter.__dict__

)
```

Đặc biệt với `slots=True`, vì lớp dùng `slots` không có `__dict__`.

---

# 20. Ví dụ Crawler

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Chapter:

    id:int

    title:str

    url:str
```

```text-x-trilium-auto
chapter=Chapter(

1,

"Chương 1",

"https://..."

)
```

Xuất

```text-x-trilium-auto
json.dumps(

asdict(chapter),

indent=4

)
```

↓

```text-x-trilium-auto
{
"id":1,
"title":"Chương 1",
"url":"https://..."
}
```

Có thể lưu cache.

---

# 21. Dynamic Plugin

Plugin

↓

Đọc Config

↓

Sinh

```text-x-trilium-auto
make_dataclass()
```

↓

Không cần viết model trước.

Đây là kỹ thuật hữu ích trong các hệ thống plugin hoặc khi làm việc với schema động.

---

# 22. Best Practice

Nên dùng:

| API | Mục đích |
| --- | --- |
| `fields()` | Reflection, ORM, Validator |
| `asdict()` | JSON, API, Cache |
| `astuple()` | Dữ liệu tuần tự |
| `replace()` | Immutable Update |
| `is_dataclass()` | Framework |
| `make_dataclass()` | Dynamic Model |

---

# 23. Những lưu ý quan trọng

### `asdict()` là đệ quy

Điều này rất tiện lợi, nhưng nếu object chứa cấu trúc dữ liệu rất lớn hoặc tham chiếu lồng nhau phức tạp, việc chuyển đổi có thể tốn thời gian và bộ nhớ.

---

### `replace()` gọi lại `__init__()`

Điều này có nghĩa:

- `__post_init__()` sẽ chạy lại.
- Các kiểm tra hợp lệ (validation) cũng sẽ chạy lại.
- Với `InitVar`, bạn có thể phải truyền lại giá trị như đã học ở buổi trước.

---

### `fields()` không trả về `InitVar`

Chỉ các field thực sự của dataclass mới xuất hiện.

---

# Tổng kết

| Hàm | Vai trò |
| --- | --- |
| `fields()` | Lấy metadata field |
| `asdict()` | Chuyển thành `dict` (đệ quy) |
| `astuple()` | Chuyển thành `tuple` |
| `replace()` | Tạo object mới với một số thay đổi |
| `is_dataclass()` | Kiểm tra dataclass |
| `make_dataclass()` | Tạo dataclass động |

---

# Bài tập thực hành

## Bài 1

Thiết kế:

```text-x-trilium-auto
@dataclass class Chapter:
    id: int
    title: str
    url: str
```

Yêu cầu:

- Dùng `fields()` in ra:
  - tên field,
  - kiểu dữ liệu,
  - giá trị mặc định.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
@dataclass class Novel:
    title: str
    chapters: list[Chapter]
```

Yêu cầu:

- Tạo dữ liệu mẫu.
- Dùng:
  - `asdict()`
  - `astuple()`
- So sánh kết quả.

---

## Bài 3 (Áp dụng dự án crawler)

Viết hàm:

```text-x-trilium-auto
def model_to_json(obj) -> str:
    ...
```

Yêu cầu:

- Kiểm tra `is_dataclass(obj)`.
- Nếu đúng:
  - dùng `asdict()`,
  - chuyển sang JSON với `json.dumps(indent=4, ensure_ascii=False)`.
- Nếu không phải dataclass:
  - phát sinh `TypeError`.

Thử nghiệm với các model `Novel`, `Chapter`, `Author` của dự án crawler.

---

# Chuẩn bị cho Buổi 12

Buổi tiếp theo là **Dataclass Design Patterns & Best Practices** – buổi tổng kết chuyên sâu của toàn bộ khóa học.

Chúng ta sẽ học:

- Các mẫu thiết kế (Design Patterns) với dataclass.
- DTO (Data Transfer Object).
- Value Object.
- Entity.
- Configuration Object.
- Event Object.
- Request / Response Model.
- Khi nào nên dùng dataclass, khi nào nên dùng class thường, `NamedTuple`, `TypedDict` hoặc `attrs`.
- Kiến trúc dataclass cho hệ thống crawler truyện hoàn chỉnh.

Đây sẽ là buổi kết nối toàn bộ kiến thức của khóa học và đưa chúng vào cách thiết kế các dự án Python thực tế.