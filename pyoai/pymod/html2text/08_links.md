# Buổi 8 — Link Configuration Deep Dive

Hôm nay chúng ta tập trung hoàn toàn vào `<a>` và các option liên quan đến link trong `html2text`.

Đây là phần **rất quan trọng với crawler**, vì HTML thực tế thường chứa:

* link tuyệt đối
* link tương đối
* anchor nội bộ
* link email
* link rất dài
* link nằm trong heading/list
* link chứa formatting
* link trùng lặp

Mental model:

```text
HTML
 │
 └── <a href="...">
          │
          ▼
      html2text
          │
          ▼
       Markdown
```

Nhưng cần nhớ:

> `html2text` chuyển đổi **format**, còn việc chuẩn hóa URL thường nên thuộc về crawler/parser của bạn.

---

# 1. HTML link cơ bản

HTML:

```html
<a href="https://python.org">
    Python
</a>
```

Markdown:

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

Đây là behavior cơ bản.

---

# 2. `ignore_links`

Option đầu tiên:

```python
converter.ignore_links = True
```

Ví dụ:

```html
<p>
    Học <a href="https://python.org">Python</a>.
</p>
```

Thay vì:

```markdown
Học [Python](https://python.org).
```

ta muốn bỏ link formatting, chỉ giữ text:

```text
Học Python.
```

Mental model:

```text
<a>
 │
 ├── text → giữ
 │
 └── href → bỏ
```

---

# 3. Khi nào dùng `ignore_links`?

Rất hữu ích khi mục tiêu cuối cùng là **plain text**.

Ví dụ pipeline:

```text
HTML
 ↓
Cleaner
 ↓
html2text
 ↓
Markdown
 ↓
Markdown → plain text
 ↓
TTS
```

Nếu TTS không cần URL:

```python
converter.ignore_links = True
```

có thể giúp output sạch hơn.

Nhưng nếu bạn muốn lưu bài viết Markdown:

```text
Article
 ↓
Markdown
```

thì thường:

```python
ignore_links = False
```

---

# 4. `inline_links`

Mặc định, link có thể được output dưới dạng inline:

```markdown
[Python](https://python.org)
```

Option:

```python
converter.inline_links = True
```

nghĩa là link được đặt trực tiếp tại vị trí xuất hiện.

Ví dụ:

```markdown
Python có tài liệu tại [python.org](https://python.org).
```

---

# 5. Reference-style links

Nếu:

```python
converter.inline_links = False
```

thì link có thể được chuyển thành reference-style:

```markdown
Python có tài liệu tại [python.org][1].

[1]: https://python.org
```

Đây là sự khác biệt quan trọng:

```text
inline
────────────────────────
[text](URL)


reference
────────────────────────
[text][1]

[1]: URL
```

---

# 6. Khi nào reference links hữu ích?

Giả sử article có:

```html
<p>
<a href="...">Python</a>
<a href="...">HTTPX</a>
<a href="...">PySide6</a>
<a href="...">SQLite</a>
</p>
```

Inline Markdown:

```markdown
[Python](...)
[HTTPX](...)
[PySide6](...)
[SQLite](...)
```

Reference style:

```markdown
[Python][1]
[HTTPX][2]
[PySide6][3]
[SQLite][4]

[1]: ...
[2]: ...
[3]: ...
[4]: ...
```

Nội dung chính có thể dễ đọc hơn.

---

# 7. Nhưng reference link có nhược điểm

Markdown:

```markdown
[Python][1]
```

không cho ta thấy URL ngay tại vị trí link.

Muốn biết URL phải tìm:

```markdown
[1]: https://python.org
```

Với crawler lưu database, điều này có thể khiến content khó debug hơn.

Do đó tôi thường ưu tiên:

```python
converter.inline_links = True
```

cho article Markdown.

---

# 8. `protect_links`

Đây là option liên quan đến wrapping.

Giả sử:

```python
converter.body_width = 30
```

và:

```html
<p>
<a href="https://example.com/very/long/path">
    Read this article
</a>
</p>
```

Converter phải xử lý:

```text
text wrapping
        +
Markdown link syntax
```

Nếu wrapping không đúng, cấu trúc:

```markdown
[text](URL)
```

có thể trở nên khó đọc hoặc không như mong muốn.

`protect_links` giúp bảo vệ link trong quá trình wrapping.

---

# 9. `body_width` + link

Đây là combination mà bạn nên tự test.

```python
import html2text

html = """
<p>
Visit
<a href="https://example.com/very/long/path/to/article">
    this article
</a>
for more information.
</p>
"""

for width in (30, 60, 0):
    converter = html2text.HTML2Text()
    converter.body_width = width

    print(f"\n===== {width} =====")
    print(converter.handle(html))
```

Sau đó thử:

```python
converter.protect_links = True
```

và so sánh.

---

# 10. `wrap_links`

Một option khác:

```python
converter.wrap_links
```

Nó kiểm soát việc link có được tham gia vào wrapping hay không.

Mental model:

```text
body_width
    │
    ▼
long text
    │
    ├── normal text
    │
    └── link
          │
          ▼
      wrap_links
```

Đừng học option này riêng biệt.

Hãy luôn test:

```text
body_width
+
wrap_links
+
protect_links
```

---

# 11. `skip_internal_links`

Đây là option **cực kỳ hữu ích khi crawl article**.

Ví dụ:

```html
<a href="#chapter-1">
    Chương 1
</a>
```

Đây là:

```text
internal anchor
```

không phải external page.

Ta có thể bật:

```python
converter.skip_internal_links = True
```

để bỏ qua loại link nội bộ này.

---

# 12. Vì sao crawler nên quan tâm internal links?

Một article có thể có:

```html
<a href="#toc">Mục lục</a>

<a href="#chapter-1">Chương 1</a>

<a href="#comments">Comments</a>

<a href="#footer">Footer</a>
```

Nếu chuyển toàn bộ thành:

```markdown
[Mục lục](#toc)
[Chương 1](#chapter-1)
[Comments](#comments)
[Footer](#footer)
```

thì Markdown có thể chứa rất nhiều navigation noise.

Trong một hệ thống đọc truyện:

```text
Chapter
 ↓
Content
```

những link này thường không có giá trị.

---

# 13. Nhưng đừng nhầm internal với relative link

Đây là điểm rất quan trọng.

### Internal anchor

```html
<a href="#chapter-1">
```

→ cùng document.

### Relative URL

```html
<a href="/chapter/2">
```

→ document khác.

### Absolute URL

```html
<a href="https://example.com/chapter/2">
```

→ document khác.

Ta có:

```text
#chapter-1
    ↓
fragment


/chapter/2
    ↓
relative URL


https://example.com/chapter/2
    ↓
absolute URL
```

`skip_internal_links` chủ yếu liên quan tới loại đầu tiên.

---

# 14. Relative URL — vấn đề rất quan trọng

HTML:

```html
<a href="/chapter/2">
    Chapter 2
</a>
```

`html2text` không biết chắc:

```text
base URL = ?
```

Nếu page hiện tại là:

```text
https://example.com/story/chapter/1
```

thì:

```text
/chapter/2
```

có thể trở thành:

```text
https://example.com/chapter/2
```

Nhưng đó là **URL resolution**, không phải trách nhiệm chính của Markdown converter.

---

# 15. URL normalization nên nằm ở đâu?

Kiến trúc:

```text
Fetcher
   ↓
HTML
   ↓
Parser
   ↓
URL Normalizer
   ↓
Clean HTML
   ↓
html2text
   ↓
Markdown
```

hoặc:

```text
HTML
 ↓
extract <a>
 ↓
resolve URL
 ↓
rewrite href
 ↓
html2text
```

Đây là cách rõ ràng hơn.

---

# 16. Dùng `urllib.parse.urljoin`

Python standard library đã có công cụ rất tốt:

```python
from urllib.parse import urljoin

base_url = "https://example.com/story/chapter-1"

href = "/chapter/2"

absolute_url = urljoin(base_url, href)

print(absolute_url)
```

Kết quả:

```text
https://example.com/chapter/2
```

---

# 17. Relative path

Ví dụ:

```python
base_url = "https://example.com/story/chapter-1"

href = "chapter-2"
```

```python
from urllib.parse import urljoin

print(urljoin(base_url, href))
```

URL được resolve dựa trên base URL.

Do đó crawler nên:

```text
HTML
 ↓
<a href>
 ↓
urljoin()
 ↓
absolute URL
```

trước khi đưa sang Markdown.

---

# 18. `href` không phải lúc nào cũng HTTP URL

Bạn có thể gặp:

```html
<a href="mailto:test@example.com">
```

hoặc:

```html
<a href="javascript:void(0)">
```

hoặc:

```html
<a href="tel:+84123456789">
```

hoặc:

```html
<a href="#">
```

Do đó URL normalizer nên có policy:

```text
href
 │
 ├── http://
 ├── https://
 ├── mailto:
 ├── tel:
 ├── javascript:
 ├── #
 └── relative
```

---

# 19. `javascript:` link

Ví dụ:

```html
<a href="javascript:void(0)">
    Click
</a>
```

Đây không phải link tài liệu.

Trong crawler:

```text
javascript:
```

thường nên loại bỏ.

Ví dụ:

```python
from urllib.parse import urlparse


def is_http_url(url: str) -> bool:
    scheme = urlparse(url).scheme

    return scheme in {"http", "https"}
```

---

# 20. Anchor `#`

Ví dụ:

```html
<a href="#">
    Back to top
</a>
```

Nếu:

```python
converter.skip_internal_links = True
```

thì đây là loại link bạn thường không muốn giữ trong article Markdown.

---

# 21. Link có formatting

HTML:

```html
<a href="https://python.org">
    <strong>Python</strong>
</a>
```

Semantic tree:

```text
a
└── strong
```

Markdown mong muốn:

```markdown
[**Python**](https://python.org)
```

Điều này cho thấy:

```text
link
 +
formatting
```

có thể nested.

---

# 22. Link chứa code

HTML:

```html
<a href="https://docs.python.org">
    <code>Python documentation</code>
</a>
```

Markdown:

```markdown
[`Python documentation`](https://docs.python.org)
```

Đây là một ví dụ rất hay để test converter.

---

# 23. Link chứa image

HTML:

```html
<a href="https://python.org">
    <img src="python.png" alt="Python">
</a>
```

Semantic:

```text
a
└── img
```

Markdown có thể trở thành:

```markdown
[![Python](python.png)](https://python.org)
```

Đây là một case cần kiểm thử nếu crawler xử lý image.

---

# 24. Empty link

HTML:

```html
<a href="https://example.com"></a>
```

Link không có text.

Bạn nên test:

```python
html = """
<a href="https://example.com"></a>
"""
```

Và xem `html2text` tạo output thế nào.

Đừng tự giả định.

Trong production crawler, có thể cần filter:

```text
empty anchor
    ↓
discard
```

---

# 25. Link text quá dài

Ví dụ:

```html
<a href="https://example.com">
    Đây là một tiêu đề bài viết rất dài và chứa rất nhiều nội dung
</a>
```

Nếu:

```python
converter.body_width = 40
```

thì link trở thành bài test tốt cho:

```text
body_width
+
wrap_links
+
protect_links
```

---

# 26. `use_automatic_links`

HTML:

```html
<p>
https://python.org
</p>
```

Có thể được nhận diện thành automatic link.

Ví dụ Markdown:

```markdown
<https://python.org>
```

thay vì:

```text
https://python.org
```

Bạn có thể kiểm soát behavior bằng:

```python
converter.use_automatic_links = False
```

---

# 27. Automatic link vs normal link

### Normal anchor

HTML:

```html
<a href="https://python.org">
    Python
</a>
```

Markdown:

```markdown
[Python](https://python.org)
```

### Bare URL

HTML:

```html
https://python.org
```

có thể trở thành:

```markdown
<https://python.org>
```

Đây là hai trường hợp khác nhau:

```text
<a href="">
     ↓
explicit link


bare URL
     ↓
automatic link detection
```

---

# 28. `ignore_links` và `use_automatic_links`

Đừng nhầm:

```python
ignore_links
```

với:

```python
use_automatic_links
```

### `ignore_links`

Liên quan đến:

```html
<a href="...">
```

### `use_automatic_links`

Liên quan đến việc nhận diện URL trực tiếp trong text.

Mental model:

```text
<a>
 ↓
ignore_links


plain URL
 ↓
use_automatic_links
```

---

# 29. Link configuration cho crawler

Nếu mục tiêu:

```text
Article HTML
 ↓
Markdown
```

tôi thường bắt đầu:

```python
converter.ignore_links = False
converter.inline_links = True
converter.skip_internal_links = True
```

và:

```python
converter.body_width = 0
```

Sau đó xử lý URL **trước converter**.

---

# 30. URL Normalizer riêng

Ví dụ đơn giản:

```python
from urllib.parse import urljoin, urlparse


class URLNormalizer:

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

Ví dụ:

```python
normalizer = URLNormalizer(
    "https://example.com/story/chapter-1"
)

print(normalizer.normalize("/chapter-2"))
```

---

# 31. Đây là Separation of Concerns

Không nên:

```python
class MarkdownConverter:
    def convert(self, html, base_url):
        # parse URL
        # resolve URL
        # remove javascript
        # remove anchor
        # convert markdown
```

Tốt hơn:

```text
URLNormalizer
      ↓
HTMLCleaner
      ↓
MarkdownConverter
```

Mỗi component có một trách nhiệm.

---

# 32. Một pipeline tốt

Với project crawler mà chúng ta đang hướng tới:

```text
                    HTTPX
                      │
                      ▼
                     HTML
                      │
                      ▼
                 Selectolax
                      │
             ┌────────┴────────┐
             │                 │
          Cleaner         URLNormalizer
             │                 │
             └────────┬────────┘
                      │
                      ▼
                html2text
                      │
                      ▼
                  Markdown
```

`html2text` không cần biết:

```text
base_url
crawler
database
HTTPX
```

Nó chỉ làm:

```text
HTML → Markdown
```

---

# 33. Một ví dụ hoàn chỉnh

HTML:

```html
<article>

<h1>Python</h1>

<p>
Learn
<a href="/tutorial">
    <strong>Python</strong>
</a>
today.
</p>

<p>
Documentation:
<a href="https://docs.python.org">
    Python Docs
</a>
</p>

<p>
<a href="#comments">
    Comments
</a>
</p>

</article>
```

Giả sử URL:

```text
https://example.com/articles/python
```

Ta muốn:

```markdown
# Python

Learn [**Python**](https://example.com/tutorial) today.

Documentation: [Python Docs](https://docs.python.org)

Comments
```

Nhưng lưu ý:

> `html2text` không tự chịu trách nhiệm hoàn toàn cho việc biến `/tutorial` thành `https://example.com/tutorial`.

Đó là nhiệm vụ của URL normalization.

---

# 34. Bài tập 1 — `ignore_links`

Test:

```python
html = """
<p>
Learn <a href="https://python.org">Python</a>.
</p>
"""
```

So sánh:

```python
ignore_links = False
```

với:

```python
ignore_links = True
```

---

# 35. Bài tập 2 — Inline vs reference

Test:

```html
<p>
<a href="https://python.org">Python</a>
and
<a href="https://docs.python.org">Documentation</a>
</p>
```

So sánh:

```python
converter.inline_links = True
```

và:

```python
converter.inline_links = False
```

Quan sát phần cuối document.

---

# 36. Bài tập 3 — Internal links

Test:

```html
<p>
<a href="#chapter-1">Chapter 1</a>
</p>

<p>
<a href="/chapter-2">Chapter 2</a>
</p>

<p>
<a href="https://example.com/chapter-3">
Chapter 3
</a>
</p>
```

với:

```python
converter.skip_internal_links = True
```

Sau đó phân biệt:

```text
#chapter-1
/chapter-2
https://example.com/chapter-3
```

---

# 37. Bài tập 4 — URL normalization

Viết:

```python
from urllib.parse import urljoin

base_url = "https://example.com/story/chapter-1"

urls = [
    "/chapter-2",
    "chapter-3",
    "https://python.org",
    "#comments",
]
```

Dùng:

```python
urljoin()
```

để xem kết quả.

---

# 38. Bài tập 5 — Link + formatting

Test tất cả:

```html
<p>
<a href="https://python.org">
    <strong>Python</strong>
</a>
</p>

<p>
<a href="https://docs.python.org">
    <em>Documentation</em>
</a>
</p>

<p>
<a href="https://example.com">
    <code>example()</code>
</a>
</p>
```

Dự đoán Markdown trước khi chạy.

---

# 39. Bài tập 6 — Long link

Tạo:

```html
<p>
<a href="https://example.com/very/long/path/to/some/article/with/many/segments">
    Read this very important article
</a>
</p>
```

Test:

```text
body_width = 30
body_width = 0
```

Sau đó thử:

```text
protect_links = True
protect_links = False
```

Quan sát sự khác biệt.

---

# 40. Bài tập 7 — Xây `LinkPolicy`

Đây là bài tập mang tính architecture.

Tạo:

```python
from dataclasses import dataclass


@dataclass
class LinkPolicy:
    keep_links: bool = True
    skip_internal: bool = True
    absolute_urls: bool = True
```

Sau đó:

```python
class LinkNormalizer:
    ...
```

Mục tiêu:

```text
LinkPolicy
    ↓
LinkNormalizer
    ↓
clean HTML
    ↓
html2text
```

Đây sẽ là nền tảng rất tốt cho crawler thực tế.

---

# 41. Configuration đề xuất sau Buổi 8

Cho một **article crawler → Markdown**, baseline:

```python
import html2text


converter = html2text.HTML2Text()

converter.body_width = 0

converter.ignore_links = False

converter.inline_links = True

converter.skip_internal_links = True
```

URL thì xử lý riêng:

```text
<a href>
    ↓
URLNormalizer
    ↓
absolute URL
    ↓
html2text
```

---

# 42. Mental model quan trọng nhất

Hãy nhớ:

```text
                    LINK
                      │
        ┌─────────────┼─────────────┐
        │             │             │
      format        URL          filtering
        │             │             │
        ▼             ▼             ▼
 inline/reference  normalize   internal?
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
                   Markdown
```

Và architecture:

```text
                 <a href>
                     │
          ┌──────────┴──────────┐
          │                     │
     URLNormalizer        html2text
          │                     │
          │                Markdown syntax
          │                     │
          └──────────┬──────────┘
                     ▼
                  Markdown
```

**Điểm mấu chốt của Buổi 8:**

> `html2text` chịu trách nhiệm **biểu diễn link thành Markdown**; crawler của bạn nên chịu trách nhiệm **URL normalization, filtering và policy**.

Buổi tiếp theo là **Buổi 9 — Image Configuration**, chúng ta sẽ đi sâu vào:

```text
<img>
 │
 ├── ignore_images
 ├── images_to_alt
 ├── images_as_html
 ├── images_with_size
 ├── default_image_alt
 ├── relative src
 ├── lazy-loading
 ├── data-src
 └── image URL normalization
```

Phần **lazy-loading + `data-src` + ảnh CDN** sẽ đặc biệt hữu ích khi bạn áp dụng `html2text` vào crawler website thực tế.
