Đúng, mình đã **đi lệch roadmap**. Cảm ơn bạn đã chỉ ra.

Từ đây mình sẽ bám **đúng roadmap bạn đưa**, không tự ý nhảy sang Navigation/Router nữa.

# Giai đoạn I — Flet Foundation

## Phần 1 — Làm quen Flet

| Buổi  | Nội dung                    | Trạng thái       |
| ----- | --------------------------- | ---------------- |
| 1     | Flet là gì? Kiến trúc Flet  | ✅                |
| 2     | `Page` và vòng đời ứng dụng | ✅                |
| 3     | Controls và UI Tree         | ✅                |
| 4     | Text, Button, Icon, Image   | ✅                |
| 5     | Row, Column, Container      | ✅                |
| 6     | Responsive Layout           | ✅                |
| **7** | **Event và Event Handler**  | ⬅️ **Tiếp theo** |
| 8     | State cơ bản                |                  |
| 9     | `page.update()` deep dive   |                  |
| 10    | Mini Project: Todo App      |                  |

Vì vậy **Buổi 7 đúng phải là Event và Event Handler**, không phải Navigation.

---

# Buổi 7 — Event và Event Handler

Hôm nay chúng ta sẽ học từ nền tảng:

```text
User Action
     ↓
Event
     ↓
Event Handler
     ↓
State Change
     ↓
page.update()
     ↓
UI thay đổi
```

Đây là một trong những cơ chế quan trọng nhất của Flet.

---

## 1. Event là gì?

Event là một sự kiện xảy ra trong UI.

Ví dụ:

```text
Click button
        ↓
click event

Gõ text
        ↓
change event

Nhấn phím
        ↓
keyboard event

Thay đổi slider
        ↓
change event
```

Ví dụ:

```python
ft.Button(
    "Click me",
)
```

Khi user click:

```text
User
 ↓
Click
 ↓
Event
```

Nhưng Flet cần biết:

> Khi event xảy ra thì phải làm gì?

Đó chính là **Event Handler**.

---

# 2. Event Handler là gì?

Event handler là một function được gọi khi event xảy ra.

Ví dụ:

```python
def handle_click(e):
    print("Button clicked!")
```

Sau đó:

```python
ft.Button(
    "Click me",
    on_click=handle_click,
)
```

Flow:

```text
User click
    ↓
on_click
    ↓
handle_click()
    ↓
print()
```

---

# 3. `on_click`

Đây là event bạn sẽ dùng cực kỳ nhiều.

```python
import flet as ft


def main(page: ft.Page):

    def handle_click(e):
        print("Clicked!")

    page.add(
        ft.Button(
            "Click",
            on_click=handle_click,
        )
    )


ft.run(main)
```

---

# 4. Event Handler nhận `e`

Bạn sẽ thấy:

```python
def handle_click(e):
    ...
```

`e` là event object.

Thông thường:

```python
e
```

là một object chứa thông tin về event.

Ví dụ:

```python
def handle_click(e):
    print(type(e))
    print(e)
```

Bạn không nên xem `e` đơn giản là:

```text
e = event name
```

Mà hãy hiểu:

```text
e
│
├── source/control
├── event information
└── event-specific data
```

Thông tin cụ thể phụ thuộc loại event.

---

# 5. Tại sao handler cần `e`?

Ví dụ click:

```python
def handle_click(e):
    print(e.control)
```

`e.control` giúp bạn biết control nào phát ra event.

Đây rất hữu ích khi có nhiều button.

Ví dụ:

```python
def handle_click(e):
    print(e.control.text)
```

---

# 6. Nhiều Button dùng một handler

Thay vì:

```python
def handle_add(e):
    ...


def handle_delete(e):
    ...


def handle_save(e):
    ...
```

đôi khi ta có thể:

```python
def handle_click(e):
    print(e.control.text)
```

Sau đó:

```python
ft.Button(
    "Add",
    on_click=handle_click,
)

ft.Button(
    "Delete",
    on_click=handle_click,
)

ft.Button(
    "Save",
    on_click=handle_click,
)
```

Kết quả:

```text
Click Add
→ Add

Click Delete
→ Delete

Click Save
→ Save
```

---

# 7. Event Handler thực chất là callback

Trong Python:

```python
on_click=handle_click
```

không phải:

```python
on_click=handle_click()
```

Đây là khác biệt cực kỳ quan trọng.

### Đúng

```python
on_click=handle_click
```

Ta truyền function.

### Sai

```python
on_click=handle_click()
```

Ta gọi function ngay lập tức.

---

# 8. Vì sao `handle_click()` sai?

Ví dụ:

```python
def handle_click(e):
    print("Clicked")
```

Nếu:

```python
on_click=handle_click()
```

Python thực hiện ngay:

```text
main()
 ↓
handle_click()
 ↓
print("Clicked")
```

Button chưa được click nhưng handler đã chạy.

Ta muốn:

```text
main()
 ↓
Đăng ký callback
 ↓
...
 ↓
User click
 ↓
handle_click()
```

Vì vậy:

```python
on_click=handle_click
```

---

# 9. Lambda Event Handler

Bạn có thể viết:

```python
ft.Button(
    "Click",
    on_click=lambda e: print("Clicked"),
)
```

Nhưng với logic phức tạp:

```python
on_click=lambda e: ...
```

sẽ nhanh chóng khó đọc.

Tốt hơn:

```python
def handle_click(e):
    ...
```

---

# 10. Khi nào dùng lambda?

### Logic cực ngắn

```python
on_click=lambda e: print("Hello")
```

OK.

### Logic dài

```python
def handle_click(e):
    ...
```

Tốt hơn.

---

# 11. Truyền argument cho handler

Đây là vấn đề rất hay gặp.

Bạn muốn:

```python
def delete_book(book_id):
    print(book_id)
```

Nhưng Flet cần handler dạng:

```python
handler(event)
```

Không thể trực tiếp:

```python
on_click=delete_book(123)
```

vì nó sẽ gọi function ngay.

---

# 12. Dùng lambda

```python
ft.Button(
    "Delete",
    on_click=lambda e: delete_book(123),
)
```

Flow:

```text
Click
 ↓
lambda(e)
 ↓
delete_book(123)
```

---

# 13. Dùng `functools.partial`

Python có:

```python
from functools import partial
```

Ví dụ:

```python
def delete_book(book_id, e):
    print(book_id)


handler = partial(
    delete_book,
    123,
)
```

Sau đó:

```python
ft.Button(
    "Delete",
    on_click=handler,
)
```

`partial` rất hữu ích khi xây UI component phức tạp.

---

# 14. Event propagation — tư duy

Trong UI framework, event có thể liên quan đến:

```text
User
 ↓
Control
 ↓
Event
 ↓
Handler
```

Ví dụ:

```text
Button
 ↓
on_click
 ↓
handle_click
```

Đừng nhầm:

```text
Event
```

với:

```text
Handler
```

Event:

> Chuyện gì vừa xảy ra?

Handler:

> Khi chuyện đó xảy ra thì làm gì?

---

# 15. `on_change`

Một event cực kỳ quan trọng khác là:

```python
on_change
```

Ví dụ `TextField`:

```python
def handle_change(e):
    print(e.control.value)


text_field = ft.TextField(
    label="Name",
    on_change=handle_change,
)
```

Khi user nhập:

```text
A
```

event.

```text
Al
```

event.

```text
Ali
```

event.

---

# 16. `TextField` event flow

```text
User types
    ↓
TextField value changes
    ↓
on_change
    ↓
handle_change(e)
    ↓
e.control.value
```

Ví dụ:

```python
def handle_change(e):
    print("Current value:", e.control.value)
```

---

# 17. Event object và `control`

Một pattern rất phổ biến:

```python
def handle_change(e):
    control = e.control

    print(control.value)
```

Có thể viết ngắn:

```python
def handle_change(e):
    print(e.control.value)
```

---

# 18. Event handler thay đổi UI

Đây mới là phần quan trọng.

Ví dụ:

```python
def handle_click(e):
    text.value = "Hello Flet!"
    page.update()
```

Full:

```python
import flet as ft


def main(page: ft.Page):

    text = ft.Text("Hello")

    def handle_click(e):
        text.value = "Button clicked!"
        page.update()

    page.add(
        text,
        ft.Button(
            "Click",
            on_click=handle_click,
        ),
    )


ft.run(main)
```

Flow:

```text
Click
 ↓
handle_click
 ↓
text.value = ...
 ↓
page.update()
 ↓
UI render
```

---

# 19. Đây là pattern cốt lõi của Flet

Hãy ghi nhớ:

```text
EVENT
  ↓
HANDLER
  ↓
CHANGE STATE
  ↓
UPDATE UI
```

Ví dụ:

```python
def handle_click(e):
    counter.value += 1
    page.update()
```

Sau này Buổi 8 chúng ta sẽ chính thức học sâu về:

```text
STATE
```

---

# 20. Counter App

Một ví dụ kinh điển:

```python
import flet as ft


def main(page: ft.Page):

    counter = ft.Text(
        "0",
        size=30,
    )

    def increment(e):
        value = int(counter.value)
        counter.value = str(value + 1)
        page.update()

    page.add(
        counter,
        ft.Button(
            "Increment",
            on_click=increment,
        ),
    )


ft.run(main)
```

Flow:

```text
0
 ↓
Click
 ↓
1
 ↓
Click
 ↓
2
 ↓
Click
 ↓
3
```

---

# 21. Hai Button

```python
def increment(e):
    counter.value = str(
        int(counter.value) + 1
    )
    page.update()


def decrement(e):
    counter.value = str(
        int(counter.value) - 1
    )
    page.update()
```

UI:

```python
ft.Row(
    controls=[
        ft.Button(
            "-",
            on_click=decrement,
        ),
        counter,
        ft.Button(
            "+",
            on_click=increment,
        ),
    ]
)
```

---

# 22. Event handler có thể gọi function khác

Không nên nhồi tất cả logic:

```python
def handle_click(e):
    # 100 dòng
```

Tốt hơn:

```python
def handle_click(e):
    result = calculate()
    update_ui(result)
```

Architecture:

```text
Event Handler
      ↓
Application logic
      ↓
Update state
      ↓
UI
```

Đây là bước đầu tiên dẫn tới architecture tốt.

---

# 23. Đừng để handler thành "God Function"

Ví dụ xấu:

```python
def on_click(e):
    validate()
    database.connect()
    database.query()
    parser.parse()
    save()
    update_everything()
    show_dialog()
    ...
```

Handler đang làm quá nhiều việc.

Tốt hơn:

```python
def on_click(e):
    result = save_book()
    show_result(result)
```

Sau này ta sẽ học:

```text
UI
 ↓
Controller / ViewModel
 ↓
Use Case
 ↓
Repository
```

---

# 24. Event handler và closure

Đây là kiến thức Python rất quan trọng khi dùng Flet.

Ví dụ:

```python
buttons = []

for i in range(3):

    def handle_click(e):
        print(i)

    buttons.append(
        ft.Button(
            str(i),
            on_click=handle_click,
        )
    )
```

Bạn có thể gặp vấn đề với closure.

Đây là **late binding** của Python.

---

# 25. Closure problem

Ví dụ:

```python
for i in range(3):
    buttons.append(
        ft.Button(
            str(i),
            on_click=lambda e: print(i),
        )
    )
```

Bạn có thể kỳ vọng:

```text
0
1
2
```

nhưng kết quả có thể là:

```text
2
2
2
```

Tại sao?

Lambda giữ reference tới biến:

```text
i
```

chứ không snapshot giá trị tại thời điểm tạo.

---

# 26. Fix bằng default argument

```python
for i in range(3):
    buttons.append(
        ft.Button(
            str(i),
            on_click=lambda e, i=i: print(i),
        )
    )
```

Bây giờ:

```text
Button 0 → 0
Button 1 → 1
Button 2 → 2
```

Đây là kiến thức Python cực kỳ quan trọng khi tạo UI động.

---

# 27. Fix bằng function factory

Cách sạch hơn:

```python
def make_handler(index):

    def handle_click(e):
        print(index)

    return handle_click
```

Sau đó:

```python
for i in range(3):
    ft.Button(
        str(i),
        on_click=make_handler(i),
    )
```

Mental model:

```text
make_handler(0)
    ↓
handler for 0

make_handler(1)
    ↓
handler for 1

make_handler(2)
    ↓
handler for 2
```

---

# 28. Event `on_submit`

Một số control có event submit.

Ví dụ TextField:

```python
def handle_submit(e):
    print(e.control.value)
```

```python
ft.TextField(
    label="Search",
    on_submit=handle_submit,
)
```

Flow:

```text
User enters text
       ↓
Submit
       ↓
on_submit
```

---

# 29. `on_focus`

Một số control có event liên quan focus.

Tư duy:

```text
Focus
 ↓
on_focus

Blur
 ↓
on_blur
```

Các event kiểu này đặc biệt hữu ích cho:

```text
Validation
Search box
Keyboard interaction
Forms
```

---

# 30. Event validation

Ví dụ:

```python
def validate(e):
    if not e.control.value:
        e.control.error_text = "Required"
    else:
        e.control.error_text = None

    page.update()
```

Đây là pattern:

```text
User input
 ↓
Event
 ↓
Validate
 ↓
Modify control
 ↓
page.update()
```

Buổi 9 chúng ta sẽ đi sâu hơn vào validation.

---

# 31. Event và `page.update()`

Một điều bạn cần đặc biệt chú ý:

```python
def handle_click(e):
    text.value = "Changed"
```

Có thay đổi object.

Nhưng UI có thể chưa được cập nhật ngay.

Thông thường ta cần:

```python
page.update()
```

Flow:

```text
Python object
     ↓
Changed
     ↓
page.update()
     ↓
Flet sends UI update
```

Buổi 9 chúng ta sẽ **deep dive riêng `page.update()`**.

---

# 32. Một event có thể thay đổi nhiều controls

```python
def handle_click(e):
    title.value = "Updated"
    status.value = "Success"
    button.disabled = True

    page.update()
```

Không cần:

```python
page.update()
```

sau mỗi dòng.

Tốt hơn:

```python
change A
change B
change C
       ↓
one update
```

---

# 33. Event batch update

Ví dụ:

```python
def handle_save(e):

    title.value = "Saved"
    status.value = "Success"
    save_button.disabled = True

    page.update()
```

Mental model:

```text
Event
 ↓
Multiple mutations
 ↓
One UI update
```

Đây là pattern hiệu quả.

---

# 34. Event handler với async

Flet cũng hỗ trợ event handler async trong các tình huống phù hợp.

Ví dụ tư duy:

```python
async def handle_click(e):
    result = await do_something()
    ...
```

Đặc biệt quan trọng với app:

```text
HTTP
Database
TTS
Crawler
File IO
```

Sau này chúng ta sẽ có một phần riêng:

```text
Async UI
```

---

# 35. Event và exception

Đừng bỏ qua lỗi trong handler.

Ví dụ:

```python
def handle_click(e):
    try:
        result = risky_operation()
    except Exception as ex:
        print(ex)
```

Trong app thật:

```text
Event
 ↓
Use case
 ↓
Exception
 ↓
UI error state
```

Không nên để UI crash vì một event handler.

---

# 36. Event Architecture

Hãy hình dung:

```text
                  User
                   │
                   ▼
                 Event
                   │
                   ▼
             Event Handler
                   │
          ┌────────┴────────┐
          ▼                 ▼
       State             Service
          │                 │
          └────────┬────────┘
                   ▼
               UI Update
```

Đây là nền móng của toàn bộ Flet application architecture.

---

# 37. Quy tắc vàng

Khi viết handler, hãy tự hỏi:

### 1. Event gì?

```text
on_click?
on_change?
on_submit?
```

### 2. Handler nhận gì?

```python
e
```

### 3. Tôi cần lấy gì từ event?

```python
e.control
e.control.value
```

### 4. Tôi thay đổi state nào?

```text
counter
text
loading
error
```

### 5. UI có cần update không?

```python
page.update()
```

---

# 38. Bài tập 1 — Counter

Tạo:

```text
┌─────────────────────────┐
│          0              │
│                         │
│    [-]         [+]      │
└─────────────────────────┘
```

Yêu cầu:

```text
+ → tăng 1
- → giảm 1
```

Không dùng:

```python
counter.value = ...
```

để làm state chính.

Hãy thử giữ:

```python
count = 0
```

và UI chỉ hiển thị:

```python
str(count)
```

Đây sẽ chuẩn bị cho **Buổi 8 — State cơ bản**.

---

# 39. Bài tập 2 — Input

Tạo:

```text
┌─────────────────────────────┐
│ Name                        │
├─────────────────────────────┤
│                             │
└─────────────────────────────┘

[Show]
```

Khi click:

```text
Hello, Garden
```

Nếu input:

```text
Garden
```

thì:

```text
Hello, Garden
```

---

# 40. Bài tập 3 — Todo Event

Tạo:

```text
┌─────────────────────────────┐
│ Todo                        │
│                             │
│ [ Learn Python ] [Add]      │
│                             │
│ □ Learn Flet                │
│ □ Learn Asyncio             │
└─────────────────────────────┘
```

Các event:

```text
Add
 ↓
on_click

Checkbox
 ↓
on_change

Delete
 ↓
on_click
```

Mục tiêu:

```text
Event
 ↓
Handler
 ↓
Modify UI
```

Chưa cần database.

---

# 41. Bài tập Deep Dive — Dynamic Buttons

Tạo 5 button:

```text
[0] [1] [2] [3] [4]
```

Mỗi button click phải in đúng:

```text
Clicked: 0
Clicked: 1
Clicked: 2
Clicked: 3
Clicked: 4
```

Bạn phải xử lý đúng vấn đề:

```text
lambda
closure
late binding
```

Đây là bài tập **rất quan trọng**.

---

# 42. Tổng kết Buổi 7

Hôm nay bạn cần nắm chắc:

```text
Event
   ↓
Event Handler
```

Các event phổ biến:

```text
on_click
on_change
on_submit
on_focus
...
```

Handler:

```python
def handler(e):
    ...
```

Đăng ký:

```python
on_click=handler
```

Không phải:

```python
on_click=handler()
```

Lấy control:

```python
e.control
```

Lấy value:

```python
e.control.value
```

Thay đổi UI:

```python
control.value = ...
```

Cập nhật:

```python
page.update()
```

Và đặc biệt:

```text
lambda
closure
late binding
```

---

## Roadmap chính thức từ đây

```text
Giai đoạn I — Flet Foundation

Phần 1 — Làm quen Flet

01. Flet là gì? Kiến trúc Flet              ✅
02. Page và vòng đời ứng dụng               ✅
03. Controls và UI Tree                     ✅
04. Text, Button, Icon, Image               ✅
05. Row, Column, Container                  ✅
06. Responsive Layout                       ✅
07. Event và Event Handler                  ← hiện tại
08. State cơ bản
09. page.update() deep dive
10. Mini Project: Todo App
```

**Buổi tiếp theo là Buổi 8 — State cơ bản**, và đây sẽ là phần rất quan trọng: chúng ta sẽ phân biệt **UI Control, Application State, Local State, Derived State, Mutable State**, đồng thời xây một Counter/Todo nhỏ theo tư duy **State → UI** thay vì chỉ sửa control trực tiếp.
