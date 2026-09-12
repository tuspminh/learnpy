# Buổi 20 — Mini Project: PDF Text Extractor

Hôm nay chúng ta **tổng hợp toàn bộ Phần II — Đọc và phân tích PDF** thành một project hoàn chỉnh.

Từ đầu phần này, chúng ta đã đi:

```text
11. TextPage
12. Extract text
13. Text position / BoundingBox
14. Character-level extraction
15. Link / Annotation
16. Page Objects
17. Images
18. Font / Text Information
19. Crop / Clipping
20. ★ Mini Project — PDF Text Extractor
```

Mục tiêu hôm nay không phải viết một script:

```python
print(text)
```

mà xây một chương trình có kiến trúc rõ ràng:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ▼
TextPage
 │
 ▼
Characters
 │
 ├── BoundingBox
 └── FontInfo
 │
 ▼
Lines
 │
 ▼
PageText
 │
 ▼
Text Extractor
 │
 ├── .txt
 └── structured output
```

Nếu bạn có một PDF truyện/tài liệu riêng, bạn có thể gửi lên để sau này chúng ta dùng chính file đó kiểm thử extractor; một PDF text-based sẽ giúp thấy rõ kết quả hơn.

---

# 1. Yêu cầu của project

Chúng ta xây CLI:

```bash
python -m pdf_text_extractor input.pdf
```

hoặc:

```bash
python -m pdf_text_extractor input.pdf output.txt
```

Có thể chỉ định:

```bash
python -m pdf_text_extractor input.pdf output.txt --start-page 1 --end-page 10
```

và crop:

```bash
python -m pdf_text_extractor input.pdf output.txt \
    --left 50 \
    --bottom 100 \
    --right 550 \
    --top 750
```

Kiến trúc:

```text
Presentation
     │
     ▼
Application
     │
     ▼
Domain
     │
     ▲
Infrastructure
     │
     ▼
pypdfium2
```

---

# 2. Thiết kế project

Tạo:

```text
pdf_text_extractor/
│
├── __init__.py
├── __main__.py
│
├── domain/
│   ├── __init__.py
│   ├── geometry.py
│   ├── font.py
│   └── text.py
│
├── application/
│   ├── __init__.py
│   ├── ports.py
│   └── extractor.py
│
├── infrastructure/
│   ├── __init__.py
│   └── pdfium/
│       ├── __init__.py
│       ├── document.py
│       └── text_reader.py
│
└── presentation/
    ├── __init__.py
    └── cli.py
```

Và:

```text
tests/
├── test_geometry.py
├── test_text.py
└── test_extractor.py
```

---

# 3. Domain — BoundingBox

## `domain/geometry.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self):
        if self.right < self.left:
            raise ValueError(
                "right phải >= left"
            )

        if self.top < self.bottom:
            raise ValueError(
                "top phải >= bottom"
            )

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.left + self.right) / 2,
            (self.bottom + self.top) / 2,
        )

    def contains_point(
        self,
        x: float,
        y: float,
    ) -> bool:

        return (
            self.left <= x <= self.right
            and
            self.bottom <= y <= self.top
        )

    def contains_box(
        self,
        other: "BoundingBox",
    ) -> bool:

        return (
            self.left <= other.left
            and
            self.bottom <= other.bottom
            and
            self.right >= other.right
            and
            self.top >= other.top
        )

    def intersects(
        self,
        other: "BoundingBox",
    ) -> bool:

        return not (
            self.right < other.left
            or self.left > other.right
            or self.top < other.bottom
            or self.bottom > other.top
        )

    def intersection(
        self,
        other: "BoundingBox",
    ) -> "BoundingBox | None":

        left = max(
            self.left,
            other.left,
        )

        bottom = max(
            self.bottom,
            other.bottom,
        )

        right = min(
            self.right,
            other.right,
        )

        top = min(
            self.top,
            other.top,
        )

        if right < left or top < bottom:
            return None

        return BoundingBox(
            left=left,
            bottom=bottom,
            right=right,
            top=top,
        )
```

---

# 4. Domain — FontInfo

## `domain/font.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FontInfo:
    size: float | None = None
    family: str | None = None
    weight: str | None = None
    italic: bool = False
```

Hiện tại chúng ta chỉ bắt buộc:

```text
size
```

Các field khác để mở rộng về sau.

---

# 5. Domain — Character

## `domain/text.py`

```python
from dataclasses import dataclass

from .font import FontInfo
from .geometry import BoundingBox


@dataclass(frozen=True)
class PdfCharacter:
    index: int
    char: str
    bbox: BoundingBox
    font: FontInfo


@dataclass(frozen=True)
class PdfWord:
    text: str
    bbox: BoundingBox
    font: FontInfo


@dataclass(frozen=True)
class PdfLine:
    text: str
    bbox: BoundingBox
    font: FontInfo


@dataclass(frozen=True)
class PageText:
    page_index: int
    page_number: int
    text: str
```

Ta có hierarchy:

```text
PdfCharacter
      ↓
PdfWord
      ↓
PdfLine
      ↓
PageText
```

---

# 6. Tại sao `PageText` vẫn tồn tại?

Bạn có thể thắc mắc:

> Nếu đã có Character/Word/Line, tại sao cần PageText?

Vì application có nhiều nhu cầu khác nhau.

Một client chỉ cần:

```python
page_text.text
```

thì không cần quan tâm:

```text
character
font
bbox
```

Ví dụ export `.txt`:

```text
PageText
    ↓
text
    ↓
file.txt
```

Trong khi layout analysis có thể dùng:

```text
PdfCharacter
    ↓
PdfWord
    ↓
PdfLine
```

Hai use case cùng tồn tại.

---

# 7. Application Port

## `application/ports.py`

```python
from typing import Protocol

from domain.text import PageText


class TextPageReader(Protocol):

    def read_page(
        self,
        page,
        page_index: int,
    ) -> PageText:
        ...
```

Đây là Dependency Inversion.

Application biết:

```text
TextPageReader
```

nhưng không biết:

```text
pypdfium2
PDFium
```

---

# 8. Infrastructure — PdfDocument

## `infrastructure/pdfium/document.py`

```python
from pathlib import Path

import pypdfium2 as pdfium


class PdfiumDocument:

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        self._pdf = None

    def open(self) -> None:

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy PDF: {self.pdf_path}"
            )

        if not self.pdf_path.is_file():
            raise ValueError(
                f"Không phải file: {self.pdf_path}"
            )

        self._pdf = pdfium.PdfDocument(
            self.pdf_path
        )

    @property
    def page_count(self) -> int:

        if self._pdf is None:
            raise RuntimeError(
                "Document chưa được mở"
            )

        return len(self._pdf)

    def get_page(self, page_index: int):

        if self._pdf is None:
            raise RuntimeError(
                "Document chưa được mở"
            )

        if not (
            0 <= page_index < len(self._pdf)
        ):
            raise IndexError(
                f"Page index không hợp lệ: "
                f"{page_index}"
            )

        return self._pdf[page_index]

    def close(self) -> None:

        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()
```

---

# 9. Infrastructure — Text Reader

## `infrastructure/pdfium/text_reader.py`

```python
from domain.font import FontInfo
from domain.geometry import BoundingBox
from domain.text import PageText


class PdfiumTextPageReader:

    def read_page(
        self,
        page,
        page_index: int,
    ) -> PageText:

        textpage = page.get_textpage()

        text = textpage.get_text_bounded()

        return PageText(
            page_index=page_index,
            page_number=page_index + 1,
            text=text,
        )

    def read_region(
        self,
        page,
        page_index: int,
        region: BoundingBox,
    ) -> PageText:

        textpage = page.get_textpage()

        text = textpage.get_text_bounded(
            left=region.left,
            bottom=region.bottom,
            right=region.right,
            top=region.top,
        )

        return PageText(
            page_index=page_index,
            page_number=page_index + 1,
            text=text,
        )
```

Đây là tầng duy nhất đang biết:

```python
page.get_textpage()
```

và:

```python
textpage.get_text_bounded()
```

pypdfium2 README chính thức hỗ trợ workflow này.

---

# 10. Application Extractor

## `application/extractor.py`

```python
from collections.abc import Iterator

from domain.text import PageText


class PdfTextExtractor:

    def __init__(
        self,
        document,
        reader,
    ):
        self.document = document
        self.reader = reader

    def extract_page(
        self,
        page_index: int,
    ) -> PageText:

        page = self.document.get_page(
            page_index
        )

        return self.reader.read_page(
            page,
            page_index,
        )

    def iter_pages(
        self,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> Iterator[PageText]:

        total = self.document.page_count

        if end_page is None:
            end_page = total

        if not 0 <= start_page < total:
            raise IndexError(
                "start_page không hợp lệ"
            )

        if not 0 < end_page <= total:
            raise IndexError(
                "end_page không hợp lệ"
            )

        if start_page >= end_page:
            raise ValueError(
                "start_page phải < end_page"
            )

        for page_index in range(
            start_page,
            end_page,
        ):
            yield self.extract_page(
                page_index
            )
```

Lưu ý:

```text
start_page
```

và:

```text
end_page
```

ở application đang dùng:

```text
0-based
[start, end)
```

Giống Python:

```python
range(start, end)
```

---

# 11. Tại sao dùng generator?

Không nên:

```python
pages = extractor.extract_all()
```

rồi:

```text
1000 pages
→ list
→ RAM
```

Thay vào đó:

```python
for page_text in extractor.iter_pages():
    process(page_text)
```

Pipeline:

```text
Page 1
 ↓
process
 ↓
Page 2
 ↓
process
 ↓
Page 3
 ↓
process
```

Đây là pattern chúng ta đã sử dụng từ Buổi 9–12.

---

# 12. Text Cleaner

Tách extraction khỏi cleaning.

## `application/extractor.py`

Thêm:

```python
class TextCleaner:

    def clean(self, text: str) -> str:

        lines = text.splitlines()

        cleaned_lines = [
            line.rstrip()
            for line in lines
        ]

        return "\n".join(
            cleaned_lines
        ).strip()
```

Đây là cleaner tương đối an toàn.

Không làm:

```python
text.replace("\n", " ")
```

vì có thể phá:

```text
Chapter 1

Paragraph 1

Paragraph 2
```

thành:

```text
Chapter 1 Paragraph 1 Paragraph 2
```

---

# 13. Application Service hoàn chỉnh

```python
from collections.abc import Iterator

from domain.text import PageText


class PdfTextService:

    def __init__(
        self,
        extractor,
        cleaner,
    ):
        self.extractor = extractor
        self.cleaner = cleaner

    def iter_clean_pages(
        self,
        start_page: int = 0,
        end_page: int | None = None,
    ) -> Iterator[PageText]:

        for page_text in self.extractor.iter_pages(
            start_page=start_page,
            end_page=end_page,
        ):

            cleaned = self.cleaner.clean(
                page_text.text
            )

            yield PageText(
                page_index=page_text.page_index,
                page_number=page_text.page_number,
                text=cleaned,
            )
```

---

# 14. Xuất TXT

Tạo:

```text
presentation/cli.py
```

Trước tiên hàm:

```python
from pathlib import Path


def write_text(
    output_path: Path,
    pages,
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for page in pages:

            file.write(
                f"\n===== PAGE "
                f"{page.page_number} =====\n\n"
            )

            file.write(page.text)

            file.write("\n")
```

Output:

```text
===== PAGE 1 =====

Chapter 1

Once upon a time...

===== PAGE 2 =====

The story continues...
```

---

# 15. CLI hoàn chỉnh

```python
import argparse
from pathlib import Path

from application.extractor import (
    PdfTextExtractor,
    PdfTextService,
    TextCleaner,
)
from infrastructure.pdfium.document import (
    PdfiumDocument,
)
from infrastructure.pdfium.text_reader import (
    PdfiumTextPageReader,
)


def build_parser():

    parser = argparse.ArgumentParser(
        description="Extract text from PDF"
    )

    parser.add_argument(
        "input",
        type=Path,
        help="PDF input",
    )

    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="TXT output",
    )

    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Trang bắt đầu, 1-based",
    )

    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="Trang kết thúc, 1-based",
    )

    return parser
```

---

# 16. Hàm main

Tiếp tục:

```python
def main():

    parser = build_parser()

    args = parser.parse_args()

    input_path = args.input

    if not input_path.exists():
        parser.error(
            f"Không tìm thấy file: {input_path}"
        )

    if args.start_page < 1:
        parser.error(
            "--start-page phải >= 1"
        )

    if (
        args.end_page is not None
        and args.end_page < args.start_page
    ):
        parser.error(
            "--end-page phải >= --start-page"
        )

    with PdfiumDocument(
        input_path
    ) as document:

        reader = PdfiumTextPageReader()

        extractor = PdfTextExtractor(
            document=document,
            reader=reader,
        )

        service = PdfTextService(
            extractor=extractor,
            cleaner=TextCleaner(),
        )

        start_index = (
            args.start_page - 1
        )

        end_index = args.end_page

        pages = service.iter_clean_pages(
            start_page=start_index,
            end_page=end_index,
        )

        if args.output is None:

            for page in pages:

                print(
                    f"\n===== PAGE "
                    f"{page.page_number} =====\n"
                )

                print(page.text)

        else:

            write_text(
                args.output,
                pages,
            )

            print(
                f"Đã extract → {args.output}"
            )


if __name__ == "__main__":
    main()
```

---

# 17. `__main__.py`

```python
from presentation.cli import main


if __name__ == "__main__":
    main()
```

Bây giờ:

```bash
python -m pdf_text_extractor sample.pdf
```

hoặc:

```bash
python -m pdf_text_extractor sample.pdf output.txt
```

---

# 18. Test BoundingBox

## `tests/test_geometry.py`

```python
from domain.geometry import BoundingBox


def test_width():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.width == 400


def test_height():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.height == 500


def test_area():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.area == 200_000


def test_contains_point():

    box = BoundingBox(
        100,
        200,
        500,
        700,
    )

    assert box.contains_point(
        300,
        400,
    )

    assert not box.contains_point(
        50,
        400,
    )


def test_intersects():

    a = BoundingBox(
        100,
        100,
        300,
        300,
    )

    b = BoundingBox(
        200,
        200,
        400,
        400,
    )

    assert a.intersects(b)


def test_not_intersects():

    a = BoundingBox(
        100,
        100,
        200,
        200,
    )

    b = BoundingBox(
        300,
        300,
        400,
        400,
    )

    assert not a.intersects(b)


def test_intersection():

    a = BoundingBox(
        100,
        100,
        300,
        300,
    )

    b = BoundingBox(
        200,
        200,
        400,
        400,
    )

    result = a.intersection(b)

    assert result is not None

    assert result.left == 200
    assert result.bottom == 200
    assert result.right == 300
    assert result.top == 300
```

Chạy:

```bash
pytest
```

---

# 19. Test TextCleaner

```python
from application.extractor import TextCleaner


def test_cleaner():

    cleaner = TextCleaner()

    text = """
Hello
World   
"""

    result = cleaner.clean(text)

    assert result == "Hello\nWorld"
```

---

# 20. Fake Document

Bây giờ đến phần rất quan trọng.

Ta không muốn test application bằng PDF thật.

Tạo:

```python
class FakePage:
    pass


class FakeDocument:

    def __init__(self):

        self.pages = [
            FakePage(),
            FakePage(),
            FakePage(),
        ]

    @property
    def page_count(self):
        return len(self.pages)

    def get_page(self, page_index):

        return self.pages[page_index]
```

---

# 21. Fake Text Reader

```python
from domain.text import PageText


class FakeTextReader:

    def read_page(
        self,
        page,
        page_index,
    ):

        return PageText(
            page_index=page_index,
            page_number=page_index + 1,
            text=f"Page {page_index + 1}",
        )
```

---

# 22. Test Extractor

```python
from application.extractor import (
    PdfTextExtractor,
)


def test_extract_page():

    document = FakeDocument()

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        document=document,
        reader=reader,
    )

    result = extractor.extract_page(0)

    assert result.page_number == 1
    assert result.text == "Page 1"
```

---

# 23. Test generator

```python
def test_iter_pages():

    document = FakeDocument()

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        document=document,
        reader=reader,
    )

    pages = list(
        extractor.iter_pages()
    )

    assert len(pages) == 3

    assert pages[0].text == "Page 1"
    assert pages[1].text == "Page 2"
    assert pages[2].text == "Page 3"
```

---

# 24. Test range

```python
def test_iter_pages_range():

    document = FakeDocument()

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        document=document,
        reader=reader,
    )

    pages = list(
        extractor.iter_pages(
            start_page=1,
            end_page=3,
        )
    )

    assert len(pages) == 2

    assert pages[0].page_number == 2
    assert pages[1].page_number == 3
```

Nhớ:

```text
start = inclusive
end   = exclusive
```

giống:

```python
range(1, 3)
```

---

# 25. Test Dependency Injection

Test này chứng minh Application **không phụ thuộc pypdfium2**.

```python
def test_extractor_does_not_need_pdfium():

    document = FakeDocument()

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        document=document,
        reader=reader,
    )

    page = extractor.extract_page(0)

    assert page.text == "Page 1"
```

Không cần:

```text
PDF
pypdfium2
PDFium
```

Đây chính là SOLID/DIP mà bạn đã học trước đây.

---

# 26. Test toàn bộ service

```python
def test_text_service():

    document = FakeDocument()

    reader = FakeTextReader()

    extractor = PdfTextExtractor(
        document=document,
        reader=reader,
    )

    service = PdfTextService(
        extractor=extractor,
        cleaner=TextCleaner(),
    )

    pages = list(
        service.iter_clean_pages()
    )

    assert len(pages) == 3

    assert pages[0].text == "Page 1"
    assert pages[1].text == "Page 2"
    assert pages[2].text == "Page 3"
```

---

# 27. Test thật với PDF

Đây là integration test.

Tạo:

```text
tests/data/sample.pdf
```

Sau đó:

```python
import pypdfium2 as pdfium


def test_real_pdf():

    pdf = pdfium.PdfDocument(
        "tests/data/sample.pdf"
    )

    try:

        page = pdf[0]

        textpage = page.get_textpage()

        text = textpage.get_text_bounded()

        assert isinstance(
            text,
            str,
        )

    finally:

        pdf.close()
```

Điểm quan trọng:

```text
Unit Test
    ↓
Fake
```

và:

```text
Integration Test
    ↓
PDF thật
    ↓
pypdfium2
```

không nên trộn hai loại test.

---

# 28. Thêm thống kê document

Project sẽ hữu ích hơn nếu CLI in:

```text
PDF: novel.pdf
Pages: 120
Text pages: 118
Empty pages: 2
Characters: 582340
```

Application service:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionStatistics:
    page_count: int
    non_empty_pages: int
    empty_pages: int
    character_count: int
```

---

# 29. Statistics collector

```python
class ExtractionStatisticsCollector:

    def collect(
        self,
        pages,
        page_count: int,
    ) -> ExtractionStatistics:

        non_empty = 0
        empty = 0
        characters = 0

        for page in pages:

            text = page.text

            if text.strip():
                non_empty += 1
            else:
                empty += 1

            characters += len(text)

        return ExtractionStatistics(
            page_count=page_count,
            non_empty_pages=non_empty,
            empty_pages=empty,
            character_count=characters,
        )
```

---

# 30. Nhưng có một vấn đề lớn

Nếu làm:

```python
pages = list(
    service.iter_clean_pages()
)
```

thì lại quay về:

```text
1200 pages
→ list
→ memory
```

Do đó statistics nên xử lý streaming:

```text
Page
 ↓
extract
 ↓
write
 ↓
statistics
 ↓
discard
```

Không cần giữ tất cả page.

---

# 31. Streaming pipeline

Architecture cuối:

```text
                  PDF
                   │
                   ▼
             PdfiumDocument
                   │
                   ▼
             PdfTextExtractor
                   │
                   ▼
              PageText
                   │
            ┌──────┴──────┐
            ▼             ▼
         Cleaner       Statistics
            │
            ▼
        TXT Writer
```

Một page đi qua pipeline rồi được giải phóng.

Đây là cách nên làm với PDF lớn.

---

# 32. Cải tiến: `ExtractionResult`

Nếu application muốn trả nhiều thông tin:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionResult:
    page: PageText
    character_count: int
    is_empty: bool
```

Nhưng hiện tại chưa cần over-engineering.

Project đầu tiên nên giữ:

```text
PageText
```

làm output chính.

---

# 33. Crop support

Ta có thể mở rộng extractor:

```python
class PdfTextExtractor:

    def __init__(
        self,
        document,
        reader,
    ):
        self.document = document
        self.reader = reader

    def extract_page(
        self,
        page_index: int,
        region=None,
    ):

        page = self.document.get_page(
            page_index
        )

        if region is None:

            return self.reader.read_page(
                page,
                page_index,
            )

        return self.reader.read_region(
            page,
            page_index,
            region,
        )
```

Nhưng interface cần đồng bộ:

```python
class TextPageReader(Protocol):

    def read_page(
        self,
        page,
        page_index: int,
    ) -> PageText:
        ...

    def read_region(
        self,
        page,
        page_index: int,
        region: BoundingBox,
    ) -> PageText:
        ...
```

---

# 34. CLI crop

Ta có thể thêm:

```python
parser.add_argument(
    "--left",
    type=float,
)

parser.add_argument(
    "--bottom",
    type=float,
)

parser.add_argument(
    "--right",
    type=float,
)

parser.add_argument(
    "--top",
    type=float,
)
```

Sau đó:

```python
region = None

if all(
    value is not None
    for value in (
        args.left,
        args.bottom,
        args.right,
        args.top,
    )
):

    region = BoundingBox(
        left=args.left,
        bottom=args.bottom,
        right=args.right,
        top=args.top,
    )
```

---

# 35. CLI thực tế

Ví dụ:

```bash
python -m pdf_text_extractor book.pdf
```

Extract toàn bộ.

---

Chỉ extract trang 10–20:

```bash
python -m pdf_text_extractor \
    book.pdf \
    book.txt \
    --start-page 10 \
    --end-page 20
```

---

Extract một vùng:

```bash
python -m pdf_text_extractor \
    book.pdf \
    content.txt \
    --left 50 \
    --bottom 100 \
    --right 550 \
    --top 750
```

---

# 36. Nhưng project hiện tại chưa phải "full layout extractor"

Đây là điều rất quan trọng.

Project hiện tại chủ yếu:

```text
PDF
 ↓
TextPage
 ↓
PageText
 ↓
TXT
```

Chúng ta **chưa** cố biến PDF thành HTML/Markdown hoàn chỉnh.

Ví dụ:

```text
Heading
Paragraph
Table
Image
Link
```

chưa được giữ hoàn toàn.

Đó là vì roadmap của chúng ta đang học từng abstraction.

---

# 37. Những gì chúng ta đã xây được

Sau Phần II:

```text
                    PDF
                     │
                     ▼
                 PdfPage
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    TextPage      Objects       Links
        │            │
        ▼            ▼
  Characters       Images
        │
        ├── BoundingBox
        │
        └── FontInfo
        │
        ▼
      Words
        │
        ▼
      Lines
        │
        ▼
   Layout Analysis
```

và:

```text
Region
  │
  ├── Text
  ├── Image
  ├── Object
  └── Link
```

---

# 38. Kiến trúc hoàn chỉnh của Mini Project

```text
┌─────────────────────────────────────┐
│           PRESENTATION              │
│                                     │
│               CLI                   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           APPLICATION               │
│                                     │
│        PdfTextService               │
│              │                      │
│        PdfTextExtractor             │
│              │                      │
│        TextPageReader               │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│              DOMAIN                 │
│                                     │
│ BoundingBox                         │
│ FontInfo                            │
│ PdfCharacter                        │
│ PdfWord                             │
│ PdfLine                             │
│ PageText                            │
└─────────────────────────────────────┘
                   ▲
                   │
┌─────────────────────────────────────┐
│          INFRASTRUCTURE             │
│                                     │
│ PdfiumDocument                      │
│ PdfiumTextPageReader                │
│                                     │
│            pypdfium2                │
└─────────────────────────────────────┘
```

---

# 39. Điểm quan trọng nhất của Buổi 20

Không phải:

```python
text = textpage.get_text_bounded()
```

mà là cách chúng ta tổ chức hệ thống:

```text
pypdfium2
    ↓
Adapter
    ↓
Application Port
    ↓
Domain Model
    ↓
Use Case
    ↓
CLI
```

Nhờ vậy sau này chúng ta có thể thay:

```text
pypdfium2
```

bằng:

```text
PyMuPDF
pypdf
OCR
```

mà application/domain ít bị ảnh hưởng.

---

# 40. Khi project lớn lên

Mini project hôm nay:

```text
PDF
 ↓
Text
 ↓
TXT
```

Sau này có thể tiến hóa thành:

```text
PDF Analyzer
│
├── Text Extraction
├── Character Analysis
├── Font Analysis
├── Layout Analysis
├── Image Extraction
├── Link Extraction
├── Table Detection
├── Chapter Detection
├── Metadata
└── OCR fallback
```

và application lớn hơn:

```text
PDF
 │
 ▼
Document Analysis
 │
 ├── Page Analysis
 │
 ├── Text Analysis
 │
 ├── Image Analysis
 │
 └── Layout Analysis
 │
 ▼
StructuredDocument
 │
 ├── Chapter
 ├── Heading
 ├── Paragraph
 ├── Image
 ├── Link
 └── ...
```

Đây chính là hướng phù hợp nếu sau này bạn muốn dùng `pypdfium2` làm **PDF parsing engine** cho hệ thống đọc/trích xuất tài liệu.

---

# 41. Phần II đã hoàn thành

Roadmap hiện tại:

```text
# Phần I — Làm quen
01. Cài đặt và kiến trúc
02. PdfDocument
03. PdfPage
04. Metadata
05. Render → Bitmap
06. Bitmap → PIL
07. DPI / Scale
08. PNG / JPEG
09. Render toàn bộ PDF
10. PDF → Image Converter

# Phần II — Đọc và phân tích PDF
11. TextPage                    ✅
12. Extract text                ✅
13. Text position / BoundingBox ✅
14. Character extraction       ✅
15. Link / Annotation           ✅
16. Page objects                ✅
17. Images                      ✅
18. Font / Text information     ✅
19. Crop / Clipping             ✅
20. PDF Text Extractor          ✅
```

## Những kiến thức cốt lõi bạn đã có

```text
PdfDocument
PdfPage
PdfTextPage
PdfCharacter
PdfWord
PdfLine
BoundingBox
FontInfo
PdfImage
PdfLink
PageObject
Region
```

và pipeline:

```text
PDF
 │
 ▼
PdfDocument
 │
 ▼
PdfPage
 │
 ├───────────────┐
 ▼               ▼
TextPage      Page Objects
 │               │
 ▼               ├── Image
Character        ├── Path
 │               ├── Text
 ▼               └── Form
Word
 │
 ▼
Line
 │
 ▼
PageText
 │
 ▼
Text Extractor
```

**Phần III tiếp theo sẽ là phần xử lý sâu hơn các thành phần PDF**, và khi chuyển sang phần đó chúng ta sẽ tiếp tục giữ nguyên nguyên tắc: **học API → xây abstraction → code hoàn chỉnh → test → ghép vào kiến trúc**, không đi lan man sang thư viện khác.
