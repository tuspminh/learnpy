# Phần IV — PDF Processing Pipeline

# Buổi 32 — PDF → OCR

Hôm nay chúng ta chuyển từ:

```text
PDF → Image
```

sang:

```text
PDF
 ↓
Render
 ↓
Image
 ↓
OCR
 ↓
Text
```

Đây là bước rất quan trọng vì từ đây `pypdfium2` không còn chỉ được dùng để xuất ảnh, mà trở thành **đầu vào cho một hệ thống xử lý tài liệu**.

---

# 1. OCR là gì?

OCR = **Optical Character Recognition**.

Nó nhận:

```text
ảnh chứa chữ
```

và cố gắng tạo:

```text
text
```

Ví dụ:

```text
PDF scan
   ↓
render page
   ↓
image
```

Ảnh:

```text
┌────────────────────────────┐
│ Chapter 1                  │
│                            │
│ The story begins here...   │
│                            │
│ He opened the door...      │
└────────────────────────────┘
```

OCR:

```text
Chapter 1

The story begins here...

He opened the door...
```

---

# 2. Tại sao pypdfium2 cần kết hợp OCR?

Một PDF có thể thuộc hai loại.

### PDF có text layer

```text
PDF
 ├── Text
 ├── Image
 └── Vector
```

Ta có thể:

```python
page.get_textpage()
```

và extract text trực tiếp.

### PDF scan

```text
PDF
 └── Image
```

Nhìn bằng mắt có chữ nhưng PDF không chứa text thực sự.

Khi đó:

```python
page.get_textpage()
```

có thể không cho kết quả hữu ích.

Ta cần:

```text
PDF
 ↓
render
 ↓
image
 ↓
OCR
 ↓
text
```

---

# 3. Kiến trúc hôm nay

Ta không muốn:

```python
class PdfiumRenderer:
    def render(self):
        ...

    def ocr(self):
        ...

    def save_text(self):
        ...
```

Đây là God Object.

Thay vào đó:

```text
                  PDF
                   │
                   ▼
             PdfRenderer
                   │
                   ▼
                Image
                   │
                   ▼
              OcrEngine
                   │
                   ▼
                 Text
```

Architecture:

```text
Presentation
     ↓
Application
     ↓
 ┌───────────────┐
 │ PdfRenderer   │
 │ OcrEngine     │
 │ TextWriter    │
 └───────────────┘
     ↑
Infrastructure
```

---

# 4. Pipeline

Ta định nghĩa pipeline:

```text
PDF
 │
 ▼
PdfiumRenderer
 │
 ▼
PIL.Image
 │
 ▼
OcrEngine
 │
 ▼
OCR Result
 │
 ▼
Text
```

Sau này sẽ phát triển thành:

```text
PDF
 ↓
Render
 ↓
Preprocess
 ↓
Detect Text Region
 ↓
OCR
 ↓
Post-process
 ↓
Store
```

---

# 5. Domain — OCR Result

Không nên để Application nhận một string đơn giản ngay từ đầu.

OCR thường có nhiều thông tin:

```text
text
confidence
bounding box
page
language
```

Ta bắt đầu bằng:

```python id="0j9o6n"
# domain/ocr.py

from dataclasses import dataclass


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float | None = None
```

Ví dụ:

```python id="2fj0ct"
result = OcrResult(
    text="Hello world",
    confidence=0.94,
)
```

---

# 6. Tại sao confidence quan trọng?

OCR không phải lúc nào cũng đúng.

Ví dụ:

```text
Original:

The quick brown fox
```

OCR có thể:

```text
The quick brown f0x
```

Confidence giúp chúng ta biết:

```text
OCR confidence = 95%
```

hay:

```text
OCR confidence = 47%
```

Sau này có thể:

```text
confidence < threshold
        ↓
retry
        ↓
preprocess mạnh hơn
```

---

# 7. OcrEngine Protocol

Đây là abstraction quan trọng nhất hôm nay.

```python id="g1tq1m"
# application/ports.py

from typing import Protocol


class OcrEngine(Protocol):

    def recognize(
        self,
        image,
    ) -> OcrResult:
        ...
```

Application chỉ biết:

```text
Image → OcrResult
```

không biết OCR engine cụ thể là gì.

---

# 8. Tại sao dùng Protocol?

Sau này chúng ta có thể có:

```text
OcrEngine
   │
   ├── TesseractOcr
   ├── EasyOcr
   ├── PaddleOcr
   └── MockOcr
```

Application:

```text
PdfOcrService
```

không cần thay đổi.

Đây chính là:

```text
DIP
+
OCP
+
Dependency Injection
```

---

# 9. Mock OCR

Trước khi cài OCR engine thật, ta có thể test bằng:

```python id="5f6n7u"
class FakeOcrEngine:

    def recognize(self, image):

        return OcrResult(
            text="fake OCR text",
            confidence=1.0,
        )
```

Điều này rất quan trọng.

Ta có thể test:

```text
PDF pipeline
```

mà không cần:

```text
Tesseract
```

---

# 10. PdfOcrService

Bây giờ xây Application Service.

```python id="txa8r4"
# application/service.py

class PdfOcrService:

    def __init__(
        self,
        renderer,
        ocr_engine,
    ):
        self.renderer = renderer
        self.ocr_engine = ocr_engine

    def recognize_page(
        self,
        page_index,
        render_options,
    ):

        image = self.renderer.render_page(
            page_index,
            render_options,
        )

        try:

            return self.ocr_engine.recognize(
                image
            )

        finally:

            image.close()
```

Flow:

```text
render
  ↓
image
  ↓
OCR
  ↓
result
  ↓
close image
```

---

# 11. Vì sao `finally` vẫn quan trọng?

OCR có thể throw exception:

```python
ocr_engine.recognize(image)
```

Ví dụ:

```text
OCR engine error
```

Nếu không quản lý lifetime:

```text
image
 ↓
OCR exception
 ↓
image vẫn tồn tại
```

Ta dùng:

```python
try:
    ...
finally:
    image.close()
```

để đảm bảo:

```text
success → close
error   → close
```

---

# 12. OCR toàn bộ PDF

Ta thêm:

```python id="b1kl5v"
def iter_pages(
    self,
    render_options,
    start_page=0,
    end_page=None,
):

    if end_page is None:
        end_page = self.renderer.page_count

    for page_index in range(
        start_page,
        end_page,
    ):

        result = self.recognize_page(
            page_index,
            render_options,
        )

        yield page_index, result
```

Sử dụng:

```python id="i0s5g3"
for page_index, result in service.iter_pages(
    render_options
):

    print(
        page_index,
        result.text,
    )
```

Đây là:

```text
streaming OCR
```

---

# 13. Memory model

Ta không làm:

```python id="8s7g6r"
images = []

for page in pages:
    images.append(
        renderer.render_page(...)
    )
```

Cũng không:

```python id="2ebs6a"
results = [
    ocr(image)
    for image in images
]
```

Mà:

```text
Page 1
 ↓
Image
 ↓
OCR
 ↓
Text
 ↓
release Image
 ↓
Page 2
```

Memory gần với:

```text
O(1)
```

theo số page, thay vì giữ toàn bộ ảnh.

---

# 14. OCR text có nên lưu ngay?

Có hai chiến lược.

### Strategy A — streaming

```text
Page
 ↓
OCR
 ↓
write
 ↓
next page
```

Phù hợp PDF lớn.

### Strategy B — collect

```text
Page
 ↓
OCR
 ↓
results.append()
```

Phù hợp PDF nhỏ hoặc khi cần xử lý toàn bộ kết quả sau đó.

Với PDF scan lớn, ưu tiên:

```text
streaming
```

---

# 15. TextWriter

Ta tạo:

```python id="j04y8j"
# infrastructure/text_writer.py

from pathlib import Path


class TextFileWriter:

    def __init__(self, output_path):

        self.output_path = Path(
            output_path
        )

    def write_page(
        self,
        page_index,
        result,
    ):

        with self.output_path.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                f"\n===== PAGE "
                f"{page_index + 1} =====\n"
            )

            f.write(
                result.text
            )

            f.write("\n")
```

Kết quả:

```text
output.txt
```

```text
===== PAGE 1 =====

Chapter One

The story begins...


===== PAGE 2 =====

The door opened slowly...
```

---

# 16. Nhưng mở file mỗi page không tối ưu

Code trên rất dễ hiểu để học, nhưng nếu 10.000 pages:

```text
page 1 → open/close
page 2 → open/close
page 3 → open/close
...
```

không lý tưởng.

Ta nên có:

```python id="ezgyrf"
class StreamingTextWriter:

    def __init__(self, output_path):

        self.output_path = Path(
            output_path
        )

        self._file = None

    def open(self):

        self._file = self.output_path.open(
            "w",
            encoding="utf-8",
        )

    def write_page(
        self,
        page_index,
        result,
    ):

        if self._file is None:
            raise RuntimeError(
                "Writer chưa mở"
            )

        self._file.write(
            f"\n===== PAGE "
            f"{page_index + 1} =====\n"
        )

        self._file.write(
            result.text
        )

        self._file.write("\n")

    def close(self):

        if self._file is not None:
            self._file.close()
            self._file = None

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

---

# 17. Pipeline hoàn chỉnh

```python id="n0k8vh"
def run_ocr(
    service,
    writer,
    render_options,
):

    with writer:

        for page_index, result in (
            service.iter_pages(
                render_options
            )
        ):

            writer.write_page(
                page_index,
                result,
            )
```

Flow:

```text
             PDF
              │
              ▼
         PdfRenderer
              │
              ▼
           Image
              │
              ▼
          OcrEngine
              │
              ▼
         OcrResult
              │
              ▼
        StreamingWriter
              │
              ▼
          output.txt
```

---

# 18. Đây là Clean Architecture

Dependency:

```text
                  Domain
                    ↑
                    │
               Application
                    ↑
                    │
              Infrastructure
                    ↑
                    │
              Presentation
```

Trong thực tế dependency direction nên hiểu là:

```text
Presentation
     ↓
Application
     ↓
Domain

Infrastructure
     ↓
Application interfaces
```

Application không import:

```python
import pytesseract
```

đây là điểm cực kỳ quan trọng.

---

# 19. OCR engine thật

Ở Buổi 35 chúng ta sẽ học:

```text
pypdfium2
+
Tesseract
```

Nhưng hôm nay cần hiểu interface trước.

Ví dụ một adapter Tesseract về sau có thể có:

```python
class TesseractOcrEngine:

    def __init__(
        self,
        language="eng",
    ):
        self.language = language

    def recognize(self, image):

        ...
```

Application không cần biết implementation bên trong.

---

# 20. Tại sao không tích hợp Tesseract ngay hôm nay?

Vì roadmap của chúng ta cố ý tách:

```text
32 PDF → OCR
33 pypdfium2 + Pillow
34 pypdfium2 + OpenCV
35 pypdfium2 + Tesseract
```

Buổi 32 tập trung vào:

```text
OCR architecture
pipeline
lifetime
streaming
```

Buổi 35 mới đi sâu:

```text
Tesseract API
language
PSM
OEM
confidence
bounding boxes
```

Như vậy kiến thức không bị trộn.

---

# 21. OCR không chỉ là `image → text`

Một OCR engine thực tế thường có pipeline:

```text
Image
 ↓
Preprocessing
 ↓
Segmentation
 ↓
Recognition
 ↓
Post-processing
```

Ví dụ:

```text
ảnh scan xấu
     ↓
grayscale
     ↓
denoise
     ↓
threshold
     ↓
deskew
     ↓
OCR
     ↓
text cleanup
```

Chúng ta sẽ học phần preprocessing qua:

```text
33 Pillow
34 OpenCV
```

---

# 22. Chất lượng OCR phụ thuộc image

Đây là nguyên tắc cực kỳ quan trọng:

> OCR tốt hay xấu không chỉ phụ thuộc OCR engine; chất lượng ảnh đầu vào có ảnh hưởng rất lớn.

Ví dụ:

```text
300 DPI
```

không đồng nghĩa luôn tốt hơn:

```text
150 DPI
```

Nếu scan bị:

```text
noise
blur
skew
low contrast
background
```

thì OCR vẫn có thể rất kém.

Do đó pipeline:

```text
PDF
 ↓
Render
 ↓
Image preprocessing
 ↓
OCR
```

thường tốt hơn:

```text
PDF
 ↓
Render
 ↓
OCR
```

---

# 23. DPI cho OCR

Thumbnail:

```text
~40–100 DPI
```

thường có thể đủ.

OCR:

```text
150–300 DPI
```

thường là vùng thực tế phổ biến cho tài liệu chữ, nhưng DPI tối ưu còn phụ thuộc font, scan và OCR engine.

Ví dụ:

```text
PDF
 ↓
150 DPI
 ↓
OCR
```

có thể đủ.

Nếu chữ nhỏ:

```text
PDF
 ↓
300 DPI
 ↓
OCR
```

có thể cho kết quả tốt hơn.

Nhưng:

```text
DPI ↑
```

thì:

```text
pixels ↑
RAM ↑
CPU ↑
OCR time ↑
```

Do đó phải cân bằng.

---

# 24. Một công thức quan trọng

Ta đã học:

```text
scale = DPI / 72
```

Ví dụ:

```python
options = RenderOptions(
    dpi=200
)
```

thì:

```text
scale ≈ 2.7778
```

Render:

```python
page.render(
    scale=options.scale
)
```

Sau đó:

```text
PdfBitmap
 ↓
PIL.Image
 ↓
OCR
```

---

# 25. OCR page range

Không phải lúc nào cũng OCR toàn bộ PDF.

Ví dụ:

```bash
pdf-ocr book.pdf --start 10 --end 20
```

Flow:

```text
page 10
 ↓
OCR

...

page 20
 ↓
OCR
```

Và nên giữ convention:

```text
CLI:
1-based inclusive

Application:
0-based [start, end)
```

giống project PDF Image hôm nay.

---

# 26. Test bằng Fake OCR

Đây là test quan trọng nhất.

```python id="v1sm5q"
class FakeOcrEngine:

    def recognize(self, image):

        return OcrResult(
            text="Hello OCR",
            confidence=1.0,
        )
```

Fake renderer:

```python id="2e2b0s"
from PIL import Image


class FakeRenderer:

    page_count = 2

    def render_page(
        self,
        page_index,
        options,
    ):

        return Image.new(
            "RGB",
            (100, 100),
        )
```

---

# 27. Test `recognize_page`

```python id="9ud9sy"
def test_recognize_page():

    renderer = FakeRenderer()

    ocr = FakeOcrEngine()

    service = PdfOcrService(
        renderer=renderer,
        ocr_engine=ocr,
    )

    result = service.recognize_page(
        page_index=0,
        render_options=RenderOptions(),
    )

    assert result.text == (
        "Hello OCR"
    )

    assert result.confidence == 1.0
```

Application test hoàn toàn không cần:

```text
Tesseract
PDF file
GPU
OpenCV
```

Đây chính là lợi ích của Dependency Injection.

---

# 28. Test nhiều page

```python id="0w1tqf"
def test_iter_pages():

    renderer = FakeRenderer()

    ocr = FakeOcrEngine()

    service = PdfOcrService(
        renderer=renderer,
        ocr_engine=ocr,
    )

    results = list(
        service.iter_pages(
            render_options=RenderOptions()
        )
    )

    assert len(results) == 2

    assert results[0][0] == 0
    assert results[1][0] == 1

    assert results[0][1].text == (
        "Hello OCR"
    )
```

Ở production, không nhất thiết phải:

```python
list(...)
```

vì như vậy lại collect toàn bộ kết quả.

Có thể:

```python
for page_index, result in service.iter_pages(...):
    writer.write_page(...)
```

---

# 29. Streaming OCR thực sự

Đây là pipeline chúng ta muốn:

```python
for page_index, result in service.iter_pages(
    render_options
):
    writer.write_page(
        page_index,
        result,
    )
```

Memory:

```text
Page 1 Image
    ↓
OCR
    ↓
Result
    ↓
write
    ↓
Image release

Page 2
    ↓
...
```

Không:

```text
results = []
```

cho hàng nghìn page.

---

# 30. Có thể lưu metadata

Sau này `OcrResult` có thể mở rộng:

```python
@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float | None
    language: str | None
    processing_time: float | None
```

và:

```text
page_index
page_number
width
height
dpi
```

Nhưng hiện tại chưa nên over-engineer.

---

# 31. OCR có thể trả bounding boxes

Đây là bước nối trực tiếp tới **Buổi 37 — Detect vùng text**.

Thay vì:

```text
OcrResult
    text
```

ta có:

```text
OcrResult
    │
    ├── text
    └── words
         ├── word
         ├── confidence
         └── bbox
```

Ví dụ:

```text
┌──────────────────────────────┐
│ Chapter One                  │
│ ┌───────┐                    │
│ │Chapter│                    │
│ └───────┘                    │
│                              │
│ The story begins...          │
└──────────────────────────────┘
```

OCR engine có thể biết:

```text
Chapter
bbox=(...)
confidence=98%
```

Đây sẽ rất hữu ích cho:

```text
highlight
search
click
text selection
OCR overlay
```

---

# 32. Coordinate system quay trở lại

Bạn đã học Buổi 27:

```text
PDF coordinates
bottom-left origin
```

Nhưng OCR thường trả:

```text
image coordinates
top-left origin
```

Do đó pipeline:

```text
PDF
 ↓
PDF coordinate
 ↓
render
 ↓
image coordinate
 ↓
OCR bounding box
```

sẽ cần chuyển đổi coordinate nếu muốn overlay OCR lên PDF.

Đây là lý do Buổi 27 không phải kiến thức riêng lẻ.

---

# 33. PDF OCR Reader architecture

Sau này có thể xây:

```text
PDF
 │
 ▼
PdfiumRenderer
 │
 ▼
Image
 │
 ▼
Preprocessor
 │
 ▼
OcrEngine
 │
 ▼
OcrResult
 │
 ├── text
 ├── words
 ├── confidence
 └── bounding boxes
```

Rồi:

```text
OcrResult
 ↓
TextRepository
 ↓
SQLite
```

Điều này cực kỳ gần với architecture của ứng dụng crawler/reader mà bạn đang xây.

---

# 34. So sánh Text Extraction và OCR

|               | Text Extraction      | OCR                   |
| ------------- | -------------------- | --------------------- |
| Input         | PDF text layer       | Image                 |
| Render        | Không nhất thiết     | Có                    |
| Tốc độ        | Thường nhanh         | Chậm hơn              |
| Scan PDF      | Không phù hợp        | Phù hợp               |
| Bbox          | Có thể lấy từ PDFium | OCR engine có thể trả |
| Font          | Có thể lấy           | Không có font PDF     |
| Confidence    | Thường không có      | Có                    |
| Preprocessing | Ít                   | Rất quan trọng        |

Pipeline:

```text
PDF có text
    ↓
TextPage
    ↓
Text
```

Trong khi scan:

```text
PDF
 ↓
Render
 ↓
Image
 ↓
OCR
 ↓
Text
```

---

# 35. Một hệ thống thực tế có thể tự quyết định

Sau này ta có thể làm:

```text
PDF Page
   │
   ▼
Có text layer?
   │
 ┌─┴───────┐
 │         │
Yes       No
 │         │
 ▼         ▼
Text     Render
Extract    │
 │         ▼
 │        OCR
 └────┬────┘
      ▼
 Unified Text
```

Đây là một architecture rất mạnh cho PDF Reader.

---

# 36. Bài tập thực hành

### Bài 1

Tạo:

```python
OcrResult
```

với:

```text
text
confidence
```

---

### Bài 2

Tạo:

```python
OcrEngine Protocol
```

---

### Bài 3

Tạo:

```python
FakeOcrEngine
```

trả:

```text
"Hello OCR"
```

---

### Bài 4

Hoàn thành:

```python
PdfOcrService
```

với:

```python
recognize_page()
iter_pages()
```

---

### Bài 5

Tạo:

```python
StreamingTextWriter
```

và chạy:

```text
PDF
 ↓
render
 ↓
fake OCR
 ↓
output.txt
```

---

# 37. Bài tập nâng cao

Thêm:

```text
--dpi
--start
--end
--output
```

Ví dụ:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --start 1 \
    --end 20 \
    --output result.txt
```

Architecture:

```text
CLI
 ↓
PdfOcrService
 ├── PdfRenderer
 └── OcrEngine
       ↓
   OcrResult
       ↓
 TextWriter
```

---

# 38. Roadmap sau Buổi 32

```text
31. PDF → Image                  ✅
32. PDF → OCR                    ✅
33. pypdfium2 + Pillow           ⬜
34. pypdfium2 + OpenCV           ⬜
35. pypdfium2 + Tesseract        ⬜
36. Xử lý PDF scan               ⬜
37. Detect vùng text             ⬜
38. Parallel rendering           ⬜
39. Streaming / batch processing ⬜
40. Mini Project: PDF OCR        ⬜
```

### Tư duy quan trọng nhất của Buổi 32

Đừng xem OCR là:

```python
text = ocr(image)
```

Hãy xem nó là một **pipeline có thể thay thế từng adapter**:

```text
                    PDF
                     │
                     ▼
                PdfRenderer
                     │
                     ▼
                PIL.Image
                     │
                     ▼
              ImageProcessor
                     │
                     ▼
                 OcrEngine
                     │
                     ▼
                OcrResult
                     │
                     ▼
                TextWriter
```

Trong bài tiếp theo, **Buổi 33 — pypdfium2 + Pillow**, chúng ta sẽ đi sâu vào phần `ImageProcessor`: grayscale, contrast, resize, sharpen, threshold và các kỹ thuật tiền xử lý ảnh bằng Pillow để chuẩn bị ảnh tốt hơn cho OCR.
