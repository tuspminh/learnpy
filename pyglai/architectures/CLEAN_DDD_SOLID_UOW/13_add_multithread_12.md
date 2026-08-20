Đối với bài toán crawl sách từ SlideShare (tải nhiều file ảnh từ internet cùng lúc), câu trả lời trực diện nhất là: Bạn nên ưu tiên sử dụng `ThreadPoolExecutor` (Multi-threading) nếu muốn giữ cho kiến trúc Clean Architecture sạch sẽ và dễ triển khai nhất. Tuy nhiên, `asyncio` cũng là một lựa chọn cực mạnh nếu bạn ưu tiên tối ưu tài nguyên tối đa.

Dưới đây là phân tích chi tiết để bạn đưa ra quyết định dựa trên đặc thù ngôn ngữ Python và cấu trúc dự án hiện tại của bạn.

* * *

## 📊 So sánh: Nên chọn bên nào cho dự án hiện tại?

Do Python có cơ chế GIL (Global Interpreter Lock), cả `ThreadPoolExecutor` lẫn `asyncio` đều không chạy đa nhân CPU thực sự, nhưng chúng đều xử lý cực kỳ tốt các tác vụ I/O-bound (chờ phản hồi mạng từ HTTP requests, ghi file xuống đĩa).

Tiêu chí| `ThreadPoolExecutor` (Khuyên dùng)| `asyncio` (Bất đồng bộ)  
---|---|---  
Độ tương thích với Clean Architecture| Cực cao. Nó hoạt động đồng bộ (`sync`). Bạn không cần thay đổi bất kỳ Interface hay cấu trúc Use Case hiện tại nào.| Thấp/Phức tạp hơn. Bạn bắt buộc phải thêm từ khóa `async/await` vào khắp dự án từ Interface, Use Case đến Repo.  
Thư viện đi kèm| Giữ nguyên `requests`, `sqlite3` thuần đang chạy ổn định của bạn.| Phải đập đi thay thế toàn bộ bằng thư viện async: `httpx` (hoặc `aiohttp`), `aiosqlite`.  
Hiệu năng (Performance)| Tải hàng chục ảnh cùng lúc cực nhanh. Mỗi thread tốn khoảng vài MB RAM của hệ thống.| Tải hàng trăm/hàng nghìn ảnh cùng lúc với chi phí RAM cực thấp (chỉ vài KB cho mỗi tác vụ).  
Độ phức tạp khi viết code| Rất dễ đọc, dễ kiểm soát lỗi (Exception handling) trong khối `try...except`.| Khó debug hơn, dễ gặp lỗi "rò rỉ" tác vụ nếu không quản lý kỹ vòng lặp sự kiện (`event loop`).  
  
Kết luận:

  * Dùng `ThreadPoolExecutor`: Khi bạn muốn ứng dụng chạy nhanh gấp 5-10 lần ngay lập tức mà không muốn phá vỡ cấu trúc code Clean & SOLID hiện tại.
  * Dùng `asyncio`: Khi bạn có ý định nâng cấp app này thành một Web API (FastAPI) chịu tải hàng nghìn lượt crawl cùng một lúc từ nhiều người dùng.



* * *

## 💻 Triển khai Tối ưu Đa luồng với `ThreadPoolExecutor`

Chúng ta áp dụng đúng nguyên lý O (Open/Closed): Không sửa bất kỳ dòng code nào trong `DownloadBookUseCase`, không sửa mô hình Domain. Chúng ta chỉ tạo ra một lớp Hạ tầng mới có tên là `MultiThreadedFileStorage` thay thế cho `FileStorage` cũ.

## 1\. Cập nhật Tầng Infrastructure (Tạo Storage đa luồng)
    
    
    # src/infrastructure/storage/multi_threaded_storage.py
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from typing import List, Tuple
    import requests
    
    class MultiThreadedFileStorage:
        def __init__(self, max_workers: int = 5):
            """
            :param max_workers: Số lượng luồng chạy đồng thời (mặc định tải 5 ảnh cùng lúc)
            """
            self.max_workers = max_workers
    
        def _download_single_image(self, url: str, local_path: str) -> None:
            """Hàm tải 1 file ảnh (giữ nguyên logic cũ nhưng chạy trong luồng riêng)"""
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    
        def download_batch(self, download_tasks: List[Tuple[str, str]]) -> None:
            """
            Nhận vào danh sách các tuple (url, local_path) và tải đa luồng
            """
            print(f"[Infrastructure] Bắt đầu tải đa luồng với tối đa {self.max_workers} workers...")
            
            # Sử dụng ThreadPoolExecutor để quản lý nhóm luồng
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Giao việc cho các luồng xử lý độc lập
                future_to_url = {
                    executor.submit(self._download_single_image, url, path): url 
                    for url, path in download_tasks
                }
                
                # Theo dõi tiến độ và bắt lỗi nếu có bất kỳ luồng nào bị sập mạng
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result() # Nếu hàm ném ra lỗi, lỗi sẽ xuất hiện ở đây
                    except Exception as exc:
                        print(f"💥 Lỗi khi tải URL {url}: {exc}")
                        raise exc # Đẩy lỗi ra ngoài để Use Case kích hoạt cơ chế Rollback/Xóa file rác
    

## 2\. Cập nhật Tầng Application (Use Case gọi hàm Batch)

Để Use Case tận dụng được tính năng tải hàng loạt, chúng ta điều chỉnh nhẹ luồng gom các tác vụ tải ảnh lại rồi đẩy cho Storage xử lý một lượt.
    
    
    # src/application/use_cases.py
    import os
    import shutil
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.domain.repositories import SlideShareClient, PdfConverter
    
    class DownloadBookUseCase:
        def __init__(self, uow: AbstractUnitOfWork, crawler: SlideShareClient, storage, pdf_converter: PdfConverter):
            self.uow = uow
            self.crawler = crawler
            self.storage = storage # Nhận lớp Storage đa luồng từ ngoài tiêm vào
            self.pdf_converter = pdf_converter
    
        def execute(self, url: str, export_pdf: bool = True) -> None:
            with self.uow:
                if self.uow.books.is_already_downloaded(url):
                    print("[Application] Sách này đã được tải trước đó. Bỏ qua.")
                    return
    
            book = self.crawler.fetch_book_info(url)
            book_output_dir = f"output/{book.book_id}"
            final_pdf_path = f"output/{book.book_id}/{book.title.replace(' ', '_')}.pdf"
    
            try:
                with self.uow:
                    self.uow.books.save_metadata(book)
    
                    # 1. Chuẩn bị danh sách tác vụ để tải hàng loạt
                    download_tasks = []
                    image_paths = []
                    for slide in book.slides:
                        download_tasks.append((slide.image_url, slide.local_path))
                        image_paths.append(slide.local_path)
    
                    # 2. Kích hoạt tải đa luồng
                    self.storage.download_batch(download_tasks)
                    print("[Application] Đã hoàn thành tải tất cả hình ảnh slide.")
    
                    if export_pdf:
                        self.pdf_converter.convert_images_to_pdf(image_paths, final_pdf_path)
    
                print(f"🎉 Hoàn thành trọn vẹn tiến trình cho sách: {book.title}!")
    
            except Exception as e:
                print(f"💥 Lỗi xảy ra: {e}. Tiến hành dọn dẹp thư mục rác...")
                if os.path.exists(book_output_dir):
                    shutil.rmtree(book_output_dir)
                raise e
    

## 3\. Thay đổi lớp khởi tạo tại Tầng Presentation (`main.py`)

Tại file cấu hình khởi chạy, bạn chỉ cần đổi lớp `FileStorage` cũ thành `MultiThreadedFileStorage`:
    
    
    # Thay đổi duy nhất tại src/presentation/main.py
    from src.infrastructure.storage.multi_threaded_storage import MultiThreadedFileStorage
    
    # Khởi tạo và quy định chạy tối đa 8 luồng cùng lúc
    storage = MultiThreadedFileStorage(max_workers=8) 
    
    # Tiêm vào Use Case như bình thường
    download_service = DownloadBookUseCase(uow, crawler, storage, pdf_converter)
    

* * *

## 🛡️ Minh chứng tối thượng của SOLID trong giải pháp này

Hãy nhìn lại toàn bộ quá trình: Khi bạn muốn tối ưu tốc độ từ Đơn luồng lên Đa luồng (Multi-threading):

  1. Bạn không cần viết lại cơ chế transaction của `SQLiteUnitOfWork`.
  2. Bạn không cần sửa logic bóc tách HTML của `SlideShareHtmlCrawler`.
  3. Bạn không cần động vào mã nguồn ghép file của `PyMuPdfConverter`.



Mọi thứ hoạt động như những khối Lego độc lập. Bạn chỉ cần chế tạo một khối Lego mới (`MultiThreadedFileStorage`) và lắp ráp nó vào hệ thống thông qua cơ chế Dependency Injection.

Nếu bạn muốn đo đạc hiệu năng thực tế, tôi có thể hướng dẫn bạn cách nhúng module `time` để in ra chính xác thời gian tải đa luồng nhanh hơn đơn luồng bao nhiêu giây, bạn có muốn thử không?