Dưới đây là mã nguồn giao diện đã được chuyển đổi hoàn toàn sang PySide6 (Qt Python). Giao diện PySide6 mang lại cảm giác hiện đại, chuyên nghiệp và có hiệu năng xử lý mượt mà hơn.

## 1\. Cài đặt thư viện

Bạn cần cài đặt thư viện `PySide6` và `edge-tts`. Chạy lệnh sau trong Terminal / Command Prompt:
    
    
    pip install PySide6 edge-tts
    

## 2\. Đoạn code giao diện PySide6 (`app.py`)
    
    
    import sys
    import asyncio
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QTextEdit, QComboBox, 
                                 QSlider, QPushButton, QFileDialog, QMessageBox)
    from PySide6.QtCore import Qt, QThread, Signal
    import edge_tts
    
    # Danh sách giọng đọc hay nhất cho truyện cổ tích/kể chuyện
    VOICES = {
        "Nữ Mỹ (Aria) - Truyền cảm": "en-US-AriaNeural",
        "Nữ Mỹ (Jenny) - Cổ tích nhẹ nhàng": "en-US-JennyNeural",
        "Nam Mỹ (Guy) - Trầm ấm": "en-US-GuyNeural",
        "Nam Mỹ (Steffan) - Cuốn hút": "en-US-SteffanNeural",
        "Nữ Anh (Sonia) - Sang trọng, cổ điển": "en-GB-SoniaNeural",
        "Nam Anh (Ryan) - Tự nhiên như người thật": "en-GB-RyanNeural",
    }
    
    # Worker Thread giúp xử lý edge-tts chạy ngầm, không gây đơ giao diện Qt
    class TTSWorker(QThread):
        finished = Signal(bool, str) # Trả về trạng thái (Thành công/Thất bại, Tin nhắn)
    
        def __init__(self, text, voice, rate, file_path):
            super().__init__()
            self.text = text
            self.voice = voice
            self.rate = rate
            self.file_path = file_path
    
        def run(self):
            try:
                # Tạo event loop mới cho thread chạy ngầm
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                communicate = edge_tts.Communicate(self.text, self.voice, rate=self.rate)
                loop.run_until_complete(communicate.save(self.file_path))
                loop.close()
                
                self.finished.emit(True, f"Đã lưu file truyện tại:\n{self.file_path}")
            except Exception as e:
                self.finished.emit(False, str(e))
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Edge-TTS Story Reader (PySide6)")
            self.setMinimumSize(600, 500)
            
            # Giao diện chính
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(12)
    
            # 1. Ô nhập văn bản truyện
            lbl_text = QLabel("Nhập hoặc dán truyện tiếng Anh vào đây:")
            lbl_text.setStyleSheet("font-weight: bold; font-size: 13px;")
            main_layout.addWidget(lbl_text)
    
            self.text_area = QTextEdit()
            self.text_area.setPlaceholderText("Once upon a time, in a magical land far away...")
            self.text_area.setText("Once upon a time, in a deep, magical forest, there lived a little golden bird...")
            main_layout.addWidget(self.text_area)
    
            # 2. Khung cấu hình (Giọng đọc & Tốc độ)
            config_layout = QHBoxLayout()
    
            # Chọn giọng
            vbox_voice = QVBoxLayout()
            vbox_voice.addWidget(QLabel("Chọn giọng kể chuyện:"))
            self.voice_combo = QComboBox()
            self.voice_combo.addItems(list(VOICES.keys()))
            vbox_voice.addWidget(self.voice_combo)
            config_layout.addLayout(vbox_voice, stretch=2)
    
            # Thanh trượt chỉnh tốc độ
            vbox_speed = QVBoxLayout()
            self.lbl_speed = QLabel("Tốc độ: -10%")
            vbox_speed.addWidget(self.lbl_speed)
            
            self.rate_slider = QSlider(Qt.Horizontal)
            self.rate_slider.setMinimum(-50)
            self.rate_slider.setMaximum(50)
            self.rate_slider.setValue(-10) # Mặc định giảm 10% để giọng thong thả
            self.rate_slider.valueChanged.connect(self.update_speed_label)
            vbox_speed.addWidget(self.rate_slider)
            config_layout.addLayout(vbox_speed, stretch=1)
    
            main_layout.addLayout(config_layout)
    
            # 3. Nhãn hiển thị trạng thái
            self.status_label = QLabel("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
            self.status_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.status_label)
    
            # 4. Nút bấm xuất file Audio
            self.btn_convert = QPushButton("XUẤT FILE AUDIO (MP3)")
            self.btn_convert.setMinimumHeight(45)
            self.btn_convert.setStyleSheet("""
                QPushButton {
                    background-color: #28a745; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 14px; 
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #218838; }
                QPushButton:disabled { background-color: #6c757d; }
            """)
            self.btn_convert.clicked.connect(self.start_conversion)
            main_layout.addWidget(self.btn_convert)
    
        def update_speed_label(self, value):
            self.lbl_speed.setText(f"Tốc độ: {value:+d}%" if value != 0 else "Tốc độ: Phổ thông")
    
        def start_conversion(self):
            text = self.text_area.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung truyện!")
                return
    
            # Lấy thông số từ giao diện
            selected_label = self.voice_combo.currentText()
            voice_code = VOICES[selected_label]
            speed_value = self.rate_slider.value()
            rate_str = f"{speed_value:+d}%" if speed_value != 0 else "+0%"
    
            # Hộp thoại chọn nơi lưu file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Chọn nơi lưu file truyện", "", "Audio files (*.mp3)"
            )
            if not file_path:
                return
    
            # Khóa giao diện & Cập nhật trạng thái
            self.btn_convert.setEnabled(False)
            self.status_label.setText("Đang xử lý tạo file MP3... Vui lòng đợi.")
            self.status_label.setStyleSheet("color: blue; font-style: italic;")
    
            # Chạy Edge-TTS qua QThread ngầm
            self.worker = TTSWorker(text, voice_code, rate_str, file_path)
            self.worker.finished.connect(self.on_conversion_finished)
            self.worker.start()
    
        def on_conversion_finished(self, success, message):
            # Mở khóa giao diện
            self.btn_convert.setEnabled(True)
            self.status_label.setText("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
    
            if success:
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra:\n{message}")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

## Ưu điểm của phiên bản PySide6 này:

  * Giao diện mượt mà tuyệt đối: Khác với Tkinter, phiên bản này tách biệt tác vụ tạo file `edge-tts` sang một luồng xử lý ngầm biệt lập (`QThread`), giúp ứng dụng không bao giờ bị đứng/đơ ứng dụng khi bạn xuất những đoạn truyện dài.
  * Tự động cập nhật: Thanh trượt tốc độ sẽ tự hiển thị con số `+10%`, `-15%` ngay khi bạn kéo chuột để bạn dễ căn chỉnh.



Nếu bạn muốn tôi hướng dẫn cách đóng gói file PySide6 này thành file `.exe` standalone (chạy độc lập không cần cài Python trên máy khác), hãy cho tôi biết nhé!