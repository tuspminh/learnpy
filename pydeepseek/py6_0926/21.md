# 📘 MODULE 2 – BÀI 2.1: QWIDGET vs QMAINWINDOW

> **Mục tiêu bài học**:
> - Hiểu rõ bản chất `QWidget` và `QMainWindow`
> - Phân biệt khi nào dùng cái nào
> - Nắm cấu trúc 5 vùng của `QMainWindow` (central widget, menu bar, toolbar, status bar, dock widgets)
> - Xây dựng được app "Notepad mini" bước đầu
> - Hiểu về **QAction** – khái niệm quan trọng xuyên suốt

---

## 🎯 PHẦN 1: NHẮC LẠI VỀ QWIDGET

### 1.1. QWidget là gì?

`QWidget` là **class cơ sở của mọi thành phần giao diện** trong Qt. Mọi thứ bạn thấy trên màn hình (nút, ô nhập, cửa sổ, label...) đều kế thừa từ `QWidget`.

```
QObject
   └── QPaintDevice
         └── QWidget  ← Base của mọi UI component
               ├── QLabel
               ├── QPushButton
               ├── QLineEdit
               ├── QMainWindow   ← Đặc biệt: có cấu trúc riêng
               ├── QDialog       ← Đặc biệt: có hành vi riêng
               └── ...
```

### 1.2. QWidget có thể là gì?

`QWidget` có **hai vai trò**:

| Vai trò | Đặc điểm | Ví dụ |
|---------|----------|-------|
| **Top-level widget** | Không có parent → là cửa sổ độc lập | `QWidget()` không truyền parent |
| **Child widget** | Có parent → là thành phần con | `QLabel(parent=window)` |

### 1.3. Ví dụ QWidget làm cửa sổ

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QWidget Window")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Đây là QWidget thuần"))
        layout.addWidget(QLabel("Không có menu, toolbar, status bar"))

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

👉 **Đặc điểm QWidget làm cửa sổ**:
- ✅ Nhẹ, đơn giản
- ✅ Linh hoạt, bạn tự do bố trí
- ❌ Không có sẵn menu bar / toolbar / status bar
- ❌ Không có dock widget
- ❌ Phải tự làm mọi thứ nếu muốn các thành phần đó

---

## 🎯 PHẦN 2: QMAINWINDOW – "CỬA SỔ CHUẨN" CỦA ỨNG DỤNG

### 2.1. QMainWindow là gì?

`QMainWindow` là class chuyên biệt cho **cửa sổ chính của ứng dụng** (main window). Nó có sẵn cấu trúc layout phức tạp mà bạn không cần tự dựng.

### 2.2. Cấu trúc 5 vùng của QMainWindow

```
┌─────────────────────────────────────────────────┐
│                  Menu Bar                       │  ← QMenuBar
├─────────────────────────────────────────────────┤
│                  Tool Bar                       │  ← QToolBar (có thể có nhiều)
├──────────┬───────────────────────────┬──────────┤
│          │                           │          │
│  Dock    │     Central Widget        │   Dock   │  ← QDockWidget (trái/phải)
│  (trái)  │    (BẮT BUỘC PHẢI CÓ)     │  (phải)  │
│          │                           │          │
├──────────┴───────────────────────────┴──────────┤
│                  Status Bar                     │  ← QStatusBar
└─────────────────────────────────────────────────┘
                        ↑
                   Dock (dưới)
```

**Bảng tóm tắt các vùng**:

| Vùng | Class | Bắt buộc? | Số lượng | Method set |
|------|-------|-----------|----------|-----------|
| **Central Widget** | Bất kỳ QWidget nào | ✅ **Có** | 1 | `setCentralWidget()` |
| **Menu Bar** | `QMenuBar` | ❌ | 1 | `menuBar()` (tự tạo) |
| **Tool Bar** | `QToolBar` | ❌ | Nhiều | `addToolBar()` |
| **Status Bar** | `QStatusBar` | ❌ | 1 | `statusBar()` (tự tạo) |
| **Dock Widget** | `QDockWidget` | ❌ | Nhiều | `addDockWidget()` |

⚠️ **Lưu ý quan trọng**: `QMainWindow` **BẮT BUỘC** phải có central widget, nếu không sẽ hiển thị trống/không đúng.

### 2.3. Ví dụ QMainWindow đầy đủ 5 vùng

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit,
    QDockWidget, QListWidget, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMainWindow Demo")
        self.resize(800, 600)
        
        # ========== 1. CENTRAL WIDGET ==========
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Nhập gì đó ở đây...")
        self.setCentralWidget(self.editor)
        
        # ========== 2. MENU BAR ==========
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")     # & = phím tắt Alt+F
        edit_menu = menubar.addMenu("&Edit")
        help_menu = menubar.addMenu("&Help")
        
        # ========== 3. TOOLBAR ==========
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # ========== 4. DOCK WIDGET ==========
        dock = QDockWidget("Danh sách", self)
        dock.setWidget(QListWidget())
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
        # ========== 5. STATUS BAR ==========
        self.statusBar().showMessage("Sẵn sàng")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

**Chạy thử** – bạn sẽ thấy cửa sổ có:
- Menu File/Edit/Help trên cùng
- Toolbar trống bên dưới menu
- Danh sách dock bên trái
- Ô nhập văn bản ở giữa
- Dòng "Sẵn sàng" ở dưới cùng

---

## 🎯 PHẦN 3: QACTION – KHÁI NIỆM CỐT LÕI

### 3.1. QAction là gì?

`QAction` là **đại diện trừu tượng của một hành động** trong app. Nó có thể xuất hiện ở **nhiều nơi cùng lúc**:
- Trong menu
- Trong toolbar
- Trong context menu (chuột phải)
- Với phím tắt (shortcut)

💡 **Triết lý**: "Một hành động – nhiều nơi hiển thị". Bạn tạo action **một lần**, dùng ở **nhiều chỗ**.

### 3.2. Ví dụ QAction

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QToolBar
from PySide6.QtGui import QAction, QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAction Demo")
        
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        
        # Tạo action "Open"
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)  # Ctrl+O
        open_action.setStatusTip("Mở file")
        open_action.triggered.connect(self.on_open)
        
        # Tạo action "Save"
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)  # Ctrl+S
        save_action.triggered.connect(self.on_save)
        
        # Thêm vào menu
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        
        # Thêm vào toolbar (dùng lại CÙNG action)
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        
        self.statusBar().showMessage("Sẵn sàng")
    
    def on_open(self):
        self.statusBar().showMessage("Đã bấm Open")
    
    def on_save(self):
        self.statusBar().showMessage("Đã bấm Save")

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
```

👉 **Chú ý**: `open_action` xuất hiện **cả trong menu và toolbar** nhưng chỉ tạo **một lần**. Khi bạn click ở bất kỳ đâu, `triggered` phát ra một lần.

### 3.3. Các thuộc tính hữu ích của QAction

```python
action.setText("Mở")                              # Text hiển thị
action.setIcon(QIcon("open.png"))                 # Icon
action.setShortcut("Ctrl+O")                      # Phím tắt
action.setStatusTip("Mở file văn bản")            # Gợi ý ở status bar
action.setToolTip("Mở file")                      # Tooltip
action.setCheckable(True)                         # Có thể check/uncheck
action.setChecked(False)                          # Trạng thái check
action.setEnabled(False)                          # Vô hiệu hóa
action.setVisible(False)                          # Ẩn
```

### 3.4. Signal của QAction

```python
action.triggered.connect(slot)         # Khi được kích hoạt (click, phím tắt)
action.toggled.connect(slot)           # Khi checkable thay đổi (bool)
action.changed.connect(slot)           # Khi thuộc tính thay đổi
```

---

## 🎯 PHẦN 4: STATUS BAR – TƯƠNG TÁC NGƯỜI DÙNG

### 4.1. Ba loại thông tin trên status bar

```python
self.statusBar().showMessage("Đang xử lý...")         # Message tạm thời
self.statusBar().showMessage("Xong", 3000)            # Hiện 3 giây rồi xóa

# Widget vĩnh viễn (bên phải)
label = QLabel("Ready")
self.statusBar().addPermanentWidget(label)

# Widget thường (bên trái)
progress = QProgressBar()
self.statusBar().addWidget(progress)
```

### 4.2. Ví dụ đầy đủ

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QProgressBar
)
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        sb = self.statusBar()
        
        # Message tạm thời
        sb.showMessage("Đang tải...", 2000)
        
        # Widget vĩnh viễn bên phải
        self.time_label = QLabel("00:00:00")
        sb.addPermanentWidget(self.time_label)
        
        # Widget bên trái
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        sb.addWidget(self.progress)
        
        # Timer update progress mỗi 200ms
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(200)
    
    def update_progress(self):
        self.counter = (self.counter + 5) % 100
        self.progress.setValue(self.counter)
        self.time_label.setText(f"{self.counter:02d}:00")

app = QApplication(sys.argv)
w = MainWindow()
w.resize(600, 400)
w.show()
sys.exit(app.exec())
```

---

## 🎯 PHẦN 5: KHI NÀO DÙNG QWIDGET vs QMAINWINDOW?

### 5.1. Bảng so sánh quyết định

| Tình huống | Nên dùng |
|------------|----------|
| App chính có menu, toolbar, status bar | ✅ `QMainWindow` |
| App kiểu IDE, editor, dashboard | ✅ `QMainWindow` |
| App cần dock panel (như Photoshop) | ✅ `QMainWindow` |
| Dialog nhỏ, popup | ✅ `QDialog` |
| Cửa sổ đơn giản, không cần menu/toolbar | ✅ `QWidget` |
| Custom widget nhúng trong widget khác | ✅ `QWidget` |
| Splash screen, welcome window | ✅ `QWidget` |

### 5.2. Quy tắc thực tế

> **Nguyên tắc 80/20**: 80% app thực tế dùng `QMainWindow` làm cửa sổ chính, và chỉ **một** QMainWindow trong toàn app.

### 5.3. Cấu trúc project chuẩn

```
myapp/
├── main.py                    ← Khởi động app
├── main_window.py             ← Class MainWindow(QMainWindow)
├── widgets/                   ← Custom widgets
│   ├── editor.py              ← Editor widget (QWidget)
│   └── sidebar.py             ← Sidebar widget (QWidget)
├── dialogs/                   ← Dialog classes
│   ├── about.py               ← AboutDialog(QDialog)
│   └── settings.py            ← SettingsDialog(QDialog)
└── resources/
```

---

## 🎯 PHẦN 6: THỰC HÀNH – APP "NOTEPAD MINI"

Chúng ta sẽ build một app notepad đơn giản nhưng có cấu trúc chuyên nghiệp.

### 6.1. Yêu cầu

- `QMainWindow` với QTextEdit làm central widget
- Menu: **File** (New, Open, Save, Exit), **Edit** (Undo, Redo, Cut, Copy, Paste), **Help** (About)
- Toolbar có: New, Open, Save
- Status bar hiển thị: dòng/cột con trỏ, thông báo tạm thời
- Phím tắt: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Q, Ctrl+Z/Y, Ctrl+C/V/X
- Title cập nhật khi mở file

### 6.2. Code đầy đủ

Tạo file `notepad_mini.py`:

```python
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QToolBar,
    QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtCore import Qt


class NotepadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notepad Mini")
        self.resize(800, 600)
        
        # Trạng thái
        self.current_file: Path | None = None
        self.is_modified = False
        
        # ===== Central widget =====
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Bắt đầu gõ...")
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._update_cursor_status)
        self.setCentralWidget(self.editor)
        
        # ===== Actions =====
        self._create_actions()
        
        # ===== Menu =====
        self._create_menus()
        
        # ===== Toolbar =====
        self._create_toolbar()
        
        # ===== Status bar =====
        self._create_status_bar()
    
    # ----------------------------------------------------------------
    # TẠO ACTIONS
    # ----------------------------------------------------------------
    def _create_actions(self):
        # File
        self.act_new = QAction("&New", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.setStatusTip("Tạo file mới")
        self.act_new.triggered.connect(self.file_new)
        
        self.act_open = QAction("&Open...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.setStatusTip("Mở file")
        self.act_open.triggered.connect(self.file_open)
        
        self.act_save = QAction("&Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.setStatusTip("Lưu file")
        self.act_save.triggered.connect(self.file_save)
        
        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.file_save_as)
        
        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # Edit
        self.act_undo = QAction("&Undo", self)
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(self.editor.undo)
        
        self.act_redo = QAction("&Redo", self)
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_redo.triggered.connect(self.editor.redo)
        
        self.act_cut = QAction("Cu&t", self)
        self.act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.act_cut.triggered.connect(self.editor.cut)
        
        self.act_copy = QAction("&Copy", self)
        self.act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.act_copy.triggered.connect(self.editor.copy)
        
        self.act_paste = QAction("&Paste", self)
        self.act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.act_paste.triggered.connect(self.editor.paste)
        
        # Help
        self.act_about = QAction("&About", self)
        self.act_about.triggered.connect(self.show_about)
    
    # ----------------------------------------------------------------
    # TẠO MENU
    # ----------------------------------------------------------------
    def _create_menus(self):
        menubar = self.menuBar()
        
        # File
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.act_new)
        file_menu.addAction(self.act_open)
        file_menu.addSeparator()
        file_menu.addAction(self.act_save)
        file_menu.addAction(self.act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)
        
        # Edit
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.act_undo)
        edit_menu.addAction(self.act_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.act_cut)
        edit_menu.addAction(self.act_copy)
        edit_menu.addAction(self.act_paste)
        
        # Help
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.act_about)
    
    # ----------------------------------------------------------------
    # TẠO TOOLBAR
    # ----------------------------------------------------------------
    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.act_new)
        toolbar.addAction(self.act_open)
        toolbar.addAction(self.act_save)
        toolbar.addSeparator()
        toolbar.addAction(self.act_undo)
        toolbar.addAction(self.act_redo)
    
    # ----------------------------------------------------------------
    # TẠO STATUS BAR
    # ----------------------------------------------------------------
    def _create_status_bar(self):
        sb = self.statusBar()
        sb.showMessage("Sẵn sàng")
        
        # Widget vĩnh viễn hiển thị dòng/cột
        from PySide6.QtWidgets import QLabel
        self.cursor_label = QLabel("Dòng 1, Cột 1")
        sb.addPermanentWidget(self.cursor_label)
    
    # ----------------------------------------------------------------
    # XỬ LÝ FILE
    # ----------------------------------------------------------------
    def file_new(self):
        if not self._maybe_save():
            return
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self._update_title()
        self.statusBar().showMessage("Đã tạo file mới", 2000)
    
    def file_open(self):
        if not self._maybe_save():
            return
        
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Mở file", "", "Text files (*.txt);;All files (*)"
        )
        if not path_str:
            return
        
        try:
            path = Path(path_str)
            self.editor.setPlainText(path.read_text(encoding="utf-8"))
            self.current_file = path
            self.is_modified = False
            self._update_title()
            self.statusBar().showMessage(f"Đã mở: {path.name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không mở được file:\n{e}")
    
    def file_save(self):
        if self.current_file is None:
            return self.file_save_as()
        self._write_file(self.current_file)
    
    def file_save_as(self):
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Lưu file", "", "Text files (*.txt);;All files (*)"
        )
        if not path_str:
            return
        self._write_file(Path(path_str))
    
    def _write_file(self, path: Path):
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.current_file = path
            self.is_modified = False
            self._update_title()
            self.statusBar().showMessage(f"Đã lưu: {path.name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không lưu được file:\n{e}")
    
    # ----------------------------------------------------------------
    # XỬ LÝ TRẠNG THÁI
    # ----------------------------------------------------------------
    def _on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self._update_title()
    
    def _update_title(self):
        name = self.current_file.name if self.current_file else "Untitled"
        mark = " *" if self.is_modified else ""
        self.setWindowTitle(f"{name}{mark} - Notepad Mini")
    
    def _update_cursor_status(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Dòng {line}, Cột {col}")
    
    def _maybe_save(self) -> bool:
        """Hỏi lưu nếu có thay đổi. Trả về True nếu được phép tiếp tục."""
        if not self.is_modified:
            return True
        
        reply = QMessageBox.question(
            self, "Chưa lưu",
            "Nội dung đã thay đổi. Bạn có muốn lưu không?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self.file_save()
            return not self.is_modified  # False nếu user cancel trong Save As
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
    
    # ----------------------------------------------------------------
    # ABOUT
    # ----------------------------------------------------------------
    def show_about(self):
        QMessageBox.about(
            self, "About Notepad Mini",
            "Notepad Mini v1.0\n\nĐược xây dựng với PySide6.\n© 2025"
        )
    
    # ----------------------------------------------------------------
    # ĐÓNG CỬA SỔ
    # ----------------------------------------------------------------
    def closeEvent(self, event):
        if self._maybe_save():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Notepad Mini")
    
    window = NotepadWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 6.3. Điểm đáng chú ý trong code

1. **Tách hàm `_create_actions` / `_create_menus` / `_create_toolbar`**: code gọn, dễ maintain.
2. **`QKeySequence.StandardKey.*`**: dùng hằng số chuẩn, không hard-code "Ctrl+O". Qt tự map trên Mac thành Cmd+O.
3. **QAction tái sử dụng**: `act_new` xuất hiện cả menu và toolbar.
4. **`_maybe_save()`**: pattern quan trọng – **luôn hỏi trước khi mất dữ liệu**.
5. **`closeEvent`**: override để chặn đóng khi user Cancel.
6. **`is_modified` flag**: đánh dấu có thay đổi chưa lưu → dấu `*` trên title.
7. **Type hint `Path | None`**: cần Python 3.10+.

---

## 📝 BÀI TẬP

### Bài tập 2.1.1 (Cơ bản)
Mở rộng Notepad Mini: thêm menu **Format** với 2 action:
- **Word Wrap** (checkable) → toggle word wrap của editor
- **Font...** → mở `QFontDialog` để đổi font chữ cho editor

💡 Gợi ý:
```python
self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
font, ok = QFontDialog.getFont(self.editor.font(), self)
if ok:
    self.editor.setFont(font)
```

### Bài tập 2.1.2 (Trung bình)
Thêm **dock widget** bên phải hiển thị **danh sách các dòng** (outline) của file hiện tại. Mỗi dòng trên 50 ký tự thì hiển thị. Click vào item → nhảy con trỏ tới dòng đó.

💡 Gợi ý: `QListWidget` + `self.editor.setTextCursor(...)`.

### Bài tập 2.1.3 (Khá)
Lưu **vị trí và kích thước cửa sổ** mỗi lần đóng, và **khôi phục** khi mở lại. Dùng `QSettings`.

💡 Gợi ý:
```python
from PySide6.QtCore import QSettings

settings = QSettings("MyCompany", "NotepadMini")
# Lưu
settings.setValue("geometry", self.saveGeometry())
# Khôi phục
self.restoreGeometry(settings.value("geometry"))
```

### Bài tập 2.1.4 (Nâng cao)
Thêm **tab editor** thay vì chỉ 1 editor. Dùng `QTabWidget` làm central widget. Mỗi tab là 1 file, có nút X để đóng.

💡 Gợi ý:
```python
self.tabs = QTabWidget()
self.tabs.setTabsClosable(True)
self.tabs.setMovable(True)
self.setCentralWidget(self.tabs)
```

---

## ✅ CHECKLIST SAU BÀI 2.1

- [ ] Hiểu 3 vai trò của `QWidget`: base class, top-level, child
- [ ] Biết cấu trúc 5 vùng của `QMainWindow`
- [ ] Phân biệt rõ `QWidget` vs `QMainWindow` – khi nào dùng cái nào
- [ ] Hiểu và dùng thành thạo `QAction` (tái sử dụng)
- [ ] Biết tạo menu, toolbar, status bar
- [ ] Biết dùng `QKeySequence.StandardKey.*`
- [ ] Hiểu pattern `_maybe_save()` – hỏi trước khi mất dữ liệu
- [ ] Override được `closeEvent`
- [ ] Hoàn thành Notepad Mini và ít nhất 2 bài tập mở rộng

---

## 🔜 BÀI TIẾP THEO

**Bài 2.2 – Các widget nhập liệu: QPushButton, QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, QSpinBox, QSlider**

Chúng ta sẽ:
- Đi qua từng widget nhập liệu phổ biến
- Signal đặc trưng của mỗi widget
- Build app "Form đăng ký" hoàn chỉnh với validation

---

👉 Bạn muốn tôi:
1. **Soạn tiếp Bài 2.2**?
2. **Giải chi tiết một bài tập 2.1.x** nào đó để bạn đối chiếu?
3. **Giải thích sâu hơn** phần nào trong Bài 2.1 (ví dụ: QAction signal, dock widget, closeEvent...)?