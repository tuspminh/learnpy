# Dataclass Deep Dive — Buổi 13

# Composition — Dataclass lồng nhau

Hôm nay chúng ta chuyển từ **Inheritance** sang một tư duy quan trọng hơn trong thiết kế domain:

> **Composition — một object chứa các object khác.**

Đặc biệt với project crawler của bạn, Composition sẽ xuất hiện rất nhiều:

```text
Novel
├── Author
├── Publisher
├── Category
├── Image
└── chapters
    ├── Chapter
    ├── Chapter
    └── Chapter
```

Đây thường là mô hình tự nhiên hơn việc cố dùng inheritance.

---

# 1. Composition là gì?

Composition nghĩa là một object **có chứa object khác**.

Ví dụ:

```python
@dataclass
class Author:
    name: str
```

```python
@dataclass
class Novel:
    title: str
    author: Author
```

Ở đây:

```text
Novel
  │
  └── Author
```

Quan hệ là:

> `Novel HAS-A Author`

không phải:

> `Novel IS-A Author`

---

# 2. Inheritance vs Composition

Inheritance:

```python
@dataclass
class Animal:
    name: str


@dataclass
class Dog(Animal):
    breed: str
```

Quan hệ:

```text
Dog IS-A Animal
```

Composition:

```python
@dataclass
class Engine:
    horsepower: int


@dataclass
class Car:
    engine: Engine
```

Quan hệ:

```text
Car HAS-A Engine
```

---

# 3. Tại sao Composition đặc biệt quan trọng với Dataclass?

Dataclass rất phù hợp để biểu diễn **data structure dạng cây/object graph**.

Ví dụ:

```text
Novel
│
├── Author
│   └── Address
│
├── Publisher
│   └── Address
│
├── categories[]
│
└── chapters[]
```

Mỗi thành phần có trách nhiệm riêng.

---

# 4. Dataclass lồng nhau

Ví dụ đơn giản:

```python
from dataclasses import dataclass


@dataclass
class Address:
    city: str
    country: str


@dataclass
class Author:
    name: str
    address: Address


@dataclass
class Novel:
    title: str
    author: Author
```

Tạo object:

```python
address = Address(
    city="Ho Chi Minh",
    country="Vietnam"
)

author = Author(
    name="Nguyen Van A",
    address=address
)

novel = Novel(
    title="Python Deep Dive",
    author=author
)
```

Object graph:

```text
Novel
│
├── title
│
└── author
     │
     ├── name
     │
     └── address
           ├── city
           └── country
```

---

# 5. Truy cập nested object

```python
print(novel.title)
```

```text
Python Deep Dive
```

Author:

```python
print(novel.author.name)
```

Address:

```python
print(
    novel.author.address.city
)
```

Đây là:

```text
novel
  ↓
author
  ↓
address
  ↓
city
```

---

# 6. Composition không phải inheritance

Không nên:

```python
@dataclass
class Author:
    name: str


@dataclass
class Novel(Author):
    title: str
```

Điều này nói:

```text
Novel IS-A Author
```

rất vô lý.

Nên:

```python
@dataclass
class Novel:
    title: str
    author: Author
```

---

# 7. Composition với List

Đây là pattern cực kỳ phổ biến.

```python
@dataclass
class Chapter:
    number: int
    title: str


@dataclass
class Novel:
    title: str
    chapters: list[Chapter]
```

Tạo:

```python
chapters = [
    Chapter(1, "Beginning"),
    Chapter(2, "Journey"),
    Chapter(3, "Return"),
]

novel = Novel(
    title="My Novel",
    chapters=chapters
)
```

Object graph:

```text
Novel
│
└── chapters
     ├── Chapter 1
     ├── Chapter 2
     └── Chapter 3
```

---

# 8. `default_factory` cho nested list

Không nên:

```python
@dataclass
class Novel:
    title: str
    chapters: list[Chapter] = []
```

Đây là mutable default nguy hiểm.

Phải dùng:

```python
from dataclasses import field


@dataclass
class Novel:
    title: str
    chapters: list[Chapter] = field(
        default_factory=list
    )
```

Bây giờ:

```python
a = Novel("A")
b = Novel("B")

a.chapters.append(
    Chapter(1, "Chapter 1")
)
```

`b` vẫn:

```python
[]
```

---

# 9. Composition với Dictionary

Ví dụ metadata:

```python
@dataclass
class Novel:
    title: str
    metadata: dict[str, str]
```

Nhưng nếu metadata có cấu trúc rõ ràng, tốt hơn nên tạo dataclass:

```python
@dataclass
class NovelMetadata:
    language: str
    status: str
    source: str
```

Sau đó:

```python
@dataclass
class Novel:
    title: str
    metadata: NovelMetadata
```

Thay vì:

```python
novel.metadata["language"]
```

ta có:

```python
novel.metadata.language
```

---

# 10. Tại sao nested dataclass tốt hơn dict?

Dict:

```python
metadata = {
    "language": "vi",
    "status": "completed",
    "source": "abc"
}
```

Không có cấu trúc type rõ ràng.

Có thể viết sai:

```python
metadata["langauge"]
```

Dataclass:

```python
@dataclass
class NovelMetadata:
    language: str
    status: str
    source: str
```

IDE/type checker có thể hiểu:

```python
metadata.language
metadata.status
metadata.source
```

---

# 11. Composition tạo domain model rõ ràng

Ví dụ crawler:

```python
@dataclass
class Author:
    id: int
    name: str
```

```python
@dataclass
class Category:
    id: int
    name: str
```

```python
@dataclass
class Chapter:
    id: int
    number: int
    title: str
    url: str
```

```python
@dataclass
class Novel:
    id: int
    title: str
    author: Author
    categories: list[Category]
    chapters: list[Chapter]
```

Ta có domain model:

```text
Novel
├── Author
├── Category[]
└── Chapter[]
```

Đây là cách rất tự nhiên.

---

# 12. Composition nhiều tầng

Ví dụ:

```python
@dataclass
class Address:
    city: str
```

```python
@dataclass
class Publisher:
    name: str
    address: Address
```

```python
@dataclass
class Author:
    name: str
    address: Address
```

```python
@dataclass
class Novel:
    title: str
    author: Author
    publisher: Publisher
```

Object graph:

```text
Novel
│
├── Author
│   └── Address
│
└── Publisher
    └── Address
```

---

# 13. Shared Object

Composition không nhất thiết có nghĩa:

> mỗi parent sở hữu một object riêng.

Hai object có thể reference cùng một object.

```python
address = Address(
    city="HCM"
)
```

Sau đó:

```python
author = Author(
    name="A",
    address=address
)

publisher = Publisher(
    name="Publisher",
    address=address
)
```

Ta có:

```text
        Address
        /     \
       /       \
   Author    Publisher
```

Cả hai cùng reference một object.

---

# 14. Identity rất quan trọng

Kiểm tra:

```python
author.address is publisher.address
```

Kết quả:

```text
True
```

Đây là điểm cần hiểu rõ.

Dataclass không tự động clone nested object.

Nó chỉ giữ reference:

```text
Novel
  ↓
Author
  ↓
Address
```

---

# 15. Mutable Composition

Ví dụ:

```python
@dataclass
class Address:
    city: str


@dataclass
class Author:
    name: str
    address: Address
```

Nếu:

```python
address = Address("HCM")
author = Author("A", address)
```

thì:

```python
address.city = "Hanoi"
```

sẽ làm:

```python
author.address.city
```

thành:

```text
Hanoi
```

vì cả hai cùng reference object.

---

# 16. Frozen Composition

Ta có:

```python
@dataclass(frozen=True)
class Address:
    city: str
```

và:

```python
@dataclass(frozen=True)
class Author:
    name: str
    address: Address
```

Bây giờ:

```python
author.name = "B"
```

không được.

Nhưng điều quan trọng là:

> Frozen chỉ đóng băng object đó, không tự động biến toàn bộ object graph thành immutable.

Nếu nested object mutable:

```python
@dataclass(frozen=True)
class Author:
    address: Address
```

nhưng:

```python
Address
```

không frozen, thì nested state vẫn có thể thay đổi.

---

# 17. Immutable graph

Nếu muốn object graph thực sự immutable:

```python
@dataclass(frozen=True)
class Address:
    city: str
```

```python
@dataclass(frozen=True)
class Author:
    name: str
    address: Address
```

```python
@dataclass(frozen=True)
class Novel:
    title: str
    author: Author
```

Tư duy:

```text
Novel frozen
   ↓
Author frozen
   ↓
Address frozen
```

Toàn bộ graph được thiết kế immutable.

---

# 18. Nhưng `list` vẫn là vấn đề

Ví dụ:

```python
@dataclass(frozen=True)
class Novel:
    chapters: list[Chapter]
```

Bạn không thể:

```python
novel.chapters = []
```

nhưng vẫn có thể:

```python
novel.chapters.append(
    Chapter(...)
)
```

Vì:

```text
frozen
```

chỉ ngăn:

```text
attribute reassignment
```

không ngăn mutation của object bên trong.

---

# 19. Dùng tuple cho immutable composition

Nếu muốn chapters immutable:

```python
@dataclass(frozen=True)
class Novel:
    chapters: tuple[Chapter, ...]
```

Ví dụ:

```python
novel = Novel(
    chapters=(
        Chapter(1, "A"),
        Chapter(2, "B"),
    )
)
```

Không thể:

```python
novel.chapters.append(...)
```

vì tuple immutable.

---

# 20. Composition + Validation

Nested validation có thể chia trách nhiệm.

```python
@dataclass
class Author:

    name: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError(
                "Author name is required"
            )
```

Novel:

```python
@dataclass
class Novel:

    title: str
    author: Author

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError(
                "Novel title is required"
            )
```

Khi tạo:

```python
Novel(
    "",
    Author("Alice")
)
```

Novel validation fail.

---

# 21. Validation không nên gom tất cả vào parent

Không nên có:

```python
Novel.__post_init__()
```

kiểm tra:

```text
author.name
publisher.name
chapter.title
category.name
image.url
```

Điều này làm `Novel` biết quá nhiều.

Tốt hơn:

```text
Author
 └── validate Author

Chapter
 └── validate Chapter

Publisher
 └── validate Publisher

Novel
 └── validate Novel invariants
```

Đây là:

> **Separation of Responsibility**

---

# 22. Computed Property trong Composition

Ví dụ:

```python
@dataclass
class Novel:

    title: str
    chapters: list[Chapter]

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)
```

Sử dụng:

```python
novel.chapter_count
```

Không cần lưu:

```python
chapter_count
```

vào object.

---

# 23. Nested computed property

```python
@dataclass
class Novel:

    title: str
    author: Author

    @property
    def author_name(self) -> str:
        return self.author.name
```

Nhưng cần cân nhắc:

```text
novel.author.name
```

đã đủ rõ ràng chưa?

Nếu có, không nhất thiết tạo:

```text
novel.author_name
```

Đừng tạo computed property chỉ để rút ngắn một expression.

---

# 24. Composition và `Optional`

Một relationship có thể không tồn tại:

```python
@dataclass
class Novel:
    title: str
    publisher: Publisher | None = None
```

Python 3.10+:

```python
Publisher | None
```

thay cho:

```python
Optional[Publisher]
```

Ví dụ:

```python
novel = Novel(
    title="A",
    publisher=None
)
```

---

# 25. Optional nested object

Khi truy cập:

```python
novel.publisher.name
```

có thể lỗi:

```text
AttributeError
```

vì:

```python
publisher is None
```

Cần thiết kế API rõ ràng.

Ví dụ:

```python
@property
def publisher_name(self) -> str | None:
    if self.publisher is None:
        return None

    return self.publisher.name
```

---

# 26. Composition và Forward Reference

Recursive structure:

```python
@dataclass
class Category:
    name: str
    parent: "Category | None" = None
```

Hoặc Python hiện đại:

```python
from __future__ import annotations


@dataclass
class Category:
    name: str
    parent: Category | None = None
```

Đây là bước chuẩn bị cho:

> **Buổi 14 — Recursive Dataclass**

---

# 27. Composition và Generic

Ta có thể có:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Response(Generic[T]):
    data: T
```

Sau đó:

```python
@dataclass
class Novel:
    title: str
```

và:

```python
response = Response[Novel](
    data=Novel("Python")
)
```

Object graph:

```text
Response[Novel]
      │
      └── Novel
```

Generic Dataclass sẽ học sâu ở **Buổi 15**.

---

# 28. Dataclass lồng nhau và `repr`

Một ưu điểm rất tiện:

```python
@dataclass
class Address:
    city: str


@dataclass
class Author:
    name: str
    address: Address


@dataclass
class Novel:
    title: str
    author: Author
```

Khi:

```python
print(novel)
```

Python tự tạo representation nested:

```text
Novel(
    title='...',
    author=Author(
        name='...',
        address=Address(city='...')
    )
)
```

Điều này cực kỳ hữu ích khi debug domain model.

---

# 29. Nested Dataclass và equality

Dataclass `__eq__()` cũng hoạt động recursively theo object equality.

```python
a1 = Author(
    "Alice",
    Address("HCM")
)

a2 = Author(
    "Alice",
    Address("HCM")
)
```

Nếu:

```python
a1 == a2
```

thì thường:

```text
True
```

vì:

```text
a1.name == a2.name
+
a1.address == a2.address
```

và `Address` cũng là dataclass.

---

# 30. Equality của Composition

Ví dụ:

```python
@dataclass
class Engine:
    horsepower: int


@dataclass
class Car:
    model: str
    engine: Engine
```

Hai object:

```python
Car(
    "BMW",
    Engine(300)
)
```

và:

```python
Car(
    "BMW",
    Engine(300)
)
```

được xem là equal theo giá trị field.

Không cần:

```python
engine1 is engine2
```

Phải phân biệt:

```text
identity
```

với:

```text
equality
```

---

# 31. Composition + `asdict()`

Đây là phần liên quan trực tiếp tới Buổi 21.

Ví dụ:

```python
from dataclasses import asdict


data = asdict(novel)
```

Dataclass nested được chuyển recursively thành dictionary.

Ví dụ conceptually:

```python
{
    "title": "Novel",
    "author": {
        "name": "Alice",
        "address": {
            "city": "HCM"
        }
    }
}
```

Nhưng `asdict()` có những behavior về recursive conversion và copying mà chúng ta sẽ phân tích kỹ ở **Buổi 21**.

---

# 32. Composition + Serialization

Đây là lý do composition rất hữu ích cho API DTO.

Ví dụ:

```python
@dataclass
class AuthorDTO:
    id: int
    name: str
```

```python
@dataclass
class ChapterDTO:
    id: int
    title: str
```

```python
@dataclass
class NovelDTO:
    id: int
    title: str
    author: AuthorDTO
    chapters: list[ChapterDTO]
```

API response có thể map trực tiếp thành:

```text
NovelDTO
├── AuthorDTO
└── ChapterDTO[]
```

Đây sẽ liên quan trực tiếp tới **Buổi 30 — API Response**.

---

# 33. Composition trong crawler

Bây giờ áp dụng vào framework crawler.

Ta có:

```python
@dataclass
class Author:
    name: str
    url: str | None = None
```

```python
@dataclass
class Category:
    name: str
    url: str | None = None
```

```python
@dataclass
class Image:
    url: str
    alt: str | None = None
```

```python
@dataclass
class Chapter:
    number: int
    title: str
    url: str
```

Và:

```python
@dataclass
class Novel:
    title: str
    author: Author
    categories: list[Category]
    chapters: list[Chapter]
    images: list[Image]
```

Đây là một domain model rất tự nhiên.

---

# 34. Nhưng cần phân biệt Domain Model và Database Model

Đây là một điểm cực kỳ quan trọng đối với dự án crawler của bạn.

Domain:

```text
Novel
├── Author
├── Category[]
└── Chapter[]
```

Database có thể là:

```text
novels
authors
categories
chapters
novel_categories
```

Không nhất thiết:

```text
1 Novel
=
1 database row
```

Domain object và database record là hai abstraction khác nhau.

Đây chính là nền tảng cho:

> **Buổi 31 — Repository Pattern**

và:

> **Buổi 32 — Dataclass + SQLite**

---

# 35. Composition và Repository

Repository có thể trả về:

```python
Novel
```

thay vì:

```python
sqlite3.Row
```

Ví dụ:

```text
SQLite
   │
   ▼
Repository
   │
   ▼
Novel
├── Author
├── Category[]
└── Chapter[]
```

Repository chịu trách nhiệm mapping:

```text
database records
       ↓
domain objects
```

Đây là architecture rất phù hợp với crawler framework.

---

# 36. Một lỗi thiết kế phổ biến

Không nên tạo một dataclass khổng lồ:

```python
@dataclass
class Novel:
    id: int
    title: str
    author_id: int
    author_name: str
    author_url: str
    category_1: str
    category_2: str
    category_3: str
    chapter_1: str
    chapter_2: str
    ...
```

Đây là kiểu:

> **Flat data structure**

khó mở rộng và khó biểu diễn domain.

Composition tốt hơn:

```python
@dataclass
class Novel:
    id: int
    title: str
    author: Author
    categories: list[Category]
    chapters: list[Chapter]
```

---

# 37. Composition tạo Boundary rõ ràng

Ví dụ:

```text
Novel
│
├── Author
│
├── Publisher
│
├── Categories
│
└── Chapters
```

Mỗi dataclass có thể có:

* validation
* computed property
* behavior nhỏ
* serialization logic phù hợp
* equality semantics

Nhờ đó domain không biến thành một class khổng lồ.

---

# 38. Composition và Aggregate

Trong Domain-Driven Design, một object có thể là **Aggregate Root**.

Ví dụ:

```text
Novel
├── Chapter
├── Chapter
└── Chapter
```

Có thể thiết kế:

```python
@dataclass
class Novel:
    chapters: list[Chapter]
```

và:

```python
def add_chapter(
    self,
    chapter: Chapter
):
    self.chapters.append(chapter)
```

Khi đó `Novel` kiểm soát cách Chapter được thêm vào.

Đây là bước giao nhau giữa:

```text
Dataclass
+
DDD
+
Repository
```

rất phù hợp với hướng học của bạn.

---

# 39. Đừng biến dataclass thành "bag of data"

Composition không có nghĩa:

```python
novel.chapters.append(...)
```

ở mọi nơi trong application.

Có thể encapsulate:

```python
@dataclass
class Novel:

    title: str
    chapters: list[Chapter] = field(
        default_factory=list
    )

    def add_chapter(
        self,
        chapter: Chapter
    ) -> None:

        self.chapters.append(chapter)
```

Sau đó:

```python
novel.add_chapter(chapter)
```

Thay vì:

```python
novel.chapters.append(chapter)
```

nếu domain có invariant cần bảo vệ.

---

# 40. Composition + Invariant

Ví dụ chapter number không được trùng:

```python
@dataclass
class Novel:

    title: str

    chapters: list[Chapter] = field(
        default_factory=list
    )

    def add_chapter(
        self,
        chapter: Chapter
    ) -> None:

        if any(
            c.number == chapter.number
            for c in self.chapters
        ):
            raise ValueError(
                "Chapter already exists"
            )

        self.chapters.append(chapter)
```

Bây giờ `Novel` bảo vệ invariant:

```text
chapter.number must be unique
```

Đây là cách Composition trở thành **domain behavior**, không chỉ là nested data.

---

# 41. Composition với immutable child

Có một pattern rất tốt:

```python
@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
```

Novel có thể mutable:

```python
@dataclass
class Novel:
    title: str
    chapters: list[Chapter]
```

Khi đó:

```text
Novel
   mutable aggregate
       │
       ├── Chapter immutable
       ├── Chapter immutable
       └── Chapter immutable
```

Đây là một thiết kế rất đáng cân nhắc cho crawler.

---

# 42. Composition vs Multiple Inheritance

Đây là câu hỏi quan trọng nhất của buổi hôm nay.

### Nếu:

```text
A IS-A B
```

có thể dùng inheritance.

### Nếu:

```text
A HAS-A B
```

thường dùng composition.

### Nếu:

```text
A HAS capability X
A HAS capability Y
```

có thể xem xét mixin/multiple inheritance.

Ví dụ:

```text
Novel
 ├── HAS Author
 ├── HAS Chapter[]
 └── HAS Category[]
```

→ Composition.

Trong khi:

```text
Novel
 ├── Identifiable
 └── Timestamped
```

→ Mixin có thể phù hợp.

---

# 43. Bài tập 1 — Basic Composition

Tạo:

```python
@dataclass
class Address:
    city: str
    country: str
```

```python
@dataclass
class Author:
    name: str
    address: Address
```

```python
@dataclass
class Book:
    title: str
    author: Author
```

Sau đó:

```python
book.author.address.city
```

phải trả về thành phố.

---

# 44. Bài tập 2 — Nested List

Tạo:

```python
@dataclass
class Chapter:
    number: int
    title: str
```

và:

```python
@dataclass
class Novel:
    title: str
    chapters: list[Chapter] = field(
        default_factory=list
    )
```

Viết:

```python
add_chapter()
```

và đảm bảo:

```text
number không được trùng
```

---

# 45. Bài tập 3 — Immutable Domain

Thiết kế:

```text
Novel
├── Author
├── Chapter[]
└── Category[]
```

Trong đó:

```text
Author    → frozen
Chapter   → frozen
Category  → frozen
Novel     → frozen
```

và sử dụng:

```python
tuple
```

thay cho:

```python
list
```

để giữ object graph immutable.

---

# 46. Bài tập 4 — Crawler Domain

Thiết kế:

```text
Novel
├── id
├── title
├── author
├── categories
├── chapters
└── images
```

Các class:

```text
Author
Category
Chapter
Image
Novel
```

Mỗi class phải có:

* type hint
* validation
* `__repr__`
* computed property nếu cần

Không được dùng inheritance giữa:

```text
Novel
Author
Chapter
Category
Image
```

Hãy dùng Composition.

---

# 47. Bài tập 5 — Domain + Database

Giả sử SQLite trả về:

```text
novels
authors
chapters
```

Hãy thiết kế:

```text
NovelRepository
```

có method:

```python
get_by_id(
    novel_id: int
) -> Novel
```

Kết quả phải là:

```text
Novel
├── Author
└── Chapter[]
```

chứ không phải:

```python
sqlite3.Row
```

Bài này sẽ chuẩn bị trực tiếp cho:

> **Buổi 31 — Repository Pattern**

---

# 48. Tổng kết Buổi 13

Tư duy quan trọng nhất hôm nay:

```text
Inheritance
    ↓
IS-A

Composition
    ↓
HAS-A
```

Dataclass rất mạnh khi dùng để xây object graph:

```text
Novel
├── Author
│   └── Address
│
├── Publisher
│   └── Address
│
├── Category[]
│
├── Chapter[]
│
└── Image[]
```

Các nguyên tắc quan trọng:

1. **Không dùng inheritance cho quan hệ HAS-A.**
2. Nested dataclass là composition tự nhiên.
3. Dùng `default_factory` cho collection mutable.
4. Frozen parent không làm nested object tự động immutable.
5. `tuple` phù hợp khi muốn collection immutable.
6. Mỗi dataclass nên chịu trách nhiệm cho invariant của chính nó.
7. Domain model không nhất thiết giống database schema.
8. Composition rất phù hợp để xây Domain Model và Aggregate.
9. Repository có thể map database records → nested dataclass graph.
10. Với crawler, `Novel → Author/Chapter/Category/Image` nên là composition.

---

## Roadmap hiện tại

```text
Phần II — Advanced

11. Inheritance                 ✅
12. Multiple Inheritance + MRO  ✅
13. Composition                 ✅ ← hôm nay
14. Recursive Dataclass         ← tiếp theo
15. Generic Dataclass
16. Abstract Dataclass
17. Protocols
18. Descriptors
19. Metaclass + Dataclass
20. Dynamic Dataclass
```

### Buổi 14 — Recursive Dataclass

Chúng ta sẽ đi sâu vào:

```text
Tree
│
├── Node
│   ├── Node
│   │   ├── Node
│   │   └── Node
│   │
│   └── Node
│
└── Node
```

và áp dụng vào **AST, filesystem, category tree, chapter tree**, bao gồm:

* Forward reference
* `from __future__ import annotations`
* self-reference
* `list[Node]`
* parent ↔ child
* circular reference
* recursive validation
* recursive serialization
* tree traversal
* immutable recursive dataclass
* tránh infinite recursion trong `repr()`
* memory/reference graph
* xây **Category Tree cho crawler**.
