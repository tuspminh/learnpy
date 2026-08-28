# Buổi 20 — Delegate trong Qt Model/View

Hôm nay chúng ta học:

```python
QStyledItemDelegate
```

Đây là bước rất quan trọng vì từ đây bạn không chỉ **hiển thị dữ liệu**, mà có thể kiểm soát:

* item được vẽ như thế nào
* editor là gì
* user chỉnh sửa ra sao
* dữ liệu từ editor được trả về Model thế nào

---

# 1. Delegate là gì?

Trong kiến trúc Model/View:

```text
Model
  ↓
QModelIndex
  ↓
Delegate
  ↓
View
```

Delegate chịu trách nhiệm chính cho:

```text
Model
  ↓
data
  ↓
Delegate
  ↓
paint()
  ↓
View
```

và khi chỉnh sửa:

```text
User double-click
       ↓
Delegate
       ↓
createEditor()
       ↓
QLineEdit / QComboBox / QSpinBox
       ↓
setModelData()
       ↓
Model.setData()
```

---

# 2. Tại sao cần Delegate?

Ví dụ `QTableView`:

```text
┌──────────────────┬───────────┐
│ Title            │ Priority  │
├──────────────────┼───────────┤
│ Learn Python     │ 1         │
│ Learn PySide6    │ 2         │
│ Learn SQLite     │ 3         │
└──────────────────┴───────────┘
```

Nếu user double-click:

```text
Priority
```

bạn không nhất thiết muốn:

```text
QLineEdit
```

Bạn có thể muốn:

```text
QSpinBox
```

hoặc:

```text
QComboBox
```

Delegate quyết định điều đó.

---

# 3. Kiến trúc hoàn chỉnh

Bây giờ Model/View có thêm Delegate:

```text
                    QTableView
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
          Delegate             Model
             │                   │
             │                   ↓
             │                 Data
             │
             ├── paint()
             │
             ├── createEditor()
             ├── setEditorData()
             └── setModelData()
```

---

# 4. Delegate không phải Model

Đừng nhầm:

```text
Model
    ↓
"Dữ liệu là gì?"

Delegate
    ↓
"Hiển thị/chỉnh sửa dữ liệu như thế nào?"
```

Ví dụ:

```text
Model:
priority = 2
```

Delegate:

```text
QSpinBox
minimum = 1
maximum = 5
```

---

# 5. `QStyledItemDelegate`

Đây là class bạn nên dùng trong phần lớn trường hợp:

```python
from PySide6.QtWidgets import QStyledItemDelegate
```

Có:

```python
QAbstractItemDelegate
        ↓
QItemDelegate
        ↓
QStyledItemDelegate
```

Trong ứng dụng hiện đại:

```python
QStyledItemDelegate
```

thường là lựa chọn mặc định tốt.

---

# 6. Delegate cơ bản nhất

```python
from PySide6.QtWidgets import (
    QStyledItemDelegate,
)


class TodoDelegate(QStyledItemDelegate):

    pass
```

Sau đó:

```python
delegate = TodoDelegate()

view.setItemDelegate(delegate)
```

Tất cả item trong View sẽ sử dụng Delegate này.

---

# 7. Delegate cho một column

Thường thực tế hơn:

```python
view.setItemDelegateForColumn(
    1,
    delegate,
)
```

Ví dụ:

```text
column 0 → Title
column 1 → Priority
column 2 → Status
```

Chỉ column Priority dùng custom Delegate:

```text
Title      → default
Priority   → custom
Status     → default
```

---

# 8. `paint()`

Method:

```python
paint(
    painter,
    option,
    index,
)
```

dùng để:

> Vẽ item.

Ví dụ:

```python
class TodoDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter,
        option,
        index,
    ):
        ...
```

Ba đối tượng quan trọng:

```text
painter
option
index
```

---

# 9. `painter`

```python
painter
```

là:

```text
QPainter
```

dùng để vẽ:

* text
* line
* rectangle
* icon
* custom shape

Ví dụ:

```python
painter.drawText(
    option.rect,
    Qt.AlignmentFlag.AlignCenter,
    "Hello",
)
```

---

# 10. `option`

```python
option
```

chứa thông tin về trạng thái item:

```text
rect
state
selected
hovered
enabled
focus
```

Ví dụ:

```python
option.rect
```

là vùng mà Delegate được phép vẽ.

---

# 11. `index`

```python
index
```

là `QModelIndex` của item.

Bạn có thể:

```python
text = index.data(
    Qt.ItemDataRole.DisplayRole
)
```

hoặc:

```python
todo_id = index.data(
    Qt.ItemDataRole.UserRole
)
```

Đây chính là kiến thức Buổi 18 + 19 được sử dụng ở đây.

---

# 12. Đừng tự vẽ nếu không cần

Một Delegate cơ bản:

```python
class MyDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter,
        option,
        index,
    ):

        super().paint(
            painter,
            option,
            index,
        )
```

Nếu chỉ cần thay đổi editing thì **không cần override `paint()`**.

Đây là nguyên tắc rất tốt:

> Chỉ override phần Delegate mà bạn thực sự cần thay đổi.

---

# 13. Editing — phần quan trọng nhất

Delegate có 4 method chính:

```text
createEditor()
setEditorData()
setModelData()
updateEditorGeometry()
```

Flow:

```text
User double-click
       ↓
createEditor()
       ↓
Editor
       ↓
setEditorData()
       ↓
User edits
       ↓
setModelData()
       ↓
Model.setData()
```

---

# 14. `createEditor()`

Ví dụ muốn Priority dùng `QSpinBox`:

```python
from PySide6.QtWidgets import (
    QSpinBox,
    QStyledItemDelegate,
)


class PriorityDelegate(QStyledItemDelegate):

    def createEditor(
        self,
        parent,
        option,
        index,
    ):

        editor = QSpinBox(parent)

        editor.setMinimum(1)
        editor.setMaximum(5)

        return editor
```

Khi user double-click:

```text
Priority = 3
```

sẽ xuất hiện:

```text
┌─────┐
│  3  │ ▲
└─────┘ ▼
```

---

# 15. `setEditorData()`

Editor vừa tạo xong.

Delegate cần đưa dữ liệu Model vào Editor.

```python
def setEditorData(
    self,
    editor,
    index,
):

    value = index.data(
        Qt.ItemDataRole.EditRole
    )

    editor.setValue(value)
```

Flow:

```text
Model
  ↓
EditRole
  ↓
Delegate
  ↓
QSpinBox
```

---

# 16. `setModelData()`

User sửa:

```text
3 → 5
```

Delegate phải đưa giá trị về Model:

```python
def setModelData(
    self,
    editor,
    model,
    index,
):

    value = editor.value()

    model.setData(
        index,
        value,
        Qt.ItemDataRole.EditRole,
    )
```

Flow:

```text
QSpinBox
   ↓
value = 5
   ↓
model.setData()
   ↓
Todo.priority = 5
```

---

# 17. `updateEditorGeometry()`

Editor phải nằm đúng vị trí cell.

```python
def updateEditorGeometry(
    self,
    editor,
    option,
    index,
):

    editor.setGeometry(
        option.rect
    )
```

Đây là implementation cơ bản nhất.

---

# 18. Delegate hoàn chỉnh

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSpinBox,
    QStyledItemDelegate,
)


class PriorityDelegate(
    QStyledItemDelegate
):

    def createEditor(
        self,
        parent,
        option,
        index,
    ):

        editor = QSpinBox(parent)

        editor.setRange(1, 5)

        return editor

    def setEditorData(
        self,
        editor,
        index,
    ):

        value = index.data(
            Qt.ItemDataRole.EditRole
        )

        editor.setValue(value)

    def setModelData(
        self,
        editor,
        model,
        index,
    ):

        value = editor.value()

        model.setData(
            index,
            value,
            Qt.ItemDataRole.EditRole,
        )

    def updateEditorGeometry(
        self,
        editor,
        option,
        index,
    ):

        editor.setGeometry(
            option.rect
        )
```

Đây là một Delegate chuẩn để học.

---

# 19. Gắn Delegate

Giả sử:

```text
column 0 = Title
column 1 = Priority
```

Ta:

```python
delegate = PriorityDelegate()

view.setItemDelegateForColumn(
    1,
    delegate,
)
```

Kết quả:

```text
┌──────────────────┬──────────┐
│ Title            │ Priority │
├──────────────────┼──────────┤
│ Learn Python     │ 1        │
│ Learn PySide6    │ 2        │
│ Learn SQLite     │ 3        │
└──────────────────┴──────────┘
```

Double-click Priority:

```text
QSpinBox
```

Double-click Title:

```text
QLineEdit
```

---

# 20. Delegate + Model Roles

Hãy chú ý flow:

```text
Delegate
    ↓
index.data(EditRole)
    ↓
Model
```

và:

```text
Delegate
    ↓
model.setData(
    index,
    value,
    EditRole
)
    ↓
Model
```

Do đó Buổi 19:

```text
DisplayRole
EditRole
UserRole
```

không phải kiến thức độc lập.

Nó được sử dụng trực tiếp trong Delegate.

---

# 21. `QComboBox` Delegate

Một ví dụ rất thực tế.

Todo có:

```text
status
```

với:

```text
Todo
Doing
Done
```

Thay vì cho user gõ:

```text
Todo
Doing
Done
```

ta dùng:

```text
QComboBox
```

---

# 22. `StatusDelegate`

```python
from PySide6.QtWidgets import (
    QComboBox,
    QStyledItemDelegate,
)


class StatusDelegate(
    QStyledItemDelegate
):

    STATUSES = [
        "Todo",
        "Doing",
        "Done",
    ]

    def createEditor(
        self,
        parent,
        option,
        index,
    ):

        editor = QComboBox(parent)

        editor.addItems(
            self.STATUSES
        )

        return editor
```

---

# 23. `setEditorData()`

```python
def setEditorData(
    self,
    editor,
    index,
):

    value = index.data(
        Qt.ItemDataRole.EditRole
    )

    position = editor.findText(value)

    if position >= 0:
        editor.setCurrentIndex(
            position
        )
```

---

# 24. `setModelData()`

```python
def setModelData(
    self,
    editor,
    model,
    index,
):

    value = editor.currentText()

    model.setData(
        index,
        value,
        Qt.ItemDataRole.EditRole,
    )
```

Kết quả:

```text
Status
┌─────────┐
│ Doing ▼ │
└─────────┘
```

---

# 25. Delegate không cần biết Database

Đây là nguyên tắc kiến trúc rất quan trọng.

Sai:

```python
class StatusDelegate:

    def setModelData(...):

        sqlite.update(...)
```

Delegate không nên:

```text
SQLite
Repository
SQL
Business Rule
```

Delegate chỉ:

```text
Editor
  ↓
value
  ↓
Model.setData()
```

---

# 26. Kiến trúc đúng

```text
QComboBox
    ↓
Delegate
    ↓
Model.setData()
    ↓
Application / Domain
    ↓
Repository
    ↓
SQLite
```

Tách trách nhiệm:

```text
Delegate
    → UI editing

Model
    → Presentation data

Application
    → Use case

Repository
    → Persistence
```

Đây là cách bạn có thể kết hợp Model/View với Clean Architecture mà chúng ta đã học.

---

# 27. Delegate và `QCheckBox`

Todo:

```text
☐ Learn Python
☑ Learn PySide6
```

Có hai cách.

### Cách 1

Dùng:

```python
CheckStateRole
```

và:

```python
ItemIsUserCheckable
```

Qt tự xử lý checkbox.

Đây thường là cách đơn giản nhất.

### Cách 2

Tạo custom Delegate vẽ checkbox/editor.

Chỉ nên làm khi bạn cần behavior hoặc giao diện đặc biệt.

---

# 28. Delegate không nhất thiết phải có Editor

Ví dụ:

```text
Priority
```

muốn hiển thị:

```text
★★★☆☆
```

nhưng khi edit:

```text
QSpinBox
```

Bạn có thể:

```text
paint()
    ↓
★★★☆☆

createEditor()
    ↓
QSpinBox
```

Đây là một pattern cực kỳ mạnh.

---

# 29. Custom `paint()`

Ví dụ Priority:

```text
1 → ★☆☆☆☆
2 → ★★☆☆☆
3 → ★★★☆☆
4 → ★★★★☆
5 → ★★★★★
```

Delegate có thể lấy:

```python
priority = index.data(
    Qt.ItemDataRole.DisplayRole
)
```

sau đó vẽ:

```python
text = "★" * priority
```

---

# 30. Ví dụ `paint()`

```python
def paint(
    self,
    painter,
    option,
    index,
):

    priority = index.data(
        Qt.ItemDataRole.DisplayRole
    )

    text = "★" * priority

    painter.drawText(
        option.rect,
        Qt.AlignmentFlag.AlignCenter,
        text,
    )
```

Nhưng có một vấn đề:

> Chúng ta đã bỏ qua selected/hover/focus/style của Qt.

Vì vậy custom paint thực tế cần cẩn thận hơn.

---

# 31. Vì vậy hãy nhớ

Nếu chỉ cần:

```text
custom editor
```

→ không override `paint()`.

Nếu cần:

```text
custom visual rendering
```

→ override `paint()`.

Đây là cách giữ Delegate đơn giản.

---

# 32. `option.state`

Trong `paint()`:

```python
option.state
```

có thể cho biết trạng thái item:

```text
selected
enabled
active
focused
mouse over
```

Bạn có thể kiểm tra:

```python
from PySide6.QtWidgets import QStyle

if option.state & QStyle.StateFlag.State_Selected:
    ...
```

---

# 33. Đừng quên style của Qt

Nếu custom paint, một cách tốt là tận dụng:

```python
QApplication.style()
```

hoặc:

```python
option
```

để giữ behavior/style nhất quán với hệ thống.

Không nên biến mỗi Delegate thành một mini painting framework nếu không cần thiết.

---

# 34. `QStyledItemDelegate` vs `QItemDelegate`

Bạn có thể gặp:

```python
QItemDelegate
```

trong tutorial cũ.

Hiện tại, hãy ưu tiên:

```python
QStyledItemDelegate
```

vì nó tích hợp tốt hơn với Qt Style.

---

# 35. Delegate cho từng column

Đây là pattern rất hay:

```text
Column 0
Title
→ default delegate

Column 1
Priority
→ PriorityDelegate

Column 2
Status
→ StatusDelegate

Column 3
Completed
→ CheckStateRole
```

Code:

```python
view.setItemDelegateForColumn(
    1,
    PriorityDelegate(),
)

view.setItemDelegateForColumn(
    2,
    StatusDelegate(),
)
```

---

# 36. Delegate cho từng item

Không chỉ column.

Có thể:

```python
view.setItemDelegateForRow(
    row,
    delegate,
)
```

Tuy nhiên trong ứng dụng thực tế, `setItemDelegateForColumn()` thường dễ quản lý hơn.

---

# 37. Delegate cho toàn View

```python
view.setItemDelegate(
    delegate
)
```

Áp dụng cho toàn bộ item.

Ví dụ:

```text
QTreeView
    ↓
FileDelegate
```

mọi node đều dùng Delegate.

---

# 38. Delegate + TreeView

Ví dụ File Explorer:

```text
📁 Python
📄 main.py
📄 model.py
```

Bạn có thể dùng Delegate để:

```text
paint()
    ↓
icon + filename

createEditor()
    ↓
QLineEdit
```

Khi rename:

```text
main.py
   ↓ double-click
QLineEdit
   ↓
main_new.py
```

→

```python
model.setData(
    index,
    "main_new.py",
    Qt.ItemDataRole.EditRole,
)
```

---

# 39. Delegate + Story App

Ví dụ:

```text
Story                  Status
──────────────────────────────
Harry Potter           Reading
Lord of Rings          Completed
Dune                   Reading
```

Status Delegate:

```text
Reading
Completed
Paused
```

Editor:

```text
QComboBox
```

Đây là một ví dụ rất gần với app truyện bạn đang xây dựng.

---

# 40. Delegate + Clean Architecture

Một kiến trúc tốt:

```text
                    PySide6
                       │
            ┌──────────┴──────────┐
            ↓                     ↓
          View                 Delegate
            │                     │
            └──────────┬──────────┘
                       ↓
                      Model
                       ↓
                Application Service
                       ↓
                    Domain
                       ↓
                  Repository
                       ↓
                    SQLite
```

Delegate không chạm:

```text
Domain
Database
Repository
```

trực tiếp.

---

# 41. Flow chỉnh sửa hoàn chỉnh

Hãy nhớ flow này:

```text
User
 │
 │ double-click
 ▼
QTableView
 │
 ▼
Delegate.createEditor()
 │
 ▼
QSpinBox
 │
 ▼
Delegate.setEditorData()
 │
 ▼
User changes value
 │
 ▼
Delegate.setModelData()
 │
 ▼
Model.setData()
 │
 ▼
Domain/Application
 │
 ▼
dataChanged
 │
 ▼
QTableView
```

Đây là **editing pipeline** của Model/View.

---

# 42. `commitData`

Trong một số custom editor, Delegate có thể chủ động thông báo:

```python
self.commitData.emit(editor)
```

và:

```python
self.closeEditor.emit(editor)
```

Ví dụ sau khi một action hoàn thành:

```python
editor.currentIndexChanged.connect(...)
```

có thể commit và đóng editor.

Đây là phần nâng cao; hiện tại chỉ cần biết nó tồn tại.

---

# 43. `closeEditor`

Một số editor như:

```text
QComboBox
```

có thể muốn đóng ngay sau khi chọn.

Flow:

```text
User chọn item
       ↓
commitData
       ↓
closeEditor
```

---

# 44. Editor là widget tạm thời

Một điều rất quan trọng:

```text
QLineEdit
QSpinBox
QComboBox
```

do Delegate tạo ra **không phải widget permanent của table**.

Nó thường chỉ xuất hiện khi user đang edit.

Ví dụ:

```text
Normal:

Learn PySide6 | 3


Double click:

Learn PySide6 | [ 3 ▲▼ ]


Finish:

Learn PySide6 | 3
```

Editor xuất hiện và biến mất theo editing lifecycle.

---

# 45. Đây là lý do không nên tạo hàng trăm widget

Không nên nghĩ:

```text
1000 rows
    ↓
1000 QLineEdit
```

Qt Delegate thiết kế để:

```text
1000 rows
    ↓
vẽ bằng Delegate

chỉ khi edit
    ↓
tạo editor
```

Đây là một trong những lý do Model/View có khả năng xử lý lượng dữ liệu lớn tốt hơn kiểu:

```text
QWidget cho từng item
```

---

# 46. Bài tập 1 — Priority Delegate

Tạo:

```text
Todo
├── title
└── priority
```

UI:

```text
Title             Priority
────────────────────────────
Learn Python      1
Learn PySide6     3
Learn SQLite      5
```

Double-click Priority:

```text
QSpinBox
```

Range:

```text
1 → 5
```

---

# 47. Bài tập 2 — Status Delegate

Status:

```text
Todo
Doing
Done
```

Double-click:

```text
QComboBox
```

Kết quả:

```text
┌────────────┐
│ Doing   ▼  │
└────────────┘
```

---

# 48. Bài tập 3 — Star Delegate

Priority:

```text
1
2
3
4
5
```

Hiển thị:

```text
★
★★
★★★
★★★★
★★★★★
```

Nhưng khi edit:

```text
QSpinBox
```

Bạn sẽ phải kết hợp:

```text
paint()
createEditor()
setEditorData()
setModelData()
```

Đây là bài tập rất tốt.

---

# 49. Bài tập 4 — File Rename

Tạo:

```text
QTreeView
```

với:

```text
Project
├── main.py
├── model.py
└── README.md
```

Double-click:

```text
main.py
```

→ `QLineEdit`.

Sau khi sửa:

```text
main.py
```

thành:

```text
app.py
```

Model nhận:

```python
EditRole
```

---

# 50. Bài tập 5 — Story Manager

Tạo:

```text
Story
├── title
├── author
└── status
```

Status:

```text
Reading
Paused
Completed
```

Dùng:

```text
QTreeView
      ↓
StoryModel
      ↓
StatusDelegate
      ↓
QComboBox
```

Đây là bài tập rất phù hợp với project đọc truyện.

---

# 51. Những lỗi thường gặp

## Lỗi 1

Không implement `setData()` trong Model nhưng Delegate gọi:

```python
model.setData(...)
```

Kết quả:

```text
edit không lưu
```

---

## Lỗi 2

Quên:

```python
flags()
```

Không cho phép:

```text
ItemIsEditable
```

thì editor có thể không xuất hiện.

Ví dụ:

```python
def flags(self, index):

    return (
        Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsSelectable
        | Qt.ItemFlag.ItemIsEditable
    )
```

---

# 52. Lỗi 3 — Delegate sửa Database trực tiếp

Sai:

```text
Delegate
   ↓
sqlite3
```

Đúng:

```text
Delegate
   ↓
Model
   ↓
Application
   ↓
Repository
```

---

# 53. Lỗi 4 — Tạo editor trong `paint()`

Không nên:

```python
def paint(...):

    editor = QLineEdit()
```

`paint()` có thể được gọi rất nhiều lần.

Editor phải được tạo trong:

```python
createEditor()
```

---

# 54. Lỗi 5 — Quên `option.rect`

Editor:

```python
editor.setGeometry(
    option.rect
)
```

Nếu không, editor có thể:

```text
sai vị trí
sai kích thước
```

---

# 55. Tổng kết kiến trúc

Đến đây bạn đã có:

```text
Buổi 11
Model/View
    ↓
architecture

Buổi 15-17
Model
    ↓
data structure

Buổi 18
QModelIndex
    ↓
item identity/location

Buổi 19
Roles
    ↓
data meaning

Buổi 20
Delegate
    ↓
render + editing
```

Đây là nền móng rất quan trọng.

---

# 56. Mental Model cuối Buổi 20

Hãy ghi nhớ sơ đồ này:

```text
                         QTableView
                             │
             ┌───────────────┴───────────────┐
             │                               │
             ▼                               ▼
          Model                           Delegate
             │                               │
             │ data(index, role)             │
             │◄──────────────────────────────┤
             │                               │
             │                               │ paint()
             │                               │ createEditor()
             │                               │ setEditorData()
             │                               │ setModelData()
             │                               │
             ▼                               ▼
          Domain                         Editor Widget
       Todo / Story                  QLineEdit / QSpinBox
```

Và editing:

```text
        User
         │
         ▼
  double-click
         │
         ▼
createEditor()
         │
         ▼
    QComboBox
         │
         ▼
setEditorData()
         │
      editing
         │
         ▼
setModelData()
         │
         ▼
 model.setData()
         │
         ▼
   dataChanged
         │
         ▼
      View
```

### 🎯 Bài tập chính

Xây một `TodoTableModel`:

```text
┌──────────────────┬──────────┬─────────────┐
│ Title            │ Priority │ Status      │
├──────────────────┼──────────┼─────────────┤
│ Learn Python     │    1     │ Todo        │
│ Learn PySide6    │    3     │ Doing       │
│ Learn SQLite     │    5     │ Done        │
└──────────────────┴──────────┴─────────────┘
```

Yêu cầu:

```text
Title
 → QLineEdit

Priority
 → QSpinBox (1-5)

Status
 → QComboBox

ID
 → UserRole
```

Mục tiêu cuối cùng là hiểu được pipeline:

```text
Model
  ↓
Role
  ↓
QModelIndex
  ↓
Delegate
  ↓
Editor
  ↓
Model.setData()
```

**Buổi 21 — Sorting & Filtering** sẽ giải quyết một vấn đề thực tế hơn nữa: khi có **10.000 Todo**, làm sao tìm kiếm, lọc theo Status/Priority và sắp xếp mà **không sửa trực tiếp dữ liệu gốc**. Đây là bước chuẩn bị trực tiếp cho `QSortFilterProxyModel` ở Buổi 22.
