# Buổi 2 — `QObject`, Parent/Child và Object Tree

Ở Buổi 1, ta đã có mental model:

```text
PySide6
   ↓
Qt Application
   ↓
Event Loop
   ↓
Widget
   ↓
Event / Signal / Slot
```

Hôm nay chúng ta đi xuống **một tầng sâu hơn**:

```text
QObject
   ↓
Parent / Child
   ↓
Object Tree
   ↓
Lifetime Management
```

Đây là kiến thức **rất quan trọng**. Nếu hiểu `QObject` tốt, sau này học `Signal/Slot`, `QThread`, `QTimer`, Model/View... sẽ dễ hơn rất nhiều.

---

# 1. `QObject` là gì?

`QObject` là một trong những class nền tảng nhất của Qt.

Rất nhiều class Qt kế thừa từ `QObject`.

Ví dụ:

```text
QObject
│
├── QWidget
│   ├── QPushButton
│   ├── QLabel
│   ├── QLineEdit
│   └── QMainWindow
│
├── QTimer
├── QThread
├── QAbstractItemModel
└── ...
```

Điều này có nghĩa:

```python
from PySide6.QtCore import QObject
```

ta có thể tạo:

```python
obj = QObject()
```

`QObject` không phải widget.

Nó là một **Qt object** có khả năng tham gia vào hệ thống object của Qt.

---

# 2. Python object và Qt object

Đây là điểm rất quan trọng.

Trong Python:

```python
class Person:
    pass


person = Person()
```

Python quản lý object bằng cơ chế của Python.

Ví dụ:

```text
Python
   │
   └── person
         ↓
       Person object
```

Trong Qt, ngoài Python reference còn có một hệ thống **Parent/Child**.

```text
Qt Object Tree

parent
 ├── child
 ├── child
 │    └── grandchild
 └── child
```

Đây là một trong những đặc điểm quan trọng nhất của Qt.

---

# 3. Parent / Child

Ta có thể tạo:

```python
from PySide6.QtCore import QObject


parent = QObject()
child = QObject(parent)
```

Ở đây:

```text
parent
   │
   └── child
```

`child` có `parent` là `parent`.

Có thể kiểm tra:

```python
print(child.parent())
```

Kết quả sẽ là object `parent`.

---

# 4. Constructor của `QObject`

Constructor của `QObject` có thể nhận `parent`.

Ví dụ:

```python
child = QObject(parent)
```

tương đương về ý nghĩa với:

```python
child = QObject()
child.setParent(parent)
```

Sau khi gọi:

```python
child.setParent(parent)
```

ta có:

```text
parent
   │
   └── child
```

---

# 5. Object Tree

Qt xây dựng một cây object.

Ví dụ:

```python
from PySide6.QtCore import QObject


app_object = QObject()

a = QObject(app_object)
b = QObject(app_object)

c = QObject(a)
d = QObject(a)
e = QObject(b)
```

Cây:

```text
app_object
│
├── a
│   ├── c
│   └── d
│
└── b
    └── e
```

Đây gọi là:

> **QObject tree / Object tree**

---

# 6. Xem children

QObject có:

```python
children()
```

Ví dụ:

```python
from PySide6.QtCore import QObject


parent = QObject()

child1 = QObject(parent)
child2 = QObject(parent)

print(parent.children())
```

Ta sẽ nhận được danh sách các child.

Có thể duyệt:

```python
for child in parent.children():
    print(child)
```

---

# 7. `findChild()`

Qt còn cho phép tìm object con.

Ví dụ:

```python
child = QObject(parent)
child.setObjectName("my_child")
```

Sau đó:

```python
found = parent.findChild(QObject, "my_child")

print(found)
```

Điều này cực kỳ hữu ích khi làm UI phức tạp.

---

# 8. `objectName`

QObject có thuộc tính:

```python
objectName()
```

và:

```python
setObjectName()
```

Ví dụ:

```python
button.setObjectName("saveButton")
```

Sau đó:

```python
print(button.objectName())
```

Kết quả:

```text
saveButton
```

`objectName` sau này đặc biệt hữu ích với:

* Qt Designer
* tìm widget
* debugging
* QSS
* UI architecture

Ví dụ QSS:

```css
QPushButton#saveButton {
    font-weight: bold;
}
```

Ở đây:

```text
QPushButton
     +
objectName = saveButton
     ↓
QPushButton#saveButton
```

---

# 9. Parent của Widget

Bây giờ chuyển sang widget.

Ví dụ:

```python
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
import sys


app = QApplication(sys.argv)

window = QWidget()
button = QPushButton("Save", window)

window.show()

sys.exit(app.exec())
```

Ta có:

```text
window
   │
   └── button
```

Vì:

```python
button = QPushButton("Save", window)
```

đã truyền:

```python
window
```

làm parent.

---

# 10. Tại sao Parent/Child quan trọng?

Có hai lý do lớn:

### 1. Quản lý lifetime

### 2. Quản lý quan hệ giữa các object

Ví dụ:

```text
window
│
├── button1
├── button2
├── label
└── input
```

Khi `window` bị destroy, các child Qt object cũng được xử lý theo object tree.

Đây là một cơ chế rất quan trọng của Qt.

---

# 11. Một hiểu lầm thường gặp

Có thể bạn sẽ nghĩ:

> "Python có garbage collector rồi, tại sao Qt cần Parent/Child?"

Đây là câu hỏi rất hay.

Python quản lý:

```text
Python object lifetime
```

Qt quản lý:

```text
Qt object ownership / object tree
```

Hai hệ thống này **không hoàn toàn giống nhau**.

PySide6 là binding giữa:

```text
Python
   ↕
C++ / Qt
```

Do đó chúng ta có thể đồng thời có:

```text
Python reference
```

và:

```text
Qt parent-child relationship
```

Đây là lý do lifetime trong PySide6 cần được hiểu kỹ.

---

# 12. Ví dụ với widget

```python
window = QWidget()

button = QPushButton("Hello", window)
```

Python có reference:

```text
button
   ↓
Python wrapper
   ↓
C++ QPushButton
```

Qt lại có:

```text
window
   │
   └── button
```

Cho nên ta không nên chỉ nhìn PySide6 như Python thuần túy.

---

# 13. Parent không nhất thiết là container trực quan

Một hiểu lầm khác:

> Parent không đơn giản chỉ có nghĩa là "widget cha đang chứa widget con".

Nó là **ownership relationship của QObject**.

Ví dụ:

```python
timer = QTimer(parent)
```

`parent` ở đây không nhất thiết là widget chứa timer.

Nó có thể chỉ đơn giản là object chịu trách nhiệm quản lý lifetime của timer.

Ví dụ:

```python
from PySide6.QtCore import QObject, QTimer


controller = QObject()

timer = QTimer(controller)
```

Object tree:

```text
controller
   │
   └── timer
```

---

# 14. Parent có thể là non-widget

Đây là điểm rất quan trọng.

Không phải:

```text
Widget
 └── Widget
```

mà có thể:

```text
QObject
 ├── QTimer
 ├── QObject
 └── Worker
```

Ví dụ:

```python
from PySide6.QtCore import QObject, QTimer


class Worker(QObject):
    pass


controller = QObject()
worker = Worker(controller)
timer = QTimer(controller)
```

Cây:

```text
controller
├── worker
└── timer
```

Sau này khi học threading, mô hình này sẽ xuất hiện rất nhiều.

---

# 15. `setParent()`

Ta có thể thay đổi parent:

```python
parent1 = QObject()
parent2 = QObject()

child = QObject(parent1)

child.setParent(parent2)
```

Ban đầu:

```text
parent1
   └── child
```

Sau:

```text
parent1

parent2
   └── child
```

Kiểm tra:

```python
print(child.parent() is parent2)
```

Kết quả:

```text
True
```

---

# 16. `parent()` và `children()`

Hai API rất quan trọng:

```python
obj.parent()
```

và:

```python
obj.children()
```

Chúng cho phép đi trong object tree.

Ví dụ:

```python
parent = QObject()

child1 = QObject(parent)
child2 = QObject(parent)
```

Ta có thể:

```python
print(child1.parent() is parent)
```

và:

```python
print(len(parent.children()))
```

---

# 17. `isWidgetType()`

QObject còn có:

```python
obj.isWidgetType()
```

Ví dụ:

```python
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject

widget = QWidget()
obj = QObject()

print(widget.isWidgetType())
print(obj.isWidgetType())
```

Kết quả:

```text
True
False
```

Điều này hữu ích khi debugging object tree.

---

# 18. `deleteLater()`

Một API rất đáng chú ý:

```python
obj.deleteLater()
```

Ví dụ:

```python
timer.deleteLater()
```

Nó yêu cầu Qt xóa object vào thời điểm an toàn thông qua event loop.

Đừng hiểu đơn giản:

```python
deleteLater()
```

= Python:

```python
del obj
```

Hai khái niệm này khác nhau.

---

# 19. `del` không phải là Qt deletion

Ví dụ:

```python
obj = QObject()
del obj
```

`del` chỉ xóa **Python reference**.

Nó không nên được hiểu là:

> "Tôi vừa trực tiếp destroy C++ QObject."

Trong PySide6, lifetime có thể liên quan đến:

```text
Python reference
        +
Qt parent
        +
C++ object lifetime
```

Đây là lý do khi làm ứng dụng lớn, cần hiểu ownership thay vì chỉ dựa vào `del`.

---

# 20. Signal `destroyed`

QObject có signal:

```python
destroyed
```

Ví dụ:

```python
from PySide6.QtCore import QObject


obj = QObject()

obj.destroyed.connect(
    lambda: print("Object destroyed")
)
```

Signal này sẽ phát khi QObject bị destroy.

Sau này chúng ta sẽ học Signal/Slot một cách đầy đủ.

Hiện tại chỉ cần biết:

```text
QObject
   │
   └── destroyed
```

---

# 21. Object Tree thực tế trong ứng dụng

Một ứng dụng có thể có cây như:

```text
QApplication
│
└── MainWindow
    │
    ├── CentralWidget
    │   ├── QLabel
    │   ├── QLineEdit
    │   └── QPushButton
    │
    ├── MenuBar
    │   ├── FileMenu
    │   └── EditMenu
    │
    └── StatusBar
```

Đây là mental model rất hữu ích.

---

# 22. Một ví dụ hoàn chỉnh

```python
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)


app = QApplication(sys.argv)

window = QWidget()
window.setObjectName("mainWindow")

layout = QVBoxLayout(window)

label = QLabel("Hello")
label.setObjectName("messageLabel")

button = QPushButton("Click")
button.setObjectName("clickButton")

layout.addWidget(label)
layout.addWidget(button)

window.show()

sys.exit(app.exec())
```

Điều thú vị là:

```python
layout = QVBoxLayout(window)
```

và:

```python
layout.addWidget(label)
layout.addWidget(button)
```

không nên được hiểu đơn giản là:

```text
Python list
```

Qt có hệ thống quản lý widget/layout riêng.

---

# 23. Object Tree vs Layout Tree

Đây là một distinction rất quan trọng.

Có:

### Layout hierarchy

```text
QVBoxLayout
├── QLabel
└── QPushButton
```

Nhưng đồng thời có:

### QObject hierarchy

```text
window
├── layout
├── label
└── button
```

Tùy API và loại object, quan hệ ownership cụ thể có thể khác nhau, nên **đừng đồng nhất layout với QObject parent**.

Đây là một trong những lỗi tư duy phổ biến khi mới học Qt.

---

# 24. Debug Object Tree

Bạn có thể dùng:

```python
print(window.children())
```

Hoặc:

```python
for child in window.children():
    print(
        type(child).__name__,
        child.objectName(),
    )
```

Ví dụ:

```text
QVBoxLayout 
QLabel messageLabel
QPushButton clickButton
```

Đây là kỹ thuật debugging rất hữu ích.

---

# 25. Một bài thực hành quan trọng

Hãy tạo:

```text
MainWindow
│
├── Header
│   ├── Title
│   └── RefreshButton
│
├── Content
│   ├── SearchBox
│   └── ResultLabel
│
└── Footer
    └── StatusLabel
```

Sau đó đặt `objectName`:

```text
mainWindow
header
titleLabel
refreshButton
content
searchBox
resultLabel
footer
statusLabel
```

Rồi viết code để in ra object tree.

---

# 26. Bài tập nâng cao

Viết hàm:

```python
def print_tree(obj, indent=0):
    ...
```

Sao cho:

```python
print_tree(window)
```

in ra:

```text
QWidget mainWindow
├── QWidget header
│   ├── QLabel titleLabel
│   └── QPushButton refreshButton
├── QWidget content
│   ├── QLineEdit searchBox
│   └── QLabel resultLabel
└── QWidget footer
    └── QLabel statusLabel
```

Bạn sẽ phải sử dụng:

```python
obj.children()
```

và đệ quy.

Đây là một bài tập rất tốt vì nó kết hợp:

* Python recursion
* `QObject`
* object tree
* `children()`
* `objectName()`
* introspection

---

# 27. Những điều cần nhớ sau Buổi 2

Nếu chỉ ghi nhớ 7 điểm, hãy ghi nhớ:

```text
1. QObject là nền tảng của Qt Object Model.

2. Nhiều class PySide6 kế thừa QObject.

3. QObject có thể có parent.

4. QObject có thể có nhiều children.

5. Parent/Child tạo thành Object Tree.

6. Qt sử dụng Object Tree cho ownership/lifetime management.

7. Python reference và Qt ownership là hai khái niệm cần phân biệt.
```

Mental model:

```text
                QObject
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
     Widget      Timer      Worker
        │
   ┌────┼────┐
   ↓    ↓    ↓
 Label Button Input
```

và:

```text
Parent
  │
  ├── Child
  │     └── Grandchild
  │
  └── Child
```

---

# Bài tập Buổi 2

**Bắt buộc:**

1. Tạo `QWidget` cha.
2. Tạo 3 `QObject` con.
3. Tạo một object cháu.
4. In `parent()`.
5. In `children()`.
6. Viết `print_tree()`.
7. Thử `setParent()`.
8. Thử `objectName`.
9. Thử `findChild()`.

**Câu hỏi kiểm tra tư duy:**

> Nếu Python biến mất reference tới một `QObject`, nhưng object đó vẫn có một Qt parent, chuyện gì có thể xảy ra với object đó?

Hãy tự trả lời câu này trước khi sang **Buổi 3 — Signal & Slot**. Đây là câu hỏi nền tảng để hiểu PySide6 thực sự khác GUI toolkit đơn giản như thế nào.
