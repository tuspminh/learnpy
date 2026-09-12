# Buổi 17 — Images trong PDF

Hôm nay chúng ta đi vào một phần rất quan trọng của `pypdfium2`: **phân tích và lấy các image object được nhúng bên trong PDF**.

Đây là điểm cần phân biệt thật rõ:

```text
PDF
 │
 ├── Text object
 ├── Image object  ← hôm nay
 ├── Path object
 ├── Form object
 └── ...
```

**Render PDF → PNG** mà chúng ta đã học trước đây là:

```text
PDF Page
   ↓
PDFium render
   ↓
Bitmap
   ↓
PIL Image
```

Còn hôm nay là:

```text
PDF Page
   ↓
Page Objects
   ↓
Image Object
   ↓
Embedded Image
   ↓
PIL Image / metadata
```

Hai khái niệm này **không giống nhau**.

pypdfium2 hiện cung cấp `page.get_objects()` để duyệt các object trên trang; PDFium cũng có API riêng để lấy bitmap, metadata và dữ liệu của image object. ([GitHub][1])

---

# 1. Mục tiêu Buổi 17

Sau bài này bạn sẽ hiểu:

```text
1. Image object là gì?
2. Image trong PDF khác rendered page như thế nào?
3. Tìm image object bằng get_objects()
4. Xác định bounding box
5. Xác định kích thước image
6. Lấy bitmap của image
7. Phân biệt:
      original image
      rendered image
      page screenshot
8. Thiết kế ImageReader theo Clean Architecture
9. Viết chương trình trích xuất image
10. Viết test
```

---

# 2. Một PDF có thể chứa image như thế nào?

Ví dụ một trang:

```text
+---------------------------------------+
|                                       |
|       Tiêu đề                         |
|                                       |
|       +-----------------------+       |
|       |                       |       |
|       |       IMAGE           |       |
|       |                       |       |
|       +-----------------------+       |
|                                       |
|       Nội dung văn bản                |
|                                       |
+---------------------------------------+
```

Về mặt page objects:

```text
PdfPage
│
├── TextObject
├── TextObject
├── ImageObject
├── TextObject
├── PathObject
└── ...
```

Khi gọi:

```python
page.get_objects()
```

ta có thể duyệt qua các object đó.

Ví dụ:

```python
for obj in page.get_objects():
    print(
        obj.level,
        obj.type,
        obj.get_bounds(),
    )
```

Đây cũng chính là cách được minh họa trong README chính thức của pypdfium2. ([GitHub][1])

---

# 3. Image object khác gì với ảnh render của trang?

Đây là phần **cực kỳ quan trọng**.

## Cách 1 — Render cả page

```python
bitmap = page.render(scale=2)
image = bitmap.to_pil()
```

Kết quả:

```text
PDF Page
 ├── text
 ├── image
 ├── line
 ├── shape
 └── ...

        ↓ render

┌───────────────────────┐
│      TITLE            │
│                       │
│      [ IMAGE ]        │
│                       │
│      paragraph...     │
└───────────────────────┘
```

Bạn nhận được **toàn bộ trang**.

---

## Cách 2 — lấy Image Object

Nếu PDF chứa:

```text
Image A
```

thì ta có thể lấy riêng:

```text
Image A
```

không cần render toàn bộ trang.

---

# 4. Ví dụ thực tế

Giả sử PDF là một cuốn truyện scan:

```text
page 1
┌────────────────────────┐
│                        │
│     scanned page       │
│                        │
└────────────────────────┘
```

PDF có thể chứa:

```text
ImageObject
```

với kích thước:

```text
2480 × 3508 px
```

Nếu bạn render page ở 150 DPI:

```text
PDF
 ↓
render(scale=150/72)
 ↓
~1240 × 1754 px
```

Bạn đã **downscale** ảnh.

Nhưng nếu lấy embedded image:

```text
ImageObject
 ↓
2480 × 3508 px
```

thì có thể giữ được dữ liệu gốc tốt hơn.

---

# 5. Tìm image object

Bắt đầu từ kiến thức Buổi 16.

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    for obj in page.get_objects():
        print("level:", obj.level)
        print("type:", obj.type)
        print("bounds:", obj.get_bounds())
        print("-" * 40)

finally:
    pdf.close()
```

Bạn có thể nhận được dạng:

```text
level: 0
type: 1
bounds: (50.0, 700.0, 550.0, 800.0)

level: 0
type: 3
bounds: (100.0, 300.0, 500.0, 650.0)
```

**Không nên đoán số `type` bằng tay trong production code.**

Thay vào đó, sử dụng các constant/type được pypdfium2 expose trong phiên bản bạn đang dùng.

---

# 6. Lọc image object

Ý tưởng:

```python
for obj in page.get_objects():
    if obj.type == IMAGE_TYPE:
        ...
```

pypdfium2 cũng hỗ trợ lọc object theo type trong các API hiện tại. Một ví dụ thực tế từ Docling sử dụng:

```python
page.get_objects(filter=[obj_type])
```

để lấy riêng image objects. ([GitHub][2])

Vì API type constants có thể khác cách đặt tên giữa các version, trước hết hãy kiểm tra:

```python
import pypdfium2.raw as pdfium_c

print(pdfium_c.FPDF_PAGEOBJ_IMAGE)
```

Thông thường chúng ta sẽ dùng:

```python
pdfium_c.FPDF_PAGEOBJ_IMAGE
```

---

# 7. Chương trình liệt kê tất cả image

Tạo:

```text
list_images.py
```

Code hoàn chỉnh:

```python
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c


def inspect_images(pdf_path: str) -> None:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(path)

    pdf = pdfium.PdfDocument(path)

    try:
        print(f"PDF: {path}")
        print(f"Pages: {len(pdf)}")
        print()

        for page_index in range(len(pdf)):
            page = pdf[page_index]

            print("=" * 60)
            print(f"PAGE {page_index + 1}")

            image_count = 0

            for obj in page.get_objects(
                filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]
            ):
                image_count += 1

                bounds = obj.get_bounds()

                print(f"Image #{image_count}")
                print(f"  bounds = {bounds}")

            print(f"Total images: {image_count}")

    finally:
        pdf.close()


if __name__ == "__main__":
    inspect_images("sample.pdf")
```

Chạy:

```bash
python list_images.py
```

Ví dụ:

```text
PDF: sample.pdf
Pages: 10

============================================================
PAGE 1
Image #1
  bounds = (50.0, 100.0, 550.0, 700.0)
Total images: 1

============================================================
PAGE 2
Total images: 0

============================================================
PAGE 3
Image #1
  bounds = (80.0, 200.0, 500.0, 600.0)
Image #2
  bounds = (100.0, 100.0, 300.0, 180.0)
Total images: 2
```

---

# 8. Bounding Box của image

Ví dụ:

```python
bounds = obj.get_bounds()
```

trả về:

```python
(
    left,
    bottom,
    right,
    top,
)
```

Ví dụ:

```python
(100, 200, 500, 700)
```

Ta có:

```text
left   = 100
bottom = 200
right  = 500
top    = 700
```

Do đó:

```python
width = right - left
height = top - bottom
```

Kết quả:

```text
width  = 400
height = 500
```

---

# 9. Tạo BoundingBox dùng chung

Chúng ta đã có concept này từ Buổi 13.

Tạo:

```text
domain/
    geometry.py
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
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.left + self.right) / 2,
            (self.bottom + self.top) / 2,
        )
```

Test:

```python
box = BoundingBox(
    left=100,
    bottom=200,
    right=500,
    top=700,
)

print(box.width)
print(box.height)
print(box.area)
print(box.center)
```

Kết quả:

```text
400
500
200000
(300.0, 450.0)
```

---

# 10. Image Domain Model

Bây giờ tạo model:

```text
domain/
    image.py
```

```python
from dataclasses import dataclass

from .geometry import BoundingBox


@dataclass(frozen=True)
class PdfImage:
    page_index: int
    image_index: int
    bbox: BoundingBox

    pixel_width: int | None = None
    pixel_height: int | None = None
    bits_per_pixel: int | None = None
```

Ta đang cố tình **không import pypdfium2**.

Đây là nguyên tắc Clean Architecture:

```text
domain
   ↑
application
   ↑
infrastructure
   ↑
pypdfium2
```

Không:

```text
domain
   ↓
pypdfium2
```

---

# 11. Metadata của image

PDFium cung cấp API để lấy metadata của image object, bao gồm:

```text
dimension
DPI
bits per pixel
colorspace
```

thông qua `FPDFImageObj_GetImageMetadata`. ([GitHub][3])

Đây là thông tin rất hữu ích.

Ví dụ:

```text
Image
├── width       = 2480
├── height      = 3508
├── DPI         = 300
├── BPP         = 24
└── colorspace  = RGB
```

---

# 12. Một điểm rất quan trọng: image có transform

Image object trong PDF không đơn giản chỉ là:

```text
x
y
width
height
```

PDFium có image transformation matrix:

```text
| a c e |
| b d f |
| 0 0 1 |
```

Nó có thể biểu diễn:

```text
scale
rotate
shear
translate
```

PDFium có `FPDFImageObj_GetMatrix()` để lấy transformation matrix của image object. ([GitHub][3])

Ví dụ một image:

```text
original:

████████
████████
████████
```

có thể được đặt lên page với:

```text
scale
+
rotation
+
translation
```

Do đó:

```text
embedded image dimensions
```

không nhất thiết bằng:

```text
displayed dimensions trên page
```

Đây là một distinction rất quan trọng khi xây PDF parser.

---

# 13. Lấy bitmap của image

PDFium có API:

```text
FPDFImageObj_GetBitmap()
```

để lấy bitmap rasterized của image object. ([GitHub][3])

Ở tầng pypdfium2, cách dùng cụ thể phụ thuộc version/helper wrapper hiện tại.

Vì vậy **không nên tự đoán tên method wrapper**.

Ta có thể kiểm tra object:

```python
for obj in page.get_objects(
    filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]
):
    print(type(obj))
    print(dir(obj))
```

Đây là kỹ thuật rất quan trọng khi học thư viện native binding.

---

# 14. Reflection để khám phá API

Tạo:

```python
def inspect_image_object(obj) -> None:
    print(type(obj))
    print()

    for name in dir(obj):
        if not name.startswith("_"):
            print(name)
```

Dùng:

```python
for obj in page.get_objects(
    filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]
):
    inspect_image_object(obj)
```

Bạn sẽ thấy các method mà **version pypdfium2 đang cài thực sự cung cấp**.

Đây là cách tốt hơn việc copy API từ một version cũ.

---

# 15. Vì sao tôi chưa cho bạn code "extract_image()" cố định?

Vì có 3 tầng API:

```text
pypdfium2 helper
        ↓
pypdfium2.raw
        ↓
PDFium C API
```

README chính thức cho thấy pypdfium2 cung cấp cả helper API và raw API. ([GitHub][1])

Trong các version khác nhau:

```text
helper API
```

có thể thay đổi.

Trong khi:

```text
PDFium ABI/API
```

là tầng thấp hơn.

Vì vậy architecture tốt là:

```text
Application
      ↓
ImageReader
      ↓
PdfiumImageReader
      ↓
pypdfium2 helper/raw
      ↓
PDFium
```

Sau này nếu API helper thay đổi:

```text
Application
      X
```

không bị ảnh hưởng.

---

# 16. Thiết kế ImageReader

Ta tạo interface:

```text
application/
    image_reader.py
```

```python
from typing import Protocol

from domain.image import PdfImage


class ImageReader(Protocol):

    def read_page_images(
        self,
        page,
        page_index: int,
    ) -> list[PdfImage]:
        ...
```

---

# 17. Infrastructure implementation

```python
from domain.geometry import BoundingBox
from domain.image import PdfImage


class PdfiumImageReader:

    def read_page_images(
        self,
        page,
        page_index: int,
    ) -> list[PdfImage]:

        import pypdfium2.raw as pdfium_c

        images: list[PdfImage] = []

        objects = page.get_objects(
            filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]
        )

        for image_index, obj in enumerate(objects):

            left, bottom, right, top = obj.get_bounds()

            bbox = BoundingBox(
                left=left,
                bottom=bottom,
                right=right,
                top=top,
            )

            image = PdfImage(
                page_index=page_index,
                image_index=image_index,
                bbox=bbox,
            )

            images.append(image)

        return images
```

Chú ý:

`PdfiumImageReader` mới được phép biết:

```python
import pypdfium2
```

Domain không biết.

---

# 18. ImageExtractor

Application layer:

```python
class ImageExtractor:

    def __init__(self, reader):
        self.reader = reader

    def extract_page(
        self,
        page,
        page_index: int,
    ):
        return self.reader.read_page_images(
            page,
            page_index,
        )
```

Sử dụng:

```python
pdf = pdfium.PdfDocument("sample.pdf")

try:
    reader = PdfiumImageReader()
    extractor = ImageExtractor(reader)

    page = pdf[0]

    images = extractor.extract_page(
        page,
        page_index=0,
    )

    for image in images:
        print(image)

finally:
    pdf.close()
```

---

# 19. Extract toàn bộ PDF

Ta dùng generator, giống phần Text.

```python
class ImageExtractor:

    def __init__(self, reader):
        self.reader = reader

    def iter_pdf(self, pdf):

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            images = self.reader.read_page_images(
                page,
                page_index,
            )

            for image in images:
                yield image
```

Sử dụng:

```python
pdf = pdfium.PdfDocument("sample.pdf")

try:
    reader = PdfiumImageReader()
    extractor = ImageExtractor(reader)

    for image in extractor.iter_pdf(pdf):
        print(
            image.page_index,
            image.image_index,
            image.bbox,
        )

finally:
    pdf.close()
```

Đây là pattern rất phù hợp với PDF lớn:

```text
PDF
 ↓
Page 1
 ↓
images
 ↓
Page 2
 ↓
images
 ↓
Page 3
 ↓
...
```

Không cần:

```python
all_images = []
```

cho toàn bộ document.

---

# 20. Phân biệt 3 loại "ảnh"

Đây là phần bạn cần ghi nhớ.

## A. Embedded Image

```text
PDF
 ↓
Image Object
 ↓
original/decoded image
```

Ví dụ:

```text
2480 × 3508
```

---

## B. Rendered Image Object

```text
Image Object
 ↓
PDFium rasterization
 ↓
Bitmap
```

Image được rasterize theo object.

---

## C. Rendered Page

```text
Entire PDF Page
 ↓
PDFium
 ↓
Bitmap
```

Bao gồm:

```text
text
image
vector
shape
annotation
...
```

---

# 21. Ví dụ trực quan

PDF:

```text
┌─────────────────────────────┐
│          TITLE              │
│                             │
│     ┌───────────────┐       │
│     │               │       │
│     │     IMAGE     │       │
│     │               │       │
│     └───────────────┘       │
│                             │
│     Some text here...       │
│                             │
└─────────────────────────────┘
```

### Render page

```text
PNG

┌─────────────────────────────┐
│          TITLE              │
│                             │
│     ┌───────────────┐       │
│     │     IMAGE     │       │
│     └───────────────┘       │
│                             │
│     Some text here...       │
└─────────────────────────────┘
```

### Extract image

```text
┌───────────────┐
│               │
│     IMAGE     │
│               │
└───────────────┘
```

Đây là hai workflow hoàn toàn khác nhau.

---

# 22. Scan detection

Kiến thức Buổi 16 bây giờ trở nên hữu ích.

Ta có:

```text
text objects
image objects
path objects
```

Có thể xây heuristic:

```python
def is_likely_scanned_page(
    text_count: int,
    image_count: int,
) -> bool:

    return text_count == 0 and image_count >= 1
```

Nhưng **đây chỉ là heuristic**.

Không được kết luận:

```text
image_count > 0
→ scanned PDF
```

vì một PDF bình thường có thể chứa:

```text
text
+
logo image
+
icons
```

---

# 23. Heuristic tốt hơn

Ví dụ:

```python
def is_likely_scanned_page(
    page_width: float,
    page_height: float,
    text_count: int,
    image_boxes: list[BoundingBox],
) -> bool:

    if text_count > 0:
        return False

    page_area = page_width * page_height

    if page_area <= 0:
        return False

    largest_area = max(
        (box.area for box in image_boxes),
        default=0,
    )

    coverage = largest_area / page_area

    return coverage >= 0.70
```

Ý tưởng:

```text
Không có text
        +
Có image lớn
        +
image chiếm > 70% page
        ↓
likely scanned page
```

Nhưng vẫn chỉ là:

```text
likely
```

không phải:

```text
guaranteed
```

---

# 24. Test Domain Model

Ta không cần pypdfium2 để test.

```python
from domain.geometry import BoundingBox
from domain.image import PdfImage


def test_image_bbox():

    bbox = BoundingBox(
        left=10,
        bottom=20,
        right=110,
        top=220,
    )

    image = PdfImage(
        page_index=0,
        image_index=0,
        bbox=bbox,
    )

    assert image.bbox.width == 100
    assert image.bbox.height == 200
    assert image.bbox.area == 20_000
```

Chạy:

```bash
pytest
```

---

# 25. Fake ImageReader

Đây mới là phần quan trọng đối với architecture.

```python
from domain.geometry import BoundingBox
from domain.image import PdfImage


class FakeImageReader:

    def read_page_images(
        self,
        page,
        page_index,
    ):

        return [
            PdfImage(
                page_index=page_index,
                image_index=0,
                bbox=BoundingBox(
                    left=0,
                    bottom=0,
                    right=100,
                    top=200,
                ),
            )
        ]
```

Test:

```python
def test_image_extractor():

    reader = FakeImageReader()

    extractor = ImageExtractor(reader)

    images = extractor.extract_page(
        page=object(),
        page_index=0,
    )

    assert len(images) == 1
    assert images[0].page_index == 0
    assert images[0].bbox.width == 100
```

Application test:

```text
không cần PDF
không cần pypdfium2
không cần file thật
```

Đây chính là lợi ích của Dependency Inversion.

---

# 26. Kiến trúc sau Buổi 17

Bây giờ hệ thống của chúng ta bắt đầu có nhiều "view" của PDF:

```text
                         ┌── TextPage
                         │
PdfDocument → PdfPage ───┼── Page Objects
                         │
                         ├── Links
                         │
                         └── Images
```

Application:

```text
PdfTextExtractor
PdfImageExtractor
PdfLinkReader
PdfPageObjectReader
```

Infrastructure:

```text
PdfiumTextReader
PdfiumImageReader
PdfiumLinkReader
PdfiumPageObjectReader
```

Domain:

```text
PageText
PdfCharacter
BoundingBox
PdfLink
PdfImage
PageObject
```

Đây chính là nền móng rất tốt cho PDF analysis engine.

---

# 27. Cấu trúc project hiện tại

Tôi đề xuất từ Buổi 17 bắt đầu gom code như sau:

```text
pdf_analyzer/
│
├── domain/
│   ├── __init__.py
│   ├── geometry.py
│   ├── text.py
│   ├── image.py
│   ├── link.py
│   └── page_object.py
│
├── application/
│   ├── text_extractor.py
│   ├── image_extractor.py
│   ├── link_extractor.py
│   └── page_object_reader.py
│
├── infrastructure/
│   └── pdfium/
│       ├── text_reader.py
│       ├── image_reader.py
│       ├── link_reader.py
│       └── page_object_reader.py
│
└── tests/
    ├── test_geometry.py
    ├── test_text.py
    ├── test_image.py
    └── test_link.py
```

Điểm rất đẹp là:

```text
pypdfium2
```

chỉ xuất hiện trong:

```text
infrastructure/pdfium/
```

---

# 28. Bài thực hành

## Bài 1

Viết:

```python
list_images(pdf_path)
```

in:

```text
Page 1:
    Image 1
    bounds
    width
    height

Page 2:
    Image 1
    bounds
    width
    height
```

---

## Bài 2

Viết:

```python
count_images(pdf_path)
```

trả về:

```python
{
    0: 1,
    1: 0,
    2: 3,
}
```

nghĩa là:

```text
page 1 → 1 image
page 2 → 0 image
page 3 → 3 images
```

---

## Bài 3

Viết:

```python
find_image_heavy_pages(pdf_path)
```

trả về các page có:

```text
image coverage >= 70%
```

---

## Bài 4

Viết:

```python
ImageExtractor
```

có:

```python
extract_page()
iter_pdf()
```

và **không import pypdfium2**.

---

# 29. Một lưu ý rất quan trọng về "extract ảnh gốc"

PDFium phân biệt nhiều thao tác:

```text
GetBitmap
GetRenderedBitmap
GetImageDataDecoded
GetImageDataRaw
GetImageMetadata
```

Trong đó:

```text
GetImageDataRaw
```

là dữ liệu ảnh raw được lưu trong PDF.

```text
GetImageDataDecoded
```

là dữ liệu sau khi PDFium giải mã filter.

```text
GetBitmap
```

là bitmap rasterized.

```text
GetRenderedBitmap
```

có thể tính đến image mask và transformation matrix. PDFium mô tả rõ những khác biệt này trong API image object. ([GitHub][3])

Cho nên **"trích xuất ảnh" không phải chỉ có một nghĩa**.

Sau này chúng ta sẽ phải quyết định:

```text
Tôi muốn:
    ├── ảnh gốc?
    ├── ảnh decoded?
    ├── ảnh rendered?
    └── ảnh theo appearance trên page?
```

Đây là lý do hôm nay chúng ta tập trung trước vào **Image Object + metadata + geometry**, thay vì vội viết một hàm `extract_image()` chung chung.

---

# 30. Tóm tắt Buổi 17

Bạn cần nhớ 8 ý chính:

```text
1. PDF page chứa Image Object.

2. page.get_objects() cho phép duyệt page objects.

3. Image Object khác với ảnh render toàn trang.

4. Image có bounding box trên PDF canvas.

5. Image có thể có transformation matrix.

6. PDFium cung cấp metadata của image:
   size / DPI / BPP / colorspace.

7. Embedded image và rendered image là hai khái niệm khác nhau.

8. pypdfium2 chỉ nên nằm ở Infrastructure.
```

Kiến trúc hiện tại:

```text
                  PDF
                   │
               PdfDocument
                   │
                PdfPage
                   │
       ┌───────────┼────────────┐
       ↓           ↓            ↓
   TextPage    PageObjects    Links
       │           │
       ↓           ↓
   TextReader   ImageReader
       │           │
       ↓           ↓
   PageText     PdfImage
```

**Buổi 18 — Font và text information** sẽ nối trực tiếp từ phần TextPage/Character mà ta đã học, đi sâu vào thông tin font, font size và cách phân tích text layout.

[1]: https://github.com/pypdfium2-team/pypdfium2/blob/main/README.md?utm_source=chatgpt.com "pypdfium2/README.md at main · pypdfium2-team/pypdfium2 · GitHub"
[2]: https://github.com/docling-project/docling/blob/main/docling/backend/pypdfium2_backend.py?utm_source=chatgpt.com "docling/docling/backend/pypdfium2_backend.py at main · docling-project/docling · GitHub"
[3]: https://github.com/prepare/pdfium/blob/master/public/fpdf_edit.h?utm_source=chatgpt.com "pdfium/public/fpdf_edit.h at master · prepare/pdfium · GitHub"
