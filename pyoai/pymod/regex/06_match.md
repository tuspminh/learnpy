# Buổi 6 — `search()` vs `match()` vs `fullmatch()`

Hôm nay chúng ta tập trung vào **3 API quan trọng nhất của Python `re`**:

```python
re.search()
re.match()
re.fullmatch()
```

Nếu hiểu đúng 3 hàm này, bạn sẽ tránh được rất nhiều lỗi khi viết **validator, parser, crawler và text extractor**.

---

# 1. Bức tranh tổng quát

Hãy nhớ 3 câu này:

```text
search()
    ↓
Tìm pattern ở BẤT KỲ ĐÂU

match()
    ↓
Pattern phải BẮT ĐẦU từ đầu string

fullmatch()
    ↓
TOÀN BỘ string phải khớp pattern
```

Ví dụ:

```python
text = "Hello Python"
pattern = r"Python"
```

| API           | Kết quả |
| ------------- | ------- |
| `search()`    | ✅       |
| `match()`     | ❌       |
| `fullmatch()` | ❌       |

Bởi vì `Python` nằm ở giữa chuỗi.

---

# 2. `re.search()`

Cú pháp:

```python
re.search(pattern, string)
```

Nó tìm **lần xuất hiện đầu tiên** của pattern ở bất kỳ vị trí nào.

Ví dụ:

```python
import re

text = "I love Python"

match = re.search(r"Python", text)

if match:
    print(match.group())
```

Output:

```text
Python
```

Vị trí của `Python` không quan trọng.

---

# 3. `search()` tìm từ giữa string

```python
import re

text = "abc123xyz"

match = re.search(r"\d+", text)

print(match.group())
```

Output:

```text
123
```

Regex:

```regex
\d+
```

được tìm thấy ở:

```text
abc123xyz
   ^^^
```

Do đó:

```python
re.search()
```

rất phù hợp với **extraction**.

---

# 4. `search()` trả về gì?

Nếu tìm thấy:

```python
match = re.search(r"\d+", "abc123")
```

thì `match` là:

```text
re.Match
```

Nếu không tìm thấy:

```python
match = re.search(r"\d+", "abc")
```

thì:

```python
match is None
```

Do đó cách viết an toàn:

```python
match = re.search(r"\d+", text)

if match:
    print(match.group())
```

---

# 5. `re.match()`

`match()` khác `search()` ở chỗ:

> Pattern phải bắt đầu từ đầu string.

Ví dụ:

```python
import re

text = "Python is great"

match = re.match(r"Python", text)

print(match.group())
```

→

```text
Python
```

---

Nhưng:

```python
text = "I love Python"

match = re.match(r"Python", text)

print(match)
```

→

```text
None
```

Vì:

```text
I love Python
^^^^^^^^^^^^^
```

`Python` không nằm ở đầu.

---

# 6. So sánh `search()` và `match()`

```python
import re

text = "I love Python"

print(re.search(r"Python", text))
print(re.match(r"Python", text))
```

Kết quả:

```text
<re.Match ...>
None
```

Có thể hình dung:

```text
search()

I love Python
       ^^^^^^
       tìm được


match()

I love Python
^^^^^^
Python phải ở đây
```

---

# 7. `match()` tương tự `^`

Ví dụ:

```python
re.match(r"Python", text)
```

về ý tưởng tương tự:

```python
re.search(r"^Python", text)
```

Ví dụ:

```python
import re

text = "Python is great"

a = re.match(r"Python", text)
b = re.search(r"^Python", text)

print(bool(a))
print(bool(b))
```

Cả hai đều:

```text
True
```

Nhưng đừng vì thế mà nghĩ `match()` và `^` hoàn toàn giống nhau trong mọi tình huống; đặc biệt khi bạn bắt đầu dùng `re.MULTILINE`, sự khác biệt về ngữ nghĩa trở nên đáng chú ý.

---

# 8. `re.fullmatch()`

Đây là API rất quan trọng.

`fullmatch()` yêu cầu:

> **Toàn bộ string phải match pattern.**

Ví dụ:

```python
import re

text = "123"

match = re.fullmatch(r"\d+", text)

print(bool(match))
```

→

```text
True
```

---

Nhưng:

```python
text = "abc123"

match = re.fullmatch(r"\d+", text)

print(match)
```

→

```text
None
```

Mặc dù chuỗi có `123`, nhưng toàn bộ chuỗi không phải là digit.

---

# 9. Ba API trên cùng một string

Đây là ví dụ bạn nên thuộc:

```python
import re

text = "abc123xyz"
pattern = r"\d+"

print(re.search(pattern, text))
print(re.match(pattern, text))
print(re.fullmatch(pattern, text))
```

Kết quả:

```text
search()     → 123
match()      → None
fullmatch()  → None
```

Tại sao?

```text
abc123xyz
   ^^^
```

`search()`:

> Tôi tìm được `123`.

`match()`:

> `123` không ở đầu.

`fullmatch()`:

> Toàn bộ chuỗi không phải `123`.

---

# 10. Ví dụ thứ hai

```python
text = "123abc"
pattern = r"\d+"
```

Kết quả:

```text
search()     → 123
match()      → 123
fullmatch()  → None
```

Vì:

```text
123abc
^^^
```

`123` nằm ở đầu → `match()` thành công.

Nhưng toàn chuỗi không phải digit → `fullmatch()` thất bại.

---

# 11. Ví dụ thứ ba

```python
text = "123"
pattern = r"\d+"
```

Kết quả:

```text
search()     → 123
match()      → 123
fullmatch()  → 123
```

Vì cả ba điều kiện đều thỏa.

---

# 12. Bảng tổng hợp

| Input      | Pattern | `search()` | `match()` | `fullmatch()` |
| ---------- | ------- | ---------: | --------: | ------------: |
| `"abc123"` | `\d+`   |          ✅ |         ❌ |             ❌ |
| `"123abc"` | `\d+`   |          ✅ |         ✅ |             ❌ |
| `"123"`    | `\d+`   |          ✅ |         ✅ |             ✅ |
| `"abc"`    | `\d+`   |          ❌ |         ❌ |             ❌ |

Đây là bảng rất đáng nhớ.

---

# 13. Khi nào dùng `search()`?

Dùng `search()` khi mục tiêu là:

> **Tìm / extract một pattern bên trong text.**

Ví dụ:

```text
Story: Đấu Phá Thương Khung
Chapter: 123
Author: ABC
```

Muốn lấy chapter:

```python
import re

text = """
Story: Đấu Phá Thương Khung
Chapter: 123
Author: ABC
"""

match = re.search(
    r"Chapter:\s*(\d+)",
    text
)

if match:
    chapter = match.group(1)
    print(chapter)
```

Output:

```text
123
```

Đây là **extraction**.

→ `search()` rất phù hợp.

---

# 14. Khi nào dùng `match()`?

Dùng `match()` khi:

> Pattern phải bắt đầu ở đầu string.

Ví dụ dữ liệu log:

```text
ERROR: database connection failed
INFO: server started
WARNING: disk almost full
```

Muốn kiểm tra dòng có bắt đầu bằng `ERROR`:

```python
import re

line = "ERROR: database connection failed"

match = re.match(r"ERROR:", line)

if match:
    print("Error log")
```

---

# 15. Nhưng `startswith()` đôi khi tốt hơn

Nếu chỉ muốn:

```text
Có bắt đầu bằng "ERROR:" không?
```

thì không nhất thiết phải dùng Regex.

Có thể:

```python
if line.startswith("ERROR:"):
    ...
```

Đây là một nguyên tắc rất quan trọng:

> **Không dùng Regex nếu một API string đơn giản đã giải quyết được bài toán.**

Regex nên được dùng khi pattern thực sự cần Regex.

---

# 16. Khi nào dùng `fullmatch()`?

Đây là trường hợp:

> **Validation.**

Ví dụ chỉ cho phép số:

```python
import re

def is_number(text: str) -> bool:
    return re.fullmatch(r"\d+", text) is not None
```

Test:

```python
print(is_number("123"))
print(is_number("123abc"))
print(is_number("abc123"))
```

Output:

```text
True
False
False
```

---

# 17. Validation username

Giả sử username:

```text
3–20 ký tự
chỉ gồm chữ, số và _
```

Ta có:

```python
import re

USERNAME_PATTERN = r"[a-zA-Z0-9_]{3,20}"

def is_valid_username(username: str) -> bool:
    return re.fullmatch(USERNAME_PATTERN, username) is not None
```

Test:

```python
tests = [
    "admin",
    "user_123",
    "ab",
    "hello world",
    "user@123",
]

for username in tests:
    print(username, is_valid_username(username))
```

---

# 18. Tại sao không dùng `search()`?

Nếu viết:

```python
re.search(r"[a-zA-Z0-9_]{3,20}", "hello world")
```

Regex vẫn có thể tìm được:

```text
hello
```

hoặc một phần phù hợp.

Nhưng username:

```text
hello world
```

phải bị reject.

`fullmatch()` diễn đạt chính xác yêu cầu:

```text
TOÀN BỘ username
        ↓
phải hợp lệ
```

---

# 19. `fullmatch()` và `^...$`

Hai cách phổ biến:

```python
re.fullmatch(r"\d+", text)
```

hoặc:

```python
re.search(r"^\d+$", text)
```

Cả hai đều nhằm mục tiêu toàn chuỗi.

Nhưng khi code Python, tôi thường thích:

```python
re.fullmatch()
```

vì nó thể hiện ý định rõ ràng:

```text
fullmatch
    ↓
toàn bộ string
```

---

# 20. Một điểm tinh tế: `$`

Khi bạn dùng:

```regex
^\d+$
```

`$` có một số hành vi liên quan đến newline cuối chuỗi mà `fullmatch()` tránh được theo cách trực tiếp hơn.

Ví dụ:

```python
text = "123\n"
```

Trong validation nghiêm ngặt, hãy ưu tiên:

```python
re.fullmatch(r"\d+", text)
```

thay vì cố xây mọi validation bằng `^...$`.

---

# 21. `match()` không phải "match toàn bộ"

Đây là lỗi rất phổ biến.

Nhiều người nghĩ:

```python
re.match(r"\d+", "123abc")
```

sẽ fail.

Không đúng.

Nó thành công:

```text
123abc
^^^
```

vì `match()` chỉ yêu cầu:

> Match bắt đầu ở vị trí 0.

Nó **không yêu cầu hết chuỗi**.

Muốn toàn bộ:

```python
re.fullmatch(r"\d+", "123abc")
```

→ fail.

---

# 22. Ví dụ cực kỳ quan trọng

```python
import re

text = "123abc"

a = re.match(r"\d+", text)
b = re.fullmatch(r"\d+", text)

print(a.group())
print(b)
```

Output:

```text
123
None
```

Hãy nhớ:

```text
match()
    ↓
"Đầu chuỗi đúng là được"

fullmatch()
    ↓
"Đầu + giữa + cuối đều phải đúng"
```

---

# 23. `search()` + Group

Trong parser, pattern thường như:

```python
import re

text = "Chapter 123: Tam Niên Chi Ước"

match = re.search(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    text
)

if match:
    print(match.groupdict())
```

Kết quả:

```python
{
    "number": "123",
    "title": "Tam Niên Chi Ước",
}
```

Ở đây:

```text
search()
   ↓
tìm chapter ở đâu đó trong text
   ↓
named groups
   ↓
extract dữ liệu
```

Đây là cách dùng rất thực tế.

---

# 24. `match()` + Group

Giả sử mỗi dòng bắt đầu bằng:

```text
Chapter 123: ...
```

Ta có:

```python
import re

line = "Chapter 123: Tam Niên Chi Ước"

match = re.match(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    line
)

if match:
    print(match.groupdict())
```

Kết quả:

```python
{
    "number": "123",
    "title": "Tam Niên Chi Ước",
}
```

Dùng `match()` khi ta biết cấu trúc bắt đầu từ đầu dòng.

---

# 25. `fullmatch()` + Group

Giả sử ta yêu cầu toàn bộ input phải có format:

```text
Chapter 123
```

thì:

```python
import re

text = "Chapter 123"

match = re.fullmatch(
    r"Chapter\s+(?P<number>\d+)",
    text
)

if match:
    print(match.groupdict())
```

→

```python
{"number": "123"}
```

Nhưng:

```text
Chapter 123 extra
```

→ fail.

---

# 26. Tư duy chọn API

Khi gặp một bài toán Regex, trước tiên hãy hỏi:

### Câu hỏi 1

> Tôi muốn **tìm** pattern bên trong text?

→

```python
re.search()
```

---

### Câu hỏi 2

> Pattern bắt buộc phải bắt đầu từ đầu string?

→

```python
re.match()
```

---

### Câu hỏi 3

> Toàn bộ string phải hợp lệ?

→

```python
re.fullmatch()
```

---

# 27. Decision Tree

Bạn có thể nhớ:

```text
                  Tôi muốn làm gì?
                         │
             ┌───────────┴───────────┐
             │                       │
          Extract                 Validate
             │                       │
             ↓                       ↓
          search()               fullmatch()
             │
             │
       Có bắt đầu từ đầu?
             │
          ┌──┴──┐
         YES    NO
          ↓      ↓
       match() search()
```

Đây là cách tư duy tốt hơn việc học thuộc lòng.

---

# 28. Ví dụ với crawler

Giả sử HTML parser lấy được:

```python
text = """
Tên truyện: Đấu Phá Thương Khung

Chapter 123: Tam Niên Chi Ước

Tác giả: Thiên Tằm Thổ Đậu
"""
```

Muốn tìm chapter:

```python
match = re.search(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    text
)
```

Tại sao `search()`?

Vì `Chapter` nằm **ở giữa text**.

---

# 29. Ví dụ với từng dòng

Nếu crawler đã tách:

```python
line = "Chapter 123: Tam Niên Chi Ước"
```

và biết chapter luôn nằm đầu dòng:

```python
match = re.match(
    r"Chapter\s+(?P<number>\d+):\s*(?P<title>.+)",
    line
)
```

`match()` có ý nghĩa hơn.

---

# 30. Ví dụ validation

Nếu API nhận:

```python
chapter_number = "123"
```

và yêu cầu:

> Chỉ được phép là số.

Dùng:

```python
re.fullmatch(r"\d+", chapter_number)
```

Không dùng:

```python
re.search(r"\d+", chapter_number)
```

vì:

```text
"abc123xyz"
```

vẫn sẽ tìm thấy `123`.

---

# 31. Một pattern thực tế

Giả sử mã truyện:

```text
NOVEL-2026-00123
```

Format:

```text
NOVEL
-
4 digits
-
5 digits
```

Validation:

```python
import re

pattern = r"NOVEL-\d{4}-\d{5}"

def is_valid_code(value: str) -> bool:
    return re.fullmatch(pattern, value) is not None
```

Test:

```python
print(is_valid_code("NOVEL-2026-00123"))
print(is_valid_code("ABC-NOVEL-2026-00123"))
print(is_valid_code("NOVEL-26-123"))
```

Kết quả:

```text
True
False
False
```

---

# 32. Một sai lầm nguy hiểm

Đừng viết validator như:

```python
def is_valid_code(value):
    return re.search(r"NOVEL-\d{4}-\d{5}", value) is not None
```

Vì:

```text
"XXX-NOVEL-2026-00123-XXX"
```

vẫn có thể pass.

Nếu yêu cầu:

> Chuỗi phải chính xác theo format.

hãy dùng:

```python
re.fullmatch()
```

---

# 33. `pos` và `endpos`

Đây là phần nâng cao nhưng rất đáng biết.

Các API này cho phép giới hạn vùng tìm kiếm:

```python
re.search(pattern, string, pos, endpos)
```

Ví dụ:

```python
import re

text = "abc123xyz456"

match = re.search(r"\d+", text, 0, 6)

print(match.group())
```

Kết quả:

```text
123
```

Ta chỉ cho Regex tìm trong:

```text
abc123
^^^^^^
```

---

# 34. `Pattern` object

Sau này khi dùng:

```python
pattern = re.compile(r"\d+")
```

thì:

```python
pattern.search(text)
pattern.match(text)
pattern.fullmatch(text)
```

Đây là nội dung của **Buổi 11 — Compiled Regex**.

Hiện tại chỉ cần biết:

```text
re.search()
re.match()
re.fullmatch()
```

là API cấp module.

---

# 35. Bài tập thực hành

## Bài 1

Cho:

```python
text = "Hello Python"
```

Pattern:

```regex
Python
```

Xác định:

```python
re.search(...)
re.match(...)
re.fullmatch(...)
```

cái nào thành công.

---

## Bài 2

Cho:

```python
text = "123abc"
pattern = r"\d+"
```

Dự đoán:

```python
re.search(pattern, text)
re.match(pattern, text)
re.fullmatch(pattern, text)
```

**Không chạy code trước.**

---

## Bài 3

Viết:

```python
def is_digits(text: str) -> bool:
    ...
```

Yêu cầu:

```text
"123"       → True
"00123"     → True
"123abc"    → False
"abc123"    → False
""          → False
```

---

## Bài 4

Viết:

```python
def extract_number(text: str) -> str | None:
    ...
```

Input:

```text
"Order ID: 12345"
```

Output:

```text
"12345"
```

Dùng `search()`.

---

# Bài 5 — `match()`

Cho:

```text
ERROR: Database failed
INFO: Server started
WARNING: Disk full
```

Viết:

```python
def get_log_level(line: str) -> str | None:
    ...
```

Sao cho:

```python
get_log_level("ERROR: Database failed")
```

trả về:

```text
ERROR
```

Gợi ý:

```regex
(?P<level>[A-Z]+):
```

và dùng `match()`.

---

# Bài 6 — `fullmatch()`

Tạo validator cho username:

```text
3–20 ký tự
a-z
A-Z
0-9
_
```

Ví dụ:

```text
admin       → True
user_123    → True
ab          → False
hello@123   → False
hello world → False
```

---

# Challenge — Parser thực tế

Cho:

```python
text = """
[INFO] Chapter 001: Vẫn là Tiêu Viêm
[INFO] Chapter 002: Ba năm
[ERROR] Chapter ABC: Invalid
[INFO] Chapter 003: Vân Lam Tông
"""
```

Viết:

```python
def parse_chapter_line(line: str) -> dict | None:
    ...
```

Yêu cầu:

```python
parse_chapter_line(
    "[INFO] Chapter 001: Vẫn là Tiêu Viêm"
)
```

trả về:

```python
{
    "level": "INFO",
    "number": "001",
    "title": "Vẫn là Tiêu Viêm",
}
```

Còn:

```python
parse_chapter_line(
    "[ERROR] Chapter ABC: Invalid"
)
```

trả về:

```python
None
```

### Gợi ý pattern

```regex
\[([A-Z]+)\]\s+Chapter\s+(\d+):\s*(.+)
```

Sau đó nâng cấp lên named groups:

```regex
\[(?P<level>[A-Z]+)\]\s+
Chapter\s+
(?P<number>\d+):
\s*
(?P<title>.+)
```

---

# 36. Tổng kết Buổi 6

Hãy nhớ 3 API bằng **3 từ khóa**:

```text
search()
   ↓
TÌM

match()
   ↓
ĐẦU

fullmatch()
   ↓
TOÀN BỘ
```

Cụ thể:

```python
re.search(pattern, text)
```

→ tìm pattern ở bất kỳ đâu.

```python
re.match(pattern, text)
```

→ pattern phải bắt đầu ở đầu string.

```python
re.fullmatch(pattern, text)
```

→ toàn bộ string phải phù hợp.

Và trong code thực tế:

```text
Crawler / Text extraction
        ↓
     search()

Parse từng dòng có format cố định
        ↓
      match()

Validation
        ↓
    fullmatch()
```

**Buổi 7 — `findall()`** sẽ giải quyết bài toán mà `search()` chưa làm được: thay vì lấy **một match đầu tiên**, chúng ta sẽ lấy **tất cả các kết quả**. Đây là bước rất quan trọng để parse danh sách chapter, URL, số điện thoại, email, ID...
