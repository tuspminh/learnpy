# Buổi 23 — Responsive UI trong Flet

Hôm nay chúng ta đi vào một phần rất quan trọng của Flet:

> **Làm thế nào để một UI tự thích nghi khi chạy trên Desktop, Tablet và Mobile?**

Đặc biệt với các app bạn đang hướng tới như:

* 📚 App đọc truyện
* 🕷️ Crawl Dashboard
* 🎧 TTS App
* 📋 Queue/Worker Dashboard

thì Responsive UI gần như bắt buộc.

---

# 1. Responsive UI là gì?

Một UI responsive không có nghĩa là:

```text
Desktop UI
↓
thu nhỏ lại
↓
Mobile UI
```

Mà là:

```text
Screen size
     ↓
Layout strategy
     ↓
UI phù hợp
```

Ví dụ Desktop:

```text
┌─────────────────────────────────────────────┐
│ Sidebar │          Main Content             │
│         │                                   │
│         │                                   │
└─────────────────────────────────────────────┘
```

Mobile:

```text
┌──────────────────────┐
│ ☰   Dashboard        │
├──────────────────────┤
│                      │
│ Main Content         │
│                      │
└──────────────────────┘
```

Không phải chỉ thay đổi width.

Mà **thay đổi cấu trúc layout**.

---

# 2. Responsive gồm những gì?

Trong Flet, bạn cần quan tâm:

```text
Screen
│
├── width
├── height
│
├── breakpoint
│
├── layout
│
├── navigation
│
├── spacing
│
└── component size
```

Ví dụ:

```text
Desktop
> 1200px

Tablet
768–1199px

Mobile
< 768px
```

Đây chỉ là **design breakpoint** do chúng ta tự định nghĩa.

---

# 3. Sai lầm phổ biến nhất

Người mới thường viết:

```python
ft.Container(
    width=1200,
)
```

và:

```python
ft.Row(
    controls=[
        sidebar,
        content,
    ]
)
```

Sau đó chạy trên mobile:

```text
┌────────────────────┐
│ Sidebar │ Content  │
│         │          │
│         │          │
└────────────────────┘
```

Mọi thứ bị chật.

Responsive UI không nên dựa quá nhiều vào:

```text
width cố định
height cố định
```

---

# 4. Nguyên tắc đầu tiên

Hãy ưu tiên:

```text
flexible sizing
```

thay vì:

```text
fixed sizing
```

Ví dụ tốt:

```python
ft.Container(
    expand=True,
)
```

thay vì:

```python
ft.Container(
    width=1200,
)
```

---

# 5. `expand` là nền tảng Responsive

Ví dụ:

```python
ft.Row(
    expand=True,
    controls=[
        sidebar,
        ft.Container(
            expand=True,
            content=content,
        ),
    ],
)
```

Mental model:

```text
Row
│
├── Sidebar
│
└── Content
    expand=True
    ↓
    lấy phần còn lại
```

Khi màn hình thay đổi:

```text
Desktop
────────────────────────────
Sidebar |       Content
────────────────────────────

Mobile
────────────────
Sidebar | Content
────────────────
```

Tuy nhiên mobile vẫn chưa tốt nếu sidebar luôn tồn tại.

Chúng ta cần **breakpoint**.

---

# 6. Breakpoint là gì?

Breakpoint là mốc kích thước để thay đổi layout.

Ví dụ:

```text
width >= 1200
    Desktop

768 <= width < 1200
    Tablet

width < 768
    Mobile
```

Ta có:

```python
def get_layout_mode(width: float):
    if width >= 1200:
        return "desktop"

    if width >= 768:
        return "tablet"

    return "mobile"
```

---

# 7. Đây là tư duy quan trọng

Đừng nghĩ:

```text
if width < 768:
    width = 500
```

Hãy nghĩ:

```text
if mobile:
    layout = mobile_layout

elif tablet:
    layout = tablet_layout

else:
    layout = desktop_layout
```

Responsive tốt là **thay đổi chiến lược layout**, không chỉ thay đổi vài con số.

---

# 8. Theo dõi kích thước màn hình

Trong Flet, bạn có thể theo dõi kích thước cửa sổ/trang thông qua event resize của page/window tùy cách app được triển khai.

Một pattern responsive điển hình là:

```python
def on_resize(e):
    print(page.width, page.height)

page.on_resize = on_resize
```

Sau khi resize:

```text
page.width
page.height
```

cho bạn thông tin để quyết định layout.

---

# 9. Ví dụ đơn giản

```python
import flet as ft


def main(page: ft.Page):

    def on_resize(e):
        print(
            "width:",
            page.width,
            "height:",
            page.height,
        )

    page.on_resize = on_resize

    page.add(
        ft.Text("Responsive App")
    )


ft.run(main)
```

Resize cửa sổ và quan sát terminal.

---

# 10. Tạo breakpoint helper

Thay vì lặp:

```python
if page.width < 768:
```

ở khắp nơi, tạo:

```python
def is_mobile(page: ft.Page) -> bool:
    return page.width < 768
```

và:

```python
def is_tablet(page: ft.Page) -> bool:
    return 768 <= page.width < 1200
```

```python
def is_desktop(page: ft.Page) -> bool:
    return page.width >= 1200
```

Nhưng app lớn còn tốt hơn nếu dùng một abstraction riêng.

---

# 11. Tạo `Breakpoint`

```python
from enum import Enum


class Breakpoint(Enum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
```

Sau đó:

```python
def get_breakpoint(width: float) -> Breakpoint:
    if width < 768:
        return Breakpoint.MOBILE

    if width < 1200:
        return Breakpoint.TABLET

    return Breakpoint.DESKTOP
```

Đây là cách tốt hơn việc dùng string rải rác.

---

# 12. Responsive Layout Factory

Ta có thể xây:

```python
def build_layout(page: ft.Page):
    breakpoint = get_breakpoint(page.width)

    if breakpoint == Breakpoint.MOBILE:
        return build_mobile_layout()

    if breakpoint == Breakpoint.TABLET:
        return build_tablet_layout()

    return build_desktop_layout()
```

Đây là pattern rất mạnh.

```text
Screen
 ↓
Breakpoint
 ↓
Layout Factory
 ↓
Desktop / Tablet / Mobile
```

---

# 13. Desktop layout

Ví dụ Crawl Dashboard:

```text
┌────────────────────────────────────────────┐
│ Header                                     │
├──────────────┬─────────────────────────────┤
│ Sidebar      │ Dashboard                   │
│              │                             │
│ Jobs         │ Stats                       │
│ Workers      │                             │
│ Sources      │ Recent Jobs                 │
│ Settings     │                             │
└──────────────┴─────────────────────────────┘
```

Code concept:

```python
def build_desktop_layout():
    return ft.Row(
        expand=True,
        controls=[
            build_sidebar(),
            ft.Container(
                expand=True,
                content=build_dashboard(),
            ),
        ],
    )
```

---

# 14. Mobile layout

Mobile:

```text
┌───────────────────────┐
│ ☰   Dashboard         │
├───────────────────────┤
│                       │
│ Stats                 │
│                       │
│ Recent Jobs           │
│                       │
│ Workers               │
│                       │
└───────────────────────┘
```

Sidebar không nên chiếm cố định 250px.

Thay vào đó:

```text
Sidebar
↓
Navigation Drawer / Menu
```

Ví dụ concept:

```python
def build_mobile_layout():
    return ft.Column(
        expand=True,
        controls=[
            build_mobile_header(),
            build_dashboard(),
        ],
    )
```

---

# 15. Đây là Responsive thật

Desktop:

```text
Sidebar + Content
```

Mobile:

```text
Header + Content
```

Đây mới là responsive architecture.

---

# 16. ResponsiveRow

Flet cung cấp `ResponsiveRow`, rất hữu ích cho grid layout.

Mental model:

```text
12-column grid
```

Ví dụ:

```text
┌────┬────┬────┬────┬────┬────┐
│    │    │    │    │    │    │
└────┴────┴────┴────┴────┴────┘
```

Bạn có thể phân bố component theo số cột.

---

# 17. Ví dụ ResponsiveRow

Concept:

```python
ft.ResponsiveRow(
    controls=[
        ft.Container(
            col=6,
            content=card1,
        ),
        ft.Container(
            col=6,
            content=card2,
        ),
    ],
)
```

Desktop:

```text
┌──────────────────┬──────────────────┐
│ Card 1           │ Card 2           │
└──────────────────┴──────────────────┘
```

---

# 18. Responsive column span

Ta có thể định nghĩa:

```python
col={
    "sm": 12,
    "md": 6,
    "lg": 4,
}
```

Ý tưởng:

```text
small
→ 12 columns

medium
→ 6 columns

large
→ 4 columns
```

Kết quả:

### Mobile

```text
┌────────────────────┐
│ Card 1             │
├────────────────────┤
│ Card 2             │
├────────────────────┤
│ Card 3             │
└────────────────────┘
```

### Tablet

```text
┌──────────────┬──────────────┐
│ Card 1       │ Card 2       │
├──────────────┼──────────────┤
│ Card 3       │ Card 4       │
└──────────────┴──────────────┘
```

### Desktop

```text
┌────────┬────────┬────────┐
│ Card 1 │ Card 2 │ Card 3 │
└────────┴────────┴────────┘
```

---

# 19. Đây là lý do `ResponsiveRow` rất mạnh

Thay vì:

```python
if mobile:
    ...
elif tablet:
    ...
else:
    ...
```

cho từng Card, bạn có thể để grid system xử lý.

```text
ResponsiveRow
       ↓
breakpoint
       ↓
column span
       ↓
automatic layout
```

---

# 20. Dashboard Stats

Đây là use case hoàn hảo.

```text
Queue
Running
Completed
Failed
```

Desktop:

```text
┌────────┬────────┬────────┬────────┐
│ Queue  │Running │Completed│ Failed │
└────────┴────────┴────────┴────────┘
```

Mobile:

```text
┌──────────────────┐
│ Queue            │
├──────────────────┤
│ Running          │
├──────────────────┤
│ Completed        │
├──────────────────┤
│ Failed           │
└──────────────────┘
```

---

# 21. GridView vs ResponsiveRow

Đây là một điểm quan trọng.

### `ResponsiveRow`

Phù hợp khi:

```text
layout có cấu trúc
```

Ví dụ:

```text
Stats
│
├── Queue
├── Running
├── Completed
└── Failed
```

### `GridView`

Phù hợp khi:

```text
danh sách item động
```

Ví dụ:

```text
Book
Book
Book
Book
Book
Book
...
```

---

# 22. Responsive Book Library

Desktop:

```text
┌──────┬──────┬──────┬──────┬──────┐
│ Book │ Book │ Book │ Book │ Book │
├──────┼──────┼──────┼──────┼──────┤
│ Book │ Book │ Book │ Book │ Book │
└──────┴──────┴──────┴──────┴──────┘
```

Mobile:

```text
┌────────────────┐
│      Book      │
├────────────────┤
│      Book      │
├────────────────┤
│      Book      │
└────────────────┘
```

Với số lượng item không biết trước:

```text
GridView
```

thường phù hợp hơn.

---

# 23. Responsive Sidebar

Đây là bài toán phổ biến nhất.

Desktop:

```text
┌────────────┬───────────────────────┐
│ Sidebar    │ Content               │
│            │                       │
└────────────┴───────────────────────┘
```

Mobile:

```text
┌───────────────────────┐
│ ☰ Dashboard           │
├───────────────────────┤
│                       │
│ Content               │
│                       │
└───────────────────────┘
```

Chiến lược:

```text
Desktop
→ permanent sidebar

Mobile
→ drawer
```

---

# 24. Đừng chỉ resize Sidebar

Sai:

```python
if mobile:
    sidebar.width = 60
```

Bạn vẫn đang giữ:

```text
Sidebar
```

trong layout.

Đúng hơn:

```python
if mobile:
    hide sidebar
    show menu button
```

Đây là **structural responsive design**.

---

# 25. Navigation responsive

Desktop:

```text
Sidebar
├── Dashboard
├── Books
├── Chapters
├── Workers
└── Settings
```

Mobile:

```text
☰
```

Click:

```text
┌──────────────────┐
│ Dashboard        │
│ Books            │
│ Chapters         │
│ Workers          │
│ Settings         │
└──────────────────┘
```

---

# 26. Responsive typography

Không chỉ layout.

Font size cũng có thể thay đổi:

```python
if mobile:
    title_size = 20
else:
    title_size = 28
```

Nhưng không nên lạm dụng.

Ưu tiên:

```text
responsive layout
```

trước:

```text
responsive font
```

---

# 27. Responsive spacing

Desktop:

```text
padding = 32
spacing = 24
```

Mobile:

```text
padding = 16
spacing = 12
```

Ví dụ:

```python
def get_page_padding(width):
    if width < 768:
        return 16

    if width < 1200:
        return 24

    return 32
```

---

# 28. Responsive card

Desktop:

```text
┌───────────────────────────┐
│ Book                      │
│ 1200 chapters             │
│ [Read] [Download]         │
└───────────────────────────┘
```

Mobile:

```text
┌────────────────┐
│ Book           │
│ 1200 chapters  │
│                │
│ [Read]         │
│ [Download]     │
└────────────────┘
```

Không nhất thiết chỉ giảm width.

Có thể đổi:

```text
Row buttons
```

thành:

```text
Column buttons
```

---

# 29. Responsive component

Một component tốt có thể nhận breakpoint:

```python
def build_book_card(book, breakpoint):
    if breakpoint == Breakpoint.MOBILE:
        return build_mobile_book_card(book)

    return build_desktop_book_card(book)
```

Nhưng đừng tạo quá nhiều nhánh.

Nếu layout có thể tự co giãn:

```text
prefer flexible layout
```

Nếu cấu trúc thực sự khác:

```text
use breakpoint-specific layout
```

---

# 30. Một nguyên tắc rất quan trọng

> **Responsive không có nghĩa là mọi component đều phải biết screen width.**

Sai:

```python
class BookCard:
    if page.width < 768:
        ...
```

mọi nơi.

Điều này tạo coupling:

```text
BookCard
 ↓
Page
 ↓
Screen
```

Tốt hơn:

```text
Page/Layout
 ↓
quyết định layout
 ↓
BookCard
```

Component càng độc lập càng tốt.

---

# 31. Responsive Architecture

Một kiến trúc tốt:

```text
Page
 │
 ├── detect breakpoint
 │
 └── Layout
      │
      ├── DesktopLayout
      │
      ├── TabletLayout
      │
      └── MobileLayout
             │
             └── shared components
```

Ví dụ:

```text
DesktopLayout
 ├── Sidebar
 ├── Header
 └── Dashboard

MobileLayout
 ├── MobileHeader
 └── Dashboard
```

`Dashboard` có thể dùng chung.

---

# 32. Shared Content

Đây là cách tôi khuyên bạn thiết kế:

```python
def build_dashboard_content():
    return ft.Column(
        controls=[
            build_stats(),
            build_recent_jobs(),
            build_workers(),
        ]
    )
```

Desktop:

```python
def build_desktop_layout():
    return ft.Row(
        controls=[
            build_sidebar(),
            build_dashboard_content(),
        ]
    )
```

Mobile:

```python
def build_mobile_layout():
    return ft.Column(
        controls=[
            build_mobile_header(),
            build_dashboard_content(),
        ]
    )
```

Như vậy:

```text
Business UI
      ↑
shared

Navigation/Layout
      ↑
responsive
```

---

# 33. Đây là kiến trúc rất đáng nhớ

```text
                    ┌── Desktop Layout
                    │
Page ── Breakpoint ─┼── Tablet Layout
                    │
                    └── Mobile Layout
                           │
                           ↓
                    Shared Components
                           │
                           ↓
                         Data
```

Đây là cách tránh duplication.

---

# 34. Responsive Book Reader

Với app đọc truyện của bạn:

### Desktop

```text
┌──────────────────────────────────────────┐
│ Sidebar │ Chapter                        │
│         │                                │
│         │        Story Content           │
│         │                                │
└──────────────────────────────────────────┘
```

### Tablet

```text
┌──────────────────────────────────────────┐
│ Header                                   │
├──────────────────────────────────────────┤
│             Story Content                │
└──────────────────────────────────────────┘
```

### Mobile

```text
┌──────────────────────┐
│ ← Chapter 120     ☰ │
├──────────────────────┤
│                      │
│   Story Content      │
│                      │
└──────────────────────┘
```

Ba breakpoint có thể có ba navigation strategy.

---

# 35. Responsive Crawl Dashboard

Desktop:

```text
┌─────────────┬────────────────────────────┐
│ Sidebar     │ Dashboard                  │
│             │                            │
│ Jobs        │ Stats                      │
│ Workers     │                            │
│ Sources     │ Jobs                       │
└─────────────┴────────────────────────────┘
```

Mobile:

```text
┌──────────────────────┐
│ ☰ Crawl Dashboard    │
├──────────────────────┤
│ Queue                │
│ Running              │
│ Completed            │
│                      │
│ Recent Jobs          │
│                      │
│ Workers              │
└──────────────────────┘
```

---

# 36. Một implementation hoàn chỉnh

Đây là skeleton rất đáng học:

```python
import flet as ft
from enum import Enum


class Breakpoint(Enum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


def get_breakpoint(width: float) -> Breakpoint:
    if width < 768:
        return Breakpoint.MOBILE

    if width < 1200:
        return Breakpoint.TABLET

    return Breakpoint.DESKTOP


def build_stats():
    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={
                    "sm": 12,
                    "md": 6,
                    "lg": 3,
                },
                content=ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Text("Queue: 120"),
                    )
                ),
            ),
            ft.Container(
                col={
                    "sm": 12,
                    "md": 6,
                    "lg": 3,
                },
                content=ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Text("Running: 5"),
                    )
                ),
            ),
            ft.Container(
                col={
                    "sm": 12,
                    "md": 6,
                    "lg": 3,
                },
                content=ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Text("Completed: 1250"),
                    )
                ),
            ),
            ft.Container(
                col={
                    "sm": 12,
                    "md": 6,
                    "lg": 3,
                },
                content=ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Text("Failed: 12"),
                    )
                ),
            ),
        ],
    )


def build_dashboard_content():
    return ft.Column(
        expand=True,
        spacing=24,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text(
                "Crawl Dashboard",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            build_stats(),
            ft.Text("Recent Jobs"),
            ft.Text("Workers"),
        ],
    )


def build_sidebar():
    return ft.Container(
        width=240,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text("Crawler"),
                ft.Text("Dashboard"),
                ft.Text("Jobs"),
                ft.Text("Workers"),
                ft.Text("Sources"),
                ft.Text("Settings"),
            ],
        ),
    )


def build_desktop_layout():
    return ft.Row(
        expand=True,
        controls=[
            build_sidebar(),
            ft.VerticalDivider(),
            ft.Container(
                expand=True,
                content=build_dashboard_content(),
            ),
        ],
    )


def build_mobile_layout():
    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                    ),
                    ft.Text("Crawl Dashboard"),
                ],
            ),
            ft.Container(
                expand=True,
                content=build_dashboard_content(),
            ),
        ],
    )


def main(page: ft.Page):

    page.padding = 0

    current_layout = None

    def rebuild():
        nonlocal current_layout

        breakpoint = get_breakpoint(page.width)

        if breakpoint == Breakpoint.MOBILE:
            new_layout = build_mobile_layout()
        else:
            new_layout = build_desktop_layout()

        page.controls.clear()
        page.add(new_layout)

        current_layout = breakpoint
        page.update()

    def on_resize(e):
        nonlocal current_layout

        breakpoint = get_breakpoint(page.width)

        if breakpoint != current_layout:
            rebuild()

    page.on_resize = on_resize

    rebuild()


ft.run(main)
```

Điểm quan trọng nhất trong code không phải syntax.

Mà là architecture:

```text
resize
 ↓
detect breakpoint
 ↓
nếu breakpoint thay đổi
 ↓
rebuild layout
```

---

# 37. Đừng rebuild mỗi pixel

Một lỗi:

```python
def on_resize(e):
    rebuild()
```

Nếu user kéo cửa sổ:

```text
1200
1199
1198
1197
1196
...
```

Bạn có thể rebuild liên tục.

Tốt hơn:

```python
breakpoint = get_breakpoint(page.width)

if breakpoint != current_breakpoint:
    rebuild()
```

Ví dụ:

```text
1200 → 1199
```

vẫn Desktop → không rebuild.

Nhưng:

```text
1200 → 1190
```

không cần.

Chỉ khi:

```text
1200 → 1199
```

nếu breakpoint của bạn định nghĩa 1200 là Desktop thì mới chuyển sang Tablet.

---

# 38. Đây là một optimization quan trọng

Thay vì:

```text
resize event
     ↓
rebuild
```

hãy:

```text
resize event
     ↓
calculate breakpoint
     ↓
compare old/new
     ↓
changed?
   /    \
 no      yes
 ↓        ↓
ignore   rebuild
```

Đây là tư duy rất gần với UI framework hiện đại.

---

# 39. Responsive không chỉ là width

Còn:

```text
height
orientation
keyboard
navigation
touch
```

Ví dụ mobile landscape:

```text
┌──────────────────────────────────────┐
│                                      │
│         Reader content               │
│                                      │
└──────────────────────────────────────┘
```

Mobile portrait:

```text
┌────────────────┐
│                │
│ Reader content │
│                │
└────────────────┘
```

Đặc biệt với app đọc truyện, `height` và orientation cũng quan trọng.

---

# 40. Responsive Reader Content

Không nên:

```python
content_width = 800
```

mọi thiết bị.

Tốt hơn:

```text
Desktop
→ max width ~ 800

Mobile
→ gần full width
```

Concept:

```text
Desktop

┌──────────────────────────────────────┐
│       ┌──────────────────────┐       │
│       │      Story           │       │
│       │      Content         │       │
│       └──────────────────────┘       │
└──────────────────────────────────────┘
```

Mobile:

```text
┌──────────────────┐
│ Story Content    │
│                  │
└──────────────────┘
```

---

# 41. Responsive không đồng nghĩa với "full width"

Đây là lỗi phổ biến:

```python
expand=True
```

cho mọi thứ.

Kết quả:

```text
┌────────────────────────────────────────┐
│ This text becomes extremely wide       │
└────────────────────────────────────────┘
```

Với text reader:

```text
max content width
```

thường tốt hơn.

Ví dụ:

```text
Desktop
→ content width giới hạn

Mobile
→ content gần full width
```

---

# 42. Rule quan trọng cho Responsive UI

Hãy ưu tiên theo thứ tự:

```text
1. Flexible layout
2. Expand
3. ResponsiveRow / GridView
4. Breakpoint
5. Structural layout change
6. Fixed width cuối cùng
```

Đừng bắt đầu bằng:

```text
width=xxx
```

---

# 43. Checklist Responsive

Khi xây một màn hình, hãy hỏi:

### 1. Có width cố định không?

```text
Có → có thực sự cần?
```

### 2. Có height cố định không?

```text
Có → mobile có ổn không?
```

### 3. Có `expand` không?

```text
Không → tại sao?
```

### 4. Row có quá nhiều child không?

```text
Mobile có overflow không?
```

### 5. Có breakpoint không?

```text
Layout có thay đổi không?
```

### 6. Sidebar?

```text
Desktop → sidebar
Mobile → drawer/menu
```

### 7. Grid?

```text
Desktop → nhiều cột
Mobile → ít cột
```

---

# 44. Bài tập thực hành

## Bài 1 — Breakpoint Detector

Tạo app hiển thị:

```text
Width: 1366
Height: 768
Mode: Desktop
```

Resize:

```text
Desktop
Tablet
Mobile
```

---

# 45. Bài 2 — Responsive Stats

Tạo 4 Card:

```text
Queue
Running
Completed
Failed
```

Dùng `ResponsiveRow`.

Yêu cầu:

```text
Mobile
→ 1 card / row

Tablet
→ 2 cards / row

Desktop
→ 4 cards / row
```

---

# 46. Bài 3 — Responsive Sidebar

Desktop:

```text
Sidebar + Content
```

Mobile:

```text
Header + Content
```

Không được chỉ:

```text
sidebar.width = 50
```

Mà phải thay đổi layout structure.

---

# 47. Bài 4 — Responsive Book Library

Desktop:

```text
5 books / row
```

Tablet:

```text
3 books / row
```

Mobile:

```text
2 books / row
```

Nếu dùng `GridView`, hãy thiết kế sao cho số cột thay đổi theo kích thước.

---

# 48. Bài 5 — Responsive Reader

Desktop:

```text
content max width
```

Mobile:

```text
content gần full width
```

Yêu cầu:

```text
font
padding
content width
```

đều phải hợp lý trên cả hai.

---

# 49. Mini Project — Responsive Crawl Dashboard

Hãy xây:

### Desktop

```text
┌─────────────┬────────────────────────────┐
│ Sidebar     │ Header                     │
│             ├────────────────────────────┤
│ Dashboard   │ Stats                      │
│ Jobs        │                            │
│ Workers     │ Recent Jobs                │
│ Sources     │                            │
│ Settings    │ Workers                    │
└─────────────┴────────────────────────────┘
```

### Tablet

```text
┌──────────────────────────────────────────┐
│ Header                                   │
├──────────────────────────────────────────┤
│ Stats                                    │
├──────────────────────────────────────────┤
│ Recent Jobs                              │
├──────────────────────────────────────────┤
│ Workers                                  │
└──────────────────────────────────────────┘
```

### Mobile

```text
┌──────────────────────┐
│ ☰ Crawl Dashboard    │
├──────────────────────┤
│ Queue                │
│ Running              │
│ Completed            │
│                      │
│ Recent Jobs          │
│                      │
│ Workers              │
└──────────────────────┘
```

---

# 50. Mental Model cuối buổi

Toàn bộ Buổi 23 có thể thu gọn thành:

```text
                    Screen
                       │
                       ↓
                  page.width
                       │
                       ↓
                   Breakpoint
                  /     |      \
                 /      |       \
          Desktop     Tablet    Mobile
             │           │         │
             ↓           ↓         ↓
          Layout      Layout     Layout
             │           │         │
             └───────────┼─────────┘
                         ↓
                 Shared Components
                         │
                         ↓
                       Data
```

Và một nguyên tắc cực kỳ quan trọng:

> **Responsive UI nên được thiết kế ở tầng Layout, không nên rải logic `page.width` vào mọi component.**

---

# Roadmap

```text
Giai đoạn II — Layout Deep Dive

11. Row deep dive                    ✅
12. Column deep dive                 ✅
13. Container deep dive              ✅
14. Stack                            ✅
15. ResponsiveRow                    ✅
16. GridView                         ✅
17. ListView                         ✅
18. Tabs                             ✅
19. Card, ExpansionTile, ListTile    ✅
20. Layout constraints & sizing      ✅
21. Alignment                        ✅
22. Spacing / padding / margin       ✅
23. Responsive UI                    ✅
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

## Buổi 24 — Theme Deep Dive

Buổi tiếp theo chúng ta sẽ không chỉ học:

```python
page.theme = ...
```

mà sẽ xây **Theme System** cho app thực tế:

```text
Theme
├── ColorScheme
├── TextTheme
├── ButtonTheme
├── CardTheme
├── InputTheme
├── AppBarTheme
└── reusable design tokens
```

Sau đó áp dụng vào chính **Crawl Dashboard / Book Reader** để tránh việc mỗi control tự định nghĩa màu sắc, font và style riêng.
