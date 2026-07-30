# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 5 - Generic Repository Deep Dive (Professional)

> Đây là kỹ thuật được sử dụng trong rất nhiều framework và dự án lớn. Sau buổi này bạn sẽ hiểu vì sao chỉ cần viết CRUD **một lần** nhưng có thể dùng cho hàng chục Entity khác nhau.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Generic Repository là gì 
  * Generic trong Python (`TypeVar`, `Generic`) 
  * BaseRepository 
  * CRUD dùng Generic 
  * Reuse code 
  * Override phương thức 
  * Generic + ABC 
  * Generic + Repository Pattern 
  * Khi nào KHÔNG nên dùng Generic Repository 



* * *

# 1\. Vấn đề khi không dùng Generic Repository

Giả sử ta có:
    
    
    StoryRepository
    
    ChapterRepository
    
    AuthorRepository
    
    GenreRepository
    
    BookmarkRepository
    
    HistoryRepository

Mỗi Repository đều có:
    
    
    save()
    
    delete()
    
    get_by_id()
    
    exists()
    
    list()

Nếu mỗi Repository tự viết:
    
    
    class StoryRepository:
    
        def get_by_id(...):
            ...
    
        def save(...):
            ...
    
        ...

Rồi
    
    
    class AuthorRepository:
    
        def get_by_id(...):
            ...
    
        def save(...):
            ...

Lặp lại hàng chục lần.

Đây gọi là

> Duplicate Code.

* * *

# 2\. Ý tưởng của Generic Repository

Ta nhận ra:

CRUD của Story

và

CRUD của Author

gần như giống nhau.

Khác mỗi
    
    
    Story
    
    ↓
    
    Author

Ta muốn
    
    
    BaseRepository<T>

* * *

# 3\. Generic là gì?

Python có
    
    
    from typing import TypeVar
    
    T = TypeVar("T")

Nghĩa là
    
    
    T
    
    ↓
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Author
    
    ↓
    
    Genre

T có thể là bất kỳ Entity nào.

* * *

# 4\. Generic Repository
    
    
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class BaseRepository(Generic[T]):
        ...

Bây giờ
    
    
    BaseRepository
    
    ↓
    
    Repository của mọi Entity

* * *

# 5\. Kết hợp với ABC

Ta không muốn ai tạo trực tiếp
    
    
    BaseRepository()

Nên
    
    
    from abc import ABC
    from abc import abstractmethod
    from typing import Generic
    from typing import TypeVar
    
    T = TypeVar("T")
    
    
    class BaseRepository(
        ABC,
        Generic[T]
    ):
        ...

* * *

# 6\. CRUD chuẩn
    
    
    class BaseRepository(
        ABC,
        Generic[T]
    ):
    
        @abstractmethod
        def get_by_id(
            self,
            id_: int
        ) -> T | None:
            ...
    
        @abstractmethod
        def save(
            self,
            entity: T
        ) -> None:
            ...
    
        @abstractmethod
        def delete(
            self,
            id_: int
        ) -> None:
            ...
    
        @abstractmethod
        def list(
            self
        ) -> list[T]:
            ...

Chỉ viết một lần.

* * *

# 7\. StoryRepository

Bây giờ
    
    
    class StoryRepository(
        BaseRepository[Story]
    ):
        ...

Tự động có kiểu
    
    
    get_by_id()
    
    ↓
    
    Story

* * *

# 8\. AuthorRepository
    
    
    class AuthorRepository(
        BaseRepository[Author]
    ):
        ...

Bây giờ
    
    
    repository.get_by_id(1)

IDE biết chắc chắn

↓

Author

* * *

# 9\. ChapterRepository
    
    
    class ChapterRepository(
        BaseRepository[Chapter]
    ):
        ...

Kiểu trả về

↓

Chapter

Không cần ép kiểu.

* * *

# 10\. Generic giúp IDE mạnh hơn

Ví dụ
    
    
    story = story_repository.get_by_id(10)

IDE biết
    
    
    Story

Nên sẽ gợi ý
    
    
    story.title
    
    story.slug
    
    story.summary

Nếu không dùng Generic

IDE chỉ biết
    
    
    object

* * *

# 11\. Generic không có nghĩa mọi Repository giống hệt nhau

Ví dụ

Story có
    
    
    find_by_slug()

Author thì không.

Ta thêm
    
    
    class StoryRepository(
        BaseRepository[Story]
    ):
    
        @abstractmethod
        def find_by_slug(
            self,
            slug: str
        ) -> Story | None:
            ...

Repository vẫn kế thừa CRUD.

* * *

# 12\. ChapterRepository đặc biệt hơn

Crawler thường cần
    
    
    find_latest()
    
    find_by_index()
    
    bulk_save()
    
    find_missing()
    
    find_by_story()

Do đó
    
    
    class ChapterRepository(
        BaseRepository[Chapter]
    ):

vẫn thêm được
    
    
    @abstractmethod
    def bulk_save(...):
        ...

* * *

# 13\. Quan hệ kế thừa
    
    
                    BaseRepository<T>
                         ▲
         ┌───────────────┼───────────────┐
         │               │               │
    StoryRepository ChapterRepository AuthorRepository

Đây là kiến trúc phổ biến trong Java, C#, Python.

* * *

# 14\. BaseRepository chỉ chứa CRUD chung

Nó không nên có
    
    
    find_by_slug()

Vì

Genre

không có slug.

Không nên có
    
    
    find_latest_chapter()

Author cũng không có.

Nguyên tắc:

BaseRepository chỉ chứa những hành vi **mọi Entity đều có**.

* * *

# 15\. Một sai lầm phổ biến

Nhiều người viết
    
    
    class BaseRepository:
    
        def search(...):
    
        def crawl(...):
    
        def download(...):

Sai.

Repository không crawl.

Repository không download.

Repository chỉ làm việc với lưu trữ dữ liệu.

* * *

# 16\. Generic Repository + Mapper

Repository nhận
    
    
    Story

↓

Mapper

↓

SQLite Row

Ngược lại

SQLite Row

↓

Mapper

↓

Story

Repository là nơi chịu trách nhiệm chuyển đổi.

* * *

# 17\. Thêm Protocol (nâng cao)

Để Generic an toàn hơn, ta có thể ràng buộc `T` phải có `id`.
    
    
    from typing import Protocol
    
    
    class Entity(Protocol):
    
        id: int | None

Sau đó
    
    
    T = TypeVar(
        "T",
        bound=Entity
    )

Bây giờ

Generic chỉ chấp nhận Entity.

* * *

# 18\. Tại sao dùng Protocol?

Nếu ai đó viết
    
    
    class Dog:
    
        name: str

Rồi
    
    
    BaseRepository[Dog]

IDE sẽ cảnh báo.

Dog không có
    
    
    id

Không phải Entity.

Đây là một lợi ích lớn của type checking hiện đại trong Python.

* * *

# 19\. Cấu trúc Repository
    
    
    domain/
    
        repositories/
    
            base_repository.py
    
            story_repository.py
    
            chapter_repository.py
    
            author_repository.py
    
            genre_repository.py

Implementation
    
    
    infrastructure/
    
        sqlite/
    
            story_repository.py
    
            chapter_repository.py
    
            author_repository.py

* * *

# 20\. Quan hệ tổng thể
    
    
                 BaseRepository<T>
                         ▲
         ┌───────────────┼────────────────┐
         │               │                │
    StoryRepo      ChapterRepo      AuthorRepo
         │               │                │
         └───────────────┼────────────────┘
                         │
                 SQLiteRepository
                         │
                     SQLite DB

* * *

# 21\. Khi nào KHÔNG nên dùng Generic Repository?

Không phải lúc nào Generic Repository cũng là lựa chọn tốt.

Ví dụ:
    
    
    find_hot_story()
    
    find_story_rank()
    
    recommend_story()
    
    find_similar_story()

Đây là các nghiệp vụ riêng.

Không nên nhét vào
    
    
    BaseRepository

Hoặc
    
    
    search_by_keyword()
    
    search_by_genre()
    
    search_by_author()
    
    search_full_text()

Đây là **Query chuyên biệt**.

Nên để trong
    
    
    StoryRepository

* * *

# 22\. Một thiết kế chuyên nghiệp hơn

Các dự án lớn thường tách:
    
    
    BaseRepository
    
    ↓
    
    CRUD

và
    
    
    StoryQueryRepository
    
    ↓
    
    Search
    
    Ranking
    
    Recommendation
    
    Analytics

Tách đọc và ghi giúp mã nguồn rõ ràng hơn. Sau này chúng ta sẽ học mô hình này khi tìm hiểu CQRS.

* * *

# 23\. Luồng hoạt động
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository
     │
     ▼
    BaseRepository
     │
     ▼
    SQLite Repository
     │
     ▼
    SQLite

`StoryService` không bao giờ biết `BaseRepository` lưu dữ liệu như thế nào.

* * *

# 24\. Sai lầm lớn nhất

Nhiều người cố gắng Generic hóa **mọi thứ**.

Ví dụ:
    
    
    BaseRepository.search()

Rồi dùng cho

  * Story 
  * Chapter 
  * Author 
  * Genre 



Kết quả là:

  * rất nhiều `if entity == Story`
  * rất nhiều `match`
  * BaseRepository ngày càng phình to 



Đây gọi là **God Object**.

Nguyên tắc:

> Generic Repository chỉ dùng cho phần **giống nhau** , không dùng cho toàn bộ nghiệp vụ.

* * *

# Kiến trúc sau 5 buổi
    
    
    app/
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── enums/
    │   ├── repositories/
    │   │   ├── base_repository.py
    │   │   ├── story_repository.py
    │   │   ├── chapter_repository.py
    │   │   ├── author_repository.py
    │   │   └── genre_repository.py
    │   └── services/
    │
    ├── infrastructure/
    │   ├── sqlite/
    │   ├── memory/
    │   └── plugins/
    │
    └── ui/

* * *

# Bài tập

## Bài 1

Thiết kế `BaseRepository[T]` với các phương thức:

  * `get_by_id()`
  * `save()`
  * `delete()`
  * `exists()`
  * `list()`
  * `count()`



Sử dụng `ABC`, `Generic` và `TypeVar`.

* * *

## Bài 2

Cho `StoryRepository` kế thừa `BaseRepository[Story]` và bổ sung:

  * `find_by_slug()`
  * `find_by_source()`
  * `find_updated_after()`



Giải thích vì sao các phương thức này **không nên** nằm trong `BaseRepository`.

* * *

## Bài 3

Viết `MemoryBaseRepository[T]` lưu dữ liệu bằng `dict[int, T]`, sau đó xây dựng:

  * `MemoryStoryRepository`
  * `MemoryAuthorRepository`



chỉ bằng cách kế thừa lớp cơ sở.

* * *

## Bài 4 (nâng cao)

Thiết kế một `Entity` `Protocol` với thuộc tính `id`, sau đó khai báo:
    
    
    T = TypeVar("T", bound=Entity)

Phân tích lợi ích của cách làm này đối với:

  * IDE (gợi ý kiểu) 
  * `mypy` / `pyright`
  * khả năng ngăn chặn lỗi ngay từ khi phát triển. 



* * *

# Chuẩn bị cho Buổi 6

Buổi tiếp theo chúng ta sẽ học **Data Mapper Pattern** và **Repository Implementation**. Đây là bước biến các `sqlite3.Row` thành `Story`, `Chapter`, `Author` và ngược lại một cách tự động, giúp Repository sạch sẽ và hoàn toàn tách biệt giữa Domain Model với cấu trúc của cơ sở dữ liệu. Đây cũng là nền tảng để sau này chuyển sang SQLAlchemy hoặc các ORM khác mà không ảnh hưởng đến tầng nghiệp vụ.

