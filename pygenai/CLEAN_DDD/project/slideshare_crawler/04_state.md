Để tránh việc tải trùng lặp khi chạy lại chương trình trên cùng một URL hoặc cùng một file, chúng ta áp dụng mô hình **State Persistence (Lưu trữ trạng thái)** theo kiến trúc Clean Architecture & DDD:

1. **Domain Layer**: Định nghĩa `ICrawlStateRepository` quản lý việc đọc/ghi trạng thái đã crawl (State Tracking).
2. **Infrastructure Layer**: Triển khai `JsonStateRepository` lưu trữ lịch sử dưới dạng file JSON (`crawl_state.json`).
3. **Application Layer**: Cập nhật `CrawlBookUseCase` để bỏ qua các slide/trang đã tồn tại hoặc đã được tải xong trước đó.

---

### Code Hiện Thực Chi Tiết

#### 1. Domain Layer (`domain/`)

Cập nhật `domain/interfaces.py`:

```python
# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Set
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

# Interface mới quản lý trạng thái Crawl
class ICrawlStateRepository(ABC):
    @abstractmethod
    def is_slide_downloaded(self, book_title: str, page_number: int) -> bool:
        pass

    @abstractmethod
    def mark_slide_as_downloaded(self, book_title: str, page_number: int, file_path: str) -> None:
        pass

    @abstractmethod
    def get_downloaded_slide_path(self, book_title: str, page_number: int) -> str:
        pass

```

---

#### 2. Infrastructure Layer (`infrastructure/`)

Tạo file mới `infrastructure/state_repository.py` triển khai `ICrawlStateRepository` ghi log vào file JSON:

```python
# infrastructure/state_repository.py
import json
import os
from typing import Dict, Any
from domain.interfaces import ICrawlStateRepository

class JsonStateRepository(ICrawlStateRepository):
    def __init__(self, state_file_path: str = "output/crawl_state.json"):
        self.state_file_path = state_file_path
        self._state: Dict[str, Dict[str, Any]] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_state(self) -> None:
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=4, ensure_ascii=False)

    def is_slide_downloaded(self, book_title: str, page_number: int) -> bool:
        book_data = self._state.get(book_title, {}).get("slides", {})
        page_key = str(page_number)
        
        if page_key in book_data:
            file_path = book_data[page_key]
            # Kiểm tra xem file thực tế còn tồn tại trên đĩa không
            return os.path.exists(file_path)
        return False

    def mark_slide_as_downloaded(self, book_title: str, page_number: int, file_path: str) -> None:
        if book_title not in self._state:
            self._state[book_title] = {"slides": {}}
        
        self._state[book_title]["slides"][str(page_number)] = file_path
        self._save_state()

    def get_downloaded_slide_path(self, book_title: str, page_number: int) -> str:
        return self._state.get(book_title, {}).get("slides", {}).get(str(page_number), "")

```

---

#### 3. Application Layer (`application/`)

Cập nhật `application/use_cases.py` kiểm tra state trước khi tải từng ảnh:

```python
# application/use_cases.py
from typing import Optional
from domain.interfaces import ICrawler, IStorage, IPdfExporter, IZipExporter, ICrawlStateRepository

class CrawlBookUseCase:
    def __init__(
        self, 
        crawler: ICrawler, 
        storage: IStorage, 
        state_repo: ICrawlStateRepository,
        pdf_exporter: Optional[IPdfExporter] = None,
        zip_exporter: Optional[IZipExporter] = None
    ):
        self.crawler = crawler
        self.storage = storage
        self.state_repo = state_repo
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
        skipped_count = 0

        for slide in book.slides:
            # Kiểm tra trạng thái đã tải trước đó
            if self.state_repo.is_slide_downloaded(book.title, slide.page_number):
                existing_path = self.state_repo.get_downloaded_slide_path(book.title, slide.page_number)
                saved_image_paths.append(existing_path)
                skipped_count += 1
                print(f" -> Trang {slide.page_number}/{len(book.slides)} đã tồn tại. [Bỏ qua]")
            else:
                print(f" -> Đang tải trang {slide.page_number}/{len(book.slides)}...")
                image_data = self.crawler.download_image(slide.image_url)
                
                saved_path = self.storage.save_slide(book.title, slide, image_data)
                self.state_repo.mark_slide_as_downloaded(book.title, slide.page_number, saved_path)
                
                saved_image_paths.append(saved_path)
                print(f"    Đã lưu: {saved_path}")

        print(f"\n[✓] Hoàn tất xử lý ảnh: Tải mới {len(book.slides) - skipped_count} trang, Bỏ qua {skipped_count} trang đã có.")

        # 1. Export PDF
        pdf_path = None
        if export_pdf and self.pdf_exporter:
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            print(f"[*] Đang đóng gói các trang thành file PDF...")
            self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_path)
            print(f"[✓] Đã tạo/cập nhật file PDF tại: {pdf_path}")

        # 2. Export ZIP
        if export_zip and self.zip_exporter:
            zip_path = f"output/{book.title}/{book.title}.zip"
            print(f"[*] Đang nén các file thành tệp .ZIP...")
            
            files_to_compress = list(saved_image_paths)
            if pdf_path:
                files_to_compress.append(pdf_path)

            self.zip_exporter.export_to_zip(files_to_compress, zip_path)
            print(f"[✓] Đã tạo/cập nhật file ZIP tại: {zip_path}")

```

---

#### 4. Presentation / Entry Point (`main.py`)

Inject `JsonStateRepository` vào Use Case:

```python
# main.py
import sys
from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from infrastructure.zip_exporter import ZipArchiver
from infrastructure.state_repository import JsonStateRepository
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
    state_repo = JsonStateRepository(state_file_path="output/crawl_state.json")
    pdf_exporter = PillowPdfExporter()
    zip_exporter = ZipArchiver()
    
    use_case = CrawlBookUseCase(
        crawler=crawler, 
        storage=storage, 
        state_repo=state_repo,
        pdf_exporter=pdf_exporter,
        zip_exporter=zip_exporter
    )
    
    try:
        use_case.execute(url, export_pdf=True, export_zip=True)
    except Exception as e:
        print(f"[!] Lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()

```

---

### Cấu trúc dữ liệu sau khi chạy lần 2

File theo dõi trạng thái `output/crawl_state.json` tự động được sinh ra:

```json
{
    "Tên_Cuốn_Sách": {
        "slides": {
            "1": "output/Tên_Cuốn_Sách/page_001.jpg",
            "2": "output/Tên_Cuốn_Sách/page_002.jpg",
            "3": "output/Tên_Cuốn_Sách/page_003.jpg"
        }
    }
}

```

Nút kiểm tra `os.path.exists()` đảm bảo nếu người dùng lỡ tay xóa mất 1 file hình ảnh trong thư mục `output/`, chương trình sẽ tự động nhận biết và chỉ tải lại đúng trang đó ở lần chạy kế tiếp.