# Buổi 13 — BeautifulSoup → html2text

Đây là lúc chúng ta bắt đầu chuyển từ **học thư viện `html2text`** sang xây dựng **pipeline xử lý HTML thực tế**.

Mục tiêu hôm nay:

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

Tư duy quan trọng:

> **BeautifulSoup dùng để chuẩn bị và làm sạch HTML. `html2text` dùng để chuyển HTML sạch thành Markdown.**

---

## 1. Vì sao không đưa HTML thẳng vào `html2text`?

Một trang web thực tế có thể như:

```html
<html>
<body>

<header>
    Logo
    Menu
</header>

<nav>
    Home | Category | Login
</nav>

<main>

    <article>
        <h1>Python</h1>

        <p>Python là...</p>

        <p>Python được sử dụng...</p>
    </article>

    <aside>
        Quảng cáo
    </aside>

</main>

<footer>
    Copyright...
</footer>

<script>
    ...
</script>

</body>
</html>
```

Nếu:

```python
markdown = html2text.html2text(html)
```

thì converter phải nhìn thấy rất nhiều thứ mà chúng ta **không muốn đưa vào Markdown**:

```text
header
nav
aside
footer
script
style
advertisement
tracking
```

Do đó nên có:

```text
Raw HTML
   ↓
BeautifulSoup
   ↓
Cleaning
   ↓
Clean HTML
   ↓
html2text
   ↓
Markdown
```

---

# 2. Hai thư viện có nhiệm vụ khác nhau

Đây là nguyên tắc quan trọng.

### BeautifulSoup

Nhiệm vụ:

```text
Parse HTML
Find elements
Remove elements
Extract elements
Modify DOM
```

### html2text

Nhiệm vụ:

```text
HTML structure
       ↓
Markdown structure
```

Không nên bắt `html2text` làm nhiệm vụ của BeautifulSoup.

---

# 3. BeautifulSoup parse HTML

Cơ bản:

```python
from bs4 import BeautifulSoup

html = """
<html>
<body>
    <h1>Hello</h1>
    <p>Python</p>
</body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

print(soup)
```

Ta có:

```text
HTML string
    ↓
BeautifulSoup
    ↓
DOM-like tree
```

---

# 4. Tìm article

Ví dụ:

```html
<main>
    <article class="article">
        <h1>Python</h1>
        <p>Hello</p>
    </article>
</main>
```

Có thể:

```python
article = soup.find("article")
```

Sau đó:

```python
print(article)
```

---

# 5. `find()` vs `select()`

BeautifulSoup có:

```python
soup.find("article")
```

và CSS selector:

```python
soup.select_one("article")
```

Ví dụ:

```python
article = soup.select_one("article.article")
```

CSS selector rất hữu ích khi scraper website thực tế.

---

# 6. Xóa element

Đây là kỹ thuật cực kỳ quan trọng.

HTML:

```html
<div class="advertisement">
    Buy something!
</div>
```

Tìm:

```python
ad = soup.select_one(".advertisement")
```

Xóa:

```python
ad.decompose()
```

DOM trở thành:

```text
<div class="advertisement">
```

→ biến mất hoàn toàn.

---

# 7. `decompose()` vs `extract()`

Hai method này rất dễ nhầm.

### `decompose()`

```python
element.decompose()
```

Xóa element khỏi tree và giải phóng nó.

Dùng khi:

> Tôi chắc chắn không cần element này nữa.

### `extract()`

```python
element.extract()
```

Tách element khỏi tree nhưng object vẫn có thể được sử dụng.

Ví dụ:

```python
ad = soup.select_one(".advertisement")

removed = ad.extract()
```

Bây giờ:

```text
soup
 ↓
ad đã bị lấy ra
```

nhưng:

```python
removed
```

vẫn tồn tại.

---

# 8. Trong HTML cleaner thường dùng `decompose()`

Ví dụ:

```python
for tag in soup.select("script, style, nav, footer"):
    tag.decompose()
```

Đây là pattern rất phổ biến.

---

# 9. Xóa nhiều loại element

Ví dụ:

```python
selectors = [
    "script",
    "style",
    "nav",
    "footer",
    ".advertisement",
    ".ads",
    ".popup",
]
```

Sau đó:

```python
for selector in selectors:
    for element in soup.select(selector):
        element.decompose()
```

Ta có:

```text
Raw HTML
   ↓
remove script
   ↓
remove style
   ↓
remove nav
   ↓
remove footer
   ↓
remove ads
   ↓
Clean HTML
```

---

# 10. Tạo HTML Cleaner đơn giản

```python
from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    selectors = [
        "script",
        "style",
        "nav",
        "footer",
    ]

    for selector in selectors:
        for element in soup.select(selector):
            element.decompose()

    return str(soup)
```

Sau đó:

```python
cleaned = clean_html(html)
```

---

# 11. Đưa Clean HTML vào html2text

```python
import html2text
from bs4 import BeautifulSoup


def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.select("script, style, nav, footer"):
        element.decompose()

    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(str(soup))
```

Pipeline:

```text
html
 ↓
BeautifulSoup
 ↓
decompose()
 ↓
str(soup)
 ↓
html2text
 ↓
Markdown
```

---

# 12. Nhưng có một vấn đề

Giả sử:

```html
<body>

<header>
    Website
</header>

<nav>
    Home | Books | Login
</nav>

<article>
    <h1>Python</h1>
    <p>Hello Python.</p>
</article>

<footer>
    Copyright 2026
</footer>

</body>
```

Sau cleaning:

```html
<body>

<article>
    <h1>Python</h1>
    <p>Hello Python.</p>
</article>

</body>
```

Tốt.

Nhưng chúng ta vẫn đang convert **toàn bộ body**.

Tốt hơn nữa:

```text
Raw HTML
 ↓
BeautifulSoup
 ↓
Extract article
 ↓
Clean article
 ↓
html2text
```

---

# 13. Extract article trước

```python
article = soup.select_one("article")
```

Sau đó:

```python
if article is None:
    raise ValueError("Article not found")
```

Rồi:

```python
clean_html = str(article)
```

Cuối cùng:

```python
markdown = converter.handle(clean_html)
```

---

# 14. Pipeline tốt hơn

```text
Raw HTML
    ↓
BeautifulSoup
    ↓
Find <article>
    ↓
Remove unwanted elements
    ↓
article HTML
    ↓
html2text
    ↓
Markdown
```

Ví dụ:

```python
def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    article = soup.select_one("article")

    if article is None:
        raise ValueError("Article not found")

    for element in article.select(
        "script, style, nav, footer, .ads, .advertisement"
    ):
        element.decompose()

    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(str(article))
```

---

# 15. Tại sao remove sau khi extract?

Đây là một quyết định architecture quan trọng.

### Cách 1

```text
Raw HTML
 ↓
Remove tất cả
 ↓
Find article
```

### Cách 2

```text
Raw HTML
 ↓
Find article
 ↓
Remove unwanted elements trong article
```

Tôi thường ưu tiên:

```text
Find content boundary
        ↓
Clean content
```

vì cleaner không vô tình đụng vào những vùng khác của trang.

---

# 16. Ví dụ thực tế

```html
<body>

<nav>
    Menu
</nav>

<main>

<article class="story">

<h1>Chương 1</h1>

<div class="ads">
    Advertisement
</div>

<p>
Ngày hôm đó...
</p>

<div class="share-buttons">
    Facebook Twitter
</div>

<p>
Anh bước vào căn phòng.
</p>

</article>

</main>

<footer>
    Copyright
</footer>

</body>
```

Ta muốn:

```text
Chương 1

Ngày hôm đó...

Anh bước vào căn phòng.
```

Không muốn:

```text
Menu
Advertisement
Facebook Twitter
Copyright
```

---

# 17. Cleaner

```python
def clean_article(article):
    selectors = [
        ".ads",
        ".advertisement",
        ".share-buttons",
    ]

    for selector in selectors:
        for element in article.select(selector):
            element.decompose()

    return article
```

---

# 18. Converter

```python
def convert_article(article) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(str(article))
```

---

# 19. Tách trách nhiệm

Đừng viết một function khổng lồ:

```python
def scrape_and_clean_and_convert_and_save(...):
    ...
```

Hãy chia:

```text
parse_html()
     ↓
extract_article()
     ↓
clean_article()
     ↓
convert_markdown()
```

Ví dụ:

```python
def parse_html(html: str):
    return BeautifulSoup(html, "html.parser")


def extract_article(soup):
    return soup.select_one("article")


def clean_article(article):
    for element in article.select(
        "script, style, .ads, .advertisement"
    ):
        element.decompose()

    return article


def convert_markdown(article) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(str(article))
```

---

# 20. Composition

Sau đó:

```python
def process_html(html: str) -> str:
    soup = parse_html(html)

    article = extract_article(soup)

    if article is None:
        raise ValueError("Article not found")

    article = clean_article(article)

    return convert_markdown(article)
```

Đây là architecture tốt hơn rất nhiều.

---

# 21. `html2text` không cần biết BeautifulSoup

Điểm này rất quan trọng.

`convert_markdown()` chỉ cần:

```python
def convert_markdown(article) -> str:
    ...
```

Nó không nên chứa:

```python
select()
decompose()
find()
```

Ngược lại:

```text
BeautifulSoup
     ↓
DOM manipulation

html2text
     ↓
HTML → Markdown
```

Hai layer độc lập.

---

# 22. Boundary giữa hai layer

Tôi khuyên xác định boundary:

```text
BeautifulSoup
      │
      │ str(element)
      ▼
Clean HTML string
      │
      ▼
html2text
```

Ví dụ:

```python
cleaned_html = str(article)

markdown = converter.handle(cleaned_html)
```

Đây là boundary rất rõ.

---

# 23. Một vấn đề với `str(soup)`

Nếu:

```python
soup = BeautifulSoup(html, "html.parser")
```

và:

```python
str(soup)
```

BeautifulSoup có thể serialize lại HTML.

Ví dụ source:

```html
<p>Hello<br/></p>
```

có thể được serialize khác một chút tùy parser.

Không sao.

Mục tiêu của chúng ta không phải giữ nguyên source HTML byte-by-byte.

Mục tiêu:

```text
semantic HTML
      ↓
Markdown
```

---

# 24. `html.parser`

BeautifulSoup có nhiều parser.

Thông dụng:

```python
BeautifulSoup(html, "html.parser")
```

Đây là parser có sẵn trong Python.

Có thể gặp:

```python
BeautifulSoup(html, "lxml")
```

hoặc:

```python
BeautifulSoup(html, "html5lib")
```

Trong khóa này, trước mắt chúng ta tập trung:

```python
"html.parser"
```

---

# 25. Một Cleaner tốt hơn

Thay vì hard-code:

```python
for element in article.select(...):
```

hãy truyền selectors:

```python
def remove_elements(root, selectors: list[str]) -> None:
    for selector in selectors:
        for element in root.select(selector):
            element.decompose()
```

Dùng:

```python
remove_elements(
    article,
    [
        "script",
        "style",
        ".ads",
        ".advertisement",
        ".share",
    ],
)
```

---

# 26. Đây chính là tiền thân của `HTMLCleaner`

Architecture:

```python
class HTMLCleaner:
    def clean(self, html: str) -> str:
        ...
```

Sau này:

```text
HTMLCleaner
    │
    ├── remove_scripts()
    ├── remove_styles()
    ├── remove_ads()
    ├── remove_navigation()
    ├── remove_social()
    └── extract_article()
```

Chúng ta sẽ xây class này ở **Buổi 15**.

---

# 27. Một phiên bản thực tế

```python
from bs4 import BeautifulSoup


class HTMLCleaner:

    REMOVE_SELECTORS = [
        "script",
        "style",
        "nav",
        "footer",
        ".ads",
        ".advertisement",
        ".share-buttons",
    ]

    def clean(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        article = soup.select_one("article")

        if article is None:
            raise ValueError("Article not found")

        for selector in self.REMOVE_SELECTORS:
            for element in article.select(selector):
                element.decompose()

        return str(article)
```

Sau đó:

```python
cleaner = HTMLCleaner()

clean_html = cleaner.clean(html)
```

---

# 28. Converter riêng

```python
import html2text


class MarkdownConverter:

    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.body_width = 0

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

---

# 29. Ghép hai component

```python
cleaner = HTMLCleaner()
converter = MarkdownConverter()

clean_html = cleaner.clean(html)

markdown = converter.convert(clean_html)
```

Pipeline rất rõ:

```text
HTMLCleaner
     ↓
Clean HTML
     ↓
MarkdownConverter
     ↓
Markdown
```

---

# 30. Tại sao architecture này tốt?

Sau này bạn có thể thay:

```text
BeautifulSoup
```

bằng:

```text
Selectolax
```

mà không cần thay `MarkdownConverter`.

Ví dụ:

```text
BeautifulSoupCleaner
        ↓
        HTML
        ↓
MarkdownConverter
```

hoặc:

```text
SelectolaxCleaner
        ↓
        HTML
        ↓
MarkdownConverter
```

Đây chính là **separation of concerns**.

---

# 31. Một vấn đề thực tế: `<article>` không phải website nào cũng có

Website A:

```html
<article>
```

Website B:

```html
<div class="post-content">
```

Website C:

```html
<div id="content">
```

Website D:

```html
<main class="chapter">
```

Do đó:

```python
soup.select_one("article")
```

không phải universal solution.

Ta sẽ học **Article Extraction** sâu hơn ở Buổi 20.

---

# 32. Selector fallback

Có thể tạm thời:

```python
ARTICLE_SELECTORS = [
    "article",
    ".post-content",
    ".article-content",
    "#content",
    "main",
]
```

Sau đó:

```python
def extract_article(soup):
    for selector in ARTICLE_SELECTORS:
        article = soup.select_one(selector)

        if article is not None:
            return article

    return None
```

Đây là một heuristic đơn giản.

---

# 33. Nhưng đừng biến nó thành "God Function"

Không nên:

```python
def extract_article(...):
    # 300 dòng
    # detect site
    # remove ads
    # parse title
    # parse author
    # convert markdown
    # save database
    ...
```

Hãy tách:

```text
Extractor
Cleaner
Converter
Repository
```

Sau này architecture sẽ rất đẹp:

```text
HTTPX
  ↓
Fetcher
  ↓
HTML
  ↓
Extractor
  ↓
Cleaner
  ↓
MarkdownConverter
  ↓
Markdown
  ↓
Model
  ↓
Repository
```

---

# 34. Pipeline của project crawler truyện

Đây là architecture tôi khuyên bạn hướng tới:

```text
HTTPX
  │
  ▼
Fetcher
  │
  ▼
Raw HTML
  │
  ▼
HTML Extractor
  │
  ▼
Article HTML
  │
  ▼
HTML Cleaner
  │
  ▼
Clean HTML
  │
  ▼
html2text
  │
  ▼
Markdown
  │
  ▼
Normalizer
  │
  ▼
Chapter Model
  │
  ▼
SQLite
```

Đây là bước đầu tiên để từ một script scraper trở thành một **pipeline có architecture**.

---

# 35. Bài tập 1

Cho HTML:

```html
<html>
<body>

<nav>
    Home | Login
</nav>

<article>
    <h1>Python</h1>
    <p>Hello Python.</p>
</article>

<footer>
    Copyright
</footer>

</body>
</html>
```

Viết:

```python
def extract_article(html: str):
    ...
```

Output phải là `<article>`.

---

# 36. Bài tập 2

Cho:

```html
<article>

<h1>Python</h1>

<div class="ads">
    BUY NOW!
</div>

<p>Hello.</p>

<script>
    alert("hello");
</script>

<p>World.</p>

</article>
```

Viết:

```python
def clean_article(article):
    ...
```

để loại bỏ:

```text
.ads
script
```

---

# 37. Bài tập 3

Viết pipeline:

```python
def html_to_markdown(html: str) -> str:
    ...
```

Yêu cầu:

```text
HTML
 ↓
BeautifulSoup
 ↓
extract article
 ↓
remove script/style/ads
 ↓
html2text
 ↓
Markdown
```

---

# 38. Bài tập 4 — Debug pipeline

Đừng chỉ:

```python
print(markdown)
```

Hãy in từng stage:

```python
print("=" * 60)
print("RAW HTML")
print(html)

print("=" * 60)
print("CLEAN HTML")
print(clean_html)

print("=" * 60)
print("MARKDOWN")
print(markdown)
```

Bạn sẽ thấy chính xác:

```text
Raw HTML
   ↓
Cleaner đã làm gì?
   ↓
html2text đã làm gì?
```

Đây là kỹ năng rất quan trọng khi scraper gặp website khó.

---

# 39. Bài tập 5 — Thiết kế class

Tạo:

```text
HTMLCleaner
MarkdownConverter
```

API:

```python
cleaner.clean(html)
converter.convert(clean_html)
```

Sau đó:

```python
clean_html = cleaner.clean(html)
markdown = converter.convert(clean_html)
```

---

# 40. Bài tập 6 — Production mindset

Giả sử website có:

```html
<nav>
<aside>
<footer>
<script>
<style>
<div class="ads">
<div class="comments">
<div class="share">
<div class="related-posts">
```

Hãy quyết định:

**Cái nào nên remove trước `html2text`?**

Gợi ý:

```text
script       → remove
style        → remove
ads          → remove
navigation   → remove
share        → thường remove
comments     → tùy website
related      → tùy requirement
```

Không phải mọi thứ đều có câu trả lời universal.

---

# 41. Mental model của Buổi 13

Hãy nhớ:

```text
              RAW HTML
                  │
                  ▼
          ┌───────────────┐
          │ BeautifulSoup │
          └───────┬───────┘
                  │
                  ▼
          Extract content
                  │
                  ▼
          Remove unwanted
                  │
                  ▼
             Clean HTML
                  │
                  ▼
          ┌───────────────┐
          │   html2text   │
          └───────┬───────┘
                  │
                  ▼
              Markdown
```

**BeautifulSoup không thay thế `html2text`.**

Hai thư viện bổ sung cho nhau:

```text
BeautifulSoup
    = DOM manipulation / cleaning

html2text
    = HTML → Markdown conversion
```

---

## Sau Buổi 13

Bạn đã có pipeline đầu tiên:

```text
HTML
 ↓
BeautifulSoup
 ↓
Extract
 ↓
Clean
 ↓
html2text
 ↓
Markdown
```

**Buổi 14 — Selectolax → html2text** sẽ thay BeautifulSoup bằng **Selectolax**, rồi chúng ta sẽ so sánh:

```text
BeautifulSoup
     vs
Selectolax
```

về:

* API
* CSS selector
* tốc độ
* memory
* `remove`
* `decompose`
* extract article
* serialization HTML
* suitability cho crawler lớn

và xây pipeline:

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
