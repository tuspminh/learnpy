# Khóa học PySide6 từ A-Z

# Buổi 3: Làm chủ các Widget cơ bản (QLabel, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit)

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu rõ sự khác nhau giữa các widget hiển thị và nhập liệu. 
>   * Thành thạo `QLabel`, `QPushButton`, `QLineEdit`, `QTextEdit`, `QPlainTextEdit`. 
>   * Biết cách đọc và ghi dữ liệu giữa các widget. 
>   * Biết xử lý các thuộc tính quan trọng như `placeholder`, `echoMode`, `readOnly`, `clear()`, `setText()`, `text()`. 
>   * Xây dựng ứng dụng **Đăng nhập** và **Notepad Mini**. 
> 


* * *

# 1\. Hệ thống Widget trong Qt

Trong Qt, gần như mọi thành phần giao diện đều kế thừa từ `QWidget`.
    
    
    QWidget
    │
    ├── QLabel
    ├── QPushButton
    ├── QLineEdit
    ├── QTextEdit
    ├── QPlainTextEdit
    ├── QListWidget
    ├── QTreeWidget
    ├── QTableWidget
    └── ...

Hôm nay chúng ta sẽ học 5 widget được sử dụng nhiều nhất.

* * *

# 2\. QLabel

`QLabel` dùng để:

  * Hiển thị văn bản. 
  * Hiển thị hình ảnh. 
  * Hiển thị HTML đơn giản. 



Ví dụ:
    
    
    label = QLabel("Xin chào PySide6")

* * *

## Đổi nội dung
    
    
    label.setText("Python")

Lấy nội dung:
    
    
    print(label.text())

* * *

## Căn lề
    
    
    from PySide6.QtCore import Qt
    
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

Các kiểu căn:
    
    
    AlignLeft
    AlignRight
    AlignCenter
    AlignTop
    AlignBottom

* * *

## Đổi font
    
    
    from PySide6.QtGui import QFont
    
    font = QFont("Arial", 16)
    
    label.setFont(font)

* * *

## Đổi màu

Tạm thời dùng CSS:
    
    
    label.setStyleSheet("""
    color: blue;
    font-size:20px;
    font-weight:bold;
    """)

QSS (Qt Style Sheet) sẽ được học kỹ ở Buổi 41.

* * *

# 3\. QPushButton

Tạo nút:
    
    
    button = QPushButton("Đăng nhập")

Đổi chữ:
    
    
    button.setText("OK")

* * *

## Tắt nút
    
    
    button.setEnabled(False)

Bật lại:
    
    
    button.setEnabled(True)

* * *

## Đổi kích thước
    
    
    button.setFixedSize(120, 40)

* * *

## Sự kiện click
    
    
    button.clicked.connect(my_function)

Ví dụ:
    
    
    def hello():
        print("Xin chào")
    
    button.clicked.connect(hello)

* * *

# 4\. QLineEdit

Đây là widget nhập **một dòng**.

Ví dụ:
    
    
    edit = QLineEdit()

* * *

## Placeholder
    
    
    edit.setPlaceholderText("Nhập họ tên...")

Kết quả:
    
    
    __________________________
    
    Nhập họ tên...

* * *

## Đọc dữ liệu
    
    
    name = edit.text()

* * *

## Ghi dữ liệu
    
    
    edit.setText("Nguyễn Văn A")

* * *

## Xóa
    
    
    edit.clear()

* * *

## Chỉ đọc
    
    
    edit.setReadOnly(True)

* * *

## Giới hạn độ dài
    
    
    edit.setMaxLength(20)

* * *

## Mật khẩu
    
    
    from PySide6.QtWidgets import QLineEdit
    
    password = QLineEdit()
    
    password.setEchoMode(QLineEdit.EchoMode.Password)

Kết quả:
    
    
    ************

Các chế độ:
    
    
    Normal
    
    NoEcho
    
    Password
    
    PasswordEchoOnEdit

* * *

# 5\. Ví dụ Login
    
    
    username = QLineEdit()
    password = QLineEdit()
    
    password.setEchoMode(QLineEdit.EchoMode.Password)

* * *

# 6\. QTextEdit

Đây là ô nhập **nhiều dòng**.

Ví dụ:
    
    
    text = QTextEdit()

* * *

## Ghi dữ liệu
    
    
    text.setPlainText("Xin chào")

* * *

## Đọc dữ liệu
    
    
    content = text.toPlainText()

* * *

## Append
    
    
    text.append("Python")

Kết quả:
    
    
    Xin chào
    
    Python

* * *

## Xóa
    
    
    text.clear()

* * *

## HTML

`QTextEdit` hỗ trợ HTML.
    
    
    text.setHtml("""
    <h1>Hello</h1>
    
    <b>Python</b>
    """)

Đây là điểm khác biệt lớn so với `QPlainTextEdit`.

* * *

# 7\. QPlainTextEdit

Widget này cũng nhập nhiều dòng.

Nhưng:

  * Nhanh hơn 
  * Tối ưu hơn 
  * Không hỗ trợ HTML 



Rất thích hợp để:

  * Code Editor 
  * Log Viewer 
  * Terminal 
  * IDE 



Ví dụ:
    
    
    editor = QPlainTextEdit()

Đọc dữ liệu:
    
    
    editor.toPlainText()

* * *

# 8\. QTextEdit hay QPlainTextEdit?

QTextEdit| QPlainTextEdit  
---|---  
Có HTML| Không HTML  
Rich Text| Plain Text  
Email| Code Editor  
Ghi chú đẹp| IDE  
  
* * *

# 9\. Ví dụ hoàn chỉnh: Form đăng nhập
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QFormLayout,
        QHBoxLayout,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    
    
    def login():
        user = username_edit.text().strip()
        password = password_edit.text()
    
        if user == "admin" and password == "123456":
            QMessageBox.information(window, "Thông báo", "Đăng nhập thành công!")
        else:
            QMessageBox.warning(window, "Lỗi", "Sai tài khoản hoặc mật khẩu!")
    
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Đăng nhập")
    
    main_layout = QVBoxLayout()
    
    form = QFormLayout()
    
    username_edit = QLineEdit()
    username_edit.setPlaceholderText("Tên đăng nhập")
    
    password_edit = QLineEdit()
    password_edit.setPlaceholderText("Mật khẩu")
    password_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    form.addRow("Tài khoản:", username_edit)
    form.addRow("Mật khẩu:", password_edit)
    
    button_layout = QHBoxLayout()
    
    login_button = QPushButton("Đăng nhập")
    exit_button = QPushButton("Thoát")
    
    login_button.clicked.connect(login)
    exit_button.clicked.connect(window.close)
    
    button_layout.addStretch()
    button_layout.addWidget(login_button)
    button_layout.addWidget(exit_button)
    
    main_layout.addLayout(form)
    main_layout.addLayout(button_layout)
    
    window.setLayout(main_layout)
    
    window.resize(420, 180)
    window.show()
    
    app.exec()

### Kiến thức rút ra

  * `QLineEdit.text()` lấy dữ liệu. 
  * `QLineEdit.setText()` gán dữ liệu. 
  * `strip()` loại bỏ khoảng trắng đầu và cuối. 
  * `QMessageBox` dùng để hiển thị thông báo. 
  * Kết hợp `QFormLayout` và `QHBoxLayout` giúp giao diện rõ ràng, dễ mở rộng. 



* * *

# 10\. Ví dụ hoàn chỉnh: Notepad Mini
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QPlainTextEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    
    
    def clear_text():
        editor.clear()
    
    
    def load_demo():
        editor.setPlainText(
            "Đây là ví dụ về QPlainTextEdit.\n"
            "Bạn có thể nhập nhiều dòng văn bản."
        )
    
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Notepad Mini")
    
    main_layout = QVBoxLayout()
    
    editor = QPlainTextEdit()
    
    button_layout = QHBoxLayout()
    
    load_button = QPushButton("Nạp mẫu")
    clear_button = QPushButton("Xóa")
    
    load_button.clicked.connect(load_demo)
    clear_button.clicked.connect(clear_text)
    
    button_layout.addWidget(load_button)
    button_layout.addWidget(clear_button)
    
    main_layout.addWidget(editor)
    main_layout.addLayout(button_layout)
    
    window.setLayout(main_layout)
    
    window.resize(600, 400)
    
    window.show()
    
    app.exec()

* * *

# 11\. Các phương thức quan trọng cần nhớ

## QLabel

Phương thức| Chức năng  
---|---  
`setText()`| Đổi nội dung  
`text()`| Lấy nội dung  
`setAlignment()`| Căn lề  
`setFont()`| Đổi font  
`setStyleSheet()`| Đổi giao diện  
  
* * *

## QPushButton

Phương thức| Chức năng  
---|---  
`setText()`| Đổi chữ  
`clicked.connect()`| Bắt sự kiện nhấn  
`setEnabled()`| Bật/tắt nút  
`setFixedSize()`| Đặt kích thước  
  
* * *

## QLineEdit

Phương thức| Chức năng  
---|---  
`text()`| Lấy dữ liệu  
`setText()`| Gán dữ liệu  
`clear()`| Xóa  
`setPlaceholderText()`| Gợi ý nhập  
`setEchoMode()`| Chế độ hiển thị (mật khẩu)  
`setReadOnly()`| Chỉ đọc  
`setMaxLength()`| Giới hạn ký tự  
  
* * *

## QTextEdit / QPlainTextEdit

Phương thức| Chức năng  
---|---  
`setPlainText()`| Gán văn bản  
`toPlainText()`| Lấy văn bản  
`append()` _(QTextEdit)_|  Thêm dòng mới  
`clear()`| Xóa nội dung  
  
* * *

# Những lỗi người mới thường gặp

  1. **Quên gọi`text()`**: 


    
    
    # Sai
    print(username_edit)
    
    # Đúng
    print(username_edit.text())

  2. **Nhầm`setText()` với `text()`**: 


  * `setText("ABC")` để gán. 
  * `text()` để lấy. 


  3. **Dùng`QTextEdit.text()`**: 


    
    
    # Sai
    content = text_edit.text()
    
    # Đúng
    content = text_edit.toPlainText()

  4. **Quên`EchoMode.Password`** khi nhập mật khẩu, khiến mật khẩu hiển thị công khai. 



* * *

# Bài tập thực hành

### Bài 1

Tạo form gồm:

  * Họ tên 
  * Email 
  * Số điện thoại 



Khi nhấn **Hiển thị** , in toàn bộ thông tin ra terminal.

* * *

### Bài 2

Tạo form đổi mật khẩu:

  * Mật khẩu cũ 
  * Mật khẩu mới 
  * Nhập lại mật khẩu 



Cả ba ô đều sử dụng `EchoMode.Password`.

* * *

### Bài 3

Tạo ứng dụng ghi chú:

  * Một `QPlainTextEdit`. 
  * Nút **Xóa**. 
  * Nút **Nạp văn bản mẫu**. 
  * Nút **Đếm số dòng** (gợi ý: `len(editor.toPlainText().splitlines())`). 



* * *

### Bài 4

Tạo ứng dụng "Thông tin cá nhân":

  * `QLabel` tiêu đề. 
  * `QLineEdit` nhập họ tên. 
  * `QTextEdit` nhập địa chỉ. 
  * Nút **Lưu** hiển thị thông tin bằng `QMessageBox`. 



* * *

# Mini Project cuối buổi: Quản lý ghi chú cá nhân

Xây dựng một ứng dụng với:

  * Tiêu đề ở trên (`QLabel`). 
  * Một `QPlainTextEdit` chiếm toàn bộ vùng nhập liệu. 
  * Ba nút: **Mở mẫu** , **Xóa** , **Thoát**. 
  * Khi nhấn **Mở mẫu** , hiển thị một đoạn văn bản có nhiều dòng. 
  * Khi nhấn **Xóa** , làm trống vùng nhập liệu. 
  * Khi nhấn **Thoát** , đóng ứng dụng. 



## Tổng kết Buổi 3

Bạn đã thành thạo các widget nền tảng được sử dụng trong hầu hết các ứng dụng PySide6:

  * `QLabel`
  * `QPushButton`
  * `QLineEdit`
  * `QTextEdit`
  * `QPlainTextEdit`



Đồng thời, bạn đã biết cách:

  * Đọc và ghi dữ liệu. 
  * Xử lý nhập liệu một dòng và nhiều dòng. 
  * Tạo form đăng nhập. 
  * Xây dựng một ứng dụng ghi chú đơn giản. 



Ở **Buổi 4** , chúng ta sẽ học các widget nhập liệu nâng cao như:

  * `QSpinBox`
  * `QDoubleSpinBox`
  * `QComboBox`
  * `QCheckBox`
  * `QRadioButton`
  * `QSlider`
  * `QDateEdit`
  * `QTimeEdit`



và xây dựng một **Form đăng ký thông tin hoàn chỉnh** với kiểm tra dữ liệu đầu vào theo phong cách ứng dụng chuyên nghiệp.

