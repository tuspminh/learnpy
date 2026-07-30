# Domain-Driven Design Deep Dive

# Buổi 10: Repository Pattern trong DDD — Cầu nối giữa Domain và Database

Sau khi học:

  * Entity 
  * Value Object 
  * Aggregate 
  * Aggregate Root 



chúng ta gặp một câu hỏi:

> Aggregate được tạo ra trong bộ nhớ, vậy làm sao lưu xuống database và lấy lại?

DDD trả lời bằng:

# Repository

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ Buổi 6: Entity

✅ Buổi 7: Value Object

✅ Buổi 8: Aggregate

✅ Buổi 9: Aggregate Root

✅ **Buổi 10: Repository**

⬜ Buổi 11: Domain Service

⬜ Buổi 12: Domain Event

* * *

# 1\. Repository là gì?

Định nghĩa DDD:

> Repository là một abstraction cung cấp collection-like interface cho việc truy cập Aggregate.

Nói đơn giản:

> Repository giúp Domain lấy và lưu Aggregate mà không cần biết dữ liệu nằm ở đâu.

* * *

Ví dụ:

Domain muốn:
    
    
    novel = repository.get(
        novel_id
    )

Domain không cần biết:

  * SQLite? 
  * PostgreSQL? 
  * MongoDB? 
  * API? 
  * File? 



* * *

# 2\. Repository giải quyết vấn đề gì?

Không có Repository:
    
    
    class Novel:
    
        def save(self):
    
            sqlite.insert(...)

Domain biết database.

Sai kiến trúc.

* * *

Luồng sai:
    
    
    Domain
       |
       |
     SQLite

Domain bị phụ thuộc Infrastructure.

* * *

DDD muốn:
    
    
                 Domain
    
                   |
                   |
            Repository Interface
    
                   |
                   |
            Infrastructure
    
                   |
                   |
               Database

* * *

# 3\. Repository thuộc tầng nào?

Trong Clean Architecture:
    
    
    src/
    
    ├── domain/
    │
    │   ├── entities/
    │   ├── value_objects/
    │   └── repositories/
    │
    ├── application/
    │
    │   └── use_cases/
    │
    └── infrastructure/
        
        ├── database/
        └── repositories/

* * *

Repository Interface:
    
    
    domain

Repository Implementation:
    
    
    infrastructure

* * *

# 4\. Ví dụ đơn giản

## Domain Entity
    
    
    class Novel:
    
        def __init__(
            self,
            novel_id,
            title
        ):
            self.id = novel_id
            self.title = title

* * *

## Repository Interface

Trong Domain:
    
    
    from abc import ABC, abstractmethod
    
    
    class NovelRepository(ABC):
    
    
        @abstractmethod
        def save(
            self,
            novel: Novel
        ):
            pass
    
    
        @abstractmethod
        def get_by_id(
            self,
            novel_id
        ):
            pass

* * *

Chú ý:

Repository này không biết:

  * SQL 
  * SQLite 
  * ORM 



* * *

# 5\. Infrastructure Implementation

Ví dụ dùng SQLite:
    
    
    import sqlite3
    
    
    class SQLiteNovelRepository:
    
        def __init__(
            self,
            connection
        ):
            self.connection = connection
    
    
        def save(
            self,
            novel
        ):
    
            self.connection.execute(
                """
                INSERT INTO novels
                (id,title)
                VALUES (?,?)
                """,
                (
                    novel.id,
                    novel.title
                )
            )
    
            self.connection.commit()
    
    
        def get_by_id(
            self,
            novel_id
        ):
    
            cursor = self.connection.execute(
                """
                SELECT id,title
                FROM novels
                WHERE id=?
                """,
                (novel_id,)
            )
    
            row = cursor.fetchone()
    
            if row:
    
                return Novel(
                    row[0],
                    row[1]
                )
    
            return None

* * *

Domain không biết lớp này tồn tại.

* * *

# 6\. Repository không phải DAO

Đây là nhầm lẫn phổ biến.

## DAO

Data Access Object.

Nó tập trung:
    
    
    Database operation

Ví dụ:
    
    
    user_table.insert()

* * *

## Repository

Tập trung:
    
    
    Domain concept

Ví dụ:
    
    
    novel_repository.save(
        novel
    )

* * *

So sánh:

DAO| Repository  
---|---  
Database-centric| Domain-centric  
CRUD| Aggregate  
Table| Business object  
Infrastructure| Domain abstraction  
  
* * *

# 7\. Repository làm việc với Aggregate Root

DDD có quy tắc:

> Repository chỉ tồn tại cho Aggregate Root.

Ví dụ:
    
    
    Order Aggregate
    
    
    Order
     |
     +-- OrderItem
     |
     +-- Money

Có:
    
    
    OrderRepository

Không có:
    
    
    OrderItemRepository

* * *

Vì:

OrderItem không tồn tại độc lập.

* * *

# 8\. Ví dụ Order Repository

Interface:
    
    
    class OrderRepository(ABC):
    
    
        @abstractmethod
        def save(
            self,
            order
        ):
            pass
    
    
        @abstractmethod
        def find(
            self,
            order_id
        ):
            pass

* * *

Không:
    
    
    save_order_item()

* * *

# 9\. Repository và Collection

DDD thích Repository giống collection.

Ví dụ:
    
    
    novels = repository

Bạn có thể:
    
    
    novel = novels.get(id)

hoặc:
    
    
    novels.add(novel)

* * *

Không quan tâm:
    
    
    SELECT *
    INSERT
    UPDATE

* * *

# 10\. Repository trong App Cào Truyện

Áp dụng vào dự án.

Các Aggregate:
    
    
    Novel
    
    Chapter
    
    Source
    
    Reader
    
    ReadingProgress

* * *

Repository:
    
    
    NovelRepository
    
    ChapterRepository
    
    SourceRepository
    
    ReaderRepository
    
    ReadingProgressRepository

* * *

Ví dụ:
    
    
    class NovelRepository(ABC):
    
    
        def get(
            self,
            novel_id
        ):
            pass
    
    
        def save(
            self,
            novel
        ):
            pass

* * *

# 11\. Use Case sử dụng Repository

Ví dụ:

Use case:

"Đổi tên truyện"

* * *

Application Layer:
    
    
    class RenameNovelUseCase:
    
    
        def __init__(
            self,
            repository
        ):
            self.repository = repository
    
    
    
        def execute(
            self,
            novel_id,
            new_title
        ):
    
            novel = (
                self.repository
                .get(novel_id)
            )
    
    
            novel.rename(
                new_title
            )
    
    
            self.repository.save(
                novel
            )

* * *

Luồng:
    
    
    User
    
     ↓
    
    Use Case
    
     ↓
    
    Repository
    
     ↓
    
    Novel Aggregate
    
     ↓
    
    Database

* * *

# 12\. Repository và Unit Of Work

Trong hệ thống lớn:

Một use case có thể thay đổi nhiều Aggregate.

Ví dụ:

Thanh toán:
    
    
    Order
    
    Inventory
    
    Payment

* * *

Cần:
    
    
    Unit Of Work

Ví dụ:
    
    
    with unit_of_work:
    
        order.pay()
    
        inventory.remove()
    
        payment.create()

* * *

Nếu lỗi:
    
    
    Rollback

* * *

Chúng ta sẽ học sâu phần này sau.

* * *

# 13\. Repository không nên có quá nhiều method

Sai:
    
    
    class NovelRepository:
    
        find_by_title()
    
        find_by_author()
    
        find_by_date()
    
        find_by_category()
    
        find_by_rating()
    
        find_by_status()
    
        ...

Repository thành Search Service.

* * *

Đúng:
    
    
    class NovelRepository:
    
        get()
    
        save()
    
        remove()

* * *

Các truy vấn phức tạp:

nên dùng:
    
    
    Query Service

* * *

# 14\. Repository vs Query Service

Ví dụ:

Màn hình tìm kiếm:
    
    
    Tìm truyện:
    
    - title chứa "abc"
    - rating > 4
    - nhiều lượt đọc

Không nên:
    
    
    NovelRepository.search_complex()

* * *

Nên:
    
    
    SearchService

hoặc:
    
    
    Read Model

* * *

DDD CQRS:
    
    
    Command Side
    
    Repository
    
            +
    
    Query Side
    
    Query Service

* * *

# 15\. Repository với SQLite trong App Cào Truyện

Cấu trúc:
    
    
    src/
    
    domain/
    
        novels/
    
            novel.py
            repository.py
    
    
    application/
    
        rename_novel.py
    
    
    infrastructure/
    
        sqlite/
    
            novel_repository.py

* * *

Domain:
    
    
    class NovelRepository(ABC):
    
        def save(self, novel):
            pass

* * *

SQLite:
    
    
    class SQLiteNovelRepository(
        NovelRepository
    ):
    
        def save(self, novel):
    
            ...

* * *

# 16\. Dependency Injection

Use case không tự tạo Repository.

Sai:
    
    
    class RenameNovel:
    
        repo = SQLiteNovelRepository()

* * *

Đúng:
    
    
    use_case = RenameNovel(
        repository
    )

* * *

Ví dụ:
    
    
    repo = SQLiteNovelRepository(
        connection
    )
    
    
    service = RenameNovelUseCase(
        repo
    )

* * *

# 17\. Repository và Testing

Đây là lợi ích rất lớn.

Không cần database thật.

Tạo:
    
    
    class MemoryNovelRepository:
    
    
        def __init__(self):
    
            self.data = {}
    
    
    
        def save(
            self,
            novel
        ):
    
            self.data[novel.id] = novel
    
    
    
        def get_by_id(
            self,
            novel_id
        ):
    
            return self.data.get(
                novel_id
            )

* * *

Test:
    
    
    repo = MemoryNovelRepository()
    
    
    use_case = RenameNovelUseCase(
        repo
    )

Nhanh hơn SQLite.

* * *

# 18\. Repository hoàn chỉnh cho Novel

## Entity
    
    
    class Novel:
    
    
        def __init__(
            self,
            novel_id,
            title
        ):
    
            self.id = novel_id
            self.title = title
    
    
    
        def rename(
            self,
            title
        ):
    
            if not title:
                raise ValueError()
    
            self.title = title

* * *

## Interface
    
    
    from abc import ABC, abstractmethod
    
    
    class NovelRepository(ABC):
    
    
        @abstractmethod
        def get_by_id(
            self,
            novel_id
        ):
            pass
    
    
    
        @abstractmethod
        def save(
            self,
            novel
        ):
            pass

* * *

## Memory Implementation
    
    
    class MemoryNovelRepository:
    
    
        def __init__(self):
    
            self.items = {}
    
    
    
        def save(
            self,
            novel
        ):
    
            self.items[
                novel.id
            ] = novel
    
    
    
        def get_by_id(
            self,
            novel_id
        ):
    
            return self.items.get(
                novel_id
            )

* * *

# 19\. Những lỗi thường gặp

## Lỗi 1

Entity tự save.

Sai:
    
    
    novel.save()

* * *

## Lỗi 2

Repository chứa business logic.

Sai:
    
    
    repository.pay_order()

* * *

Business logic thuộc:
    
    
    Aggregate

* * *

## Lỗi 3

Repository trả Dictionary

Sai:
    
    
    {
    "id":1,
    "title":"abc"
    }

* * *

Đúng:
    
    
    Novel(
        id=1,
        title="abc"
    )

* * *

## Lỗi 4

Repository phụ thuộc ORM trong Domain

Sai:
    
    
    from sqlalchemy import Model

* * *

# 20\. Kiến trúc hoàn chỉnh

Sau 10 buổi:
    
    
                     Application
    
                          |
                          |
    
                      Domain
    
            ----------------------------
    
            Entity
            Value Object
            Aggregate
            Repository Interface
    
    
                          |
    
                  Infrastructure
    
    
            SQLite Repository
    
            API Repository
    
            File Repository

* * *

# Bài tập

## Bài 1

Thiết kế:
    
    
    BookRepository

cho thư viện.

Có:
    
    
    save()
    
    get_by_id()
    
    remove()

* * *

## Bài 2

Trong App Cào Truyện:

Tạo:
    
    
    NovelRepository
    
    ChapterRepository
    
    SourceRepository

Xác định:

  * Cái nào là Aggregate Root? 
  * Repository nào cần? 



* * *

## Bài 3

Viết:
    
    
    MemoryNovelRepository

để test:
    
    
    RenameNovelUseCase

không dùng database.

* * *

# Tổng kết Buổi 10

Cần nhớ:

  * Repository là abstraction của Domain. 
  * Repository không phải DAO. 
  * Repository thuộc Aggregate Root. 
  * Repository Interface nằm trong Domain. 
  * Repository Implementation nằm trong Infrastructure. 
  * Repository không chứa business logic. 
  * Repository giúp thay đổi database mà Domain không bị ảnh hưởng. 



* * *

Ở **Buổi 11** , chúng ta sẽ học **Domain Service** :

  * Khi nào logic thuộc Entity? 
  * Khi nào cần Domain Service? 
  * Vì sao không nên tạo "Service chứa tất cả logic"? 
  * Ví dụ thực tế: Pricing Service, Recommendation Service, Crawler Matching Service trong App Cào Truyện.

