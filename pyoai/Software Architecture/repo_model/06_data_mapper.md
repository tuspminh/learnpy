# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 6 - Data Mapper Pattern & Repository Implementation Deep Dive

> Sau buổi này, bạn sẽ hiểu vì sao trong các dự án lớn (SQLAlchemy, Hibernate, Doctrine, Entity Framework...), **Mapper** là một thành phần rất quan trọng. Repository sẽ không còn phải tự tay gán từng cột của database sang object nữa.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Data Mapper là gì 
  * Mapper khác ORM thế nào 
  * Row → Entity 
  * Entity → Row 
  * Repository chỉ còn làm việc với Mapper 
  * Tổ chức thư mục Mapper 
  * Generic Mapper 
  * Mapper cho quan hệ 1-N và N-N 
  * Mapper trong app crawler truyện 



* * *

# 1\. Vấn đề khi không có Mapper

Giả sử trong `SQLiteStoryRepository`:
    
    
    def get_by_id(self, story_id: int):
    
        cursor.execute(
            """
            SELECT
                id,
                title,
                slug,
                status
            FROM story
            WHERE id=?
            """,
            (story_id,)
        )
    
        row = cursor.fetchone()
    
        return Story(
            id=row[0],
            title=row[1],
            slug=row[2],
            status=StoryStatus(row[3])
        )

Thoạt nhìn không có vấn đề.

Nhưng...

* * *

Giả sử Story có
    
    
    20 field

Repository sẽ dài.

Nếu có
    
    
    Story
    
    Chapter
    
    Author
    
    Genre
    
    Bookmark
    
    History

Bạn sẽ viết hàng nghìn dòng code chỉ để gán dữ liệu.

* * *

# 2\. Ý tưởng của Mapper

Repository không nên biết cách tạo Story.

Repository chỉ nên nói
    
    
    Database
    
    ↓
    
    Mapper
    
    ↓
    
    Story

* * *

# 3\. StoryMapper

Ta tạo
    
    
    app/
    
    infrastructure/
    
        mappers/
    
            story_mapper.py

Đây là nơi duy nhất biết
    
    
    SQLite Row
    
    ↓
    
    Story

* * *

# 4\. Row → Entity
    
    
    class StoryMapper:
    
        @staticmethod
        def to_entity(row) -> Story:
    
            return Story(
                id=row["id"],
                title=row["title"],
                slug=row["slug"],
                summary=row["summary"],
                cover=row["cover"],
                status=StoryStatus(row["status"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )

Repository không còn phải tự gán từng field nữa.

* * *

# 5\. Entity → Dictionary

Ngược lại
    
    
    Story
    
    ↓
    
    SQLite
    
    
    class StoryMapper:
    
        @staticmethod
        def to_record(story: Story):
    
            return {
    
                "id": story.id,
    
                "title": story.title,
    
                "slug": story.slug,
    
                "summary": story.summary,
    
                "cover": story.cover,
    
                "status": story.status.value,
    
                "created_at": story.created_at,
    
                "updated_at": story.updated_at
            }

Lưu ý dùng `.value` khi chuyển `Enum` sang dữ liệu lưu trữ.

* * *

# 6\. Repository trở nên rất sạch

Thay vì
    
    
    return Story(
        ...
    )

Giờ chỉ còn
    
    
    return StoryMapper.to_entity(row)

Save
    
    
    record = StoryMapper.to_record(story)

Repository chỉ lo SQL.

Mapper lo chuyển đổi.

* * *

# 7\. Mapper không phải ORM

Nhiều người nhầm.

ORM
    
    
    Object
    
    ↓
    
    SQL

Mapper
    
    
    Object
    
    ↓
    
    Dictionary
    
    ↓
    
    Row

Mapper chỉ chuyển đổi dữ liệu.

Không sinh SQL.

Không quản lý transaction.

Không quản lý connection.

* * *

# 8\. Mapper cho Chapter
    
    
    class ChapterMapper:
    
        @staticmethod
        def to_entity(row):
    
            return Chapter(
                id=row["id"],
                story_id=row["story_id"],
                index=row["index"],
                title=row["title"],
                url=row["url"],
                content=row["content"]
            )

Rất giống Story.

* * *

# 9\. Mapper cho Author
    
    
    class AuthorMapper:
    
        @staticmethod
        def to_entity(row):
    
            return Author(
    
                id=row["id"],
    
                name=row["name"]
            )

* * *

# 10\. Mapper không chứa SQL

Sai
    
    
    class StoryMapper:
    
        def get_story():
    
            SELECT ...

Mapper không truy cập database.

Chỉ chuyển đổi dữ liệu.

* * *

# 11\. Repository sau khi dùng Mapper
    
    
    SELECT
    
    ↓
    
    Row
    
    ↓
    
    Mapper
    
    ↓
    
    Story
    
    ↓
    
    Service

Chiều ngược lại
    
    
    Story
    
    ↓
    
    Mapper
    
    ↓
    
    Dictionary
    
    ↓
    
    SQL
    
    ↓
    
    SQLite

* * *

# 12\. Generic Mapper

Ta nhận ra

mọi Mapper đều có
    
    
    to_entity()
    
    to_record()

Ta tạo
    
    
    class BaseMapper(Generic[T]):
    
        def to_entity(...):
            ...
    
        def to_record(...):
            ...

StoryMapper kế thừa.

ChapterMapper kế thừa.

* * *

# 13\. Quan hệ 1-N

Ví dụ

Story

↓

Chapter

Database
    
    
    Story
    
    1
    
    ↓
    
    N
    
    Chapter

Mapper không nên tự động load Chapter.

Sai
    
    
    StoryMapper
    
    ↓
    
    SELECT chapter

Mapper chỉ map Story.

Loading quan hệ là trách nhiệm của Repository hoặc Service.

* * *

# 14\. Quan hệ N-N

Ví dụ

Story

↓

Genre

Có bảng
    
    
    story_genre

StoryMapper không nên
    
    
    JOIN
    
    ↓
    
    Genre
    
    ↓
    
    Tag
    
    ↓
    
    Author

Mapper sẽ trở nên rất nặng.

Nên tách riêng.

* * *

# 15\. Lazy Loading

Service

↓

Repository

↓

Story

Khi cần
    
    
    chapters = chapter_repository.find_by_story(story.id)

Không phải lúc nào cũng load hàng nghìn chapter.

Đây là **Lazy Loading**.

* * *

# 16\. Eager Loading

Nếu cần
    
    
    Story
    
    +
    
    Author
    
    +
    
    Genre

Repository có thể dùng JOIN.

Sau đó dùng nhiều Mapper.
    
    
    JOIN
    
    ↓
    
    StoryMapper
    
    ↓
    
    AuthorMapper
    
    ↓
    
    GenreMapper

* * *

# 17\. Mapper không validate

Sai
    
    
    StoryMapper
    
    ↓
    
    if title=="":

Validation nằm ở Domain.

Mapper chỉ chuyển đổi.

Nếu dữ liệu từ database không hợp lệ, Domain Model nên phát hiện khi khởi tạo hoặc Repository nên xử lý lỗi phù hợp.

* * *

# 18\. Thư mục hoàn chỉnh
    
    
    app/
    
    domain/
    
        entities/
    
        repositories/
    
    infrastructure/
    
        sqlite/
    
        mappers/
    
            base_mapper.py
    
            story_mapper.py
    
            chapter_mapper.py
    
            author_mapper.py
    
            genre_mapper.py

* * *

# 19\. Mapper trong app crawler

Crawler

↓

Parser

↓

Story Entity

↓

StoryRepository

↓

StoryMapper

↓

SQLite

Parser không biết SQLite.

Repository không biết HTML.

Mapper không biết Parser.

Mỗi lớp chỉ có một trách nhiệm.

* * *

# 20\. Mapper và DTO

Đừng nhầm
    
    
    Mapper

với
    
    
    DTO

Mapper

↓

Database ↔ Domain

DTO

↓

Domain ↔ GUI/API

Hai khái niệm khác nhau.

* * *

# 21\. Mapper và Value Object

Ví dụ

Domain
    
    
    StoryUrl

Database
    
    
    TEXT

Mapper
    
    
    url = StoryUrl(row["url"])

Ngược lại
    
    
    "url": story.url.value

Mapper là nơi chuyển đổi giữa kiểu dữ liệu của Domain và kiểu dữ liệu của database.

* * *

# 22\. Một Repository hoàn chỉnh
    
    
    SQLite
    
    ↓
    
    sqlite3.Row
    
    ↓
    
    StoryMapper
    
    ↓
    
    Story
    
    ↓
    
    StoryService
    
    ↓
    
    GUI

Khi lưu
    
    
    Story
    
    ↓
    
    StoryMapper
    
    ↓
    
    dict
    
    ↓
    
    INSERT
    
    ↓
    
    SQLite

* * *

# 23\. Sai lầm phổ biến

❌ Mapper mở connection

❌ Mapper commit

❌ Mapper rollback

❌ Mapper parse HTML

❌ Mapper gọi requests

❌ Mapper chứa Business Rule

Mapper chỉ làm
    
    
    A
    
    ↓
    
    B

* * *

# 24\. Kiến trúc sau 6 buổi
    
    
    GUI
     │
     ▼
    Service
     │
     ▼
    Repository
     │
     ▼
    Mapper
     │
     ▼
    SQLite

Mỗi tầng có đúng một nhiệm vụ.

* * *

# Ví dụ thực tế: Lưu một Story mới
    
    
    Crawler
       │
       ▼
    Parser
       │
       ▼
    Story.create(...)
       │
       ▼
    StoryService.save(story)
       │
       ▼
    StoryRepository.save(story)
       │
       ▼
    StoryMapper.to_record(story)
       │
       ▼
    INSERT INTO story (...)
       │
       ▼
    SQLite

Và khi đọc lại:
    
    
    SQLite
       │
       ▼
    SELECT * FROM story
       │
       ▼
    sqlite3.Row
       │
       ▼
    StoryMapper.to_entity(row)
       │
       ▼
    Story
       │
       ▼
    StoryService
       │
       ▼
    GUI

Đây là luồng dữ liệu chuẩn mà bạn sẽ gặp trong rất nhiều dự án lớn.

* * *

# Bài tập

## Bài 1

Viết `StoryMapper` với hai phương thức:

  * `to_entity(row: sqlite3.Row) -> Story`
  * `to_record(story: Story) -> dict[str, object]`



Đảm bảo xử lý đúng các trường `Enum` và `datetime`.

* * *

## Bài 2

Viết `ChapterMapper`, `AuthorMapper` và `GenreMapper` theo cùng một mẫu.

Hãy tìm những phần lặp lại và đề xuất cách tái sử dụng bằng `BaseMapper`.

* * *

## Bài 3

Cập nhật `SQLiteStoryRepository` để:

  * không còn khởi tạo `Story` trực tiếp 
  * sử dụng `StoryMapper`
  * chỉ tập trung vào SQL và transaction. 



* * *

## Bài 4 (nâng cao)

Thiết kế `StoryAggregateMapper` để ánh xạ một `Story` cùng:

  * danh sách `Chapter`
  * danh sách `Author`
  * danh sách `Genre`



Tuy nhiên, hãy phân tích khi nào nên dùng `StoryAggregateMapper` (ví dụ màn hình chi tiết truyện) và khi nào chỉ nên dùng `StoryMapper` (ví dụ danh sách truyện), nhằm tránh tải quá nhiều dữ liệu không cần thiết.

* * *

## Chuẩn bị cho Buổi 7

Ở **Buổi 7** , chúng ta sẽ xây dựng **SQLite Repository hoàn chỉnh** với:

  * `DatabaseSession` quản lý kết nối 
  * `Unit of Work` cơ bản 
  * `commit()` / `rollback()`
  * Repository dùng chung một transaction 
  * quản lý vòng đời kết nối an toàn bằng `Context Manager`



Đây sẽ là bước biến kiến trúc hiện tại thành một hệ thống sẵn sàng cho các thao tác ghi dữ liệu phức tạp của ứng dụng crawler truyện.

