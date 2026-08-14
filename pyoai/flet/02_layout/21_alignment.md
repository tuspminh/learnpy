# Buổi 21 — Alignment Deep Dive trong Flet

Hôm nay chúng ta học **Alignment** thật sâu.

Nếu `Row`, `Column`, `Container` là những thứ tạo ra layout, thì `Alignment` quyết định:

> **"Đặt child ở đâu trong vùng không gian mà parent đã cấp?"**

Đây là điểm rất quan trọng vì nhiều người mới học thường nhầm:

```text
width / height
        ↓
kích thước

alignment
        ↓
vị trí bên trong kích thước đó
```

---

# 1. Alignment là gì?

Giả sử bạn có một vùng:

```text
┌──────────────────────────────┐
│                              │
│            Hello             │
│                              │
└──────────────────────────────┘
```

Vùng ngoài có:

```text
width  = 500
height = 300
```

Text chỉ cần:

```text
width  ≈ 50
height ≈ 30
```

Alignment quyết định Text nằm:

```text
trái
giữa
phải
trên
giữa
dưới
```

---

# 2. Có 2 loại Alignment quan trọng

Trong Flet, bạn cần phân biệt:

```text
1. Alignment của Row / Column
2. Alignment của Container
```

Ngoài ra còn có:

```text
3. MainAxisAlignment
4. CrossAxisAlignment
```

Đây là phần dễ nhầm nhất.

---

# 3. Main Axis và Cross Axis

Đây là kiến thức nền tảng.

## Row

`Row` chạy theo chiều ngang:

```text
        Main Axis
→ → → → → → → → →

┌─────────────────────────────┐
│ A     B     C               │
└─────────────────────────────┘
```

Vì vậy:

```text
Row
main axis   = horizontal
cross axis  = vertical
```

---

# 4. Column

`Column` chạy theo chiều dọc:

```text
Main Axis
   ↓
   ↓
   A
   ↓
   B
   ↓
   C
```

Vì vậy:

```text
Column
main axis   = vertical
cross axis  = horizontal
```

---

# 5. Quy tắc vàng

Hãy nhớ:

```text
Row
    Main  → ngang
    Cross → dọc

Column
    Main  → dọc
    Cross → ngang
```

Chỉ cần nhớ điều này, bạn sẽ hiểu phần lớn Alignment.

---

# 6. `MainAxisAlignment`

`MainAxisAlignment` quyết định:

> Các child được phân bố như thế nào trên **main axis**.

Ví dụ:

```python
ft.Row(
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
    alignment=ft.MainAxisAlignment.START,
)
```

---

# 7. `START`

```python
ft.Row(
    alignment=ft.MainAxisAlignment.START,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

UI:

```text
┌──────────────────────────────┐
│ A B C                        │
└──────────────────────────────┘
```

Các item nằm đầu main axis.

Với `Row`:

```text
START = trái
```

Với `Column`:

```text
START = trên
```

---

# 8. `CENTER`

```python
ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

UI:

```text
┌──────────────────────────────┐
│          A B C               │
└──────────────────────────────┘
```

Với Row:

```text
CENTER = giữa ngang
```

Với Column:

```text
CENTER = giữa dọc
```

---

# 9. `END`

```python
ft.Row(
    alignment=ft.MainAxisAlignment.END,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

UI:

```text
┌──────────────────────────────┐
│                   A B C      │
└──────────────────────────────┘
```

Với Row:

```text
END = phải
```

Với Column:

```text
END = dưới
```

---

# 10. `SPACE_BETWEEN`

Đây là một trong những alignment quan trọng nhất.

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

UI:

```text
┌──────────────────────────────┐
│ A            B            C  │
└──────────────────────────────┘
```

Khoảng trống được chia **giữa các child**.

Không có khoảng trống dư ở hai đầu.

---

# 11. `SPACE_AROUND`

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_AROUND,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

Concept:

```text
┌──────────────────────────────┐
│   A       B       C          │
└──────────────────────────────┘
```

Mỗi item có khoảng trống xung quanh.

---

# 12. `SPACE_EVENLY`

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

Concept:

```text
┌──────────────────────────────┐
│    A      B      C           │
└──────────────────────────────┘
```

Khoảng cách giữa:

```text
start → A
A → B
B → C
C → end
```

được chia đều.

---

# 13. So sánh ba loại Space

Hãy nhớ:

### `SPACE_BETWEEN`

```text
| A        B        C |
```

Khoảng trống **giữa** item.

---

### `SPACE_AROUND`

```text
|  A      B      C  |
```

Mỗi item có khoảng trống hai bên.

---

### `SPACE_EVENLY`

```text
|   A    B    C   |
```

Tất cả khoảng cách đều nhau.

---

# 14. Visual comparison

```text
START

|ABC                    |
```

```text
CENTER

|        ABC            |
```

```text
END

|                    ABC|
```

```text
SPACE_BETWEEN

|A          B          C|
```

```text
SPACE_AROUND

|  A      B      C      |
```

```text
SPACE_EVENLY

|    A     B     C      |
```

Đây là bảng bạn nên nhớ.

---

# 15. `CrossAxisAlignment`

Bây giờ chuyển sang cross axis.

Ví dụ:

```python
ft.Column(
    horizontal_alignment=...,
)
```

Trong Flet, bạn sẽ gặp các thuộc tính alignment tương ứng với cách control sắp xếp child theo trục còn lại.

Mental model:

```text
MainAxisAlignment
→ phân bố child theo hướng chính

CrossAxisAlignment
→ căn child theo hướng vuông góc
```

---

# 16. Row: Cross Axis là dọc

Ví dụ:

```text
Row
──────────────────────────→ Main

Cross
  ↓
```

Vì vậy cross alignment quyết định:

```text
top
center
bottom
```

Ví dụ concept:

```text
┌────────────────────────────┐
│ A                          │
│                            │
│ B                          │
│                            │
│ C                          │
└────────────────────────────┘
```

---

# 17. Column: Cross Axis là ngang

```text
Column

Main
 ↓

Cross → → →
```

Cross alignment quyết định:

```text
left
center
right
```

Ví dụ:

```text
┌──────────────────────┐
│ A                    │
│      B               │
│            C         │
└──────────────────────┘
```

---

# 18. Một cách nhớ cực dễ

```text
Main
→ "Các item nằm cách nhau thế nào?"

Cross
→ "Các item được căn về phía nào?"
```

Ví dụ Row:

```text
Main
→ A     B     C

Cross
↓
A
B
C
```

---

# 19. `Row` + MainAxisAlignment

```python
ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Container(width=100),
        ft.Container(width=100),
        ft.Container(width=100),
    ],
)
```

Kết quả:

```text
┌────────────────────────────────────┐
│           [100][100][100]          │
└────────────────────────────────────┘
```

Main axis đang được center.

---

# 20. `Column` + MainAxisAlignment

```python
ft.Column(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

Kết quả:

```text
┌────────────────────┐
│                    │
│        A           │
│        B           │
│        C           │
│                    │
└────────────────────┘
```

Ở Column:

```text
Main axis = vertical
```

nên `CENTER` đưa nhóm item vào giữa theo chiều dọc.

---

# 21. `Column` + horizontal alignment

Ví dụ concept:

```python
ft.Column(
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
        ft.Text("C"),
    ],
)
```

Kết quả:

```text
┌────────────────────┐
│        A           │
│        B           │
│        C           │
└────────────────────┘
```

Tất cả child được căn giữa theo chiều ngang.

---

# 22. `Column` + START

```python
ft.Column(
    horizontal_alignment=ft.CrossAxisAlignment.START,
    controls=[
        ft.Text("A"),
        ft.Text("Long text"),
        ft.Text("C"),
    ],
)
```

Concept:

```text
┌────────────────────┐
│ A                  │
│ Long text          │
│ C                  │
└────────────────────┘
```

---

# 23. `Column` + CENTER

```python
ft.Column(
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    controls=[
        ft.Text("A"),
        ft.Text("Long text"),
        ft.Text("C"),
    ],
)
```

Concept:

```text
┌────────────────────┐
│        A           │
│     Long text      │
│        C           │
└────────────────────┘
```

---

# 24. `Column` + END

```python
ft.Column(
    horizontal_alignment=ft.CrossAxisAlignment.END,
    controls=[
        ft.Text("A"),
        ft.Text("Long text"),
        ft.Text("C"),
    ],
)
```

Concept:

```text
┌────────────────────┐
│                  A │
│          Long text │
│                  C │
└────────────────────┘
```

---

# 25. `Row` + vertical alignment

Tương tự, Row có thể căn child theo chiều dọc.

Concept:

```text
Row
│
├── Main → horizontal
│
└── Cross → vertical
```

Bạn có thể hình dung:

```text
┌──────────────────────────────┐
│                              │
│ A       B       C            │
│                              │
└──────────────────────────────┘
```

hoặc:

```text
┌──────────────────────────────┐
│ A       B       C            │
│                              │
│                              │
└──────────────────────────────┘
```

Tùy cross-axis alignment.

---

# 26. Alignment của `Container`

Bây giờ là một loại alignment khác.

Ví dụ:

```python
ft.Container(
    width=500,
    height=300,
    alignment=ft.Alignment.CENTER,
    content=ft.Text("Hello"),
)
```

Ở đây:

```text
Container
│
├── có kích thước 500 × 300
│
└── Text
    alignment = center
```

Kết quả:

```text
┌──────────────────────────────┐
│                              │
│            Hello             │
│                              │
└──────────────────────────────┘
```

---

# 27. Đây là điểm cực kỳ quan trọng

So sánh:

```text
Row/Column alignment
```

với:

```text
Container alignment
```

### Row / Column

Căn:

```text
nhiều children
```

### Container

Căn:

```text
content bên trong Container
```

---

# 28. Ví dụ dễ nhầm

```python
ft.Container(
    width=500,
    height=300,
    alignment=ft.Alignment.CENTER,
    content=ft.Text("Hello"),
)
```

Container đang nói:

> "Text nằm giữa tôi."

Còn:

```python
ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Text("A"),
        ft.Text("B"),
    ],
)
```

Row đang nói:

> "Nhóm A + B nằm giữa Row."

---

# 29. Hai cấp alignment

Bạn có thể kết hợp:

```text
Row
└── Container
    └── Text
```

Row:

```text
căn Container
```

Container:

```text
căn Text
```

Ví dụ:

```text
┌────────────────────────────────────┐
│                                    │
│          ┌──────────────┐          │
│          │    Hello     │          │
│          └──────────────┘          │
│                                    │
└────────────────────────────────────┘
```

Đây là **nested alignment**.

---

# 30. Alignment + expand

Đây là phần cực kỳ quan trọng.

Nếu Container:

```python
ft.Container(
    expand=True,
    alignment=ft.Alignment.CENTER,
    content=ft.Text("Hello"),
)
```

thì:

```text
expand
→ Container chiếm toàn bộ không gian

alignment
→ Text nằm giữa Container
```

UI:

```text
┌──────────────────────────────┐
│                              │
│            Hello             │
│                              │
└──────────────────────────────┘
```

Hai thuộc tính có **hai nhiệm vụ khác nhau**.

---

# 31. `expand` + alignment

Hãy ghi nhớ:

```text
expand
↓
"vùng của tôi rộng bao nhiêu?"

alignment
↓
"content của tôi nằm ở đâu?"
```

Ví dụ:

```python
ft.Container(
    expand=True,
    alignment=ft.Alignment.CENTER,
)
```

---

# 32. Đây là pattern rất phổ biến cho Loading

```python
ft.Container(
    expand=True,
    alignment=ft.Alignment.CENTER,
    content=ft.ProgressRing(),
)
```

UI:

```text
┌──────────────────────────────┐
│                              │
│             ◌                │
│                              │
└──────────────────────────────┘
```

---

# 33. Empty State

Ví dụ:

```python
ft.Container(
    expand=True,
    alignment=ft.Alignment.CENTER,
    content=ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.INBOX),
            ft.Text("No books found"),
        ],
    ),
)
```

Tree:

```text
Container
│
└── Column
    ├── Icon
    └── Text
```

Container:

```text
center group
```

Column:

```text
center children
```

Đây là một pattern rất đẹp.

---

# 34. App cào truyện — Empty Queue

Bạn có thể làm:

```text
┌────────────────────────────────────┐
│                                    │
│                 📥                 │
│                                    │
│            Queue empty             │
│                                    │
│          [ Add Job ]               │
│                                    │
└────────────────────────────────────┘
```

Tree:

```text
Container(expand=True)
│
└── Column
    │
    ├── Icon
    ├── Text
    └── Button
```

Container:

```text
alignment = CENTER
```

Column:

```text
horizontal_alignment = CENTER
```

---

# 35. `SPACE_BETWEEN` cho Header

Pattern cực kỳ phổ biến:

```text
┌────────────────────────────────────┐
│ Logo                 Search  User  │
└────────────────────────────────────┘
```

Dùng:

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    controls=[
        logo,
        ft.Row(
            controls=[
                search,
                user,
            ]
        ),
    ],
)
```

Mental model:

```text
Row
├── Logo
└── Right group
```

---

# 36. Tại sao không nên dùng `SPACE_BETWEEN` cho mọi thứ?

Ví dụ:

```text
Button  Button  Button
```

Nếu bạn muốn khoảng cách cố định:

```text
[Save] [Cancel] [Delete]
```

thì `spacing` thường rõ ràng hơn:

```python
ft.Row(
    spacing=10,
    controls=[
        save_button,
        cancel_button,
        delete_button,
    ],
)
```

Đây là điều chúng ta sẽ học kỹ hơn ở **Buổi 22**.

---

# 37. Alignment + spacing

Hãy phân biệt:

```text
alignment
→ phân bố toàn bộ nhóm

spacing
→ khoảng cách giữa từng child
```

Ví dụ:

```text
START + spacing=10
```

cho:

```text
| A   B   C                     |
```

Còn:

```text
SPACE_BETWEEN
```

cho:

```text
| A          B          C       |
```

---

# 38. Alignment + padding

Padding là:

```text
khoảng cách từ boundary vào content
```

Ví dụ:

```text
┌───────────────────────────┐
│    ┌───────────────────┐  │
│    │       Hello       │  │
│    └───────────────────┘  │
└───────────────────────────┘
```

Alignment:

```text
Hello nằm ở đâu
```

Padding:

```text
Hello cách biên bao nhiêu
```

---

# 39. Một ví dụ tổng hợp

```python
ft.Container(
    expand=True,
    padding=20,
    alignment=ft.Alignment.CENTER,
    content=ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.Icon(ft.Icons.MENU_BOOK),
            ft.Text("No chapters"),
            ft.Button("Reload"),
        ],
    ),
)
```

Mỗi thuộc tính có nhiệm vụ:

```text
expand
→ Container chiếm không gian

padding
→ tạo khoảng cách với biên

alignment
→ Column nằm giữa Container

horizontal_alignment
→ children nằm giữa Column

spacing
→ khoảng cách giữa children
```

Đây chính là tư duy layout chuyên nghiệp.

---

# 40. Một lỗi tư duy phổ biến

Người mới thường làm:

```python
ft.Container(
    width=500,
    height=500,
    padding=100,
)
```

rồi:

```python
ft.Container(
    width=300,
    height=300,
)
```

rồi tiếp tục chỉnh:

```text
width=420
height=270
padding=17
margin=13
```

để "ép" UI vào đúng vị trí.

Đây là dấu hiệu đang **hack layout**.

Tư duy đúng:

```text
1. Parent size?
2. Child size?
3. Main axis?
4. Cross axis?
5. Alignment?
6. Spacing?
7. Padding?
```

---

# 41. Pattern Sidebar + Content

Một layout rất quan trọng:

```text
┌──────────────┬─────────────────────────┐
│ Sidebar      │ Content                 │
│              │                         │
│              │                         │
└──────────────┴─────────────────────────┘
```

Code concept:

```python
ft.Row(
    expand=True,
    controls=[
        ft.Container(
            width=250,
            content=sidebar,
        ),
        ft.Container(
            expand=True,
            content=content,
        ),
    ],
)
```

Ở đây:

```text
Row
main axis
→ Sidebar + Content

Content
expand=True
→ lấy phần còn lại
```

---

# 42. Header với nhóm trái/phải

```text
┌────────────────────────────────────────┐
│ Logo             Search      Settings  │
└────────────────────────────────────────┘
```

Tree:

```text
Row
├── Logo
└── Row
    ├── Search
    └── Settings
```

Dùng:

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    controls=[
        logo,
        ft.Row(
            spacing=10,
            controls=[
                search,
                settings,
            ],
        ),
    ],
)
```

Đây là pattern bạn sẽ dùng liên tục.

---

# 43. Reader app

Với app đọc truyện:

```text
┌────────────────────────────────────────────┐
│ ← Chapter 120                 ☰ Settings  │
├────────────────────────────────────────────┤
│                                            │
│                 CONTENT                    │
│                                            │
└────────────────────────────────────────────┘
```

Header:

```python
ft.Row(
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    controls=[
        back_button,
        chapter_title,
        settings_button,
    ],
)
```

Nhưng nếu title cần nằm **chính giữa màn hình tuyệt đối**, `SPACE_BETWEEN` chưa chắc đủ.

Đó là lúc bạn cần hiểu sâu hơn về:

```text
Stack
```

và:

```text
expand
```

để thiết kế header chính xác.

---

# 44. Alignment không thay thế Stack

Ví dụ:

```text
←               Chapter 120              ⚙
```

Nếu bạn muốn:

```text
Chapter 120
```

luôn ở giữa màn hình, bất kể hai bên có độ dài khác nhau, đôi khi `Row` + `SPACE_BETWEEN` không đảm bảo điều đó.

Có thể cần:

```text
Stack
├── left
├── center
└── right
```

Đây là lý do Buổi 14 về `Stack` rất quan trọng.

---

# 45. Alignment trong `Card`

Ví dụ Book Card:

```text
┌─────────────────────┐
│                     │
│        COVER        │
│                     │
│       Naruto        │
│     1200 chapters   │
└─────────────────────┘
```

Bạn có thể:

```text
Card
└── Column
    ├── Image
    ├── Text
    └── Text
```

và:

```python
horizontal_alignment=ft.CrossAxisAlignment.CENTER
```

để căn nội dung theo chiều ngang.

---

# 46. Alignment trong Grid Item

Ví dụ:

```text
┌───────────────┐
│               │
│     Cover     │
│               │
│    Naruto     │
│               │
└───────────────┘
```

Tree:

```text
Card
└── Column
    ├── Image
    └── Text
```

Column:

```python
horizontal_alignment=ft.CrossAxisAlignment.CENTER
```

---

# 47. Alignment trong Form

Ví dụ:

```text
┌─────────────────────────────┐
│        Login                │
│                             │
│  Username                   │
│  [____________________]     │
│                             │
│  Password                   │
│  [____________________]     │
│                             │
│        [ Login ]            │
└─────────────────────────────┘
```

Một pattern:

```text
Container
└── Column
    ├── Text
    ├── TextField
    ├── TextField
    └── Button
```

Có thể:

```python
horizontal_alignment=ft.CrossAxisAlignment.CENTER
```

nhưng form field lại cần width cố định:

```python
width=350
```

Đây là:

```text
alignment
+
fixed width
```

---

# 48. Alignment và Constraints kết hợp

Buổi 20:

```text
Constraints
→ child được phép có kích thước nào?
```

Buổi 21:

```text
Alignment
→ child nằm ở đâu trong vùng đó?
```

Hai thứ kết hợp:

```text
Constraints
      ↓
┌─────────────────────────┐
│                         │
│        Alignment        │
│           ↓             │
│         Child           │
│                         │
└─────────────────────────┘
```

Đây là mental model bạn nên giữ.

---

# 49. Bài tập 1 — Alignment Playground

Tạo app:

```text
Alignment Playground
```

Có 6 button:

```text
START
CENTER
END
SPACE_BETWEEN
SPACE_AROUND
SPACE_EVENLY
```

Khi click mỗi button, thay đổi:

```python
row.alignment = ...
page.update()
```

Mục tiêu:

```text
thấy trực tiếp sự khác nhau
```

---

# 50. Bài tập 2 — Row Playground

Tạo:

```text
Row
├── A
├── B
└── C
```

Thử:

```text
START
CENTER
END
SPACE_BETWEEN
SPACE_AROUND
SPACE_EVENLY
```

Sau đó thay đổi:

```text
spacing
```

và quan sát.

---

# 51. Bài tập 3 — Column Playground

Tạo:

```text
Column
├── A
├── B
└── C
```

Thử:

```text
MainAxisAlignment:
START
CENTER
END
SPACE_BETWEEN
SPACE_AROUND
SPACE_EVENLY
```

Sau đó thử:

```text
CrossAxisAlignment:
START
CENTER
END
```

Mục tiêu là nhìn ra ngay:

```text
Main = dọc
Cross = ngang
```

---

# 52. Bài tập 4 — Empty State

Xây:

```text
┌─────────────────────────────┐
│                             │
│            📚               │
│                             │
│      No books found         │
│                             │
│       [ Add Book ]          │
│                             │
└─────────────────────────────┘
```

Yêu cầu:

```text
Container(expand=True)
    ↓
alignment=CENTER
    ↓
Column
    ↓
horizontal_alignment=CENTER
```

Đây là bài tập rất tốt để hiểu nested alignment.

---

# 53. Bài tập 5 — Header

Tạo:

```text
┌────────────────────────────────────────┐
│ ☰  Book Library      🔍    ⚙           │
└────────────────────────────────────────┘
```

Dùng:

```text
Row
├── left group
└── right group
```

với:

```python
MainAxisAlignment.SPACE_BETWEEN
```

---

# 54. Bài tập 6 — Crawl Worker

Tạo:

```text
┌─────────────────────────────────────────┐
│ Worker #1                Running        │
│                                         │
│ Queue: 20             Completed: 120   │
│                                         │
│              [ Pause ]                  │
└─────────────────────────────────────────┘
```

Sử dụng:

```text
Card
└── Column
    ├── Row
    ├── Row
    └── Button
```

Áp dụng:

```text
SPACE_BETWEEN
CENTER
spacing
```

---

# 55. Mini Project — Book Detail Header

Xây:

```text
┌──────────────────────────────────────────────┐
│ ←       Naruto — Chapter 120              ☰ │
└──────────────────────────────────────────────┘
```

Sau đó thử hai cách:

### Cách 1

```text
Row
SPACE_BETWEEN
```

### Cách 2

```text
Stack
├── Back
├── Center title
└── Menu
```

So sánh kết quả.

Bạn sẽ thấy một điều rất quan trọng:

> **Không phải mọi vấn đề căn chỉnh đều nên giải quyết bằng `MainAxisAlignment`.**

---

# 56. Tổng kết

Hôm nay bạn cần nắm chắc:

```text
Row
├── Main Axis      → horizontal
└── Cross Axis     → vertical

Column
├── Main Axis      → vertical
└── Cross Axis     → horizontal
```

`MainAxisAlignment`:

```text
START
CENTER
END
SPACE_BETWEEN
SPACE_AROUND
SPACE_EVENLY
```

`CrossAxisAlignment`:

```text
START
CENTER
END
```

`Container.alignment`:

```text
căn content bên trong Container
```

Và quan trọng nhất:

```text
expand
→ kích thước vùng

alignment
→ vị trí content/children trong vùng
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
19. Card, ExpansionTile, ListTile    ✅
20. Layout constraints & sizing      ✅
21. Alignment                        ✅
22. Spacing / padding / margin
23. Responsive UI
24. Theme
25. Dark / Light mode
26. Mini Project: Dashboard
```

## Buổi 22 — Spacing / Padding / Margin

Buổi tiếp theo chúng ta sẽ phân biệt thật kỹ:

```text
spacing
padding
margin
```

và đặc biệt là câu hỏi:

```text
"Khoảng cách này thuộc về parent hay child?"
```

Chúng ta sẽ xây các layout như:

```text
Card
├── padding
│
├── Image
│
├── spacing
│
├── Text
│
└── margin
```

để bạn hiểu **Box Model trong Flet** thay vì căn UI bằng cách thử số ngẫu nhiên.
