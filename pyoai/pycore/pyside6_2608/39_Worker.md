# Buổi 39 — Worker Object Pattern

Đây là một trong những buổi **quan trọng nhất của phần Threading & Concurrency**.

Ở Buổi 38, ta đã thấy hai cách:

```text
Cách 1:
class WorkerThread(QThread):
    def run():
        ...

Cách 2:
QThread
    +
Worker(QObject)
```

Hôm nay chúng ta tập trung vào **Cách 2**.

> **Mental model cốt lõi:** `QThread` quản lý thread, còn `Worker(QObject)` chứa công việc.

---

# 1. Vấn đề của việc subclass `QThread`

Ví dụ:

```python
class CrawlThread(QThread):

    def run(self):
        crawler.crawl()
```

Cách này có thể chạy được.

Nhưng dần dần class sẽ phình to:

```python
class CrawlThread(QThread):

    def run(self):
        connect_database()
        crawl()
        parse()
        save()
        update_progress()
        handle_error()
        cleanup()
```

Ta đang trộn:

```text
Thread management
+
Business logic
+
Application logic
```

vào một class.

Đây không phải thiết kế tốt cho application lớn.

---

# 2. Worker Object Pattern

Ta tách:

```text
QThread
    │
    │ quản lý thread
    ▼
Worker
    │
    │ thực hiện task
    ▼
Business operation
```

Ví dụ:

```python
from PySide6.QtCore import QObject


class CrawlWorker(QObject):

    def run(self):
        crawler.crawl()
```

Thread:

```python
thread = QThread()
worker = CrawlWorker()

worker.moveToThread(thread)
```

---

# 3. Mental Model

Hãy ghi nhớ:

```text
┌─────────────────────────────┐
│        GUI THREAD           │
│                             │
│       MainWindow            │
│           │                 │
│           │ start           │
│           ▼                 │
│        QThread ──────────────┼────┐
└─────────────────────────────┘    │
                                   ▼
                         ┌─────────────────┐
                         │ WORKER THREAD   │
                         │                 │
                         │ Worker(QObject) │
                         │                 │
                         │ run()           │
                         │ crawl()         │
                         │ download()      │
                         └─────────────────┘
```

---

# 4. Worker là `QObject`

Ví dụ:

```python
from PySide6.QtCore import QObject


class Worker(QObject):

    def run(self):
        print("Working...")
```

Không:

```python
class Worker(QThread):
    ...
```

mà:

```python
class Worker(QObject):
    ...
```

---

# 5. Tạo `QThread`

```python
from PySide6.QtCore import QThread


thread = QThread()
```

Lúc này:

```text
thread
   ↓
QThread object
```

Nó chưa chạy.

---

# 6. Tạo Worker

```python
worker = Worker()
```

Theo mặc định, worker được tạo trong thread hiện tại.

Nếu tạo từ GUI:

```text
GUI Thread
    │
    └── Worker
```

---

# 7. `moveToThread()`

Bây giờ:

```python
worker.moveToThread(thread)
```

Mental model:

```text
Before:

GUI Thread
    │
    └── Worker


After:

GUI Thread
    │
    └── QThread

Worker Thread
    │
    └── Worker
```

Worker đã có thread affinity tới thread mới.

---

# 8. `moveToThread()` không chạy Worker

Đây là điểm cực kỳ quan trọng.

```python
worker.moveToThread(thread)
```

**không có nghĩa:**

```text
Worker.run()
```

được thực thi ngay.

Nó chỉ thay đổi:

```text
QObject thread affinity
```

Để chạy worker:

```python
thread.start()
```

và thường kết nối:

```python
thread.started.connect(worker.run)
```

---

# 9. Flow đầy đủ

```python
thread = QThread()
worker = Worker()

worker.moveToThread(thread)

thread.started.connect(worker.run)

thread.start()
```

Flow:

```text
thread.start()
      │
      ▼
Worker Thread
      │
      ▼
thread.started
      │
      ▼
worker.run()
```

---

# 10. Tại sao dùng Signal để bắt đầu Worker?

Ta có:

```python
thread.started.connect(worker.run)
```

Khi thread bắt đầu:

```text
QThread
   │
   │ started
   ▼
Worker.run()
```

Qt sẽ dispatch lời gọi theo cơ chế signal/slot.

Đây là một điểm rất quan trọng của Worker Object Pattern.

---

# 11. Worker không biết GUI

Worker:

```python
class Worker(QObject):

    def run(self):
        result = do_work()
```

Worker không cần:

```python
self.window
self.label
self.progress_bar
```

Thay vào đó:

```python
class Worker(QObject):

    result = Signal(object)

    def run(self):
        result = do_work()
        self.result.emit(result)
```

---

# 12. GUI nhận Result

GUI:

```python
worker.result.connect(
    self.handle_result
)
```

Flow:

```text
Worker Thread
     │
     │ result.emit(data)
     ▼
Qt Signal
     │
     ▼
GUI Event Queue
     │
     ▼
GUI Thread
     │
     ▼
handle_result()
```

Đây là architecture rất đẹp:

```text
Worker
  ↓
Signal
  ↓
Presentation
```

---

# 13. Worker có thể có nhiều Signal

Ví dụ crawler:

```python
class CrawlWorker(QObject):

    progress = Signal(int)
    chapter_found = Signal(object)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()
```

Ý nghĩa:

```text
progress
    ↓
ProgressBar

chapter_found
    ↓
Update model

result
    ↓
Show result

error
    ↓
QMessageBox

finished
    ↓
Cleanup
```

---

# 14. Worker Pattern chuẩn

Một Worker thường có dạng:

```python
class Worker(QObject):

    started = Signal()
    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    @Slot()
    def run(self):
        ...
```

Có thể dùng:

```python
from PySide6.QtCore import Slot
```

và:

```python
@Slot()
def run(self):
    ...
```

`@Slot` không phải bắt buộc trong mọi trường hợp, nhưng rất hữu ích khi thiết kế signal/slot rõ ràng.

---

# 15. Ví dụ hoàn chỉnh

```python
import time

from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class Worker(QObject):

    progress = Signal(int)
    finished = Signal()

    @Slot()
    def run(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress.emit(i)

        self.finished.emit()
```

GUI:

```python
class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.button = QPushButton("Start")
        self.progress = QProgressBar()
        self.label = QLabel("Ready")

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.progress)
        layout.addWidget(self.label)

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

        self.worker.finished.connect(
            self.on_finished
        )

        self.button.clicked.connect(
            self.start
        )

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def on_finished(self):
        self.label.setText("Finished")
```

---

# 16. Flow của code

Khi:

```python
self.thread.start()
```

xảy ra:

```text
GUI Thread
    │
    │ start()
    ▼
Worker Thread
    │
    ▼
thread.started
    │
    ▼
worker.run()
```

Worker:

```text
0
 ↓
1
 ↓
2
 ↓
...
 ↓
100
```

mỗi bước:

```python
self.progress.emit(i)
```

GUI nhận:

```python
self.progress.setValue(i)
```

---

# 17. `time.sleep()` bây giờ khác hoàn toàn

Worker có:

```python
time.sleep(0.03)
```

nhưng nó đang chạy ở:

```text
Worker Thread
```

không phải:

```text
GUI Thread
```

nên:

```text
Worker Thread
    ↓
sleep()
```

trong khi:

```text
GUI Thread
    ↓
Event Loop
    ↓
tiếp tục chạy
```

Kết quả:

```text
GUI RESPONSIVE
```

---

# 18. Đây chính là mục tiêu

Trước:

```text
GUI Thread
    │
    └── long task
           ↓
         FREEZE
```

Sau:

```text
GUI Thread
    │
    ├── UI
    └── Event Loop
             ↕
          Signals
             ↕
       Worker Thread
             │
             └── long task
```

---

# 19. Worker không nên sửa UI

Sai:

```python
class Worker(QObject):

    def run(self):
        self.progress_bar.setValue(50)
```

Tại sao?

Worker đang ở:

```text
Worker Thread
```

nhưng `QProgressBar` thuộc:

```text
GUI Thread
```

Không nên thao tác trực tiếp.

Đúng:

```python
class Worker(QObject):

    progress = Signal(int)

    def run(self):
        self.progress.emit(50)
```

GUI:

```python
worker.progress.connect(
    progress_bar.setValue
)
```

---

# 20. Separation of Concerns

Worker:

```text
Do work
```

GUI:

```text
Display work
```

Ví dụ:

```text
Worker
    │
    │ "50%"
    ▼
Signal
    │
    ▼
GUI
    │
    ▼
ProgressBar
```

Worker không biết ProgressBar tồn tại.

---

# 21. Worker cũng không nên biết `MainWindow`

Tránh:

```python
class Worker(QObject):

    def __init__(self, window):
        self.window = window
```

Sau đó:

```python
self.window.label.setText(...)
```

Bạn đang tạo coupling:

```text
Worker
   ↓
MainWindow
```

Đây là điều chúng ta đã cố gắng loại bỏ ở phần UI Architecture.

---

# 22. Worker nên phụ thuộc vào Service

Ví dụ Story Reader:

```python
class CrawlWorker(QObject):

    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler
```

Sau đó:

```python
def run(self):
    self.crawler.crawl()
```

Architecture:

```text
GUI
 ↓
Worker
 ↓
Crawler Service
 ↓
Repository
```

Worker chỉ là bridge giữa:

```text
Qt concurrency
```

và:

```text
Application/Domain logic
```

---

# 23. Đây là một điểm rất quan trọng

Worker **không nhất thiết phải chứa business logic**.

Ví dụ:

```python
class CrawlWorker(QObject):

    def run(self):
        self.crawler.crawl()
```

Worker chỉ orchestration.

Business logic nằm ở:

```text
Crawler
```

Điều này cực kỳ phù hợp với:

```text
Clean Architecture
DDD
SOLID
```

mà chúng ta đã học.

---

# 24. Architecture đẹp

```text
                    Presentation
                         │
                    MainWindow
                         │
                         ▼
                       Worker
                         │
                         ▼
                 Application Service
                         │
                         ▼
                    Domain Service
                         │
                         ▼
                    Repository
                         │
                         ▼
                     SQLite
```

Threading:

```text
MainWindow
    │
    │ GUI Thread
    ▼
Worker
    │
    │ Worker Thread
    ▼
Application Service
```

---

# 25. Worker có thể emit Domain Result

Ví dụ:

```python
class CrawlResult:
    ...
```

Worker:

```python
result = self.crawler.crawl()

self.result.emit(result)
```

GUI:

```python
worker.result.connect(
    self.show_result
)
```

Không cần truyền Widget vào Worker.

---

# 26. Error Handling

Worker không nên để exception biến mất.

Sai:

```python
def run(self):
    self.service.execute()
```

nếu exception xảy ra, architecture có thể không xử lý được theo ý muốn.

Tốt hơn:

```python
class Worker(QObject):

    error = Signal(str)
    finished = Signal()

    def run(self):
        try:
            self.service.execute()

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self.finished.emit()
```

---

# 27. Nhưng `except Exception` không nên nuốt exception

Đừng:

```python
except Exception:
    pass
```

Đây là anti-pattern.

Ít nhất phải:

```python
except Exception as exc:
    self.error.emit(str(exc))
```

Production còn nên:

```text
logging
exception traceback
structured error
```

---

# 28. `finished` nên luôn được phát?

Thông thường ta muốn:

```text
success
   ↓
finished

error
   ↓
finished
```

Nên:

```python
try:
    ...
except Exception as exc:
    self.error.emit(str(exc))
finally:
    self.finished.emit()
```

Điều này giúp lifecycle predictable hơn.

---

# 29. Cleanup

Một pattern:

```python
worker.finished.connect(
    thread.quit
)
```

Sau đó:

```python
thread.finished.connect(
    worker.deleteLater
)
```

và:

```python
thread.finished.connect(
    thread.deleteLater
)
```

Tuy nhiên cần hiểu lifecycle trước khi áp dụng máy móc.

Mental model:

```text
Worker finished
      ↓
thread.quit()
      ↓
Thread Event Loop stops
      ↓
thread.finished
      ↓
cleanup
```

---

# 30. Worker `deleteLater()`

Qt có:

```python
worker.deleteLater()
```

Đây không phải:

```text
delete ngay lập tức
```

Nó yêu cầu Qt xử lý deletion an toàn thông qua event mechanism phù hợp.

Đây là lý do event loop/thread affinity rất quan trọng.

---

# 31. Một lỗi lifecycle phổ biến

Bạn tạo:

```python
thread = QThread()
worker = Worker()
```

rồi không giữ reference:

```python
def start(self):
    thread = QThread()
    worker = Worker()
```

Sau khi function kết thúc:

```text
Python references
     ↓
có thể biến mất
```

Trong GUI application, nên quản lý lifecycle rõ ràng, thường giữ reference ở object sở hữu task.

Ví dụ:

```python
self.thread
self.worker
```

---

# 32. Không cho Worker có parent GUI

Không:

```python
worker = Worker(self)
```

nếu `self` là MainWindow và bạn định:

```python
worker.moveToThread(thread)
```

Vì:

```text
MainWindow
    │
    └── Worker
```

khiến Worker có parent ở GUI thread.

Hãy tạo:

```python
worker = Worker()
```

rồi:

```python
worker.moveToThread(thread)
```

---

# 33. Thread affinity

Bạn có thể kiểm tra:

```python
print(worker.thread())
```

Trước:

```text
GUI Thread
```

Sau:

```python
worker.moveToThread(thread)
```

worker có affinity tới:

```text
Worker Thread
```

Đây là lý do `moveToThread()` quan trọng.

---

# 34. `QObject` và Thread Affinity

Mental model:

```text
QObject
    │
    └── thread affinity
```

Signal/slot queued connection có thể sử dụng affinity này để dispatch execution đến thread thích hợp.

Do đó:

```text
QObject
+
QThread
+
Event Loop
+
Signal/Slot
```

là một hệ thống liên kết với nhau.

---

# 35. Một hiểu lầm rất phổ biến

Có người viết:

```python
worker.moveToThread(thread)
worker.run()
```

và nghĩ:

> Worker đã ở thread mới nên `run()` chạy trong thread mới.

Không.

Nếu bạn gọi trực tiếp:

```python
worker.run()
```

thì Python code được thực thi bởi **thread đang gọi nó**.

Ví dụ:

```text
GUI Thread
    │
    └── worker.run()
```

thì:

```text
run()
↓
GUI Thread
```

`moveToThread()` không biến direct method call thành thread switch.

---

# 36. Đây là điểm cần nhớ tuyệt đối

```python
worker.moveToThread(thread)
```

không đồng nghĩa:

```python
worker.run()
```

tự động chạy ở thread đó.

Đúng:

```python
thread.started.connect(worker.run)
thread.start()
```

Qt dispatch:

```text
thread
 ↓
started
 ↓
Worker Thread
 ↓
worker.run()
```

---

# 37. Worker có Event Loop riêng

Sau:

```python
thread.start()
```

Qt thread thường có event loop.

Mental model:

```text
GUI Thread
    │
    └── GUI Event Loop


Worker Thread
    │
    └── Worker Event Loop
```

Điều này cho phép Qt dispatch queued signals/slots tới worker thread.

---

# 38. Worker có thể nhận command

Ví dụ:

```python
class Worker(QObject):

    @Slot()
    def pause(self):
        ...

    @Slot()
    def cancel(self):
        ...
```

GUI:

```text
Pause Button
     ↓
worker.pause()
```

Nhưng để việc này thực sự được dispatch sang Worker Thread đúng cách, chúng ta cần hiểu signal/slot connection và event loop.

Đây sẽ là nội dung quan trọng của **Buổi 40 — Signal giữa Worker và GUI**.

---

# 39. Một Worker thực tế hơn

```python
class CrawlWorker(QObject):

    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler

    @Slot()
    def run(self):
        try:
            result = self.crawler.crawl(
                progress_callback=self.progress.emit
            )

            self.result.emit(result)

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self.finished.emit()
```

Architecture:

```text
Worker
   ↓
Crawler
   ↓
Repository
```

Worker không chứa:

```text
SQLite code
HTTP implementation
HTML parser
Domain rules
```

---

# 40. Progress Callback

Đây là một pattern rất hữu ích.

Crawler:

```python
def crawl(self, progress_callback=None):

    for index, url in enumerate(urls):

        crawl_one(url)

        if progress_callback:
            progress_callback(index)
```

Worker:

```python
result = self.crawler.crawl(
    progress_callback=self.progress.emit
)
```

Ta đang bridge:

```text
Application logic
        ↓
callback
        ↓
Qt Signal
        ↓
GUI
```

---

# 41. Nhưng có một caveat

Nếu `crawler.crawl()` gọi:

```python
progress_callback(...)
```

thì callback thực tế là:

```python
self.progress.emit(...)
```

được gọi từ Worker Thread.

Điều này thường phù hợp vì Signal có thể được dispatch đến receiver ở GUI thread.

Nhưng:

> Không được biến callback thành việc trực tiếp sửa GUI.

Đúng:

```python
progress_callback(50)
```

Sai:

```python
progress_callback(
    lambda: progress_bar.setValue(50)
)
```

nếu callback được thực hiện trực tiếp trong worker thread.

---

# 42. Worker Pattern và SOLID

Pattern này hỗ trợ rất tốt:

### SRP

```text
QThread
    → thread lifecycle

Worker
    → task orchestration

Service
    → business/application logic

Repository
    → persistence
```

Mỗi class có trách nhiệm riêng.

---

### DIP

Worker nhận:

```python
def __init__(self, crawler):
```

thay vì tự:

```python
crawler = Crawler()
```

Có thể inject:

```python
MockCrawler
RealCrawler
```

rất thuận lợi cho testing.

---

# 43. Worker Pattern và Testing

Bạn có thể test Service độc lập:

```python
service = CrawlService(...)
result = service.execute()
```

Không cần:

```text
QApplication
QThread
MainWindow
```

Đây là lợi ích cực lớn.

Worker chỉ cần test riêng:

```text
Signal emitted?
Error handled?
Finished emitted?
```

---

# 44. So sánh hai architecture

### Cách A

```text
QThread subclass
     │
     ├── HTTP
     ├── SQLite
     ├── business logic
     ├── progress
     └── GUI reference
```

Một class làm quá nhiều.

### Cách B

```text
QThread
   │
   └── Worker
          │
          └── Service
                 │
                 └── Repository
```

Rõ ràng hơn.

---

# 45. Khi nào subclass `QThread` vẫn hợp lý?

Không phải:

```text
subclass QThread = always wrong
```

Ví dụ task cực đơn giản:

```python
class CalculationThread(QThread):

    result = Signal(int)

    def run(self):
        self.result.emit(calculate())
```

hoàn toàn có thể hợp lý.

Nhưng khi application bắt đầu có:

```text
Signals
Lifecycle
Cancel
Progress
Services
Repositories
Multiple tasks
```

Worker Object Pattern thường dễ maintain hơn.

---

# 46. Worker Object Pattern chuẩn

Hãy ghi nhớ template:

```text
             GUI THREAD
                 │
                 │
          ┌──────▼──────┐
          │   QThread   │
          └──────┬──────┘
                 │
                 │ affinity
                 ▼
          WORKER THREAD
          ┌──────────────┐
          │ Worker       │
          │  QObject     │
          │              │
          │ run()        │
          │ progress     │
          │ result       │
          │ error        │
          │ finished     │
          └──────┬───────┘
                 │
                 ▼
              Service
                 │
                 ▼
             Repository
```

---

# 47. Template code

Bạn có thể lưu mental template này:

```python
class Worker(QObject):

    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, service):
        super().__init__()
        self.service = service

    @Slot()
    def run(self):
        try:
            result = self.service.execute()

            self.result.emit(result)

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self.finished.emit()
```

Setup:

```python
thread = QThread()
worker = Worker(service)

worker.moveToThread(thread)

thread.started.connect(
    worker.run
)

worker.finished.connect(
    thread.quit
)

thread.start()
```

Đây là **skeleton**. Production code sẽ cần lifecycle/cancellation/shutdown kỹ hơn.

---

# 48. Bài tập 1 — Basic Worker

Tạo:

```text
Worker
QThread
Button
Label
```

Worker:

```text
sleep 3 giây
```

GUI:

```text
Start
```

Yêu cầu:

```text
GUI không freeze
```

---

# 49. Bài tập 2 — Progress

Worker:

```python
for i in range(101):
    ...
    progress.emit(i)
```

GUI:

```python
progress.connect(
    progress_bar.setValue
)
```

Yêu cầu:

```text
0 → 100
```

---

# 50. Bài tập 3 — Result

Worker:

```python
result = 12345
result.emit(result)
```

GUI:

```text
Label = 12345
```

Không cho Worker truy cập Label.

---

# 51. Bài tập 4 — Error

Worker:

```python
raise ValueError("Something went wrong")
```

GUI nhận:

```text
error
 ↓
QMessageBox
```

---

# 52. Bài tập 5 — Thread identity

In:

```python
threading.current_thread()
```

ở:

```text
GUI slot
Worker.run()
GUI result slot
```

Bạn phải thấy:

```text
GUI slot
    → MainThread

Worker.run()
    → Worker Thread

result slot
    → MainThread
```

---

# 53. Bài tập 6 — Story Reader

Thiết kế:

```text
MainWindow
    │
    └── CrawlWorker
            │
            └── CrawlService
                    │
                    ├── HTTP Client
                    ├── Parser
                    └── Repository
```

Signals:

```text
progress
chapter_found
error
finished
```

Không cho:

```text
Crawler
    ↓
MainWindow
```

---

# 54. Bài tập 7 — Tách Service

Viết:

```python
class DownloadService:

    def download(self):
        ...
```

Worker:

```python
class DownloadWorker(QObject):

    def __init__(self, service):
        ...
```

Mục tiêu:

```text
DownloadService
```

có thể test mà không cần PySide6.

---

# 55. Checklist

Sau Buổi 39, bạn phải trả lời được:

### `QThread` là gì?

```text
Thread management
```

### Worker là gì?

```text
QObject chứa background task/orchestration
```

### `moveToThread()` làm gì?

```text
Thay đổi thread affinity của QObject
```

### `moveToThread()` có chạy Worker không?

```text
Không.
```

### `run()` gọi trực tiếp có chạy background không?

```text
Không.
```

### Cách bắt đầu Worker?

```python
thread.started.connect(worker.run)
thread.start()
```

### Worker update GUI trực tiếp?

```text
Không.
```

### Worker → GUI?

```text
Signal
```

### Business logic nên nằm đâu?

```text
Service / Domain
```

---

# 56. Mental Model cuối buổi

Đây là hình quan trọng nhất:

```text
                    GUI THREAD
                ┌─────────────────┐
                │ QApplication    │
                │ Event Loop       │
                │                 │
                │ MainWindow      │
                └────────┬────────┘
                         │
                         │ start()
                         ▼
                  ┌─────────────┐
                  │   QThread   │
                  │  lifecycle  │
                  └──────┬──────┘
                         │
                         ▼
                    WORKER THREAD
                  ┌──────────────┐
                  │ Worker       │
                  │ QObject      │
                  │              │
                  │ run()        │
                  └──────┬───────┘
                         │
                         ▼
                       Service
                         │
                         ▼
                     Repository

Worker ───── Signals ─────► GUI
```

### Công thức cần thuộc

```python
thread = QThread()
worker = Worker(service)

worker.moveToThread(thread)

thread.started.connect(worker.run)

worker.finished.connect(thread.quit)

thread.start()
```

Nhưng **đừng chỉ học thuộc 5 dòng này**. Hãy hiểu 4 khái niệm đứng phía sau:

```text
QObject
   ↓
Thread Affinity
   ↓
QThread Event Loop
   ↓
Signal / Slot
```

Buổi tiếp theo **Buổi 40 — Signal giữa Worker và GUI** sẽ đào sâu đúng phần còn thiếu: **Direct Connection vs Queued Connection, Auto Connection, signal truyền dữ liệu qua thread, thread affinity của sender/receiver, và cách thiết kế `progress/result/error/finished` một cách an toàn.**
