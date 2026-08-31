# Buổi 14 — Non-capturing Group `(?:...)`

Hôm nay chúng ta học một thành phần cực kỳ quan trọng khi Regex bắt đầu phức tạp:

```regex
(?:...)
```

Tên đầy đủ:

> **Non-capturing group**

Nếu `( ... )` là **capturing group**, thì:

```regex
(?:...)
```

là group **không lưu kết quả capture**.

Điều này đặc biệt quan trọng khi bạn xây **parser, tokenizer, crawler và text cleaner**.

---

# 1. Ôn lại Capturing Group

Ở các bài trước, bạn đã thấy:

```regex
(...)
```

Ví dụ:

```python
import re

pattern = re.compile(
    r"(cat|dog)"
)

match = pattern.search("I have a dog")

print(match.group())
print(match.group(1))
```

Kết quả:

```text
dog
dog
```

`(cat|dog)` vừa:

1. Gom `cat|dog` thành một group.
2. Lưu kết quả match vào group `1`.

Đây gọi là **capturing group**.

---

# 2. Non-capturing Group

Bây giờ:

```regex
(?:cat|dog)
```

Nó vẫn gom:

```text
cat
OR
dog
```

nhưng **không tạo capture group**.

Ví dụ:

```python
import re

pattern = re.compile(
    r"(?:cat|dog)"
)

match = pattern.search("I have a dog")

print(match.group())
print(match.groups())
```

Kết quả:

```text
dog
()
```

Không có group nào được capture.

---

# 3. So sánh trực tiếp

### Capturing

```regex
(cat|dog)
```

→ Có group.

### Non-capturing

```regex
(?:cat|dog)
```

→ Không có group.

Điểm quan trọng:

> **Cả hai vẫn match giống nhau.**

Khác biệt chính là:

> Có lưu kết quả vào capture group hay không.

---

# 4. Tại sao cần Non-capturing Group?

Hãy xem:

```regex
(cat|dog)+
```

Ta dùng group để áp dụng:

```regex
+
```

cho toàn bộ:

```text
cat|dog
```

Nhưng chúng ta không thực sự cần lấy group đó.

Vậy viết:

```regex
(?:cat|dog)+
```

sẽ rõ ý hơn:

> Tôi cần group để điều khiển Regex, nhưng không cần capture dữ liệu.

---

# 5. Ví dụ

```python
import re

pattern = re.compile(
    r"(?:cat|dog)+"
)

match = pattern.fullmatch(
    "catdogcat"
)

print(match.group())
print(match.groups())
```

Kết quả:

```text
catdogcat
()
```

---

# 6. Capturing Group gây ảnh hưởng đến `findall()`

Đây là lý do bạn **rất cần hiểu** `(?:...)`.

Xét:

```python
import re

text = "cat dog bird"

pattern = re.compile(
    r"(cat|dog|bird)"
)

print(pattern.findall(text))
```

Kết quả:

```python
['cat', 'dog', 'bird']
```

Ở đây chưa có vấn đề.

Nhưng hãy thêm một group khác.

---

# 7. Một Regex có nhiều group

```python
pattern = re.compile(
    r"(cat|dog)\s+(bird|fish)"
)

text = "cat bird dog fish"

print(pattern.findall(text))
```

Kết quả:

```python
[
    ("cat", "bird"),
    ("dog", "fish"),
]
```

`findall()` trả về **các capture groups**, thay vì toàn bộ match.

---

# 8. Non-capturing Group giải quyết vấn đề

Nếu group chỉ dùng để grouping:

```python
pattern = re.compile(
    r"(?:cat|dog)\s+(bird|fish)"
)
```

Bây giờ:

```python
print(pattern.findall(text))
```

Kết quả:

```python
[
    "bird",
    "fish",
]
```

Group:

```regex
(?:cat|dog)
```

không ảnh hưởng đến kết quả capture.

---

# 9. Khi không cần lấy dữ liệu → `(?:...)`

Một quy tắc rất hữu ích:

```text
(...)
```

dùng khi:

> Tôi muốn lấy dữ liệu.

Còn:

```text
(?:...)
```

dùng khi:

> Tôi chỉ muốn nhóm pattern.

Ví dụ:

```regex
(?P<number>\d+)
```

→ muốn lấy number.

Nhưng:

```regex
(?:Chapter|Chương)
```

→ chỉ muốn grouping.

---

# 10. Ví dụ Chapter Parser

Ta có:

```text
Chapter 001: Python
Chương 002: Regex
```

Một Regex tốt:

```python
import re

pattern = re.compile(
    r"""
    (?:
        Chapter
        |
        Chương
    )
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

Ở đây:

```regex
(?:Chapter|Chương)
```

không cần capture.

Nhưng:

```regex
(?P<number>\d+)
```

cần capture.

Và:

```regex
(?P<title>.+)
```

cũng cần capture.

Đây là cách thiết kế Regex rất tốt.

---

# 11. Tại sao không viết `(Chapter|Chương)`?

Có thể viết:

```regex
(Chapter|Chương)
```

Nhưng lúc này Regex tạo:

```text
group 1
```

Trong khi chúng ta không cần nó.

Pattern trở thành:

```text
group 1 → Chapter/Chương
group 2 → number
group 3 → title
```

Trong khi điều chúng ta thực sự muốn:

```text
group 1 → number
group 2 → title
```

Hoặc tốt hơn nữa:

```text
number → named group
title  → named group
```

---

# 12. Named Group kết hợp Non-capturing Group

Đây là style tôi khuyến khích:

```python
CHAPTER_PATTERN = re.compile(
    r"""
    (?:
        Chapter
        |
        Chương
    )
    \s+
    (?P<number>\d+)
    \s*:\s*
    (?P<title>.+?)
    """,
    re.IGNORECASE | re.VERBOSE,
)
```

Sau đó:

```python
match.group("number")
match.group("title")
```

Rất rõ ràng.

---

# 13. `(?:...)` không tạo group number

Ví dụ:

```python
pattern = re.compile(
    r"(?:cat)-(dog)"
)

match = pattern.search(
    "cat-dog"
)

print(match.group(1))
```

Kết quả:

```text
dog
```

Không phải:

```text
cat
```

Vì:

```regex
(?:cat)
```

không capture.

Còn:

```regex
(dog)
```

là capture group đầu tiên.

---

# 14. Group numbering

Ví dụ:

```regex
(foo)(?:bar)(baz)
```

Các group là:

```text
(foo)       → group 1
(?:bar)     → không có group
(baz)       → group 2
```

Vì vậy:

```python
match.group(1)
```

→ `foo`

```python
match.group(2)
```

→ `baz`

---

# 15. Nested Group

Xét:

```regex
((cat|dog))
```

Có:

```text
group 1 → toàn bộ cat/dog
group 2 → cat hoặc dog
```

Điều này đôi khi không cần thiết.

Có thể viết:

```regex
((?:cat|dog))
```

Bây giờ:

```text
group 1 → cat hoặc dog
```

Group bên trong chỉ dùng để grouping.

---

# 16. Đây là pattern rất phổ biến

Thay vì:

```regex
(foo|(bar|baz))
```

có thể thiết kế:

```regex
(foo|(?:bar|baz))
```

Nhưng khi Regex phức tạp, nên hỏi:

> Tôi thực sự cần capture group nào?

Chỉ giữ lại những group cần cho dữ liệu output.

---

# 17. Non-capturing Group + Quantifier

Một use case cực kỳ phổ biến:

```regex
(?:abc)+
```

Match:

```text
abc
abcabc
abcabcabc
```

Ví dụ:

```python
pattern = re.compile(
    r"(?:abc)+"
)

print(pattern.fullmatch("abcabc"))
```

→ Match.

---

# 18. `?`

```regex
(?:https://)?
```

Có nghĩa:

```text
https://
```

có thể xuất hiện hoặc không.

Ví dụ:

```python
pattern = re.compile(
    r"(?:https://)?example\.com"
)
```

Match:

```text
example.com
https://example.com
```

---

# 19. `*`

```regex
(?:ab)*
```

Match:

```text
""
"ab"
"abab"
"ababab"
```

---

# 20. `+`

```regex
(?:ab)+
```

Match:

```text
"ab"
"abab"
"ababab"
```

nhưng không match:

```text
""
```

---

# 21. `{n,m}`

```regex
(?:ab){2,4}
```

Match:

```text
abab
ababab
abababab
```

Tức là:

```text
ab
+
ab
+
...
```

từ 2 đến 4 lần.

---

# 22. Alternation + Non-capturing Group

Đây là cặp rất thường đi cùng:

```regex
(?:A|B)
```

Ví dụ:

```regex
(?:jpg|png|gif)
```

Hoặc:

```regex
(?:GET|POST|PUT|DELETE)
```

Hoặc:

```regex
(?:Chapter|Chương)
```

---

# 23. File Extension Parser

```python
import re

EXT_PATTERN = re.compile(
    r"\.(?:jpg|png|gif|webp)"
)
```

Input:

```text
image.jpg
image.png
image.gif
image.webp
```

Không cần capture:

```text
jpg
png
gif
webp
```

Chúng ta chỉ cần match toàn bộ extension.

---

# 24. HTTP Method Parser

```python
METHOD_PATTERN = re.compile(
    r"\b(?:GET|POST|PUT|PATCH|DELETE)\b"
)
```

Tại sao dùng:

```regex
(?:GET|POST|PUT|PATCH|DELETE)
```

mà không:

```regex
(GET|POST|PUT|PATCH|DELETE)
```

?

Bởi vì chúng ta chỉ cần match method.

Không cần lấy:

```python
match.group(1)
```

---

# 25. URL Parser

```python
URL_PATTERN = re.compile(
    r"""
    https?://
    (?:www\.)?
    [A-Za-z0-9.-]+
    \.[A-Za-z]{2,}
    """,
    re.VERBOSE,
)
```

Ở đây:

```regex
https?
```

xử lý:

```text
http
https
```

Còn:

```regex
(?:www\.)?
```

xử lý:

```text
www.
```

nhưng không capture.

---

# 26. Capturing và Non-capturing trong cùng một Regex

Ví dụ:

```python
URL_PATTERN = re.compile(
    r"""
    (?P<scheme>https?)
    ://
    (?:www\.)?
    (?P<domain>[A-Za-z0-9.-]+)
    \.
    (?P<tld>[A-Za-z]{2,})
    """,
    re.VERBOSE,
)
```

Input:

```text
https://www.example.com
```

Kết quả:

```python
match.groupdict()
```

```python
{
    "scheme": "https",
    "domain": "example",
    "tld": "com",
}
```

Đây là style rất tốt:

```text
capture những gì cần
       +
không capture những gì chỉ dùng để cấu trúc
```

---

# 27. `findall()` và Non-capturing Group

Ví dụ:

```python
text = "jpg png gif webp"

pattern = re.compile(
    r"(?:jpg|png|gif|webp)"
)

print(pattern.findall(text))
```

Kết quả:

```python
[
    "jpg",
    "png",
    "gif",
    "webp",
]
```

Toàn bộ match được trả về.

---

# 28. So sánh với Capturing

```python
pattern = re.compile(
    r"(jpg|png|gif|webp)"
)
```

`findall()`:

```python
[
    "jpg",
    "png",
    "gif",
    "webp",
]
```

Trong trường hợp **chỉ một capturing group**, kết quả nhìn giống nhau.

Đây là lý do nhiều người không nhận ra sự khác biệt.

---

# 29. Nhưng khi có nhiều group

```python
pattern = re.compile(
    r"(image)\.(jpg|png|gif)"
)

text = "image.jpg image.png"

print(pattern.findall(text))
```

Kết quả:

```python
[
    ("image", "jpg"),
    ("image", "png"),
]
```

Nếu `image` không cần capture:

```python
pattern = re.compile(
    r"(?:image)\.(jpg|png|gif)"
)
```

Kết quả:

```python
[
    "jpg",
    "png",
]
```

Đây là lý do `(?:...)` rất hữu ích.

---

# 30. Non-capturing Group không làm Regex "nhanh thần kỳ"

Một hiểu lầm khác:

> `(?:...)` chắc chắn nhanh hơn `(...)`.

Không nên xem đó là mục tiêu chính.

Mục tiêu chính là:

```text
capture group
    ↓
data extraction

non-capturing group
    ↓
pattern structure
```

Nó giúp Regex:

* dễ hiểu hơn
* ít group numbering hơn
* `findall()` dễ kiểm soát hơn
* parser output sạch hơn
* maintainability tốt hơn

---

# 31. Quy tắc thiết kế Regex

Khi nhìn thấy:

```regex
(...)
```

hãy hỏi:

> Tôi có cần lấy nội dung này không?

Nếu **có**:

```regex
(...)
```

hoặc tốt hơn:

```regex
(?P<name>...)
```

Nếu **không**:

```regex
(?:...)
```

---

# 32. Named Group thường tốt hơn Numbered Group

Thay vì:

```python
match.group(1)
match.group(2)
match.group(3)
```

nên:

```python
match.group("number")
match.group("title")
match.group("author")
```

Ví dụ:

```python
pattern = re.compile(
    r"""
    (?P<number>\d+)
    \s*-\s*
    (?P<title>.+)
    """,
    re.VERBOSE,
)
```

Code sử dụng:

```python
number = match.group("number")
title = match.group("title")
```

dễ đọc hơn.

---

# 33. Non-capturing Group trong Chapter Parser

Một parser tốt:

```python
import re


CHAPTER_PATTERN = re.compile(
    r"""
    ^
    (?:
        Chapter
        |
        Chương
    )
    \s+
    (?P<number>\d+)
    \s*
    :
    \s*
    (?P<title>.+?)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

Test:

```python
text = """
Chapter 001: Python
Chương 002: Regex
CHAPTER 003: Asyncio
"""
```

```python
for match in CHAPTER_PATTERN.finditer(text):
    print(match.groupdict())
```

Output:

```python
{'number': '001', 'title': 'Python'}
{'number': '002', 'title': 'Regex'}
{'number': '003', 'title': 'Asyncio'}
```

Đây chính xác là kiểu Regex parser bạn sẽ dùng trong crawler.

---

# 34. Non-capturing Group + `|` là một cặp rất quan trọng

Nhớ mẫu:

```regex
(?:A|B)
```

Ví dụ:

```regex
(?:http|https)
```

```regex
(?:jpg|png|gif)
```

```regex
(?:Chapter|Chương)
```

```regex
(?:GET|POST|PUT|DELETE)
```

Nếu không cần lấy kết quả của group:

> **Dùng `(?:...)`.**

---

# 35. Bài tập

## Bài 1

Viết Regex match:

```text
cat
dog
bird
```

nhưng **không tạo capturing group**.

Gợi ý:

```regex
(?:...)
```

---

## Bài 2

Cho:

```python
text = "jpg png gif webp"
```

Viết:

```python
EXT_PATTERN
```

dùng:

```regex
(?:jpg|png|gif|webp)
```

và kiểm tra:

```python
pattern.findall(text)
```

---

## Bài 3

Cho:

```text
http://example.com
https://example.com
```

Viết Regex:

```regex
https?://
```

và không tạo capturing group không cần thiết.

---

# Bài 4 — Chapter

Cho:

```text
Chapter 001: Python
Chương 002: Regex
Chapter 003: Asyncio
```

Viết:

```python
CHAPTER_PATTERN
```

trong đó:

```regex
Chapter|Chương
```

phải nằm trong:

```regex
(?:...)
```

và:

```text
number
title
```

phải là named groups.

---

# Bài 5 — URL

Viết Regex match:

```text
http://example.com
https://example.com
http://www.example.com
https://www.example.com
```

Trong đó:

```regex
www.
```

là optional nhưng **không capture**.

Gợi ý:

```regex
(?:www\.)?
```

---

# Challenge — Parser thực tế

Xây:

```python
class ChapterParser:

    PATTERN = re.compile(
        ...
    )

    def parse_all(self, text: str) -> list[dict]:
        ...
```

Input có thể là:

```text
Chapter 001: Python
chapter 002 - Regex
Chương 003: Asyncio
CHƯƠNG 004 - PySide6
```

Output:

```python
[
    {"number": "001", "title": "Python"},
    {"number": "002", "title": "Regex"},
    {"number": "003", "title": "Asyncio"},
    {"number": "004", "title": "PySide6"},
]
```

Yêu cầu:

```text
re.compile()
IGNORECASE
MULTILINE
VERBOSE
Alternation
Non-capturing Group
Named Groups
finditer()
```

---

# Challenge 2 — Tokenizer

Xây tokenizer:

```python
TOKEN_PATTERN = re.compile(
    r"""
    (?P<NUMBER>\d+(?:\.\d+)?)
    |
    (?P<WORD>[A-Za-z_]\w*)
    |
    (?P<OPERATOR>[+\-*/])
    |
    (?P<SPACE>\s+)
    """,
    re.VERBOSE,
)
```

Hãy chú ý:

```regex
\d+(?:\.\d+)?
```

Ở đây:

```regex
(?:\.\d+)?
```

**không capture**.

Nó chỉ nói:

> Có thể có phần `.123`, nhưng không cần lưu riêng nó.

Với:

```text
123.456
```

toàn bộ:

```text
123.456
```

được capture bởi:

```regex
(?P<NUMBER>...)
```

Đây là một ví dụ rất đẹp về cách dùng **capturing group + non-capturing group** cùng nhau.

---

# Tổng kết

Hai loại group:

```text
(...) 
   ↓
Capturing Group
   ↓
Lấy dữ liệu
```

và:

```text
(?:...)
   ↓
Non-capturing Group
   ↓
Chỉ cấu trúc Regex
```

Quy tắc quan trọng nhất:

```text
Cần dữ liệu?
    │
    ├── YES → (?P<name>...)
    │
    └── NO  → (?:...)
```

Ví dụ production-style:

```python
CHAPTER_PATTERN = re.compile(
    r"""
    ^
    (?:
        Chapter
        |
        Chương
    )
    \s+
    (?P<number>\d+)
    \s*[-:]\s*
    (?P<title>.+?)
    $
    """,
    re.IGNORECASE
    | re.MULTILINE
    | re.VERBOSE,
)
```

Ở đây:

```text
(?:Chapter|Chương)
        ↓
    cấu trúc

(?P<number>...)
        ↓
      dữ liệu

(?P<title>...)
        ↓
      dữ liệu
```

Đây là tư duy rất quan trọng để từ **Regex search** tiến tới **Regex parser**.

**Buổi 15 — Lookahead** sẽ là bước chuyển rất thú vị: chúng ta sẽ học cách nói với Regex **“match A nhưng chỉ khi phía sau là B”** bằng `(?=...)`, hoặc **“match A nhưng phía sau không được là B”** bằng `(?!...)`, mà không đưa B vào kết quả match.
