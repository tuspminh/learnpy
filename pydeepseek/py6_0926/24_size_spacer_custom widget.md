# 📘 MODULE 2 – BÀI 2.4: SIZE POLICY, SPACER & CUSTOM WIDGET

> **Mục tiêu bài học**:
> - Hiểu **sâu** `QSizePolicy` – 7 policy và cách chúng tương tác
> - Thành thạo `QSpacerItem` – kiểm soát khoảng trống
> - Biết cách **kế thừa `QWidget`** để tạo custom widget
> - Xây dựng **compound widget** (ghép nhiều widget thành 1)
> - Tự làm widget **"Star Rating"** hoàn chỉnh

---

## 🎯 PHẦN 1: SIZE POLICY – HIỂU SÂU

### 1.1. Tại sao cần Size Policy?

Khi layout tính toán kích thước widget, nó cần biết:

1. **Kích thước "tự nhiên"** của widget là bao nhiêu? → `sizeHint()`
2. **Kích thước nhỏ nhất** có thể chấp nhận? → `minimumSizeHint()`
3. **Nếu còn chỗ dư**, widget có muốn to ra không? → **SizePolicy**

`QSizePolicy` là **hợp đồng** giữa widget và layout: *"Tôi muốn được đối xử thế nào khi có/thiếu không gian?"*

### 1.2. Cấu trúc QSizePolicy

Mỗi `QSizePolicy` có 2 thành phần:

```python
policy = QSizePolicy(horizontal_policy, vertical_policy)
```

Ví dụ:
```python
widget.setSizePolicy(
    QSizePolicy.Policy.Expanding,   # Ngang: muốn to ra
    QSizePolicy.Policy.Fixed        # Dọc: giữ nguyên
)
```

### 1.3. 7 Policy – Giải thích chi tiết

| Policy | Muốn to ra? | Cho phép nhỏ hơn sizeHint? | Dùng khi nào |
|--------|:-----------:|:--------------------------:|--------------|
| **`Fixed`** | ❌ | ❌ | Nút cố định, icon, badge |
| **`Minimum`** | ❌ (nhưng cho phép) | ❌ | Label, muốn giữ size tối thiểu |
| **`Maximum`** | ❌ (nhưng cho phép) | ✅ | Widget có thể co lại |
| **`Preferred`** | Có thể, nhưng không ưu tiên | ❌ | **Mặc định** – an toàn |
| **`Expanding`** | ✅ **Ưu tiên** | ❌ | TextEdit, vùng chính |
| **`MinimumExpanding`** | ✅ **Ưu tiên** | ❌ | Như Expanding, có min rõ |
| **`Ignored`** | ✅ Tùy ý | ✅ | Widget đặc biệt, hiếm dùng |

💡 **Phân biệt `Preferred` vs `Expanding`**:
- `Preferred`: "Tôi có thể to ra nếu cần, nhưng đừng ưu tiên tôi."
- `Expanding`: "Tôi MUỐN to ra, hãy cho tôi không gian dư!"

**Quy tắc vàng**: Khi có nhiều widget `Expanding` cùng layout, chúng **chia nhau** không gian dư. Widget `Preferred` chỉ nhận khi các `Expanding` đã no.

### 1.4. Ví dụ trực quan – 3 label

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QLabel, QSizePolicy
)

app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle("SizePolicy Demo")
w.resize(600, 100)

layout = QHBoxLayout(w)

lbl1 = QLabel("Fixed")
lbl1.setStyleSheet("background: #ffcccc; padding: 10px;")
lbl1.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

lbl2 = QLabel("Preferred")
lbl2.setStyleSheet("background: #ccffcc; padding: 10px;")
lbl2.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

lbl3 = QLabel("Expanding")
lbl3.setStyleSheet("background: #ccccff; padding: 10px;")
lbl3.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

layout.addWidget(lbl1)
layout.addWidget(lbl2)
layout.addWidget(lbl3)

w.show()
sys.exit(app.exec())
```

**Kết quả**:
```
┌────────┬─────────────┬──────────────────────────────────┐
│ Fixed  │  Preferred  │         Expanding                │
└────────┴─────────────┴──────────────────────────────────┘
```

👉 `Expanding` nuốt hết không gian dư. `Preferred` giữ ở sizeHint. `Fixed` đúng bằng sizeHint.

### 1.5. minimumSizeHint vs sizeHint

```python
class MyWidget(QWidget):
    def sizeHint(self):
        # Kích thước tự nhiên (khi có đủ chỗ)
        return QSize(200, 100)
    
    def minimumSizeHint(self):
        # Kích thước tối thiểu chấp nhận được
        return QSize(50, 30)
```

Layout sẽ:
- Nếu có đủ chỗ → cho widget 200x100
- Nếu thiếu chỗ → co xuống tối đa 50x30
- Nếu vẫn thiếu → cắt bớt/scroll

### 1.6. stretch trong layout vs sizePolicy

Hai thứ này **kết hợp** với nhau:

```python
layout.addWidget(btn1, stretch=1)    # Stretch weight
btn1.setSizePolicy(Expanding, Fixed) # Policy
```

**Cách layout tính**:
1. Cho mỗi widget đủ `sizeHint`
2. Còn dư bao nhiêu → chia theo **stretch factor** giữa các widget **có policy cho phép to ra**

### 1.7. Bảng chọn nhanh policy

| Widget | Horizontal | Vertical |
|--------|-----------|----------|
| QPushButton (nút thường) | `Fixed` hoặc `Preferred` | `Fixed` |
| QLabel (text) | `Preferred` | `Preferred` |
| QLineEdit | `Expanding` | `Fixed` |
| QTextEdit | `Expanding` | `Expanding` |
| QSlider | `Expanding` | `Fixed` |
| QProgressBar | `Expanding` | `Fixed` |
| Ảnh (QLabel pixmap) | `Fixed` | `Fixed` |
| Sidebar | `Fixed` | `Expanding` |

---

## 🎯 PHẦN 2: QSPACERITEM – KHOẢNG TRỐNG CÓ KIỂM SOÁT

### 2.1. addStretch vs addSpacing vs addItem(QSpacerItem)

| Cách | Bản chất | Dùng khi |
|------|----------|----------|
| `addStretch(n)` | Shorthand cho `QSpacerItem` với `Expanding` | Cần khoảng trống co giãn |
| `addSpacing(px)` | Thêm khoảng **cố định** px | Khoảng cách không đổi |
| `addItem(QSpacerItem)` | Kiểm soát **chi tiết** | Cần tinh chỉnh |

### 2.2. QSpacerItem – tạo thủ công

```python
from PySide6.QtWidgets import QSpacerItem, QSizePolicy

# Khoảng trống co giãn ngang
spacer = QSpacerItem(
    20, 20,                                    # w, h tối thiểu
    QSizePolicy.Policy.Expanding,              # Ngang co giãn
    QSizePolicy.Policy.Minimum                 # Dọc giữ nguyên
)
layout.addItem(spacer)
```

### 2.3. 3 use case phổ biến

**Use case 1: Nút OK/Cancel căn phải**

```python
layout = QHBoxLayout()
layout.addStretch()                    # Đẩy mọi thứ về phải
layout.addWidget(QPushButton("OK"))
layout.addWidget(QPushButton("Cancel"))
```

**Use case 2: Nút A trái, nút B phải**

```python
layout = QHBoxLayout()
layout.addWidget(QPushButton("Trái"))
layout.addStretch()                    # Ở giữa
layout.addWidget(QPushButton("Phải"))
```

**Use case 3: 3 cột đều nhau**

```python
layout = QHBoxLayout()
layout.addWidget(w1, stretch=1)
layout.addWidget(w2, stretch=1)
layout.addWidget(w3, stretch=1)
```

**Use case 4: Nút giữa, label 2 bên**

```python
layout = QHBoxLayout()
layout.addStretch(1)                   # Trái
layout.addWidget(QPushButton("Center"))
layout.addStretch(1)                   # Phải
```

### 2.4. changeSize – thay đổi kích thước

```python
# Sau này muốn đổi
spacer.changeSize(50, 50, QSizePolicy.Fixed, QSizePolicy.Fixed)
```

---

## 🎯 PHẦN 3: KẾ THỪA QWIDGET – CUSTOM WIDGET

### 3.1. Khi nào cần custom widget?

- **Gom nhóm UI**: 1 khối gồm nhiều widget, muốn tái sử dụng
- **Vẽ tùy biến**: dùng `QPainter` để vẽ
- **Logic phức tạp**: cần xử lý event riêng
- **Đóng gói**: ẩn chi tiết, chỉ expose API sạch

### 3.2. Cấu trúc cơ bản

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal


class MyWidget(QWidget):
    # 1. Định nghĩa signal (nếu có)
    value_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 2. Setup UI
        self._setup_ui()
        # 3. Kết nối signal
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("Hello")
        layout.addWidget(self.label)
    
    def _connect_signals(self):
        pass
    
    # 4. Override method khi cần
    def sizeHint(self):
        return QSize(200, 100)
```

### 3.3. Ví dụ: Compound Widget – "LabeledInput"

Widget gồm label + line edit, hay dùng trong form:

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit
)
from PySide6.QtCore import Signal


class LabeledInput(QWidget):
    """Widget gồm label ở trên + line edit ở dưới."""
    
    text_changed = Signal(str)
    
    def __init__(self, label_text: str = "", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: #555; font-weight: bold;")
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(f"Nhập {label_text.lower()}...")
        self.input.textChanged.connect(self.text_changed)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input)
    
    # API sạch
    def text(self) -> str:
        return self.input.text()
    
    def setText(self, value: str):
        self.input.setText(value)
    
    def clear(self):
        self.input.clear()
    
    def setEchoMode(self, mode):
        self.input.setEchoMode(mode)


# Dùng
class Form(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(LabeledInput("Họ tên"))
        layout.addWidget(LabeledInput("Email"))
        layout.addWidget(LabeledInput("Mật khẩu"))
```

👉 **Điểm hay**: Bên ngoài chỉ cần `LabeledInput("Họ tên")`, không cần biết bên trong có label hay input gì.

### 3.4. Kế thừa widget có sẵn

Có thể kế thừa từ `QPushButton`, `QLabel`... để thêm tính năng:

```python
from PySide6.QtWidgets import QPushButton


class DangerButton(QPushButton):
    """Nút đỏ cảnh báo."""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
```

Dùng:
```python
btn = DangerButton("Xóa tất cả")
```

---

## 🎯 PHẦN 4: QPAINTER CƠ BẢN – VẼ TRONG WIDGET

### 4.1. Khi nào dùng QPainter?

- Vẽ hình, đường, text tùy biến
- Widget đồ họa (progress bar tùy biến, star rating...)
- Hiệu ứng đặc biệt

### 4.2. Cấu trúc – override paintEvent

```python
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRect


class MyWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Làm mượt
        
        # Vẽ hình chữ nhật
        painter.setPen(QPen(QColor("red"), 2))
        painter.setBrush(QBrush(QColor("lightblue")))
        painter.drawRect(10, 10, 100, 50)
        
        # Vẽ text
        painter.setPen(QColor("black"))
        painter.drawText(20, 40, "Hello")
```

### 4.3. Các method vẽ phổ biến

```python
painter.drawRect(x, y, w, h)                     # Hình chữ nhật
painter.drawEllipse(x, y, w, h)                  # Elip
painter.drawLine(x1, y1, x2, y2)                 # Đường thẳng
painter.drawText(x, y, "text")                   # Text
painter.drawPolygon(points)                      # Đa giác
painter.drawPixmap(x, y, pixmap)                 # Ảnh
painter.fillRect(rect, color)                    # Tô màu chữ nhật
painter.drawRoundedRect(x, y, w, h, rx, ry)     # Chữ nhật bo góc
```

### 4.4. Chuyển tọa độ

```python
painter.translate(dx, dy)                        # Dịch chuyển
painter.rotate(angle)                            # Xoay (độ)
painter.scale(sx, sy)                            # Co giãn
```

⚠️ **Quan trọng**: Mọi thay đổi transform **tích lũy**. Nên `painter.save()` / `painter.restore()`:

```python
painter.save()
painter.translate(100, 100)
painter.rotate(45)
# ... vẽ
painter.restore()                                # Quay lại trạng thái cũ
```

---

## 🎯 PHẦN 5: THỰC HÀNH – STAR RATING WIDGET

Chúng ta sẽ build một widget **đánh giá 5 sao** hoàn chỉnh, có hover, click, signal.

### 5.1. Yêu cầu

- Hiển thị 5 ngôi sao
- Hover: highlight các sao từ 1 đến vị trí chuột
- Click: đặt rating
- Có signal `ratingChanged(int)`
- API: `rating()`, `setRating(int)`, `setMaxStars(int)`
- Kích thước có thể tùy chỉnh

### 5.2. Code đầy đủ

Tạo file `star_rating.py`:

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
)
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF, QBrush
from PySide6.QtCore import Qt, QPointF, QSize, Signal, QRectF
import math


class StarRating(QWidget):
    """Widget đánh giá 5 sao."""
    
    ratingChanged = Signal(int)
    
    def __init__(self, max_stars: int = 5, star_size: int = 32, parent=None):
        super().__init__(parent)
        
        self._max_stars = max_stars
        self._star_size = star_size
        self._rating = 0
        self._hover_rating = -1              # -1 = không hover
        
        # Bật theo dõi chuột
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Size cố định theo số sao
        w = self._star_size * self._max_stars + 4 * (self._max_stars - 1)
        h = self._star_size
        self.setMinimumSize(w, h)
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy()
        )
    
    # ================================================================
    # API CÔNG KHAI
    # ================================================================
    def rating(self) -> int:
        return self._rating
    
    def setRating(self, value: int):
        value = max(0, min(value, self._max_stars))
        if value != self._rating:
            self._rating = value
            self.update()
            self.ratingChanged.emit(value)
    
    def maxStars(self) -> int:
        return self._max_stars
    
    def setMaxStars(self, count: int):
        self._max_stars = max(1, count)
        self._update_size()
        self.update()
    
    def setStarSize(self, size: int):
        self._star_size = max(8, size)
        self._update_size()
        self.update()
    
    # ================================================================
    # KÍCH THƯỚC
    # ================================================================
    def _update_size(self):
        w = self._star_size * self._max_stars + 4 * (self._max_stars - 1)
        h = self._star_size
        self.setMinimumSize(w, h)
        self.updateGeometry()
    
    def sizeHint(self) -> QSize:
        w = self._star_size * self._max_stars + 4 * (self._max_stars - 1)
        return QSize(w, self._star_size)
    
    # ================================================================
    # XỬ LÝ CHUỘT
    # ================================================================
    def _star_index_at(self, pos) -> int:
        """Trả về index sao (1-based) tại vị trí chuột, 0 nếu ngoài."""
        step = self._star_size + 4
        idx = int(pos.x() // step) + 1
        if 0 <= pos.x() and idx <= self._max_stars:
            return idx
        return 0
    
    def mouseMoveEvent(self, event):
        idx = self._star_index_at(event.position())
        if idx != self._hover_rating:
            self._hover_rating = idx
            self.update()
    
    def leaveEvent(self, event):
        self._hover_rating = -1
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            idx = self._star_index_at(event.position())
            # Click vào sao đang chọn → bỏ chọn
            if idx == self._rating:
                self.setRating(0)
            else:
                self.setRating(idx)
    
    # ================================================================
    # VẼ
    # ================================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Rating hiệu dụng (ưu tiên hover)
        effective = self._hover_rating if self._hover_rating > 0 else self._rating
        
        step = self._star_size + 4
        
        for i in range(1, self._max_stars + 1):
            x = (i - 1) * step
            y = 0
            rect = QRectF(x, y, self._star_size, self._star_size)
            
            if i <= effective:
                self._draw_star(painter, rect, filled=True)
            else:
                self._draw_star(painter, rect, filled=False)
    
    def _draw_star(self, painter: QPainter, rect: QRectF, filled: bool):
        """Vẽ 1 ngôi sao 5 cánh trong rect."""
        cx = rect.center().x()
        cy = rect.center().y()
        outer_r = min(rect.width(), rect.height()) / 2 - 1
        inner_r = outer_r * 0.4
        
        # Tạo 10 điểm (5 ngoài + 5 trong) xen kẽ
        points = []
        for i in range(10):
            angle_deg = -90 + i * 36               # Bắt đầu từ trên (-90)
            angle_rad = math.radians(angle_deg)
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle_rad)
            y = cy + r * math.sin(angle_rad)
            points.append(QPointF(x, y))
        
        polygon = QPolygonF(points)
        
        if filled:
            painter.setPen(QPen(QColor("#f39c12"), 1))
            painter.setBrush(QBrush(QColor("#f1c40f")))
        else:
            painter.setPen(QPen(QColor("#bdc3c7"), 1.5))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        painter.drawPolygon(polygon)


# ====================================================================
# DEMO
# ====================================================================
class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star Rating Demo")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Rating lớn
        title = QLabel("Đánh giá sản phẩm")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        self.stars = StarRating(max_stars=5, star_size=40)
        self.stars.ratingChanged.connect(self._on_rating_changed)
        layout.addWidget(self.stars)
        
        self.lbl_result = QLabel("Chưa đánh giá")
        self.lbl_result.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.lbl_result)
        
        # Rating nhỏ
        layout.addSpacing(20)
        layout.addWidget(QLabel("Rating nhỏ (16px):"))
        
        small = StarRating(max_stars=5, star_size=16)
        small.setRating(3)
        layout.addWidget(small)
        
        # Rating nhiều sao
        layout.addSpacing(20)
        layout.addWidget(QLabel("10 sao (24px):"))
        
        big = StarRating(max_stars=10, star_size=24)
        big.setRating(7)
        layout.addWidget(big)
        
        layout.addStretch()
    
    def _on_rating_changed(self, rating: int):
        labels = {
            0: "Chưa đánh giá",
            1: "Rất tệ 😡",
            2: "Tệ 😞",
            3: "Bình thường 😐",
            4: "Tốt 🙂",
            5: "Tuyệt vời! 😍",
        }
        self.lbl_result.setText(labels.get(rating, f"{rating} sao"))


def main():
    app = QApplication(sys.argv)
    w = DemoWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 5.3. Điểm đáng chú ý trong code

1. **`Signal(int)`**: định nghĩa signal tùy chỉnh, phát khi rating đổi
2. **`setMouseTracking(True)`**: cần để nhận `mouseMoveEvent` **cả khi không bấm chuột**
3. **`_hover_rating`**: state riêng cho hover, tách khỏi `_rating` thật
4. **`_star_index_at`**: dùng toán học để xác định sao nào từ tọa độ chuột
5. **`leaveEvent`**: reset hover khi chuột rời widget
6. **Click lại sao đang chọn → bỏ chọn**: UX hay
7. **`_draw_star`**: dùng **lượng giác** để vẽ 10 điểm xen kẽ (5 ngoài, 5 trong)
8. **`paintEvent`**: KHÔNG gọi `super().paintEvent()` khi muốn vẽ hoàn toàn tùy chỉnh
9. **`sizeHint` + `setMinimumSize`**: báo cho layout biết widget cần bao nhiêu chỗ
10. **API sạch**: `rating()`, `setRating()`, `ratingChanged` – bên ngoài không cần biết bên trong vẽ thế nào

### 5.4. Công thức vẽ sao

```
Góc: -90° (đỉnh) → 5 đỉnh ngoài + 5 đỉnh trong xen kẽ
Mỗi bước: 36° (360/10)
Bán kính ngoài: outer_r
Bán kính trong: outer_r * 0.4 (tỉ lệ vàng cho sao đẹp)
```

```
        ★ (đỉnh)
       / \
      /   \
     ★     ★
    / \   / \
   ★   ★ ★   ★
    \ /   \ /
     ★     ★
```

### 5.5. Test nhanh

```python
stars = StarRating()
stars.ratingChanged.connect(lambda r: print(f"Rating: {r}"))
stars.setRating(4)
print(stars.rating())     # 4
```

---

## 🎯 PHẦN 6: COMPOUND WIDGET NÂNG CAO – CARD WIDGET

Làm thêm 1 ví dụ compound để thấy sức mạnh custom widget:

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal


class ProductCard(QWidget):
    """Thẻ sản phẩm: ảnh + tên + giá + nút mua."""
    
    buy_clicked = Signal(str)                # Phát tên sản phẩm
    
    def __init__(self, name: str, price: float, image_path: str = None, parent=None):
        super().__init__(parent)
        self._name = name
        self._price = price
        
        self.setFixedSize(200, 280)
        self.setStyleSheet("""
            ProductCard {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            ProductCard:hover {
                border: 2px solid #2196F3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Ảnh
        img = QLabel()
        img.setFixedSize(180, 120)
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setStyleSheet("background: #f5f5f5; border-radius: 4px;")
        if image_path:
            pixmap = QPixmap(image_path).scaled(
                180, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            img.setPixmap(pixmap)
        else:
            img.setText("📦")
            img.setStyleSheet("background: #f5f5f5; border-radius: 4px; font-size: 48px;")
        layout.addWidget(img)
        
        # Tên
        name_label = QLabel(name)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name_label)
        
        # Giá
        price_label = QLabel(f"{price:,.0f} đ")
        price_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        layout.addWidget(price_label)
        
        layout.addStretch()
        
        # Nút mua
        btn = QPushButton("Mua ngay")
        btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn.clicked.connect(lambda: self.buy_clicked.emit(self._name))
        layout.addWidget(btn)
```

**Sử dụng**:
```python
card = ProductCard("iPhone 15", 25_000_000)
card.buy_clicked.connect(lambda name: print(f"Mua {name}"))
```

👉 **Tư duy**: Custom widget = "đóng gói" UI + logic thành 1 khối tái sử dụng.

---

## 📝 BÀI TẬP

### Bài tập 2.4.1 (Cơ bản)
Tạo custom widget `ToggleSwitch`:
- Là công tắc ON/OFF kiểu iOS
- Kế thừa `QWidget`, dùng `QPainter` vẽ
- Có signal `toggled(bool)`
- API: `isChecked()`, `setChecked(bool)`

💡 Gợi ý: Vẽ hình chữ nhật bo tròn + hình tròn di chuyển.

### Bài tập 2.4.2 (Trung bình)
Làm widget `PasswordInput` (compound):
- Label "Mật khẩu" ở trên
- Ô input + nút 👁 ở dưới (toggle hiện/ẩn)
- Signal `returnPressed()`
- API: `text()`, `setText()`, `clear()`

### Bài tập 2.4.3 (Khá)
Custom widget `CircularProgress`:
- Vẽ vòng tròn progress (giống đồng hồ)
- API: `setValue(0-100)`, `value()`
- Signal `valueChanged(int)`
- Hiển thị % ở giữa

💡 Gợi ý: Dùng `painter.drawArc(rect, startAngle, spanAngle)` – đơn vị là 1/16 độ.

### Bài tập 2.4.4 (Nâng cao)
Làm **widget đánh giá cảm xúc** (emoji rating):
- 5 emoji: 😡 😞 😐 🙂 😍
- Hover → emoji to lên
- Click → chọn
- Signal `emojiChanged(str)`

💡 Gợi ý: Dùng font emoji (Segoe UI Emoji trên Windows).

### Bài tập 2.4.5 (Khó)
Làm widget `ColorPicker`:
- Hiển thị lưới các ô màu
- Click chọn màu
- Signal `colorSelected(QColor)`
- API: `currentColor()`, `setColors(list)`

---

## ✅ CHECKLIST SAU BÀI 2.4

- [ ] Hiểu bản chất **QSizePolicy** – không chỉ copy-paste
- [ ] Biết 7 policy và ứng dụng từng loại
- [ ] Phân biệt `Fixed` / `Preferred` / `Expanding`
- [ ] Hiểu `sizeHint()` vs `minimumSizeHint()`
- [ ] Biết dùng `QSpacerItem` và `addStretch`
- [ ] Biết khi nào cần custom widget
- [ ] Kế thừa được `QWidget` và định nghĩa `Signal`
- [ ] Biết `paintEvent` + `QPainter` cơ bản
- [ ] Vẽ được hình cơ bản: rect, ellipse, polygon, text
- [ ] Hiểu `save()` / `restore()` của painter
- [ ] Hoàn thành StarRating + ít nhất 2 bài tập
- [ ] Có thể tạo compound widget tái sử dụng

---

## 🔜 BÀI TIẾP THEO

**Bài 2.5 – Tổng kết Module 2: Project "Todo App"**

Chúng ta sẽ tổng hợp **tất cả** kiến thức Module 2:
- QMainWindow + menu + toolbar + status bar
- Nhiều loại widget nhập liệu
- Layout phức tạp (nested)
- Custom widget (task item)
- Signal/Slot kết nối phức tạp
- Lưu/đọc file JSON

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 2.5 – Project Todo App** (kết thúc Module 2)?
2. **Giải chi tiết một bài tập 2.4.x** nào?
3. **Đào sâu** phần nào (ví dụ: `QPainter` nâng cao, animation, transform)?