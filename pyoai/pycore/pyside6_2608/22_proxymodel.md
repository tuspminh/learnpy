# Buổi 22 — `QSortFilterProxyModel` chuyên sâu

Đây là một trong những buổi **quan trọng nhất của phần Model/View**.

Sau Buổi 21, bạn đã biết:

```text
Model
   ↓
Proxy
   ↓
View
```

Hôm nay chúng ta sẽ tự xây một `TodoProxyModel` có:

* Search
* Filter Status
* Filter Priority
* Filter nhiều điều kiện
* Custom sorting
* `filterAcceptsRow()`
* `lessThan()`
* `invalidateFilter()`
* `mapToSource()`
* `mapFromSource()`
* `UserRole`

---

# 1. Ôn lại kiến trúc

Không có Proxy:

```text
TodoModel
    ↓
QTableView
```

Có Proxy:

```text
TodoModel
    ↓
QSortFilterProxyModel
    ↓
QTableView
```

Điểm quan trọng:

> `TodoModel` chứa dữ liệu gốc. `TodoProxyModel` chỉ tạo ra một **projection** của dữ liệu đó.

Ví dụ Source:

```text
Python       3    Doing
SQLite       1    Todo
PySide6      5    Done
Qt           4    Doing
```

Proxy:

```text
Search = "Py"
Status = Doing
Priority >= 3
```

View:

```text
PySide6      5    Doing
```

Source Model vẫn giữ nguyên.

---

# 2. `QSortFilterProxyModel`

Import:

```python
from PySide6.QtCore import (
    QSortFilterProxyModel,
)
```

Tạo:

```python
proxy = QSortFilterProxyModel()
```

Gắn Source Model:

```python
proxy.setSourceModel(model)
```

Cuối cùng:

```python
view.setModel(proxy)
```

Flow:

```text
TodoModel
    │
    │ source
    ▼
QSortFilterProxyModel
    │
    │ projection
    ▼
QTableView
```

---

# 3. Tại sao phải subclass?

`QSortFilterProxyModel` có sẵn filtering và sorting cơ bản.

Nhưng Todo App của chúng ta cần:

```text
Search
Status
Priority
Completed
Custom sorting
```

Vì vậy:

```python
class TodoProxyModel(
    QSortFilterProxyModel
):
    ...
```

---

# 4. Thiết kế Proxy

Chúng ta bắt đầu:

```python
from PySide6.QtCore import (
    QSortFilterProxyModel,
)


class TodoProxyModel(
    QSortFilterProxyModel
):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._search_text = ""
        self._status = "All"
        self._min_priority = 0
```

Proxy giữ **filter state**:

```text
_search_text
_status
_min_priority
```

---

# 5. Setter cho Search

```python
def set_search_text(self, text: str):

    self._search_text = text.strip()

    self.invalidateFilter()
```

Điểm quan trọng:

```python
self.invalidateFilter()
```

nói với Proxy:

> Điều kiện filter đã thay đổi, hãy đánh giá lại các row.

---

# 6. Setter cho Status

```python
def set_status(self, status: str):

    self._status = status

    self.invalidateFilter()
```

Ví dụ:

```python
proxy.set_status("Doing")
```

---

# 7. Setter cho Priority

```python
def set_min_priority(self, priority: int):

    self._min_priority = priority

    self.invalidateFilter()
```

Ví dụ:

```python
proxy.set_min_priority(3)
```

---

# 8. `filterAcceptsRow()`

Đây là trái tim của custom filtering.

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):
    ...
```

Nó phải trả:

```text
True
    ↓
row được hiển thị

False
    ↓
row bị ẩn
```

---

# 9. Lấy Source Model

Trong Proxy:

```python
model = self.sourceModel()
```

Ví dụ:

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):

    model = self.sourceModel()
```

---

# 10. Lấy QModelIndex

Ví dụ Title nằm ở column `0`:

```python
title_index = model.index(
    source_row,
    0,
    source_parent,
)
```

Status column:

```python
status_index = model.index(
    source_row,
    2,
    source_parent,
)
```

Priority:

```python
priority_index = model.index(
    source_row,
    1,
    source_parent,
)
```

---

# 11. Lấy dữ liệu bằng Role

Title:

```python
title = title_index.data(
    Qt.ItemDataRole.DisplayRole
)
```

Priority:

```python
priority = priority_index.data(
    Qt.ItemDataRole.DisplayRole
)
```

Nhưng tốt hơn nữa là dùng `UserRole`.

---

# 12. Dùng `UserRole`

Giả sử Model định nghĩa:

```python
TODO_ID_ROLE = (
    Qt.ItemDataRole.UserRole + 1
)

STATUS_ROLE = (
    Qt.ItemDataRole.UserRole + 2
)

PRIORITY_ROLE = (
    Qt.ItemDataRole.UserRole + 3
)
```

Khi đó:

```python
status = status_index.data(
    STATUS_ROLE
)
```

và:

```python
priority = priority_index.data(
    PRIORITY_ROLE
)
```

Đây là cách tốt hơn việc parse text hiển thị.

---

# 13. Tại sao `UserRole` tốt hơn?

Ví dụ UI hiển thị:

```text
★★★★★
```

Nhưng dữ liệu thực sự là:

```python
5
```

Nếu Proxy dựa vào:

```python
DisplayRole
```

thì nó phải xử lý:

```text
★★★★★
```

Trong khi:

```python
UserRole
```

có thể trả:

```python
5
```

Do đó:

```text
DisplayRole
    → presentation

UserRole
    → semantic data
```

---

# 14. Search

Logic:

```python
if self._search_text:
    if self._search_text.lower() not in title.lower():
        return False
```

Tức:

```text
Search không match
        ↓
      False
```

---

# 15. Status

```python
if self._status != "All":
    if status != self._status:
        return False
```

Ví dụ:

```text
status = Doing
```

chỉ:

```text
Doing → True
Todo  → False
Done  → False
```

---

# 16. Priority

```python
if priority < self._min_priority:
    return False
```

Ví dụ:

```text
min_priority = 3
```

thì:

```text
1 → False
2 → False
3 → True
4 → True
5 → True
```

---

# 17. Kết hợp nhiều điều kiện

Full logic:

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):

    model = self.sourceModel()

    title_index = model.index(
        source_row,
        0,
        source_parent,
    )

    priority_index = model.index(
        source_row,
        1,
        source_parent,
    )

    status_index = model.index(
        source_row,
        2,
        source_parent,
    )

    title = title_index.data(
        Qt.ItemDataRole.DisplayRole
    )

    priority = priority_index.data(
        PRIORITY_ROLE
    )

    status = status_index.data(
        STATUS_ROLE
    )

    if self._search_text:
        if self._search_text.lower() not in title.lower():
            return False

    if self._status != "All":
        if status != self._status:
            return False

    if priority < self._min_priority:
        return False

    return True
```

Đây chính là:

```text
Search
   AND
Status
   AND
Priority
```

---

# 18. Đừng viết filter thành một expression khổng lồ

Không nên:

```python
return (
    (...) and (...) and (...) and (...)
)
```

vì rất khó debug.

Tốt hơn:

```python
if condition_1:
    return False

if condition_2:
    return False

if condition_3:
    return False

return True
```

Đọc rất tự nhiên:

> Không đạt điều kiện nào → loại.

---

# 19. Custom Sorting với `lessThan()`

`QSortFilterProxyModel` cho phép override:

```python
def lessThan(
    self,
    left,
    right,
):
    ...
```

Nó trả:

```text
True
    ↓
left đứng trước right
```

---

# 20. Sort Title

```python
def lessThan(
    self,
    left,
    right,
):

    left_value = left.data(
        Qt.ItemDataRole.DisplayRole
    )

    right_value = right.data(
        Qt.ItemDataRole.DisplayRole
    )

    return left_value.lower() < right_value.lower()
```

Kết quả:

```text
Python
Qt
SQLite
```

không bị ảnh hưởng bởi chữ hoa/chữ thường.

---

# 21. Sort Priority

Nếu column Priority là `1`:

```python
if left.column() == 1:

    left_value = left.data(
        PRIORITY_ROLE
    )

    right_value = right.data(
        PRIORITY_ROLE
    )

    return left_value < right_value
```

Đây là numeric sorting.

---

# 22. Tại sao không sort bằng text?

Nếu Priority là:

```text
1
2
10
20
```

Sort string có thể thành:

```text
1
10
2
20
```

Sai với numeric ordering.

Vì vậy:

```python
UserRole
    ↓
int
    ↓
numeric sorting
```

---

# 23. Sort Status

Có thể muốn thứ tự:

```text
Todo
Doing
Done
```

thay vì alphabet:

```text
Doing
Done
Todo
```

Ta tạo:

```python
STATUS_ORDER = {
    "Todo": 0,
    "Doing": 1,
    "Done": 2,
}
```

Sau đó:

```python
if left.column() == 2:

    left_status = left.data(
        STATUS_ROLE
    )

    right_status = right.data(
        STATUS_ROLE
    )

    return (
        STATUS_ORDER[left_status]
        <
        STATUS_ORDER[right_status]
    )
```

---

# 24. Custom sort hoàn chỉnh

```python
def lessThan(
    self,
    left,
    right,
):

    column = left.column()

    if column == 1:

        left_value = left.data(
            PRIORITY_ROLE
        )

        right_value = right.data(
            PRIORITY_ROLE
        )

        return left_value < right_value

    if column == 2:

        left_value = left.data(
            STATUS_ROLE
        )

        right_value = right.data(
            STATUS_ROLE
        )

        return (
            STATUS_ORDER[left_value]
            <
            STATUS_ORDER[right_value]
        )

    left_value = left.data(
        Qt.ItemDataRole.DisplayRole
    )

    right_value = right.data(
        Qt.ItemDataRole.DisplayRole
    )

    return (
        str(left_value).lower()
        <
        str(right_value).lower()
    )
```

---

# 25. `setDynamicSortFilter()`

Bạn có thể:

```python
proxy.setDynamicSortFilter(True)
```

Điều này hữu ích khi source data thay đổi.

Ví dụ:

```text
Priority = 2
```

đang ở vị trí:

```text
row 5
```

User sửa:

```text
Priority = 5
```

Nếu đang sort Priority:

```text
Proxy
   ↓
re-evaluate
   ↓
item có thể di chuyển
```

---

# 26. Search Box

UI:

```text
┌─────────────────────────────┐
│ Search: [ Python          ] │
└─────────────────────────────┘
```

Code:

```python
search_edit.textChanged.connect(
    proxy.set_search_text
)
```

Mỗi lần user gõ:

```text
P
Py
Pyt
Pyth
Pytho
Python
```

Proxy:

```text
set_search_text()
       ↓
invalidateFilter()
       ↓
filterAcceptsRow()
```

---

# 27. Status ComboBox

```python
status_combo.addItems([
    "All",
    "Todo",
    "Doing",
    "Done",
])
```

Connect:

```python
status_combo.currentTextChanged.connect(
    proxy.set_status
)
```

---

# 28. Priority SpinBox

```python
priority_spin.setRange(
    0,
    5,
)
```

Connect:

```python
priority_spin.valueChanged.connect(
    proxy.set_min_priority
)
```

---

# 29. UI hoàn chỉnh

Ta có:

```text
┌──────────────────────────────────────────┐
│ Search: [ PySide6       ]                │
│ Status: [ Doing ▼ ] Priority >= [ 3 ]   │
├──────────────────────────────────────────┤
│ Title             Priority    Status     │
├──────────────────────────────────────────┤
│ Learn PySide6        5        Doing      │
│ Qt Model/View        4        Doing      │
└──────────────────────────────────────────┘
```

Architecture:

```text
QLineEdit
    │
QComboBox
    │
QSpinBox
    │
    ▼
TodoProxyModel
    │
    ▼
TodoTableModel
    │
    ▼
Todo
```

---

# 30. `mapToSource()` cực kỳ quan trọng

Giả sử View đang hiển thị:

```text
Proxy row 0 → PySide6
Proxy row 1 → Qt
```

Source:

```text
Source row 0 → Python
Source row 1 → PySide6
Source row 2 → SQLite
Source row 3 → Qt
```

Khi click:

```python
proxy_index = view.currentIndex()
```

đây là:

```text
Proxy Index
```

Muốn lấy Source:

```python
source_index = proxy.mapToSource(
    proxy_index
)
```

Kết quả:

```text
Proxy row 0
     ↓
Source row 1
```

---

# 31. `mapFromSource()`

Ngược lại:

```python
proxy_index = proxy.mapFromSource(
    source_index
)
```

Ví dụ:

```text
Source row 3
     ↓
Proxy
     ↓
Proxy row 1
```

Nếu item bị filter:

```text
Source row 0
     ↓
không xuất hiện trong Proxy
```

thì Proxy index có thể là invalid.

---

# 32. Xóa Todo đúng cách

Đây là nơi nhiều người mới học mắc lỗi.

Bạn có:

```python
proxy_index = view.currentIndex()
```

Không nên trực tiếp:

```python
model.removeRow(
    proxy_index.row()
)
```

Vì:

```text
proxy_index.row()
```

là row của Proxy.

Đúng:

```python
source_index = proxy.mapToSource(
    proxy_index
)

model.removeRow(
    source_index.row()
)
```

Flow:

```text
View
 ↓
Proxy Index
 ↓ mapToSource()
Source Index
 ↓
Source Model
 ↓
remove
```

---

# 33. Lấy Todo ID còn tốt hơn

Nếu Model có:

```python
TODO_ID_ROLE
```

thì:

```python
todo_id = proxy_index.data(
    TODO_ID_ROLE
)
```

Sau đó Application Service:

```python
delete_todo(todo_id)
```

Kiến trúc tốt hơn:

```text
View
 ↓
Proxy Index
 ↓
Todo ID
 ↓
Use Case
 ↓
Repository
```

Không phụ thuộc vào row.

---

# 34. Tại sao ID tốt hơn row?

Row có thể thay đổi:

```text
Before:

row 0 → Todo A
row 1 → Todo B
row 2 → Todo C
```

Sau sorting:

```text
row 0 → Todo C
row 1 → Todo A
row 2 → Todo B
```

Nhưng:

```text
Todo A → ID 101
Todo B → ID 102
Todo C → ID 103
```

ID không đổi.

Vì vậy trong app thật:

> **Row là presentation concept. ID là domain identity.**

---

# 35. Proxy không sở hữu Todo

Đừng làm:

```python
class TodoProxyModel:

    self.todos = []
```

Nếu Source Model đã sở hữu data.

Đúng:

```text
TodoProxyModel
    │
    └── sourceModel()
             ↓
         TodoModel
```

Proxy chỉ giữ:

```text
Filter State
Sort behavior
Presentation logic
```

---

# 36. Proxy có thể chain

Đây là kiến thức rất hay.

Bạn có thể:

```text
DatabaseModel
      ↓
Proxy 1
      ↓
Proxy 2
      ↓
Proxy 3
      ↓
View
```

Ví dụ:

```text
TodoModel
    ↓
StatusProxy
    ↓
SearchProxy
    ↓
QTableView
```

Tuy nhiên thường ta có thể gộp các filter vào một Proxy để đơn giản hơn.

---

# 37. Khi nào chain Proxy?

Ví dụ ứng dụng lớn:

```text
Source Model
    ↓
Permission Proxy
    ↓
Search Proxy
    ↓
Sort Proxy
    ↓
View
```

Mỗi Proxy có một trách nhiệm riêng.

Nhưng:

> Không nên tạo 10 lớp Proxy chỉ vì có thể.

Nếu một `TodoProxyModel` đủ rõ ràng thì dùng một Proxy.

---

# 38. Proxy và Clean Architecture

Đây là cách mình khuyến nghị cho project của bạn:

```text
presentation/
    models/
        todo_model.py
        todo_proxy.py

application/
    use_cases/
        create_todo.py
        update_todo.py
        delete_todo.py

domain/
    entities/
        todo.py

infrastructure/
    repositories/
        sqlite_todo_repository.py
```

Flow:

```text
QTableView
    ↓
TodoProxyModel
    ↓
TodoModel
    ↓
Application
    ↓
Domain
    ↓
Repository
```

---

# 39. Một nguyên tắc rất quan trọng

Proxy **không nên gọi Repository**:

```python
# ❌
self.repository.search(...)
```

Không nên.

Proxy nên làm:

```text
presentation filtering
```

Nếu user muốn search Database với:

```text
1.000.000 records
```

thì đây là vấn đề khác:

```text
Application Query
        ↓
Repository
        ↓
Database
```

không nên load toàn bộ 1 triệu record vào Model rồi Proxy filter.

---

# 40. Proxy phù hợp khi nào?

Rất phù hợp:

```text
100
1.000
10.000
```

item trong memory, tùy dữ liệu và UI.

Ví dụ:

```text
Todo App
File Explorer
Settings
Contacts
Small inventory
```

---

# 41. Khi nào không nên filter bằng Proxy?

Nếu database có:

```text
10 triệu records
```

và user search:

```text
"python"
```

thì không nên:

```text
Database
   ↓
10 million rows
   ↓
TodoModel
   ↓
Proxy
```

Mà nên:

```text
Search
   ↓
Use Case
   ↓
Repository
   ↓
SQL WHERE
   ↓
LIMIT/OFFSET
   ↓
Model
   ↓
View
```

Đây là sự khác biệt giữa:

```text
UI filtering
```

và:

```text
data querying
```

---

# 42. TodoProxyModel hoàn chỉnh

Một skeleton tốt:

```python
from PySide6.QtCore import (
    Qt,
    QSortFilterProxyModel,
)


TODO_ID_ROLE = (
    Qt.ItemDataRole.UserRole + 1
)

STATUS_ROLE = (
    Qt.ItemDataRole.UserRole + 2
)

PRIORITY_ROLE = (
    Qt.ItemDataRole.UserRole + 3
)


STATUS_ORDER = {
    "Todo": 0,
    "Doing": 1,
    "Done": 2,
}


class TodoProxyModel(
    QSortFilterProxyModel
):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._search_text = ""
        self._status = "All"
        self._min_priority = 0

        self.setDynamicSortFilter(True)

    def set_search_text(self, text: str):

        self._search_text = text.strip()

        self.invalidateFilter()

    def set_status(self, status: str):

        self._status = status

        self.invalidateFilter()

    def set_min_priority(
        self,
        priority: int,
    ):

        self._min_priority = priority

        self.invalidateFilter()

    def filterAcceptsRow(
        self,
        source_row,
        source_parent,
    ):

        model = self.sourceModel()

        title_index = model.index(
            source_row,
            0,
            source_parent,
        )

        priority_index = model.index(
            source_row,
            1,
            source_parent,
        )

        status_index = model.index(
            source_row,
            2,
            source_parent,
        )

        title = title_index.data(
            Qt.ItemDataRole.DisplayRole
        )

        priority = priority_index.data(
            PRIORITY_ROLE
        )

        status = status_index.data(
            STATUS_ROLE
        )

        if self._search_text:
            if (
                self._search_text.lower()
                not in str(title).lower()
            ):
                return False

        if self._status != "All":
            if status != self._status:
                return False

        if priority < self._min_priority:
            return False

        return True

    def lessThan(
        self,
        left,
        right,
    ):

        column = left.column()

        if column == 1:

            left_value = left.data(
                PRIORITY_ROLE
            )

            right_value = right.data(
                PRIORITY_ROLE
            )

            return left_value < right_value

        if column == 2:

            left_value = left.data(
                STATUS_ROLE
            )

            right_value = right.data(
                STATUS_ROLE
            )

            return (
                STATUS_ORDER[left_value]
                <
                STATUS_ORDER[right_value]
            )

        left_value = left.data(
            Qt.ItemDataRole.DisplayRole
        )

        right_value = right.data(
            Qt.ItemDataRole.DisplayRole
        )

        return (
            str(left_value).lower()
            <
            str(right_value).lower()
        )
```

Đây là một `Proxy Model` khá gần với code thực tế.

---

# 43. Một lưu ý về `lessThan()`

Trong code production, dữ liệu có thể là:

```text
None
null
empty string
```

Vì vậy không nên mặc định:

```python
return left_value.lower() < right_value.lower()
```

mà nên normalize:

```python
left_value = str(left_value or "").lower()
right_value = str(right_value or "").lower()
```

Tương tự với numeric values.

---

# 44. Debug Proxy

Khi filter không hoạt động, hãy kiểm tra:

```python
print(self._search_text)
print(status)
print(priority)
```

và:

```python
print(source_row)
```

Quan trọng nhất:

```text
source_row
```

là row của:

```text
Source Model
```

không phải Proxy.

---

# 45. `filterAcceptsRow()` không nhận Proxy row

Đây là lỗi rất phổ biến.

Trong:

```python
filterAcceptsRow(
    source_row,
    source_parent,
)
```

`source_row` là:

```text
Source Model row
```

Do đó:

```python
model = self.sourceModel()
```

là chính xác.

---

# 46. `lessThan()` cũng cần hiểu Index

Bạn nhận:

```python
left
right
```

là:

```text
QModelIndex
```

và có thể:

```python
left.row()
left.column()
left.data(...)
```

Bạn đang so sánh:

```text
left item
vs
right item
```

---

# 47. Search Regex hay Text?

Có hai hướng.

### Text search

```python
proxy.setFilterRegularExpression(
    text
)
```

đơn giản.

### Custom filter

```python
filterAcceptsRow()
```

tốt khi có:

```text
Search
Status
Priority
Date
Completed
Tags
```

Trong Todo App của chúng ta:

> Custom Proxy là lựa chọn phù hợp để học.

---

# 48. Bài tập chính

Hãy xây Todo Explorer:

```text
┌─────────────────────────────────────────────┐
│ Search [_____________]                      │
│                                             │
│ Status   [All ▼]    Priority >= [0]        │
├─────────────────────────────────────────────┤
│ Title              Priority    Status       │
├─────────────────────────────────────────────┤
│ Learn Python          5        Doing        │
│ Learn PySide6         4        Doing        │
│ Learn SQLite          3        Done         │
└─────────────────────────────────────────────┘
```

Yêu cầu:

### Search

```text
"python"
```

### Status

```text
All
Todo
Doing
Done
```

### Priority

```text
0 → 5
```

### Sorting

Click header:

```text
Title
Priority
Status
```

### Selection

Click một Todo:

```python
todo_id = proxy_index.data(
    TODO_ID_ROLE
)
```

---

# 49. Bài tập nâng cao — AND / OR

Hiện tại:

```text
Search
AND
Status
AND
Priority
```

Hãy thêm:

```text
Match:
○ ALL
○ ANY
```

ALL:

```text
Search AND Status AND Priority
```

ANY:

```text
Search OR Status OR Priority
```

Bạn sẽ phải thiết kế lại:

```python
filterAcceptsRow()
```

Đây là bài tập rất tốt để luyện tư duy boolean.

---

# 50. Bài tập nâng cao — Date

Todo thêm:

```text
due_date
```

Filter:

```text
Due before
Due after
Overdue
```

Kiến trúc:

```text
Search
Status
Priority
Due Date
      ↓
TodoProxyModel
```

Đây gần như là một filter engine nhỏ.

---

# 51. Những lỗi cần tránh

### ❌ Lọc bằng cách xóa dữ liệu

```python
self.todos = [...]
```

### ❌ Proxy truy cập SQLite

```python
proxy.repository.search(...)
```

### ❌ Dùng Proxy row để xóa Source Model

```python
model.removeRow(
    proxy_index.row()
)
```

### ❌ Quên `invalidateFilter()`

```python
self._status = status
```

nhưng không:

```python
self.invalidateFilter()
```

### ❌ Sort numeric bằng string

```text
1
10
2
```

---

# 52. Mental Model Buổi 22

Bạn cần nhớ chính xác:

```text
                     QTableView
                         │
                         │ Proxy Index
                         ▼
               QSortFilterProxyModel
                    │          │
              Filtering      Sorting
                    │          │
                    └────┬─────┘
                         │
                         ▼
                    TodoModel
                         │
                         ▼
                       Todo
```

Filtering:

```text
filterAcceptsRow()
       ↓
True / False
```

Sorting:

```text
lessThan()
       ↓
left < right
```

Filter state thay đổi:

```text
set_xxx()
   ↓
invalidateFilter()
```

Selection:

```text
Proxy Index
   ↓
mapToSource()
   ↓
Source Index
```

Ngược lại:

```text
Source Index
   ↓
mapFromSource()
   ↓
Proxy Index
```

---

# 53. Kết nối với các buổi trước

Bạn đã đi qua một chuỗi rất quan trọng:

```text
Buổi 11
Model/View Architecture
       ↓
Buổi 12
QListView
       ↓
Buổi 13
QTableView
       ↓
Buổi 14
QTreeView
       ↓
Buổi 15
QAbstractListModel
       ↓
Buổi 16
QAbstractTableModel
       ↓
Buổi 17
QAbstractItemModel
       ↓
Buổi 18
QModelIndex
       ↓
Buổi 19
Roles
       ↓
Buổi 20
Delegate
       ↓
Buổi 21
Sorting & Filtering
       ↓
⭐ Buổi 22
Proxy Model
```

Từ đây bạn đã có gần như toàn bộ các mảnh quan trọng của Qt Model/View.

---

## 🎯 Bài tập cuối buổi

Đừng chỉ đọc code. Hãy tự xây:

```text
TodoTableModel
        ↓
TodoProxyModel
        ↓
QTableView
```

và thêm:

```text
QLineEdit
    → Search

QComboBox
    → Status

QSpinBox
    → Minimum Priority
```

Sau đó kiểm tra 4 tình huống:

```text
1. Search
2. Status filter
3. Priority filter
4. Search + Status + Priority
```

Cuối cùng click một row sau khi filter/sort và chứng minh rằng:

```python
proxy.mapToSource(
    view.currentIndex()
)
```

vẫn lấy đúng Todo trong Source Model.

**Buổi 23 — Selection Model** sẽ nối trực tiếp vào phần này: `QItemSelectionModel`, `currentIndex()`, `selectedIndexes()`, selection changed, current changed, multi-selection và cách xây màn hình **Master → Detail** — ví dụ click một Todo bên trái thì panel bên phải hiển thị chi tiết Todo đó.
