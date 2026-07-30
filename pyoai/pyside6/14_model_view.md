# Khóa học PySide6 từ A-Z

# Buổi 14: Model/View Architecture - Làm chủ QTableView, QListView, QTreeView và QStandardItemModel

> **Đây là một trong những buổi quan trọng nhất của toàn bộ khóa học.**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu kiến trúc **Model/View** của Qt. 
>   * Phân biệt `QTableWidget` và `QTableView`. 
>   * Thành thạo `QStandardItemModel`. 
>   * Làm việc với `QListView`, `QTreeView`, `QTableView`. 
>   * Biết sử dụng `QSortFilterProxyModel` để sắp xếp và lọc dữ liệu. 
>   * Xây dựng giao diện có thể xử lý hàng chục nghìn đến hàng triệu bản ghi. 
> 


* * *

# 1\. Vì sao Qt có Model/View?

Cho đến nay chúng ta thường dùng:
    
    
    QTableWidget

Ví dụ:
    
    
    table.setItem(0, 0, QTableWidgetItem("An"))
    table.setItem(0, 1, QTableWidgetItem("20"))

Rất đơn giản.

Nhưng nếu có:
    
    
    1.000.000 sinh viên

thì sao?

Mỗi ô đều là một `QTableWidgetItem`.

↓

Bộ nhớ tăng rất lớn.

↓

Hiệu năng giảm.

Qt giải quyết vấn đề này bằng **Model/View Architecture**.

* * *

# 2\. Kiến trúc Model/View

Qt tách dữ liệu và giao diện thành hai phần.
    
    
    Model
    │
    │  Dữ liệu
    │
    ▼
    View
    │
    │  Hiển thị
    │
    ▼
    Người dùng

Ưu điểm:

  * Không phụ thuộc giao diện. 
  * Dễ thay đổi. 
  * Tốc độ cao. 
  * Tái sử dụng dữ liệu. 



* * *

# 3\. So sánh QTableWidget và QTableView

QTableWidget| QTableView  
---|---  
Có dữ liệu bên trong| Không chứa dữ liệu  
Dễ học| Chuyên nghiệp  
Dự án nhỏ| Dự án lớn  
Chậm khi dữ liệu lớn| Rất nhanh  
  
* * *

# 4\. Model là gì?

Model là nơi chứa dữ liệu.

Ví dụ:
    
    
    Tên
    
    Tuổi
    
    Email

Model **không biết giao diện**.

Model chỉ biết:
    
    
    Có bao nhiêu hàng?
    
    Có bao nhiêu cột?
    
    Dữ liệu ô này là gì?

* * *

# 5\. View là gì?

View chỉ hiển thị.

Ví dụ:
    
    
    QTableView
    
    ↓
    
    Hiển thị dữ liệu
    
    ↓
    
    Không lưu dữ liệu

* * *

# 6\. QStandardItemModel

Đây là Model đơn giản và phổ biến nhất.
    
    
    from PySide6.QtGui import QStandardItemModel

Khởi tạo:
    
    
    model = QStandardItemModel()

* * *

# 7\. Thiết lập cột
    
    
    model.setHorizontalHeaderLabels([
        "Tên",
        "Tuổi",
        "Email"
    ])

* * *

# 8\. Thêm dữ liệu
    
    
    from PySide6.QtGui import QStandardItem
    
    model.appendRow([
        QStandardItem("An"),
        QStandardItem("20"),
        QStandardItem("an@gmail.com")
    ])

* * *

# 9\. Gắn Model vào View
    
    
    table.setModel(model)

Luồng hoạt động:
    
    
    Model
    
    ↓
    
    QTableView
    
    ↓
    
    Hiển thị

* * *

# 10\. Ví dụ hoàn chỉnh
    
    
    import sys
    
    from PySide6.QtGui import (
        QStandardItem,
        QStandardItemModel,
    )
    
    from PySide6.QtWidgets import (
        QApplication,
        QTableView,
    )
    
    app = QApplication(sys.argv)
    
    table = QTableView()
    
    model = QStandardItemModel()
    
    model.setHorizontalHeaderLabels([
        "Tên",
        "Tuổi"
    ])
    
    model.appendRow([
        QStandardItem("An"),
        QStandardItem("20")
    ])
    
    model.appendRow([
        QStandardItem("Bình"),
        QStandardItem("22")
    ])
    
    table.setModel(model)
    
    table.show()
    
    app.exec()

* * *

# 11\. QListView

Hiển thị danh sách.
    
    
    list_view = QListView()

Model:
    
    
    model = QStandardItemModel()

Thêm dữ liệu:
    
    
    model.appendRow(
        QStandardItem("Python")
    )
    
    model.appendRow(
        QStandardItem("Java")
    )
    
    model.appendRow(
        QStandardItem("Go")
    )

Gắn:
    
    
    list_view.setModel(model)

* * *

# 12\. QTreeView

Ví dụ:
    
    
    Project
    
    ├── models
    
    ├── views
    
    └── controllers

Tạo:
    
    
    root = QStandardItem("Project")

Con:
    
    
    root.appendRow(
        QStandardItem("models")
    )

Model:
    
    
    model.appendRow(root)

* * *

# 13\. Chỉnh sửa dữ liệu
    
    
    item = model.item(0, 0)
    
    item.setText("Nguyễn An")

View tự động cập nhật.

Không cần gọi `refresh()`.

* * *

# 14\. Xóa dòng
    
    
    model.removeRow(0)

* * *

# 15\. Đọc dữ liệu
    
    
    item = model.item(0, 0)
    
    print(item.text())

* * *

# 16\. QSortFilterProxyModel

Đây là lớp cực kỳ mạnh.

Có thể:

  * Sắp xếp. 
  * Lọc. 
  * Tìm kiếm. 



Không làm thay đổi dữ liệu gốc.

* * *

Tạo:
    
    
    from PySide6.QtCore import QSortFilterProxyModel
    
    proxy = QSortFilterProxyModel()

Nguồn:
    
    
    proxy.setSourceModel(model)

View:
    
    
    table.setModel(proxy)

* * *

# 17\. Sắp xếp
    
    
    table.setSortingEnabled(True)

Click Header:

↓

Tự sắp xếp.

* * *

# 18\. Lọc
    
    
    proxy.setFilterFixedString("An")

Chỉ hiển thị:
    
    
    An

* * *

# 19\. Lọc theo cột
    
    
    proxy.setFilterKeyColumn(0)

Ví dụ:
    
    
    Tên

Hoặc:
    
    
    proxy.setFilterKeyColumn(2)

↓
    
    
    Email

* * *

# 20\. Tìm kiếm theo QLineEdit
    
    
    edit.textChanged.connect(
        proxy.setFilterFixedString
    )

Người dùng nhập:
    
    
    Nguyễn

↓

Bảng tự lọc.

* * *

# 21\. Model/View hoạt động như thế nào?
    
    
    SQLite
    
    ↓
    
    StudentRepository
    
    ↓
    
    QStandardItemModel
    
    ↓
    
    QSortFilterProxyModel
    
    ↓
    
    QTableView
    
    ↓
    
    Người dùng

Đây là kiến trúc được rất nhiều phần mềm doanh nghiệp sử dụng.

* * *

# 22\. Những lỗi người mới thường gặp

## Lỗi 1

Dùng:
    
    
    table.insertRow()

với:
    
    
    QTableView

Sai.

`QTableView` không quản lý dữ liệu.

Phải thêm vào:
    
    
    model.appendRow(...)

* * *

## Lỗi 2

Quên:
    
    
    table.setModel(model)

Bảng sẽ không hiển thị gì.

* * *

## Lỗi 3

Thêm:
    
    
    QTableWidgetItem

vào:
    
    
    QTableView

Sai.

Phải dùng:
    
    
    QStandardItem

* * *

## Lỗi 4

Thay đổi Model nhưng cố cập nhật View bằng tay.

Trong Model/View, View tự động cập nhật khi Model thay đổi.

* * *

# Bài tập thực hành

## Bài 1

Tạo:
    
    
    QTableView

Hiển thị:

Tên| Tuổi  
---|---  
An| 20  
Bình| 21  
Cường| 22  
  
* * *

## Bài 2

Thêm Button:
    
    
    Thêm

↓

Thêm:
    
    
    Dũng

vào Model.

* * *

## Bài 3

Thêm Button:
    
    
    Xóa dòng đầu

↓
    
    
    removeRow(0)

* * *

## Bài 4

Thêm:
    
    
    QLineEdit

↓

Tìm kiếm theo tên.

Gợi ý:

  * Dùng `QSortFilterProxyModel`. 
  * Kết nối `textChanged` với `setFilterFixedString()`. 
  * Đặt `proxy.setFilterKeyColumn(0)` để lọc theo cột tên. 



* * *

# Mini Project cuối buổi: Student Manager - Bảng dữ liệu chuyên nghiệp

Tiếp tục dự án **Student Manager**.

Thay thế:
    
    
    QTableWidget

bằng:
    
    
    QTableView

và:
    
    
    QStandardItemModel

Yêu cầu:

  * Hiển thị các cột: 
    * Họ tên. 
    * Tuổi. 
    * Email. 
    * Lớp. 
  * Nút **Thêm** : 
    * Thêm một sinh viên vào Model. 
  * Nút **Xóa** : 
    * Xóa dòng đang được chọn. 
  * `QLineEdit` tìm kiếm: 
    * Lọc theo cột Họ tên. 
  * Cho phép sắp xếp bằng cách nhấp vào tiêu đề cột (`setSortingEnabled(True)`). 



Đây là bước chuyển từ widget tiện lợi sang kiến trúc Model/View chuyên nghiệp.

* * *

# Tổng kết Buổi 14

Bạn đã học những kiến thức nền tảng quan trọng của Qt:

  * Hiểu kiến trúc **Model/View**. 
  * Phân biệt `QTableWidget` và `QTableView`. 
  * Làm việc với `QStandardItemModel`. 
  * Hiển thị dữ liệu bằng `QListView`, `QTreeView`, `QTableView`. 
  * Sử dụng `QSortFilterProxyModel` để sắp xếp và lọc dữ liệu. 
  * Hiểu cách tổ chức dữ liệu cho các ứng dụng quy mô lớn. 



Đây là nền tảng để kết nối dữ liệu từ SQLite, PostgreSQL hoặc các API vào giao diện mà vẫn giữ được hiệu năng và khả năng mở rộng.

* * *

# Chuẩn bị cho Buổi 15

Ở **Buổi 15** , chúng ta sẽ học về **Model tùy chỉnh (Custom Model)** với:

  * `QAbstractTableModel`. 
  * `QAbstractListModel`. 
  * `QAbstractItemModel`. 
  * `QModelIndex`. 
  * `data()`, `rowCount()`, `columnCount()`, `headerData()`. 
  * Hiển thị trực tiếp danh sách đối tượng Python (`Student`, `Employee`,...) mà không cần chuyển sang `QStandardItemModel`. 



Đây là kỹ thuật được sử dụng trong các ứng dụng PySide6 chuyên nghiệp khi làm việc với dữ liệu lớn, dữ liệu động hoặc các lớp nghiệp vụ riêng của ứng dụng.

