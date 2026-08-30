# 📘 Selectolax — Buổi 2: CSS Selector

Nếu **Buổi 1** giúp bạn hiểu cách parse HTML và lấy Node, thì **Buổi 2** là phần quan trọng nhất để sử dụng Selectolax trong scraping:

> **CSS Selector chính là ngôn ngữ để nói cho Selectolax biết: "Tôi muốn lấy element nào?"**

---

# 1. Tư duy tổng quát

Giả sử HTML:

```html
<div class="article">
    <h2 class="title">Python</h2>
    <p class="description">Learn Python</p>
</div>
```

Ta có:

```text
HTML
 │
 └── div.article
      │
      ├── h2.title
      │
      └── p.description
```

Selectolax:

```python
tree.css_first("h2.title")
```

có nghĩa:

> Tìm `h2` có class `title`.

---

# 2. Tag Selector

Selector cơ bản nhất:

```python
tree.css_first("h1")
```

Lấy:

```html
<h1>Hello</h1>
```

Các ví dụ:

```python
tree.css_first("h1")
tree.css_first("p")
tree.css_first("article")
tree.css_first("div")
```

Nếu muốn lấy tất cả:

```python
tree.css("p")
```

---

# 3. Class Selector

HTML:

```html
<p class="title">Hello</p>
```

Selector:

```python
tree.css_first(".title")
```

Dấu `.` có nghĩa là **class**.

Ví dụ:

```html
<div class="article">...</div>
<div class="article">...</div>
<div class="sidebar">...</div>
```

Lấy tất cả article:

```python
articles = tree.css(".article")
```

---

# 4. ID Selector

HTML:

```html
<div id="content">
    ...
</div>
```

Selector:

```python
tree.css_first("#content")
```

Dấu `#` nghĩa là **id**.

Ví dụ:

```html
<div id="main">
    <h1>Hello</h1>
</div>
```

```python
main = tree.css_first("#main")
```

---

# 5. Tag + Class

HTML:

```html
<article class="story">
    ...
</article>
```

Có thể dùng:

```python
tree.css_first("article.story")
```

Khác với:

```python
tree.css_first(".story")
```

### Khi nào nên dùng `article.story`?

Khi muốn selector chính xác hơn.

Ví dụ:

```html
<div class="story">A</div>

<article class="story">B</article>
```

Nếu:

```python
tree.css(".story")
```

kết quả:

```text
A
B
```

Nhưng:

```python
tree.css("article.story")
```

chỉ lấy:

```text
B
```

---

# 6. Nhiều class

HTML:

```html
<article class="story featured">
    Python
</article>
```

Có thể chọn:

```python
tree.css_first(".story.featured")
```

Chú ý:

```css
.story.featured
```

không có khoảng trắng.

Nó nghĩa là:

> element vừa có `story` vừa có `featured`.

---

# 7. Descendant Selector

Đây là selector cực kỳ quan trọng khi crawl.

HTML:

```html
<div class="article">
    <h2>Python</h2>
</div>
```

Ta có thể:

```python
tree.css_first(".article h2")
```

Nghĩa là:

> tìm `h2` nằm bên trong `.article`.

---

Ví dụ:

```html
<div class="article">
    <div class="header">
        <h2>Python</h2>
    </div>
</div>
```

Selector:

```python
tree.css_first(".article h2")
```

vẫn tìm được:

```text
Python
```

Không quan trọng `h2` nằm sâu bao nhiêu cấp.

---

# 8. Child Selector `>`

Khác với descendant.

HTML:

```html
<div class="article">
    <h2>Python</h2>
</div>
```

Dùng:

```python
tree.css_first(".article > h2")
```

Nghĩa là:

> `h2` phải là **con trực tiếp** của `.article`.

---

Ví dụ:

```html
<div class="article">
    <div class="header">
        <h2>Python</h2>
    </div>
</div>
```

Selector:

```python
tree.css_first(".article > h2")
```

sẽ **không tìm thấy**.

Nhưng:

```python
tree.css_first(".article h2")
```

thì tìm thấy.

### Nhớ:

```text
.article h2
     ↓
con cháu ở bất kỳ cấp nào

.article > h2
     ↓
con trực tiếp
```

---

# 9. Attribute Selector

Đây là kỹ năng cực kỳ hữu ích khi crawl website.

HTML:

```html
<a href="/python">Python</a>
<a href="/rust">Rust</a>
```

Lấy tất cả `a` có `href`:

```python
tree.css("a[href]")
```

---

# 10. Attribute bằng giá trị

```html
<input type="text">
<input type="password">
<input type="email">
```

Lấy input text:

```python
tree.css_first('input[type="text"]')
```

Lấy:

```html
<a href="/python">Python</a>
```

bằng:

```python
tree.css_first('a[href="/python"]')
```

---

# 11. Attribute bắt đầu bằng

Ví dụ:

```html
<a href="/chapter/1">Chapter 1</a>
<a href="/chapter/2">Chapter 2</a>
<a href="/story/abc">Story</a>
```

Ta có:

```python
tree.css('a[href^="/chapter/"]')
```

`^=` nghĩa là:

> bắt đầu bằng

Kết quả:

```text
Chapter 1
Chapter 2
```

---

# 12. Attribute kết thúc bằng

Ví dụ:

```html
<img src="cover.jpg">
<img src="avatar.png">
<img src="banner.jpg">
```

Lấy ảnh `.jpg`:

```python
tree.css('img[src$=".jpg"]')
```

`$=` nghĩa là:

> kết thúc bằng

---

# 13. Attribute chứa chuỗi

HTML:

```html
<a href="/story/python">
<a href="/story/rust">
<a href="/category/python">
```

Selector:

```python
tree.css('a[href*="/story/"]')
```

`*=` nghĩa là:

> attribute có chứa chuỗi.

Kết quả:

```text
/story/python
/story/rust
```

---

# 14. Selector nhiều điều kiện

Ví dụ:

```html
<article class="story featured">
    <h2>Python</h2>
</article>
```

Ta có:

```python
tree.css_first("article.story.featured")
```

Hoặc:

```python
tree.css_first("article.story h2")
```

Hoặc:

```python
tree.css_first('article[data-type="story"]')
```

---

# 15. `:first-child`

HTML:

```html
<div class="items">
    <p>One</p>
    <p>Two</p>
    <p>Three</p>
</div>
```

Lấy paragraph đầu:

```python
tree.css_first(".items p:first-child")
```

---

# 16. `:last-child`

```python
tree.css_first(".items p:last-child")
```

Lấy:

```text
Three
```

---

# 17. `:nth-child()`

```python
tree.css_first(".items p:nth-child(2)")
```

Lấy:

```text
Two
```

Ví dụ:

```python
tree.css(".items p:nth-child(odd)")
```

hoặc:

```python
tree.css(".items p:nth-child(even)")
```

---

# 18. Multiple Selector

Có thể truyền nhiều selector:

```python
tree.css("h1, h2, h3")
```

Nghĩa là:

> lấy tất cả `h1`, `h2`, `h3`.

Ví dụ:

```html
<h1>Title</h1>
<h2>Chapter 1</h2>
<p>Text</p>
<h2>Chapter 2</h2>
```

```python
nodes = tree.css("h1, h2")
```

Kết quả:

```text
Title
Chapter 1
Chapter 2
```

---

# 19. Ví dụ thực tế: website truyện

Đây là phần đặc biệt phù hợp với project crawler của bạn.

Giả sử HTML:

```html
<div class="story">
    <h1 class="story-title">
        Đấu Phá Thương Khung
    </h1>

    <div class="story-info">
        <a class="author" href="/author/thien-tam-tho-dau">
            Thiên Tằm Thổ Đậu
        </a>
    </div>

    <div class="chapters">
        <div class="chapter">
            <a href="/chuong-1">Chương 1</a>
        </div>

        <div class="chapter">
            <a href="/chuong-2">Chương 2</a>
        </div>

        <div class="chapter">
            <a href="/chuong-3">Chương 3</a>
        </div>
    </div>
</div>
```

Lấy title:

```python
title = tree.css_first(".story-title")

print(title.text())
```

Lấy author:

```python
author = tree.css_first(".story-info .author")

print(author.text())
```

Lấy tất cả chapter:

```python
chapters = tree.css(".chapters .chapter a")

for chapter in chapters:
    print(chapter.text())
```

Kết quả:

```text
Chương 1
Chương 2
Chương 3
```

---

# 20. Lấy URL

Một trong những công việc quan trọng nhất của crawler là lấy `href`.

```python
chapter = tree.css_first(".chapter a")

print(chapter.attributes["href"])
```

Kết quả:

```text
/chuong-1
```

Đây là pattern bạn sẽ dùng liên tục:

```python
node = tree.css_first("a")

text = node.text()
url = node.attributes["href"]
```

---

# 21. Kết hợp CSS Selector + attribute

Ví dụ muốn lấy tất cả chapter link:

```python
chapters = tree.css('a[href^="/chuong-"]')
```

Sau đó:

```python
for chapter in chapters:
    title = chapter.text()
    url = chapter.attributes["href"]

    print(title, url)
```

Kết quả:

```text
Chương 1 /chuong-1
Chương 2 /chuong-2
Chương 3 /chuong-3
```

Đây là một kỹ thuật **rất thực tế** khi xây crawler.

---

# 22. Selector tương đối trên Node

Đây là một điểm rất quan trọng.

Không nhất thiết phải luôn:

```python
tree.css(...)
```

Ta có thể lấy một Node trước:

```python
article = tree.css_first(".article")
```

Sau đó tìm bên trong Node:

```python
title = article.css_first("h2")
description = article.css_first("p")
```

Tư duy:

```text
tree
 │
 └── article
      │
      ├── h2
      └── p
```

Thay vì:

```python
tree.css_first(".article h2")
tree.css_first(".article p")
```

ta có:

```python
article.css_first("h2")
article.css_first("p")
```

Điều này đặc biệt hữu ích khi xử lý **nhiều item**.

---

# 23. Pattern quan trọng nhất của Scraper

Ví dụ:

```html
<div class="books">

    <article class="book">
        <h2>Python</h2>
        <p>Python programming</p>
    </article>

    <article class="book">
        <h2>Rust</h2>
        <p>Rust programming</p>
    </article>

</div>
```

Code:

```python
books = tree.css("article.book")

for book in books:
    title = book.css_first("h2")
    description = book.css_first("p")

    print(title.text())
    print(description.text())
```

Đây chính là cấu trúc:

```text
Select collection
        ↓
      Loop
        ↓
   Select child
        ↓
   Extract data
```

Bạn nên **ghi nhớ pattern này**, vì sau này khi xây `StoryParser`, `ChapterParser`, `ArticleParser`, bạn sẽ sử dụng nó rất nhiều.

---

# 24. Một nguyên tắc rất quan trọng khi viết Selector

Không nên cố viết selector quá dài:

```python
tree.css_first(
    "html body div.container div.content div.story div.header h1.title"
)
```

Selector này rất dễ vỡ khi website thay đổi HTML.

Tốt hơn:

```python
tree.css_first("h1.title")
```

hoặc:

```python
tree.css_first(".story h1.title")
```

### Nguyên tắc:

> **Selector càng ngắn nhưng vẫn đủ chính xác thì càng tốt.**

---

# 25. Bài tập Buổi 2

Cho HTML:

```html
<div class="stories">

    <article class="story featured" data-type="novel">
        <h2 class="title">Python Mastery</h2>

        <div class="info">
            <a class="author" href="/authors/alice">
                Alice
            </a>
        </div>

        <div class="chapters">
            <a href="/python/1">Chapter 1</a>
            <a href="/python/2">Chapter 2</a>
        </div>
    </article>

    <article class="story" data-type="novel">
        <h2 class="title">Rust Mastery</h2>

        <div class="info">
            <a class="author" href="/authors/bob">
                Bob
            </a>
        </div>

        <div class="chapters">
            <a href="/rust/1">Chapter 1</a>
            <a href="/rust/2">Chapter 2</a>
        </div>
    </article>

</div>
```

### Bài 1

Lấy tất cả story.

### Bài 2

Lấy story có:

```text
featured
```

### Bài 3

Lấy title của tất cả story.

### Bài 4

Lấy author của tất cả story.

### Bài 5

Lấy `href` của tất cả chapter.

Kết quả mong muốn:

```text
/python/1
/python/2
/rust/1
/rust/2
```

### Bài 6 — Quan trọng

Viết:

```python
def parse_stories(html: str) -> list[dict]:
    ...
```

Kết quả:

```python
[
    {
        "title": "Python Mastery",
        "author": "Alice",
        "author_url": "/authors/alice",
        "chapters": [
            {
                "title": "Chapter 1",
                "url": "/python/1",
            },
            {
                "title": "Chapter 2",
                "url": "/python/2",
            },
        ],
    },
    ...
]
```

---

## 🎯 Sau Buổi 2 bạn cần nắm chắc

```text
tag              h1
class            .title
id               #content

descendant       .story h2
child            .story > h2

attribute        a[href]
attribute =      a[href="/python"]
starts with      a[href^="/chapter/"]
ends with        img[src$=".jpg"]
contains         a[href*="/story/"]

first child      :first-child
last child       :last-child
nth child        :nth-child(2)

multiple         h1, h2, h3
```

Và quan trọng nhất:

```python
nodes = tree.css("article.story")

for node in nodes:
    title = node.css_first("h2.title")
    author = node.css_first(".author")
```

**Buổi 3** sẽ đi sâu vào **Selectolax Node & DOM Traversal**: `parent`, `child`, `iter()`, `next`, `prev`, `attributes`, `tag`, `html`, `text()` và cách duyệt DOM **không phụ thuộc quá nhiều vào CSS selector**.
