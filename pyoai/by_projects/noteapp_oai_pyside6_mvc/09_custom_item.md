# Buổi 9 - `QStyledItemDelegate` và `QPainter` (Custom Item)

> Đây là một trong những chủ đề "đỉnh cao" của Qt.

Sau buổi này bạn sẽ hiểu vì sao:

- Qt Creator
- Visual Studio Code (phiên bản Qt)
- Telegram Desktop
- KDE Dolphin
- Autodesk Maya

đều có những danh sách (List) rất đẹp mà **không dùng QWidget cho từng dòng**.

---

# Mục tiêu

Hiện tại danh sách của chúng ta là:

```text-x-trilium-auto
Python
SQLite
Docker
MVC
```

Sau buổi này sẽ thành:

```text-x-trilium-auto
┌────────────────────────────────────┐
📄 Python
Học kiến trúc MVC với PySide6...
09/07/2026 21:30
─────────────────────────────────────
📄 Docker
Docker Compose + SQLite
08/07/2026 14:20
└────────────────────────────────────┘
```

Giống ứng dụng ghi chú thật.

---

# Tại sao không dùng QWidget?

Nhiều người mới nghĩ:

```text-x-trilium-auto
QListWidget

↓

QWidget

↓

QLabel

↓

QLabel

↓

QLabel
```

Mỗi item là một QWidget.

Được không?

Được.

Có nên không?

Không.

---

## Ví dụ

10000 ghi chú.

Nếu mỗi ghi chú là

```text-x-trilium-auto
QWidget

↓

3 QLabel

↓

1 Layout
```

Tổng cộng

```text-x-trilium-auto
10000 QWidget

30000 QLabel

10000 Layout
```

RAM tăng rất lớn.

CPU cũng tăng.

---

# Qt giải quyết thế nào?

Qt không tạo Widget.

Qt chỉ:

```text-x-trilium-auto
QPainter

↓

Vẽ
```

Giống như Photoshop.

Không tạo 10000 QLabel.

Chỉ vẽ.

Đây là lý do Qt cực nhanh.

---

# Kiến trúc

```text-x-trilium-auto
QListView

↓

Delegate

↓

QPainter

↓

Màn hình
```

---

# Delegate là gì?

Delegate giống như "họa sĩ".

Qt hỏi:

```text-x-trilium-auto
Item số 5

Vẽ thế nào?
```

Delegate trả lời.

---

# Tạo Delegate

Tạo file

```text-x-trilium-auto
view/note_delegate.py
```

Import

```text-x-trilium-auto
from PySide6.QtWidgets import QStyledItemDelegate from PySide6.QtGui import QPainter
```

---

```text-x-trilium-auto
class NoteDelegate(QStyledItemDelegate):

    pass
```

---

# Hai hàm quan trọng

```text-x-trilium-auto
paint()

sizeHint()
```

Chỉ hai hàm.

---

# sizeHint()

Qt hỏi

```text-x-trilium-auto
Một item cao bao nhiêu?
```

Ví dụ

```text-x-trilium-auto
from PySide6.QtCore import QSize

def sizeHint(self, option, index):

    return QSize(0,80)
```

Kết quả

```text-x-trilium-auto
Python

----------------
```

Mỗi item cao

```text-x-trilium-auto
80 pixel
```

---

# paint()

Đây là trái tim.

Qt gọi

```text-x-trilium-auto
paint()

↓

paint()

↓

paint()

↓

paint()
```

cho từng item.

---

Ví dụ

```text-x-trilium-auto
def paint(self, painter, option, index):

    title = index.data()

    painter.drawText(
        option.rect,
        title
    )
```

Qt sẽ tự vẽ.

---

# index.data()

Chính là

```text-x-trilium-auto
Qt.DisplayRole
```

trong

```text-x-trilium-auto
NoteListModel.data()
```

---

# Nhưng chúng ta muốn nhiều thông tin

Ví dụ

```text-x-trilium-auto
Title

Preview

Date
```

Không chỉ title.

---

# Thêm Role

Trong

```text-x-trilium-auto
NoteListModel
```

Ta thêm

```text-x-trilium-auto
TITLE_ROLE = Qt.UserRole + 1

CONTENT_ROLE = Qt.UserRole + 2

DATE_ROLE = Qt.UserRole + 3
```

---

Trong

```text-x-trilium-auto
data()
```

```text-x-trilium-auto
if role == TITLE_ROLE:

    return note.title

if role == CONTENT_ROLE:

    return note.content

if role == DATE_ROLE:

    return note.updated_at
```

---

Bây giờ Delegate lấy

```text-x-trilium-auto
title = index.data(TITLE_ROLE)

content = index.data(CONTENT_ROLE)

date = index.data(DATE_ROLE)
```

---

# QPainter

QPainter giống như cây bút.

Có thể:

```text-x-trilium-auto
Vẽ chữ

↓

Vẽ hình

↓

Vẽ icon

↓

Vẽ ảnh

↓

Vẽ đường
```

---

Ví dụ

```text-x-trilium-auto
painter.drawText(...)
```

---

Hoặc

```text-x-trilium-auto
painter.drawLine(...)
```

---

Hoặc

```text-x-trilium-auto
painter.drawRect(...)
```

---

# Vẽ Title

```text-x-trilium-auto
title_rect = option.rect.adjusted(
    10,
    8,
    -10,
    -40
)

painter.drawText(
    title_rect,
    title
)
```

---

# Vẽ Preview

```text-x-trilium-auto
preview_rect = option.rect.adjusted(
    10,
    30,
    -10,
    -20
)

painter.drawText(
    preview_rect,
    content[:50]
)
```

---

# Vẽ Date

```text-x-trilium-auto
date_rect = option.rect.adjusted(
    10,
    55,
    -10,
    -5
)

painter.drawText(
    date_rect,
    date
)
```

---

# Kết quả

```text-x-trilium-auto
Python

Học PySide6 MVC...

09/07/2026
```

---

# Đổi Font

```text-x-trilium-auto
font = painter.font()

font.setPointSize(12)

font.setBold(True)

painter.setFont(font)
```

↓

Title to hơn.

---

Preview

```text-x-trilium-auto
font.setBold(False)

font.setPointSize(9)
```

↓

Nhỏ hơn.

---

# Đổi màu

```text-x-trilium-auto
from PySide6.QtGui import QColor
```

```text-x-trilium-auto
painter.setPen(

    QColor("#404040")

)
```

Preview sẽ xám.

---

Date

```text-x-trilium-auto
QColor("#888888")
```

---

# Item được chọn

Qt cho biết

```text-x-trilium-auto
option.state
```

Ví dụ

```text-x-trilium-auto
from PySide6.QtWidgets import QStyle
```

```text-x-trilium-auto
if option.state & QStyle.State_Selected:
```

↓

Item đang chọn.

---

Vẽ nền

```text-x-trilium-auto
painter.fillRect(

    option.rect,

    QColor("#DCEEFF")

)
```

---

Không chọn

↓

Trắng.

---

# Hover

```text-x-trilium-auto
QStyle.State_MouseOver
```

Có thể đổi nền.

Giống VS Code.

---

# Separator

Vẽ đường

```text-x-trilium-auto
painter.drawLine(

    option.rect.bottomLeft(),

    option.rect.bottomRight()

)
```

↓

Có đường ngăn.

---

# Icon

Có thể

```text-x-trilium-auto
QIcon
```

hoặc

```text-x-trilium-auto
QPixmap
```

```text-x-trilium-auto
icon.paint(...)
```

↓

📄

---

# Hiệu năng

10000 item

↓

Qt gọi

```text-x-trilium-auto
paint()

↓

Chỉ

30 item
```

đang nhìn thấy.

Scroll

↓

Vẽ tiếp.

Rất nhanh.

---

# Kết nối Delegate

Trong

```text-x-trilium-auto
LeftPanel
```

```text-x-trilium-auto
delegate = NoteDelegate()

self.note_list.setItemDelegate(delegate)
```

Xong.

Không cần sửa Controller.

Không cần sửa SQLite.

---

# Điều rất hay

Bạn thay đổi toàn bộ giao diện.

Nhưng

```text-x-trilium-auto
Controller

Không đổi

Repository

Không đổi

Service

Không đổi

SQLite

Không đổi
```

Đó chính là lợi ích của MVC.

---

# Kiến thức mới học được

Hôm nay bạn đã tiếp cận một phần rất mạnh của Qt:

## 1. `QStyledItemDelegate`

Delegate chịu trách nhiệm **vẽ từng item** trong `QListView`. Nó thay thế việc tạo hàng nghìn `QWidget`, giúp ứng dụng nhẹ và nhanh hơn.

---

## 2. `QPainter`

`QPainter` là công cụ vẽ của Qt. Bạn có thể dùng nó để:

- Vẽ văn bản (`drawText`)
- Vẽ đường (`drawLine`)
- Vẽ hình chữ nhật (`drawRect`)
- Vẽ ảnh (`drawPixmap`)
- Tô nền (`fillRect`)

Hầu hết giao diện tùy biến trong Qt đều dựa trên `QPainter`.

---

## 3. Custom Roles

Thay vì chỉ trả về tiêu đề qua `Qt.DisplayRole`, bạn có thể định nghĩa các role riêng như:

- `TITLE_ROLE`
- `CONTENT_ROLE`
- `DATE_ROLE`

Delegate sẽ lấy đúng dữ liệu cần để hiển thị.

---

## 4. Tách biệt dữ liệu và giao diện

Điểm quan trọng nhất là:

- **Model** cung cấp dữ liệu.
- **Delegate** quyết định cách hiển thị.
- **View** chỉ quản lý việc hiển thị và lựa chọn.

Nhờ vậy, bạn có thể thay đổi toàn bộ giao diện danh sách mà không cần sửa `Controller`, `Service`, `Repository` hay `Database`.

---

# Bài tập thực hành

1. Hiển thị **3 dòng** trong mỗi item:
  - Tiêu đề (in đậm).
  - 50 ký tự đầu của nội dung.
  - Ngày cập nhật (`updated_at`).
2. Nếu nội dung dài hơn 50 ký tự, thêm `"..."` ở cuối.
3. Đổi màu nền của item khi rê chuột (`State_MouseOver`).
4. Nếu ghi chú được ghim (`is_pinned = 1`), hiển thị biểu tượng 📌 ở góc phải của item (gợi ý: thêm một `PINNED_ROLE` trong `NoteListModel`).

---

# Buổi 10 (Bước sang ứng dụng chuyên nghiệp)

Ở buổi tiếp theo, chúng ta sẽ hoàn thiện trải nghiệm người dùng:

- Xây dựng **MenuBar** và **QAction** chuẩn.
- Thêm phím tắt (`Ctrl+N`, `Ctrl+S`, `Delete`, `Ctrl+F`...).
- Tạo **Context Menu** khi nhấp chuột phải vào ghi chú.
- Quản lý **Undo/Redo** với `QUndoStack`.
- Tổ chức mã nguồn theo hướng dễ mở rộng và chuẩn bị cho các tính năng lớn như **Markdown**, **Notebook**, **Tag** và **Export PDF**.

Đến hết buổi 10, ứng dụng sẽ có nền tảng kiến trúc và giao diện tương đương với nhiều ứng dụng desktop chuyên nghiệp viết bằng PySide6.
