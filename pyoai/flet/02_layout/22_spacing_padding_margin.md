# Buổi 22 — Spacing / Padding / Margin Deep Dive

Hôm nay chúng ta giải quyết một vấn đề tưởng đơn giản nhưng cực kỳ quan trọng khi xây UI Flet:

> **Khoảng cách này nên đặt ở đâu? `spacing`, `padding` hay `margin`?**

Nếu hiểu đúng 3 khái niệm này, bạn sẽ không còn phải "chỉnh số cho đến khi UI vừa mắt".

---

# 1. Ba khái niệm cốt lõi

Hãy bắt đầu bằng mental model:

```text
┌─────────────────────────────────────┐
│              MARGIN                 │
│   ┌─────────────────────────────┐   │
│   │          BORDER             │   │
│   │   ┌─────────────────────┐   │   │
│   │   │      PADDING        │   │   │
│   │   │   ┌─────────────┐   │   │   │
│   │   │   │   CONTENT   │   │   │   │
│   │   │   └─────────────┘   │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

Trong tư duy UI:

```text
margin
→ khoảng cách bên ngoài control

padding
→ khoảng cách bên trong control

spacing
→ khoảng cách giữa các child
```

---

# 2. `padding` là gì?

`padding` tạo khoảng cách:

```text
biên của container
        ↓
      content
```

Ví dụ:

```python
ft.Container(
    padding=20,
    content=ft.Text("Hello"),
)
```

Concept:

```text
┌─────────────────────────┐
│                         │
│       Hello             │
│                         │
└─────────────────────────┘
```

`Hello` không sát biên.

---

# 3. Nếu không có padding

```python
ft.Container(
    content=ft.Text("Hello"),
)
```

Concept:

```text
┌─────────────┐
│Hello        │
└─────────────┘
```

---

# 4. Padding không phải spacing

Đây là điểm rất quan trọng.

### Padding

```text
┌──────────────────────┐
│   A                  │
└──────────────────────┘
    ↑
  padding
```

### Spacing

```text
A
     
B
```

Khoảng cách:

```text
A ↕ B
```

là `spacing`.

---

# 5. `Column.spacing`

Ví dụ:

```python
ft.Column(
    spacing=20,
    controls=[
        ft.Text("Name"),
        ft.TextField(),
        ft.Text("Email"),
        ft.TextField(),
    ],
)
```

Concept:

```text
Name

          ← 20px

[ TextField ]

          ← 20px

Email

          ← 20px

[ TextField ]
```

`spacing` nằm **giữa các child**.

---

# 6. `Row.spacing`

Tương tự:

```python
ft.Row(
    spacing=10,
    controls=[
        ft.Button("Save"),
        ft.Button("Cancel"),
        ft.Button("Delete"),
    ],
)
```

UI:

```text
[ Save ]  [ Cancel ]  [ Delete ]
          ↑      ↑
        spacing
```

---

# 7. `spacing` thuộc parent

Đây là một nguyên tắc rất đáng nhớ:

```text
Column
├── A
├── B
└── C
```

Nếu muốn:

```text
A
  20px
B
  20px
C
```

hãy nghĩ:

```python
Column(spacing=20)
```

thay vì:

```python
A margin
B margin
C margin
```

---

# 8. Khi nào dùng spacing?

Dùng `spacing` khi:

> Khoảng cách là **quy luật chung giữa các child**.

Ví dụ:

```text
Form
├── Label
├── TextField
├── Label
├── TextField
└── Button
```

Có thể:

```python
ft.Column(
    spacing=12,
    controls=[...],
)
```

---

# 9. Padding của Card

Một pattern rất phổ biến:

```python
ft.Card(
    content=ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ...
            ],
        ),
    ),
)
```

Tree:

```text
Card
└── Container
    padding=20
    │
    └── Column
```

Concept:

```text
┌───────────────────────────────┐
│                               │
│   ┌───────────────────────┐   │
│   │ Content               │   │
│   └───────────────────────┘   │
│                               │
└───────────────────────────────┘
       ↑
     padding
```

---

# 10. Padding + spacing

Hai thứ thường đi cùng nhau.

Ví dụ:

```python
ft.Container(
    padding=20,
    content=ft.Column(
        spacing=10,
        controls=[
            ft.Text("Title"),
            ft.Text("Description"),
            ft.Button("Open"),
        ],
    ),
)
```

Ý nghĩa:

```text
Container
│
├── padding = khoảng cách biên
│
└── Column
    │
    └── spacing = khoảng cách giữa children
```

---

# 11. Visualize

```text
┌───────────────────────────────────┐
│  ← padding                         │
│   ┌─────────────────────────────┐ │
│   │ Title                       │ │
│   │                             │ │
│   │ Description                 │ │
│   │                             │ │
│   │ [ Open ]                    │ │
│   └─────────────────────────────┘ │
│                                   │
└───────────────────────────────────┘
```

Khoảng cách:

```text
biên → Title
```

là:

```text
padding
```

Khoảng cách:

```text
Title → Description
Description → Button
```

là:

```text
spacing
```

---

# 12. `margin` là gì?

`margin` là khoảng cách **bên ngoài control**.

Concept:

```text
┌─────────────────────────────────────┐
│                                     │
│      margin                         │
│      ↓                              │
│      ┌───────────────┐              │
│      │   Control     │              │
│      └───────────────┘              │
│                                     │
└─────────────────────────────────────┘
```

Nó tạo khoảng cách giữa control và những thứ xung quanh.

---

# 13. Ví dụ margin

Concept:

```python
ft.Container(
    margin=20,
    content=ft.Text("Hello"),
)
```

Nếu đặt trong parent:

```text
Parent
│
├── Control A
│
└── Container
    margin=20
```

thì Container tạo khoảng cách với vùng xung quanh.

---

# 14. Padding vs Margin

Đây là bảng phải nhớ:

|                   | Padding          | Margin              |
| ----------------- | ---------------- | ------------------- |
| Vị trí            | bên trong        | bên ngoài           |
| Tạo khoảng cách   | border → content | control → bên ngoài |
| Ảnh hưởng content | Có               | Không trực tiếp     |
| Thường dùng       | Card/Form        | giữa các component  |

Mental model:

```text
margin
  ↓
[ Container ]
  ↑
padding
  ↓
[ content ]
```

---

# 15. Một cách nhớ rất đơn giản

Hãy tưởng tượng một cái hộp.

```text
margin
→ khoảng cách từ hộp này đến hộp khác

padding
→ khoảng cách từ thành hộp đến đồ vật bên trong

spacing
→ khoảng cách giữa các đồ vật bên trong
```

---

# 16. `padding` có thể truyền số

Ví dụ:

```python
ft.Container(
    padding=20,
)
```

Tức:

```text
top    = 20
right  = 20
bottom = 20
left   = 20
```

---

# 17. Padding không đều

Bạn có thể muốn:

```text
top    = 10
right  = 20
bottom = 30
left   = 40
```

Trong Flet, có thể sử dụng cấu trúc padding tương ứng thay vì chỉ truyền một số.

Concept:

```python
padding=ft.Padding(
    top=10,
    right=20,
    bottom=30,
    left=40,
)
```

Mental model:

```text
        10
   ┌───────────┐
40 │           │ 20
   └───────────┘
        30
```

---

# 18. `margin` cũng tương tự

Bạn có thể tư duy:

```text
top
right
bottom
left
```

thay vì:

```text
một giá trị duy nhất
```

Điều này hữu ích khi xây layout phức tạp.

---

# 19. Khi nào dùng padding?

Ví dụ Book Card:

```text
┌──────────────────────────────┐
│                              │
│  Naruto                      │
│                              │
│  1200 chapters               │
│                              │
│  [ Open ]                    │
│                              │
└──────────────────────────────┘
```

Bạn muốn nội dung không sát cạnh Card.

Dùng:

```python
padding=16
```

---

# 20. Khi nào dùng margin?

Ví dụ:

```text
Card A

Card B
```

Bạn muốn:

```text
Card A
    ↓
  16px
    ↓
Card B
```

Đây là khoảng cách **giữa hai component**.

Về mặt tư duy, đó là margin hoặc spacing tùy cấu trúc parent.

---

# 21. Nhưng thường nên ưu tiên `spacing`

Ví dụ bạn có:

```text
Column
├── Card A
├── Card B
├── Card C
└── Card D
```

Thay vì:

```text
Card A → margin bottom
Card B → margin bottom
Card C → margin bottom
```

nên:

```python
ft.Column(
    spacing=16,
    controls=[
        card_a,
        card_b,
        card_c,
        card_d,
    ],
)
```

Đây là cách thiết kế sạch hơn.

---

# 22. `spacing` là "layout responsibility"

Hãy nghĩ:

```text
Column
```

nói:

> "Tôi quyết định khoảng cách giữa các con."

Trong khi:

```text
Container
```

nói:

> "Tôi quyết định khoảng cách từ nội dung đến biên của tôi."

Đây là separation of responsibility rất quan trọng.

---

# 23. Form chuẩn

Ví dụ:

```python
form = ft.Container(
    padding=24,
    content=ft.Column(
        spacing=12,
        controls=[
            ft.Text("Username"),
            ft.TextField(),
            ft.Text("Password"),
            ft.TextField(password=True),
            ft.Button("Login"),
        ],
    ),
)
```

Phân tích:

```text
Container
│
└── padding=24
    │
    └── Column
        │
        └── spacing=12
```

Đây là một pattern rất sạch.

---

# 24. Card chuẩn

```python
book_card = ft.Card(
    content=ft.Container(
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Naruto"),
                ft.Text("1200 chapters"),
                ft.Button("Read"),
            ],
        ),
    ),
)
```

Tư duy:

```text
Card
 ↓
padding
 ↓
Column
 ↓
spacing
```

---

# 25. `Row` + spacing

Ví dụ action buttons:

```python
ft.Row(
    spacing=8,
    controls=[
        ft.Button("Save"),
        ft.Button("Cancel"),
    ],
)
```

UI:

```text
[ Save ]  [ Cancel ]
```

Nếu không có spacing:

```text
[ Save ][ Cancel ]
```

---

# 26. `Column` + spacing

Ví dụ settings:

```python
ft.Column(
    spacing=16,
    controls=[
        general_section,
        download_section,
        network_section,
    ],
)
```

UI:

```text
General

    ↓ 16

Download

    ↓ 16

Network
```

---

# 27. Padding cho section

Bạn có thể:

```python
def section(title, content):
    return ft.Container(
        padding=20,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text(title),
                content,
            ],
        ),
    )
```

Dùng:

```python
section(
    "Network",
    network_settings,
)
```

Đây là cách bắt đầu tạo **reusable UI component**.

---

# 28. Padding + margin + spacing cùng lúc

Ví dụ:

```python
ft.Container(
    margin=10,
    padding=20,
    content=ft.Column(
        spacing=8,
        controls=[
            ft.Text("Title"),
            ft.Text("Description"),
            ft.Button("Open"),
        ],
    ),
)
```

Đọc từ ngoài vào:

```text
margin
 ↓
Container
 ↓
padding
 ↓
Column
 ↓
spacing
 ↓
children
```

Đây là mental model cực kỳ quan trọng.

---

# 29. Box Model hoàn chỉnh

Hãy hình dung:

```text
          MARGIN
   ┌───────────────────────┐
   │                       │
   │   ┌───────────────┐   │
   │   │    PADDING    │   │
   │   │  ┌─────────┐  │   │
   │   │  │ CONTENT │  │   │
   │   │  └─────────┘  │   │
   │   └───────────────┘   │
   │                       │
   └───────────────────────┘
```

Với Flet:

```text
margin
→ bên ngoài

padding
→ bên trong

spacing
→ giữa siblings
```

---

# 30. Spacing không giống CSS margin hoàn toàn

Nếu bạn đã học CSS, đừng áp dụng máy móc:

```text
CSS
→ margin collapsing
```

Trong Flet, hãy tư duy đơn giản hơn:

```text
Column.spacing
→ khoảng cách giữa children

Row.spacing
→ khoảng cách giữa children
```

Đây là mô hình dễ kiểm soát hơn.

---

# 31. Nested Column

Ví dụ:

```text
Column
├── Header
│
├── Column
│   ├── A
│   ├── B
│   └── C
│
└── Footer
```

Bạn có thể có:

```text
Outer Column
spacing=20

Inner Column
spacing=8
```

Ví dụ:

```python
ft.Column(
    spacing=20,
    controls=[
        header,
        ft.Column(
            spacing=8,
            controls=[
                a,
                b,
                c,
            ],
        ),
        footer,
    ],
)
```

---

# 32. Tại sao nested spacing rất hữu ích?

Bạn có thể tạo hierarchy:

```text
Page sections
    spacing = 24

Inside section
    spacing = 12

Inside form group
    spacing = 8
```

Ví dụ:

```text
Dashboard
│
├── Overview
│   ├── Card
│   ├── Card
│   └── Card
│
├── Recent Jobs
│   ├── Job
│   └── Job
│
└── Workers
    ├── Worker
    └── Worker
```

Mỗi tầng có spacing riêng.

---

# 33. Design system

Đây là lúc bạn bắt đầu tư duy chuyên nghiệp.

Thay vì viết:

```python
spacing=7
spacing=13
spacing=19
spacing=23
```

hãy định nghĩa:

```python
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32
```

Sau đó:

```python
ft.Column(
    spacing=SPACING_MD,
)
```

---

# 34. Tại sao design tokens quan trọng?

App lớn có hàng trăm component.

Nếu bạn viết:

```text
Card A → padding 15
Card B → padding 17
Card C → padding 19
Card D → padding 14
```

UI sẽ trở nên thiếu nhất quán.

Thay vào đó:

```text
Card
→ padding = 16

Section
→ padding = 24

Page
→ padding = 32
```

UI nhìn chuyên nghiệp hơn.

---

# 35. Ví dụ Design Tokens

```python
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}
```

Dùng:

```python
ft.Column(
    spacing=SPACING["md"],
)
```

hoặc:

```python
ft.Container(
    padding=SPACING["lg"],
)
```

---

# 36. Page Layout

Một pattern tốt:

```text
Page
└── Container
    padding=24
    │
    └── Column
        spacing=24
        │
        ├── Header
        ├── Stats
        ├── Recent Jobs
        └── Workers
```

Code concept:

```python
ft.Container(
    expand=True,
    padding=24,
    content=ft.Column(
        spacing=24,
        controls=[
            header,
            stats,
            recent_jobs,
            workers,
        ],
    ),
)
```

Đây là pattern bạn sẽ dùng rất nhiều khi xây Dashboard.

---

# 37. Dashboard

Ví dụ:

```text
┌───────────────────────────────────────────────┐
│             padding 24                        │
│                                               │
│  Header                                       │
│                                               │
│  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │Jobs  │  │Done  │  │Failed│               │
│  └──────┘  └──────┘  └──────┘               │
│                                               │
│  Recent Jobs                                  │
│                                               │
│  Job 1                                        │
│  Job 2                                        │
│                                               │
└───────────────────────────────────────────────┘
```

Hierarchy:

```text
Page
 ↓
padding 24
 ↓
Column spacing 24
 ↓
sections
 ↓
section padding
 ↓
inner spacing
```

---

# 38. App crawl worker

Một Worker Card:

```text
┌──────────────────────────────────────┐
│                                      │
│  Worker #1                           │
│                                      │
│  Status: Running                     │
│  Queue: 20                           │
│  Completed: 100                      │
│                                      │
│  [ Pause ]     [ Stop ]              │
│                                      │
└──────────────────────────────────────┘
```

Code concept:

```python
ft.Card(
    content=ft.Container(
        padding=16,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("Worker #1"),
                ft.Text("Status: Running"),
                ft.Text("Queue: 20"),
                ft.Text("Completed: 100"),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Button("Pause"),
                        ft.Button("Stop"),
                    ],
                ),
            ],
        ),
    ),
)
```

Rất rõ ràng:

```text
Card
 ↓
padding
 ↓
Column spacing
 ↓
Row spacing
```

---

# 39. Book Card

Một Book Card:

```python
ft.Card(
    content=ft.Container(
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                cover,
                ft.Text("Naruto"),
                ft.Text("1200 chapters"),
                ft.Button("Read"),
            ],
        ),
    ),
)
```

Mental model:

```text
Card
│
└── Container
    │
    ├── padding=12
    │
    └── Column
        │
        └── spacing=8
```

---

# 40. Một câu hỏi quan trọng

Nếu bạn muốn:

```text
Card
│
│  16px
│
├── Image
│
│  8px
│
├── Title
│
│  8px
│
└── Button
```

thì dùng:

```text
Card
└── Container(padding=16)
    └── Column(spacing=8)
```

**Không cần**:

```text
Image.margin
Title.margin
Button.margin
```

Đây là cách layout sạch.

---

# 41. Khi nào margin thực sự hữu ích?

Margin phù hợp khi một component cần tạo khoảng cách **đặc biệt với bên ngoài**, không phải quy tắc chung của parent.

Ví dụ:

```text
Header

32px

Important notification

8px

Normal notification
```

Bạn có thể dùng margin cho notification đặc biệt.

Nhưng nếu tất cả:

```text
Notification
Notification
Notification
Notification
```

đều cách nhau 8px:

```python
Column(spacing=8)
```

thường tốt hơn.

---

# 42. Padding trong Button/Card/Input

Hãy phân biệt:

```text
Component internal spacing
```

với:

```text
spacing between components
```

Ví dụ Button:

```text
┌──────────────────┐
│      Save        │
└──────────────────┘
```

Khoảng cách:

```text
border → Save
```

là **internal padding** của component.

Còn:

```text
[Save]     [Cancel]
```

khoảng cách giữa hai Button:

```text
spacing
```

---

# 43. Nested containers

Ví dụ:

```text
Container
padding=24
│
└── Container
    padding=16
    │
    └── Text
```

Khoảng cách cuối cùng từ biên ngoài đến Text là tổng hợp nhiều lớp.

Vì vậy không nên lạm dụng nested Container chỉ để tạo khoảng cách.

Thường:

```text
Container
padding=24
└── Column
    spacing=16
```

sẽ đơn giản hơn.

---

# 44. Rule of Thumb

Hãy dùng quy tắc này:

### `spacing`

Khi:

```text
A
↓
B
↓
C
```

cần khoảng cách đồng đều.

---

### `padding`

Khi:

```text
Container
└── Content
```

cần khoảng cách từ biên đến content.

---

### `margin`

Khi:

```text
Component
```

cần tạo khoảng cách đặc biệt với bên ngoài.

---

# 45. Một pattern rất sạch

```python
def card(content):
    return ft.Card(
        content=ft.Container(
            padding=16,
            content=content,
        )
    )
```

Sau đó:

```python
card(
    ft.Column(
        spacing=8,
        controls=[
            title,
            description,
            button,
        ],
    )
)
```

Đây là bước đầu tiên để xây **UI component system**.

---

# 46. Bài tập 1 — Spacing Playground

Tạo:

```text
Column
├── A
├── B
└── C
```

Có Slider hoặc buttons:

```text
spacing = 0
spacing = 4
spacing = 8
spacing = 16
spacing = 32
```

Quan sát:

```text
A
B
C
```

thay đổi như thế nào.

---

# 47. Bài tập 2 — Padding Playground

Tạo:

```text
Container
└── Text("Hello")
```

Thử:

```text
padding = 0
padding = 8
padding = 16
padding = 32
```

Quan sát boundary.

---

# 48. Bài tập 3 — Box Model

Tạo:

```text
Container
├── margin
├── padding
└── Text
```

Dùng màu khác nhau:

```text
Parent
→ màu xanh

Container
→ màu vàng

Content
→ màu đỏ
```

Mục tiêu:

> Nhìn trực quan được margin và padding khác nhau.

---

# 49. Bài tập 4 — Book Card

Tạo:

```text
┌──────────────────────────────┐
│                              │
│           COVER              │
│                              │
│ Naruto                       │
│                              │
│ 1200 chapters                │
│                              │
│ [ Read ]                     │
│                              │
└──────────────────────────────┘
```

Yêu cầu:

```text
Card
 ↓
Container padding=16
 ↓
Column spacing=8
```

Không dùng margin cho từng Text.

---

# 50. Bài tập 5 — Worker Card

Tạo:

```text
┌──────────────────────────────┐
│ Worker #1                    │
│                              │
│ Status: Running              │
│ Queue: 20                    │
│ Completed: 120               │
│                              │
│ [Pause] [Stop]               │
└──────────────────────────────┘
```

Yêu cầu:

```text
Card
Container padding=16
Column spacing=10
Row spacing=8
```

---

# 51. Bài tập 6 — Dashboard

Xây:

```text
Dashboard
│
├── Header
│
├── Stats
│   ├── Card
│   ├── Card
│   └── Card
│
├── Recent Jobs
│
└── Workers
```

Quy tắc:

```text
Page padding = 24
Sections spacing = 24
Card padding = 16
Card content spacing = 8
Button spacing = 8
```

Bạn đang bắt đầu xây một **design system nhỏ** thay vì UI rời rạc.

---

# 52. Mini Project — Crawl Dashboard

Đây là bài tập rất sát với project crawl framework của bạn.

Thiết kế:

```text
┌────────────────────────────────────────────────┐
│ Crawl Dashboard                                │
│                                                │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│ │ Queue   │ │Running  │ │Completed│           │
│ │ 120     │ │5        │ │1,250    │           │
│ └─────────┘ └─────────┘ └─────────┘           │
│                                                │
│ Recent Jobs                                    │
│ ┌────────────────────────────────────────────┐ │
│ │ Naruto        Running                      │ │
│ ├────────────────────────────────────────────┤ │
│ │ One Piece     Completed                    │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Workers                                        │
│ ┌────────────────────────────────────────────┐ │
│ │ Worker #1                  Running          │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

Kiến trúc:

```text
Page
│
└── Container
    │
    ├── padding=24
    │
    └── Column
        │
        ├── spacing=24
        │
        ├── Header
        │
        ├── Row
        │   └── Cards
        │
        ├── Recent Jobs
        │
        └── Workers
```

---

# 53. Design System đầu tiên

Từ hôm nay, bạn có thể bắt đầu dùng:

```python
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

PAGE_PADDING = 24
CARD_PADDING = 16
```

Sau đó:

```python
page_content = ft.Container(
    expand=True,
    padding=PAGE_PADDING,
    content=ft.Column(
        spacing=SPACING_LG,
        controls=[
            header,
            stats,
            recent_jobs,
            workers,
        ],
    ),
)
```

Đây là tư duy rất gần với cách xây **design system trong ứng dụng thực tế**.

---

# 54. Tổng kết Buổi 22

Bạn cần nhớ:

```text
spacing
→ giữa siblings

padding
→ từ boundary đến content

margin
→ từ component đến bên ngoài
```

Mental model:

```text
┌──────────────────────────────┐
│           margin             │
│  ┌────────────────────────┐  │
│  │       padding          │  │
│  │   ┌───────────────┐    │  │
│  │   │    content    │    │  │
│  │   └───────────────┘    │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

Và:

```text
Row / Column
     ↓
  spacing
     ↓
child ↔ child
```

Quan trọng nhất:

> **Nếu khoảng cách là quy luật của một nhóm → dùng `spacing`.
> Nếu khoảng cách từ biên component vào nội dung → dùng `padding`.
> Nếu một component cần khoảng cách đặc biệt với bên ngoài → cân nhắc `margin`.**

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
21. Alignment                        ✅
22. Spacing / padding / margin       ✅
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

## Buổi 23 — Responsive UI

Đây là bước chuyển rất quan trọng:

```text
Desktop
     ↓
Laptop
     ↓
Tablet
     ↓
Mobile
```

Chúng ta sẽ học cách thiết kế một UI **không phụ thuộc vào kích thước màn hình cố định**, bao gồm:

```text
page.width
page.height
ResponsiveRow
GridView
adaptive layout
breakpoint
sidebar → drawer
desktop → mobile
card width
navigation
```

Đặc biệt chúng ta sẽ lấy chính **Book Library / Crawl Dashboard** làm ví dụ để chuyển từ **Desktop UI → Mobile UI**.
