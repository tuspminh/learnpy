# Buổi 7 — Xây `MarkdownConverter`: HTML → Markdown, bảo vệ Code Block & Inline Code

Hôm nay chúng ta bước vào phần **core của Clip2MD**.

Pipeline hiện tại:

```text
Browser
   │
   │ Ctrl+C
   ▼
Clipboard
   │
   ▼
CF_HTML Parser
   │
   ▼
BeautifulSoup
   │
   ├── StructuralCleaner
   │
   ├── SemanticCleaner
   │
   └── HTMLNormalizer
   │
   ▼
Clean HTML
   │
   ▼
MarkdownConverter   ← BUỔI 7
   │
   ▼
Markdown
   │
   ▼
Clipboard
```

Mục tiêu hôm nay:

> Xây một lớp `MarkdownConverter` có cấu hình, thay vì gọi `html2text.html2text()` trực tiếp.

---

# 1. Vì sao không gọi trực tiếp `html2text.html2text()`?

Cách đơn giản:

```python
import html2text

markdown = html2text.html2text(html)
```

Có thể đủ với demo.

Nhưng app của chúng ta có yêu cầu đặc biệt:

```text
✓ giữ heading
✓ giữ paragraph
✓ giữ list
✓ giữ link
✓ giữ inline code
✓ giữ code block
✓ nhận diện language
✓ không phá indentation
✓ không tạo Markdown rác
```

Do đó cần:

```text
MarkdownConverter
       │
       ├── cấu hình html2text
       ├── preprocess
       ├── convert
       └── postprocess
```

---

# 2. Cài `html2text`

Nếu chưa cài:

```bash
pip install html2text
```

Kiểm tra:

```bash
python -c "import html2text; print(html2text.__version__)"
```

---

# 3. Tạo module

```text
src/
└── clip2md/
    └── markdown/
        ├── __init__.py
        └── converter.py
```

Skeleton:

```python
import html2text


class MarkdownConverter:

    def convert(
        self,
        html: str,
    ) -> str:

        return html2text.html2text(
            html
        )
```

Nhưng chúng ta sẽ không dừng ở đây.

---

# 4. Tìm hiểu `HTML2Text`

Thư viện cung cấp class:

```python
html2text.HTML2Text
```

Thay vì:

```python
html2text.html2text(html)
```

ta có thể:

```python
converter = html2text.HTML2Text()

markdown = converter.handle(html)
```

Điểm quan trọng:

```text
html2text.html2text()
```

là convenience API.

Còn:

```text
HTML2Text
```

cho chúng ta khả năng cấu hình.

---

# 5. Tạo converter object

```python
import html2text


class MarkdownConverter:

    def __init__(self) -> None:

        self._converter = (
            html2text.HTML2Text()
        )
```

Sau đó:

```python
def convert(
    self,
    html: str,
) -> str:

    return self._converter.handle(
        html
    )
```

---

# 6. Cấu hình `body_width`

Một vấn đề rất khó chịu của `html2text`:

Markdown có thể bị wrap:

```markdown
Python là một ngôn ngữ lập trình
mạnh mẽ và phổ biến.
```

Trong khi ta muốn:

```markdown
Python là một ngôn ngữ lập trình mạnh mẽ và phổ biến.
```

Để tắt wrapping:

```python
self._converter.body_width = 0
```

Đây là setting rất quan trọng cho Clip2MD.

---

# 7. Vì sao `body_width = 0`?

Nếu:

```python
body_width = 80
```

thì converter có thể tạo:

```markdown
Python là một ngôn ngữ lập trình mạnh mẽ và
phổ biến.
```

Điều này không sai Markdown.

Nhưng đối với app copy:

```text
Browser
 ↓
Copy
 ↓
Markdown
```

người dùng thường muốn:

> Markdown gần với cấu trúc gốc nhất có thể.

Do đó:

```python
body_width = 0
```

---

# 8. `ignore_links`

Chúng ta muốn giữ link.

Không dùng:

```python
ignore_links = True
```

Mà:

```python
self._converter.ignore_links = False
```

Ví dụ:

```html
<a href="https://python.org">
Python
</a>
```

→

```markdown
[Python](https://python.org)
```

---

# 9. `ignore_images`

Đây là policy cần suy nghĩ.

Nếu:

```python
ignore_images = True
```

thì:

```html
<img src="python.png" alt="Python">
```

bị bỏ.

Nhưng user có thể muốn giữ hình.

Với app Clip2MD, tôi khuyên:

```python
ignore_images = False
```

Cleaner sẽ quyết định image tracking nào cần xóa.

Converter chỉ convert.

---

# 10. `escape_snob`

HTML có:

```html
<p>
Python _rocks_
</p>
```

Markdown converter có thể cần escape ký tự Markdown.

Tùy cấu hình.

Đây là setting chúng ta nên để mặc định trước.

Đừng chỉnh mọi option ngay từ đầu.

Nguyên tắc:

> Chỉ thay đổi behavior mà project thực sự cần.

---

# 11. Cấu hình converter

Phiên bản đầu:

```python
import html2text


class MarkdownConverter:

    def __init__(self) -> None:

        converter = html2text.HTML2Text()

        converter.body_width = 0
        converter.ignore_links = False
        converter.ignore_images = False

        self._converter = converter

    def convert(
        self,
        html: str,
    ) -> str:

        return self._converter.handle(
            html
        )
```

---

# 12. Test cơ bản

Input:

```html
<h1>Python</h1>

<p>
Python là ngôn ngữ lập trình.
</p>
```

Output mong muốn:

```markdown
# Python

Python là ngôn ngữ lập trình.
```

---

# 13. Paragraph

Input:

```html
<p>Hello</p>
<p>World</p>
```

Output:

```markdown
Hello

World
```

Đây chính là behavior chúng ta cần.

---

# 14. Bold / italic

Input:

```html
<p>
Hello <strong>Python</strong>
</p>
```

→

```markdown
Hello **Python**
```

Italic:

```html
<em>Python</em>
```

→

```markdown
*Python*
```

---

# 15. Inline code

Input:

```html
<p>
Dùng <code>print()</code>
</p>
```

Mục tiêu:

```markdown
Dùng `print()`
```

Đây là test bắt buộc.

---

# 16. Code block

Input:

```html
<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Ta muốn:

````markdown
```text
def hello():
    print("Hello")
```
````

Đây là nơi cần đặc biệt chú ý.

---

# 17. Chạy thử `html2text`

Với code:

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 0

html = """
<pre><code>
def hello():
    print("Hello")
</code></pre>
"""

print(converter.handle(html))
```

Kết quả thực tế có thể không đúng chính xác format mà chúng ta muốn tùy phiên bản/cấu hình.

Đây là lý do:

> Không nên giả định behavior của converter.

Ta phải viết test.

---

# 18. Code block language

Input:

```html
<pre>
<code class="language-python">
def hello():
    print("Hello")
</code>
</pre>
```

Ta muốn:

````markdown
```python
def hello():
    print("Hello")
```
````

Nhưng `html2text` không phải lúc nào cũng biến `language-python` thành fenced code với language identifier theo cách chúng ta muốn.

Vì vậy:

```text
HTML
 │
 ▼
CodeBlockProcessor
 │
 ▼
Normalized code block
 │
 ▼
html2text
```

---

# 19. Tại sao xử lý code trước `html2text`?

Nếu chờ sau khi convert:

```text
HTML
 ↓
html2text
 ↓
Markdown
 ↓
tìm code
```

chúng ta phải parse Markdown.

Việc đó phức tạp hơn.

Nếu xử lý trước:

```text
HTML
 ↓
BeautifulSoup
 ↓
CodeBlockProcessor
 ↓
html2text
```

chúng ta vẫn có DOM.

DOM dễ xử lý hơn Markdown text.

---

# 20. Tạo `CodeBlockProcessor`

File:

```text
src/clip2md/markdown/code.py
```

```python
from bs4 import BeautifulSoup, Tag


class CodeBlockProcessor:

    def process(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for pre in soup.find_all("pre"):
            self._process_pre(pre)

    def _process_pre(
        self,
        pre: Tag,
    ) -> None:
        ...
```

---

# 21. Tìm `<code>` bên trong `<pre>`

```python
code = pre.find("code")
```

Nếu:

```html
<pre>
    <code>...</code>
</pre>
```

thì:

```python
code is not None
```

Nếu:

```html
<pre>
    raw text
</pre>
```

thì:

```python
code is None
```

Cả hai đều là code block.

---

# 22. Detect language

Helper:

```python
def detect_language(
    code: Tag,
) -> str | None:

    for class_name in (
        code.get("class") or []
    ):
        if class_name.startswith(
            "language-"
        ):
            return class_name[
                len("language-"):
            ]

    return None
```

Ví dụ:

```html
<code class="language-python">
```

→

```text
python
```

---

# 23. Hỗ trợ `lang-*`

Một số site:

```html
<code class="lang-python">
```

Ta hỗ trợ:

```python
if class_name.startswith("lang-"):
    return class_name[5:]
```

---

# 24. Hỗ trợ `language`

Một số site:

```html
<code class="language-python highlight">
```

ta duyệt tất cả class:

```python
for class_name in code.get(
    "class",
    []
):
    ...
```

Không cần class phải đứng đầu.

---

# 25. Version đầy đủ

```python
def detect_language(
    code: Tag,
) -> str | None:

    classes = code.get(
        "class"
    ) or []

    for class_name in classes:

        if class_name.startswith(
            "language-"
        ):
            return class_name[
                9:
            ]

        if class_name.startswith(
            "lang-"
        ):
            return class_name[
                5:
            ]

    return None
```

---

# 26. Nhưng chưa đủ

Một số syntax highlighter dùng:

```html
class="highlight language-python"
```

→ OK.

Nhưng có website dùng:

```html
<pre data-language="python">
```

Ta hỗ trợ:

```python
language = pre.get(
    "data-language"
)
```

---

# 27. Ưu tiên language

Nếu cả:

```html
<pre data-language="javascript">
<code class="language-python">
```

thì nên ưu tiên `<code>`:

```text
code.language-python
        ↓
python
```

vì `<code>` gần nội dung hơn.

Algorithm:

```text
1. code.language-*
2. code.lang-*
3. pre.data-language
4. None
```

---

# 28. Code block phải được bảo vệ

Ta không muốn `HTMLNormalizer` sau đó làm:

```text
normalize whitespace
```

vào code.

Thứ tự:

```text
Cleaner
 ↓
Normalizer
 ↓
CodeBlockProcessor
 ↓
Converter
```

hoặc:

```text
Cleaner
 ↓
CodeBlockProcessor
 ↓
Normalizer
```

?

Tôi khuyên:

```text
Cleaner
 ↓
Normalizer
 ↓
CodeBlockProcessor
 ↓
Converter
```

nhưng `Normalizer` phải **bảo vệ `<pre>/<code>`**.

Chúng ta đã thiết kế như vậy ở Buổi 6.

---

# 29. Một cách đơn giản để đưa language vào HTML

Ví dụ:

```html
<pre>
<code class="language-python">
...
</code>
</pre>
```

Ta giữ nguyên class.

Sau đó `CodeBlockProcessor` có thể thêm:

```html
<pre data-clip2md-language="python">
```

Nhưng:

> `html2text` không nhất thiết hiểu attribute này.

Vì vậy đây chỉ là metadata cho pipeline của chúng ta.

---

# 30. Một chiến lược tốt hơn

Không cố ép `html2text` làm mọi thứ.

Ta có:

```text
HTML
 │
 ├── normal content
 │      ↓
 │   html2text
 │
 └── code block
        ↓
   CodeBlockProcessor
        ↓
   special marker
```

Sau đó replace marker.

Ví dụ:

```text
@@CLIP2MD_CODE_0@@
```

---

# 31. Vì sao marker?

Giả sử HTML:

```html
<p>Hello</p>

<pre><code class="language-python">
print("Hello")
</code></pre>

<p>World</p>
```

Ta biến thành:

```html
<p>Hello</p>

<p>
@@CLIP2MD_CODE_0@@
</p>

<p>World</p>
```

Lưu code:

```python
code_blocks = {
    "0": {
        "language": "python",
        "code": 'print("Hello")',
    }
}
```

Sau `html2text`:

```markdown
Hello

@@CLIP2MD_CODE_0@@

World
```

Sau đó:

```text
@@CLIP2MD_CODE_0@@
```

→

````markdown
```python
print("Hello")
```
````

Đây là một architecture rất mạnh.

---

# 32. Tạo `CodeBlock`

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CodeBlock:
    marker: str
    code: str
    language: str | None
```

Ví dụ:

```python
CodeBlock(
    marker="@@CLIP2MD_CODE_0@@",
    code='print("Hello")',
    language="python",
)
```

---

# 33. `CodeBlockProcessor`

```python
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag


@dataclass(slots=True)
class CodeBlock:
    marker: str
    code: str
    language: str | None


class CodeBlockProcessor:

    def process(
        self,
        soup: BeautifulSoup,
    ) -> list[CodeBlock]:

        blocks = []

        for index, pre in enumerate(
            soup.find_all("pre")
        ):
            block = self._extract(
                pre,
                index,
            )

            blocks.append(block)

        return blocks
```

---

# 34. `_extract`

```python
def _extract(
    self,
    pre: Tag,
    index: int,
) -> CodeBlock:

    code_tag = pre.find("code")

    if code_tag is not None:
        code = code_tag.get_text(
            keep_separator=True
        )
    else:
        code = pre.get_text(
            keep_separator=True
        )

    language = None

    if code_tag is not None:
        language = detect_language(
            code_tag
        )

    marker = (
        f"@@CLIP2MD_CODE_{index}@@"
    )

    return CodeBlock(
        marker=marker,
        code=code,
        language=language,
    )
```

---

# 35. `keep_separator=True`

Đây là điểm rất quan trọng.

Không dùng:

```python
get_text(strip=True)
```

vì code:

```python
def hello():
    print("Hello")
```

cần giữ newline.

Dùng:

```python
get_text(
    keep_separator=True
)
```

để bảo vệ cấu trúc.

---

# 36. Nhưng marker phải thay thế `<pre>`

Sau khi extract:

```python
pre.replace_with(marker)
```

Kết quả:

```html
<p>
@@CLIP2MD_CODE_0@@
</p>
```

Sau đó `html2text`.

---

# 37. Hoàn chỉnh processor

```python
class CodeBlockProcessor:

    def process(
        self,
        soup: BeautifulSoup,
    ) -> list[CodeBlock]:

        blocks = []

        for index, pre in enumerate(
            soup.find_all("pre")
        ):

            code_tag = pre.find("code")

            if code_tag is not None:
                code = code_tag.get_text(
                    keep_separator=True
                )
            else:
                code = pre.get_text(
                    keep_separator=True
                )

            language = (
                detect_language(code_tag)
                if code_tag is not None
                else None
            )

            marker = (
                f"@@CLIP2MD_CODE_{index}@@"
            )

            blocks.append(
                CodeBlock(
                    marker=marker,
                    code=code,
                    language=language,
                )
            )

            pre.replace_with(marker)

        return blocks
```

---

# 38. Sau đó `MarkdownConverter`

```python
class MarkdownConverter:

    def __init__(self) -> None:

        converter = html2text.HTML2Text()

        converter.body_width = 0
        converter.ignore_links = False
        converter.ignore_images = False

        self._converter = converter
        self._code_processor = (
            CodeBlockProcessor()
        )
```

---

# 39. Convert

```python
def convert(
    self,
    html: str,
) -> str:

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    blocks = self._code_processor.process(
        soup
    )

    markdown = self._converter.handle(
        str(soup)
    )

    return self._restore_code_blocks(
        markdown,
        blocks,
    )
```

---

# 40. Restore

```python
def _restore_code_blocks(
    self,
    markdown: str,
    blocks: list[CodeBlock],
) -> str:

    for block in blocks:

        fenced = self._format_code_block(
            block
        )

        markdown = markdown.replace(
            block.marker,
            fenced,
        )

    return markdown
```

---

# 41. Format fenced code

````python
def _format_code_block(
    self,
    block: CodeBlock,
) -> str:

    language = (
        block.language or ""
    )

    return (
        f"```{language}\n"
        f"{block.code}"
        f"\n```"
    )
````

---

# 42. Có một lỗi subtle

Nếu:

```python
block.code
```

đã kết thúc bằng:

```text
\n
```

thì:

````python
f"{code}\n```"
````

sẽ tạo:

```text
print()

```

````

thừa newline.

Ta cần normalize ending:

```python
code = block.code.rstrip("\n")
````

Nhưng **không được strip spaces đầu dòng**.

Do đó:

```python
code = block.code.rstrip("\n")
```

rất khác:

```python
code = block.code.strip()
```

---

# 43. Đừng dùng `.strip()` cho code

Sai:

```python
code.strip()
```

Vì:

```text
    hello()
```

có thể mất indentation đầu.

Đúng:

```python
code.rstrip("\n")
```

Chỉ loại newline cuối.

---

# 44. `_format_code_block`

````python
def _format_code_block(
    self,
    block: CodeBlock,
) -> str:

    language = (
        block.language or ""
    )

    code = block.code.rstrip(
        "\n"
    )

    return (
        f"```{language}\n"
        f"{code}\n"
        f"```"
    )
````

---

# 45. Nhưng còn inline `<code>`?

Chúng ta **không đưa inline code vào processor**.

Chỉ:

```python
soup.find_all("pre")
```

Như vậy:

```html
<p>
Dùng <code>print()</code>
</p>
```

được để `html2text` xử lý.

Đây là quyết định rất quan trọng:

```text
<code> ngoài <pre>
        ↓
html2text

<code> trong <pre>
        ↓
CodeBlockProcessor
```

---

# 46. Đây chính là semantic distinction

```text
CODE
 │
 ├── inline
 │      <code>
 │
 └── block
        <pre>
          └── <code>
```

Không được xử lý chúng giống nhau.

---

# 47. Test inline code

```python
def test_inline_code():

    html = """
    <p>
        Dùng <code>print()</code>
    </p>
    """

    markdown = converter.convert(
        html
    )

    assert "`print()`" in markdown
```

---

# 48. Test Python code block

````python
def test_python_code_block():

    html = """
    <pre>
    <code class="language-python">
def hello():
    print("Hello")
    </code>
    </pre>
    """

    markdown = converter.convert(
        html
    )

    assert (
        "```python"
        in markdown
    )

    assert (
        'print("Hello")'
        in markdown
    )
````

---

# 49. Test JavaScript

```html
<pre>
<code class="language-javascript">
function hello() {
    console.log("Hello");
}
</code>
</pre>
```

Mong muốn:

````markdown
```javascript
function hello() {
    console.log("Hello");
}
```
````

---

# 50. Test code không có language

Input:

```html
<pre><code>
SELECT *
FROM users;
</code></pre>
```

Output:

````markdown
```
SELECT *
FROM users;
```
````

Không được:

````markdown
```None
````

Do đó:

```python
language = block.language or ""
```

---

# 51. Code chứa triple backticks

Đây là edge case rất quan trọng.

Code:

````text
print("```")
````

Nếu ta tạo:

````markdown
```
print("```")
```
````

Markdown fence có thể bị phá.

Giải pháp là tìm fence dài hơn nội dung.

Ví dụ code chứa:

````text
```
````

thì dùng:

`````markdown
````python
code
```
````
`````

---

# 52. Hàm tính fence

```python
import re


def _fence_for(
    code: str,
) -> str:

    matches = re.findall(
        r"`{3,}",
        code,
    )

    longest = max(
        (
            len(match)
            for match in matches
        ),
        default=0,
    )

    return "`" * max(
        3,
        longest + 1,
    )
```

Ví dụ:

````text
code không có ```
→ ```

Không, vì `max(3, ...)`:

```text
→ ```
````

Code có:

```text
```

````

→

```text
````

````

---

# 53. Format bằng dynamic fence

```python
def _format_code_block(
    self,
    block: CodeBlock,
) -> str:

    code = block.code.rstrip(
        "\n"
    )

    fence = _fence_for(code)

    language = (
        block.language or ""
    )

    return (
        f"{fence}{language}\n"
        f"{code}\n"
        f"{fence}"
    )
````

Đây là implementation production tốt hơn.

---

# 54. Code block có dấu `\r\n`

Windows clipboard rất có thể chứa:

```text
\r\n
```

Chúng ta nên normalize line ending **ở code processor**, nhưng phải cẩn thận.

```python
code = code.replace(
    "\r\n",
    "\n",
)
```

và:

```python
code = code.replace(
    "\r",
    "\n",
)
```

Sau đó toàn pipeline dùng:

```text
\n
```

---

# 55. Tạo helper

```python
def normalize_newlines(
    text: str,
) -> str:

    return (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
```

Dùng cho code.

---

# 56. Tại sao chỉ code?

Toàn Markdown output của `html2text` cũng có thể có line ending.

Nhưng sau converter ta có thể normalize toàn output:

```python
markdown = markdown.replace(
    "\r\n",
    "\n",
)
```

Đây là hợp lý.

---

# 57. Markdown cleanup

Sau khi convert:

```python
markdown = markdown.strip()
```

Ở **Markdown output** thì `.strip()` an toàn hơn rất nhiều so với code source.

Sau đó:

```python
return markdown + "\n"
```

Có thể đảm bảo file/clipboard kết thúc bằng newline.

Ví dụ:

```python
markdown = markdown.strip()

if markdown:
    markdown += "\n"

return markdown
```

---

# 58. MarkdownConverter hoàn chỉnh phiên bản Buổi 7

```python
import html2text
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag


@dataclass(slots=True)
class CodeBlock:
    marker: str
    code: str
    language: str | None


class CodeBlockProcessor:

    def process(
        self,
        soup: BeautifulSoup,
    ) -> list[CodeBlock]:

        blocks = []

        for index, pre in enumerate(
            soup.find_all("pre")
        ):

            code_tag = pre.find("code")

            if code_tag is not None:
                code = code_tag.get_text(
                    keep_separator=True
                )
            else:
                code = pre.get_text(
                    keep_separator=True
                )

            code = (
                code
                .replace("\r\n", "\n")
                .replace("\r", "\n")
            )

            language = (
                self.detect_language(
                    code_tag
                )
                if code_tag is not None
                else None
            )

            marker = (
                f"@@CLIP2MD_CODE_{index}@@"
            )

            blocks.append(
                CodeBlock(
                    marker=marker,
                    code=code,
                    language=language,
                )
            )

            pre.replace_with(marker)

        return blocks

    @staticmethod
    def detect_language(
        code: Tag,
    ) -> str | None:

        classes = code.get(
            "class"
        ) or []

        for class_name in classes:

            if class_name.startswith(
                "language-"
            ):
                return class_name[9:]

            if class_name.startswith(
                "lang-"
            ):
                return class_name[5:]

        return None


class MarkdownConverter:

    def __init__(self) -> None:

        converter = html2text.HTML2Text()

        converter.body_width = 0
        converter.ignore_links = False
        converter.ignore_images = False

        self._converter = converter

        self._code_processor = (
            CodeBlockProcessor()
        )

    def convert(
        self,
        html: str,
    ) -> str:

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        blocks = (
            self._code_processor.process(
                soup
            )
        )

        markdown = (
            self._converter.handle(
                str(soup)
            )
        )

        markdown = (
            self._restore_code_blocks(
                markdown,
                blocks,
            )
        )

        markdown = (
            markdown
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip()
        )

        if markdown:
            markdown += "\n"

        return markdown

    def _restore_code_blocks(
        self,
        markdown: str,
        blocks: list[CodeBlock],
    ) -> str:

        for block in blocks:

            fenced = (
                self._format_code_block(
                    block
                )
            )

            markdown = markdown.replace(
                block.marker,
                fenced,
            )

        return markdown

    @staticmethod
    def _format_code_block(
        block: CodeBlock,
    ) -> str:

        code = block.code.rstrip(
            "\n"
        )

        fence = MarkdownConverter._fence_for(
            code
        )

        language = (
            block.language or ""
        )

        return (
            f"{fence}{language}\n"
            f"{code}\n"
            f"{fence}"
        )

    @staticmethod
    def _fence_for(
        code: str,
    ) -> str:

        matches = re.findall(
            r"`{3,}",
            code,
        )

        longest = max(
            (
                len(match)
                for match in matches
            ),
            default=0,
        )

        return "`" * max(
            3,
            longest + 1,
        )
```

---

# 59. Nhưng có một vấn đề kiến trúc

Hiện tại:

```text
MarkdownConverter
       │
       ├── html2text
       │
       └── CodeBlockProcessor
```

Tốt.

Nhưng:

```python
MarkdownConverter._format_code_block()
```

đang chứa logic Markdown.

Có thể tách:

```text
markdown/
├── converter.py
├── code.py
└── formatter.py
```

Ví dụ:

```python
class FencedCodeFormatter:
    ...
```

Nhưng **chưa cần** ở Buổi 7.

Đừng over-engineer quá sớm.

---

# 60. Pipeline hoàn chỉnh sau Buổi 7

```text
                  Ctrl+C
                    │
                    ▼
             Clipboard HTML
                    │
                    ▼
              CF_HTML Parser
                    │
                    ▼
              BeautifulSoup
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 Structural    Semantic      Normalize
 Cleaner       Cleaner       HTML
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
            CodeBlockProcessor
                    │
              ┌─────┴─────┐
              │           │
           inline       block
            code         code
              │           │
              │       marker
              │           │
              └─────┬─────┘
                    ▼
                 html2text
                    │
                    ▼
             Restore code block
                    │
                    ▼
                Markdown
```

---

# 61. Một quyết định rất quan trọng

Từ bây giờ:

### `html2text` chịu trách nhiệm

```text
HTML semantics
    ↓
Markdown semantics

<p>       → paragraph
<h1>      → heading
<strong>  → bold
<em>      → italic
<a>       → link
<ul>      → list
<ol>      → ordered list
<code>    → inline code
```

### CodeBlockProcessor chịu trách nhiệm

```text
<pre><code>
       ↓
fenced code block
```

### HTML Cleaner chịu trách nhiệm

```text
script
style
advertisement
tracking
navigation noise
```

Đây là separation of responsibility rất quan trọng.

---

# 62. Test matrix

Tạo:

```text
tests/test_markdown_converter.py
```

Tối thiểu:

```text
test_heading
test_paragraph
test_bold
test_italic
test_link
test_image
test_inline_code
test_python_code_block
test_javascript_code_block
test_code_without_language
test_code_with_backticks
test_windows_newline
```

Đặc biệt:

```text
inline code
```

và:

```text
code block
```

phải có test riêng.

---

# 63. Test quan trọng nhất

Input:

```html
<p>
Dùng <code>asyncio.run()</code>
để chạy coroutine.
</p>

<pre>
<code class="language-python">
async def main():
    await asyncio.sleep(1)
    print("Hello")
</code>
</pre>
```

Output mong muốn:

````markdown
Dùng `asyncio.run()` để chạy coroutine.

```python
async def main():
    await asyncio.sleep(1)
    print("Hello")
```
````

Nếu test này pass:

> Kiến trúc converter của chúng ta đang đi đúng hướng.

---

# 64. Bài tập Buổi 7

### Bài 1

Cài và tìm hiểu:

```python
html2text.HTML2Text
```

Thử các option:

```python
body_width
ignore_links
ignore_images
```

---

### Bài 2

Viết:

```python
MarkdownConverter
```

với:

```python
converter.body_width = 0
```

---

### Bài 3

Test:

```html
<code>print()</code>
```

→

```markdown
`print()`
```

---

### Bài 4

Implement:

```python
CodeBlockProcessor
```

---

### Bài 5

Hỗ trợ:

```text
language-python
lang-python
data-language
```

---

### Bài 6

Test:

```text
Python
JavaScript
Rust
SQL
unknown
```

---

### Bài 7 — quan trọng

Test code:

````text
print("```")
````

và đảm bảo output sử dụng fence dài hơn.

---

# 65. Sau Buổi 7, project đã có "engine"

Chúng ta đã đi từ một ý tưởng:

```text
"copy HTML rồi chuyển Markdown"
```

đến architecture:

```text
Clipboard
    │
    ▼
CF_HTML
    │
    ▼
HTML Parser
    │
    ▼
Structural Cleaner
    │
    ▼
Semantic Cleaner
    │
    ▼
HTML Normalizer
    │
    ▼
Code Processor
    │
    ▼
html2text
    │
    ▼
Code Restore
    │
    ▼
Markdown
```

**Buổi 8** sẽ xử lý một vấn đề cực kỳ thực tế: **Markdown output cleanup**. Chúng ta sẽ xây `MarkdownCleaner` để loại bỏ blank line dư thừa, heading lỗi, list lỗi, link/image rác còn sót, normalize newline, và quan trọng nhất là **không được làm hỏng fenced code block khi cleanup Markdown**. Sau đó chúng ta sẽ ghép toàn bộ HTML → Markdown thành một `ConversionPipeline` hoàn chỉnh.
