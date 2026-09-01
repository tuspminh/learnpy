# Buổi 41 — Progress Bar với QThread + Worker

Buổi 40 chúng ta đã hiểu:

```text
Worker Thread
     │
     │ Signal
     ▼
GUI Thread
```

Hôm nay ta áp dụng trực tiếp vào một bài toán thực tế:

> **Worker chạy công việc dài → phát progress → GUI cập nhật `QProgressBar`.**

Đây là nền tảng cho **Download Manager**, **Crawler Dashboard**, **Import/Export**, **File Processing**...

---

# 1. Mental Model

Một Progress Bar tốt không nên được thiết kế như:

```text
Worker
   │
   └── progress_bar.setValue()
```

Mà phải là:

```text
Worker
   │
   │ progress.emit(50)
   ▼
Signal
   │
   ▼
GUI Slot
   │
   ▼
QProgressBar
```

Kiến trúc:

```text
┌──────────────────────┐
│      GUI Thread      │
│                      │
│   QProgressBar       │
│        ▲             │
│        │             │
│   on_progress()      │
└────────┼─────────────┘
         │
     Signal(int)
         │
┌────────┴─────────────┐
│    Worker Thread     │
│                      │
│      Worker          │
│         │            │
│         ▼            │
│    Long Task         │
└──────────────────────┘
```

---

# 2. Vì sao không update trực tiếp?

Sai:

```python
class Worker(QObject):

    def run(self):
        for i in range(101):
            self.progress_bar.setValue(i)
```

Vấn đề:

```text
Worker Thread
      │
      ▼
QProgressBar
```

Qt GUI widgets không nên bị thao tác từ Worker Thread.

Worker chỉ nên:

```python
self.progress.emit(i)
```

---

# 3. Worker cơ bản

```python
from PySide6.QtCore import QObject, Signal, Slot
import time


class Worker(QObject):

    progress = Signal(int)
    finished = Signal()

    @Slot()
    def run(self):
        for i in range(101):
            time.sleep(0.05)
            self.progress.emit(i)

        self.finished.emit()
```

Worker không biết gì về:

```text
QProgressBar
QMainWindow
QLabel
```

---

# 4. GUI

```python
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QThread
```

Window:

```python
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.progress = QProgressBar()
        self.button = QPushButton("Start")

        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.button.clicked.connect(
            self.start_worker
        )
```

---

# 5. Tạo Thread + Worker

```python
def start_worker(self):
    self.thread = QThread()
    self.worker = Worker()

    self.worker.moveToThread(self.thread)

    self.thread.started.connect(
        self.worker.run
    )

    self.worker.progress.connect(
        self.progress.setValue
    )

    self.worker.finished.connect(
        self.thread.quit
    )

    self.thread.start()
```

Flow:

```text
Button
  │
  ▼
start_worker()
  │
  ├── create QThread
  ├── create Worker
  ├── move Worker
  └── thread.start()
          │
          ▼
       Worker.run()
          │
          ▼
    progress.emit()
          │
          ▼
      QProgressBar
```

---

# 6. Nhưng nên dùng Slot

Thay vì:

```python
self.worker.progress.connect(
    self.progress.setValue
)
```

Ta có thể viết:

```python
@Slot(int)
def on_progress(self, value):
    self.progress.setValue(value)
```

Sau đó:

```python
self.worker.progress.connect(
    self.on_progress
)
```

Tôi khuyến nghị cách này cho application lớn.

Tại sao?

Vì sau này ta có thể:

```python
@Slot(int)
def on_progress(self, value):
    self.progress.setValue(value)

    self.status_label.setText(
        f"{value}%"
    )
```

GUI presentation logic nằm tập trung trong GUI.

---

# 7. Thêm QLabel

GUI:

```python
self.label = QLabel("Ready")
```

Worker:

```python
progress = Signal(int)
```

GUI:

```python
@Slot(int)
def on_progress(self, value):
    self.progress.setValue(value)
    self.label.setText(
        f"{value}%"
    )
```

---

# 8. Progress không chỉ là %

Trong ứng dụng thực tế:

```text
37%
```

thường chưa đủ.

Ta có thể cần:

```text
37 / 100
```

hoặc:

```text
37 / 100 files
```

hoặc:

```text
Downloading chapter 37 / 100
```

Do đó Signal có thể truyền nhiều dữ liệu.

---

# 9. Signal nhiều tham số

```python
progress = Signal(int, int)
```

Ý nghĩa:

```text
current
total
```

Worker:

```python
self.progress.emit(
    current,
    total,
)
```

GUI:

```python
@Slot(int, int)
def on_progress(self, current, total):
    percent = int(
        current * 100 / total
    )

    self.progress.setValue(percent)
```

---

# 10. Thiết kế tốt hơn

Worker:

```python
progress = Signal(int, int)
```

Không để Worker tính UI:

```python
# Không cần
percent = ...
```

Worker chỉ biết:

```text
current
total
```

GUI quyết định:

```text
current + total
        ↓
percentage
        ↓
QProgressBar
```

Điều này giúp Worker độc lập với presentation.

---

# 11. Thêm message

Ta có:

```python
progress = Signal(int, int)
message = Signal(str)
```

Worker:

```python
self.message.emit(
    "Processing files..."
)

self.progress.emit(
    current,
    total,
)
```

GUI:

```python
@Slot(str)
def on_message(self, message):
    self.label.setText(message)
```

---

# 12. Worker hoàn chỉnh

```python
class Worker(QObject):

    progress = Signal(int, int)
    message = Signal(str)
    finished = Signal()

    @Slot()
    def run(self):
        total = 100

        for current in range(1, total + 1):
            time.sleep(0.05)

            self.progress.emit(
                current,
                total,
            )

            self.message.emit(
                f"Processing {current}/{total}"
            )

        self.finished.emit()
```

---

# 13. GUI hoàn chỉnh

```python
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.progress = QProgressBar()
        self.label = QLabel("Ready")
        self.button = QPushButton("Start")

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.button.clicked.connect(
            self.start_worker
        )

    def start_worker(self):
        self.progress.setValue(0)

        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.progress.connect(
            self.on_progress
        )

        self.worker.message.connect(
            self.on_message
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.on_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    @Slot(int, int)
    def on_progress(self, current, total):
        percent = int(
            current * 100 / total
        )

        self.progress.setValue(percent)

    @Slot(str)
    def on_message(self, message):
        self.label.setText(message)

    @Slot()
    def on_finished(self):
        self.label.setText("Done")
```

---

# 14. Một vấn đề quan trọng: giữ reference

Bạn thấy:

```python
self.thread = QThread()
self.worker = Worker()
```

chứ không:

```python
thread = QThread()
worker = Worker()
```

Tại sao?

Vì GUI cần giữ reference tới các object này trong lifecycle của task.

Đây là một trong những lý do chúng ta học `QObject` lifetime ở Buổi 2.

---

# 15. Lifecycle

Ta có:

```text
start
  │
  ▼
QThread created
  │
  ▼
Worker created
  │
  ▼
moveToThread
  │
  ▼
thread.start()
  │
  ▼
worker.run()
  │
  ▼
finished
  │
  ▼
thread.quit()
  │
  ▼
thread.finished
```

---

# 16. Cleanup

Một pattern thường dùng:

```python
self.worker.finished.connect(
    self.thread.quit
)

self.worker.finished.connect(
    self.worker.deleteLater
)

self.thread.finished.connect(
    self.thread.deleteLater
)
```

Flow:

```text
Worker
  │
  │ finished
  ├──────────────► worker.deleteLater()
  │
  └──────────────► thread.quit()
                         │
                         ▼
                  thread.finished
                         │
                         ▼
                  thread.deleteLater()
```

---

# 17. Nhưng `deleteLater()` không phải `del`

Đây là điểm quan trọng.

```python
del self.worker
```

là Python reference management.

Trong khi:

```python
self.worker.deleteLater()
```

là yêu cầu Qt schedule việc destruction của `QObject`.

Hai cơ chế khác nhau.

---

# 18. Progress Bar Determinate

Nếu biết tổng số:

```python
progress.setRange(0, 100)
```

Ví dụ:

```text
0% ─────────────── 100%
```

Đây gọi là:

```text
Determinate Progress
```

---

# 19. Indeterminate Progress

Nếu không biết tổng:

```python
progress.setRange(0, 0)
```

Qt sẽ hiển thị dạng:

```text
[ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ]
       moving
```

Mental model:

```text
Known total
    ↓
0 → 100
```

versus:

```text
Unknown total
    ↓
Busy indicator
```

---

# 20. Ví dụ Download

Khi HTTP response có:

```text
Content-Length: 100 MB
```

ta biết:

```text
total = 100 MB
```

Worker:

```python
progress.emit(
    downloaded,
    total,
)
```

GUI:

```text
Downloaded: 37 MB / 100 MB
████████░░░░░░░░
37%
```

Đây chính là nền tảng của **Download Manager** ở Buổi 48.

---

# 21. Progress theo bytes

Thay vì:

```python
Signal(int, int)
```

có thể:

```python
progress = Signal(int, int)
```

với:

```text
downloaded_bytes
total_bytes
```

GUI:

```python
@Slot(int, int)
def on_progress(self, downloaded, total):
    percent = downloaded * 100 // total
    self.progress.setValue(percent)
```

---

# 22. Hiển thị tốc độ

Worker có thể gửi:

```python
progress = Signal(
    int,
    int,
    float,
)
```

Ý nghĩa:

```text
downloaded
total
speed
```

GUI:

```text
37 MB / 100 MB
37%
2.4 MB/s
```

Nhưng hãy nhớ:

> Worker nên truyền **data**, GUI quyết định **presentation**.

---

# 23. Một thiết kế tốt hơn nữa

Thay vì Signal có quá nhiều tham số:

```python
progress = Signal(
    int,
    int,
    float,
    str,
    str,
)
```

có thể tạo một object:

```python
@dataclass
class ProgressInfo:
    current: int
    total: int
    speed: float
    message: str
```

Signal:

```python
progress = Signal(object)
```

Worker:

```python
info = ProgressInfo(
    current=current,
    total=total,
    speed=speed,
    message="Downloading",
)

self.progress.emit(info)
```

GUI:

```python
@Slot(object)
def on_progress(self, info):
    ...
```

Với project lớn, cách này dễ mở rộng hơn.

---

# 24. Progress trong Crawler

Đây là nơi rất gần với project Story Reader của bạn.

Giả sử:

```text
Crawler
   ↓
100 chapters
```

Worker:

```python
for index, chapter in enumerate(chapters, 1):

    crawl(chapter)

    self.progress.emit(
        index,
        100,
    )
```

GUI:

```text
Crawling
████████████░░░░░░
63 / 100
```

---

# 25. Progress không nhất thiết phải là Task %

Ví dụ crawler:

```text
Discover stories
Download metadata
Download chapters
Parse content
Save database
```

Có thể có:

```text
Phase
```

và:

```text
Progress
```

Ví dụ:

```python
phase = Signal(str)
progress = Signal(int, int)
```

Worker:

```python
self.phase.emit("Downloading chapters")
self.progress.emit(37, 100)
```

GUI:

```text
Downloading chapters

████████░░░░░░░░
37 / 100
```

---

# 26. Hai loại progress

Một application lớn thường có:

### Overall progress

```text
Task
████████████░░░░ 65%
```

### Current item progress

```text
Chapter 37

██████░░░░ 60%
```

Ví dụ Download Manager:

```text
Overall
3 / 10 files

File 3
67 MB / 100 MB
```

Kiến trúc:

```text
Worker
 ├── overall_progress
 └── item_progress
```

---

# 27. Không emit progress quá nhanh

Đây là một vấn đề thực tế.

Ví dụ:

```python
for i in range(1_000_000):
    self.progress.emit(i, 1_000_000)
```

Bạn đang tạo cực kỳ nhiều signal.

GUI có thể bị ngập event:

```text
Worker
 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
Signal Queue
 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
GUI
```

Không phải cứ emit càng nhiều càng tốt.

---

# 28. Throttle progress

Có thể chỉ emit mỗi:

```text
50 ms
100 ms
200 ms
```

hoặc khi % thay đổi.

Ví dụ:

```python
last_percent = -1

for current in range(total):

    percent = current * 100 // total

    if percent != last_percent:
        last_percent = percent
        self.progress.emit(
            current,
            total,
        )
```

Từ:

```text
100000 signals
```

có thể giảm xuống:

```text
100 signals
```

---

# 29. Bài tập 1

Tạo:

```text
QProgressBar
QPushButton
Worker
QThread
```

Worker thực hiện:

```python
for i in range(101):
    sleep(0.05)
    emit(i)
```

GUI hiển thị:

```text
0 → 100%
```

---

# 30. Bài tập 2

Đổi Signal:

```python
Signal(int)
```

thành:

```python
Signal(int, int)
```

Truyền:

```text
current
total
```

GUI tự tính:

```python
percent = current * 100 // total
```

---

# 31. Bài tập 3

Thêm:

```python
message = Signal(str)
```

GUI hiển thị:

```text
Processing 37/100
```

---

# 32. Bài tập 4

Thêm:

```text
QLabel
QProgressBar
```

Hiển thị:

```text
Processing file 37/100

████████████░░░░░░░░ 37%
```

---

# 33. Bài tập 5 — File Processing

Giả lập:

```text
100 files
```

Worker:

```text
file 1
file 2
...
file 100
```

GUI:

```text
Processing files

37 / 100

███████░░░░░░░
```

---

# 34. Bài tập 6 — Crawler

Thiết kế:

```python
class CrawlWorker(QObject):

    progress = Signal(int, int)
    chapter_found = Signal(object)
    message = Signal(str)
    finished = Signal()
```

Flow:

```text
Crawl
 ↓
Chapter 1
 ↓
chapter_found
 ↓
Chapter 2
 ↓
chapter_found
 ↓
...
```

Progress:

```text
1 / 100
2 / 100
...
100 / 100
```

---

# 35. Bài tập 7 — Download

Thiết kế:

```python
progress = Signal(int, int)
```

với:

```text
downloaded_bytes
total_bytes
```

GUI hiển thị:

```text
37.2 MB / 100 MB

███████░░░░░░ 37%

Speed: 2.4 MB/s
```

Đây là bài tập chuẩn bị trực tiếp cho:

> **Buổi 47 — PySide6 + HTTP**

và:

> **Buổi 48 — Download Manager**

---

# 36. Checklist Buổi 41

Bạn cần hiểu:

### Worker không update GUI

```text
Worker
   ❌
QProgressBar
```

### Worker emit data

```text
Worker
   │
   ▼
Signal
```

### GUI nhận data

```text
Signal
   │
   ▼
Slot
   │
   ▼
QProgressBar
```

### Progress có thể là

```text
percent
current / total
bytes
speed
phase
message
```

### Không emit quá mức

```text
Throttle
```

### Có thể có

```text
Overall Progress
Current Item Progress
```

---

# 37. Mental Model cuối buổi

Hãy nhớ kiến trúc này:

```text
                 GUI THREAD
        ┌─────────────────────────┐
        │                         │
        │     QProgressBar        │
        │           ▲             │
        │           │             │
        │     on_progress()       │
        │           ▲             │
        └───────────┼─────────────┘
                    │
              Queued Signal
                    │
                    │
        ┌───────────┴─────────────┐
        │      WORKER THREAD      │
        │                         │
        │        Worker           │
        │           │             │
        │           ▼             │
        │      Long-running       │
        │         Task             │
        │           │             │
        │           ▼             │
        │   progress.emit(...)    │
        └─────────────────────────┘
```

Công thức:

```text
Worker
   ↓
emit(data)
   ↓
Queued Signal
   ↓
GUI Slot
   ↓
QProgressBar
```

Và đây chính là nền tảng để sang **Buổi 42 — Cancel Task**:

```text
GUI
 │
 │ cancel_requested
 ▼
Worker
 │
 │ kiểm tra cancellation
 ▼
Long-running Task
```

Ở Buổi 42, chúng ta sẽ xử lý bài toán khó hơn: **làm thế nào dừng Worker một cách an toàn mà không `terminate()` và không làm hỏng state của ứng dụng.**
