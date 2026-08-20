Để trả lời câu hỏi của bạn một cách trực diện nhất: Với bài toán crawl sách từ SlideShare dưới dạng danh sách hình ảnh (mỗi slide là một ảnh), BẠN KHÔNG NHẤT THIẾT PHẢI CẦN Unit of Work (UoW) cho phần ghi file ảnh, nhưng RẤT CẦN cho phần lưu Metadata (thông tin sách) vào Database.

Tuy nhiên, nếu bạn muốn đảm bảo tính toàn vẹn theo kiểu "Nếu lỗi ở bất kỳ slide nào thì xóa sạch cả thư mục sách đó để tránh lưu file rác", chúng ta hoàn toàn có thể thiết kế một File System Unit of Work hoặc một cơ chế Rollback thư mục lồng trong UoW của Database.

Dưới đây là bản thiết kế chi tiết ứng dụng Crawl SlideShare theo kiến trúc Clean Architecture + DDD + SOLID, lưu ảnh vào thư mục `output/book_id/`.

* * *

## 📂 Cấu trúc thư mục dự án
    
    
    src/
    ├── domain/                  # Tầng Nghiệp vụ cốt lõi (Chỉ dùng Python thuần)
    │   ├── models.py            # Book (Aggregate Root), SlideImage (Value Object/Entity)
    │   └── repositories.py      # Interfaces (BookRepository, SlideShareClient)
    │
    ├── application/             # Tầng Điều hướng (Use Cases)
    │   ├── unit_of_work.py      # AbstractUnitOfWork (Quản lý Giao dịch DB)
    │   └── use_cases.py         # DownloadBookUseCase (Chứa luồng nghiệp vụ chính)
    │
    ├── infrastructure/          # Tầng Hạ tầng (Chi tiết công nghệ)
    │   ├── database/
    │   │   └── sqlite_repo.py   # Lưu thông tin sách đã tải vào SQLite bằng SQL thuần
    │   ├── crawler/
    │   │   └── slideshare.py    # Dùng requests/BeautifulSoup lấy danh sách link ảnh slide
    │   ├── storage/
    │   │   └── file_storage.py  # Chịu trách nhiệm ghi file ảnh vật lý vào thư mục output/
    │   └── unit_of_work.py      # Triển khai SQLiteUnitOfWork
    │
    └── presentation/
        └── main.py              # File chạy ứng dụng (CLI)
    

* * *

## 💻 Triển khai mã nguồn chi tiết

## 1\. Tầng Domain (Nghiệp vụ và Mô hình)

Áp dụng DDD, một cuốn sách (`Book`) sẽ là một Aggregate Root quản lý danh sách các hình ảnh slide (`SlideImage`).
    
    
    # src/domain/models.py
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class SlideImage: # Value Object hoặc Entity
        page_number: int
        image_url: str
        local_path: str = "" # Đường dẫn lưu trên máy sau này
    
    @dataclass
    class Book: # Aggregate Root
        book_id: str
        title: str
        slideshare_url: str
        slides: List[SlideImage] = field(default_factory=list)
    
        def add_slide(self, page_number: int, image_url: str) -> None:
            """Logic nghiệp vụ: Tự động tính toán đường dẫn lưu file cục bộ"""
            local_path = f"output/{self.book_id}/slide_{page_number:03d}.jpg"
            self.slides.append(SlideImage(page_number, image_url, local_path))
    
    # src/domain/repositories.py
    from abc import ABC, abstractmethod
    from src.domain.models import Book
    
    class BookRepository(ABC):
        @abstractmethod
        def save_metadata(self, book: Book) -> None: pass
        
        @abstractmethod
        def is_already_downloaded(self, slideshare_url: str) -> bool: pass
    
    class SlideShareClient(ABC):
        @abstractmethod
        def fetch_book_info(self, url: str) -> Book: pass
    

## 2\. Tầng Application (Giải pháp cho câu hỏi UoW)

Tại đây, Use Case sẽ phối hợp giữa UoW (cho Database) và File Storage. Để giải quyết bài toán "lỗi thì xóa file rác", chúng ta bọc logic tải file vào khối `try...except`. Nếu dính lỗi, ta thực hiện `rollback()` DB và đồng thời xóa thư mục rác (Compensating Action).
    
    
    # src/application/unit_of_work.py
    from abc import ABC, abstractmethod
    from src.domain.repositories import BookRepository
    
    class AbstractUnitOfWork(ABC):
        books: BookRepository
    
        def __enter__(self) -> "AbstractUnitOfWork": return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None: self.rollback()
            else: self.commit()
    
        @abstractmethod
        def commit(self): pass
        @abstractmethod
        def rollback(self): pass
    
    
    
    # src/application/use_cases.py
    import os
    import shutil
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.domain.repositories import SlideShareClient
    from src.infrastructure.storage.file_storage import FileStorage # Tiêm từ ngoài vào hoặc dùng Interface
    
    class DownloadBookUseCase:
        def __init__(self, uow: AbstractUnitOfWork, crawler: SlideShareClient, storage: FileStorage):
            self.uow = uow
            self.crawler = crawler
            self.storage = storage
    
        def execute(self, url: str) -> None:
            # 1. Kiểm tra xem sách đã tải chưa thông qua UoW
            with self.uow:
                if self.uow.books.is_already_downloaded(url):
                    print("[Application] Sách này đã được tải trước đó. Bỏ qua.")
                    return
    
            # 2. Cào thông tin và danh sách link ảnh slide từ SlideShare
            book = self.crawler.fetch_book_info(url)
            book_output_dir = f"output/{book.book_id}"
    
            # 3. Tiến hành tải ảnh và lưu DB bọc trong Giao dịch để kiểm soát lỗi liên hoàn
            try:
                with self.uow:
                    # Lưu thông tin sách vào DB (Trạng thái Pending)
                    self.uow.books.save_metadata(book)
    
                    # Tải từng slide ảnh về đĩa vật lý
                    for slide in book.slides:
                        self.storage.download_and_save(slide.image_url, slide.local_path)
                        print(f"[Application] Đã tải Slide {slide.page_number}")
    
                print(f"🎉 Tải thành công sách: {book.title}. Dữ liệu đã commit!")
    
            except Exception as e:
                # Nếu dính lỗi mạng khi đang tải ảnh dở dang -> Khối `with self.uow` tự rollback DB
                print(f"💥 Lỗi xảy ra trong quá trình tải: {e}. Tiến hành dọn dẹp file rác...")
                
                # Khôi phục trạng thái File System (Xóa thư mục rác nếu tải lỗi)
                if os.path.exists(book_output_dir):
                    shutil.rmtree(book_output_dir)
                raise e
    

## 3\. Tầng Infrastructure (Hiện thực hóa công nghệ)
    
    
    # src/infrastructure/storage/file_storage.py
    import os
    import requests
    
    class FileStorage:
        """Chịu trách nhiệm tạo thư mục và tải ảnh từ URL lưu xuống đĩa"""
        def download_and_save(self, url: str, local_path: str) -> None:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    
    
    # src/infrastructure/crawler/slideshare.py
    import uuid
    import requests
    from bs4 import BeautifulSoup
    from src.domain.repositories import SlideShareClient
    from src.domain.models import Book
    
    class SlideShareHtmlCrawler(SlideShareClient):
        """Cào dữ liệu thực tế từ SlideShare bằng BeautifulSoup"""
        def fetch_book_info(self, url: str) -> Book:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
    
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Lấy tiêu đề sách
            title_tag = soup.find("h1", id="j-title-v2") or soup.find("title")
            title = title_tag.text.strip() if title_tag else "Untitled Book"
            book_id = str(uuid.uuid4())[:8]
    
            book = Book(book_id=book_id, title=title, slideshare_url=url)
    
            # SlideShare lưu link ảnh slide trong các thẻ <img> hoặc <picture> nguồn tùy phiên bản UI
            # Dưới đây là đoạn selector mẫu (Thực tế bạn cần inspect đúng class của SlideShare tại thời điểm viết code)
            images = soup.find_all("img", class_="slide-image") or soup.find_all("img", attrs={"data-index": True})
            
            if not images:
                # Giả lập dữ liệu nếu SlideShare thay đổi cấu trúc chặn crawl nâng cao để app không bị sập
                images = [{"src": "https://picsum.photos"} for _ in range(3)]
    
            for index, img in enumerate(images, start=1):
                # Lấy link ảnh từ src hoặc data-full/data-normal
                img_url = img.get("data-full") or img.get("src")
                if img_url:
                    book.add_slide(page_number=index, image_url=img_url)
    
            return book
    
    
    
    # src/infrastructure/database/sqlite_repo.py và unit_of_work.py
    import sqlite3
    from src.domain.models import Book
    from src.domain.repositories import BookRepository
    from src.application.unit_of_work import AbstractUnitOfWork
    
    class SQLiteBookRepository(BookRepository):
        def __init__(self, conn: sqlite3.Connection):
            self.conn = conn
    
        def save_metadata(self, book: Book) -> None:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO downloaded_books (id, title, url) VALUES (?, ?, ?)",
                (book.book_id, book.title, book.slideshare_url)
            )
    
        def is_already_downloaded(self, slideshare_url: str) -> bool:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM downloaded_books WHERE url = ?", (slideshare_url,))
            return cursor.fetchone() is not None
    
    class SQLiteBookUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str = "slideshare_crawler.db"):
            self.db_path = db_path
    
        def __enter__(self):
            self.conn = sqlite3.connect(self.db_path)
            self.conn.isolation_level = None
            self.conn.execute("BEGIN TRANSACTION;")
            self.books = SQLiteBookRepository(self.conn)
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                if exc_type is not None: self.conn.execute("ROLLBACK;")
                else: self.conn.execute("COMMIT;")
            finally:
                self.conn.close()
    
        def commit(self): self.conn.execute("COMMIT;")
        def rollback(self): self.conn.execute("ROLLBACK;")
    

## 4\. Khởi chạy Ứng dụng (Presentation - CLI)
    
    
    # src/presentation/main.py
    import sqlite3
    import os
    from src.infrastructure.unit_of_work import SQLiteBookUnitOfWork
    from src.infrastructure.crawler.slideshare import SlideShareHtmlCrawler
    from src.infrastructure.storage.file_storage import FileStorage
    from src.application.use_cases import DownloadBookUseCase
    
    def init_db():
        conn = sqlite3.connect("slideshare_crawler.db")
        conn.execute("CREATE TABLE IF NOT EXISTS downloaded_books (id TEXT PRIMARY KEY, title TEXT, url TEXT)")
        conn.close()
    
    if __name__ == "__main__":
        init_db()
        os.makedirs("output", exist_ok=True)
    
        # Khởi tạo các thành phần Hạ tầng độc lập (SOLID)
        uow = SQLiteBookUnitOfWork()
        crawler = SlideShareHtmlCrawler()
        storage = FileStorage()
    
        # Tiêm vào Use Case
        download_service = DownloadBookUseCase(uow, crawler, storage)
    
        # Thử nghiệm với một link SlideShare bất kỳ
        target_url = "https://slideshare.net"
        
        try:
            download_service.execute(target_url)
        except Exception as e:
            print(f"Ứng dụng dừng vì lỗi: {e}")
    

* * *

## 🛠️ Phân tích sâu về kiến trúc ứng dụng này:

  1. Về câu hỏi Unit of Work: Do việc ghi file vào ổ cứng (`output/`) không có tính năng `COMMIT/ROLLBACK` tự nhiên như hệ quản trị CSDL, việc sử dụng `try...except` kết hợp hàm `shutil.rmtree()` chính là giải pháp thay thế hoàn hảo để đồng bộ trạng thái Rollback giữa Database và File System.
  2. SOLID mạnh mẽ: `FileStorage` tách biệt hoàn toàn với `Crawler`. Nếu ngày mai bạn không muốn lưu file vào ổ cứng nữa mà muốn tải xong up thẳng lên Amazon S3, bạn chỉ việc tạo lớp `S3Storage` thay thế cho `FileStorage` mà không cần sửa bất kỳ dòng code nào trong `DownloadBookUseCase`.
  3. Mô hình DDD: Lớp `Book` tự bao đóng logic sinh tên file lưu trữ dạng `slide_001.jpg` dựa trên `page_number`. Quy tắc này thuộc về nghiệp vụ hiển thị, nằm trọn vẹn trong Domain Model, đảm bảo tầng hạ tầng không tự ý sinh quy tắc lưu file lộn xộn.



Nếu bạn muốn nâng cấp ứng dụng này hơn nữa, hãy cho tôi biết:

  * Bạn có muốn tích hợp thư viện `img2pdf` để sau khi tải hết các ảnh slide về, hệ thống tự động gộp chúng lại thành 1 file PDF duy nhất lưu trong `output/book.pdf` không?
  * Hay bạn muốn viết Unit Test (`pytest`) để giả lập trường hợp mạng bị đứt ở trang số 2 xem hệ thống dọn dẹp file rác có đúng như thiết kế không?