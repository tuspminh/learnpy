# Buổi 23 — Selection Model

Hôm nay chúng ta học một thành phần rất quan trọng của Qt Model/View:

```python
QItemSelectionModel
```

Nếu `QModelIndex` trả lời câu hỏi:

> **"Item này là item nào?"**

thì `QItemSelectionModel` trả lời:

> **"User đang chọn item nào?"**

Đây là nền tảng để xây UI chuyên nghiệp như:

```text
Master → Detail
```

Ví dụ:

```text
┌──────────────────────┬──────────────────────────┐
│ Todo list            │ Todo Detail              │
│                      │                          │
│ ▶ Learn Python       │ Title: Learn Python      │
│   Learn SQLite       │ Priority: 5              │
│   Learn PySide6      │ Status: Doing            │
│   Learn Redis        │                          │
└──────────────────────┴──────────────────────────┘
```

---

# 1. Model/View có ba khái niệm cần phân biệt

```text
Model
    ↓
Dữ liệu

View
    ↓
Hiển thị

Selection Model
    ↓
Trạng thái chọn
```

Kiến trúc:

```text
                 QTableView
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
       Model            QItemSelectionModel
          │                     │
          │                selected index
          ↓                     ↓
        Data                  User
```

---

# 2. `QItemSelectionModel`

Import:

```python
from PySide6.QtCore import QItemSelectionModel
```

Thông thường bạn **không cần tự tạo** ngay.

Khi:

```python
view.setModel(model)
```

View có Selection Model.

Lấy nó:

```python
selection_model = view.selectionModel()
```

---

# 3. Kiểm tra item hiện tại

```python
index = view.currentIndex()
```

Nếu user click:

```text
Learn PySide6
```

thì:

```python
index
```

là:

```text
QModelIndex
```

---

# 4. Current ≠ Selected

Đây là khái niệm cực kỳ quan trọng.

### Current

```text
item hiện tại
```

### Selected

```text
item đang được chọn
```

Trong nhiều UI chúng trùng nhau.

Nhưng không phải lúc nào cũng vậy.

Ví dụ multi-selection:

```text
┌──────────────┐
│ Python       │ ← selected
│ SQLite       │ ← current
│ PySide6      │ ← selected
│ Redis        │
└──────────────┘
```

Có thể:

```text
current = SQLite
selected = Python + SQLite + PySide6
```

---

# 5. `currentIndex()`

Lấy item hiện tại:

```python
index = view.currentIndex()
```

Hoặc:

```python
selection_model = view.selectionModel()

index = selection_model.currentIndex()
```

---

# 6. `selectedIndexes()`

Lấy tất cả index được chọn:

```python
indexes = (
    selection_model.selectedIndexes()
)
```

Ví dụ:

```text
Python
SQLite
PySide6
```

được chọn.

Kết quả:

```python
[
    QModelIndex(...),
    QModelIndex(...),
    QModelIndex(...),
]
```

---

# 7. `selectedRows()`

Nếu là `QTableView`, thường bạn không muốn tất cả cell.

Ví dụ:

```text
┌───────────┬──────────┬─────────┐
│ Title     │ Priority │ Status  │
├───────────┼──────────┼─────────┤
│ Python    │ 5        │ Doing   │
└───────────┴──────────┴─────────┘
```

Nếu cả row được chọn:

```python
rows = selection_model.selectedRows()
```

Bạn nhận:

```text
QModelIndex
```

cho từng row.

Thường đây là thứ bạn muốn trong Todo App.

---

# 8. Selection Mode

`QAbstractItemView` có:

```python
SelectionMode
```

Các mode quan trọng:

```text
NoSelection
SingleSelection
MultiSelection
ExtendedSelection
ContiguousSelection
```

---

# 9. Single Selection

```python
from PySide6.QtWidgets import (
    QAbstractItemView,
)

view.setSelectionMode(
    QAbstractItemView.SelectionMode.SingleSelection
)
```

User chỉ chọn được:

```text
1 item
```

Phù hợp:

```text
Master → Detail
```

---

# 10. Multi Selection

```python
view.setSelectionMode(
    QAbstractItemView.SelectionMode.MultiSelection
)
```

Cho phép:

```text
A
B
C
```

được chọn cùng lúc.

---

# 11. Extended Selection

Rất phổ biến:

```python
view.setSelectionMode(
    QAbstractItemView.SelectionMode.ExtendedSelection
)
```

User có thể:

```text
Click
Ctrl + Click
Shift + Click
```

để chọn nhiều item.

Đây thường là lựa chọn tốt cho:

```text
File Explorer
Todo Manager
Contact Manager
```

---

# 12. Selection Behavior

Ngoài Selection Mode còn có:

```python
view.setSelectionBehavior(...)
```

Ví dụ:

```python
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectRows
)
```

Thay vì chọn từng cell:

```text
┌──────┬──────┐
│  X   │      │
└──────┴──────┘
```

chọn cả row:

```text
┌──────────────────┐
│ X  Python  5 Done│
└──────────────────┘
```

---

# 13. Todo Table nên cấu hình

```python
view.setSelectionBehavior(
    QAbstractItemView.SelectionBehavior.SelectRows
)

view.setSelectionMode(
    QAbstractItemView.SelectionMode.SingleSelection
)
```

Kết quả:

```text
Click Todo
    ↓
toàn bộ row được chọn
```

---

# 14. Signal `currentChanged`

`QItemSelectionModel` có signal:

```python
currentChanged
```

Ví dụ:

```python
selection_model.currentChanged.connect(
    self.on_current_changed
)
```

Handler:

```python
def on_current_changed(
    self,
    current,
    previous,
):
    print(current)
```

---

# 15. Signal `selectionChanged`

Signal:

```python
selectionChanged
```

Có:

```python
selected
deselected
```

Ví dụ:

```python
selection_model.selectionChanged.connect(
    self.on_selection_changed
)
```

```python
def on_selection_changed(
    self,
    selected,
    deselected,
):
    print("Selection changed")
```

---

# 16. `currentChanged` vs `selectionChanged`

Đây là điểm phải nhớ.

### `currentChanged`

```text
Current item thay đổi
```

### `selectionChanged`

```text
Selected items thay đổi
```

Ví dụ:

```text
User click A
```

có thể:

```text
currentChanged
selectionChanged
```

Nhưng khi:

```text
current item thay đổi
```

trong một số tình huống selection không thay đổi tương ứng.

Do đó không nên mặc định hai signal này là một.

---

# 17. Signal `currentRowChanged`

Ngoài ra còn có:

```python
currentRowChanged
```

Ví dụ:

```python
selection_model.currentRowChanged.connect(
    self.on_current_row_changed
)
```

Handler:

```python
def on_current_row_changed(
    self,
    current,
    previous,
):
    print("Row:", current.row())
```

---

# 18. Signal `currentColumnChanged`

Tương tự:

```python
selection_model.currentColumnChanged.connect(
    self.on_current_column_changed
)
```

Nhưng với Todo Table:

```text
SelectRows
```

thì `currentRowChanged()` thường hữu ích hơn.

---

# 19. Lấy Todo ID

Đây là cách rất thực tế.

Giả sử Model có:

```python
TODO_ID_ROLE = (
    Qt.ItemDataRole.UserRole + 1
)
```

Khi user click:

```python
def on_current_changed(
    self,
    current,
    previous,
):

    todo_id = current.data(
        TODO_ID_ROLE
    )

    print(todo_id)
```

---

# 20. Nhưng chúng ta đang có Proxy

Đây mới là phần quan trọng.

Kiến trúc:

```text
QTableView
    ↓
TodoProxyModel
    ↓
TodoTableModel
```

`current`:

```text
Proxy QModelIndex
```

Nếu muốn Source:

```python
source_index = proxy.mapToSource(
    current
)
```

---

# 21. Flow hoàn chỉnh

```text
User click
    ↓
QTableView
    ↓
QItemSelectionModel
    ↓
Proxy QModelIndex
    ↓
mapToSource()
    ↓
Source QModelIndex
    ↓
TODO_ID_ROLE
    ↓
Todo ID
```

---

# 22. Ví dụ

```python
def on_current_changed(
    self,
    current,
    previous,
):

    if not current.isValid():
        return

    source_index = (
        self.proxy.mapToSource(current)
    )

    todo_id = source_index.data(
        TODO_ID_ROLE
    )

    print("Todo:", todo_id)
```

Đây là pattern bạn sẽ sử dụng rất nhiều.

---

# 23. Tại sao cần `isValid()`?

Khi:

```text
không có item nào
```

`QModelIndex` có thể invalid.

Do đó luôn nên kiểm tra:

```python
if not current.isValid():
    return
```

Tránh:

```python
current.data(...)
```

trên index không hợp lệ.

---

# 24. Master → Detail

Đây là ứng dụng cực kỳ quan trọng.

UI:

```text
┌──────────────────┬─────────────────────────┐
│ Todo List        │ Detail                  │
├──────────────────┼─────────────────────────┤
│ Learn Python  ←  │ ID: 1                   │
│ Learn SQLite     │ Title: Learn Python     │
│ Learn PySide6    │ Priority: 5             │
│ Learn Redis      │ Status: Doing           │
└──────────────────┴─────────────────────────┘
```

Khi selection thay đổi:

```text
Selection
    ↓
Todo ID
    ↓
Load Todo
    ↓
Detail Panel
```

---

# 25. Không nên truyền cả Todo qua UI

Không nên:

```python
self.detail.show_todo(todo)
```

ở mọi nơi một cách tùy tiện.

Tốt hơn:

```text
Selection
    ↓
todo_id
    ↓
Application / State
    ↓
Detail
```

Điều này giúp architecture sạch hơn.

---

# 26. Một Controller nhỏ

Ví dụ:

```python
def on_todo_selected(
    self,
    current,
    previous,
):

    if not current.isValid():
        self.detail.clear()
        return

    source_index = (
        self.proxy.mapToSource(current)
    )

    todo_id = source_index.data(
        TODO_ID_ROLE
    )

    self.show_todo_detail(todo_id)
```

---

# 27. `selectionModel()` có thể thay đổi

Đây là một điểm nâng cao.

Khi:

```python
view.setModel(new_model)
```

Selection Model có thể thay đổi.

Do đó nếu Model thay đổi:

```python
selection_model = view.selectionModel()
```

nên được lấy lại.

Đừng giả định một Selection Model luôn tồn tại suốt vòng đời View.

---

# 28. Tạo Selection Model thủ công

Bạn cũng có thể:

```python
selection_model = QItemSelectionModel(
    model
)
```

Sau đó:

```python
view.setSelectionModel(
    selection_model
)
```

Điều này hữu ích khi:

```text
nhiều View
```

cần chia sẻ cùng selection state.

---

# 29. Một Selection Model cho nhiều View

Ví dụ:

```text
              TodoModel
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
   QTableView           QListView
        │                   │
        └─────────┬─────────┘
                  ↓
       QItemSelectionModel
```

Hai View có thể cùng phản ánh:

```text
selected Todo
```

---

# 30. Khi nào dùng shared Selection Model?

Ví dụ:

```text
TreeView
   +
TableView
```

Trong ứng dụng File Explorer:

```text
Folder Tree
    ↓
File Table
```

hoặc:

```text
Contact List
    ↓
Contact Detail
```

Selection state có thể được chia sẻ.

---

# 31. `select()`

Bạn cũng có thể chọn item bằng code.

```python
selection_model.select(
    index,
    QItemSelectionModel.SelectionFlag.Select
)
```

Ví dụ:

```python
from PySide6.QtCore import (
    QItemSelectionModel,
)
```

---

# 32. Các Selection Flags

Quan trọng:

```text
Select
Deselect
Toggle
Clear
ClearAndSelect
Rows
Columns
Current
```

Ví dụ:

```python
selection_model.select(
    index,
    QItemSelectionModel.SelectionFlag.Select
)
```

---

# 33. Chọn và đặt Current

Nếu muốn:

```text
select
+
current
```

thường dùng:

```python
flags = (
    QItemSelectionModel.SelectionFlag.Select
    | QItemSelectionModel.SelectionFlag.Current
)
```

Sau đó:

```python
selection_model.select(
    index,
    flags,
)
```

---

# 34. `ClearAndSelect`

Nếu muốn bỏ selection cũ và chọn item mới:

```python
flags = (
    QItemSelectionModel.SelectionFlag.ClearAndSelect
    | QItemSelectionModel.SelectionFlag.Current
)

selection_model.select(
    index,
    flags,
)
```

Rất hữu ích khi bạn muốn programmatically select một Todo.

---

# 35. `setCurrentIndex()`

Đặt current:

```python
selection_model.setCurrentIndex(
    index,
    QItemSelectionModel.SelectionFlag.Current
)
```

Nhưng:

```text
setCurrentIndex()
```

và:

```text
select()
```

không hoàn toàn giống nhau.

Một cái thay đổi:

```text
current
```

một cái thay đổi:

```text
selection
```

Có thể kết hợp flags để đạt hành vi mong muốn.

---

# 36. Clear Selection

```python
selection_model.clearSelection()
```

Xóa selected items.

Hoặc:

```python
selection_model.clear()
```

`clear()` có thể reset nhiều trạng thái hơn selection đơn thuần, nên hãy dùng đúng mục đích.

---

# 37. Chọn toàn bộ

View có:

```python
view.selectAll()
```

hoặc thao tác qua Selection Model.

Ví dụ:

```text
Ctrl + A
```

thường View xử lý.

---

# 38. Multi-selection

Ví dụ:

```python
view.setSelectionMode(
    QAbstractItemView.SelectionMode.ExtendedSelection
)
```

User chọn:

```text
Python
SQLite
Redis
```

Lấy:

```python
indexes = (
    view.selectionModel()
        .selectedRows()
)
```

---

# 39. Xóa nhiều Todo

Với Proxy:

```python
indexes = (
    selection_model.selectedRows()
)
```

Mỗi index là:

```text
Proxy Index
```

Không được trực tiếp dùng row của Proxy để xóa Source.

Phải:

```python
source_indexes = [
    proxy.mapToSource(index)
    for index in indexes
]
```

Sau đó lấy:

```python
todo_id
```

từ mỗi Source Index.

---

# 40. Nhưng xóa nhiều item có một vấn đề

Giả sử:

```text
Source:

row 0 → A
row 1 → B
row 2 → C
row 3 → D
```

Xóa:

```text
B
C
```

Nếu bạn xóa từ nhỏ → lớn:

```text
remove row 1
```

thì:

```text
A
C
D
```

`C` đã trở thành row 1.

Sau đó:

```python
remove row 2
```

sẽ xóa:

```text
D
```

chứ không phải C.

---

# 41. Xóa từ cuối lên

Do đó:

```python
source_indexes.sort(
    key=lambda index: index.row(),
    reverse=True,
)
```

Sau đó:

```python
for index in source_indexes:
    model.removeRow(index.row())
```

Ví dụ:

```text
3
1
```

xóa row 3 trước:

```text
A B C
```

sau đó xóa row 1:

```text
A C
```

Đây là kỹ thuật rất quan trọng.

---

# 42. Nhưng kiến trúc tốt hơn

Trong app chuyên nghiệp:

```text
View
 ↓
Selected IDs
 ↓
DeleteTodosUseCase
 ↓
Repository
```

Ví dụ:

```python
todo_ids = [
    index.data(TODO_ID_ROLE)
    for index in indexes
]
```

Sau đó:

```python
self.delete_todos(todo_ids)
```

Model được cập nhật sau khi Application xử lý.

Điều này tốt hơn việc UI tự quản lý business operation.

---

# 43. Selection + Proxy + Domain

Kiến trúc hoàn chỉnh:

```text
                  QTableView
                      │
                      ▼
             QItemSelectionModel
                      │
                      ▼
                Proxy Index
                      │
                 mapToSource()
                      │
                      ▼
                Todo ID
                      │
                      ▼
              Application Layer
                      │
                      ▼
                   Domain
```

Đây là kiến trúc rất đẹp.

---

# 44. Selection không phải Domain State

Đây là nguyên tắc quan trọng:

```text
Selected Todo
```

là:

```text
UI state
```

không phải:

```text
Todo domain state
```

Ví dụ:

```text
Todo.status = Doing
```

là Domain State.

Nhưng:

```text
Todo đang được chọn
```

là Presentation State.

Đừng đưa:

```python
todo.is_selected
```

vào Domain chỉ để phục vụ UI.

---

# 45. Selection Model và Delegate

Hai thứ này phối hợp:

```text
View
 ├── Selection Model
 │       ↓
 │   selected item
 │
 └── Delegate
         ↓
      paint selected
```

Delegate quyết định:

```text
selected item
```

được vẽ như thế nào.

Selection Model quyết định:

```text
selected item nào
```

---

# 46. Selection + StatusBar

Ví dụ khi chọn:

```text
Learn PySide6
```

Status bar:

```text
1 Todo selected
```

Code:

```python
def on_selection_changed(
    self,
    selected,
    deselected,
):

    count = len(
        self.view
        .selectionModel()
        .selectedRows()
    )

    self.statusBar().showMessage(
        f"{count} Todo selected"
    )
```

---

# 47. Selection + Detail Panel

Đây là bài tập quan trọng nhất hôm nay.

```text
┌──────────────────┬─────────────────────┐
│ Todo              │ Detail              │
├──────────────────┼─────────────────────┤
│ Python            │ ID: 1              │
│ SQLite       ←    │ Title: SQLite      │
│ PySide6           │ Priority: 4        │
│ Redis             │ Status: Doing      │
└──────────────────┴─────────────────────┘
```

Khi click:

```text
SQLite
```

thì:

```text
currentChanged
      ↓
proxy_index
      ↓
mapToSource()
      ↓
todo_id
      ↓
load detail
```

---

# 48. Code Master → Detail

```python
def on_current_changed(
    self,
    current,
    previous,
):

    if not current.isValid():
        self.clear_detail()
        return

    source_index = (
        self.proxy.mapToSource(current)
    )

    todo_id = source_index.data(
        TODO_ID_ROLE
    )

    self.show_detail(todo_id)
```

Đây là pattern bạn nên ghi nhớ.

---

# 49. Một lỗi rất phổ biến

Sai:

```python
def on_current_changed(
    self,
    current,
    previous,
):

    todo = self.todos[current.row()]
```

Tại sao sai?

Vì:

```text
current.row()
```

có thể là:

```text
Proxy row
```

Trong khi:

```text
self.todos
```

là:

```text
Source data
```

Sau filtering/sorting:

```text
Proxy row != Source row
```

---

# 50. Cách đúng

```python
source_index = (
    proxy.mapToSource(current)
)
```

hoặc lấy trực tiếp:

```python
todo_id = current.data(
    TODO_ID_ROLE
)
```

và dùng ID.

---

# 51. Khi Filter thay đổi

Đây là một tình huống thực tế.

Ban đầu:

```text
Python   ← selected
SQLite
PySide6
```

User search:

```text
PySide6
```

`Python` biến mất khỏi Proxy.

Selection hiện tại có thể trở thành:

```text
invalid
```

Detail panel phải xử lý:

```python
if not current.isValid():
    self.clear_detail()
```

Đây là lý do `isValid()` rất quan trọng.

---

# 52. Khi Model Reset

Nếu Source Model:

```python
beginResetModel()
...
endResetModel()
```

selection có thể bị thay đổi/reset.

UI không nên giả định:

```text
selected Todo vẫn tồn tại
```

Sau reset nên kiểm tra lại:

```text
currentIndex
selection
```

---

# 53. Selection Model với `QListView`

Không chỉ `QTableView`.

Ví dụ:

```python
list_view.selectionModel()
```

vẫn hoạt động.

Flow:

```text
QListView
    ↓
QItemSelectionModel
    ↓
QModelIndex
```

---

# 54. Selection Model với `QTreeView`

Cũng tương tự:

```text
QTreeView
    ↓
QItemSelectionModel
    ↓
QModelIndex
```

Nhưng Tree có:

```text
parent
child
```

nên:

```python
index.parent()
```

sẽ quan trọng hơn.

---

# 55. File Explorer

Buổi 24 chúng ta sẽ xây:

```text
┌────────────────────────────────────────────┐
│ File Explorer                              │
├────────────────┬───────────────────────────┤
│ Folders        │ Files                     │
│                │                           │
│ 📁 Documents   │ file1.txt                │
│ 📁 Pictures    │ report.pdf                │
│ 📁 Projects    │ image.png                 │
│                │                           │
└────────────────┴───────────────────────────┘
```

Selection Model sẽ kết nối:

```text
Folder selection
       ↓
File Model
       ↓
File View
```

Đây là ứng dụng thực tế rất tốt của kiến thức hôm nay.

---

# 56. Một pattern rất quan trọng

Bạn sẽ gặp pattern này liên tục:

```python
selection_model = view.selectionModel()

selection_model.currentChanged.connect(
    self.on_current_changed
)
```

Handler:

```python
def on_current_changed(
    self,
    current,
    previous,
):

    if not current.isValid():
        return

    ...
```

Nếu có Proxy:

```python
source_index = (
    proxy.mapToSource(current)
)
```

Nếu có ID:

```python
entity_id = source_index.data(
    ID_ROLE
)
```

Cuối cùng:

```text
entity_id
```

được truyền vào Application layer.

---

# 57. Bài tập 1 — Single Selection

Tạo:

```text
QTableView
```

cấu hình:

```python
SelectRows
SingleSelection
```

Khi click một Todo:

```text
console:

Selected Todo ID: 10
```

---

# 58. Bài tập 2 — Current Changed

Kết nối:

```python
selection_model.currentChanged.connect(...)
```

In:

```text
Current row
Previous row
Todo ID
```

Ví dụ:

```text
Current: 4
Previous: 2
Todo ID: 15
```

---

# 59. Bài tập 3 — Multi Selection

Đổi:

```python
ExtendedSelection
```

Cho phép chọn:

```text
Todo A
Todo C
Todo D
```

Sau đó in:

```text
Selected IDs:
[1, 3, 4]
```

---

# 60. Bài tập 4 — Delete Multiple

Tạo:

```text
[ Delete Selected ]
```

Khi click:

```text
selected indexes
       ↓
Proxy → Source
       ↓
Todo IDs
       ↓
Delete
```

Nhớ:

> Không dùng Proxy row như Source row.

---

# 61. Bài tập 5 — Master → Detail ⭐

Đây là bài tập quan trọng nhất.

Tạo:

```text
QSplitter
```

Bên trái:

```text
QTableView
```

Bên phải:

```text
QFormLayout
```

Hiển thị:

```text
ID
Title
Priority
Status
Description
```

Khi selection thay đổi:

```text
Todo List
    ↓
Selection Model
    ↓
Todo ID
    ↓
Detail Panel
```

---

# 62. Bài tập 6 — Kết hợp toàn bộ

Sử dụng:

```text
QTableView
TodoTableModel
TodoProxyModel
QItemSelectionModel
```

và:

```text
Search
Status Filter
Priority Filter
Sorting
Selection
Detail
```

Kiến trúc:

```text
                      UI
                       │
              ┌────────┴────────┐
              │                 │
          Filter UI          Detail UI
              │                 ▲
              ▼                 │
       TodoProxyModel            │
              │                 │
              ▼                 │
         QTableView              │
              │                 │
              ▼                 │
    QItemSelectionModel ─────────┘
              │
              ▼
           Todo ID
```

---

# 63. Những thứ cần nhớ hôm nay

### `QModelIndex`

```text
Item ở đâu?
```

### `QItemSelectionModel`

```text
User chọn item nào?
```

### `currentIndex()`

```text
Item hiện tại
```

### `selectedIndexes()`

```text
Tất cả selected indexes
```

### `selectedRows()`

```text
Các row được chọn
```

### `currentChanged`

```text
Current thay đổi
```

### `selectionChanged`

```text
Selection thay đổi
```

### `mapToSource()`

```text
Proxy Index
    ↓
Source Index
```

### `mapFromSource()`

```text
Source Index
    ↓
Proxy Index
```

---

# 64. Mental Model cuối buổi

Hãy nhớ chuỗi này:

```text
                 QTableView
                     │
                     ▼
          QItemSelectionModel
                     │
                     ▼
                Proxy Index
                     │
                mapToSource()
                     │
                     ▼
               Source Index
                     │
                 UserRole
                     │
                     ▼
                 Entity ID
                     │
                     ▼
             Application Layer
```

Đây là cách **Model/View + Proxy + Selection** kết hợp với nhau trong một ứng dụng PySide6 được thiết kế tốt.

---

## 🎯 Thử thách trước Buổi 24

Hãy hoàn thành một màn hình:

```text
┌──────────────────────────────────────────────────┐
│ Search: [____________] Status: [All ▼]           │
├───────────────────────┬──────────────────────────┤
│ Todo                  │ Detail                   │
├───────────────────────┼──────────────────────────┤
│ Learn Python          │ ID: 1                    │
│ Learn SQLite     ←    │ Title: Learn SQLite      │
│ Learn PySide6         │ Priority: 4              │
│ Learn Redis           │ Status: Doing            │
└───────────────────────┴──────────────────────────┘
```

Các thành phần:

```text
TodoTableModel
      ↓
TodoProxyModel
      ↓
QTableView
      ↓
QItemSelectionModel
      ↓
Todo ID
      ↓
Detail Panel
```

Nếu làm được bài này, bạn đã nối được **Buổi 15 → 19 → 21 → 22 → 23** thành một hệ thống Model/View hoàn chỉnh.

**Buổi 24 — Mini Project: File Explorer** sẽ tổng hợp toàn bộ phần II: `QTreeView` + `QTableView` + `QFileSystemModel` + Proxy Model + Selection Model + Context Menu + mở file/thư mục.
