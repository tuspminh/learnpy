Dưới đây là thiết kế chi tiết và toàn bộ mã nguồn hoàn chỉnh cho ứng dụng CLI Crawl Slide từ SlideShare và xuất file PDF bằng Python, áp dụng nghiêm ngặt kiến trúc Clean Architecture.

Hệ thống được chia thành 4 lớp độc lập: Entities, Use Cases, Interfaces (Controllers/Presenters/Gateways), và Infrastructure (CLI/Scraper/Services).

* * *

## TẦNG 1: ENTITIES (`core/entities/`)

Lớp trong cùng chứa các quy tắc nghiệp vụ cốt lõi, sử dụng thuần Python và không phụ thuộc vào bất kỳ thư viện bên ngoài nào.

## File: `core/entities/slide_page.py`
    
    
    from dataclasses import dataclass
    
    @dataclass
    class SlidePage:
        """Đại diện cho một trang slide duy nhất dưới dạng dữ liệu nhị phân."""
        page_number: int
        image_url: str
        binary_data: bytes
    

## File: `core/entities/slide_book.py`
    
    
    from dataclasses import dataclass, field
    from typing import List
    from core.entities.slide_page import SlidePage
    
    @dataclass
    class SlideBook:
        """Đại diện cho toàn bộ tập sách slide được cào về."""
        title: str
        total_pages: int
        pages: List[SlidePage] = field(default_factory=list)
    
        def add_page(self, page: SlidePage) -> None:
            self.pages.append(page)
            # Sắp xếp các trang theo đúng thứ tự tăng dần
            self.pages.sort(key=lambda p: p.page_number)
    

* * *

## TẦNG 2: USE CASES (`core/use_cases/`)

Chứa các kịch bản hành động (Application Logic) của hệ thống.

## File: `core/use_cases/download_slide_use_case.py`
    
    
    from typing import Callable, Optional
    from core.entities.slide_book import SlideBook
    from core.entities.slide_page import SlidePage
    from interfaces.gateways.crawler_gateway import CrawlerGateway
    
    class DownloadSlideUseCase:
        def __init__(self, crawler_gateway: CrawlerGateway):
            self._crawler = crawler_gateway
    
        def execute(self, url: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> SlideBook:
            # 1. Thu thập thông tin cấu trúc slide từ link
            slide_info = self._crawler.fetch_slide_info(url)
            slide_book = SlideBook(title=slide_info["title"], total_pages=len(slide_info["image_urls"]))
            
            # 2. Duyệt qua từng link ảnh để tải về dữ liệu nhị phân
            for index, img_url in enumerate(slide_info["image_urls"]):
                page_num = index + 1
                img_data = self._crawler.download_image(img_url)
                
                page = SlidePage(page_number=page_num, image_url=img_url, binary_data=img_data)
                slide_book.add_page(page)
                
                # Kích hoạt callback báo tiến độ nếu có
                if progress_callback:
                    progress_callback(page_num, slide_book.total_pages)
                    
            return slide_book
    

## File: `core/use_cases/export_pdf_use_case.py`
    
    
    from core.entities.slide_book import SlideBook
    from interfaces.gateways.pdf_gateway import PdfGateway
    
    class ExportPdfUseCase:
        def __init__(self, pdf_gateway: PdfGateway):
            self._pdf_gateway = pdf_gateway
    
        def execute(self, slide_book: SlideBook, output_path: str) -> None:
            if not slide_book.pages:
                raise ValueError("Không có trang slide nào để xuất PDF.")
                
            # Trích xuất danh sách dữ liệu nhị phân (bytes) của ảnh theo đúng thứ tự
            images_bytes = [page.binary_data for page in slide_book.pages]
            
            # Gọi hạ tầng xử lý việc đóng gói PDF
            self._pdf_gateway.convert_images_to_pdf(images_bytes, output_path)
    

* * *

## TẦNG 3: INTERFACES (`interfaces/`)

Cầu nối trung gian chứa Interface trừu tượng (Gateways) và các bộ điều phối dữ liệu (Controllers / Presenters).

## File: `interfaces/gateways/crawler_gateway.py`
    
    
    from abc import ABC, abstractmethod
    
    class CrawlerGateway(ABC):
        @abstractmethod
        def fetch_slide_info(self, url: str) -> dict:
            """Trả về dict gồm 'title' (str) và 'image_urls' (list[str])."""
            pass
    
        @abstractmethod
        def download_image(self, url: str) -> bytes:
            """Tải hình ảnh về dưới dạng chuỗi byte nhị phân."""
            pass
    

## File: `interfaces/gateways/pdf_gateway.py`
    
    
    from abc import ABC, abstractmethod
    from typing import List
    
    class PdfGateway(ABC):
        @abstractmethod
        def convert_images_to_pdf(self, images_bytes: List[bytes], output_path: str) -> None:
            """Gộp danh sách mảng byte ảnh thành một file PDF duy nhất."""
            pass
    

## File: `interfaces/controllers/cli_controller.py`
    
    
    from typing import Callable
    from core.use_cases.download_slide_use_case import DownloadSlideUseCase
    from core.use_cases.export_pdf_use_case import ExportPdfUseCase
    from interfaces.gateways.crawler_gateway import CrawlerGateway
    from interfaces.gateways.pdf_gateway import PdfGateway
    
    class CliController:
        def __init__(self, crawler_gateway: CrawlerGateway, pdf_gateway: PdfGateway):
            self._download_use_case = DownloadSlideUseCase(crawler_gateway)
            self._export_use_case = ExportPdfUseCase(pdf_gateway)
    
        def handle_download_and_export(self, url: str, output_path: str, progress_callback: Callable[[int, int], None]) -> None:
            """Điều phối tuần tự kịch bản Tải về -> Xuất file."""
            # Kích hoạt kịch bản tải slide
            slide_book = self._download_use_case.execute(url, progress_callback)
            
            # Kích hoạt kịch bản xuất file PDF
            self._export_use_case.execute(slide_book, output_path)
    

* * *

## TẦNG 4: INFRASTRUCTURE (`infrastructure/`)

Nơi cài đặt chi tiết các thư viện công nghệ như `requests`, `BeautifulSoup`, `img2pdf`, và giao diện dòng lệnh `click`.

## File: `infrastructure/scraper/slideshare_scraper.py`
    
    
    import requests
    from bs4 import BeautifulSoup
    from interfaces.gateways.crawler_gateway import CrawlerGateway
    
    class SlideShareScraper(CrawlerGateway):
        def __init__(self):
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
    
        def fetch_slide_info(self, url: str) -> dict:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                raise RuntimeError(f"Không thể truy cập SlideShare (Status code: {response.status_code})")
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Lấy tiêu đề slide
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "slideshare_document"
            
            # Tìm các thẻ hình ảnh của các trang slide (Cấu trúc phổ biến của SlideShare)
            # Note: SlideShare hay dùng cơ chế lazy-load, chúng ta lấy link từ 'data-full' hoặc 'data-normal'
            img_tags = soup.find_all('img', class_='slide_image') or soup.find_all('img', {'data-full': True})
            
            image_urls = []
            for img in img_tags:
                url_src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if url_src and url_src not in image_urls:
                    image_urls.append(url_src)
                    
            if not image_urls:
                raise ValueError("Không tìm thấy bất kỳ liên kết hình ảnh slide nào từ URL này.")
                
            return {"title": title, "image_urls": image_urls}
    
        def download_image(self, url: str) -> bytes:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                raise RuntimeError(f"Lỗi khi tải ảnh từ link: {url}")
            return response.content
    

## File: `infrastructure/services/pdf_converter.py`
    
    
    from typing import List
    import img2pdf
    from interfaces.gateways.pdf_gateway import PdfGateway
    
    class PdfConverter(PdfGateway):
        def convert_images_to_pdf(self, images_bytes: List[bytes], output_path: str) -> None:
            # Sử dụng thư viện img2pdf để gom mảng bytes ảnh thành file PDF trực tiếp không cần lưu file tạm
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(images_bytes))
    

## File: `infrastructure/cli/commands.py`
    
    
    import click
    from infrastructure.scraper.slideshare_scraper import SlideShareScraper
    from infrastructure.services.pdf_converter import PdfConverter
    from interfaces.controllers.cli_controller import CliController
    
    @click.group()
    def cli():
        """Công cụ CLI chuyên nghiệp tải SlideShare thành file PDF theo Clean Architecture."""
        pass
    
    @cli.command()
    @click.argument('url')
    @click.option('--output', '-o', default=None, help='Đường dẫn lưu file PDF đầu ra (Mặc định: Tiêu đề slide).')
    def download(url, output):
        """Tải và chuyển đổi tài liệu SlideShare thành file PDF."""
        click.secho("[*] Đang khởi tạo kết nối ngoại vi...", fg='cyan')
        
        # Khởi tạo hạ tầng (Infrastructure)
        scraper = SlideShareScraper()
        pdf_service = PdfConverter()
        
        # Khởi tạo Controller điều phối (Interfaces)
        controller = CliController(scraper, pdf_service)
        
        try:
            # Thực hiện phân tích URL trước để lấy tổng số trang cho progress bar của Click
            click.echo("[*] Đang đọc cấu trúc dữ liệu SlideShare...")
            slide_info = scraper.fetch_slide_info(url)
            total_pages = len(slide_info["image_urls"])
            
            # Xác định tên file đầu ra nếu người dùng không điền option -o
            if not output:
                safe_title = "".join([c for c in slide_info["title"] if c.isalnum() or c in (' ', '_', '-')]).rstrip()
                output = f"{safe_title}.pdf"
                
            click.secho(f"[+] Tìm thấy slide: '{slide_info['title']}' ({total_pages} trang)", fg='green')
            
            # Sử dụng thanh tiến độ của click.progressbar
            with click.progressbar(length=total_pages, label='[*] Tiến trình tải ảnh trang') as bar:
                
                # Định nghĩa hàm callback cập nhật UI thanh tiến độ cho Use Case gọi ngược lại
                def update_cli_ui(current_page: int, total: int):
                    bar.update(1)
                    
                # Chạy toàn bộ tiến trình điều phối
                controller.handle_download_and_export(url, output, update_cli_ui)
                
            click.secho(f"\n[✔] Thành công! File PDF đã được xuất tại: {output}", fg='green', bold=True)
            
        except Exception as e:
            click.secho(f"\n[✘] Lỗi hệ thống: {e}", fg='red', bold=True)
    

* * *

## ĐIỂM KHỞI CHẠY CHÍNH (`main.py`)

Nơi làm nhiệm vụ cấu hình entrypoint kích hoạt CLI của toàn bộ ứng dụng.

## File: `main.py`
    
    
    import sys
    from infrastructure.cli.commands import cli
    
    if __name__ == "__main__":
        # Đảm bảo CLI chạy đúng khi gọi lệnh từ terminal
        cli()
    

* * *

## HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

Bước 1: Tạo file `requirements.txt` với nội dung sau:
    
    
    beautifulsoup4==4.12.3
    requests==2.32.3
    click==8.1.7
    img2pdf==0.5.1
    

Bước 2: Cài đặt các thư viện phụ thuộc:
    
    
    pip install -r requirements.txt
    

Bước 3: Chạy thử ứng dụng bằng CLI với cấu trúc lệnh:
    
    
    python main.py download https://slideshare.net -o tai_lieu.pdf
    

Nếu bạn không truyền tham số `-o tai_lieu.pdf`, hệ thống sẽ tự động lấy tiêu đề trang SlideShare để đặt tên cho file PDF của bạn.

Để mở rộng ứng dụng này, ví dụ viết thêm Unit Test cho lớp Logic (`core/`) hoặc muốn thêm tính năng nén dung lượng ảnh trước khi xuất PDF, bạn có muốn tôi thiết kế tiếp phần đó không?