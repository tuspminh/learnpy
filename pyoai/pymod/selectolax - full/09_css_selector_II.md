# 📘 Selectolax — Buổi 9: CSS Selector nâng cao

Ở Buổi 8, chúng ta đã dùng những selector cơ bản:

```python
tree.css_first("h1")
tree.css(".article-content")
tree.css_first(".author")
```

Hôm nay đi sâu vào **CSS Selector**, vì với scraper thực tế, khả năng chọn đúng node quan trọng không kém việc biết dùng Selectolax.

Mục tiêu:

```text
HTML
 ↓
CSS Selector
 ↓
đúng Node
 ↓
extract data
```

---

# 1. Ôn lại `css()` và `css_first()`

```python
tree.css("article")
```

→ trả về nhiều node.

```python
tree.css_first("article")
```

→ trả về node đầu tiên.

Ví dụ:

```html
<div class="post">A</div>
<div class="post">B</div>
<div class="post">C</div>
```

```python
nodes = tree.css(".post")

for node in nodes:
    print(node.text(strip=True))
```

Kết quả:

```text
A
B
C
```

---

# 2. Selector theo tag

```python
tree.css("h1")
tree.css("p")
tree.css("article")
tree.css("img")
tree.css("a")
```

Ví dụ:

```html
<article>
    <h1>Python</h1>
    <p>Hello</p>
</article>
```

```python
tree.css_first("h1")
```

---

# 3. Selector theo class

```css
.article
```

HTML:

```html
<article class="article">
```

Python:

```python
node = tree.css_first(".article")
```

Nhiều class:

```html
<div class="article featured">
```

Có thể:

```css
.article.featured
```

```python
tree.css_first(".article.featured")
```

⚠️ Không viết:

```css
.article .featured
```

Hai selector này khác nhau.

### `.article.featured`

```text
element
├── class=article
└── class=featured
```

### `.article .featured`

```text
.article
   └── descendant
       └── .featured
```

---

# 4. Selector theo ID

```html
<div id="content">
```

Dùng:

```python
tree.css_first("#content")
```

Nhưng trong scraping, tôi thường **không quá phụ thuộc vào ID**.

Lý do:

```text
id="content"
```

có thể được sinh động hoặc thay đổi.

Class semantic như:

```text
.article-content
.post-body
.entry-content
```

thường hữu ích hơn.

---

# 5. Descendant selector

HTML:

```html
<article class="post">
    <div class="content">
        <p>Hello</p>
    </div>
</article>
```

Có thể:

```python
tree.css_first(
    ".post .content"
)
```

hoặc:

```python
tree.css_first(
    ".post .content p"
)
```

Ý nghĩa:

```text
.post
  ↓
.content
  ↓
p
```

---

# 6. Child selector `>`

Đây là selector rất quan trọng.

HTML:

```html
<div class="content">
    <p>Hello</p>

    <div>
        <p>Nested</p>
    </div>
</div>
```

Nếu:

```python
tree.css(".content p")
```

thì lấy:

```text
Hello
Nested
```

Nhưng:

```python
tree.css(".content > p")
```

chỉ lấy:

```text
Hello
```

Vì `>` nghĩa là **con trực tiếp**.

---

# 7. Descendant vs Child

```css
.content p
```

nghĩa:

```text
.content
 └── p
     └── bất kỳ cấp nào
```

Trong khi:

```css
.content > p
```

nghĩa:

```text
.content
 └── p
     └── phải là direct child
```

Đây là một trong những selector quan trọng nhất khi extract article.

---

# 8. Selector theo attribute

HTML:

```html
<input type="text">

<input type="email">

<input type="password">
```

Có thể:

```python
tree.css('input[type="email"]')
```

---

# 9. Attribute tồn tại

```css
img[src]
```

Nghĩa:

> Chọn `img` có attribute `src`.

```python
images = tree.css("img[src]")
```

Rất hữu ích cho scraper.

---

# 10. Attribute `data-*`

Ví dụ:

```html
<img
    data-src="/images/a.jpg"
>
```

Ta có:

```python
tree.css("img[data-src]")
```

Đây là pattern phổ biến khi xử lý lazy loading.

---

# 11. Attribute bằng giá trị

```html
<meta name="description">
```

Selector:

```python
tree.css_first(
    'meta[name="description"]'
)
```

Lấy:

```python
node.attributes.get("content")
```

Ví dụ:

```python
node = tree.css_first(
    'meta[name="description"]'
)

description = (
    node.attributes.get("content")
    if node
    else None
)
```

---

# 12. Attribute bắt đầu bằng

CSS:

```css
[class^="article"]
```

Nghĩa:

```text
class bắt đầu bằng "article"
```

Ví dụ:

```html
<div class="article-body">
<div class="article-content">
```

---

# 13. Attribute kết thúc bằng

```css
[class$="-content"]
```

Ví dụ:

```html
<div class="article-content">
<div class="post-content">
```

---

# 14. Attribute chứa chuỗi

```css
[class*="content"]
```

Có thể match:

```text
article-content
post-content
main-content
content-wrapper
```

Nhưng **đừng lạm dụng**.

Ví dụ:

```python
tree.css('[class*="content"]')
```

có thể match quá nhiều node không liên quan.

Trong scraper:

> Selector càng chính xác càng tốt.

---

# 15. Multiple selector

Bạn có thể viết:

```python
tree.css(
    ".article-content, "
    ".post-content, "
    ".entry-content"
)
```

Ý nghĩa:

```text
.article-content
       OR
.post-content
       OR
.entry-content
```

Đây là kỹ thuật rất hữu ích khi website có nhiều template.

---

# 16. Fallback selector

Ở Buổi 8 chúng ta đã viết:

```python
def first_match(tree, selectors):
    for selector in selectors:
        node = tree.css_first(selector)

        if node:
            return node

    return None
```

Ví dụ:

```python
title = first_match(
    tree,
    (
        "h1.article-title",
        "h1.post-title",
        "h1.title",
        "article h1",
        "h1",
    ),
)
```

Đây là **fallback strategy**.

---

# 17. Tại sao thứ tự quan trọng?

Không nên:

```python
(
    "h1",
    "h1.article-title",
)
```

Vì `h1` quá rộng.

Nên:

```python
(
    "h1.article-title",
    "h1.post-title",
    "h1",
)
```

Nguyên tắc:

```text
Specific
   ↓
Less specific
   ↓
Generic fallback
```

---

# 18. Selector theo cấu trúc

HTML:

```html
<article class="post">

    <header>
        <h1>Python</h1>
    </header>

    <div class="content">
        <h2>Introduction</h2>
    </div>

</article>
```

Ta có:

```python
tree.css_first(
    "article.post > header > h1"
)
```

Selector này rất chính xác.

---

# 19. Nhưng đừng selector quá dài

Ví dụ:

```css
body > main > div.container > div.row > div.col > article > header > h1
```

Đây là selector **fragile**.

Chỉ cần website thay:

```html
<div class="row">
```

thành:

```html
<section class="row">
```

là scraper hỏng.

Tốt hơn:

```css
article.post h1
```

hoặc:

```css
h1.article-title
```

---

# 20. Nguyên tắc selector cho scraper

Ưu tiên:

```text
semantic class
    ↓
semantic element
    ↓
attribute
    ↓
structure
```

Ví dụ tốt:

```css
.article-title
```

```css
.article-content
```

```css
time[datetime]
```

Ví dụ dễ vỡ:

```css
body > div:nth-child(3) > div:nth-child(2) > h1
```

---

# 21. `:first-child`

HTML:

```html
<div class="content">
    <p>First</p>
    <p>Second</p>
</div>
```

Có thể:

```python
tree.css_first(
    ".content > p:first-child"
)
```

---

# 22. `:last-child`

```python
tree.css_first(
    ".content > p:last-child"
)
```

Nhưng với scraper, đừng quá phụ thuộc vào vị trí.

Nếu website thêm một paragraph:

```html
<p>Advertisement</p>
```

selector có thể cho kết quả khác.

---

# 23. `:nth-child()`

Ví dụ:

```python
tree.css(
    ".content > p:nth-child(2)"
)
```

→ paragraph thứ hai.

Nhưng:

> `nth-child` thường là selector cuối cùng tôi muốn dùng trong scraper production.

Nó phụ thuộc mạnh vào DOM structure.

---

# 24. `:not()`

Ví dụ:

```html
<div class="content">

    <p>Article</p>

    <p class="advertisement">
        Advertisement
    </p>

    <p>Article 2</p>

</div>
```

Có thể:

```python
tree.css(
    ".content > p:not(.advertisement)"
)
```

Kết quả:

```text
Article
Article 2
```

Đây là selector rất hữu ích để loại noise.

---

# 25. Kết hợp selector

Ví dụ:

```python
tree.css(
    "article.post .content > p:not(.ads)"
)
```

Đọc từ trái sang phải:

```text
article.post
    ↓
.content
    ↓
direct child p
    ↓
không có class ads
```

---

# 26. Extract links

HTML:

```html
<div class="content">

    <a href="/chapter/1">
        Chapter 1
    </a>

    <a href="/chapter/2">
        Chapter 2
    </a>

</div>
```

Code:

```python
for node in tree.css(
    ".content a[href]"
):
    href = node.attributes.get("href")

    print(href)
```

---

# 27. Extract link + text

```python
links = []

for node in tree.css(
    ".content a[href]"
):
    links.append({
        "text": node.text(strip=True),
        "href": node.attributes.get("href"),
    })
```

Kết quả:

```python
[
    {
        "text": "Chapter 1",
        "href": "/chapter/1",
    },
    {
        "text": "Chapter 2",
        "href": "/chapter/2",
    },
]
```

Đây sẽ là nền tảng cho crawler pagination/chapter ở các buổi sau.

---

# 28. Extract metadata

HTML:

```html
<meta
    property="og:title"
    content="Học Selectolax"
/>

<meta
    property="og:image"
    content="/images/selectolax.jpg"
/>
```

Selector:

```python
node = tree.css_first(
    'meta[property="og:title"]'
)
```

Lấy:

```python
title = node.attributes.get("content")
```

---

# 29. Open Graph

Đây là kỹ thuật rất đáng biết.

```python
def get_meta(
    tree,
    *,
    name=None,
    property=None,
):
    if name:
        selector = f'meta[name="{name}"]'

    elif property:
        selector = (
            f'meta[property="{property}"]'
        )

    else:
        return None

    node = tree.css_first(selector)

    if node is None:
        return None

    return node.attributes.get("content")
```

Dùng:

```python
title = get_meta(
    tree,
    property="og:title",
)

image = get_meta(
    tree,
    property="og:image",
)
```

---

# 30. Fallback title

Một Article Extractor tốt có thể:

```text
1. h1.article-title
        ↓
2. h1
        ↓
3. og:title
        ↓
4. <title>
```

Ví dụ:

```python
def extract_title(tree):

    node = first_match(
        tree,
        (
            "h1.article-title",
            "h1.post-title",
            "article h1",
            "h1",
        ),
    )

    if node:
        return node.text(strip=True)

    return get_meta(
        tree,
        property="og:title",
    )
```

---

# 31. Selector là "domain knowledge"

Đây là điểm rất quan trọng.

Selectolax chỉ làm:

```text
HTML
 ↓
DOM
```

CSS selector quyết định:

```text
DOM
 ↓
Business data
```

Ví dụ:

```text
.article-content
```

không phải kiến thức của Selectolax.

Đó là kiến thức của **website/domain**.

Vì vậy trong crawler lớn, selector nên được tổ chức riêng.

---

# 32. Site-specific configuration

Ví dụ:

```python
class SiteConfig:

    title_selectors = (
        "h1.article-title",
        "h1",
    )

    content_selectors = (
        ".article-content",
        ".post-content",
    )

    author_selectors = (
        ".author",
        ".post-author",
    )
```

Extractor:

```python
class ArticleExtractor:

    def __init__(self, config):
        self.config = config
```

Sau này:

```text
SiteAConfig
SiteBConfig
SiteCConfig
```

---

# 33. Đây chính là hướng Plugin Architecture

```text
Crawler
   │
   ▼
SitePlugin
   │
   ├── selectors
   ├── extractor
   └── URL rules
```

Ví dụ:

```text
plugins/
│
├── site_a/
│   ├── config.py
│   └── extractor.py
│
├── site_b/
│   ├── config.py
│   └── extractor.py
│
└── site_c/
    ├── config.py
    └── extractor.py
```

Điều này rất phù hợp với hệ thống **cào truyện nhiều nguồn**.

---

# 34. Một helper đáng xây

```python
def first_text(tree, selectors):
    node = first_match(
        tree,
        selectors,
    )

    if node is None:
        return None

    text = node.text(strip=True)

    return text or None
```

Sau đó:

```python
title = first_text(
    tree,
    (
        "h1.article-title",
        "h1.post-title",
        "h1",
    ),
)
```

---

# 35. `first_attr`

Tương tự:

```python
def first_attr(
    tree,
    selectors,
    attr,
):
    node = first_match(
        tree,
        selectors,
    )

    if node is None:
        return None

    return node.attributes.get(attr)
```

Dùng:

```python
published_at = first_attr(
    tree,
    (
        "time[datetime]",
        "time",
    ),
    "datetime",
)
```

---

# 36. Tạo Extraction Toolkit

Sau này có thể có:

```text
ExtractionToolkit
│
├── first_match()
├── first_text()
├── first_attr()
├── all_text()
├── all_attr()
├── get_meta()
└── absolute_url()
```

Ví dụ:

```python
class ExtractionToolkit:

    @staticmethod
    def first_match(tree, selectors):
        ...

    @staticmethod
    def first_text(tree, selectors):
        ...

    @staticmethod
    def first_attr(
        tree,
        selectors,
        attr,
    ):
        ...
```

Đây là bước từ:

```text
script
```

sang:

```text
scraping library
```

---

# 37. Bài tập 1

Cho HTML:

```html
<article class="post">

    <header>
        <h1 class="title">
            Selectolax
        </h1>
    </header>

    <div class="content">

        <p>Paragraph 1</p>

        <div class="box">
            <p>Nested</p>
        </div>

        <p class="ads">
            Advertisement
        </p>

        <p>Paragraph 2</p>

    </div>

</article>
```

Viết selector để lấy:

### A

```text
Selectolax
```

### B

```text
Paragraph 1
Paragraph 2
```

nhưng không lấy:

```text
Nested
Advertisement
```

Gợi ý:

```css
.content > p:not(.ads)
```

---

# 38. Bài tập 2 — Metadata

Cho:

```html
<meta
    property="og:title"
    content="Python Scraping"
/>

<meta
    property="og:image"
    content="/image.jpg"
/>
```

Viết:

```python
get_meta(
    tree,
    property="og:title",
)
```

để trả:

```text
Python Scraping
```

---

# 39. Bài tập 3 — Article Extractor

Viết:

```python
class ArticleExtractor:
    ...
```

với fallback:

```text
Title:

h1.article-title
      ↓
h1.post-title
      ↓
h1
      ↓
og:title
      ↓
<title>
```

Content:

```text
.article-content
      ↓
.post-content
      ↓
.entry-content
```

Author:

```text
.author
      ↓
.post-author
      ↓
meta[name="author"]
```

---

# 40. Bài tập 4 — Link extractor

Cho:

```html
<div class="chapters">

    <a href="/chapter/1">
        Chương 1
    </a>

    <a href="/chapter/2">
        Chương 2
    </a>

</div>
```

Trả về:

```python
[
    {
        "title": "Chương 1",
        "url": "https://example.com/chapter/1",
    },
    {
        "title": "Chương 2",
        "url": "https://example.com/chapter/2",
    },
]
```

Sử dụng:

```python
urljoin()
```

---

# 41. Bài tập 5 — Phân tích selector

Cho:

```html
<div class="content">

    <p>A</p>

    <section>
        <p>B</p>
    </section>

    <p>C</p>

</div>
```

Dự đoán kết quả:

```python
tree.css(".content p")
```

và:

```python
tree.css(".content > p")
```

Bạn cần hiểu chính xác sự khác nhau này trước khi sang DOM Traversal.

---

# 🧠 Tổng kết Buổi 9

Các selector quan trọng cần thuộc:

```css
h1
```

```css
.article
```

```css
#content
```

```css
.article .content
```

```css
.article > .content
```

```css
img[src]
```

```css
img[data-src]
```

```css
meta[property="og:title"]
```

```css
.content > p:not(.ads)
```

```css
.article-content, .post-content
```

Và nguyên tắc quan trọng nhất:

```text
Selector cụ thể
       ↓
Selector ít cụ thể hơn
       ↓
Generic fallback
```

Không nên xây scraper dựa vào:

```css
body > div:nth-child(3) > div:nth-child(2)
```

mà ưu tiên:

```css
.article-title
.article-content
.post-author
time[datetime]
```

---

## 🔜 Buổi 10 — DOM Traversal

Buổi tiếp theo chúng ta sẽ **không chỉ dùng CSS Selector**, mà học cách đi trong DOM:

```text
Node
 │
 ├── parent
 ├── child
 ├── children
 ├── next sibling
 ├── previous sibling
 └── descendants
```

Đây là phần rất quan trọng khi gặp HTML kiểu:

```html
<div class="chapter">
    <h2>Chương 1</h2>

    <div class="content">
        ...
    </div>

    <div class="navigation">
        ...
    </div>
</div>
```

và bạn cần từ một node đã tìm được **đi lên parent, xuống children hoặc sang sibling** để lấy dữ liệu mà CSS selector thuần túy khó xử lý.
