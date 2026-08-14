# Dataclass Deep Dive — Buổi 20

# Dynamic Dataclass với `make_dataclass()`

Hôm nay chúng ta hoàn thành **Phần II — Advanced**.

Nếu các buổi trước bạn tạo class bằng:

```python
@dataclass
class User:
    id: int
    name: str
```

thì hôm nay chúng ta sẽ học cách:

> **Tạo một Dataclass hoàn toàn tại runtime.**

Đây là nền tảng rất quan trọng cho:

* ORM
* Dynamic Model
* Schema → Model
* Database → Model
* API Schema
* Plugin System
* Code generation
* Framework

---

# 1. Static Dataclass vs Dynamic Dataclass

Thông thường:

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
```

Class đã biết trước khi chương trình chạy.

Ta gọi đây là:

```text
Static definition
```

Trong dynamic dataclass:

```text
Runtime
   ↓
đọc schema
   ↓
tạo fields
   ↓
tạo class
   ↓
dataclass
```

Ví dụ:

```python
schema = {
    "id": int,
    "name": str,
    "age": int,
}
```

Sau đó:

```text
schema
   ↓
Dynamic Dataclass
   ↓
User
```

---

# 2. `make_dataclass()`

Python cung cấp:

```python
from dataclasses import make_dataclass
```

Cú pháp cơ bản:

```python
User = make_dataclass(
    "User",
    [
        ("id", int),
        ("name", str),
        ("age", int),
    ],
)
```

Bây giờ:

```python
user = User(
    id=1,
    name="Alice",
    age=20,
)
```

Hoàn toàn giống:

```python
@dataclass
class User:
    id: int
    name: str
    age: int
```

---

# 3. Kiểm tra

```python
print(User)
```

Có thể thấy:

```text
<class 'types.User'>
```

Sau đó:

```python
print(user)
```

Kết quả dạng:

```text
User(id=1, name='Alice', age=20)
```

---

# 4. `make_dataclass()` không phải magic

Conceptually:

```python
User = make_dataclass(
    "User",
    [
        ("id", int),
        ("name", str),
    ],
)
```

thực hiện một pipeline gần như:

```text
fields definition
      ↓
tạo class
      ↓
gắn annotations
      ↓
@dataclass
      ↓
generated methods
      ↓
return class
```

Nó là một dạng **runtime class generation**.

---

# 5. Cấu trúc field

Mỗi field có thể biểu diễn bằng:

```python
("name", str)
```

hoặc:

```python
("name", str, field(...))
```

Ví dụ:

```python
from dataclasses import (
    make_dataclass,
    field,
)


User = make_dataclass(
    "User",
    [
        ("id", int),
        (
            "name",
            str,
            field(default="Unknown"),
        ),
    ],
)
```

Ta có:

```python
User(id=1)
```

Kết quả:

```text
User(id=1, name='Unknown')
```

---

# 6. Dynamic Default Factory

Ví dụ:

```python
from dataclasses import (
    make_dataclass,
    field,
)


User = make_dataclass(
    "User",
    [
        ("name", str),
        (
            "tags",
            list[str],
            field(default_factory=list),
        ),
    ],
)
```

Bây giờ:

```python
u1 = User("Alice")
u2 = User("Bob")
```

Kiểm tra:

```python
u1.tags.append("python")

print(u1.tags)
print(u2.tags)
```

Kết quả:

```text
['python']
[]
```

Vì mỗi instance có list riêng.

---

# 7. Dynamic Dataclass từ Dictionary

Đây là ứng dụng rất quan trọng.

Giả sử:

```python
schema = {
    "id": int,
    "name": str,
    "age": int,
}
```

Ta chuyển thành:

```python
fields = [
    (name, type_)
    for name, type_ in schema.items()
]
```

Sau đó:

```python
User = make_dataclass(
    "User",
    fields,
)
```

Ta vừa biến:

```text
dictionary
```

thành:

```text
Dataclass
```

---

# 8. Viết Factory

Tốt hơn là đóng gói:

```python
from dataclasses import make_dataclass


def create_model(name, schema):

    fields = [
        (field_name, field_type)
        for field_name, field_type
        in schema.items()
    ]

    return make_dataclass(
        name,
        fields,
    )
```

Sử dụng:

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
        "age": int,
    },
)
```

Sau đó:

```python
user = User(
    1,
    "Alice",
    20,
)
```

---

# 9. Đây chính là Model Generator

Ta có:

```text
schema
   ↓
create_model()
   ↓
make_dataclass()
   ↓
Dataclass
```

Đây là pattern rất quan trọng:

```text
Schema → Model Generator
```

Sau này bạn có thể làm:

```text
JSON Schema
     ↓
Dataclass
```

hoặc:

```text
SQLite schema
     ↓
Dataclass
```

hoặc:

```text
API response schema
     ↓
Dataclass
```

---

# 10. Dynamic Dataclass + `field()`

Ví dụ:

```python
User = make_dataclass(
    "User",
    [
        (
            "id",
            int,
            field(
                metadata={
                    "primary_key": True
                }
            ),
        ),
        (
            "name",
            str,
            field(
                metadata={
                    "required": True
                }
            ),
        ),
    ],
)
```

Sau đó:

```python
from dataclasses import fields

for f in fields(User):
    print(
        f.name,
        f.type,
        f.metadata,
    )
```

Conceptually:

```text
id
 └── primary_key=True

name
 └── required=True
```

---

# 11. Dynamic Dataclass + `kw_only`

Bạn cũng có thể:

```python
User = make_dataclass(
    "User",
    [
        ("id", int),
        ("name", str),
    ],
    kw_only=True,
)
```

Bây giờ:

```python
User(
    id=1,
    name="Alice",
)
```

hoạt động.

Nhưng:

```python
User(1, "Alice")
```

sẽ không phù hợp với keyword-only constructor.

---

# 12. Dynamic Dataclass + `frozen`

```python
User = make_dataclass(
    "User",
    [
        ("id", int),
        ("name", str),
    ],
    frozen=True,
)
```

Sau đó:

```python
user = User(1, "Alice")
```

Không thể:

```python
user.name = "Bob"
```

vì object frozen.

---

# 13. Dynamic Dataclass + `slots`

```python
User = make_dataclass(
    "User",
    [
        ("id", int),
        ("name", str),
    ],
    slots=True,
)
```

Tương đương về ý tưởng với:

```python
@dataclass(slots=True)
class User:
    id: int
    name: str
```

---

# 14. Dynamic Dataclass + inheritance

Ta có:

```python
@dataclass
class Entity:
    id: int
```

Sau đó:

```python
User = make_dataclass(
    "User",
    [
        ("name", str),
    ],
    bases=(Entity,),
)
```

Bây giờ:

```python
user = User(
    id=1,
    name="Alice",
)
```

Ta có:

```text
Entity
  │
  └── id
       ↓
User
  └── name
```

---

# 15. Dynamic Dataclass + methods

Một class runtime không nhất thiết chỉ có fields.

Ta có thể truyền namespace.

Ví dụ:

```python
def greet(self):
    return f"Hello {self.name}"
```

Sau đó tạo class:

```python
User = make_dataclass(
    "User",
    [
        ("name", str),
    ],
    namespace={
        "greet": greet,
    },
)
```

Bây giờ:

```python
user = User("Alice")

print(user.greet())
```

Kết quả:

```text
Hello Alice
```

---

# 16. Đây là bước rất quan trọng

Dynamic Dataclass không chỉ là:

```text
fields → class
```

mà có thể là:

```text
fields
+
methods
+
base classes
+
configuration
        ↓
Dynamic Model
```

Nó bắt đầu giống một **framework model generator**.

---

# 17. Dynamic Model Factory

Ta có thể thiết kế:

```python
def create_model(
    name,
    fields,
    *,
    bases=(),
    namespace=None,
    frozen=False,
    slots=False,
):
    ...
```

Ví dụ:

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
    },
    frozen=True,
    slots=True,
)
```

Đây là abstraction tốt hơn việc gọi `make_dataclass()` trực tiếp khắp codebase.

---

# 18. Dynamic Dataclass từ Database

Đây mới là ứng dụng thực tế.

Giả sử database có:

```text
users
--------------------------------
id       INTEGER
name     TEXT
age      INTEGER
email    TEXT
```

Ta có metadata:

```python
schema = {
    "id": int,
    "name": str,
    "age": int,
    "email": str,
}
```

Sau đó:

```python
User = create_model(
    "User",
    schema,
)
```

Ta vừa tạo:

```text
Database Schema
       ↓
Python Type Schema
       ↓
Dataclass
```

---

# 19. Dynamic Dataclass trong ORM

Có thể xây:

```text
Database
    ↓
PRAGMA table_info()
    ↓
Column metadata
    ↓
Python type mapping
    ↓
make_dataclass()
    ↓
Model
```

Ví dụ:

```text
SQLite
   ↓
users
   ↓
id INTEGER
name TEXT
age INTEGER
   ↓
User dataclass
```

Đây là nền tảng của:

> Database reflection.

---

# 20. Dynamic Dataclass từ SQLite

Ví dụ metadata:

```python
columns = [
    ("id", int),
    ("name", str),
    ("age", int),
]
```

Ta có:

```python
User = make_dataclass(
    "User",
    columns,
)
```

Query database:

```python
row = (1, "Alice", 20)
```

Sau đó:

```python
user = User(*row)
```

Kết quả:

```text
User(id=1, name='Alice', age=20)
```

---

# 21. Đây chính là Pattern sẽ rất hữu ích cho project crawler

Trong crawler của bạn có thể có:

```text
Novel
Chapter
Author
Category
Image
DownloadTask
CrawlerTask
```

Thay vì tất cả đều phải hard-code ở một số hệ thống dynamic:

```text
Plugin
   ↓
Schema
   ↓
Dynamic Model
```

Ví dụ plugin cung cấp:

```python
novel_schema = {
    "id": int,
    "title": str,
    "url": str,
}
```

Framework:

```python
Novel = create_model(
    "Novel",
    novel_schema,
)
```

---

# 22. Dynamic Dataclass và Plugin Architecture

Hãy hình dung:

```text
Crawler Plugin
      │
      │ schema
      ▼
Model Factory
      │
      ▼
Dynamic Dataclass
      │
      ▼
Repository
      │
      ▼
SQLite
```

Điều này rất mạnh khi framework phải hỗ trợ nhiều plugin.

---

# 23. `make_dataclass()` vs `type()`

Có hai cách tạo class runtime.

### `type()`

```python
User = type(
    "User",
    (),
    namespace,
)
```

### `make_dataclass()`

```python
User = make_dataclass(
    "User",
    fields,
)
```

Điểm khác biệt:

```text
type()
 ↓
raw class creation

make_dataclass()
 ↓
dataclass-aware class creation
```

---

# 24. Khi nào dùng `type()`?

Dùng khi bạn muốn tạo:

```text
behavior-heavy class
```

Ví dụ dynamic methods.

---

# 25. Khi nào dùng `make_dataclass()`?

Khi class chủ yếu là:

```text
data
+
fields
+
generated methods
```

Ví dụ:

```text
DTO
Entity
Configuration
Schema
API Response
Database Record
```

---

# 26. `make_dataclass()` và `dataclass()`

Có thể hình dung:

```python
@dataclass
class User:
    id: int
```

là:

```text
Developer biết schema
        ↓
Class syntax
        ↓
@dataclass
```

Trong khi:

```python
User = make_dataclass(...)
```

là:

```text
Program biết schema
        ↓
Runtime generation
        ↓
Dataclass
```

Đây là distinction quan trọng.

---

# 27. Runtime Schema

Ví dụ:

```python
schemas = {
    "User": {
        "id": int,
        "name": str,
    },

    "Novel": {
        "id": int,
        "title": str,
    },
}
```

Ta có thể:

```python
models = {}

for name, schema in schemas.items():
    models[name] = create_model(
        name,
        schema,
    )
```

Kết quả:

```text
models
 ├── User
 └── Novel
```

---

# 28. Đây là một Model Registry

```python
models["User"]
```

là:

```python
User
```

và:

```python
models["Novel"]
```

là:

```python
Novel
```

Đây là nền tảng để xây:

```text
Dynamic ORM
Schema Registry
Plugin Framework
Serialization Framework
```

---

# 29. Một vấn đề lớn: Type Mapping

Database có:

```text
INTEGER
TEXT
REAL
BLOB
```

Python có:

```text
int
str
float
bytes
```

Ta có thể tạo:

```python
SQLITE_TYPES = {
    "INTEGER": int,
    "TEXT": str,
    "REAL": float,
    "BLOB": bytes,
}
```

Sau đó:

```text
SQLite schema
      ↓
SQLITE_TYPES
      ↓
Python annotations
      ↓
make_dataclass()
```

Đây chính là bước đầu của mini ORM.

---

# 30. Dynamic Dataclass không tự validate type

Ví dụ:

```python
User = make_dataclass(
    "User",
    [
        ("age", int),
    ],
)
```

Ta vẫn có thể:

```python
user = User("hello")
```

Dataclass không tự động:

```text
assert isinstance(age, int)
```

Đây là một misconception rất phổ biến.

```text
Type hint
   ≠
Runtime validation
```

Muốn validation phải thêm:

```text
__post_init__
Descriptor
Validator
External library
```

---

# 31. Dynamic Dataclass + `__post_init__`

Có thể truyền method:

```python
def __post_init__(self):
    if self.age < 0:
        raise ValueError(
            "age must be >= 0"
        )
```

Sau đó:

```python
User = make_dataclass(
    "User",
    [
        ("name", str),
        ("age", int),
    ],
    namespace={
        "__post_init__": __post_init__,
    },
)
```

Bây giờ validation hoạt động.

---

# 32. Dynamic Model Factory hoàn chỉnh hơn

Ta có thể viết:

```python
from dataclasses import (
    make_dataclass,
)


def create_model(
    name,
    schema,
    *,
    namespace=None,
    bases=(),
    frozen=False,
    slots=False,
    kw_only=False,
):
    fields = [
        (field_name, field_type)
        for field_name, field_type
        in schema.items()
    ]

    return make_dataclass(
        name,
        fields,
        bases=bases,
        namespace=namespace,
        frozen=frozen,
        slots=slots,
        kw_only=kw_only,
    )
```

Ví dụ:

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
    },
)
```

---

# 33. Nhưng có một vấn đề với Dynamic Class

Nếu tạo:

```python
User1 = create_model(...)
User2 = create_model(...)
```

dù schema giống nhau:

```python
User1 is User2
```

sẽ là:

```text
False
```

Chúng là hai class khác nhau.

Điều này ảnh hưởng đến:

```text
identity
isinstance
pickle
cache
serialization
```

---

# 34. Dynamic Class Cache

Ta có thể cache:

```python
_cache = {}
```

Key:

```text
model name
+
schema
+
configuration
```

Concept:

```python
key = (
    name,
    tuple(schema.items()),
)
```

Sau đó:

```python
if key in _cache:
    return _cache[key]
```

Nếu không:

```python
model = make_dataclass(...)
_cache[key] = model
return model
```

Đây là pattern rất quan trọng trong framework.

---

# 35. Dynamic Dataclass + Serialization

Ở Phần III chúng ta sẽ đi sâu:

```text
Dynamic Dataclass
        ↓
asdict()
        ↓
JSON
```

Ví dụ:

```python
from dataclasses import asdict

user = User(
    1,
    "Alice",
)

data = asdict(user)
```

Kết quả:

```python
{
    "id": 1,
    "name": "Alice",
}
```

---

# 36. Dynamic Dataclass + API

Giả sử server trả:

```json
{
    "id": 1,
    "name": "Alice",
    "age": 20
}
```

Runtime schema:

```python
schema = {
    "id": int,
    "name": str,
    "age": int,
}
```

Tạo:

```python
User = create_model(
    "User",
    schema,
)
```

Sau đó:

```python
user = User(**payload)
```

Ta vừa có:

```text
JSON
 ↓
dict
 ↓
Dynamic Dataclass
```

---

# 37. Nhưng Dynamic Dataclass không phải lúc nào cũng tốt

Không nên dùng nếu:

```text
schema đã biết
class đơn giản
codebase cần static analysis mạnh
IDE autocomplete quan trọng
```

Trong trường hợp đó:

```python
@dataclass
class User:
    id: int
    name: str
```

rõ ràng hơn rất nhiều.

---

# 38. Khi nào Dynamic Dataclass thực sự có giá trị?

Khi schema đến từ:

```text
Database
API
Plugin
Configuration
User-defined schema
JSON Schema
Metadata
Runtime configuration
```

Tức là:

> **Schema không biết trước khi viết source code.**

---

# 39. So sánh

|                 | Static Dataclass    | Dynamic Dataclass |
| --------------- | ------------------- | ----------------- |
| Schema          | Compile/source time | Runtime           |
| IDE             | Rất tốt             | Hạn chế           |
| Type checker    | Tốt                 | Hạn chế           |
| Flexibility     | Thấp hơn            | Rất cao           |
| ORM reflection  | Khó hơn             | Phù hợp           |
| Plugin          | Hạn chế             | Rất phù hợp       |
| Code generation | Không cần           | Rất phù hợp       |

---

# 40. Mini Project — Dynamic Model Factory

Hãy xây:

```text
dynamic_model/
│
├── factory.py
├── schema.py
├── registry.py
└── main.py
```

### `schema.py`

```python
USER_SCHEMA = {
    "id": int,
    "name": str,
    "age": int,
}
```

### `factory.py`

```python
from dataclasses import make_dataclass


def create_model(name, schema):

    fields = [
        (name, type_)
        for name, type_ in schema.items()
    ]

    return make_dataclass(
        name,
        fields,
    )
```

### `main.py`

```python
from factory import create_model
from schema import USER_SCHEMA


User = create_model(
    "User",
    USER_SCHEMA,
)


user = User(
    1,
    "Alice",
    20,
)

print(user)
```

Output:

```text
User(id=1, name='Alice', age=20)
```

---

# 41. Bài tập nâng cao

Hãy mở rộng factory để hỗ trợ:

```python
schema = {
    "id": {
        "type": int,
        "primary_key": True,
    },

    "name": {
        "type": str,
        "required": True,
    },

    "age": {
        "type": int,
        "default": 0,
    },
}
```

Factory phải biến thành:

```text
Schema
   ↓
Field
   ↓
metadata
   ↓
make_dataclass
   ↓
Model
```

Ví dụ:

```python
User = create_model(
    "User",
    schema,
)
```

và:

```python
from dataclasses import fields

for f in fields(User):
    print(
        f.name,
        f.type,
        f.metadata,
    )
```

---

# 42. Đây là bài tập rất quan trọng

Nếu bạn làm được factory trên, bạn đã bắt đầu chuyển từ:

```text
Dataclass user
```

sang:

```text
Dataclass framework designer
```

Đặc biệt nó liên quan trực tiếp đến dự án crawler của bạn:

```text
Crawler Plugin
       ↓
Entity Schema
       ↓
Model Factory
       ↓
Dataclass
       ↓
Repository
       ↓
SQLite
```

---

# 43. Tổng kết Phần II

Chúng ta đã đi qua:

```text
11. Inheritance
       ↓
12. Multiple Inheritance / MRO
       ↓
13. Composition
       ↓
14. Recursive Dataclass
       ↓
15. Generic Dataclass
       ↓
16. Abstract Dataclass
       ↓
17. Protocol
       ↓
18. Descriptor
       ↓
19. Metaclass
       ↓
20. Dynamic Dataclass
```

Đến đây bạn không còn chỉ biết:

```python
@dataclass
class User:
    ...
```

mà đã hiểu Dataclass ở cả ba tầng:

```text
                    Dataclass
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Language       Runtime         Framework
    syntax        mechanics         design
        │              │              │
   decorator       generated      model factory
   field           methods        ORM
   inheritance     metadata       DTO
   frozen          slots          plugin
   generic         reflection     schema
```

---

# Phần III — Serialization

Tiếp theo là:

## **Buổi 21 — `asdict()` và `astuple()` Deep Dive**

Chúng ta sẽ không chỉ học:

```python
asdict(user)
```

mà sẽ mổ xẻ:

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
deepcopy
```

và đặc biệt tìm hiểu **vì sao `asdict()` có thể tốn chi phí rất lớn**, khi nào không nên dùng nó, và cách tự xây một serializer nhanh hơn cho hệ thống crawler/SQLite của bạn.
