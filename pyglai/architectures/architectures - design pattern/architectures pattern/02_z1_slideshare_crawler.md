Dưới đây là thiết kế chi tiết cho ứng dụng Crawl Book từ SlideShare theo đúng chuẩn Clean Architecture.

Ứng dụng sẽ tải các hình ảnh slide của sách, lưu vào thư mục `output/<book-name>/` và xuất ra file PDF bằng thư viện PyMuPDF (trong Python có tên module là `fitz`, viết tắt là flitz như bạn đề xuất).

* * *

## 📂 Cấu trúc thư mục (Folder Tree) theo Clean Architecture
    
    
    slideshare_crawler/
    │
    ├── domain/                      # Vòng 1: Core Logic (Không import thư viện ngoài)
    │   ├── __init__.py
    │   └── entities.py              # Định nghĩa thực thể Book và Slide
    │
    ├── application/                 # Vòng 2: Use Cases & Interfaces (Ports)
    │   ├── __init__.py
    │   ├── ports.py                 # Interface cho Crawler, Storage và PDF Generator
    │   └── use_cases.py             # Logic điều phối: Crawl -> Lưu ảnh -> Xuất PDF
    │
    ├── adapters/                    # Vòng 3: Adapters (Chuyển đổi dữ liệu)
    │   ├── __init__.py
    │   ├── crawler.py               # Triển khai cào dữ liệu (BeautifulSoup/Requests)
    │   ├── storage.py               # Triển khai lưu file xuống ổ cứng (os/shutil)
    │   └── pdf_generator.py         # Triển khai xuất PDF bằng PyMuPDF (fitz)
    │
    ├── output/                      # Thư mục chứa kết quả đầu ra (Được tạo tự động)
    │   └── [book-name]/
    │       ├── slide_001.jpg
    │       ├── slide_002.jpg
    │       └── [book-name].pdf
    │
    └── main.py                      # Composition Root: Ráp nối và kích hoạt ứng dụng
    

Để chạy ứng dụng này, bạn cần cài đặt các thư viện sau:
    
    
    pip install beautifulsoup4 requests pymupdf
    

* * *

## 💻 Mã nguồn chi tiết theo từng lớp

## 1\. Lớp Domain (`domain/entities.py`)

Chứa định nghĩa thuần túy về dữ liệu của cuốn sách, không quan tâm đến việc nó được cào bằng công cụ nào hay lưu ở đâu.
    
    
    # domain/entities.py
    import re
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class Book:
        title: str
        url: str
        slide_urls: List[str] = None
    
        @property
        def safe_title(self) -> str:
            """Biến đổi tên sách thành tên thư mục hợp lệ (bỏ ký tự đặc biệt)"""
            return re.sub(r'[\\/*?:"<>| ]', '_', self.title).strip('_')
    

## 2\. Lớp Application (`application/ports.py` & `application/use_cases.py`)

Định nghĩa các cổng giao tiếp trừu tượng và kịch bản vận hành chính của ứng dụng.

_Cổng giao tiếp (Interfaces/Ports):_
    
    
     # application/ports.py
    from abc import ABC, abstractmethod
    from domain.entities import Book
    
    class ICrawler(ABC):
        @abstractmethod
        def fetch_book_info(self, url: str) -> Book:
            """Lấy tiêu đề và danh sách link ảnh slide từ SlideShare"""
            pass
    
        @abstractmethod
        def download_image(self, img_url: str) -> bytes:
            """Tải dữ liệu ảnh dạng bytes từ URL"""
            pass
    
    class IStorage(ABC):
        @abstractmethod
        def save_slide(self, book_title: str, file_name: str, content: bytes) -> str:
            """Lưu file ảnh vào thư mục output/book-name/"""
            pass
    
    class IPdfGenerator(ABC):
        @abstractmethod
        def convert_images_to_pdf(self, image_paths: list, output_pdf_path: str) -> None:
            """Gộp các ảnh slide lại thành một file PDF"""
            pass
    

_Kịch bản xử lý (Use Case):_
    
    
     # application/use_cases.py
    from application.ports import ICrawler, IStorage, IPdfGenerator
    
    class CrawlAndExportBookUseCase:
        def __init__(self, crawler: ICrawler, storage: IStorage, pdf_generator: IPdfGenerator):
            self.crawler = crawler
            self.storage = storage
            self.pdf_generator = pdf_generator
    
        def execute(self, slideshare_url: str) -> str:
            print(f"[*] Đang khởi chạy tiến trình cào dữ liệu từ: {slideshare_url}")
            
            # 1. Thu thập thông tin sách từ internet
            book = self.crawler.fetch_book_info(slideshare_url)
            print(f"[+] Đã tìm thấy sách: '{book.title}' với {len(book.slide_urls)} trang slide.")
    
            # 2. Tải từng trang slide và lưu xuống ổ cứng
            saved_image_paths = []
            for index, img_url in enumerate(book.slide_urls, start=1):
                file_name = f"slide_{index:03d}.jpg"
                print(f" -> Đang tải trang {index}/{len(book.slide_urls)}...", end="\r")
                
                img_bytes = self.crawler.download_image(img_url)
                saved_path = self.storage.save_slide(book.safe_title, file_name, img_bytes)
                saved_image_paths.append(saved_path)
            
            print("\n[+] Đã tải xong toàn bộ hình ảnh slide.")
    
            # 3. Xuất file PDF bằng Fitz (PyMuPDF)
            pdf_name = f"{book.safe_title}.pdf"
            # Đường dẫn lưu file PDF nằm chung thư mục với ảnh
            output_pdf_path = f"output/{book.safe_title}/{pdf_name}"
            
            print(f"[*] Đang tiến hành đóng gói file PDF qua thư viện Fitz...")
            self.pdf_generator.convert_images_to_pdf(saved_image_paths, output_pdf_path)
            
            print(f"[🎉] THÀNH CÔNG! Sách đã được lưu tại: output/{book.safe_title}/")
            return output_pdf_path
    

## 3\. Lớp Adapters (`adapters/`)

Nơi cài đặt chi tiết công nghệ (BeautifulSoup, Fitz, OS).

_Bộ cào dữ liệu (`adapters/crawler.py`):_
    
    
    # adapters/crawler.py
    import requests
    from bs4 import BeautifulSoup
    from domain.entities import Book
    from application.ports import ICrawler
    
    class SlideShareCrawler(ICrawler):
        def fetch_book_info(self, url: str) -> Book:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Không thể truy cập SlideShare (Status code: {response.status_code})")
    
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Lấy tiêu đề sách
            title_element = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
            title = title_element.text.strip() if title_element else "Untitled_Book"
            
            # Tìm tất cả các thẻ hình ảnh của Slide (SlideShare thường dùng thẻ source hoặc img với srcset/src)
            # Lưu ý: Cấu trúc HTML thực tế của SlideShare có thể thay đổi tùy thời điểm
            images = soup.find_all('img', {'class': re.compile(r'slide.*|Slide.*')}) or soup.find_all('picture')
            
            slide_urls = []
            for img in soup.find_all('img'):
                src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if src and "slide-" in src:  # Lọc ra các url chứa ảnh slide
                    # Chuẩn hóa link bỏ các tham số query nếu có
                    clean_src = src.split('?')[0]
                    if clean_src not in slide_urls:
                        slide_urls.append(clean_src)
    
            if not slide_urls:
                raise Exception("Không tìm thấy liên kết hình ảnh slide nào. Hãy kiểm tra lại cấu trúc URL.")
    
            return Book(title=title, url=url, slide_urls=slide_urls)
    
        def download_image(self, img_url: str) -> bytes:
            response = requests.get(img_url, timeout=10)
            return response.content
    

_Bộ lưu trữ dữ liệu (`adapters/storage.py`):_
    
    
    # adapters/storage.py
    import os
    from application.ports import IStorage
    
    class LocalStorage(IStorage):
        def __init__(self, base_dir: str = "output"):
            self.base_dir = base_dir
    
        def save_slide(self, book_title: str, file_name: str, content: bytes) -> str:
            # Tạo thư mục output/book-name/ nếu chưa có
            target_dir = os.path.join(self.base_dir, book_title)
            os.makedirs(target_dir, exist_ok=True)
            
            file_path = os.path.join(target_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(content)
            return file_path
    

_Bộ chuyển đổi ảnh sang PDF bằng PyMuPDF (`adapters/pdf_generator.py`):_
    
    
    # adapters/pdf_generator.py
    import fitz  # PyMuPDF [1]
    from application.ports import IPdfGenerator
    
    class FitzPdfGenerator(IPdfGenerator):
        def convert_images_to_pdf(self, image_paths: list, output_pdf_path: str) -> None:
            doc = fitz.open()  # Khởi tạo một file PDF trống [1]
            
            for img_path in image_paths:
                # Mở file ảnh làm một tài liệu tạm thời
                img_doc = fitz.open(img_path)
                
                # Chuyển đổi ảnh thành định dạng trang PDF
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
                
                # Nạp trang vừa chuyển đổi vào file PDF chính
                page_doc = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(page_doc)
                page_doc.close()
                
            # Lưu và đóng file PDF hoàn chỉnh
            doc.save(output_pdf_path)
            doc.close()
    

* * *

## 🚀 Điểm kết nối và Khởi chạy (`main.py`)

File `main.py` nằm ở lớp ngoài cùng, đóng vai trò làm Composition Root. Nó sẽ khởi tạo các công cụ cụ thể từ lớp Adapters rồi "tiêm" (Inject) vào lớp Use Case ở trong cùng.
    
    
    # main.py
    from adapters.crawler import SlideShareCrawler
    from adapters.storage import LocalStorage
    from adapters.pdf_generator import FitzPdfGenerator
    from application.use_cases import CrawlAndExportBookUseCase
    
    def main():
        # 1. Cấu hình các công cụ hạ tầng (Infrastructure/Adapters)
        crawler_infra = SlideShareCrawler()
        storage_infra = LocalStorage(base_dir="output")
        pdf_infra = FitzPdfGenerator()
    
        # 2. Inject vào Use Case của tầng Application
        use_case = CrawlAndExportBookUseCase(
            crawler=crawler_infra,
            storage=storage_infra,
            pdf_generator=pdf_infra
        )
    
        # 3. Chạy chương trình với một URL SlideShare bất kỳ
        # (Thay thế URL dưới đây bằng URL thật bạn muốn cào)
        target_url = "https://slideshare.net"
        
        try:
            pdf_result = use_case.execute(target_url)
        except Exception as e:
            print(f"\n[❌] Có lỗi xảy ra trong quá trình xử lý: {e}")
    
    if __name__ == "__main__":
        main()
    

## 💡 Tại sao thiết kế này chuẩn Clean Architecture?

  * Tính độc lập cao: Nếu ngày mai SlideShare đổi thuật toán và bạn muốn chuyển sang cào sách từ _Docco_ hoặc _LinkIn_ , bạn chỉ cần viết một class mới kế thừa `ICrawler` trong thư mục `adapters` mà không cần sửa một dòng code nào trong file xử lý logic `use_cases.py`.
  * Dễ dàng Mocking/Testing: Bạn có thể viết Unit Test cho `CrawlAndExportBookUseCase` bằng cách truyền vào các đối tượng Giả lập (Mock) mà không cần phải kết nối mạng internet hay ghi file thật vào ổ cứng.



Nếu bạn muốn nâng cấp ứng dụng này, tôi có thể hỗ trợ bạn bổ sung thêm:

  * Tính năng xử lý bất đồng bộ (Asyncio/Aiohttp) để tăng tốc độ tải hàng trăm ảnh slide cùng lúc.
  * Thêm giao diện dòng lệnh (CLI) bằng thư viện `click` hoặc `argparse` để gõ lệnh tải sách từ Terminal dễ dàng hơn.



Bạn muốn phát triển thêm tính năng nào trước?