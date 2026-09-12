# Buổi 13 — Text Position / Bounding Box

**Phần II — Đọc và phân tích PDF**

Roadmap hiện tại:

```text
11. TextPage
12. Extract text
13. Text position / bounding box   ← Hôm nay
14. Character-level extraction
15. Link / annotation
16. Page objects
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Ở Buổi 12, chúng ta đã lấy được:

```python
text = textpage.get_text_bounded()
```

nhưng kết quả chỉ là:

```text
"CHƯƠNG 1\nĐây là nội dung..."
```

Hôm nay chúng ta muốn biết thêm:

```text
Text = "CHƯƠNG 1"

Nó nằm ở đâu?
x = ?
y = ?
width = ?
height = ?
```

Tức là chuyển từ:

```text
PDF → Text
```

sang:

```text
PDF → Text + Geometry
```

Đây là bước cực kỳ quan trọng để xây PDF parser.

---

# 1. Bounding Box là gì?

Bounding box, thường gọi là **BBox**, là hình chữ nhật bao quanh một đối tượng.

Ví dụ:

```text
PDF page
┌──────────────────────────────────────┐
│                                      │
│       ┌──────────────────┐           │
│       │   CHƯƠNG 1       │           │
│       └──────────────────┘           │
│                                      │
│       ┌─────────────────────────┐    │
│       │ Đây là nội dung...      │    │
│       └─────────────────────────┘    │
│                                      │
└──────────────────────────────────────┘
```

Ta có thể biểu diễn:

```text
left
bottom
right
top
```

Ví dụ:

```text
left   = 100
bottom = 700
right  = 300
top    = 730
```

Bounding box:

```text
(left, bottom, right, top)
```

---

# 2. Vì sao position quan trọng?

Nếu chỉ có:

```text
CHƯƠNG 1
Đây là nội dung
Tác giả: ABC
```

ta không biết:

* cái nào là header
* cái nào là footer
* text nằm ở cột nào
* tiêu đề nằm ở đâu
* text có nằm trong một vùng nhất định không

Nhưng nếu có tọa độ:

```text
CHƯƠNG 1
x=100 y=750

Đây là nội dung
x=100 y=700

Tác giả: ABC
x=100 y=50
```

ta có thể suy luận:

```text
y rất cao → header
y rất thấp → footer
```

hoặc:

```text
x < 300 → column trái
x > 300 → column phải
```

Đây là nền tảng của document layout analysis.

---

# 3. Hệ tọa độ PDF

Đây là phần **cực kỳ quan trọng**.

Trong PDF, tọa độ thường được biểu diễn theo:

```text
(0, 0)
```

ở **góc dưới-trái** của trang.

Ví dụ:

```text
                 top
                  ↑
                  │
       ┌──────────────────────┐
       │                      │
       │                      │
       │       TEXT           │
       │                      │
       │                      │
       └──────────────────────┘
       ↑
      (0,0)
```

Nói đơn giản:

```text
x tăng →
y tăng ↑
```

Trong khi hình ảnh/PIL thường có:

```text
(0,0)
  ───────────────► x
  │
  │
  │
  ▼
  y
```

tức là gốc tọa độ ở **góc trên-trái**.

---

# 4. PDF coordinates vs Image coordinates

Đây là một lỗi rất dễ gặp khi kết hợp pypdfium2 với Pillow/OpenCV.

### PDF

```text
       y ↑
         │
         │
         │
(0,0) ───┴────────► x
```

### Image

```text
(0,0) ─────────────► x
  │
  │
  │
  ▼
  y
```

Vì vậy:

```text
PDF coordinate
       ≠
Image pixel coordinate
```

Nếu sau này chúng ta muốn vẽ bounding box lên ảnh render, phải chuyển đổi hệ tọa độ.

---

# 5. `get_text_bounded()` đã sử dụng bounding box

Ở Buổi 11 chúng ta đã thấy:

```python
textpage.get_text_bounded(
    left=50,
    bottom=100,
    right=500,
    top=700,
)
```

Các tham số:

```text
left
bottom
right
top
```

chính là một bounding rectangle.

Nó nói:

> "Chỉ lấy text nằm trong vùng này."

pypdfium2 cung cấp API này thông qua `PdfTextPage`.

---

# 6. Nhưng hôm nay ta muốn điều ngược lại

Buổi 12:

```text
Rectangle
   ↓
Text
```

Ví dụ:

```python
text = textpage.get_text_bounded(
    left=100,
    bottom=500,
    right=500,
    top=700,
)
```

Buổi 13 muốn:

```text
Text
   ↓
Rectangle
```

Tức là:

```text
"CHƯƠNG 1"
      ↓
(left, bottom, right, top)
```

Đây là bước đầu để phân tích layout.

---

# 7. Text range

Một trang PDF có thể chứa nhiều ký tự:

```text
CHƯƠNG 1

Đây là nội dung của chương.
```

Về mặt khái niệm, text có thể được xem như một chuỗi:

```text
C H Ư Ơ N G   1 \n
```

mỗi ký tự có vị trí trong text page.

Ví dụ:

```text
index:

0 C
1 H
2 Ư
3 Ơ
4 N
5 G
6 space
7 1
```

pypdfium2 có các API cấp range như `get_text_range()`, và đây sẽ là nền tảng để chúng ta đi sâu hơn ở **Buổi 14 — Character-level extraction**.

---

# 8. API position quan trọng

Ở cấp `PdfTextPage`, pypdfium2 có các phương thức liên quan đến text geometry/range. Một cách tiếp cận quan trọng là lấy thông tin vị trí dựa trên **index/range của text**, thay vì chỉ lấy một `str` hoàn chỉnh.

Tư duy cần nhớ:

```text
PdfTextPage
    │
    ├── text
    │
    ├── range
    │
    └── geometry
```

Trong các phiên bản pypdfium2 hiện hành, tên và kiểu trả về cụ thể của các helper geometry có thể khác tùy API wrapper/version, nên khi code production ta nên kiểm tra trực tiếp API version đang cài thay vì giả định một tuple cố định.

Điểm quan trọng của Buổi 13 là **mô hình dữ liệu**, không phải học thuộc một magic tuple.

---

# 9. Thiết kế model `TextBox`

Thay vì trả về:

```python
tuple
```

ta nên tạo model rõ nghĩa.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom
```

Ví dụ:

```python
box = BoundingBox(
    left=100,
    bottom=700,
    right=300,
    top=730,
)
```

Ta có:

```python
print(box.width)
print(box.height)
```

Kết quả:

```text
200
30
```

---

# 10. Vì sao không dùng tuple?

Có thể viết:

```python
box = (
    100,
    700,
    300,
    730,
)
```

nhưng rất khó đọc:

```python
box[0]
box[1]
box[2]
box[3]
```

Không biết:

```text
box[0] là gì?
box[1] là gì?
```

Trong khi:

```python
box.left
box.bottom
box.right
box.top
```

rõ ràng hơn rất nhiều.

---

# 11. Model `TextFragment`

Bây giờ kết hợp:

```text
text
+
bounding box
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom


@dataclass(frozen=True)
class TextFragment:
    text: str
    bbox: BoundingBox
```

Một object:

```python
fragment = TextFragment(
    text="CHƯƠNG 1",
    bbox=BoundingBox(
        left=100,
        bottom=700,
        right=300,
        top=730,
    ),
)
```

Ta có:

```python
fragment.text
```

và:

```python
fragment.bbox.left
```

---

# 12. Đây là abstraction rất quan trọng

Thay vì:

```text
str
```

ta bắt đầu có:

```text
TextFragment
├── text
└── bbox
    ├── left
    ├── bottom
    ├── right
    └── top
```

Sau này có thể mở rộng:

```text
TextFragment
├── text
├── bbox
├── font
├── font_size
├── color
├── character_index
└── ...
```

Những thông tin này sẽ liên quan trực tiếp tới:

```text
Buổi 14 — Character-level extraction
Buổi 18 — Font và text information
```

---

# 13. Text line

Một mức abstraction cao hơn:

```text
Page
 └── Line
      ├── Fragment
      ├── Fragment
      └── Fragment
```

Ví dụ PDF:

```text
CHƯƠNG 1
```

có thể được biểu diễn:

```text
TextLine
    │
    └── TextFragment
           text = "CHƯƠNG 1"
```

Một dòng:

```text
Xin chào các bạn
```

có thể có nhiều fragment:

```text
TextLine
│
├── "Xin"
├── "chào"
├── "các"
└── "bạn"
```

Đây là hướng chúng ta sẽ đi sau này.

---

# 14. Bounding box và layout

Giả sử ta có:

```text
Fragment A
x = 50
y = 700

Fragment B
x = 300
y = 700
```

Có thể suy luận:

```text
A          B
│          │
▼          ▼

Column 1   Column 2
```

Nếu:

```text
A.y ≈ B.y
```

thì có khả năng chúng thuộc cùng một dòng.

Nếu:

```text
A.y ≠ B.y
```

thì có thể thuộc các dòng khác nhau.

Nhưng:

> Không được coi `y` bằng nhau tuyệt đối.

Vì font rendering có thể tạo sai khác nhỏ:

```text
700.01
699.98
700.03
```

Ta cần tolerance.

---

# 15. Tolerance

Ví dụ:

```python
def same_line(
    y1: float,
    y2: float,
    tolerance: float = 2.0,
) -> bool:

    return abs(y1 - y2) <= tolerance
```

Test:

```python
print(
    same_line(700, 701)
)
```

```text
True
```

Nhưng:

```python
print(
    same_line(700, 710)
)
```

```text
False
```

Đây là nền tảng cho việc **group text thành lines**.

---

# 16. Group text thành dòng

Giả sử có:

```python
fragments = [
    TextFragment(...),
    TextFragment(...),
    TextFragment(...),
]
```

Mỗi fragment có:

```python
fragment.bbox.top
```

Ta có thể sắp xếp:

```python
sorted(
    fragments,
    key=lambda item: item.bbox.top,
)
```

Nhưng cần cẩn thận về hướng tọa độ.

Trong PDF:

```text
top
↑
```

nên thứ tự từ trên xuống thường cần sort theo:

```python
-key
```

hoặc một chiến lược tương ứng tùy representation.

Ví dụ:

```python
sorted(
    fragments,
    key=lambda item: -item.bbox.top,
)
```

Sau đó:

```text
y lớn
 ↓
dòng trên

y nhỏ
 ↓
dòng dưới
```

---

# 17. Group theo X để xác định thứ tự trong dòng

Sau khi xác định cùng dòng:

```text
Fragment A
x = 100

Fragment B
x = 200

Fragment C
x = 300
```

thì sort:

```python
sorted(
    fragments,
    key=lambda item: item.bbox.left,
)
```

Kết quả:

```text
A → B → C
```

Từ đó ta có thể tái dựng:

```text
Xin chào các bạn
```

thay vì:

```text
các Xin bạn chào
```

---

# 18. Đây chính là vấn đề PDF extraction thực tế

Một PDF có thể lưu:

```text
Hello
World
```

theo thứ tự object không giống thứ tự mắt nhìn.

Ta cần:

```text
Raw PDF objects
       ↓
Text fragments
       ↓
Coordinates
       ↓
Sort
       ↓
Group lines
       ↓
Group paragraphs
       ↓
Readable text
```

Đây là **layout reconstruction**.

---

# 19. Đừng làm layout reconstruction hôm nay

Đây là điểm cần giữ roadmap.

Buổi 13 chỉ cần hiểu:

```text
Text
 +
Position
```

Chúng ta **chưa** xây:

```text
paragraph detector
column detector
table detector
header detector
```

Những thứ đó sẽ làm project phức tạp rất nhanh.

---

# 20. Tạo `PdfTextPositionReader`

Ta có thể bắt đầu abstraction:

```python
from typing import Any


class PdfTextPositionReader:

    def __init__(
        self,
        page: Any,
    ) -> None:

        self.page = page
        self.textpage = page.get_textpage()

    def get_text(
        self,
    ) -> str:

        return self.textpage.get_text_bounded()
```

Hiện tại chưa lấy position.

Mục đích là chuẩn bị architecture:

```text
PdfTextReader
        ↓
text

PdfTextPositionReader
        ↓
text + geometry
```

---

# 21. Domain model hoàn chỉnh

Tạo:

```text
pdf_converter/domain/text.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:

    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:

        return self.right - self.left

    @property
    def height(self) -> float:

        return self.top - self.bottom

    @property
    def center_x(self) -> float:

        return (
            self.left + self.right
        ) / 2

    @property
    def center_y(self) -> float:

        return (
            self.bottom + self.top
        ) / 2


@dataclass(frozen=True)
class TextFragment:

    text: str
    bbox: BoundingBox
```

Bây giờ:

```python
box.center_x
```

có thể dùng để phân tích column.

---

# 22. Ví dụ thực tế

Giả sử:

```python
fragment = TextFragment(
    text="CHƯƠNG 1",
    bbox=BoundingBox(
        left=100,
        bottom=700,
        right=300,
        top=730,
    ),
)
```

Ta có:

```python
print(fragment.text)
```

```text
CHƯƠNG 1
```

và:

```python
print(fragment.bbox.width)
```

```text
200
```

và:

```python
print(fragment.bbox.height)
```

```text
30
```

---

# 23. Chuyển PDF coordinate → Image coordinate

Đây là phần rất hữu ích cho project sau này.

Giả sử:

```python
page_width, page_height = page.get_size()
```

và ta render:

```python
bitmap = page.render(
    scale=2
)
```

thì:

```text
image_width
    ≈
page_width × 2

image_height
    ≈
page_height × 2
```

Giả sử PDF BBox:

```text
left   = 100
bottom = 700
right  = 300
top    = 730
```

thì tọa độ pixel cần scale:

```text
x_pixel = x_pdf × scale
```

nhưng Y cần đảo trục khi chuyển sang image coordinate.

Khái niệm:

```python
x1 = left * scale
x2 = right * scale

y1 = (page_height - top) * scale
y2 = (page_height - bottom) * scale
```

Ví dụ:

```text
PDF:

             top=730
              ┌─────────┐
              │  TEXT   │
              └─────────┘
             bottom=700


Image:

y=page_height-730
              ┌─────────┐
              │  TEXT   │
              └─────────┘
y=page_height-700
```

Đây là công thức cực kỳ quan trọng nếu muốn **vẽ bounding box lên ảnh render**.

---

# 24. Demo vẽ BBox

Sau khi có:

```text
PIL.Image
+
BoundingBox
```

ta có thể:

```python
from PIL import ImageDraw


draw = ImageDraw.Draw(image)

draw.rectangle(
    [
        x1,
        y1,
        x2,
        y2,
    ],
    outline="red",
    width=2,
)
```

Kết quả:

```text
PDF
 ↓
render
 ↓
PIL.Image
 +
Text BBox
 ↓
draw.rectangle()
 ↓
Debug image
```

Đây là một kỹ thuật cực kỳ hữu ích để debug parser.

---

# 25. Ví dụ utility chuyển tọa độ

```python
def pdf_box_to_image_box(
    bbox: BoundingBox,
    page_width: float,
    page_height: float,
    scale: float,
) -> tuple[float, float, float, float]:

    x1 = bbox.left * scale

    y1 = (
        page_height - bbox.top
    ) * scale

    x2 = bbox.right * scale

    y2 = (
        page_height - bbox.bottom
    ) * scale

    return x1, y1, x2, y2
```

Sử dụng:

```python
x1, y1, x2, y2 = pdf_box_to_image_box(
    bbox,
    page_width,
    page_height,
    scale=2,
)
```

---

# 26. Vì sao việc này quan trọng với OCR?

Sau này chúng ta có hai nguồn:

```text
PDF text
    +
OCR text
```

OCR thường trả:

```text
text
+
bounding box
```

Ví dụ:

```text
OCR:
"CHƯƠNG 1"
bbox=(...)
```

PDF text extraction:

```text
"CHƯƠNG 1"
bbox=(...)
```

Ta có thể đối chiếu:

```text
PDF text
   ↕
OCR text
```

Đây là cơ sở để xây hệ thống document processing mạnh hơn.

---

# 27. Một use case rất thực tế: loại header/footer

Giả sử tất cả các trang có:

```text
TOP:
TÊN SÁCH

BOTTOM:
Trang 15
```

Ta có thể xác định:

```python
if fragment.bbox.top > page_height - 50:
    # header
```

hoặc:

```python
if fragment.bbox.bottom < 50:
    # footer
```

Sau đó:

```text
Raw text
 ↓
Remove header
 ↓
Remove footer
 ↓
Chapter content
```

Đối với hệ thống đọc truyện/PDF, kỹ thuật này rất hữu ích.

---

# 28. Một use case khác: chỉ lấy vùng nội dung

Giả sử trang:

```text
┌─────────────────────────────┐
│ Header                      │
├─────────────────────────────┤
│                             │
│       CONTENT               │
│                             │
├─────────────────────────────┤
│ Footer                      │
└─────────────────────────────┘
```

Ta có thể lấy:

```text
content area
```

bằng bounding rectangle.

Ở Buổi 12 chúng ta đã biết:

```python
textpage.get_text_bounded(
    left=...,
    bottom=...,
    right=...,
    top=...,
)
```

Nên Buổi 13 giúp chúng ta hiểu **vì sao API này tồn tại**.

---

# 29. Test BoundingBox

```python
from pdf_converter.domain.text import BoundingBox


def test_bbox_size():

    box = BoundingBox(
        left=100,
        bottom=200,
        right=300,
        top=500,
    )

    assert box.width == 200
    assert box.height == 300
```

Center:

```python
def test_bbox_center():

    box = BoundingBox(
        left=100,
        bottom=200,
        right=300,
        top=500,
    )

    assert box.center_x == 200
    assert box.center_y == 350
```

---

# 30. Test coordinate conversion

```python
def test_pdf_box_to_image_box():

    box = BoundingBox(
        left=100,
        bottom=700,
        right=300,
        top=730,
    )

    result = pdf_box_to_image_box(
        bbox=box,
        page_width=595,
        page_height=842,
        scale=2,
    )

    assert result == (
        200,
        224,
        600,
        284,
    )
```

Tính:

```text
x1 = 100 × 2 = 200

y1 = (842 - 730) × 2
   = 224

x2 = 300 × 2
   = 600

y2 = (842 - 700) × 2
   = 284
```

---

# 31. Kiến trúc sau Buổi 13

Bây giờ hệ thống của chúng ta đã có hai cấp:

```text
                PdfPage
                   │
             ┌─────┴──────┐
             │            │
             ▼            ▼
         Renderer      TextReader
             │            │
             ▼            ▼
        PIL.Image        Text
                          │
                          ▼
                   Position Reader
                          │
                          ▼
                  TextFragment
                          │
                          ▼
                     BoundingBox
```

Về domain:

```text
TextFragment
    │
    ├── text
    │
    └── BoundingBox
          ├── left
          ├── bottom
          ├── right
          └── top
```

---

# 32. Điều cần nhớ nhất hôm nay

### ① Text không chỉ là string

```text
"CHƯƠNG 1"
```

còn có:

```text
position
size
```

---

### ② Bounding box

```text
(left, bottom, right, top)
```

---

### ③ PDF và Image có hệ tọa độ khác nhau

```text
PDF:
origin = bottom-left

Image:
origin = top-left
```

---

### ④ Position cho phép phân tích layout

```text
position
   ↓
line
   ↓
paragraph
   ↓
column
   ↓
document structure
```

---

### ⑤ Đừng clean text quá sớm

Pipeline tốt:

```text
PDF
 ↓
Raw Text
 ↓
Text + Position
 ↓
Structured Text
 ↓
Clean
 ↓
Domain
```

Không nên:

```text
PDF
 ↓
replace("\n", " ")
 ↓
mất structure
```

---

# 33. Bài tập thực hành

### Bài 1

Tạo:

```python
BoundingBox
```

với:

```python
left
bottom
right
top
```

và implement:

```python
width
height
center_x
center_y
```

---

### Bài 2

Tạo:

```python
TextFragment
```

có:

```text
text
bbox
```

---

### Bài 3 ⭐

Viết:

```python
pdf_box_to_image_box()
```

chuyển:

```text
PDF coordinates
        ↓
Image coordinates
```

---

### Bài 4 ⭐⭐

Render trang đầu tiên ở:

```text
150 DPI
```

sau đó lấy các text fragment có position và vẽ bounding box lên ảnh.

Mục tiêu:

```text
PDF
 ↓
PdfTextPage
 ↓
Text + BBox
 ↓
Render
 ↓
PIL.Image
 ↓
draw.rectangle()
```

Đây là bài rất đáng làm vì nó giúp bạn **nhìn thấy** parser đang hiểu PDF như thế nào.

---

### Bài 5 ⭐⭐⭐

Tìm tất cả text ở vùng:

```text
top 100 points
```

và in:

```text
HEADER:
...
```

Sau đó tìm:

```text
bottom 100 points
```

và in:

```text
FOOTER:
...
```

Bạn sẽ bắt đầu thấy cách xây một **PDF layout parser** thực tế.

---

## Tiếp theo — Buổi 14

Buổi 14 sẽ đi xuống **mức ký tự**:

```text
PdfTextPage
      ↓
characters
      ↓
character index
      ↓
character text
      ↓
character position
      ↓
character bounding box
```

Từ đó chúng ta sẽ hiểu được tại sao có thể xây:

```text
Character
   ↓
Word
   ↓
Line
   ↓
Paragraph
   ↓
Chapter
```

và đây sẽ là nền móng trực tiếp cho **PDF Text Extractor** ở Buổi 20.
