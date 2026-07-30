# Khóa học PySide6 từ A-Z

# Buổi 10: Kiến trúc ứng dụng PySide6 chuyên nghiệp (MVC, tổ chức Project và tách UI khỏi Logic)

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu vì sao không nên viết tất cả code trong `main.py`. 
>   * Biết cách tổ chức một dự án PySide6 chuyên nghiệp. 
>   * Hiểu mô hình **MVC (Model - View - Controller)**. 
>   * Biết cách tách giao diện, xử lý và dữ liệu. 
>   * Xây dựng ứng dụng theo kiến trúc dễ mở rộng, dễ bảo trì. 
>   * Chuẩn bị nền tảng để phát triển các dự án lớn. 
> 


* * *

# 1\. Vấn đề của người mới học

Rất nhiều người mới viết chương trình như sau:
    
    
    import sys
    from PySide6.QtWidgets import *
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    
    layout = QVBoxLayout()
    
    edit = QLineEdit()
    button = QPushButton("Lưu")
    
    layout.addWidget(edit)
    layout.addWidget(button)
    
    window.setLayout(layout)
    
    
    def save():
        print(edit.text())
    
    
    button.clicked.connect(save)
    
    window.show()
    
    app.exec()

Ban đầu chương trình rất nhỏ nên không có vấn đề.

* * *

Sau vài tháng...
    
    
    main.py
    
    3500 dòng
    
    ↓
    
    5000 dòng
    
    ↓
    
    9000 dòng

Trong file đó có:

  * Giao diện 
  * Database 
  * Xử lý file 
  * API 
  * Xuất Excel 
  * Kiểm tra dữ liệu 
  * Đăng nhập 
  * Quản lý người dùng 
  * In hóa đơn 



Kết quả:

> **Không ai muốn sửa một file dài hàng nghìn dòng.**

* * *

# 2\. Kiến trúc là gì?

Kiến trúc phần mềm giống như bản thiết kế của một ngôi nhà.

Ví dụ xây nhà:
    
    
    Phòng khách
    
    ↓
    
    Phòng ngủ
    
    ↓
    
    Nhà bếp
    
    ↓
    
    Nhà vệ sinh

Không ai xây tất cả vào một phòng.

Phần mềm cũng vậy.

* * *

# 3\. MVC là gì?

MVC là viết tắt của:
    
    
    Model
    
    ↓
    
    View
    
    ↓
    
    Controller

Đây là mô hình phổ biến trong:

  * PySide6 
  * Django 
  * Laravel 
  * ASP.NET 
  * Java Swing 
  * Qt C++ 



* * *

# 4\. Model

Model quản lý:

  * Dữ liệu 
  * Database 
  * File 
  * API 
  * Business Logic 



Ví dụ:
    
    
    class Student:
    
        def __init__(self, name, age):
            self.name = name
            self.age = age

Hoặc:
    
    
    class StudentRepository:
    
        def get_all(self):
            ...

Model **không biết giao diện tồn tại**.

* * *

# 5\. View

View chỉ làm nhiệm vụ:

  * Hiển thị giao diện 
  * Hiển thị dữ liệu 
  * Nhận thao tác người dùng 



Ví dụ:
    
    
    +----------------+
    
    Tên:
    
    [___________]
    
    Tuổi:
    
    [___________]
    
    [ Lưu ]
    
    +----------------+

View **không lưu dữ liệu**.

View **không truy cập database**.

* * *

# 6\. Controller

Controller là "bộ não".

Ví dụ:
    
    
    Button Click
    
    ↓
    
    Controller
    
    ↓
    
    Model
    
    ↓
    
    Controller
    
    ↓
    
    View

Controller:

  * Nhận Signal 
  * Gọi Model 
  * Cập nhật View 



* * *

# 7\. Ví dụ MVC
    
    
    Người dùng
    
    ↓
    
    Nhấn nút
    
    ↓
    
    Controller
    
    ↓
    
    StudentRepository
    
    ↓
    
    Lưu Database
    
    ↓
    
    Controller
    
    ↓
    
    QMessageBox

* * *

# 8\. Cấu trúc Project chuyên nghiệp

Thay vì:
    
    
    project/
    
    main.py

Chúng ta tổ chức:
    
    
    student_manager/
    
    │
    ├── main.py
    │
    ├── models/
    │   ├── student.py
    │   └── repository.py
    │
    ├── views/
    │   ├── main_window.py
    │   └── student_dialog.py
    │
    ├── controllers/
    │   └── student_controller.py
    │
    ├── services/
    │   ├── file_service.py
    │   └── database_service.py
    │
    ├── resources/
    │   ├── icons/
    │   ├── images/
    │   └── styles/
    │
    ├── utils/
    │   ├── validator.py
    │   └── helpers.py
    │
    └── config.py

Đây là cấu trúc được sử dụng trong nhiều dự án PySide6 thực tế.

* * *

# 9\. Vai trò từng thư mục

## models/
    
    
    Student
    
    Teacher
    
    Employee
    
    Invoice

Chỉ chứa dữ liệu và xử lý dữ liệu.

* * *

## views/

Chỉ chứa:

  * Window 
  * Dialog 
  * Widget 



Không chứa logic nghiệp vụ.

* * *

## controllers/

Ví dụ:
    
    
    Save Student
    
    Delete Student
    
    Update Student

Controller điều phối giữa View và Model.

* * *

## services/

Ví dụ:
    
    
    SQLite
    
    MySQL
    
    REST API
    
    Email
    
    PDF
    
    Excel

Tách các chức năng dùng chung.

* * *

## resources/
    
    
    logo.png
    
    save.svg
    
    style.qss

Không để tài nguyên lẫn với mã nguồn.

* * *

## utils/

Các hàm hỗ trợ:

  * Định dạng ngày. 
  * Kiểm tra email. 
  * Sinh mã tự động. 
  * Hàm dùng lại nhiều nơi. 



* * *

# 10\. Ví dụ tách Model

**models/student.py**
    
    
    class Student:
    
        def __init__(self, name, age):
            self.name = name
            self.age = age

* * *

# 11\. View

**views/main_window.py**
    
    
    from PySide6.QtWidgets import *
    
    class MainWindow(QWidget):
    
        def __init__(self):
            super().__init__()
    
            self.name = QLineEdit()
    
            self.save = QPushButton("Lưu")

Chỉ tạo giao diện.

* * *

# 12\. Controller

**controllers/student_controller.py**
    
    
    class StudentController:
    
        def __init__(self, view):
    
            self.view = view
    
            self.view.save.clicked.connect(
                self.save_student
            )
    
        def save_student(self):
    
            name = self.view.name.text()
    
            print(name)

Controller không tạo widget.

Controller chỉ xử lý.

* * *

# 13\. main.py
    
    
    app = QApplication([])
    
    view = MainWindow()
    
    controller = StudentController(view)
    
    view.show()
    
    app.exec()

`main.py` chỉ làm nhiệm vụ khởi động ứng dụng và kết nối các thành phần.

* * *

# 14\. Không nên làm

Sai:
    
    
    class MainWindow(QWidget):
    
        def save():
    
            sqlite3.connect()
    
            requests.get()
    
            export_excel()
    
            send_email()
    
            ...

Một hàm làm quá nhiều việc sẽ rất khó bảo trì.

* * *

# 15\. Nên làm
    
    
    Button
    
    ↓
    
    Controller
    
    ↓
    
    DatabaseService
    
    ↓
    
    ExcelService
    
    ↓
    
    EmailService
    
    ↓
    
    View

Mỗi lớp chỉ đảm nhận một trách nhiệm.

Đây là nguyên tắc **Single Responsibility Principle (SRP)** trong thiết kế phần mềm.

* * *

# 16\. Đặt tên chuyên nghiệp

Không nên:
    
    
    abc.py
    
    test1.py
    
    new.py
    
    code.py

Nên:
    
    
    student_controller.py
    
    student_service.py
    
    student_model.py
    
    main_window.py

Tên file cần phản ánh đúng chức năng.

* * *

# 17\. Tổ chức Resource
    
    
    resources/
    
    icons/
    
    save.svg
    
    delete.svg
    
    edit.svg
    
    images/
    
    logo.png
    
    background.jpg
    
    styles/
    
    dark.qss
    
    light.qss

Đừng để hình ảnh cùng thư mục với file Python.

* * *

# 18\. Quy tắc Import

Không nên:
    
    
    from module import *

Nên:
    
    
    from PySide6.QtWidgets import (
        QWidget,
        QPushButton,
        QLabel,
    )

Hoặc:
    
    
    from models.student import Student

Import rõ ràng giúp mã dễ đọc và tránh xung đột tên.

* * *

# 19\. Ví dụ hoàn chỉnh
    
    
    main.py
    
    ↓
    
    MainWindow
    
    ↓
    
    Controller
    
    ↓
    
    StudentRepository
    
    ↓
    
    SQLite

Khi người dùng nhấn:
    
    
    Lưu

Luồng:
    
    
    Button
    
    ↓
    
    Controller
    
    ↓
    
    Repository
    
    ↓
    
    Database
    
    ↓
    
    Controller
    
    ↓
    
    MessageBox

Đây là mô hình mà chúng ta sẽ áp dụng xuyên suốt các dự án lớn sau này.

* * *

# 20\. Những lỗi người mới thường gặp

## Lỗi 1

Đặt mọi thứ vào `MainWindow`.
    
    
    MainWindow
    
    ↓
    
    Database
    
    ↓
    
    Excel
    
    ↓
    
    PDF
    
    ↓
    
    API
    
    ↓
    
    Email

`MainWindow` trở thành "God Object" (đối tượng làm mọi việc), rất khó mở rộng.

* * *

## Lỗi 2

View sửa dữ liệu trực tiếp.

Ví dụ:
    
    
    students.append(...)

Việc quản lý dữ liệu nên giao cho Model hoặc Repository.

* * *

## Lỗi 3

Controller tự tạo Widget.

Không nên:
    
    
    QPushButton(...)

Controller chỉ điều phối, không xây dựng giao diện.

* * *

## Lỗi 4

Đặt tất cả icon trong thư mục gốc.

Sau vài tháng:
    
    
    logo.png
    
    save.png
    
    icon1.png
    
    abc.png
    
    new2.png

Rất khó quản lý.

* * *

# Bài tập thực hành

## Bài 1

Tạo cấu trúc thư mục:
    
    
    project/
    
    models/
    
    views/
    
    controllers/
    
    resources/
    
    utils/

Giải thích vai trò của từng thư mục.

* * *

## Bài 2

Viết:
    
    
    Student

gồm:

  * name 
  * age 
  * email 



Đặt trong:
    
    
    models/student.py

* * *

## Bài 3

Tạo:
    
    
    views/main_window.py

Chỉ có:

  * `QLineEdit`
  * `QPushButton`



Chưa cần xử lý logic.

* * *

## Bài 4

Tạo:
    
    
    controllers/student_controller.py

Kết nối nút **Lưu** và in tên ra terminal.

* * *

# Mini Project cuối buổi: Student Manager (Kiến trúc MVC)

Xây dựng ứng dụng quản lý sinh viên với cấu trúc:
    
    
    student_manager/
    │
    ├── main.py
    ├── models/
    │   └── student.py
    ├── views/
    │   └── main_window.py
    ├── controllers/
    │   └── student_controller.py
    ├── services/
    │   └── student_repository.py
    └── resources/

Yêu cầu:

  * Giao diện nhập: 
    * Họ tên. 
    * Tuổi. 
    * Email. 
  * Nút **Lưu**. 
  * Khi nhấn: 
    * Controller lấy dữ liệu từ View. 
    * Tạo đối tượng `Student`. 
    * Gọi `StudentRepository.save(student)`. 
    * Hiển thị thông báo thành công. 



> Hiện tại `StudentRepository` có thể chỉ lưu dữ liệu vào một danh sách trong bộ nhớ. Ở các buổi sau, chúng ta sẽ thay bằng SQLite.

* * *

# Tổng kết Buổi 10

Trong buổi học này, bạn đã chuyển từ tư duy "viết được chương trình" sang tư duy "thiết kế phần mềm".

Bạn đã học:

  * Vì sao cần kiến trúc ứng dụng. 
  * Mô hình **MVC**. 
  * Cách tổ chức dự án nhiều thư mục. 
  * Tách **Model** , **View** , **Controller**. 
  * Vai trò của **Services** , **Resources** và **Utils**. 
  * Những nguyên tắc giúp mã nguồn dễ mở rộng và bảo trì. 



Đây là nền tảng để xây dựng các ứng dụng PySide6 có quy mô từ vài nghìn đến hàng chục nghìn dòng mã.

* * *

# Chuẩn bị cho Buổi 11

Ở **Buổi 11** , chúng ta sẽ bắt đầu làm việc với **Qt Designer** , công cụ thiết kế giao diện kéo-thả của Qt.

Bạn sẽ học:

  * Cài đặt và sử dụng Qt Designer. 
  * Thiết kế giao diện bằng kéo-thả. 
  * Các Layout trong Qt Designer. 
  * Lưu file `.ui`. 
  * Chuyển `.ui` sang Python bằng `pyside6-uic`. 
  * Nạp trực tiếp file `.ui` bằng `QUiLoader`. 
  * So sánh hai cách sử dụng `.ui` và lựa chọn phù hợp cho từng loại dự án. 



Đây là bước chuyển từ việc viết giao diện hoàn toàn bằng mã sang quy trình phát triển GUI chuyên nghiệp, giúp tăng tốc độ thiết kế và bảo trì ứng dụng.

