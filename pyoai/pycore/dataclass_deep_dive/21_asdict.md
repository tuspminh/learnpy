# Dataclass Deep Dive — Buổi 21

# `asdict()` và `astuple()` Deep Dive

Hôm nay bắt đầu **Phần III — Serialization**.

Hai hàm:

```python
asdict()
astuple()
```

trông rất đơn giản, nhưng bên trong có khá nhiều vấn đề quan trọng:

```text
Dataclass
   ↓
asdict()
   ↓
recursive traversal
   ↓
nested dataclass
   ↓
list / tuple / dict
   ↓
deep copy
```

Đặc biệt, bạn cần phân biệt:

> `asdict()` **không phải** một serializer JSON.

Nó chỉ chuyển dataclass thành cấu trúc Python built-in tương ứng.

---

# 1. `asdict()` là gì?

Ví dụ:

```python
from dataclasses import dataclass, asdict


@dataclass
class User:
    id: int
    name: str
    age: int


user = User(
    id=1,
    name="Alice",
    age=20,
)

data = asdict(user)

print(data)
```

Kết quả:

```text
{
    'id': 1,
    'name': 'Alice',
    'age': 20
}
```

Tức là:

```text
User instance
     ↓
asdict()
     ↓
dict
```

---

# 2. `asdict()` không trả về `User.__dict__`

Đây là điểm rất quan trọng.

Bạn có thể nghĩ:

```python
asdict(user)
```

chỉ đơn giản là:

```python
user.__dict__.copy()
```

Nhưng **không phải**.

Ví dụ:

```python
@dataclass
class User:
    id: int
    name: str
```

Có:

```python
user.__dict__
```

và:

```python
asdict(user)
```

Hai thứ này có semantics khác nhau.

`asdict()` hiểu:

```text
Dataclass structure
```

chứ không chỉ:

```text
instance dictionary
```

---

# 3. Dataclass lồng nhau

Đây mới là lý do `asdict()` tồn tại.

```python
@dataclass
class Address:
    city: str
    country: str


@dataclass
class User:
    name: str
    address: Address
```

Tạo:

```python
address = Address(
    city="Ho Chi Minh",
    country="Vietnam",
)

user = User(
    name="Alice",
    address=address,
)
```

Gọi:

```python
asdict(user)
```

Kết quả:

```python
{
    "name": "Alice",
    "address": {
        "city": "Ho Chi Minh",
        "country": "Vietnam"
    }
}
```

Nó **đệ quy** xuống `Address`.

---

# 4. Mental Model

Hãy nhớ:

```text
User
 │
 ├── name
 │
 └── address
       │
       ├── city
       └── country
```

`asdict()`:

```text
User
 ↓
dict
 ↓
address
 ↓
dict
```

---

# 5. `asdict()` xử lý container

Ví dụ:

```python
@dataclass
class User:
    name: str
    tags: list[str]
```

```python
user = User(
    name="Alice",
    tags=["python", "dataclass"],
)
```

```python
data = asdict(user)
```

Kết quả:

```python
{
    "name": "Alice",
    "tags": [
        "python",
        "dataclass"
    ]
}
```

---

# 6. List chứa Dataclass

Ví dụ:

```python
@dataclass
class Author:
    name: str


@dataclass
class Book:
    title: str
    authors: list[Author]
```

:

```python
book = Book(
    title="Python",
    authors=[
        Author("Alice"),
        Author("Bob"),
    ],
)
```

Gọi:

```python
asdict(book)
```

Kết quả:

```python
{
    "title": "Python",
    "authors": [
        {"name": "Alice"},
        {"name": "Bob"},
    ],
}
```

Nó recursive qua:

```text
Book
 ↓
authors
 ↓
list
 ↓
Author
 ↓
dict
```

---

# 7. Dict chứa Dataclass

```python
@dataclass
class User:
    name: str


@dataclass
class Group:
    users: dict[str, User]
```

:

```python
group = Group(
    users={
        "admin": User("Alice"),
        "member": User("Bob"),
    }
)
```

```python
asdict(group)
```

Kết quả:

```python
{
    "users": {
        "admin": {
            "name": "Alice"
        },
        "member": {
            "name": "Bob"
        }
    }
}
```

---

# 8. Tuple

```python
@dataclass
class Point:
    x: int
    y: int


@dataclass
class Shape:
    points: tuple[Point, ...]
```

:

```python
shape = Shape(
    points=(
        Point(1, 2),
        Point(3, 4),
    )
)
```

`asdict()`:

```python
{
    "points": (
        {
            "x": 1,
            "y": 2,
        },
        {
            "x": 3,
            "y": 4,
        },
    )
}
```

Tức là nó cố giữ kiểu container tương ứng.

---

# 9. `asdict()` hoạt động đệ quy

Mental model đơn giản:

```text
_dataclass instance
       │
       ▼
    fields()
       │
       ▼
 mỗi field value
       │
       ├── dataclass → recurse
       │
       ├── dict      → recurse
       │
       ├── list      → recurse
       │
       ├── tuple     → recurse
       │
       └── other     → deepcopy
```

Đây là phần cực kỳ quan trọng.

---

# 10. Deep Copy

`asdict()` có một behavior rất quan trọng:

> Các object không phải dataclass/container được xử lý bằng `copy.deepcopy()`.

Ví dụ:

```python
from dataclasses import dataclass, asdict


@dataclass
class User:
    name: str
    metadata: object
```

Giả sử:

```python
metadata = {
    "role": "admin"
}

user = User(
    "Alice",
    metadata,
)
```

Sau:

```python
data = asdict(user)
```

`metadata` không đơn giản là cùng object.

Nó được deep-copy theo cơ chế của `asdict()`.

---

# 11. Kiểm tra identity

```python
original = {
    "role": "admin"
}

user = User(
    "Alice",
    original,
)

data = asdict(user)

print(
    data["metadata"] is original
)
```

Thông thường:

```text
False
```

Vì object đã được copy.

---

# 12. Vì sao Deep Copy quan trọng?

Ví dụ:

```python
data = asdict(user)
```

Sau đó:

```python
data["metadata"]["role"] = "user"
```

Không nên làm thay đổi:

```python
user.metadata
```

Đây là một trong những lý do `asdict()` không chỉ đơn giản là:

```python
{
    f.name: getattr(obj, f.name)
    for f in fields(obj)
}
```

---

# 13. `asdict()` thực chất là transformation

Hãy nhìn nó như:

```text
Object Graph
     ↓
Python Data Graph
```

Ví dụ:

```text
User
 ├── Address
 │    ├── city
 │    └── country
 │
 └── list[Tag]
       ├── Tag
       └── Tag
```

sẽ trở thành:

```text
dict
 ├── address → dict
 │
 └── tags → list
```

---

# 14. `asdict()` chỉ nhận Dataclass Instance

Ví dụ:

```python
class User:
    pass
```

Gọi:

```python
asdict(User())
```

sẽ lỗi:

```text
TypeError
```

Vì:

```python
User
```

không phải dataclass.

---

# 15. Kiểm tra Dataclass

Python cung cấp:

```python
from dataclasses import is_dataclass
```

Ví dụ:

```python
@dataclass
class User:
    name: str
```

:

```python
is_dataclass(User)
```

```text
True
```

và:

```python
is_dataclass(User("Alice"))
```

cũng:

```text
True
```

---

# 16. Một điểm tinh tế: Class cũng là Dataclass

Đây là điều dễ gây nhầm.

```python
is_dataclass(User)
```

trả:

```text
True
```

Nhưng:

```python
is_dataclass(User("Alice"))
```

cũng:

```text
True
```

Nếu bạn muốn kiểm tra **instance thực sự**:

```python
is_dataclass(obj) and not isinstance(obj, type)
```

---

# 17. `asdict()` và `ClassVar`

Ví dụ:

```python
from typing import ClassVar


@dataclass
class User:
    name: str

    category: ClassVar[str] = "USER"
```

`category` không phải dataclass field.

Do đó:

```python
asdict(
    User("Alice")
)
```

chỉ chứa:

```python
{
    "name": "Alice"
}
```

Không có:

```python
"category"
```

---

# 18. `InitVar`

Tương tự:

```python
from dataclasses import (
    dataclass,
    InitVar,
)


@dataclass
class User:
    name: str
    password: InitVar[str]
```

`password` không phải stored field.

Vì vậy:

```python
asdict(user)
```

không có:

```text
password
```

Đây là một distinction quan trọng:

```text
constructor input
      ≠
stored state
```

---

# 19. `field(init=False)`

Ví dụ:

```python
@dataclass
class User:
    name: str
    slug: str = field(init=False)
```

`slug` vẫn là dataclass field.

Do đó:

```python
asdict(user)
```

có thể chứa:

```python
{
    "name": "Alice",
    "slug": "alice"
}
```

`init=False` chỉ ảnh hưởng constructor.

Nó **không có nghĩa**:

```text
ignore serialization
```

---

# 20. `repr=False` cũng vậy

```python
@dataclass
class User:
    name: str

    password: str = field(
        repr=False
    )
```

`password` không xuất hiện trong:

```python
repr(user)
```

nhưng vẫn xuất hiện trong:

```python
asdict(user)
```

Đây là hai cơ chế độc lập:

```text
repr=False
     ↓
repr()

asdict()
     ↓
serialization
```

---

# 21. `metadata` cũng không tự xuất hiện

Ví dụ:

```python
@dataclass
class User:
    name: str = field(
        metadata={
            "json_name": "user_name"
        }
    )
```

`asdict()` vẫn trả:

```python
{
    "name": "Alice"
}
```

chứ không tự động:

```python
{
    "user_name": "Alice"
}
```

`metadata` chỉ là metadata.

Framework serializer phải tự đọc nó.

---

# 22. Đây là điểm rất quan trọng khi xây Framework

Nếu bạn muốn:

```python
field(
    metadata={
        "json_name": "user_name"
    }
)
```

thì serializer riêng phải làm:

```text
Field
 ↓
metadata
 ↓
json_name
 ↓
output key
```

`asdict()` không phải serializer framework.

---

# 23. `astuple()`

Bây giờ:

```python
from dataclasses import astuple
```

Ví dụ:

```python
@dataclass
class User:
    id: int
    name: str
    age: int
```

:

```python
user = User(
    1,
    "Alice",
    20,
)
```

```python
astuple(user)
```

Kết quả:

```python
(
    1,
    "Alice",
    20,
)
```

---

# 24. `asdict()` vs `astuple()`

|                  | `asdict()` | `astuple()` |
| ---------------- | ---------- | ----------- |
| Output           | `dict`     | `tuple`     |
| Field name       | Có         | Không       |
| Nested dataclass | Recursive  | Recursive   |
| Container        | Recursive  | Recursive   |
| Deep copy        | Có         | Có          |

Ví dụ:

```text
User
 ├── id
 ├── name
 └── age
```

`asdict()`:

```python
{
    "id": 1,
    "name": "Alice",
    "age": 20,
}
```

`astuple()`:

```python
(
    1,
    "Alice",
    20,
)
```

---

# 25. Khi nào `astuple()` hữu ích?

Ví dụ database:

```python
@dataclass
class User:
    id: int
    name: str
    age: int
```

SQL:

```sql
INSERT INTO users
(id, name, age)
VALUES (?, ?, ?)
```

Bạn có thể:

```python
cursor.execute(
    """
    INSERT INTO users
    (id, name, age)
    VALUES (?, ?, ?)
    """,
    astuple(user),
)
```

Đây là một use case thực tế.

---

# 26. Nhưng hãy cẩn thận

`astuple()` phụ thuộc vào:

```text
field order
```

Nếu dataclass:

```python
@dataclass
class User:
    name: str
    age: int
    id: int
```

thì:

```python
astuple(user)
```

là:

```python
(
    name,
    age,
    id,
)
```

Không phải:

```python
(
    id,
    name,
    age,
)
```

Do đó dùng `astuple()` với SQL positional parameters cần đặc biệt cẩn thận.

---

# 27. Nested `asdict()`

Ví dụ crawler của bạn:

```python
@dataclass
class Author:
    id: int
    name: str


@dataclass
class Chapter:
    id: int
    title: str


@dataclass
class Novel:
    id: int
    title: str
    author: Author
    chapters: list[Chapter]
```

Tạo:

```python
novel = Novel(
    id=1,
    title="Python Story",
    author=Author(
        id=10,
        name="Alice",
    ),
    chapters=[
        Chapter(1, "Chapter 1"),
        Chapter(2, "Chapter 2"),
    ],
)
```

`asdict(novel)` sẽ tạo:

```python
{
    "id": 1,
    "title": "Python Story",

    "author": {
        "id": 10,
        "name": "Alice",
    },

    "chapters": [
        {
            "id": 1,
            "title": "Chapter 1",
        },
        {
            "id": 2,
            "title": "Chapter 2",
        },
    ],
}
```

---

# 28. Đây là Object Graph Traversal

Không nên nghĩ:

```text
asdict()
=
object.__dict__()
```

Hãy nghĩ:

```text
asdict()
=
recursive object graph traversal
```

Nó đi qua:

```text
root object
   ↓
fields
   ↓
field values
   ↓
containers
   ↓
nested dataclasses
   ↓
leaf objects
```

---

# 29. Vấn đề Circular Reference

Đây là một vấn đề quan trọng.

Ví dụ:

```python
@dataclass
class Node:
    name: str
    parent: object = None
```

Ta có:

```python
root = Node("root")
child = Node("child", root)

root.parent = child
```

Graph:

```text
root
 ↓
child
 ↓
root
 ↓
child
 ↓
...
```

Đây là circular reference.

`asdict()` không phải một graph serializer tổng quát có cơ chế xử lý vòng tham chiếu tùy ý.

Bạn không nên đưa object graph cyclic vào `asdict()` và kỳ vọng nó tự giải quyết như một serializer graph-aware.

---

# 30. Performance

Đây là phần rất quan trọng.

Giả sử:

```text
Novel
 ├── Author
 ├── Category × 10
 ├── Chapter × 1000
 │     ├── Image × 5
 │     └── ...
```

Gọi:

```python
asdict(novel)
```

có thể tạo ra một cấu trúc Python hoàn toàn mới.

Conceptually:

```text
Original Object Graph
        ↓
Traverse
        ↓
Allocate dict/list/tuple
        ↓
Deep-copy leaves
        ↓
New Object Graph
```

Chi phí có thể lớn.

---

# 31. Vì sao `asdict()` có thể chậm?

Không chỉ vì recursion.

Mà còn:

```text
allocation
+
recursion
+
container reconstruction
+
deepcopy
```

Ví dụ:

```text
1 Novel
1000 Chapters
5000 Images
```

thì serialization toàn bộ graph có thể khá đắt.

---

# 32. Không nên dùng `asdict()` để lấy một field

Ví dụ:

```python
user_id = asdict(user)["id"]
```

Đây là thiết kế không tốt.

Bạn đã serialize **toàn bộ object** chỉ để lấy một giá trị.

Nên:

```python
user_id = user.id
```

---

# 33. Không nên dùng `asdict()` trong hot loop

Ví dụ:

```python
for chapter in chapters:
    data = asdict(chapter)
    save(data)
```

Nếu có hàng chục nghìn chapter:

```text
asdict()
asdict()
asdict()
...
```

có thể trở thành bottleneck.

Đặc biệt trong crawler:

```text
crawl
 ↓
parse
 ↓
model
 ↓
asdict
 ↓
database
```

nếu làm không cẩn thận sẽ tạo rất nhiều object trung gian.

---

# 34. Tự viết shallow serializer

Nếu bạn chỉ cần field values:

```python
from dataclasses import fields


def shallow_asdict(obj):
    return {
        f.name: getattr(obj, f.name)
        for f in fields(obj)
    }
```

Ví dụ:

```python
data = shallow_asdict(user)
```

Điểm khác:

```text
asdict()
    ↓
recursive + deepcopy

shallow_asdict()
    ↓
top-level only
```

---

# 35. So sánh

```python
data = asdict(user)
```

với:

```python
data = {
    f.name: getattr(user, f.name)
    for f in fields(user)
}
```

Cái thứ hai:

* không recurse nested dataclass
* không deep-copy
* nhanh hơn trong nhiều trường hợp
* nhưng không có semantics giống `asdict()`

Không được coi hai cái là tương đương.

---

# 36. Benchmark

Ví dụ:

```python
from dataclasses import dataclass, asdict, fields
import timeit


@dataclass
class User:
    id: int
    name: str
    age: int


user = User(
    1,
    "Alice",
    20,
)
```

Benchmark:

```python
def shallow():
    return {
        f.name: getattr(user, f.name)
        for f in fields(user)
    }


def deep():
    return asdict(user)
```

:

```python
print(
    timeit.timeit(
        deep,
        number=100_000,
    )
)

print(
    timeit.timeit(
        shallow,
        number=100_000,
    )
)
```

Bạn sẽ thấy performance không giống nhau.

Nhưng đừng kết luận rằng shallow luôn nhanh hơn trong mọi cấu trúc; hãy benchmark đúng object graph của ứng dụng.

---

# 37. Một cách serialize tốt hơn cho Database

Nếu mục tiêu là SQLite:

```python
@dataclass
class User:
    id: int
    name: str
    age: int
```

Không nhất thiết:

```python
asdict(user)
```

Bạn có thể:

```python
def to_row(user):
    return (
        user.id,
        user.name,
        user.age,
    )
```

Hoặc:

```python
def to_row(obj):
    return tuple(
        getattr(obj, f.name)
        for f in fields(obj)
    )
```

Đây có thể phù hợp hơn với repository.

---

# 38. Đây là một Design Insight

Không có:

> "Một serializer tốt nhất cho mọi trường hợp."

Có:

```text
asdict()
    ↓
general-purpose recursive conversion

shallow serializer
    ↓
top-level conversion

to_row()
    ↓
database

to_json()
    ↓
JSON API

to_message()
    ↓
queue
```

Serializer nên phục vụ **boundary cụ thể**.

---

# 39. `asdict()` và API

Giả sử:

```python
@dataclass
class User:
    id: int
    name: str
```

Bạn có thể:

```python
payload = asdict(user)
```

Sau đó:

```python
json.dumps(payload)
```

Nhưng:

> `asdict()` không đảm bảo tất cả giá trị đều JSON serializable.

Ví dụ:

```python
@dataclass
class Event:
    timestamp: datetime
```

`asdict()` vẫn cho:

```python
{
    "timestamp": datetime(...)
}
```

Nhưng:

```python
json.dumps(...)
```

có thể fail.

---

# 40. Đây là lý do Buổi 22 sẽ quan trọng

Pipeline thực tế:

```text
Dataclass
    ↓
asdict()
    ↓
dict
    ↓
json.dumps()
    ↓
JSON
```

Nhưng:

```text
Dataclass
    ↓
asdict()
```

chưa đảm bảo:

```text
JSON compatible
```

Buổi 22 chúng ta sẽ đi sâu:

```text
json
orjson
msgspec
custom encoder
datetime
Enum
UUID
Decimal
nested dataclass
```

---

# 41. `asdict()` không đổi tên field

Ví dụ:

```python
@dataclass
class User:
    first_name: str
```

```python
asdict(user)
```

cho:

```python
{
    "first_name": "Alice"
}
```

Nó không tự biến thành:

```python
{
    "firstName": "Alice"
}
```

Muốn camelCase:

```text
field
 ↓
naming policy
 ↓
serializer
```

Bạn cần serializer riêng.

---

# 42. Custom Serializer

Ví dụ đơn giản:

```python
from dataclasses import fields


def serialize(obj):
    result = {}

    for f in fields(obj):
        value = getattr(obj, f.name)

        result[f.name.upper()] = value

    return result
```

Ví dụ:

```python
serialize(
    User(
        1,
        "Alice",
        20,
    )
)
```

Kết quả:

```python
{
    "ID": 1,
    "NAME": "Alice",
    "AGE": 20,
}
```

Đây là ý tưởng nền tảng để sau này tự xây serialization framework.

---

# 43. `asdict()` và `metadata`

Bạn có thể xây:

```python
@dataclass
class User:
    name: str = field(
        metadata={
            "json_name": "userName"
        }
    )
```

Custom serializer:

```python
def serialize(obj):
    result = {}

    for f in fields(obj):
        key = f.metadata.get(
            "json_name",
            f.name,
        )

        result[key] = getattr(
            obj,
            f.name,
        )

    return result
```

Kết quả:

```python
{
    "userName": "Alice"
}
```

Đây chính là pattern framework.

---

# 44. `asdict()` và security

Đây là một điểm rất thực tế.

Giả sử:

```python
@dataclass
class User:
    id: int
    name: str
    password_hash: str
```

Bạn gọi:

```python
asdict(user)
```

thì:

```python
password_hash
```

vẫn xuất hiện.

`repr=False` không giúp:

```python
@dataclass
class User:
    password_hash: str = field(
        repr=False
    )
```

vì:

```text
repr=False
```

chỉ ảnh hưởng `repr()`.

Nếu API không được trả password:

```text
不要:
asdict(user)

nên:
UserResponse(...)
```

---

# 45. DTO Boundary

Đây là một pattern cực kỳ quan trọng.

Không nên:

```text
Database Entity
      ↓
asdict()
      ↓
API Response
```

một cách máy móc.

Tốt hơn:

```text
Database Entity
      ↓
Response DTO
      ↓
serializer
      ↓
API
```

Ví dụ:

```python
@dataclass
class UserEntity:
    id: int
    name: str
    password_hash: str


@dataclass
class UserResponse:
    id: int
    name: str
```

Sau đó:

```python
response = UserResponse(
    id=user.id,
    name=user.name,
)
```

Rồi:

```python
asdict(response)
```

Đây là kiến trúc sạch hơn.

---

# 46. Bài tập 1

Tạo:

```python
@dataclass
class Address:
    city: str
    country: str


@dataclass
class User:
    name: str
    address: Address
    tags: list[str]
```

Thực hiện:

```python
asdict(user)
```

và giải thích chính xác cấu trúc kết quả.

---

# 47. Bài tập 2

Tạo:

```python
@dataclass
class Author:
    name: str


@dataclass
class Book:
    title: str
    author: Author
    categories: list[str]
```

So sánh:

```python
book.__dict__
```

với:

```python
asdict(book)
```

Mục tiêu là hiểu:

> Vì sao `asdict()` không đơn giản là `__dict__`.

---

# 48. Bài tập 3 — Deep Copy

Tạo:

```python
@dataclass
class User:
    name: str
    metadata: dict
```

Sau:

```python
data = asdict(user)
```

kiểm tra:

```python
data["metadata"] is user.metadata
```

Sau đó sửa:

```python
data["metadata"]["role"] = "admin"
```

và kiểm tra object gốc.

---

# 49. Bài tập 4 — Crawler

Thiết kế:

```python
@dataclass
class Image:
    url: str


@dataclass
class Chapter:
    title: str
    images: list[Image]


@dataclass
class Novel:
    title: str
    chapters: list[Chapter]
```

Tạo:

```text
Novel
 └── 100 Chapter
       └── 10 Image
```

Sau đó benchmark:

```python
asdict(novel)
```

và một serializer shallow/custom.

Mục tiêu:

> Quan sát chi phí serialization khi object graph lớn.

---

# 50. Bài tập 5 — Repository

Viết:

```python
def to_db_row(obj):
    ...
```

để:

```python
@dataclass
class User:
    id: int
    name: str
    age: int
```

trả:

```python
(
    1,
    "Alice",
    20,
)
```

Sau đó dùng trực tiếp:

```python
cursor.execute(
    """
    INSERT INTO users
    (id, name, age)
    VALUES (?, ?, ?)
    """,
    to_db_row(user),
)
```

Đây sẽ chuẩn bị trực tiếp cho:

```text
Dataclass + SQLite
```

ở **Buổi 32**.

---

# 51. Mental Model cần nhớ

Đừng ghi nhớ `asdict()` đơn giản là:

```text
dataclass → dict
```

Hãy ghi nhớ chính xác hơn:

```text
                    asdict()
                       │
                       ▼
               Dataclass instance
                       │
                       ▼
                  fields()
                       │
                       ▼
               recursive traversal
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Dataclass       container        other
        │              │              │
        ▼              ▼              ▼
     recurse         recurse       deepcopy
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                     dict
```

Còn:

```text
astuple()
```

là cùng ý tưởng nhưng root result là:

```text
tuple
```

---

# 52. Roadmap hiện tại

Bạn đã hoàn thành:

```text
Phần I — Foundation
01 Dataclass
02 Generated Methods
03 Type Hint
04 Field
05 Frozen
06 Ordering
07 Slots
08 Keyword Only
09 InitVar
10 post_init

Phần II — Advanced
11 Inheritance
12 Multiple Inheritance
13 Composition
14 Recursive
15 Generic
16 Abstract
17 Protocol
18 Descriptor
19 Metaclass
20 Dynamic Dataclass

Phần III — Serialization
21 asdict / astuple   ← hôm nay
22 JSON
23 YAML / TOML / XML
24 Pickle / copy / deepcopy
```

### Buổi 22

Chúng ta sẽ đi sâu vào:

```text
Dataclass
    ↓
JSON
    ↓
json.dumps()
```

sau đó so sánh:

```text
json
vs
orjson
vs
msgspec
```

và đặc biệt tìm hiểu **vì sao `asdict() → json.dumps()` thường không phải là lựa chọn tối ưu cho hệ thống crawler/API có lượng dữ liệu lớn**.
