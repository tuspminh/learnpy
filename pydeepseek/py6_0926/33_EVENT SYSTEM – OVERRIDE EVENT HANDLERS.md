# 📘 MODULE 3 – BÀI 3.3: EVENT SYSTEM – OVERRIDE EVENT HANDLERS

> **Mục tiêu bài học**:
> - Hiểu **bản chất** Event System trong Qt (khác Signal/Slot thế nào)
> - Nắm **vòng đời** của một event: OS → QApplication → Widget
> - Thành thạo override các **event handler** phổ biến: mouse, keyboard, paint, resize, close, focus
> - Hiểu **`accept()` vs `ignore()`** và cơ chế lan truyền
> - Biết **`event()` override** để "bắt tất cả"
> - Phân biệt **Signal** vs **Event** khi nào dùng cái nào
> - Xây dựng **Paint App** đơn giản dùng mouse events

---

## 🎯 PHẦN 1: EVENT LÀ GÌ? – GÓC NHÌN BẢN CHẤT

### 1.1. Định nghĩa

**Event** là một **gói dữ liệu** mô tả "điều gì đó đã xảy ra" với một `QObject`. Nó được OS, Qt, hoặc chính app phát ra và gửi đến đối tượng đích.

```
   ┌─────────┐         ┌──────────────┐         ┌─────────────┐
   │   OS    │ ──────▶ │ QApplication │ ──────▶ │   QWidget   │
   │ (chuột, │  Event  │   (event     │  Event  │  (xử lý     │
   │ bàn phím)│        │    loop)     │         │   event)    │
   └─────────┘         └──────────────┘         └─────────────┘
```

### 1.2. Signal vs Event – Nhắc lại (rất quan trọng)

| Tiêu chí | **Event** | **Signal** |
|----------|-----------|------------|
| Bản chất | Gói dữ liệu sự kiện (class `QEvent`) | Thông báo "có gì đó xảy ra" |
| Phát ra bởi | OS, Qt framework, `QApplication::sendEvent` | Code của bạn (`emit`) |
| Nhận bởi | Chỉ **1 widget đích** (hoặc filter) | **N slot** bất kỳ |
| Cách xử lý | Override `xxxEvent()` method | `.connect(slot)` |
| Có bubbling? | Có (ignore → parent) | Không |
| Ví dụ | `QMouseEvent`, `QKeyEvent`, `QPaintEvent` | `clicked`, `textChanged` |
| Tầng | **Thấp** (low-level) | **Cao** (high-level) |

### 1.3. Ví dụ minh họa

**Event**:
```python
class MyWidget(QWidget):
    def mousePressEvent(self, event: QMouseEvent):
        print(f"Click tại {event.position()}")
        super().mousePressEvent(event)      # Gọi mặc định
```

**Signal**:
```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.clicked.connect(self.on_click)  # QWidget không có clicked, đây là ví dụ
```

👉 **Quan hệ**: `QPushButton` khi nhận `QMouseEvent` → nó xử lý → **emit** signal `clicked`. Event ở tầng thấp, Signal ở tầng cao.

### 1.4. Cây phân cấp QEvent

```
QEvent (base)
├── QInputEvent
│   ├── QMouseEvent
│   ├── QKeyEvent
│   ├── QWheelEvent
│   ├── QTouchEvent
│   └── QTabletEvent
├── QPaintEvent
├── QResizeEvent
├── QMoveEvent
├── QShowEvent / QHideEvent
├── QCloseEvent
├── QFocusEvent
├── QEnterEvent
├── QDragEnterEvent / QDropEvent / ...
├── QTimerEvent
├── QContextMenuEvent
├── QHoverEvent (Qt 6)
├── QNativeGestureEvent
└── ... (rất nhiều)
```

Mỗi loại event có **method riêng** để override trong `QWidget`.

---

## 🎯 PHẦN 2: VÒNG ĐỜI CỦA MỘT EVENT

### 2.1. Flow đầy đủ khi user click chuột

```
1. OS phát hiện click
   ↓
2. OS gửi native message đến Qt
   ↓
3. QApplication nhận → tạo QMouseEvent
   ↓
4. QApplication gửi đến widget đích: QApplication::notify()
   ↓
5. Widget nhận qua event filter (nếu có)
   ↓
6. Widget.event(QEvent*) được gọi (method chung)
   ↓
7. `event()` phân loại → gọi mousePressEvent(QMouseEvent*)
   ↓
8. Nếu mousePressEvent gọi event->ignore() → gửi cho parent
   ↓
9. Nếu accept() (mặc định) → dừng
```

### 2.2. Hai cấp override

Có 2 cách can thiệp event:

| Cách | Method | Dùng khi |
|------|--------|----------|
| **Cấp 1** | `event(QEvent*)` | Muốn xử lý **mọi** event loại bất kỳ |
| **Cấp 2** | `mousePressEvent(QMouseEvent*)` | Chỉ quan tâm 1 loại event cụ thể |

Hầu hết bạn dùng **cấp 2**. Cấp 1 dùng khi bạn cần "bắt tất cả" hoặc custom event.

### 2.3. Event Filter – Cấp 3 (nâng cao)

Ngoài ra còn **event filter**: một object có thể **theo dõi** event của object khác.

```python
widget.installEventFilter(self)             # self sẽ nhận event của widget

def eventFilter(self, obj, event):
    if obj is widget and event.type() == QEvent.Type.MouseButtonPress:
        print("Bắt được event trước widget!")
        return True                          # True = chặn, không cho widget nhận
    return super().eventFilter(obj, event)
```

Chúng ta sẽ học event filter ở bài sau (3.4).

---

## 🎯 PHẦN 3: EVENT HANDLERS PHỔ BIẾN

### 3.1. Mouse Events

```python
def mousePressEvent(self, event: QMouseEvent):
    """Chuột vừa nhấn xuống."""
    if event.button() == Qt.MouseButton.LeftButton:
        print(f"Left click at {event.position()}")
    elif event.button() == Qt.MouseButton.RightButton:
        print(f"Right click at {event.position()}")
    super().mousePressEvent(event)

def mouseReleaseEvent(self, event: QMouseEvent):
    """Chuột nhả ra."""
    print(f"Release at {event.position()}")
    super().mouseReleaseEvent(event)

def mouseMoveEvent(self, event: QMouseEvent):
    """Chuột di chuyển (cần setMouseTracking(True) nếu không nhấn)."""
    print(f"Move: {event.position()}")
    super().mouseMoveEvent(event)

def mouseDoubleClickEvent(self, event: QMouseEvent):
    """Double click."""
    print("Double click!")
    super().mouseDoubleClickEvent(event)

def wheelEvent(self, event: QWheelEvent):
    """Cuộn chuột."""
    delta = event.angleDelta().y()           # 120 = 1 nấc lên, -120 = xuống
    print(f"Scroll: {delta}")
    super().wheelEvent(event)
```

### 3.2. Phương thức của QMouseEvent

```python
event.position()                              # QPointF vị trí so với widget
event.globalPosition()                        # QPointF vị trí trên toàn màn hình
event.button()                                # Nút nào vừa thay đổi
event.buttons()                               # Bitmask các nút đang nhấn
event.modifiers()                             # Ctrl/Shift/Alt
```

Ví dụ:

```python
def mousePressEvent(self, event):
    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
        print("Ctrl + Click")
    if event.button() == Qt.MouseButton.LeftButton:
        print("Left")
    super().mousePressEvent(event)
```

⚠️ **Lưu ý Qt6**: `event.pos()` đã **bị xóa**, thay bằng `event.position()` (trả `QPointF`, không phải `QPoint`).

### 3.3. Keyboard Events

```python
def keyPressEvent(self, event: QKeyEvent):
    """Phím được nhấn."""
    key = event.key()
    text = event.text()
    mods = event.modifiers()
    
    if key == Qt.Key.Key_Escape:
        print("Escape")
    elif key == Qt.Key.Key_Return:
        print("Enter")
    elif key == Qt.Key.Key_A and mods & Qt.KeyboardModifier.ControlModifier:
        print("Ctrl+A")
    elif text:
        print(f"Gõ: {text}")
    
    super().keyPressEvent(event)

def keyReleaseEvent(self, event: QKeyEvent):
    """Phím nhả ra."""
    super().keyReleaseEvent(event)
```

**Bảng key quan trọng**:

| Key | Enum |
|-----|------|
| Enter | `Qt.Key.Key_Return` hoặc `Key_Enter` |
| Escape | `Qt.Key.Key_Escape` |
| Space | `Qt.Key.Key_Space` |
| Tab | `Qt.Key.Key_Tab` |
| F1-F12 | `Qt.Key.Key_F1` ... `Key_F12` |
| Mũi tên | `Key_Left`, `Key_Right`, `Key_Up`, `Key_Down` |
| Delete/Backspace | `Key_Delete`, `Key_Backspace` |

### 3.4. Paint Event – Vẽ

```python
def paintEvent(self, event: QPaintEvent):
    """Được gọi khi widget cần vẽ lại."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    painter.setPen(QColor("red"))
    painter.drawLine(0, 0, self.width(), self.height())
```

⚠️ **KHÔNG** gọi `super().paintEvent(event)` nếu muốn vẽ hoàn toàn tùy chỉnh. **KHÔNG** vẽ ngoài `paintEvent`.

### 3.5. Resize & Move Events

```python
def resizeEvent(self, event: QResizeEvent):
    """Widget đổi kích thước."""
    old = event.oldSize()
    new = event.size()
    print(f"{old} → {new}")
    super().resizeEvent(event)

def moveEvent(self, event: QMoveEvent):
    """Widget đổi vị trí (khi là top-level hoặc child)."""
    print(f"Vị trí: {event.pos()}")
    super().moveEvent(event)
```

### 3.6. Show & Hide Events

```python
def showEvent(self, event: QShowEvent):
    """Widget được hiển thị."""
    print("Show!")
    super().showEvent(event)

def hideEvent(self, event: QHideEvent):
    """Widget bị ẩn."""
    print("Hide!")
    super().hideEvent(event)
```

### 3.7. Close Event

```python
def closeEvent(self, event: QCloseEvent):
    """Người dùng đóng cửa sổ."""
    reply = QMessageBox.question(
        self, "Xác nhận", "Bạn có chắc muốn đóng?"
    )
    if reply == QMessageBox.StandardButton.Yes:
        event.accept()
    else:
        event.ignore()
```

### 3.8. Focus Events

```python
def focusInEvent(self, event: QFocusEvent):
    """Widget nhận focus."""
    self.setStyleSheet("border: 2px solid blue;")
    super().focusInEvent(event)

def focusOutEvent(self, event: QFocusEvent):
    """Widget mất focus."""
    self.setStyleSheet("")
    super().focusOutEvent(event)
```

Để widget nhận focus, cần:

```python
widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
widget.setFocus()                            # Đặt focus programmatically
```

Focus policy:

| Policy | Nhận focus khi |
|--------|---------------|
| `NoFocus` | Không bao giờ |
| `TabFocus` | Nhấn Tab |
| `ClickFocus` | Click chuột |
| `StrongFocus` | Tab + Click (mặc định cho nhiều widget) |
| `WheelFocus` | Strong + cuộn chuột |

### 3.9. Enter & Leave Events (Hover)

```python
def enterEvent(self, event: QEnterEvent):
    """Chuột đi vào widget."""
    self.setStyleSheet("background: lightblue;")
    super().enterEvent(event)

def leaveEvent(self, event: QEvent):
    """Chuột rời widget."""
    self.setStyleSheet("")
    super().leaveEvent(event)
```

**Phân biệt**:
- `enterEvent` / `leaveEvent`: chuột vào/ra widget
- `QEvent.HoverMove`: cần `setAttribute(Qt.WA_Hover)`

### 3.10. Context Menu Event (chuột phải)

```python
def contextMenuEvent(self, event: QContextMenuEvent):
    """Chuột phải hoặc phím Menu."""
    menu = QMenu(self)
    menu.addAction("Copy", self.copy)
    menu.addAction("Paste", self.paste)
    menu.addSeparator()
    menu.addAction("Xóa", self.delete)
    menu.exec(event.globalPos())
```

### 3.11. Drag & Drop Events (giới thiệu)

```python
def dragEnterEvent(self, event: QDragEnterEvent):
    """Bắt đầu kéo vào."""
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dropEvent(self, event: QDropEvent):
    """Thả."""
    for url in event.mimeData().urls():
        print(f"File: {url.toLocalFile()}")
    event.acceptProposedAction()
```

Chi tiết drag & drop sẽ ở bài sau.

---

## 🎯 PHẦN 4: ACCEPT VS IGNORE – LAN TRUYỀN EVENT

### 4.1. Nguyên tắc

- Mọi event **mặc định là accepted**
- Nếu bạn gọi `event.ignore()` → Qt gửi event cho **parent widget**
- Nếu parent cũng ignore → tiếp tục lên trên
- Nếu đến top-level mà vẫn ignore → event bị bỏ

### 4.2. Ví dụ minh họa

```python
class ChildWidget(QWidget):
    def mousePressEvent(self, event):
        print("Child nhận click")
        event.ignore()                        # Chuyển cho parent
        # Nếu KHÔNG gọi ignore → parent không nhận


class ParentWidget(QWidget):
    def mousePressEvent(self, event):
        print("Parent nhận click")
        super().mousePressEvent(event)


# Layout: Parent chứa Child
parent = ParentWidget()
child = ChildWidget(parent)

# Khi click vào child:
# Output: "Child nhận click" → "Parent nhận click"
```

**Nếu bỏ `event.ignore()`**:
```
# Output: "Child nhận click" (dừng lại, parent không nhận)
```

### 4.3. Ví dụ thực tế – Tooltip qua parent

```python
class ChildButton(QPushButton):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            event.ignore()                    # Nhường cho parent xử lý context menu
        else:
            super().mousePressEvent(event)
```

### 4.4. `event.accept()`

```python
def mousePressEvent(self, event):
    if some_condition:
        event.accept()                        # Chấp nhận, không lan truyền
        # Xử lý
    else:
        event.ignore()                        # Nhường cho parent
```

---

## 🎯 PHẦN 5: `event()` – BẮT TẤT CẢ

### 5.1. Khi nào dùng `event()`?

- Cần **chặn một loại event cụ thể** mà không muốn override từng method
- Xử lý **custom event**
- Debug – in mọi event

### 5.2. Cấu trúc

```python
def event(self, event: QEvent) -> bool:
    """Xử lý MỌI event của widget này."""
    t = event.type()
    
    if t == QEvent.Type.KeyPress:
        print("Key press!")
        # Có thể xử lý tại đây
    
    # Trả về True nếu "đã xử lý", False để Qt xử lý tiếp mặc định
    return super().event(event)
```

⚠️ **Quan trọng**: `event()` trả về **bool**:
- `True` = đã xử lý, dừng
- `False` = chưa, Qt xử lý tiếp (gọi `xxxEvent()`)

Hầu hết case, bạn **luôn gọi `super().event(event)`** để giữ hành vi mặc định.

### 5.3. Ví dụ: chặn phím Delete

```python
class NoDeleteEditor(QTextEdit):
    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Delete:
                return True                   # Chặn hoàn toàn
        return super().event(event)
```

### 5.4. Debug – in mọi event

```python
class DebugWidget(QWidget):
    def event(self, event: QEvent) -> bool:
        print(f"Event: {QEvent.Type(event.type()).name}")
        return super().event(event)
```

Kết quả khi hover chuột:
```
Event: Enter
Event: HoverEnter
Event: HoverMove
Event: HoverMove
Event: HoverLeave
Event: Leave
```

### 5.5. Custom Event

Định nghĩa event type riêng:

```python
from PySide6.QtCore import QEvent, QCoreApplication

# Đăng ký type mới (bắt đầu từ User = 1000)
MY_EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

class MyCustomEvent(QEvent):
    def __init__(self, data: str):
        super().__init__(MY_EVENT_TYPE)
        self.data = data


class MyWidget(QWidget):
    def event(self, event: QEvent) -> bool:
        if event.type() == MY_EVENT_TYPE:
            print(f"Custom event: {event.data}")
            return True
        return super().event(event)


# Gửi event
w = MyWidget()
QCoreApplication.postEvent(w, MyCustomEvent("hello"))
```

**Khi nào dùng custom event?** Rất hiếm. Thường dùng Signal thay thế. Custom event chỉ cần khi:
- Làm việc với Qt state machine
- Integration với C++ code
- Cần thiết kế low-level đặc biệt

---

## 🎯 PHẦN 6: CUSTOM EVENT EXAMPLE – "HOVER BUTTON"

### 6.1. Yêu cầu

Tạo nút có hiệu ứng hover **tùy chỉnh** (không dùng CSS):

- Bình thường: nền xám nhạt
- Hover: nền xanh dương nhạt
- Pressed: nền xanh đậm
- Disabled: nền xám đậm, chữ mờ

### 6.2. Code

```python
import sys
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
)


class HoverButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._hovered = False
        self._pressed = False
        
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    
    # ============================================================
    # EVENT OVERRIDES
    # ============================================================
    def enterEvent(self, event):
        self._hovered = True
        self.update()                          # Yêu cầu vẽ lại
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)
    
    # ============================================================
    # PAINT
    # ============================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        
        # Màu theo state
        if not self.isEnabled():
            bg = QColor("#bdc3c7")
            fg = QColor("#7f8c8d")
        elif self._pressed:
            bg = QColor("#1565C0")
            fg = QColor("white")
        elif self._hovered:
            bg = QColor("#42A5F5")
            fg = QColor("white")
        else:
            bg = QColor("#e0e0e0")
            fg = QColor("#333333")
        
        # Vẽ nền bo góc
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        # Vẽ text
        painter.setPen(QPen(fg))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hover Button Demo")
        self.resize(300, 300)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Hover vào nút để thấy hiệu ứng:"))
        layout.addWidget(HoverButton("Bình thường"))
        layout.addWidget(HoverButton("Hover me!"))
        
        disabled = HoverButton("Disabled")
        disabled.setEnabled(False)
        layout.addWidget(disabled)
        
        layout.addStretch()


app = QApplication(sys.argv)
w = Demo()
w.show()
sys.exit(app.exec())
```

**Điểm hay**:
- Dùng `_hovered`, `_pressed` như **state flags**
- `self.update()` để **yêu cầu Qt vẽ lại** (không vẽ trực tiếp)
- `paintEvent` đọc state → vẽ theo state
- `setCursor` đổi con trỏ thành bàn tay
- `WA_Hover` cho phép Qt gửi hover event

---

## 🎯 PHẦN 7: THỰC HÀNH – PAINT APP ĐƠN GIẢN

### 7.1. Yêu cầu

App vẽ:
- Vẽ đường bằng chuột (drag)
- 3 màu: đen, đỏ, xanh
- 3 độ dày: 2, 5, 10 px
- Nút Clear
- Undo (Ctrl+Z)
- Hiển thị tọa độ chuột ở status bar

### 7.2. Code đầy đủ

Tạo file `paint_app.py`:

```python
import sys
from dataclasses import dataclass, field
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPainter, QPen, QColor, QMouseEvent, QPaintEvent,
    QAction, QKeySequence
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar, QLabel,
    QPushButton, QColorDialog, QSizePolicy, QStatusBar
)


# ============================================================
# STROKE – 1 nét vẽ
# ============================================================
@dataclass
class Stroke:
    color: QColor
    width: int
    points: list[QPointF] = field(default_factory=list)
    
    def add_point(self, pt: QPointF):
        self.points.append(pt)
    
    def draw(self, painter: QPainter):
        if len(self.points) < 2:
            # 1 điểm → vẽ chấm tròn
            if self.points:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.color)
                r = self.width / 2
                p = self.points[0]
                painter.drawEllipse(p, r, r)
            return
        
        pen = QPen(self.color, self.width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        for i in range(1, len(self.points)):
            painter.drawLine(self.points[i - 1], self.points[i])


# ============================================================
# CANVAS – vùng vẽ
# ============================================================
class Canvas(QWidget):
    mouse_moved = Signal(QPointF)
    
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        
        # Cấu hình cọ
        self.current_color = QColor("black")
        self.current_width = 3
        
        # Lịch sử
        self.strokes: list[Stroke] = []
        self.current_stroke: Stroke | None = None
        
        # Nền trắng
        self.setAutoFillBackground(False)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    # ============================================================
    # API
    # ============================================================
    def set_color(self, color: QColor):
        self.current_color = color
    
    def set_width(self, width: int):
        self.current_width = width
    
    def clear(self):
        self.strokes.clear()
        self.current_stroke = None
        self.update()
    
    def undo(self):
        if self.strokes:
            self.strokes.pop()
            self.update()
    
    # ============================================================
    # MOUSE EVENTS
    # ============================================================
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_stroke = Stroke(
                color=QColor(self.current_color),
                width=self.current_width,
            )
            self.current_stroke.add_point(event.position())
            self.update()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_moved.emit(event.position())
        
        if self.current_stroke is not None:
            self.current_stroke.add_point(event.position())
            self.update()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_stroke:
                self.current_stroke.add_point(event.position())
                self.strokes.append(self.current_stroke)
                self.current_stroke = None
                self.update()
        super().mouseReleaseEvent(event)
    
    def leaveEvent(self, event):
        self.mouse_moved.emit(QPointF(-1, -1))
        super().leaveEvent(event)
    
    # ============================================================
    # PAINT
    # ============================================================
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Nền trắng
        painter.fillRect(self.rect(), QColor("white"))
        
        # Vẽ tất cả strokes
        for stroke in self.strokes:
            stroke.draw(painter)
        
        # Vẽ stroke hiện tại (nếu đang vẽ)
        if self.current_stroke:
            self.current_stroke.draw(painter)


# ============================================================
# MAIN WINDOW
# ============================================================
class PaintWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint App")
        self.resize(900, 700)
        
        self.canvas = Canvas()
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        self.setCentralWidget(self.canvas)
        
        self._create_actions()
        self._create_toolbar()
        self._create_statusbar()
    
    # ============================================================
    def _create_actions(self):
        self.act_undo = QAction("↶ Undo", self)
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(self.canvas.undo)
        
        self.act_clear = QAction("🗑️ Clear", self)
        self.act_clear.setShortcut("Ctrl+Shift+X")
        self.act_clear.triggered.connect(self.canvas.clear)
        
        self.act_color = QAction("🎨 Chọn màu...", self)
        self.act_color.triggered.connect(self._pick_color)
        
        self.act_exit = QAction("Thoát", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
    
    # ============================================================
    def _create_toolbar(self):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        self.addToolBar(tb)
        
        tb.addAction(self.act_undo)
        tb.addAction(self.act_clear)
        tb.addSeparator()
        tb.addAction(self.act_color)
        tb.addSeparator()
        
        # Width buttons
        for w in (2, 5, 10, 20):
            btn = QPushButton(f"{w}px")
            btn.setFixedWidth(50)
            btn.clicked.connect(lambda checked=False, width=w: self.canvas.set_width(width))
            tb.addWidget(btn)
        
        tb.addSeparator()
        
        # Color quick buttons
        for name, color in [("Đen", "black"), ("Đỏ", "red"),
                             ("Xanh", "blue"), ("Xanh lá", "green")]:
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(
                f"background: {color}; border: 1px solid #888; border-radius: 4px;"
            )
            btn.setToolTip(name)
            btn.clicked.connect(
                lambda checked=False, c=color: self.canvas.set_color(QColor(c))
            )
            tb.addWidget(btn)
    
    # ============================================================
    def _create_statusbar(self):
        self.lbl_pos = QLabel("Chuột: (--, --)")
        self.statusBar().addPermanentWidget(self.lbl_pos)
        self.statusBar().showMessage("Kéo chuột để vẽ")
    
    # ============================================================
    def _on_mouse_moved(self, pos: QPointF):
        if pos.x() < 0:
            self.lbl_pos.setText("Chuột: (--, --)")
        else:
            self.lbl_pos.setText(f"Chuột: ({int(pos.x())}, {int(pos.y())})")
    
    def _pick_color(self):
        color = QColorDialog.getColor(self.canvas.current_color, self, "Chọn màu")
        if color.isValid():
            self.canvas.set_color(color)


# ============================================================
def main():
    app = QApplication(sys.argv)
    w = PaintWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 7.3. Điểm đáng chú ý

1. **`Stroke` dataclass**: đóng gói 1 nét vẽ
2. **`WA_OpaquePaintEvent`**: tối ưu – widget tự vẽ toàn bộ nền
3. **`setMouseTracking(True)`**: nhận `mouseMoveEvent` cả khi không nhấn
4. **`current_stroke` vs `strokes`**: nét đang vẽ (chưa lưu) vs nét đã lưu
5. **`painter.drawLine` từng cặp**: vẽ polyline thủ công
6. **`PenCapStyle.RoundCap`**: đầu nét tròn → mượt
7. **`QColorDialog`**: picker màu chuẩn
8. **`mouse_moved` signal**: canvas không biết về status bar → dùng signal
9. **Undo**: chỉ cần `strokes.pop()` + `update()`
10. **`leaveEvent`**: reset tọa độ khi chuột ra ngoài

### 7.4. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| Vẽ | Kéo chuột trái | Đường đen xuất hiện |
| Đổi màu | Click nút đỏ → vẽ | Đường đỏ |
| Đổi độ dày | Click "10px" → vẽ | Đường dày |
| Undo | Ctrl+Z | Nét cuối biến mất |
| Clear | Ctrl+Shift+X | Trắng trơn |
| Tọa độ | Di chuột | Số cập nhật ở status bar |

---

## 🎯 PHẦN 8: BEST PRACTICES

### 8.1. Luôn gọi `super().xxxEvent()`

```python
# ✅ Đúng
def mousePressEvent(self, event):
    # Xử lý của bạn
    super().mousePressEvent(event)            # Để Qt làm phần còn lại

# ❌ Sai – mất hành vi mặc định
def mousePressEvent(self, event):
    print("clicked")
    # Không gọi super → widget không còn nhận drag & drop, focus, ...
```

**Ngoại lệ**: `paintEvent` – nếu bạn vẽ **hoàn toàn**, có thể không cần super.

### 8.2. Không vẽ ngoài `paintEvent`

```python
# ❌ SAI – vẽ ở chỗ khác
def on_click(self):
    painter = QPainter(self)
    painter.drawLine(...)

# ✅ ĐÚNG
def on_click(self):
    self._something = True
    self.update()                             # Yêu cầu vẽ lại
```

Lý do: Qt chỉ cung cấp `QPainter` bên trong `paintEvent`.

### 8.3. `update()` vs `repaint()`

| Method | Khi nào |
|--------|---------|
| `update()` | **Luôn dùng** – Qt gom lại, vẽ 1 lần |
| `repaint()` | Gọi ngay, blocking – dùng khi thực sự cần |

```python
self.update()                                 # ✅
self.repaint()                                # ⚠️ Hiếm khi
```

### 8.4. Tránh logic nặng trong `paintEvent`

`paintEvent` chạy **rất thường xuyên**. Đừng làm gì nặng ở đây.

```python
# ❌ SAI
def paintEvent(self, event):
    data = load_from_database()               # Nặng!
    ...

# ✅ ĐÚNG
def paintEvent(self, event):
    # Chỉ đọc dữ liệu đã có sẵn
    ...
```

### 8.5. Cache khi cần

Nếu vẽ phức tạp, cache `QPixmap`:

```python
def __init__(self):
    self._cache = QPixmap()

def resizeEvent(self, event):
    self._cache = QPixmap(self.size())
    self._render_cache()
    super().resizeEvent(event)

def _render_cache(self):
    painter = QPainter(self._cache)
    # Vẽ mọi thứ vào cache
    ...

def paintEvent(self, event):
    painter = QPainter(self)
    painter.drawPixmap(0, 0, self._cache)
```

### 8.6. Tránh `event()` khi có thể dùng method cụ thể

```python
# ❌ Cồng kềnh
def event(self, event):
    if event.type() == QEvent.Type.MouseButtonPress:
        ...
    return super().event(event)

# ✅ Rõ ràng
def mousePressEvent(self, event):
    ...
    super().mousePressEvent(event)
```

---

## 📝 BÀI TẬP

### Bài tập 3.3.1 (Cơ bản)
Tạo widget `TrackerWidget`:
- Hiển thị tọa độ chuột **ngay tại vị trí chuột** (giống tooltip)
- Dùng `mouseMoveEvent` + `paintEvent`
- Chỉ vẽ trong vùng 100x100 quanh chuột

### Bài tập 3.3.2 (Trung bình)
Tạo `ZoomWidget`:
- Hiển thị ảnh (bất kỳ)
- Zoom in/out bằng Ctrl + con lăn chuột
- Pan (di chuyển ảnh) bằng kéo chuột trái
- Reset view khi double-click

💡 Gợi ý: `wheelEvent`, `mouseMoveEvent` + state `_panning`.

### Bài tập 3.3.3 (Khá)
Mở rộng Paint App:
- Thêm công cụ **hình chữ nhật** (vẽ rect khi kéo)
- Thêm công cụ **hình tròn**
- Preview khi đang kéo (chưa thả)
- Có nút chọn công cụ: Pencil / Rectangle / Ellipse

💡 Gợi ý: Mỗi công cụ có `start()`, `move()`, `end()`. Cần state `current_tool`.

### Bài tập 3.3.4 (Nâng cao)
Tạo `ColorPickerWidget`:
- Hiển thị bảng màu gradient HSV
- Click chọn màu
- Phát signal `colorSelected(QColor)`
- Hiển thị màu đang chọn ở ô bên cạnh

💡 Gợi ý: Dùng `QLinearGradient` + vẽ điểm HSV.

### Bài tập 3.3.5 (Khó)
Làm **text editor đơn giản** dùng `QPlainTextEdit` kết hợp event:
- Override `keyPressEvent`: hiện autocomplete khi gõ
- Override `focusInEvent` / `focusOutEvent`: highlight border
- Override `resizeEvent`: điều chỉnh vị trí popup autocomplete
- Override `wheelEvent`: zoom font khi Ctrl + wheel

---

## ✅ CHECKLIST SAU BÀI 3.3

- [ ] Hiểu bản chất Event System – khác Signal ở đâu
- [ ] Nắm vòng đời của một event: OS → QApplication → Widget
- [ ] Biết 2 cấp override: `event()` vs `mousePressEvent()`
- [ ] Override thành thạo `mousePressEvent`, `mouseMoveEvent`, `keyPressEvent`
- [ ] Biết `paintEvent` + `QPainter`
- [ ] Hiểu `resizeEvent`, `closeEvent`, `focusInEvent`, `enterEvent`
- [ ] Phân biệt `accept()` vs `ignore()`, hiểu cơ chế lan truyền
- [ ] Biết `event()` để bắt tất cả
- [ ] Biết custom event (dù ít dùng)
- [ ] Hiểu `update()` vs `repaint()`
- [ ] Biết best practices: super(), không vẽ ngoài paintEvent, cache
- [ ] Hoàn thành Paint App + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 3.4 – Event Filter & Advanced Events**

- **Event Filter**: chặn event của object khác
- `installEventFilter()` / `removeEventFilter()` / `eventFilter()`
- **Application-wide event filter**: `QApplication.installEventFilter()`
- **Shortcut events**: `QShortcut`, `QKeySequence`
- **Drag & Drop đầy đủ**: `QDrag`, `QMimeData`, custom drag
- **Native events**: `nativeEvent()` (Windows/macOS specific)
- **Timer events**: `timerEvent()`
- Project: **Global Hotkey System** + **Drag & Drop file vào app**

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 3.4 – Event Filter & Advanced Events**?
2. **Giải chi tiết một bài tập 3.3.x** nào?
3. **Đào sâu** phần nào (ví dụ: paintEvent tối ưu, custom event, drag & drop)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀