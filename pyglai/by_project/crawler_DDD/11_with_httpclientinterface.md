Hoàn toàn có thể và nên tái sử dụng `HttpClientInterface` để tải ảnh bìa.

Dưới đây là cách tái cấu trúc lại lớp hạ tầng theo đúng tinh thần SOLID (đặc biệt là _Interface Segregation_ và _Dependency Inversion_). Việc này mang lại 2 lợi ích lớn:

  1. Tái sử dụng cấu hình: Mọi thiết lập về `User-Agent`, `Timeout`, hay cơ chế `Proxy/Cookie` của HttpClient cũ sẽ được áp dụng trực tiếp khi tải ảnh mà bạn không cần phải cấu hình lại.
  2. Quản lý tập trung: Lớp Downloader chỉ tập trung vào nghiệp vụ xử lý file và lưu trữ (Ổ đĩa, S3, v.v.), còn việc kết nối mạng được đẩy lại cho HttpClient.



* * *

## 💻 1. Cập Nhật HttpClient Để Trả Về Dữ Liệu Dạng Nhị Phân (`bytes`)

Để tải được tệp tin (ảnh, file pdf, v.v.), `HttpClient` cần hỗ trợ trả về dữ liệu thô dạng `bytes` thay vì chỉ trả về `text` (HTML).

Chúng ta cập nhật lớp `PageSource` và `HttpClientInterface` trong `src/domain/services.py`:
    
    
    # src/domain/models.py (Cập nhật PageSource để lưu cả text lẫn bytes nếu cần)
    from dataclasses import dataclass
    
    @dataclass(frozen=True)
    class PageSource:
        url: str
        content: str       # Dùng cho HTML parse
        raw_bytes: bytes = b""  # Thêm trường này để chứa dữ liệu ảnh thô
    

Cập nhật `RequestsHttpClient` tại lớp hạ tầng:
    
    
    # src/infrastructure/http_client.py
    import requests
    from src.domain.services import HttpClientInterface
    from src.domain.models import PageSource
    
    class RequestsHttpClient(HttpClientInterface):
        def __init__(self, timeout: int = 10):
            self._timeout = timeout
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "NovelCrawler/2.0"})
    
        def fetch(self, url: str) -> PageSource:
            try:
                response = self._session.get(url, timeout=self._timeout)
                response.raise_for_status()
                
                # Trả về đối tượng PageSource mang cả text (HTML) lẫn bytes (Ảnh)
                return PageSource(
                    url=url, 
                    content=response.text, 
                    raw_bytes=response.content
                )
            except requests.RequestException as e:
                raise RuntimeError(f"Lỗi khi kết nối tới URL {url}: {str(e)}")
    

* * *

## 💻 2. Tái Cấu Trúc Downloader Để Inject HttpClient Vào (`SOLID - D`)

Lớp `LocalImageDownloader` bây giờ sẽ không tự tạo request nữa, mà nhận vào một `HttpClientInterface` thông qua hàm khởi tạo (Constructor Injection).
    
    
    # src/infrastructure/image_downloader.py
    import os
    import re
    from typing import Optional
    from src.domain.services import ImageDownloaderInterface, HttpClientInterface
    from src.infrastructure.logging.logger import setup_logger
    
    logger = setup_logger(__name__)
    
    class LocalImageDownloader(ImageDownloaderInterface):
        """Bộ tải ảnh bìa tái sử dụng HttpClient có sẵn (SOLID - D)"""
        def __init__(self, http_client: HttpClientInterface, download_dir: str = "cover_images"):
            self._http_client = http_client  # Inject HttpClient vào đây
            self.download_dir = download_dir
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
    
        def _slugify(self, text: str) -> str:
            return re.sub(r'[\s-]+', '-', re.sub(r'[^a-z0-9\s-]', '', text.lower())).strip('-')
    
        def download_cover(self, image_url: str, novel_title: str) -> Optional[str]:
            if not image_url or not image_url.startswith("http"):
                logger.warning(f"⏩ Bỏ qua tải ảnh bìa cho '{novel_title}' do URL không hợp lệ.")
                return None
    
            # Định dạng tên file cục bộ
            file_extension = os.path.splitext(image_url.split('?')[0])[1] or ".jpg"
            file_name = f"{self._slugify(novel_title)}{file_extension}"
            local_path = os.path.join(self.download_dir, file_name)
    
            try:
                logger.info(f"📸 Đang tận dụng HttpClient để tải ảnh bìa từ: {image_url}")
                
                # Tái sử dụng HttpClient để lấy dữ liệu nhị phân (bytes)
                page_source = self._http_client.fetch(image_url)
                
                # Tiến hành ghi dữ liệu thô ra ổ đĩa cục bộ
                with open(local_path, "wb") as f:
                    f.write(page_source.raw_bytes)
                    
                logger.info(f"✅ Đã lưu ảnh bìa thành công tại: {local_path}")
                return local_path
                
            except Exception as e:
                logger.error(f"❌ Lỗi khi tải ảnh bìa qua HttpClient cho truyện '{novel_title}': {e}")
                return None
    

* * *

## 🎮 3. Lắp Ghép Trong `main.py`

Khi khởi tạo hệ thống, bạn chỉ cần tạo duy nhất một thực thể `HttpClient`, sau đó chia sẻ (share) nó cho cả lớp App điều phối crawler và lớp Downloader ảnh bìa.
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers.factory import ParserFactory
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    from src.infrastructure.image_downloader import LocalImageDownloader
    from src.main_app import SmartNovelCrawlerApp  # Giả định lớp App của bạn ở đây
    
    def main():
        # 1. Khởi tạo một HttpClient duy nhất (Dùng chung cấu hình, session, proxy nếu có)
        shared_http_client = RequestsHttpClient(timeout=15)
        
        # 2. Inject HttpClient vào Image Downloader
        image_downloader = LocalImageDownloader(
            http_client=shared_http_client, 
            download_dir="downloaded_covers"
        )
        
        # 3. Lắp ráp toàn bộ ứng dụng crawler
        app = SmartNovelCrawlerApp(
            http_client=shared_http_client,
            parser_factory=ParserFactory(),
            repository=SqliteNovelRepository(db_path="perfect_novel.db"),
            image_downloader=image_downloader
        )
        
        # Chạy quy trình cào
        app.execute_novel_detail_crawl("https://truyenfull.vn")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🎯 Ưu điểm tuyệt đối của giải pháp này:

  * Single Responsibility (S): Lớp Downloader giờ đây hoàn thành đúng nghĩa vụ của nó: Nó chỉ lo về đường dẫn file, đặt tên file (slugify) và lưu trữ tệp tin. Nó hoàn toàn được "giải phóng" khỏi logic kết nối HTTP, `headers`, hay `timeout`.
  * Dễ dàng bảo trì (Maintainability): Nếu sau này trang truyện chặn cào bằng cách bắt đăng nhập (Cookie) hoặc Cloudflare, bạn chỉ cần xử lý nâng cấp duy nhất ở class `RequestsHttpClient`. Cả lớp parse HTML lẫn lớp tải ảnh bìa đều sẽ tự động thừa hưởng khả năng vượt tường lửa đó mà không cần sửa một dòng code nào.



Nếu bạn muốn tiếp tục tối ưu, hãy cho tôi biết: Bạn có muốn tích hợp thêm Cơ chế lưu ảnh tạm (Cache) để nếu ảnh bìa đó đã được tải về từ trước thì không cần gọi HttpClient tải lại lần 2 không?