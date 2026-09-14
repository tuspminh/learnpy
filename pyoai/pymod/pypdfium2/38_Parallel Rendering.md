# Buổi 38 — Parallel Rendering

Theo đúng roadmap **Phần IV — PDF Processing Pipeline**, hôm nay chúng ta học:

> **Render nhiều trang PDF song song bằng Python**

Đây là bước rất quan trọng vì pipeline hiện tại của chúng ta đang xử lý:

```text
PDF
 ↓
Render page 1
 ↓
OCR
 ↓
Render page 2
 ↓
OCR
 ↓
...
```

Với PDF 500–1000 trang, xử lý tuần tự có thể rất chậm.

Hôm nay ta sẽ thiết kế:

```text
PDF
 │
 ├── Page 1 ──→ Worker 1
 ├── Page 2 ──→ Worker 2
 ├── Page 3 ──→ Worker 3
 └── Page 4 ──→ Worker 4
                    ↓
                  Results
```

nhưng phải đặc biệt chú ý **thread safety, memory và resource lifetime**.

---

# 1. Trước tiên: có nên parallel không?

Không phải cứ:

```python
ThreadPoolExecutor(max_workers=20)
```

là nhanh hơn.

Pipeline của chúng ta có nhiều công đoạn:

```text
PDF
 ↓
pypdfium2 rendering
 ↓
PIL
 ↓
OpenCV
 ↓
Tesseract
```

Mỗi công đoạn có đặc tính khác nhau.

| Công đoạn     | Đặc điểm    |
| ------------- | ----------- |
| PDF rendering | CPU/native  |
| Pillow        | CPU/native  |
| OpenCV        | CPU/native  |
| Tesseract     | CPU/process |
| ghi file      | I/O         |

Do đó cần đo thực tế.

---

# 2. Sequential hiện tại

Ví dụ:

```python
for page_index in range(100):
    image = renderer.render_page(
        page_index,
        options,
    )

    try:
        processed = processor.process(image)

        try:
            result = ocr.recognize(processed)

        finally:
            processed.close()

    finally:
        image.close()
```

Luồng:

```text
Page 1
  ↓
Render
  ↓
Process
  ↓
OCR
  ↓
Page 2
  ↓
Render
  ↓
Process
  ↓
OCR
```

Chỉ có một page đang được xử lý.

---

# 3. Parallel processing

Ta muốn:

```text
                  ┌── Page 1 → Worker
                  │
PDF ──────────────┼── Page 2 → Worker
                  │
                  ├── Page 3 → Worker
                  │
                  └── Page 4 → Worker
```

Có hai hướng phổ biến:

```text
ThreadPoolExecutor
ProcessPoolExecutor
```

---

# 4. Thread hay Process?

## ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
```

Phù hợp khi:

* I/O nhiều
* thư viện native nhả GIL
* muốn chia sẻ object dễ hơn

Nhưng:

> Không nên mặc định giả định `pypdfium2.PdfDocument` có thể được nhiều thread dùng đồng thời một cách an toàn.

Đây là lý do kiến trúc của chúng ta phải cẩn thận.

---

# 5. Sai lầm phổ biến

Không nên làm:

```python
renderer = PdfiumRenderer("book.pdf")

with ThreadPoolExecutor(8) as executor:
    executor.map(
        renderer.render_page,
        range(renderer.page_count),
    )
```

Vì tất cả worker cùng truy cập:

```text
             PdfDocument
             /   |   \
            /    |    \
        Thread Thread Thread
```

Ta đang chia sẻ một resource native quan trọng giữa nhiều thread.

Thiết kế an toàn hơn là:

```text
Worker 1
 └── PdfDocument riêng

Worker 2
 └── PdfDocument riêng

Worker 3
 └── PdfDocument riêng
```

---

# 6. Nguyên tắc mới

Thay vì:

```text
1 PDF
 ↓
N threads
```

ta có:

```text
N workers
 ↓
mỗi worker có resource lifecycle riêng
```

Ví dụ:

```text
Worker 1 → open PDF → render → close
Worker 2 → open PDF → render → close
Worker 3 → open PDF → render → close
```

Tuy nhiên mở PDF riêng cho từng task sẽ có overhead.

Do đó ta cần phân biệt:

### Task-level resource

```text
mỗi page:
open PDF
render
close PDF
```

→ quá tốn.

### Worker-level resource

```text
worker start
    ↓
open PDF
    ↓
render nhiều pages
    ↓
worker end
    ↓
close PDF
```

→ tốt hơn.

---

# 7. Thiết kế Worker

Ta tạo một worker độc lập.

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderTask:
    pdf_path: Path
    page_index: int
    dpi: float
```

Worker:

```python
def render_page(task: RenderTask):

    renderer = PdfiumRenderer(task.pdf_path)

    try:
        renderer.open()

        image = renderer.render_page(
            task.page_index,
            RenderOptions(dpi=task.dpi),
        )

        return image

    finally:
        renderer.close()
```

Nhưng vẫn có vấn đề:

> Image được trả ra ngoài worker và giữ trong RAM.

Nếu:

```text
100 pages
```

được submit cùng lúc:

```text
Worker
 ↓
Image
 ↓
Future
 ↓
RAM
```

có thể rất lớn.

---

# 8. Đừng trả Image về nếu không cần

Đây là nguyên tắc rất quan trọng.

Sai:

```text
Worker
 ↓
PIL.Image
 ↓
main process
 ↓
save
```

Tốt hơn:

```text
Worker
 ↓
render
 ↓
process
 ↓
save
 ↓
close
 ↓
return metadata
```

Tức:

```text
Worker owns image lifetime
```

Ví dụ:

```python
@dataclass(frozen=True)
class RenderResult:
    page_index: int
    output_path: str
```

Worker chỉ trả:

```text
RenderResult
```

chứ không trả:

```text
PIL.Image
```

---

# 9. Render worker hoàn chỉnh

Ví dụ cho việc render PDF thành PNG:

```python
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


@dataclass(frozen=True)
class RenderTask:
    pdf_path: Path
    page_index: int
    output_dir: Path
    dpi: float


@dataclass(frozen=True)
class RenderResult:
    page_index: int
    output_path: Path


def render_one_page(
    task: RenderTask,
) -> RenderResult:

    pdf = pdfium.PdfDocument(task.pdf_path)

    try:
        page = pdf[task.page_index]

        bitmap = page.render(scale=task.dpi / 72.0)

        image = bitmap.to_pil()

        try:
            task.output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = task.output_dir / f"page-{task.page_index + 1:04d}.png"

            image.save(
                output_path,
                format="PNG",
            )

            return RenderResult(
                page_index=task.page_index,
                output_path=output_path,
            )

        finally:
            image.close()

    finally:
        pdf.close()
```

Lưu ý lifecycle:

```text
PdfDocument
    ↓
page
    ↓
bitmap
    ↓
PIL.Image
    ↓
save
    ↓
close image
    ↓
close PDF
```

---

# 10. ThreadPoolExecutor

Bây giờ:

```python
from concurrent.futures import ThreadPoolExecutor
```

Ta tạo tasks:

```python
tasks = [
    RenderTask(
        pdf_path=pdf_path,
        page_index=i,
        output_dir=output_dir,
        dpi=150,
    )
    for i in range(page_count)
]
```

Chạy:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(
            render_one_page,
            task,
        )
        for task in tasks
    ]

    for future in futures:
        result = future.result()

        print(f"Page {result.page_index + 1}: {result.output_path}")
```

---

# 11. Nhưng cách trên có một vấn đề

Ta tạo:

```python
futures = [...]
```

cho toàn bộ 1000 pages.

Không phải quá lớn về bản thân `Future`, nhưng với pipeline lớn, ta thường muốn:

```text
bounded submission
```

thay vì:

```text
submit 10000 tasks
```

---

# 12. `executor.map()`

Có thể đơn giản hóa:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    for result in executor.map(
        render_one_page,
        tasks,
    ):
        print(result)
```

Điểm hay:

* code đơn giản
* giới hạn số worker

Nhưng cần hiểu thứ tự.

Nếu:

```text
Page 1 chậm
Page 2 nhanh
Page 3 nhanh
```

`map()` có thể chờ page 1 trước khi trả kết quả page 2/3 theo thứ tự input.

Nếu không cần thứ tự hoàn thành, có thể dùng:

```python
as_completed()
```

---

# 13. `as_completed()`

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(
            render_one_page,
            task,
        ): task
        for task in tasks
    }

    for future in as_completed(futures):
        task = futures[future]

        try:
            result = future.result()

        except Exception as exc:
            print(f"Page {task.page_index + 1} lỗi: {exc}")

        else:
            print(f"Done page {result.page_index + 1}")
```

Bây giờ:

```text
Page 1 ──────── 10s
Page 2 ─ 2s
Page 3 ─ 3s

Result:
Page 2
Page 3
Page 1
```

Kết quả hoàn thành theo thời gian thực.

---

# 14. Nếu cần output đúng thứ tự?

Không cần worker phải hoàn thành đúng thứ tự.

Chúng ta có:

```python
result.page_index
```

nên có thể:

```python
results.sort(key=lambda x: x.page_index)
```

hoặc tốt hơn:

```text
output filename:
page-0001.png
page-0002.png
page-0003.png
```

Filesystem đã giúp giữ thứ tự logic.

---

# 15. Parallel Rendering Service

Ta xây abstraction:

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)


class ParallelRenderService:
    def __init__(
        self,
        max_workers: int = 4,
    ):
        if max_workers <= 0:
            raise ValueError("max_workers phải > 0")

        self.max_workers = max_workers

    def render(
        self,
        tasks,
    ):

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    render_one_page,
                    task,
                ): task
                for task in tasks
            }

            for future in as_completed(futures):
                result = future.result()

                results.append(result)

        return sorted(
            results,
            key=lambda x: x.page_index,
        )
```

---

# 16. Tuy nhiên OCR mới là phần đáng chú ý

Nếu pipeline:

```text
Render
 ↓
OCR
```

thì parallel cả pipeline thường tốt hơn chỉ parallel render:

```text
Worker
 ├── Render
 ├── Preprocess
 ├── OCR
 └── Save
```

Thay vì:

```text
Parallel render
       ↓
Images queue
       ↓
Sequential OCR
```

vì cách thứ hai có thể tạo:

```text
100 images
 ↓
RAM
```

---

# 17. Pipeline worker đúng hơn

```text
             PDF
              │
      ┌───────┼───────┐
      ↓       ↓       ↓
   Worker  Worker  Worker
      │       │       │
   Render   Render   Render
      ↓       ↓       ↓
   OpenCV  OpenCV  OpenCV
      ↓       ↓       ↓
  Tesseract Tesseract Tesseract
      ↓       ↓       ↓
    Save    Save    Save
      │       │       │
      └───────┼───────┘
              ↓
           Metadata
```

Mỗi worker xử lý trọn lifecycle của page.

---

# 18. Worker cho OCR

```python
def process_page(task):

    pdf = pdfium.PdfDocument(task.pdf_path)

    try:
        page = pdf[task.page_index]

        bitmap = page.render(scale=task.dpi / 72.0)

        image = bitmap.to_pil()

        try:
            processed = task.processor.process(image)

            try:
                result = task.ocr_engine.recognize(processed)

                task.writer.save(
                    result,
                    task.page_index,
                )

                return result.confidence

            finally:
                processed.close()

        finally:
            image.close()

    finally:
        pdf.close()
```

Nhưng đoạn này lại xuất hiện một vấn đề kiến trúc:

```python
task.processor
task.ocr_engine
```

được truyền vào worker.

Nếu dùng ProcessPool:

```text
pickle
```

sẽ trở thành vấn đề.

Vì vậy:

> **ThreadPool dễ tích hợp dependency injection hơn ProcessPool.**

---

# 19. ThreadPool và ProcessPool

### ThreadPool

```text
Main process
│
├── Thread
├── Thread
├── Thread
└── Thread
```

Object có thể chia sẻ.

### ProcessPool

```text
Process
│
├── Process
├── Process
├── Process
└── Process
```

Object phải serialize/pickle khi truyền giữa process.

Không nên truyền:

```text
PdfDocument
PIL.Image
cv2 object
Tesseract object
```

một cách tùy tiện qua ProcessPool.

---

# 20. Khi nào dùng ProcessPool?

Nếu workload CPU-bound mạnh:

```text
OpenCV
+
OCR
```

thì ProcessPool có thể đáng cân nhắc.

Kiến trúc tốt:

```text
Main
 ↓
PageTask
 ↓
Process
 ↓
worker tự tạo dependencies
 ↓
process
 ↓
save
 ↓
return metadata
```

Ví dụ task chỉ chứa dữ liệu serializable:

```python
@dataclass(frozen=True)
class OcrTask:
    pdf_path: str
    page_index: int
    dpi: int
    output_path: str
```

Không chứa:

```python
pdfium.PdfDocument
```

hay:

```python
PIL.Image
```

---

# 21. Memory — vấn đề quan trọng nhất

Giả sử:

```text
A4
300 DPI
RGB
≈ 26 MB
```

Nếu:

```text
8 workers
```

thì chỉ riêng ảnh đang xử lý có thể:

```text
8 × 26 MB
≈ 208 MB
```

Chưa tính:

* bitmap PDFium
* OpenCV NumPy array
* intermediate images
* Tesseract
* Python overhead

Có thể dễ dàng lên:

```text
300–500 MB+
```

Vì vậy:

> Số worker không nên chọn chỉ dựa vào số CPU.

---

# 22. Công thức thực tế

Nếu mỗi page cần khoảng:

```text
30 MB
```

và:

```text
8 workers
```

thì tối thiểu:

```text
8 × 30 = 240 MB
```

Nhưng thực tế nên dự phòng nhiều hơn.

Ví dụ máy có:

```text
RAM = 8 GB
```

không có nghĩa:

```python
max_workers = 32
```

là tốt.

Có thể:

```text
4 workers
```

nhanh hơn 32 worker do:

* memory pressure
* context switching
* CPU contention
* Tesseract contention
* I/O contention.

---

# 23. Thêm semaphore để giới hạn

Trong một số pipeline:

```text
render
 ↓
OCR
```

ta có thể muốn:

```text
8 render workers
2 OCR workers
```

vì OCR nặng hơn.

Kiến trúc:

```text
Render Pool
     ↓
 Queue
     ↓
OCR Pool
     ↓
Writer
```

Đây là bước tiến tới:

> **Producer / Consumer Pipeline**

mà sau này rất hữu ích cho crawler của bạn.

---

# 24. Đừng parallel vô hạn

Không:

```python
ThreadPoolExecutor(max_workers=page_count)
```

Nếu PDF có:

```text
1000 pages
```

thì:

```text
1000 workers
```

là thảm họa.

Thay vào đó:

```python
workers = min(
    4,
    page_count,
)
```

hoặc cấu hình:

```bash
--workers 4
```

---

# 25. Test architecture

Đây là điểm user đã học nhiều ở DDD/SOLID nên chúng ta áp dụng ngay.

Không cần unit test thật với PDF.

Ta tạo:

```python
class FakeRenderer:
    def __init__(self):
        self.calls = []

    def render_page(
        self,
        page_index,
        options,
    ):
        self.calls.append(page_index)
        return FakeImage()
```

và:

```python
class FakeImage:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
```

Test:

```python
def test_parallel_service():

    service = ParallelRenderService(max_workers=2)

    ...
```

Điểm cần test:

```text
✓ tất cả page được xử lý
✓ page index không mất
✓ exception được xử lý
✓ worker count hợp lệ
✓ resource được đóng
✓ kết quả được sort
```

---

# 26. Exception handling

Parallel processing có thêm một vấn đề:

```text
Page 17 lỗi
```

Ta không muốn:

```text
1000 pages
 ↓
Page 17 error
 ↓
Toàn bộ pipeline crash
```

Thay vào đó:

```text
Page 1 ✓
Page 2 ✓
...
Page 17 ✗
...
Page 18 ✓
...
```

Ta cần result:

```python
@dataclass(frozen=True)
class PageProcessResult:
    page_index: int
    success: bool
    output_path: str | None = None
    error: str | None = None
```

Ví dụ:

```text
Page 17
success = False
error = "OCR timeout"
```

Đây chính là nền tảng cho:

```text
retry failed pages
```

sau này.

---

# 27. Kiến trúc production hơn

Ta có:

```text
PageTask
   ↓
Worker
   ↓
PageProcessResult
```

Worker không cần biết toàn bộ hệ thống.

```text
Application
     │
     ▼
ParallelProcessor
     │
     ▼
PageTask
     │
     ├───────────────┐
     ▼               ▼
 Worker 1          Worker 2
     │               │
     ▼               ▼
 Result            Result
     │               │
     └───────┬───────┘
             ▼
      Result Collector
```

---

# 28. Điều này liên hệ trực tiếp với crawler của bạn

Đây chính là kiến trúc tương tự crawler:

```text
Page URLs
    ↓
Queue
    ↓
Workers
    ↓
HTTP fetch
    ↓
Parse
    ↓
Save
```

Còn PDF OCR:

```text
Page indexes
    ↓
Queue
    ↓
Workers
    ↓
Render
    ↓
Preprocess
    ↓
OCR
    ↓
Save
```

Tức kiến thức hôm nay không chỉ dùng cho PDF.

Nó chính là nền tảng của:

* crawler workers
* task queues
* RQ
* multiprocessing
* async worker architecture
* batch processing.

---

# 29. Một phiên bản service hoàn chỉnh

Ta có thể bắt đầu bằng abstraction đơn giản:

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageTask:
    pdf_path: Path
    page_index: int
    dpi: float


@dataclass(frozen=True)
class PageResult:
    page_index: int
    success: bool
    error: str | None = None


class ParallelPageService:
    def __init__(
        self,
        worker,
        max_workers: int = 4,
    ):
        if max_workers <= 0:
            raise ValueError("max_workers phải > 0")

        self.worker = worker
        self.max_workers = max_workers

    def process(
        self,
        tasks: list[PageTask],
    ) -> list[PageResult]:

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.worker,
                    task,
                ): task
                for task in tasks
            }

            for future in as_completed(futures):
                task = futures[future]

                try:
                    future.result()

                    results.append(
                        PageResult(
                            page_index=task.page_index,
                            success=True,
                        )
                    )

                except Exception as exc:
                    results.append(
                        PageResult(
                            page_index=task.page_index,
                            success=False,
                            error=str(exc),
                        )
                    )

        return sorted(
            results,
            key=lambda result: result.page_index,
        )
```

Đây là một abstraction rất đáng giữ.

Nó không biết:

```text
PDF
OCR
Tesseract
OpenCV
```

Nó chỉ biết:

```text
Task → Worker → Result
```

Đây là **Dependency Inversion** rất rõ.

---

# 30. Kiến trúc sau Buổi 38

Hiện tại pipeline đã tiến tới:

```text
                         PDF
                          │
                          ▼
                     Page Tasks
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
             Worker    Worker    Worker
                │         │         │
                ▼         ▼         ▼
             Render    Render    Render
                │         │         │
                ▼         ▼         ▼
             OpenCV    OpenCV    OpenCV
                │         │         │
                ▼         ▼         ▼
           Tesseract Tesseract Tesseract
                │         │         │
                ▼         ▼         ▼
              Save      Save      Save
                │         │         │
                └─────────┼─────────┘
                          ▼
                    Page Results
```

---

# 31. Ba nguyên tắc cần nhớ

### 1. Không share native resource bừa bãi

Không mặc định:

```text
1 PdfDocument
    ↓
20 threads
```

### 2. Worker nên sở hữu resource

```text
Worker
 ↓
open
 ↓
process
 ↓
save
 ↓
close
```

### 3. Không giữ Image lâu hơn cần thiết

```text
render
 ↓
process
 ↓
OCR
 ↓
save
 ↓
close
```

thay vì:

```text
render 100 pages
 ↓
RAM
 ↓
OCR
```

---

# 32. Roadmap chúng ta đã đi đến đâu?

```text
31 PDF → Image                 ✓
32 PDF → OCR                   ✓
33 pypdfium2 + Pillow          ✓
34 pypdfium2 + OpenCV          ✓
35 pypdfium2 + Tesseract       ✓
36 Xử lý PDF scan              ✓
37 Detect vùng text            ✓
38 Parallel rendering          ← hôm nay
39 Streaming / batch processing
40 Mini Project: PDF OCR Pipeline
```

### Bài tập Buổi 38

Hãy lấy một PDF khoảng **20–100 trang** và benchmark:

```text
workers = 1
workers = 2
workers = 4
workers = 8
```

Đo:

```text
total time
pages/second
RAM sử dụng
CPU usage
```

Mục tiêu không phải tìm `workers` lớn nhất, mà tìm:

> **điểm cân bằng giữa throughput và memory.**

Và đặc biệt, hãy nhớ kiến trúc quan trọng nhất của hôm nay:

```text
PageTask
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

Đây chính là pattern mà chúng ta sẽ dùng tiếp ở **Buổi 39 — Streaming / Batch Processing**, nơi chúng ta giải quyết bài toán lớn hơn:

```text
1000 pages
     ↓
KHÔNG load 1000 pages
     ↓
bounded queue
     ↓
workers
     ↓
process từng batch
     ↓
giải phóng memory
```
