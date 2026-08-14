# Buổi 24 — Theme Deep Dive trong Flet

Hôm nay chúng ta chuyển từ **Layout** sang một phần rất quan trọng của UI Architecture:

> **Theme — làm thế nào để toàn bộ ứng dụng có một hệ thống màu sắc, typography và component style nhất quán?**

Nếu không có Theme, app lớn thường nhanh chóng thành:

```text
Button → màu xanh này
Button khác → xanh khác
Card → radius 8
Card khác → radius 12
Text → size 16
Text khác → size 17
```

Khi có Theme:

```text
                App Theme
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      Color      Typography   Components
        │           │           │
        ↓           ↓           ↓
      Button       Text        Card
      Card         Title       Input
      Input        Body        Dialog
```

---

# 1. Theme là gì?

Theme là **quy tắc giao diện chung của ứng dụng**.

Nó có thể chứa:

```text
Color
Typography
Shape
Elevation
Button style
Input style
Card style
Navigation style
```

Ví dụ:

```text
App
│
├── Primary color
├── Secondary color
├── Background
├── Surface
├── Error
│
├── Title typography
├── Body typography
└── Button/Card/Input styles
```

---

# 2. Tại sao không style từng control?

Ví dụ cách không tốt:

```python
ft.Text(
    "Dashboard",
    size=28,
    weight=ft.FontWeight.BOLD,
)

ft.Text(
    "Recent Jobs",
    size=24,
    weight=ft.FontWeight.BOLD,
)

ft.Text(
    "Workers",
    size=25,
    weight=ft.FontWeight.BOLD,
)
```

Vấn đề:

```text
28
24
25
```

Không có quy luật.

Nếu sau này muốn đổi:

```text
Title 28 → 30
```

bạn phải sửa rất nhiều nơi.

---

# 3. Theme giải quyết vấn đề đó

Thay vì:

```python
ft.Text(
    "Dashboard",
    size=28,
    weight=ft.FontWeight.BOLD,
)
```

hãy tư duy:

```text
Dashboard
↓
Title style
↓
Theme
```

Một nơi định nghĩa:

```text
Title
→ size 28
→ bold
```

Toàn bộ app sử dụng cùng quy tắc.

---

# 4. Theme trong Flet

Ở cấp Page, bạn có thể thiết lập:

```python
page.theme = ft.Theme(
    color_scheme=...
)
```

và:

```python
page.dark_theme = ft.Theme(
    color_scheme=...
)
```

Sau đó:

```python
page.theme_mode = ft.ThemeMode.LIGHT
```

hoặc:

```python
page.theme_mode = ft.ThemeMode.DARK
```

---

# 5. Color Scheme

Một trong những phần quan trọng nhất của Theme là:

```text
Color Scheme
```

Thay vì nghĩ:

```text
Button = blue
```

hãy nghĩ:

```text
Primary
Secondary
Surface
Background
Error
OnPrimary
OnSurface
...
```

Đây là tư duy **semantic color**.

---

# 6. Semantic Color là gì?

Ví dụ không nên:

```python
ft.Text(
    "Error",
    color="#FF0000",
)
```

Mà nên tư duy:

```text
Error
↓
error color
```

Tại sao?

Vì Dark Theme có thể cần:

```text
Light:
Error → dark red

Dark:
Error → light red
```

Component không cần biết màu cụ thể.

---

# 7. Raw Color vs Semantic Color

Không tốt:

```python
color="#2196F3"
```

Tốt hơn:

```text
primary
```

Không tốt:

```python
color="#FF0000"
```

Tốt hơn:

```text
error
```

Không tốt:

```python
color="#FFFFFF"
```

Tốt hơn:

```text
on_primary
```

---

# 8. `ColorScheme`

Concept:

```python
theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.BLUE,
        secondary=ft.Colors.ORANGE,
    )
)
```

Sau đó:

```python
page.theme = theme
```

Bạn không cần rải:

```text
BLUE
ORANGE
...
```

khắp application.

---

# 9. `primary` nghĩa là gì?

`primary` thường đại diện cho:

```text
màu chủ đạo của application
```

Ví dụ Crawl Dashboard:

```text
Primary
→ màu chủ đạo cho action chính
```

Ví dụ:

```text
[ Start Crawl ]
```

---

# 10. `secondary`

`secondary` dùng cho:

```text
secondary actions
```

Ví dụ:

```text
[ Start ]
[ Filter ]
[ Refresh ]
```

Primary/secondary không nhất thiết tương ứng với "quan trọng tuyệt đối"; chúng là semantic roles.

---

# 11. `background`

Background là nền của khu vực ứng dụng.

Ví dụ:

```text
┌──────────────────────────────┐
│ background                   │
│                              │
│   Card                       │
│                              │
└──────────────────────────────┘
```

---

# 12. `surface`

`surface` thường đại diện cho những bề mặt nổi trên background:

```text
background
    │
    ├── Card → surface
    ├── Dialog → surface
    └── Panel → surface
```

Mental model:

```text
Background
└── Surface
    ├── Card
    ├── Panel
    └── Dialog
```

---

# 13. `on_*` colors

Đây là một khái niệm rất quan trọng.

Ví dụ:

```text
primary
```

là màu nền của button.

Còn:

```text
on_primary
```

là màu nội dung **trên primary**.

Ví dụ:

```text
┌──────────────────┐
│      START       │
└──────────────────┘
       ↑
   on_primary
```

---

# 14. Semantic color map

Bạn có thể hình dung:

```text
primary
   │
   └── on_primary

secondary
   │
   └── on_secondary

surface
   │
   └── on_surface

error
   │
   └── on_error
```

Đây là pattern cực kỳ quan trọng trong design system hiện đại.

---

# 15. Ví dụ Theme cơ bản

```python
import flet as ft


def main(page: ft.Page):

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
        )
    )

    page.add(
        ft.Button(
            "Start Crawl",
        )
    )


ft.run(main)
```

Điểm quan trọng:

```text
Button
 ↓
Theme
 ↓
ColorScheme
 ↓
primary
```

---

# 16. Không hard-code màu trong component

Tránh:

```python
def build_start_button():
    return ft.Button(
        "Start",
        bgcolor=ft.Colors.BLUE,
    )
```

Nếu sau này đổi theme:

```text
Blue → Green
```

component này vẫn giữ Blue.

Tốt hơn:

```python
def build_start_button():
    return ft.Button(
        "Start",
    )
```

để Theme quyết định style mặc định.

---

# 17. Theme là Dependency

Một cách tư duy architecture:

```text
Component
   ↓
Theme
   ↓
Design System
```

Component không nên chứa quá nhiều design decision.

Ví dụ:

```text
BookCard
```

nên tập trung:

```text
Book data
Layout
Interaction
```

thay vì:

```text
Book data
Layout
Interaction
#2196F3
#FFFFFF
radius=12
shadow=...
```

---

# 18. Typography

Theme không chỉ có màu.

Một hệ thống UI tốt còn cần:

```text
Typography
```

Ví dụ:

```text
Display
Headline
Title
Body
Label
Caption
```

Bạn có thể định nghĩa mental model:

```text
display_large
display_medium

headline_large
headline_medium

title_large
title_medium

body_large
body_medium

label_large
label_medium
```

---

# 19. Tại sao Typography quan trọng?

Nếu app có:

```text
Dashboard
Recent Jobs
Worker
Status
Queue
```

mà mỗi nơi dùng size khác nhau:

```text
Dashboard → 29
Recent Jobs → 23
Worker → 19
Status → 16
Queue → 15
```

UI sẽ không có hierarchy rõ ràng.

Theme giúp:

```text
Page Title
→ headline

Section Title
→ title

Description
→ body

Button text
→ label
```

---

# 20. Tạo Typography Tokens

Bạn có thể tự định nghĩa:

```python
TYPOGRAPHY = {
    "page_title": 28,
    "section_title": 20,
    "body": 14,
    "caption": 12,
}
```

Sau đó:

```python
ft.Text(
    "Crawl Dashboard",
    size=TYPOGRAPHY["page_title"],
)
```

Đây là cách đơn giản để xây design system.

---

# 21. Tách Theme khỏi UI

Không nên:

```text
main.py
 ├── theme
 ├── UI
 ├── database
 ├── business logic
 └── event
```

Khi app lớn hơn, nên:

```text
app/
├── theme/
│   ├── colors.py
│   ├── typography.py
│   ├── theme.py
│   └── tokens.py
│
├── components/
│   ├── buttons.py
│   ├── cards.py
│   └── inputs.py
│
└── screens/
```

---

# 22. Design Tokens

Đây là khái niệm quan trọng hơn cả Theme.

Design Token là giá trị thiết kế có tên.

Ví dụ:

```python
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
```

Color:

```python
PRIMARY = ...
SURFACE = ...
ERROR = ...
```

Radius:

```python
RADIUS_SM = 4
RADIUS_MD = 8
RADIUS_LG = 12
```

Typography:

```python
FONT_SIZE_SM = 12
FONT_SIZE_MD = 14
FONT_SIZE_LG = 20
```

---

# 23. Theme Architecture

Một architecture tốt:

```text
Design Tokens
      │
      ├── Colors
      ├── Typography
      ├── Spacing
      ├── Radius
      └── Elevation
             │
             ↓
          Theme
             │
             ↓
        Components
             │
             ↓
           Screens
```

Đây là bước đầu tiên để xây một **Design System**.

---

# 24. Ví dụ `tokens.py`

```python
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

RADIUS_SM = 4
RADIUS_MD = 8
RADIUS_LG = 12

FONT_SM = 12
FONT_MD = 14
FONT_LG = 20
FONT_XL = 28
```

---

# 25. `colors.py`

```python
PRIMARY = ft.Colors.BLUE
SECONDARY = ft.Colors.ORANGE

BACKGROUND = ft.Colors.GREY_100
SURFACE = ft.Colors.WHITE

ERROR = ft.Colors.RED
```

Nhưng có một vấn đề:

```text
Light Theme
→ WHITE surface

Dark Theme
→ WHITE surface?
```

Không nên.

Đây là lý do cần **semantic Theme** thay vì chỉ global constants.

---

# 26. Light Theme

Concept:

```text
background
→ light

surface
→ slightly elevated light

text
→ dark

primary
→ primary brand color
```

Ví dụ:

```python
light_theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.BLUE,
        background=ft.Colors.WHITE,
        surface=ft.Colors.GREY_100,
    )
)
```

---

# 27. Dark Theme

Dark Theme không đơn giản là:

```text
background = BLACK
```

Ví dụ:

```python
dark_theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.BLUE_200,
        background=ft.Colors.BLACK,
        surface=ft.Colors.GREY_900,
    )
)
```

Thực tế cần thiết kế độ tương phản cẩn thận.

---

# 28. `theme_mode`

Có thể chọn:

```python
page.theme_mode = ft.ThemeMode.LIGHT
```

hoặc:

```python
page.theme_mode = ft.ThemeMode.DARK
```

hoặc để hệ điều hành quyết định:

```python
page.theme_mode = ft.ThemeMode.SYSTEM
```

Tư duy:

```text
LIGHT
→ luôn sáng

DARK
→ luôn tối

SYSTEM
→ theo OS
```

---

# 29. Theme Switcher

Đây sẽ là tiền đề cho Buổi 25.

Ví dụ:

```python
def toggle_theme(e):
    if page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.DARK

    page.update()
```

Button:

```python
ft.IconButton(
    icon=ft.Icons.DARK_MODE,
    on_click=toggle_theme,
)
```

---

# 30. Điều quan trọng: Theme thay đổi không nên sửa từng Control

Đây là sức mạnh của Theme.

```text
Button
Card
Text
Input
Dialog
```

không cần:

```text
if dark:
    bgcolor = ...
else:
    bgcolor = ...
```

khắp nơi.

Thay vào đó:

```text
page.theme_mode
       ↓
Theme
       ↓
Controls
```

---

# 31. Component Theme

Một UI thực tế có rất nhiều component:

```text
Button
 ├── Filled
 ├── Outlined
 ├── Text
 └── Icon

Input
 ├── TextField
 ├── Dropdown
 └── Search

Navigation
 ├── NavigationRail
 ├── NavigationBar
 └── Drawer
```

Bạn không muốn mỗi component tự chọn style.

---

# 32. Ví dụ Button System

Thay vì:

```python
ft.Button(
    "Start",
    bgcolor=...,
    color=...,
)
```

khắp nơi, tạo:

```python
def primary_button(text, on_click=None):
    return ft.Button(
        text,
        on_click=on_click,
    )
```

Theme quyết định appearance.

Sau này:

```text
Primary Button
→ tất cả thay đổi cùng lúc
```

---

# 33. Card System

Tạo:

```python
def app_card(content):
    return ft.Card(
        content=ft.Container(
            padding=16,
            content=content,
        )
    )
```

Sau đó:

```python
app_card(
    ft.Column(
        controls=[
            ft.Text("Queue"),
            ft.Text("120"),
        ]
    )
)
```

Tất cả Card có cùng:

```text
padding
shape
elevation
surface
```

---

# 34. Input System

Ví dụ:

```python
def app_text_field(
    label: str,
    hint: str | None = None,
):
    return ft.TextField(
        label=label,
        hint_text=hint,
    )
```

Không để mỗi màn hình tự quyết định:

```text
border radius
border color
padding
text size
```

---

# 35. Theme + Component Factory

Architecture:

```text
Theme
  ↓
Component Factory
  ↓
Screen
```

Ví dụ:

```text
Theme
 ↓
app_button()
 ↓
Login Screen
```

Thay vì:

```text
Login Screen
 ↓
hard-coded Button style
```

---

# 36. Một cấu trúc project tốt

Với app Flet lớn:

```text
app/
│
├── main.py
│
├── core/
│   └── config.py
│
├── theme/
│   ├── __init__.py
│   ├── theme.py
│   ├── tokens.py
│   └── typography.py
│
├── components/
│   ├── app_button.py
│   ├── app_card.py
│   ├── app_input.py
│   └── app_dialog.py
│
├── layouts/
│   ├── desktop.py
│   ├── tablet.py
│   └── mobile.py
│
└── screens/
    ├── dashboard.py
    ├── books.py
    └── workers.py
```

Đây chính là hướng mà app Crawl Dashboard của bạn sẽ cần khi lớn lên.

---

# 37. Theme Factory

Thay vì tạo Theme trực tiếp trong `main.py`:

```python
def create_light_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
        )
    )


def create_dark_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
            secondary=ft.Colors.ORANGE_200,
        )
    )
```

Sau đó:

```python
page.theme = create_light_theme()
page.dark_theme = create_dark_theme()
```

---

# 38. Tại sao dùng Factory?

Vì sau này bạn có thể có:

```text
Default Theme
Nord Theme
Dracula Theme
Custom Theme
```

Architecture:

```text
ThemeFactory
│
├── create_light()
├── create_dark()
├── create_nord()
└── create_custom()
```

---

# 39. Theme không chỉ dành cho Dark Mode

Đây là điểm rất quan trọng.

Theme có thể thay đổi:

```text
Brand
Colors
Typography
Shape
Spacing
Components
```

Ví dụ:

```text
Crawl App
→ Blue

Book Reader
→ Purple

TTS App
→ Green
```

Nhưng code UI vẫn giữ nguyên.

---

# 40. Theme và Domain

Đừng trộn:

```text
Domain logic
```

với:

```text
Theme
```

Ví dụ:

```python
if crawler.status == "failed":
    color = ft.Colors.RED
```

Đây là chỗ cần cẩn thận.

Domain nói:

```text
status = FAILED
```

Presentation layer quyết định:

```text
FAILED
→ error semantic color
```

Tách:

```text
Domain
 ↓
FAILED
 ↓
UI
 ↓
error
 ↓
Theme
 ↓
actual color
```

Đây là tư duy Clean Architecture rất phù hợp với những project bạn đang học.

---

# 41. Status Color System

Ví dụ Crawl Worker:

```text
RUNNING
→ primary

SUCCESS
→ success

FAILED
→ error

PAUSED
→ warning

IDLE
→ neutral
```

Không nên:

```python
if status == "FAILED":
    color = "#ff0000"
```

Mà:

```python
STATUS_COLOR_ROLE = {
    "running": "primary",
    "success": "success",
    "failed": "error",
    "paused": "warning",
}
```

Sau đó Theme ánh xạ role → màu.

---

# 42. Đây là Semantic UI

Bạn đang xây:

```text
Domain Status
       ↓
Semantic Role
       ↓
Theme
       ↓
Actual Color
```

Ví dụ:

```text
FAILED
 ↓
error
 ↓
theme.error
 ↓
light/dark appropriate color
```

Đây là kiến trúc tốt hơn rất nhiều so với hard-code màu.

---

# 43. Theme Context

Một component nên lấy theme từ context/page khi cần.

Ví dụ về mặt tư duy:

```text
page
 ↓
theme
 ↓
component
```

Component không cần biết:

```text
"Blue là màu gì?"
```

Nó chỉ cần biết:

```text
"Primary là gì?"
```

---

# 44. Theme + Responsive

Hai thứ này kết hợp với nhau:

```text
Screen
 │
 ├── Breakpoint
 │      ↓
 │   Layout
 │
 └── Theme
        ↓
     Styling
```

Rất quan trọng:

```text
Responsive
→ quyết định BỐ CỤC

Theme
→ quyết định HÌNH THỨC
```

---

# 45. Đây là cách phân biệt

Ví dụ:

```text
Desktop:
Sidebar trái

Mobile:
Drawer
```

Đây là:

```text
Responsive
```

Còn:

```text
Button:
Blue trong Light
Light-blue trong Dark
```

là:

```text
Theme
```

---

# 46. Theme không nên quyết định Layout

Không nên:

```text
Dark Theme
→ sidebar width = 200
```

Theme không chịu trách nhiệm layout.

Tách:

```text
Responsive
→ width/layout

Theme
→ color/style
```

---

# 47. Theme không nên chứa Business Logic

Không:

```python
if user.is_admin:
    primary_color = ...
```

Business role không phải Theme.

Nên:

```text
user.is_admin
 ↓
UI permission
```

Theme chỉ style.

---

# 48. Mini Design System

Hãy tạo:

```python
class AppTokens:
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 16
    spacing_lg = 24
    spacing_xl = 32

    radius_sm = 4
    radius_md = 8
    radius_lg = 12

    title_size = 28
    section_size = 20
    body_size = 14
    caption_size = 12
```

Sau đó:

```python
tokens = AppTokens()
```

---

# 49. Theme Layer

```python
def create_theme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
        )
    )
```

`main.py`:

```python
def main(page: ft.Page):
    page.theme = create_theme()

    page.add(
        build_dashboard()
    )
```

---

# 50. Component Layer

```python
def build_stat_card(title, value):
    return ft.Card(
        content=ft.Container(
            padding=16,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(title),
                    ft.Text(
                        value,
                        size=28,
                    ),
                ],
            ),
        ),
    )
```

Điểm đáng chú ý:

Component không hard-code:

```text
background color
primary color
```

nếu Flet Theme đã đủ đáp ứng.

---

# 51. Screen Layer

```python
def build_dashboard():
    return ft.Column(
        spacing=24,
        controls=[
            ft.Text(
                "Crawl Dashboard",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                controls=[
                    build_stat_card("Queue", "120"),
                    build_stat_card("Running", "5"),
                    build_stat_card("Completed", "1250"),
                ]
            ),
        ],
    )
```

Sau này typography cũng có thể được đưa thành abstraction riêng.

---

# 52. Đừng over-engineer Theme quá sớm

Có hai thái cực.

### Quá đơn giản

```python
color="#123456"
```

khắp nơi.

### Quá phức tạp

```text
ThemeManager
ThemeRegistry
ThemeProvider
ThemeResolver
ThemeFactory
ThemeContext
ThemeAdapter
```

cho một app 3 màn hình.

Nguyên tắc:

> **Design system phải phát triển theo quy mô ứng dụng.**

---

# 53. Với app hiện tại của bạn

Tôi đề xuất:

```text
Giai đoạn đầu:

theme/
├── theme.py
└── tokens.py
```

Khi app lớn:

```text
theme/
├── theme.py
├── tokens.py
├── colors.py
├── typography.py
├── components.py
└── presets/
```

Không cần xây quá nhiều abstraction ngay từ đầu.

---

# 54. Bài tập 1 — Theme cơ bản

Tạo app:

```text
Crawl Dashboard
```

Có:

```text
[Start Crawl]
[Pause]
[Stop]
```

Thiết lập:

```text
primary
secondary
background
surface
error
```

Không hard-code màu trực tiếp vào Button.

---

# 55. Bài tập 2 — Light / Dark

Tạo:

```text
☀ / 🌙
```

Click:

```text
Light
 ↕
Dark
```

Yêu cầu:

```text
Button
Card
Background
Text
```

đều thay đổi phù hợp.

---

# 56. Bài tập 3 — Design Tokens

Tạo:

```python
SPACING_SM
SPACING_MD
SPACING_LG

RADIUS_SM
RADIUS_MD
RADIUS_LG

FONT_SM
FONT_MD
FONT_LG
FONT_XL
```

Sau đó refactor Dashboard để **không còn magic numbers**.

---

# 57. Bài tập 4 — Status Theme

Tạo Worker:

```text
Worker #1
Status: Running
```

Các trạng thái:

```text
Running
Completed
Failed
Paused
Idle
```

Mỗi trạng thái dùng semantic role.

Không viết:

```python
color="#..."
```

ở từng Worker.

---

# 58. Bài tập 5 — Theme + Responsive

Kết hợp:

```text
Buổi 23
Responsive UI

+

Buổi 24
Theme
```

Xây:

```text
Desktop Light
Desktop Dark

Mobile Light
Mobile Dark
```

Bạn sẽ có:

```text
          Theme
        /       \
     Light      Dark
       |          |
       └────┬─────┘
            │
        Responsive
        /    |     \
 Desktop   Tablet  Mobile
```

---

# 59. Mini Project — Crawl Dashboard Theme System

Hãy xây architecture:

```text
app/
│
├── main.py
│
├── theme/
│   ├── theme.py
│   └── tokens.py
│
├── components/
│   ├── stat_card.py
│   ├── worker_card.py
│   └── job_card.py
│
├── layouts/
│   ├── desktop.py
│   ├── tablet.py
│   └── mobile.py
│
└── screens/
    └── dashboard.py
```

Flow:

```text
main.py
   │
   ├── Theme
   │
   └── Responsive Layout
           │
           └── Dashboard
                  │
                  ├── StatCard
                  ├── JobCard
                  └── WorkerCard
```

Đây chính là nền tảng rất tốt cho Flet app thực tế.

---

# 60. Mental Model cuối buổi

Hãy nhớ 4 tầng:

```text
                 DESIGN SYSTEM
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        Tokens       Theme      Components
          │            │            │
          └────────────┼────────────┘
                       ↓
                     Screen
                       ↓
                    Layout
```

Trong đó:

### Tokens

```text
spacing
radius
font size
```

### Theme

```text
colors
component styles
light/dark
```

### Responsive

```text
desktop
tablet
mobile
```

### Component

```text
Button
Card
Input
WorkerCard
BookCard
```

---

# 61. Quy tắc vàng

Bạn có thể ghi nhớ:

> **Responsive quyết định "đặt ở đâu".**

> **Theme quyết định "trông như thế nào".**

> **Component quyết định "hành vi gì".**

> **Domain quyết định "ý nghĩa gì".**

Ví dụ:

```text
Worker FAILED
      │
      ↓
Domain
"FAILED"
      │
      ↓
Presentation
"error"
      │
      ↓
Theme
màu error
      │
      ↓
Component
WorkerCard
      │
      ↓
Responsive Layout
đặt Card ở đâu
```

Đây là tư duy kiến trúc rất quan trọng khi bạn tiến tới Flet application lớn.

---

# Roadmap hiện tại

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
24. Theme                            ✅
25. Dark / Light mode
26. Mini Project: Dashboard
```

**Buổi 25** sẽ đi sâu riêng vào **Dark / Light Mode**: `ThemeMode`, `dark_theme`, `SYSTEM`, persistence lựa chọn theme, nút chuyển theme, icon động, và cách thiết kế Light/Dark ColorScheme để không phải `if dark:` ở khắp code.
