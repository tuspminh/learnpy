# Buổi 14 — `QTreeView` Deep Dive

Hôm nay chúng ta học **`QTreeView`** — View dùng để hiển thị dữ liệu dạng cây.

Đây là kiến thức rất quan trọng vì nó là nền tảng để sau này xây:

* File Explorer
* Folder browser
* Category tree
* Navigation sidebar
* Story → Chapter → Section
* Knowledge tree
* Project explorer

Mental model:

```text
                Tree Model
                    │
                    ▼
                QTreeView
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       folder      file     selection
```

---

# 1. `QTreeView` là gì?

Import:

```python
from PySide6.QtWidgets import QTreeView
```

Khác với `QListView`:

```text
QListView

Python
PySide6
SQLite
Redis
```

`QTreeView` có quan hệ cha/con:

```text
Project
├── src
│   ├── main.py
│   └── models.py
├── tests
│   └── test_main.py
└── README.md
```

---

# 2. Tree thực chất là gì?

Một tree gồm:

```text
Parent
   │
   ├── Child
   ├── Child
   └── Child
```

Ví dụ:

```text
📁 src
├── main.py
├── models.py
└── services.py
```

Ở đây:

```text
src
```

là parent.

```text
main.py
models.py
services.py
```

là children.

---

# 3. Chương trình đầu tiên

Để học `QTreeView`, chúng ta dùng:

```python
QStandardItemModel
```

Ví dụ:

```python
import sys

from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTreeView


app = QApplication(sys.argv)

model = QStandardItemModel()

model.setHorizontalHeaderLabels([
    "Name"
])

root = QStandardItem("Project")

src = QStandardItem("src")
tests = QStandardItem("tests")
readme = QStandardItem("README.md")

root.appendRow(src)
root.appendRow(tests)
root.appendRow(readme)

src.appendRow(
    QStandardItem("main.py")
)

src.appendRow(
    QStandardItem("models.py")
)

tests.appendRow(
    QStandardItem("test_main.py")
)

model.appendRow(root)

view = QTreeView()

view.setModel(model)

view.expandAll()

view.resize(500, 400)
view.show()

sys.exit(app.exec())
```

Kết quả:

```text
Project
├── src
│   ├── main.py
│   └── models.py
├── tests
│   └── test_main.py
└── README.md
```

---

# 4. `QTreeView` không chứa data

Giống `QListView` và `QTableView`:

```text
QTreeView
    ↓
Model
    ↓
Data
```

Không nên:

```python
tree.addItem(...)
```

Thay vào đó:

```python
model.appendRow(...)
```

---

# 5. `QTreeView` vs `QListView`

### `QListView`

```text
Python
PySide6
SQLite
Redis
```

### `QTreeView`

```text
Programming
├── Python
│   ├── asyncio
│   └── typing
├── C++
└── Rust
```

Điểm khác biệt chính:

```text
List
  ↓
flat

Tree
  ↓
hierarchical
```

---

# 6. Parent / Child

Ví dụ:

```python
src = QStandardItem("src")
```

Sau đó:

```python
src.appendRow(
    QStandardItem("main.py")
)
```

Ta có:

```text
src
└── main.py
```

`src` là parent.

`main.py` là child.

---

# 7. Nhiều cấp

Có thể tạo:

```text
Project
└── src
    └── services
        └── crawler
            └── http.py
```

Code:

```python
project = QStandardItem("Project")
src = QStandardItem("src")
services = QStandardItem("services")
crawler = QStandardItem("crawler")
http = QStandardItem("http.py")

crawler.appendRow(http)
services.appendRow(crawler)
src.appendRow(services)
project.appendRow(src)

model.appendRow(project)
```

Tree không giới hạn ở 2 cấp.

---

# 8. Expand / Collapse

Tree có hai trạng thái:

```text
Expanded
Collapsed
```

Ví dụ collapsed:

```text
▶ Project
```

Expanded:

```text
▼ Project
  ├── src
  ├── tests
  └── README.md
```

---

# 9. `expandAll()`

Để mở tất cả:

```python
view.expandAll()
```

---

# 10. `collapseAll()`

Đóng tất cả:

```python
view.collapseAll()
```

---

# 11. Expand một index

```python
view.expand(index)
```

Collapse:

```python
view.collapse(index)
```

---

# 12. `expanded`

Có thể bắt sự kiện:

```python
view.expanded.connect(
    on_expanded
)
```

Ví dụ:

```python
def on_expanded(index):
    print("Expanded:", index.data())
```

---

# 13. `collapsed`

Tương tự:

```python
view.collapsed.connect(
    on_collapsed
)
```

---

# 14. Click item

Giống các View trước:

```python
view.clicked.connect(
    on_clicked
)
```

Callback:

```python
def on_clicked(index):

    if not index.isValid():
        return

    print(index.data())
```

---

# 15. `QModelIndex` trong Tree

Đây là phần cực kỳ quan trọng.

Ở `QTableView`, index có:

```text
row
column
```

Ở `QTreeView`, ngoài:

```text
row
column
```

còn có:

```text
parent
```

Ví dụ:

```text
Project
└── src
    └── main.py
```

`main.py` có:

```text
parent = src
```

---

# 16. `index.parent()`

Lấy parent:

```python
parent = index.parent()
```

Ví dụ:

```python
def on_clicked(index):

    print("Current:", index.data())

    parent = index.parent()

    if parent.isValid():
        print("Parent:", parent.data())
```

Click:

```text
main.py
```

kết quả:

```text
Current: main.py
Parent: src
```

---

# 17. Parent của parent

Có thể:

```python
parent = index.parent()

if parent.isValid():

    grand_parent = parent.parent()

    if grand_parent.isValid():
        print(grand_parent.data())
```

Ví dụ:

```text
Project
└── src
    └── main.py
```

Click `main.py`:

```text
Current: main.py
Parent: src
Grand parent: Project
```

---

# 18. Đây chính là hierarchical Model

Hãy nhớ:

```text
QModelIndex
│
├── row
├── column
├── model
└── parent()
```

So với Table:

```text
QModelIndex
├── row
├── column
└── model
```

Tree thêm:

```python
index.parent()
```

---

# 19. Kiểm tra root

Nếu:

```python
index.parent()
```

không hợp lệ:

```python
not index.parent().isValid()
```

thì index đó thường nằm ở root level.

Ví dụ:

```text
Project      ← root-level item
├── src
└── tests
```

`Project` không có parent trong model hierarchy.

---

# 20. `row()` trong Tree

Ví dụ:

```text
Project
├── src       row 0
├── tests     row 1
└── README    row 2
```

Click `tests`:

```python
index.row()
```

→

```text
1
```

---

# 21. `column()`

Nếu chỉ có:

```text
Name
```

thì:

```python
index.column()
```

→

```text
0
```

Nếu tree có nhiều columns:

```text
Name       Size       Type
```

thì:

```text
Name → 0
Size → 1
Type → 2
```

---

# 22. Tree có thể có nhiều column

Ví dụ File Explorer:

```text
┌──────────────────┬──────────┬──────────┐
│ Name             │ Size     │ Type     │
├──────────────────┼──────────┼──────────┤
│ 📁 src            │          │ Folder   │
│   main.py        │ 2 KB     │ Python   │
│   models.py      │ 4 KB     │ Python   │
│ 📁 tests          │          │ Folder   │
└──────────────────┴──────────┴──────────┘
```

Đây là một use case rất phù hợp với `QTreeView`.

---

# 23. Tree Model nhiều column

Ví dụ:

```python
model = QStandardItemModel()

model.setHorizontalHeaderLabels([
    "Name",
    "Type",
])
```

Tạo:

```python
src_name = QStandardItem("src")
src_type = QStandardItem("Folder")

src_name.appendRow([
    QStandardItem("main.py"),
    QStandardItem("Python"),
])

model.appendRow([
    src_name,
    src_type,
])
```

Tree lúc này có:

```text
Name        Type
----------------
src         Folder
└── main.py Python
```

---

# 24. Ẩn Header

Nếu chỉ muốn tree đơn giản:

```python
view.setHeaderHidden(True)
```

Kết quả:

```text
📁 Project
├── 📁 src
│   ├── main.py
│   └── models.py
└── README.md
```

Đây là kiểu thường thấy ở sidebar.

---

# 25. Header mặc định

Nếu không ẩn:

```text
Name
------------------
Project
├── src
└── tests
```

---

# 26. Column width

Có thể:

```python
view.resizeColumnToContents(0)
```

Hoặc:

```python
view.resizeColumnToContents(1)
```

---

# 27. Header Stretch

```python
header = view.header()

header.setStretchLastSection(True)
```

---

# 28. Selection

Giống `QListView`:

```python
view.setSelectionMode(
    QTreeView.SelectionMode.SingleSelection
)
```

Hoặc:

```python
view.setSelectionMode(
    QTreeView.SelectionMode.ExtendedSelection
)
```

---

# 29. Selection Behavior

Có thể chọn item:

```python
view.setSelectionBehavior(
    QTreeView.SelectionBehavior.SelectItems
)
```

Hoặc cả row:

```python
view.setSelectionBehavior(
    QTreeView.SelectionBehavior.SelectRows
)
```

Trong File Explorer thường:

```python
SelectRows
```

sẽ tiện hơn.

---

# 30. `selectionModel()`

Lấy selection model:

```python
selection_model = view.selectionModel()
```

Sau đó:

```python
selection_model.selectionChanged.connect(
    on_selection_changed
)
```

---

# 31. Selected indexes

```python
indexes = view.selectionModel().selectedIndexes()
```

Nếu có nhiều column:

```text
Name       Size
main.py    2 KB
```

một row có thể tạo nhiều indexes:

```text
(row 0, column 0)
(row 0, column 1)
```

Do đó nếu muốn lấy row duy nhất, cần chú ý điều này.

---

# 32. `selectedRows()`

Nếu muốn lấy các row:

```python
indexes = view.selectionModel().selectedRows()
```

Ví dụ:

```python
for index in indexes:
    print(index.data())
```

---

# 33. Double-click

```python
view.doubleClicked.connect(
    on_double_clicked
)
```

Ví dụ File Explorer:

```text
Double-click folder
       ↓
expand folder
```

hoặc:

```text
Double-click file
       ↓
open file
```

---

# 34. `setExpandsOnDoubleClick`

QTreeView có behavior liên quan đến double-click.

Bạn có thể kiểm soát:

```python
view.setExpandsOnDoubleClick(True)
```

Nếu muốn click/double-click không tự expand:

```python
view.setExpandsOnDoubleClick(False)
```

---

# 35. Editing

Tương tự `QListView`:

```python
view.setEditTriggers(
    QTreeView.EditTrigger.DoubleClicked
)
```

Nhưng trong ứng dụng chuyên nghiệp, việc edit sẽ đi qua:

```text
View
 ↓
Delegate
 ↓
Model.setData()
```

Chúng ta sẽ học sâu ở **Buổi 20**.

---

# 36. Drag & Drop

`QTreeView` đặc biệt hữu ích khi xây UI có:

```text
drag
drop
```

Ví dụ:

```text
📁 Folder A
📁 Folder B

drag file
     ↓
📁 Folder B
```

Đây là tính năng chúng ta có thể sử dụng khi xây File Explorer.

---

# 37. `setDragEnabled`

```python
view.setDragEnabled(True)
```

Cho phép drag item.

---

# 38. `setAcceptDrops`

```python
view.setAcceptDrops(True)
```

Cho phép nhận drop.

Nhưng để drag/drop thực sự hoạt động đúng, Model cũng cần hỗ trợ các operation tương ứng.

---

# 39. File Explorer

Đây chính là lý do `QTreeView` quan trọng.

Qt đã có sẵn:

```python
QFileSystemModel
```

Import:

```python
from PySide6.QtWidgets import QFileSystemModel
```

Nó cung cấp Model cho filesystem.

---

# 40. `QFileSystemModel`

Kiến trúc:

```text
Operating System
      │
      ▼
QFileSystemModel
      │
      ▼
QTreeView
```

Đây là kiến trúc cực kỳ đẹp.

Bạn không cần tự biến:

```text
folder
file
folder
file
```

thành tree model từ đầu.

---

# 41. Ví dụ File Explorer cực nhỏ

```python
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtWidgets import QTreeView


app = QApplication(sys.argv)

model = QFileSystemModel()

model.setRootPath(".")

view = QTreeView()

view.setModel(model)

view.setRootIndex(
    model.index(".")
)

view.resize(800, 500)
view.show()

sys.exit(app.exec())
```

Bạn đã có một filesystem tree cơ bản.

---

# 42. `setRootPath()`

```python
model.setRootPath(".")
```

Model bắt đầu theo dõi filesystem từ path đó.

Ví dụ:

```python
model.setRootPath(
    "/home/user/projects"
)
```

---

# 43. `setRootIndex()`

View cần biết bắt đầu hiển thị từ đâu:

```python
index = model.index(
    "/home/user/projects"
)

view.setRootIndex(index)
```

Mental model:

```text
Filesystem
    ↓
QFileSystemModel
    ↓
model.index(path)
    ↓
QTreeView.setRootIndex()
```

---

# 44. Ẩn column

`QFileSystemModel` có nhiều column:

```text
Name
Size
Type
Date Modified
```

Nếu muốn chỉ hiển thị Name:

```python
view.setColumnHidden(1, True)
view.setColumnHidden(2, True)
view.setColumnHidden(3, True)
```

Kết quả:

```text
📁 project
├── 📁 src
├── 📁 tests
└── README.md
```

---

# 45. Full File Explorer Demo

```python
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtWidgets import QTreeView


class MainWindow(QTreeView):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "File Explorer"
        )

        self.resize(800, 500)

        self.model = QFileSystemModel()

        self.model.setRootPath(".")

        self.setModel(self.model)

        self.setRootIndex(
            self.model.index(".")
        )

        # Chỉ hiển thị Name
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
```

Đây đã là nền tảng của **File Explorer**.

---

# 46. `QTreeView` vs `QFileSystemModel`

Cần phân biệt:

```text
QTreeView
```

là **View**.

Còn:

```text
QFileSystemModel
```

là **Model**.

Không được nhầm:

```text
QTreeView = filesystem
```

Không.

Đúng là:

```text
Filesystem
    ↓
QFileSystemModel
    ↓
QTreeView
```

---

# 47. So sánh 3 View

Sau Buổi 14, bạn đã có:

```text
QListView
QTableView
QTreeView
```

### QListView

```text
A
B
C
```

### QTableView

```text
A | B | C
D | E | F
```

### QTreeView

```text
A
├── B
│   ├── C
│   └── D
└── E
```

---

# 48. Model tương ứng

Không phải View quyết định data structure.

Ví dụ:

```text
QListView
    ↓
QAbstractListModel
```

```text
QTableView
    ↓
QAbstractTableModel
```

```text
QTreeView
    ↓
QAbstractItemModel
```

Đây chính là roadmap tiếp theo:

```text
Buổi 15
QAbstractListModel

Buổi 16
QAbstractTableModel

Buổi 17
QAbstractItemModel
```

---

# 49. Một insight rất quan trọng

Đến đây bạn có thể nhìn Qt Model/View như sau:

```text
                    MODEL
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
     QListView   QTableView   QTreeView
          │           │           │
        List        Table        Tree
```

Model quyết định:

```text
data structure
```

View quyết định:

```text
presentation
```

---

# 50. Ví dụ Story App

Với ứng dụng truyện của bạn, Tree rất tự nhiên:

```text
📚 Truyện A
├── 📖 Chương 1
├── 📖 Chương 2
├── 📖 Chương 3
└── 📖 Chương 4
```

Hoặc:

```text
📚 Library
├── Tác giả A
│   ├── Truyện 1
│   └── Truyện 2
├── Tác giả B
│   └── Truyện 3
```

Sau này:

```text
SQLite
   ↓
Repository
   ↓
QAbstractItemModel
   ↓
QTreeView
```

---

# 51. Ví dụ Knowledge Base

```text
Python
├── Basic
│   ├── Variables
│   ├── Functions
│   └── Classes
├── Advanced
│   ├── Asyncio
│   ├── Thread
│   └── Process
└── Libraries
    ├── PySide6
    ├── Redis
    └── HTTPX
```

Đây là một use case hoàn hảo cho `QTreeView`.

---

# 52. Bài tập 1 — Project Tree

Tạo:

```text
Project
├── src
│   ├── main.py
│   ├── models.py
│   └── services.py
├── tests
│   ├── test_model.py
│   └── test_service.py
└── README.md
```

Dùng:

```text
QTreeView
QStandardItemModel
QStandardItem
```

---

# 53. Bài tập 2 — Click

Khi click:

```text
models.py
```

in:

```text
Current: models.py
Parent: src
```

Gợi ý:

```python
def on_clicked(index):

    if not index.isValid():
        return

    print("Current:", index.data())

    parent = index.parent()

    if parent.isValid():
        print("Parent:", parent.data())
```

---

# 54. Bài tập 3 — Tree nhiều cấp

Tạo:

```text
Python
├── Core
│   ├── Function
│   ├── Class
│   └── Decorator
├── Async
│   ├── asyncio
│   └── Task
└── GUI
    └── PySide6
```

Click `PySide6` phải lấy được:

```text
Current: PySide6
Parent: GUI
Grand Parent: Python
```

---

# 55. Bài tập 4 — File Explorer

Dùng:

```python
QFileSystemModel
QTreeView
```

hiển thị filesystem.

Yêu cầu:

```text
1. Hiển thị folder
2. Hiển thị file
3. Chỉ hiển thị Name
4. Click file → in path
```

Gợi ý lấy path:

```python
path = model.filePath(index)
```

---

# 56. Bài tập 5 — Selection

Cho phép:

```text
Ctrl + click
Shift + click
```

và in danh sách selected items.

Dùng:

```python
QAbstractItemView.SelectionMode.ExtendedSelection
```

và:

```python
view.selectionModel().selectedIndexes()
```

---

# 57. Bài tập Deep Dive

Bạn hãy tự trả lời:

### 1.

Khác nhau giữa:

```text
QListView
QTableView
QTreeView
```

là gì?

### 2.

Tại sao `QTreeView` cần khái niệm:

```python
index.parent()
```

?

### 3.

`row()` trong Tree có ý nghĩa gì?

### 4.

Nếu:

```python
index.parent().isValid()
```

trả về `False`, điều đó thường có nghĩa gì?

### 5.

`QTreeView` có lưu filesystem không?

### 6.

Vai trò của:

```text
QFileSystemModel
```

là gì?

### 7.

Tại sao kiến trúc này tốt hơn việc tự tạo hàng nghìn `QTreeWidgetItem`?

```text
Filesystem
    ↓
QFileSystemModel
    ↓
QTreeView
```

### 8.

Trong Story App:

```text
Story
├── Chapter 1
├── Chapter 2
└── Chapter 3
```

nên dùng `QListView`, `QTableView` hay `QTreeView`? Vì sao?

---

# 58. Mental Model quan trọng nhất của Buổi 14

Hãy ghi nhớ:

```text
                  MODEL
                    │
                    ▼
                QTreeView
                    │
                    ▼
               QModelIndex
                    │
          ┌─────────┴─────────┐
          │                   │
        row()              parent()
          │                   │
          ▼                   ▼
       vị trí            node cha
```

Và với File Explorer:

```text
             Operating System
                    │
                    ▼
             QFileSystemModel
                    │
                    ▼
                QTreeView
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       expand     select     double-click
```

---

## Bước tiếp theo: Buổi 15 — `QAbstractListModel`

Đây là lúc chúng ta **bắt đầu viết Model của riêng mình**.

Thay vì:

```python
QStringListModel(...)
```

chúng ta sẽ tự xây:

```python
class TodoModel(QAbstractListModel):
    ...
```

với:

```text
Todo
 ├── id
 ├── title
 ├── completed
 └── priority
        ↓
   TodoModel
        ↓
    QListView
```

Và bạn sẽ học 3 phương thức nền tảng:

```python
rowCount()
data()
flags()
```

Đây là bước chuyển từ **"biết dùng Qt"** sang **"hiểu Model/View và có thể xây Model thật cho ứng dụng"**.
