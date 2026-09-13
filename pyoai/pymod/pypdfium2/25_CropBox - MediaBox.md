# Buổi 25 — CropBox / MediaBox

Hôm nay chúng ta đi vào một phần rất quan trọng khi làm PDF rendering: **MediaBox và CropBox**.

Đây cũng là nền tảng để sau này xử lý:

* crop trang;
* render vùng cụ thể;
* xác định kích thước thực của trang;
* chuyển đổi tọa độ;
* thumbnail;
* PDF viewer;
* cắt phần lề của trang.

Trong pypdfium2 hiện tại có sẵn các API như `page.get_mediabox()`, `page.get_cropbox()` và `page.get_bbox()`. ([GitHub][1])

---

# 1. Trước hết: PDF page không chỉ có một "kích thước"

Một lỗi phổ biến khi mới học PDF là nghĩ:

```text
PDF Page
└── width × height
```

Thực tế PDF page có nhiều boundary box:

```text
MediaBox
CropBox
BleedBox
TrimBox
ArtBox
```

Trong bài này tập trung:

```text
MediaBox
CropBox
```

Có thể hình dung:

```text
┌──────────────────────────────────┐
│                                  │
│          MediaBox                │
│                                  │
│    ┌────────────────────────┐    │
│    │                        │    │
│    │       CropBox          │    │
│    │                        │    │
│    │      CONTENT           │    │
│    │                        │    │
│    └────────────────────────┘    │
│                                  │
└──────────────────────────────────┘
```

---

# 2. MediaBox là gì?

**MediaBox** mô tả toàn bộ vùng trang vật lý.

Ví dụ:

```text
MediaBox = (0, 0, 612, 792)
```

Đây là:

```text
width  = 612 pt
height = 792 pt
```

Vì:

```text
72 pt = 1 inch
```

nên:

```text
612 / 72 = 8.5 inch
792 / 72 = 11 inch
```

Tức là:

```text
Letter
8.5 × 11 inch
```

---

# 3. CropBox là gì?

**CropBox** xác định vùng được dùng khi trang PDF được hiển thị hoặc in.

Ví dụ:

```text
MediaBox
(0, 0, 612, 792)

CropBox
(36, 36, 576, 756)
```

Ta có:

```text
MediaBox
┌───────────────────────────────┐
│                               │
│    CropBox                    │
│    ┌─────────────────────┐    │
│    │                     │    │
│    │      content        │    │
│    │                     │    │
│    └─────────────────────┘    │
│                               │
└───────────────────────────────┘
```

CropBox thường được dùng để **clip vùng hiển thị của trang**. Nếu CropBox không được khai báo riêng thì nó mặc định theo MediaBox. ([GitHub][2])

---

# 4. Điểm rất quan trọng

Đừng nhầm:

```text
CropBox
```

với:

```text
page.render(crop=...)
```

Đây là **hai khái niệm khác nhau**.

### CropBox

Là thuộc tính hình học của PDF page.

```text
PDF
└── Page
    ├── MediaBox
    └── CropBox
```

### render(crop=...)

Là yêu cầu:

> "Lần render này chỉ lấy vùng này."

Ví dụ:

```python
page.render(
    scale=2,
    crop=(100, 100, 500, 700),
)
```

Đây là **render-time crop**, không nhất thiết thay đổi CropBox của PDF.

pypdfium2 README cũng phân biệt việc render toàn trang với việc lấy text theo một rectangular area. ([GitHub][3])

---

# 5. Đọc MediaBox bằng pypdfium2

Ví dụ:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("sample.pdf")

page = pdf[0]

media_box = page.get_mediabox()

print(media_box)
```

Tùy version, kết quả là một tuple dạng:

```python
(x0, y0, x1, y1)
```

Ví dụ:

```python
(0.0, 0.0, 612.0, 792.0)
```

Ta có:

```text
left   = 0
bottom = 0
right  = 612
top    = 792
```

---

# 6. Đọc CropBox

Tương tự:

```python
crop_box = page.get_cropbox()

print(crop_box)
```

Ví dụ:

```python
(36.0, 36.0, 576.0, 756.0)
```

Ta có:

```text
CropBox width

576 - 36
= 540 pt
```

và:

```text
CropBox height

756 - 36
= 720 pt
```

---

# 7. `get_size()` thì sao?

Đây là chỗ rất dễ nhầm.

Ta đã học:

```python
width, height = page.get_size()
```

Theo README của pypdfium2, `get_size()` trả kích thước page theo PDF canvas units. ([GitHub][3])

Trong các pipeline xử lý PDF, **không nên tự suy luận rằng `get_size()` luôn chính xác là MediaBox hay CropBox trong mọi trường hợp đặc biệt**.

Thay vào đó, nếu nghiệp vụ cần biết boundary cụ thể:

```python
page.get_mediabox()
page.get_cropbox()
```

hãy lấy trực tiếp boundary tương ứng.

Đây là nguyên tắc quan trọng:

```text
Cần kích thước render
        ↓
get_size()

Cần MediaBox
        ↓
get_mediabox()

Cần CropBox
        ↓
get_cropbox()
```

---

# 8. `get_bbox()` là gì?

pypdfium2 cũng có:

```python
page.get_bbox()
```

Một backend thực tế sử dụng pypdfium2 cho document processing lấy:

```python
bbox = page.get_bbox()
media_box = page.get_mediabox()
crop_box = page.get_cropbox()
```

và xem `get_bbox()` như bounding box chính của page, trong khi vẫn giữ riêng từng loại box. ([GitHub][1])

Ta có thể kiểm tra:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("sample.pdf")
page = pdf[0]

print("SIZE:")
print(page.get_size())

print("BBOX:")
print(page.get_bbox())

print("MEDIA:")
print(page.get_mediabox())

print("CROP:")
print(page.get_cropbox())
```

---

# 9. Xây Domain Model cho PageBox

Với kiến trúc mà chúng ta đang xây dựng, tôi **không muốn Application layer biết tuple của pypdfium2**.

Không nên:

```python
media_box = page.get_mediabox()
```

rồi truyền tuple khắp application.

Thay vào đó:

```text
pypdfium2
    ↓
Infrastructure
    ↓
PageBox
    ↓
Application
```

---

## `domain/page_box.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PageBox:
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

    @property
    def origin(self) -> tuple[float, float]:
        return self.left, self.bottom

    @property
    def size(self) -> tuple[float, float]:
        return self.width, self.height

    def contains(self, other: "PageBox") -> bool:
        return (
            self.left <= other.left
            and self.bottom <= other.bottom
            and self.right >= other.right
            and self.top >= other.top
        )
```

---

# 10. Chuyển tuple PDFium → Domain

Ta tạo một mapper nhỏ:

```python
from domain.page_box import PageBox


class PageBoxMapper:

    @staticmethod
    def from_tuple(
        value: tuple[float, float, float, float]
    ) -> PageBox:
        left, bottom, right, top = value

        return PageBox(
            left=left,
            bottom=bottom,
            right=right,
            top=top,
        )
```

Bây giờ infrastructure:

```python
import pypdfium2 as pdfium

from domain.page_box import PageBox
from infrastructure.pdfium.page_box_mapper import PageBoxMapper


class PdfiumPageGeometry:

    def __init__(self, page):
        self.page = page

    def media_box(self) -> PageBox:
        value = self.page.get_mediabox()

        return PageBoxMapper.from_tuple(value)

    def crop_box(self) -> PageBox:
        value = self.page.get_cropbox()

        return PageBoxMapper.from_tuple(value)
```

---

# 11. Tạo PageGeometry

Thay vì Application phải gọi nhiều method, ta tạo một object:

```python
from dataclasses import dataclass

from domain.page_box import PageBox


@dataclass(frozen=True)
class PageGeometry:
    media_box: PageBox
    crop_box: PageBox

    @property
    def media_size(self):
        return self.media_box.size

    @property
    def crop_size(self):
        return self.crop_box.size
```

Infrastructure:

```python
class PdfiumPageGeometryReader:

    def read(self, page) -> PageGeometry:
        media = PageBoxMapper.from_tuple(
            page.get_mediabox()
        )

        crop = PageBoxMapper.from_tuple(
            page.get_cropbox()
        )

        return PageGeometry(
            media_box=media,
            crop_box=crop,
        )
```

---

# 12. Sử dụng

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("sample.pdf")

page = pdf[0]

reader = PdfiumPageGeometryReader()

geometry = reader.read(page)

print("MediaBox:")
print(geometry.media_box)

print("Media size:")
print(geometry.media_size)

print("CropBox:")
print(geometry.crop_box)

print("Crop size:")
print(geometry.crop_size)
```

Ví dụ output:

```text
MediaBox:
PageBox(left=0.0, bottom=0.0, right=612.0, top=792.0)

Media size:
(612.0, 792.0)

CropBox:
PageBox(left=36.0, bottom=36.0, right=576.0, top=756.0)

Crop size:
(540.0, 720.0)
```

---

# 13. CropBox nằm trong MediaBox

Thông thường ta kỳ vọng:

```text
CropBox ⊆ MediaBox
```

Ta có thể kiểm tra:

```python
if not geometry.media_box.contains(
    geometry.crop_box
):
    raise ValueError(
        "CropBox nằm ngoài MediaBox"
    )
```

Tuy nhiên trong production code, đừng quá đơn giản hóa PDF specification thành một giả định cứng cho mọi malformed PDF. PDF thực tế có thể chứa dữ liệu không chuẩn.

---

# 14. Render CropBox

Đây mới là phần cực kỳ quan trọng đối với project của chúng ta.

Giả sử:

```text
MediaBox

0,0 ───────────────────── 612,792
 │
 │
 │    CropBox
 │    36,36 ───────── 576,756
 │       │
 │       │ CONTENT
 │       │
```

Ta muốn render **chỉ CropBox**.

pypdfium2 hỗ trợ `crop` trong `page.render()`. Một backend thực tế cũng chuyển CropBox sang hệ tọa độ phù hợp rồi truyền vào `render(crop=...)`. ([GitHub][1])

Ví dụ cơ bản:

```python
media = page.get_mediabox()
crop = page.get_cropbox()

print("Media:", media)
print("Crop:", crop)
```

Sau đó cần đặc biệt chú ý **hệ tọa độ**.

---

# 15. Vì sao CropBox không thể đơn giản truyền thẳng?

PDF coordinate system mà chúng ta đang sử dụng:

```text
          y
          ↑
          │
          │
          │
(0,0) ────┼────────→ x
```

Tức là:

```text
bottom-left origin
```

Trong khi nhiều image/render APIs dùng:

```text
(0,0)
  ┌──────────────→ x
  │
  │
  ↓
  y
```

tức:

```text
top-left origin
```

Vì vậy:

```python
crop_box = page.get_cropbox()
```

không có nghĩa:

```python
page.render(crop=crop_box)
```

lúc nào cũng đúng về mặt semantic.

Đây chính là lý do **Buổi 27 — Coordinate System** sẽ rất quan trọng.

---

# 16. Công thức chuyển CropBox

Giả sử:

```python
crop = (
    left,
    bottom,
    right,
    top,
)
```

và page:

```python
width, height = page.get_size()
```

Nếu cần chuyển sang hệ tọa độ top-left:

```python
new_top = height - top
new_bottom = height - bottom
```

Ví dụ:

```text
Page height = 792

CropBox:
bottom = 36
top    = 756
```

Chuyển:

```text
top-left top
= 792 - 756
= 36

top-left bottom
= 792 - 36
= 756
```

Như vậy:

```text
PDF coordinates

(36,756)
   ┌─────────────┐
   │             │
   │   CropBox   │
   │             │
   └─────────────┘
(36,36)


Top-left coordinates

(36,36)
   ┌─────────────┐
   │             │
   │   CropBox   │
   │             │
   └─────────────┘
(36,756)
```

---

# 17. Tạo converter riêng

Không viết logic này trong renderer.

```python
from domain.page_box import PageBox


class PdfCoordinateConverter:

    @staticmethod
    def bottom_left_to_top_left(
        box: PageBox,
        page_height: float,
    ) -> PageBox:

        return PageBox(
            left=box.left,
            bottom=page_height - box.top,
            right=box.right,
            top=page_height - box.bottom,
        )
```

Tên property `bottom` / `top` ở đây hơi gây nhầm vì ta đang chuyển hệ tọa độ.

Trong project thực tế, tốt hơn nữa là từ Buổi 27 chúng ta sẽ có:

```text
CoordinateSystem
```

thay vì tự dùng các phép toán rải rác.

---

# 18. CropBox vs render crop

Đây là bảng cần nhớ:

| Khái niệm          | Ý nghĩa                        |
| ------------------ | ------------------------------ |
| MediaBox           | Toàn bộ physical page boundary |
| CropBox            | Vùng page được clip/display    |
| `render(crop=...)` | Crop cho một lần render        |
| `get_size()`       | Kích thước page theo PDFium    |
| `get_mediabox()`   | Đọc MediaBox                   |
| `get_cropbox()`    | Đọc CropBox                    |

Quan trọng nhất:

```text
CropBox ≠ render(crop=...)
```

---

# 19. Kiến trúc sau Buổi 25

Hiện tại kiến trúc rendering của chúng ta đang tiến tới:

```text
                    Application
                         │
                         ▼
                 PdfRenderService
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       RenderOptions          PageGeometry
              │                     │
              │              ┌──────┴──────┐
              │              │             │
              │              ▼             ▼
              │          MediaBox       CropBox
              │
              ▼
         PdfRenderer
              │
              ▼
          pypdfium2
              │
              ▼
           PdfPage
```

Và infrastructure chịu trách nhiệm:

```text
pypdfium2
   │
   ├── get_size()
   ├── get_mediabox()
   ├── get_cropbox()
   └── render()
          │
          ▼
       Domain
```

Application không cần biết tuple PDFium.

---

# 20. Test Domain

`tests/test_page_box.py`

```python
import pytest

from domain.page_box import PageBox


def test_page_box_size():
    box = PageBox(
        left=0,
        bottom=0,
        right=612,
        top=792,
    )

    assert box.width == 612
    assert box.height == 792


def test_page_box_area():
    box = PageBox(
        left=0,
        bottom=0,
        right=100,
        top=200,
    )

    assert box.area == 20_000


def test_contains():
    media = PageBox(
        0,
        0,
        612,
        792,
    )

    crop = PageBox(
        36,
        36,
        576,
        756,
    )

    assert media.contains(crop)


def test_invalid_box():
    with pytest.raises(ValueError):
        PageBox(
            left=100,
            bottom=0,
            right=50,
            top=100,
        )
```

Chạy:

```bash
pytest
```

---

# 21. Một bài thực hành rất quan trọng

Viết:

```python
def inspect_page_geometry(pdf_path, page_index):
    ...
```

Output:

```text
Page 1

SIZE
  width  : ...
  height : ...

MEDIA BOX
  left   : ...
  bottom : ...
  right  : ...
  top    : ...
  width  : ...
  height : ...

CROP BOX
  left   : ...
  bottom : ...
  right  : ...
  top    : ...
  width  : ...
  height : ...
```

Ví dụ:

```python
import pypdfium2 as pdfium


def inspect_page_geometry(
    pdf_path: str,
    page_index: int = 0,
):
    pdf = pdfium.PdfDocument(pdf_path)

    page = pdf[page_index]

    width, height = page.get_size()
    media = page.get_mediabox()
    crop = page.get_cropbox()

    print(f"Page {page_index + 1}")
    print()

    print("SIZE")
    print(f"  width  : {width}")
    print(f"  height : {height}")
    print()

    print("MEDIA BOX")
    print(f"  {media}")
    print()

    print("CROP BOX")
    print(f"  {crop}")
    print()

    media_width = media[2] - media[0]
    media_height = media[3] - media[1]

    crop_width = crop[2] - crop[0]
    crop_height = crop[3] - crop[1]

    print("MEDIA SIZE")
    print(f"  width  : {media_width}")
    print(f"  height : {media_height}")
    print()

    print("CROP SIZE")
    print(f"  width  : {crop_width}")
    print(f"  height : {crop_height}")
```

---

# 22. Liên hệ trực tiếp với project PDF của chúng ta

Sau này khi xây:

```text
PDF Thumbnail Generator
```

chúng ta có thể có option:

```text
--box media
--box crop
```

Ví dụ:

```bash
pdf-thumbnail book.pdf --box crop
```

hoặc:

```bash
pdf-thumbnail book.pdf --box media
```

Kiến trúc:

```text
CLI
 │
 ▼
ThumbnailService
 │
 ▼
PageBoundarySelector
 │
 ├── MEDIA_BOX
 └── CROP_BOX
       │
       ▼
   PdfRenderer
       │
       ▼
    Bitmap
       │
       ▼
      PIL
```

Đây là cách tốt hơn việc nhét:

```python
if crop:
    ...
```

vào renderer.

---

# 23. Điểm cần nhớ của Buổi 25

### ① MediaBox

```text
Toàn bộ page physical boundary
```

### ② CropBox

```text
Vùng page được clip khi display/print
```

### ③ CropBox mặc định

Nếu PDF không khai báo CropBox riêng:

```text
CropBox = MediaBox
```

### ④ pypdfium2

```python
page.get_mediabox()
page.get_cropbox()
page.get_bbox()
```

### ⑤ Render crop

```python
page.render(crop=...)
```

khác với CropBox của PDF.

### ⑥ Coordinate system

Đây là điểm cực kỳ quan trọng:

```text
PDF
bottom-left origin
```

vs

```text
image/render
top-left oriented coordinates
```

Không nên tùy tiện truyền box từ hệ này sang hệ kia.

---

## Roadmap tiếp theo

Chúng ta đã hoàn thành:

```text
21 Render chất lượng cao
22 Grayscale
23 Transparency
24 Rotation
25 CropBox / MediaBox  ← hiện tại
```

**Buổi 26 — Page size**

sẽ đi sâu vào:

```text
A4 / A5 / Letter / Legal
      ↓
PDF points
      ↓
inch
      ↓
mm
      ↓
DPI
      ↓
pixel
```

và đặc biệt xây một `PageSize` domain model để renderer của project có thể phân biệt **kích thước vật lý của PDF** với **kích thước bitmap sau rendering**.

[1]: https://github.com/docling-project/docling/blob/main/docling/backend/pypdfium2_backend.py?utm_source=chatgpt.com "docling/docling/backend/pypdfium2_backend.py at main · docling-project/docling · GitHub"
[2]: https://github.com/Hopding/pdf-lib/blob/master/src/api/PDFPage.ts?utm_source=chatgpt.com "pdf-lib/src/api/PDFPage.ts at master · Hopding/pdf-lib · GitHub"
[3]: https://github.com/pypdfium2-team/pypdfium2/blob/main/README.md?utm_source=chatgpt.com "pypdfium2/README.md at main · pypdfium2-team/pypdfium2 · GitHub"
