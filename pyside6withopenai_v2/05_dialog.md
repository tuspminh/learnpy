# Khóa học PySide6 từ A-Z

# Buổi 5: Làm chủ Dialog - QMessageBox, QFileDialog, QColorDialog, QFontDialog, QInputDialog

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
> - Hiểu Dialog là gì và khi nào nên sử dụng.
> - Thành thạo các Dialog chuẩn của Qt.
> - Biết mở/lưu tập tin.
> - Biết chọn font và màu chữ.
> - Biết yêu cầu người dùng nhập dữ liệu bằng hộp thoại.
> - Hoàn thành ứng dụng **Notepad Pro phiên bản 1.0**.

---

# 1. Dialog là gì?

Dialog là **cửa sổ phụ** dùng để:

- Thông báo
- Cảnh báo
- Hỏi người dùng
- Chọn file
- Chọn thư mục
- Chọn font
- Chọn màu
- Nhập dữ liệu

Ví dụ:

```text-x-trilium-auto
+----------------------------+
|       Thông báo            |
|                            |
| Đã lưu thành công!          |
|                            |
|          [ OK ]            |
+----------------------------+
```

Trong Qt, hầu hết Dialog đều kế thừa từ `QDialog`.

---

# 2. Các Dialog chuẩn của Qt

```text-x-trilium-auto
QDialog
│
├── QMessageBox
├── QFileDialog
├── QColorDialog
├── QFontDialog
├── QInputDialog
└── ...
```

Đây là các Dialog mà bạn sẽ dùng gần như hàng ngày.

---

# 3. QMessageBox

Đây là Dialog được sử dụng nhiều nhất.

Có 4 loại phổ biến:

```text-x-trilium-auto
Information

Warning

Critical

Question
```

---

# 4. Information

```text-x-trilium-auto
QMessageBox.information(
    self,
    "Thông báo",
    "Lưu thành công!"
)
```

Kết quả:

```text-x-trilium-auto
ℹ Đã lưu thành công!
```

---

# 5. Warning

```text-x-trilium-auto
QMessageBox.warning(
    self,
    "Cảnh báo",
    "Bạn chưa nhập tên!"
)
```

---

# 6. Critical

```text-x-trilium-auto
QMessageBox.critical(
    self,
    "Lỗi",
    "Không mở được file!"
)
```

---

# 7. Question

```text-x-trilium-auto
answer = QMessageBox.question(
    self,
    "Thoát",
    "Bạn có muốn thoát không?"
)
```

Kết quả:

```text-x-trilium-auto
Yes

No
```

---

## Kiểm tra kết quả

```text-x-trilium-auto
if answer == QMessageBox.StandardButton.Yes:
    print("Thoát")
```

---

# 8. QFileDialog

Dialog mở file.

Ví dụ:

```text-x-trilium-auto
filename, _ = QFileDialog.getOpenFileName(
    self,
    "Mở file"
)
```

Ví dụ kết quả:

```text-x-trilium-auto
C:/Users/Admin/Desktop/test.txt
```

---

## Bộ lọc

```text-x-trilium-auto
filename, _ = QFileDialog.getOpenFileName(
    self,
    "Mở",

    "",

    "Text (*.txt)"
)
```

---

## Nhiều định dạng

```text-x-trilium-auto
"Text (*.txt);;Python (*.py);;All Files (*)"
```

---

## Lưu file

```text-x-trilium-auto
filename, _ = QFileDialog.getSaveFileName(
    self,
    "Lưu file"
)
```

---

## Chọn thư mục

```text-x-trilium-auto
folder = QFileDialog.getExistingDirectory(
    self,
    "Chọn thư mục"
)
```

---

# 9. Đọc file

Ví dụ:

```text-x-trilium-auto
with open(filename, "r", encoding="utf8") as f:
    text = f.read()
```

---

# 10. Ghi file

```text-x-trilium-auto
with open(filename, "w", encoding="utf8") as f:
    f.write(editor.toPlainText())
```

---

# 11. QColorDialog

Chọn màu.

```text-x-trilium-auto
color = QColorDialog.getColor()
```

---

## Kiểm tra

```text-x-trilium-auto
if color.isValid():
    print(color.name())
```

Ví dụ:

```text-x-trilium-auto
#ff0000
```

---

## Đổi màu chữ

```text-x-trilium-auto
editor.setStyleSheet(
    f"color:{color.name()};"
)
```

---

# 12. QFontDialog

Chọn font.

```text-x-trilium-auto
font, ok = QFontDialog.getFont()
```

---

## Kiểm tra

```text-x-trilium-auto
if ok:
    editor.setFont(font)
```

---

# 13. QInputDialog

Nhập dữ liệu.

Ví dụ:

```text-x-trilium-auto
text, ok = QInputDialog.getText(
    self,

    "Tên",

    "Nhập tên:"
)
```

---

## Nhập số nguyên

```text-x-trilium-auto
number, ok = QInputDialog.getInt(
    self,

    "Tuổi",

    "Nhập tuổi:"
)
```

---

## Nhập số thực

```text-x-trilium-auto
value, ok = QInputDialog.getDouble(
    self,

    "Giá",

    "Nhập giá:"
)
```

---

## Chọn từ danh sách

```text-x-trilium-auto
item, ok = QInputDialog.getItem(
    self,

    "Ngôn ngữ",

    "Chọn",

    [
        "Python",
        "Rust",
        "Go"
    ]
)
```

---

# 14. Mini ví dụ

```text-x-trilium-auto
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

app = QApplication(sys.argv)

window = QWidget()

layout = QVBoxLayout()

button = QPushButton("Thông báo")

layout.addWidget(button)

window.setLayout(layout)


def hello():
    QMessageBox.information(
        window,

        "Thông báo",

        "Xin chào PySide6!"
    )


button.clicked.connect(hello)

window.show()

app.exec()
```

---

# 15. Dự án: Notepad Pro v1.0

Chúng ta sẽ xây dựng ứng dụng:

```text-x-trilium-auto
+--------------------------------------------+

 File Edit

---------------------------------------------

|                                            |
|                                            |
|            QTextEdit                       |
|                                            |
|                                            |
---------------------------------------------

[Mở]

[Lưu]

[Font]

[Màu]

[Đổi tiêu đề]

[Thoát]

+--------------------------------------------+
```

---

# Code hoàn chỉnh

```text-x-trilium-auto
import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QToolBar,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Notepad Pro")

        self.resize(800, 600)

        self.editor = QTextEdit()

        self.setCentralWidget(self.editor)

        self.create_toolbar()

    def create_toolbar(self):

        toolbar = QToolBar()

        self.addToolBar(toolbar)

        open_action = QAction("Mở", self)
        save_action = QAction("Lưu", self)
        font_action = QAction("Font", self)
        color_action = QAction("Màu", self)
        title_action = QAction("Tiêu đề", self)

        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addAction(font_action)
        toolbar.addAction(color_action)
        toolbar.addAction(title_action)

        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        font_action.triggered.connect(self.change_font)
        color_action.triggered.connect(self.change_color)
        title_action.triggered.connect(self.change_title)

    def open_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,

            "Mở file",

            "",

            "Text (*.txt);;All Files (*)"
        )

        if filename:

            with open(filename, encoding="utf8") as f:
                self.editor.setPlainText(f.read())

    def save_file(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,

            "Lưu file",

            "",

            "Text (*.txt)"
        )

        if filename:

            with open(filename, "w", encoding="utf8") as f:
                f.write(self.editor.toPlainText())

            QMessageBox.information(
                self,

                "Thông báo",

                "Lưu thành công!"
            )

    def change_font(self):

        font, ok = QFontDialog.getFont()

        if ok:
            self.editor.setFont(font)

    def change_color(self):

        color = QColorDialog.getColor()

        if color.isValid():

            self.editor.setStyleSheet(
                f"color:{color.name()};"
            )

    def change_title(self):

        title, ok = QInputDialog.getText(
            self,

            "Tiêu đề",

            "Nhập tiêu đề:"
        )

        if ok:
            self.setWindowTitle(title)


app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec()
```

---

# 16. Những lỗi người mới thường gặp

## Không kiểm tra `ok`

Sai:

```text-x-trilium-auto
font, ok = QFontDialog.getFont()

editor.setFont(font)
```

Nếu người dùng nhấn **Cancel**, bạn vẫn áp dụng font.

Đúng:

```text-x-trilium-auto
if ok:
    editor.setFont(font)
```

---

## Không kiểm tra file rỗng

Sai:

```text-x-trilium-auto
open(filename)
```

Đúng:

```text-x-trilium-auto
if filename:
```

---

## Không xử lý ngoại lệ

Nên viết:

```text-x-trilium-auto
try:
    ...
except Exception as e:
    QMessageBox.critical(
        self,
        "Lỗi",
        str(e)
    )
```

Đây là thói quen rất quan trọng trong ứng dụng thực tế.

---

# 17. Kiến thức thực tế: Tách giao diện và logic

Trong ví dụ trên, tất cả mã đều nằm trong một lớp để dễ học. Tuy nhiên, khi dự án lớn, chúng ta sẽ tách thành nhiều file:

```text-x-trilium-auto
project/
│
├── main.py
├── main_window.py
├── dialogs.py
├── file_manager.py
├── settings.py
├── resources/
│   ├── icons/
│   └── styles/
└── utils.py
```

Việc tách module giúp mã nguồn dễ đọc, dễ kiểm thử và mở rộng.

---

# Bài tập thực hành

## Bài 1: Trình xem văn bản

- Một `QTextEdit`.
- Nút **Mở**.
- Mở file `.txt` và hiển thị nội dung.

---

## Bài 2: Nhật ký cá nhân

- `QTextEdit`.
- Nút **Lưu**.
- Lưu nội dung ra file.

---

## Bài 3: Trình đổi giao diện

- `QTextEdit`.
- Nút **Đổi Font**.
- Nút **Đổi Màu**.
- Áp dụng ngay vào vùng soạn thảo.

---

## Bài 4: Đổi tiêu đề

- Một nút **Đổi tiêu đề**.
- Dùng `QInputDialog.getText()`.
- Cập nhật tiêu đề cửa sổ.

---

## Bài 5 (Nâng cao)

Xây dựng **Notepad Pro 2.0** với các chức năng:

- Mở file.
- Lưu file.
- Lưu thành file mới.
- Hỏi xác nhận khi thoát nếu tài liệu đã thay đổi.
- Hiển thị tên file trên tiêu đề cửa sổ.
- Hiển thị thông báo lỗi nếu không mở được file.

---

# Tổng kết Buổi 5

Trong buổi học này, bạn đã làm chủ các hộp thoại chuẩn của Qt:

- `QMessageBox` để thông báo, cảnh báo và xác nhận.
- `QFileDialog` để mở, lưu tệp và chọn thư mục.
- `QColorDialog` để chọn màu.
- `QFontDialog` để chọn font chữ.
- `QInputDialog` để nhập dữ liệu nhanh.

Đây là những thành phần không thể thiếu trong hầu hết các ứng dụng desktop.

---

# Chuẩn bị cho Buổi 6

Từ **Buổi 6**, chúng ta sẽ bước sang một chủ đề cực kỳ quan trọng: **Signal & Slot**.

Bạn sẽ học:

- Signal hoạt động như thế nào bên trong Qt.
- Slot là gì.
- `connect()`, `disconnect()`.
- Signal có tham số.
- Lambda trong Signal.
- Signal tự tạo (`Signal`).
- Slot tự tạo (`@Slot`).
- Giao tiếp giữa nhiều cửa sổ (Main Window ↔ Dialog).
- Xây dựng ứng dụng theo mô hình **event-driven** như các phần mềm chuyên nghiệp.

Đây là nền tảng để bạn hiểu cách mọi widget trong PySide6 giao tiếp với nhau và cũng là bước đầu để xây dựng các ứng dụng quy mô lớn.
