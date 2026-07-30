# Buổi 2 - Thiết kế giao diện ứng dụng ghi chú

Ở buổi 1, chúng ta đã tạo được bộ khung của dự án.

Hôm nay chúng ta sẽ xây dựng giao diện hoàn chỉnh nhưng **chưa có chức năng**. Đây là cách làm chuyên nghiệp: thiết kế giao diện trước, sau đó mới kết nối dữ liệu và xử lý nghiệp vụ.

---

# Mục tiêu buổi học

Sau buổi này, giao diện sẽ giống như sau:

```text-x-trilium-auto
+-----------------------------------------------------------------------+
| File   Edit   Help                                         🔍 Search  |
+-----------------------------------------------------------------------+
| [+] [-] | Danh sách ghi chú | Tiêu đề                               |
|---------+-------------------+-----------------------------------------|
| Python  |                   |                                         |
| SQLite  |                   |                                         |
| MVC     |                   |                                         |
|---------|                   |                                         |
|         |                   |                                         |
|         |                   |                                         |
|         |                   |                                         |
|         |                   |             QTextEdit                   |
|         |                   |                                         |
|         |                   |                                         |
|         |                   |                                         |
+-----------------------------------------------------------------------+
| Ready                                                                 |
+-----------------------------------------------------------------------+
```

Chúng ta **chưa lưu SQLite**, chỉ tạo giao diện.

---

# Tư duy thiết kế

Một người mới thường tạo giao diện như sau:

```text-x-trilium-auto
layout.addWidget(button)
layout.addWidget(list)
layout.addWidget(textedit)
```

Dự án nhỏ thì được.

Dự án lớn sẽ rất khó quản lý.

Thay vào đó hãy chia giao diện thành nhiều phần.

```text-x-trilium-auto
MainWindow

│

├── Toolbar

├── Central Widget

│      │

│      ├── Left Panel

│      └── Right Panel

└── Status Bar
```

Sau này chỉ cần sửa từng panel.

---

# Bước 1: Cấu trúc Widget

```text-x-trilium-auto
QMainWindow

│

├── MenuBar

├── ToolBar

├── CentralWidget

│      │

│      └── QSplitter

│              │

│              ├── Left Panel

│              └── Right Panel

└── StatusBar
```

---

# Vì sao dùng QSplitter?

Nếu dùng `QHBoxLayout`

```text-x-trilium-auto
+---------+---------------------+
| Left    | Right               |
+---------+---------------------+
```

Người dùng **không kéo được**.

Nếu dùng `QSplitter`

```text-x-trilium-auto
+---------|---------------------+
          ↑

     kéo bằng chuột
```

Đây là widget rất phổ biến trong:

- VS Code
- Qt Creator
- Visual Studio
- Photoshop
- Blender

---

# Bước 2: Thiết kế Left Panel

Left Panel gồm:

```text-x-trilium-auto
+---------------------+

[ + ] [ - ]

----------------------

QListWidget

----------------------
```

Ở trên có hai nút:

- Thêm ghi chú
- Xóa ghi chú

Phía dưới là danh sách.

---

## Tạo class riêng

File:

```text-x-trilium-auto
view/left_panel.py
```

```text-x-trilium-auto
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget
)


class LeftPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()

        self.btn_add = QPushButton("+")

        self.btn_delete = QPushButton("-")

        button_layout.addWidget(self.btn_add)

        button_layout.addWidget(self.btn_delete)

        self.note_list = QListWidget()

        layout.addLayout(button_layout)

        layout.addWidget(self.note_list)
```

---

# Phân tích

Layout đang là:

```text-x-trilium-auto
QVBoxLayout

↓

QHBoxLayout

↓

QPushButton

↓

QPushButton

↓

QListWidget
```

Kết quả:

```text-x-trilium-auto
+------------------+

+ -

-------------------

QListWidget

-------------------
```

---

# Bước 3: Thiết kế Right Panel

File:

```text-x-trilium-auto
view/right_panel.py
```

```text-x-trilium-auto
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit
)


class RightPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Title"))

        self.title_edit = QLineEdit()

        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("Content"))

        self.content_edit = QTextEdit()

        layout.addWidget(self.content_edit)
```

---

## Giao diện

```text-x-trilium-auto
Title

+-------------------------+

QLineEdit

+-------------------------+

Content

+-------------------------+

QTextEdit

+-------------------------+
```

---

# Vì sao dùng QLineEdit?

Tiêu đề chỉ có một dòng.

Không nên dùng QTextEdit.

```text-x-trilium-auto
Title

Python MVC
```

---

# Vì sao dùng QTextEdit?

Nội dung có thể nhiều dòng.

Ví dụ:

```text-x-trilium-auto
Hôm nay học PySide6.

MVC rất quan trọng.

SQLite dễ dùng.
```

Đây là lý do dùng QTextEdit.

---

# Bước 4: Ghép bằng QSplitter

Quay lại:

```text-x-trilium-auto
view/main_window.py
```

```text-x-trilium-auto
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter
)

from PySide6.QtCore import Qt

from view.left_panel import LeftPanel from view.right_panel import RightPanel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Note")

        self.resize(1000, 650)

        splitter = QSplitter(Qt.Horizontal)

        self.left_panel = LeftPanel()

        self.right_panel = RightPanel()

        splitter.addWidget(self.left_panel)

        splitter.addWidget(self.right_panel)

        splitter.setSizes([250, 750])

        self.setCentralWidget(splitter)

        self.statusBar().showMessage("Ready")
```

---

# Kết quả

```text-x-trilium-auto
+----------+--------------------------------+

LeftPanel      RightPanel

+----------+--------------------------------+
```

Có thể kéo.

---

# setSizes()

```text-x-trilium-auto
splitter.setSizes([250,750])
```

Nghĩa là

```text-x-trilium-auto
250 pixel

↓

Left

750 pixel

↓

Right
```

---

# Bước 5: Thêm Toolbar

Trong `MainWindow`

```text-x-trilium-auto
from PySide6.QtWidgets import QToolBar
```

```text-x-trilium-auto
toolbar = QToolBar()

self.addToolBar(toolbar)
```

Sau này sẽ thêm

- New
- Delete
- Save

---

# Bước 6: Thêm Search

Trong toolbar

```text-x-trilium-auto
from PySide6.QtWidgets import QLineEdit
```

```text-x-trilium-auto
search = QLineEdit()

search.setPlaceholderText("Search...")

toolbar.addWidget(search)
```

---

# Bước 7: Thêm Menu

```text-x-trilium-auto
menu = self.menuBar()

file_menu = menu.addMenu("File")

edit_menu = menu.addMenu("Edit")

help_menu = menu.addMenu("Help")
```

Đây là khung để sau này thêm các `QAction`.

---

# Bước 8: Đặt ObjectName

Một thói quen rất tốt là đặt tên cho các widget.

Ví dụ:

```text-x-trilium-auto
self.title_edit.setObjectName("titleEdit")
```

```text-x-trilium-auto
self.content_edit.setObjectName("contentEdit")
```

```text-x-trilium-auto
self.note_list.setObjectName("noteList")
```

Lợi ích:

- Dễ áp dụng QSS (Qt Style Sheet).
- Dễ tìm widget khi debug.
- Tên rõ ràng khi dự án lớn.

---

# Cấu trúc giao diện sau buổi 2

```text-x-trilium-auto
MainWindow

│

├── MenuBar

│

├── ToolBar

│      └── Search

│

├── CentralWidget

│      │

│      └── QSplitter

│              │

│              ├── LeftPanel
│              │      │
│              │      ├── +
│              │      ├── -
│              │      └── QListWidget
│              │
│              └── RightPanel
│                     │
│                     ├── QLabel
│                     ├── QLineEdit
│                     ├── QLabel
│                     └── QTextEdit
│

└── StatusBar
```

---

# Những điều chưa làm

Hiện tại:

❌ Chưa lưu SQLite.

❌ Chưa có Model.

❌ Chưa có Controller.

❌ Chưa có CRUD.

❌ Chưa có Auto Save.

Điều này là **chủ đích**. Chúng ta đang xây dựng từng lớp của ứng dụng một cách tách biệt để dễ hiểu và dễ mở rộng.

---

# Bài tập thực hành

1. Thêm nút **Save** vào `QToolBar`.
2. Thêm `QLabel` hiển thị số lượng ghi chú ở cuối `LeftPanel` (ví dụ: `Notes: 0`).
3. Đặt placeholder cho:
  - `title_edit`: `"Enter note title..."`
  - `content_edit`: `"Write your note here..."`
4. Đặt kích thước tối thiểu (`setMinimumWidth`) cho `LeftPanel` là **220 px**.
5. Thử áp dụng một `QSS` đơn giản để đổi màu nền của `QListWidget` và tăng khoảng cách (`padding`) cho `QLineEdit`.

---

# Buổi 3 (Preview)

Ở buổi tiếp theo, chúng ta sẽ bắt đầu phần **Model** bằng cách xây dựng lớp `Database` hoàn chỉnh:

- Tách riêng lớp quản lý kết nối SQLite.
- Thiết kế lớp `Note` (Data Model).
- Viết các hàm CRUD đầu tiên.
- Hiểu vì sao Model **không được** phụ thuộc vào PySide6.

Từ buổi 3 trở đi, ứng dụng sẽ bắt đầu có dữ liệu thật và từng bước trở thành một ứng dụng ghi chú hoàn chỉnh.
