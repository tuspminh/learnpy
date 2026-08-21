Dưới đây là mã nguồn chi tiết cho file `src/use_cases/download_slide.py` cùng với các file Interfaces liên quan nằm trong thư mục `interfaces/` theo đúng cấu trúc hiện đại của bạn.

Điểm đặc biệt ở đây là Use Case sẽ đóng vai trò điều phối kịch bản (Orchestrator). Nó không quan tâm bạn dùng Playwright hay ReportLab, nó chỉ làm việc với các bản hợp đồng trừu tượng (Abstract Interfaces).

* * *

## 1\. Định nghĩa các Cổng trừu tượng (Ports)

Các interface này nằm ngay trong gói `use_cases` để phục vụ chính xác nhu cầu của Use Case.

## File: `src/use_cases/interfaces/crawler.py`
    
    
    from abc import ABC, abstractmethod
    from src.domain.entities import SlideBook
    
    class CrawlerInterface(ABC):
        
        @abstractmethod
        def extract_metadata(self, url: str) -> SlideBook:
            """
            Khởi tạo thực thể SlideBook bằng cách cào tiêu đề và số trang.
            Chưa tải dữ liệu hình ảnh (binary data).
            """
            pass
    
        @abstractmethod
        def download_page_image(self, image_url: str) -> bytes:
            """
            Tải trực tiếp hình ảnh từ URL về dưới dạng chuỗi byte nhị phân.
            """
            pass
    

## File: `src/use_cases/interfaces/pdf_exporter.py`
    
    
    from abc import ABC, abstractmethod
    from src.domain.entities import SlideBook
    
    class PdfExporterInterface(ABC):
    
        @abstractmethod
        def export(self, slide_book: SlideBook, output_path: str) -> None:
            """
            Nhận vào đối tượng SlideBook đã có đủ dữ liệu hình ảnh,
            tiến hành đóng gói thành file PDF hoàn chỉnh.
            """
            pass
    

* * *

## 2\. Triển khai Use Case Điều Phối Luồng Xử Lý

File này sẽ nhận vào một hàm `progress_callback` (từ tầng `presentation/cli.py` truyền qua) để cập nhật thanh tiến độ theo thời gian thực mà không làm bẩn logic nghiệp vụ.

## File: `src/use_cases/download_slide.py`
    
    
    from typing import Callable, Optional
    from src.domain.exceptions import DomainException  # Giả định bạn định nghĩa các lỗi tại đây
    from src.use_cases.interfaces.crawler import CrawlerInterface
    from src.use_cases.interfaces.pdf_exporter import PdfExporterInterface
    
    class DownloadSlideUseCase:
        """
        Use Case trung tâm chịu trách nhiệm điều phối toàn bộ kịch bản:
        Nhận link -> Cào thông tin -> Tải từng trang -> Đóng gói PDF.
        """
        def __init__(
            self, 
            crawler: CrawlerInterface, 
            pdf_exporter: PdfExporterInterface
        ):
            # Đảo ngược phụ thuộc (DIP): Nhận interface thay vì class cụ thể
            self._crawler = crawler
            self._pdf_exporter = pdf_exporter
    
        def execute(
            self, 
            url: str, 
            output_path: str, 
            progress_callback: Optional[Callable[[int, int], None]] = None
        ) -> None:
            """
            Thực thi kịch bản tải và xuất file PDF từ SlideShare.
            
            :param url: Đường dẫn tài liệu SlideShare.
            :param output_path: Nơi lưu file PDF kết quả.
            :param progress_callback: Hàm callback nhận (số_trang_hiện_tại, tổng_số_trang) để update UI.
            """
            try:
                # Bước 1: Thu thập cấu trúc tổng quan (Title, List Image URLs)
                # Khởi tạo thực thể SlideBook (nằm trong domain/entities.py)
                slide_book = self._crawler.extract_metadata(url)
                
                if not slide_book.pages:
                    raise DomainException("Tài liệu SlideShare không chứa trang nào hoặc bị lỗi phân tích.")
    
                total_pages = slide_book.total_pages
    
                # Bước 2: Vòng lặp tải dữ liệu nhị phân (binary bytes) cho từng trang
                for index, page in enumerate(slide_book.pages):
                    # Tải ảnh qua cổng crawler
                    image_bytes = self._crawler.download_page_image(page.image_url)
                    
                    # Ghi đè dữ liệu binary vào thực thể (Entity quản lý trạng thái dữ liệu của chính nó)
                    page.binary_data = image_bytes
                    
                    # Kích hoạt hàm callback để báo cho CLI cập nhật thanh tiến độ (Click progress bar)
                    if progress_callback:
                        progress_callback(index + 1, total_pages)
    
                # Bước 3: Đóng gói toàn bộ các trang ảnh trong SlideBook thành file PDF bằng ReportLab
                self._pdf_exporter.export(slide_book, output_path)
    
            except Exception as e:
                # Log lỗi hoặc bọc lại thành lỗi của tầng ứng dụng nếu cần thiết
                # Đảm bảo lỗi không làm sập ứng dụng một cách im lặng
                raise DomainException(f"Lỗi trong quá trình xử lý Use Case: {str(e)}") from e
    

* * *

## Ý nghĩa thiết kế của đoạn code này:

  1. Hoàn toàn độc lập công nghệ: Trong file `download_slide.py` trên, bạn không thấy bất kỳ từ khóa nào liên quan đến `playwright`, `requests` hay `reportlab`. Nếu ngày mai bạn muốn chuyển qua dùng `selenium` và `fpdf2`, file Use Case này giữ nguyên 100% không sửa một chữ.
  2. Dễ dàng viết Unit Test: Bạn có thể dễ dàng viết mock test cho Use Case này bằng cách tạo ra các class giả lập (Mock/Fake) kế thừa từ `CrawlerInterface` và `PdfExporterInterface` mà không cần chạy trình duyệt thật hay tạo file PDF thật ra ổ cứng.
  3. Luồng dữ liệu một chiều: `presentation/cli.py` gọi hàm `execute()`, Use Case đẩy dữ liệu xuống hạ tầng qua `interfaces`, hạ tầng xử lý xong trả Entity ngược lại cho Use Case gom góp rồi xuất file.



Bạn có muốn viết tiếp phần cài đặt thực tế của một trong hai adapter ngoại vi, ví dụ `playwright_crawler.py` (xử lý cào bằng Playwright headless) hoặc `reportlab_exporter.py` (vẽ PDF từ mảng bytes) để khớp hoàn toàn vào Use Case này không?