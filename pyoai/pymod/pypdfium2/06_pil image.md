# Buổi 6 — Bitmap → PIL Image

Theo roadmap bạn đưa, **Buổi 6** là:

> **Bitmap → PIL Image**

Ở buổi trước chúng ta đã có:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
PdfBitmap
```

Hôm nay ta hoàn thiện nhánh:

```text
PdfBitmap
    ↓
to_pil()
    ↓
PIL.Image
    ↓
PNG / JPEG / Resize / Crop / Grayscale / OCR...
```

`pypdfium2` hiện cung cấp adapter `PdfBitmap.to_pil()` để chuyển bitmap PDFium sang ảnh PIL; Pillow là dependency tùy chọn cho phần này. ([GitHub][1])

---

# 1. Vì sao cần PIL?

`PdfBitmap` là object thuộc `pypdfium2`:

```python
bitmap = page.render(scale=2)
```

Nó phù hợp với việc nhận dữ liệu render từ PDFium.

Nhưng nếu muốn xử lý ảnh bằng Python thì **PIL/Pillow** tiện hơn rất nhiều:

```text
PdfBitmap
    │
    │ to_pil()
    ▼
PIL.Image
    │
    ├── save()
    ├── resize()
    ├── crop()
    ├── rotate()
    ├── convert()
    ├── thumbnail()
    └── ...
```

Pillow sau đó có thể trở thành điểm trung gian cho:

```text
PDF
 ↓
pypdfium2
 ↓
PIL
 ├── PNG
 ├── JPEG
 ├── resize
 ├── crop
 ├── grayscale
 ├── preprocessing
 └── OCR
```

Đây cũng là hướng mà các project xử lý PDF thực tế sử dụng: render bằng pypdfium2 rồi chuyển sang PIL để xử lý tiếp. ([GitHub][2])

---

# 2. Cài Pillow

Nếu chưa cài:

```bash
pip install Pillow
```

Kiểm tra:

```bash
python -c "from PIL import Image; print(Image.__version__)"
```

Import:

```python
from PIL import Image
```

Lưu ý:

```python
import PIL
```

và:

```python
from PIL import Image
```

là hai cách import khác nhau.

Thông thường chúng ta dùng:

```python
from PIL import Image
```

---

# 3. Chuyển PdfBitmap → PIL

Đây là phần quan trọng nhất của buổi học.

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(scale=2)

    image = bitmap.to_pil()

    print(type(bitmap))
    print(type(image))
    print(image.size)
    print(image.mode)

finally:
    pdf.close()
```

Ví dụ output:

```text
<class 'pypdfium2._helpers.bitmap.PdfBitmap'>
<class 'PIL.Image.Image'>
(1190, 1684)
RGBA
```

Kết quả:

```text
PdfBitmap
    ↓
bitmap.to_pil()
    ↓
PIL.Image.Image
```

---

# 4. `image.size`

Sau khi có PIL:

```python
image = bitmap.to_pil()
```

ta có:

```python
image.size
```

Ví dụ:

```python
print(image.size)
```

Có thể nhận:

```text
(1190, 1684)
```

Trong đó:

```python
width, height = image.size
```

hoặc:

```python
width = image.width
height = image.height
```

Ví dụ:

```python
print("Width:", image.width)
print("Height:", image.height)
```

---

# 5. Phân biệt `page.get_size()` và `image.size`

Đây là một điểm **rất quan trọng**.

PDF page:

```python
width, height = page.get_size()
```

đơn vị là **PDF points**.

Còn:

```python
image.size
```

là **pixel**.

Ví dụ:

```text
PDF page
595 × 842 points
```

Nếu render:

```python
scale=1
```

thì khoảng:

```text
595 × 842 pixels
```

Nếu:

```python
scale=2
```

thì:

```text
1190 × 1684 pixels
```

Nếu:

```python
scale=4
```

thì:

```text
2380 × 3368 pixels
```

Quan hệ:

```text
pixels ≈ PDF points × scale
```

Và:

```text
scale = DPI / 72
```

Ví dụ:

```text
72 DPI
scale = 1

144 DPI
scale = 2

300 DPI
scale = 4.1667
```

Phần DPI/scale chúng ta sẽ học sâu ở **Buổi 7**.

---

# 6. Hiển thị ảnh

Sau khi có PIL:

```python
image.show()
```

Ví dụ hoàn chỉnh:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(scale=2)

    image = bitmap.to_pil()

    image.show()

finally:
    pdf.close()
```

`image.show()` chủ yếu hữu ích khi test nhanh.

Trong ứng dụng thật, chúng ta thường:

```python
image.save(...)
```

hoặc truyền `image` sang pipeline khác.

---

# 7. Lưu PIL Image

Ví dụ:

```python
image.save("page.png")
```

Hoặc:

```python
image.save("page.jpg")
```

Nhưng JPEG có một vấn đề quan trọng.

---

# 8. PNG và JPEG

### PNG

```python
image.save("page.png")
```

PNG:

* lossless
* tốt cho tài liệu
* tốt cho text
* tốt cho OCR
* giữ chất lượng tốt

### JPEG

```python
image.save("page.jpg")
```

JPEG:

* lossy
* nhỏ hơn
* phù hợp ảnh scan/photo
* không lý tưởng nếu tài liệu chứa text nhỏ

Ví dụ:

```python
image.save(
    "page.jpg",
    quality=90
)
```

---

# 9. JPEG và RGBA

Đây là lỗi rất dễ gặp.

Nếu:

```python
print(image.mode)
```

cho:

```text
RGBA
```

thì không nên trực tiếp giả định rằng JPEG sẽ xử lý được alpha channel.

Chúng ta chuyển sang RGB:

```python
rgb_image = image.convert("RGB")
```

Sau đó:

```python
rgb_image.save(
    "page.jpg",
    quality=90
)
```

Pipeline:

```text
PdfBitmap
    ↓
PIL RGBA
    ↓
convert("RGB")
    ↓
JPEG
```

---

# 10. `Image.mode`

Pillow sử dụng `mode` để biểu diễn format pixel.

Ví dụ:

```python
print(image.mode)
```

Có thể gặp:

```text
RGB
```

hoặc:

```text
RGBA
```

Một số mode khác:

```text
L
```

là grayscale.

Ví dụ:

```python
gray = image.convert("L")

print(gray.mode)
```

Output:

```text
L
```

---

# 11. Chuyển PDF page thành grayscale

Ví dụ:

```python
gray = image.convert("L")

gray.save("page-gray.png")
```

Pipeline:

```text
PDF
 ↓
PdfPage
 ↓
PdfBitmap
 ↓
PIL RGBA
 ↓
convert("L")
 ↓
Grayscale
```

Điều này rất hữu ích cho OCR.

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(scale=2)

    image = bitmap.to_pil()

    gray = image.convert("L")

    gray.save("page-gray.png")

finally:
    pdf.close()
```

---

# 12. Resize ảnh

Sau khi đã có PIL, ta có thể resize rất dễ.

```python
resized = image.resize((800, 1000))
```

Sau đó:

```python
resized.save("resized.png")
```

Tuy nhiên resize như trên sẽ **ép ảnh về đúng kích thước**.

Nếu muốn giữ tỷ lệ, sử dụng `thumbnail()`.

---

# 13. `thumbnail()`

Ví dụ:

```python
thumbnail = image.copy()

thumbnail.thumbnail((500, 500))

thumbnail.save("thumbnail.png")
```

Nếu ảnh ban đầu:

```text
1190 × 1684
```

thì sau:

```python
thumbnail.thumbnail((500, 500))
```

sẽ trở thành kích thước gần:

```text
353 × 500
```

vì Pillow giữ aspect ratio.

Điều này rất hữu ích để tạo thumbnail cho:

```text
PDF Viewer
Dashboard
File Browser
Preview
Document Manager
```

---

# 14. Crop ảnh

Pillow cho phép crop:

```python
cropped = image.crop(
    (100, 100, 800, 1000)
)
```

Cấu trúc:

```text
(left, top, right, bottom)
```

Ví dụ:

```python
cropped = image.crop(
    (
        100,
        100,
        800,
        1000,
    )
)

cropped.save("cropped.png")
```

Pipeline:

```text
PDF
 ↓
render
 ↓
PIL
 ↓
crop
 ↓
image
```

Sau này khi học:

> Render region / CropBox / coordinate system

chúng ta sẽ phân biệt rõ **crop bằng PIL** và **render trực tiếp một vùng PDF**.

Hai việc này không hoàn toàn giống nhau.

---

# 15. Rotate bằng Pillow

Ví dụ:

```python
rotated = image.rotate(90, expand=True)

rotated.save("rotated.png")
```

Pillow sẽ xoay ảnh sau khi render.

Sau này chúng ta sẽ học cách:

```python
page.render(
    rotation=...
)
```

để PDFium render theo rotation ngay từ đầu.

Đây là một điểm quan trọng về architecture:

```text
Cách 1:

PDF
 ↓
render
 ↓
PIL
 ↓
rotate


Cách 2:

PDF
 ↓
PDFium render(rotation=...)
 ↓
Bitmap
 ↓
PIL
```

Hai pipeline có mục đích và chi phí khác nhau.

---

# 16. Ví dụ hoàn chỉnh: PDF → PIL

Bây giờ viết thành một chương trình hoàn chỉnh.

## `pdf_to_pil.py`

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def render_page_to_pil(
    pdf_path: str | Path,
    page_index: int = 0,
    scale: float = 2.0,
) -> Image.Image:

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF không tồn tại: {pdf_path}"
        )

    if scale <= 0:
        raise ValueError(
            "scale phải > 0"
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
            scale=scale
        )

        image = bitmap.to_pil()

        return image.copy()

    finally:
        pdf.close()


def main() -> None:

    image = render_page_to_pil(
        "sample.pdf",
        page_index=0,
        scale=2.0,
    )

    print("Type:", type(image))
    print("Size:", image.size)
    print("Mode:", image.mode)

    image.save("page.png")

    rgb = image.convert("RGB")

    rgb.save(
        "page.jpg",
        quality=90,
    )


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python pdf_to_pil.py
```

Kết quả:

```text
Type: <class 'PIL.Image.Image'>
Size: (1190, 1684)
Mode: RGBA
```

và:

```text
page.png
page.jpg
```

---

# 17. Tại sao tôi dùng `image.copy()`?

Đây là một vấn đề quản lý resource rất đáng chú ý.

Ta có:

```python
bitmap = page.render(...)
image = bitmap.to_pil()
```

`PIL.Image` được tạo từ dữ liệu bitmap.

Trong các pipeline production, ta không nên thiết kế code phụ thuộc vào resource PDFium lâu hơn cần thiết.

Do đó:

```python
return image.copy()
```

giúp tạo một ảnh PIL độc lập hơn với bitmap nguồn.

Một pattern thường thấy trong các ứng dụng xử lý PDF thực tế là render → `to_pil().copy()` → đóng bitmap. ([GitHub][2])

---

# 18. Thiết kế Renderer

Bây giờ đưa code vào kiến trúc mà chúng ta đang xây.

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
PdfBitmap
 │
 ▼
PIL Image
```

Ta tạo:

```text
infrastructure/
└── pdfium/
    └── renderer.py
```

## `renderer.py`

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


class PdfRenderer:

    def render_page(
        self,
        pdf_path: str | Path,
        page_index: int,
        scale: float = 1.0,
    ) -> Image.Image:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF không tồn tại: {pdf_path}"
            )

        if scale <= 0:
            raise ValueError(
                "scale phải > 0"
            )

        pdf = pdfium.PdfDocument(pdf_path)

        try:
            if not 0 <= page_index < len(pdf):
                raise IndexError(
                    f"Trang không hợp lệ: {page_index}"
                )

            page = pdf[page_index]

            bitmap = page.render(
                scale=scale
            )

            image = bitmap.to_pil()

            return image.copy()

        finally:
            pdf.close()
```

Sử dụng:

```python
from renderer import PdfRenderer


renderer = PdfRenderer()

image = renderer.render_page(
    "sample.pdf",
    page_index=0,
    scale=2,
)

print(image.size)
print(image.mode)

image.save("output.png")
```

---

# 19. Nhưng architecture còn một vấn đề

Ở đây:

```python
class PdfRenderer:
```

vẫn trả:

```python
PIL.Image.Image
```

Tức là tầng application của chúng ta biết Pillow.

Trong project nhỏ:

```text
Application
    ↓
PIL
```

có thể chấp nhận.

Nhưng với project production lớn, ta có thể muốn:

```text
Application
    ↓
Image abstraction
    ↓
Pillow adapter
```

Tuy nhiên **chưa nên abstraction quá sớm**.

Đây là nguyên tắc rất quan trọng:

> Không tạo abstraction chỉ vì “SOLID yêu cầu phải abstraction”.

Hiện tại mục tiêu của chúng ta là học chắc:

```text
PdfBitmap
    ↓
PIL
```

Sau khi hiểu pipeline, ta mới quyết định abstraction phù hợp.

---

# 20. Một pipeline rất quan trọng

Từ hôm nay, hãy ghi nhớ pipeline này:

```text
                 pypdfium2
                     │
PDF ──→ PdfDocument ─┤
                     ↓
                   PdfPage
                     │
                  render()
                     ↓
                  PdfBitmap
                     │
                  to_pil()
                     ↓
                 PIL.Image
                     │
        ┌────────────┼─────────────┐
        ↓            ↓             ↓
      PNG          JPEG          OCR
        │            │             │
        ↓            ↓             ↓
     Storage      Storage      Text
```

Đây sẽ là nền móng cho phần:

```text
PDF → OCR
PDF → OpenCV
PDF → thumbnail
PDF → image processing
PDF → document analysis
```

---

# 21. Bài tập thực hành

## Bài 1 — Kiểm tra PIL

Viết chương trình:

```text
sample.pdf
    ↓
page 1
    ↓
PdfBitmap
    ↓
PIL
```

in:

```text
type
size
width
height
mode
```

---

## Bài 2 — 3 phiên bản ảnh

Render cùng một trang:

```python
scale=1
scale=2
scale=4
```

Lưu:

```text
page-scale-1.png
page-scale-2.png
page-scale-4.png
```

Sau đó in:

```text
scale=1  size=...
scale=2  size=...
scale=4  size=...
```

Bạn sẽ thấy kích thước pixel tăng gần tuyến tính theo `scale`.

---

## Bài 3 — Grayscale

Tạo:

```text
page-color.png
page-gray.png
```

với:

```python
gray = image.convert("L")
```

Kiểm tra:

```python
print(image.mode)
print(gray.mode)
```

---

## Bài 4 — Thumbnail

Tạo:

```text
thumbnail.png
```

với giới hạn:

```text
500 × 500
```

nhưng **không được làm méo ảnh**.

Gợi ý:

```python
thumbnail = image.copy()
thumbnail.thumbnail((500, 500))
```

---

## Bài 5 — Xây `PdfPageImageRenderer`

Mục tiêu:

```python
renderer = PdfPageImageRenderer()

image = renderer.render(
    "sample.pdf",
    page_index=0,
    scale=2,
)

image.save("page.png")
```

Thiết kế:

```text
PdfPageImageRenderer
        │
        ├── validate PDF
        ├── open PdfDocument
        ├── get page
        ├── render PdfBitmap
        ├── convert PIL
        └── return PIL.Image
```

---

# 22. Tổng kết Buổi 6

Hôm nay chúng ta đã hoàn thành:

### `PdfBitmap → PIL`

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()
```

### Kiểm tra ảnh

```python
image.size
image.width
image.height
image.mode
```

### Lưu ảnh

```python
image.save("page.png")
```

### JPEG

```python
image.convert("RGB").save(
    "page.jpg",
    quality=90,
)
```

### Grayscale

```python
gray = image.convert("L")
```

### Resize

```python
image.resize(...)
```

### Thumbnail

```python
thumbnail.thumbnail(...)
```

### Crop

```python
image.crop(...)
```

### Rotate

```python
image.rotate(...)
```

Và pipeline hiện tại của chúng ta đã là:

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
Image Processing
```

Theo đúng roadmap bạn đưa, **Buổi 7** sẽ là:

# **Buổi 7 — DPI, scale và kích thước ảnh**

Ta sẽ giải quyết thật kỹ mối quan hệ:

```text
PDF Point
    ↓
DPI
    ↓
Scale
    ↓
Pixel
    ↓
Memory
    ↓
File size
    ↓
Quality
```

đặc biệt là tại sao:

```python
scale = dpi / 72
```

và tại sao render:

```python
300 DPI
```

có thể làm một trang A4 ngốn hàng chục MB RAM. ([GitHub][1])

**Tài liệu chính thức:** [pypdfium2 GitHub / Usage](https://github.com/pypdfium2-team/pypdfium2?utm_source=chatgpt.com)

[1]: https://github.com/pypdfium2-team/pypdfium2/blob/main/README.md?utm_source=chatgpt.com "pypdfium2/README.md at main · pypdfium2-team/pypdfium2 · GitHub"
[2]: https://github.com/opendatalab/MinerU/blob/master/mineru/utils/pdf_reader.py?utm_source=chatgpt.com "MinerU/mineru/utils/pdf_reader.py at master · opendatalab/MinerU · GitHub"
