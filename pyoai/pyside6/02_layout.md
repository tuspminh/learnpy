# Khóa học PySide6 từ A-Z

# Buổi 2: Làm chủ Layout - Bí quyết xây dựng giao diện chuyên nghiệp

> **Mục tiêu của buổi học**
> 
> Sau buổi này, bạn sẽ:
> 
>   * Hiểu rõ Layout là gì và vì sao nó quan trọng. 
>   * Thành thạo `QVBoxLayout`, `QHBoxLayout`, `QGridLayout`, `QFormLayout`. 
>   * Biết cách lồng (Nested Layout). 
>   * Hiểu `stretch`, `spacing`, `margin`, `alignment`. 
>   * Biết cách xây dựng giao diện responsive. 
>   * Hoàn thành một ứng dụng "Quản lý thông tin sinh viên" với giao diện đẹp và khoa học. 
> 


* * *

# 1\. Tại sao phải dùng Layout?

Giả sử bạn muốn đặt 3 nút.

### Cách cũ (tọa độ tuyệt đối)
    
    
    button1.move(20, 20)
    button2.move(20, 60)
    button3.move(20, 100)

Nhược điểm:

  * Phải tự tính toán vị trí. 
  * Khi thay đổi kích thước cửa sổ, giao diện bị lệch. 
  * Khó bảo trì. 
  * Không responsive. 



* * *

### Dùng Layout
    
    
    +------------------------+
    | Button 1               |
    | Button 2               |
    | Button 3               |
    +------------------------+

Qt sẽ tự:

  * Căn chỉnh. 
  * Co giãn. 
  * Tính khoảng cách. 
  * Điều chỉnh theo kích thước cửa sổ. 



Đây là cách mà hầu hết các ứng dụng Qt chuyên nghiệp đều sử dụng.

* * *

# 2\. Các loại Layout trong Qt
    
    
    QLayout
    │
    ├── QVBoxLayout
    ├── QHBoxLayout
    ├── QGridLayout
    └── QFormLayout

Chúng ta sẽ học lần lượt từng loại.

* * *

# 3\. QVBoxLayout

Sắp xếp các widget theo **chiều dọc**.
    
    
    ----------------------
    Tên
    
    Địa chỉ
    
    Điện thoại
    
    Email
    ----------------------

### Ví dụ
    
    
    import sys
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QVBoxLayout,
        QWidget,
    )
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("QVBoxLayout")
    
    layout = QVBoxLayout()
    
    layout.addWidget(QLabel("Python"))
    layout.addWidget(QLabel("PySide6"))
    layout.addWidget(QLabel("SQLite"))
    layout.addWidget(QLabel("Requests"))
    
    window.setLayout(layout)
    
    window.show()
    
    app.exec()

Kết quả:
    
    
    Python
    
    PySide6
    
    SQLite
    
    Requests

* * *

# 4\. QHBoxLayout

Sắp xếp theo **chiều ngang**.
    
    
    Python    PySide6    SQLite

Ví dụ:
    
    
    layout = QHBoxLayout()
    
    layout.addWidget(QPushButton("Lưu"))
    layout.addWidget(QPushButton("Sửa"))
    layout.addWidget(QPushButton("Xóa"))

Kết quả:
    
    
    +--------------------------------+
    
    [Lưu] [Sửa] [Xóa]
    
    +--------------------------------+

* * *

# 5\. Kết hợp VBox và HBox

Đây là kỹ thuật sử dụng nhiều nhất.

Ví dụ:
    
    
    Tên
    
    [______________]
    
    Email
    
    [______________]
    
            [Lưu] [Thoát]

Trong đó:
    
    
    VBox
    │
    ├── Label
    ├── LineEdit
    ├── Label
    ├── LineEdit
    └── HBox
          ├── Button
          └── Button

Ví dụ:
    
    
    button_layout = QHBoxLayout()
    
    button_layout.addWidget(QPushButton("Lưu"))
    button_layout.addWidget(QPushButton("Thoát"))
    
    layout = QVBoxLayout()
    
    layout.addWidget(QLabel("Tên"))
    layout.addWidget(QLineEdit())
    
    layout.addWidget(QLabel("Email"))
    layout.addWidget(QLineEdit())
    
    layout.addLayout(button_layout)

Lưu ý: `addWidget()` dùng để thêm widget, còn `addLayout()` dùng để thêm một layout khác.

* * *

# 6\. QGridLayout

Bố trí theo **hàng** và **cột**.
    
    
    Tên      [________]
    
    Tuổi     [________]
    
    Địa chỉ  [________]

Ví dụ:
    
    
    grid = QGridLayout()
    
    grid.addWidget(QLabel("Tên"), 0, 0)
    grid.addWidget(QLineEdit(), 0, 1)
    
    grid.addWidget(QLabel("Tuổi"), 1, 0)
    grid.addWidget(QLineEdit(), 1, 1)
    
    grid.addWidget(QLabel("Địa chỉ"), 2, 0)
    grid.addWidget(QLineEdit(), 2, 1)

Tham số:
    
    
    addWidget(widget, row, column)

Ví dụ:
    
    
    grid.addWidget(QPushButton("Lưu"), 3, 0)
    grid.addWidget(QPushButton("Thoát"), 3, 1)

* * *

# 7\. QFormLayout

Đây là layout chuyên dùng cho các biểu mẫu nhập liệu.

Ví dụ:
    
    
    Tên:        [____________]
    
    Email:      [____________]
    
    Điện thoại: [____________]

Code:
    
    
    form = QFormLayout()
    
    form.addRow("Tên", QLineEdit())
    
    form.addRow("Email", QLineEdit())
    
    form.addRow("Điện thoại", QLineEdit())

Đây là cách được khuyến khích khi xây dựng các form nhập liệu.

* * *

# 8\. Layout lồng nhau (Nested Layout)

Các giao diện thực tế hầu như luôn kết hợp nhiều layout.

Ví dụ:
    
    
    VBox
    
    Tên
    
    [____________]
    
    Email
    
    [____________]
    
    HBox
    
    [Lưu]
    
    [Xóa]
    
    [Thoát]

Mô hình:
    
    
    VBox
    │
    ├── QLabel
    ├── QLineEdit
    ├── QLabel
    ├── QLineEdit
    └── HBox
          ├── QPushButton
          ├── QPushButton
          └── QPushButton

* * *

# 9\. Khoảng cách giữa các widget (Spacing)

Ví dụ:
    
    
    layout.setSpacing(20)

Khoảng cách giữa các widget sẽ là 20 pixel.

Nếu không thiết lập, Qt sẽ dùng giá trị mặc định.

* * *

# 10\. Lề (Margin)

Ví dụ:
    
    
    layout.setContentsMargins(20, 20, 20, 20)

Ý nghĩa:
    
    
    Trái 20
    
    Trên 20
    
    Phải 20
    
    Dưới 20

* * *

# 11\. Căn lề (Alignment)

Ví dụ:
    
    
    from PySide6.QtCore import Qt
    
    layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

Các kiểu căn phổ biến:
    
    
    AlignLeft
    
    AlignRight
    
    AlignCenter
    
    AlignTop
    
    AlignBottom

* * *

# 12\. Stretch - Co giãn thông minh

Ví dụ:
    
    
    layout.addStretch()
    
    
    Label
    
    LineEdit
    
    
    (khoảng trống)
    
    
    Button

Ví dụ khác:
    
    
    layout.addWidget(button1, stretch=1)
    layout.addWidget(button2, stretch=2)

Khi cửa sổ mở rộng, `button2` sẽ nhận nhiều không gian hơn `button1`.

* * *

# 13\. Responsive trong Qt

Ví dụ:
    
    
    +--------------------+
    
    Tên
    
    [____________________]
    
    Email
    
    [____________________]
    
    [Lưu]
    
    +--------------------+

Khi kéo rộng:
    
    
    +---------------------------------------+
    
    Tên
    
    [______________________________________]
    
    Email
    
    [______________________________________]
    
    [Lưu]
    
    +---------------------------------------+

Các `QLineEdit` sẽ tự giãn theo chiều ngang nếu được đặt trong layout phù hợp.

* * *

# 14\. Ví dụ hoàn chỉnh: Form đăng ký
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QFormLayout,
        QHBoxLayout,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Đăng ký")
    
    form = QFormLayout()
    
    name_edit = QLineEdit()
    email_edit = QLineEdit()
    phone_edit = QLineEdit()
    
    form.addRow("Tên", name_edit)
    form.addRow("Email", email_edit)
    form.addRow("Điện thoại", phone_edit)
    
    button_layout = QHBoxLayout()
    
    save_button = QPushButton("Lưu")
    cancel_button = QPushButton("Thoát")
    
    button_layout.addStretch()
    button_layout.addWidget(save_button)
    button_layout.addWidget(cancel_button)
    
    main_layout = QVBoxLayout()
    
    main_layout.addLayout(form)
    main_layout.addLayout(button_layout)
    
    window.setLayout(main_layout)
    
    window.resize(500, 250)
    
    window.show()
    
    app.exec()

Đây là cấu trúc mà bạn sẽ gặp rất nhiều trong các ứng dụng quản lý.

* * *

# 15\. Những lỗi thường gặp

### 1\. Quên gán layout cho cửa sổ

Sai:
    
    
    layout = QVBoxLayout()

Đúng:
    
    
    window.setLayout(layout)

* * *

### 2\. Dùng `addWidget()` để thêm layout

Sai:
    
    
    layout.addWidget(button_layout)

Đúng:
    
    
    layout.addLayout(button_layout)

* * *

### 3\. Đặt widget nhưng không thêm vào layout

Sai:
    
    
    edit = QLineEdit()

Đúng:
    
    
    layout.addWidget(edit)

* * *

### 4\. Trộn nhiều layout mà không có cấu trúc

Hãy lên sơ đồ trước khi viết mã. Ví dụ:
    
    
    VBox
    │
    ├── Form
    ├── GroupBox
    └── HBox

Điều này giúp giao diện rõ ràng và dễ bảo trì.

* * *

# Mini Project: Quản lý thông tin sinh viên

## Yêu cầu

Thiết kế giao diện gồm:
    
    
    -------------------------------------
    
    Họ tên
    
    [_____________________]
    
    Lớp
    
    [_____________________]
    
    Email
    
    [_____________________]
    
    Điện thoại
    
    [_____________________]
    
    -------------------------------------
    
              [Lưu]
    
              [Làm mới]
    
              [Thoát]
    
    -------------------------------------

## Gợi ý

  * Dùng `QVBoxLayout` làm layout chính. 
  * Dùng `QFormLayout` để tạo phần nhập liệu. 
  * Dùng `QHBoxLayout` cho các nút. 
  * Thêm `addStretch()` để đẩy nhóm nút sang bên phải hoặc tạo khoảng cách hợp lý. 
  * Thiết lập `spacing` và `contentsMargins` để giao diện thông thoáng. 



* * *

# Kiến thức thực tế

Trong các dự án PySide6 lớn, bạn gần như **không dùng`move()` hay `resize()` để đặt từng widget**. Thay vào đó:

  * Layout quyết định vị trí và kích thước. 
  * Widget chỉ tập trung vào chức năng. 
  * Giao diện dễ thay đổi, hỗ trợ nhiều độ phân giải và phù hợp với nhiều hệ điều hành. 



Đây là nền tảng để sau này chúng ta học **Qt Designer** , **MainWindow** , **DockWidget** , **QSplitter** , **QTabWidget** và xây dựng những phần mềm chuyên nghiệp.

## Chuẩn bị cho Buổi 3

Ở **Buổi 3** , chúng ta sẽ học sâu về các widget nhập liệu quan trọng nhất:

  * `QLineEdit`
  * `QTextEdit`
  * `QPlainTextEdit`
  * `QLabel`
  * `QPushButton`
  * Placeholder, Echo Mode (mật khẩu), Validator 
  * Đọc và ghi dữ liệu từ các widget 
  * Xây dựng ứng dụng **Đăng nhập** và **Ghi chú (Notepad mini)** với mã nguồn hoàn chỉnh và giải thích chi tiết từng dòng.

