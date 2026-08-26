
# 📘 Selectolax — Buổi 3: Node & DOM Traversal

Ở Buổi 1 và 2, chúng ta chủ yếu làm:

```text
HTML
 ↓
HTMLParser
 ↓
CSS Selector
 ↓
Node
 ↓
text / attribute
```

Hôm nay chúng ta đi sâu vào **Node**.

Đây là phần rất quan trọng nếu bạn muốn sau này tự xây:

* `StoryParser`
* `ChapterParser`
* `ArticleExtractor`
* HTML cleaner
* crawler framework

---

# 1. Node là gì?

Khi viết:

```python
from selectolax.parser import HTMLParser

html = """
<div class="article">
    <h1>Python</h1>
    <p>Hello World</p>
</div>
"""

tree = HTMLParser(html)
```

`tree` đại diện cho DOM.

Ta có thể lấy một Node:

```python
article = tree.css_first(".article")
```

Lúc này:

```text
article
   │
   ├── h1
   │    └── Python
   │
   └── p
        └── Hello World
```

`article` là một **Node**.

---

# 2. `tag`

Node biết nó là HTML element nào.

```python
article.tag
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

# 3. `attributes`

Đây là một thuộc tính cực kỳ quan trọng khi scraping.

HTML:

```html
<a
    class="chapter"
    href="/chapter/1"
    title="Chapter 1"
>
    Chapter 1
</a>
```

Lấy Node:

```python
chapter = tree.css_first("a.chapter")
```

Sau đó:

```python
print(chapter.attributes)
```

Bạn có thể truy cập:

```python
chapter.attributes["href"]
```

Kết quả:

```text
/chapter/1
```

Hoặc:

```python
chapter.attributes["title"]
```

Kết quả:

```text
Chapter 1
```

---

# 4. Kiểm tra attribute

Không phải attribute nào cũng tồn tại.

Không nên:

```python
url = node.attributes["href"]
```

nếu chưa chắc Node có `href`.

An toàn hơn:

```python
url = node.attributes.get("href")
```

Nếu không tồn tại:

```python
None
```

Đây là pattern rất hữu ích:

```python
href = node.attributes.get("href")
title = node.attributes.get("title")
class_name = node.attributes.get("class")
```

---

# 5. `.text()`

Ví dụ:

```html
<h1>Python Programming</h1>
```

```python
node = tree.css_first("h1")

print(node.text())
```

Kết quả:

```text
Python Programming
```

---

# 6. Text của Node chứa Node con

HTML:

```html
<div class="article">
    <h1>Python</h1>
    <p>Hello <strong>World</strong></p>
</div>
```

Nếu:

```python
article = tree.css_first(".article")
```

thì:

```python
print(article.text())
```

sẽ lấy text bên trong toàn bộ subtree.

Tức là:

```text
Python
Hello World
```

---

# 7. `.html`

Node cũng có thể lấy HTML bên trong.

Ví dụ:

```html
<div class="article">
    <h1>Python</h1>
    <p>Hello</p>
</div>
```

```python
article = tree.css_first(".article")

print(article.html)
```

Kết quả về cơ bản là HTML của các node con:

```html
<h1>Python</h1>
<p>Hello</p>
```

Điểm quan trọng:

```text
.text()
    → text

.html
    → inner HTML
```

---

# 8. DOM Traversal

Đây là phần chính của buổi hôm nay.

Thay vì:

```python
tree.css_first(...)
```

ta có thể di chuyển trong DOM:

```text
parent
children
next
prev
```

Ví dụ:

```html
<div class="article">
    <h1>Python</h1>
    <p>Hello</p>
    <p>World</p>
</div>
```

Cây:

```text
div.article
│
├── h1
│
├── p
│
└── p
```

---

# 9. `parent`

Giả sử lấy:

```python
title = tree.css_first("h1")
```

Ta có thể đi lên:

```python
parent = title.parent
```

Tức:

```text
h1
 ↑
div.article
```

Ví dụ:

```python
print(title.parent.tag)
```

Kết quả:

```text
div
```

---

# 10. `parent` rất hữu ích khi crawl

Giả sử HTML:

```html
<article class="story">
    <h2>Python</h2>

    <div class="info">
        <span>Alice</span>
    </div>
</article>
```

Ta lấy:

```python
title = tree.css_first("h2")
```

Sau đó:

```python
story = title.parent
```

Có thể từ `story` lấy tiếp:

```python
author = story.css_first(".info span")
```

Tư duy:

```text
h2
 ↑
article
 │
 └── .info
       │
       └── span
```

---

# 11. `iter_children()`

Giả sử:

```html
<div class="article">
    <h1>Python</h1>
    <p>Hello</p>
    <p>World</p>
</div>
```

Ta lấy:

```python
article = tree.css_first(".article")
```

Sau đó:

```python
for child in article.iter_children():
    print(child.tag)
```

Kết quả:

```text
h1
p
p
```

Đây là **children trực tiếp**.

---

# 12. Children vs Descendants

Điểm này rất quan trọng.

HTML:

```html
<div>
    <section>
        <h1>Python</h1>
    </section>
</div>
```

Cây:

```text
div
└── section
    └── h1
```

`div` có child trực tiếp:

```text
section
```

Nhưng `h1` là **descendant**.

Do đó:

```text
children
    ↓
con trực tiếp

descendants
    ↓
toàn bộ cây con
```

---

# 13. `iter()`

Selectolax cho phép duyệt subtree.

Ví dụ:

```python
article = tree.css_first(".article")

for node in article.iter():
    print(node.tag)
```

Bạn có thể duyệt toàn bộ Node và các Node con của nó.

Đây là kỹ thuật rất hữu ích khi muốn:

* tìm tất cả element
* HTML cleaning
* duyệt nội dung article
* xử lý `p`, `img`, `a`, `br`
* loại bỏ tag

---

# 14. `next`

Giả sử:

```html
<div>
    <h2>Title</h2>
    <p>Paragraph 1</p>
    <p>Paragraph 2</p>
</div>
```

Nếu:

```python
title = tree.css_first("h2")
```

thì node kế tiếp trong DOM có thể được truy cập qua:

```python
title.next
```

Tư duy:

```text
h2
 ↓
p
 ↓
p
```

---

# 15. `prev`

Ngược lại:

```python
paragraph = tree.css_first("p")

previous = paragraph.prev
```

Tư duy:

```text
h2
 ↓
p
 ↓
p
```

Từ `p` thứ nhất:

```text
prev → h2
next → p thứ hai
```

---

# 16. `next` và `prev` dùng khi nào?

Trong scraping hiện đại, bạn thường ưu tiên:

```python
node.css_first(...)
```

vì dễ đọc hơn.

Nhưng `next` / `prev` rất hữu ích khi HTML có cấu trúc kiểu:

```html
<h2>Chapter 1</h2>
<div>Content...</div>

<h2>Chapter 2</h2>
<div>Content...</div>
```

Hoặc:

```html
<label>Author</label>
<span>Alice</span>
```

Có thể tìm node liên quan dựa trên vị trí DOM.

---

# 17. `iter_children()` vs `iter()`

Hãy nhớ:

### `iter_children()`

```python
for node in article.iter_children():
    ...
```

Chỉ duyệt:

```text
con trực tiếp
```

### `iter()`

```python
for node in article.iter():
    ...
```

Duyệt:

```text
node
 └── toàn bộ descendants
```

---

# 18. Ví dụ thực tế: phân tích article

HTML:

```python
html = """
<article class="story">
    <h1>Python</h1>

    <div class="content">
        <p>Hello</p>
        <p>Learning Selectolax</p>

        <strong>Important</strong>
    </div>
</article>
"""
```

Lấy article:

```python
tree = HTMLParser(html)

article = tree.css_first("article.story")
```

Duyệt toàn bộ:

```python
for node in article.iter():
    print(node.tag)
```

Ta sẽ nhìn thấy cấu trúc DOM.

Ví dụ:

```text
article
h1
div
p
p
strong
```

Đây là kỹ thuật rất hữu ích để **debug HTML structure**.

---

# 19. Debug DOM

Khi crawler không lấy được dữ liệu, đừng ngay lập tức viết selector phức tạp.

Hãy debug:

```python
article = tree.css_first(".article")

for node in article.iter():
    print(
        node.tag,
        node.attributes
    )
```

Bạn có thể thấy:

```text
article {'class': 'article'}
h1 {'class': 'title'}
p {'class': 'description'}
a {'href': '/chapter/1'}
```

Sau đó mới quyết định selector.

Đây là workflow rất tốt:

```text
HTML
 ↓
Inspect DOM
 ↓
Understand structure
 ↓
Write selector
 ↓
Extract
```

---

# 20. Xây một DOM inspector nhỏ

Bạn có thể viết:

```python
from selectolax.parser import HTMLParser


def inspect_html(html: str) -> None:
    tree = HTMLParser(html)

    for node in tree.root.iter():
        print(
            f"tag={node.tag!r}, "
            f"attrs={node.attributes}"
        )
```

Ví dụ:

```python
html = """
<div class="article">
    <h1 class="title">Python</h1>
    <a href="/chapter/1">Chapter 1</a>
</div>
"""

inspect_html(html)
```

Khi làm crawler thực tế, một utility kiểu này rất hữu ích.

---

# 21. Node và CSS Selector kết hợp

Đây là pattern mình muốn bạn sử dụng từ bây giờ.

Thay vì:

```python
tree.css_first(".story h2")
tree.css_first(".story .author")
tree.css_first(".story .chapters")
```

hãy:

```python
story = tree.css_first(".story")

title = story.css_first("h2")
author = story.css_first(".author")
chapters = story.css(".chapter")
```

Tức:

```text
Tree
 ↓
Container Node
 ↓
Query bên trong Node
```

Điều này làm code parser rõ ràng hơn.

---

# 22. Ví dụ `parse_story()`

```python
from selectolax.parser import HTMLParser


def parse_story(html: str) -> dict:
    tree = HTMLParser(html)

    story = tree.css_first("article.story")

    if story is None:
        raise ValueError("Story not found")

    title = story.css_first("h2.title")
    author = story.css_first(".author")

    return {
        "title": title.text() if title else None,
        "author": author.text() if author else None,
    }
```

Đây bắt đầu giống một parser thực tế.

---

# 23. Node không phải là string

Đây là lỗi người mới rất hay gặp.

Sai:

```python
title = tree.css_first("h1")

if title == "Python":
    ...
```

`title` là **Node**, không phải string.

Đúng:

```python
if title.text() == "Python":
    ...
```

Tư duy:

```text
Node
 ↓
.text()
 ↓
str
```

---

# 24. Node không phải dictionary

Tương tự:

```python
node["href"]
```

không phải cách phù hợp.

Dùng:

```python
node.attributes["href"]
```

hoặc an toàn hơn:

```python
node.attributes.get("href")
```

---

# 25. Một parser hoàn chỉnh hơn

Giả sử:

```html
<article class="story">
    <h2 class="title">Python Mastery</h2>

    <a class="author" href="/author/alice">
        Alice
    </a>

    <div class="chapters">
        <a href="/chapter/1">Chapter 1</a>
        <a href="/chapter/2">Chapter 2</a>
    </div>
</article>
```

Code:

```python
from selectolax.parser import HTMLParser


def parse_story(html: str) -> dict:
    tree = HTMLParser(html)

    story = tree.css_first("article.story")

    if story is None:
        raise ValueError("Story not found")

    title_node = story.css_first("h2.title")
    author_node = story.css_first("a.author")

    chapters = []

    for node in story.css(".chapters a"):
        chapters.append({
            "title": node.text(strip=True),
            "url": node.attributes.get("href"),
        })

    return {
        "title": title_node.text(strip=True) if title_node else None,
        "author": author_node.text(strip=True) if author_node else None,
        "chapters": chapters,
    }
```

Đây là một parser có cấu trúc khá tốt.

---

# 26. Một pattern cực kỳ quan trọng

Khi crawl danh sách:

```python
stories = tree.css("article.story")
```

Sau đó:

```python
for story in stories:
    title = story.css_first("h2.title")
    author = story.css_first(".author")
```

Tức là:

```text
HTMLParser
     │
     ▼
Collection
     │
     ▼
   Node
     │
     ├── child
     ├── descendant
     ├── attribute
     └── text
```

Đây là tư duy bạn cần hình thành khi sử dụng Selectolax.

---

# 27. Bài tập Buổi 3

Cho HTML:

```python
html = """
<div class="story">
    <h1 class="title">Python Mastery</h1>

    <div class="meta">
        <span class="author">Alice</span>
        <span class="category">Programming</span>
    </div>

    <div class="content">
        <p>Python is powerful.</p>
        <p>Selectolax is fast.</p>
    </div>

    <div class="chapters">
        <a href="/chapter/1">Chapter 1</a>
        <a href="/chapter/2">Chapter 2</a>
        <a href="/chapter/3">Chapter 3</a>
    </div>
</div>
"""
```

### Bài 1

Lấy:

```text
story
```

sau đó in:

```text
story.tag
story.attributes
```

---

### Bài 2

Từ `story`, lấy:

```text
title
author
category
```

---

### Bài 3

Dùng `iter_children()` để in:

```text
h1
div
div
div
```

---

### Bài 4

Dùng `iter()` để in toàn bộ tag trong story.

Bạn sẽ thấy đại khái:

```text
div
h1
div
span
span
div
p
p
div
a
a
a
```

---

### Bài 5

Lấy tất cả chapter bằng Node `story`:

```python
chapters = story.css(...)
```

Sau đó in:

```text
Chapter 1 -> /chapter/1
Chapter 2 -> /chapter/2
Chapter 3 -> /chapter/3
```

---

### Bài 6 — Thực hành quan trọng

Viết:

```python
def parse_story(html: str) -> dict:
    ...
```

Kết quả:

```python
{
    "title": "Python Mastery",
    "author": "Alice",
    "category": "Programming",
    "content": [
        "Python is powerful.",
        "Selectolax is fast.",
    ],
    "chapters": [
        {
            "title": "Chapter 1",
            "url": "/chapter/1",
        },
        {
            "title": "Chapter 2",
            "url": "/chapter/2",
        },
        {
            "title": "Chapter 3",
            "url": "/chapter/3",
        },
    ],
}
```

---

# 🧠 Tổng kết Buổi 3

Bạn cần nắm được mô hình:

```text
                     HTMLParser
                         │
                         ▼
                        Node
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   Attributes          Text             HTML
       │
       ▼
   attributes

                         Node
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
        parent         children       siblings
                          │
                   ┌──────┴──────┐
                   ▼             ▼
            iter_children()     iter()
```

Và pattern quan trọng nhất:

```python
items = tree.css("article.story")

for item in items:
    title = item.css_first("h2.title")
    author = item.css_first(".author")
```

**Buổi 4** chúng ta sẽ chuyển sang **Extract dữ liệu thực chiến**: text, attribute, link, image, xử lý `None`, normalize text và xây dựng các hàm `extract_text()`, `extract_attr()`, `extract_url()` để parser không bị vỡ khi HTML thiếu dữ liệu.
