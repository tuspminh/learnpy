# Buổi 5 - Auto Save với QTimer (Debounce)

Đây là buổi quan trọng nhất của toàn bộ dự án.

Sau buổi này, ứng dụng sẽ hoạt động giống các phần mềm ghi chú hiện đại như:

- Notion
- Obsidian
- Apple Notes
- Google Keep

Bạn **không cần bấm nút Save**.

Chỉ cần gõ là chương trình sẽ tự lưu.

---

# Tại sao không lưu ngay khi gõ?

Giả sử người dùng gõ:

```text-x-trilium-auto
Python MVC
```

Mỗi ký tự sẽ phát sinh một signal.

```text-x-trilium-auto
P

↓

Py

↓

Pyt

↓

Pyth

↓

Pytho

↓

Python
```

Nếu mỗi lần đều:

```text-x-trilium-auto
model.update(...)
```

thì SQLite sẽ ghi:

```text-x-trilium-auto
UPDATE

UPDATE

UPDATE

UPDATE

UPDATE

UPDATE
```

Có thể hàng trăm lần trong vài giây.

Không hiệu quả.

---

# Giải pháp: Debounce

Thay vì lưu ngay.

```text-x-trilium-auto
Người dùng gõ

↓

Đợi 800 ms

↓

Không còn gõ

↓

Mới lưu
```

Đây gọi là **Debounce**.

Qt hỗ trợ rất tốt bằng `QTimer`.

---

# Luồng Auto Save

```text-x-trilium-auto
User

↓

QTextEdit

↓

textChanged

↓

Controller

↓

QTimer.start()

↓

800 ms

↓

save_note()

↓

SQLite
```

---

# Bước 1 - Tạo QTimer

Trong `note_controller.py`

```text-x-trilium-auto
from PySide6.QtCore import QTimer
```

Trong `__init__()`:

```text-x-trilium-auto
self.save_timer = QTimer()

self.save_timer.setSingleShot(True)

self.save_timer.timeout.connect(
    self.save_current_note
)
```

---

## Single Shot là gì?

Nếu:

```text-x-trilium-auto
setSingleShot(False)
```

Timer sẽ chạy mãi:

```text-x-trilium-auto
1 giây

↓

1 giây

↓

1 giây

↓

...
```

Không cần.

Ta chỉ muốn:

```text-x-trilium-auto
Start

↓

800 ms

↓

Timeout

↓

Stop
```

---

# Bước 2 - Kết nối tín hiệu

Trong `connect_signals()`

```text-x-trilium-auto
right = self.view.right_panel

right.title_edit.textChanged.connect(
    self.note_changed
)

right.content_edit.textChanged.connect(
    self.note_changed
)
```

---

# Luồng

```text-x-trilium-auto
QLineEdit

↓

textChanged

↓

Controller
```

---

# Bước 3 - note_changed()

```text-x-trilium-auto
def note_changed(self):

    if self.current_note is None:
        return

    self.save_timer.start(800)
```

---

Điều gì xảy ra?

Người dùng gõ

```text-x-trilium-auto
P
```

↓

Timer

```text-x-trilium-auto
800 ms
```

Người dùng tiếp tục

```text-x-trilium-auto
Py
```

↓

Timer reset

```text-x-trilium-auto
800 ms
```

Tiếp tục

```text-x-trilium-auto
Python
```

↓

Reset

↓

Ngừng gõ

↓

800 ms

↓

Lưu

---

# Hình minh họa

```text-x-trilium-auto
P

↓

Timer

↓

Py

↓

Reset

↓

Pyt

↓

Reset

↓

Python

↓

Reset

↓

800ms

↓

Save
```

---

# Bước 4 - save_current_note()

```text-x-trilium-auto
def save_current_note(self):

    if self.current_note is None:
        return

    right = self.view.right_panel

    self.current_note.title = right.title_edit.text()

    self.current_note.content = (
        right.content_edit.toPlainText()
    )

    self.model.update(self.current_note)

    self.refresh_current_item()
```

---

Luồng

```text-x-trilium-auto
QTextEdit

↓

Controller

↓

current_note

↓

Model

↓

SQLite
```

---

# Tại sao phải cập nhật current_note?

Hiện tại trong RAM

```text-x-trilium-auto
Title

Python
```

Nếu không:

```text-x-trilium-auto
current_note.title
```

vẫn là

```text-x-trilium-auto
Old Title
```

Ta phải đồng bộ object trước.

---

# Bước 5 - Refresh QListWidget

Nếu đổi tiêu đề

```text-x-trilium-auto
New Note
```

thành

```text-x-trilium-auto
Python
```

Danh sách bên trái vẫn hiển thị:

```text-x-trilium-auto
New Note
```

Sai.

---

Ta viết:

```text-x-trilium-auto
def refresh_current_item(self):

    list_widget = self.view.left_panel.note_list

    item = list_widget.currentItem()

    if item is None:
        return

    item.setText(
        self.current_note.title
    )
```

---

Giờ khi sửa

```text-x-trilium-auto
Python MVC
```

Danh sách cũng đổi ngay.

---

# Vấn đề lớn đầu tiên

Có một lỗi rất nhiều người gặp.

Khi click ghi chú

```text-x-trilium-auto
show_note()
```

thực hiện

```text-x-trilium-auto
title_edit.setText(...)
```

Qt sẽ phát sinh:

```text-x-trilium-auto
textChanged
```

↓

Auto Save

↓

SQLite

Mặc dù người dùng chưa sửa gì.

---

# Giải pháp: blockSignals()

Trong `RightPanel`

```text-x-trilium-auto
def show_note(self, note):

    self.title_edit.blockSignals(True)

    self.content_edit.blockSignals(True)

    self.title_edit.setText(note.title)

    self.content_edit.setPlainText(
        note.content
    )

    self.title_edit.blockSignals(False)

    self.content_edit.blockSignals(False)
```

---

Đây là kỹ thuật cực kỳ quan trọng.

Không chỉ PySide6.

Mà Qt C++ cũng dùng.

---

# Hiển thị trạng thái

Trong `note_changed()`

```text-x-trilium-auto
self.view.statusBar().showMessage(
    "Editing..."
)
```

Sau khi lưu

```text-x-trilium-auto
self.view.statusBar().showMessage(
    "Saved"
)
```

Trải nghiệm sẽ giống:

```text-x-trilium-auto
Editing...

↓

Saved
```

---

# Thêm thời gian lưu

Trong `save_current_note()`

```text-x-trilium-auto
from datetime import datetime
```

```text-x-trilium-auto
time = datetime.now().strftime(
    "%H:%M:%S"
)

self.view.statusBar().showMessage(

    f"Saved at {time}"

)
```

Ví dụ

```text-x-trilium-auto
Saved at 15:42:30
```

---

# Luồng hoàn chỉnh

```text-x-trilium-auto
User

↓

QTextEdit

↓

textChanged

↓

Controller

↓

Timer.start()

↓

800 ms

↓

save_current_note()

↓

Model.update()

↓

SQLite

↓

Refresh QListWidget

↓

StatusBar
```

---

# Những lỗi thường gặp

## Lỗi 1

Lưu sau mỗi ký tự

```text-x-trilium-auto
P

↓

UPDATE
```

Không nên.

---

## Lỗi 2

Không dùng blockSignals()

↓

Mỗi lần mở note

↓

Auto Save

↓

Database ghi liên tục.

---

## Lỗi 3

Quên cập nhật current_note

↓

SQLite lưu

↓

RAM vẫn dữ liệu cũ.

---

## Lỗi 4

Đổi title

↓

ListWidget không refresh.

---

# Kiến thức mới học được

Hôm nay bạn đã học được rất nhiều kỹ thuật quan trọng:

- `QTimer` để trì hoãn thao tác (debounce).
- `setSingleShot(True)` để tạo timer chạy một lần.
- `textChanged` của `QLineEdit` và `QTextEdit`.
- `blockSignals(True/False)` để tránh vòng lặp tín hiệu.
- Đồng bộ dữ liệu giữa giao diện (`View`) và đối tượng `Note` trong bộ nhớ.
- Cập nhật giao diện sau khi lưu mà không cần tải lại toàn bộ danh sách.

Đây đều là những kỹ thuật được sử dụng trong các ứng dụng PySide6 chuyên nghiệp.

---

# Bài tập thực hành

1. Thay thời gian debounce từ **800 ms** thành **500 ms** và cảm nhận sự khác biệt.
2. Nếu tiêu đề để trống, tự động đổi thành `"Untitled"` trước khi lưu.
3. Khi người dùng chỉnh sửa nhưng chưa lưu, hiển thị trên `StatusBar`:

```text-x-trilium-auto
● Unsaved changes
```

Sau khi lưu xong, đổi thành:

```text-x-trilium-auto
✓ Saved
```

4. Nếu người dùng chỉ thay đổi khoảng trắng ở cuối tiêu đề (`"Python "`), hãy dùng `strip()` để tránh lưu tiêu đề không cần thiết.

---

# Buổi 6 (Preview)

Ở buổi tiếp theo, chúng ta sẽ hoàn thiện các chức năng quản lý ghi chú:

- Xóa ghi chú với hộp thoại xác nhận (`QMessageBox`).
- Tự động chọn ghi chú kế tiếp sau khi xóa.
- Thêm thanh tìm kiếm để lọc ghi chú theo tiêu đề.
- Sắp xếp ghi chú theo `updated_at`.
- Cập nhật số lượng ghi chú trên giao diện.

Đến hết buổi 6, ứng dụng sẽ có đầy đủ các chức năng cơ bản của một **ứng dụng ghi chú hoàn chỉnh** theo mô hình **MVC**, sẵn sàng để tiếp tục nâng cấp với Markdown, Tag, Export PDF và nhiều tính năng nâng cao khác.
