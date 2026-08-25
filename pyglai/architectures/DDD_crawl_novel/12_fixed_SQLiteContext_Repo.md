Đó là một quan sát rất chính xác. Trong đoạn thiết kế Unit of Work (UoW) ở trên, tôi đã truyền trực tiếp `sqlite3.connect` vào trong hàm `__enter__` của UoW mà quên không tận dụng lại lớp `SQLiteContext` đã định nghĩa ở mục 1.

Để đảm bảo hệ thống tuân thủ nghiêm ngặt nguyên lý SOLID, tái sử dụng code và tách biệt hoàn toàn việc khởi tạo cấu hình DB (như bật chế độ `WAL`, chỉnh `timeout`) ra khỏi UoW, chúng ta cần chỉnh sửa lại để `SQLiteUnitOfWork` sở hữu và quản lý `SQLiteContext`.

Dưới đây là cách kết hợp chuẩn xác giữa Repo, UoW và `SQLiteContext`:

* * *

## 1\. Cập nhật Connection Context (`infrastructure/context.py`)

Giữ nguyên lớp này để làm nhiệm vụ đóng/mở và cấu hình kết nối low-level cho SQLite.
    
    
    import sqlite3
    
    class SQLiteContext:
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._connection = None
    
        def __enter__(self):
            # Thiết lập kết nối tối ưu đa luồng và tắt autocommit (isolation_level=None)
            self._connection = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            self._connection.execute("PRAGMA journal_mode=WAL;")
            self._connection.execute("PRAGMA synchronous=NORMAL;")
            return self._connection
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._connection:
                self._connection.close()
    
        @property
        def connection(self) -> sqlite3.Connection:
            if not self._connection:
                raise RuntimeError("Kết nối chưa được khởi tạo. Hãy gọi trong khối 'with'.")
            return self._connection
    

* * *

## 2\. Kết hợp `SQLiteContext` vào `SQLiteUnitOfWork` (`infrastructure/sqlite_uow.py`)

Bây giờ, `SQLiteUnitOfWork` sẽ không tự gọi `sqlite3.connect` nữa. Nó sẽ nhận `SQLiteContext` được truyền vào từ bên ngoài (Dependency Injection). Khi UoW bắt đầu (`__enter__`), nó sẽ kích hoạt Context để lấy ra kết nối duy nhất, sau đó cung cấp kết nối đó cho các Repository.
    
    
    from domain.unit_of_work import AbstractUnitOfWork
    from .context import SQLiteContext
    from .sqlite_repository import SQLiteComicRepository, SQLiteChapterRepository
    from .sqlite_job_repository import SQLiteCrawlJobRepository
    
    class SQLiteUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_context: SQLiteContext):
            self.db_context = db_context
            self._conn_context_manager = None
            self._connection = None
    
        def __enter__(self):
            # 1. Kích hoạt Context Manager của SQLiteContext để lấy connection
            self._conn_context_manager = self.db_context.__enter__()
            self._connection = self.db_context.connection
            
            # 2. Bắt đầu một Transaction thuần SQL cho toàn bộ phiên làm việc
            self._connection.execute("BEGIN TRANSACTION;")
    
            # 3. Khởi tạo các Repository và dùng chung kết nối duy nhất này
            self.comic_repo = SQLiteComicRepository(self._connection)
            self.chapter_repo = SQLiteChapterRepository(self._connection)
            self.job_repo = SQLiteCrawlJobRepository(self._connection)
            
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                # Gọi hàm __exit__ của lớp cha (tự động commit nếu thành công, rollback nếu lỗi)
                super().__exit__(exc_type, exc_val, exc_tb)
            finally:
                # 4. Đóng kết nối an toàn bằng cách thoát Context Manager của SQLiteContext
                if self.db_context:
                    self.db_context.__exit__(exc_type, exc_val, exc_tb)
    
        def commit(self):
            if self._connection:
                self._connection.execute("COMMIT;")
    
        def rollback(self):
            if self._connection:
                self._connection.execute("ROLLBACK;")
    

* * *

## 3\. Bản chất luồng đi của Connection trong Repository

Như vậy, các Repository (ví dụ: `SQLiteChapterRepository`) sẽ nhận biến `self.connection` từ đâu? Nó được UoW trích xuất từ `SQLiteContext` và truyền trực tiếp vào hàm khởi tạo (`__init__`) của Repo:
    
    
    import sqlite3
    from domain.model import Chapter
    
    class SQLiteChapterRepository:
        def __init__(self, connection: sqlite3.Connection):
            # Kết nối này được lấy từ db_context.connection bên trong UoW
            self.connection = connection 
    
        def save(self, chapter: Chapter) -> None:
            # Repo sử dụng trực tiếp kết nối mà không cần quan tâm đến việc đóng/mở hay transaction
            cursor = self.connection.cursor()
            sql = "INSERT INTO chapters (id, content) VALUES (?, ?) ON CONFLICT..."
            cursor.execute(sql, (chapter.id.value, chapter.content))
    

* * *

## 4\. Cách khởi chạy trong `main.py`

Khi khởi chạy ứng dụng, luồng khởi tạo các thành phần sẽ phân cấp rõ ràng theo đúng nguyên lý SOLID:
    
    
    from infrastructure.context import SQLiteContext
    from infrastructure.sqlite_uow import SQLiteUnitOfWork
    from application.crawler_service import CrawlerApplicationService
    
    DB_PATH = "comics.db"
    
    def main():
        # Bước 1: Khởi tạo Hạ tầng quản lý kết nối low-level
        db_context = SQLiteContext(DB_PATH)
        
        # Bước 2: Khởi tạo Unit of Work điều phối Transaction (Inject db_context vào)
        uow = SQLiteUnitOfWork(db_context)
        
        # Bước 3: Khởi tạo Tầng ứng dụng (Inject uow vào)
        crawler_service = CrawlerApplicationService(uow)
        
        # Chạy tác vụ crawl
        crawler_service.crawl_and_save_chapter(
            comic_id="linh-vuc",
            job_id="job-01",
            chapter_num=1,
            title="Chương 1",
            content="Nội dung..."
        )
    
    if __name__ == "__main__":
        main()
    

## Tổng kết mối quan hệ:

  * `SQLiteContext`: Chịu trách nhiệm về vật lý (Địa chỉ file DB, Mở file, Đóng file, Cấu hình bật chế độ ghi đĩa `WAL`).
  * `SQLiteUnitOfWork`: Chịu trách nhiệm về tính toàn vẹn (Quản lý lệnh `BEGIN`, `COMMIT`, `ROLLBACK` và gom các Repo chạy chung một thuyền).
  * `Repositories`: Chịu trách nhiệm về nghiệp vụ dữ liệu (Chỉ cầm `connection` để chạy lệnh `SELECT/INSERT/UPDATE` thuần SQL).



Sự tách biệt này giúp bạn có thể dễ dàng thay thế `SQLiteContext` bằng một Context kết nối đến Database khác (như PostgreSQL) mà không làm thay đổi cấu trúc của Unit of Work hay Repositories.

Bạn có muốn tiếp tục triển khai mô hình CQRS để áp dụng `SQLiteContext` này một cách gọn nhẹ hơn cho luồng Đọc (chỉ cần Đọc truyện hiển thị lên giao diện, không cần qua UoW phức tạp) không?