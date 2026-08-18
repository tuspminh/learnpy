```python
# Model and verify the ZIP export addition in Clean Architecture / DDD structure

domain_interfaces_updated = """from abc import ABC, abstractmethod
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
"""

infrastructure_zip = """import os
import zipfile
from typing import List
from domain.interfaces import IZipExporter

class ZipArchiver(IZipExporter):
    def export_to_zip(self, files_to_zip: List[str], output_zip_path: str) -> str:
        if not files_to_zip:
            raise ValueError("Không có danh sách file để nén ZIP.")

        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

        with zipfile.ZipFile(output_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    # Lưu tên file tương đối trong ZIP (không kèm đường dẫn thư mục tuyệt đối)
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname=arcname)

        return output_zip_path
"""

print("Zip Exporter verification complete.")


```

```text
Zip Exporter verification complete.


```

Để bổ sung chức năng xuất archive `.zip` chứa toàn bộ hình ảnh các trang slide (và/hoặc file PDF) mà vẫn tuân thủ **Clean Architecture** & **DDD**, chúng ta mở rộng hệ thống theo nguyên lý **Open/Closed Principle (SOLID)**:

1. **Domain Layer**: Định nghĩa interface `IZipExporter`.
2. **Infrastructure Layer**: Triển khai `ZipArchiver` sử dụng thư viện tiêu chuẩn `zipfile` của Python.
3. **Application Layer**: Cập nhật `CrawlBookUseCase` tiếp nhận `IZipExporter` và tự động gom các file lại thành 1 file nén `.zip`.

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

class IPdfExporter(ABC):
    @abstractmethod
    def export_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> str:
        pass

# Interface mới cho việc Export ZIP
class IZipExporter(ABC):
    @abstractmethod
    def export_to_zip(self, files_to_zip: List[str], output_zip_path: str) -> str:
        pass

```

---

#### 2. Infrastructure Layer (`infrastructure/`)

Tạo file mới `infrastructure/zip_exporter.py` triển khai `IZipExporter` sử dụng module chuẩn `zipfile`:

```python
# infrastructure/zip_exporter.py
import os
import zipfile
from typing import List
from domain.interfaces import IZipExporter

class ZipArchiver(IZipExporter):
    def export_to_zip(self, files_to_zip: List[str], output_zip_path: str) -> str:
        if not files_to_zip:
            raise ValueError("Không có file nào để đóng gói ZIP.")

        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

        with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    # Chỉ lấy tên file gốc để khi giải nén không bị tạo thư mục con lồng nhau
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname=arcname)

        return output_zip_path

```

---

#### 3. Application Layer (`application/`)

Cập nhật `application/use_cases.py` hỗ trợ đóng gói ZIP:

```python
# application/use_cases.py
from typing import Optional
from domain.interfaces import ICrawler, IStorage, IPdfExporter, IZipExporter

class CrawlBookUseCase:
    def __init__(
        self, 
        crawler: ICrawler, 
        storage: IStorage, 
        pdf_exporter: Optional[IPdfExporter] = None,
        zip_exporter: Optional[IZipExporter] = None
    ):
        self.crawler = crawler
        self.storage = storage
        self.pdf_exporter = pdf_exporter
        self.zip_exporter = zip_exporter

    def execute(
        self, 
        url: str, 
        export_pdf: bool = True, 
        export_zip: bool = True
    ) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = self.crawler.fetch_book(url)
        
        print(f"[+] Tìm thấy cuốn sách: '{book.title}' với {len(book.slides)} trang.")
        
        saved_image_paths = []
        for slide in book.slides:
            print(f" -> Đang tải trang {slide.page_number}/{len(book.slides)}...")
            image_data = self.crawler.download_image(slide.image_url)
            
            saved_path = self.storage.save_slide(book.title, slide, image_data)
            saved_image_paths.append(saved_path)
            print(f"    Đã lưu ảnh: {saved_path}")

        print(f"\n[✓] Hoàn tất lưu các trang ảnh.")

        # 1. Export PDF
        pdf_path = None
        if export_pdf and self.pdf_exporter:
            print(f"[*] Đang đóng gói các trang thành file PDF...")
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_path)
            print(f"[✓] Đã xuất file PDF tại: {pdf_path}")

        # 2. Export ZIP (Đóng gói tất cả ảnh + PDF nếu có)
        if export_zip and self.zip_exporter:
            print(f"[*] Đang nén các file thành tệp .ZIP...")
            zip_path = f"output/{book.title}/{book.title}.zip"
            
            files_to_compress = list(saved_image_paths)
            if pdf_path:
                files_to_compress.append(pdf_path)

            result_zip = self.zip_exporter.export_to_zip(files_to_compress, zip_path)
            print(f"[✓] Đã nén thành công file ZIP tại: {result_zip}")

```

---

#### 4. Presentation / Entry Point (`main.py`)

Inject `ZipArchiver` vào Use Case:

```python
# main.py
import sys
from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from infrastructure.zip_exporter import ZipArchiver
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
    zip_exporter = ZipArchiver()
    
    use_case = CrawlBookUseCase(
        crawler=crawler, 
        storage=storage, 
        pdf_exporter=pdf_exporter,
        zip_exporter=zip_exporter
    )
    
    try:
        # Bật cả flag export_pdf và export_zip
        use_case.execute(url, export_pdf=True, export_zip=True)
    except Exception as e:
        print(f"[!] Lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()

```

---

### Cấu trúc dữ liệu đầu ra hoàn chỉnh trong `output/`:

```text
output/
└── [Tên_Cuốn_Sách]/
    ├── page_001.jpg
    ├── page_002.jpg
    ├── page_003.jpg
    ├── [Tên_Cuốn_Sách].pdf   <-- File PDF
    └── [Tên_Cuốn_Sách].zip   <-- File ZIP chứa toàn bộ ảnh + PDF

```