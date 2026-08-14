# Buổi 17 — `ListView` Deep Dive

Hôm nay chúng ta học **`ListView`** — control cực kỳ quan trọng trong Flet để xây dựng các danh sách có thể scroll.

Nếu `GridView` ở Buổi 16 dùng cho:

```text
Book  Book  Book
Book  Book  Book
Book  Book  Book
```

thì `ListView` chủ yếu dùng cho:

```text
Chapter 1
Chapter 2
Chapter 3
Chapter 4
Chapter 5
...
```

Với project **app cào truyện + đọc truyện**, `ListView` sẽ xuất hiện ở rất nhiều nơi:

* danh sách chapter
* danh sách task crawl
* log worker
* danh sách notification
* danh sách source
* search result
* sidebar
* lịch sử đọc
* queue job

---

# 1. `ListView` là gì?

Mental model:

```text
ListView
│
├── Item
├── Item
├── Item
├── Item
├── Item
└── ...
       ↓
     scroll
```

Ví dụ:

```text
┌──────────────────────────────┐
│ Chapter 1                    │
├──────────────────────────────┤
│ Chapter 2                    │
├──────────────────────────────┤
│ Chapter 3                    │
├──────────────────────────────┤
│ Chapter 4                    │
├──────────────────────────────┤
│ Chapter 5                    │
├──────────────────────────────┤
│ Chapter 6                    │
└──────────────────────────────┘
                ↓
              scroll
```

---

# 2. `ListView` khác `Column` như thế nào?

Đây là câu hỏi rất quan trọng.

Bạn có thể viết:

```python
ft.Column(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Nhưng `Column` không phải control chuyên dụng cho scrolling.

Trong khi:

```python
ft.ListView(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

được thiết kế cho danh sách có thể scroll.

Mental model:

```text
Column
→ layout

ListView
→ scrollable collection
```

---

# 3. Ví dụ cơ bản

```python
import flet as ft


def main(page: ft.Page):

    list_view = ft.ListView(
        expand=True,
        spacing=10,
    )

    for i in range(30):
        list_view.controls.append(
            ft.Text(f"Item {i + 1}")
        )

    page.add(list_view)


ft.run(main)
```

Khi có nhiều item:

```text
Item 1
Item 2
Item 3
Item 4
Item 5
...
Item 30
   ↓
 scroll
```

---

# 4. `expand=True`

Đây là pattern bạn sẽ sử dụng rất thường xuyên:

```python
ft.ListView(
    expand=True,
)
```

Ví dụ:

```python
page.add(
    ft.Column(
        expand=True,
        controls=[
            ft.Text("Chapter List"),

            ft.ListView(
                expand=True,
            ),
        ],
    )
)
```

Layout:

```text
Page
│
└── Column
    │
    ├── Header
    │
    └── ListView
          ↑
      remaining space
```

---

# 5. `spacing`

```python
ft.ListView(
    spacing=10,
)
```

Có nghĩa là tạo khoảng cách giữa các item.

Không có spacing:

```text
A
B
C
D
```

Có spacing:

```text
A

B

C

D
```

---

# 6. ListView với `Container`

Thông thường bạn không nên dùng:

```python
ft.Text("Chapter 1")
```

cho UI thực tế.

Thay vào đó:

```python
ft.Container(
    padding=15,
    content=ft.Text("Chapter 1"),
)
```

Ví dụ:

```python
list_view.controls.append(
    ft.Container(
        padding=15,
        content=ft.Text("Chapter 1"),
    )
)
```

---

# 7. Tạo `ChapterItem`

Tốt hơn nữa, hãy tạo component riêng:

```python
def chapter_item(title: str):
    return ft.Container(
        padding=15,
        content=ft.Text(title),
    )
```

Sau đó:

```python
list_view = ft.ListView(
    expand=True,
)

for i in range(20):
    list_view.controls.append(
        chapter_item(f"Chapter {i + 1}")
    )
```

Mental model:

```text
ListView
│
├── ChapterItem
├── ChapterItem
├── ChapterItem
└── ...
```

Đây chính là tư duy component hóa.

---

# 8. Chapter item thực tế hơn

```python
def chapter_item(
    chapter_number: int,
    title: str,
):
    return ft.Container(
        padding=15,
        content=ft.Row(
            controls=[
                ft.Text(
                    f"Chapter {chapter_number}",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(title),
            ],
        ),
    )
```

Kết quả:

```text
Chapter 1    The Beginning
Chapter 2    The Journey
Chapter 3    The Battle
Chapter 4    New World
```

---

# 9. `ListTile`

Ở Buổi 19 chúng ta sẽ học `ListTile` sâu hơn.

Nhưng bạn có thể hình dung:

```text
┌────────────────────────────────────┐
│ [icon] Chapter 1          [arrow] │
└────────────────────────────────────┘
```

`ListTile` rất phù hợp với `ListView`.

---

# 10. Pattern cực kỳ phổ biến

```python
ft.ListView(
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

Mental model:

```text
ListView
│
├── ListTile
├── ListTile
└── ListTile
```

---

# 11. ListView + `on_click`

Chapter list gần như chắc chắn cần click.

Ví dụ:

```python
def open_chapter(e):
    print("Chapter clicked")


item = ft.ListTile(
    title=ft.Text("Chapter 1"),
    on_click=open_chapter,
)
```

Khi click:

```text
Chapter 1
    ↓
open_chapter()
```

---

# 12. Lấy chapter được click

Ví dụ:

```python
def open_chapter(chapter_id: int):
    print(f"Open chapter: {chapter_id}")
```

Tạo handler:

```python
def handle_click(e):
    open_chapter(123)
```

Hoặc dùng closure:

```python
def make_handler(chapter_id: int):

    def handler(e):
        print(f"Open chapter: {chapter_id}")

    return handler
```

Sau đó:

```python
ft.ListTile(
    title=ft.Text("Chapter 123"),
    on_click=make_handler(123),
)
```

Đây là pattern rất quan trọng khi tạo UI từ data.

---

# 13. `ListView` + data

Giả sử:

```python
chapters = [
    {"id": 1, "title": "Beginning"},
    {"id": 2, "title": "Journey"},
    {"id": 3, "title": "Battle"},
]
```

Ta có thể:

```python
list_view = ft.ListView(
    expand=True,
)

for chapter in chapters:

    list_view.controls.append(
        ft.ListTile(
            title=ft.Text(
                f"Chapter {chapter['id']}: "
                f"{chapter['title']}"
            )
        )
    )
```

Mental model:

```text
Database
   ↓
chapters
   ↓
ListView
   ↓
ListTile
```

---

# 14. Đây là kiến trúc quan trọng

Trong app của bạn:

```text
SQLite
   ↓
Repository
   ↓
Service / Use Case
   ↓
UI State
   ↓
ListView
```

Không nên:

```text
ListView
   ↓
SQLite
```

UI không nên trực tiếp truy vấn database.

---

# 15. ListView cho chapter

Một màn hình đọc truyện:

```text
┌──────────────────────────────────┐
│ One Piece                        │
├──────────────────────────────────┤
│ Chapter 1001                     │
│ Chapter 1002                     │
│ Chapter 1003                     │
│ Chapter 1004                     │
│ Chapter 1005                     │
│ ...                              │
└──────────────────────────────────┘
```

Tree:

```text
Column
│
├── BookHeader
│
└── ListView
    │
    ├── ChapterItem
    ├── ChapterItem
    ├── ChapterItem
    └── ...
```

---

# 16. `horizontal=True`

`ListView` không nhất thiết chỉ scroll dọc.

Có thể tạo horizontal list:

```python
ft.ListView(
    horizontal=True,
)
```

Mental model:

```text
A → B → C → D → E → F → ...
```

Ví dụ:

```text
Recommended:

┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ──→
│ Book │ │ Book │ │ Book │ │ Book │
└──────┘ └──────┘ └──────┘ └──────┘
```

---

# 17. `ListView` vs `GridView`

Đây là phần phải nhớ.

### ListView

```text
A
B
C
D
E
```

### GridView

```text
A B C
D E F
G H I
```

Bảng:

| Control    | Use case          |
| ---------- | ----------------- |
| `ListView` | danh sách         |
| `GridView` | lưới              |
| `Column`   | vertical layout   |
| `Row`      | horizontal layout |

---

# 18. ListView vs Column

```text
Column
→ bố trí các control theo chiều dọc
```

```text
ListView
→ bố trí các item theo chiều dọc + scrolling
```

Ví dụ:

### Header cố định + list scroll

```text
Column
│
├── Header
│
└── ListView
      ↓
    scroll
```

Đây là pattern cực kỳ quan trọng.

---

# 19. Search + ListView

Ví dụ:

```text
┌──────────────────────────────┐
│ Search [ Naruto        ]     │
├──────────────────────────────┤
│ Naruto Chapter 1             │
│ Naruto Chapter 2             │
│ Naruto Chapter 3             │
│ Naruto Chapter 4             │
│ ...                          │
└──────────────────────────────┘
```

Tree:

```text
Column
│
├── SearchField
│
└── ListView
```

---

# 20. Search filtering

Giả sử:

```python
chapters = [
    "Chapter 1",
    "Chapter 2",
    "Special Chapter",
    "Chapter 3",
]
```

User nhập:

```text
special
```

State:

```text
search_query = "special"
```

Filter:

```python
filtered = [
    chapter
    for chapter in chapters
    if "special" in chapter.lower()
]
```

Sau đó render lại ListView.

---

# 21. Đây là lúc state bắt đầu quan trọng

Kiến trúc:

```text
User types
     ↓
SearchField
     ↓
state.search_query
     ↓
filter()
     ↓
ListView
     ↓
page.update()
```

Bạn đã học:

```text
Buổi 8
State

Buổi 9
page.update()

Buổi 17
ListView
```

Ba kiến thức này bắt đầu kết hợp với nhau.

---

# 22. Xóa item

Ví dụ:

```python
def delete_item(index: int):

    list_view.controls.pop(index)

    page.update()
```

Mental model:

```text
ListView
│
├── A
├── B ← delete
├── C
└── D

        ↓

ListView
│
├── A
├── C
└── D
```

---

# 23. Thêm item

```python
def add_item():

    list_view.controls.append(
        ft.Text("New Item")
    )

    page.update()
```

Mental model:

```text
state
 ↓
controls
 ↓
page.update()
```

---

# 24. Xóa toàn bộ

```python
list_view.controls.clear()

page.update()
```

Sau đó:

```text
ListView
└── empty
```

Đây sẽ rất hữu ích cho:

* refresh
* search
* filter
* reload database

---

# 25. Render lại ListView

Một pattern đơn giản:

```python
def render_chapters():

    list_view.controls.clear()

    for chapter in chapters:
        list_view.controls.append(
            create_chapter_item(chapter)
        )

    page.update()
```

Mental model:

```text
Data
 ↓
render()
 ↓
ListView
 ↓
page.update()
```

Đây là một bước đầu tiên hướng tới UI state architecture.

---

# 26. Empty state

Không có chapter:

```text
┌─────────────────────────────┐
│                             │
│       No chapters           │
│                             │
└─────────────────────────────┘
```

Không nên để:

```text
ListView
└── nothing
```

mà nên có:

```text
if chapters:
    ListView
else:
    EmptyState
```

---

# 27. Loading state

Khi đang lấy chapter từ database/network:

```text
Loading
   ↓
ProgressRing
```

Sau khi xong:

```text
Success
   ↓
ListView
```

Mental model:

```text
State
│
├── loading
│
├── success
│
├── empty
│
└── error
```

---

# 28. Error state

Ví dụ crawler source bị lỗi:

```text
┌─────────────────────────────┐
│ Failed to load chapters     │
│                             │
│         [ Retry ]           │
└─────────────────────────────┘
```

Kiến trúc:

```text
load_chapters()
      ↓
   result
      ↓
┌─────┼──────┐
│     │      │
OK   empty  error
│     │      │
List  Empty Error
```

---

# 29. ListView + Divider

Danh sách chapter thường cần divider.

Concept:

```text
Chapter 1
────────────────
Chapter 2
────────────────
Chapter 3
────────────────
```

Bạn có thể dùng các control/thuộc tính phù hợp của item hoặc `Divider`.

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Chapter 1"),
        ft.Divider(),
    ]
)
```

---

# 30. Chapter item tốt hơn

Ta có thể tạo:

```python
def chapter_item(
    chapter_number: int,
    title: str,
    is_read: bool,
):
    return ft.ListTile(
        title=ft.Text(
            f"Chapter {chapter_number}"
        ),
        subtitle=ft.Text(title),
    )
```

Sau này thêm:

```text
[✓] Chapter 120
    The Final Battle
```

---

# 31. Trạng thái `read`

Ví dụ:

```python
is_read = True
```

UI:

```text
✓ Chapter 120
```

Nếu chưa đọc:

```text
○ Chapter 121
```

State:

```text
Chapter
│
├── id
├── title
└── is_read
```

UI:

```text
ChapterItem
│
├── icon
├── title
└── subtitle
```

---

# 32. Chapter item với `ListTile`

Ví dụ:

```python
def chapter_item(
    chapter_id: int,
    title: str,
    is_read: bool,
):
    return ft.ListTile(
        leading=ft.Icon(
            ft.Icons.CHECK_CIRCLE
            if is_read
            else ft.Icons.CIRCLE_OUTLINED
        ),
        title=ft.Text(
            f"Chapter {chapter_id}"
        ),
        subtitle=ft.Text(title),
    )
```

Đây là một component thực tế.

---

# 33. Context menu

Sau này chapter có thể có:

```text
Right click
   ↓
┌──────────────────┐
│ Mark as read     │
│ Download         │
│ Re-download      │
│ Delete           │
└──────────────────┘
```

`ListView` là nền tảng để xây các UI như vậy.

---

# 34. ListView cho crawl worker

Project crawler của bạn còn có một use case cực kỳ phù hợp:

```text
Worker Dashboard
```

Ví dụ:

```text
┌──────────────────────────────────────┐
│ Crawl Queue                          │
├──────────────────────────────────────┤
│ ✓ Book A - completed                 │
│ ⟳ Book B - downloading               │
│ ⏳ Book C - waiting                  │
│ ✗ Book D - failed                    │
└──────────────────────────────────────┘
```

Đây chính là:

```text
ListView
    ↓
JobItem
```

---

# 35. Log viewer

Một use case khác:

```text
┌──────────────────────────────────────┐
│ Logs                                 │
├──────────────────────────────────────┤
│ 12:01 INFO  Start crawl              │
│ 12:02 INFO  Download chapter         │
│ 12:03 INFO  Save database            │
│ 12:04 ERROR Timeout                  │
│ ...                                  │
└──────────────────────────────────────┘
```

`ListView` rất phù hợp.

Thậm chí có thể:

```python
list_view.auto_scroll = True
```

để danh sách log tự cuộn xuống cuối khi có log mới.

---

# 36. Auto scroll

Đây là một feature cực kỳ hữu ích cho:

* logs
* chat
* terminal output
* crawler monitor

Concept:

```python
list_view.auto_scroll = True
```

Khi append:

```python
list_view.controls.append(
    ft.Text("New log")
)

page.update()
```

List sẽ tự cuộn về cuối tùy cấu hình/version behavior của Flet.

---

# 37. Chat UI

Một chat app thường:

```text
Column
│
├── ListView
│   ├── Message
│   ├── Message
│   ├── Message
│   └── ...
│
└── Row
    ├── TextField
    └── Button
```

Mental model:

```text
┌─────────────────────────────┐
│ ListView                    │
│                             │
│ User: Hello                 │
│ AI: Hello!                  │
│ User: How are you?          │
│ AI: ...                     │
│                             │
├─────────────────────────────┤
│ [ Message        ] [Send]   │
└─────────────────────────────┘
```

---

# 38. `ListView` + async

Sau này khi kết hợp với async:

```text
async load_chapters()
        ↓
database / network
        ↓
chapters
        ↓
ListView
        ↓
page.update()
```

Hoặc crawler:

```text
async worker
      ↓
queue
      ↓
event
      ↓
ListView
      ↓
UI update
```

Đây sẽ kết nối rất mạnh với những gì bạn đã học về `asyncio`.

---

# 39. Không nên thao tác database trong UI event

Sai:

```python
def on_click(e):
    chapters = database.get_chapters()
```

Tốt hơn:

```text
UI Event
   ↓
Use Case
   ↓
Repository
   ↓
Database
```

Sau đó:

```text
result
 ↓
state
 ↓
ListView
```

Đây chính là Clean Architecture/DDD mà bạn đang học.

---

# 40. `ListView` + Repository

Ví dụ:

```python
class ChapterRepository:

    def get_by_book_id(self, book_id):
        ...
```

UI:

```python
def load_chapters(book_id):

    chapters = repository.get_by_book_id(book_id)

    render_chapters(chapters)
```

Tree:

```text
ChapterPage
│
├── Header
│
└── ListView
```

---

# 41. Pagination

Giống GridView, không nên load:

```text
100,000 chapters
```

một lần.

Có thể:

```text
page 1
100 chapters

page 2
100 chapters

page 3
100 chapters
```

Architecture:

```text
Repository
    ↓
LIMIT/OFFSET
    ↓
ListView
```

Ví dụ SQL:

```sql
SELECT *
FROM chapters
WHERE book_id = ?
ORDER BY chapter_number
LIMIT ?
OFFSET ?;
```

---

# 42. Infinite loading

Concept:

```text
Chapter 1
Chapter 2
...
Chapter 100

       ↓ scroll

load more

       ↓

Chapter 101
...
Chapter 200
```

Kiến trúc:

```text
ListView
   ↓
scroll position
   ↓
near bottom?
   ↓
load more
   ↓
append controls
```

Đây sẽ là một bài tập nâng cao rất tốt sau khi học event + async.

---

# 43. `ListView` trong sidebar

Ví dụ:

```text
┌──────────────────┬───────────────────────┐
│ Home             │                       │
│ Library          │                       │
│ Downloads        │                       │
│ History          │                       │
│ Settings         │                       │
│                  │                       │
│                  │                       │
└──────────────────┴───────────────────────┘
```

Sidebar:

```text
Column
│
├── Logo
│
└── ListView
    ├── NavigationItem
    ├── NavigationItem
    ├── NavigationItem
    └── ...
```

---

# 44. ListView trong Dashboard

Ví dụ:

```text
Dashboard
│
├── Stats
│
├── GridView
│
└── Recent Tasks
    │
    └── ListView
```

Bạn sẽ kết hợp:

```text
GridView
+
ListView
```

rất thường xuyên.

---

# 45. GridView + ListView

Ví dụ màn hình Library:

```text
Column
│
├── Search
│
├── GridView
│   ├── BookCard
│   ├── BookCard
│   └── ...
│
└── ...
```

Màn hình Book Detail:

```text
Column
│
├── BookHeader
│
├── BookInfo
│
└── ListView
    ├── Chapter
    ├── Chapter
    └── ...
```

Mental model:

```text
Library
→ GridView

Book Detail
→ ListView
```

---

# 46. `ListView` và UI Tree

Hãy nhớ:

```text
Page
│
└── Column
    │
    ├── Header
    │
    └── ListView
        │
        ├── Container
        │   └── Row
        │
        ├── Container
        │   └── Row
        │
        └── Container
            └── Row
```

`ListView` vẫn là một node trong UI tree.

---

# 47. Dynamic controls

Một điều rất quan trọng:

```python
list_view.controls.append(...)
```

không có nghĩa database tự động cập nhật UI.

Bạn phải hiểu chu trình:

```text
Data changed
     ↓
Controls changed
     ↓
page.update()
```

Ví dụ:

```python
list_view.controls.append(
    ft.Text("New Chapter")
)

page.update()
```

---

# 48. Xây một Chapter List hoàn chỉnh

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    page.title = "Chapter List"

    list_view = ft.ListView(
        expand=True,
        spacing=5,
    )

    chapters = [
        "The Beginning",
        "The Journey",
        "The Battle",
        "The New World",
        "The Final Battle",
    ]

    for index, title in enumerate(chapters, start=1):

        list_view.controls.append(
            ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.MENU_BOOK
                ),
                title=ft.Text(
                    f"Chapter {index}"
                ),
                subtitle=ft.Text(title),
            )
        )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "One Piece",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                list_view,
            ],
        )
    )


ft.run(main)
```

Kiến trúc:

```text
Page
│
└── Column
    │
    ├── Book title
    │
    └── ListView
        │
        ├── ListTile
        ├── ListTile
        ├── ListTile
        └── ...
```

---

# 49. Phiên bản có click

```python
def open_chapter(chapter_id: int):

    print(f"Open chapter {chapter_id}")
```

Tạo item:

```python
def create_chapter_item(
    chapter_id: int,
    title: str,
):

    def handle_click(e):
        open_chapter(chapter_id)

    return ft.ListTile(
        leading=ft.Icon(
            ft.Icons.MENU_BOOK
        ),
        title=ft.Text(
            f"Chapter {chapter_id}"
        ),
        subtitle=ft.Text(title),
        on_click=handle_click,
    )
```

Sau đó:

```python
for chapter in chapters:

    list_view.controls.append(
        create_chapter_item(
            chapter["id"],
            chapter["title"],
        )
    )
```

Đây là một pattern bạn nên luyện thật kỹ.

---

# 50. Một lỗi Python rất hay gặp

Không nên:

```python
for chapter in chapters:
    item.on_click = lambda e: open_chapter(
        chapter["id"]
    )
```

Vì lambda/closure có thể gặp vấn đề **late binding**.

Tốt hơn:

```python
def create_handler(chapter_id):

    def handler(e):
        open_chapter(chapter_id)

    return handler
```

Hoặc:

```python
on_click=lambda e, cid=chapter["id"]:
    open_chapter(cid)
```

Đây là kiến thức Python rất quan trọng khi xây UI dynamic.

---

# 51. Bài tập 1 — Basic ListView

Tạo:

```text
Item 1
Item 2
...
Item 100
```

Yêu cầu:

* scroll được
* spacing = 10
* mỗi item là `Container`
* có padding

---

# 52. Bài tập 2 — Chapter List

Tạo:

```text
One Piece
│
├── Chapter 1
├── Chapter 2
├── Chapter 3
├── ...
└── Chapter 100
```

Mỗi chapter có:

```text
Icon
Chapter number
Title
```

Click vào chapter phải in:

```text
Open chapter 42
```

---

# 53. Bài tập 3 — Search

Tạo:

```text
TextField
ListView
```

User nhập:

```text
battle
```

List chỉ hiển thị chapter chứa:

```text
battle
```

Flow:

```text
TextField
    ↓
search_query
    ↓
filter chapters
    ↓
render ListView
    ↓
page.update()
```

---

# 54. Bài tập 4 — Read status

Mỗi chapter có:

```python
is_read: bool
```

UI:

```text
✓ Chapter 1
○ Chapter 2
✓ Chapter 3
○ Chapter 4
```

Click chapter:

```text
is_read = True
```

Sau đó update UI.

---

# 55. Bài tập 5 — Crawl Queue

Tạo:

```text
Queue
│
├── Book A  [waiting]
├── Book B  [running]
├── Book C  [completed]
└── Book D  [failed]
```

Dùng `ListView`.

Đây là bài tập cực kỳ phù hợp với **queue server + crawl worker** mà bạn đang xây dựng.

---

# 56. Bài tập 6 — Log Viewer

Tạo:

```text
Crawler Logs

12:00 INFO  Start crawler
12:01 INFO  Fetch book
12:02 INFO  Parse chapter
12:03 INFO  Save database
12:04 ERROR Request failed
```

Dùng:

```python
ListView(
    auto_scroll=True,
)
```

Khi thêm log mới:

```python
list_view.controls.append(...)
page.update()
```

---

# 57. Bài tập 7 — Mini Book Detail

Thiết kế:

```text
┌──────────────────────────────────────────┐
│ ← Back                                   │
├──────────────────────────────────────────┤
│                                          │
│ Cover     One Piece                      │
│           Author: Eiichiro Oda           │
│           Chapters: 1200                 │
│                                          │
├──────────────────────────────────────────┤
│ Chapters                                 │
├──────────────────────────────────────────┤
│ Chapter 1200                             │
│ Chapter 1199                             │
│ Chapter 1198                             │
│ Chapter 1197                             │
│ ...                                      │
└──────────────────────────────────────────┘
```

Kiến trúc:

```text
BookDetailPage
│
└── Column
    │
    ├── Header
    ├── BookInfo
    │
    └── ListView
        └── ChapterItem
```

---

# 58. Điều cần nhớ nhất hôm nay

Hãy ghi nhớ 4 câu:

```text
Column
→ layout dọc

ListView
→ danh sách + scroll

GridView
→ grid + scroll

ResponsiveRow
→ responsive page layout
```

Và kiến trúc:

```text
Library
    ↓
GridView

Book Detail
    ↓
ListView

Chapter
    ↓
ListTile

Book Card
    ↓
Container / Stack
```

---

# Roadmap hiện tại

```text
Giai đoạn II — Layout Deep Dive

11. Row deep dive                    ✅
12. Column deep dive                 ✅
13. Container deep dive              ✅
14. Stack                             ✅
15. ResponsiveRow                     ✅
16. GridView                           ✅
17. ListView                           ← Hôm nay
18. Tabs
19. Card, ExpansionTile, ListTile
20. Layout constraints & sizing
21. Alignment
22. Spacing / padding / margin
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

## Buổi 18 — `Tabs` Deep Dive

Buổi tiếp theo chúng ta sẽ học cách xây UI dạng:

```text
┌─────────────────────────────────────────┐
│ [Thông tin] [Chapters] [Comments]       │
├─────────────────────────────────────────┤
│                                         │
│             Tab content                 │
│                                         │
└─────────────────────────────────────────┘
```

và đặc biệt sẽ kết hợp:

```text
Tabs
 ├── Book Info
 ├── ListView → Chapters
 └── ListView → Comments
```

để bắt đầu xây **Book Detail Page** thực tế.
