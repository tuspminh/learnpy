Dưới đây là thiết kế chi tiết cho ứng dụng Crawl Book từ SlideShare theo đúng mô hình kiến trúc MVC (Model-View-Controller).

Trong mô hình này, Model sẽ quản lý dữ liệu cuốn sách và các tác vụ nghiệp vụ (cào, tải ảnh, gộp PDF), View chịu trách nhiệm hiển thị giao diện dòng lệnh (CLI bằng thư viện `click`), và Controller đóng vai trò điều phối, nhận lệnh từ View để điều khiển Model xử lý.

* * *

## 📂 Cấu trúc thư mục (Folder Tree) theo mô hình MVC
    
    
    slideshare_crawler_mvc/
    │
    ├── models/                      # M (Model): Quản lý dữ liệu, logic cào & export
    │   ├── __init__.py
    │   ├── book_model.py            # Định nghĩa thực thể dữ liệu Book và Slide
    │   ├── crawler_service.py       # Logic tải ảnh bất đồng bộ (Asyncio/Aiohttp)
    │   └── pdf_service.py           # Logic xuất file PDF bằng PyMuPDF (fitz)
    │
    ├── views/                       # V (View): Giao diện tương tác (CLI bằng Click)
    │   ├── __init__.py
    │   └── cli_view.py              # Định nghĩa các hàm hiển thị thông báo, nhận URL
    │
    ├── controllers/                 # C (Controller): Bộ não điều phối hệ thống
    │   ├── __init__.py
    │   └── crawler_controller.py    # Nhận lệnh từ View -> Gọi Model xử lý -> Trả kết quả về View
    │
    ├── output/                      # Thư mục lưu kết quả đầu ra (Tự động sinh ra)
    │   └── [book-name]/
    │
    └── main.py                      # Điểm khởi chạy ứng dụng (Khởi tạo Controller gốc)
    

* * *

## 💻 Mã nguồn chi tiết theo các thành phần MVC

## 1\. Tầng Models (Xử lý dữ liệu & Nghiệp vụ cốt lõi)

  * `models/book_model.py` (Định nghĩa thực thể dữ liệu)


    
    
    # models/book_model.py
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
            """Chuẩn hóa tiêu đề thành tên thư mục hợp lệ trên hệ điều hành"""
            return re.sub(r'[\\/*?:"<>| ]', '_', self.title).strip('_')
    

  * `models/crawler_service.py` (Dịch vụ cào dữ liệu và tải ảnh bất đồng bộ)


    
    
    # models/crawler_service.py
    import re
    import os
    import requests
    import aiohttp
    from bs4 import BeautifulSoup
    from models.book_model import Book, Slide
    
    class CrawlerService:
        def fetch_book_info(self, url: str) -> Book:
            """Cào thông tin tiêu đề và danh sách link slide (Đồng bộ)"""
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"Không thể truy cập SlideShare (Mã lỗi: {response.status_code})")
    
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm tiêu đề
            title_element = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
            title = title_element.text.strip() if title_element else "Untitled_Book"
            
            # Tìm danh sách URL hình ảnh slides
            slides = []
            index = 1
            for img in soup.find_all('img'):
                src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if src and "slide-" in src:
                    clean_url = src.split('?')[0]
                    if clean_url not in [s.url for s in slides]:
                        slides.append(Slide(index=index, url=clean_url))
                        index += 1
    
            if not slides:
                raise ValueError("Không tìm thấy bất kỳ trang slide nào từ đường dẫn này.")
                
            return Book(title=title, source_url=url, slides=slides)
    
        async def download_single_slide(self, session: aiohttp.ClientSession, slide: Slide, base_dir: str, book_title: str) -> str:
            """Tải một trang slide đơn lẻ (Bất đồng bộ)"""
            target_dir = os.path.join(base_dir, book_title)
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, slide.file_name)
    
            async with session.get(slide.url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Lỗi tải slide {slide.index} (Mã lỗi: {response.status})")
                content = await response.read()
    
            with open(file_path, "wb") as f:
                f.write(content)
            return file_path
    

  * `models/pdf_service.py` (Dịch vụ xuất file PDF bằng PyMuPDF - Fitz)


    
    
    # models/pdf_service.py
    import fitz  # Thư viện PyMuPDF
    import os
    
    class PdfService:
        @staticmethod
        def export_images_to_pdf(image_paths: list, output_dir: str, book_title: str) -> str:
            """Gộp các file ảnh slide thành một file PDF"""
            pdf_path = os.path.join(output_dir, book_title, f"{book_title}.pdf")
            
            doc = fitz.open()  # Khởi tạo một file PDF trống
            for img_path in image_paths:
                img_doc = fitz.open(img_path)
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
                
                page_doc = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(page_doc)
                page_doc.close()
                
            doc.save(pdf_path)
            doc.close()
            return pdf_path
    

## 2\. Tầng Views (Giao diện hiển thị cho người dùng)

View chịu trách nhiệm giao tiếp (I/O) với người dùng qua console. Ở đây chúng ta bọc View bằng cấu trúc lệnh của thư viện `click`.
    
    
    # views/cli_view.py
    import click
    
    class CliView:
        @staticmethod
        def show_message(message: str, fg_color: str = None, bold_text: bool = False):
            """In thông báo thông thường ra terminal"""
            click.secho(message, fg=fg_color, bold=bold_text)
    
        @staticmethod
        def show_progress(current: int, total: int):
            """In tiến trình tải (Nếu cần hiển thị chi tiết)"""
            click.echo(f" -> Đang xử lý: {current}/{total}...",  err=True)
    
        @staticmethod
        def show_success(pdf_path: str):
            """In thông báo thành công rực rỡ"""
            click.echo("")
            click.secho(f"[🎉] HOÀN THÀNH XUẤT FILE PDF THÀNH CÔNG!", fg="cyan", bold=True)
            click.secho(f" 👉 Đường dẫn file: {pdf_path}", fg="yellow")
    
        @staticmethod
        def show_error(error_msg: str):
            """In lỗi khi hệ thống gặp sự cố"""
            click.secho(f"\n[❌] LỖI HỆ THỐNG: {error_msg}", fg="red", bold=True)
    

## 3\. Tầng Controllers (Bộ điều phối trung gian)

Controller giữ tham chiếu tới cả Model và View. Nó tiếp nhận sự kiện, ra lệnh cho Model thực hiện rồi gửi trả kết quả để View hiển thị.
    
    
    # controllers/crawler_controller.py
    import asyncio
    import aiohttp
    from models.crawler_service import CrawlerService
    from models.pdf_service import PdfService
    from views.cli_view import CliView
    
    class CrawlerController:
        def __init__(self):
            # Controller quản lý trực tiếp các thành phần Model và View
            self.crawler_service = CrawlerService()
            self.pdf_service = PdfService()
            self.view = CliView()
    
        async def _download_all_slides(self, book, max_connections: int, output_dir: str) -> list:
            """Luồng điều phối tải ảnh bất đồng bộ"""
            connector = aiohttp.TCPConnector(limit_per_host=max_connections)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for slide in book.slides:
                    task = self.crawler_service.download_single_slide(
                        session, slide, output_dir, book.safe_title
                    )
                    tasks.append(asyncio.create_task(task))
                
                # Chạy song song và gom tất cả đường dẫn ảnh về
                return await asyncio.gather(*tasks)
    
        def start_crawl_process(self, url: str, connections: int, output_dir: str):
            """Hàm điều phối luồng chạy chính từ đầu đến cuối"""
            try:
                self.view.show_message(f"[*] Bắt đầu cào dữ liệu từ URL: {url}", fg_color="blue")
                
                # 1. Gọi Model lấy thông tin sách
                book = self.crawler_service.fetch_book_info(url)
                self.view.show_message(f"[+] Tìm thấy sách: '{book.title}' với {len(book.slides)} slides.", fg_color="green")
                
                # 2. Gọi Model tải ảnh bất đồng bộ thông qua asyncio loop
                self.view.show_message("[*] Đang tải các trang slide bất đồng bộ...", fg_color="blue")
                image_paths = asyncio.run(self._download_all_slides(book, connections, output_dir))
                self.view.show_message("[+] Đã tải xuống và lưu tất cả ảnh slide thành công.", fg_color="green")
                
                # 3. Gọi Model đóng gói file PDF bằng Fitz
                self.view.show_message("[*] Đang tiến hành xuất file PDF (PyMuPDF - Fitz)...", fg_color="blue")
                pdf_result_path = self.pdf_service.export_images_to_pdf(image_paths, output_dir, book.safe_title)
                
                # 4. Báo cho View cập nhật giao diện thành công tới người dùng
                self.view.show_success(pdf_path=pdf_result_path)
    
            except Exception as e:
                # Nếu có lỗi ở bất kỳ bước nào trong Model, Controller bắt lại và đưa sang View hiển thị
                self.view.show_error(str(e))
    

* * *

## 🚀 Cổng kích hoạt ứng dụng (`main.py`)

File `main.py` ở lớp ngoài cùng định nghĩa cấu trúc lệnh `click`, nhận tham số gõ từ bàn phím và đẩy thẳng vào cho Controller xử lý.
    
    
    # main.py
    import click
    from controllers.crawler_controller import CrawlerController
    
    @click.command()
    @click.argument('url', type=str)
    @click.option('--connections', '-c', default=5, help='Số luồng tải ảnh song song tối đa (Mặc định: 5)')
    @click.option('--output-dir', '-o', default='output', help='Thư mục chứa sách đầu ra (Mặc định: output)')
    def run_app(url, connections, output_dir):
        """Ứng dụng cào sách SlideShare và xuất PDF viết theo mô hình kiến trúc MVC kinh điển."""
        # Khởi tạo Controller nghiệp vụ
        controller = CrawlerController()
        
        # Kích hoạt luồng xử lý
        controller.start_crawl_process(url=url, connections=connections, output_dir=output_dir)
    
    if __name__ == "__main__":
        run_app()
    

* * *

## 💡 Đặc điểm của mã nguồn theo chuẩn kiến trúc MVC:

  * Controller làm chủ cuộc chơi: Không giống như Clean hay Onion Architecture nơi các lớp giao tiếp qua giao diện trừu tượng (Interface/Ports), trong mô hình MVC truyền thống, Controller import và điều phối trực tiếp các Service của Model và hàm static của View.
  * Tách biệt hiển thị (Separation of View): File `crawler_service.py` và `pdf_service.py` hoàn toàn sạch bóng các lệnh in ấn (`print` hoặc `click.echo`). Toàn bộ việc vẽ màu, thông báo lỗi, thông báo thành công đều dồn hết cho `CliView` đảm nhận.
  * Giao thức đồng bộ kết hợp bất đồng bộ: Bản thân Controller chạy luồng điều phối đồng bộ để dễ quản lý thứ tự các bước (Cào thông tin -> Tải ảnh -> Gộp PDF), nhưng tại bước tải ảnh, nó mở một phân vùng `asyncio.run` để tối ưu hóa hiệu năng mạng của Model.



Để hoàn thiện toàn bộ cẩm nang kiến trúc phần mềm, bạn có muốn tìm hiểu nốt về các Design Patterns (Creational, Structural, Behavioral) cụ thể thường áp dụng bên trong các lớp Model này (như áp dụng _Singleton_ cho bộ quản lý cấu hình, hoặc _Factory_ để sinh ra các loại Crawler khác nhau) không?