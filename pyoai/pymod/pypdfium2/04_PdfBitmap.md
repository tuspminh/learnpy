# Buổi 4 — `PdfBitmap`: Bitmap, PIL, RGB/RGBA và Memory

Ở Buổi 3 chúng ta đã đi được đến:

```text
PdfDocument
    ↓
PdfPage
    ↓
page.render()
    ↓
PdfBitmap
```

Hôm nay chúng ta tập trung vào **`PdfBitmap`**.

Đây là một mắt xích cực kỳ quan trọng vì từ bitmap của PDFium, chúng ta có thể chuyển sang:

```text
PdfBitmap
   ├── PIL.Image
   ├── NumPy
   ├── OpenCV
   └── OCR
```

---

# 1. `PdfBitmap` là gì?

Khi:

```python
bitmap = page.render(scale=2)
```

`bitmap` là kết quả render của PDFium.

Có thể hình dung:

```text
PDF
 │
 ▼
PdfPage
 │
 │ render()
 ▼
PdfBitmap
 │
 ├── width
 ├── height
 ├── pixel data
 └── format
```

Nó chứa dữ liệu hình ảnh đã được PDFium render từ trang PDF.

---

# 2. Bitmap khác PIL Image như thế nào?

Đây là điểm cần phân biệt:

```text
PdfBitmap
    │
    │ to_pil()
    ▼
PIL.Image
```

`PdfBitmap` thuộc hệ sinh thái:

```text
PDFium / pypdfium2
```

còn:

```text
PIL.Image
```

thuộc:

```text
Pillow
```

Ví dụ:

```python
bitmap = page.render()

image = bitmap.to_pil()
```

Sau đó:

```python
print(type(bitmap))
print(type(image))
```

Bạn sẽ thấy hai object khác nhau.

---

# 3. `to_pil()` — cầu nối với Pillow

Đây là API chúng ta sẽ sử dụng rất nhiều:

```python
image = bitmap.to_pil()
```

Sau đó có thể:

```python
image.save("page.png")
```

hoặc:

```python
image.resize(...)
```

hoặc:

```python
image.crop(...)
```

hoặc:

```python
image.convert("L")
```

Pipeline:

```text
PDFium
   │
   ▼
PdfBitmap
   │
   ▼
PIL.Image
   │
   ├── PNG
   ├── JPEG
   ├── resize
   ├── crop
   └── OCR
```

---

# 4. Chương trình đầu tiên

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(scale=2)

    print("Bitmap:", bitmap)

    image = bitmap.to_pil()

    print("Image:", image)
    print("Size:", image.size)
    print("Mode:", image.mode)

finally:
    pdf.close()
```

Ví dụ:

```text
Size: (1191, 1684)
Mode: RGB
```

Tùy PDF và cách render, mode có thể khác.

---

# 5. `Image.size`

Sau:

```python
image = bitmap.to_pil()
```

ta có:

```python
width, height = image.size
```

Ví dụ:

```python
print("Width:", image.width)
print("Height:", image.height)
```

hoặc:

```python
print(image.size)
```

Kết quả:

```text
(1191, 1684)
```

Đây là **pixel**, khác với:

```python
page.get_size()
```

là PDF points.

---

# 6. Hai loại kích thước cần phân biệt

Đây là kiến thức rất quan trọng:

```text
PdfPage
    │
    └── get_size()
           ↓
      PDF points

PdfBitmap / PIL
    │
    └── size
           ↓
        pixels
```

Ví dụ:

```text
PDF page:

595 × 842 points

        ↓
      render
        ↓

1191 × 1684 pixels
```

---

# 7. Pixel format

Bitmap không chỉ có:

```text
width
height
```

mà còn có:

```text
pixel format
```

Ví dụ:

```text
RGB
RGBA
BGRA
Gray
```

Điều này rất quan trọng khi chúng ta chuyển dữ liệu sang:

* Pillow
* NumPy
* OpenCV
* OCR.

---

# 8. RGB

RGB có:

```text
R = Red
G = Green
B = Blue
```

Mỗi pixel:

```text
[R, G, B]
```

Ví dụ:

```text
[255, 0, 0]
```

là đỏ.

```text
[0, 255, 0]
```

là xanh lá.

```text
[0, 0, 255]
```

là xanh dương.

---

# 9. RGBA

RGBA có thêm:

```text
A = Alpha
```

Mỗi pixel:

```text
[R, G, B, A]
```

Ví dụ:

```text
[255, 0, 0, 255]
```

nghĩa là:

```text
Red
Alpha = opaque
```

Trong Pillow:

```python
print(image.mode)
```

có thể cho:

```text
RGBA
```

---

# 10. Alpha channel

Alpha thường biểu diễn độ trong suốt:

```text
0   → transparent
255 → opaque
```

Ví dụ:

```text
RGBA

255 0 0 255
│   │ │ │
│   │ │ └── Alpha
│   │ └──── Blue
│   └────── Green
└────────── Red
```

Khi làm PDF → PNG, alpha có thể quan trọng.

Nhưng nếu mục tiêu chỉ là OCR:

```text
RGBA
 ↓
RGB / grayscale
 ↓
OCR
```

thường đơn giản hơn.

---

# 11. Chuyển sang grayscale

Pillow:

```python
gray = image.convert("L")
```

Ví dụ:

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()

gray = image.convert("L")

gray.save("page-gray.png")
```

`L` là grayscale 8-bit.

```text
0   → black
255 → white
```

---

# 12. Vì sao grayscale hữu ích cho OCR?

Một trang màu:

```text
RGB
 ↓
3 channels
```

có thể chuyển:

```text
RGB
 ↓
Grayscale
 ↓
OCR
```

Giảm dữ liệu:

```text
RGB
3 bytes / pixel

↓

Gray
1 byte / pixel
```

Ví dụ:

```text
2480 × 3508
```

RGB:

```text
2480 × 3508 × 3
≈ 26.1 MB
```

Grayscale:

```text
2480 × 3508 × 1
≈ 8.7 MB
```

Chưa tính overhead của Python/Pillow.

---

# 13. Memory — phần rất quan trọng

Giả sử:

```text
2480 × 3508
```

Số pixel:

```text
2480 × 3508
≈ 8.7 triệu pixel
```

RGB:

```text
≈ 26 MB
```

RGBA:

```text
≈ 35 MB
```

Một PDF 100 trang:

```text
100 × 35 MB
≈ 3.5 GB
```

Nếu bạn render tất cả rồi giữ trong list:

```python
images = []

for page in pdf:
    bitmap = page.render(scale=4)
    image = bitmap.to_pil()

    images.append(image)
```

thì rất nguy hiểm.

---

# 14. Không nên giữ toàn bộ image

Không nên:

```text
PDF
 ↓
Render 1
 ↓
Render 2
 ↓
Render 3
 ↓
...
 ↓
Render 100
 ↓
Memory rất lớn
```

Nên:

```text
Page 1
 ↓
Render
 ↓
Process
 ↓
Save
 ↓
Release

Page 2
 ↓
Render
 ↓
Process
 ↓
Save
 ↓
Release
```

Đây là **streaming/batch processing theo page**.

---

# 15. Hàm render an toàn hơn

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

        print(
            f"Saved: {output_path}"
        )

    finally:
        pdf.close()
```

Điểm quan trọng:

```text
render
  ↓
to_pil
  ↓
save
```

không lưu tất cả page vào memory.

---

# 16. NumPy

Nếu muốn xử lý image bằng NumPy:

```python
import numpy as np
```

Sau:

```python
image = bitmap.to_pil()
```

có thể:

```python
array = np.array(image)
```

Kiểm tra:

```python
print(array.shape)
print(array.dtype)
```

Ví dụ RGB:

```text
(1684, 1191, 3)
```

Tức:

```text
height
width
channels
```

---

# 17. RGB → NumPy

Ví dụ:

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()

array = np.array(image)

print("Shape:", array.shape)
print("Dtype:", array.dtype)
```

Ví dụ:

```text
Shape: (1684, 1191, 3)
Dtype: uint8
```

Điều này có nghĩa:

```text
1684 rows
1191 columns
3 channels
```

---

# 18. Grayscale → NumPy

```python
gray = image.convert("L")

array = np.array(gray)

print(array.shape)
```

Kết quả:

```text
(1684, 1191)
```

Không còn channel thứ ba.

---

# 19. OpenCV cần chú ý RGB/BGR

Đây là một lỗi kinh điển.

Pillow thường:

```text
RGB
```

OpenCV thường sử dụng:

```text
BGR
```

Ví dụ:

```python
from PIL import Image
import numpy as np
import cv2


image = Image.open("page.png")

rgb = np.array(image)

bgr = cv2.cvtColor(
    rgb,
    cv2.COLOR_RGB2BGR,
)
```

Pipeline:

```text
pypdfium2
     ↓
PIL RGB
     ↓
NumPy RGB
     ↓
OpenCV BGR
```

Nếu quên bước chuyển đổi:

```text
màu có thể bị đảo.
```

---

# 20. PDF → Pillow → OpenCV

Một pipeline hoàn chỉnh:

```python
import cv2
import numpy as np
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(
        scale=2
    )

    image = bitmap.to_pil()

    rgb = np.array(image)

    bgr = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2BGR,
    )

    gray = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2GRAY,
    )

    cv2.imwrite(
        "page-gray.png",
        gray,
    )

finally:
    pdf.close()
```

Pipeline:

```text
PDF
 ↓
PdfPage
 ↓
PdfBitmap
 ↓
PIL
 ↓
NumPy
 ↓
OpenCV
 ↓
Grayscale
```

Đây chính là nền móng cho OCR.

---

# 21. Bitmap → PIL → OCR

Sau này chúng ta có thể:

```text
PDF
 ↓
pypdfium2
 ↓
PdfBitmap
 ↓
PIL
 ↓
preprocessing
 ↓
OCR
 ↓
text
```

Ví dụ:

```text
novel.pdf
    ↓
page 1
    ↓
render 300 DPI
    ↓
grayscale
    ↓
threshold
    ↓
OCR
    ↓
"Chapter 1..."
```

---

# 22. Tại sao không render 600 DPI ngay?

Giả sử:

```text
A4
```

ở 300 DPI:

```text
≈ 2480 × 3508
```

ở 600 DPI:

```text
≈ 4961 × 7016
```

Số pixel tăng khoảng:

```text
4 lần
```

và memory cũng tăng gần tương ứng.

```text
300 DPI
    ↓
8.7 MP

600 DPI
    ↓
34.8 MP
```

Do đó:

> Tăng DPI không chỉ làm ảnh lớn hơn; nó làm chi phí xử lý tăng rất nhanh.

---

# 23. Render thumbnail

Nếu chỉ cần thumbnail:

```python
bitmap = page.render(
    scale=0.5
)

image = bitmap.to_pil()

image.thumbnail((300, 400))

image.save("thumbnail.png")
```

Pipeline:

```text
PDF
 ↓
low-res render
 ↓
PIL
 ↓
thumbnail
```

Không cần 300 DPI cho thumbnail.

---

# 24. Một renderer có cấu hình

Bây giờ chúng ta thiết kế tốt hơn.

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
options = RenderOptions(
    dpi=300
)

print(options.scale)
```

Kết quả:

```text
4.166666666666667
```

---

# 25. `PdfRenderer`

```python
import pypdfium2 as pdfium


class PdfRenderer:

    def render(
        self,
        page,
        options: RenderOptions,
    ):
        return page.render(
            scale=options.scale
        )
```

Sử dụng:

```python
renderer = PdfRenderer()

options = RenderOptions(
    dpi=150
)

bitmap = renderer.render(
    page,
    options,
)

image = bitmap.to_pil()
```

Kiến trúc:

```text
Application
     │
     ▼
RenderOptions
     │
     ▼
PdfRenderer
     │
     ▼
PdfPage
     │
     ▼
PdfBitmap
```

---

# 26. Vì sao tách `RenderOptions`?

Sau này chúng ta sẽ cần:

```text
RenderOptions
├── dpi
├── rotation
├── grayscale
├── crop
├── transparent
└── ...
```

Nếu viết:

```python
render(
    page,
    150,
    90,
    True,
    False,
    ...
)
```

code sẽ rất khó đọc.

Dataclass:

```python
RenderOptions(
    dpi=300,
    ...
)
```

sạch hơn rất nhiều.

Đây cũng kết nối trực tiếp với phần **Dataclass** và **Design Pattern** bạn đã học.

---

# 27. Mini Project Buổi 4

Hãy xây:

```text
pdf_bitmap/
│
├── main.py
├── renderer.py
├── options.py
└── sample.pdf
```

### `options.py`

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

### `renderer.py`

```python
import pypdfium2 as pdfium

from options import RenderOptions


class PdfRenderer:

    def render(
        self,
        page,
        options: RenderOptions,
    ):
        return page.render(
            scale=options.scale
        )

    def render_to_pil(
        self,
        page,
        options: RenderOptions,
    ):
        bitmap = self.render(
            page,
            options,
        )

        return bitmap.to_pil()
```

### `main.py`

```python
import pypdfium2 as pdfium

from options import RenderOptions
from renderer import PdfRenderer


def main():
    pdf = pdfium.PdfDocument(
        "sample.pdf"
    )

    try:
        page = pdf[0]

        options = RenderOptions(
            dpi=150
        )

        renderer = PdfRenderer()

        image = renderer.render_to_pil(
            page,
            options,
        )

        print("Image mode:", image.mode)
        print("Image size:", image.size)

        image.save(
            "page-001.png"
        )

    finally:
        pdf.close()


if __name__ == "__main__":
    main()
```

---

# 28. Bài tập

### Bài 1

Render cùng một page:

```text
72 DPI
150 DPI
300 DPI
```

và in:

```text
DPI
Image width
Image height
Image mode
```

---

### Bài 2

Chuyển:

```text
RGB → Grayscale
```

và lưu:

```text
page-gray.png
```

---

### Bài 3

Chuyển PIL → NumPy:

```python
array = np.array(image)
```

in:

```text
shape
dtype
```

---

### Bài 4

Thử với:

```text
scale=1
scale=2
scale=4
```

Quan sát:

```text
image.size
```

và so sánh memory.

---

# 29. Kiến thức quan trọng nhất Buổi 4

Bạn nên ghi nhớ pipeline này:

```text
                  PDFium
                    │
PDF ──► PdfPage ──► render()
                    │
                    ▼
                PdfBitmap
                    │
                 to_pil()
                    │
                    ▼
                PIL.Image
                    │
                 np.array()
                    │
                    ▼
                  NumPy
                    │
              cv2.cvtColor()
                    │
                    ▼
                 OpenCV
                    │
                    ▼
                   OCR
```

Và đặc biệt:

```text
PdfPage.get_size()
        ↓
     PDF points

PdfBitmap / PIL
        ↓
      pixels
```

Cùng với:

```text
scale = DPI / 72
```

và nguyên tắc memory:

```text
Render
  ↓
Process
  ↓
Save
  ↓
Release
```

**Buổi 5** chúng ta sẽ chuyển sang **render PDF → PNG/JPEG một cách bài bản**: `scale`, `dpi`, `rotation`, `crop`, chất lượng ảnh, đặt tên file, render từng trang/toàn bộ document và xây một **`PdfImageExporter`** hoàn chỉnh.
