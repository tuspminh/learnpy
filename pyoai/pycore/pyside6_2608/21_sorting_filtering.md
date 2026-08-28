# Buổi 21 — Sorting & Filtering trong Qt Model/View

Hôm nay chúng ta học cách cho `QTableView`/`QListView`:

* Sắp xếp dữ liệu
* Lọc dữ liệu
* Tìm kiếm
* Lọc theo nhiều điều kiện
* Chuẩn bị cho `QSortFilterProxyModel` ở Buổi 22

Điểm quan trọng nhất:

> **Sorting/Filtering không nên làm thay đổi dữ liệu gốc.**

---

# 1. Vấn đề thực tế

Giả sử Todo có 10.000 dòng:

```text
┌──────────────────┬──────────┬────────────┐
│ Title            │ Priority │ Status     │
├──────────────────┼──────────┼────────────┤
│ Learn Python     │    3     │ Doing      │
│ Learn SQLite     │    1     │ Todo       │
│ Learn PySide6    │    5     │ Done       │
│ ...
└──────────────────┴──────────┴────────────┘
```

User muốn:

```text
Search: PySide
Priority >= 3
Status = Doing
Sort: Priority DESC
```

Nếu chúng ta sửa trực tiếp:

```python
self.todos = ...
```

thì Model gốc bị thay đổi.

Đây là điều chúng ta **không muốn**.

---

# 2. Có hai khái niệm

Qt tách:

```text
Sorting
    ↓
Sắp xếp

Filtering
    ↓
Lọc
```

Về kiến trúc:

```text
Source Model
     ↓
Proxy Model
     ↓
View
```

Ở Buổi 21 chúng ta hiểu **cơ chế**.

Buổi 22 sẽ đi sâu vào:

```python
QSortFilterProxyModel
```

---

# 3. Sorting là gì?

Ví dụ:

```text
Original

Python       3
SQLite       1
PySide6      5
```

Sort tăng dần:

```text
SQLite       1
Python       3
PySide6      5
```

Sort giảm dần:

```text
PySide6      5
Python       3
SQLite       1
```

---

# 4. View có thể yêu cầu sort

Với `QTableView`:

```python
view.setSortingEnabled(True)
```

Sau đó user có thể click header:

```text
┌───────────────┬──────────┐
│ Title ▲       │ Priority │
├───────────────┼──────────┤
│ Learn Python  │ 1        │
│ Learn SQLite  │ 2        │
│ Learn Qt      │ 3        │
└───────────────┴──────────┘
```

Click lại:

```text
Title ▼
```

thì thứ tự đảo lại.

---

# 5. Nhưng Model phải hỗ trợ sorting

Model có thể implement:

```python
def sort(self, column, order):
    ...
```

Ví dụ:

```python
from PySide6.QtCore import Qt


def sort(self, column, order):

    reverse = (
        order == Qt.SortOrder.DescendingOrder
    )

    self.todos.sort(
        key=lambda todo: todo.title,
        reverse=reverse,
    )
```

---

# 6. `beginResetModel()` và `endResetModel()`

Nếu bạn thay đổi toàn bộ thứ tự dữ liệu:

```python
def sort(self, column, order):

    self.beginResetModel()

    reverse = (
        order == Qt.SortOrder.DescendingOrder
    )

    self.todos.sort(
        key=lambda todo: todo.title,
        reverse=reverse,
    )

    self.endResetModel()
```

View được thông báo:

```text
Model thay đổi
     ↓
View refresh
```

---

# 7. Tuy nhiên có một vấn đề

Nếu:

```python
self.todos.sort(...)
```

thì:

> **Source data đã bị thay đổi thứ tự.**

Ví dụ ban đầu:

```text
todos = [
    Todo(1, "Python"),
    Todo(2, "SQLite"),
    Todo(3, "PySide6"),
]
```

Sau sort:

```text
todos = [
    Todo(2, "SQLite"),
    Todo(1, "Python"),
    Todo(3, "PySide6"),
]
```

Điều này đôi khi không mong muốn.

Đặc biệt trong kiến trúc:

```text
Domain
Repository
Application
Presentation
```

ta thường muốn View có một **presentation order riêng**.

Đây là lý do Proxy Model rất quan trọng.

---

# 8. Filtering

Filtering nghĩa là:

> Chỉ hiển thị item thỏa mãn điều kiện.

Ví dụ:

```text
Original:

Python       Todo
PySide6      Doing
SQLite       Done
Qt           Doing
```

Filter:

```text
Status = Doing
```

View:

```text
PySide6      Doing
Qt           Doing
```

Source Model vẫn có:

```text
Python
PySide6
SQLite
Qt
```

---

# 9. Search cũng là Filtering

Ví dụ:

```text
Search:
"python"
```

Original:

```text
Learn Python
Learn PySide6
Learn SQLite
Python asyncio
```

Result:

```text
Learn Python
Python asyncio
```

Search thực chất là:

```text
Filtering by text
```

---

# 10. Filtering nhiều điều kiện

Ví dụ:

```text
Search = "python"

AND

Status = "Doing"

AND

Priority >= 3
```

Ta có:

```text
               Todos
                 │
          ┌──────┴──────┐
          ↓             ↓
       Search         Status
          ↓             ↓
       matches        Doing
          └──────┬──────┘
                 ↓
          Priority >= 3
                 ↓
              Result
```

---

# 11. Không nên xóa item để filter

Sai:

```python
self.todos = [
    todo
    for todo in self.todos
    if todo.status == "Doing"
]
```

Vì bạn đã làm mất:

```text
Todo
    ↓
Source data
```

Nếu sau đó user bỏ filter:

```text
Status = All
```

dữ liệu cũ đã bị loại khỏi list.

---

# 12. Cách tư duy đúng

Phân biệt:

```text
Source Data
     ↓
Projection
     ↓
Filtered/Sorted View
```

Ví dụ:

```text
Database
   ↓
Repository
   ↓
TodoModel
   ↓
Proxy
   ↓
QTableView
```

Proxy quyết định:

```text
item nào được hiển thị?
thứ tự nào?
```

---

# 13. Proxy Model

Đây là kiến trúc:

```text
                QTableView
                    │
                    ▼
          QSortFilterProxyModel
                    │
                    ▼
               TodoModel
                    │
                    ▼
                  Data
```

User thấy:

```text
Filtered + Sorted data
```

nhưng:

```text
TodoModel
```

vẫn giữ dữ liệu gốc.

---

# 14. Tại sao gọi là Proxy?

Proxy đứng giữa:

```text
View
  ↕
Proxy
  ↕
Source Model
```

View tưởng rằng nó đang làm việc với Model.

Thực tế:

```text
View
  ↓
Proxy
  ↓
Source Model
```

Proxy chuyển tiếp và biến đổi cách dữ liệu được nhìn thấy.

---

# 15. Ví dụ đơn giản

Source:

```text
1 Python
2 PySide6
3 SQLite
4 Qt
```

Filter:

```text
"Python"
```

Proxy chỉ cho View thấy:

```text
1 Python
```

Source Model vẫn:

```text
1 Python
2 PySide6
3 SQLite
4 Qt
```

---

# 16. `QSortFilterProxyModel`

Qt cung cấp sẵn:

```python
from PySide6.QtCore import QSortFilterProxyModel
```

Tạo:

```python
proxy = QSortFilterProxyModel()
```

Gắn source:

```python
proxy.setSourceModel(model)
```

View:

```python
view.setModel(proxy)
```

Đây là pattern quan trọng:

```python
model = TodoModel(todos)

proxy = QSortFilterProxyModel()
proxy.setSourceModel(model)

view.setModel(proxy)
```

---

# 17. Flow

```text
TodoModel
    │
    │ source data
    ▼
QSortFilterProxyModel
    │
    │ filtered/sorted
    ▼
QTableView
```

Khi user search:

```text
Search Box
    ↓
Proxy
    ↓
Filter
    ↓
View
```

---

# 18. Filtering bằng text

Proxy có:

```python
proxy.setFilterRegularExpression(...)
```

Ví dụ:

```python
proxy.setFilterRegularExpression(
    "python"
)
```

Kết quả:

```text
Learn Python
Python asyncio
```

---

# 19. Case insensitive

Ta có thể cấu hình:

```python
from PySide6.QtCore import QRegularExpression

regex = QRegularExpression(
    "python",
)

regex.setPatternOptions(
    QRegularExpression.PatternOption.CaseInsensitiveOption
)

proxy.setFilterRegularExpression(regex)
```

Khi đó:

```text
Python
PYTHON
python
PyThOn
```

đều match.

---

# 20. Filter column

Giả sử:

```text
column 0 = Title
column 1 = Priority
column 2 = Status
```

Ta muốn search chỉ trong Title:

```python
proxy.setFilterKeyColumn(0)
```

Sau đó:

```python
proxy.setFilterRegularExpression(
    "python"
)
```

---

# 21. Filter nhiều column

Nếu muốn:

```text
Title
+
Author
```

thì `QSortFilterProxyModel` mặc định không đơn giản hóa việc đó thành một dòng.

Bạn có thể subclass:

```python
class TodoProxyModel(
    QSortFilterProxyModel
):
    ...
```

và override:

```python
filterAcceptsRow()
```

Đây là kỹ thuật quan trọng.

---

# 22. `filterAcceptsRow()`

Method:

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):
    ...
```

Nó trả:

```text
True
    ↓
hiển thị

False
    ↓
ẩn
```

---

# 23. Ví dụ

```python
class TodoProxyModel(
    QSortFilterProxyModel
):

    def filterAcceptsRow(
        self,
        source_row,
        source_parent,
    ):

        index = self.sourceModel().index(
            source_row,
            0,
            source_parent,
        )

        title = index.data(
            Qt.ItemDataRole.DisplayRole
        )

        return "python" in title.lower()
```

Kết quả:

```text
Learn Python
Python asyncio
```

---

# 24. Filter theo Status

Đây là ví dụ quan trọng hơn.

Todo:

```text
Title           Status
──────────────────────
Python          Todo
PySide6         Doing
SQLite          Done
Qt              Doing
```

Ta muốn:

```text
Status = Doing
```

Proxy:

```python
def filterAcceptsRow(
    self,
    source_row,
    source_parent,
):

    model = self.sourceModel()

    index = model.index(
        source_row,
        2,
        source_parent,
    )

    status = index.data(
        Qt.ItemDataRole.DisplayRole
    )

    return status == "Doing"
```

---

# 25. Filter bằng `UserRole`

Đây chính là lý do Buổi 19 rất quan trọng.

Giả sử:

```python
STATUS_ROLE = (
    Qt.ItemDataRole.UserRole + 2
)
```

Proxy có thể:

```python
status = index.data(
    STATUS_ROLE
)
```

Không cần lấy text:

```text
"Doing"
```

mà lấy dữ liệu semantic:

```text
TodoStatus.DOING
```

Đây là cách thiết kế tốt hơn.

---

# 26. Sort

Proxy cũng có sorting:

```python
proxy.sort(
    column,
    Qt.SortOrder.AscendingOrder,
)
```

Ví dụ:

```python
proxy.sort(
    1,
    Qt.SortOrder.DescendingOrder,
)
```

→ Priority cao nhất lên đầu.

---

# 27. View + Proxy

Khi sử dụng proxy:

```python
view.setModel(proxy)
```

chứ không:

```python
view.setModel(model)
```

Flow:

```text
TodoModel
    ↓
Proxy
    ↓
View
```

---

# 28. `index` của Proxy khác Source Model

Đây là điểm rất quan trọng.

Giả sử Source:

```text
row 0 → Python
row 1 → PySide6
row 2 → SQLite
```

Filter:

```text
PySide6
```

Proxy:

```text
row 0 → PySide6
```

Nhưng:

```text
Proxy row 0
```

không phải:

```text
Source row 0
```

Nó là:

```text
Source row 1
```

---

# 29. `mapToSource()`

Khi click item trong View:

```python
proxy_index = view.currentIndex()
```

Đây là index của:

```text
Proxy Model
```

Nếu muốn index của Source:

```python
source_index = proxy.mapToSource(
    proxy_index
)
```

Flow:

```text
View
 ↓
Proxy Index
 ↓ mapToSource()
Source Index
```

Đây là kiến thức bắt buộc phải nhớ.

---

# 30. `mapFromSource()`

Ngược lại:

```python
proxy_index = proxy.mapFromSource(
    source_index
)
```

Flow:

```text
Source Index
      ↓
mapFromSource()
      ↓
Proxy Index
```

---

# 31. Ví dụ với Todo ID

Bạn click:

```text
Learn PySide6
```

View:

```python
proxy_index = view.currentIndex()
```

Lấy source:

```python
source_index = proxy.mapToSource(
    proxy_index
)
```

Sau đó:

```python
todo_id = source_index.data(
    Qt.ItemDataRole.UserRole
)
```

Kết quả:

```text
Todo ID = 2
```

---

# 32. Tại sao không lấy ID trực tiếp?

Thực ra bạn có thể:

```python
todo_id = proxy_index.data(
    Qt.ItemDataRole.UserRole
)
```

Trong nhiều trường hợp Qt sẽ chuyển tiếp dữ liệu Role.

Nhưng khi cần:

```text
row
parent
source model
setData
structural operations
```

thì phải hiểu:

```python
mapToSource()
```

---

# 33. Search Box hoàn chỉnh

UI:

```text
┌───────────────────────────────┐
│ Search: [ PySide6           ] │
└───────────────────────────────┘

┌──────────────────┬───────────┐
│ Title            │ Status    │
├──────────────────┼───────────┤
│ Learn PySide6    │ Doing     │
└──────────────────┴───────────┘
```

Code:

```python
search.textChanged.connect(
    proxy.setFilterRegularExpression
)
```

Mỗi khi user gõ:

```text
P
Py
PyS
PySi
PySid
PySide
```

Proxy tự filter lại.

---

# 34. Search + Status Filter

Ta có:

```python
self.search_text = ""
self.status = "All"
```

Proxy:

```python
class TodoProxyModel(
    QSortFilterProxyModel
):

    def __init__(self):

        super().__init__()

        self.search_text = ""
        self.status = "All"
```

---

# 35. `set_search_text()`

```python
def set_search_text(self, text):

    self.search_text = text

    self.invalidateFilter()
```

`invalidateFilter()` nói với Proxy:

> Điều kiện filter đã thay đổi, hãy tính lại.

---

# 36. `set_status()`

```python
def set_status(self, status):

    self.status = status

    self.invalidateFilter()
```

Sau đó:

```text
Search
   ↓
set_search_text()
   ↓
invalidateFilter()

Status
   ↓
set_status()
   ↓
invalidateFilter()
```

---

# 37. Filter nhiều điều kiện

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

    status_index = model.index(
        source_row,
        2,
        source_parent,
    )

    title = title_index.data(
        Qt.ItemDataRole.DisplayRole
    )

    status = status_index.data(
        Qt.ItemDataRole.DisplayRole
    )

    if self.search_text:
        if self.search_text.lower() not in title.lower():
            return False

    if self.status != "All":
        if status != self.status:
            return False

    return True
```

Đây là logic:

```text
Search
  AND
Status
```

---

# 38. Thêm Priority

Giả sử:

```text
priority >= min_priority
```

thêm:

```python
if todo_priority < self.min_priority:
    return False
```

Kết quả:

```text
Search
   AND
Status
   AND
Priority
```

---

# 39. Kiến trúc thực tế

Một Todo App tốt:

```text
                  QMainWindow
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
      SearchBox              StatusCombo
          │                       │
          └───────────┬───────────┘
                      ↓
              TodoProxyModel
                      ↓
                 TodoModel
                      ↓
                    Todo
```

View:

```python
view.setModel(proxy)
```

---

# 40. Source Model không biết Filter

Đây là nguyên tắc rất hay.

`TodoModel` chỉ biết:

```text
Todos
```

Nó không cần biết:

```text
Search = "python"
Status = "Doing"
Priority >= 3
```

Proxy biết:

```text
presentation query
```

Source Model giữ:

```text
source data
```

---

# 41. Sorting cũng nên thuộc Proxy

Thay vì:

```python
todo_model.sort(...)
```

ta thường:

```python
proxy.sort(...)
```

Khi đó:

```text
Source
    ↓
giữ dữ liệu

Proxy
    ↓
quyết định thứ tự hiển thị
```

---

# 42. `dynamicSortFilter`

Một property rất đáng biết:

```python
proxy.setDynamicSortFilter(True)
```

Khi source data thay đổi, proxy có thể tự đánh giá lại:

```text
filter
sort
```

Ví dụ Todo:

```text
Priority = 1
```

đổi thành:

```text
Priority = 5
```

Proxy đang sort descending sẽ tự điều chỉnh vị trí khi được cấu hình phù hợp.

---

# 43. `invalidateFilter()`

Khi filter condition của chính bạn thay đổi:

```python
self.search_text = text

self.invalidateFilter()
```

Dùng:

```text
invalidateFilter()
```

để yêu cầu Proxy tính lại filter.

---

# 44. Một điều cần phân biệt

```text
beginResetModel()
```

thuộc Source Model.

```text
invalidateFilter()
```

thuộc Proxy Filter.

Đừng nhầm hai thứ.

### Source thay đổi cấu trúc:

```text
beginInsertRows()
beginRemoveRows()
beginResetModel()
```

### Filter condition thay đổi:

```text
invalidateFilter()
```

---

# 45. Search bằng Regular Expression

Qt Proxy sử dụng:

```python
QRegularExpression
```

Ví dụ:

```python
regex = QRegularExpression(
    "^Python"
)

proxy.setFilterRegularExpression(
    regex
)
```

Match:

```text
Python Tutorial
Python asyncio
```

Không match:

```text
Learn Python
```

---

# 46. Search không phân biệt hoa thường

```python
regex = QRegularExpression(
    text
)

regex.setPatternOptions(
    QRegularExpression.PatternOption.CaseInsensitiveOption
)

proxy.setFilterRegularExpression(
    regex
)
```

---

# 47. Khi nào dùng `filterAcceptsRow()`?

Dùng khi logic filter đơn giản:

```text
Title contains X
Status == Y
Priority >= Z
```

Nếu:

```text
AND
OR
NOT
multiple fields
custom business conditions
```

thì subclass Proxy rất phù hợp.

---

# 48. Nhưng đừng đưa Business Rule vào Proxy

Ví dụ:

```python
if user.age > 18 and ...
```

Nếu đó là business rule thực sự:

```text
Domain
```

không nên nhét vào:

```text
Proxy
```

Proxy chỉ nên quyết định:

> item này có được hiển thị trong projection hiện tại không?

---

# 49. Một Proxy tốt

```text
TodoProxyModel
│
├── search_text
├── status_filter
├── min_priority
│
├── filterAcceptsRow()
│
└── sorting
```

Không nên:

```text
TodoProxyModel
│
├── save_to_database()
├── create_todo()
├── calculate_price()
├── business_rule()
└── send_email()
```

---

# 50. Kiến trúc lớn hơn

Bạn đang học Model/View theo hướng chuyên nghiệp, vì vậy hãy ghi nhớ:

```text
                 UI
                  │
          ┌───────┴────────┐
          ↓                ↓
        View             Controls
          │          Search / Filter
          │                │
          └───────┬────────┘
                  ↓
             Proxy Model
                  ↓
              Source Model
                  ↓
             Application
                  ↓
                Domain
                  ↓
              Repository
                  ↓
               SQLite
```

---

# 51. Ví dụ hoàn chỉnh nhỏ

```python
from PySide6.QtCore import (
    Qt,
    QSortFilterProxyModel,
)
```

Source:

```python
model = TodoModel(todos)
```

Proxy:

```python
proxy = QSortFilterProxyModel()

proxy.setSourceModel(model)

proxy.setFilterKeyColumn(0)

proxy.setFilterCaseSensitivity(
    Qt.CaseSensitivity.CaseInsensitive
)
```

View:

```python
view.setModel(proxy)
```

Search:

```python
search.textChanged.connect(
    proxy.setFilterRegularExpression
)
```

Sort:

```python
view.setSortingEnabled(True)
```

Đây đã là một kiến trúc Model/View thực tế.

---

# 52. Flow khi user search

User nhập:

```text
python
```

↓

```python
search.textChanged
```

↓

```python
proxy.setFilterRegularExpression(
    "python"
)
```

↓

```text
QSortFilterProxyModel
```

↓

```text
filterAcceptsRow()
```

↓

```text
True / False
```

↓

```text
QTableView
```

---

# 53. Flow khi user sort

User click:

```text
Priority ▲
```

↓

```text
QTableView
```

↓

```text
Proxy
```

↓

```text
sort(column, Ascending)
```

↓

```text
View hiển thị lại
```

Source data:

```text
không cần thay đổi
```

---

# 54. Flow khi user click item

```text
QTableView
   ↓
proxy_index
   ↓
proxy.mapToSource()
   ↓
source_index
   ↓
UserRole
   ↓
todo_id
```

Đây là flow bạn sẽ dùng rất nhiều trong ứng dụng thật.

---

# 55. Bài tập 1 — Sorting

Tạo:

```text
Title
Priority
Status
```

Cho phép click header:

```text
Title ↑↓
Priority ↑↓
Status ↑↓
```

---

# 56. Bài tập 2 — Search

Thêm:

```text
QLineEdit
```

```text
Search: [____________]
```

Search theo:

```text
Title
```

Không phân biệt hoa thường.

---

# 57. Bài tập 3 — Status Filter

Thêm:

```text
QComboBox
```

```text
[ All ▼ ]
```

Items:

```text
All
Todo
Doing
Done
```

Khi chọn:

```text
Doing
```

chỉ hiển thị Todo `Doing`.

---

# 58. Bài tập 4 — Search + Status

Cho phép:

```text
Search = "python"
Status = "Doing"
```

Kết quả phải thỏa:

```text
title contains "python"
AND
status == "Doing"
```

---

# 59. Bài tập 5 — Priority

Thêm:

```text
Minimum Priority
```

Ví dụ:

```text
Priority >= 3
```

Kết hợp:

```text
Search
AND
Status
AND
Priority
```

---

# 60. Bài tập 6 — mapToSource

Khi user click Todo:

```python
proxy_index = view.currentIndex()
```

lấy:

```python
source_index = proxy.mapToSource(
    proxy_index
)
```

sau đó:

```python
todo_id = source_index.data(
    Qt.ItemDataRole.UserRole
)
```

In:

```text
Selected Todo ID: 42
```

---

# 61. Bài tập nâng cao

Xây:

```text
┌─────────────────────────────────────────┐
│ Search: [ PySide6           ]           │
│ Status: [ Doing ▼ ] Priority: [ >= 3 ] │
├─────────────────────────────────────────┤
│ Title             Priority    Status    │
├─────────────────────────────────────────┤
│ Learn PySide6       5         Doing     │
│ PySide6 Model       4         Doing     │
└─────────────────────────────────────────┘
```

Kiến trúc:

```text
QLineEdit
QComboBox
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

Đây là bài tập rất tốt trước khi sang Buổi 22.

---

# 62. Tổng kết Buổi 21

Bạn cần phân biệt rõ:

| Thành phần  | Trách nhiệm           |
| ----------- | --------------------- |
| Model       | Dữ liệu nguồn         |
| View        | Hiển thị              |
| Delegate    | Vẽ + Editing          |
| Proxy       | Filter + Sort         |
| QModelIndex | Xác định item         |
| Role        | Xác định loại dữ liệu |

Kiến trúc:

```text
                 View
                  │
                  ▼
            Proxy Model
             │       │
          Filter    Sort
             │       │
             └───┬───┘
                 ↓
             Source Model
                 ↓
               Data
```

### ⭐ Điều quan trọng nhất của Buổi 21

Đừng nghĩ:

```text
Filter = xóa dữ liệu
Sort = đổi dữ liệu
```

Hãy nghĩ:

```text
Source Model
     ↓
  Projection
     ↓
Filtered / Sorted View
```

và:

```text
QSortFilterProxyModel
```

là công cụ Qt thiết kế chính xác cho việc đó.

---

## Chuẩn bị cho Buổi 22

Buổi 21 mới chỉ cho chúng ta hiểu **ý tưởng Sorting/Filtering**.

Ở **Buổi 22 — Proxy Model chuyên sâu**, chúng ta sẽ tự xây một:

```python
class TodoProxyModel(QSortFilterProxyModel):
    ...
```

với:

```text
Search
Status Filter
Priority Filter
Multiple Conditions
Custom Sorting
UserRole
mapToSource()
mapFromSource()
invalidateFilter()
lessThan()
```

và cuối buổi ghép thành:

```text
QLineEdit
    ↓
QComboBox
    ↓
QSpinBox
    ↓
TodoProxyModel
    ↓
TodoTableModel
    ↓
QTableView
```

Đây là lúc Model/View bắt đầu trở thành **kiến trúc thực sự dùng được cho app chuyên nghiệp**.
