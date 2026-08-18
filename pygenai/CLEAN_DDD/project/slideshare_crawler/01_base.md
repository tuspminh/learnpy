Để crawl một cuốn sách từ SlideShare theo chuẩn **Clean Architecture** và **DDD (Domain-Driven Design)**, hệ thống được phân tách thành 4 lớp độc lập: **Domain** (nghiệp vụ lõi), **Application** (kịch bản sử dụng), **Infrastructure** (giao tiếp bên ngoài như HTTP, File System), và **Presentation** (giao diện điều khiển CLI).

---

### Structure & Layer Responsibilities

| Layer | Component | Responsibility |
| --- | --- | --- |
| **Domain** | `Slide`, `Book` | Entity & Aggregate Root quản lý dữ liệu cuốn sách và các trang slide. |
| **Domain** | `ICrawler`, `IStorage` | Interfaces định nghĩa contract cào dữ liệu và lưu file (Dependency Inversion). |
| **Application** | `CrawlBookUseCase` | Điều phối luồng xử lý: gọi Scraper cào dữ liệu -> gọi Storage lưu file. |
| **Infrastructure** | `SlideShareScraper` | Cài đặt logic cào DOM/HTML thực tế từ URL SlideShare (BeautifulSoup). |
| **Infrastructure** | `LocalDiskStorage` | Cài đặt ghi dữ liệu ảnh xuống thư mục `output/`. |
| **Presentation** | `main.py` | CLI entry point nhận URL từ người dùng và khởi chạy Use Case. |

---

### Implementation (Python)

#### 1. Domain Layer (`domain/`)

```python
# domain/models.py
from dataclasses import dataclass
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

```

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

```

---

#### 2. Infrastructure Layer (`infrastructure/`)

```python
# infrastructure/scraper.py
import requests
from bs4 import BeautifulSoup
import re
from domain.models import Book, Slide
from domain.interfaces import ICrawler

class SlideShareScraper(ICrawler):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_book(self, url: str) -> Book:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Lấy tiêu đề sách
        title_elem = soup.find("h1") or soup.find("title")
        title = title_elem.get_text(strip=True) if title_elem else "slideshare_book"

        book = Book(title=title, source_url=url)

        # Lấy danh sách ảnh các slide
        images = soup.find_all("img", class_=re.compile(r"slide|Slide"))
        if not images:
            images = soup.select("picture source, img[data-full], img[srcset]")

        page_num = 1
        seen_urls = set()

        for img in images:
            # Ưu tiên lấy URL chất lượng cao nhất trong srcset hoặc src/data-full
            img_url = img.get("data-full") or img.get("src") or img.get("data-normal")
            if not img_url and img.get("srcset"):
                img_url = img.get("srcset").split(",")[-1].strip().split(" ")[0]

            if img_url and img_url.startswith("http") and img_url not in seen_urls:
                # Loại bỏ các thumbnail hoặc avatar nhỏ
                if "ss_thumbnails" not in img_url and "thumbnail" not in img_url:
                    seen_urls.add(img_url)
                    book.add_slide(Slide(page_number=page_num, image_url=img_url))
                    page_num += 1

        return book

    def download_image(self, image_url: str) -> bytes:
        response = requests.get(image_url, headers=self.headers)
        response.raise_for_status()
        return response.content

```

```python
# infrastructure/storage.py
import os
from domain.models import Slide
from domain.interfaces import IStorage

class LocalDiskStorage(IStorage):
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = base_output_dir

    def save_slide(self, book_title: str, slide: Slide, content: bytes) -> str:
        book_dir = os.path.join(self.base_output_dir, book_title)
        os.makedirs(book_dir, exist_ok=True)

        file_path = os.path.join(book_dir, f"page_{slide.page_number:03d}.jpg")
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

```

---

#### 3. Application Layer (`application/`)

```python
# application/use_cases.py
from domain.interfaces import ICrawler, IStorage

class CrawlBookUseCase:
    def __init__(self, crawler: ICrawler, storage: IStorage):
        self.crawler = crawler
        self.storage = storage

    def execute(self, url: str) -> None:
        print(f"[*] Đang lấy thông tin slide từ: {url}")
        book = self.crawler.fetch_book(url)
        
        print(f"[+] Tìm thấy cuốn sách: '{book.title}' với {len(book.slides)} trang.")
        
        for slide in book.slides:
            print(f" -> Đang tải trang {slide.page_number}/{len(book.slides)}...")
            image_data = self.crawler.download_image(slide.image_url)
            saved_path = self.storage.save_slide(book.title, slide, image_data)
            print(f"    Đã lưu: {saved_path}")

        print(f"\n[✓] Hoàn thành! Sách đã được lưu tại thư mục output/'{book.title}'")

```

---

#### 4. Presentation / CLI Entry Point (`main.py`)

```python
# main.py
import sys
from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
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
    
    use_case = CrawlBookUseCase(crawler=crawler, storage=storage)
    
    try:
        use_case.execute(url)
    except Exception as e:
        print(f"[!] Lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()

```

---

### Hướng dẫn chạy ứng dụng

1. **Cài đặt thư viện phụ thuộc:**
```bash
pip install requests beautifulsoup4

```


2. **Khởi chạy ứng dụng:**
```bash
python main.py "https://www.slideshare.net/slideshow/example-slide/123456"

```


3. **Cấu trúc dữ liệu đầu ra:**
```text
output/
└── [Tên_Cuốn_Sách]/
    ├── page_001.jpg
    ├── page_002.jpg
    └── page_003.jpg

```