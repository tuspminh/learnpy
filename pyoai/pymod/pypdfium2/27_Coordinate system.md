# Buổi 27 — Coordinate System

Đây là một trong những bài **quan trọng nhất của Part III**.

Sau Buổi 25–26, chúng ta đã có:

```text
MediaBox / CropBox
        ↓
PageSize
        ↓
DPI
        ↓
PixelSize
```

Nhưng vẫn còn một câu hỏi lớn:

> **Một điểm `(x, y)` trong PDF nằm ở đâu trên ảnh render?**

Để trả lời chính xác, chúng ta phải hiểu:

```text
PDF Coordinate System
        ↓
Scale
        ↓
Rotation
        ↓
Crop
        ↓
Image Coordinate System
```

Đặc biệt, bài này kết nối trực tiếp với **BoundingBox, Text Position, Character Position** mà chúng ta đã học ở Part II.

---

# 1. PDF dùng hệ tọa độ nào?

PDF sử dụng hệ tọa độ Descartes:

```text
                 y
                 ↑
                 │
                 │
                 │
                 │
(0, 0) ──────────┼────────────→ x
```

Điểm gốc thường nằm ở:

```text
bottom-left
```

Ví dụ page:

```text
612 × 792 pt
```

thì:

```text
(0, 792) ───────────────── (612, 792)
    │                           │
    │                           │
    │                           │
    │                           │
    │                           │
(0, 0) ──────────────────── (612, 0)
```

---

# 2. Nhưng ảnh lại thường dùng top-left

Bitmap/PIL thường được hiểu theo:

```text
(0,0) ─────────────────→ x
  │
  │
  │
  │
  ↓
  y
```

Tức:

```text
top-left
```

Ví dụ ảnh:

```text
width  = 612
height = 792
```

thì:

```text
(0,0) ─────────────── (612,0)
  │                       │
  │                       │
  │                       │
  │                       │
(0,792) ───────────── (612,792)
```

Vậy ta có hai hệ:

```text
PDF                       IMAGE

      y ↑                    y ↓
        │                      │
        │                      │
        │                      │
        └──────→ x             └──────→ x
     bottom-left             top-left
```

---

# 3. Đây là nguồn gốc của rất nhiều bug

Giả sử PDF có:

```text
height = 792
```

Một text có tọa độ:

```text
x = 100
y = 700
```

Trong PDF:

```text
y = 700
```

nghĩa là nó nằm **gần phía trên** page.

Nhưng nếu ta đưa thẳng:

```python
image_y = 700
```

thì trong image coordinate:

```text
700
```

lại nằm **gần phía dưới**.

Vì vậy không thể:

```python
image_x = pdf_x
image_y = pdf_y
```

một cách mù quáng.

---

# 4. Chuyển PDF → Image

Giả sử:

```text
page_height = H
```

PDF point:

```text
(x, y)
```

chuyển sang top-left coordinate:

```text
x' = x
y' = H - y
```

Ví dụ:

```text
H = 792
x = 100
y = 700
```

thì:

```text
x' = 100
y' = 792 - 700
   = 92
```

Kết quả:

```text
PDF:

(100,700)


IMAGE:

(100,92)
```

Đúng trực giác:

```text
y = 700 PDF
→ gần top

y' = 92 image
→ gần top
```

---

# 5. Nhưng PDF còn có scale

Đến đây mới chỉ là:

```text
PDF point
    ↓
Image coordinate
```

Nếu render:

```text
72 DPI
```

thì:

```text
1 pt = 1 pixel
```

Nhưng nếu:

```text
144 DPI
```

thì:

```text
1 pt = 2 pixel
```

Vì:

```text
scale = DPI / 72
```

---

# 6. Công thức đầy đủ

Với:

```text
scale = DPI / 72
```

thì:

```text
pixel_x = pdf_x × scale
```

và:

```text
pixel_y = (page_height - pdf_y) × scale
```

Ví dụ:

```text
Page:
612 × 792 pt

DPI:
144

scale:
2
```

Điểm:

```text
PDF = (100,700)
```

chuyển thành:

```text
pixel_x = 100 × 2
        = 200

pixel_y = (792 - 700) × 2
        = 184
```

Kết quả:

```text
PDF coordinate
(100,700)

        ↓

Image coordinate
(200,184)
```

---

# 7. Xây Domain `Point`

Chúng ta không nên dùng tuple khắp project:

```python
x, y
```

Hãy tạo domain model.

`domain/point.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

Đơn giản nhưng rất hữu ích.

---

# 8. Xây `CoordinateSystem`

Ta tạo:

```text
domain/coordinate.py
```

```python
from dataclasses import dataclass

from .point import Point


@dataclass(frozen=True)
class PdfCoordinateSystem:
    page_width: float
    page_height: float

    def __post_init__(self):
        if self.page_width <= 0:
            raise ValueError(
                "page_width phải > 0"
            )

        if self.page_height <= 0:
            raise ValueError(
                "page_height phải > 0"
            )

    def to_top_left(self, point: Point) -> Point:
        return Point(
            x=point.x,
            y=self.page_height - point.y,
        )
```

---

# 9. Test

```python
from domain.point import Point
from domain.coordinate import PdfCoordinateSystem


def test_pdf_to_top_left():
    coordinate = PdfCoordinateSystem(
        page_width=612,
        page_height=792,
    )

    result = coordinate.to_top_left(
        Point(100, 700)
    )

    assert result.x == 100
    assert result.y == 92
```

---

# 10. Thêm Scale

Bây giờ chúng ta muốn:

```text
PDF point
      ↓
top-left point
      ↓
pixel
```

Mở rộng class:

```python
from dataclasses import dataclass

from .point import Point


@dataclass(frozen=True)
class PdfCoordinateSystem:

    page_width: float
    page_height: float

    def __post_init__(self):
        if self.page_width <= 0:
            raise ValueError(
                "page_width phải > 0"
            )

        if self.page_height <= 0:
            raise ValueError(
                "page_height phải > 0"
            )

    def to_top_left(self, point: Point) -> Point:
        return Point(
            x=point.x,
            y=self.page_height - point.y,
        )

    def to_pixels(
        self,
        point: Point,
        dpi: float,
    ) -> Point:

        if dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        scale = dpi / 72.0

        top_left = self.to_top_left(point)

        return Point(
            x=top_left.x * scale,
            y=top_left.y * scale,
        )
```

---

# 11. Test scale

```python
def test_pdf_to_pixels():
    coordinate = PdfCoordinateSystem(
        page_width=612,
        page_height=792,
    )

    result = coordinate.to_pixels(
        Point(100, 700),
        dpi=144,
    )

    assert result.x == 200
    assert result.y == 184
```

---

# 12. Tại sao `page_width` chưa được sử dụng?

Bạn sẽ nhận ra:

```python
page_width
```

hiện tại chưa tham gia:

```python
to_top_left()
```

Điều này là bình thường.

Với **không rotation**, phép biến đổi:

```text
x' = x
y' = H-y
```

không cần width.

Nhưng khi chúng ta đưa:

```text
rotation = 90°
rotation = 180°
rotation = 270°
```

vào, width bắt đầu cực kỳ quan trọng.

Đây là lý do coordinate system phải được thiết kế cẩn thận ngay từ đầu.

---

# 13. BoundingBox thì sao?

Đây mới là phần quan trọng đối với project của chúng ta.

Ở Part II, chúng ta có:

```python
BoundingBox(
    left,
    bottom,
    right,
    top,
)
```

Ví dụ:

```text
PDF:

       top = 700
       ┌──────────────┐
       │              │
       │    TEXT      │
       │              │
       └──────────────┘
       bottom = 650

left = 100
right = 300
```

Tức:

```python
box = BoundingBox(
    left=100,
    bottom=650,
    right=300,
    top=700,
)
```

---

# 14. Chuyển BoundingBox sang top-left

Ta có:

```text
PDF:

top    = 700
bottom = 650

Page height = 792
```

Sau chuyển:

```text
image_top =
    792 - 700
    = 92

image_bottom =
    792 - 650
    = 142
```

Vậy:

```text
PDF BoundingBox

left   = 100
bottom = 650
right  = 300
top    = 700
```

thành:

```text
Image BoundingBox

left   = 100
top    = 92
right  = 300
bottom = 142
```

Lưu ý:

> **Tên `top`/`bottom` phụ thuộc hệ tọa độ.**

Đây là lý do trong các hệ thống lớn nên biểu diễn rõ coordinate system thay vì chỉ dùng bốn số.

---

# 15. Viết hàm transform BoundingBox

```python
from domain.geometry import BoundingBox


class PdfCoordinateSystem:

    # ...

    def box_to_top_left(
        self,
        box: BoundingBox,
    ) -> BoundingBox:

        return BoundingBox(
            left=box.left,
            bottom=self.page_height - box.top,
            right=box.right,
            top=self.page_height - box.bottom,
        )
```

Test:

```python
def test_box_to_top_left():
    coordinate = PdfCoordinateSystem(
        page_width=612,
        page_height=792,
    )

    box = BoundingBox(
        left=100,
        bottom=650,
        right=300,
        top=700,
    )

    result = coordinate.box_to_top_left(box)

    assert result.left == 100
    assert result.right == 300
    assert result.bottom == 92
    assert result.top == 142
```

---

# 16. Scale BoundingBox

Nếu:

```text
DPI = 144
scale = 2
```

thì:

```text
100 pt → 200 px
```

Ta cần:

```python
def box_to_pixels(
    self,
    box: BoundingBox,
    dpi: float,
) -> BoundingBox:

    top_left = self.box_to_top_left(box)

    scale = dpi / 72.0

    return BoundingBox(
        left=top_left.left * scale,
        bottom=top_left.bottom * scale,
        right=top_left.right * scale,
        top=top_left.top * scale,
    )
```

Ví dụ:

```text
PDF:

left   = 100
bottom = 650
right  = 300
top    = 700
```

144 DPI:

```text
Image:

left   = 200
top    = 184
right  = 600
bottom = 284
```

---

# 17. Tại sao điều này quan trọng với Text Extraction?

Ở Part II chúng ta đã lấy:

```python
textpage.get_charbox(...)
```

và nhận bounding box trong **PDF coordinate system**.

Ví dụ:

```text
Character:

char = "A"

bbox =
(100, 650, 110, 700)
```

Trong PDF:

```text
      y ↑
        │
        │  A
        │ ┌──┐
        │ │  │
        │ └──┘
        └────────→ x
```

Nếu muốn vẽ rectangle lên PIL image:

```text
PDF bbox
   ↓
Coordinate transform
   ↓
Pixel bbox
   ↓
PIL.ImageDraw.rectangle()
```

Đây chính là nền tảng cho:

* highlight text;
* OCR overlay;
* PDF search;
* click vào text;
* annotation;
* debugging parser;
* hiển thị bounding box;
* PDF reader.

---

# 18. Render ở 300 DPI

Giả sử:

```text
A4
595.28 × 841.89 pt
```

300 DPI:

```text
scale ≈ 4.1667
```

Page pixel:

```text
2480 × 3508
```

Một điểm:

```text
PDF:

x = 100
y = 700
```

thành:

```text
x = 100 × 4.1667
  ≈ 416.67
```

```text
y = (841.89 - 700) × 4.1667
  ≈ 591.2
```

Do đó:

```text
PDF coordinate
       ↓
       ↓
Pixel coordinate
       ↓
(417, 591)
```

---

# 19. Rotation làm mọi thứ phức tạp hơn

Đây là phần chúng ta **không nên dùng công thức tùy tiện**.

Không rotation:

```text
x' = x
y' = H-y
```

Nhưng với:

```text
90°
```

tọa độ phải thay đổi cả:

```text
x
y
width
height
```

Ví dụ page:

```text
612 × 792
```

sau 90°:

```text
792 × 612
```

Vì vậy transformation phải biết:

```text
page_width
page_height
rotation
```

---

# 20. Rotation 90° — tư duy hình học

Đừng học thuộc một công thức duy nhất trước khi xác định:

```text
90° clockwise
```

hay:

```text
90° counter-clockwise
```

và coordinate system nào đang được dùng.

Ta có thể hình dung:

```text
Original

┌───────────┐
│           │
│     ●     │
│           │
└───────────┘
```

sau rotation:

```text
       ┌─────┐
       │     │
       │  ●  │
       │     │
       │     │
       └─────┘
```

Lúc này:

```text
width ↔ height
```

và vị trí `(x,y)` cũng thay đổi.

**Buổi 24** chúng ta chỉ xử lý rotation của rendering.

**Buổi 27** bắt đầu xử lý rotation dưới góc nhìn coordinate transformation.

---

# 21. Đừng dùng PIL để "sửa" coordinate

Một lỗi architecture phổ biến:

```python
image = page.render(...).to_pil()

image = image.rotate(90)
```

rồi cố đoán:

```python
x = ...
y = ...
```

Điều này rất dễ làm:

```text
PDF coordinates
       ↓
PDFium rotation
       ↓
PIL rotation
       ↓
BoundingBox
```

bị lệch.

Tốt hơn:

```text
PDF
 ↓
PDFium render transformation
 ↓
Bitmap
```

và coordinate transformation phải biết chính xác renderer đã áp dụng transformation nào.

---

# 22. Xây một `CoordinateTransformer`

Trong project lớn, tôi muốn tách riêng:

```text
domain/
├── point.py
├── geometry.py
├── page_size.py
└── coordinate.py
```

`coordinate.py`:

```python
from dataclasses import dataclass

from .point import Point
from .geometry import BoundingBox


@dataclass(frozen=True)
class CoordinateTransformer:

    page_width: float
    page_height: float

    def pdf_to_top_left(
        self,
        point: Point,
    ) -> Point:

        return Point(
            x=point.x,
            y=self.page_height - point.y,
        )

    def pdf_box_to_top_left(
        self,
        box: BoundingBox,
    ) -> BoundingBox:

        return BoundingBox(
            left=box.left,
            bottom=self.page_height - box.top,
            right=box.right,
            top=self.page_height - box.bottom,
        )

    def pdf_to_pixel(
        self,
        point: Point,
        dpi: float,
    ) -> Point:

        if dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        scale = dpi / 72.0

        point = self.pdf_to_top_left(point)

        return Point(
            x=point.x * scale,
            y=point.y * scale,
        )

    def box_to_pixel(
        self,
        box: BoundingBox,
        dpi: float,
    ) -> BoundingBox:

        if dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        scale = dpi / 72.0

        box = self.pdf_box_to_top_left(box)

        return BoundingBox(
            left=box.left * scale,
            bottom=box.bottom * scale,
            right=box.right * scale,
            top=box.top * scale,
        )
```

---

# 23. Test toàn bộ

```python
def test_point_transform():
    transformer = CoordinateTransformer(
        page_width=612,
        page_height=792,
    )

    result = transformer.pdf_to_pixel(
        Point(100, 700),
        dpi=144,
    )

    assert result.x == 200
    assert result.y == 184
```

```python
def test_box_transform():
    transformer = CoordinateTransformer(
        page_width=612,
        page_height=792,
    )

    box = BoundingBox(
        left=100,
        bottom=650,
        right=300,
        top=700,
    )

    result = transformer.box_to_pixel(
        box,
        dpi=144,
    )

    assert result.left == 200
    assert result.bottom == 284
    assert result.right == 600
    assert result.top == 184
```

Chú ý:

Ở đây `BoundingBox` của chúng ta đang giữ semantics:

```text
left
bottom
right
top
```

nên sau khi chuyển sang top-left coordinates, nếu muốn dùng trực tiếp với PIL:

```python
ImageDraw.rectangle(
    [
        left,
        top,
        right,
        bottom,
    ]
)
```

ta cần chuyển semantics một lần nữa hoặc dùng một model riêng cho image coordinates.

---

# 24. Đây là một cải tiến architecture đáng làm

Thay vì ép:

```text
BoundingBox
```

phục vụ mọi hệ tọa độ, ta có thể định nghĩa:

```text
PdfBoundingBox
ImageBoundingBox
```

Ví dụ:

```python
@dataclass(frozen=True)
class PdfPoint:
    x: float
    y: float
```

và:

```python
@dataclass(frozen=True)
class PixelPoint:
    x: float
    y: float
```

Điều này cực kỳ hữu ích trong project PDF production.

Không thể vô tình viết:

```python
PdfPoint
+
PixelPoint
```

mà không suy nghĩ.

---

# 25. Kiến trúc coordinate cuối bài

Hiện tại:

```text
                    PDF
                     │
                     ▼
              PDF Coordinate
              bottom-left
                     │
                     │
               transformation
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
            Scale        Rotation
              │             │
              └──────┬──────┘
                     ▼
              Image Coordinate
                 top-left
                     │
                     ▼
                   Pixel
```

Khi kết hợp với text:

```text
PDF Text
   │
   ▼
TextPage
   │
   ▼
Character
   │
   ▼
PdfBoundingBox
   │
   ▼
CoordinateTransformer
   │
   ▼
PixelBoundingBox
   │
   ▼
PIL Image
```

Đây chính là pipeline để sau này làm:

```text
PDF search
    ↓
tìm text
    ↓
lấy bbox
    ↓
render page
    ↓
highlight bbox
```

---

# 26. Bài tập thực hành

Tạo:

```text
tests/test_coordinate.py
```

và kiểm tra ít nhất:

### Test 1

```text
Page = 612 × 792
Point = (0, 0)
```

Kết quả top-left:

```text
(0, 792)
```

### Test 2

```text
Point = (0, 792)
```

Kết quả:

```text
(0, 0)
```

### Test 3

```text
Point = (100, 700)
DPI = 144
```

Kết quả:

```text
(200, 184)
```

### Test 4

BoundingBox:

```text
(100, 650, 300, 700)
```

DPI:

```text
144
```

kiểm tra transformation.

### Test 5

```text
dpi = 0
```

phải:

```python
raise ValueError
```

---

# 27. Điều quan trọng nhất của Buổi 27

Hãy nhớ pipeline này:

```text
PDF coordinate
(x, y)
    │
    │ flip Y
    ▼
Top-left coordinate
(x, H-y)
    │
    │ × DPI/72
    ▼
Pixel coordinate
```

Công thức cơ bản:

```text
scale = DPI / 72

pixel_x = x × scale

pixel_y = (H - y) × scale
```

Với BoundingBox:

```text
pixel_left   = left × scale
pixel_right  = right × scale

pixel_top    = (H - top) × scale
pixel_bottom = (H - bottom) × scale
```

Nhưng:

> **Khi có rotation hoặc crop, không được áp dụng các công thức này một cách máy móc.**

---

## Roadmap

Chúng ta hiện đã đi:

```text
21 Render chất lượng cao
22 Grayscale
23 Transparency
24 Rotation
25 CropBox / MediaBox
26 Page Size
27 Coordinate System        ← xong
```

Tiếp theo:

# **Buổi 28 — Render Region**

Chúng ta sẽ ghép trực tiếp:

```text
MediaBox
CropBox
PageSize
Coordinate System
BoundingBox
DPI
Rotation
        ↓
Render một vùng cụ thể của PDF
```

và xây một API kiểu:

```python
renderer.render_region(
    page_index=0,
    region=BoundingBox(
        left=100,
        bottom=200,
        right=500,
        top=700,
    ),
    dpi=150,
)
```

để chỉ render **một vùng của trang**, thay vì render toàn bộ page rồi mới crop bằng PIL.
