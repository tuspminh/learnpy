
# 🚀 Buổi 1 — Selectolax Foundation

## 1. Selectolax là gì?

`selectolax` là thư viện Python dùng để **parse và truy vấn HTML/XML**.

Nói đơn giản:

```text
HTML
 ↓
Selectolax
 ↓
DOM Tree
 ↓
CSS Selector
 ↓
Data
```

Ví dụ HTML:

```html
<html>
    <body>
        <h1>Hello Python</h1>
        <p class="content">Learning Selectolax</p>
    </body>
</html>
```

Ta muốn lấy:

```text
Hello Python
Learning Selectolax
```

Selectolax cho phép chúng ta truy vấn trực tiếp bằng CSS selector.

---

# 2. Cài đặt

```bash
pip install selectolax
```

Nếu bạn dùng `uv`:

```bash
uv add selectolax
```

Kiểm tra:

```python
import selectolax

print(selectolax)
```

---

# 3. Parse HTML

Ví dụ đầu tiên:

```python
from selectolax.parser import HTMLParser


html = """
<html>
    <body>
        <h1>Hello Python</h1>
        <p>Learning Selectolax</p>
    </body>
</html>
"""

tree = HTMLParser(html)

print(tree)
```

Ở đây:

```python
tree = HTMLParser(html)
```

`tree` đại diện cho **cây DOM** được Selectolax tạo ra từ HTML.

---

# 4. Lấy một element

Selectolax có:

```python
css_first()
```

Ví dụ:

```python
title = tree.css_first("h1")

print(title)
```

Ta có thể lấy text:

```python
print(title.text())
```

Kết quả:

```text
Hello Python
```

---

# 5. CSS selector

Đây là phần cực kỳ quan trọng.

Ví dụ:

```html
<h1>Hello Python</h1>
<p class="content">Learning Selectolax</p>
```

Lấy `h1`:

```python
tree.css_first("h1")
```

Lấy class:

```python
tree.css_first(".content")
```

Hoặc:

```python
tree.css_first("p.content")
```

---

# 6. `css_first()` vs `css()`

Đây là hai API bạn sẽ dùng **rất thường xuyên**.

### `css_first()`

Lấy **node đầu tiên** phù hợp selector.

```python
node = tree.css_first("p")
```

Nếu HTML:

```html
<p>One</p>
<p>Two</p>
<p>Three</p>
```

thì:

```python
node.text()
```

cho:

```text
One
```

---

### `css()`

Lấy **tất cả node** phù hợp selector.

```python
nodes = tree.css("p")
```

Sau đó:

```python
for node in nodes:
    print(node.text())
```

Kết quả:

```text
One
Two
Three
```

---

# 7. Một ví dụ crawler rất điển hình

Giả sử website có:

```html
<div class="books">
    <article class="book">
        <h2>Python</h2>
    </article>

    <article class="book">
        <h2>Rust</h2>
    </article>

    <article class="book">
        <h2>Go</h2>
    </article>
</div>
```

Ta có thể:

```python
from selectolax.parser import HTMLParser


html = """
<div class="books">
    <article class="book">
        <h2>Python</h2>
    </article>

    <article class="book">
        <h2>Rust</h2>
    </article>

    <article class="book">
        <h2>Go</h2>
    </article>
</div>
"""

tree = HTMLParser(html)

books = tree.css("article.book")

for book in books:
    title = book.css_first("h2")
    print(title.text())
```

Kết quả:

```text
Python
Rust
Go
```

Đây chính là pattern cơ bản của scraping:

```text
HTML
 ↓
Select collection
 ↓
Loop
 ↓
Select child
 ↓
Extract data
```

---

# 8. `.text()` và `.html()`

Giả sử:

```html
<div class="article">
    <h1>Hello</h1>
    <p>Python <strong>is great</strong></p>
</div>
```

Ta lấy:

```python
article = tree.css_first(".article")
```

### `.text()`

```python
print(article.text())
```

Lấy **text bên trong node**.

---

### `.html()`

```python
print(article.html)
```

Lấy **HTML bên trong node**.

Điểm cần nhớ:

```text
.text()
    ↓
plain text

.html
    ↓
inner HTML
```

---

# 9. Một lỗi rất quan trọng

Không phải selector nào cũng tồn tại.

Ví dụ:

```python
node = tree.css_first(".not-exist")
```

`node` có thể là:

```python
None
```

Do đó không nên viết:

```python
print(node.text())
```

một cách mù quáng.

Nên:

```python
node = tree.css_first(".not-exist")

if node:
    print(node.text())
```

Hoặc thiết kế extractor riêng để xử lý missing data.

Đây sẽ là vấn đề chúng ta đào sâu ở **Buổi 12 — Error Handling**.

---

# 10. Bài tập Buổi 1

Cho HTML:

```html
<html>
    <body>
        <h1 class="title">Learning Python</h1>

        <div class="articles">
            <article>
                <h2>HTTPX</h2>
                <p>HTTP client for Python</p>
            </article>

            <article>
                <h2>Selectolax</h2>
                <p>Fast HTML parser</p>
            </article>

            <article>
                <h2>Asyncio</h2>
                <p>Asynchronous programming</p>
            </article>
        </div>
    </body>
</html>
```

Hãy viết chương trình:

### Bài 1

Lấy:

```text
Learning Python
```

### Bài 2

Lấy tất cả `h2`:

```text
HTTPX
Selectolax
Asyncio
```

### Bài 3

Lấy toàn bộ `article`, sau đó in:

```text
HTTPX - HTTP client for Python
Selectolax - Fast HTML parser
Asyncio - Asynchronous programming
```

### Bài 4 — Quan trọng

Viết function:

```python
def parse_articles(html: str) -> list[dict]:
    ...
```

Kết quả:

```python
[
    {
        "title": "HTTPX",
        "description": "HTTP client for Python",
    },
    {
        "title": "Selectolax",
        "description": "Fast HTML parser",
    },
    {
        "title": "Asyncio",
        "description": "Asynchronous programming",
    },
]
```

**Buổi 2** chúng ta sẽ đi sâu vào **CSS Selector**, vì đây là kỹ năng quan trọng nhất khi dùng Selectolax để crawl website.
