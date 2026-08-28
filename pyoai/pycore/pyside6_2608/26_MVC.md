# Phần III — UI Architecture

# Buổi 26 — MVC trong PySide6

Buổi này rất quan trọng vì chúng ta sẽ nối kiến thức **Qt Model/View** đã học ở Phần II với **UI Architecture**.

Mục tiêu cuối buổi:

```text
Bạn không chỉ biết viết MVC,
mà hiểu MVC nên được dùng ở đâu trong PySide6.
```

---

# 1. MVC là gì?

MVC =

```text
Model
View
Controller
```

Ý tưởng cơ bản:

```text
             ┌─────────────┐
             │    Model    │
             │             │
             │ Data        │
             │ Business    │
             └──────┬──────┘
                    │
                    │
                    ▼
             ┌─────────────┐
             │    View     │
             │             │
             │ UI          │
             └──────▲──────┘
                    │
                    │
             ┌──────┴──────┐
             │ Controller  │
             │             │
             │ User Action │
             └─────────────┘
```

Có thể hiểu đơn giản:

### Model

> Dữ liệu và logic liên quan đến dữ liệu.

### View

> Hiển thị giao diện.

### Controller

> Nhận hành động của người dùng và điều phối.

---

# 2. Ví dụ MVC kinh điển

Ta có Todo:

```text
Todo
 ├── title
 ├── completed
```

### Model

```python
class Todo:
    def __init__(self, title: str):
        self.title = title
        self.completed = False
```

### View

```python
class TodoView:
    def show_todo(self, todo):
        print(todo.title)
```

### Controller

```python
class TodoController:

    def add_todo(self, title):
        todo = Todo(title)

        self.view.show_todo(todo)
```

Controller điều phối:

```text
User
 ↓
Controller
 ↓
Model
 ↓
View
```

---

# 3. Nhưng PySide6 có một vấn đề đặc biệt

Qt đã có kiến trúc:

> **Model/View**

Chúng ta vừa học:

```text
QListView
QTableView
QTreeView

QAbstractListModel
QAbstractTableModel
QAbstractItemModel
```

Vì vậy khi nói:

> "MVC trong PySide6"

không được hiểu đơn giản là:

```text
MVC truyền thống
=
Qt Model/View
```

Hai khái niệm này **không hoàn toàn giống nhau**.

---

# 4. MVC truyền thống vs Qt Model/View

### MVC truyền thống

```text
Model
View
Controller
```

### Qt

```text
Model
    │
    ▼
View
    │
    ▼
Delegate
```

Qt thường gọi đây là:

> **Model/View architecture**

Qt tách phần hiển thị dữ liệu khỏi dữ liệu thông qua Model.

---

# 5. Qt Model/View thực chất giải quyết vấn đề gì?

Ví dụ:

```text
100.000 stories
```

Ta không muốn:

```python
for story in stories:
    list_widget.addItem(...)
```

và để UI giữ toàn bộ logic dữ liệu.

Thay vào đó:

```text
             StoryModel
                 │
                 │
                 ▼
             QListView
```

View hỏi Model:

```text
row = 10
→ data(index)
```

Model trả:

```text
Story #10
```

---

# 6. Vì vậy cần phân biệt hai "Model"

Đây là một điểm **cực kỳ quan trọng**.

Trong ứng dụng lớn có thể tồn tại:

```text
Domain Model
```

và:

```text
Qt Model
```

Chúng không nhất thiết là một class.

Ví dụ:

```text
Domain
────────────────
Story
Chapter
Author
```

Trong Presentation:

```text
Qt Model
────────────────
StoryListModel
ChapterListModel
```

---

# 7. Domain Model

Ví dụ:

```python
class Story:

    def __init__(self, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Title is required")

        self.title = title
```

Class này:

```text
không biết PySide6
không biết QWidget
không biết QModelIndex
không biết Signal
```

Đây là điều tốt.

---

# 8. Qt Model

Ta có:

```python
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
)


class StoryListModel(QAbstractListModel):

    def __init__(self, stories=None):
        super().__init__()

        self._stories = stories or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._stories)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._stories[index.row()].title

        return None
```

Model này **biết Qt**.

---

# 9. Đây là hai tầng khác nhau

```text
┌─────────────────────────┐
│       Domain            │
│                         │
│ Story                   │
│ Chapter                 │
│ Author                  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Presentation        │
│                         │
│ StoryListModel          │
│ ChapterListModel        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         View            │
│                         │
│ QListView               │
│ QTableView              │
└─────────────────────────┘
```

Đây là kiến trúc rất hữu ích cho project Story Reader sau này.

---

# 10. MVC trong một ứng dụng PySide6

Ta có thể thiết kế:

```text
                    User
                      │
                      ▼
              ┌──────────────┐
              │     View     │
              │  MainWindow  │
              └──────┬───────┘
                     │
                 user action
                     │
                     ▼
              ┌──────────────┐
              │ Controller   │
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
              └──────────────┘
```

Trong khi đó:

```text
Domain
   │
   ▼
Qt Model
   │
   ▼
QListView
```

Đây là cách kết hợp MVC với Qt Model/View.

---

# 11. Ví dụ thực tế

Ta xây Todo App.

## Domain

```python
class Todo:

    def __init__(self, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Title is required")

        self.title = title
        self.completed = False
```

---

# 12. Service

```python
class TodoService:

    def __init__(self):
        self._todos = []

    def create(self, title: str):
        todo = Todo(title)

        self._todos.append(todo)

        return todo

    def list_all(self):
        return list(self._todos)
```

Service chịu trách nhiệm application logic.

---

# 13. Qt Model

```python
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
)


class TodoListModel(QAbstractListModel):

    def __init__(self, todos=None):
        super().__init__()

        self._todos = todos or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._todos)

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid():
            return None

        todo = self._todos[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return todo.title

        return None

    def set_todos(self, todos):
        self.beginResetModel()

        self._todos = list(todos)

        self.endResetModel()
```

---

# 14. View

```python
from PySide6.QtWidgets import (
    QMainWindow,
    QListView,
)


class TodoView(QMainWindow):

    def __init__(self):
        super().__init__()

        self.list_view = QListView()

        self.setCentralWidget(
            self.list_view
        )
```

View chỉ quan tâm UI.

---

# 15. Controller

```python
class TodoController:

    def __init__(
        self,
        view,
        service,
        model,
    ):
        self.view = view
        self.service = service
        self.model = model

        self.view.add_button.clicked.connect(
            self.create_todo
        )

    def create_todo(self):
        title = self.view.title_input.text()

        try:
            self.service.create(title)

        except ValueError as e:
            self.view.show_error(str(e))
            return

        self.model.set_todos(
            self.service.list_all()
        )

        self.view.title_input.clear()
```

Controller trở thành lớp:

```text
UI Event
   ↓
Controller
   ↓
Service
   ↓
Model
```

---

# 16. Nhưng có một vấn đề

Nếu Controller phải làm:

```python
self.model.set_todos(
    self.service.list_all()
)
```

sau mỗi thao tác, controller bắt đầu biết khá nhiều chi tiết.

Sau này chúng ta sẽ học:

```text
Application State
Event Bus
Signal-based Architecture
```

để giải quyết những coupling này.

---

# 17. MVC không phải là luật cứng

Một sai lầm phổ biến:

> "Mọi PySide6 app đều phải có đúng 3 class Model/View/Controller."

Không.

MVC là **architecture pattern**, không phải template bắt buộc.

Một app nhỏ:

```text
MainWindow
```

có thể hoàn toàn hợp lý.

App vừa:

```text
MainWindow
Service
Qt Model
```

có thể đủ.

App lớn:

```text
Presentation
Application
Domain
Infrastructure
```

thì cần architecture rõ ràng hơn.

---

# 18. MVC và Clean Architecture

Đây là chỗ kiến thức cũ của bạn bắt đầu kết nối.

Ta có:

```text
             Presentation
                  │
        ┌─────────┴─────────┐
        │                   │
       View             Controller
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
             Application
                  │
                  ▼
               Domain
                  │
                  ▼
           Infrastructure
```

MVC chủ yếu giúp tổ chức:

```text
Presentation layer
```

Còn Clean Architecture tổ chức:

```text
toàn bộ application
```

Do đó:

> **MVC không thay thế Clean Architecture.**

Nó có thể trở thành một phần của Presentation Layer.

---

# 19. MVC và MVVM

Buổi 27 chúng ta sẽ học:

```text
MVC
```

so với:

```text
MVVM
```

MVC:

```text
View
 ↓
Controller
 ↓
Model
```

MVVM:

```text
View
 ↓
ViewModel
 ↓
Model
```

Điểm khác biệt rất quan trọng:

### MVC

Controller điều phối hành động.

### MVVM

ViewModel cung cấp state và behavior cho View.

Trong PySide6, MVVM có thể rất hữu ích khi UI phức tạp.

---

# 20. Khi nào dùng MVC?

MVC phù hợp khi:

```text
UI có nhiều action
```

Ví dụ:

```text
Create
Update
Delete
Search
Refresh
Import
Export
```

Controller có thể điều phối:

```text
User Action
    ↓
Controller
    ↓
Service
```

---

# 21. Khi nào không cần MVC?

Ví dụ:

```text
Calculator
```

Nếu chỉ có:

```text
9 buttons
+
-
*
/
=
```

thì tạo:

```text
CalculatorView
CalculatorController
CalculatorModel
```

có thể là over-engineering.

Đôi khi:

```python
class Calculator(QWidget):
    ...
```

là đủ.

---

# 22. Nguyên tắc quan trọng

> **Architecture phải phục vụ complexity.**

Không phải:

> "App chuyên nghiệp thì phải có thật nhiều class."

Một kiến trúc tốt là kiến trúc:

```text
đủ tách biệt
+
dễ test
+
dễ thay đổi
+
không quá phức tạp
```

---

# 23. Một architecture thực tế cho Story Reader

Project lớn của chúng ta sẽ hướng tới:

```text
story_reader/
│
├── main.py
│
├── app/
│   ├── application.py
│   └── config.py
│
├── domain/
│   ├── story.py
│   ├── chapter.py
│   └── author.py
│
├── application/
│   ├── story_service.py
│   ├── chapter_service.py
│   └── crawl_service.py
│
├── infrastructure/
│   ├── database/
│   └── repositories/
│
└── presentation/
    ├── windows/
    ├── dialogs/
    ├── widgets/
    └── models/
```

Trong đó:

```text
presentation/models/
```

chứa:

```text
StoryListModel
ChapterListModel
SourceTreeModel
```

Đây chính là Qt Model.

---

# 24. Luồng của Story List

Ví dụ user click:

```text
Source A
```

Luồng có thể là:

```text
User
 │
 ▼
SourceTreeView
 │
 ▼
Controller
 │
 ▼
StoryService
 │
 ▼
StoryRepository
 │
 ▼
SQLite
 │
 ▼
List[Story]
 │
 ▼
StoryListModel
 │
 ▼
QListView
```

Đây mới là kiến trúc mà chúng ta đang hướng tới.

---

# 25. Một lỗi kiến trúc rất phổ biến

Không nên:

```python
class StoryListModel(QAbstractListModel):

    def load_stories(self):
        conn = sqlite3.connect(
            "stories.db"
        )

        ...
```

Bởi vì:

```text
Qt Model
   ↓
SQLite
```

làm Presentation phụ thuộc Infrastructure.

Thay vào đó:

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
SQLite
```

rồi:

```text
List[Story]
    ↓
StoryListModel
    ↓
QListView
```

---

# 26. Controller không nên trở thành "God Object"

Có một cái bẫy:

Ban đầu:

```text
MainWindow
```

là God Object.

Sau khi refactor:

```text
Controller
```

lại trở thành God Object.

Ví dụ:

```python
class StoryController:

    def crawl(self):
        ...

    def save_story(self):
        ...

    def download_image(self):
        ...

    def export_epub(self):
        ...

    def backup_database(self):
        ...

    def login(self):
        ...
```

Đây vẫn là vấn đề.

Controller nên:

> **điều phối**, không nên chứa toàn bộ business logic.

---

# 27. Controller tốt

```text
Controller
    │
    ├── nhận event
    │
    ├── lấy input
    │
    ├── gọi use case/service
    │
    ├── xử lý kết quả
    │
    └── cập nhật View
```

Controller không nên:

```text
Controller
    │
    ├── SQL
    ├── HTTP
    ├── parsing
    ├── business rules
    ├── file processing
    └── crawling
```

---

# 28. Bài tập

## Bài 1

Cho:

```python
class MainWindow(QMainWindow):

    def save_story(self):
        title = self.title_input.text()

        if not title:
            return

        conn = sqlite3.connect("story.db")

        conn.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (title,),
        )

        conn.commit()

        self.list_widget.addItem(title)
```

Hãy chỉ ra:

```text
View responsibility
Controller responsibility
Business responsibility
Infrastructure responsibility
```

---

# 29. Bài 2

Thiết kế:

```text
Story
StoryService
StoryListModel
StoryView
StoryController
```

Sơ đồ:

```text
              StoryView
                  │
                  ▼
           StoryController
                  │
                  ▼
             StoryService
                  │
                  ▼
                Story
```

và:

```text
                Story
                  │
                  ▼
           StoryListModel
                  │
                  ▼
              QListView
```

---

# 30. Bài 3 — câu hỏi quan trọng

Hãy trả lời:

### 1.

`QListView` có phải Controller không?

### 2.

`QAbstractListModel` có phải Domain Model không?

### 3.

`Story` có nên import PySide6 không?

### 4.

`StoryService` có nên biết `QMessageBox` không?

### 5.

`Controller` có nên chứa SQL không?

### 6.

`MainWindow` có nên trực tiếp gọi SQLite không?

### 7.

Qt Model/View và MVC có phải cùng một thứ không?

Nếu trả lời được 7 câu này, bạn đã nắm được phần cốt lõi của Buổi 26.

---

# 31. Tổng kết Mental Model

Đừng ghi nhớ MVC như:

```text
Model
View
Controller
```

Hãy nhớ theo **luồng trách nhiệm**:

```text
                USER
                  │
                  ▼
               VIEW
                  │
             user action
                  │
                  ▼
            CONTROLLER
                  │
                  ▼
             SERVICE
                  │
                  ▼
              DOMAIN
                  │
                  ▼
           REPOSITORY
                  │
                  ▼
             DATABASE
```

Còn khi cần hiển thị collection:

```text
             DOMAIN DATA
                  │
                  ▼
              QT MODEL
                  │
                  ▼
                VIEW
                  │
                  ▼
             QListView
             QTableView
             QTreeView
```

Đây là nền tảng rất quan trọng trước khi sang **Buổi 27 — MVVM**.

Ở Buổi 27, chúng ta sẽ không chỉ học định nghĩa MVVM mà sẽ **lấy chính Todo App v2 của Buổi 25, chuyển MVC → MVVM**, từ đó thấy rõ **ViewModel khác Controller ở đâu và tại sao MVVM đặc biệt phù hợp với UI có nhiều state**.
