# Buổi 3 — Quantifier trong Python `re`

Hôm nay chúng ta học **Quantifier** — tức là cách nói cho Regex biết:

> “Ký tự/pattern này được phép xuất hiện bao nhiêu lần?”

Đây là phần cực kỳ quan trọng. Khi kết hợp **Character Class + Quantifier**, Regex bắt đầu trở nên thực sự mạnh.

---

# 1. Quantifier là gì?

Ví dụ:

```regex
\d
```

match **một** chữ số.

```text
1
```

Nhưng:

```text
12345
```

thì `\d` chỉ match một ký tự:

```text
12345
^
```

Muốn match nhiều chữ số liên tiếp, ta dùng:

```regex
\d+
```

Kết quả:

```text
12345
^^^^^
```

`+` chính là **quantifier**.

---

# 2. Các Quantifier quan trọng

| Quantifier | Ý nghĩa            |
| ---------- | ------------------ |
| `*`        | 0 hoặc nhiều       |
| `+`        | 1 hoặc nhiều       |
| `?`        | 0 hoặc 1           |
| `{n}`      | chính xác `n` lần  |
| `{n,}`     | ít nhất `n` lần    |
| `{n,m}`    | từ `n` đến `m` lần |

Đây là bảng bạn nên thuộc lòng.

---

# 3. `+` — một hoặc nhiều

Đây là quantifier bạn sẽ sử dụng rất thường xuyên.

```regex
\d+
```

nghĩa là:

> Một hoặc nhiều chữ số liên tiếp.

Ví dụ:

```python
import re

text = "Chapter 123"

match = re.search(r"\d+", text)

print(match.group())
```

Output:

```text
123
```

---

## `\d` vs `\d+`

```regex
\d
```

→ một digit.

```regex
\d+
```

→ một hoặc nhiều digit liên tiếp.

Ví dụ:

```text
12345
```

| Regex | Match   |
| ----- | ------- |
| `\d`  | `1`     |
| `\d+` | `12345` |

---

# 4. `*` — zero hoặc nhiều

Ví dụ:

```regex
a*
```

nghĩa là:

> `a` có thể xuất hiện 0 lần hoặc nhiều lần.

Do đó tất cả những chuỗi sau đều có thể match:

```text
""
"a"
"aa"
"aaa"
"aaaa"
```

Ví dụ:

```python
import re

for text in ["", "a", "aa", "aaa"]:
    match = re.fullmatch(r"a*", text)
    print(repr(text), bool(match))
```

Kết quả:

```text
'' True
'a' True
'aa' True
'aaa' True
```

Điểm quan trọng:

```regex
a*
```

**không bắt buộc phải có `a`.**

---

# 5. `+` khác `*` thế nào?

Đây là khác biệt cực kỳ quan trọng.

### `a*`

```text
0 hoặc nhiều a
```

### `a+`

```text
1 hoặc nhiều a
```

Ví dụ chuỗi rỗng:

```python
re.fullmatch(r"a*", "")
```

→ match.

Nhưng:

```python
re.fullmatch(r"a+", "")
```

→ không match.

---

# 6. `?` — zero hoặc one

```regex
a?
```

nghĩa là:

> `a` có thể xuất hiện 0 hoặc 1 lần.

Ví dụ:

```text
""
"a"
```

đều match.

Nhưng:

```text
"aa"
```

không match toàn bộ.

---

# 7. Ứng dụng cực kỳ thực tế của `?`

Giả sử website có:

```text
Chapter 123
Chapter: 123
```

Ta muốn `:` là optional.

Viết:

```regex
Chapter:?\s+\d+
```

Phần:

```regex
:?
```

nghĩa là:

```text
:
```

có thể có hoặc không.

Do đó match:

```text
Chapter 123
Chapter: 123
```

---

# 8. `{n}` — chính xác n lần

Ví dụ:

```regex
\d{3}
```

nghĩa là:

> Chính xác 3 chữ số.

Ví dụ:

```python
import re

text = "123"

match = re.fullmatch(r"\d{3}", text)

print(bool(match))
```

Output:

```text
True
```

---

Ví dụ:

```python
text = "1234"

match = re.fullmatch(r"\d{3}", text)

print(bool(match))
```

Output:

```text
False
```

Vì:

```text
1234
^^^
```

chỉ có 3 chữ số đầu, nhưng `fullmatch()` yêu cầu **toàn bộ chuỗi** phải phù hợp.

---

# 9. `{n,}` — ít nhất n lần

Ví dụ:

```regex
\d{3,}
```

nghĩa là:

> Ít nhất 3 chữ số.

Match:

```text
123
1234
12345
123456
```

Không match:

```text
12
1
```

Ví dụ:

```python
text = "123456"

match = re.fullmatch(r"\d{3,}", text)

print(match.group())
```

Output:

```text
123456
```

---

# 10. `{n,m}` — từ n đến m lần

Ví dụ:

```regex
\d{2,4}
```

nghĩa là:

> Từ 2 đến 4 chữ số.

Match:

```text
12
123
1234
```

Không match toàn bộ:

```text
1
12345
```

Ví dụ:

```python
for text in ["1", "12", "123", "1234", "12345"]:
    match = re.fullmatch(r"\d{2,4}", text)
    print(text, bool(match))
```

Kết quả:

```text
1 False
12 True
123 True
1234 True
12345 False
```

---

# 11. Quantifier áp dụng cho cái gì?

Đây là điểm rất quan trọng.

Regex:

```regex
abc+
```

**không phải**:

```text
abcabcabc
```

Nó có nghĩa:

```text
ab + ccc...
```

Tức là `+` chỉ áp dụng cho **ký tự ngay trước nó**.

Ví dụ:

```text
abccc
  ^^^
```

---

# 12. Muốn lặp cả nhóm thì dùng `()`

Ví dụ:

```regex
(ab)+
```

nghĩa là:

```text
ab
ab
ab
...
```

Match:

```text
ab
abab
ababab
```

Ví dụ:

```python
import re

text = "ababab"

match = re.fullmatch(r"(ab)+", text)

print(match.group())
```

Output:

```text
ababab
```

---

# 13. Quantifier + Character Class

Ví dụ:

```regex
[a-z]+
```

nghĩa là:

> Một hoặc nhiều chữ cái thường liên tiếp.

```python
text = "hello123"

match = re.search(r"[a-z]+", text)

print(match.group())
```

Output:

```text
hello
```

---

Tương tự:

```regex
[A-Z]+
```

→ một hoặc nhiều chữ hoa.

```regex
[0-9]+
```

→ một hoặc nhiều số.

```regex
[a-zA-Z]+
```

→ một hoặc nhiều chữ cái.

---

# 14. Quantifier + `\s`

Một pattern cực kỳ thực tế:

```regex
\s+
```

Nghĩa là:

> Một hoặc nhiều whitespace.

Ví dụ:

```text
Chapter 123
Chapter     123
Chapter        123
```

Ta có:

```regex
Chapter\s+\d+
```

---

# 15. `\s*` khác `\s+`

Đây là một vấn đề bạn sẽ gặp rất nhiều khi crawl website.

Giả sử:

```text
Chapter:123
```

Nếu dùng:

```regex
Chapter:\s+\d+
```

→ không match.

Vì `+` yêu cầu ít nhất một whitespace.

Nếu website có thể có hoặc không có whitespace:

```regex
Chapter:\s*\d+
```

`*` cho phép:

```text
0 whitespace
1 whitespace
2 whitespace
...
```

Do đó match:

```text
Chapter:123
Chapter: 123
Chapter:    123
```

---

# 16. Kết hợp `?`, `*`, `+`

Ví dụ website có thể trả:

```text
Chapter 123
Chapter: 123
Chapter : 123
Chapter    :    123
```

Ta có thể viết:

```regex
Chapter\s*:?\s*\d+
```

Phân tích:

```text
Chapter
   ↓
\s*      whitespace tùy chọn
   ↓
:?      dấu : tùy chọn
   ↓
\s*      whitespace tùy chọn
   ↓
\d+     một hoặc nhiều digit
```

Đây là kiểu Regex rất thực tế khi xử lý dữ liệu web không đồng nhất.

---

# 17. Greedy Quantifier

Bây giờ đến phần quan trọng hơn.

Các quantifier:

```regex
*
+
?
{n,m}
```

mặc định là **greedy**.

Greedy nghĩa là:

> Match nhiều nhất có thể, miễn là toàn bộ pattern vẫn có thể thành công.

Ví dụ:

```python
import re

text = "<b>Hello</b>"

match = re.search(r"<.*>", text)

print(match.group())
```

Kết quả:

```text
<b>Hello</b>
```

`.*` đã ăn:

```text
<b>Hello</b>
^^^^^^^^^^^^
```

Nó cố gắng lấy nhiều nhất có thể.

---

# 18. Lazy Quantifier

Đôi khi chúng ta không muốn greedy.

Ta có thể thêm:

```text
?
```

sau quantifier.

Ví dụ:

```regex
.*?
```

nghĩa là:

> Match ít nhất có thể.

Ví dụ:

```python
text = "<b>Hello</b>"

match = re.search(r"<.*?>", text)

print(match.group())
```

Output:

```text
<b>
```

---

# 19. Greedy vs Lazy

So sánh:

```regex
<.*>
```

và:

```regex
<.*?>
```

Input:

```text
<b>Hello</b>
```

### Greedy

```regex
<.*>
```

→

```text
<b>Hello</b>
^^^^^^^^^^^^
```

### Lazy

```regex
<.*?>
```

→

```text
<b>
^^^
```

---

# 20. Ví dụ crawler rất điển hình

Giả sử:

```python
text = """
<a>Chapter 1</a>
<a>Chapter 2</a>
<a>Chapter 3</a>
"""
```

Nếu bạn dùng:

```regex
<a>.*</a>
```

Greedy có thể lấy:

```text
<a>Chapter 1</a>
<a>Chapter 2</a>
<a>Chapter 3</a>
```

Không phải điều chúng ta muốn.

Nếu dùng:

```regex
<a>.*?</a>
```

thì có thể lấy từng đoạn ngắn nhất:

```text
<a>Chapter 1</a>
```

Đây chính là lý do **lazy quantifier** rất quan trọng.

> Tuy nhiên, với HTML thật, đừng biến Regex thành HTML parser. Bạn đã học Selectolax/BeautifulSoup, nên hãy dùng parser để hiểu cấu trúc HTML; Regex phù hợp hơn cho text patterns.

---

# 21. Các Lazy Quantifier

| Greedy  | Lazy     |
| ------- | -------- |
| `*`     | `*?`     |
| `+`     | `+?`     |
| `?`     | `??`     |
| `{n,m}` | `{n,m}?` |
| `{n,}`  | `{n,}?`  |

Ví dụ:

```regex
.*?
```

```regex
.+?
```

```regex
\d+?
```

---

# 22. Một ví dụ rất hay

```python
import re

text = "Chapter 123 and Chapter 456"

match = re.search(r"\d+", text)

print(match.group())
```

Output:

```text
123
```

Greedy `+` lấy:

```text
123
```

Nếu:

```python
match = re.search(r"\d+?", text)
```

thì lazy `+?` chỉ lấy **ít nhất có thể** để pattern thành công:

```text
1
```

Đây là ví dụ rất tốt để hiểu:

```text
greedy → nhiều nhất có thể
lazy   → ít nhất có thể
```

---

# 23. Một lỗi tư duy thường gặp

Nhiều người nghĩ:

```regex
.*
```

nghĩa là:

> mọi thứ.

Chính xác hơn:

```regex
.
```

match gần như bất kỳ ký tự nào **ngoại trừ newline theo mặc định**.

Còn:

```regex
.*
```

nghĩa là:

> zero hoặc nhiều ký tự bất kỳ phù hợp với `.`.

Nếu cần `.` match newline, có thể dùng:

```python
re.DOTALL
```

Ví dụ:

```python
pattern = re.compile(r".*", re.DOTALL)
```

Phần flags chúng ta sẽ học kỹ hơn sau.

---

# 24. `fullmatch()` rất hữu ích khi validate

Hãy nhớ:

```python
re.search()
```

tìm pattern **ở bất kỳ đâu**.

Trong khi:

```python
re.fullmatch()
```

yêu cầu **toàn bộ chuỗi** phù hợp.

Ví dụ:

```python
import re

text = "123"

print(bool(re.search(r"\d{3}", text)))
print(bool(re.fullmatch(r"\d{3}", text)))
```

Cả hai đều `True`.

Nhưng:

```python
text = "abc123xyz"

print(bool(re.search(r"\d{3}", text)))
print(bool(re.fullmatch(r"\d{3}", text)))
```

Kết quả:

```text
True
False
```

Vì `search()` chỉ cần tìm được `123`.

`fullmatch()` yêu cầu toàn bộ chuỗi phải là 3 chữ số.

---

# 25. Liên hệ với bài tập Buổi 2

Ta từng có:

```text
Chapter 1234
```

và pattern:

```regex
Chapter\s+\d{3}
```

Vấn đề:

```text
Chapter 1234
^^^^^^^^^^^^
```

Regex có thể match phần:

```text
Chapter 123
```

Đó là vì Regex chưa được yêu cầu phải kết thúc ở đó.

**Buổi 4 — Anchor** sẽ giải quyết vấn đề này bằng:

```regex
^
$
```

và:

```regex
\A
\Z
```

---

# 26. Cheat Sheet Buổi 3

```text
*       0 hoặc nhiều
+       1 hoặc nhiều
?       0 hoặc 1
{n}     chính xác n
{n,}    ít nhất n
{n,m}   từ n đến m

*?      lazy
+?      lazy
??      lazy
{n,m}?  lazy
```

Và:

```text
greedy → cố lấy nhiều nhất
lazy   → cố lấy ít nhất
```

---

# 27. Bài tập

## Bài 1

Cho:

```python
text = "Python 12345"
```

Dùng Regex lấy:

```text
12345
```

---

## Bài 2

Cho:

```python
text = "Chapter 123"
```

Chỉ chấp nhận chapter có **đúng 3 chữ số**.

```text
Chapter 123   → OK
Chapter 12    → FAIL
Chapter 1234  → FAIL
```

Chưa cần Anchor; hãy dùng `fullmatch()`.

---

## Bài 3

Match tất cả:

```text
Chapter 1
Chapter 12
Chapter 123
Chapter 1234
```

Dùng:

```regex
Chapter\s+\d+
```

---

## Bài 4

Website trả về:

```text
Chapter:123
Chapter: 123
Chapter:    123
```

Viết một Regex match cả 3.

---

## Bài 5

Cho:

```python
text = "aaaabbb"
```

Match:

```text
aaaa
```

bằng Character Class + Quantifier.

---

## Bài 6

Cho:

```python
text = "<title>Hello Python</title>"
```

Viết Regex lấy toàn bộ:

```text
<title>Hello Python</title>
```

sau đó sửa Regex để chỉ lấy:

```text
<title>
```

Gợi ý:

```regex
<title>.*?</title>
```

và:

```regex
<.*?>
```

---

# Challenge — Parser truyện

Cho dữ liệu:

```python
text = """
Story: Đấu Phá Thương Khung
Chapter 001: Vẫn là Tiêu Viêm
Chapter 002: Ba năm
Chapter 003: Vân Lam Tông
"""
```

Hãy viết chương trình sử dụng `re.search()` để lấy **chapter đầu tiên**:

```text
Chapter 001
```

và số:

```text
001
```

Gợi ý pattern:

```regex
Chapter\s+\d+
```

Sau đó thử sửa thành:

```regex
Chapter\s*:\s*\d+
```

để xử lý format khác.

**Buổi 4** chúng ta sẽ học **Anchor + Boundary**:

```regex
^
$
\A
\Z
\b
\B
```

và lúc đó bạn sẽ hiểu rất rõ tại sao:

```regex
Chapter\s+\d{3}
```

có thể match nhầm `Chapter 123` bên trong `Chapter 1234`, và cách viết Regex chuẩn để **validate toàn bộ chuỗi**.
