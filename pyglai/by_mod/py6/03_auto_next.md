Để ứng dụng tự động chuyển sang bài tiếp theo khi hát hết bài, chúng ta cần kết nối với tín hiệu (Signal) `mediaStatusChanged` của `QMediaPlayer`. Khi trạng thái chuyển sang `QMediaPlayer.MediaStatus.EndOfMedia`, chương trình sẽ tự động kích hoạt hàm chuyển bài.

Dưới đây là mã nguồn đã được cập nhật tính năng tự động chuyển bài:
    
    
    import os
    import sys
    from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                                 QHBoxLayout, QListWidget, QSlider, QLabel)
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl, Qt
    
    class AudioPlayerApp(QWidget):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("Ứng dụng Phát Audio - Tự Động Chuyển Bài")
            self.resize(500, 400)
            
            # 1. Cấu hình Audio
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(0.5) 
            
            # 2. Tạo Giao diện
            self.init_ui()
            
            # 3. Kết nối sự kiện của Player
            self.player.positionChanged.connect(self.update_position)
            self.player.durationChanged.connect(self.update_duration)
            
            # LẮNG NGHE SỰ KIỆN HẾT BÀI ĐỂ TỰ ĐỘNG CHUYỂN BÀI
            self.player.mediaStatusChanged.connect(self.handle_media_status)
            
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
            self.btn_next = QPushButton("Bài tiếp theo ⏭️") # Thêm nút Next bằng tay nếu thích bấm
            self.btn_play = QPushButton("Play")
            self.btn_pause = QPushButton("Pause")
            self.btn_stop = QPushButton("Stop")
            
            self.btn_play.clicked.connect(self.play_audio)
            self.btn_pause.clicked.connect(self.pause_audio)
            self.btn_stop.clicked.connect(self.stop_audio)
            self.btn_next.clicked.connect(self.next_track)
            
            layout_buttons = QHBoxLayout()
            layout_buttons.addWidget(self.btn_play)
            layout_buttons.addWidget(self.btn_pause)
            layout_buttons.addWidget(self.btn_stop)
            layout_buttons.addWidget(self.btn_next)
            
            # Thêm tất cả vào Layout chính
            layout_main.addWidget(self.lbl_playlist)
            layout_main.addWidget(self.list_widget)
            layout_main.addLayout(layout_info)
            layout_main.addWidget(self.slider_progress)
            layout_main.addLayout(layout_volume)
            layout_main.addLayout(layout_buttons)
            
            self.setLayout(layout_main)
    
        def scan_input_folder(self):
            self.folder_path = os.path.join(os.path.dirname(__file__), "input")
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
                self.lbl_status.setText("Đã tạo thư mục /input. Hãy chép nhạc vào đó rồi bật lại app.")
                return
                
            valid_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
            files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(valid_extensions)]
            
            if files:
                self.list_widget.addItems(files)
                self.lbl_status.setText(f"Tìm thấy {len(files)} file nhạc.")
            else:
                self.lbl_status.setText("Thư mục /input đang trống.")
    
        def play_selected_file(self, item):
            if not item:
                return
            file_name = item.text()
            full_path = os.path.join(self.folder_path, file_name)
            
            file_url = QUrl.fromLocalFile(full_path)
            self.player.setSource(file_url)
            self.player.play()
            
            self.lbl_status.setText(f"Đang phát: {file_name}")
    
        def play_audio(self):
            if self.player.source().isEmpty() and self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                self.play_selected_file(self.list_widget.currentItem())
            else:
                self.player.play()
    
        def pause_audio(self):
            self.player.pause()
    
        def stop_audio(self):
            self.player.stop()
    
        def handle_media_status(self, status):
            """Bắt sự kiện trạng thái của trình phát media"""
            # Nếu trạng thái báo là đã phát hết bài (EndOfMedia)
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                self.next_track()
    
        def next_track(self):
            """Hàm xử lý chuyển sang bài tiếp theo"""
            current_row = self.list_widget.currentRow()
            total_rows = self.list_widget.count()
            
            if total_rows == 0:
                return
                
            # Tính toán hàng tiếp theo (nếu là bài cuối thì quay lại bài đầu tiên - index 0)
            next_row = (current_row + 1) % total_rows
            
            # Chọn hàng mới trên giao diện và phát bài đó
            self.list_widget.setCurrentRow(next_row)
            self.play_selected_file(self.list_widget.currentItem())
    
        # --- Các hàm xử lý Slider và Thời gian ---
        def change_volume(self, value):
            self.audio_output.setVolume(value / 100.0)
    
        def update_position(self, position):
            if not self.slider_progress.isSliderDown():
                self.slider_progress.setValue(position)
            self.update_time_label(position, self.player.duration())
    
        def update_duration(self, duration):
            self.slider_progress.setRange(0, duration)
            self.update_time_label(self.player.position(), duration)
    
        def set_music_position(self, position):
            self.player.setPosition(position)
    
        def update_time_label(self, position, duration):
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
    

## Điểm cải tiến chính:

  1. `mediaStatusChanged`: Tín hiệu này liên tục theo dõi tiến trình load/phát file. Khi bài nhạc chạy tới giây cuối cùng và dừng lại, nó sẽ gửi trạng thái `QMediaPlayer.MediaStatus.EndOfMedia` để gọi hàm `next_track()`.
  2. Vòng lặp danh sách bài hát: Trong hàm `next_track()`, phép toán chia lấy dư `(current_row + 1) % total_rows` giúp danh sách tự động quay về bài đầu tiên sau khi đã phát hết bài cuối cùng.
  3. Nút bổ sung: Thêm nút `Bài tiếp theo ⏭️` để bạn có thể chủ động click nhảy bài bất cứ lúc nào mà không cần đợi hết bài.



Nếu bạn muốn bổ sung thêm tính năng nào khác, hãy cho mình biết nhé:

  * Thêm nút Phát ngẫu nhiên (Shuffle) hoặc Lặp lại 1 bài (Loop)?
  * Thêm nút Quay lại bài trước (Previous)?
  * Thiết kế Giao diện đẹp hơn (sử dụng QSS / CSS)?