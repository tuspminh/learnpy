# Buổi 6 — Các option quan trọng của `html2text`

Từ Buổi 6, chúng ta chuyển sang **Configuration Deep Dive**.

Mục tiêu hôm nay không phải học thuộc tất cả option, mà là hiểu:

> **Mỗi option thay đổi stage nào trong quá trình HTML → Markdown?**

Theo tài liệu hiện tại của `html2text`, `HTML2Text` có khá nhiều configuration như `body_width`, `ignore_links`, `ignore_images`, `inline_links`, `protect_links`, `unicode_snob`, `escape_snob`, `skip_internal_links`, `images_as_html`, `images_to_alt`, `ignore_emphasis`, `bypass_tables`, `single_line_break`... ([GitHub][1])

---

# 1. Nhìn tổng thể các option

Ta chia chúng thành 6 nhóm:

```text
HTML2Text Configuration
│
├── 1. Layout
│     ├── body_width
│     ├── single_line_break
│     └── wrap_*
│
├── 2. Link
│     ├── ignore_links
│     ├── inline_links
│     ├── protect_links
│     ├── skip_internal_links
│     └── use_automatic_links
│
├── 3. Image
│     ├── ignore_images
│     ├── images_as_html
│     ├── images_to_alt
│     ├── images_with_size
│     └── default_image_alt
│
├── 4. Formatting
│     ├── ignore_emphasis
│     ├── emphasis_mark
│     ├── strong_mark
│     └── include_sup_sub
│
├── 5. Character
│     ├── unicode_snob
│     ├── escape_snob
│     └── decode_errors
│
└── 6. Table / Code
      ├── bypass_tables
      ├── ignore_tables
      ├── mark_code
      └── backquote_code_style
```

Đây chính là bản đồ mà chúng ta sẽ học trong các Buổi 6–12.

---

# 2. Cách cấu hình `HTML2Text`

Pattern cơ bản:

```python
import html2text

converter = html2text.HTML2Text()

converter.body_width = 0
converter.ignore_links = False
converter.ignore_images = False

markdown = converter.handle(html)
```

Tài liệu chính thức cũng sử dụng cách tạo `HTML2Text()` rồi set thuộc tính trước khi gọi `handle()`. ([GitHub][1])

---

# 3. Option quan trọng nhất: `body_width`

Ta sẽ học riêng rất sâu ở **Buổi 7**, nhưng hôm nay cần biết nó thuộc nhóm:

```text
Layout
```

Ví dụ:

```python
converter.body_width = 80
```

→ wrap output khoảng 80 ký tự.

Hoặc:

```python
converter.body_width = 0
```

→ không wrap dòng. ([GitHub][1])

Trong crawler:

```python
converter.body_width = 0
```

thường là điểm khởi đầu tốt để ta tự kiểm soát formatting sau đó.

---

# 4. `ignore_links`

```python
converter.ignore_links = True
```

HTML:

```html
<a href="https://python.org">
    Python
</a>
```

thay vì:

```markdown
[Python](https://python.org)
```

sẽ bỏ formatting của link.

Nếu:

```python
converter.ignore_links = False
```

thì link được giữ.

Tài liệu PyPI cũng minh họa trực tiếp việc bật/tắt `ignore_links` trên cùng một converter. ([PyPI][2])

---

# 5. `inline_links`

Đây là option rất đáng học kỹ.

Mặc định, link thường được biểu diễn theo kiểu inline:

```markdown
[Python](https://python.org)
```

Nếu chuyển sang reference links:

```markdown
[Python][1]

[1]: https://python.org
```

thì:

```python
converter.inline_links = False
```

sẽ yêu cầu sử dụng reference-style links thay vì inline links. Tài liệu CLI hiện tại mô tả `--reference-links` chính là cơ chế này. ([GitHub][3])

---

# 6. So sánh `inline_links`

### Inline

```markdown
Đọc [Python](https://python.org) để biết thêm.
```

### Reference

```markdown
Đọc [Python][1] để biết thêm.

[1]: https://python.org
```

---

## Khi nào reference links hữu ích?

Một bài viết có:

```text
100 links
```

Nếu dùng inline:

```markdown
[link](https://...)
[link](https://...)
[link](https://...)
...
```

Markdown khá dài.

Reference style:

```markdown
[Python][1]
[HTTPX][2]
[PySide6][3]

[1]: ...
[2]: ...
[3]: ...
```

nội dung chính sạch hơn.

---

# 7. `protect_links`

```python
converter.protect_links = True
```

Mục đích là bảo vệ link khỏi việc wrapping làm hỏng cấu trúc Markdown. Tài liệu mô tả option này là bảo vệ link khỏi line breaks xung quanh link. ([GitHub][1])

Ví dụ:

```text
body_width
    ↓
wrap text
    ↓
link có thể bị ảnh hưởng
```

`protect_links` liên quan trực tiếp đến vấn đề đó.

---

# 8. `skip_internal_links`

Ví dụ:

```html
<a href="#chapter-1">
    Chapter 1
</a>
```

Nếu:

```python
converter.skip_internal_links = True
```

thì anchor nội bộ kiểu:

```text
#chapter-1
#comments
#footer
```

được bỏ qua.

Đây là option rất hữu ích với article crawler.

---

# 9. `use_automatic_links`

Một HTML có thể chứa:

```html
<p>
https://python.org
</p>
```

Converter có thể nhận diện URL trực tiếp và tạo automatic link.

Có thể tắt behavior này bằng:

```python
converter.use_automatic_links = False
```

CLI tương ứng là `--no-automatic-links`. ([GitHub][3])

---

# 10. Nhóm Image

Đây là nhóm rất quan trọng với crawler.

Ta có:

```text
Image Configuration
│
├── ignore_images
├── images_as_html
├── images_to_alt
├── images_with_size
└── default_image_alt
```

---

# 11. `ignore_images`

```python
converter.ignore_images = True
```

HTML:

```html
<img src="python.png" alt="Python">
```

→ bỏ image formatting.

Dùng khi muốn:

```text
HTML
 ↓
Markdown
 ↓
Text only
```

Ví dụ pipeline TTS của bạn:

```text
HTML
 ↓
Cleaner
 ↓
html2text
 ↓
Markdown
 ↓
Text
 ↓
TTS
```

thì image thường không có giá trị.

---

# 12. `images_to_alt`

Option này khác `ignore_images`.

```python
converter.images_to_alt = True
```

Thay vì giữ:

```markdown
![Python](python.png)
```

ta quan tâm đến:

```text
Python
```

Tức là:

```text
image
 ↓
alt text
```

Tài liệu chính thức mô tả option này là bỏ dữ liệu image và chỉ giữ alt text. ([GitHub][1])

---

# 13. So sánh Image options

Giả sử:

```html
<img
    src="python.png"
    alt="Python logo"
>
```

### Bình thường

```markdown
![Python logo](python.png)
```

### `ignore_images`

```python
converter.ignore_images = True
```

→ image bị bỏ.

### `images_to_alt`

```python
converter.images_to_alt = True
```

→ giữ:

```text
Python logo
```

Đây là ba behavior hoàn toàn khác nhau.

---

# 14. `images_as_html`

```python
converter.images_as_html = True
```

Thay vì chuyển image thành Markdown:

```markdown
![Python](python.png)
```

converter có thể giữ image dưới dạng HTML:

```html
<img src="python.png" alt="Python">
```

Điều này hữu ích nếu bạn cần giữ các attribute mà Markdown image cơ bản không biểu diễn đầy đủ.

Tài liệu ghi rõ option này giữ raw HTML image và cố gắng bảo toàn `height`, `width`, `alt`. ([GitHub][1])

---

# 15. `images_with_size`

Nếu kích thước image quan trọng:

```html
<img
    src="python.png"
    width="500"
    height="300"
    alt="Python"
>
```

thì:

```python
converter.images_with_size = True
```

cho phép giữ kích thước bằng raw HTML khi cần. ([GitHub][1])

Đây là trường hợp:

```text
Markdown thuần
     ↓
không đủ metadata
     ↓
Raw HTML
```

---

# 16. `default_image_alt`

Website đôi khi có:

```html
<img src="python.png">
```

không có `alt`.

Bạn có thể đặt:

```python
converter.default_image_alt = "Image"
```

Khi image thiếu alt, converter dùng giá trị mặc định này. Tài liệu hiện tại cho biết mặc định là chuỗi rỗng để duy trì backward compatibility. ([GitHub][1])

---

# 17. Nhóm Formatting

Có:

```text
Formatting
│
├── ignore_emphasis
├── emphasis_mark
├── strong_mark
└── include_sup_sub
```

---

# 18. `ignore_emphasis`

```python
converter.ignore_emphasis = True
```

HTML:

```html
<strong>Python</strong>
```

thay vì:

```markdown
**Python**
```

sẽ bỏ formatting emphasis.

Tài liệu CLI hiện tại gọi đây là `--ignore-emphasis`. ([GitHub][3])

---

# 19. `emphasis_mark`

Theo source hiện tại, `emphasis_mark` là ký tự dùng cho `<em>`. ([GitHub][1])

Ví dụ:

```python
converter.emphasis_mark = "_"
```

có thể tạo:

```markdown
_Python_
```

Thay vì:

```markdown
*Python*
```

---

# 20. `strong_mark`

Tương tự:

```python
converter.strong_mark = "**"
```

dùng cho:

```html
<strong>Python</strong>
```

→

```markdown
**Python**
```

Bạn có thể thay đổi marker.

Ví dụ:

```python
converter.strong_mark = "__"
```

→

```markdown
__Python__
```

Source hiện tại của project cho thấy `emphasis_mark` và `strong_mark` được cấu hình trực tiếp trên `HTML2Text`. ([GitHub][1])

---

# 21. `unicode_snob`

Đây là option chúng ta sẽ học kỹ ở **Buổi 10**.

```python
converter.unicode_snob = True
```

Mục tiêu là ưu tiên Unicode thay vì chuyển một số ký tự về ASCII. Tài liệu mô tả `UNICODE_SNOB` là dùng Unicode trong document. ([GitHub][1])

Ví dụ về mental model:

```text
Unicode
   ↓
ASCII normalization
```

so với:

```text
Unicode
   ↓
giữ Unicode
```

---

# 22. `escape_snob`

```python
converter.escape_snob = True
```

Option này liên quan đến việc escape các ký tự Markdown đặc biệt.

Ví dụ Markdown có:

```text
*
_
[
]
(
)
#
!
```

Nếu nội dung chứa các ký tự này mà converter không xử lý đúng, chúng có thể bị Markdown interpreter hiểu nhầm.

Tài liệu mô tả `ESCAPE_SNOB` là escape các special character. ([GitHub][1])

Ta sẽ học sâu ở **Buổi 12 — Escape Markdown**.

---

# 23. `decode_errors`

Khi decode dữ liệu HTML:

```text
bytes
 ↓
decode
 ↓
str
```

có thể gặp lỗi encoding.

`html2text` hỗ trợ các behavior như:

```python
"strict"
"ignore"
"replace"
```

Tài liệu hiện tại liệt kê đây là các lựa chọn cho `DECODE_ERRORS`. ([GitHub][1])

Ví dụ CLI:

```bash
html2text --decode-errors=replace file.html
```

---

# 24. Table options

Đây là nhóm chúng ta sẽ chưa học sâu ngay.

Có:

```text
bypass_tables
ignore_tables
wrap_tables
pad_tables
```

Ví dụ:

```python
converter.bypass_tables = True
```

có thể yêu cầu giữ bảng dưới dạng HTML thay vì chuyển sang Markdown table. ([GitHub][1])

---

# 25. `single_line_break`

Option này rất đáng nhớ.

```python
converter.single_line_break = True
```

cho phép dùng **một line break** sau block element thay vì hai.

Tài liệu CLI hiện tại lưu ý option này yêu cầu:

```python
body_width = 0
```

([Debian Sources][4])

Ví dụ mental model:

### Bình thường

```markdown
Paragraph 1

Paragraph 2
```

### Single line break

```markdown
Paragraph 1
Paragraph 2
```

Đây là option ta sẽ học sâu ở **Buổi 11**.

---

# 26. `wrap_links`

Có:

```python
converter.wrap_links
```

Nó liên quan đến việc link có được wrap trong quá trình text wrapping hay không.

Đặc biệt quan trọng khi kết hợp:

```text
body_width
+
links
```

Tài liệu hiện tại cũng ghi `--no-wrap-links` và lưu ý nó liên quan đến reference links. ([GitHub][3])

---

# 27. `wrap_list_items`

```python
converter.wrap_list_items = True
```

cho phép wrap nội dung list item khi output bị giới hạn bởi `body_width`. ([GitHub][1])

Ví dụ:

```markdown
* Đây là một list item rất dài...
  và tiếp tục ở dòng tiếp theo.
```

Đây sẽ là vấn đề chúng ta phân tích ở Buổi 7.

---

# 28. `mark_code`

Option:

```python
converter.mark_code = True
```

có thể đánh dấu code block bằng:

```text
[code]
...
[/code]
```

thay vì cách Markdown code block thông thường. Tài liệu hiện tại liệt kê rõ option này. ([GitHub][1])

Điều này khá đặc biệt và **không phải lựa chọn tôi khuyên dùng cho Markdown thông thường**.

---

# 29. Một cấu hình crawler hợp lý

Nếu mục tiêu của chúng ta là:

> Web article → Markdown sạch

thì có thể bắt đầu với:

```python
import html2text


def create_converter() -> html2text.HTML2Text:
    converter = html2text.HTML2Text()

    converter.body_width = 0

    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False

    converter.skip_internal_links = True

    converter.inline_links = True

    converter.unicode_snob = True

    return converter
```

Đây **không phải cấu hình duy nhất đúng**. Nó chỉ là baseline để chúng ta xây tiếp.

---

# 30. Tại sao không nên cấu hình tất cả?

Bạn có thể nghĩ:

```python
converter.ignore_links = False
converter.ignore_images = False
converter.inline_links = True
converter.protect_links = True
converter.unicode_snob = True
converter.escape_snob = True
converter.single_line_break = True
converter.wrap_links = False
converter.wrap_list_items = True
...
```

Nhưng:

> **Nhiều option tương tác với nhau.**

Ví dụ:

```text
body_width
     │
     ├── wrap_links
     ├── wrap_list_items
     └── protect_links
```

hoặc:

```text
images
 │
 ├── ignore_images
 ├── images_to_alt
 ├── images_as_html
 └── images_with_size
```

Nếu bật tất cả mà không hiểu quan hệ giữa chúng, bạn rất dễ tạo output khó kiểm soát.

---

# 31. Cách học configuration chuyên nghiệp

Với mỗi option, hãy dùng cùng một quy trình:

```text
1. HTML input
       ↓
2. Default output
       ↓
3. Bật option
       ↓
4. Output mới
       ↓
5. So sánh
       ↓
6. Hiểu use case
```

Ví dụ `ignore_images`:

```python
html = """
<p>Hello</p>
<img src="python.png" alt="Python">
"""
```

Baseline:

```python
converter.ignore_images = False
```

sau đó:

```python
converter.ignore_images = True
```

so sánh output.

Đây là cách học `html2text` tốt hơn rất nhiều so với học thuộc documentation.

---

# 32. Tạo một `ConverterConfig`

Đây là bước kết nối với những gì bạn đã học về **Clean Architecture / SOLID**.

Thay vì:

```python
converter.body_width = 0
converter.ignore_links = False
converter.ignore_images = False
```

rải rác khắp code, ta có thể tạo:

```python
from dataclasses import dataclass


@dataclass
class MarkdownConfig:
    body_width: int = 0

    ignore_links: bool = False
    ignore_images: bool = False
    ignore_emphasis: bool = False

    inline_links: bool = True
    protect_links: bool = False

    skip_internal_links: bool = True

    unicode_snob: bool = True
```

Sau đó:

```python
config = MarkdownConfig()
```

---

# 33. Adapter từ Config → HTML2Text

```python
import html2text


class MarkdownConverter:

    def __init__(self, config: MarkdownConfig):
        self.config = config

        self.converter = html2text.HTML2Text()

        self.converter.body_width = config.body_width

        self.converter.ignore_links = config.ignore_links
        self.converter.ignore_images = config.ignore_images
        self.converter.ignore_emphasis = config.ignore_emphasis

        self.converter.inline_links = config.inline_links
        self.converter.protect_links = config.protect_links

        self.converter.skip_internal_links = (
            config.skip_internal_links
        )

        self.converter.unicode_snob = config.unicode_snob

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

Sử dụng:

```python
config = MarkdownConfig()

converter = MarkdownConverter(config)

markdown = converter.convert(html)
```

---

# 34. Đây chính là Design Pattern gì?

Về tư duy kiến trúc:

```text
MarkdownConfig
      ↓
MarkdownConverter
      ↓
HTML2Text
```

Ta đang tạo một **Adapter/Facade** đơn giản quanh thư viện bên thứ ba.

Application của chúng ta không cần biết:

```python
html2text.HTML2Text()
```

ở mọi nơi.

Nó chỉ biết:

```python
converter.convert(html)
```

Đây là hướng rất tốt cho project lớn.

---

# 35. Bài tập Buổi 6

## Bài 1 — Option matrix

Tạo HTML:

```python
html = """
<h1>Python</h1>

<p>
Hello <strong>Python</strong>.
</p>

<p>
Visit <a href="https://python.org">Python</a>.
</p>

<img src="python.png" alt="Python logo">

<p>
Use <code>print()</code>.
</p>
"""
```

Test lần lượt:

```text
ignore_links
ignore_images
ignore_emphasis
unicode_snob
inline_links
protect_links
```

---

# 36. Bài 2 — So sánh Image options

Với:

```html
<img
    src="python.png"
    alt="Python logo"
    width="500"
    height="300"
>
```

hãy test:

```python
ignore_images = True
```

```python
images_to_alt = True
```

```python
images_as_html = True
```

```python
images_with_size = True
```

Tạo bảng:

```text
Option              Output
--------------------------------
default             ?
ignore_images       ?
images_to_alt       ?
images_as_html     ?
images_with_size   ?
```

---

# 37. Bài 3 — Link options

Test:

```html
<p>
Python:
<a href="https://python.org">Python</a>
</p>
```

với:

```python
inline_links = True
```

và:

```python
inline_links = False
```

So sánh:

```markdown
[Python](...)
```

với:

```markdown
[Python][1]

[1]: ...
```

---

# 38. Bài 4 — Config object

Viết:

```python
@dataclass
class MarkdownConfig:
    ...
```

và:

```python
class MarkdownConverter:
    ...
```

Mục tiêu:

```python
config = MarkdownConfig(
    body_width=0,
    ignore_links=False,
    ignore_images=False,
)

converter = MarkdownConverter(config)

result = converter.convert(html)
```

---

# 39. Bài 5 — Rất quan trọng

Tạo một test matrix:

```text
HTML
 │
 ├── default
 │
 ├── ignore_links
 │
 ├── ignore_images
 │
 ├── images_to_alt
 │
 ├── images_as_html
 │
 ├── inline_links=False
 │
 ├── unicode_snob=True
 │
 └── escape_snob=True
```

Với mỗi trường hợp, lưu output.

Đây chính là cách chúng ta sẽ bắt đầu xây **test suite cho `MarkdownConverter`**.

---

# 40. Tổng kết Buổi 6

Hôm nay bạn cần nắm được bản đồ:

```text
HTML2Text
│
├── Layout
│   ├── body_width
│   ├── single_line_break
│   └── wrap_*
│
├── Links
│   ├── ignore_links
│   ├── inline_links
│   ├── protect_links
│   ├── skip_internal_links
│   └── use_automatic_links
│
├── Images
│   ├── ignore_images
│   ├── images_to_alt
│   ├── images_as_html
│   ├── images_with_size
│   └── default_image_alt
│
├── Formatting
│   ├── ignore_emphasis
│   ├── emphasis_mark
│   └── strong_mark
│
├── Character
│   ├── unicode_snob
│   ├── escape_snob
│   └── decode_errors
│
└── Advanced
    ├── tables
    ├── code
    └── wrapping
```

Một điều rất quan trọng: **tên và behavior của một số option có thể phụ thuộc phiên bản `html2text` bạn cài**, vì vậy khi học sâu hãy kiểm tra chính `HTML2Text` của phiên bản đang dùng; source hiện tại của project là nguồn tốt để đối chiếu. ([GitHub][3])

### Roadmap tiếp theo

**Buổi 7 — `body_width` Deep Dive**

Chúng ta sẽ không chỉ học:

```python
converter.body_width = 80
```

mà sẽ phân tích sâu:

```text
body_width
    │
    ├── paragraph wrapping
    ├── link wrapping
    ├── list wrapping
    ├── table wrapping
    ├── code block
    ├── long URL
    └── body_width = 0
```

và đặc biệt là **vì sao `body_width=0` thường là lựa chọn đáng cân nhắc trong crawler → Markdown pipeline**.

[1]: https://github.com/Alir3z4/html2text/blob/master/docs/usage.md?utm_source=chatgpt.com "html2text/docs/usage.md at master · Alir3z4/html2text · GitHub"
[2]: https://pypi.org/project/html2text/?utm_source=chatgpt.com "html2text · PyPI"
[3]: https://github.com/Alir3z4/html2text/blob/master/html2text/cli.py?utm_source=chatgpt.com "html2text/html2text/cli.py at master · Alir3z4/html2text · GitHub"
[4]: https://sources.debian.org/src/python-html2text/2020.1.16-1/html2text/cli.py?utm_source=chatgpt.com "File: cli.py | Debian Sources"
