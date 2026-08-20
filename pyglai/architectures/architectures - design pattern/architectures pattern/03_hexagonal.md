Hexagonal Architecture (Kiến trúc lục giác), còn được gọi là Ports and Adapters Architecture, là một mẫu kiến trúc phần mềm do Alistair Cockburn giới thiệu vào năm 2005.

Mục tiêu cốt lõi của Hexagonal Architecture là tách biệt Logic nghiệp vụ cốt lõi (Domain) khỏi các yếu tố kỹ thuật bên ngoài (như Database, Web UI, API bên thứ ba, hàng đợi tin nhắn). Nhờ đó, ứng dụng có thể được kiểm thử (Test) hoặc hoán đổi công nghệ một cách dễ dàng mà không làm ảnh hưởng đến mã nguồn nghiệp vụ.

Triết lý của Hexagonal Architecture chính là nền tảng trực tiếp khai sinh ra Onion Architecture và Clean Architecture sau này.

* * *

## 🌟 Cấu trúc 3 thành phần cốt lõi của Hexagonal Architecture

Sở dĩ mô hình này có tên là "Lục giác" (Hexagon) vì nó mô phỏng một khối logic ở trung tâm có nhiều cạnh (mặt tiếp xúc), mỗi cạnh đại diện cho một cổng giao tiếp với thế giới bên ngoài.
    
    
          +-------------------------------------------------------------+
    
          |                 Hạ tầng bên ngoài (Infrastructure)          |
          |                                                             |
          |   [ Web App / FastAPI ]         [ Database (SQLAlchemy) ]   |
          |             |                               ^               |
          +-------------|-------------------------------|---------------+
    
                        | (Gọi)                         | (Triển khai)
                        v                               |
          +-------------|-------------------------------|---------------+
    
          |             v                               |               |
          |       +------------+                 +------------+         |
          |       | Input Port |                 | Output Port|         |
          |       +------------+                 +------------+         |
          |             |                               ^               |
          |             v                               |               |
          |       +-------------------------------------------+         |
          |       |         ỨNG DỤNG CỐT LÕI (DOMAIN)         |         |
          |       +-------------------------------------------+         |
          |                                                             |
          |                      TẦNG BÊN TRONG (INSIDE)                |
          +-------------------------------------------------------------+
    

  1. The Inside (Bên trong - Ứng dụng & Domain):

     * Chứa thực thể dữ liệu (Entities) và logic nghiệp vụ (Use Cases).
     * Vùng này hoàn toàn cô lập, không phụ thuộc vào bất kỳ công nghệ hay thư viện mạng/DB nào.

  2. Ports (Cổng giao tiếp):

     * Nằm ở ranh giới của khối Lục giác. Trong Python, Ports được định nghĩa bằng các lớp trừu tượng (`abc.ABC`).
     * Input Port (Driving Port): Cổng do bên ngoài gọi vào để yêu cầu ứng dụng thực hiện một chức năng (Ví dụ: `IBookCrawler`).
     * Output Port (Driven Port): Cổng do ứng dụng gọi ra để tương tác với hạ tầng, như lưu file hoặc ghi DB (Ví dụ: `IStorage`, `IPdfGenerator`).

  3. Adapters (Bộ chuyển đổi - Lớp ngoài cùng):

     * Nằm ở bên ngoài khối Lục giác, kết nối trực tiếp với công nghệ thực tế.
     * Input Adapter (Primary/Driving Adapter): Chuyển đổi request từ UI/CLI/API thành lời gọi hàm phù hợp với Input Port (Ví dụ: Một hàm nhận lệnh từ CLI `click` sẽ gọi Use Case).
     * Output Adapter (Secondary/Driven Adapter): Triển khai thực tế các hàm của Output Port (Ví dụ: Code ghi file bằng thư viện `os`, code gộp ảnh PDF bằng `fitz`).




* * *

## 📂 Cấu trúc thư mục (Folder Tree) Hexagonal chuẩn trong Python

Áp dụng vào bài toán Crawl Book SlideShare và xuất PDF, cấu trúc thư mục sẽ phân ranh giới rạch ròi giữa `domain` (Inside), `ports` (Boundary) và `adapters` (Outside).
    
    
    slideshare_hexagon/
    │
    ├── domain/                      # INSIDE: Logic nghiệp vụ thuần túy
    │   ├── __init__.py
    │   └── models.py                # Định nghĩa cấu trúc Book và Slide
    │
    ├── ports/                       # BOUNDARY: Các cổng giao tiếp trừu tượng
    │   ├── __init__.py
    │   ├── inputs.py                # Input Ports: Các kịch bản Use Case mà ứng dụng cung cấp
    │   └── outputs.py               # Output Ports: Các cổng dịch vụ ứng dụng cần để chạy
    │
    ├── adapters/                    # OUTSIDE: Triển khai công nghệ thực tế
    │   ├── __init__.py
    │   ├── driving/                 # Bộ điều khiển hướng vào (CLI, API)
    │   │   └── cli_command.py       # Nhận lệnh CLI bằng thư viện Click
    │   │
    │   └── driven/                  # Bộ dịch vụ hướng ra ngoài (Hạ tầng, Thư viện)
    │       ├── ss_crawler.py        # Triển khai cào qua BeautifulSoup & aiohttp
    │       ├── local_storage.py     # Triển khai ghi file xuống ổ đĩa vật lý
    │       └── fitz_generator.py    # Triển khai xuất PDF bằng PyMuPDF (fitz)
    │
    └── main.py                      # Composition Root: Khởi tạo, cấu hình và kích hoạt app
    

* * *

## 💻 Mã nguồn chi tiết ứng dụng Crawl Sách theo Lục giác

## 1\. Tầng lõi Domain (`domain/models.py`)
    
    
    # domain/models.py
    import re
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class Slide:
        index: int
        url: str
    
        @property
        def file_name(self) -> str:
            return f"slide_{self.index:03d}.jpg"
    
    @dataclass
    class Book:
        title: str
        source_url: str
        slides: List[Slide] = field(default_factory=list)
    
        @property
        def safe_title(self) -> str:
            return re.sub(r'[\\/*?:"<>| ]', '_', self.title).strip('_')
    

## 2\. Định nghĩa các Cổng giao tiếp (`ports/`)

  * Output Ports (`ports/outputs.py`): Ứng dụng ra lệnh ra bên ngoài.


    
    
    # ports/outputs.py
    from abc import ABC, abstractmethod
    from domain.models import Book
    
    class ICrawlerService(ABC):
        @abstractmethod
        def fetch_metadata(self, url: str) -> Book: pass
    
        @abstractmethod
        async def download_image(self, session, url: str) -> bytes: pass
    
    class IStorageService(ABC):
        @abstractmethod
        def write_file(self, folder_name: str, file_name: str, data: bytes) -> str: pass
    
    class IPdfService(ABC):
        @abstractmethod
        def create_pdf(self, img_paths: list, output_path: str) -> None: pass
    

  * Input Ports (`ports/inputs.py`): Thế giới bên ngoài ra lệnh vào ứng dụng.


    
    
    # ports/inputs.py
    from abc import ABC, abstractmethod
    
    class IBookUseCase(ABC):
        @abstractmethod
        async def run(self, url: str, concurrency: int) -> str:
            """Kịch bản thực thi chính của ứng dụng"""
            pass
    

## 3\. Triển khai Logic ứng dụng thuộc Input Port

Nó nạp các Output Ports thông qua hàm khởi tạo (Dependency Injection) và thực hiện luồng nghiệp vụ.
    
    
    # domain/use_cases.py
    import asyncio
    import aiohttp
    from ports.inputs import IBookUseCase
    from ports.outputs import ICrawlerService, IStorageService, IPdfService
    
    class CrawlAndExportBookUseCase(IBookUseCase):
        def __init__(self, crawler: ICrawlerService, storage: IStorageService, pdf_gen: IPdfService):
            self.crawler = crawler
            self.storage = storage
            self.pdf_gen = pdf_gen
    
        async def _download_task(self, session, slide, folder_name):
            img_bytes = await self.crawler.download_image(session, slide.url)
            return self.storage.write_file(folder_name, slide.file_name, img_bytes)
    
        async def run(self, url: str, concurrency: int) -> str:
            # 1. Gọi cổng Crawler lấy thông tin thô
            book = self.crawler.fetch_metadata(url)
            
            # 2. Xử lý tải ảnh bất đồng bộ qua cổng lưu trữ
            connector = aiohttp.TCPConnector(limit_per_host=concurrency)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [self._download_task(session, s, book.safe_title) for s in book.slides]
                image_paths = await asyncio.gather(*tasks)
    
            # 3. Gọi cổng đóng gói PDF
            pdf_path = f"output/{book.safe_title}/{book.safe_title}.pdf"
            self.pdf_gen.create_pdf(image_paths, pdf_path)
            return pdf_path
    

## 4\. Tầng Adapters (`adapters/`)

  * Driven Adapters (`adapters/driven/`): Triển khai chi tiết mã nguồn hạ tầng.


    
    
    # adapters/driven/ss_crawler.py
    import requests
    from bs4 import BeautifulSoup
    from ports.outputs import ICrawlerService
    from domain.models import Book, Slide
    
    class SlideShareCrawlerAdapter(ICrawlerService):
        def fetch_metadata(self, url: str) -> Book:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, 'html.parser')
            title_tag = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
            title = title_tag.text.strip() if title_tag else "Untitled"
    
            slides = []
            index = 1
            for img in soup.find_all('img'):
                src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if src and "slide-" in src:
                    clean_url = src.split('?')
                    if clean_url not in [s.url for s in slides]:
                        slides.append(Slide(index=index, url=clean_url))
                        index += 1
            return Book(title=title, source_url=url, slides=slides)
    
        async def download_image(self, session, url: str) -> bytes:
            async with session.get(url) as response:
                return await response.read()
    
    # adapters/driven/local_storage.py
    import os
    from ports.outputs import IStorageService
    
    class LocalStorageAdapter(IStorageService):
        def write_file(self, folder_name: str, file_name: str, data: bytes) -> str:
            path = os.path.join("output", folder_name)
            os.makedirs(path, exist_ok=True)
            file_path = os.path.join(path, file_name)
            with open(file_path, "wb") as f:
                f.write(data)
            return file_path
    
    # adapters/driven/fitz_generator.py
    import fitz
    from ports.outputs import IPdfService
    
    class FitzPdfAdapter(IPdfService):
        def create_pdf(self, img_paths: list, output_path: str) -> None:
            doc = fitz.open()
            for path in img_paths:
                img = fitz.open(path)
                doc.insert_pdf(fitz.open("pdf", img.convert_to_pdf()))
                img.close()
            doc.save(output_path)
            doc.close()
    

  * Driving Adapters (`adapters/driving/cli_command.py`): Điểm tiếp nhận tương tác người dùng.


    
    
    # adapters/driving/cli_command.py
    import click
    import asyncio
    from ports.inputs import IBookUseCase
    
    class CliDrivingAdapter:
        def __init__(self, use_case: IBookUseCase):
            self.use_case = use_case
    
        def create_command(self):
            @click.command()
            @click.argument('url', type=str)
            @click.option('--workers', '-w', default=5)
            def _cmd(url, workers):
                """Lệnh CLI chạy cào sách chuẩn kiến trúc lục giác Hexagonal."""
                try:
                    path = asyncio.run(self.use_case.run(url, workers))
                    click.secho(f"[🎉] XUẤT PDF LỤC GIÁC THÀNH CÔNG: {path}", fg="green", bold=True)
                except Exception as e:
                    click.secho(f"[❌] LỖI: {e}", fg="red")
            return _cmd
    

* * *

## 🚀 Điểm ráp nối hạ tầng (`main.py`)

File `main.py` nằm ở vùng rìa hệ thống, khởi tạo các Adapter công nghệ cụ thể và gắn chúng qua các cổng Port vào khối Lục giác Core.
    
    
    # main.py
    from domain.use_cases import CrawlAndExportBookUseCase
    from adapters.driven.ss_crawler import SlideShareCrawlerAdapter
    from adapters.driven.local_storage import LocalStorageAdapter
    from adapters.driven.fitz_generator import FitzPdfAdapter
    from adapters.driving.cli_command import CliDrivingAdapter
    
    if __name__ == "__main__":
        # 1. Tạo các bộ gá lắp công nghệ bên ngoài (Driven Adapters)
        crawler_tech = SlideShareCrawlerAdapter()
        storage_tech = LocalStorageAdapter()
        pdf_tech = FitzPdfAdapter()
    
        # 2. Tạo khối Logic Core bên trong và tiêm công nghệ vào các cổng Port tương ứng
        core_use_case = CrawlAndExportBookUseCase(
            crawler=crawler_tech,
            storage=storage_tech,
            pdf_gen=pdf_tech
        )
    
        # 3. Kết nối bộ điều khiển giao diện (Driving Adapter) để tiếp nhận lệnh
        cli_app = CliDrivingAdapter(use_case=core_use_case)
        
        # 4. Kích hoạt ứng dụng
        cmd = cli_app.create_command()
        cmd()
    

* * *

## ⚖️ Điểm khác biệt cốt lõi: Hexagonal vs. Clean Architecture

Rất nhiều người thường nhầm lẫn giữa hai mô hình này vì chúng đều hướng tới sự cô lập Domain. Tuy nhiên:

  * Hexagonal Architecture: Định nghĩa kiến trúc theo ranh giới "Inside vs Outside" (Bên trong và Bên ngoài) kết hợp với các khái niệm "Cổng & Bộ chuyển đổi (Ports & Adapters)". Nó không quan tâm bên trong Domain chia thành bao nhiêu lớp hay bao nhiêu vòng tròn nhỏ, miễn là giao tiếp ra bên ngoài phải tuân thủ nghiêm ngặt qua Interface Port.
  * Clean/Onion Architecture: Tiến thêm một bước xa hơn. Nó kế thừa tư tưởng Ports & Adapters của Hexagonal nhưng ép buộc phần "Inside" phải phân chia tầng nghiêm ngặt thành các vòng tròn đồng tâm, ví dụ: bắt buộc tách biệt rõ rệt lớp `Entities` nằm trong cùng rồi mới đến lớp `Use Cases`.



Chúng ta đã bao quát toàn bộ bức tranh kiến trúc từ MVC, MVT, Microservices, Event-Driven cho đến các kiến trúc hướng Domain nâng cao như Clean, Onion, và Hexagonal. Bạn có muốn chuyển sang phần tiếp theo về Các mô hình xử lý dữ liệu hiện đại trong Python (như Pydantic Models hay `@dataclass`) không?