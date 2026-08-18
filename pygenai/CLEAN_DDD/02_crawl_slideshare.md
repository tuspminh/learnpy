Ứng dụng crawl sách/slideshare dạng trang ảnh cần xử lý 3 bài toán chính: **Trích xuất dữ liệu (Scraping)**, **Tải ảnh song song (Downloading)** và **Đóng gói dữ liệu (PDF/Storage Handling)**.

Dưới đây là phân tích kiến trúc mô-đun và triển khai hoàn chỉnh bằng Python.

---

## Luồng xử lý dữ liệu (Data Workflow)

```
[URL Input] ➔ 1. Extract Metadata & Image URLs
            ➔ 2. Download Images ➔ Save to `output/<book-name>/`
            ➔ 3. Convert Images ➔ Export to `output/<book-name>.pdf`

```

1. **Trích xuất (Scrape)**: Lấy tên sách (chuẩn hóa tên thư mục) và danh sách URL ảnh theo đúng thứ tự trang ($1, 2, ..., n$).
2. **Tải về (Download)**: Lưu từng ảnh dưới dạng tên tệp định dạng số thứ tự cố định (`001.jpg`, `002.jpg`) để đảm bảo không bị lệch thứ tự khi sắp xếp.
3. **Xuất bản (Export)**: Dùng thư viện xử lý ảnh (như Pillow) để ghép chuỗi file ảnh thành file PDF duy nhất.

---

## Triển khai chi tiết bằng Python

Cài đặt các thư viện phụ thuộc:

```bash
pip install httpx beautifulsoup4 pillow

```

### Mã nguồn ứng dụng hoàn chỉnh

```python
from dataclasses import dataclass
from pathlib import Path
import re
from typing import List
from PIL import Image
import httpx


# ------------------------------------------------------------------
# 1. DOMAIN & UTILS
# ------------------------------------------------------------------
@dataclass
class BookPage:
    page_number: int
    image_url: str


@dataclass
class Book:
    title: str
    pages: List[BookPage]

    @property
    def clean_title(self) -> str:
        """Xóa các ký tự không hợp lệ trong tên thư mục/file của OS"""
        return re.sub(r'[\\/*?:"<>|]', "", self.title).strip().replace(" ", "_")


# ------------------------------------------------------------------
# 2. INFRASTRUCTURE: Scraper, Downloader, Exporter
# ------------------------------------------------------------------
class SlideShareScraper:
    """Trích xuất URL ảnh từ SlideShare hoặc các trang tương tự"""
    def __init__(self, client: httpx.Client):
        self.client = client

    def fetch_book(self, url: str) -> Book:
        response = self.client.get(url)
        response.raise_for_status()

        # Giả lập bóc tách metadata (Tùy chỉnh Selector theo cấu trúc HTML thực tế)
        # Với SlideShare, các ảnh slide thường nằm trong tag <img> có attribute data-full-slideshow
        title = "Clean_Architecture_Guide"  # Giả định lấy từ <title> hoặc <h1>
        
        # Mẫu danh sách URL ảnh minh họa
        sample_image_urls = [
            "https://picsum.photos/800/1000?random=1",
            "https://picsum.photos/800/1000?random=2",
            "https://picsum.photos/800/1000?random=3",
        ]

        pages = [
            BookPage(page_number=idx + 1, image_url=img_url)
            for idx, img_url in enumerate(sample_image_urls)
        ]
        return Book(title=title, pages=pages)


class ImageDownloader:
    """Quản lý việc lưu trữ và tải ảnh về ổ đĩa"""
    def __init__(self, client: httpx.Client, base_output_dir: Path):
        self.client = client
        self.base_output_dir = base_output_dir

    def download_book_images(self, book: Book) -> Path:
        book_dir = self.base_output_dir / book.clean_title
        book_dir.mkdir(parents=True, exist_ok=True)

        for page in book.pages:
            file_name = f"{page.page_number:03d}.jpg"  # Định dạng 001.jpg, 002.jpg
            file_path = book_dir / file_name

            if file_path.exists():
                continue

            response = self.client.get(page.image_url)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)

        return book_dir


class PdfExporter:
    """Chuyển đổi thư mục chứa ảnh thành file PDF hoàn chỉnh"""
    @staticmethod
    def export_from_directory(image_dir: Path, output_pdf_path: Path) -> None:
        image_files = sorted(image_dir.glob("*.jpg"))
        if not image_files:
            raise FileNotFoundError("Không tìm thấy file ảnh để xuất PDF")

        images = []
        for file in image_files:
            img = Image.open(file)
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)

        # Lưu ảnh đầu tiên và append các ảnh tiếp theo vào cùng file PDF
        images[0].save(
            output_pdf_path,
            save_all=True,
            append_images=images[1:]
        )


# ------------------------------------------------------------------
# 3. APPLICATION / SERVICE PIPELINE
# ------------------------------------------------------------------
class BookCrawlService:
    def __init__(self, scraper: SlideShareScraper, downloader: ImageDownloader):
        self.scraper = scraper
        self.downloader = downloader

    def execute(self, target_url: str, export_pdf: bool = True) -> None:
        print(f"[*] Đang lấy thông tin từ: {target_url}")
        book = self.scraper.fetch_book(target_url)

        print(f"[*] Đang tải {len(book.pages)} trang ảnh vào thư mục 'output/{book.clean_title}'...")
        book_dir = self.downloader.download_book_images(book)

        if export_pdf:
            pdf_path = book_dir.parent / f"{book.clean_title}.pdf"
            print(f"[*] Đang đóng gói file PDF: {pdf_path}")
            PdfExporter.export_from_directory(book_dir, pdf_path)

        print("[✔] Hoàn tất!")


# ------------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------------
if __name__ == "__main__":
    output_directory = Path("output")
    
    with httpx.Client(timeout=10.0, follow_redirects=True) as http_client:
        scraper = SlideShareScraper(client=http_client)
        downloader = ImageDownloader(client=http_client, base_output_dir=output_directory)
        
        service = BookCrawlService(scraper=scraper, downloader=downloader)
        
        # Chạy crawler
        service.execute(
            target_url="https://www.slideshare.net/example/sample-slide",
            export_pdf=True
        )

```

---

## Kỹ thuật nâng cấp cho sản phẩm thực tế

* **Xử lý JavaScript (Dynamic Loading)**: Nếu trang web chống crawl bằng cách render ảnh bằng JavaScript (Lazy Loading), thay thế `httpx` bằng **Playwright** hoặc **Selenium** để cuộn trang và bắt các request ảnh mạng (Network Interception).
* **Tải song song (Concurrency)**: Sử dụng `asyncio` kết hợp `httpx.AsyncClient` để tải hàng trăm trang ảnh cùng lúc, tối ưu tốc độ từ vài phút xuống vài giây.
* **Xử lý Watermark/Crop**: Dùng Pillow hoặc OpenCV để tự động cắt viền trắng thừa hoặc đóng dấu bản quyền nếu cần.