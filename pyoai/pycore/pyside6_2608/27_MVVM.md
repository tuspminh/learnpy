# Phần III — UI Architecture

# Buổi 27 — MVVM trong PySide6

Buổi 27 là bước tiếp theo sau MVC. Nếu **MVC giúp chúng ta tách Controller khỏi View**, thì **MVVM** đi xa hơn:

> **Đưa UI state và presentation logic vào ViewModel, để View trở nên mỏng và ít chứa logic hơn.**

Đặc biệt với PySide6, MVVM rất đáng học vì nó kết hợp tự nhiên với:

* `Signal / Slot`
* `Property`
* Qt Model/View
* State management
* Async/Thread
* Testing

Và sau này khi làm **Story Reader Desktop**, MVVM sẽ rất hữu ích.

---

# 1. Vấn đề của MVC

Ở Buổi 26 ta có:

```text
User
  │
  ▼
View
  │
  ▼
Controller
  │
  ▼
Service
  │
  ▼
Domain
```

Ví dụ:

```python
def add_todo(self):
    title = self.view.title_input.text()

    try:
        todo = self.service.create(title)

    except ValueError as e:
        self.view.show_error(str(e))
        return

    self.view.clear_input()
```

Controller xử lý khá nhiều thứ.

Khi application lớn hơn, Controller có thể bắt đầu phình to:

```text
TodoController
│
├── create
├── update
├── delete
├── search
├── filter
├── sort
├── selection
├── loading
├── error
└── pagination
```

Đây là lúc MVVM trở nên hấp dẫn.

---

# 2. MVVM là gì?

MVVM:

```text
Model
View
ViewModel
```

Kiến trúc:

```text
┌───────────────┐
│     View      │
│               │
│ PySide6 UI    │
└───────┬───────┘
        │
        │ Binding
        ▼
┌───────────────┐
│   ViewModel   │
│               │
│ UI State      │
│ UI Logic      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│     Model     │
│               │
│ Domain        │
└───────────────┘
```

Điểm quan trọng nhất:

> **View không trực tiếp quyết định application logic.**

View giao tiếp với ViewModel.

---

# 3. MVC vs MVVM

MVC:

```text
View
 │
 ▼
Controller
 │
 ▼
Model
```

MVVM:

```text
View
 │
 ▼
ViewModel
 │
 ▼
Model
```

Nhìn sơ đồ thì rất giống nhau.

Điểm khác nằm ở **vai trò**.

---

# 4. Controller vs ViewModel

### Controller

Thường phản ứng với:

```text
User Action
```

Ví dụ:

```python
button.clicked.connect(
    controller.create
)
```

Controller:

```text
Action
  ↓
Do something
```

---

### ViewModel

Quản lý:

```text
UI State
```

Ví dụ:

```text
todos
loading
error
selected_todo
search_text
can_save
```

ViewModel:

```text
State
  ↓
UI phản ánh State
```

Đây là khác biệt quan trọng nhất.

---

# 5. Mental Model

Hãy tưởng tượng ViewModel là:

> **"Bộ não dành riêng cho UI."**

Domain nói:

> Story là gì?

Application nói:

> Làm sao tạo Story?

ViewModel nói:

> UI cần biết điều gì?

Ví dụ:

```text
Domain
──────
Story

Application
───────────
CreateStory

ViewModel
─────────
stories
loading
error
selected_story
can_create
search_text

View
────
QLineEdit
QListView
QPushButton
QLabel
```

---

# 6. UI State là gì?

Đây là khái niệm cực kỳ quan trọng.

Ví dụ màn hình Story List:

```text
stories = [...]
loading = False
error = ""
search_text = ""
selected_story = None
```

Đó là **UI state**.

Ví dụ:

```python
if loading:
    self.progress.show()
else:
    self.progress.hide()
```

hoặc:

```python
self.button.setEnabled(
    bool(search_text)
)
```

Đây là presentation logic.

---

# 7. Tạo ViewModel đầu tiên

PySide6 có `QObject`.

Ta có thể tạo:

```python
from PySide6.QtCore import QObject, Signal


class TodoViewModel(QObject):

    todos_changed = Signal()
    error_changed = Signal(str)

    def __init__(self, service):
        super().__init__()

        self.service = service

        self._todos = []

    @property
    def todos(self):
        return self._todos
```

ViewModel không phải `QWidget`.

Đây là điểm quan trọng:

```text
ViewModel
    ↓
QObject

không phải

ViewModel
    ↓
QWidget
```

---

# 8. Method trong ViewModel

```python
class TodoViewModel(QObject):

    todos_changed = Signal()
    error_changed = Signal(str)

    def __init__(self, service):
        super().__init__()

        self.service = service
        self._todos = []

    @property
    def todos(self):
        return self._todos

    def load(self):
        self._todos = self.service.list_all()

        self.todos_changed.emit()
```

View có thể lắng nghe:

```python
view_model.todos_changed.connect(
    self.refresh
)
```

---

# 9. ViewModel xử lý action

```python
def create_todo(self, title):
    try:
        self.service.create(title)

    except ValueError as e:
        self.error_changed.emit(str(e))
        return

    self.load()
```

View:

```python
view_model.create_todo(
    self.title_input.text()
)
```

Nhưng View không xử lý:

```python
if not title:
```

Business rule nằm ở Domain.

---

# 10. View

View có thể rất đơn giản:

```python
class TodoView(QWidget):

    def __init__(self, view_model):
        super().__init__()

        self.view_model = view_model

        self.input = QLineEdit()
        self.button = QPushButton("Add")
        self.list_widget = QListWidget()

        layout = QVBoxLayout(self)

        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget)

        self.button.clicked.connect(
            self.add_todo
        )

        self.view_model.todos_changed.connect(
            self.refresh
        )

        self.view_model.error_changed.connect(
            self.show_error
        )
```

---

# 11. View chỉ chuyển event

```python
def add_todo(self):
    self.view_model.create_todo(
        self.input.text()
    )
```

View không làm:

```python
sqlite3.connect(...)
```

Không làm:

```python
if len(title) > 100:
```

Không làm:

```python
self.todos.append(...)
```

View chỉ:

```text
User action
    ↓
ViewModel
```

---

# 12. Refresh UI

```python
def refresh(self):
    self.list_widget.clear()

    for todo in self.view_model.todos:
        self.list_widget.addItem(
            todo.title
        )
```

View nhận state mới và render.

---

# 13. Error State

ViewModel có thể quản lý error:

```python
class TodoViewModel(QObject):

    error_changed = Signal(str)

    def create_todo(self, title):
        try:
            self.service.create(title)

        except ValueError as e:
            self.error_changed.emit(str(e))
```

View:

```python
def show_error(self, message):
    QMessageBox.warning(
        self,
        "Error",
        message,
    )
```

Điểm hay:

```text
ViewModel
    │
    │ "error = ..."
    ▼
View
    │
    ▼
QMessageBox
```

ViewModel không cần biết `QMessageBox`.

---

# 14. State nên được biểu diễn rõ ràng

Thay vì:

```python
self.loading = True
```

và không ai biết khi nào nó thay đổi, ta có:

```python
loading_changed = Signal(bool)
```

Ví dụ:

```python
class TodoViewModel(QObject):

    loading_changed = Signal(bool)

    def load(self):
        self.loading_changed.emit(True)

        try:
            self._todos = self.service.list_all()

        finally:
            self.loading_changed.emit(False)
```

View:

```python
self.view_model.loading_changed.connect(
    self.set_loading
)
```

---

# 15. Đây chính là reactive thinking

Ta không nghĩ:

```text
"hãy thay đổi button"
```

mà nghĩ:

```text
loading = True
```

Sau đó UI phản ứng:

```text
loading = True
       ↓
ProgressBar.show()
Button.disable()
```

Khi:

```text
loading = False
```

UI:

```text
ProgressBar.hide()
Button.enable()
```

Đây là tư duy rất quan trọng khi xây UI phức tạp.

---

# 16. Signal chính là cầu nối

Trong PySide6:

```text
ViewModel
   │
   │ Signal
   ▼
View
```

Ví dụ:

```python
loading_changed = Signal(bool)
```

và:

```python
todos_changed = Signal()
```

và:

```python
error_changed = Signal(str)
```

Ta có:

```text
              ViewModel
                  │
       ┌──────────┼───────────┐
       │          │           │
       ▼          ▼           ▼
 loading      todos        error
       │          │           │
       ▼          ▼           ▼
     View       View         View
```

---

# 17. Qt Property

PySide6 còn có:

```python
Property
```

Ví dụ:

```python
from PySide6.QtCore import (
    QObject,
    Property,
    Signal,
)


class TodoViewModel(QObject):

    loadingChanged = Signal()

    def __init__(self):
        super().__init__()

        self._loading = False

    def get_loading(self):
        return self._loading

    def set_loading(self, value):
        if self._loading == value:
            return

        self._loading = value
        self.loadingChanged.emit()

    loading = Property(
        bool,
        get_loading,
        set_loading,
        notify=loadingChanged,
    )
```

Đây là một chủ đề sâu.

Chúng ta sẽ quay lại `QProperty` ở **Buổi 79**.

Hiện tại chỉ cần hiểu:

```text
Property
+
Signal
=
Observable State
```

---

# 18. MVVM + Qt Model/View

Đây là phần cực kỳ quan trọng đối với bạn vì chúng ta vừa học xong Qt Model/View.

Không nên:

```text
ViewModel
   ↓
QListWidget
```

đối với data lớn.

Thay vào đó:

```text
ViewModel
   ↓
TodoListModel
   ↓
QListView
```

Kiến trúc:

```text
                    View
                     │
             ┌───────┴───────┐
             │               │
          QListView      QPushButton
             │               │
             ▼               ▼
        Qt Model        ViewModel
             ▲               │
             │               │
             └───────────────┘
                     │
                  Service
                     │
                  Domain
```

---

# 19. Tại sao cần hai Model?

Một lần nữa:

```text
Todo
```

là domain object.

Còn:

```text
TodoListModel(QAbstractListModel)
```

là **presentation model của Qt**.

```text
Domain
──────
Todo

Presentation
────────────
TodoListModel
```

Đừng trộn hai thứ này.

---

# 20. Kiến trúc MVVM hoàn chỉnh

Một app tương đối tốt:

```text
┌─────────────────────────────────────┐
│                 VIEW                │
│                                     │
│ QLineEdit                           │
│ QPushButton                         │
│ QListView                            │
│ QLabel                              │
└─────────────────┬───────────────────┘
                  │
                  │ Signal / User Action
                  ▼
┌─────────────────────────────────────┐
│             VIEWMODEL               │
│                                     │
│ state                               │
│ commands                            │
│ presentation logic                  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          APPLICATION SERVICE        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│               DOMAIN                │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│             REPOSITORY              │
└─────────────────────────────────────┘
```

Đây là architecture chúng ta sẽ tiến tới.

---

# 21. ViewModel không phải Domain Model

Đây là lỗi rất phổ biến.

Không nên:

```python
class TodoViewModel:

    title = ...
    completed = ...
```

rồi coi nó là Todo domain.

ViewModel phục vụ:

```text
UI
```

Domain Model phục vụ:

```text
Business
```

Ví dụ Domain:

```python
class Todo:

    def complete(self):
        if self.completed:
            raise ValueError(
                "Todo already completed"
            )

        self.completed = True
```

ViewModel:

```python
class TodoViewModel(QObject):

    def complete_selected(self):
        ...
```

Hai trách nhiệm khác nhau.

---

# 22. Presentation Logic là gì?

Đây là phần ViewModel rất phù hợp.

Ví dụ:

```text
Nếu không có Todo nào được chọn
→ Disable Delete button
```

Đây không phải business rule.

Nó là:

> **Presentation logic**

ViewModel có thể:

```python
can_delete_changed = Signal(bool)
```

và:

```python
@property
def can_delete(self):
    return self.selected_todo is not None
```

View:

```python
self.delete_button.setEnabled(
    self.view_model.can_delete
)
```

---

# 23. Business Logic vs Presentation Logic

Phân biệt thật rõ:

### Business

```text
Không thể publish Story nếu không có chapter.
```

→ Domain/Application.

### Presentation

```text
Disable Publish button khi chưa chọn Story.
```

→ ViewModel.

Có thể nhìn:

```text
Business rule
    ↓
Domain

UI state / UI behavior
    ↓
ViewModel
```

---

# 24. MVVM và Testing

Đây là một lợi ích cực lớn.

Ta có thể test ViewModel:

```python
def test_create_todo():
    service = FakeTodoService()

    vm = TodoViewModel(service)

    vm.create_todo("Learn PySide6")

    assert len(vm.todos) == 1
```

Không cần:

```python
QMainWindow
```

Không cần:

```python
QPushButton
```

Không cần:

```python
QMessageBox
```

Có thể test phần lớn logic UI mà không cần render giao diện.

---

# 25. Fake Service

Ví dụ:

```python
class FakeTodoService:

    def __init__(self):
        self.todos = []

    def create(self, title):
        todo = Todo(title)

        self.todos.append(todo)

        return todo

    def list_all(self):
        return list(self.todos)
```

Sau này chúng ta học:

```text
Dependency Injection
```

thì ViewModel có thể nhận service từ bên ngoài.

---

# 26. MVVM có phải luôn tốt hơn MVC?

Không.

### App nhỏ

```text
QWidget
```

có thể đủ.

### App vừa

```text
MVC
```

rất ổn.

### UI nhiều state

```text
MVVM
```

thường rất phù hợp.

Ví dụ:

```text
Story Reader
```

có:

```text
loading
search
filter
selection
reading progress
download progress
crawl status
error
current chapter
current story
```

Khi đó ViewModel rất hữu ích.

---

# 27. Ví dụ Story Reader

Một `StoryListViewModel` có thể quản lý:

```python
class StoryListViewModel(QObject):

    stories_changed = Signal()
    loading_changed = Signal(bool)
    error_changed = Signal(str)

    def __init__(self, service):
        super().__init__()

        self.service = service

        self._stories = []
        self._loading = False
        self._error = ""
        self._search = ""
```

State:

```text
stories
loading
error
search
selected_story
```

Commands:

```text
load()
search()
refresh()
select_story()
delete_story()
```

View chỉ render.

---

# 28. Kiến trúc Story Reader

Cuối cùng có thể thành:

```text
                   MainWindow
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 SourceView       StoryView      ReaderView
        │              │              │
        ▼              ▼              ▼
SourceVM          StoryVM        ReaderVM
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 Application
                    Services
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Repository    Crawler       Worker
          │
          ▼
        SQLite
```

Đây là một kiến trúc khá gần với project cuối khóa của chúng ta.

---

# 29. MVC → MVVM

Hãy nhớ sự tiến hóa:

```text
Buổi 25
────────────────────
UI ≠ Business Logic
```

↓

```text
Buổi 26
────────────────────
MVC
```

↓

```text
Buổi 27
────────────────────
MVVM
```

↓

```text
Buổi 28
────────────────────
Controller
```

↓

```text
Buổi 29
────────────────────
Service Layer
```

↓

```text
Buổi 30
────────────────────
Repository Pattern
```

↓

```text
Buổi 31
────────────────────
Dependency Injection
```

↓

```text
Buổi 32
────────────────────
Application State
```

↓

```text
Buổi 33
────────────────────
Event Bus
```

Bạn sẽ thấy architecture ngày càng hoàn chỉnh.

---

# 30. Bài tập thực hành

## Bài 1 — Phân loại

Cho các thành phần:

```text
Story
StoryListModel
MainWindow
StoryViewModel
StoryService
StoryRepository
QListView
SQLite
```

Hãy phân loại thành:

```text
Domain
Application
Presentation
Infrastructure
```

---

# 31. Bài 2 — MVC → MVVM

Ở Buổi 26 ta có:

```text
TodoView
TodoController
TodoService
Todo
```

Hãy chuyển thành:

```text
TodoView
TodoViewModel
TodoService
Todo
```

Luồng:

```text
Button.clicked
      │
      ▼
TodoViewModel.create_todo()
      │
      ▼
TodoService.create()
      │
      ▼
Todo
```

---

# 32. Bài 3 — State

Thiết kế ViewModel có state:

```text
todos
loading
error
selected_todo
```

và các Signal:

```python
todos_changed
loading_changed
error_changed
selected_todo_changed
```

Hãy suy nghĩ:

> Khi `loading=True`, View phải làm gì?

> Khi `error != ""`, View phải làm gì?

> Khi `selected_todo=None`, Delete button phải thế nào?

---

# 33. Bài 4 — Kiến trúc

Hãy giải thích tại sao kiến trúc sau không tốt:

```text
QListView
    ↓
SQLite
```

và tại sao:

```text
QListView
    ↓
TodoListModel
    ↓
ViewModel
    ↓
Service
    ↓
Repository
    ↓
SQLite
```

tốt hơn.

---

# 34. Bài tập nâng cao

Thiết kế:

```text
StoryListViewModel
```

với state:

```text
stories
loading
error
search_text
selected_story
```

và command:

```text
load()
search()
refresh()
select()
delete()
```

Không cần code hoàn chỉnh ngay.

Trước tiên hãy vẽ:

```text
              StoryListView
                    │
                    │
                    ▼
            StoryListViewModel
                    │
             ┌──────┴──────┐
             ▼             ▼
        StoryService   UI State
             │
             ▼
            Story
```

---

# 35. Tổng kết Buổi 27

Điều quan trọng nhất không phải là nhớ chữ **MVVM**.

Hãy nhớ:

```text
View
 │
 │ user interaction
 ▼
ViewModel
 │
 │ application operation
 ▼
Service
 │
 ▼
Domain
```

Và:

```text
ViewModel
    │
    ├── UI State
    ├── Presentation Logic
    ├── Commands
    └── Signals
```

Trong khi:

```text
Domain
    │
    └── Business Rules
```

Và:

```text
Qt Model
    │
    └── Adapt Domain Data → Qt View
```

### Mental Model cuối cùng

```text
                 ┌──────────────┐
                 │     View     │
                 │   PySide6    │
                 └──────┬───────┘
                        │
                 Signal / Action
                        │
                        ▼
                 ┌──────────────┐
                 │  ViewModel   │
                 │              │
                 │ UI State     │
                 │ UI Logic     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Service    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    Domain    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Repository   │
                 └──────┬───────┘
                        │
                        ▼
                    SQLite
```

**Buổi 28 — Controller** sẽ đi sâu vào một câu hỏi rất thú vị: **Nếu đã có ViewModel thì Controller còn cần không?** Chúng ta sẽ phân biệt *Controller, ViewModel, Presenter, Coordinator* và xem khi nào Controller trở thành **God Object**.
