# Buổi 2 — `PdfDocument`: Mở và quản lý PDF

Ở Buổi 1, chúng ta đã biết:

```text
PdfDocument
    ↓
PdfPage
    ↓
PDF page
```

Hôm nay tập trung vào **`PdfDocument`**: mở PDF từ file/bytes, kiểm tra document, truy cập page và quản lý resource.

---

## 1. Mở PDF từ đường dẫn

Cách cơ bản:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("sample.pdf")

print("Pages:", len(pdf))
```

`PdfDocument` đại diện cho **toàn bộ file PDF**.

```text
sample.pdf
    │
    ▼
PdfDocument
    │
    ├── Page 0
    ├── Page 1
    ├── Page 2
    └── ...
```

---

# 2. Mở PDF bằng `pathlib.Path`

Trong project thực tế, tôi khuyên dùng `Path`.

```python
from pathlib import Path
import pypdfium2 as pdfium


pdf_path = Path("sample.pdf")

pdf = pdfium.PdfDocument(pdf_path)

print("Pages:", len(pdf))
```

Điều này phù hợp với những gì bạn đã học về `pathlib`.

Có thể kiểm tra trước:

```python
from pathlib import Path
import pypdfium2 as pdfium


def open_pdf(path: str) -> pdfium.PdfDocument:
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"Not a file: {pdf_path}"
        )

    return pdfium.PdfDocument(pdf_path)
```

---

# 3. Mở PDF từ bytes

Đây là phần rất quan trọng.

Không phải lúc nào PDF cũng nằm trên disk.

Ví dụ:

```text
HTTP response
     ↓
bytes
     ↓
pypdfium2
```

Có thể đọc:

```python
from pathlib import Path
import pypdfium2 as pdfium


data = Path("sample.pdf").read_bytes()

pdf = pdfium.PdfDocument(data)

print("Pages:", len(pdf))
```

Tức là:

```python
pdfium.PdfDocument("sample.pdf")
```

và:

```python
pdfium.PdfDocument(data)
```

đều có thể dẫn tới một `PdfDocument`.

---

# 4. Tại sao mở từ bytes rất hữu ích?

Ví dụ crawler của bạn tải PDF bằng HTTPX:

```python
import httpx
import pypdfium2 as pdfium


response = httpx.get(
    "https://example.com/book.pdf"
)

response.raise_for_status()

pdf = pdfium.PdfDocument(response.content)

print("Pages:", len(pdf))
```

Pipeline:

```text
HTTPX
  │
  │ response.content
  ▼
bytes
  │
  ▼
pypdfium2
  │
  ▼
PdfDocument
  │
  ▼
PdfPage
```

Như vậy không nhất thiết phải:

```text
download PDF
      ↓
save disk
      ↓
read disk
```

mà có thể:

```text
HTTP
 ↓
bytes
 ↓
PDF processing
```

Điều này sẽ rất hữu ích khi sau này chúng ta kết hợp:

* `httpx`
* `pypdfium2`
* `asyncio`
* OCR
* crawler.

---

# 5. Đếm số trang

`PdfDocument` hỗ trợ `len()`:

```python
pdf = pdfium.PdfDocument("sample.pdf")

print(len(pdf))
```

Ví dụ:

```text
120
```

Có nghĩa:

```text
Page 0
Page 1
...
Page 119
```

**Không phải:**

```text
Page 1
...
Page 120
```

Trong Python index bắt đầu từ `0`.

---

# 6. Lấy page

Cách phổ biến:

```python
page = pdf[0]
```

Trang thứ hai:

```python
page = pdf[1]
```

Trang cuối:

```python
page = pdf[-1]
```

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

first_page = pdf[0]
last_page = pdf[-1]

print(first_page)
print(last_page)
```

---

# 7. Duyệt toàn bộ PDF

Cách đơn giản:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

for page_index in range(len(pdf)):
    page = pdf[page_index]

    width, height = page.get_size()

    print(
        f"Page {page_index + 1}: "
        f"{width:.2f} x {height:.2f}"
    )
```

Tư duy:

```text
PdfDocument
     │
     ├── [0]
     ├── [1]
     ├── [2]
     └── [n]
```

---

# 8. Kiểm tra page index

Nếu PDF có 10 trang:

```python
pdf[9]
```

hợp lệ.

Nhưng:

```python
pdf[10]
```

sẽ vượt giới hạn.

Do đó nếu xây API riêng, ta nên kiểm tra:

```python
def get_page(
    pdf: pdfium.PdfDocument,
    page_index: int,
):
    if page_index < 0 or page_index >= len(pdf):
        raise IndexError(
            f"Invalid page index: {page_index}"
        )

    return pdf[page_index]
```

---

# 9. Resource lifecycle

Đây là phần tôi muốn bạn chú ý.

PDFium sử dụng native resources bên dưới Python.

Do đó:

```python
pdf = pdfium.PdfDocument("sample.pdf")
```

không đơn giản chỉ là một object Python thuần túy.

Ta nên có ý thức về:

```text
Python object
     │
     ▼
native PDFium resource
```

Khi xử lý nhiều PDF:

```text
PDF 1
PDF 2
PDF 3
...
PDF 1000
```

thì lifecycle rất quan trọng.

---

# 10. Đóng document

Có thể gọi:

```python
pdf.close()
```

Ví dụ:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    print("Pages:", len(pdf))
finally:
    pdf.close()
```

Pattern:

```text
open
  ↓
process
  ↓
close
```

---

# 11. Một `PdfDocumentLoader`

Bây giờ bắt đầu thiết kế abstraction.

Thay vì để toàn bộ application viết:

```python
pdfium.PdfDocument(...)
```

khắp nơi, chúng ta tạo:

```text
application
     │
     ▼
PdfDocumentLoader
     │
     ▼
pypdfium2
```

Ví dụ:

```python
from pathlib import Path
import pypdfium2 as pdfium


class PdfDocumentLoader:
    def load(
        self,
        path: str | Path,
    ) -> pdfium.PdfDocument:

        pdf_path = Path(path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if not pdf_path.is_file():
            raise ValueError(
                f"Not a file: {pdf_path}"
            )

        return pdfium.PdfDocument(pdf_path)
```

Sử dụng:

```python
loader = PdfDocumentLoader()

pdf = loader.load("sample.pdf")

print("Pages:", len(pdf))

pdf.close()
```

---

# 12. Thêm hỗ trợ bytes

Ta có thể thiết kế:

```python
from pathlib import Path
import pypdfium2 as pdfium


class PdfDocumentLoader:

    def load_file(
        self,
        path: str | Path,
    ) -> pdfium.PdfDocument:

        pdf_path = Path(path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        return pdfium.PdfDocument(pdf_path)

    def load_bytes(
        self,
        data: bytes,
    ) -> pdfium.PdfDocument:

        if not data:
            raise ValueError(
                "PDF data is empty"
            )

        return pdfium.PdfDocument(data)
```

Sử dụng:

```python
loader = PdfDocumentLoader()

pdf = loader.load_file("sample.pdf")

try:
    print(len(pdf))
finally:
    pdf.close()
```

Hoặc:

```python
data = Path("sample.pdf").read_bytes()

pdf = loader.load_bytes(data)

try:
    print(len(pdf))
finally:
    pdf.close()
```

---

# 13. Một vấn đề kiến trúc

Có một câu hỏi rất đáng suy nghĩ:

> Có nên để Domain biết `pypdfium2` không?

Ví dụ **không nên**:

```python
class Novel:
    pdf: pdfium.PdfDocument
```

Vì:

```text
Domain
  ↓
pypdfium2
```

làm Domain phụ thuộc infrastructure/library cụ thể.

Theo Clean Architecture:

```text
Domain
   ↑
Application
   ↑
Infrastructure
   │
   └── pypdfium2
```

Do đó `pypdfium2` nên nằm ở Infrastructure/PDF adapter.

---

# 14. Kiến trúc bước đầu

Ta có thể bắt đầu:

```text
pdf_engine/
│
├── domain/
│
├── application/
│
├── infrastructure/
│   └── pdfium/
│       ├── document_loader.py
│       └── renderer.py
│
└── cli/
```

Sau này:

```text
                 Application
                      │
                      ▼
              PdfDocumentLoader
                      │
                      ▼
              pypdfium2 Adapter
                      │
                      ▼
                   PDFium
```

Đây sẽ rất phù hợp với kiến trúc mà bạn đang học trong các project crawler.

---

# 15. Chương trình hoàn chỉnh Buổi 2

Tạo:

```text
lesson02/
│
├── main.py
└── sample.pdf
```

`main.py`:

```python
from pathlib import Path

import pypdfium2 as pdfium


class PdfDocumentLoader:
    """Load PDF documents using pypdfium2."""

    def load_file(
        self,
        path: str | Path,
    ) -> pdfium.PdfDocument:

        pdf_path = Path(path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if not pdf_path.is_file():
            raise ValueError(
                f"Not a file: {pdf_path}"
            )

        return pdfium.PdfDocument(pdf_path)

    def load_bytes(
        self,
        data: bytes,
    ) -> pdfium.PdfDocument:

        if not data:
            raise ValueError(
                "PDF data is empty"
            )

        return pdfium.PdfDocument(data)


def inspect_pdf(
    pdf: pdfium.PdfDocument,
) -> None:

    print("Number of pages:", len(pdf))

    for index in range(len(pdf)):
        page = pdf[index]

        width, height = page.get_size()

        print(
            f"Page {index + 1}: "
            f"{width:.2f} x {height:.2f}"
        )


def main() -> None:

    loader = PdfDocumentLoader()

    pdf = loader.load_file("sample.pdf")

    try:
        inspect_pdf(pdf)

    finally:
        pdf.close()


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

Ví dụ:

```text
Number of pages: 5
Page 1: 595.28 x 841.89
Page 2: 595.28 x 841.89
Page 3: 595.28 x 841.89
Page 4: 595.28 x 841.89
Page 5: 595.28 x 841.89
```

---

# 16. Bài tập thực hành

### Bài 1

Viết:

```python
load_pdf(path)
```

trả về `PdfDocument`.

### Bài 2

Viết:

```python
get_page_count(pdf)
```

### Bài 3

Viết:

```python
get_page_size(pdf, page_index)
```

trả về:

```python
(width, height)
```

### Bài 4

Viết:

```python
inspect_pdf(path)
```

in:

```text
File: sample.pdf
Pages: 10

Page 1
  Width: 595.28
  Height: 841.89

Page 2
  Width: 595.28
  Height: 841.89
```

### Bài 5 — quan trọng

Thử mở PDF từ bytes:

```python
data = Path("sample.pdf").read_bytes()

pdf = loader.load_bytes(data)
```

Nếu chạy được, bạn đã hiểu được hai nguồn input quan trọng:

```text
File
 │
 └──► PdfDocument

Bytes
 │
 └──► PdfDocument
```

---

## Kiến thức cần nhớ sau Buổi 2

```text
PdfDocument
│
├── PdfDocument(path)
│
├── PdfDocument(bytes)
│
├── len(pdf)
│
├── pdf[index]
│
├── page.get_size()
│
└── pdf.close()
```

Và kiến trúc:

```text
Application
     │
     ▼
PdfDocumentLoader
     │
     ▼
pypdfium2
     │
     ▼
PDFium
```

**Buổi 3** chúng ta sẽ đi sâu vào **`PdfPage`**: lifecycle của page, kích thước trang, rotation, coordinate system và đặc biệt là cách **render một `PdfPage` thành bitmap** — đây là phần cốt lõi nhất của `pypdfium2`.
