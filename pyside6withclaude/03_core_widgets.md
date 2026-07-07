## Bài 3: Các Widget Cốt Lõi — QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox

### 1. Động lực (Motivation)

Ở Tkinter, bạn đã quen thuộc với `Entry`, `Button`, `Label`, `Checkbutton`. PySide6 cung cấp các widget tương đương nhưng **giàu tính năng hơn hẳn**: validation dữ liệu tích hợp sẵn, placeholder text, icon trên nút bấm, và đặc biệt — cơ chế **Signal & Slot** thay cho `command=` của Tkinter, mạnh mẽ và an toàn kiểu dữ liệu hơn nhiều.

Trong các ứng dụng thực tế 2026 — công cụ nội bộ tại các công ty fintech như Cake, Timo, hay app quản lý vận đơn tại Tiki Logistics — những widget này chính là "xương sống" của mọi form nhập liệu: đăng nhập, tạo đơn hàng, cấu hình hệ thống.

### 2. Giải thích khái niệm

#### 2.1. `QLabel` — Hiển thị văn bản/hình ảnh

python

```python
from PySide6.QtWidgets import QLabel

label = QLabel("Xin chào")
label.setText("Cập nhật nội dung")       # Đổi text
print(label.text())                       # Đọc text hiện tại
label.setStyleSheet("color: blue; font-size: 16px;")
```

`QLabel` không chỉ hiển thị text, còn hiển thị được ảnh (`setPixmap()`) — điều Tkinter cần thêm thư viện phụ mới làm gọn được.

#### 2.2. `QLineEdit` — Ô nhập liệu 1 dòng (tương đương `Entry`)

python

```python
from PySide6.QtWidgets import QLineEdit

email_input = QLineEdit()
email_input.setPlaceholderText("Nhập email của bạn")   # Gợi ý mờ - Tkinter không có sẵn!
email_input.setMaxLength(100)                           # Giới hạn ký tự
email_input.setEchoMode(QLineEdit.Password)             # Ẩn ký tự (mật khẩu)

# Đọc / ghi giá trị
print(email_input.text())        # Đọc — tương đương entry.get()
email_input.setText("abc@xyz.com")  # Ghi — tương đương entry.insert()
email_input.clear()               # Xóa trắng — tương đương entry.delete(0, END)
```

**So sánh quan trọng với Tkinter:**

| Tkinter `Entry` | PySide6 `QLineEdit` |
| --- | --- |
| `entry.get()` | `line_edit.text()` |
| `entry.delete(0, END); entry.insert(0, "x")` | `line_edit.setText("x")` (tự động thay thế, không cần xóa trước!) |
| Không có placeholder sẵn | `setPlaceholderText()` có sẵn |
| `show="*"` | `setEchoMode(QLineEdit.Password)` |

> **Lưu ý đặc biệt cho bạn** (vì bạn đã quen pattern Tkinter): trong PySide6, `setText()` sẽ **tự động ghi đè toàn bộ nội dung cũ**, khác với Tkinter — nơi bạn *luôn phải* `.delete()` trước khi `.insert()`. Đây là điểm giúp code PySide6 gọn hơn.

#### 2.3. `QPushButton` — Nút bấm & Signal/Slot đầu tiên

Đây là lúc bạn gặp khái niệm quan trọng nhất của Qt: **Signal & Slot**.

python

```python
from PySide6.QtWidgets import QPushButton

button = QPushButton("Đăng nhập")

def handle_click():
    print("Nút đã được nhấn!")

button.clicked.connect(handle_click)   # Kết nối signal "clicked" với hàm xử lý (slot)
```

**Signal & Slot là gì?**

- **Signal** (`clicked`) là "tín hiệu" widget phát ra khi có sự kiện xảy ra.
- **Slot** là hàm được gọi khi tín hiệu đó phát ra.
- `.connect()` là cầu nối giữa 2 bên.

So với Tkinter:

python

```python
# Tkinter
button = Button(root, text="Đăng nhập", command=handle_click)

# PySide6
button = QPushButton("Đăng nhập")
button.clicked.connect(handle_click)
```

Về bản chất tương tự `command=`, nhưng Signal/Slot **mạnh hơn nhiều** vì:

1. Một signal có thể kết nối với **nhiều slot** cùng lúc.
2. Slot có thể nhận **tham số** mà signal truyền qua (ví dụ signal `textChanged` truyền chuỗi text mới).
3. Bạn có thể **tự định nghĩa signal riêng** (học ở bài nâng cao) — nền tảng cho kiến trúc lớn.

python

```python
# Một signal, nhiều slot
button.clicked.connect(handle_click)
button.clicked.connect(lambda: print("Log: đã click"))
```

#### 2.4. `QCheckBox` — Hộp chọn (tương đương `Checkbutton`)

python

```python
from PySide6.QtWidgets import QCheckBox

remember_me = QCheckBox("Ghi nhớ đăng nhập")
remember_me.setChecked(True)              # Đặt trạng thái mặc định

print(remember_me.isChecked())            # True/False — đơn giản hơn Tkinter nhiều!

remember_me.stateChanged.connect(
    lambda state: print("Đã tick" if state else "Đã bỏ tick")
)
```

**Điểm khác biệt lớn với Tkinter:** Tkinter bắt bạn phải tạo `IntVar()` hoặc `BooleanVar()` riêng để đọc trạng thái Checkbutton. PySide6 **không cần biến điều khiển riêng** — đọc trực tiếp bằng `.isChecked()`. Đây là một trong những điểm giúp code PySide6 sạch hơn đáng kể.

#### 2.5. `QComboBox` — Danh sách chọn (dropdown, tương đương `OptionMenu`)

python

```python
from PySide6.QtWidgets import QComboBox

city_selector = QComboBox()
city_selector.addItem("TP. Hồ Chí Minh")
city_selector.addItems(["Hà Nội", "Đà Nẵng", "Cần Thơ"])  # Thêm nhiều item cùng lúc

print(city_selector.currentText())      # Lấy text đang chọn
print(city_selector.currentIndex())     # Lấy vị trí (index) đang chọn

city_selector.currentTextChanged.connect(
    lambda text: print(f"Bạn đã chọn: {text}")
)
```

### 3. Ví dụ thực tế 2026: Form đăng nhập hoàn chỉnh cho App Ngân hàng số

Kết hợp toàn bộ widget vừa học, mô phỏng màn hình đăng nhập của một ứng dụng ngân hàng số nội bộ:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cake Digital Bank - Đăng nhập nội bộ")
        self.resize(380, 300)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("🏦 Đăng nhập hệ thống")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Chọn chi nhánh - dùng QComboBox
        branch_row = QHBoxLayout()
        branch_row.addWidget(QLabel("Chi nhánh:"))
        self.branch_selector = QComboBox()
        self.branch_selector.addItems(["Hội sở HCM", "Chi nhánh Hà Nội", "Chi nhánh Đà Nẵng"])
        branch_row.addWidget(self.branch_selector)
        main_layout.addLayout(branch_row)

        # Form nhập liệu
        form = QGridLayout()
        form.addWidget(QLabel("Tài khoản:"), 0, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập mã nhân viên")
        form.addWidget(self.username_input, 0, 1)

        form.addWidget(QLabel("Mật khẩu:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        form.addWidget(self.password_input, 1, 1)
        main_layout.addLayout(form)

        # Ghi nhớ đăng nhập
        self.remember_checkbox = QCheckBox("Ghi nhớ đăng nhập trên thiết bị này")
        main_layout.addWidget(self.remember_checkbox)

        # Nút hành động
        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Hủy")
        login_btn = QPushButton("Đăng nhập")
        button_row.addWidget(cancel_btn)
        button_row.addWidget(login_btn)
        main_layout.addLayout(button_row)

        # Trạng thái kết quả
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Kết nối Signal & Slot
        login_btn.clicked.connect(self._handle_login)
        cancel_btn.clicked.connect(self._handle_cancel)

    def _handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        branch = self.branch_selector.currentText()
        remember = self.remember_checkbox.isChecked()

        if not username or not password:
            self.status_label.setText("⚠️ Vui lòng nhập đầy đủ thông tin!")
            self.status_label.setStyleSheet("color: red;")
            return

        self.status_label.setText(
            f"✅ Đăng nhập '{username}' tại {branch} (Ghi nhớ: {remember})"
        )
        self.status_label.setStyleSheet("color: green;")

    def _handle_cancel(self):
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.setText("Đã hủy nhập liệu.")
        self.status_label.setStyleSheet("color: gray;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
```

**Điểm cần chú ý trong ví dụ:** Tất cả widget con được lưu thành `self.xxx` (thuộc tính của class) thay vì biến cục bộ trong `_setup_ui()`. Đây là **quy tắc bắt buộc** — vì nếu chỉ là biến cục bộ, bạn sẽ không truy cập được chúng từ các hàm khác như `_handle_login()`.

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Widget là biến cục bộ, không lưu vào `self`:**

python

```python
def _setup_ui(self):
    username_input = QLineEdit()   # ❌ Biến cục bộ, biến mất sau khi hàm kết thúc
    layout.addWidget(username_input)

def _handle_login(self):
    print(self.username_input.text())  # ❌ AttributeError: không tồn tại
```

→ Luôn dùng `self.username_input = QLineEdit()` nếu cần truy cập widget ở nơi khác.

**Lỗi 2 — Quên dấu ngoặc khi connect (gọi hàm ngay thay vì truyền reference):**

python

```python
button.clicked.connect(handle_click())   # ❌ Gọi hàm NGAY LẬP TỨC lúc setup, không phải khi click
button.clicked.connect(handle_click)     # ✅ Đúng - truyền reference của hàm
```

Đây là lỗi **cực kỳ phổ biến** với người mới, tương tự lỗi hay gặp khi dùng `command=` trong Tkinter.

**Lỗi 3 — Nhầm `currentText()` và `currentIndex()`:**

python

```python
selected = combo.currentIndex()  # Trả về số (0, 1, 2...) không phải chuỗi
if selected == "Hà Nội":  # ❌ So sánh int với str luôn False
```

**Lỗi 4 — Quên `QLineEdit.Password` phải viết đúng dạng enum:**

python

```python
input.setEchoMode("password")  # ❌ Sai — không phải string
input.setEchoMode(QLineEdit.Password)  # ✅ Đúng — dùng enum của class
```

**Lỗi 5 — Dùng `stateChanged` khi chỉ cần biết checked/unchecked đơn giản:** `stateChanged` trả về số nguyên (0, 1, 2 vì `QCheckBox` hỗ trợ tri-state). Nếu chỉ cần bool đơn giản, nên đọc trực tiếp `.isChecked()` trong slot thay vì dựa vào giá trị `state` truyền qua signal.

### 5. Bài tập thực hành

Nâng cấp **"LearnHub Desktop"** thành màn hình đăng ký khóa học:

**Yêu cầu:**

1. `QComboBox` chọn khóa học: "Python cơ bản", "PySide6", "PostgreSQL nâng cao".
2. `QLineEdit` nhập họ tên (có `placeholderText`) và email (validate đơn giản: phải chứa `@`).
3. `QCheckBox` "Tôi đồng ý điều khoản sử dụng" — nút "Đăng ký" phải **kiểm tra checkbox đã tick chưa** trước khi cho đăng ký thành công.
4. Hiển thị kết quả trong `QLabel` trạng thái (giống ví dụ trên): báo lỗi nếu thiếu thông tin hoặc chưa tick điều khoản, báo thành công kèm thông tin đã nhập nếu hợp lệ.
5. Có nút "Làm mới" để xóa toàn bộ input về trạng thái ban đầu (bao gồm reset combobox về item đầu bằng `setCurrentIndex(0)` và bỏ tick checkbox bằng `setChecked(False)`).

Gõ "bài 4" khi hoàn thành — Bài 4 sẽ học các **widget nâng cao**: `QTextEdit`, `QListWidget`, `QRadioButton`, `QSpinBox`, và cách nhóm `QRadioButton` bằng `QButtonGroup`.
