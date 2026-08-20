Để tích hợp thêm chức năng xuất file PDF từ các hình ảnh slide đã tải về bằng thư viện PyMuPDF (tên package là `fitz`), chúng ta sẽ tiếp tục tuân thủ nghiêm ngặt Kiến trúc Clean Architecture và nguyên lý SOLID.

Việc xuất PDF này thuộc về chi tiết công nghệ (Hạ tầng), do đó chúng ta sẽ định nghĩa một Interface ở tầng Application, sau đó triển khai thực tế bằng `fitz` ở tầng Infrastructure.

* * *

## 📂 Cấu trúc thư mục cập nhật

Chúng ta bổ sung thêm Interface `PdfConverter` vào tầng Domain/Repository hoặc Application, và triển khai lớp hạ tầng `PyMuPdfConverter`.
    
    
    src/
    ├── domain/
    │   ├── models.py
    │   └── repositories.py      # Thêm Interface PdfConverter (hoặc đặt ở Application)
    ├── application/
    │   └── use_cases.py         # Cập nhật DownloadBookUseCase để gọi chức năng xuất PDF
    └── infrastructure/
        └── storage/
            ├── file_storage.py
            └── pdf_converter.py # [MỚI] Triển khai chuyển đổi ảnh sang PDF bằng PyMuPDF (fitz)
    

* * *

## 💻 Triển khai mã nguồn chi tiết

Trước khi bắt đầu, hãy đảm bảo bạn đã cài đặt thư viện `PyMuPDF`:
    
    
    pip install PyMuPDF
    

## 1\. Định nghĩa Interface (Tầng Domain / Application)

Để Use Case không bị dính chặt vào thư viện `fitz`, chúng ta tạo một lớp trừu tượng tuân thủ nguyên lý D (Dependency Inversion).
    
    
    # src/domain/repositories.py (hoặc src/application/interfaces.py)
    from abc import ABC, abstractmethod
    from typing import List
    
    class PdfConverter(ABC):
        @abstractmethod
        def convert_images_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> None:
            """Nhận vào danh sách đường dẫn ảnh và xuất ra 1 file PDF duy nhất"""
            pass
    

## 2\. Triển khai lớp hạ tầng sử dụng PyMuPDF/fitz (Tầng Infrastructure)

Đây là nơi công nghệ `fitz` thực sự xuất hiện để xử lý ghép ảnh thành PDF.
    
    
    # src/infrastructure/storage/pdf_converter.py
    import fitz  # PyMuPDF
    import os
    from typing import List
    from src.domain.repositories import PdfConverter
    
    class PyMuPdfConverter(PdfConverter):
        def convert_images_to_pdf(self, image_paths: List[str], output_pdf_path: str) -> None:
            if not image_paths:
                raise ValueError("Danh sách hình ảnh trống, không thể tạo PDF.")
    
            # 1. Tạo một tài liệu PDF trống bằng fitz
            doc = fitz.open()
    
            print(f"[Infrastructure] Bắt đầu đóng gói {len(image_paths)} slides thành file PDF...")
            
            for img_path in sorted(image_paths): # Đảm bảo sắp xếp đúng thứ tự trang
                if not os.path.exists(img_path):
                    continue
                    
                # 2. Mở file ảnh dưới dạng tài liệu tạm thời của fitz
                img_doc = fitz.open(img_path)
                
                # 3. Chuyển đổi ảnh thành định dạng trang PDF (PDF bytes)
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
    
                # 4. Tạo một trang PDF tạm thời từ bytes vừa chuyển đổi và chèn vào tài liệu chính
                temp_page = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(temp_page)
                temp_page.close()
    
            # 5. Đảm bảo thư mục chứa file PDF đầu ra tồn tại
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
            # 6. Lưu file PDF xuống ổ cứng và giải phóng bộ nhớ
            doc.save(output_pdf_path)
            doc.close()
            print(f"[Infrastructure] 🎉 Đã xuất file PDF thành công tại: {output_pdf_path}")
    

## 3\. Cập nhật Luồng Nghiệp vụ (Tầng Application - Use Case)

Tiêm `PdfConverter` vào `DownloadBookUseCase`. Tiến trình tạo PDF cũng nằm trong khối quản lý lỗi để nếu lỗi xảy ra, file PDF tạo dở hoặc thư mục ảnh rác sẽ bị dọn dẹp sạch sẽ.
    
    
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
            pdf_converter: PdfConverter # [MỚI] Tiêm Interface PdfConverter vào qua Constructor
        ):
            self.uow = uow
            self.crawler = crawler
            self.storage = storage
            self.pdf_converter = pdf_converter
    
        def execute(self, url: str) -> None:
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
    
                    # 3. [MỚI] Gom các file ảnh vừa tải để xuất ra PDF
                    self.pdf_converter.convert_images_to_pdf(image_paths, final_pdf_path)
    
                print(f"🎉 Hoàn thành trọn vẹn Use Case cho sách: {book.title}!")
    
            except Exception as e:
                print(f"💥 Lỗi xảy ra: {e}. Tiến hành Rollback và dọn dẹp file rác...")
                # Nếu quá trình tải ảnh hoặc tạo PDF bị lỗi, dọn sạch thư mục để tránh rác hệ thống
                if os.path.exists(book_output_dir):
                    shutil.rmtree(book_output_dir)
                raise e
    

## 4\. Khởi chạy Ứng dụng (Tầng Presentation - CLI)

Lúc này tại file chạy chính, ta chỉ cần khởi tạo `PyMuPdfConverter` và tiêm vào Use Case.
    
    
    # src/presentation/main.py
    import os
    from src.infrastructure.unit_of_work import SQLiteBookUnitOfWork
    from src.infrastructure.crawler.slideshare import SlideShareHtmlCrawler
    from src.infrastructure.storage.file_storage import FileStorage
    from src.infrastructure.storage.pdf_converter import PyMuPdfConverter # Thêm import hạ tầng mới
    from src.application.use_cases import DownloadBookUseCase
    
    if __name__ == "__main__":
        os.makedirs("output", exist_ok=True)
    
        # 1. Khởi tạo các thành phần Hạ tầng cụ thể
        uow = SQLiteBookUnitOfWork()
        crawler = SlideShareHtmlCrawler()
        storage = FileStorage()
        pdf_converter = PyMuPdfConverter() # Khởi tạo cụ thể lớp dùng fitz
    
        # 2. Tiêm toàn bộ vào Use Case (Thỏa mãn Dependency Inversion)
        download_service = DownloadBookUseCase(
            uow=uow, 
            crawler=crawler, 
            storage=storage, 
            pdf_converter=pdf_converter
        )
    
        target_url = "https://slideshare.net"
        
        try:
            download_service.execute(target_url)
        except Exception as e:
            print(f"Ứng dụng dừng vì lỗi: {e}")
    

* * *

## 🎯 Cách thiết kế này tuân thủ SOLID như thế nào?

  * O (Open/Closed Principle): Giả sử sau này bạn phát hiện ra một thư viện chuyển PDF tốt hơn `PyMuPDF` (ví dụ như `reportlab` hay `img2pdf`), bạn không cần sửa một dòng code nào trong tầng nghiệp vụ `DownloadBookUseCase`. Bạn chỉ cần tạo một class mới có tên là `ReportLabConverter(PdfConverter)` và thay thế nó ở file `main.py`.
  * D (Dependency Inversion Principle): `DownloadBookUseCase` (Mô-đun cấp cao) chỉ phụ thuộc vào `PdfConverter` (Sự trừu tượng). Bản thân thư viện `fitz` (Mô-đun cấp thấp) bị đẩy ra rìa ngoài cùng của hệ thống (`Infrastructure Layer`), giúp phần lõi ứng dụng luôn "sạch sẽ" và độc lập với các công nghệ bên ngoài.



Tính năng xuất PDF đã sẵn sàng hoạt động. Bạn có muốn tiếp tục tối ưu ứng dụng này bằng cách:

  * Viết một bài Unit Test bằng `pytest` giả lập kịch bản xuất file PDF thành công mà không cần chạy code tạo file thật?
  * Hoặc bạn muốn thêm một tùy chọn (Flag) vào giao diện CLI để người dùng có thể lựa chọn: "Chỉ tải ảnh" hoặc "Tải ảnh và gộp luôn thành PDF"?