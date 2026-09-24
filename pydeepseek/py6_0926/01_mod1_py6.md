# 📘 MODULE 1: NỀN TẢNG & CÀI ĐẶT PYSIDE6 (Chi tiết)

> **Mục tiêu module**: Hiểu PySide6 là gì, cài đặt thành công, viết được chương trình GUI đầu tiên và hiểu **tường tận từng dòng code**.

---

## 🎯 BÀI 1.1: PYSIDE6 LÀ GÌ? TẠI SAO CHỌN NÓ?

### 1.1.1. Bức tranh tổng thể về GUI Framework

Khi bạn muốn làm app có giao diện (cửa sổ, nút, menu...), bạn cần một **GUI framework**. Với Python, có các lựa chọn phổ biến:

| Framework | Nền tảng | Ưu điểm | Nhược điểm |
|-----------|----------|---------|------------|
| **Tkinter** | Có sẵn trong Python | Nhẹ, không cần cài | Giao diện cũ, widget ít |
| **PySide6** | Qt 6 (C++) | Mạnh mẽ, cross-platform, nhiều widget, chuyên nghiệp | Học hơi dốc, nặng |
| **PyQt6** | Qt 6 (C++) | Giống PySide6 | Giấy phép GPL/thương mại |
| **Kivy** | Python | Đẹp, hỗ trợ mobile | Khác biệt, ít tài liệu VN |
| **wxPython** | wxWidgets | Native look | Ít cập nhật |

### 1.1.2. PySide6 vs PyQt6 – Chọn cái nào?

Cả hai đều là **binding** của Qt 6 cho Python. Nghĩa là: Qt được viết bằng C++, binding giúp Python gọi được các class của Qt.

| Tiêu chí | PySide6 | PyQt6 |
|----------|---------|-------|
| Nhà phát triển | **Qt Company** (chính chủ) | Riverbank Computing |
| Giấy phép | **LGPL** (dùng thương mại miễn phí) | GPL v3 hoặc mua commercial |
| API | Gần như giống PyQt6 | Gần như giống PySide6 |
| Signal/Slot | `Signal`, `Slot` | `pyqtSignal`, `pyqtSlot` |
| Đóng gói | `pyside6-deploy` | `pyinstaller` |

👉 **Kết luận**: Học PySide6 vì **miễn phí cho cả mục đích thương mại** và là **chính chủ Qt**.

### 1.1.3. Kiến trúc Qt – Hiểu để học nhanh hơn

Qt được chia thành nhiều **module**. Khi học PySide6, bạn sẽ gặp các module sau:

```
PySide6/
├── QtCore       ← Nền tảng: Signal/Slot, QObject, QTimer, QFile, thread...
├── QtGui        ← Đồ họa: QPainter, QColor, QFont, QIcon, event...
├── QtWidgets    ← Widget: QPushButton, QLabel, QMainWindow, layout...
├── QtNetwork    ← HTTP, TCP socket
├── QtSql        ← Database
├── QtMultimedia ← Âm thanh, video
├── QtCharts     ← Biểu đồ
├── QtWebEngine  ← Nhúng trình duyệt Chromium
└── ...
```

💡 **Quy tắc nhớ nhanh**:
- **`QtCore`** → logic, không liên quan hình ảnh
- **`QtGui`** → thứ gì vẽ ra được (font, màu, icon, ảnh)
- **`QtWidgets`** → thứ gì người dùng tương tác (nút, ô nhập, cửa sổ)

### 1.1.4. QObject – "Ông tổ" của mọi thứ

Hầu hết class trong Qt đều kế thừa từ **`QObject`**. Nó cung cấp:
- **Signal/Slot** (cơ chế giao tiếp giữa các object)
- **Parent-Child** (quản lý bộ nhớ tự động)
- **Event system**
- **Meta-object system** (introspection)

👉 Đây là **khái niệm quan trọng nhất** cần nhớ. Mọi widget, timer, thread, model... đều là QObject (hoặc con của nó).

---

## 🎯 BÀI 1.2: CÀI ĐẶT MÔI TRƯỜNG

### 1.2.1. Yêu cầu hệ thống

- **Python**: >= 3.7 (khuyến nghị 3.10+)
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Dung lượng**: ~500MB sau khi cài

Kiểm tra Python:
```bash
python --version
# hoặc
python3 --version
```

### 1.2.2. Tạo Virtual Environment (BẮT BUỘC)

**Tại sao cần venv?**
- Cô lập project – không làm hỏng Python hệ thống
- Mỗi project có version thư viện riêng
- Dễ xóa, dễ backup

**Windows (PowerShell)**:
```powershell
cd D:\Projects\pyside-learning
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux**:
```bash
cd ~/Projects/pyside-learning
python3 -m venv venv
source venv/bin/activate
```

Sau khi activate, prompt sẽ có tiền tố `(venv)`:
```
(venv) D:\Projects\pyside-learning>
```

### 1.2.3. Cài đặt PySide6

```bash
pip install PySide6
```

Kiểm tra:
```bash
pip show PySide6
python -c "import PySide6; print(PySide6.__version__)"
# Output: 6.7.2 (hoặc version mới hơn)
```

### 1.2.4. Các tool đi kèm (RẤT QUAN TRỌNG)

Sau khi cài, bạn có sẵn các command line tool:

| Tool | Công dụng | Khi nào dùng |
|------|-----------|--------------|
| `pyside6-designer` | Kéo thả giao diện (GUI editor) | Khi muốn thiết kế UI nhanh |
| `pyside6-uic` | Convert file `.ui` → `.py` | Sau khi dùng Designer |
| `pyside6-rcc` | Convert file `.qrc` → `.py` | Khi nhúng ảnh/icon vào app |
| `pyside6-lupdate` | Trích xuất chuỗi để dịch | Khi làm app đa ngôn ngữ |
| `pyside6-deploy` | Đóng gói app | Khi phát hành |

Thử mở Designer:
```bash
pyside6-designer
```

### 1.2.5. Cấu trúc thư mục học tập đề xuất

```
pyside-learning/
├── venv/                    ← Virtual environment
├── module1/
│   ├── bai1_3_hello.py
│   └── bai1_4_variants.py
├── module2/
├── ...
└── requirements.txt
```

Tạo `requirements.txt`:
```txt
PySide6==6.7.2
```

### 1.2.6. Editor/IDE đề xuất

- **VS Code** + extension **Qt for Python** (Microsoft) – nhẹ, tốt
- **PyCharm** – mạnh, có debug UI tốt
- **Qt Creator** – chuyên cho Qt, hỗ trợ cả C++ và Python

---

## 🎯 BÀI 1.3: CHƯƠNG TRÌNH ĐẦU TIÊN – GIẢI THÍCH TỪNG DÒNG

Tạo file `module1/bai1_3_hello.py`:

```python
import sys
from PySide6.QtWidgets import QApplication, QLabel

# 1. Tạo đối tượng Application
app = QApplication(sys.argv)

# 2. Tạo widget
label = QLabel("Hello PySide6!")

# 3. Hiển thị widget
label.show()

# 4. Chạy vòng lặp sự kiện
sys.exit(app.exec())
```

Chạy:
```bash
python module1/bai1_3_hello.py
```

### 🔍 GIẢI THÍCH CHI TIẾT TỪNG DÒNG

#### Dòng 1: `import sys`
- `sys` là module chuẩn Python
- Cần để truyền `sys.argv` (đối số dòng lệnh) vào QApplication
- Cần cho `sys.exit()` để trả về exit code

#### Dòng 2: `from PySide6.QtWidgets import QApplication, QLabel`
- **`QApplication`**: đối tượng đại diện cho **toàn bộ ứng dụng**. **Chỉ được tạo MỘT lần duy nhất**. Quản lý event loop, resource, style chung.
- **`QLabel`**: widget đơn giản để **hiển thị text/ảnh**.

#### Dòng 5: `app = QApplication(sys.argv)`
- Khởi tạo app. **Bắt buộc phải có trước khi tạo bất kỳ widget nào**.
- `sys.argv`: cho phép Qt xử lý các tham số dòng lệnh như `-style`, `-platform`.
- ⚠️ **Chỉ tạo một QApplication trong toàn bộ chương trình**. Tạo cái thứ hai → crash.

#### Dòng 8: `label = QLabel("Hello PySide6!")`
- Tạo một `QLabel` với nội dung `"Hello PySide6!"`
- **Chưa hiển thị gì cả** – chỉ nằm trong bộ nhớ.
- Vì không có `parent`, label là **top-level widget** (cửa sổ độc lập).

#### Dòng 11: `label.show()`
- Yêu cầu Qt vẽ widget ra màn hình.
- Widget sẽ xuất hiện với kích thước mặc định (do Qt tính toán từ nội dung).

#### Dòng 14: `sys.exit(app.exec())`
Đây là **dòng quan trọng nhất** – hãy phân tích kỹ:

- **`app.exec()`**: bắt đầu **event loop** – vòng lặp vô hạn lắng nghe sự kiện (chuột, bàn phím, timer, vẽ...).
- Event loop chỉ **kết thúc** khi:
  - Cửa sổ cuối cùng bị đóng
  - Gọi `app.quit()`
- Khi kết thúc, `app.exec()` trả về **exit code** (0 = thành công).
- **`sys.exit(...)`**: thoát chương trình với exit code đó (truyền cho OS).

💡 **Nếu bỏ `sys.exit()`**: chương trình vẫn chạy nhưng không trả exit code sạch → không tốt cho script tự động hóa.

### 🔄 SƠ ĐỒ HOẠT ĐỘNG

```
┌─────────────────────────────────────────────┐
│  1. Tạo QApplication (khởi động Qt)         │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  2. Tạo Widget (chưa hiển thị)              │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  3. show() → đưa widget vào hàng đợi vẽ     │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  4. app.exec() → EVENT LOOP                 │
│     ┌──────────────────────────────┐        │
│     │  Lắng nghe sự kiện           │        │
│     │  ├─ Chuột click              │        │
│     │  ├─ Bàn phím                 │        │
│     │  ├─ Timer                   │        │
│     │  └─ Vẽ lại (paint)           │        │
│     └──────────────────────────────┘        │
│         ↓ (khi đóng cửa sổ)                 │
│     return exit_code                         │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  5. sys.exit(exit_code)                     │
└─────────────────────────────────────────────┘
```

---

## 🎯 BÀI 1.4: CÁC BIẾN THỂ CỦA "HELLO WORLD"

### Biến thể 1: Đổi tiêu đề cửa sổ, kích thước, vị trí

```python
import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("Hello PySide6!")
label.setWindowTitle("Ứng dụng đầu tiên")   # Tiêu đề cửa sổ
label.resize(400, 300)                        # Kích thước
label.move(100, 100)                          # Vị trí trên màn hình
label.setAlignment(
    __import__('PySide6.QtCore', fromlist=['Qt']).Qt.AlignmentFlag.AlignCenter
)                                             # Căn giữa

label.show()
sys.exit(app.exec())
```

Cách import sạch hơn:

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("Hello PySide6!")
label.setWindowTitle("Ứng dụng đầu tiên")
label.resize(400, 300)
label.move(100, 100)
label.setAlignment(Qt.AlignmentFlag.AlignCenter)

label.show()
sys.exit(app.exec())
```

**Giải thích các method**:
- `setWindowTitle(str)`: đặt tiêu đề thanh cửa sổ
- `resize(w, h)`: đổi kích thước
- `move(x, y)`: đặt vị trí góc trên-trái (so với màn hình)
- `setAlignment(flag)`: căn nội dung. Các flag:
  - `Qt.AlignmentFlag.AlignLeft / AlignRight / AlignHCenter`
  - `Qt.AlignmentFlag.AlignTop / AlignBottom / AlignVCenter`
  - `Qt.AlignmentFlag.AlignCenter` = kết hợp H + V

### Biến thể 2: Dùng QMainWindow (chuẩn cho app thực tế)

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMainWindow Demo")
        self.resize(600, 400)
        
        # Tạo label làm central widget
        label = QLabel("Đây là QMainWindow", self)
        label.setAlignment(
            __import__('PySide6.QtCore', fromlist=['Qt']).Qt.AlignmentFlag.AlignCenter
        )
        self.setCentralWidget(label)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

> **Phân biệt**:
> - `QWidget`: cửa sổ trống, đơn giản
> - `QMainWindow`: có sẵn menu bar, toolbar, status bar, dock – dùng cho app chính

### Biến thể 3: Dùng QApplication với tham số tùy chỉnh

```python
import sys
from PySide6.QtWidgets import QApplication, QLabel

# Truyền argv tùy chỉnh (ví dụ khi test)
app = QApplication(["myapp"])

# Xem thông tin về platform
print("Platform:", app.platformName())
print("Style:", app.style().objectName())

label = QLabel("Info")
label.show()
sys.exit(app.exec())
```

Chạy thử với style khác:
```bash
python bai1_3_hello.py -style Fusion
```

---

## 🎯 BÀI 1.5: HIỂU VỀ PARENT-CHILD (QUẢN LÝ BỘ NHỚ)

Đây là **cơ chế quan trọng** của Qt giúp bạn **không cần lo về memory leak**.

### Nguyên tắc

> Khi một QObject có **parent**, nó sẽ bị **tự động hủy** khi parent bị hủy.

### Ví dụ minh họa

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

app = QApplication(sys.argv)

# Tạo window (top-level, không có parent)
window = QWidget()
window.setWindowTitle("Parent-Child Demo")
window.resize(300, 200)

layout = QVBoxLayout(window)  # layout có parent = window

# Label 1: có parent là window
label1 = QLabel("Label có parent", window)

# Label 2: KHÔNG có parent
label2 = QLabel("Label không parent")

layout.addWidget(label1)
layout.addWidget(label2)  # Khi add vào layout của window → tự động có parent

window.show()

# Kiểm tra parent
print("label1.parent():", label1.parent())
print("label2.parent():", label2.parent())

sys.exit(app.exec())
```

**Kết quả**:
```
label1.parent(): <PySide6.QtWidgets.QWidget object at 0x...>
label2.parent(): <PySide6.QtWidgets.QWidget object at 0x...>  (sau khi addWidget)
```

### Ứng dụng thực tế

```python
# Cách 1: Tường minh
btn = QPushButton("OK", parent=window)

# Cách 2: Implicit qua constructor
btn = QPushButton("OK", window)

# Cách 3: Qua layout (layout tự set parent)
layout.addWidget(btn)
```

⚠️ **Cảnh báo**: Nếu bạn tạo widget **không có parent** và **không giữ reference**, Python có thể garbage collect nó → widget biến mất bất ngờ. Parent-child giúp tránh vấn đề này.

---

## 📝 BÀI TẬP THỰC HÀNH

### Bài tập 1.1 (Dễ)
Tạo cửa sổ hiển thị:
- Tiêu đề: "Giới thiệu bản thân"
- Kích thước 500x300
- Ở giữa: dòng chữ "Tôi tên là [Tên bạn], đang học PySide6"
- In ra console: platform name và version PySide6

### Bài tập 1.2 (Trung bình)
Tạo cửa sổ hiển thị **hai label** xếp dọc:
- Label 1: "Xin chào"
- Label 2: "Tạm biệt"
- Cả hai căn giữa
- Cửa sổ có kích thước 400x200, tiêu đề "Hai label"

💡 **Gợi ý**: Dùng `QVBoxLayout` để xếp dọc.

### Bài tập 1.3 (Khá)
Viết chương trình **nhận 2 đối số dòng lệnh**: `--title` và `--width`, `--height`, dùng `argparse` để parse, rồi tạo cửa sổ với tiêu đề và kích thước tương ứng.

Ví dụ:
```bash
python app.py --title "My App" --width 800 --height 600
```

### Bài tập 1.4 (Nâng cao – tùy chọn)
Nghiên cứu về **exit code**:
- Tạo app với nút bấm, khi bấm thì thoát với exit code là 42
- Chạy từ terminal, kiểm tra `$?` (Linux/Mac) hoặc `%ERRORLEVEL%` (Windows)

💡 Gợi ý: `app.exit(42)` hoặc `sys.exit(42)`.

---

## ✅ CHECKLIST SAU MODULE 1

Đánh dấu khi bạn đã nắm:

- [ ] Hiểu PySide6 là gì, khác PyQt6 ở đâu
- [ ] Biết phân biệt `QtCore` / `QtGui` / `QtWidgets`
- [ ] Hiểu `QObject` là gì
- [ ] Tạo được venv và cài PySide6 thành công
- [ ] Biết các tool: designer, uic, rcc
- [ ] Viết được chương trình "Hello World" và giải thích từng dòng
- [ ] Hiểu event loop và tại sao cần `app.exec()`
- [ ] Hiểu parent-child và cách Qt quản lý bộ nhớ
- [ ] Làm xong ít nhất 3/4 bài tập

---

## 🔜 BÀI TIẾP THEO

**Module 2 – Bài 2.1: QWidget vs QMainWindow** – chúng ta sẽ đi sâu:
- Cấu trúc của `QMainWindow` (menu bar, tool bar, status bar, dock, central widget)
- Khi nào dùng `QWidget`, khi nào dùng `QMainWindow`
- Xây dựng app "Notepad mini" bước đầu

---

👉 **Bạn muốn tôi soạn tiếp Bài 2.1 không?** Hoặc bạn muốn tôi giải chi tiết một bài tập nào trước để bạn đối chiếu kết quả?