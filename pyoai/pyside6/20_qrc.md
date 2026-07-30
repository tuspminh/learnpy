# Khóa học PySide6 từ A-Z

# Buổi 20: Qt Resource System (QRC), QSS và Theme - Thiết kế giao diện chuyên nghiệp

> **Đây là một trong những buổi học quan trọng nhất nếu bạn muốn ứng dụng PySide6 có giao diện đẹp và dễ triển khai.**

Rất nhiều ứng dụng nổi tiếng như:

  * Qt Creator 
  * Anki 
  * Wireshark (Qt phiên bản mới) 
  * MuseScore 
  * KeePassXC 
  * Calibre 



đều sử dụng **Qt Resource System (QRC)** kết hợp với **Qt Style Sheet (QSS)**.

Sau buổi học này, bạn sẽ:

  * Hiểu Qt Resource System (QRC). 
  * Đóng gói icon, ảnh, font vào ứng dụng. 
  * Thành thạo Qt Style Sheet (QSS). 
  * Thiết kế Light Theme và Dark Theme. 
  * Tạo giao diện hiện đại. 
  * Chuẩn bị cho việc đóng gói bằng PyInstaller. 



* * *

# 1\. Vì sao cần Resource System?

Giả sử bạn có:
    
    
    project/
    
    main.py
    
    icons/
    
    add.png
    
    delete.png
    
    logo.png

Trong code:
    
    
    QIcon("icons/add.png")

Lúc phát triển:

↓

Hoạt động.

Sau khi đóng gói `.exe`:

↓

Có thể lỗi:
    
    
    Không tìm thấy file

Qt giải quyết bằng Resource System.

* * *

# 2\. Qt Resource System (QRC)

Thay vì:
    
    
    icons/add.png

Ta dùng:
    
    
    :/icons/add.png

Hoặc:
    
    
    :/images/logo.png

Đường dẫn này được nhúng vào ứng dụng.

* * *

# 3\. Cấu trúc thư mục
    
    
    student_manager/
    
    resources/
    
        icons/
    
            add.png
    
            edit.png
    
            delete.png
    
        images/
    
            logo.png
    
        fonts/
    
            Roboto-Regular.ttf
    
        qss/
    
            dark.qss
    
            light.qss
    
    resources.qrc

Đây là cách tổ chức chuẩn trong các dự án Qt.

* * *

# 4\. File resources.qrc

Ví dụ:
    
    
    <RCC>
    
        <qresource prefix="/">
    
            <file>resources/icons/add.png</file>
    
            <file>resources/icons/delete.png</file>
    
            <file>resources/images/logo.png</file>
    
        </qresource>
    
    </RCC>

Sau khi biên dịch, các tài nguyên sẽ được truy cập bằng tiền tố `:/`.

* * *

# 5\. Biên dịch QRC

PySide6 cung cấp công cụ:
    
    
    pyside6-rcc

Ví dụ:
    
    
    pyside6-rcc resources.qrc -o resources_rc.py

Sau đó:
    
    
    import resources_rc

Chỉ cần import một lần khi khởi động ứng dụng.

* * *

# 6\. Dùng Icon
    
    
    button.setIcon(
        QIcon(":/resources/icons/add.png")
    )

Không phụ thuộc thư mục hiện tại.

* * *

# 7\. Hiển thị ảnh
    
    
    pixmap = QPixmap(
        ":/resources/images/logo.png"
    )
    
    label.setPixmap(pixmap)

* * *

# 8\. Font

Qt cho phép nhúng font.
    
    
    from PySide6.QtGui import QFontDatabase
    
    font_id = QFontDatabase.addApplicationFont(
        ":/resources/fonts/Roboto-Regular.ttf"
    )

Lấy tên font:
    
    
    families = QFontDatabase.applicationFontFamilies(font_id)
    
    print(families)

Áp dụng:
    
    
    app.setFont(
        QFont(families[0], 10)
    )

* * *

# 9\. Qt Style Sheet (QSS)

QSS rất giống CSS.

Ví dụ:
    
    
    QPushButton {
    
        background: #1976D2;
    
        color: white;
    }

* * *

# 10\. Đặt Style
    
    
    button.setStyleSheet("""
    
    QPushButton{
    
        background:#1976D2;
    
        color:white;
    
    }
    
    """)

Nhưng không nên viết trực tiếp trong code đối với dự án lớn.

* * *

# 11\. File QSS

Tạo:
    
    
    dark.qss

Ví dụ:
    
    
    QMainWindow{
    
        background:#2D2D30;
    
    }

Đọc:
    
    
    with open("dark.qss") as f:
    
        app.setStyleSheet(f.read())

Hoặc nếu đã nhúng vào QRC, có thể đọc từ `QFile(":/resources/qss/dark.qss")`.

* * *

# 12\. Selector

Áp dụng cho tất cả:
    
    
    QPushButton{
    
    }

Theo objectName:
    
    
    QPushButton#saveButton{
    
    }

Theo trạng thái:
    
    
    QPushButton:hover{
    
    }

Nhấn:
    
    
    QPushButton:pressed{
    
    }

Vô hiệu:
    
    
    QPushButton:disabled{
    
    }

* * *

# 13\. Ví dụ Button
    
    
    QPushButton{
    
        background:#2196F3;
    
        color:white;
    
        border-radius:6px;
    
        padding:8px;
    
    }

Hover:
    
    
    QPushButton:hover{
    
        background:#42A5F5;
    
    }

Pressed:
    
    
    QPushButton:pressed{
    
        background:#1565C0;
    
    }

* * *

# 14\. QLineEdit
    
    
    QLineEdit{
    
        border:1px solid gray;
    
        border-radius:5px;
    
        padding:6px;
    
    }

Focus:
    
    
    QLineEdit:focus{
    
        border:2px solid #2196F3;
    
    }

* * *

# 15\. QLabel
    
    
    QLabel{
    
        color:white;
    
        font-size:14px;
    
    }

* * *

# 16\. QTableView
    
    
    QTableView{
    
        gridline-color:#555;
    
        selection-background-color:#007ACC;
    
        alternate-background-color:#333;
    
    }

Để dùng nền xen kẽ:
    
    
    table.setAlternatingRowColors(True)

* * *

# 17\. Header
    
    
    QHeaderView::section{
    
        background:#444;
    
        color:white;
    
        padding:5px;
    
    }

* * *

# 18\. QMenu
    
    
    QMenu{
    
        background:#2D2D30;
    
    }

Item:
    
    
    QMenu::item:selected{
    
        background:#007ACC;
    
    }

* * *

# 19\. QScrollBar
    
    
    QScrollBar:vertical{
    
        width:12px;
    
    }

Handle:
    
    
    QScrollBar::handle:vertical{
    
        background:#666;
    
    }

* * *

# 20\. Light Theme
    
    
    Nền
    
    ↓
    
    Trắng
    
    Text
    
    ↓
    
    Đen

Ví dụ:
    
    
    QWidget{
    
        background:white;
    
        color:black;
    
    }

* * *

# 21\. Dark Theme

Ví dụ giống VS Code:
    
    
    QWidget{
    
        background:#1E1E1E;
    
        color:#DDDDDD;
    
    }

Đây là màu sắc được nhiều ứng dụng hiện đại sử dụng.

* * *

# 22\. Chuyển Theme

Ví dụ:
    
    
    def load_theme(path):
    
        with open(path) as f:
    
            app.setStyleSheet(f.read())

Button:
    
    
    Dark
    
    ↓
    
    Light

Ứng dụng đổi giao diện ngay lập tức.

* * *

# 23\. Tổ chức Theme
    
    
    resources/
    
    qss/
    
        dark.qss
    
        light.qss
    
        blue.qss
    
        green.qss

Rất dễ mở rộng.

* * *

# 24\. Không nên làm

Sai:
    
    
    button.setStyleSheet(...)

Cho từng Button.

Sau vài tháng:

↓

Khó bảo trì.

Nên:
    
    
    Toàn bộ Style
    
    ↓
    
    Một file QSS

* * *

# 25\. Những lỗi người mới thường gặp

## Lỗi 1

Đường dẫn:
    
    
    QIcon("icon.png")

↓

Lỗi khi đóng gói.

Nên:
    
    
    QIcon(":/resources/icons/icon.png")

* * *

## Lỗi 2

Viết:
    
    
    setStyleSheet(...)

500 lần.

Khó sửa.

* * *

## Lỗi 3

Đổi màu từng Widget.

Không có Theme thống nhất.

* * *

## Lỗi 4

Không dùng:
    
    
    :hover

↓

Giao diện kém sinh động.

* * *

## Lỗi 5

Nhúng font nhưng quên gọi:
    
    
    QFontDatabase.addApplicationFont(...)

↓

Font không được sử dụng.

* * *

# 26\. Mẫu kiến trúc chuyên nghiệp
    
    
    resources/
    
    ├── icons/
    
    ├── images/
    
    ├── fonts/
    
    ├── qss/
    
    │     dark.qss
    
    │     light.qss
    
    │     blue.qss
    
    │
    
    └── resources.qrc

Mọi tài nguyên đều được quản lý tập trung.

* * *

# Bài tập thực hành

## Bài 1

Tạo:
    
    
    resources.qrc

Nhúng:

  * 3 icon. 
  * 1 logo. 



Hiển thị trên giao diện.

* * *

## Bài 2

Viết:
    
    
    dark.qss

Cho:

  * MainWindow. 
  * Button. 
  * LineEdit. 
  * TableView. 



* * *

## Bài 3

Thêm:
    
    
    Light Theme
    
    ↓
    
    Dark Theme

Bằng Menu hoặc Toolbar.

* * *

## Bài 4

Nhúng một font tùy chọn vào ứng dụng bằng `QFontDatabase` và áp dụng font đó cho toàn bộ giao diện.

* * *

# Mini Project cuối buổi: Student Manager Theme Edition

Nâng cấp dự án **Student Manager** :

### Thêm thư mục
    
    
    resources/
    
    icons/
    
    images/
    
    fonts/
    
    qss/

### Chức năng

  * Logo ứng dụng. 
  * Icon cho Toolbar. 
  * Light Theme. 
  * Dark Theme. 
  * Font tùy chỉnh. 
  * `QTableView` có màu xen kẽ. 
  * `QPushButton` có hiệu ứng `:hover` và `:pressed`. 



Mục tiêu là tạo giao diện đồng nhất, hiện đại và dễ bảo trì.

* * *

# Tổng kết Buổi 20

Bạn đã học:

  * Qt Resource System (QRC). 
  * Biên dịch tài nguyên bằng `pyside6-rcc`. 
  * Nhúng icon, ảnh và font. 
  * Thiết kế giao diện bằng QSS. 
  * Tạo và chuyển đổi Theme. 
  * Tổ chức tài nguyên theo chuẩn dự án. 
  * Chuẩn bị ứng dụng cho quá trình đóng gói và phân phối. 



* * *

# Chuẩn bị cho Buổi 21

Ở **Buổi 21** , chúng ta sẽ học về **Dock Widget, MDI (Multiple Document Interface) và Layout chuyên nghiệp**.

Bạn sẽ học:

  * `QDockWidget`. 
  * `QMdiArea`. 
  * `QMdiSubWindow`. 
  * `QSplitter`. 
  * `QStackedWidget`. 
  * `QTabWidget` nâng cao. 
  * Thiết kế giao diện kiểu **Visual Studio Code** , **Qt Creator** , **Photoshop** , **AutoCAD** hoặc các IDE hiện đại. 



Đây là những thành phần giúp bạn xây dựng các ứng dụng desktop phức tạp với nhiều vùng làm việc, cửa sổ con và bố cục linh hoạt.

