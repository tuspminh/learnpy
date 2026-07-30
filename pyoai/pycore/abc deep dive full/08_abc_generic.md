# ABC Deep Dive - Buổi 8

# ABC + Generic + TypeVar + typing

Đến buổi này, chúng ta bước sang một chủ đề rất quan trọng trong Python hiện đại:

> **Kết hợp ABC với Generic để xây dựng framework type-safe.**

Nếu chỉ dùng ABC:
    
    
    class Repository(ABC):
    
        @abstractmethod
        def get(self, id):
            ...

Python không biết:

  * `get()` trả về `User`? 
  * `Story`? 
  * `Chapter`? 
  * `Book`? 



Generic giúp giải quyết vấn đề đó.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Generic là gì 
  * TypeVar 
  * Generic[T] 
  * ABC + Generic 
  * Generic Repository 
  * Generic Service 
  * Generic Parser 
  * Generic Plugin 
  * Covariant 
  * Contravariant 
  * Bounded TypeVar 



Đây là nền tảng của các framework hiện đại như:

  * SQLAlchemy 2.x 
  * Pydantic 
  * FastAPI 
  * Django stubs 
  * LangChain 
  * nhiều thư viện Python khác 



* * *

# 1\. Vấn đề khi không dùng Generic

Ví dụ
    
    
    from abc import ABC, abstractmethod
    
    
    class Repository(ABC):
    
        @abstractmethod
        def get(self, id):
            pass

Lớp con
    
    
    class UserRepository(Repository):
    
        def get(self, id):
            return User()

và
    
    
    class StoryRepository(Repository):
    
        def get(self, id):
            return Story()

Framework không biết kiểu dữ liệu trả về.

IDE cũng không thể gợi ý chính xác.

* * *

# 2\. TypeVar

Ta khai báo:
    
    
    from typing import TypeVar
    
    T = TypeVar("T")

Có thể hiểu:
    
    
    T
    
    ↓
    
    Một kiểu dữ liệu bất kỳ

Ví dụ:
    
    
    T
    
    ↓
    
    User

hoặc
    
    
    T
    
    ↓
    
    Story

hoặc
    
    
    T
    
    ↓
    
    Chapter

* * *

# 3\. Generic
    
    
    from typing import Generic
    
    class Box(Generic[T]):
        ...

Bây giờ
    
    
    Box[int]

là
    
    
    Box chứa int

Còn
    
    
    Box[str]

là
    
    
    Box chứa string

* * *

# 4\. Ví dụ đơn giản
    
    
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Box(Generic[T]):
    
        def __init__(self, value: T):
    
            self.value = value

Sử dụng
    
    
    box = Box[int](100)
    
    print(box.value)

IDE hiểu:
    
    
    value : int

* * *

# 5\. Kết hợp ABC

Đây mới là phần quan trọng.
    
    
    from abc import ABC
    from abc import abstractmethod
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Repository(ABC, Generic[T]):
    
        @abstractmethod
        def get(self, id: int) -> T:
            ...

* * *

# 6\. Repository cho User
    
    
    class User:
        pass
    
    
    class UserRepository(Repository[User]):
    
        def get(self, id: int) -> User:
    
            return User()

IDE biết ngay:
    
    
    repo = UserRepository()
    
    user = repo.get(1)

user có kiểu:
    
    
    User

* * *

# 7\. Repository cho Story
    
    
    class Story:
        pass
    
    
    class StoryRepository(Repository[Story]):
    
        def get(self, id):
    
            return Story()

Framework vẫn dùng chung:
    
    
    Repository

nhưng mỗi lớp con trả về kiểu riêng.

* * *

# 8\. Generic CRUD

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class CRUDRepository(ABC, Generic[T]):
    
        @abstractmethod
        def create(self, obj: T):
            ...
    
        @abstractmethod
        def update(self, obj: T):
            ...
    
        @abstractmethod
        def delete(self, obj: T):
            ...
    
        @abstractmethod
        def get(self, id: int) -> T:
            ...

Đây là mẫu thiết kế rất phổ biến.

* * *

# 9\. Áp dụng vào SQLite

Ví dụ
    
    
    class Story:
        pass
    
    
    class StoryRepository(CRUDRepository[Story]):
    
        ...

Tiếp theo
    
    
    class Chapter:
        pass
    
    
    class ChapterRepository(CRUDRepository[Chapter]):
    
        ...

Không cần viết lại Interface.

* * *

# 10\. Generic Parser

Đây là ví dụ rất gần với dự án crawler.
    
    
    T = TypeVar("T")
    
    
    class Parser(ABC, Generic[T]):
    
        @abstractmethod
        def parse(self, html: str) -> T:
            ...

* * *

Parser cho Story
    
    
    class StoryParser(Parser[Story]):
    
        def parse(self, html):
    
            return Story()

* * *

Parser cho Chapter
    
    
    class ChapterParser(Parser[Chapter]):
    
        def parse(self, html):
    
            return Chapter()

* * *

# 11\. Generic Downloader
    
    
    T = TypeVar("T")
    
    
    class Downloader(ABC, Generic[T]):
    
        @abstractmethod
        def download(self, url: str) -> T:
            ...

* * *
    
    
    class ImageDownloader(Downloader[bytes]):
    
        ...

* * *
    
    
    class JsonDownloader(Downloader[dict]):
    
        ...

* * *

# 12\. Generic Plugin

Ví dụ
    
    
    T = TypeVar("T")
    
    
    class SourcePlugin(ABC, Generic[T]):
    
        @abstractmethod
        def search(self, keyword: str) -> list[T]:
            ...

Plugin
    
    
    class TruyenFullPlugin(SourcePlugin[Story]):
    
        ...

Framework biết:
    
    
    search()
    
    ↓
    
    list[Story]

* * *

# 13\. Bounded TypeVar

Ta có
    
    
    T = TypeVar("T", bound=Animal)

Có nghĩa

T chỉ được phép là:
    
    
    Animal
    
    Dog
    
    Cat
    
    Bird

Không được:
    
    
    int
    
    str
    
    list

Ví dụ:
    
    
    from abc import ABC
    
    class Animal(ABC):
        pass
    
    
    T = TypeVar("T", bound=Animal)

Đây là kỹ thuật thường dùng để giới hạn Generic cho một họ lớp nhất định.

* * *

# 14\. Covariant

Ví dụ
    
    
    T = TypeVar(
        "T",
        covariant=True
    )

Ý nghĩa:

Nếu:
    
    
    Dog
    
    ↓
    
    Animal

thì
    
    
    Repository[Dog]
    
    ↓
    
    Repository[Animal]

cũng được xem là hợp lệ trong các ngữ cảnh chỉ đọc (read-only).

* * *

# 15\. Contravariant
    
    
    T = TypeVar(
        "T",
        contravariant=True
    )

Đây là chiều ngược lại.

Nó xuất hiện trong:

  * Event Handler 
  * Callback 
  * Message Bus 



Ví dụ trực quan sẽ được học sâu hơn trong khóa **Typing Deep Dive** , vì variance là một chủ đề riêng khá lớn.

* * *

# 16\. Thiết kế Repository hoàn chỉnh
    
    
    from abc import ABC
    from abc import abstractmethod
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class Repository(
        ABC,
        Generic[T]
    ):
    
        @abstractmethod
        def get(self, id: int) -> T:
            ...
    
        @abstractmethod
        def all(self) -> list[T]:
            ...
    
        @abstractmethod
        def save(self, obj: T):
            ...
    
        @abstractmethod
        def delete(self, obj: T):
            ...

Đây là interface có thể tái sử dụng cho rất nhiều loại dữ liệu.

* * *

# 17\. Áp dụng vào dự án crawler

Một thiết kế rất phù hợp:
    
    
    Parser[T]
    │
    ├── StoryParser
    ├── ChapterParser
    ├── AuthorParser
    └── CategoryParser

* * *
    
    
    Repository[T]
    │
    ├── StoryRepository
    ├── ChapterRepository
    ├── AuthorRepository
    └── CategoryRepository

* * *
    
    
    Downloader[T]
    │
    ├── HtmlDownloader
    ├── JsonDownloader
    ├── ImageDownloader
    └── AudioDownloader

Mỗi interface chỉ cần viết một lần.

* * *

# 18\. Lợi ích

Không dùng Generic:
    
    
    repo.get()

IDE:
    
    
    Unknown

* * *

Dùng Generic:
    
    
    repo.get()

IDE:
    
    
    Story

Lợi ích:

  * Tự động gợi ý thuộc tính/phương thức. 
  * Kiểm tra kiểu tốt hơn bằng `mypy`, `pyright`,... 
  * API rõ ràng hơn. 
  * Giảm lỗi khi refactor. 



* * *

# 19\. Lưu ý về runtime

Generic trong `typing` chủ yếu phục vụ **type checker** và IDE.

Ví dụ:
    
    
    box = Box[int](10)

Ở runtime, Python **không** tạo ra một lớp `Box[int]` hoàn toàn mới như C++ template.

Do đó, Generic giúp tăng độ an toàn khi phát triển, nhưng không thay thế hoàn toàn việc kiểm tra dữ liệu ở runtime nếu ứng dụng của bạn cần điều đó.

* * *

# Tổng kết

Trong buổi này bạn đã học:

  * `TypeVar`
  * `Generic`
  * `ABC + Generic`
  * Generic Repository 
  * Generic Parser 
  * Generic Plugin 
  * Bounded TypeVar 
  * Covariant 
  * Contravariant 
  * Thiết kế framework type-safe 



* * *

# Bài tập

## Bài 1

Viết:
    
    
    class Cache(ABC, Generic[T])

Có:
    
    
    get()
    
    set()
    
    delete()

* * *

## Bài 2

Viết:
    
    
    class Serializer(ABC, Generic[T])

Có:
    
    
    serialize()
    
    deserialize()

* * *

## Bài 3

Viết:
    
    
    class Storage(ABC, Generic[T])

Có:
    
    
    save()
    
    load()

* * *

## Bài 4 (Áp dụng dự án crawler)

Thiết kế các interface Generic sau:
    
    
    Repository[T]
    
    Parser[T]
    
    Downloader[T]
    
    Exporter[T]
    
    Importer[T]
    
    Cache[T]

Sau đó tạo các lớp cụ thể như:

  * `StoryRepository(Repository[Story])`
  * `ChapterRepository(Repository[Chapter])`
  * `StoryParser(Parser[Story])`
  * `ImageDownloader(Downloader[bytes])`



Đảm bảo mọi phương thức đều có type hint đầy đủ để IDE có thể suy luận kiểu chính xác.

* * *

# Buổi 9 (một trong những buổi khó nhất)

Ở **Buổi 9** , chúng ta sẽ học:

> **ABC + Multiple Inheritance + MRO (Method Resolution Order)**

Bạn sẽ hiểu:

  * Vì sao `ABC` có thể kết hợp với nhiều lớp cha. 
  * Cách `super()` hoạt động trong cây kế thừa hình kim cương (Diamond Inheritance). 
  * Vai trò của MRO trong việc gọi phương thức. 
  * Những lỗi thường gặp khi kết hợp nhiều ABC. 
  * Cách thiết kế mixin và abstract class để tránh xung đột. 



Đây là kiến thức rất quan trọng khi xây dựng framework lớn hoặc hệ thống plugin phức tạp.

