Để triển khai cơ chế cào song song vừa nhanh (bất đồng bộ) vừa có khả năng vượt tường lửa mạnh mẽ (Cloudflare, HTTP/2, TLS Fingerprint), thư viện `primp` (thư viện HTTP client viết bằng Rust cho Python, kế thừa từ `reqwest`) kết hợp với `asyncio` và `ThreadPoolExecutor` là sự lựa chọn tối ưu hàng đầu hiện nay.

Vì `primp` hoạt động theo cơ chế đồng bộ (blocking) hoặc có phiên bản async nhưng quản lý connection pool tốt nhất khi kết hợp hiệu quả với cơ chế Threading/Async của Python, dưới đây là cách tái cấu trúc Fetcher và Crawler Engine theo chuẩn DDD.

* * *

## 1\. Nâng cấp Fetcher sử dụng `primp` (`infrastructure/fetchers/primp_fetcher.py`)

Thư viện `primp` hỗ trợ giả lập trình duyệt (impersonate) cực tốt để tránh bị các hệ thống như Cloudflare chặn.
    
    
    import random
    import time
    import primp
    from domain.services.interfaces import INovelFetcher
    
    class PrimpParallelFetcher(INovelFetcher):
        """Fetcher hiệu năng cao sử dụng primp (Rust-backed) hỗ trợ impersonate browser"""
        
        def __init__(self, timeout: int = 15, max_retries: int = 3):
            self.timeout = timeout
            self.max_retries = max_retries
            # Các trình duyệt giả lập được hỗ trợ bởi primp
            self.browsers = ["chrome_120", "firefox_120", "safari_17"]
    
        def fetch_html(self, url: str) -> str:
            # Chọn ngẫu nhiên một fingerprint trình duyệt để bypass hệ thống chặn bot
            selected_browser = random.choice(self.browsers)
            client = primp.Client(impersonate=selected_browser, follow_redirects=True)
            
            for attempt in range(self.max_retries):
                try:
                    response = client.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        return response.text
                    
                    if response.status_code == 429:  # Quá tải request
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                        
                    raise RuntimeError(f"Lỗi HTTP {response.status_code} khi tải {url}")
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Thất bại hoàn toàn sau {self.max_retries} lần thử: {str(e)}")
                    time.sleep(1)
    

* * *

## 2\. Triển khai Crawler song song bất đồng bộ (`application/services/async_crawler.py`)

Chúng ta sẽ sử dụng `asyncio` kết hợp với `run_in_executor` để chạy song song nhiều tiến trình `primp` cùng lúc mà không làm nghẽn (block) luồng chính, đồng thời giới hạn số lượng request đồng thời bằng `asyncio.Semaphore` nhằm tránh làm sập nguồn truyện (hoặc bị block IP).
    
    
    import asyncio
    import logging
    from concurrent.futures import ThreadPoolExecutor
    from domain.entities import Novel, Chapter
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    from domain.repositories import INovelRepository
    
    logger = logging.getLogger(__name__)
    
    class AsyncNovelCrawler:
        """Crawler Engine bất đồng bộ, cào song song sử dụng Primp và Semaphore"""
        
        def __init__(self, fetcher: INovelFetcher, repository: INovelRepository, max_workers: int = 5):
            self.fetcher = fetcher
            self.repository = repository
            self.max_workers = max_workers
            # Giới hạn số lượng request chạy đồng thời (Concurrency Control)
            self.semaphore = asyncio.Semaphore(max_workers)
            # ThreadPool để xử lý tác vụ I/O đồng bộ của primp và sqlite
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
        async def crawl_full_novel_async(self, start_url: str) -> Novel:
            logger.info(f"🚀 Khởi động cào song song tại: {start_url}")
            
            parser = ParserFactory.get_parser(start_url)
            loop = asyncio.get_running_loop()
            
            # 1. Tải trang chủ mục lục (Chạy đồng bộ thông qua Executor)
            index_html = await loop.run_in_executor(self.executor, self.fetcher.fetch_html, start_url)
            novel = parser.parse_novel_info(index_html, source_url=start_url)
            
            # 2. Lưu thông tin Meta truyện
            await loop.run_in_executor(self.executor, self.repository.save_novel_meta, novel)
            
            logger.info(f"📖 Thống kê: Truyện '{novel.title}' có {len(novel.chapters)} chương.")
    
            # 3. Tạo danh sách các task cần cào song song
            tasks = []
            for chapter in novel.chapters:
                tasks.append(self._crawl_single_chapter_task(novel.source_url, chapter, parser, loop))
                
            # 4. Kích hoạt chạy song song toàn bộ danh sách chương
            await asyncio.gather(*tasks)
            
            logger.info(f"🏁 Hoàn thành cào song song trọn bộ truyện: {novel.title}")
            return await loop.run_in_executor(self.executor, self.repository.find_by_url, novel.source_url)
    
        async def _crawl_single_chapter_task(self, novel_url: str, chapter: Chapter, parser, loop):
            """Task xử lý cho từng chương đơn lẻ (Hỗ trợ cả Resume Crawl)"""
            async with self.semaphore:  # Giới hạn số lượng luồng chạy đồng thời tại đây
                try:
                    # Kiểm tra Resume (Đã tồn tại trong DB chưa)
                    exists = await loop.run_in_executor(
                        self.executor, self.repository.is_chapter_exists, novel_url, chapter.number
                    )
                    if exists:
                        return  # Bỏ qua không tải lại
    
                    chapter_url = self._build_chapter_url(novel_url, chapter)
                    
                    # Tải HTML thông qua primp trong ThreadPool
                    chapter_html = await loop.run_in_executor(
                        self.executor, self.fetcher.fetch_html, chapter_url
                    )
                    
                    # Parse nội dung
                    parsed_chapter = parser.parse_chapter_content(chapter_html, chapter.number, chapter.title)
                    chapter.update_content(parsed_chapter.content)
                    
                    # Ghi vào SQLite (Ghi đồng bộ an toàn thông qua ThreadPool)
                    await loop.run_in_executor(
                        self.executor, self.repository.save_chapter, novel_url, chapter
                    )
                    logger.info(f"✅ Đã tải: {chapter.title}")
                    
                except Exception as e:
                    logger.error(f"❌ Thất bại tại {chapter.title}: {str(e)}")
    
        def _build_chapter_url(self, novel_url: str, chapter: Chapter) -> str:
            if novel_url.endswith('/'):
                return f"{novel_url}chuong-{int(chapter.number)}"
            return f"{novel_url}/chuong-{int(chapter.number)}"
    

* * *

## 3\. Khởi chạy ứng dụng (Main Entry Point)

Do sử dụng `asyncio`, hàm khởi chạy chính sẽ dùng cấu trúc `asyncio.run()`.
    
    
    import asyncio
    import logging
    from infrastructure.fetchers.primp_fetcher import PrimpParallelFetcher
    from infrastructure.repositories.sqlite_repository import SQLiteNovelRepository
    from application.services.async_crawler import AsyncNovelCrawler
    
    # Cấu hình log để theo dõi tốc độ chạy song song
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    async def main():
        # 1. Khởi tạo các thành phần thuộc Infrastructure
        repo = SQLiteNovelRepository(db_path="novel_storage.db")
        fetcher = PrimpParallelFetcher(max_retries=3)
        
        # 2. Khởi tạo Engine Crawler (Cấu hình chạy tối đa 5 luồng song song cùng lúc)
        crawler = AsyncNovelCrawler(fetcher=fetcher, repository=repo, max_workers=5)
        
        # 3. Thực thi
        target_url = "https://truyenfull.io"
        await crawler.crawl_full_novel_async(target_url)
    
    if __name__ == "__main__":
        asyncio.run(main())
    

Để tối ưu hóa bước cuối cùng của ứng dụng này, bạn muốn:

  * Xây dựng thêm cấu trúc Export Service để tự động gom toàn bộ chương truyện từ SQLite và xuất ra định dạng file EPUB hoàn chỉnh (để chuyển vào điện thoại hoặc máy đọc sách)?
  * Thiết kế một lớp Proxy Rotator tích hợp thẳng vào `PrimpParallelFetcher` nếu bạn cần cào với số lượng worker cực lớn (như 20-50 luồng cùng lúc)?