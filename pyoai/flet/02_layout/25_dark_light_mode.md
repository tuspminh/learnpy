# Buổi 25 — Dark / Light Mode Deep Dive trong Flet

Hôm nay chúng ta đi sâu vào **Dark Mode / Light Mode**. Đây không chỉ là chuyện đổi:

```python
page.theme_mode = ft.ThemeMode.DARK
```

Mà mục tiêu là xây được một **Theme System hoàn chỉnh**:

```text
                Theme System
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Light       Dark      System
          │          │          │
          └──────────┼──────────┘
                     ↓
                 Components
                     ↓
                   Screens
```

Đặc biệt, chúng ta sẽ tránh kiểu code:

```python
if dark:
    color = ...
else:
    color = ...
```

rải khắp ứng dụng.

---

# 1. Dark Mode thực chất là gì?

Dark Mode **không phải**:

```text
Light Mode
↓
background = black
```

Mà là một **bộ semantic colors khác**.

Ví dụ:

### Light

```text
Background → trắng
Surface    → xám rất nhạt
Text       → đen
Primary    → xanh đậm
Error      → đỏ đậm
```

### Dark

```text
Background → đen/xám rất tối
Surface    → xám tối
Text       → trắng
Primary    → xanh sáng hơn
Error      → đỏ sáng hơn
```

---

# 2. Ba chế độ chính

Flet hỗ trợ tư duy ba trạng thái:

```text
LIGHT
DARK
SYSTEM
```

### LIGHT

```python
page.theme_mode = ft.ThemeMode.LIGHT
```

Luôn dùng Light.

### DARK

```python
page.theme_mode = ft.ThemeMode.DARK
```

Luôn dùng Dark.

### SYSTEM

```python
page.theme_mode = ft.ThemeMode.SYSTEM
```

Theo setting của hệ điều hành.

---

# 3. `page.theme` và `page.dark_theme`

Đây là cặp cực kỳ quan trọng.

```python
page.theme = light_theme
page.dark_theme = dark_theme
```

Có nghĩa:

```text
theme
  ↓
Light Theme

dark_theme
  ↓
Dark Theme
```

Sau đó:

```python
page.theme_mode = ft.ThemeMode.LIGHT
```

→ dùng `page.theme`.

```python
page.theme_mode = ft.ThemeMode.DARK
```

→ dùng `page.dark_theme`.

---

# 4. Kiến trúc

Hãy hình dung:

```text
Page
│
├── theme
│    └── Light Theme
│
├── dark_theme
│    └── Dark Theme
│
└── theme_mode
      │
      ├── LIGHT
      ├── DARK
      └── SYSTEM
```

`theme_mode` chính là **selector**.

---

# 5. Ví dụ tối thiểu

```python
import flet as ft


def main(page: ft.Page):

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
        )
    )

    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
        )
    )

    page.theme_mode = ft.ThemeMode.SYSTEM

    page.add(
        ft.Text("Hello Flet")
    )


ft.run(main)
```

---

# 6. `SYSTEM` rất quan trọng

Nếu bạn xây app desktop:

```text
Windows → Dark
```

thì app nên có khả năng:

```text
System Theme
    ↓
Windows Dark
    ↓
Flet Dark
```

Nếu OS chuyển:

```text
Dark → Light
```

app có thể thích ứng theo system mode.

Đây thường là lựa chọn mặc định tốt cho app mới.

---

# 7. Theme Switcher

Bây giờ tạo nút:

```text
🌙
```

Click:

```text
Light ↔ Dark
```

Code cơ bản:

```python
def toggle_theme(e):
    if page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.DARK

    page.update()
```

---

# 8. Nhưng cách trên có một vấn đề

Nếu người dùng chọn:

```text
SYSTEM
```

thì:

```python
page.theme_mode
```

không cho chúng ta một state:

```text
"actual current appearance"
```

mà nó biểu diễn:

```text
"theme selection mode"
```

Đây là hai khái niệm khác nhau.

---

# 9. Phân biệt Preference và Appearance

Đây là kiến thức rất quan trọng.

### Theme preference

Người dùng chọn:

```text
Light
Dark
System
```

### Actual appearance

Ứng dụng hiện tại đang:

```text
Light
```

hoặc:

```text
Dark
```

Có thể:

```text
preference = SYSTEM
actual = DARK
```

nếu OS đang Dark.

Đừng trộn hai thứ này.

---

# 10. Model đúng

Ta có:

```text
ThemePreference
│
├── LIGHT
├── DARK
└── SYSTEM
```

và:

```text
ActualTheme
│
├── LIGHT
└── DARK
```

Flow:

```text
Preference
     ↓
SYSTEM?
   /    \
 Yes     No
  ↓       ↓
OS       selected
  ↓       ↓
Actual Theme
```

---

# 11. Tại sao điều này quan trọng?

Ví dụ UI có icon:

```text
☀️
```

Nếu:

```text
preference = SYSTEM
actual = DARK
```

thì icon nên phản ánh **appearance thực tế**, không nhất thiết preference.

Ngược lại, Settings có thể hiển thị:

```text
Theme:
○ Light
○ Dark
● System
```

Đó là preference.

---

# 12. Đừng viết `if dark` khắp app

Sai:

```python
def build_card(page):
    if page.theme_mode == ft.ThemeMode.DARK:
        bgcolor = ft.Colors.GREY_900
    else:
        bgcolor = ft.Colors.WHITE

    return ft.Container(
        bgcolor=bgcolor,
    )
```

Vì:

```text
component
  ↓
biết theme mode
```

Component bị coupling với theme.

---

# 13. Tốt hơn: semantic color

Card chỉ cần:

```python
ft.Card(
    ...
)
```

và Theme chịu trách nhiệm:

```text
Light:
Card → surface light

Dark:
Card → surface dark
```

---

# 14. Color Scheme cho Light

Ví dụ:

```python
light_scheme = ft.ColorScheme(
    primary=ft.Colors.BLUE,
    secondary=ft.Colors.ORANGE,
    background=ft.Colors.WHITE,
    surface=ft.Colors.GREY_100,
    error=ft.Colors.RED,
)
```

---

# 15. Color Scheme cho Dark

```python
dark_scheme = ft.ColorScheme(
    primary=ft.Colors.BLUE_200,
    secondary=ft.Colors.ORANGE_200,
    background=ft.Colors.GREY_900,
    surface=ft.Colors.GREY_800,
    error=ft.Colors.RED_200,
)
```

Điểm quan trọng:

```text
Light scheme ≠ Dark scheme
```

Chúng là hai bộ semantic mapping.

---

# 16. `on_*` colors

Đây là phần nhiều người bỏ qua.

Ví dụ:

```text
primary
on_primary
```

Nếu:

```text
primary = dark blue
```

thì:

```text
on_primary = white
```

Nếu Dark Theme:

```text
primary = light blue
```

thì:

```text
on_primary = dark
```

Mục tiêu là:

```text
foreground
+
background
=
đủ contrast
```

---

# 17. Ví dụ Button

Concept:

```text
Light

┌──────────────────┐
│   Start Crawl    │
└──────────────────┘
   blue + white
```

Dark:

```text
┌──────────────────┐
│   Start Crawl    │
└──────────────────┘
   light blue + dark
```

Button không cần biết hai trường hợp.

Theme xử lý.

---

# 18. Surface hierarchy

Dark Mode chuyên nghiệp không nên dùng:

```text
black
black
black
```

mọi nơi.

Thay vào đó:

```text
Background
    ↓
Surface
    ↓
Elevated Surface
```

Ví dụ:

```text
┌──────────────────────────────┐
│ Background                   │
│                              │
│   ┌──────────────────────┐   │
│   │ Surface              │   │
│   │                      │   │
│   │   ┌──────────────┐   │   │
│   │   │ Elevated     │   │   │
│   │   └──────────────┘   │   │
│   └──────────────────────┘   │
└──────────────────────────────┘
```

---

# 19. Crawl Dashboard

Với app crawl:

```text
Background
│
├── Sidebar
│
├── Dashboard
│
├── Stat Cards
│
├── Job Cards
│
└── Worker Cards
```

Không nên tất cả đều cùng một màu.

Nên có hierarchy:

```text
Background
    ↓
Surface
    ↓
Cards
```

---

# 20. Reader App

Với app đọc truyện:

Light:

```text
Background → #fff
Text       → dark
```

Dark:

```text
Background → dark gray
Text       → light gray
```

Nhưng đặc biệt:

> Đừng nhất thiết dùng `pure black` cho nền đọc truyện.

Ví dụ:

```text
#000000
```

có thể quá tương phản.

Một dark gray mềm hơn thường dễ đọc hơn.

---

# 21. Text hierarchy

Dark Mode cũng cần:

```text
Primary text
Secondary text
Disabled text
Hint text
```

Ví dụ:

```text
Title
████████████

Description
██████████

Metadata
██████
```

Không nên tất cả đều:

```text
white
```

---

# 22. Semantic text

Tư duy:

```text
primary text
secondary text
disabled text
```

thay vì:

```text
white
gray
gray2
gray3
```

Ví dụ:

```text
Light
Primary → dark
Secondary → gray

Dark
Primary → light
Secondary → gray-light
```

---

# 23. Theme Switcher UI

Một UI đẹp có thể là:

```text
┌────────────────────────────┐
│ Theme                      │
│                            │
│ ○ Light                    │
│ ● Dark                     │
│ ○ System                   │
└────────────────────────────┘
```

Thay vì chỉ có:

```text
☀️ button
```

Settings screen thường phù hợp hơn với 3 lựa chọn.

---

# 24. Enum cho Theme Preference

Trong application architecture, tạo:

```python
from enum import Enum


class ThemePreference(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
```

Sau đó:

```python
theme_preference = ThemePreference.SYSTEM
```

Đây là state của application.

---

# 25. Mapping sang Flet

```python
def apply_theme(page, preference):
    if preference == ThemePreference.LIGHT:
        page.theme_mode = ft.ThemeMode.LIGHT

    elif preference == ThemePreference.DARK:
        page.theme_mode = ft.ThemeMode.DARK

    else:
        page.theme_mode = ft.ThemeMode.SYSTEM
```

---

# 26. Theme Manager

Khi app lớn hơn, có thể tạo:

```python
class ThemeManager:

    def __init__(self, page):
        self.page = page

    def set_light(self):
        self.page.theme_mode = ft.ThemeMode.LIGHT

    def set_dark(self):
        self.page.theme_mode = ft.ThemeMode.DARK

    def set_system(self):
        self.page.theme_mode = ft.ThemeMode.SYSTEM
```

Nhưng:

> Chưa cần làm class này nếu app còn rất nhỏ.

---

# 27. Khi nào cần ThemeManager?

### App nhỏ

```text
main.py
theme.py
```

là đủ.

### App trung bình

```text
ThemeManager
ThemePreference
```

có thể hữu ích.

### App lớn

```text
ThemeService
PreferenceRepository
ThemeState
ThemeController
```

có thể xuất hiện.

Đừng over-engineer.

---

# 28. Persistence — lưu lựa chọn Theme

Đây là phần quan trọng.

Nếu người dùng chọn:

```text
Dark
```

sau khi đóng app:

```text
app mở lại
```

thì họ thường muốn:

```text
Dark
```

vẫn được giữ.

Flow:

```text
User
 ↓
select Dark
 ↓
Application State
 ↓
Persistence
 ↓
restart
 ↓
load Dark
 ↓
apply theme
```

---

# 29. Lưu Theme ở đâu?

Với desktop Flet app, có thể dùng:

```text
local storage
```

hoặc một persistence mechanism phù hợp với ứng dụng.

Về architecture:

```text
ThemeController
      ↓
ThemePreferenceRepository
      ↓
Storage
```

Đừng để UI trực tiếp xử lý file/database.

---

# 30. Ví dụ đơn giản với file JSON

Để học architecture, ta có thể dùng:

```json
{
    "theme": "dark"
}
```

Nhưng đây chỉ là ví dụ.

Không nhất thiết app thật phải dùng JSON.

---

# 31. Theme Repository

```python
class ThemeRepository:

    def load(self):
        ...

    def save(self, preference):
        ...
```

UI không cần biết:

```text
JSON?
SQLite?
SharedPreferences?
File?
```

---

# 32. Architecture

```text
Settings UI
     │
     ↓
Theme Controller
     │
     ├── apply theme
     │
     └── save preference
             │
             ↓
       Theme Repository
             │
             ↓
          Storage
```

Đây là cách rất phù hợp với những gì bạn đang học về:

* Repository Pattern
* Clean Architecture
* Domain-Driven Design

---

# 33. Startup Flow

Khi app khởi động:

```text
main()
  ↓
load settings
  ↓
load theme preference
  ↓
create page
  ↓
configure light_theme
  ↓
configure dark_theme
  ↓
apply preference
  ↓
build UI
```

Đừng:

```text
build UI
 ↓
5 giây sau
 ↓
load theme
```

Nếu làm vậy UI có thể nhấp nháy.

---

# 34. Tốt hơn

```python
def main(page):

    preference = repository.load()

    configure_theme(page)

    apply_theme(page, preference)

    build_ui(page)
```

Theme được quyết định trước khi UI hoàn chỉnh được render.

---

# 35. Theme State

Một state đơn giản:

```python
class ThemeState:

    def __init__(self):
        self.preference = ThemePreference.SYSTEM
```

Khi user chọn:

```python
state.preference = ThemePreference.DARK
```

sau đó:

```text
state
 ↓
apply
 ↓
persist
 ↓
UI update
```

---

# 36. Đừng dùng `page.theme_mode` làm toàn bộ application state

Đây là một lỗi kiến trúc tinh vi.

`page.theme_mode` là:

```text
Flet UI state
```

Còn:

```python
ThemePreference.DARK
```

là:

```text
Application state
```

Tách chúng:

```text
Application
ThemePreference.DARK
       ↓
Flet
page.theme_mode = DARK
```

---

# 37. Tại sao?

Sau này bạn có thể:

```text
CLI
Config file
Settings page
Remote config
```

đều thay đổi:

```text
ThemePreference
```

nhưng UI framework không nên là source of truth duy nhất.

---

# 38. Theme Controller

Ví dụ:

```python
class ThemeController:

    def __init__(self, page, repository):
        self.page = page
        self.repository = repository

    def set_preference(self, preference):
        self.repository.save(preference)
        self.apply(preference)

    def apply(self, preference):
        if preference == ThemePreference.LIGHT:
            self.page.theme_mode = ft.ThemeMode.LIGHT

        elif preference == ThemePreference.DARK:
            self.page.theme_mode = ft.ThemeMode.DARK

        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        self.page.update()
```

---

# 39. Nhưng hãy nhớ

Đây là code architecture để học.

Không nhất thiết ngay lập tức phải tạo:

```text
Controller
Repository
State
Service
```

cho một app demo 100 dòng.

Mục tiêu của chúng ta là hiểu **khi nào abstraction có giá trị**.

---

# 40. `SYSTEM` và toggle button

Nếu app có toggle:

```text
Light ↔ Dark
```

thì bạn đã bỏ qua `SYSTEM`.

Nếu Settings có:

```text
Light
Dark
System
```

thì đầy đủ hơn.

Tôi khuyên:

### Quick toggle

```text
☀️ / 🌙
```

cho header.

### Full setting

```text
Light
Dark
System
```

cho Settings.

---

# 41. Icon động

Ví dụ:

```text
Light
→ 🌙
```

nghĩa:

> Click để chuyển Dark.

Dark:

```text
→ ☀️
```

nghĩa:

> Click để chuyển Light.

Code concept:

```python
def get_theme_icon():
    if state.preference == ThemePreference.DARK:
        return ft.Icons.LIGHT_MODE

    return ft.Icons.DARK_MODE
```

Nhưng nếu `SYSTEM`:

```text
actual appearance
```

có thể cần logic riêng.

---

# 42. Đừng nhầm `SYSTEM` với Dark

Ví dụ:

```text
preference = SYSTEM
OS = DARK
```

Không nên tự đổi:

```text
preference = DARK
```

Vì user vẫn đang chọn:

```text
SYSTEM
```

Chỉ actual appearance là:

```text
DARK
```

---

# 43. State Machine

Có thể hình dung:

```text
             ┌─────────┐
             │  LIGHT  │
             └────┬────┘
                  │
             select DARK
                  ↓
             ┌─────────┐
             │  DARK   │
             └────┬────┘
                  │
             select SYSTEM
                  ↓
             ┌─────────┐
             │ SYSTEM  │
             └─────────┘
```

Thực tế có 3 preference states:

```text
LIGHT
DARK
SYSTEM
```

---

# 44. Light/Dark Theme Factory

Tạo riêng:

```python
def create_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.ORANGE,
            background=ft.Colors.WHITE,
            surface=ft.Colors.GREY_100,
            error=ft.Colors.RED,
        )
    )
```

và:

```python
def create_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
            secondary=ft.Colors.ORANGE_200,
            background=ft.Colors.GREY_900,
            surface=ft.Colors.GREY_800,
            error=ft.Colors.RED_200,
        )
    )
```

---

# 45. `main.py`

```python
def main(page: ft.Page):

    page.theme = create_light_theme()
    page.dark_theme = create_dark_theme()

    page.theme_mode = ft.ThemeMode.SYSTEM

    page.add(
        build_app()
    )


ft.run(main)
```

Đây là pattern rất sạch.

---

# 46. Theme module

```text
theme/
├── __init__.py
├── light.py
├── dark.py
└── factory.py
```

Ví dụ:

```text
factory.py
    │
    ├── create_light_theme()
    │
    └── create_dark_theme()
```

---

# 47. Component không biết Light/Dark

Ví dụ:

```python
def build_worker_card(worker):
    return ft.Card(
        content=ft.Container(
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Text(worker.name),
                    ft.Text(worker.status),
                ],
            ),
        ),
    )
```

Không có:

```python
if dark:
```

Đây là mục tiêu.

---

# 48. Khi nào component cần biết theme?

Có một số trường hợp thực sự cần.

Ví dụ:

```text
Chart
Image
Custom painting
Canvas
```

mà màu được vẽ thủ công.

Khi đó:

```text
Theme
 ↓
component
 ↓
derive visual colors
```

có thể hợp lý.

Nhưng đây là ngoại lệ.

---

# 49. Theme-aware custom component

Nếu cần:

```python
def build_status_badge(status):
    ...
```

hãy truyền **semantic role**:

```text
success
warning
error
```

thay vì:

```text
green
yellow
red
```

Ví dụ:

```python
ROLE_BY_STATUS = {
    "running": "primary",
    "success": "success",
    "failed": "error",
    "paused": "warning",
}
```

---

# 50. Dark Mode cho Crawl Dashboard

Hãy thiết kế:

### Light

```text
Background
████████████████████

Cards
░░░░░░░░░░░░░░░░░░░

Primary
████████████
```

### Dark

```text
Background
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

Cards
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

Primary
████████████
```

Nhưng:

```text
status
```

vẫn semantic:

```text
RUNNING → primary
SUCCESS → success
FAILED → error
```

---

# 51. Dark Mode cho Book Reader

Đây là một case đặc biệt.

Không chỉ:

```text
background
text
```

mà còn:

```text
chapter title
metadata
links
selection
code block
quote
image background
```

Ví dụ:

```text
Reader Theme
│
├── page background
├── content background
├── primary text
├── secondary text
├── link
├── quote
└── code block
```

Nếu sau này bạn làm app đọc truyện thật, nên xây riêng một **ReaderTheme**.

---

# 52. Dark Mode cho TTS App

TTS app:

```text
Text Editor
Voice selector
Rate
Pitch
Volume
Generate button
Progress
```

Dark mode phải giữ:

```text
Input contrast
Button contrast
Slider visibility
Progress visibility
```

Không chỉ đổi background.

---

# 53. Accessibility

Dark/Light Theme phải đảm bảo:

```text
Contrast
Readability
Focus state
Disabled state
Error state
```

Đặc biệt:

```text
gray text
```

trên:

```text
gray background
```

là một lỗi phổ biến.

---

# 54. Focus state

Ví dụ TextField:

```text
Normal
Focused
Error
Disabled
```

Mỗi state cần hiển thị rõ trong cả:

```text
Light
Dark
```

Đây là lý do không nên chỉ test:

```text
happy path
```

---

# 55. Testing Dark Mode

Bạn nên test:

```text
Light
Dark
System
```

và:

```text
Button
Input
Card
Dialog
Navigation
Error
Disabled
Loading
```

Checklist:

```text
□ Text readable
□ Button readable
□ Border visible
□ Input visible
□ Error visible
□ Disabled distinguishable
□ Icons visible
```

---

# 56. Bài tập 1 — Theme Selector

Tạo Settings:

```text
Theme

○ Light
○ Dark
○ System
```

Khi chọn:

```text
page.theme_mode
```

được cập nhật.

---

# 57. Bài tập 2 — Persistence

Lưu:

```text
light
dark
system
```

Sau khi restart app:

```text
load preference
↓
apply
```

---

# 58. Bài tập 3 — Theme-aware Dashboard

Dashboard có:

```text
Stats
Workers
Jobs
```

Chuyển:

```text
Light ↔ Dark
```

không được có:

```python
if dark:
```

trong từng Card.

---

# 59. Bài tập 4 — Status Badge

Tạo:

```text
RUNNING
SUCCESS
FAILED
PAUSED
IDLE
```

Map sang semantic roles:

```text
primary
success
error
warning
neutral
```

Sau đó Light/Dark tự điều chỉnh.

---

# 60. Bài tập 5 — System Mode

Đặt:

```python
page.theme_mode = ft.ThemeMode.SYSTEM
```

Sau đó thay đổi Dark/Light của OS và quan sát app.

---

# 61. Mini Project

Xây:

# **Theme Settings System**

Architecture:

```text
app/
│
├── main.py
│
├── theme/
│   ├── light.py
│   ├── dark.py
│   └── preference.py
│
├── settings/
│   ├── repository.py
│   └── controller.py
│
└── screens/
    └── settings.py
```

Flow:

```text
Settings Screen
      │
      ↓
Theme Controller
      │
      ├─────────────┐
      ↓             ↓
Persistence      Flet Page
      │             │
      ↓             ↓
  saved state    theme_mode
```

---

# 62. Phiên bản đơn giản trước

Không cần Repository ngay.

Hãy bắt đầu:

```python
import flet as ft


def main(page: ft.Page):

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
        )
    )

    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_200,
        )
    )

    def set_light(e):
        page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    def set_dark(e):
        page.theme_mode = ft.ThemeMode.DARK
        page.update()

    def set_system(e):
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.update()

    page.add(
        ft.Column(
            controls=[
                ft.Text(
                    "Theme Settings",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    controls=[
                        ft.Button(
                            "Light",
                            on_click=set_light,
                        ),
                        ft.Button(
                            "Dark",
                            on_click=set_dark,
                        ),
                        ft.Button(
                            "System",
                            on_click=set_system,
                        ),
                    ]
                ),
            ]
        )
    )


ft.run(main)
```

Đây là phiên bản nền tảng.

---

# 63. Sau đó refactor

Khi đã chạy được:

```text
main.py
```

thì chuyển thành:

```text
theme/
    factory.py

settings/
    controller.py

screens/
    settings.py
```

Đây là cách học tốt:

> **Working code → refactor → architecture.**

Không phải:

> Architecture → abstraction → abstraction → chưa chạy được gì.

---

# 64. Mental Model quan trọng nhất

Hãy nhớ:

```text
              User Preference
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        LIGHT       DARK      SYSTEM
          │          │          │
          └──────────┼──────────┘
                     ↓
                Flet Theme
                     │
              ┌──────┴──────┐
              ↓             ↓
          Light Theme   Dark Theme
              │             │
              └──────┬──────┘
                     ↓
                Components
                     ↓
                  Screens
```

Và:

> **`page.theme_mode` là UI representation của theme preference, không nhất thiết phải là application state duy nhất.**

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
24. Theme                            ✅
25. Dark / Light mode                ✅
26. Mini Project: Dashboard
```

## Buổi 26 — Mini Project: Dashboard

Chúng ta sẽ **ghép toàn bộ Giai đoạn II** thành một Dashboard Flet hoàn chỉnh:

```text
Responsive Layout
        +
Row / Column / Container
        +
ResponsiveRow
        +
GridView / ListView
        +
Tabs
        +
Cards
        +
Alignment / Spacing
        +
Theme
        +
Dark / Light
        ↓
   Crawl Dashboard
```

Và lần này sẽ tập trung vào **kiến trúc project thực tế**, tách `layout`, `components`, `theme`, `state` và `screens`, thay vì viết toàn bộ ứng dụng trong một `main.py`.
