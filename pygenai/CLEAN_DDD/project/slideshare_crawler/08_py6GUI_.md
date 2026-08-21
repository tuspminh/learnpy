> Tôi muốn chuyển thành app pyside6 có thanh tìm kiếm, tìm book và hiển thị hành các card cho mỗi book. mới vào app chưa tìm kiếm thì crawl các book trên base slideshare và hiển thị. mỗi card có nút download , export pdf, export zip
>

Để chuyển ứng dụng sang giao diện đồ họa **PySide6** giữ nguyên chuẩn **Clean Architecture & DDD**, hệ thống được tổ chức như sau:

* **Domain & Application**: Giữ nguyên nghiệp vụ lõi (Book, Slide, Scraper interfaces, Use Cases).
* **Infrastructure**: Nâng cấp `SlideShareScraper` để hỗ trợ cào danh sách trang chủ/trending và tìm kiếm sách theo từ khóa.
* **Presentation (PySide6)**: Xây dựng GUI gồm `MainWindow`, `BookCardWidget`, và sử dụng `QThread` (WorkThread) để chạy các tác vụ cào dữ liệu/tải file chạy ngầm không gây đóng băng (freeze) giao diện.

---

### Structure & Clean Architecture

```text
├── domain/
│   ├── models.py
│   └── interfaces.py
├── infrastructure/
│   ├── scraper.py
│   ├── storage.py
│   ├── pdf_exporter.py
│   └── zip_exporter.py
├── application/
│   └── use_cases.py
├── presentation/
│   ├── workers.py       # QThread Workers
│   ├── components.py    # BookCardWidget, SearchBar
│   └── main_window.py   # PySide6 MainWindow
└── main.py

```

---

### Code Hiện Thực

#### 1. Domain Layer (`domain/`)

```python
# domain/models.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class Slide:
    page_number: int
    image_url: str

class Book:
    def __init__(self, title: str, source_url: str, thumbnail_url: str = "", slides: Optional[List[Slide]] = None):
        self.title = self._sanitize_title(title)
        self.source_url = source_url
        self.thumbnail_url = thumbnail_url
        self.slides = slides or []

    def add_slide(self, slide: Slide) -> None:
        self.slides.append(slide)

    @staticmethod
    def _sanitize_title(title: str) -> str:
        return "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip() or "slideshare_book"

```

```python
# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from domain.models import Book, Slide

class ICrawler(ABC):
    @abstractmethod
    def fetch_base_books((self) -> List[Book]:
        pass

    @abstractmethod
    def search_books(self, query: str) -> List[Book]:
        pass

    @abstractmethod
    def fetch_book_details(self, book: Book) -> Book:
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

#### 2. Infrastructure Layer (`infrastructure/`)

```python
# infrastructure/scraper.py
import requests
from bs4 import BeautifulSoup
import re
from typing import List
from domain.models import Book, Slide
from domain.interfaces import ICrawler

class SlideShareScraper(ICrawler):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_base_books(self) -> List[Book]:
        url = "https://www.slideshare.net/explore"
        return self._scrape_book_list(url)

    def search_books(self, query: str) -> List[Book]:
        url = f"https://www.slideshare.net/search?q={requests.utils.quote(query)}"
        return self._scrape_book_list(url)

    def _scrape_book_list(self, url: str) -> List[Book]:
        books = []
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Quét các thẻ card hoặc link chứa slideshow
            cards = soup.select("a[data-cy='slideshow-card'], a.SearchResultCard, div.slideshow-card")
            if not cards:
                cards = soup.find_all("a", href=re.compile(r"/slideshow/"))

            seen_urls = set()
            for card in cards:
                href = card.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://www.slideshare.net{href}"

                if href and href not in seen_urls and "/slideshow/" in href:
                    seen_urls.add(href)
                    
                    # Lấy tiêu đề
                    title_elem = card.find("h3") or card.find("span") or card
                    title = title_elem.get_text(strip=True) if title_elem else "SlideShare Book"
                    
                    # Lấy thumbnail
                    img_elem = card.find("img")
                    thumb_url = ""
                    if img_elem:
                        thumb_url = img_elem.get("src") or img_elem.get("srcset", "").split(" ")[0]

                    books.append(Book(title=title, source_url=href, thumbnail_url=thumb_url))
                    if len(books) >= 12:  # Giới hạn 12 kết quả
                        break
        except Exception as e:
            print(f"[Scraper Error] {e}")
        return books

    def fetch_book_details(self, book: Book) -> Book:
        res = requests.get(book.source_url, headers=self.headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

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

    def download_image(self, image_url: str) -> bytes:
        res = requests.get(image_url, headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.content

```

*(Các file `storage.py`, `pdf_exporter.py`, `zip_exporter.py` giữ nguyên như các bước trước)*

---

#### 3. Application Layer (`application/use_cases.py`)

```python
# application/use_cases.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Optional
from domain.models import Book
from domain.interfaces import ICrawler, IStorage, IPdfExporter, IZipExporter

class GetBooksUseCase:
    def __init__(self, crawler: ICrawler):
        self.crawler = crawler

    def get_base_books(self) -> List[Book]:
        return self.crawler.fetch_base_books()

    def search_books(self, query: str) -> List[Book]:
        return self.crawler.search_books(query)

class DownloadAndExportBookUseCase:
    def __init__(
        self, 
        crawler: ICrawler, 
        storage: IStorage, 
        pdf_exporter: IPdfExporter, 
        zip_exporter: IZipExporter,
        max_workers: int = 8
    ):
        self.crawler = crawler
        self.storage = storage
        self.pdf_exporter = pdf_exporter
        self.zip_exporter = zip_exporter
        self.max_workers = max_workers

    def execute(self, book: Book, action: str, progress_callback: Optional[Callable[[str], None]] = None) -> str:
        if progress_callback: progress_callback("Đang lấy chi tiết slide...")
        
        # 1. Fetch details nếu chưa có slides
        if not book.slides:
            book = self.crawler.fetch_book_details(book)

        total = len(book.slides)
        if total == 0:
            raise ValueError("Không tìm thấy trang slide nào.")

        if progress_callback: progress_callback(f"Đang tải {total} trang ảnh...")

        # 2. Tải đa luồng
        saved_images_map = {}
        def _download_task(slide):
            img_bytes = self.crawler.download_image(slide.image_url)
            saved_path = self.storage.save_slide(book.title, slide, img_bytes)
            return slide.page_number, saved_path

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_download_task, s) for s in book.slides]
            for future in as_completed(futures):
                p_num, path = future.result()
                saved_images_map[p_num] = path

        image_paths = [saved_images_map[p] for p in sorted(saved_images_map.keys())]

        # 3. Xử lý Action
        output_result = f"output/{book.title}"
        
        if action == "pdf" or action == "zip":
            pdf_path = f"output/{book.title}/{book.title}.pdf"
            if progress_callback: progress_callback("Đang tạo file PDF...")
            self.pdf_exporter.export_to_pdf(image_paths, pdf_path)
            output_result = pdf_path

            if action == "zip":
                zip_path = f"output/{book.title}/{book.title}.zip"
                if progress_callback: progress_callback("Đang nén file ZIP...")
                self.zip_exporter.export_to_zip(image_paths + [pdf_path], zip_path)
                output_result = zip_path

        if progress_callback: progress_callback("Hoàn tất!")
        return output_result

```

---

#### 4. Presentation Layer (`presentation/`)

```python
# presentation/workers.py
from PySide6.QtCore import QThread, Signal
from domain.models import Book

class FetchBooksWorker(QThread):
    books_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, use_case, query: str = ""):
        super().__init__()
        self.use_case = use_case
        self.query = query

    def run(self):
        try:
            if self.query.strip():
                books = self.use_case.search_books(self.query)
            else:
                books = self.use_case.get_base_books()
            self.books_loaded.emit(books)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ProcessBookWorker(QThread):
    progress = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, use_case, book: Book, action: str):
        super().__init__()
        self.use_case = use_case
        self.book = book
        self.action = action

    def run(self):
        try:
            res = self.use_case.execute(self.book, self.action, lambda msg: self.progress.emit(msg))
            self.finished.emit(res)
        except Exception as e:
            self.error.emit(str(e))

```

```python
# presentation/components.py
import requests
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal
from domain.models import Book

class ImageLoaderThread(QThread):
    loaded = Signal(bytes)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            if self.url:
                res = requests.get(self.url, timeout=5)
                self.loaded.emit(res.content)
        except Exception:
            pass

class BookCardWidget(QFrame):
    def __init__(self, book: Book, process_callback):
        super().__init__()
        self.book = book
        self.process_callback = process_callback
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton:disabled { background-color: #555; }
        """)

        layout = QVBoxLayout(self)

        # Thumbnail Image
        self.img_label = QLabel("Loading Image...")
        self.img_label.setFixedHeight(140)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
        layout.addWidget(self.img_label)

        # Title
        title_label = QLabel(self.book.title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 5px;")
        layout.addWidget(title_label)

        # Status / Progress Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_download = QPushButton("Tải ảnh")
        self.btn_pdf = QPushButton("PDF")
        self.btn_zip = QPushButton("ZIP")

        self.btn_download.clicked.connect(lambda: self.process_callback(self.book, "download", self))
        self.btn_pdf.clicked.connect(lambda: self.process_callback(self.book, "pdf", self))
        self.btn_zip.clicked.connect(lambda: self.process_callback(self.book, "zip", self))

        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_zip)
        layout.addLayout(btn_layout)

        # Async Load Thumbnail
        if self.book.thumbnail_url:
            self.img_thread = ImageLoaderThread(self.book.thumbnail_url)
            self.img_thread.loaded.connect(self._set_thumbnail)
            self.img_thread.start()

    def _set_thumbnail(self, data):
        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap.fromImage(image)
        self.img_label.setPixmap(pixmap.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def set_loading(self, is_loading: bool, message: str = ""):
        self.btn_download.setEnabled(not is_loading)
        self.btn_pdf.setEnabled(not is_loading)
        self.btn_zip.setEnabled(not is_loading)
        self.status_label.setText(message)

```

```python
# presentation/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QScrollArea, QGridLayout, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from presentation.components import BookCardWidget
from presentation.workers import FetchBooksWorker, ProcessBookWorker

class MainWindow(QMainWindow):
    def __init__(self, get_books_uc, process_book_uc):
        super().__init__()
        self.get_books_uc = get_books_uc
        self.process_book_uc = process_book_uc

        self.setWindowTitle("SlideShare Downloader - Clean Architecture")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        self.init_ui()
        self.load_books("")  # Crawl trang chủ khi mới mở App

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Search Bar Header
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm sách trên SlideShare...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                color: white;
                font-size: 14px;
            }
        """)
        self.search_input.returnPressed.connect(self.on_search)

        search_btn = QPushButton("Tìm kiếm")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        search_btn.clicked.connect(self.on_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)

        # 2. Loading / Status Label
        self.loading_label = QLabel("Đang tải danh sách sách ban đầu...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.loading_label)

        # 3. Grid View Trong ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.scroll_area.setWidget(self.grid_container)
        
        main_layout.addWidget(self.scroll_area)

    def on_search(self):
        query = self.search_input.text().strip()
        self.load_books(query)

    def load_books(self, query: str):
        self.loading_label.setText("Đang cào dữ liệu từ SlideShare..." if not query else f"Đang tìm kiếm '{query}'...")
        self.loading_label.show()

        # Clear cũ
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        # Chạy worker tìm kiếm ngầm
        self.fetch_worker = FetchBooksWorker(self.get_books_uc, query)
        self.fetch_worker.books_loaded.connect(self.display_books)
        self.fetch_worker.error_occurred.connect(self.show_error)
        self.fetch_worker.start()

    def display_books(self, books):
        self.loading_label.hide()
        if not books:
            self.loading_label.setText("Không tìm thấy cuốn sách nào.")
            self.loading_label.show()
            return

        cols = 3  # Hiển thị 3 card mỗi hàng
        for idx, book in enumerate(books):
            card = BookCardWidget(book, self.handle_book_action)
            row, col = divmod(idx, cols)
            self.grid_layout.addWidget(card, row, col)

    def handle_book_action(self, book, action: str, card_widget: BookCardWidget):
        card_widget.set_loading(True, "Đang khởi tạo...")

        worker = ProcessBookWorker(self.process_book_uc, book, action)
        worker.progress.connect(lambda msg: card_widget.set_loading(True, msg))
        worker.finished.connect(lambda path: self.on_process_finished(card_widget, path))
        worker.error.connect(lambda err: self.on_process_error(card_widget, err))
        
        # Giữ reference worker
        card_widget.worker = worker
        worker.start()

    def on_process_finished(self, card_widget, path):
        card_widget.set_loading(False, "Hoàn tất!")
        QMessageBox.information(self, "Thành công", f"Đã xuất thành công tại:\n{path}")

    def on_process_error(self, card_widget, err):
        card_widget.set_loading(False, "Lỗi!")
        QMessageBox.critical(self, "Lỗi", f"Thất bại: {err}")

    def show_error(self, err_msg):
        self.loading_label.setText(f"Lỗi: {err_msg}")

```

---

#### 5. Main Entry Point (`main.py`)

Cấu hình **Dependency Injection** và kích hoạt GUI:

```python
# main.py
import sys
from PySide6.QtWidgets import QApplication

from infrastructure.scraper import SlideShareScraper
from infrastructure.storage import LocalDiskStorage
from infrastructure.pdf_exporter import PillowPdfExporter
from infrastructure.zip_exporter import ZipArchiver

from application.use_cases import GetBooksUseCase, DownloadAndExportBookUseCase
from presentation.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # 1. Instantiation Infrastructure
    crawler = SlideShareScraper()
    storage = LocalDiskStorage(base_output_dir="output")
    pdf_exporter = PillowPdfExporter()
    zip_exporter = ZipArchiver()

    # 2. Instantiation Use Cases
    get_books_uc = GetBooksUseCase(crawler=crawler)
    process_book_uc = DownloadAndExportBookUseCase(
        crawler=crawler,
        storage=storage,
        pdf_exporter=pdf_exporter,
        zip_exporter=zip_exporter,
        max_workers=8
    )

    # 3. Launch Presentation GUI
    window = MainWindow(get_books_uc, process_book_uc)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

```

---

### Cài đặt dependencies và chạy app

```bash
pip install PySide6 requests beautifulsoup4 Pillow
python main.py

```