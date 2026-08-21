  # Buổi 10 — Mini Project: Todo App v1

Hôm nay chúng ta **khép lại Phần I** bằng một project nhỏ nhưng rất quan trọng: xây dựng **Todo App v1**.

Mục tiêu không phải tạo một app hoàn chỉnh, mà là **ghép những kiến thức từ Buổi 1 → 9 thành một ứng dụng có cấu trúc**.

Sau buổi này, chúng ta sẽ chuyển sang **Phần II — Qt Model/View**, nơi cách quản lý dữ liệu trong PySide6 sẽ thay đổi đáng kể.

---

# 1. Mục tiêu Todo App v1

Ứng dụng có:

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
├── Add Todo Dialog
│
├── Edit Todo Dialog
│
├── Delete Todo
│
└── In-memory data
```

UI:

```text
┌──────────────────────────────────────────────────────┐
│ File        Todo        View                         │
├──────────────────────────────────────────────────────┤
│ [New] [Edit] [Delete] [Complete]                   │
├───────────────┬──────────────────────────────────────┤
│ Categories    │                                      │
│               │  Todo List                           │
│ All           │                                      │
│ Active        │  ☐ Learn Python                      │
│ Completed     │  ☐ Learn PySide6                    │
│               │  ☑ Build Todo App                   │
│               │                                      │
├───────────────┴──────────────────────────────────────┤
│ Ready                                  3 todos       │
└──────────────────────────────────────────────────────┘
```

---

# 2. Trước tiên: thiết kế dữ liệu

Chưa dùng SQLite.

Chúng ta dùng Python list:

```python
todos = []
```

Một Todo:

```python
{
    "id": 1,
    "title": "Learn PySide6",
    "description": "Study QMainWindow",
    "completed": False,
}
```

Ví dụ:

```python
todos = [
    {
        "id": 1,
        "title": "Learn Python",
        "description": "Review OOP",
        "completed": True,
    },
    {
        "id": 2,
        "title": "Learn PySide6",
        "description": "Study Model/View",
        "completed": False,
    },
]
```

---

# 3. Tại sao cần `id`?

Không nên xác định Todo bằng:

```python
title
```

Ví dụ:

```text
Learn Python
Learn Python
```

có thể xuất hiện hai lần.

`id` phải unique:

```text
1 → Learn Python
2 → Learn Python
3 → Learn Rust
```

Sau này khi có database:

```text
Todo.id
```

sẽ tương ứng rất tự nhiên với:

```text
PRIMARY KEY
```

---

# 4. Tạo `Todo` bằng dataclass

Thay vì dictionary, chúng ta có thể dùng:

```python
from dataclasses import dataclass
```

```python
@dataclass
class Todo:
    id: int
    title: str
    description: str
    completed: bool = False
```

Sau đó:

```python
todo = Todo(
    id=1,
    title="Learn PySide6",
    description="Study Model/View",
)
```

Đây là cách tôi khuyến nghị cho project.

---

# 5. Todo Repository đơn giản

Chưa cần database, nhưng chúng ta **không nên nhét tất cả dữ liệu vào MainWindow**.

Tạo:

```python
class TodoRepository:
    ...
```

Nó quản lý:

```text
TodoRepository
│
├── add()
├── get_all()
├── get()
├── update()
├── delete()
└── toggle_completed()
```

---

# 6. Repository v1

```python
class TodoRepository:

    def __init__(self):
        self._todos = []
        self._next_id = 1

    def add(self, title, description):
        todo = Todo(
            id=self._next_id,
            title=title,
            description=description,
        )

        self._next_id += 1
        self._todos.append(todo)

        return todo

    def get_all(self):
        return list(self._todos)

    def get(self, todo_id):
        for todo in self._todos:
            if todo.id == todo_id:
                return todo

        return None

    def update(self, todo_id, title, description):

        todo = self.get(todo_id)

        if todo is None:
            return None

        todo.title = title
        todo.description = description

        return todo

    def delete(self, todo_id):

        todo = self.get(todo_id)

        if todo is None:
            return False

        self._todos.remove(todo)

        return True

    def toggle_completed(self, todo_id):

        todo = self.get(todo_id)

        if todo is None:
            return None

        todo.completed = not todo.completed

        return todo
```

---

# 7. Tại sao tạo Repository ngay từ v1?

Ta có:

```text
MainWindow
    ↓
TodoRepository
```

thay vì:

```text
MainWindow
    ↓
self.todos
```

Repository giúp MainWindow không cần biết dữ liệu được lưu ở đâu.

Hôm nay:

```text
Repository
    ↓
list
```

Sau này:

```text
Repository
    ↓
SQLite
```

hoặc:

```text
Repository
    ↓
PostgreSQL
```

UI không nhất thiết phải thay đổi.

Đây là tư duy kiến trúc rất quan trọng.

---

# 8. TodoDialog

Dialog dùng để:

```text
Create
Edit
```

Code:

```python
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)
```

```python
class TodoDialog(QDialog):

    def __init__(self, todo=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Edit Todo" if todo else "New Todo"
        )

        self.title_edit = QLineEdit()

        self.description_edit = QPlainTextEdit()

        form = QFormLayout()

        form.addRow(
            "Title:",
            self.title_edit,
        )

        form.addRow(
            "Description:",
            self.description_edit,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.validate_and_accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)
        layout.addWidget(buttons)

        if todo:
            self.title_edit.setText(
                todo.title
            )

            self.description_edit.setPlainText(
                todo.description
            )

    def validate_and_accept(self):

        title = self.title_edit.text().strip()

        if not title:
            self.title_edit.setFocus()
            return

        self.accept()

    def get_data(self):

        return {
            "title": self.title_edit.text().strip(),
            "description": (
                self.description_edit
                .toPlainText()
                .strip()
            ),
        }
```

---

# 9. Todo List

Ở Todo App v1, chúng ta **chưa học Model/View**.

Do đó có thể dùng:

```python
QListWidget
```

Import:

```python
from PySide6.QtWidgets import QListWidget
```

Đây là một bước có chủ đích.

Buổi 11 trở đi chúng ta sẽ thay:

```text
QListWidget
```

bằng:

```text
QListView
+
QAbstractListModel
```

để hiểu Model/View thực sự.

---

# 10. Hiển thị Todo

Ta có:

```python
self.todo_list = QListWidget()
```

Sau đó:

```python
for todo in self.repository.get_all():

    text = todo.title

    if todo.completed:
        text = "✓ " + text
    else:
        text = "☐ " + text

    self.todo_list.addItem(text)
```

---

# 11. Nhưng có một vấn đề

Nếu user click:

```text
Learn PySide6
```

làm sao biết Todo nào?

Ta có thể lưu ID vào item:

```python
item.setData(
    Qt.ItemDataRole.UserRole,
    todo.id,
)
```

Đây là một chi tiết rất đáng chú ý.

---

# 12. `UserRole`

Ở v1, bạn có thể dùng:

```python
Qt.ItemDataRole.UserRole
```

để lưu ID:

```python
item.setData(
    Qt.ItemDataRole.UserRole,
    todo.id,
)
```

Lấy lại:

```python
todo_id = item.data(
    Qt.ItemDataRole.UserRole
)
```

Bạn vừa chạm vào một khái niệm mà **Buổi 19 — Roles** sẽ đào sâu.

---

# 13. MainWindow

Bây giờ bắt đầu ghép.

```python
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo App v1")
        self.resize(1000, 700)

        self.repository = TodoRepository()

        self.create_central_widget()
        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_dock()

        self.refresh_todos()
```

---

# 14. Central Widget

```python
def create_central_widget(self):

    self.todo_list = QListWidget()

    self.todo_list.itemDoubleClicked.connect(
        self.edit_todo
    )

    self.setCentralWidget(
        self.todo_list
    )
```

Bây giờ vùng trung tâm là:

```text
┌──────────────────────────────┐
│ Todo List                    │
│                              │
│ ☐ Learn Python               │
│ ☐ Learn PySide6              │
│ ✓ Build Application          │
│                              │
└──────────────────────────────┘
```

---

# 15. Actions

```python
def create_actions(self):

    self.new_action = QAction(
        "New",
        self,
    )
    self.new_action.setShortcut("Ctrl+N")

    self.edit_action = QAction(
        "Edit",
        self,
    )
    self.edit_action.setShortcut("Ctrl+E")

    self.delete_action = QAction(
        "Delete",
        self,
    )
    self.delete_action.setShortcut("Delete")

    self.complete_action = QAction(
        "Complete",
        self,
    )
    self.complete_action.setShortcut("Ctrl+D")

    self.new_action.triggered.connect(
        self.new_todo
    )

    self.edit_action.triggered.connect(
        self.edit_todo
    )

    self.delete_action.triggered.connect(
        self.delete_todo
    )

    self.complete_action.triggered.connect(
        self.toggle_completed
    )
```

---

# 16. Menu

```python
def create_menu(self):

    file_menu = self.menuBar().addMenu(
        "File"
    )

    file_menu.addAction(
        self.new_action
    )

    file_menu.addSeparator()

    exit_action = QAction(
        "Exit",
        self,
    )

    exit_action.triggered.connect(
        self.close
    )

    file_menu.addAction(
        exit_action
    )

    todo_menu = self.menuBar().addMenu(
        "Todo"
    )

    todo_menu.addAction(
        self.new_action
    )

    todo_menu.addAction(
        self.edit_action
    )

    todo_menu.addAction(
        self.delete_action
    )

    todo_menu.addAction(
        self.complete_action
    )
```

---

# 17. Toolbar

```python
def create_toolbar(self):

    toolbar = QToolBar(
        "Todo Toolbar",
        self,
    )

    self.addToolBar(toolbar)

    toolbar.addAction(
        self.new_action
    )

    toolbar.addAction(
        self.edit_action
    )

    toolbar.addAction(
        self.delete_action
    )

    toolbar.addAction(
        self.complete_action
    )
```

Một `QAction` được dùng ở nhiều nơi:

```text
             QAction
           /    |     \
          /     |      \
       Menu  Toolbar  Shortcut
```

Đây chính là pattern chúng ta học ở Buổi 9.

---

# 18. StatusBar

```python
def create_statusbar(self):

    self.statusBar().showMessage(
        "Ready"
    )
```

Sau khi refresh:

```python
self.statusBar().showMessage(
    f"{len(todos)} todos"
)
```

---

# 19. Category Dock

Ở v1 ta chưa cần filter thật sự.

Tạo:

```python
def create_dock(self):

    dock = QDockWidget(
        "Categories",
        self,
    )

    categories = QListWidget()

    categories.addItems([
        "All",
        "Active",
        "Completed",
    ])

    dock.setWidget(categories)

    self.addDockWidget(
        Qt.DockWidgetArea.LeftDockWidgetArea,
        dock,
    )
```

Filter thật sẽ được làm tốt hơn ở:

```text
Buổi 21 — Sorting & Filtering
Buổi 22 — Proxy Model
```

---

# 20. `refresh_todos()`

Đây là method quan trọng.

```python
def refresh_todos(self):

    self.todo_list.clear()

    todos = self.repository.get_all()

    for todo in todos:

        prefix = (
            "✓ "
            if todo.completed
            else "☐ "
        )

        item = QListWidgetItem(
            prefix + todo.title
        )

        item.setData(
            Qt.ItemDataRole.UserRole,
            todo.id,
        )

        self.todo_list.addItem(item)

    self.statusBar().showMessage(
        f"{len(todos)} todos"
    )
```

---

# 21. Tư duy `refresh`

Một pattern quan trọng:

```text
Data changes
     ↓
refresh UI
```

Ví dụ:

```text
Add
 ↓
Repository changes
 ↓
refresh_todos()
```

Edit:

```text
Edit
 ↓
Repository changes
 ↓
refresh_todos()
```

Delete:

```text
Delete
 ↓
Repository changes
 ↓
refresh_todos()
```

---

# 22. `new_todo()`

```python
def new_todo(self):

    dialog = TodoDialog(
        parent=self
    )

    result = dialog.exec()

    if result != QDialog.DialogCode.Accepted:
        return

    data = dialog.get_data()

    self.repository.add(
        title=data["title"],
        description=data["description"],
    )

    self.refresh_todos()
```

Flow:

```text
New
 ↓
TodoDialog
 ↓
Validation
 ↓
Accepted
 ↓
get_data()
 ↓
Repository.add()
 ↓
refresh_todos()
```

Đây là flow rất quan trọng.

---

# 23. Lấy Todo đang chọn

Ta tạo helper:

```python
def get_selected_todo(self):

    item = self.todo_list.currentItem()

    if item is None:
        return None

    todo_id = item.data(
        Qt.ItemDataRole.UserRole
    )

    return self.repository.get(todo_id)
```

Bây giờ các action khác không cần biết UI internals.

---

# 24. `edit_todo()`

```python
def edit_todo(self):

    todo = self.get_selected_todo()

    if todo is None:
        return

    dialog = TodoDialog(
        todo=todo,
        parent=self,
    )

    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    data = dialog.get_data()

    self.repository.update(
        todo.id,
        data["title"],
        data["description"],
    )

    self.refresh_todos()
```

---

# 25. `delete_todo()`

Không nên delete ngay.

Hỏi user:

```python
def delete_todo(self):

    todo = self.get_selected_todo()

    if todo is None:
        return

    result = QMessageBox.question(
        self,
        "Delete Todo",
        f'Delete "{todo.title}"?',
        QMessageBox.StandardButton.Yes
        | QMessageBox.StandardButton.No,
    )

    if result != QMessageBox.StandardButton.Yes:
        return

    self.repository.delete(
        todo.id
    )

    self.refresh_todos()
```

Flow:

```text
Delete
 ↓
Get selected
 ↓
QMessageBox
 ↓
Yes?
 ↓
Repository.delete()
 ↓
refresh
```

---

# 26. `toggle_completed()`

```python
def toggle_completed(self):

    todo = self.get_selected_todo()

    if todo is None:
        return

    self.repository.toggle_completed(
        todo.id
    )

    self.refresh_todos()
```

---

# 27. Code hoàn chỉnh Todo App v1

Đây là phiên bản bạn nên tự gõ lại thay vì copy-paste.

```python
import sys

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFormLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QToolBar,
    QVBoxLayout,
)


@dataclass
class Todo:

    id: int
    title: str
    description: str
    completed: bool = False


class TodoRepository:

    def __init__(self):

        self._todos = []
        self._next_id = 1

    def add(self, title, description):

        todo = Todo(
            id=self._next_id,
            title=title,
            description=description,
        )

        self._next_id += 1

        self._todos.append(todo)

        return todo

    def get_all(self):

        return list(self._todos)

    def get(self, todo_id):

        for todo in self._todos:

            if todo.id == todo_id:
                return todo

        return None

    def update(
        self,
        todo_id,
        title,
        description,
    ):

        todo = self.get(todo_id)

        if todo is None:
            return None

        todo.title = title
        todo.description = description

        return todo

    def delete(self, todo_id):

        todo = self.get(todo_id)

        if todo is None:
            return False

        self._todos.remove(todo)

        return True

    def toggle_completed(self, todo_id):

        todo = self.get(todo_id)

        if todo is None:
            return None

        todo.completed = not todo.completed

        return todo


class TodoDialog(QDialog):

    def __init__(
        self,
        todo=None,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Edit Todo"
            if todo
            else "New Todo"
        )

        self.title_edit = QLineEdit()

        self.description_edit = QPlainTextEdit()

        form = QFormLayout()

        form.addRow(
            "Title:",
            self.title_edit,
        )

        form.addRow(
            "Description:",
            self.description_edit,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.validate_and_accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)

        layout.addWidget(buttons)

        if todo:

            self.title_edit.setText(
                todo.title
            )

            self.description_edit.setPlainText(
                todo.description
            )

    def validate_and_accept(self):

        title = self.title_edit.text().strip()

        if not title:

            self.title_edit.setFocus()

            return

        self.accept()

    def get_data(self):

        return {
            "title": (
                self.title_edit
                .text()
                .strip()
            ),
            "description": (
                self.description_edit
                .toPlainText()
                .strip()
            ),
        }


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Todo App v1"
        )

        self.resize(1000, 700)

        self.repository = TodoRepository()

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

        self.todo_list = QListWidget()

        self.todo_list.itemDoubleClicked.connect(
            self.edit_todo
        )

        self.setCentralWidget(
            self.todo_list
        )

    # -------------------------
    # Actions
    # -------------------------

    def create_actions(self):

        self.new_action = QAction(
            "New",
            self,
        )

        self.new_action.setShortcut(
            "Ctrl+N"
        )

        self.edit_action = QAction(
            "Edit",
            self,
        )

        self.edit_action.setShortcut(
            "Ctrl+E"
        )

        self.delete_action = QAction(
            "Delete",
            self,
        )

        self.delete_action.setShortcut(
            "Delete"
        )

        self.complete_action = QAction(
            "Complete",
            self,
        )

        self.complete_action.setShortcut(
            "Ctrl+D"
        )

        self.new_action.triggered.connect(
            self.new_todo
        )

        self.edit_action.triggered.connect(
            self.edit_todo
        )

        self.delete_action.triggered.connect(
            self.delete_todo
        )

        self.complete_action.triggered.connect(
            self.toggle_completed
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

        file_menu.addSeparator()

        exit_action = QAction(
            "Exit",
            self,
        )

        exit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(
            exit_action
        )

        todo_menu = self.menuBar().addMenu(
            "Todo"
        )

        todo_menu.addAction(
            self.new_action
        )

        todo_menu.addAction(
            self.edit_action
        )

        todo_menu.addAction(
            self.delete_action
        )

        todo_menu.addAction(
            self.complete_action
        )

    # -------------------------
    # Toolbar
    # -------------------------

    def create_toolbar(self):

        toolbar = QToolBar(
            "Todo Toolbar",
            self,
        )

        self.addToolBar(toolbar)

        toolbar.addAction(
            self.new_action
        )

        toolbar.addAction(
            self.edit_action
        )

        toolbar.addAction(
            self.delete_action
        )

        toolbar.addAction(
            self.complete_action
        )

    # -------------------------
    # Status Bar
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
            "Active",
            "Completed",
        ])

        dock.setWidget(categories)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            dock,
        )

    # -------------------------
    # Todo UI
    # -------------------------

    def refresh_todos(self):

        self.todo_list.clear()

        todos = self.repository.get_all()

        for todo in todos:

            prefix = (
                "✓ "
                if todo.completed
                else "☐ "
            )

            item = QListWidgetItem(
                prefix + todo.title
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                todo.id,
            )

            self.todo_list.addItem(item)

        self.statusBar().showMessage(
            f"{len(todos)} todos"
        )

    # -------------------------
    # Helpers
    # -------------------------

    def get_selected_todo(self):

        item = self.todo_list.currentItem()

        if item is None:
            return None

        todo_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        return self.repository.get(
            todo_id
        )

    # -------------------------
    # Commands
    # -------------------------

    def new_todo(self):

        dialog = TodoDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        self.repository.add(
            data["title"],
            data["description"],
        )

        self.refresh_todos()

    def edit_todo(self):

        todo = self.get_selected_todo()

        if todo is None:
            return

        dialog = TodoDialog(
            todo=todo,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        self.repository.update(
            todo.id,
            data["title"],
            data["description"],
        )

        self.refresh_todos()

    def delete_todo(self):

        todo = self.get_selected_todo()

        if todo is None:
            return

        result = QMessageBox.question(
            self,
            "Delete Todo",
            f'Delete "{todo.title}"?',
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            result
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.repository.delete(
            todo.id
        )

        self.refresh_todos()

    def toggle_completed(self):

        todo = self.get_selected_todo()

        if todo is None:
            return

        self.repository.toggle_completed(
            todo.id
        )

        self.refresh_todos()


def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

# 28. Nhưng hãy chú ý: đây chưa phải kiến trúc "chuyên nghiệp"

Todo App v1 cố tình sử dụng:

```text
QListWidget
```

và:

```text
refresh_todos()
```

mỗi khi dữ liệu thay đổi.

Ví dụ:

```text
TodoRepository
     ↓
data changed
     ↓
refresh_todos()
     ↓
QListWidget.clear()
     ↓
addItem(...)
     ↓
render lại toàn bộ
```

Với 5 Todo:

```text
OK
```

Với 10.000 Todo:

```text
Không lý tưởng
```

Đây chính là lý do chúng ta cần:

# Qt Model/View

---

# 29. Vấn đề của `QListWidget`

`QListWidget` là dạng **convenience widget**.

Nó kết hợp:

```text
Data
+
Model
+
View
```

vào một abstraction dễ sử dụng.

Mental model:

```text
QListWidget
    │
    ├── data
    ├── model
    └── view
```

Điều này rất tiện cho app nhỏ.

Nhưng khi app lớn:

```text
Data
Business Logic
UI
```

nên tách rõ.

---

# 30. Model/View sẽ thay đổi kiến trúc

Hiện tại:

```text
Repository
     ↓
refresh_todos()
     ↓
QListWidget
```

Sau này:

```text
Repository
     ↓
Model
     ↓
QListView
```

Ví dụ:

```text
TodoRepository
       │
       ↓
TodoListModel
       │
       ↓
    QListView
```

Khi dữ liệu thay đổi:

```text
Model
 ↓
signals
 ↓
View tự cập nhật
```

Không cần:

```python
clear()
addItem()
clear()
addItem()
clear()
addItem()
```

---

# 31. Đây là điểm chuyển giao quan trọng

Phần I:

```text
Widgets
Dialogs
Signals
Layouts
MainWindow
```

mục tiêu:

> **Biết xây một GUI chạy được.**

Phần II:

```text
Model
View
Delegate
Proxy
Selection
Roles
Index
```

mục tiêu:

> **Biết xây GUI quản lý dữ liệu đúng kiến trúc Qt.**

---

# 32. Bài tập bắt buộc

Trước khi sang Buổi 11, hãy tự xây lại Todo App v1 mà **không nhìn code mẫu**.

Yêu cầu tối thiểu:

### Data

```text
Todo
├── id
├── title
├── description
└── completed
```

### Repository

```text
TodoRepository
├── add
├── get
├── get_all
├── update
├── delete
└── toggle_completed
```

### MainWindow

```text
QMainWindow
├── MenuBar
├── ToolBar
├── StatusBar
├── Central Widget
└── Dock Widget
```

### Operations

```text
New
Edit
Delete
Complete
```

### Dialog

```text
TodoDialog
├── title
├── description
├── validation
└── get_data()
```

---

# 33. Bài tập nâng cao

Thêm:

### 1. Disable Edit/Delete nếu chưa chọn Todo

```text
Không chọn:
[New] [Edit disabled] [Delete disabled]

Chọn Todo:
[New] [Edit] [Delete]
```

Gợi ý:

```python
self.todo_list.itemSelectionChanged.connect(
    self.update_actions
)
```

---

### 2. Context Menu

Click chuột phải:

```text
┌─────────────────┐
│ Edit             │
│ Complete         │
│ Delete           │
└─────────────────┘
```

Bạn sẽ bắt đầu làm quen với:

```python
setContextMenuPolicy()
```

và:

```python
customContextMenuRequested
```

---

### 3. Double-click

Đã có:

```python
self.todo_list.itemDoubleClicked.connect(
    self.edit_todo
)
```

Thử thêm:

```text
Double-click Todo
        ↓
Edit Dialog
```

---

### 4. Empty state

Nếu không có Todo:

```text
┌──────────────────────────────┐
│                              │
│        No todos yet          │
│                              │
│       [+ Create Todo]        │
│                              │
└──────────────────────────────┘
```

Đây là bài tập rất tốt về UI state.

---

# 34. Kiến trúc sau Buổi 10

Bạn đã đi từ:

```text
Python
 ↓
QApplication
 ↓
QWidget
 ↓
Layout
 ↓
Signal / Slot
 ↓
Input
 ↓
Validation
 ↓
Dialog
 ↓
QMainWindow
 ↓
Mini Application
```

Và bây giờ chúng ta sẵn sàng bước sang một khái niệm **cốt lõi của Qt**:

```text
              Model
             /     \
            /       \
       Data          View
                       │
                    Delegate
```

---

# Phần II — Qt Model/View

## Buổi 11 — Model/View Architecture

Đây sẽ là một buổi **rất quan trọng**, không chỉ học API mà sẽ giải thích:

```text
Model là gì?
View là gì?
Delegate là gì?
```

và quan trọng nhất:

```text
Tại sao Qt không muốn bạn nhét data trực tiếp
vào QListWidget/QTableWidget khi ứng dụng lớn?
```

Sau đó chúng ta sẽ **refactor Todo App v1** theo hướng:

```text
TodoRepository
      ↓
TodoListModel
      ↓
QListView
```

Đây mới là bước đầu tiên để chuyển từ **PySide6 beginner → PySide6 developer có kiến trúc tốt**.
