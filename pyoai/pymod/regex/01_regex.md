Được. Tôi sẽ dạy bạn **`re` — Regular Expression trong Python** theo hướng **lập trình thực tế**, không chỉ học cú pháp.

Vì bạn đã học khá nhiều Python nâng cao, tôi đề xuất một roadmap từ nền tảng → regex nâng cao → ứng dụng vào crawler/parser/CLI.

# Giáo trình Python `re` — Regex từ cơ bản đến nâng cao

## Phần I — Regex Foundation

**Buổi 1 — Regex là gì?**

* Regular Expression là gì?
* Regex engine hoạt động thế nào?
* `import re`
* `re.search()`
* `re.match()`
* `re.fullmatch()`
* Pattern và string
* Raw string `r"..."`

**Buổi 2 — Character và Character Class**

* Ký tự thông thường
* `.`
* `[abc]`
* `[^abc]`
* `[a-z]`
* `[0-9]`
* Unicode và tiếng Việt

**Buổi 3 — Quantifier**

* `*`
* `+`
* `?`
* `{n}`
* `{n,m}`
* Greedy
* Lazy

**Buổi 4 — Anchor**

* `^`
* `$`
* `\A`
* `\Z`
* Word boundary `\b`
* `\B`

**Buổi 5 — Regex Groups**

* `(abc)`
* Capturing group
* `group()`
* `groups()`
* `group(1)`
* Named group `(?P<name>...)`

---

# Phần II — Python `re` API

**Buổi 6 — `search()` vs `match()` vs `fullmatch()`**

**Buổi 7 — `findall()`**

**Buổi 8 — `finditer()`**

**Buổi 9 — `split()`**

**Buổi 10 — `sub()` và `subn()`**

**Buổi 11 — Compiled Regex**

```python
pattern = re.compile(...)
```

**Buổi 12 — Flags**

* `re.IGNORECASE`
* `re.MULTILINE`
* `re.DOTALL`
* `re.VERBOSE`
* `re.ASCII`

---

# Phần III — Advanced Regex

**Buổi 13 — Alternation**

```regex
cat|dog
```

**Buổi 14 — Non-capturing Group**

```regex
(?:...)
```

**Buổi 15 — Lookahead**

```regex
(?=...)
(?!...)
```

**Buổi 16 — Lookbehind**

```regex
(?<=...)
(?<!...)
```

**Buổi 17 — Backreference**

```regex
(\w+)\s+\1
```

**Buổi 18 — Conditional và Advanced Group**

**Buổi 19 — Greedy vs Lazy Deep Dive**

**Buổi 20 — Regex Debugging**

---

# Phần IV — Regex thực chiến

**Buổi 21 — Validate dữ liệu**

* Email
* Username
* Password
* Phone
* URL
* IP

**Buổi 22 — Parse log**

```text
2026-08-29 10:30:12 INFO user=admin action=login
```

**Buổi 23 — Extract dữ liệu từ HTML/text**

**Buổi 24 — Làm sạch text**

**Buổi 25 — Regex + `pathlib`**

**Buổi 26 — Regex + file**

**Buổi 27 — Regex + CLI**

**Buổi 28 — Regex + crawler**

---

# Phần V — Regex chuyên sâu

**Buổi 29 — Regex trong parser architecture**

**Buổi 30 — Regex Performance**

**Buổi 31 — Catastrophic Backtracking**

**Buổi 32 — Viết Regex dễ bảo trì**

**Buổi 33 — `re.VERBOSE`**

**Buổi 34 — Testing Regex với `pytest`**

**Buổi 35 — Xây Regex Validator**

**Buổi 36 — Mini Project: Text Parser**

---

# Phần VI — Project

Cuối khóa chúng ta sẽ làm một project:

```text
Input
  ↓
Text
  ↓
Regex Scanner
  ↓
Tokenizer
  ↓
Parser
  ↓
Structured Data
```

Ví dụ input:

```text
[2026-08-29 10:20:31] INFO
user=admin
action=login
ip=192.168.1.10
```

Regex parser sẽ tạo:

```python
{
    "timestamp": "2026-08-29 10:20:31",
    "level": "INFO",
    "user": "admin",
    "action": "login",
    "ip": "192.168.1.10",
}
```

Sau đó nâng cấp thành:

```text
Regex Parser
     ↓
Domain Model
     ↓
Repository
     ↓
SQLite
     ↓
CLI
```

Điều này sẽ rất hợp với những thứ bạn đang học như **crawler, parser, SQLite, CLI, Clean Architecture và DDD**.

---

# Buổi 1 — Regex là gì?

## 1. Regex dùng để làm gì?

Regex là cách mô tả **một mẫu (pattern) của chuỗi**.

Ví dụ:

```text
Hello Python
Hello World
Hello Alice
```

Nếu muốn tìm tất cả chuỗi bắt đầu bằng:

```text
Hello
```

ta có thể dùng:

```python
import re

text = "Hello Python"

result = re.search(r"Hello", text)

print(result)
```

Nếu tìm thấy:

```text
<re.Match object; ...>
```

Nếu không tìm thấy:

```python
None
```

---

## 2. `re.search()`

Đây là API đầu tiên cần nắm.

```python
import re

text = "I love Python"

match = re.search(r"Python", text)

if match:
    print("Found")
```

Output:

```text
Found
```

Điểm quan trọng:

```python
re.search(pattern, string)
```

Trong đó:

```text
pattern
   ↓
r"Python"

string
   ↓
"I love Python"
```

---

## 3. Tại sao dùng `r"..."`?

Bạn sẽ thường thấy:

```python
r"\d+"
```

thay vì:

```python
"\\d+"
```

Ví dụ:

```python
pattern = r"\d+"
```

`r` nghĩa là **raw string**.

Điều này đặc biệt hữu ích với regex vì regex sử dụng rất nhiều:

```text
\
```

Ví dụ:

```regex
\d
\s
\w
\b
```

Nếu không dùng raw string, Python cũng có cơ chế escape riêng.

Vì vậy, hãy tạo thói quen:

```python
r"..."
```

khi viết regex.

---

# 4. Regex đầu tiên

Tìm số:

```python
import re

text = "Python 3.13"

match = re.search(r"\d+", text)

print(match.group())
```

Output:

```text
3
```

Ở đây:

```regex
\d
```

nghĩa là một chữ số.

Còn:

```regex
+
```

nghĩa là **một hoặc nhiều lần**.

Do đó:

```regex
\d+
```

có nghĩa:

> Một hoặc nhiều chữ số liên tiếp.

---

# 5. `Match` object

Đây là thứ rất quan trọng.

```python
import re

text = "Python 3.13"

match = re.search(r"\d+", text)

print(match)
print(match.group())
print(match.start())
print(match.end())
```

Có thể nhận:

```text
<re.Match object; ...>
3
7
8
```

Ta có:

```text
Python 3.13
0123456789
       ↑
       3
```

`start()`:

```python
match.start()
```

cho vị trí bắt đầu.

`end()`:

```python
match.end()
```

cho vị trí kết thúc **không bao gồm index đó**.

`group()`:

```python
match.group()
```

cho text được match.

---

# 6. Một ví dụ thực tế

Giả sử crawler của bạn lấy được:

```python
text = """
Chapter 123
Views: 45678
Comments: 120
"""
```

Ta có thể tìm chapter:

```python
import re

match = re.search(r"Chapter\s+\d+", text)

if match:
    print(match.group())
```

Output:

```text
Chapter 123
```

Regex:

```regex
Chapter\s+\d+
```

phân tích:

```text
Chapter
   ↓
\s+
   ↓
\d+
```

Tức là:

```text
"Chapter"
+
"một hoặc nhiều whitespace"
+
"một hoặc nhiều chữ số"
```

---

# 7. Regex không chỉ để validate

Một hiểu lầm phổ biến:

> Regex = kiểm tra email/password.

Không chỉ vậy.

Trong Python backend/crawler/parser, Regex thường dùng để:

```text
Extract
  ↓
Transform
  ↓
Validate
  ↓
Normalize
  ↓
Parse
```

Ví dụ crawler:

```python
html
 ↓
BeautifulSoup / Selectolax
 ↓
text
 ↓
Regex
 ↓
extract metadata
```

Ví dụ:

```text
Chapter 001
Chapter 002
Chapter 003
```

Regex có thể lấy:

```python
1
2
3
```

Hoặc:

```text
Volume 12 - Chapter 123: The Beginning
```

lấy:

```python
volume = 12
chapter = 123
title = "The Beginning"
```

Đây mới là cách chúng ta sẽ học `re`.

---

# Bài tập Buổi 1

### Bài 1

Tìm số đầu tiên trong:

```python
text = "Python version 3.13"
```

---

### Bài 2

Tìm số trong:

```python
text = "Chapter 125"
```

Kết quả mong muốn:

```text
125
```

---

### Bài 3

Tìm tất cả chữ số liên tiếp trong:

```python
text = "Book 12 has 350 pages and 20 chapters"
```

Chưa cần `findall()`.

Chỉ cần dùng:

```python
re.search()
```

để lấy số đầu tiên.

---

### Bài 4 — thực tế hơn

Cho:

```python
text = """
Story: Đấu Phá Thương Khung
Chapter: 123
Author: Thiên Tằm Thổ Đậu
"""
```

Hãy viết regex để lấy:

```text
123
```

---

### Bài 5 — Challenge

Cho:

```python
text = "Chapter 123: Tam Niên Chi Ước"
```

Hãy lấy:

```text
Chapter 123
```

**Gợi ý:**

```regex
Chapter\s+\d+
```

---

Buổi tiếp theo chúng ta sẽ học **Buổi 2 — Character Class**, và bắt đầu đi sâu vào:

```regex
.
[]
[^]
[a-z]
[A-Z]
[0-9]
\d
\w
\s
```

đây là nền móng để thực sự đọc được Regex.
