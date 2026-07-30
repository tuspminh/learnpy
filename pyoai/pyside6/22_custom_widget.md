# Khóa học PySide6 từ A-Z

# Buổi 22: Custom Widget và Composite Widget - Xây dựng thư viện Widget của riêng bạn

> **Đây là buổi học đánh dấu bước chuyển từ "người sử dụng PySide6" sang "người phát triển bằng PySide6".**

Cho đến bây giờ, chúng ta luôn sử dụng các widget mà Qt cung cấp như:

  * QPushButton 
  * QLabel 
  * QLineEdit 
  * QTableView 
  * QTreeView 



Nhưng trong các dự án thực tế, lập trình viên hiếm khi đặt trực tiếp các widget này khắp nơi trong ứng dụng. Thay vào đó, họ tạo **Custom Widget** và **Composite Widget** để tái sử dụng.

Sau buổi học này bạn sẽ:

  * Hiểu Custom Widget là gì. 
  * Hiểu Composite Widget là gì. 
  * Biết khi nào nên kế thừa widget. 
  * Biết khi nào nên ghép nhiều widget thành một widget mới. 
  * Tạo widget có Signal/Slot riêng. 
  * Thiết kế thư viện widget dùng lại cho nhiều dự án. 



* * *

# 1\. Tại sao phải tạo Custom Widget?

Giả sử trong dự án có 30 màn hình.

Mỗi màn hình đều có:
    
    
    Tên sinh viên
    
    [________________]
    
    (Tìm kiếm)

Nếu mỗi lần đều viết:
    
    
    QLabel()
    
    QLineEdit()
    
    QPushButton()

thì sẽ lặp lại rất nhiều mã.

Giải pháp:
    
    
    SearchWidget

Một widget duy nhất.

* * *

# 2\. Hai cách tạo Widget

## Cách 1

Kế thừa widget có sẵn.

Ví dụ:
    
    
    class SearchLineEdit(QLineEdit):

* * *

## Cách 2

Ghép nhiều widget.

Ví dụ:
    
    
    QLabel
    
    +
    
    QLineEdit
    
    +
    
    QPushButton

↓
    
    
    SearchWidget

Đây gọi là **Composite Widget**.

* * *

# 3\. Cấu trúc thư mục
    
    
    widgets/
    
        search_widget.py
    
        toolbar_widget.py
    
        status_widget.py
    
        student_card.py
    
        avatar_widget.py
    
        loading_widget.py

Sau này:
    
    
    from widgets.search_widget import SearchWidget

Dùng ở mọi dự án.

* * *

# 4\. Custom QPushButton

Ví dụ:
    
    
    class PrimaryButton(QPushButton):

Trong constructor:
    
    
    self.setMinimumHeight(40)
    
    self.setCursor(Qt.PointingHandCursor)

Áp dụng QSS:
    
    
    self.setStyleSheet(...)

Từ nay:
    
    
    PrimaryButton("Lưu")

thay vì cấu hình lặp đi lặp lại.

* * *

# 5\. SearchWidget

Thành phần:
    
    
    +------------------------------------+
    
    [Tìm kiếm........]
    
    (Search)
    
    +------------------------------------+

Bao gồm:

  * QLabel (tùy chọn) 
  * QLineEdit 
  * QPushButton 



* * *

# 6\. Layout
    
    
    QHBoxLayout
    
    ↓
    
    LineEdit
    
    ↓
    
    Button

* * *

# 7\. Signal riêng

Widget có thể phát Signal.
    
    
    from PySide6.QtCore import Signal
    
    class SearchWidget(QWidget):
    
        searched = Signal(str)

* * *

# 8\. Phát Signal

Khi nhấn nút:
    
    
    text = self.line_edit.text()
    
    self.searched.emit(text)

MainWindow:
    
    
    search.searched.connect(
        self.search_student
    )

MainWindow không cần biết SearchWidget được xây dựng như thế nào.

* * *

# 9\. StudentCard

Ví dụ:
    
    
    +----------------------+
    
    👤
    
    Nguyễn Văn An
    
    CNTT
    
    8.5
    
    +----------------------+

Đây là một Composite Widget.

* * *

Thành phần:
    
    
    Avatar
    
    ↓
    
    Name
    
    ↓
    
    Class
    
    ↓
    
    Score

* * *

# 10\. Constructor

Ví dụ:
    
    
    StudentCard(
    
        student
    
    )

Tự hiển thị:

  * Avatar 
  * Họ tên 
  * Lớp 
  * Điểm 



* * *

# 11\. StatusWidget

Ví dụ:
    
    
    Đã tải:
    
    120 sinh viên

Hoặc:
    
    
    Đang kết nối...

Có thể dùng ở nhiều màn hình.

* * *

# 12\. ToolbarWidget

Ví dụ:
    
    
    +--------------------------------+
    
    ➕
    
    ✏
    
    🗑
    
    💾
    
    +--------------------------------+

Đóng gói toàn bộ Toolbar.

MainWindow:
    
    
    toolbar = ToolbarWidget()

Không cần tạo từng nút.

* * *

# 13\. LoadingWidget

Ví dụ:
    
    
    Loading...
    
    ██████
    

Hoặc:
    
    
    ⭮

Hiển thị khi:

  * Download. 
  * OCR. 
  * AI. 
  * Tải Database. 



* * *

# 14\. AvatarWidget

Ví dụ:
    
    
    ○
    
    Ảnh đại diện
    
    ○

Có thể:

  * Chọn ảnh. 
  * Crop. 
  * Zoom. 
  * Hiển thị mặc định. 



* * *

# 15\. EmptyWidget

Ví dụ:
    
    
    Không có dữ liệu
    
    📂

Hiển thị khi:
    
    
    Table
    
    ↓
    
    0 dòng

Đây là trải nghiệm người dùng tốt hơn nhiều so với việc hiển thị một bảng trống.

* * *

# 16\. Widget có Property

Ví dụ:
    
    
    card.setName("An")
    
    card.setScore(9.5)

Bên trong:

↓

Tự cập nhật Label.

* * *

# 17\. Widget có Method

Ví dụ:
    
    
    loading.start()

↓

Animation chạy.
    
    
    loading.stop()

↓

Ẩn.

* * *

# 18\. Widget phát nhiều Signal

Ví dụ:
    
    
    clicked = Signal()
    
    deleted = Signal()
    
    edited = Signal()

MainWindow chỉ cần kết nối đến các Signal tương ứng.

* * *

# 19\. Widget có Theme

Ví dụ:
    
    
    Light
    
    ↓
    
    Dark

Không viết:
    
    
    setStyleSheet(...)

trong Widget.

Nên để Widget sử dụng các selector trong file QSS chung của ứng dụng.

* * *

# 20\. Không nên làm

Sai:
    
    
    QLabel()
    
    QLabel()
    
    QLabel()
    
    QLabel()

Lặp ở:

20 cửa sổ.

* * *

Đúng:
    
    
    StudentCard()

* * *

# 21\. Những lỗi người mới thường gặp

## Lỗi 1

MainWindow quá lớn.

Ví dụ:
    
    
    5000 dòng

↓

Khó bảo trì.

Nên chia thành nhiều Custom Widget.

* * *

## Lỗi 2

Widget truy cập trực tiếp Database.

Sai.

Widget chỉ hiển thị.

Không chứa SQL.

* * *

## Lỗi 3

Widget tự gọi MainWindow.

Sai.

Nên dùng Signal.

* * *

## Lỗi 4

Viết QSS bên trong từng Widget.

Khó đổi Theme.

* * *

## Lỗi 5

Một Widget làm quá nhiều việc.

Ví dụ:
    
    
    StudentWidget
    
    ↓
    
    Search
    
    ↓
    
    Edit
    
    ↓
    
    Delete
    
    ↓
    
    Export
    
    ↓
    
    Import

Nên chia nhỏ theo nguyên tắc **Single Responsibility**.

* * *

# 22\. Kiến trúc chuyên nghiệp
    
    
    MainWindow
    
    ↓
    
    SearchWidget
    
    ↓
    
    StudentTable
    
    ↓
    
    StatusWidget
    
    ↓
    
    ToolbarWidget
    
    ↓
    
    StudentCard

MainWindow chỉ ghép các thành phần.

* * *

# 23\. Thư viện Widget

Sau vài dự án bạn sẽ có:
    
    
    widgets/
    
    buttons/
    
    inputs/
    
    cards/
    
    dialogs/
    
    toolbars/
    
    status/
    
    loading/
    
    charts/
    
    calendar/
    
    viewer/

Mỗi dự án chỉ việc import.

* * *

# 24\. Ví dụ thực tế

Trong **Student Manager** :
    
    
    MainWindow
    
    ↓
    
    ToolbarWidget
    
    ↓
    
    SearchWidget
    
    ↓
    
    StudentTableWidget
    
    ↓
    
    StatusWidget

Mỗi thành phần là một file riêng.

Nếu sau này xây dựng **Employee Manager** hoặc **Library Manager** , bạn có thể tái sử dụng hầu hết các widget này.

* * *

# 25\. Composite Widget vs Custom Widget

Custom Widget| Composite Widget  
---|---  
Kế thừa từ một widget có sẵn| Ghép nhiều widget  
Ví dụ: `PrimaryButton`, `SearchLineEdit`| Ví dụ: `SearchWidget`, `StudentCard`  
Thường thay đổi hành vi hoặc giao diện của một widget| Thường tạo thành một thành phần giao diện hoàn chỉnh  
  
Trong thực tế, hai cách này thường được kết hợp với nhau.

* * *

# Bài tập thực hành

## Bài 1

Viết:
    
    
    PrimaryButton

Yêu cầu:

  * Cao 40 px. 
  * Có icon. 
  * Có hiệu ứng hover thông qua QSS. 



* * *

## Bài 2

Viết:
    
    
    SearchWidget

Gồm:

  * `QLineEdit`. 
  * `QPushButton`. 
  * Signal: 


    
    
    searched(str)

* * *

## Bài 3

Viết:
    
    
    StudentCard

Hiển thị:

  * Avatar. 
  * Họ tên. 
  * Lớp. 
  * Điểm trung bình. 



* * *

## Bài 4

Viết:
    
    
    LoadingWidget

Có các phương thức:

  * `start()`
  * `stop()`



* * *

# Mini Project cuối buổi: Student Manager Widget Library

Tách giao diện của dự án **Student Manager** thành các widget độc lập:
    
    
    student_manager/
    
    widgets/
    
        search_widget.py
    
        toolbar_widget.py
    
        status_widget.py
    
        student_card.py
    
        loading_widget.py
    
        primary_button.py

Sau đó, `MainWindow` chỉ còn nhiệm vụ:

  * Khởi tạo các widget. 
  * Sắp xếp layout. 
  * Kết nối Signal/Slot. 



Toàn bộ logic hiển thị của từng thành phần nằm trong chính widget đó.

* * *

# Tổng kết Buổi 22

Bạn đã học:

  * Khái niệm **Custom Widget** và **Composite Widget**. 
  * Khi nào nên kế thừa widget và khi nào nên ghép nhiều widget. 
  * Tạo widget có Signal/Slot riêng. 
  * Thiết kế widget có khả năng tái sử dụng. 
  * Xây dựng thư viện widget cho nhiều dự án. 
  * Giảm đáng kể mã lặp và làm cho `MainWindow` gọn gàng hơn. 



Đây là bước tiến rất quan trọng để xây dựng các ứng dụng PySide6 có kiến trúc rõ ràng, dễ mở rộng và bảo trì.

* * *

# Chuẩn bị cho Buổi 23

Ở **Buổi 23** , chúng ta sẽ học về **Animation và Graphics trong PySide6**.

Bạn sẽ được tìm hiểu:

  * `QPropertyAnimation`. 
  * `QSequentialAnimationGroup`. 
  * `QParallelAnimationGroup`. 
  * `QGraphicsOpacityEffect`. 
  * `QGraphicsDropShadowEffect`. 
  * `QGraphicsBlurEffect`. 
  * `QGraphicsView` và `QGraphicsScene`. 
  * Hiệu ứng chuyển trang, fade, slide, zoom. 
  * Thiết kế giao diện hiện đại với các hiệu ứng mượt mà. 



Sau buổi này, bạn sẽ có thể tạo ra những ứng dụng PySide6 có trải nghiệm người dùng chuyên nghiệp, với các hiệu ứng chuyển động và đồ họa tương tự nhiều phần mềm desktop hiện đại.

