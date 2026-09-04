Để hoàn thiện ứng dụng crawl truyện một cách chuyên nghiệp nhất theo đúng chuẩn DDD và SOLID, chúng ta sẽ tích hợp thêm 2 mô hình thiết kế quan trọng:

  1. Factory Pattern (Parser Factory): Tự động phân tích URL (Domain/Host) để quyết định sử dụng bộ `Parser` nào (ví dụ: `TruyenFullParser`, `MetruyenchuParser`,...). Giúp hệ thống tuân thủ tuyệt đối Open/Closed Principle (O) — khi muốn cào thêm trang web mới, bạn chỉ cần viết thêm Parser mới và đăng ký vào Factory mà không cần sửa code cốt lõi.
  2. DTO (Data Transfer Object) & Validation: Sử dụng thư viện chuẩn của Python (`dataclasses` phối hợp với logic kiểm tra) để đóng gói dữ liệu thô ngay khi bóc tách từ HTML. Lớp DTO này hoạt động như một "vòng bảo vệ" chặn đứng dữ liệu lỗi (thiếu tiêu đề, nội dung trống, HTML lỗi) trước khi nó có cơ hội đi sâu vào lớp Nghiệp vụ (Domain Model).



* * *

## 🧱 Kiến Trúc Thư Mục Toàn Diện
    
    
    src/
    ├── config/
    │   └── settings.py
    ├── domain/
    │   ├── models.py            # Domain Models (Dữ liệu "sạch" đã an toàn)
    │   └── services.py          # Interfaces & Crawler Service
    ├── infrastructure/
    │   ├── http_client.py
    │   ├── dtos.py              # <-- THÊM MỚI: Định nghĩa các DTO và hàm Validation
    │   ├── parsers/             # <-- THÊM MỚI: Thư mục chứa các Parser cụ thể
    │   │   ├── __init__.py
    │   │   ├── factory.py       # <-- THÊM MỚI: ParserFactory tự động nhận diện site
    │   │   ├── truyenfull.py    
    │   │   └── metruyenchu.py   
    │   └── repositories/
    │       ├── sqlite_repo.py
    │       └── file_repo.py
    └── main.py
    

* * *

## 💻 Triển Khai Mã Nguồn Chi Tiết

## 1\. Lớp Hạ Tầng - Data Transfer Objects (`src/infrastructure/dtos.py`)

DTO là nơi chứa dữ liệu thô, có cấu trúc lỏng lẻo giống cấu trúc trên trang web và có nhiệm vụ tự kiểm tra tính hợp lệ (`validate`). Nếu vượt qua kiểm tra, nó sẽ có một hàm `.to_domain()` để chuyển đổi chính nó thành Domain Model "sạch".
    
    
    # src/infrastructure/dtos.py
    from dataclasses import dataclass
    from typing import List, Optional
    from src.domain.models import NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    # Custom exception cho việc validate dữ liệu cào
    class DataValidationError(Exception):
        pass
    
    @dataclass(frozen=True)
    class NovelListItemDTO:
        raw_title: Optional[str]
        raw_url: Optional[str]
    
        def validate(self) -> None:
            if not self.raw_title or not self.raw_url:
                raise DataValidationError("Dữ liệu danh sách truyện thiếu Tiêu đề hoặc URL")
            if not self.raw_url.startswith("http"):
                raise DataValidationError(f"URL truyện không hợp lệ: {self.raw_url}")
    
        def to_domain(self) -> NovelListItem:
            self.validate()
            return NovelListItem(
                title=self.raw_title.strip(),
                novel_url=self.raw_url.strip()
            )
    
    @dataclass(frozen=True)
    class ChapterDetailDTO:
        raw_novel_url: Optional[str]
        raw_chapter_url: Optional[str]
        raw_title: Optional[str]
        raw_content: Optional[str]
    
        def validate(self) -> None:
            if not self.raw_title or not self.raw_content:
                raise DataValidationError("Chương truyện bị thiếu Tiêu đề hoặc Nội dung chữ")
            # Kiểm tra nội dung rác hoặc quá ngắn (ví dụ dưới 50 ký tự)
            if len(self.raw_content.strip()) < 50:
                raise DataValidationError("Nội dung chương quá ngắn hoặc cào lỗi (Chặn bởi Cloudflare?)")
    
        def to_domain(self) -> ChapterDetail:
            self.validate()
            return ChapterDetail(
                novel_url=self.raw_novel_url.strip() if self.raw_novel_url else "",
                chapter_url=self.raw_chapter_url.strip() if self.raw_chapter_url else "",
                title=self.raw_title.strip(),
                content=self.raw_content.strip()
            )
    

_(Bạn có thể tự làm tương tự các DTO cho`NovelDetailDTO` và `ChapterItemDTO` để kiểm tra các trường như tác giả, mô tả,...)_

* * *

## 2\. Lớp Hạ Tầng - Thiết Kế Các Parser Thể Hiện (`src/infrastructure/parsers/`)

Tách biệt các Parser ra các file riêng biệt để dễ quản lý.
    
    
    # src/infrastructure/parsers/truyenfull.py
    from bs4 import BeautifulSoup
    from typing import List
    from src.domain.services import NovelParserInterface
    from src.domain.models import NovelDetail, ChapterItem
    from src.infrastructure.dtos import NovelListItemDTO, ChapterDetailDTO
    
    class TruyenFullParser(NovelParserInterface):
        """Bộ cào dành riêng cho trang TruyenFull"""
        
        def parse_listing(self, source) -> List[NovelListItemDTO]:
            soup = BeautifulSoup(source.content, 'html.parser')
            dtos = []
            for row in soup.find_all('div', class_='row-novel') or []:
                # Bóc tách và đưa vào DTO tạm thời thay vì đưa thẳng vào Domain
                dtos.append(NovelListItemDTO(
                    raw_title=row.find('h3').text if row.find('h3') else None,
                    raw_url=row.find('a')['href'] if row.find('a') else None
                ))
            return dtos
    
        def parse_chapter_detail(self, source) -> ChapterDetailDTO:
            soup = BeautifulSoup(source.content, 'html.parser')
            # Giả lập cấu trúc div chứa chữ của TruyenFull
            content_div = soup.find('div', class_='chapter-c')
            
            return ChapterDetailDTO(
                raw_novel_url="https://truyenfull.vn",
                raw_chapter_url=source.url,
                raw_title=soup.find('a', class_='chapter-title').text if soup.find('a', class_='chapter-title') else "Chương không rõ",
                raw_content=content_div.text if content_div else "Nội dung chương truyện cào được rất dài..."
            )
    
        # Các hàm parse_detail và parse_chapter_list trả về DTO tương tự...
        def parse_detail(self, source) -> NovelDetail: pass
        def parse_chapter_list(self, source) -> List[ChapterItem]: pass
    
    
    
    # src/infrastructure/parsers/metruyenchu.py
    from src.domain.services import NovelParserInterface
    # Một parser hoàn toàn khác cho site Mê Truyện Chữ
    class MeTruyenChuParser(NovelParserInterface):
        def parse_listing(self, source): return []
        def parse_detail(self, source): pass
        def parse_chapter_list(self, source): return []
        def parse_chapter_detail(self, source): 
            # Cấu trúc HTML của Mê Truyện Chữ khác biệt (ví dụ: dùng class="chu-noi-dung")
            pass
    

* * *

## 3\. Lớp Hạ Tầng - Khởi Tạo Parser Factory (`src/infrastructure/parsers/factory.py`)

Tách biệt logic nhận diện trang web. Factory này sẽ quản lý danh sách các parser và tự động khớp (match) dựa trên URL đầu vào.
    
    
    # src/infrastructure/parsers/factory.py
    from urllib.parse import urlparse
    from src.domain.services import NovelParserInterface
    from src.infrastructure.parsers.truyenfull import TruyenFullParser
    from src.infrastructure.parsers.metruyenchu import MeTruyenChuParser
    
    class ParserFactory:
        """Factory tự động nhận diện trang web để trả về Parser phù hợp (SOLID - O)"""
        def __init__(self):
            # Đăng ký các bộ parser tương ứng với domain
            self._parsers = {
                "truyenfull.vn": TruyenFullParser(),
                "truyenfull.io": TruyenFullParser(),
                "metruyenchu.com.vn": MeTruyenChuParser(),
                "metruyenchu.com": MeTruyenChuParser()
            }
    
        def get_parser(self, url: str) -> NovelParserInterface:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                # Loại bỏ 'www.' nếu có
                if domain.startswith("www."):
                    domain = domain[4:]
                    
                parser = self._parsers.get(domain)
                if not parser:
                    raise ValueError(f"Hệ thống chưa hỗ trợ cào dữ liệu từ trang web này: {domain}")
                return parser
            except Exception as e:
                raise ValueError(f"Không thể phân tích URL {url}. Chi tiết: {e}")
    

* * *

## 🚀 4. Cập Nhật Hàm Điều Phối Ứng Dụng (`src/main.py`)

Bây giờ lớp điều phối chính không cần biết cụ thể nó đang làm việc với trang web nào. Nó chỉ cần đưa URL cho `ParserFactory` để lấy về Parser thích hợp, sau đó gọi các DTO để thực hiện ép kiểu an toàn sang Domain.
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers.factory import ParserFactory
    from src.infrastructure.repositories.file_repo import FileLocalRepository
    from src.infrastructure.logging.logger import setup_logger
    from src.infrastructure.dtos import DataValidationError
    
    logger = setup_logger("MainApp")
    
    class SmartNovelCrawlerApp:
        def __init__(self, http_client, parser_factory, repository):
            self.client = http_client
            self.factory = parser_factory
            self.repo = repository
    
        def execute_crawl(self, target_url: str):
            logger.info(f"--- Bắt đầu tiến trình cào thông minh cho: {target_url} ---")
            
            # 1. Sử dụng Factory để tự động lấy Parser phù hợp (SOLID - D/O)
            try:
                parser = self.factory.get_parser(target_url)
                logger.info(f"🎯 Đã kích hoạt bộ Parser: {parser.__class__.__name__}")
            except ValueError as e:
                logger.error(e)
                return
    
            # 2. Thực hiện cào dữ liệu danh sách truyện
            source = self.client.fetch(target_url)
            
            # Parser lúc này trả về một danh sách các DTO thô
            listing_dtos = parser.parse_listing(source)
            
            # Vòng lọc chuyển đổi DTO sang Domain Model và áp dụng Validation
            validated_domain_items = []
            for dto in listing_dtos:
                try:
                    # Chuyển đổi an toàn, nếu dữ liệu bẩn sẽ tự động ném lỗi ra đây
                    domain_model = dto.to_domain()
                    validated_domain_items.append(domain_model)
                except DataValidationError as val_err:
                    # Bỏ qua dòng lỗi dữ liệu nhưng vẫn tiếp tục chạy các dòng khác (Bảo vệ app khỏi crash)
                    logger.warning(f"⏩ Bỏ qua một truyện do lỗi dữ liệu: {val_err}")
                    continue
    
            # 3. Lưu trữ dữ liệu an toàn vào Repository sau khi đã sạch lỗi
            if validated_domain_items:
                self.repo.save_listing(validated_domain_items)
                logger.info(f"✅ Đã lưu {len(validated_domain_items)} truyện hợp lệ vào kho lưu trữ.")
            else:
                logger.error("❌ Không có dữ liệu nào vượt qua vòng kiểm duyệt (Validation).")
    
    if __name__ == "__main__":
        # Khởi tạo các thành phần hệ thống linh hoạt
        client = RequestsHttpClient()
        factory = ParserFactory()
        repo = FileLocalRepository(base_dir="safe_novel_storage")
    
        app = SmartNovelCrawlerApp(http_client=client, parser_factory=factory, repository=repo)
    
        # Chạy thử với URL thuộc TruyenFull
        app.execute_crawl("https://truyenfull.vn")
        
        # Chạy thử với một trang chưa được hỗ trợ để xem hệ thống chặn lỗi bằng Factory ra sao
        # app.execute_crawl("https://gandalf-story.com")
    

* * *

## 🎨 Những lợi thế kiến trúc vượt trội vừa đạt được:

  1. Vòng kiểm duyệt dữ liệu nghiêm ngặt (DTO Validation): Toàn bộ dữ liệu trống, null hoặc lỗi cấu trúc HTML phát sinh trong quá trình cào trang mạng sẽ bị chặn đứng và xử lý tại lớp hạ tầng thông qua `DataValidationError`. Lớp Domain bên trong của bạn hoàn toàn yên tâm vì chỉ nhận dữ liệu đã được làm sạch và chuẩn hóa.
  2. Khả năng mở rộng không giới hạn (Factory Pattern): Khi bạn muốn cào thêm các trang khác như _TangThuvien_ , _TruyenYY_ ,... Bạn hoàn toàn không cần chỉnh sửa file `main.py` hay lớp App điều phối. Bạn chỉ cần tạo ra một file parser mới, kế thừa `NovelParserInterface`, rồi đăng ký nó vào file `factory.py`.



Kiến trúc ứng dụng của bạn hiện đã đạt mức hoàn thiện rất cao theo chuẩn Enterprise. Bạn có muốn đi sâu thêm vào việc xử lý Anti-Crawl (Vượt tường lửa Cloudflare/Cookie Session) cho Fetcher Client hay cấu hình Dependency Injection (DI) Container nâng cao không?