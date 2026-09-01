# Buổi 42 — Cancel Task

Đây là buổi rất quan trọng trong phần Threading.

Ở Buổi 41 ta có:

```text
Worker
   │
   │ progress
   ▼
GUI
   │
   ▼
QProgressBar
```

Bây giờ ta muốn:

```text
GUI
 │
 │ Cancel
 ▼
Worker
 │
 ▼
dừng task
```

Nhưng có một nguyên tắc quan trọng:

> **Không dùng `QThread.terminate()` để cancel task thông thường.**

Thay vào đó, ta dùng **cooperative cancellation**:

```text
GUI yêu cầu cancel
        ↓
Worker nhận yêu cầu
        ↓
Worker tự kiểm tra
        ↓
Worker dừng tại điểm an toàn
```

---

# 1. Mental Model

Có hai kiểu "cancel".

### Hard cancellation

```text
GUI
 │
 ▼
terminate thread
 │
 ▼
💥 Worker bị giết
```

### Cooperative cancellation

```text
GUI
 │
 │ cancel_requested
 ▼
Worker
 │
 │ kiểm tra flag
 ▼
if cancelled:
    return
```

Ta sẽ sử dụng cách thứ hai.

---

# 2. Tại sao không `terminate()`?

Qt có:

```python
thread.terminate()
```

Nhưng đây là cách rất nguy hiểm cho application logic.

Giả sử Worker đang:

```text
BEGIN TRANSACTION
       ↓
WRITE DATABASE
       ↓
WRITE FILE
       ↓
UPDATE STATE
```

Nếu bị terminate giữa chừng:

```text
BEGIN TRANSACTION
       ↓
WRITE DATABASE
       ↓
💥 TERMINATE
```

State có thể trở nên không nhất quán.

---

# 3. Cooperative Cancellation

Worker có một trạng thái:

```python
self._cancel_requested = False
```

Khi GUI yêu cầu cancel:

```python
self._cancel_requested = True
```

Worker định kỳ kiểm tra:

```python
if self._cancel_requested:
    return
```

Flow:

```text
Worker
 │
 ▼
Task
 │
 ├── check cancelled
 │
 ├── do work
 │
 ├── check cancelled
 │
 ├── do work
 │
 └── check cancelled
```

---

# 4. Worker đơn giản

```python
from PySide6.QtCore import QObject, Signal, Slot
import time


class Worker(QObject):

    progress = Signal(int)
    finished = Signal()
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self._cancel_requested = False

    @Slot()
    def run(self):
        for i in range(101):

            if self._cancel_requested:
                self.cancelled.emit()
                return

            time.sleep(0.05)

            self.progress.emit(i)

        self.finished.emit()
```

---

# 5. Thêm `cancel()`

```python
@Slot()
def cancel(self):
    self._cancel_requested = True
```

Bây giờ Worker có:

```text
run()
cancel()
```

```python
class Worker(QObject):

    @Slot()
    def run(self):
        ...

    @Slot()
    def cancel(self):
        self._cancel_requested = True
```

---

# 6. Nhưng GUI không nên gọi trực tiếp

Không nên ưu tiên:

```python
self.worker.cancel()
```

Ta thiết kế Signal:

```python
cancel_requested = Signal()
```

GUI:

```python
self.cancel_requested.emit()
```

Kết nối:

```python
self.cancel_requested.connect(
    self.worker.cancel
)
```

Flow:

```text
GUI Thread
    │
    │ cancel_requested.emit()
    ▼
Queued Connection
    │
    ▼
Worker Thread
    │
    ▼
worker.cancel()
```

Đây chính là kiến thức của Buổi 40.

---

# 7. GUI có Start + Cancel

```python
self.start_button = QPushButton("Start")
self.cancel_button = QPushButton("Cancel")

self.start_button.clicked.connect(
    self.start_task
)

self.cancel_button.clicked.connect(
    self.request_cancel
)
```

Cancel:

```python
@Slot()
def request_cancel(self):
    self.cancel_requested.emit()
```

---

# 8. Tạo Signal

Trong MainWindow:

```python
from PySide6.QtCore import Signal


class MainWindow(QMainWindow):

    cancel_requested = Signal()
```

Sau đó:

```python
self.cancel_requested.connect(
    self.worker.cancel
)
```

---

# 9. Toàn bộ Worker

```python
class Worker(QObject):

    progress = Signal(int)
    finished = Signal()
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self._cancel_requested = False

    @Slot()
    def run(self):
        for i in range(101):

            if self._cancel_requested:
                self.cancelled.emit()
                return

            time.sleep(0.05)

            self.progress.emit(i)

        self.finished.emit()

    @Slot()
    def cancel(self):
        self._cancel_requested = True
```

---

# 10. Một vấn đề quan trọng

Giả sử:

```python
time.sleep(10)
```

Worker đang ngủ.

GUI:

```text
Cancel
```

Worker không thể kiểm tra:

```python
if self._cancel_requested:
```

cho tới khi:

```text
10 giây
```

trôi qua.

Do đó:

> **Cancellation chỉ có hiệu lực khi Worker có cơ hội kiểm tra cancellation.**

---

# 11. Cancellation Point

Ta gọi:

```text
Cancellation Point
```

là nơi Worker kiểm tra:

```python
if self._cancel_requested:
```

Ví dụ:

```python
for item in items:

    if self._cancel_requested:
        return

    process(item)
```

Có một cancellation point sau mỗi item.

---

# 12. Cancellation càng nhanh càng tốt

Không nên:

```python
for item in items:

    process_1000_items()

    if cancelled:
        return
```

vì:

```text
Cancel
 ↓
chờ process_1000_items()
 ↓
mới stop
```

Tốt hơn:

```python
for item in items:

    if cancelled:
        return

    process(item)
```

---

# 13. Cancellation với Crawler

Đây là ví dụ rất gần project của bạn.

```python
for chapter in chapters:

    if self._cancel_requested:
        self.cancelled.emit()
        return

    crawl(chapter)
```

Flow:

```text
Chapter 1
   ↓
check cancel
   ↓
crawl

Chapter 2
   ↓
check cancel
   ↓
crawl

Chapter 3
   ↓
check cancel
   ↓
Cancel!
```

Worker dừng ở ranh giới giữa các chapter.

Đây là điểm dừng khá an toàn.

---

# 14. Cancellation với File Processing

```python
for path in files:

    if self._cancel_requested:
        self.cancelled.emit()
        return

    process_file(path)
```

Nếu:

```text
1000 files
```

thì cancellation latency thường nằm quanh thời gian xử lý một file.

---

# 15. Cancellation với Download

Download phức tạp hơn.

Ví dụ:

```python
while True:

    chunk = response.read()

    if self._cancel_requested:
        break

    write(chunk)
```

Nhưng còn phụ thuộc:

```text
HTTP library
socket
timeout
blocking read
```

Nếu `read()` đang block rất lâu:

```text
GUI
 │
Cancel
 ▼
Worker
 │
 │ waiting read()
 │
 └───────────────┐
                 │
              blocked
```

Cancel flag chưa đủ.

Đây là vấn đề chúng ta sẽ gặp ở:

**Buổi 47 — PySide6 + HTTP.**

---

# 16. Cancellation State

Tôi khuyến nghị dùng một state rõ ràng:

```text
IDLE
RUNNING
CANCEL_REQUESTED
CANCELLED
FINISHED
FAILED
```

Ví dụ:

```text
IDLE
 ↓
RUNNING
 ↓
CANCEL_REQUESTED
 ↓
CANCELLED
```

Hoặc:

```text
IDLE
 ↓
RUNNING
 ↓
FINISHED
```

---

# 17. Đừng nhầm Cancel Requested với Cancelled

Đây là một distinction rất quan trọng.

### `cancel_requested`

```text
GUI nói:
"hãy dừng"
```

### `cancelled`

```text
Worker xác nhận:
"tôi đã dừng"
```

Flow:

```text
GUI
 │
 │ cancel_requested
 ▼
Worker
 │
 │ kiểm tra
 ▼
Worker dừng
 │
 │ cancelled
 ▼
GUI
```

---

# 18. Vì sao cần hai trạng thái?

Ví dụ GUI click:

```text
Cancel
```

Nhưng Worker đang:

```text
processing current file
```

Ngay lúc đó task **chưa cancelled**.

Nó chỉ:

```text
cancel requested
```

Sau khi Worker tới cancellation point:

```text
cancelled
```

---

# 19. Signal đầy đủ

Worker:

```python
class Worker(QObject):

    started = Signal()
    progress = Signal(int)
    finished = Signal()
    cancelled = Signal()
    error = Signal(str)
```

Flow:

```text
started
   ↓
progress
   ↓
progress
   ↓
cancelled
```

hoặc:

```text
started
   ↓
progress
   ↓
finished
```

hoặc:

```text
started
   ↓
error
```

---

# 20. Worker thực tế hơn

```python
class Worker(QObject):

    started = Signal()
    progress = Signal(int)
    finished = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._cancel_requested = False

    @Slot()
    def run(self):
        self.started.emit()

        try:
            for i in range(101):

                if self._cancel_requested:
                    self.cancelled.emit()
                    return

                time.sleep(0.05)

                self.progress.emit(i)

        except Exception as exc:
            self.error.emit(str(exc))
            return

        self.finished.emit()

    @Slot()
    def cancel(self):
        self._cancel_requested = True
```

---

# 21. GUI xử lý Cancel

```python
@Slot()
def on_cancelled(self):
    self.progress.setValue(0)
    self.status_label.setText(
        "Cancelled"
    )

    self.start_button.setEnabled(True)
    self.cancel_button.setEnabled(False)
```

---

# 22. GUI xử lý Finished

```python
@Slot()
def on_finished(self):
    self.progress.setValue(100)

    self.status_label.setText(
        "Finished"
    )

    self.start_button.setEnabled(True)
    self.cancel_button.setEnabled(False)
```

---

# 23. State của Button

Khi task chạy:

```text
Start     → disabled
Cancel    → enabled
```

Khi task kết thúc:

```text
Start     → enabled
Cancel    → disabled
```

Ví dụ:

```python
@Slot()
def on_started(self):
    self.start_button.setEnabled(False)
    self.cancel_button.setEnabled(True)
```

---

# 24. State Machine đơn giản

GUI có thể có:

```text
IDLE
RUNNING
CANCEL_REQUESTED
```

Ví dụ:

```text
IDLE
 │
 │ Start
 ▼
RUNNING
 │
 │ Cancel
 ▼
CANCEL_REQUESTED
 │
 │ Worker confirms
 ▼
IDLE
```

Không nhất thiết phải dùng `QStateMachine`.

Chỉ cần Python state:

```python
self.state = "idle"
```

là đủ cho project nhỏ.

---

# 25. Không cho Cancel nhiều lần

Nếu:

```text
RUNNING
```

thì:

```text
Cancel → enabled
```

Nếu:

```text
CANCEL_REQUESTED
```

thì:

```text
Cancel → disabled
```

Ví dụ:

```python
@Slot()
def request_cancel(self):
    self.cancel_button.setEnabled(False)
    self.cancel_requested.emit()
```

---

# 26. Race condition

Có thể xảy ra:

```text
Worker                  GUI

process last item
                         Cancel
finished.emit()
                         cancel_requested
```

Task đã gần hoàn thành.

Có thể:

```text
finished
```

xảy ra trước:

```text
cancel
```

Do đó GUI không nên giả định:

```text
Cancel clicked
→ chắc chắn Cancelled
```

Cancellation là một **request**, không phải guarantee tức thời.

---

# 27. `thread.quit()` và Cancel

Khi Worker emit:

```python
self.cancelled.emit()
```

ta vẫn cần:

```python
self.thread.quit()
```

Ví dụ:

```python
self.worker.cancelled.connect(
    self.thread.quit
)

self.worker.finished.connect(
    self.thread.quit
)

self.worker.error.connect(
    self.thread.quit
)
```

Như vậy mọi terminal state đều kết thúc thread.

---

# 28. Một thiết kế tốt

```text
                 Worker
                   │
          ┌────────┼─────────┐
          │        │         │
       finished cancelled  error
          │        │         │
          └────────┼─────────┘
                   ▼
              thread.quit()
```

---

# 29. Không gọi `terminate()`

Tránh:

```python
self.thread.terminate()
```

trong flow thông thường.

Đặc biệt tránh kiểu:

```python
def cancel(self):
    self.thread.terminate()
```

Worker không nên tự quyết định terminate thread.

---

# 30. `requestInterruption()`

Qt còn cung cấp:

```python
QThread.requestInterruption()
```

và:

```python
QThread.isInterruptionRequested()
```

Ví dụ:

```python
self.thread.requestInterruption()
```

Worker có thể kiểm tra:

```python
if QThread.currentThread().isInterruptionRequested():
    return
```

---

# 31. Ví dụ

```python
from PySide6.QtCore import QThread


@Slot()
def run(self):

    for i in range(101):

        if QThread.currentThread().isInterruptionRequested():
            self.cancelled.emit()
            return

        time.sleep(0.05)
        self.progress.emit(i)

    self.finished.emit()
```

GUI:

```python
self.thread.requestInterruption()
```

---

# 32. Hai cách cancellation

### Custom flag

```python
self._cancel_requested = True
```

### Qt interruption

```python
thread.requestInterruption()
```

và Worker:

```python
QThread.currentThread().isInterruptionRequested()
```

Cả hai đều hướng tới:

```text
cooperative cancellation
```

---

# 33. Khi nào dùng custom flag?

Custom flag rất tiện khi domain có nhiều trạng thái:

```text
pause
resume
cancel
```

Ví dụ:

```python
self._cancel_requested
self._pause_requested
```

Hoặc khi muốn encapsulate cancellation trong Worker.

---

# 34. Khi nào dùng `requestInterruption()`?

Nếu chỉ cần:

```text
running
   ↓
stop requested
```

thì Qt interruption là một lựa chọn đơn giản.

Ví dụ:

```python
self.thread.requestInterruption()
```

Worker:

```python
if QThread.currentThread().isInterruptionRequested():
    return
```

---

# 35. Cancellation Token

Nếu muốn architecture tốt hơn, ta có thể tạo abstraction:

```python
class CancellationToken:

    def __init__(self):
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self):
        return self._cancelled
```

Worker:

```python
if self.token.is_cancelled():
    return
```

Điều này rất hữu ích khi tách:

```text
UI
Application
Worker
Service
```

---

# 36. Application Service không cần biết PySide6

Đây là kiến trúc tôi muốn bạn hướng tới.

Thay vì:

```python
Service
   ↓
QThread
   ↓
QProgressBar
```

hãy:

```text
PySide6
   ↓
Worker
   ↓
Application Service
   ↓
Domain
```

Service nhận cancellation abstraction:

```python
service.execute(
    cancellation_token=token
)
```

Service:

```python
for item in items:

    if token.is_cancelled():
        return

    process(item)
```

---

# 37. Đây là Clean Architecture

Bạn đã học Clean Architecture / DDD, nên hãy kết nối các kiến thức:

```text
┌─────────────────────────────┐
│         PySide6 UI          │
│                             │
│ Start / Cancel / Progress   │
└──────────────┬──────────────┘
               │
            Worker
               │
               ▼
┌─────────────────────────────┐
│    Application Service      │
│                             │
│ execute(token, progress)    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           Domain            │
└─────────────────────────────┘
```

Worker chỉ là **adapter giữa Qt threading và application logic**.

---

# 38. Progress + Cancel

Kết hợp Buổi 41:

```text
Worker
 ├── progress
 ├── finished
 ├── cancelled
 └── error
```

GUI:

```text
QProgressBar
QLabel
Start
Cancel
```

Flow:

```text
Start
  ↓
Worker.run()
  ↓
progress ───────────► QProgressBar
  ↓
progress
  ↓
Cancel
  ↓
cancel_requested
  ↓
Worker detects
  ↓
cancelled ──────────► GUI
```

---

# 39. Ví dụ Crawler hoàn chỉnh

```python
class CrawlWorker(QObject):

    progress = Signal(int, int)
    chapter_found = Signal(object)
    message = Signal(str)

    finished = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler
        self._cancel_requested = False

    @Slot()
    def cancel(self):
        self._cancel_requested = True

    @Slot()
    def run(self):
        try:
            chapters = self.crawler.discover()

            total = len(chapters)

            for current, chapter in enumerate(
                chapters,
                start=1,
            ):

                if self._cancel_requested:
                    self.cancelled.emit()
                    return

                self.message.emit(
                    f"Crawling {chapter.title}"
                )

                result = self.crawler.crawl(
                    chapter
                )

                self.chapter_found.emit(
                    result
                )

                self.progress.emit(
                    current,
                    total,
                )

        except Exception as exc:
            self.error.emit(str(exc))
            return

        self.finished.emit()
```

---

# 40. Điểm dừng an toàn

Crawler:

```text
discover
   ↓
chapter 1
   ↓
SAVE
   ↓
chapter 2
   ↓
SAVE
   ↓
chapter 3
   ↓
CANCEL
```

Worker dừng **giữa các chapter**, thay vì giữa transaction hoặc giữa thao tác ghi dữ liệu.

Đây là cách thiết kế cancellation tốt.

---

# 41. Cancellation trong Transaction

Ví dụ:

```python
with transaction():
    save_story()
    save_chapters()
```

Không nên:

```python
if cancelled:
    return
```

ở giữa một transaction mà chưa hiểu transaction semantics.

Tốt hơn:

```text
check cancellation
       ↓
BEGIN
       ↓
complete atomic operation
       ↓
COMMIT
       ↓
check cancellation
```

Cancellation nên xảy ra ở **boundary an toàn**.

---

# 42. Cancellation Boundary

Đây là khái niệm quan trọng:

```text
Cancellation Boundary
```

Ví dụ:

```text
File
Chapter
HTTP request
Database transaction
Batch
```

Ta quyết định:

> Worker được phép dừng ở đâu?

Ví dụ crawler:

```text
chapter boundary
```

Download:

```text
chunk boundary
```

Database:

```text
transaction boundary
```

---

# 43. Bài tập 1 — Basic Cancel

Tạo:

```text
Start
Cancel
QProgressBar
```

Worker:

```python
for i in range(101):
    ...
```

Click:

```text
Cancel
```

phải dừng.

---

# 44. Bài tập 2 — Cancel State

Tạo:

```text
IDLE
RUNNING
CANCEL_REQUESTED
```

Button:

```text
IDLE
→ Start enabled
→ Cancel disabled
```

```text
RUNNING
→ Start disabled
→ Cancel enabled
```

```text
CANCEL_REQUESTED
→ Start disabled
→ Cancel disabled
```

---

# 45. Bài tập 3 — Cancellation latency

Thử:

```python
time.sleep(0.1)
```

sau đó:

```python
time.sleep(1)
```

Quan sát:

```text
Cancel
 ↓
Worker actually stops
```

Từ đó hiểu:

> Cancellation latency phụ thuộc vào nơi Worker có thể kiểm tra cancellation.

---

# 46. Bài tập 4 — Crawler

Giả lập:

```text
100 chapters
```

Mỗi chapter:

```python
time.sleep(0.5)
```

Cho phép:

```text
Start
Cancel
```

Cancel chỉ có hiệu lực giữa hai chapter.

---

# 47. Bài tập 5 — `requestInterruption()`

Thay:

```python
self._cancel_requested
```

bằng:

```python
QThread.currentThread().isInterruptionRequested()
```

GUI:

```python
self.thread.requestInterruption()
```

So sánh hai thiết kế.

---

# 48. Bài tập 6 — Progress + Cancel

UI:

```text
┌───────────────────────────┐
│ Downloading               │
│                           │
│ ███████████░░░░░ 63%      │
│                           │
│ 63 / 100                  │
│                           │
│ [ Cancel ]                │
└───────────────────────────┘
```

Worker:

```text
progress
cancelled
finished
error
```

---

# 49. Bài tập 7 — Story Reader

Thiết kế:

```text
StoryCrawlerWorker
```

Signals:

```python
started
progress
chapter_found
message
cancelled
finished
error
```

Flow:

```text
GUI
 │
 │ start
 ▼
Worker
 │
 ▼
Crawler
 │
 ├── chapter_found
 ├── progress
 ├── message
 │
 │ cancel
 ▼
cancelled
```

Đây chính là phiên bản đầu tiên của **Crawler Dashboard**.

---

# 50. Những lỗi cần tránh

### ❌ `terminate()`

```python
thread.terminate()
```

### ❌ Worker trực tiếp sửa GUI

```python
worker.progress_bar.setValue(...)
```

### ❌ GUI trực tiếp can thiệp state nội bộ Worker

```python
worker._cancel_requested = True
```

### ❌ Không có cancellation point

```python
while huge_operation:
    do_everything()
```

### ❌ Cho rằng Cancel = task đã dừng

```text
Cancel clicked
≠
Worker stopped
```

### ❌ Emit signal quá mức

```text
millions of progress signals
```

---

# 51. Kiến trúc chuẩn hiện tại

Sau Buổi 42, ta đã có:

```text
                  GUI THREAD
                      │
       ┌──────────────┼──────────────┐
       │              │              │
     Start          Cancel        Widgets
       │              │
       ▼              ▼
    Signal        Signal
       │              │
       └──────┬───────┘
              ▼
        WORKER THREAD
              │
              ▼
           Worker
              │
              ▼
          Service
              │
              ▼
            Task
              │
       ┌──────┴───────┐
       │              │
    progress       check cancel
       │              │
       └──────┬───────┘
              ▼
             GUI
```

---

# 52. Mental Model cuối buổi

Hãy nhớ 5 bước:

```text
1. GUI gửi cancellation request
             ↓
2. Worker nhận request
             ↓
3. Worker kiểm tra cancellation
             ↓
4. Worker dừng tại safe point
             ↓
5. Worker emit cancelled
```

Hay:

```text
Cancel ≠ Kill
```

Mà:

```text
Cancel = Request Worker tự dừng một cách an toàn
```

Đây là nguyên tắc cực kỳ quan trọng khi xây **Download Manager**, **Crawler**, **File Processor**, **Import/Export** bằng PySide6.

**Buổi tiếp theo — Buổi 43: `QThreadPool`** sẽ chuyển từ mô hình:

```text
1 QThread
    +
1 Worker
    =
1 Task
```

sang:

```text
             QThreadPool
          ┌──────┼──────┐
          ▼      ▼      ▼
       Task 1  Task 2  Task 3
          │      │      │
        Thread Thread Thread
```

Đây là bước chuyển rất quan trọng từ **single background task** sang **nhiều task đồng thời**.
