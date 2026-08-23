Dưới đây là mã nguồn hoàn chỉnh kết hợp PySide6, Asyncio (thông qua `qasync`) và Kiến trúc hướng sự kiện (EDA) để tạo ra một công cụ cào truyện từ `truyenfull.live`.

Giao diện sẽ chạy mượt mà, cập nhật tiến độ theo thời gian thực và không bao giờ bị đơ (No Freeze) nhờ tận dụng thế mạnh của lập trình bất đồng bộ.

## Cấu trúc thiết kế EDA của ứng dụng

  1. Event Broker (`CrawlEventBroker`): Lớp trung gian quản lý các tín hiệu (Signals) như báo cáo tiến độ, thông báo lỗi, hay cập nhật nội dung chương vừa cào.
  2. Event Producer / Consumer (`CrawlService`): Lớp xử lý Logic cào truyện (Bất đồng bộ). Nó nhận sự kiện bắt đầu từ UI, tự chạy và phát sự kiện cập nhật trạng thái liên tục lên Broker.
  3. Event Producer / Consumer (`CrawlWindow`): Giao diện người dùng (UI). Nó phát sự kiện yêu cầu cào truyện, đồng thời lắng nghe Broker để cập nhật thanh tiến trình (Progress Bar) và Nhật ký (Log).



* * *

## Mã nguồn Python triển khai (`app.py`)

Trước khi chạy, bạn cần cài đặt các thư viện bổ trợ sau:
    
    
    pip install PySide6 qasync beautifulsoup4 cloudscraper
    
    
    
    import sys
    import asyncio
    from bs4 import BeautifulSoup
    import cloudscraper
    from PySide6.QtCore import QObject, Signal, Slot
    from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                                   QPushButton, QProgressBar, QTextEdit, QVBoxLayout, QHBoxLayout)
    from qasync import QEventLoop, asyncSlot
    
    # ==========================================
    # 1. EVENT BROKER (Trung tâm điều phối Sự kiện)
    # ==========================================
    class CrawlEventBroker(QObject):
        # Định nghĩa các sự kiện có thể xảy ra trong hệ thống
        log_updated = Signal(str)         # Gửi thông điệp log ra màn hình
        progress_updated = Signal(int)    # Cập nhật phần trăm tiến độ (%)
        crawl_finished = Signal(str)      # Báo cáo đã hoàn thành kèm đường dẫn file
        crawl_error = Signal(str)         # Báo cáo lỗi hệ thống xảy ra
    
    GLOBAL_BROKER = CrawlEventBroker()
    
    # ==========================================
    # 2. BUSINESS LOGIC: CORE CRAWL SERVICE (Chạy Async)
    # ==========================================
    class CrawlService:
        def __init__(self):
            # Sử dụng cloudscraper để dễ dàng vượt qua Cloudflare nếu có
            self.scraper = cloudscraper.create_scraper()
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
    
        async def start_crawl_task(self, start_url: str, output_file: str):
            """Hàm core thực hiện cào truyện bất đồng bộ mà không block UI"""
            current_url = start_url
            chapter_count = 0
            
            GLOBAL_BROKER.log_updated.emit("🚀 Bắt đầu tiến trình cào dữ liệu...")
            
            try:
                # Mở file ghi dữ liệu bằng phương thức đồng bộ (hoặc aiofiles nếu muốn async thuần)
                with open(output_file, "w", encoding="utf-8") as f:
                    while current_url:
                        GLOBAL_BROKER.log_updated.emit(f"📖 Đang tải: {current_url}")
                        
                        # Chạy request trong Executor để tránh block Event Loop chính
                        loop = asyncio.get_event_loop()
                        response = await loop.run_in_executor(
                            None, lambda: self.scraper.get(current_url, headers=self.headers, timeout=10)
                        )
                        
                        if response.status_code != 200:
                            GLOBAL_BROKER.crawl_error.emit(f"❌ Lỗi kết nối HTTP: {response.status_code}")
                            break
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Trích xuất tiêu đề chương
                        title_element = soup.find('a', class_='chapter-title')
                        chapter_title = title_element.get_text(strip=True) if title_element else f"Chương {chapter_count + 1}"
                        
                        # Trích xuất nội dung
                        content_div = soup.find('div', class_='chapter-c')
                        if not content_div:
                            GLOBAL_BROKER.crawl_error.emit("❌ Không tìm thấy thẻ chứa nội dung truyện (.chapter-c)")
                            break
                        
                        # Định dạng lại xuống dòng thẻ <br>
                        for br in content_div.find_all("br"):
                            br.replace_with("\n")
                        
                        chapter_content = content_div.get_text()
                        
                        # Ghi dữ liệu vào file
                        f.write(f"\n\n=== {chapter_title} ===\n\n")
                        f.write(chapter_content.strip())
                        
                        chapter_count += 1
                        GLOBAL_BROKER.log_updated.emit(f"✅ Đã cào xong: {chapter_title}")
                        
                        # Giả lập cập nhật Progress Bar (ở đây tạm tăng tiến độ ảo theo số chương)
                        # Thực tế bạn có thể lấy tổng số chương trước để tính toán % chính xác
                        progress_val = min(chapter_count * 5, 100) 
                        GLOBAL_BROKER.progress_updated.emit(progress_val)
                        
                        # Tìm link chương tiếp theo
                        next_button = soup.find('a', id='next_chap')
                        if next_button and 'href' in next_button.attrs and 'javascript:void' not in next_button['href']:
                            current_url = next_button['href']
                            # Tránh spam server quá nhanh gây khóa IP (Crawl Delay)
                            await asyncio.sleep(1.5)
                        else:
                            GLOBAL_BROKER.log_updated.emit("🏁 Đã chạm tới chương cuối cùng của bộ truyện!")
                            current_url = None
                
                GLOBAL_BROKER.crawl_finished.emit(output_file)
                
            except Exception as e:
                GLOBAL_BROKER.crawl_error.emit(f"💥 Lỗi hệ thống: {str(e)}")
    
    # ==========================================
    # 3. USER INTERFACE: PYSIDE6 VIEW
    # ==========================================
    class CrawlWindow(QWidget):
        def __init__(self, service: CrawlService):
            super().__init__()
            self.service = service
            self.init_ui()
            self.subscribe_events()
    
        def init_ui(self):
            self.setWindowTitle("Tool Cào Truyện TruyenFull.live - Mô hình EDA")
            self.resize(650, 450)
            
            # Các thành phần UI
            self.lbl_url = QLabel("Link chương 1:", self)
            self.txt_url = QLineEdit(self)
            self.txt_url.setPlaceholderText("https://truyenfull.live")
            
            self.btn_start = QPushButton("Bắt đầu cào", self)
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setValue(0)
            
            self.log_output = QTextEdit(self)
            self.log_output.setReadOnly(True)
            
            # Bố cục giao diện Layout
            url_layout = QHBoxLayout()
            url_layout.addWidget(self.lbl_url)
            url_layout.addWidget(self.txt_url)
            
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(url_layout)
            main_layout.addWidget(self.btn_start)
            main_layout.addWidget(self.progress_bar)
            main_layout.addWidget(self.log_output)
            
            # UI phát tín hiệu kích hoạt tiến trình cào khi Click chuột
            self.btn_start.clicked.connect(self.on_click_start)
    
        def subscribe_events(self):
            """UI Đăng ký lắng nghe (Subscribe) các sự kiện từ Broker phát ra"""
            GLOBAL_BROKER.log_updated.connect(self.handle_log_update)
            GLOBAL_BROKER.progress_updated.connect(self.handle_progress_update)
            GLOBAL_BROKER.crawl_finished.connect(self.handle_crawl_finished)
            GLOBAL_BROKER.crawl_error.connect(self.handle_crawl_error)
    
        @asyncSlot() # Định nghĩa hàm nhận sự kiện click dạng AsyncSlot của qasync
        async def on_click_start(self):
            url = self.txt_url.text().strip()
            if not url:
                self.log_output.append("⚠️ Vui lòng nhập link chương 1 để bắt đầu!")
                return
                
            self.btn_start.setEnabled(False)
            self.progress_bar.setValue(0)
            self.log_output.clear()
            
            # Kích hoạt Core Logic chạy ngầm không block Main UI
            asyncio.ensure_future(self.service.start_crawl_task(url, "truyen_da_cao.txt"))
    
        # Các hàm Callback xử lý sự kiện khi lắng nghe Broker thành công
        @Slot(str)
        def handle_log_update(self, message):
            self.log_output.append(message)
    
        @Slot(int)
        def handle_progress_update(self, value):
            self.progress_bar.setValue(value)
    
        @Slot(str)
        def handle_crawl_finished(self, filepath):
            self.log_output.append(f"\n🎉 HOÀN THÀNH! Truyện đã được lưu an toàn tại: {filepath}")
            self.btn_start.setEnabled(True)
            self.progress_bar.setValue(100)
    
        @Slot(str)
        def handle_crawl_error(self, error_msg):
            self.log_output.append(f"\n{error_msg}")
            self.btn_start.setEnabled(True)
    
    # ==========================================
    # 4. CHẠY CHƯƠNG TRÌNH (KHỞI TẠO EVENT LOOP)
    # ==========================================
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        # Ép PySide6 và Asyncio chạy chung trên một kiến trúc Event Loop của qasync
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Khởi tạo Service xử lý logic và View hiển thị độc lập
        crawl_service = CrawlService()
        window = CrawlWindow(crawl_service)
        window.show()
        
        with loop:
            loop.run_forever()
    

* * *

## Điểm cộng kiến trúc của mã nguồn trên:

  1. Tuyệt đối không đơ giao diện: Khi đang cào dữ liệu qua mạng, bạn vẫn có thể di chuyển cửa sổ ứng dụng, bôi đen văn bản trong ô Nhật ký (Log) bình thường mà không gặp tình trạng `Not Responding`.
  2. Sự kết hợp hoàn hảo: Nhờ `qasync` kết hợp với `run_in_executor`, luồng xử lý mạng đồng bộ của thư viện `cloudscraper` được bao bọc cẩn thận và biến thành tác vụ bất đồng bộ (`async`) một cách mượt mà.
  3. Mô hình EDA chuẩn chỉ: Nếu sau này bạn muốn đổi tính năng từ cào truyện lưu file thành Cào truyện đẩy trực tiếp lên cơ sở dữ liệu (MySQL / MongoDB), bạn chỉ cần thay đổi mã nguồn duy nhất tại hàm `start_crawl_task` trong lớp `CrawlService`. Phần giao diện UI hoàn toàn không phải sửa một dòng code nào.



Để công cụ này hoàn thiện hơn, bạn có muốn tích hợp thêm Nút Tạm dừng (Pause / Resume) hay cấu hình Tự động gộp các file txt thành file định dạng sách EPUB để dễ đọc trên điện thoại không?