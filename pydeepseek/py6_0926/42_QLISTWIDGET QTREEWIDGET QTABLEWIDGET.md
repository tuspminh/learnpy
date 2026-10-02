# 📘 MODULE 4 – BÀI 4.2: QLISTWIDGET, QTREEWIDGET, QTABLEWIDGET

> **Mục tiêu bài học**:
> - Nắm vững 3 widget item-based quan trọng nhất
> - Hiểu **QListWidgetItem**, **QTreeWidgetItem**, **QTableWidgetItem**
> - Thêm/xóa/sửa/di chuyển item thành thạo
> - Biết **item data role** – lưu dữ liệu ẩn trong item
> - Kéo thả, sort, filter, checkbox trong item
> - **`setItemWidget()`** – nhúng widget tùy chỉnh vào item
> - Xây dựng **File Explorer** với tree + list

---

## 🎯 PHẦN 1: TỔNG QUAN 3 WIDGET

### 1.1. So sánh

| Widget | Cấu trúc | Dùng cho |
|--------|----------|----------|
| **QListWidget** | Danh sách 1 chiều | Menu, danh sách đơn giản |
| **QTreeWidget** | Cây phân cấp | File explorer, outline, category |
| **QTableWidget** | Bảng 2 chiều | Data grid, danh sách có cột |

### 1.2. Item-based vs Model/View

**Quan trọng**: 3 widget này là **item-based** (tiện lợi, code nhanh). Chúng được xây trên **Model/View** (chuyên nghiệp hơn nhưng phức tạp hơn).

| Tiêu chí | Item-based | Model/View |
|----------|-----------|------------|
| Code | Đơn giản | Phức tạp |
| Data lớn (>10k) | Chậm | Nhanh |
| Nhiều view cùng data | Khó | Dễ |
| Tùy chỉnh sâu | Hạn chế | Rất linh hoạt |
| Khi nào | < 1000 item | App lớn |

👉 **Module 6** sẽ học Model/View. Bài này dùng item-based cho nhanh.

---

## 🎯 PHẦN 2: QLISTWIDGET

### 2.1. Tạo và thêm item

```python
from PySide6.QtWidgets import QListWidget, QListWidgetItem

lst = QListWidget()

# Cách 1: Thêm bằng string
lst.addItem("Item 1")
lst.addItems(["Item 2", "Item 3", "Item 4"])

# Cách 2: Tạo item object
item = QListWidgetItem("Item 5")
lst.addItem(item)

# Chèn vị trí
lst.insertItem(0, "Đầu tiên")

# Xóa
lst.takeItem(0)                              # Xóa + trả về item
lst.clear()                                  # Xóa hết
```

### 2.2. QListWidgetItem – chi tiết

```python
item = QListWidgetItem()

# Text
item.setText("Hello")

# Icon
from PySide6.QtGui import QIcon
item.setIcon(QIcon("star.png"))

# Tooltip
item.setToolTip("Gợi ý")

# Trạng thái
item.setCheckState(Qt.CheckState.Checked)    # Có checkbox
item.setFlags(
    Qt.ItemFlag.ItemIsEnabled |
    Qt.ItemFlag.ItemIsSelectable |
    Qt.ItemFlag.ItemIsUserCheckable |
    Qt.ItemFlag.ItemIsEditable |
    Qt.ItemFlag.ItemIsDragEnabled
)

# Màu & font
item.setForeground(QColor("red"))
item.setBackground(QColor("#ffffcc"))
font = QFont()
font.setBold(True)
item.setFont(font)

# Căn lề
item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

# Size hint
item.setSizeHint(QSize(100, 40))
```

### 2.3. Data Roles – Lưu dữ liệu ẩn

Đây là **khái niệm quan trọng nhất** của item-based.

Mỗi item có **nhiều role** – mỗi role lưu 1 loại dữ liệu:

```python
# Roles có sẵn
Qt.ItemDataRole.DisplayRole          # Text hiển thị
Qt.ItemDataRole.DecorationRole       # Icon
Qt.ItemDataRole.ToolTipRole          # Tooltip
Qt.ItemDataRole.UserRole             # Dữ liệu tùy chỉnh
Qt.ItemDataRole.UserRole + 1         # Thêm role khác
Qt.ItemDataRole.CheckStateRole       # Trạng thái checkbox
```

**Ví dụ** – Lưu full path trong khi hiển thị tên file:

```python
item = QListWidgetItem("document.txt")       # Hiển thị
item.setData(Qt.ItemDataRole.UserRole, "/home/user/docs/document.txt")
item.setData(Qt.ItemDataRole.UserRole + 1, 12345)  # Size

# Đọc
display = item.text()                        # "document.txt"
full_path = item.data(Qt.ItemDataRole.UserRole)
size = item.data(Qt.ItemDataRole.UserRole + 1)
```

### 2.4. Signals

```python
lst.itemClicked.connect(self.on_click)              # Item bị click
lst.itemDoubleClicked.connect(self.on_double)       # Double click
lst.itemSelectionChanged.connect(self.on_selection) # Selection đổi
lst.itemChanged.connect(self.on_changed)            # Item đổi (text, check)
lst.currentItemChanged.connect(self.on_current)     # (current, previous)
lst.currentRowChanged.connect(self.on_row)          # int
```

**Khác biệt click vs selectionChanged**:
- `itemClicked`: chỉ khi user click chuột
- `itemSelectionChanged`: bất kỳ thay đổi selection (click, phím, code)

### 2.5. Properties

```python
lst.setSelectionMode(QListWidget.SelectionMode.SingleSelection)   # 1 item
lst.setSelectionMode(QListWidget.SelectionMode.MultiSelection)    # Nhiều
lst.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection) # Ctrl+click
lst.setSelectionMode(QListWidget.SelectionMode.ContiguousSelection)  # Shift

lst.setViewMode(QListWidget.ViewMode.ListMode)      # Danh sách
lst.setViewMode(QListWidget.ViewMode.IconMode)      # Lưới icon

lst.setIconSize(QSize(48, 48))
lst.setGridSize(QSize(100, 100))                    # Cho IconMode

lst.setSortingEnabled(True)                         # Cho phép sort
lst.setWordWrap(True)
lst.setSpacing(5)
```

### 2.6. Truy cập item

```python
# Theo vị trí
item = lst.item(0)
row = lst.row(item)

# Item đang chọn
selected = lst.selectedItems()               # list
current = lst.currentItem()                  # 1 item
current_row = lst.currentRow()               # int (-1 nếu không có)

# Đếm
count = lst.count()
```

### 2.7. Ví dụ – Todo List với checkbox

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton
)


class TodoList(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Input row
        input_row = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Nhập task...")
        self.txt_input.returnPressed.connect(self.add_task)
        
        btn_add = QPushButton("Thêm")
        btn_add.clicked.connect(self.add_task)
        
        input_row.addWidget(self.txt_input)
        input_row.addWidget(btn_add)
        layout.addLayout(input_row)
        
        # List
        self.list = QListWidget()
        self.list.itemChanged.connect(self.on_item_changed)
        self.list.itemDoubleClicked.connect(self.remove_item)
        layout.addWidget(self.list)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        btn_clear_done = QPushButton("Xóa task đã xong")
        btn_clear_done.clicked.connect(self.clear_done)
        
        btn_clear_all = QPushButton("Xóa hết")
        btn_clear_all.clicked.connect(self.list.clear)
        
        btn_row.addWidget(btn_clear_done)
        btn_row.addWidget(btn_clear_all)
        layout.addLayout(btn_row)
        
        # Count label
        self.lbl_count = QLabel("Tổng: 0")
        layout.addWidget(self.lbl_count)
        
        self.update_count()
    
    def add_task(self):
        text = self.txt_input.text().strip()
        if not text:
            return
        
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.list.addItem(item)
        
        self.txt_input.clear()
        self.update_count()
    
    def on_item_changed(self, item: QListWidgetItem):
        # Gạch ngang + màu xám nếu checked
        if item.checkState() == Qt.CheckState.Checked:
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
            item.setForeground(Qt.GlobalColor.gray)
        else:
            font = item.font()
            font.setStrikeOut(False)
            item.setFont(font)
            item.setForeground(Qt.GlobalColor.black)
        self.update_count()
    
    def remove_item(self, item: QListWidgetItem):
        self.list.takeItem(self.list.row(item))
        self.update_count()
    
    def clear_done(self):
        for i in range(self.list.count() - 1, -1, -1):
            item = self.list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.list.takeItem(i)
        self.update_count()
    
    def update_count(self):
        total = self.list.count()
        done = sum(
            1 for i in range(total)
            if self.list.item(i).checkState() == Qt.CheckState.Checked
        )
        self.lbl_count.setText(f"Tổng: {total} | Xong: {done}")


app = QApplication(sys.argv)
w = TodoList()
w.show()
sys.exit(app.exec())
```

**Lưu ý**: Cần `from PySide6.QtWidgets import QLabel` (đã thiếu trong import trên).

### 2.8. `setItemWidget()` – Nhúng widget vào item

Cực mạnh: bạn có thể nhúng **bất kỳ widget nào** vào item.

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

lst = QListWidget()

for i in range(3):
    item = QListWidgetItem()
    item.setSizeHint(QSize(0, 50))           # Cần set sizeHint
    
    # Tạo widget
    widget = QWidget()
    h = QHBoxLayout(widget)
    h.setContentsMargins(5, 5, 5, 5)
    
    h.addWidget(QLabel(f"Item {i+1}"))
    h.addStretch()
    h.addWidget(QPushButton("Edit"))
    h.addWidget(QPushButton("Delete"))
    
    # Nhúng
    lst.addItem(item)
    lst.setItemWidget(item, widget)
```

⚠️ **Quan trọng**: **PHẢI** `setSizeHint()` cho item, nếu không widget hiển thị 0px.

⚠️ **Lưu ý**: Widget trong `setItemWidget` **không** tự resize theo item. Nếu item thay đổi size, bạn phải update thủ công.

### 2.9. Drag & Drop item

```python
lst.setDragEnabled(True)                            # Cho kéo
lst.setAcceptDrops(True)                            # Cho thả
lst.setDropIndicatorShown(True)
lst.setDragDropMode(QListWidget.DragDropMode.InternalMove)   # Chỉ trong list
lst.setDefaultDropAction(Qt.DropAction.MoveAction)
```

`InternalMove`: cho user kéo item **trong cùng list** để đổi thứ tự.

---

## 🎯 PHẦN 3: QTREEWIDGET

### 3.1. Cấu trúc cây

```
QTreeWidget
├── QTreeWidgetItem (root 1)
│   ├── QTreeWidgetItem (child)
│   │   └── QTreeWidgetItem (grandchild)
│   └── QTreeWidgetItem (child)
└── QTreeWidgetItem (root 2)
```

### 3.2. Tạo cây

```python
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

tree = QTreeWidget()
tree.setHeaderLabels(["Tên", "Kích thước", "Ngày sửa"])   # Nhiều cột

# Root item
root = QTreeWidgetItem(tree, ["Documents", "", ""])

# Child của root
child1 = QTreeWidgetItem(root, ["file1.txt", "10 KB", "2025-01-01"])
child2 = QTreeWidgetItem(root, ["file2.py", "25 KB", "2025-01-02"])

# Root khác
root2 = QTreeWidgetItem(tree, ["Pictures", "", ""])
child3 = QTreeWidgetItem(root2, ["photo.jpg", "2 MB", ""])

# Expand
tree.expandAll()
```

### 3.3. QTreeWidgetItem – chi tiết

```python
item = QTreeWidgetItem()

# Set text cho từng cột
item.setText(0, "Name")
item.setText(1, "Size")

# Data ẩn
item.setData(0, Qt.ItemDataRole.UserRole, "/path/to/file")

# Icon
item.setIcon(0, QIcon("folder.png"))

# Checkbox cho cột 0
item.setCheckState(0, Qt.CheckState.Checked)

# Font/màu cho từng cột
item.setForeground(0, QColor("red"))
font = QFont()
font.setBold(True)
item.setFont(0, font)
```

### 3.4. Method của QTreeWidgetItem

```python
# Con
item.addChild(child_item)
item.insertChild(index, child)
item.removeChild(child)
item.takeChild(index)
item.childCount()
item.child(i)
item.children()

# Cha
item.parent()                                # None nếu là root

# Vị trí trong tree
tree.indexOfTopLevelItem(item)
tree.indexOfTopLevelItem(item)               # -1 nếu không phải root

# Trạng thái
item.isExpanded()
item.setExpanded(True)
item.isSelected()
item.setSelected(True)
item.isHidden()
item.setHidden(True)
```

### 3.5. Signals của QTreeWidget

```python
tree.itemClicked.connect(self.on_click)             # (item, col)
tree.itemDoubleClicked.connect(self.on_double)
tree.itemExpanded.connect(self.on_expand)           # Khi mở rộng
tree.itemCollapsed.connect(self.on_collapse)        # Khi thu gọn
tree.itemSelectionChanged.connect(self.on_selection)
tree.itemChanged.connect(self.on_changed)           # Text/check đổi
tree.currentItemChanged.connect(self.on_current)
```

### 3.6. Properties của QTreeWidget

```python
tree.setColumnCount(3)
tree.setHeaderLabels(["Name", "Size", "Date"])

tree.setColumnWidth(0, 200)
tree.header().setStretchLastSection(True)           # Cột cuối co giãn
tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

tree.setRootIsDecorated(True)                       # Hiện mũi tên expand
tree.setAlternatingRowColors(True)                  # Kẻ sọc
tree.setAnimated(True)                              # Animation expand
tree.setIndentation(20)                             # Số px thụt lề

tree.setSortingEnabled(True)
tree.sortItems(0, Qt.SortOrder.AscendingOrder)
```

### 3.7. Ví dụ – File tree

```python
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)


class FileTree(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Tree")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.tree)
        
        # Load từ thư mục home
        home = Path.home()
        self._populate(self.tree.invisibleRootItem(), home, depth=0, max_depth=2)
        self.tree.expandToDepth(1)
    
    def _populate(self, parent_item, path: Path, depth: int, max_depth: int):
        if depth > max_depth:
            return
        
        try:
            entries = sorted(
                path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            return
        
        for entry in entries:
            if entry.name.startswith("."):
                continue                          # Bỏ file ẩn
            
            if entry.is_dir():
                item = QTreeWidgetItem(parent_item, [entry.name, "Folder", ""])
                item.setIcon(0, QIcon.fromTheme("folder"))
                item.setData(0, Qt.ItemDataRole.UserRole, str(entry))
                
                # Đệ quy
                self._populate(item, entry, depth + 1, max_depth)
                
                # Nếu không có child → thêm dummy để hiện mũi tên expand
                if item.childCount() == 0:
                    QTreeWidgetItem(item, ["(empty)", "", ""])
            else:
                try:
                    size = entry.stat().st_size
                    size_str = self._format_size(size)
                except OSError:
                    size_str = "?"
                
                item = QTreeWidgetItem(parent_item, [entry.name, "File", size_str])
                item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                item.setData(0, Qt.ItemDataRole.UserRole, str(entry))
    
    def _format_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def on_double_click(self, item: QTreeWidgetItem, col: int):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            print(f"Double click: {path}")


app = QApplication(sys.argv)
w = FileTree()
w.show()
sys.exit(app.exec())
```

### 3.8. Lazy loading – Load khi expand

Thay vì load hết cả cây (chậm), load khi user expand:

```python
self.tree.itemExpanded.connect(self._on_expand)

def _on_expand(self, item: QTreeWidgetItem):
    # Nếu item chưa được populate
    if item.data(0, Qt.ItemDataRole.UserRole + 1) == "loaded":
        return
    
    path_str = item.data(0, Qt.ItemDataRole.UserRole)
    if not path_str:
        return
    
    path = Path(path_str)
    
    # Xóa dummy
    item.takeChildren()
    
    # Populate
    try:
        for entry in path.iterdir():
            if entry.name.startswith("."):
                continue
            
            child = QTreeWidgetItem(item, [entry.name, ...])
            child.setData(0, Qt.ItemDataRole.UserRole, str(entry))
            
            if entry.is_dir():
                # Thêm dummy để có mũi tên
                QTreeWidgetItem(child, ["loading...", "", ""])
    except PermissionError:
        pass
    
    item.setData(0, Qt.ItemDataRole.UserRole + 1, "loaded")
```

---

## 🎯 PHẦN 4: QTABLEWIDGET

### 4.1. Cấu trúc bảng

```
        Col 0       Col 1       Col 2
       ┌───────────┬───────────┬───────────┐
Row 0  │ cell(0,0) │ cell(0,1) │ cell(0,2) │
       ├───────────┼───────────┼───────────┤
Row 1  │ cell(1,0) │ cell(1,1) │ cell(1,2) │
       └───────────┴───────────┴───────────┘
```

### 4.2. Tạo bảng cơ bản

```python
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

table = QTableWidget()

# Setup kích thước
table.setRowCount(5)
table.setColumnCount(3)

# Header
table.setHorizontalHeaderLabels(["Name", "Age", "City"])

# Thêm item
table.setItem(0, 0, QTableWidgetItem("An"))
table.setItem(0, 1, QTableWidgetItem("25"))
table.setItem(0, 2, QTableWidgetItem("Hà Nội"))
```

### 4.3. QTableWidgetItem – chi tiết

```python
item = QTableWidgetItem("Hello")

# Data ẩn
item.setData(Qt.ItemDataRole.UserRole, {"id": 123})

# Sắp xếp số đúng cách (mặc định Qt sort theo string!)
item.setData(Qt.ItemDataRole.DisplayRole, 100)   # Qt hiển thị "100"
# Hoặc:
class NumericItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return int(self.text()) < int(other.text())
        except ValueError:
            return super().__lt__(other)

# Flags
item.setFlags(
    Qt.ItemFlag.ItemIsEnabled |
    Qt.ItemFlag.ItemIsSelectable |
    Qt.ItemFlag.ItemIsEditable
)

# Alignment
item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

# Màu
item.setBackground(QColor("#ffffcc"))
item.setForeground(QColor("red"))

# Icon
item.setIcon(QIcon("star.png"))
```

### 4.4. Method QTableWidget

```python
# Thêm/xóa hàng/cột
table.insertRow(2)
table.removeRow(0)
table.insertColumn(1)
table.removeColumn(0)
table.clear()                                       # Xóa hết data
table.clearContents()                               # Xóa content, giữ hàng/cột

# Truy cập
item = table.item(row, col)
table.setItem(row, col, item)
table.takeItem(row, col)                            # Lấy ra khỏi bảng

# Kích thước
table.rowCount()
table.columnCount()

# Chọn
table.setCurrentCell(row, col)
table.currentRow()
table.currentColumn()
table.selectedItems()
table.selectedRanges()

# Header
table.setHorizontalHeaderItem(col, item)            # Header riêng
table.horizontalHeaderItem(col)
table.setVerticalHeaderLabels(["A", "B", "C"])

# Cột/hàng ẩn
table.setColumnHidden(2, True)
table.setRowHidden(0, True)
```

### 4.5. Signals

```python
table.cellClicked.connect(self.on_cell_click)       # (row, col)
table.cellDoubleClicked.connect(self.on_double)
table.cellChanged.connect(self.on_cell_change)      # (row, col) - khi nội dung đổi
table.cellActivated.connect(self.on_activate)       # Enter
table.itemSelectionChanged.connect(self.on_sel)
table.currentCellChanged.connect(self.on_current)   # (row, col, prev_row, prev_col)
```

### 4.6. Properties

```python
table.setShowGrid(True)
table.setAlternatingRowColors(True)
table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)   # Chọn cả hàng
table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

# Sửa
table.setEditTriggers(
    QAbstractItemView.EditTrigger.DoubleClicked |
    QAbstractItemView.EditTrigger.EditKeyPressed
)

# Header
table.horizontalHeader().setStretchLastSection(True)
table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

# Sort
table.setSortingEnabled(True)

# Row height
table.verticalHeader().setDefaultSectionSize(30)
```

### 4.7. Ví dụ – Bảng quản lý sinh viên

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QHeaderView, QAbstractItemView, QMessageBox
)


class StudentTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý sinh viên")
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # ===== Input row =====
        input_row = QHBoxLayout()
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Họ tên")
        self.txt_age = QLineEdit()
        self.txt_age.setPlaceholderText("Tuổi")
        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Thành phố")
        
        btn_add = QPushButton("Thêm")
        btn_add.clicked.connect(self.add_student)
        
        input_row.addWidget(self.txt_name, 2)
        input_row.addWidget(self.txt_age, 1)
        input_row.addWidget(self.txt_city, 2)
        input_row.addWidget(btn_add)
        layout.addLayout(input_row)
        
        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Họ tên", "Tuổi", "Thành phố"])
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)
        
        # ===== Buttons row =====
        btn_row = QHBoxLayout()
        
        btn_delete = QPushButton("Xóa hàng được chọn")
        btn_delete.clicked.connect(self.delete_selected)
        
        btn_clear = QPushButton("Xóa hết")
        btn_clear.clicked.connect(self.clear_all)
        
        btn_row.addWidget(btn_delete)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        
        self.lbl_count = QLabel()
        btn_row.addWidget(self.lbl_count)
        
        layout.addLayout(btn_row)
        
        # Thêm vài row demo
        self._add_row("Nguyễn Văn An", 25, "Hà Nội")
        self._add_row("Trần Thị Bình", 22, "TP.HCM")
        self._add_row("Lê Văn Cường", 30, "Đà Nẵng")
        
        self.update_count()
    
    def add_student(self):
        name = self.txt_name.text().strip()
        age_str = self.txt_age.text().strip()
        city = self.txt_city.text().strip()
        
        if not name or not age_str:
            QMessageBox.warning(self, "Thiếu", "Nhập tên và tuổi")
            return
        
        try:
            age = int(age_str)
        except ValueError:
            QMessageBox.warning(self, "Sai", "Tuổi phải là số")
            return
        
        self._add_row(name, age, city)
        
        self.txt_name.clear()
        self.txt_age.clear()
        self.txt_city.clear()
        self.txt_name.setFocus()
        self.update_count()
    
    def _add_row(self, name: str, age: int, city: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Tạo item cho từng cột
        name_item = QTableWidgetItem(name)
        name_item.setData(Qt.ItemDataRole.UserRole, {"created": "..."})
        self.table.setItem(row, 0, name_item)
        
        # Numeric item cho cột tuổi (để sort đúng)
        age_item = NumericTableItem(str(age))
        age_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.table.setItem(row, 1, age_item)
        
        self.table.setItem(row, 2, QTableWidgetItem(city))
    
    def delete_selected(self):
        rows = sorted(
            set(index.row() for index in self.table.selectedIndexes()),
            reverse=True
        )
        for row in rows:
            self.table.removeRow(row)
        self.update_count()
    
    def clear_all(self):
        reply = QMessageBox.question(
            self, "Xác nhận", "Xóa tất cả sinh viên?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.update_count()
    
    def on_cell_changed(self, row: int, col: int):
        print(f"Cell ({row}, {col}) changed")
    
    def update_count(self):
        self.lbl_count.setText(f"Tổng: {self.table.rowCount()}")


class NumericTableItem(QTableWidgetItem):
    """Item so sánh theo số thay vì string."""
    def __lt__(self, other):
        try:
            return int(self.text()) < int(other.text())
        except ValueError:
            return super().__lt__(other)


app = QApplication(sys.argv)
w = StudentTable()
w.show()
sys.exit(app.exec())
```

### 4.8. `setCellWidget()` – Nhúng widget vào cell

Tương tự QListWidget:

```python
from PySide6.QtWidgets import QComboBox, QPushButton, QHBoxLayout

# Combo box trong cell
combo = QComboBox()
combo.addItems(["Active", "Inactive", "Pending"])
combo.currentTextChanged.connect(lambda t, r=row: self.on_status_change(r, t))
table.setCellWidget(row, 3, combo)

# Nút trong cell
btn = QPushButton("Delete")
btn.clicked.connect(lambda _, r=row: self.delete_row(r))
table.setCellWidget(row, 4, btn)
```

⚠️ **Quan trọng**: `cellWidget` **không tự động** di chuyển khi sort. Bạn phải xử lý `cellChanged` hoặc dùng Model/View.

---

## 🎯 PHẦN 5: THỰC HÀNH – FILE EXPLORER

### 5.1. Yêu cầu

- **Cây thư mục** (QTreeWidget) bên trái
- **List file** (QListWidget) bên phải
- Dùng **QSplitter** chia 2 panel
- Double click folder trong list → đi vào
- Breadcrumb path ở trên
- Nút Back, Up
- Hiển thị icon theo loại file

### 5.2. Code đầy đủ

Tạo file `file_explorer.py`:

```python
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QLabel, QFileIconProvider, QToolBar,
    QMessageBox, QHeaderView
)


# ============================================================
# FILE ICON PROVIDER
# ============================================================
class IconProvider:
    def __init__(self):
        self.provider = QFileIconProvider()
    
    def icon_for(self, path: Path) -> QIcon:
        if path.is_dir():
            return QIcon.fromTheme("folder", self.provider.icon(QFileIconProvider.IconType.Folder))
        return self.provider.icon(QFileIconProvider.IconType.File)


# ============================================================
# FILE LIST
# ============================================================
class FileList(QListWidget):
    def __init__(self):
        super().__init__()
        
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(48, 48))
        self.setGridSize(QSize(110, 90))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setSpacing(5)
        self.setWordWrap(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setUniformItemSizes(True)
        
        self._icon_provider = IconProvider()
    
    def load_directory(self, path: Path):
        self.clear()
        
        if not path.exists() or not path.is_dir():
            return
        
        try:
            entries = sorted(
                path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            return
        
        for entry in entries:
            if entry.name.startswith("."):
                continue
            
            item = QListWidgetItem(entry.name)
            item.setIcon(self._icon_provider.icon_for(entry))
            item.setData(Qt.ItemDataRole.UserRole, str(entry))
            item.setToolTip(str(entry))
            
            if entry.is_dir():
                item.setForeground(Qt.GlobalColor.darkBlue)
            
            self.addItem(item)
    
    def selected_path(self) -> Path | None:
        item = self.currentItem()
        if not item:
            return None
        path_str = item.data(Qt.ItemDataRole.UserRole)
        return Path(path_str) if path_str else None


# ============================================================
# FOLDER TREE
# ============================================================
class FolderTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(15)
        self.setDragEnabled(False)
        
        self._icon_provider = IconProvider()
        self._loaded: set[str] = set()        # Paths đã load
    
    def load_root(self, path: Path):
        self.clear()
        self._loaded.clear()
        
        root_item = self._make_item(path)
        self.addTopLevelItem(root_item)
        self._populate(root_item, path)
        root_item.setExpanded(True)
    
    def _make_item(self, path: Path) -> QTreeWidgetItem:
        item = QTreeWidgetItem([path.name or str(path)])
        item.setIcon(0, self._icon_provider.icon_for(path))
        item.setData(0, Qt.ItemDataRole.UserRole, str(path))
        
        # Nếu là folder, thêm dummy để hiện mũi tên expand
        if path.is_dir():
            QTreeWidgetItem(item, ["Loading..."])
        
        return item
    
    def _populate(self, parent: QTreeWidgetItem, path: Path):
        # Xóa dummy
        parent.takeChildren()
        
        try:
            entries = sorted(
                [p for p in path.iterdir()
                 if p.is_dir() and not p.name.startswith(".")],
                key=lambda p: p.name.lower()
            )
        except PermissionError:
            return
        
        for entry in entries:
            child = self._make_item(entry)
            parent.addChild(child)
        
        self._loaded.add(str(path))
    
    def itemExpanded(self, item: QTreeWidgetItem):
        super().itemExpanded(item)
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if not path_str or path_str in self._loaded:
            return
        
        path = Path(path_str)
        if path.is_dir():
            self._populate(item, path)


# ============================================================
# MAIN WINDOW
# ============================================================
class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.resize(1000, 700)
        
        self.current_path = Path.home()
        self.history: list[Path] = []
        
        self._setup_ui()
        self._setup_actions()
        self._setup_toolbar()
        self._setup_statusbar()
        
        # Load home
        self.navigate_to(Path.home())
    
    # ----------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # ===== Breadcrumb / nav bar =====
        nav_row = QHBoxLayout()
        
        self.btn_back = QPushButton("◀")
        self.btn_back.setFixedSize(32, 32)
        self.btn_back.setToolTip("Quay lại (Alt+Left)")
        self.btn_back.clicked.connect(self.go_back)
        
        self.btn_up = QPushButton("▲")
        self.btn_up.setFixedSize(32, 32)
        self.btn_up.setToolTip("Lên thư mục cha (Alt+Up)")
        self.btn_up.clicked.connect(self.go_up)
        
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(32, 32)
        self.btn_home.setToolTip("Home")
        self.btn_home.clicked.connect(lambda: self.navigate_to(Path.home()))
        
        self.txt_path = QLineEdit()
        self.txt_path.setReadOnly(True)
        self.txt_path.setStyleSheet(
            "QLineEdit { background: #f5f5f5; padding: 6px 10px; "
            "border-radius: 4px; font-family: monospace; }"
        )
        
        nav_row.addWidget(self.btn_back)
        nav_row.addWidget(self.btn_up)
        nav_row.addWidget(self.btn_home)
        nav_row.addWidget(self.txt_path, 1)
        
        layout.addLayout(nav_row)
        
        # ===== Splitter: tree | list =====
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: tree
        self.tree = FolderTree()
        self.tree.setMinimumWidth(180)
        self.tree.itemClicked.connect(self._on_tree_clicked)
        self.tree.itemActivated.connect(self._on_tree_clicked)
        splitter.addWidget(self.tree)
        
        # Right: list
        self.file_list = FileList()
        self.file_list.itemDoubleClicked.connect(self._on_list_double_click)
        splitter.addWidget(self.file_list)
        
        splitter.setSizes([250, 750])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter, 1)
    
    # ----------------------------------------------------------
    def _setup_actions(self):
        self.act_back = QAction("Back", self)
        self.act_back.setShortcut("Alt+Left")
        self.act_back.triggered.connect(self.go_back)
        
        self.act_up = QAction("Up", self)
        self.act_up.setShortcut("Alt+Up")
        self.act_up.triggered.connect(self.go_up)
        
        self.act_home = QAction("Home", self)
        self.act_home.setShortcut("Alt+Home")
        self.act_home.triggered.connect(lambda: self.navigate_to(Path.home()))
        
        self.act_refresh = QAction("🔄 Refresh", self)
        self.act_refresh.setShortcut(QKeySequence.StandardKey.Refresh)
        self.act_refresh.triggered.connect(lambda: self.load_directory(self.current_path))
        
        self.act_exit = QAction("Thoát", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)
        
        # Menu
        mb = self.menuBar()
        nm = mb.addMenu("&Navigate")
        nm.addAction(self.act_back)
        nm.addAction(self.act_up)
        nm.addAction(self.act_home)
        nm.addSeparator()
        nm.addAction(self.act_refresh)
        nm.addSeparator()
        nm.addAction(self.act_exit)
    
    # ----------------------------------------------------------
    def _setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        
        tb.addAction(self.act_back)
        tb.addAction(self.act_up)
        tb.addAction(self.act_home)
        tb.addSeparator()
        tb.addAction(self.act_refresh)
    
    # ----------------------------------------------------------
    def _setup_statusbar(self):
        self.lbl_status = QLabel()
        self.statusBar().addPermanentWidget(self.lbl_status)
        self.statusBar().showMessage("Sẵn sàng")
    
    # ----------------------------------------------------------
    def navigate_to(self, path: Path, push_history: bool = True):
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(self, "Lỗi", f"Không truy cập được:\n{path}")
            return
        
        if push_history and self.current_path != path:
            self.history.append(self.current_path)
        
        self.current_path = path
        self.load_directory(path)
    
    def load_directory(self, path: Path):
        self.file_list.load_directory(path)
        self.txt_path.setText(str(path))
        self.btn_back.setEnabled(bool(self.history))
        
        # Đếm số mục
        count = self.file_list.count()
        self.lbl_status.setText(f"{count} mục")
        self.statusBar().showMessage(f"Đang xem: {path}", 2000)
    
    # ----------------------------------------------------------
    def go_back(self):
        if not self.history:
            return
        path = self.history.pop()
        self.navigate_to(path, push_history=False)
    
    def go_up(self):
        parent = self.current_path.parent
        if parent != self.current_path:
            self.navigate_to(parent)
    
    # ----------------------------------------------------------
    def _on_list_double_click(self, item: QListWidgetItem):
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str:
            return
        
        path = Path(path_str)
        if path.is_dir():
            self.navigate_to(path)
        elif path.is_file():
            self.statusBar().showMessage(f"File: {path.name}", 3000)
    
    def _on_tree_clicked(self, item: QTreeWidgetItem, col: int):
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if path_str:
            self.navigate_to(Path(path_str))


# ============================================================
def main():
    app = QApplication(sys.argv)
    w = FileExplorer()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 5.3. Điểm đáng chú ý

1. **`IconProvider`**: class riêng cho icon, dùng `QFileIconProvider` (icon hệ thống)
2. **`FolderTree` lazy loading**: chỉ populate khi expand
3. **Dummy child `"Loading..."`**: để hiện mũi tên expand
4. **`FileList` view mode `IconMode`**: hiển thị dạng lưới icon
5. **`setUniformItemSizes(True)`**: tối ưu performance
6. **`history` list**: quản lý back navigation
7. **`navigate_to(path, push_history=True)`**: pattern hay, tránh vòng lặp history
8. **`Alt+Left`, `Alt+Up`**: shortcut chuẩn cho navigation
9. **`QAction` cho toolbar + menu**: tái sử dụng
10. **2 chiều đồng bộ**: tree click → list load, list double click folder → tree/list cùng update

### 5.4. Test cases

| Test | Hành động | Kỳ vọng |
|------|-----------|---------|
| Navigate | Double click folder | Đi vào folder đó |
| Back | Alt+Left | Quay lại folder trước |
| Up | Alt+Up | Lên folder cha |
| Home | 🏠 | Về thư mục home |
| Tree click | Click folder trên tree | List load folder đó |
| Refresh | F5 | Load lại folder hiện tại |
| File double click | Double click file | Hiển thị status message |

---

## 📝 BÀI TẬP

### Bài tập 4.2.1 (Cơ bản)
Mở rộng Todo List:
- Lưu/đọc từ file JSON khi mở/đóng app
- Sort task: chưa xong lên đầu, đã xong xuống cuối
- Filter: All / Active / Done (dùng QComboBox)

### Bài tập 4.2.2 (Trung bình)
Làm **QTreeWidget** hiển thị **process tree** (task manager mini):
- Root: Process ID
- Child: Tên process, CPU, RAM
- Dùng `psutil` để lấy dữ liệu
- Double click → hiện dialog chi tiết

### Bài tập 4.2.3 (Khá)
Làm **QTableWidget** với các tính năng:
- Sort theo cột (click header)
- Filter theo text
- Cell edit với validation (dùng `cellChanged`)
- Cột "Status" có `QComboBox` (dùng `setCellWidget`)

### Bài tập 4.2.4 (Nâng cao)
Làm **Multi-column tree** với checkbox 3 trạng thái:
- Cột 1: Tên (có checkbox)
- Cột 2: Mô tả
- Check parent → check tất cả con
- Check 1 vài con → parent thành `PartiallyChecked`
- Ngược lại, check parent → propagate xuống

💡 Gợi ý: `Qt.CheckState.PartiallyChecked`, override `itemChanged`.

### Bài tập 4.2.5 (Khó)
**Drag & Drop giữa các widget**:
- List A: "Available"
- List B: "Selected"
- Kéo item từ A sang B và ngược lại
- Double click item → chuyển list
- Lưu trạng thái khi đóng app

---

## ✅ CHECKLIST SAU BÀI 4.2

- [ ] Biết tạo và quản lý `QListWidget`
- [ ] Hiểu **data role** – lưu dữ liệu ẩn trong item
- [ ] Biết `QListWidgetItem` properties: text, icon, check, font, color
- [ ] Biết `setItemWidget()` nhúng widget vào item
- [ ] Biết drag & drop internal move
- [ ] Nắm `QTreeWidget`: root, child, parent
- [ ] Biết lazy loading với dummy child
- [ ] Biết `setHeaderLabels` cho multi-column tree
- [ ] Thành thạo `QTableWidget`: hàng, cột, cell
- [ ] Biết `NumericTableItem` để sort số đúng
- [ ] Biết `setCellWidget` nhúng widget vào cell
- [ ] Biết `header().setSectionResizeMode` cho cột stretch
- [ ] Hoàn thành File Explorer + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 4.3 – QDockWidget & QToolBox**

- `QDockWidget` – panel có thể dock vào cạnh cửa sổ
- Kéo dock ra thành cửa sổ nổi
- `QToolBox` – accordion nhiều mục
- `QMainWindow` với nhiều dock
- Build **IDE mini** với 3-4 dock panels

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 4.3 – QDockWidget & QToolBox**?
2. **Giải chi tiết một bài tập 4.2.x** nào?
3. **Đào sâu** phần nào (setItemWidget nâng cao, custom item, drag & drop)?

Bạn cũng có thể gửi code bạn viết để tôi review! 🚀