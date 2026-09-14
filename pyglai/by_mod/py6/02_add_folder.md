Dưới đây là phiên bản nâng cấp của ứng dụng. Chương trình sẽ tự động quét toàn bộ các file âm thanh trong thư mục `input` (nằm cùng cấp với file code), hiển thị lên một danh sách (Playlist), và tích hợp thêm Thanh tua thời gian (Slider) cùng Thanh chỉnh âm lượng.

## 1\. Chu bị thư mục

Bạn hãy tạo một thư mục tên là `input` nằm ngay cạnh file chạy Python này và bỏ các file nhạc (`.mp3`, `.wav`,...) vào đó.

## 2\. Mã nguồn ứng dụng nâng cấp
    
    
    import os
    import sys
    from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                                 QHBoxLayout, QListWidget, QSlider, QLabel)
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl, Qt
    
    class AudioPlayerApp(QWidget):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("Ứng dụng Phát Audio - Playlist & Slider")
            self.resize(500, 400)
            
            # 1. Cấu hình Audio
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            
            # Mặc định âm lượng 50%
            self.audio_output.setVolume(0.5) 
            
            # 2. Tạo Giao diện
            self.init_ui()
            
            # 3. Kết nối sự kiện của Player (Cập nhật Slider theo nhạc)
            self.player.positionChanged.connect(self.update_position)
            self.player.durationChanged.connect(self.update_duration)
            
            # 4. Tự động quét thư mục input
            self.scan_input_folder()
    
        def init_ui(self):
            layout_main = QVBoxLayout()
            
            # Danh sách bài hát
            self.lbl_playlist = QLabel("Danh sách bài hát (Thư mục /input):")
            self.list_widget = QListWidget()
            self.list_widget.itemDoubleClicked.connect(self.play_selected_file)
            
            # Thanh trạng thái & thời gian
            self.lbl_status = QLabel("Chọn bài hát để phát...")
            self.lbl_time = QLabel("00:00 / 00:00")
            self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            layout_info = QHBoxLayout()
            layout_info.addWidget(self.lbl_status)
            layout_info.addWidget(self.lbl_time)
            
            # Thanh tua nhạc (Progress Slider)
            self.slider_progress = QSlider(Qt.Orientation.Horizontal)
            self.slider_progress.setRange(0, 0)
            self.slider_progress.sliderMoved.connect(self.set_music_position)
            
            # Thanh âm lượng (Volume Slider)
            lbl_volume = QLabel("Âm lượng:")
            self.slider_volume = QSlider(Qt.Orientation.Horizontal)
            self.slider_volume.setRange(0, 100)
            self.slider_volume.setValue(50)
            self.slider_volume.setFixedWidth(100)
            self.slider_volume.valueChanged.connect(self.change_volume)
            
            layout_volume = QHBoxLayout()
            layout_volume.addStretch()
            layout_volume.addWidget(lbl_volume)
            layout_volume.addWidget(self.slider_volume)
            
            # Các nút điều khiển
            self.btn_play = QPushButton("Play")
            self.btn_pause = QPushButton("Pause")
            self.btn_stop = QPushButton("Stop")
            
            self.btn_play.clicked.connect(self.play_audio)
            self.btn_pause.clicked.connect(self.pause_audio)
            self.btn_stop.clicked.connect(self.stop_audio)
            
            layout_buttons = QHBoxLayout()
            layout_buttons.addWidget(self.btn_play)
            layout_buttons.addWidget(self.btn_pause)
            layout_buttons.addWidget(self.btn_stop)
            
            # Thêm tất cả vào Layout chính
            layout_main.addWidget(self.lbl_playlist)
            layout_main.addWidget(self.list_widget)
            layout_main.addLayout(layout_info)
            layout_main.addWidget(self.slider_progress)
            layout_main.addLayout(layout_volume)
            layout_main.addLayout(layout_buttons)
            
            self.setLayout(layout_main)
    
        def scan_input_folder(self):
            """Tự động quét và nạp các file âm thanh từ thư mục 'input'"""
            self.folder_path = os.path.join(os.path.dirname(__file__), "input")
            
            # Nếu chưa có thư mục input thì tự tạo tự động
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
                self.lbl_status.setText("Đã tạo thư mục /input. Hãy chép nhạc vào đó rồi bật lại app.")
                return
                
            # Các định dạng âm thanh được hỗ trợ
            valid_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
            
            # Quét file
            files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(valid_extensions)]
            
            if files:
                self.list_widget.addItems(files)
                self.lbl_status.setText(f"Tìm thấy {len(files)} file nhạc.")
            else:
                self.lbl_status.setText("Thư mục /input đang trống.")
    
        def play_selected_file(self, item):
            """Phát file khi double-click vào danh sách"""
            file_name = item.text()
            full_path = os.path.join(self.folder_path, file_name)
            
            file_url = QUrl.fromLocalFile(full_path)
            self.player.setSource(file_url)
            self.player.play()
            
            self.lbl_status.setText(f"Đang phát: {file_name}")
    
        def play_audio(self):
            # Nếu chưa chọn bài nào trong list, chọn bài đầu tiên
            if self.player.source().isEmpty() and self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                self.play_selected_file(self.list_widget.currentItem())
            else:
                self.player.play()
    
        def pause_audio(self):
            self.player.pause()
    
        def stop_audio(self):
            self.player.stop()
    
        # --- Các hàm xử lý Slider và Thời gian ---
        def change_volume(self, value):
            # QAudioOutput nhận giá trị từ 0.0 đến 1.0, Slider chạy từ 0 đến 100
            self.audio_output.setVolume(value / 100.0)
    
        def update_position(self, position):
            """Cập nhật vị trí thanh Slider theo tiến độ bài hát (miligiây)"""
            if not self.slider_progress.isSliderDown(): # Chỉ cập nhật khi người dùng không giữ chuột kéo
                self.slider_progress.setValue(position)
            self.update_time_label(position, self.player.duration())
    
        def update_duration(self, duration):
            """Cập nhật độ dài tối đa của Slider khi đổi bài hát mới"""
            self.slider_progress.setRange(0, duration)
            self.update_time_label(self.player.position(), duration)
    
        def set_music_position(self, position):
            """Tua nhạc đến đoạn người dùng vừa kéo Slider"""
            self.player.setPosition(position)
    
        def update_time_label(self, position, duration):
            """Đổi mili-giây thành định dạng Phút:Giây (00:00)"""
            pos_sec = position // 1000
            dur_sec = duration // 1000
            
            pos_min, pos_sec = divmod(pos_sec, 60)
            dur_min, dur_sec = divmod(dur_sec, 60)
            
            self.lbl_time.setText(f"{pos_min:02d}:{pos_sec:02d} / {dur_min:02d}:{dur_sec:02d}")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        player_app = AudioPlayerApp()
        player_app.show()
        sys.exit(app.exec())
    

## Cách hoạt động nâng cấp:

  1. `os.listdir`: Quét tự động thư mục `input`. Bạn chỉ cần mở app lên là nhạc tự động hiện sẵn trong bảng.
  2. `positionChanged` & `durationChanged`: Hai tín hiệu (Signals) này liên tục đo đạc bài nhạc đang chạy ở mili-giây thứ bao nhiêu để đẩy thanh Slider chạy theo thời gian thực và đổi số phút (Ví dụ: `01:23 / 03:45`).
  3. `sliderMoved`: Cho phép bạn bấm chuột kéo thả thanh Slider để tua bài nhạc tới/lui tùy ý.



Nếu muốn tối ưu hơn nữa, bạn có muốn tích hợp thêm tính năng tự động chuyển bài khi hết nhạc, hoặc thêm nút Trộn bài (Shuffle) / Lặp bài (Loop) không?