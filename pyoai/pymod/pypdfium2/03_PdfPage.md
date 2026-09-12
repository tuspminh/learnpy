# Buổi 3 — `PdfPage`: Làm việc với từng trang PDF

Ở Buổi 2 chúng ta đã xây được:

```text
PdfDocument
    │
    ├── Page 0
    ├── Page 1
    ├── Page 2
    └── ...
```

Hôm nay chúng ta đi sâu vào **`PdfPage`**.

Mục tiêu cuối buổi:

```text
PdfDocument
     │
     ▼
  PdfPage
     │
     ├── kích thước
     ├── rotation
     ├── coordinate
     └── render
```

Đặc biệt, cuối bài bạn sẽ hiểu được nền tảng của:

```text
PDF Page
   ↓
render()
   ↓
PdfBitmap
   ↓
PIL Image
```

---

# 1. `PdfPage` là gì?

Khi viết:

```python
page = pdf[0]
```

`page` đại diện cho **một trang PDF**.

Ví dụ PDF có 100 trang:

```text
PdfDocument
│
├── PdfPage 0
├── PdfPage 1
├── PdfPage 2
├── ...
└── PdfPage 99
```

Ta có thể lấy:

```python
page = pdf[0]
```

hoặc:

```python
page = pdf[5]
```

---

# 2. Lấy kích thước trang

API quan trọng:

```python
width, height = page.get_size()
```

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    width, height = page.get_size()

    print("Width:", width)
    print("Height:", height)

finally:
    pdf.close()
```

Ví dụ:

```text
Width: 595.2755737304688
Height: 841.8897705078125
```

Đây là **PDF points**, không phải pixel.

---

# 3. PDF points

PDF thường sử dụng:

```text
72 points = 1 inch
```

Ví dụ:

```text
A4

210 mm × 297 mm
       ↓
595 × 842 points
```

Vì vậy:

```python
width, height = page.get_size()
```

không có nghĩa:

```text
595 × 842 pixels
```

mà là:

```text
595 × 842 PDF points
```

Đây là điểm rất quan trọng khi chúng ta bắt đầu render.

---

# 4. Từ PDF point sang pixel

Giả sử:

```text
Page:
595 × 842 points
```

Render ở:

```text
72 DPI
```

thì gần:

```text
595 × 842 pixels
```

Render ở:

```text
144 DPI
```

thì:

```text
1190 × 1684 pixels
```

Render ở:

```text
300 DPI
```

thì khoảng:

```text
2480 × 3508 pixels
```

Công thức:

```text
pixels = points × DPI / 72
```

Ví dụ:

```python
pixels = 595 * 300 / 72
```

≈

```text
2479 pixels
```

---

# 5. `page.get_size()` rất quan trọng cho renderer

Sau này khi chúng ta xây:

```python
class PdfRenderer:
    ...
```

renderer cần biết:

```text
Page size
    ↓
DPI
    ↓
Scale
    ↓
Bitmap size
```

Ví dụ:

```text
PDF Page
595 × 842 points

       │
       │ DPI = 150
       ▼

Bitmap
1240 × 1754 pixels
```

---

# 6. Kiểm tra tất cả page

Ta viết:

```python
import pypdfium2 as pdfium


def inspect_pages(path: str) -> None:
    pdf = pdfium.PdfDocument(path)

    try:
        for index in range(len(pdf)):
            page = pdf[index]

            width, height = page.get_size()

            print(
                f"Page {index + 1}: "
                f"{width:.2f} × {height:.2f}"
            )

    finally:
        pdf.close()


if __name__ == "__main__":
    inspect_pages("sample.pdf")
```

---

# 7. Không phải tất cả page đều cùng kích thước

Ví dụ một PDF có:

```text
Page 1 → A4
Page 2 → A4
Page 3 → A3
Page 4 → A5
Page 5 → Landscape
```

Không được giả định:

```python
width, height = 595, 842
```

Thay vào đó luôn lấy:

```python
width, height = page.get_size()
```

Đây là một nguyên tắc quan trọng khi viết PDF processor.

---

# 8. Portrait và Landscape

Ví dụ:

```text
Portrait:

width < height

595 × 842
```

Landscape:

```text
width > height

842 × 595
```

Ta có thể viết:

```python
def get_orientation(page) -> str:
    width, height = page.get_size()

    if width > height:
        return "landscape"

    if width < height:
        return "portrait"

    return "square"
```

Sử dụng:

```python
orientation = get_orientation(page)

print(orientation)
```

---

# 9. Rotation

PDF có thể có rotation.

Ví dụ:

```text
Page
 ├── physical size
 └── rotation
```

Điều này khác với việc chỉ nhìn:

```python
width, height = page.get_size()
```

Một trang có thể có:

```text
MediaBox:
595 × 842

Rotation:
90°
```

Do đó khi xây PDF viewer hoặc renderer, rotation cần được xử lý đúng.

---

# 10. Đừng nhầm rotation với resize

Ví dụ:

```text
595 × 842
```

xoay 90° về mặt hiển thị có thể trở thành:

```text
842 × 595
```

Nhưng PDF page geometry và orientation hiển thị là hai khái niệm cần phân biệt.

Tư duy:

```text
Page geometry
      +
Page rotation
      ↓
Rendered result
```

---

# 11. Render page

Đây là phần quan trọng nhất hôm nay.

`pypdfium2` cho phép render page:

```python
bitmap = page.render()
```

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    bitmap = page.render()

    print(bitmap)

finally:
    pdf.close()
```

`bitmap` lúc này **không phải PIL Image**.

Nó là bitmap do PDFium quản lý.

---

# 12. Render với scale

Ta có thể chỉ định:

```python
bitmap = page.render(
    scale=2
)
```

Ý nghĩa:

```text
scale = 1
```

là kích thước cơ bản.

```text
scale = 2
```

làm kích thước render tăng khoảng 2 lần.

```text
scale = 3
```

tăng khoảng 3 lần.

Ví dụ:

```python
bitmap = page.render(scale=2)
```

---

# 13. Scale liên quan DPI như thế nào?

Một cách tư duy dễ nhớ:

```text
scale = DPI / 72
```

Ví dụ:

### 72 DPI

```text
scale = 72 / 72
      = 1
```

### 144 DPI

```text
scale = 144 / 72
       = 2
```

### 300 DPI

```text
scale = 300 / 72
       ≈ 4.167
```

Do đó:

```python
bitmap = page.render(scale=300 / 72)
```

có thể dùng để render khoảng 300 DPI.

---

# 14. Render một trang thành PNG

Đây là chương trình rất thực tế:

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_page(
    pdf_path: str,
    page_index: int,
    output_path: str,
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

        image.save(output_path)

    finally:
        pdf.close()


if __name__ == "__main__":
    render_page(
        "sample.pdf",
        page_index=0,
        output_path="page-1.png",
        dpi=150,
    )
```

Pipeline:

```text
sample.pdf
    │
    ▼
PdfDocument
    │
    ▼
PdfPage
    │
    ▼
page.render()
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
page-1.png
```

Đây chính là pipeline cốt lõi của `pypdfium2`.

---

# 15. `to_pil()` là cầu nối rất quan trọng

Ta có:

```python
bitmap = page.render()
```

Sau đó:

```python
image = bitmap.to_pil()
```

Kết quả là:

```python
PIL.Image.Image
```

Từ đây chúng ta có thể dùng Pillow:

```python
image.save("page.png")
```

hoặc:

```python
image.resize(...)
```

hoặc:

```python
image.convert("L")
```

hoặc:

```python
image.crop(...)
```

hoặc đưa sang OCR/OpenCV.

---

# 16. Kiểm tra kích thước bitmap

Ví dụ:

```python
bitmap = page.render(scale=2)

image = bitmap.to_pil()

print(image.size)
```

Nếu page:

```text
595 × 842 points
```

thì scale 2 sẽ cho khoảng:

```text
1190 × 1684 pixels
```

---

# 17. Một ví dụ hoàn chỉnh hơn

Tạo:

```text
lesson03/
│
├── main.py
├── sample.pdf
└── output/
```

`main.py`:

```python
from pathlib import Path

import pypdfium2 as pdfium


def render_page(
    pdf_path: Path,
    page_index: int,
    output_path: Path,
    dpi: int = 150,
) -> None:

    pdf = pdfium.PdfDocument(pdf_path)

    try:
        if page_index < 0:
            raise ValueError(
                "page_index must be >= 0"
            )

        if page_index >= len(pdf):
            raise IndexError(
                f"Page index {page_index} "
                f"is out of range"
            )

        page = pdf[page_index]

        width, height = page.get_size()

        print(
            f"PDF size: "
            f"{width:.2f} × {height:.2f} points"
        )

        scale = dpi / 72

        print(f"DPI: {dpi}")
        print(f"Scale: {scale:.2f}")

        bitmap = page.render(
            scale=scale
        )

        image = bitmap.to_pil()

        print(
            f"Image size: "
            f"{image.width} × {image.height}"
        )

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


def main() -> None:

    pdf_path = Path("sample.pdf")

    render_page(
        pdf_path=pdf_path,
        page_index=0,
        output_path=Path(
            "output/page-001.png"
        ),
        dpi=150,
    )


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

Bạn sẽ có:

```text
output/
└── page-001.png
```

---

# 18. Một lỗi tư duy rất thường gặp

Không nên nghĩ:

```python
bitmap = page.render(scale=300)
```

nghĩa là:

```text
300 DPI
```

Không phải.

`scale` là hệ số scale.

Nếu muốn khoảng:

```text
300 DPI
```

thì:

```python
scale = 300 / 72
```

tức khoảng:

```text
4.1667
```

Do đó:

```python
bitmap = page.render(
    scale=300 / 72
)
```

---

# 19. DPI nên chọn bao nhiêu?

Tùy mục đích:

|     DPI | Mục đích                    |
| ------: | --------------------------- |
|      72 | preview cơ bản              |
|      96 | screen                      |
| 120–150 | preview tốt                 |
|     200 | đọc tài liệu                |
|     300 | OCR / scan tốt              |
|     600 | chất lượng rất cao, tốn RAM |

Không nên mặc định:

```python
dpi = 600
```

cho mọi PDF.

Nếu PDF 500 trang:

```text
500 pages
×
600 DPI
×
large bitmap
```

RAM có thể tăng rất nhanh.

---

# 20. Tư duy memory

Giả sử một trang render thành:

```text
2480 × 3508
```

RGBA:

```text
4 bytes / pixel
```

thì một bitmap thô khoảng:

```text
2480 × 3508 × 4
≈ 34.8 MB
```

Một lúc giữ:

```text
20 pages
```

có thể lên đến hàng trăm MB chỉ riêng bitmap.

Vì vậy pipeline production nên:

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

thay vì:

```text
Render 1
Render 2
Render 3
...
Render 100
     ↓
Process
```

Đây sẽ là một chủ đề quan trọng ở phần **Performance & Memory**.

---

# 21. Thiết kế `PageRenderer`

Chúng ta bắt đầu tách responsibility:

```python
class PdfPageRenderer:

    def render(
        self,
        page,
        dpi: int = 150,
    ):
        scale = dpi / 72

        return page.render(
            scale=scale
        )
```

Sau đó:

```python
renderer = PdfPageRenderer()

bitmap = renderer.render(
    page,
    dpi=150,
)
```

Kiến trúc:

```text
PdfDocument
     │
     ▼
 PdfPage
     │
     ▼
PdfPageRenderer
     │
     ▼
 PdfBitmap
```

Đây là bước đầu tiên để sau này chúng ta áp dụng Strategy Pattern:

```text
Renderer
   │
   ├── PdfiumRenderer
   ├── ThumbnailRenderer
   └── HighQualityRenderer
```

---

# 22. Tách `DPI → scale`

Không nên rải:

```python
dpi / 72
```

khắp project.

Tạo function:

```python
def dpi_to_scale(dpi: int) -> float:
    if dpi <= 0:
        raise ValueError(
            "DPI must be greater than 0"
        )

    return dpi / 72
```

Test:

```python
print(dpi_to_scale(72))
print(dpi_to_scale(144))
print(dpi_to_scale(300))
```

Output:

```text
1.0
2.0
4.166666666666667
```

---

# 23. Kiến trúc sau Buổi 3

Đến đây:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ├── get_size()
 │
 └── render()
          │
          ▼
      PdfBitmap
          │
          ▼
       PIL Image
```

Đây là pipeline quan trọng nhất cần nhớ.

---

# 24. Bài tập Buổi 3

### Bài 1 — Page information

Viết:

```python
def get_page_info(page):
    ...
```

trả về:

```python
{
    "width": ...,
    "height": ...,
    "orientation": ...,
}
```

---

### Bài 2 — Render theo DPI

Viết:

```python
def render_page(
    pdf_path,
    page_index,
    dpi,
):
    ...
```

Test:

```python
render_page(
    "sample.pdf",
    0,
    72,
)
```

sau đó:

```python
render_page(
    "sample.pdf",
    0,
    150,
)
```

và:

```python
render_page(
    "sample.pdf",
    0,
    300,
)
```

So sánh:

```text
72 DPI
150 DPI
300 DPI
```

về kích thước ảnh và chất lượng.

---

### Bài 3 — Render toàn bộ PDF

Viết:

```python
def render_all_pages(
    pdf_path,
    output_dir,
    dpi=150,
):
    ...
```

Kết quả:

```text
output/
├── page-001.png
├── page-002.png
├── page-003.png
├── page-004.png
└── ...
```

**Nhưng hãy render từng page → save → giải phóng**, không giữ toàn bộ bitmap trong một list.

---

## Tóm tắt Buổi 3

Bạn cần nắm chắc 6 điểm:

```python
page = pdf[0]
```

```python
width, height = page.get_size()
```

```python
bitmap = page.render(scale=2)
```

```python
image = bitmap.to_pil()
```

```python
image.save("page.png")
```

và:

```python
scale = dpi / 72
```

Pipeline:

```text
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
     ↓
PNG/JPEG/OCR/OpenCV
```

**Buổi 4** chúng ta sẽ tập trung hoàn toàn vào **`PdfBitmap`**: bitmap là gì, `to_pil()`, pixel format, alpha channel, RGB/RGBA, chuyển sang NumPy/OpenCV và cách kiểm soát memory khi xử lý bitmap.
