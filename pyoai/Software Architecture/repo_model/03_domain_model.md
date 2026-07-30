# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 3 - Thiết kế Domain Model chuyên nghiệp bằng Python

> Đây là buổi quan trọng nhất của toàn bộ khóa học. Sau buổi này, cách bạn thiết kế model sẽ thay đổi hoàn toàn.

Ở buổi trước chúng ta đã có **Database Design**.

Rất nhiều lập trình viên mới học sẽ làm như sau:
    
    
    SQLite
        ↓
    class Story
        ↓
    GUI

Đây là cách làm phổ biến nhưng có nhiều hạn chế.

Một kiến trúc tốt sẽ là:
    
    
    SQLite/Postgres
            │
    Infrastructure Layer
            │
    Repository
            │
    Domain Model
            │
    Service
            │
    GUI / CLI / API

Điều quan trọng là **Domain Model không biết SQLite là gì**.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Domain Model là gì 
  * Entity 
  * Value Object 
  * Enum 
  * Aggregate Root 
  * Validation 
  * Business Rule 
  * Factory Method 
  * Domain Event (giới thiệu) 
  * Vì sao không để SQL trong Model 



* * *

# 1\. Domain Model là gì?

Domain Model là mô hình biểu diễn **nghiệp vụ** , không phải dữ liệu lưu trong database.

Ví dụ:

Database:
    
    
    story
    
    id
    title
    status
    cover
    created_at

Domain Model:
    
    
    Story(
        id=1,
        title="Đấu La Đại Lục",
        status=StoryStatus.ONGOING,
        ...
    )

Khác biệt là:

Database quan tâm:

  * lưu dữ liệu 



Domain quan tâm:

  * truyện có hợp lệ không 
  * có thể cập nhật không 
  * có được thêm chương không 



* * *

# 2\. Không viết Model như thế này

Đây là kiểu ORM Model.
    
    
    class Story:
        id: int
        title: str
        status: str

Model này chỉ là container.

Không có nghiệp vụ.

* * *

# Model nên có hành vi

Ví dụ:
    
    
    story.rename("Đấu La Đại Lục Full")

hoặc
    
    
    story.add_chapter(chapter)

hoặc
    
    
    story.complete()

Model phải biết tự bảo vệ dữ liệu của chính nó.

* * *

# 3\. StoryStatus

Đừng dùng string.

Sai:
    
    
    story.status="done"
    
    story.status="finish"
    
    story.status="ok"
    
    story.status="completed"

Có hàng chục cách viết.

Nên dùng Enum.
    
    
    from enum import Enum
    
    
    class StoryStatus(Enum):
        ONGOING = "ongoing"
        COMPLETED = "completed"
        HIATUS = "hiatus"

Sau này IDE sẽ tự gợi ý.

* * *

# 4\. Dataclass

Story
    
    
    from dataclasses import dataclass, field
    from datetime import datetime
    from enum import Enum
    
    
    class StoryStatus(Enum):
        ONGOING = "ongoing"
        COMPLETED = "completed"
        HIATUS = "hiatus"
    
    
    @dataclass(slots=True)
    class Story:
    
        id: int | None
    
        title: str
    
        slug: str
    
        summary: str
    
        cover: str
    
        status: StoryStatus
    
        created_at: datetime
    
        updated_at: datetime

Điểm mới:
    
    
    slots=True

Lợi ích:

  * ít tốn RAM 
  * nhanh hơn 
  * tránh tạo attribute lung tung 



* * *

# 5\. Validation

Sai:
    
    
    story = Story(
        title=""
    )

Tên truyện rỗng.

Không hợp lệ.

Ta dùng
    
    
    __post_init__()
    
    
    @dataclass(slots=True)
    class Story:
    
        title: str
    
        def __post_init__(self):
    
            if not self.title.strip():
    
                raise ValueError("Story title cannot be empty.")

Model tự kiểm tra dữ liệu.

* * *

# 6\. Value Object

Đây là phần nhiều người bỏ qua.

Ví dụ URL.

Đừng để
    
    
    url="abc"

Ta tạo
    
    
    @dataclass(frozen=True, slots=True)
    class StoryUrl:
    
        value: str
    
        def __post_init__(self):
    
            if not self.value.startswith("http"):
    
                raise ValueError("Invalid URL.")

Lợi ích:
    
    
    StoryUrl

luôn hợp lệ.

* * *

# 7\. Slug cũng là Value Object
    
    
    @dataclass(frozen=True)
    class Slug:
    
        value: str

Có thể kiểm tra
    
    
    - không khoảng trắng
    
    - chỉ chữ thường
    
    - dấu -

Ví dụ
    
    
    dau-la-dai-luc

Đúng.
    
    
    Đấu La

Sai.

* * *

# 8\. Aggregate Root

Nhớ sơ đồ
    
    
    Story
    
    ↓
    
    Chapter

Story là Aggregate Root.

Không nên
    
    
    chapter.story_id=10

ở khắp nơi.

Thay vào đó
    
    
    story.add_chapter(chapter)

Story sẽ:

  * kiểm tra chapter trùng chưa 
  * đánh số 
  * cập nhật chapter_count 



* * *

Ví dụ
    
    
    @dataclass
    class Story:
    
        chapters: list["Chapter"] = field(default_factory=list)
    
        def add_chapter(self, chapter):
    
            self.chapters.append(chapter)

Đây mới chỉ là phiên bản đơn giản.

Sau này Repository sẽ lưu xuống database.

* * *

# 9\. Business Rule

Business Rule nên nằm trong Domain.

Ví dụ

Không cho thêm chapter trùng.
    
    
    def add_chapter(self, chapter):
    
        for c in self.chapters:
    
            if c.index == chapter.index:
    
                raise ValueError("Duplicated chapter.")
    
        self.chapters.append(chapter)

GUI không cần biết.

SQLite cũng không cần biết.

* * *

# 10\. Chapter Model
    
    
    @dataclass(slots=True)
    class Chapter:
    
        id: int | None
    
        story_id: int
    
        index: int
    
        title: str
    
        url: str
    
        content: str

Có thể thêm
    
    
    @property
    def word_count(self):
    
        return len(self.content.split())

Không cần lưu
    
    
    word_count

nếu có thể tính được.

Đây gọi là **Derived Property**.

* * *

# 11\. Author
    
    
    @dataclass(slots=True)
    class Author:
    
        id: int | None
    
        name: str

Validation
    
    
    def __post_init__(self):
    
        if len(self.name) < 2:
    
            raise ValueError

* * *

# 12\. Genre
    
    
    @dataclass(slots=True)
    class Genre:
    
        id: int | None
    
        name: str

* * *

# 13\. Source
    
    
    from enum import Enum
    
    
    class SourceType(Enum):
    
        TRUYENFULL="truyenfull"
    
        NOVELBIN="novelbin"
    
        TTV="ttv"

Model
    
    
    @dataclass(slots=True)
    class Source:
    
        id:int|None
    
        name:str
    
        domain:str
    
        type:SourceType

Sau này plugin sẽ dựa vào
    
    
    type

để chọn crawler.

* * *

# 14\. Factory Method

Thay vì
    
    
    Story(...)

Ta tạo
    
    
    Story.create(...)

Ví dụ
    
    
    @dataclass
    class Story:
    
        ...
    
        @classmethod
        def create(cls,title):
    
            return cls(
    
                id=None,
    
                title=title,
    
                slug="",
    
                ...
    
            )

Factory giúp:

  * mặc định giá trị 
  * validate 
  * dễ thay đổi sau này 



* * *

# 15\. Domain Event (Giới thiệu)

Sau này khi
    
    
    story.add_chapter()

có thể phát sinh event
    
    
    ChapterAdded

Service sẽ lắng nghe.

Ví dụ
    
    
    ChapterAdded
    
    ↓
    
    Update Search Index
    
    ↓
    
    Notify User
    
    ↓
    
    Download Image

Đây là nền tảng để tích hợp Celery hoặc Dramatiq sau này.

* * *

# 16\. Cấu trúc thư mục Domain
    
    
    app/
    
    domain/
    
        entities/
    
            story.py
    
            chapter.py
    
            author.py
    
            genre.py
    
            source.py
    
        enums/
    
            story_status.py
    
            source_type.py
    
        value_objects/
    
            slug.py
    
            url.py
    
        events/
    
            chapter_added.py
    
        exceptions/
    
            invalid_story.py
    
            duplicate_chapter.py

Lưu ý: tách `entities`, `value_objects`, `enums`, `exceptions` sẽ giúp dự án dễ bảo trì hơn thay vì dồn tất cả model vào một thư mục.

* * *

# 17\. Những gì KHÔNG nên có trong Domain Model

Không nên:
    
    
    class Story:
    
        def save(self):
            ...

Không nên:
    
    
    sqlite3.connect(...)

Không nên:
    
    
    cursor.execute(...)

Không nên:
    
    
    SELECT *

Không nên:
    
    
    requests.get(...)

Không nên:
    
    
    BeautifulSoup(...)

**Domain chỉ mô tả nghiệp vụ** , không biết dữ liệu đến từ SQLite, PostgreSQL hay API.

* * *

# 18\. Kiến trúc hoàn chỉnh
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository
     │
     ▼
    SQLiteRepository
     │
     ▼
    SQLite

Trong chiều ngược lại:
    
    
    SQLite Row
          │
          ▼
    Repository
          │
          ▼
    Story Entity
          │
          ▼
    Service
          │
          ▼
    GUI

Repository chịu trách nhiệm chuyển đổi giữa dữ liệu lưu trữ và Domain Model.

* * *

# Cấu trúc project sau 3 buổi
    
    
    app/
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── enums/
    │   ├── events/
    │   ├── exceptions/
    │   └── repositories/      # Chỉ chứa interface
    │
    ├── infrastructure/
    │   ├── sqlite/
    │   ├── crawler/
    │   └── plugins/
    │
    ├── services/
    ├── ui/
    └── main.py

* * *

# Bài tập

## Bài 1

Viết đầy đủ các `dataclass` cho:

  * `Story`
  * `Chapter`
  * `Author`
  * `Genre`
  * `Source`



Yêu cầu:

  * `slots=True`
  * `__post_init__()` để kiểm tra dữ liệu 
  * sử dụng `Enum` thay cho chuỗi (`str`) ở những trường phù hợp. 



* * *

## Bài 2

Tạo các Value Object:

  * `Slug`
  * `StoryUrl`
  * `CoverUrl`



Mỗi Value Object cần:

  * immutable (`frozen=True`) 
  * validation 
  * có thể so sánh bằng giá trị (`==`). 



* * *

## Bài 3

Bổ sung các phương thức nghiệp vụ cho `Story`:

  * `rename(new_title)`
  * `change_status(status)`
  * `add_chapter(chapter)`
  * `remove_chapter(index)`



Đảm bảo không cho phép thêm hai chapter có cùng `index`.

* * *

## Bài 4 (nâng cao)

Thiết kế `Story.create(...)` như một **Factory Method** :

  * tự sinh `created_at`, `updated_at`
  * nhận `title`, `slug`, `source`
  * khởi tạo trạng thái mặc định là `StoryStatus.ONGOING`
  * trả về một `Story` luôn ở trạng thái hợp lệ. 



* * *

### Chuẩn bị cho Buổi 4

Từ buổi tiếp theo, chúng ta sẽ chuyển sang **Repository Pattern**. Chúng ta sẽ bắt đầu bằng việc thiết kế các interface như:

  * `StoryRepository`
  * `ChapterRepository`
  * `SourceRepository`



và tìm hiểu vì sao **Service chỉ nên làm việc với interface** , không phụ thuộc vào `sqlite3`, `SQLAlchemy` hay bất kỳ công nghệ lưu trữ cụ thể nào. Đây là nền tảng của Dependency Inversion và Clean Architecture trong dự án crawler truyện.

