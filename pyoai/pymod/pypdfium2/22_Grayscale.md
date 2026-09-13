# Phần III — PDF Rendering chuyên sâu

# Buổi 22 — Grayscale

Ở Buổi 21, chúng ta đã xây dựng nền tảng:

```text
RenderOptions
    ↓
PdfRenderer
    ↓
PdfPage
    ↓
PdfBitmap
    ↓
PIL.Image
```

Hôm nay thêm khả năng:

```text
Color PDF
   │
   ├── RGB
   ├── RGBA
   └── Grayscale
```

Mục tiêu không chỉ là **đổi ảnh màu thành đen trắng**, mà là hiểu **grayscale nằm ở đâu trong rendering pipeline**, khi nào nên để PDFium render grayscale và khi nào nên chuyển đổi bằng PIL.

---

# 1. Grayscale là gì?

Ảnh màu thông thường:

```text
RGB
 ├── Red
 ├── Green
 └── Blue
```

Mỗi pixel có thể được biểu diễn:

```text
R = 120
G = 80
B = 200
```

Grayscale chỉ cần một giá trị:

```text
0   → đen
255 → trắng
```

Ví dụ:

```text
RGB(255, 0, 0)
        ↓
Gray ≈ 76
```

Một ảnh grayscale có dạng:

```text
Pixel
 │
 └── intensity
       │
       ├── 0
       ├── ...
       └── 255
```

---

# 2. Hai cách tạo grayscale

Có hai chiến lược quan trọng.

## Cách 1 — Render trực tiếp grayscale

```text
PDF
 ↓
PDFium
 ↓
Grayscale Bitmap
```

## Cách 2 — Render màu rồi convert

```text
PDF
 ↓
PDFium
 ↓
RGB Bitmap
 ↓
PIL.Image
 ↓
convert("L")
 ↓
Grayscale
```

Hai cách này **không hoàn toàn giống nhau về pipeline và memory**.

---

# 3. Cách đơn giản với PIL

Ta đã biết:

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()
```

Sau đó:

```python
gray = image.convert("L")
```

Ví dụ hoàn chỉnh:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(
        scale=2,
    )

    image = bitmap.to_pil()

    gray = image.convert("L")

    gray.save("page-gray.png")

finally:
    pdf.close()
```

`"L"` trong PIL biểu diễn ảnh grayscale 8-bit.

---

# 4. Kiểm tra mode

```python
print(image.mode)
print(gray.mode)
```

Ví dụ:

```text
RGB
L
```

Có nghĩa:

```text
RGB → 3 channel
L   → 1 channel
```

---

# 5. Memory

Đây là điểm rất quan trọng.

Giả sử:

```text
2550 × 3300
```

RGB:

```text
2550 × 3300 × 3
≈ 25.2 MB
```

Grayscale:

```text
2550 × 3300 × 1
≈ 8.0 MB
```

Tuy nhiên cần phân biệt:

```text
render RGB
    ↓
convert grayscale
```

không có nghĩa memory ngay lập tức chỉ còn 8 MB.

Trong quá trình conversion có thể tồn tại:

```text
RGB image
+
Gray image
```

đồng thời.

Vì vậy:

```python
gray = image.convert("L")
```

có thể tạm thời sử dụng thêm memory.

Đây sẽ là vấn đề chúng ta quay lại ở:

```text
Buổi 29 — Tối ưu memory
```

---

# 6. Đưa grayscale vào `RenderOptions`

Ở Buổi 21:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("DPI phải > 0")

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Bây giờ:

```python
@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0
    grayscale: bool = False

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("DPI phải > 0")

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Sử dụng:

```python
options = RenderOptions(
    dpi=300,
    grayscale=True,
)
```

---

# 7. Không nên để `PdfRenderer` xử lý PIL conversion?

Đây là một quyết định kiến trúc đáng chú ý.

Ta có:

```text
PdfRenderer
```

nhiệm vụ:

> Render PDF page thành bitmap.

Còn:

```text
ImageProcessor
```

nhiệm vụ:

> Xử lý bitmap/image.

Nếu viết:

```python
class PdfRenderer:

    def render_page(...):

        bitmap = page.render(...)

        image = bitmap.to_pil()

        if options.grayscale:
            image = image.convert("L")

        return image
```

thì `PdfRenderer` bắt đầu biết:

```text
pypdfium2
+
PIL
+
image processing
```

Điều này làm abstraction bị dính chặt.

Tốt hơn:

```text
PdfRenderer
    ↓
PdfBitmap
    ↓
ImageConverter
    ↓
ImageProcessor
```

---

# 8. Tách `ImageProcessor`

Ví dụ:

```python
from PIL import Image


class ImageProcessor:

    def grayscale(self, image: Image.Image) -> Image.Image:
        return image.convert("L")
```

Test rất dễ:

```python
from PIL import Image


processor = ImageProcessor()

image = Image.new(
    "RGB",
    (100, 100),
    (255, 0, 0),
)

gray = processor.grayscale(image)

print(gray.mode)
```

Kết quả:

```text
L
```

---

# 9. Tạo Render Service

Ta có thể tạo:

```python
class PdfRenderService:

    def __init__(self, renderer, image_processor):
        self.renderer = renderer
        self.image_processor = image_processor

    def render_page(
        self,
        page_index,
        options,
    ):
        bitmap = self.renderer.render_page(
            page_index,
            options,
        )

        image = bitmap.to_pil()

        if options.grayscale:
            image = self.image_processor.grayscale(image)

        return image
```

Pipeline:

```text
PdfRenderService
       │
       ├───────────────┐
       ↓               ↓
PdfRenderer      ImageProcessor
       │               │
       ↓               │
 PdfBitmap             │
       ↓               │
    PIL.Image ─────────┘
```

---

# 10. Ví dụ hoàn chỉnh

Cấu trúc đơn giản:

```text
pdf_renderer/
├── domain/
│   └── render.py
├── infrastructure/
│   └── pdfium_renderer.py
├── application/
│   └── service.py
└── main.py
```

### `domain/render.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0
    grayscale: bool = False

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

---

### `infrastructure/pdfium_renderer.py`

```python
from pathlib import Path

import pypdfium2 as pdfium

from domain.render import RenderOptions


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

        self._pdf = pdfium.PdfDocument(
            self.pdf_path
        )

    def close(self):

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    @property
    def page_count(self):

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

        bitmap = page.render(
            scale=options.scale,
        )

        return bitmap

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

### `application/service.py`

```python
from PIL import Image

from domain.render import RenderOptions


class ImageProcessor:

    def grayscale(
        self,
        image: Image.Image,
    ) -> Image.Image:

        return image.convert("L")


class PdfRenderService:

    def __init__(
        self,
        renderer,
        image_processor,
    ):
        self.renderer = renderer
        self.image_processor = image_processor

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):

        bitmap = self.renderer.render_page(
            page_index,
            options,
        )

        image = bitmap.to_pil()

        if options.grayscale:
            image = self.image_processor.grayscale(
                image
            )

        return image
```

---

### `main.py`

```python
from domain.render import RenderOptions
from infrastructure.pdfium_renderer import PdfRenderer
from application.service import (
    PdfRenderService,
    ImageProcessor,
)


def main():

    options = RenderOptions(
        dpi=300,
        grayscale=True,
    )

    renderer = PdfRenderer(
        "sample.pdf"
    )

    processor = ImageProcessor()

    service = PdfRenderService(
        renderer,
        processor,
    )

    with renderer:

        image = service.render_page(
            page_index=0,
            options=options,
        )

        print("Mode:", image.mode)
        print("Size:", image.size)

        image.save(
            "page-1-gray.png"
        )


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Mode: L
Size: (...)
```

---

# 11. Grayscale có nghĩa là đen trắng không?

**Không.**

Đây là lỗi khái niệm rất phổ biến.

Grayscale:

```text
đen
 ↓
xám đậm
 ↓
xám
 ↓
xám nhạt
 ↓
trắng
```

Trong khi binary black/white:

```text
đen
hoặc
trắng
```

Ví dụ:

```python
gray = image.convert("L")
```

là grayscale.

Nếu muốn binary:

```python
binary = gray.point(
    lambda p: 255 if p > 128 else 0
)
```

Nhưng **không nên đưa binary vào `RenderOptions.grayscale`**.

Đó là hai khái niệm khác nhau:

```text
grayscale
binary / thresholding
```

Binary/thresholding có thể là một bài xử lý ảnh riêng sau này.

---

# 12. Vì sao grayscale hữu ích với PDF?

Đặc biệt hữu ích khi xử lý:

### PDF scan

Ví dụ:

```text
sách scan
↓
PDF
↓
ảnh màu
↓
grayscale
```

Có thể giảm đáng kể dung lượng khi xuất ảnh phù hợp.

### OCR

Pipeline:

```text
PDF
 ↓
Render
 ↓
Grayscale
 ↓
OCR
```

Một số OCR pipeline không cần thông tin màu.

### Thumbnail

Nếu thumbnail chỉ dùng để xem nhanh:

```text
PDF
 ↓
150 DPI
 ↓
Grayscale
 ↓
thumbnail
```

có thể giảm chi phí xử lý.

---

# 13. Nhưng không phải lúc nào cũng nên grayscale

Ví dụ:

```text
PDF bản đồ
PDF biểu đồ
PDF tài liệu màu
PDF highlight màu
PDF magazine
```

Màu có thể chứa thông tin.

Do đó:

```python
grayscale=True
```

phải là **option**, không phải mặc định bắt buộc.

---

# 14. Test

Ta viết test cho `ImageProcessor`.

```python
from PIL import Image

from application.service import ImageProcessor


def test_grayscale():

    processor = ImageProcessor()

    image = Image.new(
        "RGB",
        (100, 100),
        (255, 0, 0),
    )

    result = processor.grayscale(
        image
    )

    assert result.mode == "L"
    assert result.size == (100, 100)
```

Test màu xám:

```python
def test_grayscale_pixel():

    processor = ImageProcessor()

    image = Image.new(
        "RGB",
        (1, 1),
        (255, 0, 0),
    )

    result = processor.grayscale(
        image
    )

    pixel = result.getpixel((0, 0))

    assert pixel == 76
```

PIL sử dụng phép chuyển đổi luminance chuẩn, nên đỏ thuần có giá trị grayscale khoảng `76`.

---

# 15. Test `RenderOptions`

```python
from domain.render import RenderOptions


def test_default_render_options():

    options = RenderOptions()

    assert options.dpi == 150
    assert options.grayscale is False


def test_grayscale_option():

    options = RenderOptions(
        dpi=300,
        grayscale=True,
    )

    assert options.dpi == 300
    assert options.grayscale is True


def test_scale():

    options = RenderOptions(
        dpi=300
    )

    assert options.scale == 300 / 72
```

---

# 16. Một vấn đề kiến trúc quan trọng

Hiện tại:

```python
options = RenderOptions(
    dpi=300,
    grayscale=True,
)
```

nhưng:

```text
grayscale
```

thực tế được xử lý **sau khi PDFium render**.

Vì vậy cần phân biệt:

```text
Render configuration
```

với:

```text
Post-processing configuration
```

Pipeline hiện tại:

```text
             RenderOptions
                  │
                  ├── dpi
                  │
                  ▼
              PDFium
                  │
                  ▼
              Bitmap
                  │
                  ▼
              PIL Image
                  │
                  ├── grayscale
                  ▼
             Final Image
```

Sau này chúng ta có thể refactor thành:

```text
RenderOptions
    │
    ├── dpi
    ├── rotation
    ├── crop
    └── ...

ImageProcessingOptions
    │
    ├── grayscale
    ├── ...
    └── ...
```

**Nhưng hôm nay chưa cần làm vậy.**

Đây là một ví dụ tốt về nguyên tắc:

> Không abstraction quá sớm.

Khi số option còn ít, giữ:

```python
RenderOptions
```

là hợp lý.

Khi pipeline lớn lên, chúng ta sẽ tách.

---

# 17. Bài tập thực hành

## Bài 1

Render một trang:

```text
150 DPI
RGB
```

sau đó:

```text
150 DPI
Grayscale
```

So sánh:

```python
print(image.mode)
print(image.size)
```

---

## Bài 2

Render cùng một trang ở:

```text
72 DPI
150 DPI
300 DPI
600 DPI
```

và grayscale tất cả.

Ghi lại:

```text
DPI
width
height
mode
```

---

## Bài 3 — Memory

Viết hàm:

```python
def estimate_image_memory(
    width: int,
    height: int,
    channels: int,
) -> int:
    ...
```

Ví dụ:

```python
estimate_image_memory(
    2550,
    3300,
    3,
)
```

và:

```python
estimate_image_memory(
    2550,
    3300,
    1,
)
```

So sánh RGB và grayscale.

---

## Bài 4 — quan trọng

Thiết kế:

```python
class ImageProcessor:
    def grayscale(self, image):
        ...
```

sau đó viết test mà **không cần mở PDF**.

Đây chính là lợi ích của việc tách:

```text
PDF rendering
        ≠
image processing
```

---

# 18. Kiến trúc sau Buổi 22

Hiện tại:

```text
                 Application
                     │
                     ▼
             PdfRenderService
                /         \
               /           \
              ▼             ▼
       PdfRenderer    ImageProcessor
           │                │
           ▼                │
       pypdfium2             │
           │                │
           ▼                │
       PdfBitmap             │
           │                │
           ▼                │
       PIL.Image ────────────┘
                 │
                 ▼
             Grayscale
```

Và roadmap đang tiến triển:

```text
21 DPI / Quality
      ↓
22 Grayscale
      ↓
23 Transparency
      ↓
24 Rotation
      ↓
25 MediaBox / CropBox
      ↓
26 Page Size
      ↓
27 Coordinate System
      ↓
28 Render Region
      ↓
29 Memory Optimization
      ↓
30 Thumbnail Generator
```

### Điều cần nhớ

**Grayscale không đồng nghĩa với binary black/white.**

Và quan trọng hơn:

> **Render PDF và xử lý ảnh sau render là hai trách nhiệm khác nhau.**

Buổi 23 chúng ta sẽ đi vào **Transparency** — phần khá thú vị vì lúc đó phải hiểu rõ sự khác nhau giữa **RGB, RGBA, alpha channel, transparent background và nền trắng khi xuất PNG/JPEG**.
