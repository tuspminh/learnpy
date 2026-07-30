# Clean Architecture Deep Dive

# Buổi 9: Aggregate & Aggregate Root - Khái niệm khó nhất của Domain Layer

Đây là một trong những chủ đề mà ngay cả nhiều Senior Developer cũng còn nhầm lẫn.

Rất nhiều người học DDD đọc xong Aggregate vẫn không biết:

  * Khi nào cần Aggregate? 
  * Aggregate Root là gì? 
  * Vì sao Repository chỉ nên làm việc với Aggregate Root? 
  * Tại sao Aggregate giúp tránh dữ liệu bị "hỏng"? 



Sau buổi này, bạn sẽ hiểu vì sao **Aggregate chính là "người bảo vệ" (Guardian) của Domain Model.**

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Aggregate là gì? 
  * Aggregate Root là gì? 
  * Invariant của Aggregate 
  * Vì sao Repository chỉ làm việc với Aggregate Root 
  * Transaction Boundary 
  * Thiết kế Aggregate cho app cào truyện 
  * Những sai lầm phổ biến 



* * *

# Chúng ta đã có gì?
    
    
    Entity
        ↓
    Value Object
        ↓
    Domain Service
        ↓
    Aggregate   ← Hôm nay
        ↓
    Domain Event

* * *

# 1\. Vấn đề đầu tiên

Giả sử có Entity.
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Comment
    
    ↓
    
    Author

Quan hệ.
    
    
    Story
    
    ├── Chapter 1
    
    ├── Chapter 2
    
    ├── Chapter 3

Nếu Chapter có Repository riêng.
    
    
    chapter_repo.save(chapter)

Thì chuyện gì xảy ra?

* * *

Ví dụ.

Story có luật.

> Một Story luôn phải có ít nhất một Chapter.

Nhưng ai đó làm.
    
    
    chapter_repo.delete(last_chapter)

Story còn:
    
    
    Story
    
    ↓
    
    0 Chapter

Invariant bị phá vỡ.

* * *

# Một ví dụ khác

Luật.
    
    
    Story
    
    ↓
    
    Chapter Number
    
    phải liên tục

Có.
    
    
    1
    
    2
    
    3
    
    4

Ai đó.
    
    
    chapter_repo.delete(chapter2)

Thành.
    
    
    1
    
    3
    
    4

Business Rule bị hỏng.

* * *

# Aggregate sinh ra để giải quyết điều này.

* * *

# Aggregate là gì?

Định nghĩa.

> Aggregate là một nhóm các Entity và Value Object được quản lý như **một đơn vị nhất quán (Consistency Boundary).**

Có hai từ cực kỳ quan trọng:

  * Group 
  * Consistency 



* * *

# Ví dụ
    
    
    Story
    
    ├── Chapter
    
    ├── Chapter
    
    ├── Chapter

Đây là Aggregate.

* * *

Aggregate Root.
    
    
    Story

Là cửa chính.

* * *

# Aggregate Root

Aggregate Root là:

> Entity duy nhất được phép truy cập từ bên ngoài Aggregate.

Ví dụ.
    
    
    Story
    
    ├── Chapter
    
    ├── Chapter
    
    └── Chapter

Bên ngoài.

Chỉ được.
    
    
    story.add_chapter(...)

Không được.
    
    
    chapter.delete()

* * *

# Hình dung

Một công ty.
    
    
    CEO
    
    ├── Manager A
    
    ├── Manager B
    
    └── Manager C

Nhân viên ngoài công ty.

Không tự ý ra lệnh Manager.

Phải thông qua.
    
    
    CEO

CEO chính là Aggregate Root.

* * *

# Ví dụ

Sai.
    
    
    chapter.number = 99

Bất kỳ ai cũng sửa.

* * *

Đúng.
    
    
    story.renumber_chapters()

Story quyết định.

* * *

# Một Aggregate hoàn chỉnh
    
    
    from dataclasses import dataclass, field
    
    
    @dataclass
    class Chapter:
    
        number: int
    
        title: str

Aggregate Root.
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: str
    
        chapters: list[Chapter] = field(default_factory=list)
    
        def add_chapter(self, chapter):
    
            self.chapters.append(chapter)
    
        def remove_chapter(self, number):
    
            self.chapters = [
    
                c
    
                for c in self.chapters
    
                if c.number != number
            ]

Không có.
    
    
    chapter_repo.delete()

* * *

# Repository

Sai.
    
    
    StoryRepository
    
    ChapterRepository
    
    CommentRepository

Trong nhiều trường hợp.

* * *

Đúng.
    
    
    StoryRepository

Story quản lý Chapter.

* * *

# Vì sao?

Repository.
    
    
    story_repo.save(story)

Lưu toàn bộ Aggregate.

* * *

Không phải.
    
    
    chapter_repo.save()

* * *

# Transaction Boundary

Đây là khái niệm rất quan trọng.

Giả sử.
    
    
    story.add_chapter(...)

Sau đó.
    
    
    story.publish()

Sau đó.
    
    
    story_repo.save(story)

Tất cả nằm trong.
    
    
    1 Transaction

Không phải.
    
    
    Save Chapter
    
    ↓
    
    Commit
    
    ↓
    
    Publish Story
    
    ↓
    
    Commit

* * *

# Aggregate bảo vệ Invariant

Ví dụ.
    
    
    Story
    
    ↓
    
    Ít nhất một Chapter

Không ai được xóa Chapter cuối.
    
    
    def remove_chapter(self, number):
    
        if len(self.chapters) == 1:
    
            raise ValueError

Invariant được bảo vệ.

* * *

# Một ví dụ khác

Chapter Number.
    
    
    1
    
    2
    
    3

Thêm Chapter.
    
    
    story.add_chapter(...)

Story tự quyết định.
    
    
    chapter.number =
    
    len(chapters)+1

Không cho bên ngoài sửa.

* * *

# Aggregate Root quản lý Entity con

Sai.
    
    
    chapter.rename(...)

Bất kỳ ai gọi.

* * *

Đúng.
    
    
    story.rename_chapter(...)

Story quyết định.

* * *

# Aggregate và UseCase

UseCase.
    
    
    story = repo.get(id)
    
    story.add_chapter(...)
    
    repo.save(story)

UseCase không sửa.
    
    
    story.chapters.append(...)

* * *

# Aggregate trong app cào truyện

Một Aggregate.
    
    
    Story
    
    ├── Chapters
    
    ├── Tags
    
    ├── Metadata

Aggregate Root.
    
    
    Story

Repository.
    
    
    StoryRepository

Không cần.
    
    
    ChapterRepository

trong hầu hết trường hợp.

* * *

# Một Aggregate khác

Ví dụ.
    
    
    User
    
    ├── ReadingHistory
    
    ├── Bookmark
    
    ├── ReadingSetting

Aggregate Root.
    
    
    User

* * *

# Aggregate nhỏ

Một sai lầm.
    
    
    System
    
    ↓
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Author
    
    ↓
    
    Category
    
    ↓
    
    Comment
    
    ↓
    
    User
    
    ↓
    
    History
    
    ↓
    
    Plugin

Tất cả trong một Aggregate.

Sai.

Aggregate nên nhỏ.

* * *

# Quy tắc

Một Aggregate:

  * Một Root. 
  * Một Transaction. 
  * Một Consistency Boundary. 



* * *

# Aggregate không gọi Aggregate khác

Sai.
    
    
    Story
    
    ↓
    
    User
    
    ↓
    
    Comment
    
    ↓
    
    Plugin
    
    ↓
    
    Author

Chồng chéo.

* * *

Đúng.

Story.
    
    
    Story
    
    ↓
    
    AuthorId

Không giữ Author object nếu không cần.

* * *

# Tham chiếu bằng ID

Đây là nguyên tắc rất quan trọng.

Sai.
    
    
    Story.author = Author()

* * *

Đúng.
    
    
    Story.author_id = AuthorId(...)

Hoặc.
    
    
    Story.author = AuthorId(...)

Aggregate giao tiếp qua ID hoặc Value Object, không giữ tham chiếu trực tiếp tới Aggregate Root khác.

* * *

# Aggregate và Plugin

Plugin.
    
    
    story = parser.parse(html)

↓
    
    
    story.add_chapter(...)

↓
    
    
    story_repo.save(story)

Plugin không tạo Chapter Repository.

* * *

# Aggregate và Domain Service

Service.
    
    
    completion_service.check(story)

Không.
    
    
    completion_service.check(chapter)

Nếu Rule thuộc Story Aggregate.

* * *

# Aggregate và DTO

DTO.

↓

UseCase.

↓

Story Aggregate.

↓

Repository.

↓

Output DTO.

* * *

# Ví dụ chuyên nghiệp
    
    
    from dataclasses import dataclass, field
    
    
    @dataclass
    class Chapter:
    
        number: int
    
        title: str
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: str
    
        chapters: list[Chapter] = field(default_factory=list)
    
        def add_chapter(self, title):
    
            number = len(self.chapters) + 1
    
            chapter = Chapter(
    
                number=number,
    
                title=title
            )
    
            self.chapters.append(chapter)
    
        def remove_last(self):
    
            if len(self.chapters) <= 1:
    
                raise ValueError(
    
                    "Story must contain at least one chapter."
                )
    
            self.chapters.pop()

Mọi thay đổi Chapter đều đi qua Story.

* * *

# Aggregate không phải là Database

Đây là lỗi cực kỳ phổ biến.

Nhiều người.
    
    
    1 Table
    
    =
    
    1 Aggregate

Sai.

Ví dụ.
    
    
    Story
    
    Chapter
    
    Tag

Có thể là.
    
    
    3 Table
    
    ↓
    
    1 Aggregate

Hoặc.
    
    
    10 Table
    
    ↓
    
    1 Aggregate

Aggregate là khái niệm Domain.

Không phải Database.

* * *

# Aggregate không phải Object Graph

Sai.
    
    
    Story
    
    ↓
    
    Author
    
    ↓
    
    Country
    
    ↓
    
    Language
    
    ↓
    
    Currency
    
    ↓
    
    Plugin

Load tất cả.

Aggregate khổng lồ.

* * *

Đúng.
    
    
    Story
    
    ↓
    
    Chapter

Đủ.

* * *

# Thiết kế Aggregate cho dự án cào truyện

Tôi đề xuất:
    
    
    Story Aggregate
    
    Story (Aggregate Root)
    
    ├── Chapter
    ├── StoryMetadata
    ├── StoryStatus (VO)
    ├── StoryTitle (VO)
    └── StoryUrl (VO)

Một Aggregate khác:
    
    
    User Aggregate
    
    User (Aggregate Root)
    
    ├── Bookmark
    ├── ReadingHistory
    └── UserSetting

Một Aggregate khác:
    
    
    Plugin Aggregate
    
    Plugin (Aggregate Root)
    
    ├── PluginConfig
    └── PluginState

Mỗi Aggregate có Repository riêng:
    
    
    StoryRepository
    UserRepository
    PluginRepository

Không phải Repository cho từng Entity con.

* * *

# Những sai lầm phổ biến

## Sai 1

Mỗi Entity có một Repository.

Sai.

Repository thường dành cho **Aggregate Root**.

* * *

## Sai 2

Aggregate quá lớn.

Khi một Aggregate chứa quá nhiều Entity, mỗi lần tải hoặc lưu sẽ tốn tài nguyên và khó đảm bảo nhất quán.

* * *

## Sai 3

Aggregate quá nhỏ.

Nếu `Story` và `Chapter` có invariant chung nhưng lại tách thành hai Aggregate riêng, rất khó đảm bảo tính nhất quán.

* * *

## Sai 4

Sửa Entity con trực tiếp.
    
    
    chapter.number = 100

Nên để:
    
    
    story.renumber_chapters()

* * *

# Checklist

Một Aggregate tốt:

  * Có đúng một Aggregate Root. 
  * Chỉ Root được truy cập từ bên ngoài. 
  * Bảo vệ tất cả Invariant của nhóm Entity. 
  * Có một Repository cho Root. 
  * Có ranh giới Transaction rõ ràng. 
  * Không phụ thuộc trực tiếp vào Aggregate khác, chỉ tham chiếu bằng ID hoặc Value Object khi phù hợp. 



* * *

# Bài tập

## Bài 1

Thiết kế `Story Aggregate` gồm:

  * `Story` (Aggregate Root) 
  * `Chapter`
  * `StoryTitle` (VO) 
  * `StoryUrl` (VO) 



Các quy tắc:

  * Không được xóa Chapter cuối cùng. 
  * Chapter mới luôn được đánh số liên tiếp. 
  * Chỉ `Story` được phép thêm hoặc xóa Chapter. 



* * *

## Bài 2

Giả sử có các Entity:
    
    
    Story
    Chapter
    Comment
    Author
    Category
    User
    Bookmark
    ReadingHistory

Hãy chia chúng thành các Aggregate hợp lý và xác định Aggregate Root của từng nhóm.

* * *

## Bài 3

Xem lại dự án cào truyện hiện tại:

  * Bạn có đang có `ChapterRepository` riêng không? 
  * `Story` có đang cho phép sửa trực tiếp danh sách `chapters` từ bên ngoài không? 
  * Những invariant nào của `Story` đang bị phân tán giữa UI, UseCase và Repository thay vì được bảo vệ trong Aggregate? 



* * *

## Chuẩn bị cho Buổi 10

Ở buổi tiếp theo, chúng ta sẽ học **Domain Event** — cơ chế giúp các Aggregate giao tiếp với nhau mà vẫn giữ **Low Coupling**. Bạn sẽ hiểu:

  * Vì sao không nên để `Story.publish()` tự gửi email hoặc cập nhật cache. 
  * Cách phát sinh các sự kiện như `StoryPublished`, `ChapterAdded`, `StoryCompleted`. 
  * Cách Domain Event kết hợp với Celery, Redis và Plugin Architecture trong dự án cào truyện của bạn. 



Sau buổi này, Domain Layer của bạn sẽ gần như hoàn chỉnh theo đúng tinh thần của Domain-Driven Design và Clean Architecture.

