Dưới đây là file mã nguồn `main_advanced.py` hoàn chỉnh. Tôi đã tích hợp toàn bộ các lớp thiết kế theo mô hình DDD / SOLID từ các bước trước, đồng thời bổ sung thêm một nút bấm "CHUẨN HÓA VĂN BẢN TRƯỚC" (Text Normalizer) ngay trên giao diện PySide6.

Quy trình hoạt động: Bạn chọn File/Thư mục → Bấm chuẩn hóa văn bản gốc để sửa lỗi dấu câu và chữ hoa → Bấm xuất file Audio để bắt đầu chia nhỏ (chunk 2500 ký tự) và gộp (merge) âm thanh tự động.

## Toàn bộ mã nguồn hệ thống (`main_advanced.py`)
```    
    
    import sys
    import os
    import re
    import glob
    import asyncio
    from typing import List, Callable
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QComboBox, QPushButton, 
                                 QFileDialog, QMessageBox, QGroupBox, QRadioButton, 
                                 QButtonGroup)
    from PySide6.QtCore import Qt, QThread, Signal
    import edge_tts
    from pydub import AudioSegment
    
    # =====================================================================
    # 1. LỚP DOMAIN (Models, Rules & Interfaces)
    # =====================================================================
    
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
    
        def is_empty(self) -> bool:
            return not self.text.strip()
    
        def get_chunks(self, max_chars: int = 2500) -> List[str]:
            """Chia văn bản thành các đoạn nhỏ dưới max_chars, không làm cắt đôi từ"""
            if self.is_empty():
                return []
                
            sentences = re.split(r'(?<=[.!?])\s+', self.text.strip())
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                if len(sentence) > max_chars:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_length = 0
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
    
    class TextNormalizer:
        """Quy tắc lõi chuẩn hóa văn bản truyện giúp AI đọc chuẩn ngữ điệu"""
        @staticmethod
        def normalize(text: str) -> str:
            if not text: return ""
            # 1. Đổi dấu ngoặc/nháy lạ về chuẩn
            text = re.sub(r'[“”„‟″‴]', '"', text)
            text = re.sub(r'[‘’‚‛′]', "'", text)
            text = re.sub(r'–', '-', text)
            # 2. Sửa lỗi khoảng trắng quanh dấu câu dính liền
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            # 3. Thu gọn nhiều dấu câu lặp lại liên tiếp
            text = re.sub(r'\.{4,}', '...', text)
            text = re.sub(r',+', ',', text)
            text = re.sub(r'!+', '!', text)
            text = re.sub(r'\?+', '?', text)
            # 4. Loại bỏ ký tự lạ, emoji không đọc được
            text = re.sub(r'[^\w\s.,!?;:"\'\-\(\)\[\]\n]', '', text)
            # 5. Tự động viết hoa chữ cái sau dấu chấm câu (. ! ?)
            def capitalize_match(match):
                return match.group(1) + match.group(2).upper()
            text = re.sub(r'([.!?]\s+)([a-zỳỹỷýỵựửữựửứừứợởỡờớảãạảáàạậẩẫậấpấầẩẫậpếềểễệpíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ])', capitalize_match, text)
            # 6. Dọn dẹp khoảng trắng thừa giữa các từ và các dòng
            lines = text.split('\n')
            cleaned_lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines if re.sub(r'[ \t]+', ' ', line).strip()]
            return '\n'.join(cleaned_lines)
    
    class ITTSService(ABC):
        @abstractmethod
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None: pass
    
    class IAudioMerger(ABC):
        @abstractmethod
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None: pass
    
    class IFileRepository(ABC):
        @abstractmethod
        def read_text(self, path: str) -> str: pass
        @abstractmethod
        def write_text(self, path: str, content: str) -> None: pass
    
    # =====================================================================
    # 2. LỚP INFRASTRUCTURE (Cài đặt hạ tầng công nghệ)
    # =====================================================================
    
    class EdgeTTSService(ITTSService):
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            communicate = edge_tts.Communicate(text=text, voice=voice.id, rate=preset.rate, pitch=preset.pitch)
            await communicate.save(output_path)
    
    class PydubAudioMerger(IAudioMerger):
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None:
            if not src_paths: return
            combined = AudioSegment.empty()
            for path in src_paths:
                if os.path.exists(path):
                    combined += AudioSegment.from_mp3(path)
            combined.export(dest_path, format="mp3")
    
    class LocalFileRepository(IFileRepository):
        def read_text(self, path: str) -> str:
            with open(path, "r", encoding="utf-8") as f: return f.read()
        def write_text(self, path: str, content: str) -> None:
            with open(path, "w", encoding="utf-8") as f: f.write(content)
    
    # =====================================================================
    # 3. LỚP APPLICATION (Điều phối kịch bản Usecases)
    # =====================================================================
    
    class TTSOrchestrator:
        def __init__(self, tts_service: ITTSService, audio_merger: IAudioMerger, file_repo: IFileRepository):
            self._tts_service = tts_service
            self._audio_merger = audio_merger
            self._file_repo = file_repo
    
        def normalize_text_path(self, mode: str, source_path: str) -> int:
            """Đọc file text, chạy bộ chuẩn hóa và ghi đè làm sạch dữ liệu"""
            if mode == "file":
                content = self._file_repo.read_text(source_path)
                self._file_repo.write_text(source_path, TextNormalizer.normalize(content))
                return 1
            else:
                txt_files = glob.glob(os.path.join(source_path, "*.txt"))
                for path in txt_files:
                    content = self._file_repo.read_text(path)
                    self._file_repo.write_text(path, TextNormalizer.normalize(content))
                return len(txt_files)
    
        async def process_single_document(self, doc: StoryDocument, voice: Voice, preset: AudioPreset, output_dir: str, progress_cb: Callable[[str], None] = None) -> str:
            chunks = doc.get_chunks(max_chars=2500)
            if not chunks: return ""
            temp_files: List[str] = []
            final_output_path = os.path.join(output_dir, f"{doc.name}.mp3")
            try:
                for idx, chunk in enumerate(chunks):
                    if progress_cb: progress_cb(f"Đang xử lý '{doc.name}': Khối {idx + 1}/{len(chunks)}")
                    temp_path = os.path.join(output_dir, f"temp_{doc.name}_{idx}.mp3")
                    await self._tts_service.convert_chunk_to_mp3(chunk, voice, preset, temp_path)
                    temp_files.append(temp_path)
                if progress_cb: progress_cb(f"Đang gộp âm thanh: {doc.name}.mp3")
                self._audio_merger.merge_mp3_files(temp_files, final_output_path)
            finally:
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        try: os.remove(temp_file)
                        except Exception: pass
            return final_output_path
    
        async def process_batch_directory(self, input_dir: str, voice: Voice, preset: AudioPreset, output_dir: str, progress_cb: Callable[[str], None] = None) -> None:
            txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
            if not txt_files: raise FileNotFoundError("Không thấy file .txt nào trong thư mục!")
            for file_path in txt_files:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                content = self._file_repo.read_text(file_path)
                doc = StoryDocument(name=base_name, text=content)
                await self.process_single_document(doc, voice, preset, output_dir, progress_cb)
    
    # =====================================================================
    # 4. LỚP PRESENTATION (Giao diện người dùng PySide6)
    # =====================================================================
    
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
            self.mode = mode
            self.source_path = source_path
            self.output_dir = output_dir
            self.voice = voice
            self.preset = preset
    
        def run(self):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                def cb(msg): self.progress_signal.emit(msg)
    
                if self.mode == "file":
                    base_name = os.path.splitext(os.path.basename(self.source_path))[0]
                    content = self.orchestrator._file_repo.read_text(self.source_path)
                    doc = StoryDocument(name=base_name, text=content)  
                    loop.run_until_complete(self.orchestrator.process_single_document(doc, self.voice, self.preset, self.output_dir, cb))  
                else:  
                    loop.run_until_complete(self.orchestrator.process_batch_directory(self.source_path, self.voice, self.preset, self.output_dir, cb))  
                    loop.close()  
                    self.finished_signal.emit(True, "Mọi tác vụ xử lý văn bản và gộp âm thanh đã hoàn thành!")  
            except Exception as e:  
                self.finished_signal.emit(False, str(e))

class MainWindow(QMainWindow):  
    def init(self, orchestrator: TTSOrchestrator):  
        super().init()  
        self._orchestrator = orchestrator  
        self.setWindowTitle("SOLID Advance Audiobook Studio")  
        self.setMinimumSize(600, 480)  
        self.source_path = ""  
        self.output_dir = ""  
        self._init_ui()`

    def _init_ui(self):  
        main_widget = QWidget()  
        self.setCentralWidget(main_widget)  
        main_layout = QVBoxLayout(main_widget)  
        main_layout.setSpacing(15)                                                                       

        # Chế độ chạy  
        mode_group = QGroupBox("Chế độ đầu vào")  
        mode_layout = QHBoxLayout(mode_group)  
        self.rad_file = QRadioButton("Xử lý 1 File đơn lẻ (.txt)")  
        self.rad_folder = QRadioButton("Xử lý hàng loạt theo Thư mục")  
        self.rad_file.setChecked(True)  
        self.btn_group = QButtonGroup()  
        self.btn_group.addButton(self.rad_file)  
        self.btn_group.addButton(self.rad_folder)  
        mode_layout.addWidget(self.rad_file)  
        mode_layout.addWidget(self.rad_folder)  
        main_layout.addWidget(mode_group)

        # Đường dẫn  
        path_group = QGroupBox("Cấu hình đường dẫn")  
        path_layout = QVBoxLayout(path_group)  
        h1 = QHBoxLayout()  
        self.lbl_source = QLabel("Chưa chọn file/thư mục nguồn...")  
        btn_select_src = QPushButton("Chọn Nguồn")  
        btn_select_src.clicked.connect(self._select_source)  
        h1.addWidget(self.lbl_source, stretch=3)  
        h1.addWidget(btn_select_src, stretch=1)  
        path_layout.addLayout(h1)

        h2 = QHBoxLayout()  
        self.lbl_output = QLabel("Chưa chọn thư mục lưu MP3...")  
        btn_select_out = QPushButton("Chọn Nơi Lưu")  
        btn_select_out.clicked.connect(self._select_output)  
        h2.addWidget(self.lbl_output, stretch=3)  
        h2.addWidget(btn_select_out, stretch=1)  
        path_layout.addLayout(h2)  
        main_layout.addWidget(path_group)

        # Giọng đọc & cấu hình  
        config_group = QGroupBox("Cấu hình âm thanh")  
        config_layout = QHBoxLayout(config_group)  
        self.genre_combo = QComboBox()  
        self.genre_combo.addItems([p.name for p in PRESETS_DATA])  
        config_layout.addWidget(self.genre_combo)  
        self.voice_combo = QComboBox()  
        self.voice_combo.addItems([v.display_name for v in VOICES_DATA])  
        config_layout.addWidget(self.voice_combo)  
        main_layout.addWidget(config_group)

        # Trạng thái hiển thị  
        self.status_label = QLabel("Sẵn sàng hành động")  
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 13px;")  
        self.status_label.setAlignment(Qt.AlignCenter)  
        main_layout.addWidget(self.status_label)

        # Khung hành động chính (Bổ sung nút chuẩn hóa)  
        action_layout = QHBoxLayout()  
        self.btn_normalize = QPushButton("CHUẨN HÓA VĂN BẢN TRƯỚC")  
        self.btn_normalize.setMinimumHeight(50)  
        self.btn_normalize.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")  
        self.btn_normalize.clicked.connect(self._normalize_text)  
        action_layout.addWidget(self.btn_normalize)

        self.btn_start = QPushButton("XUẤT FILE AUDIO (MP3)")  
        self.btn_start.setMinimumHeight(50)  
        self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")  
        self.btn_start.clicked.connect(self._start_process)  
        action_layout.addWidget(self.btn_start)

        main_layout.addLayout(action_layout)

    def _select_source(self):  
        if self.rad_file.isChecked():  
            file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file văn bản", "", "Text files (*.txt)")  
            if file_path:  
                self.source_path = file_path  
                self.lbl_source.setText(f"File: {os.path.basename(file_path)}")  
         else:  
            dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục nguồn")  
            if dir_path:  
                self.source_path = dir_path  
                self.lbl_source.setText(f"Thư mục: {dir_path}")

    def _select_output(self):  
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục đầu ra")  
        if dir_path:  
            self.output_dir = dir_path  
            self.lbl_output.setText(f"Thư mục đầu ra: {dir_path}")

    def _normalize_text(self):  
        """Hành động xử lý nút bấm chuẩn hóa text"""  
        if not self.source_path:  
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Nguồn (.txt hoặc thư mục) trước khi dọn dẹp văn bản!")  
            return  
        mode = "file" if self.rad_file.isChecked() else "folder"  
        try:  
            count = self._orchestrator.normalize_text_path(mode, self.source_path)  
            QMessageBox.information(self, "Thành công", f"Đã chuẩn hóa, sửa lỗi dấu câu và viết hoa hoàn tất cho {count} tệp tin văn bản văn học gốc!")  
        except Exception as e:  
            QMessageBox.critical(self, "Lỗi", f"Không thể chuẩn hóa tệp: {str(e)}")

    def _start_process(self):  
        if not self.source_path or not self.output_dir:  
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đầy đủ Đường dẫn nguồn và Đích lưu!")  
            return  

        voice = VOICES_DATA[self.voice_combo.currentIndex()]  
        preset = PRESETS_DATA[self.genre_combo.currentIndex()]  
        mode = "file" if self.rad_file.isChecked() else "folder"

        self.btn_start.setEnabled(False)  
        self.btn_normalize.setEnabled(False)  
        self.status_label.setStyleSheet("color: blue;")

        self.worker = QtBatchTTSWorker(self._orchestrator, mode, self.source_path, self.output_dir, voice, preset)  
        self.worker.progress_signal.connect(self.status_label.setText)  
        self.worker.finished_signal.connect(self._on_finished)  
        self.worker.start()

    def _on_finished(self, success, message):  
        self.btn_start.setEnabled(True)  
        self.btn_normalize.setEnabled(True)  
        self.status_label.setText("Sẵn sàng hành động")  
        self.status_label.setStyleSheet("color: green; font-weight: bold;")  
        if success: 
            QMessageBox.information(self, "Hoàn tất", message)  
        else: 
            QMessageBox.critical(self, "Gặp lỗi hệ thống", message)

## =====================================================================

## 5\. KHỞI CHẠY (Composition Root)

## =====================================================================

def main():  
    app = QApplication(sys.argv)

    # Khởi tạo các Module hạ tầng kỹ thuật  
    tts_service = EdgeTTSService()  
    audio_merger = PydubAudioMerger()  
    file_repo = LocalFileRepository()

    # Tiêm dependencies vào lớp điều phối ứng dụng (SOLID - D)  
    orchestrator = TTSOrchestrator(tts_service=tts_service, audio_merger=audio_merger, file_repo=file_repo)

    window = MainWindow(orchestrator=orchestrator)  
    window.show()  
    sys.exit(app.exec())

if name == "main":  
    main()
    
```
### Cách kiểm tra chạy thử và đóng gói qua `uv`
    
1. **Khởi chạy trực tiếp từ terminal để kiểm tra phần mềm:**
       ```bash
       uv run main_advanced.py
    

1. Đóng gói dự án này thành file `.exe` độc lập để sử dụng:
         
         uv run --with PySide6 --with edge-tts --with pydub --with pyinstaller pyinstaller --noconsole --onefile --name="Audiobook_Studio_Pro" main_advanced.py
         




Hệ thống giờ đây đã trở thành một quy trình khép kín hoàn chỉnh, dễ bảo trì, mở rộng và chạy ổn định lâu dài. Chúc bạn có những trải nghiệm tạo audiobook tuyệt vời nhất!