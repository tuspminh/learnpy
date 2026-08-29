# Buổi 3 — Link & Image trong `html2text`

Hôm nay chúng ta tập trung vào 2 thành phần cực kỳ quan trọng khi crawl web:

```text
HTML
 │
 ├── <a>     → Markdown link
 │
 └── <img>   → Markdown image
```

Mục tiêu cuối buổi:

```text
<a href="...">
        ↓
[title](url)

<img src="..." alt="...">
        ↓
![alt](url)
```

---

# 1. `<a>` → Markdown Link

HTML:

```html
<a href="https://python.org">
    Python
</a>
```

Code:

```python
import html2text

html = """
<a href="https://python.org">
    Python
</a>
"""

converter = html2text.HTML2Text()

print(converter.handle(html))
```

Kết quả:

```markdown
[Python](https://python.org)
```

Đây là chuyển đổi cơ bản nhất.

---

# 2. Link trong paragraph

```html
<p>
    Học Python tại
    <a href="https://python.org">Python.org</a>.
</p>
```

→

```markdown
Học Python tại [Python.org](https://python.org).
```

`html2text` hiểu cấu trúc HTML và giữ lại semantic của `<a>`.

---

# 3. Link không có text

Ví dụ:

```html
<a href="https://python.org"></a>
```

Đây là trường hợp cần chú ý.

Một crawler thực tế có thể gặp:

```html
<a href="/chapter/1"></a>
```

hoặc:

```html
<a href="/chapter/1">
    <img src="cover.jpg">
</a>
```

Lúc này kết quả phụ thuộc vào nội dung bên trong `<a>`.

---

# 4. `ignore_links`

Nếu:

```python
converter.ignore_links = True
```

thì:

```html
<a href="https://python.org">
    Python
</a>
```

sẽ không còn được biểu diễn như:

```markdown
[Python](https://python.org)
```

Đây là option bạn đã học ở Buổi 2.

Trong crawler article, thường:

```python
converter.ignore_links = False
```

vì link thường là dữ liệu có giá trị.

---

# 5. Internal link

Ví dụ:

```html
<a href="#chapter-1">
    Chapter 1
</a>
```

Đây là anchor link.

Nếu:

```python
converter.skip_internal_links = True
```

thì các link kiểu:

```text
#chapter-1
#comments
#top
#footer
```

có thể được bỏ qua.

Điều này hữu ích với các trang article có:

```text
Table of Contents
        ↓
#chapter-1
#chapter-2
#chapter-3
```

---

# 6. Link tương đối

Đây là phần **cực kỳ quan trọng khi crawler**.

Website có:

```html
<a href="/article/python">
    Python
</a>
```

`html2text` có thể tạo:

```markdown
[Python](/article/python)
```

Nhưng nếu Markdown được lưu thành file:

```text
articles/python.md
```

thì `/article/python` có thể không còn có ý nghĩa như bạn mong muốn.

Ta thường muốn:

```markdown
[Python](https://example.com/article/python)
```

Vấn đề là:

> `html2text` không phải URL resolver.

Nó không tự biết URL gốc của document nếu bạn không cung cấp context.

---

# 7. URL resolution phải xử lý trước

Python có module rất hữu ích:

```python
from urllib.parse import urljoin
```

Ví dụ:

```python
from urllib.parse import urljoin

base_url = "https://example.com/articles/"

relative_url = "/article/python"

absolute_url = urljoin(base_url, relative_url)

print(absolute_url)
```

Kết quả:

```text
https://example.com/article/python
```

---

# 8. Vì sao cần xử lý URL trước?

Pipeline crawler:

```text
HTTPX
  ↓
HTML
  ↓
Parse
  ↓
Resolve relative URLs
  ↓
html2text
  ↓
Markdown
```

Ví dụ:

```text
<a href="/chapter/1">
```

nên biến thành:

```text
<a href="https://example.com/chapter/1">
```

trước khi đưa cho `html2text`.

---

# 9. Resolve link bằng Selectolax

Sau này bạn sẽ học sâu hơn, nhưng có thể hình dung:

```python
from urllib.parse import urljoin
from selectolax.parser import HTMLParser

html = """
<a href="/chapter/1">Chapter 1</a>
<a href="/chapter/2">Chapter 2</a>
"""

base_url = "https://example.com/story/"

tree = HTMLParser(html)

for node in tree.css("a[href]"):
    href = node.attributes["href"]

    absolute_url = urljoin(base_url, href)

    node.attributes["href"] = absolute_url
```

Ý tưởng:

```text
href tương đối
      ↓
urljoin()
      ↓
href tuyệt đối
      ↓
html2text
```

---

# 10. `<img>` → Markdown

HTML:

```html
<img
    src="python.png"
    alt="Python logo"
>
```

→

```markdown
![Python logo](python.png)
```

---

# 11. Image có title

Ví dụ:

```html
<img
    src="python.png"
    alt="Python logo"
    title="Python programming language"
>
```

Markdown có thể chứa thông tin title tùy cách converter xử lý.

Điểm quan trọng là:

```text
src
 ↓
image URL

alt
 ↓
alternative text
```

---

# 12. Image URL tương đối

Website:

```html
<img
    src="/images/python.png"
    alt="Python"
>
```

Kết quả trực tiếp:

```markdown
![Python](/images/python.png)
```

Nhưng crawler thường muốn:

```markdown
![Python](https://example.com/images/python.png)
```

Do đó lại cần:

```python
urljoin()
```

---

# 13. Resolve image URL

```python
from urllib.parse import urljoin

base_url = "https://example.com/article/"

src = "/images/python.png"

absolute_url = urljoin(base_url, src)

print(absolute_url)
```

→

```text
https://example.com/images/python.png
```

---

# 14. Image có `data-src`

Crawler thực tế thường gặp:

```html
<img
    src="placeholder.jpg"
    data-src="/images/python.jpg"
    alt="Python"
>
```

Nếu chỉ để `html2text` xử lý:

```text
src
 ↓
placeholder.jpg
```

Trong khi image thật là:

```text
data-src
 ↓
/images/python.jpg
```

Do đó **HTML cleaner/parser phải xử lý lazy loading trước**.

Ví dụ:

```python
src = node.attributes.get("data-src")

if src:
    node.attributes["src"] = src
```

Sau đó mới:

```text
HTML Cleaner
      ↓
html2text
```

---

# 15. Lazy loading nâng cao

Website có thể dùng:

```html
<img data-src="image.jpg">
```

hoặc:

```html
<img data-original="image.jpg">
```

hoặc:

```html
<img
    src="placeholder.jpg"
    data-lazy-src="image.jpg"
>
```

Crawler nên có một bước:

```text
Image normalization
```

Ví dụ:

```python
def normalize_image(node):
    for attr in (
        "data-src",
        "data-original",
        "data-lazy-src",
    ):
        value = node.attributes.get(attr)

        if value:
            node.attributes["src"] = value
            break
```

---

# 16. `srcset`

Một image hiện đại có thể:

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

Nếu mục tiêu của bạn là Markdown đơn giản:

```markdown
![...](small.jpg)
```

thường là đủ.

Nhưng nếu muốn crawler chất lượng cao, cần quyết định:

```text
src
srcset
      ↓
chọn image nào?
```

Đây là vấn đề của **image extraction**, không phải nhiệm vụ chính của `html2text`.

---

# 17. `ignore_images`

Nếu:

```python
converter.ignore_images = True
```

thì:

```html
<img src="python.png" alt="Python">
```

sẽ bị bỏ qua.

Điều này hữu ích khi bạn muốn:

```text
Article
 ↓
Text only
```

Ví dụ tạo nội dung cho TTS:

```text
HTML
 ↓
Clean
 ↓
Markdown
 ↓
Text
 ↓
TTS
```

thì image thường không cần thiết.

---

# 18. Link chứa Image

Một pattern rất phổ biến:

```html
<a href="/chapter/1">
    <img src="/cover.jpg" alt="Chapter 1">
</a>
```

Semantic của HTML là:

```text
IMAGE
   ↓
CLICKABLE
   ↓
LINK
```

Markdown có thể trở thành dạng:

```markdown
[![Chapter 1](/cover.jpg)](/chapter/1)
```

Đây là một ví dụ cho thấy tại sao ta không nên chỉ xử lý HTML bằng regex.

Cấu trúc DOM rất quan trọng.

---

# 19. Không dùng regex để parse HTML

Không nên làm:

```python
import re

html = re.sub(
    r'<a.*?href="(.*?)".*?>(.*?)</a>',
    r'[\2](\1)',
    html
)
```

Cách này rất dễ hỏng.

Ví dụ:

```html
<a
    class="link"
    href="/article"
    data-id="123"
>
    Python
</a>
```

hoặc:

```html
<a href="/article">
    <strong>Python</strong>
</a>
```

Regex sẽ nhanh chóng trở nên khó bảo trì.

Pipeline tốt:

```text
HTML
 ↓
HTML Parser
 ↓
DOM
 ↓
Normalize URL
 ↓
html2text
 ↓
Markdown
```

---

# 20. Thiết kế `URLNormalizer`

Ta có thể tách trách nhiệm:

```python
from urllib.parse import urljoin


class URLNormalizer:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def normalize(self, url: str) -> str:
        return urljoin(self.base_url, url)
```

Sử dụng:

```python
normalizer = URLNormalizer(
    "https://example.com/story/"
)

print(
    normalizer.normalize("/chapter/1")
)
```

Kết quả:

```text
https://example.com/chapter/1
```

---

# 21. Kiến trúc bắt đầu hình thành

Bây giờ project crawler của chúng ta có thể có:

```text
                HTML
                 │
                 ▼
          HTML Parser
                 │
        ┌────────┴────────┐
        │                 │
   URL Normalizer    HTML Cleaner
        │                 │
        └────────┬────────┘
                 ▼
             html2text
                 │
                 ▼
             Markdown
```

Đây là kiến trúc tốt hơn rất nhiều so với:

```python
markdown = html2text.html2text(html)
```

---

# 22. Một implementation nhỏ

```python
from urllib.parse import urljoin

import html2text
from selectolax.parser import HTMLParser


def normalize_urls(
    html: str,
    base_url: str,
) -> str:
    tree = HTMLParser(html)

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if href:
            node.attributes["href"] = urljoin(
                base_url,
                href,
            )

    for node in tree.css("img[src]"):
        src = node.attributes.get("src")

        if src:
            node.attributes["src"] = urljoin(
                base_url,
                src,
            )

    return tree.html


def html_to_markdown(html: str) -> str:
    converter = html2text.HTML2Text()

    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False
    converter.skip_internal_links = True

    return converter.handle(html)
```

Sử dụng:

```python
html = """
<h1>Python</h1>

<p>
    Học
    <a href="/tutorial">
        Python
    </a>
</p>

<img
    src="/images/python.png"
    alt="Python"
>
"""

html = normalize_urls(
    html,
    "https://example.com/",
)

markdown = html_to_markdown(html)

print(markdown)
```

Ta có:

```text
relative URL
      ↓
normalize_urls()
      ↓
absolute URL
      ↓
html2text
      ↓
Markdown
```

---

# 23. Nhưng có một vấn đề

Code trên:

```python
return tree.html
```

sau đó lại parse HTML một lần nữa trong `html2text`.

Có nghĩa:

```text
HTML
 ↓
Selectolax
 ↓
HTML string
 ↓
html2text
 ↓
Markdown
```

Đây là chuyện **hoàn toàn bình thường** trong pipeline.

Mỗi thư viện có trách nhiệm riêng:

```text
Selectolax
    ↓
DOM manipulation

html2text
    ↓
HTML → Markdown
```

Đừng cố ép một thư viện làm tất cả.

---

# 24. Bài tập Buổi 3

## Bài 1

Chuyển:

```html
<a href="https://python.org">
    Python
</a>
```

thành Markdown bằng `html2text`.

---

## Bài 2

Thử:

```html
<img
    src="python.png"
    alt="Python logo"
>
```

Quan sát Markdown.

---

## Bài 3

Tạo:

```html
<a href="/python">
    Python
</a>
```

Sau đó dùng:

```python
urljoin(
    "https://example.com/tutorial/",
    "/python",
)
```

để biến URL thành absolute URL.

---

## Bài 4 — quan trọng

Xử lý:

```html
<img
    src="placeholder.jpg"
    data-src="/images/python.jpg"
    alt="Python"
>
```

Mục tiêu:

```html
<img
    src="/images/python.jpg"
    data-src="/images/python.jpg"
    alt="Python"
>
```

sau đó mới đưa vào `html2text`.

---

## Bài 5 — Project mini

Viết:

```python
class HTMLToMarkdown:
    ...
```

API:

```python
converter = HTMLToMarkdown(
    base_url="https://example.com/"
)

markdown = converter.convert(html)
```

Pipeline:

```text
HTML
 ↓
Selectolax
 ↓
Resolve <a>
 ↓
Resolve <img>
 ↓
html2text
 ↓
Markdown
```

---

# 25. Kiến thức quan trọng nhất hôm nay

Hãy nhớ:

```text
<a>
 ↓
Markdown link
```

```text
<img>
 ↓
Markdown image
```

Nhưng:

```text
relative URL
     ↓
urljoin()
     ↓
absolute URL
     ↓
html2text
```

Và đối với crawler:

```text
           HTTPX
             ↓
            HTML
             ↓
         Selectolax
             ↓
    ┌────────┴────────┐
    │                 │
  <a> URL           <img> URL
    │                 │
    └────────┬────────┘
             ↓
        html2text
             ↓
          Markdown
```

**Buổi 4** chúng ta sẽ đi vào phần formatting: **`<h1>`, `<p>`, `<strong>`, `<em>`, `<del>`, `<code>`, `<pre>`, `<blockquote>`, ordered/unordered list và đặc biệt là cách `html2text` biến cấu trúc HTML thành Markdown**. Đây là nền tảng để sang Buổi 5 xử lý **code block** đúng cách.
