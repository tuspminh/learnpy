# Buổi 10 - MenuBar, QAction, Shortcut và Context Menu (Chuyên nghiệp hóa ứng dụng)

Đến buổi này, ứng dụng của chúng ta đã có:

- ✅ MVC
- ✅ SQLite
- ✅ Repository
- ✅ Service
- ✅ Auto Save
- ✅ QListView + QAbstractListModel
- ✅ QStyledItemDelegate

Nhìn thì khá hoàn chỉnh.

Nhưng nếu để ý, nó vẫn thiếu rất nhiều thứ mà một phần mềm desktop chuyên nghiệp cần có.

Ví dụ Notepad++, VS Code hay Qt Creator đều có:

- Menu Bar
- Toolbar
- Shortcut
- Context Menu
- Action
- Undo / Redo
- Recent Files

Hôm nay chúng ta sẽ xây dựng nền tảng đó.

---

# Mục tiêu

Sau buổi này ứng dụng sẽ hỗ trợ:

```text-x-trilium-auto
File
    New Note        Ctrl+N

    Delete Note     Delete

    Exit            Ctrl+Q

Edit
    Undo            Ctrl+Z

    Redo            Ctrl+Y

    Search          Ctrl+F

Help
    About
```

Đồng thời khi click chuột phải vào ghi chú:

```text-x-trilium-auto
New Note

Rename

Delete

Copy Title
```

---

# QAction là gì?

Nhiều người mới học Qt thường viết:

```text-x-trilium-auto
button.clicked.connect(...)
```

Chỉ dùng được cho Button.

Nhưng nếu:

- Toolbar
- Menu
- Shortcut
- Context Menu

thì sao?

Qt giải quyết bằng QAction.

---

## Triết lý của QAction

Một hành động.

Có thể xuất hiện ở nhiều nơi.

Ví dụ

```text-x-trilium-auto
Delete
```

Có thể xuất hiện:

```text-x-trilium-auto
Menu

↓

Toolbar

↓

Context Menu

↓

Shortcut
```

Nhưng tất cả đều gọi

```text-x-trilium-auto
delete_note()
```

Chỉ một lần.

---

# Kiến trúc

```text-x-trilium-auto
QAction

↓

triggered

↓

Controller

↓

Service

↓

Repository

↓

SQLite
```

---

# Tạo Action

Trong MainWindow

```text-x-trilium-auto
from PySide6.QtGui import QAction
```

---

```text-x-trilium-auto
self.action_new = QAction("New Note", self)
```

---

Đặt shortcut

```text-x-trilium-auto
self.action_new.setShortcut(
    "Ctrl+N"
)
```

---

Tooltip

```text-x-trilium-auto
self.action_new.setStatusTip(
    "Create a new note"
)
```

---

# Menu

```text-x-trilium-auto
file_menu = self.menuBar().addMenu("File")
```

Thêm

```text-x-trilium-auto
file_menu.addAction(
    self.action_new
)
```

---

Toolbar

```text-x-trilium-auto
toolbar.addAction(
    self.action_new
)
```

Đã xong.

Một QAction.

Hai nơi.

---

# Controller

Kết nối

```text-x-trilium-auto
self.view.action_new.triggered.connect(

    self.create_note

)
```

Không cần biết

Menu

hay

Toolbar.

---

# Delete

```text-x-trilium-auto
self.action_delete = QAction(

    "Delete",

    self

)
```

Shortcut

```text-x-trilium-auto
self.action_delete.setShortcut(

    "Delete"

)
```

Controller

↓

```text-x-trilium-auto
triggered.connect(
    self.delete_note
)
```

---

# Exit

```text-x-trilium-auto
self.action_exit = QAction(
    "Exit",
    self
)
```

```text-x-trilium-auto
self.action_exit.setShortcut(
    "Ctrl+Q"
)
```

↓

```text-x-trilium-auto
triggered.connect(
    self.close
)
```

---

# Search

```text-x-trilium-auto
Ctrl+F
```

↓

Focus

```text-x-trilium-auto
search_edit
```

```text-x-trilium-auto
def focus_search(self):

    self.search_edit.setFocus()

    self.search_edit.selectAll()
```

---

# Context Menu

Chuột phải.

Trong LeftPanel

```text-x-trilium-auto
self.note_list.setContextMenuPolicy(

    Qt.CustomContextMenu

)
```

---

Signal

```text-x-trilium-auto
customContextMenuRequested
```

↓

```text-x-trilium-auto
show_context_menu()
```

---

```text-x-trilium-auto
from PySide6.QtWidgets import QMenu
```

---

```text-x-trilium-auto
menu = QMenu()
```

---

Thêm

```text-x-trilium-auto
menu.addAction(
    self.action_new
)
```

---

```text-x-trilium-auto
menu.addAction(
    self.action_delete
)
```

---

Hiện

```text-x-trilium-auto
menu.exec(
    self.note_list.mapToGlobal(pos)
)
```

Xong.

---

# Tại sao dùng QAction?

Nếu không.

Bạn sẽ viết

```text-x-trilium-auto
button.clicked
```

↓

```text-x-trilium-auto
menu.clicked
```

↓

```text-x-trilium-auto
shortcut
```

↓

```text-x-trilium-auto
context
```

Rất nhiều nơi.

QAction gom tất cả lại.

---

# Undo / Redo

Qt có

```text-x-trilium-auto
QUndoStack
```

Đây là một framework rất mạnh.

Ví dụ

```text-x-trilium-auto
Typing

↓

Undo

↓

Redo
```

---

Hiện tại

chúng ta chỉ tạo.

```text-x-trilium-auto
from PySide6.QtGui import QUndoStack
```

---

```text-x-trilium-auto
self.undo_stack = QUndoStack()
```

Buổi sau sẽ học kỹ.

---

# Recent Files

Nếu sau này

```text-x-trilium-auto
File

↓

Open
```

↓

Có thể lưu

```text-x-trilium-auto
Recent

↓

note1.db

↓

note2.db
```

QAction cũng dùng được.

---

# Tổ chức Action

Đừng viết

```text-x-trilium-auto
self.action_new

self.action_delete

self.action_search

self.action_exit
```

lung tung.

Hãy viết

```text-x-trilium-auto
create_actions()

create_menu()

create_toolbar()

connect_actions()
```

Ví dụ

```text-x-trilium-auto
def create_actions(self):

    ...

def create_menu(self):

    ...

def create_toolbar(self):

    ...

def connect_actions(self):

    ...
```

MainWindow sẽ rất sạch.

---

# MainWindow sau khi refactor

```text-x-trilium-auto
MainWindow

│

├── create_actions()

├── create_menu()

├── create_toolbar()

├── create_statusbar()

├── create_layout()

└── connect_actions()
```

Đây là phong cách chuyên nghiệp.

---

# Một lưu ý quan trọng

**Controller vẫn là nơi xử lý nghiệp vụ.**

MainWindow chỉ tạo `QAction` và phát tín hiệu.

Ví dụ:

```text-x-trilium-auto
Ctrl+N

↓

QAction

↓

Controller.create_note()

↓

Service

↓

Repository

↓

SQLite
```

MainWindow **không** tự tạo ghi chú.

---

# Cấu trúc dự án đến buổi 10

```text-x-trilium-auto
note_app/

├── database/
│      database.py
│
├── model/
│      note.py
│
├── repository/
│      note_repository.py
│
├── service/
│      note_service.py
│
├── controller/
│      note_controller.py
│
├── view/
│      main_window.py
│      left_panel.py
│      right_panel.py
│      note_delegate.py
│      note_list_model.py
│
├── resources/
│      icons/
│
└── main.py
```

Đây đã là cấu trúc của một dự án PySide6 tương đối chuyên nghiệp.

---

# Những gì còn thiếu?

Nếu so với một ứng dụng như Obsidian hay Notion, chúng ta vẫn còn nhiều tính năng:

- Markdown
- Tag
- Notebook
- Favorites
- Trash
- Export PDF
- Theme (Dark/Light)
- Settings
- Plugin
- Đồng bộ Cloud

Nhưng nền tảng kiến trúc đã sẵn sàng để bổ sung các tính năng này.

---

# Kiến thức mới hôm nay

Bạn đã học thêm nhiều thành phần quan trọng của Qt:

### 1. `QAction`

Đây là cách chuẩn để biểu diễn một hành động trong ứng dụng.

Một `QAction` có thể được sử dụng đồng thời trong:

- Menu
- Toolbar
- Context Menu
- Shortcut

mà vẫn chỉ gọi một hàm xử lý duy nhất.

---

### 2. Context Menu

`QMenu` kết hợp với `Qt.CustomContextMenu` giúp tạo menu chuột phải linh hoạt.

Điểm hay là bạn có thể **tái sử dụng cùng một** `**QAction**` đã có trong MenuBar hoặc Toolbar.

---

### 3. Tổ chức MainWindow

Thay vì viết mọi thứ trong `__init__()`, hãy chia nhỏ:

- `create_actions()`
- `create_menu()`
- `create_toolbar()`
- `create_layout()`
- `connect_actions()`

Điều này giúp mã nguồn dễ đọc và dễ bảo trì hơn rất nhiều.

---

# Dự án sẽ đi tiếp như thế nào?

Nếu tiếp tục mở rộng theo hướng **xây dựng một ứng dụng ghi chú hoàn chỉnh**, lộ trình hợp lý sẽ là:

| Buổi | Chủ đề |
| --- | --- |
| **11** | Áp dụng **Dependency Injection (DI)** và **Application Context** để giảm phụ thuộc giữa các lớp. |
| **12** | Thêm **Settings** (`QSettings`) để lưu kích thước cửa sổ, vị trí, theme và cấu hình người dùng. |
| **13** | Thiết kế **Theme Engine** (Dark/Light) bằng QSS. |
| **14** | Hỗ trợ **Markdown Preview** với `QWebEngineView`. |
| **15** | Thêm **Tag**, **Notebook** và mô hình dữ liệu mở rộng. |
| **16** | **Export PDF**, **Import/Export Markdown** và sao lưu dữ liệu. |
| **17** | Kiểm thử với `pytest`, logging và xử lý lỗi. |
| **18** | Đóng gói ứng dụng bằng `PyInstaller`, tạo file `.exe`/`.app`, tối ưu cấu trúc dự án và phát hành phiên bản đầu tiên. |

---

## Đánh giá kiến trúc hiện tại

Đến hết **buổi 10**, dự án của bạn đã có rất nhiều thành phần của một ứng dụng desktop chuyên nghiệp:

- ✔ Kiến trúc MVC rõ ràng.
- ✔ Repository Pattern và Service Layer.
- ✔ `QAbstractListModel` + `QListView`.
- ✔ `QStyledItemDelegate`.
- ✔ Auto Save với `QTimer`.
- ✔ `QAction`, Menu, Toolbar và Context Menu.
- ✔ SQLite được tách riêng khỏi giao diện.

Nếu chỉ dùng `QListWidget` và viết mọi thứ trong `MainWindow`, ứng dụng sẽ rất khó mở rộng. Kiến trúc hiện tại sẽ giúp bạn tiếp tục phát triển thêm nhiều tính năng mà không phải viết lại từ đầu. Đây cũng là hướng tổ chức mã nguồn thường thấy trong các dự án PySide6 quy mô vừa và lớn.
