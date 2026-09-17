Trong kiến trúc DDD, Crawler (hay thường gọi là `CrawlerEngine`, `CrawlerService`) đóng vai trò là Application Service hoặc một Domain Service (nếu chứa các luật nghiệp vụ cào phức tạp).

Nhiệm vụ của Crawler không phải là bóc tách HTML (đó là việc của `Parser`), cũng không phải gửi request trực tiếp (đó là việc của `Fetcher`). Crawler là bộ não điều phối tổng thể: quản lý tiến độ, lập lịch, xử lý luồng (đồng bộ/bất đồng bộ), kết hợp `Fetcher` \+ `Parser` để lấy dữ liệu về và đẩy qua tầng `Repository` để lưu trữ.

* * *

## Cấu trúc tổng thể của Crawler Engine theo DDD

## 1\. Interface định nghĩa nghiệp vụ (`domain/services/crawler_service.py`)

Định nghĩa hành vi cốt lõi của một bộ cào truyện chữ.
    
    
    from abc import ABC, abstractmethod
    from domain.entities import Novel
    
    class INovelCrawler(ABC):
        """Giao diện quản lý toàn bộ vòng đời của việc cào một bộ truyện"""
        
        @abstractmethod
        def crawl_full_novel(self, start_url: str) -> Novel:
            """Cào toàn bộ từ thông tin truyện đến tất cả các chương"""
            pass
    

## 2\. Triển khai Crawler Engine (`application/services/novel_crawler.py`)

Đây là nơi chứa logic điều phối luồng chạy. Ví dụ dưới đây sử dụng Thread/Asynchronous (hoặc vòng lặp tuần tự có kiểm soát) để cào danh sách chương một cách tối ưu.
    
    
    import logging
    from domain.entities import Novel, Chapter
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    from infrastructure.repositories.novel_repository import INovelRepository
    
    logger = logging.getLogger(__name__)
    
    class MultiThreadedNovelCrawler:
        """Crawler Engine điều phối Fetcher, Parser và Repository"""
        
        def __init__(self, fetcher: INovelFetcher, repository: INovelRepository):
            self.fetcher = fetcher
            self.repository = repository  # Lưu trữ vào Database hoặc File
    
        def crawl_full_novel(self, start_url: str) -> Novel:
            logger.info(f"Bắt đầu tiến trình cào truyện tại: {start_url}")
            
            # BƯỚC 1: Chọn Parser dựa trên URL
            parser = ParserFactory.get_parser(start_url)
            
            # BƯỚC 2: Cào thông tin tổng quan và danh sách chương thô
            index_html = self.fetcher.fetch_html(start_url)
            novel = parser.parse_novel_info(index_html, source_url=start_url)
            
            logger.info(f"Đã nhận diện truyện: {novel.title} | Số chương phát hiện: {len(novel.chapters)}")
            
            # BƯỚC 3: Lưu thông tin meta-data của truyện trước vào Database
            self.repository.save_novel_meta(novel)
    
            # BƯỚC 4: Vòng lặp cào chi tiết nội dung từng chương (Crawl Content Loop)
            # Lưu ý: Thực tế bạn có thể dùng ThreadPoolExecutor hoặc asyncio để tăng tốc ở đây
            for chapter in novel.chapters:
                try:
                    # Giả định URL của chương được tính toán dựa trên domain hoặc được parse từ trước
                    chapter_url = self._build_chapter_url(novel.source_url, chapter)
                    
                    logger.info(f"Đang cào nội dung: {chapter.title}")
                    chapter_html = self.fetcher.fetch_html(chapter_url)
                    
                    # Parse nội dung chữ của chương đó
                    parsed_chapter = parser.parse_chapter_content(
                        html_content=chapter_html, 
                        number=chapter.number, 
                        title=chapter.title
                    )
                    
                    # Cập nhật nội dung vào entity
                    chapter.update_content(parsed_chapter.content)
                    
                    # Lưu chương này vào Database ngay lập tức (tránh mất dữ liệu nếu crash giữa chừng)
                    self.repository.save_chapter(novel.title, chapter)
                    
                except Exception as e:
                    logger.error(f"Lỗi khi cào {chapter.title}: {str(e)}")
                    # Tuỳ chọn: Ghi nhận lỗi và tiếp tục cào chương sau (Fault Tolerance)
                    continue
                    
            logger.info(f"Hoàn thành cào trọn bộ truyện: {novel.title}")
            return novel
    
        def _build_chapter_url(self, novel_url: str, chapter: Chapter) -> str:
            # Logic nội bộ bổ trợ để ghép link chương (nếu cần)
            # Thông thường link cụ thể đã được Parser bóc tách từ trang mục lục
            return f"{novel_url}/chuong-{int(chapter.number)}"
    

* * *

## Mô hình Luồng hoạt động (Data Flow) trong Crawler DDD

Để dễ hình dung vị trí và cách tương tác của Crawler trong hệ thống:
    
    
    [ Trigger: CLI / Web API ]
             │
             ▼
     ┌────────────────────────────────────────────────────────┐
     │  Application Layer: NovelCrawler (Engine)              │
     │  - Điều phối trạng thái & Vòng lặp qua từng chương     │
     └───────┬────────────────────────┬───────────────────────┘
             │ (1) Gửi URL            │ (2) Trả HTML thô
             ▼                        ▼
     ┌────────────────────────┐      ┌────────────────────────┐
     │ Infrastructure Layer   │      │ Infrastructure Layer   │
     │ Fetcher (HttpClient)   │      │ Parser (BeautifulSoup) │
     └────────────────────────┘      └───────────┬────────────┘
                                                 │ (3) Trả về Domain Object
                                                 ▼
                                     ┌────────────────────────┐
                                     │ Domain Layer           │
                                     │ Entities (Novel/Chapt) │
                                     └───────────┬────────────┘
                                                 │ (4) Đưa Entity sạch vào
                                                 ▼
                                     ┌────────────────────────┐
                                     │ Infrastructure Layer   │
                                     │ Repository (SQL/NoSQL) │
                                     └────────────────────────┘
    

## Tại sao cấu trúc này đúng chuẩn DDD?

  1. Tính độc lập: Nếu một ngày trang web đổi cấu trúc HTML, bạn chỉ cần tạo/sửa `Parser` mới. Nếu hệ thống bị chặn IP, bạn chỉ cần nâng cấp `Fetcher` (thêm proxy). Cấu trúc vòng lặp điều phối của `Crawler` vẫn giữ nguyên không thay đổi.
  2. Quản lý trạng thái thông minh: Khả năng tương tác với `Repository` sau mỗi chương giúp giải quyết bài toán cào truyện dài tập (hàng nghìn chương). Nếu mạng đứt, tiến trình có thể tiếp tục (resume) thay vì phải cào lại từ đầu.



Để hoàn thiện bộ khung này, bạn muốn thiết kế tiếp phần nào:

  * Xây dựng NovelRepository (lưu dữ liệu vào SQLite/PostgreSQL sử dụng SQLAlchemy)?
  * Triển khai cơ chế Crawl song song bằng Asyncio/Httpx (cho tốc độ cào nhanh gấp 5-10 lần)?