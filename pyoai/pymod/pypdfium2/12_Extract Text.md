# Buổi 12 — Extract Text

**Phần II — Đọc và phân tích PDF**

Hôm trước chúng ta đã học:

```text
PdfPage
   │
   ▼
get_textpage()
   │
   ▼
PdfTextPage
```

Hôm nay đi thêm một bước:

```text
PdfTextPage
   │
   ▼
extract text
   │
   ▼
clean / normalize
   │
   ▼
str
```

Mục tiêu của Buổi 12 là xây được một **Text Extractor có thể đọc một trang hoặc toàn bộ PDF**, đồng thời hiểu những vấn đề thực tế khi text lấy từ PDF không sạch như text trong `.txt`.

---

## 1. Lấy text cơ bản

Code tối thiểu:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]

    textpage = page.get_textpage()

    text = textpage.get_text_bounded()

    print(text)

finally:
    pdf.close()
```

Pipeline:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
PdfTextPage
 ↓
get_text_bounded()
 ↓
str
```

`get_text_bounded()` là API pypdfium2 dùng để lấy text trong một vùng của trang; khi không giới hạn vùng, ta dùng nó để lấy toàn bộ text của trang.

---

# 2. Tại sao Extract Text không đơn giản?

Nếu file `.txt` chứa:

```text
Xin chào.
Đây là một câu.
Đây là câu tiếp theo.
```

thì:

```python
text = file.read()
```

thường khá dễ hiểu.

Nhưng PDF có cấu trúc kiểu:

```text
PDF Page
│
├── Text object
├── Text object
├── Image
├── Text object
├── Graphic
└── Text object
```

PDF không nhất thiết lưu text theo đúng thứ tự mà mắt chúng ta nhìn thấy.

Ví dụ trên trang:

```text
┌──────────────────────────────┐
│       CHƯƠNG 1               │
│                              │
│ Cột trái          Cột phải   │
│ dòng 1            dòng 1     │
│ dòng 2            dòng 2     │
│ dòng 3            dòng 3     │
└──────────────────────────────┘
```

Text extraction có thể cần xử lý thứ tự.

Đó là lý do Buổi 12 chỉ tập trung vào **extract**, còn:

```text
position
bounding box
character
font
```

sẽ được tách thành các buổi sau.

---

# 3. `print()` và `repr()`

Khi debug PDF extraction, đây là kỹ thuật rất quan trọng.

```python
print(text)
```

cho:

```text
CHƯƠNG 1

Đây là nội dung.
```

Nhưng:

```python
print(repr(text))
```

có thể cho:

```text
'CHƯƠNG 1\n\nĐây là nội dung.\n'
```

Nhờ đó chúng ta nhìn thấy:

```text
\n
\t
\r
```

Ví dụ:

```python
text = textpage.get_text_bounded()

print("NORMAL:")
print(text)

print()
print("RAW:")
print(repr(text))
```

---

# 4. `strip()`

Một thao tác đơn giản:

```python
text = text.strip()
```

Ví dụ:

```text
'\n\nCHƯƠNG 1\n\n'
```

trở thành:

```text
'CHƯƠNG 1'
```

`strip()` loại whitespace ở **đầu và cuối**, không xử lý toàn bộ nội dung bên trong.

Ví dụ:

```python
text = """
CHƯƠNG 1

Đây là nội dung.
"""

text = text.strip()

print(repr(text))
```

Kết quả:

```text
'CHƯƠNG 1\n\nĐây là nội dung.'
```

---

# 5. Không nên `replace("\n", " ")` ngay

Giả sử:

```text
CHƯƠNG 1
Đây là đoạn văn.
Đây là câu tiếp theo.
```

Nếu làm:

```python
text = text.replace("\n", " ")
```

ta được:

```text
CHƯƠNG 1 Đây là đoạn văn. Đây là câu tiếp theo.
```

Có thể đúng trong một số trường hợp.

Nhưng:

```text
Mục 1
- Apple
- Banana
- Orange
```

sẽ thành:

```text
Mục 1 - Apple - Banana - Orange
```

Thông tin cấu trúc đã mất.

Vì vậy:

> **Raw extraction và text cleaning nên là hai bước khác nhau.**

---

# 6. Thiết kế `PdfTextReader`

Ta bắt đầu tạo abstraction:

```text
infrastructure/
└── pdfium/
    ├── document.py
    ├── renderer.py
    ├── exporter.py
    └── text_reader.py
```

`text_reader.py`:

```python
from typing import Any


class PdfTextReader:

    def read_page(
        self,
        page: Any,
    ) -> str:

        textpage = page.get_textpage()

        return textpage.get_text_bounded()
```

Đây là raw reader.

Nó không làm:

```text
strip
replace
normalize
remove duplicate
```

Nó chỉ có nhiệm vụ:

> PDF Page → raw text.

---

# 7. Đọc toàn bộ PDF

Bây giờ tạo:

```python
class PdfTextExtractor:

    def __init__(
        self,
        text_reader: PdfTextReader,
    ) -> None:

        self.text_reader = text_reader

    def extract(
        self,
        pdf,
    ) -> str:

        pages: list[str] = []

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            text = self.text_reader.read_page(
                page
            )

            pages.append(text)

        return "\n".join(pages)
```

Có một vấn đề nhỏ:

```python
pages = []
```

Ở PDF vài nghìn trang, toàn bộ text có thể rất lớn.

Nhưng so với việc giữ toàn bộ `PIL.Image`, text thường nhẹ hơn rất nhiều.

Dù vậy, với production system, chúng ta sẽ thiết kế API streaming ở phần sau.

---

# 8. Phiên bản hoàn chỉnh

File:

```text
pdf_converter/infrastructure/pdfium/text_reader.py
```

```python
from pathlib import Path
from typing import Any

import pypdfium2 as pdfium


class PdfTextReader:

    def read_page(
        self,
        page: Any,
    ) -> str:

        textpage = page.get_textpage()

        return textpage.get_text_bounded()


class PdfTextExtractor:

    def __init__(
        self,
        text_reader: PdfTextReader | None = None,
    ) -> None:

        self.text_reader = (
            text_reader
            if text_reader is not None
            else PdfTextReader()
        )

    def extract_page(
        self,
        page,
    ) -> str:

        return self.text_reader.read_page(page)

    def extract_pdf(
        self,
        pdf,
    ) -> str:

        pages: list[str] = []

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            text = self.extract_page(page)

            pages.append(text)

        return "\n".join(pages)

    def extract_file(
        self,
        pdf_path: str | Path,
    ) -> str:

        pdf = pdfium.PdfDocument(pdf_path)

        try:

            return self.extract_pdf(pdf)

        finally:

            pdf.close()
```

---

# 9. Sử dụng

```python
from pdf_converter.infrastructure.pdfium.text_reader import (
    PdfTextExtractor,
)


extractor = PdfTextExtractor()

text = extractor.extract_file(
    "sample.pdf"
)

print(text)
```

Pipeline:

```text
extract_file()
     │
     ▼
PdfDocument
     │
     ▼
extract_pdf()
     │
     ├── page 1
     │     ↓
     │   extract_page()
     │     ↓
     │   PdfTextReader
     │
     ├── page 2
     │
     ├── page 3
     │
     └── page N
```

---

# 10. Nhưng chúng ta đang có một vấn đề

Trong code:

```python
pages: list[str] = []
```

sau đó:

```python
return "\n".join(pages)
```

Nếu PDF có:

```text
1000 pages
```

ta giữ:

```text
page 1 text
page 2 text
page 3 text
...
page 1000 text
```

trong RAM.

Một thiết kế tốt hơn là cung cấp **iterator**.

---

# 11. Extract từng trang bằng Generator

Ta viết:

```python
from collections.abc import Iterator


class PdfTextExtractor:

    def iter_pages(
        self,
        pdf,
    ) -> Iterator[tuple[int, str]]:

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            text = self.text_reader.read_page(
                page
            )

            yield page_index, text
```

Sử dụng:

```python
for page_index, text in extractor.iter_pages(pdf):

    print(
        f"PAGE {page_index + 1}"
    )

    print(text)
```

Pipeline:

```text
PDF
 │
 ▼
page 1 → yield
 │
 ▼
page 2 → yield
 │
 ▼
page 3 → yield
 │
 ▼
...
```

Không cần tạo:

```python
all_pages = [...]
```

---

# 12. Tại sao Generator rất phù hợp?

Đây chính là kiến thức Python Advanced mà bạn đã học.

Nếu dùng:

```python
def extract_all():
    return [
        text1,
        text2,
        text3,
        ...
    ]
```

thì toàn bộ dữ liệu được tạo trước.

Generator:

```python
def iter_pages():
    yield text1
    yield text2
    yield text3
```

cho phép:

```text
request
 ↓
process
 ↓
save
 ↓
request next
```

Rất phù hợp với PDF lớn.

---

# 13. API tốt hơn

Tôi khuyến nghị `PdfTextExtractor` cuối cùng có hai API:

```python
extract_page()
```

và:

```python
iter_pages()
```

Ví dụ:

```python
class PdfTextExtractor:

    def extract_page(
        self,
        page,
    ) -> str:
        ...

    def iter_pages(
        self,
        pdf,
    ):
        ...
```

Sau này có thể thêm:

```python
extract_pdf()
```

nếu caller thực sự muốn toàn bộ text.

---

# 14. Thêm `page_number`

Thay vì:

```python
yield page_index, text
```

ta có thể tạo model:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:

    page_index: int
    page_number: int
    text: str
```

Sau đó:

```python
yield PageText(
    page_index=page_index,
    page_number=page_index + 1,
    text=text,
)
```

Tại sao có cả hai?

```text
page_index
    ↓
0-based
```

và:

```text
page_number
    ↓
1-based
```

Application code thường dùng index.

UI thường hiển thị page number.

---

# 15. Model hoàn chỉnh

File:

```text
pdf_converter/domain/models.py
```

thêm:

```python
from dataclasses import dataclass
from enum import Enum


class ImageFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"


@dataclass(frozen=True)
class ConvertOptions:

    dpi: float = 150.0
    image_format: ImageFormat = ImageFormat.PNG
    quality: int = 90
    start_page: int = 0
    end_page: int | None = None

    def __post_init__(self):

        if self.dpi <= 0:
            raise ValueError(
                "DPI phải > 0"
            )

        if not 1 <= self.quality <= 100:
            raise ValueError(
                "quality phải nằm trong 1..100"
            )

        if self.start_page < 0:
            raise ValueError(
                "start_page phải >= 0"
            )

        if self.end_page is not None:
            if self.end_page <= self.start_page:
                raise ValueError(
                    "end_page phải > start_page"
                )

    @property
    def scale(self) -> float:

        return self.dpi / 72.0


@dataclass(frozen=True)
class PageText:

    page_index: int
    page_number: int
    text: str
```

---

# 16. `PdfTextExtractor` sử dụng `PageText`

```python
from collections.abc import Iterator
from typing import Any


class PdfTextExtractor:

    def __init__(
        self,
        text_reader: PdfTextReader | None = None,
    ) -> None:

        self.text_reader = (
            text_reader
            if text_reader is not None
            else PdfTextReader()
        )

    def extract_page(
        self,
        page: Any,
    ) -> str:

        return self.text_reader.read_page(
            page
        )

    def iter_pages(
        self,
        pdf: Any,
    ) -> Iterator[PageText]:

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            text = self.extract_page(page)

            yield PageText(
                page_index=page_index,
                page_number=page_index + 1,
                text=text,
            )
```

---

# 17. Sử dụng Generator

```python
import pypdfium2 as pdfium

from pdf_converter.infrastructure.pdfium.text_reader import (
    PdfTextExtractor,
)


pdf = pdfium.PdfDocument(
    "sample.pdf"
)

try:

    extractor = PdfTextExtractor()

    for page_text in extractor.iter_pages(pdf):

        print(
            f"===== PAGE "
            f"{page_text.page_number} ====="
        )

        print(
            page_text.text
        )

finally:

    pdf.close()
```

---

# 18. Chỉ lấy những trang có text

Ví dụ:

```python
for page_text in extractor.iter_pages(pdf):

    if not page_text.text.strip():
        continue

    print(
        f"Page {page_text.page_number}"
    )

    print(page_text.text)
```

Đây là một cách rất đơn giản để phát hiện:

```text
page có text
```

hoặc:

```text
page có khả năng là scan/image-only
```

Nhưng nhớ:

> Đây chỉ là heuristic.

Một trang có thể có text layer nhưng extraction rất ít hoặc text không hữu ích.

---

# 19. Text cleaning

Đừng trộn:

```text
Extract
```

với:

```text
Clean
```

Ta có pipeline:

```text
PDF
 ↓
PdfTextPage
 ↓
Raw Text
 ↓
Text Cleaner
 ↓
Normalized Text
```

Ví dụ:

```python
class TextCleaner:

    def clean(
        self,
        text: str,
    ) -> str:

        return text.strip()
```

Sau đó:

```python
raw_text = extractor.extract_page(page)

clean_text = cleaner.clean(
    raw_text
)
```

Đây là Separation of Concerns.

---

# 20. Cleaner nâng cao hơn

Có thể làm:

```python
class TextCleaner:

    def clean(
        self,
        text: str,
    ) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)
```

Ví dụ:

```text
Input:

CHƯƠNG 1


Đây là nội dung.


Tác giả: ABC
```

Output:

```text
CHƯƠNG 1
Đây là nội dung.
Tác giả: ABC
```

Nhưng lưu ý:

**Không phải PDF nào cũng nên áp dụng cách này.**

Nếu tài liệu có:

```text
paragraph
list
table
```

thì việc loại toàn bộ blank line có thể làm mất cấu trúc.

---

# 21. Đặc biệt với truyện chữ

Project của bạn là hệ thống crawl/đọc truyện, nên sau này có thể muốn:

```text
PDF
 ↓
Extract
 ↓
Clean
 ↓
Detect chapter
 ↓
Chapter
 ↓
Content
 ↓
SQLite
```

Ví dụ:

```text
CHƯƠNG 1
...
CHƯƠNG 2
...
CHƯƠNG 3
...
```

sau đó parser có thể tách:

```text
Chapter(
    number=1,
    title="...",
    content="..."
)
```

Nhưng **chưa làm việc này ở Buổi 12**.

Buổi 12 chỉ xây nền:

```text
PDF → Text
```

---

# 22. Xử lý toàn bộ PDF theo streaming

Một application service tốt:

```python
from collections.abc import Iterator
from pathlib import Path

import pypdfium2 as pdfium


class PdfTextService:

    def iter_file(
        self,
        pdf_path: str | Path,
    ) -> Iterator[PageText]:

        pdf = pdfium.PdfDocument(pdf_path)

        try:

            extractor = PdfTextExtractor()

            yield from extractor.iter_pages(
                pdf
            )

        finally:

            pdf.close()
```

Sử dụng:

```python
service = PdfTextService()

for page_text in service.iter_file(
    "sample.pdf"
):

    print(
        page_text.page_number
    )
```

Đây là API rất đẹp cho:

```text
CLI
GUI
OCR
Search indexing
SQLite
Elasticsearch
RAG
```

---

# 23. Một lỗi resource management cần tránh

Không nên:

```python
def iter_file(path):

    pdf = pdfium.PdfDocument(path)

    for page in pdf:

        yield ...
```

mà không có:

```python
finally:
    pdf.close()
```

Vì generator có lifecycle riêng.

Đúng:

```python
try:
    yield ...
finally:
    pdf.close()
```

Đây là lý do chúng ta cần đặc biệt cẩn thận khi kết hợp:

```text
Generator
+
External resource
```

---

# 24. Test `TextCleaner`

Ví dụ:

```python
def test_clean():

    cleaner = TextCleaner()

    text = """
    CHƯƠNG 1


    Nội dung
    """

    result = cleaner.clean(text)

    assert result == (
        "CHƯƠNG 1\n"
        "Nội dung"
    )
```

Điểm hay:

Test cleaner **không cần PDF**.

Đúng tinh thần:

```text
Pure logic
    ↓
unit test

PDFium
    ↓
integration test
```

---

# 25. Test `PdfTextExtractor` bằng Fake

Ta có:

```python
class FakeTextReader:

    def read_page(self, page):

        return f"text-{page}"
```

Sau đó:

```python
def test_extract_page():

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        text_reader=reader
    )

    result = extractor.extract_page(
        "page-1"
    )

    assert result == "text-page-1"
```

Không cần cài PDFium trong test logic này.

Đây chính là lợi ích của Dependency Injection.

---

# 26. Kiến trúc hiện tại

Sau Buổi 12:

```text
pdf_converter/
│
├── domain/
│   └── models.py
│       ├── ConvertOptions
│       └── PageText
│
├── application/
│
└── infrastructure/
    └── pdfium/
        ├── document.py
        ├── renderer.py
        ├── exporter.py
        └── text_reader.py
```

Và pipeline:

```text
                     PdfPage
                    /       \
                   /         \
                  ▼           ▼
             PdfRenderer   TextReader
                  │           │
                  ▼           ▼
             PdfBitmap    PdfTextPage
                  │           │
                  ▼           ▼
              PIL.Image      str
```

---

# 27. Render và Extract có thể chạy song song về mặt kiến trúc

Một page:

```text
                 PdfPage
                /       \
               /         \
              ▼           ▼
          Renderer      Extractor
              │             │
              ▼             ▼
           Image           Text
```

Điều này rất quan trọng.

Ví dụ sau này muốn xây:

```text
PDF Reader
```

thì một page có thể:

```text
PdfPage
 ├── render thumbnail
 ├── extract text
 ├── extract links
 ├── inspect images
 └── inspect objects
```

Đó chính là lý do `PdfPage` là abstraction trung tâm.

---

# 28. Bài tập Buổi 12

### Bài 1 — Basic

Viết:

```python
extract_page_text(
    pdf_path,
    page_index,
)
```

trả về:

```python
str
```

---

### Bài 2 — Toàn bộ PDF

Viết:

```python
extract_pdf_text(
    pdf_path
)
```

trả về:

```text
page 1 text
page 2 text
...
```

---

### Bài 3 — Generator ⭐

Viết:

```python
iter_pdf_pages(
    pdf_path
)
```

trả:

```python
PageText
```

theo từng page.

Không được:

```python
pages = []
```

---

### Bài 4 — Debug

Với mỗi trang in:

```text
Page: 1
Characters: 1534
Has text: True
```

Gợi ý:

```python
length = len(page_text.text)

has_text = bool(
    page_text.text.strip()
)
```

---

### Bài 5 — Scan detection

In:

```text
Page 1: TEXT
Page 2: TEXT
Page 3: POSSIBLE SCAN
Page 4: TEXT
```

dựa trên:

```python
if not text.strip():
    ...
```

---

# 29. Bài tập quan trọng nhất

Hãy xây pipeline:

```text
sample.pdf
     │
     ▼
PdfTextExtractor
     │
     ▼
PageText
     │
     ▼
TextCleaner
     │
     ▼
output.txt
```

Ví dụ output:

```text
===== PAGE 1 =====

CHƯƠNG 1

Nội dung chương...

===== PAGE 2 =====

Nội dung tiếp theo...

===== PAGE 3 =====

...
```

Đây chính là phiên bản đầu tiên của:

**PDF → Text Converter**

và sẽ là nền móng cho Mini Project ở **Buổi 20**.

---

# 30. Tổng kết

Hôm nay chúng ta đi từ:

```python
textpage = page.get_textpage()
```

đến một kiến trúc thực tế:

```text
PdfDocument
      ↓
PdfPage
      ↓
PdfTextPage
      ↓
PdfTextReader
      ↓
PdfTextExtractor
      ↓
PageText
      ↓
TextCleaner
      ↓
Application
```

5 điểm cần nhớ:

```text
1. PdfTextPage ≠ str
2. get_textpage() tạo text layer accessor
3. get_text_bounded() lấy text
4. Extract ≠ Clean
5. PDF lớn nên ưu tiên iter_pages() / generator
```

**Buổi 13 — Text Position / Bounding Box** sẽ rất thú vị: chúng ta không chỉ lấy được `"Hello World"`, mà còn biết **text nằm ở tọa độ nào trên trang**, từ đó có thể xác định dòng, vùng, header/footer, column và tiến tới xây PDF parser thực sự.
