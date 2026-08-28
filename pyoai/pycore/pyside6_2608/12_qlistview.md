# Buổi 12 — `QListView` Deep Dive

Hôm nay chúng ta học sâu `QListView`. Đây là View đầu tiên trong hệ thống Model/View mà bạn cần nắm thật chắc trước khi sang `QTableView`, `QTreeView` và đặc biệt là `QAbstractListModel`.

Mental model của buổi hôm nay:

```text
                  Model
                    │
                    │
                    ▼
                QListView
                    │
          ┌─────────┼─────────┐
          │         │         │
        click    double    selection
          │       click       │
          └─────────┬─────────┘
                    ▼
                   App
```

---

# 1. `QListView` là gì?

`QListView` là một View dùng để hiển thị dữ liệu dạng danh sách.

Ví dụ:

```text
Python
PySide6
SQLite
Redis
Docker
```

Import:

```python
from PySide6.QtWidgets import QListView
```

Điểm quan trọng:

> `QListView` không phải nơi chứa dữ liệu chính.

Nó lấy dữ liệu từ Model:

```python
view.setModel(model)
```

---

# 2. Chương trình đầu tiên

Chúng ta dùng `QStringListModel` để tập trung vào `QListView`.

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QListView,
)


app = QApplication(sys.argv)

model = QStringListModel([
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
    "Docker",
])

view = QListView()

view.setModel(model)

view.resize(400, 300)
view.show()

sys.exit(app.exec())
```

Kiến trúc:

```text
Python
PySide6
SQLite
Redis
Docker
    │
    ▼
QStringListModel
    │
    ▼
QListView
```

---

# 3. `setModel()`

Dòng quan trọng nhất:

```python
view.setModel(model)
```

Nó tạo quan hệ:

```text
Model
  │
  ▼
QListView
```

View có thể hỏi Model:

```text
rowCount()
data()
flags()
...
```

Chúng ta sẽ tự implement những thứ này ở Buổi 15.

---

# 4. `QListView` không có `addItem()`

Đây là khác biệt quan trọng.

Với:

```python
QListWidget()
```

ta có:

```python
list_widget.addItem("Python")
```

Nhưng với:

```python
QListView()
```

không có cách sử dụng kiểu:

```python
view.addItem("Python")
```

Thay vào đó:

```python
model.setStringList([
    "Python",
    "PySide6",
])
```

---

# 5. Vì sao?

`QListWidget`:

```text
Widget
 +
Item
```

Còn:

```text
QListView
```

là:

```text
View
 ↓
Model
 ↓
Data
```

Đây là khác biệt kiến trúc chứ không chỉ là khác biệt API.

---

# 6. Selection

Một trong những chức năng quan trọng nhất của `QListView` là selection.

User click:

```text
┌─────────────────────┐
│ Python              │
│ PySide6    ← click  │
│ SQLite              │
│ Redis               │
└─────────────────────┘
```

View sẽ quản lý selection thông qua:

```python
view.selectionModel()
```

---

# 7. `clicked`

Có thể bắt sự kiện click:

```python
view.clicked.connect(on_clicked)
```

Ví dụ:

```python
def on_clicked(index):
    print(index)
```

Code đầy đủ:

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QListView,
)


def on_clicked(index):
    print(index)


app = QApplication(sys.argv)

model = QStringListModel([
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
])

view = QListView()

view.setModel(model)

view.clicked.connect(on_clicked)

view.show()

sys.exit(app.exec())
```

---

# 8. `QModelIndex`

Bạn sẽ thấy:

```python
def on_clicked(index):
```

`index` là:

```text
QModelIndex
```

Nó đại diện cho:

> vị trí của một item trong Model.

Ví dụ:

```text
Python       → row 0
PySide6      → row 1
SQLite       → row 2
Redis        → row 3
```

Click `SQLite`:

```text
QModelIndex
    │
    └── row = 2
```

Buổi 18 chúng ta sẽ học `QModelIndex` rất sâu.

---

# 9. Lấy row

```python
def on_clicked(index):
    print(index.row())
```

Kết quả:

```text
0
1
2
3
```

---

# 10. Lấy Model

Có thể:

```python
model = index.model()
```

Ví dụ:

```python
def on_clicked(index):

    model = index.model()

    print(model)
```

Điều này cho thấy `QModelIndex` gắn với Model nào.

---

# 11. Lấy data

Với `QStringListModel`:

```python
def on_clicked(index):

    value = index.data()

    print(value)
```

Click:

```text
PySide6
```

sẽ nhận:

```text
PySide6
```

---

# 12. `index.data()` thực chất là gì?

Concept:

```text
QModelIndex
     │
     ├── row
     ├── column
     └── model
             │
             ▼
          data()
```

Sau này khi học Roles:

```python
index.data(Qt.ItemDataRole.DisplayRole)
```

sẽ cực kỳ quan trọng.

---

# 13. `clicked` thực tế

Một pattern thường dùng:

```python
def on_clicked(index):

    print(
        "row:",
        index.row(),
        "value:",
        index.data(),
    )
```

---

# 14. `doubleClicked`

Bắt double-click:

```python
view.doubleClicked.connect(
    on_double_clicked
)
```

Ví dụ:

```python
def on_double_clicked(index):

    print(
        "Double clicked:",
        index.data(),
    )
```

Flow:

```text
User double-click
       ↓
QListView
       ↓
doubleClicked
       ↓
QModelIndex
       ↓
Application
```

---

# 15. `activated`

Ngoài `clicked` và `doubleClicked`, còn:

```python
view.activated.connect(...)
```

`activated` thường đại diện cho hành động activate item.

Ví dụ:

```python
def on_activated(index):
    print("Activated:", index.data())
```

Có thể xảy ra khi user double-click hoặc dùng keyboard tùy interaction style/platform.

---

# 16. `pressed`

Có:

```python
view.pressed.connect(...)
```

Ví dụ:

```python
def on_pressed(index):
    print("Pressed:", index.data())
```

Khác nhau về thời điểm:

```text
pressed
   ↓
clicked
```

---

# 17. So sánh các signal

| Signal          | Ý nghĩa           |
| --------------- | ----------------- |
| `pressed`       | User nhấn         |
| `clicked`       | User click        |
| `doubleClicked` | Double-click      |
| `activated`     | Activate item     |
| `entered`       | Mouse đi vào item |

Đừng cố học thuộc tất cả.

Quan trọng nhất:

```text
clicked
doubleClicked
activated
```

---

# 18. `currentIndex()`

Lấy item hiện tại:

```python
index = view.currentIndex()
```

Ví dụ:

```python
def show_current():

    index = view.currentIndex()

    if index.isValid():
        print(index.data())
```

---

# 19. `QModelIndex.isValid()`

Đây là check rất quan trọng:

```python
if not index.isValid():
    return
```

Ví dụ chưa chọn item:

```text
currentIndex()
     ↓
invalid QModelIndex
```

Không nên giả định luôn có selection.

---

# 20. Ví dụ hoàn chỉnh

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QListView,
)


def on_clicked(index):

    if not index.isValid():
        return

    print(
        "Row:",
        index.row(),
        "Value:",
        index.data(),
    )


app = QApplication(sys.argv)

model = QStringListModel([
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
])

view = QListView()

view.setModel(model)

view.clicked.connect(on_clicked)

view.resize(400, 300)
view.show()

sys.exit(app.exec())
```

---

# 21. Selection Mode

`QListView` hỗ trợ nhiều kiểu selection.

Ví dụ:

```python
view.setSelectionMode(
    QListView.SelectionMode.SingleSelection
)
```

Các mode quan trọng:

```text
SingleSelection
ExtendedSelection
MultiSelection
ContiguousSelection
NoSelection
```

---

# 22. `SingleSelection`

```python
QListView.SelectionMode.SingleSelection
```

Chỉ chọn một item:

```text
Python
PySide6  ← selected
SQLite
Redis
```

Phù hợp:

```text
Open file
Select story
Select user
Select todo
```

---

# 23. `MultiSelection`

Cho phép chọn nhiều item:

```text
☑ Python
☑ PySide6
☐ SQLite
☑ Redis
```

Dùng:

```python
view.setSelectionMode(
    QListView.SelectionMode.MultiSelection
)
```

---

# 24. `ExtendedSelection`

Đây là mode thường gặp trong file explorer.

Cho phép:

```text
Ctrl + click
Shift + click
```

Ví dụ:

```python
view.setSelectionMode(
    QListView.SelectionMode.ExtendedSelection
)
```

---

# 25. `NoSelection`

Nếu chỉ muốn hiển thị:

```python
view.setSelectionMode(
    QListView.SelectionMode.NoSelection
)
```

User không thể select item.

---

# 26. `selectionModel()`

Đây là một khái niệm **rất quan trọng**.

```python
selection_model = view.selectionModel()
```

`QListView` không tự mình chứa toàn bộ logic selection.

Nó có:

```text
View
 │
 └── Selection Model
```

---

# 27. Selection Model

Mental model:

```text
                 Model
                   │
                   ▼
                 View
                   │
                   ▼
            SelectionModel
```

Model:

> Có những item nào?

View:

> Hiển thị chúng.

Selection Model:

> User đang chọn item nào?

---

# 28. `selectionChanged`

Có thể bắt thay đổi selection:

```python
selection_model.selectionChanged.connect(
    on_selection_changed
)
```

Ví dụ:

```python
def on_selection_changed(
    selected,
    deselected,
):
    print("Selection changed")
```

---

# 29. `currentChanged`

Ngoài selection còn:

```python
selection_model.currentChanged.connect(
    on_current_changed
)
```

Ví dụ:

```python
def on_current_changed(
    current,
    previous,
):

    print(
        "Current:",
        current.data(),
    )
```

---

# 30. Selection và Current không hoàn toàn giống nhau

Đây là điểm dễ nhầm.

```text
Current
```

là item hiện tại/focus position.

```text
Selection
```

là tập các item đang được chọn.

Với single selection:

```text
current ≈ selected
```

nhưng về concept chúng **không giống nhau**.

Với multi-selection:

```text
Current:
    Python

Selected:
    Python
    SQLite
    Redis
```

---

# 31. Lấy selected indexes

```python
indexes = view.selectionModel().selectedIndexes()
```

Ví dụ:

```python
for index in indexes:
    print(index.data())
```

Nếu chọn:

```text
Python
SQLite
Redis
```

kết quả:

```text
Python
SQLite
Redis
```

---

# 32. Đây cực kỳ quan trọng cho File Explorer

Sau này:

```text
QTreeView
    ↓
SelectionModel
    ↓
selectedIndexes()
```

ta có thể biết:

```text
User chọn file nào?
User chọn folder nào?
User chọn nhiều file nào?
```

---

# 33. Edit item

`QListView` có thể hỗ trợ editing nếu Model cho phép.

Ví dụ với `QStringListModel`, có thể:

```python
view.edit(index)
```

Ví dụ:

```python
def edit_item(index):
    view.edit(index)
```

Khi đó item có thể chuyển sang trạng thái edit.

---

# 34. Double-click để edit

```python
view.doubleClicked.connect(
    view.edit
)
```

Ví dụ:

```python
view.doubleClicked.connect(
    lambda index: view.edit(index)
)
```

Tuy nhiên trong app thực tế, thường bạn sẽ kiểm soát editing thông qua Model/Delegate.

Chúng ta sẽ học sâu hơn ở:

```text
Buổi 19 — Roles
Buổi 20 — Delegate
```

---

# 35. `EditTriggers`

Có thể kiểm soát khi nào View cho phép edit.

```python
view.setEditTriggers(
    QListView.EditTrigger.DoubleClicked
)
```

Một số trigger:

```text
NoEditTriggers
CurrentChanged
DoubleClicked
SelectedClicked
EditKeyPressed
AnyKeyPressed
AllEditTriggers
```

---

# 36. Ví dụ

```python
view.setEditTriggers(
    QListView.EditTrigger.DoubleClicked
)
```

Bây giờ:

```text
Double-click
      ↓
Edit item
```

---

# 37. `NoEditTriggers`

Nếu View chỉ để đọc:

```python
view.setEditTriggers(
    QListView.EditTrigger.NoEditTriggers
)
```

Đây là lựa chọn tốt cho:

```text
Read-only list
Search result
Log viewer
File listing
```

---

# 38. `setSpacing()`

Điều chỉnh khoảng cách item:

```python
view.setSpacing(5)
```

Ví dụ:

```text
Python

PySide6

SQLite
```

thay vì:

```text
Python
PySide6
SQLite
```

---

# 39. `setUniformItemSizes()`

Nếu tất cả item có kích thước tương tự:

```python
view.setUniformItemSizes(True)
```

Có thể giúp View tối ưu việc layout trong một số trường hợp.

Đặc biệt hữu ích khi danh sách lớn và item có kích thước đồng nhất.

---

# 40. `setAlternatingRowColors()`

Mặc dù tên có "Row", nó cũng có thể tạo alternating background cho list view:

```python
view.setAlternatingRowColors(True)
```

Ví dụ:

```text
Python       ─────────
PySide6      ░░░░░░░░░
SQLite       ─────────
Redis        ░░░░░░░░░
```

---

# 41. `setWordWrap()`

Nếu text dài:

```python
view.setWordWrap(True)
```

Ví dụ:

```text
Learn PySide6 Model/View
Architecture and QAbstractListModel
```

có thể wrap thành nhiều dòng.

---

# 42. `setSpacing()` + `setWordWrap()`

Có thể tạo list giống ứng dụng đọc truyện:

```text
┌───────────────────────────────────┐
│ Chương 1                          │
│ Khởi đầu của cuộc hành trình      │
├───────────────────────────────────┤
│ Chương 2                          │
│ Thành phố trong màn đêm           │
└───────────────────────────────────┘
```

Đây là nơi `QListView` bắt đầu trở nên mạnh hơn `QListWidget`.

---

# 43. Scroll Mode

QListView có thể điều khiển cách scroll:

```python
view.setVerticalScrollMode(
    QListView.ScrollMode.ScrollPerPixel
)
```

hoặc:

```python
view.setVerticalScrollMode(
    QListView.ScrollMode.ScrollPerItem
)
```

---

# 44. Horizontal Scroll

Có thể:

```python
view.setHorizontalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)
```

Ví dụ list UI thường không cần horizontal scrollbar.

---

# 45. `setFlow()`

Mặc định:

```text
Python
PySide6
SQLite
Redis
```

Có thể chuyển sang dạng ngang:

```python
view.setFlow(
    QListView.Flow.LeftToRight
)
```

Ví dụ:

```text
Python   PySide6   SQLite   Redis
```

---

# 46. `setWrapping()`

Kết hợp:

```python
view.setWrapping(True)
```

có thể tạo layout:

```text
Python    PySide6    SQLite

Redis     Docker     Qt
```

Điều này hữu ích khi tạo:

```text
icon view
thumbnail view
category selector
```

---

# 47. `setViewMode()`

Có hai mode đáng chú ý:

```python
QListView.ViewMode.ListMode
```

và:

```python
QListView.ViewMode.IconMode
```

---

# 48. List Mode

Mặc định:

```text
Python
PySide6
SQLite
Redis
```

---

# 49. Icon Mode

```python
view.setViewMode(
    QListView.ViewMode.IconMode
)
```

Có thể tạo:

```text
┌──────┐  ┌──────┐  ┌──────┐
│ 📄   │  │ 📄   │  │ 📄   │
│Python│  │ Qt   │  │SQL   │
└──────┘  └──────┘  └──────┘
```

Đây là tiền đề cho kiểu giao diện giống File Explorer.

---

# 50. `QListView` trong File Explorer

Buổi 24 chúng ta sẽ xây File Explorer.

Một phần kiến trúc:

```text
Filesystem
    ↓
Model
    ↓
QTreeView / QListView
```

`QListView` có thể dùng để hiển thị:

```text
files trong folder hiện tại
```

còn:

```text
QTreeView
```

hiển thị:

```text
folder hierarchy
```

---

# 51. Một ví dụ gần với Todo App

Hãy tạo:

```text
TodoModel
   ↓
QListView
```

Tạm thời dùng `QStringListModel`:

```python
model = QStringListModel([
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
])
```

View:

```python
view = QListView()
view.setModel(model)
```

---

# 52. Click Todo

```python
def on_todo_clicked(index):

    title = index.data()

    print("Selected:", title)
```

Kết nối:

```python
view.clicked.connect(
    on_todo_clicked
)
```

---

# 53. Đây là pattern sẽ dùng rất nhiều

```python
def on_clicked(index):

    if not index.isValid():
        return

    value = index.data()

    ...
```

Hãy ghi nhớ.

---

# 54. MainWindow + QListView

Ví dụ:

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListView,
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "QListView Demo"
        )

        self.resize(500, 400)

        self.model = QStringListModel([
            "Learn Python",
            "Learn PySide6",
            "Learn SQLite",
            "Learn Redis",
        ])

        self.view = QListView()

        self.view.setModel(
            self.model
        )

        self.view.clicked.connect(
            self.on_clicked
        )

        self.setCentralWidget(
            self.view
        )

    def on_clicked(self, index):

        if not index.isValid():
            return

        print(
            "Selected:",
            index.data()
        )


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
```

---

# 55. Tư duy kiến trúc

Code trên có:

```text
MainWindow
    │
    ├── Model
    │
    └── View
```

Nhưng trong app lớn hơn, chúng ta sẽ không muốn:

```text
MainWindow
    ↓
tự quản lý data
```

Mà:

```text
Repository
    ↓
Model
    ↓
View
    ↓
MainWindow
```

---

# 56. Model thay đổi → View cập nhật

Ví dụ:

```python
self.model.setStringList([
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
    "Docker",
])
```

Model thay đổi:

```text
Model
 ↓
signal
 ↓
QListView
 ↓
update
```

Bạn không cần:

```python
view.clear()
view.addItem(...)
```

Đây chính là lợi ích của Model/View.

---

# 57. Nhiều View cùng Model

Thử:

```python
view1 = QListView()
view2 = QListView()

view1.setModel(model)
view2.setModel(model)
```

Kiến trúc:

```text
                 Model
                /     \
               ↓       ↓
          QListView  QListView
```

Một nguồn dữ liệu.

Hai presentation.

---

# 58. Đây là nền tảng của ứng dụng chuyên nghiệp

Ví dụ Story App:

```text
                 StoryModel
                /         \
               ↓           ↓
       StoryListView   StoryDetailView
```

hoặc:

```text
                 TodoModel
                /        \
               ↓          ↓
          QListView    QTableView
```

Model không cần biết View cụ thể.

---

# 59. Bài tập 1

Tạo:

```text
QListView
QStringListModel
```

với:

```text
Python
C++
Rust
Go
Java
Kotlin
```

Khi click một item:

```text
Selected: Rust
Row: 2
```

---

# 60. Bài tập 2 — Selection

Cho phép chọn nhiều:

```python
view.setSelectionMode(
    QListView.SelectionMode.ExtendedSelection
)
```

Khi selection thay đổi, in:

```text
Selected:
Python
Rust
Go
```

Gợi ý:

```python
selection_model = view.selectionModel()
```

và:

```python
selection_model.selectionChanged.connect(...)
```

---

# 61. Bài tập 3 — Todo

Dùng:

```text
QStringListModel
+
QListView
```

hiển thị:

```text
☐ Learn Python
☐ Learn PySide6
☐ Learn SQLite
☐ Learn Redis
```

Click Todo:

```text
Selected Todo: Learn PySide6
```

---

# 62. Bài tập 4 — Edit

Cho phép:

```text
Double-click
     ↓
Edit item
```

Gợi ý:

```python
view.setEditTriggers(
    QListView.EditTrigger.DoubleClicked
)
```

---

# 63. Bài tập 5 — Hai View

Tạo:

```text
                 Model
                /     \
               ↓       ↓
          QListView  QListView
```

Khi thay đổi Model:

```python
model.setStringList(...)
```

hãy quan sát cả hai View.

---

# 64. Bài tập 6 — Todo Architecture

Thiết kế:

```text
TodoRepository
       ↓
TodoModel
       ↓
QListView
```

Trong buổi này **chưa cần tự viết `TodoModel`**.

Có thể dùng:

```python
QStringListModel
```

Mục tiêu là hiểu luồng:

```text
Data
 ↓
Model
 ↓
View
 ↓
User
```

---

# 65. Bài tập Deep Dive

Hãy tự trả lời 8 câu:

### 1.

Tại sao `QListView` không có:

```python
addItem()
```

như `QListWidget`?

### 2.

`QModelIndex` đại diện cho cái gì?

### 3.

Khác nhau giữa:

```python
index.row()
```

và:

```python
index.data()
```

là gì?

### 4.

Tại sao cần:

```python
index.isValid()
```

?

### 5.

`selectionModel()` có nhiệm vụ gì?

### 6.

Khác nhau giữa:

```text
Current
```

và:

```text
Selection
```

là gì?

### 7.

Tại sao một Model có thể phục vụ nhiều View?

### 8.

Trong kiến trúc:

```text
Repository
    ↓
Model
    ↓
QListView
```

`QListView` có nên biết SQLite hay không?

**Đáp án câu 8: Không.**

---

# 66. Những thứ bạn cần nhớ sau Buổi 12

Nếu chỉ nhớ 7 thứ:

```text
1. QListView = View
2. Data nằm ở Model
3. view.setModel(model)
4. Click → QModelIndex
5. index.data() → lấy data
6. selectionModel() → quản lý selection
7. QListView không có addItem()
```

Và sơ đồ quan trọng nhất:

```text
                Model
                  │
                  │
             setModel()
                  │
                  ▼
              QListView
                  │
          ┌───────┼────────┐
          ↓       ↓        ↓
       clicked  double   selection
          │       │        │
          └───────┴────────┘
                  ↓
             QModelIndex
```

---

# Tiếp theo — Buổi 13: `QTableView`

Chúng ta sẽ chuyển từ:

```text
List
```

sang:

```text
Table
```

và xây giao diện kiểu:

```text
┌────┬──────────────────┬───────────┬──────────┐
│ ID │ Title            │ Status    │ Priority │
├────┼──────────────────┼───────────┼──────────┤
│ 1  │ Learn Python     │ Active    │ High     │
│ 2  │ Learn PySide6    │ Active    │ Medium   │
│ 3  │ Learn SQLite     │ Completed │ High     │
└────┴──────────────────┴───────────┴──────────┘
```

Quan trọng hơn, chúng ta sẽ bắt đầu hiểu sự khác nhau giữa:

```text
row
column
QModelIndex
Model
View
```

để chuẩn bị cho **Buổi 16 — `QAbstractTableModel`**.
