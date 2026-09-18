Dưới đây là bản phân tích và thiết kế kiến trúc hệ thống Crawl Truyện Chữ bằng Python áp dụng tư duy DDD (Domain-Driven Design) - Bounded Context, phân tách rõ ràng trách nhiệm của Fetcher, Parser, Crawler, và Scraper.

* * *

## 1\. Bản đồ Bounded Context (Context Map)

Trong hệ thống Crawl truyện chữ, nếu gộp chung tất cả vào một khối (Monolith) sẽ rất dễ bị rối khi cấu trúc HTML của các web nguồn (Nội tạng, TTV, TruyenFull...) thay đổi. Do đó, hệ thống được chia làm 3 Bounded Contexts chính hoạt động độc lập qua kiến trúc Event-Driven hoặc REST API:
    
    
    [ Data Ingestion Context ] --- (Domain Events) ---> [ Content Parsing Context ]
    
               |                                                 |
               +----------------- (Shared Catalog) --------------+
                                         |
                                         v
                            [ Novel Storage & Delivery Context ]
    

  1. Data Ingestion Context (Bối cảnh Thu thập Thô): Chịu trách nhiệm giao tiếp mạng, vượt tường lửa, quản lý proxy, hạ tầng xếp hàng (Queue) và tải nội dung HTML/JSON thô về.
  2. Content Parsing Context (Bối cảnh Phân tách): Chịu trách nhiệm bóc tách dữ liệu thô (HTML/JSON) thành các Entity có ý nghĩa nghiệp vụ (Tên truyện, Tác giả, Chương, Nội dung chữ).
  3. Novel Storage & Delivery Context (Bối cảnh Lưu trữ & Phát hành): Chận dữ liệu sạch để chuẩn hóa, lưu vào DB, tối ưu hóa text cho người đọc, làm mượt mục lục và phục vụ API cho App đọc truyện.



* * *

## 2\. Thiết kế chi tiết các Hợp phần theo Domain Driven Design

Để tránh nhầm lẫn về mặt thuật ngữ, chúng ta định nghĩa và đặt chúng vào đúng vị trí Layer thích hợp trong DDD.

## A. Fetcher (Bộ tải dữ liệu) -> Thuộc `Data Ingestion Context`

  *   * Vai trò trong DDD: Thuộc Infrastructure Layer (Dưới dạng một Adapter giao tiếp với môi trường ngoài - Internet).
  * Nhiệm vụ: Nhận một URL/Request, thực hiện call HTTP (dùng `httpx`, `aiohttp` hoặc `playwright` để render JS), xử lý xoay tua Proxy, giả lập User-Agent, xử lý lỗi `403 Forbidden`, `429 Too Many Requests`.
  * Đầu ra (Output): Một đối tượng `RawResponse` (Gồm HTML String, Status Code, Headers, Metadata). Nó hoàn toàn không quan tâm bên trong HTML đó có gì.
  * 


## B. Parser (Bộ phân tích cú pháp) -> Thuộc `Content Parsing Context`

  *   * Vai trò trong DDD: Thuộc Domain Layer (Dưới dạng các Domain Services hoặc Strategy Pattern).
  * Nhiệm vụ: Nhận `RawResponse` (HTML thô) từ Fetcher, sử dụng các thư viện như `BeautifulSoup` hoặc `selectolax` để bóc tách text dựa trên các luật (Selectors/XPaths) tương ứng với từng Domain nguồn (Ví dụ: `TruyenFullParser`, `TangThuVienParser`).
  * Đầu ra (Output): Trả về các Value Objects hoặc Entities sạch sẽ (Ví dụ: `ChapterContentVO` gồm: `title`, `chapter_number`, `paragraphs: List[str]`).
  * 


## C. Crawler (Bộ định tuyến & Khám phá) -> Thuộc `Data Ingestion Context`

  *   * Vai trò trong DDD: Thuộc Application Layer (Điều hướng luồng xử lý chính).
  * Nhiệm vụ: Quản lý cấu trúc cây hoặc danh sách cần cào. Ví dụ: từ URL danh mục sách -> tìm ra danh sách các truyện -> tìm ra danh sách các chương. Nó lưu giữ trạng thái (State) xem URL nào đã cào, URL nào chưa (thường dùng Redis làm Scheduler Queue).
  * Luồng đi: Tạo lệnh tải (`FetchCommand`) -> Giao cho Fetcher xử lý.
  * 


## D. Scraper (Bộ tổng hợp kết quả) -> Thuộc `Application Layer` (Phối hợp liên Context)

  *   * Vai trò trong DDD: Đóng vai trò như một Application Service đầu não kết hợp cả Crawler, Fetcher, và Parser thành một kịch bản hoàn chỉnh (Pipeline).
  * Nhiệm vụ: Khởi chạy chiến dịch cào (Scraping Job). Phối hợp đưa URL cho Crawler -> Fetcher tải HTML -> Parser bóc tách dữ liệu -> Bắn sự kiện `ChapterCrawledEvent` sang Context lưu trữ.
  * 


* * *

## 3\. Mô hình Kiến trúc và Phân lớp mã nguồn (Python Clean Architecture)

Dưới đây là cách tổ chức cấu trúc thư mục Python chuẩn chỉnh cho Context Content Parsing & Ingestion:
    
    
    src/
    │
    ├── ingestion_context/                # Context tải dữ liệu thô
    │   ├── application/
    │   │   └── crawler_service.py       # Quản lý hàng đợi URL, Scheduler
    │   └── infrastructure/
    │       └── http_fetcher.py          # Triển khai httpx / aiohttp, Rotating Proxy
    │
    ├── parsing_context/                  # Context bóc tách dữ liệu
    │   ├── domain/
    │   │   ├── models.py                # Entity: Novel, ValueObject: ChapterContent
    │   │   └── parser_interface.py      # Abstract Class / Interface cho các chiến lược Parse
    │   └── infrastructure/
    │       ├── parsers/
    │       │   ├── truyenfull_parser.py # Kế thừa parser_interface, dùng selectolax
    │       │   └── ttv_parser.py        
    │       └── parsing_service.py       # Application Service điều phối
    

* * *

## 4\. Minh họa triển khai bằng Python (Code Concept)

## Định nghĩa Domain Layer (Parsing Context)
    
    
    # parsing_context/domain/models.py
    from dataclasses import dataclass
    from typing import List
    
    @dataclass(frozen=True)
    class ChapterContentVO:
        """Value Object chứa nội dung chữ sạch của một chương"""
        novel_id: str
        chapter_number: float
        title: str
        paragraphs: List[str] # Lưu danh sách các đoạn văn để dễ format khi hiển thị
    

## Định nghĩa Interface & Infrastructure Layer (Fetcher & Parser)
    
    
    # parsing_context/domain/parser_interface.py
    from abc import ABC, abstractmethod
    from parsing_context.domain.models import ChapterContentVO
    
    class NovelParserInterface(ABC):
        @abstractmethod
        def parse_chapter(self, html_content: str, novel_id: str) -> ChapterContentVO:
            pass
    
    # ingestion_context/infrastructure/http_fetcher.py
    import httpx
    
    class HttpFetcher:
        def __init__(self, proxy_pool: list = None):
            self.proxy_pool = proxy_pool
    
        async def fetch(self, url: str) -> str:
            """Tải HTML thô, xử lý retry và proxy ở đây"""
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0..."})
                response.raise_for_status()
                return response.text
    
    # parsing_context/infrastructure/parsers/truyenfull_parser.py
    from selectolax.parser import HTMLParser
    from parsing_context.domain.parser_interface import NovelParserInterface
    from parsing_context.domain.models import ChapterContentVO
    
    class TruyenFullParser(NovelParserInterface):
        def parse_chapter(self, html_content: str, novel_id: str) -> ChapterContentVO:
            tree = HTMLParser(html_content)
            
            # Bóc tách bằng CSS Selector cực nhanh với selectolax
            title = tree.css_first(".chapter-title").text(strip=True)
            content_node = tree.css_first(".chapter-c")
            
            # Tách nhỏ các đoạn văn chống lẫn text rác quảng cáo
            paragraphs = [p.text(strip=True) for p in content_node.css("p") if p.text(strip=True)]
            
            return ChapterContentVO(
                novel_id=novel_id,
                chapter_number=1.0, # Thực tế sẽ lấy từ regex trong URL hoặc tiêu đề
                title=title,
                paragraphs=paragraphs
            )
    

## Kết hợp tại Application Service (Scraper Pipeline)
    
    
    # parsing_context/infrastructure/parsing_service.py
    class ScraperApplicationService:
        def __init__(self, fetcher: HttpFetcher, parser_factory):
            self.fetcher = fetcher
            self.parser_factory = parser_factory
    
        async def execute_crawl_chapter(self, url: str, source_type: str, novel_id: str):
            # 1. Fetcher tải thô
            raw_html = await self.fetcher.fetch(url)
            
            # 2. Lấy Parser tương ứng với nguồn (Strategy Pattern)
            parser: NovelParserInterface = self.parser_factory.get_parser(source_type)
            
            # 3. Parser bóc tách ra Domain Model sạch
            chapter_data = parser.parse_chapter(raw_html, novel_id)
            
            # 4. Bắn Event hoặc lưu dữ liệu sạch này vào Novel Storage Context
            print(f"Crawl thành công chương: {chapter_data.title} với {len(chapter_data.paragraphs)} đoạn văn.")
            return chapter_data
    

## 5\. Lợi ích khi thiết kế theo DDD cho hệ thống này

  *   * Dễ bảo trì (Maintainability): Khi web nguồn đổi cấu trúc HTML, bạn chỉ cần sửa duy nhất file `truyenfull_parser.py` ở tầng Infrastructure của `Parsing Context`. Toàn bộ logic xếp hàng (Crawler), tải mạng (Fetcher) hay lưu trữ đều giữ nguyên.
  * Tốc độ & Hiệu năng cao: Tách rời Fetcher (I/O Bound - tốn thời gian chờ mạng, cần chạy bất đồng bộ `asyncio`) và Parser (CPU Bound - tốn CPU giải mã HTML, có thể chạy đa nhân `ProcessPoolExecutor` nếu lượng dữ liệu cực lớn).
  * 


Để có thể tinh chỉnh thiết kế sâu hơn cho ứng dụng của bạn, bạn hãy cho biết thêm:

  *   * Bạn định cào dữ liệu thời gian thực (khi có chương mới thì cào ngay) hay cào hàng loạt (Bulk) một lần?
  * Số lượng nguồn truyện bạn cần tích hợp ước tính khoảng bao nhiêu web nguồn?
  * Bạn có cần xử lý các trang web bắt buộc phải render Javascript phức tạp không?
  *