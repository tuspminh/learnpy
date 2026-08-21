Chuyển sang **`asyncio`** giúp ứng dụng quản lý tài nguyên nhẹ hơn (không tốn overhead tạo OS thread), nhưng yêu cầu bạn đổi thư viện HTTP từ `requests` (blocking) sang **`httpx`** hoặc **`aiohttp`** (non-blocking) và cập nhật contract interface sang `async/await`.

---

### So sánh `asyncio` và `ThreadPoolExecutor`

| Tiêu chí | `ThreadPoolExecutor` | `asyncio` |
| --- | --- | --- |
| **Thư viện HTTP** | `requests` (đơn giản, phổ biến) | `httpx` / `aiohttp` (cần async client) |
| **Interface Domain** | Hàm đồng bộ `def` thông thường | Phải khai báo `async def` |
| **Mức tiêu thụ RAM** | Cao hơn (mỗi thread tốn bộ nhớ đệm OS) | Cực kỳ thấp (chạy trên 1 Thread / Event Loop) |
| **Tốc độ với SlideShare** | Rất nhanh (với < 100 trang) | Tương đương (nhưng mở rộng lên hàng ngàn trang tốt hơn) |

---

### Code Hiện Thực Chi Tiết (`asyncio` + `httpx`)

#### 1. Domain Layer (`domain/interfaces.py`)

Cập nhật interface crawler sang `async`:

```python
# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from domain.models import Book, Slide

class ICrawler(ABC):
    @abstractmethod
    async def fetch_book(self, url: str) -> Book:
        pass

    @abstractmethod
    async def download_image(self, image_url: str) -> bytes:
        pass

# IStorage, IPdfExporter, IZipExporter giữ nguyên hàm sync vì ghi file/tạo PDF là CPU/Disk Bound

```

---

#### 2. Infrastructure Layer (`infrastructure/scraper.py`)

Triển khai crawler bằng **`httpx.AsyncClient`**:

```python
# infrastructure/scraper.py
import httpx
from bs4 import BeautifulSoup
import re
from domain.models import Book, Slide
from domain.interfaces import ICrawler

class AsyncSlideShareScraper(ICrawler):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch_book(self, url: str) -> Book:
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title_elem = soup.find("h1") or soup.find("title")
        title = title_elem.get_text(strip=True) if title_elem else "slideshare_book"

        book = Book(title=title, source_url=url)
        images = soup.find_all("img", class_=re.compile(r"slide|Slide")) or soup.select("picture source, img[srcset]")

        page_num = 1
        seen_urls = set()

        for img in images:
            img_url = img.get("data-full") or img.get("src") or img.get("data-normal")
            if not img_url and img.get("srcset"):
                img_url = img.get("srcset").split(",")[-1].strip().split(" ")[0]

            if img_url and img_url.startswith("http") and img_url not in seen_urls:
                if "ss_thumbnails" not in img_url and "thumbnail" not in img_url:
                    seen_urls.add(img_url)
                    book.add_slide(Slide(page_number=page_num, image_url=img_url))
                    page_num += 1

        return book

    async def download_image(self, image_url: str) -> bytes:
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return response.content

```

---

#### 3. Application Layer (`application/use_cases.py`)

Sử dụng **`asyncio.gather`** để gửi đồng thời tất cả request tải ảnh:

```python
# application/use_cases.py
import asyncio
from typing import Optional, Tuple
from domain.models import Book, Slide
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

    async def _download_single_slide(self, book_title: str, slide: Slide, total: int) -> Tuple[int, str]:
        image_data = await self.crawler.download_image(slide.image_url)
        saved_path = self.storage.save_slide(book_title, slide, image_data)
        print(f" -> [Đã tải] Trang {slide.page_number}/{total}")
        return slide.page_number, saved_path

    async def execute(self, url: str, export_pdf: bool = True, export_zip: bool = True) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = await self.crawler.fetch_book(url)
        
        total_slides = len(book.slides)
        print(f"[+] Sách: '{book.title}' ({total_slides} trang).")
        print(f"[*] Đang tải bất đồng bộ (asyncio)...")

        # Khởi tạo danh sách coroutine
        tasks = [
            self._download_single_slide(book.title, slide, total_slides)
            for slide in book.slides
        ]
        
        # Tải song song tất cả các trang
        results_list = await asyncio.gather(*tasks)

        # Sắp xếp kết quả theo đúng thứ tự trang
        results_list.sort(key=lambda x: x[0])
        saved_image_paths = [path for _, path in results_list]
        
        print(f"\n[✓] Tải thành công {len(saved_image_paths)} trang ảnh.")

        # Export PDF & ZIP (Được giữ dạng synchronous)
        pdf_path = None
        if export_pdf and self.pdf_exporter:
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            self.pdf_exporter.export_to_pdf(saved_image_paths, pdf_path)
            print(f"[✓] Đã tạo file PDF: {pdf_path}")

        if export_zip and self.zip_exporter:
            zip_path = f"output/{book.title}/{book.title}.zip"
            files = list(saved_image_paths) + ([pdf_path] if pdf_path else [])
            self.zip_exporter.export_to_zip(files, zip_path)
            print(f"[✓] Đã tạo file ZIP: {zip_path}")

```

---

#### 4. Presentation / Entry Point (`main.py`)

Dùng **`asyncio.run()`** để kích hoạt Event Loop:

```python
# main.py
import sys
import asyncio
from infrastructure.scraper import AsyncSlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from infrastructure.zip_exporter import ZipArchiver
from application.use_cases import CrawlBookUseCase

async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("Nhập URL SlideShare: ").strip()
    if not url:
        return

    use_case = CrawlBookUseCase(
        crawler=AsyncSlideShareScraper(),
        storage=LocalDiskStorage(base_output_dir="output"),
        pdf_exporter=PillowPdfExporter(),
        zip_exporter=ZipArchiver()
    )
    
    try:
        await use_case.execute(url, export_pdf=True, export_zip=True)
    except Exception as e:
        print(f"[!] Lỗi: {e}")

if __name__ == "__main__":
    # Cần cài đặt: pip install httpx beautifulsoup4 Pillow
    asyncio.run(main())

```