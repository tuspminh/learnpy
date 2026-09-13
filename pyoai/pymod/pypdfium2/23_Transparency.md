# Phần III — PDF Rendering chuyên sâu

# Buổi 23 — Transparency

Ở Buổi 22 chúng ta đã có:

```text
PDF
 ↓
PDFium
 ↓
Bitmap
 ↓
PIL.Image
 ↓
Grayscale
```

Hôm nay chúng ta thêm **Transparency / Alpha channel**.

Mục tiêu của buổi này:

1. Hiểu alpha channel.
2. Phân biệt `RGB` và `RGBA`.
3. Hiểu transparent background.
4. Render PDF với nền trong suốt.
5. Hiểu tại sao PNG hỗ trợ transparency còn JPEG thì không.
6. Thiết kế `RenderOptions` để chuẩn bị cho Buổi 24–30.

---

# 1. Transparency là gì?

Một pixel RGB:

```text
RGB
├── R
├── G
└── B
```

Ví dụ:

```text
RGB(255, 0, 0)
```

là đỏ.

Khi thêm alpha:

```text
RGBA
├── R
├── G
├── B
└── A
```

Ví dụ:

```text
RGBA(255, 0, 0, 255)
```

là:

```text
đỏ + hoàn toàn nhìn thấy
```

Còn:

```text
RGBA(255, 0, 0, 128)
```

là:

```text
đỏ + trong suốt khoảng 50%
```

Và:

```text
RGBA(255, 0, 0, 0)
```

là:

```text
hoàn toàn trong suốt
```

Điểm quan trọng:

> **Alpha không phải màu. Alpha là mức độ nhìn thấy của pixel.**

---

# 2. RGBA trong PIL

Tạo một ảnh RGBA:

```python
from PIL import Image


image = Image.new(
    "RGBA",
    (400, 300),
    (255, 0, 0, 128),
)

print(image.mode)
print(image.getpixel((0, 0)))
```

Kết quả:

```text
RGBA
(255, 0, 0, 128)
```

---

# 3. Alpha từ 0 đến 255

Có thể hiểu:

```text
Alpha
│
├── 0
│   hoàn toàn trong suốt
│
├── 64
│   rất trong suốt
│
├── 128
│   bán trong suốt
│
├── 192
│   khá rõ
│
└── 255
    hoàn toàn opaque
```

Ta có thể kiểm tra:

```python
from PIL import Image


image = Image.new(
    "RGBA",
    (4, 1),
)

pixels = [
    (255, 0, 0, 0),
    (255, 0, 0, 64),
    (255, 0, 0, 128),
    (255, 0, 0, 255),
]

for x, pixel in enumerate(pixels):
    image.putpixel((x, 0), pixel)

for x in range(4):
    print(image.getpixel((x, 0)))
```

---

# 4. Render PDF và transparency

Trong pypdfium2, `page.render()` có các tùy chọn liên quan đến màu sắc/background và alpha.

Một cấu hình quan trọng là:

```python
page.render(
    scale=2,
    fill_to_stroke=True,
)
```

Tuy nhiên, khi thiết kế ứng dụng, **không nên giả định rằng chỉ bật một cờ là mọi PDF đều trở thành "ảnh nền trong suốt"**.

PDF có cơ chế transparency riêng:

```text
PDF transparency
├── transparent object
├── opacity
├── blend mode
├── soft mask
├── transparency group
└── page background
```

PDFium sẽ thực hiện compositing/rasterization các thành phần này khi render.

Do đó cần phân biệt hai khái niệm:

```text
PDF object transparency
```

và:

```text
bitmap alpha channel
```

Chúng liên quan nhưng không phải cùng một thứ.

---

# 5. Render bitmap rồi kiểm tra mode

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render(
        scale=2,
    )

    image = bitmap.to_pil()

    print("mode:", image.mode)
    print("size:", image.size)

finally:
    pdf.close()
```

Thông thường bạn sẽ gặp các mode như:

```text
RGB
RGBA
L
LA
```

tùy bitmap/render configuration và đường chuyển đổi sang PIL.

**Không nên hard-code rằng mọi PDF render đều trả về một mode duy nhất.**

---

# 6. RGB vs RGBA

## RGB

```text
R G B
```

Mỗi pixel thường:

```text
3 bytes
```

Memory gần đúng:

```text
width × height × 3
```

## RGBA

```text
R G B A
```

Mỗi pixel:

```text
4 bytes
```

Memory:

```text
width × height × 4
```

Ví dụ:

```text
2550 × 3300
```

RGB:

```text
≈ 25.2 MB
```

RGBA:

```text
≈ 33.7 MB
```

Như vậy transparency có **chi phí memory**.

Đây là lý do Buổi 29 sẽ rất quan trọng.

---

# 7. `convert("RGBA")`

PIL cho phép chuyển:

```python
rgb = image.convert("RGB")

rgba = image.convert("RGBA")
```

Ví dụ:

```python
from PIL import Image


rgb = Image.new(
    "RGB",
    (100, 100),
    "white",
)

rgba = rgb.convert("RGBA")

print(rgb.mode)
print(rgba.mode)
```

Kết quả:

```text
RGB
RGBA
```

Pixel:

```python
print(rgba.getpixel((0, 0)))
```

sẽ có dạng:

```text
(255, 255, 255, 255)
```

Tức:

```text
white
+
alpha = 255
```

Nhưng hãy chú ý:

> Chuyển RGB → RGBA **không tạo ra transparency thực sự**.

Nó chỉ thêm alpha channel với:

```text
A = 255
```

---

# 8. Tạo nền trong suốt thực sự

Ví dụ tạo canvas transparent:

```python
from PIL import Image


image = Image.new(
    "RGBA",
    (800, 600),
    (0, 0, 0, 0),
)
```

Pixel:

```python
print(image.getpixel((0, 0)))
```

Kết quả:

```text
(0, 0, 0, 0)
```

Đây mới là pixel hoàn toàn transparent.

---

# 9. PNG và JPEG

Đây là kiến thức bắt buộc.

### PNG

Hỗ trợ alpha:

```text
RGBA → PNG
```

Ví dụ:

```python
image.save(
    "output.png"
)
```

### JPEG

Không có alpha channel:

```text
RGBA
 ↓
JPEG
```

phải compositing về background trước.

Ví dụ:

```python
rgba = image.convert("RGBA")

background = Image.new(
    "RGB",
    rgba.size,
    "white",
)

background.paste(
    rgba,
    mask=rgba.getchannel("A"),
)

background.save(
    "output.jpg",
    quality=95,
)
```

Pipeline:

```text
RGBA
  │
  ▼
Alpha compositing
  │
  ▼
RGB
  │
  ▼
JPEG
```

---

# 10. Hàm compositing nền trắng

Ta nên tách thành một class:

```python
from PIL import Image


class ImageCompositor:

    def flatten_on_white(
        self,
        image: Image.Image,
    ) -> Image.Image:

        rgba = image.convert("RGBA")

        background = Image.new(
            "RGB",
            rgba.size,
            (255, 255, 255),
        )

        background.paste(
            rgba,
            mask=rgba.getchannel("A"),
        )

        return background
```

Sử dụng:

```python
compositor = ImageCompositor()

jpg_image = compositor.flatten_on_white(
    rgba_image
)

jpg_image.save(
    "output.jpg",
    quality=95,
)
```

---

# 11. Alpha compositing là gì?

Giả sử foreground:

```text
Red
```

background:

```text
White
```

và:

```text
alpha = 0.5
```

Kết quả không còn là đỏ nguyên chất.

Ta có:

```text
result
=
foreground × alpha
+
background × (1 - alpha)
```

Ví dụ:

```text
red = 255, 0, 0
white = 255, 255, 255
alpha = 0.5
```

thì kết quả xấp xỉ:

```text
255, 128, 128
```

tức màu hồng nhạt.

PIL thực hiện phần compositing này khi ta dùng:

```python
background.paste(
    rgba,
    mask=alpha,
)
```

---

# 12. Transparency trong PDF phức tạp hơn alpha đơn giản

Đây là phần rất quan trọng.

Trong PDF:

```text
Object A
 opacity = 50%
```

có thể nằm trên:

```text
Object B
```

PDFium phải tính:

```text
A
 +
B
 ↓
composited result
```

Ngoài opacity còn có:

```text
blend mode
soft mask
transparency group
```

Do đó:

```text
PDF source
```

không nhất thiết có một alpha channel đơn giản mà ta có thể "copy" trực tiếp.

Rendering engine phải **rasterize và composite**.

---

# 13. Thêm `transparent` vào RenderOptions

Ở Buổi 22:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0
    grayscale: bool = False

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

    @property
    def scale(self):
        return self.dpi / 72.0
```

Bây giờ:

```python
@dataclass(frozen=True)
class RenderOptions:

    dpi: float = 150.0
    grayscale: bool = False
    transparent: bool = False

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

    @property
    def scale(self):
        return self.dpi / 72.0
```

Ví dụ:

```python
options = RenderOptions(
    dpi=300,
    grayscale=False,
    transparent=True,
)
```

---

# 14. Nhưng `transparent=True` chưa nên tự động convert RGBA

Đây là một quyết định kiến trúc quan trọng.

Không nên viết:

```python
if options.transparent:
    image = image.convert("RGBA")
```

rồi cho rằng PDF đã được render transparent.

Vì:

```text
convert("RGBA")
```

chỉ thay đổi representation của image.

Nó **không loại bỏ background đã được composited**.

Ví dụ:

```text
PDF
 ↓
render với nền trắng
 ↓
RGB trắng
 ↓
convert RGBA
```

ta nhận:

```text
RGBA(..., alpha=255)
```

chứ không phải:

```text
transparent background
```

---

# 15. Phân biệt 3 trường hợp

### Trường hợp A

```text
PDF
 ↓
render
 ↓
RGB
```

Nền đã được composited.

---

### Trường hợp B

```text
PDF
 ↓
render
 ↓
RGBA
```

Bitmap có alpha.

---

### Trường hợp C

```text
PDF
 ↓
render
 ↓
RGBA
 ↓
PIL
 ↓
PNG
```

Đây là pipeline phù hợp khi cần giữ transparency.

---

# 16. Renderer nên nhận options

Ta cập nhật renderer:

```python
class PdfRenderer:

    def render_page(
        self,
        page_index: int,
        options: RenderOptions,
    ):

        if self._pdf is None:
            raise RuntimeError(
                "PDF chưa được mở"
            )

        page = self._pdf[page_index]

        bitmap = page.render(
            scale=options.scale,
        )

        return bitmap
```

Ở bước này ta **chưa ép transparency bằng PIL**.

Buổi 23 tập trung vào kiến trúc và semantics.

Khi triển khai một option rendering cụ thể, phải dựa vào API version của pypdfium2/PDFium mà ứng dụng đang dùng.

---

# 17. Một `ImageOutputPolicy`

Một cách thiết kế đẹp hơn là tách:

```text
Rendering
```

và:

```text
Output
```

Ví dụ:

```python
from enum import Enum


class ImageFormat(str, Enum):

    PNG = "png"
    JPEG = "jpeg"
```

Sau đó:

```python
@dataclass(frozen=True)
class OutputOptions:

    format: ImageFormat = ImageFormat.PNG
    quality: int = 95
```

Lúc này:

```text
RenderOptions
    │
    ├── dpi
    ├── grayscale
    ├── transparent
    ├── rotation
    └── crop

OutputOptions
    │
    ├── format
    └── quality
```

Đây là thiết kế tốt hơn về lâu dài.

---

# 18. Vì sao `quality` không thuộc rendering?

Ví dụ:

```python
page.render(
    scale=4
)
```

là rendering.

Nhưng:

```python
image.save(
    "page.jpg",
    quality=90,
)
```

là encoding/output.

Hai quá trình:

```text
PDF Rendering
       ↓
Bitmap
       ↓
Image Processing
       ↓
Image Encoding
```

không nên trộn lẫn.

---

# 19. Kiến trúc chúng ta đang hướng tới

```text
                  Application
                       │
                       ▼
                 RenderService
                       │
              ┌────────┴────────┐
              ▼                 ▼
       RenderOptions       OutputOptions
              │                 │
              ▼                 │
        PdfRenderer             │
              │                 │
              ▼                 │
           PDFium               │
              │                 │
              ▼                 │
          PdfBitmap             │
              │                 │
              ▼                 │
          PIL.Image ────────────┘
              │
              ▼
       Image Processing
              │
              ▼
       PNG / JPEG / ...
```

Đây chính là architecture mà Mini Project ở Buổi 30 sẽ sử dụng.

---

# 20. Test Transparency

Không cần PDF thật để test phần này.

```python
from PIL import Image


def test_rgba():

    image = Image.new(
        "RGBA",
        (10, 10),
        (255, 0, 0, 128),
    )

    assert image.mode == "RGBA"

    assert image.getpixel(
        (0, 0)
    ) == (255, 0, 0, 128)
```

---

# 21. Test flatten

```python
from PIL import Image


def test_flatten_on_white():

    rgba = Image.new(
        "RGBA",
        (1, 1),
        (255, 0, 0, 128),
    )

    background = Image.new(
        "RGB",
        rgba.size,
        (255, 255, 255),
    )

    background.paste(
        rgba,
        mask=rgba.getchannel("A"),
    )

    result = background.getpixel(
        (0, 0)
    )

    assert result == (255, 127, 127)
```

Giá trị thực tế có thể chịu ảnh hưởng bởi rounding, vì vậy trong các phép tính tổng quát không nên xây test quá phụ thuộc vào một cách làm tròn cụ thể.

---

# 22. Test `RenderOptions`

```python
def test_transparent_option():

    options = RenderOptions(
        dpi=300,
        transparent=True,
    )

    assert options.dpi == 300
    assert options.transparent is True
```

---

# 23. Bài tập thực hành

## Bài 1 — RGBA

Tạo:

```text
100 × 100
RGBA
```

với:

```text
R = 255
G = 0
B = 0
A = 128
```

sau đó lưu:

```text
red-transparent.png
```

---

## Bài 2 — So sánh

Tạo hai ảnh:

```text
RGB
RGBA
```

cùng kích thước:

```text
3000 × 3000
```

và tính memory lý thuyết:

```text
RGB  = width × height × 3
RGBA = width × height × 4
```

---

## Bài 3 — PNG

Tạo một ảnh:

```text
RGBA
```

với background:

```text
transparent
```

và một hình màu ở giữa.

Lưu:

```text
output.png
```

Sau đó mở lại:

```python
image = Image.open("output.png")

print(image.mode)
```

Kiểm tra alpha:

```python
alpha = image.getchannel("A")

print(alpha.getextrema())
```

---

## Bài 4 — JPEG

Thử:

```python
image.save("output.jpg")
```

với ảnh RGBA.

Quan sát lỗi.

Sau đó sửa bằng:

```text
RGBA
 ↓
flatten on white
 ↓
RGB
 ↓
JPEG
```

---

# 24. Bài tập kiến trúc — quan trọng nhất

Thiết kế:

```python
@dataclass(frozen=True)
class RenderOptions:
    dpi: float = 150
    grayscale: bool = False
    transparent: bool = False
```

và:

```python
@dataclass(frozen=True)
class OutputOptions:
    format: str = "png"
    quality: int = 95
```

Mục tiêu:

```text
RenderOptions
    ↓
quyết định PDF được render thế nào

OutputOptions
    ↓
quyết định bitmap được encode thế nào
```

Đừng đưa:

```python
quality
```

vào `RenderOptions`.

Và cũng đừng đưa:

```python
rotation
crop
```

vào `OutputOptions`.

---

# 25. Một lỗi kiến trúc cần tránh

Không nên viết một class kiểu:

```python
class PdfEverything:

    def render(self):
        ...

    def grayscale(self):
        ...

    def rotate(self):
        ...

    def crop(self):
        ...

    def save_png(self):
        ...

    def save_jpeg(self):
        ...

    def extract_text(self):
        ...

    def extract_images(self):
        ...
```

Đây là **God Object**.

Thay vào đó:

```text
PdfRenderer
ImageProcessor
ImageCompositor
ImageEncoder
PdfTextExtractor
PdfImageReader
...
```

Mỗi thành phần có trách nhiệm rõ ràng.

---

# 26. Tổng kết Buổi 23

Ta đã xây dựng được mô hình:

```text
PDF
 │
 ▼
PDFium Rendering
 │
 ▼
Bitmap
 │
 ▼
PIL Image
 │
 ├── RGB
 │
 └── RGBA
       │
       └── Alpha
```

Và hiểu được:

### `RGB`

```text
3 channels
```

### `RGBA`

```text
4 channels
RGB + Alpha
```

### Alpha

```text
0   → transparent
255 → opaque
```

### PNG

```text
có thể giữ alpha
```

### JPEG

```text
không giữ alpha
```

### Quan trọng nhất

```text
PDF transparency
       ≠
chỉ đơn giản convert("RGBA")
```

PDFium phải xử lý transparency/compositing trong quá trình rasterization.

---

## Roadmap tiếp theo

```text
21 — Render chất lượng cao       ✓
22 — Grayscale                   ✓
23 — Transparency                ✓
24 — Rotation                    ← tiếp theo
25 — CropBox / MediaBox
26 — Page Size
27 — Coordinate System
28 — Render Region
29 — Memory Optimization
30 — PDF Thumbnail Generator
```

**Buổi 24 — Rotation** sẽ rất quan trọng vì rotation ảnh hưởng trực tiếp đến **width/height, coordinate system, crop và mapping giữa PDF point ↔ pixel**. Đây cũng là bước chuẩn bị để chúng ta xử lý render region đúng cách ở Buổi 28.
