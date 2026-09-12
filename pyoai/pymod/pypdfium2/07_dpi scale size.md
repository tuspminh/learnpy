# Buổi 7 — DPI, Scale và kích thước ảnh

Theo đúng roadmap:

> **Buổi 7. DPI, scale và kích thước ảnh**

Đây là buổi rất quan trọng vì từ đây chúng ta không chỉ biết:

```text
PDF → Bitmap → PIL
```

mà bắt đầu **kiểm soát chất lượng render và RAM**.

Mục tiêu cuối buổi:

```text
PDF page
   │
   ├── kích thước PDF: points
   │
   ├── DPI
   │
   ├── scale
   │
   └── kích thước bitmap: pixels
             │
             └── memory
```

---

# 1. Ba đơn vị phải phân biệt

Khi làm PDF rendering, bạn sẽ gặp 3 khái niệm:

```text
1. Point
2. DPI
3. Pixel
```

Đừng trộn chúng với nhau.

---

## 1.1. Point

PDF sử dụng đơn vị **point** để mô tả kích thước trang.

Quy ước:

```text
72 points = 1 inch
```

Ví dụ A4 xấp xỉ:

```text
595 × 842 points
```

Tức:

```text
595 / 72 ≈ 8.26 inch
842 / 72 ≈ 11.69 inch
```

Đúng với kích thước A4:

```text
210 × 297 mm
```

---

# 2. Pixel là gì?

Pixel là kích thước của ảnh raster sau khi render.

Ví dụ:

```text
PDF:

595 × 842 points
```

Render ở:

```text
72 DPI
```

thì:

```text
≈ 595 × 842 pixels
```

Render ở:

```text
144 DPI
```

thì:

```text
≈ 1190 × 1684 pixels
```

Render ở:

```text
300 DPI
```

thì:

```text
≈ 2480 × 3508 pixels
```

---

# 3. DPI là gì?

DPI:

```text
Dots Per Inch
```

Trong context rendering PDF, có thể hiểu đơn giản là:

> Có bao nhiêu pixel được tạo ra trên mỗi inch của trang PDF.

Công thức:

```text
pixels = inches × DPI
```

Mà:

```text
inches = points / 72
```

nên:

```text
pixels = points × DPI / 72
```

---

# 4. Công thức quan trọng nhất

Ta có:

```text
scale = DPI / 72
```

Do đó:

```text
pixel_width  = PDF_width  × scale
pixel_height = PDF_height × scale
```

Ví dụ:

```text
A4
595 × 842 points
```

ở:

```text
300 DPI
```

thì:

```text
scale = 300 / 72
      = 4.1667
```

Kích thước:

```text
595 × 4.1667 ≈ 2479
842 × 4.1667 ≈ 3508
```

Tức khoảng:

```text
2480 × 3508 pixels
```

---

# 5. `pypdfium2` dùng `scale`

Trong code chúng ta thường viết:

```python
bitmap = page.render(
    scale=2
)
```

Có thể hiểu:

```text
scale = 2
```

tương đương khoảng:

```text
144 DPI
```

Vì:

```text
DPI = scale × 72
```

Ví dụ:

|  Scale | DPI tương đương |
| -----: | --------------: |
|    0.5 |              36 |
|      1 |              72 |
|    1.5 |             108 |
|      2 |             144 |
|      3 |             216 |
|      4 |             288 |
| 4.1667 |             300 |
|      6 |             432 |

---

# 6. Tại sao `scale=4` rất nặng?

Điểm quan trọng:

```text
scale tăng 2 lần
```

không có nghĩa RAM chỉ tăng 2 lần.

Vì ảnh có:

```text
width × height
```

pixel.

Nếu scale tăng 2 lần:

```text
width × 2
height × 2
```

thì số pixel tăng:

```text
2 × 2 = 4 lần
```

Do đó:

```text
Memory ∝ scale²
```

Đây là kiến thức cực kỳ quan trọng khi xây PDF renderer.

---

# 7. Ví dụ A4

A4:

```text
595 × 842 points
```

### Scale 1

```text
595 × 842
```

Số pixel:

```text
595 × 842
= 500,990 pixels
```

---

### Scale 2

```text
1190 × 1684
```

Số pixel:

```text
1190 × 1684
= 2,008,? 
```

xấp xỉ:

```text
2 triệu pixels
```

---

### Scale 4

```text
2380 × 3368
```

xấp xỉ:

```text
8 triệu pixels
```

So với scale 1:

```text
8 / 0.5 ≈ 16 lần
```

---

# 8. Memory của bitmap

Giả sử ảnh:

```text
2480 × 3508
```

Số pixel:

```text
2480 × 3508
= 8,699,840
```

Nếu RGB:

```text
3 bytes / pixel
```

thì:

```text
8,699,840 × 3
= 26,099,520 bytes
```

khoảng:

```text
24.9 MiB
```

Nếu RGBA:

```text
4 bytes / pixel
```

thì:

```text
8,699,840 × 4
= 34,799,360 bytes
```

khoảng:

```text
33.2 MiB
```

Chỉ **một trang**.

---

# 9. PDF 100 trang thì sao?

Giả sử:

```text
A4
300 DPI
RGBA
≈ 33.2 MiB/page
```

Nếu bạn làm:

```python
images = []

for page in pdf:
    bitmap = page.render(scale=300 / 72)
    image = bitmap.to_pil()
    images.append(image)
```

thì về lý thuyết:

```text
33.2 MiB × 100
≈ 3.3 GiB
```

Đây là lý do **không nên render toàn bộ PDF rồi giữ tất cả ảnh trong RAM**.

Thay vào đó:

```text
render page
    ↓
process
    ↓
save
    ↓
release
    ↓
render page tiếp theo
```

---

# 10. Đây là pattern chúng ta sẽ dùng

Không nên:

```python
images = []

for page_index in range(len(pdf)):
    image = render(page_index)
    images.append(image)
```

Nên:

```python
for page_index in range(len(pdf)):
    image = render(page_index)

    image.save(...)

    image.close()
```

Tư duy:

```text
Memory ≈ memory của 1 page
```

thay vì:

```text
Memory ≈ memory của toàn bộ PDF
```

Đây sẽ cực kỳ quan trọng khi chúng ta tới:

> **Buổi 29 — Tối ưu memory khi render PDF lớn**

---

# 11. Tạo hàm DPI → Scale

Không nên viết rải rác:

```python
300 / 72
```

khắp project.

Tạo một hàm:

```python
def dpi_to_scale(dpi: float) -> float:
    if dpi <= 0:
        raise ValueError("DPI phải > 0")

    return dpi / 72.0
```

Sử dụng:

```python
scale = dpi_to_scale(300)

print(scale)
```

Output:

```text
4.166666666666667
```

---

# 12. Tạo hàm Scale → DPI

Chiều ngược lại:

```python
def scale_to_dpi(scale: float) -> float:
    if scale <= 0:
        raise ValueError("scale phải > 0")

    return scale * 72.0
```

Test:

```python
print(scale_to_dpi(1))
print(scale_to_dpi(2))
print(scale_to_dpi(4))
```

Output:

```text
72
144
288
```

---

# 13. Tạo `RenderOptions`

Trong project thực tế, tôi khuyên chúng ta không truyền `dpi` và `scale` lung tung.

Tạo configuration:

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

Sử dụng:

```python
options = RenderOptions(
    dpi=300
)

print(options.dpi)
print(options.scale)
```

Output:

```text
300
4.166666666666667
```

---

# 14. Tính kích thước pixel trước khi render

Đây là một kỹ thuật rất hữu ích.

Ta có thể biết ảnh sẽ lớn bao nhiêu **trước khi render**.

```python
from math import ceil


def calculate_pixel_size(
    width_points: float,
    height_points: float,
    dpi: float,
) -> tuple[int, int]:

    if dpi <= 0:
        raise ValueError("dpi phải > 0")

    scale = dpi / 72.0

    width = ceil(width_points * scale)
    height = ceil(height_points * scale)

    return width, height
```

Ví dụ:

```python
width, height = calculate_pixel_size(
    595,
    842,
    300,
)

print(width, height)
```

Kết quả gần:

```text
2479 3509
```

Con số chính xác có thể phụ thuộc cách làm tròn/render của PDFium.

---

# 15. Tính memory dự kiến

Ta có thể xây thêm:

```python
def estimate_memory(
    width: int,
    height: int,
    bytes_per_pixel: int,
) -> int:

    return width * height * bytes_per_pixel
```

Ví dụ:

```python
width = 2480
height = 3508

memory = estimate_memory(
    width,
    height,
    4,
)

print(memory)
```

Đổi sang MiB:

```python
mib = memory / (1024 ** 2)

print(f"{mib:.2f} MiB")
```

Output:

```text
33.20 MiB
```

---

# 16. Xây Render Calculator

Bây giờ ghép lại thành một utility nhỏ.

```python
from math import ceil


def dpi_to_scale(dpi: float) -> float:
    if dpi <= 0:
        raise ValueError("DPI phải > 0")

    return dpi / 72.0


def calculate_pixel_size(
    width_points: float,
    height_points: float,
    dpi: float,
) -> tuple[int, int]:

    scale = dpi_to_scale(dpi)

    width = ceil(width_points * scale)
    height = ceil(height_points * scale)

    return width, height


def estimate_memory_mib(
    width: int,
    height: int,
    bytes_per_pixel: int = 4,
) -> float:

    total_bytes = (
        width
        * height
        * bytes_per_pixel
    )

    return total_bytes / (1024 ** 2)


def main():

    width_points = 595
    height_points = 842

    for dpi in (72, 150, 300, 600):

        width, height = calculate_pixel_size(
            width_points,
            height_points,
            dpi,
        )

        memory = estimate_memory_mib(
            width,
            height,
        )

        print(
            f"DPI={dpi:3} | "
            f"size={width}x{height} | "
            f"memory≈{memory:.2f} MiB"
        )


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy xu hướng đại loại:

```text
DPI= 72 | size=595x842   | memory≈1.91 MiB
DPI=150 | size=1240x1755 | memory≈8.33 MiB
DPI=300 | size=2480x3509 | memory≈33.21 MiB
DPI=600 | size=4960x7017 | memory≈132.84 MiB
```

Điểm quan trọng nhất:

```text
150 → 300 DPI
```

DPI tăng:

```text
2 lần
```

nhưng memory tăng khoảng:

```text
4 lần
```

Còn:

```text
300 → 600 DPI
```

memory lại tăng:

```text
4 lần
```

---

# 17. DPI nào phù hợp?

Không có một DPI duy nhất phù hợp cho mọi trường hợp.

## Preview

```text
72–100 DPI
```

Phù hợp:

```text
thumbnail
preview
document browser
GUI
```

---

## Đọc trên màn hình

```text
120–150 DPI
```

thường là mức cân bằng tốt:

```text
quality
    ↕
memory
    ↕
speed
```

---

## OCR

Thông thường có thể bắt đầu thử:

```text
200–300 DPI
```

Đặc biệt đối với tài liệu scan.

Nhưng DPI tối ưu còn phụ thuộc:

```text
font size
scan quality
language
OCR engine
noise
layout
```

---

## In / chất lượng cao

Có thể cần:

```text
300 DPI
```

hoặc cao hơn.

Nhưng không nên mặc định:

```text
600 DPI
```

cho mọi PDF.

Nếu source PDF vốn chỉ chứa ảnh scan chất lượng thấp, tăng DPI render không thể tạo ra thông tin mới.

---

# 18. Một hiểu lầm rất quan trọng

Giả sử PDF scan chứa ảnh:

```text
1000 × 1400 pixels
```

Bạn render ở:

```text
600 DPI
```

không có nghĩa source scan đột nhiên có:

```text
5000 × 7000 pixels
```

Bạn chỉ đang rasterize PDF page ở độ phân giải cao hơn.

Nếu nguồn bên trong PDF có chất lượng thấp:

```text
Low quality source
       ↓
600 DPI render
       ↓
Large image
```

thì:

```text
Large ≠ More Information
```

Đây là một nguyên tắc rất quan trọng khi xử lý PDF.

---

# 19. DPI và file size

Có một mối quan hệ khác:

```text
DPI ↑
  ↓
pixel count ↑
  ↓
image processing cost ↑
  ↓
RAM ↑
  ↓
thời gian render ↑
```

Và thường:

```text
DPI ↑
  ↓
file output ↑
```

nhưng **file size không tăng cố định theo một công thức đơn giản**, vì còn phụ thuộc:

```text
PNG compression
JPEG quality
nội dung ảnh
text
noise
scan
image complexity
```

Ví dụ hai ảnh cùng:

```text
2480 × 3508
```

có thể có kích thước file rất khác nhau.

---

# 20. Test trực tiếp với pypdfium2

Bây giờ chúng ta viết chương trình thực tế.

```python
from pathlib import Path

import pypdfium2 as pdfium


def dpi_to_scale(dpi: float) -> float:
    if dpi <= 0:
        raise ValueError("DPI phải > 0")

    return dpi / 72.0


def render_page(
    pdf_path: str | Path,
    page_index: int,
    dpi: float,
):
    pdf = pdfium.PdfDocument(pdf_path)

    try:
        if not 0 <= page_index < len(pdf):
            raise IndexError(
                f"Page không hợp lệ: {page_index}"
            )

        page = pdf[page_index]

        pdf_width, pdf_height = page.get_size()

        scale = dpi_to_scale(dpi)

        bitmap = page.render(
            scale=scale
        )

        image = bitmap.to_pil()

        print(
            f"DPI: {dpi}"
        )

        print(
            f"PDF size: "
            f"{pdf_width:.2f} × "
            f"{pdf_height:.2f} points"
        )

        print(
            f"Scale: {scale:.4f}"
        )

        print(
            f"Image size: "
            f"{image.width} × "
            f"{image.height} pixels"
        )

        print(
            f"Mode: {image.mode}"
        )

        return image.copy()

    finally:
        pdf.close()


def main():

    for dpi in (72, 150, 300):

        image = render_page(
            "sample.pdf",
            page_index=0,
            dpi=dpi,
        )

        output = Path(
            f"page-{dpi}dpi.png"
        )

        image.save(output)

        image.close()

        print(
            f"Saved: {output}"
        )

        print("-" * 50)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python dpi_test.py
```

Bạn sẽ có:

```text
page-72dpi.png
page-150dpi.png
page-300dpi.png
```

Sau đó kiểm tra:

```text
kích thước pixel
kích thước file
thời gian render
độ rõ text
```

---

# 21. Một điểm rất quan trọng về DPI và GUI

Nếu sau này chúng ta làm:

```text
PySide6 PDF Viewer
```

thì **không nên render toàn bộ PDF ở 300 DPI**.

Ví dụ:

```text
PDF 500 trang
×
300 DPI
×
RGBA
```

sẽ cực kỳ tốn tài nguyên.

Viewer nên dùng chiến lược:

```text
User đang xem page 100
        ↓
render page 100
        ↓
DPI vừa đủ
        ↓
display
```

Khi user zoom:

```text
Zoom
 ↓
render lại với scale cao hơn
```

Đây chính là nền tảng của:

```text
PDF Viewer
Tile Rendering
Lazy Rendering
Thumbnail Cache
Page Cache
```

Chúng ta sẽ quay lại các vấn đề này ở phần production.

---

# 22. Render thumbnail ở DPI thấp

Ví dụ:

```python
bitmap = page.render(
    scale=72 / 72
)
```

tức:

```text
72 DPI
```

Sau đó:

```python
image = bitmap.to_pil()
```

và:

```python
image.thumbnail((300, 400))
```

Có thể dùng để tạo:

```text
PDF
 ├── page-001 thumbnail
 ├── page-002 thumbnail
 ├── page-003 thumbnail
 └── ...
```

Thay vì render tất cả ở 300 DPI.

---

# 23. Kiến trúc hiện tại

Sau Buổi 7, renderer của chúng ta có thể tiến hóa thành:

```text
                  RenderOptions
                       │
                 ┌─────┴─────┐
                 │            │
                DPI         Scale
                 │            │
                 └─────┬──────┘
                       ↓
                  PdfRenderer
                       ↓
                    PdfPage
                       ↓
                  PdfBitmap
                       ↓
                   PIL.Image
```

`RenderOptions` chịu trách nhiệm configuration:

```python
@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150
```

Renderer chịu trách nhiệm:

```text
PDFium rendering
```

PIL chịu trách nhiệm:

```text
image processing
```

Đây là separation of concerns khá sạch.

---

# 24. Bài tập Buổi 7

### Bài 1

Viết:

```python
dpi_to_scale()
scale_to_dpi()
```

Test:

```text
72
150
300
600
```

---

### Bài 2

Cho:

```text
A4 = 595 × 842 points
```

tính kích thước pixel ở:

```text
72 DPI
100 DPI
150 DPI
200 DPI
300 DPI
600 DPI
```

---

### Bài 3

Viết:

```python
estimate_memory_mib()
```

tính RAM cho:

```text
RGB
RGBA
Grayscale
```

với:

```text
300 DPI
A4
```

---

### Bài 4 — Quan trọng

Viết chương trình render **một page** ở:

```text
72
150
300
600 DPI
```

và đo:

```text
DPI
scale
pixel size
render time
PNG file size
```

Gợi ý:

```python
from time import perf_counter

start = perf_counter()

bitmap = page.render(
    scale=scale
)

elapsed = perf_counter() - start
```

---

### Bài 5 — Mini challenge

Viết:

```python
class RenderOptions:
    ...
```

cho phép:

```python
options = RenderOptions(
    dpi=300
)
```

và:

```python
options.scale
```

trả về:

```text
4.166666...
```

Sau đó:

```python
renderer.render(
    page,
    options,
)
```

---

# 25. Tóm tắt Buổi 7

Hãy nhớ 5 công thức này:

```text
72 points = 1 inch
```

```text
pixels = points × DPI / 72
```

```text
scale = DPI / 72
```

```text
DPI = scale × 72
```

và quan trọng nhất:

```text
Memory ∝ width × height
```

mà:

```text
width  ∝ scale
height ∝ scale
```

nên:

```text
Memory ∝ scale²
```

Vì vậy:

```text
DPI tăng 2 lần
        ↓
pixel tăng khoảng 4 lần
        ↓
RAM tăng khoảng 4 lần
```

Pipeline chúng ta hiện có:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
render(scale)
 ↓
PdfBitmap
 ↓
to_pil()
 ↓
PIL.Image
```

**Buổi 8 theo roadmap:** **Render từng trang thành PNG/JPEG** — chúng ta sẽ xây một `PdfImageExporter` hoàn chỉnh, xử lý PNG/JPEG, quality, RGB/RGBA, naming `page-001`, range page và không để renderer dính với logic lưu file.
