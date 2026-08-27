Để đáp ứng yêu cầu xử lý file lớn, chia nhỏ (chunking) để tránh giới hạn ký tự của API, sau đó tự động gộp (merge) âm thanh lại theo từng file, chúng ta cần bổ sung thêm một thư viện xử lý âm thanh là `pydub`.

Dưới đây là kiến trúc mã nguồn được cập nhật theo đúng chuẩn DDD và SOLID.

* * *

## Bước 1: Cài đặt thêm công cụ hỗ trợ

`pydub` yêu cầu phần mềm FFmpeg trên máy tính để gộp file MP3. Bạn cài đặt thư viện bằng `uv`:
    
    
    uv pip install pydub
    

_(Lưu ý: Nếu chạy code bị lỗi liên quan đến FFmpeg, bạn cần tải FFmpeg về máy và thêm vào biến môi trường PATH của Windows)._

* * *

## Bước 2: Tái cấu trúc mã nguồn theo DDD & SOLID

## 1\. LỚP DOMAIN (Quy tắc xử lý văn bản và thực thể)

Thêm logic chia nhỏ văn bản (Text Chunker) vào lớp Domain để đảm bảo tính đóng gói nghiệp vụ.

`domain/models.py`:
    
    
    import re
    from dataclasses import dataclass
    from typing import List
    
    @dataclass(frozen=True)
    class Voice:
        id: str
        display_name: str
        language: str
    
    @dataclass(frozen=True)
    class AudioPreset:
        name: str
        rate: str
        pitch: str
    
    @dataclass
    class StoryDocument:
        name: str
        text: str
    
        def get_chunks(self, max_chars: int = 2500) -> List[str]:
            """Chia văn bản thành các đoạn nhỏ dưới max_chars, không làm cắt đôi từ"""
            if not self.text.strip():
                return []
                
            # Chia theo dấu câu để giữ ngữ điệu tự nhiên cho AI
            sentences = re.split(r'(?<=[.!?])\s+', self.text.strip())
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                # Nếu một câu quá dài (hiếm gặp), cắt ép buộc theo ký tự
                if len(sentence) > max_chars:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    # Cắt nhỏ câu dài
                    for i in range(0, len(sentence), max_chars):
                        chunks.append(sentence[i:i+max_chars])
                    continue
    
                if current_length + len(sentence) + 1 > max_chars:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence) + 1
    
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
            return chunks
    

`domain/interfaces.py`:
    
    
    from abc import ABC, abstractmethod
    from typing import List
    from domain.models import Voice, AudioPreset
    
    class ITTSService(ABC):
        @abstractmethod
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            """Chuyển đổi một đoạn văn bản ngắn thành file MP3 tạm thời"""
            pass
    
    class IAudioMerger(ABC):
        @abstractmethod
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None:
            """Gộp nhiều file MP3 tạm thời thành một file MP3 duy nhất"""
            pass
    

* * *

## 2\. LỚP INFRASTRUCTURE (Triển khai công nghệ kỹ thuật)

Cài đặt chi tiết cách `edge-tts` và `pydub` hoạt động.

`infrastructure/tts_service.py`:
    
    
    import edge_tts
    from domain.interfaces import ITTSService
    from domain.models import Voice, AudioPreset
    
    class EdgeTTSService(ITTSService):
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice.id,
                rate=preset.rate,
                pitch=preset.pitch
            )
            await communicate.save(output_path)
    

`infrastructure/audio_merger.py`:
    
    
    import os
    from typing import List
    from pydub import AudioSegment
    from domain.interfaces import IAudioMerger
    
    class PydubAudioMerger(IAudioMerger):
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None:
            if not src_paths:
                return
                
            # Khởi tạo phân đoạn âm thanh trống
            combined = AudioSegment.empty()
            
            for path in src_paths:
                if os.path.exists(path):
                    segment = AudioSegment.from_mp3(path)
                    combined += segment
                    
            # Xuất bản file gộp cuối cùng
            combined.export(dest_path, format="mp3")
    

* * *

## 3\. LỚP APPLICATION (Điều phối xử lý tải file/thư mục và chia nhỏ)

Quản lý luồng công việc: Đọc tài liệu $\rightarrow$ Chia nhỏ $\rightarrow$ Gọi TTS $\rightarrow$ Gộp file $\rightarrow$ Dọn dẹp file rác.

`application/tts_orchestrator.py`:
    
    
    import os
    import glob
    from typing import List, Callable
    from domain.interfaces import ITTSService, IAudioMerger
    from domain.models import StoryDocument, Voice, AudioPreset
    
    class TTSOrchestrator:
        def __init__(self, tts_service: ITTSService, audio_merger: IAudioMerger):
            self._tts_service = tts_service
            self._audio_merger = audio_merger
    
        async def process_single_document(
            self, doc: StoryDocument, voice: Voice, preset: AudioPreset, output_dir: str, progress_callback: Callable[[str], None] = None
        ) -> str:
            """Xử lý chia nhỏ, chuyển đổi và gộp âm thanh cho một tài liệu đơn lẻ"""
            chunks = doc.get_chunks(max_chars=2500)
            if not chunks:
                return ""
    
            temp_files: List[str] = []
            final_output_path = os.path.join(output_dir, f"{doc.name}.mp3")
    
            try:
                # 1. Chuyển đổi từng chunk thành file tạm
                for idx, chunk in enumerate(chunks):
                    if progress_callback:
                        progress_callback(f"Đang xử lý '{doc.name}': Đoạn {idx + 1}/{len(chunks)}")
                    
                    temp_path = os.path.join(output_dir, f"temp_{doc.name}_{idx}.mp3")
                    await self._tts_service.convert_chunk_to_mp3(chunk, voice, preset, temp_path)
                    temp_files.append(temp_path)
    
                # 2. Gộp các file tạm lại thành file chính
                if progress_callback:
                    progress_callback(f"Đang gộp âm thanh cho file: {doc.name}")
                self._audio_merger.merge_mp3_files(temp_files, final_output_path)
    
            finally:
                # 3. Dọn dẹp file tạm (Xóa bỏ để tránh rác ổ đĩa)
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception:
                            pass # Bỏ qua nếu file đang bị lock
                            
            return final_output_path
    
        async def process_batch_directory(
            self, input_dir: str, voice: Voice, preset: AudioPreset, output_dir: str, progress_callback: Callable[[str], None] = None
        ) -> None:
            """Tìm và xử lý tất cả file .txt trong thư mục đầu vào"""
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            if not txt_files:
                raise FileNotFoundError("Không tìm thấy file .txt nào trong thư mục đã chọn.")
    
            for file_path in txt_files:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                doc = StoryDocument(name=base_name, text=content)
                await self.process_single_document(doc, voice, preset, output_dir, progress_callback)
    

* * *

## 4\. LỚP PRESENTATION (Giao diện người dùng được thiết kế lại)

Giao diện bổ sung thêm tính năng: Chọn 1 File hoặc Chọn cả Thư mục, hiển thị log tiến trình xử lý thời gian thực.

`presentation/main_window.py`:
    
    
    import os
    from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QComboBox, QPushButton, QFileDialog, 
                                 QMessageBox, QGroupBox, QRadioButton, QButtonGroup)
    from PySide6.QtCore import Qt, QThread, Signal
    
    from domain.models import Voice, AudioPreset, StoryDocument
    from application.tts_orchestrator import TTSOrchestrator
    
    VOICES_DATA = [
        Voice("en-US-AriaNeural", "en-US-AriaNeural (Nữ Mỹ - Truyền cảm)", "English"),
        Voice("en-US-JennyNeural", "en-US-JennyNeural (Nữ Mỹ - Cổ tích)", "English"),
        Voice("en-US-GuyNeural", "en-US-GuyNeural (Nam Mỹ - Trầm ấm)", "English"),
        Voice("en-GB-SoniaNeural", "en-GB-SoniaNeural (Nữ Anh - Cổ điển)", "English"),
        Voice("vi-VN-HoaiAnNeural", "vi-VN-HoaiAnNeural (Nữ Việt - Dịu dàng)", "Vietnamese"),
        Voice("vi-VN-NamMinhNeural", "vi-VN-NamMinhNeural (Nam Việt - Trầm hùng)", "Vietnamese")
    ]
    
    PRESETS_DATA = [
        AudioPreset("Cổ tích / Thần thoại (Fairy Tales)", "-12%", "+3Hz"),
        AudioPreset("Kinh dị / Trinh thám (Horror / Thriller)", "-16%", "-4Hz"),
        AudioPreset("Ngôn tình / Tâm lý xã hội (Drama / Romance)", "-15%", "-1Hz"),
        AudioPreset("Mặc định / Phổ thông (Default)", "+0%", "+0Hz")
    ]
    
    class QtBatchTTSWorker(QThread):
        progress_signal = Signal(str)
        finished_signal = Signal(bool, str)
    
        def __init__(self, orchestrator: TTSOrchestrator, mode: str, source_path: str, output_dir: str, voice: Voice, preset: AudioPreset):
            super().__init__()
            self.orchestrator = orchestrator
            self.mode = mode # "file" hoặc "folder"
            self.source_path = source_path
            self.output_dir = output_dir
            self.voice = voice
            self.preset = preset
    
        def run(self):
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                def cb(msg): self.progress_signal.emit(msg)
    
                if self.mode == "file":
                    base_name = os.path.splitext(os.path.basename(self.source_path))[0]
                    with open(self.source_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    doc = StoryDocument(name=base_name, text=content)
                    loop.run_until_complete(self.orchestrator.process_single_document(doc, self.voice, self.preset, self.output_dir, cb))
                else:
                    loop.run_until_complete(self.orchestrator.process_batch_directory(self.source_path, self.voice, self.preset, self.output_dir, cb))
                    
                loop.close()
                self.finished_signal.emit(True, "Mọi tác vụ xử lý văn bản và gộp âm thanh đã hoàn thành!")
            except Exception as e:
                self.finished_signal.emit(False, str(e))
    
    class MainWindow(QMainWindow):
        def __init__(self, orchestrator: TTSOrchestrator):
            super().__init__()
            self._orchestrator = orchestrator
            self.setWindowTitle("DDD Batch Text-to-Speech Audio Merger")
            self.setMinimumSize(600, 450)
            self._init_ui()
    
        def _init_ui(self):
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(15)
    
            # Nhóm lựa chọn Chế độ chạy
            mode_group = QGroupBox("Chế độ xử lý dữ liệu")
            mode_layout = QHBoxLayout(mode_group)
            self.rad_file = QRadioButton("Chuyển đổi 1 File đơn lẻ (.txt)")
            self.rad_folder = QRadioButton("Xử lý hàng loạt theo Thư mục (Folder)")
            self.rad_file.setChecked(True)
            
            self.btn_group = QButtonGroup()
            self.btn_group.addButton(self.rad_file)
            self.btn_group.addButton(self.rad_folder)
            
            mode_layout.addWidget(self.rad_file)
            mode_layout.addWidget(self.rad_folder)
            main_layout.addWidget(mode_group)
    
            # Nhóm chọn đường dẫn vào / ra
            path_group = QGroupBox("Cấu hình đường dẫn hệ thống")
            path_layout = QVBoxLayout(path_group)
            
            # Nguồn vào
            h1 = QHBoxLayout()
            self.lbl_source = QLabel("Chưa chọn file/thư mục nguồn...")
            btn_select_src = QPushButton("Chọn Nguồn")
            btn_select_src.clicked.connect(self._select_source)
            h1.addWidget(self.lbl_source, stretch=3)
            h1.addWidget(btn_select_src, stretch=1)
            path_layout.addLayout(h1)
    
            # Đích ra
            h2 = QHBoxLayout()
            self.lbl_output = QLabel("Chưa chọn thư mục lưu MP3...")
            btn_select_out = QPushButton("Chọn Nơi Lưu")
            btn_select_out.clicked.connect(self._select_output)
            h2.addWidget(self.lbl_output, stretch=3)
            h2.addWidget(btn_select_out, stretch=1)
            path_layout.addLayout(h2)
            
            main_layout.addWidget(path_group)
    
            # Nhóm cấu hình Giọng đọc & Preset
            config_group = QGroupBox("Cấu hình âm thanh")
            config_layout = QHBoxLayout(config_group)
            
            self.genre_combo = QComboBox()
            self.genre_combo.addItems([p.name for p in PRESETS_DATA])
            config_layout.addWidget(self.genre_combo)
    
            self.voice_combo = QComboBox()
            self.voice_combo.addItems([v.display_name for v in VOICES_DATA])
            config_layout.addWidget(self.voice_combo)
            
            main_layout.addWidget(config_group)
    
            # Trạng thái & Tiến trình hiển thị
            self.status_label = QLabel("Sẵn sàng xử lý")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 13px;")
            self.status_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.status_label)
    
            # Nút hành động chính
            self.btn_start = QPushButton("BẮT ĐẦU XỬ LÝ CHUYỂN ĐỔI")
            self.btn_start.setMinimumHeight(50)
            self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; font-size: 14px;")
            self.btn_start.clicked.connect(self._start_process)
            main_layout.addWidget(self.btn_start)
    
            self.source_path = ""
            self.output_dir = ""
    
        def _select_source(self):
            if self.rad_file.isChecked():
                file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file văn bản", "", "Text files (*.txt)")
                if file_path:
                    self.source_path = file_path
                    self.lbl_source.setText(f"File chọn: {os.path.basename(file_path)}")
            else:
                dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa các file truyện")
                if dir_path:
                    self.source_path = dir_path
                    self.lbl_source.setText(f"Thư mục: {dir_path}")
    
        def _select_output(self):
            dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu kết quả đầu ra")
            if dir_path:
                self.output_dir = dir_path
                self.lbl_output.setText(f"Lưu tại: {dir_path}")
    
        def _start_process(self):
            if not self.source_path or not self.output_dir:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đầy đủ Đường dẫn nguồn và Đường dẫn đích lưu!")
                return
    
            voice = VOICES_DATA[self.voice_combo.currentIndex()]
            preset = PRESETS_DATA[self.genre_combo.currentIndex()]
            mode = "file" if self.rad_file.isChecked() else "folder"
    
            self.btn_start.setEnabled(False)
            self.status_label.setStyleSheet("color: blue;")
    
            self.worker = QtBatchTTSWorker(self._orchestrator, mode, self.source_path, self.output_dir, voice, preset)
            self.worker.progress_signal.connect(self.status_label.setText)
            self.worker.finished_signal.connect(self._on_finished)
            self.worker.start()
    
        def _on_finished(self, success, message):
            self.btn_start.setEnabled(True)
            self.status_label.setText("Sẵn sàng xử lý")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            if success:
                QMessageBox.information(self, "Hoàn tất", message)
            else:
                QMessageBox.critical(self, "Gặp lỗi hệ thống", message)
    

* * *

## 5\. FILE KHỞI CHẠY CHÍNH (Composition Root)

Liên kết các Interfaces hạ tầng mới (`IAudioMerger`) vào tầng nghiệp vụ ứng dụng.

`main.py`:
    
    
    import sys
    from PySide6.QtWidgets import QApplication
    from infrastructure.tts_service import EdgeTTSService
    from infrastructure.audio_merger import PydubAudioMerger
    from application.tts_orchestrator import TTSOrchestrator
    from presentation.main_window import MainWindow
    
    def main():
        app = QApplication(sys.argv)
        
        # Khởi tạo các module hạ tầng kỹ thuật riêng biệt (SOLID - S)
        tts_service = EdgeTTSService()
        audio_merger = PydubAudioMerger()
        
        # Tiêm hạ tầng kỹ thuật (Dependency Injection) vào kiến trúc logic Core thông qua Interface
        orchestrator = TTSOrchestrator(tts_service=tts_service, audio_merger=audio_merger)
        
        # Khởi chạy giao diện người dùng
        window = MainWindow(orchestrator=orchestrator)
        window.show()
        
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
    

## Điểm nổi bật về nghiệp vụ được xử lý:

  1. Xử lý văn bản lớn thông minh: Hàm `get_chunks` trong lớp Domain sẽ tự động quét văn bản, ngắt đoạn tối đa 2500 ký tự tại vị trí các dấu câu kết thúc câu (`.`, `!`, `?`), giữ nguyên tính mạch lạc của câu văn giúp AI không bị đọc vấp hoặc mất chữ giữa chừng.
  2. Gộp file tự động và đồng bộ: Tách biệt tác vụ chuyển đổi qua `edge-tts` cho từng khối $\rightarrow$ gộp dữ liệu nhị phân MP3 thông qua luồng ghi của `pydub` $\rightarrow$ tự động dọn dẹp (xóa bỏ) các chunk tạm thời để giải phóng dung lượng ổ cứng.



Bạn có thể tạo các thư mục tương ứng, lưu code vào các file rồi dùng lệnh `uv run main.py` để chạy phần mềm mượt mà! Nếu gặp bất kỳ vấn đề gì về luồng merge dữ liệu, hãy nhắn tôi nhé.