Rất hay. Vì bạn đã học OOP, SQLite3, PySide6, AsyncIO, Repository Pattern và đang xây dựng hệ thống crawler nên mình sẽ dạy **dataclass** ở mức **Professional/Deep Dive**, không chỉ dừng ở cú pháp.

Mục tiêu là sau khóa này bạn có thể đọc được code của các framework lớn như SQLAlchemy, Pydantic, FastAPI, attrs... và biết khi nào nên hoặc không nên dùng dataclass.

---

# Khóa học Dataclass Deep Dive

## Phần I. Foundation

**Buổi 1. Dataclass là gì?**

- Vì sao dataclass ra đời
- Boilerplate trong Python
- So sánh class thường vs dataclass
- decorator hoạt động như thế nào
- Generated methods

---

**Buổi 2. Generated Methods**

Deep dive

```text-x-trilium-auto
__init__()
__repr__()
__eq__()
__hash__()
__match_args__()
```

Hiểu Python tạo chúng ra sao.

---

**Buổi 3. Type Hint**

- Optional
- Union
- Generic
- Forward reference
- Self
- Annotated

Dataclass sử dụng type hint như thế nào.

---

**Buổi 4. Field**

```text-x-trilium-auto
field()

default

default_factory

init

repr

compare

hash

metadata

kw_only
```

Đây là phần quan trọng nhất.

---

**Buổi 5. Frozen Dataclass**

```text-x-trilium-auto
@dataclass(frozen=True)
```

- Immutable object
- Functional programming
- Thread-safe object
- Cache object

---

**Buổi 6. Ordering**

```text-x-trilium-auto
order=True
```

Python tạo

```text-x-trilium-auto
<
<=
>
>=
```

khi nào nên dùng.

---

**Buổi 7. Slots**

```text-x-trilium-auto
slots=True
```

- Memory
- Speed
- **dict**
- **slots**

Benchmark.

---

**Buổi 8. Keyword Only**

```text-x-trilium-auto
kw_only=True
```

Python 3.10+

---

**Buổi 9. InitVar**

```text-x-trilium-auto
InitVar
```

- giá trị chỉ dùng khi khởi tạo
- không lưu vào object

---

**Buổi 10. post_init()**

Deep Dive

- validation
- computed field
- dependency injection
- lazy initialization

---

# Phần II. Advanced

## Buổi 11

Inheritance

```text-x-trilium-auto
Base
↓

User

↓

Admin
```

Dataclass kế thừa.

---

## Buổi 12

Multiple inheritance

MRO

field merge

---

## Buổi 13

Composition

Dataclass lồng nhau

```text-x-trilium-auto
Book

Author

Publisher

Address
```

---

## Buổi 14

Recursive Dataclass

Tree

AST

Filesystem

---

## Buổi 15

Generic Dataclass

```text-x-trilium-auto
T

Generic[T]
```

---

## Buổi 16

Abstract Dataclass

```text-x-trilium-auto
ABC

abstractmethod
```

---

## Buổi 17

Protocols

Typing

Duck Typing

---

## Buổi 18

Descriptors

property

validator

custom field

---

## Buổi 19

Metaclass + Dataclass

---

## Buổi 20

Dynamic Dataclass

```text-x-trilium-auto
make_dataclass()
```

Runtime generation.

---

# Phần III. Serialization

## Buổi 21

```text-x-trilium-auto
asdict()

astuple()
```

Deep copy

recursive

performance

---

## Buổi 22

JSON

```text-x-trilium-auto
json

orjson

msgspec
```

Serialize dataclass.

---

## Buổi 23

YAML

TOML

XML

---

## Buổi 24

Pickle

copy

deepcopy

---

# Phần IV. Performance

## Buổi 25

Benchmark

Class

Dataclass

NamedTuple

attrs

Pydantic

---

## Buổi 26

Memory layout

GC

slots

cache locality

---

## Buổi 27

Hash

Dictionary key

Set

Frozen object

---

# Phần V. Dataclass trong dự án thực tế

## Buổi 28

DTO

Data Transfer Object

---

## Buổi 29

Configuration Object

```text-x-trilium-auto
config.py
```

---

## Buổi 30

API Response

```text-x-trilium-auto
REST
GraphQL
```

---

## Buổi 31

Repository Pattern

Entity

Value Object

---

## Buổi 32

Dataclass + SQLite

Mapping Record

---

## Buổi 33

Dataclass + SQLAlchemy

Không nên dùng khi nào.

---

## Buổi 34

Dataclass + PySide6

Model

ViewModel

State

---

## Buổi 35

Dataclass + AsyncIO

Task State

Event

Queue Item

---

## Buổi 36

Dataclass + Web Scraper

Ví dụ:

```text-x-trilium-auto
Novel

Chapter

Author

Category

Image

DownloadTask

CrawlerTask

JobStatus
```

Đây sẽ áp dụng trực tiếp vào dự án crawler của bạn.

---

# Phần VI. Internals

## Buổi 37

Đọc source code thư viện dataclasses.

```text-x-trilium-auto
dataclasses.py
```

Python tạo code như thế nào.

---

## Buổi 38

Decorator implementation

Python generate

```text-x-trilium-auto
__init__
```

ra sao.

---

## Buổi 39

Viết mini dataclass của riêng mình

```text-x-trilium-auto
@my_dataclass
```

---

## Buổi 40

Viết dataclass framework mini

Hỗ trợ

- validator
- serialize
- json
- metadata
- cache

---

# Phần VII. Project

## Project 1

Student Manager

---

## Project 2

Blog Engine

---

## Project 3

REST DTO

---

## Project 4

Crawler Framework

Chính là framework crawler truyện bạn đang xây dựng.

---

## Project 5

Mini ORM

Dataclass Mapping

SQLite

---

# Sau khóa học bạn sẽ thành thạo

- ✔ Hiểu cách `@dataclass` hoạt động bên trong.
- ✔ Thiết kế các model rõ ràng, ít boilerplate.
- ✔ Áp dụng dataclass trong Repository Pattern, DTO, cấu hình, crawler và ứng dụng PySide6.
- ✔ Biết khi nào nên dùng `dataclass`, `NamedTuple`, `attrs`, `TypedDict`, `Pydantic` hoặc class thông thường.
- ✔ Tự xây dựng một phiên bản `@dataclass` đơn giản để hiểu cơ chế sinh mã và decorator.

Đây là lộ trình **từ cơ bản đến rất chuyên sâu**, phù hợp với các dự án Python thực tế như hệ thống crawler, quản lý dữ liệu SQLite và ứng dụng desktop mà bạn đang phát triển. Ở **Buổi 1**, chúng ta sẽ bắt đầu từ nền tảng: vì sao `dataclass` ra đời, cách nó giảm boilerplate và cách Python tự động sinh các phương thức như `__init__`, `__repr__` và `__eq__`.