Dưới đây là cấu trúc toàn bộ dự án crawler truyện được thiết kế theo mô hình Clean Architecture, DDD (Domain-Driven Design) và SOLID, áp dụng cho cấu trúc thư mục phẳng (flat structure - không dùng thư mục bọc `src/`) như bạn yêu cầu.

* * *

## 📂 Cấu Trúc Toàn Bộ Dự Án (Flat Structure)
    
    
    ├── config/                  # [Infrastructure] Quản lý cấu hình & biến môi trường
    │   ├── __init__.py
    │   └── settings.py          # Đọc file .env
    │
    ├── domain/                  # [Domain - Lõi hệ thống] Không chứa thư viện ngoài, chỉ chứa Python thuần
    │   ├── __init__.py
    │   ├── exceptions.py        # Các lỗi nghiệp vụ (Cào lỗi, dữ liệu bẩn, site lạ)
    │   ├── models.py            # Thực thể nghiệp vụ (Listing, Detail, Chapter...)
    │   └── services.py          # Giao diện (Interfaces) & Lớp điều phối cốt lõi (Domain Service)
    │
    ├── infrastructure/          # [Infrastructure - Hạ tầng] Chứa các công nghệ/thư viện cụ thể
    │   ├── __init__.py
    │   ├── dtos.py              # Lớp đóng gói dữ liệu thô cào được và Validate dữ liệu
    │   ├── http_client.py       # Fetcher Client (Requests/Aiohttp)
    │   ├── image_downloader.py  # Bộ tải ảnh bìa (Tái sử dụng HttpClient)
    │   │
    │   ├── logging/             # Ghi nhật ký hệ thống tập trung
    │   │   ├── __init__.py
    │   │   └── logger.py        # Setup Root Logger cho cấu trúc Flat
    │   │
    │   ├── parsers/             # Bộ phân tích mã nguồn HTML
    │   │   ├── __init__.py
    │   │   ├── factory.py       # ParserFactory nhận diện URL theo từng site truyện (SOLID - O)
    │   │   ├── truyenfull.py    # Xử lý bóc tách & phân trang TruyenFull
    │   │   └── metruyenchu.py   # Xử lý bóc tách & phân trang Mê Truyện Chữ
    │   │
    │   └── repositories/        # Các kho lưu trữ dữ liệu khác nhau (SOLID - L)
    │       ├── __init__.py
    │       ├── dummy_uow.py     # No-Op Unit of Work cho Mongo/File
    │       ├── file_repo.py     # Lưu dữ liệu phân cấp ra File JSON cục bộ
    │       ├── mongo_repo.py    # Lưu dữ liệu vào MongoDB
    │       ├── sqlite_repo.py   # Lưu dữ liệu vào SQLite3 (SQL thuần)
    │       └── sqlite_uow.py    # Quản lý Transaction an toàn cho SQLite3 (UoW)
    │
    ├── logs/                    # Thư mục tự động sinh để chứa file crawler.log
    ├── .env                     # File lưu cấu hình môi trường bảo mật
    ├── .gitignore
    ├── requirements.txt         # Thư viện sử dụng (requests, beautifulsoup4, pymongo, python-dotenv)
    └── main.py                  # [Composition Root] Điểm khởi chạy hệ thống & Dependency Injection
    

* * *

## 💻 Chi Tiết Triển Khai Các File Quan Trọng

## 1\. File Cấu Hình (`config/settings.py`)
    
    
    # config/settings.py
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    class Settings:
        # Chọn "sqlite", "mongo" hoặc "file"
        DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
        SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "novel_database.db")
        MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "crawler_db")
        FILE_OUTPUT_DIR: str = os.getenv("FILE_OUTPUT_DIR", "downloaded_novels")
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    settings = Settings()
    

## 2\. Lớp Domain Models (`domain/models.py`)
    
    
    # domain/models.py
    from dataclasses import dataclass
    from typing import List, Optional
    
    @dataclass(frozen=True)
    class PageSource:
        url: str
        content: str
        raw_bytes: bytes = b""  # Chứa dữ liệu nhị phân khi tải ảnh bìa
    
    @dataclass(frozen=True)
    class NovelListItem:
        title: str
        novel_url: str
    
    @dataclass
    class NovelDetail:
        title: str
        author: str
        description: str
        novel_url: str
        cover_image_url: Optional[str] = None
    
    @dataclass(frozen=True)
    class ChapterItem:
        title: str
        chapter_url: str
        order_index: int
    
    @dataclass
    class ChapterDetail:
        novel_url: str
        chapter_url: str
        title: str
        content: str
    

## 3\. Lớp Domain Services & Interfaces (`domain/services.py`)

_Tệp tin này hoàn toàn sạch, sử dụng`logging` chuẩn của Python làm Abstraction và không import từ lớp hạ tầng._
    
    
    # domain/services.py
    import logging
    from abc import ABC, abstractmethod
    from typing import Any, List, Optional, Tuple
    from domain.models import PageSource, NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    logger = logging.getLogger(__name__)
    
    class HttpClientInterface(ABC):
        @abstractmethod
        def fetch(self, url: str) -> PageSource: pass
    
    class NovelParserInterface(ABC):
        @abstractmethod
        def parse_listing_page(self, source: PageSource) -> Tuple[List[Any], Optional[str]]: pass
        @abstractmethod
        def parse_detail(self, source: PageSource) -> Any: pass
        @abstractmethod
        def parse_chapter_list_page(self, source: PageSource) -> Tuple[List[Any], Optional[str]]: pass
        @abstractmethod
        def parse_chapter_detail(self, source: PageSource) -> Any: pass
    
    class ImageDownloaderInterface(ABC):
        @abstractmethod
        def download_cover(self, image_url: str, novel_title: str) -> Optional[str]: pass
    
    class NovelRepositoryInterface(ABC):
        @abstractmethod
        def save_listing(self, items: List[NovelListItem]) -> None: pass
        @abstractmethod
        def save_novel_detail(self, detail: NovelDetail) -> None: pass
        @abstractmethod
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]) -> None: pass
        @abstractmethod
        def save_chapter_detail(self, detail: ChapterDetail) -> None: pass
    
    class UnitOfWorkInterface(ABC):
        def __enter__(self) -> 'UnitOfWorkInterface': return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type: self.rollback()
            else: self.commit()
        @abstractmethod
        def commit(self) -> None: pass
        @abstractmethod
        def rollback(self) -> None: pass
        @property
        @abstractmethod
        def novels(self) -> NovelRepositoryInterface: pass
    
    class NovelCrawlerService:
        """Lớp điều phối nghiệp vụ chính của hệ thống Crawler"""
        def __init__(self, http_client: HttpClientInterface, parser_factory: Any, uow: UnitOfWorkInterface, image_downloader: ImageDownloaderInterface):
            self._http_client = http_client
            self._parser_factory = parser_factory
            self._uow = uow
            self._downloader = image_downloader
    
        def crawl_all_listings(self, start_url: str) -> None:
            logger.info(f"🚀 Bắt đầu kích hoạt quy trình cào danh sách từ: {start_url}")
            parser = self._parser_factory.get_parser(start_url)
            current_url = start_url
            page_num = 1
            
            while current_url:
                logger.info(f"🕵️ Quét trang danh mục số {page_num}: {current_url}")
                source = self._http_client.fetch(current_url)
                dtos, next_page_url = parser.parse_listing_page(source)
                
                with self._uow as uow:
                    try:
                        domain_items = [dto.to_domain() for dto in dtos]
                        if domain_items:
                            uow.novels.save_listing(domain_items)
                        uow.commit()
                    except Exception as e:
                        uow.rollback()
                        logger.error(f"❌ Lỗi ghi DB tại trang danh mục {page_num}: {e}")
                        raise e
                current_url = next_page_url
                page_num += 1
    

## 4\. Lớp Hạ Tầng - Quản Lý Log Tự Động Xoay File Cho Ứng Dụng Flat (`infrastructure/logging/logger.py`)
    
    
    # infrastructure/logging/logger.py
    import logging
    import os
    import sys
    from logging.handlers import RotatingFileHandler
    from config.settings import settings
    
    def setup_logger(name: str = "") -> logging.Logger:
        """Cấu hình Root Logger cho kiến trúc phẳng. Mọi module khác tự thừa hưởng."""
        logger = logging.getLogger(name) if name else logging.getLogger()
        if logger.handlers:
            return logger
    
        formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
        # Console output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
        # File output với cơ chế tự động xoay file bảo vệ ổ đĩa
        try:
            if not os.path.exists("logs"): os.makedirs("logs")
            file_handler = RotatingFileHandler(filename="logs/crawler.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"⚠️ Không khởi tạo được File Logger: {e}")
        return logger
    

## 5\. Lớp Hạ Tầng - Thiết Kế Parser Factory Nhận Diện URL (`infrastructure/parsers/factory.py`)
    
    
    # infrastructure/parsers/factory.py
    from urllib.parse import urlparse
    from domain.services import NovelParserInterface
    from infrastructure.parsers.truyenfull import TruyenFullParser
    
    class ParserFactory:
        """Tự động phân tích tên miền để kích hoạt Parser phù hợp (SOLID - O)"""
        def __init__(self):
            self._parsers = {
                "truyenfull.vn": TruyenFullParser(),
                "truyenfull.io": TruyenFullParser()
            }
    
        def get_parser(self, url: str) -> NovelParserInterface:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            parser = self._parsers.get(domain)
            if not parser:
                raise ValueError(f"Hệ thống chưa hỗ trợ cào dữ liệu từ trang: {domain}")
            return parser
    

## 6\. Lớp Hạ Tầng - Tải Ảnh Bìa Tái Sử Dụng HttpClient (`infrastructure/image_downloader.py`)
    
    
    # infrastructure/image_downloader.py
    import os
    import re
    from typing import Optional
    from domain.services import ImageDownloaderInterface, HttpClientInterface
    
    class LocalImageDownloader(ImageDownloaderInterface):
        """Tải ảnh bìa, xử lý ghi ổ đĩa nhưng đẩy phần kết nối mạng cho HttpClient (SOLID - S/D)"""
        def __init__(self, http_client: HttpClientInterface, download_dir: str):
            self._http_client = http_client
            self._download_dir = download_dir
            if not os.path.exists(download_dir): os.makedirs(download_dir)
    
        def download_cover(self, image_url: str, novel_title: str) -> Optional[str]:
            if not image_url or not image_url.startswith("http"): return None
            slug_name = re.sub(r'[\s-]+', '-', re.sub(r'[^a-z0-9\s-]', '', novel_title.lower())).strip('-')
            local_path = os.path.join(self._download_dir, f"{slug_name}.jpg")
            
            try:
                # Tái sử dụng client
                page_source = self._http_client.fetch(image_url)
                with open(local_path, "wb") as f:
                    f.write(page_source.raw_bytes)
                return local_path
            except Exception:
                return None
    

## 7\. Điểm Lắp Ghép & Khởi Chạy Hệ Thống (`main.py`)
    
    
    # main.py
    from config.settings import settings
    from infrastructure.logging.logger import setup_logger
    
    # Import thành phần hạ tầng
    from infrastructure.http_client import RequestsHttpClient
    from infrastructure.parsers.factory import ParserFactory
    from infrastructure.image_downloader import LocalImageDownloader
    
    # Import các kho dữ liệu tùy chọn
    from infrastructure.repositories.sqlite_uow import SqliteUnitOfWork
    from infrastructure.repositories.mongo_repo import MongoNovelRepository
    from infrastructure.repositories.file_repo import FileLocalRepository
    from infrastructure.repositories.dummy_uow import DummyUnitOfWork
    
    from domain.services import NovelCrawlerService
    
    def main():
        # 1. Kích hoạt Logger hệ thống (Vì là dự án phẳng, gọi không đối số để setup Root Logger)
        setup_logger()
        
        # 2. Khởi tạo một HTTP Client dùng chung duy nhất
        shared_client = RequestsHttpClient(timeout=15)
        
        # 3. Khởi tạo kho lưu trữ linh hoạt dựa trên file .env (Dependency Injection)
        if settings.DB_TYPE == "sqlite":
            uow = SqliteUnitOfWork(db_path=settings.SQLITE_DB_PATH)
        elif settings.DB_TYPE == "mongo":
            mongo_repo = MongoNovelRepository(connection_string=settings.MONGO_URI, db_name=settings.MONGO_DB_NAME)
            uow = DummyUnitOfWork(repository=mongo_repo)
        elif settings.DB_TYPE == "file":
            file_repo = FileLocalRepository(output_dir=settings.FILE_OUTPUT_DIR)
            uow = DummyUnitOfWork(repository=file_repo)
        else:
            raise ValueError(f"Loại lưu trữ DB_TYPE={settings.DB_TYPE} không hợp lệ!")
    
        # 4. Khởi tạo bộ tải ảnh bìa kết nối qua shared_client
        image_downloader = LocalImageDownloader(http_client=shared_client, download_dir=settings.FILE_OUTPUT_DIR)
    
        # 5. Inject toàn bộ hạ tầng vào lõi Domain Service
        crawler_app = NovelCrawlerService(
            http_client=shared_client,
            parser_factory=ParserFactory(),
            uow=uow,
            image_downloader=image_downloader
        )
    
        # 6. Bắt đầu vận hành
        seed_url = "https://truyenfull.vn"
        crawler_app.crawl_all_listings(seed_url)
    
    if __name__ == "__main__":
        main()
    

* * *

## 🎨 Tóm Tắt Các Nguyên Lý Đã Đạt Được Đầy Đủ

  1. Clean Architecture: Toàn bộ luồng phụ thuộc hướng từ ngoài vào trong. Lớp `domain/` hoàn toàn độc lập, nằm ở lõi trung tâm. Lớp `infrastructure/` bao bọc bên ngoài và triển khai các thư viện cụ thể như `requests`, `sqlite3`, `pymongo`, `BeautifulSoup`.
  2. Domain-Driven Design (DDD): Tách dữ liệu phân cấp lớn (`Listing`, `Detail`, `Chapter`) tránh nghẽn RAM, điều phối thông qua mô hình Domain Service kết hợp bảo vệ dữ liệu toàn vẹn qua Unit of Work Pattern.
  3. SOLID:

     * S (Single Responsibility): Tách nhỏ Client kết nối mạng, Bộ tải ảnh, Bộ xoay file log và các lớp Parser chuyên biệt.
     * O (Open/Closed): Thêm trang truyện mới chỉ cần viết file Parser mới rồi đăng ký vào `ParserFactory`, hoàn toàn không sửa đổi mã nguồn lõi.
     * L (Liskov Substitution): 3 loại Repository (SQLite, Mongo, File) có thể tự do hoán đổi vị trí cho nhau trong `main.py` mà không làm đảo lộn hành vi ứng dụng.
     * I (Interface Segregation): Các Interface phân tách thành các bản hợp đồng nhỏ, độc lập.
     * D (Dependency Inversion): Lớp dịch vụ `NovelCrawlerService` chỉ giao tiếp qua các lớp trừu tượng (Interface) và nhận các thực thể thật thông qua kĩ thuật Constructor Dependency Injection từ file `main.py`.




Cấu trúc kiến trúc toàn diện của dự án crawl truyện đã hoàn thiện và rất vững chắc. Bạn có muốn tôi viết chi tiết mã nguồn cho file_repo.py (Lưu JSON cục bộ), hoặc file dtos.py (Đóng gói và validate dữ liệu) để bạn có thể chạy thực tế ngay không?