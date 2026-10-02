# 📘 MODULE 3 – BÀI 3.2: CUSTOM SIGNAL NÂNG CAO & SIGNAL VỚI QT DESIGNER

> **Mục tiêu bài học**:
> - Nắm **multiple inheritance** với QObject và các pitfalls
> - Signal với **enum, list, dict, custom type phức tạp**
> - Hiểu **parent-child** ảnh hưởng thế nào đến signal
> - Biết **metaclass** `Signal` hoạt động ra sao
> - **Introspection**: liệt kê, kiểm tra signal runtime
> - Kết hợp Signal với **Qt Designer** (`.ui` file)
> - Kỹ thuật **signal forwarding**, **signal aggregation**

---

## 🎯 PHẦN 1: MULTIPLE INHERITANCE VỚI QOBJECT

### 1.1. Vấn đề khi kế thừa nhiều class

Trong Python, bạn có thể kế thừa nhiều class. Nhưng với QObject, có **quy tắc** phải tuân:

```python
# ❌ SAI – 2 class cùng kế thừa QObject → metaclass conflict
class A(QObject): pass
class B(QObject): pass
class C(A, B): pass
```

Python báo: `TypeError: multiple bases have instance lay-out conflict`

### 1.2. Giải pháp: 1 class Qt + các class thuần Python

```python
# ✅ ĐÚNG – chỉ 1 class kế thừa QObject
class QObjectBase(QObject): pass

class Mixin:                                  # Class thuần
    def helper(self):
        return "hi"

class MyClass(QObjectBase, Mixin):
    def __init__(self):
        QObjectBase.__init__(self)
        Mixin.__init__(self)
```

### 1.3. Quy tắc vàng

> **Chỉ có DUY NHẤT 1 class trong chuỗi kế thừa được là QObject (hoặc con của nó)**

Nếu bạn muốn kế thừa cả `QWidget` và `MyMixin`, thứ tự:

```python
class MyWidget(QWidget, MyMixin):            # QWidget đứng trước
    def __init__(self):
        super().__init__()                    # Gọi QWidget.__init__
        MyMixin.__init__(self)
```

### 1.4. Ví dụ: Widget với Logging Mixin

```python
import sys
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class LoggingMixin:
    """Mixin thêm khả năng log."""
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")


class MyWidget(QWidget, LoggingMixin):
    button_clicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        for name in ("OK", "Cancel"):
            btn = QPushButton(name)
            btn.clicked.connect(
                lambda checked=False, n=name: self._on_click(n)
            )
            layout.addWidget(btn)
    
    def _on_click(self, name: str):
        self.log(f"Clicked: {name}")          # Dùng method từ mixin
        self.button_clicked.emit(name)


app = QApplication(sys.argv)
w = MyWidget()
w.button_clicked.connect(lambda n: print(f"Signal: {n}"))
w.show()
sys.exit(app.exec())
```

👉 **Mixins hữu ích khi**: muốn tái sử dụng logic mà không phải kế thừa Qt class phức tạp.

---

## 🎯 PHẦN 2: SIGNAL VỚI CUSTOM TYPE PHỨC TẠP

### 2.1. Signal với Enum

```python
from enum import Enum, IntEnum
from PySide6.QtCore import QObject, Signal


class Status(Enum):
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"


class IntStatus(IntEnum):
    IDLE = 0
    RUNNING = 1
    DONE = 2


class Worker(QObject):
    # Signal với Enum
    status_changed = Signal(Status)
    
    # Signal với IntEnum (phổ biến hơn vì có thể dùng như int)
    int_status_changed = Signal(IntStatus)
    
    def set_status(self, s: Status):
        self.status_changed.emit(s)


w = Worker()
w.status_changed.connect(lambda s: print(f"Status: {s}, value: {s.value}"))
w.set_status(Status.RUNNING)
# Output: Status: Status.RUNNING, value: running
```

⚠️ **Chú ý**: Nếu bạn cần dùng Enum trong C++/QML, phải đăng ký với Qt:

```python
# PySide6 thường không cần, nhưng tốt cho C++ interop
# Trong C++: qRegisterMetaType<Status>("Status");
```

### 2.2. Signal với list & dict

```python
class DataManager(QObject):
    items_changed = Signal(list)
    config_changed = Signal(dict)
    tuple_ready = Signal(tuple)
    
    def notify(self):
        self.items_changed.emit([1, 2, 3])
        self.config_changed.emit({"theme": "dark"})
        self.tuple_ready.emit((1, "a", True))


mgr = DataManager()
mgr.items_changed.connect(lambda lst: print(f"List: {lst}, type: {type(lst)}"))
mgr.config_changed.connect(lambda d: print(f"Dict: {d}"))
mgr.notify()
```

### 2.3. Signal với dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    sender: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"{self.sender}: {self.content}"


class ChatRoom(QObject):
    message_received = Signal(Message)
    
    def receive(self, msg: Message):
        self.message_received.emit(msg)


room = ChatRoom()
room.message_received.connect(lambda m: print(f"[{m.timestamp:%H:%M}] {m}"))
room.receive(Message("An", "Chào!"))
room.receive(Message("Bình", "Hi!"))
```

### 2.4. Signal với `object` – Universal type

Khi bạn **không muốn giới hạn** kiểu:

```python
class EventBus(QObject):
    event = Signal(str, object)               # topic, payload
    
    def emit_event(self, topic: str, payload):
        self.event.emit(topic, payload)


bus = EventBus()
bus.event.connect(lambda t, p: print(f"{t}: {p} ({type(p).__name__})"))

bus.emit_event("user", {"id": 1, "name": "An"})
bus.emit_event("count", 42)
bus.emit_event("items", [1, 2, 3])
```

### 2.5. Signal không nhận `Optional` – workaround

```python
# ❌ Không khai báo được Signal(Optional[int])
# ✅ Dùng Signal(object)
value_ready = Signal(object)                  # None hoặc int đều OK
```

### 2.6. Signal với tham số mặc định – không có

Signal **KHÔNG** hỗ trợ default value. Nếu muốn, dùng overload:

```python
# Không có:
# signal = Signal(int, str="default")       # ❌

# Workaround: 1 signal, slot tự xử lý
value_ready = Signal(object)                  # Truyền None nếu không có
```

---

## 🎯 PHẦN 3: SIGNAL & PARENT-CHILD

### 3.1. Qt tự động quản lý lifecycle

Khi bạn connect signal của **parent** tới slot của **child**, Qt giữ **weak reference**. Khi 1 trong 2 bị hủy, connection tự động ngắt.

```python
class Parent(QWidget):
    parent_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.child = Child(self)              # child có parent
        self.parent_signal.connect(self.child.on_parent_signal)
    
    def emit_it(self):
        self.parent_signal.emit("hi")


class Child(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def on_parent_signal(self, msg):
        print(f"Child nhận: {msg}")


# Khi parent bị xóa → child cũng bị xóa → connection tự ngắt
```

### 3.2. Vấn đề với Python object thuần

Nếu slot là **hàm Python thuần** (không phải QObject), Qt không tự ngắt. Python có thể GC object → slot crash.

```python
# ❌ NGUY HIỂM
class Helper:                                 # Không phải QObject
    def do_something(self, msg):
        print(msg)

helper = Helper()
button.clicked.connect(helper.do_something)   # Qt giữ weak ref
del helper                                    # Python GC
button.click()                                # → crash?
```

**Giải pháp**: giữ reference

```python
self.helper = Helper()                        # Giữ trong self
button.clicked.connect(self.helper.do_something)
```

### 3.3. Kiểm tra object còn sống

```python
from PySide6.QtCore import QObject

def safe_slot(*args):
    # Kiểm tra sender còn sống không
    sender = QApplication.instance().sender() if hasattr(QApplication, 'instance') else None
    print("Sender:", sender)
```

Trong PySide6, slot là **bound method của QObject** thường an toàn.

### 3.4. Signal của widget con

```python
class Container(QWidget):
    item_clicked = Signal(str)                # Signal tổng hợp
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        for name in ["A", "B", "C"]:
            btn = QPushButton(name)
            # Forward signal của btn → signal của Container
            btn.clicked.connect(
                lambda checked=False, n=name: self.item_clicked.emit(n)
            )
            layout.addWidget(btn)


# Bên ngoài chỉ thấy 1 signal duy nhất
c = Container()
c.item_clicked.connect(lambda n: print(f"Clicked: {n}"))
```

👉 **Signal forwarding / aggregation** là pattern cực phổ biến khi làm compound widget.

---

## 🎯 PHẦN 4: SIGNAL FORWARDING – PATTERN QUAN TRỌNG

### 4.1. Vấn đề

Bạn có widget `FormWidget` chứa nhiều widget con. Bên ngoài muốn lắng nghe sự kiện của các widget con mà **không cần truy cập vào chúng**.

### 4.2. Giải pháp – Forward

```python
class FormWidget(QWidget):
    # Signal "tổng hợp" — clean API
    name_changed = Signal(str)
    email_changed = Signal(str)
    submitted = Signal()
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        self.txt_name = QLineEdit()
        self.txt_email = QLineEdit()
        btn_submit = QPushButton("Gửi")
        
        layout.addWidget(self.txt_name)
        layout.addWidget(self.txt_email)
        layout.addWidget(btn_submit)
        
        # ===== FORWARDING =====
        self.txt_name.textChanged.connect(self.name_changed)
        self.txt_email.textChanged.connect(self.email_changed)
        btn_submit.clicked.connect(self.submitted)
```

**Giải thích**: `self.name_changed` là **signal object** → có thể emit trực tiếp. Khi `textChanged` phát, nó cũng emit `name_changed` cùng tham số.

### 4.3. Forward với tham số chuyển đổi

Nếu tham số **khác kiểu**, cần lambda:

```python
class Widget(QWidget):
    age_changed = Signal(int)                 # Signal của ta: int
    
    def __init__(self):
        super().__init__()
        self.spin = QSpinBox()
        
        # spin.valueChanged phát int → không khác gì, forward thẳng
        self.spin.valueChanged.connect(self.age_changed)
        
        # Nếu muốn chuyển đổi:
        self.spin.valueChanged.connect(
            lambda v: self.age_changed.emit(v * 2)   # Ví dụ: gấp đôi
        )
```

### 4.4. Aggregate nhiều signal thành 1

```python
class MultiInput(QWidget):
    """Gộp nhiều input thành 1 signal duy nhất."""
    
    data_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.txt = QLineEdit()
        self.spin = QSpinBox()
        
        # Mỗi khi bất kỳ widget nào đổi → phát data_changed với full state
        self.txt.textChanged.connect(self._emit_all)
        self.spin.valueChanged.connect(self._emit_all)
    
    def _emit_all(self):
        self.data_changed.emit({
            "text": self.txt.text(),
            "value": self.spin.value(),
        })
```

**Ưu điểm**: Bên ngoài chỉ cần connect 1 signal, nhận full snapshot.

---

## 🎯 PHẦN 5: INTROSPECTION – XEM SIGNAL RUNTIME

### 5.1. Liệt kê signal của object

Qt cung cấp `QMetaObject` để xem:

```python
from PySide6.QtCore import QMetaObject, QMetaMethod
from PySide6.QtWidgets import QPushButton

btn = QPushButton("Test")

meta = btn.metaObject()
for i in range(meta.methodCount()):
    method = meta.method(i)
    if method.methodType() == QMetaMethod.MethodType.Signal:
        print(f"Signal: {method.methodSignature().data().decode()}")
```

Kết quả (QPushButton):
```
Signal: clicked()
Signal: clicked(bool)
Signal: pressed()
Signal: released()
Signal: toggled(bool)
Signal: destroyed()
Signal: destroyed(QObject*)
Signal: objectNameChanged(QString)
Signal: customContextMenuRequested(QPoint)
...
```

### 5.2. Kiểm tra 1 signal có tồn tại

```python
def has_signal(obj, name: str) -> bool:
    meta = obj.metaObject()
    for i in range(meta.methodCount()):
        m = meta.method(i)
        if m.methodType() == QMetaMethod.MethodType.Signal:
            sig = m.methodSignature().data().decode()
            if sig.startswith(f"{name}("):
                return True
    return False

print(has_signal(btn, "clicked"))              # True
print(has_signal(btn, "foo"))                  # False
```

### 5.3. Đếm số slot được connect

```python
# Qt không cung cấp API trực tiếp để đếm
# Workaround: dùng list riêng của bạn
self._connected_slots = []
button.clicked.connect(self.on_click)
self._connected_slots.append(self.on_click)
print(f"Có {len(self._connected_slots)} slot")
```

### 5.4. Ứng dụng: generic widget controller

```python
class SignalLogger:
    """Tự động log mọi signal của widget."""
    
    def __init__(self, widget, *signal_names):
        for name in signal_names:
            if hasattr(widget, name):
                sig = getattr(widget, name)
                sig.connect(
                    lambda *args, n=name: print(f"{widget.__class__.__name__}.{n}: {args}")
                )


btn = QPushButton("Test")
SignalLogger(btn, "clicked", "pressed", "released")
```

---

## 🎯 PHẦN 6: SIGNAL & QT DESIGNER

### 6.1. Vấn đề: Qt Designer tạo .ui

Qt Designer tạo file `.ui` (XML). Để dùng trong Python, có 3 cách:

| Cách | Khi nào |
|------|---------|
| **`pyside6-uic`** → convert thành `.py` | Sản xuất, nhanh, IDE hỗ trợ tốt |
| **`QUiLoader`** → load runtime | Prototype, không cần build |
| **Tự viết tay** | Không dùng Designer |

### 6.2. Cách 1 – Convert `.ui` → `.py`

**Bước 1**: Thiết kế trong Designer, lưu `form.ui`

**Bước 2**: Convert

```bash
pyside6-uic form.ui -o ui_form.py
```

**Bước 3**: Sinh ra file `ui_form.py`:

```python
# ui_form.py (auto-generated)
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Form)
        self.label = QLabel(Form)
        self.label.setText("Họ tên:")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QLineEdit(Form)
        self.verticalLayout.addWidget(self.lineEdit)
        self.btn_ok = QPushButton(Form)
        self.btn_ok.setText("OK")
        self.verticalLayout.addWidget(self.btn_ok)
        # ... (retranslateUi)
```

**Bước 4**: Tạo class kế thừa:

```python
# main.py
import sys
from PySide6.QtWidgets import QApplication, QWidget
from ui_form import Ui_Form


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Bây giờ có thể truy cập widget qua self.ui.xxx
        self.ui.btn_ok.clicked.connect(self.on_ok)
        self.ui.lineEdit.textChanged.connect(self.on_text_changed)
    
    def on_ok(self):
        name = self.ui.lineEdit.text()
        print(f"OK: {name}")
    
    def on_text_changed(self, text: str):
        print(f"Text: {text}")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

### 6.3. Cách 2 – QUiLoader (load runtime)

Không cần convert, load `.ui` trực tiếp:

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()
        file = QFile("form.ui")
        file.open(QFile.OpenModeFlag.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        
        # Widget từ .ui có parent là self
        # Truy cập qua findChild hoặc objectName
        btn = self.ui.findChild(QPushButton, "btn_ok")
        if btn:
            btn.clicked.connect(self.on_ok)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

### 6.4. Signal trong Qt Designer (Signal/Slot Editor)

Designer có **Signal/Slot Editor** (F4) cho phép connect **trực tiếp trong .ui**:

```xml
<connections>
    <connection>
        <sender>btn_ok</sender>
        <signal>clicked()</signal>
        <receiver>Form</receiver>
        <slot>accept()</slot>
    </connection>
</connections>
```

Nhưng trong Python, **KHÔNG NÊN** dùng cách này vì:
- Khó debug (không thấy trong code)
- Khó maintain khi đổi tên
- IDE không hỗ trợ

👉 **Best practice**: Tạo widget trong Designer, connect trong **Python code**.

### 6.5. Custom signal trong widget dùng Designer

Nếu bạn promote widget trong Designer thành custom class:

```python
# Trong Designer: promote QWidget thành MyWidget
# Tạo file mywidget.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class MyWidget(QWidget):
    custom_signal = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... setup
    
    def trigger(self):
        self.custom_signal.emit("hello")
```

Trong code chính:

```python
# Sau khi setupUi, tìm widget theo objectName
self.my_widget = self.ui.findChild(MyWidget, "my_widget")
self.my_widget.custom_signal.connect(self.on_custom)
```

### 6.6. Workflow chuẩn với Designer

```
1. Thiết kế .ui trong Qt Designer
   ↓
2. Convert: pyside6-uic form.ui -o ui_form.py
   ↓
3. Viết class MainWindow(QWidget) kế thừa, dùng Ui_Form
   ↓
4. Trong __init__, sau setupUi → connect signals
   ↓
5. Mọi logic nằm trong class của bạn, không sửa ui_form.py
```

⚠️ **KHÔNG BAO GIỜ** sửa file `ui_form.py` — mỗi lần regenerate sẽ mất.

---

## 🎯 PHẦN 7: VÍ DỤ THỰC HÀNH

### 7.1. Widget "Event Bus" hoàn chỉnh

Xây dựng event bus dùng Signal để giao tiếp giữa các widget **không biết nhau**:

```python
import sys
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget
)


# ============================================================
# EVENT BUS – singleton
# ============================================================
class EventBus(QObject):
    """Bus trung tâm cho mọi sự kiện."""
    
    # Các topic signal riêng
    user_added = Signal(dict)
    user_removed = Signal(str)
    log_message = Signal(str, str)           # (level, message)
    
    _instance = None
    
    @classmethod
    def instance(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance


bus = EventBus.instance()


# ============================================================
# USER FORM – không biết ai dùng nó
# ============================================================
class UserForm(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout(self)
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Tên user...")
        
        btn_add = QPushButton("Thêm")
        btn_add.clicked.connect(self._add)
        self.txt_name.returnPressed.connect(self._add)
        
        layout.addWidget(self.txt_name)
        layout.addWidget(btn_add)
    
    def _add(self):
        name = self.txt_name.text().strip()
        if not name:
            bus.log_message.emit("WARN", "Tên không được để trống")
            return
        
        user = {"id": name.lower().replace(" ", "_"), "name": name}
        bus.user_added.emit(user)                # Chỉ emit, không biết ai nhận
        self.txt_name.clear()


# ============================================================
# USER LIST – lắng nghe event bus
# ============================================================
class UserList(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Danh sách user:"))
        
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        btn_remove = QPushButton("Xóa user được chọn")
        btn_remove.clicked.connect(self._remove_selected)
        layout.addWidget(btn_remove)
        
        # Đăng ký nhận event
        bus.user_added.connect(self._on_user_added)
    
    def _on_user_added(self, user: dict):
        self.list.addItem(f"{user['name']} ({user['id']})")
        bus.log_message.emit("INFO", f"Đã thêm: {user['name']}")
    
    def _remove_selected(self):
        item = self.list.currentItem()
        if not item:
            bus.log_message.emit("WARN", "Chưa chọn user nào")
            return
        
        text = item.text()
        user_id = text.split("(")[-1].rstrip(")")
        bus.user_removed.emit(user_id)
        self.list.takeItem(self.list.row(item))


# ============================================================
# LOG PANEL – chỉ lắng nghe log
# ============================================================
class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Log:"))
        
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        layout.addWidget(self.txt)
        
        bus.log_message.connect(self._on_log)
    
    def _on_log(self, level: str, message: str):
        self.txt.append(f"[{level}] {message}")


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Bus Demo")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>User Form</b>"))
        layout.addWidget(UserForm())
        
        layout.addWidget(QLabel("<b>User List</b>"))
        layout.addWidget(UserList())
        
        layout.addWidget(QLabel("<b>Log</b>"))
        layout.addWidget(LogPanel())
        
        # Log sự kiện remove (nơi khác)
        bus.user_removed.connect(
            lambda uid: bus.log_message.emit("INFO", f"Đã xóa: {uid}")
        )


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

**Điểm hay**:
- **`UserForm`** không biết `UserList` tồn tại → chỉ emit
- **`UserList`** subscribe `user_added`
- **`LogPanel`** chỉ quan tâm `log_message`
- Thêm widget mới dễ: chỉ cần subscribe vào bus
- **Singleton pattern** cho bus

### 7.2. Widget forward signal – Compound Widget chuẩn

```python
class SearchBar(QWidget):
    """Search bar với input + nút + clear."""
    
    # Signals forward ra ngoài
    search_requested = Signal(str)
    text_changed = Signal(str)
    cleared = Signal()
    
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.txt = QLineEdit()
        self.txt.setPlaceholderText("Tìm kiếm...")
        self.txt.setClearButtonEnabled(True)
        
        self.btn = QPushButton("🔍 Tìm")
        
        layout.addWidget(self.txt, 1)
        layout.addWidget(self.btn)
        
        # Forward
        self.txt.textChanged.connect(self.text_changed)
        self.txt.returnPressed.connect(self._on_search)
        self.btn.clicked.connect(self._on_search)
        self.txt.textChanged.connect(self._on_text_changed)
    
    def _on_search(self):
        text = self.txt.text().strip()
        if text:
            self.search_requested.emit(text)
    
    def _on_text_changed(self, text: str):
        if not text:
            self.cleared.emit()
    
    # Public API
    def text(self) -> str:
        return self.txt.text()
    
    def setText(self, t: str):
        self.txt.setText(t)
    
    def clear(self):
        self.txt.clear()
```

Dùng:

```python
search = SearchBar()
search.search_requested.connect(self.do_search)
search.cleared.connect(self.reset_results)
```

---

## 🎯 PHẦN 8: BEST PRACTICES

### 8.1. Quy tắc đặt tên signal

| Loại | Đặt tên | Ví dụ |
|------|---------|-------|
| Sự kiện | `xxxChanged` | `valueChanged`, `textChanged` |
| Hành động | `xxxRequested` | `searchRequested`, `saveRequested` |
| Hoàn thành | `xxxFinished/Done/Completed` | `loadFinished` |
| Lỗi | `xxxError/Occurred` | `errorOccurred` |
| Trạng thái | `xxxStarted/Stopped` | `processStarted` |

### 8.2. Quy tắc tham số

- **Ít tham số** tốt hơn nhiều tham số
- **Quá 3 tham số** → gói vào dict/dataclass
- **Kiểu dữ liệu rõ ràng** → dễ maintain

```python
# ❌ Khó đọc
signal = Signal(str, str, int, bool, float)

# ✅ Rõ ràng
signal = Signal(dict)                          # {"name": ..., "age": ...}
# hoặc
signal = Signal(MyDataClass)
```

### 8.3. Signal naming convention

```python
# ✅ Dùng snake_case (PySide convention)
value_changed = Signal(int)

# ✅ Nhưng delegate signal của Qt dùng camelCase (theo Qt)
# Không tự đặt camelCase cho signal của mình
```

### 8.4. Tránh emit quá nhiều

Nếu signal phát **mỗi ký tự** khi user gõ → slot chạy liên tục. **Debounce** với `QTimer`:

```python
class DebouncedSearch(QWidget):
    search = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.txt = QLineEdit()
        self.txt.textChanged.connect(self._on_text_changed)
        
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._emit_search)
    
    def _on_text_changed(self, text: str):
        self.timer.start(300)                  # Debounce 300ms
    
    def _emit_search(self):
        self.search.emit(self.txt.text())
```

### 8.5. Signal cho API public – clean interface

Compound widget nên **expose signal** ra ngoài, không cho truy cập widget con:

```python
# ✅ Tốt
class FormWidget(QWidget):
    submitted = Signal(dict)
    cancelled = Signal()

# ❌ Không tốt – bên ngoài phụ thuộc vào cấu trúc bên trong
form = FormWidget()
form.txt_name.textChanged.connect(...)         # Phá vỡ encapsulation
```

---

## 📝 BÀI TẬP

### Bài tập 3.2.1 (Cơ bản)
Tạo class `ProcessManager(QObject)`:
- Signal `progressChanged(int, str)` – tiến độ + message
- Signal `finished(bool, str)` – thành công? message
- Signal `errorOccurred(Exception)`
- Method `start()` giả lập chạy process, phát các signal trên với `QTimer`

### Bài tập 3.2.2 (Trung bình)
Tạo **Compound Widget** `ContactCard`:
- Hiển thị avatar + tên + email + nút "Gọi", "Mail"
- Forward signals: `call_requested(str)`, `mail_requested(str)`
- Nhận `Contact` dataclass trong constructor

### Bài tập 3.2.3 (Khá)
Làm **event bus mạnh hơn**:
- Hỗ trợ `subscribe(topic, callback)` / `unsubscribe(topic, callback)`
- Có signal `any_event(str, object)` phát mọi event
- Có method `publish(topic, data)`
- Log tất cả event ra console (bonus: chỉ khi debug mode)

### Bài tập 3.2.4 (Nâng cao)
Tạo widget `MultiSelectList`:
- `QListWidget` với checkbox
- Signal `selectionChanged(list)` – phát list items được chọn
- Signal `itemToggled(str, bool)` – phát từng lần toggle
- Forward đúng cách, không để lộ QListWidget

### Bài tập 3.2.5 (Khó)
Xây dựng **Undo/Redo với Signal**:
- Class `Command` với `execute()` và `undo()`
- Class `CommandManager(QObject)`:
  - `push(cmd: Command)`
  - Signal `canUndoChanged(bool)`, `canRedoChanged(bool)`
  - Signal `commandExecuted(str)` (mô tả)
- Demo với add/remove item trong list

---

## ✅ CHECKLIST SAU BÀI 3.2

- [ ] Hiểu **multiple inheritance** với QObject (1 Qt class + mixins)
- [ ] Định nghĩa được signal với Enum, list, dict, dataclass
- [ ] Biết dùng `Signal(object)` cho universal type
- [ ] Hiểu parent-child ảnh hưởng signal lifecycle
- [ ] Biết pattern **signal forwarding**
- [ ] Biết pattern **signal aggregation** (gộp nhiều signal)
- [ ] Biết dùng `QMetaObject` để introspection
- [ ] Biết 2 cách dùng Qt Designer: `pyside6-uic` và `QUiLoader`
- [ ] Hiểu quy tắc: tạo UI trong Designer, connect signal trong code
- [ ] Biết best practices: naming, debounce, expose signal thay vì widget con
- [ ] Hoàn thành ít nhất 3 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 3.3 – Event System: Override Event Handlers**

- Phân biệt **Event** vs **Signal** (nhắc lại, sâu hơn)
- `QEvent` hierarchy: `QMouseEvent`, `QKeyEvent`, `QPaintEvent`, `QResizeEvent`, `QCloseEvent`...
- **Override event handlers**: `mousePressEvent`, `keyPressEvent`, `paintEvent`, `resizeEvent`, `enterEvent`, `leaveEvent`...
- **`event()` override** – chặn tất cả event
- **`QEvent.accept()` vs `QEvent.ignore()`** – propagation
- **Focus events**: `focusInEvent`, `focusOutEvent`
- **Drag & Drop events**: `dragEnterEvent`, `dropEvent`
- Project: **Paint app đơn giản** dùng mouse events

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 3.3 – Event System**?
2. **Giải chi tiết một bài tập 3.2.x** nào?
3. **Đào sâu** phần nào (ví dụ: Qt Designer workflow, Event Bus nâng cao, multiple inheritance)?

Bạn cũng có thể gửi code bạn viết cho bài tập, tôi sẽ review và góp ý! 🚀