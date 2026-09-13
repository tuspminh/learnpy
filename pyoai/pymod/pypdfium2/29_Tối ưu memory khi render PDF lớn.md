# Buổi 29 — Tối ưu Memory khi Render PDF lớn

Đây là bài rất quan trọng trước **Mini Project Buổi 30 — PDF Thumbnail Generator**.

Từ các bài trước, chúng ta đã biết:

```text
PDF Page
   ↓
render()
   ↓
PdfBitmap
   ↓
PIL.Image
```

Vấn đề là nếu PDF có:

```text
500 pages
×
300 DPI
×
A4
```

thì việc render tất cả page rồi giữ trong list có thể ngốn **hàng chục GB RAM**.

Mục tiêu hôm nay:

```text
Không làm:

PDF
 ↓
render 500 pages
 ↓
list[PIL.Image]
 ↓
RAM 💥
```

mà làm:

```text
PDF
 ↓
page 1 → process → release
 ↓
page 2 → process → release
 ↓
page 3 → process → release
 ...
```

---

# 1. Vì sao render PDF lớn tốn RAM?

Giả sử A4:

```text
595.28 × 841.89 pt
```

ở:

```text
300 DPI
```

ta có khoảng:

```text
2480 × 3508 px
```

Số pixel:

```text
2480 × 3508
≈ 8.7 triệu pixels
```

Nếu RGB:

```text
8.7M × 3
≈ 26 MB
```

Nếu RGBA:

```text
8.7M × 4
≈ 35 MB
```

Đây chỉ là **một page**.

---

# 2. Nếu render 100 pages

RGB khoảng:

```text
26 MB × 100
≈ 2.6 GB
```

200 pages:

```text
≈ 5.2 GB
```

500 pages:

```text
≈ 13 GB
```

Đây mới chỉ là phép tính gần đúng cho pixel data.

Trong thực tế còn có:

```text
PIL objects
PdfBitmap
PDFium internal buffers
Python objects
temporary buffers
compressed output buffers
```

nên memory thực tế có thể khác.

---

# 3. Sai lầm kinh điển

Không nên:

```python
images = []

for page_index in range(page_count):
    image = renderer.render_page(
        page_index,
        options,
    )

    images.append(image)
```

Sau vòng lặp:

```text id="w6o6w3"
images
├── page 1
├── page 2
├── page 3
├── ...
└── page 500
```

Tất cả vẫn còn reference.

Python không thể giải phóng chúng vì:

```text
images
```

vẫn giữ chúng.

---

# 4. Memory leak và memory retention không giống nhau

Đây là khái niệm rất quan trọng.

### Memory leak

Object không còn cần nhưng vẫn bị giữ do bug/reference ngoài ý muốn.

### Memory retention

Object vẫn còn được giữ vì chương trình **cố tình giữ reference**.

Ví dụ:

```python
images.append(image)
```

không phải memory leak.

Đó là:

```text
intentional retention
```

Nhưng đối với PDF renderer lớn:

```text
intentional retention
```

có thể trở thành vấn đề.

---

# 5. Pattern đúng: Process → Release

Thay vì:

```text
render all
 ↓
save all
```

ta làm:

```text
render
 ↓
process
 ↓
save
 ↓
release
```

Ví dụ:

```python
for page_index in range(page_count):
    image = renderer.render_page(
        page_index,
        options,
    )

    image.save(
        f"page-{page_index + 1}.png"
    )

    image.close()
```

Nhưng với PIL, cần hiểu rõ `close()` và lifetime của object.

---

# 6. PIL Image lifetime

Một `PIL.Image.Image` là Python object đại diện cho image data.

Ví dụ:

```python
image = bitmap.to_pil()
```

Sau khi xong:

```python
image.close()
```

có thể được dùng khi image không còn cần nữa.

Tuy nhiên:

> Không nên coi `image.close()` là "garbage collector".

Nó là hành động đóng/giải phóng tài nguyên liên quan đến image object.

Nếu còn reference:

```python
images.append(image)
```

thì việc close không biến object thành không tồn tại.

---

# 7. PdfBitmap cũng có lifetime

Một pattern nguy hiểm:

```python
bitmap = page.render(...)

image = bitmap.to_pil()

# giữ bitmap + image
```

Nếu bạn không cần `bitmap` nữa, đừng giữ nó lâu hơn cần thiết.

Pipeline tốt:

```text
PdfPage
   ↓
PdfBitmap
   ↓
PIL.Image
   ↓
save/process
   ↓
release
```

Không:

```text
PdfPage
   ↓
PdfBitmap
   ↓
PIL
   ↓
list
   ↓
500 objects
```

---

# 8. Generator là công cụ rất phù hợp

Chúng ta đã học Generator trong Python Intermediate.

Đây là lúc áp dụng thực tế.

Không:

```python
def render_all():
    return [
        render_page(i)
        for i in range(page_count)
    ]
```

Mà:

```python
def iter_rendered_pages():
    for i in range(page_count):
        yield render_page(i)
```

Điểm khác biệt:

```text
list
 ↓
tạo toàn bộ

generator
 ↓
tạo từng item khi cần
```

---

# 9. `PdfRenderIterator`

Ta xây:

```python
class PdfRenderIterator:

    def __init__(
        self,
        renderer,
        options,
    ):
        self.renderer = renderer
        self.options = options

    def iter_pages(
        self,
        start_page=0,
        end_page=None,
    ):
        if end_page is None:
            end_page = self.renderer.page_count

        for page_index in range(
            start_page,
            end_page,
        ):
            yield self.renderer.render_page(
                page_index,
                self.options,
            )
```

Sử dụng:

```python
for image in iterator.iter_pages():
    image.save(...)
    image.close()
```

---

# 10. Nhưng generator chưa tự động giải phóng

Đây là điểm rất quan trọng.

Code:

```python
for image in iterator.iter_pages():
    images.append(image)
```

vẫn giữ tất cả.

Generator chỉ đảm bảo:

```text
không tạo tất cả ngay lập tức
```

chứ không đảm bảo:

```text
người dùng không giữ chúng.
```

Memory ownership vẫn thuộc caller.

---

# 11. API tốt hơn: callback

Nếu mục tiêu của chúng ta là:

```text
render
 ↓
save
 ↓
release
```

ta có thể tạo service:

```python
class PdfRenderService:

    def process_pages(
        self,
        start_page,
        end_page,
        options,
        processor,
    ):
        for page_index in range(
            start_page,
            end_page,
        ):
            image = self.renderer.render_page(
                page_index,
                options,
            )

            try:
                processor(
                    page_index,
                    image,
                )
            finally:
                image.close()
```

Đây là pattern rất mạnh.

---

# 12. Tại sao `finally` quan trọng?

Nếu:

```python
processor(...)
```

ném exception:

```python
raise RuntimeError(...)
```

thì nếu không có `finally`:

```python
image.close()
```

có thể không được gọi ở vị trí bạn mong muốn.

Với:

```python
try:
    processor(...)
finally:
    image.close()
```

ta đảm bảo:

```text
success
   ↓
close

error
   ↓
close
```

---

# 13. Đây là code tôi khuyên dùng

```python
class PdfRenderService:

    def __init__(self, renderer):
        self.renderer = renderer

    def process_pages(
        self,
        start_page: int,
        end_page: int,
        options,
        processor,
    ):
        for page_index in range(
            start_page,
            end_page,
        ):
            image = self.renderer.render_page(
                page_index,
                options,
            )

            try:
                processor(
                    page_index,
                    image,
                )
            finally:
                image.close()
```

---

# 14. Ví dụ save từng page

```python
from pathlib import Path


def save_page(
    page_index,
    image,
    output_dir,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"page-{page_index + 1:04d}.png"
    )

    image.save(output_path)
```

Sử dụng:

```python
service.process_pages(
    start_page=0,
    end_page=pdf.page_count,
    options=options,
    processor=lambda index, image:
        save_page(
            index,
            image,
            "output",
        ),
)
```

Memory lúc này gần như:

```text
page 1
  ↓
save
  ↓
release

page 2
  ↓
save
  ↓
release
```

thay vì:

```text
page 1 ─┐
page 2  │
page 3  │
...     ├── RAM
page 500┘
```

---

# 15. Nhưng `lambda` ở đây không đẹp

Để học architecture tốt, tôi khuyên viết:

```python
def save_page_processor(
    page_index,
    image,
):
    save_page(
        page_index,
        image,
        "output",
    )
```

rồi:

```python
service.process_pages(
    start_page=0,
    end_page=pdf.page_count,
    options=options,
    processor=save_page_processor,
)
```

Hoặc inject một object:

```python
class PageSaver:

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def __call__(
        self,
        page_index,
        image,
    ):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            self.output_dir
            / f"page-{page_index + 1:04d}.png"
        )

        image.save(path)
```

---

# 16. Architecture

Ta có:

```text
Application
     │
     ▼
PdfRenderService
     │
     ├── Renderer
     │
     └── Processor
             │
             ▼
        Save / Resize /
        Thumbnail / OCR
```

Flow:

```text
Page 1
  ↓
Renderer
  ↓
Image
  ↓
Processor
  ↓
save
  ↓
close

Page 2
  ↓
...
```

Đây là một kiến trúc rất phù hợp với hệ thống PDF lớn.

---

# 17. Streaming processing

Tên pattern ở đây có thể hiểu là:

```text
Streaming / Incremental Processing
```

Không phải:

```text
Load all
```

mà:

```text
Input
 ↓
one item
 ↓
process
 ↓
output
 ↓
next item
```

Giống:

```python
for line in file:
    process(line)
```

thay vì:

```python
lines = file.readlines()
```

PDF rendering cũng áp dụng cùng tư duy.

---

# 18. Render từng page

Một iterator đẹp hơn:

```python
class PdfPageRenderer:

    def __init__(
        self,
        renderer,
        options,
    ):
        self.renderer = renderer
        self.options = options

    def iter_images(
        self,
        start_page=0,
        end_page=None,
    ):
        if end_page is None:
            end_page = self.renderer.page_count

        for page_index in range(
            start_page,
            end_page,
        ):
            yield (
                page_index,
                self.renderer.render_page(
                    page_index,
                    self.options,
                ),
            )
```

Caller:

```python
for page_index, image in renderer.iter_images():
    try:
        process(page_index, image)
    finally:
        image.close()
```

---

# 19. `yield` và lifetime

Có một chi tiết rất đáng học.

Khi:

```python
yield (
    page_index,
    image,
)
```

generator tạm dừng.

Lúc đó:

```text
image
```

được giữ alive vì caller đang sử dụng nó.

Sau:

```python
image.close()
```

caller giải phóng image.

Sau đó generator tiếp tục:

```text
next()
```

và render page tiếp theo.

Đây là mô hình:

```text
Producer
   │
   │ yield
   ▼
Consumer
   │
   │ process
   │ close
   ▼
Producer
   │
   │ yield next
   ▼
```

---

# 20. Context manager tốt hơn nữa

Nếu muốn đảm bảo lifetime rõ ràng, ta có thể dùng context manager.

```python
from contextlib import contextmanager


@contextmanager
def rendered_page(
    renderer,
    page_index,
    options,
):
    image = renderer.render_page(
        page_index,
        options,
    )

    try:
        yield image
    finally:
        image.close()
```

Sử dụng:

```python
with rendered_page(
    renderer,
    page_index,
    options,
) as image:

    image.save(
        f"page-{page_index}.png"
    )
```

Đây là pattern rất đẹp:

```text
acquire
   ↓
use
   ↓
release
```

---

# 21. Context manager + iterator

Có thể kết hợp:

```python
def iter_pages(
    renderer,
    options,
    start_page=0,
    end_page=None,
):
    if end_page is None:
        end_page = renderer.page_count

    for page_index in range(
        start_page,
        end_page,
    ):
        with rendered_page(
            renderer,
            page_index,
            options,
        ) as image:
            yield page_index, image
```

Caller:

```python
for page_index, image in iter_pages(
    renderer,
    options,
):
    image.save(
        f"page-{page_index}.png"
    )
```

Khi generator tiếp tục sang page tiếp theo:

```text
page 1
 ↓
yield
 ↓
consumer save
 ↓
generator resumes
 ↓
context manager closes image
 ↓
page 2
```

Rất sạch.

---

# 22. Tuy nhiên có một lưu ý

Nếu caller giữ image:

```python
images.append(image)
```

sau khi `with` kết thúc:

```python
image.close()
```

thì caller đang giữ một object đã được close.

Do đó API cần quy định rõ:

> **Image chỉ hợp lệ trong lifetime của iteration/processing callback.**

Đây là vấn đề **ownership/lifetime contract**.

---

# 23. Tốt nhất cho batch processing: callback

Đối với production batch processing, tôi thích:

```python
service.process_pages(...)
```

hơn:

```python
for image in service.iter_images():
    ...
```

nếu mục tiêu chính là kiểm soát lifetime.

Ví dụ:

```python
class PdfRenderService:

    def process_pages(
        self,
        options,
        processor,
        start_page=0,
        end_page=None,
    ):
        if end_page is None:
            end_page = self.renderer.page_count

        for page_index in range(
            start_page,
            end_page,
        ):
            image = self.renderer.render_page(
                page_index,
                options,
            )

            try:
                processor(
                    page_index,
                    image,
                )
            finally:
                image.close()
```

Caller không cần nhớ:

```python
image.close()
```

---

# 24. Memory không chỉ nằm ở PIL

Khi tối ưu PDF renderer, phải quan tâm:

```text
1. PdfDocument
2. PdfPage
3. PdfBitmap
4. PIL.Image
5. temporary buffers
6. encoded PNG/JPEG data
7. application caches
```

Sai lầm phổ biến:

```python
self.cache[page_index] = image
```

Nếu cache 1000 ảnh:

```text
RAM ↑↑↑
```

---

# 25. Cache cũng phải có giới hạn

Nếu muốn cache:

```text
page image
```

không nên:

```python
cache = {}
```

và giữ mãi.

Thay vào đó:

```text
LRU cache
```

Ví dụ:

```text
maxsize = 5
```

thì:

```text
page 1
page 2
page 3
page 4
page 5
```

sau page 6:

```text
page 1 → evict
```

Đối với PDF viewer, đây là chiến lược rất hữu ích.

---

# 26. Đừng gọi `gc.collect()` sau mỗi page

Một người mới tối ưu memory thường viết:

```python
import gc

for page in pages:
    image = render(page)

    save(image)

    image.close()

    gc.collect()
```

Không nên làm vậy một cách mặc định.

`gc.collect()`:

```text
không phải magic memory cleanup
```

và gọi quá thường xuyên có thể làm chương trình chậm.

Python dùng:

```text
reference counting
+
cyclic garbage collector
```

CPython thường giải phóng object không còn reference ngay thông qua reference counting, còn cyclic GC xử lý reference cycles.

Trong pipeline của chúng ta:

```text
image
 ↓
save
 ↓
close
 ↓
reference biến mất
```

thường đã đủ.

---

# 27. Xóa reference có cần thiết không?

Ví dụ:

```python
for page in pages:
    image = render(page)
    save(image)
    image.close()
```

Ở iteration tiếp theo:

```python
image = render(page)
```

reference cũ bị thay thế.

Không cần:

```python
del image
```

trong hầu hết trường hợp.

`del` chỉ xóa reference của biến:

```text
không phải "free RAM ngay lập tức".
```

---

# 28. Memory profiling

Đừng tối ưu bằng cảm giác.

Ta có thể đo:

```python
import tracemalloc


tracemalloc.start()

# render workload

current, peak = tracemalloc.get_traced_memory()

print(
    "Current:",
    current,
)

print(
    "Peak:",
    peak,
)

tracemalloc.stop()
```

Nhưng có một lưu ý:

> `tracemalloc` chủ yếu theo dõi allocations của Python, không phản ánh đầy đủ native memory mà PDFium/PIL có thể sử dụng.

Do đó đối với PDF rendering production, cần phân biệt:

```text
Python memory
vs
native process memory
```

---

# 29. Test memory theo kiến trúc

Ta không nhất thiết phải test:

```text
RAM < 100 MB
```

vì phụ thuộc môi trường.

Thay vào đó test hành vi:

```text
Không giữ images trong collection
```

và:

```text
processor được gọi đúng số page
```

Ví dụ fake renderer:

```python
class FakeRenderer:

    page_count = 3

    def __init__(self):
        self.rendered = []

    def render_page(
        self,
        page_index,
        options,
    ):
        self.rendered.append(page_index)
        return FakeImage()
```

---

# 30. Fake Image

```python
class FakeImage:

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
```

Test:

```python
def test_process_pages_closes_images():

    renderer = FakeRenderer()

    service = PdfRenderService(renderer)

    received = []

    def processor(
        page_index,
        image,
    ):
        received.append(
            page_index
        )

    service.process_pages(
        options=None,
        processor=processor,
        start_page=0,
        end_page=3,
    )

    assert received == [0, 1, 2]
```

---

# 31. Test close khi processor lỗi

Đây là test rất quan trọng.

Ta tạo:

```python
class RecordingImage:

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
```

Processor:

```python
def processor(
    page_index,
    image,
):
    raise RuntimeError(
        "processing failed"
    )
```

Ta kỳ vọng:

```text
processor error
      ↓
finally
      ↓
image.close()
```

Đây là lý do production code phải có:

```python
try:
    ...
finally:
    image.close()
```

---

# 32. Batch processing có thể resume

Một lợi ích lớn khác.

Nếu PDF:

```text
500 pages
```

và page 437 lỗi:

```text
page 437
   ↓
exception
```

Nếu mỗi page được xử lý độc lập:

```text
page 1 → output
page 2 → output
...
page 436 → output
page 437 → failed
```

ta có thể:

```text
resume from 437
```

Đây rất phù hợp với crawler architecture mà chúng ta đã học:

```text
task
 ↓
worker
 ↓
process
 ↓
success/failure
```

---

# 33. Có thể tạo `PageProcessor` Protocol

Khi project lớn hơn:

```python
from typing import Protocol


class PageProcessor(Protocol):

    def __call__(
        self,
        page_index: int,
        image,
    ) -> None:
        ...
```

Sau đó:

```python
class PdfRenderService:

    def process_pages(
        self,
        options,
        processor: PageProcessor,
        start_page=0,
        end_page=None,
    ):
        ...
```

Đây rất hợp với kiến thức:

```text
Protocol
Dependency Injection
SOLID
```

mà bạn đã học trước đó.

---

# 34. Processor có thể là gì?

Cùng một renderer:

```text
PdfRenderer
     ↓
     ├── PNG Saver
     ├── JPEG Saver
     ├── Thumbnail Generator
     ├── OCR Processor
     ├── Image Compressor
     ├── Watermark Processor
     └── Preview Generator
```

Renderer không cần biết processor làm gì.

Đây là:

```text
Single Responsibility
+
Dependency Inversion
```

---

# 35. Architecture production-style

Sau Buổi 29, tôi muốn kiến trúc của chúng ta như sau:

```text
                    Application
                        │
                        ▼
                PdfRenderService
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
        PdfRenderer          PageProcessor
             │                     │
             ▼                     ▼
         pypdfium2          Save / OCR / etc.
             │
             ▼
          PdfBitmap
             │
             ▼
          PIL.Image
             │
             ▼
        process + release
```

Memory flow:

```text
Page N
  ↓
Bitmap
  ↓
PIL
  ↓
Processor
  ↓
release
  ↓
Page N+1
```

---

# 36. Nguyên tắc vàng

Đối với PDF lớn:

### Không:

```python
images = [
    render(page)
    for page in pages
]
```

### Nên:

```python
for page in pages:
    image = render(page)

    try:
        process(image)
    finally:
        image.close()
```

Hoặc tốt hơn:

```python
service.process_pages(
    processor=processor,
)
```

để service kiểm soát lifetime.

---

# 37. Liên hệ với Render Region

Buổi 28 và 29 kết hợp rất mạnh.

Giả sử page:

```text
2480 × 3508 px
```

nhưng ta chỉ cần:

```text
500 × 500 pt
```

Render region:

```text
region
 ↓
small bitmap
 ↓
process
 ↓
release
```

Memory được giảm ở **hai tầng**:

```text
Render Region
      ↓
giảm kích thước bitmap
      ↓
Streaming
      ↓
không giữ nhiều bitmap
```

Đây chính là cách xử lý PDF lớn hiệu quả.

---

# 38. Một pipeline hoàn chỉnh

```text
                    PDF
                     │
                     ▼
                PdfDocument
                     │
                     ▼
                   Page
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
           Region         Options
              │             │
              └──────┬──────┘
                     ▼
                 Renderer
                     │
                     ▼
                  Bitmap
                     │
                     ▼
                 PIL.Image
                     │
                     ▼
                 Processor
                     │
                     ▼
                  Output
                     │
                     ▼
                  RELEASE
                     │
                     ▼
                 Next Page
```

Đây là pipeline chúng ta sẽ sử dụng trong Mini Project.

---

# 39. Bài tập thực hành

Hãy xây class:

```python
class PdfBatchRenderer:
    ...
```

với API:

```python
batch.render(
    start_page=0,
    end_page=100,
    options=options,
    processor=processor,
)
```

Yêu cầu:

### 1.

Không trả về:

```python
list[PIL.Image]
```

### 2.

Chỉ render một page tại một thời điểm.

### 3.

Processor nhận:

```python
page_index
image
```

### 4.

Luôn close image:

```python
try:
    ...
finally:
    image.close()
```

### 5.

Nếu processor lỗi:

```text
page N
   ↓
error
   ↓
image vẫn phải được close
```

### 6.

Viết FakeRenderer để unit test.

---

# 40. Tổng kết Part III

Đến đây chúng ta đã hoàn thành gần toàn bộ kiến thức rendering quan trọng:

```text
21  Render chất lượng cao       ✅
22  Grayscale                   ✅
23  Transparency                ✅
24  Rotation                    ✅
25  CropBox / MediaBox          ✅
26  Page Size                   ✅
27  Coordinate System           ✅
28  Render Region               ✅
29  Memory Optimization         ✅
30  Thumbnail Generator         ⬜
```

Điểm quan trọng nhất của Buổi 29:

```text
PDF lớn
  ↓
KHÔNG render tất cả vào RAM
  ↓
render từng page
  ↓
process
  ↓
save
  ↓
release
  ↓
page tiếp theo
```

Và architecture:

```text
PdfRenderer
    ↓
PdfRenderService
    ↓
PageProcessor
```

cho phép renderer **không cần biết** output cuối cùng là PNG, JPEG, thumbnail hay OCR.

---

# Buổi 30 — Mini Project: PDF Thumbnail Generator

Đây sẽ là bài **kết thúc Part III** và chúng ta sẽ ghép toàn bộ:

```text
PdfDocument
PdfPage
MediaBox / CropBox
PageSize
DPI
Rotation
Coordinate System
Render Region
Memory Streaming
PIL
```

để xây một chương trình hoàn chỉnh:

```bash
pdf-thumbnail book.pdf --output thumbnails/
```

có thể xử lý:

```text
PDF
 ↓
mỗi page
 ↓
render ở DPI thấp
 ↓
resize thumbnail
 ↓
save
 ↓
release
```

và quan trọng hơn, thiết kế theo architecture:

```text
CLI
 ↓
Application Service
 ↓
PdfRenderer Port
 ↓
pypdfium2
 ↓
PIL
```

để sau Buổi 30 chúng ta có một **mini project hoàn chỉnh**, thay vì chỉ học API rời rạc.
