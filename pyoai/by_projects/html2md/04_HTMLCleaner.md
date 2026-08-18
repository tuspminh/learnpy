# Buổi 4 — BeautifulSoup + thiết kế `HTMLCleaner`

Từ hôm nay chúng ta bắt đầu xử lý **HTML thật**.

Mục tiêu của Buổi 4:

```text
HTML Fragment
      │
      ▼
BeautifulSoup
      │
      ▼
HTMLCleaner
      │
      ├── remove script
      ├── remove style
      ├── remove iframe
      ├── remove svg
      ├── remove comment
      ├── remove hidden element
      └── GIỮ NGUYÊN pre/code
              │
              ▼
          Clean HTML
```

Điểm quan trọng nhất:

> **Cleaner không được phá code.**

---

# 1. Cài BeautifulSoup

Cài:

```bash
pip install beautifulsoup4 lxml
```

Kiểm tra:

```bash
python -c "from bs4 import BeautifulSoup; print('OK')"
```

---

# 2. Tại sao không dùng regex để clean HTML?

Không nên làm:

```python
import re

html = re.sub(
    r"<script.*?</script>",
    "",
    html,
)
```

HTML không phải regular language đơn giản.

Ví dụ:

```html
<script>
    const x = "</script>";
</script>
```

Regex rất dễ gặp vấn đề.

BeautifulSoup đã hiểu cấu trúc:

```text
Document
 ├── html
 │   ├── head
 │   └── body
 │       ├── article
 │       ├── p
 │       └── pre
```

Ta thao tác trên **DOM tree** thay vì chuỗi.

---

# 3. Parse HTML

Ví dụ:

```python
from bs4 import BeautifulSoup


html = """
<h1>Python</h1>

<p>Hello <strong>world</strong></p>

<script>
    alert("hello");
</script>
"""

soup = BeautifulSoup(
    html,
    "lxml",
)

print(soup.prettify())
```

BeautifulSoup tạo tree.

---

# 4. `find_all()`

Ví dụ:

```python
scripts = soup.find_all("script")
```

Ta có:

```python
for script in scripts:
    print(script)
```

Có thể xóa:

```python
for script in scripts:
    script.decompose()
```

Sau đó:

```python
print(soup)
```

`script` biến mất.

---

# 5. `decompose()` và `extract()`

Đây là hai method cần phân biệt.

### `decompose()`

```python
tag.decompose()
```

Xóa tag và giải phóng nó.

Dùng khi:

> Tôi chắc chắn muốn loại bỏ element.

### `extract()`

```python
tag.extract()
```

Tách tag khỏi tree nhưng object vẫn tồn tại.

Trong cleaner của chúng ta, chủ yếu dùng:

```python
decompose()
```

vì không cần giữ các element rác.

---

# 6. Những tag chắc chắn có thể loại bỏ

Tạo:

```python
REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "canvas",
    "svg",
}
```

Sau đó:

```python
for tag in soup.find_all(REMOVE_TAGS):
    tag.decompose()
```

BeautifulSoup hỗ trợ:

```python
soup.find_all(
    ["script", "style"]
)
```

hoặc set/list phù hợp.

---

# 7. Tại sao không xóa `<head>`?

Nếu input của chúng ta là fragment:

```html
<h1>Hello</h1>
<p>Python</p>
```

thì không có vấn đề.

Nhưng nếu browser đưa:

```html
<html>
<head>
    <title>Hello</title>
</head>
<body>
    ...
</body>
</html>
```

Ta cần quyết định policy.

Đối với app Clip2MD:

> Chúng ta chỉ quan tâm nội dung người dùng copy.

Do đó có thể bỏ:

```text
html
head
```

và lấy:

```text
body
```

nếu clipboard chứa full document.

Nhưng **không được làm mù quáng**, vì input hiện tại là fragment.

---

# 8. Comment cũng là rác

Ví dụ:

```html
<!-- Google Tag Manager -->

<p>Hello</p>

<!-- advertisement -->

<p>Python</p>
```

Ta muốn:

```html
<p>Hello</p>

<p>Python</p>
```

BeautifulSoup:

```python
from bs4 import Comment
```

Sau đó:

```python
for comment in soup.find_all(
    string=lambda text: isinstance(
        text,
        Comment,
    )
):
    comment.extract()
```

---

# 9. Viết helper `remove_comments`

```python
from bs4 import BeautifulSoup, Comment


def remove_comments(
    soup: BeautifulSoup,
) -> None:

    for comment in soup.find_all(
        string=lambda text: isinstance(
            text,
            Comment,
        )
    ):
        comment.extract()
```

Đây là một nguyên tắc thiết kế tốt:

```text
remove_comments()
remove_unwanted_tags()
remove_hidden_elements()
...
```

thay vì:

```text
clean_html() = 300 dòng
```

---

# 10. Hidden elements

Một website có thể có:

```html
<div style="display:none">
    advertisement
</div>
```

hoặc:

```html
<div hidden>
    tracking
</div>
```

hoặc:

```html
<div aria-hidden="true">
    ...
</div>
```

Ta muốn loại bỏ.

Nhưng phải cẩn thận.

---

# 11. `hidden`

Cách đơn giản:

```python
for tag in soup.find_all(
    attrs={"hidden": True}
):
    tag.decompose()
```

---

# 12. `aria-hidden`

```python
for tag in soup.find_all(
    attrs={"aria-hidden": "true"}
):
    tag.decompose()
```

---

# 13. `style="display:none"`

Không nên parse CSS hoàn chỉnh ở Buổi 4.

Ta chỉ xử lý những pattern rõ ràng:

```python
style = tag.get("style", "")
```

Ví dụ:

```text
display: none
```

hoặc:

```text
visibility: hidden
```

Helper:

```python
def is_hidden_by_style(tag) -> bool:
    style = tag.get("style")

    if not style:
        return False

    style = style.lower().replace(
        " ",
        "",
    )

    return (
        "display:none" in style
        or "visibility:hidden" in style
    )
```

---

# 14. Nhưng đừng xóa `<code>` vì style

Ví dụ hiếm nhưng có thể:

```html
<code style="display:inline">
    print("hello")
</code>
```

Không vấn đề.

Còn:

```html
<pre style="visibility:hidden">
```

thực sự có thể là hidden.

Nguyên tắc:

```text
hidden
    ↓
remove

pre/code
    ↓
preserve unless clearly hidden
```

---

# 15. Tạo `HTMLCleaner`

Tạo:

```text
src/clip2md/cleaner.py
```

Phiên bản đầu:

```python
from bs4 import BeautifulSoup, Comment


REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "canvas",
    "svg",
}


class HTMLCleaner:

    def clean(
        self,
        html: str,
    ) -> str:

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        self._remove_tags(soup)
        self._remove_comments(soup)
        self._remove_hidden(soup)

        return str(soup)
```

---

# 16. `_remove_tags`

```python
def _remove_tags(
    self,
    soup: BeautifulSoup,
) -> None:

    for tag in soup.find_all(
        REMOVE_TAGS
    ):
        tag.decompose()
```

---

# 17. `_remove_comments`

```python
def _remove_comments(
    self,
    soup: BeautifulSoup,
) -> None:

    for comment in soup.find_all(
        string=lambda text: isinstance(
            text,
            Comment,
        )
    ):
        comment.extract()
```

---

# 18. `_remove_hidden`

```python
def _remove_hidden(
    self,
    soup: BeautifulSoup,
) -> None:

    for tag in soup.find_all():

        if tag.has_attr("hidden"):
            tag.decompose()
            continue

        if tag.get(
            "aria-hidden"
        ) == "true":
            tag.decompose()
            continue

        if self._is_hidden_by_style(tag):
            tag.decompose()
```

Helper:

```python
def _is_hidden_by_style(
    self,
    tag,
) -> bool:

    style = tag.get("style")

    if not style:
        return False

    normalized = (
        style
        .lower()
        .replace(" ", "")
    )

    return (
        "display:none" in normalized
        or
        "visibility:hidden" in normalized
    )
```

---

# 19. Test Cleaner

Input:

```html
<h1>Python</h1>

<p>Hello</p>

<script>
    alert("bad");
</script>

<style>
    body {
        color: red;
    }
</style>

<div hidden>
    hidden content
</div>

<!-- tracking -->

<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Chạy:

```python
cleaner = HTMLCleaner()

result = cleaner.clean(html)

print(result)
```

Mong muốn:

```html
<html>
 <body>
  <h1>Python</h1>
  <p>Hello</p>

  <pre><code>
def hello():
    print("Hello")
</code></pre>
 </body>
</html>
```

Điểm quan trọng:

```text
script        ❌
style         ❌
hidden        ❌
comment       ❌

h1            ✅
p             ✅
pre           ✅
code          ✅
```

---

# 20. Tại sao output lại có `<html><body>`?

Bạn sẽ có thể gặp:

```html
<html>
<body>
...
</body>
</html>
```

dù input chỉ là:

```html
<h1>Hello</h1>
```

Đây là do parser:

```python
BeautifulSoup(
    html,
    "lxml",
)
```

có thể chuẩn hóa fragment thành document.

Điều này **không nhất thiết là vấn đề**.

Nhưng với pipeline của chúng ta, ta muốn:

```html
<h1>Hello</h1>
<p>...</p>
```

thay vì:

```html
<html>
<body>
<h1>Hello</h1>
...
</body>
</html>
```

Ta sẽ xử lý chuyện này ở phần normalize.

---

# 21. Fragment vs Document

Đây là một concept rất quan trọng.

Input:

```html
<h1>Hello</h1>
<p>Python</p>
```

là:

```text
HTML fragment
```

Còn:

```html
<html>
<head>...</head>
<body>
...
</body>
</html>
```

là:

```text
HTML document
```

App của chúng ta nhận chủ yếu:

```text
fragment
```

nên cleaner nên giữ semantics của fragment.

---

# 22. Dùng `html.parser` hay `lxml`?

Ta có:

```python
BeautifulSoup(
    html,
    "html.parser",
)
```

hoặc:

```python
BeautifulSoup(
    html,
    "lxml",
)
```

Ở project này mình chọn:

```text
lxml
```

vì:

* nhanh
* parser HTML tốt
* xử lý HTML thực tế tốt
* phù hợp app desktop xử lý clipboard liên tục

Nhưng ta không muốn code phụ thuộc cứng vào parser.

Có thể thiết kế:

```python
class HTMLCleaner:

    def __init__(
        self,
        parser: str = "lxml",
    ):
        self.parser = parser
```

Sau này:

```python
HTMLCleaner(
    parser="html.parser"
)
```

---

# 23. Đây là lúc thiết kế `CleaningPolicy`

Không nên hard-code mọi thứ trong `HTMLCleaner`.

Ví dụ:

```python
@dataclass(slots=True)
class CleaningPolicy:
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_iframes: bool = True
    remove_comments: bool = True
    remove_hidden: bool = True
```

Sau đó:

```python
class HTMLCleaner:

    def __init__(
        self,
        policy: CleaningPolicy | None = None,
    ):
        self.policy = (
            policy
            or CleaningPolicy()
        )
```

---

# 24. Tại sao Policy quan trọng?

Sau này người dùng có thể muốn:

```text
remove_svg = False
```

hoặc:

```text
remove_comments = False
```

hoặc:

```text
keep_iframe = True
```

Không cần sửa `HTMLCleaner`.

Chỉ thay:

```python
policy = CleaningPolicy(
    remove_comments=False,
)
```

Đây là tư duy **configuration over hard-coded behavior**.

---

# 25. `CleaningPolicy` phiên bản đầu

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CleaningPolicy:

    remove_scripts: bool = True

    remove_styles: bool = True

    remove_noscript: bool = True

    remove_iframe: bool = True

    remove_canvas: bool = True

    remove_svg: bool = True

    remove_comments: bool = True

    remove_hidden: bool = True
```

Sau đó tạo tag set:

```python
def build_remove_tags(
    policy: CleaningPolicy,
) -> set[str]:

    tags = set()

    if policy.remove_scripts:
        tags.add("script")

    if policy.remove_styles:
        tags.add("style")

    if policy.remove_noscript:
        tags.add("noscript")

    if policy.remove_iframe:
        tags.add("iframe")

    if policy.remove_canvas:
        tags.add("canvas")

    if policy.remove_svg:
        tags.add("svg")

    return tags
```

---

# 26. Nhưng code có một vấn đề

Ta đang làm:

```python
tags = build_remove_tags(policy)
```

mỗi lần clean.

Không nghiêm trọng, nhưng có thể tạo một `Cleaner` immutable policy:

```python
class HTMLCleaner:

    def __init__(
        self,
        policy: CleaningPolicy | None = None,
    ):
        self.policy = (
            policy
            or CleaningPolicy()
        )

        self._remove_tags = (
            build_remove_tags(self.policy)
        )
```

Sau này clean hàng nghìn clipboard event thì cấu trúc này tốt hơn.

---

# 27. Một nguyên tắc cực kỳ quan trọng: không remove attributes bừa bãi

Bạn có thể nghĩ:

```python
for tag in soup.find_all():
    tag.attrs.clear()
```

**Không được.**

Vì:

```html
<pre class="language-python">
```

có:

```text
class="language-python"
```

và chúng ta cần nó để xác định:

```text
Python code block
```

Tương tự:

```html
<a href="...">
```

cần:

```text
href
```

`img` cần:

```text
src
alt
```

Do đó:

> **Buổi 4 chỉ xóa element rác, chưa xóa attributes.**

Đây là quyết định rất quan trọng để bảo vệ code block và semantic HTML.

---

# 28. Đặc biệt: bảo vệ `<pre>` và `<code>`

Cleaner hiện tại không có:

```python
"pre"
"code"
```

trong:

```python
REMOVE_TAGS
```

Đây là quy tắc bất biến của project:

```text
PRE/CODE = PROTECTED
```

Sau này nếu chúng ta viết quảng cáo detector:

```python
looks_like_ad(tag)
```

thì cũng nên:

```python
if tag.name in {"pre", "code"}:
    return False
```

trừ khi element thực sự bị hidden.

---

# 29. Test code block

Input:

```html
<pre class="language-python">
<code>
def hello(name):
    print(f"Hello {name}")
</code>
</pre>
```

Cleaner phải trả:

```html
<pre class="language-python">
<code>
def hello(name):
    print(f"Hello {name}")
</code>
</pre>
```

**Không được biến thành:**

```html
def hello(name):
    print(...)
```

vì sau này `html2text` cần `<pre>` để sinh fenced code block.

---

# 30. Test inline code

Input:

```html
<p>
    Gọi hàm
    <code>hello()</code>
    để chạy chương trình.
</p>
```

Cleaner phải giữ:

```html
<p>
    Gọi hàm
    <code>hello()</code>
    để chạy chương trình.
</p>
```

Sau này `html2text` sẽ xử lý:

```markdown
Gọi hàm `hello()` để chạy chương trình.
```

---

# 31. Test quảng cáo đơn giản

Input:

```html
<article>

<h1>Python</h1>

<p>Nội dung bài viết.</p>

<div class="advertisement">
    MUA NGAY!
</div>

<p>Tiếp tục nội dung.</p>

</article>
```

**Hiện tại chưa xóa `advertisement`.**

Tại sao?

Vì Buổi 4 chúng ta mới xây:

```text
structural cleaner
```

Buổi sau mới xây:

```text
semantic/ad detector
```

Đây là cách chia architecture hợp lý.

---

# 32. Phân biệt hai loại cleaning

## Structural cleaning

Dựa vào HTML semantics:

```text
script
style
iframe
svg
canvas
noscript
comment
hidden
```

Độ tin cậy cao.

## Semantic cleaning

Dựa vào:

```text
class
id
role
aria-label
text
```

để đoán:

```text
advertisement
banner
social share
newsletter
related article
navigation
```

Độ tin cậy thấp hơn.

Do đó:

```text
Phase 1
Structural cleaning
       ↓
Phase 2
Semantic cleaning
```

Không nên trộn chúng ngay từ đầu.

---

# 33. Kiến trúc hiện tại

Sau Buổi 4:

```text
Chrome
  │
 Ctrl+C
  │
  ▼
ClipboardMonitor
  │
  ▼
ClipboardReader
  │
  ▼
CFHTMLParser
  │
  ▼
HTML Fragment
  │
  ▼
HTMLCleaner
  │
  ├── remove script
  ├── remove style
  ├── remove iframe
  ├── remove svg
  ├── remove canvas
  ├── remove comments
  ├── remove hidden
  │
  └── KEEP pre/code
          │
          ▼
      Clean HTML
```

---

# 34. Bài tập Buổi 4

## Bài 1

Tạo:

```text
cleaner.py
```

với:

```python
CleaningPolicy
HTMLCleaner
```

---

## Bài 2

Cleaner phải xóa:

```text
script
style
noscript
iframe
canvas
svg
comment
hidden
```

---

## Bài 3

Cleaner phải giữ nguyên:

```text
pre
code
```

bao gồm cả:

```text
class="language-python"
```

---

## Bài 4

Test:

```html
<h1>Python</h1>

<script>bad()</script>

<p>Hello <code>print()</code></p>

<pre class="language-python">
<code>
def hello():
    print("Hello")
</code>
</pre>

<div hidden>
    BAD
</div>

<!-- tracking -->
```

Kết quả phải giữ:

```html
<h1>Python</h1>

<p>Hello <code>print()</code></p>

<pre class="language-python">
<code>
def hello():
    print("Hello")
</code>
</pre>
```

---

# 35. Bài tập nâng cao

Viết test để chứng minh:

```python
cleaner.clean(html)
```

**không thay đổi nội dung code**.

Ví dụ:

```python
source = '''
<pre class="language-python"><code>
if x < 10:
    print("Hello & World")
</code></pre>
'''
```

Sau cleaner, nội dung trong `<code>` phải vẫn tương đương.

Đây là test rất quan trọng vì từ Buổi 7 trở đi chúng ta sẽ đặc biệt xử lý code.

---

# 36. Chuẩn bị cho Buổi 5

Buổi 5 chúng ta sẽ xây phần thú vị hơn:

```text
Semantic HTML Cleaner
```

Input:

```html
<div class="advertisement">
    Quảng cáo
</div>

<div id="ad-banner">
    ...
</div>

<aside class="social-share">
    Facebook
    Twitter
</aside>

<div class="newsletter">
    Đăng ký nhận tin
</div>
```

→ tự động phát hiện và loại bỏ.

Ta sẽ thiết kế:

```text
AdDetector
NoiseDetector
CleaningRule
CleaningContext
```

và quan trọng nhất là **scoring thay vì `if "ad" in class` một cách ngây thơ**.

Ví dụ:

```text
class="ad-banner"
       ↓
score +3

id="advertisement"
       ↓
score +5

role="complementary"
       ↓
score +1

tag="aside"
       ↓
score +1

score >= threshold
       ↓
REMOVE
```

Nhưng:

```html
<pre class="language-python">
```

sẽ được **bảo vệ khỏi detector**.

Đây sẽ là nền tảng để app của chúng ta xử lý được HTML copy từ nhiều website khác nhau mà không vô tình xóa nội dung bài viết.
