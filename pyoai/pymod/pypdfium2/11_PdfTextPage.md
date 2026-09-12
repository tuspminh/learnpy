# Buổi 11 — `PdfTextPage`

**Phần II — Đọc và phân tích PDF**

Roadmap:

```text
11. TextPage                    ← Hôm nay
12. Extract text
13. Text position / bounding box
14. Character-level extraction
15. Link / annotation
16. Page objects
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Ở Phần I, chúng ta đi theo pipeline:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
PdfBitmap
 ↓
PIL.Image
```

Từ Phần II, chúng ta mở thêm một nhánh:

```text
PDF
 ↓
PdfDocument
 ↓
PdfPage
 ↓
PdfTextPage
 ↓
Text
```

`PdfTextPage` là đối tượng quan trọng để **truy cập lớp text của một trang PDF**. pypdfium2 cung cấp `page.get_textpage()` để tạo text page; từ đó có thể truy xuất text của trang.

---

# 1. `PdfTextPage` là gì?

Giả sử PDF có:

```text
┌──────────────────────────────┐
│        CHƯƠNG 1              │
│                              │
│ Đây là nội dung của truyện.  │
│                              │
│ Tác giả: Nguyễn Văn A        │
│                              │
└──────────────────────────────┘
```

`PdfPage` đại diện cho **toàn bộ trang**.

```python
page = pdf[0]
```

Còn:

```python
textpage = page.get_textpage()
```

là đối tượng giúp chúng ta làm việc với **text information** của trang.

---

# 2. Kiến trúc

```text
PdfDocument
     │
     ▼
  PdfPage
     │
     ├──────────────► render()
     │                    │
     │                    ▼
     │                 PdfBitmap
     │                    │
     │                    ▼
     │                 PIL.Image
     │
     └──────────────► get_textpage()
                          │
                          ▼
                     PdfTextPage
                          │
                          ▼
                        Text
```

Đây là điểm rất quan trọng:

> **Text extraction không cần render PDF thành ảnh.**

Không cần:

```text
PDF
 ↓
PNG
 ↓
OCR
 ↓
Text
```

nếu PDF vốn đã chứa text.

Ta có thể:

```text
PDF
 ↓
PdfTextPage
 ↓
Text
```

nhanh và chính xác hơn.

---

# 3. PDF có phải lúc nào cũng có text?

**Không.**

Đây là một khái niệm cực kỳ quan trọng.

Có hai loại PDF phổ biến.

### PDF dạng text

Ví dụ PDF được tạo từ Word:

```text
PDF
 ├── text objects
 ├── fonts
 ├── images
 └── graphics
```

Ta có thể:

```python
page.get_textpage()
```

và lấy text.

---

### PDF scan

Ví dụ một trang sách được scan:

```text
PDF
 └── image
```

Nhìn bằng mắt:

```text
┌────────────────────┐
│ CHƯƠNG 1           │
│ Đây là nội dung... │
└────────────────────┘
```

nhưng bên trong PDF có thể chỉ là:

```text
Image
```

chứ không có text object.

Khi đó:

```python
textpage.get_text_bounded()
```

có thể trả về text rỗng hoặc rất ít.

Muốn đọc chữ cần:

```text
PDF
 ↓
Render
 ↓
Image
 ↓
OCR
 ↓
Text
```

Ví dụ:

```text
pypdfium2
    ↓
PIL
    ↓
OpenCV
    ↓
Tesseract / PaddleOCR
```

Vì vậy:

> `PdfTextPage` không phải OCR.

---

# 4. Tạo `PdfTextPage`

Code đơn giản nhất:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

page = pdf[0]

textpage = page.get_textpage()

pdf.close()
```

Luồng:

```python
page
  ↓
get_textpage()
  ↓
PdfTextPage
```

---

# 5. Lấy toàn bộ text

pypdfium2 cung cấp:

```python
textpage.get_text_bounded()
```

để lấy text trong vùng giới hạn; nếu không truyền bounds thì có thể lấy toàn bộ text của trang.

Ví dụ:

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

Đây chính là nền tảng cho Buổi 12.

---

# 6. Viết thành function

Ta không nên viết mọi thứ trong `main.py`.

```python
from pathlib import Path

import pypdfium2 as pdfium


def extract_page_text(
    pdf_path: str | Path,
    page_index: int,
) -> str:

    pdf = pdfium.PdfDocument(pdf_path)

    try:

        if not 0 <= page_index < len(pdf):
            raise IndexError(
                f"Page index không hợp lệ: "
                f"{page_index}"
            )

        page = pdf[page_index]

        textpage = page.get_textpage()

        return textpage.get_text_bounded()

    finally:

        pdf.close()
```

Sử dụng:

```python
text = extract_page_text(
    "sample.pdf",
    0,
)

print(text)
```

---

# 7. Tại sao không dùng `page` trực tiếp để lấy text?

Bởi vì pypdfium2 phân chia trách nhiệm:

```text
PdfPage
    │
    ├── geometry
    ├── rendering
    ├── rotation
    │
    └── text
           ↓
       PdfTextPage
```

Ta có:

```python
page.get_size()
```

cho geometry.

```python
page.render()
```

cho rendering.

```python
page.get_textpage()
```

cho text.

Đây là một abstraction rất hợp lý.

---

# 8. `PdfTextPage` không phải là `str`

Đây là lỗi người mới rất dễ mắc.

Sai:

```python
textpage = page.get_textpage()

print(textpage)
```

`textpage` là object:

```text
PdfTextPage
```

Muốn lấy text:

```python
text = textpage.get_text_bounded()
```

Khi đó:

```text
PdfTextPage
      ↓
   get_text_bounded()
      ↓
     str
```

---

# 9. Ví dụ đầy đủ

Tạo file:

```text
read_pdf_text.py
```

```python
from pathlib import Path

import pypdfium2 as pdfium


def read_first_page(
    pdf_path: str | Path,
) -> str:

    pdf = pdfium.PdfDocument(pdf_path)

    try:

        if len(pdf) == 0:
            return ""

        page = pdf[0]

        textpage = page.get_textpage()

        text = textpage.get_text_bounded()

        return text

    finally:

        pdf.close()


def main() -> None:

    pdf_path = Path("sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy: {pdf_path}"
        )

    text = read_first_page(pdf_path)

    print("=" * 60)
    print("TEXT CỦA TRANG 1")
    print("=" * 60)

    print(text)

    print("=" * 60)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python read_pdf_text.py
```

Nếu PDF có text:

```text
============================================================
TEXT CỦA TRANG 1
============================================================

CHƯƠNG 1

Một ngày nọ...

Tác giả: Nguyễn Văn A

============================================================
```

---

# 10. Xử lý newline

Text lấy từ PDF đôi khi không đẹp:

```text
CHƯƠNG 1


Đây là nội dung...


Tác giả:
Nguyễn Văn A
```

Đừng vội `.strip()` rồi nghĩ rằng đã xử lý xong.

Trước tiên hãy **quan sát raw text**:

```python
print(repr(text))
```

Ví dụ:

```python
print(repr(text))
```

có thể cho:

```text
'CHƯƠNG 1\n\nĐây là nội dung...\n'
```

Điều này cực kỳ hữu ích khi debug PDF extraction.

---

# 11. `repr()` rất quan trọng

So sánh:

```python
print(text)
```

và:

```python
print(repr(text))
```

`print()`:

```text
CHƯƠNG 1

Đây là nội dung.
```

`repr()`:

```text
'CHƯƠNG 1\n\nĐây là nội dung.'
```

Nhờ đó ta nhìn thấy:

```text
\n
\t
\r
```

và các ký tự whitespace.

Trong quá trình xây dựng PDF parser, tôi khuyến nghị luôn dùng:

```python
print(repr(text))
```

khi debugging.

---

# 12. TextPage có thể lấy text theo vùng

Đây là tính năng rất quan trọng cho các bài sau.

Ví dụ:

```python
text = textpage.get_text_bounded(
    left=50,
    bottom=100,
    right=500,
    top=700,
)
```

pypdfium2 hỗ trợ các tọa độ `left`, `bottom`, `right`, `top` để giới hạn vùng text được lấy.

Ta có:

```text
                 top
                  ↑
        ┌───────────────────┐
        │                   │
        │     PDF PAGE      │
        │                   │
 left → │   ┌───────────┐   │ ← right
        │   │ TEXT AREA │   │
        │   └───────────┘   │
        │                   │
        └───────────────────┘
                  ↓
                bottom
```

Đây chính là cầu nối sang:

**Buổi 13 — Text position / bounding box.**

---

# 13. PDF coordinates khác pixel

Nhớ lại Phần I:

```python
width, height = page.get_size()
```

đơn vị là **PDF points**.

Không phải:

```text
pixels
```

Ví dụ A4:

```text
≈ 595 × 842 points
```

Trong khi render 300 DPI:

```text
≈ 2480 × 3508 pixels
```

Do đó khi làm text extraction:

```text
Text coordinates
        ↓
PDF coordinate system
```

còn khi render:

```text
Image coordinates
        ↓
pixel system
```

Không nên trộn hai hệ tọa độ.

---

# 14. Lấy kích thước trang cùng TextPage

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:

    page = pdf[0]

    width, height = page.get_size()

    textpage = page.get_textpage()

    text = textpage.get_text_bounded()

    print(f"Page size: {width} × {height}")
    print(repr(text))

finally:

    pdf.close()
```

Kết quả có thể:

```text
Page size: 595.0 × 842.0
'CHƯƠNG 1\n\nNội dung...'
```

---

# 15. TextPage trong kiến trúc crawler/document system

Điều này rất phù hợp với project lớn của bạn.

Ta có thể thiết kế:

```text
infrastructure/
└── pdfium/
    ├── document.py
    ├── renderer.py
    └── text_reader.py
```

`text_reader.py`:

```python
class PdfTextReader:

    def read_page(
        self,
        page,
    ) -> str:

        textpage = page.get_textpage()

        return textpage.get_text_bounded()
```

Sau đó:

```text
Application
     │
     ▼
PdfTextReader
     │
     ▼
PdfPage
     │
     ▼
PdfTextPage
```

Application không cần biết chi tiết:

```python
page.get_textpage()
```

---

# 16. Tạo `PdfTextReader`

File:

```text
infrastructure/pdfium/text_reader.py
```

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

Ở bài này ta tạm dùng:

```python
Any
```

vì chưa cần tạo abstraction quá sâu.

Sau khi học:

```text
Protocol
ABC
Typing
```

chúng ta có thể thiết kế interface đẹp hơn.

---

# 17. Test với PDF thật

Tạo:

```text
inspect_text.py
```

```python
from pathlib import Path

import pypdfium2 as pdfium

from pdf_converter.infrastructure.pdfium.text_reader import (
    PdfTextReader,
)


def main() -> None:

    pdf_path = Path("sample.pdf")

    pdf = pdfium.PdfDocument(pdf_path)

    try:

        reader = PdfTextReader()

        for page_index in range(len(pdf)):

            page = pdf[page_index]

            text = reader.read_page(page)

            print(
                f"\n{'=' * 60}"
            )

            print(
                f"PAGE {page_index + 1}"
            )

            print(
                f"{'=' * 60}"
            )

            print(repr(text))

    finally:

        pdf.close()


if __name__ == "__main__":
    main()
```

Đây là bước kiểm tra rất tốt để xác định:

> PDF của mình có text layer hay không?

---

# 18. PDF text vs scanned PDF

Hãy thử hai file:

### File A

PDF được tạo từ Word:

```text
PDF
 ↓
PdfTextPage
 ↓
Có text
```

### File B

PDF scan:

```text
PDF
 ↓
PdfTextPage
 ↓
""
```

Nếu File B hiển thị chữ nhưng extraction ra:

```python
''
```

thì đừng nghĩ:

> pypdfium2 bị lỗi.

Có khả năng PDF chỉ chứa image.

Pipeline khi đó là:

```text
              PDF
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   Text layer       Image only
       │                │
       ▼                ▼
 PdfTextPage         Render
       │                │
       ▼                ▼
     Text              PIL
                        │
                        ▼
                       OCR
                        │
                        ▼
                       Text
```

Đây sẽ là nền tảng rất quan trọng nếu sau này chúng ta xây **PDF OCR pipeline**.

---

# 19. Resource management

Ta đang có:

```text
PdfDocument
PdfPage
PdfTextPage
```

Quy tắc hiện tại:

```python
pdf = pdfium.PdfDocument(...)
try:
    ...
finally:
    pdf.close()
```

Không nên:

```python
for page in pages:
    pdf = pdfium.PdfDocument(...)
```

vì sẽ mở/đóng document liên tục.

Đúng:

```text
open PDF
    │
    ├── page 1 → TextPage → text
    ├── page 2 → TextPage → text
    ├── page 3 → TextPage → text
    └── page N → TextPage → text
    │
close PDF
```

---

# 20. Một abstraction hoàn chỉnh hơn

Sau những gì đã học ở Phần I, ta có thể ghép:

```text
PdfDocumentSession
        │
        └── PdfPage
              │
        ┌─────┴──────┐
        ▼            ▼
 PdfRenderer     PdfTextReader
        │            │
        ▼            ▼
   PIL.Image       str
```

Một `PdfPage` có thể phục vụ **hai pipeline độc lập**:

```text
                    PdfPage
                   /       \
                  /         \
                 ▼           ▼
             Rendering      Text
                 │           │
                 ▼           ▼
             Image          String
```

Đây là một design rất hữu ích cho project PDF lớn.

---

# 21. Bài tập thực hành

### Bài 1

Viết:

```python
get_page_text(pdf_path, page_index)
```

Yêu cầu:

```text
PDF path
   ↓
PdfDocument
   ↓
PdfPage
   ↓
PdfTextPage
   ↓
str
```

---

### Bài 2

In text của **10 trang đầu tiên**:

```text
PAGE 1
------

...

PAGE 2
------

...
```

---

### Bài 3

In:

```text
Page: 1
Size: 595 × 842
Characters: 1234
```

Gợi ý:

```python
len(text)
```

---

### Bài 4

Kiểm tra PDF scan:

```python
text = textpage.get_text_bounded()

if not text.strip():
    print("Có thể đây là scanned PDF")
```

Lưu ý: đây chỉ là **heuristic**, không phải bằng chứng tuyệt đối.

---

### Bài 5 — quan trọng

Render trang đầu tiên:

```python
image = page.render(
    scale=2
).to_pil()
```

đồng thời lấy text:

```python
textpage = page.get_textpage()

text = textpage.get_text_bounded()
```

Sau đó in:

```text
PDF Page
   ├── Image
   └── Text
```

Mục tiêu là hiểu rằng:

> **Một `PdfPage` có thể được khai thác theo nhiều hướng khác nhau.**

---

# 22. Tổng kết Buổi 11

Hôm nay cần nhớ 5 dòng quan trọng nhất:

```python
pdf = pdfium.PdfDocument("sample.pdf")

page = pdf[0]

textpage = page.get_textpage()

text = textpage.get_text_bounded()

pdf.close()
```

Pipeline:

```text
PdfDocument
     ↓
PdfPage
     ↓
get_textpage()
     ↓
PdfTextPage
     ↓
get_text_bounded()
     ↓
str
```

Và phân biệt:

```text
PDF có text
    ↓
PdfTextPage
    ↓
Text extraction
```

với:

```text
PDF scan
    ↓
Render
    ↓
Image
    ↓
OCR
    ↓
Text
```

**Buổi 12** sẽ đi sâu vào **Extract Text**: không chỉ lấy toàn bộ text của trang, mà bắt đầu xử lý text thực tế — newline, whitespace, nhiều trang, thứ tự text, encoding và xây dựng `PdfTextExtractor` dùng được cho project PDF của chúng ta.
