Bạn nhận xét hoàn toàn chính xác. Việc một file thuộc lớp Domain Core (`src/domain/services.py`) đi `import` trực tiếp module `setup_logger` từ lớp Infrastructure (`src/infrastructure/logging/logger.py`) là một lỗi vi phạm nghiêm trọng quy tắc Dependency Inversion (D trong SOLID) và kiến trúc DDD / Clean Architecture.

Theo đúng chuẩn DDD: Lớp Domain phải là trung tâm, hoàn toàn "sạch" và không được phụ thuộc vào bất kỳ chi tiết hạ tầng nào.

Để sửa lỗi này, chúng ta có 2 cách tiếp cận chuẩn DDD:

  1. Cách 1 (Chuẩn DDD thuần): Định nghĩa một `LoggerInterface` trừu tượng trong Domain, sau đó Inject triển khai thực tế từ Infrastructure vào (giống như cách làm với HttpClient hay Repository).
  2. Cách 2 (Thực tế và gọn nhẹ trong Python): Sử dụng thư viện built-in `logging.getLogger(__name__)` chuẩn của Python ngay tại Domain. Bản thân thư viện `logging` gốc của Python đóng vai trò như một Abstraction Layer. Việc cấu hình ghi ra file hay console (Handlers) sẽ do Infrastructure thiết lập ở điểm khởi chạy (`main.py`).



Dưới đây là cách tái cấu trúc lại tệp `src/domain/services.py` theo Cách 2 (phổ biến và tối ưu nhất trong Python) để xóa bỏ hoàn toàn sự phụ thuộc vào hạ tầng.

* * *

## 💻 Lớp Domain Sạch Tuyệt Đối (`src/domain/services.py`)

Bây giờ file này không còn bất kỳ dòng import nào liên quan đến `src/infrastructure`.
    
    
    # src/domain/services.py
    import logging  # Sử dụng thư viện chuẩn của Python làm Abstraction
    from abc import ABC, abstractmethod
    from typing import Any, List, Optional, Tuple
    from src.domain.models import (
        PageSource, 
        NovelListItem, 
        NovelDetail, 
        ChapterItem, 
        ChapterDetail
    )
    
    # Khởi tạo logger độc lập. Lớp Domain chỉ sinh log ra hệ thống, 
    # còn việc log này đi đâu (file, console, elk) sẽ do Infrastructure cấu hình sau.
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
        @abstractmethod
        def get_by_url(self, url: str) -> Optional[NovelDetail]: pass
    
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
        """Domain Service hoàn toàn cô lập và trong sạch theo chuẩn DDD"""
        def __init__(
            self, 
            http_client: HttpClientInterface, 
            parser_factory: Any, 
            uow: UnitOfWorkInterface,
            image_downloader: ImageDownloaderInterface
        ):
            self._http_client = http_client
            self._parser_factory = parser_factory
            self._uow = uow
            self._downloader = image_downloader
    
        def crawl_novel_workflow(self, start_url: str) -> None:
            logger.info(f"🚀 Bắt đầu kích hoạt quy trình cào từ URL gốc: {start_url}")
            
            parser = self._parser_factory.get_parser(start_url)
            current_url = start_url
            page_num = 1
            
            while current_url:
                logger.info(f"🕵️ Quét trang danh mục số {page_num}: {current_url}")
                source = self._http_client.fetch(current_url)
                dtos, next_page_url = parser.parse_listing_page(source)
                
                with self._uow as uow:
                    try:
                        domain_items = []
                        for dto in dtos:
                            try:
                                domain_items.append(dto.to_domain())
                            except Exception as val_err:
                                logger.warning(f"⏩ Bỏ qua dòng dữ liệu bẩn từ DTO: {val_err}")
                                
                        if domain_items:
                            uow.novels.save_listing(domain_items)
                            
                        uow.commit()
                    except Exception as db_err:
                        uow.rollback()
                        logger.error(f"❌ Thất bại khi lưu trang danh mục {page_num}: {db_err}")
                        raise db_err
    
                current_url = next_page_url
                page_num += 1
                
            logger.info("🎉 Quy trình cào danh mục hoàn tất thành công!")
    

* * *

## 🔧 2. Cấu Hình Logger Tại Điểm Khởi Chạy (`src/main.py`)

Để các đoạn code `logger.info` hay `logger.error` ở lớp Domain thực sự ghi ra file hay hiển thị màu sắc trên Console, chúng ta chỉ cần kích hoạt cấu hình của Infrastructure ở Root của ứng dụng (`main.py`) trước khi Service chạy.
    
    
    # src/main.py
    from src.config.settings import settings
    # Kích hoạt thiết lập log của lớp hạ tầng ngay tại đây
    from src.infrastructure.logging.logger import setup_logger
    
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers.factory import ParserFactory
    from src.infrastructure.repositories.sqlite_uow import SqliteUnitOfWork
    from src.infrastructure.image_downloader import LocalImageDownloader
    from src.domain.services import NovelCrawlerService
    
    def main():
        # 1. Khởi tạo cấu hình log hệ thống (Đăng ký các Handler ghi file/console vào root logger)
        setup_logger("src") # Truyền root namespace của dự án
        
        # 2. Khởi tạo hạ tầng
        shared_client = RequestsHttpClient()
        
        app = NovelCrawlerService(
            http_client=shared_client,
            parser_factory=ParserFactory(),
            uow=SqliteUnitOfWork(db_path=settings.SQLITE_DB_PATH),
            image_downloader=LocalImageDownloader(http_client=shared_client)
        )
        
        app.crawl_novel_workflow("https://truyenfull.vn")
    
    if __name__ == "__main__":
        main()
    

Rất cảm ơn bạn đã chỉ ra điểm bất hợp lý này. Hiện tại cấu trúc luồng phụ thuộc đã đi đúng từ ngoài vào trong (Infrastructure phụ thuộc Domain), giữ cho nhân nghiệp vụ của ứng dụng hoàn toàn độc lập và dễ dàng Unit Test.

Để tiếp tục hoàn thiện, bạn có muốn tối ưu nốt phần Custom Domain Exceptions (tự định nghĩa các lỗi nghiệp vụ riêng trong domain thay vì dùng các Exception chung của Python) không?