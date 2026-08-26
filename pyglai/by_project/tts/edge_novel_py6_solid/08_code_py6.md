Dưới đây là toàn bộ mã nguồn PySide6 hoàn chỉnh, đã tích hợp menu chọn Thể loại truyện (Preset) tự động áp thông số `Rate` (Tốc độ) và `Pitch` (Cao độ) tối ưu cho cả tiếng Anh lẫn tiếng Việt.

Giao diện cũng được nâng cấp để hiển thị danh sách giọng đọc trực quan theo từng ngôn ngữ.

## Toàn bộ code file `app.py`
    
    
    import sys
    import asyncio
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QTextEdit, QComboBox, 
                                 QPushButton, QFileDialog, QMessageBox, QGroupBox)
    from PySide6.QtCore import Qt, QThread, Signal
    import edge_tts
    
    # 1. Danh sách giọng đọc hay nhất phân loại theo Ngôn ngữ
    VOICES = {
        # TIẾNG ANH
        "en-US-AriaNeural (Nữ Mỹ - Truyền cảm)": "en-US-AriaNeural",
        "en-US-JennyNeural (Nữ Mỹ - Cổ tích nhẹ nhàng)": "en-US-JennyNeural",
        "en-US-GuyNeural (Nam Mỹ - Trầm ấm)": "en-US-GuyNeural",
        "en-US-SteffanNeural (Nam Mỹ - Cuốn hút)": "en-US-SteffanNeural",
        "en-GB-SoniaNeural (Nữ Anh - Cổ điển)": "en-GB-SoniaNeural",
        "en-GB-RyanNeural (Nam Anh - Tự nhiên)": "en-GB-RyanNeural",
        # TIẾNG VIỆT
        "vi-VN-HoaiAnNeural (Nữ Việt - Dịu dàng)": "vi-VN-HoaiAnNeural",
        "vi-VN-NamMinhNeural (Nam Việt - Trầm hùng)": "vi-VN-NamMinhNeural"
    }
    
    # 2. Bảng Preset thông số tối ưu cho từng Thể loại truyện
    STORY_PRESETS = {
        "Cổ tích / Thần thoại (Fairy Tales)": {"rate": "-12%", "pitch": "+3Hz"},
        "Kinh dị / Trinh thám (Horror / Thriller)": {"rate": "-16%", "pitch": "-4Hz"},
        "Ngôn tình / Tâm lý xã hội (Drama / Romance)": {"rate": "-15%", "pitch": "-1Hz"},
        "Kiếm hiệp / Tiên hiệp (Fantasy Martial Arts)": {"rate": "-13%", "pitch": "-3Hz"},
        "Truyện cười / Thiếu nhi (Fables / Kids)": {"rate": "-6%", "pitch": "+5Hz"},
        "Mặc định / Phổ thông (Default)": {"rate": "+0%", "pitch": "+0Hz"}
    }
    
    # Worker Thread xử lý chuyển đổi ngầm để giao diện không bị treo
    class TTSWorker(QThread):
        finished = Signal(bool, str)
    
        def __init__(self, text, voice, rate, pitch, file_path):
            super().__init__()
            self.text = text
            self.voice = voice
            self.rate = rate
            self.pitch = pitch
            self.file_path = file_path
    
        def run(self):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Truyền đầy đủ text, voice, rate và pitch vào edge-tts
                communicate = edge_tts.Communicate(
                    text=self.text, 
                    voice=self.voice, 
                    rate=self.rate, 
                    pitch=self.pitch
                )
                loop.run_until_complete(communicate.save(self.file_path))
                loop.close()
                
                self.finished.emit(True, f"Đã xuất file truyện thành công tại:\n{self.file_path}")
            except Exception as e:
                self.finished.emit(False, str(e))
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Edge-TTS Advance Story Reader")
            self.setMinimumSize(650, 550)
            
            # Widget chính
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(15)
    
            # --- 1. Ô nhập văn bản truyện ---
            lbl_text = QLabel("Nhập văn bản truyện (Tiếng Anh hoặc Tiếng Việt):")
            lbl_text.setStyleSheet("font-weight: bold; font-size: 13px;")
            main_layout.addWidget(lbl_text)
    
            self.text_area = QTextEdit()
            self.text_area.setPlaceholderText("Dán nội dung truyện của bạn vào đây...")
            self.text_area.setText("Once upon a time, in a deep, magical forest, there lived a little golden bird...")
            main_layout.addWidget(self.text_area)
    
            # --- 2. Khung cấu hình âm thanh (Cài đặt Preset & Giọng đọc) ---
            config_group = QGroupBox("Cấu hình giọng đọc nâng cao")
            config_layout = QVBoxLayout(config_group)
            
            # Dòng chứa Thể loại và Giọng đọc
            row_layout = QHBoxLayout()
    
            # Chọn Thể loại truyện (Preset)
            vbox_genre = QVBoxLayout()
            vbox_genre.addWidget(QLabel("1. Chọn thể loại truyện (Preset):"))
            self.genre_combo = QComboBox()
            self.genre_combo.addItems(list(STORY_PRESETS.keys()))
            self.genre_combo.currentTextChanged.connect(self.update_preset_info)
            vbox_genre.addWidget(self.genre_combo)
            row_layout.addLayout(vbox_genre, stretch=1)
    
            # Chọn Giọng đọc
            vbox_voice = QVBoxLayout()
            vbox_voice.addWidget(QLabel("2. Chọn giọng AI phù hợp:"))
            self.voice_combo = QComboBox()
            self.voice_combo.addItems(list(VOICES.keys()))
            vbox_voice.addWidget(self.voice_combo)
            row_layout.addLayout(vbox_voice, stretch=1)
    
            config_layout.addLayout(row_layout)
    
            # Nhãn hiển thị thông số Rate/Pitch đang áp dụng
            self.lbl_info = QLabel("Thông số áp dụng: Tốc độ (Rate): -12% | Cao độ (Pitch): +3Hz")
            self.lbl_info.setStyleSheet("color: #555555; font-size: 11px; font-weight: bold;")
            config_layout.addWidget(self.lbl_info)
    
            main_layout.addWidget(config_group)
    
            # Cập nhật nhãn thông số mặc định ngay khi mở app
            self.update_preset_info(self.genre_combo.currentText())
    
            # --- 3. Nhãn hiển thị trạng thái xử lý ---
            self.status_label = QLabel("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic; font-size: 12px;")
            self.status_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.status_label)
    
            # --- 4. Nút bấm xuất file MP3 ---
            self.btn_convert = QPushButton("XUẤT FILE AUDIO (MP3)")
            self.btn_convert.setMinimumHeight(50)
            self.btn_convert.setStyleSheet("""
                QPushButton {
                    background-color: #007bff; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 14px; 
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #0069d9; }
                QPushButton:disabled { background-color: #6c757d; }
            """)
            self.btn_convert.clicked.connect(self.start_conversion)
            main_layout.addWidget(self.btn_convert)
    
        def update_preset_info(self, genre_name):
            """Cập nhật nhãn văn bản hiển thị thông số Rate/Pitch khi người dùng đổi thể loại"""
            preset = STORY_PRESETS[genre_name]
            self.lbl_info.setText(f"Thông số áp dụng: Tốc độ (Rate): {preset['rate']} | Cao độ (Pitch): {preset['pitch']}")
    
        def start_conversion(self):
            text = self.text_area.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung truyện!")
                return
    
            # Đọc cấu hình được chọn từ giao diện
            selected_voice_label = self.voice_combo.currentText()
            voice_code = VOICES[selected_voice_label]
    
            selected_genre = self.genre_combo.currentText()
            preset = STORY_PRESETS[selected_genre]
    
            # Mở hộp thoại chọn thư mục và đặt tên file lưu
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Chọn vị trí lưu file truyện", "", "Audio files (*.mp3)"
            )
            if not file_path:
                return
    
            # Khóa nút bấm và đổi trạng thái giao diện
            self.btn_convert.setEnabled(False)
            self.status_label.setText("Đang chạy AI chuyển đổi văn bản sang âm thanh... Vui lòng chờ.")
            self.status_label.setStyleSheet("color: #e67e22; font-style: italic;")
    
            # Kích hoạt Thread chạy ngầm với đầy đủ tham số rate và pitch
            self.worker = TTSWorker(text, voice_code, preset["rate"], preset["pitch"], file_path)
            self.worker.finished.connect(self.on_conversion_finished)
            self.worker.start()
    
        def on_conversion_finished(self, success, message):
            # Mở khóa giao diện sau khi chạy xong
            self.btn_convert.setEnabled(True)
            self.status_label.setText("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
    
            if success:
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể tạo file âm thanh:\n{message}")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

## Cách chạy và đóng gói nhanh bằng `uv`

Nếu bạn đã quen dùng `uv` từ bước trước, chỉ cần chạy các lệnh sau để kiểm tra và đóng gói file code này:

  1. Chạy thử giao diện:
         
         uv run app.py
         

  2. Đóng gói thành file `.exe` duy nhất:
         
         uv run --with PySide6 --with edge-tts --with pyinstaller pyinstaller --noconsole --onefile --name="StoryReader_Pro" app.py
         




Sau khi đóng gói xong, bạn chỉ cần vào thư mục `dist` lấy file `StoryReader_Pro.exe` ra sử dụng lâu dài. Chúc bạn tạo được những file âm thanh đọc truyện thật ưng ý!