Chào mừng bạn đến với **Bài 1: Làm quen với PySide6 và ứng dụng đầu tiên**!

Đây là buổi học đầu tiên trong hành trình 12 tuần của chúng ta. Hôm nay, chúng ta sẽ không chỉ học cách tạo một cửa sổ đơn giản mà còn hiểu sâu về **cách thức vận hành** của một ứng dụng đồ họa. Điều này sẽ giúp bạn không bị "mơ hồ" khi code những ứng dụng phức tạp sau này.

---

## Mục tiêu bài học

Sau bài này, bạn sẽ:
1. Hiểu rõ kiến trúc cơ bản của ứng dụng PySide6
2. Biết vòng đời của một ứng dụng GUI
3. Tạo được cửa sổ đầu tiên và tùy chỉnh được nó
4. Hiểu về **hệ thống phân cấp (hierarchy)** của các thành phần

---

## Phần 1: Cài đặt và Kiểm tra

Trước khi bắt đầu, hãy đảm bảo bạn đã cài đặt PySide6:

```bash
pip install pyside6
```

Kiểm tra xem đã cài thành công chưa bằng cách chạy lệnh sau trong Python:

```python
import PySide6

print(PySide6.__version__)  # Ví dụ: 6.6.0
```

---

## Phần 2: "Xin chào thế giới" - Phân tích từng dòng code

Đây là ứng dụng đơn giản nhất. Hãy cùng tôi phân tích **từng dòng một**:

```python
# main.py
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel

# Bước 1: Khởi tạo QApplication - "Trái tim" của ứng dụng
app = QApplication(sys.argv)

# Bước 2: Tạo cửa sổ chính
window = QWidget()
window.setWindowTitle("Ứng dụng đầu tiên của tôi")
window.resize(400, 300)  # Đặt kích thước: rộng 400, cao 300

# Bước 3: Thêm một label (nhãn) vào cửa sổ
label = QLabel("Xin chào PySide6!", parent=window)
label.move(100, 100)  # Đặt vị trí (x=100, y=100)

# Bước 4: Hiển thị cửa sổ
window.show()

# Bước 5: Chạy vòng lặp sự kiện - "Trái tim đập"
sys.exit(app.exec())
```

### Giải thích chi tiết

#### 🔹 `app = QApplication(sys.argv)`
- **Tại sao cần?** Mỗi ứng dụng PySide6 chỉ có DUY NHẤT một `QApplication`.
- **`sys.argv` là gì?** Đây là danh sách các tham số dòng lệnh (nếu bạn chạy chương trình với tham số). PySide6 dùng nó để xử lý các tùy chọn như `-style`, `-stylesheet`,...
- **Vai trò:** 
  - Quản lý vòng lặp sự kiện
  - Quản lý các tài nguyên toàn cục (font, màu sắc, stylesheet)
  - Giao tiếp với hệ điều hành (nhận sự kiện từ bàn phím, chuột)

#### 🔹 `QWidget()`
- `QWidget` là lớp **cơ sở** cho TẤT CẢ các thành phần giao diện (buttons, labels, windows,...).
- Một `QWidget` có thể là:
  - **Cửa sổ độc lập** (window) - như trong ví dụ này
  - **Thành phần con** (child widget) - như `label` ở trên

#### 🔹 `label = QLabel("Xin chào", parent=window)`
- **`parent=window`:** Đây là một khái niệm CỰC KỲ QUAN TRỌNG!
- **Hệ thống phân cấp (Hierarchy):**
  ```
  app (QApplication)
   └── window (QWidget) - Cửa sổ chính
        └── label (QLabel) - Widget con
  ```
- **Ý nghĩa của `parent`:**
  - Khi `window` bị đóng, `label` cũng tự động bị xóa (quản lý bộ nhớ tự động)
  - `label` sẽ nằm BÊN TRONG `window` (tọa độ của label tính theo `window`)
  - Các sự kiện (click, hover,...) của `label` được xử lý trong ngữ cảnh của `window`

#### 🔹 `window.show()`
- Mặc định, widget mới tạo ở trạng thái **ẩn (hidden)**.
- `show()` hiển thị widget và tất cả các widget con của nó (nếu có).
- Bạn cũng có thể dùng `hide()` để ẩn.

#### 🔹 `sys.exit(app.exec())`
- **`app.exec()`** - Bắt đầu **Vòng lặp sự kiện chính**.
  - Đây là một vòng lặp vô hạn, chạy cho đến khi ứng dụng tắt.
  - Nó liên tục lắng nghe và xử lý các sự kiện (click chuột, gõ phím, vẽ lại màn hình,...).
- **`sys.exit()`** - Nhận mã thoát từ `app.exec()` và trả về cho hệ điều hành (0 nghĩa là thành công).

---

## Phần 3: Vòng đời của một ứng dụng - HIỂU ĐỂ TRÁNH SAI LẦM

Hãy hình dung ứng dụng chạy như thế nào:

```
1. Khởi động
   ├── Import thư viện
   ├── Tạo QApplication
   └── Tạo QWidget chính
        └── Tạo các widget con (labels, buttons,...)

2. Hiển thị (show)
   └── Gửi yêu cầu hiển thị lên hệ điều hành

3. Vòng lặp sự kiện (app.exec()) - CHẠY MÃI CHO ĐẾN KHI TẮT
   ├── Chờ sự kiện từ người dùng (click, gõ phím)
   ├── Hoặc sự kiện từ hệ điều hành (cần vẽ lại, resize)
   ├── Xử lý sự kiện
   │    ├── Nếu là sự kiện đóng cửa sổ -> thoát vòng lặp
   │    └── Ngược lại -> gọi các hàm xử lý tương ứng
   └── Quay lại chờ sự kiện tiếp theo

4. Kết thúc
   ├── Người dùng tắt cửa sổ
   ├── Vòng lặp sự kiện kết thúc
   ├── Giải phóng tài nguyên
   └── Trả về mã thoát
```

**⚠️ LƯU Ý QUAN TRỌNG:** 
- **KHÔNG** code vòng lặp vô hạn (`while True`) trong ứng dụng GUI. Điều này sẽ làm "đơ" ứng dụng vì nó chiếm luồng chính.
- Mọi thao tác dài (tải file, kết nối mạng) đều phải xử lý bằng Thread hoặc QTimer (sẽ học ở tuần 8).

---

## Phần 4: Tùy chỉnh cửa sổ

Hãy làm quen với một số phương thức hay dùng của `QWidget`:

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

app = QApplication(sys.argv)

window = QWidget()

# Tùy chỉnh tiêu đề và kích thước
window.setWindowTitle("Cửa sổ của tôi")
window.resize(500, 400)

# Đặt vị trí cửa sổ trên màn hình (x=100, y=200)
window.move(100, 200)

# Đặt icon cho cửa sổ (cần file .ico hoặc .png)
# window.setWindowIcon(QIcon("icon.png"))

# Ngăn không cho resize (fixed size)
# window.setFixedSize(500, 400)

# Đặt background color (cách 1 - sử dụng stylesheet)
window.setStyleSheet("background-color: #2b2b2b;")

# Set font mặc định cho tất cả widget con
font = QFont("Arial", 12)
window.setFont(font)

window.show()
sys.exit(app.exec())
```

### Thực hành thêm: Tạo nhiều widget con

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit


class MyWindow(QWidget):  # Tạo class riêng để dễ quản lý
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Học OOP với PySide6")
        self.resize(400, 300)

        # Tạo các widget con
        self.label = QLabel("Nhập tên của bạn:", self)
        self.label.move(50, 50)

        self.input = QLineEdit(self)
        self.input.move(50, 80)
        self.input.resize(300, 30)
        self.input.setPlaceholderText("Nhập vào đây...")

        self.button = QPushButton("Hiển thị", self)
        self.button.move(150, 130)

        self.result = QLabel("", self)
        self.result.move(50, 180)

        # Kết nối signal (sẽ học kỹ ở bài sau)
        self.button.clicked.connect(self.on_button_click)

    def on_button_click(self):
        name = self.input.text()
        if name:
            self.result.setText(f"Xin chào {name}!")
        else:
            self.result.setText("Bạn chưa nhập tên!")


app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

---

## Phần 5: Lỗi thường gặp và cách khắc phục

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `QWidget: Cannot create a QWidget without QApplication` | Quên tạo `QApplication` trước khi tạo widget | Tạo `app = QApplication(sys.argv)` ở đầu chương trình |
| Ứng dụng hiện ra rồi tắt ngay | Quên gọi `app.exec()` hoặc gọi sai vị trí | Đảm bảo `sys.exit(app.exec())` ở cuối |
| Widget con không hiển thị | Quên set `parent` hoặc quên `show()` | Kiểm tra `parent` và gọi `show()` cho widget cha |
| Widget bị cắt / không đúng vị trí | Dùng `move()` với widget con nhưng cha chưa được hiển thị | Gọi `show()` trước, hoặc dùng Layout (sẽ học bài sau) |

---

## Bài tập thực hành

Hãy tự tay làm những bài tập sau:

### Bài 1: Cửa sổ thông tin
Tạo một cửa sổ có:
- Tiêu đề: "Giới thiệu bản thân"
- Kích thước: 400x250
- Màu nền: xám nhạt (#f0f0f0)
- Một label hiển thị tên và tuổi của bạn
- Một button "Đóng" để tắt ứng dụng (gợi ý: dùng `window.close()`)

### Bài 2: Ứng dụng đếm số (có kết nối signal)
Tạo ứng dụng với:
- Một label hiển thị số (ban đầu là 0)
- Một button "Tăng" - mỗi lần click tăng số lên 1
- Một button "Giảm" - mỗi lần click giảm số đi 1
- (Gợi ý: đã học `clicked.connect` ở ví dụ trên)

**Bonus:** Thêm QLineEdit để nhập số bước nhảy (ví dụ: mỗi lần tăng lên 5)

---

## Kiến thức cho bài sau

Ở bài 2, chúng ta sẽ học:
- **Layouts (QVBoxLayout, QHBoxLayout, QGridLayout)** - Thay vì dùng `move()` thủ công, Layout tự động sắp xếp các widget một cách thông minh.
- **QMainWindow** - Khung cửa sổ chuyên nghiệp với menu bar, toolbar, status bar.

---

## Tóm tắt bài học

1. **`QApplication`** là đối tượng duy nhất, quản lý toàn bộ ứng dụng.
2. **`QWidget`** là nền tảng của mọi giao diện.
3. **`parent`** tạo nên hệ thống phân cấp, giúp quản lý bộ nhớ và bố cục.
4. **`show()`** hiển thị widget, **`app.exec()`** bắt đầu vòng lặp sự kiện.
5. **Luôn luôn** đặt `app.exec()` ở cuối chương trình.

**Hãy nhớ:** Viết code và chạy thử ngay, đừng chỉ đọc. Lập trình GUI cần sự "cảm nhận" trực quan!

Bạn đã sẵn sàng cho Bài 2 về Layouts chưa? 😊