# Buổi 16 — `GridView` Deep Dive

Hôm nay chúng ta học **`GridView`** — một control cực kỳ quan trọng khi xây các ứng dụng có **nhiều item dạng lưới**.

Đặc biệt với app **cào truyện + đọc truyện** của bạn, `GridView` sẽ được dùng rất nhiều cho:

* danh sách truyện
* danh sách chapter
* gallery ảnh
* danh sách nguồn truyện
* dashboard cards
* kết quả tìm kiếm
* thư viện sách/truyện

---

# 1. `GridView` là gì?

Nếu `Row`:

```text
A B C D
```

`Column`:

```text
A
B
C
D
```

thì `GridView` tạo một **lưới các item**, thường đi kèm khả năng **scroll**.

Ví dụ:

```text
┌────────┬────────┬────────┬────────┐
│ Book 1 │ Book 2 │ Book 3 │ Book 4 │
├────────┼────────┼────────┼────────┤
│ Book 5 │ Book 6 │ Book 7 │ Book 8 │
├────────┼────────┼────────┼────────┤
│ Book 9 │ Book10 │ Book11 │ Book12 │
└────────┴────────┴────────┴────────┘
                ↓
             scroll
```

Mental model:

```text
GridView
│
├── item
├── item
├── item
├── item
├── item
└── ...
```

---

# 2. Tại sao không dùng `ResponsiveRow`?

Buổi trước chúng ta đã học:

```python
ft.ResponsiveRow(...)
```

Có thể tạo:

```text
┌──────┬──────┬──────┬──────┐
│ A    │ B    │ C    │ D    │
├──────┼──────┼──────┼──────┤
│ E    │ F    │ G    │ H    │
└──────┴──────┴──────┴──────┘
```

Vậy tại sao cần `GridView`?

Vì hai control giải quyết **hai vấn đề khác nhau**.

### ResponsiveRow

Tư duy:

```text
layout / responsive page
```

### GridView

Tư duy:

```text
collection / scrollable grid
```

Đây là distinction rất quan trọng.

---

# 3. Mental model

Hãy nhớ:

```text
ResponsiveRow
    ↓
"Trang này được chia layout như thế nào?"

GridView
    ↓
"Danh sách item này được hiển thị thành grid như thế nào?"
```

Ví dụ:

```text
Dashboard
│
├── Sidebar
│
└── Main
    │
    └── GridView
        ├── Card
        ├── Card
        ├── Card
        └── ...
```

---

# 4. GridView cơ bản

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):
    grid = ft.GridView(
        expand=True,
        runs_count=3,
        spacing=10,
        run_spacing=10,
    )

    for i in range(12):
        grid.controls.append(
            ft.Container(
                bgcolor=ft.Colors.BLUE,
                content=ft.Text(f"Item {i}"),
                padding=20,
            )
        )

    page.add(grid)


ft.run(main)
```

Mental model:

```text
GridView
│
├── Item 0
├── Item 1
├── Item 2
├── Item 3
...
```

UI:

```text
┌────────┬────────┬────────┐
│ Item 0 │ Item 1 │ Item 2 │
├────────┼────────┼────────┤
│ Item 3 │ Item 4 │ Item 5 │
├────────┼────────┼────────┤
│ Item 6 │ Item 7 │ Item 8 │
├────────┼────────┼────────┤
│ Item 9 │ Item10 │ Item11 │
└────────┴────────┴────────┘
```

---

# 5. `runs_count`

Đây là thuộc tính rất quan trọng.

```python
runs_count=3
```

Có nghĩa:

> Mỗi hàng có 3 item.

Ví dụ:

```text
runs_count=2
```

```text
┌──────────┬──────────┐
│    A     │    B     │
├──────────┼──────────┤
│    C     │    D     │
├──────────┼──────────┤
│    E     │    F     │
└──────────┴──────────┘
```

---

# 6. `runs_count=4`

```python
ft.GridView(
    runs_count=4,
)
```

```text
┌────┬────┬────┬────┐
│ A  │ B  │ C  │ D  │
├────┼────┼────┼────┤
│ E  │ F  │ G  │ H  │
└────┴────┴────┴────┘
```

---

# 7. `runs_count=6`

```text
┌───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │ E │ F │
├───┼───┼───┼───┼───┼───┤
│ G │ H │ I │ J │ K │ L │
└───┴───┴───┴───┴───┴───┘
```

---

# 8. `runs_count` không phải responsive

Đây là điểm rất quan trọng.

Nếu:

```python
runs_count=4
```

thì bạn đang nói:

```text
4 item / row
```

không phải:

```text
mobile = 1
tablet = 2
desktop = 4
```

Nếu muốn layout tự thích nghi theo kích thước item, ta cần cơ chế khác.

---

# 9. `max_extent`

Một cách khác là giới hạn kích thước tối đa của mỗi item.

Mental model:

```python
ft.GridView(
    max_extent=250,
)
```

Ý nghĩa gần với:

> cố gắng tạo các cột sao cho mỗi item có kích thước tối đa khoảng 250.

Khi màn hình rộng:

```text
┌──────┬──────┬──────┬──────┐
│      │      │      │      │
└──────┴──────┴──────┴──────┘
```

Khi màn hình hẹp:

```text
┌───────────┬───────────┐
│           │           │
└───────────┴───────────┘
```

Khi rất hẹp:

```text
┌──────────────────────┐
│                      │
└──────────────────────┘
```

Đây là một cơ chế rất hữu ích cho gallery.

---

# 10. `runs_count` vs `max_extent`

Đây là một trong những kiến thức quan trọng nhất của buổi hôm nay.

| Cách         | Ý tưởng                |
| ------------ | ---------------------- |
| `runs_count` | số cột cố định         |
| `max_extent` | kích thước item tối đa |

Ví dụ:

### Fixed columns

```python
ft.GridView(
    runs_count=4,
)
```

Tư duy:

```text
4 columns
```

### Flexible columns

```python
ft.GridView(
    max_extent=250,
)
```

Tư duy:

```text
item width ≈ tối đa 250
→ số cột phụ thuộc width
```

---

# 11. Khi nào dùng `runs_count`?

Rất phù hợp khi bạn biết chính xác:

```text
3 cards / row
```

Ví dụ dashboard:

```text
┌──────┬──────┬──────┐
│ CPU  │ RAM  │ Disk │
└──────┴──────┴──────┘
```

Bạn có thể dùng:

```python
runs_count=3
```

---

# 12. Khi nào dùng `max_extent`?

Rất phù hợp với:

```text
Book Gallery
Image Gallery
Product Gallery
Photo Gallery
```

Bạn muốn:

> Mỗi card khoảng 200–250px, còn số cột để GridView tự tính.

Ví dụ:

```python
ft.GridView(
    max_extent=220,
)
```

---

# 13. `spacing`

Khoảng cách giữa các item trên cùng một hàng:

```python
spacing=10
```

Ví dụ:

```text
A ← 10px → B ← 10px → C
```

---

# 14. `run_spacing`

Khoảng cách giữa các hàng:

```python
run_spacing=20
```

Ví dụ:

```text
A B C
     
↕ 20px

D E F
```

Tư duy:

```text
spacing
→ ngang

run_spacing
→ dọc
```

---

# 15. Ví dụ đẹp hơn

```python
grid = ft.GridView(
    expand=True,
    max_extent=220,
    spacing=15,
    run_spacing=15,
)

for i in range(30):
    grid.controls.append(
        ft.Container(
            height=250,
            border_radius=12,
            bgcolor=ft.Colors.BLUE,
            alignment=ft.alignment.center,
            content=ft.Text(f"Book {i + 1}"),
        )
    )
```

Concept:

```text
┌──────────┬──────────┬──────────┐
│ Book 1   │ Book 2   │ Book 3   │
├──────────┼──────────┼──────────┤
│ Book 4   │ Book 5   │ Book 6   │
├──────────┼──────────┼──────────┤
│ ...      │ ...      │ ...      │
└──────────┴──────────┴──────────┘
              ↓
            scroll
```

---

# 16. Scroll

Đây là điểm cực kỳ quan trọng.

`GridView` được thiết kế cho nội dung có thể **scroll**.

Ví dụ:

```text
GridView
│
├── Book 1
├── Book 2
├── Book 3
├── ...
├── Book 100
├── Book 101
└── ...
        ↓
      scroll
```

Nếu bạn có:

```text
500 books
```

thì `GridView` phù hợp hơn việc tạo một layout tĩnh bằng `ResponsiveRow`.

---

# 17. `expand=True`

Một pattern rất phổ biến:

```python
grid = ft.GridView(
    expand=True,
)
```

Nó cho phép GridView sử dụng không gian còn lại của parent.

Ví dụ:

```text
Page
│
├── AppBar
│
└── GridView
      ↑
   expand=True
```

Concept:

```text
┌─────────────────────────────┐
│ AppBar                      │
├─────────────────────────────┤
│                             │
│ GridView                    │
│                             │
│                             │
│                             │
└─────────────────────────────┘
```

---

# 18. GridView trong Column

Ví dụ:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text("Books"),
            grid,
        ],
        expand=True,
    )
)
```

Thường cần đảm bảo GridView được cấp không gian hợp lý:

```python
grid = ft.GridView(
    expand=True,
)
```

Mental model:

```text
Column
│
├── Text
│
└── GridView
      ↓
   remaining space
```

---

# 19. Đây là pattern rất quan trọng

```python
ft.Column(
    expand=True,
    controls=[
        ft.Text("Books"),
        ft.GridView(
            expand=True,
        ),
    ],
)
```

Tư duy:

```text
Column
│
├── Header
│
└── GridView
    └── chiếm phần còn lại
```

Bạn sẽ dùng pattern này rất nhiều trong ứng dụng desktop.

---

# 20. GridView + Book Card

Đây là ví dụ gần với app của bạn nhất.

```python
def book_card(title):
    return ft.Container(
        border_radius=12,
        padding=10,
        content=ft.Column(
            controls=[
                ft.Text(
                    title,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Chapter 123"),
            ],
        ),
    )
```

Grid:

```python
grid = ft.GridView(
    expand=True,
    max_extent=220,
    spacing=15,
    run_spacing=15,
)

for title in [
    "One Piece",
    "Naruto",
    "Bleach",
    "Dragon Ball",
    "Demon Slayer",
]:
    grid.controls.append(
        book_card(title)
    )
```

---

# 21. Book card + Stack

Bây giờ kết hợp Buổi 14.

```text
GridView
│
├── BookCard
│   └── Stack
│       ├── Cover
│       ├── Overlay
│       └── Badge
│
├── BookCard
│   └── Stack
│
└── ...
```

Đây là kiến trúc cực kỳ tốt.

---

# 22. BookCard hoàn chỉnh

```python
def book_card(
    title: str,
    chapter: str,
    image_url: str,
):
    return ft.Container(
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Stack(
            controls=[
                ft.Image(
                    src=image_url,
                    fit=ft.BoxFit.COVER,
                    width=220,
                    height=300,
                ),

                ft.Container(
                    width=220,
                    height=300,
                    bgcolor=ft.Colors.BLACK54,
                ),

                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                title,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(chapter),
                        ],
                    ),
                    padding=15,
                ),
            ],
        ),
    )
```

Grid:

```python
grid = ft.GridView(
    expand=True,
    max_extent=220,
    spacing=15,
    run_spacing=15,
)
```

---

# 23. GridView + image gallery

Ví dụ:

```text
┌────────┬────────┬────────┐
│ image  │ image  │ image  │
├────────┼────────┼────────┤
│ image  │ image  │ image  │
├────────┼────────┼────────┤
│ image  │ image  │ image  │
└────────┴────────┴────────┘
```

Đây là use case tự nhiên của GridView.

---

# 24. `GridView` và `ListView`

Đây là cặp bạn phải phân biệt thật rõ.

### GridView

```text
A B C
D E F
G H I
```

### ListView

```text
A
B
C
D
E
F
```

Nếu app đọc truyện:

```text
Book Library
→ GridView
```

Chapter list:

```text
Chapter 1
Chapter 2
Chapter 3
...
```

→ `ListView`.

---

# 25. GridView vs ResponsiveRow

Đây là bảng cực kỳ quan trọng.

|              | ResponsiveRow             | GridView          |
| ------------ | ------------------------- | ----------------- |
| Mục đích     | Page layout               | Collection        |
| Grid         | 12 columns                | Grid items        |
| Scroll       | không phải mục đích chính | có                |
| Responsive   | rất mạnh                  | hỗ trợ qua sizing |
| Nhiều item   | không lý tưởng            | rất phù hợp       |
| Dashboard    | rất phù hợp               | phù hợp           |
| Gallery      | có thể                    | rất phù hợp       |
| Book library | có thể                    | rất phù hợp       |

Mental model:

```text
ResponsiveRow
→ layout

GridView
→ data collection
```

---

# 26. GridView vs Column

Nếu có:

```text
10 item
```

và muốn:

```text
A
B
C
...
```

dùng:

```python
ft.ListView()
```

hoặc Column tùy trường hợp.

Nếu:

```text
A B C
D E F
G H I
```

dùng:

```python
ft.GridView()
```

---

# 27. GridView trong app cào truyện

Kiến trúc:

```text
Page
│
├── SearchBar
│
├── FilterBar
│
└── GridView
    │
    ├── BookCard
    ├── BookCard
    ├── BookCard
    ├── BookCard
    └── ...
```

Đây gần như là kiến trúc chuẩn cho màn hình:

```text
Library
```

---

# 28. GridView trong màn hình Source

Bạn có:

```text
Nguồn truyện
```

Ví dụ:

```text
┌──────────┬──────────┬──────────┐
│ Source A │ Source B │ Source C │
├──────────┼──────────┼──────────┤
│ Source D │ Source E │ Source F │
└──────────┴──────────┴──────────┘
```

GridView rất phù hợp.

---

# 29. GridView trong dashboard

Ví dụ:

```text
┌────────┬────────┬────────┬────────┐
│ Books  │ Queue  │ Worker │ Errors │
├────────┼────────┼────────┼────────┤
│ Stats  │ Stats  │ Stats  │ Stats  │
└────────┴────────┴────────┴────────┘
```

Nếu số lượng card cố định:

```python
runs_count=4
```

là hợp lý.

---

# 30. `horizontal`

GridView mặc định thường được tư duy như vertical scrolling.

Nhưng có thể cấu hình hướng scroll.

Concept:

```python
ft.GridView(
    horizontal=True,
)
```

Khi đó grid có thể cuộn theo chiều ngang.

Ví dụ:

```text
┌────┬────┬────┬────┬────┬────┬──→
│ A  │ B  │ C  │ D  │ E  │ F  │
└────┴────┴────┴────┴────┴────┴──→
```

Use case:

* horizontal cards
* media carousel
* recommendations

---

# 31. Horizontal Book Carousel

Ví dụ:

```text
Recommended

┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ───→
│ Book │ │ Book │ │ Book │ │ Book │
└──────┘ └──────┘ └──────┘ └──────┘
```

GridView có thể dùng cho kiểu layout này.

---

# 32. GridView + `first_row_filled`

Trong những layout đặc biệt, GridView có các thuộc tính kiểm soát cách phân bố item.

Bạn không cần học thuộc ngay.

Quan trọng hiện tại là hiểu:

```text
GridView
→ grid algorithm
→ item distribution
→ scroll
```

Các thuộc tính nâng cao sẽ có ý nghĩa khi bạn làm project thực tế.

---

# 33. GridView và constraints

Một trong những lỗi thường gặp:

```text
GridView
    ↓
không hiển thị
```

Nguyên nhân có thể là parent không cấp height.

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Books"),
        ft.GridView(...),
    ]
)
```

Nếu GridView không được cấp không gian phù hợp, layout có thể không hoạt động như mong muốn.

Thường cần:

```python
ft.GridView(
    expand=True,
)
```

và parent cũng phải có constraints hợp lý.

---

# 34. Mental model về constraints

Hãy nhớ:

```text
Page
 ↓
Column
 ↓
GridView
 ↓
Grid item
```

Mỗi tầng phải trả lời:

```text
Tôi rộng bao nhiêu?
Tôi cao bao nhiêu?
```

Nếu GridView không biết:

```text
height
```

thì scroll layout rất dễ gặp vấn đề.

Đây là kiến thức sẽ được đào sâu ở:

> **Buổi 20 — Layout Constraints và Sizing**

---

# 35. GridView không phải virtualized list

Đây là một điểm nâng cao.

Bạn có:

```text
100,000 books
```

không nên nghĩ đơn giản:

```python
for book in books:
    grid.controls.append(book_card(book))
```

rồi tạo toàn bộ UI một lần mà không suy nghĩ về performance.

Với lượng dữ liệu rất lớn, cần thiết kế:

```text
pagination
lazy loading
data fetching
caching
```

và kiểm soát số lượng control.

---

# 36. Pagination

Ví dụ database có:

```text
100,000 books
```

Không load tất cả.

Ta có:

```text
Page 1
Book 1 → 50

Page 2
Book 51 → 100

...
```

GridView chỉ hiển thị tập dữ liệu hiện tại.

Kiến trúc:

```text
Database
   ↓
Repository
   ↓
Pagination
   ↓
GridView
```

Điều này rất phù hợp với kiến trúc app crawl truyện của bạn.

---

# 37. Infinite Scroll

Một kiến trúc nâng cao:

```text
Load 50 books

↓ scroll gần cuối

Load thêm 50

↓ scroll gần cuối

Load thêm 50
```

Concept:

```text
GridView
│
├── 1-50
│
├── 51-100
│
├── 101-150
│
└── ...
```

Đây là hướng chúng ta có thể triển khai sau khi học:

* event
* async
* state
* repository
* worker

---

# 38. GridView + Search

Một màn hình library thực tế:

```text
┌────────────────────────────────────────┐
│ Search: [ One Piece             ] 🔍   │
├────────────────────────────────────────┤
│                                        │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│ │ Book │ │ Book │ │ Book │ │ Book │   │
│ └──────┘ └──────┘ └──────┘ └──────┘   │
│                                        │
└────────────────────────────────────────┘
```

Tree:

```text
Column
│
├── SearchField
│
└── GridView
```

Đây là pattern cực kỳ quan trọng.

---

# 39. GridView + filter

Ví dụ:

```text
Search
Genre
Status
Source
Sort
```

Sau đó:

```text
Repository
    ↓
filtered books
    ↓
GridView
```

Không nên để GridView tự chịu trách nhiệm filtering data.

Đây là separation of concerns:

```text
UI
↓
state
↓
repository/service
↓
database
```

---

# 40. GridView + loading state

Bạn có thể kết hợp Buổi 14:

```text
Stack
│
├── GridView
│
└── Loading Overlay
```

Concept:

```text
Stack
├── GridView
└── Container
    └── ProgressRing
```

Khi đang load:

```text
overlay.visible = True
```

Khi xong:

```text
overlay.visible = False
```

---

# 41. Empty state

Một app thực tế cần xử lý:

```text
Không có truyện
```

Kiến trúc:

```text
Stack
├── GridView
└── EmptyState
```

hoặc state-driven:

```text
if loading:
    LoadingView

elif books:
    GridView

else:
    EmptyView
```

Sau này chúng ta sẽ học cách tổ chức state tốt hơn.

---

# 42. Error state

Tương tự:

```text
GridView
```

có thể có:

```text
Loading
Success
Empty
Error
```

Mental model:

```text
                    ┌── Loading
                    │
Data State ─────────┼── Success → GridView
                    │
                    ├── Empty
                    │
                    └── Error
```

Đây là tư duy rất quan trọng khi xây app thực tế.

---

# 43. Một kiến trúc Library tốt

```text
LibraryPage
│
├── SearchBar
├── FilterBar
│
└── Stack
    │
    ├── GridView
    │   ├── BookCard
    │   ├── BookCard
    │   └── ...
    │
    ├── LoadingOverlay
    │
    └── EmptyState
```

Đây là một UI architecture rất tốt cho project của bạn.

---

# 44. `GridView` + `Stack` + `ResponsiveRow`

Bây giờ bạn đã học:

```text
ResponsiveRow
Stack
GridView
```

Hãy phân biệt vai trò:

```text
ResponsiveRow
    ↓
page layout

GridView
    ↓
collection layout

Stack
    ↓
layering
```

Ví dụ:

```text
Page
│
└── ResponsiveRow
    │
    ├── Sidebar
    │
    └── Main
        │
        └── GridView
            │
            ├── BookCard
            │   └── Stack
            │
            ├── BookCard
            │   └── Stack
            │
            └── ...
```

Đây là một kiến trúc rất đáng ghi nhớ.

---

# 45. Bài tập 1 — Grid cơ bản

Tạo:

```text
12 items
```

với:

```python
runs_count=4
spacing=10
run_spacing=10
```

Kết quả:

```text
A B C D
E F G H
I J K L
```

---

# 46. Bài tập 2 — Responsive Book Grid

Tạo 20 book cards.

Dùng:

```python
max_extent=220
```

Không dùng:

```python
runs_count
```

Quan sát khi thay đổi kích thước cửa sổ.

Mục tiêu:

```text
desktop → nhiều cột
tablet  → ít cột
mobile  → rất ít cột
```

---

# 47. Bài tập 3 — Book Gallery

Tạo:

```text
BookCard
```

có:

```text
Stack
├── Image
├── Overlay
├── Title
└── Badge
```

Sau đó đặt vào:

```text
GridView
```

Đây là bài tập quan trọng nhất của buổi này.

---

# 48. Bài tập 4 — Library UI

Tạo:

```text
Column
│
├── Text("My Library")
│
├── SearchField
│
└── GridView
```

GridView:

```text
Book 1
Book 2
...
Book 50
```

Yêu cầu GridView scroll được.

---

# 49. Bài tập 5 — Loading

Thêm:

```text
Stack
├── GridView
└── LoadingOverlay
```

Button:

```text
Reload
```

Khi click:

```text
LoadingOverlay.visible = True
```

Sau đó:

```text
LoadingOverlay.visible = False
```

Bài này kết nối:

```text
Buổi 8  → State
Buổi 9  → page.update()
Buổi 14 → Stack
Buổi 16 → GridView
```

---

# 50. Bài tập 6 — App đọc truyện

Thiết kế:

```text
LibraryPage
│
├── SearchField
├── FilterBar
│
└── GridView
    │
    ├── BookCard
    ├── BookCard
    ├── BookCard
    └── ...
```

Mỗi BookCard:

```text
Stack
├── Cover
├── Overlay
├── Status Badge
└── Book Info
```

Đây chính là nền tảng của màn hình Library trong app đọc truyện.

---

# 51. Bài tập nâng cao — Pagination

Giả sử:

```text
database = 10,000 books
```

Không được load toàn bộ.

Thiết kế:

```text
Repository
    ↓
get_books(
    page=1,
    page_size=50
)
    ↓
GridView
```

Sau đó:

```text
Next
```

hoặc:

```text
Load More
```

để lấy batch tiếp theo.

---

# 52. Sai lầm cần tránh

### Sai lầm 1

Dùng `Column` cho hàng nghìn item.

```text
Column
├── Book 1
├── Book 2
├── ...
└── Book 10000
```

Không phù hợp.

---

### Sai lầm 2

Dùng `ResponsiveRow` làm database collection khổng lồ.

```text
ResponsiveRow
├── 1
├── 2
├── ...
└── 10000
```

Không phải use case tốt.

---

### Sai lầm 3

Hard-code `width` quá nhiều.

```python
width=220
```

không phải lúc nào cũng xấu, nhưng cần hiểu interaction với GridView.

---

### Sai lầm 4

Không cấp constraints cho GridView.

Ví dụ:

```text
Column
└── GridView
```

nhưng GridView không có kích thước hợp lý.

Hãy nghĩ đến:

```python
expand=True
```

---

# 53. Quy tắc chọn layout

Hãy lưu bảng này:

```text
A B C D
```

→ `Row`

```text
A
B
C
D
```

→ `Column` / `ListView`

```text
A B C
D E F
G H I
```

→ `GridView`

```text
Sidebar | Main
```

→ `ResponsiveRow`

```text
Image
  + Badge
  + Text
```

→ `Stack`

---

# 54. Công thức tư duy

Khi gặp UI, hãy hỏi:

### Câu 1

Các phần tử có phải là **collection** không?

Nếu có:

```text
GridView / ListView
```

### Câu 2

Có cần scroll không?

Nếu có:

```text
GridView / ListView
```

### Câu 3

Có phải layout của page không?

Nếu có:

```text
Row / Column / ResponsiveRow
```

### Câu 4

Có các layer chồng lên nhau không?

Nếu có:

```text
Stack
```

---

# 55. Kiến trúc UI hiện tại

Sau Buổi 16, chúng ta đã có:

```text
Page
│
└── ResponsiveRow
    │
    ├── Sidebar
    │
    └── Column
        │
        ├── Header
        │
        └── Stack
            │
            ├── GridView
            │   ├── BookCard
            │   │   └── Stack
            │   ├── BookCard
            │   │   └── Stack
            │   └── ...
            │
            └── LoadingOverlay
```

Đây đã bắt đầu giống một ứng dụng Flet thực tế chứ không còn là demo đơn giản.

---

# 56. Tổng kết Buổi 16

Bạn cần nắm thật chắc:

```text
GridView
│
├── runs_count
│
├── max_extent
│
├── spacing
│
├── run_spacing
│
├── expand
│
├── scrolling
│
└── grid collection
```

Và đặc biệt:

```text
ResponsiveRow
→ page layout responsive

GridView
→ scrollable grid collection
```

---

# Roadmap

```text
11. Row Deep Dive                  ✅
12. Column Deep Dive               ✅
13. Container Deep Dive            ✅
14. Stack                          ✅
15. ResponsiveRow                  ✅
16. GridView                       ← hiện tại
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

## Buổi 17 — `ListView` Deep Dive

Buổi tiếp theo chúng ta sẽ học `ListView` thật sâu và đặt nó cạnh `GridView` để hiểu **scrollable layout** một cách bài bản:

```text
Column
  ↓
ListView
  ↓
item
item
item
...
```

Đặc biệt sẽ áp dụng vào **Chapter List của app đọc truyện**, tìm hiểu vertical/horizontal list, spacing, divider, dynamic data, loading, empty state, và quan trọng nhất là cách thiết kế:

```text
Library
   ↓
GridView

Chapter List
   ↓
ListView
```

để bạn bắt đầu có một kiến trúc UI nhất quán cho ứng dụng đọc truyện.
