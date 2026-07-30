# Khóa học PySide6 từ A-Z

# Buổi 15: Custom Model - Làm chủ QAbstractTableModel và QAbstractListModel

> **Đây là một trong những buổi nâng cao và quan trọng nhất của Qt.**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu vì sao `QStandardItemModel` vẫn còn hạn chế. 
>   * Hiểu kiến trúc **Model thực sự** của Qt. 
>   * Thành thạo `QAbstractTableModel`. 
>   * Biết cách hiển thị trực tiếp danh sách đối tượng Python. 
>   * Hiểu `QModelIndex`, `Qt.ItemDataRole`. 
>   * Chuẩn bị nền tảng để kết nối SQLite, PostgreSQL, API REST và ORM. 
> 


* * *

# 1\. Vì sao cần Custom Model?

Ở buổi trước, chúng ta dùng:
    
    
    QStandardItemModel

Ví dụ:
    
    
    model.appendRow([
        QStandardItem("An"),
        QStandardItem("20"),
        QStandardItem("an@gmail.com")
    ])

Đơn giản nhưng có một vấn đề lớn.

Giả sử bạn đã có dữ liệu:
    
    
    students = [
        Student("An", 20),
        Student("Bình", 21),
        Student("Cường", 22)
    ]

Bạn lại phải chuyển thành:
    
    
    QStandardItem(...)

Điều này gây:

  * Tốn bộ nhớ. 
  * Chuyển đổi dữ liệu nhiều lần. 
  * Khó đồng bộ khi dữ liệu thay đổi. 



* * *

# 2\. Ý tưởng của Custom Model

Thay vì:
    
    
    SQLite
    
    ↓
    
    Student
    
    ↓
    
    QStandardItem
    
    ↓
    
    QTableView

Ta sẽ dùng:
    
    
    SQLite
    
    ↓
    
    Student
    
    ↓
    
    QAbstractTableModel
    
    ↓
    
    QTableView

Không cần tạo `QStandardItem`.

* * *

# 3\. QAbstractTableModel là gì?

Đây là lớp nền (base class) của mọi bảng dữ liệu trong Qt.

Bạn chỉ cần trả lời cho Qt 4 câu hỏi:
    
    
    Có bao nhiêu hàng?
    
    ↓
    
    Có bao nhiêu cột?
    
    ↓
    
    Ô này chứa gì?
    
    ↓
    
    Tên cột là gì?

Qt sẽ tự hiển thị.

* * *

# 4\. Ví dụ lớp Student
    
    
    class Student:
    
        def __init__(self, name, age, email):
            self.name = name
            self.age = age
            self.email = email

Danh sách:
    
    
    students = [
        Student("An", 20, "an@gmail.com"),
        Student("Bình", 21, "binh@gmail.com"),
        Student("Cường", 22, "cuong@gmail.com")
    ]

* * *

# 5\. Tạo Custom Model
    
    
    from PySide6.QtCore import (
        QAbstractTableModel,
        Qt
    )
    
    class StudentModel(QAbstractTableModel):
    
        def __init__(self, students):
            super().__init__()
    
            self.students = students

* * *

# 6\. rowCount()

Qt hỏi:
    
    
    Có bao nhiêu hàng?

Ta trả lời:
    
    
    def rowCount(self, parent=None):
    
        return len(self.students)

* * *

# 7\. columnCount()

Qt hỏi:
    
    
    Có bao nhiêu cột?

Ví dụ:
    
    
    def columnCount(self, parent=None):
    
        return 3

Ba cột:

  * Tên 
  * Tuổi 
  * Email 



* * *

# 8\. QModelIndex

Qt không truyền:
    
    
    Hàng 3
    Cột 2

Mà truyền:
    
    
    QModelIndex

Ví dụ:
    
    
    index.row()

↓
    
    
    3

* * *
    
    
    index.column()

↓
    
    
    2

* * *

# 9\. data()

Đây là hàm quan trọng nhất.
    
    
    def data(self, index, role):

Qt sẽ gọi hàm này hàng nghìn lần để lấy dữ liệu.

* * *

Ví dụ:
    
    
    row = index.row()
    
    column = index.column()
    
    student = self.students[row]

* * *

Nếu:
    
    
    column == 0

↓
    
    
    student.name

* * *

Nếu:
    
    
    column == 1

↓
    
    
    student.age

* * *

Nếu:
    
    
    column == 2

↓
    
    
    student.email

* * *

# 10\. Qt.ItemDataRole

Qt gọi `data()` với nhiều mục đích.

Ví dụ:
    
    
    Qt.DisplayRole

↓

Hiển thị.

* * *
    
    
    Qt.DecorationRole

↓

Icon.

* * *
    
    
    Qt.ToolTipRole

↓

Tooltip.

* * *

Thông thường:
    
    
    if role == Qt.DisplayRole:

là đủ để hiển thị văn bản.

* * *

# 11\. Ví dụ data()
    
    
    def data(self, index, role):
    
        if role != Qt.DisplayRole:
            return None
    
        student = self.students[index.row()]
    
        if index.column() == 0:
            return student.name
    
        if index.column() == 1:
            return student.age
    
        if index.column() == 2:
            return student.email

* * *

# 12\. headerData()

Tên cột:
    
    
    def headerData(
        self,
        section,
        orientation,
        role
    ):

Ví dụ:
    
    
    headers = [
        "Tên",
        "Tuổi",
        "Email"
    ]
    
    
    if (
        role == Qt.DisplayRole
        and orientation == Qt.Horizontal
    ):
    
        return headers[section]

* * *

# 13\. Hoàn chỉnh Custom Model
    
    
    table = QTableView()
    
    model = StudentModel(students)
    
    table.setModel(model)

Không cần:
    
    
    QStandardItem

* * *

# 14\. Thêm dữ liệu

Sai:
    
    
    students.append(...)

View sẽ không biết.

Đúng:
    
    
    self.beginInsertRows(
        QModelIndex(),
        row,
        row
    )
    
    self.students.append(student)
    
    self.endInsertRows()

Qt sẽ cập nhật View đúng cách.

* * *

# 15\. Xóa dữ liệu
    
    
    self.beginRemoveRows(
        QModelIndex(),
        row,
        row
    )
    
    del self.students[row]
    
    self.endRemoveRows()

* * *

# 16\. Cập nhật dữ liệu

Ví dụ:
    
    
    student.name = "Nguyễn An"

Sau đó phát tín hiệu:
    
    
    self.dataChanged.emit(
        topLeft,
        bottomRight
    )

Hoặc:
    
    
    index = self.index(row, column)
    self.dataChanged.emit(index, index)

View sẽ cập nhật ngay.

* * *

# 17\. QAbstractListModel

Nếu chỉ có:
    
    
    Python
    
    Java
    
    Go
    
    Rust

Không cần bảng.

Dùng:
    
    
    QAbstractListModel

Chỉ cần:

  * `rowCount()`
  * `data()`



* * *

# 18\. Ưu điểm Custom Model

Không còn:
    
    
    Student
    
    ↓
    
    QStandardItem
    
    ↓
    
    QTableView

Mà:
    
    
    Student
    
    ↓
    
    QAbstractTableModel
    
    ↓
    
    QTableView

Nhanh hơn.

Ít RAM hơn.

Dễ bảo trì hơn.

* * *

# 19\. Những lỗi người mới thường gặp

## Lỗi 1

Quên kiểm tra:
    
    
    role

Kết quả:

Qt gọi:
    
    
    data()

hàng nghìn lần.

Ứng dụng chậm.

* * *

## Lỗi 2

Không gọi:
    
    
    beginInsertRows()

View không cập nhật.

* * *

## Lỗi 3

Không gọi:
    
    
    dataChanged.emit()

Sau khi sửa dữ liệu.

* * *

## Lỗi 4

Tạo:
    
    
    QStandardItem

Trong Custom Model.

Điều này làm mất ý nghĩa của Custom Model.

* * *

# Bài tập thực hành

## Bài 1

Viết:
    
    
    StudentModel

Hiển thị:

|Tên|Tuổi|Email|

* * *

## Bài 2

Thêm:
    
    
    add_student()

Sử dụng:

  * `beginInsertRows()`
  * `endInsertRows()`



* * *

## Bài 3

Viết:
    
    
    remove_student()

Sử dụng:

  * `beginRemoveRows()`
  * `endRemoveRows()`



* * *

## Bài 4

Cho phép sửa:
    
    
    student.name

Sau đó cập nhật View bằng:
    
    
    dataChanged.emit()

* * *

# Mini Project cuối buổi: Student Manager với Custom Model

Chuyển dự án **Student Manager** sang sử dụng `QAbstractTableModel`.

Cấu trúc:
    
    
    student_manager/
    │
    ├── models/
    │   ├── student.py
    │   └── student_table_model.py
    │
    ├── views/
    │   └── main_window.py
    │
    ├── controllers/
    │   └── student_controller.py
    │
    ├── services/
    │   └── student_repository.py
    │
    └── main.py

Yêu cầu:

  * `StudentRepository` lưu danh sách `Student`. 
  * `StudentTableModel` hiển thị trực tiếp danh sách đó. 
  * Chức năng: 
    * Thêm sinh viên. 
    * Xóa sinh viên. 
    * Cập nhật thông tin. 
  * Không sử dụng `QStandardItemModel`. 
  * `QTableView` phải tự cập nhật khi dữ liệu thay đổi. 



Đây là mô hình thường thấy trong các ứng dụng quản lý chuyên nghiệp.

* * *

# Tổng kết Buổi 15

Bạn đã bước sang cấp độ nâng cao của Qt:

  * Hiểu kiến trúc **Model/View** ở mức cốt lõi. 
  * Biết xây dựng `QAbstractTableModel`. 
  * Hiểu vai trò của: 
    * `rowCount()`
    * `columnCount()`
    * `data()`
    * `headerData()`
  * Biết sử dụng: 
    * `beginInsertRows()`
    * `endInsertRows()`
    * `beginRemoveRows()`
    * `endRemoveRows()`
    * `dataChanged.emit()`
  * Hiển thị trực tiếp danh sách đối tượng Python mà không cần chuyển đổi sang `QStandardItem`. 



Đây là nền tảng để xây dựng các ứng dụng có hiệu năng cao và dễ tích hợp với cơ sở dữ liệu.

* * *

# Chuẩn bị cho Buổi 16

Ở **Buổi 16** , chúng ta sẽ học về **Delegate và Editor** – một trong những tính năng mạnh nhất của Qt.

Bạn sẽ học:

  * `QStyledItemDelegate`. 
  * Tạo ô chỉnh sửa tùy biến trong `QTableView`. 
  * Hiển thị `QComboBox`, `QSpinBox`, `QDateEdit` ngay trong từng ô. 
  * Vẽ (paint) ô dữ liệu theo ý muốn. 
  * Tô màu dòng, biểu tượng trạng thái, thanh tiến trình (progress bar) trong bảng. 



Sau buổi này, bạn sẽ có thể tạo những bảng dữ liệu chuyên nghiệp giống như các phần mềm ERP, CRM và hệ thống quản lý doanh nghiệp hiện đại.

