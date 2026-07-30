# Khóa học PySide6 từ A-Z

# Buổi 12: Qt Style Sheets (QSS) - Thiết kế giao diện hiện đại và chuyên nghiệp

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu QSS là gì và cách hoạt động. 
>   * Biết áp dụng Style cho toàn bộ ứng dụng hoặc từng Widget. 
>   * Thành thạo Selector trong QSS. 
>   * Biết sử dụng các Pseudo State (`:hover`, `:pressed`, `:focus`,...). 
>   * Tổ chức Theme sáng/tối bằng file `.qss`. 
>   * Thiết kế giao diện hiện đại, dễ bảo trì. 
> 


* * *

# 1\. QSS là gì?

QSS (**Qt Style Sheets**) là hệ thống định dạng giao diện của Qt, có cú pháp rất giống CSS.

Ví dụ:
    
    
    QPushButton {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
    }

Sau khi áp dụng:

  * Nút có nền xanh. 
  * Chữ màu trắng. 
  * Góc bo tròn. 



> Nếu bạn đã biết CSS thì việc học QSS sẽ rất dễ.

* * *

# 2\. Áp dụng QSS

Có hai cách phổ biến.

## Cách 1: Áp dụng trực tiếp
    
    
    button.setStyleSheet("""
    QPushButton {
        background-color: #2196F3;
        color: white;
    }
    """)

Chỉ `button` này được đổi giao diện.

* * *

## Cách 2: Áp dụng cho toàn bộ ứng dụng
    
    
    app.setStyleSheet("""
    QPushButton {
        font-size:16px;
    }
    """)

Mọi `QPushButton` đều nhận style này.

Đây là cách nên dùng trong dự án lớn.

* * *

# 3\. Selector cơ bản

Ví dụ:
    
    
    QPushButton {
        background-color: #4CAF50;
    }

Áp dụng cho:

  * btnSave 
  * btnDelete 
  * btnExit 



* * *

### Chỉ áp dụng cho một widget

Nếu trong Qt Designer:
    
    
    objectName = btnSave

QSS:
    
    
    QPushButton#btnSave {
        background-color: green;
    }

Chỉ `btnSave` đổi màu.

* * *

# 4\. Các thuộc tính thường dùng

## Màu nền
    
    
    background-color: #2196F3;

* * *

## Màu chữ
    
    
    color: white;

* * *

## Bo góc
    
    
    border-radius: 10px;

* * *

## Viền
    
    
    border: 2px solid #1976D2;

* * *

## Padding
    
    
    padding: 8px;

Giúp nội dung không dính sát mép.

* * *

## Font
    
    
    font-size: 14px;
    font-weight: bold;

* * *

# 5\. Pseudo State

Giống CSS.

## Hover
    
    
    QPushButton:hover {
        background-color: #42A5F5;
    }

Khi rê chuột:

↓

Đổi màu.

* * *

## Pressed
    
    
    QPushButton:pressed {
        background-color: #1565C0;
    }

Khi nhấn:

↓

Đổi màu đậm hơn.

* * *

## Disabled
    
    
    QPushButton:disabled {
        background-color: gray;
    }

* * *

## Focus
    
    
    QLineEdit:focus {
        border:2px solid #2196F3;
    }

Khi người dùng nhập dữ liệu:

↓

Viền xanh.

* * *

# 6\. Styling QLineEdit
    
    
    QLineEdit {
    
        border:1px solid gray;
    
        border-radius:6px;
    
        padding:6px;
    
        background:white;
    }
    
    QLineEdit:focus {
    
        border:2px solid #2196F3;
    }

Kết quả:

  * Bình thường viền xám. 
  * Khi nhập liệu viền xanh. 



* * *

# 7\. Styling QLabel
    
    
    QLabel {
    
        color:#333333;
    
        font-size:16px;
    }

* * *

# 8\. Styling QComboBox
    
    
    QComboBox {
    
        border:1px solid gray;
    
        padding:5px;
    
        border-radius:6px;
    }

* * *

# 9\. Styling QTableWidget
    
    
    QTableWidget {
    
        gridline-color:lightgray;
    
        selection-background-color:#2196F3;
    
        font-size:14px;
    }

* * *

Header:
    
    
    QHeaderView::section {
    
        background:#1976D2;
    
        color:white;
    
        padding:6px;
    }

* * *

# 10\. Styling QMenuBar
    
    
    QMenuBar {
    
        background:#1976D2;
    
        color:white;
    }

* * *

Menu:
    
    
    QMenu {
    
        background:white;
    }

* * *

# 11\. Styling QStatusBar
    
    
    QStatusBar {
    
        background:#EEEEEE;
    }

* * *

# 12\. Styling QTabWidget
    
    
    QTabBar::tab {
    
        padding:8px;
    
        background:#DDDDDD;
    }

Tab đang chọn:
    
    
    QTabBar::tab:selected {
    
        background:#2196F3;
    
        color:white;
    }

* * *

# 13\. Styling ScrollBar
    
    
    QScrollBar:vertical {
    
        width:12px;
    }

Thanh kéo:
    
    
    QScrollBar::handle:vertical {
    
        background:#999999;
    
        border-radius:6px;
    }

* * *

# 14\. File QSS riêng

Không nên viết:
    
    
    app.setStyleSheet("""
    ...
    300 dòng...
    """)

Nên tạo:
    
    
    resources/
    
    styles/
    
    light.qss
    
    dark.qss

* * *

Đọc file:
    
    
    with open(
        "resources/styles/light.qss",
        "r",
        encoding="utf-8"
    ) as file:
    
        app.setStyleSheet(file.read())

Đây là cách làm trong hầu hết các dự án chuyên nghiệp.

* * *

# 15\. Theme sáng và tối

## light.qss
    
    
    QWidget {
        background:white;
        color:black;
    }

* * *

## dark.qss
    
    
    QWidget {
        background:#2B2B2B;
        color:white;
    }

* * *

Đổi Theme:
    
    
    def load_theme(path):
    
        with open(path, encoding="utf-8") as file:
    
            app.setStyleSheet(file.read())

* * *

# 16\. Tổ chức thư mục
    
    
    project/
    
    resources/
    
        styles/
    
            light.qss
    
            dark.qss
    
        icons/
    
            save.svg
    
            delete.svg
    
            edit.svg
    
        images/
    
            logo.png

* * *

# 17\. Ví dụ hoàn chỉnh
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QPushButton,
    )
    
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
    
    QPushButton{
    
    background:#2196F3;
    
    color:white;
    
    border-radius:8px;
    
    padding:8px;
    
    font-size:14px;
    }
    
    QPushButton:hover{
    
    background:#42A5F5;
    }
    
    QPushButton:pressed{
    
    background:#1565C0;
    }
    
    """)
    
    button = QPushButton("Lưu")
    
    button.show()
    
    app.exec()

* * *

# 18\. Những lỗi người mới thường gặp

## Lỗi 1

Viết:
    
    
    background:

Thay vì:
    
    
    background-color:

Trong QSS, một số thuộc tính CSS không được hỗ trợ đầy đủ. Hãy ưu tiên dùng các thuộc tính được Qt hỗ trợ như `background-color`, `border`, `padding`,...

* * *

## Lỗi 2

Không đặt:
    
    
    objectName

Khi đó:
    
    
    #btnSave

sẽ không áp dụng được.

* * *

## Lỗi 3

Đặt toàn bộ Style trong Python.
    
    
    setStyleSheet("""
    500 dòng
    """)

Khó bảo trì.

* * *

## Lỗi 4

Mỗi Button một Style.
    
    
    button1.setStyleSheet(...)
    
    button2.setStyleSheet(...)
    
    button3.setStyleSheet(...)

Nên dùng:
    
    
    app.setStyleSheet(...)

hoặc file `.qss`.

* * *

# Thiết kế giao diện hiện đại

Một số nguyên tắc UI nên áp dụng:

  * Khoảng cách giữa các widget: **8–12 px**. 
  * Bo góc: **6–10 px**. 
  * Font: **10–12 pt** hoặc **14–16 px**. 
  * Không dùng quá nhiều màu nổi bật. 
  * Chỉ dùng **1 màu chủ đạo** (ví dụ xanh dương) và **1 màu nhấn** (ví dụ đỏ cho nút Xóa). 



* * *

# Bài tập thực hành

## Bài 1

Thiết kế:

Nút **Lưu**

  * Xanh. 
  * Hover sáng hơn. 
  * Pressed đậm hơn. 
  * Chữ trắng. 



* * *

## Bài 2

Thiết kế:

`QLineEdit`

  * Viền xám. 
  * Focus viền xanh. 
  * Bo góc. 
  * Padding 6 px. 



* * *

## Bài 3

Thiết kế:

`QTableWidget`

  * Header xanh. 
  * Chữ trắng. 
  * Dòng được chọn có nền xanh nhạt. 



* * *

## Bài 4

Tạo:
    
    
    light.qss
    
    dark.qss

Viết chức năng chuyển đổi Theme bằng hai nút:

  * 🌞 Light 
  * 🌙 Dark 



* * *

# Mini Project cuối buổi: Student Manager Theme

Tiếp tục dự án **Student Manager** từ các buổi trước.

Yêu cầu:

  * Thiết kế giao diện bằng Qt Designer. 
  * Tạo hai file: 
    * `light.qss`
    * `dark.qss`
  * Áp dụng QSS cho: 
    * `QPushButton`
    * `QLineEdit`
    * `QComboBox`
    * `QTableWidget`
    * `QStatusBar`
  * Thêm menu **Giao diện** với hai lựa chọn: 
    * Light Theme. 
    * Dark Theme. 
  * Khi người dùng chọn một mục, ứng dụng đổi Theme ngay mà không cần khởi động lại. 



> Đây là nền tảng để xây dựng các ứng dụng desktop hiện đại có giao diện nhất quán và dễ bảo trì.

* * *

# Tổng kết Buổi 12

Bạn đã nắm được:

  * Khái niệm và cú pháp của **QSS**. 
  * Cách áp dụng Style cho từng widget và toàn ứng dụng. 
  * Selector theo loại widget và `objectName`. 
  * Pseudo State (`:hover`, `:pressed`, `:focus`, `:disabled`). 
  * Tổ chức Theme bằng file `.qss`. 
  * Các nguyên tắc thiết kế giao diện chuyên nghiệp. 



QSS là một kỹ năng quan trọng giúp tách phần **giao diện (Presentation)** khỏi **logic xử lý** , tương tự như CSS trong phát triển web.

* * *

# Chuẩn bị cho Buổi 13

Ở **Buổi 13** , chúng ta sẽ học về **Dialog và Multi-Window Application**.

Bạn sẽ học:

  * `QDialog`. 
  * `QMessageBox`. 
  * `QFileDialog`. 
  * `QColorDialog`. 
  * `QFontDialog`. 
  * `QInputDialog`. 
  * `QProgressDialog`. 
  * Giao tiếp giữa nhiều cửa sổ bằng Signal/Slot. 
  * Thiết kế hộp thoại nhập dữ liệu theo mô hình MVC. 



Sau buổi học này, bạn sẽ có thể xây dựng các ứng dụng nhiều cửa sổ, nhiều hộp thoại và có trải nghiệm người dùng chuyên nghiệp giống như các phần mềm desktop thương mại.

