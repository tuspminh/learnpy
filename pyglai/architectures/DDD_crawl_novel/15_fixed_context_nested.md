Nhận định của bạn hoàn toàn chính xác về mặt tối ưu mã nguồn. Việc lồng hai Context Manager (`with SQLiteUnitOfWork` chứa `with SQLiteContext`) trong thiết kế trước đó làm cho cấu trúc code bị rườm rà và dư thừa không cần thiết.

Trong SQLite thuần SQL, bản thân `Unit of Work` chính là một Connection Context đặc biệt chuyên cho luồng ghi (có kèm Transaction). Do đó, ta hoàn toàn có thể bỏ `SQLiteContext` ra khỏi luồng ghi và gộp thẳng logic quản lý kết nối vào trong UoW. `SQLiteContext` sẽ được giải phóng hoàn toàn và chỉ phục vụ duy nhất cho các tác vụ Đọc (Query Service) như bạn đề xuất.

Dưới đây là cách tái cấu trúc lại hệ thống theo đúng tư duy tinh gọn này:

* * *

## 1\. Unit of Work Tinh Gọn (Tự quản lý Connection & Transaction)

`SQLiteUnitOfWork` giờ đây đóng vai trò là Context Manager duy nhất của luồng Ghi. Nó tự mở kết nối, cấu hình SQLite (`WAL` mode), kích hoạt `BEGIN TRANSACTION`, khởi tạo Repositories và đóng kết nối khi kết thúc.

## Interface (`domain/unit_of_work.py`)
    
    
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
        def commit(self): pass
    
        @abstractmethod
        def rollback(self): pass
    

## Triển khai cụ thể (`infrastructure/sqlite_uow.py`)
    
    
    import sqlite3
    from domain.unit_of_work import AbstractUnitOfWork
    from .sqlite_repository import SQLiteComicRepository, SQLiteChapterRepository
    from .sqlite_job_repository import SQLiteCrawlJobRepository
    
    class SQLiteUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._connection = None
    
        def __enter__(self):
            # Tự quản lý kết nối low-level cho luồng ghi
            self._connection = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            self._connection.execute("PRAGMA journal_mode=WAL;")
            self._connection.execute("PRAGMA synchronous=NORMAL;")
            
            # Kích hoạt Transaction
            self._connection.execute("BEGIN TRANSACTION;")
    
            # Inject kết nối vào các Repository
            self.comic_repo = SQLiteComicRepository(self._connection)
            self.chapter_repo = SQLiteChapterRepository(self._connection)
            self.job_repo = SQLiteCrawlJobRepository(self._connection)
            
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                super().__exit__(exc_type, exc_val, exc_tb)
            finally:
                if self._connection:
                    self._connection.close()  # Luôn đóng file DB an toàn tại đây
    
        def commit(self):
            if self._connection:
                self._connection.execute("COMMIT;")
    
        def rollback(self):
            if self._connection:
                self._connection.execute("ROLLBACK;")
    

* * *

## 2\. Dành riêng `SQLiteContext` cho luồng Đọc (Query Service)

`SQLiteContext` giờ đây chỉ làm một nhiệm vụ: Cung cấp kết nối Read-Only gọn nhẹ, không mang theo gánh nặng của hệ thống Repositories và Transaction.

## Context Đọc (`infrastructure/context.py`)
    
    
    import sqlite3
    
    class SQLiteReadContext:
        """Chỉ phục vụ cho việc đọc dữ liệu tốc độ cao"""
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._connection = None
    
        def __enter__(self):
            # Mở kết nối đọc độc lập, bật WAL để không bị block bởi luồng Ghi
            self._connection = sqlite3.connect(self.db_path, timeout=10.0)
            self._connection.execute("PRAGMA journal_mode=WAL;")
            return self._connection
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._connection:
                self._connection.close()
    

## Áp dụng vào Luồng Đọc (`application/comic_queries.py`)
    
    
    from infrastructure.context import SQLiteReadContext
    from .dtos import ComicDetailDTO
    
    class SQLiteComicQueryService:
        def __init__(self, read_context: SQLiteReadContext):
            self.read_context = read_context
    
        def get_comic_detail(self, comic_id: str) -> ComicDetailDTO:
            # Sử dụng context đọc gọn nhẹ, chạy SQL thô lấy dữ liệu thẳng ra UI
            with self.read_context as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, title FROM comics WHERE id = ?", (comic_id,))
                row = cursor.fetchone()
                return ComicDetailDTO(id=row[0], title=row[1]) if row else None
    

* * *

## 3\. Bản đồ Sử dụng sau khi Tái Cấu Trúc

Sự phân tách lúc này trở nên rạch ròi, trực quan và không còn hiện tượng lồng chéo:
    
    
                                     [ DATABASE FILE: comics.db ]
                                                  │
                          ┌───────────────────────┴───────────────────────┐
                          ▼                                               ▼
               [ LUỒNG GHI - COMMAND ]                         [ LUỒNG ĐỌC - QUERY ]
         ┌────────────────────────────────┐              ┌────────────────────────────────┐
         │      SQLiteUnitOfWork          │              │       SQLiteReadContext        │
         │  (Connection + Transaction)    │              │          (Read Only)           │
         └────────────────────────────────┘              └────────────────────────────────┘
                          │                                               │
                          ▼                                               ▼
              Repositories (SQL Write)                        Query Services (SQL Read)
    

* * *

## 4\. Khởi chạy tinh gọn trong `main.py`

Code khởi tạo ở entrypoint trở nên cực kỳ trong sáng và tuân thủ hoàn hảo nguyên lý SOLID:
    
    
    from infrastructure.sqlite_uow import SQLiteUnitOfWork
    from infrastructure.context import SQLiteReadContext
    from application.crawler_service import ResilientCrawlerApplicationService
    from application.comic_queries import SQLiteComicQueryService
    
    DB_PATH = "comics.db"
    
    def main():
        # ---- 1. VẬN HÀNH LUỒNG GHI (CRAWLER NGẦM) ----
        # UoW tự nhận db_path để quản lý toàn bộ vòng đời ghi
        uow = SQLiteUnitOfWork(DB_PATH) 
        crawler_service = ResilientCrawlerApplicationService(uow, sanitizer=...)
        
        crawler_service.crawl_and_process_chapter(comic_id="linh-vuc", ...)
    
    
        # ---- 2. VẬN HÀNH LUỒNG ĐỌC (API / USER VIEW) ----
        # Context đọc độc lập, chạy song song không sợ nghẽn file
        read_context = SQLiteReadContext(DB_PATH)
        query_service = SQLiteComicQueryService(read_context)
        
        comic_data = query_service.get_comic_detail("linh-vuc")
        print(comic_data)
    
    if __name__ == "__main__":
        main()
    

Sự điều chỉnh này của bạn đã đưa kiến trúc về trạng thái tối ưu nhất về mặt hiệu năng (Performance) đối với SQLite: Luồng ghi được gom vào một Transaction duy nhất trong UoW để ghi đĩa 1 lần; luồng đọc được tách hẳn ra một kênh riêng biệt (`WAL` mode) để User có thể xem truyện mượt mà ngay cả khi Crawler đang xả hàng triệu dòng dữ liệu vào DB.

Hệ thống hiện tại đã rất tinh gọn. Bạn có cần bản mẫu thiết kế hoàn chỉnh (Scaffold Code) của toàn bộ các file để đóng gói thành một project chạy được luôn không?