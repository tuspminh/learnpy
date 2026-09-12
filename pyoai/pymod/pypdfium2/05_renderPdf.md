# Buổi 5 — Render PDF → PNG/JPEG với `pypdfium2`

Ở 4 buổi trước, chúng ta đã xây được nền tảng:

```text
PdfDocument
    ↓
PdfPage
    ↓
page.render()
    ↓
PdfBitmap
    ↓
bitmap.to_pil()
    ↓
PIL.Image
```

Hôm nay chúng ta biến nó thành một **PDF Image Exporter** có thể dùng thực tế:

```text
PDF
 │
 ▼
PdfDocument
 │
 ├── Page 1 ──► PNG
 ├── Page 2 ──► PNG
 ├── Page 3 ──► PNG
 └── ...
```

Mục tiêu cuối buổi:

```bash
python main.py sample.pdf output --dpi 150 --format png
```

và nhận:

```text
output/
├── page-001.png
├── page-002.png
├── page-003.png
└── ...
```

---

# 1. Render một page

Phần cốt lõi:

```python
bitmap = page.render(
    scale=dpi / 72
)

image = bitmap.to_pil()

image.save("page.png")
```

Pipeline:

```text
PdfPage
   │
   ▼
render()
   │
   ▼
PdfBitmap
   │
   ▼
to_pil()
   │
   ▼
PIL.Image
   │
   ▼
save()
```

---

# 2. Render với DPI

Ta đã biết:

```text
scale = DPI / 72
```

Do đó:

```python
def dpi_to_scale(dpi: int) -> float:
    return dpi / 72
```

Ví dụ:

```python
print(dpi_to_scale(72))
print(dpi_to_scale(150))
print(dpi_to_scale(300))
```

Kết quả:

```text
1.0
2.0833333333333335
4.166666666666667
```

---

# 3. Tạo `RenderOptions`

Không nên truyền hàng loạt tham số:

```python
render(
    page,
    150,
    90,
    False,
    ...
)
```

Ta dùng `dataclass`.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    dpi: int = 150

    @property
    def scale(self) -> float:
        if self.dpi <= 0:
            raise ValueError(
                "DPI must be greater than 0"
            )

        return self.dpi / 72
```

Sử dụng:

```python
options = RenderOptions(dpi=300)

print(options.dpi)
print(options.scale)
```

---

# 4. Render PNG

PNG phù hợp khi:

* cần chất lượng không mất dữ liệu
* tài liệu có text
* screenshot
* OCR
* lưu trữ
* cần alpha/transparency

Ví dụ:

```python
image.save(
    "page.png",
    format="PNG",
)
```

Hoặc đơn giản:

```python
image.save("page.png")
```

Pillow tự xác định format từ extension.

---

# 5. Render JPEG

JPEG phù hợp hơn khi:

* ảnh nhiều màu
* scan/photo
* cần giảm kích thước file
* không cần transparency

```python
image.save(
    "page.jpg",
    format="JPEG",
    quality=90,
)
```

Chất lượng:

```text
quality=100
```

rất cao.

```text
quality=90
```

thường khá tốt.

```text
quality=70
```

file nhỏ hơn nhưng bắt đầu mất chất lượng.

---

# 6. Một vấn đề với JPEG

JPEG không hỗ trợ alpha channel như PNG.

Nếu:

```python
image.mode == "RGBA"
```

thì:

```python
image.save("page.jpg")
```

có thể gây lỗi.

Ta nên chuyển:

```python
image = image.convert("RGB")
```

trước khi lưu JPEG.

Ví dụ:

```python
if image.mode != "RGB":
    image = image.convert("RGB")

image.save(
    "page.jpg",
    quality=90,
)
```

---

# 7. Render một page hoàn chỉnh

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_page(
    pdf_path: str | Path,
    page_index: int,
    output_path: str | Path,
    dpi: int = 150,
) -> None:

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        page = pdf[page_index]

        scale = dpi / 72

        bitmap = page.render(
            scale=scale
        )

        image = bitmap.to_pil()

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(output_path)

    finally:
        pdf.close()
```

---

# 8. Render toàn bộ PDF

Bây giờ thay vì:

```python
page = pdf[0]
```

chúng ta duyệt:

```python
for page_index in range(len(pdf)):
    page = pdf[page_index]
```

Ví dụ:

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_all_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 150,
) -> None:

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        scale = dpi / 72

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            bitmap = page.render(
                scale=scale
            )

            image = bitmap.to_pil()

            output_path = (
                output_dir
                / f"page-{page_index + 1:03d}.png"
            )

            image.save(output_path)

            print(
                f"Saved: {output_path}"
            )

    finally:
        pdf.close()
```

---

# 9. Tại sao `{page_index + 1:03d}`?

Đây:

```python
f"page-{page_index + 1:03d}.png"
```

cho:

```text
page-001.png
page-002.png
page-003.png
...
page-010.png
page-011.png
```

thay vì:

```text
page-1.png
page-2.png
page-10.png
```

Điều này rất hữu ích khi sort file.

Ví dụ:

```text
page-001
page-002
page-010
page-100
```

sẽ có thứ tự đúng.

---

# 10. Render chỉ một range page

Thực tế thường không muốn render toàn bộ PDF.

Ví dụ:

```text
PDF có 500 trang
```

nhưng chỉ muốn:

```text
trang 100 → 120
```

Ta có:

```python
def render_pages(
    pdf_path,
    output_dir,
    start_page,
    end_page,
    dpi=150,
):
    ...
```

Chú ý quy ước:

```text
start_page = inclusive
end_page   = exclusive
```

giống Python `range()`.

Ví dụ:

```python
range(100, 120)
```

là:

```text
100
101
...
119
```

---

# 11. Render range hoàn chỉnh

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    start_page: int,
    end_page: int,
    dpi: int = 150,
) -> None:

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        total_pages = len(pdf)

        if start_page < 0:
            raise ValueError(
                "start_page must be >= 0"
            )

        if end_page > total_pages:
            raise ValueError(
                "end_page exceeds PDF page count"
            )

        if start_page >= end_page:
            raise ValueError(
                "start_page must be less than end_page"
            )

        output_dir = Path(output_dir)
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        scale = dpi / 72

        for page_index in range(
            start_page,
            end_page,
        ):
            page = pdf[page_index]

            bitmap = page.render(
                scale=scale
            )

            image = bitmap.to_pil()

            output_path = (
                output_dir
                / f"page-{page_index + 1:03d}.png"
            )

            image.save(output_path)

            print(
                f"Saved page {page_index + 1}"
            )

    finally:
        pdf.close()
```

---

# 12. Rotation

Khi render PDF, rotation là một vấn đề quan trọng.

Ví dụ:

```text
Page geometry
     +
Rotation
     ↓
Rendered image
```

Một document có thể chứa page xoay:

```text
0°
90°
180°
270°
```

Trong ứng dụng PDF viewer hoặc image exporter, bạn cần xác định rõ:

> Tôi muốn giữ rotation của PDF hay áp dụng rotation tùy chỉnh?

Đây là lý do chúng ta sẽ không trộn rotation vào logic `dpi_to_scale()`.

Hai khái niệm:

```text
DPI
 ↓
resolution

Rotation
 ↓
orientation
```

là độc lập.

---

# 13. Thiết kế `RenderOptions` tốt hơn

Ta có thể mở rộng:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    dpi: int = 150
    rotation: int = 0

    @property
    def scale(self) -> float:
        if self.dpi <= 0:
            raise ValueError(
                "DPI must be greater than 0"
            )

        return self.dpi / 72

    def validate(self) -> None:
        if self.rotation not in {
            0,
            90,
            180,
            270,
        }:
            raise ValueError(
                "Rotation must be "
                "0, 90, 180 or 270"
            )
```

Tuy nhiên, **đừng vội nhét tất cả tính năng vào renderer**.

Đây là nguyên tắc SOLID:

```text
RenderOptions
    ↓
configuration

PdfRenderer
    ↓
rendering

ImageExporter
    ↓
saving
```

Mỗi class một responsibility.

---

# 14. `PdfRenderer` và `PdfImageExporter`

Đây là kiến trúc tôi muốn bạn bắt đầu hình thành.

```text
PdfRenderer
    ↓
PdfBitmap / PIL.Image

PdfImageExporter
    ↓
save image
```

Không nên:

```text
PdfRenderer
    ↓
render
    ↓
PNG
    ↓
JPEG
    ↓
filename
    ↓
directory
```

vì renderer sẽ biết quá nhiều thứ.

---

# 15. `PdfRenderer`

```python
import pypdfium2 as pdfium


class PdfRenderer:

    def render(
        self,
        page,
        options,
    ):
        return page.render(
            scale=options.scale
        )

    def render_to_pil(
        self,
        page,
        options,
    ):
        bitmap = self.render(
            page,
            options,
        )

        return bitmap.to_pil()
```

Nhiệm vụ:

```text
PdfPage
   ↓
render
   ↓
PIL Image
```

---

# 16. `PdfImageExporter`

```python
from pathlib import Path


class PdfImageExporter:

    def save(
        self,
        image,
        output_path: str | Path,
    ) -> None:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(output_path)
```

Nhiệm vụ:

```text
PIL.Image
   ↓
file
```

Không cần biết PDFium là gì.

Đây chính là **Single Responsibility Principle**.

---

# 17. JPEG exporter

Có thể thêm:

```python
class PdfImageExporter:

    def save_png(
        self,
        image,
        output_path,
    ):
        image.save(
            output_path,
            format="PNG",
        )

    def save_jpeg(
        self,
        image,
        output_path,
        quality=90,
    ):
        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            output_path,
            format="JPEG",
            quality=quality,
        )
```

Nhưng sau này tôi muốn chúng ta đi xa hơn bằng **Strategy Pattern**, thay vì `if/elif` ngày càng dài.

---

# 18. Tạo `ImageFormat`

Ta có thể dùng `Enum`:

```python
from enum import Enum


class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
```

Sau đó:

```python
class ExportOptions:
    ...
```

Nhưng ở Buổi 5 chúng ta chưa cần over-engineering.

Trước mắt hiểu rõ:

```text
rendering
≠
exporting
```

là quan trọng nhất.

---

# 19. CLI đơn giản

Bây giờ xây chương trình:

```bash
python main.py sample.pdf output
```

`main.py`:

```python
import sys
from pathlib import Path

import pypdfium2 as pdfium


def render_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 150,
) -> None:

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        scale = dpi / 72

        for index in range(len(pdf)):

            page = pdf[index]

            bitmap = page.render(
                scale=scale
            )

            image = bitmap.to_pil()

            output_path = (
                output_dir
                / f"page-{index + 1:03d}.png"
            )

            image.save(output_path)

            print(
                f"[OK] {output_path}"
            )

    finally:
        pdf.close()


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: "
            "python main.py PDF OUTPUT_DIR"
        )
        return

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]

    render_pdf(
        pdf_path,
        output_dir,
    )


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py sample.pdf output
```

---

# 20. Tách CLI khỏi application

Nhưng architecture tốt hơn là:

```text
CLI
 │
 ▼
Application
 │
 ▼
PdfRenderer
 │
 ▼
pypdfium2
```

Không nên để:

```text
CLI
 │
 └── pypdfium2.PdfDocument(...)
```

vì sau này nếu chuyển sang:

```text
PySide6
Flet
FastAPI
background worker
```

chúng ta sẽ phải copy logic.

---

# 21. Project structure

Từ bây giờ có thể tổ chức:

```text
pdf_processor/
│
├── domain/
│
├── application/
│   └── render_pdf.py
│
├── infrastructure/
│   └── pdfium/
│       ├── document_loader.py
│       └── renderer.py
│
├── presentation/
│   └── cli/
│       └── main.py
│
└── tests/
```

Luồng:

```text
CLI
 ↓
RenderPdfUseCase
 ↓
PdfRenderer
 ↓
pypdfium2
```

Đây là hướng chúng ta sẽ phát triển ở các buổi sau.

---

# 22. Memory trong render toàn bộ PDF

Code:

```python
for index in range(len(pdf)):
    page = pdf[index]

    bitmap = page.render(
        scale=2
    )

    image = bitmap.to_pil()

    image.save(...)

```

tốt hơn:

```python
images = []

for index in range(len(pdf)):
    page = pdf[index]

    bitmap = page.render(
        scale=2
    )

    image = bitmap.to_pil()

    images.append(image)
```

Vì phiên bản thứ hai giữ tất cả image.

Pipeline đúng:

```text
Page
 ↓
Bitmap
 ↓
PIL
 ↓
Save
 ↓
next page
```

thay vì:

```text
Page
 ↓
Bitmap
 ↓
PIL
 ↓
LIST
 ↓
LIST
 ↓
LIST
 ↓
...
```

---

# 23. PNG hay JPEG?

Một quy tắc thực tế:

### Tài liệu text

```text
PDF
 ↓
PNG
```

thường là lựa chọn tốt.

### Scan/photo

```text
PDF
 ↓
JPEG
```

có thể tiết kiệm dung lượng đáng kể.

### OCR

Thông thường:

```text
PDF
 ↓
render 300 DPI
 ↓
grayscale
 ↓
PNG
 ↓
OCR
```

là một pipeline rất hợp lý.

---

# 24. So sánh DPI

Giả sử page A4.

### 72 DPI

```text
≈ 595 × 842
```

Phù hợp:

```text
thumbnail
preview
```

### 150 DPI

```text
≈ 1240 × 1754
```

Phù hợp:

```text
screen
reading
preview chất lượng cao
```

### 300 DPI

```text
≈ 2480 × 3508
```

Phù hợp:

```text
OCR
document processing
printing
```

### 600 DPI

```text
≈ 4961 × 7016
```

Rất nặng.

Không nên sử dụng mặc định.

---

# 25. Mini Project — `PdfImageExporter`

Bây giờ hãy xây phiên bản hoàn chỉnh:

```text
pdf_image_exporter/
│
├── main.py
├── renderer.py
├── exporter.py
├── options.py
└── sample.pdf
```

### `options.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    dpi: int = 150

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError(
                "DPI must be greater than 0"
            )

    @property
    def scale(self) -> float:
        return self.dpi / 72
```

### `renderer.py`

```python
import pypdfium2 as pdfium

from options import RenderOptions


class PdfRenderer:

    def render_to_pil(
        self,
        page,
        options: RenderOptions,
    ):
        bitmap = page.render(
            scale=options.scale
        )

        return bitmap.to_pil()
```

### `exporter.py`

```python
from pathlib import Path


class PdfImageExporter:

    def save_png(
        self,
        image,
        path: str | Path,
    ) -> None:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            path,
            format="PNG",
        )

    def save_jpeg(
        self,
        image,
        path: str | Path,
        quality: int = 90,
    ) -> None:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            path,
            format="JPEG",
            quality=quality,
        )
```

### `main.py`

```python
from pathlib import Path

import pypdfium2 as pdfium

from exporter import PdfImageExporter
from options import RenderOptions
from renderer import PdfRenderer


def export_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 150,
) -> None:

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    options = RenderOptions(
        dpi=dpi
    )

    renderer = PdfRenderer()
    exporter = PdfImageExporter()

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        for index in range(len(pdf)):

            page = pdf[index]

            image = renderer.render_to_pil(
                page,
                options,
            )

            output_path = (
                output_dir
                / f"page-{index + 1:03d}.png"
            )

            exporter.save_png(
                image,
                output_path,
            )

            print(
                f"[OK] "
                f"{index + 1}/{len(pdf)} "
                f"{output_path}"
            )

    finally:
        pdf.close()


def main():
    export_pdf(
        "sample.pdf",
        "output",
        dpi=150,
    )


if __name__ == "__main__":
    main()
```

---

# 26. Kết quả

Chạy:

```bash
python main.py
```

Ta có:

```text
output/
├── page-001.png
├── page-002.png
├── page-003.png
├── page-004.png
└── ...
```

Và architecture:

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
        PdfRenderer
              │
              ▼
          PIL.Image
              │
              ▼
      PdfImageExporter
              │
        ┌─────┴─────┐
        ▼           ▼
       PNG         JPEG
```

Đây là architecture tốt hơn rất nhiều so với việc viết một hàm 100 dòng xử lý tất cả.

---

# 27. Bài tập Buổi 5

### Bài 1

Render PDF ở:

```text
72 DPI
150 DPI
300 DPI
```

và so sánh:

```text
width
height
file size
```

---

### Bài 2

Thêm:

```python
format="jpeg"
```

và cho phép:

```text
quality=70
quality=80
quality=90
quality=100
```

So sánh kích thước file.

---

### Bài 3

Cho phép chọn:

```text
all pages
page range
single page
```

Ví dụ:

```text
--page 5
--start 10 --end 20
```

---

### Bài 4 — quan trọng

Viết:

```python
class PdfImageExporter:
    ...
```

nhưng **không để class này biết `pypdfium2`**.

Nó chỉ nhận:

```python
PIL.Image
```

và lưu file.

Đây là bài tập để kiểm tra bạn đã hiểu **Separation of Concerns** hay chưa.

---

# Kiến thức cần nhớ

Buổi 5 có 4 tầng:

```text
1. PDF
     ↓
2. PdfPage
     ↓
3. PdfRenderer
     ↓
4. PIL.Image
     ↓
5. ImageExporter
     ↓
PNG / JPEG
```

Và nguyên tắc:

```text
Renderer
    → render

Exporter
    → save

RenderOptions
    → configuration
```

Không trộn tất cả vào một class.

**Buổi 6** chúng ta sẽ đi sâu vào **text extraction với `PdfTextPage`**: lấy text từ PDF, `get_text_range()`, text length, Unicode, page → text và bắt đầu xây `PdfTextExtractor`. Đây là nhánh thứ hai của kiến trúc:

```text
                 PdfPage
                /       \
               /         \
          Rendering      Text
             ↓             ↓
         Bitmap        TextPage
             ↓             ↓
           Image         Text
```

Từ đó `pypdfium2` không chỉ dùng để **PDF → Image**, mà còn có thể trở thành một phần của **PDF document processing engine**.
