# Buổi 26 — Mini Project: Crawl Dashboard

Hôm nay chúng ta **kết thúc Giai đoạn II — Layout Deep Dive** bằng một project tổng hợp.

Mục tiêu không phải chỉ tạo một giao diện đẹp, mà là học cách **tổ chức một Flet application có khả năng mở rộng**.

Project:

> **Crawl Dashboard** — giao diện quản lý crawler/worker.

Chúng ta sẽ sử dụng lại gần như toàn bộ kiến thức từ Buổi 11 → 25.

---

# 1. Mục tiêu project

Dashboard sẽ có:

```text
┌─────────────────────────────────────────────────────────────┐
│ Crawl Dashboard                              ☀️  🔄         │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│ Dashboard     │  Crawl Dashboard                           │
│ Jobs          │                                             │
│ Workers       │                                             │
│ Sources       │  ┌────────┐ ┌────────┐ ┌────────┐          │
│ Settings      │  │ Jobs   │ │Running │ │Failed  │          │
│               │  │  1,250 │ │   12   │ │    3   │          │
│               │  └────────┘ └────────┘ └────────┘          │
│               │                                             │
│               │  Workers                                    │
│               │  ┌──────────────────────────────────────┐  │
│               │  │ Worker 01       RUNNING       120     │  │
│               │  ├──────────────────────────────────────┤  │
│               │  │ Worker 02       IDLE           0      │  │
│               │  ├──────────────────────────────────────┤  │
│               │  │ Worker 03       FAILED         5      │  │
│               │  └──────────────────────────────────────┘  │
│               │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

---

# 2. Những kiến thức sẽ sử dụng

| Kiến thức     | Sử dụng             |
| ------------- | ------------------- |
| Row           | Header / stat cards |
| Column        | Sidebar / content   |
| Container     | Panel               |
| Stack         | Badge / overlay     |
| ResponsiveRow | Dashboard           |
| GridView      | Stat cards          |
| ListView      | Worker list         |
| Tabs          | Jobs / Workers      |
| Card          | Statistics          |
| ListTile      | Worker              |
| Alignment     | Header              |
| Padding       | Spacing             |
| Margin        | Layout              |
| Responsive UI | Desktop/mobile      |
| Theme         | Design system       |
| Dark mode     | Theme switching     |

Đây là lý do project này nằm ở cuối Giai đoạn II.

---

# 3. Architecture

Không viết:

```text
main.py
  1000 dòng
```

Chúng ta bắt đầu với:

```text
crawl_dashboard/
│
├── main.py
│
├── theme/
│   ├── __init__.py
│   └── theme.py
│
├── models/
│   ├── __init__.py
│   ├── worker.py
│   └── job.py
│
├── components/
│   ├── __init__.py
│   ├── stat_card.py
│   ├── worker_card.py
│   └── sidebar.py
│
├── screens/
│   ├── __init__.py
│   └── dashboard.py
│
└── layouts/
    ├── __init__.py
    └── dashboard_layout.py
```

---

# 4. Tư duy Architecture

Flow:

```text
main.py
   │
   ↓
DashboardLayout
   │
   ├── Sidebar
   │
   └── DashboardScreen
           │
           ├── StatCard
           ├── WorkerCard
           └── JobList
```

Theme:

```text
main.py
   ↓
Theme
   ↓
Components
```

Data:

```text
models
   ↓
screens
   ↓
components
```

---

# 5. Model Worker

Tạo:

```text
models/worker.py
```

```python
from dataclasses import dataclass


@dataclass
class Worker:
    id: int
    name: str
    status: str
    jobs: int
```

Ví dụ:

```python
workers = [
    Worker(
        id=1,
        name="Worker 01",
        status="running",
        jobs=120,
    ),
    Worker(
        id=2,
        name="Worker 02",
        status="idle",
        jobs=0,
    ),
    Worker(
        id=3,
        name="Worker 03",
        status="failed",
        jobs=5,
    ),
]
```

---

# 6. Vì sao dùng Model?

Không nên:

```python
workers = [
    ["Worker 01", "running", 120],
    ["Worker 02", "idle", 0],
]
```

Vì rất khó hiểu:

```text
[0] = ?
[1] = ?
[2] = ?
```

Với model:

```python
worker.name
worker.status
worker.jobs
```

rõ ràng hơn.

Đây cũng phù hợp với hướng **Model → Repository → Database** mà bạn đang xây cho crawler.

---

# 7. Theme

Tạo:

```text
theme/theme.py
```

```python
import flet as ft


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

# 8. Main

`main.py`:

```python
import flet as ft

from theme.theme import (
    create_dark_theme,
    create_light_theme,
)
from screens.dashboard import Dashboard


def main(page: ft.Page):

    page.title = "Crawl Dashboard"

    page.theme = create_light_theme()
    page.dark_theme = create_dark_theme()

    page.theme_mode = ft.ThemeMode.SYSTEM

    dashboard = Dashboard(page)

    page.add(dashboard)


ft.run(main)
```

Hiện tại chưa cần:

```text
Repository
Database
Service
Controller
```

Chúng ta chỉ tập trung vào UI.

---

# 9. Stat Card

Tạo:

```text
components/stat_card.py
```

```python
import flet as ft


class StatCard(ft.Card):

    def __init__(
        self,
        title: str,
        value: str,
        icon: str,
    ):
        super().__init__()

        self.content = ft.Container(
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                title,
                                size=14,
                            ),
                            ft.Icon(icon),
                        ],
                    ),
                    ft.Text(
                        value,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
        )
```

---

# 10. Tại sao `Card`?

Thay vì:

```text
Container
```

chúng ta dùng:

```text
Card
```

vì semantic của component là:

> Một vùng thông tin nổi độc lập.

Ví dụ:

```text
Jobs
1,250
```

là một card.

---

# 11. Worker Card

Tạo:

```text
components/worker_card.py
```

```python
import flet as ft

from models.worker import Worker


class WorkerCard(ft.Card):

    def __init__(self, worker: Worker):
        super().__init__()

        self.content = ft.ListTile(
            leading=ft.Icon(
                ft.Icons.COMPUTER,
            ),
            title=ft.Text(
                worker.name,
                weight=ft.FontWeight.BOLD,
            ),
            subtitle=ft.Text(
                f"Jobs: {worker.jobs}"
            ),
            trailing=ft.Text(
                worker.status.upper(),
            ),
        )
```

---

# 12. Vì sao `ListTile`?

Worker là một item dạng:

```text
Icon
Name
Description
Status
```

Đây chính là trường hợp phù hợp với:

```text
ListTile
```

thay vì tự dựng:

```text
Row + Container + Column + ...
```

---

# 13. Sidebar

Tạo:

```text
components/sidebar.py
```

```python
import flet as ft


class Sidebar(ft.Container):

    def __init__(self):
        super().__init__()

        self.width = 220
        self.padding = 16

        self.content = ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    "CRAWLER",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Divider(),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DASHBOARD),
                    title=ft.Text("Dashboard"),
                ),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.WORK),
                    title=ft.Text("Jobs"),
                ),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.COMPUTER),
                    title=ft.Text("Workers"),
                ),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LANGUAGE),
                    title=ft.Text("Sources"),
                ),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    title=ft.Text("Settings"),
                ),
            ],
        )
```

---

# 14. Sidebar architecture

```text
Sidebar
│
├── Logo
│
├── Dashboard
├── Jobs
├── Workers
├── Sources
│
└── Settings
```

Sau này chúng ta sẽ biến mỗi `ListTile` thành navigation item thực sự.

---

# 15. Dashboard Screen

Tạo:

```text
screens/dashboard.py
```

```python
import flet as ft

from models.worker import Worker
from components.stat_card import StatCard
from components.worker_card import WorkerCard


class Dashboard(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.workers = [
            Worker(1, "Worker 01", "running", 120),
            Worker(2, "Worker 02", "idle", 0),
            Worker(3, "Worker 03", "failed", 5),
            Worker(4, "Worker 04", "running", 80),
        ]

        self.expand = True

        self.controls = [
            self.build_header(),
            self.build_stats(),
            self.build_workers(),
        ]
```

---

# 16. Header

```python
def build_header(self):
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=2,
                controls=[
                    ft.Text(
                        "Crawl Dashboard",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Monitor your crawler system",
                    ),
                ],
            ),

            ft.IconButton(
                icon=ft.Icons.DARK_MODE,
                on_click=self.toggle_theme,
            ),
        ],
    )
```

---

# 17. Theme Toggle

```python
def toggle_theme(self, e):

    if self.page.theme_mode == ft.ThemeMode.DARK:
        self.page.theme_mode = ft.ThemeMode.LIGHT
    else:
        self.page.theme_mode = ft.ThemeMode.DARK

    self.page.update()
```

Đây là phiên bản đơn giản.

Sau này chúng ta sẽ nâng cấp thành:

```text
Light
Dark
System
```

và persistence.

---

# 18. Stats

```python
def build_stats(self):

    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=StatCard(
                    "Total Jobs",
                    "1,250",
                    ft.Icons.WORK,
                ),
                col={
                    "xs": 12,
                    "sm": 6,
                    "md": 3,
                },
            ),

            ft.Container(
                content=StatCard(
                    "Running",
                    "12",
                    ft.Icons.PLAY_ARROW,
                ),
                col={
                    "xs": 12,
                    "sm": 6,
                    "md": 3,
                },
            ),

            ft.Container(
                content=StatCard(
                    "Completed",
                    "1,230",
                    ft.Icons.CHECK_CIRCLE,
                ),
                col={
                    "xs": 12,
                    "sm": 6,
                    "md": 3,
                },
            ),

            ft.Container(
                content=StatCard(
                    "Failed",
                    "3",
                    ft.Icons.ERROR,
                ),
                col={
                    "xs": 12,
                    "sm": 6,
                    "md": 3,
                },
            ),
        ],
    )
```

---

# 19. ResponsiveRow ở đây rất quan trọng

Desktop:

```text
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Jobs │ │ Run  │ │ Done │ │Fail  │
└──────┘ └──────┘ └──────┘ └──────┘
```

Tablet:

```text
┌────────┐ ┌────────┐
│ Jobs   │ │ Running│
└────────┘ └────────┘

┌────────┐ ┌────────┐
│ Done   │ │ Failed │
└────────┘ └────────┘
```

Mobile:

```text
┌────────────────┐
│ Jobs           │
└────────────────┘

┌────────────────┐
│ Running        │
└────────────────┘

┌────────────────┐
│ Completed      │
└────────────────┘

┌────────────────┐
│ Failed         │
└────────────────┘
```

Không cần tự viết:

```python
if width < ...
```

cho từng Card.

---

# 20. Worker List

```python
def build_workers(self):

    return ft.Column(
        spacing=12,
        controls=[
            ft.Text(
                "Workers",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            ft.ListView(
                spacing=8,
                expand=True,
                controls=[
                    WorkerCard(worker)
                    for worker in self.workers
                ],
            ),
        ],
    )
```

---

# 21. Vấn đề

Ở đây:

```python
ft.ListView(
    expand=True
)
```

đòi hỏi parent có constraint phù hợp.

Nếu bạn đặt nó vào một `Column` không có chiều cao rõ ràng, có thể gặp layout problem.

Đây chính là kiến thức:

> **Layout constraints**

của Buổi 20.

---

# 22. Layout hoàn chỉnh

Ta có:

```text
Dashboard
│
├── Header
│
├── Stats
│
└── Workers
      │
      └── ListView
```

Cấu trúc:

```text
Column
│
├── Row
│
├── ResponsiveRow
│
└── Column(expand)
      │
      └── ListView(expand)
```

---

# 23. Dashboard Layout

Bây giờ thêm Sidebar.

Tạo:

```text
layouts/dashboard_layout.py
```

```python
import flet as ft

from components.sidebar import Sidebar


class DashboardLayout(ft.Row):

    def __init__(self, content):
        super().__init__()

        self.expand = True

        self.controls = [
            Sidebar(),
            ft.VerticalDivider(width=1),
            ft.Container(
                expand=True,
                padding=24,
                content=content,
            ),
        ]
```

---

# 24. Main thay đổi

```python
from layouts.dashboard_layout import DashboardLayout
from screens.dashboard import Dashboard
```

Sau đó:

```python
def main(page: ft.Page):

    page.title = "Crawl Dashboard"

    page.theme = create_light_theme()
    page.dark_theme = create_dark_theme()
    page.theme_mode = ft.ThemeMode.SYSTEM

    dashboard = Dashboard(page)

    layout = DashboardLayout(dashboard)

    page.add(layout)
```

---

# 25. Architecture hiện tại

```text
main.py
│
├── Theme
│
└── DashboardLayout
      │
      ├── Sidebar
      │
      └── Dashboard
            │
            ├── Header
            ├── Stats
            │    ├── StatCard
            │    ├── StatCard
            │    ├── StatCard
            │    └── StatCard
            │
            └── Workers
                 ├── WorkerCard
                 ├── WorkerCard
                 ├── WorkerCard
                 └── WorkerCard
```

Đây đã là một architecture Flet khá sạch cho project nhỏ/trung bình.

---

# 26. Nhưng Mobile thì sao?

Sidebar rộng:

```text
220px
```

trên mobile sẽ rất tệ.

Desktop:

```text
┌──────────┬─────────────────────┐
│ Sidebar  │ Dashboard           │
│ 220px    │                     │
└──────────┴─────────────────────┘
```

Mobile nên:

```text
┌───────────────────────────────┐
│ ☰   Crawl Dashboard           │
├───────────────────────────────┤
│ Dashboard                     │
│                               │
└───────────────────────────────┘
```

Đây là lúc kiến thức Responsive UI thực sự phát huy tác dụng.

---

# 27. Responsive Navigation

Có thể dùng:

```text
Desktop
→ Sidebar

Mobile
→ NavigationDrawer
```

Mental model:

```text
Screen width
     │
     ├── Desktop → Sidebar
     │
     └── Mobile  → Drawer
```

Không phải:

```text
Sidebar width = 60
```

---

# 28. Tạo AppShell

Một kiến trúc tốt hơn:

```text
AppShell
│
├── Navigation
│
└── Content
```

Navigation implementation:

```text
Desktop → Sidebar
Mobile  → Drawer
```

Như vậy Screen không cần biết navigation đang được render bằng gì.

---

# 29. Đây là abstraction quan trọng

Không:

```text
Dashboard
→ Sidebar
```

Mà:

```text
Dashboard
→ AppShell
    ├── Navigation
    └── Content
```

Sau này:

```text
Navigation
├── Sidebar
├── NavigationRail
└── Drawer
```

---

# 30. Theme + Responsive + Components

Đây là architecture chúng ta muốn đạt tới:

```text
                    App
                     │
                 AppShell
              ┌──────┴──────┐
              ↓             ↓
         Navigation       Content
              │             │
        Responsive       Screens
              │             │
              └──────┬──────┘
                     ↓
                Components
                     ↑
                     │
                   Theme
```

---

# 31. Tabs

Dashboard có thể thêm:

```text
┌──────────┬───────────┐
│ Workers  │ Jobs      │
└──────────┴───────────┘
```

Ví dụ:

```python
ft.Tabs(
    selected_index=0,
    tabs=[
        ft.Tab(
            text="Workers",
            content=workers_view,
        ),
        ft.Tab(
            text="Jobs",
            content=jobs_view,
        ),
    ],
)
```

Đây là kiến thức Buổi 18.

---

# 32. GridView

Stat cards cũng có thể dùng:

```python
ft.GridView(
    runs_count=4,
    spacing=16,
    run_spacing=16,
    controls=[
        StatCard(...),
        StatCard(...),
        StatCard(...),
        StatCard(...),
    ],
)
```

Nhưng:

> Không phải lúc nào GridView cũng tốt hơn ResponsiveRow.

---

# 33. Khi nào dùng ResponsiveRow?

Dùng khi:

```text
Card layout
12-column grid
Responsive breakpoints
```

Ví dụ:

```text
12 columns
```

Stat cards:

```text
3 + 3 + 3 + 3
```

Mobile:

```text
12
12
12
12
```

---

# 34. Khi nào dùng GridView?

Dùng khi bạn có:

```text
nhiều item đồng nhất
```

Ví dụ:

```text
Book cards
Image cards
Product cards
Gallery
```

---

# 35. Khi nào dùng ListView?

Dùng:

```text
long list
dynamic list
scrolling data
```

Ví dụ:

```text
Worker logs
Crawler jobs
Download queue
```

---

# 36. Đây là Design Decision

Không phải:

```text
"Flet có GridView → dùng GridView"
```

Mà:

```text
Requirement
     ↓
Layout behavior
     ↓
Choose control
```

Ví dụ:

```text
4 statistic cards
→ ResponsiveRow

1000 jobs
→ ListView

Book gallery
→ GridView
```

---

# 37. Stack trong Dashboard

Có thể dùng `Stack` cho notification:

```text
┌────────────────────┐
│ Worker             │
│                    │
│              🔴 3  │
└────────────────────┘
```

Ví dụ:

```python
ft.Stack(
    controls=[
        card,
        ft.Container(
            right=8,
            top=8,
            content=ft.Badge(...),
        ),
    ]
)
```

Đây là trường hợp `Stack` có ý nghĩa.

---

# 38. Spacing System

Thay vì:

```python
padding=17
spacing=13
margin=11
```

nên thống nhất:

```text
4
8
12
16
24
32
48
```

Ví dụ:

```python
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
```

Dashboard:

```python
padding=SPACING_LG
spacing=SPACING_MD
```

UI sẽ nhất quán hơn.

---

# 39. Radius System

Tương tự:

```python
RADIUS_SM = 4
RADIUS_MD = 8
RADIUS_LG = 12
```

Card:

```text
12
```

Button:

```text
8
```

Input:

```text
8
```

Đây là Design Token.

---

# 40. State hiện tại

Dashboard có thể có:

```text
workers
jobs
selected_tab
theme
```

Nhưng chưa cần database.

Ta có:

```text
UI State
```

và:

```text
Domain Data
```

tách biệt.

---

# 41. Đừng làm thế này

```python
class Dashboard(ft.Column):

    workers = [...]
    jobs = [...]

    def save_to_database(self):
        ...
    
    def crawl(self):
        ...
    
    def parse_chapter(self):
        ...
```

Đó là trộn:

```text
UI
Database
Business logic
Crawler
```

---

# 42. Architecture đúng hơn

Sau này:

```text
UI
 ↓
Application Service
 ↓
Repository
 ↓
Database
```

Ví dụ:

```text
Dashboard
   ↓
WorkerService
   ↓
WorkerRepository
   ↓
SQLite
```

Flet chỉ là UI layer.

---

# 43. Điều này cực kỳ quan trọng với project crawler của bạn

Bạn đang xây:

```text
Crawler
Worker
Queue
Repository
Database
Plugin
```

Flet Dashboard chỉ nên là:

```text
Presentation Layer
```

Architecture tương lai:

```text
                 Flet
                  │
             Presentation
                  │
             Application
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
   CrawlService QueueService WorkerService
       │          │          │
       └──────────┼──────────┘
                  ↓
             Infrastructure
                  │
             SQLite / Queue
```

Đây chính là hướng chúng ta sẽ đi ở các giai đoạn Flet nâng cao.

---

# 44. Version 1 của Dashboard

Ở thời điểm này:

```text
UI
├── Sidebar
├── Header
├── Stats
├── Workers
└── Theme
```

Data:

```text
hard-coded mock data
```

Đây là hoàn toàn hợp lý.

Không nên vội kết nối database.

---

# 45. Version 2

Sau này:

```text
Mock Data
   ↓
Repository
```

Ví dụ:

```text
WorkerRepository
JobRepository
```

---

# 46. Version 3

Sau đó:

```text
SQLite
```

```text
Dashboard
   ↓
Service
   ↓
Repository
   ↓
SQLite
```

---

# 47. Version 4

Cuối cùng:

```text
Crawler
Worker
Queue
Dashboard
```

cùng hoạt động:

```text
                  Dashboard
                      │
                      ↓
                  Controller
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        Queue       Worker      Crawler
          │           │           │
          └───────────┼───────────┘
                      ↓
                   Storage
```

Đó sẽ là một Flet application thực tế.

---

# 48. Bài tập chính

Hãy tự hoàn thành Dashboard với:

### Sidebar

```text
Dashboard
Jobs
Workers
Sources
Settings
```

### Stats

```text
Total Jobs
Running
Completed
Failed
```

### Workers

```text
Worker 01
Worker 02
Worker 03
Worker 04
```

### Theme

```text
Light
Dark
System
```

### Responsive

Desktop:

```text
Sidebar + Content
```

Mobile:

```text
Drawer + Content
```

---

# 49. Bài tập nâng cao

Thêm:

```text
Tabs
```

```text
Workers | Jobs
```

Jobs:

```text
┌─────────────────────────────────────────┐
│ Crawl Novel A       RUNNING             │
├─────────────────────────────────────────┤
│ Crawl Novel B       COMPLETED           │
├─────────────────────────────────────────┤
│ Crawl Novel C       FAILED              │
└─────────────────────────────────────────┘
```

---

# 50. Bài tập nâng cao hơn nữa

Thêm status:

```text
RUNNING
SUCCESS
FAILED
PAUSED
IDLE
```

Và semantic color:

```text
RUNNING → primary
SUCCESS → success
FAILED  → error
PAUSED  → warning
IDLE    → neutral
```

Quan trọng:

> Không hard-code màu vào từng WorkerCard.

---

# 51. Checklist hoàn thành Buổi 26

Nếu làm được các mục dưới đây thì bạn đã hoàn thành Giai đoạn II khá chắc:

```text
□ Row
□ Column
□ Container
□ Stack
□ ResponsiveRow
□ GridView
□ ListView
□ Tabs
□ Card
□ ListTile
□ Alignment
□ Padding
□ Spacing
□ Responsive layout
□ Theme
□ Light mode
□ Dark mode
□ Component architecture
□ Screen architecture
□ Layout architecture
```

---

# 52. Điều quan trọng nhất của Giai đoạn II

Không phải nhớ:

```python
ft.Row(...)
ft.Column(...)
ft.Container(...)
```

mà phải hình thành tư duy:

```text
                    UI
                     │
             ┌───────┴───────┐
             ↓               ↓
          Layout           Theme
             │               │
       Responsive        Light/Dark
             │               │
             └───────┬───────┘
                     ↓
                Components
                     ↓
                  Screens
```

Bạn đang chuyển từ:

> **"Học các Flet controls"**

sang:

> **"Thiết kế một UI system bằng Flet."**

Đây là bước chuyển rất quan trọng.

---

# Giai đoạn III — Interaction & State

Sau Buổi 26, roadmap nên chuyển sang phần tiếp theo:

### Phần 3 — Event & Interaction

**Buổi 27 — Event Model trong Flet**

**Buổi 28 — Event Handler Deep Dive**

**Buổi 29 — `ControlEvent`**

**Buổi 30 — Event Propagation**

**Buổi 31 — `on_click`**

**Buổi 32 — `on_change`**

**Buổi 33 — `on_submit`**

**Buổi 34 — Keyboard Events**

**Buổi 35 — Mouse Events**

**Buổi 36 — Gesture Events**

**Buổi 37 — Async Event Handler**

**Buổi 38 — Event Debouncing**

**Buổi 39 — Event Throttling**

**Buổi 40 — Event-driven Architecture**

**Buổi 41 — Mini Project: Interactive Task Manager**

Đây sẽ là giai đoạn rất quan trọng, bởi từ đây chúng ta bắt đầu đi từ **"UI tĩnh" → "ứng dụng Flet thực sự tương tác"**.
