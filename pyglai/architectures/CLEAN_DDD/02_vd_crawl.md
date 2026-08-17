Dưới đây là ví dụ thực tế về cách thiết kế một ứng dụng Crawl Truyện bằng Python, áp dụng triết lý Clean Architecture và DDD.

Ứng dụng này sẽ lấy nội dung chương truyện từ một trang web, xử lý làm sạch dữ liệu (Nghiệp vụ) và lưu vào file Markdown hoặc Database.

## 📂 Cấu trúc thư mục dự án
    
    
    comic_crawler/
    │
    ├── domain/                    # Layer 1: Chứa thực thể và luật nghiệp vụ (Core)
    │   ├── models.py              # Chapter (Aggregate Root), Story (Entity)
    │   └── exceptions.py          # Lỗi nghiệp vụ (v dụ: nội dung trống, lỗi kiểm tra)
    │
    ├── application/               # Layer 2: Điều phối các Use Case
    │   ├── crawler_service.py     # Use Case: Thực hiện cào và xử lý chương truyện
    │   └── interfaces.py          # Định nghĩa cổng giao tiếp (Repository, HtmlParser)
    │
    ├── infrastructure/            # Layer 3: Cài đặt chi tiết công nghệ
    │   ├── html_parser.py         # Dùng BeautifulSoup để bóc tách HTML
    │   └── repositories.py        # Lưu truyện xuống ổ đĩa (Markdown) hoặc DB
    │
    └── main.py                    # Layer 4: Điểm khởi chạy (Presentation/App Entry)
    

* * *

## 💻 Triển khai mã nguồn chi tiết

## 1\. Lớp Domain (Core Nghiệp vụ)

Lớp này hoàn toàn thuần khiết, không chứa bất kỳ thư viện cào web hay lưu trữ nào. Nó chỉ chứa cấu trúc dữ liệu và quy tắc của một "Chương truyện hợp lệ".
    
    
    # domain/exceptions.py
    class InvalidChapterError(Exception):
        """Ngoại lệ khi chương truyện không hợp lệ."""
        pass
    
    # domain/models.py
    from dataclasses import dataclass
    from domain.exceptions import InvalidChapterError
    
    @dataclass
    class Chapter:
        """Aggregate Root đại diện cho một chương truyện hợp lệ."""
        title: str
        content: str
        chapter_number: int
    
        def __post_init__(self):
            # Luật nghiệp vụ: Tên và nội dung không được để trống
            if not self.title or not self.title.strip():
                raise InvalidChapterError("Tiêu đề chương không được để trống.")
            if not self.content or len(self.content.strip()) < 50:
                raise InvalidChapterError("Nội dung chương quá ngắn hoặc bị lỗi tải.")
    
        def clean_content(self):
            """Luật nghiệp vụ: Chuẩn hóa và làm sạch nội dung truyện."""
            # Ví dụ: Xóa bỏ quảng cáo chèn trong nội dung
            ads_keywords = ["truyenfull", "doc truyen tai", "click vao day"]
            lines = self.content.split("\n")
            cleaned_lines = [
                line for line in lines 
                if not any(keyword in line.lower() for keyword in ads_keywords)
            ]
            self.content = "\n".join(cleaned_lines).strip()
    

## 2\. Lớp Application (Giao tiếp & Điều phối)

Định nghĩa các interface (giao diện) và luồng xử lý (Use Case).
    
    
    # application/interfaces.py
    from abc import ABC, abstractmethod
    from domain.models import Chapter
    
    class IHtmlParser(ABC):
        """Cổng kết nối để bóc tách dữ liệu từ URL."""
        @abstractmethod
        def fetch_chapter_data(self, url: str) -> tuple[str, str, int]:
            """Trả về (title, raw_content, chapter_number)"""
            pass
    
    class IChapterRepository(ABC):
        """Cổng kết nối để lưu trữ chương truyện."""
        @abstractmethod
        def save(self, chapter: Chapter) -> None:
            pass
    
    # application/crawler_service.py
    from application.interfaces import IHtmlParser, IChapterRepository
    from domain.models import Chapter
    
    class CrawlChapterUseCase:
        """Use Case: Điều phối quy trình cào một chương truyện."""
        def __init__(self, parser: IHtmlParser, repository: IChapterRepository):
            self.parser = parser
            self.repository = repository
    
        def execute(self, url: str) -> str:
            # 1. Thu thập dữ liệu thô qua Interface
            title, raw_content, number = self.parser.fetch_chapter_data(url)
            
            # 2. Tạo Domain Model và áp dụng luật nghiệp vụ (Clean dữ liệu)
            chapter = Chapter(title=title, content=raw_content, chapter_number=number)
            chapter.clean_content()
            
            # 3. Lưu trữ thông qua Interface
            self.repository.save(chapter)
            return f"Thành công: Đã cào và lưu Chương {chapter.chapter_number} - {chapter.title}"
    

## 3\. Lớp Infrastructure (Cài đặt công nghệ chi tiết)

Đây là nơi bạn sử dụng các thư viện như `requests`, `BeautifulSoup` (để cào) hoặc viết code lưu file/lưu DB.
    
    
    # infrastructure/html_parser.py
    import requests
    from bs4 import BeautifulSoup
    from application.interfaces import IHtmlParser
    
    class FakeBlogHtmlParser(IHtmlParser):
        """Cài đặt chi tiết việc cào dữ liệu bằng BeautifulSoup."""
        def fetch_chapter_data(self, url: str) -> tuple[str, str, int]:
            # Trong thực tế, bạn sẽ dùng requests.get(url)
            # Ở đây tôi giả lập mã HTML nhận được từ một trang truyện
            mock_html = """
            <html>
                <div class="chapter-title">Chương 1: Sự Trở Lại Của Ma Vương</div>
                <div class="chapter-content">
                    <p>Ngày xửa ngày xưa, ở một thế giới xa xôi...</p>
                    <p>TruyenFull - Đọc truyện online miễn phí!</p>
                    <p>Ma vương đã thức tỉnh sau 1000 năm ngủ say.</p>
                </div>
            </html>
            """
            soup = BeautifulSoup(mock_html, 'html.parser')
            
            title = soup.find(class_="chapter-title").text
            # Lấy nội dung text và phân tách bằng dấu xuống dòng
            paragraphs = soup.find(class_="chapter-content").find_all('p')
            raw_content = "\n".join([p.text for p in paragraphs])
            chapter_number = 1
            
            return title, raw_content, chapter_number
    
    # infrastructure/repositories.py
    import os
    from application.interfaces import IChapterRepository
    from domain.models import Chapter
    
    class MarkdownChapterRepository(IChapterRepository):
        """Cài đặt việc lưu trữ truyện dưới dạng file `.md`."""
        def __init__(self, output_dir: str = "stories"):
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
    
        def save(self, chapter: Chapter) -> None:
            filename = f"chapter_{chapter.chapter_number}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {chapter.title}\n\n")
                f.write(chapter.content)
    

## 4\. Lớp Presentation / Main Entry

Nơi khởi tạo (Dependency Injection) và chạy ứng dụng. Trong dự án thực tế, đây có thể là một giao diện dòng lệnh (CLI) hoặc một API FastAPI/Flask.
    
    
    # main.py
    from infrastructure.html_parser import FakeBlogHtmlParser
    from infrastructure.repositories import MarkdownChapterRepository
    from application.crawler_service import CrawlChapterUseCase
    from domain.exceptions import InvalidChapterError
    
    def main():
        # 1. Khởi tạo các công nghệ (Infrastructure)
        parser = FakeBlogHtmlParser()
        repository = MarkdownChapterRepository(output_dir="truyen_kiem_hiep")
        
        # 2. Tiêm (Inject) vào Use Case thuộc lớp Application
        crawler_service = CrawlChapterUseCase(parser=parser, repository=repository)
        
        # 3. Chạy ứng dụng
        target_url = "https://example-story-website.com"
        print("Bắt đầu cào truyện...")
        
        try:
            result = crawler_service.execute(target_url)
            print(result)
        except InvalidChapterError as e:
            print(f"Lỗi nghiệp vụ hệ thống: {e}")
        except Exception as e:
            print(f"Lỗi hệ thống không xác định: {x}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 💡 Tại sao thiết kế này mạnh mẽ cho một App Crawl?

  1. Dễ dàng đổi trang web cần cào: Hôm nay bạn cào trang A bằng `BeautifulSoup`, ngày mai trang A chặn và bạn phải chuyển sang trang B dùng `Selenium`. Bạn chỉ cần viết một Class mới kế thừa `IHtmlParser` ở lớp Infrastructure. Luật nghiệp vụ và logic lưu trữ không hề thay đổi.
  2. Dễ dàng đổi nơi lưu trữ: Bạn muốn chuyển từ lưu file Markdown sang lưu vào database MongoDB hay PostgreSQL? Bạn chỉ cần viết một lớp `MongoChapterRepository` thay thế cho `MarkdownChapterRepository`.
  3. Kiểm thử tự động (Unit Test) siêu dễ: Bạn có thể kiểm tra xem hàm lọc quảng cáo (`clean_content`) hoạt động đúng không mà không cần phải thực hiện kết nối Internet hay tạo file thật, bằng cách giả lập (Mock) các Interface.



Nếu bạn muốn nâng cấp hệ thống này, bạn có muốn tìm hiểu về cách áp dụng Domain Events (ví dụ: Tự động gửi thông báo Telegram khi cào xong một chương mới) không?

  


