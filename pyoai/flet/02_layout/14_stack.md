# Buổi 14 — `Stack` Deep Dive

Hôm nay chúng ta học **`Stack`** — control dùng để **xếp nhiều control chồng lên nhau**.

Nếu `Row` và `Column` giải quyết:

```text
Row    → trái → phải
Column → trên → dưới
```

thì:

```text
Stack → trước → sau / chồng lớp
```

Đây là control cực kỳ quan trọng khi xây UI hiện đại.

---

# 1. Stack là gì?

Hãy hình dung:

```text
Layer 3
┌───────────────┐
│     Badge     │
└───────────────┘

Layer 2
┌─────────────────────┐
│       Text          │
└─────────────────────┘

Layer 1
┌───────────────────────────┐
│          Image            │
└───────────────────────────┘
```

Các control không nằm cạnh nhau.

Chúng **đè lên nhau**.

Trong Flet:

```python
ft.Stack(
    controls=[
        ...,
        ...,
        ...,
    ]
)
```

---

# 2. Mental model

Nếu:

```python
ft.Column(
    controls=[
        A,
        B,
        C,
    ]
)
```

thì:

```text
A

B

C
```

Nếu:

```python
ft.Row(
    controls=[
        A,
        B,
        C,
    ]
)
```

thì:

```text
A B C
```

Còn:

```python
ft.Stack(
    controls=[
        A,
        B,
        C,
    ]
)
```

thì:

```text
┌──────────────┐
│ C            │
│   B          │
│     A        │
└──────────────┘
```

Tức là các layer nằm **trên cùng một vùng**.

---

# 3. UI Tree

Ví dụ:

```python
ft.Stack(
    controls=[
        ft.Container(...),
        ft.Text(...),
    ]
)
```

Tree:

```text
Stack
├── Container
└── Text
```

Điểm quan trọng:

> `Stack` không phải là một `Container` có nhiều children.

Nó là một **layout control** quản lý các children theo kiểu xếp lớp.

---

# 4. Ví dụ đầu tiên

```python
import flet as ft


def main(page: ft.Page):
    page.add(
        ft.Stack(
            controls=[
                ft.Container(
                    width=300,
                    height=200,
                    bgcolor=ft.Colors.BLUE,
                ),
                ft.Text("Hello"),
            ],
        )
    )


ft.run(main)
```

Concept:

```text
┌──────────────────────────────┐
│ Hello                        │
│                              │
│                              │
└──────────────────────────────┘
```

`Text` nằm trên `Container`.

---

# 5. Thứ tự controls rất quan trọng

Ví dụ:

```python
ft.Stack(
    controls=[
        background,
        text,
        badge,
    ]
)
```

Thông thường mental model:

```text
background
    ↓
text
    ↓
badge
```

Control phía sau trong danh sách được đặt ở **layer phía trên**.

Vì vậy:

```python
controls=[
    image,
    overlay,
    badge,
]
```

có nghĩa:

```text
badge
overlay
image
```

theo thứ tự từ trên xuống dưới.

---

# 6. Stack giống Photoshop Layers

Bạn có thể tư duy:

```text
Stack
│
├── Layer 0 → background
├── Layer 1 → image
├── Layer 2 → overlay
├── Layer 3 → text
└── Layer 4 → badge
```

Đây là mental model rất mạnh.

Ví dụ một card:

```text
Layer 0
Background

Layer 1
Image

Layer 2
Dark overlay

Layer 3
Title

Layer 4
Badge
```

---

# 7. Use case đầu tiên: Image + Text

```python
ft.Stack(
    controls=[
        ft.Image(
            src="https://example.com/image.jpg",
            width=300,
            height=200,
        ),
        ft.Container(
            content=ft.Text("Python"),
            padding=10,
        ),
    ]
)
```

Concept:

```text
┌─────────────────────────────┐
│                             │
│          IMAGE              │
│                             │
│ Python                      │
└─────────────────────────────┘
```

Text nằm trên image.

---

# 8. Overlay

Một pattern rất phổ biến:

```text
Image
  +
semi-transparent overlay
  +
Text
```

Tree:

```text
Stack
├── Image
├── Container → overlay
└── Text
```

Ví dụ:

```python
ft.Stack(
    controls=[
        ft.Image(
            src="image.jpg",
            width=400,
            height=250,
        ),

        ft.Container(
            width=400,
            height=250,
            bgcolor=ft.Colors.BLACK54,
        ),

        ft.Text(
            "Chapter 123",
        ),
    ]
)
```

Concept:

```text
┌───────────────────────────────┐
│                               │
│       dark overlay            │
│                               │
│       Chapter 123             │
│                               │
└───────────────────────────────┘
```

---

# 9. Tại sao cần `Container` trong Stack?

Một câu hỏi quan trọng.

Ta có:

```python
ft.Container(
    width=400,
    height=250,
    bgcolor=...
)
```

Container đóng vai trò:

```text
Overlay layer
```

Trong khi:

```python
ft.Stack(...)
```

đóng vai trò:

```text
Layer manager
```

Phân chia trách nhiệm:

```text
Stack
  ↓
xếp lớp

Container
  ↓
vẽ một lớp
```

---

# 10. `alignment`

Stack có thể căn các children.

Ví dụ:

```python
ft.Stack(
    controls=[
        image,
        ft.Text("Hello"),
    ],
    alignment=ft.alignment.center,
)
```

Text sẽ được căn giữa vùng Stack.

Concept:

```text
┌──────────────────────────┐
│                          │
│          Hello           │
│                          │
└──────────────────────────┘
```

---

# 11. Alignment của Stack

Một số alignment thường dùng:

```python
ft.alignment.top_left
ft.alignment.top_center
ft.alignment.top_right

ft.alignment.center_left
ft.alignment.center
ft.alignment.center_right

ft.alignment.bottom_left
ft.alignment.bottom_center
ft.alignment.bottom_right
```

Ví dụ:

```python
alignment=ft.alignment.bottom_right
```

thường dùng cho:

```text
image
             ┌──────┐
             │Badge │
             └──────┘
```

---

# 12. Stack + Container

Một pattern rất phổ biến:

```python
ft.Container(
    width=300,
    height=200,
    content=ft.Stack(
        controls=[
            ...
        ]
    )
)
```

Tree:

```text
Container
└── Stack
    ├── Image
    ├── Overlay
    └── Text
```

Container bên ngoài chịu trách nhiệm:

```text
size
border
radius
padding
```

Stack chịu trách nhiệm:

```text
layering
```

---

# 13. Avatar + Badge

Đây là một ví dụ rất thực tế.

```text
       ┌──────────────┐
       │              │
       │    Avatar    │
       │              │
       │          ●   │
       └──────────────┘
```

Tree:

```text
Stack
├── Avatar
└── Badge
```

Ví dụ:

```python
ft.Stack(
    width=80,
    height=80,
    controls=[
        ft.CircleAvatar(
            radius=35,
        ),
        ft.Container(
            width=16,
            height=16,
            bgcolor=ft.Colors.GREEN,
            border_radius=8,
        ),
    ],
    alignment=ft.alignment.bottom_right,
)
```

Badge:

```text
●
```

nằm ở góc avatar.

---

# 14. Notification Badge

Một pattern khác:

```text
┌─────────────┐
│ 🔔       ●3 │
└─────────────┘
```

Tree:

```text
Stack
├── Icon
└── Badge
```

Ví dụ:

```python
ft.Stack(
    controls=[
        ft.Icon(
            ft.Icons.NOTIFICATIONS,
            size=30,
        ),
        ft.Container(
            content=ft.Text(
                "3",
                size=10,
            ),
            width=18,
            height=18,
            border_radius=9,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.RED,
        ),
    ],
    alignment=ft.alignment.top_right,
)
```

---

# 15. Badge có position

Khi cần kiểm soát vị trí chính xác, Stack hỗ trợ cơ chế positioning thông qua `Stack`/`Positioned`.

Pattern:

```python
ft.Stack(
    controls=[
        background,
        ft.Positioned(
            child=badge,
            right=10,
            top=10,
        ),
    ]
)
```

Mental model:

```text
Stack
│
├── background
│
└── Positioned
    └── badge
```

---

# 16. `Positioned` là gì?

`Positioned` cho phép bạn nói:

```text
top
right
bottom
left
```

thay vì chỉ:

```text
alignment
```

Ví dụ:

```python
ft.Positioned(
    child=ft.Text("Hello"),
    left=20,
    top=10,
)
```

Concept:

```text
┌──────────────────────────┐
│   Hello                  │
│                          │
│                          │
└──────────────────────────┘
```

---

# 17. Position bằng `left`

```python
ft.Positioned(
    child=badge,
    left=10,
)
```

Nghĩa:

```text
Stack
┌──────────────────────────┐
│ badge                    │
│                          │
└──────────────────────────┘
```

---

# 18. Position bằng `right`

```python
ft.Positioned(
    child=badge,
    right=10,
)
```

```text
┌──────────────────────────┐
│                    badge │
└──────────────────────────┘
```

---

# 19. Position bằng `top`

```python
ft.Positioned(
    child=badge,
    top=10,
)
```

```text
┌──────────────────────────┐
│ badge                    │
│                          │
│                          │
└──────────────────────────┘
```

---

# 20. Position bằng `bottom`

```python
ft.Positioned(
    child=badge,
    bottom=10,
)
```

```text
┌──────────────────────────┐
│                          │
│                          │
│ badge                    │
└──────────────────────────┘
```

---

# 21. Kết hợp top + right

Đây là pattern cực phổ biến:

```python
ft.Positioned(
    child=badge,
    top=10,
    right=10,
)
```

```text
┌──────────────────────────┐
│                    ●     │
│                          │
│                          │
└──────────────────────────┘
```

---

# 22. Kết hợp left + bottom

```python
ft.Positioned(
    child=label,
    left=20,
    bottom=20,
)
```

```text
┌──────────────────────────┐
│                          │
│                          │
│   Label                  │
└──────────────────────────┘
```

---

# 23. Position không chỉ là decoration

Bạn có thể xây UI hoàn chỉnh:

```text
┌─────────────────────────────┐
│                    [NEW]    │
│                             │
│         Book Cover          │
│                             │
│                             │
│ Chapter 120                 │
│                         >   │
└─────────────────────────────┘
```

Tree:

```text
Stack
├── Image
├── Positioned → NEW
├── Positioned → Chapter
└── Positioned → Arrow
```

---

# 24. `Stack` + `clip_behavior`

Một vấn đề thường gặp:

```text
child vượt ra ngoài Stack
```

Bạn có thể kiểm soát clipping bằng:

```python
clip_behavior=...
```

Mental model:

```text
Stack boundary
┌───────────────────┐
│ child             │
│             ──────┼──→ overflow
└───────────────────┘
```

Clipping quyết định phần vượt ra ngoài có bị cắt hay không.

---

# 25. Stack và border radius

Một vấn đề thực tế:

```text
Container
└── Stack
    └── Image
```

Container có:

```python
border_radius=20
```

nhưng image có thể không tự động bị cắt theo radius trong mọi trường hợp.

Khi muốn card ảnh có góc bo đẹp, cần chú ý:

```text
border radius
+
clip behavior
```

Đây là một lỗi UI khá phổ biến.

---

# 26. Stack + Image Card

Hãy xây một card truyện:

```text
┌─────────────────────────────┐
│                             │
│          COVER              │
│                             │
│                         ●   │
│                             │
│ Chapter 123                 │
└─────────────────────────────┘
```

Code:

```python
def book_card():
    return ft.Container(
        width=220,
        height=300,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Stack(
            controls=[
                ft.Image(
                    src="cover.jpg",
                    width=220,
                    height=300,
                    fit=ft.BoxFit.COVER,
                ),

                ft.Container(
                    width=220,
                    height=300,
                    bgcolor=ft.Colors.BLACK54,
                ),

                ft.Positioned(
                    child=ft.Text(
                        "Chapter 123",
                        size=18,
                    ),
                    left=15,
                    bottom=15,
                ),
            ],
        ),
    )
```

Đây là pattern rất gần với ứng dụng đọc truyện của bạn.

---

# 27. Layered UI

Stack rất phù hợp với:

```text
Image
Overlay
Text
Badge
Button
Icon
```

Ví dụ:

```text
Stack
│
├── Image
│
├── Gradient/Overlay
│
├── Title
│
├── Badge
│
└── Button
```

Đây là cách xây:

* movie card
* book card
* product card
* profile header
* hero banner

---

# 28. Hero Banner

Ví dụ:

```text
┌─────────────────────────────────────────┐
│                                         │
│       Background Image                  │
│                                         │
│       Python Deep Dive                  │
│       Learn advanced Python             │
│                                         │
│                         [Start]         │
└─────────────────────────────────────────┘
```

Tree:

```text
Stack
├── Image
├── Overlay
├── Column
│   ├── Title
│   └── Description
└── Button
```

---

# 29. Stack + Column

Một layer có thể chứa cả `Column`.

```python
ft.Stack(
    controls=[
        background,
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Python"),
                    ft.Text("Advanced Programming"),
                    ft.Button("Learn"),
                ]
            ),
            padding=20,
        ),
    ]
)
```

Tree:

```text
Stack
├── Background
└── Container
    └── Column
        ├── Text
        ├── Text
        └── Button
```

Đây là composition rất mạnh.

---

# 30. Stack không thay thế Row / Column

Sai tư duy:

> "Stack mạnh hơn nên dùng Stack cho mọi thứ."

Không.

Nếu UI là:

```text
A
B
C
```

hãy dùng:

```python
Column
```

Nếu:

```text
A B C
```

hãy dùng:

```python
Row
```

Nếu:

```text
A
  B
    C
```

hoặc các control **chồng lớp**, dùng:

```python
Stack
```

---

# 31. So sánh

| Control      | Mục đích               |
| ------------ | ---------------------- |
| `Row`        | layout ngang           |
| `Column`     | layout dọc             |
| `Container`  | box / decoration       |
| `Stack`      | layering               |
| `Positioned` | đặt vị trí trong Stack |

Mental model:

```text
Row
 └── A B C

Column
 └── A
     B
     C

Stack
 └── A
   ┌──B──┐
   │ C   │
   └─────┘
```

---

# 32. Stack + responsive

Một điểm rất quan trọng:

Đừng hard-code quá nhiều:

```python
left=123
top=47
```

Nếu màn hình thay đổi:

```text
desktop
tablet
mobile
```

UI có thể vỡ.

Nên ưu tiên:

```text
alignment
relative sizing
responsive layout
```

và chỉ dùng `Positioned` khi vị trí tương đối thực sự cần thiết.

---

# 33. Stack trong Dashboard

Một dashboard card có thể có:

```text
┌──────────────────────────┐
│ Sales               📈   │
│                          │
│ $12,430                  │
│                          │
│ +12%                ●    │
└──────────────────────────┘
```

Tree:

```text
Stack
├── Container
├── Column
└── Positioned
```

---

# 34. Stack trong app cào truyện

Ví dụ book card:

```text
┌─────────────────────────┐
│              Completed  │
│                         │
│          COVER          │
│                         │
│                         │
│ One Piece               │
│ Chapter 1234            │
└─────────────────────────┘
```

Tree:

```text
Stack
├── Cover
├── Status Badge
├── Overlay
└── Book Information
```

Bạn sẽ dùng pattern này rất nhiều trong app đọc truyện.

---

# 35. Stack trong TTS App

Có thể dùng Stack cho:

```text
Text editor
     +
loading overlay
```

Ví dụ:

```text
┌─────────────────────────────┐
│ Text                        │
│                             │
│ Converting...               │
│                             │
│             ◌               │
└─────────────────────────────┘
```

Tree:

```text
Stack
├── TextField
└── Loading Overlay
```

Khi loading:

```text
overlay.visible = True
```

Khi hoàn thành:

```text
overlay.visible = False
```

Đây là một pattern UI cực kỳ hữu ích.

---

# 36. Loading Overlay

Ví dụ kiến trúc:

```python
loading_overlay = ft.Container(
    bgcolor=ft.Colors.BLACK54,
    content=ft.ProgressRing(),
    alignment=ft.alignment.center,
)

editor = ft.TextField(
    multiline=True,
)

root = ft.Stack(
    controls=[
        editor,
        loading_overlay,
    ]
)
```

Khi loading:

```python
loading_overlay.visible = True
```

Khi xong:

```python
loading_overlay.visible = False
```

---

# 37. Modal-like overlay

Bạn cũng có thể xây:

```text
Stack
├── Main Content
└── Overlay
    └── Dialog
```

Concept:

```text
┌────────────────────────────────┐
│ Main application               │
│                                │
│      ┌──────────────────┐      │
│      │     Dialog       │      │
│      │                  │      │
│      └──────────────────┘      │
│                                │
└────────────────────────────────┘
```

Tuy nhiên với dialog thực sự, nên cân nhắc control/dialog chuyên dụng của Flet thay vì tự xây mọi thứ bằng Stack.

---

# 38. Stack và z-order

Một khái niệm quan trọng:

```text
z-order
```

Hiểu đơn giản:

```text
z = độ sâu
```

Ví dụ:

```text
z=0 → background
z=1 → overlay
z=2 → text
z=3 → button
```

Trong Stack, thứ tự children quyết định layer.

Mental model:

```text
controls[0]
    ↓
bottom layer

controls[1]
    ↓
middle

controls[-1]
    ↓
top layer
```

---

# 39. Debug Stack

Khi Stack hiển thị sai, kiểm tra:

### 1. Thứ tự controls

```python
controls=[
    background,
    text,
]
```

hay:

```python
controls=[
    text,
    background,
]
```

### 2. Kích thước

```text
Stack có width/height hợp lý chưa?
```

### 3. Position

```text
top/right/bottom/left
```

### 4. Alignment

```text
alignment
```

### 5. Clipping

```text
clip_behavior
```

---

# 40. Một lỗi tư duy phổ biến

Bạn viết:

```python
ft.Stack(
    controls=[
        ft.Text("Hello"),
        ft.Text("World"),
    ]
)
```

và mong:

```text
Hello
World
```

Nhưng Stack không phải Column.

Nó có thể khiến hai Text nằm cùng vùng.

Nếu muốn:

```text
Hello
World
```

hãy dùng:

```python
ft.Column(
    controls=[
        ft.Text("Hello"),
        ft.Text("World"),
    ]
)
```

---

# 41. Một lỗi khác: Stack không có kích thước

Ví dụ bạn tạo:

```python
ft.Stack(
    controls=[
        ...
    ]
)
```

nhưng parent không cấp đủ constraints.

Khi đó bạn có thể gặp layout không như mong muốn.

Trong những UI quan trọng, hãy hiểu:

```text
Parent
 ↓
constraints
 ↓
Stack size
 ↓
children
```

Đây sẽ liên kết trực tiếp với **Buổi 20 — Layout Constraints và Sizing**.

---

# 42. Component `Badge`

Hãy đóng gói:

```python
def badge(text):
    return ft.Container(
        content=ft.Text(
            text,
            size=11,
        ),
        padding=ft.Padding.symmetric(
            horizontal=8,
            vertical=4,
        ),
        border_radius=20,
        bgcolor=ft.Colors.BLUE,
    )
```

Sau đó:

```python
ft.Stack(
    controls=[
        image,
        ft.Positioned(
            child=badge("NEW"),
            top=10,
            right=10,
        ),
    ]
)
```

Đây là cách bắt đầu xây reusable components.

---

# 43. Component `ImageCard`

```python
def image_card(image_src, title):
    return ft.Container(
        width=250,
        height=180,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Stack(
            controls=[
                ft.Image(
                    src=image_src,
                    width=250,
                    height=180,
                    fit=ft.BoxFit.COVER,
                ),

                ft.Container(
                    width=250,
                    height=180,
                    bgcolor=ft.Colors.BLACK54,
                ),

                ft.Positioned(
                    child=ft.Text(
                        title,
                        size=20,
                    ),
                    left=15,
                    bottom=15,
                ),
            ],
        ),
    )
```

Dùng:

```python
ft.Row(
    controls=[
        image_card("a.jpg", "Python"),
        image_card("b.jpg", "Rust"),
        image_card("c.jpg", "Flet"),
    ]
)
```

---

# 44. Bài tập thực hành 1 — Avatar

Tạo:

```text
       ┌──────────────┐
       │              │
       │    Avatar    │
       │              │
       │           ●  │
       └──────────────┘
```

Yêu cầu:

* `Stack`
* Avatar
* status badge
* `Positioned`
* `border_radius`

---

# 45. Bài tập thực hành 2 — Book Card

Tạo:

```text
┌─────────────────────────┐
│                  NEW    │
│                         │
│        COVER            │
│                         │
│                         │
│ One Piece               │
│ Chapter 1234            │
└─────────────────────────┘
```

Yêu cầu:

```text
Stack
Image
Container overlay
Positioned badge
Positioned title
```

---

# 46. Bài tập thực hành 3 — Loading Overlay

Tạo:

```text
┌─────────────────────────────┐
│                             │
│        Text Editor          │
│                             │
│       ┌──────────┐          │
│       │    ◌     │          │
│       │ Loading  │          │
│       └──────────┘          │
│                             │
└─────────────────────────────┘
```

Có:

```text
TextField
+
Stack
+
overlay
+
ProgressRing
```

Sau đó tạo Button:

```text
Start
```

để:

```text
visible = True
```

và sau một khoảng thời gian:

```text
visible = False
```

Bài này rất tốt cho việc hiểu **state + UI layering**.

---

# 47. Bài tập thực hành 4 — Hero Banner

Xây:

```text
┌──────────────────────────────────────────┐
│                                          │
│   Background Image                       │
│                                          │
│   Python Deep Dive                       │
│   Master Python internals                │
│                                          │
│                         [Start Learning] │
└──────────────────────────────────────────┘
```

Cấu trúc:

```text
Container
└── Stack
    ├── Image
    ├── Overlay
    └── Container
        └── Column
            ├── Text
            ├── Text
            └── Button
```

Nếu làm được bài này, bạn đã hiểu khá tốt `Stack`.

---

# 48. Tổng kết `Stack`

Hãy nhớ 6 thứ:

```text
Stack
│
├── controls
│      ↓
│   layers
│
├── alignment
│      ↓
│   căn layer
│
├── Positioned
│      ↓
│   vị trí cụ thể
│
├── z-order
│      ↓
│   layer trước/sau
│
├── clip_behavior
│      ↓
│   cắt overflow
│
└── constraints
       ↓
    kích thước Stack
```

---

# 49. So sánh 4 control đã học

Sau Buổi 14, hãy ghi nhớ:

```text
Row
→ horizontal layout

Column
→ vertical layout

Container
→ box / decoration / wrapper

Stack
→ layered layout
```

Ví dụ UI phức tạp:

```text
Container
└── Stack
    ├── Image
    ├── Container
    │   └── overlay
    ├── Column
    │   ├── Text
    │   └── Text
    └── Positioned
        └── Badge
```

Đây chính là **composition** trong Flet.

---

# 50. Bài tập tổng hợp

Hãy tự xây một **Book Card Component**:

```text
┌─────────────────────────────┐
│                     NEW     │
│                             │
│                             │
│          BOOK COVER         │
│                             │
│                             │
│                             │
│ One Piece                   │
│ Chapter 1234                │
│                             │
└─────────────────────────────┘
```

API mong muốn:

```python
BookCard(
    title="One Piece",
    chapter="Chapter 1234",
    image_url="...",
    badge="NEW",
)
```

Bên trong:

```text
Container
└── Stack
    ├── Image
    ├── Overlay
    ├── Positioned → Badge
    └── Positioned → Info
```

**Đừng copy code hoàn chỉnh từ đâu cả.** Hãy tự thiết kế UI Tree trước, sau đó mới code.

---

## Roadmap tiếp theo

Bạn đang ở:

```text
11. Row Deep Dive          ✅
12. Column Deep Dive       ✅
13. Container Deep Dive    ✅
14. Stack                  ← hiện tại
15. ResponsiveRow
16. GridView
17. ListView
18. Tabs
19. Card / ExpansionTile / ListTile
20. Layout Constraints
21. Alignment
22. Spacing / Padding / Margin
23. Responsive UI
24. Theme
25. Dark / Light Mode
26. Mini Project: Dashboard
```

**Buổi 15 — `ResponsiveRow` Deep Dive** sẽ rất quan trọng: chúng ta sẽ học cách chia màn hình theo kiểu **12-column grid**, tạo layout kiểu Bootstrap, sidebar/main-content, desktop/tablet/mobile và hiểu tại sao `Row` thông thường không đủ tốt cho responsive UI.
