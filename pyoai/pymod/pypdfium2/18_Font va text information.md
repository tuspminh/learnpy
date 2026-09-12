# Buổi 18 — Font và Text Information

Hôm nay chúng ta tiếp tục từ **Buổi 14 — Character-level extraction**, nhưng đi sâu hơn vào câu hỏi:

> **Một ký tự trong PDF được hiển thị bằng font nào, cỡ bao nhiêu, và làm sao dùng thông tin đó để phân tích layout?**

Đây là bước rất quan trọng nếu sau này bạn muốn xây:

```text
PDF
 ↓
Text Parser
 ↓
Heading / Paragraph / Chapter title
 ↓
Structured Document
```

---

# 1. Mục tiêu Buổi 18

Sau bài này bạn sẽ biết:

```text
1. Character trong PDF có font information
2. Lấy font size
3. Lấy character box
4. Hiểu font size ≠ chiều cao bbox
5. Phân tích heading bằng font size
6. Gom character → word
7. Gom word → line
8. Phát hiện heading
9. Thiết kế FontInfo domain model
10. Xây TextLayoutAnalyzer
```

---

# 2. Ôn lại kiến trúc TextPage

Chúng ta đã có:

```text
PdfPage
   │
   └── PdfTextPage
          │
          ├── character 0
          ├── character 1
          ├── character 2
          ├── ...
          └── character N
```

Ở Buổi 14:

```python
count = textpage.count_chars()

for index in range(count):
    char = textpage.get_text_range(
        index=index,
        count=1,
    )

    bbox = textpage.get_charbox(
        index,
        loose=True,
    )
```

Hôm nay thêm:

```text
font size
font information
```

---

# 3. Font size của character

PDFium cung cấp API:

```text
FPDFText_GetFontSize()
```

để lấy kích thước font của character. Đây là API ở tầng PDFium; pypdfium2 expose các API text tương ứng qua helper/raw layer tùy phiên bản.

Về mặt khái niệm:

```text
character
    │
    ├── Unicode
    ├── bbox
    ├── font size
    └── font information
```

Ví dụ:

```text
H
font size = 24

e
font size = 24

l
font size = 24

l
font size = 24

o
font size = 24
```

---

# 4. Font size không phải pixel height

Đây là lỗi rất dễ mắc.

Giả sử:

```text
font-size = 24 pt
```

Không có nghĩa:

```text
bbox.height == 24
```

Bởi vì font có:

```text
ascender
descender
baseline
line gap
```

Ví dụ:

```text
          H
          │
          │ ascender
──────────┼────────── baseline
          │
          │ descender
          g
```

Do đó:

```text
font size
```

và:

```text
character bbox height
```

là hai đại lượng khác nhau.

---

# 5. Lấy font size

Ở tầng helper, tùy version pypdfium2, bạn có thể kiểm tra API thực tế của `PdfTextPage`:

```python
print(dir(textpage))
```

Với raw PDFium API, ý tưởng là:

```text
FPDFText_GetFontSize(text_page, index)
```

Nếu bạn đang xây adapter production, nên kiểm tra version pypdfium2 đang cài thay vì hard-code giả định về helper method.

---

# 6. Reflection — kỹ thuật nên dùng

Tạo chương trình:

```python
import pypdfium2 as pdfium


pdf = pdfium.PdfDocument("sample.pdf")

try:
    page = pdf[0]
    textpage = page.get_textpage()

    print(type(textpage))

    for name in dir(textpage):
        if not name.startswith("_"):
            print(name)

finally:
    pdf.close()
```

Chạy:

```bash
python inspect_textpage.py
```

Mục đích không phải để dùng `dir()` trong production.

Mục đích là:

```text
học API
↓
xác định helper API của version hiện tại
↓
viết adapter
```

---

# 7. Raw API

Nếu helper API không cung cấp method bạn cần, có thể xuống:

```python
import pypdfium2.raw as pdfium_c
```

Ví dụ API PDFium:

```text
FPDFText_GetFontSize
FPDFText_GetCharBox
FPDFText_GetUnicode
FPDFText_CountChars
```

pypdfium2 cho phép sử dụng raw PDFium API trực tiếp bên cạnh helper API.

Nhưng nguyên tắc architecture của chúng ta vẫn giữ nguyên:

```text
Application
    ↓
TextReader
    ↓
PdfiumTextReader
    ↓
pypdfium2
    ↓
PDFium
```

Không để:

```text
Domain
   ↓
pypdfium2.raw
```

---

# 8. Tạo FontInfo

Bây giờ bắt đầu mở rộng domain.

Tạo:

```text
domain/font.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FontInfo:
    size: float | None = None
    family: str | None = None
    weight: str | None = None
    italic: bool = False
```

Ở Buổi 18 chúng ta chưa cần cố gắng lấy tất cả thông tin font từ mọi PDF.

Trước tiên xây model.

---

# 9. PdfCharacter hoàn chỉnh hơn

Trước đây:

```python
@dataclass(frozen=True)
class PdfCharacter:
    index: int
    char: str
    bbox: BoundingBox
```

Bây giờ mở rộng:

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
```

Ví dụ:

```python
character = PdfCharacter(
    index=10,
    char="A",
    bbox=BoundingBox(
        left=100,
        bottom=700,
        right=115,
        top=720,
    ),
    font=FontInfo(
        size=20,
    ),
)
```

---

# 10. Vì sao nên gắn FontInfo vào Character?

Bởi vì trong một đoạn text:

```text
Normal text
```

có thể xuất hiện:

```text
Normal **bold** text
```

hoặc:

```text
Chapter 1
```

có:

```text
Chapter → 24 pt
1       → 24 pt
```

trong khi paragraph:

```text
This is the content...
```

có:

```text
12 pt
```

Nếu chúng ta chỉ lấy:

```python
textpage.get_text_bounded()
```

thì mất rất nhiều thông tin layout.

---

# 11. Character extraction service

Ta xây abstraction:

```python
from typing import Protocol

from domain.text import PdfCharacter


class CharacterReader(Protocol):

    def read_characters(self, textpage) -> list[PdfCharacter]:
        ...
```

Implementation:

```python
class PdfiumCharacterReader:

    def read_characters(self, textpage):

        characters = []

        count = textpage.count_chars()

        for index in range(count):

            char = textpage.get_text_range(
                index=index,
                count=1,
            )

            left, bottom, right, top = (
                textpage.get_charbox(
                    index,
                    loose=True,
                )
            )

            bbox = BoundingBox(
                left=left,
                bottom=bottom,
                right=right,
                top=top,
            )

            font_size = self.get_font_size(
                textpage,
                index,
            )

            character = PdfCharacter(
                index=index,
                char=char,
                bbox=bbox,
                font=FontInfo(
                    size=font_size,
                ),
            )

            characters.append(character)

        return characters
```

Phần:

```python
self.get_font_size(...)
```

sẽ là adapter-specific implementation dựa trên helper/raw API của version pypdfium2 hiện tại.

---

# 12. Tại sao không nhét raw API vào model?

Không làm:

```python
@dataclass
class PdfCharacter:

    textpage: pdfium.PdfTextPage
    ...
```

hoặc:

```python
import pypdfium2.raw
```

trong domain.

Bởi vì khi đó:

```text
Domain
```

bị khóa vào:

```text
PDFium
```

Sau này nếu muốn:

```text
pypdf
PyMuPDF
PDFium
OCR
```

thì domain model không tái sử dụng được.

---

# 13. Font size dùng để làm gì?

Một ứng dụng rất thực tế:

## Detect heading

Ví dụ PDF:

```text
Chapter 1
12 pt

The beginning...
10 pt

The story continues...
10 pt
```

Ta có:

```text
font size distribution

10 pt → 95%
12 pt → 4%
18 pt → 1%
```

Có thể suy luận:

```text
18 pt → heading lớn
12 pt → subheading
10 pt → body
```

---

# 14. Font-size statistics

Tạo:

```python
from collections import Counter


def font_size_distribution(
    characters: list[PdfCharacter],
) -> Counter:
    counter = Counter()

    for character in characters:
        size = character.font.size

        if size is not None:
            rounded = round(size, 1)
            counter[rounded] += 1

    return counter
```

Ví dụ:

```python
distribution = font_size_distribution(characters)

for size, count in distribution.most_common():
    print(size, count)
```

Kết quả:

```text
10.0  1420
12.0  180
18.0  32
24.0  8
```

---

# 15. Nhưng không được kết luận heading chỉ bằng font size

Ví dụ:

```text
10 pt
```

có thể là:

```text
body
footer
caption
table
```

Và:

```text
18 pt
```

có thể là:

```text
heading
logo
watermark
```

Do đó heading detection cần kết hợp:

```text
font size
+
position
+
bold
+
line length
+
whitespace
+
alignment
```

Đây chính là lý do chúng ta đang học từng phần.

---

# 16. Character → Word

Bây giờ bắt đầu xây text layout engine.

Ví dụ:

```text
Hello world
```

Characters:

```text
H e l l o _ w o r l d
```

Ta cần gom:

```text
Hello
world
```

Một heuristic đơn giản:

```text
space
```

là delimiter.

---

# 17. Word model

```python
from dataclasses import dataclass

from .geometry import BoundingBox
from .font import FontInfo


@dataclass(frozen=True)
class PdfWord:
    text: str
    bbox: BoundingBox
    font: FontInfo
```

---

# 18. Gom character thành word

```python
def characters_to_words(
    characters: list[PdfCharacter],
) -> list[PdfWord]:

    words = []

    current_chars = []

    for character in characters:

        if character.char.isspace():

            if current_chars:
                words.append(
                    build_word(current_chars)
                )

                current_chars = []

        else:
            current_chars.append(character)

    if current_chars:
        words.append(
            build_word(current_chars)
        )

    return words
```

---

# 19. Build word

Ta cần bounding box bao toàn bộ character.

```python
def build_word(
    characters: list[PdfCharacter],
) -> PdfWord:

    text = "".join(
        character.char
        for character in characters
    )

    left = min(
        character.bbox.left
        for character in characters
    )

    bottom = min(
        character.bbox.bottom
        for character in characters
    )

    right = max(
        character.bbox.right
        for character in characters
    )

    top = max(
        character.bbox.top
        for character in characters
    )

    bbox = BoundingBox(
        left=left,
        bottom=bottom,
        right=right,
        top=top,
    )

    font = characters[0].font

    return PdfWord(
        text=text,
        bbox=bbox,
        font=font,
    )
```

---

# 20. Nhưng có một vấn đề

Không phải PDF nào cũng có:

```text
space character
```

Ví dụ PDF có thể encode:

```text
Hello
world
```

thành những character riêng biệt nhưng khoảng cách giữa chúng thể hiện bằng **tọa độ**, không phải space.

Do đó:

```python
character.char.isspace()
```

không đủ tốt cho một layout engine production.

Ta cần sử dụng:

```text
horizontal gap
```

---

# 21. Word segmentation bằng khoảng cách

Giả sử:

```text
Hello
```

có:

```text
H x=100
e x=112
l x=124
l x=130
o x=136
```

sau đó:

```text
world
```

bắt đầu:

```text
x=160
```

Ta có:

```text
gap = 160 - 148
    = 12
```

Nếu gap lớn hơn threshold:

```text
→ word boundary
```

---

# 22. Công thức

Hai character:

```text
A
B
```

với:

```text
A.right
B.left
```

Ta có:

```python
gap = B.bbox.left - A.bbox.right
```

Nếu:

```python
gap > threshold
```

thì:

```text
A và B thuộc hai word khác nhau
```

---

# 23. Threshold không nên cố định

Không nên:

```python
if gap > 5:
```

vì:

```text
5 PDF units
```

có thể lớn hoặc nhỏ tùy font.

Tốt hơn:

```python
threshold = average_char_width * 0.5
```

hoặc dựa trên font size:

```python
threshold = font_size * 0.25
```

Đây là heuristic, không phải quy luật PDF.

---

# 24. Character → Line

Sau word:

```text
Word
Word
Word
```

chúng ta cần:

```text
Line
```

Ví dụ:

```text
Hello world from PDF
```

các word có bbox:

```text
Hello   y=700
world   y=700
from    y=700
PDF     y=700
```

Ta gom các word có baseline/vertical center gần nhau.

---

# 25. Line model

```python
@dataclass(frozen=True)
class PdfLine:
    text: str
    bbox: BoundingBox
    font: FontInfo
```

Ví dụ:

```text
PdfLine(
    text="Hello world",
    bbox=(100, 700, 300, 720),
    font=FontInfo(size=12),
)
```

---

# 26. Vertical grouping

Hai word:

```text
word A
center_y = 710

word B
center_y = 711
```

→ cùng line.

Nếu:

```text
word C
center_y = 690
```

→ có khả năng là line khác.

Có thể dùng:

```python
abs(center_y_a - center_y_b) <= tolerance
```

---

# 27. Font size + line

Bây giờ ta có:

```text
PdfCharacter
      ↓
PdfWord
      ↓
PdfLine
```

và mỗi cấp có:

```text
text
bbox
font
```

Đây là nền móng của:

```text
PDF Layout Engine
```

---

# 28. Detect heading

Ví dụ:

```text
Chapter 1
```

line:

```text
font.size = 20
```

body:

```text
font.size = 10
```

Ta có thể tạo:

```python
def classify_line(
    line: PdfLine,
    body_font_size: float,
) -> str:

    if line.font.size is None:
        return "unknown"

    if line.font.size >= body_font_size * 1.5:
        return "heading"

    return "body"
```

---

# 29. Nhưng hãy cải thiện

Một heading thường có:

```text
font size lớn
+
ngắn
+
được đặt riêng
```

Ví dụ:

```text
CHAPTER ONE
```

có:

```text
font = 20
length = 11
```

Trong khi:

```text
This is a very long paragraph...
```

có:

```text
font = 10
length = 500
```

Có thể tạo scoring:

```python
def heading_score(
    line: PdfLine,
    body_font_size: float,
) -> float:

    score = 0.0

    size = line.font.size

    if size is not None:

        ratio = size / body_font_size

        if ratio >= 1.5:
            score += 0.6

        elif ratio >= 1.2:
            score += 0.3

    if len(line.text) < 100:
        score += 0.2

    return min(score, 1.0)
```

Ví dụ:

```text
score >= 0.7
→ likely heading
```

Đây sẽ rất hữu ích khi sau này chúng ta xây **PDF document structure parser**.

---

# 30. Một ví dụ hoàn chỉnh

Giả sử domain:

```text
domain/
├── geometry.py
├── font.py
├── text.py
└── layout.py
```

### `font.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FontInfo:
    size: float | None = None
    family: str | None = None
    weight: str | None = None
    italic: bool = False
```

### `text.py`

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
```

---

# 31. Layout Analyzer

```python
class TextLayoutAnalyzer:

    def analyze_characters(
        self,
        characters: list[PdfCharacter],
    ) -> dict:

        return {
            "character_count": len(characters),
            "font_sizes": self._font_sizes(
                characters
            ),
        }

    def _font_sizes(
        self,
        characters: list[PdfCharacter],
    ) -> dict[float, int]:

        result: dict[float, int] = {}

        for character in characters:

            size = character.font.size

            if size is None:
                continue

            size = round(size, 1)

            result[size] = (
                result.get(size, 0) + 1
            )

        return result
```

Sử dụng:

```python
analyzer = TextLayoutAnalyzer()

result = analyzer.analyze_characters(
    characters
)

print(result)
```

Ví dụ:

```text
{
    "character_count": 1638,
    "font_sizes": {
        10.0: 1420,
        12.0: 180,
        18.0: 32,
        24.0: 6
    }
}
```

---

# 32. Ứng dụng rất thực tế cho app truyện

Điều này đặc biệt hữu ích với mục tiêu PDF parser của chúng ta.

Ví dụ một ebook PDF:

```text
CHƯƠNG 123
```

có:

```text
font size = 20
```

Trong khi:

```text
Nội dung chương...
```

có:

```text
font size = 11
```

Ta có thể xây:

```text
PDF
 ↓
TextPage
 ↓
Character
 ↓
Word
 ↓
Line
 ↓
Font analysis
 ↓
Heading detection
 ↓
Chapter detection
```

Sau đó output:

```python
Chapter(
    title="CHƯƠNG 123",
    content="Nội dung chương..."
)
```

Đây là cầu nối rất đẹp giữa **pypdfium2** và hệ thống đọc/crawl truyện mà bạn đang xây.

---

# 33. Test

Domain test:

```python
from domain.font import FontInfo


def test_font_info():

    font = FontInfo(
        size=12,
        family="Arial",
        weight="normal",
    )

    assert font.size == 12
    assert font.family == "Arial"
    assert font.weight == "normal"
    assert font.italic is False
```

Character test:

```python
def test_character_font():

    character = PdfCharacter(
        index=0,
        char="A",
        bbox=BoundingBox(
            left=10,
            bottom=10,
            right=20,
            top=30,
        ),
        font=FontInfo(size=18),
    )

    assert character.char == "A"
    assert character.font.size == 18
```

---

# 34. Test heading detection

```python
def test_heading_detection():

    line = PdfLine(
        text="Chapter 1",
        bbox=BoundingBox(
            left=100,
            bottom=700,
            right=250,
            top=730,
        ),
        font=FontInfo(size=20),
    )

    score = heading_score(
        line,
        body_font_size=10,
    )

    assert score >= 0.7
```

---

# 35. Architecture sau Buổi 18

Bây giờ hệ thống ngày càng rõ:

```text
                    PdfPage
                       │
                       ▼
                  PdfTextPage
                       │
                       ▼
                CharacterReader
                       │
                       ▼
                 PdfCharacter
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          PdfWord             FontInfo
             │
             ▼
          PdfLine
             │
             ▼
       Layout Analyzer
             │
             ▼
       Heading Detection
```

Infrastructure:

```text
pypdfium2
     │
     ▼
PdfiumCharacterReader
     │
     ▼
Domain
```

---

# 36. Một cảnh báo quan trọng

Đừng xây parser kiểu:

```python
if font_size > 15:
    heading = True
```

rồi coi đó là parser hoàn chỉnh.

PDF rất phức tạp.

Một trang có thể có:

```text
Logo       30 pt
Heading    18 pt
Body       11 pt
Footer      8 pt
Watermark  40 pt
```

Vì vậy production parser cần kết hợp:

```text
Font
+
BoundingBox
+
Position
+
Spacing
+
Text length
+
Alignment
+
Object information
+
Reading order
```

Các bài tiếp theo sẽ giúp chúng ta từng bước xây những thành phần đó.

---

# 37. Bài tập Buổi 18

### Bài 1 — Font statistics

Viết:

```python
get_font_statistics(pdf_path)
```

output:

```text
Font size:
    10.0 → 1520 chars
    12.0 → 320 chars
    18.0 → 45 chars
```

---

### Bài 2 — Character information

In:

```text
index
character
font size
left
bottom
right
top
```

Ví dụ:

```text
0    C    20    100    700    112    720
1    H    20    113    700    126    720
2    A    20    127    700    140    720
```

---

### Bài 3 — Word builder

Xây:

```python
characters_to_words()
```

input:

```text
PdfCharacter[]
```

output:

```text
PdfWord[]
```

---

### Bài 4 — Line builder

Xây:

```python
words_to_lines()
```

dựa trên:

```text
vertical position
```

---

### Bài 5 — Heading detector

Xây:

```python
detect_headings()
```

sử dụng:

```text
font size
line length
position
```

---

# 38. Tổng kết

Buổi 18 chúng ta đã nâng mô hình từ:

```text
Text
```

thành:

```text
Character
   │
   ├── Unicode
   ├── BoundingBox
   └── FontInfo
```

Sau đó:

```text
Character
    ↓
Word
    ↓
Line
```

và:

```text
Font size
    ↓
Layout analysis
    ↓
Heading detection
```

Đây là nền tảng quan trọng để sau này biến PDF từ:

```text
một đống text
```

thành:

```text
Document
├── Title
├── Heading
├── Paragraph
├── Image
├── Link
└── ...
```

**Tiếp theo đúng roadmap:**

> **Buổi 19 — Crop / Clipping**

Chúng ta sẽ học cách giới hạn vùng PDF cần xử lý, liên hệ trực tiếp với `get_text_bounded()`, image/object bounding box và render một **vùng cụ thể của trang** thay vì toàn bộ page.
