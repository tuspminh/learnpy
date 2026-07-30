# OOP Deep Dive - Buổi 13

# Abstract Base Class (ABC) và `abc` Module – Thiết kế Framework Chuyên Nghiệp

Đến đây, bạn đã học:

- Class
- Object
- Encapsulation
- Property
- Inheritance
- Multiple Inheritance
- Mixins
- Composition
- Polymorphism
- Duck Typing

Hôm nay chúng ta sẽ học một công cụ cực kỳ quan trọng trong Python:

# Abstract Base Class (ABC)

Đây là nền tảng của rất nhiều thư viện lớn:

- Django
- SQLAlchemy
- asyncio
- pathlib
- collections.abc
- io
- concurrent.futures

Đồng thời cũng là cách rất phù hợp để thiết kế **plugin architecture** cho dự án crawler truyện của bạn.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Abstract Class
- Abstract Method
- `abc` module
- `ABC`
- `@abstractmethod`
- Interface trong Python
- Khi nào dùng ABC
- Thiết kế framework bằng ABC

---

# 1. Tại sao cần ABC?

Giả sử bạn có:

```text-x-trilium-auto
class TruyenFullSource:

    def fetch(self):
        ...

    def parse(self):
        ...
```

Sau đó có:

```text-x-trilium-auto
class BachNgocSachSource:

    def fetch(self):
        ...
```

Oops...

Quên viết:

```text-x-trilium-auto
parse()
```

Python chỉ phát hiện khi:

```text-x-trilium-auto
crawl(source)
```

gọi:

```text-x-trilium-auto
source.parse()
```

và chương trình lỗi.

---

# 2. Duck Typing có nhược điểm

Duck Typing:

```text-x-trilium-auto
Có method

↓

Được
```

Không có

↓

Runtime Error

Ví dụ

```text-x-trilium-auto
AttributeError
```

ABC giúp phát hiện sớm hơn.

---

# 3. Abstract Class là gì?

Abstract Class:

Là class:

- không dùng trực tiếp
- chỉ làm khuôn mẫu (template)
- ép class con phải cài đặt các method bắt buộc

Ví dụ

```text-x-trilium-auto
BaseSource

↓

TruyenFull

↓

TangThuVien

↓

BachNgocSach
```

---

# 4. Module `abc`

Python có sẵn:

```text-x-trilium-auto
from abc import ABC
```

và

```text-x-trilium-auto
from abc import abstractmethod
```

---

# 5. Viết Abstract Class

Ví dụ

```text-x-trilium-auto
from abc import ABC, abstractmethod


class Animal(ABC):

    @abstractmethod
    def speak(self):
        pass
```

Đây là Abstract Class.

---

# 6. Không thể tạo object

Thử:

```text-x-trilium-auto
a = Animal()
```

Kết quả

```text-x-trilium-auto
TypeError

Can't instantiate abstract class
```

Đúng.

Animal chỉ là khuôn.

---

# 7. Class con

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):

        print("Woof")
```

Bây giờ:

```text-x-trilium-auto
Dog()
```

OK.

---

# 8. Nếu quên implement?

Ví dụ

```text-x-trilium-auto
class Cat(Animal):
    pass
```

Thử:

```text-x-trilium-auto
Cat()
```

Kết quả

```text-x-trilium-auto
TypeError
```

Python báo lỗi ngay khi bạn cố tạo đối tượng, vì `Cat` vẫn còn là lớp trừu tượng.

---

# 9. Abstract Method

```text-x-trilium-auto
@abstractmethod def speak(self):
```

Nghĩa là:

Class con **bắt buộc**

phải override.

---

# 10. Abstract Method có code

Nhiều người nghĩ:

Abstract Method

↓

Không có code

Sai.

Ví dụ

```text-x-trilium-auto
class Animal(ABC):

    @abstractmethod
    def speak(self):

        print("Default")
```

Class con:

```text-x-trilium-auto
class Dog(Animal):

    def speak(self):

        super().speak()

        print("Woof")
```

Hoàn toàn hợp lệ.

---

# 11. Nhiều Abstract Method

```text-x-trilium-auto
class BaseSource(ABC):

    @abstractmethod
    def fetch(self):
        ...

    @abstractmethod
    def parse(self):
        ...
```

Class con

```text-x-trilium-auto
class TruyenFull(BaseSource):
```

bắt buộc có:

- fetch
- parse

---

# 12. Abstract Property

Có thể:

```text-x-trilium-auto
from abc import ABC, abstractmethod


class Shape(ABC):

    @property
    @abstractmethod
    def area(self):
        ...
```

Class con:

```text-x-trilium-auto
class Rectangle(Shape):

    @property
    def area(self):
        return 100
```

---

# 13. Abstract Class vẫn kế thừa được

Ví dụ

```text-x-trilium-auto
class Base(ABC):
    ...
```

↓

```text-x-trilium-auto
class Source(Base):
```

↓

```text-x-trilium-auto
class TruyenFull(Source):
```

Không vấn đề.

---

# 14. ABC + Polymorphism

```text-x-trilium-auto
class BaseSource(ABC):

    @abstractmethod
    def fetch(self):
        ...
```

Crawler

```text-x-trilium-auto
def crawl(source):

    source.fetch()
```

Truyền:

```text-x-trilium-auto
TruyenFull()
```

Hay

```text-x-trilium-auto
TangThuVien()
```

Đều được.

Đây là:

ABC + Polymorphism

---

# 15. ABC + Plugin

Plugin chuẩn:

```text-x-trilium-auto
BaseSource

↓

Source1

↓

Source2

↓

Source3
```

Crawler chỉ biết:

```text-x-trilium-auto
fetch()

parse()
```

Không cần biết plugin nào.

---

# 16. Ví dụ Parser

```text-x-trilium-auto
class Parser(ABC):

    @abstractmethod
    def parse(self,text):
        ...
```

---

```text-x-trilium-auto
class HtmlParser(Parser):

    def parse(self,text):

        ...
```

---

```text-x-trilium-auto
class JsonParser(Parser):

    def parse(self,text):

        ...
```

Loader:

```text-x-trilium-auto
parser.parse(data)
```

---

# 17. Repository

```text-x-trilium-auto
class Repository(ABC):

    @abstractmethod
    def save(self,obj):
        ...

    @abstractmethod
    def get(self,id):
        ...
```

---

SQLite

```text-x-trilium-auto
class SQLiteRepository(Repository):
```

Mongo

```text-x-trilium-auto
class MongoRepository(Repository):
```

Service không cần sửa.

---

# 18. HTTP Client

```text-x-trilium-auto
class HttpClient(ABC):

    @abstractmethod
    def get(self,url):
        ...
```

---

```text-x-trilium-auto
class RequestsClient(HttpClient):
```

---

```text-x-trilium-auto
class AioHttpClient(HttpClient):
```

Đổi client

↓

Không đổi service.

---

# 19. Sai lầm phổ biến

## Sai

Mọi class đều ABC.

Không cần.

ABC chỉ dùng khi:

- Có nhiều implementation.
- Có API chung cần bắt buộc.

---

## Sai

ABC chứa quá nhiều logic.

ABC nên:

- định nghĩa contract.
- cung cấp logic dùng chung khi hợp lý.

---

## Sai

Không dùng Duck Typing nữa.

ABC

KHÔNG thay thế

Duck Typing.

Chúng bổ sung cho nhau.

---

# 20. ABC vs Duck Typing

Duck Typing

```text-x-trilium-auto
Có method

↓

OK
```

ABC

```text-x-trilium-auto
Bắt buộc implement

↓

OK
```

Duck Typing

↓

Linh hoạt.

ABC

↓

An toàn hơn.

---

# 21. ABC trong thư viện chuẩn

Ví dụ

```text-x-trilium-auto
from collections.abc import Iterable
```

Kiểm tra

```text-x-trilium-auto
isinstance([], Iterable)
```

↓

True

---

Hay

```text-x-trilium-auto
Mapping
```

```text-x-trilium-auto
Sequence
```

```text-x-trilium-auto
MutableSequence
```

Đều là ABC.

---

# 22. Thiết kế BaseSource cho dự án

Đây là thiết kế mình khuyến nghị.

```text-x-trilium-auto
from abc import ABC, abstractmethod


class BaseSource(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Tên nguồn truyện"""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, url: str) -> str:
        """Tải HTML"""
        raise NotImplementedError

    @abstractmethod
    def parse(self, html: str):
        """Phân tích HTML"""
        raise NotImplementedError
```

Plugin

```text-x-trilium-auto
class TruyenFullSource(BaseSource):

    @property
    def name(self):

        return "truyenfull"

    def fetch(self,url):

        ...

    def parse(self,html):

        ...
```

Sau này thêm:

- Metruyen
- Tangthuvien
- Wikidich
- NovelBin

không cần sửa framework.

---

# 23. Kết hợp với Mixins

```text-x-trilium-auto
class RetryMixin:
    ...
```

```text-x-trilium-auto
class CacheMixin:
    ...
```

```text-x-trilium-auto
class TruyenFull(

    RetryMixin,

    CacheMixin,

    BaseSource
):
    ...
```

MRO vẫn hoạt động bình thường.

---

# 24. So sánh

| Duck Typing | ABC |
| --- | --- |
| Linh hoạt | Có ràng buộc |
| Không cần kế thừa | Thường kế thừa `ABC` |
| Lỗi ở runtime | Phát hiện thiếu phương thức sớm hơn |
| Pythonic | Pythonic khi cần contract rõ ràng |

---

# 25. Tổng kết

```text-x-trilium-auto
                 Abstract Base Class

                        │

        ┌───────────────┼───────────────┐

        │               │               │

   Contract       Polymorphism     Framework

        │

        ▼

  Plugin Architecture
```

---

# Điều quan trọng cần nhớ

ABC **không phải** để thay thế kế thừa hay Duck Typing.

ABC giúp định nghĩa một **contract** (hợp đồng):

> "Nếu muốn trở thành một `BaseSource`, bạn phải có các phương thức này."

Đây chính là nền tảng để xây dựng:

- Plugin system
- ORM
- Web Framework
- GUI Framework
- Driver
- Adapter

---

# Bài tập thực hành

## Bài 1

Tạo:

```text-x-trilium-auto
class Animal(ABC)
```

Có:

- `speak()`
- `move()`

đều là abstract.

Tạo:

- `Dog`
- `Cat`

override đầy đủ.

Thử tạo:

```text-x-trilium-auto
Animal()
```

và

```text-x-trilium-auto
class Bird(Animal):
    pass
```

Quan sát lỗi.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
class Database(ABC)
```

Có:

- `connect()`
- `execute()`
- `close()`

Sau đó tạo:

- `SQLiteDatabase`
- `MongoDatabase`

Viết một hàm:

```text-x-trilium-auto
def run_query(db: Database):
    ...
```

Chỉ làm việc với giao diện chung của `Database`.

---

## Bài 3

Thiết kế:

```text-x-trilium-auto
class Storage(ABC)
```

Có:

- `save()`
- `load()`

Triển khai:

- `FileStorage`
- `MemoryStorage`

Viết `BackupService` chỉ phụ thuộc vào `Storage`, không phụ thuộc vào lớp cụ thể.

---

## Bài 4 (Áp dụng vào dự án crawler)

Thiết kế các ABC sau:

- `BaseSource`
- `BaseParser`
- `BaseRepository`
- `BaseHttpClient`

Mỗi ABC chỉ định nghĩa contract cần thiết.

Sau đó triển khai:

- `TruyenFullSource`
- `SQLiteRepository`
- `RequestsHttpClient`

Cuối cùng, xây dựng:

```text-x-trilium-auto
class CrawlService:
    def __init__(
        self,
        source: BaseSource,
        repository: BaseRepository,
        http_client: BaseHttpClient,
    ):
        ...
```

Hãy để `CrawlService` chỉ làm việc với **ABC**, không biết lớp cụ thể là gì.

---

# Chuẩn bị cho Buổi 14

Ở buổi tiếp theo, chúng ta sẽ học một chủ đề hiện đại hơn ABC:

# Protocol (PEP 544) và Structural Typing

Đây là nền tảng của:

- Type Hint hiện đại.
- `typing.Protocol`.
- Static Duck Typing.
- MyPy, Pyright.
- Thiết kế API chuyên nghiệp trong Python 3.12+.

Sau buổi đó, bạn sẽ hiểu rõ sự khác biệt giữa:

- Duck Typing
- Abstract Base Class (ABC)
- Protocol

và biết khi nào nên dùng từng kỹ thuật trong các dự án Python lớn.