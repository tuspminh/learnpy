# Buổi 5 — Layout Deep Dive: `Row`, `Column`, `Container`

Đây là một trong những buổi **quan trọng nhất của Flet Foundation**.

Từ hôm nay, bạn cần bắt đầu chuyển tư duy từ:

> "Tôi có một Button, một Text..."

sang:

> "Tôi đang thiết kế một **layout tree** với các constraint về kích thước, vị trí và không gian."

---

# 1. Layout trong Flet là gì?

Ví dụ:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text("Hello"),
            ft.Button("Save"),
        ]
    )
)
```

Flet phải quyết định:

* Text nằm ở đâu?
* Button nằm ở đâu?
* khoảng cách bao nhiêu?
* Column rộng bao nhiêu?
* Control có được kéo giãn không?
* Khi cửa sổ thay đổi kích thước thì chuyện gì xảy ra?

Đó chính là **layout**.

Mental model:

```text
Page
 │
 ▼
Layout
 │
 ├── Position
 ├── Size
 ├── Alignment
 ├── Spacing
 ├── Padding
 └── Constraints
```

---

# 2. Ba control layout quan trọng nhất

Trong giai đoạn đầu, bạn phải thật sự thành thạo:

```text
Row
Column
Container
```

Có thể xem:

```text
Row       → bố trí ngang
Column    → bố trí dọc
Container → wrapper / kích thước / spacing / decoration
```

---

# 3. `Column`

Cơ bản:

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Mental model:

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

# 4. `Row`

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Mental model:

```text
A   B   C
```

Tree:

```text
Row
├── A
├── B
└── C
```

---

# 5. `Column` và `Row` khác nhau ở đâu?

Rất đơn giản:

```text
Column
    ↓
main axis = vertical
```

```text
Row
    ↓
main axis = horizontal
```

Có thể hình dung:

```text
Column:

┌───────┐
│   A   │
│   B   │
│   C   │
└───────┘
```

và:

```text
Row:

┌───────────────┐
│ A   B   C     │
└───────────────┘
```

---

# 6. `alignment`

Đây là nơi layout bắt đầu thú vị.

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Column:

```text
┌────────────────────┐
│        A           │
│        B           │
└────────────────────┘
```

---

# 7. Main Axis và Cross Axis

Đây là concept bạn nên học thuộc.

## Column

```text
main axis
    ↓

A
B
C

cross axis →
```

## Row

```text
cross axis
    ↓

A → B → C

main axis →
```

Sơ đồ:

```text
Column:

       cross axis
     ←────────────→

         A
         │
         B
         │
         C
         │
         ↓
      main axis
```

Row:

```text
      main axis
  ───────────────→

  A       B       C

  ↑
cross axis
```

Đây là nền tảng để hiểu alignment.

---

# 8. `MainAxisAlignment`

Ví dụ với `Row`:

```python
ft.Row(
    controls=[
        ft.Button("A"),
        ft.Button("B"),
        ft.Button("C"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Kết quả tư duy:

```text
┌──────────────────────────────┐
│       A    B    C            │
└──────────────────────────────┘
```

---

# 9. Các kiểu main alignment

Bạn sẽ thường gặp:

```python
ft.MainAxisAlignment.START
ft.MainAxisAlignment.CENTER
ft.MainAxisAlignment.END
ft.MainAxisAlignment.SPACE_BETWEEN
ft.MainAxisAlignment.SPACE_AROUND
ft.MainAxisAlignment.SPACE_EVENLY
```

Ví dụ:

### `START`

```text
A B C
```

### `CENTER`

```text
      A B C
```

### `END`

```text
              A B C
```

### `SPACE_BETWEEN`

```text
A       B       C
```

### `SPACE_EVENLY`

```text
   A       B       C
```

---

# 10. `Column` cũng dùng main-axis alignment

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Mental model:

```text
┌─────────────┐
│             │
│      A      │
│      B      │
│      C      │
│             │
└─────────────┘
```

---

# 11. Cross Axis

Với `Row`, cross axis là chiều dọc.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
    ],
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Mental model:

```text
┌──────────────────────────┐
│                          │
│      A       B           │
│                          │
└──────────────────────────┘
```

---

# 12. Row: main + cross

```python
ft.Row(
    controls=[
        ...,
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Nghĩ:

```text
Row
│
├── main axis
│     └── alignment
│
└── cross axis
      └── vertical_alignment
```

---

# 13. Column: main + cross

```python
ft.Column(
    controls=[
        ...,
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Nghĩ:

```text
Column
│
├── main axis
│     └── alignment
│
└── cross axis
      └── horizontal_alignment
```

---

# 14. `spacing`

Đây là property cực kỳ hữu ích.

```python
ft.Column(
    controls=[
        ft.Text("Username"),
        ft.TextField(),
        ft.Text("Password"),
        ft.TextField(),
    ],
    spacing=20,
)
```

Tư duy:

```text
Username

        20px

TextField

        20px

Password

        20px

TextField
```

---

# 15. `spacing` không phải `padding`

Đây là điểm rất quan trọng.

### `spacing`

Khoảng cách **giữa children**.

```text
A

spacing

B
```

### `padding`

Khoảng cách **giữa content và biên của container**.

```text
┌──────────────────────┐
│      padding         │
│   ┌──────────────┐   │
│   │   content    │   │
│   └──────────────┘   │
│                      │
└──────────────────────┘
```

---

# 16. `Container`

Ví dụ:

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=20,
)
```

Mental model:

```text
Container
│
├── padding
│
└── content
```

Container cực kỳ hữu ích để tạo "box".

---

# 17. Padding

Có thể viết:

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=20,
)
```

Hoặc dùng các cấu hình padding phù hợp với API phiên bản Flet bạn đang dùng.

Mental model:

```text
Container
┌──────────────────────┐
│                      │
│    ┌────────────┐    │
│    │   Hello    │    │
│    └────────────┘    │
│                      │
└──────────────────────┘
```

---

# 18. `margin`

`margin` tạo khoảng cách bên ngoài control.

Ví dụ tư duy:

```text
       margin
    ←──────────→

 ┌──────────────┐
 │   Container  │
 └──────────────┘
```

Phân biệt:

```text
margin
  ↓
bên ngoài

padding
  ↓
bên trong
```

---

# 19. Width và Height

Container có thể xác định kích thước:

```python
ft.Container(
    width=300,
    height=200,
)
```

Mental model:

```text
300
←────────────→

┌──────────────┐
│              │
│              │ 200
│              │
└──────────────┘
```

---

# 20. Một lỗi tư duy quan trọng

Không nên nghĩ:

> `width=300` luôn có nghĩa control chắc chắn hiển thị đúng 300px trong mọi layout.

Parent có thể đặt constraint.

Ví dụ:

```text
Page
 ↓
Row
 ↓
Container
```

Kích thước thực tế còn phụ thuộc vào layout của parent.

Do đó:

```text
Child size
     +
Parent constraints
     +
Available space
     ↓
Actual layout
```

Đây là lý do layout Flet cần được học theo **tree**, không phải từng control độc lập.

---

# 21. `expand`

Một trong những property quan trọng nhất.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.TextField(expand=True),
        ft.Button("Search"),
    ]
)
```

Mental model:

```text
┌───────────────────────────────────────┐
│ Search input                 [Search] │
└───────────────────────────────────────┘
```

TextField chiếm phần không gian còn lại.

---

# 22. Tư duy `expand`

Không phải:

> "TextField rộng 500px."

Mà:

> "TextField lấy phần không gian còn lại."

Đây là cách xây UI responsive tốt hơn.

```text
Available space
      │
      ├───────────────┐
      │               │
   expand=True      Button
      │
      ▼
 remaining space
```

---

# 23. `expand` trong Column

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Header"),
        ft.Container(
            expand=True,
        ),
        ft.Text("Footer"),
    ]
)
```

Mental model:

```text
┌───────────────────────┐
│ Header                │
│                       │
│                       │
│      flexible         │
│      space            │
│                       │
│ Footer                │
└───────────────────────┘
```

Đây là pattern cực kỳ hữu ích cho:

* Dashboard
* Reader
* Chat
* Log viewer
* File browser

---

# 24. Reader App của bạn

Hãy tưởng tượng app đọc truyện:

```text
┌─────────────────────────────────────┐
│ Header                              │
├─────────────────────────────────────┤
│                                     │
│                                     │
│          Chapter content            │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ Previous                  Next      │
└─────────────────────────────────────┘
```

Ta có thể nghĩ:

```text
Column
├── Header
├── Content(expand=True)
└── Navigation
```

Đây là tư duy layout rất quan trọng.

---

# 25. `Container` làm layout wrapper

Ví dụ:

```python
content = ft.Container(
    expand=True,
    padding=20,
    content=ft.Text("Chapter content"),
)
```

Sau đó:

```python
ft.Column(
    controls=[
        header,
        content,
        footer,
    ],
)
```

Tree:

```text
Column
├── Header
├── Container
│   └── Text
└── Footer
```

---

# 26. Nested layout

Đây là kỹ năng bạn phải thành thạo.

Ví dụ Dashboard:

```python
ft.Column(
    controls=[
        header,

        ft.Row(
            controls=[
                sidebar,

                ft.Container(
                    expand=True,
                    content=content,
                ),
            ],
        ),

        footer,
    ]
)
```

Tree:

```text
Column
├── Header
├── Row
│   ├── Sidebar
│   └── Container
│       └── Content
└── Footer
```

---

# 27. Dashboard thực tế

Hãy hình dung:

```text
┌─────────────────────────────────────────────┐
│                 HEADER                      │
├──────────────┬──────────────────────────────┤
│              │                              │
│   SIDEBAR    │           CONTENT            │
│              │                              │
│              │                              │
│              │                              │
├──────────────┴──────────────────────────────┤
│                 FOOTER                      │
└─────────────────────────────────────────────┘
```

UI tree:

```text
Column
├── Header
├── Row
│   ├── Sidebar
│   └── Content
└── Footer
```

Đây là một layout pattern bạn sẽ sử dụng rất nhiều.

---

# 28. `alignment` + `expand`

Đây là nơi bắt đầu có thể xây UI chuyên nghiệp.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("My App"),
        ft.Container(
            expand=True,
        ),
        ft.Button("Settings"),
    ]
)
```

Mental model:

```text
┌─────────────────────────────────────────┐
│ My App                    [ Settings ]  │
└─────────────────────────────────────────┘
```

Container ở giữa lấy phần còn lại.

Đây là một kỹ thuật cực kỳ hữu ích.

---

# 29. Toolbar

Ví dụ:

```python
toolbar = ft.Row(
    controls=[
        ft.Text(
            "Books",
            size=24,
        ),

        ft.Container(
            expand=True,
        ),

        ft.Button("Add"),
        ft.Button("Refresh"),
    ]
)
```

Kết quả:

```text
Books                         [Add] [Refresh]
```

Bạn sẽ gặp pattern này liên tục trong desktop app.

---

# 30. Search bar

Ví dụ:

```python
search = ft.Row(
    controls=[
        ft.TextField(
            label="Search",
            expand=True,
        ),
        ft.Button("Search"),
    ]
)
```

UI:

```text
┌──────────────────────────────────┐
│ Search                    [Search]│
└──────────────────────────────────┘
```

---

# 31. Card

Một card đơn giản:

```python
card = ft.Container(
    padding=20,
    content=ft.Column(
        controls=[
            ft.Text("Book title"),
            ft.Text("Author"),
            ft.Button("Read"),
        ],
    ),
)
```

Tree:

```text
Container
└── Column
    ├── Title
    ├── Author
    └── Button
```

Sau này chúng ta sẽ học thêm:

* border
* border radius
* shadow
* bgcolor
* theme

để biến nó thành card hoàn chỉnh.

---

# 32. Responsive tư duy từ sớm

Đừng thiết kế:

```text
width = 1200
height = 800
```

cho mọi thứ.

Hãy ưu tiên:

```text
expand
alignment
responsive layout
flexible width
```

Ví dụ:

```python
ft.Row(
    controls=[
        sidebar,
        ft.Container(
            expand=True,
            content=content,
        ),
    ]
)
```

Khi cửa sổ lớn:

```text
Sidebar |                  Content
```

Khi nhỏ:

```text
Sidebar |       Content
```

Phần Content tự lấy không gian còn lại.

---

# 33. `expand` và `width` khác nhau

Đây là câu hỏi bạn nên tự hỏi:

### `width=300`

```text
"Control muốn có kích thước cụ thể."
```

### `expand=True`

```text
"Control muốn sử dụng không gian linh hoạt."
```

Trong ứng dụng responsive:

```text
expand
```

thường hữu ích hơn việc hard-code width.

---

# 34. Một Form đẹp hơn

Ta có:

```python
form = ft.Container(
    width=400,
    padding=30,
    content=ft.Column(
        controls=[
            ft.Text(
                "Login",
                size=30,
            ),

            ft.TextField(
                label="Username",
            ),

            ft.TextField(
                label="Password",
                password=True,
            ),

            ft.Row(
                controls=[
                    ft.Button("Login"),
                    ft.Button("Clear"),
                ],
            ),
        ],
        spacing=15,
    ),
)
```

Tree:

```text
Container
└── Column
    ├── Text
    ├── TextField
    ├── TextField
    └── Row
        ├── Button
        └── Button
```

Đây là layout pattern rất thực tế.

---

# 35. Center một Form

Một cách tư duy là dùng alignment của parent.

Ví dụ:

```python
page.add(
    ft.Column(
        controls=[
            form,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )
)
```

Mental model:

```text
Page
└── Column(expand=True)
    │
    │       Form
    │
    └── centered
```

Đây là pattern thường dùng cho:

* Login
* Register
* Empty state
* Splash screen

---

# 36. Một ví dụ hoàn chỉnh

```python
import flet as ft


def main(page: ft.Page):
    page.title = "Login"

    username = ft.TextField(
        label="Username",
    )

    password = ft.TextField(
        label="Password",
        password=True,
    )

    status = ft.Text(
        "Ready",
    )

    def login(e):
        if not username.value:
            status.value = "Username is required"
        elif not password.value:
            status.value = "Password is required"
        else:
            status.value = "Login successfully"

        page.update()

    def clear(e):
        username.value = ""
        password.value = ""
        status.value = "Ready"

        page.update()

    buttons = ft.Row(
        controls=[
            ft.Button(
                "Login",
                on_click=login,
            ),
            ft.Button(
                "Clear",
                on_click=clear,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    form = ft.Container(
        width=400,
        padding=30,
        content=ft.Column(
            controls=[
                ft.Text(
                    "LOGIN",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                username,
                password,
                buttons,
                status,
            ],
            spacing=15,
        ),
    )

    page.add(
        ft.Column(
            controls=[form],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.run(main)
```

---

# 37. Phân tích Tree

Đừng chỉ nhìn code.

Hãy chuyển thành tree:

```text
Page
└── Column(expand=True)
    └── Container(width=400, padding=30)
        └── Column
            ├── Text("LOGIN")
            ├── TextField(username)
            ├── TextField(password)
            ├── Row
            │   ├── Button(Login)
            │   └── Button(Clear)
            └── Text(status)
```

Đây chính là kỹ năng quan trọng nhất của buổi này.

---

# 38. Phân tích Layout

```text
Page
│
└── Column(expand=True)
      │
      ├── main axis = vertical
      ├── center vertically
      └── center horizontally
             │
             ▼
        Container
        width = 400
        padding = 30
             │
             ▼
          Column
             │
             ├── title
             ├── username
             ├── password
             ├── buttons
             └── status
```

Nếu bạn hiểu được tree này, bạn đã bắt đầu **thực sự hiểu Flet layout**.

---

# 39. Ba câu hỏi phải hỏi khi thiết kế UI

Mỗi khi tạo UI, hãy hỏi:

### Câu 1

**Parent của control này là gì?**

```text
Text
 ↓
Column
```

### Câu 2

**Control này nằm trên main axis hay cross axis?**

```text
Row → horizontal main axis
Column → vertical main axis
```

### Câu 3

**Nó cần kích thước cố định hay flexible?**

```text
width=300
```

hay:

```text
expand=True
```

Chỉ ba câu hỏi này đã giải quyết rất nhiều vấn đề layout.

---

# 40. Anti-pattern: Hard-code mọi thứ

Không nên thiết kế:

```text
Button width = 123
Text left = 243
Container left = 400
```

theo kiểu absolute positioning cho toàn bộ UI.

Flet nên được tư duy theo:

```text
Parent
 ↓
Layout
 ↓
Available space
 ↓
Child constraints
```

---

# 41. Anti-pattern: quá nhiều Container

Bạn có thể gặp code:

```text
Container
└── Container
    └── Container
        └── Container
            └── Column
```

Không phải cứ thêm Container là layout tốt.

Hãy dùng Container khi thực sự cần:

* padding
* margin
* size
* background
* border
* decoration
* alignment
* wrapper

Nếu chỉ cần xếp children:

```text
Column / Row
```

thường phù hợp hơn.

---

# 42. Mental Model cuối buổi

Hãy nhớ:

```text
                 Layout
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
       Row       Column    Container
        │          │          │
    horizontal   vertical    wrapper
        │          │          │
        └──────────┼──────────┘
                   ▼
             Available Space
                   │
          ┌────────┴────────┐
          ▼                 ▼
      fixed size        flexible
      width/height      expand
```

Và:

```text
Row
 ├── Main Axis     → horizontal
 └── Cross Axis    → vertical

Column
 ├── Main Axis     → vertical
 └── Cross Axis    → horizontal
```

---

# Bài tập Buổi 5 — Dashboard Layout

Hãy xây layout sau:

```text
┌─────────────────────────────────────────────────────┐
│ My Library                         [Search] [⚙]    │
├────────────────┬────────────────────────────────────┤
│                │                                    │
│  Dashboard     │                                    │
│  Books         │             CONTENT                │
│  History       │                                    │
│  Favorites     │                                    │
│                │                                    │
│                │                                    │
├────────────────┴────────────────────────────────────┤
│ Status: Ready                                       │
└─────────────────────────────────────────────────────┘
```

UI Tree bắt buộc:

```text
Page
└── Column(expand=True)
    ├── Header
    │   └── Row
    │       ├── Title
    │       ├── flexible space
    │       ├── Search
    │       └── Settings
    │
    ├── Body(expand=True)
    │   └── Row
    │       ├── Sidebar
    │       └── Content(expand=True)
    │
    └── Footer
```

### Yêu cầu kỹ thuật

* `Page` phải sử dụng `expand=True` cho vùng cần co giãn.
* Header nằm trên cùng.
* Footer nằm dưới cùng.
* Body chiếm phần còn lại.
* Sidebar có width tương đối cố định.
* Content lấy toàn bộ không gian còn lại.
* Header sử dụng một flexible space để đẩy Search/Settings sang phải.
* Không dùng tọa độ tuyệt đối.
* Không dùng `page.clean()` để layout lại.

### Thử thách nâng cao

Tạo hàm:

```python
build_header()
build_sidebar()
build_content()
build_footer()
build_layout()
```

để cuối cùng chỉ còn:

```python
page.add(
    build_layout()
)
```

Đây chính là bước chuyển từ **viết UI trực tiếp** sang **component-based UI architecture**.

---

## Tiếp theo — Buổi 6

Sau khi đã hiểu `Row`, `Column`, `Container`, chúng ta sẽ đi vào **Responsive Layout**: `expand`, `expand_loose`, `ResponsiveRow`, breakpoint, kích thước cửa sổ, adaptive UI và cách thiết kế một giao diện **desktop/tablet/mobile** bằng cùng một codebase. Đây là phần đặc biệt hữu ích nếu bạn muốn dùng Flet để làm **TTS app, Novel Reader và Crawler Dashboard**.
