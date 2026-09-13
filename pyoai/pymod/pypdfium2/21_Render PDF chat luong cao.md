# Phần III — PDF Rendering chuyên sâu

## Buổi 21 — Render PDF chất lượng cao

Từ Phần I, chúng ta đã biết:

```python
page.render(scale=2)
```

Nhưng khi xây dựng một **PDF rendering engine thực tế**, `scale` chỉ là điểm bắt đầu.

Ở Phần III chúng ta sẽ đi sâu vào pipeline:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ├── Page Size
 ├── MediaBox / CropBox
 ├── Rotation
 ├── Coordinate System
 │
 ▼
Render Configuration
 │
 ├── scale / DPI
 ├── grayscale
 ├── transparency
 ├── crop
 │
 ▼
PdfBitmap
 │
 ▼
PIL.Image
```

### Roadmap Phần III

| Buổi   | Nội dung                               |
| ------ | -------------------------------------- |
| **21** | Render chất lượng cao                  |
| 22     | Grayscale                              |
| 23     | Transparency                           |
| 24     | Rotation                               |
| 25     | CropBox / MediaBox                     |
| 26     | Page size                              |
| 27     | Coordinate system                      |
| 28     | Render region                          |
| 29     | Tối ưu memory khi render PDF lớn       |
| 30     | Mini Project — PDF Thumbnail Generator |

---

# 1. DPI và Scale

PDF không thực sự có "độ phân giải" giống ảnh.

Một trang PDF chủ yếu được mô tả bằng:

```text
vector
text
image
path
...
```

Khi render:

```text
PDF page
   ↓
Rasterization
   ↓
Bitmap
```

ta phải quyết định bitmap có bao nhiêu pixel.

Ví dụ một trang Letter:

```text
8.5 × 11 inch
```

Ở:

```text
72 DPI
```

thì khoảng:

```text
612 × 792 px
```

Ở:

```text
144 DPI
```

thì:

```text
1224 × 1584 px
```

Ở:

```text
300 DPI
```

thì:

```text
2550 × 3300 px
```

Do đó:

```text
DPI tăng
   ↓
pixel tăng
   ↓
chất lượng tăng
   ↓
memory tăng
   ↓
thời gian render tăng
```

---

# 2. `scale` trong pypdfium2

Cách cơ bản:

```python
bitmap = page.render(scale=2)
```

Có thể hiểu gần đúng:

```text
scale=1
    ↓
72 DPI

scale=2
    ↓
144 DPI

scale=4
    ↓
288 DPI
```

Công thức thường dùng:

```python
scale = dpi / 72
```

Ví dụ:

```python
def dpi_to_scale(dpi: float) -> float:
    return dpi / 72.0
```

Test:

```python
print(dpi_to_scale(72))
print(dpi_to_scale(144))
print(dpi_to_scale(300))
```

Kết quả:

```text
1.0
2.0
4.166666666666667
```

---

# 3. Xây dựng `RenderOptions`

Không nên để application code viết trực tiếp:

```python
page.render(scale=4)
```

Thay vào đó tạo configuration.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Sử dụng:

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

Điều này quan trọng vì sau này:

```text
RenderOptions
    │
    ├── dpi
    ├── grayscale
    ├── transparency
    ├── rotation
    ├── crop
    └── ...
```

sẽ trở thành configuration trung tâm của rendering subsystem.

---

# 4. Render ở nhiều DPI

Tạo một ví dụ hoàn chỉnh:

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_page(
    pdf_path: str | Path,
    page_index: int,
    dpi: float,
):
    pdf = pdfium.PdfDocument(pdf_path)

    try:
        page = pdf[page_index]

        scale = dpi / 72.0

        bitmap = page.render(
            scale=scale,
        )

        image = bitmap.to_pil()

        return image

    finally:
        pdf.close()
```

Sử dụng:

```python
image = render_page(
    "sample.pdf",
    page_index=0,
    dpi=300,
)

print(image.size)

image.save("page-300dpi.png")
```

---

# 5. Đừng mở PDF nhiều lần

Code sau **không tốt**:

```python
for page_index in range(100):
    image = render_page(
        "book.pdf",
        page_index,
        dpi=150,
    )
```

Bởi vì mỗi lần:

```text
PdfDocument()
    ↓
open PDF
    ↓
render
    ↓
close PDF
```

Ta đang mở/đóng PDF 100 lần.

Tốt hơn:

```text
PdfDocument
     │
     ├── Page 1
     ├── Page 2
     ├── Page 3
     ├── ...
     └── Page 100
```

---

# 6. `PdfRenderer`

Ta tạo abstraction:

```python
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0

    @property
    def scale(self) -> float:
        return self.dpi / 72.0


class PdfRenderer:
    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        self._pdf = None

    def open(self):
        self._pdf = pdfium.PdfDocument(self.pdf_path)

    def close(self):
        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):
        if self._pdf is None:
            raise RuntimeError("PDF chưa được mở")

        page = self._pdf[page_index]

        return page.render(
            scale=options.scale,
        )

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
```

Sử dụng:

```python
from pathlib import Path


options = RenderOptions(dpi=300)

with PdfRenderer("sample.pdf") as renderer:

    bitmap = renderer.render_page(
        page_index=0,
        options=options,
    )

    image = bitmap.to_pil()

    image.save(
        Path("page-1.png")
    )
```

---

# 7. Kiểm tra kích thước trang trước khi render

Đây là một thói quen rất quan trọng.

```python
with PdfRenderer("sample.pdf") as renderer:

    page = renderer._pdf[0]

    width, height = page.get_size()

    print("PDF size:")
    print(width, height)
```

`get_size()` trả kích thước page trong **PDF units**, không phải pixel.

Thông thường PDF sử dụng:

```text
1 point = 1/72 inch
```

Ví dụ:

```text
612 × 792
```

tương ứng khoảng:

```text
8.5 × 11 inch
```

---

# 8. Dự đoán kích thước bitmap

Nếu page có:

```text
PDF width  = 612
PDF height = 792
```

và:

```text
DPI = 300
```

thì:

```python
scale = 300 / 72
```

Pixel gần đúng:

```python
pixel_width = 612 * scale
pixel_height = 792 * scale
```

Tức:

```text
2550 × 3300
```

Đây là thông tin cực kỳ quan trọng khi render PDF lớn.

---

# 9. Memory tăng như thế nào?

Một bitmap RGBA 8-bit thường cần khoảng:

```text
width × height × 4 bytes
```

Với:

```text
2550 × 3300
```

ta có:

```text
2550 × 3300 × 4
≈ 33.7 MB
```

**chỉ một trang**.

Nếu render:

```text
100 pages
```

và giữ tất cả image:

```python
images = []

for page_index in range(100):
    images.append(...)
```

memory có thể tăng rất nhanh.

Vì vậy trong các bài sau chúng ta sẽ đặc biệt quan tâm tới:

```text
render
  ↓
process/save
  ↓
release
  ↓
next page
```

thay vì:

```text
render tất cả
  ↓
giữ tất cả trong RAM
```

---

# 10. Render quality không chỉ là DPI

Đây là điểm quan trọng của Buổi 21.

Một renderer production không nên chỉ có:

```python
dpi=300
```

Mà configuration sẽ dần phát triển thành:

```python
@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0
    grayscale: bool = False
    transparent: bool = False
    rotation: int = 0
    crop: tuple[float, float, float, float] | None = None

    @property
    def scale(self) -> float:
        return self.dpi / 72.0
```

Sau này:

```text
Buổi 21
    dpi
     │
Buổi 22
    grayscale
     │
Buổi 23
    transparency
     │
Buổi 24
    rotation
     │
Buổi 25
    MediaBox / CropBox
     │
Buổi 26
    page size
     │
Buổi 27
    coordinate system
     │
Buổi 28
    render region
```

Như vậy chúng ta xây dựng renderer **từng lớp**, không viết một cục code khổng lồ ngay từ đầu.

---

# 11. Validation

Không nên cho phép:

```python
RenderOptions(dpi=0)
```

hoặc:

```python
RenderOptions(dpi=-100)
```

Ta thêm validation:

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

Test:

```python
options = RenderOptions(dpi=300)

print(options.scale)
```

Sai:

```python
RenderOptions(dpi=0)
```

sẽ:

```text
ValueError: DPI phải > 0
```

---

# 12. Unit Test

```python
import pytest

from render import RenderOptions


def test_dpi_to_scale():
    options = RenderOptions(dpi=72)

    assert options.scale == 1.0


def test_300_dpi():
    options = RenderOptions(dpi=300)

    assert options.scale == pytest.approx(300 / 72)


def test_invalid_dpi():
    with pytest.raises(ValueError):
        RenderOptions(dpi=0)


def test_negative_dpi():
    with pytest.raises(ValueError):
        RenderOptions(dpi=-10)
```

Chạy:

```bash
pytest -v
```

---

# 13. Kiến trúc sau Buổi 21

Chúng ta đang chuyển từ:

```text
Application
    ↓
page.render()
```

sang:

```text
Presentation
      ↓
Application
      ↓
RenderOptions
      ↓
PdfRenderer
      ↓
PdfDocument
      ↓
PdfPage
      ↓
PDFium
      ↓
PdfBitmap
      ↓
PIL.Image
```

Trong đó:

### Domain

```text
RenderOptions
```

chứa **ý định render**.

### Infrastructure

```text
PdfRenderer
```

biết cách sử dụng:

```python
pypdfium2
```

### Application

quyết định:

```text
render page nào
render ở DPI bao nhiêu
lưu ở đâu
```

---

# 14. Một ví dụ hoàn chỉnh

```python
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150.0

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("DPI phải > 0")

    @property
    def scale(self) -> float:
        return self.dpi / 72.0


class PdfRenderer:
    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(self.pdf_path)

        self._pdf = None

    def open(self):
        self._pdf = pdfium.PdfDocument(self.pdf_path)

    def close(self):
        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    @property
    def page_count(self) -> int:
        if self._pdf is None:
            raise RuntimeError("PDF chưa được mở")

        return len(self._pdf)

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):
        if self._pdf is None:
            raise RuntimeError("PDF chưa được mở")

        if not 0 <= page_index < self.page_count:
            raise IndexError("Page index không hợp lệ")

        page = self._pdf[page_index]

        return page.render(
            scale=options.scale,
        )

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def main():

    options = RenderOptions(
        dpi=300,
    )

    with PdfRenderer("sample.pdf") as renderer:

        print("Pages:", renderer.page_count)

        bitmap = renderer.render_page(
            page_index=0,
            options=options,
        )

        image = bitmap.to_pil()

        print("Image size:", image.size)

        image.save(
            "page-1-300dpi.png"
        )


if __name__ == "__main__":
    main()
```

---

# 15. Bài tập Buổi 21

### Bài 1

Viết:

```python
dpi_to_scale(72)
dpi_to_scale(150)
dpi_to_scale(300)
dpi_to_scale(600)
```

---

### Bài 2

Viết:

```python
calculate_pixel_size(
    page_width=612,
    page_height=792,
    dpi=300,
)
```

Kết quả mong muốn gần:

```text
2550 × 3300
```

---

### Bài 3

Render cùng một page:

```text
72 DPI
150 DPI
300 DPI
600 DPI
```

và in:

```text
DPI
Image width
Image height
Memory estimate
```

---

### Bài 4 — quan trọng

Thử render PDF 100 trang nhưng **không được giữ tất cả image trong list**.

Mục tiêu:

```text
page 1
 ↓
render
 ↓
save
 ↓
release

page 2
 ↓
render
 ↓
save
 ↓
release
```

Đây sẽ là nền tảng cho **Buổi 29 — Memory Optimization**.

---

# Tổng kết Buổi 21

Hôm nay chúng ta chuyển từ tư duy:

```python
page.render(scale=2)
```

sang tư duy xây dựng **Rendering Subsystem**:

```text
RenderOptions
      │
      ├── DPI
      │
      └── Scale
            ↓
       PdfRenderer
            ↓
         PdfPage
            ↓
        PdfBitmap
            ↓
         PIL.Image
```

Điểm cần nhớ nhất:

> **DPI/scale quyết định kích thước bitmap; kích thước bitmap quyết định chất lượng, thời gian render và memory.**

Buổi 22 sẽ thêm **Grayscale**, đồng thời chúng ta sẽ bắt đầu thiết kế `RenderOptions` sao cho có thể mở rộng mà không phá vỡ kiến trúc hiện tại.
