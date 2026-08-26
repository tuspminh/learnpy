Được. Mình sẽ dạy **Selectolax từ cơ bản → nâng cao → áp dụng vào crawler thực tế**, theo kiểu học từng buổi như các khóa Python trước của bạn.

## 📚 Roadmap học Selectolax

### Phần I — Foundation

**Buổi 1 — Selectolax là gì?**

* Selectolax dùng để làm gì?
* So sánh `Selectolax` vs `BeautifulSoup`
* Cài đặt
* Parse HTML
* `HTMLParser`
* Node và cây DOM
* `css_first()`, `css()`
* `.text()`, `.html`

**Buổi 2 — CSS Selector**

* Tag selector
* `.class`
* `#id`
* Attribute selector
* Descendant
* Child selector `>`
* Multiple selector
* `:first-child`, `:nth-child()`
* Selector thực tế khi crawl web

**Buổi 3 — Node Deep Dive**

* `Node`
* `parent`
* `child`
* `iter()`
* `iter_children()`
* `next`
* `prev`
* `attributes`
* `tag`
* `html`
* `text`

**Buổi 4 — Extract dữ liệu**

* Extract text
* Extract HTML
* Extract attribute
* Extract link
* Extract image
* Xử lý node không tồn tại
* Xây dựng hàm `extract_*()`

---

### Phần II — Scraping thực tế

**Buổi 5 — Parse danh sách**

* List item
* Table
* Card
* Article
* Pagination
* Extract nhiều node

**Buổi 6 — Làm sạch HTML**

* Xóa `script`
* Xóa `style`
* Xóa quảng cáo
* Xóa navigation
* Xóa comment
* Giữ lại nội dung bài viết

**Buổi 7 — Selectolax + HTTPX**

```text
HTTPX
  ↓
HTML response
  ↓
Selectolax
  ↓
CSS Selector
  ↓
Extract data
```

* `httpx.Client`
* Headers
* Timeout
* Retry
* Status code
* Parse response

**Buổi 8 — Xây Article Extractor**

```text
URL
 ↓
HTTPX
 ↓
Selectolax
 ↓
ArticleExtractor
 ↓
title
content
author
published_at
images
```

---

### Phần III — Selectolax nâng cao

**Buổi 9 — CSS Selector nâng cao**

**Buổi 10 — DOM Traversal**

**Buổi 11 — Performance**

* Selectolax nhanh vì sao?
* Parse hàng nghìn trang
* So sánh performance với BeautifulSoup

**Buổi 12 — Error Handling**

* Missing selector
* Broken HTML
* Empty response
* Encoding
* Defensive extraction

**Buổi 13 — Thiết kế Scraper**

* Parser
* Extractor
* Repository
* Model
* Separation of concerns

**Buổi 14 — Testing Selectolax**

* Test HTML fixture
* Test selector
* Test extractor
* Regression test

---

### Phần IV — Project thực tế

**Buổi 15 — Mini Crawler**

```text
HTTPX
   ↓
Fetcher
   ↓
Selectolax
   ↓
Parser
   ↓
Model
   ↓
SQLite
```

**Buổi 16 — Crawl website truyện**

* Story
* Chapter
* Author
* Category
* Content

**Buổi 17 — Pagination & Crawl nhiều chapter**

**Buổi 18 — Plugin Parser**

```text
Crawler
   ↓
Parser Interface
   ├── SiteAParser
   ├── SiteBParser
   └── SiteCParser
```

**Buổi 19 — Selectolax + Asyncio**

**Buổi 20 — Final Project**

Xây dựng một **production-style crawler framework** sử dụng:

```text
httpx
selectolax
asyncio
sqlite3
repository pattern
clean architecture
plugin architecture
```

---

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
