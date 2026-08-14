# Buổi 4 — Text, Button, TextField, Image: Control Deep Dive

Ở 3 buổi đầu, bạn đã có mental model:

```text
Application
    ↓
Page
    ↓
Control Tree
    ↓
Event
    ↓
State
    ↓
Update
```

Hôm nay chúng ta đi sâu vào **các control cơ bản nhất của Flet**.

Mục tiêu sau buổi này:

* Hiểu `Text`
* Hiểu `Button`
* Hiểu `TextField`
* Hiểu `Image`
* Hiểu properties của Control
* Hiểu `value`
* Hiểu `visible`
* Hiểu `disabled`
* Hiểu event handler
* Xây được một Form hoàn chỉnh
* Biết cách tổ chức reference tới UI controls

---

# 1. Control có hai loại dữ liệu

Khi nhìn một control:

```python
text = ft.Text("Hello")
```

hãy nghĩ nó có hai nhóm thông tin:

```text
Text
│
├── State / Data
│     └── value
│
└── Presentation
      ├── size
      ├── weight
      ├── color
      ├── visible
      └── ...
```

Ví dụ:

```python
text.value = "Hello"
text.size = 30
text.visible = True
```

Đây là tư duy rất quan trọng.

---

# 2. `Text`

Control cơ bản nhất:

```python
text = ft.Text("Hello")
```

Sau đó:

```python
page.add(text)
```

Bạn có thể thay đổi:

```python
text.value = "Hello Flet"
```

và:

```python
page.update()
```

---

# 3. `Text.value`

Ví dụ:

```python
message = ft.Text(
    value="Ready"
)
```

Thay đổi:

```python
message.value = "Loading..."
page.update()
```

Hoặc:

```python
message.value = "Completed"
page.update()
```

Mental model:

```text
message
   │
   └── value
         │
         ├── Ready
         ├── Loading...
         └── Completed
```

---

# 4. Text styling

Bạn có thể cấu hình text:

```python
title = ft.Text(
    value="My Application",
    size=30,
    weight=ft.FontWeight.BOLD,
)
```

Tư duy:

```text
Text
├── content
├── size
├── weight
└── ...
```

Ví dụ:

```python
ft.Text(
    "Hello",
    size=24,
    weight=ft.FontWeight.BOLD,
)
```

---

# 5. Text không chỉ dùng để hiển thị static content

Một pattern cực kỳ quan trọng:

```python
status = ft.Text("Ready")
```

Sau đó status trở thành một phần của state presentation:

```python
def set_status(message):
    status.value = message
    page.update()
```

Ví dụ:

```python
set_status("Loading...")
```

hoặc:

```python
set_status("Success")
```

Đây là pattern chúng ta sẽ sử dụng rất nhiều trong app thực tế.

---

# 6. `Button`

Một button cơ bản:

```python
button = ft.Button(
    "Save"
)
```

Nhưng button không làm gì nếu không có event.

```python
def save(e):
    print("Save clicked")
```

Sau đó:

```python
button = ft.Button(
    "Save",
    on_click=save,
)
```

Flow:

```text
User click
    ↓
Button
    ↓
on_click
    ↓
save(e)
```

---

# 7. Event object

Handler nhận:

```python
def save(e):
    print(e)
```

`e` là event object.

Trong nhiều trường hợp bạn có thể truy cập control phát sinh event thông qua event information.

Điều quan trọng ở giai đoạn này:

> Event handler không phải là magic. Flet gọi function của bạn và truyền event vào.

---

# 8. Có thể bỏ qua event parameter?

Python không cho:

```python
def save():
    ...
```

nếu Flet gọi callback với một argument.

Cách đơn giản:

```python
def save(e):
    ...
```

Nếu không dùng `e`, vẫn giữ nó:

```python
def save(e):
    print("Saved")
```

---

# 9. `disabled`

Một button có thể disable:

```python
button = ft.Button(
    "Save",
    disabled=True,
)
```

Khi đó:

```text
Save
↓
Disabled
↓
Không tương tác
```

Sau đó có thể bật:

```python
button.disabled = False
page.update()
```

Ví dụ:

```python
def enable_save(e):
    save_button.disabled = False
    page.update()
```

---

# 10. `visible`

Control có thể ẩn:

```python
message = ft.Text(
    "Error",
    visible=False,
)
```

Sau đó:

```python
message.visible = True
page.update()
```

Pattern:

```text
Initial
visible = False

     ↓

Error occurs

     ↓

visible = True
```

Rất hữu ích cho:

* error message
* loading indicator
* advanced options
* empty state
* conditional UI

---

# 11. `TextField`

Đây là control cực kỳ quan trọng.

```python
username = ft.TextField(
    label="Username"
)
```

Đọc dữ liệu:

```python
value = username.value
```

Ví dụ:

```python
def login(e):
    print(username.value)
```

---

# 12. TextField có state

Mental model:

```text
TextField
│
├── value
├── label
├── hint_text
├── password
├── disabled
└── ...
```

Ví dụ:

```python
username = ft.TextField(
    label="Username",
    hint_text="Enter username",
)
```

---

# 13. `label` và `hint_text`

Hai cái này khác nhau.

```python
ft.TextField(
    label="Username",
)
```

`label` mô tả field.

Còn:

```python
ft.TextField(
    hint_text="Enter your username",
)
```

là gợi ý bên trong field.

Có thể kết hợp:

```python
username = ft.TextField(
    label="Username",
    hint_text="example@gmail.com",
)
```

---

# 14. Password field

```python
password = ft.TextField(
    label="Password",
    password=True,
)
```

Mental model:

```text
TextField
    │
    ├── value
    └── password=True
```

Dữ liệu vẫn nằm trong:

```python
password.value
```

---

# 15. Xóa TextField

Bạn có thể thay đổi:

```python
username.value = ""
password.value = ""
```

Sau đó:

```python
page.update()
```

Ví dụ:

```python
def clear_form(e):
    username.value = ""
    password.value = ""

    page.update()
```

Đây là cách tốt hơn việc xóa rồi tạo TextField mới.

---

# 16. `TextField` event

TextField có thể phản ứng khi dữ liệu thay đổi.

Ví dụ:

```python
def on_change(e):
    print(username.value)
```

Sau đó:

```python
username = ft.TextField(
    label="Username",
    on_change=on_change,
)
```

Flow:

```text
User types
    ↓
TextField
    ↓
on_change
    ↓
handler
```

---

# 17. `on_submit`

Ngoài `on_change`, form thường cần xử lý khi user submit.

Ví dụ:

```python
def submit(e):
    print("Submit")

username = ft.TextField(
    label="Username",
    on_submit=submit,
)
```

Điều này hữu ích khi user nhấn Enter.

---

# 18. `on_focus` / focus-related events

Trong form thực tế, bạn có thể cần biết field được focus hoặc mất focus.

Ví dụ tư duy:

```text
TextField
   │
   ├── focus
   └── blur
```

Các API cụ thể có thể thay đổi theo phiên bản Flet, vì vậy khi xây project thực tế nên kiểm tra API của phiên bản đang dùng.

Điều quan trọng hiện tại là hiểu **event-driven UI**.

---

# 19. Validation

Bây giờ chúng ta kết hợp `TextField` + `Text`.

Ví dụ:

```python
username = ft.TextField(
    label="Username"
)

error = ft.Text(
    visible=False
)
```

Handler:

```python
def validate(e):
    if not username.value:
        error.value = "Username is required"
        error.visible = True
    else:
        error.visible = False

    page.update()
```

Flow:

```text
Input
 ↓
Validation
 ↓
Error state
 ↓
UI state
 ↓
update
```

---

# 20. Validation không nên trộn với database

Sai:

```python
def save(e):
    if not username.value:
        ...
    
    database.execute(...)
    
    api.call(...)
    
    ...
```

Ở app lớn:

```text
UI
 ↓
Validation
 ↓
Use Case
 ↓
Repository
```

Chúng ta sẽ học kiến trúc này sau.

---

# 21. `Image`

Một image cơ bản:

```python
image = ft.Image(
    src="https://example.com/image.jpg"
)
```

Hoặc tùy trường hợp sử dụng resource/file tương ứng.

Mental model:

```text
Image
│
├── source
├── width
├── height
└── fit
```

---

# 22. Image trong app đọc truyện

Sau này bạn có thể có:

```text
Book
│
├── title
├── author
├── cover
└── chapters
```

UI:

```text
┌─────────────────────┐
│                     │
│       COVER         │
│                     │
└─────────────────────┘

Title
Author

[ Read ]
```

Flet tree:

```text
Column
├── Image
├── Text(title)
├── Text(author)
└── Button("Read")
```

---

# 23. Reference tới Control

Đây là kỹ năng rất quan trọng.

Không nên:

```python
page.add(
    ft.Text("Ready")
)
```

nếu sau này bạn cần thay đổi nó.

Tốt hơn:

```python
status = ft.Text("Ready")

page.add(status)
```

Bây giờ bạn có reference:

```python
status.value = "Loading..."
```

Tư duy:

```text
Python variable
      │
      ▼
Control object
      │
      ▼
UI Tree
```

---

# 24. Một UI thực tế

Hãy xây Login Form:

```python
import flet as ft


def main(page: ft.Page):

    username = ft.TextField(
        label="Username",
    )

    password = ft.TextField(
        label="Password",
        password=True,
    )

    status = ft.Text(
        "Ready"
    )

    def login(e):
        if not username.value:
            status.value = "Username is required"
            page.update()
            return

        if not password.value:
            status.value = "Password is required"
            page.update()
            return

        status.value = "Login successfully"
        page.update()

    login_button = ft.Button(
        "Login",
        on_click=login,
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text(
                    "Login",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                username,
                password,
                login_button,
                status,
            ]
        )
    )


ft.run(main)
```

---

# 25. Phân tích object graph

Đừng chỉ đọc code.

Hãy nhìn object:

```text
username ──────┐
password ──────┤
status ────────┤
login_button ──┤
               │
               ▼
            Column
               │
               ▼
              Page
```

Event:

```text
login_button
     │
     ▼
  login(e)
     │
     ├── username.value
     ├── password.value
     │
     ▼
 status.value
     │
     ▼
 page.update()
```

---

# 26. Tách `render()`

Ta có thể cải thiện:

```python
def render():
    page.update()
```

Nhưng tốt hơn là hiểu:

> `render()` chịu trách nhiệm phản ánh state vào UI.

Ví dụ:

```python
def render():
    status.value = status_message
    login_button.disabled = is_loading

    page.update()
```

Sau này:

```text
State
 ↓
render()
 ↓
Controls
 ↓
page.update()
```

Đây là nền móng cho state management.

---

# 27. Loading state

Một pattern cực kỳ quan trọng trong ứng dụng thực tế.

Ta có:

```python
is_loading = False
```

Khi login:

```text
Before:

[ Login ]
Status: Ready


During:

[ Login disabled ]
Status: Loading...


After:

[ Login ]
Status: Success
```

Code:

```python
is_loading = False

def login(e):
    nonlocal is_loading

    is_loading = True

    login_button.disabled = True
    status.value = "Loading..."

    page.update()

    # xử lý...

    is_loading = False

    login_button.disabled = False
    status.value = "Success"

    page.update()
```

Đây chính là pattern sẽ xuất hiện rất nhiều trong:

* API request
* database
* crawler
* TTS
* file processing

---

# 28. TTS App của bạn sẽ dùng pattern này

Ví dụ:

```text
[ Convert ]

        ↓

[ Converting... ]
██████████░░░░░░ 60%

        ↓

[ Completed ]
```

State:

```python
is_processing
progress
message
```

UI:

```text
Button
ProgressBar
Status Text
```

Architecture:

```text
User
 ↓
Button
 ↓
Event
 ↓
TTS Service
 ↓
Worker
 ↓
Progress
 ↓
UI
```

Sau này chúng ta sẽ kết hợp với `asyncio`.

---

# 29. Form state

Một form có thể có:

```text
username
password
is_loading
error
```

Có thể biểu diễn:

```python
state = {
    "username": "",
    "password": "",
    "is_loading": False,
    "error": None,
}
```

Nhưng **đừng vội dùng dictionary cho mọi thứ**.

Sau này chúng ta sẽ học:

```text
dataclass
Model
ViewModel
State object
```

để quản lý state chuyên nghiệp hơn.

---

# 30. Một nguyên tắc cực kỳ quan trọng

### Không để UI object trở thành business state nếu không cần.

Ví dụ:

```python
count = 10
text.value = "10"
```

`count` là state.

`text.value` là presentation.

Không nên coi:

```python
text.value
```

là database/business state.

Mental model:

```text
Domain State
     │
     ▼
Presentation State
     │
     ▼
Control
```

Đây là một trong những nguyên tắc quan trọng nhất khi app bắt đầu lớn.

---

# 31. Ví dụ Counter đúng tư duy

```python
import flet as ft


def main(page: ft.Page):

    count = 0

    count_text = ft.Text(
        size=30,
    )

    status_text = ft.Text()

    def render():
        count_text.value = str(count)

        if count == 0:
            status_text.value = "Ready"
        else:
            status_text.value = "Counting..."

        page.update()

    def increment(e):
        nonlocal count

        count += 1
        render()

    def decrement(e):
        nonlocal count

        if count > 0:
            count -= 1

        render()

    def reset(e):
        nonlocal count

        count = 0
        render()

    page.add(
        ft.Column(
            controls=[
                count_text,
                status_text,

                ft.Row(
                    controls=[
                        ft.Button("-", on_click=decrement),
                        ft.Button("+", on_click=increment),
                        ft.Button("Reset", on_click=reset),
                    ]
                ),
            ]
        )
    )

    render()


ft.run(main)
```

Hãy chú ý:

```python
render()
```

được gọi ngay sau khi UI được tạo.

Điều này tránh phải viết:

```python
count_text.value = "0"
status_text.value = "Ready"
```

ở nhiều nơi.

---

# 32. Kiến trúc hiện tại

Counter của chúng ta:

```text
main()
│
├── State
│    └── count
│
├── Controls
│    ├── count_text
│    └── status_text
│
├── Events
│    ├── increment()
│    ├── decrement()
│    └── reset()
│
└── render()
```

Đây là một bước rất quan trọng.

Ở những buổi sau, cấu trúc này sẽ phát triển thành:

```text
Component
│
├── State
├── View
├── Events
└── Render
```

---

# 33. Một lỗi rất phổ biến

Không nên:

```python
def increment(e):
    nonlocal count

    count += 1

    page.clean()

    page.add(
        ft.Text(str(count)),
        ft.Button("+", on_click=increment),
    )
```

Tại sao?

Bạn đang:

```text
Destroy UI
   ↓
Create UI
   ↓
Attach events
   ↓
Render again
```

Trong app lớn sẽ trở nên rất khó quản lý.

Tốt hơn:

```text
Keep Controls
     ↓
Change properties
     ↓
Update
```

---

# 34. Mental model Buổi 4

Hãy ghi nhớ:

```text
                    Control
                       │
        ┌──────────────┼──────────────┐
        │              │              │
      Data       Presentation       Events
        │              │              │
      value          size         on_click
      state          visible      on_change
                     disabled      on_submit
                       │
                       ▼
                   page.update()
```

Và:

```text
Application State
       ↓
Event
       ↓
State Mutation
       ↓
Render
       ↓
Control Mutation
       ↓
page.update()
       ↓
UI
```

---

# Bài tập Buổi 4 — Login Form hoàn chỉnh

Hãy xây một Login Form có cấu trúc:

```text
┌──────────────────────────────────┐
│              LOGIN               │
│                                  │
│ Username                         │
│ ┌──────────────────────────────┐ │
│ │                              │ │
│ └──────────────────────────────┘ │
│                                  │
│ Password                         │
│ ┌──────────────────────────────┐ │
│ │                              │ │
│ └──────────────────────────────┘ │
│                                  │
│        [ Login ] [ Clear ]       │
│                                  │
│ Status: Ready                    │
└──────────────────────────────────┘
```

### Yêu cầu

**1. Controls**

Phải có reference riêng:

```python
title
username
password
login_button
clear_button
status
```

**2. Login**

Nếu username rỗng:

```text
Username is required
```

Nếu password rỗng:

```text
Password is required
```

Nếu cả hai hợp lệ:

```text
Login successfully
```

**3. Clear**

Đưa:

```text
username = ""
password = ""
status = "Ready"
```

**4. Loading**

Khi click Login:

```text
Login button → disabled
Status → Loading...
```

Sau đó trở lại trạng thái bình thường.

**5. Không rebuild UI**

Không được dùng:

```python
page.clean()
```

để refresh form.

Chỉ:

```text
State
 ↓
Control properties
 ↓
page.update()
```

---

## Thử thách Deep Dive

Tách chương trình thành:

```text
main()
│
├── create_controls()
├── setup_events()
└── render()
```

Mục tiêu là bắt đầu hình thành kiến trúc:

```text
UI Construction
       │
       ▼
Event Wiring
       │
       ▼
State
       │
       ▼
Render
```

Đây sẽ là nền tảng rất tốt trước khi chúng ta bước sang **Buổi 5 — `Row`, `Column`, `Container` và Layout Engine**, nơi chúng ta sẽ học cách kiểm soát **width, height, alignment, spacing, padding, margin, expand và responsive layout** để xây giao diện thực tế thay vì chỉ xếp control mặc định.
