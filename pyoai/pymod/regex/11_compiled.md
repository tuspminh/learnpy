# Buổi 11 — Compiled Regex với `re.compile()`

Hôm nay chúng ta chuyển từ:

```python
re.search(...)
re.findall(...)
re.split(...)
re.sub(...)
```

sang cách tổ chức Regex chuyên nghiệp hơn:

```python
pattern = re.compile(...)
```

Sau đó dùng:

```python
pattern.search(...)
pattern.findall(...)
pattern.finditer(...)
pattern.split(...)
pattern.sub(...)
```

Đây là bước rất quan trọng khi bạn bắt đầu xây **parser, crawler, text cleaner hoặc framework**.

---

# 1. `re.compile()` là gì?

Ví dụ bình thường:

```python
import re

text = "Python 123 Regex 456"

result = re.findall(r"\d+", text)

print(result)
```

Ta có thể viết:

```python
import re

pattern = re.compile(r"\d+")

result = pattern.findall(text)

print(result)
```

Kết quả giống nhau:

```text
['123', '456']
```

---

# 2. Tư duy

Cách 1:

```text
Regex pattern
      ↓
re.findall()
      ↓
result
```

Cách 2:

```text
Regex pattern
      ↓
re.compile()
      ↓
Pattern object
      ↓
findall()
finditer()
search()
match()
split()
sub()
```

Pattern object chính là một đối tượng Regex đã được biên dịch.

---

# 3. Pattern object

```python
import re

pattern = re.compile(r"\d+")

print(pattern)
print(type(pattern))
```

Bạn sẽ thấy dạng:

```text
re.compile('\\d+')
<class 're.Pattern'>
```

Vì vậy:

```python
pattern
```

không phải string.

Nó là:

```python
re.Pattern
```

---

# 4. `Pattern` có các method rất quan trọng

Sau khi:

```python
pattern = re.compile(r"\d+")
```

bạn có thể:

```python
pattern.search(text)
pattern.match(text)
pattern.fullmatch(text)

pattern.findall(text)
pattern.finditer(text)

pattern.split(text)

pattern.sub(replacement, text)
pattern.subn(replacement, text)
```

Đây chính là toàn bộ API bạn vừa học.

---

# 5. `search()`

Ví dụ:

```python
import re

pattern = re.compile(r"\d+")

text = "Python 123 Regex"

match = pattern.search(text)

print(match.group())
```

→

```text
123
```

Tương đương:

```python
re.search(r"\d+", text)
```

---

# 6. `match()`

```python
pattern = re.compile(r"\d+")

text = "123 Python"

match = pattern.match(text)

print(match.group())
```

→

```text
123
```

Nhưng:

```python
text = "Python 123"

match = pattern.match(text)

print(match)
```

→

```text
None
```

Bởi vì `match()` chỉ kiểm tra từ đầu chuỗi.

---

# 7. `fullmatch()`

```python
pattern = re.compile(r"\d+")

print(
    pattern.fullmatch("123")
)
```

→ Match.

Nhưng:

```python
print(
    pattern.fullmatch("123 Python")
)
```

→

```text
None
```

`fullmatch()` yêu cầu toàn bộ string phải khớp.

---

# 8. `findall()`

```python
pattern = re.compile(r"\d+")

text = "A 123 B 456 C 789"

numbers = pattern.findall(text)

print(numbers)
```

→

```python
['123', '456', '789']
```

---

# 9. `finditer()`

```python
pattern = re.compile(r"\d+")

text = "A 123 B 456"

for match in pattern.finditer(text):
    print(match.group())
    print(match.span())
```

Output:

```text
123
(2, 5)

456
(8, 11)
```

Compiled pattern không làm mất khả năng dùng `Match`.

---

# 10. `split()`

```python
pattern = re.compile(r"[,;|]")

text = "Python,Regex;Asyncio|PySide6"

result = pattern.split(text)

print(result)
```

→

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

---

# 11. `sub()`

```python
pattern = re.compile(r"\d+")

text = "Python 123 Regex 456"

result = pattern.sub(
    "NUMBER",
    text,
)

print(result)
```

→

```text
Python NUMBER Regex NUMBER
```

---

# 12. `subn()`

```python
pattern = re.compile(r"\d+")

text = "Python 123 Regex 456"

result, count = pattern.subn(
    "NUMBER",
    text,
)

print(result)
print(count)
```

→

```text
Python NUMBER Regex NUMBER
2
```

---

# 13. Vậy `compile()` có tác dụng gì?

Điểm quan trọng nhất:

> Khi một Regex pattern được sử dụng nhiều lần, việc compile pattern thành object giúp bạn tái sử dụng pattern thay vì phải viết pattern lặp đi lặp lại.

Ví dụ không compile:

```python
re.search(r"Chapter\s+\d+", text1)
re.search(r"Chapter\s+\d+", text2)
re.search(r"Chapter\s+\d+", text3)
```

Compile:

```python
chapter_pattern = re.compile(
    r"Chapter\s+\d+"
)

chapter_pattern.search(text1)
chapter_pattern.search(text2)
chapter_pattern.search(text3)
```

Code rõ ràng hơn rất nhiều.

---

# 14. Đặc biệt quan trọng trong parser

Giả sử crawler có:

```text
1000 chapters
```

Mỗi chapter cần tìm:

```text
Chapter number
Title
URL
Date
```

Ta có thể định nghĩa pattern một lần:

```python
CHAPTER_PATTERN = re.compile(
    r"Chapter\s+(?P<number>\d+)"
)
```

Sau đó:

```python
for chapter in chapters:
    match = CHAPTER_PATTERN.search(chapter)

    if match:
        number = match.group("number")
```

Đây là cách tổ chức rất tốt.

---

# 15. Đưa Regex thành constant

Thay vì:

```python
def parse(text):
    result = re.search(
        r"Chapter\s+(?P<number>\d+)",
        text,
    )
```

Ta có:

```python
import re

CHAPTER_PATTERN = re.compile(
    r"Chapter\s+(?P<number>\d+)"
)


def parse(text: str):
    result = CHAPTER_PATTERN.search(text)

    if result:
        return result.group("number")
```

Pattern có tên rõ ràng:

```text
CHAPTER_PATTERN
```

Code dễ đọc hơn.

---

# 16. Đây là bước đầu của Regex Parser

Ví dụ:

```python
import re


CHAPTER_PATTERN = re.compile(
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


def parse_chapter_heading(text: str):
    match = CHAPTER_PATTERN.search(text)

    if not match:
        return None

    return match.groupdict()
```

Sau này khi học:

```text
re.VERBOSE
```

pattern sẽ dễ tổ chức hơn nữa.

---

# 17. `Pattern.pattern`

Bạn có thể lấy Regex gốc:

```python
import re

pattern = re.compile(r"\d+")

print(pattern.pattern)
```

→

```text
\d+
```

---

# 18. `Pattern.flags`

```python
import re

pattern = re.compile(
    r"python",
    re.IGNORECASE,
)

print(pattern.flags)
```

Bạn có thể kiểm tra flags mà pattern đang sử dụng.

Phần flags sẽ được học kỹ ở **Buổi 12**.

---

# 19. `Pattern.groups`

Ví dụ:

```python
import re

pattern = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})"
)

print(pattern.groups)
```

→

```text
3
```

Có 3 capturing groups.

---

# 20. `Pattern.groupindex`

Named groups:

```python
import re

pattern = re.compile(
    r"""
    (?P<year>\d{4})
    -
    (?P<month>\d{2})
    -
    (?P<day>\d{2})
    """,
    re.VERBOSE,
)

print(pattern.groupindex)
```

Kết quả tương tự:

```python
{
    'year': 1,
    'month': 2,
    'day': 3,
}
```

Đây là thông tin rất hữu ích khi xây parser.

---

# 21. Compile pattern cho email

Ví dụ:

```python
import re

EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.-]+"
)
```

Sau đó:

```python
text = """
Contact:
admin@example.com
support@example.org
"""

emails = EMAIL_PATTERN.findall(text)

print(emails)
```

→

```python
[
    'admin@example.com',
    'support@example.org'
]
```

---

# 22. Compile pattern cho URL

Ví dụ đơn giản:

```python
URL_PATTERN = re.compile(
    r"https?://[^\s]+"
)
```

Sau đó:

```python
text = """
Visit https://example.com
or https://python.org
"""

urls = URL_PATTERN.findall(text)

print(urls)
```

→

```python
[
    'https://example.com',
    'https://python.org'
]
```

Pattern có thể tái sử dụng ở nhiều nơi.

---

# 23. Compile pattern cho Chapter

Đây là ví dụ sát với crawler:

```python
CHAPTER_PATTERN = re.compile(
    r"""
    Chapter
    \s+
    (?P<number>\d+)
    \s*
    :
    \s*
    (?P<title>.+)
    """,
    re.IGNORECASE | re.VERBOSE,
)
```

Input:

```text
Chapter 001: Vẫn là Tiêu Viêm
```

Ta có:

```python
match = CHAPTER_PATTERN.search(text)
```

Sau đó:

```python
print(match.groupdict())
```

→

```python
{
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
}
```

---

# 24. Một pattern có thể phục vụ nhiều API

Ví dụ:

```python
NUMBER_PATTERN = re.compile(r"\d+")
```

Sau đó:

```python
NUMBER_PATTERN.search(text)

NUMBER_PATTERN.findall(text)

NUMBER_PATTERN.finditer(text)

NUMBER_PATTERN.split(text)

NUMBER_PATTERN.sub("NUMBER", text)

NUMBER_PATTERN.subn("NUMBER", text)
```

Điều này làm Regex trở thành một **reusable component**.

---

# 25. Đóng gói Regex thành class

Khi project lớn hơn, có thể tổ chức:

```python
import re


class Patterns:
    NUMBER = re.compile(r"\d+")
    EMAIL = re.compile(
        r"[\w.+-]+@[\w-]+\.[\w.-]+"
    )
    URL = re.compile(
        r"https?://[^\s]+"
    )
```

Sử dụng:

```python
numbers = Patterns.NUMBER.findall(text)
emails = Patterns.EMAIL.findall(text)
urls = Patterns.URL.findall(text)
```

Đây là một cách tổ chức đơn giản.

---

# 26. Hoặc module riêng

Production project có thể có:

```text
project/
│
├── parser/
│   ├── __init__.py
│   ├── patterns.py
│   └── chapter_parser.py
│
└── main.py
```

`patterns.py`:

```python
import re


CHAPTER_PATTERN = re.compile(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)"
)

EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.-]+"
)

URL_PATTERN = re.compile(
    r"https?://[^\s]+"
)
```

`chapter_parser.py`:

```python
from .patterns import CHAPTER_PATTERN


def parse_chapter(text: str):
    match = CHAPTER_PATTERN.search(text)

    if not match:
        return None

    return match.groupdict()
```

Đây là kiến trúc sạch hơn rất nhiều so với rải Regex khắp project.

---

# 27. Một lỗi kiến trúc thường gặp

Không nên:

```python
def parser(text):
    re.search(r"...", text)
    re.findall(r"...", text)
    re.sub(r"...", "...", text)
    re.split(r"...", text)
```

Nếu project lớn, Regex sẽ nằm khắp nơi.

Tốt hơn:

```text
patterns.py
     │
     ├── CHAPTER_PATTERN
     ├── URL_PATTERN
     ├── EMAIL_PATTERN
     └── ...
          │
          ▼
       parser
```

Pattern được quản lý tập trung.

---

# 28. `compile()` không có nghĩa là mọi Regex đều cần compile

Đừng hiểu:

> "Dùng Regex thì luôn phải `re.compile()`."

Không cần.

Nếu chỉ dùng một lần:

```python
re.search(r"\d+", text)
```

hoàn toàn ổn.

Nếu pattern:

* dùng nhiều lần
* dài
* có tên
* có flags
* dùng trong nhiều function
* thuộc parser
* thuộc crawler framework

thì `re.compile()` rất hợp lý.

---

# 29. Python đã có caching

Một điểm kỹ thuật quan trọng:

Python `re` có cơ chế cache cho một số pattern đã sử dụng gần đây.

Vì vậy không nên tuyên bố đơn giản rằng:

> "`re.compile()` luôn nhanh hơn rất nhiều."

Không chính xác.

Lợi ích lớn của `compile()` trong code thực tế thường là:

```text
reusability
readability
centralization
configuration
maintainability
```

và tránh việc code phải biểu diễn pattern lặp đi lặp lại.

---

# 30. Compile + flags

Ví dụ:

```python
import re

pattern = re.compile(
    r"python",
    re.IGNORECASE,
)
```

Sau đó:

```python
pattern.findall(
    "Python python PYTHON"
)
```

→

```python
['Python', 'python', 'PYTHON']
```

Không cần truyền:

```python
re.IGNORECASE
```

mỗi lần.

Đây là một lợi ích rất lớn khi pattern có configuration cố định.

---

# 31. Compile + `VERBOSE`

Pattern dài:

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

Sau khi compile:

```python
pattern.search(text)
```

Code parser rất dễ đọc.

Buổi 12 chúng ta sẽ học kỹ `re.VERBOSE`.

---

# 32. Compile + function replacement

Ta có thể kết hợp toàn bộ kiến thức:

```python
import re


NUMBER_PATTERN = re.compile(r"\d+")


def double_number(match: re.Match) -> str:
    number = int(match.group())
    return str(number * 2)


text = "10 20 30"

result = NUMBER_PATTERN.sub(
    double_number,
    text,
)

print(result)
```

Kết quả:

```text
20 40 60
```

Đây là một pattern rất mạnh:

```text
Compiled Pattern
       ↓
      sub()
       ↓
 Match object
       ↓
 Python function
       ↓
 transformed text
```

---

# 33. Xây `TextCleaner`

Bây giờ chúng ta có thể bắt đầu xây một component thực tế:

```python
import re


class TextCleaner:

    WHITESPACE = re.compile(r"[ \t]+")
    BLANK_LINES = re.compile(r"\n{3,}")

    def clean(self, text: str) -> str:
        text = self.WHITESPACE.sub(" ", text)
        text = self.BLANK_LINES.sub("\n\n", text)
        return text.strip()
```

Sử dụng:

```python
cleaner = TextCleaner()

text = """
Python     Regex


Asyncio



PySide6
"""

print(cleaner.clean(text))
```

---

# 34. Đây chính là nền tảng cho project của bạn

Bạn có thể phát triển:

```text
TextCleaner
     │
     ├── normalize_whitespace()
     ├── normalize_newlines()
     ├── remove_comments()
     ├── normalize_chapters()
     └── ...
```

Các Regex:

```text
patterns
    │
    ├── WHITESPACE_PATTERN
    ├── CHAPTER_PATTERN
    ├── URL_PATTERN
    └── ...
```

được compile một lần.

Đây là cách bắt đầu biến kiến thức `re` thành **kiến trúc code thực tế**.

---

# 35. Bài tập

## Bài 1 — Compile number

Viết:

```python
NUMBER_PATTERN = re.compile(...)
```

để tìm tất cả số:

```python
text = "Python 123 Regex 456 Asyncio 789"
```

Kết quả:

```python
['123', '456', '789']
```

---

## Bài 2 — Compile email

Viết:

```python
EMAIL_PATTERN = re.compile(...)
```

và dùng:

```python
EMAIL_PATTERN.findall(text)
```

để lấy tất cả email.

---

## Bài 3 — Compile Chapter

Viết:

```python
CHAPTER_PATTERN = re.compile(...)
```

cho:

```text
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
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
    "title": "Vẫn là Tiêu Viêm"
}

{
    "number": "002",
    "title": "Ba năm"
}
```

---

# Bài 4 — Compiled `sub()`

Tạo:

```python
WHITESPACE_PATTERN = re.compile(r"\s+")
```

Sau đó:

```python
WHITESPACE_PATTERN.sub(" ", text)
```

để normalize whitespace.

---

# Bài 5 — Compiled `split()`

Tạo:

```python
DELIMITER_PATTERN = re.compile(...)
```

để xử lý:

```text
Python,Regex;Asyncio|PySide6
```

thành:

```python
[
    "Python",
    "Regex",
    "Asyncio",
    "PySide6",
]
```

---

# Challenge — `ChapterParser`

Xây một parser nhỏ:

```python
import re


class ChapterParser:

    PATTERN = re.compile(
        r"""
        Chapter
        \s+
        (?P<number>\d+)
        \s*
        :
        \s*
        (?P<title>.+)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    def parse(self, text: str) -> dict | None:
        ...
```

Input:

```text
Chapter 001: Vẫn là Tiêu Viêm
```

Output:

```python
{
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
}
```

---

# Challenge 2 — Regex Registry

Thiết kế:

```python
class Patterns:
    ...
```

với:

```python
NUMBER
EMAIL
URL
CHAPTER
WHITESPACE
```

Mỗi pattern phải được:

```python
re.compile(...)
```

Sau đó viết:

```python
class TextCleaner:
    ...
```

sử dụng các compiled patterns.

Mục tiêu kiến trúc:

```text
                  patterns.py
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Chapter      Cleaner      URL Parser
       Parser
          │           │           │
          └───────────┼───────────┘
                      ↓
                compiled Regex
```

Đây là bài tập rất tốt trước khi chuyển sang **Flags**.

---

# Tổng kết Buổi 11

Điều quan trọng nhất:

```python
pattern = re.compile(r"\d+")
```

Sau đó:

```python
pattern.search(text)
pattern.match(text)
pattern.fullmatch(text)

pattern.findall(text)
pattern.finditer(text)

pattern.split(text)

pattern.sub(...)
pattern.subn(...)
```

### Tư duy kiến trúc

Thay vì:

```python
re.search(...)
re.findall(...)
re.sub(...)
re.split(...)
```

rải rác khắp code, hãy nghĩ:

```text
Regex Definition
       ↓
re.compile()
       ↓
Pattern Object
       ↓
Parser / Cleaner / Crawler
```

Và khi project lớn:

```text
patterns.py
    ↓
compiled patterns
    ↓
parser
    ↓
domain/application
```

**Buổi 12 — Flags** sẽ hoàn thiện phần `re` API cơ bản với:

```python
re.IGNORECASE
re.MULTILINE
re.DOTALL
re.VERBOSE
re.ASCII
```

Trong đó **`MULTILINE`, `DOTALL` và `VERBOSE` cực kỳ quan trọng** khi bạn xử lý HTML/text nhiều dòng và xây parser Regex thực tế.
