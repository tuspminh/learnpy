# Buổi 30 — Mini Project: PDF Thumbnail Generator

Đây là **bài tổng kết Phần III — PDF Rendering chuyên sâu**.

Mục tiêu không chỉ là tạo thumbnail, mà xây một mini project có architecture sạch, có thể mở rộng thành module dùng trong **PDF Reader / Novel Reader / Document Manager** sau này.

---

# 1. Mục tiêu project

Ta muốn chạy:

```bash
python -m pdf_thumbnail input.pdf --output thumbnails
```

Ví dụ:

```text
book.pdf
   │
   ├── Page 1 ──→ thumbnail-0001.jpg
   ├── Page 2 ──→ thumbnail-0002.jpg
   ├── Page 3 ──→ thumbnail-0003.jpg
   └── ...
```

Đặc biệt:

```text
Không:
PDF
 ↓
render toàn bộ
 ↓
RAM lớn
```

Mà:

```text
PDF
 ↓
Page 1
 ↓
render
 ↓
resize
 ↓
save
 ↓
release
 ↓
Page 2
 ↓
...
```

---

# 2. Kiến trúc

Ta xây:

```text
pdf_thumbnail/
│
├── domain/
│   ├── options.py
│   └── thumbnail.py
│
├── application/
│   ├── ports.py
│   └── service.py
│
├── infrastructure/
│   └── pdfium/
│       ├── document.py
│       └── renderer.py
│
├── presentation/
│   └── cli.py
│
└── __main__.py
```

Dependency:

```text
Presentation
     ↓
Application
     ↓
Domain

Infrastructure
     ↓
Application Ports
```

Cụ thể:

```text
CLI
 │
 ▼
ThumbnailService
 │
 ├──── PdfRenderer
 │
 └──── ThumbnailWriter
          │
          ▼
        JPEG
```

---

# 3. Domain — ThumbnailOptions

Tạo:

```python
# domain/options.py

from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailOptions:
    width: int = 300
    height: int = 400
    dpi: float = 100.0
    quality: int = 85

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError(
                "width phải > 0"
            )

        if self.height <= 0:
            raise ValueError(
                "height phải > 0"
            )

        if self.dpi <= 0:
            raise ValueError(
                "dpi phải > 0"
            )

        if not 1 <= self.quality <= 100:
            raise ValueError(
                "quality phải nằm trong 1..100"
            )
```

---

# 4. Tại sao thumbnail có width/height?

Ta không muốn thumbnail luôn có kích thước đúng:

```text
300 × 400
```

bằng cách ép méo ảnh.

Ví dụ page A4:

```text
210 × 297
```

tỷ lệ:

```text
210 / 297 ≈ 0.707
```

Nếu resize thành:

```text
300 × 400
```

tỷ lệ:

```text
0.75
```

ảnh sẽ hơi méo.

Ta nên:

```text
giữ aspect ratio
```

---

# 5. Domain — ThumbnailSize

```python
# domain/thumbnail.py

from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailSize:
    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError(
                "width phải > 0"
            )

        if self.height <= 0:
            raise ValueError(
                "height phải > 0"
            )
```

---

# 6. Tính kích thước giữ aspect ratio

```python
# domain/thumbnail.py


def fit_size(
    source_width: int,
    source_height: int,
    max_width: int,
    max_height: int,
) -> ThumbnailSize:

    if source_width <= 0:
        raise ValueError(
            "source_width phải > 0"
        )

    if source_height <= 0:
        raise ValueError(
            "source_height phải > 0"
        )

    ratio = min(
        max_width / source_width,
        max_height / source_height,
    )

    width = max(
        1,
        round(source_width * ratio),
    )

    height = max(
        1,
        round(source_height * ratio),
    )

    return ThumbnailSize(
        width=width,
        height=height,
    )
```

Ví dụ:

```python
size = fit_size(
    source_width=2480,
    source_height=3508,
    max_width=300,
    max_height=400,
)

print(size)
```

Kết quả gần:

```text
ThumbnailSize(width=283, height=400)
```

Không bị méo.

---

# 7. Application Port — PdfRenderer

Application không được biết `pypdfium2`.

Ta tạo Protocol:

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
        dpi: float,
    ):
        ...
```

Ở đây:

```text
Application
     ↓
PdfRenderer Protocol
     ↑
PdfiumRenderer
```

Đây chính là Dependency Inversion.

---

# 8. ThumbnailWriter

```python
# application/ports.py

from typing import Protocol


class ThumbnailWriter(Protocol):

    def save(
        self,
        image,
        page_index: int,
    ) -> None:
        ...
```

Application chỉ biết:

```text
save(image, page_index)
```

không cần biết:

```text
JPEG
PNG
filesystem
S3
database
```

---

# 9. Infrastructure — PdfiumRenderer

Đây là nơi `pypdfium2` xuất hiện.

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

        if not self.pdf_path.is_file():
            raise ValueError(
                f"Không phải file: {self.pdf_path}"
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
        page_index: int,
        dpi: float,
    ):
        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                f"Page index không hợp lệ: "
                f"{page_index}"
            )

        if dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        page = self._pdf[page_index]

        scale = dpi / 72.0

        bitmap = page.render(
            scale=scale,
        )

        return bitmap.to_pil()

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

# 10. Vì sao `PdfiumRenderer` trả PIL Image?

Ta đang làm:

```text
pypdfium2
    ↓
PdfBitmap
    ↓
PIL.Image
```

Application không cần biết:

```text
PdfBitmap
```

Đây là boundary giữa:

```text
Infrastructure
```

và:

```text
Application
```

---

# 11. ThumbnailProcessor

Bây giờ xây processor.

```python
# application/service.py

from PIL import Image


class ThumbnailProcessor:

    def __init__(
        self,
        width: int,
        height: int,
    ):
        self.width = width
        self.height = height

    def process(self, image):

        size = self._calculate_size(
            image.width,
            image.height,
        )

        return image.resize(
            (
                size[0],
                size[1],
            ),
            Image.Resampling.LANCZOS,
        )

    def _calculate_size(
        self,
        source_width,
        source_height,
    ):
        ratio = min(
            self.width / source_width,
            self.height / source_height,
        )

        return (
            max(
                1,
                round(source_width * ratio),
            ),
            max(
                1,
                round(source_height * ratio),
            ),
        )
```

---

# 12. Nhưng có một vấn đề memory

Code:

```python
thumbnail = processor.process(image)
```

bây giờ có:

```text
image
+
thumbnail
```

cùng tồn tại.

Không sao vì chỉ có **một page**.

Flow:

```text
Page bitmap
      ↓
PIL image
      ↓
thumbnail
      ↓
save
      ↓
close thumbnail
      ↓
close source
```

Không bao giờ giữ:

```text
500 source images
```

---

# 13. ThumbnailWriter

```python
# infrastructure/writer.py

from pathlib import Path


class JpegThumbnailWriter:

    def __init__(
        self,
        output_dir,
        quality=85,
    ):
        self.output_dir = Path(
            output_dir
        )
        self.quality = quality

    def save(
        self,
        image,
        page_index: int,
    ):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            self.output_dir
            / f"thumbnail-{page_index + 1:04d}.jpg"
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            output_path,
            format="JPEG",
            quality=self.quality,
            optimize=True,
        )
```

---

# 14. Application Service

Đây là phần quan trọng nhất.

```python
# application/service.py


class PdfThumbnailService:

    def __init__(
        self,
        renderer,
        processor,
        writer,
    ):
        self.renderer = renderer
        self.processor = processor
        self.writer = writer

    def generate(
        self,
        start_page=0,
        end_page=None,
        dpi=100.0,
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

        processed = 0

        for page_index in range(
            start_page,
            end_page,
        ):

            image = self.renderer.render_page(
                page_index,
                dpi,
            )

            try:
                thumbnail = (
                    self.processor.process(
                        image
                    )
                )

                try:
                    self.writer.save(
                        thumbnail,
                        page_index,
                    )

                finally:
                    thumbnail.close()

                processed += 1

            finally:
                image.close()

        return processed
```

---

# 15. Đây chính là bài học Buổi 29

Notice:

```python
image = ...
```

sau đó:

```python
try:
    thumbnail = ...
    try:
        writer.save(...)
    finally:
        thumbnail.close()

finally:
    image.close()
```

Memory:

```text
          Page N
            │
            ▼
       source image
            │
            ▼
        thumbnail
            │
            ▼
          save
            │
       ┌────┴────┐
       ▼         ▼
 thumbnail     source
   close        close
       │         │
       └────┬────┘
            ▼
         Page N+1
```

---

# 16. Có thể đơn giản hóa bằng `with`

Sau này ta có thể tạo abstraction:

```python
@contextmanager
def rendered_page(...):
    ...
```

nhưng ở mini project đầu tiên tôi muốn bạn **nhìn thấy rõ ownership** bằng `try/finally`.

Đây là code rất đáng học.

---

# 17. CLI

```python
# presentation/cli.py

import argparse

from application.service import (
    PdfThumbnailService,
    ThumbnailProcessor,
)

from infrastructure.pdfium.renderer import (
    PdfiumRenderer,
)

from infrastructure.writer import (
    JpegThumbnailWriter,
)


def build_parser():

    parser = argparse.ArgumentParser(
        description=(
            "Generate PDF thumbnails"
        )
    )

    parser.add_argument(
        "input",
        help="PDF input",
    )

    parser.add_argument(
        "--output",
        default="thumbnails",
        help="Output directory",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=300,
    )

    parser.add_argument(
        "--height",
        type=int,
        default=400,
    )

    parser.add_argument(
        "--dpi",
        type=float,
        default=100.0,
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=85,
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Page bắt đầu, 1-based",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="Page kết thúc, 1-based inclusive",
    )

    return parser
```

---

# 18. `main()`

```python
# presentation/cli.py


def main():

    parser = build_parser()

    args = parser.parse_args()

    if args.start < 1:
        parser.error(
            "--start phải >= 1"
        )

    if args.end is not None:
        if args.end < args.start:
            parser.error(
                "--end phải >= --start"
            )

    renderer = PdfiumRenderer(
        args.input
    )

    processor = ThumbnailProcessor(
        width=args.width,
        height=args.height,
    )

    writer = JpegThumbnailWriter(
        output_dir=args.output,
        quality=args.quality,
    )

    service = PdfThumbnailService(
        renderer=renderer,
        processor=processor,
        writer=writer,
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

        count = service.generate(
            start_page=start_page,
            end_page=end_page,
            dpi=args.dpi,
        )

        print(
            f"Đã tạo {count} thumbnails."
        )

    finally:
        renderer.close()
```

---

# 19. `__main__.py`

```python
# __main__.py

from presentation.cli import main


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python -m pdf_thumbnail book.pdf
```

Hoặc:

```bash
python -m pdf_thumbnail book.pdf \
    --output thumbs \
    --width 300 \
    --height 400 \
    --dpi 100 \
    --quality 85
```

---

# 20. Cấu trúc hoàn chỉnh

```text
pdf_thumbnail/
│
├── __init__.py
├── __main__.py
│
├── domain/
│   ├── __init__.py
│   ├── options.py
│   └── thumbnail.py
│
├── application/
│   ├── __init__.py
│   ├── ports.py
│   └── service.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── writer.py
│   └── pdfium/
│       ├── __init__.py
│       └── renderer.py
│
└── presentation/
    ├── __init__.py
    └── cli.py

tests/
├── test_domain.py
├── test_processor.py
└── test_service.py
```

---

# 21. Unit test Domain

```python
# tests/test_domain.py

import pytest

from pdf_thumbnail.domain.thumbnail import (
    fit_size,
)


def test_fit_a4():

    result = fit_size(
        source_width=2480,
        source_height=3508,
        max_width=300,
        max_height=400,
    )

    assert result.width == 283
    assert result.height == 400


def test_invalid_source():

    with pytest.raises(ValueError):
        fit_size(
            source_width=0,
            source_height=100,
            max_width=300,
            max_height=400,
        )
```

---

# 22. Test Processor

```python
# tests/test_processor.py

from PIL import Image

from pdf_thumbnail.application.service import (
    ThumbnailProcessor,
)


def test_thumbnail_keeps_aspect_ratio():

    image = Image.new(
        "RGB",
        (2480, 3508),
    )

    processor = ThumbnailProcessor(
        width=300,
        height=400,
    )

    result = processor.process(image)

    assert result.size == (283, 400)

    result.close()
    image.close()
```

---

# 23. Fake Renderer

Bây giờ test Application mà **không cần PDF thật**.

```python
# tests/test_service.py


from PIL import Image


class FakeRenderer:

    def __init__(self, page_count=3):
        self._page_count = page_count
        self.rendered_pages = []

    @property
    def page_count(self):
        return self._page_count

    def render_page(
        self,
        page_index,
        dpi,
    ):
        self.rendered_pages.append(
            page_index
        )

        return Image.new(
            "RGB",
            (1000, 1400),
        )
```

---

# 24. Fake Writer

```python
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
def test_generate_all_pages():

    renderer = FakeRenderer(
        page_count=3
    )

    processor = ThumbnailProcessor(
        width=300,
        height=400,
    )

    writer = FakeWriter()

    service = PdfThumbnailService(
        renderer=renderer,
        processor=processor,
        writer=writer,
    )

    count = service.generate(
        start_page=0,
        end_page=3,
        dpi=100,
    )

    assert count == 3

    assert renderer.rendered_pages == [
        0,
        1,
        2,
    ]

    assert len(writer.saved) == 3
```

Chạy:

```bash
pytest -q
```

---

# 25. Một cải tiến quan trọng: không resize quá lớn

Hiện tại:

```text
PDF
 ↓
render 100 DPI
 ↓
PIL
 ↓
thumbnail 300×400
```

Nếu PDF page rất lớn thì vẫn có thể tốn RAM.

Ví dụ:

```text
page = 10,000 × 14,000
```

thì render trước rồi resize vẫn rất nặng.

Đây là vấn đề:

```text
Render resolution
        ≠
Thumbnail resolution
```

---

# 26. Tính DPI từ thumbnail size

Đây là tối ưu quan trọng.

Giả sử page A4:

```text
595 × 842 pt
```

và thumbnail cần:

```text
300 × 400 px
```

Ta không cần render:

```text
2480 × 3508
```

rồi resize xuống.

Có thể chọn DPI thấp hơn sao cho bitmap gần kích thước thumbnail.

Ví dụ:

```text
300 px / 595 pt × 72
≈ 36 DPI
```

Do đó:

```text
render ~ 40 DPI
```

có thể đủ cho thumbnail.

---

# 27. Thumbnail pipeline tối ưu

Thay vì:

```text
PDF
 ↓
300 DPI
 ↓
2480×3508
 ↓
resize
 ↓
300×400
```

ta làm:

```text
PDF
 ↓
40–60 DPI
 ↓
~300×400
 ↓
small resize
 ↓
JPEG
```

RAM giảm rất mạnh.

Đây là một trong những bài học quan trọng nhất của Part III:

> **Không render ở resolution cao hơn nhu cầu cuối cùng nếu output chỉ là thumbnail.**

---

# 28. Tính DPI mục tiêu

Ta có:

```python
def dpi_for_width(
    page_width_pt,
    target_width_px,
):
    return (
        target_width_px
        * 72
        / page_width_pt
    )
```

Ví dụ:

```python
dpi = dpi_for_width(
    page_width_pt=595.28,
    target_width_px=300,
)

print(dpi)
```

≈:

```text
36.2 DPI
```

Tuy nhiên nên thêm hệ số an toàn:

```text
36 × 1.5
≈ 54 DPI
```

rồi resize nhẹ.

---

# 29. Nhưng thumbnail không nhất thiết biết PageSize?

Đây là lý do architecture tốt quan trọng.

Renderer có thể cung cấp:

```python
page_size()
```

hoặc application lấy:

```text
PageSize
```

rồi tính:

```text
target DPI
```

Architecture nâng cao:

```text
Page Geometry
      ↓
Target Thumbnail Size
      ↓
Optimal DPI
      ↓
Renderer
```

Đây là bước phát triển tiếp theo, không cần nhồi tất cả vào mini project đầu tiên.

---

# 30. Memory profile của project

Pipeline hiện tại:

```text
             PDF
              │
              ▼
          PdfPage
              │
              ▼
          PdfBitmap
              │
              ▼
          PIL Image
              │
              ▼
         Thumbnail
              │
              ▼
             JPEG
              │
              ▼
           release
```

Peak memory chủ yếu xảy ra tại:

```text
PIL source
+
PIL thumbnail
```

nhưng chỉ cho **một page**.

Đây là mục tiêu của streaming architecture.

---

# 31. So sánh hai kiến trúc

### Cách A — sai cho PDF lớn

```text
render all
    ↓
images[]
    ↓
resize all
    ↓
save all
```

Memory:

```text
O(N)
```

với `N = số page`.

### Cách B — chúng ta xây

```text
render page
 ↓
resize
 ↓
save
 ↓
release
```

Memory:

```text
O(1)
```

theo số page, bỏ qua các buffer nội bộ và các yếu tố phụ thuộc implementation.

Đây là một khái niệm rất quan trọng:

> **Batch size 1 / streaming processing.**

---

# 32. SOLID trong project

### SRP

`PdfiumRenderer`:

```text
PDF → Image
```

`ThumbnailProcessor`:

```text
Image → Thumbnail
```

`JpegThumbnailWriter`:

```text
Thumbnail → File
```

`PdfThumbnailService`:

```text
điều phối workflow
```

---

### DIP

Application:

```python
renderer
processor
writer
```

được inject từ ngoài.

Không:

```python
PdfThumbnailService():
    pdfium.PdfDocument(...)
```

Application không phụ thuộc trực tiếp PDFium.

---

### OCP

Có thể thêm:

```text
PngThumbnailWriter
WebpThumbnailWriter
MemoryWriter
S3Writer
```

mà không sửa service.

---

# 33. Có thể thay pypdfium2

Hôm nay:

```text
PdfiumRenderer
```

Ngày mai:

```text
PyMuPDFRenderer
```

hoặc:

```text
OtherPdfRenderer
```

Application vẫn:

```text
PdfThumbnailService
```

không thay đổi.

Đây chính là giá trị của Port/Adapter.

---

# 34. Liên hệ với project Novel Crawler của bạn

Architecture này rất giống architecture crawler mà chúng ta đã xây:

```text
Crawler Application
        │
        ▼
    Port/Protocol
        │
        ▼
 Infrastructure
```

Ví dụ crawler:

```text
Use Case
   ↓
Fetcher Protocol
   ↓
HttpxFetcher
```

PDF:

```text
Use Case
   ↓
PdfRenderer Protocol
   ↓
PdfiumRenderer
```

Tư duy architecture hoàn toàn giống nhau.

---

# 35. Những gì Part III đã dạy

Chúng ta bắt đầu:

```text
PdfDocument
```

và cuối cùng xây được:

```text
Production-style PDF thumbnail pipeline
```

Toàn bộ progression:

```text
21 Render chất lượng cao
        ↓
22 Grayscale
        ↓
23 Transparency
        ↓
24 Rotation
        ↓
25 CropBox / MediaBox
        ↓
26 Page Size
        ↓
27 Coordinate System
        ↓
28 Render Region
        ↓
29 Memory Optimization
        ↓
30 PDF Thumbnail Generator
```

---

# 36. Checklist kiến thức

Bạn hiện đã có thể giải thích:

* PDF page được rasterize như thế nào.
* DPI và `scale` liên hệ thế nào.
* RGB / RGBA / grayscale ảnh hưởng memory ra sao.
* PDF transparency khác bitmap alpha thế nào.
* Rotation của PDF khác rotation PIL thế nào.
* MediaBox và CropBox.
* Page size tính bằng PDF points.
* PDF coordinate system.
* Chuyển PDF coordinate → image coordinate.
* Render region.
* Tại sao không nên giữ hàng trăm PIL Image.
* Generator/streaming processing.
* `try/finally` để quản lý lifetime.
* Dependency Injection.
* Renderer Port.
* Writer Port.
* Application Service.
* Thumbnail generation không làm méo aspect ratio.

---

# 37. Bài tập cuối Part III

Hãy nâng cấp project thành CLI:

```bash
python -m pdf_thumbnail book.pdf \
    --output thumbs \
    --width 300 \
    --height 400 \
    --format jpg \
    --quality 85
```

và thêm:

```bash
--start 10
--end 50
```

để chỉ tạo:

```text
page 10 → thumbnail
...
page 50 → thumbnail
```

Sau đó thêm:

```bash
--grayscale
```

để tạo thumbnail grayscale.

Cuối cùng thử với PDF vài trăm trang và quan sát:

```text
RAM
CPU
thời gian
output size
```

Mục tiêu quan trọng nhất không phải chạy nhanh nhất, mà là chứng minh:

```text
100 pages
1000 pages
10000 pages
```

**không khiến application giữ 100/1000/10000 ảnh trong RAM.**

---

# 🎓 Kết thúc Phần III

Từ đây roadmap chuyển sang **Phần IV — PDF Editing / Document Manipulation** nếu tiếp tục khóa pypdfium2. Tuy nhiên trước khi sang phần mới, nền tảng rendering của chúng ta đã đủ chắc để xây **PDF Reader**, **thumbnail panel**, **page preview**, **zoom/crop**, và sau này tích hợp vào kiến trúc PySide6 của ứng dụng đọc truyện/tài liệu.
