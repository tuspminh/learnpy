# Buổi 6 — Widget Foundation Deep Dive

Hôm nay chúng ta đi vào **các widget cơ bản của PySide6**.

Nhưng mục tiêu không phải học thuộc:

```python
QLabel
QPushButton
QLineEdit
...
```

Mà phải hiểu một widget Qt thực chất gồm:

```text
Widget
│
├── State
├── Property
├── Method
├── Signal
├── Event
└── Layout
```

Đây là mental model rất quan trọng để sau này bạn học `QTableView`, `QTreeView`, Model/View, MVC và xây ứng dụng lớn.

---

# 1. Widget trong Qt là gì?

Ví dụ:

```python
button = QPushButton("Save")
```

Đừng chỉ nghĩ:

> Đây là cái nút.

Hãy nghĩ:

```text
QPushButton
│
├── State
│   └── enabled / disabled
│
├── Property
│   ├── text
│   ├── icon
│   └── checkable
│
├── Method
│   ├── setText()
│   ├── setEnabled()
│   └── click()
│
├── Signal
│   ├── clicked
│   ├── pressed
│   └── released
│
└── Event
    ├── mouse
    ├── keyboard
    └── focus
```

Đây chính là cách chúng ta nên học widget.

---

# 2. `QLabel`

Widget đơn giản nhất:

```python
from PySide6.QtWidgets import QLabel
```

Tạo:

```python
label = QLabel("Hello PySide6")
```

Hiển thị:

```text
Hello PySide6
```

---

# 3. Thay đổi text

```python
label.setText("Hello")
```

Lấy text:

```python
text = label.text()
```

Mental model:

```text
setText()
   ↓
Property thay đổi
   ↓
UI cập nhật
```

---

# 4. QLabel không chỉ hiển thị text

`QLabel` còn có thể hiển thị:

* text
* rich text
* HTML
* pixmap
* movie
* link

Ví dụ HTML đơn giản:

```python
label.setText(
    "<b>Hello</b> <i>PySide6</i>"
)
```

Có thể hiển thị:

```text
Hello PySide6
```

với formatting.

---

# 5. `QPushButton`

```python
from PySide6.QtWidgets import QPushButton

button = QPushButton("Save")
```

Thay text:

```python
button.setText("Submit")
```

Lấy text:

```python
print(button.text())
```

---

# 6. Signal của QPushButton

Signal phổ biến nhất:

```python
button.clicked.connect(...)
```

Ví dụ:

```python
def save():
    print("Saved")


button.clicked.connect(save)
```

Mental model:

```text
User click
    ↓
QPushButton
    ↓
clicked
    ↓
save()
```

---

# 7. `clicked` có tham số

`clicked` có thể cung cấp trạng thái checked đối với button checkable.

Ví dụ:

```python
def handle_click(checked):
    print(checked)


button.clicked.connect(handle_click)
```

Hoặc nếu không cần:

```python
button.clicked.connect(
    lambda: print("Clicked")
)
```

---

# 8. `pressed` vs `released` vs `clicked`

Có ba signal thường gặp:

```text
pressed
released
clicked
```

Chuỗi:

```text
Mouse down
   ↓
pressed
   ↓
Mouse up
   ↓
released
   ↓
clicked
```

Không phải lúc nào `clicked` cũng tương đương đơn giản với một mouse event thô.

---

# 9. Button Checkable

Button có thể hoạt động như toggle:

```python
button.setCheckable(True)
```

Bây giờ:

```text
OFF
 ↓ click
ON
 ↓ click
OFF
```

Có thể:

```python
print(button.isChecked())
```

---

# 10. `toggled`

Khi trạng thái thay đổi:

```python
button.toggled.connect(...)
```

Ví dụ:

```python
def on_toggled(checked):
    print("Checked:", checked)


button.toggled.connect(on_toggled)
```

Đây là pattern rất hữu ích cho:

* Dark mode
* Sidebar
* Settings
* Enable/disable feature

---

# 11. `QLineEdit`

Widget nhập một dòng text:

```python
from PySide6.QtWidgets import QLineEdit

edit = QLineEdit()
```

Đặt placeholder:

```python
edit.setPlaceholderText("Enter your name...")
```

---

# 12. Text của QLineEdit

Đặt:

```python
edit.setText("Alice")
```

Lấy:

```python
text = edit.text()
```

Xóa:

```python
edit.clear()
```

---

# 13. `textChanged`

Khi text thay đổi:

```python
edit.textChanged.connect(...)
```

Ví dụ:

```python
def handle_text(text):
    print(text)


edit.textChanged.connect(handle_text)
```

Mỗi lần text thay đổi:

```text
A
AB
ABC
ABCD
```

signal được phát.

---

# 14. `textEdited`

Có một signal khác:

```python
edit.textEdited
```

Điểm rất quan trọng:

```text
textChanged
    ↑
thay đổi text nói chung

textEdited
    ↑
text được user chỉnh sửa
```

Đây là sự khác biệt bạn nên nhớ.

---

# 15. Ví dụ `textChanged` vs `textEdited`

```python
edit.setText("Hello")
```

Đây là thay đổi bằng code.

Thông thường:

```text
textChanged → có
textEdited  → không
```

Nếu user gõ:

```text
Hello World
```

thì:

```text
textChanged → có
textEdited  → có
```

Đây là distinction rất hữu ích trong form.

---

# 16. `returnPressed`

Nếu user nhấn Enter:

```python
edit.returnPressed.connect(...)
```

Ví dụ:

```python
def search():
    print("Search")


edit.returnPressed.connect(search)
```

Đây là pattern cực kỳ phổ biến:

```text
Search box
    │
    └── Enter
          ↓
       search()
```

---

# 17. Password Input

Có thể đổi echo mode:

```python
from PySide6.QtWidgets import QLineEdit

password = QLineEdit()

password.setEchoMode(
    QLineEdit.EchoMode.Password
)
```

Khi user nhập:

```text
••••••••
```

---

# 18. Các Echo Mode

Một số mode:

```text
Normal
NoEcho
Password
PasswordEchoOnEdit
```

Ví dụ:

```python
password.setEchoMode(
    QLineEdit.EchoMode.Password
)
```

---

# 19. `QTextEdit`

Dùng cho text nhiều dòng.

```python
from PySide6.QtWidgets import QTextEdit

editor = QTextEdit()
```

Ví dụ:

```text
┌──────────────────────────────┐
│ Hello                        │
│ This is a long text.         │
│ Multiple lines are possible. │
│                              │
└──────────────────────────────┘
```

---

# 20. `QPlainTextEdit`

Cũng là editor nhiều dòng:

```python
from PySide6.QtWidgets import QPlainTextEdit

editor = QPlainTextEdit()
```

Điểm khác quan trọng:

```text
QTextEdit
    ↓
rich text / document-oriented

QPlainTextEdit
    ↓
plain text
```

Nếu làm:

* Markdown editor
* code editor đơn giản
* log viewer
* text file editor

thì `QPlainTextEdit` thường rất phù hợp.

---

# 21. Lấy text

Với `QTextEdit`:

```python
text = editor.toPlainText()
```

Không dùng:

```python
editor.text()
```

Đây là lỗi người mới rất hay gặp.

---

# 22. Đặt text

```python
editor.setPlainText("Hello")
```

Ví dụ:

```python
editor.setPlainText(
    "Line 1\n"
    "Line 2\n"
    "Line 3"
)
```

---

# 23. `QCheckBox`

```python
from PySide6.QtWidgets import QCheckBox

checkbox = QCheckBox("Remember me")
```

UI:

```text
☐ Remember me
```

Click:

```text
☑ Remember me
```

---

# 24. Lấy trạng thái checkbox

```python
checked = checkbox.isChecked()
```

Ví dụ:

```python
if checkbox.isChecked():
    print("Remember")
```

---

# 25. Signal của QCheckBox

Signal quan trọng:

```python
checkbox.stateChanged
```

và:

```python
checkbox.checkStateChanged
```

Trong code hiện đại, khi cần trạng thái rõ ràng, `checkStateChanged` rất đáng chú ý.

Ví dụ:

```python
checkbox.checkStateChanged.connect(
    lambda state: print(state)
)
```

---

# 26. Checkbox không nhất thiết chỉ có 2 trạng thái

Qt hỗ trợ:

```text
Unchecked
PartiallyChecked
Checked
```

Để bật trạng thái trung gian:

```python
checkbox.setTristate(True)
```

Khi đó:

```text
☐
☑
☒
```

Khái niệm này đặc biệt hữu ích trong tree/list với trạng thái cha-con.

---

# 27. `QRadioButton`

Dùng khi user phải chọn **một trong nhiều lựa chọn**.

```python
from PySide6.QtWidgets import QRadioButton

male = QRadioButton("Male")
female = QRadioButton("Female")
```

Thông thường:

```text
○ Male
○ Female
```

Chọn một:

```text
● Male
○ Female
```

---

# 28. Radio Button cần hiểu Group

Nếu nhiều radio button nằm trong cùng parent phù hợp, Qt có thể quản lý exclusivity.

Nhưng khi UI phức tạp, nên chủ động dùng:

```python
QButtonGroup
```

Ví dụ:

```python
from PySide6.QtWidgets import QButtonGroup

group = QButtonGroup()

group.addButton(male)
group.addButton(female)
```

Bây giờ group quản lý các button.

---

# 29. `QComboBox`

Dropdown:

```python
from PySide6.QtWidgets import QComboBox

combo = QComboBox()
```

Thêm item:

```python
combo.addItem("Python")
combo.addItem("Rust")
combo.addItem("Go")
```

UI:

```text
┌─────────────────┐
│ Python        ▼ │
└─────────────────┘
```

---

# 30. `addItems`

Có thể thêm nhiều item:

```python
combo.addItems([
    "Python",
    "Rust",
    "Go",
])
```

---

# 31. Lấy item

Theo index:

```python
text = combo.itemText(0)
```

Lấy item hiện tại:

```python
text = combo.currentText()
```

Lấy index:

```python
index = combo.currentIndex()
```

---

# 32. Signal `currentIndexChanged`

```python
combo.currentIndexChanged.connect(...)
```

Ví dụ:

```python
def handle_change(index):
    print(index)


combo.currentIndexChanged.connect(handle_change)
```

Có thể nhận index hoặc text tùy overload/signature sử dụng.

Trong code rõ ràng, bạn nên chọn đúng signal/signature mình cần thay vì dựa vào overload một cách mơ hồ.

---

# 33. `QSpinBox`

Nhập số nguyên:

```python
from PySide6.QtWidgets import QSpinBox

spin = QSpinBox()
```

Ví dụ:

```text
┌──────┐
│  10 ▲│
└──────┘
```

---

# 34. Range

```python
spin.setMinimum(0)
spin.setMaximum(100)
```

Hoặc:

```python
spin.setRange(0, 100)
```

Đây là cách tốt hơn:

```python
spin.setRange(0, 100)
```

---

# 35. Value

Đặt:

```python
spin.setValue(50)
```

Lấy:

```python
value = spin.value()
```

Signal:

```python
spin.valueChanged.connect(...)
```

---

# 36. `QDoubleSpinBox`

Nếu cần số thực:

```python
from PySide6.QtWidgets import QDoubleSpinBox

spin = QDoubleSpinBox()
```

Ví dụ:

```text
0.00
0.10
0.20
...
```

Có thể:

```python
spin.setRange(0.0, 100.0)
spin.setDecimals(2)
spin.setSingleStep(0.1)
```

---

# 37. Đây chính là State

Hãy nhìn lại.

Ví dụ:

```python
spin.value()
```

là state.

```python
spin.setValue(...)
```

thay đổi state.

```python
spin.valueChanged
```

thông báo state thay đổi.

Đây là pattern rất quan trọng:

```text
Widget
│
├── State
│    └── value
│
├── Mutation
│    └── setValue()
│
└── Signal
     └── valueChanged
```

---

# 38. Tất cả widget đều có mental model tương tự

Ví dụ `QLineEdit`:

```text
QLineEdit
│
├── State
│   └── text
│
├── Mutation
│   └── setText()
│
└── Signal
    ├── textChanged
    └── textEdited
```

`QCheckBox`:

```text
QCheckBox
│
├── State
│   └── checked
│
├── Mutation
│   └── setChecked()
│
└── Signal
    └── checkStateChanged
```

`QSpinBox`:

```text
QSpinBox
│
├── State
│   └── value
│
├── Mutation
│   └── setValue()
│
└── Signal
    └── valueChanged
```

Đây chính là tư duy **state-driven UI**.

---

# 39. `setEnabled()` / `setDisabled()`

Hầu hết widget đều kế thừa:

```python
widget.setEnabled(False)
```

hoặc:

```python
widget.setDisabled(True)
```

UI:

```text
Normal
 ↓
Disabled
```

Kiểm tra:

```python
widget.isEnabled()
```

---

# 40. Ví dụ Form phụ thuộc state

Giả sử:

```text
☐ Enable advanced settings

Advanced option: [________]
```

Nếu checkbox unchecked:

```text
☐ Enable advanced settings

Advanced option: [ disabled ]
```

Nếu checked:

```text
☑ Enable advanced settings

Advanced option: [ enabled ]
```

Code:

```python
checkbox.toggled.connect(
    advanced_edit.setEnabled
)
```

Đây là một ví dụ rất đẹp của Signal → Slot.

---

# 41. Không cần viết callback dài

Thay vì:

```python
def on_toggle(checked):
    advanced_edit.setEnabled(checked)

checkbox.toggled.connect(on_toggle)
```

Có thể viết trực tiếp:

```python
checkbox.toggled.connect(
    advanced_edit.setEnabled
)
```

Vì:

```text
toggled(bool)
       ↓
setEnabled(bool)
```

signature tương thích.

Đây là cách viết Qt rất elegant.

---

# 42. Một Form hoàn chỉnh

Hãy kết hợp:

```text
QLabel
QLineEdit
QCheckBox
QComboBox
QSpinBox
QPushButton
```

Thiết kế:

```text
┌─────────────────────────────────────┐
│ User Settings                       │
│                                     │
│ Name:     [____________________]    │
│ Language: [Python              ▼]   │
│ Age:      [25                  ▲▼]  │
│                                     │
│ ☑ Receive notifications             │
│                                     │
│                         [Save]       │
└─────────────────────────────────────┘
```

---

# 43. Code hoàn chỉnh

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
)


class UserForm(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Settings")

        self.name_edit = QLineEdit()

        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Python",
            "Rust",
            "Go",
        ])

        self.age_spin = QSpinBox()
        self.age_spin.setRange(1, 120)
        self.age_spin.setValue(25)

        self.notification_check = QCheckBox(
            "Receive notifications"
        )

        self.save_button = QPushButton("Save")

        form_layout = QFormLayout()

        form_layout.addRow(
            "Name:",
            self.name_edit,
        )

        form_layout.addRow(
            "Language:",
            self.language_combo,
        )

        form_layout.addRow(
            "Age:",
            self.age_spin,
        )

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel("User Settings")
        )

        main_layout.addLayout(form_layout)

        main_layout.addWidget(
            self.notification_check
        )

        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(
            self.save
        )

    def save(self):
        print("Name:", self.name_edit.text())
        print(
            "Language:",
            self.language_combo.currentText(),
        )
        print(
            "Age:",
            self.age_spin.value(),
        )
        print(
            "Notifications:",
            self.notification_check.isChecked(),
        )


app = QApplication(sys.argv)

window = UserForm()
window.resize(500, 300)
window.show()

sys.exit(app.exec())
```

---

# 44. Kiến trúc của Form

Đừng nhìn code thành một đống widget.

Hãy nhìn:

```text
UserForm
│
├── State
│   ├── name
│   ├── language
│   ├── age
│   └── notifications
│
├── Widgets
│   ├── QLineEdit
│   ├── QComboBox
│   ├── QSpinBox
│   ├── QCheckBox
│   └── QPushButton
│
├── Layout
│   ├── QVBoxLayout
│   ├── QFormLayout
│   └── QHBoxLayout
│
└── Behavior
    └── save()
```

Đây là bước đầu tiên để chuyển từ **demo GUI** sang **application architecture**.

---

# 45. Một lỗi kiến trúc cần tránh

Không nên nhét toàn bộ logic vào:

```python
def save(self):
    ...
```

Ví dụ app thực tế:

```text
save()
│
├── validate input
├── create model
├── save database
├── show notification
└── update UI
```

Sau này chúng ta sẽ tách:

```text
View
 ↓
Controller / Presenter
 ↓
Service
 ↓
Repository
 ↓
Database
```

Đây chính là hướng rất phù hợp với các ứng dụng PySide6 lớn.

---

# 46. Widget hierarchy

Nhớ rằng:

```text
QWidget
│
├── QLabel
├── QAbstractButton
│   ├── QPushButton
│   ├── QCheckBox
│   └── QRadioButton
│
├── QLineEdit
├── QTextEdit
├── QPlainTextEdit
├── QComboBox
├── QSpinBox
└── ...
```

Nhờ inheritance nên rất nhiều behavior dùng chung.

Ví dụ:

```python
widget.setEnabled(False)
```

hoạt động với rất nhiều widget.

---

# 47. Property ≠ Method

Đây là một khái niệm cần phân biệt.

Ví dụ:

```python
edit.text()
```

là method để đọc state.

```python
edit.setText(...)
```

là method để thay đổi state.

Qt thường thiết kế API theo cặp:

```text
get/read
    ↓
text()

write
    ↓
setText()
```

Một số property được Qt khai báo dưới dạng Qt Property, nhưng Python API thường biểu hiện qua getter/setter như trên.

---

# 48. Property → Signal → UI

Một pattern cực kỳ quan trọng:

```text
User
 ↓
Interaction
 ↓
Widget State thay đổi
 ↓
Signal
 ↓
Application logic
 ↓
UI / Model update
```

Ví dụ:

```text
User nhập "Python"
       ↓
QLineEdit.text
       ↓
textChanged
       ↓
search()
       ↓
Search results
```

---

# 49. Widget Event và Widget Signal

Hãy phân biệt:

```text
Event
    ↓
QKeyEvent
QMouseEvent
QFocusEvent
```

với:

```text
Signal
    ↓
clicked
textChanged
valueChanged
currentIndexChanged
```

Quy tắc thực tế:

> Nếu widget đã cung cấp signal phù hợp, ưu tiên signal/slot.

Ví dụ muốn biết button được click:

**Không cần:**

```python
mousePressEvent()
```

Hãy dùng:

```python
button.clicked.connect(...)
```

---

# 50. Khi nào dùng Event?

Dùng Event khi bạn cần behavior thấp hơn abstraction của widget.

Ví dụ:

```text
Custom drag
Custom keyboard interaction
Custom painting
Mouse tracking
Window close confirmation
```

Còn business interaction thông thường:

```text
Button clicked
Text changed
Checkbox toggled
Value changed
```

thì dùng Signal.

---

# 51. Bài tập 1 — Login Form

Tạo:

```text
┌─────────────────────────────┐
│          Login              │
│                             │
│ Username: [_____________]   │
│ Password: [_____________]   │
│                             │
│ ☑ Remember me               │
│                             │
│                 [ Login ]   │
└─────────────────────────────┘
```

Yêu cầu:

* Username → `QLineEdit`
* Password → `QLineEdit`
* Password dùng `Password` echo mode
* Remember me → `QCheckBox`
* Login → `QPushButton`

Khi click Login:

```text
Username: ...
Password: ...
Remember: True
```

---

# 52. Bài tập 2 — Dynamic Form

Tạo:

```text
☐ Enable advanced settings

Advanced option:
[________________]
```

Yêu cầu:

```text
Unchecked
    ↓
Advanced option disabled

Checked
    ↓
Advanced option enabled
```

Cố gắng viết chỉ:

```python
checkbox.toggled.connect(...)
```

mà không cần callback trung gian.

---

# 53. Bài tập 3 — Search Box

Tạo:

```text
┌─────────────────────────────────┐
│ Search: [____________________]  │
└─────────────────────────────────┘
```

Khi user nhập:

```text
python
```

in ra:

```text
Searching: python
```

Nhưng chỉ tìm khi user nhấn Enter.

Không dùng `textChanged`.

Dùng:

```python
returnPressed
```

---

# 54. Bài tập 4 — Font Settings

Tạo:

```text
Font size: [ 14 ▲▼ ]

☐ Bold

Preview:
Hello PySide6
```

Khi đổi font size:

```text
QSpinBox
   ↓
valueChanged
   ↓
QLabel.setStyleSheet(...)
```

Khi bật Bold:

```text
QCheckBox
   ↓
toggled
   ↓
Preview
```

Bài này giúp bạn bắt đầu hiểu **reactive UI**.

---

# 55. Bài tập 5 — Mini Project

Xây:

## User Editor

```text
┌────────────────────────────────────────┐
│ User Editor                            │
│                                        │
│ Name:      [_______________________]   │
│ Email:     [_______________________]   │
│ Role:      [Admin                ▼]    │
│ Age:       [25                   ▲▼]   │
│                                        │
│ ☑ Active                               │
│ ☑ Receive email                        │
│                                        │
│                    [Cancel] [Save]     │
└────────────────────────────────────────┘
```

Khi `Save`:

```text
User:
{
    name: "...",
    email: "...",
    role: "...",
    age: 25,
    active: True,
    receive_email: True,
}
```

**Chưa cần database.**

Mục tiêu là luyện:

```text
Widget
   ↓
State
   ↓
Signal
   ↓
Handler
   ↓
Collect data
```

---

# 56. Tổng kết Buổi 6

Bạn cần nắm được bảng này:

| Widget           | State         | Getter          | Setter              | Signal                         |
| ---------------- | ------------- | --------------- | ------------------- | ------------------------------ |
| `QLabel`         | text          | `text()`        | `setText()`         | tùy property                   |
| `QPushButton`    | checked       | `isChecked()`   | `setChecked()`      | `clicked`, `toggled`           |
| `QLineEdit`      | text          | `text()`        | `setText()`         | `textChanged`, `textEdited`    |
| `QTextEdit`      | document/text | `toPlainText()` | `setPlainText()`    | `textChanged`                  |
| `QCheckBox`      | checked/state | `isChecked()`   | `setChecked()`      | `toggled`, `checkStateChanged` |
| `QComboBox`      | current item  | `currentText()` | `setCurrentIndex()` | `currentIndexChanged`          |
| `QSpinBox`       | value         | `value()`       | `setValue()`        | `valueChanged`                 |
| `QDoubleSpinBox` | value         | `value()`       | `setValue()`        | `valueChanged`                 |

Mental model cuối buổi:

```text
                 QWidget
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      State      Methods      Signals
        │           │           │
        │      setValue()       │
        │                       │
        └───────────────────────┘
                    ↓
               UI Behavior
```

**Buổi 7** chúng ta sẽ đi vào một chủ đề cực kỳ quan trọng: **Qt Resource System + Icon + Image + `QPixmap` + `QIcon`**, sau đó bắt đầu xây một UI nhỏ có cấu trúc giống ứng dụng desktop thực tế.
