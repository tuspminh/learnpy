# Buổi 1

# Thiết kế Domain Model

Đây là phần quan trọng nhất.

Sai từ đây thì sau này code sẽ cực kỳ khó sửa.

* * *

# Bước 1

Không nghĩ Database trước.

Nghĩ về "đối tượng trong thế giới thật".

Ví dụ:

Website TruyenFull có:
    
    
    Truyện
    
    ↓
    
    Chương
    
    ↓
    
    Tác giả
    
    ↓
    
    Thể loại
    
    ↓
    
    Nguồn

Vậy ta có Entity:
    
    
    Story
    
    Chapter
    
    Author
    
    Genre
    
    Source

* * *

# Entity là gì?

Entity là đối tượng có định danh (ID).

Ví dụ
    
    
    Story
    
    id = 100

Tên truyện có thể đổi.
    
    
    Đấu La Đại Lục
    
    ↓
    
    Đấu La Đại Lục Full

Nhưng id vẫn là
    
    
    100

=> vẫn là cùng một Story.

* * *

# Entity đầu tiên

Story
    
    
    Story
    
    id
    
    title
    
    slug
    
    summary
    
    status
    
    cover
    
    created_at
    
    updated_at

Python
    
    
    from dataclasses import dataclass
    from datetime import datetime
    
    
    @dataclass
    class Story:
        id: int | None
        title: str
        slug: str
        summary: str
        status: str
        cover: str
        created_at: datetime
        updated_at: datetime

Đây là **Domain Model** , không phải model của ORM.

* * *

# Chapter
    
    
    Chapter
    
    id
    
    story_id
    
    index
    
    title
    
    url
    
    content
    
    created_at

Python
    
    
    @dataclass
    class Chapter:
        id: int | None
        story_id: int
        index: int
        title: str
        url: str
        content: str

* * *

# Author
    
    
    @dataclass
    class Author:
        id: int |None
        name: str

Rất đơn giản.

* * *

# Genre
    
    
    @dataclass
    class Genre:
        id: int |None
        name: str

* * *

# Source

Nguồn truyện.

Ví dụ
    
    
    TruyenFull
    
    TangThuVien
    
    NovelBin

Model
    
    
    @dataclass
    class Source:
        id: int | None
        name: str
        domain: str

* * *

# Quan hệ giữa các Entity
    
    
    Source
       │
       │
    Story
       │
       ├──────────────┐
       │              │
    Chapter        StoryGenre
                      │
                   Genre
    
    Story
       │
    StoryAuthor
       │
    Author

Không nên lưu trực tiếp tên tác giả hoặc thể loại trong bảng `story`. Thay vào đó dùng bảng liên kết (`story_author`, `story_genre`) để một truyện có nhiều tác giả hoặc nhiều thể loại mà vẫn dễ mở rộng.

* * *

# Aggregate

Trong Domain-Driven Design (DDD), **Aggregate** là một nhóm các Entity được quản lý như một đơn vị.

Trong app cào truyện:
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Bookmark
    
    ↓
    
    History

Đều xoay quanh một Story.

Ta gọi:
    
    
    Story Aggregate

Nghĩa là:
    
    
    Story
    
    là Aggregate Root

Mọi thao tác liên quan đến Chapter nên đi qua `StoryService` hoặc `StoryRepository`, thay vì để các phần khác sửa Chapter một cách tùy tiện. Điều này giúp giữ tính nhất quán của dữ liệu.

* * *

# Value Object

Khác Entity.

Không có ID.

Ví dụ
    
    
    URL
    
    Slug
    
    Email
    
    Domain

Ta có thể tạo:
    
    
    @dataclass(frozen=True)
    class StoryUrl:
        value: str

Không có id.

Chỉ có giá trị.

Hai URL giống nhau thì coi là cùng một Value Object.

* * *

# Tại sao phải tách Model khỏi Database?

Một sai lầm phổ biến là viết model gắn chặt với SQLite hoặc ORM:
    
    
    class StoryModel:
        ...

Rồi truyền đối tượng đó khắp chương trình.

Cách tốt hơn là:
    
    
    Database
    
    ↓
    
    Repository
    
    ↓
    
    Domain Model
    
    ↓
    
    Service
    
    ↓
    
    GUI

Nhờ vậy:

  * Có thể chuyển từ SQLite sang PostgreSQL mà không ảnh hưởng đến tầng nghiệp vụ. 
  * Có thể thay ORM (hoặc không dùng ORM) mà các lớp Service vẫn giữ nguyên. 
  * Việc kiểm thử trở nên đơn giản hơn vì có thể thay Repository thật bằng Repository giả (In-memory/Fake). 



* * *

# Cấu trúc thư mục gợi ý
    
    
    app/
    
    ├── domain/
    │   ├── models/
    │   │   ├── story.py
    │   │   ├── chapter.py
    │   │   ├── author.py
    │   │   ├── genre.py
    │   │   └── source.py
    │   │
    │   ├── value_objects/
    │   │   ├── slug.py
    │   │   ├── url.py
    │   │   └── domain.py
    │   │
    │   └── repositories/
    │       ├── story_repository.py
    │       ├── chapter_repository.py
    │       └── source_repository.py
    │
    ├── infrastructure/
    │   ├── sqlite/
    │   ├── crawler/
    │   └── plugins/
    │
    ├── services/
    │
    ├── ui/
    │
    └── main.py

Đây là cấu trúc gần với **Clean Architecture** , giúp dự án dễ mở rộng khi số lượng nguồn truyện và tính năng tăng lên.

* * *

# Bài tập

### Bài 1

Vẽ sơ đồ ERD (Entity Relationship Diagram) cho các bảng:

  * Source 
  * Story 
  * Chapter 
  * Author 
  * Genre 
  * StoryAuthor 
  * StoryGenre 



Xác định rõ khóa chính (PK), khóa ngoại (FK) và quan hệ 1-n, n-n.

### Bài 2

Tạo các `dataclass` cho:

  * Story 
  * Chapter 
  * Author 
  * Genre 
  * Source 



Sử dụng kiểu dữ liệu (`typing`) đầy đủ và hợp lý.

### Bài 3

Viết một chương trình Python:

  * Tạo một `Story`. 
  * Thêm 3 `Chapter`. 
  * In toàn bộ thông tin ra màn hình theo định dạng rõ ràng. 



### Bài 4 (nâng cao)

Thiết kế thêm các Entity sau:

  * `CrawlJob`
  * `CrawlLog`
  * `Bookmark`
  * `ReadingHistory`
  * `Image`



Xác định xem mỗi Entity thuộc Aggregate nào và giải thích lý do.

* * *

Ở **Buổi 2** , chúng ta sẽ đi sâu vào **thiết kế Database chuẩn cho app cào truyện** , bao gồm chuẩn hóa dữ liệu (1NF, 2NF, 3NF), thiết kế đầy đủ khoảng 15 bảng, các chỉ mục (index), khóa ngoại, ràng buộc, chiến lược lưu chương mới, hỗ trợ đa nguồn và chuẩn bị cho khả năng mở rộng lên hàng triệu chương truyện. Đây sẽ là nền tảng trước khi bắt đầu xây dựng `Repository Pattern`.

