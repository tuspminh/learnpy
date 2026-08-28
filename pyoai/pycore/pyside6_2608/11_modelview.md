# Buổi 11 — Qt Model/View Architecture

Đây là **một trong những buổi quan trọng nhất của PySide6**.

Từ buổi này, chúng ta chuyển từ tư duy:

```text
Widget chứa dữ liệu
```

sang:

```text
Data
  ↓
Model
  ↓
View
  ↓
User
```

Nếu bạn muốn xây các app như:

* File Explorer
* Todo Manager
* Database Browser
* Table Editor
* IDE
* Note App
* Story Manager
* Download Manager

thì **Model/View là kiến thức bắt buộc**.

---

# 1. Vấn đề của cách làm cũ

Ở Todo App v1 chúng ta dùng:

```python
QListWidget
```

và:

```python
self.todo_list.addItem(...)
```

Ví dụ:

```python
self.todo_list.clear()

for todo in todos:
    self.todo_list.addItem(todo.title)
```

Cách này rất đơn giản.

Nhưng hãy tưởng tượng có:

```text
100,000 Todo
```

hoặc dữ liệu đến từ:

```text
SQLite
PostgreSQL
REST API
Crawler
Filesystem
```

Ta không muốn UI trực tiếp quản lý dữ liệu.

---

# 2. Kiến trúc cũ

Todo App v1:

```text
┌─────────────────────┐
│     MainWindow      │
│                     │
│  QListWidget        │
│      │              │
│      └── Todo data  │
└─────────────────────┘
```

`QListWidget` vừa:

```text
lưu data
+
quản lý item
+
hiển thị
```

Đây là **convenience API**.

---

# 3. Kiến trúc Model/View

Qt tách thành:

```text
┌───────────────┐
│     Model     │
│               │
│     Data      │
└───────┬───────┘
        │
        │
        ▼
┌───────────────┐
│      View     │
│               │
│    Display    │
└───────────────┘
```

Ví dụ Todo:

```text
TodoRepository
       │
       ▼
TodoModel
       │
       ▼
QListView
```

---

# 4. Model là gì?

**Model chịu trách nhiệm cung cấp dữ liệu cho View.**

Ví dụ:

```text
TodoModel
│
├── Todo 1
├── Todo 2
├── Todo 3
└── Todo 4
```

Model biết:

```text
Có bao nhiêu item?
Item thứ i là gì?
Giá trị của item là gì?
Item có thể edit không?
Item có trạng thái gì?
```

Nhưng Model **không chịu trách nhiệm vẽ UI**.

---

# 5. View là gì?

View chịu trách nhiệm:

> Hiển thị dữ liệu cho user.

Ví dụ:

```python
QListView
QTableView
QTreeView
```

View không cần biết dữ liệu lấy từ:

```text
SQLite
JSON
API
Memory
Filesystem
```

Nó chỉ cần biết:

> Model cung cấp dữ liệu như thế nào?

---

# 6. Ví dụ thực tế

Giả sử có:

```text
TodoModel

1. Learn Python
2. Learn PySide6
3. Learn SQLite
```

Có thể hiển thị bằng:

```text
QListView
```

hoặc dữ liệu tương tự có thể được hiển thị bằng:

```text
QTableView
```

View khác nhau:

```text
                Model
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
   QListView  QTableView  QTreeView
```

**Data không nhất thiết phải thay đổi.**

---

# 7. Model/View giống MVC nhưng không hoàn toàn

Nếu bạn từng học MVC:

```text
MVC

Model
View
Controller
```

Qt Model/View gần giống:

```text
Model
View
Delegate
```

Qt tập trung mạnh vào quan hệ:

```text
Model ↔ View
```

và có:

```text
Delegate
```

để xử lý việc render/edit item.

---

# 8. Kiến trúc tổng quát

Hãy ghi nhớ:

```text
                  Application Data
                         │
                         ▼
                      Model
                         │
                 ┌───────┴───────┐
                 │               │
                 ▼               ▼
              View            Delegate
                 │               │
                 └───────┬───────┘
                         ▼
                       User
```

Trong các buổi sau chúng ta sẽ lần lượt bóc từng phần.

---

# 9. Model không nhất thiết chứa toàn bộ Data

Đây là điểm rất quan trọng.

Model có thể là **adapter** giữa data source và Qt.

Ví dụ:

```text
SQLite
  ↓
Repository
  ↓
TodoModel
  ↓
QListView
```

hoặc:

```text
REST API
  ↓
Repository
  ↓
TodoModel
  ↓
QListView
```

hoặc:

```text
Filesystem
  ↓
FileModel
  ↓
QTreeView
```

---

# 10. Một ví dụ cực kỳ đơn giản

Hôm nay chưa cần `QAbstractListModel`.

Qt có model có sẵn:

```python
QStringListModel
```

Import:

```python
from PySide6.QtCore import QStringListModel
```

Dữ liệu:

```python
items = [
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
]
```

Tạo Model:

```python
model = QStringListModel(items)
```

Tạo View:

```python
view = QListView()
```

Kết nối:

```python
view.setModel(model)
```

Thế là xong.

---

# 11. Chương trình đầu tiên

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QListView,
)


app = QApplication(sys.argv)

items = [
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
]

model = QStringListModel(items)

view = QListView()

view.setModel(model)

view.resize(400, 300)
view.show()

sys.exit(app.exec())
```

Kiến trúc:

```text
items
  ↓
QStringListModel
  ↓
QListView
```

---

# 12. `setModel()` cực kỳ quan trọng

Dòng:

```python
view.setModel(model)
```

có ý nghĩa:

> View này lấy dữ liệu từ Model này.

Sau đó View hỏi Model:

```text
Có bao nhiêu item?
        ↓
Model

Item thứ 0 là gì?
        ↓
Model

Item thứ 1 là gì?
        ↓
Model
```

View không cần tự giữ danh sách.

---

# 13. Model và View tách biệt

Ví dụ:

```python
model = QStringListModel([
    "Python",
    "PySide6",
    "SQLite",
])
```

Sau đó:

```python
view1 = QListView()
view2 = QListView()

view1.setModel(model)
view2.setModel(model)
```

Một Model:

```text
                 Model
              /         \
             ↓           ↓
         QListView    QListView
```

Hai View cùng hiển thị một nguồn dữ liệu.

---

# 14. Demo

```python
import sys

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QHBoxLayout,
    QWidget,
)


app = QApplication(sys.argv)

model = QStringListModel([
    "Python",
    "PySide6",
    "SQLite",
    "Redis",
])

view1 = QListView()
view2 = QListView()

view1.setModel(model)
view2.setModel(model)

window = QWidget()

layout = QHBoxLayout(window)

layout.addWidget(view1)
layout.addWidget(view2)

window.resize(700, 300)
window.show()

sys.exit(app.exec())
```

Bạn sẽ thấy:

```text
┌───────────────┐    ┌───────────────┐
│ Python        │    │ Python        │
│ PySide6       │    │ PySide6       │
│ SQLite        │    │ SQLite        │
│ Redis         │    │ Redis         │
└───────────────┘    └───────────────┘
        ↑                    ↑
        └────────┬───────────┘
                 │
               Model
```

---

# 15. Đây là lợi ích rất lớn

Nếu Model thay đổi:

```text
Model
 ↓
data changed
```

các View liên quan có thể cập nhật.

Ta không cần:

```python
view1.clear()
view1.addItem(...)
view2.clear()
view2.addItem(...)
```

Đây chính là một trong những mục tiêu của Model/View.

---

# 16. Model có thể thay đổi

Ví dụ:

```python
model.setStringList([
    "Python",
    "PySide6",
    "PostgreSQL",
    "Redis",
    "Docker",
])
```

Model đã thay đổi.

Các View sử dụng model sẽ phản ánh dữ liệu mới.

---

# 17. View không sở hữu business data

Đây là nguyên tắc quan trọng:

❌ Không nên:

```text
QListView
   ↓
Todo objects
```

theo nghĩa View tự quản lý domain data.

Tốt hơn:

```text
Todo
 ↓
Repository
 ↓
Model
 ↓
View
```

---

# 18. Với Todo App của chúng ta

Kiến trúc v1:

```text
TodoRepository
       ↓
MainWindow
       ↓
QListWidget
```

Model/View:

```text
TodoRepository
       ↓
TodoListModel
       ↓
QListView
       ↓
MainWindow
```

Tốt hơn nữa:

```text
                MainWindow
                    │
             ┌──────┴──────┐
             │             │
        TodoListModel   TodoDialog
             │
             ↓
          QListView
```

---

# 19. `QListView`

`QListView` là View chuyên hiển thị dữ liệu dạng danh sách.

```text
Python
PySide6
SQLite
Redis
Docker
```

Nó **không phải nơi lưu danh sách chính**.

Nó lấy danh sách từ Model.

```python
view.setModel(model)
```

---

# 20. `QTableView`

Dữ liệu dạng bảng:

```text
┌────┬────────────────┬───────────┐
│ ID │ Title          │ Completed │
├────┼────────────────┼───────────┤
│ 1  │ Learn Python   │ Yes       │
│ 2  │ Learn Qt       │ No        │
│ 3  │ Learn SQLite   │ No        │
└────┴────────────────┴───────────┘
```

sẽ dùng:

```python
QTableView
```

với:

```text
QAbstractTableModel
```

---

# 21. `QTreeView`

Dữ liệu dạng cây:

```text
Project
├── src
│   ├── main.py
│   └── models.py
│
├── tests
│   └── test_main.py
│
└── README.md
```

dùng:

```python
QTreeView
```

Model tương ứng có thể là:

```text
QFileSystemModel
QAbstractItemModel
```

---

# 22. Ba loại View quan trọng

| View         | Dữ liệu |
| ------------ | ------- |
| `QListView`  | List    |
| `QTableView` | Table   |
| `QTreeView`  | Tree    |

Mental model:

```text
List
 ↓
QListView

Table
 ↓
QTableView

Tree
 ↓
QTreeView
```

---

# 23. Một Model có thể có nhiều View

Ví dụ database:

```text
TodoModel
     │
     ├── QTableView
     │
     └── QListView
```

Một View cho:

```text
danh sách
```

View kia cho:

```text
bảng chi tiết
```

Model vẫn là nguồn dữ liệu chung.

---

# 24. Model không chỉ là container

Đừng nghĩ:

```python
model = list(...)
```

Model của Qt cung cấp **interface** để View truy vấn dữ liệu.

Về concept:

```text
View hỏi:

rowCount()
    ↓
Model trả lời

data(index)
    ↓
Model trả lời
```

Đây là nền tảng để hiểu:

```text
QModelIndex
Roles
QAbstractListModel
QAbstractTableModel
```

ở các buổi sau.

---

# 25. Mental Model quan trọng nhất hôm nay

Hãy tưởng tượng View là một người hỏi:

```text
View:
"Bạn có bao nhiêu item?"

Model:
"10."

View:
"Item số 3 là gì?"

Model:
"PySide6."

View:
"Text của item này là gì?"

Model:
"PySide6."

View:
"Item này có icon không?"

Model:
"Có."
```

View **không cần biết dữ liệu nằm ở đâu**.

---

# 26. Model có thể lấy dữ liệu từ đâu?

Ví dụ:

### Python list

```text
list
 ↓
Model
 ↓
View
```

### SQLite

```text
SQLite
 ↓
Repository
 ↓
Model
 ↓
View
```

### REST API

```text
HTTP API
 ↓
Repository
 ↓
Model
 ↓
View
```

### Filesystem

```text
Filesystem
 ↓
Model
 ↓
QTreeView
```

Đây là lý do Model/View rất mạnh.

---

# 27. Model/View và Separation of Concerns

Chúng ta đang tách:

```text
Data
```

khỏi:

```text
Presentation
```

Cụ thể:

```text
Repository
    ↓
Data access

Model
    ↓
Qt data interface

View
    ↓
Presentation

Delegate
    ↓
Rendering / Editing
```

Đây là nền tảng cho app lớn.

---

# 28. Model/View không phải chỉ để hiển thị

Model còn có thể hỗ trợ:

```text
Read
Write
Edit
Insert
Remove
Sort
Filter
```

Ví dụ:

```text
User edit item
      ↓
View
      ↓
Model.setData()
      ↓
Repository
      ↓
Database
```

Chúng ta sẽ học kỹ hơn ở:

```text
Buổi 15 — QAbstractListModel
Buổi 16 — QAbstractTableModel
Buổi 19 — Roles
Buổi 20 — Delegate
Buổi 21 — Sorting & Filtering
```

---

# 29. Signal trong Model/View

Đây là một phần cực kỳ quan trọng.

Khi Model thay đổi:

```text
Model
 ↓
Signal
 ↓
View
 ↓
Update
```

Ví dụ concept:

```text
beginInsertRows()
      ↓
data inserted
      ↓
endInsertRows()
```

hoặc:

```text
dataChanged
```

Chúng ta sẽ học kỹ khi xây `QAbstractListModel`.

---

# 30. Tại sao không học ngay `QAbstractListModel`?

Vì nếu nhảy ngay vào:

```python
class TodoModel(QAbstractListModel):
```

rất dễ học theo kiểu:

> Copy code nhưng không hiểu tại sao.

Trước tiên cần hiểu:

```text
Model
View
Data
Signal
Index
Role
```

Sau đó mới xây:

```text
QAbstractListModel
```

---

# 31. So sánh `QListWidget` và `QListView`

|                   | `QListWidget` | `QListView`        |
| ----------------- | ------------- | ------------------ |
| Kiểu              | Convenience   | Model/View         |
| Data              | Item-based    | Model-based        |
| Dễ học            | ⭐⭐⭐⭐⭐         | ⭐⭐⭐                |
| App nhỏ           | Rất tốt       | Tốt                |
| App lớn           | Hạn chế       | Rất tốt            |
| Model riêng       | Không cần     | Bắt buộc           |
| Custom data       | Hạn chế       | Rất mạnh           |
| Sorting/filtering | Có            | Rất mạnh với Proxy |

Quy tắc thực tế:

```text
UI nhỏ
 ↓
QListWidget
```

Ứng dụng dữ liệu lớn:

```text
Model
 ↓
QListView
```

---

# 32. Một sai lầm phổ biến

Beginner thường nghĩ:

```text
QListView
    ↓
addItem()
```

❌ Không.

`QListView` không hoạt động như `QListWidget`.

Bạn không làm:

```python
view.addItem("Python")
```

Mà:

```python
model = QStringListModel([
    "Python",
    "PySide6",
])

view.setModel(model)
```

---

# 33. Một sai lầm khác

Đừng làm:

```python
view.model().todos.append(...)
```

để thay đổi data một cách tùy tiện.

Model phải quản lý lifecycle và thông báo thay đổi đúng cách.

Sau này chúng ta sẽ học:

```text
beginInsertRows()
endInsertRows()

beginRemoveRows()
endRemoveRows()

dataChanged
```

---

# 34. Liên hệ với Todo App v1

Hiện tại:

```text
TodoRepository
     ↓
MainWindow
     ↓
QListWidget
```

Mục tiêu sau phần Model/View:

```text
TodoRepository
     ↓
TodoListModel
     ↓
QListView
     ↓
MainWindow
```

Và sau đó:

```text
TodoRepository
       ↓
TodoListModel
       ↓
QSortFilterProxyModel
       ↓
QListView
```

Lúc đó:

```text
All
Active
Completed
Search
Sort
```

sẽ trở nên sạch hơn rất nhiều.

---

# 35. Bài tập 1 — `QStringListModel`

Tạo app:

```text
┌──────────────────────┐
│ Python               │
│ PySide6              │
│ SQLite               │
│ Redis                │
│ Docker               │
└──────────────────────┘
```

Yêu cầu:

```python
QStringListModel
QListView
```

Không được dùng:

```python
QListWidget
```

---

# 36. Bài tập 2 — Hai View

Tạo:

```text
        QStringListModel
             /      \
            /        \
           ↓          ↓
      QListView    QListView
```

Hiển thị hai View cạnh nhau.

Thử thay đổi:

```python
model.setStringList(...)
```

và quan sát cả hai View.

---

# 37. Bài tập 3 — Todo

Tạo:

```python
todos = [
    "Learn Python",
    "Learn PySide6",
    "Learn SQLite",
]
```

Dùng:

```text
QStringListModel
      ↓
QListView
```

hiển thị danh sách.

Không được dùng:

```text
QListWidget
```

---

# 38. Bài tập 4 — Tách Data và View

Thiết kế:

```text
todos
  ↓
TodoModel
  ↓
QListView
```

Không để `MainWindow` trực tiếp render:

```python
addItem(...)
```

MainWindow chỉ làm nhiệm vụ:

```text
create UI
connect actions
```

---

# 39. Bài tập 5 — Suy nghĩ kiến trúc

Hãy thiết kế:

```text
Story Reader App
```

có:

```text
Database
   ↓
Repository
   ↓
Model
   ↓
QListView
```

Dữ liệu:

```text
Story
├── id
├── title
├── author
└── status
```

Câu hỏi:

> `Story` nên thuộc View hay Model?

Đáp án: **không thuộc View**.

---

# 40. Bài tập Deep Dive

Bạn hãy tự trả lời:

### Câu 1

Sự khác nhau cơ bản giữa:

```text
QListWidget
```

và:

```text
QListView
```

là gì?

### Câu 2

Tại sao Model/View giúp tách:

```text
Data
```

khỏi:

```text
UI
```

?

### Câu 3

Một Model có thể được sử dụng bởi bao nhiêu View?

### Câu 4

Nếu dữ liệu nằm trong SQLite thì kiến trúc nên là:

```text
?
 ↓
?
 ↓
?
```

### Câu 5

`QListView` có tự chứa Todo objects không?

---

# 41. Kiến thức cần nhớ sau Buổi 11

Nếu chỉ nhớ **5 thứ**, hãy nhớ:

```text
1. Model = cung cấp dữ liệu
2. View = hiển thị dữ liệu
3. View không nên sở hữu business data
4. Một Model có thể phục vụ nhiều View
5. QListView + Model là hướng đi cho app lớn
```

Và đặc biệt:

```text
QListWidget
    ↓
dễ dùng

QListView
    ↓
Model/View
    ↓
kiến trúc chuyên nghiệp
```

---

# 42. Roadmap tiếp theo

Buổi 12:

# `QListView` Deep Dive

Chúng ta sẽ đi sâu vào:

```text
QListView
├── setModel()
├── selection
├── currentIndex()
├── clicked
├── doubleClicked
├── activated
├── edit
├── drag & drop
├── display mode
└── interaction
```

Sau đó:

```text
Buổi 13 → QTableView
Buổi 14 → QTreeView
Buổi 15 → QAbstractListModel
```

**Đặc biệt Buổi 15 sẽ là bước ngoặt:** chúng ta sẽ tự viết `TodoListModel` kế thừa `QAbstractListModel`, thay thế `QStringListModel`, và bắt đầu refactor **Todo App v1 → Todo App Model/View**.
