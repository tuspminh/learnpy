# Buổi 5 — Layout System Deep Dive

Sau 4 buổi, chúng ta đã có:

```text
QApplication
    ↓
Event Loop
    ↓
QObject
    ↓
Event
    ↓
Signal / Slot
```

Hôm nay chuyển sang một phần bạn sẽ dùng **trong gần như mọi ứng dụng PySide6**:

> **Layout System**

Mục tiêu không phải chỉ biết `QVBoxLayout` hay `QHBoxLayout`, mà phải hiểu **Qt quyết định kích thước và vị trí widget như thế nào**.

---

# 1. Vì sao không nên đặt tọa độ thủ công?

Bạn có thể làm:

```python
button.setGeometry(100, 100, 200, 50)
```

Tức là:

```text
x = 100
y = 100
width = 200
height = 50
```

Nhưng cách này nhanh chóng trở thành vấn đề.

Ví dụ:

```text
┌─────────────────────────────┐
│ [Name____________________]  │
│                             │
│ [Save] [Cancel]             │
└─────────────────────────────┘
```

Nếu cửa sổ thay đổi:

```text
┌────────────────────────────────────────────┐
│ [Name___________________________________]  │
│                                            │
│ [Save] [Cancel]                            │
└────────────────────────────────────────────┘
```

Widget phải tự thay đổi kích thước.

Nếu dùng `setGeometry()` cho từng widget, bạn phải tự tính:

```text
x
y
width
height
```

Layout giải quyết toàn bộ việc đó.

---

# 2. Layout là gì?

Layout là một **bộ máy quản lý vị trí và kích thước widget**.

Thay vì:

```text
Developer
   ↓
tự tính x/y/width/height
```

ta nói:

```text
Developer
   ↓
khai báo quan hệ bố cục
   ↓
Qt Layout Engine
   ↓
tính toán vị trí/kích thước
```

Ví dụ:

```python
layout = QVBoxLayout()
```

sau đó:

```python
layout.addWidget(label)
layout.addWidget(button)
```

Ta đang nói:

> Xếp `label` và `button` theo chiều dọc.

---

# 3. `QVBoxLayout`

`V` = Vertical.

```python
from PySide6.QtWidgets import QVBoxLayout
```

Ví dụ:

```python
layout = QVBoxLayout()

layout.addWidget(QLabel("Name"))
layout.addWidget(QLineEdit())
layout.addWidget(QPushButton("Save"))
```

Kết quả:

```text
┌─────────────────────┐
│ Name                │
│ [________________]  │
│                     │
│ [ Save ]             │
└─────────────────────┘
```

---

# 4. Gắn layout vào widget

Có hai cách phổ biến.

### Cách 1

```python
layout = QVBoxLayout()

window.setLayout(layout)
```

### Cách 2

```python
layout = QVBoxLayout(window)
```

Cách 2 rất tiện.

Ví dụ:

```python
window = QWidget()

layout = QVBoxLayout(window)
```

Sau đó:

```python
layout.addWidget(...)
```

---

# 5. `QHBoxLayout`

`H` = Horizontal.

```python
layout = QHBoxLayout()
```

Ví dụ:

```python
layout.addWidget(QPushButton("Save"))
layout.addWidget(QPushButton("Cancel"))
```

Kết quả:

```text
┌──────────────────────────┐
│                          │
│ [ Save ] [ Cancel ]      │
│                          │
└──────────────────────────┘
```

---

# 6. `QVBoxLayout` + `QHBoxLayout`

Đây là pattern bạn sẽ sử dụng liên tục.

Ví dụ:

```text
┌─────────────────────────────────┐
│ Name                            │
│ [_____________________________] │
│                                 │
│ [ Save ] [ Cancel ]             │
└─────────────────────────────────┘
```

Có thể thiết kế:

```text
Main Layout
│
├── Label
├── LineEdit
└── Button Layout
      ├── Save
      └── Cancel
```

Code:

```python
main_layout = QVBoxLayout()

main_layout.addWidget(label)
main_layout.addWidget(line_edit)

button_layout = QHBoxLayout()

button_layout.addWidget(save_button)
button_layout.addWidget(cancel_button)

main_layout.addLayout(button_layout)
```

Đây chính là **nested layout**.

---

# 7. `addLayout()`

Đây là method rất quan trọng.

```python
main_layout.addLayout(button_layout)
```

Ta đang đưa một layout vào layout khác.

Mental model:

```text
QVBoxLayout
│
├── QLabel
├── QLineEdit
└── QHBoxLayout
     ├── QPushButton
     └── QPushButton
```

---

# 8. `QGridLayout`

Dùng khi giao diện có dạng lưới.

```python
from PySide6.QtWidgets import QGridLayout
```

Ví dụ:

```text
┌───────────────────────────────┐
│ Name:     [_______________]   │
│ Email:    [_______________]   │
│ Password: [_______________]   │
│                               │
│             [ Login ]         │
└───────────────────────────────┘
```

Code:

```python
layout = QGridLayout()

layout.addWidget(name_label, 0, 0)
layout.addWidget(name_edit, 0, 1)

layout.addWidget(email_label, 1, 0)
layout.addWidget(email_edit, 1, 1)

layout.addWidget(password_label, 2, 0)
layout.addWidget(password_edit, 2, 1)
```

Cú pháp:

```python
addWidget(widget, row, column)
```

---

# 9. Row / Column

Ví dụ:

```text
       column
       0       1       2
    ┌───────┬───────┬───────┐
0   │ A     │ B     │ C     │
    ├───────┼───────┼───────┤
1   │ D     │ E     │ F     │
    ├───────┼───────┼───────┤
2   │ G     │ H     │ I     │
    └───────┴───────┴───────┘
```

Ví dụ:

```python
layout.addWidget(a, 0, 0)
layout.addWidget(b, 0, 1)
layout.addWidget(c, 0, 2)

layout.addWidget(d, 1, 0)
layout.addWidget(e, 1, 1)
layout.addWidget(f, 1, 2)
```

---

# 10. `QFormLayout`

Đặc biệt phù hợp với form.

```python
from PySide6.QtWidgets import QFormLayout
```

Ví dụ:

```python
layout = QFormLayout()

layout.addRow("Name:", name_edit)
layout.addRow("Email:", email_edit)
layout.addRow("Password:", password_edit)
```

Kết quả:

```text
┌────────────────────────────────┐
│ Name:      [_______________]   │
│ Email:     [_______________]   │
│ Password:  [_______________]   │
└────────────────────────────────┘
```

Nếu làm:

* Login
* Register
* Settings
* User profile
* Configuration

thì `QFormLayout` rất tiện.

---

# 11. So sánh 4 layout

| Layout        | Mục đích         |
| ------------- | ---------------- |
| `QVBoxLayout` | Xếp dọc          |
| `QHBoxLayout` | Xếp ngang        |
| `QGridLayout` | Dạng lưới        |
| `QFormLayout` | Form label/value |

Mental model:

```text
VBox
A
B
C

HBox
A B C

Grid
A B C
D E F
G H I

Form
A: [ ]
B: [ ]
C: [ ]
```

---

# 12. `addStretch()`

Đây là một trong những API layout quan trọng nhất.

Ví dụ:

```python
layout = QVBoxLayout()

layout.addWidget(button1)
layout.addWidget(button2)
layout.addStretch()
```

Kết quả:

```text
┌─────────────────────┐
│ [Button 1]          │
│ [Button 2]          │
│                     │
│                     │
│                     │
└─────────────────────┘
```

Stretch ăn phần không gian còn dư.

---

# 13. Stretch để đẩy widget xuống dưới

Ví dụ:

```text
┌─────────────────────────┐
│ Content                 │
│                         │
│                         │
│                         │
│ [Cancel] [Save]         │
└─────────────────────────┘
```

Code:

```python
layout.addWidget(content)
layout.addStretch()
layout.addLayout(button_layout)
```

Mental model:

```text
Content
   ↓
Stretch
   ↓
Buttons
```

Stretch hấp thụ phần không gian dư.

---

# 14. `addStretch()` trong HBox

Ví dụ muốn:

```text
┌──────────────────────────────────┐
│ [Back]                 [Save]     │
└──────────────────────────────────┘
```

Code:

```python
layout = QHBoxLayout()

layout.addWidget(back_button)
layout.addStretch()
layout.addWidget(save_button)
```

Đây là pattern cực kỳ phổ biến.

---

# 15. Stretch Factor

Ta có thể truyền factor:

```python
layout.addStretch(1)
```

hoặc:

```python
layout.addStretch(2)
```

Stretch factor quyết định tỷ lệ không gian.

Ví dụ:

```python
layout.addStretch(1)
layout.addStretch(2)
```

Nếu có 300 px dư:

```text
Stretch 1 → 100 px
Stretch 2 → 200 px
```

Tỷ lệ:

```text
1 : 2
```

---

# 16. `addWidget()` với stretch

`QBoxLayout` còn cho phép:

```python
layout.addWidget(widget, stretch=1)
```

Ví dụ:

```python
layout.addWidget(left, 1)
layout.addWidget(right, 2)
```

Không gian:

```text
┌───────────────┬────────────────────────┐
│               │                        │
│     left      │         right          │
│               │                        │
└───────────────┴────────────────────────┘
       1                  2
```

---

# 17. Margin

Layout có:

```python
layout.setContentsMargins(
    left,
    top,
    right,
    bottom,
)
```

Ví dụ:

```python
layout.setContentsMargins(20, 20, 20, 20)
```

Nếu không có margin:

```text
┌────────────────────┐
│Widget              │
└────────────────────┘
```

Có margin:

```text
┌────────────────────┐
│  ┌──────────────┐  │
│  │ Widget       │  │
│  └──────────────┘  │
└────────────────────┘
```

---

# 18. `spacing`

Spacing là khoảng cách **giữa các item**.

```python
layout.setSpacing(10)
```

Ví dụ:

```text
Button
   ↓ 10px
Button
   ↓ 10px
Button
```

Phân biệt:

```text
Margin
= khoảng cách từ layout đến biên

Spacing
= khoảng cách giữa các item
```

---

# 19. Margin vs Spacing

```text
┌──────────────────────────────┐
│ ← margin →                   │
│   Button                     │
│      ↕ spacing               │
│   Button                     │
│                              │
└──────────────────────────────┘
```

Đây là lỗi rất phổ biến khi căn UI.

---

# 20. `QSizePolicy`

Bây giờ bắt đầu phần quan trọng hơn.

Widget không chỉ có:

```text
width
height
```

Nó còn có **size policy**.

```python
widget.sizePolicy()
```

Qt cần biết:

> Widget này muốn kích thước như thế nào khi không gian thay đổi?

---

# 21. Các policy chính

`QSizePolicy` có các policy quan trọng:

```text
Fixed
Minimum
Maximum
Preferred
Expanding
MinimumExpanding
Ignored
```

Trong thực tế, đặc biệt quan trọng:

```text
Fixed
Preferred
Expanding
MinimumExpanding
```

---

# 22. `Fixed`

Widget muốn giữ kích thước cố định.

```python
policy.setHorizontalPolicy(
    QSizePolicy.Policy.Fixed
)
```

Ví dụ:

```text
[ OK ]
```

nút không muốn mở rộng theo chiều ngang.

---

# 23. `Expanding`

Widget muốn chiếm thêm không gian nếu có.

Ví dụ:

```text
┌────────────────────────────────────┐
│ [ Search________________________ ] │
└────────────────────────────────────┘
```

Search box thường phù hợp với:

```text
Expanding
```

---

# 24. `Preferred`

Widget thích kích thước tự nhiên của nó nhưng có thể lớn hơn nếu layout cần.

Đây là policy thường khá phù hợp cho nhiều widget thông thường.

---

# 25. `MinimumExpanding`

Widget muốn mở rộng nhưng vẫn có kích thước tối thiểu.

---

# 26. Ví dụ Search Box

```python
from PySide6.QtWidgets import (
    QLineEdit,
    QSizePolicy,
)
```

Có thể:

```python
search = QLineEdit()

search.setSizePolicy(
    QSizePolicy.Policy.Expanding,
    QSizePolicy.Policy.Fixed,
)
```

Nghĩa:

```text
Horizontal → Expanding
Vertical   → Fixed
```

Kết quả:

```text
┌──────────────────────────────────────┐
│ [ Search___________________________ ] │
└──────────────────────────────────────┘
```

Chiều ngang co giãn.

Chiều dọc không cần co giãn.

---

# 27. `setFixedWidth()` vs Size Policy

Bạn có thể:

```python
widget.setFixedWidth(200)
```

nhưng đây là một ràng buộc mạnh.

Nếu bạn muốn:

> "Tôi muốn widget có kích thước hợp lý nhưng vẫn thích nghi."

thì thường nên nghĩ đến:

```text
Size Policy
Minimum Size
Maximum Size
Stretch
```

thay vì `setFixedSize()` khắp nơi.

---

# 28. `sizeHint()`

Widget có:

```python
widget.sizeHint()
```

Đây là kích thước mà widget **cho rằng phù hợp** với nội dung/trạng thái hiện tại.

Ví dụ button:

```python
button.sizeHint()
```

có thể cho một `QSize`.

Mental model:

```text
Widget
  │
  └── sizeHint()
         ↓
   "Tôi nghĩ kích thước tự nhiên của tôi nên khoảng thế này."
```

---

# 29. `minimumSizeHint()`

Widget còn có:

```python
widget.minimumSizeHint()
```

Nó đại diện cho kích thước nhỏ nhất mà widget cho rằng vẫn hợp lý.

Ví dụ:

```python
print(button.sizeHint())
print(button.minimumSizeHint())
```

---

# 30. Layout không chỉ nhìn `sizeHint()`

Đây là mental model quan trọng:

```text
Layout calculation
      │
      ├── sizeHint()
      ├── minimumSizeHint()
      ├── minimumSize
      ├── maximumSize
      ├── sizePolicy
      ├── stretch
      ├── margins
      └── spacing
```

Qt kết hợp nhiều yếu tố để quyết định kích thước cuối cùng.

---

# 31. `setMinimumSize()`

Ví dụ:

```python
widget.setMinimumSize(200, 100)
```

Nghĩa:

```text
width  >= 200
height >= 100
```

---

# 32. `setMaximumSize()`

```python
widget.setMaximumSize(800, 600)
```

Nghĩa:

```text
width  <= 800
height <= 600
```

---

# 33. `setFixedSize()`

```python
widget.setFixedSize(300, 200)
```

tương đương tư duy:

```text
minimum = 300 × 200
maximum = 300 × 200
```

Tức là không được co giãn.

Đây là lý do không nên lạm dụng.

---

# 34. Một ví dụ thực tế

Giả sử có:

```text
┌────────────────────────────────────┐
│ Search: [____________________]     │
│                                    │
│ [Cancel]              [Search]     │
└────────────────────────────────────┘
```

Ta muốn:

```text
Search box → Expanding
Cancel     → Fixed / Preferred
Search     → Fixed / Preferred
```

Layout:

```text
Main VBox
│
├── Search HBox
│    ├── QLabel
│    └── QLineEdit Expanding
│
├── Stretch
│
└── Buttons HBox
     ├── Stretch
     ├── Cancel
     └── Search
```

Đây là cách thiết kế tốt hơn việc đặt:

```python
setGeometry(...)
```

---

# 35. Một ví dụ hoàn chỉnh

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Layout Demo")
        self.resize(700, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")

        search_edit = QLineEdit()
        search_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        search_layout.addWidget(search_label)
        search_layout.addWidget(search_edit)

        main_layout.addLayout(search_layout)

        main_layout.addStretch()

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        search_button = QPushButton("Search")

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(search_button)

        main_layout.addLayout(button_layout)


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())
```

Kiến trúc layout:

```text
Window
│
└── QVBoxLayout
    │
    ├── QHBoxLayout
    │   ├── QLabel
    │   └── QLineEdit
    │
    ├── Stretch
    │
    └── QHBoxLayout
        ├── Stretch
        ├── Cancel
        └── Search
```

---

# 36. Vì sao layout này tốt?

Khi resize:

```text
700 × 400
```

thành:

```text
1200 × 700
```

Search box tự mở rộng.

Buttons vẫn ở phía dưới bên phải.

Không cần tính:

```text
x
y
width
height
```

---

# 37. `QSpacerItem`

Ngoài:

```python
layout.addStretch()
```

Qt còn có:

```python
QSpacerItem
```

Ví dụ:

```python
from PySide6.QtWidgets import (
    QSpacerItem,
    QSizePolicy,
)
```

Tuy nhiên trong phần lớn layout thông thường:

```python
layout.addStretch()
```

dễ đọc và tiện hơn.

---

# 38. Một nguyên tắc rất quan trọng

Đừng thiết kế UI theo:

> "Widget này phải ở tọa độ x=100, y=50."

Hãy thiết kế theo:

> "Widget A nằm bên trái widget B, widget C chiếm phần không gian còn lại."

Tức là:

```text
Imperative positioning
        ↓
"Đặt widget ở đây"
```

so với:

```text
Declarative layout relationship
        ↓
"A nằm cạnh B"
"C chiếm phần dư"
```

Layout system mạnh chính vì cách tư duy thứ hai.

---

# 39. Những lỗi người mới thường mắc

### Lỗi 1 — `setGeometry()` quá nhiều

```python
button.setGeometry(...)
label.setGeometry(...)
input.setGeometry(...)
```

Không phù hợp với UI responsive.

---

### Lỗi 2 — `setFixedSize()` khắp nơi

Ví dụ:

```python
button.setFixedSize(200, 50)
```

cho mọi widget.

UI sẽ rất khó thích nghi.

---

### Lỗi 3 — Dùng stretch thay cho mọi thứ

Stretch rất mạnh nhưng không nên dùng bừa.

---

### Lỗi 4 — Nhầm margin và spacing

```text
margin  ≠ spacing
```

---

### Lỗi 5 — Không hiểu Size Policy

Đây là nguyên nhân rất nhiều UI "tự co giãn kỳ lạ".

---

# 40. Mental Model quan trọng nhất hôm nay

Khi Qt layout một widget, hãy nghĩ:

```text
             Layout Engine
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
  sizeHint    SizePolicy   Constraints
       │          │          │
       └──────────┼──────────┘
                  ↓
             Final Geometry
```

Và toàn bộ layout:

```text
Window
   │
   ▼
Layout
   │
   ├── Widget
   ├── Widget
   ├── Nested Layout
   └── Stretch
```

---

# Bài tập Buổi 5

## Bài 1 — Login Form

Tạo:

```text
┌─────────────────────────────────────┐
│              Login                  │
│                                     │
│ Username: [______________________]  │
│ Password: [______________________]  │
│                                     │
│                  [Cancel] [Login]   │
└─────────────────────────────────────┘
```

Yêu cầu:

* `QFormLayout` cho username/password.
* `QHBoxLayout` cho buttons.
* Button nằm bên phải.
* Form có margin.
* Resize cửa sổ thì `QLineEdit` tự mở rộng.

---

## Bài 2 — Settings UI

Thiết kế:

```text
┌──────────────────────────────────────┐
│ Settings                             │
│                                      │
│ Language: [English ▼]                │
│ Theme:    [Dark ▼]                   │
│ Font:     [14       ]                │
│                                      │
│                         [Save]        │
└──────────────────────────────────────┘
```

Sử dụng:

* `QFormLayout`
* `QComboBox`
* `QSpinBox`
* `QHBoxLayout`
* `addStretch()`

---

## Bài 3 — Dashboard

Tạo:

```text
┌─────────────────────────────────────────────┐
│ Header                                      │
├─────────────────────────────────────────────┤
│                                             │
│ Main Content                                │
│                                             │
├─────────────────────────────────────────────┤
│ Status                         [Start]      │
└─────────────────────────────────────────────┘
```

Gợi ý:

```text
QVBoxLayout
│
├── Header
├── Stretch
├── Content
├── Stretch
└── Footer
```

---

# Bài tập Deep Dive

Viết chương trình thử nghiệm:

```python
print(widget.sizeHint())
print(widget.minimumSizeHint())
print(widget.sizePolicy())
print(widget.minimumSize())
print(widget.maximumSize())
```

Sau đó thay đổi:

```python
setMinimumSize()
setMaximumSize()
setFixedSize()
setSizePolicy()
```

và quan sát sự thay đổi.

Đây là bài tập **rất đáng làm**, bởi vì mục tiêu của khóa học không phải nhớ API mà là hiểu:

> **Tại sao Qt quyết định widget này rộng bao nhiêu?**

---

## Buổi 6 — Widget Foundation

Tiếp theo chúng ta sẽ đi sâu vào nhóm widget cơ bản:

```text
QLabel
QPushButton
QLineEdit
QTextEdit
QPlainTextEdit
QCheckBox
QRadioButton
QComboBox
QSpinBox
QDoubleSpinBox
```

Nhưng sẽ không học kiểu "đây là widget, đây là method".

Ta sẽ tập trung vào **state, property, signal, interaction và cách kết hợp chúng thành một form thực tế**.
