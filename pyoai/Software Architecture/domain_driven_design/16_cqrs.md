# Domain-Driven Design Deep Dive

# Buổi 16: CQRS trong DDD (Command Query Responsibility Segregation)

Sau buổi 15, chúng ta đã học:

  * Specification Pattern 
  * Business Rule dưới dạng Object 
  * Composite Specification 
  * Domain Rule trong DDD 



Hôm nay chúng ta học một kiến trúc rất quan trọng khi hệ thống lớn:

# CQRS

* * *

# 1\. Vấn đề: Một Model phục vụ tất cả

Trong ứng dụng CRUD truyền thống:
    
    
    User
    
     |
     v
    
    Application
    
     |
     v
    
    Database

Một Model làm cả:

  * Ghi dữ liệu. 
  * Đọc dữ liệu. 
  * Tìm kiếm. 
  * Báo cáo. 
  * Thống kê. 



* * *

Ví dụ App Cào Truyện:

Bảng:
    
    
    novels
    chapters
    sources

Dùng chung cho:

## Ghi:

Crawler:
    
    
    INSERT chapter
    UPDATE novel

## Đọc:

Reader:
    
    
    SELECT novel
    SELECT chapter

## Dashboard:
    
    
    COUNT chapters
    GROUP BY source

* * *

Ban đầu:

Ổn.

Nhưng khi dữ liệu lớn:

Ví dụ:
    
    
    10 triệu chapters

Các vấn đề xuất hiện:

  * Query đọc chậm. 
  * Model quá phức tạp. 
  * Database khó tối ưu. 



* * *

CQRS giải quyết:
    
    
    Command Model
    
            +
    
    Query Model

* * *

# 2\. CQRS là gì?

CQRS:

> Command Query Responsibility Segregation

Tách:

  * Phần thay đổi trạng thái. 
  * Phần đọc dữ liệu. 



* * *

Kiến trúc:
    
    
                 User
    
                  |
                  |
    
            +-------------+
    
            |             |
    
        Command       Query
    
        Write          Read
    
            |             |
    
            v             v
    
       Domain        Read Model
    
            |             |
    
         Database    Search DB

* * *

# 3\. Command là gì?

Command:

> Một yêu cầu làm thay đổi hệ thống.

Ví dụ:
    
    
    CreateNovelCommand
    
    PublishNovelCommand
    
    AddChapterCommand

* * *

Command có:

  * Input. 
  * Ý định. 



Không có:

  * Logic. 
  * Database. 



* * *

Ví dụ:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class AddChapterCommand:
    
        novel_id: str
        title: str
        content: str

* * *

Command chỉ là dữ liệu.

* * *

# 4\. Command Handler

Ai xử lý Command?

Command Handler.

Ví dụ:
    
    
    class AddChapterHandler:
    
    
        def __init__(
            self,
            repository
        ):
            self.repository = repository
    
    
    
        def handle(
            self,
            command
        ):
    
            novel = (
                self.repository
                .get_by_id(
                    command.novel_id
                )
            )
    
    
            novel.add_chapter(
                command.title,
                command.content
            )
    
    
            self.repository.save(
                novel
            )

* * *

Luồng:
    
    
    Command
    
       |
    
    Handler
    
       |
    
    Domain
    
       |
    
    Repository
    
       |
    
    Database

* * *

# 5\. Query là gì?

Query:

> Yêu cầu lấy dữ liệu, không thay đổi trạng thái.

Ví dụ:
    
    
    GetNovelDetailQuery
    
    SearchNovelQuery
    
    GetReadingHistoryQuery

* * *

Ví dụ:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class SearchNovelQuery:
    
        keyword: str

* * *

# 6\. Query Handler

Ví dụ:
    
    
    class SearchNovelHandler:
    
    
        def __init__(
            self,
            search_engine
        ):
    
            self.search_engine = search_engine
    
    
    
        def handle(
            self,
            query
        ):
    
            return (
                self.search_engine
                .search(
                    query.keyword
                )
            )

* * *

Query không đi qua Domain.

* * *

Vì:

Đọc dữ liệu không cần:

  * Aggregate. 
  * Business Rule. 



* * *

# 7\. CQRS Flow hoàn chỉnh

Ví dụ:

Crawler thêm chapter.

## Command side
    
    
    Crawler
    
     |
    
    AddChapterCommand
    
     |
    
    Command Handler
    
     |
    
    Novel Aggregate
    
     |
    
    Repository
    
     |
    
    Write Database

* * *

Sau đó phát Event:
    
    
    ChapterAdded

* * *

## Query side

Event Handler:
    
    
    ChapterAdded
    
     |
    
    Update Search Index
    
     |
    
    Read Database

* * *

Reader:
    
    
    User
    
     |
    
    SearchQuery
    
     |
    
    Read Model
    
     |
    
    Result

* * *

# 8\. CQRS kết hợp Domain Event

Đây là phần rất quan trọng.

CQRS thường đi cùng Event.

* * *

Ví dụ:

Thêm chapter:
    
    
    AddChapterCommand
    
            |
    
            v
    
    Novel.add_chapter()
    
            |
    
            v
    
    ChapterAdded Event
    
            |
    
            +----------------+
    
            |                |
    
            v                v
    
     Search Index       Statistics

* * *

Event là cầu nối:
    
    
    Write Model
    
         |
    
     Domain Event
    
         |
    
    Read Model

* * *

# 9\. Write Model trong DDD

Write Model chính là Domain Model.

Ví dụ:
    
    
    domain/
    
        Novel
    
        Chapter
    
        Aggregate
    
        Repository

* * *

Nó ưu tiên:

  * Tính đúng nghiệp vụ. 
  * Bảo vệ invariant. 



* * *

Ví dụ:
    
    
    class Novel:
    
    
        def add_chapter(
            self,
            chapter
        ):
    
            if self.status == "locked":
    
                raise Exception(
                    "Cannot add chapter"
                )
    
            self.chapters.append(
                chapter
            )

* * *

# 10\. Read Model là gì?

Read Model tối ưu cho việc đọc.

Không cần giống Domain.

* * *

Ví dụ:

Domain:
    
    
    class Novel:
    
        id
        title
        chapters
        author
        source

* * *

Read Model:
    
    
    {
        "id": "123",
        "title": "ABC",
        "chapter_count": 200,
        "latest_chapter": "200",
        "cover": "image.jpg"
    }

* * *

Nó được thiết kế:

cho UI.

* * *

# 11\. Ví dụ App Cào Truyện

Đây là kiến trúc rất phù hợp.

* * *

## Write Database

SQLite:
    
    
    novels
    
    chapters
    
    crawl_jobs
    
    sources

Dùng cho:

Crawler.

* * *

## Read Database

Ví dụ:

SQLite khác:

hoặc:

  * Elasticsearch. 
  * PostgreSQL View. 
  * Redis. 



* * *

Lưu:
    
    
    novel_search
    
    chapter_index
    
    reading_cache

* * *

* * *

# 12\. Trước và sau CQRS

## Không CQRS
    
    
    Crawler
    
          |
    
     Database
    
          |
    
     Reader

Một database chịu tất cả.

* * *

## CQRS
    
    
                 Crawler
    
                    |
    
              Command Side
    
                    |
    
              Domain Model
    
                    |
    
              Write DB
    
                    |
    
              Domain Event
    
                    |
    
              Read Model
    
                    |
    
              Reader

* * *

# 13\. Command Model và Query Model khác nhau

Ví dụ:

## Command Model
    
    
    class Novel:
    
        def publish()
    
        def add_chapter()
    
        def archive()

* * *

## Query Model
    
    
    class NovelView:
    
    
        title
    
        author_name
    
        chapter_count
    
        latest_update

* * *

Không dùng chung.

* * *

# 14\. CQRS trong Clean Architecture

Kiến trúc:
    
    
    presentation/
    
        commands/
    
        queries/
    
    
    application/
    
        command_handlers/
    
        query_handlers/
    
    
    domain/
    
        entities/
    
        aggregates/
    
    
    infrastructure/
    
        write_repository/
    
        read_repository/

* * *

# 15\. CQRS với Repository

Có hai loại Repository.

* * *

## Write Repository

Domain:
    
    
    class NovelRepository:
    
        save()
    
        get_by_id()

* * *

## Read Repository

Application:
    
    
    class NovelQueryRepository:
    
    
        search()
    
    
        get_detail()

* * *

Không trộn.

* * *

# 16\. CQRS và Pagination

Ví dụ:

Danh sách truyện.

Không nên:
    
    
    NovelRepository.get_all()

* * *

Vì:

Có thể:
    
    
    10.000.000 novels

* * *

Query Model:
    
    
    class SearchNovelQuery:
    
    
        page: int
    
        size: int
    
        keyword: str

* * *

Handler:
    
    
    def handle(query):
    
        return database.search(
            keyword=query.keyword,
            page=query.page,
            size=query.size
        )

* * *

# 17\. CQRS và Dashboard

Dashboard rất phù hợp.

Ví dụ:

Cần:
    
    
    Tổng số truyện
    
    Chapter hôm nay
    
    Top source
    
    Crawler status

* * *

Không nên query Domain.

* * *

Tạo Read Model:
    
    
    {
        "total_novel": 50000,
        "today_chapter": 1200,
        "active_source": 15
    }

* * *

Update bằng Event:
    
    
    ChapterAdded
    
          |
    
    DashboardCounterHandler

* * *

# 18\. Khi nào nên dùng CQRS?

Không phải dự án nào cũng cần.

* * *

Không cần khi:

  * CRUD nhỏ. 
  * Ít dữ liệu. 
  * Ít business rule. 



* * *

Nên dùng khi:

✅ Read nhiều hơn Write.  
✅ Domain phức tạp.  
✅ Cần Search mạnh.  
✅ Dashboard lớn.  
✅ Có Event.  
✅ Microservice.

* * *

# 19\. CQRS không nhất thiết phải Microservice

Sai lầm:
    
    
    CQRS = Microservice

Không đúng.

Một ứng dụng Python đơn:
    
    
    FastAPI
    
        |
    CQRS
    
        |
    PostgreSQL

vẫn được.

* * *

# 20\. Ví dụ hoàn chỉnh: Publish Novel

## Command
    
    
    @dataclass
    class PublishNovelCommand:
    
        novel_id:str

* * *

## Handler
    
    
    class PublishNovelHandler:
    
    
        def handle(
            self,
            command
        ):
    
            novel = repository.get_by_id(
                command.novel_id
            )
    
    
            novel.publish()
    
    
            repository.save(
                novel
            )

* * *

## Event
    
    
    @dataclass
    class NovelPublished:
    
        novel_id:str

* * *

## Event Handler
    
    
    class UpdateSearchHandler:
    
    
        def handle(
            self,
            event
        ):
    
            search_index.update(
                event.novel_id
            )

* * *

## Query
    
    
    @dataclass
    class GetNovelQuery:
    
        id:str

* * *

## Query Handler
    
    
    class GetNovelHandler:
    
    
        def handle(
            self,
            query
        ):
    
            return read_db.find(
                query.id
            )

* * *

# 21\. Những lỗi thường gặp

* * *

## Lỗi 1: Tách CQRS quá sớm

Dự án nhỏ:
    
    
    User
    
    CRUD
    
    Database

không cần.

* * *

## Lỗi 2: Query đi qua Domain

Sai:
    
    
    search()
    
        |
    
    Novel Aggregate
    

* * *

Query chỉ đọc.

* * *

## Lỗi 3: Command chứa logic

Sai:
    
    
    command.publish()

* * *

Command chỉ là:
    
    
    data

* * *

# 22\. Kiến trúc DDD sau Buổi 16

Hiện tại:
    
    
    Domain Layer
    
    ├── Entity
    ├── Value Object
    ├── Aggregate
    ├── Repository
    ├── Domain Service
    ├── Domain Event
    ├── Factory
    └── Specification
    
    
    Application Layer
    
    ├── Use Case
    ├── Command
    ├── Command Handler
    ├── Query
    └── Query Handler
    
    
    Infrastructure
    
    ├── Write Database
    ├── Read Database
    ├── Event Bus
    └── External Service

* * *

# Bài tập

## Bài 1

Thiết kế Command cho:
    
    
    Crawler thêm chapter mới

Yêu cầu:

  * novel_id 
  * chapter_number 
  * title 
  * content 



* * *

## Bài 2

Thiết kế Query:
    
    
    Tìm truyện theo keyword

Có:

  * keyword 
  * page 
  * limit 



* * *

## Bài 3

Thiết kế CQRS flow:
    
    
    Crawler tải chapter
    
            ?
    
    Reader xem chapter

Vẽ:

  * Command 
  * Aggregate 
  * Event 
  * Read Model 



* * *

# Tổng kết Buổi 16

Cần nhớ:

✅ CQRS tách Write và Read.  
✅ Command thay đổi trạng thái.  
✅ Query chỉ đọc dữ liệu.  
✅ Domain Model nằm ở Command Side.  
✅ Read Model tối ưu cho UI.  
✅ Domain Event kết nối Write Model và Read Model.  
✅ CQRS rất phù hợp với hệ thống crawler + đọc truyện.

* * *

Buổi tiếp theo theo roadmap:

# Buổi 17: Event Sourcing trong DDD

Nội dung:

  * State hiện tại vs Event History. 
  * Aggregate với Event Store. 
  * Rebuild Aggregate. 
  * Snapshot. 
  * Event Sourcing kết hợp CQRS. 
  * Áp dụng: 
    * Lịch sử crawl. 
    * Reading History. 
    * Audit Log.

