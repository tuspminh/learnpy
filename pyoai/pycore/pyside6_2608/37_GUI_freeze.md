# Buổi 37 — Vì sao GUI bị Freeze?

Ở Buổi 36, ta đã có mental model:

```text
GUI Thread
    │
    └── Event Loop
```

Và nguyên tắc:

> **GUI Thread phải quay lại Event Loop càng nhanh càng tốt.**

Hôm nay ta đi sâu vào **vì sao GUI freeze**, freeze ở đâu, và cách phân biệt **I/O-bound**, **CPU-bound**, **blocking**, **sleep** trước khi bước sang `QThread` ở Buổi 38.

---

# 1. Freeze thực sự nghĩa là gì?

Khi người dùng nói:

> "Ứng dụng bị treo."

Không nhất thiết process đã chết.

Thường là:

```text
Application
     │
     ▼
GUI Thread
     │
     ▼
đang chạy một task lâu
     │
     X
Event Loop không được xử lý
```

Ứng dụng vẫn đang chạy.

Chỉ là **GUI không có cơ hội xử lý event mới**.

---

# 2. Event Loop là "trái tim" của GUI

Ta hình dung:

```text
                  Event Queue
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
    Click          Keyboard       Paint
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                 Event Loop
                      │
                      ▼
                  process()
```

Event Loop liên tục lấy event và xử lý.

Ví dụ:

```text
Click Button
     ↓
clicked signal
     ↓
slot()
     ↓
return
     ↓
Event Loop
     ↓
event tiếp theo
```

---

# 3. Vấn đề nằm ở `slot()`

Ví dụ:

```python
def on_click(self):
    time.sleep(10)
```

Khi click:

```text
Event Loop
    │
    ▼
on_click()
    │
    ├──────────── 10 giây ────────────┐
    │                                  │
    │                                  ▼
    │                               return
    │
    X
```

Trong 10 giây đó:

```text
Event Loop
```

không thể tiếp tục xử lý event tiếp theo.

---

# 4. Event Queue vẫn có thể nhận event

Đây là điểm rất quan trọng.

Giả sử:

```text
User click Start
```

sau đó:

```text
User click Button A
User click Button B
User resize window
User type keyboard
```

Event có thể tiếp tục được đưa vào queue:

```text
Event Queue

┌──────────────┐
│ Click A      │
├──────────────┤
│ Click B      │
├──────────────┤
│ Resize       │
├──────────────┤
│ Key Event    │
└──────────────┘
```

Nhưng:

```text
GUI Thread
    ↓
đang bận
```

nên chưa xử lý được.

---

# 5. Đây gọi là Event Loop Starvation

Một thuật ngữ quan trọng:

> **Event Loop Starvation**

Có thể hiểu:

```text
Event Loop
    ↓
không được CPU time để xử lý event
    ↓
GUI phản hồi chậm / freeze
```

Không phải event biến mất.

Chúng đang **chờ**.

---

# 6. Ví dụ trực quan

```python
import time

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.label = QLabel("Ready")
        self.button = QPushButton("Start")

        self.button.clicked.connect(self.start)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def start(self):
        self.label.setText("Working...")

        time.sleep(5)

        self.label.setText("Done")


app = QApplication([])

window = Window()
window.show()

app.exec()
```

Bạn có thể nghĩ:

```python
self.label.setText("Working...")
```

sẽ lập tức hiển thị.

Nhưng thực tế không đơn giản như vậy.

---

# 7. Tại sao `"Working..."` có thể không xuất hiện ngay?

Đây là một điểm cực kỳ quan trọng trong Qt.

Khi:

```python
self.label.setText("Working...")
```

Qt thay đổi state của widget và có thể yêu cầu repaint.

Nhưng việc vẽ GUI thực tế liên quan đến Event Loop.

Sau đó:

```python
time.sleep(5)
```

chặn GUI thread.

Vì vậy repaint có thể chưa được xử lý cho đến khi slot trả về.

Kết quả người dùng có thể thấy:

```text
Ready
   ↓
5 giây
   ↓
Done
```

thay vì:

```text
Working...
   ↓
5 giây
   ↓
Done
```

---

# 8. Đây là một lỗi thiết kế phổ biến

Developer nghĩ:

```python
label.setText("Downloading...")
download()
label.setText("Done")
```

Nhưng:

```text
setText()
   ↓
download()
   ↓
GUI Thread blocked
   ↓
repaint không được xử lý
```

Cho nên UI không phản ánh trạng thái như mong muốn.

---

# 9. `time.sleep()` là ví dụ đơn giản nhất

```python
time.sleep(5)
```

là blocking.

Nhưng không chỉ `sleep()` mới gây freeze.

---

# 10. HTTP blocking

Ví dụ:

```python
import requests


def download():
    response = requests.get(
        "https://example.com"
    )

    return response.text
```

Nếu gọi trong GUI:

```python
def on_click(self):
    data = download()
```

luồng:

```text
GUI Thread
    ↓
requests.get()
    ↓
waiting network
    ↓
waiting server
    ↓
response
```

Trong thời gian chờ:

```text
Event Loop ❌
```

---

# 11. Database blocking

Ví dụ:

```python
def load_stories():
    return repository.get_all()
```

Nếu database có:

```text
1,000,000 records
```

hoặc query rất nặng:

```text
GUI Thread
    ↓
SQL query
    ↓
3 seconds
    ↓
return
```

GUI có thể freeze 3 giây.

---

# 12. File I/O

Ví dụ:

```python
with open("huge_file.txt") as f:
    data = f.read()
```

Nếu file cực lớn:

```text
GUI Thread
    ↓
read()
    ↓
disk I/O
    ↓
memory allocation
    ↓
processing
```

GUI có thể bị block.

---

# 13. CPU-bound task

Còn nguy hiểm hơn là:

```python
def calculate():
    total = 0

    for i in range(500_000_000):
        total += i

    return total
```

Đây là CPU-bound.

```text
GUI Thread
    ↓
CPU calculation
    ↓
100% busy
    ↓
Event Loop không được xử lý
```

---

# 14. Phân biệt I/O-bound và CPU-bound

| Loại      | Ví dụ            |
| --------- | ---------------- |
| I/O-bound | HTTP             |
| I/O-bound | File             |
| I/O-bound | Database         |
| I/O-bound | Socket           |
| CPU-bound | Image processing |
| CPU-bound | Compression      |
| CPU-bound | Parsing cực nặng |
| CPU-bound | Tính toán lớn    |

Cả hai đều có thể làm GUI freeze nếu chạy trực tiếp trong GUI thread.

---

# 15. Blocking ≠ CPU-bound

Đây là distinction rất quan trọng.

### `sleep()`

```python
time.sleep(10)
```

CPU gần như không làm gì.

Nhưng GUI vẫn freeze.

### CPU calculation

```python
for i in range(...):
    ...
```

CPU hoạt động rất mạnh.

GUI vẫn freeze.

Do đó:

```text
I/O blocking → freeze
CPU-heavy     → freeze
sleep         → freeze
```

nếu chúng chạy trong GUI thread.

---

# 16. Một nguyên tắc mạnh hơn

Đừng chỉ nghĩ:

> "Task này tốn CPU không?"

Hãy hỏi:

> **"Task này có giữ GUI thread quá lâu không?"**

Nếu:

```text
10 ms
```

thường không đáng kể.

Nếu:

```text
100 ms
500 ms
1 s
5 s
30 s
```

thì bắt đầu trở thành vấn đề.

---

# 17. GUI cần latency thấp

GUI programming quan tâm rất nhiều đến:

```text
Responsiveness
```

Ví dụ:

```text
Click
 ↓
phản hồi
```

nên xảy ra gần như ngay lập tức.

Nếu:

```text
Click
 ↓
2 giây
 ↓
phản hồi
```

người dùng sẽ cảm giác ứng dụng bị treo.

---

# 18. Một task 50 ms chưa chắc nguy hiểm

Ví dụ:

```python
def on_click(self):
    result = calculate_small_value()
    self.label.setText(str(result))
```

Nếu chạy:

```text
5 ms
```

thì hoàn toàn ổn.

Không cần tạo thread cho mọi function.

---

# 19. Không nên lạm dụng Thread

Sai:

```text
Mỗi function
    ↓
1 thread
```

Không cần.

Ví dụ:

```python
def add(a, b):
    return a + b
```

Không nên:

```text
QThread
    ↓
add()
```

Đây là over-engineering.

---

# 20. Vấn đề thật sự là Long-running Task

Ví dụ:

```text
HTTP download
    10s

Crawl
    2 phút

Generate PDF
    30s

Parse large HTML
    5s

Process images
    1 phút
```

Đây là những candidate cho background execution.

---

# 21. Freeze chain

Hãy nhớ chuỗi này:

```text
User Event
     ↓
Signal
     ↓
Slot
     ↓
Long-running operation
     ↓
GUI Thread blocked
     ↓
Event Loop blocked
     ↓
Events accumulate
     ↓
GUI không phản hồi
```

Đây là mental model quan trọng nhất của Buổi 37.

---

# 22. Vì sao ProgressBar không chạy?

Giả sử:

```python
def start(self):
    for i in range(101):
        self.progress.setValue(i)
        time.sleep(0.1)
```

Bạn có thể mong:

```text
0%
10%
20%
...
100%
```

Nhưng GUI có thể không repaint từng bước như mong muốn.

Bởi vì:

```text
GUI Thread
    ↓
for loop
    ↓
sleep
    ↓
sleep
    ↓
sleep
    ↓
...
```

Event Loop không có cơ hội xử lý repaint bình thường.

---

# 23. Đây là lý do `QProgressBar` không giải quyết concurrency

Nhiều người mới nghĩ:

```text
Có ProgressBar
→ GUI sẽ update
```

Không.

ProgressBar chỉ là widget.

Nó không tạo background task.

Kiến trúc đúng là:

```text
Worker
    │
    ├── progress 10
    ├── progress 20
    ├── progress 30
    │
    ▼
GUI Thread
    │
    ▼
ProgressBar
```

---

# 24. `QApplication.processEvents()` có thể làm gì?

Bạn có thể thử:

```python
from PySide6.QtWidgets import QApplication


for i in range(101):
    self.progress.setValue(i)

    QApplication.processEvents()

    time.sleep(0.1)
```

Bây giờ GUI có cơ hội xử lý event.

Nhưng:

> Đây chỉ là workaround, không phải kiến trúc concurrency tốt.

---

# 25. Vì sao không nên dựa vào `processEvents()`?

Giả sử:

```text
Task A
  ↓
processEvents()
  ↓
Task B chạy
  ↓
Task B thay đổi state
  ↓
Task A tiếp tục
```

Có thể tạo:

```text
Re-entrancy
```

và state trở nên khó dự đoán.

Vì vậy:

```text
processEvents()
```

không nên là chiến lược chính để xử lý long-running work.

---

# 26. GUI Thread và GIL

Đối với Python, còn một khái niệm nữa:

```text
GIL
```

Global Interpreter Lock trong CPython ảnh hưởng đến việc chạy Python bytecode đồng thời trong nhiều thread.

Nhưng **đừng hiểu rằng GIL là nguyên nhân trực tiếp khiến PySide6 GUI freeze**.

Ví dụ:

```python
time.sleep(5)
```

vẫn freeze GUI khi chạy trên GUI thread, dù đây không phải CPU-bound Python code.

Nguyên nhân trực tiếp là:

```text
GUI Thread đang bị block
```

---

# 27. GIL quan trọng khi nào?

Đặc biệt khi chúng ta có:

```text
CPU-bound Python code
```

ví dụ:

```python
for i in range(500_000_000):
    ...
```

Đây là lúc phải suy nghĩ tới:

```text
Thread
vs
Process
```

Buổi 38–45 sẽ giúp chúng ta xây mental model đó.

---

# 28. Một kiến trúc đúng

Thay vì:

```text
GUI
 │
 └── long_task()
```

ta muốn:

```text
GUI
 │
 └── start_task()
          │
          ▼
       Worker
          │
          ▼
      long_task()
```

GUI:

```text
start
 ↓
return ngay
 ↓
Event Loop tiếp tục
```

Worker:

```text
long_task()
```

---

# 29. Worker báo kết quả bằng Signal

Ví dụ mental model:

```text
Worker
   │
   ├── progress.emit(20)
   ├── progress.emit(50)
   ├── progress.emit(100)
   └── finished.emit(result)
```

GUI:

```text
progress
   ↓
ProgressBar

finished
   ↓
Label
```

---

# 30. GUI không cần biết Worker thực hiện thế nào

Đây là điểm liên quan trực tiếp đến UI Architecture.

GUI chỉ cần biết:

```text
Task started
Task progress
Task finished
Task failed
```

Không cần biết:

```text
HTTP
SQLite
Crawler
Thread
```

Đó là separation of concerns.

---

# 31. Liên hệ với Story Reader

Project của chúng ta:

```text
Story Reader
```

có các task:

```text
Download story
Parse HTML
Crawl chapters
Save database
Download images
Generate audio
```

Nếu làm:

```text
MainWindow
    ↓
Crawler.crawl()
```

thì rất dễ:

```text
GUI FREEZE
```

Kiến trúc cần hướng tới:

```text
MainWindow
     │
     ▼
Application Service
     │
     ▼
Worker
     │
     ▼
Crawler
     │
     ▼
Repository
```

và:

```text
Worker
   │
   ├── progress
   ├── result
   ├── error
   └── finished
```

---

# 32. Một ví dụ thực tế

Giả sử crawl:

```text
1000 chapters
```

mỗi chapter:

```text
HTTP request
Parse HTML
SQLite save
```

Nếu trung bình:

```text
0.5 second/chapter
```

thì:

```text
1000 × 0.5
= 500 seconds
≈ 8 phút 20 giây
```

Nếu chạy trong GUI thread:

```text
Crawl
 ↓
8 phút
 ↓
GUI freeze
```

Không thể chấp nhận.

---

# 33. Nhưng nếu crawl bằng Worker?

```text
GUI Thread
    │
    ├── Crawl started
    │
    ├── Event Loop
    │      ↓
    │   responsive
    │
    └── receive progress

Worker Thread
    │
    ├── chapter 1
    ├── chapter 2
    ├── chapter 3
    └── ...
```

Người dùng có thể:

```text
Pause
Cancel
Open another story
View logs
Resize window
```

Đây chính là mục tiêu của phần IV.

---

# 34. Một sai lầm khác: tạo thread nhưng vẫn update GUI trực tiếp

Ví dụ ý tưởng:

```python
class Worker:
    def run(self):
        self.progress_bar.setValue(50)
```

Sai về mặt thiết kế.

Nên:

```text
Worker
   │
   │ emit(50)
   ▼
GUI Thread
   │
   ▼
progress_bar.setValue(50)
```

---

# 35. Quy tắc phân tầng

Một architecture tốt:

```text
Presentation
    │
    │ commands / signals
    ▼
Worker / Application
    │
    ▼
Service
    │
    ▼
Repository
    │
    ▼
Infrastructure
```

Không nên để:

```text
Repository
   ↓
QPushButton
```

hoặc:

```text
Worker
   ↓
QProgressBar trực tiếp
```

---

# 36. Bài tập thực hành

## Bài 1 — Freeze

Viết:

```text
Button Start
Button Ping
Label
```

`Start`:

```python
time.sleep(5)
```

`Ping`:

```python
label.setText("Pong")
```

Thử:

```text
Click Start
→ ngay lập tức click Ping
```

Quan sát.

---

# 37. Bài 2 — ProgressBar

Viết:

```python
for i in range(101):
    progress.setValue(i)
    time.sleep(0.05)
```

Quan sát:

```text
GUI có update mượt không?
```

Sau đó thử:

```python
QApplication.processEvents()
```

và so sánh.

Mục tiêu không phải dùng `processEvents()` làm giải pháp, mà để **thấy Event Loop đang bị block như thế nào**.

---

# 38. Bài 3 — Phân loại

Với mỗi task, hãy xác định:

```text
GUI thread
hay
background?
```

### A

```python
label.setText("Hello")
```

### B

```python
requests.get(url)
```

### C

```python
for _ in range(500_000_000):
    ...
```

### D

```python
button.setEnabled(False)
```

### E

```python
open("large_file.bin", "rb").read()
```

### F

```python
progress_bar.setValue(50)
```

Đáp án:

```text
A → GUI
B → Background
C → Background
D → GUI
E → Background
F → GUI
```

---

# 39. Bài tập kiến trúc

Thiết kế flow cho:

```text
[ Crawl ]
    ↓
Crawler
    ↓
100 chapters
    ↓
SQLite
```

Yêu cầu:

```text
GUI không freeze
Có progress
Có error
Có finished
```

Hãy tự vẽ:

```text
GUI
 ↓
 ?
 ↓
Crawler
 ↓
Repository
```

và xác định:

```text
Worker nằm ở đâu?
Signal nào?
Thread nào?
```

---

# 40. Checklist Buổi 37

Bạn nên có thể giải thích được:

* Event Loop là gì?
* Event Queue là gì?
* Vì sao một `slot` chạy lâu làm GUI freeze?
* Event Loop Starvation là gì?
* Blocking operation là gì?
* I/O-bound là gì?
* CPU-bound là gì?
* Vì sao `requests.get()` có thể freeze GUI?
* Vì sao `time.sleep()` freeze GUI?
* Vì sao CPU-heavy task freeze GUI?
* Vì sao `processEvents()` không phải giải pháp kiến trúc?
* Vì sao ProgressBar không tự tạo concurrency?
* Vì sao Worker không nên trực tiếp sửa Widget?

---

# 41. Mental Model cuối Buổi 37

Hãy nhớ hình này:

```text
                    USER
                      │
                      ▼
                ┌───────────┐
                │   Event   │
                └─────┬─────┘
                      │
                      ▼
              ┌───────────────┐
              │  Event Loop   │
              └───────┬───────┘
                      │
                      ▼
                 ┌─────────┐
                 │  Slot   │
                 └────┬────┘
                      │
             ┌────────┴─────────┐
             │                  │
        short task         long task
             │                  │
             ▼                  ▼
          return          GUI THREAD BLOCK
             │                  │
             ▼                  X
       Event Loop          Event Loop
       tiếp tục            không chạy
```

Và kiến trúc mà chúng ta sẽ xây từ **Buổi 38**:

```text
                 GUI THREAD
              ┌──────────────┐
              │ QApplication │
              │    Event     │
              │    Loop      │
              └──────┬───────┘
                     │
                start worker
                     │
                     ▼
              ┌──────────────┐
              │    WORKER    │
              │              │
              │ long task    │
              │ HTTP         │
              │ Crawl        │
              │ DB           │
              └──────┬───────┘
                     │
                  Signals
                     │
                     ▼
              ┌──────────────┐
              │ GUI THREAD   │
              │ update UI    │
              └──────────────┘
```

**Buổi 38 — `QThread`** sẽ bắt đầu phần thực chiến: hiểu `QThread` thực sự là gì, `start()`, `run()`, thread affinity, event loop của `QThread`, và đặc biệt **vì sao cách dùng `QThread` phổ biến trên mạng rất dễ sai**.
