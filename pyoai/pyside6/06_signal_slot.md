# Khóa học PySide6 từ A-Z

# Buổi 6: Làm chủ Signal & Slot - Trái tim của PySide6

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Signal và Slot là gì. 
>   * Biết cách kết nối (`connect`) và ngắt kết nối (`disconnect`). 
>   * Biết sử dụng các Signal phổ biến của widget. 
>   * Hiểu cơ chế Event-Driven Programming (lập trình hướng sự kiện). 
>   * Biết tạo nhiều Slot cho một Signal và một Slot cho nhiều Signal. 
>   * Biết truyền tham số qua Signal. 
>   * Xây dựng ứng dụng tương tác chuyên nghiệp. 
> 


* * *

# 1\. Event-Driven Programming là gì?

Cho đến nay, các chương trình Python bạn viết chủ yếu chạy theo thứ tự:
    
    
    print("Bắt đầu")
    
    a = 10
    b = 20
    
    print(a + b)
    
    print("Kết thúc")

Luồng chạy:
    
    
    Bắt đầu
       ↓
    Tính toán
       ↓
    Kết thúc

* * *

Trong GUI thì khác.

Chương trình luôn **đứng chờ** người dùng thao tác.
    
    
    Mở chương trình
    
    ↓
    
    Chờ...
    
    ↓
    
    Người dùng nhấn nút
    
    ↓
    
    Xử lý
    
    ↓
    
    Chờ...
    
    ↓
    
    Người dùng nhập dữ liệu
    
    ↓
    
    Xử lý
    
    ↓
    
    Chờ...

Đây gọi là **Event-Driven Programming**.

* * *

# 2\. Signal là gì?

Signal là **tín hiệu** do widget phát ra khi có sự kiện xảy ra.

Ví dụ:

  * Nhấn nút 
  * Đổi nội dung 
  * Kéo Slider 
  * Chọn ComboBox 
  * Đóng cửa sổ 



Ví dụ:
    
    
    Button
    
    ↓
    
    clicked Signal

* * *

# 3\. Slot là gì?

Slot là **hàm nhận Signal**.

Ví dụ:
    
    
    def hello():
        print("Xin chào")

Ở đây:
    
    
    hello()
    
    ↓
    
    Slot

* * *

# 4\. connect()

Kết nối Signal với Slot.
    
    
    button.clicked.connect(hello)

Luồng hoạt động:
    
    
    Button
    
    ↓
    
    clicked
    
    ↓
    
    connect()
    
    ↓
    
    hello()
    
    ↓
    
    print()

* * *

# 5\. Ví dụ đầu tiên
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QPushButton,
    )
    
    app = QApplication(sys.argv)
    
    button = QPushButton("Nhấn tôi")
    
    
    def hello():
        print("Xin chào PySide6")
    
    
    button.clicked.connect(hello)
    
    button.show()
    
    app.exec()

Khi nhấn nút:
    
    
    Xin chào PySide6

* * *

# 6\. Signal phổ biến

## QPushButton

Signal| Ý nghĩa  
---|---  
clicked| Nhấn xong  
pressed| Vừa nhấn xuống  
released| Thả chuột  
toggled| Dành cho nút bật/tắt  
  
* * *

## QLineEdit

Signal| Ý nghĩa  
---|---  
textChanged| Nội dung thay đổi  
textEdited| Người dùng sửa  
editingFinished| Nhấn Enter hoặc mất focus  
returnPressed| Nhấn Enter  
  
* * *

## QComboBox

Signal  
---  
currentTextChanged  
currentIndexChanged  
  
* * *

## QSpinBox
    
    
    valueChanged

* * *

## QSlider
    
    
    valueChanged

* * *

# 7\. Ví dụ textChanged
    
    
    from PySide6.QtWidgets import (
        QApplication,
        QLineEdit,
    )
    
    app = QApplication([])
    
    edit = QLineEdit()
    
    
    def changed(text):
        print(text)
    
    
    edit.textChanged.connect(changed)
    
    edit.show()
    
    app.exec()

Nếu nhập:
    
    
    Python

Terminal:
    
    
    P
    
    Py
    
    Pyt
    
    Pyth
    
    Python

* * *

# 8\. Một Signal → nhiều Slot
    
    
    def a():
        print("A")
    
    
    def b():
        print("B")
    
    
    button.clicked.connect(a)
    button.clicked.connect(b)

Kết quả:
    
    
    A
    
    B

Một Signal có thể kết nối với nhiều Slot.

* * *

# 9\. Nhiều Signal → một Slot
    
    
    button1.clicked.connect(save)
    
    button2.clicked.connect(save)

Hai nút khác nhau cùng gọi một hàm `save()`.

Đây là cách giúp tái sử dụng mã nguồn.

* * *

# 10\. disconnect()

Ngắt kết nối.
    
    
    button.clicked.disconnect()

Hoặc:
    
    
    button.clicked.disconnect(hello)

Sau khi ngắt, nhấn nút sẽ không gọi `hello()` nữa.

* * *

# 11\. Truyền tham số

Một số Signal tự động gửi dữ liệu.

Ví dụ:
    
    
    def changed(value):
        print(value)
    
    
    slider.valueChanged.connect(changed)

Nếu Slider là:
    
    
    75

Thì:
    
    
    75

được truyền vào hàm.

* * *

# 12\. Ví dụ Slider
    
    
    import sys
    
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QSlider,
        QVBoxLayout,
        QWidget,
    )
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    
    layout = QVBoxLayout()
    
    label = QLabel("0")
    
    slider = QSlider(Qt.Orientation.Horizontal)
    
    slider.setRange(0, 100)
    
    
    def update(value):
        label.setText(str(value))
    
    
    slider.valueChanged.connect(update)
    
    layout.addWidget(label)
    layout.addWidget(slider)
    
    window.setLayout(layout)
    
    window.show()
    
    app.exec()

* * *

# 13\. Signal có tham số

Ví dụ:
    
    
    combo.currentTextChanged.connect(print)

Nếu chọn:
    
    
    Python

Terminal:
    
    
    Python

* * *

# 14\. Kiểm tra Checkbox
    
    
    check.toggled.connect(print)

Kết quả:
    
    
    True
    
    False

* * *

# 15\. Ví dụ thực tế: Form đăng nhập
    
    
    def login():
    
        user = username.text()
    
        password = pwd.text()
    
        print(user)
    
        print(password)
    
    
    login_button.clicked.connect(login)

Mỗi lần nhấn nút:

Signal

↓

Slot

↓

Đăng nhập

* * *

# 16\. Lambda

Đôi khi ta cần truyền thêm dữ liệu.

Ví dụ:
    
    
    button.clicked.connect(
        lambda: print("Xin chào")
    )

Hoặc:
    
    
    button.clicked.connect(
        lambda: save(5)
    )

Trong đó:
    
    
    def save(id):
        print(id)

Kết quả:
    
    
    5

> Chúng ta sẽ học sâu về `lambda` ở **Buổi 7**.

* * *

# 17\. Ví dụ hoàn chỉnh: Máy tính cộng
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    
    layout = QVBoxLayout()
    
    a = QLineEdit()
    b = QLineEdit()
    
    result = QLabel("Kết quả")
    
    button = QPushButton("Cộng")
    
    
    def calculate():
        try:
            x = float(a.text())
            y = float(b.text())
    
            result.setText(f"Kết quả: {x+y}")
    
        except ValueError:
            result.setText("Vui lòng nhập số hợp lệ")
    
    
    button.clicked.connect(calculate)
    
    layout.addWidget(a)
    layout.addWidget(b)
    layout.addWidget(button)
    layout.addWidget(result)
    
    window.setLayout(layout)
    
    window.show()
    
    app.exec()

* * *

# 18\. Signal và Slot hoạt động như thế nào?
    
    
    Người dùng
    
    ↓
    
    Nhấn nút
    
    ↓
    
    Button.clicked
    
    ↓
    
    Qt Event Loop
    
    ↓
    
    connect()
    
    ↓
    
    Slot
    
    ↓
    
    Cập nhật giao diện

Đây là lý do PySide6 phản hồi nhanh và không cần bạn tự kiểm tra chuột hay bàn phím liên tục.

* * *

# 19\. Những lỗi người mới thường gặp

## Sai 1
    
    
    button.clicked.connect(hello())

Sai vì `hello()` được gọi **ngay khi chạy chương trình**.

Đúng:
    
    
    button.clicked.connect(hello)

Chỉ truyền **tên hàm** , không gọi hàm.

* * *

## Sai 2

Không xử lý lỗi khi chuyển kiểu:
    
    
    int(edit.text())

Nếu người dùng nhập:
    
    
    abc

Chương trình sẽ lỗi.

Hãy dùng:
    
    
    try:
        ...
    except ValueError:
        ...

* * *

## Sai 3

Quên tham số của Signal

Ví dụ:
    
    
    slider.valueChanged.connect(update)

thì hàm phải nhận một tham số:
    
    
    def update(value):
        ...

* * *

# 20\. Bài tập thực hành

## Bài 1

Tạo một `QPushButton`.

Mỗi lần nhấn:
    
    
    Hello Python

được in ra terminal.

* * *

## Bài 2

Tạo một `QLineEdit`.

Mỗi lần nhập:

Hiển thị ngay nội dung lên `QLabel`.

_Gợi ý:_ dùng `textChanged`.

* * *

## Bài 3

Tạo `QSlider`.

Giá trị Slider luôn hiển thị trên Label.

* * *

## Bài 4

Tạo 3 nút:

  * Đỏ 
  * Xanh 
  * Vàng 



Khi nhấn từng nút:

In ra tên màu tương ứng.

* * *

## Bài 5

Viết máy tính cộng:

  * Hai `QLineEdit`. 
  * Một nút **Tính**. 
  * Một `QLabel` hiển thị kết quả. 
  * Kiểm tra dữ liệu đầu vào hợp lệ. 



* * *

# Mini Project cuối buổi: Bộ chuyển đổi nhiệt độ

Thiết kế giao diện gồm:

  * `QLineEdit` nhập nhiệt độ °C. 
  * Nút **Chuyển đổi**. 
  * `QLabel` hiển thị kết quả °F. 



Công thức:
    
    
    °F = °C × 9 / 5 + 32

Yêu cầu:

  * Sử dụng Signal `clicked`. 
  * Kiểm tra dữ liệu nhập. 
  * Nếu nhập sai, hiển thị thông báo lỗi trên `QLabel` hoặc `QMessageBox`. 



* * *

# Tổng kết Buổi 6

Bạn đã học được phần cốt lõi của lập trình giao diện với PySide6:

  * Hiểu mô hình **Event-Driven Programming**. 
  * Phân biệt **Signal** và **Slot**. 
  * Sử dụng `connect()` và `disconnect()`. 
  * Kết nối một Signal với nhiều Slot và ngược lại. 
  * Nhận tham số từ Signal. 
  * Xử lý các sự kiện phổ biến của `QPushButton`, `QLineEdit`, `QSlider`, `QComboBox`,... 



Đây là nền tảng để xây dựng mọi ứng dụng Qt, từ công cụ nhỏ đến phần mềm quản lý lớn.

## Chuẩn bị cho Buổi 7

Ở **Buổi 7** , chúng ta sẽ học các kỹ thuật nâng cao với Signal & Slot:

  * `lambda` trong `connect()`. 
  * `functools.partial`. 
  * Tự tạo **Signal** bằng lớp `Signal`. 
  * Tự tạo **Slot** với `@Slot`. 
  * Giao tiếp giữa nhiều cửa sổ (`MainWindow` ↔ `Dialog`). 
  * Truyền dữ liệu giữa các đối tượng. 



Đây là những kỹ thuật mà các lập trình viên PySide6 chuyên nghiệp sử dụng để xây dựng ứng dụng có kiến trúc rõ ràng và dễ bảo trì.

