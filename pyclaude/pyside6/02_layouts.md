## Bài 2: Hệ thống Layout trong PySide6

### 1. Động lực (Motivation)

Ở Tkinter, bạn dùng `pack`, `grid`, `place` — ba hệ thống **độc lập, không tương thích lẫn nhau** trong cùng 1 container. Đây là điểm PySide6 làm **tốt hơn hẳn**: Qt chỉ có **một triết lý layout duy nhất** — mọi layout đều là object (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`, `QFormLayout`), và bạn có thể **lồng nhau tự do** (layout trong layout) mà không sợ xung đột như khi trộn `pack`/`grid`.

Trong thực tế 2026, các ứng dụng desktop chuyên nghiệp — như công cụ nội bộ giám sát pipeline ML, app quản lý kho (WMS) cho Tiki/Shopee logistics, hay phần mềm giao dịch tại các công ty chứng khoán — đều xây UI bằng cách **lồng layout** (nested layouts) để tạo ra giao diện responsive: co giãn đẹp khi resize cửa sổ, điều mà Tkinter làm khá vụng về.

### 2. Giải thích khái niệm

#### 2.1. Ba loại layout cơ bản

| Layout | Công dụng | Tương đương Tkinter |
| --- | --- | --- |
| `QVBoxLayout` | Xếp widget theo **chiều dọc** | gần giống `pack(side=TOP)` |
| `QHBoxLayout` | Xếp widget theo **chiều ngang** | gần giống `pack(side=LEFT)` |
| `QGridLayout` | Xếp theo **hàng/cột** (lưới) | tương đương `grid()` |

Khác biệt cốt lõi với Tkinter: bạn **không gắn layout vào widget con**, mà **gắn widget con vào layout**, rồi gắn layout vào container cha bằng `setLayout()`.

python

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bài 2 - QVBoxLayout")
        self.resize(300, 200)

        layout = QVBoxLayout()          # Bước 1: Tạo layout
        layout.addWidget(QLabel("Dòng 1"))   # Bước 2: Thêm widget vào layout theo thứ tự
        layout.addWidget(QLabel("Dòng 2"))
        layout.addWidget(QPushButton("Nhấn tôi"))
        self.setLayout(layout)          # Bước 3: Gắn layout vào window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

> **Lưu ý cú pháp tắt:** Nếu bạn truyền `self` khi tạo layout — `layout = QVBoxLayout(self)` — thì bước `setLayout()` tự động thực hiện luôn, không cần gọi riêng. Đây là cách viết phổ biến trong code chuyên nghiệp (bạn đã thấy ở Bài 1).

#### 2.2. `QHBoxLayout` — xếp ngang

python

```python
from PySide6.QtWidgets import QHBoxLayout

layout = QHBoxLayout(self)
layout.addWidget(QPushButton("Hủy"))
layout.addWidget(QPushButton("Đồng ý"))
```

#### 2.3. Lồng layout (Nested Layouts) — kỹ thuật cốt lõi

Đây là điều **không thể làm gọn gàng trong Tkinter** nhưng cực kỳ tự nhiên trong Qt:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit
)

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập - Cake Digital Bank (Demo)")
        self.resize(350, 180)

        # Layout tổng: dọc
        main_layout = QVBoxLayout(self)

        # Hàng nhập username (layout ngang lồng bên trong)
        row_user = QHBoxLayout()
        row_user.addWidget(QLabel("Tài khoản:"))
        row_user.addWidget(QLineEdit())

        # Hàng nhập password
        row_pass = QHBoxLayout()
        row_pass.addWidget(QLabel("Mật khẩu:"))
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)  # Ẩn ký tự khi gõ
        row_pass.addWidget(password_input)

        # Hàng nút bấm
        row_buttons = QHBoxLayout()
        row_buttons.addWidget(QPushButton("Hủy"))
        row_buttons.addWidget(QPushButton("Đăng nhập"))

        # Gộp tất cả vào layout tổng theo thứ tự
        main_layout.addLayout(row_user)
        main_layout.addLayout(row_pass)
        main_layout.addLayout(row_buttons)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginForm()
    window.show()
    sys.exit(app.exec())
```

**Điểm mấu chốt:** `addLayout()` dùng để lồng layout vào layout, khác với `addWidget()` dùng cho widget. Đây là pattern bạn sẽ dùng **liên tục** trong mọi ứng dụng thực tế.

#### 2.4. `QGridLayout` — layout dạng lưới

Rất giống `grid()` của Tkinter, nhưng cú pháp rõ ràng hơn:

python

```python
from PySide6.QtWidgets import QGridLayout

layout = QGridLayout(self)
layout.addWidget(QLabel("Mã SP:"), 0, 0)      # hàng 0, cột 0
layout.addWidget(QLineEdit(), 0, 1)            # hàng 0, cột 1
layout.addWidget(QLabel("Số lượng:"), 1, 0)    # hàng 1, cột 0
layout.addWidget(QLineEdit(), 1, 1)            # hàng 1, cột 1

# Widget chiếm nhiều cột (giống columnspan trong Tkinter)
layout.addWidget(QPushButton("Lưu đơn hàng"), 2, 0, 1, 2)  # row, col, rowspan, colspan
```

So với Tkinter `grid(row=2, column=0, columnspan=2)`, Qt dùng tham số vị trí: `addWidget(widget, row, col, rowspan, colspan)` — gọn hơn và không cần nhớ tên tham số.

#### 2.5. Điều khiển khoảng cách & lề

python

```python
layout.setSpacing(10)                    # Khoảng cách giữa các widget
layout.setContentsMargins(20, 20, 20, 20)  # Lề trái, trên, phải, dưới của layout
```

#### 2.6. Stretch — kỹ thuật co giãn thông minh

`addStretch()` chèn khoảng trống co giãn — cực kỳ hữu ích để đẩy widget về một phía, tương tự việc dùng `side=RIGHT` kết hợp `fill` trong Tkinter nhưng linh hoạt hơn:

python

```python
row_buttons = QHBoxLayout()
row_buttons.addStretch()                     # Đẩy các nút về bên phải
row_buttons.addWidget(QPushButton("Hủy"))
row_buttons.addWidget(QPushButton("Đồng ý"))
```

### 3. Ví dụ thực tế 2026: Form nhập liệu cho ứng dụng WMS (Warehouse Management)

Đây là mẫu UI thường thấy trong công cụ quản lý kho hàng nội bộ tại các sàn TMĐT như Tiki, Shopee — kết hợp cả 3 loại layout:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton
)

class WarehouseEntryForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WMS - Nhập kho hàng hóa")
        self.resize(400, 250)

        main_layout = QVBoxLayout(self)

        header = QLabel("📦 PHIẾU NHẬP KHO")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(header)

        # Form dùng grid vì có nhiều cặp label-input thẳng hàng
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Mã SKU:"), 0, 0)
        form_layout.addWidget(QLineEdit(), 0, 1)
        form_layout.addWidget(QLabel("Tên sản phẩm:"), 1, 0)
        form_layout.addWidget(QLineEdit(), 1, 1)
        form_layout.addWidget(QLabel("Số lượng:"), 2, 0)
        form_layout.addWidget(QLineEdit(), 2, 1)
        main_layout.addLayout(form_layout)

        # Hàng nút bấm: dùng HBox + stretch để đẩy nút về phải
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(QPushButton("Hủy"))
        button_row.addWidget(QPushButton("Xác nhận nhập kho"))
        main_layout.addLayout(button_row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarehouseEntryForm()
    window.show()
    sys.exit(app.exec())
```

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Quên `setLayout()` khi tạo layout không truyền `self`:**

python

```python
layout = QVBoxLayout()
layout.addWidget(QLabel("Xin chào"))
# ❌ Quên self.setLayout(layout) → cửa sổ trống trơn, không lỗi, chỉ không hiện gì
```

**Lỗi 2 — Gán 2 layout trực tiếp cho cùng 1 widget:**

python

```python
self.setLayout(layout1)
self.setLayout(layout2)  # ❌ Cảnh báo runtime: widget đã có layout rồi
```

→ Muốn nhiều layout, phải **lồng nhau** bằng `addLayout()`, không gọi `setLayout()` nhiều lần trên cùng widget.

**Lỗi 3 — Dùng `addWidget()` để thêm layout con (nhầm với `addLayout()`):**

python

```python
main_layout.addWidget(row_user)  # ❌ TypeError, row_user là QHBoxLayout không phải QWidget
```

**Lỗi 4 — Quên rằng thứ tự `addWidget()` quyết định thứ tự hiển thị:**  
Khác với `grid()` của Tkinter (chỉ định row/col rõ ràng), `QVBoxLayout`/`QHBoxLayout` xếp theo **đúng thứ tự gọi hàm**, không có tham số row/col.

**Lỗi 5 — Không set `setContentsMargins(0,0,0,0)` khi lồng layout muốn sát nhau**, dẫn đến giao diện bị nhiều khoảng trắng thừa ngoài ý muốn khi lồng nhiều tầng.

### 5. Bài tập thực hành

Nâng cấp **"LearnHub Desktop"** từ Bài 1 thành màn hình đăng nhập hoàn chỉnh:

**Yêu cầu:**

1. Layout tổng là `QVBoxLayout`.
2. Thêm 1 `QLabel` tiêu đề "LearnHub Desktop 2026" ở trên cùng, style chữ to, đậm.
3. Dùng `QGridLayout` cho phần form gồm 2 hàng: "Email" và "Mật khẩu" (mỗi hàng có `QLabel` + `QLineEdit`; ô mật khẩu dùng `setEchoMode(QLineEdit.Password)`).
4. Dùng `QHBoxLayout` với `addStretch()` để tạo hàng 2 nút "Hủy" và "Đăng nhập", đẩy về bên phải.
5. Thêm khoảng cách hợp lý bằng `setSpacing()` và `setContentsMargins()` cho layout tổng.
6. Chạy chương trình theo đúng chuẩn (`QApplication`, `show()`, `sys.exit(app.exec())`).

Gõ "bài 3" khi bạn hoàn thành — Bài 3 sẽ đi vào **các widget nhập liệu cốt lõi**: `QLineEdit`, `QPushButton`, `QLabel`, `QComboBox`, `QCheckBox` — chi tiết các thuộc tính và phương thức quan trọng nhất của từng widget.
