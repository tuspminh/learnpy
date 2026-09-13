# Buổi 26 — Page Size

Hôm nay chúng ta đi sâu vào **kích thước vật lý của PDF page** và mối quan hệ:

```text
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

Đây là bài rất quan trọng vì từ Buổi 21–25 chúng ta đã có:

```text
DPI
Grayscale
Transparency
Rotation
MediaBox / CropBox
```

Bây giờ chúng ta sẽ ghép chúng lại thành một mô hình `PageSize` đúng nghĩa.

---

# 1. PDF dùng đơn vị gì?

PDF không lưu kích thước trang bằng pixel.

Đơn vị cơ bản là **point (pt)**.

Quy ước:

```text
72 pt = 1 inch
```

Do đó:

```text
1 pt = 1 / 72 inch
```

Ví dụ A4:

```text
A4 = 210 × 297 mm
```

xấp xỉ:

```text
8.2677 × 11.6929 inch
```

Đổi sang point:

```text
8.2677 × 72 ≈ 595.28 pt
11.6929 × 72 ≈ 841.89 pt
```

Vì vậy một page A4 thường có kích thước khoảng:

```text
595.28 × 841.89 pt
```

---

# 2. PDF point ≠ pixel

Đây là nguyên tắc cần nhớ:

```text
PDF
    ↓
vector coordinate
    ↓
point
```

Còn:

```text
Bitmap
    ↓
pixel
```

PDF không nói:

```text
A4 = 2480 × 3508 pixels
```

Mà PDF nói:

```text
A4 ≈ 595 × 842 pt
```

Sau đó renderer quyết định:

```text
DPI = ?
```

để biến nó thành pixel.

---

# 3. Công thức point → inch

Rất đơn giản:

```text
inch = point / 72
```

Ví dụ:

```text
595.28 / 72
≈ 8.2678 inch
```

và:

```text
841.89 / 72
≈ 11.693 inch
```

---

# 4. Inch → point

Ngược lại:

```text
point = inch × 72
```

Ví dụ:

```text
8.5 inch × 72
= 612 pt
```

Đây chính là:

```text
Letter width = 612 pt
```

---

# 5. Point → mm

Ta biết:

```text
1 inch = 25.4 mm
1 inch = 72 pt
```

Do đó:

```text
1 pt = 25.4 / 72 mm
```

≈

```text
0.352777... mm
```

Công thức:

```text
mm = pt × 25.4 / 72
```

Ví dụ:

```text
595.28 × 25.4 / 72
≈ 210 mm
```

---

# 6. mm → point

Ngược lại:

```text
pt = mm × 72 / 25.4
```

Ví dụ:

```text
210 × 72 / 25.4
≈ 595.28 pt
```

---

# 7. Page size chuẩn

Một số kích thước thường gặp:

| Khổ    |            mm |   point gần đúng |
| ------ | ------------: | ---------------: |
| A4     |     210 × 297 |  595.28 × 841.89 |
| A5     |     148 × 210 |  419.53 × 595.28 |
| Letter | 215.9 × 279.4 |        612 × 792 |
| Legal  | 215.9 × 355.6 |       612 × 1008 |
| A3     |     297 × 420 | 841.89 × 1190.55 |

Nhưng cần nhớ:

> PDF page không nhất thiết phải là A4, A5, Letter...

Nó có thể có kích thước tùy ý.

Ví dụ:

```text
300 × 500 pt
```

hoàn toàn hợp lệ.

---

# 8. Page size và MediaBox

Ở Buổi 25 chúng ta có:

```text
MediaBox
(0, 0, 595.28, 841.89)
```

thì kích thước là:

```text
width  = 595.28 pt
height = 841.89 pt
```

Tức:

```text
A4
```

Nhưng nếu:

```text
MediaBox
(10, 20, 605.28, 861.89)
```

thì:

```text
width  = 605.28 - 10
       = 595.28

height = 861.89 - 20
       = 841.89
```

Cho nên:

> **Page size là kích thước của box, không nhất thiết là tọa độ `right/top` tuyệt đối.**

Đây là lý do domain `PageBox` của chúng ta đã có:

```python
@property
def width(self):
    return self.right - self.left
```

---

# 9. Xây `PageSize`

Bây giờ ta tạo domain model riêng.

Cấu trúc:

```text
PageBox
    ↓
PageSize
    ├── width
    └── height
```

Tạo:

```text
domain/page_size.py
```

Code:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PageSize:
    width_pt: float
    height_pt: float

    def __post_init__(self):
        if self.width_pt <= 0:
            raise ValueError(
                "width_pt phải > 0"
            )

        if self.height_pt <= 0:
            raise ValueError(
                "height_pt phải > 0"
            )

    @property
    def width_in(self) -> float:
        return self.width_pt / 72.0

    @property
    def height_in(self) -> float:
        return self.height_pt / 72.0

    @property
    def width_mm(self) -> float:
        return self.width_in * 25.4

    @property
    def height_mm(self) -> float:
        return self.height_in * 25.4
```

---

# 10. Test PageSize

```python
from domain.page_size import PageSize


def test_a4_size():
    size = PageSize(
        width_pt=595.2756,
        height_pt=841.8898,
    )

    assert abs(size.width_mm - 210) < 0.01
    assert abs(size.height_mm - 297) < 0.01


def test_letter_size():
    size = PageSize(
        width_pt=612,
        height_pt=792,
    )

    assert abs(size.width_in - 8.5) < 0.0001
    assert abs(size.height_in - 11) < 0.0001


def test_invalid_width():
    import pytest

    with pytest.raises(ValueError):
        PageSize(
            width_pt=0,
            height_pt=100,
        )
```

Chạy:

```bash
pytest
```

---

# 11. Từ PageBox tạo PageSize

Ta có thể thêm:

```python
@property
def size(self) -> PageSize:
    return PageSize(
        width_pt=self.width,
        height_pt=self.height,
    )
```

Nhưng tôi khuyên **không import chéo tùy tiện** nếu project bắt đầu lớn.

Có thể tạo factory:

```python
from domain.page_size import PageSize
from domain.page_box import PageBox


def page_size_from_box(box: PageBox) -> PageSize:
    return PageSize(
        width_pt=box.width,
        height_pt=box.height,
    )
```

---

# 12. Từ pypdfium2 → PageSize

Infrastructure:

```python
class PdfiumPageSizeReader:

    def read(self, page):
        width, height = page.get_size()

        return PageSize(
            width_pt=width,
            height_pt=height,
        )
```

Bây giờ Application không biết:

```python
page.get_size()
```

là API của pypdfium2.

Nó chỉ nhận:

```python
PageSize
```

Đúng tinh thần:

```text
Infrastructure
      ↓
Domain
      ↓
Application
```

---

# 13. Page size → pixel

Đây là phần cực kỳ quan trọng đối với rendering.

Ta đã học:

```text
scale = DPI / 72
```

Vì vậy:

```text
pixel_width
    = point_width × DPI / 72
```

hay:

```text
pixel_width
    = inch_width × DPI
```

Tương tự:

```text
pixel_height
    = point_height × DPI / 72
```

---

# 14. Ví dụ A4 ở 300 DPI

A4:

```text
595.28 × 841.89 pt
```

300 DPI:

```text
width
= 595.28 × 300 / 72
≈ 2480
```

```text
height
= 841.89 × 300 / 72
≈ 3508
```

Do đó:

```text
A4 @ 300 DPI

≈ 2480 × 3508 px
```

Đây chính là kích thước ảnh scan/render A4 rất quen thuộc.

---

# 15. Thêm phương thức tính pixel

Ta có thể mở rộng:

```python
@dataclass(frozen=True)
class PixelSize:
    width: int
    height: int
```

File:

```text
domain/pixel_size.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PixelSize:

    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError("width phải > 0")

        if self.height <= 0:
            raise ValueError("height phải > 0")
```

Sau đó:

```python
from domain.pixel_size import PixelSize


class PageSize:

    # ...

    def to_pixels(self, dpi: float) -> PixelSize:
        if dpi <= 0:
            raise ValueError("DPI phải > 0")

        width = round(
            self.width_pt * dpi / 72.0
        )

        height = round(
            self.height_pt * dpi / 72.0
        )

        return PixelSize(
            width=width,
            height=height,
        )
```

---

# 16. Test

```python
def test_a4_300_dpi():
    size = PageSize(
        width_pt=595.2756,
        height_pt=841.8898,
    )

    pixels = size.to_pixels(300)

    assert pixels.width == 2480
    assert pixels.height == 3508
```

Ta có:

```text
PageSize
595.28 × 841.89 pt
       ↓
300 DPI
       ↓
PixelSize
2480 × 3508 px
```

---

# 17. DPI càng cao thì ảnh càng lớn

Ví dụ A4:

| DPI | Pixel gần đúng |
| --: | -------------: |
|  72 |      595 × 842 |
|  96 |     794 × 1123 |
| 150 |    1240 × 1754 |
| 200 |    1654 × 2339 |
| 300 |    2480 × 3508 |
| 600 |    4961 × 7016 |

Để ý:

```text
DPI × 2
```

thì:

```text
width × 2
height × 2
```

Nhưng số pixel:

```text
× 4
```

Do đó memory cũng tăng rất nhanh.

---

# 18. Page size và memory

Ví dụ A4 @ 300 DPI:

```text
2480 × 3508
```

RGB:

```text
2480 × 3508 × 3
≈ 26 MB
```

RGBA:

```text
2480 × 3508 × 4
≈ 35 MB
```

Nếu PDF có:

```text
100 pages
```

và bạn giữ toàn bộ ảnh:

```text
26 MB × 100
≈ 2.6 GB
```

Đây chính là lý do Buổi 29:

```text
Tối ưu memory khi render PDF lớn
```

sẽ rất quan trọng.

---

# 19. Rotation ảnh hưởng PageSize

Ở Buổi 24 chúng ta học:

```text
rotation = 90°
```

thì:

```text
width ↔ height
```

Ví dụ A4:

```text
Portrait:

595 × 842
```

sau rotation 90°:

```text
842 × 595
```

Có thể tạo:

```python
def rotated(self, rotation: int) -> "PageSize":
    if rotation not in {0, 90, 180, 270}:
        raise ValueError("rotation không hợp lệ")

    if rotation in {90, 270}:
        return PageSize(
            width_pt=self.height_pt,
            height_pt=self.width_pt,
        )

    return self
```

---

# 20. Test rotation

```python
def test_rotation_90():
    size = PageSize(
        width_pt=595.2756,
        height_pt=841.8898,
    )

    rotated = size.rotated(90)

    assert rotated.width_pt == size.height_pt
    assert rotated.height_pt == size.width_pt
```

---

# 21. Nhưng có một vấn đề tinh tế

Đừng hiểu:

```text
page.get_size()
```

là:

```text
"khổ giấy vật lý tuyệt đối"
```

trong mọi trường hợp.

PDF có:

```text
MediaBox
CropBox
BleedBox
TrimBox
ArtBox
```

và page rotation cũng có thể ảnh hưởng cách page được trình bày.

Vì vậy trong architecture tốt, chúng ta nên phân biệt:

```text
PageGeometry
    │
    ├── MediaBox
    ├── CropBox
    ├── ...
    └── Rotation
```

và:

```text
PageSize
    │
    ├── width
    └── height
```

Nói cách khác:

```text
PageBox = vị trí + boundary

PageSize = kích thước

Rotation = orientation
```

Không nên gom tất cả vào một class khổng lồ.

---

# 22. Architecture hiện tại

Sau Buổi 26:

```text
                 PDF Page
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     PageGeometry          Rotation
          │
     ┌────┴────┐
     │         │
     ▼         ▼
 MediaBox   CropBox
     │         │
     └────┬────┘
          ▼
       PageBox
          │
          ▼
       PageSize
       ┌──┴───┐
       │      │
       ▼      ▼
      mm     inch
       │
       ▼
      DPI
       │
       ▼
   PixelSize
```

Đây là architecture rất hữu ích cho PDF application của chúng ta.

---

# 23. Hoàn chỉnh `PageSize`

Tôi đề xuất phiên bản hiện tại như sau:

```python
from dataclasses import dataclass

from domain.pixel_size import PixelSize


@dataclass(frozen=True)
class PageSize:

    width_pt: float
    height_pt: float

    def __post_init__(self):
        if self.width_pt <= 0:
            raise ValueError(
                "width_pt phải > 0"
            )

        if self.height_pt <= 0:
            raise ValueError(
                "height_pt phải > 0"
            )

    @property
    def width_in(self) -> float:
        return self.width_pt / 72.0

    @property
    def height_in(self) -> float:
        return self.height_pt / 72.0

    @property
    def width_mm(self) -> float:
        return self.width_in * 25.4

    @property
    def height_mm(self) -> float:
        return self.height_in * 25.4

    def to_pixels(self, dpi: float) -> PixelSize:
        if dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        return PixelSize(
            width=round(
                self.width_pt * dpi / 72.0
            ),
            height=round(
                self.height_pt * dpi / 72.0
            ),
        )

    def rotated(self, rotation: int) -> "PageSize":
        if rotation not in {0, 90, 180, 270}:
            raise ValueError(
                "rotation phải là 0, 90, 180 hoặc 270"
            )

        if rotation in {90, 270}:
            return PageSize(
                width_pt=self.height_pt,
                height_pt=self.width_pt,
            )

        return self
```

---

# 24. Một nguyên tắc architecture rất quan trọng

Ta không muốn:

```python
class PdfRenderer:
    def render(self):
        # tính mm
        # tính inch
        # tính pixel
        # xử lý crop
        # xử lý rotation
        # grayscale
        # transparency
        # ...
```

Class như vậy sẽ nhanh chóng trở thành **God Object**.

Thay vào đó:

```text
PageGeometry
       ↓
PageSize
       ↓
RenderOptions
       ↓
PdfRenderer
       ↓
PdfBitmap
       ↓
ImageProcessor
```

Mỗi thành phần có một trách nhiệm.

---

# 25. Bài tập thực hành

Viết function:

```python
def inspect_page_size(pdf_path, page_index=0):
    ...
```

Output mong muốn:

```text
Page: 1

PDF Size
--------
Width : 595.28 pt
Height: 841.89 pt

Physical Size
-------------
Width : 210.00 mm
Height: 297.00 mm

At 72 DPI
---------
595 × 842 px

At 150 DPI
----------
1240 × 1754 px

At 300 DPI
----------
2480 × 3508 px
```

Sau đó thử với:

```text
72
96
150
200
300
600
```

để quan sát tốc độ tăng pixel.

---

# 26. Quan hệ giữa 4 đại lượng

Đây là phần **phải thuộc**:

```text
              72 pt
               │
               ▼
            1 inch
               │
               ▼
            25.4 mm
```

Công thức:

```text
inch = pt / 72

pt = inch × 72

mm = pt × 25.4 / 72

pt = mm × 72 / 25.4
```

Rendering:

```text
pixel = pt × DPI / 72
```

hoặc:

```text
pixel = inch × DPI
```

---

# 27. Liên hệ với toàn bộ Part III

Chúng ta hiện đã có:

```text
21  Quality
       ↓
22  Grayscale
       ↓
23  Transparency
       ↓
24  Rotation
       ↓
25  CropBox / MediaBox
       ↓
26  Page Size        ← hiện tại
       ↓
27  Coordinate System
       ↓
28  Render Region
       ↓
29  Memory Optimization
       ↓
30  Thumbnail Generator
```

**Buổi 27 — Coordinate System** sẽ là bài rất quan trọng tiếp theo.

Chúng ta sẽ chính thức xây:

```text
PDF Coordinate System
        ↓
bottom-left origin
        ↓
x / y
        ↓
top-left image coordinate
        ↓
rotation
        ↓
scale
        ↓
PDF point → pixel
        ↓
BoundingBox transformation
```

Và đặc biệt sẽ nối trực tiếp với những gì chúng ta đã học ở **Text position / bounding box** trong Part II.
