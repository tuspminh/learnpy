# 📘 MODULE 2 – BÀI 2.5: PROJECT "TODO APP" (TỔNG KẾT MODULE 2)

> **Mục tiêu bài học**:
> - Tổng hợp **tất cả** kiến thức Module 2 vào 1 project thực tế
> - Áp dụng `QMainWindow` + menu + toolbar + status bar
> - Layout phức tạp với nested layout
> - Custom widget cho task item
> - Signal/Slot kết nối nhiều tầng
> - Lưu/đọc dữ liệu với **JSON**
> - **Model hóa dữ liệu** trước khi làm UI (tư duy chuyên nghiệp)

---

## 🎯 PHẦN 1: PHÂN TÍCH YÊU CẦU

### 1.1. Mô tả app

**Todo App** – ứng dụng quản lý công việc cá nhân:
- Thêm/sửa/xóa task
- Đánh dấu task đã hoàn thành
- Phân loại theo **độ ưu tiên** (Thấp / Trung bình / Cao)
- Đặt **deadline** (tùy chọn)
- **Lọc** theo trạng thái (Tất cả / Đang làm / Hoàn thành)
- **Tìm kiếm** theo từ khóa
- **Lưu tự động** vào file JSON
- **Thống kê** ở status bar

### 1.2. Tính năng chi tiết

| Nhóm | Chức năng |
|------|-----------|
| **File** | New, Open, Save, Save As, Exit |
| **Task** | Add, Edit, Delete, Toggle done |
| **View** | Filter All/Active/Done, Search |
| **Sort** | By priority, by deadline, by created |
| **Help** | About |

### 1.3. Tư duy thiết kế – Bước quan trọng

Trước khi viết UI, hãy **thiết kế data model**:

```
Task
├── id: str (UUID)
├── title: str
├── description: str
├── priority: int (0=Low, 1=Medium, 2=High)
├── deadline: QDate | None
├── done: bool
├── created_at: datetime
└── updated_at: datetime

TaskManager (quản lý danh sách)
├── tasks: list[Task]
├── add(task)
├── remove(id)
├── update(id, **fields)
├── get(id)
├── filter(status, keyword)
└── save_to_file(path) / load_from_file(path)
```

👉 **Nguyên tắc**: Tách **logic** (TaskManager) khỏi **UI**. UI chỉ gọi method của manager.

---

## 🎯 PHẦN 2: CẤU TRÚC PROJECT

```
todo_app/
├── main.py
├── models.py                  ← Task, TaskManager
├── ui/
│   ├── main_window.py         ← MainWindow(QMainWindow)
│   ├── task_item_widget.py    ← TaskItemWidget(QWidget)
│   └── task_dialog.py         ← TaskDialog(QDialog)
├── resources/
│   └── styles.qss             ← (tùy chọn)
└── data/
    └── tasks.json             ← File lưu
```

Trong bài này tôi sẽ **gộp vào 1 file** để dễ chạy, nhưng ở cuối bài sẽ hướng dẫn **tách file** như cấu trúc trên.

---

## 🎯 PHẦN 3: MODELS – TASK & TASKMANAGER

Tạo file `models.py`:

```python
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QDate, QObject, Signal


# ============================================================
# ENUM CHO PRIORITY
# ============================================================
class Priority:
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    
    LABELS = {LOW: "Thấp", MEDIUM: "Trung bình", HIGH: "Cao"}
    COLORS = {LOW: "#3498db", MEDIUM: "#f39c12", HIGH: "#e74c3c"}
    ICONS = {LOW: "🟢", MEDIUM: "🟡", HIGH: "🔴"}
    
    @classmethod
    def label(cls, p: int) -> str:
        return cls.LABELS.get(p, "?")
    
    @classmethod
    def color(cls, p: int) -> str:
        return cls.COLORS.get(p, "#888")
    
    @classmethod
    def icon(cls, p: int) -> str:
        return cls.ICONS.get(p, "")


# ============================================================
# MODEL: TASK
# ============================================================
@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: int = Priority.MEDIUM
    deadline: Optional[str] = None             # ISO format: "2025-12-31"
    done: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        # Chỉ lấy những field hợp lệ (bỏ field lạ)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)
    
    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def deadline_date(self) -> Optional[QDate]:
        if not self.deadline:
            return None
        d = QDate.fromString(self.deadline, "yyyy-MM-dd")
        return d if d.isValid() else None
    
    def is_overdue(self) -> bool:
        """Quá hạn chưa? (chỉ tính khi chưa done)."""
        if self.done or not self.deadline:
            return False
        d = self.deadline_date()
        return d is not None and d < QDate.currentDate()
    
    def touch(self):
        self.updated_at = datetime.now().isoformat()


# ============================================================
# MANAGER: TASKMODEL
# ============================================================
class TaskModel(QObject):
    """Quản lý danh sách task + phát signal khi thay đổi."""
    
    tasks_changed = Signal()                   # Phát khi bất kỳ thay đổi nào
    
    def __init__(self):
        super().__init__()
        self._tasks: list[Task] = []
    
    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add(self, task: Task):
        self._tasks.append(task)
        self.tasks_changed.emit()
    
    def remove(self, task_id: str):
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self.tasks_changed.emit()
    
    def update(self, task_id: str, **fields):
        task = self.get(task_id)
        if task is None:
            return
        for k, v in fields.items():
            if hasattr(task, k):
                setattr(task, k, v)
        task.touch()
        self.tasks_changed.emit()
    
    def get(self, task_id: str) -> Optional[Task]:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None
    
    def toggle_done(self, task_id: str):
        task = self.get(task_id)
        if task:
            task.done = not task.done
            task.touch()
            self.tasks_changed.emit()
    
    # ------------------------------------------------------------------
    # QUERY
    # ------------------------------------------------------------------
    def all_tasks(self) -> list[Task]:
        return list(self._tasks)
    
    def filter(self, status: str = "all", keyword: str = "") -> list[Task]:
        """
        status: 'all' | 'active' | 'done'
        keyword: tìm trong title + description
        """
        result = self._tasks
        
        if status == "active":
            result = [t for t in result if not t.done]
        elif status == "done":
            result = [t for t in result if t.done]
        
        if keyword:
            kw = keyword.lower()
            result = [
                t for t in result
                if kw in t.title.lower() or kw in t.description.lower()
            ]
        
        return list(result)
    
    def stats(self) -> dict:
        total = len(self._tasks)
        done = sum(1 for t in self._tasks if t.done)
        return {"total": total, "done": done, "active": total - done}
    
    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------
    def save_to_file(self, path: Path):
        data = {
            "version": 1,
            "tasks": [t.to_dict() for t in self._tasks],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def load_from_file(self, path: Path):
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._tasks = [Task.from_dict(d) for d in data.get("tasks", [])]
            self.tasks_changed.emit()
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"File không hợp lệ: {e}")
```

### 3.1. Điểm đáng chú ý trong Models

1. **`@dataclass`**: chuẩn Python, tự tạo `__init__`, `__repr__`
2. **`field(default_factory=...)`**: cho giá trị động (UUID, datetime)
3. **`from __future__ import annotations`**: cho phép dùng `list[Task]` ở Python 3.9+
4. **`TaskModel(QObject)`**: kế thừa QObject để dùng `Signal`
5. **`tasks_changed` signal**: 1 signal duy nhất, UI connect vào để refresh → đơn giản hóa
6. **`to_dict` / `from_dict`**: chuẩn hóa serialize, bỏ field lạ
7. **`Path`**: dùng `pathlib`, không dùng string nối tay
8. **UUID**: mỗi task có id ổn định, dễ update/remove

---

## 🎯 PHẦN 4: TASK ITEM WIDGET (CUSTOM WIDGET)

Tạo file `ui/task_item_widget.py` (hoặc gộp vào main):

```python
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QCheckBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from models import Task, Priority


class TaskItemWidget(QWidget):
    """1 dòng task trong danh sách."""
    
    toggled = Signal(str)              # task_id
    edit_requested = Signal(str)
    delete_requested = Signal(str)
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        
        self.setObjectName("TaskItemWidget")
        self._setup_ui()
        self._apply_style()
        self._refresh()
    
    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        main = QHBoxLayout(self)
        main.setContentsMargins(12, 8, 12, 8)
        main.setSpacing(12)
        
        # === Checkbox ===
        self.chk = QCheckBox()
        self.chk.setFixedSize(20, 20)
        self.chk.toggled.connect(lambda _: self.toggled.emit(self.task.id))
        main.addWidget(self.chk, alignment=Qt.AlignmentFlag.AlignTop)
        
        # === Info (title + meta) ===
        info = QVBoxLayout()
        info.setSpacing(2)
        
        # Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        
        self.lbl_priority = QLabel()
        self.lbl_priority.setFixedWidth(20)
        title_row.addWidget(self.lbl_priority)
        
        self.lbl_title = QLabel()
        self.lbl_title.setWordWrap(True)
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        self.lbl_title.setFont(f)
        title_row.addWidget(self.lbl_title, stretch=1)
        
        info.addLayout(title_row)
        
        # Description
        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #666; font-size: 12px;")
        info.addWidget(self.lbl_desc)
        
        # Meta row (deadline + created)
        self.lbl_meta = QLabel()
        self.lbl_meta.setStyleSheet("color: #888; font-size: 11px;")
        info.addWidget(self.lbl_meta)
        
        main.addLayout(info, stretch=1)
        
        # === Buttons ===
        btn_box = QVBoxLayout()
        btn_box.setSpacing(4)
        
        self.btn_edit = QPushButton("✏️")
        self.btn_edit.setFixedSize(30, 30)
        self.btn_edit.setToolTip("Sửa")
        self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.task.id))
        
        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.setToolTip("Xóa")
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.task.id))
        
        btn_box.addWidget(self.btn_edit)
        btn_box.addWidget(self.btn_delete)
        btn_box.addStretch()
        
        main.addLayout(btn_box)
    
    # ------------------------------------------------------------------
    # STYLE
    # ------------------------------------------------------------------
    def _apply_style(self):
        self.setStyleSheet("""
            #TaskItemWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            #TaskItemWidget:hover {
                border: 1px solid #2196F3;
                background: #f8fbff;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #e3f2fd;
            }
        """)
    
    # ------------------------------------------------------------------
    # REFRESH (sau khi task đổi)
    # ------------------------------------------------------------------
    def _refresh(self):
        t = self.task
        
        self.chk.blockSignals(True)
        self.chk.setChecked(t.done)
        self.chk.blockSignals(False)
        
        # Priority icon + color
        self.lbl_priority.setText(Priority.icon(t.priority))
        self.lbl_priority.setToolTip(f"Ưu tiên: {Priority.label(t.priority)}")
        
        # Title
        self.lbl_title.setText(t.title or "(Không có tiêu đề)")
        if t.done:
            self.lbl_title.setStyleSheet(
                f"color: #999; text-decoration: line-through; "
                f"border-left: 4px solid {Priority.color(t.priority)}; padding-left: 6px;"
            )
        else:
            self.lbl_title.setStyleSheet(
                f"color: #222; "
                f"border-left: 4px solid {Priority.color(t.priority)}; padding-left: 6px;"
            )
        
        # Description
        if t.description:
            self.lbl_desc.setText(t.description)
            self.lbl_desc.show()
        else:
            self.lbl_desc.hide()
        
        # Meta
        parts = []
        if t.deadline:
            d = t.deadline_date()
            if d:
                text = f"📅 {d.toString('dd/MM/yyyy')}"
                if t.is_overdue():
                    text += " ⚠️ Quá hạn"
                    parts.append(f"<span style='color:#e74c3c;'>{text}</span>")
                else:
                    parts.append(text)
        
        created = t.created_at[:10]        # yyyy-mm-dd
        parts.append(f"🕐 {created}")
        
        self.lbl_meta.setText("  •  ".join(parts))
    
    # ------------------------------------------------------------------
    # UPDATE TASK
    # ------------------------------------------------------------------
    def update_task(self, task: Task):
        self.task = task
        self._refresh()
```

### 4.1. Điểm đáng chú ý

1. **Signal riêng cho từng action**: `toggled`, `edit_requested`, `delete_requested` – MainWindow connect vào
2. **`setObjectName`**: cho phép CSS selector `#TaskItemWidget`
3. **`blockSignals(True/False)`**: khi set `chk.setChecked()` từ code, không phát `toggled` trở lại → tránh vòng lặp vô hạn
4. **`_refresh()`**: tách riêng, dễ gọi lại khi data đổi
5. **HTML inline trong QLabel**: `setText("<span style='...'>...</span>")` – QLabel hỗ trợ subset HTML
6. **`border-left` với màu priority**: cách đánh dấu mức ưu tiên không cần màu nền

---

## 🎯 PHẦN 5: TASK DIALOG – SỬA / THÊM TASK

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDateEdit, QDialogButtonBox, QCheckBox, QWidget, QHBoxLayout,
    QMessageBox
)
from PySide6.QtCore import QDate

from models import Task, Priority


class TaskDialog(QDialog):
    """Dialog thêm/sửa task."""
    
    def __init__(self, task: Task = None, parent=None):
        super().__init__(parent)
        self._task = task
        self._is_edit = task is not None
        
        self.setWindowTitle("Sửa task" if self._is_edit else "Thêm task")
        self.setMinimumWidth(450)
        
        self._setup_ui()
        
        if self._is_edit:
            self._load_task(task)
    
    # ------------------------------------------------------------------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        # Title
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("Ví dụ: Hoàn thành báo cáo Q4")
        self.txt_title.setMaxLength(200)
        form.addRow("Tiêu đề *:", self.txt_title)
        
        # Description
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Mô tả chi tiết (tùy chọn)...")
        self.txt_desc.setMaximumHeight(100)
        form.addRow("Mô tả:", self.txt_desc)
        
        # Priority
        self.cbo_priority = QComboBox()
        self.cbo_priority.addItem("🟢 Thấp", Priority.LOW)
        self.cbo_priority.addItem("🟡 Trung bình", Priority.MEDIUM)
        self.cbo_priority.addItem("🔴 Cao", Priority.HIGH)
        self.cbo_priority.setCurrentIndex(1)          # Medium
        form.addRow("Độ ưu tiên:", self.cbo_priority)
        
        # Deadline (có/không)
        deadline_widget = QWidget()
        dl_layout = QHBoxLayout(deadline_widget)
        dl_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chk_has_deadline = QCheckBox("Có deadline")
        self.chk_has_deadline.toggled.connect(self._on_deadline_toggled)
        dl_layout.addWidget(self.chk_has_deadline)
        
        self.date_deadline = QDateEdit()
        self.date_deadline.setCalendarPopup(True)
        self.date_deadline.setDisplayFormat("dd/MM/yyyy")
        self.date_deadline.setDate(QDate.currentDate().addDays(7))
        self.date_deadline.setMinimumDate(QDate.currentDate())
        self.date_deadline.setEnabled(False)
        dl_layout.addWidget(self.date_deadline)
        dl_layout.addStretch()
        
        form.addRow("Deadline:", deadline_widget)
        
        # Done (chỉ khi edit)
        self.chk_done = QCheckBox("Đã hoàn thành")
        if self._is_edit:
            form.addRow("Trạng thái:", self.chk_done)
        else:
            self.chk_done.hide()
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Lưu")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Hủy")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    # ------------------------------------------------------------------
    def _on_deadline_toggled(self, checked: bool):
        self.date_deadline.setEnabled(checked)
    
    def _load_task(self, task: Task):
        self.txt_title.setText(task.title)
        self.txt_desc.setPlainText(task.description)
        
        idx = self.cbo_priority.findData(task.priority)
        if idx >= 0:
            self.cbo_priority.setCurrentIndex(idx)
        
        if task.deadline:
            d = task.deadline_date()
            if d:
                self.chk_has_deadline.setChecked(True)
                self.date_deadline.setDate(d)
        
        self.chk_done.setChecked(task.done)
    
    # ------------------------------------------------------------------
    def _on_accept(self):
        title = self.txt_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tiêu đề.")
            self.txt_title.setFocus()
            return
        self.accept()
    
    # ------------------------------------------------------------------
    def get_data(self) -> dict:
        """Trả về dict field của task."""
        deadline = None
        if self.chk_has_deadline.isChecked():
            deadline = self.date_deadline.date().toString("yyyy-MM-dd")
        
        return {
            "title": self.txt_title.text().strip(),
            "description": self.txt_desc.toPlainText().strip(),
            "priority": self.cbo_priority.currentData(),
            "deadline": deadline,
            "done": self.chk_done.isChecked() if self._is_edit else False,
        }
```

### 5.1. Điểm hay

1. **1 dialog cho cả add & edit**: dùng cờ `_is_edit`
2. **`currentData()` của ComboBox**: lấy giá trị ẩn (int priority) thay vì text
3. **Checkbox "Có deadline"**: cho phép task không có deadline
4. **`findData(task.priority)`**: tìm index theo data (không hardcode index)
5. **`_on_accept` override**: validate trước khi đóng dialog
6. **`get_data()`**: trả về dict sạch, MainWindow không cần biết bên trong dialog có gì
7. **`QDialogButtonBox`**: cross-platform, thứ tự nút đúng trên Mac/Windows

---

## 🎯 PHẦN 6: MAIN WINDOW – KẾT NỐI MỌI THỨ

Đây là file lớn nhất. Tôi chia thành các phần rõ ràng.

```python
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QComboBox, QLineEdit, QLabel, QPushButton,
    QMessageBox, QFileDialog, QToolBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence

from models import Task, TaskModel, Priority
from ui.task_item_widget import TaskItemWidget
from ui.task_dialog import TaskDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo App")
        self.resize(700, 700)
        
        # --- Model ---
        self.model = TaskModel()
        self.model.tasks_changed.connect(self._on_tasks_changed)
        
        # --- State ---
        self.current_file: Path | None = None
        self.current_filter = "all"          # all / active / done
        self.current_keyword = ""
        self.is_modified = False
        
        # Auto-save timer (500ms debounce)
        self._autosave_timer = QTimer()
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._autosave)
        
        # --- Build ---
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_central()
        self._create_statusbar()
        
        # Load default file nếu có
        self._load_default()
    
    # ================================================================
    # ACTIONS
    # ================================================================
    def _create_actions(self):
        # File
        self.act_new = QAction("&New", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self.file_new)
        
        self.act_open = QAction("&Open...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self.file_open)
        
        self.act_save = QAction("&Save", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self.file_save)
        
        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.file_save_as)
        
        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # Task
        self.act_add = QAction("➕ &Thêm task", self)
        self.act_add.setShortcut("Ctrl+N")
        self.act_add.triggered.connect(self.add_task)
        
        self.act_delete_done = QAction("🧹 Xóa task đã xong", self)
        self.act_delete_done.triggered.connect(self.delete_done_tasks)
        
        # Help
        self.act_about = QAction("&About", self)
        self.act_about.triggered.connect(self.show_about)
    
    # ================================================================
    # MENUS
    # ================================================================
    def _create_menus(self):
        mb = self.menuBar()
        
        file_menu = mb.addMenu("&File")
        file_menu.addAction(self.act_new)
        file_menu.addAction(self.act_open)
        file_menu.addSeparator()
        file_menu.addAction(self.act_save)
        file_menu.addAction(self.act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)
        
        task_menu = mb.addMenu("&Task")
        task_menu.addAction(self.act_add)
        task_menu.addSeparator()
        task_menu.addAction(self.act_delete_done)
        
        help_menu = mb.addMenu("&Help")
        help_menu.addAction(self.act_about)
    
    # ================================================================
    # TOOLBAR
    # ================================================================
    def _create_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        
        tb.addAction(self.act_add)
        tb.addSeparator()
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_delete_done)
    
    # ================================================================
    # CENTRAL WIDGET
    # ================================================================
    def _create_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # ===== Toolbar lọc & tìm kiếm =====
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)
        
        filter_bar.addWidget(QLabel("Lọc:"))
        self.cbo_filter = QComboBox()
        self.cbo_filter.addItem("Tất cả", "all")
        self.cbo_filter.addItem("Đang làm", "active")
        self.cbo_filter.addItem("Đã xong", "done")
        self.cbo_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_bar.addWidget(self.cbo_filter)
        
        filter_bar.addSpacing(12)
        filter_bar.addWidget(QLabel("Tìm:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm theo tiêu đề / mô tả...")
        self.txt_search.setClearButtonEnabled(True)
        self.txt_search.textChanged.connect(self._on_search_changed)
        filter_bar.addWidget(self.txt_search, stretch=1)
        
        layout.addLayout(filter_bar)
        
        # ===== Danh sách task (scroll area) =====
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
        
        # Container chứa các TaskItemWidget
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(8, 8, 8, 8)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()             # Đẩy task lên đầu
        
        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll, stretch=1)
        
        # ===== Empty state label =====
        self.lbl_empty = QLabel("Chưa có task nào.\nNhấn Ctrl+N hoặc nút ➕ để bắt đầu!")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(
            "color: #aaa; font-size: 14px; padding: 40px;"
        )
        self.lbl_empty.hide()
        layout.addWidget(self.lbl_empty)
    
    # ================================================================
    # STATUS BAR
    # ================================================================
    def _create_statusbar(self):
        sb = self.statusBar()
        
        self.lbl_stats = QLabel()
        sb.addPermanentWidget(self.lbl_stats)
        
        sb.showMessage("Sẵn sàng")
    
    # ================================================================
    # RENDER DANH SÁCH TASK
    # ================================================================
    def _render_tasks(self):
        # Xóa hết widget cũ (giữ stretch cuối)
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # Lọc
        tasks = self.model.filter(self.current_filter, self.current_keyword)
        
        # Sort: chưa xong lên đầu, priority cao lên trước, deadline gần lên trước
        def sort_key(t: Task):
            return (
                t.done,                          # False (chưa xong) lên trước
                -t.priority,                     # Priority cao lên trước
                t.deadline or "9999-99-99",      # Deadline gần lên trước
                t.created_at,
            )
        
        tasks.sort(key=sort_key)
        
        # Hiển thị
        if not tasks:
            self.scroll.hide()
            self.lbl_empty.show()
        else:
            self.scroll.show()
            self.lbl_empty.hide()
            
            for t in tasks:
                widget = TaskItemWidget(t)
                widget.toggled.connect(self._on_task_toggled)
                widget.edit_requested.connect(self._on_task_edit)
                widget.delete_requested.connect(self._on_task_delete)
                # Insert trước stretch (vị trí cuối cùng - 1)
                self.list_layout.insertWidget(self.list_layout.count() - 1, widget)
        
        self._update_stats()
    
    # ================================================================
    # EVENT HANDLERS
    # ================================================================
    def _on_tasks_changed(self):
        self.is_modified = True
        self._update_title()
        self._render_tasks()
        self._schedule_autosave()
    
    def _on_filter_changed(self, _idx: int):
        self.current_filter = self.cbo_filter.currentData()
        self._render_tasks()
    
    def _on_search_changed(self, text: str):
        self.current_keyword = text.strip()
        self._render_tasks()
    
    def _on_task_toggled(self, task_id: str):
        self.model.toggle_done(task_id)
    
    def _on_task_edit(self, task_id: str):
        task = self.model.get(task_id)
        if not task:
            return
        dlg = TaskDialog(task, self)
        if dlg.exec():
            self.model.update(task_id, **dlg.get_data())
    
    def _on_task_delete(self, task_id: str):
        task = self.model.get(task_id)
        if not task:
            return
        reply = QMessageBox.question(
            self, "Xóa task",
            f"Xóa task \"{task.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.remove(task_id)
    
    # ================================================================
    # TASK ACTIONS
    # ================================================================
    def add_task(self):
        dlg = TaskDialog(parent=self)
        if dlg.exec():
            data = dlg.get_data()
            task = Task(**data)
            self.model.add(task)
            self.statusBar().showMessage(f"Đã thêm: {task.title}", 3000)
    
    def delete_done_tasks(self):
        done = [t for t in self.model.all_tasks() if t.done]
        if not done:
            QMessageBox.information(self, "Thông báo", "Không có task nào đã xong.")
            return
        reply = QMessageBox.question(
            self, "Xóa task đã xong",
            f"Xóa {len(done)} task đã hoàn thành?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for t in done:
                self.model.remove(t.id)
            self.statusBar().showMessage(f"Đã xóa {len(done)} task", 3000)
    
    # ================================================================
    # FILE OPERATIONS
    # ================================================================
    def file_new(self):
        if not self._maybe_save():
            return
        self.model._tasks.clear()
        self.model.tasks_changed.emit()
        self.current_file = None
        self.is_modified = False
        self._update_title()
        self.statusBar().showMessage("Đã tạo danh sách mới", 3000)
    
    def file_open(self):
        if not self._maybe_save():
            return
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Mở file", "", "JSON files (*.json);;All files (*)"
        )
        if not path_str:
            return
        try:
            self.model.load_from_file(Path(path_str))
            self.current_file = Path(path_str)
            self.is_modified = False
            self._update_title()
            self.statusBar().showMessage(f"Đã mở: {self.current_file.name}", 3000)
        except ValueError as e:
            QMessageBox.critical(self, "Lỗi", str(e))
    
    def file_save(self):
        if self.current_file is None:
            return self.file_save_as()
        self._write_file(self.current_file)
    
    def file_save_as(self):
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Lưu file", "tasks.json", "JSON files (*.json)"
        )
        if not path_str:
            return
        self._write_file(Path(path_str))
    
    def _write_file(self, path: Path):
        try:
            self.model.save_to_file(path)
            self.current_file = path
            self.is_modified = False
            self._update_title()
            self.statusBar().showMessage(f"Đã lưu: {path.name}", 3000)
        except OSError as e:
            QMessageBox.critical(self, "Lỗi", f"Không lưu được:\n{e}")
    
    # ================================================================
    # AUTOSAVE
    # ================================================================
    def _schedule_autosave(self):
        if self.current_file:
            self._autosave_timer.start(500)         # debounce 500ms
    
    def _autosave(self):
        if self.current_file:
            try:
                self.model.save_to_file(self.current_file)
                self.is_modified = False
                self._update_title()
            except OSError:
                pass                                # Im lặng khi autosave fail
    
    # ================================================================
    # TITLE & STATUS
    # ================================================================
    def _update_title(self):
        name = self.current_file.name if self.current_file else "Untitled"
        mark = " •" if self.is_modified else ""
        self.setWindowTitle(f"{name}{mark} - Todo App")
    
    def _update_stats(self):
        s = self.model.stats()
        self.lbl_stats.setText(
            f"📋 Tổng: {s['total']}  |  ⏳ Đang làm: {s['active']}  |  ✅ Xong: {s['done']}"
        )
    
    # ================================================================
    # DEFAULT FILE
    # ================================================================
    def _load_default(self):
        default = Path("data/tasks.json")
        if default.exists():
            try:
                self.model.load_from_file(default)
                self.current_file = default
                self.is_modified = False
                self._update_title()
                self.statusBar().showMessage(f"Đã tải: {default}", 3000)
            except ValueError:
                pass
        self._render_tasks()
    
    # ================================================================
    # CLOSE & SAVE GUARD
    # ================================================================
    def _maybe_save(self) -> bool:
        if not self.is_modified:
            return True
        reply = QMessageBox.question(
            self, "Chưa lưu",
            "Danh sách đã thay đổi. Lưu trước khi tiếp tục?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Save:
            self.file_save()
            return not self.is_modified
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
    
    def closeEvent(self, event):
        if self._maybe_save():
            event.accept()
        else:
            event.ignore()
    
    # ================================================================
    # ABOUT
    # ================================================================
    def show_about(self):
        QMessageBox.about(
            self, "About Todo App",
            "<h3>Todo App v1.0</h3>"
            "<p>Ứng dụng quản lý công việc.</p>"
            "<p>Được xây dựng với <b>PySide6</b>.</p>"
            "<p>© 2025</p>"
        )


# ================================================================
# ENTRY POINT
# ================================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Todo App")
    
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 6.1. Điểm đáng chú ý

1. **Auto-save với debounce**: `QTimer.singleShot` reset mỗi lần đổi → chỉ save sau khi user dừng 500ms
2. **`_render_tasks` xóa widget cũ đúng cách**: dùng `takeAt` + `deleteLater` (không xóa `delete` ngay → tránh crash)
3. **Sort key thông minh**: tuple đa tiêu chí, không cần `functools.cmp_to_key`
4. **`insertWidget(count - 1, ...)`**: chèn trước stretch
5. **Empty state**: hiển thị gợi ý khi chưa có task
6. **Filter + Search kết hợp**: model.filter() nhận cả 2
7. **`currentData()` trên ComboBox filter**: dùng data ẩn thay vì parse text
8. **`_maybe_save` 3 nút**: Save / Discard / Cancel (không chỉ 2)
9. **`closeEvent` guard**: chống mất dữ liệu khi đóng
10. **Autosave im lặng**: không hiện popup khi autosave fail → tránh phiền

---

## 🎯 PHẦN 7: CHẠY VÀ KIỂM THỬ

### 7.1. Chuẩn bị thư mục

```
todo_app/
├── main.py
├── models.py
├── ui/
│   ├── __init__.py
│   ├── task_item_widget.py
│   └── task_dialog.py
└── data/
    └── (tasks.json sẽ tự sinh)
```

Tạo `ui/__init__.py` rỗng.

### 7.2. Chạy

```bash
cd todo_app
python main.py
```

### 7.3. Test cases

| Test | Các bước | Kỳ vọng |
|------|----------|---------|
| Thêm task | Ctrl+N → nhập → OK | Task xuất hiện đầu danh sách |
| Đánh dấu done | Click checkbox | Title gạch ngang, đẩy xuống cuối |
| Sửa | Click ✏️ → đổi title → OK | Cập nhật ngay |
| Xóa | Click 🗑️ → Yes | Task biến mất |
| Lọc | Chọn "Đang làm" | Chỉ hiện task chưa xong |
| Tìm kiếm | Gõ từ khóa | Lọc real-time |
| Save/Load | Save As → New → Open | Dữ liệu khôi phục đúng |
| Auto-save | Save As lần đầu → thêm task | File tự cập nhật sau 500ms |
| Close guard | Sửa → đóng cửa sổ | Hiện dialog hỏi lưu |
| Quá hạn | Task có deadline hôm qua | Hiển thị "⚠️ Quá hạn" đỏ |

---

## 🎯 PHẦN 8: NHỮNG GÌ ĐÃ DÙNG – ÔN LẠI MODULE 2

| Bài | Kỹ thuật đã áp dụng |
|-----|---------------------|
| **2.1** | `QMainWindow`, menu, toolbar, status bar, `QAction`, `closeEvent` |
| **2.2** | `QLineEdit`, `QTextEdit`, `QComboBox`, `QDateEdit`, `QCheckBox`, signals |
| **2.3** | Nested layouts (`QVBoxLayout` + `QHBoxLayout`), `QScrollArea`, stretch, margin |
| **2.4** | Custom `TaskItemWidget`, `QPainter` style, `Signal` tùy chỉnh, size policy |

### 8.1. Bonus – Những tư duy chuyên nghiệp

1. **Tách Model / View**: `TaskModel` không biết gì về UI
2. **1 signal `tasks_changed`** thay vì nhiều signal nhỏ → UI refresh đơn giản
3. **Debounce autosave**: không spam I/O
4. **`_maybe_save` pattern**: chuẩn Qt, ai cũng làm thế
5. **Data-driven UI**: `_render_tasks` build UI từ data, không giữ state riêng
6. **UUID**: id ổn định, không phụ thuộc index
7. **Type hints**: `Optional[Task]`, `list[Task]` – dễ đọc, IDE gợi ý tốt

---

## 📝 BÀI TẬP MỞ RỘNG

### Bài tập 2.5.1 (Cơ bản)
Thêm cột **Sort** trong toolbar: ComboBox với các tiêu chí:
- Mặc định (priority + deadline)
- Theo tên A-Z
- Theo deadline
- Theo ngày tạo (mới nhất)

💡 Gợi ý: Thêm biến `self.sort_key`, sửa `sort_key()` trong `_render_tasks`.

### Bài tập 2.5.2 (Trung bình)
Thêm **category/tag** cho task:
- Dialog có thêm trường `tags` (list str)
- Hiển thị tag như badge trong `TaskItemWidget`
- Filter theo tag

### Bài tập 2.5.3 (Khá)
**Undo/Redo** cho thao tác với task:
- Dùng `QUndoStack`, `QUndoCommand`
- Thêm menu Edit với Undo/Redo (Ctrl+Z / Ctrl+Y)
- Mọi thao tác (add/edit/delete/toggle) đều undo được

💡 Gợi ý:
```python
from PySide6.QtGui import QUndoStack, QUndoCommand

class AddTaskCommand(QUndoCommand):
    def __init__(self, model, task):
        super().__init__(f"Thêm: {task.title}")
        self.model = model
        self.task = task
    def redo(self): self.model.add(self.task)
    def undo(self): self.model.remove(self.task.id)
```

### Bài tập 2.5.4 (Nâng cao)
**Drag & Drop** để sắp xếp task:
- Cho phép kéo task lên/xuống
- Lưu `order` vào task
- Sort theo order

💡 Gợi ý: Override `dragEnterEvent`, `dropEvent` trên `TaskItemWidget`, hoặc dùng `QListWidget` với `InternalMove`.

### Bài tập 2.5.5 (Khó)
**Reminder** – nhắc nhở khi gần đến deadline:
- Timer check mỗi 60s
- Task nào deadline <= 1 ngày → hiện `QSystemTrayIcon.showMessage()`
- Có âm thanh (dùng `QSoundEffect`)

---

## ✅ CHECKLIST SAU BÀI 2.5 – KẾT THÚC MODULE 2

- [ ] Chạy được app đầy đủ chức năng
- [ ] Hiểu luồng: **Model → Signal → MainWindow → Render UI**
- [ ] Biết tách **logic** khỏi **UI**
- [ ] Biết dùng **custom widget** cho item phức tạp
- [ ] Biết **serialize/deserialize** với dataclass
- [ ] Biết **debounce** với `QTimer`
- [ ] Biết **`_maybe_save` pattern** trước khi mất dữ liệu
- [ ] Biết xóa widget đúng cách (`takeAt` + `deleteLater`)
- [ ] Hoàn thành ít nhất **2 bài tập mở rộng**
- [ ] **Tự tay gõ code**, không copy-paste toàn bộ

---

## 🎓 TỔNG KẾT MODULE 2

Bạn đã hoàn thành Module 2 với:

| Kỹ năng | Trình độ |
|---------|----------|
| QMainWindow + menu + toolbar | ✅ Thành thạo |
| Widget nhập liệu cơ bản | ✅ Thành thạo |
| Layout (V/H/Grid/Form/Stack/Splitter) | ✅ Thành thạo |
| Size policy & spacer | ✅ Hiểu |
| Custom widget + Signal tùy chỉnh | ✅ Biết làm |
| QPainter cơ bản | ✅ Biết cơ bản |
| JSON persistence | ✅ Biết làm |
| Model/View separation (thô) | ✅ Hiểu ý tưởng |

---

## 🔜 MODULE 3 – SIGNAL & SLOT NÂNG CAO

Chúng ta sẽ đi sâu vào phần "trái tim" của Qt:

- **Signal/Slot chi tiết**: cơ chế bên dưới, performance
- **Connection types**: Auto, Direct, Queued, BlockingQueued
- **Custom Signal nâng cao**: overload, tham số phức tạp
- **Event system**: phân biệt Signal vs Event
- **Event Filter**: chặn event từ widget khác
- **Override event**: `keyPressEvent`, `mousePressEvent`, `paintEvent`, `closeEvent`, `resizeEvent`, `dropEvent`...
- **`QShortcut`, `QShortcutContext`**
- Project: **Paint app** dùng event override

---

👉 Bạn muốn:
1. **Bắt đầu Module 3 – Bài 3.1: Signal/Slot chi tiết**?
2. **Tôi giải chi tiết một bài tập 2.5.x** nào?
3. **Tôi hướng dẫn tách file** cho project Todo App (nếu bạn muốn dùng luôn)?

Bạn cũng có thể **gửi code bạn đã viết** cho Todo App, tôi sẽ review và góp ý! 🚀