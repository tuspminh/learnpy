# 📘 Selectolax — Buổi 6: Làm sạch HTML

Hôm nay chúng ta đi vào một kỹ năng rất quan trọng khi xây **article crawler / crawler truyện**:

> **Từ một HTML đầy quảng cáo, menu, script, style... → chỉ giữ lại nội dung bài viết sạch.**

Pipeline:

```text
HTML
 ↓
Selectolax
 ↓
Remove unwanted nodes
 ↓
Clean DOM
 ↓
Extract article content
 ↓
HTML / Text
```

---

# 1. Tại sao phải làm sạch HTML?

HTML thực tế thường như thế này:

```html
<body>

    <header>
        Logo
        Menu
    </header>

    <nav>
        Home
        Category
        Search
    </nav>

    <article>
        <h1>Python</h1>

        <p>Nội dung bài viết...</p>
        <p>Tiếp tục...</p>
    </article>

    <aside>
        Quảng cáo
    </aside>

    <footer>
        Copyright
    </footer>

    <script>
        ...
    </script>

</body>
```

Nếu lấy:

```python
tree.body.text()
```

bạn sẽ nhận cả:

```text
Logo
Menu
Home
Category
Search
Python
Nội dung bài viết...
Quảng cáo
Copyright
```

Trong khi ta chỉ muốn:

```text
Python

Nội dung bài viết...
Tiếp tục...
```

---

# 2. Selectolax có thể chỉnh sửa DOM

Đây là điểm quan trọng.

Selectolax không chỉ:

```text
HTML → đọc dữ liệu
```

mà còn có thể dùng để:

```text
HTML
 ↓
DOM
 ↓
Modify DOM
 ↓
HTML sạch
```

Tư duy:

```text
Original DOM
     │
     ├── script       ❌
     ├── style        ❌
     ├── nav          ❌
     ├── ads          ❌
     └── article      ✅
```

---

# 3. Xóa `script`

HTML:

```html
<body>

    <script>
        console.log("hello");
    </script>

    <h1>Python</h1>

</body>
```

Lấy tất cả:

```python
scripts = tree.css("script")
```

Sau đó loại bỏ từng Node bằng API mutation phù hợp của phiên bản Selectolax bạn đang dùng.

Với các bản Selectolax hiện đại, thao tác thường dùng là:

```python
node.decompose()
```

Ví dụ:

```python
from selectolax.parser import HTMLParser


html = """
<body>
    <script>
        console.log("hello");
    </script>

    <h1>Python</h1>
</body>
"""

tree = HTMLParser(html)

for node in tree.css("script"):
    node.decompose()

print(tree.html)
```

`script` đã bị loại khỏi DOM.

---

# 4. Xóa `style`

Tương tự:

```python
for node in tree.css("style"):
    node.decompose()
```

Ví dụ:

```html
<style>
    body {
        background: red;
    }
</style>
```

không còn trong DOM sau khi `decompose()`.

---

# 5. Xóa nhiều loại Node

Không cần viết:

```python
for node in tree.css("script"):
    node.decompose()

for node in tree.css("style"):
    node.decompose()
```

Có thể gom selector:

```python
for node in tree.css("script, style"):
    node.decompose()
```

Rất tiện.

---

# 6. Xóa comment

HTML:

```html
<!-- This is a comment -->

<p>Hello</p>
```

Comment không phải element thông thường.

Khi làm cleaner, bạn có thể duyệt DOM và loại bỏ các comment node theo loại Node mà Selectolax expose.

Một cách thực tế là tập trung trước vào các element gây nhiễu:

```text
script
style
noscript
iframe
```

Sau đó xử lý comment nếu pipeline của bạn thực sự cần loại bỏ chúng.

---

# 7. Xóa `noscript`

Website có thể chứa:

```html
<noscript>
    Please enable JavaScript.
</noscript>
```

Không phải nội dung article.

Xóa:

```python
for node in tree.css("noscript"):
    node.decompose()
```

---

# 8. Xóa `iframe`

Quảng cáo thường được nhúng bằng:

```html
<iframe src="..."></iframe>
```

Có thể:

```python
for node in tree.css("iframe"):
    node.decompose()
```

---

# 9. Xây danh sách unwanted tags

Thay vì hard-code từng lần:

```python
UNWANTED_TAGS = (
    "script",
    "style",
    "noscript",
    "iframe",
)
```

Sau đó:

```python
selector = ", ".join(UNWANTED_TAGS)

for node in tree.css(selector):
    node.decompose()
```

Kết quả selector:

```text
script, style, noscript, iframe
```

Đây là cách tốt để cấu hình cleaner.

---

# 10. Xóa quảng cáo

Quảng cáo khó hơn `script`.

Ví dụ:

```html
<div class="advertisement">
    Buy something!
</div>
```

Ta có thể:

```python
for node in tree.css(".advertisement"):
    node.decompose()
```

Nhưng website khác có thể dùng:

```text
.ads
.ad
.banner
.google-ad
.adsbygoogle
```

Do đó cần một danh sách selector.

---

# 11. Ad selectors

Ví dụ:

```python
AD_SELECTORS = (
    ".advertisement",
    ".advert",
    ".ad",
    ".ads",
    ".ads-container",
    ".adsbygoogle",
    ".banner-ad",
)
```

Cleaner:

```python
for selector in AD_SELECTORS:
    for node in tree.css(selector):
        node.decompose()
```

---

# 12. Nhưng có một vấn đề

Không nên quá mạnh tay.

Ví dụ:

```html
<div class="content">
```

Nếu bạn vô tình thêm:

```python
".content"
```

vào `AD_SELECTORS`:

```python
for node in tree.css(".content"):
    node.decompose()
```

Bạn vừa xóa **toàn bộ bài viết**.

Vì vậy:

> **Cleaner phải có selector chính xác và có test.**

---

# 13. Xóa navigation

HTML:

```html
<nav class="main-menu">
    <a href="/">Home</a>
    <a href="/news">News</a>
</nav>
```

Ta có:

```python
for node in tree.css("nav"):
    node.decompose()
```

Hoặc:

```python
for node in tree.css(".main-menu"):
    node.decompose()
```

---

# 14. Xóa header

Nếu mục tiêu là lấy article content:

```python
for node in tree.css("header"):
    node.decompose()
```

---

# 15. Xóa footer

```python
for node in tree.css("footer"):
    node.decompose()
```

---

# 16. Xóa sidebar

Ví dụ:

```html
<aside class="sidebar">
    Popular stories
    Advertisement
</aside>
```

Ta có:

```python
for node in tree.css("aside.sidebar"):
    node.decompose()
```

---

# 17. Tập hợp toàn bộ

Ta có:

```python
REMOVE_SELECTORS = (
    "script",
    "style",
    "noscript",
    "iframe",
    "nav",
    "header",
    "footer",
    "aside",
    ".advertisement",
    ".ads",
    ".adsbygoogle",
)
```

Cleaner:

```python
def clean_tree(tree):
    selector = ", ".join(REMOVE_SELECTORS)

    for node in tree.css(selector):
        node.decompose()

    return tree
```

---

# 18. Test cleaner

HTML:

```python
html = """
<html>
<body>

<header>
    Website Header
</header>

<nav>
    Home
    Categories
</nav>

<article>
    <h1>Python</h1>

    <p>Hello Python</p>

    <div class="advertisement">
        BUY NOW!
    </div>

    <p>Learning Selectolax</p>
</article>

<footer>
    Copyright
</footer>

<script>
    alert("Hello");
</script>

</body>
</html>
"""
```

Chạy:

```python
tree = HTMLParser(html)

clean_tree(tree)

print(tree.html)
```

Ta muốn còn:

```html
<article>
    <h1>Python</h1>
    <p>Hello Python</p>
    <p>Learning Selectolax</p>
</article>
```

---

# 19. Nhưng mục tiêu thực tế không phải chỉ "xóa rác"

Đây là một insight rất quan trọng.

Có hai chiến lược:

### Strategy A — Blacklist

```text
Giữ tất cả
trừ:
script
style
ads
nav
footer
...
```

### Strategy B — Whitelist

```text
Chỉ lấy:
article
  ↓
content
  ↓
h1
p
img
...
```

Với website không ổn định, **whitelist thường an toàn hơn** nếu bạn biết chính xác vùng nội dung cần lấy.

---

# 20. Blacklist

Ví dụ:

```text
body
│
├── header       ❌
├── nav          ❌
├── article      ✅
├── aside        ❌
├── footer       ❌
└── script      ❌
```

Sau khi xóa:

```text
body
│
└── article
```

Ưu điểm:

* Dễ triển khai
* Giữ được HTML article
* Có thể giữ những element chưa biết trước

Nhược điểm:

* Quảng cáo mới có thể lọt vào.

---

# 21. Whitelist

Ta xác định:

```python
article = tree.css_first("article.article")
```

Sau đó chỉ lấy:

```python
content = article.css_first(".content")
```

Rồi:

```python
content_html = content.html
```

Khi đó những thứ bên ngoài `.content` hoàn toàn không ảnh hưởng.

Đây thường là chiến lược tốt cho **site-specific parser**.

---

# 22. Kết hợp hai chiến lược

Đây là cách tôi khuyên dùng cho crawler của bạn:

```text
HTML
 ↓
Tìm article
 ↓
Lấy content
 ↓
Blacklist trong content
 ↓
Normalize
 ↓
Output
```

Ví dụ:

```python
article = tree.css_first("article")
content = article.css_first(".content")

for node in content.css(
    "script, style, iframe, .advertisement"
):
    node.decompose()

html = content.html
```

---

# 23. Xóa quảng cáo bên trong article

Đây là tình huống rất thực tế.

```html
<article>
    <h1>Python</h1>

    <p>Paragraph 1</p>

    <div class="ads">
        Advertisement
    </div>

    <p>Paragraph 2</p>
</article>
```

Nếu chỉ lấy:

```python
article.html
```

thì quảng cáo vẫn còn.

Do đó:

```python
for node in article.css(".ads"):
    node.decompose()
```

Sau đó:

```python
content_html = article.html
```

---

# 24. Xóa element dựa trên nhiều class

Ví dụ website:

```html
<div class="ad banner">
```

Bạn có thể:

```python
tree.css(".ad")
```

hoặc:

```python
tree.css(".banner")
```

Nếu muốn chính xác hơn:

```python
tree.css(".ad.banner")
```

---

# 25. Xóa theo attribute

Một số website:

```html
<div data-ad="true">
    Advertisement
</div>
```

CSS selector:

```python
tree.css('[data-ad="true"]')
```

Sau đó:

```python
for node in tree.css('[data-ad="true"]'):
    node.decompose()
```

---

# 26. Xóa theo attribute chứa chuỗi

Ví dụ:

```html
<div class="google-ad-container">
```

Có thể:

```python
tree.css('[class*="ad"]')
```

**Nhưng cực kỳ nguy hiểm.**

Vì:

```text
[class*="ad"]
```

có thể match những class không phải quảng cáo.

Ví dụ class chứa `ad` tình cờ.

Vì vậy production crawler nên ưu tiên:

```python
".adsbygoogle"
".advertisement"
".ad-container"
```

thay vì selector quá rộng.

---

# 27. Xóa `onclick` / event attributes

HTML:

```html
<a
    href="/python"
    onclick="trackClick()"
>
    Python
</a>
```

Nếu mục tiêu là HTML sạch, có thể muốn giữ:

```html
<a href="/python">Python</a>
```

Selectolax cho phép thao tác với attributes của Node. Bạn có thể duyệt các Node và loại bỏ những attribute bắt đầu bằng:

```text
on
```

như:

```text
onclick
onload
onmouseover
```

Ý tưởng:

```python
for node in tree.body.iter():
    ...
```

và loại các event attributes.

Phần này sẽ hữu ích khi chúng ta xây một **HTML sanitizer** hoàn chỉnh.

---

# 28. Giữ lại nội dung bài viết

Giả sử:

```html
<body>

    <header>...</header>

    <nav>...</nav>

    <main>

        <article class="article">

            <h1>Python</h1>

            <div class="content">
                <p>Hello</p>
                <p>World</p>
            </div>

        </article>

        <aside>...</aside>

    </main>

    <footer>...</footer>

</body>
```

Ta không cần clean toàn bộ document.

Ta có thể:

```python
content = tree.css_first(
    "article.article .content"
)
```

Sau đó:

```python
content_html = content.html
```

Đây là cách rất sạch.

---

# 29. Content extraction + cleaning

Tạo:

```python
def extract_clean_content(
    html: str,
    selector: str,
) -> str | None:

    tree = HTMLParser(html)

    content = tree.css_first(selector)

    if content is None:
        return None

    for node in content.css(
        "script, style, noscript, iframe"
    ):
        node.decompose()

    return content.html
```

Dùng:

```python
content = extract_clean_content(
    html,
    ".article .content",
)
```

---

# 30. Xây `HTMLCleaner`

Bây giờ bắt đầu thiết kế abstraction.

```python
from selectolax.parser import HTMLParser


class HTMLCleaner:

    REMOVE_SELECTORS = (
        "script",
        "style",
        "noscript",
        "iframe",
        "nav",
        "footer",
        ".advertisement",
        ".ads",
        ".adsbygoogle",
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

Dùng:

```python
cleaner = HTMLCleaner()

clean_html = cleaner.clean(html)
```

---

# 31. Nhưng `HTMLCleaner` chưa đủ tốt

Vấn đề:

```python
REMOVE_SELECTORS
```

đang hard-code.

Website A:

```text
.ads
```

Website B:

```text
.advertisement
```

Website C:

```text
.google-ad
```

Website D:

```text
.banner
```

Do đó nên cho phép cấu hình.

---

# 32. Configurable Cleaner

```python
class HTMLCleaner:

    DEFAULT_SELECTORS = (
        "script",
        "style",
        "noscript",
        "iframe",
    )

    def __init__(self, selectors=None):
        self.selectors = selectors or self.DEFAULT_SELECTORS

    def clean(self, html: str) -> str:
        tree = HTMLParser(html)

        selector = ", ".join(self.selectors)

        for node in tree.css(selector):
            node.decompose()

        return tree.html
```

Dùng:

```python
cleaner = HTMLCleaner(
    selectors=(
        "script",
        "style",
        "nav",
        ".ads",
        ".advertisement",
    )
)
```

---

# 33. Site-specific cleaner

Đây là kiến trúc rất hay cho crawler nhiều website.

```text
Crawler
│
├── SiteA
│   └── SiteACleaner
│
├── SiteB
│   └── SiteBCleaner
│
└── SiteC
    └── SiteCCleaner
```

Ví dụ:

```python
class SiteACleaner(HTMLCleaner):

    selectors = (
        "script",
        "style",
        ".ads",
        ".popup",
        ".related",
    )
```

Website B:

```python
class SiteBCleaner(HTMLCleaner):

    selectors = (
        "script",
        "style",
        ".advertisement",
        ".sidebar",
    )
```

Đây chính là nền tảng cho **Plugin Architecture** mà bạn đang học ở các khóa khác.

---

# 34. Cleaner không nên biết HTTP

Không:

```text
Cleaner
 ↓
HTTPX
```

Mà:

```text
HTTPX
 ↓
HTML
 ↓
Cleaner
 ↓
Clean HTML
```

Tương tự Parser:

```text
HTTPX
 ↓
HTML
 ↓
Cleaner
 ↓
Parser
 ↓
Data
```

---

# 35. Pipeline hoàn chỉnh

Đến cuối buổi này, pipeline của chúng ta đã trở thành:

```text
             URL
              │
              ▼
           HTTPX
              │
              ▼
         Raw HTML
              │
              ▼
        HTMLCleaner
              │
              ▼
         Clean HTML
              │
              ▼
       Selectolax Parser
              │
              ▼
        Structured Data
```

Sau này **Buổi 7** chúng ta sẽ nối HTTPX vào pipeline này.

---

# 36. Một vấn đề quan trọng: `decompose()` làm thay đổi DOM

Ví dụ:

```python
scripts = tree.css("script")

for node in scripts:
    node.decompose()
```

Sau `decompose()`:

```text
node
```

không còn nằm trong DOM.

Vì vậy không nên:

```python
node.decompose()

print(node.text())
```

và mong Node vẫn hoạt động như trước.

Hãy coi:

```python
node.decompose()
```

là:

> **Xóa Node khỏi cây DOM.**

---

# 37. Thứ tự cleaning

Một pipeline tốt:

```text
1. Parse
   ↓
2. Locate content
   ↓
3. Remove scripts/styles
   ↓
4. Remove ads
   ↓
5. Remove navigation/related content
   ↓
6. Remove unwanted attributes
   ↓
7. Extract HTML/text
```

Không nhất thiết mọi website đều cần đủ 7 bước.

---

# 38. Không nên "clean quá tay"

Đây là lỗi phổ biến.

Ví dụ:

```python
REMOVE_SELECTORS = (
    "div",
    "span",
    "p",
)
```

Tất nhiên bạn vừa xóa gần như toàn bộ article.

Cleaner tốt phải có nguyên tắc:

> **Chỉ xóa những gì bạn chắc chắn là noise.**

Không nên dùng selector rộng chỉ vì nó "có vẻ đúng".

---

# 39. Bài tập thực hành

Cho HTML:

```html
<html>
<body>

<header>
    Website Header
</header>

<nav>
    Home
    Categories
</nav>

<main>

    <article class="article">

        <h1>Học Python</h1>

        <div class="content">

            <p>Python rất mạnh.</p>

            <div class="advertisement">
                QUẢNG CÁO
            </div>

            <p>Selectolax rất nhanh.</p>

            <script>
                alert("tracking");
            </script>

            <p>HTTPX dùng để HTTP.</p>

        </div>

    </article>

    <aside class="sidebar">
        Bài viết liên quan
    </aside>

</main>

<footer>
    Copyright
</footer>

</body>
</html>
```

## Bài 1

Xóa:

```text
header
nav
aside
footer
script
```

---

## Bài 2

Xóa:

```text
.advertisement
```

---

## Bài 3

Lấy:

```text
.article .content
```

---

## Bài 4

Trả về HTML sạch:

```html
<p>Python rất mạnh.</p>
<p>Selectolax rất nhanh.</p>
<p>HTTPX dùng để HTTP.</p>
```

---

## Bài 5 — Quan trọng

Viết:

```python
class HTMLCleaner:
    ...
```

API:

```python
cleaner = HTMLCleaner()

clean_html = cleaner.clean(html)
```

---

## Bài 6 — Site-specific

Cho phép:

```python
cleaner = HTMLCleaner(
    selectors=[
        "script",
        "style",
        ".advertisement",
        ".sidebar",
    ]
)
```

---

# 🎯 Bài tập nâng cao

Xây:

```python
def clean_article(
    html: str,
    content_selector: str,
) -> dict:
    ...
```

Kết quả:

```python
{
    "html": "...",
    "text": "...",
}
```

Ví dụ:

```python
result = clean_article(
    html,
    ".article .content",
)
```

Kết quả:

```python
{
    "html": "<p>Python rất mạnh.</p>...",
    "text": "Python rất mạnh. Selectolax rất nhanh. HTTPX dùng để HTTP.",
}
```

---

# 🧠 Kiến thức quan trọng nhất của Buổi 6

Bạn cần phân biệt **3 tầng**:

### 1. Remove toàn document

```python
for node in tree.css("script, style"):
    node.decompose()
```

### 2. Locate content

```python
content = tree.css_first(
    "article .content"
)
```

### 3. Clean bên trong content

```python
for node in content.css(
    "script, style, .ads"
):
    node.decompose()
```

Với **crawler truyện/article**, tầng 2 + 3 thường là cách an toàn nhất:

```text
Raw HTML
   ↓
Find article content
   ↓
Clean inside content
   ↓
HTML sạch
   ↓
Text / Database / Reader
```

**Buổi 7** sẽ ghép `Selectolax` với **HTTPX** để tạo crawler thật:

```text
URL
 ↓
httpx.Client
 ↓
Response
 ↓
status code
 ↓
HTML
 ↓
Selectolax
 ↓
CSS Selector
 ↓
Extract
```

và chúng ta sẽ học kỹ **Headers, Timeout, Retry, status code và cách thiết kế `Fetcher` tách khỏi `Parser`**.
