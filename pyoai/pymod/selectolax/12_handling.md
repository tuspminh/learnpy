# 📘 Selectolax — Buổi 12: Error Handling

Đây là buổi rất quan trọng nếu bạn muốn dùng Selectolax để xây **scraper thực tế**.

Trong demo, HTML thường đẹp:

```html
<h1 class="title">Python</h1>
```

Nhưng website thực tế có thể:

```text
selector không tồn tại
HTML bị lỗi
response rỗng
encoding sai
attribute không có
content bị thiếu
website thay đổi cấu trúc
```

Mục tiêu hôm nay:

```text
HTML
 ↓
Selectolax
 ↓
Defensive Extraction
 ↓
Không crash
 ↓
Data hoặc None
```

---

# 1. Tư duy quan trọng nhất

Scraper phải coi HTML bên ngoài là **untrusted input**.

Không được giả định:

```python
node = tree.css_first(".title")
```

luôn trả về node.

Phải nghĩ:

```text
Có thể có
Có thể không
```

Vì vậy:

```python
node = tree.css_first(".title")

if node is None:
    ...
```

là pattern cơ bản nhất của scraper.

---

# 2. Missing selector

HTML:

```html
<article>
    <h1>Python</h1>
</article>
```

Nhưng code:

```python
title = tree.css_first(".title")
```

Không có `.title`.

Kết quả:

```python
None
```

Không phải exception.

---

# 3. Sai lầm phổ biến

Sai:

```python
title = tree.css_first(".title")

print(title.text())
```

Nếu selector không tồn tại:

```text
AttributeError
```

vì:

```python
title is None
```

---

# 4. Cách an toàn

```python
title = tree.css_first(".title")

if title is None:
    return None

return title.text(strip=True)
```

Đây là:

> **Defensive extraction**

---

# 5. Helper đầu tiên

Ta có thể viết:

```python
def get_text(node):
    if node is None:
        return None

    return node.text(strip=True)
```

Sau đó:

```python
title = get_text(
    tree.css_first(".title")
)
```

Rất sạch.

---

# 6. Nhưng có một vấn đề

Nếu:

```html
<h1 class="title"></h1>
```

thì:

```python
node.text(strip=True)
```

có thể trả:

```python
""
```

Trong scraper, thường ta muốn phân biệt:

```text
None
```

với:

```text
""
```

Ví dụ:

```text
None
→ không tìm thấy

""
→ tìm thấy nhưng không có text
```

---

# 7. Chuẩn hóa empty text

Có thể viết:

```python
def get_text(node):
    if node is None:
        return None

    text = node.text(strip=True)

    return text or None
```

Bây giờ:

```text
node không tồn tại → None
node tồn tại nhưng rỗng → None
node có text → text
```

---

# 8. Missing attribute

HTML:

```html
<a class="next" href="/chapter-2">
    Next
</a>
```

Ta có:

```python
node = tree.css_first(".next")
```

Lấy href:

```python
href = node.attributes.get("href")
```

Tốt hơn:

```python
href = node.attributes["href"]
```

Tại sao?

Nếu thiếu `href`:

```python
node.attributes["href"]
```

có thể gây:

```text
KeyError
```

Còn:

```python
node.attributes.get("href")
```

sẽ cho:

```python
None
```

---

# 9. Defensive attribute extraction

Viết helper:

```python
def get_attr(node, name):
    if node is None:
        return None

    return node.attributes.get(name)
```

Dùng:

```python
image = tree.css_first("img")

src = get_attr(
    image,
    "src",
)
```

---

# 10. Attribute rỗng

HTML:

```html
<img src="">
```

Ta có:

```python
src = node.attributes.get("src")
```

Kết quả:

```python
""
```

Có thể normalize:

```python
def get_attr(node, name):
    if node is None:
        return None

    value = node.attributes.get(name)

    return value or None
```

---

# 11. Missing HTML root

Đây cũng là tình huống cần xử lý.

Ví dụ response:

```python
html = ""
```

Ta parse:

```python
tree = HTMLParser(html)
```

Sau đó:

```python
root = tree.css_first("article")
```

có thể là:

```python
None
```

Không được assume:

```python
root.css_first(...)
```

---

# 12. Empty response

HTTP response:

```text
200 OK
Content-Length: 0
```

Code:

```python
html = response.text
```

Có thể:

```python
if not html.strip():
    return None
```

Ví dụ:

```python
def parse_article(html):

    if not html or not html.strip():
        return None

    tree = HTMLParser(html)

    ...
```

---

# 13. Whitespace-only HTML

Không chỉ:

```python
html == ""
```

Mà còn:

```python
html = """
     
     
"""
```

Vì vậy:

```python
if not html.strip():
```

tốt hơn:

```python
if not html:
```

---

# 14. Broken HTML

HTML thực tế thường không hoàn hảo.

Ví dụ:

```html
<html>
<body>

<div>
    <article>

    <h1>Hello

    <p>World

</body>
```

Không đóng:

```text
</h1>
</p>
</article>
</div>
```

Parser HTML thường được thiết kế để xử lý HTML không hoàn hảo tốt hơn parser XML.

Nhưng bạn vẫn không nên giả định:

```text
HTML lỗi
→ structure luôn đúng như mong đợi
```

---

# 15. Defensive parsing

Một pattern:

```python
from selectolax.parser import HTMLParser


def parse_html(html):

    if not html:
        return None

    try:
        return HTMLParser(html)

    except Exception:
        return None
```

Nhưng có một cảnh báo:

> Không nên `except Exception` ở mọi nơi một cách vô điều kiện.

---

# 16. Vì sao không nên bắt Exception quá rộng?

Sai:

```python
try:
    ...
except Exception:
    return None
```

Nếu code có bug:

```python
x = 10 / 0
```

bạn cũng nuốt luôn:

```text
ZeroDivisionError
```

và không biết chương trình đang sai.

---

# 17. Catch exception ở boundary

Tốt hơn:

```python
def parse_html(html):

    if not html:
        return None

    try:
        return HTMLParser(html)
    except Exception as exc:
        logger.exception(
            "Failed to parse HTML"
        )
        return None
```

Tại boundary:

```text
External HTML
      ↓
Parser boundary
      ↓
Internal application
```

---

# 18. Logging

Scraper production rất cần logging.

```python
import logging

logger = logging.getLogger(__name__)
```

Khi selector không tồn tại:

```python
logger.warning(
    "Article title not found"
)
```

Khi parse lỗi:

```python
logger.exception(
    "Failed to parse HTML"
)
```

---

# 19. Không log quá nhiều

Nếu crawl:

```text
1,000,000 pages
```

mà mỗi page:

```python
logger.info(...)
```

thì log có thể cực lớn.

Phân loại:

```text
DEBUG
INFO
WARNING
ERROR
```

Ví dụ:

```text
DEBUG
→ selector detail

INFO
→ article scraped

WARNING
→ title missing

ERROR
→ request failed
```

---

# 20. Selector fallback

Website có thể dùng:

```html
<h1 class="article-title">
```

nhưng website khác:

```html
<h1 class="post-title">
```

Ta có:

```python
def first_match(root, selectors):

    for selector in selectors:

        node = root.css_first(
            selector
        )

        if node is not None:
            return node

    return None
```

---

# 21. Dùng fallback

```python
title_node = first_match(
    tree,
    [
        ".article-title",
        ".post-title",
        ".entry-title",
        "h1",
    ],
)
```

Pipeline:

```text
.article-title
      ↓
không có
      ↓
.post-title
      ↓
không có
      ↓
.entry-title
      ↓
không có
      ↓
h1
```

---

# 22. Fallback có giới hạn

Đừng viết:

```python
[
    ".title",
    ".post-title",
    ".article-title",
    ".entry-title",
    "h1",
    "h2",
    "div",
    "span",
]
```

Selector cuối:

```css
div
```

có thể lấy dữ liệu hoàn toàn sai.

Fallback phải:

```text
specific
   ↓
less specific
   ↓
generic nhưng vẫn semantic
```

---

# 23. Selector fallback theo confidence

Một ý tưởng tốt hơn:

```python
TITLE_SELECTORS = (
    ".article-title",
    ".post-title",
    ".entry-title",
    "article h1",
)
```

Thứ tự:

```text
1. rất chính xác
2. chính xác
3. phổ biến
4. fallback
```

Không nên fallback bừa bãi.

---

# 24. Defensive extraction cho title

```python
def extract_title(root):

    node = first_match(
        root,
        (
            ".article-title",
            ".post-title",
            ".entry-title",
            "h1",
        ),
    )

    if node is None:
        return None

    text = node.text(
        strip=True
    )

    return text or None
```

Đây là extractor khá an toàn.

---

# 25. Defensive extraction cho author

```python
def extract_author(root):

    node = first_match(
        root,
        (
            ".author",
            ".post-author",
            "[rel='author']",
        ),
    )

    if node is None:
        return None

    text = node.text(
        strip=True
    )

    return text or None
```

---

# 26. Defensive extraction cho image

```python
def extract_image(root):

    node = first_match(
        root,
        (
            ".cover img",
            ".thumbnail img",
            "article img",
        ),
    )

    if node is None:
        return None

    return node.attributes.get(
        "src"
    )
```

---

# 27. `src` không phải lúc nào cũng có

Website lazy loading:

```html
<img
    data-src="/images/book.jpg"
>
```

Không có:

```html
src
```

Vậy:

```python
src = node.attributes.get("src")
```

sẽ:

```python
None
```

Ta có thể fallback:

```python
src = (
    node.attributes.get("src")
    or node.attributes.get("data-src")
    or node.attributes.get(
        "data-lazy-src"
    )
)
```

---

# 28. Đây là pattern rất hay

```python
def first_attr(node, names):

    if node is None:
        return None

    for name in names:

        value = (
            node.attributes.get(name)
        )

        if value:
            return value

    return None
```

Dùng:

```python
src = first_attr(
    image,
    (
        "src",
        "data-src",
        "data-lazy-src",
    ),
)
```

---

# 29. Broken URL

Lấy:

```python
href = node.attributes.get(
    "href"
)
```

nhưng có thể:

```text
href = ""
href = "#"
href = "javascript:void(0)"
href = None
```

Không nên coi tất cả là URL hợp lệ.

```python
def is_valid_href(href):

    if not href:
        return False

    if href.startswith("#"):
        return False

    if href.startswith(
        "javascript:"
    ):
        return False

    return True
```

---

# 30. Encoding

Đây là vấn đề quan trọng khi scrape website tiếng Việt.

Ví dụ HTML:

```html
<meta charset="utf-8">
```

HTTP response có thể có:

```text
Content-Type: text/html; charset=utf-8
```

HTTPX xử lý response encoding dựa trên thông tin response và các cơ chế encoding của nó.

Thông thường:

```python
html = response.text
```

là lựa chọn đầu tiên.

---

# 31. Đừng tự decode bừa

Sai:

```python
html = response.content.decode(
    "utf-8"
)
```

Nếu server thực sự trả:

```text
windows-1252
```

hoặc encoding khác, bạn có thể làm hỏng dữ liệu.

Ưu tiên:

```python
response.text
```

và kiểm tra:

```python
response.encoding
```

khi cần debug.

---

# 32. Khi encoding có vấn đề

Ví dụ:

```python
response = client.get(url)

print(
    response.encoding
)
```

Bạn có thể kiểm tra:

```python
print(
    response.headers.get(
        "content-type"
    )
)
```

Nếu website khai báo sai charset, lúc đó mới cần chiến lược xử lý riêng.

---

# 33. Encoding fallback

Trong scraper thực tế, có thể có:

```text
HTTP header
       ↓
HTML meta charset
       ↓
fallback
```

Nhưng đừng tự xây cơ chế encoding phức tạp nếu chưa gặp vấn đề thật.

Nguyên tắc:

> **Chỉ thêm encoding recovery khi workload thực tế yêu cầu.**

---

# 34. Missing content

Ví dụ:

```html
<article>
    <h1>Python</h1>
</article>
```

Không có:

```html
<div class="content">
```

Không nên:

```python
content = tree.css_first(
    ".content"
).text()
```

Nên:

```python
node = tree.css_first(
    ".content"
)

if node is None:
    content = None
else:
    content = node.text(
        strip=True
    )
```

---

# 35. Required vs Optional fields

Đây là một khái niệm rất quan trọng khi thiết kế extractor.

Ví dụ:

```text
title       REQUIRED
content     REQUIRED
author      OPTIONAL
published   OPTIONAL
cover       OPTIONAL
```

Nếu:

```text
author missing
```

không nên fail toàn bộ article.

Nhưng:

```text
content missing
```

có thể xem là extraction failure.

---

# 36. Model

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str

    author: str | None = None
    image: str | None = None
```

Ở đây:

```text
title
content
```

là required.

```text
author
image
```

optional.

---

# 37. Validate required fields

```python
def extract_article(tree):

    title = extract_title(tree)
    content = extract_content(tree)

    if not title:
        raise ValueError(
            "Missing article title"
        )

    if not content:
        raise ValueError(
            "Missing article content"
        )

    return Article(
        title=title,
        content=content,
        author=extract_author(tree),
    )
```

---

# 38. Nhưng có nên `raise` không?

Phụ thuộc architecture.

Có hai chiến lược.

### Strict

```text
missing required data
        ↓
raise
        ↓
job failed
```

### Lenient

```text
missing data
        ↓
return partial result
        ↓
log warning
```

---

# 39. Với scraper lớn, tôi thường khuyên

Phân biệt:

```text
Parse Error
Extraction Error
Validation Error
Network Error
```

Ví dụ:

```python
class ScraperError(Exception):
    pass


class ParseError(ScraperError):
    pass


class ExtractionError(ScraperError):
    pass


class ValidationError(ScraperError):
    pass
```

---

# 40. Tại sao cần custom exception?

Thay vì:

```python
except Exception:
```

ta có thể:

```python
except ParseError:
    ...
```

hoặc:

```python
except ExtractionError:
    ...
```

Application layer biết chính xác:

```text
Network
Parser
Extractor
```

đang lỗi ở đâu.

---

# 41. Ví dụ Parser

```python
def parse_html(html):

    if not html:
        raise ParseError(
            "Empty HTML"
        )

    try:
        return HTMLParser(html)

    except Exception as exc:
        raise ParseError(
            "Unable to parse HTML"
        ) from exc
```

---

# 42. Extractor

```python
def extract_title(root):

    node = first_match(
        root,
        (
            ".article-title",
            ".post-title",
            "h1",
        ),
    )

    if node is None:
        raise ExtractionError(
            "Article title not found"
        )

    title = node.text(
        strip=True
    )

    if not title:
        raise ExtractionError(
            "Article title is empty"
        )

    return title
```

---

# 43. Đây là boundary rất đẹp

```text
HTTPX
  ↓
response
  ↓
Parser
  ↓
HTMLParser
  ↓
Extractor
  ↓
Article
```

Error:

```text
HTTP error
Parser error
Extractor error
Validation error
```

được phân biệt rõ.

---

# 44. Một `SafeExtractor`

Bây giờ ta xây một helper nhỏ.

```python
class SafeExtractor:

    def __init__(self, root):
        self.root = root
```

Method:

```python
def text(self, selector):

    node = self.root.css_first(
        selector
    )

    if node is None:
        return None

    value = node.text(
        strip=True
    )

    return value or None
```

---

# 45. Attribute

```python
def attr(self, selector, name):

    node = self.root.css_first(
        selector
    )

    if node is None:
        return None

    value = node.attributes.get(
        name
    )

    return value or None
```

---

# 46. Dùng SafeExtractor

```python
extractor = SafeExtractor(tree)

title = extractor.text(
    "h1"
)

author = extractor.text(
    ".author"
)

image = extractor.attr(
    ".cover img",
    "src",
)
```

Code rất sạch:

```text
selector
 ↓
SafeExtractor
 ↓
None hoặc value
```

---

# 47. Nhưng đừng lạm dụng abstraction

Không nên biến:

```python
node = tree.css_first(".title")
```

thành:

```python
safe.dom.query.safe.selector.find.first.node.text.safe(...)
```

😂

Abstraction phải giúp code đơn giản hơn.

---

# 48. Một helper thực tế hơn

```python
def text(
    root,
    selector,
):
    node = root.css_first(
        selector
    )

    if node is None:
        return None

    value = node.text(
        strip=True
    )

    return value or None
```

Dùng:

```python
title = text(
    tree,
    "h1",
)

author = text(
    tree,
    ".author",
)
```

Đơn giản.

---

# 49. Multiple selectors

Kết hợp:

```python
def text_first(
    root,
    selectors,
):
    for selector in selectors:

        node = root.css_first(
            selector
        )

        if node is None:
            continue

        value = node.text(
            strip=True
        )

        if value:
            return value

    return None
```

Dùng:

```python
title = text_first(
    tree,
    (
        ".article-title",
        ".post-title",
        "h1",
    ),
)
```

Đây là helper tôi khuyên dùng cho scraper.

---

# 50. Error Handling hoàn chỉnh

Một extractor:

```python
def extract_article(html):

    if not html or not html.strip():
        raise ParseError(
            "Empty HTML"
        )

    try:
        tree = HTMLParser(html)
    except Exception as exc:
        raise ParseError(
            "Invalid HTML"
        ) from exc

    title = text_first(
        tree,
        (
            ".article-title",
            ".post-title",
            "article h1",
        ),
    )

    content = text_first(
        tree,
        (
            ".article-content",
            ".post-content",
            "article .content",
        ),
    )

    if not title:
        raise ExtractionError(
            "Missing title"
        )

    if not content:
        raise ExtractionError(
            "Missing content"
        )

    return Article(
        title=title,
        content=content,
    )
```

---

# 51. Điều gì xảy ra khi website thay đổi?

Hôm nay:

```html
<h1 class="article-title">
```

Ngày mai:

```html
<h1 class="post-title">
```

Nếu có:

```python
(
    ".article-title",
    ".post-title",
)
```

scraper vẫn chạy.

Đây chính là:

> **Resilience**

---

# 52. Nhưng fallback không giải quyết mọi thứ

Nếu website thay đổi:

```text
article
 ↓
div
 ↓
section
 ↓
content
```

và class thay đổi hoàn toàn:

```text
.article-content
→ .reading-area
```

thì fallback cũ vẫn fail.

Lúc đó cần:

```text
selector strategy
+
site-specific parser
+
tests
```

Đây sẽ liên quan trực tiếp đến **Buổi 13 — Thiết kế Scraper**.

---

# 53. Đừng silently return `None` mọi nơi

Đây là lỗi thiết kế rất nguy hiểm.

Ví dụ:

```python
def extract_title(root):
    return None
```

Website thay đổi.

Kết quả:

```text
10,000 articles
→ title = None
```

Scraper vẫn "chạy thành công".

Đây gọi là:

> **Silent failure**

Nguy hiểm hơn crash.

---

# 54. Vì vậy cần observability

Ví dụ:

```python
if title is None:
    logger.warning(
        "Title not found",
        extra={
            "url": url,
        },
    )
```

Bạn biết:

```text
scraper đang chạy
nhưng dữ liệu đang giảm chất lượng
```

---

# 55. Data quality metrics

Scraper production có thể theo dõi:

```text
pages_scraped = 10000

title_found = 9980
content_found = 9950
author_found = 7000
image_found = 8200
```

Tính:

```text
title success = 99.8%
content success = 99.5%
author success = 70%
```

Nếu hôm nay:

```text
content = 99.5%
```

ngày mai:

```text
content = 45%
```

→ website có thể đã thay đổi.

---

# 56. Đây là tư duy production scraper

Không chỉ:

```text
"Scraper có crash không?"
```

Mà:

```text
"Scraper có đang lấy đúng dữ liệu không?"
```

Hai chuyện hoàn toàn khác nhau.

---

# 57. Bài tập 1 — Missing selector

HTML:

```html
<article>
    <h1>Python</h1>
</article>
```

Viết:

```python
def extract_author(tree):
    ...
```

Kết quả phải là:

```python
None
```

Không được crash.

---

# 58. Bài tập 2 — Missing attribute

HTML:

```html
<img class="cover">
```

Viết:

```python
src = ...
```

Kết quả:

```python
None
```

Không được:

```text
KeyError
```

---

# 59. Bài tập 3 — Fallback selector

Cho 3 HTML:

### HTML A

```html
<h1 class="article-title">
    Python
</h1>
```

### HTML B

```html
<h1 class="post-title">
    Python
</h1>
```

### HTML C

```html
<article>
    <h1>Python</h1>
</article>
```

Viết:

```python
title = text_first(
    tree,
    (
        ".article-title",
        ".post-title",
        "article h1",
    ),
)
```

Cả 3 đều phải trả:

```text
Python
```

---

# 60. Bài tập 4 — Lazy image

HTML:

```html
<img
    class="cover"
    data-src="/book.jpg"
>
```

Viết:

```python
src = first_attr(
    image,
    (
        "src",
        "data-src",
        "data-lazy-src",
    ),
)
```

Kết quả:

```text
/book.jpg
```

---

# 61. Bài tập 5 — Required fields

Xây:

```python
@dataclass
class Article:
    title: str
    content: str
    author: str | None = None
```

Quy tắc:

```text
title missing
→ ExtractionError

content missing
→ ExtractionError

author missing
→ None
```

---

# 62. Bài tập 6 — Safe Article Extractor

Xây:

```python
class ArticleExtractor:

    def extract(
        self,
        html: str,
    ) -> Article:
        ...
```

Phải xử lý:

```text
✓ empty HTML
✓ missing title
✓ missing content
✓ missing author
✓ fallback selector
✓ empty text
✓ missing attributes
```

---

# 63. Bài tập 7 — Test dữ liệu lỗi

Tạo:

```text
tests/
└── test_extractor.py
```

Test:

```python
def test_missing_title():
    ...
```

```python
def test_missing_author():
    ...
```

```python
def test_empty_html():
    ...
```

```python
def test_fallback_title():
    ...
```

Đây chính là nền móng cho:

# Buổi 14 — Testing Selectolax

---

# 🧠 Tổng kết Buổi 12

Hãy nhớ 8 nguyên tắc:

```text
1. HTML bên ngoài là untrusted input.

2. css_first() có thể trả None.

3. attributes.get() an toàn hơn [] khi attribute optional.

4. Empty text cần normalize.

5. Required và optional fields phải được phân biệt.

6. Fallback selector giúp scraper resilient hơn.

7. Không được silently nuốt mọi exception.

8. Scraper cần theo dõi data quality, không chỉ exception.
```

Pattern quan trọng nhất:

```python
node = root.css_first(".title")

if node is None:
    return None

text = node.text(strip=True)

return text or None
```

Và với fallback:

```python
def text_first(root, selectors):
    for selector in selectors:
        node = root.css_first(selector)

        if node is None:
            continue

        value = node.text(strip=True)

        if value:
            return value

    return None
```

Từ đây, extractor của bạn đã bắt đầu có tính **production-ready**.

### 🔜 Buổi 13 — Thiết kế Scraper

Chúng ta sẽ đưa tất cả kiến thức từ Buổi 1–12 vào kiến trúc:

```text
                    Scraper
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Parser       Extractor    Repository
          │            │            │
      Selectolax    Article       SQLite
                     Model
```

và đặc biệt học cách tách:

```text
HTTP
 ↓
Parser
 ↓
Extractor
 ↓
Model
 ↓
Repository
```

để scraper của bạn **dễ test, dễ thay website, dễ mở rộng và không biến thành một file crawler khổng lồ**.
