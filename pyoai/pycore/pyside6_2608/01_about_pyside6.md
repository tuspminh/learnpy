
# Bắt đầu — Buổi 1

## PySide6 là gì?

PySide6 là **Python binding cho Qt 6**.

Có thể hình dung:

```text
Python
   │
   ▼
PySide6
   │
   ▼
Qt 6
   │
   ├── Window
   ├── Widget
   ├── Event
   ├── Thread
   ├── Network
   ├── File System
   ├── Model/View
   └── GUI
```

Điểm quan trọng:

> **PySide6 không phải một GUI framework được viết hoàn toàn bằng Python.**

Phần lớn hệ thống GUI nằm phía Qt/C++.

Python gọi vào Qt thông qua PySide6.

---

## Chương trình PySide6 tối thiểu

```python
import sys

from PySide6.QtWidgets import QApplication, QWidget


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Hello PySide6")
window.resize(800, 600)
window.show()

sys.exit(app.exec())
```

Đừng vội học `QPushButton`.

Trước tiên phải hiểu **5 dòng quan trọng nhất**:

```python
app = QApplication(sys.argv)
```

```python
window = QWidget()
```

```python
window.show()
```

```python
app.exec()
```

```python
sys.exit(...)
```

---

# 1. `QApplication`

```python
app = QApplication(sys.argv)
```

`QApplication` là đối tượng đại diện cho **GUI application**.

Nó chịu trách nhiệm cho nhiều thứ quan trọng:

```text
Application
    │
    ├── Event loop
    ├── Window management
    ├── Input events
    ├── Clipboard
    ├── Fonts
    ├── Style
    └── Application state
```

Một ứng dụng GUI PySide6 thông thường sẽ có **một `QApplication`**.

---

# 2. `QWidget`

```python
window = QWidget()
```

`QWidget` là class nền tảng của hệ thống widget.

Rất nhiều widget kế thừa từ nó:

```text
QObject
   │
   └── QWidget
        │
        ├── QPushButton
        ├── QLabel
        ├── QLineEdit
        ├── QTextEdit
        ├── QCheckBox
        ├── QComboBox
        └── ...
```

Do đó:

```python
window = QWidget()
```

có nghĩa:

> Tạo một widget có thể đóng vai trò như một cửa sổ.

---

# 3. `show()`

```python
window.show()
```

Chỉ tạo object:

```python
window = QWidget()
```

**chưa đảm bảo cửa sổ xuất hiện trên màn hình.**

Ta phải yêu cầu Qt hiển thị nó:

```python
window.show()
```

---

# 4. Event Loop

Đây là khái niệm **cực kỳ quan trọng**.

```python
app.exec()
```

khởi động event loop.

Có thể hình dung:

```text
                 ┌──────────────────┐
                 │    Event Loop     │
                 └────────┬─────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Mouse        Keyboard      Timer
           Event         Event        Event
             │            │            │
             └────────────┼────────────┘
                          ▼
                       Qt xử lý
                          │
                          ▼
                       UI update
```

Ví dụ người dùng click:

```text
User click
    ↓
Operating System
    ↓
Qt Event System
    ↓
Event Loop
    ↓
Widget
    ↓
Signal
    ↓
Slot / Callback
```

Đây chính là nền móng để sau này hiểu:

* Signal/Slot
* `QTimer`
* `QThread`
* GUI freeze
* asynchronous programming
* worker
* event-driven architecture

---

# 5. Vì sao phải có Event Loop?

Xem chương trình Python bình thường:

```python
print("Hello")

x = 10

print(x)
```

Python chạy tuần tự:

```text
print
 ↓
x = 10
 ↓
print
 ↓
END
```

GUI thì khác.

Chương trình phải **tiếp tục sống và chờ sự kiện**:

```text
start
  ↓
create window
  ↓
show window
  ↓
┌───────────────────┐
│    EVENT LOOP     │
│                   │
│  wait for event   │
│        ↓          │
│  process event    │
│        ↓          │
│  update UI        │
│        ↓          │
│  wait again       │
└───────────────────┘
  ↓
application quit
```

Do đó:

```python
app.exec()
```

không phải là một lệnh "chờ cho vui".

Nó là **trái tim của ứng dụng GUI**.

---

# Một thí nghiệm rất quan trọng

Thử:

```python
import sys

from PySide6.QtWidgets import QApplication, QWidget


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Test")
window.resize(800, 600)
window.show()

print("Before exec")

app.exec()

print("After exec")
```

Khi chạy:

```text
Before exec
```

xuất hiện ngay.

Nhưng:

```text
After exec
```

**chỉ xuất hiện sau khi bạn đóng cửa sổ.**

Điều này cho thấy:

```python
app.exec()
```

giữ chương trình bên trong event loop.

---

# Một mental model cần nhớ

Đừng nghĩ:

```text
PySide6 = tạo cửa sổ
```

Hãy nghĩ:

```text
PySide6
   │
   ▼
Event-driven application
   │
   ▼
Event Loop
   │
   ├── Mouse
   ├── Keyboard
   ├── Timer
   ├── Window
   ├── Network
   └── Custom Events
```

Và:

```text
Widget
   ↓
Event
   ↓
Signal
   ↓
Slot
   ↓
State change
   ↓
UI update
```

Đây sẽ là **mental model xuyên suốt toàn bộ khóa học**.

---

# Bài tập Buổi 1

### Bài 1

Tạo cửa sổ:

* tiêu đề: `PySide6 Learning`
* kích thước: `1000 × 700`

### Bài 2

Thử bỏ:

```python
window.show()
```

và quan sát.

### Bài 3

Thử bỏ:

```python
app.exec()
```

và quan sát.

### Bài 4 — quan trọng

Viết chương trình:

```text
Before window
Before event loop
[Window xuất hiện]
After event loop
```

và giải thích **tại sao thứ tự output lại như vậy**.

---

Ở **Buổi 2**, ta sẽ đi sâu vào một trong những nền tảng quan trọng nhất của PySide6:

> **`QObject` + Parent/Child + Object Tree + Lifetime Management**

Đây là phần rất đáng học kỹ, vì nó giải thích tại sao Qt có cách quản lý object khác với Python thuần túy.
