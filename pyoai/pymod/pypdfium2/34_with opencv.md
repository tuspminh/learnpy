# Phần IV — PDF Processing Pipeline

# Buổi 34 — pypdfium2 + OpenCV

Ở Buổi 33 chúng ta có:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
Pillow Processing
 ↓
OCR
```

Hôm nay ta thêm **OpenCV** để xử lý những bài toán scan khó hơn:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
OpenCV
 ├── Grayscale
 ├── Denoise
 ├── Threshold
 ├── Adaptive Threshold
 ├── Morphology
 └── Deskew
 ↓
PIL.Image
 ↓
OCR
```

Mục tiêu quan trọng nhất vẫn là **kiến trúc sạch**, không biến `PdfOcrService` thành một class chứa toàn bộ OpenCV.

---

# 1. Tại sao cần OpenCV?

Pillow rất tốt cho:

```text
resize
crop
rotate
brightness
contrast
format
```

OpenCV mạnh hơn khi xử lý ảnh scan:

```text
noise
threshold
adaptive threshold
morphology
contour
edge
deskew
perspective
```

Đặc biệt với tài liệu scan:

```text
┌───────────────────────────┐
│  nền hơi xám              │
│                           │
│  T h e   s t o r y        │
│                           │
│   ///// noise /////       │
└───────────────────────────┘
```

Ta muốn biến nó thành ảnh phù hợp hơn cho OCR.

---

# 2. Cài OpenCV

Cài:

```bash
pip install opencv-python
```

Kiểm tra:

```bash
python -c "import cv2; print(cv2.__version__)"
```

Trong project server/headless, đôi khi có thể dùng:

```bash
pip install opencv-python-headless
```

Nhưng về mặt API xử lý ảnh hôm nay, code cơ bản tương tự.

---

# 3. Kiến trúc không thay đổi

Đây là điểm rất quan trọng.

Không sửa:

```text
PdfiumRenderer
```

để thêm OpenCV.

Không sửa:

```text
OcrEngine
```

để thêm OpenCV.

Ta chỉ thêm adapter:

```text
ImageProcessor
       │
       ├── PillowProcessor
       │
       └── OpenCvProcessor
```

Architecture:

```text
                 PdfiumRenderer
                       │
                       ▼
                   PIL.Image
                       │
                       ▼
                 ImageProcessor
                       │
                 ┌─────┴─────┐
                 ▼           ▼
              Pillow      OpenCV
                 │           │
                 └─────┬─────┘
                       ▼
                   PIL.Image
                       │
                       ▼
                    OCR
```

---

# 4. Vấn đề quan trọng: OpenCV dùng NumPy

Pillow:

```python
from PIL import Image
```

OpenCV thường làm việc với:

```python
import numpy as np
```

Ảnh OpenCV thường là:

```text
numpy.ndarray
```

Trong khi pypdfium2:

```text
PdfBitmap
    ↓
PIL.Image
```

Vì vậy chúng ta cần bridge:

```text
PIL.Image
     ↓
NumPy
     ↓
OpenCV
     ↓
NumPy
     ↓
PIL.Image
```

---

# 5. PIL → OpenCV

Ta viết helper:

```python
import cv2
import numpy as np
from PIL import Image


def pil_to_cv(image: Image.Image) -> np.ndarray:
    rgb = image.convert("RGB")

    array = np.array(rgb)

    return cv2.cvtColor(
        array,
        cv2.COLOR_RGB2BGR,
    )
```

Tại sao phải:

```python
cv2.COLOR_RGB2BGR
```

?

Vì:

```text
Pillow:
RGB

OpenCV:
BGR
```

Đây là một lỗi rất phổ biến khi kết hợp hai thư viện.

---

# 6. OpenCV → PIL

Ngược lại:

```python
def cv_to_pil(
    image: np.ndarray,
) -> Image.Image:

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    return Image.fromarray(rgb)
```

Flow:

```text
PIL RGB
  ↓
RGB → BGR
  ↓
OpenCV
  ↓
BGR → RGB
  ↓
PIL RGB
```

---

# 7. Nhưng grayscale thì sao?

Nếu OpenCV image có shape:

```text
(height, width)
```

thì đó là grayscale.

Không thể lúc nào cũng:

```python
cv2.COLOR_BGR2RGB
```

Ta có helper tốt hơn:

```python
def cv_to_pil(
    image: np.ndarray,
) -> Image.Image:

    if image.ndim == 2:
        return Image.fromarray(image)

    if image.ndim == 3:
        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        return Image.fromarray(rgb)

    raise ValueError(
        f"Unsupported image shape: {image.shape}"
    )
```

---

# 8. OpenCV Grayscale

OpenCV:

```python
gray = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2GRAY,
)
```

Ta xây processor:

```python
class CvGrayscaleProcessor:

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        return cv_to_pil(gray)
```

---

# 9. Test

```python
from PIL import Image


def test_cv_grayscale():

    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    processor = CvGrayscaleProcessor()

    result = processor.process(image)

    assert result.mode == "L"
    assert result.size == (100, 100)

    result.close()
    image.close()
```

---

# 10. Threshold cơ bản

OpenCV có:

```python
cv2.threshold()
```

Ví dụ:

```python
_, binary = cv2.threshold(
    gray,
    128,
    255,
    cv2.THRESH_BINARY,
)
```

Ý nghĩa:

```text
pixel < 128
    ↓
0

pixel >= 128
    ↓
255
```

Giống ý tưởng Pillow ở Buổi 33 nhưng OpenCV cung cấp nhiều phương pháp threshold hơn.

---

# 11. Threshold Processor

```python
class CvThresholdProcessor:

    def __init__(
        self,
        threshold: int = 128,
    ):

        if not 0 <= threshold <= 255:
            raise ValueError(
                "threshold phải trong [0, 255]"
            )

        self.threshold = threshold

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        _, binary = cv2.threshold(
            gray,
            self.threshold,
            255,
            cv2.THRESH_BINARY,
        )

        return cv_to_pil(binary)
```

---

# 12. Otsu Threshold

Threshold cố định:

```text
128
```

không phải lúc nào cũng phù hợp.

Ví dụ một scan:

```text
nền = 220
chữ = 160
```

Threshold 128:

```text
220 → white
160 → white
```

Chữ biến mất.

Otsu có thể tự tìm threshold:

```python
_, binary = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY
    + cv2.THRESH_OTSU,
)
```

---

# 13. Otsu Processor

```python
class OtsuThresholdProcessor:

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY
            + cv2.THRESH_OTSU,
        )

        return cv_to_pil(binary)
```

Ưu điểm:

```text
không cần tự chọn threshold
```

Nhược điểm:

Otsu không phải giải pháp thần kỳ cho ảnh có nền không đồng đều.

---

# 14. Adaptive Threshold

Đây là kỹ thuật rất hữu ích với scan.

Ví dụ:

```text
┌──────────────────────────┐
│ nền sáng                 │
│                          │
│      chữ                 │
│                          │
│ nền tối hơn              │
└──────────────────────────┘
```

Một threshold duy nhất có thể không tốt.

Adaptive threshold tính threshold **theo vùng cục bộ**.

```python
binary = cv2.adaptiveThreshold(
    gray,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    31,
    10,
)
```

---

# 15. Hiểu các tham số

```python
cv2.adaptiveThreshold(
    gray,
    255,
    method,
    threshold_type,
    block_size,
    C,
)
```

### `block_size`

Kích thước vùng lân cận.

Ví dụ:

```text
31 × 31
```

Thường phải là số lẻ và lớn hơn 1.

### `C`

Giá trị trừ khỏi threshold cục bộ.

Không có một giá trị tốt cho mọi tài liệu.

---

# 16. Adaptive Threshold Processor

```python
class AdaptiveThresholdProcessor:

    def __init__(
        self,
        block_size: int = 31,
        c: int = 10,
    ):

        if block_size <= 1:
            raise ValueError(
                "block_size phải > 1"
            )

        if block_size % 2 == 0:
            raise ValueError(
                "block_size phải là số lẻ"
            )

        self.block_size = block_size
        self.c = c

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            self.block_size,
            self.c,
        )

        return cv_to_pil(binary)
```

---

# 17. So sánh

```text
Threshold cố định
        ↓
        128
```

Phù hợp:

```text
ảnh có lighting/background tương đối đồng đều
```

Otsu:

```text
threshold tự động
```

Phù hợp:

```text
histogram có sự phân tách tương đối rõ
```

Adaptive:

```text
threshold theo local region
```

Phù hợp:

```text
background không đồng đều
scan ánh sáng không đều
```

---

# 18. Denoising

Scan thường có:

```text
speckles
dots
noise
```

Ví dụ:

```text
The story begins...

. . . . . . .
```

Noise có thể gây nhầm cho OCR.

OpenCV cung cấp:

```python
cv2.GaussianBlur()
cv2.medianBlur()
cv2.bilateralFilter()
```

Với tài liệu scan, `medianBlur` thường đáng thử cho noise dạng chấm.

---

# 19. Median Blur

```python
class MedianBlurProcessor:

    def __init__(
        self,
        kernel_size: int = 3,
    ):

        if kernel_size <= 0:
            raise ValueError(
                "kernel_size phải > 0"
            )

        if kernel_size % 2 == 0:
            raise ValueError(
                "kernel_size phải là số lẻ"
            )

        self.kernel_size = kernel_size

    def process(self, image):

        cv_image = pil_to_cv(image)

        result = cv2.medianBlur(
            cv_image,
            self.kernel_size,
        )

        return cv_to_pil(result)
```

---

# 20. Morphology

Đây là một nhóm kỹ thuật rất quan trọng.

OpenCV có:

```text
erosion
dilation
opening
closing
```

Với OCR:

```text
Opening
```

có thể giúp loại bỏ các noise nhỏ.

```text
Closing
```

có thể giúp nối các vùng chữ bị đứt.

---

# 21. Kernel

Ta tạo kernel:

```python
kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (3, 3),
)
```

Sau đó:

```python
result = cv2.morphologyEx(
    image,
    cv2.MORPH_OPEN,
    kernel,
)
```

---

# 22. Opening

Opening:

```text
erosion
   ↓
dilation
```

Có thể hiểu đơn giản:

```text
loại bỏ những vùng nhỏ
```

Ví dụ:

```text
text + noise
       ↓
opening
       ↓
text sạch hơn
```

Nhưng nếu kernel quá lớn:

```text
chữ nhỏ
 ↓
bị erosion
 ↓
mất nét
```

Vì vậy:

> Morphology phải dùng nhẹ tay.

---

# 23. Closing

Closing:

```text
dilation
   ↓
erosion
```

Có thể giúp:

```text
chữ bị đứt nét
```

trở nên liền hơn.

---

# 24. Morphology Processor

```python
class MorphologyProcessor:

    def __init__(
        self,
        operation,
        kernel_size: int = 3,
    ):

        if kernel_size <= 0:
            raise ValueError(
                "kernel_size phải > 0"
            )

        if kernel_size % 2 == 0:
            raise ValueError(
                "kernel_size phải là số lẻ"
            )

        self.operation = operation
        self.kernel_size = kernel_size

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (
                self.kernel_size,
                self.kernel_size,
            ),
        )

        result = cv2.morphologyEx(
            gray,
            self.operation,
            kernel,
        )

        return cv_to_pil(result)
```

Sử dụng:

```python
processor = MorphologyProcessor(
    operation=cv2.MORPH_OPEN,
    kernel_size=3,
)
```

---

# 25. Deskew — sửa ảnh bị nghiêng

Đây là một trong những kỹ thuật quan trọng nhất với scan.

Ví dụ:

```text
PDF scan:

////////////////////////
     The story
////////////////////////
```

Chữ bị nghiêng vài độ.

OCR có thể kém hơn.

Ta muốn:

```text
------------------------
       The story
------------------------
```

Đây gọi là:

```text
deskew
```

---

# 26. Ý tưởng deskew

Một pipeline đơn giản:

```text
Grayscale
    ↓
Threshold
    ↓
Find foreground pixels
    ↓
Estimate angle
    ↓
Rotate
```

Ta có thể dùng:

```python
cv2.minAreaRect()
```

để ước lượng góc của vùng foreground.

---

# 27. Deskew implementation

```python
import cv2
import numpy as np


class DeskewProcessor:

    def process(self, image):

        cv_image = pil_to_cv(image)

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY,
        )

        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV
            + cv2.THRESH_OTSU,
        )

        coordinates = np.column_stack(
            np.where(binary > 0)
        )

        if len(coordinates) < 10:
            return image.copy()

        angle = cv2.minAreaRect(
            coordinates
        )[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        height, width = gray.shape

        center = (
            width / 2,
            height / 2,
        )

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0,
        )

        rotated = cv2.warpAffine(
            cv_image,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        return cv_to_pil(rotated)
```

Đây là **deskew cơ bản để học kiến trúc**, chưa phải thuật toán production hoàn chỉnh cho mọi loại tài liệu.

---

# 28. Một lưu ý cực kỳ quan trọng về deskew

Đừng nghĩ:

```text
OCR kém
 ↓
deskew
```

là luôn đúng.

Nếu PDF đã thẳng:

```text
deskew
```

có thể không đem lại lợi ích.

Nếu tài liệu có:

```text
ảnh
bảng
nhiều cột
chữ dọc
```

thì thuật toán đơn giản dựa trên toàn bộ foreground có thể ước lượng sai góc.

Buổi 36 chúng ta sẽ xử lý scan bài bản hơn.

---

# 29. Xây OpenCV Pipeline

Giống Buổi 33:

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

OpenCV không cần biết PDF tồn tại.

---

# 30. Pipeline OCR cơ bản

Ví dụ:

```python
pipeline = ImagePipeline([
    CvGrayscaleProcessor(),
    MedianBlurProcessor(3),
    OtsuThresholdProcessor(),
])
```

Flow:

```text
PIL.Image
    ↓
Grayscale
    ↓
Median Blur
    ↓
Otsu
    ↓
PIL.Image
```

---

# 31. Pipeline scan khó hơn

```python
pipeline = ImagePipeline([
    CvGrayscaleProcessor(),
    MedianBlurProcessor(3),
    AdaptiveThresholdProcessor(
        block_size=31,
        c=10,
    ),
])
```

Flow:

```text
PDF
 ↓
pypdfium2
 ↓
PIL
 ↓
Grayscale
 ↓
Denoise
 ↓
Adaptive Threshold
 ↓
OCR
```

---

# 32. Không nên dùng tất cả processor

Ví dụ **không nên** mặc định:

```text
Grayscale
 ↓
MedianBlur
 ↓
Otsu
 ↓
AdaptiveThreshold
 ↓
Opening
 ↓
Closing
 ↓
Sharpen
 ↓
Deskew
```

Đây là over-processing.

Mỗi bước có thể làm mất thông tin.

Tốt hơn:

```text
Document type
      ↓
Preprocessing profile
      ↓
chọn pipeline
```

---

# 33. Preprocessing Profile

Ta có thể tạo:

```python
class OcrPreprocessingProfile:

    def __init__(
        self,
        processors,
    ):
        self.processors = processors

    def build(self):
        return ImagePipeline(
            self.processors
        )
```

Ví dụ:

```python
clean_scan = OcrPreprocessingProfile([
    CvGrayscaleProcessor(),
])
```

Hoặc:

```python
noisy_scan = OcrPreprocessingProfile([
    CvGrayscaleProcessor(),
    MedianBlurProcessor(3),
    OtsuThresholdProcessor(),
])
```

---

# 34. Architecture hoàn chỉnh

Sau Buổi 34:

```text
                         PDF
                          │
                          ▼
                   ┌─────────────┐
                   │ pypdfium2   │
                   │ Renderer    │
                   └──────┬──────┘
                          │
                          ▼
                      PIL.Image
                          │
                          ▼
                 ┌─────────────────┐
                 │ Image Pipeline  │
                 └────────┬────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Pillow        OpenCV       ...
             │            │
             └────────────┘
                          │
                          ▼
                      PIL.Image
                          │
                          ▼
                      OcrEngine
                          │
                          ▼
                     OcrResult
```

---

# 35. `PdfOcrService` không đổi

Đây là dấu hiệu architecture tốt.

Buổi 32:

```python
service = PdfOcrService(
    renderer,
    image_processor,
    ocr_engine,
)
```

Buổi 33:

```python
image_processor = ImagePipeline([
    GrayscaleProcessor(),
    ContrastProcessor(1.5),
])
```

Buổi 34:

```python
image_processor = ImagePipeline([
    CvGrayscaleProcessor(),
    MedianBlurProcessor(3),
    OtsuThresholdProcessor(),
])
```

`PdfOcrService` vẫn:

```text
render
 ↓
process
 ↓
OCR
```

Không cần biết processor là Pillow hay OpenCV.

Đây chính là **Dependency Inversion** đang hoạt động trong project thực tế.

---

# 36. Test OpenCV Processor

Ví dụ test threshold:

```python
from PIL import Image


def test_otsu_threshold():

    image = Image.new(
        "L",
        (4, 1),
    )

    image.putdata([
        20,
        30,
        220,
        230,
    ])

    processor = OtsuThresholdProcessor()

    result = processor.process(image)

    assert result.mode == "L"
    assert result.size == (4, 1)

    values = list(result.getdata())

    assert set(values) <= {0, 255}

    result.close()
    image.close()
```

Không nên test chính xác từng pixel của mọi ảnh nếu thuật toán có thể thay đổi tùy dữ liệu.

---

# 37. Test Adaptive Threshold

```python
def test_adaptive_threshold():

    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )

    processor = AdaptiveThresholdProcessor(
        block_size=31,
        c=10,
    )

    result = processor.process(image)

    assert result.mode == "L"
    assert result.size == (100, 100)

    result.close()
    image.close()
```

---

# 38. Test Pipeline

```python
def test_opencv_pipeline():

    image = Image.new(
        "RGB",
        (200, 200),
        "white",
    )

    pipeline = ImagePipeline([
        CvGrayscaleProcessor(),
        MedianBlurProcessor(3),
        OtsuThresholdProcessor(),
    ])

    result = pipeline.process(image)

    assert result.mode == "L"
    assert result.size == (200, 200)

    result.close()
    image.close()
```

---

# 39. Pillow vs OpenCV

| Tác vụ             |        Pillow | OpenCV |
| ------------------ | ------------: | -----: |
| PDF render         |             ❌ |      ❌ |
| Resize             |             ✅ |      ✅ |
| Crop               |             ✅ |      ✅ |
| Grayscale          |             ✅ |      ✅ |
| Contrast           |             ✅ |      ✅ |
| Brightness         |             ✅ |      ✅ |
| Sharpen            |             ✅ |      ✅ |
| Threshold          |             ✅ |      ✅ |
| Otsu               |     ❌/hạn chế |      ✅ |
| Adaptive threshold |             ❌ |      ✅ |
| Morphology         |     ❌/hạn chế |      ✅ |
| Deskew             | Có thể tự làm | ✅ mạnh |
| Contour            |             ❌ |      ✅ |
| Perspective        |       hạn chế |      ✅ |

Điều quan trọng:

> Không phải chọn một trong hai. Ta có thể dùng Pillow và OpenCV cùng nhau.

---

# 40. Một kiến trúc tốt hơn nữa

Ta có thể có:

```text
ImageProcessor
      │
      ├── PillowProcessor
      │
      ├── OpenCvProcessor
      │
      └── CompositeProcessor
```

Ví dụ:

```text
Pillow
 ↓
OpenCV
 ↓
Pillow
```

Flow:

```text
PIL
 ↓
Pillow resize
 ↓
OpenCV threshold
 ↓
Pillow output
```

Không cần ép toàn bộ project phải dùng OpenCV.

---

# 41. Một ví dụ thực tế

Giả sử có PDF scan truyện:

```text
300 pages
A4
300 DPI
```

Pipeline:

```text
Page
 ↓
pypdfium2 render 200 DPI
 ↓
PIL.Image
 ↓
OpenCV grayscale
 ↓
median blur
 ↓
adaptive threshold
 ↓
OCR
 ↓
Text
 ↓
release image
```

Với từng page:

```text
Page 1 → OCR → save
Page 2 → OCR → save
Page 3 → OCR → save
...
```

Không giữ 300 ảnh trong RAM.

---

# 42. Bài tập thực hành

## Bài 1

Viết:

```python
pil_to_cv()
cv_to_pil()
```

và kiểm tra:

```text
RGB → BGR → RGB
```

---

## Bài 2

Viết:

```text
CvGrayscaleProcessor
CvThresholdProcessor
OtsuThresholdProcessor
```

---

## Bài 3

Viết:

```text
MedianBlurProcessor
```

với validation:

```text
kernel > 0
kernel là số lẻ
```

---

## Bài 4

Viết:

```text
AdaptiveThresholdProcessor
```

và test:

```text
block_size = 31
```

---

## Bài 5

Viết:

```text
MorphologyProcessor
```

hỗ trợ:

```text
MORPH_OPEN
MORPH_CLOSE
```

---

## Bài 6 — quan trọng

Tạo hai profile:

```text
clean_scan
noisy_scan
```

### clean_scan

```text
Grayscale
 ↓
Otsu
```

### noisy_scan

```text
Grayscale
 ↓
MedianBlur
 ↓
Otsu
```

Sau đó chạy cùng:

```python
PdfOcrService
```

mà không sửa Service.

---

# 43. Bài tập nâng cao

Tạo CLI:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --preprocess otsu
```

hoặc:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --preprocess adaptive
```

hoặc:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --preprocess noisy
```

CLI chỉ làm:

```text
argument
   ↓
build profile
   ↓
Dependency Injection
   ↓
PdfOcrService
```

---

# 44. Điều quan trọng nhất của Buổi 34

Đừng nhớ OpenCV chỉ bằng danh sách API.

Hãy nhớ pipeline:

```text
PIL.Image
    │
    ▼
NumPy ndarray
    │
    ▼
OpenCV
    │
    ├── grayscale
    ├── denoise
    ├── threshold
    ├── adaptive threshold
    ├── morphology
    └── deskew
    │
    ▼
NumPy ndarray
    │
    ▼
PIL.Image
```

Và kiến trúc:

```text
pypdfium2
     ↓
Renderer
     ↓
PIL
     ↓
ImageProcessor
     ↓
OpenCV / Pillow
     ↓
PIL
     ↓
OcrEngine
```

---

# 45. Roadmap

```text
31. PDF → Image                  ✅
32. PDF → OCR                    ✅
33. pypdfium2 + Pillow           ✅
34. pypdfium2 + OpenCV           ✅
35. pypdfium2 + Tesseract        ⬜
36. Xử lý PDF scan               ⬜
37. Detect vùng text             ⬜
38. Parallel rendering           ⬜
39. Streaming / batch processing ⬜
40. Mini Project: PDF OCR        ⬜
```

**Buổi 35** sẽ là bước rất quan trọng: chúng ta cắm **Tesseract thật** vào `OcrEngine`, xử lý `lang`, `PSM`, `OEM`, confidence và bounding boxes, để biến pipeline hiện tại thành:

```text
PDF
 ↓
pypdfium2
 ↓
PIL
 ↓
OpenCV preprocessing
 ↓
Tesseract
 ↓
OcrResult
 ↓
text + confidence + bbox
```

Từ đó Buổi 36 mới đi sâu vào **PDF scan thực chiến**.
