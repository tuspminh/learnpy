# 📘 MODULE 4 – BÀI 4.1: QTABWIDGET & QSPLITTER

> **Mục tiêu bài học**:
> - Thành thạo **QTabWidget** – giao diện nhiều tab
> - Hiểu **QTabBar** – thanh tab độc lập (nâng cao)
> - Nắm **QSplitter** chi tiết – chia đôi kéo được
> - Biết **nested splitter** – chia phức tạp như IDE
> - Kết hợp Tab + Splitter để làm app giống VS Code
> - Xây dựng **Text Editor nhiều tab** với split view

---

## 🎯 PHẦN 1: QTABWIDGET – GIAO DIỆN TAB

### 1.1. QTabWidget là gì?

`QTabWidget` là widget chứa nhiều **trang (page)**, mỗi trang là 1 `QWidget`, hiển thị **1 trang tại 1 thời điểm**. User chuyển trang bằng cách click **tab** ở trên.

```
┌──────────────────────────────────────┐
│  ┌─────┬─────┬─────┬─────┐           │
│  │ Tab1│ Tab2│ Tab3│  +  │           │  ← QTabBar
│  └─────┴─────┴─────┴─────┘           │
├──────────────────────────────────────┤
│                                      │
│         Nội dung của Tab2            │  ← Current page
│         (QWidget)                    │
│                                      │
└──────────────────────────────────────┘
```

### 1.2. Cấu trúc

```
QTabWidget
├── QTabBar (thanh tab)
└── QStackedWidget (chứa các page)
    ├── Page 1 (QWidget)
    ├── Page 2 (QWidget)
    └── Page 3 (QWidget)
```

👉 **Insight**: `QTabWidget` = `QTabBar` + `QStackedWidget` gộp lại. Hiểu điều này giúp bạn dùng `QTabBar` riêng khi cần.

### 1.3. Cơ bản – Tạo tab

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QLabel
)

app = QApplication(sys.argv)

tabs = QTabWidget()

# Tạo page 1
page1 = QWidget()
layout1 = QVBoxLayout(page1)
layout1.addWidget(QLabel("Nội dung tab 1"))

# Tạo page 2
page2 = QWidget()
layout2 = QVBoxLayout(page2)
layout2.addWidget(QLabel("Nội dung tab 2"))

# Thêm vào tab widget
tabs.addTab(page1, "Tab 1")
tabs.addTab(page2, "Tab 2")

tabs.resize(500, 400)
tabs.show()
sys.exit(app.exec())
```

### 1.4. Các method chính

```python
# Thêm/xóa
tabs.addTab(widget, "Title")                  # Thêm cuối
tabs.insertTab(index, widget, "Title")        # Chèn vị trí
tabs.removeTab(index)                         # Xóa (widget không bị xóa)

# Truy cập
tabs.currentIndex()                           # Vị trí tab đang active
tabs.currentWidget()                          # Widget đang active
tabs.widget(index)                            # Widget tại vị trí
tabs.indexOf(widget)                          # Ngược lại: widget → index
tabs.count()                                  # Số tab

# Đổi active
tabs.setCurrentIndex(1)
tabs.setCurrentWidget(page2)

# Title & icon
tabs.setTabText(index, "New Title")
tabs.setTabIcon(index, QIcon("icon.png"))
tabs.tabText(index)

# Bật/tắt tab
tabs.setTabEnabled(index, False)
tabs.setTabVisible(index, False)              # Qt 5.15+
tabs.isTabEnabled(index)

# Tooltip
tabs.setTabToolTip(index, "Gợi ý cho tab này")
tabs.setTabWhatsThis(index, "Trợ giúp chi tiết")

# Màu
tabs.setTabTextColor(index, QColor("red"))
```

### 1.5. Signals

```python
tabs.currentChanged.connect(self.on_tab_changed)          # int index
tabs.tabCloseRequested.connect(self.on_tab_close)         # int index
tabs.tabBarClicked.connect(lambda i: print(f"Clicked tab {i}"))
tabs.tabBarDoubleClicked.connect(lambda i: print(f"Double click {i}"))
```

### 1.6. Closable tabs

```python
tabs.setTabsClosable(True)
tabs.tabCloseRequested.connect(self.close_tab)

def close_tab(self, index: int):
    widget = tabs.widget(index)
    tabs.removeTab(index)
    if widget:
        widget.deleteLater()
```

⚠️ **Quan trọng**: `removeTab()` **KHÔNG** xóa widget. Nếu bạn không giữ reference, widget vẫn tồn tại (memory leak). Phải gọi `deleteLater()`.

### 1.7. Movable tabs

```python
tabs.setMovable(True)                         # Kéo đổi vị trí tab
```

### 1.8. Tab position

```python
from PySide6.QtWidgets import QTabWidget

tabs.setTabPosition(QTabWidget.TabPosition.North)     # Mặc định
tabs.setTabPosition(QTabWidget.TabPosition.South)
tabs.setTabPosition(QTabWidget.TabPosition.West)
tabs.setTabPosition(QTabWidget.TabPosition.East)
```

| Position | Vị trí |
|----------|--------|
| `North` | Trên (mặc định) |
| `South` | Dưới |
| `West` | Trái |
| `East` | Phải |

### 1.9. Tab shape

```python
tabs.setTabShape(QTabWidget.TabShape.Rounded)         # Mặc định
tabs.setTabShape(QTabWidget.TabShape.Triangular)      # Kiểu cổ
```

### 1.10. Document mode

```python
tabs.setDocumentMode(True)                    # Kiểu như Chrome/Safari
```

Làm tab phẳng hơn, không có viền khung — thích hợp cho browser, editor.

### 1.11. Elide mode – Cắt ngắn title dài

```python
tabs.setElideMode(Qt.TextElideMode.ElideRight)        # "Very long titl..."
tabs.setElideMode(Qt.TextElideMode.ElideMiddle)       # "Very...title"
tabs.setElideMode(Qt.TextElideMode.ElideLeft)         # "...long title"
tabs.setElideMode(Qt.TextElideMode.ElideNone)         # Không cắt
```

### 1.12. Icon size

```python
from PySide6.QtCore import QSize
tabs.setIconSize(QSize(24, 24))
```

### 1.13. Uses scroll buttons

Khi có quá nhiều tab không vừa chiều rộng:

```python
tabs.setUsesScrollButtons(True)               # Mặc định - hiện nút < >
tabs.setUsesScrollButtons(False)              # Thu nhỏ tab lại
```

### 1.14. Corner widget

Góc phải của tab bar có thể đặt widget:

```python
from PySide6.QtWidgets import QPushButton

btn_new = QPushButton("+")
btn_new.setFixedSize(24, 24)
btn_new.clicked.connect(self.add_new_tab)
tabs.setCornerWidget(btn_new, Qt.Corner.TopRightCorner)
```

### 1.15. Ví dụ – Tab Widget cơ bản

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox
)


class DemoTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Nút "+" góc phải
        btn_add = QPushButton("+")
        btn_add.setFixedSize(28, 28)
        btn_add.setToolTip("Thêm tab mới")
        btn_add.clicked.connect(self.add_new_tab)
        self.setCornerWidget(btn_add, Qt.Corner.TopRightCorner)
        
        # Signals
        self.tabCloseRequested.connect(self.close_tab)
        
        # Tab đầu tiên
        self.add_new_tab()
    
    def add_new_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        editor = QTextEdit()
        editor.setPlaceholderText("Nhập gì đó...")
        layout.addWidget(editor)
        
        idx = self.addTab(page, f"Untitled {self.count() + 1}")
        self.setCurrentIndex(idx)
    
    def close_tab(self, index: int):
        widget = self.widget(index)
        self.removeTab(index)
        if widget:
            widget.deleteLater()


app = QApplication(sys.argv)
w = DemoTabs()
w.resize(600, 400)
w.show()
sys.exit(app.exec())
```

---

## 🎯 PHẦN 2: QTABBAR – THANH TAB ĐỘC LẬP

### 2.1. Khi nào dùng QTabBar riêng?

- Cần **kiểm soát chi tiết** thanh tab (custom paint)
- Tab không đi kèm page (như tab trong browser preview)
- Cần **tab bar** ở nhiều nơi với 1 stack chung
- Custom style phức tạp

### 2.2. QTabBar cơ bản

```python
from PySide6.QtWidgets import QTabBar, QStackedWidget

tab_bar = QTabBar()
tab_bar.addTab("Tab 1")
tab_bar.addTab("Tab 2")
tab_bar.addTab("Tab 3")

stack = QStackedWidget()
stack.addWidget(page1)
stack.addWidget(page2)
stack.addWidget(page3)

# Đồng bộ
tab_bar.currentChanged.connect(stack.setCurrentIndex)
```

### 2.3. Method của QTabBar

```python
tab_bar.addTab("Title")                       # Thêm
tab_bar.insertTab(index, "Title")
tab_bar.removeTab(index)
tab_bar.count()
tab_bar.currentIndex()
tab_bar.setCurrentIndex(i)
tab_bar.tabText(i)
tab_bar.setTabText(i, "New")
tab_bar.setTabData(i, data)                   # Lưu bất kỳ dữ liệu
tab_bar.tabData(i)
tab_bar.moveTab(from_idx, to_idx)             # Đổi vị trí
tab_bar.setTabButton(i, pos, widget)          # Đặt widget trong tab
tab_bar.tabRect(i)                            # QRect của tab
```

### 2.4. Ví dụ – Tab bar + Stack

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabBar,
    QStackedWidget, QLabel
)


class TabBarDemo(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(False)     # Không giãn full width
        self.tab_bar.setMovable(True)
        layout.addWidget(self.tab_bar)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        
        # Thêm 3 tab
        for name in ["Trang 1", "Trang 2", "Trang 3"]:
            self.tab_bar.addTab(name)
            page = QLabel(f"Nội dung: {name}")
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(page)
        
        # Đồng bộ
        self.tab_bar.currentChanged.connect(self.stack.setCurrentIndex)


app = QApplication(sys.argv)
w = TabBarDemo()
w.resize(500, 400)
w.show()
sys.exit(app.exec())
```

---

## 🎯 PHẦN 3: QSPLITTER – CHI TIẾT

### 3.1. QSplitter là gì?

`QSplitter` chia vùng chứa thành nhiều phần, giữa các phần có **thanh kéo** để user điều chỉnh kích thước.

```
┌───────────────────────────────────────┐
│                                       │
│    Widget 1                           │
│                                       │
├═══════════════════════════════════════┤  ← Handle (kéo được)
│                                       │
│    Widget 2                           │
│                                       │
└───────────────────────────────────────┘
```

### 3.2. 2 hướng

```python
from PySide6.QtCore import Qt

# Ngang: chia trái/phải
splitter = QSplitter(Qt.Orientation.Horizontal)

# Dọc: chia trên/dưới
splitter = QSplitter(Qt.Orientation.Vertical)
```

### 3.3. Thêm widget

```python
splitter.addWidget(widget1)
splitter.addWidget(widget2)
splitter.addWidget(widget3)

# Hoặc chèn vị trí
splitter.insertWidget(1, widget_new)

# Xóa (không xóa widget)
splitter.widget(index).setParent(None)
# Hoặc
widget.setParent(None)
```

### 3.4. Kích thước

```python
# Đặt kích thước ban đầu (pixel) — sẽ được scale theo tỉ lệ
splitter.setSizes([200, 400, 200])            # Tỉ lệ 1:2:1

# Stretch factor — tỉ lệ co giãn khi resize
splitter.setStretchFactor(0, 1)               # Widget 0
splitter.setStretchFactor(1, 2)               # Widget 1 rộng gấp đôi
splitter.setStretchFactor(2, 1)               # Widget 2

# Đọc kích thước hiện tại
sizes = splitter.sizes()                      # list[int]

# Collapsible — cho phép thu về 0?
splitter.setCollapsible(0, False)             # Không cho thu nhỏ
splitter.setCollapsible(1, True)              # Cho phép

# Kích thước handle
splitter.setHandleWidth(8)                    # 8px

# Children có thể được kéo để sắp xếp lại?
splitter.setChildrenCollapsible(True)
```

### 3.5. Handle (thanh kéo)

```python
# Ẩn handle của widget
splitter.handle(index)                        # QSplitterHandle
splitter.handle(1).setEnabled(False)          # Không kéo được
```

### 3.6. Opague resize

```python
# True: resize ngay khi kéo (mượt nhưng nặng)
# False: chỉ hiện đường preview, resize khi thả chuột
splitter.setOpaqueResize(True)
```

### 3.7. Signals

```python
splitter.splitterMoved.connect(self.on_moved)         # (pos: int, index: int)
```

### 3.8. Save/Restore state

```python
# Lưu
state = splitter.saveState()                  # QByteArray
settings.setValue("splitter", state)

# Khôi phục
state = settings.value("splitter")
if state:
    splitter.restoreState(state)
```

### 3.9. Ví dụ cơ bản

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QSplitter, QTextEdit, QListWidget,
    QWidget, QVBoxLayout
)


app = QApplication(sys.argv)

splitter = QSplitter(Qt.Orientation.Horizontal)

left = QListWidget()
left.addItems(["Item 1", "Item 2", "Item 3"])

right = QTextEdit()
right.setPlainText("Nội dung chi tiết...")

splitter.addWidget(left)
splitter.addWidget(right)

# Tỉ lệ 1:3
splitter.setSizes([100, 300])
splitter.setStretchFactor(0, 1)
splitter.setStretchFactor(1, 3)

splitter.setHandleWidth(6)
splitter.setWindowTitle("Splitter Demo")
splitter.resize(700, 400)
splitter.show()

sys.exit(app.exec())
```

### 3.10. Nested Splitter – Chia phức tạp

Đây là **kỹ thuật quan trọng** để làm app giống VS Code:

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QSplitter, QTextEdit, QTreeWidget,
    QTabWidget, QVBoxLayout
)


class IdeLikeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IDE-like Layout")
        self.resize(1200, 700)
        
        # ===== Splitter ngoài: NGANG =====
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Cột trái: cây thư mục ---
        tree = QTreeWidget()
        tree.setHeaderLabel("Explorer")
        tree.addTopLevelItem(tree_item("project/"))
        main_splitter.addWidget(tree)
        
        # --- Cột giữa: vùng editor ---
        editor_area = QWidget()
        editor_layout = QVBoxLayout(editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor chia DỌC thành 2 tab ngang nhau
        editor_splitter = QSplitter(Qt.Orientation.Vertical)
        
        tabs1 = QTabWidget()
        tabs1.addTab(QTextEdit("// file1.py"), "file1.py")
        tabs1.addTab(QTextEdit("// file2.py"), "file2.py")
        editor_splitter.addWidget(tabs1)
        
        tabs2 = QTabWidget()
        tabs2.addTab(QTextEdit("// file3.py"), "file3.py")
        editor_splitter.addWidget(tabs2)
        
        editor_splitter.setSizes([350, 350])
        
        editor_layout.addWidget(editor_splitter)
        main_splitter.addWidget(editor_area)
        
        # --- Cột phải: panel ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        outline = QTreeWidget()
        outline.setHeaderLabel("Outline")
        right_splitter.addWidget(outline)
        
        terminal = QTextEdit()
        terminal.setPlainText("$ ")
        right_splitter.addWidget(terminal)
        
        right_splitter.setSizes([400, 300])
        main_splitter.addWidget(right_splitter)
        
        # ===== Tỉ lệ cột =====
        main_splitter.setSizes([200, 700, 300])
        main_splitter.setStretchFactor(0, 0)          # Cột trái cố định
        main_splitter.setStretchFactor(1, 1)          # Editor co giãn
        main_splitter.setStretchFactor(2, 0)          # Cột phải cố định
        
        # ===== Layout chính =====
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)


def tree_item(text: str):
    from PySide6.QtWidgets import QTreeWidgetItem
    return QTreeWidgetItem([text])


app = QApplication(sys.argv)
w = IdeLikeApp()
w.show()
sys.exit(app.exec())
```

### 3.11. Cấu trúc splitter trong ví dụ

```
MainSplitter (H)
├── Tree (explorer)
├── EditorArea
│   └── EditorSplitter (V)
│       ├── Tabs1
│       └── Tabs2
└── RightSplitter (V)
    ├── Outline
    └── Terminal
```

**Cấu trúc nested splitter** là cách chuẩn để làm layout kiểu IDE.

---

## 🎯 PHẦN 4: SO SÁNH – KHI NÀO DÙNG CÁI NÀO?

| Tình huống | Dùng |
|-----------|------|
| Nhiều page user chuyển qua lại | **QTabWidget** |
| Chia màn hình thành vùng kéo được | **QSplitter** |
| Browser-like tabs | QTabWidget + `setDocumentMode(True)` + `setTabsClosable` |
| IDE layout | Nested Splitter |
| Panel có thể ẩn/hiện | **QDockWidget** (bài sau) |
| Accordion (nhiều mục gập) | **QToolBox** (bài sau) |

---

## 🎯 PHẦN 5: THỰC HÀNH – TEXT EDITOR NHIỀU TAB

### 5.1. Yêu cầu

- `QTabWidget` với:
  - Nút `+` để thêm tab
  - Nút đóng tab (X)
  - Kéo đổi vị trí tab
  - Document mode
- Mỗi tab là 1 editor (`QPlainTextEdit`)
- Menu File: New, Open, Save, Save As, Close Tab, Exit
- Menu View: Split Horizontal, Split Vertical, Unsplit
- Status bar: dòng/cột, tên file
- Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+W (close tab), Ctrl+T (new tab)
- Cảnh báo khi đóng tab có thay đổi chưa lưu
- **Split view**: chia editor hiện tại thành 2 (giống VS Code)

### 5.2. Cấu trúc

```
MainWindow (QMainWindow)
├── Central: QSplitter (H)
│   ├── EditorPanel 1
│   │   └── QTabWidget
│   └── EditorPanel 2 (nếu split)
│       └── QTabWidget
└── Status bar
```

Để đơn giản, tôi sẽ làm **1 panel** trước, phần split sẽ là **bonus**.

### 5.3. Code đầy đủ

Tạo file `multi_tab_editor.py`:

```python
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QPlainTextEdit,
    QVBoxLayout, QFileDialog, QMessageBox, QPushButton, QLabel,
    QSplitter, QToolBar
)


# ============================================================
# EDITOR WIDGET – 1 tab editor
# ============================================================
class EditorTab(QWidget):
    """1 tab editor với file path + trạng thái modified."""
    
    def __init__(self, file_path: Path = None, parent=None):
        super().__init__(parent)
        
        self.file_path: Path | None = file_path
        self.is_modified = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setPlaceholderText("Bắt đầu gõ...")
        self.editor.setTabStopDistance(4 * self.editor.fontMetrics().horizontalAdvance(" "))
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._on_cursor_moved)
        
        layout.addWidget(self.editor)
        
        # Load file nếu có
        if file_path and file_path.exists():
            try:
                self.editor.setPlainText(file_path.read_text(encoding="utf-8"))
                self.is_modified = False
            except (OSError, UnicodeDecodeError) as e:
                QMessageBox.warning(self, "Lỗi", f"Không đọc được file:\n{e}")
    
    # ----------------------------------------------------------
    def display_name(self) -> str:
        name = self.file_path.name if self.file_path else "Untitled"
        return f"{name} •" if self.is_modified else name
    
    def _on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            # Báo cho parent cập nhật title
            parent_tabs = self.parent()
            while parent_tabs and not isinstance(parent_tabs, QTabWidget):
                parent_tabs = parent_tabs.parent()
            if parent_tabs:
                idx = parent_tabs.indexOf(self)
                if idx >= 0:
                    parent_tabs.setTabText(idx, self.display_name())
    
    def _on_cursor_moved(self):
        pass                                 # Status bar do MainWindow quản lý
    
    # ----------------------------------------------------------
    def save(self) -> bool:
        if not self.file_path:
            return False
        try:
            self.file_path.write_text(
                self.editor.toPlainText(), encoding="utf-8"
            )
            self.is_modified = False
            return True
        except OSError as e:
            QMessageBox.critical(self, "Lỗi", f"Không lưu được:\n{e}")
            return False
    
    def save_as(self) -> bool:
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Lưu file", "", "Text files (*.txt);;Python (*.py);;All files (*)"
        )
        if not path_str:
            return False
        self.file_path = Path(path_str)
        return self.save()


# ============================================================
# TAB WIDGET – quản lý nhiều EditorTab
# ============================================================
class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setIconSize(QSize(16, 16))
        
        # Corner "+" button
        btn_add = QPushButton("＋")
        btn_add.setFixedSize(28, 28)
        btn_add.setToolTip("Tab mới (Ctrl+T)")
        btn_add.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
            QPushButton:hover {
                background: #e0e0e0;
                border-radius: 4px;
            }
        """)
        btn_add.clicked.connect(lambda: self.new_tab())
        self.setCornerWidget(btn_add, Qt.Corner.TopRightCorner)
        
        # Signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)
    
    # ----------------------------------------------------------
    def new_tab(self, file_path: Path = None) -> EditorTab:
        tab = EditorTab(file_path)
        idx = self.addTab(tab, tab.display_name())
        self.setCurrentIndex(idx)
        return tab
    
    def current_editor(self) -> EditorTab | None:
        w = self.currentWidget()
        return w if isinstance(w, EditorTab) else None
    
    def close_tab(self, index: int) -> bool:
        tab = self.widget(index)
        if not isinstance(tab, EditorTab):
            return False
        
        # Cảnh báo nếu có thay đổi
        if tab.is_modified:
            reply = QMessageBox.question(
                self, "Chưa lưu",
                f"Lưu thay đổi cho \"{tab.display_name()}\"?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                if not tab.save() and not tab.file_path:
                    tab.save_as()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        
        self.removeTab(index)
        tab.deleteLater()
        return True
    
    def close_all(self) -> bool:
        while self.count() > 0:
            if not self.close_tab(0):
                return False
        return True
    
    def _on_current_changed(self, index: int):
        # Có thể emit signal để MainWindow cập nhật title
        pass


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Tab Editor")
        self.resize(1000, 700)
        
        # --- Central ---
        self.tabs = EditorTabs()
        self.tabs.currentChanged.connect(self._update_status)
        self.setCentralWidget(self.tabs)
        
        # --- Setup ---
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        
        # --- Tab đầu tiên ---
        self.tabs.new_tab()
    
    # ----------------------------------------------------------
    # ACTIONS
    # ----------------------------------------------------------
    def _create_actions(self):
        self.act_new = QAction("📄 &New Tab", self)
        self.act_new.setShortcut("Ctrl+T")
        self.act_new.triggered.connect(lambda: self.tabs.new_tab())
        
        self.act_open = QAction("📂 &Open...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self.open_file)
        
        self.act_save = QAction("💾 &Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self.save_current)
        
        self.act_save_as = QAction("💾 Save &As...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.save_as_current)
        
        self.act_close_tab = QAction("❌ &Close Tab", self)
        self.act_close_tab.setShortcut("Ctrl+W")
        self.act_close_tab.triggered.connect(
            lambda: self.tabs.close_tab(self.tabs.currentIndex())
        )
        
        self.act_exit = QAction("Thoát", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # View
        self.act_split_h = QAction("Split &Horizontal", self)
        self.act_split_h.setShortcut("Ctrl+\\")
        self.act_split_h.triggered.connect(self._split_horizontal)
        
        self.act_unsplit = QAction("&Unsplit", self)
        self.act_unsplit.triggered.connect(self._unsplit)
        
        # Edit
        self.act_undo = QAction("&Undo", self)
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(
            lambda: self._editor_do("undo")
        )
        
        self.act_redo = QAction("&Redo", self)
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_redo.triggered.connect(
            lambda: self._editor_do("redo")
        )
        
        # Help
        self.act_about = QAction("&About", self)
        self.act_about.triggered.connect(self.show_about)
    
    def _editor_do(self, action: str):
        tab = self.tabs.current_editor()
        if tab:
            getattr(tab.editor, action)()
    
    # ----------------------------------------------------------
    # MENUS
    # ----------------------------------------------------------
    def _create_menus(self):
        mb = self.menuBar()
        
        fm = mb.addMenu("&File")
        fm.addAction(self.act_new)
        fm.addAction(self.act_open)
        fm.addSeparator()
        fm.addAction(self.act_save)
        fm.addAction(self.act_save_as)
        fm.addSeparator()
        fm.addAction(self.act_close_tab)
        fm.addAction(self.act_exit)
        
        em = mb.addMenu("&Edit")
        em.addAction(self.act_undo)
        em.addAction(self.act_redo)
        
        vm = mb.addMenu("&View")
        vm.addAction(self.act_split_h)
        vm.addAction(self.act_unsplit)
        
        hm = mb.addMenu("&Help")
        hm.addAction(self.act_about)
    
    # ----------------------------------------------------------
    # TOOLBAR
    # ----------------------------------------------------------
    def _create_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        
        tb.addAction(self.act_new)
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_undo)
        tb.addAction(self.act_redo)
        tb.addSeparator()
        tb.addAction(self.act_split_h)
    
    # ----------------------------------------------------------
    # STATUS BAR
    # ----------------------------------------------------------
    def _create_statusbar(self):
        sb = self.statusBar()
        
        self.lbl_pos = QLabel("Dòng 1, Cột 1")
        sb.addPermanentWidget(self.lbl_pos)
        
        self.lbl_file = QLabel("")
        sb.addPermanentWidget(self.lbl_file)
        
        sb.showMessage("Sẵn sàng")
    
    def _update_status(self):
        tab = self.tabs.current_editor()
        if not tab:
            self.lbl_pos.setText("")
            self.lbl_file.setText("")
            return
        
        cursor = tab.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.lbl_pos.setText(f"Dòng {line}, Cột {col}")
        
        file_str = str(tab.file_path) if tab.file_path else "Chưa lưu"
        modified = " ●" if tab.is_modified else ""
        self.lbl_file.setText(f"{file_str}{modified}")
    
    # ----------------------------------------------------------
    # FILE OPERATIONS
    # ----------------------------------------------------------
    def open_file(self):
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Mở file", "", "Text files (*.txt);;Python (*.py);;All files (*)"
        )
        if not path_str:
            return
        self.tabs.new_tab(Path(path_str))
        self._update_status()
    
    def save_current(self):
        tab = self.tabs.current_editor()
        if not tab:
            return
        if tab.file_path:
            if tab.save():
                self._refresh_tab_title(tab)
                self.statusBar().showMessage("Đã lưu", 2000)
                self._update_status()
        else:
            self.save_as_current()
    
    def save_as_current(self):
        tab = self.tabs.current_editor()
        if not tab:
            return
        if tab.save_as():
            self._refresh_tab_title(tab)
            self.statusBar().showMessage("Đã lưu", 2000)
            self._update_status()
    
    def _refresh_tab_title(self, tab: EditorTab):
        idx = self.tabs.indexOf(tab)
        if idx >= 0:
            self.tabs.setTabText(idx, tab.display_name())
            self.tabs.setTabToolTip(idx, str(tab.file_path or "Chưa lưu"))
    
    # ----------------------------------------------------------
    # SPLIT VIEW (đơn giản hóa)
    # ----------------------------------------------------------
    def _split_horizontal(self):
        """Chia cửa sổ thành 2 panel editor."""
        # Nếu đã split, không làm gì
        if isinstance(self.centralWidget(), QSplitter):
            QMessageBox.information(self, "Thông báo", "Đã split rồi")
            return
        
        # Lấy tabs hiện tại ra khỏi central
        old_tabs = self.tabs
        self.takeCentralWidget()
        
        # Tạo splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(old_tabs)
        
        # Panel 2
        new_tabs = EditorTabs()
        new_tabs.new_tab()
        splitter.addWidget(new_tabs)
        
        splitter.setSizes([500, 500])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(splitter)
        self.tabs = new_tabs                     # Con trỏ sang panel mới
        self.tabs.currentChanged.connect(self._update_status)
    
    def _unsplit(self):
        """Bỏ split, quay lại 1 tab widget."""
        cw = self.centralWidget()
        if not isinstance(cw, QSplitter):
            QMessageBox.information(self, "Thông báo", "Chưa split")
            return
        
        # Lấy tab widget đầu tiên
        first = cw.widget(0)
        if not isinstance(first, EditorTabs):
            return
        
        # Xóa các panel khác
        for i in range(cw.count() - 1, 0, -1):
            w = cw.widget(i)
            if isinstance(w, EditorTabs):
                w.close_all()
            w.deleteLater()
        
        cw.widget(0).setParent(None)
        cw.deleteLater()
        
        self.setCentralWidget(first)
        self.tabs = first
        self._update_status()
    
    # ----------------------------------------------------------
    # CLOSE
    # ----------------------------------------------------------
    def closeEvent(self, event):
        # Nếu đang split → đóng tất cả tab của mọi panel
        cw = self.centralWidget()
        panels: list[EditorTabs] = []
        
        if isinstance(cw, QSplitter):
            for i in range(cw.count()):
                w = cw.widget(i)
                if isinstance(w, EditorTabs):
                    panels.append(w)
        elif isinstance(cw, EditorTabs):
            panels.append(cw)
        
        for panel in panels:
            if not panel.close_all():
                event.ignore()
                return
        
        event.accept()
    
    # ----------------------------------------------------------
    # ABOUT
    # ----------------------------------------------------------
    def show_about(self):
        QMessageBox.about(
            self, "About",
            "<h3>Multi-Tab Editor v1.0</h3>"
            "<p>Editor nhiều tab với PySide6.</p>"
            "<p>© 2025</p>"
        )


# ============================================================
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 5.4. Điểm đáng chú ý

1. **Tách lớp rõ ràng**: `EditorTab` (1 file) / `EditorTabs` (quản lý tab) / `MainWindow` (UI tổng)
2. **`EditorTab.display_name()`**: tính cả dấu `•` nếu modified
3. **Tự động cập nhật tab title**: `textChanged` → tìm parent `QTabWidget` → `setTabText`
4. **Corner widget `+`**: với style hover đẹp
5. **`closeEvent` override**: duyệt tất cả panel (kể cả split) để confirm
6. **Split đơn giản**: `takeCentralWidget` → tạo `QSplitter` → thêm 2 panel
7. **Unsplit**: xử lý xóa panel phụ đúng cách
8. **`_refresh_tab_title`**: cập nhật title khi save as xong
9. **`close_all()`**: pattern hay, dùng cho cả tab và panel
10. **`setTabStopDistance`**: độ rộng tab = 4 spaces trong editor

### 5.5. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| New tab | Ctrl+T | Tab mới trống |
| Open file | Ctrl+O | Tab mới có nội dung file |
| Edit | Gõ gì đó | Tab title có dấu `•` |
| Save | Ctrl+S | Dấu `•` biến mất |
| Close tab | Click X | Confirm nếu có thay đổi |
| Close modified | Click X trên tab có `•` | Hiện Save/Discard/Cancel |
| Reorder | Kéo tab | Đổi vị trí |
| Split | Ctrl+\\ | Cửa sổ chia 2 panel |
| Unsplit | Menu View → Unsplit | Quay lại 1 panel |
| Close window | Nút X trên title bar | Confirm tất cả panel |
| Corner + | Click nút `+` | Tab mới |

---

## 📝 BÀI TẬP

### Bài tập 4.1.1 (Cơ bản)
Mở rộng `EditorTabs`:
- Thêm **context menu** chuột phải trên tab: "Close", "Close Others", "Close All", "Close to the Right"
- Dùng `tabBar().customContextMenuRequested` để bắt vị trí click
- Dùng `tabAt(pos)` để biết tab nào

### Bài tập 4.1.2 (Trung bình)
Thêm **unsaved indicator** trực quan:
- Tab có thay đổi → icon chấm đỏ tròn
- Tab đã lưu → icon file bình thường
- Dùng `QPixmap` vẽ icon đơn giản hoặc dùng emoji text

### Bài tập 4.1.3 (Khá)
Làm **save splitter state**:
- Khi đóng app, lưu kích thước splitter vào `QSettings`
- Khi mở lại, khôi phục kích thước cũ
- Nếu splitter không tồn tại → bỏ qua

💡 Gợi ý: `splitter.saveState()` / `splitter.restoreState()`.

### Bài tập 4.1.4 (Nâng cao)
Làm **4 split view** như VS Code:
- Ctrl+\\ → split dọc (2 panel trái/phải)
- Ctrl+Shift+\\ → split ngang (2 panel trên/dưới)
- Cho phép cả 4 góc cùng lúc
- Mỗi panel có thanh tabs riêng

### Bài tập 4.1.5 (Khó)
Làm **drag tab ra ngoài tạo cửa sổ mới**:
- Kéo tab ra khỏi tab bar
- Nếu thả ra ngoài → tạo `MainWindow` mới với tab đó
- Nếu thả vào tab bar khác → chuyển tab

💡 Gợi ý: `tabBar().setAcceptDrops(True)`, override `dropEvent`, dùng `QDrag` với MIME type riêng.

---

## ✅ CHECKLIST SAU BÀI 4.1

- [ ] Biết tạo `QTabWidget` và thêm/xóa tab
- [ ] Hiểu `QTabWidget` = `QTabBar` + `QStackedWidget`
- [ ] Biết `setTabsClosable`, `setMovable`, `setDocumentMode`
- [ ] Biết `tabCloseRequested` và cách xóa tab đúng (`deleteLater`)
- [ ] Biết tab position, shape, elide mode
- [ ] Biết `setCornerWidget` để đặt nút `+`
- [ ] Biết `QTabBar` riêng + `QStackedWidget`
- [ ] Nắm vững `QSplitter`: ngang/dọc
- [ ] Biết `setSizes`, `setStretchFactor`, `setCollapsible`
- [ ] Biết **nested splitter** – làm layout kiểu IDE
- [ ] Biết `saveState` / `restoreState`
- [ ] Hoàn thành Multi-Tab Editor + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 4.2 – QListWidget, QTreeWidget, QTableWidget** (Item-based)

- 3 widget quan trọng cho danh sách dữ liệu
- `QListWidgetItem`, `QTreeWidgetItem`, `QTableWidgetItem`
- Thêm/xóa/sửa item, sort, filter
- Custom widget trong item (`setItemWidget`)
- Kéo thả item
- Multi-select, checkbox trong item
- Build **File Explorer** đơn giản

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 4.2 – QListWidget/QTreeWidget/QTableWidget**?
2. **Giải chi tiết một bài tập 4.1.x** nào?
3. **Đào sâu** phần nào (splitter custom handle, tab drag-out, corner widget nâng cao)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀