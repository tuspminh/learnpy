# Domain-Driven Design Deep Dive

# Buổi 11 (Roadmap cập nhật): Repository Pattern trong DDD

Sau buổi 10, chúng ta đã học:

  * Application Layer 
  * Use Case 
  * DTO 
  * Cách Application gọi Domain 



Bây giờ chúng ta giải quyết một vấn đề:

> Use Case lấy Aggregate ở đâu? Lưu Aggregate ở đâu? Làm sao Domain không bị phụ thuộc Database?

Câu trả lời:

# Repository Pattern

* * *

# 1\. Vấn đề nếu không có Repository

Ví dụ một Use Case:
    
    
    class PublishNovelUseCase:
    
        def execute(self, novel_id):
    
            # lấy dữ liệu từ database
    
            connection.execute(
                "SELECT * FROM novels"
            )
    
            novel.publish()
    
            connection.execute(
                "UPDATE novels ..."
            )

* * *

Có vấn đề:

Use Case biết:

  * SQLite 
  * SQL 
  * Table 
  * Query 



Kiến trúc bị dính chặt:
    
    
    Application
    
         |
         |
     SQLite

* * *

DDD muốn:
    
    
    Application
    
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

# 2\. Repository là gì?

Định nghĩa DDD:

> Repository là một abstraction cung cấp khả năng truy cập Aggregate giống như một collection trong bộ nhớ.

Nói đơn giản:

Repository là:

> Kho chứa Domain Object.

* * *

Ví dụ:

Thay vì:
    
    
    SELECT * FROM novels

Domain nhìn thấy:
    
    
    novel = repository.get_by_id(id)

* * *

# 3\. Repository thuộc Layer nào?

Đây là điểm rất quan trọng.

Repository có 2 phần:

* * *

## Repository Interface

Thuộc:
    
    
    Domain Layer

Ví dụ:
    
    
    domain/repositories/novel_repository.py

* * *

## Repository Implementation

Thuộc:
    
    
    Infrastructure Layer

Ví dụ:
    
    
    infrastructure/repositories/sqlite_novel_repository.py

* * *

Kiến trúc:
    
    
                     Domain
    
            NovelRepository Interface
    
    
                        ^
                        |
                        |
    
                 Infrastructure
    
            SQLiteNovelRepository

* * *

# 4\. Repository chỉ làm việc với Aggregate Root

DDD có nguyên tắc:

> Mỗi Aggregate Root có Repository riêng.

Ví dụ:

App Cào Truyện:

## Novel Aggregate
    
    
    Novel
     |
     + Chapter

Repository:
    
    
    NovelRepository

* * *

Không tạo:
    
    
    ChapterRepository

Nếu Chapter không phải Aggregate Root.

* * *

Vì:

Chapter sống bên trong Novel.

Không được tự ý sửa:
    
    
    chapter.update()

mà phải:
    
    
    novel.update_chapter()

* * *

# 5\. Repository Interface

Ví dụ:

Domain:
    
    
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
    
    
        @abstractmethod
        def remove(
            self,
            novel
        ):
            pass

* * *

Chú ý:

Không có:
    
    
    import sqlite3

Không có:
    
    
    SQLAlchemy

Domain không biết database.

* * *

# 6\. Repository Implementation

Ví dụ SQLite:
    
    
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
                INSERT OR REPLACE INTO novels
                (
                    id,
                    title,
                    status
                )
                VALUES (?, ?, ?)
                """,
                (
                    novel.id,
                    novel.title,
                    novel.status
                )
            )
    
            self.connection.commit()
    
    
    
        def get_by_id(
            self,
            novel_id
        ):
    
            cursor = self.connection.execute(
                """
                SELECT
                    id,
                    title,
                    status
                FROM novels
                WHERE id=?
                """,
                (novel_id,)
            )
    
    
            row = cursor.fetchone()
    
    
            if row is None:
                return None
    
    
            return Novel(
                row[0],
                row[1],
                row[2]
            )

* * *

# 7\. Repository và Use Case

Ví dụ:

## Use Case
    
    
    class PublishNovelUseCase:
    
    
        def __init__(
            self,
            repository
        ):
            self.repository = repository
    
    
    
        def execute(
            self,
            novel_id
        ):
    
            novel = (
                self.repository
                .get_by_id(novel_id)
            )
    
    
            novel.publish()
    
    
            self.repository.save(
                novel
            )

* * *

Luồng:
    
    
    User
    
     |
     v
    
    PublishNovelUseCase
    
     |
     v
    
    NovelRepository
    
     |
     v
    
    SQLiteNovelRepository
    
     |
     v
    
    Database

* * *

# 8\. Repository giống Collection

DDD muốn bạn nghĩ:

Database:
    
    
    Table
    Row
    Column

không tồn tại trong Domain.

Domain nghĩ:
    
    
    Collection
    Object

* * *

Ví dụ:
    
    
    novels = repository
    
    
    novel = novels.get_by_id(1)
    
    
    novels.save(novel)

* * *

Giống:
    
    
    list
    dict
    set

* * *

# 9\. Repository không phải DAO

Đây là phần dễ nhầm.

* * *

## DAO

Data Access Object.

Ví dụ:
    
    
    class NovelDAO:
    
    
        def insert_row():
    
            ...
    
    
        def select_rows():
    
            ...

Nó quan tâm:

  * Table 
  * SQL 
  * Row 



* * *

## Repository

Quan tâm:

  * Aggregate 
  * Domain Object 
  * Business concept 



Ví dụ:
    
    
    class NovelRepository:
    
    
        def save(
            Novel
        ):
            ...

* * *

So sánh:

DAO| Repository  
---|---  
Database centric| Domain centric  
Table| Aggregate  
SQL| Object  
Infrastructure| Domain abstraction  
  
* * *

# 10\. Repository không chứa Business Logic

Sai:
    
    
    class NovelRepository:
    
    
        def publish_novel():
    
            check_permission()
    
            update_status()

* * *

Vì:

Publish là nghiệp vụ.

Thuộc:
    
    
    Novel.publish()

* * *

Repository chỉ:
    
    
    load()
    save()
    remove()

* * *

# 11\. Repository Query

Một câu hỏi:

Có nên viết:
    
    
    find_by_title()
    find_by_author()
    find_by_rating()

?

Câu trả lời:

Tùy.

* * *

Nếu phục vụ Domain:

Có thể.

Ví dụ:
    
    
    find_active_sources()

* * *

Nhưng tìm kiếm phức tạp:

Ví dụ:
    
    
    Tìm truyện:
    
    - nhiều lượt đọc
    - rating cao
    - thể loại fantasy
    - cập nhật hôm nay

Không nên nhét vào Repository.

* * *

Nên tạo:
    
    
    Query Service

* * *

# 12\. Repository trong App Cào Truyện

Thiết kế:
    
    
    domain/
    
        novels/
    
            novel.py
            repository.py
    
    
    application/
    
        use_cases/
    
            create_novel.py
            publish_novel.py
    
    
    infrastructure/
    
        database/
    
            sqlite.py
    
        repositories/
    
            sqlite_novel_repository.py

* * *

# 13\. Memory Repository để Test

Một lợi ích rất lớn.

Không cần SQLite khi test.

* * *
    
    
    class MemoryNovelRepository:
    
    
        def __init__(self):
    
            self.data = {}
    
    
    
        def save(
            self,
            novel
        ):
    
            self.data[
                novel.id
            ] = novel
    
    
    
        def get_by_id(
            self,
            novel_id
        ):
    
            return self.data.get(
                novel_id
            )

* * *

Test:
    
    
    def test_publish():
    
        repo = MemoryNovelRepository()
    
    
        use_case = PublishNovelUseCase(
            repo
        )
    
    
        ...

* * *

Nhanh, đơn giản.

* * *

# 14\. Repository và Dependency Injection

Không tạo trực tiếp:

Sai:
    
    
    class PublishNovelUseCase:
    
        repo = SQLiteNovelRepository()

* * *

Đúng:
    
    
    use_case = PublishNovelUseCase(
        repository
    )

* * *

Composition Root:
    
    
    repository = SQLiteNovelRepository(
        connection
    )
    
    
    use_case = PublishNovelUseCase(
        repository
    )

* * *

# 15\. Repository và Unit Of Work

Một Use Case có thể thay đổi nhiều Aggregate.

Ví dụ:

Thanh toán:
    
    
    Order
    
    Inventory
    
    Payment

* * *

Không muốn:
    
    
    save()
    save()
    save()

rồi lỗi giữa chừng.

* * *

Cần:
    
    
    Unit Of Work

Ví dụ:
    
    
    with unit_of_work:
    
        order.pay()
    
        inventory.reserve()
    
        payment.create()

* * *

Sau này học sâu.

* * *

# 16\. Repository hoàn chỉnh cho Novel

## Domain
    
    
    class Novel:
    
    
        def __init__(
            self,
            id,
            title
        ):
    
            self.id = id
            self.title = title
            self.status = "draft"
    
    
    
        def publish(self):
    
            self.status = "published"

* * *

## Interface
    
    
    class NovelRepository(ABC):
    
    
        def save(
            self,
            novel
        ):
            pass
    
    
        def get_by_id(
            self,
            id
        ):
            pass

* * *

## Application
    
    
    class PublishNovelUseCase:
    
    
        def __init__(
            self,
            repository
        ):
    
            self.repository = repository
    
    
    
        def execute(
            self,
            id
        ):
    
            novel = (
                self.repository
                .get_by_id(id)
            )
    
    
            novel.publish()
    
    
            self.repository.save(
                novel
            )

* * *

## Infrastructure
    
    
    class SQLiteNovelRepository(
        NovelRepository
    ):
    
        def save(self, novel):
    
            ...
    
    
        def get_by_id(self,id):
    
            ...

* * *

# 17\. Những lỗi thường gặp

## Lỗi 1

Repository nằm trong Domain nhưng import SQLite.

Sai:
    
    
    from sqlite3 import Connection

* * *

## Lỗi 2

Một Repository cho tất cả.

Sai:
    
    
    Repository:
    
    save_user()
    
    save_order()
    
    save_novel()

* * *

Nên:
    
    
    UserRepository
    
    OrderRepository
    
    NovelRepository

* * *

## Lỗi 3

Repository trả Dictionary

Sai:
    
    
    {
    "title":"abc"
    }

* * *

Đúng:
    
    
    Novel(...)

* * *

# 18\. Kiến trúc sau buổi 11

Hiện tại:
    
    
    Presentation
    
          |
          v
    
    Application
    
          |
          |
    
    Use Case
    
          |
          v
    
    Domain
    
     + Entity
     + Aggregate
     + Repository Interface
    
          |
          v
    
    Infrastructure
    
     + SQLite Repository
     + API Repository

* * *

# Bài tập

## Bài 1

Thiết kế:
    
    
    ReaderRepository

cho App đọc truyện.

Có:
    
    
    save()
    
    get_by_id()
    
    remove()

* * *

## Bài 2

Xác định Repository nào cần cho:
    
    
    Novel
    Chapter
    Source
    Reader
    Bookmark

Cái nào là Aggregate Root?

* * *

## Bài 3

Viết:
    
    
    MemoryNovelRepository

và test:
    
    
    CreateNovelUseCase

* * *

# Tổng kết Buổi 11

Cần nhớ:

✅ Repository là abstraction của Domain.  
✅ Interface nằm trong Domain.  
✅ Implementation nằm trong Infrastructure.  
✅ Repository làm việc với Aggregate Root.  
✅ Repository không chứa business logic.  
✅ Repository giúp thay đổi database mà không ảnh hưởng Domain.  
✅ Repository giúp test dễ dàng bằng In-Memory Repository.

* * *

Buổi tiếp theo theo roadmap cập nhật:

# Buổi 12: Domain Service trong DDD

Nội dung:

  * Khi nào logic thuộc Entity? 
  * Khi nào cần Domain Service? 
  * Domain Service vs Application Service. 
  * Pricing Service. 
  * Recommendation Service. 
  * Chapter Merge Service trong App Cào Truyện.

