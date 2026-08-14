# Dataclass Deep Dive — Buổi 15

# Generic Dataclass

Hôm nay chúng ta đi vào một chủ đề rất quan trọng khi xây **framework/library có typing mạnh**:

> **Kết hợp `dataclass` với Generic để tạo ra các data structure có thể tái sử dụng cho nhiều kiểu dữ liệu khác nhau.**

Ví dụ:

```python
Box[int]
Box[str]
Box[User]
Box[Novel]
```

Thay vì phải viết:

```python
IntBox
StringBox
UserBox
NovelBox
```

ta viết **một class duy nhất**.

---

# 1. Generic là gì?

Giả sử có:

```python
@dataclass
class Box:
    value: object
```

Ta có thể:

```python
Box(10)
Box("hello")
Box(User(...))
```

Nhưng type checker không biết chính xác:

```python
box.value
```

là kiểu gì.

Generic giải quyết vấn đề này.

---

# 2. `TypeVar`

Bắt đầu với:

```python
from typing import TypeVar

T = TypeVar("T")
```

`T` là một **type variable**.

Nó có nghĩa:

> "Ở đây tôi chưa biết type cụ thể là gì, nhưng type này sẽ được xác định khi sử dụng."

---

# 3. Generic Dataclass cơ bản

```python
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class Box(Generic[T]):
    value: T
```

Bây giờ:

```python
box = Box(100)
```

conceptually:

```text
Box[int]
```

Còn:

```python
box = Box("hello")
```

conceptually:

```text
Box[str]
```

---

# 4. Generic không tạo ra nhiều class runtime

Đây là điểm rất quan trọng.

Khi viết:

```python
Box[int]
Box[str]
```

không có nghĩa Python tạo:

```text
IntBox
StringBox
```

Runtime vẫn có class:

```python
Box
```

Generic chủ yếu phục vụ:

```text
type checking
static analysis
developer tooling
```

---

# 5. Type checker mới là nơi Generic phát huy sức mạnh

Ví dụ:

```python
box: Box[int] = Box(100)
```

thì:

```python
box.value
```

được hiểu là:

```python
int
```

Nếu:

```python
box: Box[str] = Box("hello")
```

thì:

```python
box.value
```

là:

```python
str
```

Các tool như:

* Pyright
* mypy
* IDE

có thể kiểm tra điều này.

---

# 6. `Generic[T]`

Cấu trúc:

```python
class Box(Generic[T]):
```

nói rằng:

> `Box` là generic class sử dụng type variable `T`.

Field:

```python
value: T
```

nói:

> kiểu của `value` phụ thuộc vào `T`.

---

# 7. Generic với nhiều TypeVar

Ví dụ:

```python
T = TypeVar("T")
K = TypeVar("K")


@dataclass
class Pair(Generic[T, K]):
    first: T
    second: K
```

Có thể:

```python
pair = Pair(10, "hello")
```

conceptually:

```text
Pair[int, str]
```

Hoặc:

```python
Pair("id", 100)
```

→

```text
Pair[str, int]
```

---

# 8. Generic Dataclass giống Template

Bạn có thể hình dung:

```text
Box[T]
```

là template:

```text
T = int
    ↓
Box[int]

T = str
    ↓
Box[str]

T = User
    ↓
Box[User]
```

Nhưng nhớ:

> Đây là cách hiểu về type system, không phải Python runtime tạo class mới cho mỗi T.

---

# 9. Generic Container

Một ví dụ thực tế hơn:

```python
T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: list[T]
    page: int
    total: int
```

Bây giờ:

```python
Page[int]
Page[str]
Page[Novel]
Page[User]
```

---

# 10. `Page[Novel]`

Ví dụ:

```python
@dataclass
class Novel:
    id: int
    title: str
```

Ta có:

```python
page: Page[Novel]
```

và:

```python
page.items
```

là:

```python
list[Novel]
```

Không phải:

```python
list[object]
```

Đây là lợi ích lớn của Generic.

---

# 11. Generic Method

Generic không chỉ áp dụng cho field.

Ta có thể có:

```python
@dataclass
class Box(Generic[T]):
    value: T

    def get(self) -> T:
        return self.value
```

Nếu:

```python
box: Box[int]
```

thì:

```python
box.get()
```

có type:

```text
int
```

---

# 12. Generic Transformation

Ví dụ:

```python
from typing import Callable


@dataclass
class Box(Generic[T]):
    value: T

    def map(self, func: Callable[[T], T]) -> None:
        self.value = func(self.value)
```

Nhưng thiết kế này chưa thật sự hay.

Một abstraction tốt hơn là cho phép chuyển:

```text
T → U
```

---

# 13. Hai TypeVar `T` và `U`

```python
T = TypeVar("T")
U = TypeVar("U")
```

Sau đó:

```python
@dataclass
class Box(Generic[T]):
    value: T

    def map(
        self,
        func: Callable[[T], U]
    ) -> "Box[U]":

        return Box(func(self.value))
```

Ví dụ:

```python
box = Box(100)

result = box.map(str)
```

Type conceptually:

```text
Box[int]
   │
   │ map(str)
   ▼
Box[str]
```

---

# 14. Đây là một pattern cực kỳ mạnh

Ta có:

```text
Box[T]
```

và:

```text
map(T → U)
```

tạo:

```text
Box[U]
```

Ví dụ:

```text
Box[int]
    ↓
map(str)
    ↓
Box[str]
```

hoặc:

```text
Box[User]
    ↓
map(lambda user: user.id)
    ↓
Box[int]
```

---

# 15. Generic Result

Đây là abstraction rất hữu ích trong application architecture.

Ta có:

```python
T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    value: T | None
    error: str | None
```

Có thể:

```python
Result[int]
Result[User]
Result[Novel]
```

Ví dụ:

```python
result: Result[Novel]
```

nghĩa là:

```text
value → Novel | None
error → str | None
```

---

# 16. Nhưng thiết kế trên chưa tối ưu

Ta đang cho phép:

```python
Result(
    value=novel,
    error="something went wrong"
)
```

hoặc:

```python
Result(
    value=None,
    error=None
)
```

Cả hai đều không hợp lệ về mặt domain.

Đây là lúc Generic Dataclass kết hợp với:

```text
inheritance
+
validation
```

---

# 17. Result tốt hơn

Ta có thể tạo:

```python
@dataclass
class Success(Generic[T]):
    value: T
```

và:

```python
@dataclass
class Failure:
    error: str
```

Sau đó:

```text
Result[T]
├── Success[T]
└── Failure
```

Đây là một dạng **sum type pattern**.

---

# 18. Generic + Inheritance

```python
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    pass


@dataclass
class Success(Result[T]):
    value: T


@dataclass
class Failure(Result[T]):
    error: str
```

Bây giờ:

```python
result: Result[Novel]
```

có thể là:

```text
Success[Novel]
```

hoặc:

```text
Failure
```

---

# 19. Type Narrowing

Ví dụ:

```python
result: Result[Novel]
```

sau đó:

```python
if isinstance(result, Success):
    print(result.value.title)
```

Type checker có thể hiểu:

```text
result
↓
Success[Novel]
↓
value: Novel
```

Đây là một pattern rất mạnh trong architecture.

---

# 20. Generic Repository

Bây giờ đến phần đặc biệt quan trọng đối với project của bạn.

Ta có:

```python
T = TypeVar("T")


class Repository(Generic[T]):
    ...
```

Conceptually:

```text
Repository[Novel]
Repository[Chapter]
Repository[Author]
```

Một repository generic có thể định nghĩa:

```python
class Repository(Generic[T]):

    def get(self, id: int) -> T | None:
        ...

    def add(self, entity: T) -> None:
        ...

    def remove(self, entity: T) -> None:
        ...
```

---

# 21. Nhưng Repository không phải Dataclass

Đây là distinction quan trọng.

Repository thường có behavior:

```text
CRUD
query
transaction
persistence
```

nên thường không cần dataclass.

Dataclass phù hợp hơn với:

```text
Entity
DTO
Query
Result
Configuration
Command
Event
```

Generic có thể dùng cho cả hai.

---

# 22. Generic DTO

Ví dụ API:

```python
@dataclass
class ApiResponse(Generic[T]):
    data: T
    status_code: int
    message: str | None = None
```

Ta có:

```text
ApiResponse[User]
ApiResponse[list[User]]
ApiResponse[Novel]
ApiResponse[list[Novel]]
```

---

# 23. Nested Generic

Ví dụ:

```python
response: ApiResponse[list[Novel]]
```

Đọc từ trong ra:

```text
list[Novel]
```

được truyền vào:

```text
ApiResponse[T]
```

nên:

```text
T = list[Novel]
```

Kết quả:

```text
ApiResponse[list[Novel]]
```

Đây là generic composition.

---

# 24. Generic Pagination

Ví dụ thực tế:

```python
@dataclass
class Page(Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
```

API:

```python
response: ApiResponse[Page[Novel]]
```

Ta có:

```text
ApiResponse
    │
    └── Page
         │
         └── Novel
```

Type structure:

```text
ApiResponse[Page[Novel]]
```

Đây là kiểu abstraction bạn sẽ gặp rất nhiều trong framework.

---

# 25. Generic Event

Rất phù hợp với async/event-driven architecture.

```python
T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    payload: T
```

Ví dụ:

```python
@dataclass
class NovelCreated:
    novel_id: int
    title: str
```

Sau đó:

```python
event: Event[NovelCreated]
```

---

# 26. Event Queue

Ví dụ:

```python
from asyncio import Queue


queue: Queue[Event[NovelCreated]]
```

Conceptually:

```text
Queue
 ↓
Event
 ↓
NovelCreated
```

Đây là sự kết hợp:

```text
Generic
+
Dataclass
+
AsyncIO
```

và sau này sẽ rất hữu ích cho crawler worker.

---

# 27. Generic Command

```python
@dataclass
class Command(Generic[T]):
    payload: T
```

Ví dụ:

```python
@dataclass
class CrawlNovel:
    novel_id: int
```

```python
command: Command[CrawlNovel]
```

---

# 28. Generic State

Ví dụ crawler:

```python
@dataclass
class TaskState(Generic[T]):
    task_id: str
    data: T
    status: str
```

Có thể:

```python
TaskState[Novel]
TaskState[Chapter]
TaskState[DownloadTask]
```

---

# 29. Generic Dataclass cho Crawler

Một abstraction rất đáng chú ý:

```python
T = TypeVar("T")


@dataclass
class CrawlResult(Generic[T]):
    data: T
    source: str
    success: bool
    error: str | None = None
```

Ta có:

```python
CrawlResult[Novel]
```

hoặc:

```python
CrawlResult[Chapter]
```

hoặc:

```python
CrawlResult[list[Chapter]]
```

---

# 30. Generic Container + Dataclass Composition

Ta có:

```python
@dataclass
class CrawlResult(Generic[T]):
    data: T
```

và:

```python
@dataclass
class Novel:
    id: int
    title: str
```

Sau đó:

```python
result = CrawlResult(
    data=Novel(
        id=1,
        title="Example"
    )
)
```

Conceptually:

```text
CrawlResult[Novel]
        │
        ▼
      Novel
```

---

# 31. Bound TypeVar

Không phải lúc nào `T` cũng được phép là bất kỳ type nào.

Ví dụ:

```python
T = TypeVar("T", bound="Entity")
```

Nghĩa:

> `T` phải là `Entity` hoặc subclass của `Entity`.

---

# 32. Ví dụ

```python
@dataclass
class Entity:
    id: int
```

Sau đó:

```python
T = TypeVar("T", bound=Entity)
```

và:

```python
@dataclass
class Result(Generic[T]):
    entity: T
```

Có thể:

```python
Result[Novel]
```

nếu:

```python
Novel
```

kế thừa:

```python
Entity
```

---

# 33. Tại sao `bound` hữu ích?

Ví dụ repository:

```python
T = TypeVar("T", bound=Entity)
```

Repository có thể:

```python
class Repository(Generic[T]):

    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...
```

Ta đảm bảo repository chỉ làm việc với:

```text
Entity
```

hoặc subclass.

---

# 34. Constraint vs Bound

Có hai khái niệm rất dễ nhầm.

### Constraint

```python
T = TypeVar(
    "T",
    int,
    str
)
```

T chỉ được:

```text
int
str
```

### Bound

```python
T = TypeVar(
    "T",
    bound=Entity
)
```

T có thể là:

```text
Entity
Novel
Chapter
Author
...
```

miễn là subclass của `Entity`.

---

# 35. Generic Dataclass với Bound

Ví dụ:

```python
@dataclass
class Entity:
    id: int
```

```python
@dataclass
class Novel(Entity):
    title: str
```

```python
T = TypeVar("T", bound=Entity)
```

```python
@dataclass
class EntityResult(Generic[T]):
    entity: T
```

Sau đó:

```python
result: EntityResult[Novel]
```

---

# 36. Covariance

Đây là phần type-system nâng cao.

Có thể:

```python
T_co = TypeVar(
    "T_co",
    covariant=True
)
```

Ví dụ:

```python
class Producer(Generic[T_co]):
    ...
```

Ý tưởng:

```text
Dog <: Animal

Producer[Dog]
    <: Producer[Animal]
```

Nhưng covariance chỉ hợp lý khi abstraction **produce** `T`.

---

# 37. Contravariance

Ngược lại:

```python
T_contra = TypeVar(
    "T_contra",
    contravariant=True
)
```

thường phù hợp với abstraction **consume** `T`.

Ví dụ:

```text
Consumer[Animal]
```

có thể xử lý:

```text
Dog
Cat
```

---

# 38. Invariance

Generic mặc định thường là invariant.

```python
T = TypeVar("T")
```

Điều này có nghĩa:

```text
Box[Dog]
```

không tự động là:

```text
Box[Animal]
```

dù:

```text
Dog <: Animal
```

Đây là hành vi an toàn cho mutable containers.

---

# 39. Tại sao mutable container thường invariant?

Ví dụ:

```python
Box[Dog]
```

nếu cho phép coi nó là:

```python
Box[Animal]
```

thì có thể:

```python
box.value = Cat()
```

Sau đó object ban đầu vốn yêu cầu:

```text
Dog
```

lại chứa:

```text
Cat
```

Do đó invariant giúp bảo vệ type safety.

---

# 40. Generic Dataclass với covariance — cẩn thận

Ví dụ:

```python
T_co = TypeVar(
    "T_co",
    covariant=True
)


@dataclass
class Result(Generic[T_co]):
    value: T_co
```

Ở đây `Result` chỉ nên được sử dụng theo cách produce `T`.

Nếu thêm:

```python
def set_value(self, value: T_co):
    ...
```

thì covariance sẽ trở thành thiết kế không hợp lý.

Đây là vấn đề của **type-system semantics**, không phải runtime Python.

---

# 41. Generic Factory

Dataclass cũng rất phù hợp với factory.

```python
T = TypeVar("T")


@dataclass
class Box(Generic[T]):
    value: T

    @classmethod
    def create(
        cls,
        value: T
    ) -> Box[T]:

        return cls(value)
```

Conceptually:

```text
Box.create(10)
     ↓
Box[int]
```

---

# 42. Generic `classmethod` với Python hiện đại

Bạn sẽ gặp pattern:

```python
from typing import Self


@dataclass
class Box(Generic[T]):
    value: T

    @classmethod
    def create(
        cls,
        value: T
    ) -> Self:
        return cls(value)
```

`Self` giúp biểu diễn:

> method trả về instance của chính subclass hiện tại.

Đây là điểm nối trực tiếp với **Buổi 3 — Type Hint / Self**.

---

# 43. Generic Dataclass + `Self`

Ví dụ subclass:

```python
@dataclass
class SpecialBox(Box[T]):
    name: str = "special"
```

Nếu factory được thiết kế với `Self`, type checker có thể hiểu subclass trả về:

```text
SpecialBox[T]
```

thay vì chỉ:

```text
Box[T]
```

Đây là một trong những lý do `Self` rất hữu ích khi xây framework.

---

# 44. Generic Dataclass + `ClassVar`

Ví dụ:

```python
from typing import ClassVar


@dataclass
class Box(Generic[T]):
    value: T

    type_name: ClassVar[str] = "Box"
```

`ClassVar` không phải instance field.

Do đó dataclass không đưa:

```python
type_name
```

vào generated `__init__()`.

---

# 45. Generic Dataclass + `field()`

Tất cả kiến thức Buổi 4 vẫn áp dụng:

```python
@dataclass
class Page(Generic[T]):

    items: list[T] = field(
        default_factory=list
    )

    page: int = 1

    total: int = 0
```

Generic chỉ kiểm soát:

```text
T
```

còn `field()` kiểm soát:

```text
dataclass field semantics
```

Hai hệ thống hoạt động cùng nhau.

---

# 46. Generic Nested Dataclass

Ví dụ crawler:

```python
@dataclass
class Chapter:
    id: int
    title: str
```

```python
@dataclass
class Novel:
    id: int
    title: str
    chapters: list[Chapter]
```

Generic result:

```python
@dataclass
class CrawlResult(Generic[T]):
    data: T
```

Ta có:

```python
result: CrawlResult[Novel]
```

và:

```python
result.data.chapters
```

là:

```text
list[Chapter]
```

Type information được truyền xuyên qua abstraction.

---

# 47. Generic Dataclass trong Repository Architecture

Có thể hình dung:

```text
                    Entity
                      │
                      ▼
             Repository[T]
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     NovelRepo   ChapterRepo  AuthorRepo
          │           │           │
          ▼           ▼           ▼
       Novel       Chapter      Author
```

DTO:

```text
ApiResponse[T]
```

Result:

```text
Result[T]
```

Event:

```text
Event[T]
```

Task:

```text
Task[T]
```

Đây chính là cách Generic giúp framework giảm duplication.

---

# 48. Generic Dataclass trong Queue Server

Liên hệ với queue server bạn đang xây:

```python
@dataclass
class QueueItem(Generic[T]):
    id: str
    payload: T
    retry_count: int = 0
```

Có thể:

```text
QueueItem[CrawlNovel]
QueueItem[DownloadImage]
QueueItem[CrawlChapter]
```

Ví dụ:

```python
@dataclass
class CrawlNovel:
    novel_id: int
```

```python
item: QueueItem[CrawlNovel]
```

Bây giờ worker có thể biết:

```python
item.payload.novel_id
```

thay vì:

```python
item.payload["novel_id"]
```

Đây là sự khác biệt rất lớn giữa:

```text
dict-based architecture
```

và:

```text
typed domain architecture
```

---

# 49. Generic Dataclass cho Crawl Task

```python
@dataclass
class CrawlTask(Generic[T]):
    task_id: str
    payload: T
    priority: int = 0
    retry_count: int = 0
```

Ví dụ:

```python
@dataclass
class CrawlNovelRequest:
    novel_id: int
```

```python
task = CrawlTask(
    task_id="task-001",
    payload=CrawlNovelRequest(100)
)
```

Conceptually:

```text
CrawlTask[CrawlNovelRequest]
```

---

# 50. Generic Dataclass không phải Dynamic Type Validation

Điểm cực kỳ quan trọng:

```python
Box[int]
```

không có nghĩa Python runtime tự động chặn:

```python
Box("hello")
```

Generic chủ yếu là:

```text
static typing
```

Python không biến nó thành runtime validator.

Nếu muốn runtime validation, cần:

```text
__post_init__
```

hoặc:

```text
Pydantic
```

hoặc custom validation.

---

# 51. Generic + Runtime Validation

Ví dụ đơn giản:

```python
@dataclass
class Box(Generic[T]):
    value: T
```

Python không tự biết:

```text
T = int
```

ở runtime theo cách bạn có thể dùng để validate mọi trường hợp.

Nếu cần runtime validation:

```python
@dataclass
class IntBox:
    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise TypeError(...)
```

Hoặc sử dụng framework validation chuyên dụng.

---

# 52. Generic Dataclass và `__orig_class__`

Trong một số trường hợp, Python runtime có thể giữ thông tin generic specialization trên instance:

```python
box = Box[int](10)
```

có thể có:

```python
box.__orig_class__
```

Nhưng:

> **Không nên thiết kế business logic phụ thuộc vào `__orig_class__`.**

Nó là runtime typing metadata với nhiều giới hạn.

Đừng nhầm:

```text
Generic type information
```

với:

```text
runtime validation system
```

---

# 53. Generic Dataclass + `Annotated`

Có thể kết hợp:

```python
from typing import Annotated


@dataclass
class Box(Generic[T]):
    value: Annotated[T, "required"]
```

Nhưng metadata trong `Annotated` không tự động trở thành validation.

Nó chỉ là typing metadata.

Framework có thể đọc metadata và áp dụng behavior riêng.

---

# 54. Generic Dataclass + Metadata

Kết hợp với `field()`:

```python
@dataclass
class Box(Generic[T]):
    value: T = field(
        metadata={
            "description": "generic value"
        }
    )
```

Metadata vẫn có thể được đọc:

```python
from dataclasses import fields

for f in fields(Box):
    print(f.metadata)
```

Generic không làm mất khả năng metadata.

---

# 55. Generic Dataclass và Serialization

Ví dụ:

```python
@dataclass
class ApiResponse(Generic[T]):
    data: T
```

Ta có:

```text
ApiResponse[Novel]
```

Khi serialize:

```json
{
    "data": {
        "id": 1,
        "title": "Novel"
    }
}
```

Nhưng JSON không chứa:

```text
T = Novel
```

Generic information thường là compile/static typing concept.

Nếu API cần runtime schema, cần thêm metadata/schema system.

Đây là lý do các thư viện như Pydantic có hệ thống type introspection mạnh hơn.

---

# 56. Generic Dataclass vs Pydantic Generic Model

Dataclass:

```python
@dataclass
class Response(Generic[T]):
    data: T
```

ưu tiên:

```text
lightweight object modeling
```

Pydantic generic model ưu tiên:

```text
runtime validation
serialization
schema
```

Không có cái nào "luôn tốt hơn".

Chọn theo requirement.

---

# 57. Một Pattern rất quan trọng: Envelope

Một pattern thường gặp:

```python
@dataclass
class Envelope(Generic[T]):
    data: T
    request_id: str
    timestamp: float
```

Dùng:

```text
Envelope[Novel]
Envelope[Chapter]
Envelope[list[Novel]]
Envelope[Task]
```

Đây là pattern rất tốt cho:

* API
* event
* message queue
* worker
* RPC

---

# 58. Generic Event Envelope

```python
@dataclass
class Event(Generic[T]):
    name: str
    payload: T
    timestamp: float
```

Ví dụ:

```python
event: Event[NovelCreated]
```

Conceptually:

```text
Event
 ├── name
 ├── timestamp
 └── payload
       ↓
   NovelCreated
```

Đây chính là nền tảng để sau này thiết kế event system cho crawler.

---

# 59. Generic Dataclass và `Protocol`

Buổi 17 sẽ đi sâu hơn, nhưng có thể nhìn trước:

```python
T = TypeVar("T")


class Serializer(Protocol[T]):
    def serialize(self, value: T) -> bytes:
        ...
```

Sau đó:

```text
Serializer[Novel]
Serializer[Chapter]
```

Kết hợp:

```text
Generic
+
Dataclass
+
Protocol
```

sẽ tạo ra abstraction rất mạnh.

---

# 60. Generic Dataclass và Factory Pattern

Ví dụ:

```python
@dataclass
class Factory(Generic[T]):
    creator: Callable[[], T]

    def create(self) -> T:
        return self.creator()
```

Dùng:

```python
factory: Factory[Novel]
```

và:

```python
novel = factory.create()
```

Type checker biết:

```text
create() → Novel
```

---

# 61. Generic Dataclass và Repository thực tế

Ví dụ abstraction:

```python
T = TypeVar("T")


class Repository(Generic[T]):

    def get(self, id: int) -> T | None:
        raise NotImplementedError

    def save(self, entity: T) -> None:
        raise NotImplementedError
```

Sau đó:

```python
class NovelRepository(
    Repository[Novel]
):
    ...
```

Ta có:

```python
novel = repo.get(1)
```

type:

```text
Novel | None
```

Đây chính là một trong những ứng dụng quan trọng nhất của Generic trong architecture.

---

# 62. Generic Dataclass và Value Object

Ví dụ:

```python
@dataclass(frozen=True)
class Value(Generic[T]):
    value: T
```

Có thể:

```text
Value[int]
Value[str]
Value[UUID]
```

Kết hợp với:

```python
frozen=True
```

ta có immutable generic value container.

Đây là pattern rất hợp với DDD.

---

# 63. Generic + Frozen + Slots

Một abstraction rất đẹp:

```python
@dataclass(
    frozen=True,
    slots=True
)
class Value(Generic[T]):
    value: T
```

Ta có:

```text
Generic
+
Immutable
+
Slots
+
Dataclass
```

Đây là kiểu object rất phù hợp cho:

* value object
* configuration
* message
* event
* cache key

---

# 64. Ví dụ `CacheKey[T]`

```python
@dataclass(
    frozen=True,
    slots=True
)
class CacheKey(Generic[T]):
    value: T
```

Có thể:

```python
key = CacheKey("novel:100")
```

Nếu object hashable, nó có thể sử dụng trong:

```python
cache = {}
```

Đây kết nối trực tiếp với:

> Buổi 5 — Frozen
> Buổi 7 — Slots
> Buổi 27 — Hash

---

# 65. Những lỗi phổ biến

## Lỗi 1 — Nghĩ Generic tạo runtime type

Sai:

```text
Box[int] = một class hoàn toàn khác
```

Không phải.

---

## Lỗi 2 — Nghĩ Generic tự validate

Sai:

```text
Box[int] sẽ runtime reject "hello"
```

Không mặc định.

---

## Lỗi 3 — Dùng `Any` thay cho Generic

Ví dụ:

```python
@dataclass
class Box:
    value: Any
```

mất rất nhiều type information.

Generic:

```python
@dataclass
class Box(Generic[T]):
    value: T
```

giữ relationship giữa input/output.

---

# 66. `Any` vs `T`

### `Any`

```python
value: Any
```

nghĩa gần như:

> Tôi không muốn type checker kiểm soát chỗ này.

### `T`

```python
value: T
```

nghĩa:

> Có một type cụ thể, nhưng type đó được xác định bởi caller/context.

Đây là khác biệt cực kỳ quan trọng.

---

# 67. `object` vs `T`

```python
value: object
```

nghĩa:

> value có thể là bất kỳ object nào.

Nhưng sau đó type checker chỉ biết:

```text
object
```

Còn:

```python
value: T
```

giữ được type relationship.

Ví dụ:

```python
def unwrap(box: Box[T]) -> T:
    return box.value
```

Nếu:

```text
Box[Novel]
```

thì:

```text
unwrap() → Novel
```

---

# 68. Generic giúp giữ Type Relationship

Đây chính là bản chất sâu nhất.

Không chỉ:

```text
"có một type"
```

mà là:

```text
input type
      ↓
   T
      ↓
output type
```

Ví dụ:

```python
def unwrap(box: Box[T]) -> T:
    ...
```

`T` liên kết:

```text
Box[T]
```

với:

```text
T
```

---

# 69. Mental Model

Hãy nhớ:

```text
TypeVar
   ↓
đại diện cho type

Generic[T]
   ↓
class phụ thuộc type T

Dataclass
   ↓
generate data-oriented behavior

Generic Dataclass
   ↓
reusable typed data structure
```

---

# 70. Áp dụng vào hệ thống crawler của bạn

Ta có thể xây một family abstraction:

```text
                    T
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      CrawlTask   Event    Result
          │         │         │
          ▼         ▼         ▼
        Novel     Novel     Novel
```

Ví dụ:

```python
CrawlTask[Novel]
Event[Novel]
CrawlResult[Novel]
```

và:

```python
CrawlTask[Chapter]
Event[Chapter]
CrawlResult[Chapter]
```

Không cần duplicate class.

---

# 71. Kiến trúc nhìn tổng thể

```text
                 Generic[T]
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     Task[T]      Event[T]     Result[T]
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
                 Domain Model
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Novel      Chapter    Author
```

Đây là một abstraction rất gần với framework architecture thực tế.

---

# 72. Bài tập Buổi 15

### Bài 1

Viết:

```python
@dataclass
class Box(Generic[T]):
    value: T
```

và:

```python
get()
```

---

### Bài 2

Viết:

```python
@dataclass
class Page(Generic[T]):
    items: list[T]
    page: int
    total: int
```

Test:

```text
Page[int]
Page[str]
Page[Novel]
```

---

### Bài 3

Viết:

```python
@dataclass
class ApiResponse(Generic[T]):
    data: T
    status_code: int
```

Test:

```text
ApiResponse[Novel]
ApiResponse[list[Novel]]
```

---

### Bài 4

Viết:

```python
@dataclass
class QueueItem(Generic[T]):
    id: str
    payload: T
    retry_count: int = 0
```

Sau đó tạo:

```python
QueueItem[CrawlNovel]
```

---

### Bài 5 — nâng cao

Thiết kế:

```text
Result[T]
├── Success[T]
└── Failure
```

và sử dụng:

```python
Result[Novel]
```

---

### Bài 6 — Architecture

Thiết kế:

```text
Repository[T]
CrawlTask[T]
CrawlResult[T]
Event[T]
```

sao cho có thể dùng:

```text
Novel
Chapter
Image
DownloadTask
```

mà không phải duplicate abstraction.

---

# 73. Tổng kết Buổi 15

Hôm nay cần nắm thật chắc 10 điểm:

```text
1. TypeVar
2. Generic[T]
3. Generic Dataclass
4. Generic với nhiều TypeVar
5. Bound TypeVar
6. Constraint TypeVar
7. Covariance / Contravariance / Invariance
8. Generic nested types
9. Generic + inheritance
10. Generic trong architecture
```

Quan trọng nhất là hiểu:

```python
@dataclass
class Box(Generic[T]):
    value: T
```

không đơn giản chỉ là:

> "Box chứa một giá trị."

Mà là:

> **Box giữ một mối quan hệ type-safe giữa abstraction và kiểu dữ liệu mà nó chứa.**

Và khi kết hợp với architecture:

```text
Repository[T]
DTO[T]
Result[T]
Event[T]
Task[T]
Response[T]
Page[T]
```

Generic Dataclass trở thành một công cụ cực kỳ mạnh để xây **framework Python có tính tái sử dụng cao**.

---

## Roadmap hiện tại

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ✅
16. Abstract Dataclass           ← tiếp theo
17. Protocols
18. Descriptors
19. Metaclass + Dataclass
20. Dynamic Dataclass
```

**Buổi 16** sẽ chuyển sang **Abstract Dataclass**: kết hợp `@dataclass` với `ABC`, `abstractmethod`, inheritance, abstract property và cách thiết kế các domain model/framework base class mà subclass bắt buộc phải implement behavior.
