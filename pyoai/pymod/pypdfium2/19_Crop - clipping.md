# Buổi 19 — Crop / Clipping trong PDF

Hôm nay chúng ta học cách **chỉ xử lý một vùng của trang PDF** thay vì luôn làm việc với toàn bộ page.

Đây là bước rất quan trọng vì nó kết nối trực tiếp các kiến thức:

```text
Buổi 13 → BoundingBox
Buổi 16 → Page Objects
Buổi 17 → Image Object
Buổi 18 → Text Layout
Buổi 19 → Crop / Clipping
```

Mục tiêu cuối cùng:

```text
PDF Page
   │
   ├── toàn trang
   │
   └── Crop Region
          │
          ├── Text
          ├── Image
          └── Objects
```

---

# 1. Crop và Clipping là gì?

Giả sử một trang PDF:

```text
┌─────────────────────────────────────┐
│                                     │
│             HEADER                  │
│                                     │
│    ┌─────────────────────────┐      │
│    │                         │      │
│    │       CONTENT           │      │
│    │                         │      │
│    └─────────────────────────┘      │
│                                     │
│             FOOTER                  │
│                                     │
└─────────────────────────────────────┘
```

Ta chỉ muốn xử lý:

```text
┌─────────────────────────────────────┐
│                                     │
│             HEADER                  │
│                                     │
│    ┌─────────────────────────┐      │
│    │                         │      │
│    │       CONTENT           │      │
│    │                         │      │
│    └─────────────────────────┘      │
│                                     │
│             FOOTER                  │
│                                     │
└─────────────────────────────────────┘
                 ↑
             crop region
```

Ví dụ:

```text
x1 = 100
y1 = 200
x2 = 500
y2 = 700
```

Chỉ những object/text nằm trong hoặc giao với vùng đó mới được quan tâm.

---

# 2. Có hai khái niệm cần phân biệt

## Crop

Crop thường có nghĩa:

> Chọn một vùng của page để lấy ra/xử lý.

Ví dụ:

```text
PDF Page
    ↓
Crop rectangle
    ↓
Cropped result
```

---

## Clipping

Clipping là khái niệm sâu hơn trong rendering:

> Giới hạn vùng mà renderer được phép vẽ.

Ví dụ:

```text
Page
┌───────────────────────┐
│                       │
│    ┌────────────┐     │
│    │ CLIP AREA  │     │
│    └────────────┘     │
│                       │
└───────────────────────┘
```

Các pixel/object nằm ngoài vùng clip sẽ không xuất hiện trong kết quả render.

---

# 3. Crop không thay đổi PDF gốc

Đây là điểm đầu tiên cần nhớ.

Nếu:

```python
page = pdf[0]
```

sau đó bạn xử lý một vùng:

```text
crop = (100, 200, 500, 700)
```

thì:

```text
PDF file
   │
   └── không bị sửa
```

Ta chỉ tạo:

```text
view / extraction / rendering
```

trên một vùng.

---

# 4. Coordinate system

Chúng ta đã gặp vấn đề này ở Buổi 13.

PDF sử dụng coordinate system:

```text
        top
         ↑
         │
         │
         │
         │
bottom ──┼────────────→ right
        left
```

Thông thường bounding box có dạng:

```python
(left, bottom, right, top)
```

Ví dụ:

```python
bbox = (
    100,
    200,
    500,
    700,
)
```

nghĩa là:

```text
left   = 100
bottom = 200
right  = 500
top    = 700
```

Kích thước:

```python
width = right - left
height = top - bottom
```

---

# 5. Crop region nên có Domain Model

Ta không nên dùng tuple khắp application:

```python
(100, 200, 500, 700)
```

Thay vào đó dùng `BoundingBox` mà chúng ta đã xây.

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
    def area(self) -> float:
        return self.width * self.height
```

---

# 6. Validate BoundingBox

Nên kiểm tra:

```text
right > left
top > bottom
```

Tạo model tốt hơn:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:

    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self):
        if self.right < self.left:
            raise ValueError(
                "right phải >= left"
            )

        if self.top < self.bottom:
            raise ValueError(
                "top phải >= bottom"
            )

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def area(self) -> float:
        return self.width * self.height
```

---

# 7. Kiểm tra một điểm có nằm trong crop không

Ta đã từng dùng ý tưởng này cho Link.

```python
def contains_point(
    self,
    x: float,
    y: float,
) -> bool:

    return (
        self.left <= x <= self.right
        and
        self.bottom <= y <= self.top
    )
```

Ví dụ:

```python
crop = BoundingBox(
    100,
    200,
    500,
    700,
)

print(crop.contains_point(300, 400))
```

Kết quả:

```text
True
```

---

# 8. Kiểm tra hai bounding box có giao nhau

Đây là operation **rất quan trọng** đối với PDF parser.

Ví dụ:

```text
Crop
┌───────────────────┐
│                   │
│   Object          │
│   ┌────────────┐  │
│   │            │  │
└───┼────────────┼──┘
    │            │
    └────────────┘
```

Object giao với crop.

Ta xây:

```python
def intersects(
    self,
    other: "BoundingBox",
) -> bool:

    return not (
        self.right < other.left
        or self.left > other.right
        or self.top < other.bottom
        or self.bottom > other.top
    )
```

---

# 9. Tính intersection

Không chỉ cần biết:

```text
intersects = True
```

mà đôi khi cần biết **phần giao nhau**.

Ví dụ:

```text
Crop:
(100, 200, 500, 700)

Object:
(400, 600, 800, 900)
```

Intersection:

```text
(400, 600, 500, 700)
```

Code:

```python
def intersection(
    self,
    other: "BoundingBox",
) -> "BoundingBox | None":

    left = max(self.left, other.left)
    bottom = max(self.bottom, other.bottom)

    right = min(self.right, other.right)
    top = min(self.top, other.top)

    if right < left or top < bottom:
        return None

    return BoundingBox(
        left=left,
        bottom=bottom,
        right=right,
        top=top,
    )
```

---

# 10. Tỷ lệ object nằm trong crop

Ta có thể tính:

```text
intersection area
-----------------
object area
```

Ví dụ:

```python
def overlap_ratio(
    self,
    other: "BoundingBox",
) -> float:

    intersection = self.intersection(other)

    if intersection is None:
        return 0.0

    if self.area == 0:
        return 0.0

    return intersection.area / self.area
```

Nếu:

```text
object nằm hoàn toàn trong crop
```

thì:

```text
ratio = 1.0
```

Nếu chỉ một nửa:

```text
ratio = 0.5
```

---

# 11. Đây cực kỳ hữu ích cho Page Objects

Buổi 16 chúng ta có:

```python
for obj in page.get_objects():
    bounds = obj.get_bounds()
```

Giả sử:

```python
crop = BoundingBox(
    left=100,
    bottom=200,
    right=500,
    top=700,
)
```

Ta có thể:

```python
for obj in page.get_objects():

    left, bottom, right, top = (
        obj.get_bounds()
    )

    bbox = BoundingBox(
        left,
        bottom,
        right,
        top,
    )

    if bbox.intersects(crop):
        print("Object intersects crop")
```

---

# 12. Lọc object theo crop

Tạo application service:

```python
class PageObjectCropper:

    def __init__(self, object_reader):
        self.object_reader = object_reader

    def get_objects_in_region(
        self,
        page,
        region: BoundingBox,
    ):

        objects = self.object_reader.read_page(
            page
        )

        return [
            obj
            for obj in objects
            if obj.bbox.intersects(region)
        ]
```

Application không cần biết:

```text
pypdfium2
PDFium
raw API
```

---

# 13. Crop text

Đây là phần chúng ta đã gặp ở Buổi 11.

`PdfTextPage` hỗ trợ:

```python
textpage.get_text_bounded(
    left=...,
    bottom=...,
    right=...,
    top=...,
)
```

README chính thức của pypdfium2 minh họa việc lấy text trong một bounding region bằng `get_text_bounded()`.

Ví dụ:

```python
pdf = pdfium.PdfDocument(
    "sample.pdf"
)

try:
    page = pdf[0]

    width, height = page.get_size()

    textpage = page.get_textpage()

    text = textpage.get_text_bounded(
        left=100,
        bottom=200,
        right=500,
        top=700,
    )

    print(text)

finally:
    pdf.close()
```

---

# 14. Crop text bằng Domain BoundingBox

Tốt hơn là application không truyền 4 số rời rạc.

```python
def extract_text_region(
    page,
    region: BoundingBox,
) -> str:

    textpage = page.get_textpage()

    return textpage.get_text_bounded(
        left=region.left,
        bottom=region.bottom,
        right=region.right,
        top=region.top,
    )
```

Ví dụ:

```python
region = BoundingBox(
    left=100,
    bottom=200,
    right=500,
    top=700,
)

text = extract_text_region(
    page,
    region,
)

print(text)
```

---

# 15. Crop text rất hữu ích

Ví dụ PDF:

```text
┌──────────────────────────────┐
│ HEADER                       │
│                              │
│ TITLE                        │
│                              │
│ CONTENT CONTENT CONTENT      │
│ CONTENT CONTENT CONTENT      │
│                              │
│ FOOTER                       │
└──────────────────────────────┘
```

Nếu chúng ta chỉ muốn:

```text
TITLE + CONTENT
```

thì:

```python
region = BoundingBox(
    left=50,
    bottom=150,
    right=550,
    top=750,
)
```

sau đó:

```python
textpage.get_text_bounded(...)
```

Không cần extract toàn bộ page rồi lọc bằng string.

---

# 16. Crop text theo nhiều vùng

Ví dụ một trang có:

```text
┌──────────────────────────┐
│ Header                   │
├──────────────────────────┤
│                          │
│ Main content             │
│                          │
├──────────────────────────┤
│ Footer                   │
└──────────────────────────┘
```

Ta có:

```python
header_region = BoundingBox(
    0, 750, 600, 842
)

content_region = BoundingBox(
    0, 100, 600, 750
)

footer_region = BoundingBox(
    0, 0, 600, 100
)
```

Sau đó:

```text
Page
 ├── Header
 ├── Content
 └── Footer
```

Đây chính là bước đầu tiên của **layout-aware extraction**.

---

# 17. Crop khi render

Đây là phần cần phân biệt với:

```python
get_text_bounded()
```

`get_text_bounded()` chỉ ảnh hưởng đến **text extraction**.

Nếu muốn render một vùng:

```text
PDF Page
    ↓
Clip Region
    ↓
Bitmap
```

thì cần sử dụng cơ chế clipping/render crop của PDFium/pypdfium2.

Cách chính xác phụ thuộc vào API render của version pypdfium2 bạn đang sử dụng.

Do đó trước khi viết adapter, kiểm tra:

```python
import inspect
import pypdfium2 as pdfium

print(inspect.signature(
    pdfium.PdfPage.render
))
```

và:

```python
print(inspect.signature(
    pdfium.PdfPage.render_topil
))
```

nếu version hiện tại có method tương ứng.

---

# 18. Vì sao không nên tự cắt PIL sau khi render?

Có hai cách:

### Cách A

```text
PDF
 ↓
render entire page
 ↓
PIL
 ↓
PIL.crop()
```

### Cách B

```text
PDF
 ↓
render only required region
 ↓
PIL
```

Cách A:

```text
dễ
```

nhưng có thể tốn:

```text
CPU
RAM
thời gian
```

nếu page rất lớn.

Cách B:

```text
PDFium
 ↓
chỉ render vùng cần thiết
```

có thể hiệu quả hơn.

---

# 19. Ví dụ tính crop trên ảnh

Giả sử:

```text
PDF page:
595 × 842 points
```

render:

```python
scale = 2
```

thì ảnh:

```text
1190 × 1684 px
```

Crop PDF:

```text
left   = 100
bottom = 200
right  = 500
top    = 700
```

Đổi sang pixel:

```python
pixel_left = 100 * 2
pixel_right = 500 * 2
```

và vì image coordinate thường có origin phía trên:

```python
pixel_top = (842 - 700) * 2
pixel_bottom = (842 - 200) * 2
```

Kết quả:

```text
left   = 200
top    = 284
right  = 1000
bottom = 1284
```

---

# 20. Hàm chuyển PDF bbox → image bbox

Ta có thể viết:

```python
def pdf_bbox_to_image_bbox(
    bbox: BoundingBox,
    page_height: float,
    scale: float,
) -> tuple[int, int, int, int]:

    left = round(
        bbox.left * scale
    )

    top = round(
        (page_height - bbox.top) * scale
    )

    right = round(
        bbox.right * scale
    )

    bottom = round(
        (page_height - bbox.bottom) * scale
    )

    return (
        left,
        top,
        right,
        bottom,
    )
```

Ví dụ:

```python
pdf_box = BoundingBox(
    100,
    200,
    500,
    700,
)

image_box = pdf_bbox_to_image_bbox(
    pdf_box,
    page_height=842,
    scale=2,
)

print(image_box)
```

Kết quả:

```text
(200, 284, 1000, 1284)
```

---

# 21. Sau đó PIL crop

Nếu bạn đã render:

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()
```

thì:

```python
crop_box = pdf_bbox_to_image_bbox(
    region,
    page_height=page_height,
    scale=2,
)

cropped = image.crop(crop_box)
```

Lưu:

```python
cropped.save(
    "cropped.png"
)
```

---

# 22. Nhưng có một vấn đề: rotation

Cách chuyển:

```python
pdf_y
→
page_height - pdf_y
```

chỉ là trường hợp đơn giản.

PDF có thể có:

```text
rotation = 0
rotation = 90
rotation = 180
rotation = 270
```

Ngoài ra còn:

```text
CropBox
MediaBox
transformation matrix
```

Do đó trong production:

```text
PDF coordinates
       ↓
page coordinate transform
       ↓
render coordinate
       ↓
image coordinate
```

không nên viết một công thức đơn giản duy nhất cho tất cả trường hợp.

---

# 23. Crop image object

Đây là chỗ kiến thức Buổi 17 kết hợp với Buổi 19.

Ta có:

```text
Image Object
    │
    └── bbox
```

Ví dụ:

```python
image_bbox = BoundingBox(
    150,
    250,
    450,
    600,
)
```

Crop:

```python
region = BoundingBox(
    100,
    200,
    500,
    700,
)
```

Kiểm tra:

```python
if image_bbox.intersects(region):
    print("Image nằm trong crop")
```

Nếu muốn chắc chắn image nằm **hoàn toàn** trong crop:

```python
def contains_box(
    self,
    other: "BoundingBox",
) -> bool:

    return (
        self.left <= other.left
        and self.bottom <= other.bottom
        and self.right >= other.right
        and self.top >= other.top
    )
```

---

# 24. Ba mức lọc object

Đây là một abstraction rất hay:

```text
Object
 │
 ├── OUTSIDE
 ├── INTERSECT
 └── INSIDE
```

Ta có enum:

```python
from enum import Enum


class RegionRelation(str, Enum):
    OUTSIDE = "outside"
    INTERSECT = "intersect"
    INSIDE = "inside"
```

Hàm:

```python
def relation(
    object_box: BoundingBox,
    region: BoundingBox,
) -> RegionRelation:

    if not object_box.intersects(region):
        return RegionRelation.OUTSIDE

    if region.contains_box(object_box):
        return RegionRelation.INSIDE

    return RegionRelation.INTERSECT
```

---

# 25. Đây là nền tảng cho Region Query

Sau này chúng ta có thể viết:

```python
objects = page_object_reader.query_region(
    page,
    region,
)
```

hoặc:

```python
characters = character_reader.query_region(
    page,
    region,
)
```

hoặc:

```python
images = image_reader.query_region(
    page,
    region,
)
```

Tất cả đều sử dụng chung:

```text
BoundingBox
+
RegionRelation
```

---

# 26. Region Query Architecture

Kiến trúc:

```text
                     Region
                       │
                       ▼
                Region Query
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Characters     Images       Objects
          │            │            │
          ▼            ▼            ▼
      BoundingBox   BoundingBox   BoundingBox
```

Đây là cách tránh viết:

```text
text crop logic
image crop logic
object crop logic
```

mỗi nơi một kiểu.

---

# 27. Hoàn thiện BoundingBox

Tôi khuyên từ bài này chúng ta chuẩn hóa model:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:

    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self):

        if self.right < self.left:
            raise ValueError(
                "right < left"
            )

        if self.top < self.bottom:
            raise ValueError(
                "top < bottom"
            )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def area(self):
        return self.width * self.height

    def contains_point(
        self,
        x: float,
        y: float,
    ) -> bool:

        return (
            self.left <= x <= self.right
            and
            self.bottom <= y <= self.top
        )

    def contains_box(
        self,
        other: "BoundingBox",
    ) -> bool:

        return (
            self.left <= other.left
            and self.bottom <= other.bottom
            and self.right >= other.right
            and self.top >= other.top
        )

    def intersects(
        self,
        other: "BoundingBox",
    ) -> bool:

        return not (
            self.right < other.left
            or self.left > other.right
            or self.top < other.bottom
            or self.bottom > other.top
        )

    def intersection(
        self,
        other: "BoundingBox",
    ) -> "BoundingBox | None":

        left = max(
            self.left,
            other.left,
        )

        bottom = max(
            self.bottom,
            other.bottom,
        )

        right = min(
            self.right,
            other.right,
        )

        top = min(
            self.top,
            other.top,
        )

        if right < left or top < bottom:
            return None

        return BoundingBox(
            left=left,
            bottom=bottom,
            right=right,
            top=top,
        )
```

Đây là model rất đáng giữ lại cho toàn bộ PDF project.

---

# 28. Unit Test

```python
def test_bbox_dimensions():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.width == 400
    assert box.height == 500
    assert box.area == 200_000
```

---

### Test point

```python
def test_contains_point():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.contains_point(
        300,
        400,
    )

    assert not box.contains_point(
        50,
        400,
    )
```

---

### Test intersection

```python
def test_intersects():

    a = BoundingBox(
        100,
        100,
        300,
        300,
    )

    b = BoundingBox(
        200,
        200,
        400,
        400,
    )

    assert a.intersects(b)
```

---

### Test outside

```python
def test_not_intersects():

    a = BoundingBox(
        100,
        100,
        200,
        200,
    )

    b = BoundingBox(
        300,
        300,
        400,
        400,
    )

    assert not a.intersects(b)
```

---

### Test intersection box

```python
def test_intersection():

    a = BoundingBox(
        100,
        100,
        300,
        300,
    )

    b = BoundingBox(
        200,
        200,
        400,
        400,
    )

    result = a.intersection(b)

    assert result is not None

    assert result.left == 200
    assert result.bottom == 200
    assert result.right == 300
    assert result.top == 300
```

---

# 29. Crop Text Service hoàn chỉnh

Ta có thể tạo:

```python
class PdfRegionTextReader:

    def read(
        self,
        page,
        region: BoundingBox,
    ) -> str:

        textpage = page.get_textpage()

        return textpage.get_text_bounded(
            left=region.left,
            bottom=region.bottom,
            right=region.right,
            top=region.top,
        )
```

Sử dụng:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument(
    "sample.pdf"
)

try:

    page = pdf[0]

    region = BoundingBox(
        left=100,
        bottom=200,
        right=500,
        top=700,
    )

    reader = PdfRegionTextReader()

    text = reader.read(
        page,
        region,
    )

    print(text)

finally:
    pdf.close()
```

---

# 30. Ứng dụng vào PDF truyện

Đây là phần rất đáng chú ý đối với hướng project của bạn.

Giả sử PDF:

```text
┌─────────────────────────────────────┐
│              CHAPTER 1              │
│                                     │
│  Once upon a time...                │
│  The story continues...             │
│                                     │
│                                     │
│                1                    │
└─────────────────────────────────────┘
```

Ta có thể định nghĩa:

```text
Header region
Content region
Footer region
```

Sau đó:

```text
PDF
 │
 ├── Header crop
 │       ↓
 │    ignore
 │
 ├── Content crop
 │       ↓
 │    extract text
 │
 └── Footer crop
         ↓
       ignore
```

Kết quả sạch hơn rất nhiều so với:

```python
text = entire_page_text
```

rồi cố:

```python
text.replace(...)
```

---

# 31. Crop + Font Analysis

Buổi 18 và 19 kết hợp:

```text
Region
 ↓
Characters
 ↓
Font sizes
 ↓
Lines
 ↓
Heading
```

Ví dụ:

```text
Page
│
├── Header
│
├── Content
│    │
│    ├── Chapter title 20pt
│    ├── paragraph 11pt
│    └── paragraph 11pt
│
└── Footer
```

Ta chỉ phân tích:

```text
Content region
```

Do đó heading detector không bị nhiễu bởi:

```text
header
footer
page number
watermark
```

Đây là một kỹ thuật rất thực tế.

---

# 32. Crop + Image Analysis

Tương tự:

```text
Page
 ↓
Region
 ↓
Image Objects
 ↓
Image coverage
```

Ví dụ muốn tìm ảnh minh họa trong phần nội dung:

```python
images = image_reader.read_page_images(
    page,
    page_index=0,
)

content_images = [
    image
    for image in images
    if image.bbox.intersects(
        content_region
    )
]
```

---

# 33. Crop + Link

Tương tự với link:

```text
Page
 ↓
Links
 ↓
BoundingBox
 ↓
Region
```

Ví dụ:

```python
content_links = [
    link
    for link in links
    if link.bbox.intersects(
        content_region
    )
]
```

Như vậy một `Region` có thể trở thành abstraction dùng chung cho:

```text
Text
Image
Link
Page Object
Character
```

---

# 34. Kiến trúc sau Buổi 19

Bây giờ kiến trúc của PDF analyzer:

```text
                         PdfPage
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
       TextPage        Page Objects        Links
           │                │
           ▼                ▼
      Characters         Images
           │                │
           └────────┬───────┘
                    │
                    ▼
               BoundingBox
                    │
                    ▼
               Region Query
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      Text        Image       Object
```

Đây là kiến trúc rất tốt để tiếp tục sang Mini Project.

---

# 35. Một lưu ý về CropBox của PDF

Có hai khái niệm dễ bị nhầm:

### Application crop

```text
Tôi muốn lấy vùng
(x1, y1, x2, y2)
```

Đây là thứ chúng ta học hôm nay.

### PDF CropBox

PDF bản thân nó có các page boxes như:

```text
MediaBox
CropBox
BleedBox
TrimBox
ArtBox
```

Ví dụ:

```text
MediaBox
┌──────────────────────────────┐
│                              │
│    CropBox                   │
│    ┌────────────────────┐    │
│    │                    │    │
│    │     visible area   │    │
│    │                    │    │
│    └────────────────────┘    │
│                              │
└──────────────────────────────┘
```

**Không được đánh đồng CropBox của PDF với `get_text_bounded()` region.**

CropBox là thuộc tính page geometry của PDF.

Còn region hôm nay là:

```text
application-defined processing region
```

---

# 36. Bài tập Buổi 19

### Bài 1

Hoàn thiện:

```python
BoundingBox
```

với:

```text
width
height
area
contains_point
contains_box
intersects
intersection
```

---

### Bài 2

Viết:

```python
extract_text_region(
    pdf_path,
    page_index,
    region,
)
```

Ví dụ:

```python
region = BoundingBox(
    100,
    200,
    500,
    700,
)
```

---

### Bài 3

Viết:

```python
find_objects_in_region(
    page,
    region,
)
```

---

### Bài 4

Viết:

```python
find_images_in_region(
    page,
    region,
)
```

---

### Bài 5 — rất quan trọng

Tạo:

```text
RegionAnalyzer
```

có:

```python
analyze(
    page,
    region,
)
```

output:

```python
{
    "text": "...",
    "object_count": 10,
    "image_count": 2,
    "link_count": 1,
}
```

Đây sẽ là tiền thân của `PageAnalyzer`.

---

# 37. Tổng kết Buổi 19

Hôm nay chúng ta đã xây một abstraction rất quan trọng:

```text
BoundingBox
      │
      ▼
   Region
      │
      ├── Text
      ├── Character
      ├── Image
      ├── Link
      └── Page Object
```

Các phép toán quan trọng:

```text
contains_point()
contains_box()
intersects()
intersection()
```

Và nhớ sự khác biệt:

```text
get_text_bounded()
    ↓
crop vùng TEXT EXTRACTION
```

khác với:

```text
render + clip/crop
    ↓
crop vùng IMAGE/RENDERING
```

và khác nữa:

```text
PDF CropBox
    ↓
page geometry
```

---

## Roadmap tiếp theo

Chúng ta đã hoàn thành:

```text
11. TextPage
12. Extract text
13. Text position / bounding box
14. Character-level extraction
15. Link / annotation
16. Page objects
17. Images
18. Font và text information
19. Crop / clipping
```

**Buổi 20 — Mini Project: PDF Text Extractor** sẽ là bài tổng hợp toàn bộ Phần II:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ├── TextPage
 │      ↓
 │   Character
 │      ↓
 │   Word
 │      ↓
 │   Line
 │
 ├── BoundingBox
 │
 ├── FontInfo
 │
 ├── Region
 │
 └── Page Objects
 │
 ▼
PDF Text Extractor
 │
 ▼
.txt / structured text
```

Đây sẽ là lúc chúng ta **gom các abstraction đã học thành một project hoàn chỉnh**, thay vì tiếp tục học API rời rạc.
