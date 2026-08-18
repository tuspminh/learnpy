# Buổi 6 — HTML Normalization: chuẩn hóa HTML trước khi chuyển sang Markdown

Đến đây app của chúng ta đã có:

```text
Browser
   ↓ Ctrl+C
Clipboard
   ↓
CF_HTML Parser
   ↓
Structural Cleaner
   ↓
Semantic Cleaner
   ↓
???
   ↓
html2text
   ↓
Markdown
   ↓
Clipboard
```

Phần `???` chính là **HTML Normalizer**.

Đây là một tầng rất quan trọng.

Nếu đưa HTML từ website trực tiếp vào `html2text`, kết quả thường có:

* khoảng trắng thừa
* `<br>` lộn xộn
* `<div>` lồng nhau
* heading không nhất quán
* link rác
* image tracking
* code block bị hỏng
* inline code bị xuống dòng
* `<pre>` bị xử lý sai

Hôm nay chúng ta thiết kế:

```text
Clean HTML
    │
    ▼
HTMLNormalizer
    │
    ├── normalize whitespace
    ├── normalize <br>
    ├── normalize headings
    ├── normalize links
    ├── normalize images
    ├── normalize code blocks
    └── protect semantic structure
    │
    ▼
Normalized HTML
    │
    ▼
html2text
```

---

# 1. Tại sao cần Normalizer?

Ví dụ website gửi:

```html
<div>
    <div>
        <div>
            <h1>
                Python
            </h1>
        </div>
    </div>
</div>
```

Về mặt HTML không sai.

Nhưng ta muốn Markdown:

```markdown
# Python
```

Không phải:

```markdown
# Python
```

với 15 dòng whitespace trước/sau.

---

# 2. Cleaner và Normalizer khác nhau

Đây là distinction rất quan trọng.

## Cleaner

Nhiệm vụ:

> Xóa thứ không cần.

Ví dụ:

```html
<script>...</script>
```

→ xóa.

```html
<div class="advertisement">
```

→ xóa.

---

## Normalizer

Nhiệm vụ:

> Giữ nội dung nhưng đưa nó về một dạng HTML nhất quán.

Ví dụ:

```html
<p>
    Hello
</p>
```

và:

```html
<p>Hello</p>
```

về cùng semantic structure.

---

# 3. Tạo `normalizer.py`

```text
src/clip2md/html/normalizer.py
```

Skeleton:

```python
from bs4 import BeautifulSoup


class HTMLNormalizer:

    def normalize(
        self,
        soup: BeautifulSoup,
    ) -> None:

        self._normalize_headings(soup)
        self._normalize_breaks(soup)
        self._normalize_links(soup)
        self._normalize_images(soup)
        self._normalize_code(soup)
```

---

# 4. Nguyên tắc quan trọng

Normalizer **không nên stringify rồi parse lại nhiều lần**.

Không làm:

```python
html = str(soup)

soup = BeautifulSoup(
    html,
    "lxml",
)

...
```

liên tục.

Mỗi lần parse lại có thể:

* thay đổi structure
* thay đổi whitespace
* thay đổi entities
* làm mất thông tin

Tốt nhất:

```text
parse 1 lần
   ↓
clean
   ↓
normalize
   ↓
convert
```

---

# 5. Normalize heading

HTML có:

```html
<h1>Title</h1>
<h2>Chapter</h2>
<h3>Section</h3>
```

Ta **không cần đổi heading**.

`html2text` đã hiểu:

```html
<h1>Title</h1>
```

→

```markdown
# Title
```

Vấn đề là website đôi khi dùng:

```html
<div class="title">
    Python
</div>
```

Đừng vội biến tất cả `.title` thành `<h1>`.

Vì:

```text
title
```

không đảm bảo là heading.

Do đó Buổi 6:

> **Không đoán heading bằng class.**

Chỉ normalize heading thật.

---

# 6. Xử lý `<br>`

Ví dụ:

```html
<p>
Hello<br>
World
</p>
```

Markdown mong muốn:

```markdown
Hello
World
```

`html2text` thường xử lý được.

Do đó không nên biến:

```html
<br>
```

thành:

```html
<p></p>
```

hoặc:

```html
<br><br><br>
```

một cách tùy tiện.

---

# 7. Vấn đề `<br><br><br>`

Website có thể copy:

```html
Hello
<br>
<br>
<br>
World
```

Nếu đưa thẳng vào converter:

```markdown
Hello



World
```

rất xấu.

Ta có thể normalize chuỗi `<br>` liên tiếp.

Ví dụ:

```html
Hello<br><br><br>World
```

→

```html
Hello<br><br>World
```

Giữ tối đa 2 `<br>` liên tiếp.

---

# 8. Implement `_normalize_breaks`

```python
def _normalize_breaks(
    self,
    soup: BeautifulSoup,
) -> None:

    for parent in soup.find_all():

        breaks = parent.find_all(
            "br",
            recursive=False,
        )

        if len(breaks) <= 2:
            continue
```

Nhưng cách này **chưa đúng**, vì `find_all()` chỉ trả toàn bộ `<br>` trực tiếp chứ không biết chúng có liên tiếp nhau hay không.

Ta cần duyệt children.

---

# 9. Duyệt children

BeautifulSoup:

```python
for child in parent.children:
    ...
```

Ta có thể nhận:

```text
NavigableString
Tag
NavigableString
Tag
...
```

Để xử lý chính xác, ta cần:

```python
from bs4 import Tag
```

---

# 10. Xử lý chuỗi `<br>`

Một helper:

```python
def _count_consecutive_breaks(
    parent: Tag,
) -> None:
    ...
```

Nhưng implementation trực tiếp sẽ phức tạp.

Một cách đơn giản cho phiên bản đầu:

```python
def _normalize_breaks(
    self,
    soup: BeautifulSoup,
) -> None:

    for br in soup.find_all("br"):
        previous = br.find_previous_sibling()

        if (
            previous
            and getattr(
                previous,
                "name",
                None,
            ) == "br"
        ):
            br.decompose()
```

Điều này sẽ biến:

```html
<br><br><br>
```

thành:

```html
<br>
```

Đây là aggressive hơn một chút.

Tôi khuyên version đầu tiên giữ tối đa **1 `<br>` liên tiếp**, vì Markdown converter thường tự xử lý paragraph spacing.

---

# 11. Nhưng `<br>` trong code thì sao?

Ví dụ:

```html
<code>
foo<br>bar
</code>
```

Nếu normalize `<br>`:

```text
foo
bar
```

có thể làm thay đổi code.

Do đó:

```python
if br.find_parent(
    ["pre", "code"]
):
    continue
```

Đây là pattern chúng ta sẽ sử dụng rất nhiều:

```text
outside code
    → normalize

inside code
    → preserve
```

---

# 12. Quy tắc vàng của project

Từ giờ mọi normalizer rule phải hỏi:

```text
Element có nằm trong <pre>/<code> không?
```

Nếu:

```text
YES
```

→ **không đụng vào nội dung**.

Helper:

```python
def _is_code_context(
    self,
    tag: Tag,
) -> bool:

    return (
        tag.find_parent("pre") is not None
        or tag.find_parent("code") is not None
    )
```

---

# 13. `pre` và `code` không giống nhau

Đây là concept quan trọng.

## Inline code

```html
<p>
Dùng <code>print()</code>
</p>
```

Markdown:

```markdown
Dùng `print()`
```

## Block code

```html
<pre><code>
print("hello")
</code></pre>
```

Markdown:

````markdown
```python
print("hello")
```
````

Do đó pipeline phải phân biệt:

```text
code
 ├── inline
 │
 └── inside pre
      → block code
```

---

# 14. Normalize code block

Website thường có:

```html
<pre>
<code class="language-python">
def hello():
    print("Hello")
</code>
</pre>
```

Đây là structure rất tốt.

Ta **không nên** chuyển nó thành:

```html
<code>
...
</code>
```

hoặc:

```html
<div>
...
</div>
```

Giữ nguyên:

```html
<pre><code class="language-python">...</code></pre>
```

---

# 15. Code language

Class:

```html
<code class="language-python">
```

có thông tin:

```text
language = python
```

Một số website dùng:

```html
class="lang-python"
```

hoặc:

```html
class="language-javascript"
```

hoặc:

```html
class="highlight-python"
```

Trong Buổi 6 ta chưa cần convert.

Chỉ cần:

> **Không xóa class của `<code>`.**

---

# 16. Đây là lý do Buổi 4 không xóa attributes

Nếu trước đó ta làm:

```python
tag.attrs.clear()
```

thì:

```html
<code class="language-python">
```

trở thành:

```html
<code>
```

mất metadata ngôn ngữ.

Vì vậy quyết định ở Buổi 4 là chính xác.

---

# 17. Normalize links

Website có thể copy:

```html
<a href="https://example.com">
    Python
</a>
```

Ta giữ:

```html
<a href="https://example.com">
    Python
</a>
```

`html2text` sẽ tạo:

```markdown
[Python](https://example.com)
```

Không cần tự convert sang Markdown.

---

# 18. Link rác

Nhưng có những link:

```html
<a href="javascript:void(0)">
    Share
</a>
```

hoặc:

```html
<a href="#">
```

Đây không phải useful link.

Ta có thể normalize thành text.

Ví dụ:

```html
<a href="#">
    Python
</a>
```

→

```html
Python
```

---

# 19. `javascript:` cần loại bỏ

Helper:

```python
def _is_bad_href(
    href: str | None,
) -> bool:

    if not href:
        return True

    normalized = href.strip().lower()

    return (
        normalized == "#"
        or normalized.startswith(
            "javascript:"
        )
    )
```

---

# 20. Normalize link

```python
def _normalize_links(
    self,
    soup: BeautifulSoup,
) -> None:

    for tag in soup.find_all("a"):

        href = tag.get("href")

        if self._is_bad_href(href):
            tag.unwrap()
```

`unwrap()`:

```html
<a href="#">
    Python
</a>
```

→

```html
Python
```

Rất hữu ích.

---

# 21. `unwrap()` vs `decompose()`

Buổi này cần nhớ:

### `decompose()`

```python
tag.decompose()
```

→ xóa cả element + nội dung.

### `unwrap()`

```python
tag.unwrap()
```

→ xóa tag nhưng **giữ nội dung**.

Ví dụ:

```html
<a href="#">
    Python
</a>
```

`decompose()`:

```text
''
```

`unwrap()`:

```text
Python
```

Với bad link:

> Dùng `unwrap()`.

---

# 22. Images

Website:

```html
<img src="https://example.com/logo.png">
```

`html2text` sẽ tạo:

```markdown
![...](...)
```

Nhưng clipboard có thể chứa tracking image:

```html
<img
    src="https://tracker.example.com/pixel.gif"
    width="1"
    height="1"
>
```

Buổi 6 có thể loại bỏ image rõ ràng là tracking pixel.

---

# 23. Tracking pixel detection

Điều kiện:

```text
width <= 1
height <= 1
```

Ví dụ:

```python
def _is_tracking_pixel(
    tag: Tag,
) -> bool:

    width = tag.get("width")
    height = tag.get("height")

    return (
        width == "1"
        and height == "1"
    )
```

Nhưng CSS có thể:

```html
style="width:1px;height:1px"
```

Ta có thể mở rộng sau.

---

# 24. Đừng xóa image chỉ vì không có `alt`

Ví dụ:

```html
<img src="python-diagram.png">
```

không có `alt`.

Vẫn có thể là hình ảnh hữu ích.

Do đó:

```text
no alt
    ≠
bad image
```

Đừng dùng rule:

```python
if not alt:
    remove()
```

---

# 25. Xử lý image

```python
def _normalize_images(
    self,
    soup: BeautifulSoup,
) -> None:

    for tag in soup.find_all("img"):

        if self._is_tracking_pixel(tag):
            tag.decompose()
```

Tạm thời chỉ vậy.

---

# 26. Whitespace là phần khó nhất

Ví dụ:

```html
<p>
    Hello
    <strong>
        Python
    </strong>
    world
</p>
```

Ta không muốn biến text thành:

```text
HelloPythonworld
```

mà:

```text
Hello Python world
```

Nhưng nếu `.strip()` mọi text node:

```python
text.strip()
```

có thể làm mất whitespace cần thiết.

---

# 27. Đừng `.get_text(strip=True)` toàn bộ document

Một lỗi rất phổ biến:

```python
text = soup.get_text(
    strip=True
)
```

Sau đó dựng HTML lại.

Làm vậy sẽ phá:

* `<pre>`
* `<code>`
* whitespace
* paragraph boundaries
* inline formatting

Ví dụ:

```html
Hello <code>foo()</code> world
```

có thể trở thành:

```text
Hellofoo()world
```

Đối với project này:

> **Không dùng `get_text()` để rebuild document.**

---

# 28. Whitespace chỉ xử lý ngoài code

Ta có thể normalize các text node ngoài code.

Ví dụ:

```python
from bs4 import NavigableString
```

Sau đó:

```python
for text_node in soup.find_all(
    string=True
):
    ...
```

Nhưng cần kiểm tra:

```python
parent = text_node.parent

if parent.name in {
    "pre",
    "code",
}:
    continue
```

---

# 29. Normalize whitespace đơn giản

```python
import re


def _normalize_text_node(
    text: str,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        text,
    )
```

Ví dụ:

```text
"Hello     world"
```

→

```text
"Hello world"
```

Nhưng có một vấn đề:

```html
<p>
Hello
</p>

<p>
World
</p>
```

Text node normalization không được biến toàn bộ thành một dòng.

May mắn là chúng ta chỉ thay whitespace **trong từng text node**, còn `<p>` vẫn giữ structure.

---

# 30. Không normalize whitespace trong `<pre>`

Ví dụ:

```python
def _normalize_whitespace(
    self,
    soup: BeautifulSoup,
) -> None:

    for text_node in soup.find_all(
        string=True
    ):

        parent = text_node.parent

        if parent is None:
            continue

        if parent.name in {
            "pre",
            "code",
        }:
            continue

        text_node.replace_with(
            _normalize_text_node(
                str(text_node)
            )
        )
```

Đây là phiên bản đầu tiên.

---

# 31. Nhưng có thể làm hỏng leading whitespace

Ví dụ:

```html
<p>
    Hello
</p>
```

Text node:

```text
"\n    Hello\n"
```

normalize:

```text
" Hello "
```

Không quá nghiêm trọng với `html2text`, nhưng không đẹp.

Ta có thể tinh chỉnh:

```python
re.sub(
    r"[ \t]+",
    " ",
    text,
)
```

chỉ collapse spaces/tabs, giữ newline.

```python
def _normalize_text_node(
    text: str,
) -> str:

    return re.sub(
        r"[ \t]+",
        " ",
        text,
    )
```

Đây là lựa chọn an toàn hơn.

---

# 32. Nhưng newline trong text node?

Ví dụ:

```html
<p>Hello
world</p>
```

HTML rendering có thể tương đương:

```text
Hello world
```

Browser collapse whitespace.

Vì vậy nếu muốn mô phỏng browser:

```python
re.sub(
    r"\s+",
    " ",
    text,
)
```

là hợp lý **ngoài pre/code**.

Tôi chọn:

```python
r"\s+"
```

cho semantic text.

---

# 33. Bảo vệ code bằng helper

Ta tạo:

```python
def is_code_element(
    tag: Tag,
) -> bool:

    if tag.name in {
        "pre",
        "code",
    }:
        return True

    return (
        tag.find_parent(
            ["pre", "code"]
        )
        is not None
    )
```

Sau đó mọi rule:

```python
if is_code_element(tag):
    continue
```

---

# 34. Nhưng inline `<code>` vẫn cần normalize parent

Ví dụ:

```html
<p>
    Hello
    <code>
        print()
    </code>
    world
</p>
```

`<code>` giữ nguyên.

Nhưng text:

```text
Hello
```

và:

```text
world
```

có thể normalize.

Đó chính là behavior chúng ta muốn.

---

# 35. Normalize `<pre><code>`

Một website có thể copy:

```html
<pre>
    <code class="language-python">
        print("hello")
    </code>
</pre>
```

Trong code block, whitespace đầu cuối thường là indentation của HTML formatting chứ không phải code thực sự.

Nhưng **không được `.strip()` tùy tiện**.

Ví dụ:

```python
<pre>
<code>
    def hello():
        print("hello")
</code>
</pre>
```

Indentation có thể là formatting artifact.

Xử lý code indentation chính xác là một topic riêng.

Do đó Buổi 6:

> **Không sửa nội dung bên trong `<pre>`.**

Đây là quyết định an toàn.

---

# 36. Tại sao không format code ở đây?

Vì code có thể là:

```python
def hello():
    if x:
        print("hello")
```

hoặc:

```javascript
function hello() {
    console.log("hello");
}
```

hoặc:

```text
    SQL
```

Nếu ta tự `dedent()`:

```python
textwrap.dedent(...)
```

có thể đúng với một số website nhưng sai với website khác.

Buổi sau chúng ta sẽ thiết kế **CodeBlockProcessor** riêng.

---

# 37. `HTMLNormalizer` phiên bản đầu

```python
import re

from bs4 import BeautifulSoup, Tag


class HTMLNormalizer:

    def normalize(
        self,
        soup: BeautifulSoup,
    ) -> None:

        self._normalize_breaks(soup)
        self._normalize_links(soup)
        self._normalize_images(soup)
        self._normalize_whitespace(soup)

    def _normalize_breaks(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for br in soup.find_all("br"):

            if self._is_code_context(br):
                continue

            previous = br.find_previous_sibling()

            if (
                previous is not None
                and getattr(
                    previous,
                    "name",
                    None,
                ) == "br"
            ):
                br.decompose()

    def _normalize_links(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for tag in soup.find_all("a"):

            href = tag.get("href")

            if self._is_bad_href(href):
                tag.unwrap()

    def _normalize_images(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for tag in soup.find_all("img"):

            if self._is_tracking_pixel(tag):
                tag.decompose()

    def _normalize_whitespace(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for text_node in soup.find_all(
            string=True
        ):

            parent = text_node.parent

            if parent is None:
                continue

            if self._is_code_context(
                parent
            ):
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                str(text_node),
            )

            text_node.replace_with(
                normalized
            )

    @staticmethod
    def _is_code_context(
        tag: Tag,
    ) -> bool:

        return (
            tag.name in {"pre", "code"}
            or tag.find_parent(
                ["pre", "code"]
            )
            is not None
        )

    @staticmethod
    def _is_bad_href(
        href: str | None,
    ) -> bool:

        if not href:
            return True

        href = href.strip().lower()

        return (
            href == "#"
            or href.startswith(
                "javascript:"
            )
        )

    @staticmethod
    def _is_tracking_pixel(
        tag: Tag,
    ) -> bool:

        return (
            tag.get("width") == "1"
            and tag.get("height") == "1"
        )
```

---

# 38. Một lỗi nhỏ trong `_is_code_context`

Ta có:

```python
tag.find_parent(["pre", "code"])
```

nhưng nếu:

```python
tag.name == "pre"
```

thì `find_parent()` không tính chính nó.

Vì vậy:

```python
tag.name in {"pre", "code"}
```

phải có.

Ta đã làm đúng:

```python
return (
    tag.name in {"pre", "code"}
    or tag.find_parent(
        ["pre", "code"]
    ) is not None
)
```

---

# 39. Pipeline Clean → Normalize

Bây giờ:

```python
from bs4 import BeautifulSoup

from clip2md.html.cleaner import HTMLCleaner
from clip2md.html.normalizer import HTMLNormalizer


soup = BeautifulSoup(
    html,
    "lxml",
)

cleaner.clean(soup)

normalizer.normalize(soup)

result = str(soup)
```

Pipeline:

```text
HTML
 │
 ▼
BeautifulSoup
 │
 ▼
HTMLCleaner
 │
 ▼
SemanticCleaner
 │
 ▼
HTMLNormalizer
 │
 ▼
str(soup)
```

---

# 40. Nhưng thứ tự cũng rất quan trọng

Không nên:

```text
Normalize
   ↓
Clean
```

vì semantic detector có thể dựa vào:

```text
class
id
aria-label
```

và cleaner có thể xóa element.

Nếu normalize trước mà thay đổi structure, detector có thể thay đổi kết quả.

Do đó:

```text
1. Parse
2. Structural clean
3. Semantic clean
4. Normalize
5. Convert
```

là hợp lý.

---

# 41. Test toàn bộ pipeline

Input:

```html
<article>

<h1>
    Python
</h1>

<p>
    Đây là bài học về
    <code>asyncio</code>.
</p>

<div class="advertisement">
    BUY NOW
</div>

<p>
    Ví dụ:
</p>

<pre class="language-python"><code>
async def main():
    await asyncio.sleep(1)
    print("Hello")
</code></pre>

<a href="#">
    Link không hợp lệ
</a>

<a href="https://python.org">
    Python
</a>

<img
    src="pixel.gif"
    width="1"
    height="1"
>

<p>
    Nội dung cuối.
</p>

</article>
```

Sau:

```text
StructuralCleaner
        ↓
SemanticCleaner
        ↓
Normalizer
```

Ta muốn:

```html
<article>
<h1>Python</h1>

<p>
 Đây là bài học về
 <code>asyncio</code>.
</p>

<p>
 Ví dụ:
</p>

<pre class="language-python"><code>
async def main():
    await asyncio.sleep(1)
    print("Hello")
</code></pre>

Python

<p>
 Nội dung cuối.
</p>
</article>
```

---

# 42. Sau này `html2text` sẽ xử lý

HTML:

```html
<h1>Python</h1>

<p>
Đây là
<code>asyncio</code>.
</p>

<pre class="language-python"><code>
async def main():
    await asyncio.sleep(1)
</code></pre>
```

→ Markdown:

````markdown
# Python

Đây là `asyncio`.

```python
async def main():
    await asyncio.sleep(1)
````

````

Đây chính là output chúng ta muốn.

---

# 43. Nhưng `html2text` có thể không nhận language class theo đúng cách

Đây là vấn đề của **Buổi 7**.

Chúng ta cần kiểm tra:

```html
<pre>
<code class="language-python">
...
</code>
</pre>
````

có chuyển thành:

````markdown
```python
...
```
````

hay không.

Nếu không:

```text
HTML
 ↓
CodeBlockProcessor
 ↓
<pre data-language="python">
...
</pre>
 ↓
html2text
```

Hoặc một custom conversion rule.

Đây sẽ là phần rất quan trọng.

---

# 44. Một nguyên tắc kiến trúc mới

Đừng để:

```python
HTMLNormalizer
```

biết về:

```text
Markdown
```

Nó chỉ biết HTML.

Sai:

```python
if markdown:
    ...
```

Đúng:

```text
HTMLCleaner
    ↓
HTMLNormalizer
    ↓
HTML
    ↓
MarkdownConverter
```

Mỗi layer có một responsibility.

---

# 45. Cấu trúc project hiện tại

```text
clip2md/
│
├── pyproject.toml
│
├── src/
│   └── clip2md/
│
│       ├── clipboard/
│       │   ├── reader.py
│       │   ├── writer.py
│       │   ├── cf_html.py
│       │   └── monitor.py
│       │
│       ├── html/
│       │   ├── policy.py
│       │   ├── cleaner.py
│       │   ├── detector.py
│       │   ├── semantic.py
│       │   └── normalizer.py
│       │
│       └── markdown/
│           └── converter.py
│
└── tests/
```

Kiến trúc này đã bắt đầu giống một thư viện thật thay vì một script.

---

# 46. Bài tập Buổi 6

### Bài 1

Implement:

```python
HTMLNormalizer
```

---

### Bài 2

Test bad link:

```html
<a href="#">Hello</a>
```

phải trở thành:

```html
Hello
```

---

### Bài 3

Test:

```html
<a href="javascript:void(0)">
    Hello
</a>
```

phải trở thành:

```html
Hello
```

---

### Bài 4

Test valid link:

```html
<a href="https://python.org">
    Python
</a>
```

**không được unwrap**.

---

### Bài 5

Test:

```html
<br><br><br>
```

phải giảm xuống tối đa:

```html
<br>
```

---

### Bài 6

Test:

```html
<pre>
<code>
    a     b
        c
</code>
</pre>
```

Normalizer **không được thay đổi whitespace bên trong code**.

Đây là test quan trọng nhất.

---

# 47. Bài tập nâng cao — viết unit test

Ví dụ:

```python
def test_preserve_code():
    html = """
    <pre>
    <code class="language-python">
    def hello():
        print("hello")
    </code>
    </pre>
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    normalizer.normalize(soup)

    code = soup.find("code")

    assert code is not None
    assert "language-python" in (
        code.get("class") or []
    )
```

Và quan trọng hơn:

```python
original = code.get_text()

normalizer.normalize(soup)

assert (
    code.get_text()
    == original
)
```

---

# 48. Bài tập integration

Viết:

```python
def clean_html(
    html: str,
) -> str:

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    structural_cleaner.clean(soup)

    semantic_cleaner.clean(soup)

    normalizer.normalize(soup)

    return str(soup)
```

Test bằng một HTML chứa đồng thời:

```text
✓ heading
✓ paragraph
✓ inline code
✓ code block
✓ link
✓ image
✓ advertisement
✓ social
✓ script
✓ comment
✓ hidden
✓ excessive whitespace
```

Nếu pipeline pass được test này thì chúng ta đã có **HTML preprocessing engine phiên bản 1**.

---

# 49. Kiến trúc sau Buổi 6

```text
                   Browser
                      │
                    Ctrl+C
                      │
                      ▼
             ┌─────────────────┐
             │ ClipboardMonitor│
             └────────┬────────┘
                      ▼
             ┌─────────────────┐
             │ ClipboardReader │
             └────────┬────────┘
                      ▼
                  CF_HTML
                      │
                      ▼
             ┌─────────────────┐
             │ BeautifulSoup   │
             └────────┬────────┘
                      ▼
          ┌────────────────────────┐
          │ Structural Cleaner     │
          └───────────┬────────────┘
                      ▼
          ┌────────────────────────┐
          │ Semantic Cleaner       │
          │                        │
          │ Detector → Score       │
          └───────────┬────────────┘
                      ▼
          ┌────────────────────────┐
          │ HTML Normalizer        │
          │                        │
          │ links                  │
          │ images                 │
          │ breaks                 │
          │ whitespace             │
          │ code protection        │
          └───────────┬────────────┘
                      ▼
                 Clean HTML
                      │
                      ▼
                  html2text
```

## Buổi 7

Chúng ta sẽ bắt đầu **`html2text` Deep Dive**, nhưng không dùng kiểu:

```python
markdown = html2text.html2text(html)
```

rồi xong.

Ta sẽ xây một `MarkdownConverter` có cấu hình rõ ràng và đặc biệt xử lý:

```text
<pre>
<code class="language-python">
```

→

````markdown
```python
...
```
````

đồng thời giữ:

```text
inline <code>
nested code
indentation
language detection
links
headings
lists
tables
```

Sau Buổi 7, pipeline sẽ thực sự có khả năng biến **HTML copy từ browser → Markdown sạch**, thay vì chỉ là HTML cleaner.
