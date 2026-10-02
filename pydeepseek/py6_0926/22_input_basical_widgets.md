# 📘 MODULE 2 – BÀI 2.2: CÁC WIDGET NHẬP LIỆU CƠ BẢN

> **Mục tiêu bài học**:
> - Nắm vững 8 widget nhập liệu phổ biến nhất
> - Hiểu signal đặc trưng của từng widget
> - Biết cách đọc/ghi dữ liệu từ widget
> - Xây dựng **Form đăng ký** hoàn chỉnh có validation

---

## 🎯 PHẦN 1: TỔNG QUAN CÁC WIDGET NHẬP LIỆU

### 1.1. Phân loại theo mục đích

| Nhóm | Widget | Mục đích |
|------|--------|----------|
| **Text input** | `QLineEdit`, `QTextEdit`, `QPlainTextEdit` | Nhập chữ |
| **Button** | `QPushButton`, `QToolButton`, `QCheckBox`, `QRadioButton` | Bấm / chọn |
| **Selection** | `QComboBox`, `QListWidget`, `QSpinBox`, `QDoubleSpinBox`, `QSlider` | Chọn giá trị |
| **Date/Time** | `QDateEdit`, `QTimeEdit`, `QDateTimeEdit` | Chọn ngày giờ |
| **Range** | `QSlider`, `QScrollBar`, `QDial`, `QProgressBar` | Chọn trong khoảng |

### 1.2. Cấu trúc chung mỗi widget

Mọi widget đều có:
- **Properties**: đọc/ghi bằng `setXxx()` / `xxx()`
- **Signals**: sự kiện phát ra (`clicked`, `textChanged`...)
- **Methods**: hành động (`clear()`, `setFocus()`...)

💡 **Nguyên tắc vàng**: Khi học widget mới, tự hỏi 3 câu:
1. **Properties** nào? (lấy/đặt giá trị)
2. **Signals** nào quan trọng? (khi nào phát ra)
3. **Methods** đặc trưng nào? (làm gì được)

---

## 🎯 PHẦN 2: QPUSHBUTTON – NÚT BẤM

### 2.1. Tạo và dùng

```python
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon

btn = QPushButton("Click me")           # Cách 1
btn = QPushButton()                     # Cách 2
btn.setText("Click me")

btn = QPushButton(QIcon("save.png"), "Save")  # Có icon
```

### 2.2. Signals quan trọng

| Signal | Khi nào phát |
|--------|--------------|
| `clicked` | Click chuột hoặc Space khi focus |
| `pressed` | Chuột vừa nhấn xuống |
| `released` | Chuột nhả ra |
| `toggled(bool)` | Chỉ khi `setCheckable(True)` |
| `clicked(bool)` | Có tham số check state nếu checkable |

```python
btn.clicked.connect(lambda: print("Đã bấm"))
btn.clicked.connect(self.on_click)      # Method
```

### 2.3. Checkable Button

```python
btn = QPushButton("Bật/Tắt đèn")
btn.setCheckable(True)
btn.toggled.connect(lambda checked: print("Đèn:", "BẬT" if checked else "TẮT"))
```

### 2.4. Properties thường dùng

```python
btn.setEnabled(False)                    # Vô hiệu hóa
btn.setCheckable(True)                   # Có thể check
btn.setChecked(True)                     # Đang checked
btn.setDefault(True)                     # Nút mặc định (Enter)
btn.setFlat(True)                        # Kiểu phẳng
btn.setIcon(QIcon("icon.png"))
btn.setIconSize(QSize(24, 24))
btn.setShortcut("Ctrl+S")                # Phím tắt riêng cho nút
btn.setToolTip("Lưu file")
```

---

## 🎯 PHẦN 3: QLINEEDIT – Ô NHẬP MỘT DÒNG

### 3.1. Cơ bản

```python
from PySide6.QtWidgets import QLineEdit

edit = QLineEdit()
edit.setText("Hello")
text = edit.text()                       # Lấy giá trị
edit.clear()
```

### 3.2. Signals quan trọng

| Signal | Khi nào phát | Dùng khi |
|--------|--------------|----------|
| `textChanged(str)` | Mỗi khi text đổi (kể cả code) | Validate real-time |
| `textEdited(str)` | Chỉ khi user gõ | Tránh vòng lặp |
| `returnPressed()` | User nhấn Enter | Submit form |
| `editingFinished()` | Mất focus hoặc Enter | Validate khi hoàn thành |
| `selectionChanged()` | Đổi vùng chọn | Ít dùng |

💡 **Phân biệt `textChanged` vs `textEdited`**:
- `textChanged`: phát ra khi text thay đổi **bằng bất kỳ cách nào** (gõ, `setText()`, paste...)
- `textEdited`: **chỉ** khi user gõ → tránh vòng lặp vô hạn khi bạn set text trong slot

### 3.3. Validation & ràng buộc

```python
edit.setMaxLength(50)                    # Tối đa 50 ký tự
edit.setPlaceholderText("Nhập tên...")   # Chữ mờ gợi ý
edit.setReadOnly(True)                   # Chỉ đọc
edit.setEchoMode(QLineEdit.EchoMode.Password)   # Ẩn ký tự

# Echo modes:
# Normal        - hiện bình thường
# NoEcho        - không hiện gì
# Password      - hiện dấu ●
# PasswordEchoOnEdit - hiện khi gõ, ẩn khi mất focus
```

### 3.4. Dùng QRegularExpressionValidator (validate)

```python
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# Chỉ cho nhập số
regex = QRegularExpression(r"^\d+$")
validator = QRegularExpressionValidator(regex)
edit.setValidator(validator)

# Email
email_regex = QRegularExpression(r"^[\w\.-]+@[\w\.-]+\.\w+$")
edit.setValidator(QRegularExpressionValidator(email_regex))
```

### 3.5. Input Mask (định dạng cứng)

```python
# Số điện thoại VN: 090-123-4567
edit.setInputMask("000-000-0000;_")

# Ngày: 12/31/2025
edit.setInputMask("99/99/9999")

# Mã sản phẩm: AB-12345
edit.setInputMask(">AA-99999")
```

Ký hiệu mask:
- `9` – chữ số 0-9
- `0` – chữ số bắt buộc
- `A` – chữ cái (không bắt buộc)
- `a` – chữ cái (không bắt buộc, cho phép trống)
- `>` – chữ hoa
- `<` – chữ thường

---

## 🎯 PHẦN 4: QTEXTEDIT & QPLAINEDIT – Ô NHẬP NHIỀU DÒNG

### 4.1. So sánh QTextEdit vs QPlainTextEdit

| Tiêu chí | QTextEdit | QPlainTextEdit |
|----------|-----------|----------------|
| Rich text (HTML, màu) | ✅ | ❌ |
| Hiệu năng với text lớn | Chậm hơn | **Nhanh hơn** |
| Định dạng phức tạp | ✅ | ❌ |
| Dùng cho | Editor có định dạng | Log, code editor, plain text |

👉 **Quy tắc**: Cần định dạng → `QTextEdit`. Cần hiệu năng/plain → `QPlainTextEdit`.

### 4.2. QTextEdit

```python
from PySide6.QtWidgets import QTextEdit

editor = QTextEdit()
editor.setPlainText("Văn bản thuần")
editor.setHtml("<h1>Tiêu đề</h1><p>Đoạn <b>đậm</b></p>")

text = editor.toPlainText()              # Lấy text thuần
html = editor.toHtml()                   # Lấy HTML

# Định dạng
editor.setFontPointSize(14)
editor.setTextColor(QColor("red"))
editor.setFontWeight(QFont.Weight.Bold)
```

### 4.3. Signals

| Signal | Khi nào |
|--------|---------|
| `textChanged()` | Text đổi |
| `selectionChanged()` | Vùng chọn đổi |
| `cursorPositionChanged()` | Con trỏ di chuyển |
| `copyAvailable(bool)` | Có/không có gì để copy |

### 4.4. QPlainTextEdit – dùng cho log

```python
from PySide6.QtWidgets import QPlainTextEdit

log = QPlainTextEdit()
log.setReadOnly(True)
log.setMaximumBlockCount(1000)           # Chỉ giữ 1000 dòng cuối

# Thêm dòng (nhanh)
log.appendPlainText("2025-01-01 INFO: Khởi động")

# Auto scroll xuống cuối
log.verticalScrollBar().setValue(log.verticalScrollBar().maximum())
```

---

## 🎯 PHẦN 5: QCHECKBOX – HỘP KIỂM

### 5.1. Cơ bản

```python
from PySide6.QtWidgets import QCheckBox

chk = QCheckBox("Tôi đồng ý điều khoản")
chk.setChecked(True)                     # Đặt trạng thái
state = chk.isChecked()                  # Đọc trạng thái
```

### 5.2. Signals

```python
chk.toggled.connect(lambda checked: print("Checked:", checked))
chk.stateChanged.connect(self.on_state)  # int: 0=Unchecked, 2=Checked
```

### 5.3. Ba trạng thái (Tristate)

```python
chk = QCheckBox("Chọn tất cả")
chk.setTristate(True)
chk.setCheckState(Qt.CheckState.PartiallyChecked)   # Trạng thái trung gian
```

Trạng thái:
- `Qt.CheckState.Unchecked` (0)
- `Qt.CheckState.PartiallyChecked` (1)
- `Qt.CheckState.Checked` (2)

### 5.4. Nhóm checkbox với QButtonGroup

```python
from PySide6.QtWidgets import QButtonGroup

group = QButtonGroup()
group.addButton(chk1, id=1)
group.addButton(chk2, id=2)
group.buttonClicked.connect(self.on_group_click)
```

---

## 🎯 PHẦN 6: QRADIOBUTTON – NÚT CHỌN MỘT

### 6.1. Đặc điểm

- Chỉ **một** trong nhóm được chọn
- **Khác QCheckBox**: khi bấm lại không tự bỏ chọn
- Cùng parent → cùng nhóm

### 6.2. Ví dụ

```python
from PySide6.QtWidgets import QRadioButton, QButtonGroup, QVBoxLayout, QWidget

w = QWidget()
layout = QVBoxLayout(w)

# Cùng parent → tự động cùng nhóm
rb_nam = QRadioButton("Nam")
rb_nu = QRadioButton("Nữ")
rb_khac = QRadioButton("Khác")

layout.addWidget(rb_nam)
layout.addWidget(rb_nu)
layout.addWidget(rb_khac)

rb_nam.setChecked(True)                  # Mặc định

rb_nam.toggled.connect(self.on_gender_change)
```

### 6.3. Dùng QButtonGroup để quản lý

```python
group = QButtonGroup(w)
group.addButton(rb_nam, 1)
group.addButton(rb_nu, 2)
group.addButton(rb_khac, 3)

# Lấy ID được chọn
selected_id = group.checkedId()

# Signal
group.buttonToggled.connect(lambda btn, checked: print(btn.text(), checked))
```

---

## 🎯 PHẦN 7: QCOMBOBOX – DROPDOWN

### 7.1. Cơ bản

```python
from PySide6.QtWidgets import QComboBox

combo = QComboBox()
combo.addItem("Hà Nội")                          # Thêm text
combo.addItem("TP.HCM", "hcm")                   # Thêm (text, data)
combo.addItems(["Đà Nẵng", "Cần Thơ"])           # Thêm nhiều

combo.insertItem(0, "Đầu tiên")                  # Chèn vị trí
combo.removeItem(0)                              # Xóa theo vị trí
combo.clear()                                    # Xóa hết
```

### 7.2. Đọc giá trị

```python
text = combo.currentText()                       # Text đang chọn
data = combo.currentData()                       # Data ẩn (nếu có)
index = combo.currentIndex()                     # Vị trí (0, 1, 2...)

# Theo index
text2 = combo.itemText(2)
data2 = combo.itemData(2)
count = combo.count()
```

### 7.3. Signals

| Signal | Khi nào |
|--------|---------|
| `currentIndexChanged(int)` | Index đổi |
| `currentTextChanged(str)` | Text đổi |
| `activated(int)` | User chọn (không bị trigger bởi code) |
| `highlighted(int)` | Hover item |

### 7.4. Editable ComboBox

```python
combo.setEditable(True)                          # Cho nhập
combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)
combo.setDuplicatesEnabled(False)

# Khi user gõ text mới và Enter
combo.lineEdit().returnPressed.connect(self.on_custom_input)
```

### 7.5. ComboBox với icon

```python
from PySide6.QtGui import QIcon
combo.addItem(QIcon("vn.png"), "Việt Nam")
```

---

## 🎯 PHẦN 8: QSPINBOX & QDOUBLESPINBOX

### 8.1. QSpinBox – nhập số nguyên

```python
from PySide6.QtWidgets import QSpinBox

spin = QSpinBox()
spin.setRange(0, 100)                            # Giới hạn [0, 100]
spin.setValue(50)                                # Giá trị hiện tại
spin.setSingleStep(5)                            # Mỗi lần +/- là 5
spin.setSuffix(" tuổi")                          # "50 tuổi"
spin.setPrefix("$ ")                             # "$ 50"
spin.setWrapping(True)                           # Vượt max → về min

value = spin.value()                             # Lấy giá trị
```

### 8.2. QDoubleSpinBox – nhập số thực

```python
from PySide6.QtWidgets import QDoubleSpinBox

spin = QDoubleSpinBox()
spin.setRange(0.0, 1.0)
spin.setDecimals(2)                              # 2 chữ số sau dấu phẩy
spin.setSingleStep(0.1)
spin.setValue(0.75)

value = spin.value()                             # float
```

### 8.3. Signals

```python
spin.valueChanged.connect(lambda v: print("Value:", v))
spin.textChanged.connect(lambda s: print("Text:", s))   # Khi text đổi
```

---

## 🎯 PHẦN 9: QSLIDER – THANH TRƯỢT

### 9.1. Cơ bản

```python
from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

slider = QSlider(Qt.Orientation.Horizontal)      # Hoặc Vertical
slider.setRange(0, 100)
slider.setValue(50)
slider.setSingleStep(1)                          # Mỗi lần mũi tên
slider.setPageStep(10)                           # Mỗi lần Page Up/Down

value = slider.value()
```

### 9.2. Signals

```python
slider.valueChanged.connect(lambda v: print(v))          # Liên tục khi kéo
slider.sliderMoved.connect(lambda v: print(v))           # Chỉ khi user kéo
slider.sliderPressed.connect(...)                        # Vừa nhấn
slider.sliderReleased.connect(...)                       # Vừa nhả
slider.actionTriggered.connect(...)                      # Chi tiết hành động
```

💡 **Khác biệt**:
- `valueChanged`: phát ra cả khi gọi `setValue()` từ code
- `sliderMoved`: **chỉ** khi user kéo chuột

### 9.3. Kết hợp với QSpinBox

```python
from PySide6.QtWidgets import QSpinBox, QSlider, QHBoxLayout

slider = QSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 100)

spin = QSpinBox()
spin.setRange(0, 100)

# Đồng bộ 2 chiều
slider.valueChanged.connect(spin.setValue)
spin.valueChanged.connect(slider.setValue)
```

---

## 🎯 PHẦN 10: QDATETIMEEDIT – NGÀY GIỜ

### 10.1. Các loại

```python
from PySide6.QtWidgets import QDateEdit, QTimeEdit, QDateTimeEdit
from PySide6.QtCore import QDate, QTime, QDateTime

date_edit = QDateEdit()
date_edit.setDate(QDate.currentDate())
date_edit.setCalendarPopup(True)                 # Hiện popup lịch
date_edit.setDisplayFormat("dd/MM/yyyy")

time_edit = QTimeEdit()
time_edit.setTime(QTime.currentTime())
time_edit.setDisplayFormat("HH:mm:ss")

datetime_edit = QDateTimeEdit()
datetime_edit.setDateTime(QDateTime.currentDateTime())
datetime_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
```

### 10.2. Signals

```python
date_edit.dateChanged.connect(lambda d: print("Ngày:", d.toString()))
time_edit.timeChanged.connect(lambda t: print("Giờ:", t.toString()))
datetime_edit.dateTimeChanged.connect(lambda dt: print(dt.toString()))
```

### 10.3. Giới hạn

```python
date_edit.setMinimumDate(QDate(2000, 1, 1))
date_edit.setMaximumDate(QDate.currentDate())
```

---

## 🎯 PHẦN 11: THỰC HÀNH – FORM ĐĂNG KÝ HOÀN CHỈNH

Chúng ta sẽ build app "Form đăng ký" với đầy đủ validation.

### 11.1. Yêu cầu

**Các field**:
- Họ tên (QLineEdit)
- Email (QLineEdit + validation regex)
- Số điện thoại (QLineEdit + input mask)
- Ngày sinh (QDateEdit)
- Giới tính (QRadioButton: Nam/Nữ/Khác)
- Sở thích (QCheckBox: Đọc sách, Du lịch, Thể thao)
- Nghề nghiệp (QComboBox)
- Kinh nghiệm (QSpinBox năm)
- Mức lương mong muốn (QSlider + label)
- Ghi chú (QTextEdit)

**Nút**:
- Đăng ký (validate trước khi submit)
- Xóa form

**Validation**:
- Họ tên: không rỗng, ít nhất 2 ký tự
- Email: đúng format
- SĐT: đủ 10-11 số
- Ít nhất 1 sở thích
- Nếu lỗi → highlight đỏ field + QMessageBox

### 11.2. Code đầy đủ

Tạo file `registration_form.py`:

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QLineEdit,
    QTextEdit, QPushButton, QCheckBox, QRadioButton, QComboBox,
    QSpinBox, QSlider, QDateEdit, QFormLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QButtonGroup, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class RegistrationForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Đăng Ký")
        self.resize(600, 750)
        
        # Central widget với scroll để chứa form dài
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        container = QWidget()
        scroll.setWidget(container)
        
        # ===== Layout chính =====
        main_layout = QVBoxLayout(container)
        
        # --- Nhóm 1: Thông tin cá nhân ---
        main_layout.addWidget(self._create_personal_group())
        
        # --- Nhóm 2: Thông tin công việc ---
        main_layout.addWidget(self._create_job_group())
        
        # --- Nhóm 3: Ghi chú ---
        main_layout.addWidget(self._create_note_group())
        
        # --- Nút hành động ---
        main_layout.addLayout(self._create_buttons())
        main_layout.addStretch()
        
        self.statusBar().showMessage("Điền đầy đủ thông tin và nhấn Đăng ký")
    
    # ----------------------------------------------------------------
    # NHÓM 1: THÔNG TIN CÁ NHÂN
    # ----------------------------------------------------------------
    def _create_personal_group(self) -> QGroupBox:
        group = QGroupBox("Thông tin cá nhân")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        
        # Họ tên
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nguyễn Văn A")
        self.txt_name.setMaxLength(100)
        form.addRow("Họ tên *:", self.txt_name)
        
        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("example@email.com")
        email_regex = QRegularExpression(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        self.txt_email.setValidator(QRegularExpressionValidator(email_regex))
        form.addRow("Email *:", self.txt_email)
        
        # Số điện thoại
        self.txt_phone = QLineEdit()
        self.txt_phone.setInputMask("000-000-0000;_")
        self.txt_phone.setPlaceholderText("090-123-4567")
        form.addRow("SĐT *:", self.txt_phone)
        
        # Ngày sinh
        self.date_birth = QDateEdit()
        self.date_birth.setCalendarPopup(True)
        self.date_birth.setDisplayFormat("dd/MM/yyyy")
        self.date_birth.setDate(QDate(2000, 1, 1))
        self.date_birth.setMaximumDate(QDate.currentDate())
        self.date_birth.setMinimumDate(QDate(1900, 1, 1))
        form.addRow("Ngày sinh:", self.date_birth)
        
        # Giới tính
        gender_widget = QWidget()
        gender_layout = QHBoxLayout(gender_widget)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        
        self.rb_male = QRadioButton("Nam")
        self.rb_female = QRadioButton("Nữ")
        self.rb_other = QRadioButton("Khác")
        self.rb_male.setChecked(True)
        
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.rb_male, 1)
        self.gender_group.addButton(self.rb_female, 2)
        self.gender_group.addButton(self.rb_other, 3)
        
        gender_layout.addWidget(self.rb_male)
        gender_layout.addWidget(self.rb_female)
        gender_layout.addWidget(self.rb_other)
        gender_layout.addStretch()
        form.addRow("Giới tính:", gender_widget)
        
        # Sở thích
        hobby_widget = QWidget()
        hobby_layout = QHBoxLayout(hobby_widget)
        hobby_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chk_reading = QCheckBox("Đọc sách")
        self.chk_travel = QCheckBox("Du lịch")
        self.chk_sport = QCheckBox("Thể thao")
        self.chk_music = QCheckBox("Âm nhạc")
        
        for chk in (self.chk_reading, self.chk_travel, self.chk_sport, self.chk_music):
            hobby_layout.addWidget(chk)
        hobby_layout.addStretch()
        form.addRow("Sở thích *:", hobby_widget)
        
        return group
    
    # ----------------------------------------------------------------
    # NHÓM 2: THÔNG TIN CÔNG VIỆC
    # ----------------------------------------------------------------
    def _create_job_group(self) -> QGroupBox:
        group = QGroupBox("Thông tin công việc")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        
        # Nghề nghiệp
        self.cbo_job = QComboBox()
        self.cbo_job.addItem("-- Chọn nghề nghiệp --", None)
        self.cbo_job.addItem("Lập trình viên", "dev")
        self.cbo_job.addItem("Thiết kế đồ họa", "designer")
        self.cbo_job.addItem("Quản lý dự án", "pm")
        self.cbo_job.addItem("Kinh doanh", "sales")
        self.cbo_job.addItem("Khác", "other")
        form.addRow("Nghề nghiệp:", self.cbo_job)
        
        # Kinh nghiệm
        self.spin_exp = QSpinBox()
        self.spin_exp.setRange(0, 50)
        self.spin_exp.setSuffix(" năm")
        self.spin_exp.setValue(0)
        form.addRow("Kinh nghiệm:", self.spin_exp)
        
        # Mức lương (Slider)
        salary_widget = QWidget()
        salary_layout = QHBoxLayout(salary_widget)
        salary_layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider_salary = QSlider(Qt.Orientation.Horizontal)
        self.slider_salary.setRange(5, 100)          # 5 - 100 triệu
        self.slider_salary.setValue(15)
        self.slider_salary.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_salary.setTickInterval(10)
        
        self.lbl_salary = QLabel("15 triệu")
        self.lbl_salary.setMinimumWidth(90)
        self.lbl_salary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.slider_salary.valueChanged.connect(self._on_salary_changed)
        
        salary_layout.addWidget(self.slider_salary, 1)
        salary_layout.addWidget(self.lbl_salary)
        form.addRow("Lương mong muốn:", salary_widget)
        
        return group
    
    # ----------------------------------------------------------------
    # NHÓM 3: GHI CHÚ
    # ----------------------------------------------------------------
    def _create_note_group(self) -> QGroupBox:
        group = QGroupBox("Ghi chú")
        layout = QVBoxLayout(group)
        
        self.txt_note = QTextEdit()
        self.txt_note.setPlaceholderText("Thông tin thêm (không bắt buộc)...")
        self.txt_note.setMaximumHeight(100)
        layout.addWidget(self.txt_note)
        
        return group
    
    # ----------------------------------------------------------------
    # NÚT HÀNH ĐỘNG
    # ----------------------------------------------------------------
    def _create_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.btn_reset = QPushButton("Xóa form")
        self.btn_reset.clicked.connect(self.reset_form)
        
        self.btn_submit = QPushButton("Đăng ký")
        self.btn_submit.setDefault(True)
        self.btn_submit.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "padding: 8px 20px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.btn_submit.clicked.connect(self.submit_form)
        
        layout.addWidget(self.btn_reset)
        layout.addWidget(self.btn_submit)
        return layout
    
    # ----------------------------------------------------------------
    # XỬ LÝ
    # ----------------------------------------------------------------
    def _on_salary_changed(self, value: int):
        self.lbl_salary.setText(f"{value} triệu")
    
    def _mark_error(self, widget, has_error: bool):
        """Đổi viền đỏ nếu lỗi."""
        if has_error:
            widget.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        else:
            widget.setStyleSheet("")
    
    def _get_selected_hobbies(self) -> list[str]:
        hobbies = []
        for chk in (self.chk_reading, self.chk_travel, self.chk_sport, self.chk_music):
            if chk.isChecked():
                hobbies.append(chk.text())
        return hobbies
    
    def validate(self) -> tuple[bool, str]:
        """Trả về (hợp_lệ, thông_báo_lỗi)."""
        # Reset highlight
        for w in (self.txt_name, self.txt_email, self.txt_phone):
            self._mark_error(w, False)
        
        # Họ tên
        name = self.txt_name.text().strip()
        if len(name) < 2:
            self._mark_error(self.txt_name, True)
            return False, "Họ tên phải có ít nhất 2 ký tự."
        
        # Email
        email = self.txt_email.text().strip()
        if not email or "@" not in email:
            self._mark_error(self.txt_email, True)
            return False, "Email không hợp lệ."
        
        # SĐT (mask đã đảm bảo format, nhưng kiểm tra có nhập hay không)
        phone = self.txt_phone.text()
        if phone.replace("-", "").replace("_", "").strip() == "":
            self._mark_error(self.txt_phone, True)
            return False, "Vui lòng nhập số điện thoại."
        
        # Sở thích
        if not self._get_selected_hobbies():
            return False, "Vui lòng chọn ít nhất một sở thích."
        
        return True, ""
    
    def submit_form(self):
        ok, msg = self.validate()
        if not ok:
            QMessageBox.warning(self, "Lỗi nhập liệu", msg)
            return
        
        # Thu thập dữ liệu
        data = {
            "Họ tên": self.txt_name.text().strip(),
            "Email": self.txt_email.text().strip(),
            "SĐT": self.txt_phone.text(),
            "Ngày sinh": self.date_birth.date().toString("dd/MM/yyyy"),
            "Giới tính": self.gender_group.checkedButton().text(),
            "Sở thích": ", ".join(self._get_selected_hobbies()),
            "Nghề nghiệp": self.cbo_job.currentText(),
            "Kinh nghiệm": f"{self.spin_exp.value()} năm",
            "Lương mong muốn": f"{self.slider_salary.value()} triệu",
            "Ghi chú": self.txt_note.toPlainText().strip() or "(trống)",
        }
        
        # Hiển thị kết quả
        info = "\n".join(f"• {k}: {v}" for k, v in data.items())
        QMessageBox.information(self, "Đăng ký thành công", info)
        self.statusBar().showMessage("Đã đăng ký thành công!", 5000)
    
    def reset_form(self):
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa toàn bộ form?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.txt_name.clear()
        self.txt_email.clear()
        self.txt_phone.clear()
        self.date_birth.setDate(QDate(2000, 1, 1))
        self.rb_male.setChecked(True)
        for chk in (self.chk_reading, self.chk_travel, self.chk_sport, self.chk_music):
            chk.setChecked(False)
        self.cbo_job.setCurrentIndex(0)
        self.spin_exp.setValue(0)
        self.slider_salary.setValue(15)
        self.txt_note.clear()
        
        # Reset highlight
        for w in (self.txt_name, self.txt_email, self.txt_phone):
            self._mark_error(w, False)
        
        self.statusBar().showMessage("Đã xóa form", 2000)


def main():
    app = QApplication(sys.argv)
    form = RegistrationForm()
    form.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 11.3. Điểm đáng chú ý

1. **QScrollArea**: cho phép cuộn khi form dài
2. **QGroupBox**: nhóm các field liên quan, có viền + title
3. **QFormLayout**: tự động căn label + widget
4. **QButtonGroup**: gom radio lại để lấy `checkedButton()`
5. **Validator regex**: chặn ngay từ lúc gõ, không cho nhập ký tự sai
6. **Input mask**: định dạng SĐT cứng ngay khi gõ
7. **`_mark_error`**: dùng QSS động để highlight đỏ
8. **`validate()` trả tuple**: pattern hay, tách logic khỏi UI
9. **`setDefault(True)` trên submit**: nhấn Enter ở bất kỳ field nào → submit
10. **Reset form có confirm**: tránh mất dữ liệu do vô tình

---

## 📝 BÀI TẬP

### Bài tập 2.2.1 (Cơ bản)
Thêm field **"Xác nhận mật khẩu"** vào form đăng ký:
- Hai QLineEdit dùng `EchoMode.Password`
- Validate 2 field phải khớp
- Có nút con mắt 👁 để hiện/ẩn mật khẩu

💡 Gợi ý: Toggle `setEchoMode(Normal/Password)`.

### Bài tập 2.2.2 (Trung bình)
Thay QSlider lương bằng combo **QSpinBox + QSlider** đồng bộ 2 chiều:
- Slider kéo → SpinBox cập nhật
- SpinBox nhập → Slider cập nhật
- Thêm label hiển thị "X triệu Y nghìn"

### Bài tập 2.2.3 (Khá)
Thêm một **ComboBox Tỉnh/Thành** và **ComboBox Quận/Huyện**:
- Khi chọn tỉnh → quận combo load lại theo tỉnh đó
- Dùng `currentIndexChanged` để cascade

💡 Gợi ý: Dùng dict `{"Hà Nội": ["Ba Đình", "Hoàn Kiếm"], ...}`.

### Bài tập 2.2.4 (Nâng cao)
Viết **real-time validation**:
- Khi user gõ email → hiện dấu ✓ xanh nếu đúng, ✗ đỏ nếu sai
- Không cần đợi nhấn Đăng ký
- Dùng `textChanged` + icon trong `QLineEdit.addAction()`

💡 Gợi ý: `QLineEdit.addAction(QIcon(...), QLineEdit.ActionPosition.TrailingPosition)`.

### Bài tập 2.2.5 (Khó)
Thêm **nút "Lưu nháp"** và **"Tải nháp"** dùng `QSettings`:
- Lưu toàn bộ giá trị form vào QSettings
- Khi mở app, tự động load lại

---

## ✅ CHECKLIST SAU BÀI 2.2

- [ ] Biết 8 widget nhập liệu phổ biến
- [ ] Hiểu sự khác biệt `QLineEdit` vs `QTextEdit` vs `QPlainTextEdit`
- [ ] Phân biệt `QCheckBox` vs `QRadioButton` (nhiều chọn vs 1 chọn)
- [ ] Biết `QButtonGroup` để quản lý nhóm radio/checkbox
- [ ] Thành thạo `QComboBox` (text/data, editable)
- [ ] Biết `QSpinBox`, `QDoubleSpinBox`, `QSlider` và cách đồng bộ
- [ ] Biết `QDateEdit` với calendar popup
- [ ] Hiểu `Validator` và `InputMask`
- [ ] Phân biệt `textChanged` vs `textEdited`
- [ ] Hoàn thành Form đăng ký + ít nhất 2 bài tập

---

## 🔜 BÀI TIẾP THEO

**Bài 2.3 – Layout Management chi tiết**

- `QVBoxLayout`, `QHBoxLayout` – ôn kỹ
- `QGridLayout` – lưới tọa độ
- `QFormLayout` – chuyên cho form
- `QStackedLayout` – nhiều trang
- `QSplitter` – chia đôi kéo được
- **Stretch factor, spacing, margin, size policy**
- Build app **"Máy tính bỏ túi"** với QGridLayout

---

👉 Bạn muốn:
1. **Soạn tiếp Bài 2.3 (Layout)**?
2. **Giải chi tiết một bài tập 2.2.x** nào để đối chiếu?
3. **Đào sâu** widget nào bạn còn lăn tăn (ví dụ: ComboBox editable, QSlider với QSpinBox)?