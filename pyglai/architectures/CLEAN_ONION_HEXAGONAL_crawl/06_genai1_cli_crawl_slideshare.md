Dưới đây là thiết kế chi tiết cấu trúc thư mục và mã nguồn triển khai thực tế cho một công cụ CLI bằng Python (sử dụng `Click`) để crawl slide sách từ SlideShare và xuất ra file PDF dựa trên **Clean Architecture**.

---

### 1. Cấu trúc thư mục dự án

Sử dụng nguyên lý tách biệt hoàn toàn giữa **Domain/Use Cases** (quy tắc nghiệp vụ) và **Infrastructure/Presentation** (thực thi cụ thể như Playwright, ReportLab, Click).

```text
slideshare_downloader/
├── src/
│   ├── domain/                         # 1. Entities & Value Objects
│   │   ├── entities.py                 # SlideBook, SlidePage
│   │   └── exceptions.py              # Domain Exceptions
│   │
│   ├── use_cases/                      # 2. Business Logic / Application Services
│   │   ├── interfaces/                 # Abstraction Ports (Abstract Base Classes)
│   │   │   ├── crawler.py              # Interface crawl dữ liệu
│   │   │   └── pdf_exporter.py         # Interface xuất file PDF
│   │   └── download_slide.py           # Use Case điều phối luồng xử lý
│   │
│   ├── infrastructure/                 # 3. External Implementations & Adapters
│   │   ├── crawler/
│   │   │   └── playwright_crawler.py   # Triển khai Crawler bằng Playwright
│   │   └── exporter/
│   │       └── reportlab_exporter.py   # Triển khai PDF Exporter bằng ReportLab
│   │
│   └── presentation/                   # 4. Entry Points & User Interface
│       └── cli.py                      # Giao diện dòng lệnh Click CLI
│
├── requirements.txt
└── main.py                             # Entry point khởi chạy CLI

```

---

### 2. Triển khai chi tiết từng tầng (Implementation)

#### Bước 1: Domain Layer (Entities & Value Objects)

Tầng này định nghĩa cấu trúc dữ liệu cốt lõi, không chứa thư viện ngoài nào ngoại trừ Python mặc định.

```python
# src/domain/entities.py
from dataclasses import dataclass
from typing import List

@dataclass
class SlidePage:
    page_number: int
    image_url: str
    image_bytes: bytes = None

@dataclass
class SlideBook:
    title: str
    source_url: str
    pages: List[SlidePage]

```

```python
# src/domain/exceptions.py
class DomainException(Exception):
    """Base Domain Exception"""
    pass

class InvalidSlideURLException(DomainException):
    pass

class CrawlFailedException(DomainException):
    pass

```

---

#### Bước 2: Use Cases Layer (Interfaces & Interactors)

Định nghĩa các Interface (Ports) và logic điều phối chính (DownloadSlideUseCase).

```python
# src/use_cases/interfaces/crawler.py
from abc import ABC, abstractmethod
from src.domain.entities import SlideBook

class SlideCrawlerInterface(ABC):
    @abstractmethod
    def fetch_slide_info(self, url: str) -> SlideBook:
        """Thu thập danh sách trang và hình ảnh slide"""
        pass

# src/use_cases/interfaces/pdf_exporter.py
from abc import ABC, abstractmethod
from src.domain.entities import SlideBook

class PDFExporterInterface(ABC):
    @abstractmethod
    def export(self, book: SlideBook, output_path: str) -> str:
        """Đóng gói SlideBook thành file PDF"""
        pass

```

```python
# src/use_cases/download_slide.py
from src.domain.exceptions import InvalidSlideURLException
from src.use_cases.interfaces.crawler import SlideCrawlerInterface
from src.use_cases.interfaces.pdf_exporter import PDFExporterInterface

class DownloadSlideUseCase:
    def __init__(self, crawler: SlideCrawlerInterface, exporter: PDFExporterInterface):
        self.crawler = crawler
        self.exporter = exporter

    def execute(self, url: str, output_path: str) -> str:
        if "slideshare.net" not in url:
            raise InvalidSlideURLException("URL không phải thuộc về SlideShare.")
        
        # 1. Thu thập dữ liệu Slide
        book = self.crawler.fetch_slide_info(url)
        
        # 2. Xuất dữ liệu ra PDF
        result_path = self.exporter.export(book, output_path)
        return result_path

```

---

#### Bước 3: Infrastructure Layer (Adapters)

Thực thi chi tiết việc cào dữ liệu qua HTTP/Playwright và chuyển đổi ảnh thành PDF bằng Pillow / ReportLab.

```python
# src/infrastructure/crawler/playwright_crawler.py
import requests
from bs4 import BeautifulSoup
from src.domain.entities import SlideBook, SlidePage
from src.domain.exceptions import CrawlFailedException
from src.use_cases.interfaces.crawler import SlideCrawlerInterface

class BeautifulSoupCrawler(SlideCrawlerInterface):
    """
    Adapter thu thập slide từ HTML bằng requests & BeautifulSoup.
    (Giữ cấu trúc đơn giản, có thể nâng cấp lên Playwright nếu trang rendered bằng JS)
    """
    def fetch_slide_info(self, url: str) -> SlideBook:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise CrawlFailedException(f"Không thể truy cập URL, status: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Lấy tiêu đề slide
        title_elem = soup.find("h1")
        title = title_elem.text.strip() if title_elem else "slideshare_book"
        
        # Lấy hình ảnh slide
        images = soup.find_all("img", class_="slide-image")
        if not images:
            # Thu thập theo cách bổ trợ nếu class thay đổi
            images = [img for img in soup.find_all("img") if "slide" in img.get("src", "")]
        
        pages = []
        for idx, img in enumerate(images, start=1):
            img_url = img.get("srcset", "").split(",")[-1].split(" ")[0] or img.get("src")
            if img_url:
                # Tải nội dung ảnh về memory
                img_data = requests.get(img_url, headers=headers).content
                pages.append(SlidePage(page_number=idx, image_url=img_url, image_bytes=img_data))
                
        if not pages:
            raise CrawlFailedException("Không tìm thấy các trang slide trong đường dẫn này.")

        return SlideBook(title=title, source_url=url, pages=pages)

```

```python
# src/infrastructure/exporter/reportlab_exporter.py
import io
from PIL import Image
from src.domain.entities import SlideBook
from src.use_cases.interfaces.pdf_exporter import PDFExporterInterface

class PillowPDFExporter(PDFExporterInterface):
    """Adapter chuyển đổi các hình ảnh nhận được thành 1 file PDF"""
    def export(self, book: SlideBook, output_path: str) -> str:
        pil_images = []
        
        for page in book.pages:
            if page.image_bytes:
                image = Image.open(io.BytesIO(page.image_bytes)).convert("RGB")
                pil_images.append(image)
                
        if not pil_images:
            raise ValueError("Không có dữ liệu hình ảnh để xuất PDF")
            
        # Xuất ảnh đầu tiên và nối các trang tiếp theo
        first_image = pil_images[0]
        rest_images = pil_images[1:] if len(pil_images) > 1 else []
        
        final_filename = output_path if output_path.endswith(".pdf") else f"{output_path}.pdf"
        first_image.save(final_filename, save_all=True, append_images=rest_images)
        
        return final_filename

```

---

#### Bước 4: Presentation Layer (Click CLI)

Xây dựng giao diện CLI và thực hiện kỹ thuật **Dependency Injection** (kết nối Adapters vào Use Case).

```python
# src/presentation/cli.py
import click
from src.infrastructure.crawler.playwright_crawler import BeautifulSoupCrawler
from src.infrastructure.exporter.reportlab_exporter import PillowPDFExporter
from src.use_cases.download_slide import DownloadSlideUseCase

@click.command()
@click.option("--url", "-u", required=True, help="URL đường dẫn slide trên SlideShare")
@click.option("--output", "-o", default="output.pdf", help="Tên file PDF đầu ra (mặc định: output.pdf)")
def main(url: str, output: str):
    """CLI Tool để tải SlideShare sách/slide và chuyển đổi thành PDF"""
    click.echo(f"🔍 Đang khởi tạo luồng xử lý cho: {url}")
    
    # 1. Dependency Injection Setup
    crawler = BeautifulSoupCrawler()
    exporter = PillowPDFExporter()
    use_case = DownloadSlideUseCase(crawler=crawler, exporter=exporter)
    
    # 2. Xử lý nghiệp vụ
    try:
        click.echo("📥 Đang thu thập thông tin các trang slide...")
        saved_path = use_case.execute(url, output)
        click.secho(f" Success! File PDF đã lưu tại: {saved_path}", fg="green")
    except Exception as e:
        click.secho(f" Error: {str(e)}", fg="red")

if __name__ == "__main__":
    main()

```

```python
# main.py (Entry point ngoài cùng)
from src.presentation.cli import main

if __name__ == "__main__":
    main()

```

---

### 3. File cấu hình môi trường

Thêm file `requirements.txt` để cài đặt các thư viện phụ thuộc của Infrastructure và Presentation:

```text
click>=8.0.0
requests>=2.28.0
beautifulsoup4>=4.11.0
Pillow>=9.0.0

```

---

### 4. Cách chạy chương trình

1. **Cài đặt thư viện phụ thuộc:**
```bash
pip install -r requirements.txt

```


2. **Chạy ứng dụng bằng CLI:**
```bash
python main.py --url "https://www.slideshare.net/slideshow/example-slide/123456" --output "my_slide.pdf"

```


---

### 5. Ưu điểm thiết kế khi làm theo Clean Architecture

* **Tách biệt hoàn toàn:** Nếu SlideShare đổi cấu trúc HTML hoặc chặn scraping, chỉ cần sửa class `BeautifulSoupCrawler` hoặc tạo class `PlaywrightCrawler` thay thế trong `infrastructure/`.
* **Thay đổi định dạng PDF:** Nếu cần xuất ra dạng PPTX thay vì PDF, chỉ cần viết một adapter mới kế thừa từ `PDFExporterInterface` mà không sửa bất kỳ dòng code nào ở `DownloadSlideUseCase`.
* **Dễ Test:** Có thể test `DownloadSlideUseCase` dễ dàng bằng cách truyền Mock Objects vào constructor mà không cần gửi request mạng thực sự.