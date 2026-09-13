# Phần IV — PDF Processing Pipeline

# Buổi 33 — pypdfium2 + Pillow

Ở Buổi 32 chúng ta đã xây:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
OCR
 ↓
Text
```

Hôm nay tập trung vào phần:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
Image Processing
```

Mục tiêu là xây một **Image Processing Layer** đủ sạch để Buổi 35 có thể cắm Tesseract vào mà không phải sửa kiến trúc.

---

# 1. Vì sao cần Pillow?

`pypdfium2` rất mạnh ở:

```text
PDF → Bitmap
```

Nhưng sau khi đã có:

```python
PIL.Image
```

thì Pillow phù hợp hơn cho:

* grayscale
* resize
* contrast
* brightness
* sharpen
* rotate
* crop
* threshold
* format conversion
* save PNG/JPEG
* một số thao tác alpha

Kiến trúc:

```text
pypdfium2
     │
     ▼
Bitmap
     │
     ▼
PIL.Image
     │
     ▼
Pillow
     │
     ├── grayscale
     ├── contrast
     ├── sharpen
     ├── resize
     └── threshold
```

---

# 2. Pillow không phải OCR

Đây là ranh giới cần giữ rõ.

Pillow:

```text
Image → Image
```

OCR:

```text
Image → Text
```

Vì vậy:

```text
PdfRenderer
     ↓
PIL.Image
     ↓
ImageProcessor
     ↓
PIL.Image
     ↓
OcrEngine
     ↓
OcrResult
```

Không nên:

```text
PillowProcessor
      ↓
Tesseract
```

trong cùng một class.

Đó là hai responsibility khác nhau.

---

# 3. Cài Pillow

Nếu chưa có:

```bash
pip install pillow
```

Kiểm tra:

```bash
python -c "from PIL import Image; print(Image.__version__)"
```

---

# 4. ImageProcessor Protocol

Từ Buổi 32 chúng ta đã có ý tưởng:

```python
class ImageProcessor(Protocol):

    def process(self, image):
        ...
```

Nhưng hôm nay ta cần thiết kế tốt hơn.

Một processor:

```text
Image → Image
```

Ví dụ:

```python
image = processor.process(image)
```

---

# 5. Processor đầu tiên — Grayscale

```python
from PIL import Image


class GrayscaleProcessor:

    def process(self, image: Image.Image) -> Image.Image:
        return image.convert("L")
```

Input:

```text
RGB
```

Output:

```text
L
```

Pillow mode:

```text
RGB = 3 channels
L   = grayscale 8-bit
RGBA = RGB + alpha
```

---

# 6. Test Grayscale

```python
from PIL import Image


def test_grayscale():

    image = Image.new(
        "RGB",
        (100, 100),
    )

    processor = GrayscaleProcessor()

    result = processor.process(image)

    assert result.mode == "L"
    assert result.size == (100, 100)
```

---

# 7. Contrast

Scan PDF đôi khi có:

```text
chữ xám
nền xám
```

Ví dụ:

```text
Original
────────────────
dark gray text
light gray background
────────────────
```

Tăng contrast có thể giúp OCR.

Pillow cung cấp:

```python
from PIL import ImageEnhance
```

Ta xây:

```python
class ContrastProcessor:

    def __init__(self, factor: float = 1.5):
        if factor <= 0:
            raise ValueError(
                "contrast factor phải > 0"
            )

        self.factor = factor

    def process(self, image):

        enhancer = ImageEnhance.Contrast(
            image
        )

        return enhancer.enhance(
            self.factor
        )
```

---

# 8. Hiểu `factor`

Ví dụ:

```text
factor = 1.0
```

giữ nguyên.

```text
factor > 1
```

tăng contrast.

```text
factor < 1
```

giảm contrast.

Ví dụ:

```python
ContrastProcessor(1.5)
```

hoặc:

```python
ContrastProcessor(2.0)
```

Không nên mặc định tăng quá mạnh vì có thể làm mất nét chữ.

---

# 9. Brightness

Pillow cũng có:

```python
ImageEnhance.Brightness
```

Ta xây:

```python
class BrightnessProcessor:

    def __init__(self, factor: float = 1.0):

        if factor <= 0:
            raise ValueError(
                "brightness factor phải > 0"
            )

        self.factor = factor

    def process(self, image):

        enhancer = ImageEnhance.Brightness(
            image
        )

        return enhancer.enhance(
            self.factor
        )
```

Ví dụ:

```python
BrightnessProcessor(1.2)
```

làm ảnh sáng hơn.

---

# 10. Sharpen

Scan bị hơi mờ:

```text
PDF scan
   ↓
render
   ↓
ảnh hơi blur
```

Có thể thử:

```python
from PIL import ImageEnhance


class SharpenProcessor:

    def __init__(self, factor: float = 1.5):

        if factor < 0:
            raise ValueError(
                "sharpen factor phải >= 0"
            )

        self.factor = factor

    def process(self, image):

        enhancer = ImageEnhance.Sharpness(
            image
        )

        return enhancer.enhance(
            self.factor
        )
```

---

# 11. Resize

OCR không phải lúc nào cũng cần ảnh cực lớn.

Ta có thể resize:

```python
from PIL import Image


class ResizeProcessor:

    def __init__(
        self,
        width: int,
        height: int,
    ):

        if width <= 0:
            raise ValueError(
                "width phải > 0"
            )

        if height <= 0:
            raise ValueError(
                "height phải > 0"
            )

        self.width = width
        self.height = height

    def process(self, image):

        return image.resize(
            (self.width, self.height),
            Image.Resampling.LANCZOS,
        )
```

Nhưng **không nên resize tùy tiện làm méo ảnh**.

Ví dụ:

```text
2480 × 3508
```

không nên biến thành:

```text
1000 × 1000
```

vì aspect ratio bị phá.

---

# 12. Resize giữ tỷ lệ

Tốt hơn là:

```python
class FitWidthProcessor:

    def __init__(self, width: int):

        if width <= 0:
            raise ValueError(
                "width phải > 0"
            )

        self.width = width

    def process(self, image):

        ratio = (
            self.width / image.width
        )

        height = round(
            image.height * ratio
        )

        return image.resize(
            (self.width, height),
            Image.Resampling.LANCZOS,
        )
```

Ví dụ:

```text
2480 × 3508
```

fit width:

```text
1200 × 1697
```

Aspect ratio được giữ nguyên.

---

# 13. Threshold

Đây là thao tác rất quan trọng khi xử lý scan.

Grayscale:

```text
0 ─────────────────── 255
black                white
```

Threshold biến thành:

```text
0
255
```

Ví dụ:

```text
pixel < 160 → black
pixel >=160 → white
```

Pillow có thể dùng:

```python
image.point(...)
```

Ta xây:

```python
class ThresholdProcessor:

    def __init__(self, threshold: int = 160):

        if not 0 <= threshold <= 255:
            raise ValueError(
                "threshold phải nằm trong [0, 255]"
            )

        self.threshold = threshold

    def process(self, image):

        grayscale = image.convert("L")

        return grayscale.point(
            lambda value:
                255 if value >= self.threshold
                else 0
        )
```

---

# 14. Grayscale và threshold khác nhau

Grayscale:

```text
0
10
40
80
120
160
200
240
255
```

Threshold:

```text
0
255
```

Do đó:

```text
Grayscale
```

giữ lại nhiều thông tin hơn.

Threshold:

```text
```

```text
đen / trắng
```

có thể rất hữu ích cho OCR nhưng cũng có thể làm mất chi tiết.

---

# 15. Pipeline nhiều Processor

Đây là phần quan trọng nhất.

Ta không muốn:

```python
class OcrImageProcessor:

    def process(self):
        grayscale()
        contrast()
        sharpen()
        threshold()
        resize()
```

Vì class này sẽ ngày càng phình to.

Ta xây:

```python
class ImagePipeline:

    def __init__(self, processors):

        self.processors = list(processors)

    def process(self, image):

        current = image

        for processor in self.processors:

            current = processor.process(
                current
            )

        return current
```

---

# 16. Sử dụng Pipeline

```python
pipeline = ImagePipeline([
    GrayscaleProcessor(),
    ContrastProcessor(1.5),
    SharpenProcessor(1.5),
])
```

Sau đó:

```python
processed = pipeline.process(
    image
)
```

Flow:

```text
Image
 ↓
Grayscale
 ↓
Contrast
 ↓
Sharpen
 ↓
Image
```

---

# 17. Pipeline OCR thực tế

Ví dụ:

```python
pipeline = ImagePipeline([
    GrayscaleProcessor(),
    ContrastProcessor(1.4),
    SharpenProcessor(1.3),
])
```

Sau đó:

```python
processed = pipeline.process(image)

result = ocr_engine.recognize(
    processed
)
```

Pipeline:

```text
PDF
 ↓
pypdfium2
 ↓
RGB Image
 ↓
Grayscale
 ↓
Contrast
 ↓
Sharpen
 ↓
OCR
 ↓
Text
```

---

# 18. Một vấn đề quan trọng: memory

Có một lỗi dễ mắc.

Nếu processor tạo image mới:

```python
return image.convert("L")
```

thì:

```text
old image
+
new image
```

có thể cùng tồn tại trong một khoảng thời gian.

Pipeline:

```text
RGB
 ↓
L
 ↓
contrast image
 ↓
sharpen image
```

có thể tạo nhiều object.

Do đó ở mức production, ta cần quản lý lifetime cẩn thận.

---

# 19. Cách thiết kế service

Từ Buổi 32:

```text
renderer
ocr_engine
```

Bây giờ thêm:

```text
image_processor
```

Ta có:

```python
class PdfOcrService:

    def __init__(
        self,
        renderer,
        image_processor,
        ocr_engine,
    ):

        self.renderer = renderer
        self.image_processor = (
            image_processor
        )
        self.ocr_engine = ocr_engine
```

---

# 20. `recognize_page()`

```python
def recognize_page(
    self,
    page_index,
    render_options,
):

    image = self.renderer.render_page(
        page_index,
        render_options,
    )

    processed = None

    try:

        processed = (
            self.image_processor.process(
                image
            )
        )

        return self.ocr_engine.recognize(
            processed
        )

    finally:

        if processed is not None:
            processed.close()

        image.close()
```

Điểm cần chú ý:

```text
image
processed
```

là hai resource có thể cần release.

---

# 21. Nhưng processor có thể trả lại chính image

Ví dụ:

```python
class NoOpProcessor:

    def process(self, image):
        return image
```

Lúc này:

```text
image is processed
```

Nếu ta:

```python
processed.close()
image.close()
```

thì cùng một object bị close hai lần.

Pillow thường chịu được nhiều trường hợp, nhưng **thiết kế lifetime rõ ràng vẫn tốt hơn**.

Ta có thể xử lý:

```python
if processed is not image:
    processed.close()

image.close()
```

---

# 22. Service hoàn chỉnh

```python
class PdfOcrService:

    def __init__(
        self,
        renderer,
        image_processor,
        ocr_engine,
    ):

        self.renderer = renderer
        self.image_processor = (
            image_processor
        )
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

        processed = image

        try:

            processed = (
                self.image_processor.process(
                    image
                )
            )

            return self.ocr_engine.recognize(
                processed
            )

        finally:

            if processed is not image:
                processed.close()

            image.close()

    def iter_pages(
        self,
        render_options,
        start_page=0,
        end_page=None,
    ):

        if end_page is None:
            end_page = self.renderer.page_count

        if start_page < 0:
            raise ValueError(
                "start_page phải >= 0"
            )

        if end_page > self.renderer.page_count:
            raise ValueError(
                "end_page vượt quá page_count"
            )

        if start_page >= end_page:
            raise ValueError(
                "start_page phải < end_page"
            )

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

---

# 23. Nhưng có thể tối ưu thêm

Một số Pillow operation tạo image mới:

```text
convert()
resize()
point()
```

Trong khi một số operation có thể mutate image tùy API.

Ta không nên giả định:

```text
processor luôn tạo image mới
```

hoặc:

```text
processor luôn mutate
```

Interface nên quy định rõ convention.

Đối với project này, convention đơn giản:

> `ImageProcessor.process()` trả về một `Image`; processor có thể tạo image mới hoặc trả lại image cũ.

Application chịu trách nhiệm quản lý resource.

---

# 24. Port hoàn chỉnh

```python
from typing import Protocol


class ImageProcessor(Protocol):

    def process(self, image):
        """
        Nhận PIL.Image và trả về PIL.Image.
        """
        ...
```

Ta có:

```text
ImageProcessor
      │
      ├── NoOpProcessor
      ├── GrayscaleProcessor
      ├── ContrastProcessor
      ├── SharpenProcessor
      ├── ThresholdProcessor
      └── ImagePipeline
```

---

# 25. Project structure

Sau Buổi 33, project nên phát triển thành:

```text
pdf_ocr/
│
├── domain/
│   ├── __init__.py
│   ├── ocr.py
│   └── options.py
│
├── application/
│   ├── __init__.py
│   ├── ports.py
│   └── service.py
│
├── infrastructure/
│   ├── __init__.py
│   │
│   ├── pdfium/
│   │   ├── __init__.py
│   │   └── renderer.py
│   │
│   ├── pillow/
│   │   ├── __init__.py
│   │   ├── processors.py
│   │   └── pipeline.py
│   │
│   └── ocr/
│       └── ...
│
├── presentation/
│   ├── __init__.py
│   └── cli.py
│
└── tests/
    ├── test_processors.py
    ├── test_pipeline.py
    └── test_service.py
```

---

# 26. Test Pipeline

```python
from PIL import Image


def test_pipeline():

    image = Image.new(
        "RGB",
        (100, 100),
    )

    pipeline = ImagePipeline([
        GrayscaleProcessor(),
        ContrastProcessor(1.5),
        SharpenProcessor(1.2),
    ])

    result = pipeline.process(image)

    assert result.mode == "L"
    assert result.size == (100, 100)

    result.close()
    image.close()
```

---

# 27. Test Threshold

```python
from PIL import Image


def test_threshold():

    image = Image.new(
        "L",
        (2, 1),
    )

    image.putdata([
        50,
        200,
    ])

    processor = ThresholdProcessor(
        threshold=128
    )

    result = processor.process(
        image
    )

    assert list(result.getdata()) == [
        0,
        255,
    ]

    result.close()
    image.close()
```

---

# 28. Test Fake OCR

Kết hợp với Buổi 32:

```python
class FakeOcrEngine:

    def recognize(self, image):

        assert image.mode == "L"

        return OcrResult(
            text="Hello OCR",
            confidence=1.0,
        )
```

Service:

```python
service = PdfOcrService(
    renderer=fake_renderer,
    image_processor=ImagePipeline([
        GrayscaleProcessor(),
    ]),
    ocr_engine=FakeOcrEngine(),
)
```

Như vậy ta test được toàn bộ:

```text
Renderer
 ↓
Processor
 ↓
OCR
```

mà không cần Tesseract.

---

# 29. CLI nên cho phép chọn pipeline

Sau này CLI có thể:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --grayscale \
    --contrast 1.5 \
    --sharpen 1.3 \
    --output result.txt
```

Application nhận:

```text
RenderOptions
+
ImagePipeline
+
OcrEngine
```

CLI chỉ có nhiệm vụ:

```text
parse arguments
      ↓
construct dependencies
      ↓
call service
```

Không xử lý ảnh trực tiếp.

---

# 30. Một pipeline tốt không phải pipeline nhiều bước nhất

Không nên mặc định:

```text
grayscale
 ↓
brightness
 ↓
contrast
 ↓
sharpen
 ↓
threshold
 ↓
resize
 ↓
...
```

vì nhiều preprocessing có thể **làm OCR tệ hơn**.

Ví dụ:

```text
Ảnh tốt
 ↓
threshold quá mạnh
 ↓
chữ mảnh biến mất
```

Hoặc:

```text
Ảnh hơi noisy
 ↓
sharpen quá mạnh
 ↓
noise trở nên rõ hơn
```

Do đó preprocessing phải dựa trên loại tài liệu.

---

# 31. Các profile OCR

Đây là cách thiết kế tốt hơn.

Ví dụ:

```text
DocumentProfile
```

### Profile 1 — PDF text scan sạch

```text
grayscale
```

### Profile 2 — Scan hơi mờ

```text
grayscale
 ↓
contrast
 ↓
sharpen
```

### Profile 3 — Scan nền xám

```text
grayscale
 ↓
contrast
 ↓
threshold
```

### Profile 4 — Chữ nhỏ

```text
grayscale
 ↓
resize 1.5x
 ↓
sharpen
```

Sau này ta có thể cấu hình bằng CLI/config thay vì hard-code.

---

# 32. Resize trước hay sau OCR?

Thông thường:

```text
PDF
 ↓
render DPI phù hợp
 ↓
preprocess
 ↓
OCR
```

không nên:

```text
render 300 DPI
 ↓
resize xuống rất nhỏ
 ↓
OCR
```

nếu mục tiêu ban đầu chỉ là OCR ở kích thước nhỏ.

Tốt hơn là chọn DPI render phù hợp ngay từ đầu.

Ví dụ:

```text
DPI 300
```

tạo ảnh rất lớn:

```text
A4 ≈ 2480 × 3508
```

Nếu OCR engine chỉ cần khoảng 1800 px chiều rộng, render quá lớn sẽ tốn:

```text
RAM
CPU
I/O
OCR time
```

---

# 33. Pipeline hoàn chỉnh sau Buổi 33

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
                ImagePipeline
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Grayscale    Contrast    Sharpen
          │           │           │
          └───────────┼───────────┘
                      ▼
                  PIL.Image
                      │
                      ▼
                   OCR
                      │
                      ▼
                 OcrResult
                      │
                      ▼
                TextWriter
```

Đây chính là kiến trúc chúng ta sẽ tiếp tục mở rộng.

---

# 34. Quan trọng: phân biệt 4 layer

Sau 33, bạn nên nhớ:

### PDF rendering

```text
pypdfium2
```

chịu trách nhiệm:

```text
PDF → Image
```

### Image processing

```text
Pillow
```

chịu trách nhiệm:

```text
Image → Image
```

### OCR

```text
Tesseract / EasyOCR / ...
```

chịu trách nhiệm:

```text
Image → Text
```

### Application

```text
PdfOcrService
```

chịu trách nhiệm orchestration:

```text
Render
 → Process
 → OCR
 → Release
```

Không trộn bốn trách nhiệm này vào một class.

---

# 35. Roadmap hiện tại

```text
31. PDF → Image                  ✅
32. PDF → OCR                    ✅
33. pypdfium2 + Pillow           ✅
34. pypdfium2 + OpenCV           ⬜
35. pypdfium2 + Tesseract        ⬜
36. Xử lý PDF scan               ⬜
37. Detect vùng text             ⬜
38. Parallel rendering           ⬜
39. Streaming / batch processing ⬜
40. Mini Project: PDF OCR        ⬜
```

## Kiến thức cốt lõi của Buổi 33

Hãy ghi nhớ mô hình:

```text
pypdfium2
    ↓
PIL.Image
    ↓
ImageProcessor
    ↓
PIL.Image
    ↓
OcrEngine
    ↓
OcrResult
```

Và nguyên tắc thiết kế:

> **pypdfium2 render PDF, Pillow xử lý ảnh, OCR engine nhận diện chữ, Application Service điều phối tất cả.**

Sang **Buổi 34**, chúng ta sẽ thay/đưa thêm **OpenCV** vào pipeline để xử lý những thứ Pillow không thuận tiện bằng: **denoise, threshold nâng cao, adaptive threshold, morphology, deskew và xử lý scan trước OCR**.
