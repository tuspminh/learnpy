Rất hay. Đây là một trong những chủ đề mà rất nhiều lập trình viên Python còn yếu, mặc dù nó quyết định ứng dụng có thể mở rộng được hay không.

Nếu chỉ viết một app cào truyện nhỏ thì ai cũng làm được. Nhưng nếu muốn xây dựng một **framework crawler** có thể chạy nhiều nguồn (TruyenFull, TangThuVien, TruyenYY, Wikidich, NovelBin...), hỗ trợ plugin, queue, Celery/Dramatiq, SQLite/PostgreSQL thì việc thiết kế **Model + Repository** là cực kỳ quan trọng.

* * *

# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

Mục tiêu cuối khóa:

✅ Thiết kế được database chuẩn

✅ Thiết kế Model Python sạch

✅ Repository Pattern chuẩn

✅ Unit of Work

✅ Generic Repository

✅ Plugin Repository

✅ Service Layer

✅ Cache Layer

✅ Async Repository

✅ Repository cho SQLite/Postgres

✅ Chuẩn bị để sau này chuyển sang SQLAlchemy hoặc Tortoise ORM mà không phải sửa business logic.

* * *

# Roadmap

## Phần I — Phân tích Domain

Buổi 1

  * Domain Driven Design cơ bản 
  * Phân tích nghiệp vụ app cào truyện 
  * Entity là gì 
  * Value Object 
  * Aggregate 
  * Quan hệ giữa các model 



* * *

## Phần II — Thiết kế Database

Buổi 2

Thiết kế bảng
    
    
    source
    
    story
    
    chapter
    
    author
    
    genre
    
    tag
    
    crawl_job
    
    crawl_log
    
    image
    
    bookmark
    
    history

Chuẩn hóa dữ liệu

1NF

2NF

3NF

* * *

## Phần III — Thiết kế Model

Buổi 3

Model Python
    
    
    Story
    
    Chapter
    
    Author
    
    Genre
    
    Tag
    
    Source
    
    CrawlJob

Dataclass

ABC

Validation

* * *

## Phần IV — Repository Pattern

Buổi 4

Repository là gì

Repository Interface

SQLite Repository

In-memory Repository

* * *

## Phần V — Generic Repository

Buổi 5

BaseRepository

CRUD

Pagination

Search

Sort

Filter

* * *

## Phần VI — Service Layer

Buổi 6

StoryService

CrawlerService

BookmarkService

HistoryService

* * *

## Phần VII — Unit Of Work

Buổi 7

Transaction

Rollback

Commit

SQLite

* * *

## Phần VIII — Async Repository

Buổi 8

aiosqlite

Async CRUD

Connection Pool

* * *

## Phần IX — Repository Plugin

Buổi 9

Mỗi source có repository riêng
    
    
    TruyenFullRepository
    
    NovelBinRepository
    
    TangThuVienRepository

* * *

## Phần X — Repository Cache

Buổi 10

Redis

Memory Cache

TTL

* * *

## Phần XI — Testing Repository

Buổi 11

Fake Repository

Mock

Test Database

* * *

## Phần XII — Thiết kế Clean Architecture

Buổi 12

Repository

Service

Controller

CLI

GUI

