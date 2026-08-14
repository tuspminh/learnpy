# Buổi 15 — `ResponsiveRow` Deep Dive

Hôm nay chúng ta học một control rất quan trọng khi xây ứng dụng Flet thực tế:

> **`ResponsiveRow` — xây layout responsive dựa trên hệ thống 12 cột.**

Sau buổi này bạn sẽ hiểu cách xây:

```text
Desktop
┌──────────┬─────────────────────────────┐
│ Sidebar  │ Main                        │
│          │                             │
└──────────┴─────────────────────────────┘
```

nhưng khi xuống mobile:

```text
┌──────────────────────┐
│ Header               │
├──────────────────────┤
│ Main                 │
│                      │
├──────────────────────┤
│ Sidebar / Menu       │
└──────────────────────┘
```

---

# 1. Tại sao cần `ResponsiveRow`?

Ở các buổi trước, ta dùng:

```python
ft.Row(
    controls=[
        sidebar,
        content,
    ]
)
```

Ví dụ:

```text
Desktop 1200px

┌────────────┬───────────────────────────┐
│ Sidebar    │ Content                   │
│ 250px      │                           │
└────────────┴───────────────────────────┘
```

Có thể hoạt động tốt.

Nhưng nếu màn hình còn:

```text
800px
```

hoặc:

```text
400px
```

thì:

```text
┌───────┬────────────────┐
│ Side  │ Content        │
└───────┴────────────────┘
```

có thể trở nên quá chật.

Ta cần một cơ chế:

```text
màn hình rộng
    ↓
nhiều cột

màn hình hẹp
    ↓
ít cột

mobile
    ↓
xếp dọc
```

Đó chính là mục đích của `ResponsiveRow`.

---

# 2. Mental model

`ResponsiveRow` sử dụng **12-column grid**.

```text
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

Một control có thể chiếm:

```text
12/12
6/12
4/12
3/12
```

Ví dụ:

```text
6 columns + 6 columns

┌──────────────────┬──────────────────┐
│      6           │       6          │
└──────────────────┴──────────────────┘
```

Hoặc:

```text
3 + 3 + 3 + 3

┌──────┬──────┬──────┬──────┐
│  3   │  3   │  3   │  3   │
└──────┴──────┴──────┴──────┘
```

---

# 3. `ResponsiveRow` cơ bản

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):
    page.add(
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    col=6,
                    bgcolor=ft.Colors.BLUE,
                    content=ft.Text("Left"),
                ),
                ft.Container(
                    col=6,
                    bgcolor=ft.Colors.GREEN,
                    content=ft.Text("Right"),
                ),
            ]
        )
    )


ft.run(main)
```

Mental model:

```text
ResponsiveRow
│
├── Container → 6
└── Container → 6
```

Kết quả:

```text
┌────────────────────┬────────────────────┐
│ Left               │ Right              │
│      6 columns     │      6 columns     │
└────────────────────┴────────────────────┘
```

---

# 4. `col`

Đây là thuộc tính quan trọng nhất.

Ví dụ:

```python
ft.Container(
    col=4,
)
```

Nghĩa:

```text
12 columns
───────────
   4
```

Control chiếm:

```text
4 / 12
```

tức khoảng:

```text
33.33%
```

---

# 5. Một phần ba màn hình

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            col=4,
            content=ft.Text("A"),
        ),
        ft.Container(
            col=4,
            content=ft.Text("B"),
        ),
        ft.Container(
            col=4,
            content=ft.Text("C"),
        ),
    ]
)
```

Kết quả:

```text
┌────────────┬────────────┬────────────┐
│     A      │     B      │     C      │
│     4      │     4      │     4      │
└────────────┴────────────┴────────────┘
```

---

# 6. `col=3`

```python
col=3
```

Có:

```text
12 / 3 = 4
```

nên một hàng chứa được 4 control:

```text
3 + 3 + 3 + 3
```

```text
┌──────┬──────┬──────┬──────┐
│  A   │  B   │  C   │  D   │
│  3   │  3   │  3   │  3   │
└──────┴──────┴──────┴──────┘
```

Đây là pattern rất phổ biến cho dashboard.

---

# 7. `col=2`

```text
2 + 2 + 2 + 2 + 2 + 2
```

```text
┌───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │ E │ F │
└───┴───┴───┴───┴───┴───┘
```

---

# 8. `col=1`

Tối đa 12 control:

```text
1 + 1 + 1 + ... + 1
```

```text
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
│ │ │ │ │ │ │ │ │ │ │ │ │
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

---

# 9. Tổng `col` lớn hơn 12

Ví dụ:

```python
col=8
col=8
```

Tổng:

```text
8 + 8 = 16
```

không vừa một hàng.

ResponsiveRow có thể đưa control tiếp theo xuống dòng.

Concept:

```text
┌──────────────────────────────┐
│          A = 8               │
├──────────────────────────────┤
│          B = 8               │
└──────────────────────────────┘
```

Đây chính là một trong những điểm mạnh của grid layout.

---

# 10. `ResponsiveRow` vs `Row`

### `Row`

Bạn nghĩ theo:

```text
A + B + C
```

### `ResponsiveRow`

Bạn nghĩ theo:

```text
12-column grid
```

Ví dụ:

```text
Row:

Sidebar | Main
```

Trong ResponsiveRow:

```text
Sidebar = 3
Main    = 9
```

```text
┌───────────┬──────────────────────────┐
│    3      │            9             │
└───────────┴──────────────────────────┘
```

Đây là tư duy rất khác.

---

# 11. Responsive breakpoints

Điểm mạnh nhất của `ResponsiveRow`:

Một control có thể có `col` khác nhau theo kích thước màn hình.

Ví dụ concept:

```python
ft.Container(
    col={
        "sm": 12,
        "md": 6,
        "lg": 4,
    }
)
```

Mental model:

```text
mobile
→ 12

tablet
→ 6

desktop
→ 4
```

Tức:

```text
Mobile:
┌──────────────────────┐
│ Card                 │
└──────────────────────┘

Tablet:
┌────────────┬─────────┐
│ Card       │ Card    │
└────────────┴─────────┘

Desktop:
┌──────┬──────┬──────┐
│ Card │ Card │ Card │
└──────┴──────┴──────┘
```

---

# 12. Breakpoint là gì?

Breakpoint là ngưỡng mà layout thay đổi.

Mental model:

```text
< breakpoint
    ↓
mobile

breakpoint
    ↓
tablet

> breakpoint
    ↓
desktop
```

Trong Flet, ResponsiveRow cung cấp các breakpoint để bạn khai báo responsive columns.

Điều quan trọng là:

> Không phải viết `if screen_width < ...` cho từng control.

Bạn khai báo layout rules.

---

# 13. Các breakpoint thường gặp

Trong Flet, responsive layout sử dụng các breakpoint như:

```text
xs
sm
md
lg
xl
xxl
```

Mental model:

```text
xs
↓
sm
↓
md
↓
lg
↓
xl
↓
xxl
```

Càng về sau:

```text
màn hình càng rộng
```

---

# 14. Ví dụ mobile-first

Hãy tạo card:

```python
ft.Container(
    col={
        "xs": 12,
        "sm": 6,
        "md": 4,
        "lg": 3,
    },
    content=...
)
```

Ý nghĩa:

```text
xs → 12
sm → 6
md → 4
lg → 3
```

Tức:

```text
Mobile
1 card / row

Tablet
2 cards / row

Medium
3 cards / row

Desktop
4 cards / row
```

Đây là pattern cực kỳ quan trọng.

---

# 15. Dashboard cards

Giả sử có:

```text
Books
Chapters
Sources
Errors
Downloads
Users
```

Ta muốn:

```text
Mobile:

┌───────────────┐
│ Books         │
└───────────────┘

┌───────────────┐
│ Chapters      │
└───────────────┘
```

Tablet:

```text
┌───────────┬───────────┐
│ Books     │ Chapters  │
└───────────┴───────────┘
```

Desktop:

```text
┌───────┬───────┬───────┬───────┐
│ Books │ Chapt │ Source│ Errors│
└───────┴───────┴───────┴───────┘
```

Ta có:

```python
def stat_card(title, value):
    return ft.Container(
        col={
            "xs": 12,
            "sm": 6,
            "md": 3,
        },
        content=...
    )
```

---

# 16. Đây là responsive thực sự

Không phải:

```python
if width < 600:
    ...
else:
    ...
```

mà là:

```python
col={
    "xs": 12,
    "sm": 6,
    "md": 4,
}
```

Bạn mô tả:

> "Control này muốn chiếm bao nhiêu phần grid ở mỗi breakpoint?"

Đây là **declarative responsive layout**.

---

# 17. `ResponsiveRow` + `Container`

Pattern phổ biến:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            col=4,
            content=...,
        ),
        ft.Container(
            col=8,
            content=...,
        ),
    ]
)
```

Tree:

```text
ResponsiveRow
│
├── Container
│   └── content
│
└── Container
    └── content
```

`ResponsiveRow` quản lý:

```text
grid
```

`Container` quản lý:

```text
box
```

---

# 18. `spacing`

ResponsiveRow cũng cần khoảng cách giữa các columns.

Bạn có thể sử dụng các thuộc tính spacing tương ứng của layout.

Ví dụ concept:

```python
ft.ResponsiveRow(
    spacing=20,
    run_spacing=20,
    controls=[
        ...
    ],
)
```

Mental model:

```text
spacing
→ khoảng cách ngang

run_spacing
→ khoảng cách giữa các hàng
```

---

# 19. `spacing` vs `run_spacing`

Ví dụ:

```text
A B C
D E F
```

Khoảng cách:

```text
A ←→ B ←→ C
```

là:

```text
spacing
```

Khoảng cách:

```text
A B C
     ↕
D E F
```

là:

```text
run_spacing
```

Rất hữu ích khi grid tự động wrap.

---

# 20. `ResponsiveRow` cho Gallery

Ví dụ app đọc truyện:

```text
Desktop:

┌─────┬─────┬─────┬─────┐
│Book │Book │Book │Book │
└─────┴─────┴─────┴─────┘
```

Tablet:

```text
┌────────┬────────┐
│ Book   │ Book   │
├────────┼────────┤
│ Book   │ Book   │
└────────┴────────┘
```

Mobile:

```text
┌────────────────┐
│ Book           │
├────────────────┤
│ Book           │
├────────────────┤
│ Book           │
└────────────────┘
```

Mỗi card:

```python
col={
    "xs": 12,
    "sm": 6,
    "lg": 3,
}
```

---

# 21. Book Grid thực tế

```python
def book_card(title):
    return ft.Container(
        col={
            "xs": 12,
            "sm": 6,
            "md": 4,
            "lg": 3,
        },
        content=ft.Container(
            padding=15,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(title),
                    ft.Text("Chapter 123"),
                ]
            ),
        ),
    )
```

Sau đó:

```python
books = ft.ResponsiveRow(
    controls=[
        book_card("One Piece"),
        book_card("Naruto"),
        book_card("Bleach"),
        book_card("Dragon Ball"),
        book_card("Demon Slayer"),
    ],
    spacing=20,
    run_spacing=20,
)
```

---

# 22. Tư duy Grid

Đừng nghĩ:

```text
Book 1
Book 2
Book 3
```

Hãy nghĩ:

```text
Mỗi Book = grid item
```

và:

```text
grid item
→ chiếm X/12 columns
```

Đây là tư duy CSS Grid/Bootstrap rất gần với cách thiết kế responsive UI.

---

# 23. Sidebar + Main

Một layout cực kỳ quan trọng:

```text
Desktop:

┌──────────────┬─────────────────────────┐
│ Sidebar      │ Main                    │
│              │                         │
└──────────────┴─────────────────────────┘
```

Ta có:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            col={
                "xs": 12,
                "lg": 3,
            },
            content=sidebar,
        ),
        ft.Container(
            col={
                "xs": 12,
                "lg": 9,
            },
            content=main,
        ),
    ]
)
```

---

# 24. Kết quả responsive

Desktop:

```text
3 + 9

┌──────────┬────────────────────────────┐
│ Sidebar  │ Main                       │
└──────────┴────────────────────────────┘
```

Mobile:

```text
12 + 12

┌────────────────────────────┐
│ Sidebar                    │
├────────────────────────────┤
│ Main                       │
└────────────────────────────┘
```

Đây chính là một trong những use case quan trọng nhất của ResponsiveRow.

---

# 25. Dashboard layout

Ta có:

```text
Dashboard
```

với:

```text
Sidebar
Header
Stats
Chart
Recent Books
```

ResponsiveRow có thể:

```text
Desktop
──────────────────────────────
Sidebar 3 | Main 9
           |
           | Header
           |
           | Stats
           |
           | Chart
──────────────────────────────
```

Mobile:

```text
Header
Stats
Chart
Recent Books
Menu
```

---

# 26. Nested ResponsiveRow

Bạn có thể lồng:

```text
ResponsiveRow
└── Container
    └── ResponsiveRow
```

Ví dụ:

```text
Page
└── ResponsiveRow
    ├── Sidebar
    └── Main
        └── ResponsiveRow
            ├── Card
            ├── Card
            └── Card
```

Đây là pattern rất mạnh.

---

# 27. Outer grid

Outer:

```text
3 + 9
```

```text
┌───────┬─────────────────────────┐
│ Side  │ Main                    │
└───────┴─────────────────────────┘
```

Inner:

```text
3 + 3 + 3 + 3
```

```text
┌────┬────┬────┬────┐
│ A  │ B  │ C  │ D  │
└────┴────┴────┴────┘
```

Composition:

```text
ResponsiveRow
├── Sidebar
└── Main
    └── ResponsiveRow
        ├── Card
        ├── Card
        ├── Card
        └── Card
```

---

# 28. `ResponsiveRow` không phải GridView

Điểm rất quan trọng.

### ResponsiveRow

Phù hợp:

```text
dashboard
form
two-column layout
sidebar
hero
sections
```

### GridView

Phù hợp:

```text
rất nhiều item
scrollable gallery
book list
image gallery
```

Buổi 16 chúng ta sẽ học `GridView`.

---

# 29. ResponsiveRow không phải ListView

`ListView` phù hợp:

```text
item
item
item
item
...
```

và scroll.

`ResponsiveRow` phù hợp:

```text
grid layout
```

---

# 30. Form responsive

Đây là use case cực kỳ quan trọng.

Desktop:

```text
┌────────────────┬────────────────┐
│ First Name     │ Last Name      │
└────────────────┴────────────────┘

┌──────────────────────────────────┐
│ Email                            │
└──────────────────────────────────┘
```

Mobile:

```text
┌──────────────────────────────────┐
│ First Name                      │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ Last Name                       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ Email                           │
└──────────────────────────────────┘
```

Code:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            col={
                "xs": 12,
                "md": 6,
            },
            content=ft.TextField(
                label="First Name"
            ),
        ),
        ft.Container(
            col={
                "xs": 12,
                "md": 6,
            },
            content=ft.TextField(
                label="Last Name"
            ),
        ),
        ft.Container(
            col=12,
            content=ft.TextField(
                label="Email"
            ),
        ),
    ]
)
```

---

# 31. Đây là một pattern bạn nên thuộc

```python
col={
    "xs": 12,
    "sm": 12,
    "md": 6,
    "lg": 4,
}
```

Mental model:

```text
Mobile
████████████ 12

Tablet
████████████ 12

Medium
██████ ██████
  6      6

Desktop
████ ████ ████
 4     4    4
```

---

# 32. Mobile-first

Một chiến lược tốt:

```text
xs → thiết kế mobile trước
↓
sm
↓
md
↓
lg
↓
xl
```

Ví dụ:

```python
col={
    "xs": 12,
    "md": 6,
    "lg": 4,
}
```

Bạn nói:

> Trên mobile, item full width. Khi đủ rộng, chuyển sang 2 cột. Khi desktop, chuyển sang 3 cột.

Đây là responsive design đúng nghĩa.

---

# 33. `ResponsiveRow` + `expand`

Có thể kết hợp với:

```python
expand=True
```

nhưng phải hiểu:

```text
col
→ grid allocation

expand
→ available space
```

Đừng dùng cả hai một cách tùy tiện.

Khi layout bắt đầu phức tạp, hãy xác định:

```text
Ai quyết định width?
Ai quyết định height?
Ai quyết định grid?
Ai quyết định child size?
```

Đây là tư duy constraints.

---

# 34. `col` và `width` khác nhau

Ví dụ:

```python
ft.Container(
    width=300,
    col=6,
)
```

Hai khái niệm khác nhau:

```text
width
→ kích thước cụ thể

col
→ phần grid
```

Trong responsive layout, ưu tiên suy nghĩ bằng:

```text
col
```

thay vì hard-code:

```text
width=300
```

---

# 35. Một lỗi phổ biến

Sai:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            width=300,
            col=6,
        )
    ]
)
```

Không phải lúc nào cũng sai, nhưng bạn đang trộn:

```text
grid sizing
+
fixed sizing
```

Điều này có thể làm layout khó đoán.

Hãy hỏi:

> Control này cần width cố định hay width theo grid?

Nếu theo responsive grid:

```python
col=6
```

thường là abstraction phù hợp hơn.

---

# 36. Dashboard hoàn chỉnh

Ta có thể tạo:

```python
def stat_card(title, value):
    return ft.Container(
        col={
            "xs": 12,
            "sm": 6,
            "lg": 3,
        },
        padding=20,
        border_radius=12,
        border=ft.Border.all(1),
        content=ft.Column(
            controls=[
                ft.Text(title),
                ft.Text(
                    value,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
            ]
        ),
    )
```

Sau đó:

```python
stats = ft.ResponsiveRow(
    controls=[
        stat_card("Books", "12,450"),
        stat_card("Chapters", "245,320"),
        stat_card("Sources", "18"),
        stat_card("Errors", "32"),
    ],
    spacing=20,
    run_spacing=20,
)
```

Desktop:

```text
┌──────┬──────┬──────┬──────┐
│Books │Chap. │Source│Error │
└──────┴──────┴──────┴──────┘
```

Mobile:

```text
┌─────────────────────────┐
│ Books                   │
├─────────────────────────┤
│ Chapters                │
├─────────────────────────┤
│ Sources                 │
├─────────────────────────┤
│ Errors                  │
└─────────────────────────┘
```

---

# 37. ResponsiveRow + Stack

Hai control này kết hợp rất mạnh.

Ví dụ:

```text
ResponsiveRow
├── Card 4
│   └── Stack
│       ├── Image
│       ├── Overlay
│       └── Badge
│
├── Card 4
│   └── Stack
│
└── Card 4
    └── Stack
```

ResponsiveRow:

```text
grid
```

Stack:

```text
layers
```

Container:

```text
box
```

---

# 38. Đây là kiến trúc UI rất quan trọng

Ví dụ Book Grid:

```text
ResponsiveRow
│
├── Container
│   └── Stack
│       ├── Image
│       ├── Overlay
│       ├── Badge
│       └── Info
│
├── Container
│   └── Stack
│
└── Container
    └── Stack
```

Mỗi layer có một nhiệm vụ:

```text
ResponsiveRow
→ responsive grid

Container
→ card box

Stack
→ layered card

Positioned
→ precise placement
```

Đây chính là cách bạn nên tư duy khi xây app lớn.

---

# 39. Bài tập 1 — Responsive Cards

Tạo 8 cards.

Mỗi card:

```python
col={
    "xs": 12,
    "sm": 6,
    "md": 4,
    "lg": 3,
}
```

Yêu cầu:

```text
mobile  → 1
tablet  → 2
medium  → 3
desktop → 4
```

---

# 40. Bài tập 2 — Responsive Form

Tạo form:

```text
First Name
Last Name
Email
Phone
Address
City
Country
```

Yêu cầu:

Desktop:

```text
First Name | Last Name
Email      | Phone
Address    | Address
City       | Country
```

Mobile:

```text
First Name
Last Name
Email
Phone
Address
City
Country
```

---

# 41. Bài tập 3 — Sidebar

Desktop:

```text
3 / 9
```

Mobile:

```text
12 / 12
```

Tạo:

```python
sidebar = ft.Container(
    col={
        "xs": 12,
        "lg": 3,
    },
    ...
)

main = ft.Container(
    col={
        "xs": 12,
        "lg": 9,
    },
    ...
)
```

---

# 42. Bài tập 4 — App đọc truyện

Thiết kế:

```text
Desktop:

┌───────────────┬────────────────────────────┐
│ Categories    │ Books                      │
│               │                            │
│               │ [Book][Book][Book][Book]   │
│               │ [Book][Book][Book][Book]   │
└───────────────┴────────────────────────────┘
```

Mobile:

```text
┌────────────────────────────┐
│ Categories                 │
├────────────────────────────┤
│ Book                       │
├────────────────────────────┤
│ Book                       │
├────────────────────────────┤
│ Book                       │
└────────────────────────────┘
```

Sử dụng:

```text
ResponsiveRow
+
Stack
+
Container
```

---

# 43. Bài tập 5 — TTS App

Thiết kế:

Desktop:

```text
┌──────────────────┬───────────────────────┐
│ Settings         │ Text Editor           │
│                  │                       │
│ Voice            │                       │
│ Rate             │                       │
│ Pitch            │                       │
│                  │                       │
│ [Convert]        │ [Audio Player]        │
└──────────────────┴───────────────────────┘
```

Mobile:

```text
┌──────────────────────┐
│ Settings             │
├──────────────────────┤
│ Text Editor          │
├──────────────────────┤
│ Audio Player         │
└──────────────────────┘
```

Đây sẽ rất hữu ích cho TTS CLI/Flet app mà bạn đang hướng tới.

---

# 44. Debug ResponsiveRow

Khi responsive không đúng, kiểm tra theo thứ tự:

### 1. `col`

```text
xs?
sm?
md?
lg?
```

### 2. Tổng columns

Một hàng có:

```text
≤ 12
```

hay:

```text
> 12
```

### 3. Parent width

Parent có đủ width không?

### 4. Fixed width

Bạn có đang ép:

```python
width=500
```

không?

### 5. Nested layout

Có `Row` bên trong `ResponsiveRow` không?

### 6. Spacing

`spacing` có làm layout quá chật không?

---

# 45. Mental model quan trọng nhất

Đừng nghĩ:

> ResponsiveRow = Row tự co giãn.

Hãy nghĩ:

```text
ResponsiveRow
        │
        ↓
    12-column grid
        │
        ├── xs
        ├── sm
        ├── md
        ├── lg
        ├── xl
        └── xxl
```

Mỗi child khai báo:

```text
"Ở breakpoint này, tôi chiếm bao nhiêu cột?"
```

Ví dụ:

```python
col={
    "xs": 12,
    "sm": 6,
    "lg": 3,
}
```

Nghĩa là:

```text
mobile
████████████

tablet
██████ ██████

desktop
████ ████ ████
```

---

# 46. Tổng kết Buổi 15

Bạn cần nắm chắc:

```text
ResponsiveRow
│
├── 12-column grid
│
├── col
│
├── responsive breakpoints
│   ├── xs
│   ├── sm
│   ├── md
│   ├── lg
│   ├── xl
│   └── xxl
│
├── spacing
│
├── run_spacing
│
└── responsive composition
```

Và quan trọng nhất:

```text
Row
→ sắp xếp

ResponsiveRow
→ sắp xếp theo grid responsive
```

---

# 47. Chuỗi tư duy UI hiện tại

Sau 15 buổi:

```text
Row
  ↓
horizontal layout

Column
  ↓
vertical layout

Container
  ↓
box / decoration

Stack
  ↓
layering

ResponsiveRow
  ↓
responsive grid
```

Khi kết hợp:

```text
ResponsiveRow
└── Container
    └── Stack
        ├── Image
        ├── Overlay
        ├── Badge
        └── Text
```

bạn đã có thể xây được rất nhiều UI thực tế.

---

## Roadmap

```text
11. Row Deep Dive                  ✅
12. Column Deep Dive               ✅
13. Container Deep Dive             ✅
14. Stack                           ✅
15. ResponsiveRow                   ← hiện tại
16. GridView
17. ListView
18. Tabs
19. Card, ExpansionTile, ListTile
20. Layout Constraints & Sizing
21. Alignment
22. Spacing / Padding / Margin
23. Responsive UI
24. Theme
25. Dark / Light Mode
26. Mini Project: Dashboard
```

**Buổi 16 — `GridView` Deep Dive** sẽ nối trực tiếp với bài hôm nay. Ta sẽ phân biệt rất kỹ **`ResponsiveRow` vs `GridView`**, học grid có scroll, `runs_count`, `max_extent`, lazy rendering, xây **Book Gallery**, và đặc biệt là cách chọn giữa `ResponsiveRow`, `GridView` và `ListView` khi xây app đọc truyện.
