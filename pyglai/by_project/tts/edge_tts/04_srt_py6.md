Để tích hợp dữ liệu WordBoundary từ `edge-tts` thành file phụ đề `.srt` và hiển thị trực tiếp lên giao diện đồ họa PySide6 (Qt for Python), chúng ta cần giải quyết một bài toán: Không làm treo giao diện đồ họa (UI Thread) khi đang chạy tác vụ bất đồng bộ (`asyncio`).

Tôi sẽ sử dụng thư viện `qasync` để kết hợp hoàn hảo vòng lặp sự kiện của Qt với `asyncio`.

## 1\. Cài đặt các thư viện cần thiết

Bạn chạy lệnh sau trong terminal để cài đặt PySide6 và gói hỗ trợ async:
    
    
    pip install PySide6 qasync edge-tts
    

## 2\. Mã nguồn ứng dụng PySide6 hoàn chỉnh

Đoạn code dưới đây sẽ tạo một giao diện cho phép bạn nhập văn bản, nhấn nút để tạo file âm thanh, đồng thời tự động xuất ra file phụ đề `.srt` và hiển thị trực tiếp tiến trình chạy chữ lên giao diện.
    
    
    import sys
    import asyncio
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
    from PySide6.QtCore import Qt
    from qasync import QEventLoop, asyncSlot
    import edge_tts
    
    class KaraokeApp(QWidget):
        def __init__(self):
            super().__init__()
            self.init_ui()
    
        def init_ui(self):
            self.setWindowTitle("Edge-TTS Karaoke & SRT Exporter")
            self.resize(500, 400)
    
            # Giao diện người dùng
            self.layout = QVBoxLayout(self)
    
            self.label_input = QLabel("Nhập văn bản cần đọc:")
            self.layout.addWidget(self.label_input)
    
            self.text_edit = QTextEdit()
            self.text_edit.setText("Học lập trình Python với PySide6 rất thú vị và có nhiều ứng dụng thực tế.")
            self.layout.addWidget(self.text_edit)
    
            self.btn_start = QPushButton("Chuyển đổi & Xuất SRT")
            self.layout.addWidget(self.btn_start)
    
            self.label_status = QLabel("Trạng thái: Sẵn sàng")
            self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.label_status)
    
            # Nhãn hiển thị từ đang đọc (Hiệu ứng karaoke)
            self.label_word = QLabel("-")
            self.label_word.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
            self.label_word.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.label_word)
    
            # Kết nối sự kiện nút bấm với hàm async
            self.btn_start.clicked.connect(self.start_processing)
    
        def ms_to_srt_time(self, ms: float) -> str:
            """Chuyển đổi mili-giây sang định dạng thời gian SRT (HH:MM:SS,mmm)"""
            hours = int(ms // 3600000)
            minutes = int((ms % 3600000) // 60000)
            seconds = int((ms % 60000) // 1000)
            milliseconds = int(ms % 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
        @asyncSlot()
        async def start_processing(self):
            text = self.text_edit.toPlainText().strip()
            if not text:
                self.label_status.setText("Vui lòng không để trống văn bản!")
                return
    
            self.btn_start.setEnabled(False)
            self.label_status.setText("Đang xử lý luồng dữ liệu...")
            self.label_word.setText("-")
    
            voice = "vi-VN-HoaiAnNeural"
            audio_file = "output.mp3"
            srt_file = "output.srt"
    
            communicate = edge_tts.Communicate(text, voice)
            srt_subtitles = []
            index = 1
    
            try:
                with open(audio_file, "wb") as f:
                    async for chunk in communicate.stream():
                        # Ghi dữ liệu âm thanh
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                        
                        # Xử lý dữ liệu WordBoundary để làm phụ đề và cập nhật UI
                        elif chunk["type"] == "WordBoundary":
                            word = chunk["text"]
                            start_ms = chunk["offset"] / 10000
                            duration_ms = chunk["duration"] / 10000
                            end_ms = start_ms + duration_ms
    
                            # Cập nhật chữ đang đọc lên giao diện ngay lập tức
                            self.label_word.setText(word)
    
                            # Định dạng mốc thời gian phụ đề
                            start_time = self.ms_to_srt_time(start_ms)
                            end_time = self.ms_to_srt_time(end_ms)
    
                            # Lưu vào danh sách phụ đề SRT
                            srt_block = f"{index}\n{start_time} --> {end_time}\n{word}\n"
                            srt_subtitles.append(srt_block)
                            index += 1
                            
                            # Thêm một chút delay siêu ngắn để giao diện kịp vẽ lại mượt mà
                            await asyncio.sleep(0.001)
    
                # Ghi toàn bộ danh sách phụ đề ra file .srt
                with open(srt_file, "w", encoding="utf-8") as f_srt:
                    f_srt.write("\n".join(srt_subtitles))
    
                self.label_status.setText("Hoàn thành! Đã xuất file output.mp3 và output.srt")
                self.label_word.setText("Xong!")
    
            except Exception as e:
                self.label_status.setText(f"Có lỗi xảy ra: {str(e)}")
            finally:
                self.btn_start.setEnabled(True)
    
    if __name__ == "__main__":
        # Cấu hình vòng lặp sự kiện đặc biệt kết hợp giữa Qt và Asyncio
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
    
        window = KaraokeApp()
        window.show()
    
        with loop:
            sys.exit(loop.run_forever())
    

## Cách thức hoạt động của đoạn mã:

  1. `qasync.QEventLoop`: Thay thế vòng lặp mặc định của Qt để các lệnh `async for` và `await asyncio.sleep()` chạy trực tiếp trên ứng dụng mà không gây hiện tượng đứng hình (Not Responding).
  2. `@asyncSlot()`: Đây là decorator bắt buộc để biến hàm xử lý sự kiện bấm nút của PySide6 thành một hàm bất đồng bộ.
  3. `ms_to_srt_time`: Hàm tự động quy đổi từ mili-giây thuần sang định dạng chuẩn quốc tế của file phụ đề SRT (`00:00:01,250`).
  4. Hiệu ứng chữ đổi: Hàm `self.label_word.setText(word)` liên tục cập nhật từ đơn đang phát âm lên màn hình theo thời gian thực (real-time).



Bạn có thể chạy thử mã nguồn trên. Nếu bạn muốn, chúng ta có thể nâng cấp thêm để tự gom cụm các từ đơn thành một câu phụ đề dài hoàn chỉnh (thay vì mỗi từ một dòng SRT) hoặc tích hợp trình phát nhạc `QMediaPlayer` để bấm phát lại file ngay trên giao diện!