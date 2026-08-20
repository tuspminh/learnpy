# Buổi 8 — Dialog trong PySide6

Hôm nay chúng ta học **Dialog**, một thành phần cực kỳ quan trọng trong ứng dụng desktop.

Roadmap:

```text
QDialog
├── Modal / Modeless
├── exec()
├── show()
├── open()
├── accept()
├── reject()
│
├── QMessageBox
├── QInputDialog
├── QFileDialog
│
└── Custom Dialog
```

Mục tiêu cuối buổi: bạn phải hiểu **khi nào dùng dialog, dialog chạy như thế nào, và cách tự xây Custom Dialog**.

---

# 1. Dialog là gì?

Dialog là một cửa sổ dùng để:

* hỏi người dùng
* nhập dữ liệu
* xác nhận hành động
* chọn file
* chọn thư mục
* hiển thị cảnh báo
* cấu hình một đối tượng

Ví dụ:

```text
┌──────────────────────────────┐
│ Delete Todo                  │
│                              │
│ Are you sure?                │
│                              │
│             [Cancel] [Yes]   │
└──────────────────────────────┘
```

Dialog thường có vòng đời ngắn:

```text
Open
 ↓
User interacts
 ↓
Accept / Reject
 ↓
Close
```

---

# 2. `QDialog`

Import:

```python
from PySide6.QtWidgets import QDialog
```

Tạo dialog:

```python
dialog = QDialog()
```

Đặt title:

```python
dialog.setWindowTitle("My Dialog")
```

Hiển thị:

```python
dialog.show()
```

---

# 3. Dialog cũng là một Widget

Đây là điều quan trọng.

Quan hệ kế thừa:

```text
QObject
  ↓
QWidget
  ↓
QDialog
```

Vì vậy `QDialog` có rất nhiều khả năng của `QWidget`:

```python
dialog.resize(400, 300)
dialog.setWindowTitle("Settings")
dialog.setLayout(...)
```

---

# 4. Dialog cần Layout

Ví dụ:

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QVBoxLayout,
)


class MyDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello")

        label = QLabel("Hello Dialog")

        layout = QVBoxLayout(self)
        layout.addWidget(label)


app = QApplication(sys.argv)

dialog = MyDialog()
dialog.show()

sys.exit(app.exec())
```

---

# 5. `show()` — Modeless Dialog

Khi:

```python
dialog.show()
```

dialog được hiển thị nhưng **không khóa cửa sổ cha**.

Ví dụ:

```text
Main Window
┌─────────────────────────────┐
│                             │
│        Main Window          │
│                             │
└─────────────────────────────┘
             +
             ↓
┌─────────────────────────────┐
│        Settings             │
│                             │
└─────────────────────────────┘
```

User vẫn có thể quay lại Main Window.

Đây gọi là:

> **Modeless**

---

# 6. Modeless Dialog

Modeless phù hợp với:

* Find
* Replace
* Tool window
* Floating settings
* Inspector
* Debug panel

Ví dụ:

```text
Main Window
      ↕
Find Dialog
```

Hai cửa sổ có thể tương tác độc lập.

---

# 7. Modal Dialog

Modal nghĩa là:

> Trong khi dialog đang mở, user phải xử lý dialog trước khi quay lại cửa sổ cha.

Ví dụ:

```text
Main Window
      ↓
Delete confirmation
      ↓
[Cancel] [Delete]
```

User không thể tiếp tục thao tác bình thường với Main Window cho tới khi dialog kết thúc.

---

# 8. `exec()`

Đây là method quan trọng:

```python
result = dialog.exec()
```

`exec()` hiển thị dialog theo kiểu modal và chạy một **nested event loop** cho dialog.

Mental model:

```text
Main Event Loop
       │
       ↓
 dialog.exec()
       │
       ↓
Nested Event Loop
       │
       ├── User clicks
       ├── Signals
       ├── Events
       │
       ↓
accept() / reject()
       │
       ↓
exec() returns
       │
       ↓
Main Event Loop continues
```

Đây là một trong những điểm quan trọng nhất của `QDialog`.

---

# 9. `exec()` trả về kết quả

Ví dụ:

```python
result = dialog.exec()
```

Sau khi dialog kết thúc, `result` có thể biểu thị:

```text
Accepted
Rejected
```

Ví dụ:

```python
if result == QDialog.DialogCode.Accepted:
    print("User accepted")
else:
    print("User rejected")
```

---

# 10. `accept()`

Khi user xác nhận:

```python
self.accept()
```

Dialog đóng và:

```python
dialog.exec()
```

trả về:

```python
QDialog.DialogCode.Accepted
```

---

# 11. `reject()`

Khi user hủy:

```python
self.reject()
```

Dialog đóng và:

```python
dialog.exec()
```

trả về:

```python
QDialog.DialogCode.Rejected
```

---

# 12. Đây là pattern cực kỳ quan trọng

Một dialog thường có:

```text
                 Dialog
                   │
          ┌────────┴────────┐
          ↓                 ↓
       Accept             Reject
          │                 │
          ↓                 ↓
      Accepted           Rejected
```

Code bên ngoài:

```python
result = dialog.exec()

if result == QDialog.DialogCode.Accepted:
    # lấy dữ liệu
    ...
```

---

# 13. `QDialogButtonBox`

Qt có widget chuyên dùng cho nút dialog:

```python
from PySide6.QtWidgets import QDialogButtonBox
```

Ví dụ:

```python
buttons = QDialogButtonBox(
    QDialogButtonBox.StandardButton.Ok
    | QDialogButtonBox.StandardButton.Cancel
)
```

UI:

```text
┌──────────────────────────┐
│                          │
│                          │
│              [OK] [Cancel]│
└──────────────────────────┘
```

---

# 14. Kết nối button

```python
buttons.accepted.connect(
    self.accept
)

buttons.rejected.connect(
    self.reject
)
```

Đây là pattern chuẩn:

```text
OK
 ↓
accepted
 ↓
accept()
 ↓
Accepted
```

và:

```text
Cancel
 ↓
rejected
 ↓
reject()
 ↓
Rejected
```

---

# 15. Custom Dialog cơ bản

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class ConfirmDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirm")

        label = QLabel(
            "Are you sure?"
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addWidget(label)
        layout.addWidget(buttons)


app = QApplication(sys.argv)

dialog = ConfirmDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    print("Confirmed")
else:
    print("Cancelled")
```

---

# 16. `QMessageBox`

Khi chỉ cần thông báo hoặc hỏi xác nhận, không cần tự tạo `QDialog`.

Dùng:

```python
from PySide6.QtWidgets import QMessageBox
```

---

# 17. Information Message

```python
QMessageBox.information(
    self,
    "Success",
    "Todo saved successfully.",
)
```

UI:

```text
┌──────────────────────────────┐
│ Information                  │
│                              │
│ Todo saved successfully.     │
│                              │
│                       [OK]   │
└──────────────────────────────┘
```

---

# 18. Warning

```python
QMessageBox.warning(
    self,
    "Warning",
    "Please enter a title.",
)
```

Dùng khi:

```text
cảnh báo
```

nhưng chưa hẳn là lỗi nghiêm trọng.

---

# 19. Critical

```python
QMessageBox.critical(
    self,
    "Error",
    "Unable to save file.",
)
```

Dùng cho lỗi nghiêm trọng hơn.

---

# 20. Question

Đây là loại rất thường gặp:

```python
result = QMessageBox.question(
    self,
    "Delete",
    "Are you sure?",
)
```

Sau đó:

```python
if result == QMessageBox.StandardButton.Yes:
    print("Delete")
```

---

# 21. Chọn Button

Có thể chỉ định button:

```python
result = QMessageBox.question(
    self,
    "Delete",
    "Delete this todo?",
    QMessageBox.StandardButton.Yes
    | QMessageBox.StandardButton.No,
)
```

Sau đó:

```python
if result == QMessageBox.StandardButton.Yes:
    self.delete_todo()
```

---

# 22. `QMessageBox` thực chất cũng là Dialog

Quan hệ:

```text
QDialog
   ↑
QMessageBox
```

Vì vậy:

```text
information
warning
critical
question
```

đều là các dạng dialog được dựng sẵn.

---

# 23. `QInputDialog`

Khi chỉ cần hỏi một giá trị đơn giản.

Import:

```python
from PySide6.QtWidgets import QInputDialog
```

Ví dụ nhập text:

```python
text, ok = QInputDialog.getText(
    self,
    "Rename",
    "New name:",
)
```

Kết quả gồm:

```text
text
ok
```

---

# 24. Kiểm tra `ok`

Không nên chỉ kiểm tra text:

```python
if text:
    ...
```

Vì user có thể:

```text
OK
```

với text rỗng.

Cần phân biệt:

```python
if ok:
    print(text)
```

với:

```python
if not ok:
    print("Cancelled")
```

Đây là pattern quan trọng.

---

# 25. `QInputDialog.getInt()`

Nhập số nguyên:

```python
value, ok = QInputDialog.getInt(
    self,
    "Age",
    "Enter age:",
    18,
    1,
    120,
)
```

Các tham số quan trọng:

```text
default = 18
min     = 1
max     = 120
```

---

# 26. `QInputDialog.getDouble()`

```python
value, ok = QInputDialog.getDouble(
    self,
    "Price",
    "Enter price:",
    10.0,
    0.0,
    100000.0,
    2,
)
```

---

# 27. `QInputDialog.getItem()`

Cho user chọn một item:

```python
items = [
    "Python",
    "Rust",
    "Go",
]

item, ok = QInputDialog.getItem(
    self,
    "Language",
    "Choose:",
    items,
)
```

Kết quả:

```python
item
ok
```

---

# 28. `QFileDialog`

Dialog chọn file.

```python
from PySide6.QtWidgets import QFileDialog
```

Chọn file:

```python
file_path, _ = QFileDialog.getOpenFileName(
    self,
    "Open File",
)
```

---

# 29. Chọn nhiều file

```python
files, _ = QFileDialog.getOpenFileNames(
    self,
    "Open Files",
)
```

Kết quả:

```python
[
    "a.txt",
    "b.txt",
    "c.txt",
]
```

---

# 30. Chọn thư mục

```python
folder = QFileDialog.getExistingDirectory(
    self,
    "Select Folder",
)
```

Kết quả:

```text
C:/Users/User/Documents
```

hoặc:

```text
""
```

nếu user cancel.

---

# 31. Save File

```python
file_path, _ = QFileDialog.getSaveFileName(
    self,
    "Save File",
)
```

Đây là pattern phổ biến:

```text
Ctrl + S
   ↓
getSaveFileName()
   ↓
User chooses path
   ↓
Save file
```

---

# 32. File Filter

Không nên cho user nhìn thấy mọi file nếu app chỉ làm việc với một loại.

Ví dụ:

```python
file_path, _ = QFileDialog.getOpenFileName(
    self,
    "Open Text File",
    "",
    "Text Files (*.txt);;All Files (*)",
)
```

UI:

```text
File name: [________________]

Files of type:
[ Text Files (*.txt) ▼ ]
```

---

# 33. File Dialog trả về gì?

Đây là pattern cần nhớ:

```python
file_path, selected_filter = ...
```

Ví dụ:

```python
file_path, selected_filter = (
    QFileDialog.getOpenFileName(...)
)
```

Nếu Cancel:

```python
file_path == ""
```

Vì vậy luôn kiểm tra:

```python
if not file_path:
    return
```

---

# 34. Modal vs Modeless — tổng hợp

| Cách     |                                     Modal? |             Blocking? | Dùng cho           |
| -------- | -----------------------------------------: | --------------------: | ------------------ |
| `show()` |                                      Không |                 Không | Tool, Find         |
| `open()` | Có theo window modality nhưng non-blocking |                 Không | Dialog bất đồng bộ |
| `exec()` |                                         Có | Có về mặt flow Python | Form xác nhận      |

Điểm quan trọng:

> `exec()` **không làm Qt ngừng xử lý event**.

Nó tạo một **nested event loop**.

---

# 35. `exec()` không phải "đóng băng GUI"

Sai mental model:

```text
dialog.exec()
    ↓
Qt đứng im
```

Đúng hơn:

```text
Main event loop
       │
       └── dialog.exec()
                │
                ↓
         Nested event loop
                │
          ┌─────┼─────┐
          ↓     ↓     ↓
        click  paint  key
                │
                ↓
             accept()
                │
                ↓
           exec() return
```

Cho nên dialog vẫn:

* repaint
* nhận click
* nhận keyboard
* phát signal
* xử lý event

---

# 36. `exec()` và `show()` khác nhau về flow

### `show()`

```python
dialog.show()

print("Next")
```

Flow:

```text
show()
 ↓
return ngay
 ↓
print("Next")
```

---

### `exec()`

```python
result = dialog.exec()

print("Next")
```

Flow:

```text
exec()
 ↓
dialog hoạt động
 ↓
user đóng dialog
 ↓
exec() return
 ↓
print("Next")
```

Đây là khác biệt cực kỳ quan trọng.

---

# 37. `open()`

`open()` cũng mở dialog theo kiểu non-blocking.

```python
dialog.open()
```

Thay vì:

```python
result = dialog.exec()
```

thường bạn sẽ xử lý kết quả thông qua signal:

```python
dialog.accepted.connect(...)
dialog.rejected.connect(...)
```

hoặc các signal phù hợp khác.

Đây là cách tốt khi bạn muốn giữ flow event-driven thay vì viết code theo kiểu:

```text
mở dialog
 ↓
chờ
 ↓
lấy kết quả
```

---

# 38. Khi nào dùng `exec()`?

Dùng khi flow nghiệp vụ tự nhiên là:

```text
Create Todo
 ↓
mở form
 ↓
chờ user hoàn thành
 ↓
lấy kết quả
 ↓
tiếp tục
```

Ví dụ:

```python
dialog = TodoDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    todo = dialog.get_data()
    self.save(todo)
```

Code rất dễ đọc.

---

# 39. Khi nào dùng `open()`?

Khi bạn muốn:

```text
Main UI tiếp tục chạy
       ↓
Dialog xử lý event
       ↓
Khi đóng → signal
```

Ví dụ:

```python
self.dialog = TodoDialog()

self.dialog.accepted.connect(
    self.todo_saved
)

self.dialog.open()
```

Đây là style event-driven hơn.

---

# 40. Custom Dialog với dữ liệu

Đây mới là phần quan trọng.

Giả sử Todo:

```python
{
    "title": "Learn PySide6",
    "priority": 2,
}
```

Ta muốn dialog:

```text
┌─────────────────────────────┐
│ New Todo                    │
│                             │
│ Title:    [_____________]   │
│ Priority: [2           ▼]   │
│                             │
│             [Cancel] [OK]   │
└─────────────────────────────┘
```

---

# 41. `TodoDialog`

```python
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QSpinBox,
    QFormLayout,
    QVBoxLayout,
)
```

Code:

```python
class TodoDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Todo")

        self.title_edit = QLineEdit()

        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)

        form = QFormLayout()

        form.addRow(
            "Title:",
            self.title_edit,
        )

        form.addRow(
            "Priority:",
            self.priority_spin,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)
        layout.addWidget(buttons)
```

---

# 42. `get_data()`

Dialog nên có API để lấy dữ liệu:

```python
def get_data(self):
    return {
        "title": self.title_edit.text().strip(),
        "priority": self.priority_spin.value(),
    }
```

Sau đó:

```python
dialog = TodoDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    data = dialog.get_data()

    print(data)
```

Kết quả:

```python
{
    "title": "Learn PySide6",
    "priority": 3,
}
```

---

# 43. Đây là một design pattern rất quan trọng

Đừng để Main Window truy cập trực tiếp:

```python
dialog.title_edit.text()
dialog.priority_spin.value()
```

Thay vào đó:

```python
dialog.get_data()
```

Main Window chỉ cần biết:

```text
TodoDialog
    ↓
get_data()
    ↓
Todo data
```

Nó giảm coupling.

---

# 44. Dialog nhận dữ liệu để Edit

Dialog không chỉ dùng Create.

Ví dụ:

```text
Todo hiện tại:

title = "Learn Python"
priority = 3
```

Mở Edit:

```python
dialog = TodoDialog(todo)
```

Trong constructor:

```python
def __init__(self, todo=None, parent=None):
    super().__init__(parent)

    ...

    if todo:
        self.title_edit.setText(
            todo["title"]
        )

        self.priority_spin.setValue(
            todo["priority"]
        )
```

Bây giờ cùng một dialog phục vụ:

```text
Create
Edit
```

---

# 45. `accept()` không nên tự động có nghĩa là dữ liệu hợp lệ

Đây là một lỗi thiết kế phổ biến.

Nếu:

```python
buttons.accepted.connect(
    self.accept
)
```

thì user có thể nhấn OK dù:

```text
Title = ""
```

Tốt hơn:

```python
buttons.accepted.connect(
    self.validate_and_accept
)
```

Sau đó:

```python
def validate_and_accept(self):

    title = self.title_edit.text().strip()

    if not title:
        self.title_edit.setFocus()
        return

    self.accept()
```

Mental model:

```text
OK
 ↓
Validate
 ↓
 ┌─────────────┐
 │             │
Invalid       Valid
 │             │
Stay open     accept()
```

Đây chính là kiến thức Buổi 7 được sử dụng lại.

---

# 46. Custom Dialog hoàn chỉnh

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)


class TodoDialog(QDialog):

    def __init__(self, todo=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Edit Todo" if todo else "New Todo"
        )

        self.title_edit = QLineEdit()

        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)

        if todo:
            self.title_edit.setText(
                todo["title"]
            )

            self.priority_spin.setValue(
                todo["priority"]
            )

        form = QFormLayout()

        form.addRow(
            "Title:",
            self.title_edit,
        )

        form.addRow(
            "Priority:",
            self.priority_spin,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.validate_and_accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)
        layout.addWidget(buttons)

    def validate_and_accept(self):

        title = self.title_edit.text().strip()

        if not title:
            self.title_edit.setFocus()
            return

        self.accept()

    def get_data(self):
        return {
            "title": self.title_edit.text().strip(),
            "priority": self.priority_spin.value(),
        }


app = QApplication(sys.argv)

dialog = TodoDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    print(dialog.get_data())

sys.exit(app.exec())
```

---

# 47. Một vấn đề rất quan trọng: Parent

Khi tạo dialog:

```python
dialog = TodoDialog(self)
```

`self` thường là Main Window.

Điều này giúp Qt hiểu quan hệ:

```text
MainWindow
    │
    └── TodoDialog
```

Dialog sẽ có:

* owner/parent phù hợp
* behavior window tốt hơn
* lifetime management tốt hơn trong nhiều trường hợp
* vị trí/window relationship phù hợp

---

# 48. Đừng tạo dialog mỗi lần một cách tùy tiện nếu cần giữ state

Ví dụ:

```python
def open_settings(self):
    dialog = SettingsDialog(self)
    dialog.show()
```

Nếu mỗi lần gọi đều tạo instance mới:

```text
click
 ↓
Dialog A

click
 ↓
Dialog B

click
 ↓
Dialog C
```

Có thể không phải behavior bạn muốn.

Với modeless dialog, đôi khi nên giữ reference:

```python
self.settings_dialog = SettingsDialog(self)
self.settings_dialog.show()
```

Để tránh nhiều instance hoặc để quản lý lifetime.

---

# 49. `QMessageBox` nên dùng khi nào?

Dùng:

```python
QMessageBox
```

cho các tình huống đơn giản:

```text
Success
Warning
Error
Confirmation
```

Không nên tự tạo:

```text
SuccessDialog
WarningDialog
DeleteDialog
...
```

nếu chúng chỉ chứa một message và vài button cơ bản.

---

# 50. `QInputDialog` nên dùng khi nào?

Dùng khi chỉ cần một input đơn giản:

```text
Enter name
Enter number
Choose item
```

Không nên xây custom dialog cho:

```text
"Nhập một cái tên"
```

nếu chỉ có một `QLineEdit`.

---

# 51. Khi nào phải dùng Custom Dialog?

Khi form có nhiều field:

```text
Title
Description
Priority
Category
Due date
Tags
...
```

hoặc logic:

```text
Validation
Preview
Advanced settings
Multiple widgets
```

thì:

```python
class TodoDialog(QDialog):
    ...
```

là hợp lý.

---

# 52. Bài tập 1

Tạo:

```text
ConfirmDeleteDialog
```

UI:

```text
┌──────────────────────────────────┐
│ Delete Todo                      │
│                                  │
│ Are you sure you want to delete  │
│ "Learn PySide6"?                 │
│                                  │
│                 [Cancel] [Delete]│
└──────────────────────────────────┘
```

Kết quả:

```python
if dialog.exec() == QDialog.DialogCode.Accepted:
    delete_todo()
```

---

# 53. Bài tập 2

Tạo:

```text
RenameDialog
```

UI:

```text
┌──────────────────────────┐
│ Rename                   │
│                          │
│ Name: [______________]   │
│                          │
│             [OK] [Cancel]│
└──────────────────────────┘
```

Yêu cầu:

* Không cho OK khi name rỗng.
* Enter → OK.
* Escape → Cancel.
* Có `get_name()`.

---

# 54. Bài tập 3

Dùng `QFileDialog` xây:

```text
Simple Text Viewer
```

UI:

```text
┌─────────────────────────────────┐
│ [Open]                          │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ file content                │ │
│ │                             │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

Flow:

```text
Open
 ↓
QFileDialog
 ↓
select .txt
 ↓
read file
 ↓
QPlainTextEdit
```

---

# 55. Bài tập 4 — Mini Dialog Architecture

Xây:

```text
TodoDialog
```

có:

```text
title
description
priority
```

và API:

```python
dialog.get_data()
```

Kết quả:

```python
{
    "title": "...",
    "description": "...",
    "priority": 3,
}
```

Không để Main Window truy cập trực tiếp widget bên trong dialog.

---

# 56. Bài tập 5 — So sánh 3 cách

Hãy viết cùng một chức năng:

```text
Nhập tên Todo
```

bằng:

### Cách 1

```python
QInputDialog.getText()
```

### Cách 2

```python
QDialog + QLineEdit
```

### Cách 3

```python
TodoDialog
```

Sau đó tự trả lời:

> Khi nào nên dùng cách nào?

Đây là bài tập rất quan trọng để hiểu **abstraction level**.

---

# 57. Tổng kết Buổi 8

Bạn cần nhớ:

```text
QDialog
│
├── show()
│     └── modeless / non-blocking
│
├── open()
│     └── non-blocking dialog flow
│
└── exec()
      └── modal + nested event loop
```

Kết quả:

```text
accept()
   ↓
Accepted

reject()
   ↓
Rejected
```

Các dialog dựng sẵn:

```text
QMessageBox
    ↓
message / warning / error / confirmation

QInputDialog
    ↓
simple input

QFileDialog
    ↓
file / folder selection
```

Custom dialog:

```text
QDialog
   ↓
Widgets
   ↓
Validation
   ↓
accept / reject
   ↓
get_data()
```

Và pattern quan trọng nhất:

```python
dialog = TodoDialog(parent=self)

if dialog.exec() == QDialog.DialogCode.Accepted:
    data = dialog.get_data()
    self.save(data)
```

Đây sẽ là nền móng trực tiếp cho **Buổi 9 — `QMainWindow`**, nơi chúng ta xây cấu trúc của một desktop application thực sự với:

```text
QMainWindow
├── MenuBar
├── ToolBar
├── StatusBar
├── Central Widget
└── Dock Widget
```

Sau đó **Buổi 10** sẽ ghép `QMainWindow + Dialog + Form + Validation` thành **Todo App v1**.
