# Buổi 12 — Regex Flags

Hôm nay chúng ta học **Flags** trong Python `re`.

Flags cho phép thay đổi **cách Regex hoạt động** mà không cần thay đổi pattern.

Các flag quan trọng:

```python
re.IGNORECASE
re.MULTILINE
re.DOTALL
re.VERBOSE
re.ASCII
```

Đặc biệt, 3 flag bạn cần nắm thật chắc là:

```text
IGNORECASE
MULTILINE
DOTALL
```

vì chúng xuất hiện rất nhiều trong parser, crawler và text processing.

---

# 1. Flag là gì?

Ví dụ:

```python
import re

pattern = re.compile(
    r"python",
    re.IGNORECASE,
)
```

Pattern vẫn là:

```regex
python
```

nhưng:

```python
re.IGNORECASE
```

nói với Regex engine:

> Không phân biệt chữ hoa/chữ thường.

---

# 2. `re.IGNORECASE`

Có alias:

```python
re.I
```

Hai cách tương đương:

```python
re.IGNORECASE
```

và:

```python
re.I
```

Tôi khuyên khi học và viết code production nên ưu tiên:

```python
re.IGNORECASE
```

vì dễ đọc.

---

# 3. Không có `IGNORECASE`

```python
import re

pattern = re.compile(r"python")

print(pattern.findall(
    "Python python PYTHON"
))
```

Kết quả:

```python
['python']
```

Chỉ:

```text
python
```

match.

---

# 4. Có `IGNORECASE`

```python
pattern = re.compile(
    r"python",
    re.IGNORECASE,
)

print(pattern.findall(
    "Python python PYTHON"
))
```

Kết quả:

```python
[
    "Python",
    "python",
    "PYTHON",
]
```

---

# 5. `IGNORECASE` rất hữu ích với parser

Ví dụ website có thể viết:

```text
Chapter 001
chapter 002
CHAPTER 003
ChApTeR 004
```

Không nên viết:

```python
re.search(
    r"Chapter\s+\d+",
    text,
)
```

nếu format không nhất quán.

Có thể:

```python
CHAPTER_PATTERN = re.compile(
    r"Chapter\s+(?P<number>\d+)",
    re.IGNORECASE,
)
```

Sau đó:

```python
match = CHAPTER_PATTERN.search(text)
```

Tất cả các dạng chữ hoa/thường đều được xử lý.

---

# 6. `re.MULTILINE`

Đây là flag cực kỳ quan trọng.

Alias:

```python
re.M
```

Nó thay đổi ý nghĩa của:

```regex
^
$
```

khi string có nhiều dòng.

---

# 7. Không có `MULTILINE`

Ví dụ:

```python
import re

text = """Python
Regex
Asyncio
"""

result = re.findall(
    r"^.+$",
    text,
)

print(result)
```

Không nên suy nghĩ đơn giản rằng `^` và `$` tự động hoạt động trên từng dòng.

Mặc định:

```text
^
```

→ đầu toàn bộ string.

```text
$
```

→ cuối toàn bộ string.

---

# 8. Có `MULTILINE`

```python
result = re.findall(
    r"^.+$",
    text,
    re.MULTILINE,
)

print(result)
```

Kết quả:

```python
[
    "Python",
    "Regex",
    "Asyncio",
]
```

Bây giờ:

```text
^
```

có thể match đầu **mỗi dòng**.

và:

```text
$
```

có thể match cuối **mỗi dòng**.

---

# 9. Đây là điểm cần nhớ

Không có `MULTILINE`:

```text
^ → đầu string
$ → cuối string
```

Có `MULTILINE`:

```text
^ → đầu string hoặc đầu dòng
$ → cuối string hoặc cuối dòng
```

Nó **không làm `.` match newline**.

Đây là một hiểu nhầm rất phổ biến.

---

# 10. Ví dụ lọc comment

Input:

```python
text = """Python
# comment 1
Regex
# comment 2
Asyncio
"""
```

Ta muốn tìm các dòng comment.

```python
pattern = re.compile(
    r"^#.*$",
    re.MULTILINE,
)

comments = pattern.findall(text)

print(comments)
```

Kết quả:

```python
[
    "# comment 1",
    "# comment 2",
]
```

---

# 11. Xóa comment bằng `sub()`

Kết hợp kiến thức Buổi 10:

```python
pattern = re.compile(
    r"^#.*$",
    re.MULTILINE,
)

cleaned = pattern.sub(
    "",
    text,
)
```

Ta vừa dùng:

```text
compile
+
MULTILINE
+
sub
```

Đây là một pattern thực tế.

---

# 12. `MULTILINE` không phải multi-line matching theo nghĩa `.`

Ví dụ:

```python
text = """Python
Regex
Asyncio"""
```

Pattern:

```regex
^Python.*Asyncio$
```

Có:

```python
re.MULTILINE
```

**vẫn không** match toàn bộ 3 dòng.

Tại sao?

Vì:

```regex
.
```

mặc định không match:

```text
\n
```

Muốn `.` đi qua newline, cần:

```python
re.DOTALL
```

---

# 13. `re.DOTALL`

Alias:

```python
re.S
```

Đây là flag thay đổi:

```regex
.
```

Mặc định:

```regex
.
```

match gần như mọi ký tự **trừ newline**.

Với:

```python
re.DOTALL
```

`.` cũng match newline.

---

# 14. Ví dụ

```python
import re

text = """Hello
Python
Regex"""
```

Pattern:

```python
pattern = re.compile(
    r"Hello.*Regex"
)
```

Không có `DOTALL`:

```python
print(
    pattern.search(text)
)
```

→ `None`.

Vì:

```text
.
```

không đi qua `\n`.

---

# 15. Thêm `DOTALL`

```python
pattern = re.compile(
    r"Hello.*Regex",
    re.DOTALL,
)

match = pattern.search(text)

print(match.group())
```

Kết quả:

```text
Hello
Python
Regex
```

---

# 16. `DOTALL` cực kỳ hữu ích với block text

Ví dụ:

```text
START
Python
Regex
Asyncio
END
```

Ta có:

```python
pattern = re.compile(
    r"START.*END",
    re.DOTALL,
)
```

Sau đó:

```python
match = pattern.search(text)
```

→ lấy được toàn bộ block.

---

# 17. Nhưng `DOTALL` có thể nguy hiểm

Pattern:

```python
r"<div>.*</div>"
```

với:

```python
re.DOTALL
```

có thể match **quá nhiều**.

Ví dụ:

```html
<div>A</div>
<div>B</div>
<div>C</div>
```

Pattern:

```regex
<div>.*</div>
```

có thể lấy:

```html
<div>A</div>
<div>B</div>
<div>C</div>
```

thay vì chỉ một `<div>`.

---

# 18. Greedy vs non-greedy

Giải pháp thường gặp:

```regex
.*
```

đổi thành:

```regex
.*?
```

Ví dụ:

```python
pattern = re.compile(
    r"<div>.*?</div>",
    re.DOTALL,
)
```

`.*?` là **non-greedy**.

Nó cố gắng match ít nhất có thể.

Tuy nhiên, đây vẫn **không phải cách đáng tin cậy để parse HTML tổng quát**. Với HTML thật, hãy dùng HTML parser.

---

# 19. `MULTILINE` và `DOTALL` khác nhau

Đây là bảng cần nhớ:

| Flag        | Thay đổi |
| ----------- | -------- |
| `MULTILINE` | `^`, `$` |
| `DOTALL`    | `.`      |

Cụ thể:

```text
MULTILINE
    ↓
^ $
```

còn:

```text
DOTALL
    ↓
.
```

---

# 20. Kết hợp `MULTILINE + DOTALL`

Có thể dùng:

```python
pattern = re.compile(
    r"^START.*END$",
    re.MULTILINE | re.DOTALL,
)
```

Ý nghĩa:

```text
^
↓
đầu dòng/string

.*
↓
có thể đi qua newline

$
↓
cuối dòng/string
```

Flags có thể kết hợp bằng:

```python
|
```

---

# 21. `re.VERBOSE`

Đây là flag tôi rất khuyến khích bạn sử dụng khi Regex dài.

Alias:

```python
re.X
```

Nó cho phép viết Regex:

* nhiều dòng
* có indentation
* có comment
* dễ đọc hơn

---

# 22. Regex khó đọc

Ví dụ:

```python
pattern = re.compile(r"Chapter\s+(?P<number>\d+)\s*:\s*(?P<title>.+)")
```

Pattern này chưa quá dài.

Nhưng Regex thực tế có thể trở thành:

```text
30–50 ký tự
100 ký tự
200 ký tự
```

Lúc đó rất khó bảo trì.

---

# 23. Dùng `VERBOSE`

```python
pattern = re.compile(
    r"""
    Chapter
    \s+
    (?P<number>\d+)
    \s*
    :
    \s*
    (?P<title>.+)
    """,
    re.VERBOSE,
)
```

Bây giờ pattern có cấu trúc:

```text
Chapter
   ↓
whitespace
   ↓
number
   ↓
:
   ↓
title
```

Dễ đọc hơn rất nhiều.

---

# 24. Comment trong `VERBOSE`

Bạn có thể viết:

```python
pattern = re.compile(
    r"""
    Chapter              # keyword
    \s+                  # whitespace
    (?P<number>\d+)      # chapter number
    \s*                  # optional whitespace
    :                    # separator
    \s*                  # optional whitespace
    (?P<title>.+)        # title
    """,
    re.VERBOSE,
)
```

Đây là một Regex có thể bảo trì.

---

# 25. Một lưu ý quan trọng của `VERBOSE`

Trong `VERBOSE`, whitespace trong pattern thường được bỏ qua.

Ví dụ:

```python
r"""
hello world
"""
```

không có nghĩa đơn giản là match:

```text
hello world
```

Whitespace giữa `hello` và `world` có thể bị bỏ qua.

Muốn match space thật:

```regex
hello\s+world
```

hoặc:

```regex
hello[ ]world
```

---

# 26. `#` trong `VERBOSE`

Trong `VERBOSE`,:

```text
#
```

bắt đầu comment.

Ví dụ:

```python
pattern = re.compile(
    r"""
    hello
    # comment
    world
    """,
    re.VERBOSE,
)
```

Phần:

```text
# comment
```

không phải Regex.

Muốn match literal `#`, cần escape:

```regex
\#
```

hoặc đặt trong character class:

```regex
[#]
```

---

# 27. `VERBOSE` rất phù hợp với parser

Ví dụ parser chapter:

```python
CHAPTER_PATTERN = re.compile(
    r"""
    ^                       # start
    Chapter                 # keyword
    \s+                     # whitespace
    (?P<number>\d+)         # number
    \s*                     # optional whitespace
    :                       # separator
    \s*                     # optional whitespace
    (?P<title>.+?)          # title
    $                       # end
    """,
    re.IGNORECASE | re.VERBOSE,
)
```

Đây là Regex production-style dễ đọc hơn rất nhiều.

---

# 28. `re.ASCII`

Flag này:

```python
re.ASCII
```

hoặc:

```python
re.A
```

làm cho một số shorthand character classes hoạt động theo quy tắc ASCII thay vì Unicode.

Các pattern đáng chú ý:

```text
\d
\w
\s
\b
```

---

# 29. Python mặc định dùng Unicode

Ví dụ:

```python
import re

text = "Python tiếng Việt"

pattern = re.compile(r"\w+")

print(pattern.findall(text))
```

Python Regex mặc định hiểu Unicode.

Vì vậy:

```text
tiếng
Việt
```

được xử lý theo Unicode rules.

---

# 30. Với `re.ASCII`

```python
pattern = re.compile(
    r"\w+",
    re.ASCII,
)
```

thì:

```python
\w
```

bị giới hạn theo ASCII semantics.

Nói đơn giản:

```text
Unicode mode
    ↓
\w rộng hơn

ASCII mode
    ↓
\w theo ASCII
```

---

# 31. Khi nào dùng `ASCII`?

Ví dụ bạn đang parse một format protocol chỉ chấp nhận:

```text
A-Z
a-z
0-9
_
```

thì:

```python
re.ASCII
```

có thể giúp Regex semantics phù hợp với dữ liệu ASCII.

Nhưng với text tiếng Việt:

> Không nên tùy tiện dùng `re.ASCII`.

---

# 32. So sánh 5 flags

| Flag         | Tác dụng chính                       |
| ------------ | ------------------------------------ |
| `IGNORECASE` | Không phân biệt hoa/thường           |
| `MULTILINE`  | `^`, `$` theo từng dòng              |
| `DOTALL`     | `.` match newline                    |
| `VERBOSE`    | Regex nhiều dòng + comment           |
| `ASCII`      | ASCII semantics cho một số shorthand |

---

# 33. Kết hợp flags

Bạn có thể:

```python
pattern = re.compile(
    r"""
    ^chapter
    \s+
    (?P<number>\d+)
    \s*:
    \s*
    (?P<title>.+)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

Ba flag:

```text
IGNORECASE
MULTILINE
VERBOSE
```

---

# 34. Ví dụ thực tế — Chapter Parser

Input:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
chapter 002: Ba năm
CHAPTER 003: Vân Lam Tông
"""
```

Pattern:

```python
import re

CHAPTER_PATTERN = re.compile(
    r"""
    ^chapter
    \s+
    (?P<number>\d+)
    \s*:
    \s*
    (?P<title>.+?)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

Sau đó:

```python
for match in CHAPTER_PATTERN.finditer(text):
    print(match.groupdict())
```

Kết quả:

```python
{
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
}

{
    "number": "002",
    "title": "Ba năm",
}

{
    "number": "003",
    "title": "Vân Lam Tông",
}
```

Đây là một ví dụ rất tốt về cách kết hợp kiến thức từ:

```text
Buổi 8  → finditer()
Buổi 11 → compile()
Buổi 12 → flags
```

---

# 35. Ví dụ thực tế — Text Block

Input:

```python
text = """
BEGIN
Python
Regex
Asyncio
END
"""
```

Pattern:

```python
BLOCK_PATTERN = re.compile(
    r"""
    BEGIN
    .*?
    END
    """,
    re.DOTALL
    | re.VERBOSE,
)
```

Sau đó:

```python
match = BLOCK_PATTERN.search(text)

if match:
    print(match.group())
```

---

# 36. Ví dụ thực tế — nhiều block

Input:

```text
BEGIN
Python
END

BEGIN
Regex
END
```

Dùng:

```python
BLOCK_PATTERN = re.compile(
    r"""
    BEGIN
    .*?
    END
    """,
    re.DOTALL
    | re.VERBOSE,
)
```

rồi:

```python
blocks = BLOCK_PATTERN.findall(text)
```

Có thể lấy từng block.

Điểm quan trọng là:

```regex
.*?
```

thay vì:

```regex
.*
```

để tránh greedy matching quá xa.

---

# 37. Một lỗi cực kỳ phổ biến

Nhiều người thấy:

```python
re.DOTALL
```

và nghĩ:

> "Regex multi-line."

Không chính xác.

`DOTALL` chỉ thay đổi:

```regex
.
```

Còn:

```regex
^
$
```

là việc của:

```python
MULTILINE
```

Nhớ:

```text
DOTALL
   ↓
.

MULTILINE
   ↓
^ $
```

---

# 38. Một lỗi khác

Nhiều người thấy:

```python
re.MULTILINE
```

và nghĩ:

> "`.` sẽ match newline."

Sai.

Ví dụ:

```python
re.compile(
    r"A.*B",
    re.MULTILINE,
)
```

vẫn không cho `.` vượt qua newline.

Muốn:

```text
A
...
B
```

thì cần:

```python
re.DOTALL
```

---

# 39. Flags với module API

Bạn có thể viết:

```python
re.findall(
    pattern,
    text,
    re.IGNORECASE,
)
```

hoặc:

```python
re.search(
    pattern,
    text,
    re.MULTILINE,
)
```

Nhưng nếu pattern được dùng nhiều lần, thường nên:

```python
pattern = re.compile(
    pattern,
    flags,
)
```

rồi:

```python
pattern.findall(text)
pattern.search(text)
```

---

# 40. Flags với compiled pattern

Ví dụ:

```python
CHAPTER_PATTERN = re.compile(
    r"Chapter\s+\d+",
    re.IGNORECASE,
)
```

Không cần:

```python
CHAPTER_PATTERN.search(
    text,
    re.IGNORECASE,
)
```

Thực tế các method của `Pattern` không nhận flags mới theo cách đó.

Configuration đã nằm trong compiled pattern.

---

# 41. Một kiến trúc Regex tốt

Bạn có thể tổ chức:

```text
regex/
│
├── patterns.py
├── chapter.py
├── cleaner.py
└── url.py
```

`patterns.py`:

```python
import re


CHAPTER_PATTERN = re.compile(
    r"""
    ^chapter
    \s+
    (?P<number>\d+)
    \s*:
    \s*
    (?P<title>.+?)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

Parser:

```python
from .patterns import CHAPTER_PATTERN


def parse_chapters(text: str):
    return [
        match.groupdict()
        for match in CHAPTER_PATTERN.finditer(text)
    ]
```

Đây là kiến trúc rất phù hợp với crawler framework.

---

# 42. Bài tập

## Bài 1 — `IGNORECASE`

Cho:

```python
text = "Python PYTHON python PyThOn"
```

Viết:

```python
pattern = re.compile(...)
```

để:

```python
pattern.findall(text)
```

trả về cả 4 kết quả.

---

# Bài 2 — `MULTILINE`

Cho:

```python
text = """Python
Regex
Asyncio
PySide6"""
```

Dùng:

```regex
^.+$
```

với:

```python
re.MULTILINE
```

để lấy từng dòng.

---

# Bài 3 — `DOTALL`

Cho:

```python
text = """START
Python
Regex
Asyncio
END"""
```

Viết pattern để lấy toàn bộ:

```text
START
Python
Regex
Asyncio
END
```

Gợi ý:

```regex
START.*END
```

và:

```python
re.DOTALL
```

---

# Bài 4 — `VERBOSE`

Viết Regex:

```text
Chapter 001: Vẫn là Tiêu Viêm
```

với:

```python
re.VERBOSE
```

và named groups:

```text
number
title
```

---

# Bài 5 — Kết hợp flags

Input:

```python
text = """
Chapter 001: Python
chapter 002: Regex
CHAPTER 003: Asyncio
"""
```

Viết:

```python
CHAPTER_PATTERN = re.compile(...)
```

sử dụng:

```python
re.IGNORECASE
re.MULTILINE
re.VERBOSE
```

Sau đó:

```python
for match in CHAPTER_PATTERN.finditer(text):
    print(match.groupdict())
```

---

# Challenge — `ChapterParser`

Xây:

```python
import re


class ChapterParser:

    PATTERN = re.compile(
        ...
    )

    def parse_all(self, text: str) -> list[dict]:
        ...
```

Input:

```text
Chapter 001: Vẫn là Tiêu Viêm
chapter 002: Ba năm
CHAPTER 003: Vân Lam Tông
```

Output:

```python
[
    {
        "number": "001",
        "title": "Vẫn là Tiêu Viêm",
    },
    {
        "number": "002",
        "title": "Ba năm",
    },
    {
        "number": "003",
        "title": "Vân Lam Tông",
    },
]
```

Yêu cầu:

```text
re.compile()
+
re.IGNORECASE
+
re.MULTILINE
+
re.VERBOSE
+
finditer()
+
named groups
```

---

# Challenge 2 — Text Block Parser

Xây:

```python
class BlockParser:

    PATTERN = re.compile(
        ...
    )

    def parse_all(self, text: str) -> list[str]:
        ...
```

Input:

```text
BEGIN
Python
Regex
END

BEGIN
Asyncio
PySide6
END
```

Output:

```python
[
    "BEGIN\nPython\nRegex\nEND",
    "BEGIN\nAsyncio\nPySide6\nEND",
]
```

Yêu cầu sử dụng:

```python
re.DOTALL
re.VERBOSE
```

và **non-greedy `.*?`**.

---

# Tổng kết Buổi 12

Bạn cần ghi nhớ chính xác:

```text
┌────────────────┬─────────────────────────────┐
│ Flag           │ Tác dụng                    │
├────────────────┼─────────────────────────────┤
│ IGNORECASE     │ hoa/thường                  │
│ MULTILINE      │ ^ và $ theo từng dòng       │
│ DOTALL         │ . match newline             │
│ VERBOSE        │ Regex dễ đọc + comment      │
│ ASCII          │ ASCII semantics              │
└────────────────┴─────────────────────────────┘
```

Đặc biệt:

```text
IGNORECASE
    ↓
Python = python = PYTHON


MULTILINE
    ↓
^ $
↓
từng dòng


DOTALL
    ↓
.
↓
newline


VERBOSE
    ↓
Regex
↓
nhiều dòng + comment
```

Và khi kết hợp với Buổi 11:

```python
CHAPTER_PATTERN = re.compile(
    r"""
    ^chapter
    \s+
    (?P<number>\d+)
    \s*:
    \s*
    (?P<title>.+?)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

bạn đã có nền tảng rất tốt để bắt đầu viết **Regex Parser thực tế**.

**Phần III** nên đi sâu vào nhóm Regex pattern quan trọng: **Character Classes → Quantifiers → Groups → Anchors → Boundary → Lookaround → Backreference → Conditional/Advanced Regex**, rồi cuối cùng ghép tất cả thành một **production-style text/chapter parser**.
