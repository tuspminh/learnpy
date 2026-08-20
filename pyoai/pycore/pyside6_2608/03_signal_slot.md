# Buổi 3 — Signal & Slot trong PySide6

Đây là **một trong những bài quan trọng nhất của PySide6**.

Nếu ở Buổi 1 ta học:

```text
Event Loop
```

và Buổi 2:

```text
QObject
Parent / Child
Object Tree
```

thì hôm nay ta nối chúng lại:

```text
User Action
    ↓
Event
    ↓
Signal
    ↓
Slot
    ↓
Business Logic
    ↓
UI Update
```

Sau buổi này bạn phải hiểu được **Signal là gì, Slot là gì, `connect()` làm gì, `emit()` làm gì và vì sao Qt dùng Signal/Slot thay vì gọi callback trực tiếp**.

---

# 1. Callback truyền thống

Trước khi học Signal/Slot, hãy hiểu callback.

Python thuần:

```python
def on_click():
    print("Button clicked")
```

Ta có thể truyền function:

```python
def run(callback):
    callback()


run(on_click)
```

Kết quả:

```text
Button clicked
```

Đây là:

```text
function A
    ↓
truyền function B
    ↓
A gọi B
```

GUI cũng thường cần cơ chế tương tự.

---

# 2. GUI cần phản ứng với sự kiện

Ví dụ:

```text
User
 ↓
click button
 ↓
Application
 ↓
do something
```

Ta có thể nghĩ:

```python
def on_button_clicked():
    print("Clicked")
```

Nhưng Qt không thiết kế GUI theo kiểu mỗi widget phải biết trực tiếp function nào cần gọi.

Thay vào đó Qt sử dụng:

```text
Signal
   ↓
Slot
```

---

# 3. Signal là gì?

Có thể hiểu đơn giản:

> **Signal là thông báo rằng một sự kiện nào đó đã xảy ra.**

Ví dụ `QPushButton` có signal:

```python
button.clicked
```

Khi user click:

```text
User clicks
     ↓
QPushButton
     ↓
clicked signal
```

Signal không nhất thiết biết business logic của ứng dụng là gì.

Nó chỉ thông báo:

> "Tôi vừa được click."

---

# 4. Slot là gì?

Slot là function/method được gọi khi signal phát ra.

Ví dụ:

```python
def on_click():
    print("Hello")
```

Ta kết nối:

```python
button.clicked.connect(on_click)
```

Sơ đồ:

```text
QPushButton
    │
    │ clicked
    ▼
 Signal
    │
    │ connect()
    ▼
on_click()
```

Đây là kiến trúc rất quan trọng.

---

# 5. Ví dụ đầu tiên

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
)


app = QApplication(sys.argv)

button = QPushButton("Click me")


def on_click():
    print("Button clicked")


button.clicked.connect(on_click)

button.show()

sys.exit(app.exec())
```

Khi user click:

```text
click
 ↓
button.clicked
 ↓
on_click()
 ↓
Button clicked
```

---

# 6. `connect()`

Dòng:

```python
button.clicked.connect(on_click)
```

có thể đọc như:

> Khi `clicked` phát ra, hãy gọi `on_click`.

Cấu trúc:

```python
signal.connect(slot)
```

Ví dụ:

```python
button.clicked.connect(on_click)
```

---

# 7. `emit()`

Signal có thể được phát bằng:

```python
signal.emit()
```

Ví dụ custom signal:

```python
from PySide6.QtCore import QObject, Signal


class MyObject(QObject):

    something_happened = Signal()
```

Tạo object:

```python
obj = MyObject()
```

Kết nối:

```python
obj.something_happened.connect(
    lambda: print("Something happened")
)
```

Phát signal:

```python
obj.something_happened.emit()
```

Kết quả:

```text
Something happened
```

---

# 8. `Signal()` — Custom Signal

Đây là phần rất quan trọng.

Ta có thể tự tạo signal.

```python
from PySide6.QtCore import QObject, Signal


class Worker(QObject):

    finished = Signal()
```

`finished` là signal do chúng ta định nghĩa.

Sử dụng:

```python
worker = Worker()

worker.finished.connect(
    lambda: print("Worker finished")
)
```

Sau đó:

```python
worker.finished.emit()
```

---

# 9. Signal có thể truyền dữ liệu

Signal không chỉ truyền:

```text
"đã xảy ra"
```

Nó có thể truyền dữ liệu.

Ví dụ:

```python
message_changed = Signal(str)
```

Signal này mang một `str`.

Ta có:

```python
class MyObject(QObject):

    message_changed = Signal(str)
```

Connect:

```python
def on_message(message):
    print(message)


obj.message_changed.connect(on_message)
```

Emit:

```python
obj.message_changed.emit("Hello PySide6")
```

Kết quả:

```text
Hello PySide6
```

---

# 10. Signal nhiều tham số

Ví dụ:

```python
data_changed = Signal(str, int)
```

Signal này truyền:

```text
str
int
```

Ví dụ:

```python
class Downloader(QObject):

    progress = Signal(str, int)
```

Emit:

```python
self.progress.emit("file.zip", 50)
```

Slot:

```python
def on_progress(filename, percent):
    print(filename, percent)
```

Connect:

```python
downloader.progress.connect(on_progress)
```

---

# 11. Một ví dụ thực tế

Giả sử ta có Downloader:

```text
Downloader
    │
    ├── progress
    ├── finished
    └── error
```

GUI:

```text
MainWindow
    │
    ├── ProgressBar
    ├── StatusLabel
    └── ErrorMessage
```

Không nên để Downloader biết:

```python
self.progress_bar.setValue(...)
```

vì Downloader lúc đó phụ thuộc trực tiếp vào GUI.

Thay vào đó:

```text
Downloader
    │
    │ progress.emit(50)
    ▼
Signal
    │
    ▼
MainWindow
    │
    ▼
ProgressBar
```

Đây là **loose coupling**.

---

# 12. Loose Coupling

Đây chính là sức mạnh lớn của Signal/Slot.

Không tốt:

```python
class Downloader:

    def __init__(self, progress_bar):
        self.progress_bar = progress_bar

    def download(self):
        ...
        self.progress_bar.setValue(50)
```

Downloader biết GUI.

Kiến trúc tốt hơn:

```python
class Downloader(QObject):

    progress = Signal(int)

    def download(self):
        ...
        self.progress.emit(50)
```

GUI:

```python
downloader.progress.connect(
    progress_bar.setValue
)
```

Bây giờ:

```text
Downloader
   │
   └── không biết GUI tồn tại
```

Đây là một nguyên tắc kiến trúc rất quan trọng.

---

# 13. Signal có thể connect trực tiếp vào method

Ta không nhất thiết phải viết:

```python
def update_progress(value):
    progress_bar.setValue(value)


downloader.progress.connect(update_progress)
```

Có thể viết:

```python
downloader.progress.connect(
    progress_bar.setValue
)
```

Vì:

```python
progress_bar.setValue
```

là một callable.

---

# 14. Signal → Signal

Một Signal có thể connect tới Signal khác.

Ví dụ:

```python
class Worker(QObject):

    finished = Signal()


class Controller(QObject):

    finished = Signal()
```

Có thể:

```python
worker.finished.connect(controller.finished)
```

Khi:

```python
worker.finished.emit()
```

thì:

```text
worker.finished
      ↓
controller.finished
```

Signal được truyền tiếp.

Điều này hữu ích trong architecture lớn.

---

# 15. Disconnect

Ta có:

```python
button.clicked.connect(on_click)
```

Có thể ngắt:

```python
button.clicked.disconnect(on_click)
```

Sau đó:

```text
button
  │
clicked
  │
X── on_click
```

không còn connection đó nữa.

---

# 16. Một signal có nhiều slot

Ví dụ:

```python
button.clicked.connect(save_data)
button.clicked.connect(update_ui)
button.clicked.connect(write_log)
```

Khi click:

```text
             ┌── save_data()
             │
clicked ─────┼── update_ui()
             │
             └── write_log()
```

Đây là một đặc điểm rất mạnh.

Một event có thể thông báo cho nhiều thành phần.

---

# 17. Một slot có nhiều signal

Ngược lại:

```python
button1.clicked.connect(refresh)
button2.clicked.connect(refresh)
timer.timeout.connect(refresh)
```

Ta có:

```text
button1 ───┐
           │
button2 ───┼──→ refresh()
           │
timer ─────┘
```

Một function có thể nhận notification từ nhiều signal.

---

# 18. Lambda

Có thể:

```python
button.clicked.connect(
    lambda: print("Clicked")
)
```

Hoặc:

```python
button.clicked.connect(
    lambda: label.setText("Clicked!")
)
```

Điều này tiện cho logic rất ngắn.

Nhưng đừng lạm dụng lambda cho business logic phức tạp.

Không nên:

```python
button.clicked.connect(
    lambda: (
        validate(),
        save(),
        update_database(),
        refresh_table(),
        log(),
    )
)
```

Tốt hơn:

```python
button.clicked.connect(self.handle_save)
```

---

# 19. Signal trong class

Một pattern rất quan trọng:

```python
class Counter(QObject):

    value_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self._value = 0

    def set_value(self, value):
        self._value = value
        self.value_changed.emit(value)
```

Sử dụng:

```python
counter = Counter()

counter.value_changed.connect(
    lambda value: print("Value:", value)
)

counter.set_value(10)
counter.set_value(20)
```

Kết quả:

```text
Value: 10
Value: 20
```

---

# 20. Signal như một "event channel"

Mental model tốt:

```text
                Signal
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
      Slot A    Slot B    Slot C
```

Signal không cần biết:

```text
Slot A là ai?
Slot B là ai?
Slot C làm gì?
```

Nó chỉ phát:

```python
signal.emit(...)
```

Qt sẽ xử lý các connection.

---

# 21. Signal + Event Loop

Liên hệ với Buổi 1:

```text
User click
    ↓
Qt Event Loop
    ↓
QPushButton
    ↓
clicked Signal
    ↓
Connected Slot
```

Cho nên Signal/Slot không tồn tại độc lập.

Nó nằm trong hệ thống event-driven của Qt.

---

# 22. Signal + QObject

Liên hệ với Buổi 2:

```text
QObject
   │
   ├── Signal
   │
   ├── Slot
   │
   ├── Parent
   │
   └── Children
```

Đây là lý do `QObject` quan trọng như vậy.

---

# 23. Ví dụ hoàn chỉnh — Counter

Hãy xem một ví dụ gần với kiến trúc thực tế:

```python
import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Counter(QObject):

    value_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self._value = 0

    def increment(self):
        self._value += 1
        self.value_changed.emit(self._value)

    def decrement(self):
        self._value -= 1
        self.value_changed.emit(self._value)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.counter = Counter()

        self.label = QLabel("0")

        self.increment_button = QPushButton("+")
        self.decrement_button = QPushButton("-")

        layout = QVBoxLayout(self)

        layout.addWidget(self.label)
        layout.addWidget(self.increment_button)
        layout.addWidget(self.decrement_button)

        self.increment_button.clicked.connect(
            self.counter.increment
        )

        self.decrement_button.clicked.connect(
            self.counter.decrement
        )

        self.counter.value_changed.connect(
            self.update_value
        )

    def update_value(self, value):
        self.label.setText(str(value))


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())
```

Kiến trúc:

```text
             ┌───────────────┐
             │    Button +   │
             └───────┬───────┘
                     │ clicked
                     ▼
             counter.increment()
                     │
                     ▼
              value_changed
                     │
                     ▼
             update_value()
                     │
                     ▼
                  QLabel
```

Đây đã bắt đầu giống architecture của ứng dụng thực tế.

---

# 24. Điều quan trọng nhất trong ví dụ trên

`Counter` **không biết `QLabel` tồn tại**.

Nó chỉ biết:

```python
self.value_changed.emit(value)
```

Trong khi Window quyết định:

```python
self.counter.value_changed.connect(
    self.update_value
)
```

Do đó:

```text
Counter
   │
   │ Signal
   ▼
Window
   │
   ▼
UI
```

Thay vì:

```text
Counter
   │
   └── QLabel
```

Đây chính là cách chúng ta bắt đầu xây dựng **separation of concerns**.

---

# 25. Signal với dữ liệu domain

Sau này bạn có thể có:

```python
class StoryService(QObject):

    story_loaded = Signal(object)
    error_occurred = Signal(str)
    progress_changed = Signal(int)
```

GUI:

```python
service.story_loaded.connect(self.show_story)
service.error_occurred.connect(self.show_error)
service.progress_changed.connect(self.progress_bar.setValue)
```

Ta có:

```text
StoryService
    │
    ├── story_loaded ─────→ UI
    │
    ├── error_occurred ───→ UI
    │
    └── progress_changed ─→ UI
```

Đây là pattern chúng ta sẽ dùng rất nhiều trong các project lớn.

---

# 26. Signal không phải Magic

Hãy tránh suy nghĩ:

> "Signal/Slot là một loại callback thần bí của Qt."

Mental model chính xác hơn:

```text
Signal
  │
  ├── giữ các connection
  │
  └── emit()
        │
        ├── gọi slot A
        ├── gọi slot B
        └── gọi slot C
```

Và Qt còn cung cấp cơ chế connection phù hợp với thread/event-loop.

Phần này sẽ trở nên cực kỳ quan trọng khi chúng ta học:

> **QThread + Worker**

---

# 27. `Signal` phải khai báo ở class level

Thường viết:

```python
class Worker(QObject):

    finished = Signal()
```

Không viết kiểu:

```python
class Worker(QObject):

    def __init__(self):
        self.finished = Signal()
```

Signal Qt được thiết kế để khai báo ở class definition.

Đây là điểm bạn cần nhớ.

---

# 28. Signal và type

Bạn có thể định nghĩa:

```python
Signal()
```

hoặc:

```python
Signal(str)
```

hoặc:

```python
Signal(int)
```

hoặc:

```python
Signal(str, int)
```

Ví dụ:

```python
progress = Signal(int)
```

nghĩa là:

```python
progress.emit(50)
```

Slot tương ứng:

```python
def on_progress(value):
    ...
```

---

# 29. Bài tập 1 — Counter

Tự viết:

```text
Counter
   │
   ├── increment()
   ├── decrement()
   └── value_changed
```

UI:

```text
┌──────────────────────┐
│         0            │
│                      │
│    [ - ]   [ + ]     │
└──────────────────────┘
```

Yêu cầu:

* Không cho `Window` trực tiếp thay đổi `_value`.
* `Counter` phải tự quản lý state.
* Khi value thay đổi phải emit `value_changed`.
* UI chỉ lắng nghe signal.

---

# 30. Bài tập 2 — Temperature

Tạo:

```python
class Temperature(QObject):
    value_changed = Signal(float)
```

Có:

```python
increase()
decrease()
```

UI:

```text
Temperature: 25.0 °C

[-]     [+]
```

Mỗi lần thay đổi:

```text
Temperature
      ↓
value_changed
      ↓
QLabel
```

---

# 31. Bài tập 3 — Todo

Tạo:

```python
class TodoManager(QObject):

    todo_added = Signal(str)
    todo_removed = Signal(int)
```

Ví dụ:

```python
manager.add("Learn PySide6")
```

phải phát:

```python
todo_added.emit("Learn PySide6")
```

GUI lắng nghe:

```python
manager.todo_added.connect(...)
```

**Không cho `TodoManager` biết QListWidget tồn tại.**

Đây là bài tập rất quan trọng để tập tư duy architecture.

---

# 32. Câu hỏi kiểm tra

Hãy tự trả lời:

### Câu 1

Khác nhau giữa:

```python
button.clicked.connect(on_click)
```

và:

```python
button.clicked.connect(on_click())
```

là gì?

---

### Câu 2

Tại sao:

```python
button.clicked.connect(on_click)
```

truyền function nhưng không có `()`?

---

### Câu 3

`emit()` làm gì?

---

### Câu 4

Tại sao `Counter` không nên giữ reference tới `QLabel`?

---

### Câu 5

Một signal có thể connect tới bao nhiêu slot?

---

### Câu 6

Một slot có thể nhận signal từ nhiều nguồn không?

---

# 33. Mental Model sau 3 buổi

Đến đây bạn nên có bức tranh:

```text
                    QApplication
                         │
                         ▼
                    Event Loop
                         │
                         ▼
                       Event
                         │
                         ▼
                      Widget
                         │
                         ▼
                      Signal
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Slot        Slot        Slot
             │           │           │
             ▼           ▼           ▼
         Service      State          UI
```

Và phía dưới:

```text
QObject
   │
   ├── Parent
   ├── Children
   ├── Signal
   ├── Event
   └── Lifetime
```

Đây chính là **core mental model của PySide6**.

---

## Buổi tiếp theo — Event System

**Buổi 4** chúng ta sẽ học:

* `QEvent`
* `event()`
* Event propagation
* Mouse event
* Keyboard event
* `mousePressEvent()`
* `keyPressEvent()`
* `closeEvent()`
* `accept()`
* `ignore()`
* Event Filter
* `installEventFilter()`

Đặc biệt, tôi sẽ chỉ cho bạn sự khác nhau giữa:

```text
Event
Signal
Slot
Callback
```

vì **4 khái niệm này rất dễ bị người mới học PySide6 trộn lẫn với nhau**.
