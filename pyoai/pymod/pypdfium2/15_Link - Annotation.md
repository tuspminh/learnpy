# Buổi 15 — Link / Annotation

Hôm nay chúng ta chuyển từ **Text** sang một loại đối tượng khác của PDF: **Link và Annotation**.

Roadmap:

```text
11. TextPage
12. Extract text
13. Text position / bounding box
14. Character-level extraction
15. Link / annotation          ← Hôm nay
16. Page objects
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Điểm rất quan trọng của bài này:

```text
PDF
├── Text
├── Images
├── Graphics
└── Annotations
      └── Link
```

**Link không phải là Text.**

Ví dụ trên PDF nhìn thấy:

```text
Xem website: https://example.com
```

phần chữ có thể là text object, còn vùng click:

```text
┌──────────────────────────────┐
│ https://example.com          │
└──────────────────────────────┘
```

là một **link annotation** riêng.

PDFium cũng phân biệt rõ **link annotation** với các URL được tự động phát hiện trong text; API `FPDFLink_LoadWebLinks()` xử lý loại URL xuất hiện trong nội dung trang ngay cả khi PDF không có link annotation. ([GitHub][1])

---

# 1. Annotation là gì?

Annotation có thể hiểu đơn giản là:

> Một đối tượng gắn với một vùng trên trang PDF và mang thêm thông tin/hành vi.

Ví dụ:

```text
PDF Page
│
├── Text
│
├── Image
│
└── Annotation
     ├── Link
     ├── Highlight
     ├── Note
     ├── Popup
     ├── FileAttachment
     └── ...
```

PDF hỗ trợ rất nhiều annotation type như Text, Link, FreeText, Highlight, Underline, Stamp, FileAttachment, Widget... ([GitHub][2])

Nhưng trong course này hôm nay chúng ta **chỉ tập trung vào Link**.

---

# 2. Link có 2 loại quan trọng

Về mặt ứng dụng, chúng ta thường gặp:

### External link

```text
https://example.com
```

Click vào:

```text
Browser
```

### Internal link

```text
Click here
      ↓
Page 25
```

Click vào:

```text
PDF page 25
```

Tức là:

```text
Link
├── External URL
└── Internal destination
```

PDFium có API để lấy destination hoặc action của link. ([GitHub][3])

---

# 3. Link có Bounding Box

Điều này nối trực tiếp với Buổi 13.

Một link có:

```text
rectangle
```

Ví dụ:

```text
┌─────────────────────────────┐
│     Click here              │
└─────────────────────────────┘
```

và:

```text
left
bottom
right
top
```

PDFium cung cấp `FPDFLink_GetAnnotRect()` để lấy rectangle của link annotation. ([GitHub][3])

Do đó:

```text
Buổi 13
Text → BoundingBox

Buổi 15
Link → BoundingBox
```

Hai khái niệm này sẽ rất dễ kết hợp.

---

# 4. Link không nhất thiết chứa text

Đây là điều cần nhớ.

Có thể có:

```text
┌─────────────────┐
│                 │
│    IMAGE        │ ← clickable
│                 │
└─────────────────┘
```

Hình ảnh có thể có link annotation.

Vì vậy không được suy luận:

```python
if "http" in text:
    # chắc chắn có link
```

Sai.

Có thể:

```text
Text có URL
+
không có annotation
```

hoặc:

```text
Annotation có URL
+
text không chứa URL
```

---

# 5. pypdfium2 và Link

pypdfium2 là binding ở mức ABI của PDFium và có cả helper API lẫn raw API. Khi helper chưa bao phủ đầy đủ một chức năng, có thể sử dụng `pypdfium2.raw`. README chính thức mô tả rõ cơ chế này. ([GitHub][4])

Đây là một điểm kiến trúc quan trọng:

```text
Application
     ↓
LinkReader
     ↓
pypdfium2 helper / raw API
     ↓
PDFium
```

Không nên để raw PDFium API tràn vào toàn bộ application.

---

# 6. Enumerate Link

Ở tầng PDFium, link annotation trên page được enumerate bằng:

```text
FPDFLink_Enumerate()
```

Nó trả về từng `FPDF_LINK` handle. ([GitHub][3])

Conceptually:

```text
Page
 │
 ├── Link 0
 ├── Link 1
 ├── Link 2
 └── ...
```

Đây là khác với:

```python
for page in pdf:
```

vì chúng ta đang enumerate **object trên một page**.

---

# 7. Link Rectangle

Sau khi có link handle:

```text
FPDF_LINK
```

có thể lấy rectangle:

```text
FPDFLink_GetAnnotRect()
```

Kết quả:

```text
left
bottom
right
top
```

Tức là:

```python
BoundingBox(
    left=...,
    bottom=...,
    right=...,
    top=...,
)
```

Chúng ta có thể **tái sử dụng `BoundingBox` của Buổi 13**.

Đây chính là lợi ích của việc thiết kế domain model tốt.

---

# 8. Domain model `PdfLink`

Tạo:

```text
domain/link.py
```

```python
from dataclasses import dataclass

from .text import BoundingBox


@dataclass(frozen=True)
class PdfLink:
    bbox: BoundingBox
    url: str | None = None
    target_page: int | None = None
```

Ví dụ external:

```python
link = PdfLink(
    bbox=BoundingBox(
        left=100,
        bottom=500,
        right=300,
        top=530,
    ),
    url="https://example.com",
)
```

Internal:

```python
link = PdfLink(
    bbox=BoundingBox(
        left=100,
        bottom=500,
        right=300,
        top=530,
    ),
    target_page=24,
)
```

Ở đây:

```text
target_page = 24
```

có thể quy ước là **0-based page index** trong domain của chúng ta.

---

# 9. Tại sao `url` và `target_page` là optional?

Bởi vì một link có thể có:

```text
External URL
```

hoặc:

```text
Internal destination
```

hoặc action phức tạp hơn.

Không nên thiết kế:

```python
@dataclass
class PdfLink:
    url: str
```

vì internal link không có URL.

---

# 10. External URL

PDFium có thể lấy **Action** của link:

```text
FPDFLink_GetAction()
```

hoặc destination:

```text
FPDFLink_GetDest()
```

theo loại link. ([GitHub][3])

Tư duy:

```text
PdfLink
    │
    ├── rectangle
    │
    └── action
          ├── URL
          ├── GoTo
          └── ...
```

Đây là lý do `PdfLink` nên là domain object thay vì chỉ:

```python
str
```

---

# 11. External và Internal Link

Ta có thể định nghĩa rõ hơn:

```python
from dataclasses import dataclass
from enum import Enum

from .text import BoundingBox


class LinkType(str, Enum):
    EXTERNAL = "external"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PdfLink:
    bbox: BoundingBox
    link_type: LinkType
    url: str | None = None
    target_page: int | None = None
```

Ví dụ:

```python
PdfLink(
    bbox=box,
    link_type=LinkType.EXTERNAL,
    url="https://example.com",
)
```

hoặc:

```python
PdfLink(
    bbox=box,
    link_type=LinkType.INTERNAL,
    target_page=10,
)
```

---

# 12. Annotation model tổng quát

Về lâu dài chúng ta có thể có:

```python
from dataclasses import dataclass
from enum import Enum


class AnnotationType(str, Enum):
    LINK = "link"
    TEXT = "text"
    HIGHLIGHT = "highlight"
    FILE_ATTACHMENT = "file_attachment"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PdfAnnotation:
    annotation_type: AnnotationType
    bbox: BoundingBox
```

Sau đó:

```text
PdfAnnotation
     │
     ├── LinkAnnotation
     ├── TextAnnotation
     ├── HighlightAnnotation
     └── ...
```

Nhưng **chưa cần triển khai toàn bộ hôm nay**.

---

# 13. Vì sao không dùng pypdf?

Bạn có thể thắc mắc:

> "Annotation có thể đọc bằng pypdf, tại sao đang học pypdfium2?"

Đúng. `pypdf` có API đọc annotation trực tiếp từ `/Annots`, `/Subtype`, `/Rect`, v.v. ([GitHub][2])

Nhưng mục tiêu khóa học này là hiểu:

```text
pypdfium2
   ↓
PDFium
   ↓
page geometry
   ↓
render
   ↓
text
   ↓
objects
```

Do đó chúng ta ưu tiên hiểu **PDFium model**.

Trong production, hoàn toàn có thể dùng:

```text
pypdfium2
+
pypdf
```

nếu cần hai nhóm capability khác nhau.

---

# 14. Link annotation vs WebLink detection

Đây là phần **rất quan trọng**.

PDFium có hai khái niệm:

### A. Link annotation

PDF thực sự chứa:

```text
Link Annotation
```

Ví dụ:

```text
[Click here]
```

và PDF biết vùng này clickable.

### B. Web link detection

Trang chỉ chứa:

```text
https://example.com
```

nhưng không có annotation.

PDFium có `FPDFLink_LoadWebLinks()` để tự động phát hiện các URL dạng này trong text content. Header PDFium mô tả rõ đây là các "web links" được phát hiện từ nội dung, và không phải link annotation. ([GitHub][1])

Do đó:

```text
PDF
│
├── Annotation links
│
└── Detected web links
```

là hai nguồn dữ liệu khác nhau.

---

# 15. Ví dụ

PDF A:

```text
Visit:
https://example.com
```

không có annotation.

Ta vẫn có:

```text
Text
 ↓
URL detector
 ↓
https://example.com
```

PDF B:

```text
Visit our website
```

text không chứa URL.

Nhưng:

```text
"Visit our website"
        ↓
Link annotation
        ↓
https://example.com
```

Nếu chỉ tìm:

```python
"http://" in text
```

ta sẽ bỏ sót PDF B.

---

# 16. Tại sao BoundingBox cực kỳ quan trọng?

Giả sử:

```text
Visit our website
```

là text.

Link annotation:

```text
left   = 100
bottom = 500
right  = 250
top    = 530
```

Ta có thể xác định:

```text
Text
"Visit our website"
      │
      ▼
┌──────────────────────┐
│ Visit our website    │
└──────────────────────┘
      ▲
      │
Link rectangle
```

Sau này có thể làm:

```text
PDF reader
    ↓
mouse click
    ↓
point(x, y)
    ↓
find link whose bbox contains point
    ↓
open URL
```

---

# 17. Point-in-rectangle

Ta có:

```python
def contains_point(
    bbox: BoundingBox,
    x: float,
    y: float,
) -> bool:

    return (
        bbox.left <= x <= bbox.right
        and
        bbox.bottom <= y <= bbox.top
    )
```

Ví dụ:

```python
box = BoundingBox(
    left=100,
    bottom=500,
    right=300,
    top=530,
)
```

Click:

```python
contains_point(
    box,
    150,
    515,
)
```

→ `True`.

Click:

```python
contains_point(
    box,
    500,
    515,
)
```

→ `False`.

---

# 18. Đây là nền tảng PDF Reader

Sau này nếu xây reader bằng PySide6:

```text
Mouse click
    ↓
Image coordinate
    ↓
PDF coordinate
    ↓
Point
    ↓
Link bounding boxes
    ↓
Matched PdfLink
    ↓
Open URL
```

Do đó Buổi 15 không chỉ là:

> "Đọc annotation."

Mà còn là nền tảng để xây **interactive PDF reader**.

---

# 19. Coordinate conversion

Ở Buổi 13 ta đã có:

```text
PDF coordinate
     ↓
Image coordinate
```

Bây giờ cần chiều ngược lại.

Nếu:

```text
x_image
y_image
```

và:

```python
scale = dpi / 72
```

thì:

```python
x_pdf = x_image / scale
```

Còn Y cần đảo:

```python
y_pdf = (
    page_height
    - y_image / scale
)
```

Ví dụ:

```python
def image_point_to_pdf_point(
    x: float,
    y: float,
    page_height: float,
    scale: float,
) -> tuple[float, float]:

    pdf_x = x / scale

    pdf_y = (
        page_height
        - y / scale
    )

    return pdf_x, pdf_y
```

---

# 20. Click link hoàn chỉnh

Giả sử:

```text
PIL image
```

có kích thước:

```text
2480 × 3508
```

render ở:

```text
300 DPI
```

thì:

```python
scale = 300 / 72
```

Người dùng click:

```python
x = 500
y = 800
```

Ta chuyển:

```python
pdf_x, pdf_y = image_point_to_pdf_point(
    x,
    y,
    page_height=842,
    scale=300 / 72,
)
```

Sau đó:

```python
for link in links:
    if contains_point(
        link.bbox,
        pdf_x,
        pdf_y,
    ):
        activate(link)
```

Đây là architecture cơ bản của clickable PDF renderer.

---

# 21. `PdfLinkReader`

Giống Buổi 14, ta tạo abstraction:

```python
from collections.abc import Iterator

from domain.link import PdfLink


class LinkReader:

    def iter_links(
        self,
        page,
    ) -> Iterator[PdfLink]:
        ...
```

Infrastructure:

```text
infrastructure/
└── pdfium/
    └── link_reader.py
```

Domain không import:

```python
import pypdfium2
```

---

# 22. Raw API adapter

Với những chức năng link mà helper chưa cung cấp trực tiếp, infrastructure có thể dùng:

```python
import pypdfium2.raw as pdfium_c
```

pypdfium2 chính thức hỗ trợ cách tiếp cận này. Các helper object có thể được truyền trực tiếp cho raw API hoặc lấy `.raw`. ([GitHub][4])

Ví dụ conceptually:

```python
pdfium_c.FPDFLink_Enumerate(...)
```

Nhưng có một điểm rất quan trọng:

**Không nên vội viết ctypes wrapper khắp application.**

Chúng ta gom toàn bộ raw API vào:

```text
infrastructure/pdfium/
```

Ví dụ:

```text
infrastructure/
└── pdfium/
    ├── document.py
    ├── renderer.py
    ├── text_reader.py
    ├── character_reader.py
    └── link_reader.py
```

---

# 23. Một `LinkReader` production-style

Về architecture, ta muốn application chỉ nhìn thấy:

```python
links = link_reader.iter_links(page)
```

chứ không cần biết:

```text
FPDF_LINK
FPDFLink_Enumerate
FPDFLink_GetAnnotRect
FPDFLink_GetAction
FPDFLink_GetDest
```

Luồng:

```text
Application
     │
     ▼
LinkReader
     │
     ▼
PdfiumLinkReader
     │
     ▼
PDFium raw API
```

Đây chính là **Adapter Pattern**.

---

# 24. Không nên biến Link thành string

Sai:

```python
links = [
    "https://example.com",
    "https://google.com",
]
```

Vì mất:

```text
position
page
type
destination
```

Tốt:

```python
PdfLink(
    bbox=...,
    link_type=LinkType.EXTERNAL,
    url="https://example.com",
)
```

---

# 25. Test domain trước

`contains_point()` không cần PDFium.

```python
def test_point_inside():

    box = BoundingBox(
        left=100,
        bottom=500,
        right=300,
        top=530,
    )

    assert contains_point(
        box,
        150,
        515,
    )
```

Ngoài box:

```python
def test_point_outside():

    box = BoundingBox(
        left=100,
        bottom=500,
        right=300,
        top=530,
    )

    assert not contains_point(
        box,
        400,
        515,
    )
```

Đây là unit test rất sạch.

---

# 26. Test Link model

```python
def test_external_link():

    box = BoundingBox(
        left=100,
        bottom=500,
        right=300,
        top=530,
    )

    link = PdfLink(
        bbox=box,
        link_type=LinkType.EXTERNAL,
        url="https://example.com",
    )

    assert link.link_type == LinkType.EXTERNAL
    assert link.url == "https://example.com"
    assert link.target_page is None
```

Internal:

```python
def test_internal_link():

    link = PdfLink(
        bbox=box,
        link_type=LinkType.INTERNAL,
        target_page=10,
    )

    assert link.target_page == 10
    assert link.url is None
```

---

# 27. Annotation không chỉ là Link

Hôm nay chỉ học Link, nhưng hãy hình dung:

```text
PdfAnnotation
│
├── Link
│
├── Highlight
│
├── Text Note
│
├── Stamp
│
├── File Attachment
│
└── Widget
```

Ví dụ highlight có thể có:

```text
/QuadPoints
```

thay vì chỉ một rectangle. Các annotation dạng Highlight thường dùng các quadrilateral points để mô tả vùng được highlight. ([GitHub][2])

Do đó:

```text
Annotation geometry
```

không phải lúc nào cũng đơn giản là:

```text
Rectangle
```

Đây là lý do chúng ta chưa nên thiết kế:

```python
class PdfAnnotation:
    bbox: BoundingBox
```

là toàn bộ abstraction cho mọi loại annotation.

---

# 28. Một thiết kế tốt hơn về lâu dài

Có thể đi theo:

```text
PdfAnnotation
│
├── geometry
│
└── metadata
```

với geometry có thể là:

```text
Rectangle
Quadrilateral
Polygon
...
```

Nhưng hiện tại:

```text
Buổi 15
    ↓
Link
    ↓
Rectangle
```

là đủ.

**Không over-engineer.**

---

# 29. Hai nguồn Link trong hệ thống

Sau Buổi 15, parser của chúng ta nên phân biệt:

```text
                 PDF Page
                    │
           ┌────────┴────────┐
           │                 │
           ▼                 ▼
    Link Annotation      Text Content
           │                 │
           ▼                 ▼
       PdfLink          URL detection
           │                 │
           └────────┬────────┘
                    ▼
              Link Discovery
```

Ví dụ:

```text
Annotation:
"Click here" → https://example.com

Text detection:
"https://google.com"
```

Hai loại đều có thể trở thành:

```text
DiscoveredLink
```

ở application layer.

---

# 30. Kiến trúc tới Buổi 15

Chúng ta hiện có:

```text
                         PdfPage
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
      Renderer          TextPage         Annotations
          │                 │                 │
          ▼          ┌──────┴──────┐          ▼
      PIL.Image      │             │       Links
                     ▼             ▼          │
                   Text      Characters       ▼
                     │             │       PdfLink
                     │             │          │
                     ▼             ▼          ▼
                 TextFragment  PdfCharacter  BBox
```

Đây là một bước tiến rất lớn so với Buổi 11.

---

# 31. Bài tập thực hành

### Bài 1 — `PdfLink`

Tạo:

```python
@dataclass(frozen=True)
class PdfLink:
    bbox: BoundingBox
    link_type: LinkType
    url: str | None = None
    target_page: int | None = None
```

---

### Bài 2 — Point hit testing

Viết:

```python
contains_point(
    bbox,
    x,
    y,
)
```

Test ít nhất:

```text
inside
outside
left edge
right edge
top edge
bottom edge
```

---

### Bài 3 ⭐ — Link Reader

Thiết kế:

```python
class LinkReader(Protocol):

    def iter_links(self, page):
        ...
```

Sau đó tạo:

```text
PdfiumLinkReader
```

ở infrastructure.

---

### Bài 4 ⭐⭐ — Click detection

Xây pipeline:

```text
Mouse(x, y)
    ↓
Image coordinate
    ↓
PDF coordinate
    ↓
for link
    ↓
contains_point()
    ↓
PdfLink
```

---

### Bài 5 ⭐⭐⭐ — URL detection

Tách riêng:

```text
Annotation links
```

và:

```text
Web links detected from text
```

sau đó tạo:

```text
LinkDiscoveryService
```

để hợp nhất kết quả.

---

# 32. Điều cần nhớ nhất

```text
1. Link là annotation/object riêng
```

không đồng nhất với text.

```text
2. Link có geometry
```

thường có rectangle.

```text
3. Link có action/destination
```

có thể là:

```text
URL
Internal page
...
```

```text
4. Link annotation ≠ detected web link
```

PDFium phân biệt hai cơ chế này. ([GitHub][1])

```text
5. BoundingBox tái sử dụng được
```

từ Buổi 13.

```text
6. Raw PDFium API nên nằm trong Infrastructure
```

không để leak vào Domain/Application.

---

## Pipeline sau 15 buổi

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ├─────────────── Render ────────────────► PIL.Image
 │
 ├─────────────── Text ─────────────────► Text
 │                                      │
 │                                      ▼
 │                                  Characters
 │                                      │
 │                                      ▼
 │                                  BBox
 │
 ├─────────────── Links ────────────────► PdfLink
 │                                      │
 │                                      ▼
 │                                     BBox
 │
 └─────────────── Objects ──────────────► Buổi 16
```

**Buổi 16 — Page Objects** sẽ đi sâu vào các object thực sự được đặt trên trang PDF: **text object, image object, path/vector object, form object...**, cách lấy `get_objects()`, object type và bounding box. Đây là bước nối rất tự nhiên từ Link/Annotation sang **phân tích toàn bộ cấu trúc hình học của một PDF page**.

[1]: https://github.com/PDFium/PDFium/blob/master/fpdfsdk/include/fpdftext.h?utm_source=chatgpt.com "PDFium/fpdfsdk/include/fpdftext.h at master · PDFium/PDFium · GitHub"
[2]: https://github.com/py-pdf/pypdf/blob/main/docs/user/reading-pdf-annotations.md?utm_source=chatgpt.com "pypdf/docs/user/reading-pdf-annotations.md at main · py-pdf/pypdf · GitHub"
[3]: https://github.com/documentcloud/pdfium/blob/master/public/fpdf_doc.h?utm_source=chatgpt.com "pdfium/public/fpdf_doc.h at master · documentcloud/pdfium · GitHub"
[4]: https://github.com/pypdfium2-team/pypdfium2/blob/main/README.md?utm_source=chatgpt.com "pypdfium2/README.md at main · pypdfium2-team/pypdfium2 · GitHub"
