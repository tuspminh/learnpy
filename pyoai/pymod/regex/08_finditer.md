# Buổi 8 — `re.finditer()`

Ở Buổi 7, chúng ta học:

```python
re.findall()
```

Nó rất tiện khi chỉ cần **danh sách kết quả**.

Nhưng khi viết parser/crawler thực tế, ta thường cần nhiều hơn:

```text
giá trị match
↓
group
↓
named group
↓
vị trí bắt đầu
↓
vị trí kết thúc
↓
span
```

Lúc này dùng:

```python
re.finditer()
```

---

# 1. `finditer()` là gì?

Cú pháp:

```python
re.finditer(pattern, string)
```

Nó tìm **tất cả match**, nhưng thay vì trả về `list`, nó trả về một **iterator chứa các `Match` object**.

Ví dụ:

```python
import re

text = "Python 123 Regex 456"

matches = re.finditer(r"\d+", text)

for match in matches:
    print(match)
```

Kết quả đại khái:

```text
<re.Match object; span=(7, 10), match='123'>
<re.Match object; span=(17, 20), match='456'>
```

---

# 2. Lấy giá trị bằng `.group()`

```python
import re

text = "Python 123 Regex 456"

for match in re.finditer(r"\d+", text):
    print(match.group())
```

Output:

```text
123
456
```

Đây là điểm rất quan trọng:

```python
findall()
    ↓
'123'

finditer()
    ↓
Match object
    ↓
.group()
    ↓
'123'
```

---

# 3. `findall()` vs `finditer()`

Cùng một Regex:

```python
pattern = r"\d+"
text = "abc123 xyz456"
```

### `findall()`

```python
matches = re.findall(pattern, text)

print(matches)
```

→

```python
['123', '456']
```

### `finditer()`

```python
matches = re.finditer(pattern, text)

for match in matches:
    print(match.group())
```

→

```text
123
456
```

Nhưng `finditer()` còn cho phép:

```python
match.start()
match.end()
match.span()
match.group()
match.groupdict()
```

---

# 4. `.start()`

`start()` trả về vị trí bắt đầu của match.

```python
import re

text = "abc123xyz"

match = re.search(r"\d+", text)

print(match.group())
print(match.start())
```

Output:

```text
123
3
```

Vì:

```text
abc123xyz
012345678
   ^^^
```

`123` bắt đầu ở index `3`.

---

# 5. `.end()`

```python
import re

text = "abc123xyz"

match = re.search(r"\d+", text)

print(match.start())
print(match.end())
```

Output:

```text
3
6
```

Nhớ:

> `end()` là vị trí **sau ký tự cuối cùng**.

Không phải index của ký tự cuối.

```text
abc123xyz
   012345678
   │  │
 start=3
 end=6
```

Python slicing cũng dùng quy tắc này:

```python
text[3:6]
```

→

```text
123
```

---

# 6. `.span()`

`span()` trả về:

```python
(start, end)
```

Ví dụ:

```python
import re

text = "abc123xyz"

match = re.search(r"\d+", text)

print(match.span())
```

Output:

```text
(3, 6)
```

Tương đương:

```python
match.start()
match.end()
```

---

# 7. `finditer()` + vị trí

Đây là điểm rất mạnh.

```python
import re

text = "abc123 xyz456 test789"

for match in re.finditer(r"\d+", text):
    print(
        match.group(),
        match.start(),
        match.end(),
        match.span(),
    )
```

Output:

```text
123 3 6 (3, 6)
456 10 13 (10, 13)
789 18 21 (18, 21)
```

Ta vừa lấy được:

```text
giá trị
+
vị trí
```

---

# 8. Vì sao vị trí quan trọng?

Trong parser, đôi khi ta không chỉ muốn biết:

```text
"123"
```

mà còn muốn biết:

```text
"123" nằm ở đâu trong document?
```

Ví dụ:

```text
Title: Python
Chapter: 123
Content: Hello...
```

Regex có thể cho:

```text
123
↓
start = 24
end = 27
```

Từ đó ta có thể:

* highlight text
* cắt document
* tạo index
* phân tích cấu trúc document
* xác định vị trí lỗi
* xây syntax parser

---

# 9. `finditer()` với capturing group

Ví dụ:

```python
import re

text = "Chapter 001 Chapter 002 Chapter 003"

pattern = r"Chapter\s+(\d+)"

for match in re.finditer(pattern, text):
    print(match.group())
    print(match.group(1))
```

Output:

```text
Chapter 001
001

Chapter 002
002

Chapter 003
003
```

Khác với `findall()`:

```python
re.findall(pattern, text)
```

→

```python
['001', '002', '003']
```

`finditer()` giữ nguyên **toàn bộ Match object**.

---

# 10. `group(0)`

Có một quy tắc quan trọng:

```python
match.group(0)
```

là **toàn bộ match**.

Ví dụ:

```python
import re

text = "Chapter 001"

match = re.search(
    r"Chapter\s+(\d+)",
    text
)

print(match.group(0))
print(match.group(1))
```

Output:

```text
Chapter 001
001
```

Có thể nhớ:

```text
group(0)
    ↓
toàn bộ match

group(1)
    ↓
capturing group thứ nhất

group(2)
    ↓
capturing group thứ hai
```

---

# 11. Nhiều groups

```python
import re

text = "Chapter 001: Python"

pattern = r"Chapter\s+(\d+):\s*(.+)"

match = re.search(pattern, text)

print(match.group(0))
print(match.group(1))
print(match.group(2))
```

Output:

```text
Chapter 001: Python
001
Python
```

---

# 12. `finditer()` với nhiều match

```python
import re

text = """
Chapter 001: Python
Chapter 002: Regex
Chapter 003: Asyncio
"""

pattern = r"Chapter\s+(\d+):\s*(.+)"

for match in re.finditer(pattern, text):
    print("FULL:", match.group(0))
    print("NUMBER:", match.group(1))
    print("TITLE:", match.group(2))
    print("SPAN:", match.span())
    print()
```

Kết quả:

```text
FULL: Chapter 001: Python
NUMBER: 001
TITLE: Python
SPAN: (...)

FULL: Chapter 002: Regex
NUMBER: 002
TITLE: Regex
SPAN: (...)

FULL: Chapter 003: Asyncio
NUMBER: 003
TITLE: Asyncio
SPAN: (...)
```

Đây là kiểu code rất gần với parser thực tế.

---

# 13. Named Groups

Trong parser chuyên nghiệp, tôi khuyên bạn sử dụng **named groups**.

Thay vì:

```regex
Chapter\s+(\d+):\s*(.+)
```

ta viết:

```regex
Chapter\s+(?P<number>\d+):\s*(?P<title>.+)
```

Python:

```python
import re

text = "Chapter 001: Python"

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

print(match.group("number"))
print(match.group("title"))
```

Output:

```text
001
Python
```

---

# 14. `.groupdict()`

Named groups trở nên cực kỳ hữu ích với:

```python
match.groupdict()
```

Ví dụ:

```python
import re

text = "Chapter 001: Python"

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

print(match.groupdict())
```

Kết quả:

```python
{
    "number": "001",
    "title": "Python",
}
```

Đây là một trong những lý do `finditer()` rất thích hợp cho parser.

---

# 15. `findall()` vs `finditer()` với named groups

### `findall()`

```python
result = re.findall(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    text
)
```

→

```python
[
    ("001", "Python"),
    ("002", "Regex"),
]
```

### `finditer()`

```python
for match in re.finditer(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    text
):
    print(match.groupdict())
```

→

```python
{
    "number": "001",
    "title": "Python"
}

{
    "number": "002",
    "title": "Regex"
}
```

Và đồng thời có:

```python
match.span()
match.start()
match.end()
```

---

# 16. Đây là pattern parser tôi muốn bạn ghi nhớ

```python
import re

pattern = re.compile(
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

for match in pattern.finditer(text):
    data = match.groupdict()

    print(data)
    print(match.span())
```

Ta có kiến trúc:

```text
Regex
  ↓
finditer()
  ↓
Match
  ├── group()
  ├── groupdict()
  ├── start()
  ├── end()
  └── span()
```

Đây là nền tảng rất tốt để xây parser.

---

# 17. `finditer()` trả iterator

Ví dụ:

```python
import re

matches = re.finditer(
    r"\d+",
    "123 abc 456"
)

print(matches)
```

Bạn sẽ nhận một iterator:

```text
<callable_iterator ...>
```

Nó không phải:

```python
list
```

Bạn có thể lặp:

```python
for match in matches:
    print(match.group())
```

---

# 18. Iterator nghĩa là xử lý từng match

Điều này rất hữu ích khi text lớn.

Thay vì ngay lập tức tạo một list tất cả kết quả:

```python
matches = re.findall(...)
```

`finditer()` cho phép xử lý từng match:

```python
for match in re.finditer(...):
    process(match)
```

Tư duy:

```text
document lớn
     ↓
finditer()
     ↓
match 1 → xử lý
match 2 → xử lý
match 3 → xử lý
...
```

Đặc biệt hữu ích trong các pipeline xử lý text.

---

# 19. `list(finditer())`

Nếu thật sự muốn list:

```python
matches = list(
    re.finditer(r"\d+", text)
)
```

Bây giờ:

```python
type(matches)
```

là:

```python
list
```

và mỗi phần tử là:

```python
re.Match
```

Ví dụ:

```python
for match in matches:
    print(match.group())
```

---

# 20. `finditer()` vs `search()` trong vòng lặp

Bạn có thể tưởng tượng:

```python
re.search()
```

→ tìm một match.

```python
re.finditer()
```

→ tìm tất cả match.

Nếu viết:

```python
match = re.search(pattern, text)
```

chỉ có:

```text
match đầu tiên
```

Trong khi:

```python
for match in re.finditer(pattern, text):
    ...
```

có:

```text
match 1
match 2
match 3
...
```

---

# 21. Ví dụ thực tế: parse chapter

Cho:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
```

Ta viết:

```python
import re

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

for match in re.finditer(pattern, text):
    print(match.groupdict())
```

Kết quả:

```python
{'number': '001', 'title': 'Vẫn là Tiêu Viêm'}
{'number': '002', 'title': 'Ba năm'}
{'number': '003', 'title': 'Vân Lam Tông'}
```

---

# 22. Tạo list chapter

Ta có thể tạo:

```python
chapters = []

for match in re.finditer(pattern, text):
    chapters.append(
        match.groupdict()
    )
```

Kết quả:

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

---

# 23. Và giữ cả vị trí

Đây mới là điểm mạnh.

```python
chapters = []

for match in re.finditer(pattern, text):
    chapters.append({
        **match.groupdict(),
        "start": match.start(),
        "end": match.end(),
    })
```

Kết quả dạng:

```python
{
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
    "start": ...,
    "end": ...,
}
```

Bây giờ parser không chỉ biết:

```text
chapter là gì
```

mà còn biết:

```text
chapter nằm ở đâu trong document
```

---

# 24. Dùng `.span()`

Có thể viết gọn:

```python
chapters = []

for match in re.finditer(pattern, text):
    data = match.groupdict()

    data["span"] = match.span()

    chapters.append(data)
```

---

# 25. `.groups()`

Ngoài:

```python
group()
groupdict()
```

còn có:

```python
groups()
```

Ví dụ:

```python
import re

match = re.search(
    r"Chapter\s+(\d+):\s*(.+)",
    "Chapter 001: Python"
)

print(match.groups())
```

Kết quả:

```python
('001', 'Python')
```

Nó trả về tuple chứa tất cả capturing groups.

---

# 26. So sánh các API của `Match`

Bạn nên nhớ:

```python
match.group()
```

→ toàn bộ match.

```python
match.group(1)
```

→ group 1.

```python
match.groups()
```

→ tất cả groups dưới dạng tuple.

```python
match.groupdict()
```

→ named groups dưới dạng dict.

```python
match.start()
```

→ vị trí bắt đầu.

```python
match.end()
```

→ vị trí kết thúc.

```python
match.span()
```

→ `(start, end)`.

---

# 27. Một ví dụ tổng hợp

```python
import re

text = "Chapter 001: Python"

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

print("group:", match.group())
print("groups:", match.groups())
print("dict:", match.groupdict())
print("number:", match.group("number"))
print("title:", match.group("title"))
print("start:", match.start())
print("end:", match.end())
print("span:", match.span())
```

Đây là đoạn code rất đáng chạy thử.

---

# 28. Một lỗi thường gặp

Không nên:

```python
for match in re.finditer(pattern, text):
    print(match.groupdict)
```

Bạn đang lấy **method object**.

Phải gọi:

```python
match.groupdict()
```

Tương tự:

```python
match.group()
match.groups()
match.start()
match.end()
match.span()
```

đều cần `()`.

---

# 29. `finditer()` với named group là combo rất mạnh

Tôi khuyên bạn hình thành thói quen:

```python
pattern = re.compile(
    r"...(?P<name>...)..."
)

for match in pattern.finditer(text):
    data = match.groupdict()
```

Sau này khi học:

```text
Parser
Crawler
HTML extraction
Log parser
Markdown parser
Document processing
```

cách này sẽ xuất hiện rất nhiều.

---

# 30. Bài tập

## Bài 1 — Tìm tất cả số

```python
text = "Python 3.12 was released in 2023"
```

Dùng:

```python
re.finditer(r"\d+", text)
```

in:

```text
value
start
end
span
```

Ví dụ:

```text
3 ...
12 ...
2023 ...
```

---

## Bài 2 — Tìm tất cả chapter

Cho:

```python
text = """
Chapter 001
Chapter 002
Chapter 003
"""
```

Dùng:

```python
re.finditer()
```

để in:

```text
001
002
003
```

---

# Bài 3 — Named groups

Cho:

```python
text = """
Chapter 001: Python
Chapter 002: Regex
Chapter 003: Asyncio
"""
```

Pattern:

```regex
Chapter\s+(?P<number>\d+):\s*(?P<title>.+)
```

Dùng `finditer()` và in:

```python
match.groupdict()
```

---

# Bài 4 — Position

Vẫn dữ liệu trên.

In:

```text
number
title
start
end
```

Ví dụ:

```text
001 | Python | 1 | 20
002 | Regex  | ...
```

Không cần đúng số trong ví dụ; hãy để Python tính.

---

# Bài 5 — Tạo parser

Viết:

```python
def parse_chapters(text: str) -> list[dict]:
    ...
```

Input:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
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
finditer()
+
named groups
+
groupdict()
```

---

# Challenge — Chapter Index

Hãy xây:

```python
def build_chapter_index(text: str) -> list[dict]:
    ...
```

Input:

```python
text = """
Introduction

Chapter 001: Vẫn là Tiêu Viêm

Lorem ipsum...

Chapter 002: Ba năm

Lorem ipsum...

Chapter 003: Vân Lam Tông

Lorem ipsum...
"""
```

Output:

```python
[
    {
        "number": "001",
        "title": "Vẫn là Tiêu Viêm",
        "start": ...,
        "end": ...,
    },
    ...
]
```

Yêu cầu:

```text
finditer()
     ↓
groupdict()
     ↓
start()
end()
```

Đây là bài rất tốt để chuyển từ **Regex cơ bản → Regex parser**.

---

# 31. Tổng kết Buổi 8

Ba API quan trọng nhất hiện tại:

```text
search()
    ↓
1 Match

findall()
    ↓
nhiều kết quả dạng list

finditer()
    ↓
nhiều Match objects
```

Trong đó `finditer()` đặc biệt mạnh:

```python
for match in re.finditer(pattern, text):
    match.group()
    match.groups()
    match.groupdict()
    match.start()
    match.end()
    match.span()
```

Nếu `findall()` thiên về:

```text
"Cho tôi dữ liệu"
```

thì `finditer()` thiên về:

```text
"Cho tôi từng Match để tôi xử lý nó"
```

### Mẫu code nên ghi nhớ

```python
import re

pattern = re.compile(
    r"Chapter\s+"
    r"(?P<number>\d+):\s*"
    r"(?P<title>.+)"
)

for match in pattern.finditer(text):
    data = match.groupdict()

    print(data)
    print(match.span())
```

**Buổi 9 — `re.split()`**: chúng ta sẽ chuyển từ việc **tìm pattern** sang **dùng Regex làm delimiter để chia text**. Đây là kỹ thuật rất hữu ích khi xử lý text không đồng nhất như whitespace, nhiều dấu phân cách, HTML/text extraction và dữ liệu crawler.
