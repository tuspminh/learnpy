# Buổi 39 — Streaming / Batch Processing

Theo đúng roadmap, hôm nay chúng ta giải quyết bài toán:

> **PDF rất lớn nhưng không được phép load toàn bộ vào RAM.**

Sau Buổi 38, chúng ta đã có:

```text
PageTask
   ↓
Worker Pool
   ↓
Render
   ↓
Process
   ↓
OCR
   ↓
Save
```

Nhưng nếu có:

```text
PDF = 2.000 trang
```

thì cách:

```python
tasks = [PageTask(...) for i in range(2000)]
```

và submit toàn bộ một lúc **không phải kiến trúc tối ưu**.

Hôm nay ta xây:

```text
PDF 2000 pages
       ↓
   Streaming
       ↓
  Batch nhỏ
       ↓
┌──────┬──────┬──────┐
│1-20  │21-40 │41-60 │ ...
└──────┴──────┴──────┘
       ↓
 Workers
       ↓
 Save
       ↓
 Release memory
```

---

# 1. Streaming và Batch khác nhau thế nào?

Hai khái niệm này liên quan nhưng không giống nhau.

## Streaming

Xử lý từng item khi nó xuất hiện:

```text
Page 1 → process
Page 2 → process
Page 3 → process
...
```

Không cần có toàn bộ danh sách trong RAM.

Ví dụ:

```python
for page_index in range(page_count):
    process(page_index)
```

---

## Batch

Chia dữ liệu thành từng nhóm:

```text
Pages:

1 2 3 ... 20
      ↓
Batch 1

21 22 ... 40
      ↓
Batch 2
```

Ví dụ:

```python
for batch in batches:
    process_batch(batch)
```

---

# 2. Vì sao cần hai kỹ thuật?

Giả sử:

```text
10.000 pages
```

Nếu tạo:

```python
tasks = [...]
```

thì bản thân task objects có thể chưa quá lớn.

Nhưng nếu submit rồi giữ:

```text
Future
 ↓
Image
 ↓
Result
```

thì memory có thể tăng mạnh.

Đặc biệt nguy hiểm khi worker trả về:

```python
PIL.Image
```

thay vì:

```python
PageResult
```

---

# 3. Nguyên tắc của hôm nay

Chúng ta muốn:

```text id="2y8d7w"
Input
 ↓
Generator
 ↓
bounded batch
 ↓
Worker pool
 ↓
Output
 ↓
release
 ↓
batch tiếp theo
```

Chứ không:

```text id="q6a2pi"
Input
 ↓
Load tất cả
 ↓
Process tất cả
 ↓
RAM tăng
```

---

# 4. Generator tạo PageTask

Ta bắt đầu rất đơn giản.

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageTask:
    pdf_path: Path
    page_index: int
    dpi: float


def iter_page_tasks(
    pdf_path: Path,
    page_count: int,
    dpi: float,
):
    for page_index in range(page_count):
        yield PageTask(
            pdf_path=pdf_path,
            page_index=page_index,
            dpi=dpi,
        )
```

Điểm quan trọng:

```python
yield
```

không tạo toàn bộ:

```text
PageTask 1
PageTask 2
...
PageTask 10000
```

ngay lập tức.

Nó tạo:

```text
PageTask 1
↓
consumer
↓
PageTask 2
↓
consumer
↓
...
```

---

# 5. Test Generator

```python
def test_iter_page_tasks():

    tasks = iter_page_tasks(
        Path("book.pdf"),
        page_count=3,
        dpi=200,
    )

    first = next(tasks)

    assert first.page_index == 0

    second = next(tasks)

    assert second.page_index == 1
```

Ta chỉ tạo task khi cần.

---

# 6. Chia generator thành batch

Đây là utility rất quan trọng.

```python
from itertools import islice


def batched(iterable, size):

    if size <= 0:
        raise ValueError("size phải > 0")

    iterator = iter(iterable)

    while True:
        batch = list(
            islice(
                iterator,
                size,
            )
        )

        if not batch:
            break

        yield batch
```

Sử dụng:

```python
tasks = iter_page_tasks(
    Path("book.pdf"),
    1000,
    200,
)

for batch in batched(tasks, 20):
    print(
        "Batch:",
        batch[0].page_index,
        "→",
        batch[-1].page_index,
    )
```

Kết quả:

```text
Batch: 0 → 19
Batch: 20 → 39
Batch: 40 → 59
...
```

---

# 7. Python mới có `itertools.batched`

Nếu Python version của bạn hỗ trợ, có thể dùng:

```python
from itertools import batched
```

thay vì tự viết helper.

Ví dụ:

```python
for batch in batched(tasks, 20):
    process_batch(batch)
```

Tự viết helper ở trên vẫn rất tốt để **học cách streaming hoạt động**.

---

# 8. Batch processing với ThreadPool

Ta kết hợp với Buổi 38.

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)


class BatchProcessor:
    def __init__(
        self,
        worker,
        max_workers=4,
    ):
        if max_workers <= 0:
            raise ValueError("max_workers phải > 0")

        self.worker = worker
        self.max_workers = max_workers

    def process_batch(
        self,
        tasks,
    ):

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
                    result = future.result()

                except Exception as exc:
                    results.append(
                        (
                            task,
                            exc,
                        )
                    )

                else:
                    results.append(
                        (
                            task,
                            result,
                        )
                    )

        return results
```

---

# 9. Streaming toàn bộ PDF

Bây giờ:

```python
def process_pdf(
    pdf_path,
    page_count,
    dpi,
    worker,
    batch_size=20,
    max_workers=4,
):

    processor = BatchProcessor(
        worker=worker,
        max_workers=max_workers,
    )

    tasks = iter_page_tasks(
        pdf_path,
        page_count,
        dpi,
    )

    for batch in batched(
        tasks,
        batch_size,
    ):
        results = processor.process_batch(batch)

        for task, result in results:
            yield task, result
```

Đây là **streaming pipeline**.

---

# 10. Memory lúc này như thế nào?

Giả sử:

```text
PDF = 2.000 pages
batch_size = 20
workers = 4
```

Ta không có:

```text
2000 images
```

mà gần như:

```text
Batch 20
 ↓
maximum vài worker đang giữ image
 ↓
save
 ↓
release
 ↓
Batch tiếp
```

Đây chính là mục tiêu.

---

# 11. Nhưng `batch_size=20` có nghĩa 20 images trong RAM?

**Không nhất thiết.**

Batch chứa:

```text
PageTask
```

không phải:

```text
PIL.Image
```

Ví dụ:

```text
Batch
├── PageTask 1
├── PageTask 2
├── ...
└── PageTask 20
```

Worker mới tạo:

```text
PIL.Image
```

khi thực sự xử lý.

Nếu worker:

```text
render
 ↓
OCR
 ↓
save
 ↓
close
```

thì số image sống đồng thời gần với:

```text
max_workers
```

chứ không phải:

```text
batch_size
```

---

# 12. Đây là điểm cực kỳ quan trọng

Có ba loại giới hạn:

```text
batch_size
max_workers
memory
```

Không được nhầm:

```text
batch_size = số image trong RAM
```

Không đúng.

Thông thường:

```text
batch_size
≈ số task được submit trong một đợt

max_workers
≈ số task thực sự chạy đồng thời
```

---

# 13. Nhưng vẫn có một vấn đề

Đoạn:

```python
futures = {executor.submit(...) for task in batch}
```

vẫn tạo tất cả Future của batch.

Nếu:

```text
batch_size = 10.000
```

thì lại quay về vấn đề cũ.

Vì vậy:

```text
batch_size
```

nên có giới hạn hợp lý.

Ví dụ:

```text
20
50
100
```

chứ không phải:

```text
10000
```

---

# 14. Producer → Consumer

Đây là mô hình tổng quát:

```text
Producer
   │
   │ PageTask
   ▼
┌─────────────┐
│    Queue    │
└──────┬──────┘
       │
       ├── Worker 1
       ├── Worker 2
       ├── Worker 3
       └── Worker 4
              │
              ▼
           Results
```

Queue có thể **bounded**:

```text
maxsize=20
```

Điều này cực kỳ quan trọng.

Nếu worker chậm:

```text
Queue đầy
```

producer phải chờ.

Đó gọi là:

> **Backpressure**

---

# 15. Backpressure là gì?

Ví dụ:

```text
Producer
  ↓
1000 pages/sec
```

nhưng worker chỉ xử lý:

```text
10 pages/sec
```

Nếu queue không giới hạn:

```text
1000
2000
3000
4000
...
```

task tồn đọng ngày càng nhiều.

Nếu queue có:

```text
maxsize=20
```

thì:

```text
Producer
   ↓
Queue 20
   ↓
FULL
   ↓
Producer BLOCK
```

Worker xử lý bớt:

```text
Queue 19
```

Producer lại tiếp tục.

Đây chính là **flow control**.

---

# 16. Queue pipeline

Với Python:

```python
from queue import Queue
```

Ta có thể tạo:

```python
queue = Queue(maxsize=20)
```

Producer:

```python
def producer(
    queue,
    tasks,
):

    for task in tasks:
        queue.put(task)

    queue.put(None)
```

`None` ở đây có thể dùng làm sentinel:

```text
None
 ↓
Producer kết thúc
```

Nhưng nếu có nhiều worker thì cần nhiều sentinel.

---

# 17. Worker loop

```python
def worker(
    queue,
    process,
):

    while True:
        task = queue.get()

        try:
            if task is None:
                return

            process(task)

        finally:
            queue.task_done()
```

Luồng:

```text
queue
 ↓
worker lấy task
 ↓
process
 ↓
task_done()
```

---

# 18. Nhiều worker

Ví dụ:

```python
from threading import Thread
from queue import Queue


def run_workers(
    tasks,
    process,
    worker_count=4,
    queue_size=20,
):

    queue = Queue(maxsize=queue_size)

    threads = []

    for _ in range(worker_count):
        thread = Thread(
            target=worker,
            args=(
                queue,
                process,
            ),
        )

        thread.start()

        threads.append(thread)

    for task in tasks:
        queue.put(task)

    for _ in range(worker_count):
        queue.put(None)

    queue.join()

    for thread in threads:
        thread.join()
```

Đây là một implementation cơ bản của:

```text
Producer → Bounded Queue → Workers
```

---

# 19. Tại sao không dùng queue vô hạn?

Không nên:

```python
Queue()
```

nếu producer có thể chạy nhanh hơn consumer rất nhiều.

Nên:

```python
Queue(maxsize=20)
```

hoặc:

```python
Queue(maxsize=50)
```

Tùy workload.

---

# 20. Resource lifecycle

Trong worker PDF:

```python
def process_page(task):

    pdf = pdfium.PdfDocument(task.pdf_path)

    try:
        page = pdf[task.page_index]

        bitmap = page.render(scale=task.dpi / 72)

        image = bitmap.to_pil()

        try:
            # processing
            ...

        finally:
            image.close()

    finally:
        pdf.close()
```

Điểm quan trọng:

```text
Worker
 ↓
PDF open
 ↓
render
 ↓
image
 ↓
process
 ↓
save
 ↓
image.close()
 ↓
PDF close
```

Không được:

```text
Worker
 ↓
render 100 pages
 ↓
giữ 100 images
 ↓
OCR
```

---

# 21. Streaming OCR Pipeline hoàn chỉnh

Ta có thể hình dung:

```text
                         PDF
                          │
                          ▼
                   PageTask Generator
                          │
                          ▼
                    Bounded Queue
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       Worker 1        Worker 2        Worker 3
          │               │               │
       Render           Render           Render
          ↓               ↓               ↓
       OpenCV           OpenCV           OpenCV
          ↓               ↓               ↓
      Tesseract        Tesseract        Tesseract
          ↓               ↓               ↓
        Save            Save            Save
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                       Results
```

---

# 22. Xử lý lỗi không làm chết pipeline

Ví dụ:

```text
Page 1 ✓
Page 2 ✓
Page 3 ✗
Page 4 ✓
Page 5 ✓
```

Worker nên tạo:

```python
@dataclass(frozen=True)
class PageResult:
    page_index: int
    success: bool
    error: str | None = None
```

Khi lỗi:

```python
try:
    process(task)

except Exception as exc:
    result = PageResult(
        page_index=task.page_index,
        success=False,
        error=str(exc),
    )
```

Sau đó ghi:

```text
failed_pages.json
```

Ví dụ:

```json
[
    {
        "page_index": 2,
        "error": "OCR timeout"
    },
    {
        "page_index": 37,
        "error": "PDFium error"
    }
]
```

Đây chính là nền tảng để sau này:

```text
retry failed pages
```

---

# 23. Resume processing

Đây là một lợi ích rất lớn của batch/streaming.

Giả sử:

```text
PDF = 1000 pages
```

đã xử lý:

```text
1–730 ✓
```

process crash.

Không nên:

```text
restart → page 1
```

Ta lưu:

```text
completed:
1
2
3
...
730
```

hoặc output:

```text
page-0001.txt
...
page-0730.txt
```

Khi restart:

```python
if output_path.exists():
    skip
```

Kết quả:

```text
731 → tiếp tục
```

Đây là **checkpoint/resume**.

---

# 24. Batch rất phù hợp với checkpoint

Ví dụ:

```text
Batch 1
1–50 ✓
checkpoint

Batch 2
51–100 ✓
checkpoint

Batch 3
101–150 ✓
checkpoint
```

Nếu crash tại:

```text
Page 127
```

ta có thể:

```text
resume từ batch 3
```

hoặc chính xác hơn:

```text
resume từ page 127
```

---

# 25. Batch size không nên quá nhỏ

Ví dụ:

```text
batch_size = 1
```

thì:

```text
submit
wait
submit
wait
...
```

overhead tăng.

### Quá lớn

```text
batch_size = 10000
```

thì:

```text
queue/futures
memory
error handling
```

khó kiểm soát.

### Điểm cân bằng

Thường bắt đầu thử:

```text
10
20
50
100
```

sau đó benchmark.

Không có con số universal.

---

# 26. Streaming output

Một nguyên tắc nữa:

Không:

```python
results = []

for ...:
    results.append(result)
```

với hàng triệu result nếu không cần.

Thay vào đó:

```python
for result in process_pdf(...):
    writer.write(result)
```

Tức:

```text
process
 ↓
write
 ↓
release
 ↓
next
```

---

# 27. Đây chính là Generator Pipeline

Python rất mạnh ở mô hình:

```text
generator
   ↓
generator
   ↓
generator
```

Ví dụ:

```python
tasks = iter_page_tasks(...)

batches = batched(
    tasks,
    20,
)

for batch in batches:
    results = processor.process_batch(batch)

    for result in results:
        writer.write(result)
```

Dữ liệu chảy qua pipeline.

Không cần:

```text
load everything
```

---

# 28. So sánh 3 kiến trúc

### Cách 1 — All at once

```text
1000 pages
 ↓
1000 tasks
 ↓
1000 futures
 ↓
memory
```

Không tốt cho workload lớn.

---

### Cách 2 — Batch

```text
1000 pages
 ↓
20 tasks
 ↓
process
 ↓
20 tasks
 ↓
process
```

Tốt hơn.

---

### Cách 3 — Bounded Queue

```text
Generator
 ↓
Queue(maxsize=20)
 ↓
Workers
```

Đây là hướng production mạnh hơn vì có:

```text
backpressure
```

---

# 29. Với project PDF OCR của chúng ta

Kiến trúc hiện tại:

```text
pdf_ocr/
│
├── domain/
│   ├── ocr.py
│   ├── options.py
│   ├── tesseract.py
│   ├── scan.py
│   ├── image_geometry.py
│   └── text_region.py
│
├── application/
│   ├── ports.py
│   ├── service.py
│   ├── scan_ocr.py
│   ├── region_ocr.py
│   └── batch.py
│
├── infrastructure/
│   ├── pdfium/
│   │   └── renderer.py
│   ├── pillow/
│   │   ├── processors.py
│   │   └── cropper.py
│   ├── opencv/
│   │   ├── processors.py
│   │   ├── scan_processor.py
│   │   └── text_detector.py
│   └── ocr/
│       └── tesseract.py
│
└── presentation/
    └── cli.py
```

Ta đang có đủ các abstraction để Buổi 40 ghép lại.

---

# 30. Một thiết kế Batch Processor sạch hơn

Ta có thể định nghĩa:

```python
from typing import Iterable


class BatchProcessor:
    def __init__(
        self,
        worker,
        batch_size=20,
    ):
        if batch_size <= 0:
            raise ValueError("batch_size phải > 0")

        self.worker = worker
        self.batch_size = batch_size

    def process(
        self,
        tasks: Iterable,
    ):

        for batch in batched(
            tasks,
            self.batch_size,
        ):
            for task in batch:
                yield self.worker(task)
```

Đây là phiên bản tuần tự.

Sau đó thay implementation bằng parallel mà Application không cần thay đổi API.

Đây chính là:

> **OCP — Open/Closed Principle**

---

# 31. Streaming + Parallel

Phiên bản concept:

```text
iter_tasks()
      ↓
batch
      ↓
ThreadPool
      ↓
results
      ↓
writer
```

Code:

```python
def stream_parallel(
    tasks,
    worker,
    batch_size=20,
    max_workers=4,
):

    for batch in batched(
        tasks,
        batch_size,
    ):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    worker,
                    task,
                )
                for task in batch
            ]

            for future in as_completed(futures):
                yield future.result()
```

Có thể cải thiện thêm bằng cách giữ một executor xuyên suốt các batch thay vì tạo lại executor mỗi batch:

```python
def stream_parallel(
    tasks,
    worker,
    batch_size=20,
    max_workers=4,
):

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for batch in batched(
            tasks,
            batch_size,
        ):
            futures = [
                executor.submit(
                    worker,
                    task,
                )
                for task in batch
            ]

            for future in as_completed(futures):
                yield future.result()
```

Đây là phiên bản nên ưu tiên.

---

# 32. Memory model

Hãy ghi nhớ sơ đồ này:

```text
                    batch_size
                        │
                        ▼
                  ┌──────────┐
Generator ──────→ │  Tasks   │
                  └────┬─────┘
                       │
                       ▼
                  max_workers
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Image     Image     Image
             │         │         │
             ▼         ▼         ▼
           OCR       OCR       OCR
             │         │         │
             ▼         ▼         ▼
           close     close     close
```

Trong đó:

```text
batch_size
```

kiểm soát lượng task đang được đưa vào một đợt.

```text
max_workers
```

kiểm soát concurrency.

```text
image.close()
```

kiểm soát lifetime của image.

---

# 33. Ba thứ cần benchmark

Khi xử lý PDF lớn, đừng chỉ đo:

```text
total time
```

Hãy đo:

```text
1. throughput
2. peak memory
3. CPU utilization
```

Ví dụ:

| Workers | Batch | Pages/s | Peak RAM |
| ------: | ----: | ------: | -------: |
|       1 |    20 |     0.8 |   100 MB |
|       2 |    20 |     1.5 |   180 MB |
|       4 |    20 |     2.7 |   330 MB |
|       8 |    20 |     2.9 |   650 MB |

Trong ví dụ này:

```text
8 workers
```

không đáng dùng.

`4 workers` có thể là điểm cân bằng tốt hơn.

---

# 34. Kết nối với hệ thống crawler của bạn

Kiến thức hôm nay cực kỳ gần với crawler architecture mà bạn đang xây:

```text
Crawler
   ↓
URL Generator
   ↓
Bounded Queue
   ↓
Workers
   ↓
Fetch
   ↓
Parse
   ↓
Save
```

PDF OCR:

```text
OCR
   ↓
Page Generator
   ↓
Bounded Queue
   ↓
Workers
   ↓
Render
   ↓
Preprocess
   ↓
Tesseract
   ↓
Save
```

Cấu trúc tư duy giống nhau gần như hoàn toàn.

---

# 35. Tổng kết Buổi 39

Chúng ta đã giải quyết bài toán:

```text
PDF rất lớn
```

bằng:

### Streaming

```text
yield page/task
```

### Batch

```text
10–100 tasks / batch
```

### Parallel

```text
ThreadPool / Worker Pool
```

### Bounded queue

```text
Queue(maxsize=N)
```

### Backpressure

```text
Producer nhanh
      ↓
Queue đầy
      ↓
Producer chờ
```

### Resource lifecycle

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

### Checkpoint

```text
completed pages
       ↓
resume
```

---

# Roadmap hiện tại

```text
31 PDF → Image                    ✓
32 PDF → OCR                      ✓
33 pypdfium2 + Pillow             ✓
34 pypdfium2 + OpenCV             ✓
35 pypdfium2 + Tesseract          ✓
36 Xử lý PDF scan                 ✓
37 Detect vùng text               ✓
38 Parallel rendering             ✓
39 Streaming / batch processing   ✓
40 Mini Project: PDF OCR Pipeline ← tiếp theo
```

## Buổi 40 sẽ là bài quan trọng nhất của Phần IV

Chúng ta sẽ **không chỉ viết demo**, mà ghép toàn bộ kiến thức thành một project hoàn chỉnh:

```text
                    PDF
                     ↓
              PdfiumRenderer
                     ↓
               PIL.Image
                     ↓
              ScanProcessor
                     ↓
             TextRegionDetector
                     ↓
              Region Cropper
                     ↓
               Tesseract OCR
                     ↓
              Confidence Check
                     ↓
                 Retry
                     ↓
              PageOcrResult
                     ↓
              Streaming Writer
                     ↓
              final .txt / JSON
```

và tổ chức thành:

```text
Presentation
      ↓
Application
      ↓
Ports
      ↓
Infrastructure
```

với **CLI + DI + fake implementations + unit tests + integration test + parallel workers + batch + retry + checkpoint**, để kết thúc trọn vẹn **Phần IV — PDF Processing Pipeline**.
