# Buổi 11 — `Row` Deep Dive

Hôm nay bắt đầu **Giai đoạn II — Layout Deep Dive**.

`Row` nhìn rất đơn giản:

```python
ft.Row(...)
```

nhưng khi xây UI thực tế, `Row` liên quan trực tiếp đến:

```text
width
alignment
spacing
expand
responsive layout
constraints
overflow
nested layout
```

Nếu hiểu `Row` sâu, bạn sẽ hiểu được một phần rất lớn cách Flet bố trí UI.

---

# 1. `Row` là gì?

`Row` là control dùng để bố trí các control con **theo chiều ngang**.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("Hello"),
        ft.Button("OK"),
    ]
)
```

UI:

```text
┌─────────────────────────────┐
│ Hello       [ OK ]          │
└─────────────────────────────┘
```

Mental model:

```text
Row
│
├── Child 1
├── Child 2
├── Child 3
└── Child 4
```

Các child được sắp xếp:

```text
→ → → →
```

---

# 2. `Row` không phải một "hàng HTML"

Nếu bạn từng học CSS, đừng đồng nhất:

```python
ft.Row()
```

với:

```css
display: flex;
flex-direction: row;
```

Concept tương tự, nhưng Flet có hệ thống layout/control riêng.

Hãy nghĩ:

```text
Row
=
Horizontal Layout Container
```

---

# 3. Ví dụ cơ bản

```python
import flet as ft


def main(page: ft.Page):

    page.add(
        ft.Row(
            controls=[
                ft.Text("Python"),
                ft.Text("Flet"),
                ft.Button("Learn"),
            ]
        )
    )


ft.run(main)
```

Kết quả conceptually:

```text
Python    Flet    [Learn]
```

---

# 4. `controls`

Cấu trúc cơ bản:

```python
ft.Row(
    controls=[
        control_1,
        control_2,
        control_3,
    ]
)
```

`controls` là danh sách các child control.

Ví dụ:

```python
row = ft.Row()

row.controls.append(
    ft.Text("Hello")
)

row.controls.append(
    ft.Button("Click")
)
```

---

# 5. UI Tree

Ví dụ:

```python
row = ft.Row(
    controls=[
        ft.Text("Hello"),
        ft.Button("Click"),
    ]
)
```

Tree:

```text
Row
├── Text
└── Button
```

Nếu:

```python
page.add(row)
```

thì:

```text
Page
└── Row
    ├── Text
    └── Button
```

Đây chính là UI Tree mà bạn đã học ở Giai đoạn I.

---

# 6. `Row` có kích thước bao nhiêu?

Đây là điểm bắt đầu của Layout Deep Dive.

Một câu hỏi quan trọng:

> Row rộng bao nhiêu?

Câu trả lời không đơn giản là:

```text
width = tổng width của children
```

`Row` phải được layout trong **constraints từ parent**.

Mental model:

```text
Parent
  │
  │ constraints
  ▼
 Row
  │
  ├── Child
  ├── Child
  └── Child
```

Parent quyết định giới hạn không gian mà Row có thể sử dụng.

---

# 7. `Row` mặc định

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ]
)
```

Các control được đặt cạnh nhau.

Conceptually:

```text
A B C
```

---

# 8. `spacing`

`spacing` tạo khoảng cách giữa các child.

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
    spacing=20,
)
```

Conceptually:

```text
A        B        C
```

Nếu:

```python
spacing=0
```

thì:

```text
ABC
```

---

# 9. `spacing` khác `padding`

Đây là distinction cực kỳ quan trọng.

## `spacing`

Khoảng cách **giữa children**:

```text
A ← spacing → B
```

## `padding`

Khoảng cách **giữa nội dung và biên container**:

```text
┌─────────────────────────┐
│   padding               │
│     A    B              │
│                         │
└─────────────────────────┘
```

Không nên dùng `spacing` để giải quyết vấn đề padding.

---

# 10. `alignment`

`Row` có:

```python
alignment=...
```

để điều chỉnh vị trí của children trên **trục chính**.

Vì Row chạy ngang:

```text
Main Axis
──────────────────────────→
```

Do đó `alignment` chủ yếu điều khiển vị trí theo chiều ngang.

---

# 11. `MainAxisAlignment`

Các giá trị thường gặp:

```python
ft.MainAxisAlignment.START
ft.MainAxisAlignment.CENTER
ft.MainAxisAlignment.END
ft.MainAxisAlignment.SPACE_BETWEEN
ft.MainAxisAlignment.SPACE_AROUND
ft.MainAxisAlignment.SPACE_EVENLY
```

---

# 12. `START`

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
    ],
    alignment=ft.MainAxisAlignment.START,
)
```

Concept:

```text
A B
```

Children bắt đầu từ đầu Row.

---

# 13. `CENTER`

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Concept:

```text
       A B
```

Nếu Row rộng:

```text
┌──────────────────────────────┐
│           A B                │
└──────────────────────────────┘
```

---

# 14. `END`

```python
alignment=ft.MainAxisAlignment.END
```

Concept:

```text
              A B
```

---

# 15. `SPACE_BETWEEN`

Đây là một giá trị cực kỳ hữu ích.

```python
ft.Row(
    controls=[
        ft.Text("Logo"),
        ft.Text("Profile"),
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
)
```

Concept:

```text
Logo                         Profile
```

Khoảng trống được phân phối **giữa children**.

---

# 16. `SPACE_AROUND`

```python
alignment=ft.MainAxisAlignment.SPACE_AROUND
```

Concept:

```text
    A          B          C
```

Mỗi child có khoảng trống xung quanh.

---

# 17. `SPACE_EVENLY`

```python
alignment=ft.MainAxisAlignment.SPACE_EVENLY
```

Concept:

```text
    A       B       C
```

Khoảng cách giữa:

```text
edge → A
A → B
B → C
C → edge
```

được phân phối đều.

---

# 18. So sánh

Giả sử Row rộng 600:

```text
START

A B C
```

```text
CENTER

          A B C
```

```text
END

                    A B C
```

```text
SPACE_BETWEEN

A                  B                  C
```

```text
SPACE_EVENLY

      A             B             C
```

---

# 19. `vertical_alignment`

Vì Row chạy theo chiều ngang, ta còn có **cross axis**:

```text
          Cross Axis
              ↓
              │
              │
──────────────┼──────────────→
              │   Main Axis
```

Để điều khiển vị trí theo chiều dọc:

```python
vertical_alignment=...
```

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("Hello"),
        ft.Button("Button"),
    ],
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
)
```

---

# 20. Cross Axis

Row:

```text
Main Axis
──────────────────────→
```

Cross Axis:

```text
        ↓
        │
        │
        │
```

Do đó:

```text
Row
│
├── Main Axis → horizontal
└── Cross Axis ↓ vertical
```

Đây là một trong những concept quan trọng nhất của layout.

---

# 21. `CrossAxisAlignment.START`

```python
vertical_alignment=ft.CrossAxisAlignment.START
```

Children nằm phía trên.

```text
┌───────────────────────────┐
│ A    B    C               │
│                           │
│                           │
└───────────────────────────┘
```

---

# 22. `CENTER`

```python
vertical_alignment=ft.CrossAxisAlignment.CENTER
```

```text
┌───────────────────────────┐
│                           │
│ A    B    C               │
│                           │
└───────────────────────────┘
```

---

# 23. `END`

```python
vertical_alignment=ft.CrossAxisAlignment.END
```

```text
┌───────────────────────────┐
│                           │
│                           │
│ A    B    C               │
└───────────────────────────┘
```

---

# 24. Đây là quy tắc cần nhớ

Đối với:

```python
Row
```

thì:

```text
Main Axis
→ horizontal
```

```text
Cross Axis
→ vertical
```

Do đó:

```python
alignment
```

→ horizontal.

```python
vertical_alignment
```

→ vertical.

---

# 25. Ví dụ Header thực tế

Một header thường có:

```text
Logo                         User
```

Ta viết:

```python
header = ft.Row(
    controls=[
        ft.Text("My App"),
        ft.Text("User"),
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
)
```

Đây là một trong những pattern Row phổ biến nhất.

---

# 26. Header phức tạp

```text
┌─────────────────────────────────────────┐
│ My App       Home  About  Settings   👤 │
└─────────────────────────────────────────┘
```

Có thể:

```python
header = ft.Row(
    controls=[
        ft.Text("My App"),

        ft.Row(
            controls=[
                ft.TextButton("Home"),
                ft.TextButton("About"),
                ft.TextButton("Settings"),
            ],
            spacing=10,
        ),

        ft.IconButton(
            icon=ft.Icons.PERSON,
        ),
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
)
```

Bạn vừa sử dụng:

```text
Row
 ├── Text
 ├── Row
 │   ├── Button
 │   ├── Button
 │   └── Button
 └── IconButton
```

---

# 27. Nested Row

Row có thể chứa Row:

```python
ft.Row(
    controls=[
        ft.Text("Left"),

        ft.Row(
            controls=[
                ft.Text("A"),
                ft.Text("B"),
            ]
        ),
    ]
)
```

Tree:

```text
Row
├── Text
└── Row
    ├── Text
    └── Text
```

Đây là điều cực kỳ phổ biến.

---

# 28. Nhưng nested Row quá nhiều sẽ thành vấn đề

Ví dụ:

```text
Row
 └── Row
      └── Row
           └── Row
                └── Row
```

Code bắt đầu khó đọc.

Khi đó nên tạo component:

```python
def build_actions():
    return ft.Row(...)
```

thay vì nhồi mọi thứ vào một expression.

---

# 29. `expand`

Đây là phần quan trọng.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.TextField(),
        ft.Button("Search"),
    ]
)
```

Bạn muốn TextField chiếm phần không gian còn lại.

Có thể:

```python
ft.TextField(
    expand=True,
)
```

Concept:

```text
┌───────────────────────────────────────┐
│ Search......................... [Go]   │
└───────────────────────────────────────┘
```

TextField mở rộng.

---

# 30. `expand` nghĩa là gì?

Trong Row:

```python
expand=True
```

nói rằng control có thể tham gia vào việc **chiếm không gian còn lại** theo cơ chế flex/expand của Flet.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.TextField(expand=True),
        ft.Button("Search"),
    ]
)
```

Button giữ kích thước cần thiết.

TextField nhận phần còn lại.

---

# 31. Nhiều `expand`

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(expand=1),
        ft.Container(expand=2),
        ft.Container(expand=1),
    ]
)
```

Concept:

```text
┌────────┬────────────────┬────────┐
│        │                │        │
│   1    │       2        │   1    │
│        │                │        │
└────────┴────────────────┴────────┘
```

Tỷ lệ:

```text
1 : 2 : 1
```

---

# 32. `expand=1` vs `expand=2`

Điểm này rất quan trọng.

Giả sử available width:

```text
800
```

Có:

```python
expand=1
expand=2
expand=1
```

Tổng:

```text
1 + 2 + 1 = 4
```

Tỷ lệ:

```text
1/4
2/4
1/4
```

Concept:

```text
200 + 400 + 200
```

---

# 33. `expand=True`

Có thể hiểu:

```python
expand=True
```

là một dạng yêu cầu control tham gia vào việc expand.

Nhưng khi bạn cần **chia tỷ lệ rõ ràng**, dùng:

```python
expand=1
expand=2
```

sẽ diễn đạt ý đồ layout tốt hơn.

---

# 34. Search Bar thực tế

Pattern cực phổ biến:

```python
search_bar = ft.Row(
    controls=[
        ft.TextField(
            hint_text="Search...",
            expand=True,
        ),
        ft.Button("Search"),
    ],
)
```

Đây là pattern bạn sẽ sử dụng rất nhiều.

---

# 35. Button group

```python
actions = ft.Row(
    controls=[
        ft.Button("Save"),
        ft.Button("Cancel"),
    ],
    spacing=10,
)
```

Concept:

```text
[ Save ]  [ Cancel ]
```

---

# 36. Form

```python
form = ft.Row(
    controls=[
        ft.TextField(
            label="Name",
            expand=True,
        ),
        ft.TextField(
            label="Age",
            width=100,
        ),
        ft.Button("Save"),
    ]
)
```

Concept:

```text
┌─────────────────────────────────────────────┐
│ Name................ │ Age │ [ Save ]       │
└─────────────────────────────────────────────┘
```

---

# 37. `wrap`

Một vấn đề:

```text
A B C D E F G H
```

Nếu màn hình nhỏ:

```text
A B C D E F G H
        ↓
   overflow
```

Trong một số trường hợp bạn muốn child tự xuống dòng.

Flet có hỗ trợ cơ chế `wrap` cho Row:

```python
ft.Row(
    controls=[...],
    wrap=True,
)
```

Concept:

```text
A B C D
E F G H
```

---

# 38. `run_spacing`

Khi `wrap=True`, bạn có thể cần khoảng cách giữa các dòng.

```python
ft.Row(
    controls=[...],
    wrap=True,
    spacing=10,
    run_spacing=10,
)
```

Phân biệt:

```text
spacing
→ khoảng cách giữa children trong cùng run

run_spacing
→ khoảng cách giữa các dòng
```

---

# 39. Ví dụ tag UI

```python
tags = ft.Row(
    controls=[
        ft.Container(
            content=ft.Text("Python"),
            padding=10,
        ),
        ft.Container(
            content=ft.Text("Flet"),
            padding=10,
        ),
        ft.Container(
            content=ft.Text("Async"),
            padding=10,
        ),
    ],
    wrap=True,
    spacing=8,
    run_spacing=8,
)
```

Khi màn hình nhỏ:

```text
Python   Flet   Async
```

có thể thành:

```text
Python   Flet
Async
```

---

# 40. `scroll`

Một Row có nhiều child có thể cần scrolling.

Flet hỗ trợ scroll behavior cho các layout control phù hợp.

Mental model:

```text
Row
│
├── A
├── B
├── C
├── D
├── E
└── ...
```

Nếu không đủ không gian:

```text
viewport
    ↓
[A B C D]
```

thì scroll có thể được sử dụng.

Nhưng với danh sách dài, `ListView` thường là lựa chọn tốt hơn — chúng ta sẽ học ở **Buổi 17**.

---

# 41. `Row` và `ListView`

Không nên dùng:

```python
ft.Row(
    controls=[
        # 10,000 controls
    ]
)
```

để xây một danh sách dữ liệu dài.

Nếu cần:

```text
horizontal scrolling
```

thì Row có thể phù hợp.

Nhưng nếu là:

```text
data list
chat messages
todos
logs
```

hãy nghĩ đến:

```python
ft.ListView(...)
```

---

# 42. `Row` và `Column`

Đây là cặp control quan trọng nhất trong Flet.

```text
Row
→ horizontal
```

```text
Column
↓ vertical
```

Ví dụ:

```text
Column
│
├── Row
│   ├── A
│   └── B
│
├── Row
│   ├── C
│   └── D
│
└── Row
    ├── E
    └── F
```

Đây chính là cách xây rất nhiều UI.

---

# 43. Form với Row + Column

```python
form = ft.Column(
    controls=[
        ft.Row(
            controls=[
                ft.TextField(
                    label="First name",
                    expand=True,
                ),
                ft.TextField(
                    label="Last name",
                    expand=True,
                ),
            ]
        ),

        ft.Row(
            controls=[
                ft.TextField(
                    label="Email",
                    expand=True,
                ),
                ft.Button("Submit"),
            ]
        ),
    ],
    spacing=15,
)
```

Tree:

```text
Column
├── Row
│   ├── TextField
│   └── TextField
│
└── Row
    ├── TextField
    └── Button
```

---

# 44. Row + Container

Ví dụ card header:

```python
header = ft.Container(
    content=ft.Row(
        controls=[
            ft.Text("Dashboard"),
            ft.Button("Refresh"),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    ),
    padding=15,
)
```

`Container` đảm nhiệm:

```text
padding
background
border
border radius
```

Còn Row:

```text
horizontal arrangement
```

Đây là separation of concerns rất tốt.

---

# 45. Đừng dùng Row để làm mọi thứ

Ví dụ bạn muốn:

```text
      Hello
      World
```

Không nên:

```python
ft.Row(...)
```

Hãy dùng:

```python
ft.Column(...)
```

Tư duy:

```text
Ngang → Row
Dọc → Column
```

---

# 46. `Row` và `alignment`

Hãy nhớ:

```python
alignment=ft.MainAxisAlignment.CENTER
```

không có nghĩa:

> căn giữa toàn bộ control theo cả hai chiều.

Nó chỉ tác động đến **main axis**.

Để căn giữa theo cross axis:

```python
vertical_alignment=ft.CrossAxisAlignment.CENTER
```

---

# 47. Muốn căn giữa hoàn toàn

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("Hello"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
)
```

Nhưng để thấy hiệu quả, Row phải có đủ không gian.

Đây chính là vấn đề:

> **Constraints**

Chúng ta sẽ học sâu ở Buổi 20.

---

# 48. Tại sao `alignment=CENTER` đôi khi "không hoạt động"?

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("Hello"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Bạn thấy:

```text
Hello
```

vẫn ở đầu?

Có thể vì Row không có đủ **extra width** để phân phối.

Nếu Row chỉ rộng đúng bằng child:

```text
Row width ≈ child width
```

thì:

```text
CENTER
```

không có khoảng trống để thể hiện.

Đây là một trong những lỗi layout phổ biến nhất.

---

# 49. Muốn Row full width

Bạn có thể cần:

```python
ft.Row(
    controls=[
        ...
    ],
    expand=True,
)
```

hoặc đặt Row trong parent có kích thước phù hợp.

Mental model:

```text
Parent width = 800

Row width = 800

children width = 200

remaining = 600

CENTER
→ remaining space distributed
```

---

# 50. `expand=True` là một concept cực quan trọng

Ví dụ:

```python
row = ft.Row(
    controls=[
        ft.Text("Hello"),
    ],
    expand=True,
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Concept:

```text
┌─────────────────────────────────┐
│                                 │
│             Hello               │
│                                 │
└─────────────────────────────────┘
```

Row chiếm không gian được phép.

Sau đó:

```text
alignment=CENTER
```

mới có không gian để hoạt động.

---

# 51. `expand` của Row và `expand` của Child khác nhau

Đây là điểm rất quan trọng.

## Row expand

```python
ft.Row(
    expand=True,
)
```

→ Row muốn chiếm thêm không gian từ parent.

## Child expand

```python
ft.Row(
    controls=[
        ft.TextField(expand=True),
        ft.Button("Go"),
    ]
)
```

→ TextField muốn chiếm phần không gian còn lại trong Row.

Hai cấp khác nhau:

```text
Parent
 ↓
Row expand
 ↓
Child expand
```

---

# 52. Ví dụ dễ nhầm

```python
ft.Row(
    controls=[
        ft.Text("Hello"),
    ],
    expand=True,
)
```

Không có nghĩa:

```text
Text tự động full width
```

Chỉ có:

```text
Row full available space
```

Muốn child expand:

```python
ft.Row(
    controls=[
        ft.Text(
            "Hello",
            expand=True,
        ),
    ]
)
```

hoặc dùng control/layout phù hợp.

---

# 53. `Row` trong Dashboard

Sau này ở Mini Project Dashboard:

```text
┌─────────────────────────────────────────────┐
│ Revenue       Users       Orders      Sales │
└─────────────────────────────────────────────┘
```

Ta có thể dùng:

```python
ft.Row(
    controls=[
        stat_card_1,
        stat_card_2,
        stat_card_3,
        stat_card_4,
    ],
    spacing=15,
)
```

Nếu responsive:

```python
ft.Row(
    controls=[
        ...
    ],
    wrap=True,
)
```

Hoặc sau này:

```python
ft.ResponsiveRow(...)
```

---

# 54. Row trong Navigation

Ví dụ:

```text
[☰]  My Application             [🔔] [👤]
```

```python
app_bar = ft.Row(
    controls=[
        ft.IconButton(
            icon=ft.Icons.MENU,
        ),

        ft.Text(
            "My Application",
            expand=True,
        ),

        ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS,
        ),

        ft.IconButton(
            icon=ft.Icons.PERSON,
        ),
    ],
)
```

Đây là pattern cực kỳ thực tế.

---

# 55. Tại sao `Text(expand=True)` hữu ích?

Giả sử:

```text
[☰]  Title                         [🔔] [👤]
```

Nếu:

```python
title = ft.Text(
    "My Application",
    expand=True,
)
```

Title chiếm phần còn lại:

```text
Menu
 ↓
Title ← remaining space
 ↓
Notification
 ↓
Profile
```

Đây là một pattern layout rất quan trọng.

---

# 56. `Row` + `expand` = Flexbox mindset

Hãy bắt đầu suy nghĩ:

```text
Fixed
+
Flexible
+
Flexible
+
Fixed
```

Ví dụ:

```python
ft.Row(
    controls=[
        ft.IconButton(...),    # fixed
        ft.TextField(
            expand=True        # flexible
        ),
        ft.Button("Search"),   # fixed
    ]
)
```

Layout:

```text
┌────┬────────────────────────────┬─────────┐
│ 🔍 │ Search.................... │ Search  │
└────┴────────────────────────────┴─────────┘
```

---

# 57. Row với tỷ lệ

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Container(expand=1),
        ft.Container(expand=3),
    ]
)
```

Concept:

```text
25%                  75%
┌─────────┬─────────────────────────────┐
│         │                             │
│    1    │             3               │
│         │                             │
└─────────┴─────────────────────────────┘
```

Đây là nền tảng để xây:

```text
Sidebar + Content
```

---

# 58. Sidebar

Ví dụ:

```python
layout = ft.Row(
    controls=[
        ft.Container(
            width=250,
            content=sidebar,
        ),

        ft.Container(
            expand=True,
            content=content,
        ),
    ]
)
```

Concept:

```text
┌──────────┬─────────────────────────────┐
│ Sidebar  │                             │
│          │ Content                     │
│          │                             │
│          │                             │
└──────────┴─────────────────────────────┘
    250px             flexible
```

Đây là pattern chúng ta sẽ sử dụng rất nhiều ở các project Flet sau này.

---

# 59. Một quy tắc layout cực kỳ hữu ích

Khi thiết kế Row, hãy hỏi:

### 1.

Control nào có kích thước cố định?

```text
Icon
Button
Avatar
```

### 2.

Control nào cần ăn phần còn lại?

```text
TextField
Text
Content
```

### 3.

Control nào cần chia theo tỷ lệ?

```text
Sidebar
Main
```

Sau đó chọn:

```text
width
expand
expand=n
```

---

# 60. Debug Row

Khi Row không hiển thị như mong muốn, kiểm tra theo thứ tự:

```text
1. Parent có đủ width không?
2. Row có đủ width không?
3. Child có width cố định không?
4. Child có expand không?
5. alignment đang tác động axis nào?
6. spacing có quá lớn không?
7. Có overflow không?
8. wrap có cần không?
```

Đừng sửa layout bằng cách thêm:

```python
width=999
```

một cách ngẫu nhiên.

---

# 61. Bài tập thực hành 1 — Header

Tạo:

```text
┌────────────────────────────────────────────┐
│ My App              Home About     [User] │
└────────────────────────────────────────────┘
```

Yêu cầu:

* `Row`
* `SPACE_BETWEEN`
* nested `Row`
* `spacing`

---

# 62. Bài tập 2 — Search Bar

Tạo:

```text
┌─────────────────────────────────────┐
│ Search..................... [Search] │
└─────────────────────────────────────┘
```

Yêu cầu:

```python
ft.TextField(expand=True)
```

Button không expand.

---

# 63. Bài tập 3 — Toolbar

Tạo:

```text
[ New ] [ Edit ] [ Delete ]             [ Refresh ]
```

Gợi ý:

```python
ft.Row(
    controls=[
        ft.Row(
            controls=[
                ...
            ]
        ),

        ft.Button("Refresh"),
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
)
```

---

# 64. Bài tập 4 — Sidebar

Tạo:

```text
┌──────────────┬────────────────────────────┐
│ Dashboard    │                            │
│ Users        │       Main Content         │
│ Settings     │                            │
│              │                            │
└──────────────┴────────────────────────────┘
```

Gợi ý:

```python
ft.Row(
    controls=[
        ft.Container(
            width=220,
            content=sidebar,
        ),
        ft.Container(
            expand=True,
            content=content,
        ),
    ]
)
```

---

# 65. Bài tập 5 — Responsive Tags

Tạo:

```text
Python   Flet   Async   SQLite   Docker
```

Khi màn hình nhỏ:

```text
Python   Flet
Async    SQLite
Docker
```

Sử dụng:

```python
wrap=True
spacing=...
run_spacing=...
```

---

# 66. Bài tập 6 — Deep Dive `expand`

Tạo layout:

```text
┌────────┬──────────────────────┬────────┐
│  1/4   │         1/2          │  1/4   │
└────────┴──────────────────────┴────────┘
```

Sử dụng:

```python
expand=1
expand=2
expand=1
```

Không dùng:

```python
width=200
width=400
width=200
```

Mục tiêu là hiểu **flexible sizing**.

---

# 67. Bài tập 7 — Debug

Viết:

```python
row = ft.Row(
    controls=[
        ft.Text("Hello"),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
)
```

Sau đó giải thích tại sao trong một số trường hợp bạn không thấy:

```text
Hello
```

nằm giữa màn hình.

Sau đó sửa bằng cách làm cho Row có đủ không gian.

Đây là bài tập quan trọng nhất hôm nay.

---

# 68. Cheat Sheet

## Basic

```python
ft.Row(
    controls=[...],
)
```

## Spacing

```python
spacing=10
```

## Main axis

```python
alignment=ft.MainAxisAlignment.CENTER
```

## Cross axis

```python
vertical_alignment=ft.CrossAxisAlignment.CENTER
```

## Flexible Row

```python
expand=True
```

## Flexible child

```python
ft.TextField(expand=True)
```

## Ratio

```python
expand=1
expand=2
```

## Wrapping

```python
wrap=True
```

## Gap between wrapped runs

```python
run_spacing=10
```

---

# 69. Mental Model cần nhớ

Đừng học thuộc API một cách rời rạc.

Hãy nhìn `Row` như sau:

```text
                     Parent
                       │
                  Constraints
                       │
                       ▼
                     Row
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
      Child A       Child B       Child C
         │             │             │
         └─────────────┼─────────────┘
                       │
                 Main Axis →
                       │
                 Cross Axis ↓
```

Sau đó:

```text
alignment
    ↓
Main Axis

vertical_alignment
    ↓
Cross Axis

spacing
    ↓
between children

expand
    ↓
consume available space

wrap
    ↓
move children to next line
```

Đây là kiến thức cốt lõi của `Row`.

---

# 70. Kết nối với Todo App vừa học

Todo App ở Buổi 10 có đoạn:

```python
ft.Row(
    controls=[
        checkbox,
        delete_button,
    ],
)
```

Bây giờ chúng ta có thể hiểu sâu hơn.

Ta có thể viết:

```python
ft.Row(
    controls=[
        ft.Checkbox(
            label=todo.title,
            value=todo.completed,
            expand=True,
        ),
        ft.Button("Delete"),
    ],
    spacing=10,
)
```

Kết quả:

```text
┌──────────────────────────────────────────────┐
│ ☐ Learn Flet......................... [Delete]│
└──────────────────────────────────────────────┘
```

Đây chính là:

```text
Checkbox → flexible
Button   → fixed
```

**Bạn đã bắt đầu chuyển từ "biết dùng `Row`" sang "biết thiết kế layout bằng `Row`".**

Buổi tiếp theo là **Buổi 12 — `Column` Deep Dive**, trong đó chúng ta sẽ đào sâu chiều dọc, `alignment`, `horizontal_alignment`, `expand`, scroll, nested `Column`, form layout và cách kết hợp `Row + Column` để xây giao diện ứng dụng thực tế.
