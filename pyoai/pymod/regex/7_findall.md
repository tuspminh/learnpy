# Buổi 7 — `re.findall()`

Ở Buổi 6, bạn đã học:

```python
re.search()
re.match()
re.fullmatch()
```

Điểm chung của chúng là chúng ta thường làm việc với **một kết quả match**.

Hôm nay học:

```python
re.findall()
```

Mục tiêu:

> **Tìm tất cả các phần khớp Regex và trả về dữ liệu dưới dạng list.**

Đây là API cực kỳ hữu ích khi xây **parser/crawler**.

---

# 1. `findall()` là gì?

Cú pháp:

```python
re.findall(pattern, string)
```

Ví dụ:

```python
import re

text = "Chapter 1 Chapter 2 Chapter 3"

result = re.findall(r"Chapter", text)

print(result)
```

Kết quả:

```text
['Chapter', 'Chapter', 'Chapter']
```

`search()` chỉ lấy match đầu tiên:

```python
match = re.search(r"Chapter", text)

print(match.group())
```

→

```text
Chapter
```

Còn:

```python
re.findall()
```

→ lấy **tất cả**.

---

# 2. Ví dụ đơn giản

Tìm tất cả số:

```python
import re

text = "Python 3.12 was released in 2023"

numbers = re.findall(r"\d+", text)

print(numbers)
```

Kết quả:

```python
['3', '12', '2023']
```

Regex:

```regex
\d+
```

match:

```text
3
12
2023
```

---

# 3. `findall()` luôn trả về list

Ví dụ:

```python
import re

result = re.findall(r"\d+", "abc123xyz456")

print(type(result))
print(result)
```

Kết quả:

```text
<class 'list'>
['123', '456']
```

Nếu không tìm thấy:

```python
result = re.findall(r"\d+", "abcdef")

print(result)
```

→

```python
[]
```

Không phải:

```python
None
```

Điểm này khác `search()`.

---

# 4. So sánh `search()` và `findall()`

```python
import re

text = "ID: 123, ID: 456, ID: 789"

match = re.search(r"\d+", text)

print(match.group())
```

→

```text
123
```

Trong khi:

```python
ids = re.findall(r"\d+", text)

print(ids)
```

→

```python
['123', '456', '789']
```

Có thể nhớ:

```text
search()
    ↓
first match

findall()
    ↓
all matches
```

---

# 5. `findall()` với Capturing Group

Đây là phần **rất quan trọng**.

Cho:

```python
text = "Chapter 1 Chapter 2 Chapter 3"
```

Ta viết:

```python
result = re.findall(
    r"Chapter\s+(\d+)",
    text
)

print(result)
```

Kết quả:

```python
['1', '2', '3']
```

Không phải:

```python
[
    'Chapter 1',
    'Chapter 2',
    'Chapter 3'
]
```

Tại sao?

Vì Regex có **một capturing group**:

```regex
Chapter\s+(\d+)
             ^^^^
             group 1
```

`findall()` trả về **nội dung của group**.

---

# 6. Không có Group vs Có Group

### Không có group

```python
import re

text = "Chapter 1 Chapter 2"

print(re.findall(r"Chapter\s+\d+", text))
```

Kết quả:

```python
['Chapter 1', 'Chapter 2']
```

### Có group

```python
print(
    re.findall(
        r"Chapter\s+(\d+)",
        text
    )
)
```

Kết quả:

```python
['1', '2']
```

Đây là một quy tắc quan trọng:

```text
Không có capturing group
    ↓
findall() → toàn bộ match

Có 1 capturing group
    ↓
findall() → nội dung group đó
```

---

# 7. Hai capturing groups

Ví dụ:

```python
import re

text = """
Chapter 1: Intro
Chapter 2: Python
Chapter 3: Regex
"""

result = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)

print(result)
```

Kết quả:

```python
[
    ('1', 'Intro'),
    ('2', 'Python'),
    ('3', 'Regex')
]
```

Vì có **2 capturing groups**:

```regex
Chapter\s+(\d+):\s*(.+)
             │         │
             │         └── group 2
             └──────────── group 1
```

`findall()` trả về:

```text
list[tuple]
```

---

# 8. Ba capturing groups

Ví dụ:

```python
import re

text = """
001 - Python - Beginner
002 - Regex - Intermediate
003 - Asyncio - Advanced
"""

result = re.findall(
    r"(\d+)\s+-\s+(\w+)\s+-\s+(\w+)",
    text
)

print(result)
```

Kết quả:

```python
[
    ('001', 'Python', 'Beginner'),
    ('002', 'Regex', 'Intermediate'),
    ('003', 'Asyncio', 'Advanced'),
]
```

Có 3 groups:

```text
group 1 → ID
group 2 → name
group 3 → level
```

---

# 9. `findall()` với Named Group

Bạn có thể dùng:

```python
(?P<name>...)
```

nhưng cần lưu ý:

> `findall()` vẫn trả về list/tuple, không trả về dictionary.

Ví dụ:

```python
import re

text = """
Chapter 1: Intro
Chapter 2: Python
"""

result = re.findall(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    text
)

print(result)
```

Kết quả vẫn là:

```python
[
    ('1', 'Intro'),
    ('2', 'Python')
]
```

Tên group không làm `findall()` biến kết quả thành dictionary.

Nếu muốn:

```python
{
    "number": "1",
    "title": "Intro"
}
```

thì `finditer()` sẽ phù hợp hơn.

---

# 10. Đây là khác biệt quan trọng với `finditer()`

`findall()`:

```python
re.findall(...)
```

→ trả về **data trực tiếp**.

`finditer()`:

```python
re.finditer(...)
```

→ trả về các **Match objects**.

Ví dụ:

```text
findall()
    ↓
['1', '2', '3']

finditer()
    ↓
Match
Match
Match
```

Buổi 8 chúng ta sẽ học kỹ `finditer()`.

---

# 11. `findall()` và `\w+`

Ví dụ:

```python
import re

text = "Python is a programming language"

words = re.findall(r"\w+", text)

print(words)
```

Kết quả:

```python
[
    'Python',
    'is',
    'a',
    'programming',
    'language'
]
```

Đây là một cách đơn giản để lấy các token.

---

# 12. Tìm tất cả URL đơn giản

Ví dụ:

```python
import re

text = """
Visit https://example.com
or https://python.org
"""

urls = re.findall(
    r"https?://[^\s]+",
    text
)

print(urls)
```

Kết quả:

```python
[
    'https://example.com',
    'https://python.org'
]
```

Đây là một ứng dụng thực tế của `findall()`.

---

# 13. Tìm tất cả email

Một Regex đơn giản:

```python
import re

text = """
admin@example.com
hello@gmail.com
support@test.org
"""

emails = re.findall(
    r"[\w.-]+@[\w.-]+\.\w+",
    text
)

print(emails)
```

Kết quả:

```python
[
    'admin@example.com',
    'hello@gmail.com',
    'support@test.org'
]
```

Lưu ý: đây chỉ là Regex email **đơn giản**, không phải validator đầy đủ theo mọi quy tắc của email.

---

# 14. Tìm tất cả số điện thoại

Ví dụ dữ liệu:

```python
text = """
0901234567
0912345678
0987654321
"""
```

Regex:

```python
phones = re.findall(
    r"\b0\d{9}\b",
    text
)

print(phones)
```

Kết quả:

```python
[
    '0901234567',
    '0912345678',
    '0987654321'
]
```

---

# 15. `findall()` trong crawler

Đây là phần quan trọng nhất đối với hướng học của bạn.

Giả sử crawler lấy được text:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
```

Muốn lấy tất cả chapter number:

```python
import re

numbers = re.findall(
    r"Chapter\s+(\d+)",
    text
)

print(numbers)
```

Kết quả:

```python
['001', '002', '003']
```

---

# 16. Lấy cả chapter + title

```python
import re

text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""

chapters = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)

print(chapters)
```

Kết quả:

```python
[
    ('001', 'Vẫn là Tiêu Viêm'),
    ('002', 'Ba năm'),
    ('003', 'Vân Lam Tông')
]
```

Đây đã khá gần với parser thực tế.

---

# 17. Chuyển tuple thành dictionary

Ta có:

```python
chapters = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

Kết quả:

```python
[
    ('001', 'Vẫn là Tiêu Viêm'),
    ('002', 'Ba năm'),
]
```

Có thể chuyển thành:

```python
data = [
    {
        "number": number,
        "title": title,
    }
    for number, title in chapters
]
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
]
```

---

# 18. `findall()` + list comprehension

Có thể viết gọn:

```python
import re

text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""

chapters = [
    {
        "number": number,
        "title": title,
    }
    for number, title in re.findall(
        r"Chapter\s+(\d+):\s*(.+)",
        text
    )
]
```

Đây là code khá đẹp cho parser nhỏ.

---

# 19. Một vấn đề với `.+`

Pattern:

```regex
(.+)
```

thường dùng để lấy title.

Nhưng cần hiểu:

```regex
.
```

mặc định **không match newline**.

Do đó:

```python
text = """
Chapter 1: Hello
Chapter 2: Python
"""
```

với:

```python
re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

mỗi dòng có thể được xử lý độc lập nếu pattern tìm thấy phần phù hợp.

Nhưng khi muốn Regex đi qua newline, chúng ta sẽ cần:

```python
re.DOTALL
```

Flags sẽ được học ở **Buổi 12**.

---

# 20. `findall()` với `re.IGNORECASE`

Bạn có thể truyền flags:

```python
import re

text = "Chapter 1 CHAPTER 2 chapter 3"

result = re.findall(
    r"chapter\s+(\d+)",
    text,
    re.IGNORECASE
)

print(result)
```

Kết quả:

```python
['1', '2', '3']
```

Flags sẽ được học hệ thống ở Buổi 12.

---

# 21. `findall()` với nhóm optional

Đây là một điểm cần chú ý.

Ví dụ:

```python
import re

text = "abc123 xyz"

result = re.findall(
    r"(\w+)(\d+)?",
    text
)

print(result)
```

Kết quả có thể chứa:

```python
[
    ('abc', '123'),
    ('xyz', '')
]
```

Group optional không match sẽ thường xuất hiện dưới dạng chuỗi rỗng trong kết quả của `findall()`.

Điều này có thể gây bất ngờ.

---

# 22. `findall()` với zero-width match

Regex có thể match một vị trí mà không tiêu thụ ký tự.

Ví dụ:

```python
import re

result = re.findall(r"^", "abc")

print(result)
```

Kết quả:

```python
['']
```

Không phải lúc nào `findall()` cũng trả về chuỗi có nội dung.

Đây là phần nâng cao; hiện tại chỉ cần biết rằng:

> Regex match không nhất thiết phải chứa ký tự.

---

# 23. `findall()` không trả Match Object

Ví dụ:

```python
import re

result = re.findall(r"\d+", "abc123")

print(result)
```

Bạn nhận:

```python
['123']
```

Không có:

```python
match.group()
match.start()
match.end()
```

Nếu cần:

```text
match.group()
match.start()
match.end()
match.span()
match.groupdict()
```

thì dùng:

```python
re.finditer()
```

Đó chính là lý do tồn tại của `finditer()`.

---

# 24. Khi nào dùng `findall()`?

Dùng `findall()` khi:

### Trường hợp 1 — Chỉ cần dữ liệu

```python
numbers = re.findall(r"\d+", text)
```

### Trường hợp 2 — Cần danh sách kết quả

```python
emails = re.findall(email_pattern, text)
```

### Trường hợp 3 — Parser đơn giản

```python
chapters = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

---

# 25. Khi nào không nên dùng `findall()`?

Nếu bạn cần metadata của từng match:

```text
group
start
end
span
named groups
```

thì:

```python
re.finditer()
```

tốt hơn.

Ví dụ:

```python
for match in re.finditer(pattern, text):
    print(match.group())
    print(match.start())
    print(match.end())
```

---

# 26. Một ví dụ rất thực tế

Giả sử HTML đã được convert thành text:

```python
text = """
Chapter 1: Opening
Chapter 2: The Journey
Chapter 3: The Battle
Chapter 4: Return
"""
```

Ta cần danh sách:

```python
chapters = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

Kết quả:

```python
[
    ("1", "Opening"),
    ("2", "The Journey"),
    ("3", "The Battle"),
    ("4", "Return"),
]
```

Sau đó:

```python
for number, title in chapters:
    print(number, title)
```

Output:

```text
1 Opening
2 The Journey
3 The Battle
4 Return
```

---

# 27. `findall()` với `compile()`

Ở Buổi 11 chúng ta sẽ học `re.compile()`, nhưng có thể xem trước:

```python
import re

pattern = re.compile(
    r"Chapter\s+(\d+):\s*(.+)"
)

chapters = pattern.findall(text)
```

Thay vì:

```python
re.findall(pattern, text)
```

Kết quả giống nhau.

---

# 28. Một lỗi phổ biến

Nhiều người viết:

```python
matches = re.findall(
    r"Chapter\s+\d+",
    text
)

for match in matches:
    print(match.group())
```

Sai.

Vì:

```python
re.findall()
```

không trả Match Object.

Nó trả:

```python
['Chapter 1', 'Chapter 2']
```

Do đó phải:

```python
for match in matches:
    print(match)
```

Nếu muốn `.group()`:

```python
for match in re.finditer(...):
    print(match.group())
```

---

# 29. So sánh 4 API hiện tại

Bạn đã học đến đây:

| API           | Số kết quả | Kết quả         |
| ------------- | ---------: | --------------- |
| `search()`    |          1 | `Match \| None` |
| `match()`     |          1 | `Match \| None` |
| `fullmatch()` |          1 | `Match \| None` |
| `findall()`   |      nhiều | `list`          |

Và:

```text
search()
    ↓
tìm đầu tiên ở bất kỳ đâu

match()
    ↓
tìm ở đầu

fullmatch()
    ↓
toàn bộ chuỗi

findall()
    ↓
tất cả kết quả
```

---

# 30. Quy tắc cực kỳ quan trọng về Groups

Hãy thuộc bảng này:

| Regex          | `findall()` trả        |
| -------------- | ---------------------- |
| `\d+`          | `['123', '456']`       |
| `(\d+)`        | `['123', '456']`       |
| `(\d+)-(\w+)`  | `[('123','abc'), ...]` |
| không có group | toàn bộ match          |
| 1 group        | nội dung group         |
| 2+ groups      | tuple các groups       |

Ví dụ:

```python
re.findall(r"\d+", text)
```

và:

```python
re.findall(r"(\d+)", text)
```

có thể cho kết quả giống nhau:

```python
['123', '456']
```

Nhưng về semantics thì khác: trường hợp thứ hai chủ động capture phần số.

---

# 31. Bài tập

## Bài 1 — Numbers

Cho:

```python
text = "Python 3.12, released in 2023"
```

Dùng `findall()` lấy tất cả số.

Kết quả mong muốn:

```python
['3', '12', '2023']
```

---

## Bài 2 — Words

Cho:

```python
text = "Python makes regex programming easier"
```

Dùng:

```regex
\w+
```

để lấy tất cả word.

---

## Bài 3 — Chapter numbers

Cho:

```python
text = """
Chapter 1
Chapter 2
Chapter 3
Chapter 4
"""
```

Kết quả:

```python
['1', '2', '3', '4']
```

---

# Bài 4 — Chapter + title

Cho:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
```

Dùng `findall()` để tạo:

```python
[
    ("001", "Vẫn là Tiêu Viêm"),
    ("002", "Ba năm"),
    ("003", "Vân Lam Tông"),
]
```

---

# Bài 5 — URL

Cho:

```python
text = """
https://example.com
http://python.org
https://github.com/python/cpython
"""
```

Dùng `findall()` lấy tất cả URL.

Gợi ý:

```regex
https?://[^\s]+
```

---

# Bài 6 — Email

Cho:

```python
text = """
admin@example.com
hello@gmail.com
test@example.org
"""
```

Dùng `findall()` lấy toàn bộ email.

---

# Bài 7 — Group

Cho:

```python
text = """
User: admin
User: john
User: alice
"""
```

Dùng:

```regex
User:\s*(\w+)
```

Kết quả:

```python
['admin', 'john', 'alice']
```

---

# Challenge — Parser chapter

Viết:

```python
def parse_chapters(text: str) -> list[dict[str, str]]:
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

* dùng `re.findall()`
* dùng **2 capturing groups**
* không dùng `finditer()`

Gợi ý:

```python
matches = re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

Sau đó chuyển:

```python
(number, title)
```

thành:

```python
{
    "number": number,
    "title": title,
}
```

---

# Challenge 2 — Parser đa format

Cho:

```python
text = """
Chapter 001: Vẫn là Tiêu Viêm
Chương 002: Ba năm
Chapter 003 - Vân Lam Tông
Chương 004 - Trận chiến
"""
```

Mục tiêu:

```python
[
    ("001", "Vẫn là Tiêu Viêm"),
    ("002", "Ba năm"),
    ("003", "Vân Lam Tông"),
    ("004", "Trận chiến"),
]
```

Bạn cần kết hợp:

```text
(?:Chapter|Chương)
        +
\s*
        +
\d+
        +
(?::|-)
```

Đây là bài rất tốt để luyện:

```text
Non-capturing group
        +
Capturing group
        +
findall()
        +
Alternation
```

---

## Tổng kết Buổi 7

Điểm cốt lõi:

```python
re.findall(pattern, text)
```

→ **lấy tất cả match và trả về list**.

Đặc biệt phải nhớ:

```text
Không có group
    ↓
list[match]

1 group
    ↓
list[group1]

2+ groups
    ↓
list[tuple]
```

Ví dụ quan trọng nhất:

```python
re.findall(
    r"Chapter\s+(\d+):\s*(.+)",
    text
)
```

→

```python
[
    ("001", "Vẫn là Tiêu Viêm"),
    ("002", "Ba năm"),
]
```

**Buổi 8 — `re.finditer()`** sẽ giải quyết hạn chế lớn của `findall()`: lấy **tất cả match nhưng vẫn giữ nguyên `Match Object`**, từ đó có thể dùng `group()`, `groupdict()`, `start()`, `end()`, `span()` và xây parser mạnh hơn.
