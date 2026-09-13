# Phần III — PDF Rendering chuyên sâu

# Buổi 24 — Rotation

Ở Buổi 23, chúng ta đã hiểu:

```text
PDF
 ↓
PDFium
 ↓
Bitmap
 ↓
PIL
 ↓
RGB / RGBA / Grayscale
```

Hôm nay chúng ta thêm:

```text
rotation
```

Đây là một chủ đề **rất quan trọng**, vì rotation không chỉ làm ảnh xoay.

Nó ảnh hưởng đến:

* `width / height`
* hướng hiển thị page
* coordinate system
* crop
* render region
* mapping PDF point → pixel
* thumbnail

Đặc biệt, **rotation 90° và 270° làm width/height đổi chỗ**.

---

# 1. Rotation trong PDF là gì?

Một PDF page có thể có rotation:

```text
0°
90°
180°
270°
```

Ví dụ page gốc:

```text
┌──────────────────────┐
│                      │
│                      │
│       PDF PAGE       │
│                      │
│                      │
└──────────────────────┘
```

Kích thước:

```text
612 × 792
```

Sau rotation 90°:

```text
┌─────────────────────────────┐
│                             │
│          PDF PAGE           │
│                             │
└─────────────────────────────┘
```

Kích thước hiển thị trở thành gần:

```text
792 × 612
```

---

# 2. Có hai loại rotation cần phân biệt

Đây là điểm rất quan trọng.

## Loại 1 — Page rotation

PDF bản thân nó có thông tin rotation.

Ví dụ:

```text
Page
rotation = 90°
```

## Loại 2 — Render rotation

Khi render, chúng ta yêu cầu:

```python
page.render(
    rotation=1,
)
```

hoặc giá trị tương ứng theo API của pypdfium2.

Hai khái niệm này không nên nhập làm một.

---

# 3. PDF page có thể có rotation metadata

PDF có thể nói:

```text
Page 1
MediaBox = ...
CropBox = ...
Rotate = 90
```

Điều đó có nghĩa nội dung page có một orientation được áp dụng khi hiển thị.

Khi xây dựng renderer, cần xác định rõ:

```text
PDF page rotation
```

và:

```text
requested render rotation
```

đang được xử lý như thế nào.

---

# 4. Render rotation với pypdfium2

Ở mức API, pypdfium2 hỗ trợ tham số:

```python
page.render(
    scale=2,
    rotation=...
)
```

Ta không nên coi `rotation` là số độ trực tiếp.

Trong PDFium, rotation thường được biểu diễn bằng enum:

```text
0
90°
180°
270°
```

và trong pypdfium2 nên dùng enum/API tương ứng thay vì tự suy đoán số nguyên.

Một cách an toàn là import rotation enum từ pypdfium2:

```python
import pypdfium2 as pdfium
```

rồi kiểm tra API/version đang dùng trước khi hard-code giá trị.

---

# 5. Ý tưởng abstraction

Không nên để application viết:

```python
page.render(
    scale=4,
    rotation=1,
)
```

Ta đưa rotation vào:

```python
RenderOptions
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0
    grayscale: bool = False
    transparent: bool = False
    rotation: int = 0

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        if self.rotation not in {
            0,
            90,
            180,
            270,
        }:
            raise ValueError(
                "Rotation phải là 0, 90, 180 hoặc 270"
            )

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Ở **domain**, ta có thể biểu diễn rotation bằng độ vì đó là khái niệm dễ hiểu:

```text
0°
90°
180°
270°
```

Còn infrastructure chịu trách nhiệm chuyển sang representation mà PDFium yêu cầu.

---

# 6. Tại sao không lưu rotation dưới dạng `1, 2, 3`?

Không nên:

```python
rotation = 1
```

ở domain.

Bởi vì:

```text
1 có nghĩa gì?
```

Người đọc code phải biết:

```text
1 = 90°
2 = 180°
3 = 270°
```

Tốt hơn:

```python
rotation = 90
```

hoặc tốt hơn nữa:

```python
from enum import IntEnum


class Rotation(IntEnum):
    DEG_0 = 0
    DEG_90 = 90
    DEG_180 = 180
    DEG_270 = 270
```

---

# 7. Tạo `Rotation`

```python
from enum import IntEnum


class Rotation(IntEnum):

    DEG_0 = 0
    DEG_90 = 90
    DEG_180 = 180
    DEG_270 = 270
```

Sử dụng:

```python
options = RenderOptions(
    dpi=300,
    rotation=Rotation.DEG_90,
)
```

Nhưng `IntEnum` vẫn có giá trị số.

Nếu muốn domain thuần túy hơn:

```python
from enum import Enum


class Rotation(Enum):

    DEG_0 = 0
    DEG_90 = 90
    DEG_180 = 180
    DEG_270 = 270
```

Tôi khuyến nghị cách này cho domain.

---

# 8. Validation rotation

Không cho phép:

```python
rotation=45
```

vì PDF page rotation chuẩn thường chỉ cần:

```text
0
90
180
270
```

Test:

```python
import pytest


def test_valid_rotation():

    RenderOptions(
        dpi=300,
        rotation=90,
    )


def test_invalid_rotation():

    with pytest.raises(ValueError):

        RenderOptions(
            dpi=300,
            rotation=45,
        )
```

---

# 9. Render page với rotation

Infrastructure:

```python
class PdfRenderer:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self._pdf = None

    def open(self):
        self._pdf = pdfium.PdfDocument(
            self.pdf_path
        )

    def close(self):
        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    def render_page(
        self,
        page_index,
        options,
    ):

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        page = self._pdf[page_index]

        bitmap = page.render(
            scale=options.scale,
            rotation=options.rotation,
        )

        return bitmap
```

Đây là nơi application-level option được chuyển xuống PDFium.

---

# 10. Nhưng rotation 90° ảnh hưởng width/height

Giả sử:

```text
PDF page:
612 × 792
```

Render:

```text
rotation = 0°
```

thì bitmap gần:

```text
612 × 792
```

nếu scale = 1.

Rotation 90°:

```text
792 × 612
```

Rotation 180°:

```text
612 × 792
```

Rotation 270°:

```text
792 × 612
```

Ta có:

```text
0°     → W × H
90°    → H × W
180°   → W × H
270°   → H × W
```

---

# 11. Hàm tính kích thước sau rotation

Ta có thể viết domain utility:

```python
def rotated_size(
    width: float,
    height: float,
    rotation: int,
) -> tuple[float, float]:

    if rotation in (0, 180):
        return width, height

    if rotation in (90, 270):
        return height, width

    raise ValueError(
        "Rotation không hợp lệ"
    )
```

Test:

```python
assert rotated_size(
    612,
    792,
    0,
) == (612, 792)
```

```python
assert rotated_size(
    612,
    792,
    90,
) == (792, 612)
```

```python
assert rotated_size(
    612,
    792,
    180,
) == (612, 792)
```

```python
assert rotated_size(
    612,
    792,
    270,
) == (792, 612)
```

---

# 12. Rotation và DPI

Giả sử:

```text
page = 612 × 792 PDF points
DPI = 300
```

Scale:

```python
scale = 300 / 72
```

Kích thước chưa rotation:

```python
width_px = 612 * scale
height_px = 792 * scale
```

xấp xỉ:

```text
2550 × 3300
```

Sau 90°:

```text
3300 × 2550
```

Điều quan trọng:

> **Rotation không làm tăng số pixel về mặt lý thuyết; nó chỉ đổi orientation của bounding dimensions.**

---

# 13. Rotation 90° không giống crop

Ví dụ:

```text
Original:

612 × 792
```

rotation:

```text
792 × 612
```

Nhưng crop:

```text
612 × 792
       ↓
300 × 400
```

là:

```text
giảm vùng nhìn thấy
```

Hai khái niệm hoàn toàn khác:

```text
rotation
    ↓
thay đổi orientation

crop
    ↓
thay đổi vùng render
```

Sau này Buổi 28 chúng ta sẽ kết hợp cả hai.

---

# 14. Rotation và coordinate system

Đây là lý do Buổi 24 quan trọng.

Giả sử:

```text
PDF coordinate:

(0,H)
  ┌──────────────────────┐
  │                      │
  │                      │
  │                      │
  └──────────────────────┘
(0,0)
```

Một điểm:

```text
(x, y)
```

sau rotation 90° không thể đơn giản:

```python
x, y = y, x
```

Đây là sai trong nhiều trường hợp vì phải tính cả:

```text
width
height
origin
rotation direction
```

Ví dụ với rotation quanh origin, phép biến đổi hình học có thể là:

### 90°

```text
x' = y
y' = W - x
```

hoặc một biến thể tương ứng tùy convention/origin.

Đây chính là lý do chúng ta **không nên tự viết coordinate transformation tùy tiện** trước khi học kỹ Buổi 27.

---

# 15. Rotation và PIL

Có hai cách tiếp cận.

### Cách A

Render trực tiếp bằng PDFium:

```text
PDF
 ↓
PDFium rotation
 ↓
Bitmap
```

### Cách B

Render bình thường rồi xoay PIL:

```text
PDF
 ↓
PDFium
 ↓
Bitmap
 ↓
PIL
 ↓
rotate()
```

Ví dụ:

```python
image.rotate(
    90,
    expand=True,
)
```

---

# 16. Khi nào nên xoay bằng PDFium?

Nếu mục tiêu là:

```text
PDF rendering
```

thì ưu tiên:

```text
PDF
 ↓
PDFium
 ↓
rotated bitmap
```

vì renderer hiểu:

* page geometry
* PDF coordinate system
* page transformation
* PDF objects

thay vì ta lấy bitmap rồi tự xoay.

---

# 17. Khi nào PIL rotation hữu ích?

PIL rotation hữu ích khi:

```text
đã có image
```

và cần post-processing:

```text
Image
 ↓
rotate
 ↓
resize
 ↓
filter
 ↓
save
```

Ví dụ thumbnail pipeline có thể cần:

```text
render
 ↓
resize
 ↓
rotate
```

nhưng phải xác định rõ rotation nào thuộc PDF semantics và rotation nào là image processing.

---

# 18. Không được nhầm `page rotation` và `image rotation`

Ví dụ:

```text
PDF page
Rotate = 90°
```

Nếu PDFium đã áp dụng rotation khi render:

```text
PDFium
 ↓
90°
 ↓
Bitmap
```

thì **không nên tiếp tục**:

```python
image.rotate(90)
```

nếu mục tiêu chỉ là hiển thị đúng orientation.

Nếu làm vậy:

```text
PDF rotation 90°
+
PIL rotation 90°
=
180°
```

Đây là một bug rất dễ gặp.

---

# 19. Thiết kế `RenderOptions` hiện tại

Sau Buổi 24:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0

    grayscale: bool = False

    transparent: bool = False

    rotation: int = 0

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        if self.rotation not in {
            0,
            90,
            180,
            270,
        }:
            raise ValueError(
                "Rotation phải là 0, 90, 180 hoặc 270"
            )

    @property
    def scale(self) -> float:

        return self.dpi / 72.0
```

---

# 20. Hoàn chỉnh `PdfRenderer`

```python
from pathlib import Path

import pypdfium2 as pdfium


class PdfRenderer:

    def __init__(
        self,
        pdf_path: str | Path,
    ):
        self.pdf_path = Path(pdf_path)
        self._pdf = None

    def open(self):

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                self.pdf_path
            )

        if not self.pdf_path.is_file():
            raise ValueError(
                f"Không phải file: {self.pdf_path}"
            )

        self._pdf = pdfium.PdfDocument(
            self.pdf_path
        )

    def close(self):

        if self._pdf is not None:

            self._pdf.close()
            self._pdf = None

    @property
    def page_count(self) -> int:

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        return len(self._pdf)

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        if not 0 <= page_index < self.page_count:
            raise IndexError(
                "Page index không hợp lệ"
            )

        page = self._pdf[page_index]

        return page.render(
            scale=options.scale,
            rotation=options.rotation,
        )

    def __enter__(self):

        self.open()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        self.close()
```

---

# 21. Chương trình test thực tế

Giả sử:

```text
sample.pdf
```

ta thử:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument(
    "sample.pdf"
)

try:

    page = pdf[0]

    for rotation in (
        0,
        90,
        180,
        270,
    ):

        bitmap = page.render(
            scale=2,
            rotation=rotation,
        )

        image = bitmap.to_pil()

        print(
            f"rotation={rotation}:",
            image.size,
        )

        image.save(
            f"page-{rotation}.png"
        )

finally:

    pdf.close()
```

Bạn sẽ thấy sự khác nhau về orientation.

**Lưu ý:** cách pypdfium2 diễn giải tham số `rotation` có thể phụ thuộc version/API wrapper; khi chạy project thực tế, nên kiểm tra version đang cài và enum rotation tương ứng thay vì giả định raw integer mapping.

---

# 22. Test logic rotation

```python
import pytest


@pytest.mark.parametrize(
    "rotation,expected",
    [
        (0, (612, 792)),
        (90, (792, 612)),
        (180, (612, 792)),
        (270, (792, 612)),
    ],
)
def test_rotated_size(
    rotation,
    expected,
):

    assert rotated_size(
        612,
        792,
        rotation,
    ) == expected
```

---

# 23. Bài tập thực hành

## Bài 1 — Render 4 hướng

Render trang đầu tiên:

```text
0°
90°
180°
270°
```

ở:

```text
150 DPI
```

lưu:

```text
page-0.png
page-90.png
page-180.png
page-270.png
```

Sau đó kiểm tra:

```python
image.size
```

---

## Bài 2 — So sánh page size

Viết:

```python
def get_render_size(
    page_width,
    page_height,
    dpi,
    rotation,
):
    ...
```

Ví dụ:

```python
get_render_size(
    612,
    792,
    300,
    90,
)
```

kết quả gần:

```text
3300 × 2550
```

---

# 24. Bài tập kiến trúc

Cập nhật:

```python
RenderOptions
```

để hỗ trợ:

```text
dpi
grayscale
transparent
rotation
```

sau đó giữ cho:

```text
PdfRenderer
```

chỉ chịu trách nhiệm:

```text
PDF → Bitmap
```

Còn:

```text
ImageProcessor
```

chịu trách nhiệm:

```text
Bitmap/PIL → processed image
```

Không viết:

```python
class PdfRenderer:

    def render():
        ...
        grayscale()
        ...
        rotate()
        ...
        save()
```

---

# 25. Kiến trúc sau Buổi 24

Chúng ta hiện có:

```text
                    Application
                         │
                         ▼
                  PdfRenderService
                         │
                         ▼
                  RenderOptions
                         │
          ┌──────────────┼──────────────┐
          │              │              │
         DPI        Grayscale     Transparency
                         │
                     Rotation
                         │
                         ▼
                    PdfRenderer
                         │
                         ▼
                       PDFium
                         │
                         ▼
                      PdfPage
                         │
                         ▼
                     PdfBitmap
                         │
                         ▼
                     PIL.Image
                         │
                         ▼
                  Image Processing
```

Và toàn bộ Phần III hiện tại:

```text
21 — Render chất lượng cao       ✓
22 — Grayscale                   ✓
23 — Transparency                ✓
24 — Rotation                    ✓
25 — CropBox / MediaBox          ← tiếp theo
26 — Page Size
27 — Coordinate System
28 — Render Region
29 — Memory Optimization
30 — Thumbnail Generator
```

## 3 điều cần nhớ sau Buổi 24

**1.**

```text
0° / 180°
→ W × H
```

**2.**

```text
90° / 270°
→ H × W
```

**3.**

Quan trọng nhất:

> **Đừng trộn page rotation của PDF với rotation của PIL.**

Nếu PDFium đã áp dụng rotation của page khi render, xoay ảnh thêm một lần rất dễ tạo ra orientation sai.

Buổi **25 — CropBox / MediaBox** sẽ đi sâu vào một vấn đề còn quan trọng hơn: **tại sao `page.get_size()` không phải lúc nào cũng đủ để biết vùng PDF thực sự được hiển thị**, và cách MediaBox/CropBox ảnh hưởng đến rendering.
