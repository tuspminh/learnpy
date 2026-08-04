# Buổi 29. Regular Expression (Regex) trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu bản chất của Regular Expression (Regex).
> * Thành thạo module `re`.
> * Biết khi nào nên dùng Regex, khi nào không.
> * Thành thạo `match()`, `search()`, `fullmatch()`, `findall()`, `finditer()`.
> * Sử dụng `split()`, `sub()`, `subn()`.
> * Hiểu Groups, Named Groups.
> * Thành thạo Lookahead, Lookbehind.
> * Áp dụng Regex trong crawler, parser, validation và xử lý văn bản.

---

# 1. Regex là gì?

Regular Expression (Regex) là **một ngôn ngữ mô tả mẫu chuỗi (pattern)**.

Ví dụ:

Chuỗi:

```text
Python 3.12
```

Regex:

```regex
\d+
```

Kết quả:

```text
3
12
```

Regex không tìm theo giá trị cụ thể, mà tìm theo **quy luật**.

---

# 2. Khi nào dùng Regex?

Regex rất mạnh khi:

* Kiểm tra email
* Kiểm tra số điện thoại
* Trích xuất URL
* Trích xuất HTML
* Tìm số
* Tìm ngày tháng
* Parse log
* Crawler

Ví dụ:

```
Giá sản phẩm: 1.250.000 VNĐ
```

Regex:

```regex
\d[\d.]*
```

Kết quả:

```
1.250.000
```

---

# 3. Module `re`

Python có sẵn:

```python
import re
```

Không cần cài đặt.

---

# 4. Pattern đầu tiên

```python
import re

text = "Python"

result = re.match("Python", text)

print(result)
```

Output

```
<re.Match object>
```

Nếu không khớp

```python
re.match("Java", text)
```

↓

```
None
```

---

# 5. `match()`

Chỉ kiểm tra **đầu chuỗi**.

```python
import re

text = "Python Programming"

print(re.match("Python", text))
```

Đúng.

Nhưng

```python
re.match("Programming", text)
```

↓

```
None
```

vì không nằm ở đầu chuỗi.

---

# 6. `search()`

Tìm ở **mọi vị trí**.

```python
import re

text = "Python Programming"

print(re.search("Programming", text))
```

↓

Có kết quả.

---

# 7. `fullmatch()`

Toàn bộ chuỗi phải khớp.

```python
import re

print(re.fullmatch(r"\d+", "12345"))
```

↓

Có.

Nhưng

```python
re.fullmatch(r"\d+", "123abc")
```

↓

```
None
```

---

# 8. `findall()`

Tìm tất cả.

```python
import re

text = "I have 12 apples and 35 oranges"

print(re.findall(r"\d+", text))
```

Output

```python
["12", "35"]
```

---

# 9. `finditer()`

Khác `findall()`.

```python
import re

text = "12 34 56"

for m in re.finditer(r"\d+", text):
    print(m.group(), m.start(), m.end())
```

Output

```
12 0 2
34 3 5
56 6 8
```

Ưu điểm:

Có vị trí.

---

# 10. Ký tự đặc biệt

## `.`

Khớp mọi ký tự.

```regex
a.c
```

Khớp

```
abc

axc

a1c
```

---

## `*`

0 hoặc nhiều.

```regex
ab*
```

Khớp

```
a

ab

abb

abbbb
```

---

## `+`

1 hoặc nhiều.

```regex
ab+
```

Khớp

```
ab

abb
```

Không khớp

```
a
```

---

## `?`

0 hoặc 1.

```
ab?
```

Khớp

```
a

ab
```

---

# 11. Character Class

```regex
[abc]
```

↓

```
a

b

c
```

---

```regex
[a-z]
```

↓

mọi chữ thường.

---

```regex
[A-Z]
```

↓

mọi chữ hoa.

---

```regex
[0-9]
```

↓

mọi số.

---

```regex
[a-zA-Z0-9]
```

↓

mọi ký tự chữ và số.

---

# 12. Shortcut

## `\d`

Số

```
0-9
```

---

## `\D`

Không phải số.

---

## `\w`

```
a-zA-Z0-9_
```

---

## `\W`

Ngược lại.

---

## `\s`

Whitespace.

```
space

tab

newline
```

---

## `\S`

Không phải khoảng trắng.

---

# 13. Neo (`^`, `$`)

Đầu chuỗi

```regex
^Python
```

Cuối chuỗi

```regex
Python$
```

Ví dụ

```python
re.search("^Hello", "Hello World")
```

Có.

---

# 14. Biên từ (`\b`)

Ví dụ

```
cat
```

Trong

```
cat
```

Có.

Trong

```
category
```

Không.

Regex

```regex
\bcat\b
```

---

# 15. Group

```python
import re

text = "2026-08-01"

m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)

print(m.group(1))

print(m.group(2))

print(m.group(3))
```

Output

```
2026

08

01
```

---

# 16. Named Group

```python
m = re.search(
    r"(?P<year>\d{4})"
    r"-(?P<month>\d{2})"
    r"-(?P<day>\d{2})",
    text,
)

print(m.group("year"))
```

Rõ nghĩa hơn.

---

# 17. `split()`

```python
import re

text = "A,B;C D"

print(re.split(r"[,; ]", text))
```

Output

```
['A', 'B', 'C', 'D']
```

---

# 18. `sub()`

Thay thế.

```python
import re

text = "Python 3.12"

print(re.sub(r"\d", "*", text))
```

↓

```
Python *.**
```

---

# 19. `subn()`

```python
text = "111222"

print(re.subn("1", "A", text))
```

Output

```python
("AAA222", 3)
```

Số thứ hai là số lần thay thế.

---

# 20. Lookahead

Ví dụ

```
100USD
```

Muốn lấy

```
100
```

Regex

```regex
\d+(?=USD)
```

---

# 21. Negative Lookahead

```regex
\d+(?!USD)
```

---

# 22. Lookbehind

```
USD100
```

Regex

```regex
(?<=USD)\d+
```

↓

```
100
```

---

# 23. Negative Lookbehind

```regex
(?<!USD)\d+
```

---

# 24. Compile Pattern

Sai

```python
for line in lines:
    re.search(...)
```

Đúng

```python
pattern = re.compile(r"\d+")

for line in lines:
    pattern.search(line)
```

Nhanh hơn nhiều nếu dùng lặp đi lặp lại.

---

# 25. Flags

Ignore Case

```python
re.search("python", "Python", re.IGNORECASE)
```

---

Multiline

```python
re.MULTILINE
```

---

Dot All

```python
re.DOTALL
```

`.`

sẽ khớp cả newline.

---

Verbose

```python
re.VERBOSE
```

Cho phép viết regex nhiều dòng và có chú thích.

Ví dụ:

```python
pattern = re.compile(
    r"""
    ^
    (?P<year>\d{4})  # năm
    -
    (?P<month>\d{2}) # tháng
    -
    (?P<day>\d{2})   # ngày
    $
""",
    re.VERBOSE,
)
```

---

# 26. Email Validation

```python
pattern = re.compile(
    r"^[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+"
    r"\.[A-Za-z]{2,}$"
)
```

---

# 27. Phone Number

```python
pattern = re.compile(
    r"^(0|\+84)"
    r"\d{9}$"
)
```

---

# 28. URL

```python
pattern = re.compile(r"https?://[^\s]+")
```

---

# 29. Crawler Example

HTML

```html
<a href="/story/123">ABC</a>
```

Regex

```python
re.search(r'href="([^"]+)"', html)
```

Kết quả

```
/story/123
```

> **Lưu ý quan trọng:** Regex chỉ phù hợp để trích xuất các mẫu đơn giản. Với HTML thực tế, nên dùng parser như `html.parser`, BeautifulSoup, lxml hoặc Parsel thay vì Regex, vì HTML có thể lồng thẻ và không phải là ngôn ngữ chính quy.

---

# 30. Log Parser

Log

```
2026-08-01 ERROR Database failed
```

Regex

```python
r"(\d{4}-\d{2}-\d{2})"

r"\s+"

r"(\w+)"

r"\s+"

r"(.*)"
```

---

# 31. Best Practices

## ✔ Dùng Raw String

Đúng

```python
r"\d+"
```

Sai

```python
"\\d+"
```

Raw string giúp regex dễ đọc hơn và tránh phải escape nhiều lần.

---

## ✔ Compile nếu dùng nhiều lần

```python
pattern = re.compile(...)
```

---

## ✔ Dùng Named Group

Đúng

```python
m.group("year")
```

Sai

```python
m.group(7)
```

---

## ✔ Không dùng Regex khi không cần

Sai

```python
re.search("Python", text)
```

Đúng

```python
"Python" in text
```

Hoặc:

```python
text.startswith("Python")
text.endswith(".txt")
text.split(",")
```

Regex rất mạnh nhưng cũng phức tạp và có thể chậm hơn các thao tác chuỗi thông thường.

---

# 32. Mini Project - Log Analyzer

Cấu trúc:

```text
log_analyzer/

├── app.log
└── analyzer.py
```

**app.log**

```
2026-08-01 INFO Server Start
2026-08-01 ERROR Database Error
2026-08-02 WARNING Disk Full
```

Chương trình cần:

* Đếm số lượng `INFO`.
* Đếm số lượng `WARNING`.
* Đếm số lượng `ERROR`.
* Liệt kê tất cả các ngày xuất hiện trong log.
* Trích xuất toàn bộ nội dung thông báo.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Bản chất của Regular Expression.
* Các hàm quan trọng trong module `re`.
* Ký tự đặc biệt, character class và shortcut.
* Neo (`^`, `$`) và biên từ (`\b`).
* Groups và Named Groups.
* Lookahead và Lookbehind.
* `split()`, `sub()`, `subn()`.
* `re.compile()` và các cờ (`IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`).
* Các ứng dụng thực tế trong validation, crawler và phân tích log.

# Bài tập thực hành

### Bài 1

Viết chương trình trích xuất tất cả số nguyên từ một đoạn văn bằng `findall()`.

### Bài 2

Viết hàm kiểm tra địa chỉ email hợp lệ bằng `fullmatch()` và biểu thức chính quy.

### Bài 3

Đọc một file log, sử dụng `finditer()` để in ra:

* Ngày.
* Mức log (`INFO`, `ERROR`, ...).
* Nội dung thông báo.

### Bài 4

Viết chương trình thay thế tất cả số điện thoại trong một đoạn văn bằng chuỗi `"***"` sử dụng `re.sub()`.

### Bài 5

Viết một `re.compile(..., re.VERBOSE)` để phân tích chuỗi ngày theo định dạng `YYYY-MM-DD` và trả về `year`, `month`, `day` bằng **Named Groups**.

### Bài 6 (Thử thách)

Xây dựng **Text Extractor** hỗ trợ:

```text
===== Text Extractor =====
1. Trích xuất Email
2. Trích xuất URL
3. Trích xuất Số điện thoại
4. Trích xuất Ngày tháng
5. Thống kê số lần xuất hiện
6. Thoát
```

Chương trình nhận một đoạn văn bản đầu vào, sử dụng các biểu thức chính quy đã học để trích xuất và thống kê kết quả theo từng loại dữ liệu.

---

## Chuẩn bị cho buổi sau

Ở **Buổi 30**, chúng ta sẽ học **Iterator**, bao gồm:

* Iterator Protocol (`__iter__()`, `__next__()`).
* Hàm `iter()` và `next()`.
* Tự xây dựng Iterator.
* `StopIteration`.
* Iterator vs Iterable.
* Ứng dụng Iterator trong đọc file lớn, xử lý dữ liệu theo luồng (streaming) và thiết kế thư viện Python hiệu quả.

> **Lưu ý:** Mặc dù bạn đã học chuyên sâu về Iterator trong một lộ trình khác, buổi này sẽ ôn lại ở mức **Python Intermediate**, tập trung vào việc sử dụng đúng và hiệu quả trong các chương trình Python thông thường, làm nền tảng trước khi sang **Generator (Buổi 31)** và **Context Manager (Buổi 34)**.
