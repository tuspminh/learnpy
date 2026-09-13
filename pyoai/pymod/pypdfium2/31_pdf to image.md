# Phần IV — PDF Processing Pipeline

## Buổi 31 — PDF → Image

Từ Phần III chúng ta đã học **render PDF**, nhưng hôm nay sẽ nâng nó thành một **pipeline xử lý PDF → Image** có kiến trúc rõ ràng.

Điểm khác biệt:

```text
Phần III
PDF → render → PIL.Image
```

Phần IV:

```text
PDF
 ↓
Load
 ↓
Render
 ↓
Image Processing
 ↓
Output
```

Và pipeline này sẽ là nền tảng cho:

```text
31 PDF → Image
32 PDF → OCR
33 pypdfium2 + Pillow
34 pypdfium2 + OpenCV
35 pypdfium2 + Tesseract
36 PDF scan
37 Detect text region
38 Parallel rendering
39 Streaming / batch
40 PDF OCR Pipeline
```

---

# 1. Mục tiêu Buổi 31

Sau bài này, bạn sẽ xây được pipeline:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ▼
PDFium Render
 │
 ▼
PdfBitmap
 │
 ▼
PIL.Image
 │
 ▼
Image Processor
 │
 ▼
Image Writer
 │
 ▼
PNG / JPEG
```

Ví dụ:

```bash
python -m pdf_image book.pdf --output images
```

Kết quả:

```text
images/
├── page-0001.png
├── page-0002.png
├── page-0003.png
├── ...
└── page-0100.png
```

---

# 2. PDF → Image thực chất là gì?

PDF không phải một tập hợp các ảnh.

Ví dụ một page có:

```text
Text
Image
Vector
Line
Shape
Font
Transparency
```

PDFium phải **rasterize** chúng:

```text
PDF objects
     ↓
PDFium rendering engine
     ↓
Bitmap
```

Sau đó:

```text
Bitmap
 ↓
PIL.Image
```

Vì vậy:

> PDF → Image là quá trình **rasterization**, không đơn giản là "extract image".

Đây là distinction rất quan trọng.

---

# 3. PDF → Image khác Extract Embedded Image

Có hai trường hợp:

### A. Render page

```text
PDF Page
 ↓
PDFium
 ↓
Bitmap
```

Output nhìn giống page PDF:

```text
text
images
vector
background
```

### B. Extract embedded image

```text
PDF
 ↓
Image Object
 ↓
Original image
```

Nếu PDF chứa:

```text
photo.jpg
```

thì extract có thể lấy được ảnh JPEG gốc.

Nhưng:

```text
PDF → Image
```

trong pipeline hôm nay có nghĩa là:

> **Render toàn bộ page thành raster image.**

---

# 4. Kiến trúc pipeline

Ta sẽ dùng:

```text
Presentation
     │
     ▼
Application
     │
     ▼
Render Port
     │
     ▼
Infrastructure
     │
     ▼
pypdfium2
```

Sau render:

```text
Application
     │
     ├── Image Processor
     │
     └── Image Writer
```

Toàn bộ:

```text
                  PDF
                   │
                   ▼
              PdfRenderer
                   │
                   ▼
                Bitmap
                   │
                   ▼
               PIL.Image
                   │
          ┌────────┴────────┐
          ▼                 ▼
       Processor           Writer
          │                 │
          ▼                 ▼
       PIL.Image          File
```

---

# 5. Tạo project

```text
pdf_image/
├── __init__.py
├── __main__.py
│
├── domain/
│   ├── __init__.py
│   └── options.py
│
├── application/
│   ├── __init__.py
│   ├── ports.py
│   └── service.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── pdfium/
│   │   ├── __init__.py
│   │   └── renderer.py
│   │
│   └── image/
│       ├── __init__.py
│       └── writer.py
│
└── presentation/
    ├── __init__.py
    └── cli.py

tests/
├── test_options.py
└── test_service.py
```

---

# 6. Domain — ImageFormat

Ta không muốn Application biết string tùy tiện:

```python
format="png"
```

Tạo Enum:

```python
# domain/options.py

from enum import Enum


class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
```

---

# 7. RenderOptions

Ta tái sử dụng tư duy từ Part III:

```python
# domain/options.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0

    grayscale: bool = False

    rotation: int = 0

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "dpi phải > 0"
            )

        if self.rotation not in {
            0,
            90,
            180,
            270,
        }:
            raise ValueError(
                "rotation phải là "
                "0, 90, 180 hoặc 270"
            )

    @property
    def scale(self):
        return self.dpi / 72.0
```

---

# 8. OutputOptions

Không nên trộn:

```text
render options
```

với:

```text
output options
```

Tách:

```python
@dataclass(frozen=True)
class OutputOptions:

    format: ImageFormat = ImageFormat.PNG

    quality: int = 90

    def __post_init__(self):

        if not 1 <= self.quality <= 100:
            raise ValueError(
                "quality phải nằm trong 1..100"
            )
```

Architecture:

```text
RenderOptions
├── DPI
├── rotation
└── grayscale

OutputOptions
├── PNG/JPEG
└── quality
```

---

# 9. Application Port

```python
# application/ports.py

from typing import Protocol


class PdfRenderer(Protocol):

    @property
    def page_count(self) -> int:
        ...

    def render_page(
        self,
        page_index: int,
        options,
    ):
        ...
```

Writer:

```python
class ImageWriter(Protocol):

    def save(
        self,
        image,
        page_index: int,
    ) -> None:
        ...
```

Processor:

```python
class ImageProcessor(Protocol):

    def process(self, image):
        ...
```

---

# 10. PdfiumRenderer

Infrastructure:

```python
# infrastructure/pdfium/renderer.py

from pathlib import Path

import pypdfium2 as pdfium


class PdfiumRenderer:

    def __init__(self, pdf_path):
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

    @property
    def page_count(self):

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        return len(self._pdf)

    def render_page(
        self,
        page_index,
        options,
    ):

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                page_index
            )

        page = self._pdf[page_index]

        bitmap = page.render(
            scale=options.scale,
            rotation=options.rotation,
        )

        image = bitmap.to_pil()

        if options.grayscale:
            image = image.convert("L")

        return image

    def close(self):

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

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

# 11. Một điểm kiến trúc quan trọng

Ở đây:

```python
bitmap = page.render(...)
```

là trách nhiệm của:

```text
Infrastructure
```

Còn:

```python
image.convert("L")
```

là image processing.

Trong project nhỏ có thể để chung.

Nhưng khi project lớn:

```text
PdfiumRenderer
    ↓
PdfBitmap → PIL

ImageProcessor
    ↓
PIL → PIL
```

sẽ sạch hơn.

Vì chúng ta đang xây pipeline để sau này dùng:

```text
Pillow
OpenCV
Tesseract
OCR
```

nên nên giữ boundary rõ.

---

# 12. Tách ImageProcessor

```python
# infrastructure/image/processor.py

class PillowImageProcessor:

    def grayscale(self, image):

        return image.convert("L")
```

Nhưng pipeline hôm nay chưa cần processor phức tạp.

Ta có thể giữ:

```text
PdfiumRenderer
 ↓
PIL Image
```

và Application điều phối processor.

---

# 13. ImageWriter

```python
# infrastructure/image/writer.py

from pathlib import Path


class PillowImageWriter:

    def __init__(
        self,
        output_dir,
        output_format,
        quality=90,
    ):
        self.output_dir = Path(
            output_dir
        )

        self.output_format = (
            output_format
        )

        self.quality = quality

    def save(
        self,
        image,
        page_index,
    ):

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = (
            self.output_format.value
        )

        path = (
            self.output_dir
            / f"page-{page_index + 1:04d}.{extension}"
        )

        if self.output_format.value == "jpeg":

            if image.mode != "RGB":
                image = image.convert(
                    "RGB"
                )

            image.save(
                path,
                format="JPEG",
                quality=self.quality,
            )

        else:

            image.save(
                path,
                format="PNG",
            )
```

---

# 14. JPEG và RGBA

Đây là vấn đề bạn đã học ở Buổi 23.

JPEG không hỗ trợ alpha.

Nếu:

```python
image.mode == "RGBA"
```

thì:

```python
image.save(
    "page.jpg",
    format="JPEG",
)
```

có thể lỗi.

Phải:

```python
image.convert("RGB")
```

trước.

Do đó Writer là nơi thích hợp để xử lý format-specific requirements.

---

# 15. Application Service

```python
# application/service.py


class PdfImageService:

    def __init__(
        self,
        renderer,
        writer,
    ):
        self.renderer = renderer
        self.writer = writer

    def export(
        self,
        render_options,
        start_page=0,
        end_page=None,
    ):

        if end_page is None:
            end_page = self.renderer.page_count

        if start_page < 0:
            raise ValueError(
                "start_page phải >= 0"
            )

        if end_page > self.renderer.page_count:
            raise ValueError(
                "end_page vượt quá page_count"
            )

        if start_page >= end_page:
            raise ValueError(
                "start_page phải < end_page"
            )

        count = 0

        for page_index in range(
            start_page,
            end_page,
        ):

            image = self.renderer.render_page(
                page_index,
                render_options,
            )

            try:

                self.writer.save(
                    image,
                    page_index,
                )

                count += 1

            finally:
                image.close()

        return count
```

Đây chính là:

```text
Streaming
+
Resource Lifetime
```

từ Buổi 29.

---

# 16. Pipeline hiện tại

```text
PDF
 │
 ▼
PdfiumRenderer
 │
 ▼
PIL.Image
 │
 ▼
PillowImageWriter
 │
 ▼
PNG/JPEG
```

Mỗi lần chỉ có:

```text
1 page
```

trong memory.

---

# 17. CLI

```python
# presentation/cli.py

import argparse

from domain.options import (
    ImageFormat,
    RenderOptions,
)

from application.service import (
    PdfImageService,
)

from infrastructure.pdfium.renderer import (
    PdfiumRenderer,
)

from infrastructure.image.writer import (
    PillowImageWriter,
)


def build_parser():

    parser = argparse.ArgumentParser(
        description="PDF → Image"
    )

    parser.add_argument(
        "input",
    )

    parser.add_argument(
        "--output",
        default="images",
    )

    parser.add_argument(
        "--dpi",
        type=float,
        default=150,
    )

    parser.add_argument(
        "--format",
        choices=[
            "png",
            "jpeg",
        ],
        default="png",
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=90,
    )

    parser.add_argument(
        "--grayscale",
        action="store_true",
    )

    parser.add_argument(
        "--rotation",
        type=int,
        choices=[
            0,
            90,
            180,
            270,
        ],
        default=0,
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--end",
        type=int,
    )

    return parser
```

---

# 18. Main

```python
def main():

    parser = build_parser()

    args = parser.parse_args()

    renderer = PdfiumRenderer(
        args.input
    )

    image_format = ImageFormat(
        args.format
    )

    writer = PillowImageWriter(
        output_dir=args.output,
        output_format=image_format,
        quality=args.quality,
    )

    service = PdfImageService(
        renderer=renderer,
        writer=writer,
    )

    render_options = RenderOptions(
        dpi=args.dpi,
        grayscale=args.grayscale,
        rotation=args.rotation,
    )

    try:

        renderer.open()

        total = renderer.page_count

        start_page = args.start - 1

        if args.end is None:
            end_page = total
        else:
            end_page = min(
                args.end,
                total,
            )

        count = service.export(
            render_options=render_options,
            start_page=start_page,
            end_page=end_page,
        )

        print(
            f"Đã export {count} pages."
        )

    finally:

        renderer.close()
```

---

# 19. `__main__.py`

```python
from presentation.cli import main


if __name__ == "__main__":
    main()
```

---

# 20. Chạy thử

PNG:

```bash
python -m pdf_image book.pdf \
    --output images \
    --dpi 150 \
    --format png
```

JPEG:

```bash
python -m pdf_image book.pdf \
    --output images \
    --dpi 120 \
    --format jpeg \
    --quality 85
```

Grayscale:

```bash
python -m pdf_image book.pdf \
    --output images \
    --dpi 150 \
    --grayscale
```

Chỉ page 10 → 20:

```bash
python -m pdf_image book.pdf \
    --output images \
    --start 10 \
    --end 20
```

---

# 21. Một vấn đề cần sửa

Hiện tại CLI nhận:

```text
--start 10
--end 20
```

theo **1-based inclusive**.

Application nhận:

```text
start_page=9
end_page=20
```

theo Python convention:

```python
range(9, 20)
```

tức:

```text
9 ... 19
```

Tương ứng:

```text
page 10 ... page 20
```

Đây là boundary rất tốt:

```text
CLI
1-based inclusive

Application
0-based [start, end)
```

---

# 22. Unit test Application

Ta không cần PDF thật.

```python
from PIL import Image


class FakeRenderer:

    page_count = 3

    def render_page(
        self,
        page_index,
        options,
    ):
        return Image.new(
            "RGB",
            (100, 100),
        )


class FakeWriter:

    def __init__(self):
        self.saved = []

    def save(
        self,
        image,
        page_index,
    ):
        self.saved.append(
            (
                page_index,
                image.size,
            )
        )
```

Test:

```python
def test_export_all_pages():

    renderer = FakeRenderer()

    writer = FakeWriter()

    service = PdfImageService(
        renderer=renderer,
        writer=writer,
    )

    options = RenderOptions(
        dpi=100,
    )

    count = service.export(
        render_options=options,
    )

    assert count == 3

    assert writer.saved == [
        (0, (100, 100)),
        (1, (100, 100)),
        (2, (100, 100)),
    ]
```

---

# 23. Test page range

```python
def test_export_page_range():

    renderer = FakeRenderer()

    writer = FakeWriter()

    service = PdfImageService(
        renderer=renderer,
        writer=writer,
    )

    options = RenderOptions()

    count = service.export(
        render_options=options,
        start_page=1,
        end_page=3,
    )

    assert count == 2

    assert writer.saved == [
        (1, (100, 100)),
        (2, (100, 100)),
    ]
```

---

# 24. Test validation

```python
import pytest


def test_invalid_page_range():

    renderer = FakeRenderer()

    writer = FakeWriter()

    service = PdfImageService(
        renderer=renderer,
        writer=writer,
    )

    with pytest.raises(ValueError):

        service.export(
            render_options=RenderOptions(),
            start_page=3,
            end_page=1,
        )
```

---

# 25. Test resource cleanup

Đây là test rất đáng chú ý.

Ta tạo:

```python
class TrackingImage:

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
```

Renderer:

```python
class TrackingRenderer:

    page_count = 1

    def __init__(self):
        self.image = TrackingImage()

    def render_page(
        self,
        page_index,
        options,
    ):
        return self.image
```

Writer:

```python
class FailingWriter:

    def save(
        self,
        image,
        page_index,
    ):
        raise RuntimeError(
            "save failed"
        )
```

Test:

```python
def test_image_closed_when_writer_fails():

    renderer = TrackingRenderer()

    writer = FailingWriter()

    service = PdfImageService(
        renderer=renderer,
        writer=writer,
    )

    with pytest.raises(RuntimeError):

        service.export(
            render_options=RenderOptions()
        )

    assert renderer.image.closed is True
```

Test này chứng minh:

```python
finally:
    image.close()
```

thực sự hoạt động.

---

# 26. Vì sao Pipeline này quan trọng cho OCR?

Đây chính là cầu nối sang Buổi 32.

Hiện tại:

```text
PDF
 ↓
render
 ↓
PIL.Image
 ↓
save
```

OCR sẽ thay:

```text
save
```

bằng:

```text
OCR
```

Thành:

```text
PDF
 ↓
PdfiumRenderer
 ↓
PIL.Image
 ↓
OCR Engine
 ↓
text
```

Ví dụ:

```text
Page 1
 ↓
Image
 ↓
Tesseract
 ↓
"Chapter One..."
```

---

# 27. Pipeline tiến hóa

### Buổi 31

```text
PDF
 ↓
Render
 ↓
Image
 ↓
File
```

### Buổi 32

```text
PDF
 ↓
Render
 ↓
Image
 ↓
OCR
 ↓
Text
```

### Buổi 33

```text
PDF
 ↓
pypdfium2
 ↓
Pillow
 ↓
preprocess
```

### Buổi 34

```text
PDF
 ↓
pypdfium2
 ↓
OpenCV
 ↓
image processing
```

### Buổi 35

```text
PDF
 ↓
pypdfium2
 ↓
Pillow/OpenCV
 ↓
Tesseract
 ↓
Text
```

Cuối cùng:

```text
PDF
 ↓
Render
 ↓
Preprocess
 ↓
Detect text
 ↓
OCR
 ↓
Post-process
 ↓
Store
```

---

# 28. Điều quan trọng về PDF scan

Một PDF scan thường:

```text
PDF Page
    ↓
large image
```

chứ không có text layer.

Ví dụ:

```text
page.get_textpage()
```

có thể không cho chúng ta text hữu ích.

Nhưng:

```text
page.render()
```

vẫn tạo được:

```text
PIL.Image
```

Sau đó:

```text
PIL.Image
 ↓
OCR
```

Vì vậy render chính là **cửa vào của OCR pipeline**.

---

# 29. Pipeline chuẩn bị cho OpenCV

Ở Buổi 34 chúng ta sẽ có:

```text
Pdfium
   ↓
PIL
   ↓
NumPy
   ↓
OpenCV
```

Ví dụ:

```text
PIL.Image
     ↓
numpy.ndarray
     ↓
cv2.cvtColor
     ↓
threshold
     ↓
denoise
     ↓
OCR
```

Cho nên hôm nay chúng ta cố tình giữ:

```text
PdfRenderer
```

và:

```text
ImageProcessor
```

tách biệt.

---

# 30. Một nguyên tắc architecture rất quan trọng

Không nên biến:

```python
PdfiumRenderer
```

thành một class khổng lồ:

```text
PdfiumRenderer
├── render
├── grayscale
├── threshold
├── denoise
├── crop
├── OCR
├── save PNG
├── save JPEG
├── save WebP
└── ...
```

Đó là:

```text
God Object
```

Thay vào đó:

```text
PdfiumRenderer
       ↓
     Image
       ↓
ImageProcessor
       ↓
Processed Image
       ↓
ImageWriter
```

Mỗi thành phần một trách nhiệm.

---

# 31. Dependency graph

Ta muốn:

```text
presentation
      ↓
application
      ↓
domain
```

Infrastructure:

```text
infrastructure
      ↓
application ports
```

Không muốn:

```text
domain
  ↓
pypdfium2
```

và cũng không muốn:

```text
application
  ↓
pypdfium2
```

Đây chính là Clean Architecture mà bạn đã học.

---

# 32. Project hôm nay có thể mở rộng thành

```text
PDF Processing Framework
│
├── Render
│   └── PdfiumRenderer
│
├── Image Processing
│   ├── PillowProcessor
│   └── OpenCVProcessor
│
├── OCR
│   ├── Tesseract
│   └── Other OCR
│
└── Output
    ├── FileWriter
    ├── JsonWriter
    └── DatabaseWriter
```

Và pipeline:

```text
PDF
 ↓
Render
 ↓
Process
 ↓
OCR
 ↓
Post-process
 ↓
Persist
```

Đây chính là architecture chúng ta sẽ tiến dần tới **Buổi 40 — PDF OCR Pipeline**.

---

# 33. Tổng kết Buổi 31

Hôm nay chúng ta đã chuyển từ:

```text
"Học render PDF"
```

sang:

```text
"Xây PDF Processing Pipeline"
```

Kiến trúc:

```text
                  ┌──────────────┐
                  │     PDF      │
                  └──────┬───────┘
                         ↓
                 ┌───────────────┐
                 │ PdfiumRenderer│
                 └──────┬────────┘
                        ↓
                   PIL.Image
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
       ImageProcessor        ImageWriter
                                  ↓
                             PNG / JPEG
```

Các nguyên tắc quan trọng:

1. **PDF → Image là rasterization**, không phải extract embedded image.
2. `pypdfium2` nằm ở Infrastructure.
3. Application phụ thuộc vào Protocol/Port.
4. Render options và output options nên tách.
5. Xử lý page theo streaming để tránh giữ toàn bộ ảnh trong RAM.
6. `try/finally` đảm bảo image được release.
7. Writer chịu trách nhiệm format-specific behavior như JPEG cần RGB.
8. Kiến trúc này chính là nền tảng để sang **OCR**.

### Roadmap hiện tại

```text
31. PDF → Image                 ✅
32. PDF → OCR                   ⬜
33. pypdfium2 + Pillow          ⬜
34. pypdfium2 + OpenCV          ⬜
35. pypdfium2 + Tesseract       ⬜
36. Xử lý PDF scan              ⬜
37. Detect vùng text             ⬜
38. Parallel rendering          ⬜
39. Streaming / batch processing ⬜
40. Mini Project: PDF OCR       ⬜
```

**Buổi 32 sẽ bắt đầu phần OCR: PDF → Image → OCR → Text**, trong đó chúng ta sẽ thiết kế `OcrEngine` dưới dạng Port để sau này có thể thay Tesseract bằng engine OCR khác mà không phải sửa Application Layer.
