Chào mừng bạn đến **Bài 4: QMainWindow - Xây dựng ứng dụng chuyên nghiệp**!

Chúng ta đã học về QWidget và Layouts. Hôm nay, chúng ta sẽ bước sang một cấp độ mới: **QMainWindow** - khung cửa sổ chính của mọi ứng dụng desktop chuyên nghiệp. Đây là nơi bạn sẽ thêm Menu Bar, Tool Bar, Status Bar, và các thành phần nâng cao khác.

---

## Mục tiêu bài học

Sau bài này, bạn sẽ:
1. Hiểu cấu trúc của QMainWindow và các thành phần của nó
2. Tạo và sử dụng Menu Bar, Tool Bar, Status Bar
3. Làm việc với QAction - đơn vị cơ bản của Menu và Toolbar
4. Sử dụng Dock Widgets (cửa sổ con có thể gắn/di chuyển)
5. Xây dựng ứng dụng Notepad đơn giản

---

## Phần 1: Cấu trúc của QMainWindow

### 1.1. Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar (File | Edit | View | Help)                     │  ← Menu Bar
├─────────────────────────────────────────────────────────────┤
│  [🔍] [📂] [💾] [✂️] [📋] [🖨️]                           │  ← Tool Bar
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┬──────────────────────────────────┬───────────┐ │
│ │         │                                  │           │ │
│ │ Dock    │    Central Widget                │ Dock      │ │
│ │ Widget  │    (Nội dung chính)              │ Widget    │ │
│ │ (Trái)  │                                  │ (Phải)    │ │
│ │         │                                  │           │ │
│ └─────────┴──────────────────────────────────┴───────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Status Bar (Ready | Line: 10 | Col: 5)                  │  ← Status Bar
└─────────────────────────────────────────────────────────────┘
```

### 1.2. Các thành phần chính

| Thành phần | Vai trò | Ví dụ |
|------------|---------|-------|
| **Menu Bar** | Thanh menu ở trên cùng | File, Edit, View, Help |
| **Tool Bar** | Thanh công cụ chứa các nút chức năng | Save, Open, Copy, Paste |
| **Central Widget** | Nội dung chính của ứng dụng | Editor, Table, Canvas |
| **Dock Widgets** | Cửa sổ con có thể gắn/di chuyển | File Explorer, Properties, Console |
| **Status Bar** | Thanh trạng thái ở dưới cùng | Hiển thị thông tin, progress |

### 1.3. So sánh QWidget vs QMainWindow

```python
# QWidget - Đơn giản, linh hoạt
class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()
        # Chỉ có central content, tự quản lý layout


# QMainWindow - Chuyên nghiệp, có cấu trúc sẵn
class ProfessionalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Có sẵn menu bar, tool bar, status bar
        # Phải set central widget
```

---

## Phần 2: Tạo QMainWindow cơ bản

### 2.1. Ứng dụng đầu tiên với QMainWindow

```python
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Qt


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng QMainWindow đầu tiên")
        self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)

        # === TẠO CENTRAL WIDGET ===
        # BẮT BUỘC: Mỗi QMainWindow phải có central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Thêm nội dung vào central widget
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Đây là nội dung chính của ứng dụng"))
        layout.addWidget(QPushButton("Nút bấm"))
        central_widget.setLayout(layout)

        # === TẠO MENU BAR ===
        self.create_menu_bar()

        # === TẠO STATUS BAR ===
        self.create_status_bar()

    def create_menu_bar(self):
        """Tạo Menu Bar"""
        # Lấy menu bar của cửa sổ
        menubar = self.menuBar()

        # Tạo menu
        file_menu = menubar.addMenu("&File")  # Alt+F
        edit_menu = menubar.addMenu("&Edit")  # Alt+E
        help_menu = menubar.addMenu("&Help")  # Alt+H

        # Thêm các action vào menu
        # Sẽ học chi tiết ở phần sau

    def create_status_bar(self):
        """Tạo Status Bar"""
        self.statusBar().showMessage("Sẵn sàng")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
```

---

## Phần 3: QAction - Đơn vị cơ bản

### 3.1. Giới thiệu về QAction

`QAction` là đơn vị cơ bản của Menu và Toolbar. Một QAction đại diện cho một hành động (ví dụ: "Mở file", "Lưu file", "Copy", "Paste").

**Tính năng của QAction:**
- Có thể có icon, text, shortcut
- Có thể được kích hoạt từ Menu, Toolbar, hoặc phím tắt
- Có thể được bật/tắt (enabled/disabled)
- Có thể được check/uncheck (cho các tùy chọn)

### 3.2. Tạo QAction

```python
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtCore import Qt


class ActionExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAction Example")
        self.setGeometry(100, 100, 600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        self.label = QLabel("Chưa có hành động nào")
        layout.addWidget(self.label)
        central.setLayout(layout)

        # Tạo Menu và Action
        self.create_actions()

    def create_actions(self):
        """Tạo các Action và thêm vào Menu"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # === Cách 1: Tạo QAction trực tiếp ===
        # Tạo action mới
        new_action = QAction("&Mới", self)
        new_action.setShortcut(QKeySequence.New)  # Ctrl+N
        new_action.setStatusTip("Tạo file mới")
        new_action.triggered.connect(self.on_new_file)  # Kết nối signal
        file_menu.addAction(new_action)

        # === Cách 2: Sử dụng QAction với Icon ===
        open_action = QAction("&Mở...", self)
        open_action.setShortcut(QKeySequence.Open)  # Ctrl+O
        # open_action.setIcon(QIcon("open.png"))  # Có thể thêm icon
        open_action.setStatusTip("Mở file có sẵn")
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)

        # === Separator (đường phân cách) ===
        file_menu.addSeparator()

        # === Action với Checkable ===
        save_action = QAction("&Lưu", self)
        save_action.setShortcut(QKeySequence.Save)  # Ctrl+S
        save_action.setStatusTip("Lưu file")
        save_action.triggered.connect(self.on_save_file)
        file_menu.addAction(save_action)

        # === Action có thể check (toggle) ===
        auto_save_action = QAction("Tự động lưu", self)
        auto_save_action.setCheckable(True)
        auto_save_action.setChecked(False)
        auto_save_action.triggered.connect(self.on_auto_save_toggle)
        file_menu.addAction(auto_save_action)

        file_menu.addSeparator()

        # === Action với icon và shortcut ===
        exit_action = QAction("&Thoát", self)
        exit_action.setShortcut(QKeySequence.Quit)  # Ctrl+Q
        # exit_action.setIcon(QIcon("exit.png"))
        exit_action.setStatusTip("Thoát ứng dụng")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # === Tạo Edit Menu ===
        edit_menu = menubar.addMenu("&Edit")

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)  # Ctrl+C
        copy_action.triggered.connect(self.on_copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)  # Ctrl+V
        paste_action.triggered.connect(self.on_paste)
        edit_menu.addAction(paste_action)

        # === Help Menu ===
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    # === Các Slot cho Action ===
    def on_new_file(self):
        self.label.setText("Tạo file mới!")
        print("New file created")

    def on_open_file(self):
        self.label.setText("Mở file!")
        print("File opened")

    def on_save_file(self):
        self.label.setText("Lưu file!")
        print("File saved")

    def on_auto_save_toggle(self, checked):
        if checked:
            self.label.setText("Bật tự động lưu")
            print("Auto-save enabled")
        else:
            self.label.setText("Tắt tự động lưu")
            print("Auto-save disabled")

    def on_copy(self):
        self.label.setText("Copy!")
        print("Copied")

    def on_paste(self):
        self.label.setText("Paste!")
        print("Pasted")

    def on_about(self):
        self.label.setText("About - Ứng dụng ví dụ")
        print("About dialog")
```

---

## Phần 4: Tool Bar

### 4.1. Tạo Tool Bar cơ bản

```python
class ToolBarExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Bar Example")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        self.label = QLabel("Sử dụng các công cụ trên Toolbar")
        layout.addWidget(self.label)
        central.setLayout(layout)
        
        # Tạo Action và Toolbar
        self.create_toolbar()
    
    def create_toolbar(self):
        """Tạo Toolbar"""
        # Tạo toolbar
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)  # Không cho di chuyển
        toolbar.setFloatable(False)  # Không cho thả nổi
        
        # Tạo các action
        new_action = QAction("Mới", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.label.setText("Mới"))
        
        open_action = QAction("Mở", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(lambda: self.label.setText("Mở"))
        
        save_action = QAction("Lưu", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.label.setText("Lưu"))
        
        copy_action = QAction("Sao chép", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.label.setText("Sao chép"))
        
        paste_action = QAction("Dán", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.label.setText("Dán"))
        
        # Thêm action vào toolbar
        toolbar.addAction(new_action)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()  # Đường phân cách
        toolbar.addAction(copy_action)
        toolbar.addAction(paste_action)
        
        # === Thêm Widget vào Toolbar ===
        # Thêm QLabel
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("  Tìm kiếm: "))
        
        # Thêm QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa...")
        self.search_input.setMaximumWidth(150)
        toolbar.addWidget(self.search_input)
        
        # Thêm QPushButton
        search_btn = QPushButton("🔍")
        search_btn.setMaximumWidth(40)
        search_btn.clicked.connect(self.on_search)
        toolbar.addWidget(search_btn)
    
    def on_search(self):
        text = self.search_input.text()
        if text:
            self.label.setText(f"Tìm kiếm: {text}")
        else:
            self.label.setText("Vui lòng nhập từ khóa")
```

### 4.2. Tool Bar với nhiều vị trí

```python
class MultipleToolbars(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple Toolbars")

        # Tạo nhiều toolbar với vị trí khác nhau
        toolbar1 = self.addToolBar("Toolbar 1")
        toolbar2 = self.addToolBar("Toolbar 2")

        # Vị trí: Top, Bottom, Left, Right
        self.addToolBarBreak()  # Xuống dòng

        toolbar3 = QToolBar("Toolbar 3")
        self.addToolBar(Qt.LeftToolBarArea, toolbar3)

        toolbar4 = QToolBar("Toolbar 4")
        self.addToolBar(Qt.RightToolBarArea, toolbar4)

        # Thêm action vào các toolbar
        for i, tb in enumerate([toolbar1, toolbar2, toolbar3, toolbar4]):
            action = QAction(f"Action {i + 1}", self)
            tb.addAction(action)
```

---

## Phần 5: Status Bar

### 5.1. Sử dụng Status Bar cơ bản

```python
class StatusBarExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Status Bar Example")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        self.button = QPushButton("Cập nhật trạng thái")
        self.button.clicked.connect(self.update_status)
        layout.addWidget(self.button)
        central.setLayout(layout)
        
        # Tạo Status Bar
        self.create_status_bar()
    
    def create_status_bar(self):
        """Tạo Status Bar với nhiều thành phần"""
        status_bar = self.statusBar()
        
        # 1. Hiển thị message tạm thời (mặc định)
        status_bar.showMessage("Sẵn sàng", 3000)  # 3000ms = 3 giây
        
        # 2. Thêm widget vào Status Bar
        # Tạo label bên trái
        self.left_label = QLabel("Left Status")
        status_bar.addWidget(self.left_label)
        
        # Tạo label bên phải
        self.right_label = QLabel("Right Status")
        status_bar.addPermanentWidget(self.right_label)
        
        # 3. Thêm Progress Bar
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(150)
        self.progress.setValue(0)
        status_bar.addPermanentWidget(self.progress)
    
    def update_status(self):
        """Cập nhật status khi click button"""
        import random
        
        # Cập nhật message tạm thời
        messages = ["Đang xử lý...", "Hoàn thành!", "Lỗi xảy ra", "Đang tải..."]
        self.statusBar().showMessage(random.choice(messages), 2000)
        
        # Cập nhật các label
        self.left_label.setText(f"Click: {random.randint(1, 100)}")
        self.right_label.setText(f"Time: {random.randint(10, 60)}s")
        
        # Cập nhật progress
        value = self.progress.value() + random.randint(1, 10)
        if value > 100:
            value = 0
        self.progress.setValue(value)
```

---

## Phần 6: Dock Widgets

### 6.1. Giới thiệu và sử dụng cơ bản

Dock Widgets là các cửa sổ con có thể:
- Di chuyển và gắn vào các cạnh của cửa sổ chính
- Thả nổi thành cửa sổ độc lập
- Đóng/mở được
- Có thể xếp chồng lên nhau

```python
from PySide6.QtWidgets import QDockWidget, QTextEdit, QListWidget


class DockExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dock Widgets Example")
        self.setGeometry(100, 100, 800, 600)

        # === CENTRAL WIDGET ===
        self.editor = QTextEdit()
        self.editor.setPlainText("Đây là editor chính...")
        self.setCentralWidget(self.editor)

        # === DOCK WIDGET 1: File Explorer ===
        self.create_file_explorer()

        # === DOCK WIDGET 2: Properties ===
        self.create_properties()

        # === DOCK WIDGET 3: Console ===
        self.create_console()

    def create_file_explorer(self):
        """Tạo Dock Widget cho File Explorer"""
        dock = QDockWidget("File Explorer", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Nội dung của dock
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Danh sách file:"))

        list_widget = QListWidget()
        for item in ["main.py", "config.json", "data.csv", "image.png"]:
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        widget.setLayout(layout)
        dock.setWidget(widget)

        # Thêm dock vào cửa sổ chính
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def create_properties(self):
        """Tạo Dock Widget cho Properties"""
        dock = QDockWidget("Properties", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)

        # Nội dung
        widget = QWidget()
        layout = QFormLayout()
        layout.addRow("File:", QLabel("main.py"))
        layout.addRow("Size:", QLabel("2.4 KB"))
        layout.addRow("Modified:", QLabel("2024-01-15"))
        widget.setLayout(layout)
        dock.setWidget(widget)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def create_console(self):
        """Tạo Dock Widget cho Console"""
        dock = QDockWidget("Console", self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)

        # Nội dung
        console = QTextEdit()
        console.setPlainText("> Python 3.12\n> Ready...")
        console.setMaximumHeight(150)
        dock.setWidget(console)

        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
```

### 6.2. Tùy chỉnh Dock Widget

```python
# Tùy chỉnh dock
dock = QDockWidget("Title", self)
dock.setFeatures(
    QDockWidget.DockWidgetClosable  # Có nút đóng
    | QDockWidget.DockWidgetMovable  # Có thể di chuyển
    | QDockWidget.DockWidgetFloatable  # Có thể thả nổi
    | QDockWidget.DockWidgetVerticalTitleBar  # Title bar dọc
)

# Tắt một số tính năng
dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

# Đặt vị trí mặc định
self.addDockWidget(Qt.LeftDockWidgetArea, dock)
self.splitDockWidget(dock, another_dock, Qt.Vertical)  # Chia dock
self.tabifyDockWidget(dock1, dock2)  # Tab hóa các dock
```

---

## Phần 7: Ứng dụng thực tế - Notepad đơn giản

Kết hợp tất cả kiến thức để tạo một Notepad đơn giản:

```python
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QAction, QKeySequence, QIcon, QFont


class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyNote - Notepad đơn giản")
        self.setGeometry(100, 100, 800, 600)
        self.current_file = None

        # === CENTRAL WIDGET ===
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.setCentralWidget(self.editor)

        # === TẠO UI ===
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        self.create_dock_widgets()

        # Kết nối signal
        self.editor.textChanged.connect(self.on_text_changed)

    def create_menu_bar(self):
        """Tạo Menu Bar"""
        menubar = self.menuBar()

        # === File Menu ===
        file_menu = menubar.addMenu("&File")

        # New
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Create a new file")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Save current file")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Save file as...")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # === Edit Menu ===
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)

        # === Help Menu ===
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Tạo Toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # Tạo các action với icon (sử dụng icon từ hệ thống)
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Thêm các nút edit
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.editor.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.editor.redo)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        # Thêm font size combobox
        toolbar.addWidget(QLabel(" Font: "))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["10", "12", "14", "16", "18", "20", "24"])
        self.font_combo.setCurrentText("12")
        self.font_combo.currentTextChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_combo)

    def create_status_bar(self):
        """Tạo Status Bar"""
        status_bar = self.statusBar()

        # Thông tin file
        self.file_info_label = QLabel("No file opened")
        status_bar.addWidget(self.file_info_label)

        # Thông tin vị trí con trỏ
        self.cursor_label = QLabel("Line: 1, Col: 1")
        status_bar.addPermanentWidget(self.cursor_label)

        # Kết nối signal để cập nhật vị trí con trỏ
        self.editor.cursorPositionChanged.connect(self.update_cursor_position)

        # Message mặc định
        status_bar.showMessage("Ready", 3000)

    def create_dock_widgets(self):
        """Tạo Dock Widgets"""
        # === Document Outline ===
        dock = QDockWidget("Document Outline", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        outline_list = QListWidget()
        outline_list.addItems(["Line 1", "Line 2", "Line 3"])  # Có thể parse từ editor
        dock.setWidget(outline_list)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # === Find/Replace ===
        dock2 = QDockWidget("Find & Replace", self)
        dock2.setAllowedAreas(Qt.BottomDockWidgetArea)

        find_widget = QWidget()
        find_layout = QVBoxLayout()

        find_input = QLineEdit()
        find_input.setPlaceholderText("Find...")
        find_button = QPushButton("Find Next")

        replace_input = QLineEdit()
        replace_input.setPlaceholderText("Replace with...")
        replace_button = QPushButton("Replace All")

        find_layout.addWidget(QLabel("Find:"))
        find_layout.addWidget(find_input)
        find_layout.addWidget(find_button)
        find_layout.addWidget(QLabel("Replace:"))
        find_layout.addWidget(replace_input)
        find_layout.addWidget(replace_button)

        find_widget.setLayout(find_layout)
        dock2.setWidget(find_widget)

        self.addDockWidget(Qt.BottomDockWidgetArea, dock2)

    # === CÁC SLOT ===

    def new_file(self):
        """Tạo file mới"""
        if self.editor.document().isModified():
            if not self.confirm_save():
                return

        self.editor.clear()
        self.current_file = None
        self.update_status("New file created")

    def open_file(self):
        """Mở file"""
        if self.editor.document().isModified():
            if not self.confirm_save():
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.update_status(f"Opened: {file_path}")
                self.update_file_info()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open file: {e}")

    def save_file(self):
        """Lưu file"""
        if self.current_file is None:
            self.save_file_as()
        else:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.editor.document().setModified(False)
                self.update_status(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot save file: {e}")

    def save_file_as(self):
        """Lưu file với tên mới"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            self.current_file = file_path
            self.save_file()
            self.update_file_info()

    def confirm_save(self):
        """Xác nhận lưu trước khi đóng"""
        reply = QMessageBox.question(
            self,
            "Save Changes",
            "Do you want to save changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if reply == QMessageBox.Save:
            self.save_file()
            return True
        elif reply == QMessageBox.Discard:
            return True
        else:
            return False

    def on_text_changed(self):
        """Cập nhật status khi text thay đổi"""
        self.statusBar().showMessage("Modified", 2000)
        self.update_file_info()

    def update_cursor_position(self):
        """Cập nhật vị trí con trỏ"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Line: {line}, Col: {col}")

    def update_file_info(self):
        """Cập nhật thông tin file"""
        if self.current_file:
            import os

            size = os.path.getsize(self.current_file)
            self.file_info_label.setText(
                f"File: {os.path.basename(self.current_file)} ({size} bytes)"
            )
        else:
            self.file_info_label.setText("No file opened")

    def update_status(self, message):
        """Cập nhật status bar"""
        self.statusBar().showMessage(message, 3000)

    def change_font_size(self, size):
        """Thay đổi font size"""
        font = self.editor.font()
        font.setPointSize(int(size))
        self.editor.setFont(font)

    def show_about(self):
        """Hiển thị About dialog"""
        QMessageBox.about(
            self,
            "About PyNote",
            "PyNote - Simple Notepad Application\n\nBuilt with PySide6\nVersion 1.0",
        )

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        if self.editor.document().isModified():
            if not self.confirm_save():
                event.ignore()
                return
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Notepad()
    window.show()
    sys.exit(app.exec())
```

---

## Phần 8: Bài tập thực hành

### Bài 1: Text Editor với Syntax Highlight (Đơn giản)
Tạo một text editor với:
- Menu: File, Edit, Format, Help
- Toolbar: New, Open, Save, Copy, Paste, Undo, Redo
- Status Bar: Hiển thị số dòng, số từ
- Font size có thể thay đổi (ComboBox trên Toolbar)
- **Bonus:** Highlight các từ khóa Python (if, else, def, class)

### Bài 2: Trình quản lý file đơn giản
Tạo ứng dụng với:
- Central Widget: QTableWidget hiển thị danh sách file
- Menu: File (New Folder, Delete, Rename, Exit)
- Toolbar: Back, Forward, Up
- Dock Widget bên trái: Tree view hiển thị thư mục
- Status Bar: Hiển thị đường dẫn hiện tại

### Bài 3: Ứng dụng Paint đơn giản (chuẩn bị cho bài sau)
Tạo ứng dụng vẽ với:
- Menu: File (New, Save, Exit), Tools (Pen, Eraser, Shapes)
- Toolbar: Các công cụ vẽ, màu sắc, độ dày
- Central Widget: QWidget để vẽ (sẽ dùng QPainter)
- Dock Widget: Properties (hiển thị tọa độ, màu sắc)

---

## Phần 9: Mẹo và thủ thuật

### 1. Shortcut Keys cho Menu

```python
# Tạo shortcut với QKeySequencenew_action.setShortcut(QKeySequence.New)  # Ctrl+N

# Hoặc tự định nghĩa
new_action.setShortcut("Ctrl+Shift+N")

# Shortcut cho toàn ứng dụng
shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
shortcut.activated.connect(self.custom_shortcut_action)
```

### 2. Context Menu (Menu chuột phải)

```python
def contextMenuEvent(self, event):
    """Xử lý menu chuột phải"""
    context_menu = QMenu(self)
    
    copy_action = context_menu.addAction("Copy")
    paste_action = context_menu.addAction("Paste")
    context_menu.addSeparator()
    delete_action = context_menu.addAction("Delete")
    
    # Kết nối action
    copy_action.triggered.connect(self.on_copy)
    paste_action.triggered.connect(self.on_paste)
    
    context_menu.exec(event.globalPos())
```

### 3. Tạo Action Groups (Chọn 1 trong nhiều)

```python
# Tạo group cho các option
view_group = QActionGroup(self)
view_group.setExclusive(True)  # Chỉ chọn 1

view_normal = QAction("Normal", self, checkable=True)
view_normal.setChecked(True)
view_full = QAction("Full Screen", self, checkable=True)
view_mini = QAction("Mini", self, checkable=True)

view_group.addAction(view_normal)
view_group.addAction(view_full)
view_group.addAction(view_mini)

# Kết nối signal cho group
view_group.triggered.connect(self.on_view_mode_change)
```

### 4. Tạo Custom Title Bar (Cửa sổ không có viền)

```python
# Tạo cửa sổ không viền
self.setWindowFlags(Qt.FramelessWindowHint)

# Thêm custom title bar (QWidget) với các nút Minimize, Maximize, Close
# Sau đó kết nối các nút với window.showMinimized(), window.showMaximized(), window.close()
```

---

## Tóm tắt bài học

1. **QMainWindow** là khung chính cho ứng dụng chuyên nghiệp
2. **Central Widget** là bắt buộc - chứa nội dung chính
3. **QAction** đại diện cho một hành động, có thể dùng trong Menu và Toolbar
4. **Menu Bar** chứa các menu (File, Edit, View, Help...)
5. **Tool Bar** chứa các action và widget để truy cập nhanh
6. **Status Bar** hiển thị thông tin trạng thái
7. **Dock Widgets** là các cửa sổ con có thể di chuyển và gắn vào cửa sổ chính

---

## Kiến thức cho bài sau

Ở **Bài 5: Dialogs và giao tiếp**, chúng ta sẽ:
- Sử dụng các Dialog có sẵn (QFileDialog, QColorDialog, QFontDialog)
- Tạo Custom Dialog
- Xử lý giao tiếp giữa các cửa sổ
- Sử dụng Message Boxes

Bạn đã sẵn sàng để tạo ứng dụng với đầy đủ tính năng chuyên nghiệp chưa? 😊