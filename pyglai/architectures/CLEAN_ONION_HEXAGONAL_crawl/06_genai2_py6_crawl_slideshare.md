Dưới đây là thiết kế và triển khai lại ứng dụng theo **Clean Architecture**, thay thế lớp Presentation từ **Click CLI** sang giao diện người dùng đồ họa **PySide6 (Qt for Python)**.

Nhờ tuân thủ Clean Architecture, toàn bộ lớp **Domain**, **Use Cases**, và **Infrastructure** từ phần trước **giữ nguyên 100%**. Chúng ta chỉ cần tạo một lớp Presentation mới cho GUI.

---

### 1. Cấu trúc thư mục được cập nhật

```text
slideshare_downloader/
├── src/
│   ├── domain/                         # Giữ nguyên
│   │   ├── entities.py
│   │   └── exceptions.py
│   │
│   ├── use_cases/                      # Giữ nguyên
│   │   ├── interfaces/
│   │   │   ├── crawler.py
│   │   │   └── pdf_exporter.py
│   │   └── download_slide.py
│   │
│   ├── infrastructure/                 # Giữ nguyên
│   │   ├── crawler/
│   │   │   └── playwright_crawler.py
│   │   └── exporter/
│   │       └── reportlab_exporter.py
│   │
│   └── presentation/                   # [CẬP NHẬT] Giao diện PySide6
│       └── gui.py                      # PySide6 Application Window & Worker Thread
│
├── requirements.txt                    # Thêm PySide6
└── main.py                             # Khởi chạy PySide6 App

```

---

### 2. Triển khai Lớp Presentation mới (PySide6 GUI)

Do tải dữ liệu từ internet và tạo PDF có thể gây treo/lag giao diện (UI Freeze), ứng dụng sử dụng `QThread` và `Signal` để đưa Use Case chạy dưới nền (Background Thread).

```python
# src/presentation/gui.py
import sys
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QProgressBar
)

from src.infrastructure.crawler.playwright_crawler import BeautifulSoupCrawler
from src.infrastructure.exporter.reportlab_exporter import PillowPDFExporter
from src.use_cases.download_slide import DownloadSlideUseCase


class DownloadWorker(QThread):
    """Worker Thread để thực thi Use Case dưới nền mà không làm treo UI."""
    finished_signal = Signal(str)
    error_signal = Signal(str)
    log_signal = Signal(str)

    def __init__(self, use_case: DownloadSlideUseCase, url: str, output_path: str):
        super().__init__()
        self.use_case = use_case
        self.url = url
        self.output_path = output_path

    def run(self):
        try:
            self.log_signal.emit("🔍 Đang kết nối và cào dữ liệu từ SlideShare...")
            result_path = self.use_case.execute(self.url, self.output_path)
            self.finished_signal.emit(result_path)
        except Exception as e:
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SlideShare Book/Slide Downloader (Clean Architecture)")
        self.resize(600, 350)

        # 1. Dependency Injection Setup
        crawler = BeautifulSoupCrawler()
        exporter = PillowPDFExporter()
        self.use_case = DownloadSlideUseCase(crawler=crawler, exporter=exporter)

        # 2. Xây dựng Giao diện
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(12)

        # Title Header
        title_label = QLabel("Tải Slide / Book từ SlideShare ra PDF")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Form Input URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL Slide:")
        url_label.setFixedWidth(80)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.slideshare.net/slideshow/...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Form Input Output Path
        output_layout = QHBoxLayout()
        output_label = QLabel("Lưu tại:")
        output_label.setFixedWidth(80)
        self.output_input = QLineEdit("slide_output.pdf")
        self.browse_btn = QPushButton("Chọn nơi lưu")
        self.browse_btn.clicked.connect(self._select_output_file)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.browse_btn)
        layout.addLayout(output_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate status
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Download Button
        self.download_btn = QPushButton("🚀 Tải về và Xuất PDF")
        self.download_btn.setStyleSheet("font-weight: bold; padding: 8px; background-color: #0d6efd; color: white;")
        self.download_btn.clicked.connect(self._start_download)
        layout.addWidget(self.download_btn)

        # Log Window
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Nhật ký hệ thống...")
        layout.addWidget(self.log_area)

    def _select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Chọn vị trí lưu file PDF", "slide_output.pdf", "PDF Files (*.pdf)"
        )
        if file_path:
            self.output_input.setText(file_path)

    def _start_download(self):
        url = self.url_input.text().strip()
        output_path = self.output_input.text().strip()

        if not url:
            self.log_area.append("❌ Lỗi: Vui lòng nhập URL SlideShare.")
            return

        # Vô hiệu hóa nút và hiện thanh tiến trình
        self.download_btn.setEnabled(False)
        self.progress_bar.show()
        self.log_area.clear()

        # Tạo và chạy Background Thread
        self.worker = DownloadWorker(self.use_case, url, output_path)
        self.worker.log_signal.connect(self.log_area.append)
        self.worker.finished_signal.connect(self._on_success)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_success(self, result_path: str):
        self.log_area.append(f" Success! File đã được lưu tại: {result_path}")
        self._reset_ui_state()

    def _on_error(self, error_msg: str):
        self.log_area.append(f"❌ Lỗi: {error_msg}")
        self._reset_ui_state()

    def _reset_ui_state(self):
        self.download_btn.setEnabled(True)
        self.progress_bar.hide()


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

```

---

### 3. File Khởi chạy (Entry Point)

Thay đổi file `main.py` ở thư mục gốc để khởi chạy GUI thay vì CLI:

```python
# main.py
from src.presentation.gui import run_app

if __name__ == "__main__":
    run_app()

```

---

### 4. File cấu hình `requirements.txt`

Cập nhật danh sách thư viện (thay `click` bằng `PySide6`):

```text
PySide6>=6.5.0
requests>=2.28.0
beautifulsoup4>=4.11.0
Pillow>=9.0.0

```

---

### 5. Lợi ích thu được từ Clean Architecture trong lần thay đổi này

* **Không ảnh hưởng logic nghiệp vụ:** Các file trong `domain/`, `use_cases/`, và `infrastructure/` không hề bị đụng đến hay sửa đổi dù chuyển từ CLI màn hình đen sang ứng dụng Desktop có giao diện đồ họa.
* **Tách biệt luồng UI và Logic (Asynchronous execution):** Bằng cách inject `DownloadSlideUseCase` vào `QThread` của PySide6, giao diện người dùng không bao giờ bị đơ (Not Responding) trong khi đang tải dữ liệu.