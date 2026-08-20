Dưới đây là thiết kế chi tiết cho ứng dụng Crawl Book từ SlideShare chuyển đổi sang Onion Architecture.

Về bản chất, Onion Architecture rất gần với Clean Architecture, nhưng điểm đặc trưng của nó là tập trung tách biệt rõ ràng giữa Domain Entities (Thực thể), Domain Services (Logic thuần giữa các thực thể mà bản thân một thực thể không tự làm được) và định nghĩa các Ports (Interfaces) ngay tại ranh giới của tầng Application [the-onion-architecture, clean-architecture-vs-onion-architecture].

* * *

## 📂 Cấu trúc thư mục (Folder Tree) theo Onion Architecture
    
    
    slideshare_crawler/
    │
    ├── core/                        # Phần lõi trung tâm của hệ thống
    │   ├── domain/                  # Lớp 1 & Lớp 2: Domain Layer
    │   │   ├── __init__.py
    │   │   ├── entities.py          # Lớp 1: Khái niệm thực thể nghiệp vụ (Book, Slide)
    │   │   └── services.py          # Lớp 2: Logic xử lý tên/định dạng chuẩn của Domain
    │   │
    │   └── application/             # Lớp 3: Application Services (Điều phối Use Cases)
    │       ├── __init__.py
    │       ├── ports.py             # Các cổng (Interfaces) trừu tượng để lớp ngoài cắm vào
    │       └── services.py          # Luồng công việc chính (Workflow: Crawl -> Save -> PDF)
    │
    ├── infrastructure/              # Lớp 4: Lớp ngoài cùng (Chứa toàn bộ công nghệ cụ thể)
    │   ├── __init__.py
    │   ├── crawler/                 # Thư viện BeautifulSoup, Requests/Aiohttp để cào
    │   │   └── ss_crawler.py
    │   ├── storage/                 # Thư viện hệ điều hành (os, shutil) để ghi file
    │   │   └── local_storage.py
    │   └── pdf/                     # Thư viện PyMuPDF (fitz) để xử lý PDF
    │       └── fitz_generator.py
    │
    ├── output/                      # Thư mục sinh ra trong quá trình chạy ứng dụng
    │   └── [book-name]/
    │
    └── main.py                      # Composition Root: Điểm khởi tạo và tiêm phụ thuộc (DI)
    

* * *

## 💻 Mã nguồn chi tiết theo các tầng của Onion Architecture

## 1\. Tầng Domain Core (`core/domain/`)

  * Lớp 1: Domain Entities (`core/domain/entities.py`)  
Chứa cấu trúc dữ liệu thuần túy nhất của thực thể.


    
    
    # core/domain/entities.py
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class Slide:
        index: int
        url: str
        file_name: str = ""
    
    @dataclass
    class Book:
        title: str
        source_url: str
        slides: List[Slide] = field(default_factory=list)
    

  * Lớp 2: Domain Services (`core/domain/services.py`)  
Chứa các quy tắc nghiệp vụ xử lý dữ liệu chung. Ở đây là chuẩn hóa tên sách tránh ký tự lỗi của hệ điều hành và đánh số thứ tự file ảnh.


    
    
    # core/domain/services.py
    import re
    from core.domain.entities import Book
    
    class BookDomainService:
        @staticmethod
        def generate_safe_title(title: str) -> str:
            """Chuẩn hóa tiêu đề sách thành tên thư mục hợp lệ"""
            return re.sub(r'[\\/*?:"<>| ]', '_', title).strip('_')
    
        @staticmethod
        def format_slide_filenames(book: Book) -> None:
            """Tự động đặt tên file cho từng slide theo đúng chuẩn định dạng"""
            for slide in book.slides:
                slide.file_name = f"slide_{slide.index:03d}.jpg"
    

## 2\. Tầng Application Services (`core/application/`)

  * Cổng giao tiếp trừu tượng (`core/application/ports.py`)  
Định nghĩa ranh giới (Ports) dưới dạng các `ABC` class (Abstract Base Classes) để ứng dụng giao tiếp với thế giới hạ tầng bên ngoài.


    
    
    # core/application/ports.py
    from abc import ABC, abstractmethod
    from core.domain.entities import Book
    
    class ICrawlerPort(ABC):
        @abstractmethod
        def fetch_book_metadata(self, url: str) -> Book:
            """Cào tiêu đề và danh sách slide thô"""
            pass
    
        @abstractmethod
        async def download_slide_content(self, session, url: str) -> bytes:
            """Tải dữ liệu bytes của slide (Bất đồng bộ)"""
            pass
    
    class IStoragePort(ABC):
        @abstractmethod
        def save_file(self, folder_name: str, file_name: str, content: bytes) -> str:
            """Lưu file xuống bộ nhớ vật lý"""
            pass
    
    class IPdfGeneratorPort(ABC):
        @abstractmethod
        def build_pdf(self, image_paths: list, output_path: str) -> None:
            """Tạo file PDF từ danh sách ảnh bằng Fitz"""
            pass
    

  * Ứng dụng điều phối (`core/application/services.py`)  
Nơi thực hiện Use Case (luồng đi của ứng dụng). Nó kết hợp logic từ tầng Domain Services và gọi các hàm qua `Ports`.


    
    
    # core/application/services.py
    import asyncio
    import aiohttp
    from core.application.ports import ICrawlerPort, IStoragePort, IPdfGeneratorPort
    from core.domain.services import BookDomainService
    
    class BookCrawlApplicationService:
        def __init__(self, crawler: ICrawlerPort, storage: IStoragePort, pdf_generator: IPdfGeneratorPort):
            # Điểm nhận Dependency Injection từ ngoài vào
            self.crawler = crawler
            self.storage = storage
            self.pdf_generator = pdf_generator
    
        async def _download_and_store(self, session, slide, folder_name) -> str:
            """Tác vụ tải và lưu một slide"""
            img_bytes = await self.crawler.download_slide_content(session, slide.url)
            saved_path = self.storage.save_file(folder_name, slide.file_name, img_bytes)
            return saved_path
    
        async def execute(self, slideshare_url: str, max_concurrent: int = 5) -> str:
            print(f"[*] Bắt đầu xử lý URL: {slideshare_url}")
            
            # 1. Gọi hạ tầng cào dữ liệu thô
            book = self.crawler.fetch_book_metadata(slideshare_url)
            
            # 2. Áp dụng nghiệp vụ của lớp Domain để chuẩn hóa dữ liệu
            safe_folder = BookDomainService.generate_safe_title(book.title)
            BookDomainService.format_slide_filenames(book)
            print(f"[+] Sách hợp lệ: '{safe_folder}' ({len(book.slides)} slides)")
    
            # 3. Tải bất đồng bộ thông qua Port hạ tầng
            print("[*] Đang tải các trang slide bất đồng bộ...")
            connector = aiohttp.TCPConnector(limit_per_host=max_concurrent)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    self._download_and_store(session, slide, safe_folder)
                    for slide in book.slides
                ]
                # Kích hoạt chạy song song
                image_paths = await asyncio.gather(*tasks)
    
            # 4. Đóng gói PDF thông qua Port
            output_pdf = f"output/{safe_folder}/{safe_folder}.pdf"
            print("[*] Đang chuyển đổi ảnh sang PDF bằng PyMuPDF (Fitz)...")
            self.pdf_generator.build_pdf(image_paths, output_pdf)
            
            print(f"[🎉] HOÀN THÀNH: {output_pdf}")
            return output_pdf
    

## 3\. Tầng Hạ tầng Ngoài cùng (`infrastructure/`)

Nơi cài đặt chi tiết tất cả các thư viện công nghệ nặng ký. Các Class ở đây bắt buộc phải kế thừa (triển khai) các Port ở tầng Application [clean-architecture-vs-onion-architecture].

  * Hạ tầng Cào (`infrastructure/crawler/ss_crawler.py`):


    
    
    # infrastructure/crawler/ss_crawler.py
    import requests
    import aiohttp
    from bs4 import BeautifulSoup
    from core.application.ports import ICrawlerPort
    from core.domain.entities import Book, Slide
    
    class SlideShareCrawlerAdapter(ICrawlerPort):
        def fetch_book_metadata(self, url: str) -> Book:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                raise RuntimeError(f"Lỗi kết nối SlideShare: {res.status_code}")
                
            soup = BeautifulSoup(res.text, 'html.parser')
            title_tag = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
            title = title_tag.text.strip() if title_tag else "Untitled"
    
            slides = []
            index = 1
            for img in soup.find_all('img'):
                src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if src and "slide-" in src:
                    clean_url = src.split('?')[0]
                    # Tránh trùng lặp URL slide
                    if clean_url not in [s.url for s in slides]:
                        slides.append(Slide(index=index, url=clean_url))
                        index += 1
                        
            if not slides:
                raise ValueError("Không tìm thấy dữ liệu ảnh slide nào trên trang này.")
                
            return Book(title=title, source_url=url, slides=slides)
    
        async def download_slide_content(self, session: aiohttp.ClientSession, url: str) -> bytes:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Không thể tải ảnh: {url}")
                return await response.read()
    

  * Hạ tầng Lưu trữ (`infrastructure/storage/local_storage.py`):


    
    
    # infrastructure/storage/local_storage.py
    import os
    from core.application.ports import IStoragePort
    
    class LocalStorageAdapter(IStoragePort):
        def __init__(self, base_path: str = "output"):
            self.base_path = base_path
    
        def save_file(self, folder_name: str, file_name: str, content: bytes) -> str:
            target_dir = os.path.join(self.base_path, folder_name)
            os.makedirs(target_dir, exist_ok=True)
            
            file_path = os.path.join(target_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(content)
            return file_path
    

  * Hạ tầng đóng gói PDF (`infrastructure/pdf/fitz_generator.py`):


    
    
    # infrastructure/pdf/fitz_generator.py
    import fitz  # Thư viện PyMuPDF
    from core.application.ports import IPdfGeneratorPort
    
    class FitzPdfGeneratorAdapter(IPdfGeneratorPort):
        def build_pdf(self, image_paths: list, output_path: str) -> None:
            doc = fitz.open()
            for img_path in image_paths:
                img_doc = fitz.open(img_path)
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
                
                page_doc = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(page_doc)
                page_doc.close()
                
            doc.save(output_path)
            doc.close()
    

* * *

## 🚀 Điểm kết nối ứng dụng (`main.py`)

Tại lớp ngoài cùng này, chúng ta sử dụng `click` làm CLI và thực hiện việc khởi tạo các Adapter để "tiêm" thẳng vào dịch vụ Application (Dependency Injection) [the-onion-architecture, clean-architecture-vs-onion-architecture].
    
    
    # main.py
    import asyncio
    import click
    
    # Import Hạ tầng (Lớp ngoài cùng)
    from infrastructure.crawler.ss_crawler import SlideShareCrawlerAdapter
    from infrastructure.storage.local_storage import LocalStorageAdapter
    from infrastructure.pdf.fitz_generator import FitzPdfGeneratorAdapter
    
    # Import Ứng dụng (Lớp bên trong)
    from core.application.services import BookCrawlApplicationService
    
    @click.command()
    @click.argument('url', type=str)
    @click.option('--workers', '-w', default=5, help='Số lượng luồng cào ảnh song song.')
    def main(url, workers):
        """Crawl sách SlideShare chuẩn cấu trúc Onion Architecture và xuất PDF bằng Fitz."""
        
        # 1. Khởi tạo các adapter thực tế từ lớp hạ tầng bên ngoài
        crawler_adapter = SlideShareCrawlerAdapter()
        storage_adapter = LocalStorageAdapter(base_path="output")
        pdf_adapter = FitzPdfGeneratorAdapter()
    
        # 2. Tiêm các adapter xuyên qua cổng Port để cấp cho Service lớp trong
        app_service = BookCrawlApplicationService(
            crawler=crawler_adapter,
            storage=storage_adapter,
            pdf_generator=pdf_adapter
        )
    
        # 3. Kích hoạt tiến trình bất đồng bộ
        try:
            asyncio.run(app_service.execute(slideshare_url=url, max_concurrent=workers))
        except Exception as e:
            click.secho(f"\n[❌] THẤT BẠI: {e}", fg="red", bold=True)
    
    if __name__ == "__main__":
        main()
    

* * *

## 💡 Sự khác biệt tinh tế của mã nguồn này so với Clean Architecture:

  1. Sự xuất hiện của `Domain Services` (`core/domain/services.py`): Trong Clean Architecture, Use Case thường trực tiếp điều khiển dữ liệu thực thể. Trong cấu trúc Onion này, toàn bộ quy tắc biến đổi chuỗi dữ liệu (đổi tên thư mục an toàn, định dạng số thứ tự slide `001, 002`) được bàn giao hẳn cho một dịch vụ miền riêng biệt (`BookDomainService`).
  2. Cấu trúc thư mục đóng gói (`core/`): Thư mục `core` đóng vai trò là một khối độc lập hoàn chỉnh chứa cả Domain và Application [the-onion-architecture, clean-architecture-vs-onion-architecture]. Tất cả các công nghệ bên ngoài (`infrastructure/`) chỉ là "vỏ bọc" có thể bóc tách hoặc thay đổi bất cứ lúc nào.



Bạn có muốn bổ sung thêm tính năng ghi log (logging) lưu lại lịch sử cào sách thành công/thất bại vào một file cấu hình riêng ở tầng hạ tầng (`infrastructure/logging/`) nữa không?