# Buổi 15 — Lookahead `(?=...)` và `(?!...)`

Hôm nay chúng ta học **Lookahead** — một trong những kỹ thuật quan trọng nhất của Advanced Regex.

Nếu `Alternation` giúp ta nói:

```regex
A|B
```

> A hoặc B

thì Lookahead giúp ta nói:

```regex
A(?=B)
```

> Match **A**, nhưng chỉ khi **ngay phía sau A là B**.

Điểm quan trọng:

> **B được kiểm tra nhưng không bị lấy vào kết quả match.**

---

# 1. Lookahead là gì?

Có 2 loại chính:

### Positive Lookahead

```regex
(?=...)
```

Nghĩa:

> Phía sau **phải có** pattern này.

### Negative Lookahead

```regex
(?!...)
```

Nghĩa:

> Phía sau **không được có** pattern này.

---

# 2. Positive Lookahead

Pattern:

```regex
foo(?=bar)
```

Có thể đọc là:

```text
match "foo"
NHƯNG
sau foo phải là "bar"
```

Input:

```text
foobar
```

→ match:

```text
foo
```

Không match:

```text
foo123
```

vì sau `foo` không phải `bar`.

---

# 3. Ví dụ Python

```python
import re

pattern = re.compile(
    r"foo(?=bar)"
)

text = "foobar"

match = pattern.search(text)

print(match.group())
```

Kết quả:

```text
foo
```

Chú ý:

```text
foobar
^^^
foo
```

`bar` được kiểm tra nhưng **không nằm trong match**.

---

# 4. Đây là điểm quan trọng nhất

So sánh:

### Regex bình thường

```regex
foobar
```

Match:

```text
foobar
```

### Lookahead

```regex
foo(?=bar)
```

Match:

```text
foo
```

Nhưng điều kiện là:

```text
foo + bar
```

phải tồn tại.

---

# 5. Visualize

Regex:

```regex
foo(?=bar)
```

Input:

```text
foobar
```

Ta có:

```text
f o o b a r
└───┘
  foo
     └────┘
      bar
      ↑
   kiểm tra
```

Kết quả:

```text
foo
```

---

# 6. Positive Lookahead với số

Giả sử muốn tìm số nhưng chỉ khi phía sau là:

```text
USD
```

Ví dụ:

```text
100 USD
200 EUR
300 USD
```

Regex:

```regex
\d+(?=\sUSD)
```

Python:

```python
import re

pattern = re.compile(
    r"\d+(?=\sUSD)"
)

text = """
100 USD
200 EUR
300 USD
"""

print(pattern.findall(text))
```

Kết quả:

```python
['100', '300']
```

Rất hay:

```text
100 USD
^^^
match

200 EUR
không match

300 USD
^^^
match
```

`USD` không nằm trong kết quả.

---

# 7. Nếu không dùng Lookahead?

Bạn có thể viết:

```regex
\d+\sUSD
```

Nhưng kết quả sẽ là:

```text
100 USD
300 USD
```

Trong khi đôi khi bạn chỉ muốn:

```text
100
300
```

Lookahead giải quyết chính xác vấn đề đó.

---

# 8. Lookahead không consume characters

Đây là khái niệm quan trọng.

Regex:

```regex
foo(?=bar)
```

match:

```text
foo
```

Regex engine kiểm tra:

```text
bar
```

nhưng không "ăn" `bar`.

Có thể hình dung:

```text
foo | bar
^^^   ^^^
 │     │
 │     └── chỉ kiểm tra
 └──────── match
```

---

# 9. Negative Lookahead

Bây giờ:

```regex
(?!...)
```

Ví dụ:

```regex
foo(?!bar)
```

Nghĩa:

> Match `foo` nhưng phía sau **không được là `bar`**.

---

# 10. Ví dụ

```python
import re

pattern = re.compile(
    r"foo(?!bar)"
)

text = """
foobar
foobaz
foo123
"""

print(pattern.findall(text))
```

Kết quả:

```python
['foo', 'foo']
```

Hai match là:

```text
foobaz
^^^

foo123
^^^
```

Còn:

```text
foobar
```

không match.

---

# 11. So sánh hai loại

### Positive

```regex
foo(?=bar)
```

```text
foo + phải có bar
```

### Negative

```regex
foo(?!bar)
```

```text
foo + không được có bar
```

---

# 12. Một ví dụ rất thực tế

Giả sử có:

```text
chapter.html
chapter.php
chapter.json
chapter.css
```

Bạn muốn tìm filename nhưng **chỉ khi extension không phải `.css`**.

Có thể:

```regex
chapter(?!\.css)
```

Ví dụ:

```python
pattern = re.compile(
    r"chapter(?!\.css)"
)

text = """
chapter.html
chapter.php
chapter.json
chapter.css
"""

print(pattern.findall(text))
```

Kết quả:

```python
['chapter', 'chapter', 'chapter']
```

`chapter.css` bị loại.

---

# 13. Negative Lookahead rất hữu ích trong Text Cleaner

Ví dụ muốn tìm:

```text
http://...
https://...
```

nhưng không muốn match:

```text
http://localhost
```

Ta có thể tạo điều kiện:

```regex
https?://(?!localhost)
```

Ví dụ:

```python
pattern = re.compile(
    r"https?://(?!localhost)"
)
```

Input:

```text
https://google.com
http://github.com
http://localhost
```

Hai URL đầu được match phần protocol.

---

# 14. Lookahead + `findall()`

Ví dụ:

```text
100 USD
200 EUR
300 USD
400 VND
```

Regex:

```python
pattern = re.compile(
    r"\d+(?=\sUSD)"
)
```

```python
print(pattern.findall(text))
```

→

```python
['100', '300']
```

Đây là một use case rất phổ biến:

> **Extract A based on condition B, nhưng chỉ lấy A.**

---

# 15. Lookahead + nhiều điều kiện

Bạn có thể nối nhiều lookahead.

Ví dụ password phải:

* có ít nhất một chữ cái
* có ít nhất một số
* dài ít nhất 8 ký tự

Regex:

```regex
^(?=.*[A-Za-z])(?=.*\d).{8,}$
```

Đây là một Regex rất quan trọng để hiểu Lookahead.

---

# 16. Phân tích password Regex

```regex
^
(?=.*[A-Za-z])
(?=.*\d)
.{8,}
$
```

### `^`

Bắt đầu string.

### `(?=.*[A-Za-z])`

Phía sau phải tồn tại ít nhất một chữ cái.

### `(?=.*\d)`

Phía sau phải tồn tại ít nhất một số.

### `.{8,}`

Ít nhất 8 ký tự.

### `$`

Kết thúc string.

---

# 17. Tại sao Lookahead mạnh?

Vì chúng ta có thể kiểm tra nhiều điều kiện:

```text
        ┌── có chữ
        │
        ├── có số
        │
        ├── có ký tự đặc biệt
        │
        ▼
    PASSWORD
```

nhưng không cần consume những phần dùng làm điều kiện.

---

# 18. Password nâng cao

Ví dụ yêu cầu:

* ít nhất 8 ký tự
* có chữ
* có số
* có `!@#$`

Có thể:

```regex
^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$]).{8,}$
```

Python:

```python
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$]).{8,}$"
)
```

Test:

```python
tests = [
    "abc123",
    "abc12345",
    "abc12345!",
    "abcdefgh!",
]

for value in tests:
    print(
        value,
        bool(PASSWORD_PATTERN.fullmatch(value))
    )
```

---

# 19. Lookahead với Word Boundary

Ví dụ muốn match:

```text
http
```

nhưng chỉ khi nó bắt đầu URL:

```text
http://
https://
```

Có thể:

```regex
https?(?=://)
```

Input:

```text
http://example.com
https://google.com
httpx://test.com
```

Match:

```text
http
https
```

nhưng:

```text
httpx
```

không match.

---

# 20. Lookahead cực hữu ích cho URL Parser

Ví dụ:

```regex
https?(?=://)
```

Ở đây:

```text
https?
```

là phần muốn lấy.

```text
://
```

chỉ là điều kiện.

Do đó:

```python
pattern.findall(
    "http://google.com https://github.com"
)
```

→

```python
['http', 'https']
```

---

# 21. Lookahead với Extension

Giả sử:

```text
image.jpg
image.png
image.gif
document.pdf
```

Muốn lấy tên file **chỉ khi extension là image format**.

Có thể:

```regex
\w+(?=\.(?:jpg|png|gif))
```

Phân tích:

```text
\w+
```

→ tên file

```text
(?=...)
```

→ phía sau phải có extension phù hợp.

```regex
\.(?:jpg|png|gif)
```

→ `.jpg`, `.png`, `.gif`

Nhưng extension không nằm trong match.

---

# 22. Python

```python
import re

pattern = re.compile(
    r"\w+(?=\.(?:jpg|png|gif))"
)

text = """
image.jpg
photo.png
icon.gif
document.pdf
"""

print(pattern.findall(text))
```

Kết quả:

```python
[
    "image",
    "photo",
    "icon",
]
```

Đây là ví dụ kết hợp:

```text
Lookahead
+
Non-capturing Group
```

---

# 23. Negative Lookahead + Alternation

Ví dụ:

```text
Chapter 1
Chapter 2
Advertisement
Chapter 3
```

Muốn match `Chapter` nhưng không match nếu sau đó là:

```text
Advertisement
```

Có thể:

```regex
Chapter(?!\s+Advertisement)
```

Nếu có nhiều từ cần loại:

```regex
Chapter(?!\s+(?:Advertisement|Sponsored|Ads))
```

Đây là pattern rất thực tế trong **text extraction**.

---

# 24. Loại bỏ link quảng cáo

Giả sử text:

```text
https://example.com
https://ads.example.com
https://github.com
```

Bạn muốn match URL nhưng không phải URL có host:

```text
ads.example.com
```

Có thể dùng:

```regex
https?://(?!ads\.)
```

Ví dụ:

```python
pattern = re.compile(
    r"https?://(?!ads\.)\S+"
)
```

---

# 25. Lookahead không phải Lookbehind

Đừng nhầm:

### Lookahead

Nhìn về **phía trước**:

```regex
A(?=B)
```

```text
A B
  →
```

### Lookbehind

Nhìn về **phía sau**:

```regex
(?<=A)B
```

```text
A B
←
```

Lookbehind chúng ta học ở **Buổi 16**.

---

# 26. So sánh

Muốn lấy:

```text
100
```

trong:

```text
100 USD
```

### Lookahead

```regex
\d+(?=\sUSD)
```

→ match `100`.

Ngược lại, muốn lấy:

```text
USD
```

nhưng chỉ khi phía trước là số:

```regex
(?<=\d\s)USD
```

→ đây là Lookbehind.

---

# 27. Lookahead có thể chứa Regex phức tạp

Không chỉ:

```regex
(?=abc)
```

Bạn có thể:

```regex
(?=\d+)
```

hoặc:

```regex
(?=[A-Za-z]+)
```

hoặc:

```regex
(?=https?://)
```

hoặc:

```regex
(?=(?:jpg|png|gif))
```

hoặc:

```regex
(?=.*\d)
```

---

# 28. Lookahead + Lazy Matching

Ví dụ muốn lấy text giữa:

```text
START
...
END
```

Ta có thể dùng:

```regex
START.*?(?=END)
```

Ví dụ:

```python
pattern = re.compile(
    r"START.*?(?=END)",
    re.DOTALL,
)

text = """
START
Hello Python
Hello Regex
END
"""

match = pattern.search(text)

print(match.group())
```

Kết quả:

```text
START
Hello Python
Hello Regex
```

`END` không nằm trong match.

Đây là một kỹ thuật cực kỳ hữu ích khi xử lý text.

---

# 29. So sánh với `.*?END`

Nếu viết:

```regex
START.*?END
```

thì:

```text
END
```

sẽ nằm trong match.

Nếu viết:

```regex
START.*?(?=END)
```

thì:

```text
END
```

chỉ được dùng làm **điều kiện dừng**.

---

# 30. Trích xuất chapter

Đây là một ví dụ sát với crawler truyện.

Input:

```text
Chapter 1
Python is great.
Regex is powerful.
Chapter 2
Asyncio is interesting.
Chapter 3
PySide6 is useful.
```

Muốn lấy nội dung chapter 1 nhưng không lấy:

```text
Chapter 2
```

Có thể dùng:

```regex
Chapter 1.*?(?=Chapter 2)
```

với:

```python
re.DOTALL
```

Nhưng cách tổng quát hơn là:

```regex
Chapter 1.*?(?=Chapter \d+|$)
```

Nghĩa:

> lấy chapter 1 cho đến trước chapter tiếp theo hoặc hết text.

---

# 31. Đây là pattern rất đáng nhớ

```regex
.*?(?=NEXT|$)
```

Nghĩa:

```text
lấy ít nhất có thể
cho đến khi gặp NEXT
hoặc hết string
```

Ví dụ:

```regex
Chapter\s+\d+.*?(?=Chapter\s+\d+|$)
```

Đây là một pattern có thể dùng để tách chapter.

---

# 32. Negative Lookahead để loại trừ

Ví dụ:

```text
.py
.pyc
.pyw
```

Muốn match `.py` nhưng không match `.pyc`.

Có thể:

```regex
\.py(?!c)
```

Input:

```text
test.py
test.pyc
test.py
```

Match:

```text
.py
.py
```

---

# 33. Nhưng có thể tốt hơn

Nếu mục tiêu là extension `.py` chính xác:

```regex
\.py\b
```

hoặc nếu cuối token:

```regex
\.py$
```

Tư duy quan trọng:

> Lookahead rất mạnh, nhưng không phải lúc nào cũng là công cụ đơn giản nhất.

Regex tốt là Regex **đủ rõ ràng**, không phải Regex phức tạp nhất.

---

# 34. Lookahead + `re.MULTILINE`

Ví dụ:

```text
Chapter 1: Python
Chapter 2: Regex
Chapter 3: Asyncio
```

Muốn match `Chapter` chỉ khi phía sau có số:

```regex
^Chapter(?=\s+\d+)
```

với:

```python
re.MULTILINE
```

Ví dụ:

```python
pattern = re.compile(
    r"^Chapter(?=\s+\d+)",
    re.MULTILINE,
)

print(pattern.findall(text))
```

---

# 35. Lookahead + Named Group

Ví dụ:

```regex
(?P<number>\d+)(?=\sUSD)
```

Python:

```python
pattern = re.compile(
    r"(?P<number>\d+)(?=\sUSD)"
)

match = pattern.search(
    "Price: 100 USD"
)

print(match.groupdict())
```

Kết quả:

```python
{
    "number": "100"
}
```

`USD` không được capture.

---

# 36. Multiple Lookahead

Một Regex có thể có nhiều Lookahead:

```regex
^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$
```

Điều này có nghĩa:

```text
          ┌── phải có uppercase
          │
          ├── phải có lowercase
          │
          ├── phải có digit
          │
          └── tối thiểu 8 ký tự
```

Đây là cách Regex biểu diễn nhiều **constraints**.

---

# 37. Tư duy quan trọng

Regex thông thường:

```regex
A B C
```

nghĩa:

> Match A, sau đó B, sau đó C.

Lookahead:

```regex
A(?=B)
```

nghĩa:

> Match A, **kiểm tra** B.

Do đó:

```text
Normal:
A → consume B

Lookahead:
A → check B
```

---

# 38. Pattern Template quan trọng

### Positive

```regex
TARGET(?=CONDITION)
```

> TARGET phải có CONDITION phía sau.

### Negative

```regex
TARGET(?!FORBIDDEN)
```

> TARGET không được có FORBIDDEN phía sau.

---

# 39. Ví dụ thực tế với crawler

Giả sử HTML/text có:

```text
Chapter 001
Chapter 002
Chapter 003
Advertisement
Chapter 004
```

Bạn muốn nhận diện `Chapter` chỉ khi phía sau là chapter number:

```regex
Chapter(?=\s+\d+)
```

Điều này tránh match các text như:

```text
Chapter title
Chapter navigation
Chapter list
```

nếu chúng không có number ngay sau.

---

# 40. Ví dụ với Markdown

Giả sử:

```text
# Chapter 1
## Chapter 2
Chapter 3
```

Muốn match `Chapter` chỉ khi nó nằm sau heading marker:

```regex
(?<=^# )Chapter
```

Đây là **Lookbehind**, nên để Buổi 16.

Nhưng nếu muốn match heading marker chỉ khi phía sau là `Chapter`:

```regex
^#+(?=\s+Chapter)
```

Đây là Lookahead.

---

# 41. Bài tập

## Bài 1

Cho:

```text
100 USD
200 EUR
300 USD
400 VND
```

Viết Regex chỉ lấy:

```text
100
300
```

Gợi ý:

```regex
\d+(?=...)
```

---

## Bài 2

Cho:

```text
foo123
foobar
foobaz
```

Match `foo` nếu phía sau **không phải** `bar`.

Kết quả:

```text
foo123
foobaz
```

Gợi ý:

```regex
foo(?!bar)
```

---

## Bài 3

Cho:

```text
image.jpg
image.png
image.gif
document.pdf
```

Chỉ lấy:

```text
image
image
image
```

Gợi ý:

```regex
\w+(?=...)
```

---

# Bài 4 — URL

Cho:

```text
http://google.com
https://github.com
ftp://example.com
```

Chỉ match:

```text
http
https
```

Gợi ý:

```regex
https?(?=://)
```

---

# Bài 5 — Password

Viết Regex kiểm tra password:

* tối thiểu 8 ký tự
* có ít nhất 1 chữ cái
* có ít nhất 1 số

Gợi ý kiến trúc:

```regex
^
(?=.*[A-Za-z])
(?=.*\d)
.{8,}
$
```

---

# Challenge 1 — Chapter Extraction

Cho:

```text
Chapter 1
Python is great.
Regex is powerful.

Chapter 2
Asyncio is powerful.

Chapter 3
PySide6 is great.
```

Viết Regex lấy **toàn bộ Chapter 1**, nhưng không lấy:

```text
Chapter 2
```

Gợi ý:

```regex
Chapter\s+1.*?(?=Chapter\s+\d+|$)
```

và cần:

```python
re.DOTALL
```

---

# Challenge 2 — File Parser

Cho:

```text
book.txt
book.pdf
book.epub
book.jpg
book.png
```

Match filename nhưng chỉ khi extension là:

```text
txt
pdf
epub
```

Gợi ý:

```regex
\w+(?=\.(?:txt|pdf|epub)\b)
```

---

# Challenge 3 — Text Cleaner

Cho:

```text
Hello
[Advertisement]
Python
[Sponsored]
Regex
[Important]
Asyncio
```

Viết Regex tìm:

```text
[Advertisement]
[Sponsored]
```

nhưng không match:

```text
[Important]
```

Gợi ý:

```regex
\[(?:Advertisement|Sponsored)\]
```

Sau đó nâng cấp thành **negative lookahead** để loại một danh sách từ không mong muốn.

---

# Challenge 4 — Production-style

Xây một parser tìm giá USD:

```text
Apple: 100 USD
Book: 20 EUR
Phone: 500 USD
Table: 300 VND
Laptop: 1200 USD
```

Output:

```python
["100", "500", "1200"]
```

Yêu cầu:

```text
re.compile()
finditer()
Named Group
Positive Lookahead
```

Pattern gợi ý:

```regex
(?P<price>\d+(?:\.\d+)?)(?=\sUSD)
```

Sau đó:

```python
for match in pattern.finditer(text):
    print(match.group("price"))
```

---

# Tổng kết Buổi 15

Ba pattern cần nhớ:

```regex
A(?=B)
```

→ **A phải có B phía sau**

```regex
A(?!B)
```

→ **A không được có B phía sau**

```regex
A(?=B|C)
```

→ **A phải có B hoặc C phía sau**

Và đặc điểm quan trọng nhất:

```text
Lookahead
    ↓
kiểm tra điều kiện
    ↓
không consume condition
    ↓
condition không nằm trong match
```

Ví dụ kinh điển:

```regex
\d+(?=\sUSD)
```

Input:

```text
100 USD
```

Match:

```text
100
```

chứ không phải:

```text
100 USD
```

### Bức tranh Advanced Regex

```text
Buổi 13
Alternation
A|B
   ↓
Buổi 14
Non-capturing Group
(?:A|B)
   ↓
Buổi 15
Lookahead
A(?=B)
A(?!B)
   ↓
Buổi 16
Lookbehind
(?<=A)B
(?<!A)B
   ↓
Buổi 17
Backreference
(\w+)\s+\1
```

**Buổi 16 — Lookbehind** sẽ đối xứng với bài này: thay vì *“A phải có B ở phía sau”*, ta sẽ học *“B chỉ được match khi phía trước là A”*.
