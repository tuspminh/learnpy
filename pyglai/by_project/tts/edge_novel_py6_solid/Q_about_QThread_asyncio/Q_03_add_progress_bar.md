Để hiển thị thanh tiến trình (QProgressBar) chạy liên tục (dạng chạy qua chạy lại để báo hiệu hệ thống đang xử lý, gọi là _Indeterminate Progress Bar_) hoặc cập nhật trạng thái tải, bạn chỉ cần thực hiện 3 bước đơn giản dưới đây.

* * *

## 1\. Cập nhật mã nguồn Worker (`TTSWorker`)

Mã nguồn của Worker được giữ nguyên cấu trúc kết hợp giữa `QThread` và `asyncio`. Chúng ta chỉ cần đảm bảo các tín hiệu được phát đi chính xác.
    
    
    import asyncio
    import edge_tts
    from PySide6.QtCore import QThread, Signal
    
    class TTSWorker(QThread):
        # Tín hiệu trả về kết quả: (Trạng thái thành công, Tin nhắn/Đường dẫn file)
        tts_finished = Signal(bool, str) 
    
        def __init__(self, text, voice, rate, file_path):
            super().__init__()
            self.text = text
            self.voice = voice
            self.rate = rate
            self.file_path = file_path
    
        def run(self):
            loop = None
            try:
                # Tạo và thiết lập loop asyncio cho thread ngầm
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                communicate = edge_tts.Communicate(self.text, self.voice, rate=self.rate)
                loop.run_until_complete(communicate.save(self.file_path))
                
                # Phát tín hiệu THÀNH CÔNG
                self.tts_finished.emit(True, self.file_path)
                
            except Exception as e:
                # Phát tín hiệu THẤT BẠI kèm lỗi
                self.tts_finished.emit(False, str(e))
                
            finally:
                if loop and loop.is_open():
                    loop.close()
    

* * *

## 2\. Giao diện điều khiển (MainWindow) tích hợp QProgressBar

Trong class giao diện, chúng ta sẽ thêm một `QProgressBar`.

  * Khi bắt đầu chuyển đổi: Đặt thanh tiến trình về chế độ chạy liên tục (giá trị tối đa và tối thiểu bằng `0`).
  * Khi hoàn thành: Ẩn hoặc dừng thanh tiến trình.


    
    
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QVBoxLayout, QWidget, QMessageBox
    from PySide6.QtCore import Qt
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Edge-TTS với QProgressBar")
            self.resize(400, 150)
    
            # 1. Tạo các thành phần giao diện
            self.btn_start = QPushButton("Bắt đầu chuyển đổi văn bản", self)
            
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(False) # Ẩn phần trăm chữ (vì đang chạy vô định)
            self.progress_bar.hide() # Mặc định ẩn đi, khi nào chạy mới hiện
    
            # 2. Sắp xếp bố cục (Layout)
            layout = QVBoxLayout()
            layout.addWidget(self.btn_start)
            layout.addWidget(self.progress_bar)
    
            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)
    
            # 3. Kết nối sự kiện nút bấm
            self.btn_start.clicked.connect(self.start_tts_process)
            
            # Biến toàn cục trong class để giữ luồng worker
            self.worker = None
    
        def start_tts_process(self):
            """Kích hoạt khi người dùng bấm nút"""
            # Vô hiệu hóa nút bấm để tránh bấm liên tục gây crash
            self.btn_start.setEnabled(False)
            
            # Hiển thị thanh tiến trình và bật chế độ chạy qua chạy lại (Animation)
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0) # Mẹo tạo thanh tiến trình chạy vô định trong Qt
    
            # Khởi tạo Worker chạy ngầm
            text_data = "Xin chào, đây là đoạn văn bản dài đang được xử lý ngầm bằng thư viện edge-tts mà không làm đơ giao diện của bạn."
            self.worker = TTSWorker(text_data, "vi-VN-HoaiAnNeural", "+0%", "truyen_audio.mp3")
            
            # Kết nối tín hiệu phản hồi kết quả
            self.worker.tts_finished.connect(self.handle_tts_result)
            
            # Tự động xóa vùng nhớ giải phóng RAM khi Thread kết thúc
            self.worker.finished.connect(self.worker.deleteLater)
            
            # Khởi động thread
            self.worker.start()
    
        def handle_tts_result(self, success, result_message):
            """Xử lý kết quả trả về từ luồng ngầm"""
            # 1. Khôi phục trạng thái giao diện
            self.btn_start.setEnabled(True)
            self.progress_bar.setRange(0, 100) # Đưa thanh tiến trình về trạng thái tĩnh
            self.progress_bar.setValue(100)    # Đầy thanh
            self.progress_bar.hide()           # Ẩn thanh tiến trình đi
    
            # 2. Hiển thị thông báo kết quả cho người dùng
            if success:
                QMessageBox.information(
                    self, 
                    "Thành công", 
                    f"Quá trình chuyển đổi hoàn tất!\nFile đã lưu tại: {result_message}"
                )
            else:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    f"Đã xảy ra lỗi trong quá trình xử lý:\n{result_message}"
                )
    
    # Chạy ứng dụng
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

* * *

## 📝 Giải thích cơ chế điều khiển tiến trình:

  1. `self.progress_bar.setRange(0, 0)`: Đây là tính năng cực kỳ hay của Qt. Khi bạn đặt cả giá trị tối thiểu (Minimum) và tối đa (Maximum) đều bằng `0`, thanh tiến trình sẽ tự động chuyển sang chế độ Indeterminate (Hiệu ứng dải màu chạy qua chạy lại liên tục). Nó rất phù hợp cho các tác vụ tải dữ liệu từ Internet (như `edge-tts`) vì chúng ta không biết trước file audio sẽ mất bao nhiêu giây để tải xong.
  2. `self.progress_bar.hide()` và `show()`: Giúp giao diện gọn gàng hơn. Thanh trạng thái chỉ xuất hiện khi hệ thống thực sự làm việc và biến mất khi đã xong.



Nếu bạn cần tối ưu thêm như chia nhỏ văn bản dài thành từng câu để cập nhật phần trăm chính xác (Ví dụ: `Đang chạy câu 3/10 (30%)`), hãy phản hồi để tôi hướng dẫn cách bóc tách chuỗi nhé!