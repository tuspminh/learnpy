Chào mừng bạn đến **Bài 2: Layouts - Nghệ thuật sắp xếp giao diện**!

Trong bài 1, chúng ta đã dùng `move()` để đặt vị trí widget - cách này rất **tệ** vì khi bạn thay đổi kích thước cửa sổ, mọi thứ sẽ vỡ trận. Hôm nay, chúng ta sẽ học cách "thông minh" hơn với **Layouts** - công cụ tự động sắp xếp và co giãn các widget.

---

## Mục tiêu bài học

Sau bài này, bạn sẽ:
1. Hiểu tại sao Layout là "bắt buộc" trong ứng dụng chuyên nghiệp
2. Sử dụng thành thạo 3 Layout cơ bản: VBox, HBox, Grid
3. Biết cách lồng ghép Layout để tạo giao diện phức tạp
4. Quản lý được tỉ lệ co giãn (stretch) và khoảng cách (spacing)

---

## Phần 1: Tại sao cần Layout?

### Cách SAI - Dùng `move()` và `resize()` thủ công

```python
# ❌ CÁCH NÀY SAI - ĐỪNG LÀM
label = QLabel("Tên:", self)
label.move(50, 50)

input_box = QLineEdit(self)
input_box.move(100, 50)
input_box.resize(200, 30)

button = QPushButton("Lưu", self)
button.move(150, 100)
```

**Vấn đề:**
- Khi cửa sổ bị kéo to ra, các widget vẫn đứng yên chỗ cũ → xấu
- Khi cửa sổ bị thu nhỏ, widget có thể bị che khuất
- Phải tính toán tọa độ bằng tay cho từng widget → mất thời gian
- Không tương thích với các màn hình có độ phân giải khác nhau

### Cách ĐÚNG - Dùng Layout

```python
# ✅ CÁCH NÀY ĐÚNG
layout = QVBoxLayout()
layout.addWidget(label)
layout.addWidget(input_box)
layout.addWidget(button)
self.setLayout(layout)
```

**Lợi ích:**
- Widget tự động co giãn theo cửa sổ
- Không cần tính toán tọa độ
- Thay đổi thứ tự dễ dàng
- Tương thích mọi màn hình

---

## Phần 2: 3 Layout Cơ Bản

### 1. QVBoxLayout (Xếp dọc)

Xếp các widget theo **hàng dọc**, từ trên xuống dưới.

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class VBoxExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QVBoxLayout - Xếp dọc")
        self.resize(300, 250)

        # Tạo layout dọc
        layout = QVBoxLayout()

        # Tạo các widget
        label = QLabel("Đây là label ở trên cùng")
        btn1 = QPushButton("Nút 1")
        btn2 = QPushButton("Nút 2")
        btn3 = QPushButton("Nút 3")

        # Thêm widget vào layout
        layout.addWidget(label)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)

        # Gán layout cho cửa sổ
        self.setLayout(layout)


app = QApplication(sys.argv)
window = VBoxExample()
window.show()
sys.exit(app.exec())
```

### 2. QHBoxLayout (Xếp ngang)

Xếp các widget theo **hàng ngang**, từ trái sang phải.

```python
class HBoxExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QHBoxLayout - Xếp ngang")
        self.resize(400, 100)
        
        # Tạo layout ngang
        layout = QHBoxLayout()
        
        # Tạo các nút
        btn1 = QPushButton("Trái")
        btn2 = QPushButton("Giữa")
        btn3 = QPushButton("Phải")
        
        # Thêm vào layout
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        
        self.setLayout(layout)
```

### 3. QGridLayout (Xếp lưới)

Xếp các widget theo **dạng bảng**, có hàng và cột.

```python
from PySide6.QtWidgets import QGridLayout


class GridExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridLayout - Xếp lưới")

        layout = QGridLayout()

        # Tạo các widget
        label1 = QLabel("Tên:")
        input1 = QLineEdit()
        label2 = QLabel("Email:")
        input2 = QLineEdit()
        label3 = QLabel("SĐT:")
        input3 = QLineEdit()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")

        # Thêm vào lưới: addWidget(widget, hàng, cột, rowSpan, colSpan)
        layout.addWidget(label1, 0, 0)  # hàng 0, cột 0
        layout.addWidget(input1, 0, 1)  # hàng 0, cột 1
        layout.addWidget(label2, 1, 0)  # hàng 1, cột 0
        layout.addWidget(input2, 1, 1)  # hàng 1, cột 1
        layout.addWidget(label3, 2, 0)  # hàng 2, cột 0
        layout.addWidget(input3, 2, 1)  # hàng 2, cột 1

        # Span: chiếm nhiều cột
        layout.addWidget(save_btn, 3, 0, 1, 1)  # hàng 3, cột 0, chiếm 1 cột
        layout.addWidget(cancel_btn, 3, 1, 1, 1)  # hàng 3, cột 1, chiếm 1 cột

        self.setLayout(layout)
```

---

## Phần 3: Kỹ thuật Layout lồng nhau (Nested Layouts)

**Đây là kỹ thuật quan trọng nhất!** Không một ứng dụng nào chỉ dùng 1 layout đơn lẻ. Hãy nhìn giao diện dưới đây:

```
┌─────────────────────────────────────────────┐
│  [Header - Tiêu đề]                        │  ← QVBoxLayout (chính)
│  ┌─────────────────────────────────────────┐ │
│  │  [Nút 1] [Nút 2] [Nút 3]              │ │  ← QHBoxLayout (con)
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │  Tên: [___________]                    │ │  ← QGridLayout (con)
│  │  Email: [___________]                  │ │
│  │  [Lưu] [Hủy]                          │ │
│  └─────────────────────────────────────────┘ │
│  [Footer - Trạng thái]                     │
└─────────────────────────────────────────────┘
```

### Ví dụ thực tế: Tạo giao diện đăng nhập

```python
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QCheckBox,
)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập - Layout lồng nhau")
        self.setFixedSize(400, 350)  # Fixed size để dễ demo
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton#cancel_btn {
                background-color: #e0e0e0;
                color: #333;
            }
            QPushButton#cancel_btn:hover {
                background-color: #d0d0d0;
            }
        """)

        # === LAYOUT CHÍNH: Dọc ===
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # Khoảng cách giữa các thành phần
        main_layout.setContentsMargins(30, 30, 30, 30)  # Padding xung quanh

        # === 1. HEADER (Label) ===
        header_label = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        header_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078d7;
            margin-bottom: 10px;
        """)
        header_label.setAlignment(2)  # Qt.AlignCenter

        # === 2. FORM ĐĂNG NHẬP (GridLayout) ===
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setVerticalSpacing(20)

        # Tạo các widget
        username_label = QLabel("Tên đăng nhập:")
        username_input = QLineEdit()
        username_input.setPlaceholderText("Nhập tên đăng nhập...")

        password_label = QLabel("Mật khẩu:")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Nhập mật khẩu...")
        password_input.setEchoMode(QLineEdit.Password)  # Ẩn ký tự

        # Checkbox "Ghi nhớ"
        remember_check = QCheckBox("Ghi nhớ đăng nhập")

        # Thêm vào GridLayout
        # addWidget(widget, row, col, rowSpan, colSpan)
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(username_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(password_input, 1, 1)
        form_layout.addWidget(remember_check, 2, 1)  # Đưa checkbox sang cột bên phải

        # === 3. BUTTONS (HBoxLayout) ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        login_btn = QPushButton("Đăng nhập")
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancel_btn")  # Để stylesheet phân biệt

        # Thêm các nút vào hàng ngang, có khoảng cách đẩy sang phải
        button_layout.addStretch()  # Đẩy các nút sang phải
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)

        # === 4. LỒNG LAYOUT VÀO NHAU ===
        # Thêm header
        main_layout.addWidget(header_label)

        # Thêm form
        main_layout.addLayout(form_layout)

        # Thêm các nút
        main_layout.addLayout(button_layout)

        # === 5. GÁN LAYOUT CHÍNH CHO CỬA SỔ ===
        self.setLayout(main_layout)

        # === 6. KẾT NỐI SIGNAL - SLOT ===
        login_btn.clicked.connect(self.on_login)
        cancel_btn.clicked.connect(self.close)

        # Lưu tham chiếu để xài ở các hàm khác
        self.username_input = username_input
        self.password_input = password_input
        self.remember_check = remember_check

    def on_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        remember = self.remember_check.isChecked()

        if username and password:
            print(f"Đăng nhập với: {username}")
            print(f"Ghi nhớ: {remember}")
            # Ở đây bạn có thể kiểm tra database...
        else:
            print("Vui lòng nhập đầy đủ thông tin!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
```

---

## Phần 4: Stretch - Kiểm soát tỉ lệ co giãn

`addStretch()` tạo ra một "lò xo" (spring) đẩy các widget ra xa nhau.

```python
class StretchExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stretch - Điều khiển co giãn")
        self.resize(500, 200)
        
        layout = QHBoxLayout()
        
        # TH1: Không có stretch - các nút dính sát vào nhau
        btn1 = QPushButton("Nút 1")
        btn2 = QPushButton("Nút 2")
        btn3 = QPushButton("Nút 3")
        
        # TH2: Có stretch
        layout.addWidget(btn1)
        layout.addStretch(1)  # Lò xo với trọng số 1
        layout.addWidget(btn2)
        layout.addStretch(2)  # Lò xo với trọng số 2 (to gấp đôi)
        layout.addWidget(btn3)
        
        # Kết quả: btn1 ở trái, btn3 ở phải, btn2 ở giữa
        # Khoảng cách btn1-btn2 = 1/3, btn2-btn3 = 2/3
        
        self.setLayout(layout)
```

**Công thức:** Trọng số càng lớn, khoảng trống càng nhiều.

---

## Phần 5: Spacing và Margins - Làm đẹp giao diện

```python
class SpacingExample(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Khoảng cách giữa các widget (pixel)
        layout.setSpacing(25)
        
        # Khoảng cách từ mép layout đến các widget (trái, trên, phải, dưới)
        layout.setContentsMargins(20, 30, 20, 30)
        
        # Hoặc set cùng lúc
        # layout.setContentsMargins(20, 30, 20, 30)
        
        for i in range(1, 5):
            btn = QPushButton(f"Nút {i}")
            layout.addWidget(btn)
        
        self.setLayout(layout)
```

---

## Phần 6: Bài tập thực hành

### Bài 1: Giao diện máy tính đơn giản

Tạo giao diện máy tính với:
- Màn hình hiển thị (QLabel) ở trên
- Các nút số từ 0-9, phép tính (+, -, *, /), nút "=" và "C"
- Sử dụng QGridLayout cho các nút
- Tham khảo layout:

```
┌─────────────────────┐
│  [Màn hình: 0]      │  ← QLabel (đẩy xuống dưới cùng với stretch)
├─────────────────────┤
│  [7] [8] [9] [/]    │
│  [4] [5] [6] [*]    │  ← QGridLayout 4 cột
│  [1] [2] [3] [-]    │
│  [0] [.] [=] [+]    │
│  [C]                │  ← QHBoxLayout cho nút C (chiếm full width)
└─────────────────────┘
```

### Bài 2: Form nhập thông tin cá nhân

Tạo form với:
- Tiêu đề "THÔNG TIN CÁ NHÂN" (căn giữa)
- GridLayout với các trường:
  - Họ và tên (QLineEdit)
  - Ngày sinh (QLineEdit + QPushButton "Chọn" - đặt cùng hàng)
  - Giới tính (QComboBox: Nam/Nữ/Khác)
  - Sở thích (QCheckBox: Đọc sách, Nghe nhạc, Thể thao)
  - Ghi chú (QTextEdit)
- Hai nút "Lưu" và "Hủy" (đặt ở dưới cùng, căn phải)
- Sử dụng ít nhất 2 loại Layout khác nhau

### Bài 3: Thực đơn đặt hàng (Nâng cao)

Tạo giao diện đặt đồ ăn với:
- Danh sách món (QVBoxLayout với các QCheckBox)
- Số lượng (QSpinBox) và nút "Thêm vào giỏ"
- Giỏ hàng hiện tại (QLabel hiển thị danh sách)
- Tổng tiền (QLabel)
- Nút "Thanh toán" và "Xóa giỏ"

---

## Phần 7: Mẹo và thủ thuật

### 1. Widget co giãn theo tỉ lệ

```python
# Đặt tỉ lệ co giãn cho widget trong layout
layout.addWidget(widget1, stretch=1)  # Widget1 chiếm 1 phần
layout.addWidget(widget2, stretch=2)  # Widget2 chiếm 2 phần (to gấp đôi)
layout.addWidget(widget3, stretch=1)  # Widget3 chiếm 1 phần
```

### 2. Thêm khoảng cách (Spacer) linh hoạt

```python
# Cách 1: Dùng addStretch()
layout.addStretch()  # Đẩy các widget về phía bên kia

# Cách 2: Dùng QSpacerItem (kiểm soát chính xác hơn)
from PySide6.QtWidgets import QSpacerItem, QSizePolicy

spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
layout.addItem(spacer)
```

### 3. Ẩn/hiện widget mà không phá vỡ layout

```python
widget.setVisible(False)  # Ẩn
widget.setVisible(True)  # Hiện
# Layout sẽ tự động cập nhật vị trí các widget khác
```

### 4. Thêm widget vào vị trí cụ thể

```python
# Chèn widget vào vị trí index
layout.insertWidget(0, new_widget)  # Chèn lên đầu
layout.insertWidget(2, new_widget)  # Chèn vào vị trí thứ 2
```

---

## Kiến thức cho bài sau

Ở **Bài 3: Signals & Slots nâng cao**, chúng ta sẽ:
- Tự tạo Signal với dữ liệu tùy chỉnh
- Kết nối nhiều Slot với cùng một Signal
- Sử dụng lambda để truyền tham số
- Xử lý sự kiện từ bàn phím và chuột

---

## Tóm tắt bài học

1. **Layout là bắt buộc** - Không dùng `move()` trong ứng dụng thực tế
2. **3 Layout cơ bản**:
   - `QVBoxLayout`: Xếp dọc
   - `QHBoxLayout`: Xếp ngang
   - `QGridLayout`: Xếp lưới
3. **Layout lồng nhau** - Kỹ thuật quan trọng nhất để tạo giao diện phức tạp
4. **Stretch** kiểm soát tỉ lệ co giãn
5. **Spacing** và **Margins** làm đẹp giao diện

**Nguyên tắc vàng:** Luôn bắt đầu từ Layout lớn nhất (outermost), sau đó lồng các Layout con vào bên trong.

---

## Lời khuyên

- **Thực hành nhiều:** Hãy thử tạo lại giao diện của các ứng dụng bạn thường dùng (Facebook login, Google search, Zalo...)
- **Sử dụng Qt Designer:** Đây là công cụ kéo thả để thiết kế UI trực quan (sẽ học sau), giúp bạn hiểu cấu trúc Layout nhanh hơn
- **Đọc code nguồn:** Xem các ví dụ trong thư viện PySide6 để học cách các chuyên gia làm

Bạn đã sẵn sàng cho Bài 3 về Signals & Slots chưa? 😊