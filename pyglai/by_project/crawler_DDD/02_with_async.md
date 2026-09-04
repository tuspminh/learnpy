Để nâng cấp hệ thống cào truyện lên Bất đồng bộ (Asyncio/Aiohttp) và tích hợp lớp Repository (SQLAlchemy/MongoDB) theo đúng chuẩn DDD và SOLID, chúng ta sẽ mở rộng cấu trúc thư mục và tái cấu trúc lại các lớp hạ tầng.

Dưới đây là giải pháp chi tiết giúp bạn tối ưu tốc độ cào dữ liệu và quản lý lưu trữ dữ liệu bền vững.

* * *

## 🧱 Kiến Trúc Thư Mục Mở Rộng
    
    
    src/
    │
    ├── domain/
    │   ├── models.py            # Giữ nguyên thực thể Novel, Chapter, PageSource
    │   └── services.py          # Thêm Repository Interface và cập nhật Async
    │
    ├── infrastructure/
    │   ├── async_http_client.py # Fetcher Client bất đồng bộ (Aiohttp)
    │   ├── parsers.py           # Bộ parse HTML (Giữ nguyên hoặc dùng Async nếu cần)
    │   └── repositories.py      # Lớp lưu trữ dữ liệu (SQLAlchemy Async / Mongo)
    │
    └── main.py                  # Khởi chạy hệ thống bằng Asyncio
    

* * *

## 💻 Triển Khai Mã Nguồn Chi Tiết

## 1\. Lớp Domain (Cập Nhật Bất Đồng Bộ và Thêm Interface)

Chúng ta chuyển đổi các hàm xử lý thành `async` và định nghĩa thêm `NovelRepositoryInterface` để tách biệt logic nghiệp vụ khỏi Database.
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from src.domain.models import PageSource, Novel
    
    class AsyncHttpClientInterface(ABC):
        """Interface cho Async Fetcher Client (SOLID - I)"""
        @abstractmethod
        async def fetch(self, url: str) -> PageSource:
            pass
    
    class NovelParserInterface(ABC):
        """Interface cho Bộ Parser"""
        @abstractmethod
        def parse_novel(self, source: PageSource) -> Novel:
            pass
    
    class NovelRepositoryInterface(ABC):
        """Interface cho Repository - Định nghĩa cách lưu trữ (DDD - Repository Pattern)"""
        @abstractmethod
        async def save(self, novel: Novel) -> None:
            pass
        
        @abstractmethod
        async def get_by_url(self, url: str) -> Novel | None:
            pass
    
    class AsyncNovelCrawlerService:
        """Fetcher Crawler Service điều phối luồng bất đồng bộ (DDD - Domain Service)"""
        def __init__(
            self, 
            http_client: AsyncHttpClientInterface, 
            parser: NovelParserInterface,
            repository: NovelRepositoryInterface
        ):
            self._http_client = http_client
            self._parser = parser
            self._repository = repository
    
        async def crawl_and_save(self, url: str) -> Novel:
            # Kiểm tra xem truyện đã tồn tại trong DB chưa để tránh cào trùng
            existing_novel = await self._repository.get_by_url(url)
            if existing_novel:
                return existing_novel
    
            # 1. Fetch dữ liệu bất đồng bộ
            page_source = await self._http_client.fetch(url)
            
            # 2. Parse dữ liệu thô sang Domain Model
            novel = self._parser.parse_novel(page_source)
            
            # 3. Lưu vào Cơ sở dữ liệu thông qua Repository
            await self._repository.save(novel)
            return novel
    

## 2\. Lớp Hạ Tầng (Infrastructure Layer)

## 🔹 Fetcher Client Bất Đồng Bộ (Aiohttp)
    
    
    # src/infrastructure/async_http_client.py
    import aiohttp
    from src.domain.services import AsyncHttpClientInterface
    from src.domain.models import PageSource
    
    class AiohttpHttpClient(AsyncHttpClientInterface):
        """Fetcher Client sử dụng aiohttp để cào dữ liệu hiệu năng cao (SOLID - O/L)"""
        def __init__(self, timeout: int = 10):
            self._timeout = aiohttp.ClientTimeout(total=timeout)
            self._headers = {"User-Agent": "AsyncNovelCrawler/2.0"}
    
        async def fetch(self, url: str) -> PageSource:
            try:
                # Khởi tạo session cho mỗi request (hoặc pass session từ ngoài vào để tối ưu)
                async with aiohttp.ClientSession(headers=self._headers, timeout=self._timeout) as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        content = await response.text()
                        return PageSource(url=url, content=content)
            except Exception as e:
                raise RuntimeError(f"Lỗi Async Fetch tại URL {url}: {str(e)}")
    

## 🔹 Repository Tích Hợp Database (Ví dụ với MongoDB Async)

Bạn có thể dễ dàng hoán đổi đoạn code này sang SQLAlchemy Async (PostgreSQL/MySQL) mà không cần chạm vào lớp Domain ở trên.
    
    
    # src/infrastructure/repositories.py
    from motor.motor_asyncio import AsyncIOMotorClient
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import Novel, Chapter
    
    class MongoNovelRepository(NovelRepositoryInterface):
        """Triển khai Repository lưu trữ vào MongoDB bất đồng bộ"""
        def __init__(self, connection_string: str, db_name: str):
            self._client = AsyncIOMotorClient(connection_string)
            self._db = self._client[db_name]
            self._collection = self._db["novels"]
    
        async def save(self, novel: Novel) -> None:
            # Chuyển đổi Domain Model thành định dạng BSON/Dictionary để lưu vào Mongo
            novel_data = {
                "title": novel.title,
                "author": novel.author,
                "chapters": [
                    {"title": ch.title, "content": ch.content, "url": ch.url} 
                    for ch in novel.chapters
                ]
            }
            # Thực hiện cập nhật nếu trùng tên hoặc chèn mới (Upsert)
            await self._collection.update_one(
                {"title": novel.title}, 
                {"$set": novel_data}, 
                upsert=True
            )
    
        async def get_by_url(self, url: str) -> Novel | None:
            # Giả định tìm kiếm truyện dựa trên danh sách chương hoặc thực thể liên quan
            doc = await self._collection.find_one({"chapters.url": url})
            if not doc:
                return None
                
            # Map từ DB Document ngược trở lại Domain Model
            chapters = [Chapter(**ch) for ch in doc.get("chapters", [])]
            return Novel(title=doc["title"], author=doc["author"], chapters=chapters)
    

## 3\. Khởi Chạy Ứng Dụng (Async Event Loop)
    
    
    # src/main.py
    import asyncio
    from src.infrastructure.async_http_client import AiohttpHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    from src.infrastructure.repositories import MongoNovelRepository
    from src.domain.services import AsyncNovelCrawlerService
    
    async def main():
        # 1. Khởi tạo hạ tầng (Infrastructure setup)
        http_client = AiohttpHttpClient(timeout=5)
        parser = TruyenFullParser()
        repository = MongoNovelRepository(
            connection_string="mongodb://localhost:27017", 
            db_name="crawler_db"
        )
        
        # 2. Dependency Injection vào Service
        crawler = AsyncNovelCrawlerService(
            http_client=http_client, 
            parser=parser, 
            repository=repository
        )
        
        # 3. Kịch bản cào nhiều truyện cùng lúc (Tận dụng sức mạnh Async)
        urls_to_crawl = [
            "https://example-truyen.com",
            "https://example-truyen.com",
            "https://example-truyen.com"
        ]
        
        print("🚀 Bắt đầu cào truyện bất đồng bộ...")
        tasks = [crawler.crawl_and_save(url) for url in urls_to_crawl]
        
        # Chạy đồng thời tất cả các tác vụ cào
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for url, result in zip(urls_to_crawl, results):
            if isinstance(result, Exception):
                print(f"❌ Thất bại khi cào {url}: {result}")
            else:
                print(f"✅ Thành công: Truyen '{result.title}' đã được xử lý và lưu DB.")
    
    if __name__ == "__main__":
        # Chạy Event Loop của Asyncio
        asyncio.run(main())
    

* * *

## 💡 Lợi ích thu được từ kiến trúc này

  1. Hiệu năng vượt trội: Nhờ `aiohttp` và `asyncio.gather`, ứng dụng có thể gửi hàng trăm request cào chương truyện cùng một lúc mà không bị nghẽn (Blocking I/O) như thư viện `requests` cũ.
  2. Không sợ "Vendor Lock-in" (Database): Hôm nay bạn dùng MongoDB, ngày mai sếp yêu cầu đổi sang PostgreSQL, bạn chỉ cần tạo file `SqlAlchemyNovelRepository` và thế chỗ vào `main.py`. Toàn bộ code xử lý logic cào truyện ở lớp Domain giữ nguyên 100%.
  3. Dễ viết Unit Test: Bạn có thể dễ dàng tạo ra các `MockHttpClient` hoặc `MockRepository` (chỉ lưu vào RAM/List) để test logic của `AsyncNovelCrawlerService` mà không cần phải bật mạng mạng hay bật Database lên.



Để tiếp tục hoàn thiện, bạn có muốn tích hợp thêm Cơ chế hàng đợi (Queue) để quản lý danh sách URL cần cào, hoặc Tự động thay đổi Proxy (Rotation Proxy) để tránh bị các trang web chặn (Ban IP) không?