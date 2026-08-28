# Buổi 2 — Character Class trong Python `re`

Hôm nay chúng ta học **Character Class** — một trong những nền tảng quan trọng nhất của Regex.

Mục tiêu sau buổi này, bạn phải đọc được những pattern như:

```regex
[a-z]
[0-9]
[^0-9]
\d
\w
\s
```

và hiểu chính xác Regex đang làm gì.

---

# 1. Character Class là gì?

Character Class cho phép chúng ta nói:

> "Tại vị trí này, tôi chấp nhận một trong những ký tự thuộc tập này."

Cú pháp:

```regex
[...]
```

Ví dụ:

```python
import re

text = "cat"

match = re.search(r"[abc]", text)

print(match.group())
```

Kết quả:

```text
c
```

Regex:

```regex
[abc]
```

nghĩa là:

```text
a hoặc b hoặc c
```

Nó chỉ match **một ký tự**.

---

# 2. `[abc]`

Ví dụ:

```python
import re

text = "hello"

match = re.search(r"[aeiou]", text)

print(match.group())
```

Output:

```text
e
```

Pattern:

```regex
[aeiou]
```

nghĩa là:

```text
a
e
i
o
u
```

Chỉ cần một ký tự trong tập đó xuất hiện.

---

## Quan trọng

Regex:

```regex
[abc]
```

không có nghĩa:

```text
abc
```

Nó có nghĩa:

```text
a hoặc b hoặc c
```

Ví dụ:

```python
re.search(r"[abc]", "dog")
```

→ `None`

Nhưng:

```python
re.search(r"[abc]", "cat")
```

→ match `"c"`

---

# 3. Character Class + Quantifier

Đây là lúc Regex bắt đầu mạnh.

```regex
[abc]+
```

nghĩa là:

> Một hoặc nhiều ký tự liên tiếp thuộc `a`, `b`, `c`.

Ví dụ:

```python
import re

text = "aaabbcxxx"

match = re.search(r"[abc]+", text)

print(match.group())
```

Kết quả:

```text
aaabbc
```

Vì:

```text
aaabbc xxx
^^^^^^
```

đều thuộc character class `[abc]`.

---

# 4. Range

Thay vì viết:

```regex
[abcdefghijklmnopqrstuvwxyz]
```

ta có thể viết:

```regex
[a-z]
```

Ví dụ:

```python
import re

text = "Hello Python"

match = re.search(r"[a-z]+", text)

print(match.group())
```

Kết quả:

```text
ello
```

Bởi vì:

```regex
[a-z]
```

chỉ match chữ thường ASCII từ `a` đến `z`.

---

# 5. `[A-Z]`

Tương tự:

```regex
[A-Z]
```

match chữ hoa:

```text
A
B
C
...
Z
```

Ví dụ:

```python
text = "hello WORLD"

match = re.search(r"[A-Z]+", text)

print(match.group())
```

Output:

```text
WORLD
```

---

# 6. `[0-9]`

Match một chữ số:

```regex
[0-9]
```

Ví dụ:

```python
text = "Chapter 123"

match = re.search(r"[0-9]+", text)

print(match.group())
```

Output:

```text
123
```

`[0-9]` và `\d` thường được dùng cho mục đích tương tự, nhưng chúng **không hoàn toàn giống nhau** trong mọi chế độ/Unicode.

Trong Python 3, `\d` mặc định có phạm vi Unicode rộng hơn `[0-9]`.

Ví dụ:

```python
r"\d+"
```

thường là lựa chọn tiện dụng khi bạn muốn "digit" theo định nghĩa Unicode của Python.

Còn:

```python
r"[0-9]+"
```

rõ ràng là **chỉ ASCII 0–9**.

---

# 7. Nhiều range

Ta có thể kết hợp:

```regex
[a-zA-Z]
```

nghĩa là:

```text
a-z
hoặc
A-Z
```

Ví dụ:

```python
text = "123Python456"

match = re.search(r"[a-zA-Z]+", text)

print(match.group())
```

Output:

```text
Python
```

---

# 8. `[a-zA-Z0-9]`

Rất phổ biến:

```regex
[a-zA-Z0-9]
```

nghĩa là:

```text
chữ thường
+
chữ hoa
+
chữ số
```

Ví dụ:

```python
text = "abc123XYZ"

match = re.search(r"[a-zA-Z0-9]+", text)

print(match.group())
```

Output:

```text
abc123XYZ
```

Pattern này thường xuất hiện khi xử lý:

* username
* ID
* slug
* token
* mã sản phẩm

---

# 9. Phủ định với `^`

Đây là một điểm **cực kỳ quan trọng**.

Khi `^` đứng ngay sau `[`:

```regex
[^abc]
```

nghĩa là:

> Một ký tự **không phải** `a`, `b`, hoặc `c`.

Ví dụ:

```python
import re

text = "apple"

match = re.search(r"[^abc]", text)

print(match.group())
```

Kết quả:

```text
p
```

Bởi vì:

```text
a → bị loại
p → được phép
```

---

# 10. `[^\d]`

Ví dụ:

```python
text = "123abc"

match = re.search(r"[^\d]+", text)

print(match.group())
```

Kết quả:

```text
abc
```

Ý nghĩa:

```regex
[^\d]
```

= một ký tự không phải digit.

---

# 11. Một lỗi rất phổ biến

So sánh:

```regex
[^0-9]
```

với:

```regex
^0-9
```

Hai cái hoàn toàn khác nhau.

### `[ ^0-9 ]`

```regex
[^0-9]
```

nghĩa là:

> Không phải số.

### `^0-9`

```regex
^0-9
```

nghĩa là:

> Chuỗi bắt đầu bằng `0-9`.

`^` có **hai vai trò khác nhau** tùy vị trí.

---

# 12. Dấu `-`

Trong Character Class:

```regex
[a-z]
```

dấu `-` biểu diễn range.

Nhưng nếu muốn match dấu `-` thật thì phải cẩn thận.

Ví dụ:

```regex
[-a-z]
```

Ở đầu class, `-` được hiểu như literal.

Hoặc:

```regex
[a-z-]
```

Cũng có thể dùng:

```regex
[a\-z]
```

Nhưng cách dễ đọc thường là đặt `-` ở đầu/cuối class.

---

# 13. Dấu `.` trong Character Class

Bên ngoài:

```regex
.
```

có ý nghĩa đặc biệt: match gần như bất kỳ ký tự nào trừ newline mặc định.

Nhưng bên trong:

```regex
[.]
```

thì `.` chỉ là **dấu chấm literal**.

Ví dụ:

```python
text = "example.com"

match = re.search(r"[.]", text)

print(match.group())
```

Output:

```text
.
```

---

# 14. `\d` — digit

Pattern:

```regex
\d
```

thường dùng để match một chữ số.

Ví dụ:

```python
text = "Chapter 123"

match = re.search(r"\d+", text)

print(match.group())
```

Output:

```text
123
```

So sánh:

```regex
\d+
```

với:

```regex
[0-9]+
```

Trong nhiều bài toán thông thường chúng cho kết quả giống nhau.

Nhưng:

```regex
[0-9]
```

rõ ràng hơn nếu yêu cầu chính xác là ASCII `0–9`.

---

# 15. `\D`

Ngược lại:

```regex
\D
```

nghĩa là:

> Không phải digit.

Ví dụ:

```python
text = "123abc"

match = re.search(r"\D+", text)

print(match.group())
```

Output:

```text
abc
```

Có thể nhớ:

```text
\d → digit
\D → NOT digit
```

---

# 16. `\w` — word character

Pattern:

```regex
\w
```

thường match:

```text
chữ
số
_
```

Trong Python 3, mặc định nó có tính đến Unicode.

Ví dụ:

```python
text = "hello_123"

match = re.search(r"\w+", text)

print(match.group())
```

Output:

```text
hello_123
```

---

# 17. `\W`

Ngược lại:

```regex
\W
```

nghĩa là:

> Không phải word character.

Ví dụ:

```python
text = "hello world"

match = re.search(r"\W+", text)

print(match.group())
```

Output:

```text
 
```

Nó match khoảng trắng giữa `hello` và `world`.

---

# 18. `\s` — whitespace

`\s` match whitespace.

Ví dụ:

```python
text = "hello   world"

match = re.search(r"\s+", text)

print(repr(match.group()))
```

Output:

```text
'   '
```

Whitespace có thể bao gồm:

```text
space
\t
\n
\r
...
```

Do đó:

```regex
\s+
```

rất hữu ích khi parse text không ổn định.

Ví dụ:

```text
Chapter    123
Chapter 123
Chapter\t123
```

đều có thể xử lý bằng:

```regex
Chapter\s+\d+
```

---

# 19. `\S`

Ngược lại:

```regex
\S
```

= không phải whitespace.

Ví dụ:

```python
text = "hello world"

match = re.search(r"\S+", text)

print(match.group())
```

Output:

```text
hello
```

---

# 20. Bảng ghi nhớ

| Regex         | Ý nghĩa                                 |
| ------------- | --------------------------------------- |
| `[abc]`       | `a` hoặc `b` hoặc `c`                   |
| `[^abc]`      | Không phải `a/b/c`                      |
| `[a-z]`       | Chữ thường ASCII                        |
| `[A-Z]`       | Chữ hoa ASCII                           |
| `[0-9]`       | Số ASCII                                |
| `[a-zA-Z]`    | Chữ ASCII                               |
| `[a-zA-Z0-9]` | Chữ hoặc số ASCII                       |
| `\d`          | Digit                                   |
| `\D`          | Không phải digit                        |
| `\w`          | Word character                          |
| `\W`          | Không phải word character               |
| `\s`          | Whitespace                              |
| `\S`          | Không phải whitespace                   |
| `.`           | Gần như mọi ký tự, trừ newline mặc định |

Một quy tắc cực kỳ hữu ích:

```text
\d  ↔  \D
\w  ↔  \W
\s  ↔  \S
```

Chữ hoa thường mang ý nghĩa **phủ định**.

---

# 21. Áp dụng vào crawler truyện

Đây là phần tôi muốn bạn đặc biệt chú ý.

Giả sử crawler lấy được:

```python
text = "Chapter 123: Tam Niên Chi Ước"
```

Ta muốn lấy số chapter.

```python
import re

match = re.search(r"\d+", text)

if match:
    chapter = match.group()
    print(chapter)
```

Output:

```text
123
```

Nhưng website có thể trả:

```text
Chapter    123
```

hoặc:

```text
Chapter: 123
```

hoặc:

```text
Chapter\t123
```

Ta có thể dùng:

```regex
Chapter\D+\d+
```

Ví dụ:

```python
text = "Chapter: 123"

match = re.search(r"Chapter\D+\d+", text)

if match:
    print(match.group())
```

Output:

```text
Chapter: 123
```

---

# 22. Một ví dụ thực tế hơn

Giả sử:

```python
text = """
Tên truyện: Đấu Phá Thương Khung
Chapter: 123
Tác giả: Thiên Tằm Thổ Đậu
"""
```

Ta muốn xác định dòng chapter:

```python
match = re.search(r"Chapter\s*:\s*\d+", text)

print(match.group())
```

Output:

```text
Chapter: 123
```

Phân tích:

```regex
Chapter
\s*
:
\s*
\d+
```

Trong đó:

```text
\s* → có thể có hoặc không có whitespace
\d+ → một hoặc nhiều chữ số
```

Regex này xử lý được:

```text
Chapter:123
Chapter: 123
Chapter : 123
Chapter    :    123
```

---

# 23. Một khái niệm rất quan trọng: Regex không hiểu "ý nghĩa"

Regex:

```regex
\d+
```

không hiểu:

> Đây là chapter.

Nó chỉ hiểu:

> Đây là một hoặc nhiều digit.

Đây là lý do kiến trúc parser tốt thường là:

```text
HTML
 ↓
Selectolax / BeautifulSoup
 ↓
Text
 ↓
Regex
 ↓
Structured data
```

Regex làm nhiệm vụ **pattern matching**, không nên biến thành toàn bộ parser.

---

# 24. Bài tập Buổi 2

## Bài 1 — Character Class

Cho:

```python
text = "abc123xyz"
```

Tìm chuỗi chữ cái đầu tiên bằng:

```python
re.search()
```

Gợi ý:

```regex
[a-z]+
```

Kết quả:

```text
abc
```

---

## Bài 2 — Chữ hoa

```python
text = "python PYTHON Java"
```

Lấy:

```text
PYTHON
```

Dùng:

```regex
[A-Z]+
```

---

## Bài 3 — Số

```python
text = "Book ID: 12345"
```

Lấy:

```text
12345
```

---

## Bài 4 — Không phải số

```python
text = "123ABC"
```

Dùng:

```regex
\D+
```

để lấy:

```text
ABC
```

---

## Bài 5 — Whitespace

Cho:

```python
text = "Chapter     123"
```

Viết Regex tìm toàn bộ:

```text
Chapter     123
```

Gợi ý:

```regex
Chapter\s+\d+
```

---

## Bài 6 — Thực chiến

Website có thể trả về:

```text
Chapter 123
Chapter: 124
Chapter    :    125
```

Viết **một Regex duy nhất** có thể match cả ba dạng.

Gợi ý:

```regex
Chapter\s*:?\s*\d+
```

---

## Bài 7 — Challenge

Cho:

```python
text = """
Novel: Đấu Phá Thương Khung
Chapter: 123
Views: 12,345
Author: Thiên Tằm Thổ Đậu
"""
```

Viết Regex để tìm:

```text
12,345
```

Gợi ý: character class:

```regex
[0-9,]+
```

---

# Bài tập nâng cao

Thử tự viết Regex cho các chuỗi sau:

```text
Chapter 001
Chapter 002
Chapter 120
Chapter 999
```

Mục tiêu: chỉ match những chuỗi có dạng:

```text
Chapter + whitespace + 3 chữ số
```

Ví dụ:

```text
Chapter 123       → match
Chapter 001       → match
Chapter 12        → không match
Chapter ABC       → không match
Chapter 1234      → không match
```

Regex gợi ý:

```regex
Chapter\s+\d{3}
```

Nhưng **hãy chú ý:** pattern này vẫn có thể match một phần của `Chapter 1234`. Đây chính là vấn đề chúng ta sẽ giải quyết ở **Buổi 4 — Anchor (`^`, `$`, `\A`, `\Z`, `\b`)**.

Ở **Buổi 3**, trước khi học Anchor, chúng ta sẽ học một thứ cực kỳ quan trọng: **Quantifier `*`, `+`, `?`, `{n}`, `{n,m}` và đặc biệt là Greedy vs Lazy**.
