# Khóa học PySide6 từ A-Z

# Buổi 16: Delegate và Editor - Làm chủ QStyledItemDelegate

> **Đây là một trong những chủ đề mạnh nhất của Qt.**
> 
> Hầu hết các phần mềm chuyên nghiệp (ERP, CRM, IDE, phần mềm kế toán, quản lý kho...) đều sử dụng **Delegate** để hiển thị và chỉnh sửa dữ liệu.

Sau buổi này bạn sẽ:

  * Hiểu Delegate là gì. 
  * Phân biệt Model, View và Delegate. 
  * Thành thạo `QStyledItemDelegate`. 
  * Tạo Editor tùy chỉnh (`QLineEdit`, `QComboBox`, `QSpinBox`, `QDateEdit`, `QCheckBox`...). 
  * Vẽ (Paint) dữ liệu theo ý muốn. 
  * Chuẩn bị nền tảng cho các bảng dữ liệu chuyên nghiệp. 



* * *

# 1\. Kiến trúc Model/View hoàn chỉnh

Ở buổi trước chúng ta đã học:
    
    
    Model
    
    ↓
    
    View

Thực tế Qt có 3 thành phần:
    
    
    Model
    
    ↓
    
    Delegate
    
    ↓
    
    View

Hay đầy đủ hơn:
    
    
    Người dùng
    
    ↓
    
    View
    
    ↓
    
    Delegate
    
    ↓
    
    Model

Trong đó:

  * **Model** → quản lý dữ liệu. 
  * **View** → hiển thị bảng. 
  * **Delegate** → quyết định cách hiển thị và chỉnh sửa từng ô. 



* * *

# 2\. Delegate là gì?

Giả sử bảng:

Tên| Tuổi| Trạng thái  
---|---|---  
An| 20| Hoạt động  
Bình| 18| Khóa  
  
Nếu không có Delegate:
    
    
    Hoạt động

chỉ là văn bản.

Có Delegate:
    
    
    🟢 Hoạt động

hoặc
    
    
    🔴 Khóa

Hoặc:
    
    
    ██████████ 80%

Thay vì:
    
    
    80

* * *

# 3\. Delegate làm được gì?

Delegate có thể:

  * Đổi màu chữ. 
  * Đổi màu nền. 
  * Hiển thị Icon. 
  * Hiển thị ProgressBar. 
  * Hiển thị ComboBox. 
  * Hiển thị CheckBox. 
  * Hiển thị Calendar. 
  * Hiển thị Rating (★★★★★). 
  * Hiển thị hình ảnh. 



* * *

# 4\. QStyledItemDelegate

Đây là Delegate được dùng nhiều nhất.
    
    
    from PySide6.QtWidgets import QStyledItemDelegate

Tạo:
    
    
    class StudentDelegate(QStyledItemDelegate):
        pass

* * *

# 5\. Các hàm quan trọng

Bạn sẽ thường ghi đè các hàm sau:

Hàm| Chức năng  
---|---  
`paint()`| Vẽ dữ liệu  
`createEditor()`| Tạo widget chỉnh sửa  
`setEditorData()`| Đưa dữ liệu vào editor  
`setModelData()`| Ghi dữ liệu ngược về model  
`updateEditorGeometry()`| Đặt vị trí editor  
  
* * *

# 6\. createEditor()

Ví dụ muốn cột tuổi sử dụng `QSpinBox`.
    
    
    from PySide6.QtWidgets import QSpinBox
    
    def createEditor(
        self,
        parent,
        option,
        index
    ):
        return QSpinBox(parent)

Qt sẽ tự mở `QSpinBox` khi người dùng sửa ô.

* * *

# 7\. Giới hạn giá trị
    
    
    editor = QSpinBox(parent)
    
    editor.setRange(0, 120)
    
    return editor

* * *

# 8\. setEditorData()

Đưa dữ liệu từ Model sang Editor.
    
    
    value = index.data()
    
    editor.setValue(int(value))

Ví dụ:

Model:
    
    
    20

↓

Editor:
    
    
    [20]

* * *

# 9\. setModelData()

Khi người dùng sửa xong:
    
    
    20
    
    ↓
    
    25

Ghi lại vào Model.
    
    
    model.setData(
        index,
        editor.value()
    )

* * *

# 10\. updateEditorGeometry()

Đặt vị trí Editor.
    
    
    editor.setGeometry(
        option.rect
    )

Thông thường chỉ cần một dòng như trên.

* * *

# 11\. Gắn Delegate
    
    
    table.setItemDelegate(
        StudentDelegate()
    )

Hoặc chỉ cho một cột:
    
    
    table.setItemDelegateForColumn(
        1,
        AgeDelegate()
    )

Ví dụ:
    
    
    Cột Tuổi
    
    ↓
    
    SpinBox
    
    Cột Trạng thái
    
    ↓
    
    ComboBox

* * *

# 12\. ComboBox Delegate

Ví dụ cột:
    
    
    Trạng thái

Chỉ cho phép:

  * Hoạt động 
  * Khóa 
  * Nghỉ học 


    
    
    editor = QComboBox(parent)
    
    editor.addItems([
        "Hoạt động",
        "Khóa",
        "Nghỉ học"
    ])

* * *

# 13\. Date Delegate
    
    
    editor = QDateEdit(parent)
    
    editor.setCalendarPopup(True)

Khi sửa:

↓

Hiện Calendar.

* * *

# 14\. CheckBox Delegate

Ví dụ:
    
    
    Đã đóng học phí
    
    ☑
    
    ☐

Có thể dùng:
    
    
    QCheckBox()

hoặc xử lý trực tiếp trong `paint()` để tăng hiệu năng.

* * *

# 15\. Paint()

Đây là phần mạnh nhất.

Ví dụ:
    
    
    def paint(
        self,
        painter,
        option,
        index
    ):

Bạn có thể vẽ bất cứ thứ gì.

* * *

# 16\. Đổi màu theo điểm

Ví dụ:
    
    
    95

↓

Màu xanh.
    
    
    40

↓

Màu đỏ.
    
    
    if score >= 80:
    
        painter.setPen(Qt.green)
    
    else:
    
        painter.setPen(Qt.red)

Sau đó gọi hàm vẽ văn bản hoặc dùng `super().paint(...)` tùy trường hợp.

* * *

# 17\. Vẽ ProgressBar

Thay vì:
    
    
    75

Hiển thị:
    
    
    ███████░░ 75%

Qt cung cấp:
    
    
    QStyleOptionProgressBar

để vẽ thanh tiến trình ngay trong ô.

* * *

# 18\. Hiển thị Icon

Ví dụ:
    
    
    ✔ Đã duyệt
    
    ✖ Chưa duyệt

Trong `paint()`:
    
    
    icon.paint(...)

* * *

# 19\. Đổi màu cả dòng

Ví dụ:

Sinh viên:
    
    
    Nghỉ học

↓

Tô đỏ.

Hoặc:
    
    
    Đã tốt nghiệp

↓

Màu xám.

Bạn có thể thay đổi màu nền hoặc màu chữ trong `paint()` dựa trên dữ liệu của từng dòng.

* * *

# 20\. Ví dụ thực tế

Phần mềm quản lý kho:

Tên hàng| Số lượng  
---|---  
RAM| 100  
SSD| 5  
  
Nếu:
    
    
    <10

↓

Đỏ.

Nếu:
    
    
    >50

↓

Xanh.

Không cần người dùng đọc từng số.

* * *

# 21\. Delegate với nhiều cột

Ví dụ:

Cột| Delegate  
---|---  
Tên| QLineEdit  
Tuổi| QSpinBox  
Giới tính| QComboBox  
Ngày sinh| QDateEdit  
Đã tốt nghiệp| QCheckBox  
  
Mỗi cột có một Delegate riêng.

* * *

# 22\. Không nên làm

Sai:
    
    
    if column == 0:
        ...

rồi tạo rất nhiều `if` trong một Delegate lớn.

Nên:
    
    
    AgeDelegate
    
    GenderDelegate
    
    DateDelegate
    
    ScoreDelegate

Mỗi Delegate chỉ phụ trách một kiểu dữ liệu.

* * *

# 23\. Những lỗi người mới thường gặp

## Lỗi 1

Quên:
    
    
    setModelData()

Kết quả:

Sửa xong.

↓

Không lưu.

* * *

## Lỗi 2

Không gọi:
    
    
    editor.setGeometry(...)

Editor hiển thị sai vị trí.

* * *

## Lỗi 3

Vẽ mọi thứ trong `paint()` mà không cân nhắc hiệu năng.

`paint()` được gọi rất nhiều lần khi cuộn hoặc cập nhật bảng, vì vậy cần giữ mã ngắn gọn và tránh xử lý nặng.

* * *

## Lỗi 4

Một Delegate xử lý mọi cột.

Rất khó bảo trì.

* * *

# Bài tập thực hành

## Bài 1

Viết:
    
    
    AgeDelegate

Hiển thị:
    
    
    QSpinBox

Giới hạn:
    
    
    0-120

* * *

## Bài 2

Viết:
    
    
    GenderDelegate

Hiển thị:
    
    
    QComboBox

Gồm:

  * Nam 
  * Nữ 
  * Khác 



* * *

## Bài 3

Viết:
    
    
    BirthdayDelegate

Hiển thị:
    
    
    QDateEdit

Có Calendar.

* * *

## Bài 4

Đổi màu:

Điểm:
    
    
    >=80
    
    ↓
    
    Xanh
    
    <50
    
    ↓
    
    Đỏ

* * *

# Mini Project cuối buổi: Student Manager - Chỉnh sửa trực tiếp trên bảng

Tiếp tục dự án **Student Manager**.

Yêu cầu:

### Cột Tuổi

  * `QSpinBox`
  * 0–120 



### Cột Lớp

  * `QComboBox`



Ví dụ:

  * CNTT 
  * Kế toán 
  * Điện tử 
  * Marketing 



### Cột Trạng thái

  * `QComboBox`



Ví dụ:

  * Đang học 
  * Bảo lưu 
  * Đã tốt nghiệp 



### Cột Điểm trung bình

Hiển thị màu:

  * ≥ 8.0 → Xanh. 
  * 5.0–7.9 → Cam. 
  * < 5.0 → Đỏ. 



Yêu cầu bổ sung:

  * Người dùng có thể sửa trực tiếp trên `QTableView`. 
  * Dữ liệu được cập nhật ngay vào `StudentTableModel`. 
  * Không sử dụng `QTableWidget`. 



Đây là mô hình thường thấy trong các phần mềm quản lý hiện đại, nơi người dùng chỉnh sửa dữ liệu ngay trên bảng mà không cần mở hộp thoại riêng.

* * *

# Tổng kết Buổi 16

Bạn đã học được:

  * Vai trò của **Delegate** trong kiến trúc Model/View. 
  * Sử dụng `QStyledItemDelegate`. 
  * Tạo các editor tùy chỉnh (`QSpinBox`, `QComboBox`, `QDateEdit`,...). 
  * Đồng bộ dữ liệu giữa editor và model. 
  * Tùy biến cách hiển thị bằng `paint()`. 
  * Thiết kế delegate theo từng cột để mã nguồn rõ ràng và dễ bảo trì. 



Đến thời điểm này, bạn đã nắm được hầu hết các thành phần cốt lõi của hệ thống **Model/View/Delegate** của Qt.

* * *

# Chuẩn bị cho Buổi 17

Ở **Buổi 17** , chúng ta sẽ học về **Threading và Concurrency trong PySide6** với:

  * `QThread`. 
  * `QRunnable`. 
  * `QThreadPool`. 
  * Signal/Slot giữa Thread và GUI. 
  * Cập nhật `QProgressBar` theo thời gian thực. 
  * Hủy tác vụ đang chạy. 
  * Tránh làm treo giao diện (UI Freeze). 



Đây là kỹ năng bắt buộc khi xây dựng các ứng dụng thực tế như:

  * Tải file. 
  * Gọi API. 
  * Xử lý ảnh. 
  * Chuyển văn bản thành giọng nói (TTS). 
  * Nhận dạng giọng nói (STT). 
  * AI và Machine Learning. 
  * Đồng bộ cơ sở dữ liệu. 
  * Web Scraping. 



Buổi này sẽ giúp bạn hiểu cách giữ giao diện luôn mượt mà ngay cả khi ứng dụng đang thực hiện các tác vụ nặng.

