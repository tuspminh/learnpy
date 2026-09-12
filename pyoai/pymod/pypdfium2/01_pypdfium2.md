
# Buổi 1 — Kiến trúc pypdfium2

## 1. pypdfium2 là gì?

`pypdfium2` là Python binding cho **PDFium**, engine xử lý PDF được phát triển bởi Google/Chromium.

Có thể hình dung:

```text
Python
   │
   ▼
pypdfium2
   │
   ▼
PDFium
   │
   ▼
PDF
```

Điểm quan trọng:

> `pypdfium2` không chỉ đơn giản là một thư viện "đọc PDF".

Nó đặc biệt mạnh ở việc **render PDF**.

Ví dụ:

```text
PDF
 │
 ├── Page 1 ──► Render ──► Image
 ├── Page 2 ──► Render ──► Image
 ├── Page 3 ──► Render ──► Image
 └── Page 4 ──► Render ──► Image
```

Điều này rất hữu ích cho:

* PDF viewer
* PDF thumbnail
* PDF preview
* OCR
* PDF scanner processing
* document indexing
* image extraction pipeline
* tạo ảnh preview cho app GUI

---

# 2. So sánh với các thư viện PDF khác

Bạn nên phân biệt rõ:

```text
PyPDF
   ↓
PDF structure / manipulation

PyMuPDF
   ↓
PDF + rendering + text + image + annotation

pypdfium2
   ↓
PDFium rendering engine
```

Không có nghĩa thư viện nào "tốt nhất".

Mỗi thư viện có thế mạnh khác nhau.

Ví dụ:

| Thư viện     | Điểm mạnh               |
| ------------ | ----------------------- |
| `pypdf`      | đọc/sửa/merge/split PDF |
| `PyMuPDF`    | PDF processing tổng hợp |
| `pypdfium2`  | PDFium rendering        |
| `pdfplumber` | text/table extraction   |
| `Pillow`     | xử lý ảnh               |

Trong khóa này chúng ta sẽ tập trung vào:

```text
pypdfium2
     │
     ├── Document
     ├── Page
     ├── Text
     ├── Bitmap
     └── Rendering
```

---

# 3. Cài đặt

Tạo môi trường:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Cài:

```bash
pip install pypdfium2
```

Kiểm tra:

```bash
python -c "import pypdfium2; print(pypdfium2.__version__)"
```

---

# 4. Import

Thông thường:

```python
import pypdfium2 as pdfium
```

Sau đó:

```python
pdf = pdfium.PdfDocument("document.pdf")
```

Ta có:

```text
PdfDocument
     │
     ├── Page 0
     ├── Page 1
     ├── Page 2
     └── ...
```

Lưu ý:

**Index bắt đầu từ 0.**

```python
page = pdf[0]
```

là trang đầu tiên.

---

# 5. Chương trình đầu tiên

Tạo:

```text
lesson01/
│
├── main.py
└── sample.pdf
```

`main.py`:

```python
import pypdfium2 as pdfium


def main():
    pdf = pdfium.PdfDocument("sample.pdf")

    print("Number of pages:", len(pdf))

    for index in range(len(pdf)):
        page = pdf[index]
        print("Page:", index + 1)
        print("Page object:", page)


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
Page: 1
Page object: ...
Page: 2
Page object: ...
Page: 3
Page object: ...
Page: 4
Page object: ...
Page: 5
Page object: ...
```

---

# 6. Hiểu `PdfDocument`

Đây là object trung tâm:

```python
pdf = pdfium.PdfDocument("sample.pdf")
```

Ta có:

```text
PdfDocument
     │
     ├── PdfPage
     ├── PdfPage
     ├── PdfPage
     └── PdfPage
```

Ví dụ:

```python
page = pdf[0]
```

hoặc:

```python
page = pdf.get_page(0)
```

Tư duy:

```python
document = PdfDocument(...)
page = document[0]
```

giống:

```python
book
  ↓
chapter
```

---

# 7. Lấy kích thước trang

Một thao tác rất quan trọng:

```python
page.get_size()
```

Ví dụ:

```python
import pypdfium2 as pdfium


def main():
    pdf = pdfium.PdfDocument("sample.pdf")

    for index in range(len(pdf)):
        page = pdf[index]

        width, height = page.get_size()

        print(
            f"Page {index + 1}: "
            f"{width:.2f} x {height:.2f}"
        )


if __name__ == "__main__":
    main()
```

Ví dụ output:

```text
Page 1: 595.28 x 841.89
Page 2: 595.28 x 841.89
Page 3: 595.28 x 841.89
```

Đây gần với kích thước chuẩn A4 theo đơn vị PDF.

---

# 8. Vì sao kích thước không phải pixel?

Đây là kiến thức cực kỳ quan trọng.

PDF không phải bản chất là một ảnh.

PDF thường chứa:

```text
Text
Vector
Image
Path
Font
Annotation
...
```

Kích thước trang được biểu diễn trong **PDF points**.

Thông thường:

```text
72 points = 1 inch
```

Ví dụ A4:

```text
210 mm × 297 mm
```

xấp xỉ:

```text
595 × 842 points
```

Nhưng khi render:

```text
PDF
 ↓
Renderer
 ↓
Bitmap
```

ta mới có:

```text
pixels
```

Ví dụ:

```text
PDF page
595 × 842 points

       ↓ render @ 72 DPI

595 × 842 pixels

       ↓ render @ 144 DPI

1190 × 1684 pixels

       ↓ render @ 300 DPI

2480 × 3508 pixels
```

Đây chính là nền tảng để chúng ta học phần render sau.

---

# 9. Đọc metadata

Ta có thể kiểm tra một số thông tin document:

```python
import pypdfium2 as pdfium


def main():
    pdf = pdfium.PdfDocument("sample.pdf")

    print("Pages:", len(pdf))

    print("Metadata:")
    print(pdf.get_metadata())


if __name__ == "__main__":
    main()
```

Không phải PDF nào cũng có metadata đầy đủ.

Có thể gặp:

```text
Title
Author
Subject
Keywords
Creator
Producer
CreationDate
ModDate
```

---

# 10. Đóng document

Trong các chương trình đơn giản:

```python
pdf = pdfium.PdfDocument("sample.pdf")
```

sau đó xử lý.

Nhưng khi làm production, ta phải quan tâm đến resource management.

Một pattern tốt là:

```python
pdf = pdfium.PdfDocument("sample.pdf")

try:
    ...
finally:
    pdf.close()
```

Ví dụ:

```python
import pypdfium2 as pdfium


def main():
    pdf = pdfium.PdfDocument("sample.pdf")

    try:
        print("Pages:", len(pdf))

        for index in range(len(pdf)):
            page = pdf[index]

            width, height = page.get_size()

            print(
                f"Page {index + 1}: "
                f"{width:.2f} x {height:.2f}"
            )

    finally:
        pdf.close()


if __name__ == "__main__":
    main()
```

Đây là tư duy rất quan trọng khi chúng ta đi tới:

```text
PDF
 ↓
many pages
 ↓
render
 ↓
many bitmaps
 ↓
OCR
```

vì một PDF lớn có thể tiêu tốn khá nhiều memory.

---

# 11. Kiến trúc mà chúng ta sẽ xây dựng

Không học pypdfium2 theo kiểu nhớ API rời rạc.

Chúng ta sẽ xây dần pipeline:

```text
                  pypdfium2
                      │
                      ▼
                PdfDocument
                      │
                      ▼
                   PdfPage
                      │
             ┌────────┴────────┐
             ▼                 ▼
         TextPage           Render
             │                 │
             ▼                 ▼
           Text              Bitmap
                               │
                               ▼
                          PIL Image
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                   PNG       OpenCV      OCR
```

Đến cuối khóa, chúng ta sẽ có kiến trúc kiểu:

```text
PDF Processing Engine
│
├── document/
│   ├── loader.py
│   └── document.py
│
├── rendering/
│   ├── renderer.py
│   ├── bitmap.py
│   └── options.py
│
├── extraction/
│   ├── text.py
│   ├── image.py
│   └── metadata.py
│
├── ocr/
│   └── pipeline.py
│
└── cli/
    └── main.py
```

Và áp dụng những thứ bạn đã học:

```text
SOLID
DDD
Repository
Dependency Injection
Strategy
Factory
Clean Architecture
Async / Threading
Testing
Logging
```

thay vì chỉ viết vài script PDF đơn lẻ.

---

# 12. Bài tập Buổi 1

Tạo chương trình:

```text
pdf_info.py
```

Chương trình nhận:

```bash
python pdf_info.py sample.pdf
```

và in:

```text
PDF Information
===============

File: sample.pdf
Pages: 12

Page 1
  Width: 595.28
  Height: 841.89

Page 2
  Width: 595.28
  Height: 841.89

...
```

Gợi ý cấu trúc:

```python
import sys
import pypdfium2 as pdfium


def show_pdf_info(path: str) -> None:
    ...


def main() -> None:
    ...


if __name__ == "__main__":
    main()
```

**Buổi 2** chúng ta sẽ đi sâu vào `PdfDocument`: mở PDF từ **path / bytes**, xử lý lỗi file, lifecycle/resource, truy cập page và xây một `PdfDocumentLoader` nhỏ theo hướng sạch hơn.
