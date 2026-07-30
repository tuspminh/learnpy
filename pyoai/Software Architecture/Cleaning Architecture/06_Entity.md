# Clean Architecture Deep Dive

# Buổi 6: Domain Layer - Entity (Trái tim của Clean Architecture)

Đây là một trong những buổi **quan trọng nhất của toàn bộ khóa học**.

Thực tế, đa số lập trình viên Python đều hiểu sai về Entity.

Nhiều người nghĩ Entity chỉ là:
    
    
    @dataclass
    class User:
        id: int
        name: str

hoặc
    
    
    class User(Base):
        __tablename__ = "users"

Đó **không phải Entity trong Clean Architecture**.

Đó chỉ là:

  * Data Model 
  * ORM Model 
  * Database Record 



chứ chưa phải **Domain Entity**.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Entity là gì 
  * Entity khác Database Model như thế nào 
  * Rich Domain Model 
  * Anemic Domain Model 
  * Identity 
  * Business Rule 
  * Invariant 
  * Encapsulation trong Entity 
  * Entity trong app cào truyện 



* * *

# Roadmap Domain Layer

Trong 5 buổi tiếp theo chúng ta sẽ học:
    
    
    Buổi 6  Entity
    
    ↓
    
    Buổi 7  Value Object
    
    ↓
    
    Buổi 8  Domain Service
    
    ↓
    
    Buổi 9  Aggregate
    
    ↓
    
    Buổi 10 Domain Event

Đây là trái tim của Domain Driven Design (DDD) và Clean Architecture.

* * *

# 1\. Entity là gì?

Định nghĩa:

> Entity là một đối tượng có **Identity** và chứa **Business Rules**.

Có hai từ cực kỳ quan trọng:

  * Identity 
  * Business Rules 



* * *

Ví dụ

Trong app cào truyện.
    
    
    Story

là Entity.

Vì:
    
    
    Story #100

vẫn là truyện đó.

Cho dù:

  * đổi tên 
  * đổi tác giả 
  * đổi mô tả 



Identity vẫn giữ nguyên.

* * *

# Ví dụ
    
    
    Story(
        id=100,
        title="Đấu Phá Thương Khung"
    )

Mai đổi:
    
    
    Story(
        id=100,
        title="Đấu Phá Thương Khung (Bản mới)"
    )

Đây vẫn là cùng một Story.

Identity:
    
    
    id = 100

* * *

# Không phải mọi object đều là Entity

Ví dụ:
    
    
    Temperature
    
    Money
    
    Email
    
    Coordinate

Không có Identity.

Đó là Value Object.

Buổi sau sẽ học.

* * *

# Entity ≠ Database Table

Đây là lỗi phổ biến nhất.

Ví dụ SQLAlchemy.
    
    
    class Story(Base):
    
        __tablename__ = "story"
    
        id = Column(Integer)
    
        title = Column(String)

Nhiều người nghĩ đây là Entity.

Không.

Đây là ORM Model.

Nó phục vụ Database.

Không phải Business.

* * *

# Entity phải chứa Business

Ví dụ.

Sai.
    
    
    @dataclass
    class Story:
    
        id: int
        title: str
        author: str

Nó chỉ là cái hộp dữ liệu.

Không có hành vi.

Không có luật.

Đây gọi là

**Anemic Domain Model**.

* * *

# Rich Domain Model

Entity nên biết cách tự bảo vệ mình.

Ví dụ.
    
    
    class Story:
    
        def __init__(self, id: int, title: str):
    
            self.id = id
            self.title = title

Thêm luật.
    
    
    class Story:
    
        def rename(self, new_title):
    
            if not new_title.strip():
                raise ValueError("Title cannot be empty")
    
            self.title = new_title

Business Rule nằm trong Entity.

* * *

# Sai lầm phổ biến

Viết:
    
    
    story.title = ""

Không ai kiểm tra.

Không có Rule.

* * *

Đúng.
    
    
    story.rename("")

Kết quả:
    
    
    ValueError

Entity tự bảo vệ dữ liệu.

* * *

# Business Rule

Ví dụ.

Một Story:

  * phải có tiêu đề 
  * tiêu đề tối đa 300 ký tự 
  * không được toàn khoảng trắng 



Entity kiểm tra.
    
    
    class Story:
    
        def rename(self, title):
    
            title = title.strip()
    
            if not title:
                raise ValueError
    
            if len(title) > 300:
                raise ValueError
    
            self.title = title

Không phải UI kiểm tra.

Không phải Database.

Entity kiểm tra.

* * *

# Invariant

Invariant =

Luật luôn đúng.

Ví dụ.
    
    
    Story
    
    ↓
    
    Title
    
    ↓
    
    Không bao giờ rỗng

Đó là Invariant.

* * *

Ví dụ.
    
    
    story.rename("")

Không được phép.

* * *

Ví dụ khác.
    
    
    Chapter
    
    ↓
    
    chapter_number
    
    ↓
    
    >=1

Đó là Invariant.

* * *

# Entity bảo vệ Invariant
    
    
    class Chapter:
    
        def __init__(self, number):
    
            if number < 1:
                raise ValueError
    
            self.number = number

Không thể tạo Chapter số 0.

* * *

# Encapsulation

Sai.
    
    
    story.title = ""

* * *

Đúng.
    
    
    story.rename("One Piece")

Entity quyết định.

Không phải bên ngoài.

* * *

# Entity không biết Database

Sai.
    
    
    class Story:
    
        def save(self):
    
            sqlite.save(self)

Entity biết SQLite.

Sai.

* * *

Đúng.
    
    
    class Story:
    
        def rename(self, title):
            ...

Repository mới lưu.

* * *

# Entity không biết HTTP

Sai.
    
    
    story.download_cover()

Download ảnh là Infrastructure.

Không phải Business.

* * *

# Entity không biết GUI

Sai.
    
    
    story.show_messagebox()

* * *

Không biết:

  * PySide6 
  * FastAPI 
  * Requests 
  * Redis 
  * SQLite 



* * *

# Entity giàu nghiệp vụ

Ví dụ.
    
    
    class Story:
    
        def publish(self):
    
            if not self.chapters:
                raise Exception
    
            self.status = "published"

Không phải UseCase.

Không phải UI.

Entity tự quyết định.

* * *

# Entity và UseCase

Một hiểu lầm phổ biến.

Nhiều người viết.
    
    
    class PublishStoryUseCase:
    
        def execute(self):
    
            if len(story.chapters)==0:
                ...

Sai.

Business Rule nằm ngoài Entity.

* * *

Đúng.
    
    
    story.publish()

UseCase chỉ điều phối.
    
    
    story.publish()
    
    repo.save(story)

* * *

# Ví dụ hoàn chỉnh
    
    
    from dataclasses import dataclass, field
    
    
    @dataclass
    class Story:
    
        id: int
    
        title: str
    
        chapters: list = field(default_factory=list)
    
        published: bool = False
    
        def rename(self, title):
    
            title = title.strip()
    
            if not title:
    
                raise ValueError("Empty title")
    
            self.title = title
    
        def publish(self):
    
            if len(self.chapters) == 0:
    
                raise ValueError("No chapters")
    
            self.published = True

Đây mới là Entity.

* * *

# Entity trong app cào truyện

Story.

Có thể có.
    
    
    rename()
    
    publish()
    
    add_chapter()
    
    remove_chapter()
    
    change_author()
    
    archive()

Không có.
    
    
    save()
    
    delete_sqlite()
    
    download()
    
    parse_html()
    
    requests.get()

* * *

# Ví dụ Chapter Entity
    
    
    class Chapter:
    
        def __init__(self, number, title):
    
            if number < 1:
                raise ValueError
    
            self.number = number
    
            self.title = title
    
        def rename(self, title):
    
            if not title.strip():
    
                raise ValueError
    
            self.title = title

* * *

# Entity và Repository

Repository.
    
    
    save()
    
    delete()
    
    find()
    
    list()

Entity.
    
    
    rename()
    
    publish()
    
    archive()

Hai vai trò khác nhau.

* * *

# Entity và Parser

Parser.
    
    
    HTML
    
    ↓
    
    Entity

Parser tạo Entity.

Không lưu Database.

* * *

# Entity và DTO

DTO.
    
    
    CreateStoryInput

↓

UseCase

↓

Entity

↓

Repository

↓

Output DTO

↓

UI

Entity không đi thẳng tới UI.

* * *

# Thiết kế Story Entity chuyên nghiệp
    
    
    from __future__ import annotations
    
    from dataclasses import dataclass, field
    
    
    @dataclass(slots=True)
    class Story:
    
        id: int
    
        title: str
    
        author: str
    
        chapters: list["Chapter"] = field(default_factory=list)
    
        is_published: bool = False
    
        def rename(self, title: str):
    
            title = title.strip()
    
            if not title:
    
                raise ValueError("Title empty")
    
            self.title = title
    
        def add_chapter(self, chapter):
    
            self.chapters.append(chapter)
    
        def publish(self):
    
            if not self.chapters:
    
                raise ValueError("Cannot publish story without chapters")
    
            self.is_published = True

Đây là Rich Domain Model.

* * *

# So sánh Anemic vs Rich Domain

## Anemic Domain Model
    
    
    @dataclass
    class Story:
        id: int
        title: str

Business Rule nằm trong:

  * Service 
  * UseCase 
  * Controller 



Entity chỉ là dữ liệu.

* * *

## Rich Domain Model
    
    
    story.rename("One Piece")
    
    story.publish()
    
    story.add_chapter(...)

Business Rule nằm trong Entity.

* * *

# Khi nào không nên nhồi mọi thứ vào Entity?

Đây là điểm nhiều tài liệu nói chưa rõ.

Entity **không nên** chứa nghiệp vụ cần đến dữ liệu hoặc dịch vụ bên ngoài.

Ví dụ:

> "Tên truyện phải là duy nhất trong toàn hệ thống."

Entity **không thể tự kiểm tra** , vì nó cần truy vấn Repository.

Sai:
    
    
    class Story:
        def rename(self, title, repo):
            if repo.exists_title(title):
                raise ValueError

Entity đã phụ thuộc Repository.

Đúng:
    
    
    UseCase
        ↓
    Repository kiểm tra
        ↓
    Story.rename(title)

Hoặc dùng Domain Service (chúng ta sẽ học ở Buổi 8).

* * *

# Checklist thiết kế Entity

Một Entity tốt nên trả lời "Có" cho các câu hỏi sau:

  * Có **Identity** rõ ràng không? 
  * Có chứa Business Rule không? 
  * Có tự bảo vệ Invariant không? 
  * Có che giấu việc thay đổi trạng thái qua các method thay vì sửa trực tiếp thuộc tính không? 
  * Không import `sqlite3`, `requests`, `PySide6`, `redis`, `httpx`? 
  * Không biết Repository, Database hay UI? 



Nếu một class chỉ có thuộc tính và không có hành vi, hãy tự hỏi:

> Đây thực sự là Entity hay chỉ là một Data Transfer Object?

* * *

# Bài tập

## Bài 1

Thiết kế `Story` Entity cho app cào truyện với các yêu cầu:

  * Tiêu đề không được rỗng. 
  * Không được publish khi chưa có Chapter. 
  * Có thể đổi tác giả. 
  * Có thể thêm và xóa Chapter. 



Chỉ viết các hành vi nghiệp vụ, không có code database.

* * *

## Bài 2

Thiết kế `Chapter` Entity:

  * `number >= 1`
  * Tiêu đề không được rỗng. 
  * Có thể đổi tiêu đề. 
  * Có thể đánh dấu đã tải nội dung (`mark_downloaded()`). 



Hãy xác định các **Invariant** của `Chapter`.

* * *

## Bài 3

Xem lại dự án cào truyện hiện tại của bạn:

  * `Story` hiện là ORM Model, DTO hay Domain Entity? 
  * Có method nào như `save()`, `download()`, `parse_html()` đang nằm trong Entity không? 
  * Những Business Rule nào đang nằm trong UseCase mà thực ra nên chuyển vào Entity? 



* * *

## Chuẩn bị cho Buổi 7

Ở buổi sau chúng ta sẽ học **Value Object** — một khái niệm cực kỳ quan trọng nhưng thường bị bỏ qua. Sau buổi đó, bạn sẽ biết cách thay thế các kiểu dữ liệu nguyên thủy (`str`, `int`, `float`) bằng các đối tượng giàu ngữ nghĩa như `StoryTitle`, `ChapterNumber`, `Email`, `Url`, `Money`, giúp mã nguồn an toàn hơn, dễ đọc hơn và giảm đáng kể các lỗi do truyền nhầm dữ liệu. Đây cũng là một bước quan trọng để xây dựng Domain Model chuyên nghiệp theo DDD và Clean Architecture.

