Để thêm tùy chọn (Flag) lựa chọn giữa việc "Chỉ tải ảnh" hoặc "Tải ảnh và gộp luôn thành PDF", chúng ta sẽ sử dụng thư viện `argparse` tiêu chuẩn của Python ở tầng Presentation.

Đồng thời, để tuân thủ SOLID (nguyên lý O - Open/Closed), chúng ta không cần chỉnh sửa cấu trúc bên trong của Use Case, mà chỉ cần truyền thêm một cấu hình (Flag điều hướng) vào hàm `execute()`.

Dưới đây là cách cập nhật chi tiết cho tầng Application và tầng Presentation.

* * *

## 💻 Triển khai mã nguồn cập nhật

## 1\. Cập nhật Tầng Application (Use Case)

Chúng ta bổ sung thêm tham số `export_pdf: bool = True` vào hàm `execute`. Nếu flag này là `False`, Use Case sẽ bỏ qua bước gộp PDF.
    
    
    # src/application/use_cases.py
    import os
    import shutil
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.domain.repositories import SlideShareClient, PdfConverter
    from src.infrastructure.storage.file_storage import FileStorage
    
    class DownloadBookUseCase:
        def __init__(
            self, 
            uow: AbstractUnitOfWork, 
            crawler: SlideShareClient, 
            storage: FileStorage,
            pdf_converter: PdfConverter
        ):
            self.uow = uow
            self.crawler = crawler
            self.storage = storage
            self.pdf_converter = pdf_converter
    
        def execute(self, url: str, export_pdf: bool = True) -> None:
            """
            Thực thi Use Case tải sách.
            :param url: Đường dẫn SlideShare cần crawl.
            :param export_pdf: Flag quyết định có gộp thành file PDF hay không.
            """
            with self.uow:
                if self.uow.books.is_already_downloaded(url):
                    print("[Application] Sách này đã được tải trước đó. Bỏ qua.")
                    return
    
            book = self.crawler.fetch_book_info(url)
            book_output_dir = f"output/{book.book_id}"
            final_pdf_path = f"output/{book.book_id}/{book.title.replace(' ', '_')}.pdf"
    
            try:
                with self.uow:
                    # 1. Lưu thông tin metadata sách vào DB
                    self.uow.books.save_metadata(book)
    
                    # 2. Tải tất cả các slide ảnh về máy
                    image_paths = []
                    for slide in book.slides:
                        self.storage.download_and_save(slide.image_url, slide.local_path)
                        image_paths.append(slide.local_path)
                        print(f"[Application] Đã tải Slide {slide.page_number}")
    
                    # 3. Kiểm tra Flag điều hướng: Nếu người dùng yêu cầu xuất PDF thì mới chạy
                    if export_pdf:
                        self.pdf_converter.convert_images_to_pdf(image_paths, final_pdf_path)
                    else:
                        print("[Application] Nhận flag chỉ tải ảnh. Bỏ qua bước xuất PDF.")
    
                print(f"🎉 Hoàn thành trọn vẹn tiến trình cho sách: {book.title}!")
    
            except Exception as e:
                print(f"💥 Lỗi xảy ra: {e}. Tiến hành Rollback và dọn dẹp file rác...")
                if os.path.exists(book_output_dir):
                    shutil.rmtree(book_output_dir)
                raise e
    

## 2\. Cập nhật Tầng Presentation (Giao diện CLI bằng `argparse`)

Chúng ta xây dựng giao diện CLI nhận vào 2 tham số:

  * `url`: Đường dẫn bắt buộc.
  * `--only-images`: Flag tùy chọn. Nếu người dùng thêm flag này, hệ thống sẽ chỉ tải ảnh. Mặc định nếu không truyền gì, hệ thống sẽ vừa tải ảnh vừa gộp thành PDF.


    
    
    # src/presentation/main.py
    import argparse
    import os
    import sqlite3
    from src.infrastructure.unit_of_work import SQLiteBookUnitOfWork
    from src.infrastructure.crawler.slideshare import SlideShareHtmlCrawler
    from src.infrastructure.storage.file_storage import FileStorage
    from src.infrastructure.storage.pdf_converter import PyMuPdfConverter
    from src.application.use_cases import DownloadBookUseCase
    
    def init_db():
        conn = sqlite3.connect("slideshare_crawler.db")
        conn.execute("CREATE TABLE IF NOT EXISTS downloaded_books (id TEXT PRIMARY KEY, title TEXT, url TEXT)")
        conn.close()
    
    def main():
        init_db()
        os.makedirs("output", exist_ok=True)
    
        # 1. Định nghĩa bộ phân tích cú pháp CLI (Argparse)
        parser = argparse.ArgumentParser(description="SlideShare Book Downloader (Clean Architecture & SOLID)")
        
        # Tham số bắt buộc: URL
        parser.add_argument("url", type=str, help="Đường dẫn (URL) của tài liệu SlideShare cần tải.")
        
        # Tham số tùy chọn (Flag): Chỉ tải ảnh, không xuất PDF
        parser.add_argument(
            "--only-images", 
            action="store_true", 
            help="Chỉ tải hình ảnh slide về máy, không tự động đóng gói thành file PDF."
        )
    
        args = parser.parse_args()
    
        # 2. Khởi tạo và tiêm các thành phần Hạ tầng (Dependency Injection)
        uow = SQLiteBookUnitOfWork()
        crawler = SlideShareHtmlCrawler()
        storage = FileStorage()
        pdf_converter = PyMuPdfConverter()
    
        download_service = DownloadBookUseCase(
            uow=uow, 
            crawler=crawler, 
            storage=storage, 
            pdf_converter=pdf_converter
        )
    
        # 3. Điều hướng Flag từ CLI vào tầng Ứng dụng
        # Nếu người dùng truyền --only-images thì export_pdf sẽ là False
        export_pdf_flag = not args.only_images
    
        print(f"[CLI] Đang chuẩn bị xử lý URL: {args.url}")
        print(f"[CLI] Chế độ xuất PDF: {'BẬT' if export_pdf_flag else 'TẮT (Chỉ tải ảnh)'}")
    
        try:
            download_service.execute(args.url, export_pdf=export_pdf_flag)
        except Exception as e:
            print(f"[CLI] Ứng dụng dừng vì lỗi hệ thống: {e}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🚀 Hướng dẫn vận hành ứng dụng qua Terminal

Bây giờ bạn có thể mở Terminal và chạy ứng dụng với 2 tùy chọn khác nhau tùy theo nhu cầu:

## Kịch bản A: Chạy mặc định (Tải ảnh + Tự động gộp thành file PDF)

Bạn chỉ cần truyền URL vào sau file chạy:
    
    
    python -m src.presentation.main https://slideshare.net
    

  * Kết quả: Hệ thống sẽ tạo thư mục `output/book_id/`, tải toàn bộ ảnh slide về đĩa, sau đó dùng thư viện `fitz` tạo ra file `.pdf` nằm ngay trong thư mục đó.



## Kịch bản B: Chỉ tải ảnh slide (Bỏ qua bước gộp PDF)

Bạn thêm flag `--only-images` ở cuối câu lệnh:
    
    
    python -m src.presentation.main https://slideshare.net --only-images
    

  * Kết quả trên Terminal sẽ hiển thị:
        
        [CLI] Đang chuẩn bị xử lý URL: https://slideshare.net
        [CLI] Chế độ xuất PDF: TẮT (Chỉ tải ảnh)
        [Application] Đã tải Slide 1
        [Application] Đã tải Slide 2
        [Application] Đã tải Slide 3
        [Application] Nhận flag chỉ tải ảnh. Bỏ qua bước xuất PDF.
        🎉 Hoàn thành trọn vẹn tiến trình cho sách: Sample Presentation!
        

  * Kết quả: Trong thư mục `output/book_id/` sẽ chỉ chứa các file ảnh `.jpg`, hoàn toàn không sinh ra file `.pdf` nào, giúp tiết kiệm thời gian và tài nguyên CPU nếu người dùng không cần.



* * *

## 🛡️ Tính bền vững của thiết kế này

Nhờ tách biệt giao diện (`main.py` thuộc lớp Presentation) khỏi logic nghiệp vụ (`use_cases.py` thuộc lớp Application):

  1. Nếu sau này bạn chuyển ứng dụng từ giao diện dòng lệnh (CLI) thành một trang Web API (FastAPI), bạn chỉ cần lấy đúng hàm `download_service.execute(url, export_pdf=...)` gắn vào router của FastAPI. Toàn bộ logic tải ảnh, quản lý lỗi, rollback dữ liệu và kiểm tra Flag vẫn giữ nguyên vẹn 100%.
  2. Tầng UI (CLI) chịu trách nhiệm nhận tham số từ người dùng, làm sạch dữ liệu, sau đó "phiên dịch" thành kiểu dữ liệu nguyên thủy (`bool`) để truyền vào lớp lõi, giữ cho lớp lõi luôn độc lập hoàn toàn khỏi thư viện `argparse`.



Để hoàn thiện trọn vẹn dự án này, hãy cho tôi biết:

  * Bạn có muốn tối ưu hiệu năng tải ảnh bằng cách áp dụng cơ chế đa luồng (Multi-threading) để tải nhiều slide ảnh cùng một lúc cho nhanh hơn không?
  * Hay bạn muốn tìm hiểu cách viết mã nguồn kiểm thử Unit Test (`pytest`) để giả lập việc bật/tắt flag `--only-images` này hoạt động chính xác?