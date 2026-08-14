# Buổi 13 — `Container` Deep Dive

Hôm nay chúng ta học **`Container` thật sâu**.

Trong Flet, nếu `Row` và `Column` chịu trách nhiệm **sắp xếp**, thì `Container` thường chịu trách nhiệm **đóng gói + định kích thước + khoảng cách + trang trí + căn chỉnh**.

Mental model:

```text
Row / Column
    ↓
sắp xếp children

Container
    ↓
đóng gói một control
    ↓
size
padding
margin
alignment
background
border
border radius
shadow
```

---

# 1. `Container` là gì?

Ví dụ đơn giản:

```python
import flet as ft


def main(page: ft.Page):
    page.add(
        ft.Container(
            content=ft.Text("Hello Flet"),
        )
    )


ft.run(main)
```

Ta có:

```text
Container
└── Text
```

`Container` không phải là một "div HTML" đơn giản.

Nó là một control có thể kiểm soát nhiều khía cạnh của layout và presentation.

---

# 2. Mental Model

Hãy tưởng tượng:

```text
┌──────────────────────────────┐
│           margin             │
│   ┌──────────────────────┐   │
│   │      Container       │   │
│   │                      │   │
│   │       padding        │   │
│   │     ┌──────────┐     │   │
│   │     │ content  │     │   │
│   │     └──────────┘     │   │
│   │                      │   │
│   └──────────────────────┘   │
└──────────────────────────────┘
```

Có 4 khái niệm phải phân biệt:

```text
margin
   ↓
Container boundary
   ↓
padding
   ↓
content
```

---

# 3. Cú pháp cơ bản

Một `Container` có thể có:

```python
ft.Container(
    content=...,
    width=...,
    height=...,
    padding=...,
    margin=...,
    alignment=...,
    bgcolor=...,
    border=...,
    border_radius=...,
    shadow=...,
    expand=...,
)
```

Không cần nhớ tất cả ngay.

Chúng ta sẽ chia thành nhóm.

---

# 4. `content`

Đây là control nằm bên trong Container.

```python
ft.Container(
    content=ft.Text("Hello")
)
```

Tree:

```text
Container
└── Text
```

Có thể chứa:

```python
ft.Container(
    content=ft.Column(...)
)
```

hoặc:

```python
ft.Container(
    content=ft.Row(...)
)
```

hoặc:

```python
ft.Container(
    content=ft.Image(...)
)
```

---

# 5. Container có thể chứa gần như mọi UI

Ví dụ:

```python
card = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text("Python"),
            ft.Text("Learn Python"),
            ft.Button("Open"),
        ]
    )
)
```

Tree:

```text
Container
└── Column
    ├── Text
    ├── Text
    └── Button
```

Đây là pattern cực kỳ phổ biến.

---

# 6. `width`

```python
ft.Container(
    content=ft.Text("Hello"),
    width=300,
)
```

Concept:

```text
┌──────────────────────────────┐
│ Hello                        │
└──────────────────────────────┘
        300px
```

`width` xác định chiều rộng của Container.

---

# 7. `height`

```python
ft.Container(
    content=ft.Text("Hello"),
    height=100,
)
```

Concept:

```text
┌──────────────────────┐
│ Hello                │
│                      │
│                      │
└──────────────────────┘
        100px
```

---

# 8. `width` + `height`

```python
ft.Container(
    content=ft.Text("Hello"),
    width=300,
    height=150,
)
```

Bạn tạo một vùng:

```text
┌──────────────────────────────┐
│                              │
│            Hello             │
│                              │
└──────────────────────────────┘
```

Nhưng chú ý:

> `width` và `height` chỉ xác định kích thước Container, không tự động căn content vào giữa.

---

# 9. `alignment`

Đây là một trong những thuộc tính quan trọng nhất của Container.

```python
ft.Container(
    content=ft.Text("Hello"),
    width=300,
    height=150,
    alignment=ft.alignment.center,
)
```

Kết quả:

```text
┌──────────────────────────────┐
│                              │
│           Hello              │
│                              │
└──────────────────────────────┘
```

Container có thể căn content bên trong.

---

# 10. Alignment của Container khác Column

Đây là điểm rất quan trọng.

### Column

```python
alignment=ft.MainAxisAlignment.CENTER
```

→ căn **children theo main axis**.

### Container

```python
alignment=ft.alignment.center
```

→ căn **content bên trong Container**.

Mental model:

```text
Column
└── điều khiển children

Container
└── điều khiển content
```

---

# 11. Các alignment phổ biến

```python
ft.alignment.top_left
ft.alignment.top_center
ft.alignment.top_right

ft.alignment.center_left
ft.alignment.center
ft.alignment.center_right

ft.alignment.bottom_left
ft.alignment.bottom_center
ft.alignment.bottom_right
```

Ví dụ:

```python
alignment=ft.alignment.center_right
```

```text
┌──────────────────────────────┐
│                              │
│                        Hello │
│                              │
└──────────────────────────────┘
```

---

# 12. `padding`

Padding là khoảng cách **giữa border của Container và content**.

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=20,
)
```

Concept:

```text
┌──────────────────────────────┐
│                              │
│     Hello                    │
│                              │
└──────────────────────────────┘
        ↑
      padding
```

---

# 13. Padding số

```python
padding=20
```

có thể hiểu là khoảng cách đều:

```text
top    = 20
right  = 20
bottom = 20
left   = 20
```

---

# 14. Padding từng cạnh

Bạn có thể kiểm soát từng phía bằng `ft.Padding`.

```python
ft.Container(
    content=ft.Text("Hello"),
    padding=ft.Padding(
        left=20,
        top=10,
        right=20,
        bottom=10,
    ),
)
```

Concept:

```text
        top = 10
       ↓
┌─────────────────────┐
│                     │
│   Hello             │
│                     │
└─────────────────────┘
       ↑
    bottom = 10
```

---

# 15. Padding horizontal / vertical

Pattern thường gặp:

```python
padding=ft.Padding.symmetric(
    horizontal=20,
    vertical=10,
)
```

Tư duy:

```text
horizontal
← 20 → content ← 20 →

vertical
↑ 10
content
↓ 10
```

Rất hữu ích cho:

* button
* card
* toolbar
* header

---

# 16. `margin`

Margin nằm **bên ngoài Container**.

```python
ft.Container(
    content=ft.Text("Hello"),
    margin=20,
)
```

Mental model:

```text
outside
   ↓
 margin
   ↓
┌───────────────┐
│   Container   │
└───────────────┘
```

---

# 17. Margin vs Padding

Đây là kiến thức bắt buộc phải thuộc.

### Padding

```text
Container
┌──────────────────────┐
│   padding             │
│     Hello             │
│   padding             │
└──────────────────────┘
```

### Margin

```text
       margin
          ↓
    ┌───────────────┐
    │   Container   │
    └───────────────┘
          ↑
       margin
```

Tư duy:

```text
padding
→ khoảng cách bên trong

margin
→ khoảng cách bên ngoài
```

---

# 18. `bgcolor`

Container có thể có background:

```python
ft.Container(
    content=ft.Text("Hello"),
    bgcolor=ft.Colors.BLUE,
)
```

Concept:

```text
┌──────────────────────────┐
│ Hello                    │
└──────────────────────────┘
```

---

# 19. Background + padding

```python
ft.Container(
    content=ft.Text("Hello"),
    bgcolor=ft.Colors.BLUE,
    padding=20,
)
```

Tư duy:

```text
background
┌────────────────────────────┐
│                            │
│       Hello                │
│                            │
└────────────────────────────┘
       ↑
    padding
```

---

# 20. `border`

Bạn có thể thêm border:

```python
ft.Container(
    content=ft.Text("Hello"),
    border=ft.Border.all(1),
)
```

Concept:

```text
┌──────────────────────────────┐
│ Hello                        │
└──────────────────────────────┘
```

Border là đường bao quanh Container.

---

# 21. Border có màu

```python
ft.Container(
    content=ft.Text("Hello"),
    border=ft.Border.all(
        1,
        ft.Colors.BLUE,
    ),
)
```

---

# 22. Border từng cạnh

Có thể kiểm soát từng cạnh:

```python
ft.Border(
    top=...,
    right=...,
    bottom=...,
    left=...,
)
```

Điều này hữu ích khi tạo:

```text
divider
header bottom border
input underline
section separator
```

---

# 23. `border_radius`

Bo góc:

```python
ft.Container(
    content=ft.Text("Hello"),
    border_radius=10,
)
```

Concept:

```text
╭────────────────────────╮
│ Hello                  │
╰────────────────────────╯
```

---

# 24. Border + radius

Một card thường:

```python
ft.Container(
    content=ft.Text("Python"),
    border=ft.Border.all(1),
    border_radius=12,
    padding=20,
)
```

Đây là pattern UI rất phổ biến.

---

# 25. `shadow`

Container có thể có shadow:

```python
ft.Container(
    content=ft.Text("Card"),
    shadow=ft.BoxShadow(
        blur_radius=10,
        spread_radius=1,
    ),
)
```

Concept:

```text
     ┌───────────────────┐
     │       Card        │
     └───────────────────┘
        ░░░░░░░░░░░░
```

Shadow thường dùng cho:

* Card
* Dialog
* Floating panel
* Sidebar
* Popup

---

# 26. Card cơ bản

Kết hợp:

```python
card = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text("Python", size=22),
            ft.Text("Learn Python deeply"),
        ],
        spacing=10,
    ),
    padding=20,
    border_radius=12,
    border=ft.Border.all(1),
)
```

Tree:

```text
Container
├── padding
├── border
├── radius
└── Column
    ├── Text
    └── Text
```

---

# 27. Container như "Box"

Một mental model tốt:

```text
Container
=
Box
```

Ví dụ:

```text
┌──────────────────────┐
│                      │
│       content        │
│                      │
└──────────────────────┘
```

Container cho phép bạn kiểm soát:

```text
size
position/alignment
spacing
background
border
radius
shadow
```

---

# 28. Container không nhất thiết phải có `content`

Bạn có thể tạo một vùng rỗng:

```python
ft.Container(
    width=100,
    height=100,
    bgcolor=ft.Colors.BLUE,
)
```

Nó hữu ích cho:

* spacer
* background
* placeholder
* layout
* separator
* visual decoration

---

# 29. Spacer bằng Container

Đây là pattern chúng ta đã gặp ở Buổi 12.

```python
ft.Container(
    expand=True,
)
```

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Top"),
        ft.Container(expand=True),
        ft.Text("Bottom"),
    ]
)
```

Kết quả:

```text
┌────────────────────┐
│ Top                │
│                    │
│                    │
│                    │
│ Bottom             │
└────────────────────┘
```

---

# 30. Container `expand=True`

```python
ft.Container(
    content=ft.Text("Content"),
    expand=True,
)
```

Nó yêu cầu Container sử dụng phần không gian có thể được cấp.

Nhưng nhớ:

> `expand=True` vẫn phụ thuộc vào constraints của parent.

---

# 31. `expand` trong Row

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(
            content=ft.Text("Left"),
            expand=True,
        ),
        ft.Container(
            content=ft.Text("Right"),
            width=200,
        ),
    ]
)
```

Concept:

```text
┌──────────────────────────────────────┐
│ Left                    │ Right      │
│                        │             │
└──────────────────────────────────────┘
        flexible              200px
```

---

# 32. `expand` trong Column

```python
ft.Column(
    controls=[
        ft.Container(
            content=ft.Text("Header"),
            height=60,
        ),

        ft.Container(
            content=ft.Text("Content"),
            expand=True,
        ),

        ft.Container(
            content=ft.Text("Footer"),
            height=50,
        ),
    ]
)
```

Concept:

```text
Header → fixed

Content → flexible

Footer → fixed
```

---

# 33. Container + `alignment`

Ví dụ tạo button-like box:

```python
ft.Container(
    content=ft.Text("Click me"),
    width=200,
    height=60,
    alignment=ft.alignment.center,
    bgcolor=ft.Colors.BLUE,
    border_radius=10,
)
```

Concept:

```text
┌──────────────────────┐
│                      │
│       Click me       │
│                      │
└──────────────────────┘
```

---

# 34. Container vs Button

Bạn có thể nghĩ:

> Tại sao không dùng Button?

Đúng.

Nếu cần:

```text
click
hover
keyboard interaction
accessibility
```

thì dùng Button.

Container phù hợp khi bạn cần:

```text
visual box
layout
decoration
wrapping
custom UI
```

---

# 35. Container + event

Container cũng có thể tham gia event interaction.

Ví dụ concept:

```python
def clicked(e):
    print("clicked")


box = ft.Container(
    content=ft.Text("Click"),
    on_click=clicked,
)
```

Nhưng đừng biến mọi Container thành Button.

Nếu control có semantics rõ ràng là button, nên dùng control button tương ứng.

---

# 36. Container + `on_hover`

Bạn có thể xây UI tương tác:

```python
def hover(e):
    e.control.bgcolor = (
        ft.Colors.BLUE
        if e.data == "true"
        else ft.Colors.WHITE
    )
    e.control.update()
```

Sau đó:

```python
box = ft.Container(
    content=ft.Text("Hover me"),
    on_hover=hover,
)
```

Đây là nền tảng để xây:

```text
sidebar item
dashboard card
navigation item
custom menu
```

---

# 37. Nhưng hãy cẩn thận với state

Không nên viết quá nhiều logic:

```python
on_hover
on_click
on_enter
on_exit
```

trực tiếp trong một Container lớn.

Sau này khi học architecture, chúng ta sẽ tách:

```text
View
State
Event
Controller
```

---

# 38. Container + Column = Card

Đây là pattern bạn cần thuộc:

```python
card = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text("Title"),
            ft.Text("Description"),
            ft.Button("Open"),
        ],
        spacing=10,
    ),
    padding=20,
    border_radius=12,
)
```

Tư duy:

```text
Container
    ↓
visual shell

Column
    ↓
vertical content
```

---

# 39. Container + Row = Toolbar

```python
toolbar = ft.Container(
    content=ft.Row(
        controls=[
            ft.Text("Dashboard"),
            ft.Button("Refresh"),
            ft.Button("Settings"),
        ],
        spacing=10,
    ),
    padding=10,
)
```

Tree:

```text
Container
└── Row
    ├── Text
    ├── Button
    └── Button
```

---

# 40. Container + Stack

Sau này khi học `Stack`, bạn sẽ thấy:

```text
Container
└── Stack
    ├── Image
    └── Text
```

Rất phù hợp để tạo:

```text
image card
overlay
badge
avatar
banner
```

---

# 41. Container làm Divider

Bạn không nhất thiết cần một control đặc biệt.

Ví dụ:

```python
ft.Container(
    height=1,
    bgcolor=ft.Colors.GREY,
)
```

Concept:

```text
────────────────────────
```

Hoặc:

```python
ft.Container(
    width=1,
    bgcolor=ft.Colors.GREY,
)
```

cho vertical divider.

---

# 42. Container làm Spacer cố định

Không phải lúc nào cũng cần:

```python
expand=True
```

Bạn có thể:

```python
ft.Container(height=20)
```

để tạo khoảng cách dọc.

Ví dụ:

```python
ft.Column(
    controls=[
        title,
        ft.Container(height=20),
        form,
    ]
)
```

Nhưng nếu chỉ muốn khoảng cách giữa children, `spacing` thường rõ nghĩa hơn.

---

# 43. `spacing` vs Container height

Không nên:

```python
ft.Column(
    controls=[
        text1,
        ft.Container(height=10),
        text2,
        ft.Container(height=10),
        text3,
    ]
)
```

nếu mục đích đơn giản chỉ là spacing.

Tốt hơn:

```python
ft.Column(
    controls=[
        text1,
        text2,
        text3,
    ],
    spacing=10,
)
```

Nguyên tắc:

> Dùng đúng abstraction cho đúng nhiệm vụ.

---

# 44. Container cho Section

Ví dụ:

```python
section = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text("General"),
            ft.TextField(label="Name"),
            ft.TextField(label="Email"),
        ],
        spacing=15,
    ),
    padding=20,
    border_radius=10,
)
```

Concept:

```text
┌──────────────────────────────┐
│ General                      │
│                              │
│ Name                         │
│ [.........................]  │
│                              │
│ Email                        │
│ [.........................]  │
└──────────────────────────────┘
```

---

# 45. Container cho Sidebar

```python
sidebar = ft.Container(
    width=240,
    padding=20,
    content=ft.Column(
        controls=[
            logo,
            dashboard,
            users,
            settings,
            ft.Container(expand=True),
            logout,
        ]
    ),
)
```

Container:

```text
width
padding
background
border
```

Column:

```text
arrangement
```

Đây là cách phân chia trách nhiệm rất sạch.

---

# 46. Container cho Header

```python
header = ft.Container(
    height=64,
    padding=ft.Padding.symmetric(
        horizontal=20,
        vertical=10,
    ),
    content=ft.Row(
        controls=[
            ft.Text("Dashboard"),
            ft.Button("Refresh"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    ),
)
```

Mental model:

```text
Container
    ↓
Header box

Row
    ↓
Header content arrangement
```

---

# 47. Container + Responsive Layout

Container thường được dùng làm wrapper:

```python
ft.Container(
    content=content,
    expand=True,
)
```

Sau đó parent quyết định kích thước.

Đây là pattern quan trọng trong responsive UI:

```text
Page
 ↓
Responsive layout
 ↓
Container
 ↓
actual content
```

Chúng ta sẽ đào sâu ở các buổi:

* `ResponsiveRow`
* Responsive UI
* Layout constraints

---

# 48. Một Dashboard Card hoàn chỉnh

```python
def stat_card(title, value, subtitle):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title),

                ft.Text(
                    value,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(subtitle),
            ],
            spacing=8,
        ),
        width=220,
        padding=20,
        border_radius=12,
        border=ft.Border.all(1),
    )
```

Dùng:

```python
cards = ft.Row(
    controls=[
        stat_card("Books", "12,450", "+12%"),
        stat_card("Chapters", "245,320", "+8%"),
        stat_card("Sources", "18", "+2"),
    ],
    spacing=20,
)
```

Tree:

```text
Row
├── Container
│   └── Column
│       ├── Text
│       ├── Text
│       └── Text
│
├── Container
│   └── Column
│
└── Container
    └── Column
```

Đây là nền tảng của **Dashboard Project ở Buổi 26**.

---

# 49. Component hóa Container

Đừng lặp:

```python
ft.Container(
    padding=20,
    border_radius=12,
    border=ft.Border.all(1),
    ...
)
```

ở 20 nơi.

Tạo component:

```python
def card(content):
    return ft.Container(
        content=content,
        padding=20,
        border_radius=12,
        border=ft.Border.all(1),
    )
```

Sau đó:

```python
card(
    ft.Column(
        controls=[
            ft.Text("Python"),
            ft.Text("Learn Python"),
        ]
    )
)
```

Đây là bước đầu tiên hướng tới Design System.

---

# 50. Tạo `AppCard`

Ví dụ:

```python
class AppCard(ft.Container):

    def __init__(self, content):
        super().__init__(
            content=content,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1),
        )
```

Dùng:

```python
AppCard(
    ft.Column(
        controls=[
            ft.Text("Python"),
            ft.Text("Learn Python"),
        ]
    )
)
```

Sau này bạn có thể mở rộng:

```text
AppCard
├── padding
├── radius
├── border
├── shadow
├── theme
└── hover
```

---

# 51. Container và Constraints

Đây là phần cực kỳ quan trọng.

Giả sử:

```python
ft.Container(
    width=500,
)
```

Bạn không thể kết luận:

> Container luôn rộng 500px.

Bởi vì layout còn phụ thuộc:

```text
Parent constraints
+
Container properties
+
Child constraints
```

Mental model:

```text
Parent
   │
   │ constraints
   ↓
Container
   │
   │ constraints
   ↓
Content
```

Đây chính là lý do Buổi 20 sẽ rất quan trọng.

---

# 52. Một lỗi phổ biến

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(
            width=500,
        ),
        ft.Container(
            width=500,
        ),
    ]
)
```

Nếu màn hình chỉ rộng:

```text
800px
```

thì bạn đang yêu cầu:

```text
500 + 500 = 1000px
```

Không đủ.

Kết quả có thể là overflow hoặc layout không như mong muốn.

Không phải Flet "bị lỗi".

Bạn đã tạo constraint không hợp lý.

---

# 53. `expand` thay vì hard-code width

Thay vì:

```python
ft.Container(width=500)
```

đôi khi nên:

```python
ft.Container(
    expand=True,
)
```

Ví dụ:

```text
Sidebar = 240px
Main = remaining width
```

```python
ft.Row(
    controls=[
        ft.Container(width=240),
        ft.Container(expand=True),
    ]
)
```

Đây là responsive thinking.

---

# 54. Container trong ứng dụng đọc truyện

Một chapter content có thể:

```python
chapter = ft.Container(
    content=ft.Column(
        controls=[
            ft.Text(
                "Chapter 123",
                size=28,
            ),
            ft.Text("Paragraph 1..."),
            ft.Text("Paragraph 2..."),
            ft.Text("Paragraph 3..."),
        ],
        spacing=15,
    ),
    padding=30,
)
```

Nếu muốn reading width giới hạn:

```text
┌─────────────────────────────────────┐
│                                     │
│       ┌────────────────────┐        │
│       │ Chapter            │        │
│       │                    │        │
│       │ Content            │        │
│       └────────────────────┘        │
│                                     │
└─────────────────────────────────────┘
```

Container là lớp rất phù hợp để kiểm soát vùng đọc.

---

# 55. Container trong TTS App

Ví dụ:

```python
input_box = ft.Container(
    content=ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=20,
    ),
    padding=10,
    border_radius=10,
    border=ft.Border.all(1),
)
```

Mental model:

```text
Container
└── TextField
```

Container cung cấp:

```text
padding
border
radius
visual grouping
```

---

# 56. Quy tắc phân chia trách nhiệm

Khi xây UI, hãy tư duy:

### `Row`

```text
Sắp xếp ngang
```

### `Column`

```text
Sắp xếp dọc
```

### `Container`

```text
Box / Wrapper / Decoration
```

Ví dụ:

```text
Container
└── Column
    ├── Text
    ├── TextField
    └── Row
        ├── Button
        └── Button
```

Mỗi control có một nhiệm vụ rõ ràng.

---

# 57. Anti-pattern

Không nên tạo một `Container` khổng lồ:

```text
Container
└── Column
    ├── Container
    │   └── Row
    │       └── Container
    │           └── Column
    │               └── Container
    │                   └── ...
```

Không phải nested container nào cũng sai.

Nhưng nếu bạn không biết **tại sao cần Container**, hãy xem lại.

Mỗi wrapper nên có lý do:

```text
size
padding
background
border
alignment
spacing
decoration
```

---

# 58. Nguyên tắc rất quan trọng

Đừng dùng:

```python
Container(width=10)
```

chỉ để tạo spacing nếu bạn có:

```python
spacing=10
```

Đừng dùng:

```python
Container(height=100)
```

để ép layout nếu vấn đề thực sự là:

```text
alignment
expand
constraints
```

Đừng hard-code kích thước khắp nơi.

Hãy hiểu layout trước.

---

# 59. Mini Project — Profile Card

Hãy xây:

```text
┌─────────────────────────────────┐
│                                 │
│           [ Avatar ]            │
│                                 │
│           Garden                │
│      Python Developer           │
│                                 │
│    [ Follow ]    [ Message ]   │
│                                 │
└─────────────────────────────────┘
```

Tree:

```text
Container
└── Column
    ├── Container / Image
    ├── Text
    ├── Text
    └── Row
        ├── Button
        └── Button
```

Yêu cầu:

```text
width = 320
padding
border
border_radius
alignment
spacing
```

---

# 60. Mini Project — Dashboard Stat Card

Tạo:

```text
┌───────────────────────────┐
│ Total Books               │
│                           │
│ 12,450                    │
│                           │
│ +12% this month           │
└───────────────────────────┘
```

Sau đó tạo 4 card:

```text
┌──────────┐ ┌──────────┐
│ Books    │ │ Chapters │
│ 12,450   │ │ 245,320  │
└──────────┘ └──────────┘

┌──────────┐ ┌──────────┐
│ Sources  │ │ Errors   │
│ 18       │ │ 32       │
└──────────┘ └──────────┘
```

Đây sẽ là tiền đề cho Dashboard ở Buổi 26.

---

# 61. Mini Project — Sidebar

Xây:

```text
┌──────────────────────┐
│ 📚 My Reader         │
│                      │
│ Dashboard            │
│ Books                │
│ Favorites            │
│ History              │
│                      │
│                      │
│ Settings             │
│ Logout               │
└──────────────────────┘
```

Gợi ý:

```python
ft.Container(
    width=240,
    padding=20,
    content=ft.Column(
        controls=[
            logo,
            dashboard,
            books,
            favorites,
            history,

            ft.Container(expand=True),

            settings,
            logout,
        ]
    )
)
```

Bạn đang sử dụng đồng thời:

```text
Container
+
Column
+
expand
```

---

# 62. Mini Project — Reading Page

Đây là bài tập rất sát với project của bạn.

Tạo:

```text
┌─────────────────────────────────────────┐
│             Chapter 123                 │
├─────────────────────────────────────────┤
│                                         │
│        Chapter content...               │
│                                         │
│        Paragraph...                     │
│                                         │
│        Paragraph...                     │
│                                         │
│             [Previous] [Next]           │
└─────────────────────────────────────────┘
```

Cấu trúc:

```text
Column
├── Container → Header
├── Container → Content
└── Container → Navigation
```

Content:

```python
expand=True
```

Sau đó thêm:

```python
scroll=ft.ScrollMode.AUTO
```

---

# 63. Cheat Sheet `Container`

```python
ft.Container(
    content=...,

    # sizing
    width=300,
    height=200,

    # spacing
    padding=20,
    margin=10,

    # alignment
    alignment=ft.alignment.center,

    # background
    bgcolor=...,

    # border
    border=ft.Border.all(1),

    # radius
    border_radius=12,

    # shadow
    shadow=...,

    # layout
    expand=True,
)
```

Không cần nhớ hết.

Hãy nhớ 5 nhóm:

```text
Container
│
├── Size
│   ├── width
│   └── height
│
├── Space
│   ├── padding
│   └── margin
│
├── Alignment
│   └── alignment
│
├── Decoration
│   ├── bgcolor
│   ├── border
│   ├── border_radius
│   └── shadow
│
└── Layout
    └── expand
```

---

# 64. Mental Model cuối buổi

Nếu gặp một UI:

```text
┌─────────────────────────────────────┐
│              HEADER                 │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │ Card                        │   │
│   │                             │   │
│   │ Title                       │   │
│   │ Description                 │   │
│   │                             │   │
│   │             [Open]          │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

Hãy tư duy:

```text
Column
│
├── Container
│   └── Row → Header
│
└── Container
    └── Column
        ├── Text
        ├── Text
        └── Row
```

Không bắt đầu bằng:

> "Mình phải viết code gì?"

Mà bắt đầu bằng:

> **"UI Tree của mình là gì?"**

Đây là tư duy quan trọng nhất khi học Flet.

---

# 65. Tổng kết Giai đoạn II đến hiện tại

Bạn đã đi:

```text
Buổi 11
Row Deep Dive
    ↓
Buổi 12
Column Deep Dive
    ↓
Buổi 13
Container Deep Dive
```

Ba control này tạo thành bộ khung cơ bản:

```text
              UI
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
      Row    Column  Container
       │       │        │
     ngang    dọc      Box
```

Và trong ứng dụng thực tế:

```text
Container
└── Row
    ├── Container
    │   └── Column
    │       ├── Text
    │       └── Text
    │
    └── Container
        └── Column
```

Bạn sẽ sử dụng kiểu composition này **liên tục** khi xây Dashboard, CRUD app, TTS app và app đọc truyện.

**Buổi 14 — `Stack` Deep Dive** sẽ chuyển sang một kiểu layout hoàn toàn khác: **xếp các control chồng lên nhau**. Ta sẽ dùng nó để xây avatar có badge, card có ảnh + overlay text, floating button, notification badge và các UI phức tạp hơn.
