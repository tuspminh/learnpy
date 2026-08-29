# Buổi 5 — Code Block trong `html2text`

Đây là buổi rất quan trọng nếu mục tiêu của bạn là xây **HTML → Markdown converter** tốt.

Đặc biệt với tài liệu lập trình, blog kỹ thuật, GitHub-like pages, documentation..., code thường là phần **không được phép làm hỏng**.

Mental model:

````text
HTML
 │
 ├── <code>          → inline code
 │
 └── <pre><code>     → code block
                         ↓
                    Markdown
                         ↓
                  ```python
                  ...
                  ```
````

---

# 1. Inline code vs Code Block

Đây là distinction quan trọng nhất.

## Inline code

HTML:

```html
<p>
    Dùng <code>print()</code> để in dữ liệu.
</p>
```

Markdown:

```markdown
Dùng `print()` để in dữ liệu.
```

Semantic:

```text
<p>
 ├── text
 ├── code
 └── text
```

---

## Code block

HTML:

```html
<pre>
print("Hello")
print("World")
</pre>
```

Markdown cần biểu diễn thành block:

````markdown
```
print("Hello")
print("World")
```
````

Semantic:

```text
<pre>
 └── code
```

---

# 2. Chạy thử

```python
import html2text

html = """
<p>
Dùng <code>print()</code> để in dữ liệu.
</p>

<pre>
print("Hello")
print("World")
</pre>
"""

converter = html2text.HTML2Text()
converter.body_width = 0

print(converter.handle(html))
```

Bạn sẽ thấy hai loại output khác nhau:

```text
inline
↓
`print()`

block
↓
code block
```

---

# 3. `<pre>` có ý nghĩa gì?

HTML:

```html
<pre>
    line 1
        line 2
    line 3
</pre>
```

`<pre>` có nghĩa:

> Preserve preformatted text.

Tức là whitespace và newline bên trong nó có ý nghĩa.

Đây là điểm cực kỳ quan trọng.

Với paragraph:

```html
<p>
    Hello
       World
</p>
```

whitespace có thể được normalize.

Nhưng với:

```html
<pre>
    Hello
       World
</pre>
```

thì indentation có thể là **một phần của dữ liệu**.

---

# 4. Code block không được xử lý như text bình thường

Hãy tưởng tượng code:

```python
def hello():
    print("Hello")

    if True:
        print("Python")
```

Nếu converter phá indentation:

```python
def hello():
print("Hello")
if True:
print("Python")
```

thì code đã bị hỏng.

Do đó pipeline phải coi:

```text
normal text
```

và:

```text
code
```

là hai loại dữ liệu khác nhau.

---

# 5. `<pre><code>`

Đây là pattern phổ biến nhất:

```html
<pre>
<code>
def hello():
    print("Hello")
</code>
</pre>
```

Semantic:

```text
pre
└── code
```

Trong Markdown:

````markdown
```
def hello():
    print("Hello")
```
````

---

# 6. Code có language

Website thường có:

```html
<pre>
<code class="language-python">
def hello():
    print("Hello")
</code>
</pre>
```

Ta muốn:

````markdown
```python
def hello():
    print("Hello")
```
````

Nhưng có một điểm quan trọng:

> Không phải mọi HTML → Markdown converter đều tự động suy luận language theo cách bạn mong muốn.

Do đó crawler chuyên nghiệp thường có bước:

````text
<code class="language-python">
             ↓
       detect language
             ↓
        ```python
````

---

# 7. Detect language từ class

Ví dụ HTML:

```html
<pre>
<code class="language-python">
print("Hello")
</code>
</pre>
```

Ta có thể dùng Selectolax:

```python
from selectolax.parser import HTMLParser

html = """
<pre>
<code class="language-python">
print("Hello")
</code>
</pre>
"""

tree = HTMLParser(html)

code = tree.css_first("pre code")

print(code.attributes.get("class"))
```

Kết quả:

```text
language-python
```

Ta có thể lấy:

```python
class_name = code.attributes.get("class", "")
```

rồi xử lý.

---

# 8. Các convention thường gặp

Website có thể dùng:

```text
language-python
lang-python
python
highlight-python
brush: python
```

Ví dụ:

```html
<code class="language-python">
```

hoặc:

```html
<code class="lang-python">
```

Do đó một parser thực tế có thể có:

```python
def detect_language(class_name: str) -> str | None:
    for prefix in ("language-", "lang-"):
        if class_name.startswith(prefix):
            return class_name[len(prefix):]

    return None
```

---

# 9. Code block chứa HTML entities

Ví dụ:

```html
<pre>
<code>
if x &lt; 10:
    print("Hello")
</code>
</pre>
```

Ta muốn code cuối cùng:

```python
if x < 10:
    print("Hello")
```

chứ không phải:

```python
if x &lt; 10:
```

HTML parser phải decode HTML entity đúng cách.

Đây là một lý do nữa để **không dùng regex để xử lý HTML**.

---

# 10. Code có `<span>`

Syntax highlighting thường tạo HTML rất phức tạp:

```html
<pre>
<code class="language-python">
<span class="keyword">def</span>
<span class="function">hello</span>():
    <span class="keyword">return</span> <span class="string">"Hello"</span>
</code>
</pre>
```

Nếu bạn lấy HTML trực tiếp và xử lý không đúng, có thể nhận được Markdown rác:

```text
keyword
function
string
```

Trong trường hợp này ta muốn:

```python
def hello():
    return "Hello"
```

Tức là:

```text
HTML syntax highlighting
        ↓
remove presentation markup
        ↓
raw code
        ↓
Markdown code block
```

---

# 11. Đây là nhiệm vụ của HTML Cleaner

Vì vậy kiến trúc tốt:

```text
HTML
 │
 ▼
Parser
 │
 ▼
Code Normalizer
 │
 ├── detect language
 ├── remove syntax highlighting tags
 ├── preserve whitespace
 └── preserve code
 │
 ▼
html2text
 │
 ▼
Markdown
```

Đừng cố bắt `html2text` làm toàn bộ công việc này.

---

# 12. Một vấn đề rất nguy hiểm: indentation

Ví dụ:

```html
<pre><code>
def hello():
    print("Hello")

    if True:
        print("Python")
</code></pre>
```

Có thể có newline thừa ở đầu:

```text
\n
def hello():
...
```

Nếu lưu nguyên:

````markdown
```

def hello():
    print("Hello")
```
````

thì Markdown vẫn có thể render được, nhưng dữ liệu không sạch.

Ta thường muốn:

````markdown
```python
def hello():
    print("Hello")

    if True:
        print("Python")
```
````

---

# 13. Nhưng đừng dùng `.strip()` một cách mù quáng

Sai lầm:

```python
code = code.strip()
```

Có thể phá dữ liệu trong một số trường hợp.

Ví dụ code có ý nghĩa với whitespace đầu/cuối:

```text
    hello
```

hoặc code block có formatting đặc biệt.

Trong crawler, cần phân biệt:

```text
unwanted wrapper whitespace
```

với:

```text
meaningful indentation
```

Đây là một vấn đề parsing chứ không đơn giản là string cleanup.

---

# 14. Inline code có backtick

Một vấn đề thú vị.

HTML:

```html
<p>
Dùng <code>print(`hello`)</code>.
</p>
```

Nếu chuyển đơn giản:

```markdown
Dùng `print(`hello`)`.
```

Markdown sẽ bị lỗi vì backtick bên trong code.

Trong trường hợp này cần dùng fence dài hơn hoặc escaping phù hợp.

Ví dụ:

```markdown
Dùng ``print(`hello`)``.
```

Mental model:

```text
code content
     ↓
contains `
     ↓
need longer delimiter
     ↓
``code content``
```

---

# 15. Code block chứa triple backticks

Đây là case nâng cao nhưng rất thực tế.

Code:

````text
```python
print("Hello")
```
````

Nếu ta bao lại bằng:

````markdown
```
```python
print("Hello")
```
````

thì Markdown bị phá.

Do đó một converter tốt phải tìm fence phù hợp.

Ví dụ:

`````markdown
````text
```python
print("Hello")
```
````
`````

Mental model:

````text
code contains ```
       ↓
outer fence must be longer
       ↓
````

````

---

# 16. `html2text` và code fence

Khi làm việc với `html2text`, bạn nên **kiểm tra output thực tế của phiên bản thư viện đang cài** thay vì giả định tuyệt đối rằng mọi trường hợp `<pre>` đều cho cùng một kiểu fence.

Test:

```python
import html2text

html = """
<pre><code>
def hello():
    print("Hello")
</code></pre>
"""

converter = html2text.HTML2Text()
converter.body_width = 0

print(converter.handle(html))
````

Hãy quan sát:

```text
Có fence không?
Có giữ indentation không?
Có newline thừa không?
Có language không?
```

Đây là cách học library thực tế.

---

# 17. Đừng nhầm `pre` và `code`

### `<code>`

```html
<code>print()</code>
```

thường là:

```markdown
`print()`
```

### `<pre>`

```html
<pre>
print()
</pre>
```

là:

````markdown
```
print()
```
````

### `<pre><code class="language-python">`

là:

````markdown
```python
print()
```
````

nếu language được nhận diện và chuyển đổi.

---

# 18. Code block trong article thực tế

Ví dụ một bài tutorial:

```html
<article>

<h1>Python HTTPX</h1>

<p>
Cài đặt bằng <code>pip install httpx</code>.
</p>

<pre>
<code class="language-python">
import httpx

response = httpx.get(
    "https://example.com"
)

print(response.text)
</code>
</pre>

</article>
```

Mục tiêu Markdown:

````markdown
# Python HTTPX

Cài đặt bằng `pip install httpx`.

```python
import httpx

response = httpx.get(
    "https://example.com"
)

print(response.text)
```
````

Đây là output chất lượng cao mà crawler cần hướng tới.

---

# 19. Pipeline chuyên nghiệp

Từ các buổi trước, kiến trúc bắt đầu thành:

```text
                         HTTPX
                           │
                           ▼
                          HTML
                           │
                           ▼
                     Selectolax
                           │
             ┌─────────────┼─────────────┐
             │             │             │
          Article        Links          Images
          Extractor      Normalize      Normalize
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    Code Normalizer
                           │
                           ▼
                      HTML Cleaner
                           │
                           ▼
                       html2text
                           │
                           ▼
                        Markdown
```

Bạn có thể thấy:

> `html2text` chỉ là **một stage trong pipeline**, không phải toàn bộ pipeline.

---

# 20. Thiết kế `CodeNormalizer`

Ví dụ:

```python
class CodeNormalizer:

    def normalize(self, html: str) -> str:
        ...
```

Nhiệm vụ:

```text
CodeNormalizer
│
├── find <pre>
├── find <code>
├── detect language
├── remove syntax highlighting
├── preserve code text
└── normalize wrapper whitespace
```

Sau này có thể test riêng class này.

Đây chính là tư duy **Single Responsibility**.

---

# 21. Ví dụ detect language

```python
def detect_language(class_name: str) -> str | None:
    parts = class_name.split()

    for part in parts:
        if part.startswith("language-"):
            return part.removeprefix("language-")

        if part.startswith("lang-"):
            return part.removeprefix("lang-")

    return None
```

Test:

```python
print(detect_language("language-python"))
print(detect_language("foo language-javascript"))
print(detect_language("lang-rust"))
```

Kết quả mong muốn:

```text
python
javascript
rust
```

---

# 22. Nhưng language không phải lúc nào cũng đáng tin

Ví dụ:

```html
<code class="language-python hljs">
```

thì:

```python
class_name.split()
```

cho:

```text
[
    "language-python",
    "hljs"
]
```

Ta chỉ lấy:

```text
language-python
```

Một website khác:

```html
<code class="hljs python">
```

thì không có prefix.

Do đó production crawler có thể cần:

```text
language detection strategy
```

với nhiều fallback.

---

# 23. Fallback language

Một strategy có thể là:

```text
1. language-python
2. lang-python
3. data-language="python"
4. class="python"
5. parent <pre class="python">
6. không xác định
```

Kết quả cuối:

```text
python
```

hoặc:

```text
None
```

Không nên đoán language nếu không có đủ thông tin.

---

# 24. Bài tập 1 — Inline code

Cho:

```html
<p>
Dùng <code>httpx.get()</code>
để gửi HTTP request.
</p>
```

Hãy dự đoán Markdown.

---

# 25. Bài tập 2 — Code block

Cho:

```html
<pre>
def hello():
    print("Hello")
</pre>
```

Hãy chạy `html2text` và quan sát output.

---

# 26. Bài tập 3 — Language

Cho:

```html
<pre>
<code class="language-python">
def hello():
    print("Hello")
</code>
</pre>
```

Kiểm tra:

```text
html2text có tự thêm python vào fence không?
```

Đây là bài tập quan trọng.

**Không đoán. Hãy chạy.**

---

# 27. Bài tập 4 — Syntax highlighting

Cho:

```html
<pre>
<code class="language-python">
<span class="keyword">def</span>
<span class="function">hello</span>():
    <span class="keyword">return</span>
        <span class="string">"Hello"</span>
</code>
</pre>
```

Mục tiêu:

```python
def hello():
    return "Hello"
```

Hãy suy nghĩ:

> Nên để `html2text` xử lý trực tiếp hay cần một bước cleaner trước?

---

# 28. Bài tập 5 — Code thực tế

Tạo HTML:

```html
<article>

<h1>HTTPX Tutorial</h1>

<p>
Cài đặt:
<code>pip install httpx</code>
</p>

<h2>GET request</h2>

<pre>
<code class="language-python">
import httpx

response = httpx.get(
    "https://example.com"
)

print(response.status_code)
</code>
</pre>

<blockquote>
HTTPX là HTTP client hiện đại cho Python.
</blockquote>

</article>
```

Mục tiêu:

````markdown
# HTTPX Tutorial

Cài đặt: `pip install httpx`

## GET request

```python
import httpx

response = httpx.get(
    "https://example.com"
)

print(response.status_code)
```

> HTTPX là HTTP client hiện đại cho Python.
````

Hãy so sánh output thực tế của `html2text` với output mục tiêu.

---

# 29. Bài tập thiết kế

Tạo class:

```python
class CodeNormalizer:
    def normalize(self, html: str) -> str:
        ...
```

và class:

```python
class MarkdownConverter:
    def convert(self, html: str) -> str:
        ...
```

Pipeline:

```text
HTML
 ↓
CodeNormalizer
 ↓
MarkdownConverter
 ↓
Markdown
```

Chưa cần hoàn thiện 100%.

Mục tiêu là luyện **separation of concerns**.

---

# 30. Mental model sau Buổi 5

Bạn cần nhớ:

````text
<code>
   │
   ├── inline
   │      ↓
   │     `code`
   │
   └── nằm trong <pre>
          ↓
       code block
          ↓
       ```...```
````

Và:

````text
<pre><code class="language-python">
            ↓
      detect language
            ↓
         python
            ↓
      ```python
````

Quan trọng nhất:

```text
Code ≠ normal text
```

Code phải được xử lý với quy tắc riêng:

```text
preserve indentation
preserve newline
preserve characters
preserve entities
preserve nested syntax
preserve fence
```

---

## Bài tập tổng hợp 1–5

Đây là bài tôi khuyên bạn **thực sự code**, thay vì chỉ đọc.

Viết chương trình:

```text
html_to_md.py
```

nhận:

```python
html: str
```

và convert:

```text
<h1>
<p>
<strong>
<em>
<ul>
<ol>
<a>
<img>
<code>
<pre>
<blockquote>
```

thành Markdown.

Kiến trúc:

```text
HTML
 │
 ▼
Parser
 │
 ├── URL normalization
 ├── Image normalization
 ├── Code normalization
 └── HTML cleaning
 │
 ▼
html2text
 │
 ▼
Markdown
```

**Buổi 6** ta sẽ chuyển sang phần **configuration nâng cao của `HTML2Text`**, đặc biệt là các option ảnh hưởng trực tiếp đến output Markdown: `body_width`, link handling, image handling, emphasis, Unicode/entity, wrapping và cách xây một `MarkdownConverter` có configuration rõ ràng thay vì hard-code mọi thứ.
