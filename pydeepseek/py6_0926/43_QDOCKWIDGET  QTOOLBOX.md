# 📘 MODULE 4 – BÀI 4.3: QDOCKWIDGET & QTOOLBOX

> **Mục tiêu bài học**:
> - Nắm vững **QDockWidget** – panel có thể dock vào cạnh cửa sổ
> - Hiểu **DockWidgetArea** – 4 vùng dock (Left/Right/Top/Bottom)
> - Biết cách **di chuyển**, **float**, **tabify**, **corner** dock widget
> - Lưu/khôi phục **dock layout** với `saveState()` / `restoreState()`
> - Thành thạo **QToolBox** – accordion nhiều mục gập
> - Biết **QMainWindow** với nhiều dock panel
> - Build **IDE mini** với 3-4 dock panels

---

## 🎯 PHẦN 1: QDOCKWIDGET LÀ GÌ?

### 1.1. Khái niệm

**QDockWidget** là một panel **có thể dock** (neo) vào cạnh của `QMainWindow`. Nó có đặc điểm:
- **Neo** vào 1 trong 4 cạnh cửa sổ chính
- Có thể **tách ra** thành cửa sổ nổi (float)
- Có thể **kéo** đến vị trí khác
- Có thể **đóng/mở** qua menu View
- Có **title bar** riêng với nút float và close

```
┌──────────────────────────────────────────────┐
│             MainWindow                       │
│ ┌────────────┬───────────────────┬─────────┐ │
│ │ Dock Left  │                   │ Dock    │ │
│ │            │   Central Widget  │ Right   │ │
│ │ [Tools]    │                   │ [Info]  │ │
│ │            │                   │         │ │
│ ├────────────┤                   ├─────────┤ │
│ │            │                   │ Dock    │ │
│ │ Dock Left  │                   │ Bottom  │ │
│ │ [Outline]  │                   │ [Term]  │ │
│ └────────────┴───────────────────┴─────────┘ │
└──────────────────────────────────────────────┘
```

### 1.2. Cấu trúc

`QDockWidget` là 1 widget chứa **1 widget khác** (không phải layout trực tiếp).

```python
dock = QDockWidget("Title", parent)
dock.setWidget(content_widget)               # Content của dock
main_window.addDockWidget(area, dock)        # Thêm vào MainWindow
```

### 1.3. 4 vùng dock (DockWidgetArea)

```python
from PySide6.QtCore import Qt

Qt.DockWidgetArea.LeftDockWidgetArea         # Cạnh trái
Qt.DockWidgetArea.RightDockWidgetArea        # Cạnh phải
Qt.DockWidgetArea.TopDockWidgetArea          # Cạnh trên
Qt.DockWidgetArea.BottomDockWidgetArea       # Cạnh dưới
Qt.DockWidgetArea.NoDockWidgetArea           # Không dock
Qt.DockWidgetArea.AllDockWidgetAreas         # Tất cả
```

### 1.4. Ví dụ cơ bản

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QListWidget,
    QTextEdit, QWidget, QVBoxLayout, QLabel
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dock Widget Demo")
        self.resize(900, 600)
        
        # Central: editor
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        
        # Dock trái: danh sách file
        self.dock_files = QDockWidget("Files", self)
        files_list = QListWidget()
        files_list.addItems(["file1.py", "file2.py", "file3.py"])
        self.dock_files.setWidget(files_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_files)
        
        # Dock phải: thông tin
        self.dock_info = QDockWidget("Info", self)
        info = QLabel("Thông tin chi tiết ở đây")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dock_info.setWidget(info)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_info)
        
        # Dock dưới: terminal
        self.dock_term = QDockWidget("Terminal", self)
        term = QTextEdit()
        term.setPlainText("$ ")
        self.dock_term.setWidget(term)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_term)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

**Kết quả**: cửa sổ có 3 panel xung quanh editor chính.

---

## 🎯 PHẦN 2: QDOCKWIDGET – CHI TIẾT

### 2.1. Các method quan trọng

```python
# Nội dung
dock.setWidget(widget)                       # Set 1 widget làm content
dock.widget()                                # Lấy widget
dock.setTitleBarWidget(widget)               # Custom title bar (nâng cao)

# Title
dock.setWindowTitle("New Title")
dock.windowTitle()

# Vị trí
main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
main.removeDockWidget(dock)                  # Bỏ khỏi dock
main.splitDockWidget(dock1, dock2, Qt.Orientation.Vertical)  # Chia 2 dock

# Vùng cho phép
dock.setAllowedAreas(
    Qt.DockWidgetArea.LeftDockWidgetArea |
    Qt.DockWidgetArea.RightDockWidgetArea
)
dock.allowedAreas()

# Có thể float (tách ra cửa sổ riêng)?
dock.setFloating(True)                       # Đang floating
dock.isFloating()
dock.setFeatures(...)                        # Các nút trên title bar

# Có thể di chuyển?
dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)  # Khóa
```

### 2.2. DockWidgetFeature – 5 features

```python
QDockWidget.DockWidgetFeature.DockWidgetClosable       # Nút X
QDockWidget.DockWidgetFeature.DockWidgetMovable        # Kéo được
QDockWidget.DockWidgetFeature.DockWidgetFloatable      # Float được
QDockWidget.DockWidgetFeature.DockWidgetVerticalTitleBar  # Title bar dọc
QDockWidget.DockWidgetFeature.NoDockWidgetFeatures     # Không feature nào
QDockWidget.DockWidgetFeature.AllDockWidgetFeatures    # Tất cả (default)
```

**Ví dụ** – Dock cố định (không di chuyển, không float, không close):

```python
dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
```

**Ví dụ** – Chỉ float + close:

```python
dock.setFeatures(
    QDockWidget.DockWidgetFeature.DockWidgetFloatable |
    QDockWidget.DockWidgetFeature.DockWidgetClosable
)
```

### 2.3. Title bar

**Ẩn title bar** (giữ widget, không cho kéo):

```python
dock.setTitleBarWidget(QWidget())             # Empty widget
```

**Custom title bar** – title bar của bạn:

```python
class CustomTitleBar(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        layout.addWidget(QLabel(f"<b>{title}</b>"))
        layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.clicked.connect(lambda: parent.hide())
        layout.addWidget(btn_close)

dock.setTitleBarWidget(CustomTitleBar("Files", dock))
```

### 2.4. Signals

```python
dock.allowedAreasChanged.connect(...)         # Khi allowed areas đổi
dock.dockLocationChanged.connect(...)         # Khi đổi vùng dock
dock.featuresChanged.connect(...)             # Khi features đổi
dock.topLevelChanged.connect(...)             # Khi float/unfloat
dock.visibilityChanged.connect(self.on_visibility)  # Khi ẩn/hiện
```

### 2.5. Tabify DockWidget – Gộp nhiều dock thành tab

```python
main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock1)
main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock2)

# Gộp thành tab
main.tabifyDockWidget(dock1, dock2)

# Đưa dock1 lên trước
dock1.raise_()
```

Kết quả: dock1 và dock2 chia sẻ cùng vùng, có tab trên cùng để chuyển.

### 2.6. Corner – Góc giữa 2 vùng dock

MainWindow có 4 góc. Mặc định góc thuộc 1 vùng dock:

```python
main.setCorner(
    Qt.Corner.TopLeftCorner,
    Qt.DockWidgetArea.LeftDockWidgetArea       # Top-left thuộc left
)
main.setCorner(
    Qt.Corner.BottomRightCorner,
    Qt.DockWidgetArea.BottomDockWidgetArea
)

main.corner(Qt.Corner.TopLeftCorner)          # Đọc lại
```

### 2.7. Split Dock – Chia dock thành 2 phần

```python
main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock1)
main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock2)

# Mặc định: cùng cột, chia ngang
# Muốn chia dọc:
main.splitDockWidget(dock1, dock2, Qt.Orientation.Vertical)
```

### 2.8. Save / Restore layout

Đây là **tính năng quan trọng nhất** của QDockWidget – cho user save/load layout.

```python
# Save
state = main.saveState()                      # QByteArray
settings.setValue("windowState", state)

# Restore
state = settings.value("windowState")
if state:
    main.restoreState(state)

# Save geometry (kích thước + vị trí cửa sổ)
settings.setValue("geometry", main.saveGeometry())
main.restoreGeometry(settings.value("geometry"))
```

⚠️ **Quan trọng**: `saveState()` **CHỈ** lưu layout của dock và toolbar, **KHÔNG** lưu nội dung widget bên trong. Nếu bạn tạo widget trong dock qua code, phải restore đúng.

⚠️ **Đặt `objectName`**: Để `restoreState` hoạt động ổn định, mỗi dock **phải có `objectName`** duy nhất:

```python
dock.setObjectName("dock_files")              # BẮT BUỘC
```

Nếu không có, Qt cảnh báo:
```
QMainWindow::saveState(): 'objectName' not set for QDockWidget
```

### 2.9. Ví dụ – Restore state tự động

```python
from PySide6.QtCore import QSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... setup docks, mỗi dock cần setObjectName
        
        self.settings = QSettings("MyCompany", "MyApp")
        self.restore_layout()
    
    def restore_layout(self):
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("window/state")
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
        super().closeEvent(event)
```

### 2.10. Menu View – Toggle docks

Đây là **UX chuẩn** của app có dock:

```python
def _create_view_menu(self):
    view_menu = self.menuBar().addMenu("&View")
    
    for dock in self.findChildren(QDockWidget):
        # Action checkable, sync với visibility
        action = dock.toggleViewAction()
        view_menu.addAction(action)
    
    view_menu.addSeparator()
    action_reset = QAction("Reset Layout", self)
    action_reset.triggered.connect(self.reset_layout)
    view_menu.addAction(action_reset)
```

**`dock.toggleViewAction()`** trả về 1 `QAction` **tự động**:
- Text = title của dock
- Checkable = trạng thái visible
- Khi toggle → ẩn/hiện dock

Rất tiện!

---

## 🎯 PHẦN 3: QTOOLBOX – ACCORDION

### 3.1. Khái niệm

**QToolBox** là widget hiển thị **nhiều trang xếp chồng**, mỗi lần chỉ **1 trang mở** (giống accordion hoặc sidebar của Photoshop).

```
┌─────────────────┐
│ ▶ Mục 1         │  ← Đóng
├─────────────────┤
│ ▼ Mục 2         │  ← Mở
│                 │
│  Nội dung của   │
│  mục 2          │
│                 │
├─────────────────┤
│ ▶ Mục 3         │
└─────────────────┘
```

### 3.2. Tạo QToolBox

```python
from PySide6.QtWidgets import QToolBox, QWidget, QVBoxLayout, QLabel, QPushButton

toolbox = QToolBox()

# Thêm trang
page1 = QWidget()
layout1 = QVBoxLayout(page1)
layout1.addWidget(QLabel("Nội dung mục 1"))
toolbox.addItem(page1, "Mục 1")

page2 = QWidget()
layout2 = QVBoxLayout(page2)
layout2.addWidget(QPushButton("Button"))
toolbox.addItem(page2, "Mục 2")
```

### 3.3. Method của QToolBox

```python
# Thêm/xóa
toolbox.addItem(widget, "Title")
toolbox.insertItem(index, widget, "Title")
toolbox.removeItem(index)

# Truy cập
toolbox.currentIndex()
toolbox.currentWidget()
toolbox.setCurrentIndex(i)
toolbox.setCurrentWidget(widget)
toolbox.widget(index)
toolbox.indexOf(widget)
toolbox.count()

# Title & icon
toolbox.setItemText(index, "New Title")
toolbox.itemText(index)
toolbox.setItemIcon(index, QIcon("icon.png"))
toolbox.itemIcon(index)

# Bật/tắt
toolbox.setItemEnabled(index, False)
toolbox.isItemEnabled(index)

# Tooltip
toolbox.setItemToolTip(index, "Gợi ý")
```

### 3.4. Signals

```python
toolbox.currentChanged.connect(self.on_page_changed)  # int index
```

### 3.5. Ví dụ – Sidebar Photoshop-like

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBox, QLabel, QPushButton, QSlider, QCheckBox,
    QSpinBox, QComboBox, QFormLayout
)


class ToolboxSidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toolbox Demo")
        self.resize(300, 600)
        
        layout = QVBoxLayout(self)
        
        toolbox = QToolBox()
        
        # ===== Mục 1: Màu sắc =====
        color_page = QWidget()
        color_layout = QFormLayout(color_page)
        color_layout.addRow("Màu nền:", QPushButton("Chọn..."))
        color_layout.addRow("Màu cọ:", QPushButton("Chọn..."))
        color_layout.addRow("Độ trong suốt:", QSlider(Qt.Orientation.Horizontal))
        toolbox.addItem(color_page, "🎨 Màu sắc")
        
        # ===== Mục 2: Cọ vẽ =====
        brush_page = QWidget()
        brush_layout = QVBoxLayout(brush_page)
        brush_layout.addWidget(QLabel("Loại cọ:"))
        combo = QComboBox()
        combo.addItems(["Bút chì", "Cọ mềm", "Cọ cứng", "Bút lông"])
        brush_layout.addWidget(combo)
        brush_layout.addWidget(QLabel("Kích thước:"))
        brush_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        brush_layout.addWidget(QLabel("Độ mềm:"))
        brush_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        brush_layout.addStretch()
        toolbox.addItem(brush_page, "🖌️ Cọ vẽ")
        
        # ===== Mục 3: Layers =====
        layers_page = QWidget()
        layers_layout = QVBoxLayout(layers_page)
        for i in range(3):
            layers_layout.addWidget(QCheckBox(f"Layer {i+1}"))
        layers_layout.addWidget(QPushButton("+ Thêm layer"))
        layers_layout.addStretch()
        toolbox.addItem(layers_page, "📚 Layers")
        
        # ===== Mục 4: Cài đặt =====
        settings_page = QWidget()
        settings_layout = QFormLayout(settings_page)
        settings_layout.addRow("Kích thước canvas:", QSpinBox())
        settings_layout.addRow("Đơn vị:", QComboBox())
        toolbox.addItem(settings_page, "⚙️ Cài đặt")
        
        layout.addWidget(toolbox)


app = QApplication(sys.argv)
w = ToolboxSidebar()
w.show()
sys.exit(app.exec())
```

### 3.6. QToolBox vs QTabWidget vs QStackedWidget

| Widget | Đặc điểm | Dùng khi |
|--------|----------|----------|
| **QTabWidget** | Tab ngang, nhiều tab thấy cùng lúc | Nội dung chính nhiều loại |
| **QToolBox** | Accordion dọc, chỉ 1 mở | Sidebar, palette công cụ |
| **QStackedWidget** | Không có UI chuyển, phải code | Wizard, multi-step |

### 3.7. QToolBox vs QDockWidget với Tabify

Cả 2 đều cho accordion. Khác biệt:

| QToolBox | QDockWidget (tabify) |
|----------|----------------------|
| Cố định trong 1 vùng | Có thể dock/float/di chuyển |
| Chỉ 1 mở cùng lúc | Chuyển tab |
| Đơn giản | Linh hoạt |
| Sidebar đơn giản | IDE panels |

---

## 🎯 PHẦN 4: THỰC HÀNH – IDE MINI

### 4.1. Yêu cầu

Xây dựng **IDE mini** với:
- **Central widget**: Editor (`QPlainTextEdit`)
- **Dock trái**: File Explorer (Tree)
- **Dock phải**: Properties (Form)
- **Dock dưới**: Terminal / Output (TextEdit)
- **Dock trái thứ 2**: Outline (tabify với Explorer)
- Menu **View** để toggle các dock
- **Save/Load layout** khi đóng/mở app
- Toolbar với nút Save, Open, Reset Layout

### 4.2. Code đầy đủ

Tạo file `ide_mini.py`:

```python
import sys
from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QPlainTextEdit,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QToolBar, QLabel, QMessageBox, QTextEdit,
    QFileDialog
)
from pathlib import Path


class IdeMini(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IDE Mini")
        self.resize(1200, 800)
        
        self.settings = QSettings("MyCompany", "IdeMini")
        
        # ===== Central: Editor =====
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setPlaceholderText("// Bắt đầu code ở đây...")
        self.editor.setTabStopDistance(
            4 * self.editor.fontMetrics().horizontalAdvance(" ")
        )
        self.setCentralWidget(self.editor)
        
        # ===== Create docks =====
        self._create_file_dock()
        self._create_outline_dock()
        self._create_properties_dock()
        self._create_terminal_dock()
        
        # ===== Tabify Explorer + Outline =====
        self.tabifyDockWidget(self.dock_explorer, self.dock_outline)
        self.dock_explorer.raise_()               # Explorer hiện trước
        
        # ===== Corner =====
        self.setCorner(
            Qt.Corner.BottomLeftCorner,
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        # ===== Actions/Menu =====
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        
        # ===== Restore layout =====
        self._restore_layout()
        
        # Load file demo
        self._load_demo_files()
    
    # ================================================================
    # DOCK: FILE EXPLORER
    # ================================================================
    def _create_file_dock(self):
        self.dock_explorer = QDockWidget("📁 Explorer", self)
        self.dock_explorer.setObjectName("dock_explorer")     # BẮT BUỘC
        self.dock_explorer.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemDoubleClicked.connect(self._on_file_double_click)
        
        self.dock_explorer.setWidget(self.tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_explorer)
    
    # ================================================================
    # DOCK: OUTLINE
    # ================================================================
    def _create_outline_dock(self):
        self.dock_outline = QDockWidget("📋 Outline", self)
        self.dock_outline.setObjectName("dock_outline")
        self.dock_outline.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.outline = QListWidget()
        self.outline.addItems([
            "class MainWindow",
            "  def __init__",
            "  def setup_ui",
            "  def create_actions",
            "  def save_file",
        ])
        
        self.dock_outline.setWidget(self.outline)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_outline)
    
    # ================================================================
    # DOCK: PROPERTIES
    # ================================================================
    def _create_properties_dock(self):
        self.dock_props = QDockWidget("⚙️ Properties", self)
        self.dock_props.setObjectName("dock_props")
        self.dock_props.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        page = QWidget()
        form = QFormLayout(page)
        
        self.txt_name = QLineEdit()
        self.cbo_lang = QComboBox()
        self.cbo_lang.addItems(["Python", "JavaScript", "C++", "Rust"])
        self.spin_tabsize = QSpinBox()
        self.spin_tabsize.setRange(1, 8)
        self.spin_tabsize.setValue(4)
        
        form.addRow("Tên file:", self.txt_name)
        form.addRow("Ngôn ngữ:", self.cbo_lang)
        form.addRow("Tab size:", self.spin_tabsize)
        
        self.dock_props.setWidget(page)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_props)
    
    # ================================================================
    # DOCK: TERMINAL
    # ================================================================
    def _create_terminal_dock(self):
        self.dock_term = QDockWidget("💻 Terminal", self)
        self.dock_term.setObjectName("dock_term")
        self.dock_term.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea
        )
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet(
            "background: #1e1e1e; color: #d4d4d4; "
            "font-family: Consolas; font-size: 12px;"
        )
        self.terminal.setPlainText("$ Welcome to IDE Mini\n$ Ready...")
        
        self.dock_term.setWidget(self.terminal)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_term)
    
    # ================================================================
    # ACTIONS
    # ================================================================
    def _create_actions(self):
        self.act_new = QAction("📄 New", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self._new_file)
        
        self.act_open = QAction("📂 Open...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self._open_file)
        
        self.act_save = QAction("💾 Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self._save_file)
        
        self.act_exit = QAction("Thoát", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # View actions
        self.act_reset_layout = QAction("🔄 Reset Layout", self)
        self.act_reset_layout.triggered.connect(self._reset_layout)
        
        self.act_fullscreen = QAction("⛶ Fullscreen", self)
        self.act_fullscreen.setShortcut("F11")
        self.act_fullscreen.setCheckable(True)
        self.act_fullscreen.toggled.connect(self._toggle_fullscreen)
    
    # ================================================================
    # MENUS
    # ================================================================
    def _create_menus(self):
        mb = self.menuBar()
        
        fm = mb.addMenu("&File")
        fm.addAction(self.act_new)
        fm.addAction(self.act_open)
        fm.addAction(self.act_save)
        fm.addSeparator()
        fm.addAction(self.act_exit)
        
        # View menu – auto-generated từ docks
        vm = mb.addMenu("&View")
        
        # Dùng toggleViewAction của mỗi dock
        vm.addAction(self.dock_explorer.toggleViewAction())
        vm.addAction(self.dock_outline.toggleViewAction())
        vm.addAction(self.dock_props.toggleViewAction())
        vm.addAction(self.dock_term.toggleViewAction())
        
        vm.addSeparator()
        vm.addAction(self.act_reset_layout)
        vm.addSeparator()
        vm.addAction(self.act_fullscreen)
    
    # ================================================================
    # TOOLBAR
    # ================================================================
    def _create_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)
        
        tb.addAction(self.act_new)
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_reset_layout)
    
    # ================================================================
    # STATUS BAR
    # ================================================================
    def _create_statusbar(self):
        self.statusBar().showMessage("Sẵn sàng")
        
        self.lbl_cursor = QLabel("Dòng 1, Cột 1")
        self.statusBar().addPermanentWidget(self.lbl_cursor)
        
        self.editor.cursorPositionChanged.connect(self._update_cursor)
    
    def _update_cursor(self):
        c = self.editor.textCursor()
        self.lbl_cursor.setText(f"Dòng {c.blockNumber() + 1}, Cột {c.columnNumber() + 1}")
    
    # ================================================================
    # FILE OPS
    # ================================================================
    def _new_file(self):
        self.editor.clear()
        self.txt_name.clear()
        self._log("New file created")
    
    def _open_file(self):
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Open", "", "All files (*)"
        )
        if not path_str:
            return
        try:
            content = Path(path_str).read_text(encoding="utf-8")
            self.editor.setPlainText(content)
            self.txt_name.setText(Path(path_str).name)
            self._log(f"Opened: {path_str}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
    
    def _save_file(self):
        name = self.txt_name.text() or "untitled.txt"
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Save", name, "All files (*)"
        )
        if not path_str:
            return
        try:
            Path(path_str).write_text(self.editor.toPlainText(), encoding="utf-8")
            self._log(f"Saved: {path_str}")
            self.statusBar().showMessage(f"Đã lưu: {path_str}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
    
    # ================================================================
    # LAYOUT
    # ================================================================
    def _reset_layout(self):
        reply = QMessageBox.question(
            self, "Reset Layout",
            "Khôi phục layout mặc định?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Hiện tất cả dock
        for dock in (self.dock_explorer, self.dock_outline,
                     self.dock_props, self.dock_term):
            dock.show()
        
        # Reset kích thước
        self.resizeDocks(
            [self.dock_explorer, self.dock_props],
            [250, 250],
            Qt.Orientation.Horizontal
        )
        self.resizeDocks(
            [self.dock_term],
            [200],
            Qt.Orientation.Vertical
        )
        
        # Tabify lại
        self.tabifyDockWidget(self.dock_explorer, self.dock_outline)
        self.dock_explorer.raise_()
        
        self._log("Layout reset")
    
    def _restore_layout(self):
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("window/state")
        if state:
            restored = self.restoreState(state)
            if restored:
                self._log("Layout restored from settings")
    
    def _save_layout(self):
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
    
    # ================================================================
    # FULLSCREEN
    # ================================================================
    def _toggle_fullscreen(self, checked: bool):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    # ================================================================
    # DEMO FILES
    # ================================================================
    def _load_demo_files(self):
        root = QTreeWidgetItem(self.tree, ["src", ""])
        root.setExpanded(True)
        
        files = [
            ("main.py", "2.5 KB"),
            ("utils.py", "1.2 KB"),
            ("models.py", "3.8 KB"),
            ("config.json", "0.5 KB"),
        ]
        for name, size in files:
            item = QTreeWidgetItem(root, [name, size])
            item.setData(0, Qt.ItemDataRole.UserRole, name)
        
        root2 = QTreeWidgetItem(self.tree, ["tests", ""])
        QTreeWidgetItem(root2, ["test_main.py", "1.8 KB"])
        QTreeWidgetItem(root2, ["test_utils.py", "0.9 KB"])
        root2.setExpanded(True)
    
    def _on_file_double_click(self, item: QTreeWidgetItem, col: int):
        name = item.data(0, Qt.ItemDataRole.UserRole)
        if name:
            self.txt_name.setText(name)
            self._log(f"Opened: {name}")
            self.statusBar().showMessage(f"Đã mở: {name}", 2000)
    
    # ================================================================
    # LOG
    # ================================================================
    def _log(self, message: str):
        self.terminal.append(f"$ {message}")
    
    # ================================================================
    # CLOSE
    # ================================================================
    def closeEvent(self, event):
        self._save_layout()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("MyCompany")
    app.setApplicationName("IdeMini")
    
    w = IdeMini()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 4.3. Điểm đáng chú ý

1. **`setObjectName` cho mỗi dock**: BẮT BUỘC để `saveState`/`restoreState` hoạt động
2. **`setAllowedAreas`**: giới hạn vùng dock có thể đến
3. **`tabifyDockWidget`**: Explorer + Outline chung 1 vùng dạng tab
4. **`setCorner`**: điều chỉnh góc giữa 2 vùng
5. **`toggleViewAction()`**: auto-checkable action cho menu View
6. **`resizeDocks`**: reset kích thước dock theo pixel
7. **`restoreState` / `saveState`**: lưu/khôi phục layout
8. **`restoreGeometry` / `saveGeometry`**: lưu vị trí + kích thước cửa sổ
9. **`QSettings("MyCompany", "IdeMini")`**: namespace rõ ràng
10. **`raise_()`**: đưa dock lên trước khi tabify

### 4.4. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| Move dock | Kéo File Explorer sang phải | Dock di chuyển |
| Float dock | Double click title bar | Tách ra cửa sổ riêng |
| Tabify | Click tab Outline | Chuyển giữa Explorer/Outline |
| Toggle | Menu View → bỏ tick Properties | Dock ẩn |
| Reset layout | Toolbar → Reset | Về layout mặc định |
| Save layout | Đóng app | Layout lưu |
| Restore layout | Mở lại app | Layout khôi phục |
| Fullscreen | F11 | Toàn màn hình |
| Double click tree | Double click main.py | Hiện tên trong Properties |

---

## 🎯 PHẦN 5: BEST PRACTICES

### 5.1. Luôn đặt `objectName`

```python
dock.setObjectName("unique_dock_name")        # BẮT BUỘC
```

### 5.2. Đặt `objectName` cho toolbar

Nếu toolbar có `saveState`, cũng cần `objectName`:

```python
toolbar.setObjectName("main_toolbar")
```

### 5.3. Giới hạn `allowedAreas` khi cần

Dock phải ở Left/Right (không xuống Bottom):

```python
dock.setAllowedAreas(
    Qt.DockWidgetArea.LeftDockWidgetArea |
    Qt.DockWidgetArea.RightDockWidgetArea
)
```

### 5.4. Không dùng dock cho nội dung chính

Dock chỉ nên chứa **auxiliary** (panel phụ). Nội dung chính dùng `setCentralWidget`.

### 5.5. Set kích thước ban đầu hợp lý

```python
self.resizeDocks([dock], [250], Qt.Orientation.Horizontal)
```

### 5.6. Xử lý dock với widget nặng

Nếu dock content nặng → lazy load khi `visibilityChanged(True)`:

```python
def on_visibility(self, visible: bool):
    if visible and not self._initialized:
        self._populate()
        self._initialized = True

dock.visibilityChanged.connect(on_visibility)
```

### 5.7. QToolBox cho sidebar đơn giản

Nếu không cần float/move → dùng QToolBox cho gọn.

### 5.8. Tránh tạo dock trong `closeEvent`

Tạo dock trong `__init__` **trước** khi restore state.

---

## 📝 BÀI TẬP

### Bài tập 4.3.1 (Cơ bản)
Tạo app có **2 dock widget**: "Nội dung" (TextEdit) và "Lịch sử" (ListWidget). Menu View cho phép ẩn/hiện. Lưu layout khi đóng.

### Bài tập 4.3.2 (Trung bình)
Làm **image viewer** với 3 dock:
- Left: danh sách ảnh (List)
- Center: ảnh lớn
- Bottom: thông tin EXIF

Cho phép user di chuyển dock, lưu layout.

### Bài tập 4.3.3 (Khá)
**QToolBox** làm panel cài đặt:
- Mục 1: Tài khoản (avatar + tên + email)
- Mục 2: Giao diện (theme, font size)
- Mục 3: Thông báo (checkboxes)
- Mục 4: Bảo mật (đổi mật khẩu)

Mỗi mục có form đầy đủ.

### Bài tập 4.3.4 (Nâng cao)
**Multi-monitor dock**:
- Cho phép float dock ra
- Khi float, dock vẫn giữ kết nối với main window (signals, data)
- Double click title → float/unfloat
- Nút Close trên dock → ẩn (không xóa)

💡 Gợi ý: override `topLevelChanged`, `closeEvent` của dock.

### Bài tập 4.3.5 (Khó)
**Workspace presets** cho IDE:
- Preset "Editing": Explorer + Editor + Outline
- Preset "Debugging": Terminal + Variables + Watch
- Preset "Review": File diff + Comments
- Menu chọn preset → `restoreState` từ state đã lưu
- Lưu 3 preset trong QSettings

💡 Gợi ý: mỗi preset là 1 `saveState()` lưu riêng. Apply = `restoreState(preset_state)`.

---

## ✅ CHECKLIST SAU BÀI 4.3

- [ ] Hiểu `QDockWidget` – panel có thể dock vào MainWindow
- [ ] Biết 4 vùng: Left, Right, Top, Bottom
- [ ] Biết `setWidget`, `setAllowedAreas`, `setFeatures`
- [ ] Biết `setFloating`, `isFloating`
- [ ] Biết `tabifyDockWidget` – gộp 2 dock thành tab
- [ ] Biết `splitDockWidget` – chia 2 dock
- [ ] Biết `setCorner` – điều chỉnh góc
- [ ] Biết `toggleViewAction()` cho menu View
- [ ] Hiểu tầm quan trọng của **`setObjectName`**
- [ ] Biết `saveState` / `restoreState` layout
- [ ] Biết `saveGeometry` / `restoreGeometry` cửa sổ
- [ ] Thành thạo `QToolBox` – accordion
- [ ] Biết khi nào dùng ToolBox vs Dock vs Tab
- [ ] Hoàn thành IDE Mini + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 4.4 – QScrollArea, QProgressBar, QStatusBar nâng cao**

- `QScrollArea` chi tiết: content, viewport, scrollbar policy
- Custom scrollbar
- `QProgressBar`: value, format, orientation
- Indeterminate progress (busy)
- `QStatusBar`: 3 vùng (message, normal widgets, permanent widgets)
- Custom status bar widgets
- Build **download manager** demo

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 4.4 – QScrollArea, QProgressBar, QStatusBar nâng cao**?
2. **Giải chi tiết một bài tập 4.3.x** nào?
3. **Đào sâu** phần nào (custom title bar dock, multi-monitor, workspace presets)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀