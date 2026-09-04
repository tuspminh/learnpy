Để tích hợp tính năng Tải ảnh bìa (Download Cover) cho truyện mà vẫn đảm bảo đúng chuẩn DDD và SOLID, chúng ta cần phân tích nghiệp vụ này dưới góc nhìn kiến trúc:

  1. Về mặt Domain: Tải ảnh là một hành vi hạ tầng (I/O). Domain chỉ cần định nghĩa một giao diện (Interface) trừu tượng, ví dụ: `ImageDownloaderInterface`.
  2. Về mặt Infrastructure: Triển khai chi tiết việc tải ảnh bằng `requests` hoặc `shutil` và lưu vào ổ đĩa.
  3. Về mặt Data Flow: Khi lớp Parser cào được URL ảnh bìa (`cover_image_url`), luồng điều phối (`Application Service`) sẽ ra lệnh cho bộ tải ảnh hoạt động, sau đó cập nhật đường dẫn file cục bộ vào DB/File thay vì lưu URL thô của trang nguồn (tránh lỗi link ảnh die sau này).



* * *

## 🧱 1. Cập Nhật Interface Tại Lớp Domain (`src/domain/services.py`)

Bổ sung một Interface chịu trách nhiệm chuyên biệt cho việc tải hình ảnh độc lập với bộ cào HTML.
    
    
    # src/domain/services.py (Bổ sung thêm Interface)
    from abc import ABC, abstractmethod
    
    class ImageDownloaderInterface(ABC):
        """Interface chịu trách nhiệm tải hình ảnh (SOLID - S/I)"""
        @abstractmethod
        def download_cover(self, image_url: str, novel_title: str) -> Optional[str]:
            """Tải ảnh bìa và trả về đường dẫn file cục bộ (Local Path) sau khi lưu thành công"""
            pass
    

* * *

## 💻 2. Triển Khai Bộ Tải Ảnh Tại Lớp Hạ Tầng (`src/infrastructure/image_downloader.py`)

Bộ tải ảnh tuân thủ nghiêm ngặt Single Responsibility (S): Nó không quan tâm cấu trúc truyện ra sao, chỉ nhận URL ảnh và tên truyện để lưu trữ, đồng thời kết hợp bộ `logger` đã viết ở bước trước để kiểm soát lỗi (ví dụ: link ảnh 404).
    
    
    # src/infrastructure/image_downloader.py
    import os
    import re
    import requests
    from typing import Optional
    from src.domain.services import ImageDownloaderInterface
    from src.infrastructure.logging.logger import setup_logger
    
    logger = setup_logger(__name__)
    
    class LocalImageDownloader(ImageDownloaderInterface):
        """Triển khai bộ tải ảnh bìa lưu trữ tại thư mục cục bộ (SOLID - L)"""
        def __init__(self, download_dir: str = "cover_images"):
            self.download_dir = download_dir
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
    
        def _slugify(self, text: str) -> str:
            """Tạo tên file an toàn từ tên truyện"""
            return re.sub(r'[\s-]+', '-', re.sub(r'[^a-z0-9\s-]', '', text.lower())).strip('-')
    
        def download_cover(self, image_url: str, novel_title: str) -> Optional[str]:
            if not image_url or not image_url.startswith("http"):
                logger.warning(f"⏩ Bỏ qua tải ảnh bìa cho truyện '{novel_title}' do URL không hợp lệ: {image_url}")
                return None
    
            # Lấy phần mở rộng của file ảnh (jpg, png,...) từ URL
            file_extension = os.path.splitext(image_url.split('?')[0])[1]
            if not file_extension or len(file_extension) > 5:
                file_extension = ".jpg" # Mặc định nếu không bắt được extension
    
            file_name = f"{self._slugify(novel_title)}{file_extension}"
            local_path = os.path.join(self.download_dir, file_name)
    
            try:
                logger.info(f"📸 Đang tải ảnh bìa từ: {image_url}")
                response = requests.get(image_url, timeout=15, headers={"User-Agent": "NovelCrawler/2.0"})
                response.raise_for_status()
    
                with open(local_path, "wb") as f:
                    f.write(response.content)
                    
                logger.info(f"✅ Đã lưu ảnh bìa cục bộ tại: {local_path}")
                return local_path
                
            except Exception as e:
                logger.error(f"❌ Không thể tải ảnh bìa cho truyện '{novel_title}' từ {image_url}. Lỗi: {e}")
                return None
    

* * *

## 🔄 3. Tích Hợp Vào Lớp Điều Phối Ứng Dụng (`src/main.py`)

Chúng ta sẽ inject `ImageDownloaderInterface` vào Service điều phối để xử lý việc tải ảnh ngay khi cào xong thông tin chi tiết của truyện (`Novel Detail`).
    
    
    # src/main.py (Cập nhật từ phiên bản trước)
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers.factory import ParserFactory
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    from src.infrastructure.image_downloader import LocalImageDownloader
    from src.infrastructure.logging.logger import setup_logger
    
    logger = setup_logger("MainApp")
    
    class SmartNovelCrawlerApp:
        def __init__(self, http_client, parser_factory, repository, image_downloader):
            self.client = http_client
            self.factory = parser_factory
            self.repo = repository
            self.downloader = image_downloader # Inject bộ tải ảnh bìa vào đây
    
        def execute_novel_detail_crawl(self, novel_url: str):
            logger.info(f"📖 Bắt đầu cào chi tiết truyện: {novel_url}")
            
            parser = self.factory.get_parser(novel_url)
            source = self.client.fetch(novel_url)
            
            # 1. Parse thông tin chi tiết truyện từ HTML
            # Giả định Parser đã cập nhật để lấy thêm trường 'cover_image_url' đưa vào Detail DTO/Model
            detail = parser.parse_detail(source) 
            
            # 2. Xử lý tải ảnh bìa độc lập thông qua bộ Downloader
            if hasattr(detail, 'cover_image_url') and detail.cover_image_url:
                local_cover_path = self.downloader.download_cover(
                    image_url=detail.cover_image_url, 
                    novel_title=detail.title
                )
                # Thay đổi thuộc tính URL nguồn thành đường dẫn file local để lưu vào DB
                if local_cover_path:
                    detail.cover_image_url = local_cover_path 
    
            # 3. Lưu thông tin chi tiết truyện (đã kèm đường dẫn ảnh cục bộ) vào Repository
            self.repo.save_novel_detail(detail)
            logger.info(f"🎉 Hoàn thành cào và lưu trữ thông tin truyện: {detail.title}")
    
    if __name__ == "__main__":
        # Khởi tạo và lắp ráp hệ thống (Dependency Injection)
        app = SmartNovelCrawlerApp(
            http_client=RequestsHttpClient(),
            parser_factory=ParserFactory(),
            repository=SqliteNovelRepository(db_path="perfect_novel.db"),
            image_downloader=LocalImageDownloader(download_dir="downloaded_covers") # Cấu hình thư mục lưu ảnh
        )
        
        app.execute_novel_detail_crawl("https://truyenfull.vn")
    

* * *

## 🎯 Điểm Sáng Kiến Trúc SOLID Đạt Được:

  * Mở rộng (Open/Closed): Hiện tại ảnh đang được lưu ở ổ đĩa cục bộ (`LocalImageDownloader`). Nếu sau này bạn chuyển app lên Cloud và muốn lưu ảnh lên Amazon S3 hoặc Cloudinary, bạn chỉ cần tạo class `S3ImageDownloader` triển khai từ `ImageDownloaderInterface` rồi thay thế ở `main.py`. Toàn bộ code logic của `SmartNovelCrawlerApp` không phải sửa một dòng nào.
  * Tách biệt luồng lỗi: Nếu tải ảnh bìa thất bại (ví dụ: link ảnh của site nguồn bị lỗi 404), hệ thống sẽ ghi `logger.error` nhưng không làm gián đoạn hay làm dừng tiến trình cào dữ liệu chữ và danh sách chương của truyện.



Bạn có muốn tích hợp thêm Cơ chế nén dung lượng ảnh hoặc Chuyển đổi định dạng ảnh (như sang .webp) ngay khi tải về để tối ưu bộ nhớ lưu trữ cho app không?