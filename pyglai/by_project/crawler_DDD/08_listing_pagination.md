Để xử lý vấn đề phân trang (Pagination) cho cả `Listing Novel` và `Chapter List` theo chuẩn DDD và SOLID, chúng ta cần giải quyết một bài toán quan trọng: Làm sao để cào hết tất cả các trang mà không làm phình to bộ nhớ (RAM) và không vi phạm Single Responsibility (S).

Giải pháp tốt nhất là sử dụng Python Generator (`yield`) kết hợp với Iterator Pattern. Điều này giúp lớp `Parser` chỉ cần trả về liên tục dữ liệu của từng trang, và lớp `Application Service` sẽ xử lý vòng lặp để lưu vào `Repository` theo kiểu cuốn chiếu (Cào trang nào, lưu trang đó).

* * *

## 🧱 1. Cập Nhật Lớp Domain Models (`src/domain/models.py`)

Chúng ta không cần thay đổi cấu trúc cốt lõi của các Model trước, nhưng cần bổ sung thêm khái niệm Pagination URL Info (hoặc một lớp cấu trúc để nhận diện trang tiếp theo).
    
    
    # src/domain/models.py (Giữ nguyên các model cũ, chỉ bổ sung tư duy thiết kế luồng dữ liệu)
    # Các đối tượng NovelListItem, ChapterItem... giữ nguyên.
    

## 💻 2. Cập Nhật Interface và Bộ Parser (`src/domain/services.py` & `parsers.py`)

Thay vì trả về một danh sách cố định `List[...]`, các hàm parse phân trang sẽ trả về một Generator (hoặc `Iterator`) chứa các DTO. Đồng thời, Parser có nhiệm vụ tìm xem trên trang hiện tại có URL của trang tiếp theo (Next Page) hay không.
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from typing import Iterator, Optional, Tuple, List
    from src.domain.models import PageSource, NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class NovelParserInterface(ABC):
        """Cập nhật Interface hỗ trợ phân trang (SOLID - I)"""
        
        @abstractmethod
        def parse_listing_page(self, source: PageSource) -> Tuple[List[Any], Optional[str]]:
            """Trả về: (Danh sách DTO của trang hiện tại, URL của trang tiếp theo nếu có)"""
            pass
        
        @abstractmethod
        def parse_chapter_list_page(self, source: PageSource) -> Tuple[List[Any], Optional[str]]:
            """Trả về: (Danh sách Chapter DTO của trang hiện tại, URL của trang tiếp theo nếu có)"""
            pass
    
        @abstractmethod
        def parse_detail(self, source: PageSource) -> NovelDetail: pass
        @abstractmethod
        def parse_chapter_detail(self, source: PageSource) -> ChapterDetail: pass
    

Triển khai cụ thể cho một trang web (ví dụ `TruyenFullParser`):
    
    
    # src/infrastructure/parsers/truyenfull.py
    from bs4 import BeautifulSoup
    from typing import Tuple, List, Optional
    from src.domain.services import NovelParserInterface
    from src.infrastructure.dtos import NovelListItemDTO  # Giả định đã có ChapterItemDTO tương tự
    
    class TruyenFullParser(NovelParserInterface):
        
        def parse_listing_page(self, source) -> Tuple[List[NovelListItemDTO], Optional[str]]:
            soup = BeautifulSoup(source.content, 'html.parser')
            dtos = []
            
            # 1. Bóc tách danh sách truyện của TRANG HIỆN TẠI
            for row in soup.find_all('div', class_='row-novel') or []:
                dtos.append(NovelListItemDTO(
                    raw_title=row.find('h3').text if row.find('h3') else None,
                    raw_url=row.find('a')['href'] if row.find('a') else None
                ))
                
            # 2. Tìm nút "Trang tiếp theo" (Next Page URL)
            # Giả sử cấu trúc HTML: <a class="next-page" href="https://site.com">Tiếp</a>
            next_btn = soup.find('a', class_='next-page')
            next_page_url = next_btn['href'] if next_btn and next_btn.has_attr('href') else None
            
            return dtos, next_page_url
    
        def parse_chapter_list_page(self, source) -> Tuple[List[Any], Optional[str]]:
            soup = BeautifulSoup(source.content, 'html.parser')
            chapter_dtos = []
            
            # Bóc tách danh sách chương của TRANG HIỆN TẠI
            for idx, li in enumerate(soup.find_all('ul', class_='list-chapter') or []):
                # Giả định cấu trúc tương tự bài trước nhưng bọc qua DTO
                # chapter_dtos.append(ChapterItemDTO(...))
                pass
                
            # Tìm nút phân trang của danh sách chương
            next_btn = soup.find('a', class_='next-chapter-page')
            next_page_url = next_btn['href'] if next_btn and next_btn.has_attr('href') else None
            
            return chapter_dtos, next_page_url
    
        # Các hàm parse_detail và parse_chapter_detail giữ nguyên độc lập (Single Responsibility)
        def parse_detail(self, source): pass
        def parse_chapter_detail(self, source): pass
    

* * *

## 🔄 3. Cập Nhật Lớp Điều Phối Ứng Dụng (`src/main.py`)

Lớp `SmartNovelCrawlerApp` đóng vai trò điều phối luồng chạy. Chúng ta sẽ dùng vòng lặp `while current_url:` để tự động "lật trang" liên tục cho đến khi bộ `Parser` báo về là không còn trang tiếp theo (`None`).

Cách thiết kế này giúp giải quyết triệt để vấn đề phân trang mà không làm phình RAM, vì dữ liệu được cào, kiểm tra qua DTO, và đẩy thẳng xuống Repository để lưu (ổ đĩa/DB) ngay lập tức theo từng trang.
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers.factory import ParserFactory
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    from src.infrastructure.logging.logger import setup_logger
    from src.infrastructure.dtos import DataValidationError
    
    logger = setup_logger("MainApp")
    
    class SmartNovelCrawlerApp:
        def __init__(self, http_client, parser_factory, repository):
            self.client = http_client
            self.factory = parser_factory
            self.repo = repository
    
        def crawl_all_listings(self, start_url: str):
            """Cào toàn bộ danh sách truyện từ trang 1 đến trang cuối cùng"""
            current_url = start_url
            page_num = 1
            
            try:
                parser = self.factory.get_parser(start_url)
            except ValueError as e:
                logger.error(e)
                return
    
            while current_url:
                logger.info(f"🕵️ Đang cào Listing trang {page_num}: {current_url}")
                source = self.client.fetch(current_url)
                
                # Lấy dữ liệu trang hiện tại và URL trang tiếp theo
                dtos, next_page_url = parser.parse_listing_page(source)
                
                # Validate và chuyển đổi DTO sang Domain một cách cuốn chiếu
                validated_items = []
                for dto in dtos:
                    try:
                        validated_items.append(dto.to_domain())
                    except DataValidationError as val_err:
                        logger.warning(f"⏩ Bỏ qua 1 dòng dữ liệu lỗi: {val_err}")
                
                # Lưu ngay dữ liệu trang này vào Repository
                if validated_items:
                    self.repo.save_listing(validated_items)
                    logger.info(f"✅ Đã lưu {len(validated_items)} truyện của trang {page_num}")
    
                # Chuyển sang trang tiếp theo
                current_url = next_page_url
                page_num += 1
                
            logger.info("🎉 Đã hoàn thành cào toàn bộ các trang Listing!")
    
        def crawl_all_chapters_of_novel(self, novel_url: str):
            """Cào toàn bộ danh sách chương từ trang 1 đến trang cuối cùng của một truyện"""
            current_url = novel_url + "/chapters"  # Hoặc URL trang chapter 1 tùy site
            page_num = 1
            parser = self.factory.get_parser(novel_url)
            
            while current_url:
                logger.info(f"📜 Đang quét danh sách chương trang {page_num}: {current_url}")
                source = self.client.fetch(current_url)
                
                chapter_dtos, next_page_url = parser.parse_chapter_list_page(source)
                
                # Validate và chuyển sang Domain Model...
                validated_chapters = [] # [dto.to_domain() for dto in chapter_dtos nếu hợp lệ]
                
                if validated_chapters:
                    self.repo.save_chapters(novel_url, validated_chapters)
                    logger.info(f"✅ Đã lưu {len(validated_chapters)} chương của trang {page_num}")
                    
                current_url = next_page_url
                page_num += 1
                
            logger.info("🎉 Đã hoàn thành quét toàn bộ danh sách chương!")
    
    if __name__ == "__main__":
        client = RequestsHttpClient()
        factory = ParserFactory()
        repo = SqliteNovelRepository(db_path="perfect_novel.db")
    
        app = SmartNovelCrawlerApp(http_client=client, parser_factory=factory, repository=repo)
    
        # Thử nghiệm chạy cào phân trang danh sách truyện
        app.crawl_all_listings("https://truyenfull.vn")
    

* * *

## 🎯 Phân Tích Tính Tuân Thủ SOLID & DDD

  * Single Responsibility (S): Lớp `Parser` chỉ đảm nhận việc tìm dữ liệu và tìm thẻ "Next Page" trên chính trang HTML đó. Nó hoàn toàn không tự ý gửi request HTTP hay tự gọi vòng lặp. Việc điều phối chuyển trang thuộc trách nhiệm của `SmartNovelCrawlerApp`.
  * Tối ưu kiến trúc: Hệ thống không lưu giữ mảng dữ liệu khổng lồ của hàng ngàn trang trong RAM. Nó hoạt động theo cơ chế Stream/Cuốn chiếu (Fetch -> Parse -> Validate -> Save -> Release RAM -> Next), giúp ứng dụng cực kỳ ổn định dù site truyện có lên tới 10.000 trang.



Bạn có muốn tối ưu luồng này bằng cách thêm Cơ chế Sleep ngẫu nhiên (Random Delay) giữa các trang để tránh bị hệ thống của site truyện phát hiện và block IP do gửi request quá nhanh không?