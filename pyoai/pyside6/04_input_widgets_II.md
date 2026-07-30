# Khóa học PySide6 từ A-Z

# Buổi 4: Các Widget nhập liệu nâng cao

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Thành thạo các widget nhập liệu nâng cao trong PySide6. 
>   * Hiểu khi nào nên dùng từng widget. 
>   * Biết lấy và gán dữ liệu cho từng widget. 
>   * Biết kết hợp các widget để xây dựng một biểu mẫu chuyên nghiệp. 
>   * Hoàn thành một ứng dụng **Đăng ký thành viên** có đầy đủ các loại điều khiển. 
> 


* * *

# 1\. Tổng quan

Đến nay chúng ta đã học:
    
    
    QLabel
    QPushButton
    QLineEdit
    QTextEdit
    QPlainTextEdit

Hôm nay chúng ta học các widget chuyên dùng cho nhập liệu có cấu trúc:
    
    
    QSpinBox
    QDoubleSpinBox
    QComboBox
    QCheckBox
    QRadioButton
    QSlider
    QDateEdit
    QTimeEdit
    QDateTimeEdit

Đây là các widget xuất hiện trong hầu hết phần mềm quản lý.

* * *

# 2\. QSpinBox

Dùng để nhập **số nguyên**.

Ví dụ:
    
    
    age = QSpinBox()

Hiển thị:
    
    
    [ 18 ▲ ]
         ▼

* * *

## Giới hạn giá trị
    
    
    age.setRange(1, 120)

* * *

## Giá trị mặc định
    
    
    age.setValue(20)

* * *

## Lấy giá trị
    
    
    print(age.value())

* * *

## Bước nhảy
    
    
    age.setSingleStep(5)

Kết quả:
    
    
    5
    
    10
    
    15
    
    20

* * *

## Tiền tố và hậu tố
    
    
    age.setSuffix(" tuổi")

Hiển thị:
    
    
    25 tuổi

Hoặc:
    
    
    spin.setPrefix("$ ")

Hiển thị:
    
    
    $ 500

* * *

# 3\. QDoubleSpinBox

Dùng cho **số thực**.

Ví dụ:
    
    
    price = QDoubleSpinBox()

* * *

## Số chữ số thập phân
    
    
    price.setDecimals(2)

* * *

## Bước nhảy
    
    
    price.setSingleStep(0.5)

* * *

## Giá trị
    
    
    price.value()

Ví dụ:
    
    
    15.50

* * *

# 4\. QComboBox

Danh sách chọn.

Ví dụ:
    
    
    combo = QComboBox()

* * *

## Thêm dữ liệu
    
    
    combo.addItem("Python")
    combo.addItem("Java")
    combo.addItem("Rust")

Hoặc:
    
    
    combo.addItems([
        "Python",
        "C++",
        "Go",
        "Rust"
    ])

* * *

## Lấy giá trị
    
    
    combo.currentText()

* * *

## Lấy vị trí
    
    
    combo.currentIndex()

* * *

## Chọn mặc định
    
    
    combo.setCurrentIndex(2)

* * *

## Xóa
    
    
    combo.clear()

* * *

# 5\. QCheckBox

Dùng cho lựa chọn **Có / Không** hoặc nhiều lựa chọn độc lập.

Ví dụ:
    
    
    check = QCheckBox("Đồng ý điều khoản")

* * *

## Kiểm tra trạng thái
    
    
    check.isChecked()

Ví dụ:
    
    
    if check.isChecked():
        print("Đã đồng ý")

* * *

## Chọn
    
    
    check.setChecked(True)

* * *

# 6\. QRadioButton

Dùng khi chỉ được chọn **một** trong nhiều lựa chọn.

Ví dụ:
    
    
    male = QRadioButton("Nam")
    female = QRadioButton("Nữ")

Khi đặt trong cùng một container hoặc `QButtonGroup`, chỉ một lựa chọn được chọn tại một thời điểm.

* * *

## Kiểm tra
    
    
    male.isChecked()

* * *

## Chọn
    
    
    male.setChecked(True)

* * *

# 7\. QButtonGroup

Giúp quản lý nhóm RadioButton.
    
    
    from PySide6.QtWidgets import QButtonGroup
    
    group = QButtonGroup()
    
    group.addButton(male)
    group.addButton(female)

Việc dùng `QButtonGroup` giúp mã nguồn rõ ràng hơn và thuận tiện khi cần xử lý nhiều lựa chọn.

* * *

# 8\. QSlider

Thanh kéo.

Ví dụ:
    
    
    slider = QSlider()

Thông thường ta nên chỉ rõ hướng:
    
    
    from PySide6.QtCore import Qt
    
    slider = QSlider(Qt.Orientation.Horizontal)

* * *

## Khoảng giá trị
    
    
    slider.setRange(0, 100)

* * *

## Giá trị
    
    
    slider.value()

* * *

## Giá trị mặc định
    
    
    slider.setValue(30)

* * *

Ví dụ:
    
    
    0 --------------------100
    
              ●

* * *

# 9\. QDateEdit

Chọn ngày.
    
    
    date = QDateEdit()

* * *

## Ngày hiện tại
    
    
    from PySide6.QtCore import QDate
    
    date.setDate(QDate.currentDate())

* * *

## Lấy ngày
    
    
    date.date()

* * *

## Định dạng
    
    
    date.setDisplayFormat("dd/MM/yyyy")

Ví dụ:
    
    
    07/07/2026

* * *

## Hiển thị lịch
    
    
    date.setCalendarPopup(True)

Khi nhấn vào ô nhập, người dùng có thể chọn ngày từ lịch thay vì nhập tay.

* * *

# 10\. QTimeEdit

Chọn giờ.
    
    
    time = QTimeEdit()

* * *

## Giờ hiện tại
    
    
    from PySide6.QtCore import QTime
    
    time.setTime(QTime.currentTime())

* * *

## Định dạng
    
    
    time.setDisplayFormat("HH:mm:ss")

* * *

# 11\. QDateTimeEdit

Kết hợp ngày và giờ.
    
    
    from PySide6.QtCore import QDateTime
    
    datetime_edit = QDateTimeEdit()
    datetime_edit.setDateTime(QDateTime.currentDateTime())

Rất hữu ích trong các ứng dụng quản lý lịch hẹn hoặc ghi nhận thời gian tạo dữ liệu.

* * *

# 12\. Ví dụ hoàn chỉnh: Form đăng ký thành viên
    
    
    import sys
    
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import (
        QApplication,
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDateEdit,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
        QMessageBox,
        QPushButton,
        QRadioButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )
    
    
    def save():
        gender = "Nam" if male.isChecked() else "Nữ"
    
        hobbies = []
    
        if hobby_read.isChecked():
            hobbies.append("Đọc sách")
    
        if hobby_music.isChecked():
            hobbies.append("Âm nhạc")
    
        if hobby_sport.isChecked():
            hobbies.append("Thể thao")
    
        info = (
            f"Họ tên: {name.currentText()}\n"
            f"Tuổi: {age.value()}\n"
            f"Chiều cao: {height.value():.2f} m\n"
            f"Giới tính: {gender}\n"
            f"Ngày sinh: {birthday.date().toString('dd/MM/yyyy')}\n"
            f"Sở thích: {', '.join(hobbies) if hobbies else 'Không có'}"
        )
    
        QMessageBox.information(window, "Thông tin", info)
    
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Đăng ký thành viên")
    
    main_layout = QVBoxLayout()
    
    form = QFormLayout()
    
    name = QComboBox()
    name.setEditable(True)
    name.addItems([
        "Nguyễn Văn A",
        "Trần Thị B",
        "Lê Văn C",
    ])
    
    age = QSpinBox()
    age.setRange(1, 120)
    age.setValue(20)
    age.setSuffix(" tuổi")
    
    height = QDoubleSpinBox()
    height.setRange(0.5, 2.5)
    height.setDecimals(2)
    height.setSingleStep(0.01)
    height.setValue(1.70)
    height.setSuffix(" m")
    
    birthday = QDateEdit()
    birthday.setCalendarPopup(True)
    birthday.setDate(QDate.currentDate())
    birthday.setDisplayFormat("dd/MM/yyyy")
    
    male = QRadioButton("Nam")
    female = QRadioButton("Nữ")
    male.setChecked(True)
    
    gender_group = QButtonGroup()
    gender_group.addButton(male)
    gender_group.addButton(female)
    
    gender_layout = QHBoxLayout()
    gender_layout.addWidget(male)
    gender_layout.addWidget(female)
    
    hobby_read = QCheckBox("Đọc sách")
    hobby_music = QCheckBox("Âm nhạc")
    hobby_sport = QCheckBox("Thể thao")
    
    hobby_layout = QHBoxLayout()
    hobby_layout.addWidget(hobby_read)
    hobby_layout.addWidget(hobby_music)
    hobby_layout.addWidget(hobby_sport)
    
    form.addRow("Họ tên:", name)
    form.addRow("Tuổi:", age)
    form.addRow("Chiều cao:", height)
    form.addRow("Ngày sinh:", birthday)
    form.addRow("Giới tính:", gender_layout)
    form.addRow("Sở thích:", hobby_layout)
    
    button_layout = QHBoxLayout()
    
    save_button = QPushButton("Lưu")
    exit_button = QPushButton("Thoát")
    
    save_button.clicked.connect(save)
    exit_button.clicked.connect(window.close)
    
    button_layout.addStretch()
    button_layout.addWidget(save_button)
    button_layout.addWidget(exit_button)
    
    main_layout.addLayout(form)
    main_layout.addLayout(button_layout)
    
    window.setLayout(main_layout)
    window.resize(600, 320)
    window.show()
    
    app.exec()

* * *

# 13\. Signal thường dùng

Widget| Signal| Ý nghĩa  
---|---|---  
`QSpinBox`| `valueChanged(int)`| Giá trị thay đổi  
`QDoubleSpinBox`| `valueChanged(float)`| Giá trị thay đổi  
`QComboBox`| `currentIndexChanged(int)`| Thay đổi mục chọn  
`QComboBox`| `currentTextChanged(str)`| Thay đổi nội dung  
`QCheckBox`| `toggled(bool)`| Đánh dấu/Bỏ đánh dấu  
`QRadioButton`| `toggled(bool)`| Chuyển trạng thái  
`QSlider`| `valueChanged(int)`| Thanh kéo thay đổi  
`QDateEdit`| `dateChanged(QDate)`| Ngày thay đổi  
`QTimeEdit`| `timeChanged(QTime)`| Giờ thay đổi  
  
* * *

# 14\. Những lỗi người mới thường gặp

### 1\. Dùng `text()` với `QSpinBox`

Sai:
    
    
    age.text()

Đúng:
    
    
    age.value()

* * *

### 2\. Dùng `value()` với `QLineEdit`

Sai:
    
    
    name.value()

Đúng:
    
    
    name.text()

* * *

### 3\. Quên `setCalendarPopup(True)`

Nếu không bật, người dùng phải nhập ngày thủ công, dễ sai định dạng.

* * *

### 4\. Không nhóm các `QRadioButton`

Nếu các `QRadioButton` nằm ở những container khác nhau và không dùng `QButtonGroup`, có thể xảy ra tình trạng chọn được nhiều nút cùng lúc.

* * *

# 15\. Bảng ghi nhớ

Widget| Dùng để  
---|---  
`QSpinBox`| Nhập số nguyên  
`QDoubleSpinBox`| Nhập số thực  
`QComboBox`| Chọn một giá trị từ danh sách  
`QCheckBox`| Chọn nhiều tùy chọn độc lập  
`QRadioButton`| Chọn một trong nhiều tùy chọn  
`QSlider`| Điều chỉnh giá trị bằng thanh kéo  
`QDateEdit`| Chọn ngày  
`QTimeEdit`| Chọn giờ  
`QDateTimeEdit`| Chọn ngày và giờ  
  
* * *

# Bài tập thực hành

## Bài 1: Máy tính BMI

Thiết kế giao diện gồm:

  * Họ tên (`QLineEdit`) 
  * Chiều cao (`QDoubleSpinBox`) 
  * Cân nặng (`QDoubleSpinBox`) 
  * Nút **Tính BMI**



Yêu cầu:

  * Tính BMI = cân nặng / (chiều cao²). 
  * Hiển thị kết quả bằng `QMessageBox`. 



* * *

## Bài 2: Đăng ký khóa học

Sử dụng:

  * `QComboBox` chọn khóa học. 
  * `QRadioButton` chọn ca học (Sáng/Chiều/Tối). 
  * `QCheckBox` chọn hình thức học (Online, Offline). 
  * `QDateEdit` chọn ngày bắt đầu. 



Khi nhấn **Đăng ký** , hiển thị toàn bộ thông tin.

* * *

## Bài 3: Điều chỉnh âm lượng

  * `QSlider` từ 0 đến 100. 
  * `QLabel` hiển thị giá trị hiện tại. 
  * Mỗi khi kéo thanh trượt, `QLabel` cập nhật ngay giá trị mới bằng signal `valueChanged`. 



* * *

# Mini Project cuối buổi: Hồ sơ nhân viên

Hãy xây dựng giao diện quản lý hồ sơ nhân viên với các trường:

  * Họ tên (`QLineEdit`) 
  * Tuổi (`QSpinBox`) 
  * Mức lương (`QDoubleSpinBox`) 
  * Phòng ban (`QComboBox`) 
  * Giới tính (`QRadioButton`) 
  * Kỹ năng (`QCheckBox`) 
  * Ngày vào làm (`QDateEdit`) 
  * Nút **Lưu** và **Thoát**



Yêu cầu:

  * Kiểm tra dữ liệu trước khi lưu. 
  * Hiển thị toàn bộ thông tin bằng `QMessageBox`. 
  * Bố cục gọn gàng bằng `QFormLayout` kết hợp `QHBoxLayout`. 



* * *

## Tổng kết Buổi 4

Bạn đã làm quen với nhóm widget nhập liệu nâng cao và biết cách chọn widget phù hợp cho từng loại dữ liệu. Đây là nền tảng quan trọng để xây dựng các phần mềm quản lý thực tế.

**Buổi 5** sẽ tập trung vào các **Dialog** trong PySide6:

  * `QMessageBox`
  * `QFileDialog`
  * `QColorDialog`
  * `QFontDialog`
  * `QInputDialog`



và xây dựng một ứng dụng **Notepad** có thể mở, lưu tệp văn bản và thay đổi font, màu chữ thông qua các hộp thoại chuẩn của hệ điều hành. Đây sẽ là bước đầu tiên để tạo ra một ứng dụng desktop hoàn chỉnh.

