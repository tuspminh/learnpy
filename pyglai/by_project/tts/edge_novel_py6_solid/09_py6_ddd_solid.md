Để tái cấu trúc mã nguồn theo chuẩn DDD (Domain-Driven Design) và SOLID, chúng ta cần tách biệt hoàn toàn phần cốt lõi xử lý nghiệp vụ (Domain/Business Logic) ra khỏi chi tiết công nghệ giao diện (PySide6) và thư viện bên thứ ba (Edge-TTS).

Dưới đây là cấu trúc thư mục được khuyến nghị cho dự án:
    
    
    story_reader/
    │
    ├── domain/                  # Lớp Domain: Chứa thực thể và quy tắc nghiệp vụ thuần túy
    │   ├── __init__.py
    │   ├── models.py            # Thực thể Voice, Preset, Story
    │   └── interfaces.py        # Các giao diện trừu tượng (Abstractions)
    │
    ├── infrastructure/          # Lớp Hạ tầng: Cài đặt cụ thể các công nghệ (Edge-TTS)
    │   ├── __init__.py
    │   └── tts_service.py       # Cài đặt chi tiết việc kết nối và lưu file từ Edge-TTS
    │
    ├── application/             # Lớp Ứng dụng: Điều phối luồng công việc (Use Cases)
    │   ├── __init__.py
    │   └── tts_orchestrator.py  # Điều phối việc nhận text, áp preset và gọi hạ tầng
    │
    └── presentation/            # Lớp Hiển thị: Giao diện người dùng (PySide6 UI)
        ├── __init__.py
        └── main_window.py       # Chỉ xử lý hiển thị, bắt sự kiện và gọi Application layer
    

* * *

## 1\. LỚP DOMAIN (Mô hình nghiệp vụ thuần túy)

Lớp này không phụ thuộc vào bất kỳ thư viện ngoài nào (Kể cả PySide6 hay Edge-TTS). Nó định nghĩa cấu trúc dữ liệu cốt lõi (S - Single Responsibility).

`domain/models.py`:
    
    
    from dataclasses import dataclass
    
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
    class Story:
        text: str
    
        def is_empty(self) -> bool:
            return not self.text.strip()
    

`domain/interfaces.py`:  
Định nghĩa hợp đồng giao tiếp (D - Dependency Inversion Principle).
    
    
    from abc import ABC, abstractmethod
    from domain.models import Voice, AudioPreset
    
    class ITTSService(ABC):
        @abstractmethod
        async def convert_text_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            """Thực hiện chuyển đổi văn bản và ghi trực tiếp ra file mp3"""
            pass
    

* * *

## 2\. LỚP INFRASTRUCTURE (Cài đặt hạ tầng kỹ thuật)

Nơi triển khai các chi tiết công nghệ cụ thể. Nếu sau này bạn đổi sang Google TTS hay OpenAI TTS, bạn chỉ cần tạo một file mới ở đây mà không làm ảnh hưởng đến phần còn lại (O - Open/Closed Principle).

`infrastructure/tts_service.py`:
    
    
    import edge_tts
    from domain.interfaces import ITTSService
    from domain.models import Voice, AudioPreset
    
    class EdgeTTSService(ITTSService):
        async def convert_text_to_mp3(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice.id,
                rate=preset.rate,
                pitch=preset.pitch
            )
            await communicate.save(output_path)
    

* * *

## 3\. LỚP APPLICATION (Luồng xử lý ứng dụng)

Lớp trung gian tiếp nhận yêu cầu từ UI, kết nối Domain Model và gọi Hạ tầng thông qua Interface (D - Dependency Inversion).

`application/tts_orchestrator.py`:
    
    
    from domain.interfaces import ITTSService
    from domain.models import Story, Voice, AudioPreset
    
    class TTSOrchestrator:
        def __init__(self, tts_service: ITTSService):
            self._tts_service = tts_service  # Phụ thuộc vào Interface, không phụ thuộc vào Class cụ thể
    
        async def generate_audiobook(self, text: str, voice: Voice, preset: AudioPreset, output_path: str) -> None:
            story = Story(text=text)
            if story.is_empty():
                raise ValueError("Nội dung truyện không được để trống.")
                
            # Điều phối hạ tầng xử lý tác vụ
            await self._tts_service.convert_text_to_mp3(
                text=story.text,
                voice=voice,
                preset=preset,
                output_path=output_path
            )
    

* * *

## 4\. LỚP PRESENTATION (Giao diện người dùng)

Giao diện PySide6 lúc này đóng vai trò rất "ngốc nghếch", nó chỉ thu thập dữ liệu từ các ô nhập liệu, kích hoạt Thread ngầm và hiển thị thông báo.

`presentation/main_window.py`:
    
    
    import sys
    import asyncio
    from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QTextEdit, QComboBox, QPushButton, 
                                 QFileDialog, QMessageBox, QGroupBox)
    from PySide6.QtCore import Qt, QThread, Signal
    
    from domain.models import Voice, AudioPreset
    from application.tts_orchestrator import TTSOrchestrator
    
    # Dữ liệu tĩnh được ánh xạ trực tiếp sang Domain Models
    VOICES_DATA = [
        Voice("en-US-AriaNeural", "en-US-AriaNeural (Nữ Mỹ - Truyền cảm)", "English"),
        Voice("en-US-JennyNeural", "en-US-JennyNeural (Nữ Mỹ - Cổ tích)", "English"),
        Voice("en-US-GuyNeural", "en-US-GuyNeural (Nam Mỹ - Trầm ấm)", "English"),
        Voice("en-US-SteffanNeural", "en-US-SteffanNeural (Nam Mỹ - Cuốn hút)", "English"),
        Voice("en-GB-SoniaNeural", "en-GB-SoniaNeural (Nữ Anh - Cổ điển)", "English"),
        Voice("en-GB-RyanNeural", "en-GB-RyanNeural (Nam Anh - Tự nhiên)", "English"),
        Voice("vi-VN-HoaiAnNeural", "vi-VN-HoaiAnNeural (Nữ Việt - Dịu dàng)", "Vietnamese"),
        Voice("vi-VN-NamMinhNeural", "vi-VN-NamMinhNeural (Nam Việt - Trầm hùng)", "Vietnamese")
    ]
    
    PRESETS_DATA = [
        AudioPreset("Cổ tích / Thần thoại (Fairy Tales)", "-12%", "+3Hz"),
        AudioPreset("Kinh dị / Trinh thám (Horror / Thriller)", "-16%", "-4Hz"),
        AudioPreset("Ngôn tình / Tâm lý xã hội (Drama / Romance)", "-15%", "-1Hz"),
        AudioPreset("Kiếm hiệp / Tiên hiệp (Fantasy Martial Arts)", "-13%", "-3Hz"),
        AudioPreset("Truyện cười / Thiếu nhi (Fables / Kids)", "-6%", "+5Hz"),
        AudioPreset("Mặc định / Phổ thông (Default)", "+0%", "+0Hz")
    ]
    
    class QtTTSWorker(QThread):
        finished = Signal(bool, str)
    
        def __init__(self, orchestrator: TTSOrchestrator, text: str, voice: Voice, preset: AudioPreset, file_path: str):
            super().__init__()
            self.orchestrator = orchestrator
            self.text = text
            self.voice = voice
            self.preset = preset
            self.file_path = file_path
    
        def run(self):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.orchestrator.generate_audiobook(self.text, self.voice, self.preset, self.file_path)
                )
                loop.close()
                self.finished.emit(True, f"Đã xuất file truyện thành công tại:\n{self.file_path}")
            except Exception as e:
                self.finished.emit(False, str(e))
    
    class MainWindow(QMainWindow):
        def __init__(self, orchestrator: TTSOrchestrator):
            super().__init__()
            self._orchestrator = orchestrator # Dependency Injection qua constructor
            
            self.setWindowTitle("DDD & SOLID Edge-TTS Reader")
            self.setMinimumSize(650, 550)
            self._init_ui()
    
        def _init_ui(self):
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(15)
    
            lbl_text = QLabel("Nhập văn bản truyện:")
            lbl_text.setStyleSheet("font-weight: bold; font-size: 13px;")
            main_layout.addWidget(lbl_text)
    
            self.text_area = QTextEdit()
            self.text_area.setText("Once upon a time, in a deep, magical forest...")
            main_layout.addWidget(self.text_area)
    
            config_group = QGroupBox("Cấu hình giọng đọc nâng cao")
            config_layout = QVBoxLayout(config_group)
            row_layout = QHBoxLayout()
    
            # ComboBox Thể loại
            vbox_genre = QVBoxLayout()
            vbox_genre.addWidget(QLabel("1. Chọn thể loại truyện (Preset):"))
            self.genre_combo = QComboBox()
            self.genre_combo.addItems([p.name for p in PRESETS_DATA])
            self.genre_combo.currentIndexChanged.connect(self._on_preset_changed)
            vbox_genre.addWidget(self.genre_combo)
            row_layout.addLayout(vbox_genre, stretch=1)
    
            # ComboBox Giọng đọc
            vbox_voice = QVBoxLayout()
            vbox_voice.addWidget(QLabel("2. Chọn giọng AI phù hợp:"))
            self.voice_combo = QComboBox()
            self.voice_combo.addItems([v.display_name for v in VOICES_DATA])
            vbox_voice.addWidget(self.voice_combo)
            row_layout.addLayout(vbox_voice, stretch=1)
    
            config_layout.addLayout(row_layout)
    
            self.lbl_info = QLabel()
            self.lbl_info.setStyleSheet("color: #555555; font-size: 11px; font-weight: bold;")
            config_layout.addWidget(self.lbl_info)
            main_layout.addWidget(config_group)
    
            self._on_preset_changed(self.genre_combo.currentIndex())
    
            self.status_label = QLabel("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
            self.status_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.status_label)
    
            self.btn_convert = QPushButton("XUẤT FILE AUDIO (MP3)")
            self.btn_convert.setMinimumHeight(50)
            self.btn_convert.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
            self.btn_convert.clicked.connect(self._start_conversion)
            main_layout.addWidget(self.btn_convert)
    
        def _on_preset_changed(self, index):
            preset = PRESETS_DATA[index]
            self.lbl_info.setText(f"Thông số áp dụng: Tốc độ: {preset.rate} | Cao độ: {preset.pitch}")
    
        def _start_conversion(self):
            text = self.text_area.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập văn bản!")
                return
    
            voice = VOICES_DATA[self.voice_combo.currentIndex()]
            preset = PRESETS_DATA[self.genre_combo.currentIndex()]
    
            file_path, _ = QFileDialog.getSaveFileName(self, "Chọn vị trí lưu", "", "Audio files (*.mp3)")
            if not file_path:
                return
    
            self.btn_convert.setEnabled(False)
            self.status_label.setText("Đang xử lý xuất audio...")
            self.status_label.setStyleSheet("color: #e67e22; font-style: italic;")
    
            self.worker = QtTTSWorker(self._orchestrator, text, voice, preset, file_path)
            self.worker.finished.connect(self._on_conversion_finished)
            self.worker.start()
    
        def _on_conversion_finished(self, success, message):
            self.btn_convert.setEnabled(True)
            self.status_label.setText("Sẵn sàng")
            self.status_label.setStyleSheet("color: green; font-style: italic;")
            if success:
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.critical(self, "Lỗi", message)
    

* * *

## 5\. FILE KHỞI CHẠY (Composition Root)

Nơi khởi tạo toàn bộ các thành phần phụ thuộc và "tiêm" (Inject) chúng vào nhau theo đúng quy tắc kiến trúc.

`main.py` (Đặt ở thư mục gốc ngoài cùng):
    
    
    import sys
    from PySide6.QtWidgets import QApplication
    from infrastructure.tts_service import EdgeTTSService
    from application.tts_orchestrator import TTSOrchestrator
    from presentation.main_window import MainWindow
    
    def main():
        app = QApplication(sys.argv)
        
        # 1. Khởi tạo dịch vụ ở lớp hạ tầng thấp nhất
        infrastructure_service = EdgeTTSService()
        
        # 2. Khởi tạo tầng ứng dụng và "tiêm" hạ tầng vào thông qua Interfaces (SOLID - D)
        application_orchestrator = TTSOrchestrator(tts_service=infrastructure_service)
        
        # 3. Khởi tạo giao diện và "tiêm" tầng ứng dụng vào xử lý hiển thị
        window = MainWindow(orchestrator=application_orchestrator)
        window.show()
        
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
    

## Các nguyên tắc SOLID đã được áp dụng như thế nào?

  * S (Single Responsibility): Mỗi file giữ một vai trò duy nhất. `models.py` lưu dữ liệu, `tts_service.py` chỉ làm việc với API của Edge-TTS, `main_window.py` chỉ xử lý các nút bấm giao diện.
  * O (Open/Closed Principle): Mở rộng dễ dàng bằng cách tạo cấu trúc dữ liệu mới. Nếu muốn thêm `Voice` hoặc `Preset` mới, bạn chỉ cần chỉnh sửa danh sách mảng dữ liệu mà không cần can thiệp logic của hàm tạo file.
  * L (Liskov Substitution Principle): Lớp `EdgeTTSService` hoàn toàn có thể thay thế cho lớp cha trừu tượng `ITTSService` mà không làm thay đổi tính đúng đắn của chương trình ứng dụng.
  * I (Interface Segregation Principle): `ITTSService` cung cấp đúng một chức năng tinh gọn mà tầng ứng dụng cần, không bắt buộc lớp triển khai phải gánh những hàm thừa thãi.
  * D (Dependency Inversion Principle): Lớp ứng dụng nâng cao `TTSOrchestrator` phụ thuộc hoàn toàn vào cổng giao tiếp trừu tượng `ITTSService` thay vì phụ thuộc trực tiếp vào lớp công nghệ chi tiết `EdgeTTSService`.



Nếu bạn muốn cấu trúc các file này trên ổ đĩa để đóng gói bằng `uv`, hãy cho tôi biết nếu có thư mục nào cần giải thích thêm cấu trúc import nhé!