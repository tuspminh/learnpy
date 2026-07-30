# Clean Architecture Deep Dive

# Buổi 7: Domain Layer - Value Object (Khái niệm bị đánh giá thấp nhất trong DDD)

Đây là buổi mà rất nhiều lập trình viên Python sau khi học xong đều nói:

> **"Giờ mình mới hiểu tại sao code của mình trước đây lại đầy bug."**

Trong các dự án lớn, **Value Object (VO)** được sử dụng còn nhiều hơn Entity.

Eric Evans (tác giả Domain-Driven Design) từng nhấn mạnh rằng:

> Một Domain Model mạnh thường có rất nhiều Value Object nhỏ thay vì chỉ có các Entity lớn.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Value Object là gì? 
  * Value Object khác Entity như thế nào? 
  * Tại sao nên thay thế primitive (`str`, `int`, `float`) bằng Value Object? 
  * Immutable là gì? 
  * Equality theo giá trị 
  * Validation trong Value Object 
  * Value Object trong app cào truyện 



* * *

# Roadmap Domain Layer
    
    
    Entity
        ↓
    Value Object   ← Hôm nay
        ↓
    Domain Service
        ↓
    Aggregate
        ↓
    Domain Event

* * *

# 1\. Vấn đề của Primitive Obsession

Đây là một trong những Code Smell nổi tiếng của Martin Fowler.

Ví dụ:
    
    
    story = Story(
        id=1,
        title="One Piece",
        author="Oda"
    )

Nhìn có vẻ bình thường.

Nhưng thực ra:
    
    
    title: str
    author: str

Đều chỉ là `str`.

Python không phân biệt.

Ví dụ:
    
    
    Story(
        id=1,
        title="Oda",
        author="One Piece"
    )

Code vẫn chạy.

Sai nghiệp vụ.

* * *

Ví dụ khác
    
    
    chapter = Chapter(
        number=-10
    )

`int` chấp nhận.

Business không chấp nhận.

* * *

Đây gọi là:

> **Primitive Obsession**

Lạm dụng kiểu dữ liệu nguyên thủy.

* * *

# 2\. Value Object là gì?

Value Object là object:

  * Không có Identity 
  * So sánh theo giá trị 
  * Immutable (không thay đổi) 
  * Đại diện cho một khái niệm trong Domain 



Ví dụ:
    
    
    StoryTitle
    
    AuthorName
    
    ChapterNumber
    
    Email
    
    Money
    
    Coordinate
    
    Url
    
    Language
    
    ISBN

Không cái nào cần ID.

* * *

# Entity vs Value Object

## Entity
    
    
    Story #100

Có Identity.

Đổi tên:
    
    
    Story #100

Vẫn là truyện đó.

* * *

## Value Object
    
    
    StoryTitle
    
    ↓
    
    "One Piece"

Nếu đổi thành:
    
    
    "Naruto"

Đó là một Value Object khác.

* * *

# So sánh

Entity| Value Object  
---|---  
Có Identity| Không có Identity  
Mutable (thường)| Immutable  
So sánh bằng ID| So sánh bằng giá trị  
Đại diện thực thể| Đại diện thuộc tính có ý nghĩa nghiệp vụ  
  
* * *

# Ví dụ đầu tiên

Không dùng VO.
    
    
    @dataclass
    class Story:
    
        title: str

Có thể:
    
    
    story.title = ""

Hoặc:
    
    
    story.title = "     "

Sai.

* * *

Dùng Value Object.
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True, slots=True)
    class StoryTitle:
    
        value: str
    
        def __post_init__(self):
    
            title = self.value.strip()
    
            if not title:
                raise ValueError("Title cannot be empty")
    
            if len(title) > 300:
                raise ValueError("Title too long")
    
            object.__setattr__(self, "value", title)

* * *

Sử dụng
    
    
    title = StoryTitle(" One Piece ")
    
    print(title.value)

Kết quả:
    
    
    One Piece

Tự động chuẩn hóa.

* * *

# Immutable

Đây là đặc điểm cực kỳ quan trọng.
    
    
    title = StoryTitle("Naruto")

Sau đó:
    
    
    title.value = "Bleach"

Python báo lỗi.

Vì:
    
    
    @dataclass(frozen=True)

Immutable.

* * *

Tại sao cần Immutable?

Ví dụ.
    
    
    story.title

Đang được:

  * UI dùng 
  * Cache dùng 
  * Logger dùng 



Nếu title đổi liên tục.

Rất khó debug.

Immutable giúp an toàn.

* * *

# Equality

Entity:
    
    
    Story(1)

và
    
    
    Story(1)

Là cùng Entity.

* * *

Value Object.
    
    
    StoryTitle("One Piece")

và
    
    
    StoryTitle("One Piece")

Bằng nhau.
    
    
    == True

Không cần ID.

* * *

Ví dụ.
    
    
    title1 = StoryTitle("Naruto")
    
    title2 = StoryTitle("Naruto")
    
    print(title1 == title2)

Kết quả.
    
    
    True

* * *

# Validation

Validation nên nằm trong VO.

Ví dụ.

Sai.
    
    
    if len(title) > 300:
        ...

Xuất hiện:

  * UI 
  * API 
  * UseCase 
  * CLI 



Lặp lại.

* * *

Đúng.
    
    
    StoryTitle(title)

Nếu hợp lệ.

Object được tạo.

Nếu không.

Exception.

* * *

# Value Object trong Entity
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: StoryTitle

Không còn.
    
    
    title: str

* * *

Tạo Entity.
    
    
    story = Story(
    
        id=1,
    
        title=StoryTitle("One Piece")
    )

* * *

# Một Value Object khác

Chapter Number.
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True, slots=True)
    class ChapterNumber:
    
        value: int
    
        def __post_init__(self):
    
            if self.value < 1:
                raise ValueError("Chapter must be >=1")

Không còn.
    
    
    number = -100

* * *

# URL

App cào truyện.

URL rất quan trọng.

Sai.
    
    
    url: str

* * *

Đúng.
    
    
    from dataclasses import dataclass
    from urllib.parse import urlparse
    
    
    @dataclass(frozen=True, slots=True)
    class StoryUrl:
    
        value: str
    
        def __post_init__(self):
    
            parsed = urlparse(self.value)
    
            if parsed.scheme not in ("http", "https"):
                raise ValueError("Invalid URL")

* * *

UseCase.
    
    
    dto.url

↓
    
    
    StoryUrl(dto.url)

Nếu URL sai.

Lỗi ngay.

* * *

# Author Name
    
    
    @dataclass(frozen=True, slots=True)
    class AuthorName:
    
        value: str
    
        def __post_init__(self):
    
            name = self.value.strip()
    
            if not name:
                raise ValueError("Author empty")
    
            object.__setattr__(self, "value", name)

* * *

# Story Entity
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: StoryTitle
    
        author: AuthorName

Entity mạnh hơn nhiều.

* * *

# Value Object có method

Không chỉ dữ liệu.

Ví dụ.
    
    
    @dataclass(frozen=True)
    class StoryTitle:
    
        value: str
    
        def slug(self):
    
            return (
                self.value
                .lower()
                .replace(" ", "-")
            )

Dùng.
    
    
    title.slug()

↓
    
    
    one-piece

Business nằm trong VO.

* * *

# Value Object trong app cào truyện

Có thể có.
    
    
    StoryTitle
    
    AuthorName
    
    StoryUrl
    
    ChapterNumber
    
    ChapterTitle
    
    Language
    
    Status
    
    Rating
    
    TagName

Không dùng.
    
    
    str
    
    int
    
    float

khắp nơi.

* * *

# Entity + Value Object
    
    
    Story
    
    ├── StoryTitle
    ├── AuthorName
    ├── StoryUrl
    ├── StoryStatus
    └── list[Chapter]

Domain trở nên rất rõ ràng.

* * *

# So sánh

Không dùng VO.
    
    
    story.title = ""

Không lỗi.

* * *

Dùng VO.
    
    
    story.title = StoryTitle("")

↓
    
    
    ValueError

Bug bị chặn ngay khi tạo dữ liệu.

* * *

# Một thiết kế chuyên nghiệp
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: StoryTitle
    
        author: AuthorName
    
        url: StoryUrl

UseCase.
    
    
    story = Story(
    
        id=1,
    
        title=StoryTitle(dto.title),
    
        author=AuthorName(dto.author),
    
        url=StoryUrl(dto.url),
    )

Không cần validate ở nhiều nơi.

* * *

# Khi nào KHÔNG nên dùng Value Object?

Không phải lúc nào cũng cần.

Ví dụ:
    
    
    page = 1

Nếu:

  * chỉ dùng nội bộ 
  * không có business rule 
  * không cần validation 



Thì:
    
    
    int

là đủ.

Đừng tạo:
    
    
    PageNumber
    
    Offset
    
    Limit

nếu chúng không mang ý nghĩa nghiệp vụ đặc biệt.

* * *

# Những Value Object rất đáng có trong dự án cào truyện

Đối với dự án của bạn, tôi khuyến nghị:
    
    
    StoryTitle
    AuthorName
    StoryUrl
    ChapterTitle
    ChapterNumber
    LanguageCode
    StoryStatus
    PluginName
    SourceId

Sau này khi xây dựng Plugin Architecture và nhiều nguồn truyện, các VO này sẽ giúp giảm đáng kể lỗi do truyền nhầm dữ liệu.

* * *

# Những sai lầm phổ biến

## Sai lầm 1

Value Object chứa ID.
    
    
    class StoryTitle:
    
        id: int

Sai.

VO không có Identity.

* * *

## Sai lầm 2

VO mutable.
    
    
    title.value = ""

Sai.

VO nên immutable.

* * *

## Sai lầm 3

Validation nằm ngoài VO.
    
    
    if title == "":
        ...

lặp đi lặp lại ở nhiều nơi.

Nên để:
    
    
    StoryTitle(title)

* * *

## Sai lầm 4

Biến mọi thứ thành Value Object.

Không cần.

Chỉ tạo VO khi:

  * Có business meaning. 
  * Có business rule. 
  * Có validation. 
  * Có hành vi liên quan. 



* * *

# Checklist

Một đối tượng nên là Value Object nếu:

  * Không có Identity. 
  * So sánh theo giá trị. 
  * Có ý nghĩa nghiệp vụ. 
  * Có thể immutable. 
  * Có validation hoặc hành vi riêng. 
  * Có thể tái sử dụng ở nhiều Entity. 



* * *

# Bài tập

## Bài 1

Thiết kế các Value Object sau:

  * `StoryTitle`
  * `AuthorName`
  * `ChapterTitle`
  * `ChapterNumber`



Yêu cầu:

  * Immutable (`frozen=True`) 
  * Có validation trong `__post_init__`
  * Chuẩn hóa dữ liệu (ví dụ `strip()` với chuỗi) 



* * *

## Bài 2

Refactor `Story` Entity để thay thế:
    
    
    title: str
    author: str

bằng:
    
    
    title: StoryTitle
    author: AuthorName

và cập nhật các phương thức (`rename()`, `change_author()`) để chỉ nhận Value Object.

* * *

## Bài 3

Lập danh sách các trường trong dự án cào truyện của bạn và phân loại:

Trường| Primitive| Nên là Value Object?| Lý do  
---|---|---|---  
title| `str`| Có| Có validation, mang ý nghĩa nghiệp vụ  
author| `str`| Có| Chuẩn hóa và kiểm tra rỗng  
url| `str`| Có| Kiểm tra định dạng URL  
page| `int`| Có/Không?| Giải thích lựa chọn  
timeout| `int`| Có/Không?| Giải thích lựa chọn  
  
Việc tự phân loại này sẽ giúp bạn hình thành tư duy thiết kế Domain Model thay vì chỉ sử dụng các kiểu dữ liệu nguyên thủy.

* * *

## Chuẩn bị cho Buổi 8

Buổi tiếp theo chúng ta sẽ học **Domain Service** — câu trả lời cho câu hỏi rất thường gặp:

> "Nếu nghiệp vụ không thuộc Entity, cũng không thuộc UseCase thì nên đặt ở đâu?"

Bạn sẽ học cách phân biệt rõ **Entity** , **Value Object** , **Domain Service** và **Use Case** , cũng như tránh hai cực đoan phổ biến:

  * Nhồi mọi nghiệp vụ vào Entity. 
  * Biến UseCase thành "God Service" chứa toàn bộ business logic. 



Sau buổi này, mô hình Domain của bạn sẽ bắt đầu tiến gần đến cách các hệ thống doanh nghiệp lớn được thiết kế.

