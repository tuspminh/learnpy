# Buổi 16 — Page Objects

Hôm nay chúng ta chuyển sang một tầng thấp hơn của PDF:

```text
PDF Page
   ↓
Page Objects
```

Roadmap hiện tại:

```text
11. TextPage
12. Extract text
13. Text position / bounding box
14. Character-level extraction
15. Link / annotation
16. Page objects          ← Hôm nay
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Ở các buổi trước chúng ta đã xử lý:

```text
PdfPage
 ├── Text
 ├── Character
 └── Link
```

Hôm nay muốn nhìn toàn bộ nội dung hình học của một page:

```text
PdfPage
 └── Objects
      ├── Text
      ├── Image
      ├── Path
      ├── Form
      └── ...
```

---

# 1. Page Object là gì?

Hãy tưởng tượng một PDF page như một canvas:

```text
┌───────────────────────────────────┐
│                                   │
│       CHƯƠNG 1                    │ ← Text
│                                   │
│   ┌─────────────────────────┐     │
│   │                         │     │
│   │         IMAGE           │     │ ← Image
│   │                         │     │
│   └─────────────────────────┘     │
│                                   │
│   ───────────────────────────     │ ← Path
│                                   │
└───────────────────────────────────┘
```

Một page có thể chứa nhiều object.

Về mặt khái niệm:

```text
Page
 │
 ├── Text object
 ├── Image object
 ├── Path object
 ├── Form object
 └── ...
```

Mỗi object thường có:

```text
type
geometry
properties
```

---

# 2. Object khác TextPage như thế nào?

Đây là điểm rất quan trọng.

Ở Buổi 11:

```python
textpage = page.get_textpage()
```

`PdfTextPage` là một **cấu trúc phục vụ text extraction**.

Nó cho chúng ta:

```text
Text
Character
Character position
```

Còn page objects là cách nhìn:

```text
"PDF page thực sự chứa những loại object nào?"
```

Ví dụ:

```text
PdfPage
│
├── Text object
├── Image object
├── Path object
└── ...
```

Hai abstraction này **không nên đồng nhất**.

---

# 3. Tư duy quan trọng

Chúng ta có hai cách nhìn một page:

### Text-centric

```text
PdfPage
   ↓
PdfTextPage
   ↓
Characters
   ↓
Words
   ↓
Lines
```

### Object-centric

```text
PdfPage
   ↓
Page Objects
   ├── Text
   ├── Image
   ├── Path
   └── Form
```

Đây là hai pipeline khác nhau:

```text
                PdfPage
               /       \
              /         \
             ▼           ▼
        Text analysis   Object analysis
```

---

# 4. Tại sao Page Objects quan trọng?

Giả sử một PDF có:

```text
┌───────────────────────────────┐
│           BOOK TITLE          │
│                               │
│      ┌───────────────┐        │
│      │    IMAGE      │        │
│      └───────────────┘        │
│                               │
│ Some text                     │
│                               │
└───────────────────────────────┘
```

Nếu chỉ:

```python
textpage.get_text_bounded()
```

ta nhận:

```text
BOOK TITLE

Some text
```

Nhưng không biết:

```text
giữa hai đoạn text có một image
```

Object analysis cho ta:

```text
Text
Image
Text
```

Đây là thông tin rất có giá trị.

---

# 5. pypdfium2 và page objects

pypdfium2 cung cấp API để truy cập page objects thông qua:

```python
page.get_objects()
```

Đây là helper quan trọng khi muốn duyệt các object được PDFium expose trên page.

Tư duy sử dụng:

```python
for obj in page.get_objects():
    print(obj)
```

Thay vì:

```python
for character in textpage:
    ...
```

Ta đang duyệt:

```text
object
object
object
...
```

---

# 6. Object type

Một object cần có loại.

Về PDFium, các page object type chính gồm:

```text
PDF page object
├── Text
├── Path
├── Image
└── Form
```

PDFium định nghĩa các loại object page tương ứng trong public API. pypdfium2 expose chúng ở tầng Python thông qua object wrappers.

Có thể hình dung:

```text
FPDF_PAGEOBJ_TEXT
FPDF_PAGEOBJ_PATH
FPDF_PAGEOBJ_IMAGE
FPDF_PAGEOBJ_FORM
```

---

# 7. Đừng nhầm Path với Image

Ví dụ:

```text
┌───────────────┐
│               │
│    IMAGE      │
│               │
└───────────────┘
```

là image object.

Nhưng:

```text
┌───────────────┐
│               │
│   VECTOR      │
│      ▲        │
│     / \       │
│    /___\      │
│               │
└───────────────┘
```

có thể được tạo bởi path/vector graphics.

Do đó:

```text
Image ≠ Path
```

---

# 8. Object geometry

Đây là phần nối trực tiếp với Buổi 13.

Một page object có thể có bounding rectangle.

Tư duy:

```text
Object
   ↓
BoundingBox
```

Ví dụ:

```text
Image Object

left   = 100
bottom = 300
right  = 500
top    = 600
```

Ta có:

```text
┌────────────────────────┐
│                        │
│        IMAGE           │
│                        │
└────────────────────────┘
```

với:

```python
BoundingBox(
    left=100,
    bottom=300,
    right=500,
    top=600,
)
```

Do đó `BoundingBox` chúng ta đã xây ở Buổi 13 tiếp tục được tái sử dụng.

---

# 9. Một abstraction rất đẹp

Ta có thể tạo:

```python
from dataclasses import dataclass
from enum import Enum

from .text import BoundingBox


class PageObjectType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    PATH = "path"
    FORM = "form"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PageObject:
    object_type: PageObjectType
    bbox: BoundingBox
```

Đây là **domain model**, không phụ thuộc pypdfium2.

---

# 10. Ví dụ

```python
text_object = PageObject(
    object_type=PageObjectType.TEXT,
    bbox=BoundingBox(
        left=100,
        bottom=700,
        right=400,
        top=730,
    ),
)
```

Image:

```python
image_object = PageObject(
    object_type=PageObjectType.IMAGE,
    bbox=BoundingBox(
        left=100,
        bottom=300,
        right=500,
        top=600,
    ),
)
```

Path:

```python
path_object = PageObject(
    object_type=PageObjectType.PATH,
    bbox=BoundingBox(
        left=50,
        bottom=100,
        right=550,
        top=120,
    ),
)
```

---

# 11. Nhưng `PageObject` chỉ là abstraction chung

Không nên dừng mãi ở:

```text
PageObject
```

vì mỗi object type có thông tin riêng.

Ví dụ:

### Text

```text
text
font
font size
color
```

### Image

```text
width
height
image data
metadata
```

### Path

```text
commands
fill
stroke
line width
```

### Form

```text
children
matrix
...
```

Do đó:

```text
PageObject
    │
    ├── TextObject
    ├── ImageObject
    ├── PathObject
    └── FormObject
```

sẽ là hướng phát triển sau này.

---

# 12. Không over-engineer ngay

Ở Buổi 16 chúng ta **không cần** xây:

```text
AbstractPageObject
ConcreteTextObject
ConcreteImageObject
ConcretePathObject
Visitor
Factory
Registry
...
```

Chỉ cần hiểu:

```text
Page
 ↓
Objects
 ↓
Object Type
 ↓
Bounding Box
```

Sau Buổi 17–18 chúng ta sẽ có đủ thông tin để quyết định abstraction sâu hơn.

---

# 13. Duyệt objects

Về mặt sử dụng:

```python
for obj in page.get_objects():
    print(
        type(obj).__name__
    )
```

Mục tiêu debug ban đầu là biết:

```text
Page
 ↓
Object 1
Object 2
Object 3
...
```

Ví dụ một page có thể cho:

```text
PdfTextObject
PdfImageObject
PdfPathObject
PdfTextObject
```

Thứ tự và loại cụ thể phụ thuộc vào nội dung PDF.

---

# 14. `get_objects()` rất hữu ích cho debug

Hãy tưởng tượng parser của bạn không hiểu vì sao:

```text
ảnh không được tìm thấy
```

hoặc:

```text
text không xuất hiện trong extraction
```

Ta có thể debug:

```python
for obj in page.get_objects():
    print(
        type(obj),
        obj
    )
```

Từ đó biết:

```text
PDFium thực sự đang nhìn thấy gì?
```

Đây là một kỹ thuật rất hữu ích khi reverse-engineer PDF.

---

# 15. Page object và render

Một điểm quan trọng:

```text
Page Objects
       ↓
Render
```

PDFium sử dụng page objects để render trang.

Nhưng:

```text
Render result
```

là:

```text
pixels
```

còn:

```text
Page Objects
```

là:

```text
vector/object representation
```

Pipeline:

```text
PDF
 │
 ▼
PdfPage
 │
 ├──────────► Objects
 │
 └──────────► Render
                  │
                  ▼
               Bitmap
                  │
                  ▼
              PIL.Image
```

---

# 16. Một page có thể có object không nhìn thấy rõ

Ví dụ:

```text
Text object
```

có thể nằm:

```text
ngoài vùng crop
```

hoặc:

```text
màu trắng trên nền trắng
```

hoặc:

```text
opacity thấp
```

Do đó:

```text
object exists
```

không đồng nghĩa:

```text
object visibly contributes to rendered image
```

Đây là một distinction rất quan trọng trong document analysis.

---

# 17. Text Object vs TextPage

Đây là câu hỏi dễ xuất hiện:

> Nếu đã có `PdfTextPage`, tại sao cần Text Object?

Bởi vì:

```text
PdfTextPage
```

là **text extraction view**.

Còn:

```text
PdfTextObject
```

là **page object view**.

Ví dụ:

```text
Page
│
├── TextObject A
├── ImageObject
├── TextObject B
└── PathObject
```

TextPage có thể đưa cho bạn:

```text
TextObject A + TextObject B
       ↓
combined text stream
```

Nhưng object traversal cho biết:

```text
Text
Image
Text
Path
```

Thứ tự/representation cũng có thể không hoàn toàn giống nhau.

---

# 18. Object order không nên coi là document order

Đây là cảnh báo quan trọng.

Không nên mặc định:

```python
objects = list(page.get_objects())
```

rồi kết luận:

```text
objects[0] = đọc đầu tiên
objects[1] = đọc thứ hai
```

PDF là một format mô tả việc vẽ nội dung, không phải HTML DOM.

Do đó:

```text
Object order
≠
Reading order
```

Đây chính là một trong những lý do text extraction và layout reconstruction khó.

---

# 19. Object matrix / transformation

Một object trong PDF có thể chịu transformation.

Ví dụ:

```text
Original image
       ↓
scale
       ↓
rotate
       ↓
translate
       ↓
placed on page
```

Vì vậy geometry của image không đơn giản chỉ là:

```text
image.width
image.height
```

mà còn liên quan tới transformation matrix.

Conceptually:

```text
Object
 ├── local geometry
 └── transformation matrix
```

Sau này khi học Image object chúng ta sẽ gặp vấn đề này rõ hơn.

---

# 20. Vì sao Image object là Buổi 17?

Bởi vì:

```text
Page Objects
      ↓
Image Object
```

là bước tự nhiên.

Ở Buổi 17 chúng ta sẽ tìm hiểu:

```text
PdfImageObject
    ↓
Image size
    ↓
Image data
    ↓
Extract image
```

và phân biệt:

```text
Rendered page
```

với:

```text
Original embedded image
```

Đây là hai thứ **hoàn toàn khác nhau**.

---

# 21. Render image vs embedded image

Ví dụ PDF:

```text
PDF
 ├── Text
 └── JPEG image
```

Nếu render:

```text
PDF
 ↓
page.render()
 ↓
PIL.Image
```

ta nhận:

```text
toàn bộ trang
```

bao gồm:

```text
text + image + graphics
```

Nhưng nếu lấy Image object:

```text
PDF
 ↓
Image Object
 ↓
embedded image
```

ta có thể lấy **ảnh gốc được nhúng trong PDF**.

Ví dụ:

```text
PDF page
┌───────────────────────────┐
│ Title                     │
│                           │
│  ┌─────────────────────┐  │
│  │ original JPEG       │  │
│  └─────────────────────┘  │
└───────────────────────────┘
```

Render:

```text
2480 × 3508 PNG
```

Extract embedded image:

```text
1200 × 800 JPEG
```

Đây là hai workflow khác nhau.

---

# 22. Object-level architecture

Ta có thể tạo interface:

```python
from collections.abc import Iterator
from typing import Protocol


class PageObjectReader(Protocol):

    def iter_objects(
        self,
        page,
    ) -> Iterator:
        ...
```

Infrastructure:

```python
class PdfiumPageObjectReader:

    def iter_objects(self, page):
        yield from page.get_objects()
```

Application:

```python
for obj in reader.iter_objects(page):
    ...
```

Domain không cần biết:

```text
pypdfium2
```

---

# 23. Adapter

Architecture:

```text
Application
     │
     ▼
PageObjectReader
     │
     ▼
PdfiumPageObjectReader
     │
     ▼
pypdfium2
     │
     ▼
PDFium
```

Đây tiếp tục là:

```text
Dependency Inversion
+
Adapter Pattern
```

giống các phần chúng ta đã xây trước đó.

---

# 24. Mapping object type

Infrastructure chịu trách nhiệm chuyển:

```text
pypdfium2 object
       ↓
PageObjectType
```

Ví dụ conceptually:

```python
def map_object_type(obj) -> PageObjectType:

    name = type(obj).__name__

    if "Text" in name:
        return PageObjectType.TEXT

    if "Image" in name:
        return PageObjectType.IMAGE

    if "Path" in name:
        return PageObjectType.PATH

    if "Form" in name:
        return PageObjectType.FORM

    return PageObjectType.UNKNOWN
```

Đây chỉ là **demo tư duy**.

Trong production, tốt hơn là dựa vào API/type constants chính thức của pypdfium2 thay vì kiểm tra tên class bằng substring.

---

# 25. Tách mapper

Không nên để:

```python
PdfiumPageObjectReader
```

vừa:

```text
enumerate
+
map
+
validate
+
business logic
```

Tách:

```text
PdfiumPageObjectReader
       ↓
PageObjectMapper
       ↓
PageObject
```

Architecture:

```text
PDFium Object
      ↓
Reader
      ↓
Mapper
      ↓
Domain PageObject
```

---

# 26. Domain model hoàn chỉnh hơn

Ta có thể mở rộng:

```python
from dataclasses import dataclass
from enum import Enum

from .text import BoundingBox


class PageObjectType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    PATH = "path"
    FORM = "form"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PageObject:
    object_type: PageObjectType
    bbox: BoundingBox
```

Sau này:

```text
PageObject
    │
    ├── object_type
    └── bbox
```

là base class/domain record.

---

# 27. Test object model

```python
def test_page_object():

    box = BoundingBox(
        left=100,
        bottom=200,
        right=300,
        top=500,
    )

    obj = PageObject(
        object_type=PageObjectType.IMAGE,
        bbox=box,
    )

    assert obj.object_type == PageObjectType.IMAGE
    assert obj.bbox.width == 200
    assert obj.bbox.height == 300
```

Không cần PDF.

---

# 28. Fake Page

Test reader:

```python
class FakePage:

    def get_objects(self):

        return [
            "object-1",
            "object-2",
            "object-3",
        ]
```

Reader:

```python
class FakePageObjectReader:

    def iter_objects(self, page):

        yield from page.get_objects()
```

Test:

```python
def test_iter_objects():

    page = FakePage()

    reader = FakePageObjectReader()

    objects = list(
        reader.iter_objects(page)
    )

    assert objects == [
        "object-1",
        "object-2",
        "object-3",
    ]
```

---

# 29. Một use case thực tế: detect scanned PDF

Đây là một ứng dụng thú vị.

Giả sử PDF scan:

```text
Page
└── Image
```

Text layer:

```text
TextPage
└── ""
```

Ta có:

```text
text_count = 0
image_count > 0
```

→ có khả năng là scanned PDF.

PDF text:

```text
Page
├── Text
├── Text
└── ...
```

thì:

```text
text_count > 0
```

Có thể là text PDF.

Nhưng đây vẫn chỉ là heuristic.

---

# 30. Scan detection tốt hơn

Không nên:

```python
if image_count > 0:
    scanned = True
```

vì PDF text bình thường cũng có thể chứa:

```text
Text + Image
```

Ví dụ sách:

```text
Text
Image
Text
```

Một heuristic tốt hơn có thể kết hợp:

```text
text amount
+
image coverage
+
page dimensions
+
number of text objects
```

Ví dụ:

```text
Text gần như không có
+
Image phủ gần toàn page
```

→ khả năng scan cao.

---

# 31. Object coverage

Giả sử:

```text
page_width
page_height
```

và image:

```text
image_width
image_height
```

coverage:

```python
coverage = (
    image_width * image_height
) / (
    page_width * page_height
)
```

Ví dụ:

```text
coverage = 0.98
```

thì image gần phủ toàn page.

Nếu:

```text
coverage = 0.15
```

thì có thể chỉ là một hình minh họa.

Đây là nền tảng cho:

```text
Scan Detector
```

sau này.

---

# 32. Page analysis model

Ta có thể hình dung một service:

```text
PageAnalyzer
      │
      ├── text objects
      ├── image objects
      ├── path objects
      └── annotations
```

Kết quả:

```python
@dataclass(frozen=True)
class PageAnalysis:
    object_count: int
    text_count: int
    image_count: int
    path_count: int
    link_count: int
```

Ví dụ:

```text
PageAnalysis(
    object_count=17,
    text_count=12,
    image_count=2,
    path_count=3,
    link_count=1,
)
```

Đây là một **read model** rất hữu ích.

---

# 33. Tại sao PageAnalysis hữu ích?

Dashboard crawler/PDF processor sau này có thể hiển thị:

```text
PDF: novel.pdf

Pages: 120

Text pages: 117
Scanned pages: 3

Images: 240
Links: 38
```

Hoặc:

```text
Page 25

Text objects: 17
Images: 2
Paths: 8
Links: 3
```

---

# 34. Nhưng chưa xây `PageAnalyzer` hôm nay

Roadmap vẫn là:

```text
16. Page Objects
17. Images
18. Font / text info
19. Crop
20. Mini Project
```

Chúng ta chỉ cần xây nền:

```text
Page
 ↓
Objects
 ↓
Object Type
 ↓
BoundingBox
```

Buổi 17 sẽ làm rõ Image Object.

---

# 35. Bài tập thực hành

## Bài 1 — Domain model

Tạo:

```python
class PageObjectType(Enum):
    TEXT
    IMAGE
    PATH
    FORM
    UNKNOWN
```

và:

```python
@dataclass(frozen=True)
class PageObject:
    object_type: PageObjectType
    bbox: BoundingBox
```

---

## Bài 2 — Enumerate objects

Với một PDF thật:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    for obj in page.get_objects():
        print(type(obj).__name__)

finally:
    pdf.close()
```

Mục tiêu:

> Xem PDF của bạn thực sự chứa những loại object nào.

---

## Bài 3 ⭐ — Object geometry

Tìm cách lấy geometry/bounds của các object mà pypdfium2 expose.

In:

```text
Object type
left
bottom
right
top
```

Đừng vội assume mọi object đều có cùng API geometry.

---

## Bài 4 ⭐⭐ — Page statistics

Tạo:

```python
PageStatistics
```

để thống kê:

```text
Text objects
Image objects
Path objects
Form objects
Unknown objects
```

---

## Bài 5 ⭐⭐⭐ — Scan detector

Xây heuristic:

```text
Page
 ↓
Objects
 ↓
Text count
+
Image count
+
Image coverage
 ↓
likely_scanned
```

Ví dụ:

```python
PageScanInfo(
    likely_scanned=True,
    text_objects=0,
    image_objects=1,
    image_coverage=0.98,
)
```

---

# 36. Một lưu ý về API thực tế

`page.get_objects()` là abstraction thuận tiện, nhưng **không nên viết parser production dựa trên việc đoán tên class hoặc giả định mọi object có cùng property**.

Ví dụ không nên:

```python
obj.bbox
```

một cách mù quáng cho mọi object.

Hãy kiểm tra API/type cụ thể của pypdfium2 version đang cài.

Đây cũng là lý do architecture:

```text
pypdfium2
    ↓
Adapter
    ↓
Domain model
```

rất hữu ích.

Nếu pypdfium2 thay đổi wrapper:

```text
Infrastructure thay đổi
```

thay vì:

```text
Toàn bộ Application thay đổi
```

---

# 37. Kiến trúc sau Buổi 16

Hệ thống hiện tại:

```text
                           PdfPage
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
    Renderer              TextPage             Objects
        │                     │                     │
        ▼               ┌─────┴─────┐               ▼
    PIL.Image            │           │         PageObject
                         ▼           ▼              │
                       Text     Characters          ├── type
                                    │               └── bbox
                                    ▼
                                   BBox

                              Annotations
                                   │
                                   ▼
                                 Links
                                   │
                                   ▼
                                  BBox
```

Chúng ta đang dần xây một **PDF domain model** thay vì chỉ viết vài hàm đọc PDF.

---

# 38. Toàn bộ tiến trình từ Buổi 11 → 16

```text
Buổi 11
PdfTextPage
    ↓

Buổi 12
Text extraction
    ↓

Buổi 13
Text + BoundingBox
    ↓

Buổi 14
Character + BoundingBox
    ↓

Buổi 15
Link + BoundingBox
    ↓

Buổi 16
Page Object + BoundingBox
```

Điểm chung:

```text
              PDF Page
                  │
                  ▼
             Geometry
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     Text      Character    Link
       │          │          │
       └──────────┼──────────┘
                  │
                BBox
```

Đây là một abstraction cực kỳ quan trọng cho toàn bộ phần còn lại.

---

# 39. Điều cần nhớ nhất

### 1. Page Object

```text
object trên PDF page
```

không phải chỉ là text.

### 2. Các loại chính

```text
Text
Image
Path
Form
```

### 3. Object có geometry

```text
BoundingBox
```

### 4. Object order không đồng nghĩa reading order

PDF không phải HTML.

### 5. `PdfTextPage` và Page Objects là hai view khác nhau

```text
TextPage
→ text analysis

Page Objects
→ object analysis
```

### 6. Infrastructure nên che giấu PDFium

```text
pypdfium2
     ↓
Adapter
     ↓
Domain
```

---

## Buổi 17 — Images trong PDF

Buổi tiếp theo sẽ đi sâu vào **Image Object**, một phần rất quan trọng đối với PDF crawler/document processor:

```text
PdfPage
   ↓
Image Objects
   ↓
embedded image
   ├── width
   ├── height
   ├── pixel format
   ├── raw image data
   └── extraction
```

Đặc biệt chúng ta sẽ phân biệt rõ:

```text
PDF page
   ↓
render()
   ↓
ảnh của TOÀN TRANG
```

với:

```text
PDF page
   ↓
Image Object
   ↓
ảnh GỐC được nhúng trong PDF
```

Hai thứ này rất dễ bị nhầm và sẽ là trọng tâm của **Buổi 17**.
