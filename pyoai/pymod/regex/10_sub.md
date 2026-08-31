# Buổi 10 — `re.sub()` và `re.subn()`

Hôm nay chúng ta học một API cực kỳ quan trọng của `re`:

```python
re.sub()
re.subn()
```

Nếu các buổi trước:

```text
search()     → tìm 1 match
findall()    → lấy tất cả kết quả
finditer()   → lấy tất cả Match
split()      → chia text
```

thì:

```text
sub()        → tìm + thay thế
subn()       → tìm + thay thế + đếm số lần
```

Đây là kỹ thuật bạn sẽ dùng rất nhiều khi làm:

* Text cleaning
* HTML cleaning
* Markdown normalization
* Crawler
* Parser
* Log processing
* Data normalization

---

# 1. `re.sub()` cơ bản

Cú pháp:

```python
re.sub(pattern, repl, string)
```

Ví dụ:

```python
import re

text = "Python 123 Regex 456"

result = re.sub(
    r"\d+",
    "NUMBER",
    text,
)

print(result)
```

Kết quả:

```text
Python NUMBER Regex NUMBER
```

Regex:

```regex
\d+
```

tìm:

```text
123
456
```

Sau đó thay bằng:

```text
NUMBER
```

---

# 2. Tư duy của `sub()`

Có thể hình dung:

```text
text
 │
 ▼
Regex tìm match
 │
 ▼
123
456
 │
 ▼
replace
 │
 ▼
NUMBER
NUMBER
```

Ví dụ:

```python
re.sub(r"\d+", "X", "abc123 xyz456")
```

→

```text
abcX xyzX
```

---

# 3. `re.sub()` không sửa string gốc

Python `str` là immutable.

```python
import re

text = "Python 123"

re.sub(r"\d+", "X", text)

print(text)
```

Vẫn là:

```text
Python 123
```

Phải gán kết quả:

```python
text = re.sub(
    r"\d+",
    "X",
    text,
)
```

---

# 4. Thay thế ký tự

Ví dụ loại bỏ dấu `-`:

```python
import re

text = "2026-08-31"

result = re.sub(
    r"-",
    "/",
    text,
)

print(result)
```

→

```text
2026/08/31
```

---

# 5. Xóa bằng replacement rỗng

Một kỹ thuật cực kỳ phổ biến:

```python
re.sub(pattern, "", text)
```

Ví dụ xóa số:

```python
import re

text = "Python 123 Regex 456"

result = re.sub(
    r"\d+",
    "",
    text,
)

print(result)
```

→

```text
Python  Regex
```

Regex tìm cái gì thì xóa cái đó.

---

# 6. Xóa HTML tag

Đây là ví dụ gần với công việc crawler.

```python
import re

html = "<p>Hello <b>Python</b></p>"

text = re.sub(
    r"<[^>]+>",
    "",
    html,
)

print(text)
```

Kết quả:

```text
Hello Python
```

Regex:

```regex
<[^>]+>
```

tìm các đoạn:

```html
<p>
<b>
</b>
</p>
```

rồi thay bằng:

```text
""
```

### Nhưng lưu ý

Regex kiểu này chỉ phù hợp cho HTML rất đơn giản. **Không nên dùng Regex làm HTML parser tổng quát**; với HTML thực tế nên dùng BeautifulSoup, selectolax, lxml hoặc parser chuyên dụng.

---

# 7. Chuẩn hóa nhiều whitespace

Một ứng dụng cực kỳ quan trọng:

```python
import re

text = "Python    Regex\t\tAsyncio\nPySide6"

result = re.sub(
    r"\s+",
    " ",
    text,
)

print(result)
```

Kết quả:

```text
Python Regex Asyncio PySide6
```

Ta đã biến:

```text
space
tab
newline
nhiều whitespace
```

thành:

```text
một space
```

---

# 8. Đây là một pattern rất đáng nhớ

```python
re.sub(r"\s+", " ", text)
```

Nó thường xuất hiện trong:

```text
text cleaning
normalization
crawler
parser
search indexing
```

---

# 9. Xóa whitespace đầu/cuối

Có thể dùng:

```python
text.strip()
```

thay vì Regex.

Ví dụ:

```python
text = text.strip()
```

Không nên dùng Regex nếu Python đã có API đơn giản hơn.

Nguyên tắc:

> Regex nên được dùng khi pattern thực sự có cấu trúc.

---

# 10. `sub()` với capturing group

Đây là phần rất quan trọng.

Ví dụ:

```python
import re

text = "2026-08-31"

result = re.sub(
    r"(\d{4})-(\d{2})-(\d{2})",
    r"\3/\2/\1",
    text,
)

print(result)
```

Kết quả:

```text
31/08/2026
```

Ta có:

```text
(\d{4}) → 2026 → group 1
(\d{2}) → 08   → group 2
(\d{2}) → 31   → group 3
```

Replacement:

```text
\3/\2/\1
```

→

```text
31/08/2026
```

---

# 11. Backreference trong replacement

Đây là khái niệm quan trọng:

```text
Regex:
(...)
(...)
(...)

Replacement:
\1
\2
\3
```

Ví dụ:

```python
re.sub(
    r"(\w+)\s+(\w+)",
    r"\2 \1",
    "Hello Python",
)
```

Kết quả:

```text
Python Hello
```

Regex:

```text
(\w+) → Hello
(\w+) → Python
```

Replacement:

```text
\2 \1
```

→

```text
Python Hello
```

---

# 12. Named group trong `sub()`

Với Regex phức tạp, named group dễ đọc hơn.

```python
import re

text = "2026-08-31"

pattern = (
    r"(?P<year>\d{4})-"
    r"(?P<month>\d{2})-"
    r"(?P<day>\d{2})"
)

result = re.sub(
    pattern,
    r"\g<day>/\g<month>/\g<year>",
    text,
)

print(result)
```

→

```text
31/08/2026
```

Dùng:

```text
\g<year>
\g<month>
\g<day>
```

thay vì:

```text
\1
\2
\3
```

---

# 13. Vì sao nên dùng `\g<name>`?

Ví dụ:

```python
r"\1"
```

khó đọc khi Regex lớn.

Trong khi:

```python
r"\g<day>/\g<month>/\g<year>"
```

rõ nghĩa ngay lập tức.

Với parser production-style:

> Named groups thường dễ bảo trì hơn numbered groups.

---

# 14. `sub()` với function

Đây là phần **rất quan trọng**.

Replacement không nhất thiết phải là string.

Ta có thể truyền một function:

```python
re.sub(pattern, function, text)
```

Ví dụ:

```python
import re

def replace_number(match):
    return str(int(match.group()) * 2)

text = "10 20 30"

result = re.sub(
    r"\d+",
    replace_number,
    text,
)

print(result)
```

Kết quả:

```text
20 40 60
```

---

# 15. Function nhận `Match`

Function:

```python
def replace_number(match):
    ...
```

`match` chính là:

```python
re.Match
```

Do đó bạn có thể dùng:

```python
match.group()
match.start()
match.end()
match.groups()
match.groupdict()
```

Ví dụ:

```python
import re

def replace_number(match):
    value = match.group()
    return f"[{value}]"

text = "Python 123 Regex 456"

result = re.sub(
    r"\d+",
    replace_number,
    text,
)

print(result)
```

→

```text
Python [123] Regex [456]
```

---

# 16. Đây là sức mạnh lớn của `sub()`

Với replacement string:

```python
re.sub(
    r"\d+",
    "NUMBER",
    text,
)
```

mọi match đều nhận cùng một replacement.

Nhưng function:

```python
re.sub(
    r"\d+",
    replace_number,
    text,
)
```

cho phép:

```text
match
 ↓
Python function
 ↓
tính toán
 ↓
replacement riêng
```

---

# 17. Ví dụ: đánh số chapter

Input:

```python
text = """
Chapter 1
Chapter 2
Chapter 3
"""
```

Ta có thể:

```python
import re

def normalize_chapter(match):
    number = int(match.group(1))
    return f"Chapter {number:03d}"

result = re.sub(
    r"Chapter\s+(\d+)",
    normalize_chapter,
    text,
)

print(result)
```

Kết quả:

```text
Chapter 001
Chapter 002
Chapter 003
```

Đây là ví dụ rất thực tế.

---

# 18. Named group + function

Ví dụ:

```python
import re

text = """
Chapter 1: Python
Chapter 2: Regex
"""

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+)"
)

def normalize(match):
    number = int(match.group("number"))
    return f"Chapter {number:03d}"

result = re.sub(
    pattern,
    normalize,
    text,
)

print(result)
```

→

```text
Chapter 001: Python
Chapter 002: Regex
```

---

# 19. `count`

`re.sub()` có parameter:

```python
count
```

Ví dụ:

```python
import re

text = "123 456 789"

result = re.sub(
    r"\d+",
    "X",
    text,
    count=2,
)

print(result)
```

→

```text
X X 789
```

Chỉ thay **2 match đầu tiên**.

---

# 20. `count=1`

Rất hữu ích khi chỉ muốn thay lần đầu.

```python
text = "Python Python Python"

result = re.sub(
    r"Python",
    "Regex",
    text,
    count=1,
)

print(result)
```

→

```text
Regex Python Python
```

---

# 21. `count=0`

Mặc định:

```python
count=0
```

nghĩa là:

> thay tất cả match.

```python
re.sub(
    r"Python",
    "Regex",
    text,
    count=0,
)
```

---

# 22. `re.subn()`

`subn()` gần giống `sub()` nhưng trả về **2 giá trị**:

```python
(
    new_string,
    number_of_replacements
)
```

Ví dụ:

```python
import re

text = "Python 123 Regex 456"

result = re.subn(
    r"\d+",
    "NUMBER",
    text,
)

print(result)
```

Kết quả:

```python
('Python NUMBER Regex NUMBER', 2)
```

---

# 23. Unpack `subn()`

Thường viết:

```python
new_text, count = re.subn(
    r"\d+",
    "NUMBER",
    text,
)

print(new_text)
print(count)
```

Output:

```text
Python NUMBER Regex NUMBER
2
```

---

# 24. Khi nào dùng `subn()`?

Khi bạn cần biết:

```text
đã thay bao nhiêu lần?
```

Ví dụ validation:

```python
new_text, count = re.subn(
    r"<script.*?</script>",
    "",
    html,
)
```

Sau đó:

```python
print("Removed:", count)
```

Có thể biết:

```text
Removed: 3
```

Điều này hữu ích cho logging/debugging pipeline.

---

# 25. `sub()` vs `subn()`

| API         | Kết quả           |
| ----------- | ----------------- |
| `re.sub()`  | string            |
| `re.subn()` | `(string, count)` |

Ví dụ:

```python
re.sub(...)
```

→

```python
"abc"
```

Trong khi:

```python
re.subn(...)
```

→

```python
("abc", 3)
```

---

# 26. `sub()` với `\b`

Ví dụ chỉ muốn thay từ `Python` hoàn chỉnh.

```python
import re

text = "Python Pythonista Python"

result = re.sub(
    r"\bPython\b",
    "Regex",
    text,
)

print(result)
```

Kết quả:

```text
Regex Pythonista Regex
```

`Pythonista` không bị thay.

Vì:

```regex
\b
```

xác định word boundary.

---

# 27. Xóa comment

Ví dụ đơn giản:

```python
import re

text = """
Python code
# comment
Regex code
# another comment
"""

result = re.sub(
    r"(?m)^\s*#.*$",
    "",
    text,
)

print(result)
```

Pattern:

```regex
(?m)^
```

→ bắt đầu mỗi dòng.

```regex
#.*
```

→ comment.

```regex
$
```

→ cuối dòng.

---

# 28. Xóa dòng trống

Sau khi cleaning:

```python
text = re.sub(
    r"\n\s*\n+",
    "\n\n",
    text,
)
```

Có thể dùng để chuẩn hóa nhiều blank lines.

Ví dụ:

```text
A



B



C
```

→

```text
A

B

C
```

---

# 29. Text normalization pipeline

Đây là một ví dụ rất thực tế:

```python
import re


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text
```

Input:

```text
"   Python    Regex \n Asyncio   "
```

Output:

```text
"Python Regex Asyncio"
```

---

# 30. Pipeline phức tạp hơn

Ví dụ:

```python
import re


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
```

Ta đang làm:

```text
CRLF
 ↓
LF

spaces/tabs
 ↓
1 space

3+ newline
 ↓
2 newline

strip
 ↓
clean text
```

Đây chính là kiểu pipeline thường gặp khi xử lý dữ liệu crawl.

---

# 31. Một ví dụ crawler

Giả sử crawler lấy được:

```python
html = """
<div>
    <p>Hello</p>
    <script>alert("x")</script>
    <p>Python</p>
</div>
"""
```

Có thể có một pipeline:

```text
HTML
 ↓
remove unwanted elements
 ↓
extract text
 ↓
normalize whitespace
 ↓
normalize newlines
 ↓
clean text
```

Ví dụ với text đã extract:

```python
text = re.sub(r"[ \t]+", " ", text)
text = re.sub(r"\n{3,}", "\n\n", text)
text = text.strip()
```

Lưu ý: **xóa `<script>`, `<style>`, quảng cáo HTML** nên ưu tiên DOM parser như BeautifulSoup/selectolax trước khi dùng Regex để normalize text.

---

# 32. Một lỗi rất thường gặp

Không nên viết:

```python
re.sub(
    r"\d+",
    123,
    text,
)
```

`repl` dạng string phải là string, hoặc callable.

Đúng:

```python
re.sub(
    r"\d+",
    "123",
    text,
)
```

hoặc:

```python
def replace(match):
    return "123"

re.sub(
    r"\d+",
    replace,
    text,
)
```

---

# 33. Một lỗi khác: escape replacement

Nếu muốn replacement chứa backslash, cần cẩn thận vì replacement string có cú pháp riêng.

Ví dụ:

```python
r"\1"
```

không phải text literal `\1`; nó có thể được hiểu là backreference.

Vì vậy với replacement phức tạp, function thường rõ ràng hơn:

```python
def replace(match):
    return r"\1"
```

---

# 34. Pattern + function = mini transformation engine

Bạn có thể nghĩ:

```text
Regex
 ↓
Match
 ↓
Function
 ↓
New text
```

Ví dụ:

```python
def transform(match):
    data = match.groupdict()

    ...
    
    return replacement
```

Đây chính là nền tảng cho nhiều text transformation tool.

---

# 35. Ví dụ nâng cao: chuẩn hóa URL

Input:

```python
text = """
https://example.com/
https://example.com////
"""
```

Ta có thể:

```python
import re

text = re.sub(
    r"/{2,}",
    "/",
    text,
)
```

Nhưng cẩn thận:

```text
https://
```

cũng chứa `//`.

Nếu làm trực tiếp như trên sẽ phá URL:

```text
https:/example.com/
```

Đây là bài học quan trọng:

> Regex phải xét **context**, không chỉ xét pattern cục bộ.

---

# 36. Dùng negative lookbehind

Có thể xử lý trường hợp trên bằng Regex phức tạp hơn:

```python
text = re.sub(
    r"(?<!:)//+",
    "/",
    text,
)
```

Ý tưởng:

```regex
(?<!:)
```

không cho phép match bắt đầu ngay sau `:`.

Do đó:

```text
https://
```

không bị xử lý theo cách đó.

Đây là ví dụ cho thấy `sub()` kết hợp với **lookaround** rất mạnh.

---

# 37. `sub()` + compiled pattern

Từ buổi sau chúng ta sẽ học:

```python
pattern = re.compile(...)
```

Sau đó:

```python
pattern.sub(...)
```

Ví dụ:

```python
pattern = re.compile(r"\d+")

result = pattern.sub(
    "NUMBER",
    text,
)
```

Tư duy:

```text
re.sub(pattern, ...)
```

vs:

```text
compiled_pattern.sub(...)
```

Đây sẽ là nội dung Buổi 11.

---

# 38. Bài tập

## Bài 1 — Thay số

Cho:

```python
text = "Python 123 Regex 456"
```

Dùng:

```python
re.sub()
```

để biến thành:

```text
Python NUMBER Regex NUMBER
```

---

## Bài 2 — Xóa số

Input:

```text
Python 123 Regex 456
```

Output:

```text
Python  Regex
```

---

## Bài 3 — Chuẩn hóa whitespace

Input:

```python
text = "Python    Regex\t\tAsyncio\nPySide6"
```

Output:

```text
Python Regex Asyncio PySide6
```

---

## Bài 4 — Đổi format ngày

Input:

```python
text = "2026-08-31"
```

Output:

```text
31/08/2026
```

Yêu cầu dùng capturing groups:

```regex
(\d{4})-(\d{2})-(\d{2})
```

---

## Bài 5 — `count`

Input:

```python
text = "Python Python Python"
```

Chỉ thay Python đầu tiên:

```text
Regex Python Python
```

---

## Bài 6 — Function replacement

Cho:

```python
text = "10 20 30 40"
```

Dùng `re.sub()` + function để nhân tất cả số với `10`.

Kết quả:

```text
100 200 300 400
```

Gợi ý:

```python
def multiply(match):
    value = int(match.group())
    return str(value * 10)
```

---

# Bài 7 — `subn()`

Cho:

```python
text = "Python Python Python"
```

Dùng:

```python
re.subn()
```

để thay `Python` thành `Regex`.

Kết quả cần lấy được:

```python
(
    "Regex Regex Regex",
    3,
)
```

---

# Challenge — Text Cleaner

Viết:

```python
def clean_text(text: str) -> str:
    ...
```

Input:

```python
text = """
    Python     Regex


    Asyncio\t\tPySide6



"""
```

Yêu cầu:

### Bước 1

Chuẩn hóa CRLF:

```python
\r\n?
```

thành:

```text
\n
```

### Bước 2

Chuẩn hóa spaces/tabs:

```regex
[ \t]+
```

→ một space.

### Bước 3

Chuẩn hóa quá nhiều newline:

```regex
\n{3,}
```

→ `\n\n`.

### Bước 4

```python
strip()
```

Kết quả mong muốn:

```text
Python Regex

Asyncio PySide6
```

---

# Challenge 2 — Chapter Normalizer

Cho:

```python
text = """
Chapter 1: Python
Chapter 2: Regex
Chapter 10: Asyncio
"""
```

Viết:

```python
def normalize_chapters(text: str) -> str:
    ...
```

để biến thành:

```text
Chapter 001: Python
Chapter 002: Regex
Chapter 010: Asyncio
```

Gợi ý:

```python
pattern = r"Chapter\s+(?P<number>\d+)"
```

và replacement phải là **function**.

---

# Tổng kết Buổi 10

Bạn cần nắm chắc 5 kỹ thuật:

### 1. Replace

```python
re.sub(
    r"\d+",
    "NUMBER",
    text,
)
```

### 2. Delete

```python
re.sub(
    r"\d+",
    "",
    text,
)
```

### 3. Backreference

```python
re.sub(
    r"(\d{4})-(\d{2})-(\d{2})",
    r"\3/\2/\1",
    text,
)
```

### 4. Function replacement

```python
re.sub(
    r"\d+",
    replace_function,
    text,
)
```

### 5. `subn()`

```python
new_text, count = re.subn(
    pattern,
    replacement,
    text,
)
```

Hãy đặc biệt nhớ mô hình:

```text
                 re.sub()
                    │
          ┌─────────┴─────────┐
          │                   │
      replacement         function
          │                   │
      string cố định      Match object
                              │
                              ▼
                         xử lý logic
                              │
                              ▼
                         replacement
```

Với những gì bạn đã học từ **Buổi 6 → 10**, bạn đã có gần như toàn bộ nhóm API thao tác Regex cơ bản:

```text
search()
match()
fullmatch()
findall()
finditer()
split()
sub()
subn()
```

**Buổi 11 — Compiled Regex (`re.compile()`)** sẽ chuyển chúng ta từ cách dùng Regex đơn lẻ sang cách tổ chức Regex **có thể tái sử dụng trong parser/crawler**, đặc biệt quan trọng khi một pattern được dùng hàng trăm hoặc hàng nghìn lần.
