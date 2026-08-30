# 📘 Selectolax — Buổi 8: Xây dựng `ArticleExtractor`

Hôm nay chúng ta ghép toàn bộ kiến thức từ Buổi 1 → 7 thành một component có tính thực tế:

```text
URL
 ↓
HTTPFetcher
 ↓
HTML
 ↓
HTMLCleaner
 ↓
Selectolax
 ↓
ArticleExtractor
 ↓
Article
 ├── title
 ├── content
 ├── author
 ├── published_at
 └── images
```

Mục tiêu quan trọng nhất:

> **Tách việc lấy HTML, làm sạch HTML và trích xuất dữ liệu thành các component độc lập.**

---

# 1. Bài toán

Giả sử một trang bài viết:

```html
<article class="article">

    <h1 class="title">
        Học Python với Selectolax
    </h1>

    <div class="author">
        Garden
    </div>

    <time datetime="2026-08-27">
        27/08/2026
    </time>

    <div class="article-content">

        <p>Selectolax là HTML parser.</p>

        <p>HTTPX dùng để gửi HTTP request.</p>

        <img src="/images/python.jpg">

    </div>

</article>
```

Ta muốn:

```python
{
    "title": "Học Python với Selectolax",
    "author": "Garden",
    "published_at": "2026-08-27",
    "content": "...",
    "images": [
        "/images/python.jpg"
    ]
}
```

---

# 2. Đừng trả về `dict` mãi

Ban đầu:

```python
return {
    "title": title,
    "author": author,
}
```

được.

Nhưng crawler lớn dần sẽ có:

```text
Article
Chapter
Story
Author
Category
Image
```

Tốt hơn nên tạo model.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str | None
    content: str | None
    author: str | None
    published_at: str | None
    images: list[str]
```

---

# 3. Tạo `Article`

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str | None = None
    content: str | None = None
    author: str | None = None
    published_at: str | None = None
    images: list[str] | None = None
```

Nhưng:

```python
images: list[str] | None = None
```

không thật sự tiện.

Ta có thể dùng:

```python
from dataclasses import dataclass, field


@dataclass
class Article:
    title: str | None = None
    content: str | None = None
    author: str | None = None
    published_at: str | None = None
    images: list[str] = field(default_factory=list)
```

---

# 4. Vì sao `default_factory`?

Không nên:

```python
images: list[str] = []
```

vì list mutable không nên dùng làm default trực tiếp.

Dùng:

```python
field(default_factory=list)
```

Mỗi `Article` có một list riêng.

---

# 5. `ArticleExtractor`

Bắt đầu đơn giản:

```python
from selectolax.parser import HTMLParser


class ArticleExtractor:

    def extract(self, html: str) -> Article:
        tree = HTMLParser(html)

        return Article(
            title=self._extract_title(tree),
            author=self._extract_author(tree),
            published_at=self._extract_date(tree),
            content=self._extract_content(tree),
            images=self._extract_images(tree),
        )
```

Đây là pattern rất quan trọng:

```text
extract()
   │
   ├── _extract_title()
   ├── _extract_author()
   ├── _extract_date()
   ├── _extract_content()
   └── _extract_images()
```

---

# 6. Extract title

```python
def _extract_title(self, tree):
    node = tree.css_first("h1")

    if node is None:
        return None

    return node.text(strip=True)
```

Ví dụ:

```html
<h1>
    Học Python
</h1>
```

Kết quả:

```text
Học Python
```

---

# 7. `text()` và `text(strip=True)`

Thay vì:

```python
node.text()
```

nên thường dùng:

```python
node.text(strip=True)
```

để loại khoảng trắng dư thừa ở đầu/cuối.

Ví dụ:

```html
<h1>
    Hello
</h1>
```

Ta muốn:

```text
Hello
```

thay vì:

```text
    Hello
```

---

# 8. Extract author

HTML:

```html
<div class="author">
    Garden
</div>
```

Code:

```python
def _extract_author(self, tree):
    node = tree.css_first(".author")

    if node is None:
        return None

    return node.text(strip=True)
```

---

# 9. Extract published date

HTML:

```html
<time datetime="2026-08-27">
    27/08/2026
</time>
```

Đừng lấy text nếu muốn dữ liệu chuẩn.

Thay vào đó:

```python
def _extract_date(self, tree):
    node = tree.css_first("time")

    if node is None:
        return None

    return node.attributes.get("datetime")
```

Kết quả:

```text
2026-08-27
```

---

# 10. Tại sao lấy attribute?

HTML:

```html
<time datetime="2026-08-27">
    27/08/2026
</time>
```

Có hai dữ liệu:

```text
text
 ↓
27/08/2026

attribute
 ↓
2026-08-27
```

Đối với crawler:

```text
attribute thường là dữ liệu machine-readable
```

nên thường ưu tiên:

```python
node.attributes.get("datetime")
```

---

# 11. Extract content

Giả sử:

```html
<div class="article-content">

    <p>Paragraph 1</p>

    <p>Paragraph 2</p>

</div>
```

Ta có:

```python
def _extract_content(self, tree):
    node = tree.css_first(
        ".article-content"
    )

    if node is None:
        return None

    return node.html
```

Kết quả là HTML:

```html
<p>Paragraph 1</p>
<p>Paragraph 2</p>
```

---

# 12. Content HTML hay Text?

Đây là một quyết định kiến trúc rất quan trọng.

### Nếu lấy:

```python
node.text()
```

ta mất:

```html
<p>
<strong>
<em>
<a>
<img>
<pre>
<code>
```

Ví dụ:

```html
<p>
    Hello <strong>Python</strong>
</p>
```

Text:

```text
Hello Python
```

HTML:

```html
<p>
    Hello <strong>Python</strong>
</p>
```

Đối với **app đọc truyện / article reader**, nên giữ HTML.

---

# 13. Tôi khuyên `Article` giữ HTML

```python
@dataclass
class Article:
    title: str | None = None
    content: str | None = None
    author: str | None = None
    published_at: str | None = None
    images: list[str] = field(
        default_factory=list
    )
```

Trong đó:

```text
content
   ↓
clean HTML
```

Sau này muốn text:

```python
tree = HTMLParser(article.content)

text = tree.body.text(
    separator="\n"
)
```

Như vậy:

```text
HTML
 ↓
database

HTML
 ↓
reader

HTML
 ↓
Markdown

HTML
 ↓
text-to-speech
```

đều có thể thực hiện.

---

# 14. Extract images

HTML:

```html
<img src="/images/python.jpg">
<img src="/images/httpx.jpg">
```

Selectolax:

```python
def _extract_images(self, tree):
    images = []

    for node in tree.css(
        ".article-content img"
    ):
        src = node.attributes.get("src")

        if src:
            images.append(src)

    return images
```

---

# 15. `src` có thể không tồn tại

Một số website dùng:

```html
<img
    data-src="/images/python.jpg"
>
```

thay vì:

```html
<img src="/images/python.jpg">
```

Ta có thể fallback:

```python
src = (
    node.attributes.get("src")
    or node.attributes.get("data-src")
)
```

---

# 16. `srcset`

Website responsive có thể:

```html
<img
    src="small.jpg"
    srcset="
        small.jpg 480w,
        medium.jpg 800w,
        large.jpg 1200w
    "
>
```

Đây là một bài toán khác.

Ở phiên bản đầu:

```python
src = node.attributes.get("src")
```

là đủ.

Sau này có thể xây:

```text
ImageExtractor
```

riêng.

---

# 17. Relative URL

Đây là vấn đề cực kỳ quan trọng.

Website:

```html
<img src="/images/python.jpg">
```

URL:

```text
https://example.com/article/python
```

`src` không phải URL hoàn chỉnh.

Ta cần:

```text
/images/python.jpg

        ↓

https://example.com/images/python.jpg
```

Python có:

```python
from urllib.parse import urljoin
```

---

# 18. `urljoin`

```python
from urllib.parse import urljoin


base_url = "https://example.com/article/python"

image_url = urljoin(
    base_url,
    "/images/python.jpg",
)

print(image_url)
```

Kết quả:

```text
https://example.com/images/python.jpg
```

---

# 19. Extract images có `base_url`

```python
def _extract_images(self, tree, base_url):
    images = []

    for node in tree.css(
        ".article-content img"
    ):
        src = (
            node.attributes.get("src")
            or node.attributes.get("data-src")
        )

        if not src:
            continue

        images.append(
            urljoin(base_url, src)
        )

    return images
```

---

# 20. Vì vậy `extract()` cần URL

Thay vì:

```python
extract(html)
```

ta dùng:

```python
extract(
    html,
    url,
)
```

Ví dụ:

```python
def extract(
    self,
    html: str,
    url: str,
) -> Article:
    ...
```

---

# 21. Full `ArticleExtractor`

```python
from dataclasses import dataclass, field
from urllib.parse import urljoin

from selectolax.parser import HTMLParser


@dataclass
class Article:
    title: str | None = None
    content: str | None = None
    author: str | None = None
    published_at: str | None = None
    images: list[str] = field(
        default_factory=list
    )


class ArticleExtractor:

    def extract(
        self,
        html: str,
        url: str,
    ) -> Article:

        tree = HTMLParser(html)

        return Article(
            title=self._extract_title(tree),
            content=self._extract_content(tree),
            author=self._extract_author(tree),
            published_at=self._extract_date(tree),
            images=self._extract_images(
                tree,
                url,
            ),
        )

    def _extract_title(self, tree):
        node = tree.css_first("h1")

        if node is None:
            return None

        return node.text(strip=True)

    def _extract_author(self, tree):
        node = tree.css_first(".author")

        if node is None:
            return None

        return node.text(strip=True)

    def _extract_date(self, tree):
        node = tree.css_first("time")

        if node is None:
            return None

        return node.attributes.get(
            "datetime"
        )

    def _extract_content(self, tree):
        node = tree.css_first(
            ".article-content"
        )

        if node is None:
            return None

        return node.html

    def _extract_images(
        self,
        tree,
        base_url,
    ):
        images = []

        for node in tree.css(
            ".article-content img"
        ):
            src = (
                node.attributes.get("src")
                or node.attributes.get(
                    "data-src"
                )
            )

            if not src:
                continue

            images.append(
                urljoin(base_url, src)
            )

        return images
```

---

# 22. Nhưng còn HTMLCleaner?

Buổi 6 chúng ta đã xây Cleaner.

Không nên bỏ nó.

Pipeline nên là:

```text
HTTPFetcher
     ↓
Raw HTML
     ↓
HTMLCleaner
     ↓
Clean HTML
     ↓
ArticleExtractor
     ↓
Article
```

---

# 23. `HTMLCleaner`

Ví dụ:

```python
class HTMLCleaner:

    REMOVE_SELECTORS = (
        "script",
        "style",
        "noscript",
        "iframe",
        ".advertisement",
        ".ads",
    )

    def clean(self, html: str) -> str:
        tree = HTMLParser(html)

        selector = ", ".join(
            self.REMOVE_SELECTORS
        )

        for node in tree.css(selector):
            node.decompose()

        return tree.html
```

---

# 24. Cleaner + Extractor

```python
class ArticleExtractor:

    def __init__(
        self,
        cleaner: HTMLCleaner,
    ):
        self.cleaner = cleaner

    def extract(
        self,
        html: str,
        url: str,
    ) -> Article:

        clean_html = self.cleaner.clean(
            html
        )

        tree = HTMLParser(clean_html)

        return Article(
            title=self._extract_title(tree),
            content=self._extract_content(tree),
            author=self._extract_author(tree),
            published_at=self._extract_date(tree),
            images=self._extract_images(
                tree,
                url,
            ),
        )
```

Đây là Dependency Injection đơn giản:

```text
ArticleExtractor
      │
      ▼
HTMLCleaner
```

---

# 25. Ghép HTTPX

Bây giờ:

```text
             URL
              │
              ▼
        ┌─────────────┐
        │ HTTPFetcher │
        └──────┬──────┘
               │
             HTML
               │
               ▼
        ┌─────────────┐
        │ HTMLCleaner │
        └──────┬──────┘
               │
          Clean HTML
               │
               ▼
       ┌─────────────────┐
       │ ArticleExtractor│
       └────────┬────────┘
                │
                ▼
             Article
```

---

# 26. `Scraper`

```python
class Scraper:

    def __init__(
        self,
        fetcher,
        extractor,
    ):
        self.fetcher = fetcher
        self.extractor = extractor

    def scrape(
        self,
        url: str,
    ) -> Article:

        html = self.fetcher.fetch(url)

        return self.extractor.extract(
            html,
            url,
        )
```

Đây là orchestration.

---

# 27. Full architecture

```python
fetcher = HTTPFetcher()

cleaner = HTMLCleaner()

extractor = ArticleExtractor(
    cleaner=cleaner,
)

scraper = Scraper(
    fetcher=fetcher,
    extractor=extractor,
)

article = scraper.scrape(url)

print(article.title)
print(article.author)
print(article.published_at)
print(article.images)
print(article.content)
```

---

# 28. Đây mới là kiến trúc đáng chú ý

Chúng ta có:

```text
                 Scraper
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Fetcher             Extractor
        │                     │
      HTTPX                Cleaner
                              │
                           Selectolax
```

Mỗi component có một trách nhiệm.

### `HTTPFetcher`

```text
HTTP
```

### `HTMLCleaner`

```text
Remove noise
```

### `ArticleExtractor`

```text
HTML → Article
```

### `Scraper`

```text
Orchestration
```

---

# 29. Site-specific selector

Đây là vấn đề thực tế nhất.

Không phải website nào cũng:

```css
h1
.article-content
.author
time
```

Có website:

```css
article h1.title
.post-body
.post-author
.publish-date
```

Có website khác:

```css
.story-title
.chapter-content
.author-name
```

Không nên nhét tất cả vào một Extractor.

---

# 30. Configurable Extractor

Ta có thể truyền selector:

```python
class ArticleExtractor:

    def __init__(
        self,
        title_selector="h1",
        content_selector=".article-content",
        author_selector=".author",
        date_selector="time",
    ):
        self.title_selector = title_selector
        self.content_selector = content_selector
        self.author_selector = author_selector
        self.date_selector = date_selector
```

Sau đó:

```python
extractor = ArticleExtractor(
    title_selector="h1.title",
    content_selector=".post-body",
    author_selector=".post-author",
    date_selector="time",
)
```

---

# 31. Đây là bước đầu của Plugin Architecture

Ta có:

```text
Site A
 ↓
ArticleExtractor(
    title_selector="h1.title",
    content_selector=".content",
)

Site B
 ↓
ArticleExtractor(
    title_selector=".post-title",
    content_selector=".post-content",
)
```

Sau này có thể tiến tới:

```text
Extractor
   │
   ├── SiteAExtractor
   ├── SiteBExtractor
   └── SiteCExtractor
```

Đây rất phù hợp với crawler truyện mà bạn đang xây dựng.

---

# 32. Đừng parse bằng một selector duy nhất

Ví dụ:

```python
title = tree.css_first("h1")
```

có thể thất bại.

Một chiến lược tốt hơn:

```python
def first_match(tree, selectors):
    for selector in selectors:
        node = tree.css_first(selector)

        if node:
            return node

    return None
```

Sau đó:

```python
title_node = first_match(
    tree,
    (
        "h1.article-title",
        "h1.post-title",
        "h1.title",
        "article h1",
    ),
)
```

---

# 33. Generic selector helper

Đây là helper rất đáng xây:

```python
def first_match(tree, selectors):
    for selector in selectors:
        node = tree.css_first(selector)

        if node is not None:
            return node

    return None
```

Dùng:

```python
node = first_match(
    tree,
    [
        ".article-title",
        ".post-title",
        "h1",
    ],
)
```

---

# 34. Extract title với fallback

```python
def _extract_title(self, tree):

    node = first_match(
        tree,
        (
            "h1.article-title",
            "h1.post-title",
            "h1.title",
            "article h1",
        ),
    )

    if node is None:
        return None

    return node.text(strip=True)
```

Đây là kỹ thuật rất hữu ích khi crawler nhiều phiên bản HTML.

---

# 35. Content extraction khó hơn title

Title thường:

```text
h1
```

Nhưng content có thể:

```text
.article-content
.post-content
.entry-content
.content
article
```

Ta có:

```python
CONTENT_SELECTORS = (
    ".article-content",
    ".post-content",
    ".entry-content",
    "article",
)
```

Sau đó:

```python
content = first_match(
    tree,
    CONTENT_SELECTORS,
)
```

---

# 36. Nhưng fallback `article` nguy hiểm

Nếu:

```python
article = tree.css_first("article")
```

bên trong có:

```text
related posts
advertisement
comments
sidebar
```

thì content có thể bị nhiễm.

Do đó:

```text
Ưu tiên selector cụ thể
        ↓
fallback selector rộng
        ↓
clean
```

---

# 37. `ArticleExtractor` không nên biết HTTP

Nhớ nguyên tắc:

```text
❌ ArticleExtractor → httpx
```

mà:

```text
✅ HTTPFetcher → HTML
                  ↓
           ArticleExtractor
```

Điều này giúp test cực kỳ dễ.

---

# 38. Unit Test

Ta có thể test:

```python
HTML = """
<article>

    <h1>Python</h1>

    <div class="article-content">

        <p>Hello</p>

        <script>
            alert("tracking");
        </script>

        <p>Selectolax</p>

    </div>

</article>
"""
```

Extractor:

```python
article = extractor.extract(
    HTML,
    "https://example.com/article",
)
```

Assert:

```python
assert article.title == "Python"
assert "Hello" in article.content
assert "Selectolax" in article.content
assert "tracking" not in article.content
```

Không cần Internet.

Đây là một lợi ích rất lớn của architecture hiện tại.

---

# 39. Test HTTPFetcher riêng

Không test:

```text
HTTP + Selectolax + Extractor
```

cùng một lúc.

Ta test:

```text
HTTPFetcher
     ↓
HTTP behavior
```

và:

```text
ArticleExtractor
     ↓
HTML behavior
```

riêng.

Sau đó integration test mới kiểm tra toàn pipeline.

---

# 40. Một phiên bản hoàn chỉnh hơn

Cấu trúc thư mục:

```text
scraper/
│
├── models/
│   └── article.py
│
├── http/
│   └── fetcher.py
│
├── html/
│   └── cleaner.py
│
├── extractors/
│   └── article.py
│
└── scraper.py
```

Luồng:

```text
scraper.py
    │
    ├── http/fetcher.py
    │
    └── extractors/article.py
                    │
                    └── html/cleaner.py
```

---

# 41. Một lưu ý quan trọng về `content`

Hiện tại:

```python
return node.html
```

có thể trả về:

```html
<div class="article-content">
    <p>Hello</p>
</div>
```

Nếu bạn muốn **chỉ children**:

```html
<p>Hello</p>
```

thì cần thiết kế rõ API.

Ví dụ:

```python
return "".join(
    child.html for child in node.iter()
)
```

Tuy nhiên cần cẩn thận vì `iter()` và cấu trúc Node của Selectolax phụ thuộc API/version bạn đang dùng.

Trong project thực tế, nên kiểm tra chính xác version Selectolax và test output.

---

# 42. Một quyết định thiết kế tốt

Tôi khuyên model:

```python
@dataclass
class Article:
    title: str | None
    content_html: str | None
    author: str | None
    published_at: str | None
    images: list[str]
```

thay vì:

```python
content
```

Vì tên:

```text
content_html
```

nói rõ dữ liệu là gì.

Sau này có thể thêm:

```python
content_text: str | None
```

nếu cần.

---

# 43. Model hoàn chỉnh

```python
@dataclass
class Article:

    title: str | None = None

    content_html: str | None = None

    author: str | None = None

    published_at: str | None = None

    images: list[str] = field(
        default_factory=list
    )
```

Sau này:

```python
article.content_html
```

và:

```python
article.content_text
```

có thể là hai representation khác nhau.

---

# 44. Pipeline production hơn

Đến đây:

```text
                         URL
                          │
                          ▼
                   ┌─────────────┐
                   │ HTTPFetcher │
                   │   HTTPX     │
                   └──────┬──────┘
                          │
                        HTML
                          │
                          ▼
                   ┌─────────────┐
                   │ HTMLCleaner │
                   └──────┬──────┘
                          │
                     Clean HTML
                          │
                          ▼
                   ┌─────────────┐
                   │  Selectolax │
                   └──────┬──────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ArticleExtractor │
                 └───────┬─────────┘
                         │
                         ▼
                      Article
```

Đây chính là nền móng để sau này thêm:

```text
Database
Queue
Retry
Concurrency
Plugin
CLI
PySide6
```

mà không phải viết lại toàn bộ scraper.

---

# 🧪 Bài tập Buổi 8

## Bài 1 — `Article`

Tạo:

```python
@dataclass
class Article:
    title: str | None
    content_html: str | None
    author: str | None
    published_at: str | None
    images: list[str]
```

---

## Bài 2 — Extractor

Viết:

```python
class ArticleExtractor:

    def extract(
        self,
        html: str,
        url: str,
    ) -> Article:
        ...
```

Extract:

```text
title
author
published_at
content_html
images
```

---

## Bài 3 — Relative image URL

Cho:

```html
<img src="/images/python.jpg">
```

và:

```text
https://example.com/articles/python
```

Kết quả phải là:

```text
https://example.com/images/python.jpg
```

---

## Bài 4 — Lazy image

Xử lý:

```html
<img data-src="/images/python.jpg">
```

nếu không có `src`.

---

## Bài 5 — Fallback selectors

Title:

```python
(
    "h1.article-title",
    "h1.post-title",
    "h1",
)
```

Content:

```python
(
    ".article-content",
    ".post-content",
    ".entry-content",
)
```

Viết helper:

```python
first_match()
```

---

# 🚀 Bài tập lớn

Xây mini crawler:

```text
article_scraper/
│
├── models/
│   └── article.py
│
├── http/
│   └── fetcher.py
│
├── html/
│   └── cleaner.py
│
├── extractors/
│   └── article.py
│
├── scraper.py
│
└── main.py
```

Pipeline:

```text
URL
 ↓
HTTPFetcher
 ↓
HTMLCleaner
 ↓
ArticleExtractor
 ↓
Article
```

`main.py`:

```python
url = "https://example.com/article"

article = scraper.scrape(url)

print(article.title)
print(article.author)
print(article.published_at)
print(article.images)
print(article.content_html)
```

---

# 🎯 4 nguyên tắc cần nhớ sau Buổi 8

### 1. Fetcher không parse

```text
HTTPFetcher
    ↓
   HTML
```

### 2. Extractor không gọi HTTP

```text
ArticleExtractor
    ↓
HTML → Article
```

### 3. Cleaner không biết Article

```text
HTMLCleaner
    ↓
HTML → Clean HTML
```

### 4. Scraper chỉ orchestration

```text
Scraper
 ├── Fetcher
 └── Extractor
```

Tư duy này rất quan trọng nếu mục tiêu của bạn không chỉ là viết một script scraping mà là xây **crawler framework có thể mở rộng**.

---

## 📚 Roadmap tiếp theo

Sau Buổi 8, phần Selectolax có thể đi tiếp theo hướng:

```text
Buổi 9   — Selectolax nâng cao
           Node / parent / children / traversal

Buổi 10  — CSS Selector nâng cao
           attribute / combinator / pseudo selector

Buổi 11  — Extract text sạch
           whitespace / paragraph / normalize

Buổi 12  — Extract links
           absolute URL / relative URL

Buổi 13  — Extract images
           src / data-src / srcset

Buổi 14  — HTML → Markdown

Buổi 15  — Article extraction nâng cao

Buổi 16  — Xây Crawler Engine
```

Nếu mục tiêu cuối cùng của bạn là **app cào truyện + đọc truyện bằng PySide6**, thì từ đây phần đáng học sâu nhất là **Extractor + site-specific parser + plugin architecture**, vì nó sẽ nối trực tiếp với kiến trúc crawler mà bạn đã học về Clean Architecture/DDD/SOLID.
