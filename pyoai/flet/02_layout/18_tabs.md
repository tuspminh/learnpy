# Buổi 18 — `Tabs` Deep Dive

Hôm nay chúng ta học **`Tabs`** trong Flet.

`Tabs` rất quan trọng khi xây các màn hình có nhiều nhóm nội dung nhưng muốn giữ tất cả trong **một page**.

Ví dụ với app đọc truyện:

```text
┌────────────────────────────────────────────┐
│ Naruto                                     │
├────────────────────────────────────────────┤
│ [Thông tin] [Chapters] [Bình luận]        │
├────────────────────────────────────────────┤
│                                            │
│       Nội dung của tab hiện tại            │
│                                            │
└────────────────────────────────────────────┘
```

Và đặc biệt hôm nay chúng ta sẽ kết hợp:

```text
Tabs
 ├── Tab 1 → Book Info
 ├── Tab 2 → ListView → Chapters
 └── Tab 3 → ListView → Comments
```

---

# 1. `Tabs` là gì?

`Tabs` là UI component dùng để chuyển đổi giữa nhiều nội dung.

Mental model:

```text
Tabs
│
├── Tab A
├── Tab B
└── Tab C
```

Người dùng chọn:

```text
Tab A
 ↓
Content A
```

hoặc:

```text
Tab B
 ↓
Content B
```

---

# 2. Ví dụ cơ bản

Một `Tabs` thường gồm:

```text
Tabs
├── Tab
├── Tab
├── Tab
└── content
```

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Home",
                content=ft.Text("Home content"),
            ),
            ft.Tab(
                text="Profile",
                content=ft.Text("Profile content"),
            ),
            ft.Tab(
                text="Settings",
                content=ft.Text("Settings content"),
            ),
        ],
    )

    page.add(tabs)


ft.run(main)
```

Kết quả:

```text
[ Home ] [ Profile ] [ Settings ]

--------------------------------

Home content
```

Click:

```text
[ Profile ]
```

thì:

```text
Profile content
```

được hiển thị.

---

# 3. Mental model quan trọng

Hãy phân biệt:

```text
Tab
```

và:

```text
Tab content
```

Ví dụ:

```text
[Chapters]
```

là tab header.

Còn:

```text
Chapter 1
Chapter 2
Chapter 3
```

là content.

Mental model:

```text
Tabs
│
├── Tab
│   ├── label
│   └── content
│
├── Tab
│   ├── label
│   └── content
│
└── Tab
    ├── label
    └── content
```

---

# 4. `selected_index`

Ví dụ:

```python
ft.Tabs(
    selected_index=0,
)
```

Nghĩa là tab đầu tiên được chọn.

```text
index

0 → Info
1 → Chapters
2 → Comments
```

Nếu:

```python
selected_index=1
```

thì:

```text
Info
Chapters ← selected
Comments
```

---

# 5. Thay đổi tab bằng code

Đây là một khả năng rất quan trọng.

Ví dụ:

```python
tabs.selected_index = 1
page.update()
```

Sau đó:

```text
Chapters
```

được chọn.

Mental model:

```text
User
 ↓
click button
 ↓
tabs.selected_index = 1
 ↓
page.update()
 ↓
Chapters tab
```

---

# 6. Event khi đổi tab

`Tabs` có thể phản ứng khi người dùng thay đổi tab.

Concept:

```python
def on_tab_change(e):
    print(e.control.selected_index)
```

Sau đó:

```python
tabs = ft.Tabs(
    selected_index=0,
    on_change=on_tab_change,
    tabs=[
        ...
    ],
)
```

Khi user chuyển:

```text
Info → Chapters
```

handler được gọi.

---

# 7. `e.control`

Trong event:

```python
def on_tab_change(e):
    tabs = e.control
```

`e.control` chính là control phát sinh event.

Sau đó:

```python
index = e.control.selected_index

print(index)
```

Nếu user chọn tab thứ 2:

```text
1
```

---

# 8. Vì sao `selected_index` quan trọng?

Giả sử:

```text
Book Detail
```

Có:

```text
[Info] [Chapters] [Comments]
```

User bấm:

```text
Read Now
```

Bạn muốn chuyển thẳng tới:

```text
[Chapters]
```

Có thể:

```python
tabs.selected_index = 1
page.update()
```

Đây là navigation **trong cùng một màn hình**.

---

# 9. Tabs + `Column`

Một pattern rất phổ biến:

```python
page.add(
    ft.Column(
        expand=True,
        controls=[
            ft.Text(
                "Book Detail",
                size=24,
            ),

            tabs,
        ],
    )
)
```

Tree:

```text
Page
│
└── Column
    │
    ├── Header
    │
    └── Tabs
        ├── Info
        ├── Chapters
        └── Comments
```

---

# 10. `expand=True`

Đối với màn hình thực tế, thường muốn Tabs chiếm phần còn lại:

```python
ft.Tabs(
    expand=True,
    tabs=[...],
)
```

Ví dụ:

```python
page.add(
    ft.Column(
        expand=True,
        controls=[
            ft.Text("Book Detail"),
            ft.Tabs(
                expand=True,
                tabs=[...],
            ),
        ],
    )
)
```

Layout:

```text
┌───────────────────────────────┐
│ Book Detail                   │
├───────────────────────────────┤
│ [Info] [Chapters] [Comments]  │
│                               │
│                               │
│          content              │
│                               │
│                               │
└───────────────────────────────┘
```

---

# 11. Tab chứa `ListView`

Đây là phần cực kỳ quan trọng.

```python
chapters = ft.ListView(
    expand=True,
    spacing=5,
)

for i in range(100):
    chapters.controls.append(
        ft.ListTile(
            title=ft.Text(
                f"Chapter {i + 1}"
            )
        )
    )
```

Sau đó:

```python
tabs = ft.Tabs(
    expand=True,
    tabs=[
        ft.Tab(
            text="Chapters",
            content=chapters,
        ),
    ],
)
```

Kết quả:

```text
Tabs
│
└── Chapters
     │
     └── ListView
          ├── Chapter 1
          ├── Chapter 2
          ├── Chapter 3
          └── ...
```

---

# 12. Đây là pattern cực kỳ quan trọng

Bạn sẽ thường xuyên gặp:

```text
Tabs
│
├── Tab
│   └── Column
│
├── Tab
│   └── ListView
│
└── Tab
    └── GridView
```

Ví dụ app truyện:

```text
Tabs
│
├── Info
│   └── Column
│
├── Chapters
│   └── ListView
│
└── Related Books
    └── GridView
```

---

# 13. Tab Info

Ví dụ:

```python
info_tab = ft.Column(
    controls=[
        ft.Text(
            "Naruto",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text("Author: Masashi Kishimoto"),
        ft.Text("Status: Completed"),
        ft.Text("Genres: Action, Adventure"),
    ]
)
```

Sau đó:

```python
ft.Tab(
    text="Info",
    content=info_tab,
)
```

---

# 14. Tab Chapters

```python
chapter_list = ft.ListView(
    expand=True,
)

for i in range(100):
    chapter_list.controls.append(
        ft.ListTile(
            title=ft.Text(
                f"Chapter {i + 1}"
            ),
        )
    )
```

```python
ft.Tab(
    text="Chapters",
    content=chapter_list,
)
```

---

# 15. Tab Comments

```python
comments = ft.ListView(
    expand=True,
    controls=[
        ft.ListTile(
            title=ft.Text("User A"),
            subtitle=ft.Text(
                "Great chapter!"
            ),
        ),
        ft.ListTile(
            title=ft.Text("User B"),
            subtitle=ft.Text(
                "Interesting story."
            ),
        ),
    ],
)
```

```python
ft.Tab(
    text="Comments",
    content=comments,
)
```

---

# 16. Ghép thành Book Detail

```python
import flet as ft


def main(page: ft.Page):

    info_tab = ft.Column(
        controls=[
            ft.Text(
                "Naruto",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Author: Masashi Kishimoto"
            ),
            ft.Text(
                "Status: Completed"
            ),
        ]
    )

    chapter_list = ft.ListView(
        expand=True,
    )

    for i in range(100):
        chapter_list.controls.append(
            ft.ListTile(
                title=ft.Text(
                    f"Chapter {i + 1}"
                ),
            )
        )

    comments = ft.ListView(
        expand=True,
        controls=[
            ft.ListTile(
                title=ft.Text("User A"),
                subtitle=ft.Text(
                    "Great chapter!"
                ),
            ),
            ft.ListTile(
                title=ft.Text("User B"),
                subtitle=ft.Text(
                    "Nice story."
                ),
            ),
        ],
    )

    tabs = ft.Tabs(
        expand=True,
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Info",
                content=info_tab,
            ),
            ft.Tab(
                text="Chapters",
                content=chapter_list,
            ),
            ft.Tab(
                text="Comments",
                content=comments,
            ),
        ],
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "Book Detail",
                    size=24,
                ),
                tabs,
            ],
        )
    )


ft.run(main)
```

---

# 17. UI Tree của ví dụ trên

```text
Page
│
└── Column
    │
    ├── Text
    │
    └── Tabs
        │
        ├── Tab: Info
        │   └── Column
        │       ├── Text
        │       ├── Text
        │       └── Text
        │
        ├── Tab: Chapters
        │   └── ListView
        │       ├── ListTile
        │       ├── ListTile
        │       └── ...
        │
        └── Tab: Comments
            └── ListView
                ├── ListTile
                └── ListTile
```

Đây chính là **UI composition**.

---

# 18. Tabs không chỉ chứa Text

Một `Tab` có thể chứa gần như bất kỳ UI tree nào.

Ví dụ:

```text
Tab
│
└── Column
    ├── Row
    ├── Container
    ├── ListView
    └── GridView
```

Hoặc:

```text
Tab
│
└── Stack
    ├── Image
    └── Container
```

Vì vậy:

> `Tabs` là container/navigation mechanism, không phải một loại layout nội dung cụ thể.

---

# 19. Tabs + GridView

Ví dụ Library:

```text
[Books] [Authors] [Genres]

Books:
┌────┐ ┌────┐ ┌────┐
│ A  │ │ B  │ │ C  │
└────┘ └────┘ └────┘
```

Code concept:

```python
book_grid = ft.GridView(
    expand=True,
    runs_count=4,
)

tabs = ft.Tabs(
    expand=True,
    tabs=[
        ft.Tab(
            text="Books",
            content=book_grid,
        ),
    ],
)
```

---

# 20. Tabs + Stack

Có thể làm:

```text
Tab
│
└── Stack
    │
    ├── Cover
    └── Overlay
```

Ví dụ:

```text
┌──────────────────────────┐
│                          │
│        BOOK COVER        │
│                          │
│  ┌────────────────────┐  │
│  │ Read Now           │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

Điều này kết nối với kiến thức **Buổi 14 — Stack**.

---

# 21. Tabs + Search

Ví dụ:

```text
[All] [Unread] [Downloaded]

[ Search................ ]

Chapter 1
Chapter 2
Chapter 3
```

Tree:

```text
Tab
│
└── Column
    │
    ├── TextField
    │
    └── ListView
```

---

# 22. Tabs + state

Giả sử:

```python
selected_tab = 0
```

User click:

```text
Chapters
```

thì:

```text
selected_tab = 1
```

State có thể là:

```python
state = {
    "selected_tab": 1,
}
```

UI:

```text
state
 ↓
Tabs.selected_index
```

---

# 23. Một pattern quan trọng: Tab không nhất thiết render lại data

Giả sử bạn có:

```text
Info
Chapters
Comments
```

Khi chuyển:

```text
Info → Chapters
```

`chapter_list` đã tồn tại.

Bạn chỉ thay đổi:

```python
tabs.selected_index
```

Điều này khác với việc bạn phải tạo lại toàn bộ UI mỗi lần.

---

# 24. Lazy loading tab

Tuy nhiên với dữ liệu lớn, ta có thể muốn:

```text
User mở Chapters
        ↓
load chapters
```

thay vì:

```text
App startup
   ↓
load Info
load Chapters
load Comments
```

Mental model:

```text
App start
   ↓
Info only

User click Chapters
   ↓
load chapters

User click Comments
   ↓
load comments
```

Đây là một pattern rất tốt khi kết hợp với network/database.

---

# 25. Ví dụ lazy loading

Ta có:

```python
loaded = {
    "chapters": False,
    "comments": False,
}
```

Khi đổi tab:

```python
def on_tab_change(e):

    index = e.control.selected_index

    if index == 1 and not loaded["chapters"]:
        load_chapters()
        loaded["chapters"] = True

    page.update()
```

Flow:

```text
Tab change
    ↓
selected_index
    ↓
need data?
    ↓
load
    ↓
update
```

---

# 26. Lazy loading với async

Sau này có thể:

```python
async def load_chapters():
    chapters = await repository.get_chapters()
```

Event:

```text
Tabs changed
     ↓
async load
     ↓
show loading
     ↓
data
     ↓
ListView
```

Ví dụ UX:

```text
[Info] [Chapters] [Comments]

        Loading...
```

sau đó:

```text
[Info] [Chapters] [Comments]

Chapter 1
Chapter 2
Chapter 3
...
```

---

# 27. Tabs và navigation

Có hai kiểu navigation:

### Page navigation

```text
Home
 ↓
Book Detail
 ↓
Reader
```

### Tab navigation

```text
Book Detail

[Info]
[Chapters]
[Comments]
```

Tab navigation không nhất thiết thay đổi route/page.

Mental model:

```text
Route
→ thay đổi màn hình

Tabs
→ thay đổi khu vực nội dung trong màn hình
```

---

# 28. Khi nào dùng Tabs?

Dùng khi các nội dung:

* liên quan chặt chẽ
* cùng thuộc một entity
* người dùng thường xuyên chuyển đổi

Ví dụ:

```text
Book
├── Info
├── Chapters
└── Comments
```

Rất phù hợp.

---

# 29. Khi nào không nên dùng Tabs?

Không nên biến toàn bộ app thành:

```text
[Home]
[Library]
[Settings]
[Downloads]
[Reader]
[Admin]
```

Nếu các phần này là những khu vực chức năng lớn, tốt hơn dùng:

```text
NavigationRail
NavigationBar
Sidebar
Routes
```

Tabs phù hợp hơn với **sub-sections của cùng một context**.

---

# 30. Tabs vs Navigation

Ví dụ:

```text
App
│
├── Home
├── Library
├── Downloads
└── Settings
```

→ Navigation.

Trong:

```text
Book Detail
│
├── Info
├── Chapters
└── Comments
```

→ Tabs.

Đây là distinction rất quan trọng khi thiết kế UI.

---

# 31. Tabs + `ListView` trong app crawler

Đây là ví dụ cực kỳ sát với project của bạn.

Dashboard:

```text
[Queue] [Running] [Completed] [Failed]
```

Mỗi tab:

```text
Queue
 ↓
ListView

Running
 ↓
ListView

Completed
 ↓
ListView

Failed
 ↓
ListView
```

Tree:

```text
Tabs
│
├── Queue
│   └── ListView
│
├── Running
│   └── ListView
│
├── Completed
│   └── ListView
│
└── Failed
    └── ListView
```

Đây là một UI pattern rất thực tế.

---

# 32. Filter queue theo tab

Thay vì tạo 4 danh sách độc lập, có thể có:

```python
jobs = [
    {"id": 1, "status": "waiting"},
    {"id": 2, "status": "running"},
    {"id": 3, "status": "completed"},
]
```

Tab:

```text
Queue
```

filter:

```python
job["status"] == "waiting"
```

Tab:

```text
Running
```

filter:

```python
job["status"] == "running"
```

Architecture:

```text
jobs
 ↓
filter(status)
 ↓
ListView
```

---

# 33. Tabs + event bus

Trong crawler framework lớn hơn:

```text
Crawler Worker
      ↓
Event Bus
      ↓
Dashboard State
      ↓
Tabs
      ↓
ListView
```

Ví dụ worker phát event:

```text
JobCompleted
```

Dashboard cập nhật:

```text
Completed tab
```

Đây là kiến trúc mà sau này bạn có thể kết hợp với:

* asyncio
* queue server
* crawl worker
* event-driven architecture

---

# 34. Một Book Detail Page tốt hơn

Hãy thiết kế:

```text
┌──────────────────────────────────────────────┐
│ ← Back                                      │
├──────────────────────────────────────────────┤
│ Cover    Naruto                              │
│          Author: Kishimoto                   │
│          [Read]                               │
├──────────────────────────────────────────────┤
│ [Info] [Chapters] [Comments]                │
├──────────────────────────────────────────────┤
│                                              │
│ Chapter 1200                                │
│ Chapter 1199                                │
│ Chapter 1198                                │
│ ...                                          │
│                                              │
└──────────────────────────────────────────────┘
```

Tree:

```text
BookDetailPage
│
└── Column
    │
    ├── BookHeader
    │
    └── Tabs
        │
        ├── Info
        ├── Chapters
        │   └── ListView
        │
        └── Comments
            └── ListView
```

Đây là bài tập rất đáng làm.

---

# 35. Mini Project hôm nay

## Book Detail Tabs

Tạo ứng dụng:

```text
Book Detail
```

### Tab 1 — Info

Hiển thị:

```text
Title
Author
Status
Genres
Description
```

### Tab 2 — Chapters

Có ít nhất 50 chapter:

```text
Chapter 1
Chapter 2
...
Chapter 50
```

Dùng:

```text
ListView
```

### Tab 3 — Comments

Có:

```text
User A
User B
User C
...
```

Cũng dùng:

```text
ListView
```

### Yêu cầu

1. `Tabs` chiếm toàn bộ phần còn lại.
2. `Chapters` có scroll.
3. `Comments` có scroll.
4. Click chapter in ra chapter ID.
5. Có nút `Read Now`.
6. Click `Read Now` tự chuyển sang tab `Chapters`.

---

# 36. Bài tập nâng cao

Thêm:

```text
[Info] [Chapters] [Comments]
```

Khi click `Chapters`:

```text
Loading...
```

sau đó:

```text
Chapter 1
Chapter 2
...
```

Giả lập loading:

```python
async def load_chapters():
    ...
```

Mục tiêu:

```text
Tabs
 ↓
event
 ↓
async
 ↓
state
 ↓
ListView
 ↓
page.update()
```

Đây là bài tập kết hợp rất nhiều kiến thức bạn đã học.

---

# 37. Những lỗi cần tránh

### Lỗi 1 — Dùng Tabs cho navigation toàn app

```text
Home
Library
Settings
```

Không phải use case lý tưởng.

---

### Lỗi 2 — Tab chứa danh sách nhưng không `expand`

Ví dụ:

```python
ft.Tab(
    content=ft.ListView(...)
)
```

Nếu sizing không đúng, list có thể không chiếm được không gian mong muốn.

Thường nên thiết kế:

```python
ft.ListView(
    expand=True,
)
```

và kiểm soát constraints của parent.

---

### Lỗi 3 — Load tất cả dữ liệu ngay từ đầu

Không nên:

```text
App startup
 ↓
load 100,000 chapters
 ↓
load 50,000 comments
```

Nên cân nhắc:

```text
Tab activated
 ↓
load data
```

---

### Lỗi 4 — UI tự truy cập database

Không nên:

```text
Tab
 ↓
SQLite
```

Nên:

```text
Tab
 ↓
Use Case
 ↓
Repository
 ↓
SQLite
```

---

# 38. Tổng kết kiến thức

Hôm nay bạn cần nắm chắc:

```text
ft.Tabs
```

và:

```text
selected_index
```

```text
on_change
```

cùng với:

```text
Tab
```

và cách kết hợp:

```text
Tabs
├── Column
├── ListView
├── GridView
├── Stack
└── Container
```

Đặc biệt:

```text
Book Detail
│
└── Tabs
    ├── Info
    ├── Chapters → ListView
    └── Comments → ListView
```

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
19. Card, ExpansionTile, ListTile    ← tiếp theo
20. Layout constraints & sizing
21. Alignment
22. Spacing / padding / margin
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

**Điểm quan trọng nhất của Buổi 18:** đừng chỉ học `Tabs` như một control. Hãy nhìn nó như một **composition/navigation mechanism bên trong một context**. Với project đọc truyện của bạn, pattern `BookDetail → Tabs → ListView` sẽ là một pattern nền tảng.
