# 📘 Selectolax — Buổi 3: Node & DOM Traversal

Ở **Buổi 1**, bạn học parse HTML và lấy Node.
Ở **Buổi 2**, bạn học CSS Selector.

Hôm nay chúng ta học một phần rất quan trọng khi xây scraper thực tế:

> **Sau khi lấy được một Node, làm thế nào để đi lên, đi xuống, sang trái, sang phải trong cây DOM?**

Đây gọi là **DOM Traversal**.

---

# 1. DOM là một cây

HTML:

```html
<div class="article">
    <h1>Python</h1>

    <div class="content">
        <p>Hello</p>
        <p>World</p>
    </div>
</div>
```

Có thể hình dung:

```text
div.article
│
├── h1
│
└── div.content
    │
    ├── p
    │
    └── p
```

Mỗi element trong cây này là một **Node**.

Selectolax cho phép chúng ta di chuyển giữa các Node:

```text
              parent
                ↑
                │
previous ←── Node ──→ next
                │
                ↓
              child
```

---

# 2. Tạo Node

Bắt đầu:

```python
from selectolax.parser import HTMLParser


html = """
<div class="article">
    <h1>Python</h1>
    <div class="content">
        <p>Hello</p>
        <p>World</p>
    </div>
</div>
"""

tree = HTMLParser(html)

article = tree.css_first(".article")
```

`article` là một Node.

---

# 3. `node.tag`

Lấy tên HTML tag:

```python
print(article.tag)
```

Kết quả:

```text
div
```

Ví dụ:

```python
title = tree.css_first("h1")

print(title.tag)
```

Kết quả:

```text
h1
```

---

# 4. `node.text()`

Lấy text của Node:

```python
title = tree.css_first("h1")

print(title.text())
```

Kết quả:

```text
Python
```

Với Node chứa nhiều element:

```python
article = tree.css_first(".article")

print(article.text())
```

Có thể nhận được text của toàn bộ subtree:

```text
Python
Hello
World
```

---

# 5. `node.html`

Lấy HTML bên trong Node.

```python
content = tree.css_first(".content")

print(content.html)
```

Kết quả tương tự:

```html
<p>Hello</p>
<p>World</p>
```

Điểm cần nhớ:

```text
node.text()
    → text bên trong

node.html
    → inner HTML
```

---

# 6. `node.attributes`

Đây là phần rất quan trọng khi crawl.

HTML:

```html
<a
    class="chapter"
    href="/chapter-1"
    data-id="100"
>
    Chapter 1
</a>
```

Lấy Node:

```python
chapter = tree.css_first("a.chapter")
```

Xem attributes:

```python
print(chapter.attributes)
```

Ta có dictionary-like object chứa:

```text
class
href
data-id
```

---

# 7. Lấy một attribute

```python
href = chapter.attributes["href"]

print(href)
```

Kết quả:

```text
/chapter-1
```

Hoặc:

```python
chapter_id = chapter.attributes["data-id"]

print(chapter_id)
```

Kết quả:

```text
100
```

Đây là pattern bạn sẽ sử dụng cực kỳ nhiều:

```python
url = node.attributes["href"]
```

---

# 8. Cẩn thận với attribute không tồn tại

Ví dụ:

```python
node.attributes["data-id"]
```

nhưng HTML không có `data-id`.

Có thể xảy ra lỗi.

Trong scraper nên defensive:

```python
data_id = node.attributes.get("data-id")
```

Nếu không tồn tại:

```text
None
```

Đây là cách an toàn hơn.

---

# 9. `parent`

Giả sử:

```html
<div class="article">
    <h1>Python</h1>
</div>
```

Ta lấy:

```python
title = tree.css_first("h1")
```

Sau đó:

```python
parent = title.parent
```

`parent` chính là:

```html
<div class="article">
```

Ta có:

```python
print(parent.tag)
```

Kết quả:

```text
div
```

---

# 10. Đi lên nhiều cấp

Ví dụ:

```html
<div class="article">
    <div class="header">
        <h1>Python</h1>
    </div>
</div>
```

Ta có:

```python
title = tree.css_first("h1")

header = title.parent
article = header.parent
```

Sơ đồ:

```text
article
   ↑
header
   ↑
 h1
```

Đây là DOM traversal từ **child → parent**.

---

# 11. `child`

Một Node có thể có các Node con.

Ví dụ:

```html
<div class="article">
    <h1>Python</h1>
    <p>Hello</p>
</div>
```

Ta có thể truy cập children của `article`.

Trong Selectolax, các API traversal có thể khác nhau tùy phiên bản parser/backend, vì vậy khi viết code production bạn nên ưu tiên các phương thức traversal được phiên bản Selectolax của mình hỗ trợ và kiểm tra API tương ứng.

Một pattern rất hữu ích là:

```python
for child in node.iter_children():
    print(child.tag)
```

---

# 12. `iter_children()`

Ví dụ:

```python
html = """
<div class="article">
    <h1>Python</h1>
    <p>Hello</p>
    <p>World</p>
</div>
"""

tree = HTMLParser(html)

article = tree.css_first(".article")

for child in article.iter_children():
    print(child.tag)
```

Ta sẽ duyệt các Node con trực tiếp.

Tư duy:

```text
article
│
├── h1
├── p
└── p
```

`iter_children()` chỉ đi **một cấp**.

---

# 13. `iter()`

`iter()` mạnh hơn.

Nó cho phép duyệt các Node trong subtree.

Ví dụ:

```python
for node in article.iter():
    print(node.tag)
```

Có thể hình dung:

```text
article
 ↓
h1
 ↓
content
 ↓
p
 ↓
p
```

Đây là cách hữu ích khi bạn muốn **duyệt toàn bộ DOM subtree**.

---

# 14. So sánh `iter_children()` và `iter()`

### `iter_children()`

```python
for node in article.iter_children():
    ...
```

Duyệt:

```text
article
├── h1
├── div
└── p
```

Chỉ **con trực tiếp**.

### `iter()`

```python
for node in article.iter():
    ...
```

Duyệt sâu hơn trong subtree.

```text
article
├── h1
└── div
    ├── p
    └── span
```

---

# 15. `next`

Đây là khái niệm rất hữu ích.

HTML:

```html
<div>
    <p>One</p>
    <p>Two</p>
    <p>Three</p>
</div>
```

Nếu đang đứng ở:

```python
one = tree.css_first("p")
```

Ta có thể đi tới Node kế tiếp bằng API traversal tương ứng của Node.

Khái niệm:

```text
p One
  │
  ↓
p Two
  │
  ↓
p Three
```

Tuy nhiên, khi crawl website, **đừng mặc định rằng "next" luôn là element kế tiếp mà bạn nhìn thấy trong HTML**. DOM có thể chứa text/comment nodes và behavior có thể phụ thuộc backend/version.

Đây là lý do trong nhiều scraper, CSS selector hoặc `iter_children()` thường dễ kiểm soát hơn.

---

# 16. Previous / Previous sibling

Tương tự:

```text
p One
  ↑
p Two
  ↑
p Three
```

Khi đang ở `Three`, ta có thể traversal ngược về Node trước đó.

Tư duy quan trọng:

```text
parent
   ↑
previous ← current → next
   ↓
 children
```

Đây chính là mô hình DOM traversal.

---

# 17. Khi nào dùng CSS Selector?

Ví dụ:

```python
title = article.css_first("h2.title")
```

Đây là cách **declarative**:

> Tôi muốn Node phù hợp với selector này.

Rất phù hợp khi HTML có cấu trúc ổn định.

---

# 18. Khi nào dùng DOM Traversal?

Ví dụ HTML:

```html
<div class="info">
    <span>Author:</span>
    <strong>Alice</strong>
</div>
```

Bạn có thể lấy:

```python
info = tree.css_first(".info")
```

sau đó traversal trong Node.

Đặc biệt hữu ích khi:

* HTML không có class rõ ràng
* Website dùng class động
* Muốn xử lý cấu trúc tương đối
* Muốn viết parser generic
* Muốn tìm element dựa vào vị trí trong DOM

---

# 19. Ví dụ thực tế: tìm dữ liệu theo cấu trúc

HTML:

```html
<div class="book">
    <div class="metadata">
        <span>Tác giả:</span>
        <strong>Nguyễn Văn A</strong>
    </div>
</div>
```

Ta lấy:

```python
metadata = tree.css_first(".metadata")
```

Sau đó:

```python
children = list(metadata.iter_children())

for child in children:
    print(child.tag)
```

Có thể thấy:

```text
span
strong
```

Ta có thể xử lý cấu trúc:

```text
metadata
│
├── label
└── value
```

Thay vì phụ thuộc vào:

```python
.metadata strong
```

---

# 20. Một kỹ thuật rất quan trọng: Node làm "scope"

Giả sử có 100 bài viết:

```html
<article class="story">
    <h2>Story 1</h2>
</article>

<article class="story">
    <h2>Story 2</h2>
</article>

<article class="story">
    <h2>Story 3</h2>
</article>
```

Ta làm:

```python
stories = tree.css("article.story")

for story in stories:
    title = story.css_first("h2")
    print(title.text())
```

Ở đây:

```text
tree
 │
 ├── story 1
 │    └── h2
 │
 ├── story 2
 │    └── h2
 │
 └── story 3
      └── h2
```

Mỗi `story` trở thành một **scope**.

Đây là pattern cực kỳ quan trọng:

```python
for item in tree.css(".item"):
    title = item.css_first(".title")
    author = item.css_first(".author")
    url = item.css_first("a")
```

Thay vì:

```python
tree.css(".title")
tree.css(".author")
tree.css("a")
```

Cách thứ hai dễ làm bạn **ghép nhầm dữ liệu giữa các item**.

---

# 21. Ví dụ lỗi rất phổ biến

HTML:

```html
<article class="story">
    <h2>Python</h2>
    <span>Alice</span>
</article>

<article class="story">
    <h2>Rust</h2>
    <span>Bob</span>
</article>
```

Sai:

```python
titles = tree.css("h2")
authors = tree.css("span")

for title, author in zip(titles, authors):
    print(title.text(), author.text())
```

Code này có thể hoạt động với HTML đơn giản, nhưng kiến trúc không tốt.

Tốt hơn:

```python
stories = tree.css("article.story")

for story in stories:
    title = story.css_first("h2")
    author = story.css_first("span")

    print(title.text(), author.text())
```

Ta giữ được **ngữ cảnh của từng article**.

---

# 22. `node.text(strip=True)`

Khi crawl website, HTML thường có whitespace:

```html
<h1>
    Python
</h1>
```

Bạn có thể muốn:

```text
Python
```

thay vì text có nhiều whitespace.

Tùy phiên bản Selectolax, API text có các tùy chọn xử lý whitespace khác nhau. Một cách an toàn là chuẩn hóa kết quả sau khi lấy:

```python
text = node.text().strip()
```

Ví dụ:

```python
title = node.text().strip()
```

---

# 23. Xây helper `get_text()`

Khi làm crawler lớn, bạn sẽ không muốn lặp:

```python
node = ...
if node:
    text = node.text().strip()
```

khắp nơi.

Có thể tạo:

```python
def get_text(node):
    if node is None:
        return None

    return node.text().strip()
```

Sau đó:

```python
title = get_text(article.css_first("h2.title"))
author = get_text(article.css_first(".author"))
```

Đây chính là bước đầu tiên để xây dựng **Extractor layer**.

---

# 24. Xây helper `get_attr()`

Tương tự:

```python
def get_attr(node, name):
    if node is None:
        return None

    return node.attributes.get(name)
```

Dùng:

```python
link = article.css_first("a")

url = get_attr(link, "href")
```

Bây giờ parser của bạn sạch hơn rất nhiều:

```python
title = get_text(article.css_first("h2"))
author = get_text(article.css_first(".author"))
url = get_attr(article.css_first("a"), "href")
```

---

# 25. Mini Parser

Hãy kết hợp tất cả:

```python
from selectolax.parser import HTMLParser


def get_text(node):
    if node is None:
        return None

    return node.text().strip()


def get_attr(node, name):
    if node is None:
        return None

    return node.attributes.get(name)


def parse_stories(html: str) -> list[dict]:
    tree = HTMLParser(html)

    stories = []

    for story in tree.css("article.story"):
        title = get_text(
            story.css_first("h2.title")
        )

        author_node = story.css_first(".author")

        author = get_text(author_node)
        author_url = get_attr(author_node, "href")

        stories.append({
            "title": title,
            "author": author,
            "author_url": author_url,
        })

    return stories
```

Đây đã bắt đầu giống một **parser thực tế**, chứ không còn chỉ là vài câu lệnh Selectolax.

---

# 26. Kiến trúc tư duy

Từ hôm nay bạn nên nhìn Selectolax theo 3 tầng:

```text
┌──────────────────────────────┐
│          HTMLParser          │
│                              │
│   HTML → DOM Tree            │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│            Node              │
│                              │
│ text                         │
│ html                         │
│ attributes                   │
│ parent                       │
│ children / traversal         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       CSS Selector           │
│                              │
│ .class                       │
│ #id                          │
│ tag                          │
│ attribute                    │
│ descendant                   │
│ child                        │
└──────────────────────────────┘
```

Trong scraper thực tế:

```text
HTML
 ↓
HTMLParser
 ↓
Node
 ↓
CSS Selector
 ↓
Node
 ↓
Traversal
 ↓
Extract
 ↓
Model
```

---

# 27. Khi nào CSS Selector, khi nào Traversal?

| Tình huống              | Nên dùng  |
| ----------------------- | --------- |
| Biết class rõ ràng      | CSS       |
| Biết id                 | CSS       |
| Biết attribute          | CSS       |
| Tìm nhiều item          | CSS       |
| Tìm Node con trong item | CSS       |
| Đi lên parent           | Traversal |
| Duyệt children          | Traversal |
| Duyệt toàn subtree      | `iter()`  |
| HTML cấu trúc phức tạp  | Kết hợp   |
| Parser generic          | Kết hợp   |

**Đừng chọn một trong hai.**

Parser tốt thường kết hợp:

```python
node = tree.css_first(".article")
```

sau đó:

```python
parent = node.parent
```

hoặc:

```python
for child in node.iter_children():
    ...
```

---

# 🧪 Bài tập Buổi 3

Cho HTML:

```html
<div class="stories">

    <article class="story">
        <div class="header">
            <h2>Python</h2>
            <a href="/python">Read</a>
        </div>

        <div class="content">
            <p>Python programming</p>
            <p>Advanced Python</p>
        </div>
    </article>

    <article class="story">
        <div class="header">
            <h2>Rust</h2>
            <a href="/rust">Read</a>
        </div>

        <div class="content">
            <p>Rust programming</p>
            <p>Advanced Rust</p>
        </div>
    </article>

</div>
```

### Bài 1

Lấy tất cả:

```text
article.story
```

---

### Bài 2

Với mỗi `article`, lấy:

```text
title
url
```

Kết quả:

```text
Python /python
Rust /rust
```

---

### Bài 3

Với mỗi article, duyệt toàn bộ Node bằng `iter()` và in:

```text
tag
```

---

### Bài 4

Với mỗi article, duyệt `iter_children()` và quan sát sự khác nhau giữa:

```text
iter()
```

và:

```text
iter_children()
```

---

### Bài 5 — Quan trọng

Viết:

```python
def parse_stories(html: str) -> list[dict]:
    ...
```

Kết quả:

```python
[
    {
        "title": "Python",
        "url": "/python",
        "paragraphs": [
            "Python programming",
            "Advanced Python",
        ],
    },
    {
        "title": "Rust",
        "url": "/rust",
        "paragraphs": [
            "Rust programming",
            "Advanced Rust",
        ],
    },
]
```

---

## 🎯 Sau Buổi 3 cần nhớ

Quan trọng nhất không phải thuộc lòng tất cả API, mà là hiểu mô hình:

```text
                    parent
                      ↑
                      │
previous ←───────── Node ─────────→ next
                      │
                      ↓
                  children
```

và pattern scraper:

```python
for item in tree.css("article.story"):
    title = item.css_first("h2")
    link = item.css_first("a")

    title_text = title.text().strip()
    url = link.attributes.get("href")
```

**Buổi 4** chúng ta sẽ chuyển sang phần rất thực dụng: **Extract dữ liệu với Selectolax** — text, HTML, attribute, link, image, xử lý `None`, chuẩn hóa dữ liệu và xây một `BaseExtractor` nhỏ để dùng lại trong các crawler sau này.
