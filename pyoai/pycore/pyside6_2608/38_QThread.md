# Buổi 38 — `QThread` Deep Dive

Sau Buổi 36–37, ta đã biết:

```text
GUI Thread
    ↓
Event Loop
    ↓
không được block
```

Bây giờ chúng ta bắt đầu công cụ quan trọng nhất của Qt để chạy công việc nền:

```python
QThread
```

> **Mục tiêu của buổi này không phải chỉ biết viết `QThread`, mà phải hiểu `QThread` thực sự đại diện cho cái gì và tránh cách dùng sai phổ biến.**

---

# 1. `QThread` là gì?

`QThread` là abstraction của Qt để quản lý một thread.

Mental model đơn giản:

```text
GUI Thread
    │
    │ start
    ▼
QThread
    │
    ▼
Background execution
```

Nhưng có một điểm rất quan trọng:

> **`QThread` object không đơn giản đồng nghĩa với "code bên trong object này chạy ở thread đó".**

Đây là phần dễ gây nhầm nhất.

---

# 2. Ví dụ tối thiểu

```python
from PySide6.QtCore import QThread


thread = QThread()

thread.start()
```

Ta đã yêu cầu Qt tạo/chạy thread.

Nhưng thread chưa làm công việc gì hữu ích.

---

# 3. `start()` làm gì?

Khi:

```python
thread.start()
```

Qt sẽ khởi động thread.

Mental model:

```text
GUI Thread
    │
    │ thread.start()
    ▼
OS Thread
    │
    ▼
QThread execution
```

Thông thường ta **không gọi `run()` trực tiếp**.

---

# 4. `start()` khác `run()`

Đây là distinction rất quan trọng.

```python
thread.start()
```

nghĩa là:

> Yêu cầu Qt khởi động thread.

Trong khi:

```python
thread.run()
```

chỉ là gọi method `run()` trực tiếp.

Nếu bạn làm:

```python
thread.run()
```

từ GUI thread:

```text
GUI Thread
    ↓
thread.run()
    ↓
task
    ↓
GUI FREEZE
```

Không tạo background execution như bạn mong muốn.

---

# 5. Mental model

Đúng:

```text
GUI Thread
    │
    │ start()
    ▼
Worker Thread
    │
    ▼
run()
```

Sai:

```text
GUI Thread
    │
    │ run()
    ▼
run()
    │
    ▼
GUI FREEZE
```

---

# 6. `QThread.run()`

`QThread` có:

```python
def run(self):
    ...
```

Theo mặc định, Qt xử lý execution của thread thông qua `run()`.

Một ví dụ:

```python
from PySide6.QtCore import QThread


class MyThread(QThread):

    def run(self):
        print("Hello from worker thread")
```

Sau đó:

```python
thread = MyThread()
thread.start()
```

Khi `start()`:

```text
OS Thread
   ↓
MyThread.run()
```

---

# 7. Demo hoàn chỉnh

```python
import threading

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MyThread(QThread):

    def run(self):
        print(
            "Python:",
            threading.current_thread().name
        )


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.button = QPushButton("Start")

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)

        self.thread = MyThread()

        self.button.clicked.connect(
            self.start_thread
        )

    def start_thread(self):
        self.thread.start()


app = QApplication([])

window = Window()
window.show()

app.exec()
```

Khi click:

```text
MainThread
```

và thread worker sẽ có thread riêng.

---

# 8. Nhưng subclass `QThread` có vấn đề gì?

Cách:

```python
class WorkerThread(QThread):
    def run(self):
        ...
```

**không phải lúc nào cũng sai**.

Nó phù hợp với những task đơn giản:

```text
start
  ↓
run()
  ↓
do task
  ↓
finish
```

Ví dụ:

```python
class CalculationThread(QThread):

    def run(self):
        result = calculate()
        print(result)
```

Nhưng với application lớn, cách này thường không phải architecture tốt nhất.

---

# 9. Vì sao?

Vì ta dễ nhầm:

```text
QThread object
```

với:

```text
thread execution context
```

Qt có khái niệm rất quan trọng:

```text
Thread Affinity
```

---

# 10. Thread Affinity

Một `QObject` có thread affinity.

Bạn có thể kiểm tra:

```python
obj.thread()
```

Ví dụ:

```python
from PySide6.QtCore import QObject


obj = QObject()

print(obj.thread())
```

Object thuộc một Qt thread context.

---

# 11. Đây là điều rất quan trọng

Giả sử:

```python
class Worker(QObject):
    ...
```

và:

```python
worker = Worker()
```

sau đó:

```python
worker.moveToThread(thread)
```

Ta đã yêu cầu:

```text
Worker
   │
   ▼
Thread affinity
   │
   ▼
Worker Thread
```

Đây chính là nền tảng của **Worker Object Pattern**, sẽ học kỹ ở Buổi 39.

---

# 12. `moveToThread()`

API:

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

---

# 13. Tại sao Worker Object tốt hơn?

Thay vì:

```python
class CrawlThread(QThread):
    def run(self):
        crawler.crawl()
```

ta có:

```text
QThread
    +
Worker QObject
```

```python
class CrawlWorker(QObject):

    def run(self):
        crawler.crawl()
```

và:

```python
thread = QThread()
worker = CrawlWorker()

worker.moveToThread(thread)
```

---

# 14. Đây là architecture Qt khuyến nghị

Mental model:

```text
GUI Thread
    │
    ├── MainWindow
    │
    └── QThread object
              │
              ▼
       Worker Thread
              │
              └── Worker QObject
```

Worker thực hiện business/background task.

`QThread` quản lý thread.

Hai trách nhiệm khác nhau.

---

# 15. `QThread` không phải Worker

Đây là câu bạn nên nhớ:

> **`QThread` quản lý thread; Worker thực hiện công việc.**

Ví dụ:

```text
QThread
   │
   └── quản lý execution thread

Worker
   │
   └── thực hiện crawl()
```

Không nên gom tất cả trách nhiệm vào `QThread`.

---

# 16. `QThread` có Event Loop

Đây là một điểm rất hay.

Khi thread chạy, Qt có thể chạy:

```text
QThread
   ↓
Event Loop
```

Thông thường:

```python
thread.start()
```

dẫn tới `run()`, và implementation mặc định của `run()` gọi event loop.

Mental model:

```text
Worker Thread
    │
    ▼
QThread.run()
    │
    ▼
exec()
    │
    ▼
Event Loop
```

---

# 17. Tại sao Worker Object cần Event Loop?

Giả sử:

```python
worker = Worker()
worker.moveToThread(thread)
```

Sau đó:

```python
thread.started.connect(worker.run)
```

Khi:

```python
thread.start()
```

Qt phát:

```text
started
   ↓
worker.run()
```

Signal/slot và queued connection dựa rất nhiều vào event system của thread đích.

---

# 18. Ví dụ Worker Object cơ bản

```python
from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
)


class Worker(QObject):

    finished = Signal()

    def run(self):
        print("Working...")
        self.finished.emit()
```

Main:

```python
thread = QThread()
worker = Worker()

worker.moveToThread(thread)

thread.started.connect(worker.run)

worker.finished.connect(thread.quit)

thread.start()
```

Flow:

```text
thread.start()
      ↓
Worker Thread
      ↓
thread.started
      ↓
worker.run()
      ↓
finished.emit()
      ↓
thread.quit()
```

---

# 19. Nhưng code trên vẫn chưa hoàn chỉnh

Một ứng dụng production cần quan tâm:

```text
worker lifetime
thread lifetime
cleanup
exceptions
cancel
progress
result
```

Đó là lý do chúng ta không nên copy một snippet `QThread` từ internet rồi coi là xong.

---

# 20. Signal từ Worker về GUI

Worker:

```python
class Worker(QObject):

    finished = Signal()
    result = Signal(str)

    def run(self):
        result = "Hello"
        self.result.emit(result)
        self.finished.emit()
```

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
     │ result.emit()
     ▼
Qt Signal
     │
     ▼
GUI Thread
     │
     ▼
handle_result()
```

---

# 21. Tại sao GUI slot có thể chạy trên GUI Thread?

Đây là sức mạnh của Qt's signal/slot threading model.

Nếu sender và receiver thuộc thread khác nhau, Qt có thể sử dụng:

```text
Queued Connection
```

Mental model:

```text
Worker Thread
    │
    │ emit()
    ▼
Event Queue của GUI Thread
    │
    ▼
GUI Event Loop
    │
    ▼
GUI Slot
```

Vì vậy GUI được cập nhật ở đúng thread.

---

# 22. Không cần tự quản lý lock cho mọi Signal

Ví dụ:

```python
worker.progress.emit(50)
```

GUI:

```python
worker.progress.connect(
    progress_bar.setValue
)
```

Qt xử lý việc dispatch signal/slot theo connection type và thread affinity.

Đây là một trong những lý do Signal/Slot rất phù hợp với GUI concurrency.

---

# 23. `thread.started`

Một pattern phổ biến:

```python
thread.started.connect(worker.run)
```

Flow:

```text
GUI
 │
 │ start()
 ▼
QThread
 │
 ▼
started
 │
 ▼
Worker.run()
```

Đây là pattern chúng ta sẽ hoàn thiện ở Buổi 39.

---

# 24. Cleanup

Khi worker xong:

```python
worker.finished.connect(thread.quit)
```

Flow:

```text
Worker
   │
   │ finished
   ▼
thread.quit()
   │
   ▼
Thread event loop stops
   │
   ▼
Thread finishes
```

Có thể tiếp tục kết nối:

```python
thread.finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)
```

Tuy nhiên cleanup lifecycle cần được thiết kế cẩn thận; không nên máy móc copy các dòng này vào mọi trường hợp.

---

# 25. `quit()` là gì?

```python
thread.quit()
```

không có nghĩa:

> "kill thread ngay lập tức."

Nó yêu cầu event loop của thread kết thúc.

Mental model:

```text
Worker
   ↓
finished
   ↓
thread.quit()
   ↓
event loop stops
```

---

# 26. `terminate()` là gì?

Qt có:

```python
thread.terminate()
```

Nhưng đây là công cụ nguy hiểm.

Nó có thể dừng thread một cách cưỡng bức.

Có thể gây:

```text
resource chưa cleanup
lock chưa release
state không nhất quán
database transaction dang dở
```

Do đó:

> **Không dùng `terminate()` như cơ chế Cancel thông thường.**

Buổi 42 chúng ta sẽ thiết kế cancellation đúng cách.

---

# 27. `wait()`

Có:

```python
thread.wait()
```

Nó chờ thread kết thúc.

Nhưng nếu gọi trong GUI thread:

```python
thread.wait()
```

bạn có thể tự block GUI.

Ví dụ:

```text
GUI Thread
   ↓
thread.wait()
   ↓
WAIT
   ↓
GUI FREEZE
```

Vì vậy phải rất cẩn thận.

---

# 28. Một anti-pattern phổ biến

```python
def closeEvent(self, event):
    self.thread.quit()
    self.thread.wait()
```

Nó có thể hợp lý trong một số lifecycle cụ thể, nhưng nếu worker không thể kết thúc vì đang chờ GUI/event loop thì bạn có thể tạo tình huống chờ đợi khó xử.

Production code phải thiết kế shutdown protocol rõ ràng.

---

# 29. `QThread.sleep()`

Qt có:

```python
QThread.sleep(5)
```

Nhưng:

> Nếu bạn gọi nó trong GUI thread, GUI vẫn freeze.

Ví dụ:

```python
def on_click(self):
    QThread.sleep(5)
```

vẫn là:

```text
GUI Thread
    ↓
sleep
    ↓
FREEZE
```

Điều quan trọng không phải API nào bạn dùng.

Điều quan trọng là:

> **Task đang chạy ở thread nào?**

---

# 30. `QThread.msleep()`

Tương tự:

```python
QThread.msleep(100)
```

Nếu chạy trên GUI thread:

```text
GUI freeze
```

Nếu chạy trong worker thread:

```text
GUI vẫn responsive
```

---

# 31. Ví dụ Thread Identity

Worker:

```python
import threading

from PySide6.QtCore import (
    QObject,
    Signal,
)


class Worker(QObject):

    finished = Signal(str)

    def run(self):
        name = threading.current_thread().name
        self.finished.emit(name)
```

GUI:

```python
worker.finished.connect(
    self.show_thread
)
```

Bạn có thể quan sát:

```text
Worker:
    Thread-1

GUI:
    MainThread
```

---

# 32. Đây là thí nghiệm rất nên làm

Tạo:

```text
MainWindow
    │
    ├── Button Start
    └── Label
```

Worker:

```text
Worker.run()
    ↓
print(thread name)
```

GUI slot:

```text
handle_result()
    ↓
print(thread name)
```

Bạn sẽ thấy:

```text
Worker.run()
    → Worker Thread

handle_result()
    → GUI Thread
```

Đây là cách tốt nhất để hiểu Signal/Slot cross-thread.

---

# 33. Một vấn đề quan trọng: QObject không tự thread-safe

Ví dụ:

```python
class Worker(QObject):
    ...
```

không có nghĩa:

```text
Worker
```

tự nhiên thread-safe.

Nếu nhiều thread cùng truy cập:

```python
self.data
```

thì vẫn phải thiết kế concurrency đúng.

---

# 34. `moveToThread()` có điều kiện

Không nên:

```python
worker.setParent(main_window)
worker.moveToThread(thread)
```

vì QObject có parent phải có cùng thread affinity với parent.

Qt object tree và thread affinity có quan hệ rất chặt.

Mental model:

```text
Parent
  │
  └── Child
```

thường phải cùng thread affinity.

Đây là sự kết hợp kiến thức từ:

```text
Buổi 2 — QObject Object Model
```

và:

```text
Buổi 38 — QThread
```

---

# 35. Đây là lý do Parent/Child rất quan trọng

Ví dụ:

```python
worker = Worker(main_window)
```

thì:

```text
worker
   ↓
parent = main_window
```

và `worker` có affinity của GUI thread.

Bạn không thể đơn giản:

```python
worker.moveToThread(worker_thread)
```

với một QObject đã có parent ở thread khác.

---

# 36. Worker nên thường được tạo độc lập

Pattern:

```python
worker = Worker()
worker.moveToThread(thread)
```

thường phù hợp hơn.

Không:

```python
worker = Worker(main_window)
```

nếu mục tiêu là chuyển worker sang background thread.

---

# 37. Lifecycle chuẩn

Một worker task thường có flow:

```text
CREATE
   ↓
MOVE TO THREAD
   ↓
START THREAD
   ↓
RUN
   ↓
PROGRESS
   ↓
RESULT / ERROR
   ↓
FINISHED
   ↓
QUIT THREAD
   ↓
CLEANUP
```

Đây là lifecycle bạn nên nhớ.

---

# 38. Ví dụ kiến trúc

```text
MainWindow
    │
    ├── QThread
    │
    └── Worker
           │
           ├── run()
           ├── progress
           ├── result
           ├── error
           └── finished
```

Connections:

```text
thread.started
       ↓
worker.run()

worker.progress
       ↓
GUI

worker.result
       ↓
GUI

worker.error
       ↓
GUI

worker.finished
       ↓
thread.quit()
```

---

# 39. Ví dụ hoàn chỉnh hơn

```python
import time

from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Worker(QObject):

    progress = Signal(int)
    finished = Signal()

    def run(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress.emit(i)

        self.finished.emit()


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.button = QPushButton("Start")
        self.label = QLabel("0%")

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.progress.connect(
            self.update_progress
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.button.clicked.connect(
            self.start
        )

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def update_progress(self, value):
        self.label.setText(
            f"{value}%"
        )


app = QApplication([])

window = Window()
window.show()

app.exec()
```

---

# 40. Flow của code

Khi click:

```text
Button
  ↓
start()
  ↓
thread.start()
  ↓
Worker Thread
  ↓
thread.started
  ↓
worker.run()
```

Worker:

```text
run()
  ↓
0 → 1 → 2 → ... → 100
```

mỗi lần:

```python
self.progress.emit(i)
```

GUI nhận:

```python
update_progress(i)
```

và:

```text
GUI Thread
    ↓
QLabel
```

---

# 41. Một vấn đề trong ví dụ

Code trên dùng một `QThread` cho một task.

Sau khi:

```python
worker.finished.emit()
```

thì:

```python
thread.quit()
```

Thread kết thúc.

Nếu muốn chạy task lần nữa, lifecycle cần được thiết kế cẩn thận.

Đặc biệt khi worker có state hoặc task có thể restart/cancel.

Chúng ta sẽ cải thiện architecture ở các buổi sau.

---

# 42. Không nên tạo Thread mỗi click một cách vô tội vạ

Ví dụ:

```python
def start(self):
    thread = QThread()
    worker = Worker()

    worker.moveToThread(thread)
    thread.start()
```

Nếu user click:

```text
Start
Start
Start
Start
```

có thể tạo:

```text
Thread 1
Thread 2
Thread 3
Thread 4
```

Điều này dễ dẫn tới:

```text
resource explosion
race conditions
lifecycle bugs
```

Về sau `QThreadPool` sẽ giải quyết bài toán task ngắn/nhiều hơn hiệu quả hơn.

---

# 43. `QThread` phù hợp với loại task nào?

Rất phù hợp với:

```text
Long-running background task
```

Ví dụ:

```text
Crawler
Download
Long DB operation
File processing
Background service
```

Đặc biệt khi task có lifecycle:

```text
Start
Progress
Cancel
Finished
Error
```

---

# 44. `QThread` chưa phải lựa chọn duy nhất

Qt còn:

```text
QThread
QThreadPool
QRunnable
```

Python còn:

```text
threading
ThreadPoolExecutor
ProcessPoolExecutor
asyncio
```

Chúng ta sẽ không dùng một công cụ cho tất cả.

Mental model:

```text
Long-lived worker
       ↓
QThread

Many short tasks
       ↓
QThreadPool / QRunnable

CPU-heavy
       ↓
ProcessPoolExecutor / multiprocessing

Async I/O
       ↓
asyncio
```

Đây là roadmap của phần IV.

---

# 45. `QThread` vs `ThreadPoolExecutor`

Bạn đã học `ThreadPoolExecutor`, nên hãy so sánh:

| `QThread`               | `ThreadPoolExecutor`    |
| ----------------------- | ----------------------- |
| Qt-native               | Python-native           |
| Signal/Slot integration | Future                  |
| QObject affinity        | Python callable         |
| Event loop              | Worker function         |
| GUI integration tốt     | Cần bridge              |
| Long-lived worker       | Short independent tasks |

Không phải cái nào "tốt hơn".

Chọn theo architecture.

---

# 46. `QThread` vs `asyncio`

Ví dụ HTTP:

### QThread

```text
GUI
 ↓
QThread
 ↓
blocking HTTP
```

### asyncio

```text
GUI
 ↓
async event loop
 ↓
await HTTP
```

Hai architecture khác nhau.

Buổi 46 chúng ta sẽ đi sâu:

```text
PySide6 + asyncio
```

---

# 47. Bài tập 1 — Thread Identity

Tạo:

```text
Button Start
Label
```

Khi click:

```text
GUI thread name
Worker thread name
```

Hiển thị trên Label.

Mục tiêu:

```text
GUI ≠ Worker
```

---

# 48. Bài tập 2 — Progress

Worker chạy:

```python
for i in range(101):
    ...
```

emit:

```python
progress.emit(i)
```

GUI cập nhật:

```python
progress_bar.setValue(i)
```

Yêu cầu:

```text
GUI không freeze
Progress chạy 0 → 100
```

---

# 49. Bài tập 3 — Result

Worker:

```python
result = calculate()
```

Signal:

```python
result = Signal(int)
```

GUI:

```python
result.connect(self.show_result)
```

Flow:

```text
Worker
 ↓
result.emit(42)
 ↓
GUI
 ↓
Label = 42
```

---

# 50. Bài tập 4 — Error

Thiết kế:

```python
error = Signal(str)
```

Worker:

```python
try:
    ...
except Exception as exc:
    self.error.emit(str(exc))
```

GUI:

```text
error
 ↓
QMessageBox
```

Đây sẽ là nền tảng cho architecture production.

---

# 51. Bài tập 5 — Thread lifecycle

Theo dõi:

```python
thread.started
thread.isRunning()
thread.finished
```

Vẽ lifecycle:

```text
Created
   ↓
Not Running
   ↓
start()
   ↓
Running
   ↓
quit()
   ↓
Finished
```

---

# 52. Bài tập 6 — Phân tích code sai

Code:

```python
class Worker(QThread):

    def run(self):
        self.window.label.setText("Done")
```

Hãy trả lời:

1. Worker có nên kế thừa `QThread` không?
2. Có vấn đề gì khi Worker giữ reference tới `window`?
3. Worker có nên update `QLabel`?
4. Architecture đúng nên là gì?

Đáp án hướng tới:

```text
QThread
   +
Worker QObject
   +
Signal
```

chứ không:

```text
Worker
   ↓
Widget
```

---

# 53. Bài tập 7 — Story Reader

Thiết kế:

```text
[Crawl Story]
```

Flow:

```text
MainWindow
     ↓
QThread
     ↓
CrawlerWorker
     ↓
Crawler
     ↓
Repository
```

Signals:

```text
progress
chapter_found
error
finished
```

Chưa cần code hoàn chỉnh.

Chỉ cần thiết kế architecture.

---

# 54. Những điều KHÔNG nên làm

### ❌ Gọi `run()` để tạo background task

```python
thread.run()
```

### ❌ Worker trực tiếp sửa Widget

```python
label.setText(...)
```

### ❌ `QThread.sleep()` trong GUI thread

```python
QThread.sleep(5)
```

### ❌ `wait()` bừa bãi trong GUI thread

```python
thread.wait()
```

### ❌ Dùng `terminate()` như Cancel bình thường

```python
thread.terminate()
```

### ❌ Tạo vô hạn QThread

```text
mỗi click → một thread mới
```

---

# 55. 5 câu cần nhớ

### Câu 1

> `start()` khởi động thread; gọi `run()` trực tiếp không tạo concurrency.

### Câu 2

> `QThread` quản lý thread, còn Worker nên chịu trách nhiệm thực hiện công việc.

### Câu 3

> `QObject` có thread affinity.

### Câu 4

> Worker có thể dùng Signal để giao tiếp với GUI.

### Câu 5

> GUI chỉ nên cập nhật Widget từ GUI thread.

---

# 56. Mental Model quan trọng nhất

Đừng học thuộc code:

```python
thread = QThread()
worker = Worker()

worker.moveToThread(thread)

thread.started.connect(worker.run)
```

Hãy hiểu:

```text
                   GUI THREAD
                ┌──────────────┐
                │ MainWindow   │
                │ Event Loop   │
                └──────┬───────┘
                       │
                       │ start()
                       ▼
                ┌──────────────┐
                │   QThread    │
                └──────┬───────┘
                       │
                       ▼
                WORKER THREAD
                ┌──────────────┐
                │ Worker       │
                │              │
                │ run()        │
                │ HTTP         │
                │ Crawl        │
                │ Database     │
                └──────┬───────┘
                       │
                    Signal
                       │
                       ▼
                ┌──────────────┐
                │ GUI Thread   │
                │              │
                │ update UI    │
                └──────────────┘
```

---

## Sau Buổi 38

Ta đã có:

```text
36 — GUI Thread
       ↓
37 — GUI Freeze
       ↓
38 — QThread
```

Bước tiếp theo rất quan trọng:

```text
39 — Worker Object Pattern
```

Ở Buổi 39, chúng ta sẽ **bỏ cách nhồi business logic vào subclass `QThread`**, xây một `Worker(QObject)` đúng chuẩn, tìm hiểu sâu `moveToThread()`, `thread.started`, `thread.quit`, lifecycle/cleanup và xây một **Reusable Worker Pattern** có thể áp dụng trực tiếp cho crawler, downloader và SQLite service.
