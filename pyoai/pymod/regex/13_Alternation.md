# Buổi 13 — Alternation `|`

Hôm nay chúng ta học **Alternation** — phép "hoặc" trong Regex.

Đây là một trong những thành phần quan trọng nhất khi xây parser:

```regex
cat|dog
```

có nghĩa:

> Match `cat` **hoặc** `dog`.

---

# 1. Alternation là gì?

Ký hiệu:

```regex
|
```

Ví dụ:

```regex
cat|dog
```

Regex engine sẽ thử:

```text
cat
 ↓
match?

nếu không
 ↓
dog
 ↓
match?
```

---

# 2. Ví dụ cơ bản

```python
import re

pattern = re.compile(r"cat|dog")

text = "I have a cat and a dog."

print(pattern.findall(text))
```

Kết quả:

```python
['cat', 'dog']
```

---

# 3. Alternation có thể có nhiều lựa chọn

Không chỉ:

```regex
cat|dog
```

mà:

```regex
cat|dog|bird|fish
```

Ví dụ:

```python
pattern = re.compile(
    r"cat|dog|bird|fish"
)

text = "cat dog bird fish horse"

print(pattern.findall(text))
```

Kết quả:

```python
['cat', 'dog', 'bird', 'fish']
```

`horse` không match.

---

# 4. Alternation giống `or`

Trong Python:

```python
if animal == "cat" or animal == "dog":
    ...
```

Regex:

```regex
cat|dog
```

Có thể hiểu:

```text
cat OR dog
```

---

# 5. Nhưng có một vấn đề rất quan trọng

Xét:

```regex
cat|dog
```

Regex engine sẽ tìm:

```text
cat
```

hoặc:

```text
dog
```

ở **bất kỳ vị trí nào** trong string nếu bạn dùng:

```python
pattern.search(text)
```

Ví dụ:

```python
pattern = re.compile(r"cat|dog")

text = "concatenate"

match = pattern.search(text)

print(match.group())
```

Kết quả:

```text
cat
```

Vì `cat` xuất hiện bên trong:

```text
conCATenate
```

Nếu bạn muốn match **whole word**, cần thêm boundary.

Ví dụ:

```regex
\b(?:cat|dog)\b
```

Phần `(?:...)` chúng ta sẽ học kỹ ở **Buổi 14**.

---

# 6. Alternation + `findall()`

```python
pattern = re.compile(
    r"cat|dog"
)

text = """
cat
dog
cat
bird
dog
"""

print(pattern.findall(text))
```

Kết quả:

```python
['cat', 'dog', 'cat', 'dog']
```

---

# 7. Alternation + `search()`

```python
pattern = re.compile(
    r"cat|dog"
)

text = "I have a dog."

match = pattern.search(text)

if match:
    print(match.group())
```

Kết quả:

```text
dog
```

---

# 8. Alternation + `match()`

```python
pattern = re.compile(
    r"cat|dog"
)

print(pattern.match("cat is here"))
print(pattern.match("dog is here"))
print(pattern.match("I have a cat"))
```

Kết quả:

```text
<Match ...>
<Match ...>
None
```

Bởi vì `match()` yêu cầu match bắt đầu ở vị trí `0`.

---

# 9. Alternation + `fullmatch()`

```python
pattern = re.compile(
    r"cat|dog"
)

print(pattern.fullmatch("cat"))
print(pattern.fullmatch("dog"))
print(pattern.fullmatch("I have a cat"))
```

Kết quả:

```text
Match
Match
None
```

---

# 10. Alternation trong parser

Đây là nơi Alternation bắt đầu thực sự hữu ích.

Giả sử crawler gặp:

```text
Chapter
CHAPTER
chapter
Chương
```

Ta có thể viết:

```regex
Chapter|Chương
```

với:

```python
re.IGNORECASE
```

Ví dụ:

```python
import re

pattern = re.compile(
    r"Chapter|Chương",
    re.IGNORECASE,
)

text = """
Chapter 1
Chương 2
chapter 3
"""

print(pattern.findall(text))
```

Kết quả:

```python
[
    "Chapter",
    "Chương",
    "chapter",
]
```

---

# 11. Alternation + cụm từ

Alternation không chỉ dành cho một từ.

Ví dụ:

```regex
New York|Ho Chi Minh|Ha Noi
```

```python
pattern = re.compile(
    r"New York|Ho Chi Minh|Ha Noi"
)

text = """
I live in Ho Chi Minh.
She lives in Ha Noi.
He lives in New York.
"""

print(pattern.findall(text))
```

Kết quả:

```python
[
    "Ho Chi Minh",
    "Ha Noi",
    "New York",
]
```

---

# 12. Thứ tự Alternation rất quan trọng

Đây là điểm **cực kỳ quan trọng**.

Xét:

```regex
cat|catalog
```

Input:

```text
catalog
```

Regex có thể match:

```text
cat
```

thay vì:

```text
catalog
```

Bởi vì Alternation được thử theo thứ tự.

```text
cat
 ↓
match
 ↓
dừng
```

Nó không nhất thiết thử `catalog` trước.

---

# 13. Đảo thứ tự

Viết:

```regex
catalog|cat
```

Input:

```text
catalog
```

Bây giờ:

```text
catalog
```

được match trước.

---

# 14. Quy tắc thực tế

Khi có alternative mà một lựa chọn là prefix của lựa chọn khác:

```text
short
long
```

thường nên đặt lựa chọn dài hơn trước.

Ví dụ:

```regex
https://|http://
```

thay vì:

```regex
http://|https://
```

Trong ví dụ thứ hai, với:

```text
https://
```

`http://` không match vì có `s`, nên vẫn ổn.

Nhưng với những pattern prefix phức tạp hơn, thứ tự có thể quyết định kết quả.

---

# 15. Alternation + Group

Đây là nơi bắt đầu xuất hiện một khái niệm quan trọng:

```regex
(...)
```

Ví dụ:

```regex
(cat|dog)
```

Có nghĩa:

```text
cat
OR
dog
```

trong một group.

---

# 16. Tại sao cần Group?

Ví dụ:

```regex
I have a cat|dog
```

Có thể được hiểu là:

```text
I have a cat
OR
dog
```

chứ **không phải**:

```text
I have a cat
OR
I have a dog
```

Đây là một lỗi rất phổ biến.

---

# 17. Cách đúng

Dùng group:

```regex
I have a (cat|dog)
```

Bây giờ:

```text
I have a cat
```

hoặc:

```text
I have a dog
```

đều match.

Ví dụ:

```python
pattern = re.compile(
    r"I have a (cat|dog)"
)

print(
    pattern.search("I have a dog").group()
)
```

→

```text
I have a dog
```

---

# 18. Group xác định phạm vi của Alternation

Đây là tư duy quan trọng:

```regex
A|B
```

có phạm vi:

```text
A
OR
B
```

Còn:

```regex
X(A|B)
```

có nghĩa:

```text
X
+
(A OR B)
```

Ví dụ:

```regex
https?://(google|github)\.com
```

Match:

```text
https://google.com
https://github.com
```

---

# 19. Alternation + Quantifier

Một lỗi rất hay gặp.

Bạn muốn:

```text
catcat
```

hoặc:

```text
dogdog
```

Có thể bạn viết:

```regex
cat|dog+
```

Nhưng điều này có nghĩa:

```text
cat
OR
do + g+
```

Không phải:

```text
(cat|dog)+
```

---

# 20. Group để áp dụng Quantifier cho Alternation

Đúng:

```regex
(cat|dog)+
```

Ví dụ:

```python
pattern = re.compile(
    r"(cat|dog)+"
)

print(pattern.fullmatch("catdogcat"))
```

→ Match.

Vì:

```text
cat
+
dog
+
cat
```

---

# 21. Ví dụ với `?`

Bạn muốn:

```text
color
colour
```

Có thể:

```regex
colou?r
```

Đây là cách tốt.

Alternation cũng có thể:

```regex
color|colour
```

Nhưng:

```regex
colou?r
```

ngắn hơn.

---

# 22. Khi nào dùng Alternation?

Alternation phù hợp khi các lựa chọn thực sự khác nhau.

Ví dụ:

```regex
jpg|png|gif
```

```regex
GET|POST|PUT|DELETE
```

```regex
cat|dog|bird
```

```regex
Chapter|Chương
```

---

# 23. Ví dụ HTTP Method

```python
import re

METHOD_PATTERN = re.compile(
    r"GET|POST|PUT|PATCH|DELETE"
)
```

Input:

```text
GET /users
POST /users
DELETE /users/10
```

Ta có:

```python
methods = METHOD_PATTERN.findall(text)

print(methods)
```

---

# 24. Nhưng nên dùng Boundary

Nếu viết:

```regex
GET|POST
```

input:

```text
GETTING
```

có thể match:

```text
GET
```

Nếu muốn method nguyên vẹn:

```regex
\b(?:GET|POST|PUT|PATCH|DELETE)\b
```

Ở đây:

```regex
\b
```

đảm bảo boundary.

Còn:

```regex
(?:...)
```

là **non-capturing group** — bài kế tiếp.

---

# 25. Alternation + Character Class

Đôi khi bạn không cần Alternation.

Ví dụ:

```regex
cat|bat|hat
```

Có thể viết:

```regex
[cbh]at
```

Vì chỉ có **một ký tự thay đổi**.

---

# 26. So sánh

```regex
cat|bat|hat
```

và:

```regex
[cbh]at
```

Cả hai có thể match:

```text
cat
bat
hat
```

Nhưng Character Class phù hợp hơn khi:

> Chỉ một ký tự khác nhau.

---

# 27. Khi khác nhau nhiều

Ví dụ:

```regex
cat|dog|elephant
```

Không thể đơn giản thay bằng character class.

Lúc này:

```regex
cat|dog|elephant
```

là phù hợp.

---

# 28. Alternation trong URL parser

Ví dụ bạn muốn tìm protocol:

```text
http://
https://
ftp://
```

Có thể:

```python
PROTOCOL_PATTERN = re.compile(
    r"https?|ftp"
)
```

Sau đó:

```text
http
https
ftp
```

match.

Đây là cách kết hợp:

```regex
?
```

với pattern thay vì viết:

```regex
http|https|ftp
```

---

# 29. Alternation với Named Group

Bạn có thể xác định lựa chọn nào match.

Ví dụ:

```python
import re

pattern = re.compile(
    r"(?P<animal>cat|dog)"
)
```

Input:

```python
match = pattern.search(
    "I have a dog"
)
```

Sau đó:

```python
print(match.group("animal"))
```

→

```text
dog
```

---

# 30. Parser thực tế

Giả sử website có nhiều format:

```text
Chapter 001: Python
Chương 002: Regex
Chapter 003: Asyncio
```

Ta có thể:

```python
import re

CHAPTER_PATTERN = re.compile(
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
Chapter|Chương
```

là Alternation.

---

# 31. Nhưng có thể viết tốt hơn

Vì:

```text
Chapter
chapter
CHAPTER
```

chỉ khác hoa/thường, ta đã có:

```python
re.IGNORECASE
```

nên:

```regex
Chapter|Chương
```

là đủ.

---

# 32. Alternation + `finditer()`

```python
pattern = re.compile(
    r"cat|dog"
)

text = "cat dog cat dog"

for match in pattern.finditer(text):
    print(
        match.group(),
        match.span(),
    )
```

Kết quả:

```text
cat (0, 3)
dog (4, 7)
cat (8, 11)
dog (12, 15)
```

---

# 33. Một kỹ thuật rất hữu ích: xác định loại token

Ví dụ parser đơn giản:

```python
TOKEN_PATTERN = re.compile(
    r"""
    (?P<number>\d+)
    |
    (?P<word>[A-Za-z]+)
    |
    (?P<operator>[+\-*/])
    """,
    re.VERBOSE,
)
```

Input:

```text
123 Python + 456
```

Ta có:

```python
for match in TOKEN_PATTERN.finditer(text):
    print(match.groupdict())
```

Kết quả dạng:

```python
{'number': '123', 'word': None, 'operator': None}
{'number': None, 'word': 'Python', 'operator': None}
{'number': None, 'word': None, 'operator': '+'}
{'number': '456', 'word': None, 'operator': None}
```

Đây là nền tảng của **lexing/tokenization**.

---

# 34. Alternation có thể xây lexer

Tư duy:

```text
Input
  │
  ▼
Regex
  │
  ├── number
  ├── word
  ├── operator
  └── whitespace
```

Ví dụ:

```python
TOKEN_PATTERN = re.compile(
    r"""
    (?P<number>\d+(?:\.\d+)?)
    |
    (?P<word>[A-Za-z_]\w*)
    |
    (?P<operator>[+\-*/=])
    |
    (?P<space>\s+)
    """,
    re.VERBOSE,
)
```

Đây là bước đầu để hiểu cách parser/tokenizer hoạt động.

---

# 35. Alternation và thứ tự token

Thứ tự rất quan trọng.

Ví dụ:

```regex
=
==
```

Nếu viết:

```regex
=|==
```

với input:

```text
==
```

Regex có thể match:

```text
=
```

trước.

Thường nên đặt:

```regex
==|=
```

để token dài hơn được thử trước.

Đây là nguyên tắc:

> **Longest / more specific alternative first.**

---

# 36. Ví dụ lexer tốt hơn

```python
TOKEN_PATTERN = re.compile(
    r"""
    (?P<EQ>==)
    |
    (?P<ASSIGN>=)
    |
    (?P<NUMBER>\d+)
    |
    (?P<WORD>[A-Za-z_]\w*)
    """,
    re.VERBOSE,
)
```

Input:

```text
x == 10
```

Sẽ nhận:

```text
WORD
EQ
NUMBER
```

thay vì:

```text
WORD
ASSIGN
...
```

---

# 37. Một lỗi rất quan trọng với Alternation

Không nên viết Regex kiểu:

```regex
foo|bar|baz|qux|...
```

một cách thiếu cấu trúc khi pattern trở nên lớn.

Nếu pattern có nhiều lựa chọn:

```text
Chapter
Chương
Chap
CH
...
```

hãy tổ chức:

```python
pattern = re.compile(
    r"""
    (?P<keyword>
        Chapter
        |
        Chương
        |
        Chap
        |
        CH
    )
    ...
    """,
    re.IGNORECASE | re.VERBOSE,
)
```

Regex sẽ dễ đọc hơn.

---

# 38. Alternation trong Text Cleaner

Giả sử muốn loại bỏ:

```text
[AD]
[QUẢNG CÁO]
ADVERTISEMENT
```

Có thể:

```python
AD_PATTERN = re.compile(
    r"""
    \[AD\]
    |
    \[QUẢNG CÁO\]
    |
    ADVERTISEMENT
    """,
    re.IGNORECASE | re.VERBOSE,
)
```

Sau đó:

```python
cleaned = AD_PATTERN.sub("", text)
```

Đây là ví dụ rất sát với **HTML/text cleaner**.

---

# 39. Alternation + `sub()`

Ví dụ:

```python
pattern = re.compile(
    r"cat|dog"
)

text = "cat dog bird"

result = pattern.sub(
    "animal",
    text,
)

print(result)
```

→

```text
animal animal bird
```

---

# 40. Thay thế khác nhau tùy alternative

Đây mới là kỹ thuật mạnh.

```python
pattern = re.compile(
    r"cat|dog"
)
```

Ta có thể dùng function:

```python
def replace(match):
    if match.group() == "cat":
        return "CAT"

    return "DOG"
```

Sau đó:

```python
result = pattern.sub(
    replace,
    text,
)
```

Input:

```text
cat dog cat
```

Output:

```text
CAT DOG CAT
```

---

# 41. Named groups làm cách này tốt hơn

```python
pattern = re.compile(
    r"""
    (?P<cat>cat)
    |
    (?P<dog>dog)
    """,
    re.VERBOSE,
)
```

Function:

```python
def replace(match):
    if match.group("cat"):
        return "CAT"

    if match.group("dog"):
        return "DOG"

    return match.group()
```

Đây là kỹ thuật rất hữu ích khi Regex trở thành một mini-parser.

---

# 42. Quy tắc thiết kế Alternation

Khi viết:

```regex
A|B|C
```

hãy tự hỏi:

### 1. Có cần group không?

```regex
foo(bar|baz)
```

hay:

```regex
foo|bar|baz
```

### 2. Các alternative có chung prefix không?

```regex
http|https
```

có thể tối ưu thành:

```regex
https?
```

### 3. Một alternative có là prefix của alternative khác không?

```regex
cat|catalog
```

→ cân nhắc:

```regex
catalog|cat
```

### 4. Có cần boundary không?

```regex
cat|dog
```

có thể match một phần của từ lớn hơn.

---

# 43. Một ví dụ tổng hợp

Ta xây parser nhận:

```text
GET /users
POST /users
DELETE /users/1
```

Pattern:

```python
import re

REQUEST_PATTERN = re.compile(
    r"""
    (?P<method>
        GET
        |
        POST
        |
        PUT
        |
        PATCH
        |
        DELETE
    )
    \s+
    (?P<path>/\S*)
    """,
    re.VERBOSE,
)
```

Test:

```python
text = """
GET /users
POST /users
DELETE /users/1
"""

for match in REQUEST_PATTERN.finditer(text):
    print(match.groupdict())
```

Kết quả:

```python
{'method': 'GET', 'path': '/users'}
{'method': 'POST', 'path': '/users'}
{'method': 'DELETE', 'path': '/users/1'}
```

Ở đây ta đã kết hợp:

```text
Buổi 8  → finditer()
Buổi 11 → compile()
Buổi 12 → VERBOSE
Buổi 13 → Alternation
Named groups
```

---

# 44. Bài tập

## Bài 1

Match:

```text
cat
dog
bird
```

Viết:

```python
pattern = re.compile(...)
```

---

## Bài 2

Cho:

```text
I like Python
I like Java
I like Rust
I like Go
```

Tìm tất cả language:

```text
Python
Java
Rust
Go
```

Gợi ý:

```regex
Python|Java|Rust|Go
```

---

## Bài 3

Tìm HTTP methods:

```text
GET
POST
PUT
PATCH
DELETE
```

Viết:

```python
METHOD_PATTERN
```

bằng `re.compile()`.

---

# Bài 4 — Chapter

Cho:

```text
Chapter 001
Chương 002
chapter 003
CHƯƠNG 004
```

Viết Regex match:

```text
Chapter
Chương
```

không phân biệt hoa/thường.

Gợi ý:

```python
re.IGNORECASE
```

---

# Bài 5 — Extension

Cho:

```text
image.jpg
image.png
image.gif
image.webp
image.txt
```

Match:

```text
.jpg
.png
.gif
.webp
```

Gợi ý:

```regex
\.(jpg|png|gif|webp)
```

---

# Bài 6 — Alternation + Group

Cho:

```text
I have a cat
I have a dog
I have a bird
```

Viết:

```regex
I have a (cat|dog|bird)
```

và lấy animal bằng:

```python
match.group(1)
```

---

# Challenge 1 — URL Protocol

Xây:

```python
PROTOCOL_PATTERN
```

match:

```text
http://
https://
ftp://
```

Nhưng không match:

```text
file://
ssh://
```

---

# Challenge 2 — Chapter Parser

Xây:

```python
CHAPTER_PATTERN = re.compile(
    ...
)
```

cho các format:

```text
Chapter 001: Python
Chapter 002 - Regex
Chương 003: Asyncio
Chương 004 - PySide6
```

Output mong muốn:

```python
{
    "number": "001",
    "title": "Python",
}
```

và:

```python
{
    "number": "003",
    "title": "Asyncio",
}
```

Bạn sẽ phải kết hợp:

```text
Alternation
+
Named Group
+
IGNORECASE
+
VERBOSE
+
finditer()
```

---

# Challenge 3 — Tokenizer

Đây là bài quan trọng nhất.

Xây Regex:

```python
TOKEN_PATTERN = re.compile(
    ...
)
```

có thể nhận:

```text
123 + 456 * Python
```

thành:

```text
NUMBER
OPERATOR
NUMBER
OPERATOR
WORD
```

Gợi ý kiến trúc:

```python
r"""
(?P<NUMBER>\d+)
|
(?P<WORD>[A-Za-z_]\w*)
|
(?P<OPERATOR>[+\-*/])
|
(?P<SPACE>\s+)
"""
```

Sau đó dùng:

```python
for match in TOKEN_PATTERN.finditer(text):
    print(match.lastgroup, match.group())
```

Bạn sẽ thấy Regex bắt đầu chuyển từ **tìm kiếm text** sang **xây tokenizer/parser**.

---

# Tổng kết Buổi 13

Điểm cốt lõi:

```regex
A|B
```

nghĩa là:

```text
A OR B
```

Nếu cần gom phạm vi:

```regex
(A|B)
```

Nếu muốn áp dụng quantifier:

```regex
(A|B)+
```

Nếu muốn tránh capturing:

```regex
(?:A|B)
```

**Một quy tắc cực kỳ quan trọng:**

```regex
cat|catalog
```

có thể ưu tiên:

```text
cat
```

trước.

Thường nên cân nhắc:

```regex
catalog|cat
```

khi các alternative chồng lấn.

Và với parser:

```text
specific / longer
        ↓
generic / shorter
```

thường nên đặt **alternative cụ thể hơn trước**.

---

### Bức tranh của Phần III hiện tại

```text
Buổi 13
Alternation
    │
    ├── A|B
    ├── Group
    ├── precedence
    └── tokenizer
         │
         ▼
Buổi 14
Non-capturing Group
(?:...)
         │
         ▼
Buổi 15
Lookahead
(?=...)
(?!...)
         │
         ▼
Buổi 16
Lookbehind
(?<=...)
(?<!...)
```

**Buổi 14 — Non-capturing Group `(?:...)`** sẽ giải quyết một vấn đề rất quan trọng của Buổi 13: *khi nào cần `(A|B)`, khi nào nên dùng `(?:A|B)`, ảnh hưởng của capturing group đến `findall()`, `groups()`, `groupdict()`, và cách thiết kế Regex parser không tạo ra các capture group không cần thiết.*
