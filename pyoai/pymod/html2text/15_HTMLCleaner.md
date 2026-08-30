# Buổi 15 — Xây dựng `HTMLCleaner`

Từ Buổi 13–14, chúng ta đã có:

```text
HTML
 ↓
BeautifulSoup / Selectolax
 ↓
Extract article
 ↓
html2text
 ↓
Markdown
```

Hôm nay chúng ta **tách riêng phần cleaning** thành một component có thể tái sử dụng:

```text
HTML
 ↓
Parser
 ↓
HTMLCleaner
 ↓
Clean HTML
 ↓
html2text
 ↓
Markdown
```

Mục tiêu cuối buổi:

```python
cleaner = HTMLCleaner()

clean_html = cleaner.clean(html)
markdown = converter.convert(clean_html)
```

---

# 1. HTML Cleaner là gì?

`HTMLCleaner` không có nhiệm vụ:

```text
HTML → Markdown
```

Nó chỉ có nhiệm vụ:

```text
Dirty HTML
    ↓
Clean HTML
```

Ví dụ:

```html
<article>

    <h1>Python</h1>

    <div class="advertisement">
        Buy now!
    </div>

    <p>Hello Python.</p>

    <script>
        tracking();
    </script>

</article>
```

Sau cleaning:

```html
<article>

    <h1>Python</h1>

    <p>Hello Python.</p>

</article>
```

Sau đó mới:

```text
Clean HTML
    ↓
html2text
    ↓
Markdown
```

---

# 2. Tại sao phải tách Cleaner?

Nếu viết tất cả trong một function:

```python
def html_to_markdown(html):
    tree = HTMLParser(html)

    article = tree.css_first("article")

    for node in article.css("script"):
        node.decompose()

    for node in article.css(".ads"):
        node.decompose()

    ...

    converter = html2text.HTML2Text()

    return converter.handle(article.html)
```

ban đầu nhìn khá ổn.

Nhưng vài tuần sau:

```text
script
style
ads
popup
social
comments
related
navigation
newsletter
tracking
recommendation
```

function sẽ phình ra.

Ta muốn:

```text
Extractor
    ↓
Cleaner
    ↓
Converter
```

---

# 3. Responsibility

Hãy xác định rõ:

### Extractor

```text
Tìm vùng nội dung chính
```

### Cleaner

```text
Loại bỏ thành phần không mong muốn
```

### Converter

```text
HTML → Markdown
```

Ví dụ:

```text
ArticleExtractor
        │
        ▼
   article node
        │
        ▼
   HTMLCleaner
        │
        ▼
 clean article node
        │
        ▼
 MarkdownConverter
        │
        ▼
     Markdown
```

---

# 4. Tạo `HTMLCleaner`

Bắt đầu đơn giản:

```python
from selectolax.parser import HTMLParser


class HTMLCleaner:

    REMOVE_SELECTORS = [
        "script",
        "style",
        "nav",
        "footer",
        ".ads",
        ".advertisement",
    ]

    def clean(self, html: str) -> str:
        tree = HTMLParser(html)

        for selector in self.REMOVE_SELECTORS:
            for node in tree.css(selector):
                node.decompose()

        return tree.html
```

Nhưng có một vấn đề architecture.

---

# 5. Cleaner có nên extract article không?

Nếu class làm:

```python
cleaner.clean()
```

mà bên trong:

```python
find article
remove ads
remove nav
remove footer
extract title
remove comments
...
```

thì nó bắt đầu có quá nhiều responsibility.

Tốt hơn:

```text
ArticleExtractor
       ↓
HTMLCleaner
```

---

# 6. Tách `ArticleExtractor`

```python
class ArticleExtractor:

    SELECTORS = [
        "article",
        ".article-content",
        ".post-content",
        "#content",
    ]

    def extract(self, html: str):
        tree = HTMLParser(html)

        for selector in self.SELECTORS:
            node = tree.css_first(selector)

            if node is not None:
                return node

        raise ValueError("Article not found")
```

Bây giờ:

```text
ArticleExtractor
    =
"Article nằm ở đâu?"
```

Còn:

```text
HTMLCleaner
    =
"Cái gì cần loại bỏ?"
```

Hai câu hỏi khác nhau.

---

# 7. Cleaner nhận Node

Ta có:

```python
article = extractor.extract(html)
```

Sau đó:

```python
cleaner.clean(article)
```

Cleaner:

```python
class HTMLCleaner:

    REMOVE_SELECTORS = [
        "script",
        "style",
        ".ads",
        ".advertisement",
    ]

    def clean(self, root) -> None:
        for selector in self.REMOVE_SELECTORS:
            for node in root.css(selector):
                node.decompose()
```

Chú ý:

```python
-> None
```

vì cleaner đang **modify node trực tiếp**.

---

# 8. Mutable DOM

Đây là concept cần hiểu.

```python
article = extractor.extract(html)
```

`article` là object đại diện cho DOM node.

Khi:

```python
cleaner.clean(article)
```

Cleaner thay đổi chính object đó.

Trước:

```text
article
 ├── h1
 ├── ads
 ├── p
 └── script
```

Sau:

```text
article
 ├── h1
 └── p
```

Không nhất thiết phải:

```python
article = cleaner.clean(article)
```

---

# 9. Hai kiểu API

### Mutable API

```python
cleaner.clean(article)
```

Cleaner sửa trực tiếp.

### Functional API

```python
clean_article = cleaner.clean(article)
```

Cleaner tạo output mới.

Với DOM parser như Selectolax, mutable approach thường đơn giản và hiệu quả hơn.

---

# 10. Nhưng API `clean()` có thể trả lại node

Bạn cũng có thể:

```python
def clean(self, root):
    ...

    return root
```

Sau đó:

```python
article = cleaner.clean(article)
```

Cách này tiện cho chaining.

Ví dụ:

```python
article = (
    cleaner
    .clean(article)
)
```

Nhưng về semantic, nếu object được mutate thì việc return chính nó không bắt buộc.

---

# 11. Tôi khuyên API nào?

Trong project crawler:

```python
cleaner.clean(article)
```

là đủ rõ ràng.

Ví dụ:

```python
article = extractor.extract(html)

cleaner.clean(article)

markdown = converter.convert(article.html)
```

Đọc rất tự nhiên.

---

# 12. Rule cleaning

Hiện tại:

```python
REMOVE_SELECTORS = [
    "script",
    "style",
    "nav",
    "footer",
    ".ads",
    ".advertisement",
]
```

Nhưng đây mới chỉ là một danh sách.

Hãy coi nó là:

```text
Cleaning Rules
```

---

# 13. Phân loại rule

Không phải mọi thứ đều giống nhau.

### Structural

```text
script
style
nav
footer
aside
```

### Advertisement

```text
.ads
.ad
.advertisement
.sponsor
```

### Social

```text
.share
.social
.share-buttons
```

### Recommendation

```text
.related
.related-posts
.recommended
```

### Comments

```text
.comments
.comment-section
```

Ta nên phân loại chúng.

---

# 14. Configuration

Thay vì hard-code:

```python
class HTMLCleaner:

    REMOVE_SELECTORS = [...]
```

có thể:

```python
class HTMLCleaner:

    def __init__(self, remove_selectors=None):
        self.remove_selectors = remove_selectors or []

    def clean(self, root):
        for selector in self.remove_selectors:
            for node in root.css(selector):
                node.decompose()
```

Dùng:

```python
cleaner = HTMLCleaner(
    remove_selectors=[
        "script",
        "style",
        ".ads",
    ]
)
```

---

# 15. Nhưng có một vấn đề với `or []`

Nếu truyền:

```python
remove_selectors=[]
```

thì:

```python
remove_selectors or []
```

vẫn tạo list mới.

Không nghiêm trọng ở đây, nhưng về Python API design, tốt hơn:

```python
def __init__(self, remove_selectors=None):
    if remove_selectors is None:
        remove_selectors = []

    self.remove_selectors = list(remove_selectors)
```

---

# 16. Vì sao `list()`?

Giả sử caller truyền:

```python
selectors = (
    "script",
    "style",
    ".ads",
)
```

Ta muốn internal state luôn là list:

```python
self.remove_selectors = list(selectors)
```

Kết quả:

```python
[
    "script",
    "style",
    ".ads",
]
```

---

# 17. Cleaner hoàn chỉnh phiên bản 1

```python
from selectolax.parser import HTMLParser


class HTMLCleaner:

    DEFAULT_SELECTORS = [
        "script",
        "style",
        "nav",
        "footer",
        ".ads",
        ".advertisement",
    ]

    def __init__(self, remove_selectors=None):
        if remove_selectors is None:
            remove_selectors = self.DEFAULT_SELECTORS

        self.remove_selectors = list(remove_selectors)

    def clean(self, root) -> None:
        for selector in self.remove_selectors:
            for node in root.css(selector):
                node.decompose()
```

---

# 18. Test

```python
html = """
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
"""
```

Parse:

```python
tree = HTMLParser(html)

article = tree.css_first("article")
```

Clean:

```python
cleaner = HTMLCleaner()

cleaner.clean(article)
```

Kiểm tra:

```python
print(article.html)
```

---

# 19. Kết quả mong muốn

```html
<article>
<h1>Python</h1>

<p>Hello Python.</p>

<p>Python is powerful.</p>

</article>
```

Không còn:

```html
<div class="ads">
```

và:

```html
<script>
```

---

# 20. Sau đó mới dùng html2text

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 0

markdown = converter.handle(article.html)

print(markdown)
```

Pipeline:

```text
HTML
 ↓
Selectolax
 ↓
Article
 ↓
HTMLCleaner
 ↓
Clean Article
 ↓
article.html
 ↓
html2text
 ↓
Markdown
```

---

# 21. Tạo `MarkdownConverter`

Để architecture rõ hơn:

```python
class MarkdownConverter:

    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.body_width = 0

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

---

# 22. Full architecture

```python
extractor = ArticleExtractor()
cleaner = HTMLCleaner()
converter = MarkdownConverter()

article = extractor.extract(html)

cleaner.clean(article)

markdown = converter.convert(article.html)

print(markdown)
```

Đây là code rất dễ đọc.

---

# 23. Tách `Cleaner` thành các method

Khi project lớn hơn:

```python
class HTMLCleaner:

    def remove_scripts(self, root):
        ...

    def remove_styles(self, root):
        ...

    def remove_ads(self, root):
        ...

    def remove_navigation(self, root):
        ...

    def clean(self, root):
        ...
```

Ví dụ:

```python
class HTMLCleaner:

    def remove_scripts(self, root):
        for node in root.css("script"):
            node.decompose()

    def remove_styles(self, root):
        for node in root.css("style"):
            node.decompose()

    def remove_ads(self, root):
        for node in root.css(".ads, .advertisement"):
            node.decompose()

    def clean(self, root):
        self.remove_scripts(root)
        self.remove_styles(root)
        self.remove_ads(root)
```

---

# 24. Ưu điểm

Ta có thể test riêng:

```python
cleaner.remove_scripts(article)
```

hoặc:

```python
cleaner.remove_ads(article)
```

Nhưng cũng có nhược điểm.

Nếu có 30 loại rule:

```text
remove_scripts()
remove_styles()
remove_ads()
remove_nav()
remove_footer()
remove_sidebar()
remove_comments()
remove_social()
...
```

class lại trở nên rất lớn.

Đây chính là vấn đề chúng ta sẽ giải quyết sau.

---

# 25. Rule-based Cleaner

Một hướng tốt hơn:

```text
HTMLCleaner
     │
     ├── Rule 1
     ├── Rule 2
     ├── Rule 3
     └── Rule 4
```

Ví dụ:

```python
class RemoveSelectorRule:

    def __init__(self, selector: str):
        self.selector = selector

    def apply(self, root) -> None:
        for node in root.css(self.selector):
            node.decompose()
```

---

# 26. Rule

Tạo:

```python
rule = RemoveSelectorRule(".ads")
```

Apply:

```python
rule.apply(article)
```

DOM:

```text
article
 ├── h1
 ├── ads  ← removed
 └── p
```

---

# 27. Nhiều rule

```python
rules = [
    RemoveSelectorRule("script"),
    RemoveSelectorRule("style"),
    RemoveSelectorRule(".ads"),
    RemoveSelectorRule(".share"),
]
```

Cleaner:

```python
class HTMLCleaner:

    def __init__(self, rules):
        self.rules = list(rules)

    def clean(self, root) -> None:
        for rule in self.rules:
            rule.apply(root)
```

---

# 28. Đây là một bước architecture rất quan trọng

Bây giờ:

```text
HTMLCleaner
```

không cần biết:

```text
ads
script
style
share
```

Nó chỉ biết:

```text
Rule
 ↓
apply(root)
```

Đây chính là tư duy:

> **Open/Closed Principle**

Cleaner có thể mở rộng bằng rule mới mà không cần sửa logic `clean()`.

---

# 29. Ví dụ thêm rule

```python
class RemoveSelectorRule:

    def __init__(self, selector):
        self.selector = selector

    def apply(self, root):
        for node in root.css(self.selector):
            node.decompose()
```

Tạo:

```python
rules = [
    RemoveSelectorRule("script"),
    RemoveSelectorRule("style"),
    RemoveSelectorRule(".ads"),
    RemoveSelectorRule(".comments"),
    RemoveSelectorRule(".share-buttons"),
]
```

Cleaner không thay đổi:

```python
cleaner = HTMLCleaner(rules)

cleaner.clean(article)
```

---

# 30. Nhưng đừng over-engineer quá sớm

Ở Buổi 15, chúng ta chỉ cần hiểu hai cấp độ:

### Level 1

```python
HTMLCleaner
    ↓
selectors
```

### Level 2

```python
HTMLCleaner
    ↓
Cleaning Rules
```

Chưa cần xây framework rule quá phức tạp.

---

# 31. Một vấn đề rất thực tế: Selector sai

Giả sử:

```python
".content"
```

trùng với:

```html
<div class="content">
    Article
</div>
```

nhưng cũng:

```html
<div class="content">
    Advertisement
</div>
```

Nếu:

```python
root.css(".content")
```

thì có thể xóa cả nội dung chính.

Đây là lý do:

> **Cleaning rule phải cực kỳ thận trọng.**

---

# 32. Không nên dùng selector quá rộng

Ví dụ:

```python
".content"
```

nguy hiểm.

Tốt hơn:

```python
".article-content .advertisement"
```

hoặc:

```python
"article .advertisement"
```

Selector càng chính xác càng tốt.

---

# 33. Cẩn thận với `aside`

Có website:

```html
<article>
    <aside>
        Author information
    </aside>
</article>
```

Nếu:

```python
root.css("aside")
```

và remove, bạn có thể mất metadata hữu ích.

Do đó:

```text
remove aside
```

không phải universal rule.

---

# 34. Cleaner không nên "đoán" quá nhiều

Một Cleaner tốt:

```text
Rule rõ ràng
   ↓
Apply
```

Không nên:

```text
AI-like guessing
   ↓
Xóa những gì "có vẻ là quảng cáo"
```

Ở giai đoạn đầu, hãy dùng:

```text
CSS selectors
```

và cấu hình theo từng website.

---

# 35. Site-specific configuration

Đây là kiến trúc rất quan trọng cho crawler.

Website A:

```python
HTMLCleaner([
    RemoveSelectorRule(".ads"),
    RemoveSelectorRule(".share"),
])
```

Website B:

```python
HTMLCleaner([
    RemoveSelectorRule(".advertisement"),
    RemoveSelectorRule(".comments"),
])
```

Website C:

```python
HTMLCleaner([
    RemoveSelectorRule("#sidebar"),
])
```

Cleaner engine giống nhau.

Rules khác nhau.

---

# 36. Đây chính là Plugin/Strategy mindset

```text
Cleaner Engine
      │
      ├── Site A Rules
      ├── Site B Rules
      └── Site C Rules
```

Sau này crawler của bạn có thể có:

```text
SourceAdapter
   │
   ├── SourceA
   │      ├── extractor
   │      └── cleaner rules
   │
   ├── SourceB
   │      ├── extractor
   │      └── cleaner rules
   │
   └── SourceC
```

Rất phù hợp với project crawler truyện của bạn.

---

# 37. Một thiết kế tôi khuyên dùng

Ở thời điểm này:

```text
ArticleExtractor
        ↓
HTMLCleaner
        ↓
MarkdownConverter
```

Trong đó:

```text
ArticleExtractor
    = WHERE

HTMLCleaner
    = REMOVE

MarkdownConverter
    = RENDER
```

Ba từ này rất dễ nhớ:

```text
WHERE
REMOVE
RENDER
```

---

# 38. Full example

```python
import html2text

from selectolax.parser import HTMLParser


class ArticleExtractor:

    SELECTORS = [
        "article",
        ".article-content",
        ".post-content",
    ]

    def extract(self, html: str):
        tree = HTMLParser(html)

        for selector in self.SELECTORS:
            article = tree.css_first(selector)

            if article is not None:
                return article

        raise ValueError("Article not found")


class HTMLCleaner:

    REMOVE_SELECTORS = [
        "script",
        "style",
        ".ads",
        ".advertisement",
        ".share-buttons",
    ]

    def clean(self, root) -> None:
        for selector in self.REMOVE_SELECTORS:
            for node in root.css(selector):
                node.decompose()


class MarkdownConverter:

    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.body_width = 0

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

---

# 39. Application

```python
extractor = ArticleExtractor()
cleaner = HTMLCleaner()
converter = MarkdownConverter()

article = extractor.extract(html)

cleaner.clean(article)

markdown = converter.convert(article.html)

print(markdown)
```

Đây đã là một pipeline khá sạch.

---

# 40. Thêm HTTPX

Sau này:

```python
import httpx


def fetch(url: str) -> str:
    response = httpx.get(url)
    response.raise_for_status()

    return response.text
```

Application:

```python
html = fetch(url)

article = extractor.extract(html)

cleaner.clean(article)

markdown = converter.convert(article.html)
```

Pipeline:

```text
             URL
              │
              ▼
            HTTPX
              │
              ▼
             HTML
              │
              ▼
     ArticleExtractor
              │
              ▼
          Article
              │
              ▼
        HTMLCleaner
              │
              ▼
       Clean Article
              │
              ▼
     MarkdownConverter
              │
              ▼
          Markdown
```

---

# 41. Một nguyên tắc architecture

Không nên để `MarkdownConverter` làm:

```python
converter.convert(url)
```

hoặc:

```python
converter.convert(raw_html)
```

nếu application muốn đảm bảo HTML đã được clean.

Tốt hơn:

```python
clean_html = cleaner.clean(...)

markdown = converter.convert(clean_html)
```

Mỗi component có input/output rõ ràng.

---

# 42. Testing

Bây giờ component có thể test độc lập.

### Test Cleaner

```python
def test_remove_script():
    ...
```

### Test Extractor

```python
def test_extract_article():
    ...
```

### Test Converter

```python
def test_convert_bold():
    ...
```

Đây là một lợi ích cực lớn của separation.

---

# 43. Test Cleaner đơn giản

Ví dụ:

```python
def test_cleaner():
    html = """
    <article>
        <h1>Python</h1>

        <script>
            alert("x")
        </script>

        <p>Hello</p>
    </article>
    """

    tree = HTMLParser(html)

    article = tree.css_first("article")

    cleaner = HTMLCleaner()
    cleaner.clean(article)

    result = article.html

    assert "<script" not in result
    assert "Hello" in result
    assert "Python" in result
```

Đây là **structural test**.

---

# 44. Test Markdown riêng

```python
def test_converter():
    converter = MarkdownConverter()

    html = "<strong>Python</strong>"

    result = converter.convert(html)

    assert "Python" in result
```

Cleaner không xuất hiện trong test này.

Converter cũng không biết Cleaner tồn tại.

Đó chính là loose coupling.

---

# 45. Bài tập 1 — `HTMLCleaner`

Viết:

```python
class HTMLCleaner:

    REMOVE_SELECTORS = [
        "script",
        "style",
        ".ads",
    ]

    def clean(self, root):
        ...
```

Test với:

```html
<article>
    <h1>Python</h1>

    <script>tracking()</script>

    <div class="ads">
        Advertisement
    </div>

    <p>Hello</p>
</article>
```

Kết quả không được chứa:

```text
tracking
Advertisement
```

---

# 46. Bài tập 2 — Custom selectors

Cho phép:

```python
cleaner = HTMLCleaner(
    remove_selectors=[
        "script",
        ".my-ad",
    ]
)
```

Test:

```html
<div class="my-ad">
    Buy now
</div>
```

phải bị remove.

---

# 47. Bài tập 3 — Extract + Clean

Xây:

```python
extractor = ArticleExtractor()
cleaner = HTMLCleaner()
```

Pipeline:

```text
HTML
 ↓
extractor.extract()
 ↓
article
 ↓
cleaner.clean()
 ↓
article.html
```

---

# 48. Bài tập 4 — Clean + html2text

Xây:

```python
converter = MarkdownConverter()
```

Pipeline hoàn chỉnh:

```text
HTML
 ↓
Extract
 ↓
Clean
 ↓
Serialize
 ↓
html2text
 ↓
Markdown
```

---

# 49. Bài tập 5 — Kiểm tra semantic

HTML:

```html
<article>

<h1>Python</h1>

<p>
Python <strong>rất mạnh</strong>.
</p>

<div class="ads">
    Advertisement
</div>

</article>
```

Sau pipeline phải giữ:

```markdown
# Python

Python **rất mạnh**.
```

và loại:

```text
Advertisement
```

Đây là test rất tốt vì kiểm tra cả:

```text
Cleaner
+
html2text
```

---

# 50. Bài tập 6 — Thiết kế rule

Viết:

```python
class RemoveSelectorRule:
    ...
```

API:

```python
rule = RemoveSelectorRule(".ads")

rule.apply(article)
```

Sau đó:

```python
rules = [
    RemoveSelectorRule("script"),
    RemoveSelectorRule("style"),
    RemoveSelectorRule(".ads"),
]
```

và:

```python
cleaner = HTMLCleaner(rules)
```

Đây là bài tập quan trọng nhất của Buổi 15.

---

# 51. Bài tập 7 — Site-specific cleaner

Tạo:

```python
source_a_cleaner
source_b_cleaner
```

Ví dụ:

```text
Source A
    .ads
    .share

Source B
    .advertisement
    .comments
```

Cả hai sử dụng chung:

```python
HTMLCleaner
```

nhưng rules khác nhau.

---

# 52. Sai lầm cần tránh

### Sai 1

```python
article.text()
```

quá sớm.

→ mất HTML semantic.

### Sai 2

```python
html2text.html2text(raw_html)
```

trước cleaning.

→ quảng cáo/navigation lọt vào Markdown.

### Sai 3

Selector quá rộng:

```python
".content"
```

→ có thể xóa content thật.

### Sai 4

Cleaner tự convert Markdown.

→ vi phạm responsibility.

### Sai 5

Một class làm tất cả:

```text
fetch
parse
extract
clean
convert
save
```

→ God Object.

---

# 53. Mental model Buổi 15

Hãy nhớ:

```text
              Raw HTML
                  │
                  ▼
          ArticleExtractor
                  │
                  │ WHERE?
                  ▼
              Article
                  │
                  ▼
             HTMLCleaner
                  │
                  │ REMOVE
                  ▼
           Clean Article
                  │
                  ▼
            article.html
                  │
                  ▼
         MarkdownConverter
                  │
                  │ RENDER
                  ▼
              Markdown
```

Ba responsibility:

```text
Extractor → WHERE
Cleaner   → REMOVE
Converter → RENDER
```

---

# 54. Kiến trúc sau Buổi 15

Chúng ta đã đi từ:

```text
HTML → html2text
```

thành:

```text
HTML
 ↓
Selectolax
 ↓
ArticleExtractor
 ↓
HTMLCleaner
 ↓
MarkdownConverter
 ↓
Markdown
```

Đây là nền móng cho các buổi tiếp theo.

---

## Tiếp theo — Buổi 16: Remove quảng cáo

Buổi 16 chúng ta sẽ đi sâu vào vấn đề **khó hơn rất nhiều so với `script`/`style`**:

```text
<div class="ads">
<div class="advertisement">
<div id="google_ads">
<aside class="sponsor">
<div data-ad="true">
```

và đặc biệt:

```text
class="box"
class="content"
class="sidebar"
```

không phải lúc nào cũng cho biết element đó là quảng cáo.

Chúng ta sẽ học:

```text
CSS selector
        ↓
class/id heuristic
        ↓
attribute heuristic
        ↓
parent/child relationship
        ↓
multiple rules
        ↓
site-specific rules
```

để xây một **Ad Removal Strategy** an toàn hơn, thay vì đơn giản:

```python
for node in root.css(".ads"):
    node.decompose()
```
