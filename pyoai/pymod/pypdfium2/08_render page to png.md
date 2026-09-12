# Buổi 8 — Render từng trang thành PNG/JPEG

Theo đúng roadmap:

> **Buổi 8. Render từng trang thành PNG/JPEG**

Ở Buổi 7 chúng ta đã hiểu:

```text
PDF points
    ↓
DPI
    ↓
scale
    ↓
pixel
    ↓
memory
```

Bây giờ chúng ta xây thành một thành phần thực tế:

```text
PdfDocument
     ↓
   PdfPage
     ↓
 PdfRenderer
     ↓
 PIL.Image
     ↓
 PdfImageExporter
     ├── PNG
     └── JPEG
```

Mục tiêu quan trọng của buổi này là **tách rendering khỏi việc lưu file**.

---

# 1. Bài toán

Ta muốn chạy:

```bash
python main.py sample.pdf output/
```

và nhận:

```text
output/
├── page-001.png
├── page-002.png
├── page-003.png
└── ...
```

Hoặc JPEG:

```text
output/
├── page-001.jpg
├── page-002.jpg
├── page-003.jpg
└── ...
```

Với các tùy chọn:

```text
DPI
format
JPEG quality
page range
output directory
```

---

# 2. Kiến trúc

Không nên viết một class kiểu:

```python
class PdfToImage:
    def render_and_save(...):
        ...
```

vì class đó làm quá nhiều việc.

Ta tách:

```text
┌──────────────────────┐
│     PdfRenderer      │
│                      │
│ PDF → PIL.Image      │
└──────────┬───────────┘
           │
           ▼
      PIL.Image
           │
           ▼
┌──────────────────────┐
│   PdfImageExporter   │
│                      │
│ PIL → PNG/JPEG       │
└──────────────────────┘
```

Đây là Separation of Concerns.

---

# 3. `RenderOptions`

Ta tiếp tục sử dụng cấu hình từ Buổi 7.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("dpi phải > 0")

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Ví dụ:

```python
options = RenderOptions(dpi=300)

print(options.dpi)
print(options.scale)
```

Kết quả:

```text
300
4.166666666666667
```

---

# 4. `PdfRenderer`

Renderer chỉ có nhiệm vụ:

> PDF page → PIL Image

Nó **không biết PNG hay JPEG**.

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


class PdfRenderer:

    def render_page(
        self,
        pdf_path: str | Path,
        page_index: int,
        options: RenderOptions,
    ) -> Image.Image:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF không tồn tại: {pdf_path}"
            )

        pdf = pdfium.PdfDocument(pdf_path)

        try:
            page_count = len(pdf)

            if not 0 <= page_index < page_count:
                raise IndexError(
                    f"page_index={page_index} không hợp lệ. "
                    f"PDF có {page_count} trang."
                )

            page = pdf[page_index]

            bitmap = page.render(
                scale=options.scale
            )

            image = bitmap.to_pil()

            return image.copy()

        finally:
            pdf.close()
```

Điểm quan trọng:

```python
return image.copy()
```

để kết quả PIL độc lập hơn với resource PDFium.

---

# 5. `PdfImageExporter`

Bây giờ tạo class khác.

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
                "JPEG quality phải nằm trong 1..100"
            )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            output_path,
            format="JPEG",
            quality=quality,
        )
```

Nhìn vào đây:

```text
PdfRenderer
```

không biết:

```text
PNG
JPEG
quality
output directory
```

Còn:

```text
PdfImageExporter
```

không biết:

```text
PdfDocument
PdfPage
PdfBitmap
PDFium
```

Đây chính là điều chúng ta muốn.

---

# 6. Tạo file project

Tạm thời project:

```text
pdf_image_export/
│
├── options.py
├── renderer.py
├── exporter.py
└── main.py
```

---

# 7. `options.py`

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

# 8. `renderer.py`

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

from options import RenderOptions


class PdfRenderer:

    def render_page(
        self,
        pdf_path: str | Path,
        page_index: int,
        options: RenderOptions,
    ) -> Image.Image:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF không tồn tại: {pdf_path}"
            )

        pdf = pdfium.PdfDocument(pdf_path)

        try:
            page_count = len(pdf)

            if not 0 <= page_index < page_count:
                raise IndexError(
                    f"page_index={page_index} không hợp lệ. "
                    f"PDF có {page_count} trang."
                )

            page = pdf[page_index]

            bitmap = page.render(
                scale=options.scale
            )

            image = bitmap.to_pil()

            return image.copy()

        finally:
            pdf.close()
```

---

# 9. `exporter.py`

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
                "JPEG quality phải nằm trong 1..100"
            )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            output_path,
            format="JPEG",
            quality=quality,
        )
```

---

# 10. `main.py`

```python
from pathlib import Path

from options import RenderOptions
from renderer import PdfRenderer
from exporter import PdfImageExporter


def main() -> None:

    pdf_path = Path("sample.pdf")

    output_dir = Path("output")

    options = RenderOptions(
        dpi=150
    )

    renderer = PdfRenderer()

    exporter = PdfImageExporter()

    image = renderer.render_page(
        pdf_path=pdf_path,
        page_index=0,
        options=options,
    )

    try:

        png_path = output_dir / "page-001.png"

        exporter.save_png(
            image=image,
            output_path=png_path,
        )

        print(
            f"PNG saved: {png_path}"
        )

        jpg_path = output_dir / "page-001.jpg"

        exporter.save_jpeg(
            image=image,
            output_path=jpg_path,
            quality=90,
        )

        print(
            f"JPEG saved: {jpg_path}"
        )

    finally:
        image.close()


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

Kết quả:

```text
output/
├── page-001.png
└── page-001.jpg
```

---

# 11. Tại sao `image.close()`?

Pillow image là resource có thể giữ memory.

Sau khi:

```python
image.save(...)
```

không còn sử dụng:

```python
image
```

thì có thể:

```python
image.close()
```

Đặc biệt quan trọng khi xử lý hàng trăm/hàng nghìn trang.

Pattern:

```text
render
   ↓
process
   ↓
save
   ↓
close
   ↓
next page
```

thay vì:

```text
render page 1
render page 2
render page 3
...
render page 100
       ↓
giữ tất cả trong RAM
```

---

# 12. Render từng trang

Bây giờ nâng cấp.

Ta muốn:

```python
for page_index in range(...):
    image = renderer.render_page(...)
    exporter.save_png(...)
    image.close()
```

Code:

```python
from pathlib import Path

from options import RenderOptions
from renderer import PdfRenderer
from exporter import PdfImageExporter


def export_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    options: RenderOptions,
) -> None:

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(pdf_path)

    try:

        renderer = PdfRenderer()
        exporter = PdfImageExporter()

        for page_index in range(len(pdf)):

            print(
                f"Rendering page "
                f"{page_index + 1}/{len(pdf)}..."
            )

            page = pdf[page_index]

            bitmap = page.render(
                scale=options.scale
            )

            image = bitmap.to_pil().copy()

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

    finally:

        pdf.close()
```

Nhưng ở đây có một vấn đề architecture:

```text
export_pages()
```

lại trực tiếp đụng:

```python
pdfium.PdfDocument
```

Trong khi ta đã có `PdfRenderer`.

Ta nên cải thiện.

---

# 13. Render từng page bằng Renderer

Ta có thể viết:

```python
class PdfRenderer:

    def render_page(
        self,
        pdf_path,
        page_index,
        options,
    ):
        ...
```

Sau đó:

```python
for page_index in range(page_count):

    image = renderer.render_page(
        pdf_path,
        page_index,
        options,
    )

    try:
        exporter.save_png(
            image,
            output_path,
        )
    finally:
        image.close()
```

Nhưng mỗi lần gọi:

```python
render_page()
```

lại:

```text
open PDF
render
close PDF
```

Nếu PDF có 500 trang:

```text
open PDF
close PDF

open PDF
close PDF

open PDF
close PDF

...
```

Không tối ưu.

Đây là lý do **Buổi 9 — Render toàn bộ PDF** sẽ cần thiết kế tốt hơn.

---

# 14. Naming file

Ta dùng:

```python
f"page-{page_index + 1:03d}.png"
```

Giải thích:

```text
:03d
```

nghĩa là số nguyên có ít nhất 3 chữ số.

Kết quả:

```text
1   → 001
2   → 002
9   → 009
10  → 010
99  → 099
100 → 100
```

Vì vậy:

```text
page-001.png
page-002.png
page-003.png
...
page-010.png
...
page-100.png
```

Điều này rất quan trọng vì file explorer sẽ sort đúng thứ tự.

Nếu dùng:

```text
page-1.png
page-2.png
...
page-10.png
```

thì sorting alphabetic có thể thành:

```text
page-1.png
page-10.png
page-11.png
...
page-2.png
```

Không mong muốn.

---

# 15. PNG

PNG phù hợp với:

```text
PDF text
line art
diagram
screenshot
OCR
tài liệu
```

Code:

```python
image.save(
    "page.png",
    format="PNG",
)
```

PNG là lossless.

Tức:

```text
PIL image
   ↓
PNG
```

không cố tình loại bỏ thông tin hình ảnh bằng lossy compression như JPEG.

---

# 16. JPEG

JPEG phù hợp hơn với:

```text
photograph
scan có nhiều ảnh
tài liệu thiên về hình ảnh
```

Ví dụ:

```python
image.save(
    "page.jpg",
    format="JPEG",
    quality=90,
)
```

Quality:

```text
1
```

→ nén mạnh, chất lượng thấp.

```text
100
```

→ chất lượng cao, file thường lớn hơn.

Thực tế thường thử:

```text
70
80
85
90
95
```

thay vì luôn dùng 100.

---

# 17. So sánh JPEG quality

Ta có thể test:

```python
for quality in (50, 70, 80, 90, 95):
    output = f"page-q{quality}.jpg"

    image.convert("RGB").save(
        output,
        quality=quality,
    )
```

Sau đó:

```text
page-q50.jpg
page-q70.jpg
page-q80.jpg
page-q90.jpg
page-q95.jpg
```

Kiểm tra:

```text
file size
visual quality
text readability
```

Đây là một bài thực hành rất tốt.

---

# 18. Một lỗi phổ biến

Không nên làm:

```python
image.save(
    "page.jpg",
    format="JPEG",
)
```

nếu image đang:

```text
RGBA
```

An toàn hơn:

```python
if image.mode != "RGB":
    image = image.convert("RGB")
```

hoặc:

```python
rgb = image.convert("RGB")

try:
    rgb.save(...)
finally:
    rgb.close()
```

Trong exporter, chúng ta đã đóng gói việc này:

```python
def save_jpeg(...):
    if image.mode != "RGB":
        image = image.convert("RGB")
```

---

# 19. Thêm `save()`

Thay vì chỉ có:

```python
save_png()
save_jpeg()
```

ta có thể tạo API tổng quát:

```python
class PdfImageExporter:

    def save(
        self,
        image: Image.Image,
        output_path: str | Path,
        image_format: str,
        quality: int = 90,
    ) -> None:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image_format = image_format.lower()

        if image_format == "png":

            image.save(
                output_path,
                format="PNG",
            )

        elif image_format in {"jpg", "jpeg"}:

            if image.mode != "RGB":
                image = image.convert("RGB")

            image.save(
                output_path,
                format="JPEG",
                quality=quality,
            )

        else:

            raise ValueError(
                f"Format không hỗ trợ: {image_format}"
            )
```

Sử dụng:

```python
exporter.save(
    image,
    "page.png",
    "png",
)
```

hoặc:

```python
exporter.save(
    image,
    "page.jpg",
    "jpeg",
    quality=85,
)
```

---

# 20. Nhưng có nên dùng `str` cho format?

Có thể, nhưng tốt hơn nữa là dùng Enum.

```python
from enum import Enum


class ImageFormat(str, Enum):

    PNG = "png"
    JPEG = "jpeg"
```

Sau đó:

```python
class PdfImageExporter:

    def save(
        self,
        image,
        output_path,
        image_format: ImageFormat,
        quality: int = 90,
    ):
        ...
```

Sử dụng:

```python
exporter.save(
    image,
    "page.png",
    ImageFormat.PNG,
)
```

hoặc:

```python
exporter.save(
    image,
    "page.jpg",
    ImageFormat.JPEG,
    quality=90,
)
```

Nhưng ở giai đoạn hiện tại, chưa cần abstraction quá sâu. `save_png()` và `save_jpeg()` rất rõ ràng và dễ học.

---

# 21. Page range

Một yêu cầu thực tế:

> Chỉ render trang 10 → 20.

Ta thống nhất API:

```text
start_page = 10
end_page = 20
```

và:

```text
10 ≤ page < 20
```

tức `end_page` **exclusive**.

Ví dụ:

```python
for page_index in range(
    start_page,
    end_page,
):
    ...
```

sẽ render:

```text
10
11
12
...
19
```

Tổng cộng:

```text
10 pages
```

Đây là convention rất thuận tiện vì tương thích với Python `range()`.

---

# 22. Kiểm tra range

```python
def validate_page_range(
    page_count: int,
    start_page: int,
    end_page: int,
) -> None:

    if start_page < 0:
        raise ValueError(
            "start_page phải >= 0"
        )

    if end_page > page_count:
        raise ValueError(
            f"end_page={end_page} "
            f"vượt quá page_count={page_count}"
        )

    if start_page >= end_page:
        raise ValueError(
            "start_page phải < end_page"
        )
```

Ví dụ PDF:

```text
100 pages
```

thì:

```python
validate_page_range(
    100,
    10,
    20,
)
```

hợp lệ.

Nhưng:

```python
validate_page_range(
    100,
    80,
    120,
)
```

không hợp lệ.

---

# 23. Một vấn đề cần nhớ: PDF page index bắt đầu từ 0

API:

```python
pdf[0]
```

là trang 1 đối với người dùng.

Do đó:

```text
page_index = 0
display page = 1
```

và:

```text
filename = page-001.png
```

Công thức:

```python
display_page = page_index + 1
```

---

# 24. Mini implementation tốt hơn

Một exporter đơn giản nhưng thực dụng:

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


class PdfPageExporter:

    def export_png(
        self,
        pdf_path: str | Path,
        page_index: int,
        output_path: str | Path,
        dpi: float = 150,
    ) -> None:

        pdf_path = Path(pdf_path)
        output_path = Path(output_path)

        if dpi <= 0:
            raise ValueError(
                "dpi phải > 0"
            )

        pdf = pdfium.PdfDocument(pdf_path)

        try:

            if not 0 <= page_index < len(pdf):
                raise IndexError(
                    "page_index không hợp lệ"
                )

            page = pdf[page_index]

            bitmap = page.render(
                scale=dpi / 72.0
            )

            image = bitmap.to_pil()

            try:

                output_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                image.save(
                    output_path,
                    format="PNG",
                )

            finally:

                image.close()

        finally:

            pdf.close()
```

Nhưng hãy nhìn kỹ:

```text
PdfPageExporter
```

đang vừa:

```text
open PDF
render
convert PIL
save PNG
```

Nó vi phạm separation of concerns mà chúng ta vừa học.

**Đừng dùng thiết kế này làm architecture chính.**

Nó chỉ hữu ích để thấy sự khác nhau giữa:

```text
quick utility
```

và:

```text
production architecture
```

---

# 25. Architecture chúng ta muốn

Cuối cùng hướng tới:

```text
                    Application
                        │
                        ▼
                 RenderPdfPage
                        │
                        ▼
                  PdfRenderer
                        │
                        ▼
                   pypdfium2
                        │
                        ▼
                    PIL.Image
                        │
                        ▼
                PdfImageExporter
                   /          \
                  /            \
                PNG            JPEG
```

Trong đó:

### Renderer

```text
PDF → Image
```

### Exporter

```text
Image → File
```

Đây là hai responsibility khác nhau.

---

# 26. Test đơn giản

Ta nên bắt đầu test `PdfImageExporter` độc lập với PDFium.

Tạo một PIL image giả:

```python
from PIL import Image

from exporter import PdfImageExporter


def test_save_png(tmp_path):

    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    exporter = PdfImageExporter()

    output = tmp_path / "test.png"

    exporter.save_png(
        image,
        output,
    )

    assert output.exists()

    image.close()
```

Điểm hay:

```text
Không cần PDF.
Không cần pypdfium2.
```

Ta chỉ test:

```text
PIL.Image → PNG
```

Đây chính là lợi ích của việc tách exporter.

---

# 27. Test JPEG

```python
from PIL import Image

from exporter import PdfImageExporter


def test_save_jpeg(tmp_path):

    image = Image.new(
        "RGBA",
        (100, 100),
        "white",
    )

    exporter = PdfImageExporter()

    output = tmp_path / "test.jpg"

    exporter.save_jpeg(
        image,
        output,
        quality=90,
    )

    assert output.exists()

    image.close()
```

Test này còn kiểm tra gián tiếp việc:

```text
RGBA → RGB → JPEG
```

---

# 28. Bài tập thực hành

### Bài 1

Render trang đầu tiên:

```text
150 DPI
```

thành:

```text
page-001.png
page-001.jpg
```

---

### Bài 2

Render trang đầu tiên thành JPEG với:

```text
quality=50
quality=70
quality=80
quality=90
quality=95
```

So sánh:

```text
file size
quality
```

---

### Bài 3

Render trang:

```text
1
2
3
...
10
```

thành:

```text
page-001.png
page-002.png
...
page-010.png
```

---

### Bài 4

Viết:

```python
export_pages(
    pdf_path="sample.pdf",
    output_dir="output",
    start_page=0,
    end_page=10,
    dpi=150,
)
```

Yêu cầu:

```text
start_page inclusive
end_page exclusive
```

---

### Bài 5 — Quan trọng

Tách thành:

```text
options.py
renderer.py
exporter.py
main.py
```

với:

```text
Renderer
    ↓
PIL.Image
    ↓
Exporter
    ↓
PNG/JPEG
```

Đảm bảo:

> `PdfImageExporter` **không import `pypdfium2`**.

Đây là yêu cầu architecture quan trọng nhất của bài.

---

# 29. Tổng kết Buổi 8

Chúng ta đã xây được pipeline:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
PdfBitmap
 ↓
PIL.Image
 ↓
PdfImageExporter
 ├── PNG
 └── JPEG
```

Các kiến thức quan trọng:

```python
image.save("page.png")
```

```python
image.save(
    "page.jpg",
    quality=90,
)
```

```python
image.convert("RGB")
```

```python
f"page-{page_index + 1:03d}.png"
```

và:

```text
Renderer ≠ Exporter
```

Đây là nền tảng để sang **Buổi 9 — Render toàn bộ PDF**, nơi chúng ta sẽ xử lý đúng bài toán:

```text
PDF 500 trang
      ↓
mở PDF 1 lần
      ↓
page 1 → render → save → release
page 2 → render → save → release
page 3 → render → save → release
...
page 500 → render → save → release
      ↓
không giữ 500 ảnh trong RAM
```

Đồng thời chúng ta sẽ thiết kế `PdfDocumentSession`/renderer theo hướng **mở document một lần**, thay vì mỗi trang lại mở PDF một lần.
