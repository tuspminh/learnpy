# 📘 MODULE 2 – BÀI 2.3: LAYOUT MANAGEMENT CHI TIẾT

> **Mục tiêu bài học**:
> - Hiểu **tại sao** phải dùng Layout (thay vì setGeometry thủ công)
> - Nắm vững 5 loại layout chính và khi nào dùng cái nào
> - Hiểu sâu **stretch, spacing, margins, size policy**
> - Biết lồng layout (nested layout) để tạo giao diện phức tạp
> - Build app **"Máy tính bỏ túi"** với `QGridLayout`

---

## 🎯 PHẦN 1: TẠI SAO CẦN LAYOUT?

### 1.1. Cách "cổ điển" – Đặt vị trí tuyệt đối (KHÔNG NÊN)

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton

app = QApplication(sys.argv)
w = QWidget()
w.resize(400, 300)

btn1 = QPushButton("Button 1", w)
btn1.setGeometry(10, 10, 100, 30)   # x, y, width, height

btn2 = QPushButton("Button 2", w)
btn2.setGeometry(10, 50, 100, 30)

w.show()
sys.exit(app.exec())
```

**Vấn đề của cách này**:

| Vấn đề | Giải thích |
|--------|-----------|
| ❌ Không tự động resize | Kéo cửa sổ to → widget vẫn nhỏ xíu |
| ❌ Không tự sắp xếp | Thêm/xóa widget → phải tính tay lại hết |
| ❌ Không thích ứng ngôn ngữ | Tiếng Anh "Save", tiếng Việt "Lưu lại" → độ dài khác nhau |
| ❌ Không thích ứng font | User dùng font lớn → chữ bị cắt |
| ❌ Không thích ứng DPI | Màn hình Retina/4K → vị trí lệch hết |

### 1.2. Cách đúng – Dùng Layout

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout
)

app = QApplication(sys.argv)
w = QWidget()

layout = QVBoxLayout(w)
layout.addWidget(QPushButton("Button 1"))
layout.addWidget(QPushButton("Button 2"))

w.resize(400, 300)
w.show()
sys.exit(app.exec())
```

**Ưu điểm**:
- ✅ Tự động resize khi cửa sổ đổi
- ✅ Tự động căn chỉnh, tính toán kích thước
- ✅ Thêm/xóa widget chỉ cần `addWidget` / `removeWidget`
- ✅ Cross-platform, cross-DPI
- ✅ Thích ứng với font, ngôn ngữ

> **Nguyên tắc vàng**: *Trong Qt, bạn KHÔNG BAO GIỜ set vị trí tuyệt đối cho widget. Layout lo hết.*

### 1.3. Cách Layout hoạt động

```
┌───────────────────────────────────────┐
│  Widget cha (400x300)                 │
│  ┌─────────────────────────────────┐  │
│  │ Layout (quản lý vùng bên trong) │  │
│  │  ┌──────────────────────────┐   │  │
│  │  │  Child 1                 │   │  │
│  │  ├──────────────────────────┤   │  │
│  │  │  Child 2                 │   │  │
│  │  ├──────────────────────────┤   │  │
│  │  │  Child 3                 │   │  │
│  │  └──────────────────────────┘   │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
```

Khi cửa sổ đổi kích thước, layout **tự động tính lại** vị trí + kích thước mọi child.

---

## 🎯 PHẦN 2: HAI CÁCH GẮN LAYOUT VÀO WIDGET

### Cách 1: Truyền parent vào constructor (khuyên dùng)

```python
layout = QVBoxLayout(w)              # Tự động set layout cho w
layout.addWidget(btn)
```

### Cách 2: Dùng setLayout

```python
layout = QVBoxLayout()
layout.addWidget(btn)
w.setLayout(layout)
```

### Cách 3: Trong class con của QWidget

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)   # Gắn vào self
        layout.addWidget(QPushButton("OK"))
```

⚠️ **Cảnh báo**: Một widget **chỉ có 1 layout top-level**. Nếu bạn `setLayout` hai lần → lần đầu bị thay thế (mất hết widget).

---

## 🎯 PHẦN 3: QVBoxLayout & QHBoxLAYOUT

### 3.1. QVBoxLayout – Xếp dọc

```python
from PySide6.QtWidgets import QVBoxLayout

layout = QVBoxLayout()
layout.addWidget(QPushButton("Top"))
layout.addWidget(QPushButton("Middle"))
layout.addWidget(QPushButton("Bottom"))
```

Kết quả:
```
┌────────────────┐
│  [  Top  ]     │
├────────────────┤
│  [ Middle ]    │
├────────────────┤
│  [ Bottom ]    │
└────────────────┘
```

### 3.2. QHBoxLayout – Xếp ngang

```python
from PySide6.QtWidgets import QHBoxLayout

layout = QHBoxLayout()
layout.addWidget(QPushButton("Left"))
layout.addWidget(QPushButton("Center"))
layout.addWidget(QPushButton("Right"))
```

Kết quả:
```
┌────────┬──────────┬─────────┐
│ [Left] │ [Center] │ [Right] │
└────────┴──────────┴─────────┘
```

### 3.3. addStretch() – Đẩy widget về phía

```python
layout = QHBoxLayout()
layout.addWidget(QPushButton("OK"))
layout.addWidget(QPushButton("Cancel"))
layout.addStretch()                          # Đẩy 2 nút về bên trái
```

Kết quả:
```
┌─────────┬───────────┬───────────────────┐
│  [OK]   │ [Cancel]  │  (khoảng trống)   │
└─────────┴───────────┴───────────────────┘
```

```python
layout.addStretch()                          # Bên trái
layout.addWidget(btn1)
layout.addWidget(btn2)                       # Đẩy 2 nút sang phải
```

### 3.4. addSpacing() vs addStretch()

```python
layout.addWidget(btn1)
layout.addSpacing(50)                        # Khoảng cố định 50px
layout.addWidget(btn2)
```

| Method | Đặc điểm |
|--------|----------|
| `addSpacing(px)` | Khoảng **cố định** px |
| `addStretch(factor)` | Khoảng **co giãn**, chiếm không gian dư |

### 3.5. Tham số stretch trong addWidget

```python
layout.addWidget(btn_left, stretch=1)        # Chiếm 1 phần
layout.addWidget(btn_right, stretch=2)       # Chiếm 2 phần
# Tỉ lệ 1:2 → btn_right rộng gấp đôi
```

### 3.6. Nested Layout – Lồng nhau

Đây là **chìa khóa tạo layout phức tạp**:

```python
# Layout ngoài: dọc
outer = QVBoxLayout(w)

# Hàng trên: 3 nút ngang
top_row = QHBoxLayout()
top_row.addWidget(QPushButton("A"))
top_row.addWidget(QPushButton("B"))
top_row.addWidget(QPushButton("C"))

# Hàng dưới: 2 nút ngang
bottom_row = QHBoxLayout()
bottom_row.addWidget(QPushButton("D"))
bottom_row.addWidget(QPushButton("E"))

# Lồng vào
outer.addLayout(top_row)
outer.addLayout(bottom_row)
```

Kết quả:
```
┌─────┬─────┬─────┐
│ [A] │ [B] │ [C] │
├─────┴─────┴─────┤
│ [D]     │ [E]   │
└─────────┴───────┘
```

💡 **Mẹo**: Bất kỳ layout phức tạp nào cũng có thể chia nhỏ thành V/H lồng nhau.

---

## 🎯 PHẦN 4: QGRIDLAYOUT – LƯỚI 2 CHIỀU

### 4.1. Cơ bản

```python
from PySide6.QtWidgets import QGridLayout

grid = QGridLayout()
grid.addWidget(widget, row, col)                     # Vị trí (row, col)
grid.addWidget(widget, row, col, rowSpan, colSpan)   # Chiếm nhiều ô
```

Ví dụ:
```python
grid.addWidget(QLabel("Tên:"), 0, 0)
grid.addWidget(QLineEdit(),   0, 1)
grid.addWidget(QLabel("Email:"), 1, 0)
grid.addWidget(QLineEdit(),   1, 1)
```

Kết quả:
```
┌───────┬─────────────────┐
│ Tên:  │ [_____________] │
├───────┼─────────────────┤
│ Email:│ [_____________] │
└───────┴─────────────────┘
```

### 4.2. Spanning – Ô chiếm nhiều ô

```python
grid.addWidget(QLabel("Header"), 0, 0, 1, 3)   # Chiếm 1 hàng, 3 cột
grid.addWidget(btn, 1, 0)                      # Hàng 1, cột 0
grid.addWidget(btn, 1, 1)                      # Hàng 1, cột 1
grid.addWidget(btn, 1, 2)                      # Hàng 1, cột 2
grid.addWidget(btn_wide, 2, 0, 1, 3)           # Chiếm cả 3 cột
```

### 4.3. Stretch cho hàng/cột

```python
grid.setColumnStretch(0, 1)                     # Cột 0 co giãn gấp 1
grid.setColumnStretch(1, 2)                     # Cột 1 co giãn gấp 2
grid.setRowStretch(0, 1)                        # Hàng 0 co giãn
```

### 4.4. Khoảng cách

```python
grid.setSpacing(10)                             # Khoảng cách giữa các ô
grid.setHorizontalSpacing(20)                   # Chỉ ngang
grid.setVerticalSpacing(5)                      # Chỉ dọc
```

### 4.5. Grid có bao nhiêu ô?

```python
rows = grid.rowCount()
cols = grid.columnCount()
```

---

## 🎯 PHẦN 5: QFORMLAYOUT – CHUYÊN CHO FORM

### 5.1. Cơ bản

```python
from PySide6.QtWidgets import QFormLayout

form = QFormLayout()
form.addRow("Họ tên:", QLineEdit())
form.addRow("Email:", QLineEdit())
form.addRow("Địa chỉ:", QLineEdit())
```

`QFormLayout` tự động:
- Cột 1: Label (căn phải)
- Cột 2: Widget (co giãn)

Kết quả:
```
      Họ tên: [_______________]
       Email: [_______________]
     Địa chỉ: [_______________]
```

### 5.2. Row wrapping – Khi cửa sổ hẹp

Mặc định nếu không đủ chỗ, QFormLayout tự động **chuyển widget xuống dưới label**:

```
Họ tên:
[____________________]
```

Kiểm soát bằng:
```python
form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
# WrapLongRows - wrap khi không đủ chỗ (mặc định)
# WrapAllRows   - luôn xuống dòng
# DontWrapRows  - không bao giờ
```

### 5.3. Label alignment

```python
form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)   # Mặc định
form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)    # Căn trái
```

### 5.4. Field growth policy

```python
form.setFieldGrowthPolicy(
    QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
)
```

### 5.5. QFormLayout với QGroupBox

Pattern cực phổ biến khi làm form:

```python
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit

group = QGroupBox("Thông tin cá nhân")
form = QFormLayout(group)                    # Layout gắn vào group
form.addRow("Họ tên:", QLineEdit())
form.addRow("Email:", QLineEdit())
```

Kết quả:
```
┌─ Thông tin cá nhân ──────────┐
│   Họ tên: [_______________]  │
│    Email: [_______________]  │
└──────────────────────────────┘
```

---

## 🎯 PHẦN 6: QSTACKEDLAYOUT – NHIỀU TRANG

### 6.1. Đặc điểm

- Nhiều widget chồng lên nhau
- **Chỉ 1 widget hiển thị** tại mỗi thời điểm
- Chuyển trang bằng `setCurrentIndex()` hoặc `setCurrentWidget()`

### 6.2. Ví dụ

```python
from PySide6.QtWidgets import QStackedLayout, QLabel, QPushButton, QVBoxLayout, QWidget

w = QWidget()
outer = QVBoxLayout(w)

# Stack
stack = QStackedLayout()
stack.addWidget(QLabel("Trang 1"))
stack.addWidget(QLabel("Trang 2"))
stack.addWidget(QLabel("Trang 3"))

# Nút chuyển trang
btn_next = QPushButton("Trang tiếp theo")
def next_page():
    idx = (stack.currentIndex() + 1) % stack.count()
    stack.setCurrentIndex(idx)

btn_next.clicked.connect(next_page)

outer.addLayout(stack)
outer.addWidget(btn_next)
```

### 6.3. Kết hợp QComboBox làm tab

```python
combo = QComboBox()
combo.addItems(["Trang 1", "Trang 2", "Trang 3"])
combo.currentIndexChanged.connect(stack.setCurrentIndex)
```

### 6.4. QStackedWidget – Phiên bản widget của StackedLayout

```python
from PySide6.QtWidgets import QStackedWidget

stack = QStackedWidget()
stack.addWidget(widget1)
stack.addWidget(widget2)
stack.setCurrentIndex(1)
```

👉 **`QStackedWidget`** hay dùng hơn vì nó là widget thực sự, có thể nhúng vào layout, splitter...

---

## 🎯 PHẦN 7: QSPLITTER – CHIA ĐÔI KÉO ĐƯỢC

### 7.1. QSplitter ngang / dọc

```python
from PySide6.QtWidgets import QSplitter, QTextEdit
from PySide6.QtCore import Qt

splitter = QSplitter(Qt.Orientation.Horizontal)
splitter.addWidget(QTextEdit())
splitter.addWidget(QTextEdit())
splitter.addWidget(QTextEdit())
```

Kết quả: 3 vùng có **thanh kéo** giữa để điều chỉnh kích thước.

### 7.2. Properties

```python
splitter.setSizes([100, 300, 100])              # Kích thước từng vùng
splitter.setStretchFactor(0, 1)                 # Vùng 0 co giãn gấp 1
splitter.setStretchFactor(1, 2)                 # Vùng 1 co giãn gấp 2
splitter.setChildrenCollapsible(False)          # Không cho thu nhỏ về 0
splitter.setHandleWidth(5)                      # Độ dày thanh kéo
```

### 7.3. Ẩn/hiện

```python
splitter.widget(0).hide()
splitter.widget(0).show()
```

### 7.4. Signals

```python
splitter.splitterMoved.connect(lambda pos, idx: print(f"Splitter {idx} at {pos}"))
```

---

## 🎯 PHẦN 8: SPACING, MARGINS, SIZE POLICY

### 8.1. Spacing – Khoảng cách giữa các widget

```python
layout.setSpacing(10)                            # Tất cả
layout.setSpacing(0)                             # Sát nhau

# Grid có 2 chiều
grid.setHorizontalSpacing(10)
grid.setVerticalSpacing(5)
```

### 8.2. Margins – Khoảng cách với biên layout

```python
layout.setContentsMargins(20, 10, 20, 10)        # left, top, right, bottom
layout.setContentsMargins(0, 0, 0, 0)            # Không margin
```

**Mặc định** của `QVBoxLayout`, `QHBoxLayout` là `(9, 9, 9, 9)`. Khi lồng nhiều layout, nên đặt về `0` để tránh padding không cần thiết.

```python
inner_layout = QHBoxLayout()
inner_layout.setContentsMargins(0, 0, 0, 0)
```

### 8.3. QSizePolicy – Cách widget co giãn

Mỗi widget có một **size policy** gồm 2 thành phần:
- **Horizontal policy**
- **Vertical policy**

Các giá trị:

| Policy | Ý nghĩa |
|--------|---------|
| `Fixed` | Không co giãn, giữ nguyên `sizeHint` |
| `Minimum` | Có thể to hơn `sizeHint`, không nhỏ hơn |
| `Maximum` | Có thể nhỏ hơn `sizeHint`, không to hơn |
| `Preferred` | Mặc định – co giãn thoải mái |
| `Expanding` | **Ưu tiên** chiếm không gian dư |
| `MinimumExpanding` | Như Minimum nhưng ưu tiên mở rộng |
| `Ignored` | Bỏ qua sizeHint, co giãn tùy ý |

```python
from PySide6.QtWidgets import QSizePolicy

widget.setSizePolicy(
    QSizePolicy.Policy.Expanding,     # Horizontal
    QSizePolicy.Policy.Fixed          # Vertical
)
```

### 8.4. Ví dụ: label luôn ở giữa, nút cố định

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)

w = QWidget()
layout = QVBoxLayout(w)

label = QLabel("Nội dung co giãn")
label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
label.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn = QPushButton("Cố định chiều cao")
btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

layout.addWidget(label)
layout.addWidget(btn)
```

### 8.5. sizeHint, minimumSize, maximumSize

```python
widget.setMinimumSize(100, 50)                   # Không nhỏ hơn
widget.setMaximumSize(400, 200)                  # Không to hơn
widget.setFixedSize(200, 100)                    # Cố định cả 2
widget.setMinimumWidth(100)
widget.setMaximumHeight(500)
```

---

## 🎯 PHẦN 9: SO SÁNH NHANH – CHỌN LAYOUT NÀO?

| Tình huống | Layout nên dùng |
|-----------|-----------------|
| Xếp dọc đơn giản | `QVBoxLayout` |
| Xếp ngang đơn giản | `QHBoxLayout` |
| Form nhập liệu | `QFormLayout` |
| Bàn phím, lưới nút, bảng | `QGridLayout` |
| Nhiều trang chuyển qua lại | `QStackedLayout` / `QStackedWidget` |
| Chia đôi kéo được | `QSplitter` |
| Layout phức tạp | **Lồng nhiều layout** |

---

## 🎯 PHẦN 10: THỰC HÀNH – MÁY TÍNH BỎ TÚI

### 10.1. Yêu cầu

- Màn hình hiển thị phép tính
- Các nút: 0-9, +, -, ×, ÷, =, C, ±, .
- Layout: `QGridLayout`
- Click nút → cập nhật màn hình
- Có phím tắt bàn phím (bonus)

### 10.2. Bố cục Grid

```
┌─────────────────────────────┐
│          MÀN HÌNH           │  ← row 0, span 4
├──────┬──────┬──────┬────────┤
│  C   │  ±   │  ÷   │   ×    │  ← row 1
├──────┼──────┼──────┼────────┤
│  7   │  8   │  9   │   -    │  ← row 2
├──────┼──────┼──────┼────────┤
│  4   │  5   │  6   │   +    │  ← row 3
├──────┼──────┼──────┼────────┤
│  1   │  2   │  3   │        │  ← row 4
├──────┴──────┼──────┤   =    │
│      0      │  .   │        │  ← row 5 (0 span 2)
└─────────────┴──────┴────────┘
```

### 10.3. Code đầy đủ

Tạo file `calculator.py`:

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal


class CalculatorButton(QPushButton):
    """Nút đặc biệt cho máy tính – có style riêng."""
    def __init__(self, text: str, kind: str = "number"):
        super().__init__(text)
        self.kind = kind
        self.setMinimumSize(60, 60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Style theo loại nút
        styles = {
            "number": "background: #f0f0f0; font-size: 20px;",
            "operator": "background: #ff9500; color: white; font-size: 22px;",
            "function": "background: #a5a5a5; color: white; font-size: 20px;",
            "equals": "background: #2196F3; color: white; font-size: 24px; font-weight: bold;",
            "zero": "background: #f0f0f0; font-size: 20px;",
        }
        
        base = styles.get(kind, styles["number"])
        self.setStyleSheet(f"""
            QPushButton {{
                {base}
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                filter: brightness(0.9);
            }}
            QPushButton:pressed {{
                background: #d0d0d0;
            }}
        """)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Máy tính bỏ túi")
        self.resize(320, 480)
        
        # Trạng thái
        self.current = "0"                # Số đang nhập
        self.previous = None              # Số trước đó
        self.operator = None              # Phép toán đang chờ
        self.should_reset = False         # Cờ reset khi nhập số mới
        self.expression = ""              # Hiển thị lịch sử phép tính
        
        # Build UI
        self._build_ui()
        self._update_display()
    
    # ----------------------------------------------------------------
    # XÂY DỰNG GIAO DIỆN
    # ----------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(10)
        
        # ===== Màn hình =====
        screen = QWidget()
        screen_layout = QVBoxLayout(screen)
        screen_layout.setContentsMargins(10, 10, 10, 10)
        screen_layout.setSpacing(5)
        
        self.lbl_expression = QLabel("")
        self.lbl_expression.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.lbl_expression.setStyleSheet(
            "color: #888; font-size: 16px;"
        )
        
        self.lbl_display = QLabel("0")
        self.lbl_display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.lbl_display.setStyleSheet(
            "color: #222; font-size: 40px; font-weight: bold;"
        )
        self.lbl_display.setMinimumHeight(60)
        
        screen_layout.addWidget(self.lbl_expression)
        screen_layout.addWidget(self.lbl_display)
        
        screen.setStyleSheet(
            "background: white; border-radius: 10px;"
        )
        main.addWidget(screen, stretch=2)
        
        # ===== Bàn phím =====
        grid = QGridLayout()
        grid.setSpacing(8)
        
        buttons = [
            # (text, row, col, rowspan, colspan, kind)
            ("C",  1, 0, 1, 1, "function"),
            ("±",  1, 1, 1, 1, "function"),
            ("÷",  1, 2, 1, 1, "operator"),
            ("×",  1, 3, 1, 1, "operator"),
            
            ("7",  2, 0, 1, 1, "number"),
            ("8",  2, 1, 1, 1, "number"),
            ("9",  2, 2, 1, 1, "number"),
            ("-",  2, 3, 1, 1, "operator"),
            
            ("4",  3, 0, 1, 1, "number"),
            ("5",  3, 1, 1, 1, "number"),
            ("6",  3, 2, 1, 1, "number"),
            ("+",  3, 3, 1, 1, "operator"),
            
            ("1",  4, 0, 1, 1, "number"),
            ("2",  4, 1, 1, 1, "number"),
            ("3",  4, 2, 1, 1, "number"),
            ("=",  4, 3, 2, 1, "equals"),
            
            ("0",  5, 0, 1, 2, "zero"),
            (".",  5, 2, 1, 1, "number"),
        ]
        
        for text, row, col, rs, cs, kind in buttons:
            btn = CalculatorButton(text, kind)
            btn.clicked.connect(lambda _, t=text: self._on_button(t))
            grid.addWidget(btn, row, col, rs, cs)
        
        # Đặt stretch cho các hàng nút
        for r in range(1, 6):
            grid.setRowStretch(r, 1)
        for c in range(4):
            grid.setColumnStretch(c, 1)
        
        main.addLayout(grid, stretch=5)
    
    # ----------------------------------------------------------------
    # XỬ LÝ LOGIC
    # ----------------------------------------------------------------
    def _on_button(self, text: str):
        if text.isdigit():
            self._input_digit(text)
        elif text == ".":
            self._input_dot()
        elif text == "C":
            self._clear()
        elif text == "±":
            self._toggle_sign()
        elif text in ("+", "-", "×", "÷"):
            self._set_operator(text)
        elif text == "=":
            self._calculate()
        
        self._update_display()
    
    def _input_digit(self, digit: str):
        if self.should_reset or self.current == "0":
            self.current = digit
            self.should_reset = False
        else:
            self.current += digit
    
    def _input_dot(self):
        if self.should_reset:
            self.current = "0."
            self.should_reset = False
        elif "." not in self.current:
            self.current += "."
    
    def _clear(self):
        self.current = "0"
        self.previous = None
        self.operator = None
        self.should_reset = False
        self.expression = ""
    
    def _toggle_sign(self):
        if self.current.startswith("-"):
            self.current = self.current[1:]
        elif self.current != "0":
            self.current = "-" + self.current
    
    def _set_operator(self, op: str):
        # Nếu đang có phép toán chờ → tính luôn
        if self.previous is not None and self.operator and not self.should_reset:
            self._calculate()
        
        self.previous = self._parse_number(self.current)
        self.operator = op
        self.should_reset = True
        self.expression = f"{self._format(self.previous)} {op}"
    
    def _calculate(self):
        if self.previous is None or self.operator is None:
            return
        
        b = self._parse_number(self.current)
        a = self.previous
        op = self.operator
        
        try:
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op == "×":
                result = a * b
            elif op == "÷":
                if b == 0:
                    self.lbl_display.setText("Lỗi")
                    self._clear()
                    return
                result = a / b
            else:
                return
        except Exception:
            self.lbl_display.setText("Lỗi")
            self._clear()
            return
        
        self.expression = f"{self._format(a)} {op} {self._format(b)} ="
        self.current = self._format(result)
        self.previous = None
        self.operator = None
        self.should_reset = True
    
    # ----------------------------------------------------------------
    # HELPER
    # ----------------------------------------------------------------
    def _parse_number(self, s: str) -> float:
        try:
            return float(s)
        except ValueError:
            return 0.0
    
    def _format(self, num: float) -> str:
        """Format số: bỏ .0 nếu là số nguyên."""
        if num == int(num):
            return str(int(num))
        return f"{num:.10g}"
    
    def _update_display(self):
        self.lbl_display.setText(self.current)
        self.lbl_expression.setText(self.expression)
    
    # ----------------------------------------------------------------
    # PHÍM TẮT BÀN PHÍM
    # ----------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        
        # Số 0-9
        if text in "0123456789":
            self._on_button(text)
        elif text == ".":
            self._on_button(".")
        elif text == "+":
            self._on_button("+")
        elif text == "-":
            self._on_button("-")
        elif text == "*":
            self._on_button("×")
        elif text == "/":
            self._on_button("÷")
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_button("=")
        elif key == Qt.Key.Key_Escape:
            self._on_button("C")
        elif key == Qt.Key.Key_Backspace:
            self._backspace()
        else:
            super().keyPressEvent(event)
    
    def _backspace(self):
        if self.should_reset:
            return
        if len(self.current) > 1:
            self.current = self.current[:-1]
        else:
            self.current = "0"
        self._update_display()


def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 10.4. Điểm đáng chú ý trong code

1. **Subclass `QPushButton`** → `CalculatorButton`: tập trung style, dễ mở rộng
2. **`lambda _, t=text:`**: pattern bắt biến trong vòng lặp (tránh bug late-binding)
3. **`grid.setRowStretch` / `setColumnStretch`**: các hàng/cột chia đều
4. **`addWidget(btn, 4, 3, 2, 1)`**: nút `=` chiếm 2 hàng
5. **`addWidget(btn, 5, 0, 1, 2)`**: nút `0` chiếm 2 cột
6. **Logic `should_reset`**: cờ để biết đang nhập số mới hay tiếp tục số cũ
7. **`keyPressEvent`**: xử lý phím tắt bàn phím
8. **`_format`**: loại bỏ `.0` cho đẹp

### 10.5. Flow xử lý

```
User bấm "7" → current = "7"
User bấm "+" → previous = 7, operator = "+", expression = "7 +"
User bấm "3" → current = "3", should_reset = False
User bấm "=" → calculate: 7 + 3 = 10, current = "10"
```

---

## 📝 BÀI TẬP

### Bài tập 2.3.1 (Cơ bản)
Thiết kế layout cho **form đăng nhập** dùng nested layout:
- Trên cùng: Logo + Tiêu đề (căn giữa)
- Giữa: 2 field (Username, Password) dùng `QFormLayout`
- Dưới: Nút "Đăng nhập" full width
- Bottom: Link "Quên mật khẩu?" căn phải

### Bài tập 2.3.2 (Trung bình)
Làm **layout cho chat app**:
- Bên trái (30%): danh sách bạn bè
- Bên phải (70%): chia 2 phần dọc
  - Trên (80%): vùng tin nhắn
  - Dưới (20%): ô nhập + nút gửi
- Dùng `QSplitter` để có thể kéo

### Bài tập 2.3.3 (Khá)
Làm **dashboard** với `QGridLayout`:
- Ô (0,0): thẻ "Doanh thu" chiếm 2 cột
- Ô (0,2): thẻ "Đơn hàng"
- Ô (1,0): thẻ "Khách hàng" 
- Ô (1,1, 1, 2): thẻ "Biểu đồ" chiếm 2 cột
- Các thẻ là `QGroupBox` với số liệu.

### Bài tập 2.3.4 (Nâng cao)
Mở rộng Máy tính:
- Thêm nút `%`, `√`, `x²`
- Thêm nút "History" mở dialog hiển thị lịch sử phép tính
- Lịch sử lưu trong list, mỗi lần tính xong append vào

### Bài tập 2.3.5 (Khó)
Dùng `QStackedWidget` + `QListWidget` làm **app cài đặt**:
- Cột trái: danh sách mục (General, Account, Privacy, About)
- Cột phải: stack chứa widget tương ứng
- Click item trái → đổi trang phải

---

## ✅ CHECKLIST SAU BÀI 2.3

- [ ] Hiểu tại sao không dùng setGeometry, phải dùng Layout
- [ ] Biết 3 cách gắn layout vào widget
- [ ] Nắm vững `QVBoxLayout` / `QHBoxLayout` / `addStretch` / `addSpacing`
- [ ] Biết stretch factor trong `addWidget` và `setColumnStretch`
- [ ] Thành thạo lồng layout (nested)
- [ ] Biết `QGridLayout` với `addWidget(w, r, c, rs, cs)`
- [ ] Biết `QFormLayout` và dùng với `QGroupBox`
- [ ] Hiểu `QStackedLayout` vs `QStackedWidget`
- [ ] Biết `QSplitter` và các method
- [ ] Hiểu `sizePolicy` (Fixed, Expanding, Preferred...)
- [ ] Phân biệt `setSpacing` vs `setContentsMargins`
- [ ] Hoàn thành Máy tính bỏ túi + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 2.4 – Size Policy, Spacer & Custom Widget**

- Đào sâu `QSizePolicy` với ví dụ cụ thể
- `QSpacerItem` – tạo khoảng trống có kiểm soát
- Kế thừa `QWidget` để tạo **custom widget** đầu tiên
- Compound widget: ghép nhiều widget thành 1
- Build **"Star Rating"** widget tự làm

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 2.4**?
2. **Giải chi tiết một bài tập 2.3.x** nào đó?
3. **Đào sâu** phần nào trong bài này (ví dụ: sizePolicy, nested layout phức tạp hơn)?