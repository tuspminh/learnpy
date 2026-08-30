# Phần III — UI Architecture

# Buổi 34 — Signal-based Architecture

Ở **Buổi 33**, chúng ta học `Event Bus`.

Hôm nay đi sâu vào một thứ **rất quan trọng trong PySide6 architecture**:

> **Không chỉ dùng Signal để xử lý `button.clicked`; chúng ta có thể dùng Signal như một cơ chế giao tiếp giữa các layer của application.**

Mục tiêu cuối buổi:

```text
View
 │
 │ Signal
 ▼
ViewModel / Controller
 │
 │ Signal
 ▼
View
```

và:

```text
Worker
   │
   │ Signal
   ▼
Application
   │
   │ Signal
   ▼
UI
```

---

# 1. Signal-based Architecture là gì?

Trong PySide6, Signal thường được nhìn thấy như:

```python
button.clicked.connect(...)
```

Nhưng Signal thực chất có thể trở thành **communication mechanism** của toàn bộ application.

Ví dụ:

```text
┌──────────────┐
│     View     │
└──────┬───────┘
       │ signal
       ▼
┌──────────────┐
│  Controller  │
└──────┬───────┘
       │ signal
       ▼
┌──────────────┐
│     View     │
└──────────────┘
```

Các object không nhất thiết phải gọi trực tiếp method của nhau.

---

# 2. Vì sao cần Signal Architecture?

Hãy nhìn code này:

```python
class MainWindow:

    def __init__(self, controller):
        self.controller = controller

    def on_save_clicked(self):
        self.controller.save()
```

Không sai.

Nhưng MainWindow biết:

```text
MainWindow
    ↓
Controller
```

Nếu application lớn:

```text
MainWindow
    ↓
Controller
    ↓
Service
    ↓
Repository
```

UI bắt đầu biết rất nhiều về application.

Signal cho phép giảm coupling.

---

# 3. Signal cơ bản

```python
from PySide6.QtCore import QObject, Signal


class Worker(QObject):

    finished = Signal()

    def run(self):
        print("Working...")
        self.finished.emit()
```

Consumer:

```python
worker.finished.connect(
    on_finished
)
```

Flow:

```text
worker.run()
    │
    ▼
finished.emit()
    │
    ▼
on_finished()
```

---

# 4. Signal có dữ liệu

Ví dụ:

```python
progress_changed = Signal(int)
```

Emit:

```python
self.progress_changed.emit(50)
```

Connect:

```python
worker.progress_changed.connect(
    progress_bar.setValue
)
```

Flow:

```text
Worker
  │
  │ emit(50)
  ▼
Signal
  │
  ▼
QProgressBar.setValue(50)
```

---

# 5. Signal nhiều argument

Có thể:

```python
progress_changed = Signal(int, int)
```

Ví dụ:

```python
self.progress_changed.emit(
    current,
    total,
)
```

Handler:

```python
def on_progress(current, total):
    ...
```

---

# 6. Signal truyền object

Có thể:

```python
event = Signal(object)
```

Ví dụ:

```python
event.emit(
    CrawlProgress(...)
)
```

Nhưng không nên lạm dụng:

```python
Signal(object)
```

nếu chúng ta biết rõ type.

Tốt hơn:

```python
Signal(int)
Signal(str)
Signal(bool)
Signal(dict)
```

hoặc QObject/domain-compatible type khi phù hợp.

---

# 7. Signal phải khai báo trên class

Một lỗi phổ biến:

```python
class Worker:

    def run(self):
        self.finished = Signal()
```

Không nên.

Signal nên được khai báo:

```python
class Worker(QObject):

    finished = Signal()
```

và class phải kế thừa `QObject`.

---

# 8. Signal là descriptor của Qt

Đây là một mental model quan trọng.

Khi viết:

```python
class Worker(QObject):
    finished = Signal()
```

`finished` chưa phải là một Signal instance bình thường như:

```python
finished = object()
```

Nó là declaration để Qt xây dựng hệ thống signal/slot cho QObject.

Khi instance được tạo:

```python
worker = Worker()
```

Qt cung cấp bound signal:

```python
worker.finished
```

để:

```python
worker.finished.connect(...)
worker.finished.emit()
```

---

# 9. Signal vs Python callback

Python thuần:

```python
class Worker:

    def __init__(self, callback):
        self.callback = callback

    def run(self):
        self.callback()
```

Đây là callback.

PySide6:

```python
class Worker(QObject):

    finished = Signal()

    def run(self):
        self.finished.emit()
```

Khác biệt lớn:

```text
Callback
    Worker biết callback

Signal
    Worker chỉ phát signal
```

---

# 10. Dependency Direction

Callback:

```text
Worker
  │
  ▼
callback
```

Signal:

```text
Worker
  │
  ▼
Signal
  │
  ├── A
  ├── B
  └── C
```

Worker không cần biết A, B, C là ai.

Đây là loose coupling.

---

# 11. Signal một chiều

Signal rất phù hợp với communication:

```text
Producer
   │
   ▼
Signal
   │
   ▼
Consumer
```

Ví dụ:

```text
Worker
  ↓
progress_changed
  ↓
ProgressBar
```

Không nên biến Signal thành một mạng lưới khó kiểm soát:

```text
A ↔ B ↔ C ↔ D ↔ E ↔ A
```

Đó là dấu hiệu architecture đang trở nên rối.

---

# 12. Signal Architecture cho ViewModel

Đây là phần quan trọng nhất hôm nay.

Ta có:

```text
View
   ↓
ViewModel
   ↓
Service
```

ViewModel có thể expose signals:

```python
class StoryViewModel(QObject):

    title_changed = Signal(str)
    loading_changed = Signal(bool)
    error_occurred = Signal(str)
```

View chỉ cần subscribe.

---

# 13. Ví dụ ViewModel

```python
from PySide6.QtCore import QObject, Signal


class StoryViewModel(QObject):

    title_changed = Signal(str)
    loading_changed = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

        self._title = ""

    @property
    def title(self):
        return self._title

    def set_title(self, title):
        if title == self._title:
            return

        self._title = title

        self.title_changed.emit(
            title
        )
```

View:

```python
view_model.title_changed.connect(
    label.setText
)
```

---

# 14. Tại sao không để View gọi trực tiếp `label.setText()`?

ViewModel không nên biết:

```python
QLabel
QPushButton
QLineEdit
```

Nó chỉ biết:

```text
title_changed
loading_changed
error_occurred
```

Do đó:

```text
ViewModel
    │
    │ Signal
    ▼
View
```

View quyết định hiển thị thế nào.

---

# 15. ViewModel không nên import QWidget

Đây là nguyên tắc quan trọng:

Không:

```python
class StoryViewModel(QObject):

    def __init__(self, label):
        self.label = label
```

và:

```python
self.label.setText(...)
```

ViewModel trở thành UI-dependent.

Nên:

```python
class StoryViewModel(QObject):

    title_changed = Signal(str)
```

---

# 16. State + Signal

Kết hợp Buổi 32:

```text
Application State
       │
       ├── data
       │
       └── signals
```

Ví dụ:

```python
class AppState(QObject):

    story_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self._story_id = None

    @property
    def story_id(self):
        return self._story_id

    def select_story(self, story_id):

        if story_id == self._story_id:
            return

        self._story_id = story_id

        self.story_changed.emit(
            story_id
        )
```

---

# 17. View subscribe State

```python
state.story_changed.connect(
    reader.on_story_changed
)
```

Flow:

```text
Controller
    │
    ▼
state.select_story(10)
    │
    ▼
story_changed.emit(10)
    │
    ▼
Reader
```

Controller không cần:

```python
reader.load_story(10)
```

---

# 18. Đây là reactive architecture

Ta có:

```text
State changes
      ↓
Signal
      ↓
UI reacts
```

Thay vì:

```text
Controller
    ↓
find widget
    ↓
set text
    ↓
update progress
    ↓
refresh list
```

Reactive approach:

```text
State
 ↓
Signals
 ↓
Views react
```

---

# 19. Một ví dụ hoàn chỉnh

```python
from PySide6.QtCore import QObject, Signal


class AppState(QObject):

    story_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self._story_id = None

    def select_story(self, story_id):

        if story_id == self._story_id:
            return

        self._story_id = story_id

        self.story_changed.emit(
            story_id
        )


class ReaderView(QObject):

    def on_story_changed(self, story_id):
        print(
            f"Loading story {story_id}"
        )
```

Composition:

```python
state = AppState()
reader = ReaderView()

state.story_changed.connect(
    reader.on_story_changed
)

state.select_story(10)
```

Kết quả:

```text
Loading story 10
```

---

# 20. Signal nên đại diện cho cái gì?

Một Signal tốt thường biểu diễn:

### State changed

```python
title_changed = Signal(str)
```

### Operation completed

```python
saved = Signal()
```

### Progress

```python
progress_changed = Signal(int)
```

### Error

```python
error_occurred = Signal(str)
```

### User intent

```python
save_requested = Signal()
```

---

# 21. Signal `*_changed`

Đây là convention rất hữu ích.

Ví dụ:

```python
title_changed
loading_changed
selected_story_changed
progress_changed
theme_changed
```

Khi property thay đổi:

```python
self._title = title
self.title_changed.emit(title)
```

---

# 22. Tránh emit thừa

Không nên:

```python
def set_title(self, title):

    self._title = title
    self.title_changed.emit(title)
```

nếu title không thay đổi.

Nên:

```python
def set_title(self, title):

    if title == self._title:
        return

    self._title = title
    self.title_changed.emit(title)
```

Điều này tránh UI update không cần thiết.

---

# 23. Signal `loading_changed`

Ví dụ:

```python
class StoryViewModel(QObject):

    loading_changed = Signal(bool)

    def load_story(self):

        self.loading_changed.emit(True)

        # load...

        self.loading_changed.emit(False)
```

UI:

```python
vm.loading_changed.connect(
    spinner.setVisible
)
```

---

# 24. Error Signal

Không nên để ViewModel:

```python
QMessageBox.warning(...)
```

Thay vào đó:

```python
error_occurred = Signal(str)
```

Ví dụ:

```python
try:
    self.service.load_story(story_id)

except Exception as exc:
    self.error_occurred.emit(
        str(exc)
    )
```

View:

```python
vm.error_occurred.connect(
    self.show_error
)
```

---

# 25. Tại sao cách này tốt?

ViewModel:

```text
"Đã xảy ra lỗi"
```

View quyết định:

```text
QMessageBox
StatusBar
Inline error
Toast
Log
```

Do đó business/application layer không bị dính UI.

---

# 26. Signal cho User Intent

Một pattern khác:

```python
class StoryView(QObject):

    save_requested = Signal()

    def on_save_clicked(self):
        self.save_requested.emit()
```

Controller:

```python
view.save_requested.connect(
    controller.save
)
```

Flow:

```text
Button
 ↓
View
 ↓
save_requested
 ↓
Controller
```

View không biết:

```text
Service
Repository
Database
```

---

# 27. Đây là UI boundary

Ta có:

```text
┌────────────── Presentation ──────────────┐
│                                          │
│ View ─────Signal────→ Controller         │
│                                          │
└──────────────────────────────────────────┘
                         │
                         ▼
                  Application Layer
```

Signal trở thành một boundary rất hữu ích.

---

# 28. Controller có Signal không?

Có.

Ví dụ:

```python
class StoryController(QObject):

    story_loaded = Signal(object)
    error_occurred = Signal(str)
```

Controller:

```python
def load_story(self, story_id):

    try:
        story = self.service.get_story(
            story_id
        )

        self.story_loaded.emit(story)

    except Exception as exc:
        self.error_occurred.emit(str(exc))
```

View:

```python
controller.story_loaded.connect(
    self.show_story
)
```

---

# 29. Nhưng Controller không nên trở thành Event Bus

Sai architecture:

```text
Controller
 ├── 30 signals
 ├── 20 methods
 ├── state
 ├── repository
 ├── service
 ├── worker
 └── event bus
```

Đây là dấu hiệu Controller đang thành **God Object**.

Controller nên orchestration vừa đủ.

---

# 30. Signal vs Event Bus

Bây giờ chúng ta có thể phân biệt sâu hơn:

### Signal

```text
QObject A
   │
   ▼
Signal
   │
   ▼
QObject B
```

Thường có context rõ ràng.

### Event Bus

```text
Publisher
    │
    ▼
 EventBus
    │
 ┌──┼──┐
 ▼  ▼  ▼
 A  B  C
```

Cross-module và decoupled hơn.

---

# 31. Khi nào dùng Signal?

Tôi khuyến nghị:

```text
Button → View
View → Controller
Worker → Controller
State → ViewModel
ViewModel → View
```

dùng Signal.

---

# 32. Khi nào dùng Event Bus?

Ví dụ:

```text
Crawler
   │
   ▼
EventBus
   ├── Logger
   ├── Dashboard
   ├── Notification
   └── Statistics
```

Event Bus phù hợp hơn.

---

# 33. Một architecture kết hợp

Đây là architecture chúng ta muốn hướng tới:

```text
                         Application
                              │
               ┌──────────────┴──────────────┐
               │                             │
             State                        EventBus
               │                             │
            Signal                         Events
               │                             │
               ▼                             ▼
          ViewModel                    Cross-module
               │                       subscribers
            Signal
               │
               ▼
              View
```

Đây là điểm quan trọng:

> **Không phải Signal hoặc Event Bus. Có thể dùng cả hai, nhưng mỗi cái giải quyết một loại communication khác nhau.**

---

# 34. Signal với Service Layer

Service thường không cần kế thừa `QObject`.

Ví dụ:

```python
class StoryService:

    def get_story(self, story_id):
        ...
```

ViewModel:

```python
class StoryViewModel(QObject):

    story_loaded = Signal(object)

    def __init__(self, service):
        super().__init__()

        self.service = service

    def load(self, story_id):

        story = self.service.get_story(
            story_id
        )

        self.story_loaded.emit(
            story
        )
```

Đây là design rất sạch:

```text
ViewModel
   │
   │ method call
   ▼
Service
   │
   ▼
Repository

ViewModel
   │
   │ Signal
   ▼
View
```

---

# 35. Không cần biến mọi class thành QObject

Đây là lỗi rất hay gặp:

```python
class User(QObject):
    ...
```

```python
class Repository(QObject):
    ...
```

```python
class Calculator(QObject):
    ...
```

Không cần.

`QObject` nên được sử dụng khi class thực sự cần Qt object system:

```text
Signal
Slot
Parent/Child
Event
Thread affinity
Timer
```

Domain model thuần Python có thể vẫn là:

```python
@dataclass
class Story:
    id: int
    title: str
```

---

# 36. Signal và Thread

Đây là lý do Signal đặc biệt mạnh trong PySide6.

Ví dụ:

```text
Worker Thread
      │
      │ progress.emit(50)
      ▼
   Signal
      │
      ▼
 GUI Thread
      │
      ▼
ProgressBar
```

Qt có cơ chế queued connection giúp communication giữa QObject ở các thread khác nhau.

Chúng ta sẽ học sâu ở **Buổi 38–40**.

---

# 37. Direct vs Queued Connection

Qt có các kiểu connection.

Một trong những khái niệm quan trọng:

```text
Direct Connection
Queued Connection
```

### Direct

Slot có thể chạy ngay trong thread phát signal.

### Queued

Event được đưa vào event loop của receiver thread.

Đây là một trong những nền tảng của:

```text
QThread
Worker
GUI thread
```

Chúng ta chưa cần đào sâu implementation hôm nay.

---

# 38. `@Slot`

Có thể khai báo:

```python
from PySide6.QtCore import Slot


@Slot(int)
def on_progress(value):
    ...
```

Ví dụ:

```python
class ProgressWidget(QObject):

    @Slot(int)
    def on_progress(self, value):
        print(value)
```

`@Slot` giúp Qt biết rõ slot signature và có thể có lợi về hiệu năng/metadata.

---

# 39. Signal → Slot nên rõ ràng

Tốt:

```python
progress_changed = Signal(int)

@Slot(int)
def on_progress(value):
    ...
```

Không rõ:

```python
event = Signal(object)

def handler(data):
    ...
```

Trong application lớn, typed communication dễ maintain hơn.

---

# 40. Signal naming

Tôi đề xuất:

```text
*_changed
*_requested
*_started
*_finished
*_completed
*_failed
*_occurred
*_selected
*_updated
```

Ví dụ:

```python
story_selected = Signal(int)
save_requested = Signal()
loading_changed = Signal(bool)
crawl_started = Signal()
crawl_completed = Signal()
error_occurred = Signal(str)
```

---

# 41. Một lỗi architecture nguy hiểm

Không nên:

```python
class ViewModel(QObject):

    @Slot()
    def save(self):
        self.button.setEnabled(False)
        self.status_bar.showMessage(...)
        self.table.clear()
```

ViewModel đang điều khiển UI.

Nên:

```python
class ViewModel(QObject):

    loading_changed = Signal(bool)
    saved = Signal()
    error_occurred = Signal(str)
```

View:

```python
vm.loading_changed.connect(
    self.set_loading
)

vm.saved.connect(
    self.show_saved
)

vm.error_occurred.connect(
    self.show_error
)
```

---

# 42. Reactive UI

Khi áp dụng đúng:

```text
Application State
        │
        ▼
     Signal
        │
        ▼
    ViewModel
        │
        ▼
     Signal
        │
        ▼
       View
```

View chủ yếu:

```text
render
bind
respond
```

thay vì chứa business logic.

---

# 43. Data Binding thủ công

PySide6 không bắt buộc bạn phải dùng framework MVVM đầy đủ.

Có thể binding thủ công:

```python
vm.title_changed.connect(
    self.title_label.setText
)
```

```python
vm.loading_changed.connect(
    self.spinner.setVisible
)
```

```python
vm.progress_changed.connect(
    self.progress_bar.setValue
)
```

Đây chính là một dạng **manual reactive binding**.

---

# 44. Một ViewModel hoàn chỉnh hơn

```python
class StoryViewModel(QObject):

    title_changed = Signal(str)
    loading_changed = Signal(bool)
    progress_changed = Signal(int)
    error_occurred = Signal(str)
    loaded = Signal()

    def __init__(self, service):
        super().__init__()

        self.service = service

    def load_story(self, story_id):

        self.loading_changed.emit(True)

        try:
            story = self.service.get_story(
                story_id
            )

            self.title_changed.emit(
                story.title
            )

            self.progress_changed.emit(
                100
            )

            self.loaded.emit()

        except Exception as exc:

            self.error_occurred.emit(
                str(exc)
            )

        finally:

            self.loading_changed.emit(
                False
            )
```

---

# 45. View

```python
class StoryView(QWidget):

    def __init__(self, vm):
        super().__init__()

        self.vm = vm

        vm.title_changed.connect(
            self.title_label.setText
        )

        vm.loading_changed.connect(
            self.set_loading
        )

        vm.progress_changed.connect(
            self.progress_bar.setValue
        )

        vm.error_occurred.connect(
            self.show_error
        )
```

View không biết Repository.

Không biết SQLite.

Không biết SQL.

Không biết crawler.

---

# 46. Architecture lúc này

```text
                 ┌──────────────┐
                 │     View     │
                 └──────┬───────┘
                        │
                     Signals
                        │
                 ┌──────▼───────┐
                 │  ViewModel   │
                 └──────┬───────┘
                        │
                    Method Call
                        │
                 ┌──────▼───────┐
                 │   Service    │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │  Repository  │
                 └──────┬───────┘
                        │
                    Database
```

Đây là một architecture rất tốt cho nhiều ứng dụng PySide6 vừa và lớn.

---

# 47. Signal Architecture + Event Bus

Nếu thêm Event Bus:

```text
                        ┌─────────────┐
                        │  Event Bus  │
                        └──────▲──────┘
                               │
                            Events
                               │
                        ┌──────┴──────┐
                        │ Application │
                        └──────┬──────┘
                               │
                           Signals
                               │
                        ┌──────▼──────┐
                        │  ViewModel  │
                        └──────┬──────┘
                               │
                           Signals
                               │
                        ┌──────▼──────┐
                        │    View     │
                        └─────────────┘
```

Đây là mô hình chúng ta sẽ tiếp tục sử dụng ở các buổi sau.

---

# 48. Khi nào không nên dùng Signal?

Không nên biến:

```python
service.get_story()
```

thành:

```python
service.story_requested.emit(...)
```

nếu chỉ có một nơi cần kết quả.

Nếu logic là:

```text
request → result
```

method call thường rõ ràng hơn.

Signal phù hợp với:

```text
notification
state change
lifecycle
progress
user intent
```

---

# 49. Nguyên tắc vàng

Có thể nhớ 4 câu:

```text
Method Call
→ Tôi cần bạn làm việc này.

Signal
→ Tôi thông báo rằng điều này xảy ra.

State
→ Đây là trạng thái hiện tại.

Event Bus
→ Tôi phát một fact cho nhiều module.
```

---

# 50. Bài tập 1 — Counter

Tạo:

```python
class Counter(QObject):

    value_changed = Signal(int)
```

Có:

```python
increment()
decrement()
```

Mỗi khi value thay đổi:

```python
value_changed.emit(value)
```

UI:

```text
Value: 10

[ - ] [ + ]
```

---

# 51. Bài tập 2 — ViewModel

Tạo:

```python
class UserViewModel(QObject):
```

Signals:

```python
name_changed = Signal(str)
loading_changed = Signal(bool)
error_occurred = Signal(str)
```

Không được import:

```python
QWidget
QLabel
QMessageBox
```

---

# 52. Bài tập 3 — User Intent

Tạo:

```python
class UserView(QWidget):

    save_requested = Signal()
    delete_requested = Signal(int)
```

Khi user click:

```text
Save
Delete user 10
```

emit signal tương ứng.

Controller subscribe.

---

# 53. Bài tập 4 — State → View

Tạo:

```python
class AppState(QObject):

    selected_story_changed = Signal(int)
```

Khi:

```python
state.select_story(100)
```

View phải tự động:

```text
Story ID: 100
```

Không cho Controller gọi trực tiếp:

```python
view.label.setText(...)
```

---

# 54. Bài tập 5 — Signal vs Event Bus

Thiết kế:

```text
A. Button → Controller
B. State → View
C. Worker → ProgressBar
D. Crawler → Logger
E. Crawler → Dashboard
F. Crawler → Notification
```

Chọn:

```text
Signal
Event Bus
Method Call
```

và giải thích lý do.

---

# 55. Mini Project — Reactive Story Reader

Xây một UI:

```text
┌─────────────────────────────────────────┐
│ Story Reader                            │
├─────────────────────────────────────────┤
│ Story ID: [10]          [Load]          │
│                                         │
│ Title: Naruto                           │
│                                         │
│ Loading: ████████░░ 80%                 │
│                                         │
│ Status: Loading chapter...              │
└─────────────────────────────────────────┘
```

Architecture:

```text
                 View
                  │
             save/load Signal
                  │
                  ▼
             Controller
                  │
                  ▼
             ViewModel
                  │
             ┌────┴─────┐
             ▼          ▼
          Service      Signals
             │           │
             ▼           ▼
        Repository       View
             │
             ▼
           SQLite
```

Yêu cầu:

### View không được:

```python
service.get_story()
```

### ViewModel không được:

```python
label.setText(...)
```

### Service không được:

```python
Signal(...)
```

### Repository không được:

```python
QWidget
```

Mục tiêu là giữ boundary rõ ràng.

---

# 56. Checklist Buổi 34

Bạn cần hiểu được:

* `Signal` là gì?
* `Slot` là gì?
* `connect()` và `emit()` hoạt động thế nào?
* Signal khác callback thế nào?
* Signal có thể truyền dữ liệu thế nào?
* Tại sao ViewModel nên expose Signal?
* Tại sao ViewModel không nên biết `QWidget`?
* `*_changed` dùng để làm gì?
* Signal có thể dùng cho User Intent không?
* Signal và Event Bus khác nhau ở đâu?
* Khi nào nên dùng method call thay vì Signal?
* `@Slot` có vai trò gì?
* Signal liên quan thế nào tới QThread?
* Vì sao Signal rất phù hợp với reactive UI?

---

# 57. Mental Model cuối buổi

Đừng chỉ nhớ:

```python
button.clicked.connect(...)
```

Hãy nhìn Signal ở mức architecture:

```text
                    APPLICATION
                         │
          ┌──────────────┴──────────────┐
          │                             │
        State                        Services
          │                             │
       Signals                       Methods
          │                             │
          ▼                             ▼
      ViewModel                    Repository
          │
       Signals
          │
          ▼
         View
```

Còn **Event Bus** dùng ở nơi communication cần rộng hơn:

```text
Crawler
   │
   ▼
Event Bus
   ├── Logger
   ├── Dashboard
   ├── Notification
   └── Statistics
```

### Công thức kiến trúc cần nhớ

```text
Local UI communication
        ↓
      Signal

State notification
        ↓
      Signal

Request → result
        ↓
   Method / Service

Cross-module notification
        ↓
    Event Bus
```

**Buổi 35 — Project Structure** sẽ ghép toàn bộ những gì chúng ta vừa học:

```text
main.py
   │
   ▼
Composition Root
   │
   ├── State
   ├── EventBus
   ├── Services
   ├── Repositories
   ├── ViewModels
   └── Views
```

và chúng ta sẽ thiết kế **project structure thực tế cho một ứng dụng PySide6 production-style**, trước khi bước sang **Phần IV — Threading & Concurrency**.
