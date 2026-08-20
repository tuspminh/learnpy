# Buổi 9 — `QMainWindow` trong PySide6

Hôm nay chúng ta chuyển từ các `QWidget`/`QDialog` nhỏ sang **kiến trúc cửa sổ chính của một ứng dụng desktop thực tế**.

Roadmap:

```text
QMainWindow
├── Central Widget
├── MenuBar
├── ToolBar
├── StatusBar
└── Dock Widget
```

Sau buổi này, bạn sẽ có mental model:

```text
                    QMainWindow
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     MenuBar          ToolBar         StatusBar
                         │
                         │
                  Central Widget
                         │
                   ┌─────┴─────┐
                   │           │
                 Content      Dock
```

---

# 1. `QMainWindow` là gì?

`QMainWindow` là class được thiết kế dành riêng cho **main window** của ứng dụng.

Import:

```python
from PySide6.QtWidgets import QMainWindow
```

Một ứng dụng CRUD thường có:

```text
┌──────────────────────────────────────────────┐
│ File   Edit   View   Help              Menu │
├──────────────────────────────────────────────┤
│ New  Open  Save  Delete                 Tool │
├──────────────────────────────────────────────┤
│                                              │
│              Main Content                    │
│                                              │
│                                              │
├──────────────────────────────────────────────┤
│ Ready                              3 Todos   │
└──────────────────────────────────────────────┘
```

Đây chính là trường hợp `QMainWindow` phát huy tác dụng.

---

# 2. Khác biệt `QWidget` và `QMainWindow`

Trước đây chúng ta có:

```python
class Window(QWidget):
    ...
```

`QWidget` là widget tổng quát.

Còn:

```python
class MainWindow(QMainWindow):
    ...
```

được thiết kế cho application main window.

Mental model:

```text
QWidget
    ↓
generic container

QMainWindow
    ↓
application main window
    ├── menu
    ├── toolbar
    ├── statusbar
    ├── central widget
    └── dock
```

---

# 3. Tạo `QMainWindow` tối thiểu

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Application")
        self.resize(800, 600)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
```

Chạy lên bạn sẽ có cửa sổ chính.

---

# 4. `QMainWindow` có cấu trúc đặc biệt

Đây là điểm rất quan trọng.

Không nên nghĩ:

```text
QMainWindow
    ↓
QVBoxLayout
```

theo kiểu:

```python
layout = QVBoxLayout(self)
```

như với `QWidget`.

`QMainWindow` có hệ thống layout nội bộ riêng:

```text
QMainWindow
├── MenuBar
├── ToolBar
├── Dock Area
├── Central Widget
└── StatusBar
```

Vì vậy content chính phải được đưa vào:

```python
self.setCentralWidget(...)
```

---

# 5. Central Widget

Ví dụ:

```python
from PySide6.QtWidgets import QLabel
```

```python
label = QLabel("Hello Main Window")

self.setCentralWidget(label)
```

Toàn bộ vùng trung tâm:

```text
┌─────────────────────────────┐
│                             │
│       Hello Main Window     │
│                             │
│        CENTRAL AREA         │
│                             │
└─────────────────────────────┘
```

---

# 6. Thường Central Widget là một container

Trong ứng dụng thực tế, không nên dùng trực tiếp một widget đơn giản.

Thường:

```python
central = QWidget()
```

sau đó:

```python
layout = QVBoxLayout(central)
```

thêm widgets:

```python
layout.addWidget(...)
```

cuối cùng:

```python
self.setCentralWidget(central)
```

---

# 7. Ví dụ

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo App")
        self.resize(800, 600)

        central = QWidget()

        layout = QVBoxLayout(central)

        layout.addWidget(
            QLabel("Todo Application")
        )

        layout.addWidget(
            QPushButton("Add Todo")
        )

        self.setCentralWidget(central)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
```

---

# 8. Vì sao phải `setCentralWidget()`?

`QMainWindow` quản lý rất nhiều vùng:

```text
┌─────────────────────────────────┐
│ MenuBar                         │
├─────────────────────────────────┤
│ ToolBar                         │
├───────┬─────────────────┬───────┤
│       │                 │       │
│ Dock  │ Central Widget  │ Dock  │
│       │                 │       │
├───────┴─────────────────┴───────┤
│ StatusBar                       │
└─────────────────────────────────┘
```

Qt cần biết:

> Widget nào là nội dung chính?

Câu trả lời:

```python
self.setCentralWidget(central)
```

---

# 9. MenuBar

MenuBar nằm phía trên cùng:

```text
File   Edit   View   Help
```

Lấy menu bar:

```python
menu_bar = self.menuBar()
```

Tạo menu:

```python
file_menu = menu_bar.addMenu("File")
```

---

# 10. `QAction`

Menu không trực tiếp thực hiện công việc.

Ta thường tạo:

```python
QAction
```

Import:

```python
from PySide6.QtGui import QAction
```

Ví dụ:

```python
new_action = QAction("New", self)
```

Sau đó:

```python
file_menu.addAction(new_action)
```

---

# 11. Kết nối Action

```python
new_action.triggered.connect(
    self.new_todo
)
```

và:

```python
def new_todo(self):
    print("New Todo")
```

Flow:

```text
User clicks File → New
        ↓
     QAction
        ↓
   triggered
        ↓
    new_todo()
```

Đây là kiến trúc rất quan trọng.

---

# 12. Tạo Menu hoàn chỉnh

```python
def create_menu(self):

    menu_bar = self.menuBar()

    file_menu = menu_bar.addMenu("File")

    new_action = QAction(
        "New",
        self,
    )

    exit_action = QAction(
        "Exit",
        self,
    )

    new_action.triggered.connect(
        self.new_todo
    )

    exit_action.triggered.connect(
        self.close
    )

    file_menu.addAction(new_action)

    file_menu.addSeparator()

    file_menu.addAction(exit_action)
```

---

# 13. Separator

```python
file_menu.addSeparator()
```

UI:

```text
File
├── New
├── Open
├── Save
├────────────
└── Exit
```

Rất hữu ích khi menu có nhiều action.

---

# 14. Menu lồng nhau

Có thể:

```python
view_menu = menu_bar.addMenu("View")

theme_menu = view_menu.addMenu("Theme")
```

Sau đó:

```python
theme_menu.addAction(light_action)
theme_menu.addAction(dark_action)
```

Kết quả:

```text
View
└── Theme
    ├── Light
    └── Dark
```

---

# 15. Toolbar

Toolbar là thanh công cụ:

```text
┌─────────────────────────────────────┐
│ [New] [Open] [Save] [Delete]       │
├─────────────────────────────────────┤
│                                     │
```

Tạo:

```python
toolbar = self.addToolBar("Main Toolbar")
```

Sau đó:

```python
toolbar.addAction(new_action)
toolbar.addAction(open_action)
toolbar.addAction(save_action)
```

---

# 16. Một `QAction` có thể dùng lại

Đây là một trong những design pattern quan trọng nhất của Qt.

Không cần:

```text
Menu → NewButton logic
Toolbar → NewButton logic
```

Mà:

```text
                 QAction
                /       \
               /         \
           Menu           Toolbar
```

Ví dụ:

```python
new_action = QAction("New", self)

file_menu.addAction(new_action)
toolbar.addAction(new_action)
```

Cùng một action.

Khi user:

```text
Menu → New
```

hoặc:

```text
Toolbar → New
```

đều gọi:

```python
new_action.triggered
```

---

# 17. Đây là kiến trúc rất đẹp

```text
                    QAction
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
       MenuItem                  ToolButton
          │                         │
          └────────────┬────────────┘
                       ↓
                  Business Action
```

Không nên copy logic.

---

# 18. StatusBar

StatusBar nằm phía dưới:

```text
┌──────────────────────────────────────┐
│ Ready                    5 Todos     │
└──────────────────────────────────────┘
```

Có thể dùng:

```python
self.statusBar().showMessage(
    "Ready"
)
```

---

# 19. Hiển thị message tạm thời

```python
self.statusBar().showMessage(
    "Todo saved",
    3000,
)
```

`3000` milliseconds:

```text
3 seconds
```

Sau đó message tự biến mất.

---

# 20. StatusBar thường dùng cho gì?

Ví dụ:

```text
Ready
Saving...
Saved successfully
3 items selected
File opened
```

Không nên dùng StatusBar để hiển thị lỗi quan trọng.

Lỗi quan trọng nên dùng:

```text
QMessageBox
```

hoặc inline error.

---

# 21. `QDockWidget`

Đây là thành phần rất thú vị.

Dock widget là panel có thể:

* dock
* undock
* move
* resize
* close

Ví dụ:

```text
┌──────────────────────────────────────────┐
│ Menu                                     │
├──────────────┬───────────────────────────┤
│              │                           │
│ Navigation   │       Main Content        │
│              │                           │
│              │                           │
├──────────────┴───────────────────────────┤
│ Status                                   │
└──────────────────────────────────────────┘
```

---

# 22. Tạo Dock

Import:

```python
from PySide6.QtWidgets import QDockWidget
```

Tạo:

```python
dock = QDockWidget(
    "Navigation",
    self,
)
```

Tạo content:

```python
list_widget = QListWidget()
```

Gắn vào dock:

```python
dock.setWidget(list_widget)
```

---

# 23. Add Dock vào Main Window

```python
self.addDockWidget(
    Qt.DockWidgetArea.LeftDockWidgetArea,
    dock,
)
```

Cần:

```python
from PySide6.QtCore import Qt
```

---

# 24. Dock bên trái

```python
self.addDockWidget(
    Qt.DockWidgetArea.LeftDockWidgetArea,
    dock,
)
```

Các vị trí phổ biến:

```text
LeftDockWidgetArea
RightDockWidgetArea
TopDockWidgetArea
BottomDockWidgetArea
```

---

# 25. Ví dụ Dock

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QListWidget,
)
```

```python
dock = QDockWidget(
    "Categories",
    self,
)

categories = QListWidget()

categories.addItems([
    "All",
    "Work",
    "Personal",
])

dock.setWidget(categories)

self.addDockWidget(
    Qt.DockWidgetArea.LeftDockWidgetArea,
    dock,
)
```

---

# 26. Dock có thể đóng

Mặc định dock thường có nút close.

User có thể:

```text
X
```

để đóng.

Ta có thể kiểm soát features:

```python
dock.setFeatures(
    QDockWidget.DockWidgetFeature.DockWidgetMovable
    | QDockWidget.DockWidgetFeature.DockWidgetFloatable
)
```

---

# 27. Dock Movable

```python
QDockWidget.DockWidgetFeature.DockWidgetMovable
```

cho phép user di chuyển dock.

Ví dụ:

```text
Left
 ↓
Right
```

---

# 28. Dock Floatable

```python
QDockWidget.DockWidgetFeature.DockWidgetFloatable
```

cho phép dock tách ra thành cửa sổ riêng.

```text
Main Window
     +
     |
     └── Floating Dock
```

Đây là behavior rất giống:

* IDE
* Photoshop
* Blender
* Qt Creator

---

# 29. Dock và IDE

Bạn sẽ thấy mô hình này trong:

```text
Qt Creator
Visual Studio
PyCharm
```

Ví dụ:

```text
┌──────────────────────────────────────────┐
│ Menu / Toolbar                           │
├───────────────┬──────────────────────────┤
│ Project       │                          │
│ Explorer      │ Editor                   │
│               │                          │
├───────────────┤                          │
│              │                           │
│ Outline       │                          │
└───────────────┴──────────────────────────┘
```

Các panel như:

```text
Project
Outline
Terminal
Debugger
```

rất phù hợp với `QDockWidget`.

---

# 30. Main Window hoàn chỉnh

Bây giờ ghép tất cả:

```python
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QLabel,
    QListWidget,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo App")
        self.resize(1000, 700)

        self.create_central_widget()
        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_dock()

    # -------------------------
    # Central Widget
    # -------------------------

    def create_central_widget(self):

        central = QWidget()

        layout = QVBoxLayout(central)

        layout.addWidget(
            QLabel("Todo List")
        )

        self.setCentralWidget(central)

    # -------------------------
    # Actions
    # -------------------------

    def create_actions(self):

        self.new_action = QAction(
            "New",
            self,
        )

        self.open_action = QAction(
            "Open",
            self,
        )

        self.save_action = QAction(
            "Save",
            self,
        )

        self.exit_action = QAction(
            "Exit",
            self,
        )

        self.new_action.triggered.connect(
            self.new_todo
        )

        self.open_action.triggered.connect(
            self.open_file
        )

        self.save_action.triggered.connect(
            self.save_file
        )

        self.exit_action.triggered.connect(
            self.close
        )

    # -------------------------
    # Menu
    # -------------------------

    def create_menu(self):

        file_menu = self.menuBar().addMenu(
            "File"
        )

        file_menu.addAction(
            self.new_action
        )

        file_menu.addAction(
            self.open_action
        )

        file_menu.addAction(
            self.save_action
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.exit_action
        )

    # -------------------------
    # Toolbar
    # -------------------------

    def create_toolbar(self):

        toolbar = QToolBar(
            "Main Toolbar",
            self,
        )

        self.addToolBar(toolbar)

        toolbar.addAction(
            self.new_action
        )

        toolbar.addAction(
            self.open_action
        )

        toolbar.addAction(
            self.save_action
        )

    # -------------------------
    # StatusBar
    # -------------------------

    def create_statusbar(self):

        self.statusBar().showMessage(
            "Ready"
        )

    # -------------------------
    # Dock
    # -------------------------

    def create_dock(self):

        dock = QDockWidget(
            "Categories",
            self,
        )

        categories = QListWidget()

        categories.addItems([
            "All",
            "Work",
            "Personal",
        ])

        dock.setWidget(categories)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            dock,
        )

    # -------------------------
    # Actions
    # -------------------------

    def new_todo(self):

        self.statusBar().showMessage(
            "New Todo",
            3000,
        )

    def open_file(self):

        self.statusBar().showMessage(
            "Open",
            3000,
        )

    def save_file(self):

        self.statusBar().showMessage(
            "Saved",
            3000,
        )


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
```

---

# 31. Kiến trúc code này

Chúng ta đã bắt đầu có một cấu trúc tốt:

```text
MainWindow
│
├── create_central_widget()
│
├── create_actions()
│
├── create_menu()
│
├── create_toolbar()
│
├── create_statusbar()
│
└── create_dock()
```

Đây là một bước tiến rất lớn so với:

```python
def __init__(self):
    # 300 dòng code
```

---

# 32. Tại sao tạo `QAction` trước Menu/Toolbar?

Vì:

```text
Action
  ↓
Menu
  ↓
Toolbar
```

Action là **command**.

Menu và toolbar chỉ là **presentation/access point** của command.

Mental model:

```text
                   New Todo
                      │
                   QAction
                  /       \
                 /         \
             Menu          Toolbar
```

---

# 33. Đây chính là Command Pattern ở mức đơn giản

Ví dụ:

```python
self.new_action
```

đại diện cho:

> New Todo command.

Sau này command có thể được gọi từ:

```text
Menu
Toolbar
Keyboard shortcut
Context menu
```

mà không cần duplicate business logic.

---

# 34. Keyboard Shortcut

Có thể thêm:

```python
self.new_action.setShortcut("Ctrl+N")
```

Bây giờ:

```text
Menu → New
Toolbar → New
Ctrl+N
```

đều thực hiện cùng:

```python
self.new_todo()
```

Đây là sức mạnh của `QAction`.

---

# 35. Shortcut nên gắn vào Action

Không nên làm:

```text
Menu → function A
Toolbar → function A
Ctrl+N → function A
```

một cách riêng biệt.

Tốt hơn:

```text
                  QAction
                /    |    \
               /     |     \
            Menu  Toolbar  Shortcut
```

---

# 36. `setCentralWidget()` chỉ có một central widget

Bạn không thể làm:

```python
self.setCentralWidget(widget1)
self.setCentralWidget(widget2)
```

và mong cả hai cùng tồn tại.

Lần gọi sau sẽ thay thế central widget trước.

Nếu cần nhiều widget:

```text
QMainWindow
    ↓
Central QWidget
    ↓
Layout
    ├── Widget A
    ├── Widget B
    └── Widget C
```

---

# 37. Một Central Widget thường chứa cả một page

Ví dụ Todo App:

```text
QMainWindow
    │
    └── CentralWidget
          │
          └── QVBoxLayout
                ├── SearchBar
                ├── FilterBar
                └── TodoTable
```

Đây là kiến trúc thực tế hơn.

---

# 38. `QMainWindow` không phải Layout

Đây là lỗi beginner rất thường gặp.

Không nên:

```python
layout = QVBoxLayout(self)
```

với `self` là `QMainWindow`.

Thay vào đó:

```python
central = QWidget()

layout = QVBoxLayout(central)

self.setCentralWidget(central)
```

---

# 39. `QMainWindow` Architecture

Hãy ghi nhớ sơ đồ này:

```text
                       QMainWindow
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
    MenuBar              ToolBar             Dock Area
       │                    │                    │
    QAction              QAction            QDockWidget
       │
       │
       ▼
Central Widget
       │
       └── Layout
             ├── Search
             ├── Filter
             ├── Table
             └── Buttons

                       StatusBar
```

---

# 40. Bài tập 1 — Main Window cơ bản

Tạo:

```text
Todo App
```

với:

```text
MenuBar
    File
        New
        Exit

Toolbar
    New

StatusBar
    Ready

Central Widget
    QLabel("Todo List")
```

---

# 41. Bài tập 2 — QAction

Tạo các action:

```text
New
Edit
Delete
Refresh
```

Mỗi action có:

* text
* shortcut
* slot

Ví dụ:

```text
Ctrl+N → New
Ctrl+E → Edit
Delete → Delete
F5 → Refresh
```

---

# 42. Bài tập 3 — Dock

Tạo:

```text
Categories
```

với:

```text
All
Today
Work
Personal
Completed
```

Dock nằm bên trái.

Yêu cầu:

* movable
* floatable
* closable

---

# 43. Bài tập 4 — Shared QAction

Tạo:

```text
New Todo
```

Sau đó cho cùng một `QAction` xuất hiện ở:

```text
File → New Todo

Toolbar → New Todo
```

và:

```text
Ctrl+N
```

Tất cả phải gọi:

```python
new_todo()
```

---

# 44. Bài tập 5 — Todo Main Window

Xây giao diện:

```text
┌────────────────────────────────────────────────────┐
│ File   Edit   View   Help                          │
├────────────────────────────────────────────────────┤
│ [New] [Edit] [Delete] [Refresh]                   │
├───────────────┬────────────────────────────────────┤
│ Categories    │                                    │
│               │             Todo List              │
│ All           │                                    │
│ Today         │   ┌────────────────────────────┐   │
│ Work          │   │ Learn PySide6              │   │
│ Personal      │   │ Learn SQLite               │   │
│ Completed     │   │ Build Todo App             │   │
│               │   └────────────────────────────┘   │
├───────────────┴────────────────────────────────────┤
│ Ready                              3 todos         │
└────────────────────────────────────────────────────┘
```

Bạn **chưa cần database**.

Chỉ cần UI.

---

# 45. Bài tập Deep Dive

Sau khi làm xong Todo Main Window, hãy thử trả lời 5 câu này:

### Câu 1

Tại sao:

```python
QVBoxLayout(self)
```

không phải cách phù hợp cho `QMainWindow`?

### Câu 2

Tại sao nên tạo:

```python
QAction
```

rồi dùng nó cho cả Menu và Toolbar?

### Câu 3

Khác nhau giữa:

```python
dialog.show()
dialog.open()
dialog.exec()
```

là gì?

### Câu 4

Tại sao `QDockWidget` phù hợp cho:

```text
Project Explorer
Navigation
Inspector
```

nhưng không phù hợp cho nội dung chính?

### Câu 5

Tại sao `QMainWindow` chỉ có một `Central Widget`, và nếu muốn có nhiều widget trong vùng trung tâm thì phải dùng một container + layout?

Nếu bạn trả lời được 5 câu này thì phần **QMainWindow architecture** đã khá vững.

---

# 46. Chuẩn bị cho Buổi 10

Buổi tiếp theo chúng ta sẽ **không học thêm widget rời rạc**, mà bắt đầu ghép kiến thức thành một ứng dụng:

# Todo App v1

Kiến trúc dự kiến:

```text
Todo App v1
│
├── QMainWindow
│
├── MenuBar
│
├── ToolBar
│
├── StatusBar
│
├── Category Dock
│
├── Todo List
│
├── TodoDialog
│     ├── Create
│     └── Edit
│
├── Validation
│
└── In-memory Todo data
```

Flow chính:

```text
New Todo
   ↓
TodoDialog
   ↓
Validation
   ↓
Accepted
   ↓
Create Todo
   ↓
Update UI
   ↓
StatusBar
```

và:

```text
Select Todo
   ↓
Edit
   ↓
TodoDialog
   ↓
Validation
   ↓
Update Todo
   ↓
Refresh UI
```

**Buổi 10 sẽ là bài đầu tiên chúng ta bắt đầu tư duy như đang xây một ứng dụng PySide6 thật**, thay vì chỉ học từng widget riêng lẻ.
