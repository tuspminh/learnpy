# Buổi 4 — Anchor & Boundary trong Python `re`

Hôm nay chúng ta học một phần rất quan trọng để chuyển Regex từ kiểu:

> "Tìm thấy pattern ở đâu đó"

sang:

> "Pattern phải xuất hiện **đúng vị trí**, **đúng toàn bộ chuỗi**, **đúng ranh giới**."

Các ký hiệu chính:

```regex
^
$
\A
\Z
\b
\B
```

---

# 1. Vấn đề của `re.search()`

Giả sử:

```python
import re

text = "Chapter 1234"

match = re.search(r"Chapter\s+\d{3}", text)

print(match.group())
```

Kết quả có thể là:

```text
Chapter 123
```

Nhưng chúng ta muốn:

```text
Chapter 1234
```

không được coi là chapter có **đúng 3 chữ số**.

Tại sao?

Regex:

```regex
Chapter\s+\d{3}
```

chỉ nói:

> Hãy tìm `Chapter`, whitespace, rồi 3 chữ số.

Nó **không nói rằng sau 3 chữ số phải kết thúc**.

Đây chính là lúc Anchor xuất hiện.

---

# 2. `^` — bắt đầu chuỗi

Regex:

```regex
^
```

nghĩa là:

> Vị trí bắt đầu của chuỗi.

Ví dụ:

```python
import re

text = "Python is great"

print(bool(re.search(r"^Python", text)))
```

Kết quả:

```text
True
```

Vì `Python` nằm ở đầu.

Nhưng:

```python
text = "I love Python"

print(bool(re.search(r"^Python", text)))
```

→

```text
False
```

Vì:

```text
I love Python
^^^^^^^^^^^^^^
```

`Python` không nằm ở đầu.

---

# 3. `^` không phải ký tự

Đây là điểm cần nhớ.

```regex
^Python
```

không có nghĩa là tìm:

```text
^Python
```

Nó có nghĩa:

```text
start
  ↓
Python
```

---

# 4. `$` — cuối chuỗi

Ngược lại:

```regex
$
```

nghĩa là:

> Vị trí cuối chuỗi.

Ví dụ:

```python
import re

text = "I love Python"

print(bool(re.search(r"Python$", text)))
```

→

```text
True
```

Nhưng:

```python
text = "Python is great"

print(bool(re.search(r"Python$", text)))
```

→

```text
False
```

---

# 5. `^...$`

Khi kết hợp:

```regex
^Python$
```

ta có nghĩa:

> Toàn bộ chuỗi phải chính xác là `Python`.

Ví dụ:

```python
import re

pattern = r"^Python$"

for text in ["Python", "I love Python", "Python is great"]:
    print(text, bool(re.search(pattern, text)))
```

Kết quả:

```text
Python True
I love Python False
Python is great False
```

---

# 6. `^` + `$` để validate

Ví dụ muốn kiểm tra chuỗi chỉ chứa chữ số:

```python
import re

pattern = r"^\d+$"

for text in ["123", "12345", "abc123", "123abc", ""]:
    print(text, bool(re.search(pattern, text)))
```

Ta muốn:

```text
123      → True
12345    → True
abc123   → False
123abc   → False
""       → False
```

Đây là một pattern rất phổ biến.

---

# 7. Nhưng Python có `fullmatch()`

Trong Python, nếu mục tiêu là:

> Toàn bộ string phải match pattern

thì thường nên cân nhắc:

```python
re.fullmatch()
```

Ví dụ:

```python
import re

text = "123"

match = re.fullmatch(r"\d+", text)

print(bool(match))
```

→ `True`

Với validation đơn giản, `fullmatch()` thường rõ nghĩa hơn:

```python
re.fullmatch(r"\d+", text)
```

thay vì:

```python
re.search(r"^\d+$", text)
```

---

# 8. `^` và `$` với multiline

Đây là chỗ bắt đầu thú vị.

Cho:

```python
text = """Python
Java
Rust"""
```

Nếu:

```python
import re

matches = re.findall(r"^Python", text)

print(matches)
```

→

```text
['Python']
```

Mặc định `^` liên quan đến đầu **toàn bộ string**.

Nhưng với:

```python
re.MULTILINE
```

thì `^` và `$` có thể hoạt động theo từng dòng.

Ví dụ:

```python
import re

text = """Python
Java
Rust"""

matches = re.findall(r"^Java", text, re.MULTILINE)

print(matches)
```

→

```text
['Java']
```

Tương tự:

```regex
$
```

có thể match cuối từng dòng khi dùng `re.MULTILINE`.

---

# 9. `\A` — tuyệt đối bắt đầu string

Python `re` có:

```regex
\A
```

Nó biểu diễn:

> Bắt đầu của toàn bộ string.

Ví dụ:

```python
import re

text = "Python\nJava"

print(bool(re.search(r"\APython", text)))
```

→ `True`.

Điểm quan trọng:

```text
^
```

có thể thay đổi hành vi khi dùng `re.MULTILINE`.

Trong khi:

```text
\A
```

luôn chỉ đến **đầu toàn bộ string**.

---

# 10. `\Z` — cuối string

Tương tự:

```regex
\Z
```

biểu diễn cuối string.

Ví dụ:

```python
import re

text = "Python"

print(bool(re.search(r"Python\Z", text)))
```

→ `True`.

Có thể ghi nhớ:

```text
\A → absolute beginning
\Z → absolute end
```

---

# 11. `^` vs `\A`

Không có `MULTILINE`:

```regex
^
```

và:

```regex
\A
```

thường cho kết quả tương tự khi xét đầu toàn bộ string.

Nhưng khi có:

```python
re.MULTILINE
```

thì:

```regex
^
```

có thể match đầu mỗi dòng.

Còn:

```regex
\A
```

vẫn chỉ match đầu string.

---

# 12. `\b` — Word Boundary

Đây là một trong những phần quan trọng nhất của Regex.

`\b` nghĩa là:

> Ranh giới giữa word character (`\w`) và non-word character (`\W`), hoặc ranh giới đầu/cuối chuỗi.

Ví dụ:

```python
import re

text = "Python is powerful"

match = re.search(r"\bPython\b", text)

print(match.group())
```

→

```text
Python
```

---

# 13. Tại sao cần `\b`?

Giả sử:

```python
text = "Python Pythonic"

match = re.search(r"Python", text)
```

Regex sẽ tìm thấy:

```text
Python
```

Nhưng nếu muốn **chính xác từ `Python`**, không phải một phần của `Pythonic`, ta dùng:

```regex
\bPython\b
```

---

# 14. So sánh

### Không có boundary

```regex
Python
```

có thể match:

```text
Python
Pythonic
MyPython
Python123
```

### Có boundary

```regex
\bPython\b
```

chỉ muốn `Python` như một word riêng.

Ví dụ:

```python
import re

pattern = r"\bPython\b"

tests = [
    "Python",
    "Pythonic",
    "I love Python",
    "MyPython",
    "Python123",
]

for text in tests:
    print(text, bool(re.search(pattern, text)))
```

Kết quả:

```text
Python True
Pythonic False
I love Python True
MyPython False
Python123 False
```

---

# 15. Tại sao `Python123` không match?

Vì:

```text
Python123
      ^^^
```

`n` là `\w`.

`1` cũng là `\w`.

Không có ranh giới giữa chúng.

Do đó:

```regex
\bPython\b
```

không match.

---

# 16. `\B` — không phải boundary

Ngược lại:

```regex
\B
```

nghĩa là:

> Vị trí không phải word boundary.

Ví dụ:

```python
import re

text = "Python"

print(bool(re.search(r"\Byth", text)))
```

Ở giữa một word không có boundary nên có thể match.

Thực tế, `\B` ít dùng hơn `\b`, nhưng bạn cần biết nó tồn tại.

---

# 17. Word Boundary và tiếng Việt

Python 3 Regex hỗ trợ Unicode mặc định.

Ví dụ:

```python
import re

text = "Tôi học Python"

match = re.search(r"\bPython\b", text)

print(match.group())
```

→ `Python`.

Với tiếng Việt:

```python
text = "Tôi đang học lập trình Python rất vui"
```

`\w` mặc định có thể xử lý các chữ Unicode tốt hơn so với tư duy ASCII đơn thuần.

Tuy nhiên, khi xây parser thực tế, bạn vẫn nên test với **dữ liệu tiếng Việt thật** thay vì giả định.

---

# 18. Boundary trong parser truyện

Đây là ứng dụng rất phù hợp với project crawler của bạn.

Giả sử:

```text
Chapter 123
Chapter 1234
Chapter 123A
```

Ta muốn tìm:

```text
Chapter 123
```

nhưng không muốn match một phần của:

```text
Chapter 1234
```

Có thể dùng:

```regex
\bChapter\s+123\b
```

Tuy nhiên với format chapter, cách tốt hơn thường là thiết kế pattern toàn bộ cấu trúc và boundary phù hợp.

---

# 19. `\b` + `\d`

Ví dụ:

```python
import re

text = "Chapter 123"

match = re.search(r"\b\d+\b", text)

print(match.group())
```

→

```text
123
```

Pattern:

```regex
\b\d+\b
```

nghĩa là:

```text
word boundary
+
một hoặc nhiều digit
+
word boundary
```

---

# 20. Một lỗi quan trọng với `\b`

Hãy thử:

```python
import re

text = "Chapter 1234"

match = re.search(r"\b\d{3}\b", text)

print(match)
```

Kết quả:

```text
None
```

Đây chính là điều chúng ta muốn.

Vì sau:

```text
123
```

vẫn còn:

```text
4
```

và `3` với `4` đều là `\w`.

Không có boundary ở đó.

---

# 21. Giải quyết bài toán Buổi 2

Trước đây:

```regex
Chapter\s+\d{3}
```

có thể match một phần:

```text
Chapter 1234
^^^^^^^^^^^^
```

Ta có thể dùng:

```regex
\bChapter\s+\d{3}\b
```

Ví dụ:

```python
import re

pattern = r"\bChapter\s+\d{3}\b"

tests = [
    "Chapter 123",
    "Chapter 001",
    "Chapter 1234",
    "Chapter 12",
]

for text in tests:
    match = re.search(pattern, text)
    print(text, bool(match))
```

Kết quả mong muốn:

```text
Chapter 123   → True
Chapter 001   → True
Chapter 1234  → False
Chapter 12    → False
```

---

# 22. Nhưng còn một vấn đề

Pattern:

```regex
\bChapter\s+\d{3}\b
```

có thể match:

```text
Story Chapter 123 Title
```

vì nó chỉ yêu cầu `Chapter 123` xuất hiện như một đoạn hợp lệ.

Nếu yêu cầu:

> **Toàn bộ string phải chính xác là `Chapter` + whitespace + 3 digits**

thì dùng:

```python
re.fullmatch(r"Chapter\s+\d{3}", text)
```

Đây là tư duy rất quan trọng:

### Extraction

```python
re.search()
```

### Validation toàn chuỗi

```python
re.fullmatch()
```

---

# 23. `search()` + Anchor

Ví dụ:

```python
text = "Chapter 123"
```

Pattern:

```regex
^Chapter\s+\d{3}$
```

có nghĩa:

```text
START
 ↓
Chapter
 ↓
whitespace
 ↓
3 digits
 ↓
END
```

Đây là Regex validation cổ điển.

---

# 24. `^` và `$` vs `\A` và `\Z`

Tóm tắt:

| Regex | Ý nghĩa                               |
| ----- | ------------------------------------- |
| `^`   | đầu string / đầu dòng với MULTILINE   |
| `$`   | cuối string / cuối dòng với MULTILINE |
| `\A`  | đầu toàn bộ string                    |
| `\Z`  | cuối toàn bộ string                   |
| `\b`  | word boundary                         |
| `\B`  | non-word-boundary                     |

---

# 25. Một ví dụ thực tế: username

Giả sử username chỉ được phép:

```text
a-z
A-Z
0-9
_
```

và dài từ 3 đến 20 ký tự.

Pattern:

```regex
^[a-zA-Z0-9_]{3,20}$
```

Ví dụ:

```python
import re

pattern = r"^[a-zA-Z0-9_]{3,20}$"

tests = [
    "admin",
    "user_123",
    "ab",
    "hello world",
    "user@123",
]

for username in tests:
    print(
        username,
        bool(re.fullmatch(r"[a-zA-Z0-9_]{3,20}", username))
    )
```

Ở đây tôi dùng `fullmatch()` vì nó thể hiện rõ ý định:

> Toàn bộ username phải hợp lệ.

---

# 26. Một ví dụ thực tế: mã chapter

Giả sử quy định:

```text
Chapter 001
Chapter 002
...
Chapter 999
```

Pattern:

```regex
Chapter\s+\d{3}
```

Nếu validation toàn chuỗi:

```python
pattern = r"Chapter\s+\d{3}"

text = "Chapter 123"

if re.fullmatch(pattern, text):
    print("Valid")
```

Hoặc:

```regex
^Chapter\s+\d{3}$
```

với `search()`.

Trong Python, tôi khuyên bạn ưu tiên:

```python
re.fullmatch()
```

khi mục đích là validation.

---

# 27. `re.match()` nằm ở đâu?

Bạn đã học:

```python
re.search()
re.fullmatch()
```

Còn:

```python
re.match()
```

thì sao?

`re.match()` tìm pattern **từ đầu string**.

Ví dụ:

```python
import re

print(re.match(r"Python", "Python is great"))
```

→ match.

Nhưng:

```python
print(re.match(r"Python", "I love Python"))
```

→ `None`.

Về mặt tư duy:

```text
search()
    ↓
tìm ở bất kỳ đâu

match()
    ↓
từ đầu string

fullmatch()
    ↓
toàn bộ string
```

---

# 28. Ba API cần nhớ

```text
re.search()
     ↓
     tìm ở đâu đó

re.match()
     ↓
     phải bắt đầu từ đầu

re.fullmatch()
     ↓
     toàn bộ chuỗi
```

Ví dụ:

```python
text = "abc123xyz"
pattern = r"\d+"
```

### `search`

```python
re.search(pattern, text)
```

→ `123`

### `match`

```python
re.match(pattern, text)
```

→ `None`

### `fullmatch`

```python
re.fullmatch(pattern, text)
```

→ `None`

---

# 29. Bài tập Buổi 4

## Bài 1

Viết Regex match:

```text
Python
```

chỉ khi nó nằm **ở đầu string**.

```text
Python is good       → True
I love Python        → False
```

---

## Bài 2

Viết Regex match:

```text
Python
```

chỉ khi nó nằm **ở cuối string**.

```text
I love Python        → True
Python is good       → False
```

---

## Bài 3

Viết Regex kiểm tra toàn bộ string chỉ gồm số:

```text
123       → True
12345     → True
123abc    → False
abc123    → False
```

---

## Bài 4

Dùng `\b` để match chính xác từ:

```text
Python
```

Test:

```text
Python          → True
I love Python   → True
Pythonic        → False
MyPython        → False
Python123       → False
```

---

## Bài 5

Cho:

```python
text = "Chapter 1234"
```

Viết Regex sao cho:

```text
Chapter 123    → True
Chapter 001    → True
Chapter 1234   → False
Chapter 12     → False
```

Gợi ý:

```regex
\bChapter\s+\d{3}\b
```

---

# Challenge — Cực kỳ thực tế

Cho danh sách:

```python
chapters = [
    "Chapter 001",
    "Chapter 12",
    "Chapter 123",
    "Chapter 1234",
    "Chapter ABC",
    "Chapter 999",
    "Chapter 000",
]
```

Viết hàm:

```python
def is_valid_chapter(text: str) -> bool:
    ...
```

Yêu cầu:

```text
Chapter 001   → True
Chapter 12    → False
Chapter 123   → True
Chapter 1234  → False
Chapter ABC   → False
Chapter 999   → True
Chapter 000   → True
```

**Khuyến nghị:** dùng `re.fullmatch()` thay vì `re.search()`.

---

## Bài tập nâng cao

Viết:

```python
def extract_chapter(text: str) -> int | None:
    ...
```

Cho:

```text
"Chapter 123: Tam Niên Chi Ước"
```

trả về:

```python
123
```

Cho:

```text
"Chapter 1234: Something"
```

cũng phải lấy:

```python
1234
```

Ở đây chúng ta **không validation**, mà đang **extraction**.

Đây là điểm khác biệt rất quan trọng:

```text
Validation
    ↓
fullmatch()

Extraction
    ↓
search()
findall()
finditer()
```

---

### Sau Buổi 4, bạn đã có nền móng:

```text
Character Class
      ↓
Quantifier
      ↓
Anchor
      ↓
Boundary
      ↓
Regex Pattern
```

**Buổi 5** chúng ta sẽ học **Groups** — `( )`, capturing group, `group()`, `groups()`, named group `(?P<name>...)`. Đây là bước cực kỳ quan trọng để từ việc **match text** chuyển sang **trích xuất dữ liệu có cấu trúc**, đặc biệt hữu ích cho crawler/parser.
