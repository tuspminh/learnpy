# 📘 MODULE 3 – BÀI 3.4: EVENT FILTER & ADVANCED EVENTS

> **Mục tiêu bài học**:
> - Hiểu **Event Filter** – quan sát/chặn event của object khác
> - Phân biệt **local filter** vs **global (application-wide) filter**
> - Thành thạo `installEventFilter()`, `eventFilter()`, `removeEventFilter()`
> - Nắm **Shortcut System**: `QShortcut`, `QKeySequence`, shortcut context
> - Hiểu **Drag & Drop đầy đủ**: `QDrag`, `QMimeData`, custom MIME types
> - Biết **`timerEvent()`** – cách thay thế `QTimer` trong một số case
> - Xây dựng **Global Hotkey System** + **Drag & Drop file vào app**

---

## 🎯 PHẦN 1: EVENT FILTER LÀ GÌ?

### 1.1. Vấn đề đặt ra

Giả sử bạn muốn:
- **Chặn** một số phím trong `QLineEdit` mà không muốn subclass
- **Log** mọi sự kiện click của tất cả button
- **Bắt** sự kiện từ widget con mà widget đó không cho bạn override

→ Không thể override nếu không có quyền sửa class. **Event Filter** giải quyết.

### 1.2. Định nghĩa

**Event Filter** là một `QObject` có thể **đăng ký theo dõi** event của object khác. Khi object đích nhận event, filter được gọi **TRƯỚC** object đích.

```
Widget A (đích)          Widget B (filter)
    │                          │
    │  ◀── installEventFilter(B)
    │
    │  [nhận event từ OS]
    │
    │  eventFilter(obj=A, event)  ──▶  B.eventFilter() trả về True/False
    │                                        │
    │  ◀────────── True: chặn ──────────────┤
    │  ◀────────── False: cho qua ──────────┤
    │
    │  [xử lý event bình thường]
```

### 1.3. Ba method chính

```python
# 1. Đăng ký: đối tượng nào làm filter?
target_widget.installEventFilter(filter_object)

# 2. Hủy đăng ký
target_widget.removeEventFilter(filter_object)

# 3. Filter object phải override method này
class MyFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # Trả về True = "đã xử lý, chặn object đích"
        # Trả về False = "cho qua, object đích tự xử lý"
        return False
```

### 1.4. Ví dụ cơ bản – Chặn ký tự trong QLineEdit

```python
import sys
from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel


class NoDigitsFilter(QObject):
    """Chặn mọi ký tự số trong widget được filter."""
    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.text().isdigit():
                return True                   # Chặn, không cho widget nhận
        return False                          # Cho qua


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Ô dưới không cho nhập số:"))
        
        edit = QLineEdit()
        layout.addWidget(edit)
        
        layout.addWidget(QLabel("Ô dưới bình thường:"))
        layout.addWidget(QLineEdit())
        
        # Cài filter cho edit đầu tiên
        self.filter = NoDigitsFilter()
        edit.installEventFilter(self.filter)


app = QApplication(sys.argv)
w = Demo()
w.show()
sys.exit(app.exec())
```

**Kết quả**: Ô đầu chặn mọi chữ số, ô sau bình thường.

---

## 🎯 PHẦN 2: HIỂU SÂU eventFilter()

### 2.1. Tham số

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:
    """
    watched: object đích nhận event
    event:   event đang xảy ra
    return:  True = chặn, False = cho qua
    """
```

### 2.2. Return value – Cực quan trọng

| Return | Ý nghĩa |
|--------|---------|
| `True` | Event **bị chặn** – object đích **KHÔNG nhận** |
| `False` | Event **đi qua** – object đích nhận bình thường |

⚠️ Nhiều người lầm tưởng `True` là "cho qua" – ngược lại đấy!

### 2.3. Filter cho nhiều widget

1 filter object có thể filter **nhiều widget**:

```python
class ClickLogger(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            print(f"Click vào: {watched.objectName() or watched.__class__.__name__}")
        return False


logger = ClickLogger()
button1.installEventFilter(logger)
button2.installEventFilter(logger)
button3.installEventFilter(logger)
```

### 2.4. Nhiều filter cho 1 widget

```python
widget.installEventFilter(filter1)
widget.installEventFilter(filter2)
widget.installEventFilter(filter3)
```

Qt gọi theo **thứ tự ngược** (filter gần nhất được gọi trước):

```
Event ──▶ filter3 ──▶ filter2 ──▶ filter1 ──▶ widget.event()
```

Nếu filter3 return True → dừng, không gọi các filter khác.

### 2.5. Gọi `super().eventFilter()`

**Không bắt buộc** nếu bạn là `QObject` thuần, nhưng nên làm nếu kế thừa widget khác:

```python
class MyWidget(QWidget):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                return True
        return super().eventFilter(watched, event)
```

### 2.6. Ứng dụng thực tế của Event Filter

| Use case | Cách làm |
|----------|---------|
| Validate phím khi không có quyền sửa widget | Chặn `KeyPress` |
| Log mọi event toàn app | Application-wide filter |
| Bắt Ctrl+Enter trong QTextEdit | Chặn trong `KeyPress` |
| Highlight khi hover (không dùng QSS) | Bắt `Enter`/`Leave` |
| Chặn paste trong QLineEdit | Bắt `QEvent.Type.Paste` |
| Bắt phím tắt toàn cục | App filter + key check |
| Auto-select all khi focus | Bắt `FocusIn` |
| Prevent scroll khi QComboBox mất focus | Bắt `Wheel` |

---

## 🎯 PHẦN 3: VÍ DỤ THỰC TẾ

### 3.1. Ứng dụng 1 – Validate không cho nhập ký tự đặc biệt

```python
class AlphanumericFilter(QObject):
    """Chỉ cho phép chữ và số."""
    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            # Cho phép các phím điều hướng
            nav_keys = {
                Qt.Key.Key_Backspace, Qt.Key.Key_Delete,
                Qt.Key.Key_Left, Qt.Key.Key_Right,
                Qt.Key.Key_Home, Qt.Key.Key_End,
                Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter,
            }
            if key in nav_keys:
                return False
            # Cho phép Ctrl combos
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                return False
            # Cho phép chữ và số
            text = event.text()
            if text and (text.isalnum() or text in " _-"):
                return False
            return True                       # Chặn
        
        return False
```

### 3.2. Ứng dụng 2 – Auto-select-all khi focus

```python
class SelectAllOnFocus(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.FocusIn:
            if hasattr(watched, "selectAll"):
                watched.selectAll()
        return False


# Dùng cho nhiều input
sel_filter = SelectAllOnFocus()
for edit in [self.txt_name, self.txt_email, self.txt_phone]:
    edit.installEventFilter(sel_filter)
```

### 3.3. Ứng dụng 3 – Ctrl+Enter để submit form

```python
class SubmitOnCtrlEnter(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()
            
            is_enter = key in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            is_ctrl = bool(mods & Qt.KeyboardModifier.ControlModifier)
            
            if is_enter and is_ctrl:
                self.callback()
                return True                   # Chặn không cho chèn newline
        
        return False


# Dùng
edit = QTextEdit()
edit.installEventFilter(SubmitOnCtrlEnter(self.submit_form))
```

### 3.4. Ứng dụng 4 – Chặn wheel trên ComboBox khi chưa focus

Vấn đề: user cuộn trang vô tình thay đổi giá trị QComboBox.

```python
class WheelGuard(QObject):
    """Chặn wheel khi widget không có focus."""
    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel:
            if not watched.hasFocus():
                return True                   # Chặn
        return False


# Áp dụng cho tất cả combo box
guard = WheelGuard()
for combo in self.findChildren(QComboBox):
    combo.installEventFilter(guard)
```

### 3.5. Ứng dụng 5 – Log mọi event của 1 widget (debug)

```python
class EventLogger(QObject):
    def __init__(self, name: str = "widget"):
        super().__init__()
        self.name = name
    
    def eventFilter(self, watched, event):
        type_name = QEvent.Type(event.type()).name
        print(f"[{self.name}] {type_name}")
        return False


# Áp dụng
edit.installEventFilter(EventLogger("MyLineEdit"))
```

Khi gõ 1 ký tự, output:
```
[MyLineEdit] KeyPress
[MyLineEdit] InputMethod
[MyLineEdit] KeyRelease
[MyLineEdit] ShortcutOverride
[MyLineEdit] KeyPress
...
```

---

## 🎯 PHẦN 4: APPLICATION-WIDE EVENT FILTER

### 4.1. Global filter – bắt MỌI event toàn app

```python
app.installEventFilter(my_filter)
```

Filter sẽ nhận **mọi event** được gửi đến **bất kỳ object nào** trong app.

### 4.2. Ví dụ – Global hotkey (Ctrl+Shift+P)

```python
class GlobalHotkeyFilter(QObject):
    triggered = Signal(str)                   # hotkey name
    
    def __init__(self):
        super().__init__()
        self._hotkeys = {}                    # name → QKeySequence
    
    def register(self, name: str, key_sequence: str):
        self._hotkeys[name] = QKeySequence(key_sequence)
    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            # Build QKeySequence từ event
            key = event.key()
            mods = event.modifiers()
            
            # Bỏ các modifier không dùng
            mod_int = int(mods)
            mod_int &= ~int(Qt.KeyboardModifier.KeypadModifier)
            mod_int &= ~int(Qt.KeyboardModifier.GroupSwitchModifier)
            
            seq_int = mod_int | key
            seq = QKeySequence(seq_int)
            
            for name, ks in self._hotkeys.items():
                if seq == ks:
                    self.triggered.emit(name)
                    return True                # Chặn để không chèn vào widget
        
        return False


# Dùng
hotkey = GlobalHotkeyFilter()
hotkey.register("save", "Ctrl+S")
hotkey.register("quit", "Ctrl+Q")
hotkey.register("palette", "Ctrl+Shift+P")
hotkey.triggered.connect(lambda name: print(f"Hotkey: {name}"))

app.installEventFilter(hotkey)
```

### 4.3. Cảnh báo – Global filter ảnh hưởng performance

Filter chạy cho **mọi event**. Nếu logic nặng → app chậm.

**Best practices**:
- **Early return** ngay nếu event type không quan tâm
- **Cache** dữ liệu (như dict hotkey ở ví dụ trên)
- Chỉ dùng global filter khi thực sự cần

### 4.4. Debug – Log event của toàn app

```python
class GlobalEventLogger(QObject):
    def __init__(self, ignore_types=None):
        super().__init__()
        self.ignore = ignore_types or {
            QEvent.Type.Paint,                 # Rất nhiều, bỏ qua
            QEvent.Type.UpdateRequest,
            QEvent.Type.Move,
            QEvent.Type.HoverMove,
            QEvent.Type.MouseMove,
        }
    
    def eventFilter(self, watched, event):
        if event.type() not in self.ignore:
            type_name = QEvent.Type(event.type()).name
            obj_name = watched.objectName() or watched.__class__.__name__
            print(f"{obj_name}: {type_name}")
        return False


app.installEventFilter(GlobalEventLogger())
```

---

## 🎯 PHẦN 5: SHORTCUT SYSTEM

### 5.1. Ba cách tạo phím tắt

| Cách | Khi nào |
|------|---------|
| **QAction** với `setShortcut()` | Khi có menu/toolbar |
| **QShortcut** | Phím tắt độc lập, không qua menu |
| **Override `keyPressEvent`** | Xử lý phím đặc biệt |

### 5.2. QShortcut

```python
from PySide6.QtGui import QShortcut, QKeySequence

shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
shortcut.activated.connect(self.save)

# Hoặc dùng biến thành viên để giữ reference
self.sc_save = QShortcut(QKeySequence.StandardKey.Save, self)
self.sc_save.activated.connect(self.save)
```

⚠️ **Quan trọng**: phải giữ **reference** đến `QShortcut`, nếu không nó bị GC.

### 5.3. QKeySequence – Nhiều định dạng

```python
# String
QKeySequence("Ctrl+S")
QKeySequence("Ctrl+Shift+P")
QKeySequence("F5")
QKeySequence("Alt+F4")

# Standard key (cross-platform)
QKeySequence(QKeySequence.StandardKey.Save)          # Ctrl+S (Win) / Cmd+S (Mac)
QKeySequence(QKeySequence.StandardKey.Copy)
QKeySequence(QKeySequence.StandardKey.Paste)
QKeySequence(QKeySequence.StandardKey.Undo)
QKeySequence(QKeySequence.StandardKey.Redo)
QKeySequence(QKeySequence.StandardKey.Quit)
QKeySequence(QKeySequence.StandardKey.Open)
QKeySequence(QKeySequence.StandardKey.New)
QKeySequence(QKeySequence.StandardKey.Find)
QKeySequence(QKeySequence.StandardKey.HelpContents)

# Nhiều tổ hợp thay thế
QKeySequence("Ctrl+S, Ctrl+Shift+S")                  # Cả 2 đều dùng
```

### 5.4. Shortcut Context – quan trọng

`QShortcut` có **context** quyết định **khi nào active**:

| Context | Kích hoạt khi |
|---------|--------------|
| `WidgetShortcut` | Chỉ khi widget có focus |
| `WidgetWithChildrenShortcut` | Widget hoặc con có focus |
| `WindowShortcut` (default) | Bất kỳ đâu trong window |
| `ApplicationShortcut` | Bất kỳ đâu trong app |
| `ApplicationShortcut` | Bất kỳ đâu, kể cả dialog khác |

```python
sc = QShortcut(QKeySequence("F1"), self)
sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
sc.activated.connect(self.show_help)
```

### 5.5. Ambiguous shortcuts – Khi 2 shortcut trùng

Nếu 2 shortcut cùng tổ hợp, Qt gọi `QApplication.ambiguousShortcutActivated`:

```python
# Cách xử lý
sc.activatedAmbiguously.connect(self.handle_ambiguous)
```

Hoặc set `Qt.ShortcutContext.WidgetShortcut` để giới hạn.

### 5.6. Ví dụ – Shortcut toàn diện cho app

```python
class AppShortcuts:
    def __init__(self, window):
        self.window = window
        self._shortcuts = []               # Giữ reference
        
        self._add("Ctrl+N", window.new_file)
        self._add("Ctrl+O", window.open_file)
        self._add("Ctrl+S", window.save_file)
        self._add("Ctrl+Shift+S", window.save_as)
        self._add("Ctrl+Z", window.undo)
        self._add("Ctrl+Y", window.redo)
        self._add("F5", window.refresh)
        self._add("F11", window.toggle_fullscreen)
        self._add("Ctrl+Shift+P", window.show_command_palette)
    
    def _add(self, key_seq: str, callback):
        sc = QShortcut(QKeySequence(key_seq), self.window)
        sc.setContext(Qt.ShortcutContext.WindowShortcut)
        sc.activated.connect(callback)
        self._shortcuts.append(sc)          # Chống GC
```

---

## 🎯 PHẦN 6: DRAG & DROP ĐẦY ĐỦ

### 6.1. Khái niệm

**Drag & Drop** là cơ chế chuyển dữ liệu giữa:
- 2 widget trong cùng app
- App và OS (file manager)
- 2 app khác nhau

### 6.2. Mô hình

```
SOURCE                                TARGET
  │                                     │
  │  mousePress → drag started          │
  │                                     │
  │  QDrag.exec(QMimeData) ─────────▶   │
  │                                     │
  │                           dragEnterEvent
  │                                     │
  │                           dragMoveEvent
  │                                     │
  │                           dropEvent
  │                                     │
  │  ◀────── result ──────────────────  │
  │                                     │
```

### 6.3. 3 thành phần chính

1. **QMimeData**: chứa dữ liệu + loại dữ liệu (MIME type)
2. **QDrag**: thực hiện thao tác kéo
3. **Target events**: `dragEnterEvent`, `dragMoveEvent`, `dropEvent`

### 6.4. Bật Drag & Drop cho target

```python
widget.setAcceptDrops(True)                   # Nhận drop
```

### 6.5. 3 event cần override trên target

```python
def dragEnterEvent(self, event: QDragEnterEvent):
    """Chuột kéo vào widget."""
    if event.mimeData().hasUrls():
        event.acceptProposedAction()
    else:
        event.ignore()

def dragMoveEvent(self, event: QDragMoveEvent):
    """Chuột di chuyển khi đang kéo."""
    # Cập nhật UI highlight, ...
    event.acceptProposedAction()

def dropEvent(self, event: QDropEvent):
    """User thả chuột."""
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            print(f"File: {path}")
        event.acceptProposedAction()
```

### 6.6. Ví dụ 1 – Drop file vào app

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget
)


class FileDropArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)             # BẬT drop
        
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background: #f0f0f0;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Kéo file vào đây")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: #666; border: none;")
        layout.addWidget(self.label)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Đổi màu để thông báo
            self.setStyleSheet("""
                QWidget {
                    background: #e3f2fd;
                    border: 2px dashed #2196F3;
                    border-radius: 8px;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        # Chuột ra khỏi widget mà không drop
        self.setStyleSheet("""
            QWidget {
                background: #f0f0f0;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
    
    def dropEvent(self, event):
        # Reset style
        self.setStyleSheet("""
            QWidget {
                background: #f0f0f0;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
        
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            self.label.setText("Đã nhận:\n" + "\n".join(files))
            event.acceptProposedAction()


app = QApplication(sys.argv)
w = FileDropArea()
w.setWindowTitle("Drop File Demo")
w.show()
sys.exit(app.exec())
```

### 6.7. Ví dụ 2 – Custom drag giữa 2 list

```python
import sys
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QListWidget, QListWidgetItem
)


class DraggableList(QListWidget):
    """List cho phép kéo item ra ngoài."""
    
    MIME_TYPE = "application/x-myapp-item"
    
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
    
    def startDrag(self, supported_actions):
        item = self.currentItem()
        if not item:
            return
        
        mime = QMimeData()
        mime.setData(self.MIME_TYPE, item.text().encode("utf-8"))
        
        drag = QDrag(self)
        drag.setMimeData(mime)
        
        # Thực hiện drag
        result = drag.exec(Qt.DropAction.MoveAction)
        
        # Nếu drop thành công và là Move → xóa item khỏi list nguồn
        if result == Qt.DropAction.MoveAction:
            row = self.row(item)
            self.takeItem(row)
    
    # -------- Drop handlers --------
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(self.MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(self.MIME_TYPE):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat(self.MIME_TYPE):
            data = event.mimeData().data(self.MIME_TYPE)
            text = bytes(data).decode("utf-8")
            
            # Thêm vào vị trí drop
            pos = event.position().toPoint()
            item = QListWidgetItem(text)
            self.insertItem(self.indexAt(pos).row() or self.count(), item)
            
            event.acceptProposedAction()
            # Nếu không phải chính list này thì source tự xóa (đã xử lý ở startDrag)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop giữa 2 list")
        self.resize(600, 400)
        
        layout = QHBoxLayout(self)
        
        self.list1 = DraggableList()
        self.list1.addItems(["Item A", "Item B", "Item C"])
        layout.addWidget(self.list1)
        
        self.list2 = DraggableList()
        self.list2.addItems(["Item X", "Item Y"])
        layout.addWidget(self.list2)


app = QApplication(sys.argv)
w = Demo()
w.show()
sys.exit(app.exec())
```

**Điểm hay**:
- **Custom MIME type**: `"application/x-myapp-item"` – chỉ app của bạn hiểu
- **`startDrag` override**: tạo `QDrag` + `QMimeData`
- **`drag.exec(MoveAction)`**: blocking, trả về action đã thực hiện
- **Chỉ xóa source khi Move**: nếu Copy thì giữ lại

### 6.8. MIME types có sẵn

| MIME type | Nội dung |
|-----------|----------|
| `text/plain` | Text thuần |
| `text/html` | HTML |
| `text/uri-list` | Danh sách file |
| `image/png`, `image/jpeg` | Ảnh |
| `application/x-qt-windows-mime;value="FileName"` | File trên Windows |

### 6.9. Drop action

| Action | Ý nghĩa |
|--------|---------|
| `CopyAction` | Copy dữ liệu |
| `MoveAction` | Di chuyển |
| `LinkAction` | Tạo link |
| `IgnoreAction` | Từ chối |
| `TargetMoveAction` | Target quyết định move |

Hiển thị cursor khác nhau cho từng action.

---

## 🎯 PHẦN 7: TIMER EVENT

### 7.1. `timerEvent()` – Cách cũ

Trước khi có `QTimer`, người ta dùng `QObject.startTimer()` + override `timerEvent()`:

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.timer_id = self.startTimer(1000)   # 1000ms
    
    def timerEvent(self, event: QTimerEvent):
        if event.timerId() == self.timer_id:
            print("Tick!")
    
    def stop_timer(self):
        self.killTimer(self.timer_id)
```

### 7.2. `QTimer` – Cách hiện đại (khuyên dùng)

```python
timer = QTimer(self)
timer.timeout.connect(self.on_tick)
timer.start(1000)
```

### 7.3. Khi nào dùng `timerEvent`?

**Hầu như không bao giờ**. Chỉ dùng khi:
- Kế thừa C++ code cũ
- Cần nhiều timer với cùng handler
- Tiết kiệm object (rất hiếm)

### 7.4. QTimer nâng cao – Single shot

```python
# Chạy 1 lần sau 1s
QTimer.singleShot(1000, self.do_something)

# Debounce
self.timer = QTimer()
self.timer.setSingleShot(True)
self.timer.timeout.connect(self.save)
# Mỗi lần gọi:
self.timer.start(500)                        # Reset, chỉ save khi dừng 500ms
```

---

## 🎯 PHẦN 8: THỰC HÀNH – "FILE DROP + HOTKEY" APP

Chúng ta sẽ tổng hợp: **File Drop + Global Hotkey + Shortcut + Event Filter**.

### 8.1. Yêu cầu

- Kéo file vào cửa sổ → hiển thị danh sách
- Ctrl+O cũng mở file dialog
- Ctrl+Shift+P → Command Palette (đơn giản: focus vào search)
- Chặn wheel trên ComboBox khi không focus
- Esc → clear danh sách
- Ctrl+Backspace trong search box → xóa toàn bộ từ

### 8.2. Code đầy đủ

Tạo file `file_drop_hotkey.py`:

```python
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QObject, QEvent, QMimeData
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QFileDialog, QMessageBox, QToolBar
)


# ============================================================
# FILTER 1: Chặn wheel trên ComboBox khi không focus
# ============================================================
class WheelGuard(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel:
            if not watched.hasFocus():
                return True
        return False


# ============================================================
# FILTER 2: Ctrl+Backspace xóa toàn bộ trong QLineEdit
# ============================================================
class CtrlBackspaceFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            if (event.key() == Qt.Key.Key_Backspace and
                    event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                watched.clear()                # Xóa hết
                return True
        return False


# ============================================================
# DROP AREA
# ============================================================
class DropListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setStyleSheet("""
            QListWidget {
                background: #fafafa;
                border: 2px dashed #bbb;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget:focus {
                border-color: #2196F3;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QListWidget {
                    background: #e3f2fd;
                    border: 2px dashed #2196F3;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self._reset_style()
    
    def dropEvent(self, event):
        self._reset_style()
        if event.mimeData().hasUrls():
            paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
            for p in paths:
                self._add_path(p)
            event.acceptProposedAction()
    
    def _add_path(self, path: Path):
        # Tránh trùng
        existing = [self.item(i).text() for i in range(self.count())]
        if str(path) in existing:
            return
        
        size = path.stat().st_size if path.exists() else 0
        size_str = self._format_size(size)
        icon = "📁" if path.is_dir() else "📄"
        text = f"{icon} {path.name}  ({size_str})  —  {path.parent}"
        
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        item.setToolTip(str(path))
        self.addItem(item)
    
    def _format_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _reset_style(self):
        self.setStyleSheet("""
            QListWidget {
                background: #fafafa;
                border: 2px dashed #bbb;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget:focus {
                border-color: #2196F3;
            }
        """)
    
    # Signal để báo MainWindow khi có file mới
    def paths(self) -> list[str]:
        return [self.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.count())]


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Drop + Hotkey Demo")
        self.resize(700, 500)
        
        self._setup_ui()
        self._setup_actions()
        self._setup_shortcuts()
        self._setup_filters()
    
    # ----------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("📥 Kéo file/thư mục vào vùng bên dưới")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Search bar
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Lọc:"))
        
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText(
            "Tìm theo tên file  •  Ctrl+Backspace để xóa nhanh  •  Esc để reset"
        )
        self.txt_filter.textChanged.connect(self._filter_items)
        search_row.addWidget(self.txt_filter, 1)
        
        self.cbo_sort = QComboBox()
        self.cbo_sort.addItems(["Tên A→Z", "Tên Z→A", "Kích thước ↓", "Kích thước ↑"])
        search_row.addWidget(self.cbo_sort)
        
        layout.addLayout(search_row)
        
        # Drop list
        self.list = DropListWidget()
        layout.addWidget(self.list, 1)
    
    # ----------------------------------------------------------
    def _setup_actions(self):
        # File
        act_open = QAction("📂 Mở file...", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.open_files)
        
        act_clear = QAction("🗑️ Xóa danh sách", self)
        act_clear.setShortcut("Ctrl+Shift+X")
        act_clear.triggered.connect(self.clear_list)
        
        act_exit = QAction("Thoát", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        
        # Edit
        act_focus_search = QAction("🔍 Focus tìm kiếm", self)
        act_focus_search.setShortcut("Ctrl+F")
        act_focus_search.triggered.connect(self._focus_search)
        
        act_palette = QAction("⚡ Command Palette", self)
        act_palette.setShortcut("Ctrl+Shift+P")
        act_palette.triggered.connect(self._open_command_palette)
        
        # Menu
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        fm.addAction(act_open)
        fm.addAction(act_clear)
        fm.addSeparator()
        fm.addAction(act_exit)
        
        em = mb.addMenu("&Edit")
        em.addAction(act_focus_search)
        em.addAction(act_palette)
        
        # Toolbar
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction(act_open)
        tb.addAction(act_clear)
        tb.addSeparator()
        tb.addAction(act_focus_search)
        tb.addAction(act_palette)
        
        # Status
        self.statusBar().showMessage("Sẵn sàng — kéo file vào hoặc Ctrl+O")
    
    # ----------------------------------------------------------
    def _setup_shortcuts(self):
        # Esc để clear list
        sc_esc = QShortcut(QKeySequence("Escape"), self)
        sc_esc.activated.connect(self._on_escape)
        self._sc_esc = sc_esc                  # Giữ reference
    
    # ----------------------------------------------------------
    def _setup_filters(self):
        # Wheel guard cho combo
        self._wheel_guard = WheelGuard()
        self.cbo_sort.installEventFilter(self._wheel_guard)
        
        # Ctrl+Backspace cho search
        self._ctrl_bs = CtrlBackspaceFilter()
        self.txt_filter.installEventFilter(self._ctrl_bs)
    
    # ----------------------------------------------------------
    # ACTIONS
    # ----------------------------------------------------------
    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Chọn file", "", "All files (*)"
        )
        for p in paths:
            self.list._add_path(Path(p))
        if paths:
            self.statusBar().showMessage(f"Đã thêm {len(paths)} file", 3000)
    
    def clear_list(self):
        if self.list.count() == 0:
            return
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Xóa {self.list.count()} mục?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.list.clear()
            self.txt_filter.clear()
            self.statusBar().showMessage("Đã xóa danh sách", 2000)
    
    def _focus_search(self):
        self.txt_filter.setFocus()
        self.txt_filter.selectAll()
        self.statusBar().showMessage("Focus vào ô tìm kiếm", 2000)
    
    def _open_command_palette(self):
        # Demo đơn giản: show popup với các lệnh
        from PySide6.QtWidgets import QInputDialog
        commands = ["Mở file (Ctrl+O)", "Xóa danh sách", "Focus tìm kiếm"]
        cmd, ok = QInputDialog.getItem(
            self, "Command Palette", "Chọn lệnh:", commands, 0, False
        )
        if not ok:
            return
        if "Mở file" in cmd:
            self.open_files()
        elif "Xóa danh sách" in cmd:
            self.clear_list()
        elif "Focus" in cmd:
            self._focus_search()
    
    # ----------------------------------------------------------
    # FILTER LIST
    # ----------------------------------------------------------
    def _filter_items(self, text: str):
        """Ẩn các item không khớp text."""
        text = text.lower().strip()
        for i in range(self.list.count()):
            item = self.list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole) or ""
            match = text in path.lower()
            item.setHidden(not match)
    
    # ----------------------------------------------------------
    # ESC HANDLER
    # ----------------------------------------------------------
    def _on_escape(self):
        if self.txt_filter.text():
            self.txt_filter.clear()
            self.statusBar().showMessage("Đã xóa ô tìm kiếm", 2000)
        else:
            self.statusBar().showMessage("Nhấn Ctrl+Shift+X để xóa toàn bộ", 2000)


# ============================================================
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 8.3. Điểm đáng chú ý

1. **3 kỹ thuật khác nhau**: Event Filter + Shortcut + Drag & Drop trong 1 app
2. **`WheelGuard`**: bảo vệ combo khỏi scroll vô tình
3. **`CtrlBackspaceFilter`**: tiện ích người dùng
4. **`DropListWidget`** tự xử lý drag/drop, không phụ thuộc MainWindow
5. **`_sc_esc` giữ reference** → tránh QShortcut bị GC
6. **`Qt.ItemDataRole.UserRole`**: lưu full path ẩn trong item
7. **`event.acceptProposedAction()`**: chuẩn cho drop
8. **Early return** trong `eventFilter` → performance
9. **`item.setHidden()`**: filter không xóa item (giữ nguyên khi clear filter)
10. **`_reset_style`**: reset style của drop area sau khi dragLeave/drop

### 8.4. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| Drop file | Kéo 1 file từ Explorer vào list | Hiện tên file + size |
| Multi drop | Kéo nhiều file | Thêm hết |
| Drag over | Kéo file vào nhưng không drop, rồi ra | Border đổi xanh → trắng lại |
| Ctrl+O | Mở dialog chọn file | Thêm vào list |
| Ctrl+F | Focus vào ô tìm kiếm | Con trỏ nhảy vào, text select all |
| Ctrl+Backspace | Ở ô tìm kiếm, nhấn | Xóa toàn bộ |
| Esc | Nhấn khi có text search | Clear search |
| Esc | Nhấn lần 2 | Chỉ hiện gợi ý |
| Ctrl+Shift+P | Mở command palette | Hiện dialog chọn lệnh |
| Wheel trên combo | Cuộn khi combo không focus | Không đổi giá trị |

---

## 📝 BÀI TẬP

### Bài tập 3.4.1 (Cơ bản)
Tạo **filter chặn paste** trong `QLineEdit`:
- Bắt `QEvent.Type.KeyPress`
- Nếu là `Ctrl+V` → chặn (return True)
- Test: copy text từ Notepad rồi thử paste

### Bài tập 3.4.2 (Trung bình)
Tạo **shortcut toàn cục** cho app:
- `Ctrl+Shift+D` → toggle dark mode (đổi stylesheet app)
- `Ctrl+Shift+T` → toggle theme mặc định
- `F1` → hiện dialog help
- Giữ reference đúng cách

### Bài tập 3.4.3 (Khá)
Mở rộng `DropListWidget`:
- Nhận cả file và thư mục
- Nếu là thư mục → đệ quy thêm file bên trong (giới hạn 100 file)
- Có nút "Remove selected" trong context menu chuột phải

💡 Gợi ý: Override `contextMenuEvent`, dùng `path.iterdir()`.

### Bài tập 3.4.4 (Nâng cao)
Làm **custom drag ghost** (hình ảnh hiển thị khi kéo):
- Khi bắt đầu drag item, tạo `QPixmap` từ item
- Dùng `drag.setPixmap(pixmap)`
- Đặt hotspot ở giữa: `drag.setHotSpot(QPoint(w//2, h//2))`

### Bài tập 3.4.5 (Khó)
Làm **auto-complete popup** dùng Event Filter:
- Có `QLineEdit` + `QListWidget` (popup)
- Khi gõ, hiện popup với gợi ý
- Bắt `KeyPress` trong lineedit: Down/Up di chuyển trong popup, Enter chọn
- Popup tự ẩn khi mất focus

💡 Gợi ý: Dùng `Qt.WindowType.Popup`, `move()` popup theo cursor.

---

## ✅ CHECKLIST SAU BÀI 3.4

- [ ] Hiểu **Event Filter** – filter được gọi trước widget đích
- [ ] Biết `installEventFilter`, `removeEventFilter`, `eventFilter`
- [ ] Hiểu return value: `True` = chặn, `False` = cho qua
- [ ] Biết filter cho nhiều widget, nhiều filter cho 1 widget
- [ ] Biết **application-wide filter** (`QApplication.installEventFilter`)
- [ ] Biết cảnh báo performance của global filter
- [ ] Phân biệt **QShortcut** vs **QAction shortcut**
- [ ] Hiểu **Shortcut Context**
- [ ] Biết giữ reference đến QShortcut
- [ ] Hiểu **Drag & Drop**: 3 events trên target
- [ ] Biết tạo custom MIME type
- [ ] Biết **QDrag.exec()** blocking
- [ ] Biết `dragLeaveEvent` để reset UI
- [ ] Hiểu `timerEvent()` (dù không dùng)
- [ ] Hoàn thành app File Drop + Hotkey + ít nhất 2 bài tập

---

## 🎓 TỔNG KẾT MODULE 3

| Kỹ năng | Trình độ |
|---------|----------|
| Signal/Slot cơ bản | ✅ Thành thạo |
| Connection Types | ✅ Hiểu |
| Custom Signal nâng cao | ✅ Thành thạo |
| Signal forwarding / aggregation | ✅ Biết pattern |
| Event System & override | ✅ Thành thạo |
| Event Filter (local + global) | ✅ Hiểu rõ |
| Shortcut & QKeySequence | ✅ Thành thạo |
| Drag & Drop cơ bản | ✅ Biết làm |
| Paint với QPainter | ✅ Khá |

---

## 🔜 MODULE 4 – WIDGET NÂNG CAO

Sẽ bao gồm:
- **QTabWidget** – giao diện tab
- **QSplitter** – chia đôi (đã học sơ ở Module 2)
- **QDockWidget** – panel có thể dock
- **QToolBox** – accordion
- **QScrollArea** nâng cao
- **QListWidget/QTreeWidget/QTableWidget** đầy đủ
- **QCalendarWidget**, **QDateEdit** nâng cao
- **QProgressBar** + custom

Hoặc chuyển sang **Module 6 – Model/View** để đi sâu vào cách chuyên nghiệp.

---

👉 Bạn muốn:
1. **Bắt đầu Module 4 – Bài 4.1: QTabWidget & QSplitter**?
2. **Bắt đầu Module 6 – Model/View** (phần chuyên nghiệp nhất)?
3. **Giải chi tiết một bài tập 3.4.x** nào?
4. **Đào sâu** phần nào (Drag & Drop MIME, Application filter, Shortcut conflict)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀