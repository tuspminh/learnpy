# Buổi 12 — Escape Markdown

Hôm nay chúng ta kết thúc **Phần II — Configuration Deep Dive**.

Chủ đề rất quan trọng:

```text
HTML
 ↓
html2text
 ↓
Markdown
```

Khi chuyển HTML → Markdown, một số ký tự vốn chỉ là **text bình thường** trong HTML lại có ý nghĩa đặc biệt trong Markdown.

Ví dụ:

```text
2 * 3 = 6
```

Trong HTML, `*` chỉ là ký tự.

Nhưng trong Markdown:

```markdown
*text*
```

lại có nghĩa là **italic**.

Vì vậy `html2text` phải quyết định:

> Ký tự này là nội dung hay là Markdown syntax?

---

# 1. Markdown có những ký tự đặc biệt nào?

Các ký tự thường cần quan tâm:

```text
*
_
`
[
]
(
)
#
>
-
+
.
!
|
\
```

Không phải ký tự nào cũng luôn cần escape.

Ví dụ:

```markdown
*hello*
```

có nghĩa:

```text
italic
```

Trong khi:

```markdown
\*hello\*
```

hiển thị:

```text
*hello*
```

---

# 2. Escape là gì?

Escape nghĩa là:

> Biến một ký tự Markdown đặc biệt thành literal text.

Ví dụ:

```markdown
*hello*
```

→ Markdown parser hiểu là italic.

Escape:

```markdown
\*hello\*
```

→ hiển thị:

```text
*hello*
```

Mental model:

```text
*
│
├── syntax
│
└── \* → literal character
```

---

# 3. Ví dụ đơn giản

Input HTML:

```html
<p>
2 * 3 = 6
</p>
```

Nếu converter output:

```markdown
2 * 3 = 6
```

Markdown parser có thể không coi đây là italic vì không có cặp `*` hợp lệ.

Nhưng:

```html
<p>
*hello*
</p>
```

có thể trở thành Markdown emphasis:

```markdown
*hello*
```

Khi render:

```text
hello
```

thay vì:

```text
*hello*
```

Nếu nội dung website thực sự muốn hiển thị dấu `*`, đây là một thay đổi semantic.

---

# 4. HTML và Markdown có hai grammar khác nhau

Đây là concept quan trọng nhất của buổi học.

HTML:

```html
<p>*hello*</p>
```

ý nghĩa:

```text
literal "*hello*"
```

Markdown:

```markdown
*hello*
```

ý nghĩa:

```text
emphasis
```

Do đó:

```text
HTML text
   ↓
Markdown text
```

không phải lúc nào cũng có thể copy nguyên xi.

---

# 5. `html2text` phải escape khi nào?

Converter cần phân biệt:

```text
HTML structure
```

và:

```text
HTML text
```

Ví dụ:

```html
<p>
This is <strong>important</strong>.
</p>
```

HTML structure:

```text
<strong>
```

phải trở thành Markdown:

```markdown
**important**
```

Nhưng:

```html
<p>
2 * 3 = 6
</p>
```

thì:

```text
*
```

là text.

---

# 6. Không phải cứ gặp `*` là escape

Đây là lỗi tư duy phổ biến.

Không nên làm:

```python
text = text.replace("*", r"\*")
```

cho toàn bộ output.

Vì nếu converter đã tạo:

```markdown
**important**
```

thì bạn biến thành:

```markdown
\*\*important\*\*
```

và Markdown không còn bold nữa.

Do đó:

> Escape phải diễn ra ở đúng context.

---

# 7. Context là thứ quan trọng nhất

Cùng một ký tự:

```text
*
```

có thể là:

### Text

```html
<p>2 * 3</p>
```

### Markdown syntax do converter tạo

```markdown
**important**
```

### Code

```html
<code>a * b</code>
```

### Raw HTML

```html
<div>*</div>
```

Mỗi context cần xử lý khác nhau.

---

# 8. Inline emphasis

HTML:

```html
<p>
Hello <strong>Python</strong>
</p>
```

`html2text` có thể tạo:

```markdown
Hello **Python**
```

Ở đây:

```text
**Python**
```

là Markdown syntax **do converter tạo ra**.

Không được escape nó sau cùng.

Sai:

```markdown
Hello \*\*Python\*\*
```

Kết quả sẽ hiển thị:

```text
Hello **Python**
```

thay vì:

```text
Hello Python
```

với bold.

---

# 9. `<em>`

HTML:

```html
<p>
This is <em>important</em>.
</p>
```

Markdown:

```markdown
This is *important*.
```

Ở đây `*` là syntax.

Không escape.

---

# 10. Text chứa dấu `*`

HTML:

```html
<p>
Price: 100 * 2
</p>
```

Markdown:

```markdown
Price: 100 * 2
```

Ở đây `*` là literal.

Không cần thiết phải biến thành:

```markdown
Price: 100 \* 2
```

nếu Markdown parser vẫn hiểu đúng.

---

# 11. Nhưng có trường hợp phải escape

Ví dụ text:

```html
<p>
*important*
</p>
```

Nếu output:

```markdown
*important*
```

thì Markdown hiểu là emphasis.

Nếu muốn giữ literal:

```markdown
\*important\*
```

Nhưng `html2text` có logic riêng để quyết định việc escape.

Đây là lý do bạn không nên tự viết một `replace()` đơn giản.

---

# 12. `escape_snob`

Trong `html2text`, bạn sẽ gặp option:

```python
converter.escape_snob
```

Đây là một configuration liên quan đến escaping.

Ví dụ:

```python
converter.escape_snob = True
```

Ý tưởng là yêu cầu converter **aggressive hơn trong việc escaping** một số ký tự Markdown.

Bạn nên xem đây là:

```text
normal mode
     vs
strict escaping mode
```

chứ không phải:

```text
escape EVERYTHING
```

---

# 13. Test `escape_snob`

Tạo:

```python
import html2text

html = """
<p>*hello*</p>
<p>_hello_</p>
<p>[Python]</p>
<p># Python</p>
<p>2 * 3 = 6</p>
"""

converter = html2text.HTML2Text()

converter.escape_snob = False

result1 = converter.handle(html)

print("FALSE")
print(result1)
print(repr(result1))
```

Sau đó:

```python
converter.escape_snob = True

result2 = converter.handle(html)

print("TRUE")
print(result2)
print(repr(result2))
```

Hãy quan sát sự khác biệt.

---

# 14. Đừng chỉ nhìn `print()`

Như Buổi 11:

```python
print(result)
```

cho bạn output trực quan.

Nhưng:

```python
print(repr(result))
```

cho bạn biết chính xác:

```text
\*
\_
\[
\]
\n
```

Đây là cách tốt để nghiên cứu escaping.

---

# 15. Backslash

Markdown dùng:

```text
\
```

để escape.

Ví dụ:

```markdown
\*
```

nghĩa là literal `*`.

Nhưng bản thân backslash cũng có ý nghĩa.

Ví dụ HTML:

```html
<p>
C:\Python\Scripts
</p>
```

Có thể cần chú ý khi output Markdown.

---

# 16. Windows path

Đây là case rất thực tế với Python:

```text
C:\Python\Scripts
```

Nếu text được đưa vào Markdown, bạn không muốn converter vô tình làm thay đổi path.

Ví dụ:

```text
C:\new\test
```

có thể chứa:

```text
\n
\t
```

nhưng trong Python source:

```python
"C:\new\test"
```

lại là escape sequence.

Vì vậy khi test phải dùng:

```python
r"C:\new\test"
```

hoặc:

```python
"C:\\new\\test"
```

---

# 17. Python escaping ≠ Markdown escaping

Đây là hai tầng hoàn toàn khác nhau.

### Python string

```python
"\n"
```

→ newline.

### Markdown

```markdown
\*
```

→ literal `*`.

Mental model:

```text
Python escaping
       ≠
Markdown escaping
       ≠
HTML entities
```

Ba hệ thống khác nhau.

---

# 18. HTML entity và Markdown escaping

Ví dụ:

```html
<p>
&amp; *hello*
</p>
```

Có hai vấn đề:

```text
&amp;
 ↓
&
```

và:

```text
*hello*
 ↓
Markdown emphasis?
```

Pipeline:

```text
HTML entity processing
          ↓
Unicode text
          ↓
Markdown escaping
          ↓
Markdown
```

Hai loại escaping không nên trộn lẫn.

---

# 19. `&ast;`

HTML cũng có entity cho một số ký tự.

Ví dụ conceptually:

```text
entity
 ↓
*
```

Sau đó Markdown layer lại phải quyết định:

```text
*
 ↓
literal hay syntax?
```

Do đó có thể có nhiều tầng:

```text
HTML entity
      ↓
Unicode character
      ↓
Markdown escaping
```

---

# 20. Square brackets

Markdown:

```markdown
[Python](https://python.org)
```

là link.

Nhưng HTML:

```html
<p>
Array [0] contains Python.
</p>
```

thì `[0]` chỉ là text.

Không muốn Markdown hiểu nhầm thành link/reference.

---

# 21. Link syntax

HTML:

```html
<a href="https://example.com">
Python
</a>
```

`html2text` chuyển thành:

```markdown
[Python](https://example.com)
```

Ở đây:

```text
[
]
(
)
```

là Markdown syntax do converter tạo ra.

Không được escape chúng sau cùng.

---

# 22. Literal Markdown-looking text

Website có thể viết:

```html
<p>
Use [Python] for scripting.
</p>
```

Output:

```markdown
Use [Python] for scripting.
```

Thông thường Markdown parser sẽ không coi đây là link nếu không có target/reference hợp lệ.

Nhưng nếu content có pattern đặc biệt:

```markdown
[Python][1]

[1]: https://python.org
```

thì lại có nghĩa khác.

Đây là lý do Markdown escaping khá phức tạp.

---

# 23. Heading `#`

HTML:

```html
<p>
# Python
</p>
```

Nội dung semantic:

```text
# Python
```

Nhưng Markdown:

```markdown
# Python
```

lại là heading.

Nếu muốn literal:

```markdown
\# Python
```

hoặc tùy context có thể dùng:

```markdown
# Python
```

khi `#` không ở vị trí khiến parser nhận diện heading.

---

# 24. Heading thật

HTML:

```html
<h1>Python</h1>
```

phải trở thành:

```markdown
# Python
```

Đây là **syntax có chủ đích**.

Trong khi:

```html
<p># Python</p>
```

lại là text.

Hai input:

```text
<h1>Python</h1>
```

và:

```text
<p># Python</p>
```

không thể có cùng output Markdown nếu muốn giữ semantic.

---

# 25. List marker

HTML:

```html
<ul>
<li>Python</li>
<li>Rust</li>
</ul>
```

Markdown:

```markdown
- Python
- Rust
```

Nhưng:

```html
<p>- Python</p>
```

lại là literal:

```text
- Python
```

Nếu nằm ở đầu dòng, Markdown có thể hiểu nó là list.

Một lần nữa:

```text
HTML structure
     ↓
Markdown syntax

HTML text
     ↓
Markdown escaped text
```

---

# 26. `>` và blockquote

HTML:

```html
<blockquote>
Hello
</blockquote>
```

Markdown:

```markdown
> Hello
```

Nhưng:

```html
<p>> Hello</p>
```

là literal text.

Nếu muốn bảo vệ:

```markdown
\> Hello
```

---

# 27. Code là context đặc biệt

HTML:

```html
<code>
a * b
</code>
```

Markdown:

```markdown
`a * b`
```

Trong code span:

```text
*
_
[
]
#
```

không còn hoạt động giống Markdown prose.

Đây là một nguyên tắc quan trọng:

> Không escape Markdown syntax trong code theo cách escape prose.

---

# 28. Code block

HTML:

```html
<pre><code>
def hello():
    print("*")
</code></pre>
```

Markdown:

````markdown
```
def hello():
    print("*")
```
````

Trong code block:

```text
*
```

là literal.

Không cần:

```text
\*
```

---

# 29. Vì sao không escape toàn bộ output?

Giả sử output:

```markdown
# Python

Hello **world**.

- Fast
- Simple

[Documentation](https://example.com)
```

Nếu chạy:

```python
escape_markdown(result)
```

có thể biến thành:

```markdown
\# Python

Hello \*\*world\*\*.

\- Fast
\- Simple

\[Documentation\]\(https://example.com\)
```

Toàn bộ Markdown bị biến thành text.

Đây là **anti-pattern cực kỳ nghiêm trọng**.

---

# 30. Escape phải xảy ra trước khi tạo Markdown syntax

Một pipeline đúng về mặt concept:

```text
HTML node
   │
   ├── text node
   │      ↓
   │   escape nếu cần
   │
   ├── <strong>
   │      ↓
   │   tạo **
   │
   ├── <em>
   │      ↓
   │   tạo *
   │
   ├── <a>
   │      ↓
   │   tạo [...]
   │
   └── <h1>
          ↓
       tạo #
```

Không phải:

```text
HTML
 ↓
tạo Markdown
 ↓
escape toàn bộ
```

---

# 31. Đây chính là lý do `html2text` không phải `replace()`

Một converter đúng nghĩa phải có:

```text
Parser
   ↓
DOM / token
   ↓
semantic interpretation
   ↓
Markdown renderer
```

Mental model:

```text
HTML AST
   ↓
Markdown AST-like representation
   ↓
Markdown serializer
```

`html2text` không hoàn toàn phải là AST implementation theo nghĩa này, nhưng tư duy architecture nên như vậy.

---

# 32. Một ví dụ phức tạp

HTML:

```html
<article>

<h1>Python *Deep Dive*</h1>

<p>
Python <strong>rất mạnh</strong>.
</p>

<p>
Công thức: a * b = c
</p>

<p>
Pattern: [Python]
</p>

<pre><code>
result = a * b
</code></pre>

</article>
```

Có nhiều context:

```text
<h1>
    ↓
Markdown heading

<strong>
    ↓
Markdown bold

text "*"
    ↓
literal

[Python]
    ↓
literal bracket

<pre><code>
    ↓
code
```

---

# 33. Cấu hình cơ bản

Một converter cho crawler có thể bắt đầu:

```python
import html2text


def create_converter() -> html2text.HTML2Text:
    converter = html2text.HTML2Text()

    converter.body_width = 0
    converter.ignore_images = False
    converter.ignore_links = False

    return converter
```

Sau đó mới tinh chỉnh:

```python
converter.escape_snob = ...
```

dựa trên yêu cầu output.

---

# 34. Đừng bật option chỉ vì "nghe có vẻ an toàn"

Ví dụ:

```python
converter.escape_snob = True
```

không có nghĩa:

```text
"Markdown luôn tốt hơn"
```

Mà phải hỏi:

```text
Application cần gì?
```

### Nếu cần Markdown đẹp:

```text
preserve Markdown semantics
```

### Nếu cần literal content:

```text
escape aggressively
```

### Nếu cần TTS:

```text
Markdown cuối cùng có thể không còn là representation quan trọng nhất
```

---

# 35. Với crawler truyện

Trong project crawler truyện của bạn:

```text
Website
 ↓
Cleaner
 ↓
html2text
 ↓
Markdown
 ↓
SQLite
```

Bạn thường muốn giữ:

```text
heading
paragraph
bold
italic
links
code
lists
```

nếu reader cần render Markdown.

Do đó không nên aggressive escaping toàn bộ.

---

# 36. Với TTS

Nếu mục tiêu cuối cùng là:

```text
Markdown
 ↓
TTS
```

thì bạn không cần quá ám ảnh về Markdown escaping ở tầng TTS.

Bạn nên:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
Markdown parser / cleaner
 ↓
plain text
 ↓
TTS
```

Tức là TTS nhận:

```text
plain text
```

chứ không đọc:

```text
**Python**
[link](...)
```

---

# 37. Đừng dùng regex để remove Markdown syntax

Anti-pattern:

```python
import re

text = re.sub(r"[*_`\[\]]", "", markdown)
```

Vì:

```markdown
**Python**
```

→ Python

có vẻ đúng.

Nhưng:

```markdown
a * b
```

→

```text
a  b
```

lại mất `*`.

Hoặc:

```markdown
[Python](https://python.org)
```

→ có thể xử lý sai.

Markdown cần parser nếu muốn xử lý chính xác.

---

# 38. Separation of concerns

Architecture tốt:

```text
                HTML
                  │
                  ▼
             HTML Cleaner
                  │
                  ▼
              html2text
                  │
                  ▼
              Markdown
             /        \
            /          \
           ▼            ▼
        Reader       Markdown Parser
                         │
                         ▼
                     Plain Text
                         │
                         ▼
                        TTS
```

Mỗi layer có nhiệm vụ riêng.

---

# 39. Test suite nên có

Khi xây crawler, hãy test các nhóm:

### Basic

```text
hello
```

### Emphasis

```text
*italic*
**bold**
```

### Literal characters

```text
2 * 3
[Python]
# Python
> Hello
```

### Links

```text
[Python](...)
```

### Code

```text
a * b
```

### Lists

```text
- Python
- Rust
```

### Unicode

```text
Tiếng Việt 🇻🇳
```

---

# 40. Test với `html2text`

Ví dụ:

```python
import html2text


def convert(html: str) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(html)
```

Test:

```python
html = """
<h1>Python</h1>

<p>
Python <strong>rất mạnh</strong>.
</p>

<p>
2 * 3 = 6
</p>

<p>
[Python]
</p>

<pre><code>
a * b
</code></pre>
"""

print(convert(html))
```

Sau đó kiểm tra từng section.

---

# 41. Test semantic thay vì test string mù quáng

Không chỉ:

```python
assert result == expected
```

Bạn nên suy nghĩ:

```text
Heading còn là heading?
Bold còn là bold?
List còn là list?
Code còn là code?
Literal * còn là literal?
```

Đây là **semantic testing**.

---

# 42. Một nguyên tắc rất quan trọng

Khi HTML → Markdown:

> Không phải mục tiêu là giữ nguyên source HTML.

Mục tiêu là:

> Giữ nguyên **ý nghĩa/nội dung** trong representation Markdown.

Ví dụ:

```html
<strong>Python</strong>
```

không cần giữ:

```text
<strong>Python</strong>
```

mà chuyển thành:

```markdown
**Python**
```

Đó là transformation hợp lệ.

---

# 43. Nhưng literal content phải được bảo vệ

Ví dụ:

```html
<p>
*Python*
</p>
```

Nếu website muốn người dùng nhìn thấy:

```text
*Python*
```

thì Markdown representation phải đảm bảo render ra đúng:

```text
*Python*
```

có thể cần:

```markdown
\*Python\*
```

Đây là nhiệm vụ của escaping.

---

# 44. `escape_snob` — cách học tốt nhất

Đừng cố học thuộc implementation ngay.

Hãy tạo matrix:

| Input      | `escape_snob=False` | `escape_snob=True` |
| ---------- | ------------------- | ------------------ |
| `*hello*`  | test                | test               |
| `_hello_`  | test                | test               |
| `[Python]` | test                | test               |
| `# Python` | test                | test               |
| `> Hello`  | test                | test               |
| `- Python` | test                | test               |
| `2 * 3`    | test                | test               |

Sau đó chạy trên **version `html2text` bạn đang cài**.

Đây là cách tốt nhất để hiểu behavior thay vì dựa vào trí nhớ.

---

# 45. Bài tập 1 — Literal Markdown

Chuyển HTML:

```html
<p>*hello*</p>
<p>_hello_</p>
<p>[Python]</p>
<p># Python</p>
<p>> Hello</p>
```

và quan sát:

```python
print(repr(result))
```

---

# 46. Bài tập 2 — Semantic Markdown

HTML:

```html
<h1>Python</h1>

<p>
This is <strong>important</strong>.
</p>

<p>
This is <em>interesting</em>.
</p>
```

Xác định đâu là:

```text
literal text
```

và đâu là:

```text
Markdown syntax generated by converter
```

---

# 47. Bài tập 3 — Code

HTML:

```html
<pre><code>
a * b
x _ y
[0]
# comment
</code></pre>
```

Kiểm tra xem các ký tự:

```text
*
_
[
]
#
```

có bị escape không.

Sau đó giải thích:

> Vì sao code không nên xử lý giống prose?

---

# 48. Bài tập 4 — `escape_snob`

Chạy:

```python
for value in [False, True]:
    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.escape_snob = value

    result = converter.handle("""
    <p>*hello*</p>
    <p>_hello_</p>
    <p>[Python]</p>
    <p># Python</p>
    """)

    print("=" * 60)
    print("escape_snob =", value)
    print(repr(result))
```

Ghi lại sự khác biệt.

---

# 49. Bài tập 5 — Windows path

Test:

```html
<p>
C:\Python\Scripts
</p>
```

và:

```python
print(repr(result))
```

Đảm bảo bạn phân biệt:

```text
HTML content
```

với:

```text
Python source escaping
```

---

# 50. Bài tập 6 — Toàn bộ pipeline

Tạo HTML:

```html
<article>

<h1>Python *Deep Dive*</h1>

<p>
Xin&nbsp;&nbsp;chào <strong>Việt Nam</strong>.
</p>

<p>
2 * 3 = 6
</p>

<p>
[Python]
</p>

<p>
# Python
</p>

<ul>
    <li>Python</li>
    <li>Rust</li>
</ul>

<pre><code>
result = a * b
print("[Python]")
</code></pre>

</article>
```

Pipeline:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
repr()
```

Sau đó phân loại từng ký tự:

```text
*
_
[
]
#
-
\
```

thành:

```text
literal
```

hoặc:

```text
Markdown syntax
```

---

# 51. Bài tập 7 — Thiết kế converter

Viết:

```python
import html2text


def create_converter() -> html2text.HTML2Text:
    ...
```

Yêu cầu:

```text
body_width = 0
```

và lựa chọn hợp lý cho:

```text
ignore_links
ignore_images
escape_snob
single_line_break
```

Sau đó giải thích **tại sao bạn chọn mỗi option**.

Đây mới là mục tiêu của phần Configuration Deep Dive:

> Không học thuộc option, mà biết option nào phục vụ requirement nào.

---

# 52. Tổng kết Phần II

Bạn vừa đi qua:

```text
Buổi 6
Các option quan trọng

Buổi 7
body_width

Buổi 8
Link configuration

Buổi 9
Image configuration

Buổi 10
Unicode & HTML entities

Buổi 11
Whitespace & newline

Buổi 12
Escape Markdown
```

Bây giờ bạn đã có mental model khá đầy đủ:

```text
                     HTML
                       │
                       ▼
              ┌─────────────────┐
              │    html2text    │
              │                 │
              │ links           │
              │ images          │
              │ entities        │
              │ whitespace      │
              │ escaping        │
              └────────┬────────┘
                       │
                       ▼
                    Markdown
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
            Reader             TTS
```

---

# 53. 7 nguyên tắc cần nhớ

### ① HTML entity ≠ Markdown escape

```text
&amp; → &
\*   → *
```

Hai tầng khác nhau.

### ② `str` Unicode ≠ bytes

```text
str
 ↓ encode
bytes
```

### ③ `<p>` ≠ `<br>`

```text
<p> → paragraph
<br> → line break
```

### ④ `<pre>` phải bảo vệ whitespace

```text
code ≠ prose
```

### ⑤ Không normalize Markdown bằng:

```python
re.sub(r"\s+", " ", markdown)
```

### ⑥ Không escape toàn bộ Markdown sau khi converter đã tạo nó

```text
Markdown syntax
     ≠
literal text
```

### ⑦ Luôn nghĩ theo **context**

```text
prose
code
heading
list
link
blockquote
```

mỗi context có rules khác nhau.

---

# 54. Kiến thức quan trọng nhất của 12 buổi

Nếu chỉ giữ lại một mental model, hãy giữ:

```text
                 RAW HTML
                    │
                    ▼
              HTML structure
                    │
                    ▼
              semantic nodes
                    │
                    ▼
              html2text
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
      heading     prose       code
         │          │          │
         ▼          ▼          ▼
         #       escape?     preserve
                    │
                    ▼
                 Markdown
                    │
                    ▼
              Application
```

`html2text` không đơn thuần là:

```python
HTML.replace(...)
```

Mà là một **HTML → Markdown conversion layer**.

---

## Phần III — Advanced Conversion

Sau Configuration Deep Dive, roadmap nên đi tiếp theo hướng:

```text
Phần III — Advanced Conversion
```

với các chủ đề như:

1. **Buổi 13 — HTML → Markdown Architecture**
2. **Buổi 14 — `HTML2Text` internals**
3. **Buổi 15 — `handle()` và conversion pipeline**
4. **Buổi 16 — Customizing `HTML2Text`**
5. **Buổi 17 — Override xử lý HTML tag**
6. **Buổi 18 — Custom link/image handling**
7. **Buổi 19 — Custom whitespace handling**
8. **Buổi 20 — Custom Markdown renderer**
9. **Buổi 21 — HTML cleaning + html2text**
10. **Buổi 22 — Selectolax + html2text**
11. **Buổi 23 — Xây `HTMLToMarkdownConverter`**
12. **Buổi 24 — Testing converter**

Phần này sẽ bắt đầu chuyển từ **“biết dùng `html2text`”** sang **“có khả năng mở rộng `html2text` cho crawler thực tế”**.
