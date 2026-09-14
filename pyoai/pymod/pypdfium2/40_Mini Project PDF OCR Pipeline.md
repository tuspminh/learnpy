# Phần IV — PDF Processing Pipeline

# Buổi 40 — Mini Project: PDF OCR Pipeline

Đây là **bài tổng kết Phần IV**. Chúng ta sẽ ghép toàn bộ kiến thức từ Buổi 31–39 thành một pipeline hoàn chỉnh:

```text
                    PDF
                     │
                     ▼
              ┌─────────────┐
              │ pypdfium2   │
              │   Renderer  │
              └──────┬──────┘
                     │ PIL.Image
                     ▼
              ┌─────────────┐
              │ Preprocess  │
              │ Pillow/OpenCV
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  Tesseract  │
              │     OCR     │
              └──────┬──────┘
                     │ OcrResult
                     ▼
              ┌─────────────┐
              │ Text Writer │
              └─────────────┘
                     │
                     ▼
                 result.txt
```

Đồng thời áp dụng:

* Clean Architecture
* SOLID
* Dependency Injection
* Protocol
* Streaming
* Batch processing
* Parallel workers
* Memory-safe processing
* Checkpoint/resume

---

# 1. Mục tiêu project

Ta muốn chạy:

```bash
python -m pdf_ocr_pipeline book.pdf
```

hoặc:

```bash
python -m pdf_ocr_pipeline book.pdf \
    --output result.txt \
    --dpi 200 \
    --lang vie+eng \
    --psm 3 \
    --workers 4 \
    --batch-size 10
```

Pipeline:

```text
PDF
 │
 ├── Page 1 ──┐
 ├── Page 2 ──┤
 ├── Page 3 ──┤
 │             │
 ▼             ▼
Page Generator → Batch → Workers
                         │
                         ├── Render
                         ├── Preprocess
                         ├── OCR
                         └── Close resources
                                  │
                                  ▼
                              PageResult
                                  │
                                  ▼
                              TextWriter
```

Điểm quan trọng:

> **Không bao giờ load toàn bộ PDF thành hàng trăm PIL.Image cùng lúc.**

---

# 2. Project structure

Ta xây dựng:

```text
pdf_ocr_pipeline/
│
├── __init__.py
├── __main__.py
│
├── domain/
│   ├── __init__.py
│   ├── models.py
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
│   ├── opencv/
│   │   ├── __init__.py
│   │   └── processor.py
│   │
│   ├── tesseract/
│   │   ├── __init__.py
│   │   └── engine.py
│   │
│   └── writer/
│       ├── __init__.py
│       └── text.py
│
└── presentation/
    ├── __init__.py
    └── cli.py
```

---

# 3. Domain

## `domain/models.py`

```python
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
    page_index: int
    page_number: int
    text: str
    confidence: float | None
    words: tuple[OcrWord, ...]


@dataclass(frozen=True)
class PageResult:
    page_index: int
    success: bool
    ocr: OcrResult | None = None
    error: str | None = None
```

Ta có hai tầng:

```text
OcrResult
    ↓
PageResult
```

`OcrResult` chứa kết quả OCR.

`PageResult` chứa trạng thái xử lý page.

---

# 4. Domain options

## `domain/options.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PdfOcrOptions:
    dpi: float = 200.0
    language: str = "eng"
    psm: int = 3
    oem: int = 3

    def __post_init__(self):
        if self.dpi <= 0:
            raise ValueError("dpi phải > 0")

        if not self.language:
            raise ValueError("language không được rỗng")

        if not 0 <= self.psm <= 13:
            raise ValueError("psm phải trong [0, 13]")

        if not 0 <= self.oem <= 3:
            raise ValueError("oem phải trong [0, 3]")
```

Domain không biết:

```text
pypdfium2
Pillow
OpenCV
Tesseract
```

Đây là nguyên tắc rất quan trọng.

---

# 5. Application ports

## `application/ports.py`

```python
from pathlib import Path
from typing import Protocol

from PIL import Image

from domain.models import OcrResult
from domain.options import PdfOcrOptions


class PdfRenderer(Protocol):
    def render_page(
        self,
        pdf_path: Path,
        page_index: int,
        dpi: float,
    ) -> Image.Image: ...


class ImageProcessor(Protocol):
    def process(
        self,
        image: Image.Image,
    ) -> Image.Image: ...


class OcrEngine(Protocol):
    def recognize(
        self,
        image: Image.Image,
    ) -> OcrResult: ...


class TextWriter(Protocol):
    def write(
        self,
        result: OcrResult,
    ) -> None: ...
```

Đây là DIP:

```text
Application
     ↓
    Port
     ↑
Adapter
```

Application không phụ thuộc trực tiếp Tesseract.

---

# 6. PDFium renderer

## `infrastructure/pdfium/renderer.py`

```python
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


class PdfiumRenderer:
    def render_page(
        self,
        pdf_path: Path,
        page_index: int,
        dpi: float,
    ) -> Image.Image:

        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        if dpi <= 0:
            raise ValueError("dpi phải > 0")

        pdf = pdfium.PdfDocument(pdf_path)

        try:
            if not 0 <= page_index < len(pdf):
                raise IndexError(page_index)

            page = pdf[page_index]

            bitmap = page.render(
                scale=dpi / 72.0,
            )

            image = bitmap.to_pil()

            return image

        finally:
            pdf.close()
```

Ở đây mỗi worker tự:

```text
open PDF
   ↓
render page
   ↓
close PDF
```

Điều này đơn giản và an toàn hơn việc cho nhiều worker cùng chia sẻ một `PdfDocument`.

---

# 7. OpenCV preprocessing

## `infrastructure/opencv/processor.py`

```python
import cv2
import numpy as np

from PIL import Image


class OpenCvOcrProcessor:
    def __init__(
        self,
        denoise: bool = True,
        threshold: bool = True,
    ):
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

Pipeline preprocessing:

```text
RGB
 ↓
Grayscale
 ↓
Median Blur
 ↓
Otsu
 ↓
OCR
```

Nhưng nhớ:

> Đây chỉ là một OCR profile. Không phải PDF nào cũng nên threshold.

---

# 8. Tesseract adapter

## `infrastructure/tesseract/engine.py`

```python
import pytesseract

from PIL import Image

from domain.models import OcrResult, OcrWord


class TesseractEngine:
    def __init__(
        self,
        language: str = "eng",
        psm: int = 3,
        oem: int = 3,
    ):
        self.language = language
        self.psm = psm
        self.oem = oem

    def recognize(
        self,
        image: Image.Image,
    ) -> OcrResult:

        config = f"--psm {self.psm} --oem {self.oem}"

        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        words = []

        for i, raw_text in enumerate(data["text"]):
            text = raw_text.strip()

            if not text:
                continue

            raw_confidence = float(data["conf"][i])

            confidence = raw_confidence if raw_confidence >= 0 else None

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

        text = " ".join(word.text for word in words)

        confidences = [word.confidence for word in words if word.confidence is not None]

        average = sum(confidences) / len(confidences) if confidences else None

        return OcrResult(
            page_index=-1,
            page_number=-1,
            text=text,
            confidence=average,
            words=tuple(words),
        )
```

Tại đây `TesseractEngine` chỉ quan tâm:

```text
Image
 ↓
Tesseract
 ↓
OcrResult
```

Không biết PDF là gì.

---

# 9. Text writer

## `infrastructure/writer/text.py`

```python
from pathlib import Path

from domain.models import OcrResult


class PlainTextWriter:
    def __init__(self, output_path: Path):
        self.output_path = output_path

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(
        self,
        result: OcrResult,
    ) -> None:

        with self.output_path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(f"\n\n===== PAGE {result.page_number} =====\n\n")

            file.write(result.text)

            file.write("\n")
```

Điểm đáng chú ý:

```python
"a"
```

thay vì:

```python
"w"
```

Vì chúng ta muốn **stream kết quả**.

Không cần:

```python
all_results = []
```

---

# 10. Worker

Bây giờ tới phần quan trọng nhất.

## `application/service.py`

```python
from dataclasses import dataclass
from pathlib import Path

from application.ports import (
    ImageProcessor,
    OcrEngine,
    PdfRenderer,
)
from domain.models import PageResult, OcrResult
from domain.options import PdfOcrOptions


@dataclass(frozen=True)
class PageTask:
    pdf_path: Path
    page_index: int


class PageWorker:
    def __init__(
        self,
        renderer: PdfRenderer,
        processor: ImageProcessor,
        ocr_engine: OcrEngine,
        options: PdfOcrOptions,
    ):
        self.renderer = renderer
        self.processor = processor
        self.ocr_engine = ocr_engine
        self.options = options

    def process(
        self,
        task: PageTask,
    ) -> PageResult:

        image = None
        processed = None

        try:
            image = self.renderer.render_page(
                pdf_path=task.pdf_path,
                page_index=task.page_index,
                dpi=self.options.dpi,
            )

            processed = self.processor.process(image)

            ocr = self.ocr_engine.recognize(processed)

            ocr = OcrResult(
                page_index=task.page_index,
                page_number=task.page_index + 1,
                text=ocr.text,
                confidence=ocr.confidence,
                words=ocr.words,
            )

            return PageResult(
                page_index=task.page_index,
                success=True,
                ocr=ocr,
            )

        except Exception as exc:
            return PageResult(
                page_index=task.page_index,
                success=False,
                error=str(exc),
            )

        finally:
            if processed is not None:
                processed.close()

            if image is not None:
                image.close()
```

Đây là **memory safety**:

```text
render
  ↓
process
  ↓
OCR
  ↓
close processed
  ↓
close original
```

Mỗi worker chỉ giữ những image cần thiết trong thời gian ngắn.

---

# 11. Streaming page tasks

```python
def iter_page_tasks(
    pdf_path: Path,
    page_count: int,
):
    for page_index in range(page_count):
        yield PageTask(
            pdf_path=pdf_path,
            page_index=page_index,
        )
```

Không tạo:

```python
tasks = [
    PageTask(...)
    for ...
]
```

nếu PDF cực lớn.

Generator:

```text
Page 1
 ↓
Page 2
 ↓
Page 3
 ↓
...
```

---

# 12. Batch processing

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)


class ParallelPageProcessor:
    def __init__(
        self,
        worker: PageWorker,
        max_workers: int = 4,
    ):
        if max_workers <= 0:
            raise ValueError("max_workers phải > 0")

        self.worker = worker
        self.max_workers = max_workers

    def process_batch(
        self,
        tasks: list[PageTask],
    ) -> list[PageResult]:

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(
                    self.worker.process,
                    task,
                )
                for task in tasks
            ]

            for future in as_completed(futures):
                results.append(future.result())

        return results
```

---

# 13. Batch helper

```python
from itertools import islice


def batched(iterable, size):

    if size <= 0:
        raise ValueError("size phải > 0")

    iterator = iter(iterable)

    while True:
        batch = list(islice(iterator, size))

        if not batch:
            break

        yield batch
```

Ví dụ:

```python
tasks = range(1, 11)

for batch in batched(tasks, 3):
    print(batch)
```

Kết quả:

```text
[1, 2, 3]
[4, 5, 6]
[7, 8, 9]
[10]
```

---

# 14. Pipeline Service

Đây là application service chính.

```python
class PdfOcrPipeline:
    def __init__(
        self,
        page_processor: ParallelPageProcessor,
        writer,
    ):
        self.page_processor = page_processor
        self.writer = writer

    def run(
        self,
        tasks,
        batch_size: int,
    ):

        for batch in batched(
            tasks,
            batch_size,
        ):
            results = self.page_processor.process_batch(batch)

            # Worker hoàn thành không theo thứ tự.
            results.sort(key=lambda result: result.page_index)

            for result in results:
                if not result.success:
                    print(f"[ERROR] Page {result.page_index + 1}: {result.error}")
                    continue

                self.writer.write(result.ocr)

                print(f"[OK] Page {result.page_index + 1}")
```

---

# 15. Một vấn đề quan trọng: thứ tự page

Parallel worker:

```text
Page 1 ────────────────┐
Page 2 ────────┐       │
Page 3 ──┐     │       │
          ↓     ↓       ↓
        Page 3 Page 2 Page 1
```

`as_completed()` trả về:

```text
Page 3
Page 2
Page 1
```

Nếu ghi ngay:

```python
writer.write(result)
```

thì file có thể thành:

```text
PAGE 3
PAGE 2
PAGE 1
```

Không được.

Vì vậy trong **mỗi batch**:

```python
results.sort(key=lambda result: result.page_index)
```

Sau đó:

```text
Batch 1:
1 2 3 4 5

Batch 2:
6 7 8 9 10
```

Kết quả cuối:

```text
1
2
3
4
5
6
7
8
9
10
```

---

# 16. Nhưng batch vẫn có giới hạn

Giả sử:

```text
1000 pages
batch_size = 20
workers = 4
```

Ta không tạo:

```text
1000 futures
```

mà:

```text
20 tasks
 ↓
4 workers
 ↓
20 results
 ↓
write
 ↓
next 20
```

Memory ổn định hơn nhiều.

---

# 17. CLI

## `presentation/cli.py`

```python
import argparse
from pathlib import Path

from application.service import (
    PageTask,
    PageWorker,
    ParallelPageProcessor,
    PdfOcrPipeline,
    batched,
    iter_page_tasks,
)
from domain.options import PdfOcrOptions
from infrastructure.opencv.processor import (
    OpenCvOcrProcessor,
)
from infrastructure.pdfium.renderer import (
    PdfiumRenderer,
)
from infrastructure.tesseract.engine import (
    TesseractEngine,
)
from infrastructure.writer.text import (
    PlainTextWriter,
)


def build_parser():

    parser = argparse.ArgumentParser(description="PDF OCR Pipeline")

    parser.add_argument(
        "pdf",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("result.txt"),
    )

    parser.add_argument(
        "--dpi",
        type=float,
        default=200,
    )

    parser.add_argument(
        "--lang",
        default="eng",
    )

    parser.add_argument(
        "--psm",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--oem",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--no-threshold",
        action="store_true",
    )

    return parser


def main():

    parser = build_parser()

    args = parser.parse_args()

    options = PdfOcrOptions(
        dpi=args.dpi,
        language=args.lang,
        psm=args.psm,
        oem=args.oem,
    )

    renderer = PdfiumRenderer()

    processor = OpenCvOcrProcessor(
        denoise=True,
        threshold=not args.no_threshold,
    )

    ocr_engine = TesseractEngine(
        language=options.language,
        psm=options.psm,
        oem=options.oem,
    )

    worker = PageWorker(
        renderer=renderer,
        processor=processor,
        ocr_engine=ocr_engine,
        options=options,
    )

    parallel_processor = ParallelPageProcessor(
        worker=worker,
        max_workers=args.workers,
    )

    writer = PlainTextWriter(args.output)

    pipeline = PdfOcrPipeline(
        page_processor=parallel_processor,
        writer=writer,
    )

    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(args.pdf)

    try:
        page_count = len(pdf)
    finally:
        pdf.close()

    tasks = iter_page_tasks(
        args.pdf,
        page_count,
    )

    pipeline.run(
        tasks=tasks,
        batch_size=args.batch_size,
    )
```

---

# 18. `__main__.py`

```python
from presentation.cli import main


if __name__ == "__main__":
    main()
```

---

# 19. Chạy project

Cài Python packages:

```bash
pip install pypdfium2 pillow opencv-python numpy pytesseract
```

Kiểm tra Tesseract:

```bash
tesseract --version
```

Kiểm tra tiếng Việt:

```bash
tesseract --list-langs
```

Phải thấy:

```text
vie
```

nếu muốn:

```bash
--lang vie
```

hoặc:

```bash
--lang vie+eng
```

---

# 20. Chạy OCR

Ví dụ:

```bash
python -m pdf_ocr_pipeline book.pdf
```

Output:

```text
result.txt
```

Hoặc:

```bash
python -m pdf_ocr_pipeline book.pdf \
    --output novel.txt \
    --dpi 200 \
    --lang vie+eng \
    --psm 3 \
    --workers 4 \
    --batch-size 10
```

---

# 21. Pipeline thực tế

Ví dụ PDF 500 trang:

```text
500 pages
    │
    ▼
Generator
    │
    ├── batch 1 → 10 pages
    ├── batch 2 → 10 pages
    ├── batch 3 → 10 pages
    │
    ...
    └── batch 50
```

Mỗi batch:

```text
10 PageTask
     │
     ▼
4 workers
     │
     ├── Worker 1 → render → preprocess → OCR
     ├── Worker 2 → render → preprocess → OCR
     ├── Worker 3 → render → preprocess → OCR
     └── Worker 4 → render → preprocess → OCR
                         │
                         ▼
                     close()
```

Sau đó:

```text
sort page_index
      ↓
write text
      ↓
batch tiếp theo
```

Memory không tăng tuyến tính theo 500 trang.

---

# 22. Checkpoint / Resume

Một pipeline production còn phải xử lý:

```text
500 pages
   ↓
page 327 lỗi
   ↓
program crash
```

Không muốn lần sau OCR lại:

```text
1 → 326
```

Ta có thể tạo:

```text
output/
├── page-0001.txt
├── page-0002.txt
├── ...
└── page-0326.txt
```

Khi restart:

```python
def is_completed(
    output_dir: Path,
    page_index: int,
) -> bool:

    path = output_dir / f"page-{page_index + 1:04d}.txt"

    return path.exists()
```

Sau đó generator:

```python
def iter_pending_tasks(
    pdf_path,
    page_count,
    output_dir,
):

    for page_index in range(page_count):
        if is_completed(
            output_dir,
            page_index,
        ):
            continue

        yield PageTask(
            pdf_path=pdf_path,
            page_index=page_index,
        )
```

Đây chính là:

```text
Checkpoint
    ↓
Crash
    ↓
Restart
    ↓
Skip completed
    ↓
Continue
```

---

# 23. Một cải tiến production quan trọng

Hiện tại:

```text
Worker
 ↓
Tesseract
```

Nếu OCR thất bại:

```text
PageResult(
    success=False
)
```

Ta có thể thêm retry:

```text
OCR profile 1
    │
    ├── confidence >= threshold
    │       ↓
    │      OK
    │
    └── confidence < threshold
            ↓
      profile 2
            ↓
          OCR
```

Ví dụ:

```text
Profile 1
grayscale

Profile 2
grayscale + denoise

Profile 3
grayscale + threshold
```

Đây là bước rất gần với crawler architecture mà bạn đang học:

```text
Request
 ↓
Fetch
 ↓
Check quality
 ↓
Retry
 ↓
Alternative strategy
```

---

# 24. Unit test quan trọng nhất

Ta không muốn unit test phải cài Tesseract.

Tạo fake:

```python
class FakeOcrEngine:
    def recognize(self, image):

        return OcrResult(
            page_index=-1,
            page_number=-1,
            text="Hello OCR",
            confidence=95.0,
            words=(),
        )
```

Fake renderer:

```python
from PIL import Image


class FakeRenderer:
    def render_page(
        self,
        pdf_path,
        page_index,
        dpi,
    ):

        return Image.new(
            "RGB",
            (100, 100),
            "white",
        )
```

Fake processor:

```python
class FakeProcessor:
    def process(self, image):
        return image.copy()
```

Test:

```python
def test_worker():

    worker = PageWorker(
        renderer=FakeRenderer(),
        processor=FakeProcessor(),
        ocr_engine=FakeOcrEngine(),
        options=PdfOcrOptions(),
    )

    task = PageTask(
        pdf_path=Path("dummy.pdf"),
        page_index=0,
    )

    result = worker.process(task)

    assert result.success is True
    assert result.ocr.text == "Hello OCR"
    assert result.ocr.page_number == 1
```

Không cần:

```text
PDF thật
Tesseract thật
OpenCV thật
```

Đây chính là lợi ích của:

```text
Protocol + DI
```

---

# 25. Integration test

Integration test mới kiểm tra:

```text
pypdfium2
      +
Pillow
      +
OpenCV
      +
Tesseract
```

Ví dụ:

```python
def test_real_tesseract():

    engine = TesseractEngine(
        language="eng",
        psm=7,
        oem=3,
    )

    image = Image.new(
        "RGB",
        (800, 200),
        "white",
    )

    # Integration test thực tế nên
    # dùng fixture image có chữ.

    result = engine.recognize(image)

    assert result is not None
```

Nhưng integration test kiểu này cần fixture ảnh thật có text.

---

# 26. Architecture cuối cùng

Đây là kiến trúc chúng ta vừa xây:

```text
                    PRESENTATION
                         │
                         ▼
                       CLI
                         │
                         ▼
                  APPLICATION
                         │
              ┌──────────┴──────────┐
              │                     │
         PageWorker          PipelineService
              │                     │
              ▼                     ▼
            PORTS                PORTS
              │
      ┌───────┼────────┬───────────┐
      ▼       ▼        ▼           ▼
   Renderer Processor OCR        Writer
      │       │        │           │
      ▼       ▼        ▼           ▼
 pypdfium2 OpenCV Tesseract      File
```

Dependency direction:

```text
Presentation
     ↓
Application
     ↓
Domain
```

Infrastructure:

```text
Infrastructure
      ↑
   implements
      ↑
Application Ports
```

Đây là **Dependency Inversion Principle**.

---

# 27. Liên hệ với hệ thống crawler của bạn

Điểm đáng học nhất của project này không phải OCR.

Mà là kiến trúc worker.

PDF:

```text
PageTask
   ↓
Queue/Batch
   ↓
Worker
   ↓
Render
   ↓
Process
   ↓
OCR
   ↓
Save
   ↓
PageResult
```

Crawler:

```text
CrawlTask
   ↓
Queue
   ↓
Worker
   ↓
HTTPX Fetch
   ↓
Parser
   ↓
Validate
   ↓
Repository
   ↓
CrawlResult
```

Hai hệ thống có cùng một abstraction:

```text
             Task
               │
               ▼
             Worker
               │
        ┌──────┴──────┐
        │             │
     Process        Retry
        │             │
        └──────┬──────┘
               ▼
             Result
               │
               ▼
             Save
```

Đây chính là lý do các bài:

* Parallel rendering
* Streaming
* Batch
* Queue
* Worker
* Retry
* Checkpoint

rất quan trọng đối với project crawler của bạn.

---

# 28. Tổng kết toàn bộ Phần IV

Chúng ta đã đi từ:

```text
31 PDF → Image
```

đến:

```text
32 PDF → OCR
```

rồi:

```text
33 Pillow
34 OpenCV
35 Tesseract
36 Scan PDF
37 Text Region Detection
38 Parallel Rendering
39 Streaming / Batch
40 PDF OCR Pipeline
```

Kiến trúc cuối:

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
                OpenCV/Pillow
                      │
                      ▼
                  Tesseract
                      │
                      ▼
                  OcrResult
                      │
                      ▼
                    Save
```

và ở production:

```text
Page Generator
      ↓
Bounded Batch / Queue
      ↓
Worker Pool
      ↓
Render
      ↓
Preprocess
      ↓
OCR
      ↓
Confidence / Retry
      ↓
Save
      ↓
Checkpoint
```

**Như vậy Phần IV — PDF Processing Pipeline đã hoàn thành đủ 40 buổi.**
