Đúng. Theo roadmap bạn vừa đưa, **Buổi 7 phải là Input & Validation**, không phải Resource System như tôi vừa đề xuất. Từ đây tôi sẽ bám đúng roadmap này.

# Buổi 7 — Input & Validation

Hôm nay chúng ta học cách kiểm soát dữ liệu người dùng nhập vào.

Mục tiêu:

```text
User Input
    ↓
Validator
    ↓
Valid / Invalid
    ↓
Form Validation
    ↓
Submit
```

Đây là nền tảng cực kỳ quan trọng khi xây:

* Login
* Register
* Settings
* User management
* Database form
* CRUD application

---

# 1. Validation là gì?

Giả sử có form:

```text
┌─────────────────────────────────┐
│ Username: [_________________]   │
│ Age:      [_________________]   │
│ Email:    [_________________]   │
│                                 │
│                 [Save]          │
└─────────────────────────────────┘
```

Người dùng có thể nhập:

```text
Username: ""
Age: abc
Email: hello
```

Nhưng dữ liệu này có thể không hợp lệ.

Validation là quá trình:

```text
Input
  ↓
Kiểm tra
  ↓
Valid?
 ┌───────┴───────┐
 No              Yes
 ↓                ↓
Reject           Accept
```

---

# 2. Có hai loại validation

Đây là điểm rất quan trọng.

## Validation khi nhập

Ví dụ:

```text
Age: abc
```

Không cho phép nhập chữ.

Đây là công việc của:

```text
Validator
```

---

## Validation khi submit

Ví dụ:

```text
Username: ""
Email: ""
```

Các field có thể cho phép người dùng nhập tạm thời, nhưng khi nhấn:

```text
Save
```

thì phải kiểm tra toàn bộ form.

Đây là:

```text
Form Validation
```

Hai tầng này nên kết hợp với nhau.

---

# 3. Validator trong Qt

PySide6 cung cấp các validator:

```text
QValidator
│
├── QIntValidator
├── QDoubleValidator
└── QRegularExpressionValidator
```

Mental model:

```text
QLineEdit
    │
    └── Validator
           ↓
       User input
           ↓
      Accept / Reject
```

---

# 4. `QValidator`

Import:

```python
from PySide6.QtGui import QValidator
```

`QValidator` là class cơ sở.

Nó định nghĩa trạng thái validation.

Có ba trạng thái chính:

```text
Acceptable
Intermediate
Invalid
```

---

# 5. `Acceptable`

Dữ liệu hoàn toàn hợp lệ.

Ví dụ:

```text
Age = 25
```

Nếu validator yêu cầu:

```text
0 <= age <= 120
```

thì:

```text
25
```

là:

```text
Acceptable
```

---

# 6. `Invalid`

Dữ liệu không hợp lệ.

Ví dụ:

```text
Age = abc
```

nếu validator yêu cầu số nguyên.

Kết quả:

```text
Invalid
```

---

# 7. `Intermediate`

Đây là trạng thái rất thú vị.

Dữ liệu:

> Chưa hợp lệ hoàn toàn nhưng vẫn có thể trở thành hợp lệ nếu user tiếp tục nhập.

Ví dụ user đang nhập:

```text
-
```

hoặc:

```text
1
```

tùy validator.

Qt không nhất thiết coi nó là lỗi ngay lập tức.

Mental model:

```text
Invalid
    ↓
Không thể trở thành valid bằng việc tiếp tục nhập

Intermediate
    ↓
Có thể tiếp tục nhập để trở thành valid

Acceptable
    ↓
Đã hợp lệ
```

Đây là lý do validator hoạt động tốt với input tương tác.

---

# 8. `QIntValidator`

Dùng để giới hạn số nguyên.

```python
from PySide6.QtGui import QIntValidator
```

Ví dụ:

```python
validator = QIntValidator(0, 120)
```

Sau đó:

```python
age_edit.setValidator(validator)
```

Bây giờ:

```text
Age:
[ 25 ]
```

hợp lệ.

Nhưng:

```text
abc
```

không hợp lệ.

---

# 9. Ví dụ hoàn chỉnh

```python
import sys

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QVBoxLayout,
)


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.age_edit = QLineEdit()

        validator = QIntValidator(0, 120)

        self.age_edit.setValidator(validator)

        layout = QVBoxLayout(self)
        layout.addWidget(self.age_edit)


app = QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())
```

---

# 10. Validator không phải Form Validation

Đây là điểm cần nhớ.

Có:

```python
age_edit.setValidator(
    QIntValidator(0, 120)
)
```

không có nghĩa:

> Form của bạn đã được validation đầy đủ.

Validator chỉ kiểm soát **một input**.

Ví dụ:

```text
Username → validator
Age      → validator
Email    → validator
```

Sau đó vẫn cần:

```text
Form validation
```

---

# 11. `QDoubleValidator`

Dùng cho số thực.

```python
from PySide6.QtGui import QDoubleValidator
```

Ví dụ:

```python
validator = QDoubleValidator(
    0.0,
    100.0,
    2,
)
```

Ý nghĩa:

```text
min = 0.0
max = 100.0
decimals = 2
```

Gắn vào:

```python
price_edit.setValidator(validator)
```

---

# 12. Ví dụ

Cho phép:

```text
0
10
10.5
99.99
100
```

Không cho:

```text
abc
-10
200
```

về mặt range/format theo validator.

---

# 13. Decimal và Locale

`QDoubleValidator` có liên quan đến locale.

Ví dụ một số locale sử dụng:

```text
10,5
```

thay vì:

```text
10.5
```

Trong ứng dụng quốc tế hóa, bạn cần chú ý:

```python
validator.setLocale(...)
```

Đừng giả định mọi hệ thống đều dùng dấu `.` cho decimal.

---

# 14. `QRegularExpressionValidator`

Đây là validator mạnh nhất trong ba loại cơ bản.

Dùng:

```python
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
```

Ví dụ username:

```text
Chỉ cho phép:
a-z
A-Z
0-9
_
```

Regex:

```text
^[A-Za-z0-9_]+$
```

Code:

```python
regex = QRegularExpression(
    "^[A-Za-z0-9_]+$"
)

validator = QRegularExpressionValidator(regex)

username_edit.setValidator(validator)
```

---

# 15. Regex Validator

Ví dụ user nhập:

```text
john_123
```

→ hợp lệ.

```text
john123
```

→ hợp lệ.

```text
john-doe
```

→ không phù hợp regex trên.

```text
john doe
```

→ không phù hợp.

---

# 16. Regex không phải lúc nào cũng nên dùng

Đây là nguyên tắc quan trọng.

Không nên:

```text
Mọi validation → Regex
```

Ví dụ số tuổi:

```text
0 <= age <= 120
```

dùng:

```python
QIntValidator
```

tự nhiên hơn regex.

Giá:

```text
0.0 <= price <= 100000
```

dùng:

```python
QDoubleValidator
```

Regex phù hợp hơn với **format**.

Ví dụ:

```text
username
code
phone pattern
ID format
```

---

# 17. Ví dụ Regex cho username

```python
regex = QRegularExpression(
    "^[A-Za-z][A-Za-z0-9_]{2,19}$"
)
```

Ý nghĩa:

```text
^
[A-Za-z]
[A-Za-z0-9_]{2,19}
$
```

Tổng cộng:

```text
3 → 20 ký tự
```

và ký tự đầu tiên phải là chữ.

---

# 18. Regex cho mã sản phẩm

Ví dụ:

```text
SP-000001
```

Regex:

```text
^SP-[0-9]{6}$
```

Code:

```python
regex = QRegularExpression(
    r"^SP-[0-9]{6}$"
)

validator = QRegularExpressionValidator(regex)
```

---

# 19. Validator được gắn vào `QLineEdit`

Pattern chung:

```python
edit = QLineEdit()

validator = ...

edit.setValidator(validator)
```

Đây là architecture:

```text
QLineEdit
    │
    └── QValidator
           │
           ├── Acceptable
           ├── Intermediate
           └── Invalid
```

---

# 20. Kiểm tra trạng thái validator

Ta có thể gọi:

```python
state, _, _ = validator.validate(
    text,
    position,
)
```

Ví dụ:

```python
state, _, _ = validator.validate(
    "123",
    3,
)
```

Sau đó:

```python
if state == QValidator.State.Acceptable:
    print("Valid")
```

---

# 21. Nhưng thường không cần tự gọi `validate()`

Khi validator đã gắn:

```python
edit.setValidator(validator)
```

Qt tự sử dụng validator trong quá trình nhập.

Ta thường chỉ cần:

```text
setValidator()
```

và ở bước submit kiểm tra trạng thái/value.

---

# 22. `hasAcceptableInput()`

`QLineEdit` có method rất hữu ích:

```python
edit.hasAcceptableInput()
```

Ví dụ:

```python
if edit.hasAcceptableInput():
    print("Valid")
else:
    print("Invalid")
```

Đây là cách rất tiện khi validation form.

---

# 23. Form Validation

Bây giờ đến phần quan trọng nhất.

Giả sử form:

```text
┌─────────────────────────────────┐
│ Name:     [_________________]   │
│ Age:      [_________________]   │
│ Username: [_________________]   │
│                                 │
│                  [Save]         │
└─────────────────────────────────┘
```

Ta có:

```text
Name
 ↓
required

Age
 ↓
0–120

Username
 ↓
regex
```

Khi Save:

```text
Save
 ↓
validate_form()
 ↓
 ┌───────────────┐
 │               │
Valid          Invalid
 │               │
Save           Show error
```

---

# 24. Validation không nên chỉ dựa vào Validator

Ví dụ:

```python
age_edit.setValidator(
    QIntValidator(0, 120)
)
```

Nhưng user không nhập gì.

Empty string có thể chưa phải là điều bạn muốn coi là valid business data.

Vì vậy:

```text
Validator
    +
Business/Form validation
```

là tốt hơn.

---

# 25. Ví dụ Form Validation

```python
def validate_form(self):

    name = self.name_edit.text().strip()

    if not name:
        return False

    if not self.age_edit.hasAcceptableInput():
        return False

    if not self.username_edit.hasAcceptableInput():
        return False

    return True
```

Sau đó:

```python
def save(self):

    if not self.validate_form():
        print("Invalid form")
        return

    print("Saving...")
```

---

# 26. Hiển thị lỗi

Có thể dùng `QLabel`:

```text
Name:
[________________]

Name is required.
```

Ví dụ:

```python
self.name_error = QLabel()
```

Khi lỗi:

```python
self.name_error.setText(
    "Name is required."
)
```

Khi hợp lệ:

```python
self.name_error.clear()
```

---

# 27. Validation theo field

Một pattern tốt:

```python
def validate_name(self):
    ...

def validate_age(self):
    ...

def validate_username(self):
    ...

def validate_form(self):
    ...
```

Ví dụ:

```python
def validate_name(self):

    if not self.name_edit.text().strip():
        self.name_error.setText(
            "Name is required."
        )
        return False

    self.name_error.clear()
    return True
```

---

# 28. Validation toàn form

```python
def validate_form(self):

    valid = True

    if not self.validate_name():
        valid = False

    if not self.validate_age():
        valid = False

    if not self.validate_username():
        valid = False

    return valid
```

Điểm hay:

> Ta không dừng ở lỗi đầu tiên.

Có thể hiển thị tất cả lỗi cùng lúc.

---

# 29. UX tốt hơn

Không nên:

```text
Click Save
 ↓
"Name invalid"
 ↓
User sửa
 ↓
Click Save
 ↓
"Age invalid"
 ↓
User sửa
```

Tốt hơn:

```text
Click Save

Name:
❌ Required

Age:
❌ Must be between 0 and 120

Username:
❌ Invalid format
```

User có thể sửa toàn bộ một lần.

---

# 30. Validation realtime

Có thể validate khi user nhập.

Ví dụ:

```python
self.username_edit.textChanged.connect(
    self.validate_username
)
```

Mental model:

```text
User typing
    ↓
textChanged
    ↓
validate_username()
    ↓
update error UI
```

Đây là realtime validation.

---

# 31. Nhưng không nên validate quá aggressive

Ví dụ user đang gõ:

```text
john
```

Nếu regex yêu cầu:

```text
john@example.com
```

thì khi user mới gõ:

```text
j
```

không nên ngay lập tức làm UI đỏ chói:

```text
❌ Invalid email
```

Có thể dùng:

```text
Intermediate
```

hoặc chỉ validation đầy đủ khi:

```text
focus out
```

hoặc:

```text
Submit
```

UX tốt rất quan trọng.

---

# 32. `QLineEdit` có `editingFinished`

Signal:

```python
edit.editingFinished
```

thường xảy ra khi việc chỉnh sửa kết thúc, chẳng hạn user rời field hoặc xác nhận bằng Enter tùy ngữ cảnh.

Có thể dùng:

```python
edit.editingFinished.connect(
    self.validate_username
)
```

Đây thường là một lựa chọn tốt hơn realtime validation cho những field cần validation khi user hoàn thành nhập.

---

# 33. Enable/Disable nút Save

Một pattern rất đẹp:

```text
Form valid
    ↓
Save enabled

Form invalid
    ↓
Save disabled
```

Ví dụ:

```python
self.save_button.setEnabled(False)
```

Sau mỗi thay đổi:

```python
def update_save_state(self):
    valid = self.validate_form()
    self.save_button.setEnabled(valid)
```

Kết nối:

```python
self.name_edit.textChanged.connect(
    self.update_save_state
)

self.age_edit.textChanged.connect(
    self.update_save_state
)

self.username_edit.textChanged.connect(
    self.update_save_state
)
```

---

# 34. Nhưng có một vấn đề

Nếu `validate_form()` đồng thời:

* kiểm tra
* thay đổi UI
* hiển thị lỗi

thì nó trở thành function có quá nhiều trách nhiệm.

Tốt hơn tách:

```text
validate_name()
validate_age()
validate_username()
       ↓
validation result
       ↓
update_error_ui()
```

Khi app lớn, điều này rất quan trọng.

---

# 35. Một kiến trúc validation tốt

Ta có thể nghĩ:

```text
User Input
    ↓
Field Validator
    ↓
Field State
    ↓
Form Validator
    ↓
Form State
    ↓
Submit
```

Ví dụ:

```text
Username
   ↓
QRegularExpressionValidator
   ↓
acceptable
```

Sau đó:

```text
Name
Age
Username
Email
   ↓
Form validation
   ↓
valid = True/False
```

---

# 36. Ví dụ hoàn chỉnh

```python
import sys

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QIntValidator,
    QRegularExpressionValidator,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QFormLayout,
    QVBoxLayout,
)


class UserForm(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Validation Demo")

        self.name_edit = QLineEdit()

        self.age_edit = QLineEdit()
        self.age_edit.setValidator(
            QIntValidator(1, 120)
        )

        self.username_edit = QLineEdit()

        regex = QRegularExpression(
            r"^[A-Za-z][A-Za-z0-9_]{2,19}$"
        )

        self.username_edit.setValidator(
            QRegularExpressionValidator(regex)
        )

        self.error_label = QLabel()
        self.save_button = QPushButton("Save")

        form = QFormLayout()

        form.addRow(
            "Name:",
            self.name_edit,
        )

        form.addRow(
            "Age:",
            self.age_edit,
        )

        form.addRow(
            "Username:",
            self.username_edit,
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(self.save_button)

        self.save_button.clicked.connect(
            self.save
        )

    def validate_form(self):

        errors = []

        name = self.name_edit.text().strip()

        if not name:
            errors.append(
                "Name is required."
            )

        if not self.age_edit.hasAcceptableInput():
            errors.append(
                "Age must be between 1 and 120."
            )

        if not self.username_edit.hasAcceptableInput():
            errors.append(
                "Username is invalid."
            )

        return errors

    def save(self):

        errors = self.validate_form()

        if errors:
            self.error_label.setText(
                "\n".join(errors)
            )
            return

        self.error_label.clear()

        print("Form is valid.")
        print("Name:", self.name_edit.text())
        print("Age:", self.age_edit.text())
        print(
            "Username:",
            self.username_edit.text(),
        )


app = QApplication(sys.argv)

window = UserForm()
window.resize(450, 250)
window.show()

sys.exit(app.exec())
```

---

# 37. Có một vấn đề nhỏ trong ví dụ trên

`QIntValidator` kiểm tra:

```text
1 → 120
```

nhưng business rule:

```text
Age bắt buộc
```

lại là một chuyện khác.

Nếu `age_edit` rỗng:

```python
hasAcceptableInput()
```

không phải lúc nào cũng nên được coi là cách duy nhất để biểu diễn required-field semantics.

Đây chính là lý do:

```text
Input Validator
        ≠
Business Validation
```

---

# 38. Phân tầng validation

Một kiến trúc tốt:

```text
Layer 1
Input validation
    ↓
"Người dùng có thể nhập gì?"

Layer 2
Form validation
    ↓
"Form đã đầy đủ chưa?"

Layer 3
Domain validation
    ↓
"Dữ liệu có hợp lệ theo nghiệp vụ?"

Layer 4
Database validation
    ↓
"Dữ liệu có vi phạm constraint?"
```

Ví dụ:

```text
Age
```

### Input

```text
chỉ số nguyên
```

### Form

```text
required
```

### Domain

```text
age >= 18 nếu đăng ký tài khoản đặc biệt
```

### Database

```text
NOT NULL
```

Bốn tầng không nên bị trộn lẫn.

---

# 39. Validator không thay thế Database Constraint

Ví dụ:

```python
email_edit.setValidator(...)
```

không có nghĩa database sẽ an toàn.

Database vẫn phải có:

```text
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
```

Qt validation chủ yếu là:

> **User Experience + Input Control**

chứ không phải security boundary.

---

# 40. Validation và Security

Đặc biệt nếu app giao tiếp với:

* API
* database
* server

thì:

```text
Client validation
```

không được coi là:

```text
Security validation
```

Server/backend vẫn phải validate lại.

---

# 41. Bài tập 1 — Age Validator

Tạo:

```text
Age:
[__________]
```

Yêu cầu:

```text
0 → 120
```

dùng:

```python
QIntValidator
```

Không dùng regex.

---

# 42. Bài tập 2 — Price

Tạo:

```text
Price:
[____________]
```

Yêu cầu:

```text
0.00 → 999999.99
```

Tối đa:

```text
2 decimal places
```

Dùng:

```python
QDoubleValidator
```

---

# 43. Bài tập 3 — Username

Yêu cầu:

```text
3 → 20 characters

First character:
A-Z / a-z

Remaining:
A-Z / a-z / 0-9 / _
```

Regex:

```text
^[A-Za-z][A-Za-z0-9_]{2,19}$
```

Dùng:

```python
QRegularExpressionValidator
```

---

# 44. Bài tập 4 — Product Code

Format:

```text
SP-000001
```

Ví dụ valid:

```text
SP-000001
SP-123456
```

Invalid:

```text
sp-000001
SP-123
ABC-123456
```

---

# 45. Bài tập 5 — Registration Form

Xây:

```text
┌───────────────────────────────────┐
│ Register                          │
│                                   │
│ Username: [___________________]   │
│ Password: [___________________]   │
│ Age:      [___________________]   │
│ Email:    [___________________]   │
│                                   │
│              [ Register ]         │
└───────────────────────────────────┘
```

Validation:

```text
Username
    ↓
3–20 chars

Age
    ↓
18–120

Email
    ↓
required + format

Password
    ↓
required + minimum length
```

Khi nhấn Register:

```text
Nếu invalid
    ↓
hiển thị tất cả lỗi

Nếu valid
    ↓
print("Register success")
```

---

# 46. Bài tập Deep Dive — Tự viết Validator

Sau khi làm xong các validator có sẵn, hãy thử viết:

```python
class EvenNumberValidator(QValidator):
    ...
```

Mục tiêu:

```text
2
4
6
8
...
```

là `Acceptable`.

Ví dụ:

```text
abc
```

→ `Invalid`.

Nhưng:

```text
1
```

có thể coi là:

```text
Intermediate
```

vì user có thể tiếp tục nhập:

```text
12
```

để tạo thành số chẵn.

Đây là bài tập rất tốt để bạn thực sự hiểu:

```text
Acceptable
Intermediate
Invalid
```

---

# 47. Mental Model Buổi 7

Bạn cần nhớ:

```text
                   User Input
                       │
                       ▼
                  QLineEdit
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         Validator          Form Validator
             │                   │
       ┌─────┼─────┐             │
       ▼     ▼     ▼             ▼
   Invalid  Inter  Accept     Form Valid?
                               │
                         ┌─────┴─────┐
                         ▼           ▼
                       Submit      Show errors
```

Và đặc biệt:

```text
QIntValidator
    ↓
Integer input

QDoubleValidator
    ↓
Floating-point input

QRegularExpressionValidator
    ↓
Pattern input

Form Validation
    ↓
Business/form completeness
```

---

## Roadmap tiếp theo

### Buổi 8 — Dialog

Chúng ta sẽ học:

```text
QDialog
    │
    ├── Modal
    ├── Modeless
    ├── exec()
    ├── open()
    ├── accept()
    ├── reject()
    ├── QDialogButtonBox
    │
    ├── QMessageBox
    ├── QInputDialog
    ├── QFileDialog
    │
    └── Custom Dialog
```

Đặc biệt tôi sẽ giải thích kỹ **`exec()` vs `show()` vs `open()`**, vì đây là chỗ rất nhiều người dùng PySide6 hiểu sai về **nested event loop và modal dialog**.
