Dưới đây là hướng dẫn tạo một ứng dụng phát âm thanh đơn giản bằng PySide6 sử dụng module `QMediaPlayer` và `QAudioOutput`.

Trong PySide6, để phát được âm thanh, bạn cần kết hợp `QMediaPlayer` (bộ điều khiển phát) và `QAudioOutput` (bộ phần cứng đầu ra).

## 1\. Cài đặt thư viện

Nếu chưa cài đặt PySide6, bạn chạy lệnh sau trong terminal:
    
    
    pip install PySide6
    

## 2\. Mã nguồn ứng dụng phát Audio

Dưới đây là đoạn code hoàn chỉnh tạo giao diện gồm nút Chọn file, Phát (Play), Tạm dừng (Pause), và Dừng lại (Stop).
    
    
    import sys
    from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl
    
    class AudioPlayerApp(QWidget):
        def __init__(self):
            super().__init__()
            
            # Thiết lập cửa sổ chính
            self.setWindowTitle("Ứng dụng Phát Audio - PySide6")
            self.resize(400, 150)
            
            # Khởi tạo các thành phần Audio
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            
            # Biến lưu đường dẫn file
            self.file_url = None
            
            # Khởi tạo Giao diện (UI)
            self.init_ui()
    
        def init_ui(self):
            # Tạo các Widget
            self.lbl_status = QLabel("Vui lòng chọn một file âm thanh (.mp3, .wav, ...)")
            self.lbl_status.setWordWrap(True)
            
            self.btn_open = QPushButton("Chọn File")
            self.btn_play = QPushButton("Play")
            self.btn_pause = QPushButton("Pause")
            self.btn_stop = QPushButton("Stop")
            
            # Vô hiệu hóa các nút phát khi chưa chọn file
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            
            # Sắp xếp bố cục (Layout)
            layout_buttons = QHBoxLayout()
            layout_buttons.addWidget(self.btn_play)
            layout_buttons.addWidget(self.btn_pause)
            layout_buttons.addWidget(self.btn_stop)
            
            layout_main = QVBoxLayout()
            layout_main.addWidget(self.btn_open)
            layout_main.addWidget(self.lbl_status)
            layout_main.addLayout(layout_buttons)
            
            self.setLayout(layout_main)
            
            # Kết nối sự kiện (Signals & Slots)
            self.btn_open.clicked.connect(self.open_file)
            self.btn_play.clicked.connect(self.play_audio)
            self.btn_pause.clicked.connect(self.pause_audio)
            self.btn_stop.clicked.connect(self.stop_audio)
    
        def open_file(self):
            # Mở hộp thoại chọn file âm thanh
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Chọn File Âm Thanh", "", "Audio Files (*.mp3 *.wav *.ogg *.m4a)"
            )
            
            if file_path:
                self.file_url = QUrl.fromLocalFile(file_path)
                self.player.setSource(self.file_url)
                
                # Cập nhật giao diện
                self.lbl_status.setText(f"Đang chọn: {file_path.split('/')[-1]}")
                self.btn_play.setEnabled(True)
                self.btn_pause.setEnabled(True)
                self.btn_stop.setEnabled(True)
    
        def play_audio(self):
            self.player.play()
            self.lbl_status.setText("Trạng thái: Đang phát...")
    
        def pause_audio(self):
            self.player.pause()
            self.lbl_status.setText("Trạng thái: Đang tạm dừng.")
    
        def stop_audio(self):
            self.player.stop()
            self.lbl_status.setText("Trạng thái: Đã dừng.")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        player_app = AudioPlayerApp()
        player_app.show()
        sys.exit(app.exec())
    

## 3\. Giải thích các điểm cốt lõi:

  * `QMediaPlayer`: Đối tượng chịu trách nhiệm đọc và điều khiển luồng dữ liệu media (Play, Pause, Stop).
  * `QAudioOutput`: Đối tượng phụ trách kết nối với phần cứng âm thanh (loa/tai nghe) của máy tính. Nếu thiếu dòng `self.player.setAudioOutput(self.audio_output)`, ứng dụng sẽ chạy nhưng bạn không nghe thấy tiếng.
  * `QUrl.fromLocalFile(file_path)`: Khác với PyQt5, PySide6 yêu cầu truyền một `QUrl` làm nguồn phát (`setSource`) thay vì truyền chuỗi đường dẫn text thông thường.



Nếu bạn muốn nâng cấp thêm ứng dụng này, hãy cho mình biết nhé! Mình có thể giúp bạn tích hợp thêm:

  * Thanh trượt (Slider) để tua thời gian bài hát.
  * Thanh trượt âm lượng (Volume control).
  * Danh sách phát (Playlist).