# Lộ trình học PySide6 bài bản cho người mới

Chào bạn! Tôi sẽ xây dựng cho bạn một **lộ trình học PySide6 có hệ thống**, chia thành các module rõ ràng, từ cơ bản đến nâng cao. Mỗi bài đều có lý thuyết, code mẫu và bài tập thực hành.

---

## 📋 TỔNG QUAN LỘ TRÌNH

| Module | Chủ đề | Thời lượng ước tính |
|--------|--------|---------------------|
| 1 | Nền tảng & Cài đặt | 1-2 ngày |
| 2 | Widget cơ bản & Layout | 3-4 ngày |
| 3 | Signal & Slot (Event handling) | 2-3 ngày |
| 4 | Widget nâng cao | 4-5 ngày |
| 5 | Dialog & Window | 2-3 ngày |
| 6 | Model/View Architecture | 4-5 ngày |
| 7 | Styling với QSS | 2-3 ngày |
| 8 | Đa luồng & Async | 3-4 ngày |
| 9 | Networking & File I/O | 3-4 ngày |
| 10 | Database với QtSql | 3 ngày |
| 11 | Multimedia & Graphics | 3-4 ngày |
| 12 | Đóng gói & Triển khai | 2 ngày |
| 13 | Dự án tổng hợp (Capstone) | 5-7 ngày |

---

## 🎯 MODULE 1: NỀN TẢNG & CÀI ĐẶT

### Bài 1.1: PySide6 là gì? So sánh với PyQt
- **Qt** là framework C++ đa nền tảng
- **PySide6** là binding chính thức của Qt cho Python (do chính Qt Company phát hành, giấy phép LGPL)
- **PyQt6** là binding của Riverbank (GPL/commercial)
- Ưu điểm PySide6: license thoáng, API gần như tương đương

### Bài 1.2: Cài đặt môi trường
```bash
# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Cài đặt
pip install PySide6
```

Công cụ đi kèm:
- `pyside6-designer` – kéo thả giao diện
- `pyside6-uic` – convert .ui → .py
- `pyside6-rcc` – quản lý resource

### Bài 1.3: Chương trình đầu tiên
```python
import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello PySide6!")
label.show()
sys.exit(app.exec())
```

**Bài tập**: Tạo cửa sổ hiển thị tên bạn, đổi title, set kích thước 400x300.

---

## 🎯 MODULE 2: WIDGET CƠ BẢN & LAYOUT

### Bài 2.1: QWidget và QMainWindow
- `QWidget` – base class của mọi UI component
- `QMainWindow` – cửa sổ chính có menu, toolbar, status bar, dock widget

### Bài 2.2: Các widget nhập liệu
- `QPushButton`, `QLineEdit`, `QTextEdit`, `QPlainTextEdit`
- `QCheckBox`, `QRadioButton`, `QComboBox`, `QSpinBox`, `QSlider`

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.input = QLineEdit()
        self.btn = QPushButton("Click me")
        layout.addWidget(self.input)
        layout.addWidget(self.btn)
        self.setLayout(layout)

app = QApplication([])
w = MyWindow()
w.show()
app.exec()
```

### Bài 2.3: Layout Management
- `QVBoxLayout`, `QHBoxLayout` – dọc/ngang
- `QGridLayout` – lưới
- `QFormLayout` – form nhập liệu
- `QStackedLayout` – nhiều trang
- **Stretch, spacing, margins**

### Bài 2.4: Size Policy & Spacer
- `QSpacerItem`, `addStretch()`
- `setSizePolicy()`

**Bài tập**: Làm form đăng nhập có: Label + LineEdit + Checkbox "Nhớ mật khẩu" + Button, dùng QFormLayout.

---

## 🎯 MODULE 3: SIGNAL & SLOT (EVENT HANDLING)

### Bài 3.1: Khái niệm Signal-Slot
- Signal: sự kiện phát ra (clicked, textChanged, ...)
- Slot: hàm xử lý

```python
self.btn.clicked.connect(self.on_click)

def on_click(self):
    print("Clicked!")
```

### Bài 3.2: Custom Signal
```python
from PySide6.QtCore import Signal, QObject

class MyEmitter(QObject):
    my_signal = Signal(str, int)
```

### Bài 3.3: Event override
- `mousePressEvent`, `keyPressEvent`, `paintEvent`, `closeEvent`

### Bài 3.4: QTimer
- Hẹn giờ, chạy định kỳ

**Bài tập**: Đồng hồ số cập nhật mỗi giây dùng QTimer.

---

## 🎯 MODULE 4: WIDGET NÂNG CAO

### Bài 4.1: QTabWidget, QToolBox
### Bài 4.2: QSplitter, QScrollArea
### Bài 4.3: QListWidget, QTreeWidget, QTableWidget (dạng đơn giản)
### Bài 4.4: QMenu, QToolBar, QStatusBar
### Bài 4.5: QProgressBar, QSystemTrayIcon
### Bài 4.6: QCalendarWidget, QDateEdit, QTimeEdit

**Bài tập**: App ghi chú có: menu, toolbar, list các note, ô nhập nội dung.

---

## 🎯 MODULE 5: DIALOG & WINDOW

### Bài 5.1: QMessageBox (thông báo)
```python
QMessageBox.information(self, "Title", "Nội dung")
QMessageBox.question(self, "?", "Bạn chắc chưa?")
```

### Bài 5.2: QFileDialog, QColorDialog, QFontDialog, QInputDialog
### Bài 5.3: QDialog tùy chỉnh
- `exec()` vs `show()`
- `accept()` / `reject()`

**Bài tập**: App chỉnh sửa ảnh đơn giản – chọn file, chọn màu, đổi font chữ label.

---

## 🎯 MODULE 6: MODEL/VIEW ARCHITECTURE

> Đây là phần **quan trọng nhất** để làm app chuyên nghiệp.

### Bài 6.1: Vì sao cần Model/View? (So sánh với QTableWidget)
### Bài 6.2: QStringListModel + QListView
### Bài 6.3: QStandardItemModel + QTableView/QTreeView
### Bài 6.4: Custom Model với QAbstractTableModel
```python
class MyModel(QAbstractTableModel):
    def rowCount(self, parent): ...
    def columnCount(self, parent): ...
    def data(self, index, role): ...
```

### Bài 6.5: QSortFilterProxyModel (tìm kiếm, sắp xếp)
### Bài 6.6: Delegate (tùy biến hiển thị & edit)

**Bài tập**: App quản lý sinh viên với bảng, tìm kiếm real-time, sắp xếp theo cột.

---

## 🎯 MODULE 7: STYLING VỚI QSS (Qt Style Sheets)

### Bài 7.1: Cú pháp QSS (giống CSS)
```css
QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 5px;
    padding: 8px 16px;
}
QPushButton:hover { background-color: #2980b9; }
```

### Bài 7.2: Selector, pseudo-state, property
### Bài 7.3: QPalette & theme sáng/tối
### Bài 7.4: Custom widget paint (QPainter)

**Bài tập**: Làm theme Dark/Light toggle cho app.

---

## 🎯 MODULE 8: ĐA LUỒNG & ASYNC

### Bài 8.1: Vấn đề blocking UI
### Bài 8.2: QThread cơ bản
### Bài 8.3: Worker pattern với Signal/Slot
```python
class Worker(QObject):
    finished = Signal()
    progress = Signal(int)
    
    def run(self):
        for i in range(100):
            self.progress.emit(i)
        self.finished.emit()
```

### Bài 8.4: QThreadPool + QRunnable
### Bài 8.5: Async với qasync (tùy chọn)

**Bài tập**: App download file có progress bar, không đơ UI.

---

## 🎯 MODULE 9: NETWORKING & FILE I/O

### Bài 9.1: QFile, QTextStream, QDataStream
### Bài 9.2: JSON với QJsonDocument
### Bài 9.3: QNetworkAccessManager (HTTP request)
### Bài 9.4: QSettings (lưu config)

**Bài tập**: App đọc API thời tiết, hiển thị + lưu setting vào QSettings.

---

## 🎯 MODULE 10: DATABASE VỚI QTSQL

### Bài 10.1: QSqlDatabase – kết nối SQLite/MySQL
### Bài 10.2: QSqlQuery – CRUD
### Bài 10.3: QSqlTableModel, QSqlQueryModel
### Bài 10.4: QSqlRelationalTableModel (quan hệ bảng)

**Bài tập**: App quản lý kho hàng dùng SQLite + QTableView.

---

## 🎯 MODULE 11: MULTIMEDIA & GRAPHICS

### Bài 11.1: QMediaPlayer, QVideoWidget (âm thanh/video)
### Bài 11.2: QGraphicsScene, QGraphicsView, QGraphicsItem
### Bài 11.3: Animation với QPropertyAnimation
### Bài 11.4: Chart với QtCharts

**Bài tập**: App vẽ đồ thị sin/cos bằng QtCharts, có animation.

---

## 🎯 MODULE 12: ĐÓNG GÓI & TRIỂN KHAI

### Bài 12.1: Cấu trúc project chuẩn
```
myapp/
├── main.py
├── ui/
├── core/
├── resources/
└── requirements.txt
```

### Bài 12.2: Resource system (.qrc)
### Bài 12.3: Đóng gói với PyInstaller
```bash
pyinstaller --windowed --name MyApp main.py
```
### Bài 12.4: Đóng gói với Nuitka (tùy chọn)

---

## 🎯 MODULE 13: DỰ ÁN TỔNG HỢP (CAPSTONE)

Chọn **1 trong các dự án** sau để làm:

1. **Todo App nâng cao**: SQLite + tag + deadline + notification
2. **Trình quản lý ảnh**: Thumbnail, tag, slideshow
3. **Chat app client**: Socket/HTTP + multi-thread
4. **Trình soạn thảo markdown**: Editor + preview + export PDF
5. **Dashboard tài chính**: Chart + database + import/export CSV

---

## 📚 TÀI NGUYÊN HỌC

| Loại | Nguồn |
|------|-------|
| Docs chính thức | https://doc.qt.io/qtforpython-6/ |
| Ví dụ code | Cài PySide6 → thư mục `examples/` |
| Sách | "Qt for Python" (Qt docs), "Rapid GUI Programming with Python and Qt" (PyQt nhưng áp dụng được) |
| Video | Kênh YouTube: "Python GUIs", "Codemy" |
| Cộng đồng | Reddit r/QtFramework, Qt Forum |

---

## 🎓 CÁCH HỌC HIỆU QUẢ

1. **Mỗi bài phải gõ tay code**, không copy-paste
2. **Làm hết bài tập** – không bỏ qua
3. **Đọc Qt Docs** dù khó, vì PySide6 docs = Qt C++ docs
4. **Xem source của Qt examples** đi kèm
5. **Làm project nhỏ sau mỗi module**
6. **Cuối cùng: build 1 app hoàn chỉnh** và deploy

---

## 💡 GỢI Ý BẮT ĐẦU NGAY

Bạn muốn tôi **bắt đầu dạy chi tiết bài nào trước**? 

Tôi đề xuất thứ tự:
1. **Module 1 → 2 → 3** (nền tảng vững)
2. **Module 6** (Model/View) – cái này tách biệt người nghiệp dư và chuyên nghiệp
3. **Module 8** (Threading) – để làm app thực tế
4. Sau đó học các module còn lại tùy nhu cầu

👉 **Bạn muốn tôi soạn chi tiết bài nào đầu tiên?** Ví dụ: "Dạy tôi Bài 2.3 – Layout Management chi tiết" hoặc "Bắt đầu từ Bài 1.3 với giải thích từng dòng code".