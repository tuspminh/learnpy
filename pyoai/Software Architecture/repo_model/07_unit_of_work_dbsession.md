# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 7 - Database Session & Unit of Work (Professional Architecture)

> Đây là một trong những buổi quan trọng nhất của cả khóa học. Nếu Repository là "thủ thư", thì **Unit of Work (UoW)** là "người quản lý thư viện". UoW đảm bảo rằng nhiều thao tác trên database được thực hiện như **một giao dịch (transaction)** : hoặc tất cả thành công, hoặc tất cả thất bại.

Đây là kiến trúc được sử dụng trong:

  * SQLAlchemy 
  * Entity Framework 
  * Hibernate 
  * Django ORM (ở mức transaction) 
  * Nhiều hệ thống ERP, CRM, Banking 



* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Database Session là gì 
  * Transaction là gì 
  * Commit 
  * Rollback 
  * Unit of Work Pattern 
  * Context Manager 
  * Repository dùng chung Connection 
  * Repository Factory 
  * Transaction xuyên nhiều Repository 
  * Vì sao không để Repository tự commit 



* * *

# 1\. Vấn đề khi Repository tự mở Connection

Giả sử:
    
    
    story_repo.save(story)
    
    chapter_repo.save(chapter)
    
    author_repo.save(author)

Mỗi Repository tự làm:
    
    
    conn = sqlite3.connect(...)
    ...
    conn.commit()
    conn.close()

Điều gì xảy ra nếu:
    
    
    Story
    
    OK
    
    Chapter
    
    OK
    
    Author
    
    Lỗi

Kết quả:
    
    
    Story đã lưu
    
    Chapter đã lưu
    
    Author chưa lưu

Database bị **không nhất quán (inconsistent)**.

* * *

# 2\. Transaction

Ta muốn:
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Author
    
    ↓
    
    Commit

Hoặc
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Author
    
    ↓
    
    Rollback

Không có trạng thái ở giữa.

* * *

# 3\. Unit of Work

Ý tưởng:
    
    
    Repository
    
    ↓
    
    Không commit

Mà:
    
    
    UnitOfWork
    
    ↓
    
    Commit

Repository chỉ thao tác dữ liệu.

UnitOfWork quyết định khi nào lưu.

* * *

# 4\. Kiến trúc
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    UnitOfWork
     │
     ├──────────────┐
     ▼              ▼
    StoryRepo   ChapterRepo
     │              │
     └──────┬───────┘
            ▼
       SQLite Connection

Mọi Repository dùng **cùng một Connection**.

* * *

# 5\. DatabaseSession

Ta tạo
    
    
    infrastructure/
    
        database/
    
            session.py
    
    
    import sqlite3
    
    
    class DatabaseSession:
    
        def __init__(self, db_path: str):
    
            self.db_path = db_path
    
            self.connection = None

Nhiệm vụ:

  * mở connection 
  * đóng connection 
  * commit 
  * rollback 



* * *

# 6\. Context Manager
    
    
    with DatabaseSession(...) as session:
    
        ...

Tự động:
    
    
    enter
    
    ↓
    
    connection
    
    ↓
    
    exit
    
    ↓
    
    close

Đây là lý do chúng ta đã học **Context Manager** trước đó.

* * *

# 7\. Cài đặt Session
    
    
    class DatabaseSession:
    
        def __enter__(self):
    
            self.connection = sqlite3.connect(
                self.db_path
            )
    
            self.connection.row_factory = sqlite3.Row
    
            return self
    
        def __exit__(
            self,
            exc_type,
            exc,
            tb
        ):
    
            self.connection.close()

Session quản lý vòng đời của connection.

* * *

# 8\. Commit
    
    
    class DatabaseSession:
    
        ...
    
        def commit(self):
    
            self.connection.commit()

* * *

# 9\. Rollback
    
    
    class DatabaseSession:
    
        ...
    
        def rollback(self):
    
            self.connection.rollback()

* * *

# 10\. Repository nhận Connection

Sai:
    
    
    class StoryRepository:
    
        def __init__(self):
    
            self.conn = sqlite3.connect(...)

Đúng:
    
    
    class SQLiteStoryRepository:
    
        def __init__(
    
            self,
    
            connection
    
        ):
    
            self.connection = connection

Repository không tạo Connection.

Repository chỉ sử dụng Connection được truyền vào.

Đây là **Dependency Injection**.

* * *

# 11\. UnitOfWork
    
    
    class UnitOfWork:
    
        def __init__(
    
            self,
    
            session
    
        ):
    
            self.session = session

* * *

# 12\. Repository Factory

Trong UnitOfWork
    
    
    class UnitOfWork:
    
        @property
    
        def stories(self):
    
            return SQLiteStoryRepository(
                self.session.connection
            )

Có thể thêm:
    
    
    @property
    def chapters(self):
        return SQLiteChapterRepository(
            self.session.connection
        )
    
    
    @property
    def authors(self):
        return SQLiteAuthorRepository(
            self.session.connection
        )

* * *

# 13\. Commit trong UoW
    
    
    class UnitOfWork:
    
        ...
    
        def commit(self):
    
            self.session.commit()

Rollback
    
    
    def rollback(self):
    
        self.session.rollback()

* * *

# 14\. Service sử dụng UoW
    
    
    with DatabaseSession(DB) as session:
    
        uow = UnitOfWork(session)
    
        service = StoryService(uow)
    
        service.import_story(...)

Service không thấy sqlite3.

Chỉ thấy UoW.

* * *

# 15\. StoryService
    
    
    story = Story.create(...)
    
    uow.stories.save(story)
    
    chapter = ...
    
    uow.chapters.save(chapter)
    
    uow.commit()

Nếu lỗi
    
    
    uow.rollback()

* * *

# 16\. Context Manager cho UoW

Chúng ta có thể nâng cấp:
    
    
    with UnitOfWork(DB) as uow:
    
        ...

Bên trong:
    
    
    Enter
    
    ↓
    
    Open Connection
    
    ↓
    
    Repositories
    
    ↓
    
    Commit
    
    ↓
    
    Close

Nếu có Exception

↓

Rollback

↓

Close

* * *

# 17\. Cài đặt **exit**
    
    
    def __exit__(
    
        self,
    
        exc_type,
    
        exc,
    
        tb
    
    ):
    
        if exc_type:
    
            self.rollback()
    
        else:
    
            self.commit()
    
        self.session.close()

Đây là mẫu rất phổ biến trong SQLAlchemy.

* * *

# 18\. Transaction xuyên nhiều Repository

Ví dụ crawler:
    
    
    Insert Story
    
    ↓
    
    Insert Author
    
    ↓
    
    Insert Genre
    
    ↓
    
    Insert Chapter
    
    ↓
    
    Insert Image
    
    ↓
    
    Commit

Nếu
    
    
    Insert Image
    
    ↓
    
    Fail

↓

Rollback toàn bộ.

Không còn dữ liệu dở dang.

* * *

# 19\. Vì sao Repository không commit?

Nếu Repository tự commit:
    
    
    StoryRepo.save()
    
    ↓
    
    commit

Sau đó
    
    
    ChapterRepo
    
    ↓
    
    fail

Không thể rollback Story.

Đó là lý do **commit phải ở UnitOfWork**.

* * *

# 20\. Nested Transaction

Sau này có thể:
    
    
    UnitOfWork
    
    ↓
    
    Savepoint
    
    ↓
    
    Rollback Savepoint

SQLite hỗ trợ
    
    
    SAVEPOINT

PostgreSQL hỗ trợ mạnh hơn.

Đây là nền tảng cho các thao tác phức tạp như import nhiều truyện cùng lúc.

* * *

# 21\. Một Import Story hoàn chỉnh
    
    
    Crawler
    
    ↓
    
    Parser
    
    ↓
    
    Story Entity
    
    ↓
    
    StoryService
    
    ↓
    
    UnitOfWork
    
    ↓
    
    StoryRepository
    
    ↓
    
    StoryMapper
    
    ↓
    
    SQLite

Mọi Repository dùng chung Connection.

* * *

# 22\. Repository không biết Transaction

Repository chỉ biết:
    
    
    INSERT

Không biết:
    
    
    commit()

Không biết:
    
    
    rollback()

Đây là trách nhiệm của UoW.

* * *

# 23\. Cấu trúc thư mục
    
    
    app/
    
    domain/
        entities/
        repositories/
    
    services/
        story_service.py
    
    infrastructure/
    
        database/
            session.py
            unit_of_work.py
    
        sqlite/
            story_repository.py
            chapter_repository.py
            author_repository.py
    
        mappers/

Sau này khi chuyển sang PostgreSQL, chỉ cần thay tầng `infrastructure/database` và `infrastructure/sqlite`.

* * *

# 24\. Luồng hoàn chỉnh
    
    
    GUI
     │
     ▼
    StoryService
     │
     ▼
    UnitOfWork
     │
     ├─────────────┐
     ▼             ▼
    StoryRepo  ChapterRepo
     │             │
     ▼             ▼
    StoryMapper ChapterMapper
     │             │
     └──────┬──────┘
            ▼
    SQLite Connection
            │
            ▼
    SQLite Database

Đây là kiến trúc rất gần với các hệ thống doanh nghiệp.

* * *

# 25\. Tối ưu: Repository được tạo một lần

Đừng làm:
    
    
    @property
    def stories(self):
        return SQLiteStoryRepository(self.session.connection)

Mỗi lần truy cập sẽ tạo một đối tượng mới.

Tốt hơn:
    
    
    class UnitOfWork:
        def __enter__(self):
            self._stories = SQLiteStoryRepository(self.session.connection)
            self._chapters = SQLiteChapterRepository(self.session.connection)
            return self
    
        @property
        def stories(self):
            return self._stories

Các Repository được tái sử dụng trong suốt vòng đời của một Unit of Work.

* * *

# 26\. Thiết kế DatabaseSession tốt hơn

Ngoài `connection`, `DatabaseSession` có thể quản lý:

  * timeout 
  * foreign key (`PRAGMA foreign_keys = ON`) 
  * WAL mode 
  * busy timeout 
  * journal mode 
  * logging SQL 



Ví dụ:
    
    
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")

Đây là các thiết lập rất hữu ích cho ứng dụng crawler ghi dữ liệu thường xuyên.

* * *

# Sai lầm phổ biến

❌ Repository tự mở Connection

❌ Repository tự commit

❌ Service gọi `sqlite3`

❌ Mỗi Repository dùng một Connection khác nhau trong cùng một nghiệp vụ

❌ Không rollback khi có Exception

Nguyên tắc:
    
    
    Service
        │
        ▼
    UnitOfWork
        │
        ▼
    Repositories
        │
        ▼
    Connection

* * *

# Bài tập

## Bài 1

Viết `DatabaseSession` hỗ trợ:

  * `__enter__()`
  * `__exit__()`
  * `commit()`
  * `rollback()`
  * `close()`



Đảm bảo bật:

  * `sqlite3.Row`
  * `PRAGMA foreign_keys = ON`



* * *

## Bài 2

Viết `UnitOfWork`:

  * quản lý `StoryRepository`
  * `ChapterRepository`
  * `AuthorRepository`



Các Repository phải dùng chung một `sqlite3.Connection`.

* * *

## Bài 3

Viết `StoryService.import_story()`:

  1. Lưu `Story`
  2. Lưu tất cả `Author`
  3. Lưu tất cả `Genre`
  4. Lưu tất cả `Chapter`
  5. Nếu bất kỳ bước nào lỗi, rollback toàn bộ transaction. 



* * *

## Bài 4 (nâng cao)

Thiết kế `AbstractUnitOfWork` trong `domain`:
    
    
    class AbstractUnitOfWork(ABC):
        stories: StoryRepository
        chapters: ChapterRepository
        authors: AuthorRepository
    
        @abstractmethod
        def commit(self): ...
    
        @abstractmethod
        def rollback(self): ...

Sau đó xây dựng:

  * `SQLiteUnitOfWork`
  * `MemoryUnitOfWork`



đều triển khai interface này.

Đây là cách mà nhiều dự án theo **Clean Architecture** và **Cosmic Python** tổ chức tầng truy cập dữ liệu.

* * *

# Chuẩn bị cho Buổi 8

Ở buổi tiếp theo, chúng ta sẽ xây dựng **Query Specification Pattern** và **Query Object**. Thay vì liên tục thêm các phương thức như:

  * `find_by_slug()`
  * `find_by_author()`
  * `find_by_status()`
  * `find_by_genre()`
  * `find_by_updated_after()`



chúng ta sẽ thiết kế một cơ chế truy vấn linh hoạt, có thể kết hợp nhiều điều kiện, sắp xếp, phân trang và tái sử dụng giữa các Repository. Đây là nền tảng cho các hệ thống tìm kiếm và lọc dữ liệu quy mô lớn.

