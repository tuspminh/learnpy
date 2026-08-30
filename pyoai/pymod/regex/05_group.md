# Buổi 5 — Groups trong Python `re`

Hôm nay chúng ta chuyển sang một cấp độ quan trọng hơn:

> Không chỉ **tìm thấy** một chuỗi, mà còn **tách các phần dữ liệu bên trong chuỗi**.

Ví dụ:

```text
Chapter 123: Tam Niên Chi Ước
```

Ta muốn lấy riêng:

```text
chapter = 123
title   = "Tam Niên Chi Ước"
```

Đây chính là nhiệm vụ của **Regex Groups**.

---

# 1. Vì sao cần Group?

Giả sử:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

match = re.search(
    r"Chapter\s+\d+",
    text
)

print(match.group())
```

Kết quả:

```text
Chapter 123
```

Nhưng chúng ta muốn:

```python
chapter = "123"
```

Regex cần biết:

> Phần nào của pattern là dữ liệu tôi muốn lấy?

Ta dùng:

```regex
(...)
```

---

# 2. Capturing Group `( )`

Ví dụ:

```python
import re

text = "Chapter 123"

match = re.search(
    r"Chapter\s+(\d+)",
    text
)

print(match.group())
print(match.group(1))
```

Kết quả:

```text
Chapter 123
123
```

Pattern:

```regex
Chapter\s+(\d+)
             ^^^^
             group 1
```

---

# 3. `group()` và `group(1)`

Đây là điểm cần nhớ.

```python
match.group()
```

hoặc:

```python
match.group(0)
```

→ toàn bộ phần match.

Trong khi:

```python
match.group(1)
```

→ group đầu tiên.

Ví dụ:

```python
import re

text = "Chapter 123"

match = re.search(r"Chapter\s+(\d+)", text)

print(match.group(0))
print(match.group(1))
```

Output:

```text
Chapter 123
123
```

Có thể nhớ:

```text
group(0) → toàn bộ match
group(1) → group đầu tiên
group(2) → group thứ hai
...
```

---

# 4. Nhiều Groups

Giả sử:

```text
Chapter 123: Tam Niên Chi Ước
```

Ta muốn:

```text
123
Tam Niên Chi Ước
```

Regex:

```regex
Chapter\s+(\d+):\s*(.+)
```

Code:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

match = re.search(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)

print(match.group(1))
print(match.group(2))
```

Kết quả:

```text
123
Tam Niên Chi Ước
```

---

# 5. Group được đánh số theo thứ tự

Ví dụ:

```regex
(\d+)-([A-Z]+)-(\w+)
```

Có 3 groups:

```text
(\d+)      → group 1
([A-Z]+)   → group 2
(\w+)      → group 3
```

Ví dụ:

```python
import re

text = "123-ABC-python"

match = re.search(
    r"(\d+)-([A-Z]+)-(\w+)",
    text
)

print(match.group(1))
print(match.group(2))
print(match.group(3))
```

Output:

```text
123
ABC
python
```

---

# 6. `groups()`

Thay vì lấy từng group:

```python
match.group(1)
match.group(2)
match.group(3)
```

có thể dùng:

```python
match.groups()
```

Ví dụ:

```python
import re

text = "123-ABC-python"

match = re.search(
    r"(\d+)-([A-Z]+)-(\w+)",
    text
)

print(match.groups())
```

Output:

```text
('123', 'ABC', 'python')
```

Lưu ý:

```python
match.groups()
```

**không bao gồm group 0**.

Nó chỉ trả về các capturing groups.

---

# 7. Group + Character Class

Ví dụ:

```text
User: admin
```

Regex:

```regex
User:\s*(\w+)
```

Code:

```python
import re

text = "User: admin"

match = re.search(
    r"User:\s*(\w+)",
    text
)

print(match.group(1))
```

Output:

```text
admin
```

---

# 8. Group + Quantifier

Điều này rất quan trọng.

Regex:

```regex
(\d+)
```

`+` áp dụng cho:

```regex
\d
```

bên trong group.

Nó lấy:

```text
12345
```

thành một group duy nhất.

---

# 9. Group không làm Regex lặp

Một hiểu nhầm phổ biến:

```regex
(\d)+
```

không giống:

```regex
(\d+)
```

### `(\d+)`

Có nghĩa:

> Một hoặc nhiều digit được gom thành **một group**.

Ví dụ:

```text
12345
```

Group 1:

```text
12345
```

---

### `(\d)+`

Có nghĩa:

> Match một hoặc nhiều lần group `(\d)`.

Ví dụ:

```text
12345
```

Regex vẫn match toàn bộ, nhưng capturing group chỉ lưu **lần capture cuối cùng**.

Ví dụ:

```python
import re

match = re.search(r"(\d)+", "12345")

print(match.group())
print(match.group(1))
```

Kết quả:

```text
12345
5
```

Đây là điểm rất quan trọng.

Thông thường nếu muốn lấy toàn bộ số:

```regex
(\d+)
```

chứ không phải:

```regex
(\d)+
```

---

# 10. Group để trích xuất dữ liệu

Đây là cách tư duy bạn nên hình thành:

```text
Input
   ↓
Regex
   ↓
Groups
   ↓
Structured Data
```

Ví dụ:

```text
Chapter 123: Tam Niên Chi Ước
```

Regex:

```regex
Chapter\s+(\d+):\s*(.+)
```

Sau đó:

```python
chapter = match.group(1)
title = match.group(2)
```

Ta đã biến text thành dữ liệu có cấu trúc.

---

# 11. Named Group

Khi Regex lớn lên, dùng:

```python
match.group(1)
match.group(2)
match.group(3)
```

sẽ rất khó đọc.

Python cho phép đặt tên group.

Cú pháp:

```regex
(?P<name>...)
```

Ví dụ:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

pattern = (
    r"Chapter\s+"
    r"(?P<chapter>\d+)"
    r":\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

print(match.group("chapter"))
print(match.group("title"))
```

Output:

```text
123
Tam Niên Chi Ước
```

Đây là cách tôi khuyên bạn sử dụng khi Regex bắt đầu phức tạp.

---

# 12. `groupdict()`

Named groups còn có một API rất hay:

```python
match.groupdict()
```

Ví dụ:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

pattern = (
    r"Chapter\s+"
    r"(?P<chapter>\d+)"
    r":\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

print(match.groupdict())
```

Output:

```python
{
    'chapter': '123',
    'title': 'Tam Niên Chi Ước'
}
```

Đây chính là dạng dữ liệu cực kỳ tiện cho parser.

---

# 13. Từ Regex → Dictionary

Ví dụ:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

pattern = (
    r"Chapter\s+"
    r"(?P<chapter>\d+)"
    r":\s*"
    r"(?P<title>.+)"
)

match = re.search(pattern, text)

if match:
    data = match.groupdict()
    print(data)
```

Kết quả:

```python
{
    "chapter": "123",
    "title": "Tam Niên Chi Ước",
}
```

Đây là pattern rất hữu ích trong crawler.

---

# 14. Chuyển kiểu dữ liệu

Regex luôn trả về **string**.

Ví dụ:

```python
data = match.groupdict()

print(type(data["chapter"]))
```

→

```text
<class 'str'>
```

Nếu muốn integer:

```python
data["chapter"] = int(data["chapter"])
```

Bây giờ:

```python
{
    "chapter": 123,
    "title": "Tam Niên Chi Ước",
}
```

Regex chịu trách nhiệm:

```text
extract
```

Business logic chịu trách nhiệm:

```text
convert / validate / normalize
```

Đây là cách thiết kế sạch hơn.

---

# 15. Named Group trong parser

Ví dụ crawler lấy:

```text
Story: Đấu Phá Thương Khung
Author: Thiên Tằm Thổ Đậu
Chapter: 123
```

Ta có thể viết:

```python
import re

text = """
Story: Đấu Phá Thương Khung
Author: Thiên Tằm Thổ Đậu
Chapter: 123
"""

pattern = (
    r"Story:\s*(?P<story>.+)\n"
    r"Author:\s*(?P<author>.+)\n"
    r"Chapter:\s*(?P<chapter>\d+)"
)

match = re.search(pattern, text)

if match:
    print(match.groupdict())
```

Có thể nhận:

```python
{
    "story": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "chapter": "123",
}
```

---

# 16. Non-Capturing Group `(?:...)`

Có một loại group khác:

```regex
(?:...)
```

Nó gọi là **non-capturing group**.

Ví dụ:

```regex
(?:Chapter|Chương)\s+\d+
```

Nó cho phép gom pattern lại nhưng **không tạo group**.

---

# 17. Vì sao cần Non-Capturing Group?

Giả sử:

```regex
(Chapter|Chương)\s+(\d+)
```

Ta có:

```text
group 1 → Chapter
group 2 → 123
```

Nếu chúng ta không cần lấy `"Chapter"` mà chỉ muốn group số:

```regex
(?:Chapter|Chương)\s+(\d+)
```

thì:

```text
group 1 → 123
```

Điều này rất hữu ích.

---

# 18. So sánh

### Capturing

```regex
(Chapter|Chương)\s+(\d+)
```

```python
match.groups()
```

→

```python
("Chapter", "123")
```

### Non-capturing

```regex
(?:Chapter|Chương)\s+(\d+)
```

```python
match.groups()
```

→

```python
("123",)
```

---

# 19. Quy tắc thực tế

Một nguyên tắc tốt:

> Chỉ dùng capturing group khi bạn thực sự muốn lấy dữ liệu.

Nếu chỉ cần grouping để điều khiển Regex:

```regex
(?:...)
```

Ví dụ:

```regex
(?:Chapter|Chương)\s+(?P<number>\d+)
```

Rất rõ ràng:

```text
(?:Chapter|Chương)
        ↓
chỉ grouping

(?P<number>\d+)
        ↓
dữ liệu cần lấy
```

---

# 20. Named Group + Alternation

Ví dụ website có:

```text
Chapter 123
Chương 124
```

Ta có thể:

```python
import re

pattern = (
    r"(?:Chapter|Chương)\s+"
    r"(?P<number>\d+)"
)

for text in ["Chapter 123", "Chương 124"]:
    match = re.search(pattern, text)

    if match:
        print(match.groupdict())
```

Output:

```text
{'number': '123'}
{'number': '124'}
```

Rất tiện cho crawler đa website.

---

# 21. Group với `findall()`

Đây là phần rất quan trọng.

Cho:

```python
import re

text = """
Chapter 1
Chapter 2
Chapter 3
"""
```

Nếu:

```python
matches = re.findall(
    r"Chapter\s+(\d+)",
    text
)

print(matches)
```

Output:

```python
['1', '2', '3']
```

Khi Regex có **một capturing group**, `findall()` trả về danh sách giá trị group đó.

---

# 22. `findall()` với nhiều Groups

Ví dụ:

```python
import re

text = """
Chapter 1: Intro
Chapter 2: Python
Chapter 3: Regex
"""

matches = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)

print(matches)
```

Output:

```python
[
    ('1', 'Intro'),
    ('2', 'Python'),
    ('3', 'Regex')
]
```

Tức là:

```text
mỗi match
    ↓
tuple
    ↓
(group1, group2)
```

---

# 23. Named Group + `finditer()`

Khi parser phức tạp, tôi thường thích:

```python
re.finditer()
```

Ví dụ:

```python
import re

text = """
Chapter 1: Intro
Chapter 2: Python
Chapter 3: Regex
"""

pattern = (
    r"Chapter\s+"
    r"(?P<number>\d+)"
    r":\s*"
    r"(?P<title>.+)"
)

for match in re.finditer(pattern, text):
    print(match.groupdict())
```

Output:

```python
{'number': '1', 'title': 'Intro'}
{'number': '2', 'title': 'Python'}
{'number': '3', 'title': 'Regex'}
```

Đây là cách rất đẹp để xây parser.

---

# 24. Một parser mini

Ta có:

```python
import re


CHAPTER_PATTERN = re.compile(
    r"Chapter\s+"
    r"(?P<number>\d+)"
    r":\s*"
    r"(?P<title>.+)"
)


def parse_chapters(text: str) -> list[dict[str, str]]:
    return [
        match.groupdict()
        for match in CHAPTER_PATTERN.finditer(text)
    ]
```

Input:

```python
text = """
Chapter 1: Intro
Chapter 2: Python
Chapter 3: Regex
"""

print(parse_chapters(text))
```

Output:

```python
[
    {"number": "1", "title": "Intro"},
    {"number": "2", "title": "Python"},
    {"number": "3", "title": "Regex"},
]
```

Đây đã bắt đầu giống một **parser component** thực tế.

---

# 25. Group và Backreference

Group còn có một công dụng khác:

> Tham chiếu lại nội dung đã match.

Ví dụ:

```regex
(\w+)\s+\1
```

Ý nghĩa:

```text
(\w+)
   ↓
lấy một word

\1
   ↓
phải xuất hiện lại chính word đó
```

Nó có thể tìm:

```text
hello hello
test test
Python Python
```

Ví dụ:

```python
import re

text = "hello hello"

match = re.search(r"(\w+)\s+\1", text)

print(match.group())
```

Output:

```text
hello hello
```

Backreference chúng ta sẽ đào sâu ở phần Regex nâng cao.

---

# 26. Named Backreference

Nếu group là:

```regex
(?P<word>\w+)
```

có thể tham chiếu:

```regex
(?P=word)
```

Ví dụ:

```regex
(?P<word>\w+)\s+(?P=word)
```

Tức là:

```text
word
+
chính xác lại word đó
```

---

# 27. Một lỗi rất thường gặp

Đừng viết:

```python
match.group("chapter")
```

nếu Regex không có:

```regex
(?P<chapter>...)
```

Ví dụ:

```python
match = re.search(r"Chapter\s+(\d+)", text)
```

thì phải:

```python
match.group(1)
```

Không phải:

```python
match.group("chapter")
```

Muốn dùng tên:

```python
match = re.search(
    r"Chapter\s+(?P<chapter>\d+)",
    text
)
```

sau đó:

```python
match.group("chapter")
```

---

# 28. Kiến trúc tư duy hôm nay

Bạn nên hình dung:

```text
Regex
 │
 ├── Matching
 │
 └── Groups
       │
       ├── Capturing
       │      └── (...)
       │
       ├── Named
       │      └── (?P<name>...)
       │
       └── Non-capturing
              └── (?:...)
```

Và API:

```text
group()
group(1)
group("name")
groups()
groupdict()
```

---

# 29. Cheat Sheet

### Capturing

```regex
(...)
```

### Named capturing

```regex
(?P<name>...)
```

### Non-capturing

```regex
(?:...)
```

### Toàn bộ match

```python
match.group()
```

### Group theo số

```python
match.group(1)
```

### Group theo tên

```python
match.group("name")
```

### Tất cả groups

```python
match.groups()
```

### Named groups thành dictionary

```python
match.groupdict()
```

---

# 30. Bài tập Buổi 5

## Bài 1

Cho:

```python
text = "User: admin"
```

Viết Regex để lấy:

```text
admin
```

---

## Bài 2

Cho:

```python
text = "Chapter 123"
```

Dùng capturing group để lấy:

```text
123
```

---

## Bài 3

Cho:

```python
text = "Chapter 123: Tam Niên Chi Ước"
```

Lấy:

```python
{
    "number": "123",
    "title": "Tam Niên Chi Ước"
}
```

**Bắt buộc dùng named group.**

---

## Bài 4

Cho:

```python
text = """
Chapter 1: Intro
Chapter 2: Python
Chapter 3: Regex
"""
```

Dùng `finditer()` + named groups để tạo:

```python
[
    {"number": "1", "title": "Intro"},
    {"number": "2", "title": "Python"},
    {"number": "3", "title": "Regex"},
]
```

---

# Challenge — Parser truyện

Đây là bài tôi khuyên bạn tự làm kỹ.

Input:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
```

Viết:

```python
def parse_chapters(text: str) -> list[dict]:
    ...
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

Gợi ý pattern:

```regex
Chapter\s+(?P<number>\d+):\s*(?P<title>.+)
```

và sử dụng:

```python
re.finditer()
```

---

## Challenge 2 — Website không thống nhất

Hãy xử lý cả:

```text
Chapter 001: Vẫn là Tiêu Viêm
Chương 002: Ba năm
Chapter: 003: Vân Lam Tông
```

Mục tiêu:

```python
[
    {"number": "001", "title": "Vẫn là Tiêu Viêm"},
    {"number": "002", "title": "Ba năm"},
    {"number": "003", "title": "Vân Lam Tông"},
]
```

Ở bài này bạn sẽ phải kết hợp:

```text
Alternation
    +
Non-capturing Group
    +
Named Group
    +
Quantifier
    +
Whitespace
```

Đây chính là kiểu Regex mà bạn sẽ gặp khi xây **crawler/parser đa website**.

**Buổi 6** chúng ta sẽ đi sâu vào `re.search()` vs `re.match()` vs `re.fullmatch()` và cách lựa chọn API đúng trong **extraction, validation và parser**, sau đó bắt đầu `findall()`/`finditer()` một cách bài bản.
