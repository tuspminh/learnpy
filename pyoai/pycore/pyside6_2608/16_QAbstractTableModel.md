# Buổi 16 — `QAbstractTableModel`

Hôm nay chúng ta chuyển từ:

```text
QAbstractListModel
        ↓
QListView
```

sang:

```text
QAbstractTableModel
        ↓
QTableView
```

Đây là bài **rất quan trọng** nếu bạn muốn làm ứng dụng thực tế với:

```text
SQLite
    ↓
Repository
    ↓
QAbstractTableModel
    ↓
QTableView
```

Đặc biệt phù hợp với các app bạn đang hướng tới như **Todo Manager, Student Manager, Story Manager, Database Browser**.

---

# 1. Mục tiêu buổi học

Sau buổi này bạn cần hiểu:

* `QAbstractTableModel`
* `rowCount()`
* `columnCount()`
* `data()`
* `headerData()`
* `flags()`
* `setData()`
* `dataChanged`
* `beginInsertRows()` / `endInsertRows()`
* `beginRemoveRows()` / `endRemoveRows()`
* cách map object Python → table
* kiến trúc `Repository → TableModel → QTableView`

---

# 2. Từ List sang Table

Ở Buổi 15:

```python
todos = [
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
]
```

Ta có:

```text
Learn Python
Learn PySide6
Learn SQLite
```

Đây là **List**.

---

Bây giờ Todo có nhiều thuộc tính:

```python
todos = [
    {
        "id": 1,
        "title": "Learn Python",
        "status": "Active",
    },
    {
        "id": 2,
        "title": "Learn PySide6",
        "status": "Active",
    },
]
```

Ta muốn:

```text
┌────┬───────────────┬────────┐
│ ID │ Title         │ Status │
├────┼───────────────┼────────┤
│ 1  │ Learn Python  │ Active │
│ 2  │ Learn PySide6 │ Active │
└────┴───────────────┴────────┘
```

Đây là nhiệm vụ của:

```text
QAbstractTableModel
```

---

# 3. Import

```python
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt
```

View:

```python
from PySide6.QtWidgets import QTableView
```

---

# 4. Model đầu tiên

```python
import sys

from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTableView


class TodoTableModel(QAbstractTableModel):

    def __init__(self, todos=None):
        super().__init__()

        self.todos = todos or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.todos)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:

            todo = self.todos[index.row()]

            if index.column() == 0:
                return todo["id"]

            if index.column() == 1:
                return todo["title"]

            if index.column() == 2:
                return todo["status"]

        return None


app = QApplication(sys.argv)

todos = [
    {
        "id": 1,
        "title": "Learn Python",
        "status": "Active",
    },
    {
        "id": 2,
        "title": "Learn PySide6",
        "status": "Active",
    },
    {
        "id": 3,
        "title": "Learn SQLite",
        "status": "Done",
    },
]

model = TodoTableModel(todos)

view = QTableView()
view.setModel(model)

view.resize(600, 300)
view.show()

sys.exit(app.exec())
```

---

# 5. Ba câu hỏi quan trọng

`QTableView` sẽ hỏi Model:

```text
Có bao nhiêu row?
        ↓
rowCount()
```

```text
Có bao nhiêu column?
        ↓
columnCount()
```

```text
Cell này chứa gì?
        ↓
data()
```

Mental model:

```text
                 QTableView
                     │
         ┌───────────┼───────────┐
         ↓           ↓           ↓
    rowCount()  columnCount()   data()
         │           │           │
         ↓           ↓           ↓
        rows       columns       value
```

---

# 6. `rowCount()`

```python
def rowCount(self, parent=QModelIndex()):
    return len(self.todos)
```

Nếu:

```python
len(self.todos) == 3
```

thì:

```text
rowCount() → 3
```

---

# 7. `columnCount()`

```python
def columnCount(self, parent=QModelIndex()):
    return 3
```

Có:

```text
0 → ID
1 → Title
2 → Status
```

Table:

```text
             columns
          0      1       2
       ┌──────┬───────┬────────┐
row 0  │ 1    │ Python│ Active │
       ├──────┼───────┼────────┤
row 1  │ 2    │ Qt    │ Active │
       ├──────┼───────┼────────┤
row 2  │ 3    │ SQLite│ Done   │
       └──────┴───────┴────────┘
```

---

# 8. `data()` là trung tâm của Model

```python
def data(self, index, role):
```

Ví dụ Qt hỏi:

```text
row = 1
column = 2
role = DisplayRole
```

Ta làm:

```python
todo = self.todos[index.row()]
```

→ Todo số 2.

Sau đó:

```python
if index.column() == 2:
    return todo["status"]
```

→ `"Active"`.

---

# 9. Mapping column

Hiện tại chúng ta đang viết:

```python
if index.column() == 0:
    return todo["id"]

if index.column() == 1:
    return todo["title"]

if index.column() == 2:
    return todo["status"]
```

Đây là mapping:

```text
column 0 → id
column 1 → title
column 2 → status
```

Đây là pattern cơ bản nhất của Table Model.

---

# 10. Cách tốt hơn: danh sách columns

Thay vì hard-code quá nhiều:

```python
class TodoTableModel(QAbstractTableModel):

    COLUMNS = [
        "id",
        "title",
        "status",
    ]
```

Sau đó:

```python
def columnCount(self, parent=QModelIndex()):
    return len(self.COLUMNS)
```

Và:

```python
def data(self, index, role):

    if not index.isValid():
        return None

    if role == Qt.ItemDataRole.DisplayRole:

        todo = self.todos[index.row()]

        field = self.COLUMNS[index.column()]

        return todo[field]

    return None
```

Đây là cách thiết kế tốt hơn.

---

# 11. `headerData()`

Hiện tại table chưa có header đẹp.

Ta override:

```python
def headerData(
    self,
    section,
    orientation,
    role=Qt.ItemDataRole.DisplayRole,
):
```

Ví dụ:

```python
def headerData(
    self,
    section,
    orientation,
    role=Qt.ItemDataRole.DisplayRole,
):

    if role != Qt.ItemDataRole.DisplayRole:
        return None

    if orientation == Qt.Orientation.Horizontal:
        return self.COLUMNS[section]

    return str(section + 1)
```

---

# 12. Horizontal Header

Khi:

```python
orientation == Qt.Orientation.Horizontal
```

ta đang xử lý:

```text
ID | Title | Status
```

---

# 13. Vertical Header

Khi:

```python
orientation == Qt.Orientation.Vertical
```

ta đang xử lý:

```text
1
2
3
```

ở bên trái table.

---

# 14. Full Model tốt hơn

```python
class TodoTableModel(QAbstractTableModel):

    COLUMNS = [
        "id",
        "title",
        "status",
    ]

    def __init__(self, todos=None):
        super().__init__()

        self.todos = todos or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.todos)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMNS)

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:

            todo = self.todos[index.row()]

            field = self.COLUMNS[index.column()]

            return todo[field]

        return None

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]

        return str(section + 1)
```

---

# 15. Nhưng header đang hơi xấu

Ta muốn:

```text
id → ID
title → Title
status → Status
```

Có thể tạo riêng:

```python
HEADERS = [
    "ID",
    "Title",
    "Status",
]
```

và:

```python
COLUMNS = [
    "id",
    "title",
    "status",
]
```

---

# 16. Tách field và header

```python
class TodoTableModel(QAbstractTableModel):

    COLUMNS = [
        "id",
        "title",
        "status",
    ]

    HEADERS = [
        "ID",
        "Title",
        "Status",
    ]
```

Sau đó:

```python
def headerData(
    self,
    section,
    orientation,
    role=Qt.ItemDataRole.DisplayRole,
):

    if role != Qt.ItemDataRole.DisplayRole:
        return None

    if orientation == Qt.Orientation.Horizontal:
        return self.HEADERS[section]

    return str(section + 1)
```

Đây là thiết kế sạch hơn.

---

# 17. `flags()`

Giống Buổi 15.

Nếu chỉ muốn:

```text
select
```

thì:

```python
def flags(self, index):

    if not index.isValid():
        return Qt.ItemFlag.NoItemFlags

    return (
        Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsSelectable
    )
```

---

# 18. Cho phép edit

Nếu muốn user sửa:

```text
Learn Python
```

thành:

```text
Learn Advanced Python
```

thì:

```python
def flags(self, index):

    if not index.isValid():
        return Qt.ItemFlag.NoItemFlags

    return (
        Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsSelectable
        | Qt.ItemFlag.ItemIsEditable
    )
```

---

# 19. `setData()`

Bây giờ Model cần nhận thay đổi:

```python
def setData(
    self,
    index,
    value,
    role=Qt.ItemDataRole.EditRole,
):
```

Implementation:

```python
def setData(
    self,
    index,
    value,
    role=Qt.ItemDataRole.EditRole,
):

    if not index.isValid():
        return False

    if role != Qt.ItemDataRole.EditRole:
        return False

    todo = self.todos[index.row()]

    if index.column() == 0:
        todo["id"] = value

    elif index.column() == 1:
        todo["title"] = value

    elif index.column() == 2:
        todo["status"] = value

    else:
        return False

    self.dataChanged.emit(
        index,
        index,
        [role],
    )

    return True
```

---

# 20. Flow của Edit

Khi user double-click:

```text
QTableView
     ↓
Delegate
     ↓
Model.setData()
     ↓
Todo thay đổi
     ↓
dataChanged.emit()
     ↓
QTableView refresh
```

Bạn cần nhớ flow này.

---

# 21. Edit Trigger

Cho phép double-click:

```python
view.setEditTriggers(
    QTableView.EditTrigger.DoubleClicked
)
```

Hoặc có thể cho edit bằng:

```text
DoubleClick
F2
SelectedClicked
```

Tùy cấu hình.

---

# 22. Một vấn đề: ID có nên edit?

Thường:

```text
ID        → không edit
Title     → edit
Status    → edit
```

Do đó `flags()` có thể kiểm tra column.

```python
def flags(self, index):

    if not index.isValid():
        return Qt.ItemFlag.NoItemFlags

    flags = (
        Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsSelectable
    )

    if index.column() != 0:
        flags |= Qt.ItemFlag.ItemIsEditable

    return flags
```

Bây giờ:

```text
ID       ❌ edit
Title    ✅ edit
Status   ✅ edit
```

---

# 23. Nhưng `setData()` cũng phải validate

Không nên chỉ dựa vào UI.

Ví dụ:

```python
if index.column() == 1:

    title = str(value).strip()

    if not title:
        return False

    todo["title"] = title
```

Model nên bảo vệ invariant của data.

---

# 24. Model không nên tin View

Đây là nguyên tắc quan trọng.

Không nên nghĩ:

```text
View validation = đủ
```

Bởi vì Model có thể được sử dụng bởi:

```text
QTableView
QSortFilterProxyModel
Unit Test
Other View
```

Do đó:

```text
Model
 ↓
validate data
```

---

# 25. `beginInsertRows()`

Thêm Todo:

```python
def insertRows(
    self,
    row,
    count,
    parent=QModelIndex(),
):

    self.beginInsertRows(
        parent,
        row,
        row + count - 1,
    )

    for _ in range(count):
        self.todos.insert(
            row,
            {
                "id": 0,
                "title": "",
                "status": "Active",
            },
        )

    self.endInsertRows()

    return True
```

---

# 26. Tại sao cần begin/end?

Qt cần biết cấu trúc Model thay đổi.

Không nên:

```python
self.todos.insert(...)
```

một cách âm thầm.

Đúng:

```text
beginInsertRows()
       ↓
modify data
       ↓
endInsertRows()
```

---

# 27. Xóa row

```python
def removeRows(
    self,
    row,
    count,
    parent=QModelIndex(),
):

    if row < 0:
        return False

    if row + count > len(self.todos):
        return False

    self.beginRemoveRows(
        parent,
        row,
        row + count - 1,
    )

    del self.todos[row:row + count]

    self.endRemoveRows()

    return True
```

---

# 28. Full `TodoTableModel`

Đây là phiên bản bạn nên tự gõ lại thay vì copy-paste:

```python
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)


class TodoTableModel(QAbstractTableModel):

    COLUMNS = [
        "id",
        "title",
        "status",
    ]

    HEADERS = [
        "ID",
        "Title",
        "Status",
    ]

    def __init__(self, todos=None):
        super().__init__()

        self.todos = todos or []

    def rowCount(self, parent=QModelIndex()):

        return len(self.todos)

    def columnCount(self, parent=QModelIndex()):

        return len(self.COLUMNS)

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:

            todo = self.todos[index.row()]

            field = self.COLUMNS[index.column()]

            return todo[field]

        if role == Qt.ItemDataRole.EditRole:

            todo = self.todos[index.row()]

            field = self.COLUMNS[index.column()]

            return todo[field]

        return None

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]

        return str(section + 1)

    def flags(self, index):

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )

        if index.column() != 0:
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def setData(
        self,
        index,
        value,
        role=Qt.ItemDataRole.EditRole,
    ):

        if not index.isValid():
            return False

        if role != Qt.ItemDataRole.EditRole:
            return False

        todo = self.todos[index.row()]

        field = self.COLUMNS[index.column()]

        if field == "title":

            value = str(value).strip()

            if not value:
                return False

        todo[field] = value

        self.dataChanged.emit(
            index,
            index,
            [role],
        )

        return True
```

---

# 29. Chạy Model

```python
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTableView


app = QApplication(sys.argv)

todos = [
    {
        "id": 1,
        "title": "Learn Python",
        "status": "Active",
    },
    {
        "id": 2,
        "title": "Learn PySide6",
        "status": "Active",
    },
    {
        "id": 3,
        "title": "Learn SQLite",
        "status": "Done",
    },
]

model = TodoTableModel(todos)

view = QTableView()

view.setModel(model)

view.setSelectionBehavior(
    QTableView.SelectionBehavior.SelectRows
)

view.resizeColumnsToContents()

view.resize(600, 300)
view.show()

sys.exit(app.exec())
```

---

# 30. Đừng dùng `QTableWidget`

Từ đây trở đi, khi học Model/View, hãy tập thói quen:

❌:

```python
QTableWidget
```

Thay bằng:

```text
QAbstractTableModel
       ↓
QTableView
```

Nếu dữ liệu đến từ database, kiến trúc sẽ cực kỳ đẹp:

```text
SQLite
   ↓
Repository
   ↓
TodoTableModel
   ↓
QTableView
```

---

# 31. Model với `dataclass`

Dictionary hoạt động tốt để học.

Nhưng ứng dụng thực tế nên dùng Domain Model.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    status: str
```

Data:

```python
todos = [
    Todo(
        1,
        "Learn Python",
        "Active",
    ),
    Todo(
        2,
        "Learn PySide6",
        "Active",
    ),
    Todo(
        3,
        "Learn SQLite",
        "Done",
    ),
]
```

---

# 32. Model với Object

Bây giờ mapping:

```text
Todo
 ├── id
 ├── title
 └── status
```

sang:

```text
Table
 ├── column 0 → id
 ├── column 1 → title
 └── column 2 → status
```

Trong `data()`:

```python
todo = self.todos[index.row()]
```

sau đó:

```python
if index.column() == 0:
    return todo.id

if index.column() == 1:
    return todo.title

if index.column() == 2:
    return todo.status
```

---

# 33. Kiến trúc thực tế

Đây mới là mục tiêu của chúng ta:

```text
┌───────────────────┐
│      SQLite       │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│ TodoRepository    │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│ Todo objects      │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│ TodoTableModel    │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│    QTableView     │
└───────────────────┘
```

View **không biết SQLite**.

Model **không biết SQL**.

Repository **không biết PySide6 UI**.

Đây là separation of concerns rất quan trọng.

---

# 34. Một lỗi kiến trúc thường gặp

Không nên:

```python
class TodoTableModel:

    def load(self):

        conn = sqlite3.connect(
            "todo.db"
        )

        cursor = conn.execute(
            "SELECT * FROM todos"
        )
```

Model lúc này biết:

```text
SQLite
SQL
Database
```

và UI layer bị dính database.

Tốt hơn:

```python
todos = repository.list_all()

model = TodoTableModel(todos)
```

---

# 35. Refresh toàn bộ Model

Trong trường hợp đơn giản, đôi khi bạn sẽ muốn reload toàn bộ dữ liệu.

Qt có các cơ chế thông báo thay đổi Model.

Nhưng **không nên lạm dụng** kiểu:

```python
beginResetModel()
...
endResetModel()
```

cho mọi thay đổi.

Nếu chỉ một row thay đổi:

```python
dataChanged
```

Nếu insert:

```python
beginInsertRows
endInsertRows
```

Nếu remove:

```python
beginRemoveRows
endRemoveRows
```

Thông báo càng chính xác, View càng hoạt động hiệu quả.

---

# 36. `headerData()` cực kỳ quan trọng

Bạn sẽ gặp:

```python
headerData(
    section,
    orientation,
    role,
)
```

rất nhiều khi làm Table Model.

Mental model:

```text
Horizontal
     ↓
column headers

Vertical
     ↓
row headers
```

Ví dụ:

```text
       ID    Title    Status
     ─────────────────────────
  1  │ 1     Python   Active
  2  │ 2     PySide6  Active
  3  │ 3     SQLite   Done
```

---

# 37. `QModelIndex` trong Table

Ví dụ:

```text
row = 2
column = 1
```

nghĩa là:

```text
row 2
column 1
```

→:

```text
Learn SQLite
```

Bạn có thể lấy:

```python
index.row()
index.column()
index.data()
```

---

# 38. Table Model vs List Model

### `QAbstractListModel`

```text
rowCount()
data()
flags()
```

### `QAbstractTableModel`

```text
rowCount()
columnCount()
data()
headerData()
flags()
setData()
```

Ta thêm:

```text
columnCount()
headerData()
```

vì Table có columns.

---

# 39. Bảng so sánh

| Model                 | View         | Data  |
| --------------------- | ------------ | ----- |
| `QAbstractListModel`  | `QListView`  | List  |
| `QAbstractTableModel` | `QTableView` | Table |
| `QAbstractItemModel`  | `QTreeView`  | Tree  |

Đây là ba mảnh ghép lớn của Qt Model/View.

---

# 40. Bài tập 1 — Student Model

Tạo:

```python
@dataclass
class Student:
    id: int
    name: str
    age: int
    class_name: str
```

Data:

```text
1 | An    | 20 | Python
2 | Bình  | 21 | Python
3 | Cường | 19 | Qt
```

Viết:

```python
class StudentTableModel(QAbstractTableModel):
    ...
```

Hiển thị bằng:

```python
QTableView
```

---

# 41. Bài tập 2 — Header

Header:

```text
ID | Name | Age | Class
```

Vertical header:

```text
1
2
3
```

---

# 42. Bài tập 3 — Select Row

Cấu hình:

```python
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectRows
)
```

Khi click:

```text
2 | Bình | 21 | Python
```

in:

```text
Selected student: Bình
```

---

# 43. Bài tập 4 — Edit

Cho phép:

```text
Name
Age
Class
```

edit.

Nhưng:

```text
ID
```

không được edit.

---

# 44. Bài tập 5 — Validation

Không cho:

```text
Name = ""
Age = -1
```

Ví dụ:

```python
if not name:
    return False

if age < 0:
    return False
```

---

# 45. Bài tập 6 — Insert

Thêm Student:

```text
ID: 4
Name: Dũng
Age: 22
Class: Python
```

bằng:

```python
model.insertRows(...)
```

---

# 46. Bài tập 7 — Remove

Chọn một row:

```text
2 | Bình | 21 | Python
```

rồi:

```python
model.removeRows(...)
```

---

# 47. Bài tập 8 — Todo Manager

Xây:

```text
┌────┬────────────────┬──────────┐
│ ID │ Title          │ Status   │
├────┼────────────────┼──────────┤
│ 1  │ Learn Python   │ Active   │
│ 2  │ Learn PySide6  │ Active   │
│ 3  │ Learn SQLite   │ Done     │
└────┴────────────────┴──────────┘
```

Có:

```text
Add
Edit
Delete
```

Nhưng **chưa cần SQLite**.

SQLite sẽ được nối vào kiến trúc sau.

---

# 48. Bài tập Deep Dive

Bạn nên tự trả lời:

### Câu 1

Tại sao `QAbstractTableModel` cần `columnCount()` còn `QAbstractListModel` thường không cần?

### Câu 2

`headerData()` dùng để làm gì?

### Câu 3

Trong:

```python
index.row()
index.column()
```

hai giá trị này dùng để xác định gì?

### Câu 4

Nếu:

```text
row = 3
column = 2
```

thì Model phải làm thế nào để lấy đúng field?

### Câu 5

Tại sao cần:

```python
dataChanged.emit()
```

sau `setData()`?

### Câu 6

Khi thêm row, tại sao dùng:

```python
beginInsertRows()
endInsertRows()
```

?

### Câu 7

Khi xóa row, tại sao dùng:

```python
beginRemoveRows()
endRemoveRows()
```

?

### Câu 8

Tại sao `TodoTableModel` không nên trực tiếp query SQLite?

### Câu 9

Trong kiến trúc:

```text
SQLite
 ↓
Repository
 ↓
TodoTableModel
 ↓
QTableView
```

mỗi thành phần chịu trách nhiệm gì?

### Câu 10

Nếu chỉ thay đổi:

```text
Todo #5 title
```

nên dùng:

```text
dataChanged
```

hay:

```text
beginResetModel
```

? Vì sao?

---

# 49. Mental Model cần nhớ

Sau Buổi 16, hãy nhớ mô hình này:

```text
                     QTableView
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
        rowCount()   columnCount()    data()
             │            │            │
             ▼            ▼            ▼
           rows        columns        cell
```

Khi edit:

```text
User
 ↓
Delegate
 ↓
setData()
 ↓
Model
 ↓
dataChanged.emit()
 ↓
QTableView
```

Khi insert:

```text
beginInsertRows()
        ↓
    modify data
        ↓
endInsertRows()
```

Khi remove:

```text
beginRemoveRows()
        ↓
    modify data
        ↓
endRemoveRows()
```

---

# 50. Và kiến trúc ứng dụng thực tế

Đây là phần quan trọng nhất của buổi hôm nay:

```text
                    DOMAIN
                       │
                    Todo
                       │
                       ▼
                TodoRepository
                       │
                       ▼
              TodoTableModel
                       │
                       ▼
                  QTableView
                       │
                       ▼
                     User
```

Từ đây trở đi, **Model/View không còn chỉ là một kỹ thuật hiển thị bảng**. Nó trở thành cầu nối giữa **Domain/Application data** và UI.

---

## Buổi 17 — `QAbstractItemModel`

Buổi tiếp theo sẽ khó hơn đáng kể.

Chúng ta sẽ xây Model cho cấu trúc:

```text
Library
├── Python
│   ├── Basic
│   └── Advanced
├── PySide6
│   ├── Widgets
│   └── Model/View
└── SQLite
    ├── Query
    └── Transaction
```

và học cách tự xây **Tree Model** với:

```python
QAbstractItemModel
```

Các khái niệm sẽ kết nối với nhau:

```text
QTreeView
    ↓
QAbstractItemModel
    ↓
QModelIndex
    ↓
parent / child
    ↓
internalPointer
```

Đây chính là bước khó nhất của phần Model/View trước khi chúng ta đi sâu vào **`QModelIndex` ở Buổi 18**.
