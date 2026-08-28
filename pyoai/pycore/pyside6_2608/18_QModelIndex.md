# Buổi 18 — `QModelIndex` Deep Dive

Hôm nay chúng ta học một trong những khái niệm **quan trọng nhất của Qt Model/View**:

```python
QModelIndex
```

Nếu chưa hiểu `QModelIndex`, bạn sẽ rất khó làm chủ:

```text
QTreeView
QTableView
QAbstractItemModel
Delegate
Selection Model
Proxy Model
```

Mục tiêu hôm nay không phải học thuộc API, mà phải hiểu:

> **`QModelIndex` thực sự là gì và nó kết nối View ↔ Model ↔ Data như thế nào?**

---

# 1. `QModelIndex` là gì?

Đừng hiểu nó đơn giản là:

> "index của một item".

Hãy hiểu:

> **`QModelIndex` là một handle/địa chỉ do Qt tạo ra để xác định một item trong Model.**

Ví dụ Table:

```text
       0          1          2
    ┌──────────┬──────────┬──────────┐
0   │ 1        │ Python   │ Active   │
    ├──────────┼──────────┼──────────┤
1   │ 2        │ PySide6  │ Active   │
    ├──────────┼──────────┼──────────┤
2   │ 3        │ SQLite   │ Done     │
    └──────────┴──────────┴──────────┘
```

Cell:

```text
Python
```

có:

```text
row    = 0
column = 1
```

Nhưng với Tree thì chỉ `row` + `column` **chưa đủ**.

---

# 2. Tại sao Tree cần QModelIndex phức tạp hơn?

Tree:

```text
Python
├── Basic
│   ├── Variable
│   └── Function
└── Advanced
    └── Asyncio
```

Có thể có:

```text
row = 0
column = 0
```

cho:

```text
Basic
```

Nhưng:

```text
Variable
```

cũng có:

```text
row = 0
column = 0
```

Nếu chỉ có:

```text
row = 0
column = 0
```

thì không thể phân biệt:

```text
Basic
Variable
```

Do đó `QModelIndex` còn phải biết **context/parent** của item.

---

# 3. Mental Model

Hãy hình dung:

```text
QModelIndex
┌──────────────────────────┐
│ row                      │
│ column                   │
│ parent/context            │
│ model                    │
│ internalPointer          │
│ internalId               │
└──────────────────────────┘
```

Nó không phải chính dữ liệu.

Ví dụ:

```python
index
```

không phải:

```python
Todo(...)
```

mà nó giúp Model tìm tới:

```text
Todo
```

---

# 4. `QModelIndex` không phải Domain Object

Đây là điểm rất quan trọng.

Ví dụ:

```python
@dataclass
class Todo:
    id: int
    title: str
```

Ta có:

```python
todo = Todo(
    id=1,
    title="Learn Python",
)
```

và:

```python
index
```

Hai thứ hoàn toàn khác nhau:

```text
Todo
 ↓
Domain data

QModelIndex
 ↓
Qt model location
```

---

# 5. Quan hệ giữa chúng

Trong kiến trúc:

```text
QTableView
     │
     ▼
QModelIndex
     │
     ▼
QAbstractTableModel
     │
     ▼
Todo
```

View nói:

> "Tôi muốn item này."

Thông qua:

```python
QModelIndex
```

Model xác định:

```python
index.row()
index.column()
```

và lấy:

```python
Todo
```

---

# 6. `row()`

```python
index.row()
```

trả về row của item.

Ví dụ:

```text
       ID       Title
    ┌───────┬──────────┐
0   │ 1     │ Python   │
1   │ 2     │ PySide6  │
2   │ 3     │ SQLite   │
    └───────┴──────────┘
```

Index của:

```text
PySide6
```

có:

```python
index.row()
```

→

```text
1
```

---

# 7. `column()`

```python
index.column()
```

Ví dụ:

```text
       0          1
    ┌───────┬──────────┐
0   │ 1     │ Python   │
1   │ 2     │ PySide6  │
2   │ 3     │ SQLite   │
    └───────┴──────────┘
```

Index của:

```text
PySide6
```

→

```python
index.column()
```

→ `1`.

---

# 8. `isValid()`

Một `QModelIndex` có thể **invalid**.

Kiểm tra:

```python
if not index.isValid():
    return
```

Đây là pattern bạn sẽ thấy liên tục trong Qt Model/View.

Ví dụ:

```python
def data(self, index, role):

    if not index.isValid():
        return None
```

---

# 9. Invalid QModelIndex

Ta tạo:

```python
index = QModelIndex()
```

Index này:

```python
index.isValid()
```

→

```text
False
```

Nó thường đại diện cho:

```text
không có item
```

hoặc trong Tree Model:

```text
invisible root
```

---

# 10. Vì sao Root dùng QModelIndex rỗng?

Ví dụ:

```text
Root
├── Python
├── PySide6
└── SQLite
```

`Root` không nhất thiết phải có một `QModelIndex`.

Qt convention:

```python
QModelIndex()
```

được dùng để nói:

> Không có parent.

Do đó:

```python
model.rowCount(QModelIndex())
```

nghĩa là:

> Có bao nhiêu item ở cấp root?

---

# 11. `model()`

Một `QModelIndex` biết Model nào tạo ra nó.

```python
index.model()
```

Ví dụ:

```python
model = index.model()
```

Bạn có thể kiểm tra:

```python
print(index.model())
```

Mental model:

```text
QModelIndex
      │
      └── model()
             ↓
       QAbstractItemModel
```

---

# 12. `data()`

`QModelIndex` có:

```python
index.data()
```

Ví dụ:

```python
value = index.data()
```

thường tương ứng:

```python
model.data(
    index,
    Qt.ItemDataRole.DisplayRole,
)
```

Do đó:

```python
index.data()
```

là shortcut tiện lợi.

---

# 13. `index.data(role)`

Bạn cũng có thể:

```python
index.data(
    Qt.ItemDataRole.DisplayRole
)
```

Sau này khi học Roles:

```python
index.data(
    Qt.ItemDataRole.UserRole
)
```

sẽ cực kỳ hữu ích.

---

# 14. `internalPointer()`

Đây là phần **quan trọng nhất hôm nay**.

Trong custom Tree Model, chúng ta thường:

```python
return self.createIndex(
    row,
    column,
    node,
)
```

Tham số:

```python
node
```

được lưu làm internal pointer.

Sau đó:

```python
node = index.internalPointer()
```

ta lấy lại được:

```text
TreeNode
```

---

# 15. Flow của `internalPointer()`

Ví dụ:

```python
node = TreeNode("Python")
```

Model:

```python
index = self.createIndex(
    0,
    0,
    node,
)
```

Sau đó:

```python
index.internalPointer()
```

→

```python
node
```

Flow:

```text
TreeNode
    │
    │ createIndex()
    ▼
QModelIndex
    │
    │ internalPointer()
    ▼
TreeNode
```

Nó giống như một cây cầu.

---

# 16. Tại sao cần `internalPointer()`?

Hãy xem Tree:

```text
Python
├── Basic
└── Advanced
```

Khi Qt gọi:

```python
data(index)
```

Model cần biết:

> Index này đại diện cho node nào?

Ta làm:

```python
node = index.internalPointer()
```

Sau đó:

```python
return node.name
```

Không cần tìm kiếm toàn bộ tree.

---

# 17. Đây là code rất quan trọng

```python
def data(
    self,
    index,
    role=Qt.ItemDataRole.DisplayRole,
):

    if not index.isValid():
        return None

    node = index.internalPointer()

    if role == Qt.ItemDataRole.DisplayRole:
        return node.name

    return None
```

Bạn nên thuộc **logic**, không cần thuộc từng ký tự.

---

# 18. `internalId()`

Ngoài:

```python
internalPointer()
```

Qt còn có:

```python
index.internalId()
```

Nó cung cấp một ID nội bộ dạng integer.

Khi tạo index có thể dùng:

```python
createIndex(
    row,
    column,
    id,
)
```

thay vì pointer.

Nhưng khi viết Tree Model bằng Python, pattern:

```python
internalPointer()
```

thường dễ hiểu và tiện hơn.

---

# 19. Pointer vs ID

Có thể hình dung:

```text
internalPointer
        ↓
Python object
```

hoặc:

```text
internalId
        ↓
integer ID
```

Ví dụ:

```text
internalPointer → TreeNode("Python")
```

hoặc:

```text
internalId → 12345
```

Trong các custom model Python, chúng ta sẽ ưu tiên hiểu và sử dụng:

```python
internalPointer()
```

trước.

---

# 20. `parent()`

Đây là phần kết nối trực tiếp với Buổi 17.

Ví dụ:

```text
Python
├── Basic
│   ├── Variable
│   └── Function
└── Advanced
```

Index của:

```text
Variable
```

có:

```python
node = index.internalPointer()
```

→ `Variable`.

Sau đó:

```python
parent_node = node.parent
```

→ `Basic`.

Sau đó Model tạo:

```python
parent_index = self.createIndex(
    parent_node.row(),
    0,
    parent_node,
)
```

---

# 21. `index()` và `parent()`

Đây là cặp API bạn phải hiểu cực rõ.

### Đi từ parent xuống child

```text
parent QModelIndex
        ↓
      index()
        ↓
child QModelIndex
```

### Đi từ child lên parent

```text
child QModelIndex
        ↓
     parent()
        ↓
parent QModelIndex
```

Hai chiều:

```text
             Tree
              ↕
           QModelIndex
              ↕
             Model
```

---

# 22. Ví dụ cụ thể

Tree:

```text
Python
├── Basic
│   ├── Variable
│   └── Function
└── Advanced
```

Giả sử có:

```python
python_index
basic_index
variable_index
```

Ta có:

```python
model.parent(variable_index)
```

→ `basic_index`.

Và:

```python
model.parent(basic_index)
```

→ `python_index`.

Còn:

```python
model.parent(python_index)
```

→ invalid `QModelIndex()`.

---

# 23. `parent()` của root

Root:

```text
Root
├── Python
└── PySide6
```

`Python` là top-level item.

Do đó:

```python
model.parent(python_index)
```

→

```python
QModelIndex()
```

Không phải:

```python
root_index
```

vì root đang là **invisible root**.

---

# 24. `sibling()`

`QModelIndex` còn có:

```python
index.sibling(
    row,
    column,
)
```

Ví dụ:

```text
Python
├── Basic
├── Advanced
└── Asyncio
```

Nếu đang ở:

```text
Basic
```

có thể lấy sibling:

```python
basic_index.sibling(
    1,
    0,
)
```

→ `Advanced`.

Sibling nghĩa là:

> item có cùng parent.

---

# 25. `child` trong Qt hiện đại

Bạn có thể gặp code cũ kiểu:

```python
index.child(...)
```

Nhưng với custom model hiện đại, cách tư duy chính vẫn là:

```python
model.index(
    row,
    column,
    parent,
)
```

và:

```python
model.parent(index)
```

Không nên phụ thuộc vào các API cũ chỉ vì thấy chúng trong tutorial cũ.

---

# 26. `QModelIndex` không nên được lưu tùy tiện

Đây là một quy tắc quan trọng.

Không nên thiết kế Domain:

```python
class Todo:
    selected_index: QModelIndex
```

Sai kiến trúc.

Domain không nên biết:

```text
PySide6
QModelIndex
QWidget
QTableView
```

Nên:

```text
Domain
  ↓
Todo
```

còn:

```text
UI
  ↓
QModelIndex
```

---

# 27. QModelIndex thuộc Presentation Layer

Kiến trúc:

```text
┌─────────────────────┐
│       Domain        │
│                     │
│ Todo                │
│ Story               │
│ Chapter             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│        Model        │
│                     │
│ QAbstractTableModel │
│ QAbstractItemModel  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│         View        │
│                     │
│ QTableView          │
│ QTreeView           │
└─────────────────────┘
```

`QModelIndex` nằm ở tầng Model/View.

---

# 28. QModelIndex và SQLite ID

Trong app thực tế, bạn sẽ thường có:

```text
Todo
├── id = 100
├── title
└── status
```

và:

```text
QModelIndex
├── row = 3
├── column = 1
└── internalPointer → Todo
```

Đừng nhầm:

```text
Todo.id
```

với:

```text
index.row()
```

Hai thứ khác nhau.

Ví dụ:

```text
Database ID = 100
Table row   = 3
```

hoàn toàn bình thường.

---

# 29. Đây là lý do `UserRole` rất quan trọng

Ở Buổi 19 chúng ta sẽ học:

```python
Qt.ItemDataRole.UserRole
```

để có thể:

```python
index.data(
    Qt.ItemDataRole.UserRole
)
```

trả về:

```python
todo.id
```

Ví dụ:

```text
DisplayRole
    ↓
"Learn Python"

UserRole
    ↓
100
```

Đây là pattern cực kỳ hữu ích khi làm:

```text
QListView
QTableView
QTreeView
```

---

# 30. Selection và QModelIndex

Sau này:

```python
selection_model = view.selectionModel()
```

có thể lấy:

```python
indexes = selection_model.selectedIndexes()
```

Kết quả:

```text
QModelIndex
QModelIndex
QModelIndex
```

Ví dụ user chọn:

```text
ID = 100
Title = Learn Python
Status = Active
```

View không trả trực tiếp:

```python
Todo(...)
```

mà trả:

```python
QModelIndex
```

Model dùng index để tìm dữ liệu.

---

# 31. Vì vậy Model/View rất linh hoạt

Một View:

```text
QTableView
```

không cần biết:

```text
Todo
Student
Story
Chapter
File
```

Nó chỉ biết:

```text
QModelIndex
```

Model chịu trách nhiệm biến:

```text
QModelIndex
```

thành:

```text
data
```

Đây là một trong những lý do Qt Model/View mạnh.

---

# 32. Debug `QModelIndex`

Bạn có thể viết:

```python
def debug_index(index):

    print("valid:", index.isValid())
    print("row:", index.row())
    print("column:", index.column())
    print("data:", index.data())
    print("model:", index.model())
```

Với Tree Model:

```python
node = index.internalPointer()

print("node:", node.name)
```

---

# 33. Một ví dụ hoàn chỉnh

Ta tạo Tree:

```text
Programming
├── Python
│   ├── Asyncio
│   └── Decorator
└── PySide6
    ├── Widgets
    └── Model/View
```

Khi user click:

```text
Decorator
```

ta có:

```python
index
```

Sau đó:

```python
index.row()
```

→ `1`

```python
index.column()
```

→ `0`

```python
index.data()
```

→ `"Decorator"`

```python
index.internalPointer()
```

→

```text
TreeNode("Decorator")
```

và:

```python
index.model()
```

→ `TreeModel`.

---

# 34. Một flow hoàn chỉnh

Khi user click vào item:

```text
User
 ↓
QTreeView
 ↓
QModelIndex
 ↓
SelectionModel
 ↓
Model
 ↓
internalPointer()
 ↓
TreeNode
```

Nếu cần parent:

```text
QModelIndex
 ↓
Model.parent()
 ↓
internalPointer()
 ↓
TreeNode.parent
 ↓
createIndex()
 ↓
Parent QModelIndex
```

---

# 35. QModelIndex không phải "con trỏ sống mãi"

Một lỗi người mới thường mắc:

```python
self.current_index = index
```

rồi giả định index đó luôn hợp lệ sau mọi thay đổi Model.

Nhưng khi Model:

```text
insert
remove
move
reset
sort
```

cấu trúc có thể thay đổi.

Qt có cơ chế:

```python
QPersistentModelIndex
```

cho trường hợp cần một index có tính bền vững hơn.

Chúng ta chưa cần dùng ngay.

Chỉ cần nhớ:

> `QModelIndex` nên được xem là một handle do Model/View cung cấp, không phải ID database bất biến.

---

# 36. `QPersistentModelIndex`

Khi thực sự cần giữ index qua các thay đổi Model:

```python
from PySide6.QtCore import QPersistentModelIndex
```

Ví dụ:

```python
persistent = QPersistentModelIndex(index)
```

Nhưng **không nên dùng nó thay cho mọi `QModelIndex`**.

Thông thường:

```python
QModelIndex
```

là đủ.

---

# 37. QModelIndex và Proxy Model

Sau này chúng ta sẽ học:

```text
Source Model
     ↓
Proxy Model
     ↓
View
```

Ví dụ:

```text
Database
   ↓
TodoTableModel
   ↓
QSortFilterProxyModel
   ↓
QTableView
```

Lúc này View nhận:

```python
proxy_index
```

không nhất thiết là index của source model.

Có thể cần:

```python
proxy.mapToSource(index)
```

và:

```python
proxy.mapFromSource(index)
```

Đây là lý do hiểu `QModelIndex` từ bây giờ rất quan trọng.

---

# 38. Một ví dụ với Table Model

Giả sử:

```python
class TodoTableModel(QAbstractTableModel):
    ...
```

View:

```python
view = QTableView()
view.setModel(model)
```

Khi user click cell:

```python
index = view.currentIndex()
```

Bạn có:

```python
index.row()
index.column()
index.data()
```

Ví dụ:

```python
print(
    index.row(),
    index.column(),
    index.data(),
)
```

có thể ra:

```text
2 1 Learn SQLite
```

---

# 39. Lấy Todo từ QModelIndex

Nếu Model dùng `internalPointer()`:

```python
todo = index.internalPointer()
```

thì:

```python
print(todo.id)
print(todo.title)
```

Tuy nhiên với `QAbstractTableModel` thông thường, bạn thường quản lý mapping:

```python
todo = self.todos[index.row()]
```

Còn `internalPointer()` đặc biệt hữu ích trong custom hierarchical model.

---

# 40. Hai phong cách mapping

### Table

```text
QModelIndex
    ↓
row()
    ↓
self.todos[row]
```

### Tree

```text
QModelIndex
    ↓
internalPointer()
    ↓
TreeNode
```

Đây là distinction rất đáng nhớ.

---

# 41. Sai lầm phổ biến #1

Viết:

```python
node = index.internalPointer()
```

trước khi kiểm tra:

```python
if not index.isValid():
```

Nên:

```python
if not index.isValid():
    return None

node = index.internalPointer()
```

---

# 42. Sai lầm phổ biến #2

Nhầm:

```python
index.row()
```

với:

```python
database_id
```

Ví dụ:

```text
Database:
ID = 500

View:
row = 0
```

Không có gì mâu thuẫn.

---

# 43. Sai lầm phổ biến #3

Lưu `QModelIndex` vào Domain.

Không nên:

```python
@dataclass
class Todo:
    id: int
    title: str
    index: QModelIndex   # ❌
```

Nên:

```python
@dataclass
class Todo:
    id: int
    title: str
```

---

# 44. Sai lầm phổ biến #4

Tìm item bằng cách scan toàn bộ tree:

```python
for node in all_nodes:
    if node.name == "Python":
        ...
```

trong khi index đã có:

```python
internalPointer()
```

Custom Tree Model có thể truy cập trực tiếp object tương ứng.

---

# 45. Bài tập 1 — QModelIndex cơ bản

Tạo:

```python
model = TodoTableModel(...)
view = QTableView()
```

Khi click cell:

```python
index = view.currentIndex()
```

in:

```text
row
column
data
isValid
model
```

---

# 46. Bài tập 2 — Tree QModelIndex

Tạo:

```text
Python
├── Basic
│   ├── Variable
│   └── Function
└── Advanced
```

Khi click `Variable`, in:

```text
Current: Variable
Parent: Basic
```

Dựa trên:

```python
node = index.internalPointer()
parent = node.parent
```

---

# 47. Bài tập 3 — Đi lên cây

Cho:

```text
Python
└── Advanced
    └── Asyncio
```

Từ:

```python
asyncio_index
```

lấy parent:

```python
advanced_index = model.parent(
    asyncio_index
)
```

rồi:

```python
python_index = model.parent(
    advanced_index
)
```

Cuối cùng:

```text
Asyncio
   ↑
Advanced
   ↑
Python
```

---

# 48. Bài tập 4 — Đi xuống cây

Từ:

```python
python_index
```

lấy child:

```python
advanced_index = model.index(
    0,
    0,
    python_index,
)
```

Sau đó:

```python
print(
    advanced_index.data()
)
```

---

# 49. Bài tập 5 — Sibling

Cây:

```text
Python
├── Basic
├── Advanced
└── Asyncio
```

Từ:

```text
Basic
```

tìm:

```text
Advanced
```

và:

```text
Asyncio
```

bằng `sibling()` hoặc thông qua:

```python
model.index(...)
```

---

# 50. Bài tập 6 — Debug Tree

Trong `data()`:

```python
print(
    "row:",
    index.row(),
    "column:",
    index.column(),
    "node:",
    index.internalPointer().name,
)
```

Quan sát Qt gọi `data()` như thế nào khi:

```text
expand
collapse
click
select
scroll
```

Đây là một bài tập rất tốt để hiểu Model/View **không hoạt động theo kiểu "render toàn bộ UI một lần"**.

---

# 51. Bài tập Deep Dive

Bạn nên tự trả lời được:

### Câu 1

`QModelIndex` có phải Domain Object không?

### Câu 2

`index.row()` biểu diễn gì?

### Câu 3

`index.column()` biểu diễn gì?

### Câu 4

Khi nào `index.isValid()` là `False`?

### Câu 5

`internalPointer()` dùng để làm gì?

### Câu 6

`createIndex()` liên quan gì tới `internalPointer()`?

### Câu 7

Tại sao Tree Model cần `index()` và `parent()`?

### Câu 8

`QModelIndex()` rỗng có ý nghĩa gì?

### Câu 9

`QModelIndex` có nên được lưu vào Domain Model không?

### Câu 10

Database ID:

```text
500
```

và:

```python
index.row() == 0
```

có mâu thuẫn không?

**Không.**

---

# 52. Mental Model cuối buổi

Nếu chỉ nhớ một sơ đồ, hãy nhớ cái này:

```text
                         QTreeView
                            │
                            │
                            ▼
                      QModelIndex
                 ┌──────────┼──────────┐
                 │          │          │
                 ▼          ▼          ▼
               row()    column()    data()
                                      │
                                      ▼
                              QAbstractItemModel
                                      │
                                      ▼
                              internalPointer()
                                      │
                                      ▼
                                  TreeNode
                                  /     \
                                 /       \
                            parent       children
```

Và hai hướng navigation:

```text
                 ┌──────────────┐
                 │              │
                 ▼              │
            QModelIndex         │
                 │              │
             parent()           │
                 │              │
                 ▼              │
            Parent Index        │
                                │
                 ▲              │
                 │              │
              index()           │
                 │              │
                 └──────────────┘
```

Cuối cùng, hãy nhớ **3 tầng không được trộn lẫn**:

```text
Domain Object
    ↓
Todo / Story / Chapter / File

QModelIndex
    ↓
Địa chỉ item trong Qt Model

QWidget
    ↓
Cách item được hiển thị
```

Đây là nền tảng để sang **Buổi 19 — Roles**, nơi chúng ta sẽ học cách một `QModelIndex` có thể cung cấp **nhiều loại dữ liệu khác nhau** thông qua `DisplayRole`, `EditRole`, `DecorationRole`, `UserRole` — và từ đó bắt đầu xây Model theo kiểu chuyên nghiệp thay vì chỉ trả về text.
