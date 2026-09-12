# Buổi 10 — Mini Project: PDF → Image Converter

Đây là **Mini Project kết thúc Phần I — Làm quen**.

Chúng ta sẽ gom kiến thức từ Buổi 1 → 9 thành một chương trình CLI hoàn chỉnh:

```text
PDF
 │
 ▼
PdfDocument
 │
 ├── Page 1 ──► Render ──► PNG/JPEG
 ├── Page 2 ──► Render ──► PNG/JPEG
 ├── Page 3 ──► Render ──► PNG/JPEG
 │
 └── Page N ──► Render ──► PNG/JPEG
```

Chương trình hỗ trợ:

```text
✓ PDF input
✓ output directory
✓ PNG / JPEG
✓ DPI
✓ JPEG quality
✓ page range
✓ progress
✓ mở PDF một lần
✓ xử lý từng page
✓ giải phóng image sau mỗi page
✓ CLI bằng argparse
```

---

# 1. Mục tiêu project

Ta muốn chạy đơn giản:

```bash
python -m pdf_converter sample.pdf output
```

Mặc định:

```text
DPI = 150
format = PNG
```

Hoặc:

```bash
python -m pdf_converter sample.pdf output --dpi 300
```

JPEG:

```bash
python -m pdf_converter sample.pdf output --format jpeg
```

JPEG quality:

```bash
python -m pdf_converter sample.pdf output --format jpeg --quality 85
```

Chỉ render một khoảng trang:

```bash
python -m pdf_converter sample.pdf output --start 10 --end 20
```

---

# 2. Kiến trúc project

Ta sẽ không nhét tất cả vào `main.py`.

```text
pdf_converter/
│
├── __init__.py
├── __main__.py
│
├── domain/
│   ├── __init__.py
│   └── models.py
│
├── application/
│   ├── __init__.py
│   └── convert_pdf.py
│
├── infrastructure/
│   ├── __init__.py
│   └── pdfium/
│       ├── __init__.py
│       ├── document.py
│       ├── renderer.py
│       └── exporter.py
│
└── presentation/
    ├── __init__.py
    └── cli.py
```

Kiến trúc:

```text
                 CLI
                  │
                  ▼
             Application
                  │
                  ▼
              Domain
                  │
                  ▼
          Infrastructure
                  │
          ┌───────┴────────┐
          ▼                ▼
      pypdfium2          Pillow
```

Đây là phiên bản mini của Clean Architecture mà bạn đã học trước đó.

---

# 3. Domain Model

File:

```text
domain/models.py
```

Chúng ta cần model cấu hình conversion.

```python
from dataclasses import dataclass
from enum import Enum


class ImageFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"


@dataclass(frozen=True)
class ConvertOptions:
    dpi: float = 150.0
    image_format: ImageFormat = ImageFormat.PNG
    quality: int = 90
    start_page: int = 0
    end_page: int | None = None

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("DPI phải > 0")

        if not 1 <= self.quality <= 100:
            raise ValueError(
                "JPEG quality phải nằm trong 1..100"
            )

        if self.start_page < 0:
            raise ValueError(
                "start_page phải >= 0"
            )

        if self.end_page is not None:
            if self.end_page <= self.start_page:
                raise ValueError(
                    "end_page phải > start_page"
                )

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

---

# 4. Tại sao `ConvertOptions` nằm trong Domain?

Vì:

```text
DPI
format
quality
page range
```

không phải kiến thức riêng của PDFium.

Đây là **business configuration của PDF conversion**.

Domain không cần biết:

```python
import pypdfium2
```

Đó là điểm quan trọng.

---

# 5. PdfDocumentSession

File:

```text
infrastructure/pdfium/document.py
```

```python
from pathlib import Path

import pypdfium2 as pdfium


class PdfDocumentSession:

    def __init__(
        self,
        pdf_path: str | Path,
    ) -> None:

        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"PDF không tồn tại: {self.pdf_path}"
            )

        if not self.pdf_path.is_file():
            raise ValueError(
                f"Không phải file: {self.pdf_path}"
            )

        self._pdf = None

    def open(self) -> None:

        if self._pdf is not None:
            raise RuntimeError(
                "Document đã được mở"
            )

        self._pdf = pdfium.PdfDocument(
            self.pdf_path
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

    @property
    def page_count(self) -> int:

        if self._pdf is None:
            raise RuntimeError(
                "Document chưa được mở"
            )

        return len(self._pdf)

    def get_page(self, page_index: int):

        if self._pdf is None:
            raise RuntimeError(
                "Document chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                f"Page index không hợp lệ: "
                f"{page_index}"
            )

        return self._pdf[page_index]

    def close(self) -> None:

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None
```

---

# 6. Renderer

File:

```text
infrastructure/pdfium/renderer.py
```

```python
from PIL import Image

from domain.models import ConvertOptions


class PdfRenderer:

    def render_page(
        self,
        page,
        options: ConvertOptions,
    ) -> Image.Image:

        bitmap = page.render(
            scale=options.scale
        )

        image = bitmap.to_pil()

        return image.copy()
```

Renderer chỉ biết:

```text
PdfPage
   ↓
PdfBitmap
   ↓
PIL.Image
```

Không biết:

```text
output/
PNG
JPEG filename
CLI
```

---

# 7. Exporter

File:

```text
infrastructure/pdfium/exporter.py
```

Thực tế exporter dùng Pillow nên về architecture có thể đặt riêng dưới `infrastructure/image/`; nhưng mini project này giữ đơn giản.

```python
from pathlib import Path

from PIL import Image

from domain.models import ImageFormat


class ImageExporter:

    def save(
        self,
        image: Image.Image,
        output_path: str | Path,
        image_format: ImageFormat,
        quality: int = 90,
    ) -> None:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if image_format == ImageFormat.PNG:

            image.save(
                output_path,
                format="PNG",
            )

            return

        if image_format == ImageFormat.JPEG:

            rgb_image = image

            if image.mode != "RGB":
                rgb_image = image.convert("RGB")

            try:
                rgb_image.save(
                    output_path,
                    format="JPEG",
                    quality=quality,
                )
            finally:
                if rgb_image is not image:
                    rgb_image.close()

            return

        raise ValueError(
            f"Format không hỗ trợ: {image_format}"
        )
```

---

# 8. Application Service

Đây là phần quan trọng nhất.

File:

```text
application/convert_pdf.py
```

```python
from pathlib import Path
from typing import Callable

from domain.models import ConvertOptions
from infrastructure.pdfium.document import (
    PdfDocumentSession,
)
from infrastructure.pdfium.renderer import (
    PdfRenderer,
)
from infrastructure.pdfium.exporter import (
    ImageExporter,
)


ProgressCallback = Callable[[int, int], None]


class PdfConverter:

    def __init__(
        self,
        renderer: PdfRenderer,
        exporter: ImageExporter,
    ) -> None:

        self.renderer = renderer
        self.exporter = exporter

    def convert(
        self,
        pdf_path: str | Path,
        output_dir: str | Path,
        options: ConvertOptions,
        progress_callback: ProgressCallback | None = None,
    ) -> int:

        output_dir = Path(output_dir)

        with PdfDocumentSession(pdf_path) as document:

            page_count = document.page_count

            start_page = options.start_page

            end_page = (
                options.end_page
                if options.end_page is not None
                else page_count
            )

            if start_page >= page_count:
                raise ValueError(
                    f"start_page={start_page} "
                    f"vượt quá PDF "
                    f"({page_count} trang)"
                )

            if end_page > page_count:
                raise ValueError(
                    f"end_page={end_page} "
                    f"vượt quá PDF "
                    f"({page_count} trang)"
                )

            total = end_page - start_page

            processed = 0

            for page_index in range(
                start_page,
                end_page,
            ):

                page = document.get_page(
                    page_index
                )

                image = self.renderer.render_page(
                    page,
                    options,
                )

                try:

                    page_number = page_index + 1

                    extension = (
                        "png"
                        if options.image_format.value == "png"
                        else "jpg"
                    )

                    output_path = (
                        output_dir
                        / f"page-{page_number:03d}.{extension}"
                    )

                    self.exporter.save(
                        image=image,
                        output_path=output_path,
                        image_format=options.image_format,
                        quality=options.quality,
                    )

                finally:

                    image.close()

                processed += 1

                if progress_callback:
                    progress_callback(
                        processed,
                        total,
                    )

        return processed
```

---

# 9. Chú ý `start_page` và `end_page`

Ví dụ:

```text
start_page = 9
end_page = 20
```

sẽ xử lý:

```text
PDF index:
9
10
11
...
19
```

tương ứng với trang người dùng nhìn thấy:

```text
10
11
12
...
20
```

Kết quả:

```text
page-010.png
page-011.png
...
page-020.png
```

Đây là lý do chúng ta dùng:

```python
range(
    start_page,
    end_page,
)
```

---

# 10. Progress callback

Application không nên phụ thuộc vào `print()`.

Ta dùng:

```python
ProgressCallback = Callable[
    [int, int],
    None,
]
```

Ví dụ CLI:

```python
def show_progress(
    current: int,
    total: int,
) -> None:

    percent = current / total * 100

    print(
        f"[{current}/{total}] "
        f"{percent:6.2f}%"
    )
```

Nhưng GUI sau này cũng có thể dùng:

```python
def update_progress(
    current: int,
    total: int,
):
    progress_bar.setValue(
        int(current / total * 100)
    )
```

Application không cần biết nó là:

```text
CLI
PySide6
Flet
Web
```

Đây là Dependency Inversion rất hữu ích.

---

# 11. CLI

File:

```text
presentation/cli.py
```

```python
import argparse
from pathlib import Path

from application.convert_pdf import PdfConverter
from domain.models import (
    ConvertOptions,
    ImageFormat,
)
from infrastructure.pdfium.renderer import (
    PdfRenderer,
)
from infrastructure.pdfium.exporter import (
    ImageExporter,
)


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Convert PDF pages to PNG/JPEG images."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Đường dẫn tới file PDF",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Thư mục output",
    )

    parser.add_argument(
        "--dpi",
        type=float,
        default=150,
        help="DPI, mặc định 150",
    )

    parser.add_argument(
        "--format",
        choices=["png", "jpeg"],
        default="png",
        help="Image format",
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=90,
        help="JPEG quality 1..100",
    )

    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Page index bắt đầu, mặc định 0",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help=(
            "Page index kết thúc "
            "(exclusive)"
        ),
    )

    return parser


def main() -> None:

    parser = build_parser()

    args = parser.parse_args()

    image_format = ImageFormat(
        args.format
    )

    options = ConvertOptions(
        dpi=args.dpi,
        image_format=image_format,
        quality=args.quality,
        start_page=args.start,
        end_page=args.end,
    )

    renderer = PdfRenderer()

    exporter = ImageExporter()

    converter = PdfConverter(
        renderer=renderer,
        exporter=exporter,
    )

    def progress(
        current: int,
        total: int,
    ) -> None:

        percent = (
            current / total * 100
        )

        print(
            f"[{current}/{total}] "
            f"{percent:6.2f}%"
        )

    try:

        count = converter.convert(
            pdf_path=args.input,
            output_dir=args.output,
            options=options,
            progress_callback=progress,
        )

    except Exception as exc:

        parser.error(str(exc))

    print(
        f"Hoàn thành: {count} trang"
    )
```

---

# 12. `__main__.py`

File:

```text
pdf_converter/__main__.py
```

```python
from presentation.cli import main


if __name__ == "__main__":
    main()
```

Nhưng để chạy:

```bash
python -m pdf_converter
```

thì các package phải nằm bên trong package root.

Cấu trúc đầy đủ:

```text
project/
│
├── pdf_converter/
│   ├── __init__.py
│   ├── __main__.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   └── convert_pdf.py
│   │
│   └── infrastructure/
│       ├── __init__.py
│       └── pdfium/
│           ├── __init__.py
│           ├── document.py
│           ├── renderer.py
│           └── exporter.py
│
└── presentation/
    ├── __init__.py
    └── cli.py
```

Tuy nhiên để tránh import phức tạp trong mini project, ta nên đưa `presentation` vào trong package:

```text
project/
│
├── pdf_converter/
│   ├── __init__.py
│   ├── __main__.py
│   │
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   │   └── pdfium/
│   │
│   └── presentation/
│       ├── __init__.py
│       └── cli.py
│
└── sample.pdf
```

Đây là cấu trúc tôi khuyến nghị.

---

# 13. Sửa import

Trong `application/convert_pdf.py`:

```python
from pdf_converter.domain.models import ConvertOptions
from pdf_converter.infrastructure.pdfium.document import (
    PdfDocumentSession,
)
from pdf_converter.infrastructure.pdfium.renderer import (
    PdfRenderer,
)
from pdf_converter.infrastructure.pdfium.exporter import (
    ImageExporter,
)
```

Trong `presentation/cli.py`:

```python
from pdf_converter.application.convert_pdf import (
    PdfConverter,
)

from pdf_converter.domain.models import (
    ConvertOptions,
    ImageFormat,
)

from pdf_converter.infrastructure.pdfium.renderer import (
    PdfRenderer,
)

from pdf_converter.infrastructure.pdfium.exporter import (
    ImageExporter,
)
```

Trong `__main__.py`:

```python
from pdf_converter.presentation.cli import main


if __name__ == "__main__":
    main()
```

---

# 14. Chạy chương trình

Từ thư mục:

```text
project/
```

chạy:

```bash
python -m pdf_converter sample.pdf output
```

Ví dụ:

```text
PDF có 20 trang

[1/20]   5.00%
[2/20]  10.00%
[3/20]  15.00%
...
[20/20] 100.00%

Hoàn thành: 20 trang
```

Output:

```text
output/
├── page-001.png
├── page-002.png
├── page-003.png
├── ...
└── page-020.png
```

---

# 15. JPEG

```bash
python -m pdf_converter sample.pdf output \
    --format jpeg \
    --quality 85
```

Windows CMD có thể viết một dòng:

```bash
python -m pdf_converter sample.pdf output --format jpeg --quality 85
```

---

# 16. 300 DPI

```bash
python -m pdf_converter sample.pdf output --dpi 300
```

Scale được tính:

```python
scale = dpi / 72
```

nên:

```text
150 DPI
    ↓
scale ≈ 2.0833
```

và:

```text
300 DPI
    ↓
scale ≈ 4.1667
```

300 DPI sẽ tạo ảnh lớn hơn rất nhiều.

---

# 17. Render một phần PDF

Giả sử PDF có 100 trang.

Chạy:

```bash
python -m pdf_converter sample.pdf output --start 9 --end 20
```

Sẽ xử lý:

```text
PDF index 9  → page-010
PDF index 10 → page-011
...
PDF index 19 → page-020
```

Tổng:

```text
11 pages
```

vì:

```python
len(range(9, 20))
```

là:

```text
11
```

---

# 18. Có một vấn đề UX

Người dùng thường nghĩ:

```text
--start 10 --end 20
```

nghĩa là:

```text
trang 10 → trang 20
```

Trong khi API của chúng ta:

```text
start = page index
end = exclusive
```

nghĩa là:

```text
--start 10
```

thực tế là **trang 11**.

Đây là vấn đề API rất đáng lưu ý.

Với CLI production, tốt hơn nên để CLI nhận **page number 1-based**:

```bash
--start-page 10
--end-page 20
```

sau đó CLI chuyển sang index nội bộ:

```python
start_index = start_page - 1
end_index = end_page
```

Như vậy:

```bash
--start-page 10 --end-page 20
```

thật sự có nghĩa:

```text
Trang 10 → trang 20
```

---

# 19. Cải thiện CLI

Thay:

```python
--start
--end
```

bằng:

```python
--start-page
--end-page
```

```python
parser.add_argument(
    "--start-page",
    type=int,
    default=1,
    help="Trang bắt đầu, tính từ 1",
)

parser.add_argument(
    "--end-page",
    type=int,
    default=None,
    help="Trang kết thúc, tính từ 1",
)
```

Sau đó:

```python
start_index = args.start_page - 1

if args.end_page is None:
    end_index = None
else:
    end_index = args.end_page
```

Domain vẫn dùng:

```text
0-based index
```

CLI dùng:

```text
1-based page number
```

Đây là cách thiết kế tốt hơn.

---

# 20. Error handling

Các lỗi có thể xảy ra:

```text
PDF không tồn tại
PDF không hợp lệ
DPI <= 0
quality ngoài 1..100
start page sai
end page sai
output không ghi được
PDF bị lỗi
```

Ví dụ:

```bash
python -m pdf_converter abc.pdf output
```

sẽ báo:

```text
error: PDF không tồn tại: abc.pdf
```

---

# 21. Một điểm architecture rất quan trọng

CLI:

```text
presentation
```

không trực tiếp gọi:

```python
pypdfium2.PdfDocument(...)
```

Thay vào đó:

```text
CLI
 ↓
PdfConverter
 ↓
PdfDocumentSession
 ↓
pypdfium2
```

Điều này cho phép sau này thay CLI bằng GUI:

```text
PySide6
   ↓
PdfConverter
```

hoặc:

```text
Flet
   ↓
PdfConverter
```

hoặc:

```text
FastAPI
   ↓
PdfConverter
```

Application không cần thay đổi.

---

# 22. Test Domain

Tạo:

```text
tests/
├── test_options.py
├── test_exporter.py
└── test_converter.py
```

## `test_options.py`

```python
import pytest

from pdf_converter.domain.models import (
    ConvertOptions,
    ImageFormat,
)


def test_default_options():

    options = ConvertOptions()

    assert options.dpi == 150
    assert options.image_format == ImageFormat.PNG
    assert options.quality == 90
    assert options.start_page == 0
    assert options.end_page is None


def test_scale():

    options = ConvertOptions(
        dpi=144
    )

    assert options.scale == 2.0


def test_invalid_dpi():

    with pytest.raises(ValueError):

        ConvertOptions(
            dpi=0
        )


def test_invalid_quality():

    with pytest.raises(ValueError):

        ConvertOptions(
            quality=101
        )
```

Chạy:

```bash
pytest
```

---

# 23. Test Exporter

```python
from PIL import Image

from pdf_converter.domain.models import (
    ImageFormat,
)

from pdf_converter.infrastructure.pdfium.exporter import (
    ImageExporter,
)


def test_save_png(tmp_path):

    image = Image.new(
        "RGB",
        (100, 100),
    )

    exporter = ImageExporter()

    output = tmp_path / "test.png"

    exporter.save(
        image,
        output,
        ImageFormat.PNG,
    )

    assert output.exists()

    image.close()
```

JPEG:

```python
def test_save_jpeg(tmp_path):

    image = Image.new(
        "RGBA",
        (100, 100),
    )

    exporter = ImageExporter()

    output = tmp_path / "test.jpg"

    exporter.save(
        image,
        output,
        ImageFormat.JPEG,
        quality=85,
    )

    assert output.exists()

    image.close()
```

Điểm quan trọng:

> Test exporter **không cần PDF thật**.

---

# 24. Dependency Injection

Chúng ta đã vô tình áp dụng DI:

```python
class PdfConverter:

    def __init__(
        self,
        renderer,
        exporter,
    ):
        self.renderer = renderer
        self.exporter = exporter
```

CLI tạo:

```python
renderer = PdfRenderer()
exporter = ImageExporter()
```

rồi inject:

```python
converter = PdfConverter(
    renderer=renderer,
    exporter=exporter,
)
```

Sau này test có thể inject fake:

```python
fake_renderer
fake_exporter
```

mà không cần PDFium.

Đây chính là những gì bạn đã học trong SOLID/DDD đang được áp dụng vào một project thật.

---

# 25. Pipeline hoàn chỉnh

Toàn bộ Mini Project:

```text
                    CLI
                     │
                     ▼
              argparse
                     │
                     ▼
              ConvertOptions
                     │
                     ▼
              PdfConverter
                     │
                     ▼
          PdfDocumentSession
                     │
                     ▼
                PdfPage
                     │
                     ▼
               PdfRenderer
                     │
                     ▼
                PdfBitmap
                     │
                     ▼
                PIL.Image
                     │
                     ▼
               ImageExporter
                  /       \
                 /         \
               PNG        JPEG
```

Resource lifecycle:

```text
open PDF
   │
   ├── page 1
   │    ├── render
   │    ├── save
   │    └── release image
   │
   ├── page 2
   │    ├── render
   │    ├── save
   │    └── release image
   │
   ├── ...
   │
   └── page N
        ├── render
        ├── save
        └── release image
   │
   ▼
close PDF
```

---

# 26. Những gì bạn vừa thực sự học

Mini Project này không chỉ là:

> "PDF → Image"

Mà chúng ta đã luyện lại rất nhiều kiến thức architecture:

### Separation of Concerns

```text
Document
Renderer
Exporter
CLI
```

### Dependency Injection

```text
PdfConverter(
    renderer,
    exporter,
)
```

### Resource Management

```text
with PdfDocumentSession(...)
```

### Streaming Processing

```text
one page
    ↓
process
    ↓
release
    ↓
next page
```

### Domain Configuration

```text
ConvertOptions
```

### Enum

```text
ImageFormat.PNG
ImageFormat.JPEG
```

### Callback

```text
ProgressCallback
```

### CLI

```text
argparse
```

Đây chính là kiểu architecture có thể mở rộng tiếp.

---

# 27. Checklist Phần I

Sau Buổi 10, Phần I hoàn thành:

| Buổi | Nội dung                      | Trạng thái |
| ---- | ----------------------------- | ---------- |
| 1    | Cài đặt & kiến trúc pypdfium2 | ✅          |
| 2    | `PdfDocument`                 | ✅          |
| 3    | `PdfPage`                     | ✅          |
| 4    | Page count & metadata         | ✅          |
| 5    | Render → Bitmap               | ✅          |
| 6    | Bitmap → PIL                  | ✅          |
| 7    | DPI, scale, image size        | ✅          |
| 8    | PNG/JPEG                      | ✅          |
| 9    | Render toàn bộ PDF            | ✅          |
| 10   | PDF → Image Converter         | ✅          |

---

# 28. Phần II — Đọc và phân tích PDF

Sau Mini Project, chúng ta chuyển từ:

```text
PDF
 ↓
Image
```

sang nhánh cực kỳ quan trọng:

```text
PDF
 ↓
PdfPage
 ↓
TextPage
 ↓
Text
```

Roadmap tiếp theo:

```text
11. TextPage
12. Extract text
13. Text position / bounding box
14. Character-level extraction
15. Link / annotation
16. Page objects
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Và từ đây `pypdfium2` bắt đầu trở thành **PDF document processing engine**, chứ không còn đơn thuần là thư viện render PDF thành ảnh.
