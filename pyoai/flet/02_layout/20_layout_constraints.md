# Buổi 20 — Layout Constraints & Sizing Deep Dive

Đây là một trong những buổi **quan trọng nhất của Flet Layout**.

Nếu bạn từng gặp tình huống:

```python
ft.Container(width=300)
```

nhưng UI không có kích thước như mong đợi, hoặc:

```python
ft.ListView(expand=True)
```

nhưng nó không scroll / không hiển thị đúng, thì nguyên nhân thường nằm ở **constraints**.

Hôm nay chúng ta xây dựng mental model từ gốc:

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

---

# 1. Vấn đề cốt lõi: Control không tự quyết định kích thước

Một sai lầm phổ biến khi học Flet là nghĩ:

```text
Container(width=300)
```

có nghĩa:

> "Container chắc chắn rộng 300."

Không hẳn.

Kích thước cuối cùng còn phụ thuộc vào **parent**.

Mental model:

```text
Parent
│
│  "Tôi cho phép con có kích thước
│   trong phạm vi này."
│
▼
Child
│
│ "Tôi muốn kích thước này."
│
▼
Final Size
```

---

# 2. Constraints là gì?

Có thể hiểu đơn giản:

> **Constraints là giới hạn mà parent áp đặt lên child.**

Ví dụ parent nói:

```text
width:
    min = 0
    max = 800

height:
    min = 0
    max = 600
```

Child không thể:

```text
width = 1200
```

vì:

```text
1200 > 800
```

---

# 3. Mental model cực kỳ quan trọng

Hãy nhớ:

```text
Parent
   ↓
gives constraints
   ↓
Child chooses size
   ↓
Parent positions child
```

Không phải:

```text
Child
   ↓
tự muốn kích thước
   ↓
Parent phải chấp nhận
```

---

# 4. `width` và `height`

Ví dụ:

```python
ft.Container(
    width=300,
    height=200,
)
```

Bạn đang nói:

```text
Tôi muốn:
width  = 300
height = 200
```

Nhưng parent vẫn có thể giới hạn.

---

# 5. Ví dụ Page

```python
import flet as ft


def main(page: ft.Page):

    page.add(
        ft.Container(
            width=300,
            height=200,
            bgcolor=ft.Colors.BLUE,
        )
    )


ft.run(main)
```

Concept:

```text
Page
└── Container
    width  = 300
    height = 200
```

---

# 6. Container trong `Column`

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Container(
            width=300,
            height=100,
        )
    ]
)
```

Mental model:

```text
Page
 ↓
Column
 ↓
Container
```

`Column` kiểm soát cách các child được bố trí theo chiều dọc.

---

# 7. Container trong `Row`

```python
ft.Row(
    controls=[
        ft.Container(
            width=300,
            height=100,
        )
    ]
)
```

Ở đây:

```text
Row
 ↓
Container
```

Row bố trí theo chiều ngang.

---

# 8. Tại sao `expand=True` quan trọng?

Ví dụ:

```python
ft.Container(
    expand=True,
)
```

Có thể hiểu:

> "Hãy sử dụng phần không gian mà parent cho phép."

Ví dụ:

```text
┌──────────────────────────────┐
│                              │
│         Container            │
│         expand=True          │
│                              │
└──────────────────────────────┘
```

---

# 9. `expand=True` trong Column

Ví dụ rất quan trọng:

```python
page.add(
    ft.Column(
        expand=True,
        controls=[
            ft.Text("Header"),
            ft.Container(
                expand=True,
            ),
        ],
    )
)
```

Mental model:

```text
Page
│
└── Column
    │
    ├── Header
    │
    └── Container
        expand=True
```

Container chiếm phần không gian còn lại.

---

# 10. Đây chính là pattern của app thực tế

Ví dụ:

```text
┌─────────────────────────────────┐
│ Header                           │
├─────────────────────────────────┤
│                                 │
│ Content                         │
│                                 │
│                                 │
├─────────────────────────────────┤
│ Footer                           │
└─────────────────────────────────┘
```

Có thể tư duy:

```text
Column
│
├── Header
│
├── Content
│   expand=True
│
└── Footer
```

---

# 11. `expand=True` không có nghĩa "to nhất có thể"

Đây là điểm rất quan trọng.

Nó phụ thuộc vào **không gian mà parent cung cấp**.

Nếu parent chỉ có:

```text
height = 300
```

thì child không thể chiếm:

```text
height = 1000
```

---

# 12. `expand` trong Row

Ví dụ:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(
            expand=True,
        ),
        ft.Container(
            expand=True,
        ),
    ],
)
```

Concept:

```text
┌───────────────────────────────────────┐
│                 │                     │
│   Container     │     Container       │
│   expand        │     expand          │
│                 │                     │
└───────────────────────────────────────┘
```

Không gian được phân chia giữa các child.

---

# 13. `expand=1`, `expand=2`

Trong layout có thể tư duy theo tỷ lệ.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(expand=1),
        ft.Container(expand=2),
    ]
)
```

Concept:

```text
┌────────────┬─────────────────────────┐
│            │                         │
│   1 part   │        2 parts          │
│            │                         │
└────────────┴─────────────────────────┘
```

Tức:

```text
1 : 2
```

---

# 14. Đây rất hữu ích cho Dashboard

Ví dụ:

```text
┌────────────┬─────────────────────────┐
│ Sidebar    │ Main                    │
│            │                         │
│            │                         │
│            │                         │
└────────────┴─────────────────────────┘
```

Code:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(
            width=250,
        ),
        ft.Container(
            expand=True,
        ),
    ],
)
```

Hoặc theo tỷ lệ:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(expand=1),
        ft.Container(expand=4),
    ],
)
```

---

# 15. `ListView` và constraints

Đây là phần cực kỳ quan trọng.

Ví dụ:

```python
ft.Column(
    controls=[
        ft.Text("Chapters"),
        ft.ListView(
            controls=[
                ft.Text("Chapter 1"),
                ft.Text("Chapter 2"),
            ]
        ),
    ]
)
```

Có thể gặp vấn đề vì:

```text
Column
 ↓
ListView
```

ListView cần biết:

> "Tôi cao bao nhiêu?"

Nếu không có giới hạn phù hợp, layout có thể không hoạt động như bạn mong muốn.

---

# 16. Pattern đúng: `ListView(expand=True)`

Thường:

```python
ft.Column(
    expand=True,
    controls=[
        ft.Text("Chapters"),
        ft.ListView(
            expand=True,
            controls=[
                ...
            ],
        ),
    ],
)
```

Mental model:

```text
Column
│
├── Text
│
└── ListView
    expand=True
```

ListView lấy phần còn lại.

---

# 17. Tại sao ListView cần constraint?

ListView là scrollable control.

Nó cần một viewport:

```text
┌─────────────────────────┐
│ Chapter 1               │
│ Chapter 2               │
│ Chapter 3               │
│ Chapter 4               │
│ Chapter 5               │
└─────────────────────────┘
              ↕ scroll
```

Nếu không biết viewport cao bao nhiêu, hệ thống layout không thể xác định vùng scroll đúng cách.

---

# 18. ListView trong Container

Ví dụ:

```python
ft.Container(
    height=400,
    content=ft.ListView(
        controls=[
            ...
        ]
    )
)
```

Ở đây:

```text
Container
height = 400
   ↓
ListView
```

ListView có giới hạn rõ ràng.

---

# 19. Hoặc `expand=True`

```python
ft.Container(
    expand=True,
    content=ft.ListView(
        expand=True,
        controls=[
            ...
        ],
    ),
)
```

Mental model:

```text
Page
 ↓
Container
 expand
 ↓
ListView
 expand
```

---

# 20. `GridView` cũng cần constraints

Ví dụ:

```python
ft.GridView(
    controls=[
        ...
    ]
)
```

Nếu GridView nằm trong layout không có kích thước rõ ràng, bạn có thể gặp vấn đề.

Pattern thường dùng:

```python
ft.GridView(
    expand=True,
    runs_count=4,
)
```

Ví dụ:

```text
Column
│
├── Header
│
└── GridView
    expand=True
```

---

# 21. `Column` + `GridView`

Đây là pattern dashboard:

```python
ft.Column(
    expand=True,
    controls=[
        ft.Text("Library"),
        ft.GridView(
            expand=True,
            runs_count=4,
        ),
    ],
)
```

UI:

```text
┌───────────────────────────────┐
│ Library                       │
├───────────────────────────────┤
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐ │
│ │ A  │ │ B  │ │ C  │ │ D  │ │
│ └────┘ └────┘ └────┘ └────┘ │
│                               │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐ │
│ │ E  │ │ F  │ │ G  │ │ H  │ │
│ └────┘ └────┘ └────┘ └────┘ │
└───────────────────────────────┘
```

---

# 22. `Row` và chiều cao

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(
            width=200,
            height=100,
        ),
        ft.Container(
            width=200,
            height=200,
        ),
    ]
)
```

Concept:

```text
┌──────────┐   ┌──────────┐
│          │   │          │
│  100px   │   │          │
│          │   │  200px   │
└──────────┘   │          │
               └──────────┘
```

Row phải xử lý sự khác biệt kích thước giữa các child.

---

# 23. `Column` và chiều rộng

Tương tự:

```python
ft.Column(
    controls=[
        ft.Container(
            width=100,
            height=100,
        ),
        ft.Container(
            width=300,
            height=100,
        ),
    ]
)
```

Concept:

```text
┌──────────────┐
│              │
│  100         │
└──────────────┘

┌────────────────────────┐
│                        │
│          300           │
└────────────────────────┘
```

---

# 24. Cross Axis và Main Axis

Đây là khái niệm bạn cần chuẩn bị cho Buổi 21.

### Row

```text
Main axis
→→→→→→→→
```

Cross axis:

```text
↓
↓
↓
```

### Column

```text
Main axis
↓
↓
↓
```

Cross axis:

```text
→→→→
```

Visual:

```text
Row:

      cross
       ↓
       │
───────┼────────→ main


Column:

main
 ↓
 ↓
 ↓
 ─────────→ cross
```

---

# 25. `alignment` và constraints liên quan thế nào?

Ví dụ:

```python
ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Nếu Row có:

```text
width = 1000
```

nhưng children chỉ cần:

```text
300
```

thì còn:

```text
1000 - 300 = 700
```

không gian dư.

`alignment` quyết định đặt 300px đó ở đâu.

```text
START

┌──────────────────────────┐
│███                       │
└──────────────────────────┘
```

CENTER:

```text
┌──────────────────────────┐
│         ███              │
└──────────────────────────┘
```

END:

```text
┌──────────────────────────┐
│                       ███│
└──────────────────────────┘
```

---

# 26. `width` khác `expand`

Đây là câu hỏi bạn phải phân biệt:

```python
width=300
```

và:

```python
expand=True
```

### width

```text
Tôi muốn khoảng 300px.
```

### expand

```text
Tôi muốn sử dụng không gian được phân bổ cho tôi.
```

Mental model:

```text
width
→ kích thước cụ thể

expand
→ kích thước dựa trên available space
```

---

# 27. `Container(width=300)` trong Row

```python
ft.Row(
    controls=[
        ft.Container(width=300),
    ]
)
```

Nó muốn:

```text
300px
```

---

# 28. `Container(expand=True)` trong Row

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(expand=True),
    ]
)
```

Nó muốn:

```text
phần không gian còn lại
```

---

# 29. Kết hợp fixed + flexible

Đây là pattern cực kỳ quan trọng:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(
            width=250,
        ),
        ft.Container(
            expand=True,
        ),
    ],
)
```

Mental model:

```text
┌──────────────┬─────────────────────────┐
│   250px      │       flexible          │
│   Sidebar    │       Content           │
└──────────────┴─────────────────────────┘
```

Đây là layout của rất nhiều desktop app.

---

# 30. App đọc truyện

Ví dụ:

```text
┌────────────────────────────────────────────┐
│ Sidebar       │ Reader                     │
│               │                            │
│ Chapters      │                            │
│               │       Page content         │
│               │                            │
└────────────────────────────────────────────┘
```

Code:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(
            width=280,
            content=chapter_list,
        ),
        ft.Container(
            expand=True,
            content=reader,
        ),
    ],
)
```

---

# 31. `Container` sizing

`Container` có thể dùng:

```python
ft.Container(
    width=300,
    height=200,
)
```

hoặc:

```python
ft.Container(
    expand=True,
)
```

hoặc kết hợp:

```python
ft.Container(
    width=300,
    expand=False,
)
```

Tư duy:

```text
fixed
vs
flexible
```

---

# 32. Không nên hard-code mọi thứ

Một layout như:

```python
width=300
height=500
width=400
height=700
```

có thể chạy trên một màn hình nhưng hỏng trên màn hình khác.

Ví dụ:

```text
Desktop 1920px
→ đẹp

Laptop 1366px
→ có thể chật

Mobile 390px
→ vỡ layout
```

Vì vậy:

```text
fixed size
+
flexible size
+
responsive
```

phải được cân bằng.

---

# 33. Một lỗi phổ biến: Nested expand

Ví dụ:

```text
Column(expand=True)
└── Container(expand=True)
    └── Column(expand=True)
        └── ListView(expand=True)
```

Không phải cứ thêm:

```python
expand=True
```

ở mọi nơi là đúng.

Bạn phải hỏi:

> Control nào thực sự cần chiếm phần không gian còn lại?

---

# 34. Quy tắc thực hành

Khi gặp layout lỗi, đi từ ngoài vào:

```text
1. Page
   ↓
2. Parent
   ↓
3. Child
   ↓
4. Scrollable
```

Hỏi:

```text
Parent có kích thước không?
        ↓
Child có constraint không?
        ↓
Child có expand cần thiết không?
        ↓
Có nested scroll không?
```

---

# 35. Debug layout

Một kỹ thuật rất hữu ích là thêm màu tạm thời.

Ví dụ:

```python
ft.Container(
    bgcolor=ft.Colors.RED,
    content=...
)
```

Parent:

```python
ft.Container(
    bgcolor=ft.Colors.BLUE,
    content=...
)
```

Bạn có thể nhìn:

```text
BLUE = parent
RED  = child
```

để hiểu control thực tế đang chiếm bao nhiêu không gian.

---

# 36. Debug bằng border

Có thể dùng decoration để nhìn boundaries.

Ví dụ concept:

```python
ft.Container(
    border=ft.Border.all(1),
    content=...
)
```

Mental model:

```text
┌─────────────────────────────┐
│ Parent                      │
│  ┌───────────────────────┐  │
│  │ Child                 │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

Khi học layout, **hãy luôn nhìn boundaries**.

---

# 37. Constraint problem kinh điển

Ví dụ:

```python
ft.Column(
    controls=[
        ft.ListView(
            controls=[
                ...
            ]
        )
    ]
)
```

Bạn thấy:

```text
ListView
```

không hoạt động như mong muốn.

Hãy thử:

```python
ft.Column(
    expand=True,
    controls=[
        ft.ListView(
            expand=True,
            controls=[
                ...
            ],
        )
    ],
)
```

Tại sao?

```text
Page
 ↓
Column
 ↓
ListView
```

Bây giờ ListView được cấp vùng rõ ràng.

---

# 38. Nested scroll

Đây là một chủ đề cần đặc biệt cẩn thận.

Ví dụ:

```text
ListView
└── Column
    └── ListView
```

Bạn đang có:

```text
scroll
 ↓
scroll
```

Có thể gây UX rất tệ hoặc constraint khó kiểm soát.

Thông thường nên thiết kế:

```text
Một scroll container chính
```

Ví dụ:

```text
ListView
├── Header
├── Card
├── ExpansionTile
└── ...
```

thay vì:

```text
ListView
└── Column
    └── ListView
```

---

# 39. Một pattern tốt cho Book Detail

Thay vì:

```text
Column
├── Header
└── ListView
```

nếu sizing không rõ, hãy xác định rõ:

```text
Column(expand=True)
├── Header
└── ListView(expand=True)
```

Code:

```python
ft.Column(
    expand=True,
    controls=[
        book_header,
        chapter_list,
    ],
)
```

và:

```python
chapter_list = ft.ListView(
    expand=True,
)
```

---

# 40. `Card` và constraints

Ví dụ:

```python
ft.Card(
    content=ft.ListTile(...)
)
```

Card không tự động có width cố định theo ý bạn.

Width của Card phụ thuộc vào context.

Nếu muốn Card có width:

```python
ft.Container(
    width=300,
    content=ft.Card(
        content=...
    ),
)
```

Tree:

```text
Container
width=300
│
└── Card
    └── ListTile
```

---

# 41. GridView + Card

Trong GridView:

```text
GridView
 ↓
Card
```

Card thường nên:

```text
fill available cell
```

thay vì cố định width quá lớn.

Ví dụ:

```python
ft.Card(
    content=ft.Container(
        padding=10,
        content=...
    )
)
```

GridView quyết định cell layout.

---

# 42. Layout thật sự là một cây

Hãy nhìn UI này:

```text
Page
│
└── Column
    │
    ├── Header
    │
    └── Row
        │
        ├── Sidebar
        │
        └── Column
            │
            ├── Toolbar
            │
            └── ListView
```

Constraints truyền xuống:

```text
Page
 ↓
Column
 ↓
Row
 ↓
Column
 ↓
ListView
```

Nếu một tầng không có constraint phù hợp:

```text
          ↓
      problem
          ↓
    ListView
```

Đó là lý do phải hiểu UI Tree.

---

# 43. Một cách tư duy rất mạnh

Khi thiết kế:

### Bước 1

Xác định vùng lớn:

```text
Page
```

### Bước 2

Chia:

```text
Header
Content
Footer
```

### Bước 3

Content:

```text
Sidebar
Main
```

### Bước 4

Main:

```text
Toolbar
Content
```

### Bước 5

Content:

```text
ListView
```

Sau đó mới quyết định:

```text
width
height
expand
alignment
```

---

# 44. Ví dụ Dashboard

```text
Page
│
└── Column(expand=True)
    │
    ├── Header
    │
    └── Row(expand=True)
        │
        ├── Sidebar(width=250)
        │
        └── Column(expand=True)
            │
            ├── Toolbar
            │
            └── GridView(expand=True)
```

Đây là một layout cực kỳ chuẩn:

```text
fixed
+
flexible
+
flexible
```

---

# 45. Ví dụ Crawl Dashboard

```text
┌────────────────────────────────────────────────────┐
│ Crawl Dashboard                                    │
├──────────────┬─────────────────────────────────────┤
│ Sources      │ Queue                               │
│              │                                     │
│ Novel A      │ Job 1                               │
│ Novel B      │ Job 2                               │
│ Novel C      │ Job 3                               │
│              │                                     │
│              │                                     │
└──────────────┴─────────────────────────────────────┘
```

Tree:

```text
Column(expand=True)
│
├── Header
│
└── Row(expand=True)
    │
    ├── Sidebar(width=250)
    │
    └── ListView(expand=True)
```

---

# 46. Constraint Debug Checklist

Khi UI bị:

```text
overflow
không scroll
không full screen
size sai
control biến mất
```

hãy kiểm tra:

### 1. Parent có kích thước không?

```text
Page
Column
Row
Container
```

### 2. Child cần `expand` không?

```python
expand=True
```

### 3. Scrollable có viewport không?

```text
ListView
GridView
```

### 4. Có nested scroll không?

```text
ListView
  ↓
ListView
```

### 5. Có hard-code width/height quá lớn không?

```python
width=1200
```

trong một container nhỏ.

---

# 47. Bài tập 1 — Layout Playground

Hãy tạo một app:

```text
Layout Playground
```

Có:

```text
┌──────────────────────────────────────┐
│ Header                               │
├──────────────┬───────────────────────┤
│ Sidebar      │ Content               │
│              │                       │
│              │                       │
└──────────────┴───────────────────────┘
```

Yêu cầu:

```text
Header → fixed height
Sidebar → fixed width
Content → expand
```

---

# 48. Bài tập 2 — ListView

Tạo:

```text
Column
├── Text("Chapters")
└── ListView
```

Yêu cầu:

* Column full page
* ListView chiếm phần còn lại
* 100 chapter
* scroll được

Mental model:

```text
Column(expand=True)
│
├── Header
│
└── ListView(expand=True)
```

---

# 49. Bài tập 3 — Reader Layout

Tạo:

```text
┌──────────────────────────────────────┐
│ Toolbar                              │
├───────────────┬──────────────────────┤
│ Chapters      │ Reader               │
│               │                      │
│ Chapter 1     │ Content              │
│ Chapter 2     │                      │
│ Chapter 3     │                      │
└───────────────┴──────────────────────┘
```

Quy tắc:

```text
Toolbar → fixed
Sidebar → 280px
Reader → expand
Chapter list → expand
```

---

# 50. Bài tập 4 — Grid

Tạo:

```text
Column(expand=True)
│
├── Text("Library")
│
└── GridView(expand=True)
```

Grid có:

```text
20 Card
```

Mỗi Card:

```text
Container
 ├── Image
 └── Text
```

---

# 51. Bài tập 5 — Cố tình tạo lỗi

Hãy thử:

```python
ft.Column(
    controls=[
        ft.ListView(
            controls=[
                ft.Text("A"),
                ft.Text("B"),
                ft.Text("C"),
            ]
        )
    ]
)
```

Sau đó sửa thành:

```python
ft.Column(
    expand=True,
    controls=[
        ft.ListView(
            expand=True,
            controls=[
                ft.Text("A"),
                ft.Text("B"),
                ft.Text("C"),
            ],
        )
    ],
)
```

Quan sát sự khác biệt.

Mục tiêu không phải học thuộc:

```python
expand=True
```

mà hiểu:

```text
Tại sao ListView cần không gian được xác định?
```

---

# 52. Mini Project — Responsive Book Library

Xây:

```text
Book Library
```

Desktop:

```text
┌──────────────┬─────────────────────────────┐
│ Categories   │ Books                       │
│              │                             │
│ Action       │ [A] [B] [C] [D]            │
│ Romance      │ [E] [F] [G] [H]            │
│ Fantasy      │                             │
└──────────────┴─────────────────────────────┘
```

Kiến trúc:

```text
Page
└── Row(expand=True)
    │
    ├── Container(width=250)
    │   └── ListView
    │
    └── GridView(expand=True)
        ├── Card
        ├── Card
        └── ...
```

Sau này Buổi 23 sẽ biến layout này thành responsive.

---

# 53. Tổng kết Buổi 20

Bạn cần nắm chắc 6 khái niệm:

```text
1. constraints
2. width / height
3. expand
4. fixed size
5. flexible size
6. scrollable constraints
```

Mental model quan trọng nhất:

```text
                 Parent
                   │
                   │ constraints
                   ▼
                 Child
                   │
                   │ chooses size
                   ▼
                Final Size
```

Và đối với layout thực tế:

```text
Page
 ↓
Parent
 ↓
Child
 ↓
Scrollable
```

mỗi tầng phải có **không gian xác định hợp lý**.

---

# Roadmap cập nhật

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
21. Alignment
22. Spacing / padding / margin
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

### Buổi 21 — Alignment

Buổi tiếp theo chúng ta sẽ đào rất sâu vào:

```text
Row
 ├── MainAxisAlignment
 └── CrossAxisAlignment

Column
 ├── MainAxisAlignment
 └── CrossAxisAlignment
```

và giải quyết những câu hỏi cực kỳ thực tế:

```text
"center" hoạt động thế nào?
start / center / end khác nhau ra sao?
spaceBetween / spaceAround / spaceEvenly khác nhau thế nào?
cross_axis_alignment dùng khi nào?
Tại sao Text không nằm chính giữa?
Làm sao căn icon + text chuẩn?
```

Đây sẽ là nền tảng để sang **Buổi 22 — spacing, padding, margin** mà không còn phải căn UI bằng cách thử từng con số.
