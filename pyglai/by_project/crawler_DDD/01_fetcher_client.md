Để xây dựng một hệ thống crawl truyện theo DDD (Domain-Driven Design) và SOLID, chúng ta cần chia hệ thống thành các lớp rõ ràng: Domain (chứa nghiệp vụ cốt lõi), Infrastructure (chứa mã kết nối mạng, client), và Application (điều phối luồng đi).

Dưới đây là kiến trúc và mã nguồn chi tiết bằng Python cho Fetcher Client (dùng để cào dữ liệu thô) và Fetcher cho Crawler (phần xử lý logic lấy dữ liệu).

* * *

## 🧱 Kiến Trúc Thư Mục (DDD)
    
    
    src/
    │
    ├── domain/                  # Lớp nghiệp vụ (Không phụ thuộc vào thư viện ngoài)
    │   ├── models.py            # Chứa thực thể Novel, Chapter, PageSource
    │   └── services.py          # Logic crawler cốt lõi
    │
    ├── infrastructure/          # Lớp triển khai công nghệ (HTTP client, Thư viện parse)
    │   ├── http_client.py       # Fetcher Client (Requests/Aiohttp)
    │   └── parsers.py           # Parser chuyển HTML thành Domain Model
    │
    └── main.py                  # Điểm chạy ứng dụng (Dependency Injection)
    

* * *

## 💻 Triển Khai Mã Nguồn

## 1\. Lớp Domain (Domain Layer)

Định nghĩa các Interface (Abstractions) và Entities. Tuân thủ Dependency Inversion Principle (D) trong SOLID: Lớp cao không phụ thuộc lớp thấp, cả hai phụ thuộc vào Abstraction.
    
    
    # src/domain/models.py
    from dataclasses import dataclass
    from typing import List
    
    @dataclass(frozen=True)
    class PageSource:
        """Mã nguồn thô của trang web (HTML)"""
        url: str
        content: str
    
    @dataclass
    class Chapter:
        title: str
        content: str
        url: str
    
    @dataclass
    class Novel:
        title: str
        author: str
        chapters: List[Chapter]
    
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from src.domain.models import PageSource, Novel
    
    class HttpClientInterface(ABC):
        """Interface cho Fetcher Client - Tuân thủ Interface Segregation (I)"""
        @abstractmethod
        def fetch(self, url: str) -> PageSource:
            pass
    
    class NovelParserInterface(ABC):
        """Interface cho Parser - Tuân thủ Single Responsibility (S)"""
        @abstractmethod
        def parse_novel(self, source: PageSource) -> Novel:
            pass
    
    class NovelCrawlerService:
        """Fetcher cho Crawler (Application/Domain Service) 
        Điều phối việc fetch và parse, hoàn toàn độc lập với công nghệ HTTP hay BeautifulSoup.
        """
        def __init__(self, http_client: HttpClientInterface, parser: NovelParserInterface):
            self._http_client = http_client
            self._parser = parser
    
        def crawl_novel(self, url: str) -> Novel:
            # 1. Fetch dữ liệu thô (Dùng client)
            page_source = self._http_client.fetch(url)
            # 2. Parse dữ liệu sang Domain Model
            novel = self._parser.parse_novel(page_source)
            return novel
    

## 2\. Lớp Hạ Tầng (Infrastructure Layer)

Triển khai chi tiết các Interface từ lớp Domain. Bạn có thể dễ dàng thay đổi từ `requests` sang `aiohttp` hoặc `playwright` mà không làm ảnh hưởng tới logic crawl truyện nhờ Open/Closed Principle (O).
    
    
    # src/infrastructure/http_client.py
    import requests
    from src.domain.services import HttpClientInterface
    from src.domain.models import PageSource
    
    class RequestsHttpClient(HttpClientInterface):
        """Fetcher Client sử dụng thư viện Requests"""
        def __init__(self, timeout: int = 10):
            self._timeout = timeout
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "NovelCrawler/1.0"})
    
        def fetch(self, url: str) -> PageSource:
            try:
                response = self._session.get(url, timeout=self._timeout)
                response.raise_for_status()
                return PageSource(url=url, content=response.text)
            except requests.RequestException as e:
                # Ở đây có thể raise một Custom Domain Exception nếu cần
                raise RuntimeError(f"Lỗi khi fetch URL {url}: {str(e)}")
    
    
    
    # src/infrastructure/parsers.py
    from bs4 import BeautifulSoup
    from src.domain.services import NovelParserInterface
    from src.domain.models import PageSource, Novel
    
    class TruyenFullParser(NovelParserInterface):
        """Parser riêng cho một trang web cụ thể (Ví dụ: TruyenFull)"""
        def parse_novel(self, source: PageSource) -> Novel:
            soup = BeautifulSoup(source.content, 'html.parser')
            
            # Logic bóc tách HTML theo cấu trúc của site (Đây là ví dụ giả định)
            title = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Unknown"
            author = soup.find('a', class_='author').text.strip() if soup.find('a', class_='author') else "Unknown"
            
            return Novel(title=title, author=author, chapters=[])
    

## 3\. Khởi tạo và Chạy Ứng dụng (Composition Root)

Nơi lắp ghép các thành phần lại với nhau (Dependency Injection).
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    from src.domain.services import NovelCrawlerService
    
    def main():
        # 1. Khởi tạo các phần phụ thuộc (Dependencies)
        http_client = RequestsHttpClient(timeout=5)
        parser = TruyenFullParser()
        
        # 2. Inject vào Crawler Service
        crawler = NovelCrawlerService(http_client=http_client, parser=parser)
        
        # 3. Chạy crawl
        target_url = "https://example-truyen-website.com"
        try:
            novel = crawler.crawl_novel(target_url)
            print(f"Crawl thành công truyện: {novel.title} - Tác giả: {novel.author}")
        except Exception as e:
            print(f"Thất bại: {e}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🎯 Phân Tích Sự Tuân Thủ SOLID & DDD Trong Thiết Kế Trên

  * Single Responsibility (S): `RequestsHttpClient` chỉ làm duy nhất một việc là lấy HTML thô. `TruyenFullParser` chỉ làm việc bóc tách HTML. `NovelCrawlerService` chỉ điều phối luồng.
  * Open/Closed (O): Nếu bạn muốn crawl một trang web mới (ví dụ: _Metruyenchu_), bạn chỉ cần tạo lớp `MetruyenchuParser` kế thừa từ `NovelParserInterface` và truyền vào `NovelCrawlerService`. Không cần sửa lại code cũ.
  * Liskov Substitution (L): Bất kỳ class nào kế thừa `HttpClientInterface` (như `AiohttpHttpClient`, `PlaywrightClient`) đều có thể thay thế cho `RequestsHttpClient` mà không làm lỗi hệ thống.
  * Interface Segregation (I): Các interface được chia nhỏ theo đúng cụm chức năng (`HttpClientInterface` tách biệt hoàn toàn với `NovelParserInterface`).
  * Dependency Inversion (D): Lớp dịch vụ `NovelCrawlerService` không trực tiếp import hay phụ thuộc vào thư viện `requests` hay `BeautifulSoup`. Nó chỉ phụ thuộc vào các Interface trừu tượng.



Nếu bạn muốn nâng cấp hệ thống này, hãy cho tôi biết:

  * Bạn có cần cấu hình chạy bất đồng bộ (Asyncio/Aiohttp) để crawl nhanh hơn không?
  * Bạn có muốn thiết kế thêm lớp Repository để lưu truyện vào Database (MySQL/MongoDB) theo chuẩn DDD không?