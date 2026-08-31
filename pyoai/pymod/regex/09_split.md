# Buổi 9 — `re.split()`

Hôm nay chúng ta học:

```python
re.split()
```

Nếu:

```python
findall()
```

dùng để **tìm dữ liệu**,

thì:

```python
split()
```

dùng để **chia dữ liệu thành nhiều phần**.

Điểm đặc biệt của `re.split()` là **delimiter cũng có thể là Regex**.

---

# 1. `str.split()` vs `re.split()`

Python đã có:

```python
text.split(",")
```

Ví dụ:

```python
text = "Python,Regex,Asyncio"

print(text.split(","))
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio']
```

Nhưng `str.split()` chỉ thuận tiện khi delimiter khá cố định.

Ví dụ dữ liệu:

```text
Python,Regex;Asyncio|PySide6
```

Nếu muốn tách bằng:

```text
,
;
|
```

thì `re.split()` rất phù hợp.

---

# 2. `re.split()` cơ bản

```python
import re

text = "Python,Regex;Asyncio|PySide6"

result = re.split(r"[,;|]", text)

print(result)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Regex:

```regex
[,;|]
```

nghĩa là:

```text
,
;
|
```

đều được xem là delimiter.

---

# 3. Cú pháp

```python
re.split(pattern, string, maxsplit=0, flags=0)
```

Trong đó:

```text
pattern
    ↓
Regex delimiter

string
    ↓
chuỗi cần chia

maxsplit
    ↓
số lần split tối đa

flags
    ↓
Regex flags
```

---

# 4. `re.split()` trả về list

Ví dụ:

```python
import re

result = re.split(r"\s+", "Python   Regex   Asyncio")

print(result)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio']
```

Nếu không có delimiter:

```python
result = re.split(r"\s+", "Python")
```

→

```python
['Python']
```

---

# 5. Split bằng whitespace

Một trong những ứng dụng phổ biến nhất:

```python
import re

text = "Python   Regex\tAsyncio\nPySide6"

result = re.split(r"\s+", text)

print(result)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Ở đây:

```regex
\s+
```

match:

```text
space
tab
newline
```

và một hoặc nhiều whitespace liên tiếp.

---

# 6. `str.split()` cũng có thể xử lý whitespace

Điều thú vị:

```python
text.split()
```

đã xử lý khá tốt whitespace.

Ví dụ:

```python
text = "Python   Regex\tAsyncio\nPySide6"

print(text.split())
```

→

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Vì vậy:

> Không phải cứ có Regex là phải dùng `re.split()`.

Nếu chỉ cần whitespace:

```python
text.split()
```

thường đơn giản hơn.

---

# 7. Khi `re.split()` thực sự hữu ích

Ví dụ delimiter có nhiều dạng:

```text
,
;
|
::
---
```

Ta có thể:

```python
import re

text = "Python,Regex;Asyncio|PySide6::Qt"

parts = re.split(
    r"[,;|]|::",
    text
)

print(parts)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6', 'Qt']
```

Đây là lúc Regex phát huy tác dụng.

---

# 8. Split bằng nhiều ký tự

Ví dụ:

```python
text = "Python---Regex===Asyncio+++PySide6"
```

Ta có:

```python
parts = re.split(
    r"---|===|\+\+\+",
    text
)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Lưu ý:

```regex
+
```

là metacharacter.

Muốn match dấu `+` literal:

```regex
\+
```

Do đó:

```regex
\+\+\+
```

match:

```text
+++
```

---

# 9. `maxsplit`

Giống `str.split()`, `re.split()` có:

```python
maxsplit
```

Ví dụ:

```python
import re

text = "a,b,c,d"

result = re.split(
    r",",
    text,
    maxsplit=2
)

print(result)
```

Kết quả:

```python
['a', 'b', 'c,d']
```

---

# 10. `maxsplit=1`

Rất hữu ích khi parser key/value.

Ví dụ:

```text
title: Python: Regex: Advanced
```

Nếu viết:

```python
text.split(":")
```

ta nhận:

```python
['title', ' Python', ' Regex', ' Advanced']
```

Nhưng có thể muốn:

```python
key = "title"
value = "Python: Regex: Advanced"
```

Dùng:

```python
parts = re.split(
    r":",
    text,
    maxsplit=1
)

print(parts)
```

→

```python
['title', ' Python: Regex: Advanced']
```

---

# 11. Đây là kỹ thuật rất hữu ích cho parser

Ví dụ:

```python
line = "Title: Đấu Phá Thương Khung: Phần 1"

key, value = re.split(
    r":\s*",
    line,
    maxsplit=1
)

print(key)
print(value)
```

Kết quả:

```text
Title
Đấu Phá Thương Khung: Phần 1
```

Ta không làm mất dấu `:` bên trong title.

---

# 12. Capturing Group trong `re.split()`

Đây là phần **cực kỳ quan trọng**.

Khi delimiter có capturing group:

```python
re.split(
    r"([,;])",
    text
)
```

thì delimiter được **giữ lại trong kết quả**.

Ví dụ:

```python
import re

text = "Python,Regex;Asyncio"

result = re.split(
    r"([,;])",
    text
)

print(result)
```

Kết quả:

```python
[
    'Python',
    ',',
    'Regex',
    ';',
    'Asyncio'
]
```

---

# 13. Tại sao delimiter lại xuất hiện?

Regex:

```regex
([,;])
```

có capturing group:

```text
( ... )
```

Python giữ lại nội dung của capturing group trong output.

So sánh:

### Không capture

```python
re.split(r"[,;]", text)
```

→

```python
['Python', 'Regex', 'Asyncio']
```

### Có capture

```python
re.split(r"([,;])", text)
```

→

```python
['Python', ',', 'Regex', ';', 'Asyncio']
```

---

# 14. Non-capturing group

Nếu Regex phức tạp nhưng không muốn delimiter xuất hiện trong output:

```python
(?:...)
```

Ví dụ:

```python
import re

text = "Python,Regex;Asyncio"

result = re.split(
    r"(?:,|;)",
    text
)

print(result)
```

→

```python
['Python', 'Regex', 'Asyncio']
```

Có thể nhớ:

```text
(...)
    ↓
capture
    ↓
delimiter được giữ

(?:...)
    ↓
không capture
    ↓
delimiter bị loại
```

---

# 15. Empty string ở đầu/cuối

Đây là một vấn đề thực tế.

```python
import re

text = ",Python,Regex,"

result = re.split(r",", text)

print(result)
```

Kết quả:

```python
['', 'Python', 'Regex', '']
```

Tại sao?

Vì delimiter nằm:

```text
^
,
Python
,
Regex
,
$
```

Có phần text rỗng trước và sau delimiter.

---

# 16. Nhiều delimiter liên tiếp

Ví dụ:

```python
import re

text = "Python,,,Regex"

result = re.split(r",+", text)

print(result)
```

Kết quả:

```python
['Python', 'Regex']
```

Regex:

```regex
,+
```

match:

```text
,,,
```

như **một delimiter duy nhất**.

Đây là ưu điểm lớn của Regex.

---

# 17. `re.split(r"\s+", ...)`

Ví dụ:

```python
text = "Python    Regex\t\tAsyncio\nPySide6"

parts = re.split(r"\s+", text)

print(parts)
```

→

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

---

# 18. Nhưng chú ý whitespace đầu/cuối

```python
text = "   Python   Regex   "

parts = re.split(r"\s+", text)

print(parts)
```

Có thể nhận:

```python
['', 'Python', 'Regex', '']
```

Nếu muốn loại bỏ:

```python
parts = [
    part
    for part in re.split(r"\s+", text.strip())
    if part
]
```

Hoặc nếu chỉ là whitespace đơn giản:

```python
parts = text.split()
```

sẽ tiện hơn.

---

# 19. Split câu

Một bài toán thú vị:

```python
text = "Hello. How are you? I'm fine! Thanks."
```

Có thể:

```python
sentences = re.split(
    r"[.!?]+",
    text
)

print(sentences)
```

Kết quả gần dạng:

```python
[
    'Hello',
    ' How are you',
    " I'm fine",
    ' Thanks',
    ''
]
```

Sau đó làm sạch:

```python
sentences = [
    s.strip()
    for s in re.split(r"[.!?]+", text)
    if s.strip()
]
```

Kết quả:

```python
[
    'Hello',
    'How are you',
    "I'm fine",
    'Thanks'
]
```

---

# 20. Split đoạn văn

Ví dụ:

```python
text = """
Chapter 1: Hello

Chapter 2: Python

Chapter 3: Regex
"""
```

Muốn chia theo blank line:

```python
parts = re.split(
    r"\n\s*\n",
    text.strip()
)
```

Kết quả:

```python
[
    'Chapter 1: Hello',
    'Chapter 2: Python',
    'Chapter 3: Regex'
]
```

Đây là kỹ thuật rất hữu ích khi xử lý text crawler.

---

# 21. Split Markdown

Ví dụ Markdown:

```text
# Introduction

Nội dung...

# Python

Nội dung...

# Regex

Nội dung...
```

Ta có thể dùng Regex để tìm delimiter:

```python
parts = re.split(
    r"\n(?=# )",
    text
)
```

Ý nghĩa:

```regex
\n
```

→ newline

```regex
(?=# )
```

→ ngay sau newline phải là `# `.

Đây là **lookahead**.

Ta sẽ học sâu hơn ở phần Regex nâng cao.

---

# 22. Split chapter

Đây là ví dụ gần với project crawler của bạn.

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm

Nội dung chapter 1...

Chapter 002: Ba năm

Nội dung chapter 2...

Chapter 003: Vân Lam Tông

Nội dung chapter 3...
"""
```

Có thể chia theo chapter:

```python
import re

parts = re.split(
    r"(?=Chapter\s+\d+:)",
    text.strip()
)
```

Kết quả:

```python
[
    "Chapter 001: Vẫn là Tiêu Viêm\n\nNội dung chapter 1...",
    "Chapter 002: Ba năm\n\nNội dung chapter 2...",
    "Chapter 003: Vân Lam Tông\n\nNội dung chapter 3..."
]
```

---

# 23. Tại sao chapter marker vẫn còn?

Pattern:

```regex
(?=Chapter\s+\d+:)
```

là **positive lookahead**.

Nó kiểm tra:

```text
phía sau đây có "Chapter xxx:" không?
```

nhưng **không consume text**.

Do đó:

```text
Chapter 001
Chapter 002
Chapter 003
```

vẫn còn trong kết quả.

Đây là một kỹ thuật cực kỳ hữu ích khi chia document.

---

# 24. So sánh consume và lookahead

### Consume delimiter

```python
re.split(r"Chapter\s+\d+:", text)
```

`Chapter 001:` bị loại khỏi kết quả.

### Lookahead

```python
re.split(r"(?=Chapter\s+\d+:)", text)
```

`Chapter 001:` vẫn giữ lại.

Tư duy:

```text
Chapter 001
      ↓
delimiter thật
      ↓
bị remove


(?=Chapter 001)
      ↓
chỉ kiểm tra
      ↓
không consume
      ↓
được giữ
```

---

# 25. Đây là kỹ thuật parser rất đáng nhớ

Giả sử:

```text
Chapter 001: A
...
Chapter 002: B
...
Chapter 003: C
...
```

Ta có:

```python
chunks = re.split(
    r"(?=Chapter\s+\d+:)",
    text.strip()
)
```

Sau đó:

```python
for chunk in chunks:
    print(chunk)
    print("---")
```

Ta đã biến:

```text
document
```

thành:

```text
chapter 1
chapter 2
chapter 3
```

Tiếp theo có thể dùng:

```python
re.match()
```

hoặc:

```python
re.search()
```

để parse metadata từng chapter.

---

# 26. Pipeline rất hay

Đây là một kiến trúc Regex parser thực tế:

```text
Raw text
   ↓
re.split()
   ↓
chunks
   ↓
từng chapter
   ↓
re.match()
   ↓
metadata
   ↓
re.finditer()
   ↓
entities bên trong chapter
```

Ví dụ:

```text
HTML
 ↓
html2text
 ↓
Markdown/Text
 ↓
re.split()
 ↓
Chapter chunks
 ↓
re.match()
 ↓
Chapter metadata
 ↓
re.finditer()
 ↓
Links / references / IDs
```

Bạn sẽ gặp pattern này rất nhiều khi làm crawler.

---

# 27. `re.split()` không phải parser hoàn chỉnh

Ví dụ:

```python
re.split(r"Chapter\s+\d+:", text)
```

rất tiện.

Nhưng nếu dữ liệu phức tạp:

```text
Chapter 1:
Chapter 2:
Chapter 3:
```

có thể có:

* heading giả
* chapter nằm trong code
* chapter nằm trong quote
* HTML còn sót
* format không đồng nhất

Khi đó cần parser nhiều bước.

Regex nên được xem là:

> **một công cụ trong pipeline**, không phải lúc nào cũng là toàn bộ parser.

---

# 28. `re.split()` với Unicode

Python Regex hỗ trợ Unicode khá tốt.

Ví dụ:

```python
import re

text = "Python，Regex；Asyncio｜PySide6"

parts = re.split(
    r"[，；｜]",
    text
)

print(parts)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Bạn có thể đưa các delimiter Unicode trực tiếp vào Regex.

---

# 29. Split dữ liệu không đồng nhất

Ví dụ:

```text
Python, Regex; Asyncio | PySide6
```

Ta có:

```python
parts = re.split(
    r"\s*[,;|]\s*",
    text
)
```

Kết quả:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

Pattern:

```regex
\s*
```

cho phép whitespace xung quanh delimiter.

Đây là một pattern thực tế rất hay.

---

# 30. Một ví dụ khác

Input:

```text
Python / Regex | Asyncio , PySide6
```

Ta có:

```python
parts = re.split(
    r"\s*[/|,]\s*",
    text
)
```

→

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

---

# 31. Khi nào dùng `str.split()`?

Nếu delimiter cố định:

```python
text.split(",")
```

→ tốt.

Nếu whitespace:

```python
text.split()
```

→ tốt.

Nếu cần nhiều loại delimiter:

```python
re.split(r"[,;|]", text)
```

→ tốt.

Nếu delimiter có cấu trúc:

```python
re.split(r"\n(?=Chapter\s+\d+)", text)
```

→ Regex gần như bắt buộc.

---

# 32. So sánh nhanh

| Tình huống         | Nên dùng                     |              |
| ------------------ | ---------------------------- | ------------ |
| `"a,b,c"`          | `split(",")`                 |              |
| `"a b c"`          | `split()`                    |              |
| `"a,b;c            | d"`                          | `re.split()` |
| nhiều whitespace   | `split()` hoặc `re.split()`  |              |
| delimiter phức tạp | `re.split()`                 |              |
| cần lookahead      | `re.split()`                 |              |
| cần giữ delimiter  | capturing group / lookaround |              |

---

# 33. Bài tập

## Bài 1 — Nhiều delimiter

Cho:

```python
text = "Python,Regex;Asyncio|PySide6"
```

Dùng:

```python
re.split()
```

để tạo:

```python
['Python', 'Regex', 'Asyncio', 'PySide6']
```

---

## Bài 2 — Whitespace

Cho:

```python
text = "Python   Regex\tAsyncio\nPySide6"
```

Dùng:

```regex
\s+
```

để split.

---

## Bài 3 — `maxsplit`

Cho:

```python
text = "title: Python: Regex: Advanced"
```

Tạo:

```python
[
    "title",
    "Python: Regex: Advanced"
]
```

Yêu cầu:

```text
maxsplit=1
```

---

# Bài 4 — Giữ delimiter

Cho:

```python
text = "Python,Regex;Asyncio"
```

Tạo:

```python
[
    "Python",
    ",",
    "Regex",
    ";",
    "Asyncio"
]
```

Gợi ý:

```regex
([,;])
```

---

# Bài 5 — Tách câu

Cho:

```python
text = "Hello. How are you? I'm fine! Thanks."
```

Tạo:

```python
[
    "Hello",
    "How are you",
    "I'm fine",
    "Thanks"
]
```

---

# Bài 6 — Tách paragraph

Cho:

```python
text = """
Paragraph 1

Paragraph 2

Paragraph 3
"""
```

Dùng `re.split()` để tạo:

```python
[
    "Paragraph 1",
    "Paragraph 2",
    "Paragraph 3",
]
```

---

# Bài 7 — Chapter splitter

Cho:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm

Nội dung 1...

Chapter 002: Ba năm

Nội dung 2...

Chapter 003: Vân Lam Tông

Nội dung 3...
"""
```

Dùng:

```python
re.split()
```

với lookahead để tạo:

```python
[
    "Chapter 001: Vẫn là Tiêu Viêm\n\nNội dung 1...",
    "Chapter 002: Ba năm\n\nNội dung 2...",
    "Chapter 003: Vân Lam Tông\n\nNội dung 3...",
]
```

Gợi ý:

```regex
(?=Chapter\s+\d+:)
```

---

# Challenge — Xây `ChapterSplitter`

Viết:

```python
import re


def split_chapters(text: str) -> list[str]:
    ...
```

Input:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm

Nội dung chapter 1...

Chapter 002: Ba năm

Nội dung chapter 2...

Chapter 003: Vân Lam Tông

Nội dung chapter 3...
"""
```

Yêu cầu:

### 1. Xóa whitespace thừa đầu/cuối

```python
text.strip()
```

### 2. Split bằng lookahead

```python
r"(?=Chapter\s+\d+:)"
```

### 3. Không làm mất `Chapter XXX:`

### 4. Không tạo phần tử rỗng.

Sau đó viết tiếp:

```python
def parse_chapter(chunk: str) -> dict[str, str]:
    ...
```

để biến:

```text
Chapter 001: Vẫn là Tiêu Viêm

Nội dung chapter 1...
```

thành:

```python
{
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
    "content": "Nội dung chapter 1..."
}
```

Đây là bài tập **rất gần với crawler/parser framework**.

---

# Tổng kết Buổi 9

Ba thứ quan trọng nhất hôm nay:

### 1. Split bằng Regex

```python
re.split(r"[,;|]", text)
```

### 2. `maxsplit`

```python
re.split(r":\s*", text, maxsplit=1)
```

### 3. Lookahead để giữ delimiter

```python
re.split(
    r"(?=Chapter\s+\d+:)",
    text
)
```

Đặc biệt hãy nhớ kỹ:

```text
findall()
    ↓
Tìm tất cả

finditer()
    ↓
Tìm tất cả + Match object

split()
    ↓
Chia text

re.split()
    ↓
Chia text bằng Regex
```

Và pipeline rất quan trọng:

```text
                 Raw Text
                    │
                    ▼
              re.split()
                    │
                    ▼
              Text Chunks
                    │
                    ▼
               re.match()
                    │
                    ▼
              Metadata
                    │
                    ▼
             re.finditer()
                    │
                    ▼
             Extract entities
```

**Buổi 10 — `re.sub()` và `re.subn()`** sẽ là bước tiếp theo: thay vì **tìm** hoặc **chia**, chúng ta sẽ học cách **thay thế hàng loạt bằng Regex**. Đây là nền tảng để xây HTML cleaner, text cleaner, normalization pipeline và xử lý dữ liệu crawler.
