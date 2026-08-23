# Buổi 3 — Signal / Slot Deep Dive

Ở Buổi 2, chúng ta đã đi qua:

```text
OS
 ↓
Qt Event System
 ↓
Event Queue
 ↓
Event Loop
 ↓
QObject
 ↓
Signal / Slot
```

Hôm nay tập trung vào **Signal/Slot** — cơ chế giao tiếp cốt lõi của Qt và cũng là cầu nối từ Qt Event System sang Event-Driven Architecture của ứng dụng.

Mục tiêu cuối buổi:

```text
QObject A
   │
   │ emit Signal
   ▼
Qt Meta-Object System
   │
   ▼
Slot B
```

và hiểu sâu hơn:

```text
Signal
  ↓
Connection
  ↓
Slot
```

---

# 1. Signal / Slot là gì?

Có thể hiểu đơn giản:

> **Signal = thông báo rằng một điều gì đó vừa xảy ra.**

> **Slot = hàm được gọi để phản ứng với thông báo đó.**

Ví dụ:

```text
Button
  │
  │ clicked
  ▼
Slot
```

Code:

```python
button.clicked.connect(on_clicked)
```

Khi người dùng click:

```text
clicked
   ↓
on_clicked()
```

---

# 2. Signal không phải function bình thường

Đây là điểm cần hiểu.

Bạn có:

```python
button.clicked
```

`clicked` không phải một function mà bạn tự gọi như:

```python
button.clicked()
```

Thay vào đó, nó là một **Qt Signal**.

Ta đăng ký receiver:

```python
button.clicked.connect(on_clicked)
```

và signal được phát bởi Qt khi sự kiện xảy ra.

---

# 3. Signal giống như Publisher

Có thể liên hệ với Buổi 1:

```text
Signal
   ↓
Event
   ↓
Consumer
```

Ví dụ:

```text
QPushButton
    │
    │ clicked
    ▼
Slot A
Slot B
Slot C
```

Một signal có thể có nhiều receiver.

Đây là điểm rất quan trọng.

---

# 4. Signal tự định nghĩa

Trong PySide6, ta có thể tạo Signal:

```python
from PySide6.QtCore import QObject, Signal


class Counter(QObject):

    value_changed = Signal(int)
```

Ở đây:

```python
Signal(int)
```

nghĩa là signal truyền một giá trị kiểu `int`.

Ta có:

```text
value_changed
       │
       └── int
```

---

# 5. Emit Signal

Để phát signal:

```python
self.value_changed.emit(10)
```

Đầy đủ:

```python
from PySide6.QtCore import QObject, Signal


class Counter(QObject):

    value_changed = Signal(int)

    def set_value(self, value):
        self.value_changed.emit(value)
```

---

# 6. Connect

Tạo receiver:

```python
def on_value_changed(value):
    print("Value:", value)
```

Kết nối:

```python
counter.value_changed.connect(
    on_value_changed
)
```

Flow:

```text
counter
   │
   │ emit(10)
   ▼
value_changed
   │
   ▼
on_value_changed(10)
```

---

# 7. Ví dụ hoàn chỉnh

```python
from PySide6.QtCore import QObject, Signal


class Counter(QObject):

    value_changed = Signal(int)

    def set_value(self, value):
        self.value_changed.emit(value)


def on_value_changed(value):
    print("New value:", value)


counter = Counter()

counter.value_changed.connect(
    on_value_changed
)

counter.set_value(10)
counter.set_value(20)
counter.set_value(30)
```

Kết quả:

```text
New value: 10
New value: 20
New value: 30
```

---

# 8. Signal có thể có nhiều tham số

Ví dụ:

```python
class UserService(QObject):

    user_created = Signal(int, str)
```

Emit:

```python
self.user_created.emit(
    10,
    "Alice"
)
```

Receiver:

```python
def on_user_created(user_id, username):
    print(user_id, username)
```

Kết nối:

```python
service.user_created.connect(
    on_user_created
)
```

Flow:

```text
UserService
    │
    │ emit(10, "Alice")
    ▼
user_created
    │
    ▼
on_user_created(10, "Alice")
```

---

# 9. Signal với `str`

```python
class SearchBox(QObject):

    text_changed = Signal(str)
```

Emit:

```python
self.text_changed.emit("python")
```

Receiver:

```python
def search(text):
    print("Search:", text)
```

---

# 10. Signal với object

Bạn có thể truyền object.

Ví dụ:

```python
class Note:
    def __init__(self, note_id, title):
        self.note_id = note_id
        self.title = title
```

Signal:

```python
class NoteService(QObject):

    note_created = Signal(object)
```

Emit:

```python
note = Note(1, "Hello")

self.note_created.emit(note)
```

Receiver:

```python
def on_note_created(note):
    print(note.title)
```

---

# 11. Tại sao dùng `Signal(object)`?

Vì `object` cho phép truyền Python object.

Ví dụ:

```python
Signal(object)
```

có thể truyền:

```text
Note
User
Order
DTO
Domain Event
```

Tuy nhiên, **đừng lạm dụng `object`**.

Nếu biết rõ type:

```python
Signal(int)
```

thường tốt hơn:

```python
Signal(object)
```

vì contract rõ ràng hơn.

---

# 12. Signal có nhiều Slot

Ví dụ:

```python
button.clicked.connect(
    save_note
)

button.clicked.connect(
    update_status
)

button.clicked.connect(
    write_log
)
```

Khi click:

```text
              clicked
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      save     status     log
```

Đây chính là một dạng **fan-out**.

---

# 13. Một Slot có nhiều Signal

Một function cũng có thể nhận từ nhiều signal.

```python
button1.clicked.connect(handle_action)
button2.clicked.connect(handle_action)
```

Khi đó:

```text
Button 1 ──┐
           ├──► handle_action()
Button 2 ──┘
```

Tuy nhiên, nếu cần phân biệt nguồn event, thường nên thiết kế rõ ràng hơn thay vì để handler quá thông minh.

---

# 14. `connect()` thực chất làm gì?

Khi viết:

```python
signal.connect(slot)
```

ta đang tạo một **connection**:

```text
Signal ─────────► Slot
```

Qt lưu thông tin connection này trong hệ thống meta-object.

Khi signal được emit:

```text
emit()
  ↓
Qt tìm connections
  ↓
gọi receivers
```

Đây là lý do signal/slot khác với việc bạn tự gọi function.

---

# 15. Signal không biết business logic

Đây là điểm rất quan trọng khi kết hợp với Clean Architecture.

Không nên:

```python
class NoteWidget:

    saved = Signal()

    def save(self):
        self.repository.save(...)
        self.database.commit()
        self.cache.clear()
```

Widget đang biết quá nhiều.

Thay vào đó:

```text
Widget
  │
  │ Signal
  ▼
Application
  │
  ▼
Use Case
  │
  ▼
Domain
```

---

# 16. Signal nên dùng ở đâu?

Một kiến trúc tốt:

```text
PySide6
   │
   ├── Signal
   ├── Slot
   └── Qt Event
        │
        ▼
Presentation Layer
        │
        ▼
Application Layer
```

Signal rất phù hợp cho:

* UI interaction
* UI state change
* worker progress
* worker completion
* worker error
* component communication

---

# 17. Signal không nên trở thành Event Bus toàn hệ thống

Ví dụ không nên biến mọi thứ thành:

```python
global_signal.note_created.emit(...)
global_signal.user_logged.emit(...)
global_signal.order_paid.emit(...)
```

rồi toàn bộ application phụ thuộc vào một object khổng lồ.

Đó sẽ trở thành:

```text
God Event Object
```

Thay vào đó:

```text
Qt Signal
     ↓
Application boundary
     ↓
Event Bus
     ↓
Domain/Application Events
```

Chúng ta sẽ xây cách này từ Buổi 4.

---

# 18. Signal vs Event

Hai khái niệm rất gần nhau nhưng không hoàn toàn giống.

### Qt Signal

Là cơ chế communication của Qt:

```python
value_changed = Signal(int)
```

### Application Event

Là concept trong kiến trúc:

```python
@dataclass(frozen=True)
class NoteCreated:
    note_id: int
```

Có thể kết hợp:

```text
Qt Signal
    ↓
Application Event
    ↓
Event Bus
```

Ví dụ:

```text
button.clicked
      ↓
CreateNoteCommand
      ↓
UseCase
      ↓
NoteCreated
      ↓
EventBus
```

---

# 19. Signal vs Callback

Callback:

```python
def do_work(callback):
    ...
    callback(result)
```

Caller:

```python
do_work(on_completed)
```

Signal:

```python
worker.completed.connect(
    on_completed
)
```

Điểm khác biệt lớn là Signal/Slot có **Qt meta-object system** phía sau và hỗ trợ các kiểu connection, thread communication, object lifetime.

---

# 20. Direct Connection

Đây là phần rất quan trọng.

Giả sử:

```text
Thread A
   │
   │ Signal
   ▼
Slot
```

Nếu connection được thực hiện theo kiểu **Direct Connection**, slot có thể được gọi trực tiếp trong context của thread đang emit signal.

Khái niệm:

```text
emit()
  │
  ▼
slot()
```

Không nhất thiết phải chờ event queue.

Điều này rất quan trọng khi làm multithreading.

---

# 21. Queued Connection

Với **Queued Connection**, signal được đưa vào event queue của receiver thread.

Conceptually:

```text
Thread A
   │
   │ emit()
   ▼
Event Queue của Thread B
   │
   ▼
Thread B Event Loop
   │
   ▼
Slot
```

Đây là một trong những cơ chế quan trọng giúp Qt giao tiếp giữa các thread.

---

# 22. Tại sao Queued Connection quan trọng?

Giả sử:

```text
Worker Thread
      │
      │ progress.emit(50)
      ▼
GUI Thread
      │
      ▼
update_progress_bar()
```

Ta muốn GUI update ở GUI thread.

Flow:

```text
Worker
   │
   │ Signal
   ▼
Qt Event Queue
   │
   ▼
GUI Event Loop
   │
   ▼
Slot
   │
   ▼
ProgressBar
```

Đây là architecture cực kỳ quan trọng khi chúng ta học `QThread`.

---

# 23. GUI thread và worker thread

Một quy tắc bạn cần nhớ:

> **Không tự ý cập nhật Qt Widget từ worker thread.**

Không nên:

```text
Worker Thread
     │
     ▼
label.setText(...)
```

Thay vào đó:

```text
Worker Thread
     │
     │ progress.emit(...)
     ▼
GUI Thread Event Queue
     │
     ▼
Slot
     │
     ▼
label.setValue(...)
```

Sau này chúng ta sẽ học rất sâu phần này.

---

# 24. Connection Type

Qt có các loại connection quan trọng:

```text
AutoConnection
DirectConnection
QueuedConnection
BlockingQueuedConnection
UniqueConnection
```

Trong thực tế:

### `AutoConnection`

Thường là lựa chọn mặc định.

Qt quyết định cách dispatch dựa trên thread affinity của sender/receiver.

### `DirectConnection`

Gọi slot trực tiếp.

### `QueuedConnection`

Đưa invocation vào event queue của receiver.

### `BlockingQueuedConnection`

Thread emit sẽ chờ receiver xử lý xong.

Cái này cần cực kỳ cẩn thận vì có thể gây deadlock.

### `UniqueConnection`

Ngăn duplicate connection trong một số trường hợp.

---

# 25. `AutoConnection`

Thông thường bạn chỉ viết:

```python
signal.connect(slot)
```

Qt dùng `AutoConnection`.

Trong single-thread:

```text
Signal
  ↓
Slot
```

Trong cross-thread scenario, Qt có thể sử dụng queued delivery phù hợp với thread affinity.

Điểm quan trọng:

> **Đừng mặc định nghĩ Signal luôn chạy slot ngay lập tức.**

Đặc biệt khi bắt đầu dùng threads.

---

# 26. Thread Affinity

Đây là khái niệm bạn sẽ gặp rất nhiều.

Mỗi `QObject` có một thread affinity.

Có thể hình dung:

```text
QObject
   │
   └── thuộc về Thread X
```

Khi queued signal được xử lý, Qt sử dụng event loop của thread phù hợp để invoke slot.

Đó là lý do worker architecture của Qt phụ thuộc rất nhiều vào:

```text
QObject
+
moveToThread()
+
Event Loop
+
Signal/Slot
```

---

# 27. Object Lifetime và Connection

Một ưu điểm lớn của Qt là hệ thống object ownership/lifetime giúp quản lý connection.

Ví dụ:

```python
button.clicked.connect(window.handle_click)
```

Nếu object receiver bị destroy đúng cách, Qt có thể tự quản lý connection liên quan.

Điều này khác với một số hệ thống callback thuần Python, nơi bạn phải tự quản lý lifecycle dễ gây:

* callback giữ object sống quá lâu
* memory leak
* callback gọi object đã không còn hợp lệ

---

# 28. `disconnect()`

Bạn có thể ngắt connection:

```python
button.clicked.disconnect(
    on_clicked
)
```

Hoặc với signal tự định nghĩa:

```python
counter.value_changed.disconnect(
    on_value_changed
)
```

Flow:

```text
Before:

Signal ─────► Slot


After disconnect:

Signal       Slot
```

---

# 29. Duplicate Connection

Một lỗi phổ biến:

```python
def setup(self):
    self.button.clicked.connect(
        self.on_clicked
    )
```

Nếu `setup()` được gọi 3 lần:

```text
clicked
  │
  ├──► on_clicked
  ├──► on_clicked
  └──► on_clicked
```

Một click có thể gọi handler nhiều lần.

Vì vậy cần thiết kế lifecycle cẩn thận.

---

# 30. Signal/Slot và SOLID

Đây là chỗ kết nối với những gì bạn đã học.

Ví dụ:

```text
Button
  ↓
Signal
  ↓
SaveNoteCommand
  ↓
UseCase
```

Button không biết:

```text
Database
Repository
Domain
```

=> giảm coupling.

Một handler:

```python
def on_note_created(event):
    ...
```

chỉ chịu trách nhiệm phản ứng:

=> **SRP**

Thêm handler:

```text
NoteCreated
 ├── UI
 ├── Log
 ├── Cache
 └── Analytics
```

không sửa producer:

=> **OCP**

Đây chính là lý do Signal/Event rất phù hợp với kiến trúc SOLID.

---

# 31. Mini Project

Ta xây một `CounterWidget`.

UI:

```text
┌───────────────────────┐
│                       │
│         10            │
│                       │
│   [-]         [+]     │
│                       │
└───────────────────────┘
```

Architecture ban đầu:

```text
+ button
   ↓
clicked
   ↓
increment()
   ↓
value_changed
   ↓
Label
```

Code:

```python
from PySide6.QtCore import QObject, Signal


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
```

Widget:

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)


class CounterWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.counter = Counter()

        self.label = QLabel("0")

        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("-")

        buttons = QHBoxLayout()
        buttons.addWidget(self.minus_button)
        buttons.addWidget(self.plus_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addLayout(buttons)

        self.plus_button.clicked.connect(
            self.counter.increment
        )

        self.minus_button.clicked.connect(
            self.counter.decrement
        )

        self.counter.value_changed.connect(
            self.on_value_changed
        )

    def on_value_changed(self, value):
        self.label.setText(str(value))
```

Flow:

```text
          + Button
              │
           clicked
              │
              ▼
      counter.increment()
              │
              ▼
      value_changed.emit()
              │
              ▼
      on_value_changed()
              │
              ▼
            QLabel
```

---

# 32. Nhưng architecture này vẫn chưa phải EDA hoàn chỉnh

Hiện tại:

```text
Counter
   │
   ▼
value_changed
   │
   ▼
UI
```

Đây là **reactive communication**, nhưng chưa phải architecture mà chúng ta đang hướng tới.

Sau này sẽ là:

```text
Button
   │
   │ clicked
   ▼
IncrementCounterCommand
   │
   ▼
UseCase
   │
   ▼
Counter
   │
   │ CounterIncremented
   ▼
EventBus
   │
   ├──► UpdateUIHandler
   ├──► LogHandler
   └──► AnalyticsHandler
```

Đó mới là nơi **Qt Signal/Slot + EDA + Clean Architecture + DDD** hội tụ.

---

# 33. Bài tập Buổi 3

## Bài 1 — Signal cơ bản

Tạo:

```python
class Temperature(QObject):
    temperature_changed = Signal(float)
```

Có:

```python
set_temperature(temperature)
```

Khi gọi:

```python
temperature.set_temperature(35.5)
```

signal phải emit:

```text
35.5
```

---

## Bài 2 — Multiple Slots

Một signal:

```text
temperature_changed
```

có 3 slot:

```text
DisplayHandler
LogHandler
WarningHandler
```

Flow:

```text
temperature_changed
       │
       ├──► display
       ├──► log
       └──► warning
```

---

## Bài 3 — Counter

Xây `CounterWidget` như ví dụ trên nhưng thêm:

```text
Reset
```

Flow:

```text
Reset
  ↓
counter.reset()
  ↓
value_changed
  ↓
UI
```

---

## Bài 4 — Tư duy kiến trúc

Hãy trả lời câu hỏi:

> Nếu `Counter` bắt đầu phải ghi log, cập nhật database và gửi notification mỗi khi value thay đổi, bạn sẽ sửa `Counter` như thế nào?

Mục tiêu của câu hỏi là nhận ra vấn đề:

```text
Counter
 ├── UI
 ├── Logger
 ├── Database
 └── Notification
```

và chuẩn bị chuyển sang:

```text
Counter
   │
   ▼
CounterChanged
   │
   ▼
EventBus
   ├── UI Handler
   ├── Log Handler
   ├── Database Handler
   └── Notification Handler
```

---

# 34. Tóm tắt Buổi 3

Bạn cần nắm chắc:

```text
Signal
  ↓
emit()
  ↓
Connection
  ↓
Slot
```

Và:

```text
One Signal
    ↓
Many Slots
```

cũng như:

```text
Worker Thread
    │
    │ Signal
    ▼
GUI Event Queue
    │
    ▼
GUI Event Loop
    │
    ▼
GUI Slot
```

Đặc biệt ghi nhớ:

> **Signal/Slot là cơ chế communication của Qt; Event Bus là cơ chế communication ở application architecture.**

Ở **Buổi 4**, chúng ta sẽ bắt đầu xây **Event Bus thật sự bằng Python**, nhưng lần này sẽ thiết kế có `Event`, `Handler`, `subscribe()`, `unsubscribe()`, `publish()`, nhiều handler và type-safe bằng `Protocol`/`TypeVar`. Sau đó ta sẽ nối Event Bus đó vào PySide6.
