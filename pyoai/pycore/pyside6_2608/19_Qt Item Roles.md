# Buổi 19 — Qt Item Roles

Hôm nay chúng ta học một phần **cực kỳ quan trọng của Qt Model/View**:

```python
Qt.ItemDataRole
```

Đặc biệt:

```text
DisplayRole
EditRole
DecorationRole
UserRole
```

Nếu `QModelIndex` ở Buổi 18 trả lời câu hỏi:

> **"Item nào?"**

thì `Role` trả lời:

> **"Tôi muốn loại dữ liệu nào của item này?"**

---

# 1. Tại sao cần Role?

Giả sử có một Todo:

```python
todo = Todo(
    id=100,
    title="Learn PySide6",
    completed=True,
)
```

Một item có rất nhiều thông tin:

```text
Todo
├── id
├── title
├── completed
├── created_at
└── priority
```

Nhưng `QTableView` có thể cần:

```text
Title
```

Checkbox cần:

```text
completed
```

Logic ứng dụng cần:

```text
id
```

Icon cần:

```text
priority
```

Nếu `data()` chỉ có:

```python
return todo.title
```

thì Model không thể phục vụ nhiều nhu cầu khác nhau.

Qt giải quyết bằng **Role**.

---

# 2. `data(index, role)`

Đây là API trung tâm:

```python
def data(self, index, role):
    ...
```

Ví dụ:

```python
def data(self, index, role):

    if role == Qt.ItemDataRole.DisplayRole:
        return "Learn PySide6"

    if role == Qt.ItemDataRole.UserRole:
        return 100
```

Cùng một `QModelIndex`:

```text
                 QModelIndex
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
     DisplayRole  UserRole   DecorationRole
          ↓           ↓           ↓
        Text        ID          Icon
```

---

# 3. Role là gì?

Role thực chất là một enum:

```python
Qt.ItemDataRole
```

Ví dụ:

```python
Qt.ItemDataRole.DisplayRole
```

hoặc:

```python
Qt.ItemDataRole.UserRole
```

Khi View gọi:

```python
model.data(
    index,
    Qt.ItemDataRole.DisplayRole,
)
```

Model trả về dữ liệu phù hợp với Role đó.

---

# 4. `DisplayRole`

Đây là Role quan trọng nhất.

```python
Qt.ItemDataRole.DisplayRole
```

Nó đại diện cho:

> **Dữ liệu chính được hiển thị cho người dùng.**

Ví dụ:

```python
if role == Qt.ItemDataRole.DisplayRole:
    return todo.title
```

View sẽ hiển thị:

```text
Learn PySide6
```

---

# 5. Ví dụ `QListView`

Data:

```python
todos = [
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
]
```

Model:

```python
def data(self, index, role):

    if role == Qt.ItemDataRole.DisplayRole:
        return self.todos[index.row()]

    return None
```

View:

```text
Learn Python
Learn PySide6
Learn SQLite
```

---

# 6. `DisplayRole` không có nghĩa là "mọi dữ liệu"

Đây là lỗi tư duy phổ biến:

```python
def data(self, index, role):
    return todo
```

Không nên.

`DisplayRole` thường trả:

```text
str
number
giá trị hiển thị
```

Ví dụ:

```python
return todo.title
```

---

# 7. `EditRole`

Role thứ hai:

```python
Qt.ItemDataRole.EditRole
```

Dùng cho:

> **Dữ liệu được sử dụng khi chỉnh sửa item.**

Ví dụ:

```python
if role == Qt.ItemDataRole.DisplayRole:
    return todo.title

if role == Qt.ItemDataRole.EditRole:
    return todo.title
```

Thoạt nhìn có vẻ giống nhau.

Nhưng về mặt ý nghĩa:

```text
DisplayRole
    ↓
"Learn PySide6"

EditRole
    ↓
giá trị dùng cho editor
```

---

# 8. Ví dụ DisplayRole khác EditRole

Giả sử database lưu:

```text
2026-08-28 18:30:00
```

Nhưng View muốn hiển thị:

```text
28/08/2026 18:30
```

Ta có thể:

```python
if role == Qt.ItemDataRole.DisplayRole:
    return todo.created_at.strftime(
        "%d/%m/%Y %H:%M"
    )

if role == Qt.ItemDataRole.EditRole:
    return todo.created_at
```

Tức là:

```text
DisplayRole
    ↓
formatted value

EditRole
    ↓
raw/editable value
```

---

# 9. `DecorationRole`

Role:

```python
Qt.ItemDataRole.DecorationRole
```

thường được sử dụng cho:

* Icon
* Decoration
* Visual indicator

Ví dụ:

```text
📁 Python
📁 PySide6
📄 main.py
📄 model.py
```

Model có thể:

```python
if role == Qt.ItemDataRole.DecorationRole:
    return icon
```

---

# 10. Icon trong Model

Ví dụ:

```python
from PySide6.QtGui import QIcon
```

Model:

```python
if role == Qt.ItemDataRole.DecorationRole:

    if node.is_folder:
        return QIcon("folder.png")

    return QIcon("file.png")
```

QTreeView có thể hiển thị:

```text
📁 Python
📁 PySide6
📄 main.py
```

Đây chính là một phần quan trọng của File Explorer.

---

# 11. `UserRole`

Role cực kỳ quan trọng:

```python
Qt.ItemDataRole.UserRole
```

Dùng cho:

> **Dữ liệu riêng của ứng dụng.**

Ví dụ:

```text
DisplayRole
    ↓
"Learn PySide6"

UserRole
    ↓
100
```

Trong đó:

```text
100 = database ID
```

---

# 12. Tại sao UserRole quan trọng?

Giả sử:

```text
Todo
├── id = 100
└── title = "Learn PySide6"
```

View hiển thị:

```text
Learn PySide6
```

Khi user click item, bạn cần biết:

```text
Todo ID = 100
```

Không nên:

```python
search_database_by_title(
    "Learn PySide6"
)
```

Có thể dùng:

```python
todo_id = index.data(
    Qt.ItemDataRole.UserRole
)
```

→

```text
100
```

---

# 13. Pattern rất quan trọng

Đây là pattern bạn nên ghi nhớ:

```python
def data(self, index, role):

    todo = self.todos[index.row()]

    if role == Qt.ItemDataRole.DisplayRole:
        return todo.title

    if role == Qt.ItemDataRole.UserRole:
        return todo.id

    return None
```

Sau đó:

```python
title = index.data(
    Qt.ItemDataRole.DisplayRole
)

todo_id = index.data(
    Qt.ItemDataRole.UserRole
)
```

---

# 14. Một item có nhiều "gương mặt"

Hãy hình dung:

```text
Todo
│
├── DisplayRole
│      ↓
│   "Learn PySide6"
│
├── EditRole
│      ↓
│   "Learn PySide6"
│
├── DecorationRole
│      ↓
│   icon
│
└── UserRole
       ↓
      100
```

Vẫn là **một Todo**.

Chỉ khác:

> Qt đang hỏi dữ liệu theo mục đích nào.

---

# 15. Ví dụ hoàn chỉnh

Tạo Todo:

```python
from dataclasses import dataclass


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
    Todo(2, "Learn PySide6", True),
    Todo(3, "Learn SQLite", False),
]
```

Model:

```python
from PySide6.QtCore import (
    QAbstractListModel,
    Qt,
)


class TodoModel(QAbstractListModel):

    def __init__(self, todos):

        super().__init__()

        self.todos = todos

    def rowCount(self, parent=None):

        return len(self.todos)

    def data(self, index, role):

        if not index.isValid():
            return None

        todo = self.todos[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return todo.title

        if role == Qt.ItemDataRole.UserRole:
            return todo.id

        return None
```

---

# 16. Lấy UserRole từ View

Ví dụ user chọn:

```text
Learn PySide6
```

Ta có:

```python
index = view.currentIndex()
```

Sau đó:

```python
todo_id = index.data(
    Qt.ItemDataRole.UserRole
)
```

Kết quả:

```text
2
```

---

# 17. UserRole không chỉ chứa ID

Bạn có thể dùng:

```python
if role == Qt.ItemDataRole.UserRole:
    return todo
```

Tức là:

```text
UserRole
    ↓
Todo object
```

Nhưng có một lưu ý kiến trúc.

Nếu View/Delegate cần Domain Object để xử lý UI, cách này có thể tiện.

Tuy nhiên, trong app lớn, bạn nên cân nhắc rõ:

```text
UserRole → ID
```

hay:

```text
UserRole → Domain Object
```

---

# 18. Tôi thường khuyến nghị

Với ứng dụng CRUD:

```text
DisplayRole → text
UserRole    → entity ID
```

Ví dụ:

```python
if role == Qt.ItemDataRole.DisplayRole:
    return todo.title

if role == Qt.ItemDataRole.UserRole:
    return todo.id
```

Sau đó:

```text
UI
 ↓
ID
 ↓
Application Service
 ↓
Repository
 ↓
Database
```

Điều này giúp View không phải phụ thuộc quá sâu vào Domain Object.

---

# 19. `CheckStateRole`

Ngoài 4 Role hôm nay, có một Role rất đáng biết:

```python
Qt.ItemDataRole.CheckStateRole
```

Dùng cho checkbox.

Ví dụ Todo:

```text
☐ Learn Python
☑ Learn PySide6
☐ Learn SQLite
```

Model:

```python
if role == Qt.ItemDataRole.CheckStateRole:

    return (
        Qt.CheckState.Checked
        if todo.completed
        else Qt.CheckState.Unchecked
    )
```

---

# 20. `flags()` kết hợp với CheckStateRole

Chỉ trả:

```python
CheckStateRole
```

chưa đủ.

Model cần cho phép item checkable:

```python
def flags(self, index):

    if not index.isValid():
        return Qt.ItemFlag.NoItemFlags

    return (
        Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsSelectable
        | Qt.ItemFlag.ItemIsUserCheckable
    )
```

Sau đó View có thể hiển thị checkbox.

---

# 21. Role + flags

Đây là mối quan hệ quan trọng:

```text
Role
 ↓
"Dữ liệu nào?"

flags
 ↓
"Item được phép làm gì?"
```

Ví dụ:

```text
CheckStateRole
       +
ItemIsUserCheckable
       ↓
    Checkbox
```

---

# 22. Role và `setData()`

Nếu muốn chỉnh sửa:

```text
View
 ↓
setData(index, value, role)
 ↓
Model
 ↓
Domain
```

Ví dụ:

```python
def setData(self, index, value, role):

    if role == Qt.ItemDataRole.EditRole:

        todo = self.todos[index.row()]
        todo.title = value

        self.dataChanged.emit(
            index,
            index,
            [role],
        )

        return True

    return False
```

---

# 23. DisplayRole và EditRole trong edit

Flow:

```text
User double-click
       ↓
Editor
       ↓
EditRole
       ↓
setData()
       ↓
Domain data
       ↓
dataChanged
       ↓
DisplayRole
       ↓
View
```

Đây là pipeline rất quan trọng.

---

# 24. Role không chỉ dành cho View

Bạn sẽ thấy Role được sử dụng bởi:

```text
View
Delegate
Proxy Model
Selection
Sorting
Filtering
Application UI
```

Ví dụ Proxy Model có thể:

```python
index.data(
    Qt.ItemDataRole.UserRole
)
```

để lấy ID.

---

# 25. Custom Role

Đây là phần cực kỳ mạnh.

Bạn có:

```python
Qt.ItemDataRole.UserRole
```

nhưng có thể tạo thêm:

```python
TODO_ID_ROLE = Qt.ItemDataRole.UserRole + 1
TODO_STATUS_ROLE = Qt.ItemDataRole.UserRole + 2
TODO_PRIORITY_ROLE = Qt.ItemDataRole.UserRole + 3
```

Ví dụ:

```python
TODO_ID_ROLE = (
    Qt.ItemDataRole.UserRole + 1
)

TODO_STATUS_ROLE = (
    Qt.ItemDataRole.UserRole + 2
)
```

---

# 26. Model với Custom Roles

```python
def data(self, index, role):

    if not index.isValid():
        return None

    todo = self.todos[index.row()]

    if role == Qt.ItemDataRole.DisplayRole:
        return todo.title

    if role == TODO_ID_ROLE:
        return todo.id

    if role == TODO_STATUS_ROLE:
        return todo.completed

    return None
```

Bây giờ:

```text
DisplayRole
     ↓
Learn PySide6

TODO_ID_ROLE
     ↓
2

TODO_STATUS_ROLE
     ↓
True
```

---

# 27. Vì sao Custom Role rất hay?

Trong app lớn, một item có thể có:

```text
Text
ID
Status
Priority
Type
CreatedAt
Permission
```

Không cần nhồi tất cả vào:

```text
DisplayRole
```

Mà tách:

```text
Role
 ↓
specific information
```

Đây chính là cách Model/View trở nên mạnh.

---

# 28. RoleName

Khi dùng QML/Qt Quick, bạn còn gặp khái niệm:

```text
roleNames()
```

Ví dụ:

```python
{
    Qt.UserRole + 1: b"id",
    Qt.UserRole + 2: b"title",
}
```

Trong PySide6 Widgets, bạn chưa cần đi sâu ngay.

Nhưng nó rất quan trọng khi sau này học:

```text
Qt Quick
QML
```

---

# 29. Role và `QModelIndex`

Bây giờ kết nối Buổi 18 + 19:

Buổi 18:

```text
QModelIndex
    ↓
Item nào?
```

Buổi 19:

```text
role
    ↓
Muốn dữ liệu nào?
```

Kết hợp:

```python
index.data(role)
```

nghĩa là:

> Lấy dữ liệu của **item này**, theo **Role này**.

---

# 30. Một ví dụ cực kỳ trực quan

Data:

```text
Todo
┌────┬─────────────────┬──────────┐
│ ID │ Title           │ Complete │
├────┼─────────────────┼──────────┤
│ 10 │ Learn Python    │ False    │
│ 20 │ Learn PySide6   │ True     │
└────┴─────────────────┴──────────┘
```

Index:

```text
row = 1
column = 1
```

Role:

```text
DisplayRole
```

→

```text
Learn PySide6
```

Cùng index:

```text
UserRole
```

→

```text
20
```

Cùng index:

```text
CheckStateRole
```

→

```text
Checked
```

Một Index.

Nhiều Role.

---

# 31. `DecorationRole`

Ví dụ File Explorer:

```text
📁 Python
📁 PySide6
📄 main.py
```

Model:

```python
if role == Qt.ItemDataRole.DisplayRole:
    return node.name

if role == Qt.ItemDataRole.DecorationRole:
    return node.icon

if role == Qt.ItemDataRole.UserRole:
    return node.path
```

Một file:

```text
DisplayRole
    ↓
main.py

DecorationRole
    ↓
file icon

UserRole
    ↓
C:\project\main.py
```

Đây chính là kiến trúc chúng ta sẽ cần cho **File Explorer** ở Buổi 24.

---

# 32. Một Model chuyên nghiệp

Một Model tốt có thể trông như:

```python
def data(self, index, role):

    if not index.isValid():
        return None

    node = index.internalPointer()

    match role:

        case Qt.ItemDataRole.DisplayRole:
            return node.name

        case Qt.ItemDataRole.DecorationRole:
            return node.icon

        case Qt.ItemDataRole.UserRole:
            return node.id

        case Qt.ItemDataRole.CheckStateRole:
            return node.checked

    return None
```

Lưu ý: `match` trên enum hoạt động tốt trong Python hiện đại.

---

# 33. Không nên làm thế này

```python
def data(self, index, role):

    node = index.internalPointer()

    if role == Qt.ItemDataRole.DisplayRole:
        return {
            "name": node.name,
            "id": node.id,
            "status": node.status,
        }
```

Vì View chỉ cần:

```text
name
```

Còn metadata nên tách Role.

---

# 34. Role là một "protocol"

Hãy nhìn Model như một API:

```text
Model
 │
 ├── DisplayRole
 │      → text
 │
 ├── EditRole
 │      → editable value
 │
 ├── DecorationRole
 │      → icon
 │
 ├── CheckStateRole
 │      → checkbox
 │
 └── UserRole
        → application metadata
```

View không cần biết cấu trúc Domain Object.

Nó chỉ hỏi Model theo protocol.

---

# 35. Bài tập 1 — Todo Model

Tạo:

```python
@dataclass
class Todo:
    id: int
    title: str
    completed: bool
```

Implement:

```text
DisplayRole
UserRole
CheckStateRole
```

Hiển thị:

```text
☐ Learn Python
☑ Learn PySide6
☐ Learn SQLite
```

---

# 36. Bài tập 2 — Todo ID

Khi click Todo:

```python
index = view.currentIndex()
```

lấy:

```python
todo_id = index.data(
    Qt.ItemDataRole.UserRole
)
```

và in:

```text
Selected Todo ID: 2
```

---

# 37. Bài tập 3 — File Explorer

Tạo:

```python
class FileNode:
    name
    path
    is_folder
```

Model:

```text
DisplayRole
    ↓
name

DecorationRole
    ↓
folder/file icon

UserRole
    ↓
path
```

Tree:

```text
📁 Project
├── 📁 src
│   ├── 📄 main.py
│   └── 📄 model.py
└── 📄 README.md
```

---

# 38. Bài tập 4 — Custom Roles

Tạo:

```python
FILE_PATH_ROLE = Qt.ItemDataRole.UserRole + 1
FILE_TYPE_ROLE = Qt.ItemDataRole.UserRole + 2
```

Sau đó:

```python
index.data(FILE_PATH_ROLE)
```

→:

```text
C:\project\src\main.py
```

và:

```python
index.data(FILE_TYPE_ROLE)
```

→:

```text
python
```

---

# 39. Bài tập 5 — Display vs Edit

Cho dữ liệu:

```text
database:
"learn-pyside6"
```

Display:

```text
Learn PySide6
```

Edit:

```text
learn-pyside6
```

Implement:

```python
DisplayRole
EditRole
```

---

# 40. Bài tập 6 — Checkbox

Cho:

```python
completed = True
```

Model trả:

```python
Qt.CheckState.Checked
```

Nếu:

```python
completed = False
```

trả:

```python
Qt.CheckState.Unchecked
```

Sau đó thêm:

```python
ItemIsUserCheckable
```

---

# 41. Kiến trúc cần nhớ

Sau 3 buổi:

```text
Buổi 17
QAbstractItemModel
       ↓
quản lý cấu trúc

Buổi 18
QModelIndex
       ↓
xác định item

Buổi 19
Role
       ↓
xác định loại dữ liệu
```

Kết hợp:

```text
                   View
                    │
                    ▼
              QModelIndex
                    │
             ┌──────┴──────┐
             │             │
           index          role
             │             │
       "item nào?"    "data nào?"
             │             │
             └──────┬──────┘
                    ▼
                  Model
                    │
                    ▼
                 Domain
```

---

# 42. Mental Model quan trọng nhất

Khi bạn nhìn thấy:

```python
model.data(index, role)
```

hãy đọc nó thành câu tiếng Việt:

> **"Model ơi, hãy cho tôi dữ liệu của item được xác định bởi `index`, với mục đích được xác định bởi `role`."**

Ví dụ:

```python
model.data(
    index,
    Qt.ItemDataRole.DisplayRole,
)
```

=

> Cho tôi **text hiển thị** của item này.

Còn:

```python
model.data(
    index,
    Qt.ItemDataRole.UserRole,
)
```

=

> Cho tôi **metadata của ứng dụng** của item này.

---

# 43. Bảng tổng kết

| Role             | Mục đích            | Ví dụ                 |
| ---------------- | ------------------- | --------------------- |
| `DisplayRole`    | Nội dung hiển thị   | `"Learn Python"`      |
| `EditRole`       | Giá trị cho editing | `"learn-python"`      |
| `DecorationRole` | Icon/decoration     | `QIcon(...)`          |
| `CheckStateRole` | Checkbox            | `Checked`             |
| `UserRole`       | Metadata ứng dụng   | `todo.id`             |
| Custom Role      | Dữ liệu riêng       | `file.path`, `status` |

---

## 🎯 Bài tập chính của Buổi 19

Hãy xây một **Todo Model hoàn chỉnh**:

```text
Todo
├── id
├── title
├── completed
└── priority
```

Model phải hỗ trợ:

```text
DisplayRole
    ↓
title

EditRole
    ↓
title

CheckStateRole
    ↓
completed

UserRole
    ↓
id

UserRole + 1
    ↓
priority
```

và:

```text
QListView
     ↓
TodoModel
     ↓
Todo
```

Sau khi làm được bài này, bạn đã bắt đầu chuyển từ **"dùng Model/View"** sang **"thiết kế Model/View"**.

**Buổi 20 — Delegate** sẽ nối tiếp rất tự nhiên: chúng ta sẽ học cách biến dữ liệu từ Role thành **editor, checkbox, combobox, progress bar, custom widget...** trong `QTableView`/`QTreeView`.
