# Buổi 13 — `QTableView`

Hôm nay chúng ta chuyển từ **List View** sang **Table View**.

Nếu `QListView` phù hợp với:

```text
Python
PySide6
SQLite
Redis
```

thì `QTableView` phù hợp với dữ liệu có nhiều thuộc tính:

```text
┌────┬────────────────┬───────────┬──────────┐
│ ID │ Title          │ Status    │ Priority │
├────┼────────────────┼───────────┼──────────┤
│ 1  │ Learn Python   │ Active    │ High     │
│ 2  │ Learn PySide6  │ Active    │ Medium   │
│ 3  │ Learn SQLite   │ Done      │ High     │
└────┴────────────────┴───────────┴──────────┘
```

Đây là kiến thức rất quan trọng cho các app:

* Database browser
* Student Manager
* Todo Manager
* Story Manager
* Admin Dashboard
* File metadata manager

---

# 1. `QTableView` là gì?

Import:

```python
from PySide6.QtWidgets import QTableView
```

`QTableView` chịu trách nhiệm **hiển thị dữ liệu dạng bảng**.

Nó không tự quản lý dữ liệu.

Kiến trúc:

```text
              Model
                │
                │
                ▼
           QTableView
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
      Row     Column   Cell
```

---

# 2. Ví dụ đơn giản nhất

Chúng ta vẫn dùng Model có sẵn:

```python
QStringListModel
```

nhưng hôm nay `QTableView` cần Model có cấu trúc row/column.

Một Model rất tiện để học là:

```python
QStandardItemModel
```

Import:

```python
from PySide6.QtGui import QStandardItemModel
from PySide6.QtGui import QStandardItem
```

---

# 3. Chương trình đầu tiên

```python
import sys

from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTableView


app = QApplication(sys.argv)

model = QStandardItemModel(3, 3)

model.setHorizontalHeaderLabels([
    "ID",
    "Title",
    "Status",
])

data = [
    ["1", "Learn Python", "Active"],
    ["2", "Learn PySide6", "Active"],
    ["3", "Learn SQLite", "Done"],
]

for row, values in enumerate(data):
    for column, value in enumerate(values):
        item = QStandardItem(value)
        model.setItem(row, column, item)


view = QTableView()

view.setModel(model)

view.resize(600, 300)
view.show()

sys.exit(app.exec())
```

Kết quả:

```text
┌────┬────────────────┬──────────┐
│ ID │ Title          │ Status   │
├────┼────────────────┼──────────┤
│ 1  │ Learn Python   │ Active   │
│ 2  │ Learn PySide6  │ Active   │
│ 3  │ Learn SQLite   │ Done     │
└────┴────────────────┴──────────┘
```

---

# 4. Điều quan trọng nhất: Row và Column

Trong `QTableView`, mỗi ô có:

```text
row
column
```

Ví dụ:

```text
             column
          0       1        2
       ┌──────┬─────────┬────────┐
row 0  │ 1    │ Python  │ Active │
       ├──────┼─────────┼────────┤
row 1  │ 2    │ PySide6 │ Active │
       ├──────┼─────────┼────────┤
row 2  │ 3    │ SQLite  │ Done   │
       └──────┴─────────┴────────┘
```

Cell:

```text
(row=1, column=2)
```

là:

```text
Active
```

---

# 5. `QModelIndex`

Khi user click một cell:

```python
view.clicked.connect(on_clicked)
```

callback nhận:

```python
def on_clicked(index):
    ...
```

`index` là:

```text
QModelIndex
```

Nó chứa thông tin về vị trí cell.

---

# 6. Lấy row và column

```python
def on_clicked(index):

    print("row:", index.row())
    print("column:", index.column())
```

Nếu click:

```text
PySide6
```

thì:

```text
row: 1
column: 1
```

---

# 7. Lấy data

```python
def on_clicked(index):

    print(index.data())
```

Click:

```text
Learn PySide6
```

sẽ nhận:

```text
Learn PySide6
```

---

# 8. Lấy toàn bộ thông tin

Một pattern rất hữu ích:

```python
def on_clicked(index):

    if not index.isValid():
        return

    print("row:", index.row())
    print("column:", index.column())
    print("value:", index.data())
```

Đây là pattern bạn sẽ gặp rất thường xuyên trong Model/View.

---

# 9. `doubleClicked`

```python
view.doubleClicked.connect(
    on_double_clicked
)
```

Ví dụ:

```python
def on_double_clicked(index):

    print(
        "Double click:",
        index.data()
    )
```

---

# 10. `pressed`

Tương tự `QListView`:

```python
view.pressed.connect(
    on_pressed
)
```

---

# 11. `activated`

```python
view.activated.connect(
    on_activated
)
```

---

# 12. Header

`QTableView` có:

```text
Horizontal Header
Vertical Header
```

Ví dụ:

```text
        Horizontal Header
       ↓      ↓       ↓
      ID     Title   Status

    ┌────┬────────┬────────┐
 ←  │ 1  │ Python │ Active │
 ←  │ 2  │ Qt     │ Done   │
    └────┴────────┴────────┘
    ↑
Vertical Header
```

---

# 13. Horizontal Header

Lấy header:

```python
header = view.horizontalHeader()
```

Import:

```python
from PySide6.QtWidgets import QHeaderView
```

Có thể cấu hình:

```python
header.setStretchLastSection(True)
```

---

# 14. Stretch column

Ví dụ:

```python
view.horizontalHeader().setStretchLastSection(True)
```

Column cuối cùng sẽ kéo dài theo phần còn lại.

---

# 15. Resize columns

Một lựa chọn rất hữu ích:

```python
view.resizeColumnsToContents()
```

Qt sẽ tính kích thước dựa trên nội dung.

Ví dụ:

```text
ID       → nhỏ
Title    → lớn
Status   → vừa
```

---

# 16. `ResizeMode`

Có thể:

```python
header.setSectionResizeMode(
    QHeaderView.ResizeMode.Stretch
)
```

Khi đó các column sẽ stretch.

Ví dụ:

```text
┌────────────┬────────────┬────────────┐
│ ID         │ Title      │ Status     │
└────────────┴────────────┴────────────┘
```

---

# 17. Chỉ định column

Ví dụ muốn `Title` chiếm phần lớn:

```python
header.setSectionResizeMode(
    1,
    QHeaderView.ResizeMode.Stretch
)
```

Ở đây:

```text
1 = Title
```

vì:

```text
0 = ID
1 = Title
2 = Status
```

---

# 18. Ẩn column

Ví dụ không muốn hiển thị ID:

```python
view.setColumnHidden(0, True)
```

Khi đó:

```text
┌──────────────┬──────────┐
│ Title        │ Status   │
├──────────────┼──────────┤
│ Learn Python │ Active   │
└──────────────┴──────────┘
```

Nhưng Model vẫn có ID.

Đây là một kỹ thuật rất hữu ích.

---

# 19. Ẩn row

Tương tự:

```python
view.setRowHidden(1, True)
```

Row 1 sẽ không hiển thị.

---

# 20. Selection

Mặc định user có thể chọn cell.

```text
┌────┬──────────────┬────────┐
│ 1  │ Python       │ Active │
├────┼──────────────┼────────┤
│ 2  │ PySide6      │ Active │ ←
├────┼──────────────┼────────┤
```

Có thể chọn:

```text
cell
row
column
```

---

# 21. Chọn cả row

Đây là cấu hình rất phổ biến:

```python
from PySide6.QtWidgets import QAbstractItemView

view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectRows
)
```

Bây giờ:

```text
┌────┬──────────────┬────────┐
│ 1  │ Python       │ Active │
├────┼──────────────┼────────┤
│ 2  │ PySide6      │ Active │
├────┼──────────────┼────────┤
│ 3  │ SQLite       │ Done   │
└────┴──────────────┴────────┘
```

Click một cell sẽ chọn **toàn bộ row**.

Đây thường là lựa chọn tốt cho:

```text
Student Manager
Todo Manager
Story Manager
Database Browser
```

---

# 22. Chọn column

Có:

```python
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectColumns
)
```

---

# 23. Chọn cell

Mặc định:

```python
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectItems
)
```

---

# 24. Selection Mode

Giống `QListView`:

```python
view.setSelectionMode(
    QAbstractItemView.SelectionMode.SingleSelection
)
```

Hoặc:

```python
view.setSelectionMode(
    QAbstractItemView.SelectionMode.ExtendedSelection
)
```

`ExtendedSelection` rất hữu ích khi muốn:

```text
Ctrl + click
Shift + click
```

để chọn nhiều row.

---

# 25. Selection Model

Lấy:

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

# 26. Lấy selected rows

Nếu đang dùng:

```python
SelectRows
```

ta có thể:

```python
indexes = view.selectionModel().selectedRows()
```

Ví dụ:

```python
def on_selection_changed(
    selected,
    deselected,
):

    indexes = view.selectionModel().selectedRows()

    for index in indexes:
        print(index.row())
```

---

# 27. Lấy dữ liệu của selected rows

Ví dụ:

```python
def on_selection_changed(
    selected,
    deselected,
):

    for index in view.selectionModel().selectedRows():

        row = index.row()

        print(
            "Selected row:",
            row
        )
```

Sau này với Todo Model:

```text
selected row
      ↓
Todo ID
      ↓
Repository
      ↓
Todo
```

---

# 28. `currentIndex()`

```python
index = view.currentIndex()
```

Ví dụ:

```python
if index.isValid():
    print(index.row())
    print(index.column())
    print(index.data())
```

---

# 29. Row vs selected row

Nếu:

```python
index = view.currentIndex()
```

thì:

```python
index.row()
```

chỉ cho biết vị trí hiện tại.

Còn:

```python
view.selectionModel().selectedRows()
```

cho biết các row đang được chọn.

---

# 30. Editing

`QTableView` có thể cho phép edit cell.

Ví dụ:

```python
view.setEditTriggers(
    QAbstractItemView.EditTrigger.DoubleClicked
)
```

Double-click:

```text
Learn PySide6
```

→ chuyển thành:

```text
[Learn PySide6_______]
```

User có thể sửa.

---

# 31. Nhưng ai thực sự thay đổi data?

Đây là câu hỏi rất quan trọng.

`QTableView`:

```text
hiển thị
```

Model:

```text
quản lý data + nhận edit
```

Flow:

```text
User
 ↓
QTableView
 ↓
Delegate
 ↓
Model.setData()
 ↓
Data
```

Delegate chúng ta sẽ học ở **Buổi 20**.

---

# 32. `QStandardItemModel`

Trong hôm nay chúng ta dùng:

```python
QStandardItemModel
```

vì nó giúp học `QTableView` nhanh.

Ví dụ:

```python
model = QStandardItemModel(3, 3)
```

nghĩa là:

```text
3 rows
3 columns
```

---

# 33. Header

```python
model.setHorizontalHeaderLabels([
    "ID",
    "Title",
    "Status",
])
```

---

# 34. Set cell

```python
model.setItem(
    0,
    0,
    QStandardItem("1")
)
```

Nghĩa là:

```text
row = 0
column = 0
value = "1"
```

---

# 35. Tạo bảng từ Python list

Có thể viết:

```python
data = [
    ["1", "Learn Python", "Active"],
    ["2", "Learn PySide6", "Active"],
    ["3", "Learn SQLite", "Done"],
]
```

Sau đó:

```python
for row, values in enumerate(data):

    for column, value in enumerate(values):

        model.setItem(
            row,
            column,
            QStandardItem(value)
        )
```

Đây là pattern rất đáng nhớ.

---

# 36. Full Example — Todo Table

```python
import sys

from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QTableView


app = QApplication(sys.argv)


data = [
    ["1", "Learn Python", "Active"],
    ["2", "Learn PySide6", "Active"],
    ["3", "Learn SQLite", "Done"],
    ["4", "Learn Redis", "Active"],
]


model = QStandardItemModel(
    len(data),
    3,
)

model.setHorizontalHeaderLabels([
    "ID",
    "Title",
    "Status",
])


for row, values in enumerate(data):

    for column, value in enumerate(values):

        model.setItem(
            row,
            column,
            QStandardItem(value)
        )


view = QTableView()

view.setModel(model)


# Chọn toàn bộ row
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectRows
)


# Cho phép chọn nhiều row
view.setSelectionMode(
    QAbstractItemView.SelectionMode.ExtendedSelection
)


# Double-click để edit
view.setEditTriggers(
    QAbstractItemView.EditTrigger.DoubleClicked
)


# Header
header = view.horizontalHeader()

header.setSectionResizeMode(
    1,
    QHeaderView.ResizeMode.Stretch
)

header.setStretchLastSection(True)


view.resize(700, 400)
view.show()

sys.exit(app.exec())
```

---

# 37. Bắt click row

```python
def on_clicked(index):

    if not index.isValid():
        return

    print(
        "Row:",
        index.row(),
        "Column:",
        index.column(),
        "Value:",
        index.data(),
    )
```

Kết nối:

```python
view.clicked.connect(on_clicked)
```

---

# 38. Một điểm rất quan trọng

Nếu bạn cấu hình:

```python
SelectRows
```

click vào:

```text
Title
```

thì `index.column()` vẫn có thể là:

```text
1
```

Trong khi selection là cả row.

Vì vậy:

```text
current index
```

và:

```text
selected rows
```

vẫn là hai khái niệm cần phân biệt.

---

# 39. Todo App chuyên nghiệp

Sau này chúng ta muốn:

```text
┌────┬────────────────┬──────────┬──────────┐
│ ID │ Title          │ Status   │ Priority │
├────┼────────────────┼──────────┼──────────┤
│ 1  │ Learn Python   │ Active   │ High     │
│ 2  │ Learn PySide6  │ Active   │ Medium   │
│ 3  │ Learn SQLite   │ Done     │ High     │
└────┴────────────────┴──────────┴──────────┘
```

Kiến trúc:

```text
SQLite
   ↓
TodoRepository
   ↓
TodoTableModel
   ↓
QTableView
```

**Không phải:**

```text
SQLite
   ↓
QTableView
```

---

# 40. Tại sao không query SQLite trực tiếp trong View?

Không nên:

```python
class TodoWindow:

    def load_todos(self):

        cursor = sqlite3.connect(...)

        ...
```

Vì View lúc này biết:

```text
SQLite
SQL
Database schema
```

Điều này phá vỡ separation of concerns.

Tốt hơn:

```text
TodoRepository
    ↓
TodoTableModel
    ↓
QTableView
```

---

# 41. `QTableView` và Database

Đây là nơi Model/View cực kỳ mạnh.

Ví dụ database:

```text
todos
--------------------------------
id
title
status
priority
created_at
```

Model sẽ biến database record thành interface mà Qt hiểu.

```text
SQLite
   │
   ▼
Repository
   │
   ▼
QAbstractTableModel
   │
   ▼
QTableView
```

Đây chính là kiến trúc chúng ta sẽ xây ở **Buổi 16**.

---

# 42. `QTableView` vs `QTableWidget`

Giống:

```text
QListWidget
```

vs:

```text
QListView
```

ta có:

```text
QTableWidget
```

vs:

```text
QTableView
```

### `QTableWidget`

Dễ:

```python
table.setItem(...)
```

### `QTableView`

Model/View:

```python
table.setModel(model)
```

---

# 43. Khi nào dùng `QTableWidget`?

App nhỏ:

```text
10 rows
20 rows
temporary data
```

có thể dùng:

```text
QTableWidget
```

Nhưng với:

```text
SQLite
API
10000 rows
sorting
filtering
custom editing
```

nên học:

```text
QTableView
```

---

# 44. Một điểm cực kỳ quan trọng: Performance

Giả sử:

```text
1,000,000 records
```

Bạn không muốn tạo:

```text
1,000,000 QTableWidgetItem
```

rồi nhét vào widget.

Model/View cho phép View chỉ yêu cầu dữ liệu cần thiết.

Concept:

```text
1,000,000 records
        │
        ▼
     Model
        │
        ▼
   QTableView
        │
        ▼
Visible rows
```

Đây là một lý do Model/View rất mạnh cho ứng dụng dữ liệu lớn.

---

# 45. Bài tập 1

Tạo bảng:

```text
┌────┬──────────────┬──────────┬──────────┐
│ ID │ Name         │ Age      │ Class    │
├────┼──────────────┼──────────┼──────────┤
│ 1  │ An           │ 20       │ Python   │
│ 2  │ Bình         │ 21       │ Python   │
│ 3  │ Cường        │ 19       │ Qt       │
└────┴──────────────┴──────────┴──────────┘
```

Dùng:

```text
QTableView
QStandardItemModel
```

---

# 46. Bài tập 2 — Click

Khi click cell, in:

```text
Row: 1
Column: 2
Value: 21
```

Gợi ý:

```python
def on_clicked(index):

    print(index.row())
    print(index.column())
    print(index.data())
```

---

# 47. Bài tập 3 — Select Rows

Cấu hình:

```python
SelectRows
```

và:

```python
ExtendedSelection
```

Cho phép:

```text
Ctrl + click
Shift + click
```

chọn nhiều học sinh.

Sau đó in:

```text
Selected:
1 An
2 Bình
```

---

# 48. Bài tập 4 — Header

Thử:

```python
header.setSectionResizeMode(
    QHeaderView.ResizeMode.Stretch
)
```

Sau đó thử:

```python
view.resizeColumnsToContents()
```

Quan sát sự khác nhau.

---

# 49. Bài tập 5 — Todo Table

Tạo:

```text
┌────┬────────────────┬──────────┬──────────┐
│ ID │ Title          │ Status   │ Priority │
├────┼────────────────┼──────────┼──────────┤
│ 1  │ Python         │ Active   │ High     │
│ 2  │ PySide6        │ Active   │ Medium   │
│ 3  │ SQLite         │ Done     │ High     │
│ 4  │ Redis          │ Active   │ Low      │
└────┴────────────────┴──────────┴──────────┘
```

Click row:

```text
Selected Todo ID: 2
```

---

# 50. Bài tập Deep Dive

Tự trả lời:

### Câu 1

`QTableView` khác `QTableWidget` như thế nào?

### Câu 2

Một cell được xác định bởi những thông tin nào?

```text
?
?
```

### Câu 3

`QModelIndex.row()` dùng để làm gì?

### Câu 4

`QModelIndex.column()` dùng để làm gì?

### Câu 5

Tại sao `QTableView` không nên truy cập SQLite trực tiếp?

### Câu 6

Sự khác nhau giữa:

```python
view.currentIndex()
```

và:

```python
view.selectionModel().selectedRows()
```

là gì?

### Câu 7

Nếu có 1 triệu records, tại sao Model/View phù hợp hơn `QTableWidget`?

---

# 51. Mental Model sau Buổi 13

Bạn cần hình dung:

```text
                     DATA
                       │
                       ▼
                     MODEL
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
        rows                     columns
          │                         │
          └────────────┬────────────┘
                       ▼
                  QTableView
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           click    selection   edit
             │         │         │
             └─────────┼─────────┘
                       ▼
                  QModelIndex
```

Và kiến trúc ứng dụng thực tế:

```text
┌──────────────┐
│   SQLite     │
└──────┬───────┘
       ↓
┌──────────────┐
│ Repository   │
└──────┬───────┘
       ↓
┌──────────────┐
│ Table Model  │
└──────┬───────┘
       ↓
┌──────────────┐
│ QTableView   │
└──────────────┘
```

---

# Tiếp theo — Buổi 14: `QTreeView`

Chúng ta sẽ chuyển từ:

```text
List
 ↓
QListView
```

và:

```text
Table
 ↓
QTableView
```

sang cấu trúc:

```text
Tree
 ↓
QTreeView
```

Ví dụ:

```text
📁 Project
├── 📁 src
│   ├── main.py
│   ├── models.py
│   └── services.py
│
├── 📁 tests
│   ├── test_model.py
│   └── test_service.py
│
└── README.md
```

Đây sẽ là bước chuẩn bị trực tiếp cho **Mini Project Buổi 24 — File Explorer**, và chúng ta sẽ bắt đầu làm việc nghiêm túc với **hierarchical Model/View**.
