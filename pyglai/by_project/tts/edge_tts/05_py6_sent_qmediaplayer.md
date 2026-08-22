Để gom các từ đơn thành một câu hoàn chỉnh và tích hợp trình phát nhạc `QMediaPlayer` ngay trên giao diện, chúng ta cần thay đổi chiến lược xử lý dữ liệu WordBoundary.

Thay vì ghi mỗi từ một dòng phụ đề, hệ thống sẽ gom các từ lại dựa trên dấu câu (dấu chấm, dấu phẩy, dấu chấm hỏi) hoặc khoảng lặng (`break`), đồng thời tính toán lại thời gian bắt đầu của từ đầu tiên và thời gian kết thúc của từ cuối cùng trong câu đó.

Dưới đây là mã nguồn Python hoàn chỉnh sử dụng PySide6, `qasync` và `QMediaPlayer` (đi kèm thành phần xuất âm thanh `QAudioOutput` bắt buộc của Qt6):
    
    
    import sys
    import asyncio
    import os
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from qasync import QEventLoop, asyncSlot
    import edge_tts
    
    class AdvancedKaraokeApp(QWidget):
        def __init__(self):
            super().__init__()
            self.audio_file = "output.mp3"
            self.srt_file = "output.srt"
            self.init_ui()
            self.init_audio()
    
        def init_ui(self):
            self.setWindowTitle("Edge-TTS Sentence Gom & Player")
            self.resize(600, 500)
    
            self.layout = QVBoxLayout(self)
    
            # Khung nhập văn bản
            self.layout.addWidget(QLabel("Nhập đoạn văn bản dài:"))
            self.text_edit = QTextEdit()
            self.text_edit.setText(
                "Học lập trình Python với PySide6 rất thú vị. "
                "Hệ thống này sẽ tự động gom các từ đơn lẻ lại thành một câu hoàn chỉnh, "
                "sau đó xuất ra file phụ đề SRT chuẩn xác. Bạn có muốn thử ngay không?"
            )
            self.layout.addWidget(self.text_edit)
    
            # Nút chức năng xử lý chuyển đổi
            self.btn_start = QPushButton("1. Chuyển đổi & Xuất SRT (Gom câu)")
            self.layout.addWidget(self.btn_start)
    
            # Khung điều khiển nhạc (Bị ẩn lúc đầu, hiện sau khi chuyển đổi xong)
            self.play_layout = QHBoxLayout()
            self.btn_play = QPushButton("Phát âm thanh")
            self.btn_stop = QPushButton("Dừng")
            self.play_layout.addWidget(self.btn_play)
            self.play_layout.addWidget(self.btn_stop)
            self.layout.addLayout(self.play_layout)
            self.btn_play.setEnabled(False)
            self.btn_stop.setEnabled(False)
    
            # Trạng thái hệ thống
            self.label_status = QLabel("Trạng thái: Sẵn sàng")
            self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.label_status)
    
            # Nhãn hiển thị cả câu đang đọc
            self.label_sentence = QLabel("-")
            self.label_sentence.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
            self.label_sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_sentence.setWordWrap(True)
            self.layout.addWidget(self.label_sentence)
    
            # Kết nối sự kiện nút bấm
            self.btn_start.clicked.connect(self.start_processing)
            self.btn_play.clicked.connect(self.play_audio)
            self.btn_stop.clicked.connect(self.stop_audio)
    
        def init_audio(self):
            """Khởi tạo bộ phát âm thanh của Qt6"""
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            
            # Lắng nghe sự kiện thay đổi mốc thời gian của trình phát để cập nhật chữ lên giao diện
            self.player.positionChanged.connect(self.on_audio_position_changed)
    
        def ms_to_srt_time(self, ms: float) -> str:
            """Đổi mili-giây sang định dạng thời gian SRT (HH:MM:SS,mmm)"""
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
            self.btn_play.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.label_status.setText("Đang sinh dữ liệu và gom câu từ Edge-TTS...")
            self.label_sentence.setText("-")
    
            voice = "vi-VN-HoaiAnNeural"
            communicate = edge_tts.Communicate(text, voice)
            
            raw_words = []
    
            try:
                # Bước 1: Thu thập luồng âm thanh và toàn bộ các từ đơn lẻ từ WordBoundary
                with open(self.audio_file, "wb") as f:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            raw_words.append({
                                "word": chunk["text"],
                                "start": chunk["offset"] / 10000,
                                "duration": chunk["duration"] / 10000
                            })
                
                # Bước 2: Thuật toán gom từ đơn thành câu dựa trên cấu trúc dấu câu tiếng Việt
                self.sentences_data = []
                current_sentence = []
                
                # Danh sách các dấu câu dùng để ngắt câu
                end_punctuation = ('.', '?', '!', ';', ':', '...', '..')
    
                for item in raw_words:
                    current_sentence.append(item)
                    word_str = item["word"]
                    
                    # Nếu từ hiện tại kết thúc bằng dấu ngắt câu, thực hiện đóng gói câu đó lại
                    if word_str.endswith(end_punctuation):
                        start_time = current_sentence[0]["start"]
                        end_time = current_sentence[-1]["start"] + current_sentence[-1]["duration"]
                        sentence_string = " ".join([w["word"] for w in current_sentence])
                        
                        self.sentences_data.append({
                            "start": start_time,
                            "end": end_time,
                            "text": sentence_string
                        })
                        current_sentence = [] # Giải phóng để gom câu tiếp theo
    
                # Xử lý đoạn từ còn sót lại cuối cùng nếu không có dấu chấm ở cuối văn bản
                if current_sentence:
                    start_time = current_sentence[0]["start"]
                    end_time = current_sentence[-1]["start"] + current_sentence[-1]["duration"]
                    sentence_string = " ".join([w["word"] for w in current_sentence])
                    self.sentences_data.append({
                        "start": start_time,
                        "end": end_time,
                        "text": sentence_string
                    })
    
                # Bước 3: Xuất danh sách câu đã gom ra file .srt chuẩn
                srt_subtitles = []
                for index, s_data in enumerate(self.sentences_data, start=1):
                    start_str = self.ms_to_srt_time(s_data["start"])
                    end_str = self.ms_to_srt_time(s_data["end"])
                    srt_block = f"{index}\n{start_str} --> {end_str}\n{s_data['text']}\n"
                    srt_subtitles.append(srt_block)
    
                with open(self.srt_file, "w", encoding="utf-8") as f_srt:
                    f_srt.write("\n".join(srt_subtitles))
    
                self.label_status.setText("Đã lưu output.mp3 & output.srt thành công!")
                self.btn_play.setEnabled(True)
    
            except Exception as e:
                self.label_status.setText(f"Có lỗi xảy ra: {str(e)}")
            finally:
                self.btn_start.setEnabled(True)
    
        def play_audio(self):
            """Nạp file âm thanh vừa tạo vào QMediaPlayer và phát"""
            if os.path.exists(self.audio_file):
                # Qt6 yêu cầu đường dẫn file tuyệt đối kèm định dạng QUrl
                abs_path = os.path.abspath(self.audio_file)
                self.player.setSource(QUrl.fromLocalFile(abs_path))
                self.player.play()
                self.btn_play.setEnabled(False)
                self.btn_stop.setEnabled(True)
                self.label_status.setText("Đang phát âm thanh...")
    
        def stop_audio(self):
            """Dừng phát âm thanh"""
            self.player.stop()
            self.btn_play.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.label_status.setText("Đã dừng phát.")
            self.label_sentence.setText("-")
    
        def on_audio_position_changed(self, position_ms):
            """Kích hoạt liên tục khi bài nhạc đang chạy để quét mốc thời gian phụ đề khớp với UI"""
            if not hasattr(self, 'sentences_data'):
                return
    
            # Tìm câu thích hợp nằm trong khoảng thời gian hiện tại của bài nhạc
            current_text = "-"
            for s_data in self.sentences_data:
                if s_data["start"] <= position_ms <= s_data["end"]:
                    current_text = s_data["text"]
                    break
            
            self.label_sentence.setText(current_text)
    
            # Nếu nhạc hết, cập nhật lại trạng thái nút bấm
            if position_ms >= self.player.duration() and self.player.duration() > 0:
                self.btn_play.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.label_status.setText("Đã phát xong toàn bộ.")
                self.label_sentence.setText("Xong!")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
    
        window = AdvancedKaraokeApp()
        window.show()
    
        with loop:
            sys.exit(loop.run_forever())
    

## Điểm cải tiến cốt lõi trong phiên bản này:

  1. Thuật toán gom câu thông minh: Nhận diện ký tự cuối từ bằng tuple `end_punctuation = ('.', '?', '!', ';', ':', '...', '..')`. Khi quét trúng, toàn bộ các từ đơn đứng trước đó sẽ được dính lại với nhau, lấy mốc thời gian bắt đầu của từ đầu câu và mốc kết thúc của từ cuối câu.
  2. `QMediaPlayer` phối hợp với `positionChanged`: Khi bạn bấm "Phát âm thanh", bài nhạc chạy tới đâu (đơn vị mili-giây), hàm `on_audio_position_changed` sẽ liên tục tra cứu mốc thời gian đó thuộc về câu nào trong bộ nhớ để in ra màn hình `label_sentence`.
  3. Quản lý đa phương tiện chuẩn Qt6: Mã nguồn sử dụng `QAudioOutput()` liên kết trực tiếp vào `QMediaPlayer`, khắc phục hoàn toàn việc lỗi không có tiếng hoặc lỗi thiếu driver âm thanh khi nâng cấp từ phiên bản Qt5 cũ lên Qt6.



Bạn hãy chạy thử giao diện này. Nếu muốn mở rộng thêm, tôi có thể chỉ bạn cách:

  * Thêm thanh trượt `QSlider` giúp người dùng kéo tua thời gian bài đọc.
  * Thay đổi màu sắc của từ hiện tại ngay bên trong câu đang phát (chạy chữ karaoke nâng cao).