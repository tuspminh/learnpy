## Bài 7: QTableView & Model/View Architecture — Hiển Thị Dữ Liệu Dạng Bảng Chuyên Nghiệp

### 1. Động lực (Motivation)

Đây là một trong những bài **quan trọng nhất** của toàn khóa học, vì nó kết nối trực tiếp với kiến thức Database bạn đang học song song. Mọi ứng dụng quản lý dữ liệu thực tế — từ phần mềm kế toán, hệ thống quản lý kho (WMS), dashboard vận hành ngân hàng số, đến công cụ nội bộ theo dõi giao dịch fintech — đều cần hiển thị dữ liệu dạng **bảng** (rows/columns) lấy từ database.

Nếu dùng `QListWidget` (Bài 4) để hiển thị hàng nghìn dòng dữ liệu từ PostgreSQL, bạn sẽ gặp vấn đề nghiêm trọng: mỗi item phải tạo thủ công, cập nhật dữ liệu phải xóa-tạo-lại toàn bộ, hiệu năng tệ khi dữ liệu lớn. Qt giải quyết vấn đề này bằng **Model/View Architecture** — một trong những thiết kế kiến trúc phần mềm kinh điển nhất trong lịch sử lập trình GUI, tách biệt hoàn toàn **dữ liệu** (Model) khỏi **cách hiển thị** (View).

Đây chính xác là tư duy MVC (Model-View-Controller) mà bạn sẽ gặp lại xuyên suốt sự nghiệp lập trình: Django (MVT), React (component + state), hay thiết kế API backend RESTful — tất cả đều xoay quanh nguyên tắc "tách dữ liệu khỏi giao diện" mà Qt dạy bạn ngay ở bài này.

### 2. Giải thích khái niệm

#### 2.1. Vấn đề cách cũ (Widget-based) vs cách mới (Model/View)

python

```python
# ❌ Cách "widget-based" - KHÔNG scale được với dữ liệu lớn
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

table = QTableWidget(3, 2)   # 3 hàng, 2 cột
table.setItem(0, 0, QTableWidgetItem("Nguyễn Văn A"))
table.setItem(0, 1, QTableWidgetItem("1,500,000"))
# Với 10,000 dòng dữ liệu từ DB → phải gọi setItem() 20,000 lần → chậm, tốn RAM
```

`QTableWidget` (không phải trọng tâm bài này) lưu **từng ô** như 1 object riêng — cách này dễ học nhưng **không hiệu quả** với dữ liệu lớn từ database. Cách chuyên nghiệp là dùng **`QTableView` + Model**, nơi dữ liệu được lưu trong **1 cấu trúc dữ liệu duy nhất** (list, hoặc kết quả `SELECT` từ PostgreSQL), và View chỉ **"nhìn vào" và vẽ ra** dữ liệu đó theo yêu cầu — không copy dữ liệu ra widget riêng lẻ.

#### 2.2. Kiến trúc Model/View: 3 vai trò

```
┌─────────┐         ┌──────────┐        ┌────────┐
│  Model   │ <-----> │   View    │ <----> │  User  │
│(dữ liệu) │         │(hiển thị) │        │(tương tác)│
└─────────┘         └──────────┘        └────────┘
```

- **Model**: Nắm giữ dữ liệu thật (list Python, kết quả query SQL...) và biết cách "trả lời" khi View hỏi "ô (hàng 2, cột 3) chứa gì?"
- **View** (`QTableView`): Chỉ lo việc **vẽ** dữ liệu ra màn hình dạng bảng, cuộn, chọn dòng... không tự lưu dữ liệu.
- Khi Model thay đổi dữ liệu và phát tín hiệu, View **tự động vẽ lại** — không cần code thủ công refresh từng ô.

#### 2.3. Cách đơn giản nhất: `QStandardItemModel`

Đây là model dựng sẵn của Qt, phù hợp khi dữ liệu không quá lớn hoặc chưa cần custom phức tạp:

python

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtGui import QStandardItemModel, QStandardItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bài 7 - QTableView cơ bản")
        self.resize(500, 300)

        # Bước 1: Tạo Model - 0 hàng, 3 cột ban đầu
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Mã KH", "Họ tên", "Số dư (VNĐ)"])

        # Bước 2: Nạp dữ liệu vào Model
        data = [
            ("KH001", "Nguyễn Văn An", "15,500,000"),
            ("KH002", "Trần Thị Bình", "8,200,000"),
            ("KH003", "Lê Hoàng Cường", "23,750,000"),
        ]
        for row in data:
            items = [QStandardItem(str(field)) for field in row]
            self.model.appendRow(items)

        # Bước 3: Tạo View và gắn Model vào
        self.table_view = QTableView()
        self.table_view.setModel(self.model)   # <-- Đây là bước kết nối Model/View

        self.setCentralWidget(self.table_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**So sánh tư duy với kiến thức DB bạn đã học:** `QStandardItemModel` giống hệt việc bạn `SELECT` dữ liệu ra thành 1 tập kết quả (result set), rồi `QTableView` chính là **cách trình bày** tập kết quả đó — hoàn toàn tách biệt khỏi nguồn dữ liệu gốc.

#### 2.4. Tùy chỉnh hiển thị View

python

```python
from PySide6.QtWidgets import QAbstractItemView, QHeaderView

# Chọn theo hàng, không cho chọn từng ô lẻ
self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

# Chỉ cho chọn 1 hàng tại 1 thời điểm
self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)

# Không cho sửa trực tiếp trên bảng (read-only)
self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

# Cột tự động giãn để lấp đầy chiều ngang
self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

# Ẩn số thứ tự hàng bên trái (vertical header)
self.table_view.verticalHeader().setVisible(False)

# Bôi màu xen kẽ các dòng (zebra striping) - rất phổ biến trong UI enterprise
self.table_view.setAlternatingRowColors(True)
```

#### 2.5. Đọc dữ liệu khi người dùng chọn dòng

python

```python
def _handle_selection_changed(self):
    selected_indexes = self.table_view.selectionModel().selectedRows()
    if not selected_indexes:
        return

    row = selected_indexes[0].row()   # Lấy số thứ tự hàng được chọn
    customer_id = self.model.item(row, 0).text()    # Cột 0: Mã KH
    customer_name = self.model.item(row, 1).text()  # Cột 1: Họ tên
    print(f"Đã chọn: {customer_id} - {customer_name}")

# Kết nối signal selectionChanged của selectionModel
self.table_view.selectionModel().selectionChanged.connect(self._handle_selection_changed)
```

Lưu ý: `selectionModel()` là 1 object **riêng biệt** được Qt tự tạo khi bạn `setModel()`, chuyên quản lý "hàng/ô nào đang được chọn" — tách biệt khỏi Model chứa dữ liệu.

#### 2.6. Cập nhật, thêm, xóa dữ liệu qua Model

python

```python
# Thêm 1 hàng mới
new_row = [QStandardItem("KH004"), QStandardItem("Phạm Thị Dung"), QStandardItem("5,000,000")]
self.model.appendRow(new_row)

# Sửa giá trị 1 ô cụ thể
self.model.item(0, 2).setText("16,000,000")   # Hàng 0, cột 2

# Xóa 1 hàng theo index
self.model.removeRow(2)

# Xóa toàn bộ dữ liệu (giữ header)
self.model.removeRows(0, self.model.rowCount())
```

**Điểm mạnh cốt lõi:** Bạn **không bao giờ** thao tác trực tiếp lên `QTableView` để đổi dữ liệu — luôn thao tác qua `Model`. View chỉ **lắng nghe** signal nội bộ của Model (`dataChanged`, `rowsInserted`...) và tự vẽ lại. Đây là nguyên tắc kiến trúc: **View không bao giờ nắm dữ liệu, Model không bao giờ biết cách vẽ**.

### 3. Ví dụ thực tế 2026: Dashboard Quản lý Giao dịch — Chuẩn bị kết nối PostgreSQL

Đây là mô hình chính xác bạn sẽ dùng ở Bài 14-18 (khi nối PostgreSQL thật). Ví dụ này giả lập dữ liệu tĩnh nhưng **cấu trúc code giống hệt** khi thay bằng kết quả `SELECT` thật từ database:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QLabel, QPushButton, QAbstractItemView, QHeaderView, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class TransactionDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Dashboard - Cake Digital Bank")
        self.resize(700, 450)
        self._setup_ui()
        self._load_sample_data()

    def _setup_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        header = QLabel("💳 Danh sách giao dịch gần đây")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # --- Thiết lập Model ---
        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(["Mã GD", "Khách hàng", "Số tiền (VNĐ)", "Trạng thái"])

        # --- Thiết lập View ---
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)

        # --- Thanh hành động ---
        action_row = QHBoxLayout()
        self.detail_label = QLabel("Chọn 1 giao dịch để xem chi tiết")
        action_row.addWidget(self.detail_label)
        action_row.addStretch()

        approve_btn = QPushButton("✅ Duyệt giao dịch")
        approve_btn.clicked.connect(self._handle_approve)
        action_row.addWidget(approve_btn)
        layout.addLayout(action_row)

        self.setCentralWidget(central)

        # Kết nối signal chọn hàng
        self.table_view.selectionModel().selectionChanged.connect(self._handle_selection_changed)

    def _load_sample_data(self):
        # Trong thực tế: đây sẽ là kết quả từ cursor.fetchall() sau khi SELECT từ PostgreSQL
        transactions = [
            ("GD-88291", "Nguyễn Văn An", "2,500,000", "Chờ duyệt"),
            ("GD-88292", "Trần Thị Bình", "15,000,000", "Chờ duyệt"),
            ("GD-88293", "Lê Hoàng Cường", "750,000", "Đã duyệt"),
            ("GD-88294", "Phạm Thị Dung", "42,300,000", "Chờ duyệt"),
        ]
        for row_data in transactions:
            row_items = [QStandardItem(str(field)) for field in row_data]
            for item in row_items:
                item.setTextAlignment(Qt.AlignCenter)
            self.model.appendRow(row_items)

    def _handle_selection_changed(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            self.detail_label.setText("Chọn 1 giao dịch để xem chi tiết")
            return

        row = selected[0].row()
        txn_id = self.model.item(row, 0).text()
        customer = self.model.item(row, 1).text()
        amount = self.model.item(row, 2).text()
        self.detail_label.setText(f"Đang xem: {txn_id} — {customer} — {amount}đ")

    def _handle_approve(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn 1 giao dịch để duyệt.")
            return

        row = selected[0].row()
        status_item = self.model.item(row, 3)

        if status_item.text() == "Đã duyệt":
            QMessageBox.information(self, "Thông báo", "Giao dịch này đã được duyệt trước đó.")
            return

        status_item.setText("Đã duyệt")
        self.detail_label.setText(f"✅ Đã duyệt giao dịch {self.model.item(row, 0).text()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransactionDashboard()
    window.show()
    sys.exit(app.exec())
```

**Điểm cần chú ý:** Hàm `_load_sample_data()` được tách riêng biệt — đây **chính là điểm** mà ở Bài 14-18, bạn chỉ cần thay nội dung hàm này bằng:

python

```python
cursor.execute("SELECT txn_id, customer_name, amount, status FROM transactions")
transactions = cursor.fetchall()
```

Toàn bộ phần còn lại của UI **không cần sửa gì cả** — đây chính là giá trị thực sự của Model/View Architecture: tách biệt nguồn dữ liệu khỏi cách hiển thị.

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Quên gọi `setModel()`:**

python

```python
table_view = QTableView()
# ❌ Quên table_view.setModel(self.model) → bảng trống trơn, không lỗi
```

**Lỗi 2 — Thao tác trực tiếp lên View thay vì Model:**

python

```python
table_view.item(0, 0).setText("...")   # ❌ QTableView KHÔNG có method item() như QTableWidget
model.item(0, 0).setText("...")         # ✅ Đúng - luôn thao tác qua Model
```

**Lỗi 3 — Quên `setEditTriggers(NoEditTriggers)` cho bảng chỉ để xem:** Người dùng double-click vô tình sửa được dữ liệu hiển thị (dù dữ liệu gốc trong DB không đổi, nhưng gây hiểu nhầm nghiêm trọng khi demo/thực tế sử dụng).

**Lỗi 4 — Dùng sai index khi đọc dữ liệu từ `selectionModel()`:**

python

```python
row = self.table_view.selectionModel().selectedRows()   # ❌ Đây là LIST các QModelIndex, không phải số hàng
row = self.table_view.selectionModel().selectedRows()[0].row()   # ✅ Phải lấy .row() từ phần tử đầu
```

**Lỗi 5 — Không kiểm tra `selectedRows()` rỗng trước khi truy cập `[0]`:**

python

```python
row = selected[0].row()   # ❌ IndexError nếu người dùng chưa chọn gì (list rỗng)
```

→ Luôn kiểm tra `if not selected: return` trước.

### 5. Bài tập thực hành

Xây dựng **"LearnHub Desktop - Bảng điểm học viên"**, chuẩn bị nền tảng cho việc nối PostgreSQL sau này:

**Yêu cầu:**

1. Dùng `QMainWindow`, `QStandardItemModel` với 4 cột: "Mã HV", "Họ tên", "Khóa học", "Điểm".
2. Nạp sẵn ít nhất 6 dòng dữ liệu mẫu qua hàm `_load_sample_data()` riêng biệt (mô phỏng dữ liệu từ DB).
3. `QTableView` cấu hình: chọn theo hàng, không cho sửa trực tiếp, zebra stripe (`setAlternatingRowColors`), header cột giãn đều.
4. Khi chọn 1 hàng, hiển thị `QLabel` phía dưới bảng: "Đang xem: [Họ tên] - Khóa [Khóa học] - Điểm: [Điểm]".
5. Nút "🎓 Đánh dấu Đạt/Không đạt": nếu điểm >= 5 thì cập nhật cột thứ 5 (thêm cột "Kết quả") thành "Đạt" (màu xanh), ngược lại "Không đạt" (màu đỏ) — gợi ý dùng `item.setForeground()` với `QColor`.
6. Nút "Xóa học viên đã chọn" — hiện `QMessageBox.question()` xác nhận trước khi `removeRow()`.

Gõ "bài 8" khi hoàn thành — Bài 8 sẽ học **QDialog** (hộp thoại tùy chỉnh): tạo form thêm/sửa dữ liệu dạng popup — thứ bạn sẽ cần ngay để hoàn thiện chức năng "Thêm học viên mới" cho bảng vừa xây ở bài này.
