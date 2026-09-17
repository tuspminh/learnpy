Trong kiến trúc DDD, Fetcher (hoặc `Downloader`, `HttpService`) thuộc tầng Infrastructure. Nó chịu trách nhiệm giao tiếp với môi trường Internet (gửi HTTP request, bypass Cloudflare, fake User-Agent, xoay tua Proxy) để mang mã HTML thô về cho ứng dụng.

Điểm mấu chốt là Fetcher không được biết về BeautifulSoup hay quy tắc bóc tách HTML, nó chỉ tập trung vào việc lấy dữ liệu thô.

* * *

## 1\. Tầng Domain (Interface Định Hướng Nghiệp Vụ)

Để tầng Application không bị phụ thuộc vào thư viện `requests` hay `httpx`, ta tạo một Interface ở tầng Domain hoặc Application (cơ chế Dependency Inversion).

## `domain/services/interfaces.py`
    
    
    from abc import ABC, abstractmethod
    
    class INovelFetcher(ABC):
        """Giao diện chuẩn cho Fetcher, độc lập với thư viện mạng cụ thể"""
        
        @abstractmethod
        def fetch_html(self, url: str) -> str:
            """Nhận vào một URL và trả về chuỗi mã nguồn HTML thô"""
            pass
    

* * *

## 2\. Tầng Infrastructure (Triển khai kỹ thuật)

Nơi bạn chọn thư viện thực thi (ví dụ: `requests`, `httpx` hoặc `playwright` cho các trang chạy Javascript heavy).

## `infrastructure/fetchers/http_fetcher.py`
    
    
    import random
    import time
    import requests
    from domain.services.interfaces import INovelFetcher
    
    class CloudflareBypassFetcher(INovelFetcher):
        """Fetcher chuyên nghiệp có cấu hình Fake User-Agent và cơ chế chống block nhẹ"""
        
        def __init__(self, timeout: int = 10, max_retries: int = 3):
            self.timeout = timeout
            self.max_retries = max_retries
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
    
        def _get_headers(self) -> dict:
            return {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com"
            }
    
        def fetch_html(self, url: str) -> str:
            for attempt in range(self.max_retries):
                try:
                    # Giãn cách thời gian ngẫu nhiên để tránh bị phát hiện là bot
                    time.sleep(random.uniform(1.0, 2.5))
                    
                    response = requests.get(
                        url, 
                        headers=self._get_headers(), 
                        timeout=self.timeout
                    )
                    
                    # Trả về HTML nếu request thành công
                    if response.status_code == 200:
                        return response.text
                    
                    # Nếu gặp lỗi HTTP (ví dụ 429 Too Many Requests)
                    response.raise_for_status()
                    
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Thất bại khi tải URL {url} sau {self.max_retries} lần thử. Lỗi: {e}")
                    continue
    

* * *

## 3\. Tầng Application (Lắp ghép Fetcher và Parser)

Bây giờ, Use Case sẽ nhận cả `Fetcher` và `Parser` dưới dạng Dependency Injection (truyền từ ngoài vào). Điều này giúp code cực kỳ linh hoạt và dễ viết Unit Test (có thể mock Fetcher mà không cần mạng thật).

## `application/crawl_use_case.py`
    
    
    from domain.entities import Novel
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    
    class CrawlNovelUseCase:
        """Use Case kết hợp giữa Fetcher (Lấy dữ liệu) và Parser (Phân tích dữ liệu)"""
        
        def __init__(self, fetcher: INovelFetcher):
            # Inject Fetcher thông qua constructor
            self.fetcher = fetcher
        
        def execute(self, url: str) -> Novel:
            # 1. Chọn đúng parser dựa trên domain của URL
            parser = ParserFactory.get_parser(url)
            
            # 2. Sử dụng Fetcher được cấu hình sẵn để lấy HTML
            raw_html = self.fetcher.fetch_html(url)
            
            # 3. Đẩy HTML thô vào Parser để nhận về Domain Entity
            novel = parser.parse_novel_info(raw_html, source_url=url)
            
            return novel
    

* * *

## 4\. Khởi chạy ứng dụng (Main Entry Point)
    
    
    if __name__ == "__main__":
        from infrastructure.fetchers.http_fetcher import CloudflareBypassFetcher
        
        # 1. Khởi tạo hạ tầng (Infrastructure)
        my_fetcher = CloudflareBypassFetcher(max_retries=3)
        
        # 2. Inject vào tầng nghiệp vụ ứng dụng (Application)
        crawler_service = CrawlNovelUseCase(fetcher=my_fetcher)
        
        # 3. Chạy luồng xử lý chính
        target_url = "https://truyenfull.io"
        try:
            novel_data = crawler_service.execute(target_url)
            print(f"Crawl thành công truyện: {novel_data.title} - Tác giả: {novel_data.author}")
            print(f"Tìm thấy tổng cộng {len(novel_data.chapters)} chương.")
        except Exception as error:
            print(f"Quá trình crawl thất bại: {error}")
    

Nếu bạn muốn mở rộng hệ thống, hãy cho tôi biết:

  * Bạn có cần chạy crawl song song (Asynchronous / Multithreading) để tăng tốc độ tải chương truyện không?
  * Trang truyện bạn đang nhắm tới có bắt buộc phải render Javascript (dùng Playwright / Selenium) mới lấy được nội dung hay không?