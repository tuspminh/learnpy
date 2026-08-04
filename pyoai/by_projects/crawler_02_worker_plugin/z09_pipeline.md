# Buổi 9 — Thiết kế Crawl Pipeline

> Đây là buổi quan trọng nhất từ đầu roadmap đến giờ.

Nếu **CrawlContext** là "bộ não", **Plugin** là "người biết website", thì **Pipeline** chính là "dây chuyền sản xuất".

Đây là kiến trúc mà hầu hết crawler framework chuyên nghiệp (Scrapy, Haystack, Airflow theo một góc nhìn, ETL Framework...) đều áp dụng.

---

# Mục tiêu

Sau buổi này chúng ta sẽ có một luồng chuẩn:

```text
URL
 │
 ▼
Request
 │
 ▼
HTTP Client
 │
 ▼
Response
 │
 ▼
Parser
 │
 ▼
Model
 │
 ▼
Pipeline
 │
 ▼
Repository
```

Plugin chỉ còn nhiệm vụ:

```python
response = context.http.get(url)

book = context.parsers.book.parse(response)

context.pipeline.process(book)
```

Không còn:

* save SQLite
* download ảnh
* emit event
* log
* validate

---

# Pipeline là gì?

Pipeline là chuỗi các bước xử lý dữ liệu.

Ví dụ:

```text
Book

↓

Validate

↓

Normalize

↓

Save Database

↓

Download Cover

↓

Emit Event

↓

Done
```

Mỗi bước chỉ làm đúng một việc.

---

# Kiến trúc

```
crawler/

pipeline/

    __init__.py

    base.py

    manager.py

    context.py

    exceptions.py

    stages/

        validate.py

        normalize.py

        save.py

        cover.py

        event.py
```

---

# Luồng Pipeline

```
Book

↓

ValidateStage

↓

NormalizeStage

↓

RepositoryStage

↓

DownloadImageStage

↓

EventStage
```

---

# 1. BasePipelineStage

```python
from abc import ABC
from abc import abstractmethod

class PipelineStage(ABC):

    @abstractmethod
    def process(

        self,

        item,

        context

    ):

        ...
```

Tất cả Stage đều kế thừa lớp này.

---

# 2. Pipeline Manager

```python
class Pipeline:

    def __init__(self):

        self.stages = []
```

Đăng ký

```python
pipeline.add_stage(
    ValidateStage()
)
```

Chạy

```python
pipeline.process(book)
```

---

# 3. Validate Stage

```python
class ValidateStage(

    PipelineStage

):

    def process(

        self,

        item,

        context

    ):

        validate(item)

        return item
```

Nếu sai

↓

```text
Pipeline dừng
```

---

# 4. Normalize Stage

Ví dụ

```text
" Đấu Phá Thương Khung "

↓

"Đấu Phá Thương Khung"
```

Code

```python
item.title = item.title.strip()
```

Có thể:

* normalize unicode
* chuẩn hóa xuống dòng
* bỏ HTML thừa

---

# 5. Save Stage

```python
class SaveStage(

    PipelineStage

):

    def process(

        self,

        item,

        context

    ):

        context.repository.save(
            item
        )

        return item
```

Parser không được save.

Plugin không được save.

Pipeline save.

---

# 6. Download Cover Stage

```text
Book

↓

cover_url

↓

download

↓

local_path

↓

Book.cover_path
```

---

Code

```python
image = context.http.download(
    item.cover
)

item.cover_path = image.path
```

---

# 7. Event Stage

Sau khi lưu

↓

```text
BookSaved
```

```python
context.events.emit(

    BookSaved(item)
)
```

Worker có thể:

* update progress
* ghi log
* gửi websocket

Plugin không cần biết.

---

# 8. Pipeline Context

Không dùng trực tiếp CrawlContext.

Ta tạo PipelineContext.

```python
@dataclass

class PipelineContext:

    repository

    logger

    http

    events
```

Pipeline không cần parser.

---

# 9. Pipeline Manager

```python
pipeline = Pipeline()

pipeline.add_stage(

    ValidateStage()

)

pipeline.add_stage(

    NormalizeStage()

)

pipeline.add_stage(

    SaveStage()

)

pipeline.add_stage(

    EventStage()
)
```

Chạy

```python
pipeline.process(book)
```

Flow

```text
Book

↓

Validate

↓

Normalize

↓

Save

↓

Event

↓

Done
```

---

# 10. Stop Pipeline

Một Stage có thể dừng.

Ví dụ

```python
if item.deleted:

    return None
```

Pipeline

↓

không chạy tiếp.

---

# 11. Error Handling

```python
try:

    stage.process()

except Exception:

    ...
```

Có thể:

```text
Skip

Retry

Stop

Continue
```

Đây sẽ được mở rộng ở buổi Worker.

---

# 12. CLI Test

Đây là điểm mạnh của framework.

---

## Chạy Pipeline

```bash
crawler dev pipeline run book.json
```

↓

```text
Validate

OK

Normalize

OK

Save

OK

Event

OK
```

---

## Danh sách Stage

```bash
crawler dev pipeline list
```

↓

```text
Validate

Normalize

Save

Cover

Event
```

---

## Chạy một Stage

```bash
crawler dev pipeline stage validate book.json
```

↓

```text
Validation OK
```

---

## Benchmark

```bash
crawler dev pipeline benchmark
```

↓

```text
Validate

2 ms

Normalize

1 ms

Save

18 ms

Total

21 ms
```

---

# 13. Unit Test

```python
def test_validate():

    stage = ValidateStage()

    stage.process(book, context)
```

---

```python
def test_pipeline():

    pipeline = Pipeline()

    pipeline.add_stage(
        ValidateStage()
    )

    pipeline.process(book)
```

---

# 14. Kiến trúc sau Buổi 9

```
pipeline/

    base.py

    manager.py

    context.py

    exceptions.py

    stages/

        validate.py

        normalize.py

        save.py

        cover.py

        event.py
```

---

# Luồng hoàn chỉnh

```text
Plugin

↓

RequestClient

↓

Parser

↓

Book

↓

Pipeline

↓

Repository

↓

SQLite
```

Đây là lần đầu tiên dữ liệu được ghi xuống database.

---

# Bài tập

Xây dựng:

* `PipelineStage`
* `Pipeline`
* `PipelineContext`

Viết các Stage:

* `ValidateStage`
* `NormalizeStage`
* `SaveStage`
* `DownloadCoverStage`
* `EventStage`

Viết CLI:

```bash
crawler dev pipeline list

crawler dev pipeline run FILE

crawler dev pipeline stage validate FILE

crawler dev pipeline benchmark
```

Viết unit test cho:

* `Pipeline`
* từng `Stage`
* luồng đầy đủ từ `Book` → `Repository`

---

# Cải tiến kiến trúc (khuyến nghị)

Đây là điểm tôi khuyên nên làm ngay từ đầu để framework đủ linh hoạt cho các nguồn truyện khác nhau.

## Thay vì Pipeline chỉ xử lý `Book`

Hãy thiết kế Pipeline xử lý **Item** tổng quát:

```text
Item
 ├── Book
 ├── Chapter
 ├── Image
 ├── Author
 ├── Category
 └── Tag
```

Khi đó mỗi Stage có thể khai báo mình hỗ trợ kiểu dữ liệu nào:

```python
class SaveStage(PipelineStage):
    supported_types = (Book, Chapter, Image)
```

Pipeline Manager sẽ tự bỏ qua các Stage không phù hợp.

Ví dụ:

```text
Book
 ├─ Validate
 ├─ Normalize
 ├─ Save
 └─ DownloadCover

Chapter
 ├─ Validate
 ├─ Normalize
 └─ Save

Image
 ├─ Download
 ├─ Optimize
 └─ Save
```

Thiết kế này giúp bạn **không phải tạo nhiều pipeline khác nhau** (`BookPipeline`, `ChapterPipeline`, `ImagePipeline`) mà chỉ cần **một Pipeline duy nhất**, rất dễ mở rộng khi sau này bổ sung thêm `Comment`, `Review`, `Volume` hoặc các loại dữ liệu mới. Đây cũng là hướng thiết kế được nhiều framework ETL và crawler hiện đại áp dụng.
