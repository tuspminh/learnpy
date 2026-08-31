Để kết nối kiến trúc 3 tầng Bounded Context ở trên với giao diện PySide6 một cách mượt mà, không gây đơ lag và đảm bảo nguyên lý SOLID, chúng ta sẽ sử dụng mô hình MVVM (Model-View-ViewModel) [1] kết hợp với lớp Worker chạy trên `QThread`.

Dưới đây là thiết kế chi tiết luồng xử lý và mã nguồn triển khai công cụ cập nhật tiến độ cào (Progress Bar) theo thời gian thực.

* * *

## Sơ đồ Luồng Hoạt động (State & Event Flow)
    
    
    [View: UI PySide6] 
           │ (1. Người dùng bấm "Cào")
           ▼
    [ViewModel] ──(2. Tạo & Kích hoạt)──► [QThread Worker] ──► [Application Service]
           ▲                                   │                    │ (3. Cào & Lưu DB)
           │                                   │                    ▼
           └───────(5. Nhận Tín Hiệu)──────────┴──(4. Bắn Signal)─── [Mỗi khi xong 1 chương]
           │
           ▼ (6. Cập nhật Progress Bar & Bảng)
    [Hiển thị trên màn hình]
    

* * *

## Triển khai Mã nguồn Chi tiết

## 1\. Lớp Worker (Tầng Giao diện - Phần ngầm)

Lớp này kế thừa từ `QThread` (hoặc `QRunnable`), đóng vai trò là cầu nối chạy ngầm để thực thi Application Service mà không chặn luồng xử lý giao diện (UI Thread).
    
    
    # presentation/workers.py
    from PySide6.QtCore import QThread, Signal
    import time
    
    class ChapterCrawlWorker(QThread):
        """Worker chạy ngầm để cào danh sách chương.
        Tuân thủ SRP: Chỉ làm nhiệm vụ điều phối luồng (Thread), không chứa logic cào HTML.
        """
        # Định nghĩa các Event (Signals) để gửi ngược về cho ViewModel
        chapter_downloaded = Signal(int, str)  # (index_vừa_cào, tiêu_đề_chương)
        progress_updated = Signal(int)         # phần_trăm_tiến_độ (0-100)
        finished_successfully = Signal(int)     # tổng_số_chương_thành_công
        error_occurred = Signal(str)           # thông_báo_lỗi
    
        def __init__(self, novel_id: str, chapter_links: list, reading_app_service):
            super().__init__()
            self.novel_id = novel_id
            self.chapter_links = chapter_links
            self.reading_app_service = reading_app_service # Nhận service từ tầng Application
    
        def run(self):
            """Hàm chạy trên luồng phụ khi gọi worker.start()"""
            total_chapters = len(self.chapter_links)
            if total_chapters == 0:
                self.finished_successfully.emit(0)
                return
    
            success_count = 0
            
            for index, link_entity in enumerate(self.chapter_links, start=1):
                try:
                    # Gọi xuống Application Service thuộc Reading Context để cào và lưu DB
                    # link_entity.chapter_url là link cần cào, link_entity.id là khóa ngoại
                    self.reading_app_service.download_and_save_chapter(
                        link_entity.id, 
                        link_entity.chapter_url
                    )
                    success_count += 1
                    
                    # Bắn sự kiện cập nhật tiến độ ra ngoài theo thời gian thực
                    self.chapter_downloaded.emit(link_entity.chapter_index, link_entity.title)
                    
                    percent = int((index / total_chapters) * 100)
                    self.progress_updated.emit(percent)
                    
                    # Giả lập độ trễ mạng nhẹ để tránh bị chặn IP (Rate limit)
                    time.sleep(0.5) 
                    
                except Exception as e:
                    self.error_occurred.emit(f"Lỗi chương {link_entity.chapter_index}: {str(e)}")
    
            self.finished_successfully.emit(success_count)
    

## 2\. Lớp ViewModel (Tầng Giao diện - Phần trung gian)

ViewModel chịu trách nhiệm quản lý State (Trạng thái UI) và chuyển đổi dữ liệu từ tầng Application thành định dạng mà View có thể hiển thị trực tiếp. ViewModel không được phép import các widget của PySide6 (như `QPushButton`, `QProgressBar`).
    
    
    # presentation/viewmodels.py
    from PySide6.QtCore import QObject, Signal
    from presentation.workers import ChapterCrawlWorker
    
    class ReaderViewModel(QObject):
        """ViewModel quản lý trạng thái màn hình đọc/cào truyện.
        Tuân thủ DIP: Phụ thuộc vào các Service trừu tượng.
        """
        # Các Trạng thái (State) đẩy ra cho View liên kết (Data Binding)
        status_text_changed = Signal(str)
        progress_val_changed = Signal(int)
        log_added = Signal(str)
        crawl_finished = Signal(bool)
    
        def __init__(self, catalog_app_service, reading_app_service):
            super().__init__()
            self.catalog_app_service = catalog_app_service
            self.reading_app_service = reading_app_service
            self._worker = None
    
        def start_crawling_novel_chapters(self, novel_id: str):
            """Kích hoạt tiến trình cào dữ liệu"""
            self.status_text_changed.emit("Đang lấy danh sách mục lục từ database...")
            self.progress_val_changed.emit(0)
    
            # 1. Lấy danh sách link chương (đã cào từ Catalog Context trước đó)
            chapter_links = self.catalog_app_service.get_all_chapter_links(novel_id)
            
            if not chapter_links:
                self.status_text_changed.emit("Không tìm thấy chương nào cần cào.")
                return
    
            self.status_text_changed.emit(f"Phát hiện {len(chapter_links)} chương. Bắt đầu tải ngầm...")
    
            # 2. Khởi tạo Worker và truyền Application Service vào (Dependency Injection)
            self._worker = ChapterCrawlWorker(novel_id, chapter_links, self.reading_app_service)
            
            # 3. Lắng nghe (Binds) sự kiện từ Worker sang các hàm xử lý trạng thái nội bộ
            self._worker.chapter_downloaded.connect(self._on_chapter_success)
            self._worker.progress_updated.connect(self.progress_val_changed.emit) # Chuyển tiếp signal thẳng tới UI
            self._worker.error_occurred.connect(self._on_chapter_error)
            self._worker.finished_successfully.connect(self._on_crawl_finished)
    
            # 4. Kích hoạt luồng chạy ngầm
            self._worker.start()
    
        def _on_chapter_success(self, index: int, title: str):
            self.status_text_changed.emit(f"Đang tải: Chương {index}")
            self.log_added.emit(f"✔ Đã lưu thành công: {title}")
    
        def _on_chapter_error(self, error_msg: str):
            self.log_added.emit(f"❌ {error_msg}")
    
        def _on_crawl_finished(self, total: int):
            self.status_text_changed.emit(f"Hoàn thành! Đã tải {total} chương về máy.")
            self.crawl_finished.emit(True)
    

## 3\. Lớp View (Tầng Giao diện - Phần hiển thị)

Lớp này thuần túy vẽ giao diện (Widget). Nhiệm vụ duy nhất của nó là nhận tương tác từ người dùng (gọi hàm ViewModel) và nghe các Signal của ViewModel để tự cập nhật chính nó. Nó không chứa bất kỳ một logic tính toán hay xử lý luồng nào.
    
    
    # presentation/views.py
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel, QTextEdit, QMessageBox
    from presentation.viewmodels import ReaderViewModel
    
    class NovelReaderWidget(QWidget):
        """View: Giao diện người dùng bằng PySide6.
        Tuân thủ SRP: Chỉ chứa mã cấu hình giao diện.
        """
        def __init__(self, view_model: ReaderViewModel, novel_id: str):
            super().__init__()
            self.view_model = view_model
            self.novel_id = novel_id # ID truyện hiện tại đang xem
            self.init_ui()
            self.bind_view_model()
    
        def init_ui(self):
            self.setWindowTitle("Trình cào truyện Offline")
            self.resize(500, 400)
            
            layout = QVBoxLayout(self)
            
            self.lbl_status = QLabel("Sẵn sàng cào nội dung", self)
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setValue(0)
            
            self.btn_start = QPushButton("Bắt đầu cào nội dung truyện (Offline)", self)
            self.btn_start.clicked.connect(self.on_btn_start_clicked)
            
            self.txt_log = QTextEdit(self)
            self.txt_log.setReadOnly(True)
            
            layout.addWidget(self.lbl_status)
            layout.addWidget(self.progress_bar)
            layout.addWidget(self.btn_start)
            layout.addWidget(self.txt_log)
    
        def bind_view_model(self):
            """Kết nối Giao diện với ViewModel (Data Binding)"""
            self.view_model.status_text_changed.connect(self.lbl_status.setText)
            self.view_model.progress_val_changed.connect(self.progress_bar.setValue)
            self.view_model.log_added.connect(self.txt_log.append)
            self.view_model.crawl_finished.connect(self.on_finished)
    
        def on_btn_start_clicked(self):
            self.btn_start.setEnabled(False) # Vô hiệu hóa nút bấm tránh bấm trùng
            self.view_model.start_crawling_novel_chapters(self.novel_id)
    
        def on_finished(self, success: bool):
            self.btn_start.setEnabled(True)
            QMessageBox.information(self, "Thông báo", "Tải dữ liệu truyện hoàn tất!")
    

* * *

## Đề xuất Tối ưu Tối đa Hiệu năng cho Tiến Trình Này

  1. Sử dụng Bulk Commit (Giao dịch DB lớn) ở tầng Hạ tầng:

     * Thay vì mỗi lần cào xong 1 chương lại mở kết nối DB để `INSERT` (gây thắt nút cổ chai I/O đĩa cứng), hãy thiết lập mã nguồn DB lưu tạm vào bộ nhớ cache. Cứ sau mỗi 20 chương cào xong, hoặc sau 5 giây, mới thực hiện một câu lệnh `COMMIT` xuống ổ cứng một lần. Tốc độ lưu sẽ tăng lên gấp 10-20 lần.

  2. Hủy luồng an toàn (Graceful Shutdown):

     * Nếu người dùng đột ngột tắt cửa sổ PySide6 (`closeEvent`) khi `QThread` đang chạy, ứng dụng có thể bị sập (Crash - Segmentation Fault).
     * Giải pháp: Trong `ReaderViewModel`, ghi đè hàm hủy để kiểm tra nếu `self._worker.isRunning()`, hãy phát tín hiệu dừng ngầm và đợi luồng kết thúc (`self._worker.quit(); self._worker.wait()`) trước khi đóng hẳn ứng dụng.




Tiếp theo, bạn đã có giải pháp nào cho việc quản lý Proxy hoặc tự động đổi User-Agent ở tầng Infrastructure để chống bị các website truyện lớn (như chặn Cloudflare) khóa IP khi chạy cào đa luồng tốc độ cao chưa?