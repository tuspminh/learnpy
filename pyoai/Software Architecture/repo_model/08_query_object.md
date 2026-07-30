Rất đúng. Sau 7 buổi, chúng ta đang đi hơi sâu vào kiến trúc. Mình sẽ **nhắc lại roadmap tổng thể** để tránh lan man và đảm bảo mỗi buổi đều phục vụ trực tiếp cho **app cào truyện**.

# Roadmap hoàn chỉnh: Thiết kế Model & Repository cho App Cào Truyện

## Phần I — Domain Analysis (2 buổi)

✅ **Buổi 1** : Phân tích Domain

  * Domain Model 
  * Entity 
  * Value Object 
  * Aggregate 
  * Quan hệ giữa các Entity 



✅ **Buổi 2** : Thiết kế Database

  * ERD 
  * Chuẩn hóa dữ liệu 
  * PK/FK 
  * Index 
  * Constraint 
  * Thiết kế bảng cho app crawler 



* * *

## Phần II — Domain Model (1 buổi)

✅ **Buổi 3** : Thiết kế Domain Model

  * Dataclass 
  * Enum 
  * Validation 
  * Factory Method 
  * Aggregate Root 
  * Business Rule 



* * *

## Phần III — Repository Foundation (5 buổi)

✅ **Buổi 4** : Repository Pattern

  * Repository Interface 
  * Repository Implementation 
  * Dependency Injection 



✅ **Buổi 5** : Generic Repository

  * Generic 
  * BaseRepository 
  * Generic CRUD 



✅ **Buổi 6** : Mapper Pattern

  * Entity ↔ Record 
  * BaseMapper 
  * Aggregate Mapper 



✅ **Buổi 7** : Unit Of Work

  * DatabaseSession 
  * Transaction 
  * Commit 
  * Rollback 



* * *

# Chúng ta đang ở đây

⬇⬇⬇

## Phần IV — Repository nâng cao

### Buổi 8 (Hôm nay)

# Query Specification Pattern

Đây là chủ đề cực kỳ quan trọng.

Sau buổi này chúng ta sẽ **không bao giờ phải viết**
    
    
    find_by_slug()
    
    find_by_title()
    
    find_by_author()
    
    find_by_status()
    
    find_by_genre()
    
    find_by_source()
    
    find_by_created()
    
    find_by_updated()
    
    find_by_keyword()

nữa.

Thay vào đó chỉ cần
    
    
    repository.find(specification)

* * *

### Buổi 9

Pagination

Sorting

Filtering

Cursor Pagination

Offset Pagination

* * *

### Buổi 10

Bulk Insert

Bulk Update

Bulk Delete

Batch Processing

Tối ưu cho crawler.

* * *

### Buổi 11

Async Repository

aiosqlite

Async Transaction

* * *

### Buổi 12

Cache Repository

Memory Cache

Redis Cache

TTL

* * *

## Phần V — Repository cho App Crawler

### Buổi 13

StoryRepository chuyên nghiệp

* * *

### Buổi 14

ChapterRepository

Đây là Repository lớn nhất.

Ví dụ
    
    
    find_latest()
    
    find_missing()
    
    find_range()
    
    bulk_save()
    
    find_after()

* * *

### Buổi 15

CrawlerRepository

Quản lý Job

Queue

Retry

* * *

### Buổi 16

Plugin Repository
    
    
    TruyenFullRepository
    
    NovelBinRepository
    
    TangThuVienRepository
    
    WikiDichRepository

* * *

### Buổi 17

Repository Factory

Tự động chọn Repository theo Source.

* * *

## Phần VI — Service Layer

### Buổi 18

StoryService

* * *

### Buổi 19

CrawlerService

* * *

### Buổi 20

BookmarkService

HistoryService

* * *

## Phần VII — Testing

### Buổi 21

Fake Repository

Memory Repository

* * *

### Buổi 22

Unit Test

Integration Test

* * *

## Phần VIII — Kiến trúc hoàn chỉnh

### Buổi 23

Clean Architecture

* * *

### Buổi 24

DDD Lite

* * *

### Buổi 25

Xây dựng toàn bộ Repository Layer cho App Cào Truyện

Từ đầu đến cuối.

* * *

# Buổi 8

# Query Specification Pattern Deep Dive

Đây là một Pattern xuất hiện rất nhiều trong:

  * Domain-Driven Design (DDD) 
  * CQRS 
  * Enterprise Java 
  * .NET 
  * SQLAlchemy (có tư duy tương tự với các biểu thức truy vấn) 
  * Các hệ thống ERP/CRM lớn 



Mục tiêu là **đóng gói điều kiện truy vấn thành các đối tượng** , thay vì tạo vô số phương thức trong Repository.

* * *

# 1\. Vấn đề

Giả sử `StoryRepository` có:
    
    
    find_by_slug()
    
    find_by_title()
    
    find_by_status()
    
    find_by_source()
    
    find_by_author()
    
    find_by_genre()
    
    find_by_tag()
    
    find_by_keyword()
    
    find_by_created_after()
    
    find_by_updated_after()
    
    find_hot_story()
    
    find_completed_story()
    
    find_ongoing_story()

Sau một thời gian:
    
    
    StoryRepository
    
    ↓
    
    200 methods

Repository trở thành một "God Class", rất khó bảo trì.

* * *

# 2\. Ý tưởng của Specification

Thay vì:
    
    
    repo.find_by_status("ongoing")

Ta tạo:
    
    
    spec = StoryStatusSpecification(
        StoryStatus.ONGOING
    )
    
    stories = repo.find(spec)

Repository chỉ cần biết:
    
    
    find(specification)

* * *

# 3\. Interface Specification
    
    
    from abc import ABC, abstractmethod
    from typing import Generic, TypeVar
    
    T = TypeVar("T")
    
    
    class Specification(ABC, Generic[T]):
    
        @abstractmethod
        def is_satisfied_by(
            self,
            candidate: T
        ) -> bool:
            ...

Đây là một điều kiện có thể áp dụng cho bất kỳ Entity nào.

* * *

# 4\. Ví dụ: StoryStatusSpecification
    
    
    class StoryStatusSpecification(
        Specification[Story]
    ):
    
        def __init__(self, status):
    
            self.status = status
    
        def is_satisfied_by(
            self,
            story: Story
        ) -> bool:
    
            return story.status == self.status

Dùng với `MemoryRepository`:
    
    
    stories = [
        s
        for s in repo.list()
        if spec.is_satisfied_by(s)
    ]

* * *

# 5\. StoryTitleSpecification
    
    
    class StoryTitleSpecification(
        Specification[Story]
    ):
    
        def __init__(self, keyword: str):
    
            self.keyword = keyword.lower()
    
        def is_satisfied_by(
            self,
            story: Story
        ) -> bool:
    
            return self.keyword in story.title.lower()

Không cần thêm `find_by_title()` nữa.

* * *

# 6\. Kết hợp Specification

Điểm mạnh nhất là có thể ghép điều kiện.

Ví dụ:

  * đang cập nhật (`ONGOING`) 
  * thuộc nguồn TruyenFull 
  * có chữ "Đấu La" 



Thay vì viết:
    
    
    find_ongoing_truyenfull_title_contains(...)

Ta kết hợp các Specification.

* * *

# 7\. AndSpecification
    
    
    class AndSpecification(
        Specification[T]
    ):
    
        def __init__(self, *specs):
    
            self.specs = specs
    
        def is_satisfied_by(self, obj):
    
            return all(
                spec.is_satisfied_by(obj)
                for spec in self.specs
            )

Sử dụng:
    
    
    spec = AndSpecification(
        StoryStatusSpecification(
            StoryStatus.ONGOING
        ),
        StoryTitleSpecification("đấu la")
    )

* * *

# 8\. OrSpecification
    
    
    return any(
        spec.is_satisfied_by(obj)
        for spec in self.specs
    )

Ví dụ:

  * Tiên hiệp **hoặc**
  * Huyền huyễn 



* * *

# 9\. NotSpecification
    
    
    return not self.spec.is_satisfied_by(obj)

Ví dụ:
    
    
    NOT COMPLETED

Tức là lấy tất cả truyện chưa hoàn thành.

* * *

# 10\. Repository thay đổi

Thay vì:
    
    
    find_by_status(...)
    find_by_title(...)
    find_by_source(...)

Chỉ cần:
    
    
    find(
        specification
    )

Đối với `MemoryRepository`, `find()` có thể lọc bằng `is_satisfied_by()`. Với `SQLiteRepository`, cùng một `Specification` có thể được chuyển thành `WHERE` tương ứng (thông qua một lớp chuyển đổi ở tầng Infrastructure).

* * *

# 11\. Không để Specification sinh SQL

Một sai lầm phổ biến là:
    
    
    class StoryStatusSpecification:
    
        def to_sql():
            ...

Điều này làm tầng Domain phụ thuộc vào SQLite.

Đúng hơn:

  * **Domain** : `is_satisfied_by()`
  * **Infrastructure** : nếu cần tối ưu, tạo `SQLiteSpecificationTranslator` để chuyển Specification thành câu lệnh SQL. 



Nhờ đó Domain vẫn thuần túy và có thể tái sử dụng với `MemoryRepository` hoặc các nguồn dữ liệu khác.

* * *

# Cấu trúc sau Buổi 8
    
    
    domain/
    ├── entities/
    ├── repositories/
    ├── specifications/
    │   ├── base.py
    │   ├── story_status.py
    │   ├── story_title.py
    │   ├── and_specification.py
    │   ├── or_specification.py
    │   └── not_specification.py
    │
    infrastructure/
    ├── sqlite/
    ├── mappers/
    └── query/
        └── sqlite_specification_translator.py

* * *

# Bài tập

### Bài 1

Viết các Specification sau:

  * `StoryStatusSpecification`
  * `StoryTitleSpecification`
  * `StorySourceSpecification`



Tất cả đều kế thừa `Specification[Story]`.

* * *

### Bài 2

Viết:

  * `AndSpecification`
  * `OrSpecification`
  * `NotSpecification`



để có thể kết hợp nhiều điều kiện.

* * *

### Bài 3

Nâng cấp `MemoryStoryRepository.find(specification)` để lọc dữ liệu bằng `specification.is_satisfied_by()`.

* * *

### Bài 4 (nâng cao)

Thiết kế `SQLiteSpecificationTranslator` nhận một `Specification` và tạo:

  * `WHERE` clause 
  * danh sách tham số (`params`) 



để `SQLiteStoryRepository` có thể thực hiện truy vấn trực tiếp trên database mà vẫn giữ Domain độc lập với SQL.

* * *

> **Lưu ý:** Từ **Buổi 9** trở đi, chúng ta sẽ chuyển sang tối ưu các truy vấn với **Pagination, Sorting và Filtering**. Những kiến thức này sẽ kết hợp với Specification để tạo nên một tầng truy cập dữ liệu linh hoạt và mạnh mẽ, rất phù hợp cho ứng dụng crawler truyện có hàng trăm nghìn truyện và hàng triệu chương.

