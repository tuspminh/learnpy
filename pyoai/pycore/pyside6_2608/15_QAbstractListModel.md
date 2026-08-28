# Buổi 15 — `QAbstractListModel`

Hôm nay là một mốc rất quan trọng trong PySide6.

Từ các buổi trước, chúng ta chủ yếu **sử dụng Model có sẵn**:

```text
QStandardItemModel
QStringListModel
QFileSystemModel
```

Hôm nay chúng ta bắt đầu **tự viết Model**.

Mục tiêu:

```text
Python list
    ↓
QAbstractListModel
    ↓
QListView
```

Sau buổi này, bạn sẽ hiểu được nền tảng của Model/View thay vì chỉ biết sử dụng Widget.

---

# 1. `QAbstractListModel` là gì?

`QAbstractListModel` là base class để xây dựng Model cho dữ liệu dạng list.

Ví dụ dữ liệu:

```python
todos = [
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
]
```

Ta muốn hiển thị:

```text
┌──────────────────────┐
│ Learn Python         │
│ Learn PySide6        │
│ Learn SQLite         │
└──────────────────────┘
```

Kiến trúc:

```text
todos
  │
  ▼
TodoModel
  │
  ▼
QListView
```

---

# 2. Tại sao không dùng `QListWidget`?

Cách đơn giản:

```python
list_widget = QListWidget()

list_widget.addItem("Learn Python")
list_widget.addItem("Learn PySide6")
```

Hoạt động.

Nhưng kiến trúc:

```text
QListWidget
   +
data
```

bị trộn lẫn.

Model/View:

```text
data
 ↓
Model
 ↓
View
```

tách biệt rõ ràng.

Điều này rất quan trọng khi ứng dụng lớn.

---

# 3. Ba phương thức quan trọng nhất

Một `QAbstractListModel` cơ bản cần hiểu:

```python
rowCount()
data()
```

và thường sẽ cần:

```python
flags()
```

Mental model:

```text
QListView
    │
    ├── "Có bao nhiêu item?"
    │          ↓
    │      rowCount()
    │
    └── "Item này chứa gì?"
               ↓
             data()
```

---

# 4. Model đầu tiên

```python
import sys

from PySide6.QtCore import QAbstractListModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QListView


class TodoModel(QAbstractListModel):

    def __init__(self, todos=None):

        super().__init__()

        self.todos = todos or []

    def rowCount(
        self,
        parent=QModelIndex(),
    ):
        return len(self.todos)

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self.todos[index.row()]

        return None


app = QApplication(sys.argv)

todos = [
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
]

model = TodoModel(todos)

view = QListView()

view.setModel(model)

view.resize(400, 300)
view.show()

sys.exit(app.exec())
```

---

# 5. Điều gì xảy ra bên trong?

Khi:

```python
view.setModel(model)
```

View bắt đầu hỏi Model.

Ví dụ:

```text
QListView
   │
   │ "Có bao nhiêu item?"
   ▼
rowCount()
   │
   │ → 3
   ▼
QListView
```

Sau đó:

```text
QListView
   │
   │ "Item row 0 là gì?"
   ▼
data(index, DisplayRole)
   │
   │ → "Learn Python"
   ▼
QListView
```

Tiếp:

```text
row 1 → Learn PySide6
row 2 → Learn SQLite
```

---

# 6. `rowCount()`

Đây là phương thức đầu tiên cần hiểu.

```python
def rowCount(self, parent=QModelIndex()):
    return len(self.todos)
```

Nếu:

```python
self.todos = [
    "A",
    "B",
    "C",
]
```

thì:

```python
rowCount()
```

trả về:

```text
3
```

---

# 7. Vì sao tên là `rowCount()`?

Model/View của Qt dùng khái niệm:

```text
row
column
```

Ngay cả List Model cũng dùng:

```text
row
```

Ví dụ:

```text
row 0 → A
row 1 → B
row 2 → C
```

---

# 8. `columnCount()` có cần không?

Với `QAbstractListModel`, bạn thường **không cần override `columnCount()`**.

List Model về cơ bản:

```text
1 column

row 0
row 1
row 2
...
```

Trong khi Table Model:

```text
row × column
```

Buổi 16 chúng ta sẽ học `QAbstractTableModel`.

---

# 9. `data()`

Đây là phương thức quan trọng nhất.

```python
def data(self, index, role):
```

Qt hỏi:

```text
"Ô / item này chứa dữ liệu gì?"
```

---

# 10. `QModelIndex`

Ví dụ View hỏi:

```text
row = 1
```

Model nhận:

```python
index
```

Sau đó:

```python
index.row()
```

→

```text
1
```

Ta lấy data:

```python
return self.todos[index.row()]
```

---

# 11. `isValid()`

Luôn nên kiểm tra:

```python
if not index.isValid():
    return None
```

Vì có thể Qt truyền vào một index không hợp lệ.

Pattern nên nhớ:

```python
def data(self, index, role):

    if not index.isValid():
        return None

    ...
```

---

# 12. `role` là gì?

Đây là phần cực kỳ quan trọng.

Qt không chỉ hỏi:

```text
"data là gì?"
```

Nó hỏi:

```text
"Data dùng cho mục đích gì?"
```

Thông qua:

```python
role
```

Ví dụ:

```python
Qt.ItemDataRole.DisplayRole
```

---

# 13. `DisplayRole`

Dùng cho text hiển thị.

```python
if role == Qt.ItemDataRole.DisplayRole:
    return self.todos[index.row()]
```

Ví dụ:

```text
row 0
 ↓
"Learn Python"
```

View hiển thị:

```text
Learn Python
```

---

# 14. Các Role sẽ học sâu ở Buổi 19

Một số role quan trọng:

```text
DisplayRole
EditRole
DecorationRole
ToolTipRole
ForegroundRole
BackgroundRole
CheckStateRole
UserRole
```

Hôm nay tập trung:

```text
DisplayRole
```

---

# 15. Tại sao `data()` nhận `role`?

Ví dụ cùng một item:

```text
Learn Python
```

Qt có thể hỏi:

```text
DisplayRole
```

→ text.

Hoặc:

```text
DecorationRole
```

→ icon.

Hoặc:

```text
ToolTipRole
```

→ tooltip.

Do đó:

```python
def data(index, role):
```

có thể trả về nhiều loại thông tin cho cùng một item.

---

# 16. Ví dụ thêm Tooltip

```python
def data(self, index, role):

    if not index.isValid():
        return None

    todo = self.todos[index.row()]

    if role == Qt.ItemDataRole.DisplayRole:
        return todo

    if role == Qt.ItemDataRole.ToolTipRole:
        return f"Todo: {todo}"

    return None
```

Bây giờ hover:

```text
Learn Python
```

có thể hiện:

```text
Todo: Learn Python
```

---

# 17. `flags()`

Đây là phương thức cho biết item có khả năng gì.

Ví dụ:

```text
selectable
enabled
editable
drag
drop
```

Một model cơ bản:

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

# 18. Giải thích flags

```python
Qt.ItemFlag.ItemIsEnabled
```

Item được enable.

```python
Qt.ItemFlag.ItemIsSelectable
```

User có thể select.

Kết hợp:

```python
Qt.ItemFlag.ItemIsEnabled
| Qt.ItemFlag.ItemIsSelectable
```

---

# 19. Cho phép Edit

Nếu muốn user sửa item:

```python
return (
    Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEditable
)
```

Nhưng chỉ thêm flag chưa đủ.

Cần:

```python
setData()
```

Chúng ta sẽ làm ngay sau đây.

---

# 20. `setData()`

Giả sử:

```text
Learn Python
```

User double-click và sửa thành:

```text
Learn Advanced Python
```

View sẽ yêu cầu Model:

```python
model.setData(index, value, role)
```

Model phải xử lý.

---

# 21. Model Editable

```python
class TodoModel(QAbstractListModel):

    def __init__(self, todos=None):

        super().__init__()

        self.todos = todos or []

    def rowCount(self, parent=QModelIndex()):

        return len(self.todos)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self.todos[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return self.todos[index.row()]

        return None

    def flags(self, index):

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

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

        self.todos[index.row()] = value

        self.dataChanged.emit(
            index,
            index,
            [role],
        )

        return True
```

---

# 22. `dataChanged`

Đây là một khái niệm **cực kỳ quan trọng**.

Sau khi sửa:

```python
self.todos[index.row()] = value
```

Model phải thông báo:

```python
self.dataChanged.emit(...)
```

Flow:

```text
User sửa
   ↓
setData()
   ↓
thay đổi dữ liệu
   ↓
dataChanged.emit()
   ↓
QListView cập nhật
```

---

# 23. Tại sao phải emit signal?

Nếu không:

```python
self.todos[index.row()] = value
```

data Python đã thay đổi.

Nhưng View có thể **không biết** rằng data đã thay đổi.

Vì vậy:

```text
Data thay đổi
     ↓
Model phát signal
     ↓
View refresh
```

Đây là nguyên tắc nền tảng của Qt Model/View.

---

# 24. Chạy Editable Model

```python
import sys

from PySide6.QtCore import QAbstractListModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QListView


class TodoModel(QAbstractListModel):

    def __init__(self, todos=None):

        super().__init__()

        self.todos = todos or []

    def rowCount(self, parent=QModelIndex()):

        return len(self.todos)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role in (
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole,
        ):
            return self.todos[index.row()]

        return None

    def flags(self, index):

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

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

        self.todos[index.row()] = str(value)

        self.dataChanged.emit(
            index,
            index,
            [Qt.ItemDataRole.DisplayRole],
        )

        return True


app = QApplication(sys.argv)

model = TodoModel([
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
])

view = QListView()

view.setModel(model)

view.resize(400, 300)
view.show()

sys.exit(app.exec())
```

Double-click item → sửa.

---

# 25. Flow hoàn chỉnh

Bây giờ hãy nhìn toàn bộ:

```text
                  QListView
                      │
                      │ rowCount()
                      ▼
                 TodoModel
                      │
                      │ data()
                      ▼
                    Data
```

Khi user edit:

```text
User
 ↓
QListView
 ↓
setData()
 ↓
TodoModel
 ↓
self.todos[index.row()] = value
 ↓
dataChanged.emit()
 ↓
QListView
```

---

# 26. Đây chính là MVC-ish

Qt Model/View có thể hình dung:

```text
             MODEL
               │
               │ data
               ▼
             VIEW
               │
               │ interaction
               ▼
             MODEL
```

Model chịu trách nhiệm:

```text
data
data access
data modification
signals
```

View chịu trách nhiệm:

```text
display
selection
interaction
```

---

# 27. Thêm `insertRows()`

Bây giờ chúng ta muốn:

```text
Add Todo
```

Model có thể implement:

```python
def insertRows(
    self,
    row,
    count,
    parent=QModelIndex(),
):
```

Đây là API chuẩn của Qt.

---

# 28. Ví dụ thêm một Todo

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
        self.todos.insert(row, "")

    self.endInsertRows()

    return True
```

---

# 29. Tại sao cần `beginInsertRows()`?

Không nên chỉ:

```python
self.todos.insert(row, "")
```

vì View không biết cấu trúc Model thay đổi.

Đúng:

```text
beginInsertRows()
      ↓
modify data
      ↓
endInsertRows()
```

Qt sẽ cập nhật View đúng cách.

---

# 30. Xóa item

Tương tự:

```python
def removeRows(
    self,
    row,
    count,
    parent=QModelIndex(),
):

    self.beginRemoveRows(
        parent,
        row,
        row + count - 1,
    )

    del self.todos[row:row + count]

    self.endRemoveRows()

    return True
```

Flow:

```text
beginRemoveRows()
       ↓
delete data
       ↓
endRemoveRows()
```

---

# 31. Đây là pattern cần nhớ

### Insert

```text
beginInsertRows
      ↓
modify data
      ↓
endInsertRows
```

### Remove

```text
beginRemoveRows
      ↓
modify data
      ↓
endRemoveRows
```

### Update

```text
modify data
      ↓
dataChanged.emit()
```

---

# 32. Tại sao không emit `dataChanged` khi insert?

Vì:

```text
dataChanged
```

có nghĩa:

> Data của những index hiện có đã thay đổi.

Còn insert là:

> Cấu trúc Model đã thay đổi.

Do đó phải dùng:

```text
beginInsertRows()
endInsertRows()
```

---

# 33. `QAbstractListModel` + Todo

Đây chính là kiến trúc chúng ta sẽ tiến tới:

```text
TodoRepository
       │
       ▼
    TodoModel
       │
       ▼
   QListView
```

Ví dụ:

```text
SQLite
  ↓
Repository
  ↓
list[Todo]
  ↓
TodoModel
  ↓
QListView
```

---

# 34. Nhưng có một vấn đề

Nếu:

```python
self.todos
```

là:

```python
[
    Todo(...),
    Todo(...),
    Todo(...),
]
```

thì `data()` có thể trả về:

```text
Todo object
```

nhưng View cần:

```text
string
```

Đây là lúc **Roles** trở nên quan trọng.

Buổi 19 chúng ta sẽ học rất sâu:

```text
DisplayRole
EditRole
DecorationRole
UserRole
```

để Model có thể cung cấp nhiều loại dữ liệu.

---

# 35. Todo Model thực tế hơn

Ví dụ:

```python
@dataclass
class Todo:
    id: int
    title: str
    completed: bool
```

Data:

```python
todos = [
    Todo(1, "Learn Python", False),
    Todo(2, "Learn PySide6", False),
    Todo(3, "Learn SQLite", True),
]
```

Model:

```text
Todo
 ↓
TodoModel
 ↓
QListView
```

View chỉ hiển thị:

```text
Learn Python
Learn PySide6
Learn SQLite
```

Nhưng Model vẫn giữ:

```text
id
title
completed
```

Sau này:

```text
User click
   ↓
QModelIndex
   ↓
UserRole
   ↓
Todo ID
```

Đây là pattern rất mạnh.

---

# 36. Một Model tốt không nên biết View

Điều rất quan trọng:

Không nên viết:

```python
class TodoModel:

    self.list_view = ...
```

Model không nên biết:

```text
QListView
QTableView
Widget
Window
```

Model chỉ biết:

```text
data
index
roles
signals
```

View biết Model:

```text
QListView
   ↓
TodoModel
```

Nhưng Model không cần biết View.

---

# 37. Model độc lập với UI

Điều này cho phép:

```text
                 TodoModel
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
      QListView           QTableView
```

Cùng một nguồn dữ liệu có thể phục vụ nhiều View.

---

# 38. Đây là điểm khác biệt lớn

Widget-centric:

```text
TodoWidget
    ↓
Todo data
```

Model/View:

```text
             TodoModel
             /       \
            /         \
           ↓           ↓
     QListView     QTableView
```

---

# 39. `QAbstractListModel` khi nào dùng?

Dùng khi dữ liệu có dạng:

```text
A
B
C
D
```

Ví dụ:

* Todo list
* Playlist
* Search results
* Story list
* Chapter list
* User list
* Notification list

Nếu dữ liệu có nhiều columns:

```text
ID | Name | Status
```

→ `QAbstractTableModel`.

Nếu dữ liệu hierarchical:

```text
Story
├── Chapter
└── Chapter
```

→ `QAbstractItemModel`.

---

# 40. So sánh

```text
QAbstractListModel
        ↓
      List
```

```text
QAbstractTableModel
        ↓
      Table
```

```text
QAbstractItemModel
        ↓
      Tree
```

Đây chính là ba Model quan trọng trong roadmap của chúng ta.

---

# 41. Bài tập 1

Tạo:

```python
class StudentModel(QAbstractListModel):
    ...
```

Data:

```python
students = [
    "An",
    "Bình",
    "Cường",
    "Dũng",
]
```

Hiển thị bằng:

```text
QListView
```

---

# 42. Bài tập 2

Thêm:

```python
Qt.ItemDataRole.ToolTipRole
```

Hover:

```text
An
```

hiển thị:

```text
Student: An
```

---

# 43. Bài tập 3

Cho phép edit:

```text
An
```

→

```text
Nguyễn An
```

Bạn cần implement:

```python
flags()
setData()
dataChanged.emit()
```

---

# 44. Bài tập 4

Thêm:

```python
insertRows()
```

để thêm item.

Flow:

```text
Add button
     ↓
model.insertRows()
     ↓
beginInsertRows()
     ↓
insert data
     ↓
endInsertRows()
```

---

# 45. Bài tập 5

Implement:

```python
removeRows()
```

Cho phép xóa item đang selected.

Kiến trúc:

```text
QListView
   ↓
selectionModel()
   ↓
selectedIndexes()
   ↓
model.removeRows()
```

---

# 46. Bài tập 6 — Todo Model

Tạo:

```python
@dataclass
class Todo:
    id: int
    title: str
    completed: bool
```

Data:

```text
1 | Learn Python | False
2 | Learn PySide6 | False
3 | Learn SQLite | True
```

Sau đó viết:

```python
class TodoModel(QAbstractListModel):
    ...
```

View:

```text
☐ Learn Python
☐ Learn PySide6
☑ Learn SQLite
```

Chưa cần checkbox thật. Trước tiên hãy làm cho `DisplayRole` hiển thị:

```text
☐ Learn Python
☐ Learn PySide6
☑ Learn SQLite
```

---

# 47. Bài tập Deep Dive

Hãy tự trả lời 10 câu này.

### 1.

`QAbstractListModel` có nhiệm vụ gì?

### 2.

`QListView` có lưu dữ liệu không?

### 3.

`rowCount()` trả về gì?

### 4.

`data()` dùng để làm gì?

### 5.

`role` dùng để làm gì?

### 6.

Tại sao cần:

```python
index.isValid()
```

?

### 7.

`flags()` dùng để làm gì?

### 8.

Tại sao `setData()` cần:

```python
dataChanged.emit()
```

?

### 9.

Tại sao thêm row phải dùng:

```python
beginInsertRows()
endInsertRows()
```

thay vì chỉ:

```python
list.insert()
```

?

### 10.

Tại sao Model không nên giữ reference đến `QListView`?

---

# 48. Mental Model cuối buổi

Đây là phần bạn **phải thuộc**:

```text
                    QLISTVIEW
                        │
                        │ hỏi
                        ▼
                 QABSTRACTLISTMODEL
                        │
             ┌──────────┼──────────┐
             │          │          │
             ▼          ▼          ▼
         rowCount()    data()    flags()
             │          │          │
             ▼          ▼          ▼
           count      value      capability
```

Khi update:

```text
Model data thay đổi
       │
       ▼
dataChanged.emit()
       │
       ▼
QListView cập nhật
```

Khi insert:

```text
beginInsertRows()
       │
       ▼
thay đổi list
       │
       ▼
endInsertRows()
```

Khi remove:

```text
beginRemoveRows()
       │
       ▼
xóa khỏi list
       │
       ▼
endRemoveRows()
```

---

# 49. Kiến trúc chúng ta đang xây

Bạn có thể bắt đầu nhìn toàn bộ roadmap như sau:

```text
                   DATA
                    │
                    ▼
              Repository
                    │
                    ▼
            QAbstractListModel
                    │
                    ▼
                QListView
                    │
                    ▼
                  User
```

Đến **Buổi 16**, chúng ta sẽ nâng cấp từ List sang Table:

```text
              TodoRepository
                    │
                    ▼
          QAbstractTableModel
                    │
                    ▼
                QTableView
```

và đây sẽ là nền tảng cực kỳ quan trọng để sau này kết hợp với **SQLite + Repository Pattern + PySide6**, đúng kiểu kiến trúc ứng dụng thực tế.
