# Buổi 9 — Render toàn bộ PDF

Theo đúng roadmap:

> **Buổi 9. Render toàn bộ PDF**

Ở Buổi 8 chúng ta đã biết render **một trang** và xuất PNG/JPEG.

Hôm nay chuyển từ:

```text
PDF
 ↓
1 page
 ↓
Image
 ↓
File
```

sang:

```text
PDF
 ↓
N pages
 ↓
page 1 → render → save → release
page 2 → render → save → release
page 3 → render → save → release
...
page N → render → save → release
```

Mục tiêu quan trọng nhất:

> **Mở PDF một lần và xử lý từng trang tuần tự, không giữ toàn bộ ảnh trong RAM.**

---

# 1. Thiết kế sai mà người mới thường viết

Ví dụ:

```python
images = []

for page_index in range(len(pdf)):
    page = pdf[page_index]
    bitmap = page.render(scale=2)
    image = bitmap.to_pil()

    images.append(image)
```

Sau đó mới:

```python
for index, image in enumerate(images):
    image.save(...)
```

Vấn đề:

```text
PDF 100 trang
       ↓
100 Bitmap/Image
       ↓
RAM tăng rất lớn
```

Với PDF 500 trang thì càng nguy hiểm.

---

# 2. Thiết kế đúng

Ta xử lý từng trang:

```text
page 1
  ↓
render
  ↓
PIL
  ↓
save
  ↓
release

page 2
  ↓
render
  ↓
PIL
  ↓
save
  ↓
release
```

Memory gần với:

```text
RAM ≈ 1 page
```

thay vì:

```text
RAM ≈ toàn bộ PDF
```

---

# 3. Vấn đề khác: mở PDF bao nhiêu lần?

Ở Buổi 8, nếu có:

```python
renderer.render_page(
    "sample.pdf",
    page_index=0,
    options=options,
)
```

rồi:

```python
renderer.render_page(
    "sample.pdf",
    page_index=1,
    options=options,
)
```

và bên trong `render_page()`:

```python
pdf = pdfium.PdfDocument(pdf_path)
```

thì ta đang:

```text
open PDF
render page 1
close PDF

open PDF
render page 2
close PDF

open PDF
render page 3
close PDF
```

Không tốt khi xử lý nhiều trang.

Ta muốn:

```text
open PDF
   │
   ├── page 1
   ├── page 2
   ├── page 3
   ├── ...
   └── page N
   │
close PDF
```

Đây là thay đổi kiến trúc quan trọng của Buổi 9.

---

# 4. Kiến trúc mới

Ta có:

```text
PdfDocument
     │
     ▼
PdfDocumentSession
     │
     ├── render page 1
     ├── render page 2
     ├── render page 3
     └── ...
```

Session chịu trách nhiệm vòng đời của PDF:

```text
open
  ↓
use
  ↓
close
```

---

# 5. Tạo `PdfDocumentSession`

File:

```text
pdf_document.py
```

Code:

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

        self._pdf = None

    def open(self) -> None:

        if self._pdf is not None:
            raise RuntimeError(
                "PDF document đã được mở"
            )

        self._pdf = pdfium.PdfDocument(
            self.pdf_path
        )

    @property
    def page_count(self) -> int:

        if self._pdf is None:
            raise RuntimeError(
                "PDF document chưa được mở"
            )

        return len(self._pdf)

    def get_page(self, page_index: int):

        if self._pdf is None:
            raise RuntimeError(
                "PDF document chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                f"page_index={page_index} "
                f"không hợp lệ"
            )

        return self._pdf[page_index]

    def close(self) -> None:

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None
```

---

# 6. Nhưng `open()` / `close()` thủ công dễ quên

Không nên:

```python
session.open()

# code...

session.close()
```

vì nếu có exception:

```python
session.open()

do_something()

session.close()
```

`do_something()` lỗi thì:

```text
close()
```

có thể không chạy.

Ta cần Context Manager.

---

# 7. Context Manager

Thêm:

```python
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

Full class:

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

        self._pdf = None

    def open(self) -> None:

        if self._pdf is not None:
            raise RuntimeError(
                "PDF document đã được mở"
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
                "PDF document chưa được mở"
            )

        return len(self._pdf)

    def get_page(self, page_index: int):

        if self._pdf is None:
            raise RuntimeError(
                "PDF document chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                f"page_index={page_index} "
                f"không hợp lệ"
            )

        return self._pdf[page_index]

    def close(self) -> None:

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None
```

Bây giờ:

```python
with PdfDocumentSession("sample.pdf") as document:

    print(document.page_count)

    page = document.get_page(0)
```

Khi ra khỏi `with`:

```text
__exit__()
    ↓
close()
```

được gọi.

---

# 8. Renderer bây giờ nhận `PdfPage`

Ở Buổi 8:

```python
renderer.render_page(
    pdf_path,
    page_index,
    options,
)
```

Bây giờ ta tách rõ hơn:

```python
renderer.render_page(
    page,
    options,
)
```

Renderer không cần biết document nằm ở đâu.

```python
from PIL import Image


class PdfRenderer:

    def render_page(
        self,
        page,
        options,
    ) -> Image.Image:

        bitmap = page.render(
            scale=options.scale
        )

        image = bitmap.to_pil()

        return image.copy()
```

Rất sạch:

```text
PdfDocumentSession
        ↓
     PdfPage
        ↓
   PdfRenderer
        ↓
    PIL.Image
```

---

# 9. Tại sao đây là thiết kế tốt hơn?

`PdfDocumentSession`:

```text
quản lý document lifecycle
```

`PdfRenderer`:

```text
quản lý rendering
```

`PdfImageExporter`:

```text
quản lý output image
```

Ba responsibility:

```text
┌─────────────────────────┐
│ PdfDocumentSession      │
│ open / close / page     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ PdfRenderer              │
│ PdfPage → PIL.Image      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ PdfImageExporter         │
│ PIL → PNG/JPEG           │
└─────────────────────────┘
```

---

# 10. Render toàn bộ PDF

Bây giờ phần chính.

```python
from pathlib import Path

from options import RenderOptions
from pdf_document import PdfDocumentSession
from renderer import PdfRenderer
from exporter import PdfImageExporter


def export_pdf_to_png(
    pdf_path: str | Path,
    output_dir: str | Path,
    options: RenderOptions,
) -> None:

    output_dir = Path(output_dir)

    renderer = PdfRenderer()
    exporter = PdfImageExporter()

    with PdfDocumentSession(pdf_path) as document:

        page_count = document.page_count

        print(
            f"PDF có {page_count} trang"
        )

        for page_index in range(page_count):

            print(
                f"Rendering "
                f"{page_index + 1}/{page_count}"
            )

            page = document.get_page(
                page_index
            )

            image = renderer.render_page(
                page,
                options,
            )

            try:

                output_path = (
                    output_dir
                    / f"page-{page_index + 1:03d}.png"
                )

                exporter.save_png(
                    image,
                    output_path,
                )

            finally:

                image.close()
```

Đây chính là pipeline chúng ta muốn.

---

# 11. Luồng thực thi

Ví dụ PDF có 5 trang:

```text
PdfDocumentSession
       │
       │ open()
       ▼
   PdfDocument
       │
       ├── Page 0
       │     ↓
       │   render
       │     ↓
       │   PIL
       │     ↓
       │   save page-001
       │     ↓
       │   close image
       │
       ├── Page 1
       │     ↓
       │   render
       │     ↓
       │   save page-002
       │
       ├── Page 2
       │
       ├── Page 3
       │
       └── Page 4
             ↓
        close document
```

Tại bất kỳ thời điểm nào chúng ta chỉ giữ image hiện tại.

---

# 12. JPEG cũng tương tự

Ta có thể viết:

```python
def export_pdf_to_jpeg(
    pdf_path: str | Path,
    output_dir: str | Path,
    options: RenderOptions,
    quality: int = 90,
) -> None:

    output_dir = Path(output_dir)

    renderer = PdfRenderer()
    exporter = PdfImageExporter()

    with PdfDocumentSession(pdf_path) as document:

        page_count = document.page_count

        for page_index in range(page_count):

            page = document.get_page(
                page_index
            )

            image = renderer.render_page(
                page,
                options,
            )

            try:

                output_path = (
                    output_dir
                    / f"page-{page_index + 1:03d}.jpg"
                )

                exporter.save_jpeg(
                    image,
                    output_path,
                    quality=quality,
                )

            finally:

                image.close()
```

---

# 13. Tránh duplicate code

Hai hàm:

```python
export_pdf_to_png()
export_pdf_to_jpeg()
```

gần như giống nhau.

Điểm khác duy nhất:

```text
PNG
JPEG
```

Ta có thể tạo:

```python
export_pdf(
    ...
    image_format=...
)
```

---

# 14. Dùng Enum

```python
from enum import Enum


class ImageFormat(str, Enum):

    PNG = "png"
    JPEG = "jpeg"
```

Sau đó:

```python
def export_pdf(
    pdf_path,
    output_dir,
    options,
    image_format: ImageFormat,
    quality: int = 90,
):
    ...
```

---

# 15. Full `export_pdf()`

```python
from pathlib import Path
from enum import Enum

from options import RenderOptions
from pdf_document import PdfDocumentSession
from renderer import PdfRenderer
from exporter import PdfImageExporter


class ImageFormat(str, Enum):

    PNG = "png"
    JPEG = "jpeg"


def export_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    options: RenderOptions,
    image_format: ImageFormat,
    quality: int = 90,
) -> None:

    output_dir = Path(output_dir)

    renderer = PdfRenderer()
    exporter = PdfImageExporter()

    with PdfDocumentSession(pdf_path) as document:

        page_count = document.page_count

        for page_index in range(page_count):

            print(
                f"[{page_index + 1}/{page_count}] "
                f"Rendering..."
            )

            page = document.get_page(
                page_index
            )

            image = renderer.render_page(
                page,
                options,
            )

            try:

                page_number = page_index + 1

                if image_format == ImageFormat.PNG:

                    output_path = (
                        output_dir
                        / f"page-{page_number:03d}.png"
                    )

                    exporter.save_png(
                        image,
                        output_path,
                    )

                elif image_format == ImageFormat.JPEG:

                    output_path = (
                        output_dir
                        / f"page-{page_number:03d}.jpg"
                    )

                    exporter.save_jpeg(
                        image,
                        output_path,
                        quality=quality,
                    )

                else:

                    raise ValueError(
                        f"Format không hỗ trợ: "
                        f"{image_format}"
                    )

            finally:

                image.close()

            print(
                f"Saved: {output_path}"
            )
```

---

# 16. Sử dụng

PNG:

```python
export_pdf(
    pdf_path="sample.pdf",
    output_dir="output/png",
    options=RenderOptions(dpi=150),
    image_format=ImageFormat.PNG,
)
```

JPEG:

```python
export_pdf(
    pdf_path="sample.pdf",
    output_dir="output/jpeg",
    options=RenderOptions(dpi=150),
    image_format=ImageFormat.JPEG,
    quality=85,
)
```

Kết quả:

```text
output/
├── png/
│   ├── page-001.png
│   ├── page-002.png
│   ├── page-003.png
│   └── ...
│
└── jpeg/
    ├── page-001.jpg
    ├── page-002.jpg
    ├── page-003.jpg
    └── ...
```

---

# 17. Full project

Đến đây project có thể tổ chức:

```text
pdf_image_export/
│
├── main.py
│
├── options.py
│
├── pdf_document.py
│
├── renderer.py
│
└── exporter.py
```

---

## `options.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "dpi phải > 0"
            )

    @property
    def scale(self) -> float:

        return self.dpi / 72.0
```

---

## `pdf_document.py`

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

        self._pdf = None

    def open(self) -> None:

        if self._pdf is not None:
            raise RuntimeError(
                "PDF document đã được mở"
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
                "PDF document chưa được mở"
            )

        return len(self._pdf)

    def get_page(self, page_index: int):

        if self._pdf is None:
            raise RuntimeError(
                "PDF document chưa được mở"
            )

        if not 0 <= page_index < len(self._pdf):
            raise IndexError(
                f"page_index={page_index} "
                f"không hợp lệ"
            )

        return self._pdf[page_index]

    def close(self) -> None:

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None
```

---

## `renderer.py`

```python
from PIL import Image


class PdfRenderer:

    def render_page(
        self,
        page,
        options,
    ) -> Image.Image:

        bitmap = page.render(
            scale=options.scale
        )

        image = bitmap.to_pil()

        return image.copy()
```

---

## `exporter.py`

```python
from pathlib import Path

from PIL import Image


class PdfImageExporter:

    def save_png(
        self,
        image: Image.Image,
        output_path: str | Path,
    ) -> None:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            output_path,
            format="PNG",
        )

    def save_jpeg(
        self,
        image: Image.Image,
        output_path: str | Path,
        quality: int = 90,
    ) -> None:

        if not 1 <= quality <= 100:
            raise ValueError(
                "quality phải nằm trong 1..100"
            )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
```

---

# 18. `main.py`

```python
from enum import Enum
from pathlib import Path

from options import RenderOptions
from pdf_document import PdfDocumentSession
from renderer import PdfRenderer
from exporter import PdfImageExporter


class ImageFormat(str, Enum):

    PNG = "png"
    JPEG = "jpeg"


def export_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    options: RenderOptions,
    image_format: ImageFormat,
    quality: int = 90,
) -> None:

    output_dir = Path(output_dir)

    renderer = PdfRenderer()
    exporter = PdfImageExporter()

    with PdfDocumentSession(pdf_path) as document:

        page_count = document.page_count

        print(
            f"PDF: {pdf_path}"
        )

        print(
            f"Pages: {page_count}"
        )

        print(
            f"DPI: {options.dpi}"
        )

        print(
            f"Scale: {options.scale:.4f}"
        )

        for page_index in range(page_count):

            page_number = page_index + 1

            print(
                f"[{page_number}/{page_count}] "
                f"Rendering..."
            )

            page = document.get_page(
                page_index
            )

            image = renderer.render_page(
                page,
                options,
            )

            try:

                if image_format == ImageFormat.PNG:

                    output_path = (
                        output_dir
                        / f"page-{page_number:03d}.png"
                    )

                    exporter.save_png(
                        image,
                        output_path,
                    )

                elif image_format == ImageFormat.JPEG:

                    output_path = (
                        output_dir
                        / f"page-{page_number:03d}.jpg"
                    )

                    exporter.save_jpeg(
                        image,
                        output_path,
                        quality=quality,
                    )

                else:

                    raise ValueError(
                        f"Format không hỗ trợ: "
                        f"{image_format}"
                    )

            finally:

                image.close()

            print(
                f"        Saved: {output_path}"
            )


def main():

    export_pdf(
        pdf_path="sample.pdf",
        output_dir="output",
        options=RenderOptions(
            dpi=150
        ),
        image_format=ImageFormat.PNG,
    )


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

---

# 19. Luồng resource management

Đây là phần tôi muốn bạn đặc biệt ghi nhớ.

Khi xử lý một PDF lớn:

```text
PdfDocument
     │
     │ sống trong toàn bộ session
     │
     ├── Page 1
     │     ↓
     │   Bitmap
     │     ↓
     │   PIL
     │     ↓
     │   save
     │     ↓
     │   close
     │
     ├── Page 2
     │     ↓
     │   Bitmap
     │     ↓
     │   PIL
     │     ↓
     │   save
     │     ↓
     │   close
     │
     └── Page N
           ↓
         close
```

Ta có **hai lifecycle khác nhau**:

### Document lifecycle

```text
open PDF
   ↓
process all pages
   ↓
close PDF
```

### Image lifecycle

```text
render page
   ↓
process
   ↓
save
   ↓
close image
```

Đây là cách suy nghĩ rất quan trọng khi làm resource-heavy application.

---

# 20. Không nên đóng `PdfPage` ngay lập tức

Một điểm nữa:

```python
page = document.get_page(index)
```

`page` thuộc document.

Ta không cần thiết kế:

```python
page.close()
```

sau mỗi lần lấy page nếu API/version hiện tại của pypdfium2 không yêu cầu như vậy cho flow này.

Lifecycle chính mà ta kiểm soát ở đây là:

```text
PdfDocument
Bitmap
PIL Image
```

Đặc biệt:

```text
PdfDocument → close()
PIL.Image → close()
```

---

# 21. Progress

Với PDF 1.000 trang:

```text
Rendering...
Rendering...
Rendering...
```

không đủ tốt.

Ta nên hiển thị:

```text
[1/1000]
[2/1000]
[3/1000]
```

hoặc:

```text
1%
2%
3%
```

Công thức:

```python
progress = (
    page_number / page_count
) * 100
```

Ví dụ:

```python
progress = (
    page_number / page_count
) * 100

print(
    f"[{page_number}/{page_count}] "
    f"{progress:.1f}%"
)
```

---

# 22. Đo thời gian từng trang

Đây sẽ chuẩn bị cho phần Performance sau này.

```python
from time import perf_counter
```

Trong loop:

```python
start = perf_counter()

image = renderer.render_page(
    page,
    options,
)

elapsed = perf_counter() - start

print(
    f"Render time: {elapsed:.3f}s"
)
```

Ta có thể biết:

```text
[1/100] 0.12s
[2/100] 0.10s
[3/100] 0.11s
...
```

Sau này có thể tính:

```text
pages/second
average render time
total render time
```

---

# 23. Một cải tiến rất quan trọng: callback

Nếu đây là thư viện:

```text
pdf_processing_engine
```

thì không nên để renderer tự:

```python
print(...)
```

Application layer có thể nhận progress.

Ví dụ:

```python
from collections.abc import Callable


ProgressCallback = Callable[
    [int, int],
    None,
]
```

Ý nghĩa:

```text
current_page
total_pages
```

Ví dụ:

```python
def progress(
    current: int,
    total: int,
):
    print(
        f"{current}/{total}"
    )
```

Sau đó:

```python
export_pdf(
    ...,
    progress_callback=progress,
)
```

Đây sẽ rất hữu ích khi sau này chúng ta đưa engine vào:

```text
PySide6
Flet
CLI
Web API
```

GUI có thể nhận:

```text
current=37
total=100
```

và cập nhật:

```text
████████░░░░░░ 37%
```

---

# 24. Tại sao điều này liên quan tới project crawler của bạn?

Mô hình này rất giống crawler.

Crawler:

```text
Document
   ↓
Chapter 1
   ↓
process
   ↓
save
   ↓
release
```

PDF:

```text
Document
   ↓
Page 1
   ↓
render
   ↓
save
   ↓
release
```

Cả hai đều có pattern:

```text
Open Resource
      ↓
Iterate
      ↓
Process Item
      ↓
Persist Result
      ↓
Release Item
      ↓
Next Item
      ↓
Close Resource
```

Đây chính là tư duy architecture rất quan trọng cho các hệ thống processing pipeline.

---

# 25. Bài tập Buổi 9

## Bài 1 — Cơ bản

Render toàn bộ PDF:

```text
sample.pdf
```

thành:

```text
output/
├── page-001.png
├── page-002.png
├── ...
```

ở:

```text
150 DPI
```

---

## Bài 2 — JPEG

Render toàn bộ PDF thành:

```text
output-jpeg/
├── page-001.jpg
├── page-002.jpg
└── ...
```

với:

```text
quality=85
```

---

## Bài 3 — Page range

Chỉ render:

```text
page 10 → page 20
```

Yêu cầu:

```text
10 inclusive
20 exclusive
```

Kết quả:

```text
page-011.png
...
page-020.png
```

Chú ý:

```text
page index 9  → page number 10
page index 19 → page number 20
```

---

## Bài 4 — Đo performance

Ghi:

```text
page
render time
image size
file size
```

Ví dụ:

```text
Page 1
  render: 0.120s
  image: 1240×1755
  file: 1.82 MB
```

---

## Bài 5 — Quan trọng nhất

Chứng minh rằng code của bạn **không giữ toàn bộ images trong RAM**.

Không được:

```python
images = []
```

Không được:

```python
images.append(image)
```

Phải là:

```python
image = renderer.render_page(...)

try:
    exporter.save_png(...)
finally:
    image.close()
```

---

# 26. Checklist kiến thức

Sau Buổi 9, bạn cần hiểu rõ:

* [x] Mở `PdfDocument` một lần.
* [x] Lấy từng `PdfPage`.
* [x] Render từng page.
* [x] `PdfBitmap → PIL.Image`.
* [x] Save image.
* [x] Release image.
* [x] Tiếp tục page kế tiếp.
* [x] Cuối cùng đóng `PdfDocument`.
* [x] Dùng Context Manager cho document lifecycle.
* [x] Không giữ toàn bộ image trong RAM.
* [x] `Renderer` không chịu trách nhiệm lưu file.
* [x] `Exporter` không phụ thuộc PDFium.
* [x] Có thể xuất PNG hoặc JPEG.
* [x] Có thể theo dõi progress.

---

# 27. Kiến trúc sau Buổi 9

Chúng ta đã có một pipeline khá hoàn chỉnh:

```text
                    Application
                         │
                         ▼
                  PDF Processing
                         │
                         ▼
              PdfDocumentSession
                         │
                    PdfDocument
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
          PdfPage                 page_count
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
      PdfImageExporter
          │       │
          ▼       ▼
         PNG     JPEG
```

Và resource lifecycle:

```text
Document
   │
   ├── Page 1 → Image → Save → Release
   ├── Page 2 → Image → Save → Release
   ├── Page 3 → Image → Save → Release
   ├── ...
   └── Page N → Image → Save → Release
   │
   ▼
 Close Document
```

Đây là nền tảng rất quan trọng trước khi chúng ta bước sang **Buổi 10 — Mini Project: PDF → Image Converter**.

Ở Buổi 10, chúng ta sẽ **đóng gói toàn bộ những gì đã học từ Buổi 1–9 thành một CLI converter hoàn chỉnh**, có `argparse`, input/output, DPI, format PNG/JPEG, quality, page range, progress và cấu trúc project sạch.
