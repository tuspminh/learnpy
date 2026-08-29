Được. Tôi sẽ dạy **`html2text` trong Python theo kiểu Deep Dive**, tập trung vào cách dùng thực tế để xây dựng các tool xử lý HTML → Markdown, đặc biệt phù hợp với hướng bạn đang học về **HTTPX + Selectolax + BeautifulSoup + crawler + ứng dụng đọc truyện**.

# Giáo trình học `html2text`

## Phần I — Foundation

1. **Buổi 1 — HTML → Markdown là gì?**

   * `html2text` là gì?
   * Cài đặt
   * HTML → Markdown
   * `html2text.html2text()`
   * `HTML2Text`
   * So sánh `html2text` với BeautifulSoup
   * Khi nào nên dùng `html2text`

2. **Buổi 2 — `HTML2Text` Deep Dive**

   * Tạo converter
   * Cấu hình converter
   * `body_width`
   * `ignore_links`
   * `ignore_images`
   * `ignore_emphasis`
   * `skip_internal_links`

3. **Buổi 3 — Link & Image**

   * `<a>`
   * `<img>`
   * Markdown links
   * Reference links
   * Inline links
   * Xử lý link tương đối

4. **Buổi 4 — Formatting**

   * `<strong>`
   * `<em>`
   * `<del>`
   * `<code>`
   * `<pre>`
   * Heading
   * List
   * Blockquote

5. **Buổi 5 — Code Block**

   * Inline code
   * Fenced code
   * `<pre><code>`
   * Syntax highlighting
   * Giữ nguyên source code
   * Xử lý code trong bài viết

---

# Phần II — Configuration Deep Dive

6. **Buổi 6 — Các option quan trọng**
7. **Buổi 7 — `body_width`**
8. **Buổi 8 — Link configuration**
9. **Buổi 9 — Image configuration**
10. **Buổi 10 — Unicode & HTML entities**
11. **Buổi 11 — Whitespace & newline**
12. **Buổi 12 — Escape Markdown**

---

# Phần III — Pipeline HTML → Markdown

13. **Buổi 13 — BeautifulSoup → html2text**

```text
HTML
 ↓
BeautifulSoup
 ↓
Remove unwanted elements
 ↓
Clean HTML
 ↓
html2text
 ↓
Markdown
```

14. **Buổi 14 — Selectolax → html2text**

```text
HTTPX
  ↓
HTML
  ↓
Selectolax
  ↓
Extract article
  ↓
html2text
  ↓
Markdown
```

15. **Buổi 15 — Xây dựng HTML Cleaner**
16. **Buổi 16 — Remove quảng cáo**
17. **Buổi 17 — Remove navigation**
18. **Buổi 18 — Remove script/style**
19. **Buổi 19 — Chuẩn hóa whitespace**
20. **Buổi 20 — Article extraction**

---

# Phần IV — Project

### Buổi 21 — HTML → Markdown CLI

```bash
html2md article.html
```

### Buổi 22 — URL → Markdown

```bash
html2md https://example.com/article
```

Kiến trúc:

```text
HTTPX
   ↓
Fetcher
   ↓
HTML Cleaner
   ↓
html2text
   ↓
Markdown
```

### Buổi 23 — Crawl → Markdown

```text
Crawler
   ↓
HTML
   ↓
Parser
   ↓
Cleaner
   ↓
Markdown
   ↓
File
```

### Buổi 24 — Markdown Writer

```text
article/
    001.md
    002.md
    003.md
```

### Buổi 25 — Mini Project

**Web Article Extractor**

```text
URL
 ↓
HTTPX
 ↓
Selectolax
 ↓
Article Extractor
 ↓
HTML Cleaner
 ↓
html2text
 ↓
Markdown
 ↓
SQLite / File
```

---

# Buổi 1 — HTML → Markdown

## 1. `html2text` dùng để làm gì?

Giả sử chúng ta có HTML:

```html
<h1>Hello Python</h1>

<p>
    Python là một <strong>ngôn ngữ lập trình</strong>.
</p>

<p>
    Xem <a href="https://python.org">Python</a>.
</p>
```

Ta muốn chuyển thành Markdown:

```markdown
# Hello Python

Python là một **ngôn ngữ lập trình**.

Xem [Python](https://python.org).
```

Đây chính là nhiệm vụ của `html2text`.

---

# 2. Cài đặt

```bash
pip install html2text
```

Nếu bạn dùng `uv`:

```bash
uv add html2text
```

---

# 3. Cách đơn giản nhất

```python
import html2text

html = """
<h1>Hello Python</h1>

<p>
    Python là một <strong>ngôn ngữ lập trình</strong>.
</p>
"""

markdown = html2text.html2text(html)

print(markdown)
```

Kết quả đại khái:

```markdown
# Hello Python

Python là một **ngôn ngữ lập trình**.
```

API:

```python
html2text.html2text(html)
```

nhận HTML và trả về Markdown.

---

# 4. `html2text` thực chất làm gì?

Hãy hình dung:

```text
HTML
 │
 │ parser
 ▼
HTML structure
 │
 │ converter
 ▼
Markdown
```

Ví dụ:

```html
<h1>Python</h1>
```

được chuyển thành:

```markdown
# Python
```

---

### `<strong>`

```html
<strong>Python</strong>
```

→

```markdown
**Python**
```

---

### `<em>`

```html
<em>Python</em>
```

→

```markdown
*Python*
```

---

### `<a>`

```html
<a href="https://python.org">
    Python
</a>
```

→

```markdown
[Python](https://python.org)
```

---

### `<ul>`

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

---

# 5. `html2text` và BeautifulSoup khác nhau thế nào?

Đây là điểm **rất quan trọng**.

### BeautifulSoup

BeautifulSoup chủ yếu dùng để:

> **parse và thao tác HTML**

Ví dụ:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

for p in soup.find_all("p"):
    print(p.get_text())
```

Nó rất mạnh trong việc:

```text
HTML
 ↓
Parse
 ↓
Find
 ↓
Remove
 ↓
Modify
 ↓
Extract
```

---

### html2text

`html2text` tập trung vào:

```text
HTML
 ↓
Markdown
```

Ví dụ:

```python
markdown = html2text.html2text(html)
```

---

# 6. Vì vậy không nên nghĩ:

```text
BeautifulSoup OR html2text
```

Mà nên nghĩ:

```text
BeautifulSoup
      ↓
Cleaning
      ↓
html2text
      ↓
Markdown
```

Đây là pipeline cực kỳ hữu ích.

Ví dụ website có:

```html
<body>

    <nav>...</nav>

    <div class="advertisement">
        QUẢNG CÁO
    </div>

    <article>
        <h1>Python Tutorial</h1>

        <p>Nội dung...</p>
    </article>

    <footer>...</footer>

</body>
```

Ta **không nên** đưa toàn bộ HTML vào `html2text`.

Thay vào đó:

```text
HTML
 │
 ▼
BeautifulSoup
 │
 ├── remove nav
 ├── remove advertisement
 ├── remove footer
 │
 ▼
<article>
 │
 ▼
html2text
 │
 ▼
Markdown
```

Đây chính là tư duy mà bạn sẽ dùng khi xây dựng crawler.

---

# 7. `HTML2Text` class

Ngoài hàm:

```python
html2text.html2text(html)
```

thư viện còn cung cấp class:

```python
html2text.HTML2Text
```

Ví dụ:

```python
import html2text

converter = html2text.HTML2Text()

html = """
<h1>Hello</h1>
<p>Hello <strong>Python</strong></p>
"""

markdown = converter.handle(html)

print(markdown)
```

Điểm khác biệt:

```python
html2text.html2text(html)
```

là cách **nhanh và đơn giản**.

Còn:

```python
converter = html2text.HTML2Text()
converter.handle(html)
```

cho phép chúng ta **cấu hình converter**.

---

# 8. Tại sao phải dùng `HTML2Text`?

Ví dụ chúng ta muốn bỏ link:

```python
import html2text

converter = html2text.HTML2Text()

converter.ignore_links = True

html = """
<p>
    Visit
    <a href="https://python.org">Python</a>
</p>
"""

print(converter.handle(html))
```

Thay vì:

```markdown
Visit [Python](https://python.org)
```

ta có thể cấu hình để bỏ thông tin link.

Đây là lý do `HTML2Text` rất quan trọng khi làm project thật.

---

# 9. Tư duy kiến trúc

Một converter tốt có thể được thiết kế:

```python
class MarkdownConverter:
    def __init__(self):
        self.converter = html2text.HTML2Text()

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

Sử dụng:

```python
converter = MarkdownConverter()

markdown = converter.convert(html)
```

Sau này có thể mở rộng:

```text
MarkdownConverter
       │
       ├── configure()
       ├── clean()
       ├── convert()
       └── normalize()
```

---

# 10. Bài tập Buổi 1

### Bài 1

Cho HTML:

```python
html = """
<h1>Python</h1>

<p>
Python là <strong>ngôn ngữ lập trình</strong>.
</p>

<p>
Học <em>Python mỗi ngày</em>.
</p>

<a href="https://python.org">
Python.org
</a>
"""
```

Hãy dùng `html2text` chuyển thành Markdown.

---

### Bài 2

Thử các HTML sau:

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
```

Quan sát Markdown tạo ra.

---

### Bài 3

Thử:

```html
<ul>
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
```

và:

```html
<ol>
    <li>Install Python</li>
    <li>Write code</li>
    <li>Run program</li>
</ol>
```

Quan sát sự khác nhau.

---

### Bài 4 — Quan trọng

Tạo:

```python
converter = html2text.HTML2Text()
```

và thử:

```python
converter.ignore_links = True
converter.ignore_images = True
converter.ignore_emphasis = True
```

Sau mỗi lần thay đổi, chạy lại HTML và quan sát kết quả.

---

## Kiến thức cần nhớ sau Buổi 1

```text
html2text
│
├── html2text.html2text()
│
└── HTML2Text
      │
      ├── configuration
      └── handle()
```

Và quan trọng nhất:

```text
BeautifulSoup / Selectolax
        ↓
     Cleaning
        ↓
    html2text
        ↓
     Markdown
```

**Buổi 2** chúng ta sẽ đi sâu vào `HTML2Text`, đặc biệt là **toàn bộ hệ thống configuration**, để bạn hiểu tại sao cùng một HTML nhưng chỉ cần thay đổi `ignore_links`, `ignore_images`, `body_width`, `protect_links`, `skip_internal_links`... thì Markdown đầu ra có thể thay đổi rất nhiều.
