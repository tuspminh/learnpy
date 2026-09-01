# Phần IV — Threading & Concurrency

# Buổi 36 — GUI Thread

Đây là buổi đầu tiên của phần **Threading & Concurrency**.

Sau phần UI Architecture, chúng ta đã biết cách tách:

```text
View
 ↓
ViewModel
 ↓
Service
 ↓
Repository
 ↓
Infrastructure
```

Nhưng có một vấn đề mới:

> **Nếu Service thực hiện một công việc mất 10 giây thì GUI sẽ làm gì trong 10 giây đó?**

Đây chính là lý do phải hiểu **GUI Thread** trước khi học `QThread`.

---

# 1. Mental Model

Một ứng dụng PySide6 có một thread đặc biệt:

```text
                    Application
                         │
                         ▼
                 ┌───────────────┐
                 │   GUI Thread  │
                 │               │
                 │ QApplication  │
                 │ MainWindow    │
                 │ Widgets       │
                 └───────┬───────┘
                         │
                         ▼
                    Event Loop
```

GUI của Qt về cơ bản được điều khiển bởi **event loop** chạy trên thread chính.

---

# 2. `QApplication`

Một ứng dụng thường bắt đầu:

```python
from PySide6.QtWidgets import QApplication


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
```

Điểm quan trọng nhất là:

```python
app.exec()
```

Nó bắt đầu:

```text
Qt Event Loop
```

---

# 3. Event Loop là gì?

Có thể hình dung đơn giản:

```text
while application_running:

    event = get_next_event()

    process(event)
```

Ví dụ người dùng:

```text
Click button
      ↓
Mouse Event
      ↓
Event Loop
      ↓
Button
      ↓
Signal
      ↓
Slot
```

Hoặc:

```text
Keyboard
   ↓
Key Event
   ↓
Event Loop
   ↓
Widget
```

---

# 4. GUI Thread

Thông thường:

```text
Main Thread
    │
    └── GUI Thread
```

GUI Thread chịu trách nhiệm:

```text
QApplication
QWidget
QMainWindow
QPushButton
QLineEdit
QListView
QTableView
...
```

Nói đơn giản:

> **Các thao tác GUI phải được thực hiện đúng GUI thread.**

---

# 5. Kiểm tra thread hiện tại

Python:

```python
import threading

print(threading.current_thread())
```

Trong GUI:

```python
from PySide6.QtWidgets import QApplication


app = QApplication([])

print(threading.current_thread())

app.exec()
```

Bạn sẽ thấy thread chính.

---

# 6. Qt cũng có khái niệm Thread

Qt cung cấp:

```python
from PySide6.QtCore import QThread
```

Ta có thể kiểm tra:

```python
from PySide6.QtCore import QThread

print(QThread.currentThread())
```

Hai hệ thống cần phân biệt:

```text
Python
    threading.Thread

Qt
    QThread
```

Đừng đồng nhất chúng.

---

# 7. GUI Thread ≠ mọi công việc

Một lỗi phổ biến là nghĩ:

```text
GUI Thread
   │
   ├── GUI
   ├── Database
   ├── HTTP
   ├── Crawl
   ├── File processing
   └── Everything
```

Điều này rất nguy hiểm.

Nên hướng tới:

```text
                 GUI Thread
                     │
              ┌──────┴──────┐
              │             │
             GUI          Events
                           
                     │
                     ▼
                Worker Thread
                     │
              ┌──────┼──────┐
              ▼      ▼      ▼
             HTTP    DB    Crawl
```

---

# 8. Tại sao Qt cần GUI Thread?

GUI framework phải duy trì trạng thái UI nhất quán.

Ví dụ:

```python
button.setText("Hello")
```

Qt phải:

```text
update widget state
        ↓
layout
        ↓
paint
        ↓
screen
```

Nếu nhiều thread cùng sửa widget:

```text
Thread A ──┐
            ├──> QPushButton
Thread B ──┘
```

sẽ rất dễ tạo race condition hoặc hành vi không an toàn.

Vì vậy Qt thiết kế GUI quanh một thread chính.

---

# 9. Event Loop cực kỳ quan trọng

Hãy tưởng tượng:

```text
Event Queue

┌─────────────────────┐
│ Mouse Click         │
├─────────────────────┤
│ Keyboard Event      │
├─────────────────────┤
│ Timer Event         │
├─────────────────────┤
│ Paint Event         │
├─────────────────────┤
│ Signal              │
└─────────────────────┘
          │
          ▼
      Event Loop
```

Event loop lấy từng event và xử lý.

---

# 10. Một event được xử lý tuần tự

Giả sử queue:

```text
A
B
C
D
```

Event loop:

```text
A → xử lý xong
B → xử lý xong
C → xử lý xong
D → xử lý xong
```

Đây là một mental model rất quan trọng.

---

# 11. Vấn đề xuất hiện khi một task quá lâu

Ví dụ:

```python
def on_click():
    do_something_for_10_seconds()
```

Khi click:

```text
Event Loop
    │
    ▼
on_click()
    │
    │ 10 seconds
    │
    ▼
return
```

Trong khoảng 10 giây:

```text
Event Loop
     X
```

không thể xử lý các event tiếp theo.

---

# 12. GUI sẽ "đứng"

Trong lúc đó người dùng:

```text
click
click
click
drag
resize
type
```

Nhưng event loop đang bận:

```text
on_click()
    ↓
10 seconds
```

Các event phải chờ.

Kết quả:

```text
┌────────────────────────────┐
│ My Application             │
│                            │
│       Not Responding       │
│                            │
└────────────────────────────┘
```

---

# 13. Ví dụ freeze đơn giản

```python
import time

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.button = QPushButton(
            "Start",
            self
        )

        self.button.clicked.connect(
            self.start_task
        )

    def start_task(self):
        time.sleep(5)
```

Chạy:

```text
Click Start
     ↓
sleep(5)
     ↓
GUI freeze
```

---

# 14. `time.sleep()` không phải nguyên nhân duy nhất

Đây là điểm rất quan trọng.

GUI freeze không phải vì:

```python
time.sleep()
```

mà vì:

> **GUI thread đang thực hiện một operation blocking/long-running.**

Ví dụ:

```python
requests.get(...)
```

cũng có thể block.

---

# 15. Database cũng có thể block

Ví dụ:

```python
rows = repository.load_one_million_rows()
```

Nếu thực hiện trên GUI thread:

```text
GUI Thread
    │
    ▼
SQLite
    │
    │ 5 seconds
    ▼
return
```

GUI không xử lý event trong khoảng đó.

---

# 16. Crawler cũng vậy

Ví dụ:

```python
def crawl():
    for url in urls:
        download(url)
        parse(url)
        save(url)
```

Nếu gọi trực tiếp:

```python
button.clicked.connect(crawl)
```

thì:

```text
Button
  ↓
crawl()
  ↓
100 URLs
  ↓
GUI freeze
```

Đây chính là vấn đề chúng ta sẽ gặp trong **Story Reader**.

---

# 17. HTTP là ví dụ rất điển hình

Sai:

```python
def download():
    response = requests.get(url)
```

Nếu server mất:

```text
10 seconds
```

thì GUI thread cũng bị block:

```text
GUI Thread
    │
    ▼
requests.get()
    │
    │ waiting...
    │
    │
    ▼
response
```

---

# 18. GUI không "chậm"

Đây là cách hiểu sai phổ biến.

Người dùng nói:

> "PySide6 chạy chậm."

Thực tế có thể là:

```text
PySide6
    ↓
GUI Thread
    ↓
blocking operation
    ↓
Event Loop không được xử lý
```

Không phải Qt đang xử lý UI chậm.

---

# 19. Event Loop cần được "nhường quyền"

Trong GUI programming, nguyên tắc:

> **GUI thread phải quay lại event loop càng sớm càng tốt.**

Ví dụ:

```text
Event
  ↓
Handle quickly
  ↓
Return
  ↓
Event Loop
  ↓
Next event
```

Không nên:

```text
Event
  ↓
10-second task
  ↓
5-second task
  ↓
100MB processing
  ↓
Return
```

---

# 20. GUI Thread nên làm gì?

Phù hợp:

```text
✓ Update widget
✓ Handle click
✓ Handle keyboard
✓ Update progress
✓ Start worker
✓ Receive signal
✓ Render data
```

Không phù hợp:

```text
✗ Crawl 10,000 URLs
✗ Download large files
✗ CPU-heavy processing
✗ Long database operation
✗ Blocking network
✗ Huge file processing
```

---

# 21. Mô hình đúng

Thay vì:

```text
GUI
 │
 └── crawl()
```

nên:

```text
GUI
 │
 └── start worker
          │
          ▼
      Worker Thread
          │
          └── crawl()
```

Sau đó:

```text
Worker
   │
   │ progress
   ▼
GUI Thread
```

---

# 22. Signal rất quan trọng

Ví dụ worker:

```text
Worker
   │
   ├── progress
   ├── finished
   └── error
```

GUI:

```text
progress → ProgressBar
finished → Enable Button
error    → QMessageBox
```

Đây chính là kiến thức **Buổi 34 — Signal-based Architecture** được sử dụng lại.

---

# 23. GUI Thread và Worker Thread

Mental model:

```text
             GUI THREAD
        ┌──────────────────┐
        │ QApplication      │
        │ MainWindow        │
        │ Widgets           │
        │ Event Loop        │
        └────────┬─────────┘
                 │
              Signals
                 │
        ┌────────▼─────────┐
        │ WORKER THREAD    │
        │                  │
        │ HTTP             │
        │ Crawl            │
        │ Database         │
        │ File processing  │
        └──────────────────┘
```

---

# 24. Worker không nên sửa Widget

Sai:

```python
class Worker:

    def run(self):
        self.progress_bar.setValue(50)
```

Worker đang trực tiếp thao tác GUI.

Không nên.

Nên:

```text
Worker
   │
   │ emit(50)
   ▼
GUI
   │
   ▼
progress_bar.setValue(50)
```

---

# 25. Tại sao Signal tốt?

Worker:

```python
progress.emit(50)
```

không cần biết:

```text
ProgressBar
MainWindow
StatusBar
```

Worker chỉ nói:

> "Tôi đang ở 50%."

GUI quyết định:

```python
progress_bar.setValue(50)
```

Đây chính là **separation of concerns**.

---

# 26. GUI Thread là "orchestrator"

Một cách nhìn rất hữu ích:

```text
GUI Thread
    │
    ├── nhận input
    │
    ├── khởi động task
    │
    ├── nhận result
    │
    └── cập nhật UI
```

Worker:

```text
Worker
    │
    ├── thực hiện task
    ├── báo progress
    ├── trả result
    └── báo lỗi
```

---

# 27. Không phải cứ dùng Thread là tốt

Ví dụ:

```python
for i in range(10):
    print(i)
```

Không cần thread.

Thread hữu ích khi có:

```text
Long-running operation
Blocking I/O
Concurrent work
Background task
```

---

# 28. I/O-bound và CPU-bound

Đây là kiến thức bạn đã học ở Thread/Executor, giờ áp dụng vào GUI.

### I/O-bound

Ví dụ:

```text
HTTP
File
Database
Network
```

Thường phù hợp:

```text
QThread
QThreadPool
asyncio
```

tùy kiến trúc.

### CPU-bound

Ví dụ:

```text
Image processing
Compression
Parsing cực nặng
Machine learning
```

Có thể cần:

```text
ProcessPoolExecutor
multiprocessing
```

để tránh giới hạn GIL trong CPython.

---

# 29. Một nguyên tắc thực tế

Đừng hỏi:

> "Task này có dùng thread không?"

Hãy hỏi:

> **"Task này có thể chạy lâu hoặc block GUI thread không?"**

Nếu có:

```text
→ đưa nó ra background
```

---

# 30. Ví dụ với Story Reader

Giả sử:

```text
User click "Crawl"
```

Không nên:

```text
MainWindow
   ↓
Crawler.crawl()
   ↓
500 URLs
```

Mà:

```text
MainWindow
   ↓
Start Crawl Worker
   ↓
GUI Event Loop tiếp tục chạy
```

Worker:

```text
Worker
   │
   ├── URL 1
   ├── URL 2
   ├── URL 3
   ├── ...
   └── URL 500
```

và liên tục:

```text
progress.emit(...)
```

---

# 31. Kết hợp với Architecture của Phần III

Architecture trước:

```text
MainWindow
    ↓
ViewModel
    ↓
Service
    ↓
Repository
```

Bây giờ thêm concurrency:

```text
MainWindow
    ↓
ViewModel
    ↓
Worker
    ↓
Service
    ↓
Repository
```

Nhưng cần cẩn thận:

> Không phải lúc nào Worker cũng nên trực tiếp gọi Service theo cách này.

Chúng ta sẽ thiết kế rõ hơn ở **Buổi 39 — Worker Object Pattern**.

---

# 32. Một ví dụ mental model tốt hơn

```text
                     GUI THREAD
                 ┌─────────────────┐
                 │     View        │
                 │       ↓         │
                 │   ViewModel     │
                 │       ↓         │
                 │   Start Task    │
                 └───────┬─────────┘
                         │
                         │ start
                         ▼
                  ┌─────────────┐
                  │   Worker    │
                  │             │
                  │  Thread     │
                  └──────┬──────┘
                         │
                         ▼
                      Service
                         │
                         ▼
                    Repository
                         │
                         ▼
                      SQLite
```

Worker hoàn thành:

```text
Worker
   │
   ├── progress
   ├── result
   ├── error
   └── finished
          │
          ▼
      GUI Thread
```

---

# 33. `QApplication.processEvents()` có phải giải pháp?

Bạn có thể thấy code:

```python
for item in items:
    process(item)

    QApplication.processEvents()
```

Nó có thể làm GUI responsive hơn trong một số tình huống, nhưng:

> **Không nên xem đây là giải pháp concurrency chính.**

Nó chỉ ép event loop xử lý event giữa các lần iteration.

---

# 34. Vì sao `processEvents()` nguy hiểm?

Có thể tạo:

```text
re-entrancy
```

Ví dụ:

```text
Task đang chạy
     ↓
processEvents()
     ↓
User click button
     ↓
slot khác chạy
     ↓
thay đổi state
     ↓
quay lại task
```

State có thể trở nên khó kiểm soát.

Do đó:

```text
processEvents()
```

không thay thế:

```text
QThread
QThreadPool
asyncio
```

---

# 35. `QTimer` cũng không biến task thành background

Sai suy nghĩ:

```python
QTimer.singleShot(
    0,
    long_task
)
```

rồi nghĩ:

> "Task chạy background."

Không.

Nếu callback chạy trong GUI thread:

```text
GUI Thread
    ↓
QTimer callback
    ↓
long_task()
```

GUI vẫn freeze.

`QTimer` chỉ giúp **schedule event**, không tự tạo worker thread.

---

# 36. Thread-safe không có nghĩa là GUI-safe

Một function:

```python
def update_data():
    ...
```

có thể thread-safe.

Nhưng:

```python
label.setText(...)
```

là thao tác GUI và phải được thiết kế chạy đúng GUI thread.

Đừng nhầm:

```text
thread-safe
```

với:

```text
safe to update Qt widgets from any thread
```

---

# 37. Quy tắc vàng

Hãy ghi nhớ:

```text
┌─────────────────────────────────────┐
│           GUI THREAD                │
│                                     │
│  QWidget                            │
│  QMainWindow                        │
│  QListView                          │
│  QLabel                             │
│  QPushButton                        │
│  Event Loop                         │
│                                     │
│  → UI work                          │
└─────────────────────────────────────┘

                 ↕ Signals

┌─────────────────────────────────────┐
│          WORKER THREAD              │
│                                     │
│  HTTP                               │
│  Crawl                              │
│  File I/O                           │
│  Long database task                 │
│  Background processing              │
└─────────────────────────────────────┘
```

---

# 38. Demo hoàn chỉnh: nhận biết GUI Thread

```python
import threading

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.label = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.show_thread()

    def show_thread(self):
        thread = threading.current_thread()

        self.label.setText(
            f"Python thread: {thread.name}"
        )


app = QApplication([])

window = Window()
window.show()

app.exec()
```

Kết quả thường sẽ là:

```text
Python thread: MainThread
```

---

# 39. Demo freeze

```python
import time

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.button = QPushButton(
            "Start"
        )

        self.button.clicked.connect(
            self.run_task
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)

    def run_task(self):
        time.sleep(5)


app = QApplication([])

window = Window()
window.show()

app.exec()
```

Trong 5 giây:

```text
GUI bị block
```

---

# 40. Bài tập 1

Tạo:

```text
QPushButton("Start")
QLabel()
```

Khi click:

```text
for i in range(10):
    time.sleep(1)
```

Cập nhật:

```text
0
1
2
...
9
```

Quan sát GUI.

Bạn sẽ thấy vấn đề:

```text
GUI không update bình thường
```

---

# 41. Bài tập 2

Tạo:

```text
Button: Start
Button: Click me
Label
```

Trong `Start`:

```python
time.sleep(5)
```

Trong `Click me`:

```python
label.setText("Clicked")
```

Thử:

```text
Click Start
↓
ngay lập tức Click me
```

Bạn sẽ thấy:

```text
Click me
```

không được xử lý ngay.

Đây là bằng chứng trực quan cho:

```text
blocking GUI thread
```

---

# 42. Bài tập 3 — Thread identification

Tạo một function:

```python
def print_thread():
    ...
```

in:

```text
Python thread name
thread ident
Qt current thread
```

Sau đó gọi từ GUI.

Mục tiêu:

> Nhận biết GUI đang chạy trên thread nào.

---

# 43. Bài tập 4 — Architecture

Thiết kế:

```text
Download Button
      ↓
Download Service
      ↓
HTTP
```

Nhưng **chưa cần viết `QThread`**.

Hãy xác định:

```text
Cái gì chạy GUI thread?
Cái gì chạy worker thread?
Signal nào cần có?
```

---

# 44. Bài tập 5 — Phân loại task

Phân loại:

| Task               | GUI Thread? |
| ------------------ | ----------- |
| `button.setText()` | ✅           |
| `label.setText()`  | ✅           |
| `QMessageBox`      | ✅           |
| HTTP request 10s   | ❌           |
| Crawl 1000 URLs    | ❌           |
| Đọc file 2GB       | ❌           |
| Tính toán CPU 30s  | ❌           |
| Update ProgressBar | ✅           |
| Nhận worker signal | ✅           |

---

# 45. Kiến thức cần nhớ

Sau Buổi 36, bạn cần hiểu rõ 6 điểm:

### 1.

```text
PySide6 GUI có GUI Thread.
```

### 2.

```text
GUI Thread chạy Event Loop.
```

### 3.

```text
Event Loop cần được trả quyền thường xuyên.
```

### 4.

```text
Long-running/blocking task
→ không nên chạy trên GUI Thread.
```

### 5.

```text
Worker Thread
→ xử lý background work.
```

### 6.

```text
Worker ↔ GUI
→ Signals / Events.
```

---

# 46. Mental Model cuối buổi

Đừng nhớ `QThread` trước.

Hãy nhớ:

```text
                    EVENT LOOP
                        │
                        ▼
               ┌─────────────────┐
               │   GUI THREAD    │
               │                 │
               │  handle events  │
               │  update UI      │
               │  emit/receive   │
               └────────┬────────┘
                        │
                 start worker
                        │
                        ▼
               ┌─────────────────┐
               │ WORKER THREAD   │
               │                 │
               │ long task       │
               │ HTTP            │
               │ Crawl           │
               │ DB              │
               └────────┬────────┘
                        │
                    signals
                        │
                        ▼
               ┌─────────────────┐
               │   GUI THREAD    │
               │ update UI       │
               └─────────────────┘
```

**Buổi 36 chưa cần học `QThread`.** Mục tiêu là hiểu tại sao nó tồn tại.

Sang **Buổi 37 — Vì sao GUI bị freeze?**, chúng ta sẽ đào sâu hơn vào **blocking operation, event loop starvation, synchronous I/O, CPU-bound task, GIL**, và đặc biệt phân tích chính xác chuyện gì xảy ra bên trong khi một `slot` chạy mất 10 giây.
