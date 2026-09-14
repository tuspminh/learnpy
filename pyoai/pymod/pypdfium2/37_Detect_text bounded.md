# Buổi 37 — Detect vùng text

Hôm nay chúng ta đi thêm một bước so với Buổi 36:

```text
PDF Scan
   ↓
pypdfium2
   ↓
PIL.Image
   ↓
OpenCV
   ↓
Detect vùng text
   ↓
Crop từng vùng
   ↓
OCR
```

Mục tiêu chưa phải xây một hệ thống layout analysis hoàn chỉnh. Ta sẽ xây **text-region detector cơ bản nhưng có kiến trúc tốt**, đủ để hiểu nền tảng và mở rộng ở các buổi sau.

---

# 1. Vì sao cần Detect vùng text?

Giả sử trang scan:

```text
┌──────────────────────────────────┐
│          CHƯƠNG 12               │
│                                  │
│ Đây là đoạn văn thứ nhất...      │
│ Đây là đoạn văn thứ nhất...      │
│ Đây là đoạn văn thứ nhất...      │
│                                  │
│ Đây là đoạn văn thứ hai...       │
│ Đây là đoạn văn thứ hai...       │
│                                  │
│              125                 │
└──────────────────────────────────┘
```

Nếu OCR toàn trang:

```text
Image
  ↓
Tesseract
  ↓
Text
```

Tesseract phải tự xử lý:

* heading
* paragraph
* khoảng trắng
* số trang
* hình ảnh
* bảng
* cột

Thay vì vậy:

```text
Image
  ↓
Detect regions
  ↓
┌──────────────┐
│ Heading      │
└──────────────┘

┌──────────────┐
│ Paragraph    │
└──────────────┘

┌──────────────┐
│ Paragraph    │
└──────────────┘
```

sau đó OCR từng vùng.

---

# 2. Detect text region không đồng nghĩa OCR

Đây là distinction rất quan trọng.

### OCR

Trả lời:

> "Trong ảnh này có chữ gì?"

### Text detection

Trả lời:

> "Chữ nằm ở đâu?"

Ví dụ:

```text
Input
  ↓
┌──────────────────────┐
│       HELLO          │
│                      │
│ Python is great.     │
│ Python is powerful. │
└──────────────────────┘
```

Detector trả:

```python
[
    BoundingBox(...),  # HELLO
    BoundingBox(...),  # paragraph
]
```

OCR sau đó mới xử lý từng box.

---

# 3. Phương pháp đơn giản nhất với OpenCV

Với sách scan có chữ đen trên nền trắng, ta có thể bắt đầu bằng:

```text
Image
 ↓
Grayscale
 ↓
Threshold
 ↓
Morphology
 ↓
Find contours
 ↓
Bounding boxes
```

Ví dụ:

```text
Grayscale
    ↓
Threshold
    ↓
Binary image
    ↓
Contours
    ↓
BoundingRect
```

OpenCV:

```python
cv2.findContours()
cv2.boundingRect()
```

---

# 4. Domain model

Ta đã có `BoundingBox` từ các buổi trước.

Không cần tạo một geometry class mới.

Ta chỉ cần thêm:

## `domain/text_region.py`

```python
from dataclasses import dataclass

from domain.geometry import BoundingBox


@dataclass(frozen=True)
class TextRegion:
    bbox: BoundingBox
    confidence: float | None = None

    @property
    def width(self) -> float:
        return self.bbox.width

    @property
    def height(self) -> float:
        return self.bbox.height

    @property
    def area(self) -> float:
        return self.bbox.area
```

Domain không biết:

```text
cv2
numpy
PIL
```

---

# 5. Detector interface

Trong Application:

## `application/ports.py`

Thêm:

```python
from typing import Protocol

from PIL import Image

from domain.text_region import TextRegion


class TextRegionDetector(Protocol):
    def detect(
        self,
        image: Image.Image,
    ) -> list[TextRegion]: ...
```

Bây giờ Application chỉ biết:

```text
TextRegionDetector
```

chứ không biết detector được xây bằng:

```text
OpenCV
Tesseract
EasyOCR
PaddleOCR
...
```

Đây chính là DIP.

---

# 6. OpenCV detector

Bây giờ mới đến infrastructure.

## `infrastructure/opencv/text_detector.py`

```python
import cv2
import numpy as np

from PIL import Image

from domain.geometry import BoundingBox
from domain.text_region import TextRegion


class OpenCvTextRegionDetector:
    def __init__(
        self,
        min_width: int = 20,
        min_height: int = 8,
        min_area: int = 100,
    ):
        if min_width <= 0:
            raise ValueError("min_width phải > 0")

        if min_height <= 0:
            raise ValueError("min_height phải > 0")

        if min_area <= 0:
            raise ValueError("min_area phải > 0")

        self.min_width = min_width
        self.min_height = min_height
        self.min_area = min_area

    def detect(
        self,
        image: Image.Image,
    ) -> list[TextRegion]:

        rgb = image.convert("RGB")

        array = np.array(rgb)

        gray = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2GRAY,
        )

        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        regions: list[TextRegion] = []

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)

            area = width * height

            if width < self.min_width:
                continue

            if height < self.min_height:
                continue

            if area < self.min_area:
                continue

            bbox = BoundingBox(
                left=x,
                bottom=y,
                right=x + width,
                top=y + height,
            )

            regions.append(
                TextRegion(
                    bbox=bbox,
                )
            )

        regions.sort(
            key=lambda region: (
                region.bbox.top,
                region.bbox.left,
            )
        )

        return regions
```

Nhưng ở đây có **một lỗi khái niệm quan trọng**.

---

# 7. Cẩn thận: tọa độ OpenCV

OpenCV/PIL dùng:

```text
(0,0)
  ───────────→ x
  │
  │
  ↓
  y
```

Tức:

```text
top-left
```

Trong khi `BoundingBox` PDF của chúng ta trước đây dùng:

```text
          top
           ↑
           │
left ──────┼────── right
           │
           ↓
         bottom
```

Để tránh trộn hai hệ tọa độ, **không nên dùng `BoundingBox` PDF trực tiếp cho detector ảnh**.

Đây là một bài học rất quan trọng từ Buổi 27.

---

# 8. Tạo ImageBoundingBox

Ta nên có model riêng cho image coordinate.

## `domain/image_geometry.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ImageBoundingBox:
    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self):

        if self.left < 0:
            raise ValueError("left phải >= 0")

        if self.top < 0:
            raise ValueError("top phải >= 0")

        if self.right < self.left:
            raise ValueError("right phải >= left")

        if self.bottom < self.top:
            raise ValueError("bottom phải >= top")

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def area(self) -> int:
        return self.width * self.height
```

Bây giờ rất rõ:

```text
PDF BoundingBox
    ↓
PDF coordinate

ImageBoundingBox
    ↓
Image coordinate
```

Không lẫn nhau.

---

# 9. Sửa TextRegion

## `domain/text_region.py`

```python
from dataclasses import dataclass

from domain.image_geometry import ImageBoundingBox


@dataclass(frozen=True)
class TextRegion:
    bbox: ImageBoundingBox

    confidence: float | None = None

    @property
    def width(self) -> int:
        return self.bbox.width

    @property
    def height(self) -> int:
        return self.bbox.height

    @property
    def area(self) -> int:
        return self.bbox.area
```

---

# 10. Sửa detector

## `infrastructure/opencv/text_detector.py`

```python
import cv2
import numpy as np

from PIL import Image

from domain.image_geometry import ImageBoundingBox
from domain.text_region import TextRegion


class OpenCvTextRegionDetector:
    def __init__(
        self,
        min_width: int = 20,
        min_height: int = 8,
        min_area: int = 100,
    ):
        if min_width <= 0:
            raise ValueError("min_width phải > 0")

        if min_height <= 0:
            raise ValueError("min_height phải > 0")

        if min_area <= 0:
            raise ValueError("min_area phải > 0")

        self.min_width = min_width
        self.min_height = min_height
        self.min_area = min_area

    def detect(
        self,
        image: Image.Image,
    ) -> list[TextRegion]:

        rgb = image.convert("RGB")

        array = np.array(rgb)

        gray = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2GRAY,
        )

        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        regions: list[TextRegion] = []

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)

            area = width * height

            if width < self.min_width:
                continue

            if height < self.min_height:
                continue

            if area < self.min_area:
                continue

            bbox = ImageBoundingBox(
                left=x,
                top=y,
                right=x + width,
                bottom=y + height,
            )

            regions.append(
                TextRegion(
                    bbox=bbox,
                )
            )

        regions.sort(
            key=lambda region: (
                region.bbox.top,
                region.bbox.left,
            )
        )

        return regions
```

---

# 11. Nhưng detector hiện tại còn một vấn đề

Nếu một dòng có:

```text
Python is a powerful language
```

thì contour có thể là:

```text
P
y
t
h
o
n
...
```

Thay vì:

```text
┌───────────────────────────────┐
│ Python is a powerful language │
└───────────────────────────────┘
```

Tức là:

> **Contour detection chưa phải text-line detection.**

Đây là bước cực kỳ quan trọng.

---

# 12. Morphological dilation

Ta có thể nối các ký tự gần nhau.

```text
P y t h o n
↓
dilation
↓
Python
```

OpenCV:

```python
kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (25, 5),
)
```

Sau đó:

```python
dilated = cv2.dilate(
    binary,
    kernel,
    iterations=1,
)
```

Bây giờ các ký tự trong cùng dòng có thể được nối thành một vùng.

---

# 13. Detector phiên bản tốt hơn

```python
import cv2
import numpy as np

from PIL import Image

from domain.image_geometry import ImageBoundingBox
from domain.text_region import TextRegion


class OpenCvTextRegionDetector:
    def __init__(
        self,
        min_width: int = 30,
        min_height: int = 8,
        min_area: int = 200,
        kernel_width: int = 25,
        kernel_height: int = 5,
    ):
        if min_width <= 0:
            raise ValueError("min_width phải > 0")

        if min_height <= 0:
            raise ValueError("min_height phải > 0")

        if min_area <= 0:
            raise ValueError("min_area phải > 0")

        if kernel_width <= 0:
            raise ValueError("kernel_width phải > 0")

        if kernel_height <= 0:
            raise ValueError("kernel_height phải > 0")

        self.min_width = min_width
        self.min_height = min_height
        self.min_area = min_area

        self.kernel_width = kernel_width
        self.kernel_height = kernel_height

    def detect(
        self,
        image: Image.Image,
    ) -> list[TextRegion]:

        array = np.array(image.convert("RGB"))

        gray = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2GRAY,
        )

        binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (
                self.kernel_width,
                self.kernel_height,
            ),
        )

        dilated = cv2.dilate(
            binary,
            kernel,
            iterations=1,
        )

        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        regions: list[TextRegion] = []

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)

            area = width * height

            if width < self.min_width:
                continue

            if height < self.min_height:
                continue

            if area < self.min_area:
                continue

            bbox = ImageBoundingBox(
                left=x,
                top=y,
                right=x + width,
                bottom=y + height,
            )

            regions.append(
                TextRegion(
                    bbox=bbox,
                )
            )

        regions.sort(
            key=lambda region: (
                region.bbox.top,
                region.bbox.left,
            )
        )

        return regions
```

---

# 14. Tại sao kernel `(25, 5)`?

Đây không phải con số thần kỳ.

Ta muốn:

```text
width lớn
height nhỏ
```

vì text thường có cấu trúc:

```text
████████████████████████
```

theo chiều ngang.

Kernel:

```text
25 × 5
```

có xu hướng nối:

```text
character → character → character
```

trên cùng một dòng.

Nhưng:

```text
kernel = (100, 30)
```

có thể nối luôn nhiều dòng.

Khi đó:

```text
Line 1
Line 2
Line 3
```

có thể trở thành:

```text
┌──────────────────────┐
│ Line 1               │
│ Line 2               │
│ Line 3               │
└──────────────────────┘
```

Vì vậy kernel cần phụ thuộc vào:

* DPI
* font size
* khoảng cách ký tự
* khoảng cách dòng
* loại tài liệu.

---

# 15. Một vấn đề khác: DPI

Đây là nơi kiến thức Buổi 21–29 bắt đầu kết nối.

Ví dụ:

```text
150 DPI
```

thì một chữ có thể cao:

```text
20 px
```

Nhưng:

```text
300 DPI
```

chữ đó có thể cao:

```text
40 px
```

Nếu dùng:

```python
kernel_width = 25
```

cho cả hai thì kết quả khác nhau.

Do đó production system nên tính kernel dựa trên DPI hoặc kích thước chữ.

Ví dụ:

```python
kernel_width = round(25 * dpi / 200)
```

Nếu:

```text
dpi = 200
```

→ 25

Nếu:

```text
dpi = 300
```

→ 38.

---

# 16. Crop vùng text

Sau khi detect:

```python
regions = detector.detect(image)
```

ta cần crop.

Tạo adapter:

## `infrastructure/pillow/cropper.py`

```python
from PIL import Image

from domain.text_region import TextRegion


class PillowRegionCropper:
    def crop(
        self,
        image: Image.Image,
        region: TextRegion,
    ) -> Image.Image:

        box = region.bbox

        return image.crop(
            (
                box.left,
                box.top,
                box.right,
                box.bottom,
            )
        )
```

---

# 17. Pipeline

Bây giờ:

```python
regions = detector.detect(image)

cropper = PillowRegionCropper()

for region in regions:
    cropped = cropper.crop(
        image,
        region,
    )

    try:
        result = ocr_engine.recognize(cropped)

        print(result.text)

    finally:
        cropped.close()
```

Pipeline:

```text
                    PDF
                     ↓
                 pypdfium2
                     ↓
                    Image
                     ↓
             ┌───────────────┐
             │ Text Detector │
             └───────┬───────┘
                     ↓
             TextRegion[]
                     ↓
              ┌─────────────┐
              │   Cropper   │
              └──────┬──────┘
                     ↓
                 Crop Image
                     ↓
                Tesseract
                     ↓
                 OcrResult
```

---

# 18. Application service

Không để CLI tự làm pipeline.

## `application/region_ocr.py`

```python
class RegionOcrService:
    def __init__(
        self,
        detector,
        cropper,
        ocr_engine,
    ):
        self.detector = detector
        self.cropper = cropper
        self.ocr_engine = ocr_engine

    def process(
        self,
        image,
    ):
        regions = self.detector.detect(image)

        results = []

        for region in regions:
            cropped = self.cropper.crop(
                image,
                region,
            )

            try:
                ocr_result = self.ocr_engine.recognize(cropped)

                results.append(
                    (
                        region,
                        ocr_result,
                    )
                )

            finally:
                cropped.close()

        return results
```

---

# 19. Nhưng đừng vội OCR từng contour

Đây là một điểm cần hiểu rất sâu.

Có ba cấp độ:

```text
Character
    ↓
Word
    ↓
Line
    ↓
Paragraph
    ↓
Block
```

Detector đơn giản của chúng ta đang cố gắng tìm:

```text
Line / text region
```

nhưng chưa thực sự hiểu semantic structure.

Ví dụ:

```text
CHƯƠNG I

Đây là đoạn văn...
Đây là đoạn văn...

CHƯƠNG II

Đây là đoạn văn...
```

Detector chỉ thấy:

```text
Region 1
Region 2
Region 3
Region 4
Region 5
```

Nó chưa biết:

```text
Region 1 = heading
Region 2 = paragraph
```

Đó là **layout analysis**.

---

# 20. Test detector

Không cần PDF.

Ta tạo ảnh giả:

```python
from PIL import Image, ImageDraw

from infrastructure.opencv.text_detector import (
    OpenCvTextRegionDetector,
)


def create_test_image():

    image = Image.new(
        "RGB",
        (800, 300),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (50, 50),
        "Python OCR Test",
        fill="black",
    )

    draw.text(
        (50, 120),
        "This is a scanned document.",
        fill="black",
    )

    return image
```

Test:

```python
def test_detect_text_regions():

    image = create_test_image()

    detector = OpenCvTextRegionDetector(
        min_width=20,
        min_height=5,
        min_area=50,
    )

    regions = detector.detect(image)

    assert len(regions) >= 1
```

Lưu ý:

> Test bằng font hệ thống có thể cho kết quả khác nhau giữa OS.

Do đó unit test production tốt hơn nên kiểm tra:

```text
region tồn tại
bbox hợp lệ
bbox nằm trong image
```

thay vì bắt buộc chính xác `len(regions) == 2`.

---

# 21. Validate bounding box

Ta nên thêm:

```python
def is_inside(
    bbox,
    image_width,
    image_height,
):
    return (
        0 <= bbox.left < image_width
        and 0 <= bbox.top < image_height
        and bbox.right <= image_width
        and bbox.bottom <= image_height
    )
```

Test:

```python
for region in regions:
    bbox = region.bbox

    assert bbox.left >= 0
    assert bbox.top >= 0
    assert bbox.right <= image.width
    assert bbox.bottom <= image.height
```

Điều này quan trọng vì detector là infrastructure không nên tạo ra dữ liệu invalid.

---

# 22. Thêm padding

OCR thường tốt hơn nếu crop có một chút khoảng trắng.

Thay vì:

```text
┌──────────────┐
│Hello world   │
└──────────────┘
```

có thể:

```text
┌──────────────────┐
│                  │
│ Hello world      │
│                  │
└──────────────────┘
```

Cropper:

```python
class PillowRegionCropper:
    def __init__(self, padding: int = 5):
        if padding < 0:
            raise ValueError("padding phải >= 0")

        self.padding = padding

    def crop(
        self,
        image,
        region,
    ):
        box = region.bbox

        left = max(
            0,
            box.left - self.padding,
        )

        top = max(
            0,
            box.top - self.padding,
        )

        right = min(
            image.width,
            box.right + self.padding,
        )

        bottom = min(
            image.height,
            box.bottom + self.padding,
        )

        return image.crop(
            (
                left,
                top,
                right,
                bottom,
            )
        )
```

---

# 23. Kiến trúc hiện tại

Sau Buổi 37, hệ thống của chúng ta:

```text
                         PDF
                          │
                          ▼
                    PdfRenderer
                    pypdfium2
                          │
                          ▼
                      PIL.Image
                          │
                          ▼
                 TextRegionDetector
                     OpenCV
                          │
                          ▼
                  TextRegion[]
                          │
                          ▼
                     Cropper
                     Pillow
                          │
                          ▼
                    Crop Images
                          │
                          ▼
                    OcrEngine
                    Tesseract
                          │
                          ▼
                     OcrResult
```

Application:

```text
RegionOcrService
```

không phụ thuộc trực tiếp vào:

```text
pypdfium2
OpenCV
Pillow
Tesseract
```

---

# 24. Điều gì đã giải quyết?

Buổi 36:

```text
OCR cả trang
```

Buổi 37:

```text
Detect
 ↓
Region
 ↓
Crop
 ↓
OCR
```

Điều này có thể giúp:

* giảm vùng nhiễu
* bỏ bớt margin
* bỏ header/footer nếu detect được
* OCR từng vùng
* xử lý layout tốt hơn
* chuẩn bị cho paragraph/line detection

---

# 25. Nhưng thuật toán này có giới hạn

Phương pháp:

```text
Threshold
 ↓
Dilation
 ↓
Contour
```

không đủ tốt cho mọi PDF scan.

Nó dễ gặp vấn đề với:

### Hai cột

```text
┌──────────┬──────────┐
│ Column A │ Column B │
│ Column A │ Column B │
│ Column A │ Column B │
└──────────┴──────────┘
```

### Bảng

```text
┌───────┬───────┐
│ A     │ B     │
├───────┼───────┤
│ C     │ D     │
└───────┴───────┘
```

### Ảnh chứa chữ

```text
┌─────────────────┐
│     [IMAGE]     │
│    TEXT HERE    │
└─────────────────┘
```

### Trang bị nghiêng

```text
//////// text
```

### Nền phức tạp

```text
██████████████
```

Vì vậy đây là **baseline detector**, không phải OCR layout engine production hoàn chỉnh.

---

# 26. Roadmap kỹ thuật từ đây

Chúng ta đang tiến tới:

```text
Buổi 37
Text Region Detection
       ↓
Buổi 38
Parallel Rendering
       ↓
Buổi 39
Streaming / Batch
       ↓
Buổi 40
PDF OCR Pipeline
```

Trong **Buổi 40**, chúng ta sẽ ghép toàn bộ:

```text
PDF
 ↓
pypdfium2
 ↓
Render
 ↓
Preprocessing
 ↓
Text Detection
 ↓
Crop
 ↓
Tesseract
 ↓
Confidence
 ↓
Retry
 ↓
Result
```

---

## Bài tập Buổi 37

Hãy lấy một PDF scan thật và thử 3 cấu hình:

```python
OpenCvTextRegionDetector(
    kernel_width=15,
    kernel_height=3,
)
```

sau đó:

```python
OpenCvTextRegionDetector(
    kernel_width=25,
    kernel_height=5,
)
```

và:

```python
OpenCvTextRegionDetector(
    kernel_width=40,
    kernel_height=7,
)
```

Quan sát:

```text
Số region
Kích thước region
Có gộp nhiều dòng không?
Có tách một dòng thành nhiều region không?
Có bắt nhầm hình/đường kẻ không?
```

Nếu bạn có **một PDF scan cụ thể**, bạn có thể tải lên để chúng ta dùng chính tài liệu đó làm dữ liệu thực hành; từ đó có thể xem detector đang bắt sai ở đâu và điều chỉnh kernel/DPI/padding cho phù hợp.

**Kết luận quan trọng nhất của Buổi 37:**

```text
OCR không chỉ là:

Image → Tesseract

mà trong tài liệu scan phức tạp nên hướng tới:

Image
  ↓
Layout / Region Detection
  ↓
Text Regions
  ↓
Crop
  ↓
OCR
  ↓
Structured Result
```

Đây là nền móng để sau này chúng ta xây **OCR pipeline cho sách scan**, thay vì chỉ chạy Tesseract trên toàn bộ trang.
