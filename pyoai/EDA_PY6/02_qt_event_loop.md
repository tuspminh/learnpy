# Buổi 2 — Qt Event Loop Deep Dive

Ở Buổi 1, chúng ta đã hiểu:

```text
Event
   ↓
Event Bus
   ↓
Handler
```

Hôm nay đi xuống **tầng thấp hơn**:

```text
Operating System
       ↓
      Qt
       ↓
Event Queue
       ↓
Event Loop
       ↓
Event Dispatcher
       ↓
QObject / Widget
       ↓
Signal / Slot / Event Handler
```

Đây là phần cực kỳ quan trọng nếu bạn muốn hiểu sâu **PySide6 + Event-Driven Architecture**, đặc biệt sau này khi kết hợp với `QThread`, worker, asyncio và background task.

---

# 1. Một chương trình Python bình thường

Ví dụ:

```python
print("A")
print("B")
print("C")
```

Flow rất đơn giản:

```text
A
 ↓
B
 ↓
C
 ↓
Exit
```

Python chạy từ trên xuống dưới.

---

# 2. Nhưng GUI thì khác

Một ứng dụng PySide6:

```python
from PySide6.QtWidgets import QApplication, QPushButton

app = QApplication()

button = QPushButton("Click me")
button.show()

app.exec()
```

Điểm kỳ lạ là:

```python
app.exec()
```

không phải một câu lệnh chạy công việc cụ thể như:

```python
print(...)
```

Nó bắt đầu một **event loop**.

```text
app.exec()
    │
    ▼
┌─────────────────┐
│   Event Loop    │◄────────┐
└────────┬────────┘         │
         │                  │
         ▼                  │
   lấy Event                │
         │                  │
         ▼                  │
   Dispatch Event           │
         │                  │
         ▼                  │
      Handler               │
         │                  │
         └──────────────────┘
```

Chương trình GUI về cơ bản sẽ ở đây cho đến khi application thoát.

---

# 3. Event Loop là gì?

Có thể hiểu đơn giản:

> **Event Loop là một vòng lặp liên tục chờ event, lấy event và phân phối event đến nơi xử lý nó.**

Khái niệm:

```text
while application_is_running:

    event = get_next_event()

    dispatch(event)
```

Đây là mô hình khái niệm, **không phải implementation thực tế của Qt**.

Nhưng nó giúp bạn hiểu bản chất.

---

# 4. Tại sao GUI cần Event Loop?

Hãy tưởng tượng không có event loop.

User:

```text
Click button
```

Hệ điều hành tạo ra một sự kiện:

```text
Mouse Click
```

Nhưng ai xử lý?

```text
Mouse Click
      ↓
      ???
```

Event loop chính là thành phần liên tục nhận và phân phối những sự kiện này.

```text
OS
 │
 │ mouse click
 ▼
Qt
 │
 ▼
Event Queue
 │
 ▼
Event Loop
 │
 ▼
QPushButton
```

---

# 5. Event Queue

Các event không nhất thiết được xử lý ngay lập tức.

Chúng có thể đi qua một hàng đợi:

```text
Event Queue

┌─────────────────┐
│ MouseClick      │
├─────────────────┤
│ KeyPress        │
├─────────────────┤
│ Timer           │
├─────────────────┤
│ Paint           │
└─────────────────┘
```

Event loop lấy event ra:

```text
Queue
  │
  │ pop
  ▼
Event
  │
  ▼
Dispatch
```

Sau đó tiếp tục lấy event tiếp theo.

---

# 6. Event Dispatcher

Event loop không trực tiếp xử lý mọi thứ.

Nó cần một cơ chế phân phối event.

Khái niệm:

```text
Event Loop
    │
    ▼
Event Dispatcher
    │
    ├── Mouse event → Widget
    ├── Key event   → Widget
    ├── Timer       → QObject
    ├── Paint event → Widget
    └── Custom event → QObject
```

Trong Qt có hệ thống event dispatcher bên dưới để giao tiếp với hệ điều hành và điều phối event.

Bạn không thường xuyên phải gọi nó trực tiếp, nhưng hiểu nó giúp bạn hiểu kiến trúc Qt.

---

# 7. `QApplication`

Trong PySide6:

```python
from PySide6.QtWidgets import QApplication

app = QApplication()
```

`QApplication` quản lý những thứ cấp application của GUI.

Nó cung cấp infrastructure cho:

* event processing
* application lifetime
* GUI initialization
* widget management
* application-wide state

Đối với ứng dụng Widgets, thường sẽ có:

```text
QApplication
      │
      ▼
 Event System
      │
      ▼
  Main Window
      │
      ├── Button
      ├── Label
      └── Table
```

---

# 8. `app.exec()`

Đây là dòng cực kỳ quan trọng:

```python
app.exec()
```

Nó bắt đầu Qt event loop.

Ví dụ:

```python
from PySide6.QtWidgets import QApplication, QPushButton

app = QApplication()

button = QPushButton("Hello")
button.show()

app.exec()
```

Flow:

```text
QApplication()
      ↓
Create Widget
      ↓
show()
      ↓
app.exec()
      ↓
┌───────────────────────┐
│                       │
│      Event Loop       │
│                       │
│   waiting for event   │
│                       │
└───────────┬───────────┘
            │
            ▼
          User
            │
            ▼
        Click Button
            │
            ▼
       Qt processes
            │
            ▼
      Signal / Handler
```

---

# 9. Tại sao `app.exec()` không làm chương trình "đứng"?

Nếu bạn nhìn code:

```python
app.exec()
```

có vẻ chương trình bị block.

Đúng.

Nhưng nó **không phải block vô ích**.

Nó đang liên tục xử lý event:

```text
app.exec()
   │
   ├── mouse
   ├── keyboard
   ├── timer
   ├── paint
   ├── window
   └── custom event
```

Nói cách khác:

> GUI application "block" tại event loop để có thể tiếp tục phản ứng với thế giới bên ngoài.

---

# 10. Event Loop và `while True`

Ta có thể hình dung:

```python
while running:
    event = get_event()
    dispatch(event)
```

Nhưng đừng viết GUI kiểu:

```python
while True:
    ...
```

vì bạn có thể chiếm CPU và phá event processing.

Ví dụ tệ:

```python
while True:
    print("working...")
```

Nếu chạy trong GUI thread:

```text
GUI Thread
   │
   ▼
while True
   │
   └──► không quay lại Qt Event Loop
```

Kết quả:

```text
Window
  ↓
Frozen
  ↓
Not responding
```

---

# 11. Đây là khái niệm cực kỳ quan trọng

**GUI thread phải thường xuyên quay lại event loop.**

Ví dụ:

```text
Event Loop
    ↓
Handler
    ↓
Handler hoàn thành nhanh
    ↓
Event Loop
    ↓
Event tiếp theo
```

Nhưng nếu handler chạy quá lâu:

```text
Event Loop
    ↓
Handler
    ↓
████████████████████
████  10 seconds ███
████████████████████
    ↓
Event Loop
```

Trong 10 giây đó:

```text
Mouse ❌
Keyboard ❌
Paint ❌
Resize ❌
```

GUI có thể bị freeze.

---

# 12. Ví dụ kinh điển

```python
import time

def on_clicked():
    time.sleep(10)
```

Nếu:

```python
button.clicked.connect(on_clicked)
```

thì khi click:

```text
clicked
   ↓
on_clicked()
   ↓
sleep(10)
   ↓
GUI thread bị block
```

Trong lúc đó event loop không thể xử lý bình thường các event tiếp theo.

---

# 13. Đây là lý do chúng ta cần Worker

Sau này:

```text
GUI Thread
    │
    ├── Event Loop
    │
    └── UI
         
Worker Thread
    │
    └── Long Task
```

Ví dụ:

```text
Button
  │
  ▼
StartDownload
  │
  ▼
Worker
  │
  ├── progress
  ├── progress
  ├── progress
  └── finished
```

Worker không được tự ý thao tác UI.

Nó gửi event/signal về GUI thread:

```text
Worker
   │
   │ signal/event
   ▼
GUI Event Loop
   │
   ▼
Update UI
```

Đây sẽ là một phần rất quan trọng ở các buổi sau.

---

# 14. Event propagation

Qt event không phải lúc nào cũng đơn giản:

```text
Event → Widget
```

Có thể có quá trình propagation.

Ví dụ:

```text
Application
    │
    ▼
MainWindow
    │
    ▼
Panel
    │
    ▼
Button
```

Một mouse event có thể được Qt đưa đến object phù hợp.

Qt có hệ thống:

```text
QObject
   │
   ├── event()
   ├── eventFilter()
   └── event handling
```

---

# 15. `QObject.event()`

Một trong những API quan trọng:

```python
def event(self, event):
    ...
```

Ví dụ:

```python
from PySide6.QtCore import QObject


class MyObject(QObject):

    def event(self, event):
        print("Event received")
        return super().event(event)
```

`event()` là một điểm trung tâm trong Qt event system.

Conceptually:

```text
Qt Event
    ↓
QObject.event()
    ↓
specific event handler
```

---

# 16. Event handler chuyên biệt

Ví dụ với widget:

```python
def mousePressEvent(self, event):
    ...
```

Hoặc:

```python
def keyPressEvent(self, event):
    ...
```

Hoặc:

```python
def paintEvent(self, event):
    ...
```

Ta có:

```text
Event
 │
 ├── mouse → mousePressEvent()
 ├── key   → keyPressEvent()
 └── paint → paintEvent()
```

---

# 17. `event()` và `mousePressEvent()`

Đây là điểm nhiều người mới học Qt dễ nhầm.

`event()` là một entry point tổng quát:

```text
QObject.event()
```

Còn:

```python
mousePressEvent()
```

là handler chuyên biệt cho mouse press.

Có thể hình dung:

```text
                 event()
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
mousePressEvent  keyPressEvent  paintEvent
```

---

# 18. Event Filter

Qt còn có một cơ chế rất mạnh:

```python
eventFilter()
```

Một object có thể quan sát event của object khác.

Ví dụ:

```text
MainWindow
    │
    │ eventFilter
    ▼
Button
```

Ta có thể dùng nó để:

* logging
* global keyboard shortcut
* intercept mouse event
* custom behavior
* debugging

Ví dụ:

```python
class EventFilter(QObject):

    def eventFilter(self, watched, event):
        print(event.type())

        return False
```

`False` nghĩa là:

> Tôi không xử lý event này, hãy tiếp tục xử lý bình thường.

Nếu trả về:

```python
True
```

thì event đã được filter/consume.

---

# 19. Event Loop + Signal/Slot

Bây giờ kết nối với Buổi 1.

Ta có:

```text
User
 │
 │ click
 ▼
OS
 │
 ▼
Qt Event System
 │
 ▼
Event Loop
 │
 ▼
QPushButton
 │
 ▼
clicked Signal
 │
 ▼
Slot
```

Ví dụ:

```python
button.clicked.connect(on_clicked)
```

Ta đang nói với Qt:

> Khi `clicked` xảy ra, hãy gọi `on_clicked`.

---

# 20. Hai tầng Event-Driven

Đây là một kiến trúc rất quan trọng cần ghi nhớ.

### Tầng 1 — Framework

```text
OS
 ↓
Qt Event Loop
 ↓
Qt Event
 ↓
Signal / Slot
```

### Tầng 2 — Application

```text
UI
 ↓
Command
 ↓
Use Case
 ↓
Domain Event
 ↓
Event Bus
 ↓
Handler
```

Kết hợp:

```text
                    PySide6
                       │
                  Qt Event
                       │
                       ▼
                 Signal / Slot
                       │
                       ▼
                Application
                       │
                    Command
                       │
                       ▼
                   Use Case
                       │
                       ▼
                    Domain
                       │
                  Domain Event
                       │
                       ▼
                   Event Bus
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Handler   Handler   Handler
```

Đây chính là kiến trúc mà chúng ta sẽ xây.

---

# 21. Một sai lầm rất phổ biến

Không nên nghĩ:

> "PySide6 đã là Event-Driven Architecture rồi, vậy chỉ cần Signal/Slot là đủ."

Không phải.

Ví dụ:

```python
def on_save_clicked():
    repository.save(note)
    refresh_table()
    logger.info("saved")
    cache.clear()
```

Mặc dù nó dùng:

```python
button.clicked.connect(on_save_clicked)
```

nhưng architecture vẫn coupling.

Ta muốn:

```text
clicked
   ↓
SaveNoteCommand
   ↓
SaveNoteUseCase
   ↓
NoteSaved
   ↓
EventBus
   ├── RefreshTableHandler
   ├── LogHandler
   └── CacheHandler
```

Qt Event System và Application EDA là **hai cấp độ khác nhau**.

---

# 22. Event Loop và Clean Architecture

Sau này architecture của chúng ta sẽ giống:

```text
┌───────────────────────────────┐
│        Presentation           │
│                               │
│ PySide6                       │
│ Signal / Slot                 │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Application             │
│                               │
│ Commands                       │
│ Use Cases                      │
│ Application Events             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           Domain              │
│                               │
│ Entity                         │
│ Aggregate                      │
│ Domain Event                   │
└───────────────────────────────┘
```

Dependency:

```text
Presentation
      ↓
Application
      ↓
Domain
```

Nhưng:

```text
Domain
  ❌
  ↓
PySide6
```

Domain không nên biết Qt.

---

# 23. Một nguyên tắc quan trọng

Đừng đưa code nghiệp vụ vào Qt event handler.

Không nên:

```python
def on_save_clicked(self):
    # 300 dòng business logic
    ...
```

Nên:

```python
def on_save_clicked(self):
    command = SaveNoteCommand(...)
    self.save_note.execute(command)
```

Sau đó:

```text
Qt
 │
 │ Signal
 ▼
Presentation
 │
 │ Command
 ▼
Application
 │
 │ Use Case
 ▼
Domain
```

Đây là sự phân chia trách nhiệm rất quan trọng.

---

# 24. Mini Project cuối Buổi 2

Ta có thể xây một ứng dụng nhỏ:

```text
┌──────────────────────────────┐
│       Event Monitor          │
├──────────────────────────────┤
│                              │
│ Event: ButtonClicked         │
│ Event: TimerTick             │
│ Event: TextChanged           │
│                              │
├──────────────────────────────┤
│ [Click]   [Start]   [Stop]   │
└──────────────────────────────┘
```

Architecture:

```text
QPushButton
     │
     ▼
Qt Signal
     │
     ▼
Application Event
     │
     ▼
EventBus
     │
     ▼
Event Monitor
```

Ví dụ Event:

```python
@dataclass(frozen=True)
class ButtonClicked:
    button_name: str
```

Khi click:

```text
QPushButton.clicked
        ↓
ButtonClicked("save")
        ↓
EventBus.publish()
        ↓
EventMonitorHandler
```

Đây sẽ là bài tập chuẩn bị cho **Buổi 3 — Signal/Slot Deep Dive**.

---

# 25. Tổng kết Buổi 2

Bạn cần nắm chắc flow này:

```text
             OPERATING SYSTEM
                    │
                    ▼
              Qt Event System
                    │
                    ▼
                Event Queue
                    │
                    ▼
                Event Loop
                    │
                    ▼
             Event Dispatcher
                    │
                    ▼
                  QObject
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Event()           Signal/Slot
          │
          ▼
    Event Handler
```

Và phân biệt:

| Khái niệm         | Vai trò                         |
| ----------------- | ------------------------------- |
| Event             | Điều xảy ra                     |
| Event Queue       | Nơi chờ event                   |
| Event Loop        | Liên tục xử lý event            |
| Event Dispatcher  | Phân phối event                 |
| `QObject.event()` | Entry point xử lý event         |
| `eventFilter()`   | Quan sát/intercept event        |
| Signal            | Cơ chế notification của Qt      |
| Slot              | Hàm phản ứng với signal         |
| Event Bus         | Application-level event routing |

### Điều quan trọng nhất

Trong PySide6:

```text
app.exec()
```

chính là nơi Qt bước vào **event-driven world**.

Từ đó:

```text
User action
    ↓
Qt Event Loop
    ↓
Qt Event
    ↓
Signal/Slot
    ↓
Application logic
```

Ở **Buổi 3**, chúng ta sẽ mổ xẻ `Signal/Slot` rất sâu: `Signal`, `Slot`, `connect()`, `emit()`, kiểu dữ liệu của signal, nhiều receiver, connection lifetime, và đặc biệt **Direct Connection vs Queued Connection** — nền tảng để sau này hiểu `QThread` và worker architecture.
