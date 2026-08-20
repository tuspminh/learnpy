# Buổi 4 — Event System trong PySide6

Ở 3 buổi trước, ta đã xây được nền móng:

```text
Buổi 1
QApplication
Event Loop
Widget

Buổi 2
QObject
Parent / Child
Object Tree

Buổi 3
Signal / Slot
```

Hôm nay ta học **Event System**.

Đây là phần rất quan trọng vì phải phân biệt rõ:

```text
Event
Signal
Slot
Callback
```

Chúng **không phải cùng một thứ**.

---

# 1. Event là gì?

Event là một đối tượng mô tả:

> **Một điều gì đó đã xảy ra đối với một QObject.**

Ví dụ người dùng:

* click chuột
* di chuyển chuột
* nhấn phím
* thả phím
* đóng cửa sổ
* resize cửa sổ
* focus vào widget

Qt biểu diễn những hành động đó bằng các event.

Mental model:

```text
User
 │
 ├── Click
 ├── Key press
 ├── Mouse move
 └── Close window
       │
       ▼
     Qt
       │
       ▼
    QEvent
       │
       ▼
    QObject
```

---

# 2. Event khác Signal như thế nào?

Đây là câu hỏi quan trọng nhất của buổi học.

Ví dụ:

```text
User click QPushButton
```

Có thể hình dung:

```text
Operating System
       │
       ▼
Mouse Event
       │
       ▼
QPushButton
       │
       ├── xử lý event
       │
       └── phát clicked signal
                 │
                 ▼
               Slot
```

Vậy:

### Event

Là **thông tin Qt gửi tới object**.

### Signal

Là **thông báo mà object phát ra cho các object/function khác**.

---

# 3. `QEvent`

Class cơ sở:

```python
from PySide6.QtCore import QEvent
```

`QEvent` là base class cho nhiều loại event.

Ví dụ:

```text
QEvent
 │
 ├── QMouseEvent
 ├── QKeyEvent
 ├── QCloseEvent
 ├── QResizeEvent
 ├── QFocusEvent
 └── ...
```

Có thể hình dung:

```text
QEvent
   │
   ├── Mouse
   ├── Keyboard
   ├── Window
   ├── Focus
   ├── Paint
   └── Timer
```

---

# 4. Event Loop nhận Event

Nhớ Buổi 1:

```python
app.exec()
```

khởi động event loop.

Event loop liên tục chờ:

```text
┌────────────────────────────┐
│         Event Loop          │
│                            │
│   wait for event            │
│          ↓                  │
│   receive event             │
│          ↓                  │
│   dispatch event            │
│          ↓                  │
│   wait again                │
└────────────────────────────┘
```

Ví dụ user click:

```text
Mouse click
     ↓
OS
     ↓
Qt Event Loop
     ↓
QPushButton
     ↓
QMouseEvent
```

---

# 5. `event()`

`QObject` có method:

```python
event(self, event)
```

Ta có thể override nó.

Ví dụ:

```python
import sys

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QWidget


class Window(QWidget):

    def event(self, event):
        print("Event:", event.type())

        return super().event(event)


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())
```

Khi tương tác với cửa sổ, bạn sẽ thấy rất nhiều event được in ra.

---

# 6. Tại sao phải gọi `super().event(event)`?

Đây là điểm cực kỳ quan trọng.

Khi override:

```python
def event(self, event):
```

ta đang can thiệp vào event processing.

Nếu viết:

```python
def event(self, event):
    print(event.type())
```

thì ta đã không cho class cha xử lý event theo cách thông thường.

Thông thường nên:

```python
def event(self, event):
    print(event.type())

    return super().event(event)
```

Mental model:

```text
MyWindow.event()
       │
       ▼
super().event()
       │
       ▼
Qt xử lý mặc định
```

---

# 7. Event type

Ta có:

```python
event.type()
```

Ví dụ:

```python
if event.type() == QEvent.Type.MouseButtonPress:
    ...
```

Có rất nhiều loại:

```text
MouseButtonPress
MouseButtonRelease
MouseMove
KeyPress
KeyRelease
Resize
Close
Paint
FocusIn
FocusOut
Timer
...
```

---

# 8. Mouse Event

Mouse event thường dùng:

```python
from PySide6.QtGui import QMouseEvent
```

Nhưng trong method override, ta thường nhận event:

```python
def mousePressEvent(self, event):
    ...
```

Ví dụ:

```python
from PySide6.QtWidgets import QWidget


class Window(QWidget):

    def mousePressEvent(self, event):
        print("Mouse pressed")
```

Khi click vào window:

```text
Mouse click
    ↓
QMouseEvent
    ↓
mousePressEvent()
```

---

# 9. `mousePressEvent()`

Đây là cách phổ biến hơn việc tự kiểm tra:

```python
event.type()
```

Ví dụ:

```python
class Window(QWidget):

    def mousePressEvent(self, event):
        print("Mouse pressed")
```

Qt sẽ tự gọi method này khi có mouse press.

---

# 10. Mouse Button

Ta có thể kiểm tra nút chuột:

```python
from PySide6.QtCore import Qt
```

Ví dụ:

```python
class Window(QWidget):

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            print("Left click")

        elif event.button() == Qt.MouseButton.RightButton:
            print("Right click")
```

Sơ đồ:

```text
QMouseEvent
    │
    ├── button()
    ├── position()
    ├── globalPosition()
    └── ...
```

---

# 11. Mouse Position

Ví dụ:

```python
class Window(QWidget):

    def mousePressEvent(self, event):

        position = event.position()

        print(position.x())
        print(position.y())
```

Nếu click tại:

```text
x = 100
y = 50
```

thì ta có:

```text
(100, 50)
```

---

# 12. Mouse Move

Có:

```python
def mouseMoveEvent(self, event):
    ...
```

Nhưng mặc định widget có thể không nhận mouse move nếu không có button pressed.

Có thể bật:

```python
self.setMouseTracking(True)
```

Ví dụ:

```python
class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        print(event.position())
```

Bây giờ di chuyển chuột trên widget sẽ tạo mouse move events.

---

# 13. Mouse Release

Có:

```python
def mouseReleaseEvent(self, event):
    print("Mouse released")
```

Chuỗi:

```text
Mouse Press
     ↓
mousePressEvent()

Mouse Move
     ↓
mouseMoveEvent()

Mouse Release
     ↓
mouseReleaseEvent()
```

---

# 14. Double Click

Có:

```python
def mouseDoubleClickEvent(self, event):
    print("Double click")
```

---

# 15. Keyboard Event

Keyboard event:

```python
def keyPressEvent(self, event):
    ...
```

Ví dụ:

```python
from PySide6.QtCore import Qt


class Window(QWidget):

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_A:
            print("A pressed")
```

---

# 16. Lấy phím

Ví dụ:

```python
key = event.key()
```

Ta có:

```python
if key == Qt.Key.Key_Escape:
    print("Escape")
```

Hoặc:

```python
if key == Qt.Key.Key_Return:
    print("Enter")
```

Một số phím thường dùng:

```text
Key_A
Key_B
Key_C

Key_Return
Key_Enter
Key_Escape
Key_Space
Key_Tab
Key_Backspace
Key_Delete

Key_Left
Key_Right
Key_Up
Key_Down
```

---

# 17. Keyboard Modifier

Ta có thể kiểm tra Ctrl, Shift, Alt...

Ví dụ:

```python
modifiers = event.modifiers()
```

Kiểm tra Ctrl:

```python
if modifiers & Qt.KeyboardModifier.ControlModifier:
    print("Ctrl is pressed")
```

Ví dụ:

```python
if (
    event.key() == Qt.Key.Key_S
    and event.modifiers()
    & Qt.KeyboardModifier.ControlModifier
):
    print("Ctrl + S")
```

Đây là nền tảng để xây shortcut.

---

# 18. `keyPressEvent()` và Focus

Một điểm rất quan trọng:

Không phải widget nào cũng nhận keyboard event.

Keyboard event thường được gửi đến widget đang có:

```text
focus
```

Ví dụ:

```text
QLineEdit
   ↑
 Focus
   ↑
Keyboard event
```

Nếu click vào `QLineEdit`, nó thường nhận keyboard event.

---

# 19. `setFocus()`

Ta có thể yêu cầu widget nhận focus:

```python
line_edit.setFocus()
```

Hoặc:

```python
button.setFocus()
```

Focus là một khái niệm cực kỳ quan trọng trong GUI.

---

# 20. Close Event

Khi cửa sổ đóng:

```python
def closeEvent(self, event):
    print("Window closing")

    super().closeEvent(event)
```

Ví dụ:

```python
class Window(QWidget):

    def closeEvent(self, event):
        print("Closing...")
        event.accept()
```

---

# 21. `accept()` và `ignore()`

Đây là một concept rất hay.

Khi nhận close event:

```python
event.accept()
```

nghĩa là:

> Tôi đồng ý cho event được xử lý.

Còn:

```python
event.ignore()
```

nghĩa là:

> Không chấp nhận event này.

Ví dụ hỏi người dùng trước khi thoát:

```python
from PySide6.QtWidgets import QMessageBox


class Window(QWidget):

    def closeEvent(self, event):

        result = QMessageBox.question(
            self,
            "Confirm",
            "Do you want to quit?",
        )

        if result == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
```

Sơ đồ:

```text
User closes window
       ↓
closeEvent()
       ↓
Confirm?
   ┌───┴───┐
  Yes      No
   ↓        ↓
accept    ignore
   ↓        ↓
 Close    Stay
```

Đây là một ứng dụng thực tế của Event System.

---

# 22. Event Propagation

Đây là phần khó hơn một chút.

Event có thể được truyền qua hệ thống widget.

Ví dụ:

```text
Parent
  │
  └── Child
```

Một event xảy ra trên child.

Qt có cơ chế xử lý event và propagation tùy loại event.

Điểm quan trọng:

> Widget có thể xử lý event hoặc để event tiếp tục được xử lý bởi hệ thống/parent theo quy tắc của Qt.

---

# 23. `accept()` vs `ignore()`

Đừng nghĩ:

```text
accept = event thành công
ignore = event thất bại
```

Mental model tốt hơn:

```text
accept()
    ↓
"Tôi đã xử lý / chấp nhận event"

ignore()
    ↓
"Tôi không xử lý event này"
```

Với một số event, `ignore()` có thể cho phép event tiếp tục propagation.

---

# 24. `event()` vs `mousePressEvent()`

Có hai cách.

### Cách tổng quát:

```python
def event(self, event):
    ...
```

Bạn phải kiểm tra:

```python
event.type()
```

### Cách chuyên biệt:

```python
def mousePressEvent(self, event):
    ...
```

Đây thường là cách dễ đọc hơn.

Ví dụ:

```python
class Window(QWidget):

    def mousePressEvent(self, event):
        print("Mouse!")
```

thay vì:

```python
class Window(QWidget):

    def event(self, event):

        if event.type() == QEvent.Type.MouseButtonPress:
            print("Mouse!")

        return super().event(event)
```

---

# 25. Khi nào dùng `event()`?

`event()` hữu ích khi bạn muốn xử lý nhiều loại event tại một điểm.

Ví dụ:

```python
def event(self, event):

    if event.type() == QEvent.Type.MouseButtonPress:
        ...

    elif event.type() == QEvent.Type.KeyPress:
        ...

    return super().event(event)
```

Nhưng nếu chỉ xử lý mouse:

```python
def mousePressEvent(self, event):
    ...
```

sẽ rõ ràng hơn.

---

# 26. Event Filter

Đây là một trong những tính năng rất mạnh của Qt.

Qt cho phép một QObject **theo dõi event của QObject khác**.

Ví dụ:

```text
Window
   │
   └── LineEdit
```

Ta muốn `Window` quan sát event của `LineEdit`.

Có thể dùng:

```python
installEventFilter()
```

---

# 27. `installEventFilter()`

Ví dụ:

```python
line_edit.installEventFilter(self)
```

Nghĩa là:

> `self` sẽ được phép quan sát event của `line_edit`.

Sau đó implement:

```python
def eventFilter(self, watched, event):
    ...
```

---

# 28. Ví dụ Event Filter

```python
import sys

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QWidget,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.line_edit = QLineEdit(self)

        self.line_edit.installEventFilter(self)

    def eventFilter(self, watched, event):

        if (
            watched is self.line_edit
            and event.type() == QEvent.Type.KeyPress
        ):
            print("Key pressed in line edit")

        return super().eventFilter(watched, event)


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())
```

Sơ đồ:

```text
Keyboard
   ↓
QLineEdit
   ↓
Event Filter
   ↓
Window.eventFilter()
   ↓
QLineEdit tiếp tục xử lý
```

---

# 29. Event Filter rất mạnh

Nó cho phép một object quan sát object khác mà không cần subclass object đó.

Ví dụ:

```text
MainWindow
    │
    ├── SearchBox
    ├── Table
    ├── Tree
    └── Button
```

Ta có thể cài event filter cho:

```text
SearchBox
Table
Tree
```

và xử lý event tập trung.

---

# 30. Event Filter có thể chặn event

Đây là điểm quan trọng.

`eventFilter()` trả về:

```python
True
```

thì event đã được xử lý/chặn.

Ví dụ:

```python
def eventFilter(self, watched, event):

    if event.type() == QEvent.Type.KeyPress:
        print("Blocked")

        return True

    return super().eventFilter(watched, event)
```

Khi đó event sẽ không tiếp tục xử lý theo cách bình thường.

Ngược lại:

```python
return False
```

hoặc gọi:

```python
return super().eventFilter(watched, event)
```

thì event có thể tiếp tục.

---

# 31. Event Filter vs Signal

Đây là chỗ người mới rất dễ nhầm.

Giả sử `QLineEdit`.

Ta có:

```python
line_edit.textChanged.connect(...)
```

Đây là:

```text
Signal
```

Còn:

```python
line_edit.installEventFilter(...)
```

là:

```text
Event System
```

Khác nhau:

```text
Signal
   ↓
"Điều gì đó đã xảy ra"

Event Filter
   ↓
"Cho tôi quan sát / can thiệp event"
```

---

# 32. Ví dụ thực tế: Shortcut toàn cửa sổ

Giả sử muốn:

```text
Ctrl + S
```

dù user đang focus vào widget nào.

Có thể dùng nhiều cách, trong đó một cách là event filter.

```text
MainWindow
│
├── SearchBox
├── Table
├── Editor
└── Button
```

Event filter có thể quan sát keyboard events và phát hiện:

```text
Ctrl + S
```

Sau đó gọi:

```python
save()
```

Tuy nhiên với shortcut thực sự, Qt còn có `QShortcut`/`QAction`, mà chúng ta sẽ học sau.

---

# 33. Event và Signal trong một Button

Đây là ví dụ cực kỳ quan trọng.

Khi click button:

```text
User
 ↓
Mouse event
 ↓
QPushButton
 ↓
internal event handling
 ↓
clicked signal
 ↓
your slot
```

Cho nên:

```python
button.clicked.connect(...)
```

không phải là "bắt mouse click trực tiếp".

Bạn đang lắng nghe **signal cấp cao** do button phát ra.

---

# 34. Hai tầng abstraction

Đây là một mental model rất tốt:

### Tầng thấp

```text
QMouseEvent
QKeyEvent
QResizeEvent
QCloseEvent
```

### Tầng cao

```text
clicked
pressed
released
textChanged
currentChanged
valueChanged
```

Tức là:

```text
Low-level Event
       ↓
Widget xử lý
       ↓
High-level Signal
       ↓
Application logic
```

Thông thường business logic nên làm việc ở tầng Signal/Slot càng nhiều càng tốt.

---

# 35. Ví dụ kiến trúc tốt

Không nên:

```python
def mousePressEvent(self, event):
    if ...:
        save_database()
        update_ui()
        send_request()
```

Nếu đây là click button, tốt hơn để button phát:

```python
clicked
```

rồi:

```python
button.clicked.connect(self.handle_save)
```

Sau đó:

```python
def handle_save(self):
    ...
```

Event thấp hơn chỉ cần dùng khi bạn thật sự cần custom interaction.

---

# 36. Khi nào nên override Event?

Dùng khi cần:

### Custom mouse behavior

```python
mousePressEvent()
mouseMoveEvent()
mouseReleaseEvent()
```

### Custom keyboard behavior

```python
keyPressEvent()
keyReleaseEvent()
```

### Window lifecycle

```python
closeEvent()
```

### Custom rendering

```python
paintEvent()
```

### Resize behavior

```python
resizeEvent()
```

### Focus behavior

```python
focusInEvent()
focusOutEvent()
```

---

# 37. Bài tập 1 — Mouse Tracker

Tạo window:

```text
┌──────────────────────────┐
│                          │
│       Mouse Position     │
│                          │
│       X: 120             │
│       Y: 80              │
│                          │
└──────────────────────────┘
```

Khi di chuyển chuột:

```text
X: ...
Y: ...
```

phải thay đổi.

Gợi ý:

```python
self.setMouseTracking(True)
```

và:

```python
mouseMoveEvent()
```

---

# 38. Bài tập 2 — Keyboard Monitor

Tạo app hiển thị:

```text
Last key:
Ctrl + S
```

Khi user nhấn:

```text
A
B
Escape
Ctrl + S
Shift + A
```

UI phải hiển thị phím tương ứng.

Bạn cần nghiên cứu:

```python
event.key()
event.modifiers()
```

---

# 39. Bài tập 3 — Confirm Close

Tạo cửa sổ.

Khi user đóng:

```text
┌───────────────────────────┐
│ Do you want to quit?      │
│                           │
│      Yes       No         │
└───────────────────────────┘
```

Nếu Yes:

```python
event.accept()
```

Nếu No:

```python
event.ignore()
```

---

# 40. Bài tập 4 — Event Filter

Tạo:

```text
Window
│
├── QLineEdit
└── QLabel
```

Cài event filter cho `QLineEdit`.

Mỗi lần user nhấn phím trong `QLineEdit`, QLabel hiển thị:

```text
Last event: KeyPress
```

Không được subclass `QLineEdit`.

Mục tiêu là hiểu:

```python
installEventFilter()
```

---

# 41. Bài tập 5 — Phân biệt Event và Signal

Viết app có:

```text
QPushButton
```

và giải thích đường đi:

```text
Mouse click
    ↓
?
    ↓
?
    ↓
?
```

Bạn phải điền:

```text
QMouseEvent
clicked
slot
```

theo đúng thứ tự.

---

# 42. Tổng kết 4 buổi

Đến đây bạn đã có core architecture:

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
                     QObject
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
           Event Handler        Signal
               │                   │
               ▼                   ▼
        xử lý event              Slot
```

Và:

```text
QObject
│
├── Parent / Child
├── Event
├── Signal
└── Lifetime
```

---

# 43. Điều tôi muốn bạn đặc biệt nhớ

Có 4 khái niệm:

| Khái niệm         | Ý nghĩa                                        |
| ----------------- | ---------------------------------------------- |
| **Event**         | Qt gửi thông tin về một sự kiện đến object     |
| **Event Handler** | Method xử lý event                             |
| **Signal**        | Object thông báo rằng một điều gì đó đã xảy ra |
| **Slot**          | Callable nhận signal                           |

Ví dụ:

```text
User click
    ↓
QMouseEvent          ← Event
    ↓
QPushButton
    ↓
clicked              ← Signal
    ↓
on_click()           ← Slot
```

Nếu bạn nắm chắc sơ đồ này, bạn đã bắt đầu **thực sự hiểu Qt**, chứ không chỉ biết kéo widget lên cửa sổ.

---

## Buổi 5

Tiếp theo chúng ta sẽ học **Layout System Deep Dive**:

```text
QVBoxLayout
QHBoxLayout
QGridLayout
QFormLayout
stretch
spacing
margin
sizeHint()
minimumSizeHint()
sizePolicy()
QSizePolicy
```

Đặc biệt sẽ giải quyết một vấn đề người mới học PySide6 thường gặp:

> **"Tại sao widget của tôi cứ tự co giãn, tại sao `setFixedSize()` làm UI xấu, và làm thế nào để thiết kế layout giống một ứng dụng desktop chuyên nghiệp?"**
