# Buổi 17 — `QAbstractItemModel`

Hôm nay chúng ta bước vào phần **khó nhất của Qt Model/View**:

```text
QAbstractItemModel
```

Nếu `QAbstractListModel` là:

```text
A
B
C
```

và `QAbstractTableModel` là:

```text
A | B | C
D | E | F
```

thì `QAbstractItemModel` cho phép biểu diễn dữ liệu **có quan hệ cha → con**:

```text
Python
├── Basic
│   ├── Variable
│   ├── Function
│   └── Class
└── Advanced
    ├── Asyncio
    └── Decorator
```

Đây chính là nền tảng để làm:

* File Explorer
* Folder Tree
* Category Tree
* Story → Chapter
* Database Browser
* Project Explorer
* Organization Tree

---

# 1. Bức tranh tổng thể

Ba loại Model chúng ta đã học:

```text
QAbstractListModel
        ↓
      List
        ↓
   QListView
```

```text
QAbstractTableModel
        ↓
      Table
        ↓
   QTableView
```

và hôm nay:

```text
QAbstractItemModel
        ↓
       Tree
        ↓
    QTreeView
```

---

# 2. Tại sao không dùng `QAbstractListModel`?

List không có quan hệ parent/child:

```text
Python
PySide6
SQLite
Redis
```

Nhưng Tree có:

```text
Python
├── Basic
│   ├── Variable
│   └── Function
└── Advanced
    ├── Asyncio
    └── Decorator
```

Ta cần biết:

```text
Python là parent của Basic
Basic là parent của Variable
Variable không có child
```

Do đó Model phải hiểu:

```text
parent
child
sibling
```

---

# 3. `QAbstractItemModel` không phải chỉ dành cho Tree

Tên của nó là:

```python
QAbstractItemModel
```

vì nó là abstraction tổng quát cho item hierarchy.

Nó có thể biểu diễn:

```text
List
Table
Tree
```

Nhưng khi tự xây tree model, nó đặc biệt hữu ích.

---

# 4. Model Tree đầu tiên

Ta có data:

```python
class TreeNode:

    def __init__(self, name, parent=None):

        self.name = name
        self.parent = parent
        self.children = []
```

Cấu trúc:

```text
Root
├── Python
│   ├── Basic
│   └── Advanced
├── PySide6
│   ├── Widgets
│   └── Model/View
└── SQLite
```

Đây là một **tree data structure** thông thường của Python.

---

# 5. `TreeNode`

Viết đầy đủ:

```python
class TreeNode:

    def __init__(self, name, parent=None):

        self.name = name
        self.parent = parent
        self.children = []

        if parent is not None:
            parent.children.append(self)
```

Sau đó:

```python
root = TreeNode("Root")

python = TreeNode(
    "Python",
    root,
)

basic = TreeNode(
    "Basic",
    python,
)

advanced = TreeNode(
    "Advanced",
    python,
)
```

Ta có:

```text
Root
└── Python
    ├── Basic
    └── Advanced
```

---

# 6. Thêm nhiều node

```python
root = TreeNode("Root")

python = TreeNode("Python", root)

TreeNode("Basic", python)
TreeNode("Advanced", python)

pyside6 = TreeNode("PySide6", root)

TreeNode("Widgets", pyside6)
TreeNode("Model/View", pyside6)

sqlite = TreeNode("SQLite", root)

TreeNode("Query", sqlite)
TreeNode("Transaction", sqlite)
```

Cây:

```text
Root
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

---

# 7. Tại sao cần `parent`?

Mỗi node cần biết:

```text
"Tôi thuộc về ai?"
```

Ví dụ:

```text
Basic
```

có:

```python
basic.parent
```

→

```text
Python
```

Ngược lại:

```python
python.children
```

→

```text
Basic
Advanced
```

Đây chính là hai chiều:

```text
parent
  ↑
  │
child
```

---

# 8. QTreeView cần gì từ Model?

`QTreeView` cần Model trả lời những câu hỏi:

```text
Có child không?
        ↓
rowCount()
```

```text
Item này là gì?
        ↓
data()
```

```text
Parent của item này là ai?
        ↓
parent()
```

```text
Row/column này tương ứng item nào?
        ↓
index()
```

Đây là bốn hàm quan trọng nhất.

---

# 9. Các phương thức chính

Với Tree Model:

```python
rowCount()
columnCount()
data()
index()
parent()
```

Có thể hình dung:

```text
                 QTreeView
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     index()      parent()      data()
        │            │            │
        └────────────┼────────────┘
                     ↓
                  TreeNode
```

---

# 10. `columnCount()`

Tree của chúng ta chỉ có một cột:

```text
Name
```

nên:

```python
def columnCount(
    self,
    parent=QModelIndex(),
):
    return 1
```

---

# 11. `rowCount()`

Đây là phần quan trọng.

Nếu:

```text
Root
├── Python
├── PySide6
└── SQLite
```

thì:

```python
rowCount(root)
```

→ `3`.

Nếu:

```text
Python
├── Basic
└── Advanced
```

thì:

```python
rowCount(python)
```

→ `2`.

Vì vậy `rowCount()` phụ thuộc vào **parent**.

---

# 12. Implement `rowCount()`

```python
def rowCount(
    self,
    parent=QModelIndex(),
):

    if not parent.isValid():
        node = self.root

    else:
        node = parent.internalPointer()

    return len(node.children)
```

Đây là code rất quan trọng.

---

# 13. `QModelIndex` bắt đầu xuất hiện

Ở các buổi trước bạn đã gặp:

```python
index.row()
index.column()
```

Nhưng với Tree Model, ta cần thêm:

```python
index.internalPointer()
```

Nó có thể chứa reference đến object Python tương ứng.

Ví dụ:

```text
QModelIndex
      │
      │ internalPointer()
      ▼
   TreeNode
```

Đây là một trong những kỹ thuật quan trọng nhất của custom Tree Model.

---

# 14. `index()`

Qt hỏi:

> "Hãy cho tôi QModelIndex đại diện cho child ở row X của parent này."

Ta implement:

```python
def index(
    self,
    row,
    column,
    parent=QModelIndex(),
):

    if not self.hasIndex(
        row,
        column,
        parent,
    ):
        return QModelIndex()

    if not parent.isValid():
        parent_node = self.root

    else:
        parent_node = parent.internalPointer()

    child_node = parent_node.children[row]

    return self.createIndex(
        row,
        column,
        child_node,
    )
```

---

# 15. `createIndex()`

Đây là phần rất quan trọng:

```python
self.createIndex(
    row,
    column,
    child_node,
)
```

Tham số thứ ba:

```python
child_node
```

được lưu vào:

```python
QModelIndex.internalPointer()
```

Nói đơn giản:

```text
QModelIndex
     │
     ├── row
     ├── column
     └── internalPointer
              ↓
           TreeNode
```

---

# 16. `parent()`

Bây giờ Qt có một `QModelIndex`.

Ví dụ index đại diện:

```text
Basic
```

Qt hỏi:

> Parent của Basic là ai?

Ta làm:

```python
def parent(self, index):

    if not index.isValid():
        return QModelIndex()

    node = index.internalPointer()

    parent_node = node.parent

    if parent_node is None:
        return QModelIndex()

    if parent_node == self.root:
        return QModelIndex()

    return self.createIndex(
        parent_node.row(),
        0,
        parent_node,
    )
```

Nhưng để làm được:

```python
parent_node.row()
```

TreeNode cần biết vị trí của nó.

---

# 17. Thêm `row()` vào `TreeNode`

```python
class TreeNode:

    def __init__(self, name, parent=None):

        self.name = name
        self.parent = parent
        self.children = []

        if parent is not None:
            parent.children.append(self)

    def row(self):

        if self.parent is None:
            return 0

        return self.parent.children.index(self)
```

Ví dụ:

```text
Python
├── Basic       row = 0
└── Advanced    row = 1
```

---

# 18. `data()`

Bây giờ đơn giản hơn:

```python
def data(
    self,
    index,
    role=Qt.ItemDataRole.DisplayRole,
):

    if not index.isValid():
        return None

    if role == Qt.ItemDataRole.DisplayRole:

        node = index.internalPointer()

        return node.name

    return None
```

---

# 19. Tree Model hoàn chỉnh

Bây giờ ghép lại:

```python
import sys

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    Qt,
)

from PySide6.QtWidgets import (
    QApplication,
    QTreeView,
)


class TreeNode:

    def __init__(self, name, parent=None):

        self.name = name
        self.parent = parent
        self.children = []

        if parent is not None:
            parent.children.append(self)

    def row(self):

        if self.parent is None:
            return 0

        return self.parent.children.index(self)


class TreeModel(QAbstractItemModel):

    def __init__(self, root):

        super().__init__()

        self.root = root

    def columnCount(
        self,
        parent=QModelIndex(),
    ):

        return 1

    def rowCount(
        self,
        parent=QModelIndex(),
    ):

        if not parent.isValid():

            node = self.root

        else:

            node = parent.internalPointer()

        return len(node.children)

    def index(
        self,
        row,
        column,
        parent=QModelIndex(),
    ):

        if not self.hasIndex(
            row,
            column,
            parent,
        ):
            return QModelIndex()

        if not parent.isValid():

            parent_node = self.root

        else:

            parent_node = parent.internalPointer()

        child_node = parent_node.children[row]

        return self.createIndex(
            row,
            column,
            child_node,
        )

    def parent(self, index):

        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()

        parent_node = node.parent

        if (
            parent_node is None
            or parent_node == self.root
        ):
            return QModelIndex()

        return self.createIndex(
            parent_node.row(),
            0,
            parent_node,
        )

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:

            node = index.internalPointer()

            return node.name

        return None


root = TreeNode("Root")

python = TreeNode(
    "Python",
    root,
)

TreeNode(
    "Basic",
    python,
)

TreeNode(
    "Advanced",
    python,
)

pyside6 = TreeNode(
    "PySide6",
    root,
)

TreeNode(
    "Widgets",
    pyside6,
)

TreeNode(
    "Model/View",
    pyside6,
)

sqlite = TreeNode(
    "SQLite",
    root,
)

TreeNode(
    "Query",
    sqlite,
)

TreeNode(
    "Transaction",
    sqlite,
)


app = QApplication(sys.argv)

model = TreeModel(root)

view = QTreeView()

view.setModel(model)

view.resize(500, 400)
view.show()

sys.exit(app.exec())
```

---

# 20. Một điểm quan trọng: Root không hiển thị

Khi chạy:

```text
Root
├── Python
├── PySide6
└── SQLite
```

thực tế `QTreeView` sẽ hiển thị:

```text
Python
├── Basic
└── Advanced

PySide6
├── Widgets
└── Model/View

SQLite
├── Query
└── Transaction
```

`root` ở đây là **invisible root**.

Nó tồn tại để quản lý toàn bộ tree.

---

# 21. Tại sao Root không cần `QModelIndex`?

Đây là convention quan trọng của Qt:

```python
QModelIndex()
```

không hợp lệ:

```text
isValid() == False
```

được sử dụng để đại diện cho:

```text
Root / no parent
```

Do đó:

```python
if not parent.isValid():
```

nghĩa là:

> Đang yêu cầu các node cấp cao nhất.

---

# 22. Hãy hiểu `QModelIndex` bằng hình ảnh

Cây:

```text
Root
├── Python
│   ├── Basic
│   └── Advanced
└── PySide6
    ├── Widgets
    └── Model/View
```

Khi Qt lấy index của:

```text
Basic
```

ta có thể hình dung:

```text
QModelIndex
┌─────────────────────┐
│ row = 0             │
│ column = 0          │
│ internalPointer ────┼──→ TreeNode("Basic")
└─────────────────────┘
```

TreeNode:

```text
Basic
  │
  └── parent
          ↓
       Python
```

Do đó:

```python
index.internalPointer()
```

→ Basic.

và:

```python
index.internalPointer().parent
```

→ Python.

---

# 23. Đây chính là lý do `parent()` hoạt động

```text
QModelIndex
     ↓
internalPointer()
     ↓
TreeNode Basic
     ↓
.parent
     ↓
TreeNode Python
     ↓
createIndex()
     ↓
QModelIndex Python
```

Toàn bộ tree được Qt kết nối thông qua `QModelIndex`.

---

# 24. `index()` và `parent()` là hai chiều

Hãy đặc biệt ghi nhớ:

### Đi xuống

```text
parent QModelIndex
        ↓
      index()
        ↓
child QModelIndex
```

### Đi lên

```text
child QModelIndex
        ↓
     parent()
        ↓
parent QModelIndex
```

Hai hàm này tạo ra navigation trong Tree.

---

# 25. `rowCount()` cũng phụ thuộc vào index

Ví dụ:

```python
model.rowCount()
```

→ số node cấp root.

```python
model.rowCount(python_index)
```

→ số node con của Python.

```python
model.rowCount(basic_index)
```

→ `0`.

Vì Basic không có child.

---

# 26. `hasChildren()`

Qt mặc định có thể suy ra từ `rowCount()`.

Nhưng khi Tree lớn, bạn có thể override:

```python
def hasChildren(self, parent):

    return self.rowCount(parent) > 0
```

Ví dụ:

```text
Python       ▶
Basic
Advanced
```

`Python` có children.

`Basic` không.

---

# 27. Tại sao `QAbstractItemModel` khó?

Vì bạn phải quản lý đồng thời:

```text
Data Structure
       +
QModelIndex
       +
parent()
       +
index()
       +
rowCount()
       +
columnCount()
       +
signals
```

Trong `QAbstractListModel`:

```text
row
 ↓
list[row]
```

rất đơn giản.

Trong Tree:

```text
parent index
      ↓
TreeNode
      ↓
children
      ↓
child index
```

phức tạp hơn nhiều.

---

# 28. Đây là kiến trúc quan trọng

Không nên nghĩ:

```text
QTreeView
    ↓
TreeNode
```

Mà:

```text
Tree Data
    ↓
QAbstractItemModel
    ↓
QTreeView
```

Model là **adapter** giữa cấu trúc dữ liệu Python và Qt.

---

# 29. Ví dụ thực tế: Story App

Đây là nơi kiến trúc bắt đầu rất thú vị.

Giả sử app đọc truyện:

```text
Novel
├── Chapter 1
├── Chapter 2
├── Chapter 3
└── Chapter 4
```

Hoặc nhiều truyện:

```text
Stories
├── Harry Potter
│   ├── Chapter 1
│   ├── Chapter 2
│   └── Chapter 3
│
├── Lord of the Rings
│   ├── Chapter 1
│   └── Chapter 2
│
└── Dune
    ├── Chapter 1
    └── Chapter 2
```

Kiến trúc:

```text
SQLite
   ↓
Repository
   ↓
Story / Chapter
   ↓
TreeModel
   ↓
QTreeView
```

---

# 30. Ví dụ File Explorer

Đây chính là Project cuối phần này:

```text
C:\
├── Users
│   ├── Admin
│   └── Guest
├── Program Files
│   ├── Python
│   └── Qt
└── Windows
    ├── System32
    └── Temp
```

Model:

```text
FileSystem
    ↓
QAbstractItemModel
    ↓
QTreeView
```

Tuy nhiên Qt đã có:

```python
QFileSystemModel
```

nên trong Mini Project chúng ta có thể vừa học cách sử dụng Model có sẵn, vừa hiểu cách tự xây custom model.

---

# 31. `QAbstractItemModel` có nhiều API hơn

Hôm nay chúng ta mới học phần cốt lõi:

```text
rowCount()
columnCount()
index()
parent()
data()
```

Sau này còn:

```text
setData()
flags()
insertRows()
removeRows()
insertColumns()
removeColumns()
mimeData()
dropMimeData()
```

và signals:

```text
dataChanged
rowsInserted
rowsRemoved
layoutChanged
modelReset
```

Không cần học hết trong một lần.

---

# 32. Insert Node

Nếu muốn thêm child:

```text
Python
├── Basic
├── Advanced
└── Asyncio    ← thêm
```

không được đơn giản:

```python
python.children.append(asyncio)
```

mà Model phải thông báo cho View:

```text
beginInsertRows()
       ↓
modify tree
       ↓
endInsertRows()
```

Ví dụ:

```python
self.beginInsertRows(
    parent_index,
    row,
    row,
)

parent_node.children.insert(
    row,
    new_node,
)

self.endInsertRows()
```

---

# 33. Remove Node

Tương tự:

```text
beginRemoveRows()
       ↓
remove node
       ↓
endRemoveRows()
```

Ví dụ:

```python
self.beginRemoveRows(
    parent_index,
    row,
    row,
)

parent_node.children.pop(row)

self.endRemoveRows()
```

---

# 34. Một nguyên tắc cực kỳ quan trọng

Khi thay đổi cấu trúc Model:

```text
INSERT
REMOVE
MOVE
```

phải **thông báo cho Qt**.

Không nên âm thầm sửa:

```python
node.children
```

mà không phát signal/protocol tương ứng.

---

# 35. `dataChanged` vs `beginInsertRows`

Phân biệt thật rõ:

### Sửa dữ liệu

```text
Basic
 ↓
Advanced Python
```

→

```python
dataChanged.emit()
```

### Thêm node

```text
Basic
Advanced
```

→

```text
Basic
Advanced
Asyncio
```

→

```python
beginInsertRows()
endInsertRows()
```

### Xóa node

→

```python
beginRemoveRows()
endRemoveRows()
```

---

# 36. Bài tập 1 — Category Tree

Tạo:

```text
Programming
├── Python
│   ├── Basic
│   └── Advanced
├── Rust
│   ├── Basic
│   └── Ownership
└── Dart
    ├── Basic
    └── Flutter
```

Viết:

```python
TreeNode
TreeModel
```

và hiển thị bằng:

```python
QTreeView
```

---

# 37. Bài tập 2 — Story Tree

Tạo:

```text
Stories
├── Story A
│   ├── Chapter 1
│   ├── Chapter 2
│   └── Chapter 3
│
├── Story B
│   ├── Chapter 1
│   └── Chapter 2
│
└── Story C
    ├── Chapter 1
    └── Chapter 2
```

Yêu cầu:

```text
QTreeView
     ↓
TreeModel
     ↓
StoryNode
```

---

# 38. Bài tập 3 — nhiều column

Thay:

```text
Name
```

bằng:

```text
Name | Type
```

Ví dụ:

```text
Python     | Folder
Basic      | Folder
variable.py| File
```

Lúc này:

```python
columnCount()
```

phải trả về:

```text
2
```

và `data()` phải xử lý:

```text
column 0 → name
column 1 → type
```

Đây là bước rất tốt để chuẩn bị cho File Explorer.

---

# 39. Bài tập 4 — `internalPointer()`

Tự debug:

```python
def data(self, index, role):

    node = index.internalPointer()

    print(
        "row:",
        index.row(),
        "name:",
        node.name,
    )
```

Quan sát khi mở rộng Tree.

Bạn sẽ thấy Qt liên tục làm việc với các `QModelIndex`.

---

# 40. Bài tập 5 — Parent

Viết debug:

```python
def parent(self, index):

    node = index.internalPointer()

    print(
        "Current:",
        node.name,
    )

    print(
        "Parent:",
        node.parent.name
        if node.parent
        else None,
    )

    ...
```

Mục tiêu là thực sự hiểu:

```text
child index
    ↓
internalPointer
    ↓
TreeNode
    ↓
parent
```

---

# 41. Bài tập Deep Dive

Bạn cần trả lời được những câu này trước Buổi 18.

### 1.

Tại sao `QAbstractItemModel` phù hợp với Tree?

### 2.

`QModelIndex` khác gì object `TreeNode`?

### 3.

`internalPointer()` dùng để làm gì?

### 4.

`createIndex()` làm gì?

### 5.

Tại sao Tree Model cần cả:

```text
index()
parent()
```

?

### 6.

`rowCount(parent)` có ý nghĩa gì?

### 7.

Tại sao:

```python
QModelIndex()
```

được dùng để biểu diễn root/no-parent?

### 8.

Nếu `Basic` không có child thì:

```python
rowCount(basic_index)
```

trả về bao nhiêu?

### 9.

Nếu thêm một node, tại sao phải dùng:

```text
beginInsertRows()
endInsertRows()
```

?

### 10.

Model có nên biết `QTreeView` không?

Câu trả lời vẫn là:

> **Không.**

---

# 42. Mental Model của Buổi 17

Đây là sơ đồ bạn nên ghi nhớ:

```text
                         QTreeView
                             │
                             ▼
                     QAbstractItemModel
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
          index()         parent()        data()
             │               │               │
             └───────┬───────┴───────────────┘
                     ▼
                  QModelIndex
                     │
                     │ internalPointer()
                     ▼
                  TreeNode
                 /        \
           parent          children
              ↑               ↓
              └────── Tree ───┘
```

Và flow quan trọng nhất:

```text
QTreeView
    │
    │ index()
    ▼
QModelIndex
    │
    │ internalPointer()
    ▼
TreeNode
    │
    ├── parent
    │
    └── children
```

---

## Bước tiếp theo: Buổi 18 — `QModelIndex`

Buổi 18 chúng ta sẽ **tách riêng `QModelIndex` để học thật sâu**, vì đây là khái niệm mà rất nhiều người học PySide6 bị "kẹt".

Ta sẽ làm rõ:

```text
QModelIndex
├── row()
├── column()
├── parent()
├── child
├── data()
├── isValid()
├── internalPointer()
├── internalId()
└── model()
```

và quan trọng nhất là hiểu chính xác mối quan hệ:

```text
QModelIndex
      ↕
QAbstractItemModel
      ↕
Domain Object
```

Sau đó sang **Buổi 19 — Roles**, chúng ta sẽ biến Tree/Table Model thành Model thực sự mạnh với:

```text
DisplayRole
EditRole
DecorationRole
UserRole
```

để có thể giữ cả **Domain Object / ID / trạng thái / icon / metadata** bên trong Model mà không làm View biết chi tiết dữ liệu.
