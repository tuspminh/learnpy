# 🚀 Buổi 24 — Mini Project: File Explorer

Hôm nay chúng ta tổng hợp toàn bộ **Qt Model/View** đã học từ Buổi 11 → 23 để xây một **File Explorer v1**.

Mục tiêu không phải làm một Windows Explorer hoàn chỉnh, mà là hiểu cách các thành phần Model/View phối hợp trong một ứng dụng thực tế.

---

# 1. Mục tiêu

Chúng ta sẽ xây UI:

```text
┌─────────────────────────────────────────────────────────┐
│ File Explorer                                           │
├──────────────────────┬──────────────────────────────────┤
│ Folders              │ Files                            │
│                      │                                  │
│ 📁 Documents         │ 📄 report.pdf                    │
│ 📁 Downloads         │ 📄 notes.txt                     │
│ 📁 Pictures          │ 🖼 image.png                     │
│ 📁 Projects          │ 🐍 main.py                       │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│ Ready                                                  │
└─────────────────────────────────────────────────────────┘
```

Có:

* `QTreeView`
* `QTableView`
* `QFileSystemModel`
* `QSortFilterProxyModel`
* `QItemSelectionModel`
* `QSplitter`
* `QLineEdit`
* Context Menu
* Double-click
* StatusBar

---

# 2. Kiến trúc

Đây là kiến trúc chính:

```text
                 File Explorer
                       │
              ┌────────┴────────┐
              │                 │
          Folder Tree       File Table
              │                 │
         QTreeView          QTableView
              │                 │
       QFileSystemModel   QFileSystemModel
              │                 │
              └────────┬────────┘
                       │
                  Proxy Model
                       │
                Selection Model
```

Nhưng thực tế ta sẽ dùng **hai view trên cùng một filesystem model**.

---

# 3. `QFileSystemModel`

PySide6 đã cung cấp Model chuyên dùng để biểu diễn filesystem:

```python
from PySide6.QtWidgets import QFileSystemModel
```

Model này có thể biểu diễn:

```text
/
├── home
├── tmp
├── usr
├── etc
└── ...
```

hoặc trên Windows:

```text
C:\
├── Users
├── Windows
├── Program Files
└── ...
```

---

# 4. Tại sao không tự viết File Model?

Bạn hoàn toàn có thể tự viết:

```python
class FileSystemModel(QAbstractItemModel):
    ...
```

nhưng filesystem có:

* directory
* file
* permissions
* size
* modified time
* icon
* hierarchy
* lazy loading

Qt đã giải quyết phần này.

Vì vậy:

> Với File Explorer, trước tiên hãy học cách sử dụng `QFileSystemModel`.

---

# 5. Import

```python
import sys

from PySide6.QtCore import (
    Qt,
    QDir,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileSystemModel,
    QTreeView,
    QTableView,
    QSplitter,
    QLineEdit,
    QWidget,
    QVBoxLayout,
)
```

---

# 6. Khởi tạo Model

```python
self.model = QFileSystemModel()
```

Sau đó:

```python
self.model.setRootPath(
    QDir.rootPath()
)
```

`QDir.rootPath()` trả về root filesystem phù hợp với hệ điều hành.

---

# 7. Tree View

Tạo:

```python
self.tree = QTreeView()
```

Gắn Model:

```python
self.tree.setModel(
    self.model
)
```

---

# 8. Table View

```python
self.table = QTableView()
```

Gắn cùng Model:

```python
self.table.setModel(
    self.model
)
```

Bây giờ:

```text
QFileSystemModel
       │
   ┌───┴────┐
   ↓        ↓
 Tree     Table
```

---

# 9. Nhưng Table không nên hiển thị toàn bộ filesystem

Đây là điểm quan trọng.

Tree cần:

```text
folder hierarchy
```

Table cần:

```text
contents of selected folder
```

Do đó chúng ta dùng:

```python
root_index = self.model.index(
    QDir.rootPath()
)
```

Tree:

```python
self.tree.setRootIndex(
    root_index
)
```

Table cũng có thể thay đổi `rootIndex()` theo folder đang chọn.

---

# 10. Root Index là gì?

Model chứa:

```text
/
├── home
├── tmp
├── usr
```

Nhưng View có thể nói:

```text
"Hiển thị từ node này"
```

Ví dụ:

```python
index = self.model.index(
    "/home/user/Documents"
)
```

rồi:

```python
self.table.setRootIndex(index)
```

Table sẽ hiển thị:

```text
report.pdf
notes.txt
project/
```

thay vì toàn bộ filesystem.

---

# 11. Kiến trúc Master → Detail

File Explorer chính là ví dụ hoàn hảo của:

```text
Master
  ↓
Folder Tree

Detail
  ↓
Files
```

Flow:

```text
User click folder
       ↓
QTreeView
       ↓
Selection Model
       ↓
QModelIndex
       ↓
QTableView.setRootIndex()
       ↓
Folder contents
```

---

# 12. Lấy Selection Model

```python
selection_model = (
    self.tree.selectionModel()
)
```

Kết nối:

```python
selection_model.currentChanged.connect(
    self.on_folder_changed
)
```

---

# 13. `on_folder_changed`

```python
def on_folder_changed(
    self,
    current,
    previous,
):
    if not current.isValid():
        return

    self.table.setRootIndex(
        current
    )
```

Đây là core của File Explorer.

---

# 14. Nhưng phải kiểm tra Directory

User có thể chọn file.

Do đó:

```python
if self.model.isDir(current):
    self.table.setRootIndex(current)
```

Full:

```python
def on_folder_changed(
    self,
    current,
    previous,
):

    if not current.isValid():
        return

    if self.model.isDir(current):
        self.table.setRootIndex(
            current
        )
```

---

# 15. Double Click

Ta muốn:

```text
double-click folder
        ↓
open folder
```

Có thể kết nối:

```python
self.tree.doubleClicked.connect(
    self.on_double_click
)
```

---

# 16. Double-click handler

```python
def on_double_click(
    self,
    index,
):

    if self.model.isDir(index):
        self.tree.setCurrentIndex(
            index
        )
```

Khi selection thay đổi:

```text
currentChanged
    ↓
table.setRootIndex()
```

---

# 17. Table cũng có Double Click

```python
self.table.doubleClicked.connect(
    self.on_table_double_click
)
```

Nếu folder:

```python
def on_table_double_click(
    self,
    index,
):

    if self.model.isDir(index):
        self.table.setRootIndex(
            index
        )
```

Nhưng tốt hơn là điều hướng thống nhất.

---

# 18. `filePath()`

Một API cực kỳ quan trọng:

```python
path = self.model.filePath(index)
```

Ví dụ:

```text
QModelIndex
     ↓
filePath()
     ↓
/home/user/Documents/report.pdf
```

---

# 19. `fileName()`

```python
name = self.model.fileName(index)
```

Ví dụ:

```text
report.pdf
```

---

# 20. `isDir()`

```python
self.model.isDir(index)
```

Trả:

```text
True
```

nếu là directory.

---

# 21. `fileInfo()`

Có thể lấy:

```python
info = self.model.fileInfo(index)
```

Sau đó:

```python
info.size()
info.lastModified()
info.isDir()
info.isFile()
```

---

# 22. File Explorer hoàn chỉnh hơn

Ta muốn:

```text
Tree
        │
        └── selected folder
                   ↓
                Table
                   ↓
            selected file
                   ↓
               StatusBar
```

---

# 23. Table Selection

```python
self.table.selectionModel().currentChanged.connect(
    self.on_file_selected
)
```

Handler:

```python
def on_file_selected(
    self,
    current,
    previous,
):

    if not current.isValid():
        return

    path = self.model.filePath(
        current
    )

    self.statusBar().showMessage(
        path
    )
```

Kết quả:

```text
Ready

→ /home/user/Documents/report.pdf
```

---

# 24. `QSplitter`

Để chia:

```text
Tree | Table
```

dùng:

```python
splitter = QSplitter()
```

Thêm:

```python
splitter.addWidget(self.tree)
splitter.addWidget(self.table)
```

---

# 25. Central Widget

```python
central = QWidget()

layout = QVBoxLayout(
    central
)

layout.addWidget(splitter)

self.setCentralWidget(
    central
)
```

---

# 26. Search

Thêm:

```python
self.search = QLineEdit()

self.search.setPlaceholderText(
    "Search files..."
)
```

UI:

```text
┌────────────────────────────────────────────┐
│ Search: [ report                 ]         │
├────────────────┬───────────────────────────┤
│ Folders        │ Files                     │
```

---

# 27. Proxy Model

Đây là lúc kiến thức Buổi 22 quay lại.

```python
from PySide6.QtCore import (
    QSortFilterProxyModel,
)
```

Tạo:

```python
self.proxy = (
    QSortFilterProxyModel()
)
```

Source:

```python
self.proxy.setSourceModel(
    self.model
)
```

Table:

```python
self.table.setModel(
    self.proxy
)
```

Bây giờ:

```text
QFileSystemModel
       ↓
QSortFilterProxyModel
       ↓
QTableView
```

---

# 28. Search bằng Proxy

```python
self.search.textChanged.connect(
    self.proxy.setFilterRegularExpression
)
```

Về cơ bản:

```text
User type
    ↓
Regex
    ↓
Proxy
    ↓
Filter
    ↓
Table
```

---

# 29. Filter column

FileSystemModel có nhiều column:

```text
Name
Size
Type
Date Modified
```

Nếu muốn search theo Name:

```python
self.proxy.setFilterKeyColumn(
    0
)
```

---

# 30. Case Insensitive

Có thể dùng:

```python
from PySide6.QtCore import (
    QRegularExpression
)
```

Ví dụ:

```python
regex = QRegularExpression(
    text,
    QRegularExpression.PatternOption.CaseInsensitiveOption
)
```

Sau đó:

```python
self.proxy.setFilterRegularExpression(
    regex
)
```

---

# 31. Search tốt hơn

```python
def search_files(self, text):

    regex = QRegularExpression(
        text,
        QRegularExpression.PatternOption.CaseInsensitiveOption,
    )

    self.proxy.setFilterRegularExpression(
        regex
    )
```

Connect:

```python
self.search.textChanged.connect(
    self.search_files
)
```

---

# 32. Một vấn đề quan trọng với Proxy

Table hiện tại:

```text
QSortFilterProxyModel
```

nên `current` của table là:

```text
Proxy QModelIndex
```

Nếu cần Source:

```python
source_index = (
    self.proxy.mapToSource(current)
)
```

Sau đó:

```python
path = self.model.filePath(
    source_index
)
```

---

# 33. Đây chính là kiến thức Buổi 22 + 23

Flow:

```text
QTableView
    ↓
Selection Model
    ↓
Proxy Index
    ↓
mapToSource()
    ↓
Source Index
    ↓
QFileSystemModel
    ↓
filePath()
```

Bạn vừa sử dụng lại toàn bộ kiến thức trước đó.

---

# 34. Context Menu

File Explorer cần:

```text
Right Click
```

UI:

```text
┌──────────────────────┐
│ Open                 │
│ Open in Explorer     │
│ ───────────────────  │
│ Rename               │
│ Delete               │
│ ───────────────────  │
│ Properties           │
└──────────────────────┘
```

Bật:

```python
self.table.setContextMenuPolicy(
    Qt.ContextMenuPolicy.CustomContextMenu
)
```

---

# 35. Context Menu Signal

```python
self.table.customContextMenuRequested.connect(
    self.show_context_menu
)
```

---

# 36. Context Menu cơ bản

```python
from PySide6.QtWidgets import (
    QMenu,
)

def show_context_menu(self, pos):

    menu = QMenu(self)

    open_action = menu.addAction(
        "Open"
    )

    rename_action = menu.addAction(
        "Rename"
    )

    delete_action = menu.addAction(
        "Delete"
    )

    menu.exec(
        self.table.viewport().mapToGlobal(pos)
    )
```

---

# 37. Lấy item đang right-click

Không nên chỉ dùng:

```python
self.table.currentIndex()
```

vì user có thể right-click một item mà current chưa thay đổi như bạn mong muốn.

Ta có:

```python
index = self.table.indexAt(pos)
```

Nếu:

```python
not index.isValid()
```

thì click vào vùng trống.

---

# 38. Proxy → Source

```python
source_index = (
    self.proxy.mapToSource(index)
)
```

Sau đó:

```python
path = self.model.filePath(
    source_index
)
```

---

# 39. Open

Một cách đơn giản:

```python
import os

os.startfile(path)
```

Nhưng:

> `os.startfile()` chỉ phù hợp Windows.

Nếu muốn cross-platform:

```python
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
```

Sau đó:

```python
QDesktopServices.openUrl(
    QUrl.fromLocalFile(path)
)
```

---

# 40. Rename

`QFileSystemModel` hỗ trợ editing.

Cho phép:

```python
self.table.setEditTriggers(
    QAbstractItemView.EditTrigger.SelectedClicked
)
```

hoặc:

```python
DoubleClicked
```

Model có thể xử lý việc rename thông qua editing.

Điểm quan trọng:

```text
View
 ↓
Edit
 ↓
Model.setData()
 ↓
Filesystem
```

---

# 41. Delete

Trong project v1, bạn có thể dùng:

```python
self.model.remove(index)
```

Nhưng cần cẩn thận:

* File
* Directory
* permissions
* recursive deletion

Không nên vội xây delete recursive thủ công trong buổi này.

---

# 42. Hiển thị Column

Table:

```python
self.table.setColumnWidth(
    0,
    300,
)
```

Các column:

```text
0 → Name
1 → Size
2 → Type
3 → Date Modified
```

---

# 43. Ẩn column không cần thiết

Ví dụ Tree không cần:

```text
Size
Type
Date
```

Ta có thể:

```python
for column in range(1, 4):
    self.tree.hideColumn(column)
```

Kết quả:

```text
Tree
──────────────
📁 Documents
📁 Downloads
📁 Pictures
📁 Projects
```

---

# 44. Table

Table giữ:

```text
Name
Size
Type
Date Modified
```

```text
┌──────────────┬────────┬─────────┬──────────────┐
│ Name         │ Size   │ Type    │ Modified     │
├──────────────┼────────┼─────────┼──────────────┤
│ main.py      │ 2 KB   │ Python  │ ...          │
│ report.pdf   │ 120 KB │ PDF     │ ...          │
└──────────────┴────────┴─────────┴──────────────┘
```

---

# 45. Sorting

`QTableView` hỗ trợ sorting:

```python
self.table.setSortingEnabled(
    True
)
```

Click:

```text
Name
```

→ alphabetic.

Click:

```text
Size
```

→ numeric.

Đây chính là kiến thức:

```text
Buổi 21
Sorting
```

được áp dụng trực tiếp.

---

# 46. Header

Có thể:

```python
header = self.table.horizontalHeader()
```

và:

```python
header.setStretchLastSection(
    True
)
```

---

# 47. StatusBar

Trong `QMainWindow`:

```python
self.statusBar().showMessage(
    "Ready"
)
```

Khi chọn file:

```python
self.statusBar().showMessage(
    path
)
```

---

# 48. Main Window Structure

Bây giờ architecture:

```text
QMainWindow
│
├── Search
│
├── Central Widget
│   │
│   └── QSplitter
│       │
│       ├── QTreeView
│       │      │
│       │      └── QFileSystemModel
│       │
│       └── QTableView
│              │
│              └── QSortFilterProxyModel
│                       │
│                       └── QFileSystemModel
│
└── StatusBar
```

---

# 49. Code v1 hoàn chỉnh

Đây là phiên bản bạn nên **tự gõ lại**, thay vì copy-paste.

```python
import sys

from PySide6.QtCore import (
    Qt,
    QDir,
    QRegularExpression,
    QUrl,
)

from PySide6.QtGui import (
    QDesktopServices,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QLineEdit,
    QTreeView,
    QTableView,
    QFileSystemModel,
    QSortFilterProxyModel,
    QMenu,
    QAbstractItemView,
)


class FileExplorer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "File Explorer"
        )

        self.resize(1000, 600)

        self.setup_model()
        self.setup_ui()
        self.setup_connections()

    def setup_model(self):

        self.model = QFileSystemModel()

        root_path = QDir.rootPath()

        self.root_index = (
            self.model.setRootPath(
                root_path
            )
        )

        self.proxy = (
            QSortFilterProxyModel(self)
        )

        self.proxy.setSourceModel(
            self.model
        )

        self.proxy.setFilterKeyColumn(
            0
        )

    def setup_ui(self):

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search files..."
        )

        self.tree = QTreeView()

        self.tree.setModel(
            self.model
        )

        self.table = QTableView()

        self.table.setModel(
            self.proxy
        )

        self.table.setSortingEnabled(
            True
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        for column in range(1, 4):
            self.tree.hideColumn(column)

        splitter = QSplitter()

        splitter.addWidget(
            self.tree
        )

        splitter.addWidget(
            self.table
        )

        central = QWidget()

        layout = QVBoxLayout(
            central
        )

        layout.addWidget(
            self.search
        )

        layout.addWidget(
            splitter
        )

        self.setCentralWidget(
            central
        )

        self.statusBar().showMessage(
            "Ready"
        )

        self.tree.setRootIndex(
            self.root_index
        )

        self.table.setRootIndex(
            self.proxy.mapFromSource(
                self.root_index
            )
        )

    def setup_connections(self):

        self.tree.selectionModel().currentChanged.connect(
            self.on_folder_changed
        )

        self.table.selectionModel().currentChanged.connect(
            self.on_file_selected
        )

        self.search.textChanged.connect(
            self.search_files
        )

        self.table.doubleClicked.connect(
            self.on_table_double_clicked
        )

        self.table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.table.customContextMenuRequested.connect(
            self.show_context_menu
        )

    def on_folder_changed(
        self,
        current,
        previous,
    ):

        if not current.isValid():
            return

        if not self.model.isDir(current):
            return

        proxy_index = (
            self.proxy.mapFromSource(
                current
            )
        )

        self.table.setRootIndex(
            proxy_index
        )

        path = self.model.filePath(
            current
        )

        self.statusBar().showMessage(
            path
        )

    def on_file_selected(
        self,
        current,
        previous,
    ):

        if not current.isValid():
            return

        source_index = (
            self.proxy.mapToSource(
                current
            )
        )

        path = self.model.filePath(
            source_index
        )

        self.statusBar().showMessage(
            path
        )

    def search_files(
        self,
        text,
    ):

        regex = QRegularExpression(
            text,
            QRegularExpression.PatternOption.CaseInsensitiveOption,
        )

        self.proxy.setFilterRegularExpression(
            regex
        )

    def on_table_double_clicked(
        self,
        index,
    ):

        source_index = (
            self.proxy.mapToSource(
                index
            )
        )

        if not self.model.isDir(
            source_index
        ):
            path = self.model.filePath(
                source_index
            )

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(path)
            )

            return

        self.table.setRootIndex(
            index
        )

    def show_context_menu(
        self,
        pos,
    ):

        index = self.table.indexAt(pos)

        if not index.isValid():
            return

        source_index = (
            self.proxy.mapToSource(
                index
            )
        )

        path = self.model.filePath(
            source_index
        )

        menu = QMenu(self)

        open_action = menu.addAction(
            "Open"
        )

        menu.addSeparator()

        copy_path_action = menu.addAction(
            "Copy Path"
        )

        action = menu.exec(
            self.table.viewport().mapToGlobal(
                pos
            )
        )

        if action == open_action:

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(path)
            )

        elif action == copy_path_action:

            QApplication.clipboard().setText(
                path
            )


def main():

    app = QApplication(sys.argv)

    window = FileExplorer()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
```

---

# 50. Điểm quan trọng nhất trong code

Hãy đặc biệt nhìn đoạn:

```python
source_index = (
    self.proxy.mapToSource(
        current
    )
)
```

và:

```python
proxy_index = (
    self.proxy.mapFromSource(
        current
    )
)
```

Bạn vừa sử dụng:

```text
Buổi 18 — QModelIndex
        +
Buổi 19 — Roles
        +
Buổi 21 — Sorting
        +
Buổi 22 — Proxy
        +
Buổi 23 — Selection
```

để xây một ứng dụng thật.

---

# 51. Một lỗi tinh tế trong File Explorer

Có một vấn đề bạn cần tự suy nghĩ:

```text
Search = "python"
```

Table đang filter:

```text
main.py
python.txt
python_project/
```

Sau đó user chọn folder từ Tree.

Table cần:

```text
folder contents
+
search filter
```

Proxy vẫn giữ:

```python
self.proxy.setFilterRegularExpression(...)
```

nên filter sẽ tiếp tục hoạt động.

Đây là sức mạnh của Proxy:

```text
Folder navigation
        +
Search
        +
Sorting
```

được tách khỏi Source Model.

---

# 52. Bài tập nâng cấp 1 — Back / Forward

Thêm:

```text
←
→
```

Ví dụ:

```text
Documents
   ↓
Projects
   ↓
Python
```

History:

```python
self.history = []
self.history_index = -1
```

Bạn sẽ học:

```text
Navigation State
```

rất giống browser.

---

# 53. Bài tập nâng cấp 2 — Breadcrumb

Thêm:

```text
Home > Projects > Python > PySide6
```

Mỗi lần folder thay đổi:

```python
path = self.model.filePath(
    current
)
```

sau đó build breadcrumb.

---

# 54. Bài tập nâng cấp 3 — File Information

Khi chọn file:

```text
Name
Size
Type
Modified
Path
```

hiển thị bên phải.

Kiến trúc:

```text
QTableView
     ↓
SelectionModel
     ↓
Proxy Index
     ↓
Source Index
     ↓
QFileInfo
     ↓
Detail Panel
```

Đây chính là:

> **Master → Detail**

mà chúng ta học ở Buổi 23.

---

# 55. Bài tập nâng cấp 4 — Context Menu

Thêm:

```text
Open
Open Containing Folder
Copy Path
Rename
Delete
Properties
```

Đừng làm tất cả cùng lúc.

Thứ tự:

```text
1. Open
2. Copy Path
3. Rename
4. Delete
5. Properties
```

---

# 56. Bài tập nâng cấp 5 — Filter

Thêm ComboBox:

```text
[ All Files ▼ ]
```

Các lựa chọn:

```text
All
Images
Documents
Python
Text
```

Kiến trúc:

```text
Search
    +
File Type
    ↓
QSortFilterProxyModel
```

Đây sẽ giúp bạn hiểu sâu hơn `filterAcceptsRow()`.

---

# 57. Bài tập nâng cấp 6 — Custom Proxy

Đây là bài tập quan trọng.

Tạo:

```python
class FileProxyModel(
    QSortFilterProxyModel
):
    ...
```

Override:

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):
    ...
```

Cho phép:

```text
Search filename
AND
File extension
```

Ví dụ:

```text
Search: py
Type: Python
```

Kết quả:

```text
main.py
test.py
app.py
```

---

# 58. Bài tập nâng cấp 7 — Hidden Files

Thử:

```python
self.model.setFilter(...)
```

với các flag của:

```python
QDir.Filter
```

Ví dụ cần nghiên cứu:

```text
AllEntries
NoDotAndDotDot
Hidden
Files
Dirs
Drives
```

Đây là lúc bạn bắt đầu làm việc với Qt API thay vì chỉ widget.

---

# 59. Bài tập nâng cấp 8 — Multiple Selection

Đổi:

```python
ExtendedSelection
```

cho Table.

Sau đó:

```text
Ctrl + Click
```

nhiều file.

Hiển thị:

```text
3 files selected
```

trên StatusBar.

Bạn sẽ áp dụng lại:

```python
selectedRows()
```

từ Buổi 23.

---

# 60. Bài tập nâng cấp 9 — Delete Multiple

Flow:

```text
Selected Proxy Indexes
          ↓
mapToSource()
          ↓
Source Indexes
          ↓
File paths
          ↓
Delete
```

Hãy đặc biệt cẩn thận với:

```text
Proxy row
≠
Source row
```

---

# 61. Bài tập nâng cấp 10 — Architecture

Đừng giữ toàn bộ code trong:

```python
FileExplorer(QMainWindow)
```

Khi project lớn hơn, tách:

```text
file_explorer/
│
├── main.py
│
├── views/
│   ├── main_window.py
│   ├── folder_view.py
│   └── file_view.py
│
├── models/
│   └── file_proxy_model.py
│
├── services/
│   ├── file_service.py
│   └── clipboard_service.py
│
└── utils/
```

Sau này khi kết hợp với **Clean Architecture / DDD** mà bạn đang học, ta có thể tiến tới:

```text
Presentation
     ↓
Application
     ↓
Domain
     ↓
Infrastructure
```

---

# 62. Tổng kết toàn bộ Phần II

Bạn vừa hoàn thành một phần rất quan trọng của PySide6:

```text
                 Qt Model/View
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
     Model            View          Selection
       │               │               │
       ↓               ↓               ↓
QAbstractModel    QList/Table/Tree   QModelIndex
       │                               │
       └───────────────┬───────────────┘
                       ↓
                  Proxy Model
                       │
              ┌────────┴────────┐
              ↓                 ↓
           Filter             Sort
                       │
                       ↓
                 Real Project
                       │
                       ↓
                 File Explorer
```

Các kiến thức cốt lõi bạn cần nhớ:

```text
QModelIndex
QAbstractListModel
QAbstractTableModel
QAbstractItemModel
Roles
Delegate
QSortFilterProxyModel
QItemSelectionModel
QFileSystemModel
```

---

# 🎓 Sau Buổi 24

**Phần II — Qt Model/View đã hoàn thành.**

Phần tiếp theo mình khuyên đi theo hướng **Qt Model/View nâng cao + kiến trúc ứng dụng**, thay vì nhảy ngay sang các widget lẻ.

Roadmap tiếp theo có thể là:

```text
# Phần III — Qt Model/View Advanced

Buổi 25 — Model/View Deep Dive
Buổi 26 — `beginInsertRows()` / `endInsertRows()`
Buổi 27 — `beginRemoveRows()` / `endRemoveRows()`
Buổi 28 — Model Reset & Layout Change
Buổi 29 — Editable Model
Buổi 30 — `setData()` Deep Dive
Buổi 31 — Drag & Drop Model/View
Buổi 32 — Custom Delegate
Buổi 33 — Checkbox Delegate
Buổi 34 — ComboBox Delegate
Buổi 35 — SpinBox Delegate
Buổi 36 — Persistent Model Index
Buổi 37 — Advanced Proxy Model
Buổi 38 — Model/View Performance
Buổi 39 — Thread + Model/View
Buổi 40 — Mini Project: Advanced Data Manager
```

Đặc biệt **Buổi 26–30** rất đáng học kỹ, vì đây là phần biến bạn từ người **biết sử dụng `QTableView`** thành người có thể **tự thiết kế Model/View đúng chuẩn Qt**.
