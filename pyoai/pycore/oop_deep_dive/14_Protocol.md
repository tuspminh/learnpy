# OOP Deep Dive – Buổi 14

# Protocol (PEP 544), Structural Typing và Static Duck Typing

Đây là một trong những chủ đề hiện đại nhất của Python.

Nếu Buổi 13 giúp bạn hiểu **ABC (Abstract Base Class)** thì hôm nay chúng ta sẽ học một khái niệm mới được bổ sung từ Python 3.8:

> **Protocol (PEP 544)**

Đây là nền tảng của:

- FastAPI
- Pydantic
- LangChain
- Pandas
- VSCode/Pylance
- MyPy
- Pyright

Sau buổi này bạn sẽ hiểu tại sao rất nhiều dự án Python hiện đại **không còn dùng ABC quá nhiều**, mà chuyển sang **Protocol**.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Structural Typing
- Nominal Typing
- Protocol
- Runtime Protocol
- Static Duck Typing
- Type Checker
- Protocol Generic

---

# 1. Ôn tập

Chúng ta đã học ba cách thiết kế API.

## Cách 1 - Duck Typing

```text-x-trilium-auto
class Dog:
    def speak(self):
        print("Woof")
```

```text-x-trilium-auto
def make_sound(obj):
    obj.speak()
```

Không cần kế thừa.

---

## Cách 2 - ABC

```text-x-trilium-auto
class Animal(ABC):

    @abstractmethod
    def speak(self):
        ...
```

Dog phải:

```text-x-trilium-auto
class Dog(Animal):
```

---

## Cách 3

Protocol

Đây là thứ chúng ta học hôm nay.

---

# 2. Nominal Typing

Java sử dụng:

Nominal Typing.

Nghĩa là:

```text-x-trilium-auto
Tên class

↓

Quan trọng
```

Ví dụ

```text-x-trilium-auto
class Animal:
    pass


class Dog(Animal):
    pass
```

Dog là Animal

↓

Do kế thừa.

---

# 3. Structural Typing

Protocol dùng:

Structural Typing.

Nghĩa là:

```text-x-trilium-auto
Có cấu trúc phù hợp

↓

Được
```

Không quan tâm:

```text-x-trilium-auto
Kế thừa?
```

---

# 4. Ví dụ

```text-x-trilium-auto
class Robot:

    def speak(self):

        print("Beep")
```

Không kế thừa.

Nhưng nếu Protocol yêu cầu:

```text-x-trilium-auto
speak()
```

Robot vẫn hợp lệ.

---

# 5. Import Protocol

```text-x-trilium-auto
from typing import Protocol
```

---

# 6. Viết Protocol

```text-x-trilium-auto
from typing import Protocol


class Speaker(Protocol):

    def speak(self)->None:
        ...
```

Đây KHÔNG phải ABC.

---

# 7. Sử dụng

```text-x-trilium-auto
class Dog:

    def speak(self):

        print("Woof")
```

Không kế thừa.

Nhưng:

```text-x-trilium-auto
def make_sound(obj: Speaker):

    obj.speak()
```

Dog hợp lệ.

---

# 8. Điều kỳ diệu

Không có:

```text-x-trilium-auto
class Dog(Speaker)
```

Vẫn được.

Đây gọi là:

Structural Typing.

---

# 9. Ví dụ khác

```text-x-trilium-auto
class Cat:

    def speak(self):

        print("Meow")
```

```text-x-trilium-auto
make_sound(Cat())
```

OK.

---

# 10. IDE hoạt động thế nào?

Ví dụ

```text-x-trilium-auto
make_sound(robot)
```

Pylance

↓

Kiểm tra

```text-x-trilium-auto
Robot

↓

Có speak()

↓

OK
```

Không cần kế thừa.

---

# 11. Sai ví dụ

```text-x-trilium-auto
class Fish:

    def swim(self):
        ...
```

```text-x-trilium-auto
make_sound(Fish())
```

MyPy báo:

```text-x-trilium-auto
Fish

không có

speak()
```

Đây là:

Static Checking.

---

# 12. Protocol không tạo object

Ví dụ

```text-x-trilium-auto
class Speaker(Protocol):

    def speak(self):
        ...
```

Không nên:

```text-x-trilium-auto
Speaker()
```

Protocol chủ yếu dùng để mô tả kiểu cho type checker và IDE, không phải để tạo đối tượng hay chia sẻ logic như ABC.

---

# 13. Protocol có nhiều method

```text-x-trilium-auto
class Source(Protocol):

    def fetch(self,url):
        ...

    def parse(self,text):
        ...
```

Class:

```text-x-trilium-auto
class TruyenFull:
```

Nếu có:

```text-x-trilium-auto
fetch()

parse()
```

↓

Đạt.

---

# 14. Không cần BaseSource

ABC:

```text-x-trilium-auto
class TruyenFull(BaseSource)
```

Protocol:

```text-x-trilium-auto
class TruyenFull:
```

Không kế thừa.

Vẫn được.

---

# 15. So sánh

ABC

```text-x-trilium-auto
Inheritance

↓

Contract
```

Protocol

```text-x-trilium-auto
Structure

↓

Contract
```

---

# 16. Runtime Protocol

Có thể

```text-x-trilium-auto
from typing import runtime_checkable
```

```text-x-trilium-auto
@runtime_checkable class Speaker(Protocol):

    def speak(self):
        ...
```

Bây giờ

```text-x-trilium-auto
isinstance(dog,Speaker)
```

↓

True

Nếu `dog` có `speak()`.

Lưu ý: `isinstance()` với `Protocol` chỉ hoạt động khi có `@runtime_checkable`, và việc kiểm tra chỉ xác nhận sự tồn tại của các thành viên cần thiết, không kiểm tra đầy đủ kiểu dữ liệu của chúng.

---

# 17. Protocol + Property

```text-x-trilium-auto
class Shape(Protocol):

    @property
    def area(self)->float:
        ...
```

Class

```text-x-trilium-auto
class Rectangle:
```

Có:

```text-x-trilium-auto
@property def area(...)
```

↓

Đạt.

---

# 18. Protocol + Generic

Ví dụ

```text-x-trilium-auto
from typing import TypeVar

T=TypeVar("T")
```

```text-x-trilium-auto
class Repository(Protocol[T]):

    def save(self,obj:T):
        ...
```

Sau này:

```text-x-trilium-auto
Repository[Book]
```

```text-x-trilium-auto
Repository[Novel]
```

```text-x-trilium-auto
Repository[User]
```

Đều dùng chung.

Đây là nền tảng của Generic Repository Pattern.

---

# 19. Áp dụng vào dự án crawler

Thay vì

```text-x-trilium-auto
class BaseHttpClient(ABC)
```

Có thể

```text-x-trilium-auto
class HttpClient(Protocol):

    def get(self,url)->str:
        ...
```

Requests

```text-x-trilium-auto
class RequestsClient:
```

Aiohttp

```text-x-trilium-auto
class AioHttpClient:
```

Không cần kế thừa.

---

# 20. Service

```text-x-trilium-auto
class CrawlService:

    def __init__(

        self,

        client:HttpClient

    ):

        self.client=client
```

Bất kỳ object nào có:

```text-x-trilium-auto
get()
```

↓

Được.

---

# 21. So sánh ABC và Protocol

| ABC | Protocol |
| --- | --- |
| Có kế thừa | Không cần kế thừa |
| Có thể chia sẻ code | Chỉ mô tả giao diện (thường không có logic dùng chung) |
| Runtime | Chủ yếu phục vụ static type checking |
| Có constructor | Không dùng để khởi tạo đối tượng |
| Có state | Thường không có state |

---

# 22. Khi nào dùng gì?

## Duck Typing

Dự án nhỏ.

Không dùng Type Hint.

---

## ABC

Framework.

Plugin.

Cần:

- code chung
- ép implement
- logic mặc định

---

## Protocol

Python hiện đại.

Type Hint.

MyPy.

Pyright.

IDE.

Không cần chia sẻ implementation.

---

# 23. Sai lầm phổ biến

## Sai

Protocol thay thế ABC.

Không.

ABC và Protocol giải quyết hai vấn đề khác nhau.

---

## Sai

Protocol có nhiều logic.

Protocol nên chỉ mô tả API.

---

## Sai

Mọi thứ đều Protocol.

Không.

Nếu cần:

- code dùng chung
- state
- cache
- implementation

↓

ABC tốt hơn.

---

# 24. Kiến trúc hiện đại

Rất nhiều framework dùng:

```text-x-trilium-auto
Service

↓

Protocol

↓

Implementation
```

Ví dụ

```text-x-trilium-auto
CrawlerService

↓

HttpClient Protocol

↓

RequestsClient
```

Hoặc

```text-x-trilium-auto
↓

AioHttpClient
```

Service không cần biết implementation.

---

# 25. Thiết kế hệ thống crawler

Đây là kiến trúc mình khuyến nghị:

```text-x-trilium-auto
                 CrawlService
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
 HttpClient      Repository       Source
  Protocol         Protocol       Protocol
      │               │               │
 ┌────┴────┐     ┌────┴────┐     ┌────┴─────────┐
 │         │     │         │     │              │
Requests  Aiohttp SQLite Mongo TruyenFull  TangThuVien
```

Nếu sau này bạn đổi:

- SQLite → PostgreSQL
- Requests → aiohttp
- TruyenFull → NovelBin

`CrawlService` gần như không phải thay đổi.

---

# 26. ABC + Protocol kết hợp

Trong các framework lớn, hai kỹ thuật này thường được kết hợp:

```text-x-trilium-auto
            ABC
             │
   Chia sẻ implementation
             │
             ▼
      BaseSource

             ▲

             │ implements

         Protocol
```

Ví dụ:

- `BaseSource` (ABC) cung cấp retry, cache, helper...
- `SourceProtocol` mô tả API mà các service phụ thuộc.

Đây là cách thiết kế rất phổ biến trong các thư viện hiện đại.

---

# Tổng kết Buổi 14

```text-x-trilium-auto
                  Python Contracts

                    Duck Typing
                         │

                Runtime Behaviour

                         │

         ┌───────────────┼───────────────┐

         ▼                               ▼

        ABC                         Protocol

  Shared Logic                  Structural Typing

  Runtime Contract              Static Contract
```

---

# Điều quan trọng nhất cần nhớ

Hãy phân biệt rõ ba khái niệm:

| Kỹ thuật | Mục tiêu |
| --- | --- |
| Duck Typing | Chỉ cần đối tượng có hành vi phù hợp |
| ABC | Chia sẻ logic + ép lớp con cài đặt |
| Protocol | Mô tả giao diện cho type checker mà không cần kế thừa |

Một quy tắc thực tế:

- Cần **logic dùng chung** → ABC.
- Chỉ cần **hợp đồng kiểu (type contract)** → Protocol.
- Không cần ràng buộc, muốn linh hoạt tối đa → Duck Typing.

---

# Bài tập thực hành

## Bài 1

Tạo một `Protocol` tên `Drawable`:

```text-x-trilium-auto
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...
```

Sau đó tạo:

- `Circle`
- `Rectangle`
- `Image`

Không lớp nào kế thừa `Drawable`, nhưng tất cả đều có `draw()`.

Viết:

```text-x-trilium-auto
def render(obj: Drawable):
    obj.draw()
```

---

## Bài 2

Tạo `StorageProtocol`:

- `save(data)`
- `load(id)`

Triển khai:

- `SQLiteStorage`
- `MemoryStorage`
- `JsonStorage`

Viết `BackupService` chỉ phụ thuộc vào `StorageProtocol`.

---

## Bài 3

Thử dùng:

```text-x-trilium-auto
from typing import runtime_checkable
```

Đánh dấu `Drawable` là `@runtime_checkable`.

Kiểm tra:

```text-x-trilium-auto
isinstance(circle, Drawable)
```

và thử với một lớp không có `draw()`.

Giải thích kết quả.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế các `Protocol`:

- `SourceProtocol`
- `HttpClientProtocol`
- `RepositoryProtocol`
- `ParserProtocol`

Sau đó:

- `TruyenFullSource` triển khai `SourceProtocol`.
- `RequestsHttpClient` triển khai `HttpClientProtocol`.
- `SQLiteRepository` triển khai `RepositoryProtocol`.

Cuối cùng, xây dựng:

```text-x-trilium-auto
class CrawlService:
    def __init__(
        self,
        source: SourceProtocol,
        client: HttpClientProtocol,
        repository: RepositoryProtocol,
    ):
        ...
```

Hãy chứng minh rằng bạn có thể thay thế bất kỳ implementation nào mà **không cần sửa** `CrawlService`.

---

# Chuẩn bị cho Buổi 15

Từ buổi sau, chúng ta sẽ bước vào **trái tim của OOP trong Python**:

# Descriptor Protocol

Đây là cơ chế nền tảng đứng sau rất nhiều tính năng của Python:

- `@property`
- Method
- Function
- `staticmethod`
- `classmethod`
- `cached_property`
- ORM (SQLAlchemy, Django ORM)
- Pydantic
- Dataclasses
- Slots

Sau khi hiểu Descriptor, bạn sẽ thấy rằng nhiều tính năng tưởng như "phép màu" của Python thực chất đều được xây dựng trên cùng một cơ chế cốt lõi. Đây là một trong những chủ đề chuyên sâu và giá trị nhất của Python.