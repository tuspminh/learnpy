Có, rất nên tách biệt. Việc mỗi Repository tự mở kết nối (`sqlite3.connect`), tự quản lý `BEGIN TRANSACTION` và `COMMIT` đang vi phạm nghiêm trọng các nguyên lý SOLID, cụ thể là:

  * Single Responsibility Principle (SRP): Repository vừa phải làm nhiệm vụ truy vấn SQL, vừa phải gánh thêm trách nhiệm quản lý vòng đời kết nối và tính toàn vẹn của dữ liệu (Transaction).
  * Dependency Inversion Principle (DIP): Tầng Domain hoặc Application bị phụ thuộc gián tiếp vào cơ chế Transaction của một Database cụ thể (SQLite).
  * Tính toàn vẹn dữ liệu (Atomicity): Nếu một tác vụ Application Service cần lưu thông tin truyện vào `ComicRepository` VÀ lưu tiến độ vào `CrawlJobRepository`. Nếu một trong hai Repo bị lỗi, bạn không thể ROLLBACK đồng bộ cả hai vì chúng dùng hai kết nối độc lập.



Dưới đây là cách triển khai Connection Context và Unit of Work (UoW) thuần Python & SQL theo đúng chuẩn DDD và SOLID.

* * *

## 1\. Thiết kế Connection Context (`infrastructure/context.py`)

Thành phần này đóng vai trò quản lý vòng đời của một kết nối SQLite duy nhất xuyên suốt một phiên làm việc (Session), sử dụng cơ chế `Context Manager` (`with`) của Python.
    
    
    import sqlite3
    
    class SQLiteContext:
        """Quản lý kết nối SQLite duy nhất cho một chuỗi tác vụ"""
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._connection = None
    
        def __enter__(self):
            # Khởi tạo kết nối với cấu hình tối ưu đa luồng
            # Tắt autocommit bằng isolation_level=None để nhường quyền cho Unit of Work
            self._connection = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            self._connection.execute("PRAGMA journal_mode=WAL;")
            self._connection.execute("PRAGMA synchronous=NORMAL;")
            return self._connection
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._connection:
                self._connection.close()
    
        @property
        def connection(self) -> sqlite3.Connection:
            if self._connection is None:
                raise RuntimeError("Kết nối chưa được khởi tạo. Hãy sử dụng trong block 'with'.")
            return self._connection
    

* * *

## 2\. Thiết kế Unit of Work (`domain/unit_of_work.py` & `infrastructure/`)

Unit of Work chịu trách nhiệm quản lý các Transaction. Nó điều phối việc ghi dữ liệu và đảm bảo tính toàn vẹn (tất cả cùng thành công hoặc tất cả cùng thất bại).

## Interface ở tầng Domain (`domain/unit_of_work.py`)

Tầng Domain chỉ định nghĩa Interface mẫu để Application Service gọi, hoàn toàn không phụ thuộc vào SQL.
    
    
    from abc import ABC, abstractmethod
    from .repository import ComicRepository, ChapterRepository
    from .job_repository import CrawlJobRepository
    
    class AbstractUnitOfWork(ABC):
        comic_repo: ComicRepository
        chapter_repo: ChapterRepository
        job_repo: CrawlJobRepository
    
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
    
        @abstractmethod
        def commit(self):
            pass
    
        @abstractmethod
        def rollback(self):
            pass
    

## Triển khai cụ thể ở tầng Infrastructure (`infrastructure/sqlite_uow.py`)

Lớp này sẽ kết hợp `SQLiteContext` và truyền chung một kết nối duy nhất vào tất cả các Repository.
    
    
    import sqlite3
    from domain.unit_of_work import AbstractUnitOfWork
    from .sqlite_repository import SQLiteComicRepository, SQLiteChapterRepository
    from .sqlite_job_repository import SQLiteCrawlJobRepository
    
    class SQLiteUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._connection = None
    
        def __enter__(self):
            # 1. Mở kết nối duy nhất
            self._connection = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            self._connection.execute("PRAGMA journal_mode=WAL;")
            
            # 2. Bắt đầu Transaction thuần SQL
            self._connection.execute("BEGIN TRANSACTION;")
    
            # 3. Tiêm (Inject) chung một kết nối vào các Repository
            self.comic_repo = SQLiteComicRepository(self._connection)
            self.chapter_repo = SQLiteChapterRepository(self._connection)
            self.job_repo = SQLiteCrawlJobRepository(self._connection)
            
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            super().__exit__(exc_type, exc_val, exc_tb)
            if self._connection:
                self._connection.close() # Đóng kết nối khi thoát block 'with'
    
        def commit(self):
            if self._connection:
                self._connection.execute("COMMIT;")
    
        def rollback(self):
            if self._connection:
                self._connection.execute("ROLLBACK;")
    

* * *

## 3\. Cập nhật lại Repository (Thuần SQL, Không tự tạo Connection)

Lúc này, các Repository trở nên vô cùng sạch sẽ (Clean Code). Chúng không quan tâm DB được mở ra sao hay đóng khi nào, chúng chỉ nhận `connection` và chạy lệnh SQL.
    
    
    import sqlite3
    from domain.model import Comic
    
    class SQLiteComicRepository:
        def __init__(self, connection: sqlite3.Connection):
            # Nhận kết nối dùng chung từ Unit of Work cấp cho
            self.connection = connection 
    
        def save(self, comic: Comic) -> None:
            cursor = self.connection.cursor()
            sql = "INSERT INTO comics (id, title, source_url) VALUES (?, ?, ?) ON CONFLICT..."
            cursor.execute(sql, (comic.id.value, comic.title, comic.source_url))
            # Không viết conn.commit() hay conn.close() ở đây nữa!
    

* * *

## 4\. Sử dụng tại Tầng Application Service (Cực kỳ an toàn)

Hãy xem cách `CrawlerApplicationService` điều phối một tác vụ cào truyện: Lưu truyện thành công, cập nhật trạng thái Task thành công. Nếu việc lưu trạng thái Task bị lỗi, thông tin truyện cũng tự động được Rollback để tránh lệch dữ liệu.
    
    
    from domain.unit_of_work import AbstractUnitOfWork
    from domain.model import ComicId
    
    class CrawlerApplicationService:
        def __init__(self, uow: AbstractUnitOfWork):
            self.uow = uow # Inject Unit of Work interface
    
        def crawl_and_save_chapter(self, comic_id: ComicId, job_id, chapter_num: int, title: str, content: str):
            # Toàn bộ mã nguồn bên trong block 'with' chạy chung 1 Transaction duy nhất
            with self.uow:
                # 1. Lưu kho truyện chính thông qua Repo 1
                chapter = ... # Khởi tạo Domain Object
                self.uow.chapter_repo.save(chapter)
                
                # 2. Cập nhật tiến độ thông qua Repo 2
                self.uow.job_repo.update_task_status(job_id, chapter_num, "SUCCESS", None)
                
                # Tự động gọi COMMIT khi hết block 'with' nếu không có exception.
                # Nếu có bất kỳ lỗi nào xảy ra ở bước 1 hoặc 2, tự động gọi ROLLBACK sạch sẽ.
    

## Kết luận giá trị mang lại của mô hình này:

  1. Repository độc lập tối đa: Đúng chuẩn SOLID, Repository giờ đây chỉ tập trung vào việc chuyển đổi Object thành các câu lệnh SQL và ngược lại.
  2. Transaction đồng bộ: Giải quyết triệt để bài toán lưu dở dang (ví dụ: truyện đã lưu vào DB nhưng tiến độ tác vụ chưa cập nhật, dẫn tới việc app bật lại sẽ cào đè làm hỏng data).
  3. Dễ dàng Unit Test: Bạn có thể dễ dàng viết Mock cho `AbstractUnitOfWork` để test tầng Application Service mà không cần đụng tới một file `.db` vật lý nào của SQLite.



Bạn có muốn mở rộng hệ thống bằng cách áp dụng CQRS (Command Query Responsibility Segregation), tách biệt Unit of Work cho luồng Ghi dữ liệu (Crawl), và dùng một Context gọn nhẹ riêng cho luồng Đọc dữ liệu (Hiển thị truyện lên giao diện) không?