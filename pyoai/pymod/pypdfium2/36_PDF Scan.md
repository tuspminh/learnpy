# Buổi 36 — Xử lý PDF Scan

Hôm nay chúng ta chuyển sang một vấn đề rất quan trọng trong OCR thực tế:

> **PDF scan không phải là PDF có text — mỗi trang thường chỉ là một ảnh.**

Mục tiêu của buổi này là xây dựng pipeline xử lý **PDF scan → ảnh → tiền xử lý → OCR → text**, đồng thời chuẩn bị nền tảng cho **Buổi 37 — Detect vùng text**.

---

# 1. PDF scan là gì?

Có hai loại PDF rất dễ nhầm:

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

và lấy text trực tiếp.

### PDF scan

```text
PDF
 ├── Page 1 → Image
 ├── Page 2 → Image
 ├── Page 3 → Image
 └── ...
```

Ví dụ một cuốn sách giấy được scan:

```text
Scanner
   ↓
JPEG/PNG
   ↓
PDF
```

Trong trường hợp này:

```python
page.get_textpage()
```

có thể trả về:

```text
""
```

hoặc gần như không có text.

Nhưng:

```python
page.render(...)
```

vẫn tạo ra được hình ảnh trang.

Do đó:

```text
PDF scan
   ↓
pypdfium2
   ↓
PIL.Image
   ↓
OpenCV preprocessing
   ↓
Tesseract
   ↓
Text
```

---

# 2. Kiến trúc chúng ta muốn

Không nên viết:

```python
pdf = ...
ocr = ...
opencv = ...
```

tất cả trong một class.

Ta tiếp tục kiến trúc đã xây dựng:

```text
                 ┌───────────────┐
                 │     PDF       │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │  PdfRenderer  │
                 │  pypdfium2    │
                 └───────┬───────┘
                         ↓
                    PIL.Image
                         ↓
                 ┌───────────────┐
                 │ ImagePipeline │
                 │ Pillow/OpenCV │
                 └───────┬───────┘
                         ↓
                    PIL.Image
                         ↓
                 ┌───────────────┐
                 │ OcrEngine     │
                 │ Tesseract     │
                 └───────┬───────┘
                         ↓
                    OcrResult
                         ↓
                 ┌───────────────┐
                 │ Text Writer   │
                 └───────────────┘
```

Điểm quan trọng:

> `PdfRenderer` không biết Tesseract.

> `TesseractOcrEngine` không biết PDF.

> `OpenCVProcessor` không biết PDF.

Đây chính là **SRP + DIP**.

---

# 3. Vấn đề đặc biệt của PDF scan

Ảnh scan thường có các vấn đề:

```text
Ảnh scan
│
├── nghiêng
├── nền xám
├── nhiễu
├── bóng
├── độ tương phản thấp
├── chữ nhỏ
├── chữ mờ
├── trang bị cong
├── lề lớn
└── ảnh có nhiều vùng không phải text
```

Ví dụ:

```text
Scan gốc
   ↓
████████████████████
█                  █
█   Chương I       █
█                  █
█  Lorem ipsum...  █
█  Lorem ipsum...  █
█                  █
████████████████████
```

OCR trực tiếp:

```python
ocr.recognize(image)
```

có thể hoạt động.

Nhưng thường chất lượng chưa tối ưu.

Ta muốn:

```text
Scan
 ↓
Grayscale
 ↓
Denoise
 ↓
Contrast
 ↓
Threshold
 ↓
Deskew
 ↓
OCR
```

---

# 4. Không nên xử lý quá nhiều

Đây là một nguyên tắc rất quan trọng.

Không phải:

```text
Grayscale
 ↓
Blur
 ↓
Threshold
 ↓
Adaptive Threshold
 ↓
Morphology
 ↓
Sharpen
 ↓
Deskew
 ↓
...
```

càng nhiều bước càng tốt.

Có thể xảy ra:

```text
Ảnh tốt
 ↓
Preprocess quá mức
 ↓
Chữ bị mất
 ↓
OCR tệ hơn
```

Do đó chúng ta cần **OCR profiles**.

Ví dụ:

### Profile A

```text
Grayscale
 ↓
Otsu
 ↓
Tesseract
```

### Profile B

```text
Grayscale
 ↓
Median Blur
 ↓
Otsu
 ↓
Tesseract
```

### Profile C

```text
Grayscale
 ↓
Adaptive Threshold
 ↓
Tesseract
```

Sau này có thể:

```text
OCR profile A
      ↓
confidence = 62
      ↓
thấp
      ↓
profile B
      ↓
confidence = 87
      ↓
chọn B
```

---

# 5. Thiết kế Domain

Ta giữ domain độc lập với thư viện.

## `domain/scan.py`

```python
from dataclasses import dataclass
from enum import Enum


class ScanMode(Enum):
    AUTO = "auto"
    ORIGINAL = "original"
    GRAYSCALE = "grayscale"
    BINARY = "binary"


@dataclass(frozen=True)
class ScanOptions:
    dpi: float = 200.0
    mode: ScanMode = ScanMode.AUTO
    deskew: bool = False
    denoise: bool = False

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("dpi phải > 0")
```

Ta không import:

```python
cv2
PIL
pytesseract
pypdfium2
```

vào domain.

---

# 6. Scan Processor

Application cần một abstraction.

## `application/ports.py`

```python
from typing import Protocol

from PIL import Image

from domain.ocr import OcrResult


class ScanProcessor(Protocol):
    def process(
        self,
        image: Image.Image,
    ) -> Image.Image: ...


class OcrEngine(Protocol):
    def recognize(
        self,
        image: Image.Image,
    ) -> OcrResult: ...
```

Application chỉ biết:

```text
ScanProcessor
OcrEngine
```

không biết implementation cụ thể.

---

# 7. OpenCV Scan Processor

Bây giờ infrastructure mới được phép dùng OpenCV.

## `infrastructure/opencv/scan_processor.py`

```python
import cv2
import numpy as np

from PIL import Image


class OpenCvScanProcessor:
    def __init__(
        self,
        grayscale: bool = True,
        denoise: bool = False,
        threshold: bool = False,
    ):
        self.grayscale = grayscale
        self.denoise = denoise
        self.threshold = threshold

    def process(
        self,
        image: Image.Image,
    ) -> Image.Image:

        rgb = image.convert("RGB")

        array = np.array(rgb)

        gray = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2GRAY,
        )

        result = gray

        if self.denoise:
            result = cv2.medianBlur(
                result,
                3,
            )

        if self.threshold:
            result = cv2.threshold(
                result,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )[1]

        return Image.fromarray(result)
```

---

# 8. Test processor

Ta không cần PDF để test.

Đây là ưu điểm của kiến trúc.

## `tests/unit/test_scan_processor.py`

```python
from PIL import Image

from infrastructure.opencv.scan_processor import (
    OpenCvScanProcessor,
)


def test_grayscale():

    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    processor = OpenCvScanProcessor(
        grayscale=True,
    )

    result = processor.process(image)

    assert result.mode == "L"
    assert result.size == (100, 100)
```

Test:

```bash
pytest
```

---

# 9. Tạo Scan OCR Service

Bây giờ ghép:

```text
Renderer
   ↓
Processor
   ↓
OCR
```

## `application/scan_ocr.py`

```python
from dataclasses import dataclass

from domain.ocr import OcrResult


@dataclass(frozen=True)
class PageOcrResult:
    page_index: int
    result: OcrResult


class ScanOcrService:
    def __init__(
        self,
        renderer,
        processor,
        ocr_engine,
    ):
        self.renderer = renderer
        self.processor = processor
        self.ocr_engine = ocr_engine

    def process_page(
        self,
        page_index: int,
        render_options,
    ) -> PageOcrResult:

        image = self.renderer.render_page(
            page_index,
            render_options,
        )

        processed = None

        try:
            processed = self.processor.process(image)

            result = self.ocr_engine.recognize(processed)

            return PageOcrResult(
                page_index=page_index,
                result=result,
            )

        finally:
            image.close()

            if processed is not None:
                processed.close()
```

Đây là đoạn rất quan trọng:

```python
finally:
    image.close()

    if processed is not None:
        processed.close()
```

Bởi vì PDF scan có thể rất lớn.

Ví dụ:

```text
300 pages
×
A4
×
300 DPI
```

không thể tùy tiện giữ toàn bộ ảnh trong RAM.

---

# 10. Pipeline thực tế

Ta có thể cấu hình:

```python
processor = OpenCvScanProcessor(
    grayscale=True,
    denoise=True,
    threshold=True,
)
```

sau đó:

```python
service = ScanOcrService(
    renderer=renderer,
    processor=processor,
    ocr_engine=ocr_engine,
)
```

và:

```python
result = service.process_page(
    page_index=0,
    render_options=render_options,
)
```

Kết quả:

```python
result.result.text
```

hoặc:

```python
result.result.confidence
```

hoặc:

```python
result.result.words
```

---

# 11. Nhưng scan sách có một vấn đề lớn

Giả sử trang:

```text
┌─────────────────────────────┐
│         CHƯƠNG 1            │
│                             │
│ Lorem ipsum dolor sit amet  │
│ Lorem ipsum dolor sit amet  │
│ Lorem ipsum dolor sit amet  │
│                             │
│ Lorem ipsum dolor sit amet  │
│ Lorem ipsum dolor sit amet  │
│                             │
│              25             │
└─────────────────────────────┘
```

Tesseract nhận toàn bộ trang.

Nó có thể nhận:

```text
CHƯƠNG 1
Lorem ipsum...
...
25
```

nhưng chúng ta chưa biết:

```text
25
```

là số trang.

Cũng chưa biết:

```text
CHƯƠNG 1
```

là heading.

Cũng chưa biết:

```text
Lorem...
```

là paragraph.

Đó chính là vấn đề của **layout analysis**.

Và đây sẽ là nội dung quan trọng của:

> **Buổi 37 — Detect vùng text**

---

# 12. Scan PDF có thể có text layer giả

Một trường hợp đặc biệt:

```text
Scan Image
     +
OCR text layer
     ↓
Searchable PDF
```

Khi đó PDF nhìn như scan nhưng vẫn có:

```python
page.get_textpage()
```

và lấy được text.

Vì vậy không nên xác định:

```python
if text == "":
    chắc chắn PDF scan
```

một cách tuyệt đối.

Có thể dùng heuristic:

```text
Text layer?
    │
    ├── Có nhiều text → PDF text/searchable
    │
    └── Gần như không có
            ↓
       Render page
            ↓
       Detect image
            ↓
       OCR
```

---

# 13. Kiến trúc hoàn chỉnh sau Buổi 36

Hiện tại project của chúng ta có thể tiến tới:

```text
pdf_ocr/
│
├── domain/
│   ├── ocr.py
│   ├── options.py
│   ├── tesseract.py
│   └── scan.py
│
├── application/
│   ├── ports.py
│   ├── service.py
│   └── scan_ocr.py
│
├── infrastructure/
│   │
│   ├── pdfium/
│   │   └── renderer.py
│   │
│   ├── pillow/
│   │   └── processors.py
│   │
│   ├── opencv/
│   │   ├── processors.py
│   │   └── scan_processor.py
│   │
│   └── ocr/
│       └── tesseract.py
│
├── presentation/
│   └── cli.py
│
└── tests/
    ├── unit/
    │   ├── test_domain.py
    │   ├── test_service.py
    │   ├── test_processors.py
    │   └── test_scan_processor.py
    │
    └── integration/
        └── test_tesseract.py
```

---

# 14. Pipeline cuối cùng

Chúng ta đã đi từ:

### Buổi 31

```text
PDF
 ↓
pypdfium2
 ↓
Image
```

### Buổi 32

```text
PDF
 ↓
Image
 ↓
OCR
```

### Buổi 33

```text
PDF
 ↓
Image
 ↓
Pillow
 ↓
OCR
```

### Buổi 34

```text
PDF
 ↓
Image
 ↓
OpenCV
 ↓
OCR
```

### Buổi 35

```text
PDF
 ↓
Image
 ↓
OpenCV
 ↓
Tesseract
 ↓
OcrResult
```

### **Buổi 36**

```text
PDF Scan
    ↓
Render
    ↓
Preprocessing
    ↓
 ┌──────────────┐
 │ Grayscale    │
 │ Denoise      │
 │ Threshold    │
 │ Deskew       │
 └──────┬───────┘
        ↓
    Tesseract
        ↓
    OcrResult
```

---

# 15. Bài tập thực hành

Hãy thử cùng một trang scan với 3 profile:

### Profile 1

```text
Render 200 DPI
 ↓
Tesseract
```

### Profile 2

```text
Render 200 DPI
 ↓
Grayscale
 ↓
Tesseract
```

### Profile 3

```text
Render 200 DPI
 ↓
Grayscale
 ↓
MedianBlur
 ↓
Otsu
 ↓
Tesseract
```

So sánh:

```text
text
confidence
thời gian OCR
```

Bạn sẽ bắt đầu thấy một nguyên tắc rất quan trọng của OCR:

> **Chất lượng OCR không chỉ phụ thuộc vào Tesseract; chất lượng ảnh đầu vào thường quyết định rất nhiều.**

---

## Tóm tắt Buổi 36

Sau buổi này, chúng ta đã có tư duy đúng cho **PDF scan processing**:

```text
PDF
 │
 ├── Text layer tồn tại
 │       ↓
 │    Text extraction
 │
 └── Text layer không tồn tại
         ↓
      Render
         ↓
      Image preprocessing
         ↓
      OCR
```

Và kiến trúc:

```text
Domain
  ↑
Application
  ↑
Ports
  ↑
Infrastructure
 ├── pypdfium2
 ├── Pillow
 ├── OpenCV
 └── Tesseract
```

**Buổi tiếp theo theo đúng roadmap:**

### **Buổi 37 — Detect vùng text**

Chúng ta sẽ bắt đầu từ:

```text
Scan Page
    ↓
OpenCV
    ↓
Detect Text Region
    ↓
┌───────────┐
│ Paragraph │
│ Paragraph │
│ Heading   │
└───────────┘
    ↓
Crop từng vùng
    ↓
OCR
```

Đây là bước chuyển từ **“OCR cả trang”** sang **“phân tích bố cục trang trước khi OCR”**.
