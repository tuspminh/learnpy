Bạn vừa yêu cầu **Buổi 8** lần nữa. Mình sẽ dạy lại theo hướng **Deep Dive + thực hành**, tập trung vào cách `html2text` xử lý `<a>` trong một crawler thực tế.

# Buổi 8 — Link Configuration Deep Dive

## 1. Mục tiêu

Sau buổi này bạn cần hiểu được:

```text
<a href="...">
       │
       ├── ignore_links
       ├── inline_links
       ├── use_automatic_links
       ├── skip_internal_links
       ├── protect_links
       └── wrap_links
```

và quan trọng hơn:

```text
URL normalization
        ≠
Markdown conversion
```

Đây là nguyên tắc architecture rất quan trọng.

---

# 2. Link cơ bản

HTML:

```html
<a href="https://python.org">
    Python
</a>
```

`html2text` chuyển thành:

```markdown
[Python](https://python.org)
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

---

# 3. `ignore_links`

Option:

```python
converter.ignore_links = True
```

HTML:

```html
<p>
Học <a href="https://python.org">Python</a>.
</p>
```

Thay vì:

```markdown
Học [Python](https://python.org).
```

ta muốn:

```text
Học Python.
```

Mental model:

```text
<a>
 │
 ├── text  ──► giữ
 │
 └── href  ──► bỏ
```

---

# 4. Khi nào dùng `ignore_links`?

Ví dụ bạn xây hệ thống:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
TTS
```

Nếu TTS không cần đọc URL:

```python
converter.ignore_links = True
```

có thể hợp lý.

Nhưng với app đọc truyện:

```text
Crawler
 ↓
Chapter
 ↓
Markdown
 ↓
Reader
```

thường nên:

```python
converter.ignore_links = False
```

vì link vẫn là thông tin của document.

---

# 5. `inline_links`

Thông thường bạn muốn:

```markdown
Python có tài liệu tại [Python Docs](https://docs.python.org).
```

Đây là inline link.

Có thể cấu hình:

```python
converter.inline_links = True
```

Mental model:

```text
HTML
 ↓
<a>
 ↓
[text](url)
```

---

# 6. Reference-style links

Nếu:

```python
converter.inline_links = False
```

output có thể sử dụng reference-style:

```markdown
Python có tài liệu tại [Python Docs][1].

[1]: https://docs.python.org
```

So sánh:

### Inline

```markdown
[Python Docs](https://docs.python.org)
```

### Reference

```markdown
[Python Docs][1]

[1]: https://docs.python.org
```

---

# 7. Ưu và nhược điểm

### Inline

```markdown
[Python](https://python.org)
```

Ưu:

* dễ đọc source
* dễ debug
* URL nằm ngay cạnh text
* dễ xử lý tiếp

Nhược:

* URL dài làm Markdown rất dài

---

### Reference

```markdown
[Python][1]

[1]: https://python.org
```

Ưu:

* body sạch
* dễ đọc khi có nhiều link

Nhược:

* khó debug URL
* cần phần reference definitions

---

# 8. Với crawler, tôi khuyên gì?

Nếu lưu Markdown vào database:

```python
converter.inline_links = True
```

thường là lựa chọn dễ quản lý hơn.

Ví dụ:

```text
SQLite
   │
   └── chapter.content

# Chapter 1

Xem [Chapter 2](https://example.com/chapter/2).
```

Khi debug database, bạn nhìn là biết URL nào được lưu.

---

# 9. `skip_internal_links`

Một HTML article thường có:

```html
<a href="#toc">Mục lục</a>
<a href="#chapter-1">Chương 1</a>
<a href="#comments">Bình luận</a>
```

Đây là fragment/internal links.

Có thể bật:

```python
converter.skip_internal_links = True
```

Mental model:

```text
href="#something"
        │
        ▼
same document
        │
        ▼
skip_internal_links
```

---

# 10. Phân biệt 3 loại URL

Đây là kiến thức bắt buộc.

### 1. Fragment

```html
<a href="#chapter-1">
```

### 2. Relative URL

```html
<a href="/chapter/2">
```

### 3. Absolute URL

```html
<a href="https://example.com/chapter/2">
```

Sơ đồ:

```text
#chapter-1
    │
    └── fragment


/chapter/2
    │
    └── relative URL


https://example.com/chapter/2
    │
    └── absolute URL
```

---

# 11. `skip_internal_links` không phải URL normalizer

Đây là lỗi thiết kế rất dễ mắc.

Không nên nghĩ:

```text
skip_internal_links
       ↓
URL processing
```

Mà:

```text
skip_internal_links
       ↓
filtering
```

Còn:

```text
/chapter/2
       ↓
https://example.com/chapter/2
```

là:

```text
URL resolution
```

---

# 12. URL resolution

Python có sẵn:

```python
from urllib.parse import urljoin

base_url = "https://example.com/story/chapter-1"

href = "/chapter/2"

print(urljoin(base_url, href))
```

Kết quả:

```text
https://example.com/chapter/2
```

---

# 13. Tại sao không để `html2text` làm việc này?

Vì architecture nên tách:

```text
URL
 │
 ├── resolve
 ├── normalize
 ├── filter
 └── classify
```

khỏi:

```text
HTML
 │
 └── Markdown conversion
```

Do đó:

```text
URLNormalizer
       ↓
HTMLCleaner
       ↓
html2text
```

sạch hơn.

---

# 14. `javascript:` link

Website thực tế có:

```html
<a href="javascript:void(0)">
    Click
</a>
```

Không phải URL article.

Crawler có thể loại:

```python
from urllib.parse import urlparse


def is_http_url(url: str) -> bool:
    scheme = urlparse(url).scheme
    return scheme in {"http", "https"}
```

Ví dụ:

```python
print(is_http_url("https://example.com"))
print(is_http_url("javascript:void(0)"))
```

---

# 15. `mailto:` và `tel:`

Có thể gặp:

```html
<a href="mailto:abc@example.com">
```

và:

```html
<a href="tel:+84123456789">
```

Đây không phải HTTP page.

Do đó crawler nên có policy:

```text
href
 │
 ├── http
 ├── https
 │      ↓
 │    KEEP
 │
 ├── mailto
 ├── tel
 ├── javascript
 └── fragment
        ↓
      POLICY
```

---

# 16. `protect_links`

Bây giờ kết hợp với Buổi 7.

Ta có:

```python
converter.body_width = 30
```

và URL rất dài:

```html
<a href="https://example.com/very/long/path/to/article">
    Read article
</a>
```

Converter phải xử lý:

```text
body wrapping
       +
Markdown link
```

`protect_links` liên quan tới việc bảo vệ link trong quá trình wrapping.

---

# 17. Test `protect_links`

Đừng đoán behavior.

Hãy chạy:

```python
import html2text

html = """
<p>
Read
<a href="https://example.com/very/long/path/to/article">
    this article
</a>
for more information.
</p>
"""

for protect in (False, True):

    converter = html2text.HTML2Text()
    converter.body_width = 30
    converter.protect_links = protect

    print(f"\n===== protect_links={protect} =====")
    print(converter.handle(html))
```

Điều quan trọng là **quan sát behavior của phiên bản `html2text` bạn đang dùng**.

---

# 18. `wrap_links`

Tương tự:

```python
converter.wrap_links = False
```

liên quan đến việc link có tham gia wrapping hay không.

Đừng học riêng:

```text
wrap_links
```

Hãy học theo nhóm:

```text
body_width
    +
wrap_links
    +
protect_links
```

---

# 19. Automatic links

Có một trường hợp khác:

```html
<p>
https://python.org
</p>
```

Đây không phải:

```html
<a href="...">
```

mà là **bare URL**.

`use_automatic_links` liên quan đến việc xử lý URL xuất hiện trực tiếp trong text.

Ví dụ Markdown có thể biểu diễn URL tự động dạng:

```markdown
<https://python.org>
```

---

# 20. Phân biệt explicit và automatic link

### Explicit

```html
<a href="https://python.org">
    Python
</a>
```

→

```markdown
[Python](https://python.org)
```

### Automatic

```html
https://python.org
```

→ có thể được nhận diện thành automatic link tùy configuration.

Sơ đồ:

```text
<a href="">
      │
      ▼
explicit link


plain URL
      │
      ▼
automatic link
```

---

# 21. Link chứa `<strong>`

HTML:

```html
<a href="https://python.org">
    <strong>Python</strong>
</a>
```

Markdown mong muốn:

```markdown
[**Python**](https://python.org)
```

Đây là test rất tốt vì có nested inline elements:

```text
a
└── strong
```

---

# 22. Link chứa `<em>`

```html
<a href="https://python.org">
    <em>Python</em>
</a>
```

→

```markdown
[*Python*](https://python.org)
```

---

# 23. Link chứa `<code>`

```html
<a href="https://docs.python.org">
    <code>Python</code>
</a>
```

→ dạng:

```markdown
[`Python`](https://docs.python.org)
```

Đây là case nên đưa vào test suite.

---

# 24. Link chứa image

HTML:

```html
<a href="https://python.org">
    <img src="/images/python.png" alt="Python">
</a>
```

Semantic tree:

```text
a
└── img
```

Markdown có thể có dạng:

```markdown
[![Python](/images/python.png)](https://python.org)
```

Đây là nơi Buổi 8 bắt đầu giao với **Buổi 9 — Image Configuration**.

---

# 25. Empty link

HTML:

```html
<a href="https://example.com"></a>
```

Đây là một case production rất hay gặp.

Bạn nên test:

```python
html = """
<a href="https://example.com"></a>
"""

converter = html2text.HTML2Text()

print(repr(converter.handle(html)))
```

Dùng:

```python
repr()
```

để nhìn rõ newline/whitespace.

---

# 26. Vì sao dùng `repr()`?

Thay vì:

```python
print(result)
```

hãy thử:

```python
print(repr(result))
```

Ví dụ:

```text
'[Python](https://python.org)\n\n'
```

Bạn sẽ nhìn thấy:

```text
\n
```

Điều này rất hữu ích khi debug Markdown.

---

# 27. Xây `LinkNormalizer`

Bây giờ bắt đầu thiết kế component riêng.

```python
from urllib.parse import urljoin, urlparse


class LinkNormalizer:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def normalize(self, href: str) -> str | None:

        if not href:
            return None

        if href.startswith("#"):
            return None

        url = urljoin(self.base_url, href)

        scheme = urlparse(url).scheme

        if scheme not in {"http", "https"}:
            return None

        return url
```

---

# 28. Test `LinkNormalizer`

```python
normalizer = LinkNormalizer(
    "https://example.com/story/chapter-1"
)

urls = [
    "/chapter/2",
    "chapter-3",
    "https://python.org",
    "#comments",
    "javascript:void(0)",
]

for url in urls:
    print(url, "=>", normalizer.normalize(url))
```

Bạn đang xây:

```text
HTML crawler infrastructure
```

chứ không còn chỉ học `html2text`.

---

# 29. `LinkNormalizer` không nên biết Markdown

Đây là điểm architecture rất quan trọng.

Không nên:

```python
class LinkNormalizer:
    def to_markdown(...):
        ...
```

Nó chỉ nên:

```text
input:
href

output:
normalized URL | None
```

Ví dụ:

```text
"/chapter/2"
        ↓
"https://example.com/chapter/2"
```

Còn:

```text
https://example.com/chapter/2
        ↓
[Chapter 2](...)
```

là việc của `html2text`.

---

# 30. Pipeline chuẩn

Từ đây project của bạn có thể tiến tới:

```text
                HTTPX
                  │
                  ▼
                 HTML
                  │
                  ▼
              Selectolax
                  │
        ┌─────────┴─────────┐
        │                   │
   HTML Cleaner       LinkNormalizer
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
             html2text
                  │
                  ▼
              Markdown
```

Đây là architecture tốt hơn nhiều so với việc nhồi tất cả vào một hàm.

---

# 31. Configuration baseline

Cho crawler → Markdown:

```python
import html2text


converter = html2text.HTML2Text()

converter.body_width = 0

converter.ignore_links = False

converter.inline_links = True

converter.skip_internal_links = True
```

Sau đó URL được normalize **trước khi conversion**.

---

# 32. Một converter hoàn chỉnh hơn

```python
import html2text


class MarkdownConverter:

    def __init__(self):

        self.converter = html2text.HTML2Text()

        self.converter.body_width = 0
        self.converter.ignore_links = False
        self.converter.inline_links = True
        self.converter.skip_internal_links = True

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

Điểm quan trọng:

```text
MarkdownConverter
```

không biết:

```text
HTTPX
SQLite
Crawler
base URL
```

Nó chỉ làm:

```text
HTML → Markdown
```

---

# 33. Test architecture

Ta có thể test độc lập:

### Test URL

```python
def test_relative_url():
    ...
```

### Test converter

```python
def test_markdown_link():
    ...
```

### Test integration

```text
HTML
 ↓
normalize
 ↓
convert
 ↓
Markdown
```

Ba tầng test:

```text
Unit
  ↓
Component
  ↓
Integration
```

Đây chính là cách xây code production.

---

# 34. Bài tập thực hành

## Bài 1

Chuyển:

```html
<p>
Học <a href="https://python.org">Python</a>.
</p>
```

với:

```python
ignore_links = False
```

và:

```python
ignore_links = True
```

---

## Bài 2

Test:

```html
<p>
<a href="https://python.org">Python</a>
<a href="https://docs.python.org">Docs</a>
<a href="https://github.com">GitHub</a>
</p>
```

So sánh:

```python
inline_links = True
```

và:

```python
inline_links = False
```

---

## Bài 3

Test:

```html
<a href="#toc">TOC</a>
<a href="/chapter/2">Chapter 2</a>
<a href="https://example.com/chapter/3">Chapter 3</a>
```

với:

```python
skip_internal_links = True
```

Phân loại ba URL.

---

## Bài 4

Test nested formatting:

```html
<a href="https://python.org">
    <strong>Python</strong>
</a>
```

```html
<a href="https://python.org">
    <em>Python</em>
</a>
```

```html
<a href="https://python.org">
    <code>Python</code>
</a>
```

Dự đoán Markdown trước khi chạy.

---

# 35. Bài tập nâng cao

Viết:

```python
class LinkPolicy:
    ...
```

với các policy:

```text
keep_links
skip_internal
allow_http
allow_https
allow_mailto
normalize_relative
```

Sau đó:

```text
LinkPolicy
     ↓
LinkNormalizer
     ↓
HTML
     ↓
html2text
     ↓
Markdown
```

Mục tiêu của bài này không phải viết nhiều code.

Mục tiêu là hiểu **separation of concerns**.

---

# 36. Tổng kết Buổi 8

Bạn cần nhớ 3 lớp:

```text
                 LINK
                   │
        ┌──────────┼──────────┐
        │          │          │
     FORMAT       URL       FILTER
        │          │          │
        ▼          ▼          ▼
     html2text   normalizer  policy
```

### `html2text`

Chịu trách nhiệm:

```text
<a>
 ↓
Markdown link
```

### URLNormalizer

Chịu trách nhiệm:

```text
relative URL
 ↓
absolute URL
```

### LinkPolicy

Chịu trách nhiệm:

```text
giữ?
bỏ?
HTTP?
HTTPS?
fragment?
mailto?
javascript?
```

Đây là mental model bạn nên giữ khi xây crawler:

```text
Fetcher
   ↓
HTML
   ↓
Parser
   ↓
Cleaner
   ↓
LinkNormalizer
   ↓
html2text
   ↓
Markdown
```

**Buổi 9** chúng ta sẽ chuyển sang `<img>` — đặc biệt quan trọng với crawler vì sẽ gặp **`src`, `srcset`, `data-src`, lazy loading, CDN URL, relative image URL và `images_with_size`**.
