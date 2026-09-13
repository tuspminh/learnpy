# Buổi 28 — Render Region

Hôm nay chúng ta ghép các kiến thức:

```text
CropBox
PageSize
Coordinate System
BoundingBox
DPI
Rotation
```

để thực hiện một thao tác rất thực tế:

> **Chỉ render một vùng của PDF thay vì render toàn bộ page rồi crop bằng PIL.**

Ví dụ:

```text
PDF Page
┌──────────────────────────────┐
│                              │
│       ┌──────────────┐       │
│       │              │       │
│       │    REGION    │       │
│       │              │       │
│       └──────────────┘       │
│                              │
└──────────────────────────────┘
```

Mục tiêu cuối bài:

```python
image = renderer.render_region(
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

---

# 1. Render toàn trang khác Render Region

Render toàn trang:

```python
page.render(
    scale=2
)
```

Pipeline:

```text
PDF Page
   ↓
PDFium
   ↓
Full Bitmap
   ↓
PIL
```

Nếu sau đó:

```python
image.crop(...)
```

thì chúng ta đã:

```text
Render toàn bộ
       ↓
Bitmap rất lớn
       ↓
PIL crop
       ↓
vùng nhỏ
```

Trong khi Render Region:

```text
PDF Page
       ↓
chọn region
       ↓
PDFium
       ↓
Bitmap chỉ chứa region
```

Điểm khác biệt rất quan trọng:

```text
Full render + PIL crop
    → tốn memory hơn

Render region
    → bitmap nhỏ hơn ngay từ đầu
```

---

# 2. Ví dụ thực tế

Giả sử A4:

```text
595 × 842 pt
```

300 DPI:

```text
2480 × 3508 px
```

Toàn trang:

```text
2480 × 3508
≈ 8.7 triệu pixels
```

Nhưng ta chỉ cần vùng:

```text
200 × 300 pt
```

Ở 300 DPI:

```text
200 × 300 × (300/72)^2
```

chỉ khoảng:

```text
694 × 1250 px
```

Chênh lệch rất lớn.

---

# 3. Region là gì?

Chúng ta đã có `BoundingBox`:

```python
BoundingBox(
    left=100,
    bottom=200,
    right=500,
    top=700,
)
```

Nó biểu diễn:

```text
         top = 700
         ┌─────────────────┐
         │                 │
         │     REGION      │
         │                 │
         └─────────────────┘
bottom = 200

left = 100
right = 500
```

Width:

```text
500 - 100 = 400 pt
```

Height:

```text
700 - 200 = 500 pt
```

---

# 4. Region phải nằm trong Page

Trước khi render:

```text
Region ⊆ Page
```

Ví dụ:

```text
Page:
0,0 → 595,842

Region:
100,200 → 500,700
```

hợp lệ.

Nhưng:

```text
Region:
500,700 → 700,900
```

vượt khỏi page.

Có hai chiến lược:

### Strategy A — Reject

```text
Invalid region
     ↓
ValueError
```

### Strategy B — Clamp

```text
Region vượt page
       ↓
cắt về boundary page
```

Trong renderer core, tôi khuyên:

> **Reject trước.**

Bởi vì silently clamp có thể che giấu bug trong application.

Nếu muốn clamp, hãy để một service riêng làm việc đó.

---

# 5. Tạo `RenderRegion`

Có thể dùng trực tiếp `BoundingBox`.

Nhưng về domain semantics, tôi thích tạo:

```python
@dataclass(frozen=True)
class RenderRegion:
    bounds: BoundingBox
```

Tuy nhiên ở giai đoạn hiện tại chúng ta **không cần abstraction thêm**.

Dùng:

```python
BoundingBox
```

là đủ.

Đây cũng phù hợp với nguyên tắc chúng ta đã theo từ đầu:

> Không abstraction chỉ để abstraction.

---

# 6. Kiểm tra region

Thêm:

```python
def validate_region(
    page_box: BoundingBox,
    region: BoundingBox,
) -> None:

    if not page_box.contains(region):
        raise ValueError(
            "Region nằm ngoài page"
        )
```

Ví dụ:

```python
page_box = BoundingBox(
    0,
    0,
    595,
    842,
)

region = BoundingBox(
    100,
    200,
    500,
    700,
)

validate_region(page_box, region)
```

Không lỗi.

---

# 7. Region và Coordinate System

Đây là phần quan trọng nhất.

`BoundingBox` của chúng ta đang dùng:

```text
PDF coordinate system
```

tức:

```text
bottom-left
```

Trong khi render API có thể cần crop rectangle theo convention riêng của PDFium/pypdfium2.

Vì vậy:

```text
BoundingBox
    ↓
Coordinate transformation
    ↓
PDFium crop rectangle
    ↓
page.render(...)
```

**Không nên**:

```python
page.render(crop=(
    region.left,
    region.bottom,
    region.right,
    region.top,
))
```

mà chưa xác định chính xác semantics của `crop`.

Đây là điểm chúng ta phải rất cẩn thận với API version của pypdfium2.

---

# 8. Kiểm tra API pypdfium2

Với pypdfium2, `page.render()` có hỗ trợ:

```python
page.render(
    scale=...,
    crop=...
)
```

nhưng semantics của `crop` phải được hiểu theo API hiện tại thay vì tự suy luận từ `BoundingBox`.

Trong project production, nguyên tắc của chúng ta là:

```text
Domain coordinate
       ↓
Adapter
       ↓
pypdfium2 coordinate convention
```

Không để domain phụ thuộc pypdfium2.

---

# 9. Thiết kế `RegionCropper`

Ta tạo một adapter:

```text
infrastructure/pdfium/crop.py
```

```python
from domain.geometry import BoundingBox


class PdfiumCropConverter:

    def __init__(
        self,
        page_width: float,
        page_height: float,
    ):
        self.page_width = page_width
        self.page_height = page_height

    def convert(
        self,
        region: BoundingBox,
    ):
        ...
```

Nhưng trước khi điền công thức, chúng ta cần xác định coordinate convention của `crop`.

Đây chính là lý do Buổi 27 vừa học:

```text
PDF coordinate
        ↓
Image coordinate
```

---

# 10. Tư duy Render Region đúng

Ta không nên nghĩ:

```text
BoundingBox
   ↓
crop tuple
```

mà nên nghĩ:

```text
Domain Region
      ↓
Region Validation
      ↓
Coordinate Transformation
      ↓
PDFium Render Region
      ↓
Bitmap
```

Đây là architecture sạch hơn.

---

# 11. `RegionRenderer`

Bây giờ xây abstraction:

```python
from abc import ABC, abstractmethod

from domain.geometry import BoundingBox


class RegionRenderer(ABC):

    @abstractmethod
    def render_region(
        self,
        page_index: int,
        region: BoundingBox,
        dpi: float,
    ):
        ...
```

Nhưng tôi **không khuyên** tạo interface này nếu renderer hiện tại chỉ có một implementation.

Ta có thể bắt đầu đơn giản:

```python
class PdfRenderer:
    ...
```

rồi thêm:

```python
render_region()
```

---

# 12. Mở rộng `PdfRenderer`

Ví dụ architecture:

```python
class PdfRenderer:

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):
        ...

    def render_region(
        self,
        page_index: int,
        region: BoundingBox,
        options: RenderOptions,
    ):
        ...
```

Hai method cùng thuộc trách nhiệm:

> PDF → bitmap

nên hiện tại đặt cùng class là hợp lý.

---

# 13. Validate page

Ta có:

```python
def get_page(self, page_index):
    ...
```

Render region:

```python
def render_region(
    self,
    page_index: int,
    region: BoundingBox,
    options: RenderOptions,
):
    page = self.document.get_page(page_index)

    width, height = page.get_size()

    page_box = BoundingBox(
        0,
        0,
        width,
        height,
    )

    if not page_box.contains(region):
        raise ValueError(
            "Region nằm ngoài page"
        )

    ...
```

Nhưng có một điểm cần cải tiến.

---

# 14. Không nên dùng `get_size()` thay cho mọi box

Ở Buổi 25–26 chúng ta đã phân biệt:

```text
MediaBox
CropBox
PageSize
```

Nếu application muốn render theo **CropBox**, thì page boundary phải là:

```python
page.get_cropbox()
```

Nếu muốn render theo MediaBox:

```python
page.get_mediabox()
```

Do đó tốt hơn:

```python
class PageGeometryReader:
    ...
```

để application có geometry chính xác.

---

# 15. `RenderRegionService`

Ta có thể tạo:

```python
class RenderRegionService:

    def __init__(
        self,
        renderer,
        geometry_reader,
    ):
        self.renderer = renderer
        self.geometry_reader = geometry_reader

    def render(
        self,
        page_index,
        region,
        options,
    ):
        geometry = self.geometry_reader.read(
            page_index
        )

        if not geometry.page_box.contains(region):
            raise ValueError(
                "Region nằm ngoài page"
            )

        return self.renderer.render_region(
            page_index,
            region,
            options,
        )
```

Nhưng lại xuất hiện một câu hỏi:

> `renderer` hay service chịu trách nhiệm validation?

Với architecture hiện tại:

```text
Application
   ↓
RenderRegionService
   ↓
Renderer
```

thì validation nghiệp vụ nên ở Application.

Renderer vẫn phải có validation defensive.

---

# 16. Region → expected pixel size

Đây là phần rất dễ kiểm chứng.

Region:

```text
400 × 500 pt
```

DPI:

```text
150
```

scale:

```text
150 / 72
≈ 2.0833
```

Pixel:

```text
width:
400 × 2.0833
≈ 833
```

```text
height:
500 × 2.0833
≈ 1042
```

Vậy expected:

```text
833 × 1042 px
```

Đây là một test rất tốt.

---

# 17. Hàm tính kích thước Region

Không cần render để biết kích thước.

```python
def region_pixel_size(
    region: BoundingBox,
    dpi: float,
):
    if dpi <= 0:
        raise ValueError(
            "DPI phải > 0"
        )

    scale = dpi / 72.0

    width = round(region.width * scale)
    height = round(region.height * scale)

    return width, height
```

Test:

```python
def test_region_pixel_size():
    region = BoundingBox(
        100,
        200,
        500,
        700,
    )

    width, height = region_pixel_size(
        region,
        dpi=150,
    )

    assert width == 833
    assert height == 1042
```

---

# 18. Đây là một điểm architecture rất hay

Ta có thể kiểm tra:

```text
Expected size
       ↓
Actual bitmap size
```

Ví dụ:

```python
expected_width, expected_height = (
    region_pixel_size(region, options.dpi)
)

bitmap = renderer.render_region(...)

actual_width = bitmap.width
actual_height = bitmap.height
```

Nếu lệch:

```text
Expected:
833 × 1042

Actual:
832 × 1042
```

thì có thể do:

* rounding;
* PDFium crop semantics;
* rotation;
* coordinate conversion;
* crop boundary.

Đây là một debugging technique rất tốt.

---

# 19. Render Region không nhất thiết chỉ dùng cho crop ảnh

Đây là nơi tính năng này trở nên rất mạnh.

## Trường hợp 1 — Text highlight

Ta tìm:

```text
"Chapter 10"
```

Text extraction trả:

```text
BoundingBox
```

Sau đó:

```text
BoundingBox
     ↓
render_region()
     ↓
ảnh chỉ chứa text
```

---

## Trường hợp 2 — OCR

Một PDF scan có page rất lớn:

```text
2480 × 3508
```

Nhưng chỉ cần OCR vùng:

```text
200 × 500 pt
```

thì render region sẽ giảm đáng kể dữ liệu đưa vào OCR.

---

## Trường hợp 3 — Preview

Reader cần preview một vùng:

```text
User zoom
    ↓
viewport
    ↓
render region
```

Thay vì:

```text
render full page
    ↓
scale
    ↓
crop
```

---

# 20. Render Region + Text BoundingBox

Đây là pipeline rất quan trọng với project PDF của chúng ta:

```text
PDF
 │
 ├───────────────┐
 │               │
 ▼               ▼
TextPage       Renderer
 │               │
 ▼               │
Text search      │
 │               │
 ▼               │
BoundingBox      │
 │               │
 └───────┬───────┘
         ▼
   render_region()
         │
         ▼
       Bitmap
```

Sau này có thể xây:

```text
PDF Search
```

theo kiểu:

```text
Search "hello"
      ↓
Character / text match
      ↓
BoundingBox
      ↓
Render region
      ↓
Preview
```

---

# 21. Crop Region khác CropBox

Cần ghi nhớ:

```text
CropBox
```

là thuộc tính của PDF page.

Còn:

```text
Render Region
```

là vùng mà **ứng dụng yêu cầu renderer lấy trong lần render đó**.

Ví dụ:

```text
Page
┌────────────────────────────┐
│                            │
│  CropBox                   │
│  ┌──────────────────────┐  │
│  │                      │  │
│  │   Render Region      │  │
│  │   ┌──────────────┐   │  │
│  │   │              │   │  │
│  │   └──────────────┘   │  │
│  │                      │  │
│  └──────────────────────┘  │
│                            │
└────────────────────────────┘
```

Có thể:

```text
MediaBox
  >
CropBox
  >
Render Region
```

nhưng không phải lúc nào application cũng phải tuân theo hierarchy này; nó phụ thuộc nghiệp vụ và boundary mà renderer sử dụng.

---

# 22. Thiết kế API cuối bài

Tôi đề xuất API hiện tại:

```python
class PdfRenderer:

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):
        ...

    def render_region(
        self,
        page_index: int,
        region: BoundingBox,
        options: RenderOptions,
    ):
        ...
```

Sử dụng:

```python
options = RenderOptions(
    dpi=150,
)

region = BoundingBox(
    left=100,
    bottom=200,
    right=500,
    top=700,
)

image = renderer.render_region(
    page_index=0,
    region=region,
    options=options,
)
```

---

# 23. Một abstraction rất hữu ích: `RenderRequest`

Khi options bắt đầu nhiều:

```text
dpi
grayscale
transparent
rotation
region
```

API:

```python
render_page(
    page_index,
    dpi,
    grayscale,
    transparent,
    rotation,
    ...
)
```

sẽ rất xấu.

Ta đã có:

```python
RenderOptions
```

nên giữ:

```python
render_page(
    page_index,
    options,
)
```

và region là parameter riêng:

```python
render_region(
    page_index,
    region,
    options,
)
```

Điều này rõ ràng hơn.

---

# 24. Nhưng hãy tránh abstraction quá sớm

Không nên ngay lập tức tạo:

```text
RenderRequest
RenderRegionRequest
RenderContext
RenderSpecification
RenderPolicy
RenderStrategy
RenderCoordinateAdapter
RenderBoundaryResolver
```

cho một tính năng đơn giản.

Hiện tại:

```text
RenderOptions
BoundingBox
PdfRenderer
```

là đủ.

Sau này khi:

```text
rotation
crop
zoom
viewport
tile
thumbnail
```

phát triển, lúc đó mới refactor.

Đây chính là **SOLID nhưng không over-engineering**.

---

# 25. Test quan trọng nhất

Chúng ta cần test domain trước:

```python
def test_region_inside_page():
    page = BoundingBox(
        0,
        0,
        595.28,
        841.89,
    )

    region = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert page.contains(region)
```

Test invalid:

```python
def test_region_outside_page():
    page = BoundingBox(
        0,
        0,
        595.28,
        841.89,
    )

    region = BoundingBox(
        500,
        700,
        700,
        900,
    )

    assert not page.contains(region)
```

---

# 26. Test pixel size

```python
def test_region_pixel_size():
    region = BoundingBox(
        100,
        200,
        500,
        700,
    )

    width, height = region_pixel_size(
        region,
        dpi=150,
    )

    assert width == 833
    assert height == 1042
```

Test DPI:

```python
import pytest


def test_invalid_dpi():
    region = BoundingBox(
        100,
        200,
        500,
        700,
    )

    with pytest.raises(ValueError):
        region_pixel_size(
            region,
            dpi=0,
        )
```

---

# 27. Một vấn đề rất quan trọng: Rotation

Nếu:

```python
rotation = 90
```

thì:

```text
region width
      ↕
region height
```

có thể bị đảo trong bitmap.

Ví dụ:

```text
Region:
400 × 500 pt
```

90°:

```text
500 × 400 pt
```

Ở đây `region_pixel_size()` đơn giản ở trên **chưa tính rotation**.

Điều này không phải bug.

Nó chỉ có nghĩa:

> Hàm đó đang tính kích thước region trong coordinate system chưa rotate.

Để tính **output bitmap size**, ta cần:

```text
Region
  ↓
Rotation transformation
  ↓
Scale
  ↓
PixelSize
```

Đây là nơi Buổi 27 bắt đầu phát huy tác dụng.

---

# 28. Region với Rotation

Kiến trúc đúng:

```text
RenderRegion
      │
      ▼
CoordinateTransformer
      │
      ├── rotation
      ├── crop
      └── scale
      │
      ▼
Pdfium Renderer
      │
      ▼
Bitmap
```

Không nên:

```text
PdfRenderer
    ├── calculate rotation
    ├── calculate crop
    ├── calculate coordinates
    ├── calculate pixel size
    ├── grayscale
    └── transparency
```

Nếu làm vậy renderer sẽ trở thành God Object.

---

# 29. Render Region trong project Novel/PDF

Liên hệ với hệ thống đọc truyện/PDF của bạn:

```text
PDF Chapter
    ↓
Page
    ↓
Text extraction
    ↓
Character / Line / Word
    ↓
BoundingBox
```

Reader có thể yêu cầu:

```text
"Hiển thị vùng chứa đoạn text này"
```

Application:

```python
region = text_block.bbox

image = renderer.render_region(
    page_index=page_index,
    region=region,
    options=options,
)
```

Như vậy PDF renderer trở thành một infrastructure component rất sạch.

---

# 30. Kiến trúc sau Buổi 28

```text
                       Application
                           │
                           ▼
                  PdfRenderService
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        RenderOptions              BoundingBox
              │                         │
              └────────────┬────────────┘
                           ▼
                    Coordinate
                    Transformer
                           │
                           ▼
                      PdfRenderer
                           │
                           ▼
                       pypdfium2
                           │
                           ▼
                        PdfPage
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
               full render   region render
                    │             │
                    └──────┬──────┘
                           ▼
                       PdfBitmap
                           │
                           ▼
                         PIL
```

---

# 31. Ba loại crop cần phân biệt

Đến thời điểm này chúng ta có **3 khái niệm khác nhau**:

```text
1. CropBox
   ↓
PDF page property
```

```text
2. Render Region
   ↓
region cho một lần rendering
```

```text
3. PIL crop
   ↓
crop bitmap sau rendering
```

Pipeline:

```text
PDF
 │
 ├── CropBox
 │
 ▼
Renderer
 │
 ├── Render Region
 │
 ▼
Bitmap
 │
 └── PIL crop
```

Về hiệu năng:

```text
Render Region
    > thường tốt hơn
Full Render + PIL crop
```

khi vùng cần lấy nhỏ hơn đáng kể so với toàn page.

---

# 32. Một nguyên tắc performance quan trọng

Nếu chỉ cần:

```text
100 × 100 pt
```

trên page:

```text
600 × 800 pt
```

đừng làm:

```text
600 × 800
    ↓
render
    ↓
PIL crop
    ↓
100 × 100
```

nếu PDFium có thể render trực tiếp region phù hợp.

Nên hướng tới:

```text
600 × 800
       │
       └── region 100 × 100
                  ↓
               render
                  ↓
             bitmap nhỏ
```

Điều này sẽ đặc biệt quan trọng ở:

**Buổi 29 — Tối ưu memory khi render PDF lớn.**

---

# 33. Tổng kết Buổi 28

Ta đã xây dựng được tư duy:

```text
Region
   ↓
validate
   ↓
coordinate transform
   ↓
scale / rotation
   ↓
PDFium
   ↓
Bitmap
```

Và phân biệt rõ:

```text
MediaBox
CropBox
Render Region
PIL Crop
```

Công thức cơ bản khi **chưa rotation**:

```text
region_width_pt
    = right - left

region_height_pt
    = top - bottom
```

và:

```text
scale = DPI / 72
```

```text
pixel_width
    ≈ region_width_pt × scale

pixel_height
    ≈ region_height_pt × scale
```

Nhưng khi có:

```text
rotation
crop coordinate transformation
```

thì phải để `CoordinateTransformer` xử lý thay vì tự tính trong renderer.

---

# Roadmap hiện tại

```text
21 Render chất lượng cao       ✅
22 Grayscale                   ✅
23 Transparency                ✅
24 Rotation                    ✅
25 CropBox / MediaBox          ✅
26 Page Size                   ✅
27 Coordinate System           ✅
28 Render Region               ✅
29 Memory Optimization         ← tiếp theo
30 PDF Thumbnail Generator
```

## Buổi 29 sẽ rất thực tế

Chúng ta sẽ lấy một PDF lớn và phân tích:

```text
PDF 500 pages
       ↓
render từng page
       ↓
memory tăng thế nào?
```

Sau đó thiết kế:

```text
Streaming render
Page-by-page processing
Lazy iteration
Bitmap lifetime
PIL image lifetime
Explicit close()
Garbage collection
```

và quan trọng nhất:

```text
Không bao giờ giữ
500 PdfBitmap / PIL.Image
trong RAM
```

đồng thời xây một `PdfRenderIterator` phù hợp với architecture hiện tại.
