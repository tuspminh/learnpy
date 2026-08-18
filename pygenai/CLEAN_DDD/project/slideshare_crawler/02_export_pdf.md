```python
import os
from PIL import Image

# Setup Clean Architecture & DDD structure for SlideShare Crawler with PDF Export feature

# Domain Entities & Interfaces
domain_models = """from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Slide:
    page_number: int
    image_url: str

class Book:
    def __init__(self, title: str, source_url: str, slides: List[Slide] = None):
        self.title = self._sanitize_title(title)
        self.source_url = source_url
        self.slides = slides or []

    def add_slide(self, slide: Slide) -> None:
        self.slides.append(slide)

    @staticmethod
    def _sanitize_title(title: str) -> str:
        return "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
"""

domain_interfaces = """from abc import ABC, abstractmethod
from typing import List
from domain.models import Book, Slide

class ICrawler(ABC):
    @abstractmethod
    def fetch_book(self, url: str) -> Book:
        pass

    @abstractmethod
    def download_image(self, image_url: str) -> bytes:
        pass

class IStorage(ABC):
    @abstractmethod
    def save_slide(self, book_title: str, slide: Slide, content: bytes) -> str:
        pass

class IPdfExporter(ABC):
    @abstractmethod
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        pass
"""

infrastructure_pdf = """import os
from typing import List
from PIL import Image
from domain.interfaces import IPdfExporter

class PillowPdfExporter(IPdfExporter):
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        if not image_paths:
            raise ValueError("Không có file ảnh nào để tạo PDF.")

        images = []
        for img_path in image_paths:
            if os.path.exists(img_path):
                img = Image.open(img_path)
                # Convert RGBA or P mode images to RGB for PDF compatibility
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                images.append(img)

        if not images:
            raise ValueError("Không thể mở danh sách hình ảnh.")

        # Save first image and append the rest
        first_img = images[0]
        rest_imgs = images[1:]
        
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        first_img.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest_imgs)
        
        for img in images:
            img.close()

        return output_pdf_path
"""

app_usecase = """from typing import Optional
from domain.interfaces import ICrawler, IStorage, IPdfExporter

class CrawlBookUseCase:
    def __init__(self, crawler: ICrawler, storage: IStorage, pdf_exporter: Optional[IPdfExporter] = None):
        self.crawler = crawler
        self.storage = storage
        self.pdf_exporter = pdf_exporter

    def execute(self, url: str, export_pdf: bool = True) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = self.crawler.fetch_book(url)
        
        print(f"[+] Tìm thấy cuốn sách: '{book.title}' với {len(book.slides)} trang.")
        
        saved_image_paths = []
        for slide in book.slides:
            print(f" -> Đang tải trang {slide.page_number}/{len(book.slides)}...")
            image_data = self.crawler.download_image(slide.image_url)
            saved_path = self.storage.save_slide(book.title, slide, image_data)
            saved_image_paths.append(saved_path)
            print(f"    Đã lưu: {saved_path}")

        print(f"\n[✓] Hoàn thành lưu hình ảnh tại thư mục output/'{book.title}'")

        if export_pdf and self.pdf_exporter:
            print(f"[*] Đang đóng gói các trang thành file PDF...")
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            result_pdf = self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_path)
            print(f"[✓] Đã xuất file PDF thành công: {result_pdf}")
"""

print("Components successfully modeled.")


```

```text
Components successfully modeled.


```

Để bổ sung tính năng xuất file PDF theo kiến trúc Clean Architecture & DDD, chúng ta áp dụng nguyên lý **Dependency Inversion (DIP)**:

1. **Domain Layer**: Khai báo interface `IPdfExporter` làm contract.
2. **Infrastructure Layer**: Cài đặt `PillowPdfExporter` bằng thư viện `Pillow` (hoặc `reportlab`).
3. **Application Layer**: Cập nhật `CrawlBookUseCase` để tiếp nhận `IPdfExporter` và tự động gom các file hình ảnh đã lưu thành 1 file PDF hoàn chỉnh.

---

### Code Hiện Thực Chi Tiết

#### 1. Domain Layer (`domain/`)

Cập nhật `domain/interfaces.py`:

```python
# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from domain.models import Book, Slide

class ICrawler(ABC):
    @abstractmethod
    def fetch_book(self, url: str) -> Book:
        pass

    @abstractmethod
    def download_image(self, image_url: str) -> bytes:
        pass

class IStorage(ABC):
    @abstractmethod
    def save_slide(self, book_title: str, slide: Slide, content: bytes) -> str:
        pass

# Interface mới cho việc Export PDF
class IPdfExporter(ABC):
    @abstractmethod
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        pass

```

---

#### 2. Infrastructure Layer (`infrastructure/`)

Tạo file mới `infrastructure/pdf_exporter.py` triển khai `IPdfExporter` sử dụng thư viện **Pillow**:

```python
# infrastructure/pdf_exporter.py
import os
from typing import List
from PIL import Image
from domain.interfaces import IPdfExporter

class PillowPdfExporter(IPdfExporter):
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        if not image_paths:
            raise ValueError("Không có danh sách hình ảnh để tạo PDF.")

        images = []
        for path in image_paths:
            if os.path.exists(path):
                img = Image.open(path)
                # Chuyển đổi định dạng về RGB (nếu là RGBA/P) để tương thích với định dạng PDF
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                images.append(img)

        if not images:
            raise ValueError("Không thể mở được file ảnh nào.")

        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        # Lưu ảnh đầu tiên và đóng gói tất cả các ảnh còn lại thành PDF
        first_img = images[0]
        rest_imgs = images[1:]
        first_img.save(
            output_pdf_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=rest_imgs
        )

        for img in images:
            img.close()

        return output_pdf_path

```

---

#### 3. Application Layer (`application/`)

Cập nhật `application/use_cases.py` để gọi PDF Exporter sau khi tải xong toàn bộ slide:

```python
# application/use_cases.py
from typing import Optional
from domain.interfaces import ICrawler, IStorage, IPdfExporter

class CrawlBookUseCase:
    def __init__(
        self, 
        crawler: ICrawler, 
        storage: IStorage, 
        pdf_exporter: Optional[IPdfExporter] = None
    ):
        self.crawler = crawler
        self.storage = storage
        self.pdf_exporter = pdf_exporter

    def execute(self, url: str, export_pdf: bool = True) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = self.crawler.fetch_book(url)
        
        print(f"[+] Tìm thấy cuốn sách: '{book.title}' với {len(book.slides)} trang.")
        
        saved_image_paths = []
        for slide in book.slides:
            print(f" -> Đang tải trang {slide.page_number}/{len(book.slides)}...")
            image_data = self.crawler.download_image(slide.image_url)
            
            # Lưu ảnh lẻ xuống đĩa
            saved_path = self.storage.save_slide(book.title, slide, image_data)
            saved_image_paths.append(saved_path)
            print(f"    Đã lưu ảnh: {saved_path}")

        print(f"\n[✓] Hoàn tất lưu các trang ảnh.")

        # Xuất PDF nếu flag export_pdf=True và đã truyền dependency pdf_exporter
        if export_pdf and self.pdf_exporter:
            print(f"[*] Đang đóng gói {len(saved_image_paths)} trang thành file PDF...")
            pdf_output_path = f"output/{book.title}/{book.title}.pdf"
            
            result_pdf = self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_output_path)
            print(f"[✓] Đã xuất thành công file PDF tại: {result_pdf}")

```

---

#### 4. Presentation / Entry Point (`main.py`)

Inject `PillowPdfExporter` vào Use Case:

```python
# main.py
import sys
from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from application.use_cases import CrawlBookUseCase

def main():
    if len(sys.argv) < 2:
        url = input("Nhập URL SlideShare cần crawl: ").strip()
    else:
        url = sys.argv[1]

    if not url:
        print("URL không hợp lệ.")
        return

    # Dependency Injection Container
    crawler = SlideShareScraper()
    storage = LocalDiskStorage(base_output_dir="output")
    pdf_exporter = PillowPdfExporter()
    
    use_case = CrawlBookUseCase(
        crawler=crawler, 
        storage=storage, 
        pdf_exporter=pdf_exporter
    )
    
    try:
        # Mặc định export_pdf=True
        use_case.execute(url, export_pdf=True)
    except Exception as e:
        print(f"[!] Lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()

```

---

### Cấu trúc file trong thư mục `output/` sau khi chạy:

```text
output/
└── [Tên_Cuốn_Sách]/
    ├── page_001.jpg
    ├── page_002.jpg
    ├── page_003.jpg
    └── [Tên_Cuốn_Sách].pdf   <-- File PDF tổng hợp đã được tạo

```

### Cài đặt thư viện bổ sung (nếu chưa có Pillow)

```bash
pip install Pillow requests beautifulsoup4

```