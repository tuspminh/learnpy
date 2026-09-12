# Buổi 14 — Character-level Extraction

Hôm nay chúng ta đi xuống **mức ký tự**.

Roadmap:

```text
11. TextPage
12. Extract text
13. Text position / bounding box
14. Character-level extraction   ← Hôm nay
15. Link / annotation
16. Page objects
17. Images trong PDF
18. Font và text information
19. Crop / clipping
20. Mini Project: PDF Text Extractor
```

Ở Buổi 13 chúng ta có:

```text
TextFragment
    ├── text
    └── BoundingBox
```

Hôm nay sẽ đi sâu hơn:

```text
PdfTextPage
     ↓
character
     ↓
index
     ↓
unicode/text
     ↓
bounding box
     ↓
font size
```

pypdfium2/PDFium coi các ký tự trong một text page như một **character stream có index bắt đầu từ 0**. PDFium cũng cung cấp API lấy Unicode, font size và bounding box của từng character. ([GitHub][1])

---

# 1. Vì sao phải xuống mức Character?

Ở Buổi 12:

```python
text = textpage.get_text_bounded()
```

ta nhận:

```text
Xin chào các bạn
```

Nhưng nếu muốn biết:

```text
X ở đâu?
i ở đâu?
n ở đâu?
```

thì string không đủ.

Ta cần:

```text
Character
├── index
├── text
├── bbox
└── font information
```

Ví dụ:

```text
"Hello"

H → index 0 → bbox(...)
e → index 1 → bbox(...)
l → index 2 → bbox(...)
l → index 3 → bbox(...)
o → index 4 → bbox(...)
```

Đây chính là nền móng để sau này xây:

```text
Character
    ↓
Word
    ↓
Line
    ↓
Paragraph
```

---

# 2. Character index

PDFium cung cấp:

```text
CountChars
```

để lấy số character trên text page.

Ví dụ:

```python
textpage = page.get_textpage()

count = textpage.count_chars()

print(count)
```

Conceptually:

```text
textpage
    │
    ├── index 0
    ├── index 1
    ├── index 2
    ├── ...
    └── index N-1
```

Index bắt đầu từ `0`. PDFium cũng tính các ký tự được sinh ra trong quá trình text extraction, chẳng hạn newline hoặc space, vào character stream. ([GitHub][1])

---

# 3. Ví dụ

Giả sử text page:

```text
Hello World
```

Có thể hình dung:

```text
index:

0 → H
1 → e
2 → l
3 → l
4 → o
5 → space
6 → W
7 → o
8 → r
9 → l
10 → d
```

Do đó:

```python
for index in range(textpage.count_chars()):
    ...
```

là pattern quan trọng.

---

# 4. Lấy character text

Ở cấp PDFium, API tương ứng là:

```text
FPDFText_GetUnicode()
```

nó lấy Unicode của character tại index. ([GitHub][2])

pypdfium2 cung cấp các helper để làm việc với text page, còn các phần raw PDFium vẫn có thể truy cập qua `pypdfium2.raw` khi helper không bao phủ trực tiếp. README chính thức cũng lưu ý rằng pypdfium2 là binding của PDFium và raw API có thể được truy cập qua `pypdfium2.raw`. ([GitHub][3])

Điểm quan trọng ở bài hôm nay:

> **Đừng vội phụ thuộc vào raw ctypes nếu chưa cần.**

Ta sẽ xây abstraction trước.

---

# 5. Character model

Tạo:

```text
domain/character.py
```

```python
from dataclasses import dataclass

from .text import BoundingBox


@dataclass(frozen=True)
class PdfCharacter:
    index: int
    text: str
    bbox: BoundingBox
```

Ví dụ:

```python
character = PdfCharacter(
    index=0,
    text="H",
    bbox=BoundingBox(
        left=100,
        bottom=700,
        right=112,
        top=720,
    ),
)
```

Ta có:

```python
print(character.index)
print(character.text)
print(character.bbox)
```

---

# 6. Character khác TextFragment

Đây là điểm rất quan trọng.

### Character

```text
H
```

```text
index = 0
```

### Fragment

```text
Hello
```

```text
bbox = toàn bộ vùng Hello
```

Có thể hình dung:

```text
TextFragment
┌─────────────────────────┐
│ H │ e │ l │ l │ o       │
└─────────────────────────┘
```

Trong đó:

```text
Character 0 → H
Character 1 → e
Character 2 → l
Character 3 → l
Character 4 → o
```

---

# 7. Character bounding box

PDFium cung cấp:

```text
FPDFText_GetCharBox()
```

với:

```text
left
right
bottom
top
```

và tọa độ được đo trong **PDF user space**. ([GitHub][1])

Đây chính là API rất quan trọng của hôm nay.

Ví dụ:

```text
Character: H

       top
        ┌───────┐
        │   H   │
        └───────┘
      bottom
```

Ta có:

```text
left
bottom
right
top
```

---

# 8. Character box không nhất thiết bằng glyph nhìn thấy

Đây là một chi tiết quan trọng.

Bounding box của character là geometry mà PDFium cung cấp cho character.

Nó không nên được hiểu đơn giản là:

> "pixel chính xác của phần mực nhìn thấy."

Ví dụ chữ:

```text
A
```

box có thể bao gồm vùng rộng hơn phần pixel thực sự được vẽ.

Do đó:

```text
character bbox
≠
visible pixel bbox
```

Điều này đặc biệt quan trọng khi làm OCR/layout.

---

# 9. `loose=True`

Trong pypdfium2, `get_charbox()` có hỗ trợ tùy chọn `loose`. Ví dụ chính thức trong các thảo luận của dự án sử dụng:

```python
left, bottom, right, top = textpage.get_charbox(
    index,
    loose=True,
)
```

để lấy bounding box của từng character. ([GitHub][4])

Ý tưởng:

```text
strict
vs
loose
```

là một chi tiết của PDFium geometry.

Khi xây parser production, chúng ta nên **chọn rõ mode** thay vì tùy tiện trộn hai loại box.

---

# 10. Character reader

Ta xây abstraction:

```python
from collections.abc import Iterator

from .character import PdfCharacter
from .text import BoundingBox


class CharacterReader:

    def iter_characters(
        self,
        textpage,
    ) -> Iterator[PdfCharacter]:

        count = textpage.count_chars()

        for index in range(count):

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

            yield PdfCharacter(
                index=index,
                text="...",
                bbox=bbox,
            )
```

Nhưng còn một vấn đề:

```text
text="..."
```

Chúng ta phải lấy **ký tự thực tế**.

---

# 11. Lấy character text bằng `get_text_range`

pypdfium2 hỗ trợ:

```python
textpage.get_text_range(
    index=10,
    count=15,
)
```

để lấy một đoạn text bắt đầu từ character index. README chính thức có ví dụ trực tiếp cho API này. ([GitHub][3])

Với một character:

```python
character_text = textpage.get_text_range(
    index=index,
    count=1,
)
```

Tức là:

```text
index = 0
count = 1

       ↓

"H"
```

---

# 12. CharacterReader hoàn chỉnh

Ta có thể viết:

```python
from collections.abc import Iterator

from .character import PdfCharacter
from .text import BoundingBox


class CharacterReader:

    def iter_characters(
        self,
        textpage,
    ) -> Iterator[PdfCharacter]:

        count = textpage.count_chars()

        for index in range(count):

            text = textpage.get_text_range(
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

            yield PdfCharacter(
                index=index,
                text=text,
                bbox=bbox,
            )
```

Đây là một abstraction rất đẹp:

```text
PdfTextPage
      ↓
CharacterReader
      ↓
Iterator[PdfCharacter]
```

---

# 13. Vì sao dùng Generator?

Không nên:

```python
characters = []

for ...:
    characters.append(...)
```

nếu PDF rất lớn.

Thay vào đó:

```python
yield PdfCharacter(...)
```

Ta có:

```python
for character in reader.iter_characters(textpage):
    print(character)
```

Memory:

```text
PDF
 ↓
character 1
 ↓
character 2
 ↓
character 3
 ↓
...
```

thay vì:

```text
PDF
 ↓
[character1, character2, character3, ...]
```

---

# 14. Debug character extraction

Ví dụ:

```python
for character in reader.iter_characters(textpage):

    print(
        character.index,
        repr(character.text),
        character.bbox,
    )
```

Có thể nhận:

```text
0 'H' BoundingBox(...)
1 'e' BoundingBox(...)
2 'l' BoundingBox(...)
3 'l' BoundingBox(...)
4 'o' BoundingBox(...)
5 ' ' BoundingBox(...)
6 'W' BoundingBox(...)
...
```

`repr()` rất hữu ích vì ta nhìn thấy:

```text
' '
'\n'
'\t'
```

thay vì chúng bị biến mất trong output.

---

# 15. Space cũng cần chú ý

Ví dụ:

```text
Hello World
```

character stream có thể chứa:

```text
H
e
l
l
o
space
W
o
r
l
d
```

Do đó:

```python
character.text == " "
```

là trường hợp hợp lệ.

Không nên viết:

```python
if not character.text.strip():
    continue
```

ngay trong tầng extraction.

Vì:

```text
Extraction
```

phải giữ dữ liệu gốc càng nhiều càng tốt.

Việc loại space/newline thuộc:

```text
Cleaning
Normalization
Layout reconstruction
```

---

# 16. Character index rất quan trọng

Giả sử:

```text
Hello World
```

và search:

```python
searcher = textpage.search(
    "World",
    match_case=False,
)
```

pypdfium2 có thể trả về:

```text
(char_index, char_count)
```

cho match. README chính thức mô tả search result theo dạng starting character index và character count. ([GitHub][3])

Ví dụ:

```text
index = 6
count = 5
```

Ta biết:

```text
6 → W
7 → o
8 → r
9 → l
10 → d
```

---

# 17. Từ search → character boxes

Đây là một use case cực kỳ mạnh.

```python
searcher = textpage.search(
    "World",
    match_case=False,
)

match = searcher.get_next()

if match is not None:

    start, count = match

    for i in range(count):

        index = start + i

        box = textpage.get_charbox(
            index,
            loose=True,
        )

        print(
            index,
            box,
        )
```

Pipeline:

```text
Search "World"
       ↓
start index
       ↓
character indexes
       ↓
get_charbox()
       ↓
bounding boxes
```

Đây chính là cách xây tính năng:

```text
Find text
   ↓
Highlight text trên PDF
```

pypdfium2 cũng có ví dụ/thảo luận chính thức về việc dùng search result index rồi gọi `get_charbox()` cho từng character. ([GitHub][4])

---

# 18. Tạo `TextMatch`

Ta có thể tạo domain model:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TextMatch:
    text: str
    start_index: int
    count: int
```

Ví dụ:

```python
match = TextMatch(
    text="World",
    start_index=6,
    count=5,
)
```

Sau đó:

```text
TextMatch
     │
     ├── character 6
     ├── character 7
     ├── character 8
     ├── character 9
     └── character 10
```

---

# 19. Một match có thể có nhiều rectangle

Đây là điểm rất quan trọng.

Giả sử text:

```text
Đây là một đoạn văn rất dài...
```

nằm trên **hai dòng**:

```text
Đây là một đoạn văn rất
dài và tiếp tục ở đây
```

Một text range:

```text
"Đây là một đoạn văn rất dài và tiếp tục ở đây"
```

không nhất thiết tương ứng với **một rectangle duy nhất**.

PDFium có:

```text
FPDFText_CountRects()
FPDFText_GetRect()
```

để lấy các rectangular areas của một text segment; PDFium mô tả rằng các character boxes có thể được tự động merge thành các rectangle lớn hơn khi các ký tự nằm cùng dòng và có cùng font settings. ([GitHub][1])

Đây là khác biệt:

```text
Character-level:
H → box
e → box
l → box

Range-level:
Hello → rectangle(s)
```

---

# 20. Character → Word

Bây giờ ta đã có:

```text
H
e
l
l
o
space
W
o
r
l
d
```

Ta có thể group:

```text
H e l l o
    ↓
"Hello"
```

Gặp:

```text
" "
```

thì kết thúc word.

Pseudo:

```python
current_word = []

for character in characters:

    if character.text.isspace():
        emit(current_word)
        current_word = []
    else:
        current_word.append(character)

emit(current_word)
```

Nhưng **chưa nên xây WordParser hôm nay**.

Đây là bước tiếp theo của tư duy layout.

---

# 21. Character → Line

Có thể dựa vào BBox:

```text
Character A
top = 700

Character B
top = 701

Character C
top = 700
```

với tolerance:

```python
abs(top_a - top_b) <= 2
```

thì coi là cùng dòng.

Ví dụ:

```text
H e l l o
─────────
W o r l d
─────────
```

Character geometry cho phép chúng ta xây line reconstruction.

---

# 22. Character → Paragraph

Tiếp tục:

```text
Line 1
Line 2
Line 3

      ↓

Paragraph
```

Ví dụ:

```text
Line 1 y=700
Line 2 y=680
Line 3 y=660
```

Nếu khoảng cách:

```text
20
20
```

có thể là cùng paragraph.

Nhưng:

```text
Line 4 y=600
```

có khoảng cách lớn hơn:

```text
60
```

có thể bắt đầu paragraph mới.

Đây là heuristic, không phải quy luật PDF.

---

# 23. Một kiến trúc tốt

Sau Buổi 14:

```text
                     PdfPage
                        │
                        ▼
                  PdfTextPage
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
    TextReader                 CharacterReader
          │                           │
          ▼                           ▼
        str                    PdfCharacter
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                       text                      bbox
                                                   │
                                                   ▼
                                            BoundingBox
```

Đây là kiến trúc khá phù hợp với project PDF processor của chúng ta.

---

# 24. Không nên để Domain biết pypdfium2

Ví dụ **không nên**:

```python
from pypdfium2 import PdfTextPage
```

trong:

```text
domain/
```

Domain chỉ biết:

```python
@dataclass(frozen=True)
class PdfCharacter:
    index: int
    text: str
    bbox: BoundingBox
```

Infrastructure mới biết:

```python
import pypdfium2
```

Kiến trúc:

```text
Domain
  ↑
Application
  ↑
Infrastructure
  │
  └── pypdfium2
```

Điều này tiếp tục đúng với những gì chúng ta đã học về Clean Architecture/DDD.

---

# 25. CharacterReader interface

Nếu muốn abstraction sạch hơn:

```python
from collections.abc import Iterator
from typing import Protocol

from domain.character import PdfCharacter


class CharacterReader(Protocol):

    def iter_characters(
        self,
        textpage,
    ) -> Iterator[PdfCharacter]:
        ...
```

Infrastructure:

```python
class PdfiumCharacterReader:

    def iter_characters(
        self,
        textpage,
    ):
        ...
```

Sau này test:

```text
Application
     ↓
FakeCharacterReader
```

không cần PDF thật.

---

# 26. Test bằng Fake TextPage

Ví dụ:

```python
class FakeTextPage:

    def count_chars(self):
        return 3

    def get_text_range(self, index, count):
        chars = ["A", "B", "C"]
        return chars[index]

    def get_charbox(self, index, loose=True):
        return (
            index * 10,
            100,
            index * 10 + 8,
            120,
        )
```

Test:

```python
reader = CharacterReader()

characters = list(
    reader.iter_characters(
        FakeTextPage()
    )
)
```

Kiểm tra:

```python
assert len(characters) == 3

assert characters[0].text == "A"
assert characters[1].text == "B"
assert characters[2].text == "C"
```

---

# 27. Test geometry

```python
first = characters[0]

assert first.bbox.left == 0
assert first.bbox.bottom == 100
assert first.bbox.right == 8
assert first.bbox.top == 120
```

Như vậy ta test được:

```text
CharacterReader
```

mà không cần:

```text
PDF file
PDFium
PIL
```

Đây là một ví dụ rất tốt của Dependency Inversion.

---

# 28. Một vấn đề thực tế: Unicode

Đặc biệt với tiếng Việt:

```text
Xin chào Việt Nam
```

có:

```text
X
i
n
space
c
h
à
o
...
```

Nhưng Unicode trong PDF có thể phức tạp hơn ASCII.

Ví dụ:

```text
ế
```

về mặt Unicode có thể được biểu diễn bằng:

```text
U+1EBF
```

hoặc trong một số ngữ cảnh Unicode có thể sử dụng ký tự + combining mark.

Do đó:

```text
Python string character
```

và:

```text
PDFium character index
```

không nên mặc định coi là hai khái niệm hoàn toàn giống nhau.

Đây là một lý do rất tốt để giữ:

```python
PdfCharacter.index
```

riêng biệt với:

```python
PdfCharacter.text
```

---

# 29. Một cảnh báo quan trọng về `get_text_range()`

Có những PDF có encoding/character mapping phức tạp. Dự án pypdfium2 từng ghi nhận trường hợp index từ `get_text_range()` có thể có hành vi không nhất quán trên một số tài liệu/PDFium situations. ([GitHub][5])

Vì vậy:

**Không nên xây production parser với giả định tuyệt đối rằng:**

```text
Python string index
==
PDFium character index
```

Hãy coi:

```text
PDFium character index
```

là một **index riêng của text page**.

---

# 30. Bài tập thực hành

## Bài 1 — Character model

Tạo:

```python
@dataclass(frozen=True)
class PdfCharacter:
    index: int
    text: str
    bbox: BoundingBox
```

---

## Bài 2 — Character reader

Viết:

```python
class CharacterReader:

    def iter_characters(
        self,
        textpage,
    ):
        ...
```

Yêu cầu:

```text
count_chars()
      ↓
range(count)
      ↓
get_text_range(index, 1)
      ↓
get_charbox(index)
      ↓
PdfCharacter
      ↓
yield
```

---

## Bài 3 — Debug

In:

```text
index | char | left | bottom | right | top
```

Ví dụ:

```text
0 | 'H' | 100 | 700 | 112 | 720
1 | 'e' | 112 | 700 | 124 | 720
2 | 'l' | 124 | 700 | 130 | 720
```

---

## Bài 4 ⭐ — Search + BBox

Tìm:

```text
"Python"
```

sau đó:

```text
search
 ↓
start index
 ↓
count
 ↓
get_charbox()
 ↓
tất cả character boxes
```

---

## Bài 5 ⭐⭐ — Highlight

Render trang PDF thành PIL:

```text
PDF
 ↓
PIL.Image
```

Tìm:

```text
"Python"
```

lấy character boxes rồi chuyển:

```text
PDF coordinates
        ↓
Image coordinates
```

và:

```python
draw.rectangle(...)
```

để highlight từng character.

---

# 31. Kiến thức cốt lõi của Buổi 14

Bạn cần nhớ 6 thứ:

```text
1. count_chars()
```

→ có bao nhiêu character trong text page.

```text
2. character index
```

→ index bắt đầu từ 0.

```text
3. get_text_range(index, 1)
```

→ lấy text của một character/range.

```text
4. get_charbox(index)
```

→ lấy bounding box của character.

```text
5. character index ≠ Python string index
```

→ không nên đánh đồng hai hệ index.

```text
6. Character geometry
```

→ nền tảng để xây Word / Line / Paragraph / Layout.

---

## Toàn bộ pipeline chúng ta đã xây tới đây

```text
                    PDF
                     │
                     ▼
                 PdfDocument
                     │
                     ▼
                   PdfPage
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      Renderer              TextPage
          │                     │
          ▼              ┌──────┴──────┐
       Bitmap             │             │
          │               ▼             ▼
          ▼             Text        Characters
      PIL.Image                       │
                                      │
                              ┌───────┴────────┐
                              ▼                ▼
                           text              bbox
```

Và roadmap tiếp theo rất tự nhiên:

```text
Buổi 13
Text + BBox
      ↓
Buổi 14
Character + BBox
      ↓
Buổi 15
Link / Annotation
      ↓
Buổi 16
Page Objects
      ↓
Buổi 17
Images
      ↓
Buổi 18
Font + Text Information
```

**Buổi 15 sẽ chuyển từ text sang các đối tượng tương tác của PDF: Link và Annotation** — ví dụ phát hiện URL, vùng click, link trong trang, và cách phân biệt chúng với text thông thường.

[1]: https://github.com/PDFium/PDFium/blob/master/fpdfsdk/include/fpdftext.h?utm_source=chatgpt.com "PDFium/fpdfsdk/include/fpdftext.h at master · PDFium/PDFium · GitHub"
[2]: https://github.com/documentcloud/pdfium/blob/master/fpdfsdk/fpdftext.cpp?utm_source=chatgpt.com "pdfium/fpdfsdk/fpdftext.cpp at master · documentcloud/pdfium · GitHub"
[3]: https://github.com/pypdfium2-team/pypdfium2/blob/main/README.md?utm_source=chatgpt.com "pypdfium2/README.md at main · pypdfium2-team/pypdfium2 · GitHub"
[4]: https://github.com/pypdfium2-team/pypdfium2/discussions/284?utm_source=chatgpt.com "Coordinate conversion help · pypdfium2-team pypdfium2 · Discussion #284 · GitHub"
[5]: https://github.com/pypdfium2-team/pypdfium2/issues/261?utm_source=chatgpt.com "Inconsistent textpage.get_text_range results · Issue #261 · pypdfium2-team/pypdfium2 · GitHub"
