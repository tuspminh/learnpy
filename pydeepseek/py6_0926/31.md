# 📘 MODULE 3 – BÀI 3.1: SIGNAL & SLOT CHI TIẾT

> **Mục tiêu bài học**:
> - Hiểu **bản chất** Signal/Slot – không chỉ cách dùng
> - Phân biệt **Signal** vs **Event** (hay bị nhầm)
> - Nắm **Connection Types**: Auto, Direct, Queued, BlockingQueued
> - Biết **overload signal** và **signal có tham số phức tạp**
> - Hiểu **disconnect**, **blockSignals**, tránh vòng lặp vô hạn
> - Biết khi nào Signal **không phát** và cách debug
> - Hiểu **lambda + closure** trong connect

---

## 🎯 PHẦN 1: SIGNAL/SLOT LÀ GÌ? – GÓC NHÌN BẢN CHẤT

### 1.1. Định nghĩa

**Signal/Slot** là cơ chế giao tiếp **loose coupling** (liên kết lỏng) giữa các QObject:

- **Signal**: sự kiện được phát ra (emit) khi có gì đó xảy ra
- **Slot**: hàm được gọi khi signal phát ra

```
   ┌─────────────┐                       ┌─────────────┐
   │  Object A   │  ──── signal ────▶    │  Object B   │
   │ (phát tín   │                       │  (nhận và   │
   │   hiệu)     │                       │   xử lý)    │
   └─────────────┘                       └─────────────┘
```

### 1.2. Tại sao cần Signal/Slot?

**Cách 1 – Không dùng Signal/Slot (tight coupling)**:

```python
class Button:
    def click(self):
        # Button phải biết về Dialog → coupling chặt
        dialog = Dialog()
        dialog.save_file()
```

❌ Button phải biết Dialog, phải import, phải gọi đúng method. Nếu Dialog đổi API → Button hỏng.

**Cách 2 – Dùng Signal/Slot (loose coupling)**:

```python
class Button(QObject):
    clicked = Signal()
    
    def click(self):
        self.clicked.emit()                # Chỉ phát tín hiệu

# Ở đâu đó khác:
button.clicked.connect(dialog.save_file)
```

✅ Button **không cần biết** Dialog tồn tại. Ai cần thì tự connect.

### 1.3. Cú pháp cơ bản

```python
# 1. Định nghĩa signal (chỉ trong class kế thừa QObject)
class MyClass(QObject):
    my_signal = Signal()                    # Không tham số
    value_changed = Signal(int)             # 1 tham số int
    data_ready = Signal(str, list)          # Nhiều tham số

# 2. Phát signal
obj.my_signal.emit()

# 3. Kết nối
obj.my_signal.connect(slot_function)

# 4. Ngắt kết nối
obj.my_signal.disconnect(slot_function)
```

### 1.4. Signal có thể connect tới đâu?

Signal có thể connect tới **bất kỳ callable nào**:

```python
# 1. Method của QObject
button.clicked.connect(self.on_click)

# 2. Hàm thường (module-level)
button.clicked.connect(print)

# 3. Lambda
button.clicked.connect(lambda: print("Clicked!"))

# 4. Built-in function
button.clicked.connect(self.close)

# 5. Signal khác (signal-to-signal)
button1.clicked.connect(button2.click)      # Nối 2 signal
```

### 1.5. Signal-to-signal – Nối chuỗi

```python
class Widget(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.slider = QSlider()
        # Khi slider đổi → phát signal của Widget
        self.slider.valueChanged.connect(self.valueChanged)
        # (không cần .emit() vì signal có thể emit signal khác trực tiếp)
```

---

## 🎯 PHẦN 2: SIGNAL vs EVENT – HAY BỊ NHẦM

### 2.1. Bảng so sánh

| Tiêu chí | Signal | Event |
|----------|--------|-------|
| **Bản chất** | Thông báo "có gì đã xảy ra" | Gói dữ liệu sự kiện |
| **Class** | `Signal(...)` | `QEvent` |
| **Phát/nhận** | `.emit()` / `.connect()` | `QApplication.sendEvent()` / override `xxxEvent()` |
| **Ai phát** | Bạn chủ động | Qt tự động (OS → Qt → widget) |
| **Đối tượng** | Bất kỳ callable | Chỉ method của QObject |
| **Ví dụ** | `clicked`, `textChanged` | `QMouseEvent`, `QKeyEvent`, `QPaintEvent` |

### 2.2. Ví dụ minh họa

**Signal**: Khi user click nút, `QPushButton` **emit** `clicked`:

```python
button.clicked.connect(self.handle)         # Bạn connect
```

**Event**: Khi user nhấn chuột, OS gửi event đến Qt, Qt gửi đến widget:

```python
class MyWidget(QWidget):
    def mousePressEvent(self, event: QMouseEvent):
        print("Clicked at:", event.position())
        super().mousePressEvent(event)      # Gọi cha để xử lý mặc định
```

### 2.3. Chuyển Event thành Signal

Nhiều widget trong Qt làm điều này:

```
OS ──mouse press──▶ QWidget::mousePressEvent() ──▶ emit clicked() ──▶ slot
```

👉 **Quan hệ**: Event là **tầng thấp**, Signal là **tầng cao** được xây trên Event.

### 2.4. Khi nào dùng cái nào?

| Tình huống | Dùng |
|-----------|------|
| Kết nối 2 object đã có sẵn | **Signal/Slot** |
| Custom widget cần biết mouse/keyboard | **Override Event** |
| Cần lọc event trước khi widget xử lý | **Event Filter** |
| Thông báo trạng thái thay đổi | **Signal** |

---

## 🎯 PHẦN 3: SIGNAL CÓ THAM SỐ

### 3.1. Signal với nhiều tham số

```python
from PySide6.QtCore import QObject, Signal

class DataProcessor(QObject):
    # Signal với nhiều loại tham số
    data_received = Signal(str, int, float)
    error_occurred = Signal(str, Exception)         # Có thể dùng Exception
    progress = Signal(int, str)
    
    def process(self):
        self.data_received.emit("Hello", 42, 3.14)
        self.error_occurred.emit("Lỗi mạng", ValueError("Timeout"))
        self.progress.emit(50, "Đang xử lý...")

# Connect
proc = DataProcessor()
proc.data_received.connect(lambda s, i, f: print(f"{s} {i} {f}"))
proc.error_occurred.connect(lambda msg, e: print(f"{msg}: {e}"))
proc.progress.connect(lambda pct, msg: print(f"{pct}% - {msg}"))
```

### 3.2. Signal với custom type

Muốn dùng custom type trong signal, cần khai báo với Qt:

```python
from PySide6.QtCore import QObject, Signal, QObject
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

class UserManager(QObject):
    user_added = Signal(User)                # Signal với custom class
    user_list_updated = Signal(list)         # list cũng OK
    
    def add_user(self, user: User):
        self.user_added.emit(user)

# Connect
mgr = UserManager()
mgr.user_added.connect(lambda u: print(f"User: {u.name}, {u.age}"))
mgr.add_user(User("An", 25))
```

⚠️ **Lưu ý**: Với PySide6, custom Python type thường hoạt động ngay. Với PyQt hoặc C++, đôi khi cần `qRegisterMetaType`.

### 3.3. Signal overload – Cùng tên, khác tham số

Một số signal có nhiều phiên bản:

```python
# QComboBox có 2 signal currentIndexChanged:
# - currentIndexChanged(int)
# - currentIndexChanged(str)

combo.currentIndexChanged[int].connect(self.on_index)    # Chỉ int
combo.currentIndexChanged[str].connect(self.on_text)     # Chỉ str
```

Với signal tự định nghĩa:

```python
class MyClass(QObject):
    valueChanged = Signal(int)
    valueChanged = Signal(str)                # ❌ Không được — Python không hỗ trợ overload
```

👉 **Kết luận**: Overload chỉ có sẵn trên signal của Qt, không tự định nghĩa được trong Python.

### 3.4. Signal với `object` – Bất kỳ

```python
from PySide6.QtCore import Signal

class Emitter(QObject):
    any_data = Signal(object)                # Nhận bất kỳ Python object
    
    def send(self, data):
        self.any_data.emit(data)             # dict, list, custom... đều OK
```

Dùng khi bạn không chắc kiểu dữ liệu.

---

## 🎯 PHẦN 4: CONNECTION TYPES – QUAN TRỌNG

### 4.1. 4 loại Connection Type

Khi connect, Qt có 4 chế độ:

| Type | Khi nào slot chạy | Dùng khi |
|------|-------------------|----------|
| **`AutoConnection`** | Tự động (mặc định) | **99% trường hợp** |
| **`DirectConnection`** | Ngay lập tức, cùng thread | Cùng thread, cần đồng bộ |
| **`QueuedConnection`** | Xếp vào event queue | **Khác thread** |
| **`BlockingQueuedConnection`** | Như Queued nhưng chờ | Cross-thread cần đợi |

### 4.2. AutoConnection – "thông minh"

Qt tự quyết định dựa vào **thread của sender và receiver**:

- Cùng thread → `DirectConnection`
- Khác thread → `QueuedConnection`

```python
# Mặc định là Auto, không cần ghi
button.clicked.connect(self.on_click)
```

### 4.3. DirectConnection – chạy ngay

```python
from PySide6.QtCore import Qt

button.clicked.connect(
    self.on_click,
    Qt.ConnectionType.DirectConnection
)
```

⚠️ **Nguy hiểm**: Nếu sender ở thread A, receiver ở thread B, `DirectConnection` sẽ chạy slot **trong thread A** → có thể race condition.

### 4.4. QueuedConnection – xếp hàng

```python
signal.connect(slot, Qt.ConnectionType.QueuedConnection)
```

Slot chạy **sau** khi control quay về event loop của thread receiver. An toàn với đa luồng.

### 4.5. Ví dụ minh họa

```python
from PySide6.QtCore import QObject, Signal, Qt, QThread, QTimer
from PySide6.QtWidgets import QApplication
import sys, threading

class Emitter(QObject):
    sig = Signal()

def receiver_slot():
    print(f"Slot chạy ở thread: {threading.get_ident()}")

app = QApplication(sys.argv)
print(f"Main thread: {threading.get_ident()}")

emitter = Emitter()
emitter.sig.connect(receiver_slot, Qt.ConnectionType.DirectConnection)
emitter.sig.emit()                            # Chạy ngay, cùng thread
```

Sẽ học kỹ hơn trong Module 8 (Threading).

---

## 🎯 PHẦN 5: DISCONNECT & BLOCK SIGNALS

### 5.1. Disconnect – Ngắt kết nối

```python
# Ngắt 1 slot cụ thể
button.clicked.disconnect(self.on_click)

# Ngắt tất cả slot của signal
button.clicked.disconnect()

# Ngắt tất cả signal của object
obj.disconnect()
```

### 5.2. Khi nào cần disconnect?

**Trường hợp 1: Đối tượng bị xóa**

Qt **tự động disconnect** khi QObject bị hủy. Với Python object thuần, bạn phải tự lo.

```python
# Nếu self.on_click là bound method của self
# và self bị xóa → Qt tự ngắt (nhờ parent-child)
```

**Trường hợp 2: Tránh slot gọi nhiều lần**

```python
# Nếu connect nhiều lần → slot chạy nhiều lần
button.clicked.connect(self.on_click)
button.clicked.connect(self.on_click)         # ❌ Gọi 2 lần khi click

# Đúng: dùng UniqueConnection
button.clicked.connect(
    self.on_click,
    Qt.ConnectionType.UniqueConnection
)
```

**Trường hợp 3: Đổi hành vi runtime**

```python
def setup_mode_a(self):
    self.btn.clicked.disconnect()
    self.btn.clicked.connect(self.on_mode_a)

def setup_mode_b(self):
    self.btn.clicked.disconnect()
    self.btn.clicked.connect(self.on_mode_b)
```

### 5.3. blockSignals – Tạm ngưng phát signal

```python
# Tạm ngưng
widget.blockSignals(True)
widget.setValue(50)                          # Không phát valueChanged
widget.blockSignals(False)

# Kiểm tra
is_blocked = widget.signalsBlocked()
```

💡 **Ứng dụng**: Khi bạn **set giá trị từ code** và **không muốn** slot chạy.

**Ví dụ điển hình**:

```python
# Synchronize 2 spinbox
def on_spin1_changed(self, value):
    self.spin2.blockSignals(True)            # Chặn spin2 phát signal
    self.spin2.setValue(value)
    self.spin2.blockSignals(False)           # Bật lại

# Không có blockSignals → vòng lặp vô hạn:
# spin1 đổi → on_spin1 → spin2.setValue → on_spin2 → spin1.setValue → ...
```

### 5.4. Ví dụ: vòng lặp vô hạn – cách nhận biết

```python
# ❌ CODE SAI – gây RecursionError
spin1.valueChanged.connect(spin2.setValue)
spin2.valueChanged.connect(spin1.setValue)
```

Khi kéo spin1 từ 0 → 1:
```
spin1.valueChanged(1) → spin2.setValue(1) → spin2.valueChanged(1)
  → spin1.setValue(1) → spin1.valueChanged(1) (giá trị không đổi, nhưng vẫn emit!)
    → spin2.setValue(1) → ...
```

**Fix**:

```python
def on_spin1_changed(self, value):
    if self.spin2.value() != value:
        self.spin2.setValue(value)

def on_spin2_changed(self, value):
    if self.spin1.value() != value:
        self.spin1.setValue(value)
```

Hoặc `blockSignals` như trên.

---

## 🎯 PHẦN 6: LAMBDA & CLOSURE – CẨN THẬN BUG

### 6.1. Vấn đề late-binding trong vòng lặp

```python
# ❌ BUG: Tất cả nút đều in "Button 2"
for i in range(3):
    btn = QPushButton(f"Button {i}")
    btn.clicked.connect(lambda: print(f"Clicked {i}"))
```

Vì lambda bắt **biến i theo tham chiếu**, khi vòng lặp kết thúc, i = 2.

### 6.2. Fix – default argument

```python
# ✅ Đúng: capture i theo giá trị
for i in range(3):
    btn = QPushButton(f"Button {i}")
    btn.clicked.connect(lambda checked=False, i=i: print(f"Clicked {i}"))
```

**Giải thích**:
- `i=i`: default argument, được đánh giá **tại thời điểm định nghĩa lambda**
- `checked=False`: Qt truyền `checked` (bool) cho slot → cần placeholder

### 6.3. Signal có tham số – lambda nhận đúng

```python
button.clicked.connect(lambda: self.on_click())              # Không nhận gì
button.clicked.connect(lambda checked: self.on_click())      # Nhận checked
button.clicked.connect(lambda checked=False: self.on_click())
```

QPushButton.clicked có 2 overload:
- `clicked()` – không tham số
- `clicked(bool)` – có checked

Lambda cần **khớp** với overload đang dùng.

### 6.4. Bound method vs lambda – khi nào dùng?

| Trường hợp | Dùng |
|-----------|------|
| Gọi method của self | `self.on_click` (bound method) |
| Cần truyền thêm tham số | `lambda: self.on_click(arg)` |
| Loop với biến | `lambda i=i: ...` |
| Đơn giản, ngắn | `lambda: print("hi")` |

**Performance**: Bound method nhanh hơn lambda một chút. Với hàng nghìn connect, dùng bound method.

---

## 🎯 PHẦN 7: SIGNAL KHÔNG PHÁT – DEBUG

### 7.1. Checklist khi signal không hoạt động

1. **Signal có tồn tại không?**
   ```python
   print(dir(button))                       # Kiểm tra
   ```

2. **Connect trước khi emit không?**
   ```python
   # ❌ Sai
   button.clicked.emit()
   button.clicked.connect(slot)              # Quá muộn
   
   # ✅ Đúng
   button.clicked.connect(slot)
   button.clicked.emit()
   ```

3. **Có gọi emit không?** (với custom signal)
   ```python
   class MyWidget(QWidget):
       my_signal = Signal()
       
       def do_something(self):
           # ❌ Quên emit
           # ✅ Đúng
           self.my_signal.emit()
   ```

4. **Object có bị garbage collected không?**
   ```python
   # ❌ Sai: obj không giữ reference
   MyClass().my_signal.connect(slot)          # Ngay sau dòng này, obj bị GC
   
   # ✅ Đúng
   self.obj = MyClass()
   self.obj.my_signal.connect(slot)
   ```

5. **Có bị blockSignals?**
   ```python
   print(widget.signalsBlocked())
   ```

6. **Có bị disconnect?**
   ```python
   # Python không có cách "xem" list connected slots dễ dàng
   # Nhưng Qt có: QObject.receivers(signal)
   ```

### 7.2. Debug bằng cách in

```python
def debug_slot(*args):
    print(f"Slot nhận: {args}")

button.clicked.connect(debug_slot)
```

### 7.3. Signal của widget con không phát?

Widget con đôi khi không phát signal vì bạn **quên set parent** hoặc **quên show**.

---

## 🎯 PHẦN 8: VÍ DỤ THỰC HÀNH

### 8.1. Custom widget với signal đa dạng

```python
import sys
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QTextEdit, QGroupBox, QFormLayout
)


class FormWidget(QWidget):
    """Form đơn giản, phát signal khi submit."""
    
    submitted = Signal(dict)                 # data
    cancelled = Signal()
    field_changed = Signal(str, object)      # (field_name, value)
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Form
        group = QGroupBox("Thông tin")
        form = QFormLayout(group)
        
        self.txt_name = QLineEdit()
        self.txt_name.textChanged.connect(
            lambda t: self.field_changed.emit("name", t)
        )
        form.addRow("Tên:", self.txt_name)
        
        self.cbo_role = QComboBox()
        self.cbo_role.addItems(["Admin", "User", "Guest"])
        self.cbo_role.currentTextChanged.connect(
            lambda t: self.field_changed.emit("role", t)
        )
        form.addRow("Vai trò:", self.cbo_role)
        
        self.spin_age = QSpinBox()
        self.spin_age.setRange(1, 120)
        self.spin_age.valueChanged.connect(
            lambda v: self.field_changed.emit("age", v)
        )
        form.addRow("Tuổi:", self.spin_age)
        
        layout.addWidget(group)
        
        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()
        
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.cancelled)
        
        btn_submit = QPushButton("Gửi")
        btn_submit.clicked.connect(self._on_submit)
        
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_submit)
        layout.addLayout(btns)
    
    def _on_submit(self):
        data = {
            "name": self.txt_name.text(),
            "role": self.cbo_role.currentText(),
            "age": self.spin_age.value(),
        }
        self.submitted.emit(data)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Demo")
        self.resize(400, 400)
        
        layout = QVBoxLayout(self)
        
        self.form = FormWidget()
        self.form.submitted.connect(self.on_submit)
        self.form.cancelled.connect(self.on_cancel)
        self.form.field_changed.connect(self.on_field_changed)
        layout.addWidget(self.form)
        
        self.lbl_log = QLabel("Chưa có gì")
        self.lbl_log.setStyleSheet("color: #666; padding: 10px;")
        self.lbl_log.setWordWrap(True)
        layout.addWidget(self.lbl_log)
        
        self.log_lines = []
    
    def on_submit(self, data: dict):
        print(f"Submitted: {data}")
        self.lbl_log.setText(f"Gửi thành công: {data}")
    
    def on_cancel(self):
        print("Cancelled")
        self.lbl_log.setText("Đã hủy")
    
    def on_field_changed(self, name: str, value):
        self.log_lines.append(f"{name} = {value}")
        self.log_lines = self.log_lines[-5:]     # Giữ 5 dòng cuối
        self.lbl_log.setText("\n".join(self.log_lines))


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

**Điểm hay**:
- `submitted = Signal(dict)` – phát 1 dict thay vì nhiều tham số
- `field_changed = Signal(str, object)` – `object` cho phép bất kỳ kiểu
- `btn_cancel.clicked.connect(self.cancelled)` – nối signal → signal
- Tách biệt hoàn toàn: FormWidget không cần biết ai dùng nó

### 8.2. Signal-to-signal chain

```python
class Processor(QObject):
    data_in = Signal(str)
    data_out = Signal(str)
    
    def __init__(self):
        super().__init__()
        # Nối data_in → transform → data_out
        self.data_in.connect(self._transform)
    
    def _transform(self, text: str):
        result = text.upper()
        self.data_out.emit(result)


proc = Processor()
proc.data_out.connect(lambda x: print(f"Out: {x}"))
proc.data_in.emit("hello")                    # In: Out: HELLO
```

---

## 🎯 PHẦN 9: PERFORMANCE & BEST PRACTICES

### 9.1. Khi có nhiều signal

Nếu bạn có **hàng nghìn** object, mỗi object có signal → khởi tạo signal tốn bộ nhớ.

**Giải pháp**: chỉ định nghĩa signal ở class, Qt tối ưu.

### 9.2. Tránh lambda khi không cần

```python
# ❌ Không cần lambda
button.clicked.connect(lambda: self.on_click())

# ✅ Dùng bound method
button.clicked.connect(self.on_click)
```

### 9.3. Tránh connect trùng

```python
# Nếu setup gọi nhiều lần → slot chạy nhiều lần
button.clicked.connect(self.on_click, Qt.ConnectionType.UniqueConnection)
```

### 9.4. Dùng blockSignals khi set value từ code

Đã nói ở Phần 5.3.

### 9.5. Disconnect khi không cần

Nếu slot chỉ cần chạy 1 lần:

```python
def on_first_click(self):
    print("Chỉ chạy lần đầu")
    self.btn.clicked.disconnect(self.on_first_click)
    # Tiếp tục xử lý

self.btn.clicked.connect(self.on_first_click)
```

Hoặc:

```python
from PySide6.QtCore import Qt
btn.clicked.connect(
    self.on_first_click,
    Qt.ConnectionType.SingleShotConnection    # Qt 6.5+
)
```

---

## 📝 BÀI TẬP

### Bài tập 3.1.1 (Cơ bản)
Tạo class `Counter(QObject)`:
- Có signal `countChanged(int)` phát khi đếm thay đổi
- Có signal `reachedMax()` phát khi đạt 10
- Có method `increment()`, `reset()`
- Viết demo connect 2 signal tới 2 slot khác nhau

### Bài tập 3.1.2 (Trung bình)
Làm widget `SearchBox`:
- Có `QLineEdit` và `QPushButton` "Tìm"
- Signal `searchRequested(str)` khi bấm nút hoặc Enter
- Signal `textCleared()` khi clear
- Khi text thay đổi → phát `textChanged(str)`

### Bài tập 3.1.3 (Khá)
Tạo **hệ thống event bus** đơn giản dùng Signal:

```python
class EventBus(QObject):
    message = Signal(str, object)
    
    def publish(self, topic: str, data: object):
        self.message.emit(topic, data)

bus = EventBus()

# Nhiều "subscriber" cùng lắng nghe, nhưng chỉ quan tâm topic nhất định
bus.message.connect(lambda topic, data: 
    print(f"A nhận: {data}") if topic == "user" else None
)
bus.message.connect(lambda topic, data:
    print(f"B nhận: {data}") if topic == "order" else None
)

bus.publish("user", {"name": "An"})       # Chỉ A in
bus.publish("order", {"id": 123})         # Chỉ B in
```

### Bài tập 3.1.4 (Nâng cao)
Cho đoạn code sau, tìm và sửa bug:

```python
class BuggyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.spin1 = QSpinBox()
        self.spin2 = QSpinBox()
        self.spin1.valueChanged.connect(self.spin2.setValue)
        self.spin2.valueChanged.connect(self.spin1.setValue)
        # Đặt spin1 = 5, spin2 = 10
        self.spin1.setValue(5)
        self.spin2.setValue(10)
        # BUG: Khi user đổi giá trị → chương trình treo
```

💡 **Gợi ý**: Vòng lặp vô hạn. Fix bằng `blockSignals` hoặc so sánh giá trị.

### Bài tập 3.1.5 (Khó)
Làm widget `MultiStepForm` với nhiều bước:
- Bước 1 → 2 → 3 → Submit
- Mỗi bước phát signal `stepCompleted(int, dict)` khi user Next
- Signal `stepBack(int)` khi user Back
- Signal `formSubmitted(dict)` khi submit
- Cho phép validate từng bước

---

## ✅ CHECKLIST SAU BÀI 3.1

- [ ] Hiểu bản chất Signal/Slot – loose coupling
- [ ] Phân biệt rõ **Signal** vs **Event**
- [ ] Biết định nghĩa signal với nhiều tham số
- [ ] Biết signal-to-signal chain
- [ ] Hiểu 4 Connection Types: Auto, Direct, Queued, BlockingQueued
- [ ] Biết `disconnect()`, `blockSignals()`, `UniqueConnection`
- [ ] Nhận diện được **bug closure** trong lambda
- [ ] Biết debug khi signal không phát
- [ ] Tránh được vòng lặp vô hạn khi 2 widget sync
- [ ] Hoàn thành ít nhất 3 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 3.2 – Custom Signal nâng cao & Signal với Qt Designer**

- Signal với tham số phức tạp (list các object, custom enum)
- Signal trong **multiple inheritance**
- Signal với **parent-child** – tự động disconnect
- `QMetaObject` và introspection
- Debug nâng cao

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 3.2**?
2. **Giải chi tiết một bài tập 3.1.x** nào?
3. **Đào sâu** phần nào (ví dụ: Connection Types với thread, overload signal, Event System)?