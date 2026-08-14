# Buổi 2 — `Page` và vòng đời ứng dụng Flet

Ở buổi 1, bạn đã biết mô hình cơ bản:

```text
Python
   ↓
Flet
   ↓
Page
   ↓
Control Tree
   ↓
UI
```

Hôm nay chúng ta đi sâu vào **`Page`**, vì nếu hiểu sai `Page`, về sau bạn sẽ rất khó hiểu:

* `page.add()`
* `page.controls`
* `page.update()`
* event handler
* state
* navigation
* dialog
* responsive UI
* lifecycle
* async task

---

# 1. `Page` thực chất là gì?

Khi viết:

```python
import flet as ft


def main(page: ft.Page):
    ...
    

ft.run(main)
```

Flet sẽ tạo application và truyền một đối tượng `Page` vào hàm `main()`.

Ta có:

```text
ft.run(main)
    │
    ▼
Flet tạo Application
    │
    ▼
Tạo Page
    │
    ▼
Gọi main(page)
    │
    ▼
Bạn xây UI
```

Vì vậy:

```python
def main(page: ft.Page):
```

không phải là một hàm bình thường được bạn tự gọi.

Flet là bên gọi nó.

---

# 2. Application lifecycle cơ bản

Hãy hình dung:

```text
        ft.run(main)
              │
              ▼
     ┌─────────────────┐
     │ Create App      │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Create Page     │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ main(page)      │
     └────────┬────────┘
              │
              ▼
       Build Control Tree
              │
              ▼
         Render UI
              │
              ▼
       User interaction
              │
              ▼
           Events
              │
              ▼
       State changes
              │
              ▼
         page.update()
```

Đây là mental model rất quan trọng.

---

# 3. `page` chứa những gì?

`Page` có rất nhiều thuộc tính và phương thức.

Những thứ quan trọng nhất lúc đầu:

```python
page.title
page.controls
page.add()
page.remove()
page.clean()
page.update()
```

Ngoài ra còn có:

```python
page.theme
page.dark_mode
page.route
page.overlay
page.dialog
```

và nhiều API khác.

---

# 4. `page.add()`

Ví dụ:

```python
def main(page: ft.Page):
    page.add(
        ft.Text("Hello"),
        ft.Button("Click"),
    )
```

Có thể hình dung:

```text
Page
├── Text
└── Button
```

Tức là:

```python
page.add(...)
```

thêm control trực tiếp vào danh sách control của `Page`.

---

# 5. `page.controls`

Bạn có thể xem các control trực tiếp của Page:

```python
def main(page: ft.Page):
    page.add(
        ft.Text("Hello"),
        ft.Button("OK"),
    )

    print(page.controls)
```

Mental model:

```text
page.controls
       │
       ├── Text
       └── Button
```

Ví dụ:

```python
page.controls.append(ft.Text("Hello"))
```

về mặt ý tưởng là bạn đang thao tác vào control collection.

Nhưng trong code ứng dụng, **không nên lạm dụng thao tác trực tiếp vào `controls`**.

Thông thường nên dùng:

```python
page.add(...)
page.remove(...)
page.clean(...)
```

và sau đó update khi cần.

---

# 6. `page.clean()`

Xóa các control trực tiếp trên Page:

```python
def main(page: ft.Page):

    page.add(
        ft.Text("Hello"),
        ft.Button("OK"),
    )

    page.clean()
```

Sau `clean()`:

```text
Page
└── empty
```

Một ứng dụng nhiều màn hình có thể sử dụng pattern:

```text
Page
 │
 └── current_view
```

Sau đó thay view:

```text
Dashboard
    ↓
Users
    ↓
Settings
```

Tuy nhiên khi ứng dụng lớn, chúng ta sẽ học **Routing** thay vì tự `clean()` thủ công ở mọi nơi.

---

# 7. `page.remove()`

Bạn có thể xóa control cụ thể:

```python
def main(page: ft.Page):

    text = ft.Text("Hello")

    page.add(text)

    page.remove(text)
```

Mental model:

```text
Before:

Page
└── Text


remove(text)


After:

Page
```

---

# 8. `page.update()`

Đây là phần cực kỳ quan trọng.

Ví dụ:

```python
def main(page: ft.Page):

    text = ft.Text("Hello")

    page.add(text)

    text.value = "Hello Flet"

    page.update()
```

Có hai bước:

```text
1. Thay đổi state/control

text.value = "Hello Flet"

2. Đồng bộ UI

page.update()
```

---

# 9. Tách "state" và "UI"

Đây là tư duy rất quan trọng.

Ví dụ:

```python
count = 0
```

là state của application.

Còn:

```python
text = ft.Text("Count: 0")
```

là UI.

Khi user click:

```text
User
 ↓
Click
 ↓
count thay đổi
 ↓
Text thay đổi
 ↓
UI update
```

Ví dụ:

```python
def main(page: ft.Page):

    count = 0

    text = ft.Text("Count: 0")

    def increment(e):
        nonlocal count

        count += 1
        text.value = f"Count: {count}"

        page.update()

    page.add(
        text,
        ft.Button(
            "+",
            on_click=increment,
        ),
    )


ft.run(main)
```

Đây là pattern cơ bản:

```text
Event
  ↓
State mutation
  ↓
Control mutation
  ↓
page.update()
```

---

# 10. Tại sao phải `nonlocal`?

Đây là Python chứ không riêng Flet.

Ta có:

```python
def main(page):

    count = 0

    def increment(e):
        count += 1
```

Code trên lỗi.

Bởi vì Python xem:

```python
count += 1
```

là assignment vào biến local của `increment()`.

Phải viết:

```python
def increment(e):
    nonlocal count
    count += 1
```

Mental model:

```text
main()
 │
 ├── count
 │
 └── increment()
       │
       └── nonlocal count
```

---

# 11. Một vấn đề của cách trên

Ví dụ:

```python
count = 0

text = ft.Text("Count: 0")

def increment(e):
    nonlocal count
    count += 1
    text.value = f"Count: {count}"
    page.update()
```

Với app nhỏ thì ổn.

Nhưng nếu application lớn:

```text
count
username
loading
error
selected_book
selected_chapter
current_page
settings
...
```

thì event handler sẽ bắt đầu trở nên rất khó quản lý.

Đây chính là lý do chúng ta sẽ học:

```text
State Management
```

ở các buổi sau.

---

# 12. `Page` không phải là toàn bộ Application State

Một lỗi tư duy phổ biến:

> "Tất cả dữ liệu của app cứ nhét vào `page`."

Không nên.

Ví dụ không nên biến `page` thành một "god object":

```python
page.count = ...
page.user = ...
page.books = ...
page.settings = ...
page.database = ...
page.service = ...
```

Thay vào đó:

```text
Application
│
├── State
│
├── Services
│
├── Repositories
│
└── UI
     │
     └── Page
```

Sau này khi kết hợp với Clean Architecture:

```text
                 Flet
                  │
                  ▼
             Presentation
                  │
                  ▼
              Use Cases
                  │
                  ▼
               Domain
                  │
                  ▼
           Infrastructure
                  │
             ┌────┴────┐
             │         │
           SQLite     API
```

---

# 13. Page configuration

Ta có thể cấu hình cửa sổ:

```python
def main(page: ft.Page):

    page.title = "My Application"

    page.window.width = 1000
    page.window.height = 700

    page.add(
        ft.Text("Hello")
    )


ft.run(main)
```

Một số cấu hình thường gặp:

```python
page.title
page.theme
page.dark_mode
```

và các thuộc tính liên quan tới window.

Đừng cố học thuộc tất cả API ngay.

Quan trọng nhất là hiểu:

```text
Page
 ├── Window configuration
 ├── UI tree
 ├── Theme
 ├── Navigation
 ├── Overlay
 └── Update
```

---

# 14. `page.add()` nhiều lần

Ví dụ:

```python
page.add(ft.Text("A"))
page.add(ft.Text("B"))
page.add(ft.Text("C"))
```

Control tree:

```text
Page
├── Text("A")
├── Text("B")
└── Text("C")
```

Tương đương về mặt ý tưởng với:

```python
page.add(
    ft.Text("A"),
    ft.Text("B"),
    ft.Text("C"),
)
```

---

# 15. Container tree

Điểm cực kỳ quan trọng:

`Page` cũng là một node trong UI hierarchy.

Ví dụ:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text("Name"),
            ft.TextField(),
            ft.Button("Save"),
        ]
    )
)
```

Ta có:

```text
Page
└── Column
    ├── Text
    ├── TextField
    └── Button
```

Nếu:

```python
page.add(
    ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Left")
                ]
            ),
            ft.Column(
                controls=[
                    ft.Text("Right")
                ]
            ),
        ]
    )
)
```

thì:

```text
Page
└── Row
    ├── Column
    │   └── Text
    │
    └── Column
        └── Text
```

Đây là **UI Tree**.

---

# 16. Control có parent

Hãy suy nghĩ:

```text
Page
└── Column
    └── Text
```

`Text` không nằm trực tiếp trong Page.

Nó nằm trong:

```text
Column
```

Do đó khi xây UI phức tạp, chúng ta phải hiểu **control hierarchy**.

Ví dụ:

```python
column = ft.Column()

text = ft.Text("Hello")

column.controls.append(text)

page.add(column)
```

Tree:

```text
Page
└── Column
    └── Text
```

---

# 17. Event handler có `page` không?

Thông thường handler nhận event:

```python
def on_click(e):
    ...
```

Event object chứa thông tin event và control liên quan.

Ví dụ:

```python
def on_click(e):
    print(e)
```

Một cách phổ biến là closure:

```python
def main(page: ft.Page):

    def on_click(e):
        page.add(ft.Text("Clicked"))

    page.add(
        ft.Button(
            "Click",
            on_click=on_click,
        )
    )
```

Ở đây `on_click()` có thể truy cập `page` vì Python closure.

```text
main()
 │
 ├── page
 │
 └── on_click()
       │
       └── closure → page
```

---

# 18. Một pattern tốt hơn

Khi app lớn, thay vì handler làm mọi thứ:

```python
def on_click(e):
    ...
    ...
    ...
    ...
    ...
```

ta có thể:

```python
def on_click(e):
    service.do_something()
    render()
```

Sau này sẽ tiến tới:

```text
UI Event
   ↓
Controller / Handler
   ↓
Use Case
   ↓
Domain
   ↓
Repository
```

Đây là cách chúng ta sẽ xây ứng dụng Flet production-style.

---

# 19. `page.update()` — hiểu đúng

Một misconception thường gặp:

> Mỗi lần thay đổi control đều phải gọi `page.update()` ngay.

Không nhất thiết.

Ví dụ:

```python
text.value = "A"
button.text = "B"
container.visible = False

page.update()
```

Có thể gom nhiều thay đổi rồi update một lần.

Mental model:

```text
Change 1 ─┐
Change 2 ─┼──→ update
Change 3 ─┘
```

Thay vì:

```text
Change 1 → update
Change 2 → update
Change 3 → update
```

Đây là tư duy quan trọng cho performance.

---

# 20. Ví dụ Counter chuẩn hơn

```python
import flet as ft


def main(page: ft.Page):
    page.title = "Counter"

    count = 0

    counter_text = ft.Text(
        value="Count: 0",
        size=30,
    )

    def increment(e):
        nonlocal count

        count += 1
        counter_text.value = f"Count: {count}"

        page.update()

    def decrement(e):
        nonlocal count

        if count > 0:
            count -= 1
            counter_text.value = f"Count: {count}"

        page.update()

    page.add(
        ft.Column(
            controls=[
                counter_text,
                ft.Row(
                    controls=[
                        ft.Button(
                            "-",
                            on_click=decrement,
                        ),
                        ft.Button(
                            "+",
                            on_click=increment,
                        ),
                    ]
                ),
            ]
        )
    )


ft.run(main)
```

Architecture hiện tại:

```text
main
│
├── State
│    └── count
│
├── UI
│    └── counter_text
│
├── Event
│    ├── increment
│    └── decrement
│
└── Page
```

Đây là kiến trúc **đủ tốt cho app nhỏ**.

Nhưng chưa phù hợp app lớn.

---

# 21. Một cải tiến nhỏ

Thay vì lặp:

```python
counter_text.value = f"Count: {count}"
```

ta có thể tạo hàm:

```python
def render():
    counter_text.value = f"Count: {count}"
```

Sau đó:

```python
def increment(e):
    nonlocal count

    count += 1
    render()
    page.update()
```

và:

```python
def decrement(e):
    nonlocal count

    if count > 0:
        count -= 1

    render()
    page.update()
```

Mental model:

```text
State
 ↓
render()
 ↓
UI
 ↓
update()
```

Đây là một bước rất quan trọng để tiến tới **reactive architecture**.

---

# 22. Tư duy cần ghi nhớ sau Buổi 2

Đừng chỉ nhớ API.

Hãy nhớ 5 khái niệm này:

### 1. `Page`

Root của UI.

```text
Page
└── ...
```

### 2. Control Tree

UI là một cây.

```text
Page
└── Column
    ├── Text
    └── Button
```

### 3. State

Dữ liệu thay đổi theo thời gian.

```python
count = 0
```

### 4. Event

User tạo ra event.

```text
click
input
change
submit
```

### 5. Update

State/UI thay đổi → đồng bộ UI.

```python
page.update()
```

---

# 23. Mental model tổng hợp

Hãy ghi nhớ sơ đồ này:

```text
                 Application
                     │
                     ▼
                   Page
                     │
                     ▼
                Control Tree
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Text      TextField   Button
                                 │
                                 │ click
                                 ▼
                              Event
                                 │
                                 ▼
                              Handler
                                 │
                                 ▼
                              State
                                 │
                                 ▼
                              Render
                                 │
                                 ▼
                           page.update()
                                 │
                                 ▼
                                UI
```

Đây chính là nền tảng của Flet.

---

# Bài tập Buổi 2

Hãy tự xây **Counter v2** với yêu cầu:

```text
┌──────────────────────────────┐
│          Counter             │
│                              │
│             0                │
│                              │
│       [-]   [+]   Reset      │
│                              │
│       Status: Ready          │
└──────────────────────────────┘
```

Yêu cầu:

1. `+` tăng `count`.
2. `-` giảm `count`.
3. `Reset` đưa count về `0`.
4. Không cho count < `0`.
5. `Status` hiển thị:

   * `Ready` khi `0`
   * `Counting...` khi `> 0`
6. Tạo riêng:

   ```python
   increment()
   decrement()
   reset()
   render()
   ```
7. **Không tạo lại `Text`, `Button`, `Column` mỗi lần click.**
8. Chỉ thay đổi state/control hiện có rồi `page.update()`.

### Thử thách thêm

Thêm:

```text
Count: 0
```

và một `TextField` để user nhập số, sau đó có nút:

```text
[ Set ]
```

Ví dụ:

```text
Count: 15

[ 20        ] [Set]
```

Nếu nhập:

```text
abc
```

thì hiển thị:

```text
Invalid number
```

Nếu nhập:

```text
-10
```

thì hiển thị:

```text
Number must be >= 0
```

**Buổi 3** chúng ta sẽ đi vào một phần rất quan trọng: **Control và UI Tree** — `Text`, `Button`, `TextField`, `Container`, `Row`, `Column`, parent/child, `controls`, và cách Flet xây dựng một giao diện từ một cây object Python.
