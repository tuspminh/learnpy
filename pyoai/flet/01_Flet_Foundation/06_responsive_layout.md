# Buổi 6 — Responsive Layout trong Flet

Buổi 5 chúng ta học:

```text
Row
Column
Container
alignment
spacing
padding
width / height
expand
```

Hôm nay chúng ta đi sâu hơn:

```text
Responsive UI
     │
     ├── expand
     ├── expand_loose
     ├── ResponsiveRow
     ├── breakpoint
     ├── window size
     ├── responsive layout
     └── desktop / tablet / mobile
```

Mục tiêu cuối buổi:

> Bạn có thể xây một UI tự thay đổi bố cục khi cửa sổ thay đổi kích thước.

---

# 1. Responsive UI là gì?

Giả sử bạn có app:

```text
Desktop
┌──────────────────────────────────────┐
│ Sidebar │         Content            │
│         │                            │
│         │                            │
└──────────────────────────────────────┘
```

Khi cửa sổ nhỏ:

```text
Mobile
┌──────────────────┐
│      Header      │
├──────────────────┤
│     Content      │
│                  │
├──────────────────┤
│     Navigation   │
└──────────────────┘
```

Ta không muốn viết:

```python
desktop_app.py
tablet_app.py
mobile_app.py
```

Mà muốn:

```text
Một UI tree
      ↓
Responsive rules
      ↓
Different layout
```

---

# 2. Responsive không chỉ là "co nhỏ"

Đây là sai lầm phổ biến.

Responsive không đơn giản là:

```text
1200px
 ↓
800px
 ↓
400px
```

Responsive thực sự là:

```text
Không gian thay đổi
       ↓
Layout strategy thay đổi
```

Ví dụ:

```text
Desktop:

Sidebar + Content


Mobile:

Header
Content
Bottom navigation
```

Đó là **layout adaptation**.

---

# 3. `expand=True`

Đầu tiên ôn lại:

```python
ft.Container(
    expand=True,
)
```

Nó có nghĩa gần như:

> Hãy sử dụng phần không gian khả dụng mà layout parent cho phép.

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

Kết quả:

```text
┌─────────────────────────┐
│ Header                  │
├─────────────────────────┤
│                         │
│                         │
│      flexible area      │
│                         │
│                         │
├─────────────────────────┤
│ Footer                  │
└─────────────────────────┘
```

---

# 4. `expand` là tư duy Flexbox

Nếu bạn từng học CSS:

```css
flex: 1;
```

thì hãy liên tưởng tới:

```python
expand=True
```

Ví dụ:

```text
Row
├── Sidebar
├── Content(expand=True)
└── Actions
```

Tư duy:

```text
Sidebar
   +
Content → lấy phần còn lại
   +
Actions
```

---

# 5. Flexible spacer

Một kỹ thuật rất quan trọng:

```python
ft.Container(expand=True)
```

Ví dụ toolbar:

```python
ft.Row(
    controls=[
        ft.Text("My Library"),

        ft.Container(
            expand=True,
        ),

        ft.Button("Search"),
        ft.Button("Settings"),
    ]
)
```

Kết quả:

```text
┌─────────────────────────────────────────┐
│ My Library              Search Settings │
└─────────────────────────────────────────┘
```

Container ở giữa hoạt động như:

```text
flexible spacer
```

---

# 6. `expand_loose`

Đây là concept cần hiểu kỹ.

`expand=True` nói:

> Control có thể lấy phần không gian còn lại.

Trong một số layout, bạn có thể muốn control **được phép mở rộng nhưng không bắt buộc chiếm hết không gian**.

Đó là lúc `expand_loose` hữu ích.

Mental model:

```text
expand=True

"Give me available space."
```

trong khi:

```text
expand_loose=True

"I can use extra space, but don't force me
to consume it all."
```

Đây là distinction quan trọng khi thiết kế layout phức tạp.

---

# 7. Vấn đề của layout cố định

Ví dụ:

```python
ft.Container(
    width=1200,
    height=700,
)
```

Trên desktop:

```text
OK
```

Nhưng cửa sổ:

```text
600px
```

thì:

```text
1200px content
    ↓
overflow / clipping / layout problems
```

Do đó responsive UI cần:

```text
fixed dimensions
       ↓
chỉ dùng ở nơi thực sự cần
```

và:

```text
flexible dimensions
       ↓
expand / responsive layout
```

---

# 8. ResponsiveRow

Flet cung cấp `ResponsiveRow` để xây layout theo kiểu grid responsive.

Mental model:

```text
12-column grid
```

Ví dụ:

```text
┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
│  │  │  │  │  │  │  │  │  │  │  │  │
└──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

Một control có thể chiếm:

```text
12 / 12
6 / 12
4 / 12
3 / 12
```

---

# 9. ResponsiveRow cơ bản

Ví dụ:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            content=ft.Text("A"),
            col=6,
        ),
        ft.Container(
            content=ft.Text("B"),
            col=6,
        ),
    ]
)
```

Desktop:

```text
┌──────────────────────┬──────────────────────┐
│          A           │          B           │
└──────────────────────┴──────────────────────┘
```

Mỗi cái:

```text
6 / 12
```

---

# 10. `col`

Trong `ResponsiveRow`, bạn có thể khai báo:

```python
col=6
```

nghĩa là:

```text
6 / 12 columns
```

Ví dụ:

```python
col=3
```

nghĩa:

```text
3 / 12
```

Mental model:

```text
12-column grid

[ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ][ 9 ][10][11][12]
```

---

# 11. Ba card

Ví dụ:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            content=ft.Text("Card 1"),
            col=4,
        ),
        ft.Container(
            content=ft.Text("Card 2"),
            col=4,
        ),
        ft.Container(
            content=ft.Text("Card 3"),
            col=4,
        ),
    ]
)
```

Desktop:

```text
┌────────────┬────────────┬────────────┐
│ Card 1     │ Card 2     │ Card 3     │
└────────────┴────────────┴────────────┘
```

Mỗi card:

```text
4 / 12
```

---

# 12. Khi màn hình nhỏ

Điểm mạnh của `ResponsiveRow` là có thể định nghĩa kích thước theo breakpoint.

Tư duy:

```text
Desktop
4 / 12

Tablet
6 / 12

Mobile
12 / 12
```

Ví dụ theo API Flet hiện tại, bạn có thể cấu hình breakpoint-specific column spans trong `col`.

Mental model:

```text
xs → mobile
sm → small
md → medium
lg → large
xl → extra large
```

---

# 13. Ví dụ Responsive Cards

Ví dụ:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            content=ft.Text("Card 1"),
            col={
                "xs": 12,
                "sm": 6,
                "md": 4,
            },
        ),
        ft.Container(
            content=ft.Text("Card 2"),
            col={
                "xs": 12,
                "sm": 6,
                "md": 4,
            },
        ),
        ft.Container(
            content=ft.Text("Card 3"),
            col={
                "xs": 12,
                "sm": 6,
                "md": 4,
            },
        ),
    ]
)
```

Tư duy:

```text
xs:
┌──────────────┐
│ Card 1       │
├──────────────┤
│ Card 2       │
├──────────────┤
│ Card 3       │
└──────────────┘
```

Tablet:

```text
┌──────────┬──────────┐
│ Card 1   │ Card 2   │
├──────────┴──────────┤
│ Card 3              │
└─────────────────────┘
```

Desktop:

```text
┌────────┬────────┬────────┐
│ Card 1 │ Card 2 │ Card 3 │
└────────┴────────┴────────┘
```

---

# 14. Đây là sức mạnh thật sự của ResponsiveRow

Bạn không cần:

```python
if desktop:
    ...

if tablet:
    ...

if mobile:
    ...
```

cho từng control.

Thay vào đó:

```text
ResponsiveRow
     ↓
Grid
     ↓
Breakpoint
     ↓
Column span
```

---

# 15. Grid thinking

Khi thiết kế Dashboard:

```text
12 columns
```

Ví dụ:

```text
Sidebar = 3
Content = 9
```

```text
┌───────┬─────────────────────┐
│       │                     │
│  3    │         9           │
│       │                     │
└───────┴─────────────────────┘
```

Mobile:

```text
Sidebar = 12
Content = 12
```

```text
┌──────────────────────────────┐
│ Sidebar                      │
├──────────────────────────────┤
│ Content                      │
└──────────────────────────────┘
```

---

# 16. Responsive Reader App

Đây là ví dụ rất phù hợp với project đọc truyện của bạn.

Desktop:

```text
┌──────────────────────────────────────────────┐
│                 Reader Header                │
├──────────────┬───────────────────────────────┤
│ Chapter List │                               │
│              │       Chapter Content         │
│              │                               │
│              │                               │
└──────────────┴───────────────────────────────┘
```

Có thể tư duy:

```text
ResponsiveRow
├── ChapterList
│      col = 3
│
└── Content
       col = 9
```

Mobile:

```text
┌────────────────────────┐
│ Reader Header          │
├────────────────────────┤
│ Chapter Content        │
│                        │
│                        │
├────────────────────────┤
│ Navigation             │
└────────────────────────┘
```

---

# 17. Responsive không nhất thiết phải là ResponsiveRow

Đây là điểm rất quan trọng.

Có ba chiến lược:

```text
1. Flexible layout
2. ResponsiveRow
3. Conditional layout
```

---

# 18. Flexible layout

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

Dùng khi:

```text
layout không cần thay đổi cấu trúc
```

Chỉ cần:

```text
chiếm không gian còn lại
```

---

# 19. ResponsiveRow

Dùng khi:

```text
Grid
Cards
Dashboard
Forms
Gallery
```

Ví dụ:

```text
Desktop
3 cards / row

Tablet
2 cards / row

Mobile
1 card / row
```

---

# 20. Conditional layout

Có trường hợp layout thực sự phải thay đổi.

Ví dụ:

Desktop:

```text
Sidebar + Content
```

Mobile:

```text
Drawer + Content
```

Lúc này:

```python
if is_mobile:
    ...
else:
    ...
```

là hợp lý.

Đừng cố nhồi mọi thứ vào `ResponsiveRow`.

---

# 21. Làm sao biết kích thước cửa sổ?

Flet có thông tin kích thước cửa sổ/page tùy theo phiên bản và loại app.

Một pattern thường dùng là đọc kích thước hiện tại:

```python
page.width
page.height
```

Sau đó:

```python
if page.width < 600:
    ...
```

Tuy nhiên:

> Không nên biến toàn bộ UI thành hàng trăm `if page.width`.

Đó sẽ trở thành responsive code rất khó bảo trì.

---

# 22. Breakpoint

Ta có thể định nghĩa:

```python
MOBILE = 600
TABLET = 900
```

Mental model:

```text
width < 600
    ↓
mobile

600 <= width < 900
    ↓
tablet

width >= 900
    ↓
desktop
```

Ví dụ:

```python
def get_layout_mode(width):
    if width < 600:
        return "mobile"

    if width < 900:
        return "tablet"

    return "desktop"
```

Đây là cách tốt hơn việc rải magic number khắp code.

---

# 23. Responsive State

Một app có thể có:

```python
layout_mode = "desktop"
```

Khi resize:

```text
desktop
   ↓
tablet
   ↓
mobile
```

Ta có:

```text
Application State
├── data
├── loading
├── error
└── layout_mode
```

Điều này rất quan trọng.

Responsive không chỉ là UI.

Nó có thể ảnh hưởng đến:

* navigation
* toolbar
* sidebar
* dialog
* card layout

---

# 24. Một Responsive Dashboard

Ta bắt đầu với:

```python
import flet as ft


def main(page: ft.Page):

    sidebar = ft.Container(
        width=220,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Library"),
                ft.Button("Books"),
                ft.Button("History"),
                ft.Button("Favorites"),
            ],
        ),
    )

    content = ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Books",
                    size=30,
                ),
            ],
        ),
    )

    body = ft.Row(
        controls=[
            sidebar,
            content,
        ],
        expand=True,
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text("Header"),
                body,
            ],
            expand=True,
        )
    )


ft.run(main)
```

Desktop hoạt động khá tốt.

Nhưng mobile?

```text
Sidebar 220px
+
Content
```

có thể trở nên chật.

---

# 25. Mobile strategy

Ta có thể chuyển:

```text
Desktop

Sidebar | Content
```

thành:

```text
Mobile

Header
Content
Navigation
```

Đây là lúc **conditional layout** hợp lý.

---

# 26. Tách layout components

Đừng viết:

```python
if mobile:
    page.add(...)
else:
    page.add(...)
```

ngay trong `main()`.

Tốt hơn:

```python
def build_desktop_layout():
    ...


def build_mobile_layout():
    ...


def build_layout():
    ...
```

Ví dụ:

```python
def build_desktop_layout():
    return ft.Row(
        controls=[
            build_sidebar(),
            build_content(),
        ],
        expand=True,
    )
```

và:

```python
def build_mobile_layout():
    return ft.Column(
        controls=[
            build_content(),
            build_mobile_navigation(),
        ],
        expand=True,
    )
```

---

# 27. Component architecture

Lúc này code bắt đầu có hình dạng:

```text
App
│
├── Header
├── Sidebar
├── Content
├── MobileNavigation
│
└── Layout
     ├── DesktopLayout
     └── MobileLayout
```

Đây là nền móng để sau này xây:

```text
Novel Reader
Crawler Dashboard
TTS App
```

---

# 28. Responsive Cards cho Novel App

Giả sử:

```python
books = [
    "One Piece",
    "Naruto",
    "Bleach",
    "Dragon Ball",
]
```

Ta có thể tạo:

```python
def build_book_card(title):
    return ft.Container(
        padding=15,
        content=ft.Column(
            controls=[
                ft.Text(title),
                ft.Button("Read"),
            ],
        ),
    )
```

Sau đó:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            content=build_book_card(book),
            col={
                "xs": 12,
                "sm": 6,
                "md": 4,
                "lg": 3,
            },
        )
        for book in books
    ]
)
```

Mental model:

```text
xs → 1 card / row
sm → 2 cards / row
md → 3 cards / row
lg → 4 cards / row
```

Đây là pattern cực kỳ mạnh cho thư viện truyện.

---

# 29. Gallery

Cũng có thể dùng cho:

```text
Book covers
Image gallery
Products
Characters
Authors
```

Ví dụ:

```text
Desktop:

┌────┬────┬────┬────┐
│ A  │ B  │ C  │ D  │
├────┼────┼────┼────┤
│ E  │ F  │ G  │ H  │
└────┴────┴────┴────┘
```

Mobile:

```text
┌──────────┐
│ A        │
├──────────┤
│ B        │
├──────────┤
│ C        │
└──────────┘
```

---

# 30. Responsive Form

Desktop:

```text
┌───────────────────────┬───────────────────────┐
│ First name            │ Last name             │
└───────────────────────┴───────────────────────┘
```

Mobile:

```text
┌─────────────────────────────┐
│ First name                  │
├─────────────────────────────┤
│ Last name                   │
└─────────────────────────────┘
```

`ResponsiveRow` rất phù hợp.

Ví dụ:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            content=ft.TextField(
                label="First name",
            ),
            col={
                "xs": 12,
                "md": 6,
            },
        ),
        ft.Container(
            content=ft.TextField(
                label="Last name",
            ),
            col={
                "xs": 12,
                "md": 6,
            },
        ),
    ]
)
```

---

# 31. Responsive TTS App

Đây là một bài toán thực tế.

Desktop:

```text
┌──────────────────────────────────────────────┐
│ TTS Studio                         Settings  │
├───────────────────────┬──────────────────────┤
│                       │                      │
│ Text                  │ Voice                │
│                       │ Rate                 │
│                       │ Pitch                │
│                       │ Volume               │
│                       │                      │
│                       │ [ Convert ]          │
└───────────────────────┴──────────────────────┘
```

Mobile:

```text
┌───────────────────────┐
│ TTS Studio            │
├───────────────────────┤
│ Text                  │
│                       │
├───────────────────────┤
│ Voice                 │
│ Rate                  │
│ Pitch                 │
│ Volume                │
│                       │
│ [ Convert ]           │
└───────────────────────┘
```

Responsive architecture:

```text
Desktop
    Row
    ├── TextEditor
    └── SettingsPanel

Mobile
    Column
    ├── TextEditor
    └── SettingsPanel
```

---

# 32. Responsive + State

Một lỗi kiến trúc thường gặp:

```python
def on_resize(e):
    # thay đổi business state
    ...
```

Không nên.

Resize là:

```text
Presentation concern
```

Business state:

```text
Text
Voice
Rate
Pitch
Volume
```

Layout state:

```text
Desktop
Tablet
Mobile
```

Nên tách:

```text
Application State
│
├── Business State
│   ├── text
│   ├── voice
│   └── rate
│
└── UI State
    ├── loading
    └── layout_mode
```

---

# 33. Một nguyên tắc rất quan trọng

### Responsive không được phá domain logic.

Ví dụ:

```python
def convert_text():
    ...
```

không được chứa:

```python
if page.width < 600:
    ...
```

Tốt hơn:

```text
UI
 ↓
Use Case
 ↓
TTS Service
```

Responsive chỉ nằm ở:

```text
UI / Presentation Layer
```

Đây chính là điều sau này cực kỳ hữu ích khi chúng ta học:

* MVC
* MVVM
* Clean Architecture
* Domain-Driven Design

---

# 34. Responsive UI Tree

Hãy học cách thiết kế:

```text
Page
│
└── AppShell
    │
    ├── Header
    │
    └── ResponsiveBody
        │
        ├── Desktop
        │    ├── Sidebar
        │    └── Content
        │
        └── Mobile
             ├── Content
             └── Navigation
```

Đây là architecture tốt hơn:

```text
main()
    500 dòng UI code
```

---

# 35. Khi nào dùng cái gì?

| Nhu cầu                      | Công cụ              |
| ---------------------------- | -------------------- |
| Xếp dọc                      | `Column`             |
| Xếp ngang                    | `Row`                |
| Flexible space               | `expand`             |
| Box/wrapper                  | `Container`          |
| Grid responsive              | `ResponsiveRow`      |
| Desktop/mobile khác cấu trúc | Conditional layout   |
| Khoảng cách children         | `spacing`            |
| Khoảng cách bên trong        | `padding`            |
| Khoảng cách bên ngoài        | `margin`             |
| Căn main axis                | `MainAxisAlignment`  |
| Căn cross axis               | `CrossAxisAlignment` |

---

# 36. Sai lầm số 1 — Hard-code kích thước

Không nên:

```python
width=1200
```

ở mọi nơi.

Hãy hỏi:

> Có thực sự cần 1200 không?

Nếu không:

```python
expand=True
```

hoặc:

```python
ResponsiveRow
```

---

# 37. Sai lầm số 2 — Quá nhiều `if width`

Không nên:

```python
if width < 600:
    ...
elif width < 700:
    ...
elif width < 800:
    ...
elif width < 900:
    ...
```

Đây là dấu hiệu responsive logic đang bị phân tán.

Hãy dùng:

```text
breakpoint
+
layout component
```

---

# 38. Sai lầm số 3 — Dùng ResponsiveRow cho mọi thứ

Không phải mọi UI đều cần grid.

Nếu chỉ cần:

```text
Sidebar | Content
```

thì:

```python
Row
```

*

```python
expand=True
```

có thể đơn giản và tốt hơn.

---

# 39. Sai lầm số 4 — Không nghĩ tới parent

Nếu:

```python
child.expand = True
```

nhưng parent không có không gian để expand, bạn sẽ không nhận được kết quả mong muốn.

Luôn suy nghĩ:

```text
Parent
 ↓
Available space
 ↓
Child
```

Không suy nghĩ:

```text
Child
 ↓
expand=True
```

một cách độc lập.

---

# 40. Mental Model quan trọng nhất của Buổi 6

Hãy nhớ 4 tầng:

```text
                 Window
                    │
                    ▼
                  Page
                    │
                    ▼
               Layout Parent
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Fixed              Flexible
      width/height        expand
          │                   │
          └─────────┬─────────┘
                    ▼
              Responsive UI
```

Và:

```text
Responsive
│
├── Flexible space
│     └── expand
│
├── Grid
│     └── ResponsiveRow
│
└── Structural adaptation
      └── Desktop/Mobile layout
```

---

# Bài tập Buổi 6 — Responsive Novel Library

Hãy xây một giao diện:

```text
Desktop
┌────────────────────────────────────────────────────────┐
│ My Novel Library                         [Search]      │
├────────────────┬───────────────────────────────────────┤
│                │                                       │
│  Categories    │  Books                                │
│                │                                       │
│  All           │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│  Completed     │  │ Book │ │ Book │ │ Book │ │ Book │ │
│  Reading      │  │  1   │ │  2   │ │  3   │ │  4   │ │
│  Favorites     │  └──────┘ └──────┘ └──────┘ └──────┘ │
│                │                                       │
└────────────────┴───────────────────────────────────────┘
```

### Desktop

```text
Sidebar = 3/12
Content = 9/12
```

### Tablet

```text
Sidebar = 4/12
Content = 8/12
```

### Mobile

```text
Sidebar = hidden
Content = 12/12
```

### Books

Dùng:

```text
xs = 12
sm = 6
md = 4
lg = 3
```

Tức:

```text
Mobile → 1 card
Tablet → 2 cards
Medium → 3 cards
Large → 4 cards
```

---

# Bài tập Deep Dive

Thiết kế architecture:

```text
NovelLibraryApp
│
├── state
│   ├── books
│   ├── selected_category
│   ├── search_text
│   └── layout_mode
│
├── components
│   ├── Header
│   ├── Sidebar
│   ├── BookCard
│   └── BookGrid
│
└── layouts
    ├── DesktopLayout
    ├── TabletLayout
    └── MobileLayout
```

**Chưa cần database, chưa cần API.**

Mục tiêu là tập trung hoàn toàn vào **layout architecture**.

---

## Roadmap tiếp theo

```text
Buổi 1  → Flet architecture
Buổi 2  → Page / Control / Event
Buổi 3  → State & update
Buổi 4  → Text / Button / TextField / Image
Buổi 5  → Row / Column / Container
Buổi 6  → Responsive Layout              ← hiện tại
Buổi 7  → Navigation & View
Buổi 8  → Dialog / BottomSheet / SnackBar
Buổi 9  → Form & Validation
Buổi 10 → Theme & Styling
Buổi 11 → Component Design
Buổi 12 → State Management
...
```

Ở **Buổi 7**, chúng ta sẽ bắt đầu một bước rất quan trọng: **Navigation trong Flet** — `View`, route, `page.go()`, `page.on_route_change`, nested navigation và thiết kế cấu trúc **nhiều màn hình** cho một ứng dụng thực tế như **Novel Reader / TTS / Crawler Dashboard**.
