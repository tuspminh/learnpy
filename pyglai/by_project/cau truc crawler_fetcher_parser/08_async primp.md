Chính xác, `primp` có hỗ trợ Client bất đồng bộ (`primp.AsyncClient`) được xây dựng trên nền tảng async của Rust (tokio). Việc sử dụng `primp.AsyncClient` trực tiếp giúp code sạch hơn, không cần đến `ThreadPoolExecutor` cho các tác vụ I/O mạng, giúp tối ưu hiệu năng và tiết kiệm tài nguyên CPU.

Dưới đây là phiên bản tái cấu trúc toàn diện sử dụng 100% Async Client thuần túy của `primp`.

* * *

## 1\. Cập nhật Interface Fetcher (`domain/services/interfaces.py`)

Để đồng bộ với luồng async, Interface của Fetcher cần được chuyển sang dạng `async`.
    
    
    from abc import ABC, abstractmethod
    
    class INovelFetcher(ABC):
        """Giao diện chuẩn cho Async Fetcher"""
        
        @abstractmethod
        async def fetch_html(self, url: str) -> str:
            """Nhận vào URL và trả về HTML thô bất đồng bộ"""
            pass
    

* * *

## 2\. Triển khai Async Fetcher với `primp.AsyncClient` (`infrastructure/fetchers/primp_fetcher.py`)

_Lưu ý: Đối với`primp`, việc tái sử dụng một đối tượng client duy nhất (`AsyncClient`) cho toàn bộ các request là cách tốt nhất để nó tối ưu hóa Connection Pool của HTTP/2._
    
    
    import random
    import asyncio
    import primp
    from domain.services.interfaces import INovelFetcher
    
    class PrimpAsyncFetcher(INovelFetcher):
        """Fetcher bất đồng bộ hiệu năng cao sử dụng primp.AsyncClient"""
        
        def __init__(self, timeout: int = 15, max_retries: int = 3):
            self.timeout = timeout
            self.max_retries = max_retries
            self.browsers = ["chrome_120", "firefox_120", "safari_17"]
            # Khởi tạo client dùng chung duy nhất
            self.client = primp.AsyncClient(
                impersonate=random.choice(self.browsers), 
                follow_redirects=True
            )
    
        async def fetch_html(self, url: str) -> str:
            for attempt in range(self.max_retries):
                try:
                    # Gọi request bất đồng bộ thuần túy của primp
                    response = await self.client.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        return response.text
                    
                    if response.status_code == 429:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff bằng async
                        continue
                        
                    raise RuntimeError(f"Lỗi HTTP {response.status_code} khi tải {url}")
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Thất bại hoàn toàn sau {self.max_retries} lần thử: {str(e)}")
                    await asyncio.sleep(1)
    

* * *

## 3\. Tối ưu hóa Crawler Engine bất đồng bộ (`application/services/async_crawler.py`)

Bây giờ ta loại bỏ hoàn toàn `ThreadPoolExecutor` cho các tác vụ mạng. Tuy nhiên, thư viện `sqlite3` mặc định của Python không hỗ trợ async (nó là blocking I/O). Để đảm bảo tính toàn vẹn dữ liệu (Thread-safety) và không làm block Event Loop khi ghi DB, ta vẫn giữ một `ThreadPoolExecutor` nhỏ chỉ riêng cho các hàm của Repository, hoặc dùng giải pháp an toàn là chạy qua `asyncio.to_thread()`.
    
    
    import asyncio
    import logging
    from domain.entities import Novel, Chapter
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    from domain.repositories import INovelRepository
    
    logger = logging.getLogger(__name__)
    
    class PureAsyncNovelCrawler:
        """Crawler Engine tối ưu hóa: prump async cho mạng + asyncio.to_thread cho DB blocking"""
        
        def __init__(self, fetcher: INovelFetcher, repository: INovelRepository, max_workers: int = 5):
            self.fetcher = fetcher
            self.repository = repository
            self.semaphore = asyncio.Semaphore(max_workers)
    
        async def crawl_full_novel_async(self, start_url: str) -> Novel:
            logger.info(f"🚀 Bắt đầu cào song song với primp.AsyncClient tại: {start_url}")
            parser = ParserFactory.get_parser(start_url)
            
            # 1. Tải trang chủ mục lục bằng async fetcher thuần
            index_html = await self.fetcher.fetch_html(start_url)
            novel = parser.parse_novel_info(index_html, source_url=start_url)
            
            # 2. Lưu Meta truyện (Đẩy sang Thread riêng vì SQLite là blocking)
            await asyncio.to_thread(self.repository.save_novel_meta, novel)
            
            logger.info(f"📖 Tìm thấy truyện: '{novel.title}' | Quy mô: {len(novel.chapters)} chương.")
    
            # 3. Kích hoạt toàn bộ các Task tải chương song song
            tasks = [self._crawl_single_chapter(novel.source_url, chapter, parser) for chapter in novel.chapters]
            await asyncio.gather(*tasks)
            
            logger.info(f"🏁 Hoàn thành cào toàn bộ truyện: {novel.title}")
            
            # Tái tạo và trả về Entity hoàn chỉnh từ DB
            return await asyncio.to_thread(self.repository.find_by_url, novel.source_url)
    
        async def _crawl_single_chapter(self, novel_url: str, chapter: Chapter, parser):
            """Xử lý tải một chương riêng biệt sử dụng Semaphore để điều tiết lượng request"""
            async with self.semaphore:
                try:
                    # Kiểm tra Resume (Chạy non-blocking thông qua to_thread)
                    exists = await asyncio.to_thread(self.repository.is_chapter_exists, novel_url, chapter.number)
                    if exists:
                        return  
    
                    chapter_url = self._build_chapter_url(novel_url, chapter)
                    
                    # Cào HTML bất đồng bộ bằng primp
                    chapter_html = await self.fetcher.fetch_html(chapter_url)
                    
                    # Parse nội dung (Tác vụ CPU-bound siêu nhẹ, chạy trực tiếp)
                    parsed_chapter = parser.parse_chapter_content(chapter_html, chapter.number, chapter.title)
                    chapter.update_content(parsed_chapter.content)
                    
                    # Ghi dữ liệu vào SQLite bằng to_thread để tránh nghẽn luồng chính
                    await asyncio.to_thread(self.repository.save_chapter, novel_url, chapter)
                    logger.info(f"✅ Đã tải thành công: {chapter.title}")
                    
                except Exception as e:
                    logger.error(f"❌ Lỗi xử lý tại {chapter.title}: {str(e)}")
    
        def _build_chapter_url(self, novel_url: str, chapter: Chapter) -> str:
            suffix = f"chuong-{int(chapter.number)}"
            return f"{novel_url}{suffix}" if novel_url.endswith('/') else f"{novel_url}/{suffix}"
    

Nếu bạn muốn hệ thống này đạt trạng thái sản phẩm (Production-ready), tôi có thể giúp thiết kế:

  * Tích hợp aiosqlite (Thư viện SQLite async hoàn toàn) vào NovelRepository để loại bỏ hoàn toàn `asyncio.to_thread()`.
  * Viết Export Service sử dụng thư viện Python để đóng gói dữ liệu từ cơ sở dữ liệu thành file sách điện tử EPUB có mục lục chuẩn chỉnh.



Bạn muốn đi sâu vào giải pháp nào tiếp theo?