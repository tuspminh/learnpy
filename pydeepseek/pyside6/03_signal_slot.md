Chào mừng bạn đến **Bài 3: Signals & Slots - Trái tim của PySide6**!

Nếu Layout là "bộ xương" của ứng dụng, thì Signals & Slots chính là "hệ thần kinh" - giúp các thành phần giao tiếp và phản ứng với nhau. Hôm nay chúng ta sẽ đi sâu vào cơ chế này, từ cơ bản đến nâng cao.

---

## Mục tiêu bài học

Sau bài này, bạn sẽ:
1. Hiểu sâu về cơ chế Signals & Slots
2. Kết nối nhiều Slot với một Signal
3. Tạo Signal tùy chỉnh với dữ liệu phức tạp
4. Sử dụng Lambda để truyền tham số linh hoạt
5. Xử lý sự kiện từ bàn phím và chuột

---

## Phần 1: Ôn tập và đào sâu Signals & Slots

### 1.1. Cơ chế hoạt động

Signals & Slots là một **cơ chế giao tiếp an toàn theo kiểu Observer Pattern**:

```
[Đối tượng A] --phát signal--> [Hệ thống Qt] --gọi slot--> [Đối tượng B]
     |                           |
  Sự kiện xảy ra          Kết nối được thiết lập
  (click, text change...)  qua connect()
```

**Ưu điểm:**
- **Loosely coupled** (kết nối lỏng lẻo): A không cần biết B là ai
- **Type-safe**: Kiểm tra kiểu dữ liệu tại compile time
- **Thread-safe**: Có thể giao tiếp giữa các luồng khác nhau

### 1.2. Các Signal phổ biến của Widgets

| Widget | Signal | Dữ liệu gửi kèm |
|--------|--------|----------------|
| `QPushButton` | `clicked()` | Không có |
| `QPushButton` | `pressed()` / `released()` | Không có |
| `QLineEdit` | `textChanged(text)` | `str` |
| `QLineEdit` | `returnPressed()` | Không có |
| `QCheckBox` | `stateChanged(state)` | `int` (0/2) |
| `QComboBox` | `currentTextChanged(text)` | `str` |
| `QComboBox` | `currentIndexChanged(index)` | `int` |
| `QSlider` | `valueChanged(value)` | `int` |

### Ví dụ: Kết nối cơ bản

```python
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt


class BasicSignalsExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signals & Slots cơ bản")
        self.resize(400, 300)

        # Tạo layout
        layout = QVBoxLayout()

        # Tạo widget
        self.label = QLabel("Nhập gì đó vào ô bên dưới:")
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Gõ chữ vào đây...")
        self.button = QPushButton("Xóa text")
        self.result_label = QLabel("Kết quả sẽ hiện ở đây")

        # Thêm vào layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        # === KẾT NỐI SIGNALS ===

        # 1. Signal đơn giản, không có dữ liệu
        self.button.clicked.connect(self.clear_text)

        # 2. Signal có dữ liệu (text)
        self.line_edit.textChanged.connect(self.on_text_changed)

        # 3. Kết nối nhiều Signal vào cùng một Slot
        self.line_edit.returnPressed.connect(self.on_enter_pressed)
        self.button.clicked.connect(self.on_button_clicked_too)

    def clear_text(self):
        self.line_edit.clear()

    def on_text_changed(self, text):
        self.result_label.setText(f"Đang gõ: {text}")

    def on_enter_pressed(self):
        self.result_label.setText(f"Đã nhấn Enter: {self.line_edit.text()}")

    def on_button_clicked_too(self):
        print("Nút cũng được click từ một slot khác!")


app = QApplication(sys.argv)
window = BasicSignalsExample()
window.show()
sys.exit(app.exec())
```

---

## Phần 2: Kết nối nâng cao

### 2.1. Một Signal - Nhiều Slots

```python
class MultiSlotsExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.button = QPushButton("Click vào tôi!")
        self.label1 = QLabel("Label 1")
        self.label2 = QLabel("Label 2")
        self.label3 = QLabel("Label 3")
        
        layout.addWidget(self.button)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)
        self.setLayout(layout)
        
        # MỘT Signal - NHIỀU Slots (chạy theo thứ tự kết nối)
        self.button.clicked.connect(self.update_label1)
        self.button.clicked.connect(self.update_label2)
        self.button.clicked.connect(self.update_label3)
    
    def update_label1(self):
        self.label1.setText("Label 1 đã được click!")
    
    def update_label2(self):
        self.label2.setText("Label 2 đã được click!")
    
    def update_label3(self):
        self.label3.setText("Label 3 đã được click!")
```

### 2.2. Nhiều Signals - Một Slot

```python
class MultiSignalsExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.btn1 = QPushButton("Nút 1")
        self.btn2 = QPushButton("Nút 2")
        self.btn3 = QPushButton("Nút 3")
        self.label = QLabel("Chưa có nút nào được click")
        
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # NHIỀU Signals - MỘT Slot
        self.btn1.clicked.connect(lambda: self.on_any_button_clicked("Nút 1"))
        self.btn2.clicked.connect(lambda: self.on_any_button_clicked("Nút 2"))
        self.btn3.clicked.connect(lambda: self.on_any_button_clicked("Nút 3"))
    
    def on_any_button_clicked(self, button_name):
        self.label.setText(f"Bạn vừa click: {button_name}")
```

### 2.3. Ngắt kết nối (Disconnect)

```python
class DisconnectExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.button = QPushButton("Click me")
        self.toggle_btn = QPushButton("Bật/Tắt kết nối")
        self.label = QLabel("Kết nối đang BẬT")
        self.connected = True
        
        layout.addWidget(self.button)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Lưu connection để ngắt sau
        self.connection = self.button.clicked.connect(self.on_button_click)
        self.toggle_btn.clicked.connect(self.toggle_connection)
    
    def on_button_click(self):
        print("Nút được click!")
        self.label.setText("Nút đã được click!")
    
    def toggle_connection(self):
        if self.connected:
            # Ngắt kết nối
            self.button.clicked.disconnect(self.connection)
            self.connected = False
            self.label.setText("Kết nối đã TẮT")
            self.toggle_btn.setText("Bật kết nối")
        else:
            # Kết nối lại
            self.connection = self.button.clicked.connect(self.on_button_click)
            self.connected = True
            self.label.setText("Kết nối đang BẬT")
            self.toggle_btn.setText("Tắt kết nối")
```

---

## Phần 3: Tự tạo Signal tùy chỉnh

### 3.1. Signal với dữ liệu đơn giản

```python
from PySide6.QtCore import Signal, QObject


# Tạo class có Signal
class Messenger(QObject):
    # Định nghĩa Signal với kiểu dữ liệu
    message_sent = Signal(str)  # Gửi kèm chuỗi
    progress_updated = Signal(int)  # Gửi kèm số nguyên
    finished = Signal()  # Không gửi dữ liệu


class CustomSignalExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Signal")
        layout = QVBoxLayout()

        self.messenger = Messenger()
        self.button = QPushButton("Gửi tin nhắn")
        self.progress_bar = QProgressBar()
        self.label = QLabel("Chờ tin nhắn...")

        layout.addWidget(self.button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Kết nối Signal từ Messenger
        self.messenger.message_sent.connect(self.on_message_received)
        self.messenger.progress_updated.connect(self.progress_bar.setValue)
        self.messenger.finished.connect(lambda: self.label.setText("Hoàn thành!"))

        self.button.clicked.connect(self.start_work)

    def start_work(self):
        self.label.setText("Đang xử lý...")
        # Phát Signal từ Messenger (emit)
        self.messenger.message_sent.emit("Bắt đầu công việc!")

        for i in range(101):
            self.messenger.progress_updated.emit(i)
            # Giả lập công việc
            QApplication.processEvents()  # Xử lý sự kiện ngay

        self.messenger.message_sent.emit("Hoàn thành công việc!")
        self.messenger.finished.emit()

    def on_message_received(self, message):
        self.label.setText(message)
```

### 3.2. Signal với dữ liệu phức tạp

```python
from PySide6.QtCore import Signal, QObject
from dataclasses import dataclass


# Tạo class dữ liệu
@dataclass
class UserData:
    name: str
    age: int
    email: str


class DataProcessor(QObject):
    # Signal với dữ liệu phức tạp
    user_processed = Signal(UserData)
    error_occurred = Signal(str, int)  # error_message, error_code


class ComplexDataExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal với dữ liệu phức tạp")
        layout = QVBoxLayout()

        self.processor = DataProcessor()

        # UI
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên")
        self.age_input = QSpinBox()
        self.age_input.setRange(1, 150)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.process_btn = QPushButton("Xử lý dữ liệu")
        self.result_label = QLabel("Kết quả sẽ hiện ở đây")

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Tên:", self.name_input)
        form_layout.addRow("Tuổi:", self.age_input)
        form_layout.addRow("Email:", self.email_input)

        layout.addLayout(form_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        # Kết nối Signal
        self.processor.user_processed.connect(self.on_user_processed)
        self.processor.error_occurred.connect(self.on_error)
        self.process_btn.clicked.connect(self.process_data)

    def process_data(self):
        # Kiểm tra dữ liệu
        if not self.name_input.text():
            self.processor.error_occurred.emit("Tên không được để trống", 1001)
            return

        try:
            # Tạo đối tượng UserData
            user = UserData(
                name=self.name_input.text(),
                age=self.age_input.value(),
                email=self.email_input.text(),
            )
            # Phát Signal với dữ liệu
            self.processor.user_processed.emit(user)
        except Exception as e:
            self.processor.error_occurred.emit(str(e), 9999)

    def on_user_processed(self, user: UserData):
        self.result_label.setText(
            f"Đã xử lý: {user.name}, {user.age} tuổi, Email: {user.email}"
        )
        self.result_label.setStyleSheet("color: green;")

    def on_error(self, message, code):
        self.result_label.setText(f"Lỗi {code}: {message}")
        self.result_label.setStyleSheet("color: red;")
```

---

## Phần 4: Lambda và Partial - Truyền tham số linh hoạt

### 4.1. Sử dụng Lambda (Hàm vô danh)

```python
class LambdaExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Tạo 5 nút với lambda
        for i in range(1, 6):
            btn = QPushButton(f"Nút {i}")
            # ⚠️ QUAN TRỌNG: Dùng default argument để capture giá trị
            btn.clicked.connect(lambda checked, x=i: self.on_button_click(x))
            layout.addWidget(btn)
        
        self.setLayout(layout)
    
    def on_button_click(self, number):
        print(f"Nút {number} được click!")
        QMessageBox.information(self, "Thông báo", f"Bạn đã click nút {number}")
```

**⚠️ LƯU Ý VỀ LAMBDA:**
```python
# ❌ SAI - Tất cả sẽ in ra 5
for i in range(5):
    btn.clicked.connect(lambda: print(i))  # i là biến tham chiếu

# ✅ ĐÚNG - In đúng 0,1,2,3,4
for i in range(5):
    btn.clicked.connect(lambda checked, x=i: print(x))  # x là giá trị copy
```

### 4.2. Sử dụng Partial (từ functools)

```python
from functools import partial


class PartialExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Tạo các nút với partial
        names = ["Alice", "Bob", "Charlie", "David"]
        for name in names:
            btn = QPushButton(f"Xin chào {name}")
            btn.clicked.connect(partial(self.greet, name))
            layout.addWidget(btn)

        self.setLayout(layout)

    def greet(self, name, checked=False):  # checked là tham số của clicked
        print(f"Xin chào {name}!")
        QMessageBox.information(self, "Chào", f"Xin chào {name}!")
```

### 4.3. Truyền dữ liệu từ QLineEdit

```python
class DataPassingExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Nhập gì đó...")
        self.button = QPushButton("Lưu dữ liệu")
        self.label = QLabel("")
        
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Cách 1: Lấy dữ liệu trực tiếp trong Slot
        self.button.clicked.connect(self.save_data)
        
        # Cách 2: Dùng lambda để lấy dữ liệu
        # self.button.clicked.connect(lambda: self.save_data_with_text(self.input.text()))
    
    def save_data(self):
        text = self.input.text()
        self.label.setText(f"Đã lưu: {text}")
    
    def save_data_with_text(self, text):
        self.label.setText(f"Đã lưu: {text}")
```

---

## Phần 5: Xử lý sự kiện từ bàn phím và chuột

### 5.1. Sự kiện bàn phím

```python
from PySide6.QtCore import Qt, QEvent


class KeyboardEventsExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sự kiện bàn phím")
        layout = QVBoxLayout()

        self.label = QLabel("Nhấn phím bất kỳ...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; padding: 50px;")

        layout.addWidget(self.label)
        self.setLayout(layout)

        # Bật khả năng nhận sự kiện bàn phím
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Xử lý khi nhấn phím"""
        key = event.key()
        text = event.text()
        modifiers = event.modifiers()

        # Kiểm tra các phím đặc biệt
        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            self.label.setText("Bạn đã nhấn Enter!")
        elif key == Qt.Key_Space:
            self.label.setText("Bạn đã nhấn Space!")
        elif key == Qt.Key_A and modifiers == Qt.ControlModifier:
            self.label.setText("Ctrl + A được nhấn!")
        elif text:
            self.label.setText(f"Bạn đã nhấn: {text}")
        else:
            self.label.setText(f"Phím đặc biệt: {key}")

        # Gọi phương thức cha để xử lý mặc định
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Xử lý khi thả phím"""
        print(f"Đã thả phím: {event.text()}")
        super().keyReleaseEvent(event)
```

### 5.2. Sự kiện chuột

```python
class MouseEventsExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sự kiện chuột")
        self.setMinimumSize(400, 300)

        self.label = QLabel("Tương tác với chuột ở đây")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #999;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Bật tracking chuột (để biết vị trí khi không click)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Xử lý khi nhấn chuột"""
        pos = event.position()
        button = event.button()

        button_name = {
            Qt.LeftButton: "Trái",
            Qt.RightButton: "Phải",
            Qt.MiddleButton: "Giữa",
        }.get(button, "Khác")

        self.label.setText(
            f"Nhấn chuột {button_name} tại ({int(pos.x())}, {int(pos.y())})"
        )
        self.label.setStyleSheet(
            "background-color: #ffffcc; border: 2px solid #ff9900;"
        )

    def mouseReleaseEvent(self, event):
        """Xử lý khi thả chuột"""
        self.label.setText("Đã thả chuột")
        self.label.setStyleSheet(
            "background-color: #ccffcc; border: 2px solid #00cc00;"
        )

    def mouseDoubleClickEvent(self, event):
        """Xử lý khi double click"""
        self.label.setText("Double click!")
        self.label.setStyleSheet(
            "background-color: #ffcccc; border: 2px solid #ff0000;"
        )

    def mouseMoveEvent(self, event):
        """Xử lý khi di chuyển chuột (cần setMouseTracking(True))"""
        pos = event.position()
        self.label.setText(f"Di chuyển tại ({int(pos.x())}, {int(pos.y())})")
```

---

## Phần 6: Ứng dụng thực tế - Trình quản lý công việc đơn giản

Kết hợp tất cả kiến thức:

```python
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class TaskManager(QWidget):
    # Signal tùy chỉnh để thông báo khi task được thêm
    task_added = Signal(str)
    task_completed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý công việc")
        self.setFixedSize(500, 400)

        self.tasks = []  # Lưu danh sách công việc

        # === Tạo Layout ===
        main_layout = QVBoxLayout()

        # 1. Input area
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nhập công việc mới...")
        self.task_input.returnPressed.connect(self.add_task)
        self.add_btn = QPushButton("➕ Thêm")
        self.add_btn.clicked.connect(self.add_task)

        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)

        # 2. Task list
        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QListWidget.ExtendedSelection)

        # 3. Action buttons
        button_layout = QHBoxLayout()
        self.complete_btn = QPushButton("✓ Hoàn thành")
        self.complete_btn.clicked.connect(self.complete_task)
        self.delete_btn = QPushButton("✗ Xóa")
        self.delete_btn.clicked.connect(self.delete_task)
        self.clear_btn = QPushButton("🗑 Xóa tất cả")
        self.clear_btn.clicked.connect(self.clear_all)

        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)

        # 4. Status
        self.status_label = QLabel("Số công việc: 0")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                padding: 8px;
                border-radius: 4px;
            }
        """)

        # === Lồng layout ===
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.task_list)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # === Kết nối Signal ===
        # Signal tùy chỉnh
        self.task_added.connect(self.on_task_added)
        self.task_completed.connect(self.on_task_completed)

        # Double click để hoàn thành
        self.task_list.itemDoubleClicked.connect(self.complete_selected_task)

        # Shortcut: Delete key để xóa
        self.task_list.installEventFilter(self)  # Lọc sự kiện

    def add_task(self):
        """Thêm công việc mới"""
        text = self.task_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập công việc!")
            return

        # Thêm vào danh sách
        self.tasks.append(text)
        self.task_list.addItem(text)
        self.task_input.clear()
        self.update_status()

        # Phát signal
        self.task_added.emit(text)

        # Focus lại input
        self.task_input.setFocus()

    def complete_task(self):
        """Đánh dấu công việc đã hoàn thành"""
        selected = self.task_list.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn công việc!")
            return

        self.complete_selected_task(self.task_list.currentItem())

    def complete_selected_task(self, item):
        """Hoàn thành công việc được chọn"""
        if not item:
            return

        text = item.text()
        # Đánh dấu bằng cách thay đổi màu và thêm ✓
        if not text.startswith("✓ "):
            item.setText(f"✓ {text}")
            item.setForeground(Qt.green)
            self.task_completed.emit(text)
            self.update_status()

    def delete_task(self):
        """Xóa công việc được chọn"""
        selected = self.task_list.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn công việc!")
            return

        # Hỏi xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa công việc này?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.task_list.takeItem(selected)
            del self.tasks[selected]
            self.update_status()

    def clear_all(self):
        """Xóa tất cả công việc"""
        if not self.tasks:
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa tất cả",
            "Bạn có chắc muốn xóa tất cả công việc?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.task_list.clear()
            self.tasks.clear()
            self.update_status()

    def update_status(self):
        """Cập nhật trạng thái"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.startswith("✓ "))
        self.status_label.setText(f"Tổng: {total} | Đã hoàn thành: {completed}")

    # === Slots cho Signal tùy chỉnh ===
    def on_task_added(self, task):
        print(f"[LOG] Đã thêm công việc: {task}")

    def on_task_completed(self, task):
        print(f"[LOG] Đã hoàn thành: {task}")
        # Có thể thêm hiệu ứng thông báo ở đây

    # === Xử lý sự kiện ===
    def eventFilter(self, obj, event):
        """Lọc sự kiện để bắt phím Delete"""
        from PySide6.QtCore import QEvent

        if obj == self.task_list and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.delete_task()
                return True
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())
```

---

## Phần 7: Bài tập thực hành

### Bài 1: Ứng dụng chuyển đổi nhiệt độ
Tạo ứng dụng với:
- QLineEdit để nhập nhiệt độ (Celsius)
- QSlider để điều chỉnh nhiệt độ (0-100)
- QLabel hiển thị nhiệt độ tương ứng ở Fahrenheit
- Khi QLineEdit thay đổi → cập nhật Slider và Fahrenheit
- Khi Slider thay đổi → cập nhật LineEdit và Fahrenheit

**Gợi ý:** Sử dụng `textChanged` và `valueChanged`

### Bài 2: Đồng hồ bấm giờ
Tạo ứng dụng với:
- QLabel hiển thị thời gian (00:00:00)
- Nút "Bắt đầu", "Dừng", "Đặt lại"
- Sử dụng QTimer (sẽ học) hoặc custom Signal để update mỗi giây
- Lưu các vòng (lap) vào QListWidget

### Bài 3: Trò chơi đoán số
Tạo ứng dụng với:
- Hệ thống random số từ 1-100
- QLineEdit để nhập số đoán
- QLabel hiển thị gợi ý "Lớn hơn" / "Nhỏ hơn" / "Đúng rồi!"
- Đếm số lần đoán
- Nút "Chơi lại" để reset game
- Sử dụng Signal tùy chỉnh để thông báo khi đoán đúng

---

## Phần 8: Mẹo và thủ thuật

### 1. Sử dụng sender() để biết ai phát Signal

```python
def on_button_click(self):
    button = self.sender()  # QPushButton đã phát signal
    if button:
        print(f"Nút được click: {button.text()}")
```

### 2. Block Signal tạm thời

```python
# Ngăn không cho signal được phát
self.line_edit.blockSignals(True)
self.line_edit.setText("New text")
self.line_edit.blockSignals(False)  # Bật lại
```

### 3. Kiểm tra kết nối đã tồn tại

```python
# Kiểm tra xem signal đã kết nối chưa
if self.button.clicked.isConnected():
    self.button.clicked.disconnect()
```

### 4. Xóa tất cả kết nối

```python
# Xóa tất cả slot đã kết nối với signal
self.button.clicked.disconnect()
```

---

## Tóm tắt bài học

1. **Signals & Slots** là cơ chế giao tiếp chính trong PySide6
2. **Một Signal** có thể kết nối với **nhiều Slots**
3. **Nhiều Signals** có thể kết nối với **một Slot**
4. **Custom Signal** được tạo bằng `Signal(kiểu_dữ_liệu)`
5. **Lambda** và **Partial** giúp truyền tham số linh hoạt
6. **Event** (keyPress, mousePress) cho phép xử lý tương tác trực tiếp

---

## Kiến thức cho bài sau

Ở **Bài 4: QMainWindow và các thành phần nâng cao**, chúng ta sẽ:
- Sử dụng QMainWindow với MenuBar, ToolBar, StatusBar
- Tạo các Action và Shortcut
- Làm việc với Dock Widgets và Central Widget

Bạn đã sẵn sàng để xây dựng ứng dụng chuyên nghiệp hơn chưa? 😊