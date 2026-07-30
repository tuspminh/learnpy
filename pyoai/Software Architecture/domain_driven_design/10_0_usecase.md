# Domain-Driven Design Deep Dive

# Buổi 10 (Roadmap cập nhật): Application Layer và Use Case trong DDD

Sau khi đã học:

  * Domain 
  * Entity 
  * Value Object 
  * Aggregate 
  * Aggregate Root 



chúng ta đã xây dựng được **trái tim của hệ thống**.

Nhưng còn một câu hỏi:

> Ai sẽ gọi Domain Model? Ai điều phối quy trình nghiệp vụ? Ai nhận request từ UI/API rồi đưa vào Domain?

Câu trả lời:

# Application Layer + Use Case

Đây là phần cực kỳ quan trọng khi chuyển từ học DDD lý thuyết sang xây dựng ứng dụng Python thật.

* * *

# 1\. Kiến trúc tổng quan DDD

Một hệ thống DDD thường chia thành:
    
    
                    Presentation Layer
    
                 UI / API / CLI / GUI
    
                         |
                         v
    
                  Application Layer
    
                  Use Case
                  Application Service
                  DTO
    
                         |
                         v
    
                    Domain Layer
    
           Entity
           Aggregate
           Value Object
           Domain Service
           Domain Event
    
                         |
                         v
    
                Infrastructure Layer
    
           Database
           File
           HTTP
           Message Queue

* * *

# 2\. Application Layer là gì?

Định nghĩa:

> Application Layer điều phối các hoạt động của hệ thống nhưng không chứa business rule.

Nó trả lời câu hỏi:

> Người dùng muốn làm việc gì?

Ví dụ:

Người dùng:

"Thêm truyện mới"

Application Layer:
    
    
    CreateNovelUseCase

sẽ:

  1. Nhận dữ liệu. 
  2. Gọi Factory. 
  3. Tạo Aggregate. 
  4. Lưu Repository. 
  5. Trả kết quả. 



* * *

# 3\. Domain Layer khác Application Layer thế nào?

Đây là điểm rất nhiều người nhầm.

* * *

## Domain Layer

Chứa:

"Luật nghiệp vụ"

Ví dụ:

Novel:
    
    
    class Novel:
    
        def publish(self):
    
            if not self.chapters:
                raise Exception(
                    "Cannot publish empty novel"
                )
    
            self.status = "published"

* * *

Đây là business rule.

Thuộc Domain.

* * *

## Application Layer

Chứa:

"Luồng xử lý"

Ví dụ:
    
    
    class PublishNovelUseCase:
    
        def execute(
            self,
            novel_id
        ):
    
            novel = repository.get(
                novel_id
            )
    
            novel.publish()
    
            repository.save(
                novel
            )

* * *

Nó không quyết định:

"Bao nhiêu chapter thì được publish?"

Nó chỉ điều phối.

* * *

# 4\. Use Case là gì?

Use Case biểu diễn một hành động mà hệ thống cung cấp.

Ví dụ App Cào Truyện:

## Crawler
    
    
    Start Crawl
    Stop Crawl
    Import Novel
    Import Chapter

* * *

## Library
    
    
    Create Novel
    Update Novel
    Delete Novel
    Publish Novel

* * *

## Reader
    
    
    Start Reading
    Bookmark Chapter
    Complete Novel

* * *

Mỗi hành động:

=> Một Use Case.

* * *

# 5\. Use Case không phải Function CRUD

Nhiều lập trình viên tạo:
    
    
    NovelService
    
    create()
    update()
    delete()

Đây là CRUD.

DDD muốn:
    
    
    CreateNovelUseCase
    
    PublishNovelUseCase
    
    ArchiveNovelUseCase

Vì mỗi cái có ý nghĩa nghiệp vụ.

* * *

Ví dụ:

Sai:
    
    
    novel.update(
        status="published"
    )

Ai cũng có thể update.

* * *

Đúng:
    
    
    publish_novel.execute()

Use Case kiểm soát quy trình.

* * *

# 6\. Ví dụ hoàn chỉnh: Create Novel

Giả sử App Cào Truyện.

Người dùng thêm nguồn truyện mới.

* * *

## Domain Entity
    
    
    class Novel:
    
    
        def __init__(
            self,
            novel_id,
            title
        ):
    
            self.id = novel_id
            self.title = title
            self.status = "draft"
    
    
    
        def publish(self):
    
            self.status = "published"

* * *

# 7\. Repository Interface

Domain định nghĩa:
    
    
    from abc import ABC, abstractmethod
    
    
    class NovelRepository(ABC):
    
    
        @abstractmethod
        def save(
            self,
            novel
        ):
            pass
    
    
        @abstractmethod
        def get_by_id(
            self,
            novel_id
        ):
            pass

* * *

# 8\. Factory

Tạo Novel hợp lệ:
    
    
    import uuid
    
    
    class NovelFactory:
    
    
        def create(
            self,
            title
        ):
    
            if not title:
                raise ValueError(
                    "Title required"
                )
    
    
            return Novel(
                str(uuid.uuid4()),
                title
            )

* * *

# 9\. CreateNovelUseCase

Đây là Application Layer.
    
    
    class CreateNovelUseCase:
    
    
        def __init__(
            self,
            factory,
            repository
        ):
    
            self.factory = factory
            self.repository = repository
    
    
    
        def execute(
            self,
            title
        ):
    
            novel = (
                self.factory.create(
                    title
                )
            )
    
    
            self.repository.save(
                novel
            )
    
    
            return novel

* * *

Luồng chạy:
    
    
    User nhập:
    
    "Đấu Phá Thương Khung"
    
    
            |
    
            v
    
    
    CreateNovelUseCase
    
    
            |
    
            v
    
    
    NovelFactory
    
    
            |
    
            v
    
    
    Novel Aggregate
    
    
            |
    
            v
    
    
    NovelRepository
    
    
            |
    
            v
    
    
    Database

* * *

# 10\. DTO trong Application Layer

Application không nên nhận trực tiếp Entity.

Ví dụ:

Không:
    
    
    create_novel(
        Novel(...)
    )

* * *

Nên:

Input DTO:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class CreateNovelRequest:
    
        title: str
        source_id: int

* * *

Output DTO:
    
    
    @dataclass
    class NovelResponse:
    
        id: str
        title: str
        status: str

* * *

# 11\. Vì sao cần DTO?

Ví dụ UI:

PySide6:
    
    
    {
    "title":
    "Truyện A"
    }

API:
    
    
    {
    "title":"Truyện A",
    "source":1
    }

Database:
    
    
    novels
    
    id
    title
    source_id

* * *

Không nên để các layer phụ thuộc nhau.

DTO là lớp chuyển đổi.

* * *

# 12\. Application Service

Một số tài liệu gọi:
    
    
    Use Case
    
    =
    Application Service

Ví dụ:
    
    
    class ImportChapterService:

hoặc:
    
    
    class ImportChapterUseCase:

Tên không quan trọng bằng trách nhiệm.

* * *

# 13\. Một Use Case lớn hơn

Ví dụ:

Import Novel từ crawler.

Luồng:
    
    
    Crawler phát hiện truyện mới
    
    
            |
    
    ImportNovelUseCase
    
    
            |
    
    Kiểm tra tồn tại
    
    
            |
    
    Tạo Novel Aggregate
    
    
            |
    
    Lưu Database
    
    
            |
    
    Phát Domain Event
    
    NovelCreated

* * *

Code:
    
    
    class ImportNovelUseCase:
    
    
        def __init__(
            self,
            repository,
            factory,
            event_bus
        ):
    
            self.repository = repository
            self.factory = factory
            self.event_bus = event_bus
    
    
    
        def execute(
            self,
            title
        ):
    
            novel = (
                self.factory.create(
                    title
                )
            )
    
    
            self.repository.save(
                novel
            )
    
    
            self.event_bus.publish(
                NovelCreated(
                    novel.id
                )
            )

* * *

# 14\. Use Case và Transaction

Ví dụ:

Tạo truyện:
    
    
    1. Save Novel
    
    2. Save Chapter
    
    3. Update Source

Nếu bước 3 lỗi?

Cần:
    
    
    Rollback

Sau này học:
    
    
    Unit Of Work

* * *

# 15\. Use Case trong App Cào Truyện

Tôi sẽ thiết kế như sau:
    
    
    application/
    
        novels/
    
            create_novel.py
            publish_novel.py
            delete_novel.py
    
    
        chapters/
    
            import_chapter.py
            merge_chapter.py
    
    
        crawler/
    
            start_crawl.py
            stop_crawl.py

* * *

Ví dụ:

## Start Crawl
    
    
    class StartCrawlUseCase:
    
    
        def execute(
            self,
            source_id
        ):
    
            source = (
                self.source_repo.get(
                    source_id
                )
            )
    
    
            source.start_crawl()
    
    
            self.source_repo.save(
                source
            )

* * *

# 16\. Controller không nên chứa logic

Sai:
    
    
    def create_novel(request):
    
        title=request.title
    
        if title:
            save_database()

* * *

Controller chỉ:
    
    
    def create_novel(request):
    
        use_case.execute(
            request.title
        )

* * *

# 17\. Testing Use Case

Ví dụ:
    
    
    def test_create_novel():
    
    
        repo = MemoryNovelRepository()
    
        factory = NovelFactory()
    
    
        use_case = CreateNovelUseCase(
            factory,
            repo
        )
    
    
        novel = use_case.execute(
            "Truyện ABC"
        )
    
    
        assert novel.title == "Truyện ABC"

* * *

Không cần:

  * SQLite 
  * API 
  * UI 



* * *

# 18\. Cấu trúc Project Python thực tế
    
    
    src/
    
    ├── domain/
    │
    │   ├── novels/
    │   │
    │   ├── entities/
    │   ├── value_objects/
    │   ├── events/
    │   └── repositories/
    │
    
    
    ├── application/
    │
    │   ├── use_cases/
    │   │
    │   │   ├── create_novel.py
    │   │   ├── publish_novel.py
    │   │
    │   └── dto/
    
    
    ├── infrastructure/
    │
    │   ├── sqlite/
    │   ├── repositories/
    │   └── http/
    
    
    └── presentation/
    
        ├── api/
        └── gui/

* * *

# 19\. Những lỗi phổ biến

## Lỗi 1: Đưa business logic vào Use Case

Sai:
    
    
    if chapter_count > 3:
        publish()

Rule này thuộc:
    
    
    Novel Aggregate

* * *

## Lỗi 2: Entity quá ngu

Sai:
    
    
    class Novel:
    
        title
        status

chỉ chứa dữ liệu.

* * *

DDD muốn:
    
    
    class Novel:
    
        publish()
        rename()
        archive()

* * *

## Lỗi 3: Một Use Case làm quá nhiều việc

Sai:
    
    
    ManageNovelEverythingUseCase

* * *

Nên:
    
    
    CreateNovelUseCase
    
    PublishNovelUseCase
    
    ArchiveNovelUseCase

* * *

# 20\. Tổng kết Buổi 10

Cần nhớ:

  * Application Layer điều phối. 
  * Use Case đại diện hành động của hệ thống. 
  * Use Case không chứa business rule. 
  * Domain chứa luật nghiệp vụ. 
  * Repository được Use Case sử dụng. 
  * DTO giúp các layer không phụ thuộc nhau. 
  * Controller/UI chỉ gọi Use Case. 



* * *

Kiến trúc hiện tại:
    
    
                 Presentation
    
                      |
                      v
    
              Application Layer
    
            Use Case + DTO
    
                      |
                      v
    
                 Domain Layer
    
     Entity
     Value Object
     Aggregate
     Domain Service
     Domain Event
    
                      |
                      v
    
              Infrastructure
    
     Database / API / File

* * *

Buổi tiếp theo theo roadmap:

# Buổi 11: Repository Pattern trong DDD (bản cập nhật)

Chúng ta sẽ học sâu hơn:

  * Repository Interface nằm ở đâu? 
  * Repository khác DAO thế nào? 
  * Repository với Aggregate Root. 
  * Repository + Unit Of Work. 
  * Repository thực tế bằng Python + SQLite cho App Cào Truyện.

