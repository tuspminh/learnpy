# Buổi 11 — Whitespace & Newline Deep Dive

Đây là một trong những buổi **quan trọng nhất của `html2text`**.

Khi chuyển:

```text
HTML → Markdown
```

thì vấn đề không chỉ là:

```text
<p>Hello</p>
```

→

```markdown
Hello
```

Mà là phải hiểu:

```text
space
tab
newline
blank line
paragraph
<br>
<div>
<p>
<pre>
```

Nếu xử lý sai, output có thể bị:

```text
Đây là đoạn 1.Đây là đoạn 2.
```

hoặc:

```text
Đây là đoạn 1.


Đây là đoạn 2.
```

Đặc biệt với hệ thống **crawler → Markdown → TTS**, whitespace ảnh hưởng trực tiếp đến chất lượng văn bản.

---

# 1. HTML whitespace khác Markdown whitespace

Ví dụ HTML:

```html
<p>Hello     World</p>
```

Browser thường hiển thị:

```text
Hello World
```

Nhiều space liên tiếp được collapse.

Trong khi Markdown:

```markdown
Hello     World
```

lại giữ nhiều space ở dạng source.

Vì vậy:

```text
HTML whitespace
       ↓
browser rendering rules
```

khác:

```text
Markdown whitespace
       ↓
Markdown parser rules
```

`html2text` phải chuyển đổi giữa hai thế giới này.

---

# 2. HTML có rất nhiều whitespace "vô nghĩa"

Ví dụ:

```html
<p>
    Hello
    World
</p>
```

Nếu nhìn source code, bạn thấy:

```text
newline
spaces
Hello
spaces
World
newline
```

Nhưng nội dung semantic thường chỉ là:

```text
Hello World
```

Đây là lý do không thể đơn giản:

```python
html.replace("\n", " ")
```

---

# 3. `body_width`

Bạn đã học `body_width` ở Buổi 7.

Ví dụ:

```python
converter.body_width = 80
```

`html2text` có thể wrap Markdown:

```markdown
Đây là một đoạn văn rất dài và
được chia thành nhiều dòng theo
chiều rộng được cấu hình.
```

Trong khi:

```python
converter.body_width = 0
```

thường được dùng để:

```text
không wrap dòng theo width
```

Đối với crawler, thường rất hữu ích:

```python
converter.body_width = 0
```

---

# 4. Vì sao crawler thường dùng `body_width = 0`?

Giả sử:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
Database
 ↓
TTS
```

Nếu:

```python
body_width = 80
```

một câu có thể bị:

```text
Python là ngôn ngữ lập trình phổ
biến được sử dụng trong rất nhiều
ứng dụng.
```

TTS vẫn có thể đọc được, nhưng source Markdown bị thêm newline không cần thiết.

Tốt hơn:

```python
converter.body_width = 0
```

để giữ paragraph:

```text
Python là ngôn ngữ lập trình phổ biến được sử dụng trong rất nhiều ứng dụng.
```

---

# 5. `<p>` tạo paragraph

HTML:

```html
<p>Đoạn thứ nhất.</p>
<p>Đoạn thứ hai.</p>
```

Markdown nên là:

```markdown
Đoạn thứ nhất.

Đoạn thứ hai.
```

Chú ý:

```text
paragraph
   ↓
blank line
   ↓
paragraph
```

Không chỉ là một newline.

---

# 6. Một newline và blank line

Có sự khác biệt:

### Một newline

```text
A
B
```

### Blank line

```text
A

B
```

Source representation:

```python
"A\nB"
```

vs:

```python
"A\n\nB"
```

Trong Markdown, `\n\n` thường biểu thị ranh giới paragraph.

---

# 7. `<br>`

HTML:

```html
<p>
Hello<br>
World
</p>
```

Thông thường output Markdown:

```markdown
Hello  
World
```

hoặc một representation tương đương tùy configuration/version.

Điểm quan trọng:

```text
<br>
 ↓
line break
```

không phải:

```text
paragraph break
```

---

# 8. `<br>` vs `<p>`

So sánh:

### `<br>`

```html
Hello<br>World
```

semantic:

```text
Hello
World
```

cùng paragraph.

### `<p>`

```html
<p>Hello</p>
<p>World</p>
```

semantic:

```text
paragraph 1

paragraph 2
```

Mental model:

```text
<br>
 ↓
line break

<p>
 ↓
paragraph boundary
```

---

# 9. `<div>` là case thú vị

HTML:

```html
<div>Hello</div>
<div>World</div>
```

thường được xử lý như block-level content.

Output có thể tương tự:

```markdown
Hello

World
```

Nhưng:

```html
<div>
    Hello
    <span>World</span>
</div>
```

thì `<span>` lại là inline element.

---

# 10. Block vs inline

Đây là concept quan trọng.

### Block

Ví dụ:

```text
<p>
<div>
<section>
<article>
<h1>
<ul>
<ol>
<li>
```

### Inline

Ví dụ:

```text
<span>
<a>
<strong>
<em>
<code>
```

Mental model:

```text
Block
  ↓
có khả năng tạo structural newline


Inline
  ↓
thường nằm cùng dòng
```

---

# 11. Ví dụ

HTML:

```html
<p>
Hello
<strong>Python</strong>
World
</p>
```

Mong muốn:

```markdown
Hello **Python** World
```

Không phải:

```markdown
Hello

**Python**

World
```

Vì:

```text
<strong>
```

là inline.

---

# 12. Whitespace quanh inline element

HTML:

```html
<p>
Hello
<strong>Python</strong>
World
</p>
```

Browser semantic:

```text
Hello Python World
```

Nhưng nếu:

```html
<p>
Hello<strong>Python</strong>World
</p>
```

thì semantic là:

```text
HelloPythonWorld
```

Do đó whitespace trong HTML source không phải lúc nào cũng là whitespace semantic.

---

# 13. Đây là lý do không được strip từng node tùy tiện

Ví dụ bạn tự viết:

```python
text = element.text(strip=True)
```

cho từng node.

Có thể biến:

```html
Hello <strong>Python</strong> World
```

thành:

```text
Hello
Python
World
```

và sau đó:

```text
HelloPythonWorld
```

hoặc spacing sai.

Khi xử lý DOM:

> Phải hiểu context của whitespace.

---

# 14. `html2text` có `single_line_break`

Một option đáng chú ý:

```python
converter.single_line_break = True
```

Nó liên quan đến cách converter xử lý line break trong output.

Bạn nên thử cùng một HTML với:

```python
converter.single_line_break = False
```

và:

```python
converter.single_line_break = True
```

để thấy sự khác biệt.

---

# 15. Test `single_line_break`

```python
import html2text

html = """
<p>Paragraph one.</p>
<p>Paragraph two.</p>
"""

converter = html2text.HTML2Text()

converter.single_line_break = False

print(repr(converter.handle(html)))
```

Sau đó:

```python
converter.single_line_break = True

print(repr(converter.handle(html)))
```

Điều quan trọng ở đây không phải chỉ nhớ output mà là:

> hiểu option đang thay đổi quy tắc newline nào.

---

# 16. `\n` trong Python

Khi debug whitespace, luôn dùng:

```python
repr(result)
```

thay vì:

```python
print(result)
```

Ví dụ:

```python
result = "Hello\n\nWorld"

print(result)
```

hiển thị:

```text
Hello

World
```

Nhưng:

```python
print(repr(result))
```

cho:

```text
'Hello\n\nWorld'
```

Rõ ràng hơn rất nhiều.

---

# 17. Đây là kỹ thuật debug quan trọng

Khi xử lý crawler:

```python
print(repr(markdown))
```

Bạn sẽ nhìn thấy:

```text
\n
\t
\xa0
```

Ví dụ:

```text
'Hello\n\nWorld\n'
```

Bạn biết ngay:

```text
Hello
blank line
World
newline cuối
```

---

# 18. `strip()`

Python:

```python
text.strip()
```

loại bỏ whitespace ở **hai đầu**.

Ví dụ:

```python
text = "\n\n Hello World \n\n"

print(repr(text.strip()))
```

→

```text
'Hello World'
```

Rất hữu ích.

---

# 19. Nhưng `strip()` không nên dùng cho từng dòng

Ví dụ:

```python
lines = [
    "  Hello",
    "    World",
]
```

Nếu:

```python
[line.strip() for line in lines]
```

sẽ mất indentation.

Điều này đặc biệt nguy hiểm với:

```text
code block
```

---

# 20. `pre` và whitespace

HTML:

```html
<pre>
    def hello():
        print("Hello")
</pre>
```

Whitespace ở đây có ý nghĩa.

Output Markdown:

````markdown
```
    def hello():
        print("Hello")
```
````

Bạn **không được** áp dụng:

```python
" ".join(text.split())
```

cho code.

Nếu làm vậy:

```text
    def hello():
        print("Hello")
```

có thể bị biến thành:

```text
def hello(): print("Hello")
```

Code bị phá.

---

# 21. Đây là nguyên tắc cực kỳ quan trọng

Không phải mọi text node đều có cùng whitespace semantics.

```text
Normal text
    ↓
whitespace có thể collapse


<pre>
    ↓
whitespace có ý nghĩa


<code>
    ↓
cần context


Markdown code block
    ↓
indentation rất quan trọng
```

---

# 22. `<pre>` và TTS

Nếu bạn đang làm TTS:

```text
code block
```

thường không cần đọc indentation.

Bạn có thể có pipeline riêng:

```text
Markdown
 ↓
AST / Markdown parser
 ↓
code block
 ↓
skip hoặc xử lý riêng
```

Đừng phá whitespace của code ngay từ HTML stage.

---

# 23. Multiple newlines

Crawler có thể nhận:

```text
Hello



World
```

tức:

```python
"Hello\n\n\n\nWorld"
```

Bạn có thể muốn normalize thành:

```text
Hello

World
```

Một cách:

```python
import re

text = re.sub(r"\n{3,}", "\n\n", text)
```

---

# 24. Nhưng cẩn thận với Markdown

Regex:

```python
re.sub(r"\n{3,}", "\n\n", markdown)
```

thường ổn cho plain prose, nhưng có thể ảnh hưởng những cấu trúc Markdown đặc biệt.

Đặc biệt khi document chứa:

* code fences
* tables
* lists
* blockquotes
* raw HTML

Do đó normalization nên có context.

---

# 25. Không dùng regex để "làm sạch tất cả"

Anti-pattern:

```python
markdown = re.sub(r"\s+", " ", markdown)
```

Đây là một trong những cách nhanh nhất để phá Markdown.

Ví dụ:

```markdown
# Title

Paragraph one.

Paragraph two.
```

sẽ thành:

```text
# Title Paragraph one. Paragraph two.
```

Mất cấu trúc document.

---

# 26. Whitespace normalization đúng cách

Nếu mục tiêu là **plain text cho TTS**, có thể:

```python
def normalize_plain_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
```

Nhưng nếu mục tiêu là **Markdown**, phải nhẹ tay hơn.

---

# 27. Plain text và Markdown là hai pipeline khác nhau

### Markdown

```text
HTML
 ↓
html2text
 ↓
Markdown normalization
```

### TTS

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
Markdown → plain text
 ↓
Text normalization
 ↓
TTS
```

Không nên dùng cùng một hàm normalization cho cả hai.

---

# 28. `body_width = 0` + TTS

Đối với crawler TTS:

```python
converter.body_width = 0
```

Sau đó:

```text
Markdown
 ↓
extract plain text
 ↓
normalize whitespace
 ↓
sentence splitting
 ↓
TTS
```

Đây là pipeline sạch hơn.

---

# 29. Heading

HTML:

```html
<h1>Chapter 1</h1>
<p>Hello world.</p>
```

Markdown:

```markdown
# Chapter 1

Hello world.
```

Heading tạo structural boundary.

Do đó:

```text
<h1>
 ↓
heading + newline structure
```

không nên bị collapse thành:

```text
# Chapter 1 Hello world.
```

---

# 30. Lists

HTML:

```html
<ul>
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
```

Markdown:

```markdown
- Python
- Rust
- Go
```

Ở đây newline có semantic.

Nếu:

```python
re.sub(r"\s+", " ", markdown)
```

thì:

```markdown
- Python - Rust - Go
```

Bạn đã phá list.

---

# 31. Nested list

HTML:

```html
<ul>
    <li>
        Python

        <ul>
            <li>FastAPI</li>
            <li>PySide6</li>
        </ul>
    </li>
</ul>
```

Markdown cần indentation:

```markdown
- Python
    - FastAPI
    - PySide6
```

Whitespace ở đây có **structural meaning**.

---

# 32. Blockquote

HTML:

```html
<blockquote>
    Hello
    World
</blockquote>
```

Markdown:

```markdown
> Hello
> World
```

newline lại có semantic.

Đây là lý do:

```text
whitespace normalization
```

không thể chỉ đơn giản là:

```text
remove spaces
```

---

# 33. Table

Markdown table:

```markdown
| Name | Age |
|---|---:|
| Minh | 30 |
```

Newline là bắt buộc để phân biệt rows.

Một normalization quá mạnh có thể biến:

```text
row 1
row 2
```

thành một dòng.

---

# 34. `html2text` và `pretty`

Bạn sẽ gặp HTML source:

```html
<p>Hello</p>
```

và:

```html
<p>
    Hello
</p>
```

Về semantic gần như giống nhau.

`html2text` cố gắng tạo Markdown dựa trên HTML structure chứ không đơn giản copy whitespace source.

Đây là một distinction rất quan trọng:

```text
HTML source whitespace
        ≠
HTML semantic structure
```

---

# 35. Một ví dụ tổng hợp

HTML:

```html
<article>

<h1>Python</h1>

<p>
Python là ngôn ngữ
<strong>lập trình</strong>
phổ biến.
</p>

<p>
Nó được dùng cho:
</p>

<ul>
    <li>Web</li>
    <li>Data</li>
    <li>AI</li>
</ul>

<p>
Dòng đầu<br>
Dòng thứ hai
</p>

<pre><code>
def hello():
    print("Hello")
</code></pre>

</article>
```

Hãy quan sát:

```text
<h1>      → heading
<p>       → paragraph
<strong>  → inline
<ul>      → list
<br>      → line break
<pre>     → preserve whitespace
```

---

# 36. Đừng nhìn HTML bằng mắt

Khi debug:

```python
result = converter.handle(html)

print(result)
```

chưa đủ.

Hãy:

```python
print(repr(result))
```

và nếu cần:

```python
for i, line in enumerate(result.splitlines()):
    print(i, repr(line))
```

Ví dụ:

```text
0 '# Python'
1 ''
2 'Python là ngôn ngữ **lập trình** phổ biến.'
3 ''
4 '- Web'
5 '- Data'
6 '- AI'
```

Cách debug này cực kỳ hữu ích.

---

# 37. Viết helper debug

Bạn có thể tạo:

```python
def debug_lines(text: str) -> None:
    for index, line in enumerate(text.splitlines()):
        print(f"{index:03}: {line!r}")
```

Dùng:

```python
debug_lines(markdown)
```

Kết quả:

```text
000: '# Python'
001: ''
002: 'Python là ngôn ngữ **lập trình** phổ biến.'
003: ''
004: '- Web'
005: '- Data'
006: '- AI'
```

---

# 38. Đây là công cụ nên giữ lại

Trong project crawler của bạn, tôi khuyên có:

```text
utils/
    text_debug.py
    text_normalizer.py
```

Ví dụ:

```text
text_debug.py
    ↓
debug_lines()
show_repr()
```

và:

```text
text_normalizer.py
    ↓
normalize_unicode()
normalize_plain_text()
```

Tách riêng sẽ dễ test.

---

# 39. `normalize_plain_text()`

Một implementation tốt hơn:

```python
import re
import unicodedata


def normalize_plain_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)

    text = text.replace("\xa0", " ")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n[ \t]+", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
```

Lưu ý:

> Hàm này dành cho **plain text**, không phải raw Markdown.

---

# 40. Vì sao tách Markdown và plain text?

Một article có thể cần hai representation:

```text
                    Article
                       │
                       ▼
                    Markdown
                   /        \
                  /          \
             Reader           TTS
                │              │
             render       plain text
                              │
                         normalization
                              │
                             TTS
```

Reader cần structure.

TTS cần text sạch.

Hai mục tiêu khác nhau.

---

# 41. Một architecture rất tốt

```text
HTML
 │
 ▼
Cleaner
 │
 ▼
html2text
 │
 ▼
Markdown
 │
 ├───────────────┐
 ▼               ▼
Reader       MarkdownParser
                 │
                 ▼
             Plain Text
                 │
                 ▼
             Normalizer
                 │
                 ▼
                TTS
```

Đây là architecture bạn có thể dùng lâu dài.

---

# 42. `body_width` nên cấu hình thế nào?

### Website → Markdown archive

```python
converter.body_width = 0
```

thường phù hợp.

### Output cần readability trực tiếp

```python
converter.body_width = 80
```

hoặc width tùy yêu cầu.

### TTS

Thường:

```python
converter.body_width = 0
```

rồi normalize plain text sau.

---

# 43. `single_line_break`

Bạn nên test riêng option này:

```python
converter.single_line_break = True
```

và:

```python
converter.single_line_break = False
```

với:

```html
<p>One</p>
<p>Two</p>

<div>Three</div>
<div>Four</div>

<p>
Five<br>
Six
</p>
```

Sau đó dùng:

```python
debug_lines(result)
```

để nghiên cứu chính xác output của phiên bản `html2text` bạn đang dùng.

Đây là cách học tốt hơn việc chỉ học thuộc output.

---

# 44. Bài tập 1 — Paragraph

Input:

```html
<p>Hello</p>
<p>World</p>
```

Hãy trả lời:

```text
Có bao nhiêu newline?
Có bao nhiêu paragraph?
```

---

# 45. Bài tập 2 — `<br>`

Input:

```html
<p>
Hello<br>
World
</p>
```

Hãy so sánh với:

```html
<p>Hello</p>
<p>World</p>
```

Bạn phải phân biệt:

```text
line break
```

và:

```text
paragraph break
```

---

# 46. Bài tập 3 — Inline

Xử lý:

```html
<p>
Python
<strong>rất</strong>
tuyệt
</p>
```

Mục tiêu:

```markdown
Python **rất** tuyệt
```

Không được biến thành ba dòng.

---

# 47. Bài tập 4 — List

Input:

```html
<ul>
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
```

Sau `html2text`, dùng:

```python
repr(result)
```

để nghiên cứu newline giữa các item.

---

# 48. Bài tập 5 — Code

Input:

```html
<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Kiểm tra:

```python
print(repr(result))
```

Mục tiêu là xác định:

* newline đầu
* indentation
* newline cuối
* code fence

---

# 49. Bài tập 6 — Multiple newline

Tạo:

```python
text = "A\n\n\n\n\nB"
```

Viết:

```python
def collapse_blank_lines(text: str) -> str:
    ...
```

để:

```text
A



B
```

thành:

```text
A

B
```

---

# 50. Bài tập 7 — TTS normalization

Viết:

```python
def normalize_for_tts(text: str) -> str:
    ...
```

Yêu cầu:

```text
NFC
NBSP → space
collapse horizontal whitespace
max 1 blank line
preserve paragraph boundaries
```

Input:

```text
Xin\xa0chào     bạn.


Đây là đoạn thứ hai.
```

Output:

```text
Xin chào bạn.

Đây là đoạn thứ hai.
```

---

# 51. Bài tập 8 — Production HTML

Dùng HTML:

```html
<article>

<h1>Python</h1>

<p>
Python là <strong>ngôn ngữ</strong>
lập trình.
</p>

<p>
Các lĩnh vực:
</p>

<ul>
    <li>Web</li>
    <li>AI</li>
    <li>Automation</li>
</ul>

<p>
Dòng một<br>
Dòng hai<br>
Dòng ba
</p>

<pre><code>
def hello():
    print("Hello")
</code></pre>

</article>
```

Chạy:

```python
import html2text

converter = html2text.HTML2Text()

converter.body_width = 0

result = converter.handle(html)

print(result)
print("=" * 60)
print(repr(result))
```

Sau đó tự phân loại từng newline:

```text
heading boundary
paragraph boundary
list item boundary
line break
code block boundary
```

---

# 52. Bài tập nâng cao — viết test

Bạn có thể bắt đầu test:

```python
def test_paragraphs():
    html = """
    <p>Hello</p>
    <p>World</p>
    """

    converter = html2text.HTML2Text()
    result = converter.handle(html)

    assert "Hello" in result
    assert "World" in result
```

Sau đó nâng cấp test structural:

```python
assert "Hello\n\nWorld" in result
```

Nhưng lưu ý: **đừng viết test quá phụ thuộc vào whitespace nội bộ nếu behavior đó không phải contract bạn cần giữ.**

---

# 53. Nguyên tắc testing rất quan trọng

Nếu application của bạn yêu cầu:

```text
Mỗi paragraph cách nhau bằng một blank line
```

thì test:

```python
assert "A\n\nB" in result
```

hợp lý.

Nếu chỉ cần:

```text
A và B xuất hiện
```

thì không nên test:

```python
assert result == "A\n\nB\n"
```

quá cứng.

---

# 54. Mental model Buổi 11

Hãy nhớ sơ đồ này:

```text
                    HTML
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
       Inline       Block         Pre
          │           │            │
          ▼           ▼            ▼
       same line   structure    preserve
                      │
             ┌────────┼─────────┐
             │        │         │
             ▼        ▼         ▼
             p       div       br
             │        │         │
             ▼        ▼         ▼
         paragraph  block     line break
```

Sau đó:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
plain text extraction
 ↓
TTS normalization
```

---

# 55. Những điều cần nhớ nhất

### 1. `<p>` ≠ `<br>`

```text
<p> → paragraph
<br> → line break
```

### 2. Block ≠ inline

```text
<p>       → block
<div>     → block
<strong>  → inline
<span>    → inline
```

### 3. `<pre>` cần giữ whitespace

Không được:

```python
" ".join(text.split())
```

một cách mù quáng.

### 4. `body_width`

Crawler/Markdown archive thường nên cân nhắc:

```python
converter.body_width = 0
```

### 5. Debug bằng `repr()`

```python
print(repr(result))
```

### 6. Markdown và TTS cần normalization khác nhau

```text
Markdown → preserve structure
TTS      → normalize prose
```

### 7. Không dùng:

```python
re.sub(r"\s+", " ", markdown)
```

cho toàn bộ Markdown.

---

## Bài tập cuối buổi

Hãy tự xây pipeline:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
extract plain text
 ↓
normalize Unicode
 ↓
normalize whitespace
```

với HTML:

```html
<article>

<h1>Chương 1</h1>

<p>
Xin&nbsp;&nbsp;&nbsp;chào <strong>Việt Nam</strong>.
</p>

<p>
Đây là đoạn thứ hai.<br>
Đây là dòng thứ hai.
</p>

<ul>
    <li>Python</li>
    <li>PySide6</li>
    <li>HTML2Text</li>
</ul>

</article>
```

Mục tiêu cuối cùng:

```text
Chương 1

Xin chào Việt Nam.

Đây là đoạn thứ hai.
Đây là dòng thứ hai.

Python
PySide6
HTML2Text
```

**Buổi 12 — Escape Markdown** sẽ là buổi cuối của phần Configuration Deep Dive. Ta sẽ học một vấn đề rất quan trọng: tại sao text HTML như:

```text
2 * 3 = 6
C:\Python
[Python]
# Python
`code`
_hello_
```

có thể bị `html2text` hiểu nhầm là Markdown syntax, và cách kiểm soát **Markdown escaping** để crawler không làm thay đổi nội dung gốc.
