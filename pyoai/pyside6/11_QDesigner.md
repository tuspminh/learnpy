# Khóa học PySide6 từ A-Z

# Buổi 11: Qt Designer - Thiết kế giao diện chuyên nghiệp bằng kéo thả

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Qt Designer là gì. 
>   * Biết cài đặt và khởi động Qt Designer. 
>   * Thành thạo thiết kế giao diện bằng kéo-thả. 
>   * Biết sử dụng Layout đúng cách. 
>   * Hiểu file `.ui` là gì. 
>   * Biết 2 cách sử dụng file `.ui` trong PySide6. 
>   * Hoàn thành giao diện đầu tiên bằng Qt Designer. 
> 


* * *

# 1\. Vì sao cần Qt Designer?

Cho đến nay, chúng ta đều viết giao diện bằng mã Python:
    
    
    layout = QVBoxLayout()
    
    layout.addWidget(QLabel("Tên"))
    
    layout.addWidget(QLineEdit())
    
    layout.addWidget(QPushButton("Lưu"))

Điều này rất tốt để học.

Nhưng khi giao diện lớn:
    
    
    MainWindow
    
    ↓
    
    Menu
    
    ↓
    
    Toolbar
    
    ↓
    
    StatusBar
    
    ↓
    
    20 Button
    
    ↓
    
    15 Label
    
    ↓
    
    10 LineEdit
    
    ↓
    
    Table
    
    ↓
    
    Tree
    
    ↓
    
    Tab

Nếu viết toàn bộ bằng code sẽ rất mất thời gian.

Qt Designer ra đời để giải quyết vấn đề này.

* * *

# 2\. Qt Designer là gì?

Qt Designer là công cụ **thiết kế giao diện kéo-thả (Drag & Drop)** của Qt.

Bạn có thể:

  * Kéo Button 
  * Kéo Label 
  * Kéo Table 
  * Kéo Menu 
  * Kéo Toolbar 
  * Kéo Tab 
  * Kéo Tree 
  * Kéo Splitter 



Giống như:

  * Visual Studio (Windows Forms) 
  * Delphi 
  * Android Studio (Layout Editor) 



* * *

# 3\. Cài đặt Qt Designer

Nếu đã cài PySide6 đầy đủ, bạn có thể kiểm tra:
    
    
    pyside6-designer

Hoặc:
    
    
    designer

Nếu không có, hãy cài:
    
    
    pip install pyside6

Trong một số hệ điều hành, Qt Designer được cài riêng cùng bộ công cụ Qt.

> **Lưu ý:** Tùy hệ điều hành và cách cài đặt, đường dẫn thực thi của `pyside6-designer` có thể khác nhau.

* * *

# 4\. Giao diện Qt Designer

Khi mở Designer, bạn sẽ thấy:
    
    
    +-----------------------------------------------------------+
    
     Widget Box        Form Editor         Object Inspector
    
     Property Editor
    
     Resource Browser
    
     Signal/Slot Editor
    
    +-----------------------------------------------------------+

Các khu vực quan trọng:

Thành phần| Chức năng  
---|---  
Widget Box| Danh sách widget  
Form Editor| Thiết kế giao diện  
Object Inspector| Cây widget  
Property Editor| Chỉnh thuộc tính  
Action Editor| Quản lý Action  
Resource Browser| Tài nguyên  
  
* * *

# 5\. Tạo Form mới

Chọn:
    
    
    Main Window

hoặc
    
    
    Widget

Hoặc:
    
    
    Dialog

### Khi nào dùng?

Loại| Dùng khi  
---|---  
Widget| Cửa sổ đơn giản  
Main Window| Phần mềm có Menu, Toolbar, StatusBar  
Dialog| Hộp thoại nhập dữ liệu  
  
Trong khóa học này, chúng ta sẽ chủ yếu dùng **Main Window**.

* * *

# 6\. Widget Box

Đây là nơi chứa tất cả widget.

Ví dụ:
    
    
    Buttons
    
    ↓
    
    PushButton
    
    ↓
    
    RadioButton
    
    ↓
    
    CheckBox

Hoặc:
    
    
    Input Widgets
    
    ↓
    
    LineEdit
    
    ↓
    
    SpinBox
    
    ↓
    
    ComboBox

Bạn chỉ cần kéo widget vào Form.

* * *

# 7\. Property Editor

Mỗi widget đều có thuộc tính.

Ví dụ:
    
    
    QPushButton
    
    ↓
    
    text
    
    ↓
    
    Lưu

hoặc:
    
    
    objectName
    
    ↓
    
    btnSave

Các thuộc tính quan trọng:

  * `objectName`
  * `text`
  * `enabled`
  * `font`
  * `styleSheet`
  * `geometry`
  * `toolTip`



* * *

# 8\. objectName

Đây là thuộc tính **rất quan trọng**.

Ví dụ:
    
    
    btnSave

Không nên:
    
    
    pushButton

Hãy đặt tên có ý nghĩa:
    
    
    btnSave
    
    btnDelete
    
    txtName
    
    txtEmail
    
    lblResult
    
    tblStudent

* * *

# 9\. Layout

Đây là phần quan trọng nhất của Designer.

Rất nhiều người mới mắc lỗi:
    
    
    Kéo widget
    
    ↓
    
    Đặt bằng chuột
    
    ↓
    
    Xong

Sai!

Qt luôn khuyến khích dùng Layout.

* * *

# 10\. Các Layout

### Vertical Layout
    
    
    Label
    
    ↓
    
    LineEdit
    
    ↓
    
    Button

* * *

### Horizontal Layout
    
    
    Label   LineEdit

* * *

### Grid Layout
    
    
    Tên     [_____]
    
    Tuổi    [_____]
    
    Email   [_____]

* * *

### Form Layout
    
    
    Tên:      [________]
    
    Tuổi:     [________]
    
    Email:    [________]

Đây là Layout được dùng nhiều nhất cho biểu mẫu nhập liệu.

* * *

# 11\. Ví dụ thiết kế Form

Tạo giao diện:
    
    
    Tên
    
    [____________]
    
    Tuổi
    
    [____________]
    
    Email
    
    [____________]
    
    [Lưu]

Các bước:

  * Kéo 3 `QLabel`
  * Kéo 3 `QLineEdit`
  * Kéo 1 `QPushButton`
  * Chọn tất cả 
  * Chuột phải → **Lay Out → Form Layout**



Ngay lập tức giao diện sẽ tự căn chỉnh.

* * *

# 12\. Lưu file `.ui`

Ví dụ:
    
    
    mainwindow.ui

Đây thực chất là một file XML.

Ví dụ rút gọn:
    
    
    <widget class="QMainWindow">
        <property name="windowTitle">
            <string>Student Manager</string>
        </property>
    </widget>

Bạn không cần chỉnh sửa XML bằng tay.

* * *

# 13\. Hai cách sử dụng file `.ui`

Có **2 cách phổ biến**.

* * *

## Cách 1: Chuyển `.ui` thành Python

Lệnh:
    
    
    pyside6-uic mainwindow.ui -o ui_mainwindow.py

Kết quả:
    
    
    mainwindow.ui
    
    ↓
    
    ui_mainwindow.py

Ưu điểm:

  * Nhanh. 
  * Không cần nạp file khi chạy. 



Nhược điểm:

  * Mỗi lần sửa `.ui` phải chạy lại `pyside6-uic`. 



* * *

## Cách 2: Nạp trực tiếp bằng `QUiLoader`

Ví dụ:
    
    
    from PySide6.QtUiTools import QUiLoader
    
    loader = QUiLoader()
    
    window = loader.load("mainwindow.ui")

Ưu điểm:

  * Không cần sinh lại file Python. 
  * Designer thay đổi là chương trình dùng ngay. 



Nhược điểm:

  * Chậm hơn một chút. 
  * Khó kiểm tra lỗi khi thiếu widget. 



* * *

# 14\. Cách được khuyến nghị

Trong dự án nhỏ:
    
    
    .ui
    
    ↓
    
    QUiLoader

Trong dự án lớn:
    
    
    .ui
    
    ↓
    
    pyside6-uic
    
    ↓
    
    ui_xxx.py

Sau đó tạo lớp kế thừa:
    
    
    class MainWindow(QMainWindow, Ui_MainWindow):
        ...

Đây là cách mà phần lớn dự án PySide6 chuyên nghiệp sử dụng.

* * *

# 15\. Ví dụ sử dụng file đã sinh

Giả sử bạn đã tạo:
    
    
    ui_mainwindow.py

Trong đó có lớp:
    
    
    Ui_MainWindow

Sử dụng:
    
    
    import sys
    
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    from ui_mainwindow import Ui_MainWindow
    
    
    class MainWindow(QMainWindow):
    
        def __init__(self):
            super().__init__()
    
            self.ui = Ui_MainWindow()
    
            self.ui.setupUi(self)
    
            self.ui.btnSave.clicked.connect(self.save)
    
        def save(self):
            print(
                self.ui.txtName.text()
            )
    
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    
    window.show()
    
    app.exec()

> **Quy ước:** Không sửa trực tiếp `ui_mainwindow.py` vì file này sẽ bị ghi đè mỗi lần chạy `pyside6-uic`.

* * *

# 16\. Quy tắc đặt tên Widget

Widget| Ví dụ  
---|---  
QPushButton| `btnSave`  
QLabel| `lblStatus`  
QLineEdit| `txtName`  
QTextEdit| `txtDescription`  
QComboBox| `cboDepartment`  
QTableWidget| `tblStudent`  
QListWidget| `lstFiles`  
QTreeWidget| `treeFolder`  
QCheckBox| `chkRemember`  
QRadioButton| `radMale`  
  
Đặt tên nhất quán sẽ giúp mã nguồn dễ đọc hơn.

* * *

# 17\. Những lỗi người mới thường gặp

## Lỗi 1

Không dùng Layout.

Khi phóng to cửa sổ:
    
    
    Button
    
    ↓
    
    Không di chuyển

Giao diện bị vỡ.

* * *

## Lỗi 2

Đặt:
    
    
    pushButton

làm `objectName`.

Sau này sẽ có:
    
    
    pushButton
    
    pushButton_2
    
    pushButton_3

Rất khó quản lý.

* * *

## Lỗi 3

Sửa trực tiếp:
    
    
    ui_mainwindow.py

Sau khi chạy:
    
    
    pyside6-uic

Mọi thay đổi sẽ mất.

* * *

## Lỗi 4

Quên chạy lại:
    
    
    pyside6-uic

Sau khi sửa `.ui`.

Kết quả là chương trình vẫn dùng giao diện cũ.

* * *

# Bài tập thực hành

## Bài 1

Thiết kế bằng Qt Designer:

  * `QLineEdit` nhập tên. 
  * `QLineEdit` nhập email. 
  * `QPushButton` Lưu. 



Sử dụng `Form Layout`.

* * *

## Bài 2

Lưu thành:
    
    
    student.ui

Sinh:
    
    
    ui_student.py

* * *

## Bài 3

Viết `main.py`:

  * Hiển thị giao diện. 
  * Khi nhấn **Lưu** , in tên và email ra terminal. 



* * *

## Bài 4

Thiết kế cửa sổ có:

  * `MenuBar`
  * `ToolBar`
  * `StatusBar`



Đặt các `QAction`:

  * Mở 
  * Lưu 
  * Thoát 



Chưa cần viết xử lý.

* * *

# Mini Project cuối buổi: Student Manager UI

Thiết kế giao diện quản lý sinh viên bằng **Qt Designer** với các thành phần:

  * `QLineEdit`: Họ tên. 
  * `QSpinBox`: Tuổi. 
  * `QLineEdit`: Email. 
  * `QComboBox`: Lớp học. 
  * `QPushButton`: Thêm, Sửa, Xóa, Làm mới. 
  * `QTableWidget`: Danh sách sinh viên. 
  * `QStatusBar`: Hiển thị trạng thái. 



Yêu cầu:

  * Sử dụng `Main Window`. 
  * Dùng `Form Layout` cho phần nhập liệu. 
  * Dùng `Horizontal Layout` cho các nút. 
  * Đặt `objectName` theo đúng quy ước. 
  * Lưu thành `student_manager.ui` và sinh `ui_student_manager.py`. 



> Đây sẽ là giao diện nền để chúng ta phát triển ứng dụng quản lý sinh viên trong các buổi tiếp theo.

* * *

# Tổng kết Buổi 11

Trong buổi học này, bạn đã làm quen với quy trình thiết kế giao diện chuyên nghiệp:

  * Hiểu vai trò của **Qt Designer**. 
  * Biết sử dụng các Layout để tạo giao diện co giãn đúng cách. 
  * Thiết kế và lưu file `.ui`. 
  * Sử dụng `pyside6-uic` để sinh mã Python. 
  * Hiểu cách kết hợp `Ui_MainWindow` với lớp `MainWindow` của riêng bạn. 
  * Biết quy tắc đặt tên widget và tổ chức dự án. 



Đây là quy trình mà phần lớn lập trình viên PySide6 sử dụng trong các dự án thực tế.

* * *

# Chuẩn bị cho Buổi 12

Ở **Buổi 12** , chúng ta sẽ học về **Qt Style Sheets (QSS)** – hệ thống tạo giao diện đẹp cho ứng dụng Qt.

Bạn sẽ học:

  * Cú pháp QSS. 
  * Styling cho `QPushButton`, `QLineEdit`, `QTableWidget`,... 
  * Pseudo-state (`:hover`, `:pressed`, `:disabled`,...). 
  * Theme sáng và tối. 
  * Tổ chức file `.qss`. 
  * Xây dựng giao diện hiện đại giống các ứng dụng chuyên nghiệp. 



Sau buổi này, bạn sẽ có thể biến các giao diện mặc định của PySide6 thành những ứng dụng có giao diện đẹp mắt và nhất quán.

