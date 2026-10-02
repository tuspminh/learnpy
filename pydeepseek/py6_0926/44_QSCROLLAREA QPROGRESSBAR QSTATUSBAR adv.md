# 📘 MODULE 4 – BÀI 4.4: QSCROLLAREA, QPROGRESSBAR, QSTATUSBAR NÂNG CAO

> **Mục tiêu bài học**:
> - Hiểu sâu **QScrollArea** – viewport, content widget, scrollbar
> - Biết **custom scrollbar** và style
> - Thành thạo **QProgressBar** – determinate & indeterminate
> - Hiểu **QStatusBar** với 3 vùng: message, normal widgets, permanent widgets
> - Biết **QSizeGrip**, `QStatusBar.setSizeGripEnabled()`
> - Build **Download Manager** demo kết hợp cả 3

---

## 🎯 PHẦN 1: QSCROLLAREA – HIỂU SÂU

### 1.1. QScrollArea là gì?

`QScrollArea` là widget cung cấp **vùng cuộn** cho widget con. Khi content lớn hơn vùng hiển thị, scrollbar xuất hiện.

```
┌──────────────────────────────────┐
│ QScrollArea                      │
│ ┌──────────────────────────────┐ │
│ │ Viewport (vùng hiển thị)     │ │
│ │ ┌──────────────────────────┐ │ │
│ │ │ Content Widget           │ │ │
│ │ │ (to hơn viewport)        │ │ │
│ │ │                          │ │ │
│ │ │                          │ │ │
│ │ └──────────────────────────┘ │ │
│ │                        ▲     │ │
│ │                        │     │ │
│ └────────────────────────┼─────┘ │
│                          │       │
│                    Scrollbar     │
└──────────────────────────────────┘
```

### 1.2. Cấu trúc

```
QScrollArea (là QAbstractScrollArea)
├── viewport()  ← QWidget hiển thị
├── widget()    ← Content widget (bạn set)
├── verticalScrollBar()
└── horizontalScrollBar()
```

### 1.3. Cơ bản

```python
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel

scroll = QScrollArea()
scroll.setWidgetResizable(True)              # QUAN TRỌNG

# Content
content = QWidget()
layout = QVBoxLayout(content)
for i in range(50):
    layout.addWidget(QLabel(f"Dòng {i+1}"))

scroll.setWidget(content)
```

⚠️ **`setWidgetResizable(True)`** – CỰC QUAN TRỌNG:
- `True`: content tự resize theo viewport khi viewport lớn hơn content's `sizeHint`
- `False` (mặc định): content giữ nguyên kích thước, chỉ cuộn

**Luôn set `True`** trừ khi bạn cần hành vi đặc biệt.

### 1.4. Properties

```python
# Widget resizable
scroll.setWidgetResizable(True)

# Alignment của content trong viewport (khi content nhỏ hơn viewport)
scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

# Scrollbar policy
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)   # Mặc định
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

# Frame
scroll.setFrameShape(QFrame.Shape.NoFrame)   # Bỏ viền
scroll.setFrameShape(QFrame.Shape.Box)       # Có viền (mặc định)

# Widget hiện tại
scroll.widget()                              # Content widget
scroll.takeWidget()                          # Lấy ra, không xóa
```

### 1.5. ScrollBar Policy – 3 giá trị

| Policy | Ý nghĩa |
|--------|---------|
| `ScrollBarAsNeeded` | Chỉ hiện khi cần (mặc định) |
| `ScrollBarAlwaysOn` | Luôn hiện |
| `ScrollBarAlwaysOff` | Luôn ẩn |

### 1.6. ScrollBar – truy cập

```python
vbar = scroll.verticalScrollBar()
hbar = scroll.horizontalScrollBar()

# Range
vbar.minimum()                               # Thường 0
vbar.maximum()                               # Tổng chiều cao - viewport
vbar.value()                                 # Vị trí hiện tại
vbar.setValue(100)                           # Đặt vị trí
vbar.setRange(0, 1000)

# Đơn vị
vbar.setSingleStep(20)                       # Mỗi mũi tên
vbar.setPageStep(100)                        # Mỗi PageUp/Down

# Inverted
vbar.setInvertedAppearance(True)             # Đảo ngược

# Signals
vbar.valueChanged.connect(self.on_scroll)
vbar.sliderMoved.connect(self.on_drag)
vbar.rangeChanged.connect(self.on_range)     # (min, max)
vbar.actionTriggered.connect(self.on_action)
```

### 1.7. Scroll tới vị trí

```python
# Scroll tuyệt đối
scroll.verticalScrollBar().setValue(500)

# Scroll tới widget con
scroll.ensureWidgetVisible(child_widget)
scroll.ensureWidgetVisible(child_widget, xmargin=50, ymargin=50)

# Scroll tới đầu/cuối
scroll.verticalScrollBar().setValue(0)                             # Lên đầu
vbar = scroll.verticalScrollBar()
vbar.setValue(vbar.maximum())                                      # Xuống cuối

# Scroll tới vị trí % 
def scroll_to_percent(scroll, percent: int):
    vbar = scroll.verticalScrollBar()
    value = int(vbar.maximum() * percent / 100)
    vbar.setValue(value)
```

### 1.8. Signals

```python
# QScrollArea không có signal riêng, phải dùng scrollbar
vbar.valueChanged.connect(self.on_vscroll)
hbar.valueChanged.connect(self.on_hscroll)
```

### 1.9. Ví dụ 1 – Danh sách dài

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton
)


class LongList(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScrollArea Demo")
        self.resize(400, 400)
        
        layout = QVBoxLayout(self)
        
        # ===== Controls =====
        controls = QHBoxLayout()
        btn_top = QPushButton("⬆ Đầu")
        btn_top.clicked.connect(lambda: self.scroll.verticalScrollBar().setValue(0))
        
        btn_bottom = QPushButton("⬇ Cuối")
        btn_bottom.clicked.connect(lambda: self._scroll_to_bottom())
        
        btn_mid = QPushButton("↕ Giữa")
        btn_mid.clicked.connect(lambda: self._scroll_to_percent(50))
        
        controls.addWidget(btn_top)
        controls.addWidget(btn_mid)
        controls.addWidget(btn_bottom)
        layout.addLayout(controls)
        
        # ===== Scroll area =====
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        
        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        for i in range(100):
            lbl = QLabel(f"Dòng {i+1}: Lorem ipsum dolor sit amet...")
            lbl.setStyleSheet(
                "padding: 8px; border-bottom: 1px solid #eee; "
                f"background: {'#f9f9f9' if i % 2 == 0 else 'white'};"
            )
            content_layout.addWidget(lbl)
        
        content_layout.addStretch()
        self.scroll.setWidget(content)
        
        layout.addWidget(self.scroll)
        
        # Scrollbar signal
        self.scroll.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
        # Status
        self.lbl_status = QLabel()
        layout.addWidget(self.lbl_status)
    
    def on_scroll(self, value: int):
        vbar = self.scroll.verticalScrollBar()
        max_val = vbar.maximum()
        percent = int(value * 100 / max_val) if max_val > 0 else 0
        self.lbl_status.setText(f"Vị trí: {value}/{max_val} ({percent}%)")
    
    def _scroll_to_bottom(self):
        vbar = self.scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())
    
    def _scroll_to_percent(self, percent: int):
        vbar = self.scroll.verticalScrollBar()
        vbar.setValue(int(vbar.maximum() * percent / 100))


app = QApplication(sys.argv)
w = LongList()
w.show()
sys.exit(app.exec())
```

### 1.10. Ví dụ 2 – Custom scrollbar style

```python
scroll.setStyleSheet("""
    QScrollBar:vertical {
        background: #f0f0f0;
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #bdc3c7;
        border-radius: 6px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #95a5a6;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;                            /* Ẩn nút mũi tên */
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: transparent;
    }
""")
```

**Selector của QScrollBar**:

| Selector | Phần |
|----------|------|
| `QScrollBar` | Toàn bộ |
| `QScrollBar::handle` | Thanh kéo |
| `QScrollBar::add-line` | Nút tăng (mũi tên xuống) |
| `QScrollBar::sub-line` | Nút giảm (mũi tên lên) |
| `QScrollBar::add-page` | Vùng dưới handle |
| `QScrollBar::sub-page` | Vùng trên handle |
| `QScrollBar::up-arrow` | Icon mũi tên lên |
| `QScrollBar::down-arrow` | Icon mũi tên xuống |

### 1.11. Ví dụ 3 – Dynamic content

Khi bạn thêm widget vào content **sau khi** đã hiển thị:

```python
class DynamicScroll(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        btn_add = QPushButton("Thêm dòng")
        btn_add.clicked.connect(self.add_line)
        layout.addWidget(btn_add)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.addStretch()
        self.scroll.setWidget(self.content)
        
        layout.addWidget(self.scroll)
        
        self.counter = 0
    
    def add_line(self):
        self.counter += 1
        label = QLabel(f"Dòng mới #{self.counter}")
        
        # Chèn trước stretch
        self.content_layout.insertWidget(
            self.content_layout.count() - 1, label
        )
        
        # Auto scroll xuống cuối
        vbar = self.scroll.verticalScrollBar()
        vbar.setValue(vbar.maximum())
```

### 1.12. Khi nào dùng QScrollArea?

| Tình huống | Dùng |
|-----------|------|
| Form dài hơn màn hình | ✅ QScrollArea chứa form |
| Danh sách hàng nghìn item | ❌ Dùng QListView/QListWidget |
| Preview ảnh lớn | ✅ QScrollArea |
| Bảng dữ liệu lớn | ❌ Dùng QTableView |
| Panel chứa nhiều widget | ✅ |

---

## 🎯 PHẦN 2: QPROGRESSBAR

### 2.1. Determinate vs Indeterminate

| Loại | Đặc điểm | Dùng khi |
|------|----------|----------|
| **Determinate** | Có range, hiện % | Biết tiến độ |
| **Indeterminate** | Không có range cụ thể | Không biết tiến độ |

### 2.2. Determinate Progress

```python
from PySide6.QtWidgets import QProgressBar

bar = QProgressBar()
bar.setRange(0, 100)                         # Min, max
bar.setValue(45)                             # 45%

# Đọc giá trị
value = bar.value()
minimum = bar.minimum()
maximum = bar.maximum()

# Format text
bar.setFormat("%p%")                         # Mặc định: "45%"
bar.setFormat("%v / %m")                     # "45 / 100"
bar.setFormat("Đang xử lý %p%...")           # Custom
bar.setFormat("")                            # Không hiện text
bar.setFormat("%p% - %v/%m items")
```

**Format placeholders**:
- `%p` – phần trăm hiện tại
- `%v` – giá trị hiện tại
- `%m` – giá trị max

### 2.3. Hướng

```python
from PySide6.QtCore import Qt

bar.setOrientation(Qt.Orientation.Horizontal)   # Mặc định
bar.setOrientation(Qt.Orientation.Vertical)

# Inverted (từ phải sang trái)
bar.setInvertedAppearance(True)
```

### 2.4. Text alignment & visibility

```python
bar.setTextVisible(False)                    # Ẩn text
bar.setTextVisible(True)

bar.setAlignment(Qt.AlignmentFlag.AlignCenter)   # Mặc định
bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
bar.setAlignment(Qt.AlignmentFlag.AlignRight)
```

### 2.5. Indeterminate (Busy)

```python
bar = QProgressBar()
bar.setRange(0, 0)                           # Indeterminate!
# → Bar chạy qua lại liên tục
```

Cách khác:

```python
bar.setMinimum(0)
bar.setMaximum(0)
```

**Khi nào indeterminate?** Khi không biết mất bao lâu (loading, connecting...).

### 2.6. Signals

```python
bar.valueChanged.connect(self.on_progress)   # int
```

### 2.7. Style QProgressBar

```python
bar.setStyleSheet("""
    QProgressBar {
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        text-align: center;
        background: #ecf0f1;
        height: 25px;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #3498db, stop:1 #2ecc71
        );
        border-radius: 6px;
    }
""")
```

### 2.8. Ví dụ 1 – Determinate

```python
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QProgressBar,
    QPushButton, QHBoxLayout, QLabel
)


class ProgressDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProgressBar Demo")
        self.resize(500, 200)
        
        layout = QVBoxLayout(self)
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setFormat("Đang tải %p%...")
        self.bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 6px;
                text-align: center;
                height: 24px;
            }
            QProgressBar::chunk {
                background: #3498db;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.bar)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        btn_start = QPushButton("Bắt đầu")
        btn_start.clicked.connect(self.start)
        
        btn_pause = QPushButton("Tạm dừng")
        btn_pause.clicked.connect(self.pause)
        
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.reset)
        
        btn_row.addWidget(btn_start)
        btn_row.addWidget(btn_pause)
        btn_row.addWidget(btn_reset)
        layout.addLayout(btn_row)
        
        self.lbl = QLabel("Chưa bắt đầu")
        layout.addWidget(self.lbl)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
    
    def start(self):
        if self.bar.value() >= self.bar.maximum():
            self.bar.setValue(0)
        self.timer.start(100)                # Mỗi 100ms
        self.lbl.setText("Đang chạy...")
    
    def pause(self):
        self.timer.stop()
        self.lbl.setText(f"Tạm dừng ở {self.bar.value()}%")
    
    def reset(self):
        self.timer.stop()
        self.bar.setValue(0)
        self.lbl.setText("Đã reset")
    
    def tick(self):
        v = self.bar.value() + 2
        if v >= 100:
            v = 100
            self.timer.stop()
            self.lbl.setText("✅ Hoàn thành!")
        self.bar.setValue(v)


app = QApplication(sys.argv)
w = ProgressDemo()
w.show()
sys.exit(app.exec())
```

### 2.9. Ví dụ 2 – Busy indicator

```python
class BusyDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Busy Indicator")
        
        layout = QVBoxLayout(self)
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)              # Indeterminate
        self.bar.setTextVisible(False)
        self.bar.setMaximumHeight(20)
        layout.addWidget(self.bar)
        
        btn = QPushButton("Toggle")
        btn.setCheckable(True)
        btn.toggled.connect(self._on_toggle)
        layout.addWidget(btn)
        
        self._on_toggle(True)
    
    def _on_toggle(self, checked: bool):
        if checked:
            self.bar.setRange(0, 0)          # Busy
        else:
            self.bar.setRange(0, 100)
            self.bar.setValue(0)


app = QApplication(sys.argv)
w = BusyDemo()
w.show()
sys.exit(app.exec())
```

### 2.10. Ví dụ 3 – Nhiều task cùng lúc

```python
class MultiTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi Task Progress")
        
        layout = QVBoxLayout(self)
        
        self.bars = []
        for i in range(3):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Task {i+1}:"))
            bar = QProgressBar()
            bar.setRange(0, 100)
            row.addWidget(bar)
            layout.addLayout(row)
            self.bars.append(bar)
        
        # Timer tick khác nhau cho mỗi bar
        self.timers = []
        for i, bar in enumerate(self.bars):
            timer = QTimer()
            timer.timeout.connect(lambda b=bar, s=2+i: self._tick(b, s))
            timer.start(100 + i * 50)
            self.timers.append(timer)
    
    def _tick(self, bar: QProgressBar, step: int):
        v = bar.value() + step
        if v > 100:
            v = 0
        bar.setValue(v)
```

---

## 🎯 PHẦN 3: QSTATUSBAR – CHI TIẾT

### 3.1. 3 vùng của QStatusBar

```
┌─────────────────────────────────────────────────────────────────┐
│  Message (tạm thời)             │ Normal widgets │ Permanent    │
│  showMessage()                  │ addWidget()    │ addPermanentWidget() │
├─────────────────────────────────┼────────────────┼──────────────┤
│  "Đang lưu..."                  │  [ProgressBar] │  [Ln 1, Col 1]│
└─────────────────────────────────────────────────────────────────┘
                                    ▲                ▲
                                    │                │
                                Có thể che        Không bao giờ
                                bởi message       bị che
```

| Vùng | Method | Bị `showMessage()` che? |
|------|--------|:-----------------------:|
| **Message** | `showMessage()` | – (chính nó) |
| **Normal widget** | `addWidget()` | ✅ Bị che |
| **Permanent widget** | `addPermanentWidget()` | ❌ Không bị che |

### 3.2. Message

```python
sb = self.statusBar()

sb.showMessage("Đang xử lý...")              # Vĩnh viễn
sb.showMessage("Xong!", 3000)                # Hiện 3s rồi xóa

sb.clearMessage()                            # Xóa message

# Đọc message hiện tại
sb.currentMessage()

# Signal
sb.messageChanged.connect(self.on_message)   # str
```

### 3.3. Normal widgets

```python
from PySide6.QtWidgets import QLabel, QProgressBar

# Widget bình thường (bên trái, sau message)
lbl_status = QLabel("Ready")
sb.addWidget(lbl_status)

# Có thể ẩn khi cần (khi showMessage chiếm chỗ)
sb.addWidget(lbl_status, stretch=1)

# Xóa
sb.removeWidget(lbl_status)
```

### 3.4. Permanent widgets

```python
# Widget vĩnh viễn (bên phải)
sb.addPermanentWidget(QLabel("Ln 1, Col 1"))
sb.addPermanentWidget(QProgressBar())
sb.addPermanentWidget(QLabel("UTF-8"))

# Stretch (ít dùng)
sb.addPermanentWidget(lbl, stretch=1)
```

⚠️ **Lưu ý**: Permanent widgets **luôn** hiển thị, kể cả khi có message.

### 3.5. Size grip

Góc phải dưới có thể có **size grip** để resize cửa sổ:

```python
sb.setSizeGripEnabled(True)                  # Mặc định: True
sb.setSizeGripEnabled(False)

sb.isSizeGripEnabled()
```

### 3.6. Ví dụ – Status bar đầy đủ

```python
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStatusBar, QLabel, QProgressBar,
    QTextEdit, QPushButton, QWidget, QVBoxLayout
)


class StatusBarDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StatusBar Demo")
        self.resize(700, 500)
        
        # Central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Gõ gì đó...")
        layout.addWidget(self.editor)
        
        btn = QPushButton("Hiện message 3 giây")
        btn.clicked.connect(
            lambda: self.statusBar().showMessage("Đã bấm nút!", 3000)
        )
        layout.addWidget(btn)
        
        # ===== Status bar =====
        self._setup_statusbar()
        
        # Update cursor position
        self.editor.cursorPositionChanged.connect(self._update_cursor)
    
    def _setup_statusbar(self):
        sb = self.statusBar()
        sb.showMessage("Sẵn sàng")
        
        # --- Normal widget (bên trái, sau message) ---
        self.lbl_word_count = QLabel("Từ: 0")
        sb.addWidget(self.lbl_word_count)
        
        # --- Progress (giữa, có thể bị che) ---
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(150)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        sb.addWidget(self.progress, 1)
        
        # --- Permanent widget (bên phải, không bị che) ---
        self.lbl_cursor = QLabel("Dòng 1, Cột 1")
        self.lbl_cursor.setMinimumWidth(120)
        sb.addPermanentWidget(self.lbl_cursor)
        
        self.lbl_encoding = QLabel("UTF-8")
        sb.addPermanentWidget(self.lbl_encoding)
        
        self.lbl_modified = QLabel("")
        sb.addPermanentWidget(self.lbl_modified)
        
        # Đếm từ
        self.editor.textChanged.connect(self._update_word_count)
        
        # Demo progress tự chạy
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick_progress)
        self._timer.start(500)
    
    def _update_cursor(self):
        c = self.editor.textCursor()
        self.lbl_cursor.setText(f"Dòng {c.blockNumber() + 1}, Cột {c.columnNumber() + 1}")
    
    def _update_word_count(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        self.lbl_word_count.setText(f"Từ: {words}")
        
        self.lbl_modified.setText("● Đã sửa")
    
    def _tick_progress(self):
        v = (self.progress.value() + 5) % 100
        self.progress.setValue(v)


app = QApplication(sys.argv)
w = StatusBarDemo()
w.show()
sys.exit(app.exec())
```

---

## 🎯 PHẦN 4: THỰC HÀNH – DOWNLOAD MANAGER

### 4.1. Yêu cầu

App mô phỏng **download manager**:
- Danh sách download (mỗi download 1 hàng)
- Mỗi download: tên file, progress bar, tốc độ, nút Pause/Cancel
- **Status bar**: tổng downloads, tổng tốc độ, progress tổng
- Nút **Add download** (mô phỏng)
- Dùng `QTimer` giả lập tiến trình

### 4.2. Code đầy đủ

Tạo file `download_manager.py`:

```python
import sys
import random
import time
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton, QProgressBar, QToolBar,
    QStatusBar, QMessageBox, QFileDialog, QLineEdit, QSizePolicy,
    QFrame, QMenu
)


# ============================================================
# DOWNLOAD STATE
# ============================================================
class DownloadState(Enum):
    QUEUED = "Đang chờ"
    DOWNLOADING = "Đang tải"
    PAUSED = "Tạm dừng"
    COMPLETED = "Hoàn thành"
    ERROR = "Lỗi"
    CANCELLED = "Đã hủy"


# ============================================================
# DOWNLOAD MODEL
# ============================================================
class Download(QObject):
    progress_changed = Signal()
    state_changed = Signal()
    
    def __init__(self, name: str, size_mb: float):
        super().__init__()
        self.name = name
        self.size_mb = size_mb
        self.downloaded = 0.0
        self.speed = 0.0                      # MB/s
        self.state = DownloadState.QUEUED
        self._last_tick = time.time()
    
    def start(self):
        if self.state in (DownloadState.QUEUED, DownloadState.PAUSED):
            self.state = DownloadState.DOWNLOADING
            self._last_tick = time.time()
            self.state_changed.emit()
    
    def pause(self):
        if self.state == DownloadState.DOWNLOADING:
            self.state = DownloadState.PAUSED
            self.speed = 0.0
            self.state_changed.emit()
    
    def cancel(self):
        self.state = DownloadState.CANCELLED
        self.state_changed.emit()
    
    def tick(self, dt: float):
        """Tiến trình mô phỏng — dt là delta time."""
        if self.state != DownloadState.DOWNLOADING:
            self.speed = 0
            return
        
        # Tốc độ ngẫu nhiên 0.5 - 3 MB/s
        self.speed = random.uniform(0.5, 3.0)
        self.downloaded = min(
            self.downloaded + self.speed * dt,
            self.size_mb
        )
        
        if self.downloaded >= self.size_mb:
            self.state = DownloadState.COMPLETED
            self.speed = 0.0
            self.state_changed.emit()
        
        self.progress_changed.emit()
    
    @property
    def percent(self) -> int:
        if self.size_mb <= 0:
            return 0
        return int(self.downloaded / self.size_mb * 100)


# ============================================================
# DOWNLOAD ROW WIDGET
# ============================================================
class DownloadRow(QFrame):
    """1 hàng download."""
    
    start_clicked = Signal(object)
    pause_clicked = Signal(object)
    cancel_clicked = Signal(object)
    
    def __init__(self, download: Download, parent=None):
        super().__init__(parent)
        self.download = download
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            DownloadRow {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px;
            }
            DownloadRow:hover {
                border-color: #2196F3;
            }
        """)
        
        self._setup_ui()
        self._refresh()
        
        # Connect model signals
        download.progress_changed.connect(self._refresh)
        download.state_changed.connect(self._refresh)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)
        
        # ===== Row 1: name + size + buttons =====
        row1 = QHBoxLayout()
        
        self.lbl_name = QLabel()
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.lbl_size = QLabel()
        self.lbl_size.setStyleSheet("color: #666; font-size: 12px;")
        
        row1.addWidget(self.lbl_name)
        row1.addStretch()
        row1.addWidget(self.lbl_size)
        
        # Buttons
        self.btn_start = QPushButton("▶")
        self.btn_start.setFixedSize(28, 28)
        self.btn_start.setToolTip("Bắt đầu / Tiếp tục")
        self.btn_start.clicked.connect(lambda: self.start_clicked.emit(self.download))
        
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(28, 28)
        self.btn_pause.setToolTip("Tạm dừng")
        self.btn_pause.clicked.connect(lambda: self.pause_clicked.emit(self.download))
        
        self.btn_cancel = QPushButton("✕")
        self.btn_cancel.setFixedSize(28, 28)
        self.btn_cancel.setToolTip("Hủy")
        self.btn_cancel.clicked.connect(lambda: self.cancel_clicked.emit(self.download))
        
        for btn in (self.btn_start, self.btn_pause, self.btn_cancel):
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: #f0f0f0;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background: #e0e0e0; }
                QPushButton:disabled { color: #ccc; }
            """)
            row1.addWidget(btn)
        
        layout.addLayout(row1)
        
        # ===== Row 2: progress =====
        row2 = QHBoxLayout()
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 18px;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #64B5F6
                );
                border-radius: 3px;
            }
        """)
        self.progress.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        
        self.lbl_speed = QLabel("—")
        self.lbl_speed.setFixedWidth(100)
        self.lbl_speed.setStyleSheet("color: #888; font-size: 11px;")
        self.lbl_speed.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        
        row2.addWidget(self.progress, 1)
        row2.addWidget(self.lbl_speed)
        
        layout.addLayout(row2)
        
        # ===== Row 3: state =====
        self.lbl_state = QLabel()
        self.lbl_state.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.lbl_state)
    
    def _refresh(self):
        d = self.download
        
        self.lbl_name.setText(d.name)
        self.lbl_size.setText(
            f"{d.downloaded:.1f} / {d.size_mb:.1f} MB"
        )
        self.progress.setValue(d.percent)
        
        if d.state == DownloadState.DOWNLOADING:
            self.lbl_speed.setText(f"⚡ {d.speed:.2f} MB/s")
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_cancel.setEnabled(True)
            self.lbl_state.setText(f"⬇ {d.state.value}")
        elif d.state == DownloadState.PAUSED:
            self.lbl_speed.setText("—")
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_cancel.setEnabled(True)
            self.lbl_state.setText(f"⏸ {d.state.value}")
        elif d.state == DownloadState.QUEUED:
            self.lbl_speed.setText("—")
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_cancel.setEnabled(True)
            self.lbl_state.setText(f"⏳ {d.state.value}")
        elif d.state == DownloadState.COMPLETED:
            self.lbl_speed.setText("—")
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_cancel.setEnabled(False)
            self.lbl_state.setText(f"✅ {d.state.value}")
            self.lbl_state.setStyleSheet("color: #27ae60; font-size: 11px; font-weight: bold;")
        elif d.state == DownloadState.CANCELLED:
            self.lbl_speed.setText("—")
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_cancel.setEnabled(False)
            self.lbl_state.setText(f"❌ {d.state.value}")
            self.lbl_state.setStyleSheet("color: #e74c3c; font-size: 11px;")


# ============================================================
# DOWNLOAD MANAGER (Main Window)
# ============================================================
class DownloadManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Download Manager")
        self.resize(750, 600)
        
        self.downloads: list[Download] = []
        self.rows: dict[str, DownloadRow] = {}
        
        self._setup_ui()
        self._setup_actions()
        self._setup_toolbar()
        self._setup_statusbar()
        
        # Main timer tick
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick_all)
        self._timer.start(200)                # 200ms
        self._last_tick = time.time()
        
        # Add vài demo
        self._add_demo_downloads()
    
    # ============================================================
    # UI
    # ============================================================
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # ===== Input bar =====
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Tên file:"))
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("video.mp4")
        self.txt_name.returnPressed.connect(self._add_download)
        input_row.addWidget(self.txt_name, 1)
        
        input_row.addWidget(QLabel("Size (MB):"))
        self.txt_size = QLineEdit("100")
        self.txt_size.setFixedWidth(80)
        input_row.addWidget(self.txt_size)
        
        btn_add = QPushButton("➕ Thêm")
        btn_add.clicked.connect(self._add_download)
        input_row.addWidget(btn_add)
        
        layout.addLayout(input_row)
        
        # ===== Scroll area =====
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll, 1)
        
        # Empty state
        self.lbl_empty = QLabel("Chưa có download nào.\nThêm file để bắt đầu.")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(
            "color: #aaa; font-size: 14px; padding: 40px;"
        )
        self.lbl_empty.hide()
        layout.addWidget(self.lbl_empty)
    
    # ============================================================
    # ACTIONS & MENUS
    # ============================================================
    def _setup_actions(self):
        self.act_add = QAction("➕ Thêm download", self)
        self.act_add.setShortcut("Ctrl+N")
        self.act_add.triggered.connect(self._add_download)
        
        self.act_start_all = QAction("▶ Bắt đầu tất cả", self)
        self.act_start_all.triggered.connect(self._start_all)
        
        self.act_pause_all = QAction("⏸ Dừng tất cả", self)
        self.act_pause_all.triggered.connect(self._pause_all)
        
        self.act_clear_done = QAction("🧹 Xóa đã xong", self)
        self.act_clear_done.triggered.connect(self._clear_completed)
        
        self.act_clear_all = QAction("🗑️ Xóa tất cả", self)
        self.act_clear_all.triggered.connect(self._clear_all)
        
        self.act_exit = QAction("Thoát", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # Menu
        mb = self.menuBar()
        
        fm = mb.addMenu("&File")
        fm.addAction(self.act_add)
        fm.addSeparator()
        fm.addAction(self.act_exit)
        
        dm = mb.addMenu("&Download")
        dm.addAction(self.act_start_all)
        dm.addAction(self.act_pause_all)
        dm.addSeparator()
        dm.addAction(self.act_clear_done)
        dm.addAction(self.act_clear_all)
    
    def _setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        
        tb.addAction(self.act_add)
        tb.addSeparator()
        tb.addAction(self.act_start_all)
        tb.addAction(self.act_pause_all)
        tb.addSeparator()
        tb.addAction(self.act_clear_done)
    
    # ============================================================
    # STATUS BAR
    # ============================================================
    def _setup_statusbar(self):
        sb = self.statusBar()
        sb.showMessage("Sẵn sàng")
        
        # Normal widget bên trái (sau message)
        self.lbl_count = QLabel("0 download")
        sb.addWidget(self.lbl_count)
        
        # Progress tổng (giữa, stretch)
        self.total_progress = QProgressBar()
        self.total_progress.setRange(0, 100)
        self.total_progress.setFormat("Tổng: %p%")
        self.total_progress.setMaximumWidth(200)
        sb.addWidget(self.total_progress, 1)
        
        # Permanent widgets bên phải
        self.lbl_total_speed = QLabel("⚡ 0.00 MB/s")
        self.lbl_total_speed.setMinimumWidth(120)
        sb.addPermanentWidget(self.lbl_total_speed)
        
        self.lbl_active = QLabel("Hoạt động: 0")
        self.lbl_active.setMinimumWidth(100)
        sb.addPermanentWidget(self.lbl_active)
    
    # ============================================================
    # ADD DOWNLOAD
    # ============================================================
    def _add_download(self):
        name = self.txt_name.text().strip()
        if not name:
            name = f"file_{len(self.downloads) + 1}.bin"
        
        try:
            size = float(self.txt_size.text() or "100")
            size = max(1.0, min(size, 10000))
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Size phải là số")
            return
        
        download = Download(name, size)
        self.downloads.append(download)
        
        # Tạo row
        row = DownloadRow(download)
        row.start_clicked.connect(self._start_one)
        row.pause_clicked.connect(self._pause_one)
        row.cancel_clicked.connect(self._cancel_one)
        
        self.rows[name] = row
        
        # Insert trước stretch
        self.list_layout.insertWidget(
            self.list_layout.count() - 1, row
        )
        
        self._update_empty_state()
        self._update_stats()
        
        self.txt_name.clear()
        self.txt_name.setFocus()
        
        # Auto start
        download.start()
        
        self.statusBar().showMessage(f"Đã thêm: {name}", 2000)
    
    def _add_demo_downloads(self):
        demos = [
            ("ubuntu-24.04.iso", 4500),
            ("video_lecture.mp4", 850),
            ("dataset.zip", 2200),
        ]
        for name, size in demos:
            self.txt_name.setText(name)
            self.txt_size.setText(str(size))
            self._add_download()
    
    # ============================================================
    # CONTROLS
    # ============================================================
    def _start_one(self, download: Download):
        download.start()
        self.statusBar().showMessage(f"Bắt đầu: {download.name}", 2000)
    
    def _pause_one(self, download: Download):
        download.pause()
        self.statusBar().showMessage(f"Tạm dừng: {download.name}", 2000)
    
    def _cancel_one(self, download: Download):
        download.cancel()
        self.statusBar().showMessage(f"Đã hủy: {download.name}", 2000)
    
    def _start_all(self):
        for d in self.downloads:
            if d.state in (DownloadState.QUEUED, DownloadState.PAUSED):
                d.start()
    
    def _pause_all(self):
        for d in self.downloads:
            d.pause()
    
    def _clear_completed(self):
        to_remove = [
            d for d in self.downloads
            if d.state in (DownloadState.COMPLETED, DownloadState.CANCELLED)
        ]
        for d in to_remove:
            self._remove_download(d)
        
        if to_remove:
            self.statusBar().showMessage(
                f"Đã xóa {len(to_remove)} download", 2000
            )
    
    def _clear_all(self):
        if not self.downloads:
            return
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Xóa tất cả {len(self.downloads)} download?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        for d in list(self.downloads):
            self._remove_download(d)
    
    def _remove_download(self, download: Download):
        self.downloads.remove(download)
        row = self.rows.pop(download.name, None)
        if row:
            self.list_layout.removeWidget(row)
            row.deleteLater()
        
        self._update_empty_state()
        self._update_stats()
    
    # ============================================================
    # TICK
    # ============================================================
    def _tick_all(self):
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now
        
        for d in self.downloads:
            d.tick(dt)
        
        self._update_stats()
    
    # ============================================================
    # STATS & UI UPDATE
    # ============================================================
    def _update_stats(self):
        total = len(self.downloads)
        active = sum(
            1 for d in self.downloads
            if d.state == DownloadState.DOWNLOADING
        )
        total_speed = sum(
            d.speed for d in self.downloads
            if d.state == DownloadState.DOWNLOADING
        )
        
        self.lbl_count.setText(f"{total} download")
        self.lbl_active.setText(f"Hoạt động: {active}")
        self.lbl_total_speed.setText(f"⚡ {total_speed:.2f} MB/s")
        
        # Progress tổng = trung bình cộng
        if total > 0:
            avg = sum(d.percent for d in self.downloads) / total
            self.total_progress.setValue(int(avg))
        else:
            self.total_progress.setValue(0)
    
    def _update_empty_state(self):
        if self.downloads:
            self.scroll.show()
            self.lbl_empty.hide()
        else:
            self.scroll.hide()
            self.lbl_empty.show()
    
    # ============================================================
    # CLOSE
    # ============================================================
    def closeEvent(self, event):
        active = [
            d for d in self.downloads
            if d.state == DownloadState.DOWNLOADING
        ]
        if active:
            reply = QMessageBox.question(
                self, "Đang tải",
                f"Có {len(active)} download đang chạy. Thoát?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        event.accept()


def main():
    app = QApplication(sys.argv)
    w = DownloadManager()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 4.3. Điểm đáng chú ý

1. **`Download` (QObject)**: model với signal, không phụ thuộc UI
2. **`Download.tick(dt)`: mô phỏng download với delta time**
3. **`DownloadRow` (QFrame)**: custom widget cho 1 hàng
4. **Signal từ row → manager**: `start_clicked`, `pause_clicked`, `cancel_clicked`
5. **`_tick_all`**: 1 timer cho toàn bộ, tick mỗi download
6. **Status bar 3 vùng rõ ràng**: message, normal widget (progress), permanent (speed, active)
7. **Progress tổng**: trung bình % của tất cả downloads
8. **Empty state**: ẩn scroll, hiện label khi không có download
9. **Xóa row đúng cách**: `removeWidget` + `deleteLater`
10. **Đổi style khi state thay đổi**: `_refresh` xử lý từng state

### 4.4. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| Add | Nhập tên + size → Enter | Row mới xuất hiện, tự chạy |
| Pause | Click ⏸ | State đổi, progress dừng |
| Resume | Click ▶ | Chạy lại |
| Cancel | Click ✕ | Row chuyển xám |
| Complete | Đợi progress 100% | State ✅, không chạy nữa |
| Total progress | Theo dõi status bar | Cập nhật theo trung bình |
| Total speed | Nhiều download chạy | Tổng speed hiện |
| Clear done | Menu Download | Xóa row đã xong |
| Close guard | Đóng khi có download active | Confirm |

---

## 📝 BÀI TẬP

### Bài tập 4.4.1 (Cơ bản)
Tạo **file preview**:
- `QScrollArea` chứa 1 `QLabel` với ảnh lớn
- Nút "Fit width", "Fit window", "100%", "Zoom in/out"
- Hiển thị % zoom ở status bar

### Bài tập 4.4.2 (Trung bình)
Làm **process bar với custom format**:
- Progress bar hiển thị "Đang xử lý file 5/100 (5%)"
- Đổi format runtime khi cần
- Có nút test với 3 loại format khác nhau

### Bài tập 4.4.3 (Khá)
Mở rộng Download Manager:
- **Pause all / Resume all**
- **Sort** theo tên, size, progress
- **Speed limit** giả lập (chọn 1 MB/s, 5 MB/s, Unlimited)
- Lưu trạng thái vào JSON, load khi mở app

### Bài tập 4.4.4 (Nâng cao)
**Global progress** ở status bar phức tạp:
- Vùng 1: Nút bật/tắt chi tiết
- Vùng 2 (normal widget): Số task đang chạy
- Vùng 3 (normal widget): Progress bar tổng (bị che khi có message dài)
- Vùng 4 (permanent): Memory usage (cập nhật mỗi 1s)
- Vùng 5 (permanent): Time
- Vùng 6 (permanent): Status LED (đỏ/xanh/vàng theo trạng thái)

### Bài tập 4.4.5 (Khó)
**Infinite scroll** với QScrollArea:
- Load 50 item ban đầu
- Khi scroll tới gần cuối → load thêm 50
- Có indicator "Đang tải..."
- Dùng `verticalScrollBar().valueChanged` để detect
- Stop khi hết data

---

## ✅ CHECKLIST SAU BÀI 4.4

- [ ] Hiểu `QScrollArea`: viewport, widget, scrollbar
- [ ] Biết `setWidgetResizable(True)` và tại sao quan trọng
- [ ] Biết scrollbar policy: AsNeeded, AlwaysOn, AlwaysOff
- [ ] Biết truy cập scrollbar: `verticalScrollBar()`, `horizontalScrollBar()`
- [ ] Biết scroll tới vị trí, tới widget, tới %
- [ ] Biết style scrollbar bằng QSS
- [ ] Hiểu `QProgressBar` determinate vs indeterminate
- [ ] Biết `setRange(0, 0)` = busy indicator
- [ ] Biết `setFormat`, `setTextVisible`, `setOrientation`
- [ ] Hiểu 3 vùng của `QStatusBar`
- [ ] Phân biệt `addWidget` vs `addPermanentWidget`
- [ ] Biết `showMessage` với timeout
- [ ] Biết `setSizeGripEnabled`
- [ ] Hoàn thành Download Manager + ít nhất 2 bài tập

---

## 🎓 TỔNG KẾT MODULE 4

| Kỹ năng | Trình độ |
|---------|----------|
| QTabWidget + QTabBar | ✅ Thành thạo |
| QSplitter + nested | ✅ Thành thạo |
| QListWidget/QTreeWidget/QTableWidget | ✅ Thành thạo |
| QDockWidget + save layout | ✅ Thành thạo |
| QToolBox | ✅ Biết dùng |
| QScrollArea | ✅ Hiểu sâu |
| QProgressBar | ✅ Thành thạo |
| QStatusBar 3 vùng | ✅ Thành thạo |

---

## 🔜 MODULE 5 – DIALOG & WINDOW

Tiếp theo:
- **5.1**: QMessageBox, QInputDialog
- **5.2**: QFileDialog, QColorDialog, QFontDialog
- **5.3**: Custom QDialog, QWizard
- **5.4**: QSplashScreen, QSystemTrayIcon

Hoặc chuyển sang **Module 6 – Model/View** (phần chuyên nghiệp nhất).

---

👉 Bạn muốn:
1. **Bắt đầu Module 5 – Bài 5.1: QMessageBox & QInputDialog**?
2. **Bắt đầu Module 6 – Model/View** (chuyên nghiệp)?
3. **Giải chi tiết một bài tập 4.4.x** nào?
4. **Đào sâu** phần nào (custom scrollbar, QScrollArea performance, indeterminate progress)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀