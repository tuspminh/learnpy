**Có, code sẽ gọn nhẹ và dễ bảo trì hơn rất nhiều!**

Nếu dự án của bạn chủ yếu dùng để cào các bộ slide vừa và nhỏ (10 - 100 trang), tốc độ của **ThreadPoolExecutor** đã đủ nhanh (chỉ mất 2-5 giây) đến mức việc lưu state trở nên không quá cần thiết.

---

### So sánh Trade-off

| Tiêu chí | Có State Persistence | Loại bỏ State (Chỉ dùng Threading) |
| --- | --- | --- |
| **Độ gọn của Code** | Nhiều file, cần Interface `IRepository`, Lock thread, ghi JSON. | **Rất gọn**, bỏ hẳn 1 Layer/Interface quản lý file JSON. |
| **Tốc độ thực thi** | Nhanh nếu chạy lại (bỏ qua trang cũ). | **Luôn luôn tải mới**, nhưng tải cực nhanh nhờ đa luồng. |
| **Độ phức tạp** | Phải xử lý Thread Lock, đồng bộ dữ liệu. | **Đơn giản**, không lo dính lỗi Race Condition hay file JSON bị hỏng. |
| **Khả năng Resume** | Tải tiếp khi rớt mạng giữa chừng. | Phải tải lại từ trang 1 nếu gặp sự cố. |

---

### Code sau khi tinh gọn (Clean Architecture + Threading)

Khi bỏ State Management, cấu trúc ứng dụng chỉ còn lại luồng chạy xử lý chính vô cùng sáng rõ:

#### 1. Domain Interfaces (`domain/interfaces.py`)

Bỏ hoàn toàn `ICrawlStateRepository`.

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

class IPdfExporter(ABC):
    @abstractmethod
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        pass

class IZipExporter(ABC):
    @abstractmethod
    def export_to_zip(self, files_to_zip: List[str], output_zip_path: str) -> str:
        pass

```

---

#### 2. Application Layer (`application/use_cases.py`)

Code tinh gọn đáng kể, không cần dùng `threading.Lock()` hay kiểm tra file cũ.

```python
# application/use_cases.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple
from domain.models import Book, Slide
from domain.interfaces import ICrawler, IStorage, IPdfExporter, IZipExporter

class CrawlBookUseCase:
    def __init__(
        self, 
        crawler: ICrawler, 
        storage: IStorage, 
        pdf_exporter: Optional[IPdfExporter] = None,
        zip_exporter: Optional[IZipExporter] = None,
        max_workers: int = 8
    ):
        self.crawler = crawler
        self.storage = storage
        self.pdf_exporter = pdf_exporter
        self.zip_exporter = zip_exporter
        self.max_workers = max_workers

    def _download_single_slide(self, book_title: str, slide: Slide, total: int) -> Tuple[int, str]:
        """Worker tải và lưu 1 trang slide"""
        image_data = self.crawler.download_image(slide.image_url)
        saved_path = self.storage.save_slide(book_title, slide, image_data)
        print(f" -> [Đã tải] Trang {slide.page_number}/{total}")
        return slide.page_number, saved_path

    def execute(self, url: str, export_pdf: bool = True, export_zip: bool = True) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = self.crawler.fetch_book(url)
        
        total_slides = len(book.slides)
        print(f"[+] Sách: '{book.title}' ({total_slides} trang).")
        print(f"[*] Đang tải đa luồng ({self.max_workers} threads)...")

        results = {}
        # Tải ảnh song song
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._download_single_slide, book.title, slide, total_slides)
                for slide in book.slides
            ]
            for future in as_completed(futures):
                page_num, path = future.result()
                results[page_num] = path

        # Sắp xếp danh sách file theo đúng thứ tự trang (1 -> n)
        saved_image_paths = [results[page] for page in sorted(results.keys())]
        print(f"\n[✓] Tải thành công {len(saved_image_paths)} trang ảnh.")

        # Export PDF
        pdf_path = None
        if export_pdf and self.pdf_exporter:
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_path)
            print(f"[✓] Đã tạo file PDF: {pdf_path}")

        # Export ZIP
        if export_zip and self.zip_exporter:
            zip_path = f"output/{book.title}/{book.title}.zip"
            files = list(saved_image_paths) + ([pdf_path] if pdf_path else [])
            self.zip_exporter.export_to_zip(files, zip_path)
            print(f"[✓] Đã tạo file ZIP: {zip_path}")

```

---

#### 3. Main Entry Point (`main.py`)

Khâu khởi tạo Dependency Injection ngắn gọn hơn rất nhiều:

```python
# main.py
import sys
from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from infrastructure.zip_exporter import ZipArchiver
from application.use_cases import CrawlBookUseCase

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("Nhập URL SlideShare: ").strip()
    if not url:
        return

    # Injection
    use_case = CrawlBookUseCase(
        crawler=SlideShareScraper(),
        storage=LocalDiskStorage(base_output_dir="output"),
        pdf_exporter=PillowPdfExporter(),
        zip_exporter=ZipArchiver(),
        max_workers=8  # Tăng số thread lên 8 - 12
    )
    
    try:
        use_case.execute(url, export_pdf=True, export_zip=True)
    except Exception as e:
        print(f"[!] Lỗi: {e}")

if __name__ == "__main__":
    main()

```

### Lời khuyên

Nếu bạn đang xây dựng một **Tool CLI phục vụ cá nhân hoặc công việc hàng ngày**, phương án **bỏ State + Tăng Threading** là sự lựa chọn hợp lý nhất vì nó đạt **điểm cân bằng hoàn hảo** giữa hiệu năng cực cao và lượng code tối giản.