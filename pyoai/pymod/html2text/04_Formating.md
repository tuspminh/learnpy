# Buổi 4 — Formatting: HTML → Markdown

Hôm nay ta đi sâu vào cách `html2text` chuyển **cấu trúc HTML thành Markdown**.

Đây là buổi rất quan trọng vì từ đây bạn sẽ bắt đầu hiểu `html2text` không chỉ là:

```text
HTML → text
```

mà thực chất là:

```text
HTML semantic structure
        ↓
Markdown semantic structure
```

---

# 1. Mapping HTML → Markdown

Trước tiên hãy nhớ bảng này:

| HTML           | Markdown                  |
| -------------- | ------------------------- |
| `<h1>`         | `#`                       |
| `<h2>`         | `##`                      |
| `<h3>`         | `###`                     |
| `<p>`          | paragraph                 |
| `<strong>`     | `**...**`                 |
| `<b>`          | `**...**`                 |
| `<em>`         | `*...*`                   |
| `<i>`          | `*...*`                   |
| `<del>`        | `~~...~~` hoặc tùy output |
| `<code>`       | `` `...` ``               |
| `<pre>`        | code block                |
| `<blockquote>` | `>`                       |
| `<ul>`         | `*` / `-`                 |
| `<ol>`         | `1.`                      |
| `<li>`         | list item                 |

Ta sẽ lần lượt kiểm tra.

---

# 2. Heading

HTML:

```html
<h1>Python</h1>
<h2>Python cơ bản</h2>
<h3>Biến</h3>
```

Python:

```python
import html2text

html = """
<h1>Python</h1>
<h2>Python cơ bản</h2>
<h3>Biến</h3>
"""

converter = html2text.HTML2Text()

print(converter.handle(html))
```

Markdown:

```markdown
# Python

## Python cơ bản

### Biến
```

---

# 3. Heading là semantic structure

Đừng nghĩ:

```text
<h1>
```

chỉ là:

```text
font-size lớn
```

Trong HTML:

```text
h1
h2
h3
```

mang **ý nghĩa cấu trúc**.

Vì vậy khi chuyển sang Markdown:

```text
<h1> → #
<h2> → ##
<h3> → ###
```

là một mapping rất tự nhiên.

---

# 4. `<p>` — Paragraph

HTML:

```html
<p>Hello Python</p>
<p>Python rất dễ học.</p>
```

→

```markdown
Hello Python

Python rất dễ học.
```

Lưu ý:

`<p>` không trở thành một ký tự Markdown đặc biệt.

Nó trở thành **paragraph + newline**.

---

# 5. `<strong>`

HTML:

```html
<p>
Python là <strong>ngôn ngữ mạnh</strong>.
</p>
```

→

```markdown
Python là **ngôn ngữ mạnh**.
```

Code:

```python
html = """
<p>
Python là <strong>ngôn ngữ mạnh</strong>.
</p>
"""

print(html2text.html2text(html))
```

---

# 6. `<b>`

```html
<b>Python</b>
```

thường được chuyển thành:

```markdown
**Python**
```

Tức là:

```text
<strong>
   ↓
**

<b>
   ↓
**
```

---

# 7. `<em>`

HTML:

```html
<em>Python</em>
```

→

```markdown
*Python*
```

---

# 8. `<i>`

HTML:

```html
<i>Python</i>
```

→

```markdown
*Python*
```

Do đó:

```text
<em> ≈ <i>
```

ở cấp Markdown output.

---

# 9. Nested formatting

Đây mới là phần thú vị.

HTML:

```html
<p>
Python là
<strong>
    rất <em>mạnh</em>
</strong>
</p>
```

Về semantic:

```text
strong
 └── em
```

Markdown tương ứng có thể là:

```markdown
Python là **rất *mạnh***.
```

Ta thấy:

```text
HTML
 │
 └── strong
       │
       └── em

        ↓

Markdown
 │
 └── **
       │
       └── *
```

Đây là lý do việc parse DOM rất quan trọng.

---

# 10. `ignore_emphasis`

Nếu:

```python
converter.ignore_emphasis = True
```

thì các formatting như:

```html
<strong>Python</strong>
```

và:

```html
<em>Python</em>
```

sẽ không còn được biểu diễn bằng Markdown emphasis như bình thường.

Ví dụ:

```python
converter = html2text.HTML2Text()

converter.ignore_emphasis = True

html = """
<p>
Python là <strong>mạnh</strong>
và <em>dễ học</em>.
</p>
"""

print(converter.handle(html))
```

Tư duy:

```text
HTML formatting
      ↓
ignore_emphasis
      ↓
plain text
```

---

# 11. `<del>` / `<s>`

HTML:

```html
<del>Python 2</del>
```

Markdown hiện đại thường dùng:

```markdown
~~Python 2~~
```

Nhưng output cụ thể có thể phụ thuộc vào phiên bản/configuration của `html2text`.

Điểm quan trọng:

> Không nên xây pipeline dựa vào việc đoán chính xác từng ký tự Markdown của mọi phiên bản.

Hãy kiểm thử output của phiên bản `html2text` bạn đang dùng.

---

# 12. Inline `<code>`

HTML:

```html
<p>
Dùng hàm <code>print()</code>.
</p>
```

→

```markdown
Dùng hàm `print()`.
```

Đây là **inline code**.

Khác với:

```html
<pre>
...
</pre>
```

là code block.

---

# 13. Tại sao inline code quan trọng?

Ví dụ tài liệu Python:

```html
<p>
Dùng <code>list.append()</code> để thêm phần tử.
</p>
```

Nếu chuyển thành plain text:

```text
Dùng list.append() để thêm phần tử.
```

ta mất semantic.

Markdown:

```markdown
Dùng `list.append()` để thêm phần tử.
```

giữ được semantic đó.

---

# 14. `<blockquote>`

HTML:

```html
<blockquote>
Python is easy to learn.
</blockquote>
```

→

```markdown
> Python is easy to learn.
```

Ví dụ nhiều dòng:

```html
<blockquote>
<p>Python is easy.</p>
<p>Python is powerful.</p>
</blockquote>
```

Markdown có dạng blockquote tương ứng.

Tư duy:

```text
<blockquote>
      ↓
>
```

---

# 15. Nested blockquote

HTML:

```html
<blockquote>
    <p>Hello</p>

    <blockquote>
        <p>Nested quote</p>
    </blockquote>
</blockquote>
```

Về Markdown:

```markdown
> Hello
>
> > Nested quote
```

Ta thấy DOM hierarchy được chuyển thành Markdown hierarchy.

---

# 16. Unordered list

HTML:

```html
<ul>
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
```

→

```markdown
* Python
* Rust
* Go
```

Một số configuration/version có thể cho marker khác.

Điều quan trọng là **list semantic được giữ lại**.

---

# 17. Ordered list

HTML:

```html
<ol>
    <li>Install Python</li>
    <li>Write code</li>
    <li>Run program</li>
</ol>
```

→

```markdown
1. Install Python
2. Write code
3. Run program
```

---

# 18. Nested list

Đây là trường hợp rất hay gặp trong documentation.

HTML:

```html
<ul>
    <li>
        Python

        <ul>
            <li>Syntax</li>
            <li>OOP</li>
        </ul>
    </li>

    <li>Rust</li>
</ul>
```

Về semantic:

```text
Python
 ├── Syntax
 └── OOP

Rust
```

Markdown:

```markdown
* Python
    * Syntax
    * OOP
* Rust
```

Đây là một ví dụ rất rõ về:

> HTML tree → Markdown tree.

---

# 19. List + formatting

HTML:

```html
<ul>
    <li>
        <strong>Python</strong>
    </li>

    <li>
        <em>Rust</em>
    </li>
</ul>
```

→

```markdown
* **Python**
* *Rust*
```

Formatting có thể nằm bên trong list item.

---

# 20. `<br>`

HTML:

```html
Hello<br>
World
```

có thể tạo line break trong Markdown.

Đây là một điểm cần chú ý khi xử lý website.

Website đôi khi có:

```html
<p>
    Chapter 1<br>
    Chapter 2<br>
    Chapter 3
</p>
```

Nếu bạn đang xử lý **truyện**, `<br>` có thể cực kỳ quan trọng.

---

# 21. `<div>` không phải paragraph

Đây là lỗi tư duy phổ biến.

Ví dụ:

```html
<div>
    Hello
</div>

<div>
    World
</div>
```

Không nên tự động suy nghĩ:

```text
<div> = <p>
```

Vì HTML semantic của chúng khác nhau.

Trong crawler, nếu website dùng `<div>` để chứa từng đoạn truyện:

```html
<div class="chapter">
    <div>Đoạn 1...</div>
    <div>Đoạn 2...</div>
</div>
```

thì ta phải xem **DOM thực tế** và output thực tế.

Đừng áp đặt giả định.

---

# 22. Whitespace trong HTML

Ví dụ:

```html
<p>
    Python
       là

    ngôn ngữ
    lập trình.
</p>
```

Browser có cách render whitespace riêng.

Markdown cũng có quy tắc riêng.

Vì vậy:

```text
HTML whitespace
       ↓
html2text
       ↓
Markdown whitespace
```

không nhất thiết giữ nguyên byte-for-byte.

Đây là điều bình thường.

---

# 23. `body_width = 0`

Trong crawler, tôi khuyến nghị bạn thử:

```python
converter.body_width = 0
```

Ví dụ:

```python
converter = html2text.HTML2Text()

converter.body_width = 0

markdown = converter.handle(html)
```

Sau đó bạn có thể tự normalize:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
normalize whitespace
 ↓
save
```

Thay vì để converter tự wrap quá nhiều.

---

# 24. Một article hoàn chỉnh

Giả sử:

```html
<article>

<h1>Python</h1>

<p>
Python là <strong>ngôn ngữ lập trình</strong>.
</p>

<h2>Ưu điểm</h2>

<ul>
    <li>Dễ học</li>
    <li>Mạnh</li>
    <li>Cộng đồng lớn</li>
</ul>

<h2>Ví dụ</h2>

<p>
Dùng <code>print()</code> để in dữ liệu.
</p>

<blockquote>
Python is powerful.
</blockquote>

</article>
```

Ta có semantic tree:

```text
article
│
├── h1
├── p
│    └── strong
│
├── h2
├── ul
│    ├── li
│    ├── li
│    └── li
│
├── h2
├── p
│    └── code
│
└── blockquote
```

Sau `html2text`:

```markdown
# Python

Python là **ngôn ngữ lập trình**.

## Ưu điểm

* Dễ học
* Mạnh
* Cộng đồng lớn

## Ví dụ

Dùng `print()` để in dữ liệu.

> Python is powerful.
```

Đây chính là điều bạn cần hiểu sâu:

```text
DOM Tree
   ↓
Semantic interpretation
   ↓
Markdown structure
```

---

# 25. Một bài test rất tốt

Hãy tự tạo:

```python
html = """
<h1>Python</h1>

<p>
Python là <strong>mạnh</strong>
và <em>dễ học</em>.
</p>

<h2>Features</h2>

<ul>
    <li>
        <strong>Easy</strong>
    </li>

    <li>
        <em>Powerful</em>
    </li>
</ul>

<blockquote>
    Python is great.
</blockquote>

<p>
Dùng <code>print()</code>.
</p>
"""
```

Sau đó:

```python
import html2text

converter = html2text.HTML2Text()

converter.body_width = 0

print(converter.handle(html))
```

Đừng chỉ nhìn output.

Hãy tự dự đoán trước:

```text
<h1>       → ?
<strong>   → ?
<em>       → ?
<h2>       → ?
<ul>       → ?
<li>       → ?
<blockquote> → ?
<code>     → ?
```

Sau đó mới chạy.

Đây là cách học nhanh hơn nhiều.

---

# 26. Thiết kế converter cho project

Sau 4 buổi, ta có thể bắt đầu chuẩn hóa:

```python
import html2text


class MarkdownConverter:

    def __init__(self):
        self._converter = html2text.HTML2Text()

        self._converter.body_width = 0

        self._converter.ignore_links = False
        self._converter.ignore_images = False
        self._converter.ignore_emphasis = False

        self._converter.skip_internal_links = True

    def convert(self, html: str) -> str:
        return self._converter.handle(html)
```

API rất sạch:

```python
converter = MarkdownConverter()

markdown = converter.convert(html)
```

Sau này:

```text
MarkdownConverter
│
├── configuration
├── convert()
├── normalize()
└── clean()
```

---

# 27. Một nguyên tắc kiến trúc rất quan trọng

Đừng làm:

```python
class MarkdownConverter:

    def convert(self, url):
        # HTTP request
        # parse HTML
        # remove ads
        # resolve URL
        # convert markdown
        # save file
```

Đó là **God Object**.

Thay vào đó:

```text
Fetcher
   ↓
Parser
   ↓
Cleaner
   ↓
URLNormalizer
   ↓
MarkdownConverter
   ↓
Writer
```

Mỗi thành phần một trách nhiệm.

Điều này liên kết trực tiếp với những gì bạn đang học về **SOLID / Clean Architecture / DDD**.

---

# 28. Bài tập Buổi 4

### Bài 1 — Basic formatting

Viết HTML chứa:

```text
h1
h2
h3
p
strong
em
code
blockquote
```

và chuyển sang Markdown.

---

### Bài 2 — Nested formatting

Tạo:

```html
<p>
    Đây là
    <strong>
        một đoạn <em>quan trọng</em>
    </strong>
</p>
```

Dự đoán output trước khi chạy.

---

### Bài 3 — Nested list

Tạo:

```html
<ul>
    <li>
        Python

        <ul>
            <li>Syntax</li>
            <li>OOP</li>
        </ul>
    </li>

    <li>Rust</li>
</ul>
```

Kiểm tra Markdown.

---

### Bài 4 — Article

Tạo một HTML khoảng 20–30 dòng có:

```text
<h1>
<p>
<strong>
<em>
<ul>
<ol>
<li>
<blockquote>
<code>
<a>
<img>
```

Sau đó convert.

---

### Bài 5 — Quan trọng nhất

Viết class:

```python
class MarkdownConverter:
    ...
```

với:

```python
converter = MarkdownConverter()

result = converter.convert(html)
```

Không sử dụng BeautifulSoup/Selectolax.

Mục tiêu là **chỉ tập trung vào HTML → Markdown**.

---

# 29. Tổng kết Buổi 4

Bạn cần hình thành mental model này:

```text
                  HTML
                   │
                   ▼
              DOM / Tree
                   │
       ┌───────────┼───────────┐
       │           │           │
   Heading     Formatting     List
       │           │           │
       ▼           ▼           ▼
      #          **text**      *
                   │
                   ▼
               Markdown
```

Mapping quan trọng:

```text
<h1>        → #
<h2>        → ##
<strong>    → **
<em>        → *
<code>      → ``
<blockquote>→ >
<ul>        → *
<ol>        → 1.
<li>        → item
```

Và đặc biệt:

> **`html2text` bảo toàn semantic structure tốt hơn rất nhiều so với việc dùng regex để biến HTML thành Markdown.**

**Buổi 5** chúng ta sẽ tập trung riêng vào **Code Block** — `<pre>`, `<code>`, fenced code block, inline code, multiline code, indentation, syntax highlighting và cách xây pipeline để **không làm hỏng source code** khi crawl các trang có code.
