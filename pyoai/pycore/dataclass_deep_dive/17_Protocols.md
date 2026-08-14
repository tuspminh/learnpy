# Dataclass Deep Dive — Buổi 17

# Protocols + Typing + Duck Typing

Hôm nay chúng ta chuyển từ tư duy:

```text
ABC
 ↓
"Class này phải kế thừa tôi"
```

sang:

```text
Protocol
 ↓
"Object này chỉ cần có đúng interface"
```

Đây là một bước rất quan trọng để hiểu **Python typing hiện đại** và đặc biệt hữu ích khi bạn xây **Repository, Parser, Crawler Plugin, Service, Adapter**.

---

# 1. Nhắc lại ABC từ Buổi 16

Ví dụ:

```python
from abc import ABC, abstractmethod


class Parser(ABC):

    @abstractmethod
    def parse(self, html: str):
        ...
```

Muốn trở thành `Parser`:

```python
class NovelParser(Parser):

    def parse(self, html: str):
        return "novel"
```

Ta có:

```text
Parser
   ↑
NovelParser
```

Đây là **nominal typing**.

Nói đơn giản:

> Tôi là `Parser` vì tôi khai báo rằng tôi kế thừa `Parser`.

---

# 2. Duck Typing

Python có một triết lý nổi tiếng:

> If it walks like a duck and quacks like a duck, it's a duck.

Ví dụ:

```python
class Duck:

    def quack(self):
        print("quack")


class Person:

    def quack(self):
        print("I'm pretending to be a duck")
```

Hàm:

```python
def make_it_quack(obj):
    obj.quack()
```

Không quan tâm:

```text
obj là Duck?
obj là Person?
```

Chỉ quan tâm:

```text
obj có .quack()?
```

Đó là **duck typing**.

---

# 3. Vấn đề của Duck Typing thuần túy

Runtime rất linh hoạt:

```python
def save(repository):
    repository.save(...)
```

Nhưng IDE/type checker không biết:

```text
repository
    ?
```

Nó không biết object cần có:

```python
save()
get()
delete()
```

Đây là nơi `Protocol` xuất hiện.

---

# 4. Protocol là gì?

Python cung cấp:

```python
from typing import Protocol
```

Ta định nghĩa:

```python
class Repository(Protocol):

    def save(self, entity) -> None:
        ...
```

Điểm quan trọng:

**Class không cần kế thừa `Repository`.**

Ví dụ:

```python
class SQLiteRepository:

    def save(self, entity) -> None:
        print("save")
```

`SQLiteRepository` vẫn phù hợp với protocol.

---

# 5. Structural Typing

Có hai kiểu tư duy:

### Nominal

```text
class A(B)
```

Muốn là `B`:

```text
phải khai báo kế thừa B
```

### Structural

```text
class A:
    có method giống B
```

thì:

```text
A phù hợp với B
```

---

# 6. ABC vs Protocol

So sánh:

| ABC                 | Protocol          |         |
| ------------------- | ----------------- | ------- |
| Nominal typing      | Structural typing |         |
| Cần inheritance     | Không cần         |         |
| Có thể chứa state   | Chủ yếu interface |         |
| Có implementation   | Có thể            |         |
| `abstractmethod`    | Method signature  |         |
| Runtime enforcement | Có                |         |
| Static typing       | Có                |         |
| Loose coupling      | Thấp hơn          | Cao hơn |

---

# 7. Protocol cơ bản

```python
from typing import Protocol


class Serializer(Protocol):

    def serialize(self, value: object) -> str:
        ...
```

Implementation:

```python
class JsonSerializer:

    def serialize(self, value: object) -> str:
        return "{}"
```

Không cần:

```python
class JsonSerializer(Serializer):
```

---

# 8. Dataclass + Protocol

Đây là trọng tâm hôm nay.

Ví dụ:

```python
from dataclasses import dataclass
from typing import Protocol


class HasId(Protocol):
    id: int


@dataclass
class User:
    id: int
    name: str
```

`User` phù hợp với:

```python
HasId
```

vì có:

```python
id: int
```

---

# 9. Protocol mô tả Data Shape

Protocol không chỉ mô tả method.

Nó có thể mô tả attribute:

```python
class Identifiable(Protocol):
    id: int
```

Dataclass:

```python
@dataclass
class Novel:
    id: int
    title: str
```

```python
@dataclass
class Chapter:
    id: int
    content: str
```

Cả hai đều có thể phù hợp:

```text
Identifiable
```

---

# 10. Một function dùng Protocol

```python
def print_id(obj: Identifiable):
    print(obj.id)
```

Có thể:

```python
novel = Novel(1, "Python")

print_id(novel)
```

Không cần:

```python
Novel(Identifiable)
```

Đây chính là sức mạnh của structural typing.

---

# 11. Protocol với Method

Ví dụ:

```python
class Savable(Protocol):

    def save(self) -> None:
        ...
```

Dataclass:

```python
@dataclass
class User:

    id: int

    def save(self) -> None:
        print("saving user")
```

`User` phù hợp với:

```text
Savable
```

---

# 12. Protocol với nhiều method

```python
class Repository(Protocol):

    def get(self, id: int):
        ...

    def save(self, entity) -> None:
        ...

    def delete(self, id: int) -> None:
        ...
```

Implementation:

```python
class SQLiteRepository:

    def get(self, id: int):
        ...

    def save(self, entity) -> None:
        ...

    def delete(self, id: int) -> None:
        ...
```

Không cần inheritance.

---

# 13. Đây là Loose Coupling

Nếu viết:

```python
def process(repo: Repository):
    ...
```

code không phụ thuộc:

```text
SQLiteRepository
PostgresRepository
MemoryRepository
MockRepository
```

Nó chỉ phụ thuộc:

```text
Repository interface
```

Ta có:

```text
             Repository Protocol
                    ↑
          ┌─────────┼─────────┐
          │         │         │
       SQLite     Memory     Mock
```

---

# 14. Protocol + Generic

Bây giờ nâng cấp.

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar("T")


class Repository(Protocol[T]):

    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...
```

Sau đó:

```python
class NovelRepository:

    def get(self, id: int) -> Novel | None:
        ...

    def save(self, entity: Novel) -> None:
        ...
```

Concept:

```text
Repository[T]
      │
      ├── Repository[Novel]
      ├── Repository[Chapter]
      └── Repository[Author]
```

---

# 15. Protocol + Dataclass + Generic

Đây là pattern rất mạnh:

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar


T = TypeVar("T")


class Repository(Protocol[T]):

    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...


@dataclass
class Novel:
    id: int
    title: str
```

Implementation:

```python
class NovelRepository:

    def get(self, id: int) -> Novel | None:
        ...

    def save(self, entity: Novel) -> None:
        ...
```

---

# 16. ABC vs Protocol trong Repository

### ABC

```python
class Repository(ABC, Generic[T]):

    @abstractmethod
    def save(self, entity: T):
        ...
```

Implementation:

```python
class SQLiteRepository(Repository[Novel]):
    ...
```

Có coupling:

```text
SQLiteRepository
       ↓
Repository
```

### Protocol

```python
class Repository(Protocol[T]):

    def save(self, entity: T):
        ...
```

Implementation:

```python
class SQLiteRepository:
    ...
```

Không coupling inheritance.

---

# 17. Khi nào ABC tốt hơn?

Dùng ABC khi bạn muốn:

### 1. Shared implementation

```python
class Parser(ABC):

    def normalize(self, text):
        return text.strip()

    @abstractmethod
    def parse(self, html):
        ...
```

### 2. Shared state

```python
@dataclass
class Parser(ABC):
    source: str
```

### 3. Enforce inheritance hierarchy

Ví dụ:

```text
Plugin
 ├── NovelPlugin
 ├── ChapterPlugin
 └── ImagePlugin
```

---

# 18. Khi nào Protocol tốt hơn?

Dùng Protocol khi bạn muốn:

### Dependency Inversion

```python
def service(repo: Repository):
    ...
```

không cần biết repository thực sự là class nào.

### Adapter

```text
External API
     ↓
Adapter
     ↓
Protocol
```

### Testing

```text
ProductionRepository
MockRepository
FakeRepository
```

đều có thể đáp ứng cùng protocol.

---

# 19. Protocol + `@runtime_checkable`

Thông thường:

```python
isinstance(obj, Protocol)
```

không được phép.

Có thể dùng:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasId(Protocol):
    id: int
```

Sau đó:

```python
@dataclass
class User:
    id: int
```

Có thể:

```python
isinstance(User(1), HasId)
```

Nhưng cần hiểu rất rõ:

> Runtime protocol checking chỉ kiểm tra cấu trúc ở mức runtime đơn giản, không thay thế static type checking.

---

# 20. `runtime_checkable` không kiểm tra type annotation đầy đủ

Ví dụ:

```python
@runtime_checkable
class HasId(Protocol):
    id: int
```

Object:

```python
class Weird:
    id = "hello"
```

Runtime structural check có thể vẫn coi attribute `id` tồn tại.

Nó không hoạt động như:

```text
mypy
pyright
```

để kiểm tra:

```text
id phải là int
```

Đây là khác biệt rất quan trọng.

---

# 21. Protocol với `@property`

Ví dụ:

```python
class Named(Protocol):

    @property
    def name(self) -> str:
        ...
```

Dataclass:

```python
@dataclass
class User:
    username: str

    @property
    def name(self) -> str:
        return self.username
```

User phù hợp với:

```text
Named
```

---

# 22. Protocol có thể kế thừa Protocol

```python
class Identifiable(Protocol):
    id: int


class Named(Protocol):
    name: str


class EntityProtocol(
    Identifiable,
    Named,
    Protocol,
):
    pass
```

Object cần có:

```text
id
name
```

---

# 23. Protocol inheritance khác class inheritance

Đây là điểm rất quan trọng.

```python
class A:
    ...
```

là implementation inheritance.

Trong:

```python
class AProtocol(Protocol):
    ...
```

chúng ta đang mô tả:

```text
contract
```

Không nên nghĩ Protocol đơn giản là "ABC phiên bản khác".

---

# 24. Dataclass rất hợp với Protocol

Dataclass thường đại diện cho:

```text
Data
```

Protocol thường đại diện cho:

```text
Behavior / Shape
```

Ví dụ:

```python
@dataclass
class Novel:
    id: int
    title: str
```

Protocol:

```python
class Persistable(Protocol):

    id: int

    def save(self) -> None:
        ...
```

Nếu Novel có:

```python
def save(self):
    ...
```

thì nó phù hợp.

---

# 25. Protocol cho Entity

Một thiết kế tốt:

```python
class EntityProtocol(Protocol):
    id: int
```

Các dataclass:

```python
@dataclass
class Novel:
    id: int
    title: str


@dataclass
class Chapter:
    id: int
    content: str
```

Có thể viết:

```python
def get_id(entity: EntityProtocol) -> int:
    return entity.id
```

Không cần:

```text
Novel
Chapter
Entity
```

phải nằm trong cùng inheritance tree.

---

# 26. Protocol cho Repository

Đây là ứng dụng cực kỳ thực tế:

```python
T = TypeVar("T")


class Repository(Protocol[T]):

    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...

    def delete(self, id: int) -> None:
        ...
```

Service:

```python
def create_novel(
    repo: Repository[Novel],
    novel: Novel,
):
    repo.save(novel)
```

Service không biết:

```text
SQLite?
PostgreSQL?
Memory?
Mock?
```

---

# 27. Dependency Injection

Protocol đặc biệt mạnh khi kết hợp DI.

```python
class NovelService:

    def __init__(
        self,
        repository: Repository[Novel],
    ):
        self.repository = repository
```

Production:

```python
service = NovelService(
    SQLiteNovelRepository(...)
)
```

Testing:

```python
service = NovelService(
    FakeNovelRepository()
)
```

Không cần thay đổi:

```text
NovelService
```

---

# 28. Protocol cho Crawler Plugin

Trong crawler framework của bạn:

```python
class CrawlerPlugin(Protocol):

    name: str

    def crawl_novel(self, url: str) -> Novel:
        ...

    def crawl_chapter(self, url: str) -> Chapter:
        ...
```

Plugin:

```python
@dataclass
class MyNovelPlugin:

    name: str = "my-source"

    def crawl_novel(self, url: str) -> Novel:
        ...

    def crawl_chapter(self, url: str) -> Chapter:
        ...
```

Không cần:

```python
class MyNovelPlugin(CrawlerPlugin)
```

---

# 29. Đây là kiến trúc Plugin rất tốt

Ta có:

```text
                 CrawlerPlugin
                    Protocol
                       │
          ┌────────────┼────────────┐
          │            │            │
       Source A      Source B     Source C
          │            │            │
       dataclass     dataclass    dataclass
```

Core framework chỉ biết:

```text
CrawlerPlugin
```

Không biết implementation cụ thể.

Đây chính là:

> **Dependency Inversion + Structural Typing**

---

# 30. Protocol vs ABC trong Plugin Architecture

### ABC

```text
Plugin
  ↑
PluginA
PluginB
PluginC
```

Framework kiểm soát hierarchy.

### Protocol

```text
             Plugin Protocol
              ↑     ↑     ↑
              │     │     │
             A     B     C
```

A/B/C hoàn toàn độc lập.

Điều này rất hữu ích khi plugin đến từ:

```text
package khác
third-party
external developer
```

---

# 31. Một ưu điểm lớn: Adapter

Giả sử thư viện bên ngoài có:

```python
class ExternalStorage:

    def put(self, key, value):
        ...
```

Framework cần:

```python
class Storage(Protocol):

    def save(self, key, value):
        ...
```

Không thể sửa:

```text
ExternalStorage
```

Ta tạo adapter:

```python
class StorageAdapter:

    def __init__(self, storage):
        self.storage = storage

    def save(self, key, value):
        self.storage.put(key, value)
```

Adapter tự động phù hợp với:

```text
Storage Protocol
```

Không cần inheritance.

Đây là một trong những điểm Protocol cực kỳ mạnh.

---

# 32. Protocol + Dataclass Adapter

Adapter cũng có thể là dataclass:

```python
@dataclass
class StorageAdapter:

    storage: ExternalStorage

    def save(self, key, value):
        self.storage.put(key, value)
```

Ta có:

```text
ExternalStorage
       │
       ▼
StorageAdapter
       │
       ▼
Storage Protocol
```

Dataclass quản lý dependency state.

Protocol định nghĩa contract.

---

# 33. ABC + Protocol có thể cùng tồn tại

Không phải:

```text
ABC hoặc Protocol
```

mà đôi khi:

```text
ABC + Protocol
```

Ví dụ framework core:

```python
class BaseParser(ABC):
    ...
```

Public integration boundary:

```python
class ParserProtocol(Protocol):
    ...
```

Một bên dùng:

```text
inheritance
```

một bên dùng:

```text
structural typing
```

---

# 34. Một nguyên tắc kiến trúc

Ở **core domain**:

```text
ABC
```

có thể hữu ích nếu hierarchy có ý nghĩa.

Ở **application boundary**:

```text
Protocol
```

thường rất phù hợp.

Ví dụ:

```text
Domain
  ↓
ABC Entity behavior

Application
  ↓
Protocol Repository

Infrastructure
  ↓
SQLiteRepository
```

---

# 35. Ví dụ hoàn chỉnh

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic


T = TypeVar("T")


@dataclass
class Novel:
    id: int
    title: str


class Repository(Protocol[T]):

    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...


@dataclass
class MemoryNovelRepository:

    novels: dict[int, Novel]

    def get(self, id: int) -> Novel | None:
        return self.novels.get(id)

    def save(self, entity: Novel) -> None:
        self.novels[entity.id] = entity
```

Service:

```python
class NovelService:

    def __init__(
        self,
        repository: Repository[Novel],
    ):
        self.repository = repository

    def create(self, novel: Novel):
        self.repository.save(novel)
```

Sử dụng:

```python
repo = MemoryNovelRepository({})

service = NovelService(repo)

service.create(
    Novel(
        id=1,
        title="Python Deep Dive",
    )
)
```

Điểm quan trọng:

```text
NovelService
     │
     ▼
Repository[Novel]
     │
     ▼
MemoryNovelRepository
```

`NovelService` **không phụ thuộc implementation**.

---

# 36. Mental Model

Hãy ghi nhớ:

```text
ABC
 │
 └── "You must inherit from me."

Protocol
 │
 └── "You only need to look like me."
```

Hoặc:

```text
ABC
 ↓
Nominal typing

Protocol
 ↓
Structural typing

Duck typing
 ↓
Runtime structural behavior
```

---

# 37. Dataclass trong toàn bộ bức tranh

Đến Buổi 17, ta có:

```text
Dataclass
   │
   ├── State
   │
   ├── Generated methods
   │
   ├── Validation
   │
   ├── Inheritance
   │
   ├── Generic
   │
   └── Composition
```

Và bây giờ:

```text
Protocol
   │
   ├── Interface
   ├── Structural typing
   ├── Dependency inversion
   ├── Adapter
   └── Plugin
```

Kết hợp:

```text
Dataclass
    +
Protocol
    +
Generic
    ↓
Flexible Python architecture
```

---

# 38. Bài tập Buổi 17

## Bài 1 — Protocol cơ bản

Tạo:

```python
class Identifiable(Protocol):
    id: int
```

Sau đó tạo:

```text
User
Novel
Chapter
```

đều là dataclass.

Viết:

```python
def get_id(obj: Identifiable) -> int:
    ...
```

---

## Bài 2 — Repository Protocol

Tạo:

```python
class Repository(Protocol[T]):
    ...
```

với:

```text
get()
save()
delete()
```

Tạo:

```text
MemoryRepository
SQLiteRepository
FakeRepository
```

Không class nào được phép kế thừa `Repository`.

---

## Bài 3 — Generic Protocol

Thiết kế:

```text
Repository[Novel]
Repository[Chapter]
Repository[Author]
```

để type checker có thể phát hiện:

```python
repository.save(chapter)
```

khi repository chỉ nhận:

```text
Novel
```

---

## Bài 4 — Crawler Plugin

Tạo:

```python
class CrawlerPlugin(Protocol):
    name: str

    def crawl_novel(self, url: str) -> Novel:
        ...

    def crawl_chapter(self, url: str) -> Chapter:
        ...
```

Tạo hai plugin độc lập:

```text
SourceAPlugin
SourceBPlugin
```

Không inheritance.

---

## Bài 5 — Adapter

Giả sử:

```python
class ExternalDownloader:

    def download(self, url: str) -> bytes:
        ...
```

Framework yêu cầu:

```python
class Downloader(Protocol):

    def fetch(self, url: str) -> bytes:
        ...
```

Viết:

```text
DownloaderAdapter
```

để biến `ExternalDownloader` thành `Downloader`.

---

# 39. Thử thách Deep Dive

Hãy tự trả lời 5 câu này:

1. Tại sao `Protocol` không cần inheritance?
2. ABC và Protocol khác nhau ở **nominal typing vs structural typing** như thế nào?
3. Tại sao Protocol phù hợp với Dependency Injection?
4. Tại sao `runtime_checkable` không thay thế mypy/pyright?
5. Trong crawler framework, khi nào bạn chọn `ABC`, khi nào chọn `Protocol`?

Nếu hiểu được 5 câu này thì bạn đã nắm được phần cốt lõi của Buổi 17.

---

# Roadmap hiện tại

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ✅
16. Abstract Dataclass            ✅
17. Protocols                    ✅ ← hôm nay
18. Descriptors                  ← tiếp theo
19. Metaclass + Dataclass
20. Dynamic Dataclass
```

**Buổi 18** chúng ta sẽ đi vào phần khó hơn nhiều: **Descriptors + `property` + validator + custom field**, và đặc biệt sẽ tìm hiểu một câu hỏi rất quan trọng:

> **`dataclasses.field()` thực sự làm gì với attribute của class, và liệu ta có thể tự tạo một `field()` riêng có validation hay không?**
