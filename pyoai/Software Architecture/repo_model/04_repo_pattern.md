# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 4 - Repository Pattern Deep Dive

> Đây là buổi mà chúng ta bắt đầu tách **Business Logic** khỏi **Database**. Nếu làm đúng từ đầu, sau này bạn có thể đổi từ SQLite sang PostgreSQL, MySQL, SQLAlchemy, thậm chí REST API mà gần như không phải sửa Service.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Repository là gì 
  * Vì sao cần Repository 
  * Repository Interface 
  * Repository Implementation 
  * Dependency Inversion Principle (DIP) 
  * CRUD chuẩn 
  * Mapper 
  * Repository và ORM khác nhau thế nào 
  * Repository trong app crawler 



* * *

# 1\. Vấn đề khi không dùng Repository

Rất nhiều người viết như sau:
    
    
    class StoryService:
    
        def get_story(self, story_id):
    
            conn = sqlite3.connect("story.db")
    
            cursor = conn.cursor()
    
            cursor.execute(
                "SELECT * FROM story WHERE id=?",
                (story_id,)
            )
    
            row = cursor.fetchone()
    
            conn.close()
    
            return row

Thoạt nhìn có vẻ ổn.

Nhưng thực tế Service đang làm quá nhiều việc:

  * mở database 
  * SQL 
  * chuyển row thành object 
  * xử lý nghiệp vụ 



Điều này vi phạm **Single Responsibility Principle (SRP)**.

* * *

# 2\. Kiến trúc đúng
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository
     │
     ▼
    SQLite

Service chỉ nói:

> "Cho tôi Story có id = 10"

Nó không quan tâm dữ liệu đến từ đâu.

* * *

# 3\. Repository là gì?

Repository giống như một "thủ thư".

Ví dụ:

Bạn hỏi:

> Cho tôi truyện Đấu La Đại Lục.

Bạn không quan tâm:

  * lấy từ SQLite 
  * PostgreSQL 
  * Redis 
  * Cache 
  * File JSON 



Repository sẽ làm việc đó.

* * *

# 4\. Interface đầu tiên

Ta tạo interface.
    
    
    domain/
    
        repositories/
    
            story_repository.py
    
    
    from abc import ABC
    from abc import abstractmethod
    
    from app.domain.entities.story import Story
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        def get_by_id(self, story_id: int) -> Story | None:
            ...
    
        @abstractmethod
        def save(self, story: Story) -> None:
            ...
    
        @abstractmethod
        def delete(self, story_id: int) -> None:
            ...

Đây gọi là **Repository Interface**.

* * *

# 5\. Vì sao dùng Interface?

Giả sử mai bạn đổi sang PostgreSQL.

Nếu Service viết:
    
    
    sqlite3.connect(...)

Bạn sẽ sửa hàng trăm file.

Nếu Service dùng
    
    
    StoryRepository

Bạn chỉ đổi implementation.

Service không cần sửa.

* * *

# 6\. SQLite Repository
    
    
    infrastructure/
    
        sqlite/
    
            story_repository.py
    
    
    import sqlite3
    
    from app.domain.entities.story import Story
    from app.domain.repositories.story_repository import StoryRepository
    
    
    class SQLiteStoryRepository(StoryRepository):
    
        def __init__(self, db_path: str):
    
            self.db_path = db_path
    
        def get_by_id(self, story_id: int):
    
            ...

Đây gọi là

> Repository Implementation.

* * *

# 7\. Mapper

Database trả về
    
    
    row = (
        1,
        "Đấu La Đại Lục",
        "ongoing"
    )

Nhưng Domain cần
    
    
    Story(...)

Ai chuyển?

Repository.

Ví dụ
    
    
    story = Story(
    
        id=row[0],
    
        title=row[1],
    
        status=StoryStatus(row[2])
    )

Đây gọi là **Data Mapper**.

* * *

# 8\. Không trả về tuple

Sai
    
    
    return row

Sai tiếp
    
    
    return dict(row)

Đúng
    
    
    return Story(...)

Service chỉ làm việc với Domain Model.

Không bao giờ biết tuple là gì.

* * *

# 9\. Repository CRUD

Repository tối thiểu nên có
    
    
    get_by_id()
    
    save()
    
    delete()
    
    exists()

Sau đó mở rộng
    
    
    list()
    
    count()
    
    search()
    
    update()
    
    find_by_slug()
    
    find_by_url()

* * *

# 10\. Save nghĩa là gì?

Không nên có
    
    
    insert()
    
    update()

Service sẽ phải quyết định.

Đúng hơn
    
    
    save(story)

Repository sẽ tự quyết định
    
    
    id=None
    
    ↓
    
    INSERT
    
    ------------------
    
    id!=None
    
    ↓
    
    UPDATE

Service không cần biết.

* * *

# 11\. Ví dụ Save
    
    
    story = Story.create(...)
    
    repository.save(story)

Lần đầu

↓

INSERT

Sau này
    
    
    story.rename("Tên mới")
    
    repository.save(story)

↓

UPDATE

* * *

# 12\. Delete

Sai
    
    
    DELETE

Trong app crawler.

Đúng hơn
    
    
    story.mark_deleted()
    
    repository.save(story)

Repository cập nhật
    
    
    deleted_at

Không mất dữ liệu.

* * *

# 13\. Exists

Rất hữu ích.
    
    
    if repository.exists(slug):
    
        ...

Không cần
    
    
    SELECT *

Chỉ cần
    
    
    SELECT 1

Nhanh hơn.

* * *

# 14\. Find By Slug

Ví dụ
    
    
    https://truyenfull.vn/
    
    dau-la-dai-luc

Repository
    
    
    story = repository.find_by_slug(
        "dau-la-dai-luc"
    )

Không cần Service viết SQL.

* * *

# 15\. Find By URL

Crawler thường cần
    
    
    find_by_url(url)

Nếu đã tồn tại

↓

update

Nếu chưa

↓

insert

* * *

# 16\. Repository chỉ làm một việc

Repository chỉ làm
    
    
    Database
    ⇅
    Domain

Không làm
    
    
    requests.get()

Không làm
    
    
    BeautifulSoup()

Không làm
    
    
    lxml

Không download ảnh.

Không crawl.

* * *

# 17\. Crawler sử dụng Repository

Ví dụ
    
    
    Crawler
    
    ↓
    
    HTML
    
    ↓
    
    Parser
    
    ↓
    
    Story
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Parser tạo Domain Model.

Repository lưu.

Parser không biết SQLite.

* * *

# 18\. Service sử dụng Repository
    
    
    class StoryService:
    
        def __init__(
            self,
            repository: StoryRepository
        ):
    
            self.repository = repository
    
        def rename_story(
            self,
            story_id,
            title
        ):
    
            story = self.repository.get_by_id(story_id)
    
            story.rename(title)
    
            self.repository.save(story)

Đây là Dependency Injection.

* * *

# 19\. InMemory Repository

Đây là vũ khí cực mạnh khi test.
    
    
    class MemoryStoryRepository(
        StoryRepository
    ):
    
        def __init__(self):
    
            self.data = {}

Không SQLite.

Không file.

Không database.

Chỉ RAM.

Unit Test sẽ cực nhanh.

* * *

# 20\. Fake Repository

Ví dụ
    
    
    repo = MemoryStoryRepository()
    
    service = StoryService(repo)

Không cần SQLite.

Không cần Docker.

Không cần PostgreSQL.

Đây là cách kiểm thử business logic độc lập với hạ tầng.

* * *

# 21\. Cấu trúc thư mục
    
    
    app/
    
    domain/
    
        repositories/
    
            story_repository.py
    
            chapter_repository.py
    
    infrastructure/
    
        sqlite/
    
            story_repository.py
    
            chapter_repository.py
    
        memory/
    
            story_repository.py
    
    services/
    
        story_service.py

Đây là cấu trúc rất phổ biến trong Clean Architecture.

* * *

# 22\. Luồng hoạt động hoàn chỉnh
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository (Interface)
     │
     ▼
    SQLiteStoryRepository
     │
     ▼
    SQLite Database

Nếu mai chuyển PostgreSQL:
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository
     │
     ▼
    PostgresStoryRepository
     │
     ▼
    PostgreSQL

`StoryService` không thay đổi.

* * *

# 23\. Repository và ORM khác nhau thế nào?

Repository| ORM  
---|---  
Là một pattern kiến trúc| Là công cụ ánh xạ Object ↔ Database  
Ẩn chi tiết lưu trữ| Sinh SQL và quản lý entity  
Service chỉ biết interface| Service có thể phụ thuộc trực tiếp ORM nếu thiết kế không tốt  
Có thể dùng với sqlite3 thuần, SQLAlchemy, Tortoise, REST API...| Thường gắn với một ORM cụ thể  
  
Nhiều dự án lớn vẫn dùng SQLAlchemy bên trong **Repository** , thay vì để Service gọi SQLAlchemy trực tiếp.

* * *

# 24\. Sai lầm phổ biến

❌ Repository trả về `sqlite3.Row`

❌ Repository trả về `dict`

❌ Repository chứa business logic (`if chapter_count > ...`)

❌ Service viết SQL

❌ GUI gọi Repository trực tiếp

Nguyên tắc:
    
    
    GUI
       ↓
    Service
       ↓
    Repository
       ↓
    Database

GUI không nên bỏ qua Service để truy cập Repository, vì như vậy business rule sẽ bị phân tán.

* * *

# Bài tập

## Bài 1

Thiết kế interface cho:

  * `StoryRepository`
  * `ChapterRepository`
  * `AuthorRepository`



Mỗi interface cần có:

  * `get_by_id()`
  * `save()`
  * `delete()`
  * `exists()`
  * `list()`



* * *

## Bài 2

Viết `MemoryStoryRepository` sử dụng `dict[int, Story]` để lưu dữ liệu trong RAM.

Yêu cầu:

  * hỗ trợ `save()`
  * `get_by_id()`
  * `delete()`
  * `exists()`
  * `list()`



* * *

## Bài 3

Viết `StoryService` chỉ làm việc với `StoryRepository` (interface), không import `sqlite3`.

Thử thay thế `MemoryStoryRepository` bằng một `SQLiteStoryRepository` giả lập để thấy rằng `StoryService` không cần thay đổi.

* * *

## Bài 4 (nâng cao)

Với `ChapterRepository`, hãy đề xuất các phương thức đặc thù cho ứng dụng crawler, ví dụ:

  * `find_by_story_id(story_id)`
  * `find_by_index(story_id, index)`
  * `find_latest(story_id)`
  * `find_missing_indices(story_id)`
  * `bulk_save(chapters)`



Giải thích phương thức nào nên có trong **Repository chung** và phương thức nào chỉ nên xuất hiện trong **Repository dành riêng cho Chapter**.

* * *

## Chuẩn bị cho Buổi 5

Buổi tiếp theo chúng ta sẽ xây dựng **Generic Repository** – một lớp `BaseRepository[T]` dùng `Generic`, `TypeVar` và `ABC` để tái sử dụng phần lớn mã CRUD cho mọi Entity (`Story`, `Chapter`, `Author`, `Genre`...), đồng thời vẫn cho phép mỗi Repository bổ sung các phương thức đặc thù của riêng mình. Đây là bước quan trọng để giảm lặp mã trong các dự án Python lớn.

