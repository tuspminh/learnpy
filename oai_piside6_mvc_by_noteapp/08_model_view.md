# Buổi 8 - Qt Model/View Framework với `QAbstractListModel`

> Đây là một trong những buổi quan trọng nhất của PySide6.

Đến đây chúng ta sẽ **bỏ** `**QListWidget**`.

Đây là điều mà rất nhiều người mới học PySide6 không hiểu.

Họ nghĩ:

```text-x-trilium-auto
QListWidget
```

là chuẩn.

Thực tế:

**QListWidget chỉ phù hợp cho ứng dụng nhỏ.**

Các phần mềm lớn đều dùng:

- Qt Creator
- Autodesk Maya
- VLC
- KDE Dolphin
- Qt Designer

đều sử dụng **Qt Model/View Framework**.

---

# Mục tiêu buổi học

Sau buổi này, bạn sẽ hiểu:

- Qt Model/View là gì
- Vì sao `QListWidget` không mở rộng tốt
- `QListView`
- `QAbstractListModel`
- Qt Roles
- MVC của Qt khác MVC của chúng ta như thế nào
- Viết Custom Model đầu tiên

---

# Hai loại Widget trong Qt

Qt có hai cách làm.

## Cách 1

Widget-Based

```text-x-trilium-auto
QListWidget

QTreeWidget

QTableWidget
```

Đây là cách dễ.

---

## Cách 2

Model/View

```text-x-trilium-auto
QListView

QTreeView

QTableView
```

Khó hơn.

Nhưng mạnh hơn rất nhiều.

---

# So sánh

## QListWidget

```text-x-trilium-auto
listWidget.addItem("Python")
```

Đơn giản.

---

## QListView

Không có

```text-x-trilium-auto
addItem()
```

Mà là

```text-x-trilium-auto
QListView

↓

Model

↓

Data
```

---

# Mô hình mới

```text-x-trilium-auto
          QListView

               ▲

               │

       QAbstractListModel

               ▲

               │

        List<Note>
```

View không chứa dữ liệu.

Model mới chứa.

Đây là triết lý của Qt.

---

# MVC của chúng ta

```text-x-trilium-auto
Controller

↓

Service

↓

Repository

↓

SQLite
```

---

# MVC của Qt

Qt cũng có MVC.

```text-x-trilium-auto
View

↓

Qt Model

↓

Data
```

Hai cái này **không xung đột**.

Thực tế:

```text-x-trilium-auto
PySide MVC

↓

View

↓

Qt Model

↓

Repository

↓

SQLite
```

---

# Dữ liệu

Giả sử có

```text-x-trilium-auto
Python

SQLite

Docker

MVC
```

Trong RAM.

```text-x-trilium-auto
notes = [

    Note(...),

    Note(...),

    Note(...)

]
```

QListView không biết.

Model sẽ trả lời.

---

# Tạo Model

Tạo file

```text-x-trilium-auto
view/note_list_model.py
```

---

Import

```text-x-trilium-auto
from PySide6.QtCore import (
    Qt,
    QAbstractListModel,
    QModelIndex
)
```

---

Tạo class

```text-x-trilium-auto
class NoteListModel(QAbstractListModel):

    def __init__(self):

        super().__init__()

        self.notes = []
```

---

# rowCount()

Qt hỏi

```text-x-trilium-auto
Có bao nhiêu dòng?
```

Ta trả lời.

```text-x-trilium-auto
def rowCount(self, parent=QModelIndex()):

    return len(self.notes)
```

---

Ví dụ

```text-x-trilium-auto
notes

↓

5
```

Qt sẽ vẽ

```text-x-trilium-auto
0

1

2

3

4
```

---

# data()

Đây là hàm quan trọng nhất.

Qt hỏi

```text-x-trilium-auto
Dòng số 2

Hiển thị gì?
```

Ta trả lời.

```text-x-trilium-auto
def data(self, index, role):

    if not index.isValid():
        return None

    note = self.notes[index.row()]

    if role == Qt.DisplayRole:

        return note.title

    return None
```

---

# Qt Roles

Qt không chỉ hỏi

```text-x-trilium-auto
Text?
```

Mà còn hỏi

```text-x-trilium-auto
Icon?

Color?

Font?

Tooltip?

Alignment?
```

Đó là Roles.

---

Ví dụ

```text-x-trilium-auto
Qt.DisplayRole
```

↓

Hiển thị

```text-x-trilium-auto
Python
```

---

Sau này

```text-x-trilium-auto
Qt.DecorationRole
```

↓

Icon.

---

# Thêm dữ liệu

Viết

```text-x-trilium-auto
def set_notes(self, notes):

    self.beginResetModel()

    self.notes = notes

    self.endResetModel()
```

---

beginResetModel()

↓

Qt chuẩn bị

↓

Dữ liệu đổi

↓

endResetModel()

↓

Qt vẽ lại.

---

# Thay QListWidget

Trong LeftPanel

Thay

```text-x-trilium-auto
QListWidget
```

thành

```text-x-trilium-auto
QListView
```

---

Khởi tạo

```text-x-trilium-auto
from view.note_list_model import NoteListModel

self.model = NoteListModel()

self.note_list = QListView()

self.note_list.setModel(self.model)
```

---

Giờ dữ liệu sẽ đi như sau

```text-x-trilium-auto
SQLite

↓

Repository

↓

Service

↓

Controller

↓

NoteListModel

↓

QListView
```

---

# Controller

load_notes()

không còn

```text-x-trilium-auto
left.clear()

for note in notes:

    left.add_note(...)
```

Mà chỉ

```text-x-trilium-auto
notes = self.service.get_all()

left.model.set_notes(notes)
```

Chỉ một dòng.

Đẹp hơn rất nhiều.

---

# Chọn item

QListView không dùng

```text-x-trilium-auto
currentItemChanged
```

Mà dùng

```text-x-trilium-auto
selectionModel()
```

```text-x-trilium-auto
self.note_list.selectionModel().currentChanged.connect(
    self.select_note
)
```

---

Lấy dữ liệu

```text-x-trilium-auto
index.row()
```

↓

```text-x-trilium-auto
note = self.model.notes[index.row()]
```

---

# Không cần Qt.UserRole

Trước đây

```text-x-trilium-auto
item.setData(...)
```

Bây giờ

Không cần nữa.

Vì

```text-x-trilium-auto
model.notes
```

đã chứa object.

---

# Hiển thị

Ví dụ

```text-x-trilium-auto
notes

↓

0 Python

1 SQLite

2 Docker
```

Qt gọi

```text-x-trilium-auto
rowCount()

↓

3
```

Sau đó

```text-x-trilium-auto
data(0)

↓

Python
```

```text-x-trilium-auto
data(1)

↓

SQLite
```

```text-x-trilium-auto
data(2)

↓

Docker
```

Qt tự vẽ.

---

# Ưu điểm

Nếu

```text-x-trilium-auto
50000 ghi chú
```

QListWidget

↓

Tạo 50000 Widget.

Rất nặng.

---

QListView

↓

Chỉ vẽ

```text-x-trilium-auto
Những dòng đang nhìn thấy.
```

Ví dụ

```text-x-trilium-auto
0-25
```

Scroll

↓

Qt vẽ tiếp

```text-x-trilium-auto
26-50
```

Rất nhanh.

---

# Chuẩn bị cho Delegate

Hiện tại

```text-x-trilium-auto
Python
```

chỉ có text.

Buổi sau

Ta sẽ hiển thị

```text-x-trilium-auto
Python

15 phút trước

12 dòng
```

Mỗi item đẹp như

Notion.

Đó là Delegate.

---

# Kiến thức mới hôm nay

Bạn đã học một phần rất quan trọng của Qt:

### 1. Widget-Based vs Model/View

| Widget-Based | Model/View |
| --- | --- |
| `QListWidget` | `QListView` |
| `QTableWidget` | `QTableView` |
| `QTreeWidget` | `QTreeView` |

Widget-Based dễ học nhưng ít linh hoạt. Model/View mạnh hơn và phù hợp với dữ liệu lớn.

---

### 2. `QAbstractListModel`

Đây là lớp nền để xây dựng model riêng.

Bạn chỉ cần cài đặt tối thiểu:

- `rowCount()`
- `data()`

là `QListView` đã có thể hiển thị dữ liệu.

---

### 3. Qt Roles

Một dòng trong `QListView` không chỉ có văn bản.

Qt có nhiều "vai trò" (roles):

- `Qt.DisplayRole` → Văn bản
- `Qt.DecorationRole` → Biểu tượng
- `Qt.ToolTipRole` → Tooltip
- `Qt.FontRole` → Phông chữ
- `Qt.ForegroundRole` → Màu chữ
- ...

Nhờ đó một model có thể cung cấp nhiều loại dữ liệu cho cùng một item.

---

### 4. Model không phải View

Đây là điểm rất nhiều người mới nhầm lẫn.

`NoteListModel` **không vẽ giao diện**.

Nó chỉ trả lời các câu hỏi như:

- Có bao nhiêu dòng?
- Dòng số 5 hiển thị gì?
- Dòng số 2 có icon gì?

Chính `QListView` mới là thành phần vẽ giao diện.

---

# Bài tập thực hành

1. Mở rộng `data()` để hỗ trợ `Qt.ToolTipRole`, hiển thị ngày `updated_at` khi rê chuột lên một ghi chú.
2. Nếu tiêu đề ghi chú rỗng, hiển thị `"Untitled"` thay vì chuỗi rỗng.
3. Thêm phương thức `get_note(row)` vào `NoteListModel` để Controller không truy cập trực tiếp `self.notes`.
4. Thử thêm 1.000 ghi chú giả và quan sát hiệu năng của `QListView`.

---

# Buổi 9 (Rất hay)

Ở buổi tiếp theo, chúng ta sẽ học **QStyledItemDelegate** để biến danh sách ghi chú từ:

```text-x-trilium-auto
Python
SQLite
Docker
```

thành giao diện hiện đại hơn:

```text-x-trilium-auto
📄 Python
Học MVC với PySide6
Cập nhật: 09/07/2026 21:30

📄 Docker
Docker Compose và SQLite
Cập nhật: 08/07/2026 15:12
```

Bạn sẽ học:

- `QStyledItemDelegate`
- `paint()`
- `sizeHint()`
- Vẽ bằng `QPainter`
- Hiển thị nhiều dòng, icon và màu sắc trong từng item.

Đây là kỹ thuật được sử dụng trong các ứng dụng Qt chuyên nghiệp để tạo danh sách đẹp và hiệu quả
