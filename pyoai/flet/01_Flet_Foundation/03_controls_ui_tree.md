# Buổi 3 — Controls và UI Tree trong Flet

Buổi này rất quan trọng. Nếu Buổi 2 giúp bạn hiểu **`Page`**, thì hôm nay chúng ta sẽ hiểu **UI của Flet thực sự được cấu tạo như thế nào**.

Mục tiêu:

* Hiểu `Control`
* Hiểu `parent / child`
* Hiểu `controls`
* Hiểu UI Tree
* Phân biệt container và leaf control
* Hiểu cách tổ chức UI
* Hiểu vì sao `Row`, `Column`, `Container` quan trọng
* Tự xây một UI có cấu trúc rõ ràng

---

# 1. Flet UI không phải là HTML

Nếu bạn từng học web, có thể bạn sẽ nghĩ:

```html
<div>
    <button>Save</button>
</div>
```

Flet không hoạt động theo kiểu bạn viết markup.

Bạn tạo **Python objects**:

```python
container = ft.Container(
    content=ft.Button("Save")
)
```

Tức là:

```text
Python Object
      ↓
Flet Control
      ↓
UI Tree
      ↓
Rendered UI
```

Đây là tư duy đầu tiên cần nhớ.

---

# 2. Control là gì?

Trong Flet, UI được xây dựng từ các **Control**.

Ví dụ:

```python
ft.Text("Hello")
ft.Button("Save")
ft.TextField()
ft.Image(...)
ft.Container(...)
ft.Row(...)
ft.Column(...)
```

Có thể hình dung:

```text
Control
│
├── Text
├── Button
├── TextField
├── Image
├── Container
├── Row
├── Column
└── ...
```

Mỗi control đại diện cho một thành phần UI.

---

# 3. Leaf Control và Container Control

Một cách phân loại rất hữu ích:

## Leaf Control

Control chủ yếu hiển thị một nội dung và không chứa nhiều control con.

Ví dụ:

```python
ft.Text("Hello")
```

hoặc:

```python
ft.Button("Save")
```

Mental model:

```text
Text
└── no children
```

---

## Container / Parent Control

Control có thể chứa control khác.

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Name"),
        ft.TextField(),
    ]
)
```

Tree:

```text
Column
├── Text
└── TextField
```

Đây là khái niệm cực kỳ quan trọng.

---

# 4. UI Tree

Hãy xem:

```python
import flet as ft


def main(page: ft.Page):
    page.add(
        ft.Column(
            controls=[
                ft.Text("Username"),
                ft.TextField(),
                ft.Button("Login"),
            ]
        )
    )


ft.run(main)
```

UI Tree:

```text
Page
└── Column
    ├── Text
    ├── TextField
    └── Button
```

Đây chính là cấu trúc UI.

---

# 5. Tree sâu hơn

Ví dụ:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text("Login"),

            ft.Row(
                controls=[
                    ft.TextField(),
                    ft.Button("Login"),
                ]
            ),
        ]
    )
)
```

Cây:

```text
Page
└── Column
    ├── Text
    └── Row
        ├── TextField
        └── Button
```

Nếu thêm `Container`:

```python
page.add(
    ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Login"),
                ft.Row(
                    controls=[
                        ft.TextField(),
                        ft.Button("Login"),
                    ]
                ),
            ]
        )
    )
)
```

thì:

```text
Page
└── Container
    └── Column
        ├── Text
        └── Row
            ├── TextField
            └── Button
```

---

# 6. `controls` là gì?

Một số control có thuộc tính:

```python
controls=[...]
```

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Ta có:

```text
Column
├── A
├── B
└── C
```

`controls` chính là collection các child controls.

---

# 7. `Column`

`Column` sắp xếp control theo chiều dọc.

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Kết quả tư duy:

```text
A

B

C
```

Tree:

```text
Column
├── A
├── B
└── C
```

---

# 8. `Row`

`Row` sắp xếp theo chiều ngang.

```python
ft.Row(
    controls=[
        ft.Button("Save"),
        ft.Button("Cancel"),
    ]
)
```

Tư duy:

```text
[ Save ] [ Cancel ]
```

Tree:

```text
Row
├── Button
└── Button
```

---

# 9. Kết hợp `Row` + `Column`

Đây là pattern bạn sẽ sử dụng **rất nhiều**.

```python
ft.Column(
    controls=[
        ft.Text("User"),

        ft.Row(
            controls=[
                ft.Button("Save"),
                ft.Button("Cancel"),
            ]
        ),
    ]
)
```

Tree:

```text
Column
├── Text
└── Row
    ├── Button
    └── Button
```

Mental model:

```text
User

[ Save ] [ Cancel ]
```

---

# 10. `Container`

`Container` thường dùng để:

* bọc content
* padding
* margin
* background
* border
* border radius
* alignment
* kích thước

Ví dụ:

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=20,
)
```

Tree:

```text
Container
└── Text
```

---

# 11. Container không giống Column

Đây là lỗi người mới hay gặp.

### Container

Thông thường chứa một `content`:

```python
ft.Container(
    content=...
)
```

### Column

Chứa nhiều `controls`:

```python
ft.Column(
    controls=[
        ...,
        ...,
        ...,
    ]
)
```

So sánh:

```text
Container
└── content
```

với:

```text
Column
├── child
├── child
└── child
```

---

# 12. Container + Column

Thường chúng ta sẽ viết:

```python
ft.Container(
    padding=20,
    content=ft.Column(
        controls=[
            ft.Text("Login"),
            ft.TextField(),
            ft.Button("Login"),
        ]
    )
)
```

Tree:

```text
Container
└── Column
    ├── Text
    ├── TextField
    └── Button
```

Đây là một UI pattern cơ bản nhưng cực kỳ quan trọng.

---

# 13. Tạo UI từng bước

Đừng lúc nào cũng viết một expression khổng lồ:

```python
page.add(
    ft.Container(
        content=ft.Column(
            controls=[
                ...
            ]
        )
    )
)
```

Khi UI lớn, nên tách object:

```python
title = ft.Text("Login")

username = ft.TextField(
    label="Username",
)

password = ft.TextField(
    label="Password",
    password=True,
)

login_button = ft.Button(
    "Login",
)

form = ft.Column(
    controls=[
        title,
        username,
        password,
        login_button,
    ]
)

container = ft.Container(
    content=form,
    padding=20,
)

page.add(container)
```

Tree:

```text
Page
└── Container
    └── Column
        ├── Text
        ├── TextField
        ├── TextField
        └── Button
```

Ưu điểm cực lớn:

```python
username.value
password.value
login_button.disabled
```

có thể được truy cập từ event handler.

---

# 14. Đây là lý do không nên tạo lại UI

Ví dụ không tốt:

```python
def on_click(e):
    page.clean()

    page.add(
        ft.Text("Clicked")
    )
```

Mỗi lần click bạn lại tạo UI mới.

Với app lớn, điều này dễ dẫn đến:

* mất state
* mất reference
* logic khó kiểm soát
* khó maintain
* event handler khó quản lý

Thay vào đó:

```python
text = ft.Text("Ready")


def on_click(e):
    text.value = "Clicked"
    page.update()
```

UI vẫn là object cũ:

```text
Text object
     │
     ├── value = "Ready"
     │
     └── value = "Clicked"
```

---

# 15. Object identity

Đây là một khái niệm Python rất quan trọng.

```python
text = ft.Text("Hello")
```

`text` là một object.

Khi:

```python
text.value = "World"
```

ta **không tạo Text mới**.

Ta sửa object cũ.

```text
Text object
    │
    └── value
         │
         ├── before: Hello
         └── after:  World
```

Sau đó:

```python
page.update()
```

để đồng bộ thay đổi.

---

# 16. UI Tree và Python references

Ví dụ:

```python
text = ft.Text("Hello")

column = ft.Column(
    controls=[text]
)

page.add(column)
```

Có hai mối quan hệ:

```text
Python reference:

text ──────────────┐
                   │
                   ▼
                Text object
                   ▲
                   │
column.controls ───┘
```

và UI Tree:

```text
Page
└── Column
    └── Text
```

Đây là một điểm rất quan trọng khi làm Flet.

Bạn vừa có:

1. **Object graph**
2. **UI tree**

Hai khái niệm này liên quan nhưng không hoàn toàn giống nhau.

---

# 17. Ví dụ thực tế

Ta xây Login UI:

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

    message = ft.Text()

    def login(e):
        if not username.value:
            message.value = "Username is required"
        elif not password.value:
            message.value = "Password is required"
        else:
            message.value = "Login successfully"

        page.update()

    login_button = ft.Button(
        "Login",
        on_click=login,
    )

    form = ft.Column(
        controls=[
            ft.Text("Login"),
            username,
            password,
            login_button,
            message,
        ]
    )

    page.add(
        ft.Container(
            content=form,
            padding=20,
        )
    )


ft.run(main)
```

UI Tree:

```text
Page
└── Container
    └── Column
        ├── Text("Login")
        ├── TextField(username)
        ├── TextField(password)
        ├── Button
        └── Text(message)
```

Event:

```text
Button
   │
   ▼
login()
   │
   ├── username.value
   ├── password.value
   │
   ▼
message.value
   │
   ▼
page.update()
```

---

# 18. Một nguyên tắc kiến trúc quan trọng

Đừng nghĩ:

> Flet app = một file chứa toàn bộ UI.

Ngay từ bây giờ hãy tập tư duy:

```text
Application
│
├── Page
│
├── View
│
├── Components
│
├── State
│
├── Services
│
└── Repository
```

Ví dụ app đọc truyện sau này:

```text
Page
│
└── MainLayout
    │
    ├── NavigationRail
    │
    └── Content
        │
        ├── LibraryView
        ├── BookDetailView
        ├── ChapterListView
        └── ReaderView
```

Mỗi View lại có tree riêng.

---

# 19. UI Tree của ứng dụng đọc truyện

Ví dụ:

```text
Page
│
└── Row
    │
    ├── NavigationRail
    │
    └── Column
        │
        ├── AppBar
        │
        └── Content
            │
            └── ReaderView
                │
                ├── BookTitle
                ├── ChapterTitle
                ├── Content
                └── Navigation
                    ├── Previous
                    └── Next
```

Đây chính là cách bạn nên bắt đầu suy nghĩ về UI.

Không phải:

> "Tôi cần một Button."

Mà:

> "Button nằm ở đâu trong UI Tree? Nó thuộc component nào? Nó thay đổi state nào?"

Đây là sự khác biệt giữa **học Flet** và **thiết kế ứng dụng bằng Flet**.

---

# 20. Component boundary

Giả sử có:

```text
Page
└── Column
    ├── Header
    ├── Search
    ├── List
    └── Footer
```

Đừng nhất thiết viết thành một hàm 500 dòng.

Có thể chia:

```python
def build_header():
    ...


def build_search():
    ...


def build_list():
    ...


def build_footer():
    ...
```

Sau đó:

```python
page.add(
    ft.Column(
        controls=[
            build_header(),
            build_search(),
            build_list(),
            build_footer(),
        ]
    )
)
```

Đây là bước đầu tiên để tiến tới **Component Architecture**.

---

# 21. Function component đơn giản

Ví dụ:

```python
def create_header():
    return ft.Row(
        controls=[
            ft.Text(
                "My App",
                size=24,
            ),
            ft.Button("Settings"),
        ]
    )
```

Sau đó:

```python
page.add(
    ft.Column(
        controls=[
            create_header(),
        ]
    )
)
```

Mental model:

```text
create_header()
       │
       ▼
     Row
    /   \
 Text   Button
```

---

# 22. Component có state

Ví dụ Counter:

```python
def create_counter(page: ft.Page):

    count = 0

    text = ft.Text("0")

    def increment(e):
        nonlocal count

        count += 1
        text.value = str(count)
        page.update()

    return ft.Column(
        controls=[
            text,
            ft.Button(
                "+",
                on_click=increment,
            ),
        ]
    )
```

Sau đó:

```python
page.add(
    create_counter(page)
)
```

Đây là một pattern rất thú vị:

```text
create_counter()
      │
      ├── state
      ├── event handlers
      └── controls
```

Nó chính là tiền đề để chúng ta học **Custom Control / reusable component** sau này.

---

# 23. `Column` + `Row` là nền tảng

Bạn có thể xây phần lớn UI cơ bản bằng:

```text
Column
Row
Container
```

Ví dụ:

```text
Container
└── Column
    ├── Row
    │   ├── Logo
    │   └── Button
    │
    ├── Row
    │   ├── Sidebar
    │   └── Content
    │
    └── Footer
```

Đây là lý do chúng ta sẽ học layout rất sâu ở giai đoạn tiếp theo.

---

# 24. Sai lầm phổ biến #1

Viết UI quá sâu trong một expression:

```python
page.add(
    ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(...),
                        ft.Button(...),
                    ]
                )
            ]
        )
    )
)
```

Không sai về kỹ thuật.

Nhưng nếu UI lớn, rất khó đọc.

Tốt hơn:

```python
header = create_header()
content = create_content()
footer = create_footer()

layout = ft.Column(
    controls=[
        header,
        content,
        footer,
    ]
)

page.add(layout)
```

---

# 25. Sai lầm phổ biến #2

Tạo lại toàn bộ UI:

```python
def refresh():
    page.clean()
    page.add(build_ui())
```

App nhỏ có thể chạy.

Nhưng khi application lớn:

```text
State
Events
References
Async tasks
Forms
Navigation
```

sẽ bắt đầu phức tạp.

Chúng ta sẽ học cách cập nhật **state/control hiện tại** thay vì luôn rebuild toàn bộ Page.

---

# 26. Sai lầm phổ biến #3

Nhét business logic vào UI:

```python
def on_save(e):
    # validate
    # database
    # API
    # business rule
    # file system
    # update UI
    ...
```

Đây là một anti-pattern.

Về sau nên hướng tới:

```text
Button
  ↓
Event Handler
  ↓
Use Case
  ↓
Service
  ↓
Repository
```

Ví dụ:

```python
def on_save(e):
    result = create_book_use_case.execute(...)
    update_ui(result)
```

Đây sẽ kết nối trực tiếp với những gì bạn đã học về:

* Repository Pattern
* Clean Architecture
* DDD
* Model
* Service
* Use Case

---

# 27. Tổng kết Buổi 3

Bạn cần nắm chắc sơ đồ này:

```text
                    Page
                     │
                     ▼
               Control Tree
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Container       Column         Row
       │             │             │
       ▼             ▼             ▼
    content       controls       controls
                     │
              ┌──────┼──────┐
              ▼      ▼      ▼
             Text  Button TextField
```

Và lifecycle cơ bản:

```text
Create controls
      ↓
Build tree
      ↓
Add to Page
      ↓
Render
      ↓
User event
      ↓
Change state/control
      ↓
page.update()
      ↓
UI updated
```

---

# Bài tập Buổi 3 — Login UI

Hãy xây UI sau:

```text
┌─────────────────────────────────────┐
│                                     │
│              LOGIN                  │
│                                     │
│  Username                           │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  Password                           │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│          [ Login ]                  │
│                                     │
│       Status: Ready                │
│                                     │
└─────────────────────────────────────┘
```

Yêu cầu kiến trúc:

```text
Page
└── Container
    └── Column
        ├── Title
        ├── Username
        ├── Password
        ├── Login Button
        └── Status
```

Tạo riêng các object:

```python
title
username
password
login_button
status
```

Không tạo lại chúng khi click.

Handler chỉ được phép:

```text
đọc input
   ↓
thay đổi state/UI
   ↓
page.update()
```

**Thử thách:** thêm một `Row` chứa hai nút:

```text
[ Login ] [ Clear ]
```

Trong đó `Clear` xóa username/password và đưa `Status` về `Ready`.

---

## Buổi 4

Tiếp theo chúng ta sẽ học **`Text`, `Button`, `TextField`, `Image` và các control cơ bản một cách deep dive**: properties, event, value, disabled, visible, styling, reference tới control và cách xây **Form UI thực tế**.
