# Khóa học PySide6 từ A-Z

# Buổi 13: Dialog và Multi-Window Application - Xây dựng ứng dụng nhiều cửa sổ chuyên nghiệp

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu sự khác nhau giữa `QWidget`, `QMainWindow` và `QDialog`. 
>   * Thành thạo các Dialog có sẵn của Qt. 
>   * Tự tạo `QDialog` để nhập dữ liệu. 
>   * Truyền dữ liệu giữa nhiều cửa sổ bằng Signal/Slot. 
>   * Quản lý nhiều cửa sổ trong một ứng dụng theo cách chuyên nghiệp. 
> 


* * *

# 1\. Một ứng dụng thực tế có bao nhiêu cửa sổ?

Ví dụ phần mềm quản lý sinh viên:
    
    
    Main Window
    │
    ├── Thêm sinh viên
    ├── Sửa sinh viên
    ├── Xóa sinh viên
    ├── Cài đặt
    ├── Đăng nhập
    ├── Giới thiệu
    └── Xuất báo cáo

Không ai đưa tất cả vào một cửa sổ duy nhất.

* * *

# 2\. QWidget, QMainWindow và QDialog

Lớp| Mục đích  
---|---  
`QWidget`| Widget hoặc cửa sổ đơn giản  
`QMainWindow`| Cửa sổ chính của ứng dụng  
`QDialog`| Hộp thoại nhập dữ liệu, xác nhận  
  
Ví dụ:
    
    
    MainWindow
    
    ↓
    
    Nhấn "Thêm"
    
    ↓
    
    QDialog
    
    ↓
    
    Nhập thông tin
    
    ↓
    
    OK
    
    ↓
    
    MainWindow cập nhật

* * *

# 3\. Modal và Modeless Dialog

## Modal Dialog

Người dùng **phải xử lý hộp thoại trước**.

Ví dụ:
    
    
    Thông báo lỗi
    
    ↓
    
    Chỉ bấm OK
    
    ↓
    
    Mới làm tiếp được

Mở:
    
    
    dialog.exec()

* * *

## Modeless Dialog

Người dùng vẫn thao tác được cửa sổ chính.

Ví dụ:
    
    
    Find
    
    Replace
    
    History

Mở:
    
    
    dialog.show()

* * *

# 4\. Tạo Dialog đầu tiên
    
    
    from PySide6.QtWidgets import *
    
    class StudentDialog(QDialog):
    
        def __init__(self):
            super().__init__()
    
            self.setWindowTitle("Thêm sinh viên")
    
            layout = QVBoxLayout()
    
            layout.addWidget(QLabel("Tên"))
    
            layout.addWidget(QLineEdit())
    
            layout.addWidget(QPushButton("OK"))
    
            self.setLayout(layout)

Mở:
    
    
    dialog = StudentDialog()
    
    dialog.exec()

* * *

# 5\. exec() và show()

exec()| show()  
---|---  
Modal| Modeless  
Chờ Dialog đóng| Không chờ  
Có giá trị trả về| Không có  
  
* * *

# 6\. accept() và reject()

Qt quy định:
    
    
    self.accept()

↓
    
    
    Dialog thành công

* * *
    
    
    self.reject()

↓
    
    
    Dialog bị hủy

* * *

Ví dụ:
    
    
    button_ok.clicked.connect(self.accept)
    
    button_cancel.clicked.connect(self.reject)

* * *

# 7\. Giá trị trả về của exec()
    
    
    result = dialog.exec()

Nếu:
    
    
    OK

↓
    
    
    QDialog.DialogCode.Accepted

Nếu:
    
    
    Cancel

↓
    
    
    QDialog.DialogCode.Rejected

* * *

# 8\. QMessageBox

Qt có sẵn nhiều MessageBox.

* * *

## Information
    
    
    QMessageBox.information(
        self,
        "Thông báo",
        "Lưu thành công"
    )

* * *

## Warning
    
    
    QMessageBox.warning(
        self,
        "Cảnh báo",
        "Email không hợp lệ"
    )

* * *

## Critical
    
    
    QMessageBox.critical(
        self,
        "Lỗi",
        "Không kết nối được Database"
    )

* * *

## Question
    
    
    answer = QMessageBox.question(
        self,
        "Xóa",
    
        "Bạn có chắc?"
    )

* * *

Kiểm tra:
    
    
    if answer == QMessageBox.StandardButton.Yes:
        ...

* * *

# 9\. QFileDialog

Mở file:
    
    
    filename, _ = QFileDialog.getOpenFileName(
        self,
    
        "Chọn File",
    
        "",
    
        "Images (*.png *.jpg)"
    )

* * *

Lưu file:
    
    
    filename, _ = QFileDialog.getSaveFileName(
        self,
    
        "Lưu File"
    )

* * *

# 10\. QColorDialog
    
    
    color = QColorDialog.getColor()

Nếu:
    
    
    color.isValid()

↓

Lấy:
    
    
    color.name()

Ví dụ:
    
    
    #2196F3

* * *

# 11\. QFontDialog
    
    
    font, ok = QFontDialog.getFont()

Nếu:
    
    
    ok

↓
    
    
    label.setFont(font)

* * *

# 12\. QInputDialog

Nhập chuỗi:
    
    
    text, ok = QInputDialog.getText(
        self,
    
        "Tên",
    
        "Nhập tên:"
    )

* * *

Nhập số:
    
    
    number, ok = QInputDialog.getInt(
        self,
    
        "Tuổi",
    
        "Nhập tuổi:"
    )

* * *

# 13\. QProgressDialog

Ví dụ:
    
    
    progress = QProgressDialog(
        "Đang xử lý...",
    
        "Hủy",
    
        0,
    
        100
    )

Cập nhật:
    
    
    progress.setValue(50)

> Trong ứng dụng thực tế, `QProgressDialog` thường được kết hợp với `QThread` để giao diện không bị treo khi xử lý tác vụ dài.

* * *

# 14\. Truyền dữ liệu bằng Signal

Đây là cách chuyên nghiệp nhất.

Dialog:
    
    
    from PySide6.QtCore import Signal
    
    class StudentDialog(QDialog):
    
        studentCreated = Signal(str)

* * *

Khi nhấn OK:
    
    
    self.studentCreated.emit(
        self.txtName.text()
    )

* * *

MainWindow:
    
    
    dialog.studentCreated.connect(
        self.add_student
    )

* * *

Slot:
    
    
    def add_student(name):
    
        print(name)

* * *

# 15\. Không nên làm

Sai:
    
    
    parent.label.setText(...)

Dialog sửa trực tiếp MainWindow.

Điều này làm hai lớp phụ thuộc chặt chẽ vào nhau.

* * *

Nên:
    
    
    Dialog
    
    ↓
    
    Signal
    
    ↓
    
    MainWindow

Đây là cách thiết kế đúng theo nguyên tắc tách biệt trách nhiệm.

* * *

# 16\. Ví dụ hoàn chỉnh

## dialog.py
    
    
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import *
    
    class StudentDialog(QDialog):
    
        studentCreated = Signal(str)
    
        def __init__(self):
    
            super().__init__()
    
            layout = QVBoxLayout()
    
            self.edit = QLineEdit()
    
            button = QPushButton("OK")
    
            layout.addWidget(self.edit)
    
            layout.addWidget(button)
    
            self.setLayout(layout)
    
            button.clicked.connect(
                self.send_data
            )
    
        def send_data(self):
    
            self.studentCreated.emit(
                self.edit.text()
            )
    
            self.accept()

* * *

## main.py
    
    
    dialog = StudentDialog()
    
    dialog.studentCreated.connect(
        print
    )
    
    dialog.exec()

Kết quả:
    
    
    Nguyễn Văn A

* * *

# 17\. Quản lý nhiều cửa sổ

Ví dụ:
    
    
    Main Window
    
    ↓
    
    Settings
    
    ↓
    
    About
    
    ↓
    
    Student Dialog
    
    ↓
    
    Teacher Dialog

Mỗi cửa sổ nên có:

  * Một file riêng. 
  * Một lớp riêng. 
  * Một Controller riêng (nếu áp dụng MVC). 



* * *

# 18\. Những lỗi người mới thường gặp

## Lỗi 1

Dùng `show()` nhưng lại kiểm tra kết quả.

Sai:
    
    
    dialog.show()

`show()` không trả về `Accepted` hay `Rejected`.

* * *

## Lỗi 2

Quên gọi:
    
    
    accept()

Khi nhấn OK.

Dialog sẽ không đóng.

* * *

## Lỗi 3

Dialog sửa trực tiếp dữ liệu của MainWindow.

Nên phát `Signal` để MainWindow tự xử lý.

* * *

## Lỗi 4

Tạo Dialog trong biến cục bộ rồi để mất tham chiếu:
    
    
    def open_dialog(self):
        dialog = StudentDialog()
        dialog.show()

Sau khi hàm kết thúc, `dialog` có thể bị thu hồi bởi bộ nhớ. Với dialog **modeless** , hãy lưu tham chiếu:
    
    
    self.dialog = StudentDialog()
    self.dialog.show()

* * *

# Bài tập thực hành

## Bài 1

Tạo Dialog:

  * Nhập tên. 
  * OK. 
  * Cancel. 



In kết quả khi người dùng chọn OK.

* * *

## Bài 2

Sử dụng:

  * `QMessageBox.question()`



Hỏi:
    
    
    Bạn có muốn thoát?

Nếu:

Yes

↓

Thoát.

* * *

## Bài 3

Dùng:
    
    
    QFileDialog

Chọn ảnh.

Hiển thị đường dẫn trong `QLabel`.

* * *

## Bài 4

Tạo Dialog.

Nhập:

  * Tên 
  * Tuổi 



Gửi dữ liệu về MainWindow bằng `Signal`.

* * *

# Mini Project cuối buổi: Student Manager - Thêm sinh viên

Tiếp tục dự án **Student Manager**.

Thiết kế:

## MainWindow

  * `QTableWidget`
  * Nút **Thêm**



* * *

## StudentDialog

  * Họ tên 
  * Tuổi 
  * Email 
  * Lớp học 
  * OK 
  * Cancel 



* * *

Yêu cầu:

  1. Nhấn **Thêm**. 
  2. Mở `StudentDialog` bằng `exec()`. 
  3. Khi người dùng bấm **OK** : 
     * Dialog phát `studentCreated`. 
     * MainWindow nhận dữ liệu. 
     * Thêm một dòng vào `QTableWidget`. 
  4. Nếu người dùng bấm **Cancel** , không thêm dữ liệu. 



Đây là mô hình được sử dụng trong rất nhiều phần mềm quản lý doanh nghiệp.

* * *

# Tổng kết Buổi 13

Trong buổi học này, bạn đã học:

  * Phân biệt `QWidget`, `QMainWindow` và `QDialog`. 
  * Hiểu sự khác nhau giữa `exec()` và `show()`. 
  * Sử dụng `accept()` và `reject()`. 
  * Làm việc với các dialog có sẵn: 
    * `QMessageBox`
    * `QFileDialog`
    * `QColorDialog`
    * `QFontDialog`
    * `QInputDialog`
    * `QProgressDialog`
  * Truyền dữ liệu giữa nhiều cửa sổ bằng **Signal/Slot**. 
  * Tổ chức ứng dụng nhiều cửa sổ theo kiến trúc rõ ràng. 



* * *

# Chuẩn bị cho Buổi 14

Ở **Buổi 14** , chúng ta sẽ học một trong những chủ đề quan trọng nhất của PySide6:

# Model/View Architecture

Bạn sẽ học:

  * `QStandardItemModel`. 
  * `QListView`. 
  * `QTreeView`. 
  * `QTableView`. 
  * Sự khác nhau giữa `QTableWidget` và `QTableView`. 
  * `QSortFilterProxyModel`. 
  * Hiển thị và lọc dữ liệu theo kiến trúc Model/View của Qt. 



Đây là nền tảng để xây dựng các ứng dụng quản lý dữ liệu chuyên nghiệp có hiệu năng cao và khả năng mở rộng tốt, đặc biệt khi làm việc với hàng nghìn hoặc hàng triệu bản ghi.

