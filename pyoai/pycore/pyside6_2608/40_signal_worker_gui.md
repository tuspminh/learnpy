# Buổi 40 — Signal giữa Worker và GUI

Buổi này là **mảnh ghép quan trọng nhất** để hiểu tại sao `QThread + Worker(QObject)` hoạt động an toàn.

Ở Buổi 39 ta có:

```text
GUI Thread
    │
    │ Signal
    ▼
Worker Thread

Worker Thread
    │
    │ Signal
    ▼
GUI Thread
```

Hôm nay ta đi sâu vào câu hỏi:

> **Khi Signal được emit từ Worker Thread, slot của GUI thực sự chạy ở thread nào?**

---

# 1. Mental Model

Đừng nghĩ Signal/Slot đơn giản như:

```python
signal.connect(slot)
signal.emit()
```

Mà hãy nghĩ:

```text
Signal
   │
   │ emit()
   ▼
Qt Connection
   │
   ├── Direct
   ├── Queued
   ├── BlockingQueued
   └── Auto
```

Qt quyết định **slot sẽ được thực thi như thế nào**.

Đặc biệt khi có nhiều thread:

```text
GUI Thread
    │
    │     queued signal
    │ ◄──────────────────── Worker Thread
    │
    ▼
GUI Event Loop
    │
    ▼
GUI Slot
```

---

# 2. Ví dụ cơ bản

Worker:

```python
from PySide6.QtCore import QObject, Signal, Slot


class Worker(QObject):

    progress = Signal(int)

    @Slot()
    def run(self):
        for i in range(101):
            self.progress.emit(i)
```

GUI:

```python
self.worker.progress.connect(
    self.progress_bar.setValue
)
```

Khi Worker:

```python
self.progress.emit(50)
```

GUI:

```python
self.progress_bar.setValue(50)
```

được gọi.

Nhưng câu hỏi quan trọng là:

```text
setValue()
```

chạy ở đâu?

---

# 3. GUI Thread hay Worker Thread?

Trong thiết kế thông thường:

```text
Worker Thread
      │
      │ emit
      ▼
   Signal
      │
      │ queued
      ▼
GUI Event Loop
      │
      ▼
GUI Thread
      │
      ▼
progress_bar.setValue()
```

Do đó GUI widget được cập nhật trong GUI thread.

---

# 4. Tại sao Qt làm được điều này?

Mỗi `QObject` có:

```text
Thread Affinity
```

Ví dụ:

```text
MainWindow
    ↓
GUI Thread

Worker
    ↓
Worker Thread
```

Qt có thể dựa vào thread affinity của receiver để quyết định cách dispatch slot.

Đây chính là lý do Buổi 39 chúng ta phải học:

```python
worker.moveToThread(thread)
```

---

# 5. Connection Type

Qt có các connection type quan trọng:

```python
Qt.DirectConnection
Qt.QueuedConnection
Qt.BlockingQueuedConnection
Qt.AutoConnection
```

Import:

```python
from PySide6.QtCore import Qt
```

---

# 6. Direct Connection

```python
signal.connect(
    slot,
    Qt.DirectConnection
)
```

Mental model:

```text
emit()
  │
  ▼
slot()
```

Slot được gọi **ngay trong thread đang emit signal**.

Ví dụ:

```text
Worker Thread
    │
    │ emit()
    ▼
    slot()
```

thì:

```text
slot()
→ Worker Thread
```

---

# 7. Đây có thể nguy hiểm

Giả sử:

```python
worker.progress.connect(
    progress_bar.setValue,
    Qt.DirectConnection
)
```

Worker thread emit:

```python
self.progress.emit(50)
```

thì:

```text
Worker Thread
    │
    ▼
QProgressBar.setValue()
```

Bạn đang thao tác GUI widget từ Worker Thread.

**Không nên làm như vậy.**

---

# 8. Queued Connection

```python
signal.connect(
    slot,
    Qt.QueuedConnection
)
```

Mental model:

```text
Worker Thread
     │
     │ emit()
     ▼
Signal Event
     │
     ▼
GUI Event Queue
     │
     ▼
GUI Event Loop
     │
     ▼
slot()
```

Slot chạy trong thread của receiver.

Đây là pattern rất quan trọng cho:

```text
Worker → GUI
```

---

# 9. Ví dụ

```python
worker.progress.connect(
    self.progress_bar.setValue,
    Qt.QueuedConnection
)
```

Worker:

```python
self.progress.emit(50)
```

Flow:

```text
Worker Thread
      │
      ▼
emit(50)
      │
      ▼
Queued Event
      │
      ▼
GUI Event Queue
      │
      ▼
setValue(50)
```

---

# 10. Auto Connection

Thông thường bạn viết:

```python
signal.connect(slot)
```

Qt sử dụng:

```text
Qt.AutoConnection
```

Nếu sender và receiver ở:

### Cùng thread

Qt thường thực hiện kiểu direct.

```text
Thread A
   │
   ├── Sender
   │
   └── Receiver
```

### Khác thread

Qt thường sử dụng queued delivery.

```text
Thread A
   │
   └── Sender
          │
          ▼
       Signal
          │
          ▼
Thread B
   │
   └── Receiver
```

Đây là lý do trong phần lớn trường hợp bạn **không cần tự ghi `Qt.QueuedConnection`**.

---

# 11. Nhưng "Auto" không phải phép màu

Bạn cần hiểu:

```text
AutoConnection
```

được quyết định dựa trên thread context/affinity liên quan tới connection.

Vì vậy đừng suy nghĩ:

> "Signal từ Worker luôn luôn chạy ở GUI."

Không.

Điều đúng hơn là:

> **Slot được dispatch dựa trên connection type và thread affinity của QObject liên quan.**

---

# 12. Một ví dụ rất quan trọng

```python
class Worker(QObject):

    value = Signal(int)

    def run(self):
        self.value.emit(10)
```

GUI:

```python
worker.value.connect(
    self.handle_value
)
```

và:

```python
@Slot(int)
def handle_value(self, value):
    print(value)
```

Nếu:

```text
Worker → Worker Thread
MainWindow → GUI Thread
```

thì:

```text
Worker Thread
    │
    │ emit(10)
    ▼
Qt Queued Delivery
    │
    ▼
GUI Thread
    │
    ▼
handle_value(10)
```

---

# 13. Kiểm tra bằng Python

Đây là bài test rất đáng làm.

```python
import threading
```

Worker:

```python
class Worker(QObject):

    value = Signal()

    @Slot()
    def run(self):
        print(
            "Worker:",
            threading.current_thread().name
        )

        self.value.emit()
```

GUI:

```python
@Slot()
def handle_value(self):
    print(
        "GUI:",
        threading.current_thread().name
    )
```

Bạn sẽ thấy hai execution context khác nhau.

---

# 14. `QThread.currentThread()`

Ngoài Python:

```python
threading.current_thread()
```

có thể kiểm tra Qt:

```python
from PySide6.QtCore import QThread

print(QThread.currentThread())
```

Hoặc:

```python
print(self.thread())
```

Cần phân biệt:

```text
QThread object
```

và:

```text
thread đang thực thi code
```

Đây là một trong những điểm dễ nhầm nhất khi học Qt threading.

---

# 15. Signal truyền dữ liệu

Signal có thể truyền:

```python
Signal(int)
Signal(str)
Signal(float)
Signal(object)
```

Ví dụ:

```python
progress = Signal(int)
message = Signal(str)
result = Signal(object)
```

Worker:

```python
self.progress.emit(50)
self.message.emit("Downloading...")
self.result.emit(result)
```

GUI:

```python
worker.progress.connect(
    self.update_progress
)

worker.message.connect(
    self.update_message
)

worker.result.connect(
    self.show_result
)
```

---

# 16. `Signal(object)`

Rất hữu ích khi truyền Python object:

```python
result = Signal(object)
```

Ví dụ:

```python
result.emit({
    "total": 100,
    "success": 97,
    "failed": 3,
})
```

GUI:

```python
@Slot(object)
def handle_result(self, result):
    print(result)
```

---

# 17. Nhưng đừng lạm dụng `object`

Bạn có thể viết:

```python
result = Signal(object)
```

nhưng nếu API của Worker đã ổn định, tốt hơn là thiết kế payload rõ ràng.

Ví dụ:

```python
result = Signal(CrawlResult)
```

nếu kiến trúc/domain của bạn phù hợp với việc expose type đó.

Hoặc:

```python
result = Signal(object)
```

khi cần linh hoạt.

---

# 18. Nhiều Signal cho một Worker

Một Worker thực tế:

```python
class Worker(QObject):

    started = Signal()
    progress = Signal(int)
    message = Signal(str)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()
```

Architecture:

```text
                  Worker
                    │
       ┌────────────┼────────────┐
       │            │            │
   progress      result        error
       │            │            │
       ▼            ▼            ▼
 ProgressBar      Model       ErrorDialog
```

---

# 19. Signal `started`

Có thể:

```python
thread.started.connect(
    worker.run
)
```

Nhưng nếu muốn Worker có signal:

```python
started = Signal()
```

thì:

```python
@Slot()
def run(self):
    self.started.emit()

    ...
```

GUI có thể:

```python
worker.started.connect(
    self.on_started
)
```

---

# 20. Signal `finished`

Một pattern rất phổ biến:

```python
finished = Signal()
```

Worker:

```python
@Slot()
def run(self):
    try:
        ...
    finally:
        self.finished.emit()
```

GUI:

```python
worker.finished.connect(
    self.on_finished
)
```

Thread:

```python
worker.finished.connect(
    thread.quit
)
```

---

# 21. Error Signal

Ví dụ:

```python
error = Signal(str)
```

Worker:

```python
try:
    result = service.execute()

except Exception as exc:
    self.error.emit(str(exc))

finally:
    self.finished.emit()
```

GUI:

```python
worker.error.connect(
    self.show_error
)
```

---

# 22. Error flow

```text
Worker Thread
     │
     │ exception
     ▼
error.emit(message)
     │
     ▼
Queued Signal
     │
     ▼
GUI Thread
     │
     ▼
show_error()
     │
     ▼
QMessageBox
```

Worker không cần biết:

```text
QMessageBox
MainWindow
QLabel
```

Đây chính là **separation of concerns**.

---

# 23. Worker → GUI và GUI → Worker

Đây mới là architecture quan trọng.

### Worker → GUI

```text
Worker
  │
  │ Signal
  ▼
GUI
```

Ví dụ:

```python
worker.progress.connect(
    self.progress_bar.setValue
)
```

### GUI → Worker

```text
GUI
  │
  │ Signal
  ▼
Worker
```

Ví dụ:

```python
cancel_requested = Signal()
```

GUI:

```python
self.cancel_requested.connect(
    worker.cancel
)
```

Đây sẽ là nền tảng cho **Buổi 42 — Cancel Task**.

---

# 24. Không gọi trực tiếp Worker từ GUI nếu không cần

Ví dụ:

```python
self.worker.cancel()
```

có thể tạo ra vấn đề về thread context tùy cách thiết kế.

Thay vào đó, một architecture rõ ràng là:

```python
cancel_requested = Signal()
```

GUI:

```python
self.cancel_requested.connect(
    worker.cancel
)
```

Khi đó Qt có thể dispatch lời gọi tới Worker thread phù hợp.

---

# 25. Worker nhận command

```python
class Worker(QObject):

    @Slot()
    def cancel(self):
        self._cancelled = True
```

GUI:

```python
self.cancel_requested.emit()
```

Flow:

```text
GUI Thread
    │
    │ emit cancel
    ▼
Queued Connection
    │
    ▼
Worker Thread
    │
    ▼
worker.cancel()
```

Đây là pattern rất đẹp.

---

# 26. Signal-based architecture

Ta có:

```text
GUI
 │
 │ signals
 ▼
Worker
 │
 │ signals
 ▼
GUI
```

Thay vì:

```text
GUI
 │
 ├── gọi Worker
 ├── Worker gọi GUI
 ├── GUI gọi Service
 └── Worker sửa Widget
```

Signal giúp giảm coupling.

---

# 27. Một Worker hoàn chỉnh

```python
from PySide6.QtCore import QObject, Signal, Slot


class Worker(QObject):

    progress = Signal(int)
    message = Signal(str)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service

    @Slot()
    def run(self):
        try:
            self.message.emit("Starting...")

            result = self.service.execute(
                progress_callback=self.progress.emit
            )

            self.result.emit(result)

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self.finished.emit()
```

---

# 28. GUI setup

```python
self.thread = QThread()
self.worker = Worker(service)

self.worker.moveToThread(
    self.thread
)
```

Kết nối:

```python
self.thread.started.connect(
    self.worker.run
)

self.worker.progress.connect(
    self.progress_bar.setValue
)

self.worker.message.connect(
    self.status_label.setText
)

self.worker.result.connect(
    self.handle_result
)

self.worker.error.connect(
    self.handle_error
)

self.worker.finished.connect(
    self.thread.quit
)
```

---

# 29. Toàn bộ flow

```text
                    GUI THREAD
                        │
                ┌───────┴────────┐
                │                │
             Button          Widgets
                │
                │ start
                ▼
             QThread
                │
                │ started
                ▼
             WORKER THREAD
                │
                ▼
             Worker.run()
                │
                ▼
              Service
                │
       ┌────────┼─────────┐
       │        │         │
   progress   result    error
       │        │         │
       └────────┼─────────┘
                │
                ▼
             Signals
                │
                ▼
             GUI THREAD
```

---

# 30. Một vấn đề rất quan trọng: Event Loop

Queued connection cần nơi để event được xử lý.

Với GUI:

```text
QApplication
    ↓
app.exec()
    ↓
GUI Event Loop
```

Với Worker thread:

```text
QThread.start()
    ↓
Worker Thread
    ↓
Event Loop
```

Do đó:

```text
Queued Signal
       ↓
Event Queue
       ↓
Event Loop
```

là một chuỗi logic.

---

# 31. Nếu Worker thread không có event loop?

Đây là lý do Worker Object Pattern khác với:

```python
QThread.run()
```

custom implementation.

Worker Object thường được sử dụng cùng event loop của `QThread`.

Nếu bạn override `QThread.run()` và tự thực hiện một vòng:

```python
while ...:
    ...
```

mà không chạy event loop phù hợp, việc nhận queued commands trong thread đó có thể không hoạt động như bạn mong đợi.

Điểm này cực kỳ quan trọng khi sau này làm:

```text
Pause
Resume
Cancel
```

---

# 32. Direct vs Queued

Hãy nhớ bảng này:

| Connection     | Slot chạy ở đâu?     | Dùng cho                   |
| -------------- | -------------------- | -------------------------- |
| Direct         | thread gọi `emit()`  | trường hợp kiểm soát rõ    |
| Queued         | receiver/event loop  | cross-thread communication |
| Auto           | Qt tự quyết định     | mặc định                   |
| BlockingQueued | sender chờ slot xong | rất cẩn thận               |

---

# 33. `BlockingQueuedConnection`

Ví dụ:

```python
signal.connect(
    slot,
    Qt.BlockingQueuedConnection
)
```

Mental model:

```text
Thread A
   │
   │ emit()
   ▼
Thread B
   │
   │ slot()
   ▼
done
   │
   ▼
Thread A continues
```

Thread A bị block cho tới khi slot hoàn thành.

---

# 34. Vì sao nguy hiểm?

Có thể deadlock.

Ví dụ:

```text
Thread A
    │
    │ waiting B
    ▼
Thread B
    │
    │ waiting A
    ▼
DEADLOCK
```

Vì vậy:

> Không dùng `BlockingQueuedConnection` nếu chưa thực sự hiểu synchronization.

Trong GUI application thông thường:

```text
Auto
Queued
```

là hai loại bạn sẽ dùng nhiều nhất.

---

# 35. `@Slot` có vai trò gì?

Ví dụ:

```python
@Slot(int)
def update_progress(self, value):
    self.progress_bar.setValue(value)
```

Bạn có thể định nghĩa signature rõ ràng:

```python
@Slot(int)
```

hoặc:

```python
@Slot(str)
```

hoặc:

```python
@Slot()
```

Lợi ích:

* API rõ ràng
* Qt meta-object system hiểu slot
* phù hợp hơn với architecture Signal/Slot
* có thể giúp tránh một số vấn đề về dispatch/overhead

---

# 36. GUI Slot

Ví dụ:

```python
@Slot(int)
def on_progress(self, value):
    self.progress_bar.setValue(value)
```

Worker:

```python
progress = Signal(int)
```

Kết nối:

```python
worker.progress.connect(
    self.on_progress
)
```

Architecture rất rõ:

```text
Signal(int)
     ↓
Slot(int)
```

---

# 37. Không nên nhồi logic vào GUI Slot

Không nên:

```python
@Slot(int)
def on_progress(self, value):
    calculate_something_expensive()
    parse_huge_data()
    self.progress_bar.setValue(value)
```

Nếu:

```text
on_progress()
```

chạy trên GUI thread thì:

```text
calculate_something_expensive()
```

có thể freeze UI.

GUI slot nên nhẹ:

```python
@Slot(int)
def on_progress(self, value):
    self.progress_bar.setValue(value)
```

---

# 38. Signal truyền dữ liệu lớn

Ví dụ:

```python
result.emit(huge_python_object)
```

không có nghĩa là:

```text
zero-cost transfer
```

Bạn vẫn đang truyền dữ liệu giữa các execution contexts.

Do đó với dữ liệu rất lớn:

```text
10 MB
100 MB
1 GB
```

cần cân nhắc architecture.

Thay vì:

```text
Worker
   ↓ huge object
GUI
```

có thể:

```text
Worker
   ↓
Repository / File
   ↓
GUI
   ↓
load needed data
```

Đây sẽ rất hữu ích với Story Reader.

---

# 39. Ví dụ Story Reader

Worker:

```python
chapter_found = Signal(object)
```

Crawler:

```text
HTTP
 ↓
Parser
 ↓
Chapter
```

Worker:

```python
self.chapter_found.emit(chapter)
```

GUI:

```python
worker.chapter_found.connect(
    self.on_chapter_found
)
```

Flow:

```text
Crawler
   ↓
Chapter
   ↓
Worker Signal
   ↓
GUI Thread
   ↓
Model
   ↓
QListView
```

Đây là nơi kiến thức Model/View của **Phần II** quay trở lại.

---

# 40. Kết hợp Model/View

Ví dụ:

```python
@Slot(object)
def on_chapter_found(self, chapter):
    self.model.add_chapter(chapter)
```

Bạn không làm:

```python
worker
   ↓
QListWidget.addItem()
```

mà:

```text
Worker
   ↓
Signal
   ↓
GUI/controller
   ↓
Model
   ↓
View
```

Architecture sạch hơn rất nhiều.

---

# 41. Worker không biết View

Đây là nguyên tắc:

```text
Worker
  ❌ MainWindow
  ❌ QLabel
  ❌ QListView
  ❌ QProgressBar

Worker
  ✅ Signal
  ✅ Service
```

GUI:

```text
MainWindow
  ✅ Widget
  ✅ View
  ✅ Presentation Model
  ✅ Signal connection
```

---

# 42. Một kiến trúc rất tốt

```text
              Presentation
                   │
              MainWindow
                   │
            ┌──────┴──────┐
            │             │
          View         Controller
                            │
                            ▼
                         Worker
                            │
                            ▼
                       Application
                         Service
                            │
                            ▼
                         Domain
                            │
                            ▼
                       Repository
```

Thread:

```text
MainWindow
    ↓
GUI Thread

Worker
    ↓
Worker Thread
```

---

# 43. Bài tập 1 — Xác định thread

Tạo:

```text
MainWindow
Worker
QThread
```

In:

```python
threading.current_thread().name
```

ở:

```text
1. Button handler
2. Worker.run()
3. Worker signal
4. GUI slot
```

Mục tiêu:

```text
Button handler → MainThread
Worker.run()   → Worker thread
GUI slot       → MainThread
```

---

# 44. Bài tập 2 — Progress

Tạo:

```text
QProgressBar
Worker
QThread
```

Worker:

```python
progress = Signal(int)
```

GUI:

```python
worker.progress.connect(
    self.on_progress
)
```

Không được:

```python
worker → progress_bar
```

---

# 45. Bài tập 3 — Message

Worker:

```python
message = Signal(str)
```

Emit:

```text
"Connecting..."
"Downloading..."
"Parsing..."
"Saving..."
"Finished"
```

GUI hiển thị bằng:

```text
QLabel
```

---

# 46. Bài tập 4 — Result

Worker:

```python
result = Signal(object)
```

Service:

```python
return {
    "success": 100,
    "failed": 3,
}
```

Worker:

```python
self.result.emit(result)
```

GUI hiển thị:

```text
Success: 100
Failed: 3
```

---

# 47. Bài tập 5 — Error

Service:

```python
raise RuntimeError(
    "Connection failed"
)
```

Worker:

```python
error = Signal(str)
```

GUI:

```python
@Slot(str)
def on_error(self, message):
    QMessageBox.critical(
        self,
        "Error",
        message,
    )
```

---

# 48. Bài tập 6 — Hai chiều

Thiết kế:

```text
GUI
 │
 │ start_requested
 ▼
Worker
 │
 │ progress
 ▼
GUI
 │
 │ cancel_requested
 ▼
Worker
```

Đây là architecture chúng ta sẽ tiếp tục dùng ở:

**Buổi 42 — Cancel Task.**

---

# 49. Bài tập 7 — `AutoConnection`

Thử:

```python
worker.progress.connect(
    self.on_progress
)
```

Sau đó thử:

```python
worker.progress.connect(
    self.on_progress,
    Qt.QueuedConnection
)
```

So sánh behavior.

Mục tiêu là hiểu rằng:

```text
Auto
```

thường đủ cho cross-thread signal/slot khi object/thread affinity được thiết kế đúng.

---

# 50. Bài tập 8 — Direct Connection

Thử:

```python
worker.progress.connect(
    self.on_progress,
    Qt.DirectConnection
)
```

Trong:

```python
@Slot(int)
def on_progress(self, value):
    print(
        threading.current_thread().name
    )
```

Bạn sẽ thấy tại sao Direct Connection cần cực kỳ cẩn thận khi crossing threads.

**Không dùng cách này để update GUI trong production.**

---

# 51. Bài tập 9 — Story Crawler

Thiết kế:

```text
CrawlWorker
```

với:

```python
started = Signal()
progress = Signal(int)
chapter_found = Signal(object)
message = Signal(str)
error = Signal(str)
finished = Signal()
```

Architecture:

```text
CrawlWorker
     │
     ├── started
     ├── progress
     ├── chapter_found
     ├── message
     ├── error
     └── finished
```

GUI chỉ subscribe vào những gì cần.

---

# 52. Checklist Buổi 40

Bạn cần nắm chắc:

### `DirectConnection`

```text
slot chạy trong thread gọi emit
```

### `QueuedConnection`

```text
slot được đưa vào event queue
```

### `AutoConnection`

```text
Qt tự chọn cách phù hợp
```

### Cross-thread communication

```text
Signal → Queued → Receiver Thread
```

### Worker → GUI

```text
Signal
```

### GUI → Worker

```text
Signal
```

### GUI widget

```text
Chỉ thao tác ở GUI Thread
```

### Worker

```text
Không biết GUI
```

### `@Slot`

```text
Khai báo rõ receiver/slot
```

---

# 53. Mental Model cuối buổi

Nếu chỉ nhớ **một sơ đồ**, hãy nhớ sơ đồ này:

```text
                    GUI THREAD
                ┌─────────────────┐
                │                 │
                │   MainWindow    │
                │       │         │
                │       ▼         │
                │    GUI Slot     │
                │                 │
                └───────▲─────────┘
                        │
                  Queued Signal
                        │
                        │
                ┌───────┴─────────┐
                │  WORKER THREAD  │
                │                 │
                │    Worker       │
                │       │         │
                │       ▼         │
                │    Service      │
                │       │         │
                │       ▼         │
                │   progress.emit │
                │                 │
                └─────────────────┘
```

Và architecture hai chiều:

```text
                 GUI THREAD
                    │
          ┌─────────┴─────────┐
          │                   │
          │ start/cancel      │
          ▼                   │
       Signal             Signal
          │                   ▲
          ▼                   │
      WORKER THREAD           │
          │                   │
          ├── progress ───────┤
          ├── result ─────────┤
          ├── error ──────────┤
          └── finished ───────┘
```

**Công thức của Buổi 40:**

```text
QObject
   +
Thread Affinity
   +
Signal / Slot
   +
Event Loop
   =
Cross-thread communication
```

Đây là nền tảng để sang **Buổi 41 — Progress Bar**: chúng ta sẽ xây một Worker thực tế có **progress %, current item, total, message**, rồi thiết kế cách cập nhật `QProgressBar` mà không làm GUI freeze.
