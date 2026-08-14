# Dataclass Deep Dive — Buổi 16

# Abstract Dataclass

Hôm nay chúng ta kết hợp hai cơ chế rất quan trọng của Python:

```text
@dataclass
      +
ABC / abstractmethod
      ↓
Abstract Dataclass
```

Mục tiêu không chỉ là biết cú pháp, mà phải hiểu **khi nào nên dùng**, Python tạo class như thế nào, inheritance hoạt động ra sao và cách áp dụng vào framework crawler của bạn.

---

# 1. Abstract Class là gì?

Một abstract class là class được thiết kế làm **base class**, không phải để tạo instance trực tiếp.

Ví dụ:

```python
from abc import ABC, abstractmethod


class Animal(ABC):

    @abstractmethod
    def speak(self) -> str:
        ...
```

Ta không nên:

```python
animal = Animal()
```

Python sẽ báo:

```text
TypeError:
Can't instantiate abstract class Animal
```

Subclass phải implement:

```python
class Dog(Animal):

    def speak(self) -> str:
        return "Woof"
```

Bây giờ:

```python
dog = Dog()
```

hợp lệ.

---

# 2. Dataclass + ABC

Hai cơ chế này hoàn toàn có thể kết hợp:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Animal(ABC):
    name: str

    @abstractmethod
    def speak(self) -> str:
        ...
```

Subclass:

```python
@dataclass
class Dog(Animal):
    age: int

    def speak(self) -> str:
        return "Woof"
```

Sử dụng:

```python
dog = Dog(
    name="Bobby",
    age=3,
)
```

---

# 3. Dataclass không làm mất tính abstract

Đây là điểm quan trọng.

`@dataclass` vẫn generate:

```python
__init__()
__repr__()
__eq__()
...
```

nhưng class vẫn giữ:

```python
__abstractmethods__
```

Do đó:

```python
Animal("Bob")
```

vẫn không được phép.

Dataclass chịu trách nhiệm về:

```text
data
```

ABC chịu trách nhiệm về:

```text
contract / behavior
```

---

# 4. Hai trách nhiệm khác nhau

Ta có:

```text
@dataclass
    ↓
data structure

ABC
    ↓
behavior contract
```

Khi kết hợp:

```text
Abstract Dataclass
        │
        ├── data definition
        │
        └── behavior contract
```

Đây là một pattern rất hữu ích trong domain model.

---

# 5. Ví dụ đơn giản

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Shape(ABC):
    color: str

    @abstractmethod
    def area(self) -> float:
        ...
```

Subclass:

```python
@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height
```

Dùng:

```python
rectangle = Rectangle(
    color="red",
    width=10,
    height=5,
)

print(rectangle.area())
```

Kết quả:

```text
50
```

---

# 6. Generated `__init__()`

Một câu hỏi quan trọng:

> Abstract dataclass có generated `__init__()` không?

Có.

Ví dụ:

```python
@dataclass
class Shape(ABC):
    color: str
```

Dataclass tạo tương đương:

```python
def __init__(self, color: str):
    self.color = color
```

Nhưng:

```python
Shape("red")
```

vẫn không thể instantiate vì class abstract.

Đây là hai cơ chế độc lập:

```text
__init__()
     ≠
abstractness
```

---

# 7. Abstract method không cần implementation

Thông thường:

```python
@abstractmethod
def area(self) -> float:
    ...
```

hoặc:

```python
@abstractmethod
def area(self) -> float:
    raise NotImplementedError
```

Cả hai đều có thể.

Nhưng:

```python
...
```

thường đủ để biểu diễn contract.

---

# 8. Abstract Property

Không chỉ method.

Có thể:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Entity(ABC):
    id: int

    @property
    @abstractmethod
    def entity_type(self) -> str:
        ...
```

Subclass:

```python
@dataclass
class Novel(Entity):

    title: str

    @property
    def entity_type(self) -> str:
        return "novel"
```

---

# 9. Abstract Classmethod

Có thể yêu cầu subclass cung cấp factory:

```python
from abc import ABC, abstractmethod


@dataclass
class Entity(ABC):

    @classmethod
    @abstractmethod
    def create(cls):
        ...
```

Thứ tự decorator quan trọng:

```python
@classmethod
@abstractmethod
def create(cls):
    ...
```

Không nên tùy tiện đảo thứ tự.

---

# 10. Abstract Staticmethod

Tương tự:

```python
@dataclass
class Parser(ABC):

    @staticmethod
    @abstractmethod
    def parse(text: str):
        ...
```

Subclass:

```python
@dataclass
class NovelParser(Parser):

    @staticmethod
    def parse(text: str):
        ...
```

---

# 11. Dataclass Abstract Base Model

Một pattern phổ biến:

```python
@dataclass
class Entity(ABC):
    id: int

    @property
    @abstractmethod
    def type_name(self) -> str:
        ...
```

Sau đó:

```text
Entity
├── Novel
├── Chapter
├── Author
└── Category
```

Mỗi subclass có:

```python
type_name
```

riêng.

---

# 12. Abstract Dataclass + Inheritance

Ví dụ:

```python
@dataclass
class Entity(ABC):
    id: int
```

Subclass:

```python
@dataclass
class Novel(Entity):
    title: str
```

Generated constructor conceptually:

```python
Novel(
    id,
    title,
)
```

Dataclass merge field của base class và subclass.

---

# 13. Abstract field?

Đây là điểm dễ hiểu nhầm.

Python không có:

```python
@abstractfield
```

built-in tương tự:

```python
@abstractmethod
```

Nếu muốn bắt subclass cung cấp property:

```python
@property
@abstractmethod
def name(self) -> str:
    ...
```

thì dùng abstract property.

---

# 14. Abstract Dataclass + Property

Ví dụ:

```python
@dataclass
class Entity(ABC):
    id: int

    @property
    @abstractmethod
    def name(self) -> str:
        ...
```

Subclass:

```python
@dataclass
class Novel(Entity):
    title: str

    @property
    def name(self) -> str:
        return self.title
```

Điều này cho phép base class định nghĩa:

```text
contract
```

trong khi subclass quyết định:

```text
implementation
```

---

# 15. Abstract Dataclass + `__post_init__`

Có thể kết hợp:

```python
@dataclass
class Entity(ABC):
    id: int

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError("id must be positive")

    @abstractmethod
    def validate(self) -> None:
        ...
```

Subclass:

```python
@dataclass
class Novel(Entity):
    title: str

    def validate(self) -> None:
        if not self.title:
            raise ValueError("title is empty")
```

Khi:

```python
novel = Novel(
    id=1,
    title="Python",
)
```

`__post_init__()` của base class cũng tham gia initialization.

---

# 16. `__post_init__()` và inheritance

Giả sử:

```python
@dataclass
class Base(ABC):
    x: int

    def __post_init__(self):
        print("Base")
```

Subclass:

```python
@dataclass
class Child(Base):
    y: int

    def __post_init__(self):
        print("Child")
```

Nếu tạo:

```python
Child(1, 2)
```

thì không tự động có:

```text
Base
Child
```

mà chỉ:

```text
Child
```

Vì `Child.__post_init__()` override method của base.

Muốn gọi base:

```python
def __post_init__(self):
    super().__post_init__()
    print("Child")
```

---

# 17. Abstract Dataclass + `super()`

Đây là pattern quan trọng:

```python
@dataclass
class Entity(ABC):
    id: int

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError("Invalid id")
```

```python
@dataclass
class Novel(Entity):
    title: str

    def __post_init__(self):
        super().__post_init__()

        if not self.title:
            raise ValueError("Invalid title")
```

Ta có:

```text
Novel.__post_init__()
       │
       ▼
Entity.__post_init__()
       │
       ▼
Novel validation
```

---

# 18. Abstract Dataclass với Generic

Đây là nơi bài 16 nối trực tiếp với bài 15.

Ví dụ:

```python
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Repository(ABC, Generic[T]):

    @abstractmethod
    def get(self, id: int) -> T | None:
        ...

    @abstractmethod
    def save(self, entity: T) -> None:
        ...
```

Đây là:

```text
ABC
+
Generic[T]
```

---

# 19. Nhưng Repository có cần dataclass không?

Thông thường:

```python
class Repository(ABC, Generic[T]):
    ...
```

có thể hợp lý hơn.

Dataclass chỉ nên dùng nếu repository thực sự có **state/data fields**.

Ví dụ:

```python
@dataclass
class Repository(ABC, Generic[T]):
    connection: object

    @abstractmethod
    def get(self, id: int) -> T | None:
        ...
```

Ở đây dataclass có lý do:

```text
connection
```

là state.

---

# 20. Abstract Repository cho crawler

Ví dụ:

```python
T = TypeVar("T")


class Repository(ABC, Generic[T]):

    @abstractmethod
    def get(self, id: int) -> T | None:
        ...

    @abstractmethod
    def save(self, entity: T) -> None:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...
```

Sau đó:

```python
class NovelRepository(Repository[Novel]):

    def get(self, id: int) -> Novel | None:
        ...

    def save(self, entity: Novel) -> None:
        ...

    def delete(self, id: int) -> None:
        ...
```

Đây là abstraction rất phù hợp với architecture bạn đang xây.

---

# 21. Abstract Dataclass cho Parser

Crawler framework còn có một ứng dụng rất hay.

```python
@dataclass
class Parser(ABC, Generic[T]):
    source: str

    @abstractmethod
    def parse(self, html: str) -> T:
        ...
```

Subclass:

```python
@dataclass
class NovelParser(Parser["Novel"]):

    def parse(self, html: str) -> Novel:
        ...
```

Conceptually:

```text
Parser[T]
   │
   └── Parser[Novel]
          │
          └── parse() → Novel
```

---

# 22. Abstract Parser Hierarchy

Ta có thể xây:

```text
Parser[T]
   │
   ├── NovelParser
   │
   ├── ChapterParser
   │
   ├── AuthorParser
   │
   └── ImageParser
```

Mỗi parser có contract:

```python
parse(html) -> T
```

Nhưng `T` khác nhau.

Đây là nơi:

```text
Dataclass
+
ABC
+
Generic
```

thực sự phát huy sức mạnh.

---

# 23. Abstract Dataclass cho Crawler Plugin

Ví dụ:

```python
@dataclass
class CrawlerPlugin(ABC):

    name: str
    version: str

    @abstractmethod
    def crawl_novel(self, url: str) -> Novel:
        ...

    @abstractmethod
    def crawl_chapter(self, url: str) -> Chapter:
        ...
```

Plugin cụ thể:

```python
@dataclass
class ExamplePlugin(CrawlerPlugin):

    def crawl_novel(self, url: str) -> Novel:
        ...

    def crawl_chapter(self, url: str) -> Chapter:
        ...
```

---

# 24. Abstract Dataclass không nhất thiết chỉ có abstract methods

Một base class có thể có cả:

### Concrete field

```python
name: str
```

### Concrete method

```python
def log(self):
    ...
```

### Abstract method

```python
@abstractmethod
def crawl():
    ...
```

Ví dụ:

```python
@dataclass
class Plugin(ABC):
    name: str

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    @abstractmethod
    def run(self):
        ...
```

Subclass chỉ cần implement:

```python
def run(self):
    ...
```

---

# 25. Template Method Pattern

Đây là một pattern rất hợp với abstract dataclass.

```python
@dataclass
class Crawler(ABC):
    name: str

    def run(self):
        self.before_crawl()

        result = self.crawl()

        self.after_crawl(result)

        return result

    def before_crawl(self):
        pass

    @abstractmethod
    def crawl(self):
        ...

    def after_crawl(self, result):
        pass
```

Subclass:

```python
@dataclass
class NovelCrawler(Crawler):

    def crawl(self):
        return "novel"
```

Ta có:

```text
run()
 │
 ├── before_crawl()
 │
 ├── crawl()       ← bắt buộc subclass
 │
 └── after_crawl()
```

Đây là **Template Method Pattern**.

---

# 26. Đây là cách framework thường được thiết kế

Framework không muốn subclass tự quyết định toàn bộ flow.

Framework định nghĩa:

```text
lifecycle
```

Subclass chỉ implement extension points.

Ví dụ:

```text
Framework
    │
    ├── initialize()
    ├── validate()
    ├── execute()       ← abstract
    ├── finalize()
    └── error handling
```

Dataclass cung cấp:

```text
state
```

ABC cung cấp:

```text
contract
```

---

# 27. Abstract Dataclass + `slots`

Có thể:

```python
@dataclass(slots=True)
class Entity(ABC):
    id: int

    @abstractmethod
    def validate(self) -> None:
        ...
```

Subclass:

```python
@dataclass(slots=True)
class Novel(Entity):
    title: str

    def validate(self) -> None:
        ...
```

Cả hai đều có thể sử dụng slots.

---

# 28. Abstract Dataclass + Frozen

Cũng có thể:

```python
@dataclass(frozen=True)
class ValueObject(ABC):

    @abstractmethod
    def validate(self):
        ...
```

Ví dụ:

```python
@dataclass(frozen=True)
class ISBN(ValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise ValueError
```

Đây là pattern rất phù hợp cho **DDD Value Object**.

---

# 29. Abstract Dataclass + `order`

Có thể:

```python
@dataclass(order=True)
class Version(ABC):
    major: int
    minor: int

    @abstractmethod
    def is_compatible(self) -> bool:
        ...
```

Nhưng cần cân nhắc semantic.

Generated ordering dựa trên field:

```text
major
minor
```

không phải abstract method.

Do đó:

> `order=True` chỉ nên dùng nếu field ordering thực sự phản ánh domain ordering.

---

# 30. Abstract Dataclass + `eq`

Tương tự:

```python
@dataclass
class Entity(ABC):
    id: int
```

Generated:

```python
__eq__()
```

sẽ dựa trên dataclass fields.

Nhưng trong DDD, đôi khi Entity equality lại dựa trên:

```text
identity
```

thay vì toàn bộ state.

Đây là lý do không nên bật `eq=True` một cách máy móc.

---

# 31. Entity equality là vấn đề thiết kế

Ví dụ:

```python
@dataclass
class Novel(Entity):
    title: str
```

Hai object:

```python
Novel(1, "A")
Novel(1, "B")
```

Dataclass có thể coi:

```text
different
```

nhưng DDD có thể coi:

```text
same Entity
```

vì:

```text
id = 1
```

Do đó Abstract Dataclass thường cần được thiết kế cẩn thận về:

```text
eq
hash
identity
```

---

# 32. `ABC` vs `Protocol`

Đây là phần rất quan trọng trước Buổi 17.

### ABC

Dùng:

```python
class Repository(ABC):
```

để tạo:

```text
nominal contract
```

Class phải nằm trong inheritance hierarchy.

### Protocol

Dùng:

```python
class Repository(Protocol):
```

để tạo:

```text
structural contract
```

Không cần kế thừa trực tiếp.

---

# 33. ABC

```python
class Serializer(ABC):

    @abstractmethod
    def serialize(self, value):
        ...
```

Class:

```python
class JsonSerializer(Serializer):
    ...
```

phải kế thừa.

---

# 34. Protocol

```python
class Serializer(Protocol):

    def serialize(self, value) -> bytes:
        ...
```

Class:

```python
class JsonSerializer:

    def serialize(self, value) -> bytes:
        ...
```

không cần:

```python
Serializer
```

nhưng vẫn có thể thỏa contract về typing.

Buổi 17 chúng ta sẽ đào rất sâu phần này.

---

# 35. Abstract Dataclass với `__init_subclass__`

Có thể kết hợp:

```python
@dataclass
class Plugin(ABC):
    name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        print(f"Registered: {cls.__name__}")

    @abstractmethod
    def run(self):
        ...
```

Mỗi subclass được tạo sẽ đi qua:

```python
__init_subclass__()
```

Đây là bước đầu tiến đến:

```text
metaprogramming
```

và sau này:

> **Buổi 19 — Metaclass + Dataclass**

---

# 36. Một Abstract Dataclass hoàn chỉnh

Hãy thiết kế:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BaseModel(ABC):

    id: int

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError("id must be positive")

    @property
    @abstractmethod
    def type_name(self) -> str:
        ...

    @abstractmethod
    def validate(self) -> None:
        ...

    def describe(self) -> str:
        return f"{self.type_name}:{self.id}"
```

Subclass:

```python
@dataclass
class Novel(BaseModel):

    title: str

    @property
    def type_name(self) -> str:
        return "novel"

    def validate(self) -> None:
        if not self.title:
            raise ValueError("title is required")
```

---

# 37. Flow khi tạo `Novel`

```python
novel = Novel(
    id=1,
    title="Python"
)
```

Flow:

```text
Novel(...)
   │
   ▼
generated __init__()
   │
   ▼
assign fields
   │
   ▼
__post_init__()
   │
   ▼
BaseModel.__post_init__()
   │
   ▼
object ready
```

Abstract methods không chạy trong initialization.

Chúng chỉ đảm bảo:

```text
Novel phải implement contract
```

---

# 38. Một lỗi rất phổ biến

Viết:

```python
@dataclass
class Base(ABC):
    x: int

    @abstractmethod
    def validate(self):
        ...
```

sau đó:

```python
@dataclass
class Child(Base):
    y: int
```

và quên:

```python
validate()
```

Kết quả:

```python
Child(1, 2)
```

sẽ lỗi:

```text
TypeError:
Can't instantiate abstract class Child
```

---

# 39. Cách debug abstract class

Python cung cấp:

```python
Child.__abstractmethods__
```

Ví dụ:

```python
print(Child.__abstractmethods__)
```

có thể nhận:

```python
{'validate'}
```

Nếu:

```python
print(Child.__abstractmethods__)
```

ra:

```python
frozenset()
```

thì class không còn abstract methods chưa implement.

Đây là một kỹ thuật debug rất hữu ích.

---

# 40. `ABC` hoạt động như thế nào?

Khi class kế thừa:

```python
ABC
```

Python sử dụng:

```python
ABCMeta
```

làm metaclass.

`ABCMeta` theo dõi:

```python
__isabstractmethod__
```

và xây dựng:

```python
__abstractmethods__
```

Nếu set này không rỗng:

```text
class abstract
```

Nếu rỗng:

```text
class concrete
```

Đây là một phần quan trọng của Python internals.

---

# 41. Dataclass không phải metaclass

Khi viết:

```python
@dataclass
class Model(ABC):
    ...
```

có hai cơ chế:

```text
class creation
      │
      ▼
ABCMeta
      │
      ▼
class object
      │
      ▼
@dataclass
      │
      ▼
modify class
      │
      ├── __init__
      ├── __repr__
      ├── __eq__
      └── ...
```

Điểm này rất đáng nhớ.

`@dataclass` là decorator.

`ABCMeta` là metaclass.

Hai thứ khác nhau.

---

# 42. Thứ tự decorator

Ví dụ:

```python
@dataclass
class Model(ABC):
    ...
```

Python conceptually làm:

```python
class Model(ABC):
    ...

Model = dataclass(Model)
```

Do đó `dataclass` nhận class đã được tạo bởi metaclass của `ABC`.

Đây là lý do hai cơ chế có thể phối hợp.

---

# 43. Abstract Dataclass cho Domain Model

Trong DDD:

```text
Entity
├── Novel
├── Chapter
├── Author
└── Category
```

Có thể:

```python
@dataclass
class Entity(ABC):
    id: int

    @abstractmethod
    def validate(self) -> None:
        ...
```

Sau đó:

```python
@dataclass
class Novel(Entity):
    title: str
    chapters: list["Chapter"]
```

```python
@dataclass
class Chapter(Entity):
    title: str
    content: str
```

Mỗi entity có:

```text
shared state
+
shared contract
```

---

# 44. Abstract Dataclass cho Parser Framework

Một thiết kế tốt:

```python
T = TypeVar("T")


@dataclass
class Parser(ABC, Generic[T]):
    source_name: str

    @abstractmethod
    def parse(self, html: str) -> T:
        ...
```

Novel parser:

```python
@dataclass
class NovelParser(Parser[Novel]):

    def parse(self, html: str) -> Novel:
        ...
```

Chapter parser:

```python
@dataclass
class ChapterParser(Parser[Chapter]):

    def parse(self, html: str) -> Chapter:
        ...
```

Đây là một pattern rất đáng ghi nhớ:

```text
Abstract Generic Base
          │
          ▼
Parser[T]
          │
   ┌──────┴──────┐
   ▼             ▼
NovelParser   ChapterParser
Parser[Novel]  Parser[Chapter]
```

---

# 45. Khi nào nên dùng Abstract Dataclass?

Nên dùng khi object có:

### 1. State

Ví dụ:

```python
name
id
config
connection
```

### 2. Common implementation

Ví dụ:

```python
log()
validate_id()
describe()
```

### 3. Required behavior

Ví dụ:

```python
parse()
execute()
validate()
serialize()
```

### 4. Inheritance hierarchy thực sự có ý nghĩa

Ví dụ:

```text
Parser
 ├── NovelParser
 └── ChapterParser
```

---

# 46. Khi nào KHÔNG nên dùng?

Không nên tạo:

```text
ABC
   ↓
Subclass
   ↓
Subclass
   ↓
Subclass
```

chỉ để "tổ chức code".

Nếu chỉ cần:

```text
interface
```

hãy cân nhắc:

```python
Protocol
```

Nếu chỉ cần:

```text
data
```

dùng:

```python
@dataclass
```

Nếu chỉ cần:

```text
behavior
```

có thể dùng class thông thường.

---

# 47. Một nguyên tắc thiết kế quan trọng

Đừng biến mọi dataclass thành:

```python
@dataclass
class Base(ABC):
    ...
```

Chỉ dùng abstract base class khi có:

> **invariant hoặc contract thực sự cần được các subclass tuân thủ.**

Nếu không:

```text
ABC
```

chỉ làm architecture phức tạp hơn.

---

# 48. Bài tập Buổi 16

### Bài 1 — Basic

Tạo:

```python
@dataclass
class Shape(ABC):
    color: str

    @abstractmethod
    def area(self) -> float:
        ...
```

Tạo:

```text
Circle
Rectangle
Triangle
```

---

### Bài 2 — Validation

Tạo:

```python
@dataclass
class Entity(ABC):
    id: int
```

Yêu cầu:

```text
id > 0
```

Subclass:

```text
Novel
Chapter
Author
```

mỗi class phải implement:

```python
validate()
```

---

### Bài 3 — Generic Abstract Dataclass

Tạo:

```python
@dataclass
class Parser(ABC, Generic[T]):
    source: str

    @abstractmethod
    def parse(self, data: str) -> T:
        ...
```

Sau đó:

```text
NovelParser
ChapterParser
ImageParser
```

---

### Bài 4 — Crawler Framework

Thiết kế:

```text
Crawler[T]
```

với lifecycle:

```text
run()
 │
 ├── before()
 ├── crawl()       ← abstract
 ├── validate()
 └── after()
```

Sau đó tạo:

```text
NovelCrawler
ChapterCrawler
```

---

### Bài 5 — Deep Dive

Kiểm tra:

```python
Base.__abstractmethods__
Child.__abstractmethods__
```

và tìm hiểu:

```python
ABCMeta
__isabstractmethod__
__abstractmethods__
```

---

# 49. Tổng kết Buổi 16

Mental model quan trọng nhất:

```text
                 Dataclass
                    │
                 STATE
                    │
                    ▼
             ┌─────────────┐
             │             │
             │  Abstract   │
             │  Dataclass  │
             │             │
             └─────────────┘
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
          fields        behavior
             │             │
             ▼             ▼
       @dataclass         ABC
                         │
                         ▼
                  abstractmethod
```

Và khi kết hợp với Generic:

```text
Abstract Dataclass
        +
     Generic[T]
        ↓
Abstract Generic Data Model
```

Ví dụ quan trọng nhất của hôm nay:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Parser(ABC, Generic[T]):
    source: str

    @abstractmethod
    def parse(self, html: str) -> T:
        ...
```

Đây chính là nền móng để sau này chúng ta có thể xây:

```text
Parser[T]
Repository[T]
Serializer[T]
Handler[T]
Task[T]
Event[T]
```

một cách có **contract + typing + reusable architecture**.

---

## Roadmap

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ✅
16. Abstract Dataclass           ✅
17. Protocols                    ← tiếp theo
18. Descriptors
19. Metaclass + Dataclass
20. Dynamic Dataclass
```

**Buổi 17** sẽ đi sâu vào **Dataclass + `Protocol` + Structural Typing + Duck Typing**, đặc biệt là sự khác biệt sâu sắc giữa `ABC` và `Protocol`, và tại sao khi xây framework Python hiện đại, `Protocol` nhiều lúc tốt hơn inheritance.
