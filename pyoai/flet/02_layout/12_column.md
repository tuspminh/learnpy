# Buổi 12 — `Column` Deep Dive

Hôm nay chúng ta học sâu `Column`.

Nếu `Row` là nền tảng của **layout ngang**, thì `Column` là nền tảng của **layout dọc**.

```text
Row
→ → → →

Column
↓
↓
↓
```

Mục tiêu buổi này không chỉ là biết dùng `Column`, mà phải hiểu:

* Main Axis / Cross Axis
* `alignment`
* `horizontal_alignment`
* `spacing`
* `expand`
* `scroll`
* `wrap`
* nested `Column`
* `Row + Column`
* sizing và constraints
* các pattern UI thực tế

---

# 1. `Column` là gì?

`Column` sắp xếp các control con theo **chiều dọc**.

```python
ft.Column(
    controls=[
        ft.Text("Name"),
        ft.TextField(),
        ft.Button("Save"),
    ]
)
```

Concept:

```text
┌──────────────────────┐
│ Name                 │
│                      │
│ [ TextField       ]  │
│                      │
│ [ Save ]             │
└──────────────────────┘
```

UI Tree:

```text
Column
├── Text
├── TextField
└── Button
```

---

# 2. `Column` là đối tác của `Row`

Nhớ:

```text
Row
→ Main Axis: horizontal
→ Cross Axis: vertical
```

Còn:

```text
Column
↓ Main Axis: vertical
→ Cross Axis: horizontal
```

Đây là kiến thức cực kỳ quan trọng.

---

# 3. Main Axis của `Column`

Với:

```python
ft.Column(...)
```

Main Axis là:

```text
vertical
```

```text
        Main Axis
            ↓
            │
            │
            │
            ↓
```

Do đó:

```python
alignment=...
```

sẽ điều khiển **vị trí theo chiều dọc**.

---

# 4. Cross Axis của `Column`

Cross Axis là:

```text
horizontal
```

```text
←──────────────→
 Cross Axis
```

Do đó:

```python
horizontal_alignment=...
```

điều khiển vị trí theo chiều ngang.

---

# 5. So sánh Row và Column

|                 | Row                  | Column                 |
| --------------- | -------------------- | ---------------------- |
| Main Axis       | ngang                | dọc                    |
| Cross Axis      | dọc                  | ngang                  |
| Main alignment  | `alignment`          | `alignment`            |
| Cross alignment | `vertical_alignment` | `horizontal_alignment` |
| `spacing`       | giữa children        | giữa children          |

Hãy thuộc bảng này.

---

# 6. Column cơ bản

```python
import flet as ft


def main(page: ft.Page):

    page.add(
        ft.Column(
            controls=[
                ft.Text("Hello"),
                ft.Text("Flet"),
                ft.Button("Learn"),
            ]
        )
    )


ft.run(main)
```

Concept:

```text
Hello

Flet

[ Learn ]
```

---

# 7. `spacing`

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
    spacing=20,
)
```

Concept:

```text
A

      20px

B

      20px

C
```

---

# 8. `spacing` không phải `padding`

Giống `Row`.

```text
spacing
↓
A
     khoảng cách
B
```

Còn padding:

```text
┌──────────────────────┐
│ padding              │
│   A                  │
│   B                  │
└──────────────────────┘
```

`spacing` thuộc về **layout giữa children**.

`padding` thuộc về **khoảng cách nội bộ container/control**.

---

# 9. `alignment`

Ví dụ:

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

Vì Column có Main Axis là vertical:

```text
alignment=CENTER
```

→ children được căn giữa **theo chiều dọc**.

---

# 10. `START`

```python
alignment=ft.MainAxisAlignment.START
```

```text
┌─────────────────────┐
│ A                   │
│ B                   │
│ C                   │
│                     │
│                     │
└─────────────────────┘
```

---

# 11. `CENTER`

```python
alignment=ft.MainAxisAlignment.CENTER
```

```text
┌─────────────────────┐
│                     │
│                     │
│ A                   │
│ B                   │
│ C                   │
│                     │
└─────────────────────┘
```

---

# 12. `END`

```python
alignment=ft.MainAxisAlignment.END
```

```text
┌─────────────────────┐
│                     │
│                     │
│                     │
│ A                   │
│ B                   │
│ C                   │
└─────────────────────┘
```

---

# 13. `SPACE_BETWEEN`

```python
ft.Column(
    controls=[
        ft.Text("Header"),
        ft.Text("Content"),
        ft.Text("Footer"),
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
)
```

Concept:

```text
┌──────────────────────┐
│ Header               │
│                      │
│                      │
│ Content              │
│                      │
│                      │
│ Footer               │
└──────────────────────┘
```

Đây là pattern rất hữu ích khi xây:

* sidebar
* settings
* dashboard
* page layout

---

# 14. `SPACE_AROUND`

```python
alignment=ft.MainAxisAlignment.SPACE_AROUND
```

Khoảng trống được phân bố xung quanh các child.

Concept:

```text
┌──────────────────────┐
│                      │
│ Header               │
│                      │
│ Content              │
│                      │
│ Footer               │
│                      │
└──────────────────────┘
```

---

# 15. `SPACE_EVENLY`

```python
alignment=ft.MainAxisAlignment.SPACE_EVENLY
```

Khoảng cách giữa:

```text
top → A
A → B
B → C
C → bottom
```

được phân phối đều.

---

# 16. `horizontal_alignment`

Đây là điểm khác biệt quan trọng so với `Row`.

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Column:

```text
Main Axis
↓
```

Cross Axis:

```text
←────────→
```

Vì vậy:

```python
horizontal_alignment
```

→ căn children theo chiều ngang.

---

# 17. `START`

```python
horizontal_alignment=ft.CrossAxisAlignment.START
```

```text
┌──────────────────────┐
│ A                    │
│ B                    │
│ C                    │
└──────────────────────┘
```

---

# 18. `CENTER`

```python
horizontal_alignment=ft.CrossAxisAlignment.CENTER
```

```text
┌──────────────────────┐
│          A           │
│          B           │
│          C           │
└──────────────────────┘
```

---

# 19. `END`

```python
horizontal_alignment=ft.CrossAxisAlignment.END
```

```text
┌──────────────────────┐
│                    A │
│                    B │
│                    C │
└──────────────────────┘
```

---

# 20. `Column` muốn căn giữa hoàn toàn

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Hello"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Concept:

```text
┌──────────────────────────┐
│                          │
│                          │
│          Hello           │
│                          │
│                          │
└──────────────────────────┘
```

Nhưng một lần nữa:

> Column phải có đủ không gian để alignment có tác dụng.

---

# 21. `expand`

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Hello"),
    ],
    expand=True,
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Column muốn chiếm không gian dọc được phép.

Khi đó:

```text
┌──────────────────────┐
│                      │
│                      │
│        Hello         │
│                      │
│                      │
└──────────────────────┘
```

---

# 22. `Column(expand=True)` và `alignment`

Đây là một pattern cực kỳ quan trọng.

```python
content = ft.Column(
    controls=[
        ft.Text("Welcome"),
    ],
    expand=True,
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Bạn đang nói:

```text
Column:
    hãy lấy không gian có thể
    ↓
children:
    đặt giữa không gian đó
```

---

# 23. `Column` trong `Row`

Đây là pattern cực kỳ phổ biến.

```python
ft.Row(
    controls=[
        ft.Column(
            controls=[
                ft.Text("Title"),
                ft.Text("Description"),
            ]
        ),

        ft.Button("Action"),
    ]
)
```

Concept:

```text
┌────────────────────────────────────┐
│ Title                 [Action]     │
│ Description                        │
└────────────────────────────────────┘
```

Tree:

```text
Row
├── Column
│   ├── Text
│   └── Text
└── Button
```

---

# 24. Đây là pattern UI quan trọng

Rất nhiều UI có dạng:

```text
Row
├── Column
│   ├── Title
│   └── Subtitle
└── Actions
```

Ví dụ list item:

```text
┌────────────────────────────────────────┐
│ Python                 [Edit] [Delete] │
│ Learn Python deeply                    │
└────────────────────────────────────────┘
```

Code:

```python
ft.Row(
    controls=[
        ft.Column(
            controls=[
                ft.Text("Python"),
                ft.Text("Learn Python deeply"),
            ],
            expand=True,
        ),
        ft.Button("Edit"),
        ft.Button("Delete"),
    ]
)
```

---

# 25. `Column` + `Row` là nền tảng của UI

Ví dụ:

```text
Page
│
└── Column
    │
    ├── Row → Header
    │
    ├── Row → Toolbar
    │
    └── Row → Content
```

Hoặc:

```text
Page
│
└── Row
    ├── Column → Sidebar
    └── Column → Main
```

Khi bạn hiểu hai control này, bạn đã nắm được nền tảng layout của Flet.

---

# 26. `Column` làm Form

Một form thường là:

```python
form = ft.Column(
    controls=[
        ft.TextField(label="Username"),
        ft.TextField(label="Password"),
        ft.Button("Login"),
    ],
    spacing=15,
)
```

Concept:

```text
Username
[....................]

Password
[....................]

[ Login ]
```

---

# 27. Form thực tế

```python
form = ft.Column(
    controls=[
        ft.Text(
            "Login",
            size=28,
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
                ft.Checkbox(
                    label="Remember me",
                ),
                ft.TextButton("Forgot password?"),
            ],
        ),

        ft.Button("Login"),
    ],
    spacing=15,
)
```

Tree:

```text
Column
├── Text
├── TextField
├── TextField
├── Row
│   ├── Checkbox
│   └── TextButton
└── Button
```

Đây là UI composition thực tế.

---

# 28. `Column` và `expand` của child

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

Concept:

```text
┌────────────────────────────┐
│ Header                     │
│                            │
│                            │
│     Flexible Content       │
│                            │
│                            │
│ Footer                     │
└────────────────────────────┘
```

Child `expand=True` nhận phần không gian còn lại.

Đây là pattern cực kỳ hữu ích.

---

# 29. Layout Header / Content / Footer

Một app thường có:

```text
┌─────────────────────────────┐
│ Header                      │
├─────────────────────────────┤
│                             │
│ Content                     │
│                             │
├─────────────────────────────┤
│ Footer                      │
└─────────────────────────────┘
```

Có thể tư duy:

```python
ft.Column(
    controls=[
        header,
        content,
        footer,
    ]
)
```

Trong đó `content`:

```python
expand=True
```

---

# 30. Ví dụ

```python
layout = ft.Column(
    controls=[
        ft.Container(
            content=ft.Text("HEADER"),
            height=60,
        ),

        ft.Container(
            content=ft.Text("CONTENT"),
            expand=True,
        ),

        ft.Container(
            content=ft.Text("FOOTER"),
            height=40,
        ),
    ],
    expand=True,
)
```

Concept:

```text
Header → fixed
Content → flexible
Footer → fixed
```

Đây là một pattern layout cực kỳ quan trọng.

---

# 31. `Column` và Sidebar

Sidebar thường:

```text
┌──────────────────┐
│ Logo             │
│                  │
│ Dashboard        │
│ Users            │
│ Settings         │
│                  │
│                  │
│ Logout           │
└──────────────────┘
```

Có thể:

```python
sidebar = ft.Column(
    controls=[
        logo,

        ft.TextButton("Dashboard"),
        ft.TextButton("Users"),
        ft.TextButton("Settings"),

        ft.Container(
            expand=True,
        ),

        ft.TextButton("Logout"),
    ],
)
```

Child `expand=True` tạo khoảng trống đẩy Logout xuống dưới.

Đây là một pattern bạn nên ghi nhớ.

---

# 32. Spacer Pattern

Trong nhiều UI framework có khái niệm:

```text
Spacer
```

Flet có thể đạt hiệu ứng tương tự bằng:

```python
ft.Container(expand=True)
```

Ví dụ:

```python
ft.Column(
    controls=[
        top,
        ft.Container(expand=True),
        bottom,
    ]
)
```

Kết quả:

```text
TOP


                BOTTOM
```

Đây là kỹ thuật layout rất mạnh.

---

# 33. `Column` với danh sách dài

Nếu:

```python
ft.Column(
    controls=[
        item1,
        item2,
        item3,
        ...
        item1000,
    ]
)
```

thì đây không phải lựa chọn tốt cho một danh sách lớn.

Khi có dữ liệu:

```text
100
1,000
10,000
items
```

hãy nghĩ đến:

```python
ft.ListView(...)
```

Chúng ta sẽ học `ListView` ở **Buổi 17**.

---

# 34. `scroll`

Nếu Column chứa nhiều nội dung, có thể bật scrolling.

Ví dụ:

```python
ft.Column(
    controls=[
        ...
    ],
    scroll=ft.ScrollMode.AUTO,
)
```

Concept:

```text
┌──────────────────────┐
│ Item 1               │
│ Item 2               │
│ Item 3               │
│ Item 4               │
│ Item 5               │
│                 ║    │
│                 ║ ↓  │
└──────────────────────┘
```

---

# 35. `scroll` và `ListView`

Đừng nhầm:

### Column + scroll

Phù hợp:

```text
form dài
settings page
article
document
static content
```

### ListView

Phù hợp:

```text
chat
logs
todos
database records
large list
```

Tư duy:

```text
Column + scroll
→ page/document

ListView
→ collection/list
```

---

# 36. `auto_scroll`

Trong những UI dạng log/chat, bạn có thể gặp nhu cầu:

```text
new message
↓
scroll xuống cuối
```

Flet có cơ chế auto scrolling cho các scrollable controls.

Ví dụ concept:

```python
ft.Column(
    controls=[],
    scroll=ft.ScrollMode.AUTO,
    auto_scroll=True,
)
```

Đặc biệt hữu ích cho:

```text
terminal
log viewer
chat
streaming output
```

---

# 37. `wrap`

Với Column, `wrap` không phải trọng tâm như Row.

Nếu bạn muốn:

```text
A B C
D E F
```

thì thường bạn đang nghĩ tới:

```python
ft.Row(wrap=True)
```

Còn:

```text
A
B
C
D
```

thì:

```python
ft.Column(...)
```

---

# 38. Column nested Column

Có thể:

```python
ft.Column(
    controls=[
        ft.Column(
            controls=[
                ft.Text("Section 1"),
                ft.Text("Content"),
            ]
        ),

        ft.Column(
            controls=[
                ft.Text("Section 2"),
                ft.Text("Content"),
            ]
        ),
    ]
)
```

Nhưng không nên lạm dụng.

Tốt hơn:

```python
def build_section(title, content):
    return ft.Column(...)
```

---

# 39. Component hóa

Thay vì:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text(...),
            ft.TextField(...),
            ft.Button(...),
            ft.Row(...),
            ...
        ]
    )
)
```

hãy:

```python
def build_login_form():
    return ft.Column(
        controls=[
            ...
        ]
    )
```

Sau đó:

```python
page.add(
    build_login_form()
)
```

Đây là bước chuyển từ:

```text
UI script
```

sang:

```text
UI architecture
```

---

# 40. `Column` + `Container`

Ví dụ card:

```python
card = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text(
                "Python",
                size=22,
            ),
            ft.Text(
                "Learn Python deeply",
            ),
            ft.Button("Open"),
        ],
        spacing=10,
    ),
    padding=20,
)
```

Phân chia trách nhiệm:

```text
Container
→ visual box
→ padding
→ background
→ border

Column
→ vertical arrangement
```

Đây là cách thiết kế rất tốt.

---

# 41. Column + Row + Container

Một card thực tế:

```text
┌──────────────────────────────────────┐
│ Python                               │
│ Learn Python deeply                  │
│                                      │
│ 100 lessons           [Open]         │
└──────────────────────────────────────┘
```

Tree:

```text
Container
└── Column
    ├── Text
    ├── Text
    └── Row
        ├── Text
        └── Button
```

Code:

```python
card = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text(
                "Python",
                size=22,
            ),

            ft.Text(
                "Learn Python deeply",
            ),

            ft.Row(
                controls=[
                    ft.Text("100 lessons"),
                    ft.Button("Open"),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ],
        spacing=10,
    ),
    padding=20,
)
```

Đây chính là composition.

---

# 42. `Column` và `TextField`

Một lỗi thường gặp:

```python
ft.Column(
    controls=[
        ft.TextField(),
        ft.TextField(),
        ft.TextField(),
    ]
)
```

Nếu bạn muốn các TextField full width, hãy chú ý đến constraints.

Trong một layout có đủ width, bạn có thể dùng:

```python
ft.TextField(
    expand=True,
)
```

hoặc đảm bảo parent cung cấp width phù hợp.

---

# 43. `expand` truyền qua hierarchy

Đây là phần quan trọng.

Giả sử:

```text
Page
└── Row
    └── Column
        └── TextField(expand=True)
```

`TextField` muốn expand.

Nhưng nếu:

```text
Column
```

không có đủ width thì TextField không thể tự nhiên chiếm vô hạn.

Layout phải có:

```text
Parent
 ↓
constraints
 ↓
Row
 ↓
Column
 ↓
TextField
```

Vì vậy:

> `expand` không phải phép thuật.

Nó hoạt động trong **constraints** mà parent cung cấp.

---

# 44. Đây là lý do cần học Constraints

Bạn sẽ gặp những tình huống:

```python
expand=True
```

nhưng UI:

```text
không expand
```

hoặc:

```text
overflow
```

hoặc:

```text
layout exception
```

Không nên xử lý bằng cách thử ngẫu nhiên:

```python
width=500
height=500
```

Thay vào đó phải hỏi:

```text
Parent đang cho child constraint gì?
```

Phần này sẽ được đào sâu ở **Buổi 20 — Layout Constraints và Sizing**.

---

# 45. Pattern: Center Screen

Một màn hình login:

```text
┌──────────────────────────────────┐
│                                  │
│                                  │
│           Login Form             │
│                                  │
│                                  │
└──────────────────────────────────┘
```

Có thể tư duy:

```python
page.add(
    ft.Column(
        controls=[
            login_form,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
)
```

---

# 46. Pattern: Header + Body

```text
┌──────────────────────────────────┐
│ Header                           │
├──────────────────────────────────┤
│                                  │
│ Body                             │
│                                  │
└──────────────────────────────────┘
```

```python
ft.Column(
    controls=[
        header,

        body,
    ],
    expand=True,
)
```

Nếu body cần ăn phần còn lại:

```python
ft.Column(
    controls=[
        header,

        ft.Container(
            content=body,
            expand=True,
        ),
    ],
    expand=True,
)
```

---

# 47. Pattern: Header + Scrollable Body

Đây là pattern cực kỳ quan trọng cho app desktop/mobile:

```text
┌──────────────────────────────┐
│ Header                       │
├──────────────────────────────┤
│ Content                 ║    │
│                         ║    │
│                         ║ ↓  │
│                         ║    │
└──────────────────────────────┘
```

```python
layout = ft.Column(
    controls=[
        header,

        ft.Column(
            controls=content,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
    ],
    expand=True,
)
```

---

# 48. Pattern: Sidebar + Main

Kết hợp `Row` và `Column`:

```text
Page
└── Row
    ├── Sidebar
    │   └── Column
    │
    └── Main
        └── Column
            ├── Header
            ├── Content
            └── Footer
```

Đây là kiến trúc layout của rất nhiều desktop application.

---

# 49. Ví dụ hoàn chỉnh

```python
import flet as ft


def main(page: ft.Page):

    sidebar = ft.Container(
        width=220,
        content=ft.Column(
            controls=[
                ft.Text(
                    "My App",
                    size=24,
                ),

                ft.TextButton("Dashboard"),
                ft.TextButton("Users"),
                ft.TextButton("Settings"),

                ft.Container(
                    expand=True,
                ),

                ft.TextButton("Logout"),
            ],
            spacing=10,
        ),
        padding=20,
    )

    header = ft.Row(
        controls=[
            ft.Text(
                "Dashboard",
                size=28,
            ),

            ft.Button("Refresh"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    content = ft.Column(
        controls=[
            ft.Text("Welcome!"),
            ft.Text("This is dashboard content."),
        ],
        spacing=10,
    )

    main_content = ft.Column(
        controls=[
            header,

            ft.Container(
                content=content,
                expand=True,
            ),
        ],
        expand=True,
        spacing=20,
    )

    page.add(
        ft.Row(
            controls=[
                sidebar,
                main_content,
            ],
            expand=True,
        )
    )


ft.run(main)
```

Mental Tree:

```text
Page
└── Row
    │
    ├── Container
    │   └── Column
    │       ├── Text
    │       ├── Button
    │       ├── Button
    │       ├── Button
    │       ├── Spacer
    │       └── Button
    │
    └── Column
        ├── Row
        │   ├── Text
        │   └── Button
        │
        └── Container
            └── Column
                ├── Text
                └── Text
```

Nếu bạn hiểu được Tree này thì bạn đang bắt đầu thực sự hiểu Flet Layout.

---

# 50. `Column` trong Todo App

Todo item có thể:

```text
┌────────────────────────────────────┐
│ ☐ Learn Flet                       │
│   Layout Deep Dive                 │
└────────────────────────────────────┘
```

Tree:

```text
Row
├── Checkbox
├── Column
│   ├── Text
│   └── Text
└── Button
```

Code:

```python
item = ft.Row(
    controls=[
        ft.Checkbox(),

        ft.Column(
            controls=[
                ft.Text("Learn Flet"),
                ft.Text("Layout Deep Dive"),
            ],
            expand=True,
        ),

        ft.Button("Delete"),
    ]
)
```

Đây là pattern bạn sẽ gặp liên tục trong ứng dụng CRUD.

---

# 51. `Column` cho Settings

Ví dụ:

```text
Settings

Appearance
[ Dark Mode        ON ]

Notifications
[ Enable alerts    ON ]

Language
[ Vietnamese       ▼ ]

                 [ Save ]
```

Tree:

```text
Column
├── Text
├── Row
├── Row
├── Row
└── Row
```

`Column` là layout chính.

Mỗi `Row` là một setting item.

---

# 52. `Column` cho trang đọc truyện

Với project crawler/reader của bạn, một reading page có thể:

```text
Page
│
└── Column
    ├── Header
    ├── Chapter Title
    ├── Content
    ├── Content
    ├── Content
    ├── ...
    └── Navigation
```

Sau này:

```text
Column
+ scroll
```

sẽ rất hữu ích.

---

# 53. `Column` cho CLI/TTS app GUI

Một app TTS:

```text
┌─────────────────────────────────┐
│ Text to Speech                  │
│                                 │
│ [ Input text                 ]  │
│ [                             ] │
│                                 │
│ Voice                           │
│ [ Vietnamese                  ] │
│                                 │
│ Rate                            │
│ [──────────────●─────────────]  │
│                                 │
│             [ Convert ]         │
└─────────────────────────────────┘
```

Layout chính:

```text
Column
├── Text
├── TextField
├── Text
├── Dropdown
├── Text
├── Slider
└── Button
```

Đây là một use case rất điển hình.

---

# 54. Quy tắc thiết kế `Column`

Khi nhìn UI, hãy hỏi:

### Nội dung xếp dọc?

```text
Column
```

### Nội dung xếp ngang?

```text
Row
```

### Một phần cần chiếm không gian còn lại?

```text
expand=True
```

### Muốn tạo khoảng trống đẩy item xuống?

```text
Container(expand=True)
```

### Nội dung quá dài?

```text
scroll
```

### Có rất nhiều items?

```text
ListView
```

---

# 55. Debug `Column`

Khi Column không đúng:

```text
1. Column có đủ height không?
2. Parent có cấp height không?
3. alignment đang tác động main axis nào?
4. horizontal_alignment đang tác động cross axis nào?
5. child có expand không?
6. Có scroll không?
7. Có nested Column quá sâu không?
8. Có overflow không?
```

---

# 56. Bài tập 1 — Login Form

Tạo:

```text
        Login

Username
[......................]

Password
[......................]

☐ Remember me

          [ Login ]
```

Yêu cầu:

```text
Column
├── Text
├── TextField
├── TextField
├── Checkbox
└── Button
```

---

# 57. Bài tập 2 — Center Login

Đưa form vào chính giữa màn hình.

Gợi ý:

```python
ft.Column(
    controls=[form],
    expand=True,
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Bạn cần hiểu tại sao phải có:

```python
expand=True
```

---

# 58. Bài tập 3 — Header / Content / Footer

Tạo:

```text
┌────────────────────────────┐
│ HEADER                     │
├────────────────────────────┤
│                            │
│ CONTENT                    │
│                            │
├────────────────────────────┤
│ FOOTER                     │
└────────────────────────────┘
```

Trong đó:

```text
Header → height cố định
Content → expand
Footer → height cố định
```

---

# 59. Bài tập 4 — Sidebar

Tạo:

```text
Dashboard
Users
Books
Settings


Logout
```

Yêu cầu `Logout` luôn nằm cuối sidebar.

Gợi ý:

```python
ft.Container(expand=True)
```

ở giữa.

---

# 60. Bài tập 5 — Dashboard Card

Tạo card:

```text
┌──────────────────────────────┐
│ Total Books                  │
│                              │
│ 12,450                       │
│                              │
│ +12%                 [View]  │
└──────────────────────────────┘
```

Tree:

```text
Container
└── Column
    ├── Text
    ├── Text
    └── Row
        ├── Text
        └── Button
```

---

# 61. Bài tập 6 — Scroll

Tạo 100 item:

```text
Item 1
Item 2
Item 3
...
Item 100
```

Dùng:

```python
ft.Column(
    ...,
    scroll=ft.ScrollMode.AUTO,
)
```

Sau đó thử lại bằng:

```python
ft.ListView(...)
```

và tự trả lời:

> Khi nào nên dùng Column + scroll, khi nào nên dùng ListView?

Chúng ta sẽ đào sâu câu hỏi này ở Buổi 17.

---

# 62. Bài tập 7 — Row + Column

Tạo:

```text
┌───────────────────────────────────────┐
│ Python                      [Open]    │
│ Learn Python deeply                   │
│ 43 lessons                            │
└───────────────────────────────────────┘
```

Tree:

```text
Container
└── Row
    ├── Column
    │   ├── Text
    │   ├── Text
    │   └── Text
    │
    └── Button
```

Sau đó làm cho `Column` chiếm phần không gian còn lại.

---

# 63. Bài tập 8 — Debug Alignment

Tạo:

```python
ft.Column(
    controls=[
        ft.Text("Hello"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Quan sát.

Sau đó:

```python
ft.Column(
    controls=[
        ft.Text("Hello"),
    ],
    expand=True,
    alignment=ft.MainAxisAlignment.CENTER,
)
```

So sánh.

Bạn phải giải thích được:

```text
Tại sao cùng CENTER
nhưng kết quả khác nhau?
```

---

# 64. Cheat Sheet

### Basic

```python
ft.Column(
    controls=[...]
)
```

### Khoảng cách

```python
spacing=10
```

### Main Axis — vertical

```python
alignment=ft.MainAxisAlignment.CENTER
```

### Cross Axis — horizontal

```python
horizontal_alignment=ft.CrossAxisAlignment.CENTER
```

### Chiếm không gian

```python
expand=True
```

### Scroll

```python
scroll=ft.ScrollMode.AUTO
```

### Spacer

```python
ft.Container(expand=True)
```

---

# 65. Mental Model cuối buổi

Hãy ghi nhớ sơ đồ này:

```text
                     Column
                       │
                       │
                 Main Axis ↓
                       │
              ┌────────┼────────┐
              │        │        │
           Child    Child    Child
              │        │        │
              └────────┼────────┘
                       │
              Cross Axis ←→
```

Và:

```text
Column
│
├── alignment
│      ↓
│   vertical
│
├── horizontal_alignment
│      ↓
│   horizontal
│
├── spacing
│      ↓
│   between children
│
├── expand
│      ↓
│   consume available space
│
└── scroll
       ↓
    overflow content
```

---

# 66. Điều quan trọng nhất của Buổi 12

Đừng chỉ nhớ:

```python
ft.Column(...)
```

Hãy chuyển sang tư duy:

```text
                 Layout
                   │
          ┌────────┴────────┐
          │                 │
        Row              Column
          │                 │
       ngang               dọc
          │                 │
     Main Axis          Main Axis
      →                   ↓
          │                 │
     Cross Axis         Cross Axis
       ↓                   →
```

Và khi xây UI:

```text
Row
└── Column
    ├── Row
    ├── Row
    └── Row
```

hoặc:

```text
Column
├── Row
├── Container
│   └── Column
└── Row
```

chính là cách chúng ta **composition UI trong Flet**.

**Buổi 13** sẽ đi vào `Container` Deep Dive — một control cực kỳ quan trọng vì nó là nơi kết hợp **layout + padding + margin + background + border + border radius + alignment + sizing + decoration**. Sau `Row` và `Column`, hiểu `Container` sâu sẽ giúp bạn bắt đầu xây được các UI thực tế như Card, Sidebar, Toolbar và Dashboard.
