Để hoàn thiện ứng dụng crawl truyện theo đúng chuẩn DDD và SOLID, chúng ta sẽ tích hợp thêm:

  1. Unit of Work (UoW) Pattern: Quản lý Transaction cho SQLite3, đảm bảo tính toàn vẹn dữ liệu (Atomic). Nếu lỗi xảy ra giữa chừng khi đang cào, toàn bộ dữ liệu rác của lượt cào đó sẽ bị Rollback.
  2. Logging & Configuration (Độc lập môi trường): Sử dụng thư viện `logging` của Python và file `.env` (thông qua `pydantic-settings` hoặc `python-dotenv`) để quản lý thông tin kết nối an toàn.



* * *

## 🧱 Kiến Trúc Thư Mục Hoàn Chỉnh
    
    
    src/
    │
    ├── config/
    │   └── settings.py          # Quản lý cấu hình hệ thống (.env)
    │
    ├── domain/
    │   ├── models.py            # Chứa các Domain Model
    │   ├── services.py          # Thêm Interface UnitOfWork
    │   └── exceptions.py        # Các lỗi đặc thù của Domain (Cào lỗi, DB lỗi)
    │
    ├── infrastructure/
    │   ├── http_client.py
    │   ├── parsers.py
    │   ├── logging/
    │   │   └── logger.py        # Cấu hình log tập trung
    │   └── repositories/
    │       ├── sqlite_uow.py    # Triển khai Unit of Work cho SQLite3
    │       ├── sqlite_repo.py   
    │       └── mongo_repo.py    # Mongo không đổi (Không cần SQL transaction)
    │
    └── main.py                  # Điểm chạy ứng dụng
    

* * *

## 💻 Triển Khai Mã Nguồn Chi Tiết

## 1\. Lớp Cấu Hình (Configuration Layer)

Tạo file `.env` ở thư mục gốc của dự án:
    
    
    DB_TYPE=sqlite
    SQLITE_DB_PATH=novel_database.db
    MONGO_URI=mongodb://localhost:27017
    MONGO_DB_NAME=crawler_sync_db
    LOG_LEVEL=INFO
    

Đọc cấu hình bằng Python thuần để tránh phụ thuộc quá nhiều thư viện:
    
    
    # src/config/settings.py
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    class Settings:
        DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
        SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "novel_database.db")
        MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "crawler_sync_db")
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    settings = Settings()
    

## 2\. Lớp Hạ Tầng - Logging (Infrastructure)
    
    
    # src/infrastructure/logging/logger.py
    import logging
    import sys
    from src.config.settings import settings
    
    def setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', 
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        return logger
    

## 3\. Lớp Domain - Bổ Sung Unit of Work Interface

Theo DDD, Unit of Work chịu trách nhiệm quản lý Transaction nhằm duy trì tính toàn vẹn dữ liệu khi làm việc với các Repository.
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from typing import Any
    from src.domain.models import PageSource, Novel
    from src.infrastructure.logging.logger import setup_logger
    
    logger = setup_logger("DomainService")
    
    class NovelRepositoryInterface(ABC):
        @abstractmethod
        def save(self, novel: Novel, context: Any = None) -> None: pass
        
        @abstractmethod
        def get_by_url(self, url: str) -> Novel | None: pass
    
    class UnitOfWorkInterface(ABC):
        """Interface quản lý Transaction (SOLID - D)"""
        def __enter__(self) -> 'UnitOfWorkInterface': return self
        def __exit__(self, exc_type, exc_val, exc_tb): self.rollback()
        
        @abstractmethod
        def commit(self) -> None: pass
        @abstractmethod
        def rollback(self) -> None: pass
        @property
        @abstractmethod
        def novels(self) -> NovelRepositoryInterface: pass
    
    # Cập nhật Crawler Service sử dụng UoW
    class NovelCrawlerService:
        def __init__(
            self, 
            http_client: Any, 
            parser: Any,
            uow: UnitOfWorkInterface # Inject UoW thay vì Inject trực tiếp Repository
        ):
            self._http_client = http_client
            self._parser = parser
            self._uow = uow
    
        def crawl_and_save(self, url: str) -> Novel:
            logger.info(f"Bắt đầu kiểm tra URL: {url}")
            
            # Đọc dữ liệu không cần transaction lớn
            existing_novel = self._uow.novels.get_by_url(url)
            if existing_novel:
                logger.info(f"Truyện đã tồn tại trong DB: {existing_novel.title}")
                return existing_novel
    
            # 1. Fetch & Parse dữ liệu ngoài Transaction (Tránh block DB quá lâu)
            page_source = self._http_client.fetch(url)
            novel = self._parser.parse_novel(page_source)
            
            # 2. Thực hiện ghi dữ liệu an toàn trong Context Manager của Unit of Work
            with self._uow as uow:
                try:
                    logger.info(f"Đang lưu truyện '{novel.title}' vào DB...")
                    uow.novels.save(novel)
                    uow.commit() # Chỉ commit khi mọi thứ thành công
                    logger.info(f"Lưu thành công truyện '{novel.title}'")
                except Exception as e:
                    logger.error(f"Lỗi khi lưu DB, tiến hành Rollback. Chi tiết: {e}")
                    uow.rollback() # Khôi phục trạng thái cũ nếu lỗi nửa chừng
                    raise e
            return novel
    

## 4\. Lớp Hạ Tầng - Triển Khai SQLite Unit Of Work (Infrastructure)

Để đảm bảo câu lệnh SQL chia sẻ chung một _Connection/Transaction Context_ , chúng ta nạp `connection` vào qua Repository.
    
    
    # src/infrastructure/repositories/sqlite_repo.py
    import sqlite3
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import Novel, Chapter
    
    class SqliteNovelRepository(NovelRepositoryInterface):
        def __init__(self, conn: sqlite3.Connection):
            self._conn = conn
    
        def save(self, novel: Novel, context: sqlite3.Connection = None) -> None:
            cursor = self._conn.cursor()
            # Chèn Novel
            cursor.execute(
                "INSERT OR IGNORE INTO novels (title, author) VALUES (?, ?)",
                (novel.title, novel.author)
            )
            cursor.execute("SELECT id FROM novels WHERE title = ?", (novel.title,))
            novel_id = cursor.fetchone()[0]
    
            # Giả lập lỗi giữa chừng để test Transaction:
            # Nếu truyện có tên là "Lỗi", hệ thống sẽ văng lỗi trước khi chèn xong chapter
            if novel.title == "Lỗi":
                raise ValueError("Lỗi cố ý tạo ra để test Rollback Transaction!")
    
            # Chèn Chapters
            for ch in novel.chapters:
                cursor.execute(
                    "INSERT OR IGNORE INTO chapters (novel_id, title, content, url) VALUES (?, ?, ?, ?)",
                    (novel_id, ch.title, ch.content, ch.url)
                )
    
        def get_by_url(self, url: str) -> Novel | None:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT n.title, n.author FROM novels n
                JOIN chapters c ON n.id = c.novel_id WHERE c.url = ?
            """, (url,))
            row = cursor.fetchone()
            if not row: return None
            return Novel(title=row[0], author=row[1], chapters=[])
    
    
    
    # src/infrastructure/repositories/sqlite_uow.py
    import sqlite3
    from src.domain.services import UnitOfWorkInterface, NovelRepositoryInterface
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    
    class SqliteUnitOfWork(UnitOfWorkInterface):
        """Triển khai quản lý Transaction thực tế trên SQLite3"""
        def __init__(self, db_path: str):
            self._db_path = db_path
            self._conn = None
            self._repository = None
            self._create_tables()
    
        def _create_tables(self):
            # Hàm khởi tạo bảng cấu trúc ban đầu giống như bài trước
            conn = sqlite3.connect(self._db_path)
            with conn:
                conn.execute("CREATE TABLE IF NOT EXISTS novels (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, author TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS chapters (id INTEGER PRIMARY KEY AUTOINCREMENT, novel_id INTEGER, title TEXT, content TEXT, url TEXT UNIQUE)")
    
        def __enter__(self):
            self._conn = sqlite3.connect(self._db_path)
            self._conn.execute("BEGIN TRANSACTION;") # Bắt đầu cô lập dữ liệu
            self._repository = SqliteNovelRepository(self._conn)
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.rollback()
            else:
                self.commit()
            if self._conn:
                self._conn.close()
    
        def commit(self):
            if self._conn:
                self._conn.commit()
    
        def rollback(self):
            if self._conn:
                self._conn.rollback()
    
        @property
        def novels(self) -> NovelRepositoryInterface:
            if self._repository is None:
                # Tạo connection tạm nếu gọi đọc dữ liệu ngoài context manager
                temp_conn = sqlite3.connect(self._db_path)
                return SqliteNovelRepository(temp_conn)
            return self._repository
    

_Lưu ý: Đối với MongoDB, do bản chất lưu dạng Document lồng nhau (Embedded) — cả`Novel` và `Chapters` nằm gọn trong 1 document đơn lẻ — lệnh `update_one` hoặc `insert_map` đã tự mang tính chất Atomic (Nguyên tử) trên Single Document, nên bạn không cần viết cấu trúc Transaction lồng phức tạp như SQL._

* * *

## 5\. Khởi Chạy Hệ Thống Hoàn Chỉnh (`main.py`)
    
    
    # src/main.py
    from src.config.settings import settings
    from src.infrastructure.logging.logger import setup_logger
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    
    # Khởi tạo UoW / Repositories
    from src.infrastructure.repositories.sqlite_uow import SqliteUnitOfWork
    from src.infrastructure.repositories.mongo_repo import MongoNovelRepository 
    
    from src.domain.services import NovelCrawlerService
    
    logger = setup_logger("MainApp")
    
    def main():
        logger.info("--- Khởi động Ứng dụng Thiết kế chuẩn DDD & SOLID ---")
        
        # 1. Khởi tạo lõi Fetcher Client độc lập
        http_client = RequestsHttpClient(timeout=settings.SQLITE_DB_PATH)
        parser = TruyenFullParser()
        
        # 2. Lắp ráp dữ liệu theo cấu hình từ file .env
        if settings.DB_TYPE == "sqlite":
            logger.info(f"Sử dụng SQLite với cơ chế an toàn Transaction (UoW). File: {settings.SQLITE_DB_PATH}")
            uow = SqliteUnitOfWork(db_path=settings.SQLITE_DB_PATH)
        elif settings.DB_TYPE == "mongo":
            logger.info("Sử dụng cơ chế lưu trữ MongoDB.")
            # Với Mongo ta bọc qua một Fake/Wrapper UoW hoặc inject trực tiếp tùy thiết kế
            # Để giữ cấu trúc đơn giản, ta minh họa trực tiếp với SQLite UoW phía trên.
            raise NotImplementedError("Vui lòng cấu hình DB_TYPE=sqlite để test Transaction.")
    
        # 3. Inject Unit of Work vào Service điều phối
        crawler = NovelCrawlerService(http_client=http_client, parser=parser, uow=uow)
        
        # 4. Thực thi chạy thử nghiệm
        target_url = "https://example-truyen.com"
        try:
            novel = crawler.crawl_and_save(target_url)
            logger.info(f"Hoàn thành toàn bộ quy trình cho truyện: {novel.title}")
        except Exception as e:
            logger.critical(f"Ứng dụng gặp sự cố nhưng DB đã được bảo vệ an toàn. Chi tiết lỗi: {e}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🎯 Các điểm cải tiến cốt lõi đạt được:

  * Hạn chế dữ liệu rác (Atomicity): Nhờ có `SqliteUnitOfWork`, nếu tiến trình cào mạng bị ngắt quãng hoặc bị crash khi đang ghi dở danh sách chương (chương 5 lỗi trong tổng số 10 chương), toàn bộ dữ liệu của truyện đó ở phiên làm việc hiện tại sẽ bị xóa sạch khỏi SQLite, không để lại bản ghi mồ côi.
  * Ghi nhật ký hệ thống chuyên nghiệp: Loại bỏ hoàn toàn lệnh `print()` thô sơ, thay vào đó là hệ thống `logging` phân cấp giúp bạn dễ dàng debug khi ứng dụng chạy ngầm (Cronjob/Docker).



Hệ thống crawl của bạn hiện tại đã rất vững chắc về mặt kiến trúc. Bạn có muốn bổ sung thêm Cơ chế Retry (Tự động cào lại khi lỗi mạng mạng) hay Xử lý đa luồng (Multi-threading) cho kiến trúc đồng bộ này không?