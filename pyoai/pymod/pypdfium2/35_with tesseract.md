# Phần IV — PDF Processing Pipeline

# Buổi 35 — pypdfium2 + Tesseract

Đây là buổi chúng ta ghép các thành phần đã học thành OCR thực sự:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
OpenCV / Pillow
 ↓
Tesseract
 ↓
OCR Result
 ↓
Text + Confidence + Bounding Box
```

Từ buổi này, pipeline bắt đầu có giá trị thực tế.

---

# 1. Tesseract là gì?

![Image](https://images.openai.com/static-rsc-4/uiQQdTUBMXedH4wQhFQ_vBTW7zUlVH5IiZlppKdOJa4nRrzWLF680Pxx6agKyPdbhRaPI7i3GDOj7Mp-ZxniE2yXIvj9jy9lwWCT349pe1BPsjt4uuyBuqCdnMmc62WAO6BjiHYTyZkTqXEZY5kvRcF3EFIDeYCsxCiJJJQzep9BAEdiNR6XdepyMbsbb3r3?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/GLLb-WE4L1pRHuwGQbsP1qJNiyrdhFTs3wQi9z-puYfNasX1EcZp3R5_3sh7Ve7SuzyUMj2r1Af_F1SUZ6pcG6TzEas8Po9LF-kQhV1jElE-jHxhSZ9uGPP4E-rFEJQ7KRQSkl5pn7DFYa13kNzD7ZxAY6k7A5OvcDrS1UU1bF9z_zi6FrtBeBUBBdEzZYSc?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/y-KfAB8Hz69DqjrLXy2695f2BUTxyKCYTMj691Cp9ZczZE0-7dRMW1ykmH3e9bcYFroInDAYkKvcxuBVdreIGoXF3ie6pBioe5fiBdlz_UkHLCBn4TKWLzRxWeoc4Qw6UKSuRqTR-49tyOe-vnZDErnfqmBb5wiM6vs7uxZ2c_SPpFMqzEO0KnhYb3E4C5Na?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/J_GI--iB31nG-Zp6SsPhl63v5FjnCO3lkBtBY40cA8BTw08eaC8sMoXWE_jXM_L8BGNImfR9EMV-zoIYrAEB8mXuG7Lmd1fk1eSJMMfUu5mim8ZpJ3fCPQasgX6-jtQa60GIBzdKIrH6lDSCqVrCpOd59iurY7_6VVcc0I2bvWXQXj3Zkd0OTSIAv6dJW76I?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/jwCeZQ9QJaFmdTqm7zWS0onBzrA6qjhv8KrAvfkQJ0gLnAhHvAZjsu6lhKTuCr6mLqQpx-x24FBjsgTcwqK3zzBRNkJjQBx_I1w2W_FGDd5YFn9hqxgYkmo0RZhKsVc_DR9ta-qGhgj6Dao9qXUAxzm-YEFun-qHgwUlZUPeyY6dL7ze_ykXMsESQA-dTJyk?purpose=fullsize)

Tesseract là OCR engine.

Nó nhận ảnh:

```text
PIL.Image / image file
```

và nhận dạng:

```text
text
```

Ngoài text, Tesseract còn có thể cung cấp:

```text
confidence
bounding box
page
block
paragraph
line
word
```

Đây chính là thứ chúng ta cần để xây PDF Reader/OCR Pipeline.

---

# 2. Có hai phần cần phân biệt

Python package:

```bash
pip install pytesseract
```

**không phải Tesseract engine itself**.

Kiến trúc:

```text
Python
  │
  ▼
pytesseract
  │
  ▼
Tesseract executable
  │
  ▼
OCR
```

`pytesseract` là Python wrapper giao tiếp với Tesseract.

Do đó chỉ:

```bash
pip install pytesseract
```

chưa chắc đã chạy OCR được nếu máy chưa có Tesseract executable.

---

# 3. Kiểm tra Tesseract

Sau khi cài Tesseract trên hệ điều hành, kiểm tra:

```bash
tesseract --version
```

Nếu Windows không nhận:

```text
'tesseract' is not recognized...
```

thì cần cấu hình PATH hoặc chỉ rõ executable path trong Python.

Ví dụ:

```python
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
```

**Không hard-code path này vào Application Layer.**

Nó thuộc Infrastructure/configuration.

---

# 4. Cài Python wrapper

```bash
pip install pytesseract
```

Kiểm tra:

```python
import pytesseract

print(
    pytesseract.get_tesseract_version()
)
```

Nếu chạy được, Python đã giao tiếp được với Tesseract.

---

# 5. OCR đơn giản nhất

```python
import pytesseract

text = pytesseract.image_to_string(
    image,
    lang="eng",
)

print(text)
```

Đây là:

```text
Image
 ↓
Tesseract
 ↓
str
```

Nhưng architecture của project chúng ta không nên dừng ở đây.

---

# 6. Vì sao không dùng trực tiếp `image_to_string()`?

Vì ta sẽ mất nhiều thông tin.

Ví dụ:

```python
text = pytesseract.image_to_string(image)
```

chỉ cho:

```text
Hello world
```

Trong khi chúng ta có thể cần:

```text
Hello
confidence = 96
bbox = (...)
```

hoặc:

```text
world
confidence = 91
bbox = (...)
```

Vì vậy cần:

```python
pytesseract.image_to_data()
```

---

# 7. Thiết kế `OcrResult`

Ta nâng cấp model từ Buổi 32.

```python
# domain/ocr.py

from dataclasses import dataclass


@dataclass(frozen=True)
class OcrWord:
    text: str
    confidence: float | None
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float | None
    words: tuple[OcrWord, ...]
```

Bây giờ:

```text
OcrResult
 ├── text
 ├── confidence
 └── words
      ├── OcrWord
      ├── OcrWord
      └── OcrWord
```

---

# 8. Vì sao `tuple`?

Kết quả OCR sau khi tạo ra thường không nên bị thay đổi tùy tiện.

Do đó:

```python
words: tuple[OcrWord, ...]
```

thay vì:

```python
words: list[OcrWord]
```

Đây là một domain model immutable hơn.

---

# 9. Tesseract trả dữ liệu gì?

`image_to_data()` có thể trả các cột dạng:

```text
level
page_num
block_num
par_num
line_num
word_num
left
top
width
height
conf
text
```

Ví dụ:

```text
text       left  top  width height conf
Chapter    120   80   150   40    96.2
One        280   80   70    40    94.8
```

Ta chuyển dữ liệu này thành:

```python
OcrWord(...)
```

Đây chính là nhiệm vụ của Infrastructure Adapter.

---

# 10. TesseractOcrEngine

```python
# infrastructure/ocr/tesseract.py

from PIL import Image
import pytesseract

from domain.ocr import (
    OcrResult,
    OcrWord,
)


class TesseractOcrEngine:

    def __init__(
        self,
        language: str = "eng",
    ):
        self.language = language

    def recognize(
        self,
        image: Image.Image,
    ) -> OcrResult:

        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            output_type=(
                pytesseract.Output.DICT
            ),
        )

        words = []

        for i, text in enumerate(
            data["text"]
        ):

            text = text.strip()

            if not text:
                continue

            confidence = float(
                data["conf"][i]
            )

            word = OcrWord(
                text=text,
                confidence=(
                    confidence
                    if confidence >= 0
                    else None
                ),
                left=int(data["left"][i]),
                top=int(data["top"][i]),
                width=int(data["width"][i]),
                height=int(data["height"][i]),
            )

            words.append(word)

        full_text = "\n".join(
            word.text
            for word in words
        )

        valid_confidences = [
            word.confidence
            for word in words
            if word.confidence is not None
        ]

        average_confidence = (
            sum(valid_confidences)
            / len(valid_confidences)
            if valid_confidences
            else None
        )

        return OcrResult(
            text=full_text,
            confidence=average_confidence,
            words=tuple(words),
        )
```

Đây là adapter thực sự:

```text
Tesseract
    ↓
raw dict
    ↓
Domain model
```

---

# 11. Nhưng có một vấn đề

Đoạn:

```python
full_text = "\n".join(
    word.text
    for word in words
)
```

không giữ được layout thật.

Ví dụ:

```text
Chapter One

The story begins here.
```

có thể biến thành:

```text
Chapter
One
The
story
begins
here
```

Trong OCR production, ta cần bảo toàn:

```text
block
paragraph
line
word
```

Do đó đây chỉ là phiên bản **Buổi 35 cơ bản**.

Chúng ta sẽ cải thiện cấu trúc OCR ở Buổi 37.

---

# 12. `PSM` — Page Segmentation Mode

Đây là tham số rất quan trọng của Tesseract.

Tesseract phải biết:

> "Ảnh này chứa kiểu bố cục gì?"

Ví dụ:

```text
PSM 3
```

thường dùng cho automatic page segmentation.

```text
PSM 6
```

phù hợp khi ảnh được coi là một block text duy nhất.

```text
PSM 7
```

phù hợp một dòng text.

```text
PSM 8
```

một từ.

```text
PSM 13
```

raw line.

Không nên học PSM như những con số rời rạc; nó là **giả định về layout đầu vào**.

---

# 13. Thêm PSM vào Engine

```python
class TesseractOcrEngine:

    def __init__(
        self,
        language: str = "eng",
        psm: int = 3,
    ):
        if psm < 0 or psm > 13:
            raise ValueError(
                "PSM phải trong khoảng 0..13"
            )

        self.language = language
        self.psm = psm
```

Sau đó:

```python
config = f"--psm {self.psm}"
```

và:

```python
data = pytesseract.image_to_data(
    image,
    lang=self.language,
    config=config,
    output_type=pytesseract.Output.DICT,
)
```

---

# 14. OEM

Tesseract cũng có:

```text
OEM = OCR Engine Mode
```

Nó liên quan đến engine recognition mà Tesseract sử dụng.

Ví dụ:

```text
--oem 3
```

là một lựa chọn phổ biến để Tesseract tự lựa chọn engine phù hợp.

Ta có thể cấu hình:

```python
class TesseractOcrEngine:

    def __init__(
        self,
        language="eng",
        psm=3,
        oem=3,
    ):
        self.language = language
        self.psm = psm
        self.oem = oem
```

Config:

```python
config = (
    f"--oem {self.oem} "
    f"--psm {self.psm}"
)
```

Không nên hard-code tất cả option vào Application.

---

# 15. Domain Configuration

Tốt hơn là tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TesseractOptions:
    language: str = "eng"
    psm: int = 3
    oem: int = 3

    def __post_init__(self):

        if not self.language:
            raise ValueError(
                "language không được rỗng"
            )

        if not 0 <= self.psm <= 13:
            raise ValueError(
                "psm phải trong [0, 13]"
            )

        if not 0 <= self.oem <= 3:
            raise ValueError(
                "oem phải trong [0, 3]"
            )
```

Engine:

```python
class TesseractOcrEngine:

    def __init__(
        self,
        options: TesseractOptions,
    ):
        self.options = options
```

---

# 16. Language

Ví dụ:

```text
eng
```

English.

Tiếng Việt:

```text
vie
```

Có thể dùng nhiều language:

```text
eng+vie
```

Ví dụ:

```python
options = TesseractOptions(
    language="vie+eng",
)
```

Điều kiện là language data tương ứng phải được cài trong Tesseract.

---

# 17. Tại sao `vie+eng` hữu ích?

Tài liệu có thể chứa:

```text
Chương 1

The beginning of the story...
```

Nếu chỉ:

```text
eng
```

tiếng Việt có thể nhận dạng kém.

Nếu:

```text
vie+eng
```

Tesseract có thêm language model phù hợp.

Nhưng nhiều language hơn cũng có thể:

```text
tăng thời gian OCR
```

và đôi khi làm recognition không tốt hơn.

Không phải:

```text
language càng nhiều → càng tốt
```

---

# 18. Tesseract Adapter hoàn chỉnh

Ta gom lại:

```python
from PIL import Image
import pytesseract

from domain.ocr import (
    OcrResult,
    OcrWord,
)
from domain.tesseract import (
    TesseractOptions,
)


class TesseractOcrEngine:

    def __init__(
        self,
        options: TesseractOptions,
    ):
        self.options = options

    def recognize(
        self,
        image: Image.Image,
    ) -> OcrResult:

        config = (
            f"--oem {self.options.oem} "
            f"--psm {self.options.psm}"
        )

        data = pytesseract.image_to_data(
            image,
            lang=self.options.language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        words = []

        for i, raw_text in enumerate(
            data["text"]
        ):

            text = raw_text.strip()

            if not text:
                continue

            raw_confidence = float(
                data["conf"][i]
            )

            confidence = (
                raw_confidence
                if raw_confidence >= 0
                else None
            )

            words.append(
                OcrWord(
                    text=text,
                    confidence=confidence,
                    left=int(data["left"][i]),
                    top=int(data["top"][i]),
                    width=int(data["width"][i]),
                    height=int(data["height"][i]),
                )
            )

        text = " ".join(
            word.text
            for word in words
        )

        confidences = [
            word.confidence
            for word in words
            if word.confidence is not None
        ]

        average = (
            sum(confidences)
            / len(confidences)
            if confidences
            else None
        )

        return OcrResult(
            text=text,
            confidence=average,
            words=tuple(words),
        )
```

---

# 19. `text` và `words` là hai thứ khác nhau

Ta có:

```text
OcrResult
```

với:

```text
text
```

để đọc nhanh.

Và:

```text
words
```

để xử lý cấu trúc.

Ví dụ:

```python
result.text
```

cho:

```text
Chapter One The story begins
```

Trong khi:

```python
result.words
```

cho:

```text
[
    OcrWord(...),
    OcrWord(...),
    OcrWord(...),
]
```

Sau này có thể dựng lại:

```text
Word
 ↓
Line
 ↓
Paragraph
 ↓
Page
```

---

# 20. Bounding Box

Tesseract trả:

```text
left
top
width
height
```

Đây là image coordinate:

```text
(0,0)
 ┌───────────────────────→ x
 │
 │
 │
 ↓
 y
```

Trong khi PDF:

```text
        y
        ↑
        │
        │
(0,0) ──┼────────→ x
```

Đây chính là kiến thức **Buổi 27 — Coordinate System** quay trở lại.

---

# 21. Chuyển OCR BBox về PDF

Giả sử:

```text
image width  = W
image height = H
```

Tesseract:

```text
left = x
top = y
width = w
height = h
```

Ta có image box:

```text
left   = x
top    = y
right  = x + w
bottom = y + h
```

Muốn chuyển về hệ PDF, cần biết:

```text
scale
page size
rotation
crop
```

Ví dụ đơn giản, không rotation/crop:

```text
PDF x = image_x / scale

PDF y_top    = H - image_top
PDF y_bottom = H - image_bottom
```

Đây là lý do **không được bỏ qua coordinate system**.

---

# 22. Tesseract + OpenCV

Bây giờ ghép Buổi 34:

```python
pipeline = ImagePipeline([
    CvGrayscaleProcessor(),
    MedianBlurProcessor(3),
    OtsuThresholdProcessor(),
])
```

Tesseract:

```python
ocr_engine = TesseractOcrEngine(
    TesseractOptions(
        language="vie+eng",
        psm=3,
        oem=3,
    )
)
```

Renderer:

```python
renderer = PdfiumRenderer(
    "book.pdf"
)
```

Service:

```python
service = PdfOcrService(
    renderer=renderer,
    image_processor=pipeline,
    ocr_engine=ocr_engine,
)
```

---

# 23. Toàn bộ pipeline

```text
                    book.pdf
                       │
                       ▼
                ┌──────────────┐
                │ pypdfium2    │
                │ PdfRenderer   │
                └──────┬───────┘
                       │
                       ▼
                    PIL.Image
                       │
                       ▼
                ┌──────────────┐
                │ ImagePipeline│
                └──────┬───────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
         Grayscale  Median     Otsu
             │         │         │
             └─────────┼─────────┘
                       ▼
                    PIL.Image
                       │
                       ▼
                Tesseract OCR
                       │
                       ▼
                  OcrResult
                  ├── text
                  ├── confidence
                  └── words
                       │
                       ▼
                   TXT / DB
```

---

# 24. PdfOcrService vẫn không đổi

Đây là thành quả của kiến trúc.

```python
service = PdfOcrService(
    renderer,
    pipeline,
    ocr_engine,
)
```

Application không biết:

```text
pypdfium2
OpenCV
Pillow
Tesseract
```

Nó chỉ biết:

```text
Renderer
Processor
OcrEngine
```

Đây chính là:

```text
Dependency Inversion
Dependency Injection
Ports & Adapters
```

---

# 25. CLI

Ta có thể cho phép:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --lang vie+eng \
    --psm 3 \
    --oem 3 \
    --output result.txt
```

Hoặc:

```bash
python -m pdf_ocr book.pdf \
    --dpi 200 \
    --lang vie \
    --psm 6 \
    --output result.txt
```

---

# 26. PSM nào nên thử?

Với một trang sách thông thường:

```text
--psm 3
```

là điểm bắt đầu hợp lý.

Nếu ảnh đã crop thành một block text:

```text
--psm 6
```

có thể phù hợp hơn.

Nếu chỉ OCR một dòng:

```text
--psm 7
```

Nếu chỉ một từ:

```text
--psm 8
```

Không nên cố định:

```text
PSM = 6
```

cho mọi loại PDF.

---

# 27. Confidence

Giả sử:

```text
word 1 = 98
word 2 = 97
word 3 = 43
word 4 = 95
```

Có thể thấy:

```text
word 3
```

đáng nghi ngờ.

Sau này:

```text
confidence < 60
```

có thể:

```text
retry OCR
```

với pipeline khác.

Ví dụ:

```text
OCR #1
   ↓
confidence thấp
   ↓
grayscale
   ↓
adaptive threshold
   ↓
OCR #2
```

Đây là một architecture rất hữu ích.

---

# 28. OCR Retry Strategy

Sau này có thể:

```text
             Image
               │
               ▼
           OCR Profile 1
               │
        confidence < 70?
          /          \
        No            Yes
        │              │
        ▼              ▼
      accept       Profile 2
                       │
                       ▼
                     OCR
```

Ví dụ:

```text
Profile 1
Grayscale
 ↓
Tesseract

Profile 2
Grayscale
 ↓
MedianBlur
 ↓
AdaptiveThreshold
 ↓
Tesseract
```

Buổi 36 sẽ đi sâu hơn vào chiến lược xử lý scan.

---

# 29. Test Tesseract Adapter

Unit test không nhất thiết phải gọi Tesseract thật.

Ta test Application bằng Fake:

```python
class FakeOcrEngine:

    def recognize(self, image):

        return OcrResult(
            text="Hello OCR",
            confidence=99.0,
            words=(
                OcrWord(
                    text="Hello",
                    confidence=99.0,
                    left=10,
                    top=10,
                    width=50,
                    height=20,
                ),
            ),
        )
```

Test:

```python
def test_service():

    service = PdfOcrService(
        renderer=fake_renderer,
        image_processor=NoOpProcessor(),
        ocr_engine=FakeOcrEngine(),
    )

    result = service.recognize_page(
        0,
        RenderOptions(dpi=150),
    )

    assert result.text == "Hello OCR"
    assert result.confidence == 99.0
```

---

# 30. Integration test

Test Tesseract thật nên tách riêng:

```text
tests/
├── unit/
│   ├── test_service.py
│   └── test_domain.py
│
└── integration/
    └── test_tesseract.py
```

Vì integration test phụ thuộc:

```text
Tesseract executable
language data
environment
```

Không nên để mọi unit test đều phụ thuộc Tesseract.

---

# 31. Integration test đơn giản

Nếu có một ảnh test:

```python
from PIL import Image

import pytesseract


def test_tesseract():

    image = Image.open(
        "tests/data/simple_text.png"
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng",
    )

    assert "Hello" in text
```

Đây mới là:

```text
Python
 ↓
pytesseract
 ↓
Tesseract executable
 ↓
real OCR
```

---

# 32. Một vấn đề thực tế: Tesseract không nhận trực tiếp PDF

Đừng thiết kế:

```python
tesseract(pdf)
```

Thay vào đó:

```text
PDF
 ↓
pypdfium2
 ↓
PIL.Image
 ↓
Tesseract
```

Đây chính là lý do project của chúng ta dùng `pypdfium2`.

---

# 33. Render DPI và Tesseract

Ví dụ:

```python
RenderOptions(
    dpi=100
)
```

ảnh có thể quá nhỏ.

```python
RenderOptions(
    dpi=300
)
```

ảnh lớn hơn đáng kể.

Nhưng:

```text
DPI ↑
 ↓
pixels ↑
 ↓
RAM ↑
 ↓
OCR time ↑
```

Do đó không nên mặc định:

```text
300 DPI cho mọi PDF
```

Một workflow thực tế:

```text
150–200 DPI
 ↓
test OCR
 ↓
nếu confidence thấp
 ↓
300 DPI
```

---

# 34. OCR Pipeline production

Từ những gì đã học, architecture bắt đầu trở thành:

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
              Preprocessing
                     │
            ┌────────┴────────┐
            │                 │
         Pillow            OpenCV
            │                 │
            └────────┬────────┘
                     ▼
                   Image
                     │
                     ▼
                Tesseract
                     │
                     ▼
                 OcrResult
              ┌──────┼──────┐
              │      │      │
             Text Confidence BBox
```

---

# 35. Project structure sau Buổi 35

```text
pdf_ocr/
│
├── domain/
│   ├── __init__.py
│   ├── ocr.py
│   ├── options.py
│   └── tesseract.py
│
├── application/
│   ├── __init__.py
│   ├── ports.py
│   └── service.py
│
├── infrastructure/
│   ├── pdfium/
│   │   └── renderer.py
│   │
│   ├── pillow/
│   │   └── processors.py
│   │
│   ├── opencv/
│   │   └── processors.py
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
    │   └── test_processors.py
    │
    └── integration/
        └── test_tesseract.py
```

---

# 36. SOLID nhìn từ project

### SRP

```text
PdfiumRenderer
```

chỉ:

```text
PDF → Image
```

```text
OpenCvProcessor
```

chỉ:

```text
Image → Image
```

```text
TesseractOcrEngine
```

chỉ:

```text
Image → OcrResult
```

---

### OCP

Muốn thêm:

```text
EasyOCR
```

không cần sửa:

```text
PdfOcrService
```

Chỉ thêm:

```python
class EasyOcrEngine:
    ...
```

---

### DIP

Application phụ thuộc:

```text
OcrEngine Protocol
```

không phụ thuộc:

```text
pytesseract
```

---

# 37. Một điểm rất quan trọng: `pytesseract` không phải Domain

Không được:

```python
# domain/ocr.py

import pytesseract
```

Sai architecture.

Đúng:

```text
domain
  ↑
application
  ↑
infrastructure
       │
       └── pytesseract
```

Tesseract là external technology.

---

# 38. Bài tập thực hành

### Bài 1

Cài:

```bash
pip install pytesseract
```

và cài Tesseract executable.

Kiểm tra:

```python
import pytesseract

print(
    pytesseract.get_tesseract_version()
)
```

---

### Bài 2

Viết:

```text
TesseractOptions
```

có:

```text
language
psm
oem
```

---

### Bài 3

Viết:

```text
OcrWord
OcrResult
```

---

### Bài 4

Viết:

```text
TesseractOcrEngine
```

sử dụng:

```python
pytesseract.image_to_data()
```

---

### Bài 5

Ghép:

```text
pypdfium2
+
OpenCV
+
Tesseract
```

thành:

```text
PDF → OCR
```

---

# 39. Bài tập quan trọng nhất

Thử ba pipeline:

### Pipeline A

```text
Render 150 DPI
 ↓
Tesseract
```

### Pipeline B

```text
Render 200 DPI
 ↓
Grayscale
 ↓
Tesseract
```

### Pipeline C

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
processing time
OCR text
confidence
```

Đây là cách học OCR tốt hơn rất nhiều so với chỉ học API.

---

# 40. Roadmap

```text
31. PDF → Image                  ✅
32. PDF → OCR                    ✅
33. pypdfium2 + Pillow           ✅
34. pypdfium2 + OpenCV           ✅
35. pypdfium2 + Tesseract        ✅
36. Xử lý PDF scan               ⬜
37. Detect vùng text             ⬜
38. Parallel rendering           ⬜
39. Streaming / batch processing ⬜
40. Mini Project: PDF OCR        ⬜
```

## Kết luận Buổi 35

Bây giờ chúng ta đã có một pipeline OCR thực sự:

```text
                 PDF
                  │
                  ▼
             pypdfium2
                  │
                  ▼
              PIL.Image
                  │
                  ▼
        Pillow / OpenCV
                  │
                  ▼
              PIL.Image
                  │
                  ▼
             Tesseract
                  │
                  ▼
             OcrResult
          ┌───────┼────────┐
          ▼       ▼        ▼
        text  confidence   words
                            │
                            └── bbox
```

Điểm quan trọng nhất không phải `pytesseract.image_to_string()`, mà là chúng ta đã biến Tesseract thành một **adapter triển khai `OcrEngine`**. Vì vậy toàn bộ Application Layer vẫn độc lập với Tesseract.

**Buổi 36 — Xử lý PDF scan** sẽ đưa pipeline này vào tình huống thực tế hơn: scan nghiêng, nền xám, noise, trang đen, chữ mờ, độ phân giải khác nhau, tự động chọn preprocessing profile và retry OCR khi confidence thấp.
