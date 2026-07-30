## Bài 6: QMainWindow — Menu, Toolbar, StatusBar & Cấu Trúc Cửa Sổ Chuyên Nghiệp

### 1. Động lực (Motivation)

Từ Bài 1 đến Bài 5, chúng ta luôn dùng `QWidget` làm cửa sổ gốc — điều này phù hợp cho form đơn giản, dialog, hoặc widget con. Nhưng **mọi ứng dụng desktop chuyên nghiệp thực thụ** — từ VS Code, Photoshop, đến các công cụ nội bộ tại ngân hàng số hay sàn TMĐT — đều dùng một cấu trúc cửa sổ chuẩn có: **thanh menu** (File, Edit, Help...), **thanh công cụ** (toolbar với icon), **thanh trạng thái** (status bar hiển thị thông tin ngắn ở đáy), và **vùng nội dung trung tâm**. Qt cung cấp sẵn class chuyên biệt cho việc này: **`QMainWindow`**.

Đây là bước ngoặt quan trọng: từ giờ, mọi ứng dụng "thật" bạn xây dựng trong khóa học này (kể cả project cuối) sẽ dùng `QMainWindow` làm nền, không còn `QWidget` trần nữa. Tkinter không có khái niệm tương đương sẵn có ở tầm này — bạn phải tự dựng `Menu`, `Frame` làm toolbar thủ công. Đây là một trong những lý do lớn nhất khiến Qt được chọn cho phần mềm desktop chuyên nghiệp: cấu trúc chuẩn hóa, tiết kiệm thời gian.

### 2. Giải thích khái niệm

#### 2.1. Cấu trúc `QMainWindow`

`QMainWindow` có bố cục cố định gồm 5 vùng:

```
┌─────────────────────────────────────┐
│              Menu Bar                │
├─────────────────────────────────────┤
│              Toolbar                  │
├─────────────────────────────────────┤
│                                        │
│          Central Widget               │  ← Vùng nội dung chính
│                                        │
├─────────────────────────────────────┤
│              Status Bar               │
└─────────────────────────────────────┘
```

**Nguyên tắc quan trọng nhất:** `QMainWindow` **không** cho `setLayout()` trực tiếp như `QWidget`. Bạn phải tạo 1 `QWidget` riêng làm "vùng trung tâm", set layout lên nó, rồi gọi `setCentralWidget()`:

python

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LearnHub Desktop - QMainWindow")
        self.resize(700, 500)

        # Bước 1: Tạo widget trung tâm
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel("Đây là vùng nội dung chính"))

        # Bước 2: Gán làm vùng trung tâm của QMainWindow
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Lỗi phổ biến nhất khi mới chuyển từ `QWidget` sang `QMainWindow`:**

python

```python
self.setLayout(layout)   # ❌ AttributeError - QMainWindow không có setLayout()
```

#### 2.2. Menu Bar — Thanh menu

python

```python
def _setup_menu(self):
    menu_bar = self.menuBar()          # QMainWindow tự có sẵn menu bar, chỉ cần gọi ra

    file_menu = menu_bar.addMenu("&File")     # dấu & tạo phím tắt Alt+F
    new_action = file_menu.addAction("Tạo mới")
    open_action = file_menu.addAction("Mở file...")
    file_menu.addSeparator()                   # Đường kẻ ngăn cách
    exit_action = file_menu.addAction("Thoát")

    # Kết nối signal - QAction cũng có signal triggered
    new_action.triggered.connect(self._handle_new)
    exit_action.triggered.connect(self.close)   # self.close() có sẵn, đóng cửa sổ

    edit_menu = menu_bar.addMenu("&Edit")
    edit_menu.addAction("Sao chép")
    edit_menu.addAction("Dán")
```

**Khái niệm cốt lõi: `QAction`** — đại diện cho "một hành động" (mở file, lưu, thoát...) — có thể gắn vào **nhiều nơi cùng lúc** (menu, toolbar, phím tắt) mà chỉ cần định nghĩa **1 lần**. Đây là điểm khác biệt lớn so với việc tự tạo `Menu` trong Tkinter, nơi bạn phải viết `command=` riêng cho từng nơi xuất hiện.

python

```python
from PySide6.QtGui import QAction, QKeySequence

save_action = QAction("Lưu", self)
save_action.setShortcut(QKeySequence("Ctrl+S"))   # Gán phím tắt
save_action.setStatusTip("Lưu dữ liệu hiện tại")   # Hiện ở status bar khi hover
save_action.triggered.connect(self._handle_save)

file_menu.addAction(save_action)     # Gắn vào menu
toolbar.addAction(save_action)       # CÙNG action đó, gắn thêm vào toolbar
```

#### 2.3. Toolbar — Thanh công cụ

python

```python
def _setup_toolbar(self):
    toolbar = self.addToolBar("Công cụ chính")
    toolbar.setMovable(False)   # Không cho kéo thả toolbar (mặc định Qt cho phép kéo!)

    toolbar.addAction(self.save_action)
    toolbar.addSeparator()
    toolbar.addAction(self.refresh_action)
```

Toolbar còn hỗ trợ icon thực thụ (không chỉ text) — dùng `QIcon`:

python

```python
from PySide6.QtGui import QIcon

save_action.setIcon(QIcon("icons/save.png"))
```

#### 2.4. Status Bar — Thanh trạng thái

python

```python
def _setup_statusbar(self):
    self.status_bar = self.statusBar()      # Tự động tạo nếu chưa có
    self.status_bar.showMessage("Sẵn sàng", 3000)   # Hiện 3000ms rồi tự ẩn

    # Thêm widget cố định bên phải status bar (VD: hiển thị user đang đăng nhập)
    from PySide6.QtWidgets import QLabel
    self.user_label = QLabel("👤 Nhân viên: NV-1024")
    self.status_bar.addPermanentWidget(self.user_label)
```

`showMessage(text, timeout)` — nếu `timeout=0` (mặc định), thông báo hiển thị **vĩnh viễn** cho đến khi bị thay bằng thông báo khác.

#### 2.5. Dialog cảnh báo/xác nhận — `QMessageBox`

Khi làm menu "Thoát" hay "Xóa dữ liệu", ta cần hỏi xác nhận — dùng `QMessageBox`, tương đương `messagebox` của Tkinter nhưng API rõ ràng hơn:

python

```python
from PySide6.QtWidgets import QMessageBox

def _handle_exit_request(self):
    reply = QMessageBox.question(
        self,
        "Xác nhận thoát",
        "Bạn có chắc muốn thoát ứng dụng?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No   # Nút mặc định được highlight
    )
    if reply == QMessageBox.Yes:
        self.close()
```

### 3. Ví dụ thực tế 2026: Ứng dụng Quản lý Đơn hàng nội bộ (Internal Order Management Tool)

Mô phỏng công cụ nội bộ dạng dùng ở kho vận Tiki/Shopee Logistics — kết hợp toàn bộ Menu/Toolbar/StatusBar:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QListWidget, QMessageBox
)
from PySide6.QtGui import QAction, QKeySequence

class OrderManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Management Tool - Kho vận nội bộ v2.1")
        self.resize(750, 500)

        self._order_count = 12   # Dữ liệu giả lập

        self._setup_central_widget()
        self._setup_actions()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()

    def _setup_central_widget(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        self.title_label = QLabel(f"📦 Đơn hàng đang xử lý: {self._order_count}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        layout.addWidget(self.title_label)

        self.order_list = QListWidget()
        self.order_list.addItems([
            f"DH-{10000 + i} — Chờ đóng gói" for i in range(1, self._order_count + 1)
        ])
        layout.addWidget(self.order_list)

        self.setCentralWidget(central)

    def _setup_actions(self):
        # QAction định nghĩa 1 lần, dùng lại ở cả menu và toolbar
        self.refresh_action = QAction("🔄 Làm mới", self)
        self.refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        self.refresh_action.setStatusTip("Tải lại danh sách đơn hàng từ server")
        self.refresh_action.triggered.connect(self._handle_refresh)

        self.delete_action = QAction("🗑️ Xóa đơn đã chọn", self)
        self.delete_action.setStatusTip("Xóa đơn hàng đang được chọn")
        self.delete_action.triggered.connect(self._handle_delete)

        self.exit_action = QAction("Thoát", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self._handle_exit_request)

    def _setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Tệp")
        file_menu.addAction(self.refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        order_menu = menu_bar.addMenu("&Đơn hàng")
        order_menu.addAction(self.delete_action)

    def _setup_toolbar(self):
        toolbar = self.addToolBar("Công cụ chính")
        toolbar.setMovable(False)
        toolbar.addAction(self.refresh_action)
        toolbar.addAction(self.delete_action)

    def _setup_statusbar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sẵn sàng", 3000)

        self.user_label = QLabel("👤 NV-1024 | Kho HCM-01")
        self.status_bar.addPermanentWidget(self.user_label)

    def _handle_refresh(self):
        self.status_bar.showMessage("Đã tải lại danh sách đơn hàng", 2000)

    def _handle_delete(self):
        current = self.order_list.currentItem()
        if not current:
            self.status_bar.showMessage("⚠️ Chưa chọn đơn hàng nào để xóa", 3000)
            return

        row = self.order_list.currentRow()
        self.order_list.takeItem(row)
        self._order_count -= 1
        self.title_label.setText(f"📦 Đơn hàng đang xử lý: {self._order_count}")
        self.status_bar.showMessage(f"Đã xóa: {current.text()}", 3000)

    def _handle_exit_request(self):
        reply = QMessageBox.question(
            self, "Xác nhận thoát",
            "Bạn có chắc muốn thoát ứng dụng?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderManagementApp()
    window.show()
    sys.exit(app.exec())
```

**Điểm thiết kế đáng học:** Tách `_setup_actions()` riêng khỏi `_setup_menu()` và `_setup_toolbar()` — đây là pattern chuẩn trong code Qt chuyên nghiệp, giúp 1 `QAction` tái sử dụng ở nhiều nơi (menu + toolbar + phím tắt) mà không lặp code, đúng nguyên tắc **DRY (Don't Repeat Yourself)**.

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Gọi `setLayout()` trực tiếp trên `QMainWindow`:**

python

```python
self.setLayout(layout)   # ❌ AttributeError
```

→ Phải tạo `QWidget` trung tâm và dùng `setCentralWidget()`.

**Lỗi 2 — Quên `self` khi tạo `QAction`:**

python

```python
action = QAction("Lưu")        # ⚠️ Thiếu parent, có thể bị Python garbage-collect sớm
action = QAction("Lưu", self)  # ✅ Đúng - self làm "cha" quản lý vòng đời của action
```

Đây là lỗi khó phát hiện: action "biến mất" không rõ lý do vì không có tham chiếu giữ nó sống.

**Lỗi 3 — Gọi `setCentralWidget()` nhiều lần với các widget khác nhau:** Chỉ widget **cuối cùng** được set mới hiển thị, các lần trước bị thay thế hoàn toàn (không lỗi, nhưng dễ gây bug logic khi code phức tạp).

**Lỗi 4 — Nhầm `statusBar()` (method, tự tạo bar) với việc tạo `QStatusBar()` thủ công:** `QMainWindow` đã tự quản lý status bar, gọi `self.statusBar()` là đủ — không cần `QStatusBar()` + `setStatusBar()` thủ công trừ khi có nhu cầu tùy biến đặc biệt.

**Lỗi 5 — Toolbar bị "mất tích" khi kéo thả (vì mặc định `movable=True`):** Người dùng vô tình kéo toolbar ra khỏi vị trí, tưởng bị lỗi mất giao diện. Luôn cân nhắc `toolbar.setMovable(False)` cho ứng dụng nội bộ ổn định.

### 5. Bài tập thực hành

Nâng cấp toàn bộ **"LearnHub Desktop"** thành ứng dụng `QMainWindow` chuẩn chuyên nghiệp:

**Yêu cầu:**

1. Chuyển `MainWindow` sang kế thừa `QMainWindow`, dùng `QWidget` trung tâm chứa `QListWidget` hiển thị danh sách khóa học đã đăng ký (dữ liệu mẫu tự đặt, ít nhất 5 khóa).
2. Menu **"Khóa học"** gồm: "Thêm khóa học mới", "Xóa khóa học đã chọn", dấu phân cách, "Thoát" (phím tắt `Ctrl+Q`).
3. Toolbar chứa 2 action "Thêm" và "Xóa" (dùng chung `QAction` với menu, không định nghĩa lại).
4. Status bar: hiển thị "Sẵn sàng" mặc định; khi thêm/xóa thành công thì hiện thông báo tương ứng trong 2-3 giây; góc phải cố định hiển thị `QLabel` dạng "Tổng: x khóa học" (dùng `addPermanentWidget`), tự cập nhật số liệu.
5. Action "Xóa khóa học đã chọn" phải hiện `QMessageBox.question()` xác nhận trước khi xóa thật.
6. Action "Thoát" cũng phải xác nhận bằng `QMessageBox` trước khi `self.close()`.

Gõ "bài 7" khi hoàn thành — Bài 7 sẽ học **QTableView + Model/View Architecture** — cách hiển thị dữ liệu dạng bảng chuyên nghiệp (rất hợp với kiến thức Database bạn đang học song song), nền tảng cho mọi ứng dụng quản lý dữ liệu thực tế.
