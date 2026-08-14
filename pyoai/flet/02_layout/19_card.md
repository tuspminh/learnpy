# Buổi 19 — `Card`, `ExpansionTile`, `ListTile` Deep Dive

Hôm nay chúng ta học 3 control cực kỳ quan trọng để xây UI thực tế:

```text
Card
ListTile
ExpansionTile
```

Ba control này thường đi cùng nhau:

```text
Card
└── ListTile
```

hoặc:

```text
ExpansionTile
├── ListTile
├── ListTile
└── ListTile
```

Đặc biệt với project **app cào truyện + đọc truyện**, chúng ta sẽ dùng chúng cho:

* Book Card
* Chapter Item
* Menu
* Category
* Filter
* Crawl Job
* Worker
* Settings
* FAQ
* Dashboard

---

# 1. Bức tranh tổng thể

Hãy phân biệt vai trò:

```text
Card
→ tạo "bề mặt" / grouping / visual container

ListTile
→ tạo một dòng item chuẩn

ExpansionTile
→ một dòng item có thể mở rộng
```

Ví dụ:

```text
Card
┌──────────────────────────────┐
│ [icon] Naruto                │
│        1200 chapters         │
└──────────────────────────────┘
```

---

# 2. `ListTile` là gì?

`ListTile` là control được thiết kế cho **một dòng nội dung**.

Ví dụ:

```text
┌──────────────────────────────────┐
│ 📖 Chapter 1200        →         │
└──────────────────────────────────┘
```

Mental model:

```text
ListTile
│
├── leading
├── title
├── subtitle
└── trailing
```

Đây là một control cực kỳ hữu dụng khi kết hợp với `ListView`.

---

# 3. `ListTile` cơ bản

```python
import flet as ft


def main(page: ft.Page):

    page.add(
        ft.ListTile(
            title=ft.Text("Chapter 1"),
        )
    )


ft.run(main)
```

Kết quả concept:

```text
Chapter 1
```

---

# 4. `title`

`title` là nội dung chính.

```python
ft.ListTile(
    title=ft.Text("Chapter 1"),
)
```

Ví dụ:

```text
Chapter 1
```

Thông thường:

```text
title
→ thông tin chính
```

---

# 5. `subtitle`

Thêm thông tin phụ:

```python
ft.ListTile(
    title=ft.Text("Chapter 1"),
    subtitle=ft.Text(
        "The Beginning"
    ),
)
```

UI:

```text
Chapter 1
The Beginning
```

Mental model:

```text
ListTile
├── title
└── subtitle
```

---

# 6. `leading`

`leading` nằm bên trái.

```python
ft.ListTile(
    leading=ft.Icon(
        ft.Icons.MENU_BOOK
    ),
    title=ft.Text("Chapter 1"),
)
```

UI:

```text
📖  Chapter 1
```

Đây là pattern rất phổ biến.

---

# 7. `trailing`

`trailing` nằm bên phải.

```python
ft.ListTile(
    title=ft.Text("Chapter 1"),
    trailing=ft.Icon(
        ft.Icons.CHEVRON_RIGHT
    ),
)
```

UI:

```text
Chapter 1                 →
```

---

# 8. Kết hợp cả 4

```python
ft.ListTile(
    leading=ft.Icon(
        ft.Icons.MENU_BOOK
    ),
    title=ft.Text("Chapter 120"),
    subtitle=ft.Text(
        "The Final Battle"
    ),
    trailing=ft.Icon(
        ft.Icons.CHEVRON_RIGHT
    ),
)
```

Mental model:

```text
┌─────────────────────────────────────────┐
│ 📖  Chapter 120          The Final →   │
└─────────────────────────────────────────┘
```

---

# 9. `ListTile` + `on_click`

Rất quan trọng.

```python
def open_chapter(e):
    print("Open chapter")


ft.ListTile(
    title=ft.Text("Chapter 1"),
    on_click=open_chapter,
)
```

Flow:

```text
User click
    ↓
on_click
    ↓
handler
```

---

# 10. Dynamic ListTile

Với app truyện:

```python
chapters = [
    {
        "id": 1,
        "title": "The Beginning",
    },
    {
        "id": 2,
        "title": "The Journey",
    },
]
```

Tạo item:

```python
def create_chapter_item(chapter):

    def handle_click(e):
        print(
            f"Open chapter {chapter['id']}"
        )

    return ft.ListTile(
        leading=ft.Icon(
            ft.Icons.MENU_BOOK
        ),
        title=ft.Text(
            f"Chapter {chapter['id']}"
        ),
        subtitle=ft.Text(
            chapter["title"]
        ),
        on_click=handle_click,
    )
```

Sau đó:

```python
for chapter in chapters:
    list_view.controls.append(
        create_chapter_item(chapter)
    )
```

---

# 11. `ListTile` rất hợp với `ListView`

Pattern:

```text
ListView
│
├── ListTile
├── ListTile
├── ListTile
├── ListTile
└── ...
```

Ví dụ:

```python
list_view = ft.ListView(
    expand=True,
    controls=[
        ft.ListTile(
            title=ft.Text("Chapter 1"),
        ),
        ft.ListTile(
            title=ft.Text("Chapter 2"),
        ),
        ft.ListTile(
            title=ft.Text("Chapter 3"),
        ),
    ],
)
```

Đây là một trong những pattern Flet bạn sẽ dùng nhiều nhất.

---

# 12. `ListTile` không phải Card

Đây là distinction quan trọng.

`ListTile`:

```text
→ một item / một dòng
```

`Card`:

```text
→ một surface / grouping
```

Ví dụ:

```text
Card
┌────────────────────────────┐
│ ListTile                   │
│ 📖 Naruto          →       │
└────────────────────────────┘
```

---

# 13. `Card` là gì?

`Card` dùng để tạo một bề mặt nổi bật cho một nhóm nội dung.

Concept:

```text
┌─────────────────────────────┐
│                             │
│       Content               │
│                             │
└─────────────────────────────┘
```

Thường dùng cho:

* Book
* Product
* User
* Dashboard statistic
* Notification
* Crawl job

---

# 14. Card cơ bản

```python
ft.Card(
    content=ft.Text("Hello"),
)
```

Concept:

```text
┌──────────────┐
│ Hello        │
└──────────────┘
```

---

# 15. Card + Container

Một pattern rất phổ biến:

```python
ft.Card(
    content=ft.Container(
        padding=20,
        content=ft.Text("Hello"),
    )
)
```

Tree:

```text
Card
└── Container
    └── Text
```

Tại sao?

`Card` chịu trách nhiệm:

```text
surface / elevation
```

`Container` chịu trách nhiệm:

```text
padding / margin / size / decoration
```

---

# 16. Card + ListTile

Đây là pattern cực kỳ hữu ích:

```python
ft.Card(
    content=ft.ListTile(
        leading=ft.Icon(
            ft.Icons.MENU_BOOK
        ),
        title=ft.Text("Naruto"),
        subtitle=ft.Text(
            "1200 chapters"
        ),
    )
)
```

UI:

```text
┌──────────────────────────────────┐
│ 📖 Naruto                        │
│    1200 chapters                 │
└──────────────────────────────────┘
```

---

# 17. Card trong `ListView`

Ví dụ:

```text
ListView
│
├── Card
├── Card
├── Card
└── Card
```

Code:

```python
list_view = ft.ListView(
    expand=True,
)

for i in range(10):
    list_view.controls.append(
        ft.Card(
            content=ft.ListTile(
                title=ft.Text(
                    f"Book {i + 1}"
                )
            )
        )
    )
```

---

# 18. Card cho Book

Một Book Card có thể:

```text
┌──────────────────────────────┐
│                              │
│          COVER               │
│                              │
├──────────────────────────────┤
│ Naruto                       │
│ Masashi Kishimoto            │
│ 1200 chapters                │
└──────────────────────────────┘
```

Tree:

```text
Card
│
└── Column
    │
    ├── Image
    └── ListTile
```

Ví dụ:

```python
ft.Card(
    content=ft.Column(
        controls=[
            ft.Image(
                src="https://example.com/cover.jpg",
                height=200,
            ),
            ft.ListTile(
                title=ft.Text("Naruto"),
                subtitle=ft.Text(
                    "1200 chapters"
                ),
            ),
        ]
    )
)
```

---

# 19. Card + click

Bạn có thể cho item phản hồi click thông qua control bên trong hoặc thiết kế tương tác phù hợp.

Ví dụ:

```python
ft.Card(
    content=ft.ListTile(
        title=ft.Text("Naruto"),
        on_click=open_book,
    )
)
```

Flow:

```text
Card
 ↓
ListTile
 ↓
on_click
 ↓
open_book()
```

---

# 20. Card trong GridView

Đây là nơi `Card` cực kỳ phù hợp.

Ở Buổi 16 bạn học:

```text
GridView
```

Hôm nay kết hợp:

```text
GridView
   ↓
Card
```

Ví dụ:

```text
┌────────┐ ┌────────┐ ┌────────┐
│ Book A │ │ Book B │ │ Book C │
│        │ │        │ │        │
└────────┘ └────────┘ └────────┘
```

Code:

```python
grid = ft.GridView(
    expand=True,
    runs_count=4,
    spacing=10,
)

for i in range(20):
    grid.controls.append(
        ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Text(
                    f"Book {i + 1}"
                ),
            )
        )
    )
```

---

# 21. Card cho Dashboard

Ví dụ:

```text
┌──────────────┐
│ Downloads    │
│              │
│ 1,250        │
└──────────────┘
```

Một dashboard thường có:

```text
GridView
│
├── Card → Downloads
├── Card → Completed
├── Card → Failed
└── Card → Running
```

---

# 22. `ExpansionTile` là gì?

`ExpansionTile` là một item có thể:

```text
collapsed
```

hoặc:

```text
expanded
```

Ví dụ:

```text
▼ Naruto
   Chapter 1
   Chapter 2
   Chapter 3
```

Thu gọn:

```text
▶ Naruto
```

---

# 23. ExpansionTile cơ bản

Concept:

```python
ft.ExpansionTile(
    title=ft.Text("Naruto"),
    controls=[
        ft.Text("Chapter 1"),
        ft.Text("Chapter 2"),
        ft.Text("Chapter 3"),
    ],
)
```

Mental model:

```text
ExpansionTile
│
├── title
└── controls
    ├── item
    ├── item
    └── item
```

---

# 24. Expanded vs collapsed

Collapsed:

```text
▶ Naruto
```

Expanded:

```text
▼ Naruto
   Chapter 1
   Chapter 2
   Chapter 3
```

Điểm hay:

> `ExpansionTile` quản lý trạng thái mở/đóng của chính nó.

---

# 25. ExpansionTile + ListTile concept

`ExpansionTile` có tư duy rất gần `ListTile`:

```text
ListTile
→ một dòng

ExpansionTile
→ một dòng + children
```

Ví dụ:

```text
ListView
│
├── ExpansionTile
│   ├── Chapter 1
│   ├── Chapter 2
│   └── Chapter 3
│
├── ExpansionTile
│   ├── Chapter 4
│   └── Chapter 5
│
└── ...
```

---

# 26. Use case: Category

Ví dụ:

```text
▶ Programming
▶ Database
▶ Networking
```

Mở:

```text
▼ Programming
    Python
    Rust
    Go
```

Rất phù hợp với:

* category
* folder
* menu
* settings
* FAQ

---

# 27. Use case cực kỳ phù hợp với app truyện

Bạn có thể nhóm chapter theo volume:

```text
▼ Volume 1
    Chapter 1
    Chapter 2
    Chapter 3

▶ Volume 2

▶ Volume 3
```

Tree:

```text
ListView
│
├── ExpansionTile
│   ├── Chapter 1
│   ├── Chapter 2
│   └── Chapter 3
│
├── ExpansionTile
│   ├── Chapter 4
│   └── Chapter 5
│
└── ...
```

---

# 28. ExpansionTile + ListTile

Đây là pattern cực kỳ đẹp:

```python
ft.ExpansionTile(
    title=ft.Text("Volume 1"),
    leading=ft.Icon(
        ft.Icons.FOLDER
    ),
    controls=[
        ft.ListTile(
            title=ft.Text("Chapter 1"),
        ),
        ft.ListTile(
            title=ft.Text("Chapter 2"),
        ),
        ft.ListTile(
            title=ft.Text("Chapter 3"),
        ),
    ],
)
```

UI:

```text
▼ 📁 Volume 1
    Chapter 1
    Chapter 2
    Chapter 3
```

---

# 29. ExpansionTile + ListView

Toàn bộ volume:

```python
list_view = ft.ListView(
    expand=True,
    controls=[
        ft.ExpansionTile(
            title=ft.Text("Volume 1"),
            controls=[
                ft.ListTile(
                    title=ft.Text("Chapter 1"),
                ),
                ft.ListTile(
                    title=ft.Text("Chapter 2"),
                ),
            ],
        ),
    ],
)
```

Đây là một pattern thực tế.

---

# 30. ExpansionTile cho Settings

Ví dụ:

```text
▼ Download Settings
    Download images
    Concurrent workers
    Retry count

▶ Network Settings

▶ Storage Settings
```

Cấu trúc:

```text
ListView
│
├── ExpansionTile
│
├── ExpansionTile
│
└── ExpansionTile
```

---

# 31. ExpansionTile cho crawler

Đây còn là một use case rất hay cho project của bạn.

```text
▼ Worker #1
    Status: Running
    Queue: 15
    Completed: 120
    Failed: 2

▶ Worker #2

▶ Worker #3
```

Tree:

```text
ListView
│
├── ExpansionTile → Worker 1
├── ExpansionTile → Worker 2
└── ExpansionTile → Worker 3
```

---

# 32. Card + ExpansionTile

Có thể kết hợp:

```text
Card
└── ExpansionTile
```

Ví dụ:

```python
ft.Card(
    content=ft.ExpansionTile(
        title=ft.Text("Worker #1"),
        controls=[
            ft.Text("Status: Running"),
            ft.Text("Queue: 15"),
        ],
    )
)
```

UI:

```text
┌──────────────────────────────┐
│ ▼ Worker #1                  │
│   Status: Running            │
│   Queue: 15                  │
└──────────────────────────────┘
```

---

# 33. Khi nào dùng `Card`?

Hãy nghĩ:

> "Tôi muốn tách một nhóm thông tin thành một visual surface."

Ví dụ:

```text
Book
Product
Dashboard statistic
User profile
Notification
Job
```

---

# 34. Khi nào dùng `ListTile`?

Hãy nghĩ:

> "Tôi cần một dòng item chuẩn."

Ví dụ:

```text
Chapter
User
Setting
Menu
Notification
File
```

---

# 35. Khi nào dùng `ExpansionTile`?

Hãy nghĩ:

> "Tôi có một item nhưng bên trong còn nội dung có thể mở rộng."

Ví dụ:

```text
Folder
Category
FAQ
Volume
Worker
Settings group
```

---

# 36. Ba control kết hợp

Đây là pattern bạn nên ghi nhớ:

```text
Card
└── ExpansionTile
    ├── ListTile
    ├── ListTile
    └── ListTile
```

Hoặc:

```text
ListView
└── Card
    └── ListTile
```

Hoặc:

```text
GridView
└── Card
    └── Column
```

---

# 37. Book Library hoàn chỉnh

Hãy tưởng tượng:

```text
Library
│
└── GridView
    │
    ├── Card
    │   └── Book
    │
    ├── Card
    │   └── Book
    │
    └── Card
        └── Book
```

Click Book:

```text
Book Detail
│
└── Tabs
    │
    ├── Info
    │
    └── Chapters
        │
        └── ListView
            │
            └── ExpansionTile
                │
                ├── Chapter
                ├── Chapter
                └── Chapter
```

Bạn đang bắt đầu xây được UI tree khá phức tạp.

---

# 38. So sánh 3 control

| Control         | Mục đích            | Ví dụ   |
| --------------- | ------------------- | ------- |
| `Card`          | Surface/group       | Book    |
| `ListTile`      | Một dòng            | Chapter |
| `ExpansionTile` | Dòng có thể mở rộng | Volume  |

Mental model:

```text
Card
→ "khung"

ListTile
→ "dòng"

ExpansionTile
→ "dòng + children"
```

---

# 39. Dynamic `ExpansionTile`

Giả sử database trả về:

```python
volumes = [
    {
        "id": 1,
        "title": "Volume 1",
        "chapters": [
            {"id": 1, "title": "Beginning"},
            {"id": 2, "title": "Journey"},
        ],
    },
    {
        "id": 2,
        "title": "Volume 2",
        "chapters": [
            {"id": 3, "title": "Battle"},
        ],
    },
]
```

Render:

```python
def create_volume(volume):

    chapter_controls = []

    for chapter in volume["chapters"]:

        chapter_controls.append(
            ft.ListTile(
                title=ft.Text(
                    f"Chapter {chapter['id']}"
                ),
                subtitle=ft.Text(
                    chapter["title"]
                ),
            )
        )

    return ft.ExpansionTile(
        title=ft.Text(
            volume["title"]
        ),
        controls=chapter_controls,
    )
```

Sau đó:

```python
for volume in volumes:
    list_view.controls.append(
        create_volume(volume)
    )
```

---

# 40. Đây chính là Data → UI

Kiến trúc:

```text
Database
   ↓
Repository
   ↓
Volume / Chapter models
   ↓
ViewModel / State
   ↓
ExpansionTile
   ↓
ListTile
```

Bạn sẽ gặp pattern này rất nhiều khi xây app thực tế.

---

# 41. `ListTile` với trạng thái

Chapter có:

```python
{
    "id": 120,
    "is_read": True,
    "downloaded": True,
}
```

Ta có thể biểu diễn:

```text
✓ Chapter 120                    ✓
```

hoặc:

```text
○ Chapter 121                    ↓
```

Ví dụ concept:

```python
ft.ListTile(
    leading=ft.Icon(
        ft.Icons.CHECK_CIRCLE
    ),
    title=ft.Text("Chapter 120"),
    trailing=ft.Icon(
        ft.Icons.DOWNLOAD_DONE
    ),
)
```

---

# 42. Download manager

Một item download:

```text
┌─────────────────────────────────────┐
│ Naruto Chapter 120                  │
│ ████████████░░░░ 75%       Pause   │
└─────────────────────────────────────┘
```

Có thể dùng:

```text
Card
└── Column
    ├── ListTile
    └── ProgressBar
```

Mental model:

```text
Card
│
└── Column
    ├── ListTile
    └── Progress
```

---

# 43. Worker dashboard

Một worker:

```text
┌─────────────────────────────────────┐
│ ▼ Worker #1                         │
│   Status: Running                   │
│   Queue: 12                         │
│   Completed: 152                    │
│   Failed: 3                         │
│                                     │
│   [Pause] [Resume] [Stop]           │
└─────────────────────────────────────┘
```

Tree:

```text
Card
└── ExpansionTile
    └── Column
        ├── Text
        ├── Text
        ├── Text
        └── Row
            ├── Button
            ├── Button
            └── Button
```

Đây là UI rất sát với hệ thống crawl worker của bạn.

---

# 44. Bài tập 1 — Book List

Tạo:

```text
ListView
│
├── Card
│   └── ListTile
│
├── Card
│   └── ListTile
│
└── ...
```

Mỗi book:

```text
Icon
Title
Author
```

Click book:

```text
Open book: <id>
```

---

# 45. Bài tập 2 — Volume / Chapter

Tạo:

```text
▼ Volume 1
    Chapter 1
    Chapter 2
    Chapter 3

▶ Volume 2

▶ Volume 3
```

Yêu cầu:

* `ListView`
* `ExpansionTile`
* `ListTile`
* click chapter
* mỗi volume có dữ liệu riêng

---

# 46. Bài tập 3 — Worker Dashboard

Tạo:

```text
┌──────────────────────────────┐
│ ▼ Worker #1                  │
│ Status: Running              │
│ Queue: 20                    │
│ Completed: 100               │
│ Failed: 2                    │
│ [Pause] [Stop]               │
└──────────────────────────────┘
```

Có 5 workers.

Dùng:

```text
ListView
 ↓
Card
 ↓
ExpansionTile
```

---

# 47. Bài tập 4 — Settings

Tạo:

```text
▼ General
    Auto start
    Notifications

▶ Download

▶ Network

▶ Storage
```

Mỗi setting dùng `ListTile`.

---

# 48. Bài tập 5 — Dashboard

Tạo:

```text
Dashboard

┌────────┐ ┌────────┐
│ Jobs   │ │ Done   │
│ 120    │ │ 100    │
└────────┘ └────────┘

Recent Jobs

┌─────────────────────────────┐
│ Job #120        Completed   │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Job #119        Running     │
└─────────────────────────────┘
```

Sử dụng:

```text
GridView
    ↓
Card

ListView
    ↓
Card + ListTile
```

---

# 49. Mini Project — Book Explorer

Hôm nay tôi khuyên bạn làm một mini project nhỏ:

```text
Book Explorer
```

UI:

```text
┌─────────────────────────────────────────┐
│ Book Explorer                           │
├─────────────────────────────────────────┤
│                                         │
│ ┌────────┐ ┌────────┐ ┌────────┐       │
│ │ Naruto │ │ One    │ │ Bleach │       │
│ │        │ │ Piece  │ │        │       │
│ └────────┘ └────────┘ └────────┘       │
│                                         │
├─────────────────────────────────────────┤
│ Volumes                                 │
│                                         │
│ ▼ Volume 1                              │
│    Chapter 1                            │
│    Chapter 2                            │
│    Chapter 3                            │
│                                         │
│ ▶ Volume 2                              │
│ ▶ Volume 3                              │
└─────────────────────────────────────────┘
```

Kiến trúc:

```text
Page
│
└── Column
    │
    ├── Text
    │
    ├── GridView
    │   ├── Card
    │   ├── Card
    │   └── Card
    │
    └── ListView
        │
        ├── ExpansionTile
        │   ├── ListTile
        │   ├── ListTile
        │   └── ListTile
        │
        ├── ExpansionTile
        └── ExpansionTile
```

Đây là bài tập tổng hợp rất tốt từ **Buổi 11 → 19**.

---

# 50. Một nguyên tắc thiết kế quan trọng

Đừng nghĩ:

```text
"Control nào làm được UI này?"
```

Hãy nghĩ:

```text
"UI này gồm những semantic component nào?"
```

Ví dụ:

```text
Book
```

không phải chỉ là:

```text
Container
```

mà có thể là:

```text
Card
└── Column
    ├── Image
    └── ListTile
```

Còn:

```text
Volume
```

có thể là:

```text
ExpansionTile
└── ListTile[]
```

Đây là tư duy **composition**.

---

# 51. Kết nối với những buổi trước

Bạn đã học:

```text
11 Row
12 Column
13 Container
14 Stack
15 ResponsiveRow
16 GridView
17 ListView
18 Tabs
19 Card / ExpansionTile / ListTile
```

Bây giờ bạn có thể xây:

```text
BookDetail
│
├── Header
│   └── Row
│
├── Cover
│   └── Stack
│
└── Tabs
    │
    ├── Info
    │   └── Column
    │
    ├── Chapters
    │   └── ListView
    │       └── ExpansionTile
    │           └── ListTile
    │
    └── Related
        └── GridView
            └── Card
```

Đây đã là một **UI tree có cấu trúc khá hoàn chỉnh**.

---

# 52. Roadmap

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
19. Card, ExpansionTile, ListTile    ✅ ← hôm nay
20. Layout constraints & sizing
21. Alignment
22. Spacing / padding / margin
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

## Buổi 20 — Layout Constraints & Sizing

Buổi tiếp theo là **một trong những buổi quan trọng nhất của toàn bộ phần Layout**.

Chúng ta sẽ đi sâu vào câu hỏi:

> **Tại sao một control không chịu `width`, `height`, `expand` như mình mong muốn?**

Và học mô hình:

```text
Parent
  ↓
Constraints
  ↓
Child
  ↓
Size
  ↓
Layout
```

Sau Buổi 20, bạn sẽ hiểu sâu các vấn đề như:

```text
Container width/height
expand=True
Row / Column sizing
ListView trong Column
GridView trong Container
unbounded constraints
min/max width
alignment
responsive sizing
```

Đây là nền tảng để từ Buổi 20 trở đi bạn không còn phải "thử width=500, height=300 xem có vừa không" khi thiết kế Flet UI.
