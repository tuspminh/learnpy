# Buổi 14 — Selectolax → html2text

Hôm nay chúng ta thay **BeautifulSoup** bằng **Selectolax** để xây pipeline phù hợp hơn cho crawler:

```text
HTTPX
  ↓
HTML
  ↓
Selectolax
  ↓
Extract article
  ↓
Clean HTML
  ↓
html2text
  ↓
Markdown
```

Điểm quan trọng nhất của buổi này:

> **Selectolax chịu trách nhiệm parse/truy vấn/thao tác DOM; `html2text` chịu trách nhiệm render HTML → Markdown.**

---

# 1. Tại sao cần Selectolax?

Ở Buổi 13 ta có:

```text
HTML
 ↓
BeautifulSoup
 ↓
Clean
 ↓
html2text
```

BeautifulSoup rất dễ học và rất tiện.

Nhưng với crawler, chúng ta thường xử lý:

```text
hàng nghìn
hàng chục nghìn
hàng trăm nghìn
```

trang HTML.

Khi đó hiệu năng parsing trở nên đáng quan tâm.

Selectolax được thiết kế thiên về:

```text
HTML parsing
DOM traversal
CSS selector
high performance
```

---

# 2. Cài đặt

Nếu chưa có:

```bash
pip install selectolax
```

Kiểm tra:

```python
import selectolax

print(selectolax)
```

---

# 3. Parser cơ bản

Selectolax có parser HTML.

Ví dụ:

```python
from selectolax.parser import HTMLParser

html = """
<html>
<body>
    <h1>Python</h1>
    <p>Hello Python</p>
</body>
</html>
"""

tree = HTMLParser(html)

print(tree)
```

Mental model:

```text
HTML string
    ↓
HTMLParser
    ↓
DOM tree
```

---

# 4. Tìm node

Ví dụ:

```python
node = tree.css_first("h1")

print(node.text())
```

Output:

```text
Python
```

So sánh với BeautifulSoup:

```python
soup.find("h1")
```

Selectolax:

```python
tree.css_first("h1")
```

---

# 5. CSS selector

Đây là một trong những điểm mạnh khi scraper.

HTML:

```html
<article class="story">
    <h1>Python</h1>
    <p>Hello</p>
</article>
```

Tìm:

```python
article = tree.css_first("article.story")
```

Hoặc:

```python
article = tree.css_first(".story")
```

---

# 6. `css_first()`

```python
node = tree.css_first("article")
```

Nếu không tìm thấy:

```python
print(node)
```

sẽ là:

```text
None
```

Do đó:

```python
if node is None:
    raise ValueError("Article not found")
```

Đây là pattern bạn nên hình thành từ bây giờ.

---

# 7. `css()`

Nếu muốn tìm nhiều node:

```python
nodes = tree.css("p")
```

Ví dụ:

```python
for node in nodes:
    print(node.text())
```

HTML:

```html
<p>One</p>
<p>Two</p>
<p>Three</p>
```

Output:

```text
One
Two
Three
```

---

# 8. So sánh nhanh

### BeautifulSoup

```python
soup.select_one("article")
```

### Selectolax

```python
tree.css_first("article")
```

### BeautifulSoup

```python
soup.select("p")
```

### Selectolax

```python
tree.css("p")
```

Tư duy CSS selector gần như giống nhau.

---

# 9. Lấy text

Selectolax:

```python
node.text()
```

Ví dụ:

```python
html = """
<p>Hello <strong>Python</strong></p>
"""

tree = HTMLParser(html)

p = tree.css_first("p")

print(p.text())
```

Kết quả:

```text
Hello Python
```

---

# 10. Nhưng chúng ta không muốn lấy text

Đây là điểm cực kỳ quan trọng.

Nếu mục tiêu là:

```text
HTML → Markdown
```

thì **đừng làm**:

```python
text = article.text()
```

rồi:

```python
markdown = html2text.html2text(text)
```

Vì lúc đó HTML structure đã mất.

---

# 11. Ví dụ mất structure

HTML:

```html
<h1>Python</h1>

<p>Hello <strong>world</strong>.</p>
```

Nếu:

```python
article.text()
```

ta có:

```text
Python

Hello world.
```

`html2text` không còn biết:

```text
Python = heading
world = bold
```

Kết quả Markdown sẽ mất semantic.

---

# 12. Chúng ta cần HTML của node

Thay vì:

```python
article.text()
```

hãy giữ:

```text
article node
```

và serialize lại thành:

```text
HTML
```

rồi đưa HTML đó cho `html2text`.

Pipeline:

```text
Selectolax Node
     ↓
HTML serialization
     ↓
html2text
     ↓
Markdown
```

---

# 13. `html` property

Với node, bạn có thể lấy HTML serialization:

```python
article.html
```

Ví dụ:

```python
article = tree.css_first("article")

clean_html = article.html
```

Sau đó:

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 0

markdown = converter.handle(clean_html)
```

---

# 14. Pipeline đầu tiên

```python
from selectolax.parser import HTMLParser
import html2text


def html_to_markdown(html: str) -> str:
    tree = HTMLParser(html)

    article = tree.css_first("article")

    if article is None:
        raise ValueError("Article not found")

    clean_html = article.html

    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(clean_html)
```

Đây là pipeline cơ bản.

---

# 15. Thêm cleaning

Giả sử:

```html
<article>

<h1>Python</h1>

<div class="ads">
    BUY NOW
</div>

<p>Hello Python.</p>

<script>
    tracking();
</script>

<p>Python is powerful.</p>

</article>
```

Chúng ta muốn:

```text
<h1>Python</h1>
<p>Hello Python.</p>
<p>Python is powerful.</p>
```

---

# 16. Selectolax remove node

Ta tìm:

```python
ads = article.css_first(".ads")
```

Sau đó xóa node.

Selectolax có API thao tác node để loại bỏ phần tử khỏi cây.

Một pattern thường dùng là:

```python
for node in article.css("script, style, .ads"):
    node.decompose()
```

Sau cleaning:

```python
clean_html = article.html
```

---

# 17. Cleaner

Ta có thể viết:

```python
def clean_article(article) -> None:
    selectors = [
        "script",
        "style",
        ".ads",
        ".advertisement",
    ]

    for selector in selectors:
        for node in article.css(selector):
            node.decompose()
```

Sau đó:

```python
clean_article(article)
```

---

# 18. Full pipeline

```python
from selectolax.parser import HTMLParser
import html2text


def clean_article(article) -> None:
    selectors = [
        "script",
        "style",
        ".ads",
        ".advertisement",
    ]

    for selector in selectors:
        for node in article.css(selector):
            node.decompose()


def convert_html_to_markdown(html: str) -> str:
    tree = HTMLParser(html)

    article = tree.css_first("article")

    if article is None:
        raise ValueError("Article not found")

    clean_article(article)

    converter = html2text.HTML2Text()
    converter.body_width = 0

    return converter.handle(article.html)
```

---

# 19. Test

HTML:

```python
html = """
<html>
<body>

<nav>
    Home | Login
</nav>

<article>

<h1>Python</h1>

<div class="ads">
    Advertisement
</div>

<p>
Python <strong>rất mạnh</strong>.
</p>

<script>
    alert("tracking");
</script>

<p>
Python dùng được cho crawler.
</p>

</article>

<footer>
    Copyright 2026
</footer>

</body>
</html>
"""
```

Chạy:

```python
print(convert_html_to_markdown(html))
```

Ta kỳ vọng:

```markdown
# Python

Python **rất mạnh**.

Python dùng được cho crawler.
```

---

# 20. Một chi tiết cực kỳ quan trọng

Ta **không remove `nav` và `footer` trước khi extract article**.

Vì:

```text
Raw HTML
    ↓
Extract article
    ↓
Clean article
```

Nếu:

```text
article
```

đã nằm trong vùng nội dung chính thì:

```text
nav
footer
aside
```

thường đã nằm ngoài boundary.

Đây là một cách giảm công việc cho cleaner.

---

# 21. Selectolax vs BeautifulSoup

| Công việc             | BeautifulSoup | Selectolax    |
| --------------------- | ------------- | ------------- |
| Parse HTML            | ✅             | ✅             |
| CSS selector          | ✅             | ✅             |
| `find()`              | ✅             | Có API khác   |
| `select_one()`        | ✅             | `css_first()` |
| `select()`            | ✅             | `css()`       |
| DOM manipulation      | ✅             | ✅             |
| Dễ học                | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐          |
| Crawler hiệu năng cao | ⭐⭐⭐           | ⭐⭐⭐⭐⭐         |
| HTML → Markdown       | ❌             | ❌             |
| Markdown conversion   | `html2text`   | `html2text`   |

Điểm cuối cùng:

> **Cả BeautifulSoup lẫn Selectolax đều không phải Markdown converter.**

---

# 22. Vai trò của `html2text` vẫn giữ nguyên

Ta có:

```text
                 HTML
                  │
                  ▼
          ┌───────────────┐
          │   Selectolax  │
          │               │
          │ extract       │
          │ clean         │
          │ manipulate    │
          └───────┬───────┘
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

Đây là architecture chúng ta muốn giữ.

---

# 23. Kết hợp HTTPX

Bây giờ thêm HTTPX:

```python
import httpx
from selectolax.parser import HTMLParser
import html2text
```

Fetcher:

```python
def fetch(url: str) -> str:
    response = httpx.get(url)
    response.raise_for_status()

    return response.text
```

Sau đó:

```python
html = fetch(url)

markdown = convert_html_to_markdown(html)
```

Pipeline:

```text
URL
 ↓
HTTPX
 ↓
HTML
 ↓
Selectolax
 ↓
Article
 ↓
Clean
 ↓
html2text
 ↓
Markdown
```

---

# 24. Nhưng đừng dùng `httpx.get()` trực tiếp trong architecture cuối cùng

Về sau nên:

```text
Fetcher
```

chịu trách nhiệm HTTP.

```text
Parser
```

chịu trách nhiệm HTML.

```text
Cleaner
```

chịu trách nhiệm cleaning.

```text
Converter
```

chịu trách nhiệm Markdown.

Ví dụ:

```text
Fetcher
   ↓
str
   ↓
ArticleExtractor
   ↓
Node / HTML
   ↓
HTMLCleaner
   ↓
str
   ↓
MarkdownConverter
   ↓
str
```

---

# 25. Một thiết kế tốt

### Extractor

```python
class ArticleExtractor:

    def extract(self, html: str):
        tree = HTMLParser(html)

        article = tree.css_first("article")

        if article is None:
            raise ValueError("Article not found")

        return article
```

### Cleaner

```python
class HTMLCleaner:

    SELECTORS = [
        "script",
        "style",
        ".ads",
        ".advertisement",
    ]

    def clean(self, article) -> None:
        for selector in self.SELECTORS:
            for node in article.css(selector):
                node.decompose()
```

### Converter

```python
class MarkdownConverter:

    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.body_width = 0

    def convert(self, article) -> str:
        return self.converter.handle(article.html)
```

---

# 26. Composition

```python
extractor = ArticleExtractor()
cleaner = HTMLCleaner()
converter = MarkdownConverter()

article = extractor.extract(html)

cleaner.clean(article)

markdown = converter.convert(article)
```

Rất rõ ràng:

```text
Extractor
    ↓
Cleaner
    ↓
Converter
```

---

# 27. Tại sao truyền Node giữa các layer?

Có hai lựa chọn.

### Option A

```text
Extractor
 ↓
Node
 ↓
Cleaner
 ↓
Node
 ↓
Converter
 ↓
HTML
```

### Option B

```text
Extractor
 ↓
HTML string
 ↓
Cleaner
 ↓
HTML string
 ↓
Converter
```

Trong giai đoạn này tôi khuyên bạn hiểu cả hai.

Nhưng khi cleaning bằng Selectolax, giữ:

```text
Node
```

trong quá trình DOM manipulation rất tiện.

Cuối cùng mới:

```python
article.html
```

để giao cho `html2text`.

---

# 28. Boundary rất đẹp

```text
                 Selectolax world
────────────────────────────────────────

HTML
 ↓
Parser
 ↓
Node
 ↓
Extract
 ↓
Remove
 ↓
Clean Node


────────────────────────────────────────
                Boundary
                    ↓

               article.html

────────────────────────────────────────

              html2text world
                    ↓
                Markdown
```

Boundary này rất đáng nhớ.

---

# 29. Không convert quá sớm

Sai:

```python
markdown = html2text.html2text(html)

# sau đó mới cố remove ads
```

Lúc này:

```text
HTML structure
```

đã trở thành:

```text
Markdown
```

Việc remove DOM element không còn dễ.

Đúng:

```text
HTML
 ↓
Selectolax
 ↓
Extract
 ↓
Clean
 ↓
html2text
 ↓
Markdown
```

---

# 30. Không lấy `.text()` quá sớm

Sai:

```python
article_text = article.text()
markdown = converter.handle(article_text)
```

Vì:

```text
<h1>
<strong>
<em>
<a>
<ul>
<code>
```

đều có thể mất semantic.

Đúng:

```python
clean_html = article.html

markdown = converter.handle(clean_html)
```

---

# 31. Đây là nguyên tắc rất quan trọng

Trong pipeline:

```text
HTML
```

là **rich representation**.

```text
plain text
```

là **poor representation**.

Một khi:

```text
HTML
 ↓
plain text
```

thì rất khó phục hồi:

```text
heading
bold
italic
link
list
code
```

Do đó:

> **Giữ representation giàu thông tin càng lâu càng tốt.**

---

# 32. Ví dụ

HTML:

```html
<h1>Python</h1>

<p>
Python <strong>rất mạnh</strong>.
</p>

<ul>
    <li>Web</li>
    <li>Data</li>
</ul>
```

Rich representation:

```text
heading
paragraph
strong
list
list item
```

Nếu `.text()`:

```text
Python

Python rất mạnh.

Web
Data
```

Semantic đã mất.

---

# 33. Selectolax rất hợp với crawler

Đặc biệt pipeline của chúng ta:

```text
HTTPX
 ↓
Selectolax
 ↓
Article extraction
 ↓
Cleaner
```

Bởi vì parser và CSS selector nằm ngay trong layer crawling.

Sau đó:

```text
Clean HTML
 ↓
html2text
```

đảm nhận conversion.

---

# 34. Bài tập 1 — Parse

Viết:

```python
def parse(html: str):
    ...
```

trả về:

```python
HTMLParser
```

Test:

```python
tree = parse("<h1>Python</h1>")

print(tree.css_first("h1").text())
```

---

# 35. Bài tập 2 — Extract

Viết:

```python
def extract_article(tree):
    ...
```

Input:

```html
<html>
<body>

<header>Website</header>

<article class="story">
    <h1>Python</h1>
    <p>Hello</p>
</article>

<footer>Copyright</footer>

</body>
</html>
```

Kết quả phải là node:

```text
article.story
```

---

# 36. Bài tập 3 — Remove

HTML:

```html
<article>

<h1>Python</h1>

<div class="ads">
    BUY NOW
</div>

<p>Hello</p>

<script>
    tracking()
</script>

</article>
```

Viết:

```python
def clean_article(article):
    ...
```

Xóa:

```text
.ads
script
```

---

# 37. Bài tập 4 — HTML → Markdown

Viết:

```python
def convert(article) -> str:
    ...
```

Không được dùng:

```python
article.text()
```

Mà phải giữ:

```text
article.html
```

rồi:

```text
html2text
```

---

# 38. Bài tập 5 — Full pipeline

Viết:

```python
def process(html: str) -> str:
    ...
```

Pipeline bắt buộc:

```text
HTML
 ↓
HTMLParser
 ↓
css_first("article")
 ↓
remove unwanted nodes
 ↓
article.html
 ↓
HTML2Text
 ↓
Markdown
```

---

# 39. Bài tập 6 — Debug

Hãy in:

```python
print("ARTICLE HTML")
print(article.html)

print("=" * 50)

print("MARKDOWN")
print(markdown)
```

Mục tiêu là phân biệt:

```text
Selectolax làm gì?
```

với:

```text
html2text làm gì?
```

---

# 40. Bài tập 7 — So sánh BeautifulSoup và Selectolax

Cùng một HTML:

```html
<article class="story">
    <h1>Python</h1>
    <p>Hello</p>
</article>
```

Viết hai implementation:

```python
def extract_bs4(html: str):
    ...
```

và:

```python
def extract_selectolax(html: str):
    ...
```

Sau đó so sánh:

```text
API
code length
readability
serialization
performance
```

---

# 41. Bài tập 8 — Benchmark

Đây là bài tập rất đáng làm.

Tạo HTML lớn:

```python
html = """
<article>
""" + "<p>Hello Python</p>" * 10000 + """
</article>
"""
```

Sau đó benchmark:

```python
from time import perf_counter
```

So sánh:

```text
BeautifulSoup
vs
Selectolax
```

Ví dụ concept:

```python
start = perf_counter()

# parse

elapsed = perf_counter() - start

print(elapsed)
```

Chạy nhiều lần thay vì chỉ một lần.

---

# 42. Một lưu ý về benchmark

Đừng kết luận:

```text
"Selectolax nhanh hơn X lần"
```

chỉ từ một lần chạy.

Benchmark đúng cần:

```text
warm-up
multiple iterations
same input
same machine
same operation
```

Sau này khi học performance Python, chúng ta sẽ làm kỹ hơn.

---

# 43. Architecture cuối buổi

Tôi muốn bạn ghi nhớ architecture này:

```text
                    HTTPX
                      │
                      ▼
                   HTML
                      │
                      ▼
             ┌────────────────┐
             │   Selectolax   │
             └───────┬────────┘
                     │
                     ▼
              Extract article
                     │
                     ▼
              Clean DOM nodes
                     │
                     ▼
                article.html
                     │
                     ▼
             ┌────────────────┐
             │    html2text   │
             └───────┬────────┘
                     │
                     ▼
                  Markdown
```

---

# 44. Hai thư viện — hai trách nhiệm

### Selectolax

```text
HTML
 ↓
Parse
 ↓
Find
 ↓
Extract
 ↓
Remove
 ↓
Modify
```

### html2text

```text
Clean HTML
 ↓
Interpret HTML semantics
 ↓
Markdown
```

Không nên đảo ngược hai nhiệm vụ.

---

# 45. Một insight quan trọng hơn

Bạn đang bắt đầu hình thành một **compiler-like pipeline**:

```text
Source
  ↓
Parsing
  ↓
Transformation
  ↓
Rendering
  ↓
Output
```

Cụ thể:

```text
HTML
 ↓
Selectolax parser
 ↓
DOM
 ↓
Cleaning / extraction
 ↓
Clean HTML
 ↓
html2text
 ↓
Markdown
```

Đây chính là tư duy rất tốt khi xây scraper chuyên nghiệp.

---

## Kết thúc Buổi 14

Bạn cần nắm chắc 5 điểm:

```text
1. Selectolax dùng để parse/manipulate HTML.

2. html2text dùng để HTML → Markdown.

3. Không gọi article.text() nếu muốn giữ Markdown semantics.

4. Giữ DOM càng lâu càng tốt.

5. Chỉ serialize article.html ngay trước khi đưa vào html2text.
```

Pipeline chuẩn:

```text
HTTPX
  ↓
HTML
  ↓
Selectolax
  ↓
Extract
  ↓
Clean
  ↓
article.html
  ↓
html2text
  ↓
Markdown
```

**Buổi 15** chúng ta sẽ xây `HTMLCleaner` thành một component thực sự:

```text
HTMLCleaner
│
├── remove_scripts()
├── remove_styles()
├── remove_ads()
├── remove_navigation()
├── remove_social()
├── remove_comments()
└── clean()
```

và quan trọng hơn, chúng ta sẽ thiết kế nó sao cho **không biến thành một God Object** khi số lượng rule cleaning tăng lên.
