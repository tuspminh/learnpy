# Buổi 7 — `body_width` Deep Dive

Hôm nay chúng ta đào sâu một option tưởng đơn giản nhưng ảnh hưởng rất lớn đến chất lượng Markdown:

```python
converter.body_width
```

Nếu bạn dùng `html2text` để **crawl bài viết → Markdown**, hiểu `body_width` rất quan trọng.

---

# 1. `body_width` là gì?

`body_width` quy định độ rộng dòng mà `html2text` dùng khi **wrap text**.

Ví dụ:

```python
converter.body_width = 40
```

Nếu có đoạn:

```html
<p>
Python is a powerful programming language
that is easy to learn.
</p>
```

output có thể được wrap thành các dòng ngắn hơn.

Mental model:

```text
HTML
 │
 ▼
html2text
 │
 ▼
text wrapping
 │
 ▼
Markdown
```

`body_width` tác động chủ yếu ở bước:

```text
text wrapping
```

---

# 2. Test đầu tiên

Hãy chạy:

```python
import html2text

html = """
<p>
Python is a powerful programming language that is easy to learn.
</p>
"""

converter = html2text.HTML2Text()
converter.body_width = 40

print(converter.handle(html))
```

Bạn sẽ thấy paragraph được chia dòng.

Đừng quá quan tâm chính xác từng vị trí xuống dòng lúc đầu.

Điều quan trọng là:

```text
body_width = 40
       ↓
wrap output
```

---

# 3. `body_width = 80`

```python
converter.body_width = 80
```

Tư duy:

```text
80 characters / line
```

Output sẽ ít dòng hơn so với:

```python
body_width = 40
```

So sánh:

```text
40
 ↓
nhiều line break

80
 ↓
ít line break
```

---

# 4. `body_width = 0`

Đây là giá trị đặc biệt quan trọng:

```python
converter.body_width = 0
```

Nó yêu cầu không thực hiện body wrapping theo độ rộng thông thường.

Ví dụ:

```python
converter = html2text.HTML2Text()
converter.body_width = 0

markdown = converter.handle(html)
```

Mental model:

```text
body_width = 0

HTML
 ↓
html2text
 ↓
không ép wrap theo column width
 ↓
Markdown
```

Đây là configuration tôi thường ưu tiên **khi muốn giữ output ổn định để xử lý tiếp bằng pipeline riêng**.

---

# 5. Tại sao crawler thường thích `body_width = 0`?

Giả sử website có:

```html
<p>
Python is a programming language designed to emphasize readability.
</p>
```

Nếu:

```python
body_width = 40
```

ta có thể nhận:

```markdown
Python is a programming language
designed to emphasize readability.
```

Nhưng nếu lưu database:

```text
content
```

thì line wrapping này thường **không mang semantic information**.

Ta chỉ muốn:

```markdown
Python is a programming language designed to emphasize readability.
```

Sau đó renderer Markdown sẽ tự quyết định cách hiển thị.

---

# 6. Presentation vs Content

Đây là một khái niệm rất quan trọng.

### `body_width = 40`

Bạn đang yêu cầu:

```text
converter
    ↓
Markdown content
    +
presentation-oriented wrapping
```

### `body_width = 0`

Bạn gần hơn với:

```text
converter
    ↓
Markdown semantic content
```

Trong pipeline:

```text
Crawler
   ↓
Parser
   ↓
Cleaner
   ↓
Markdown
   ↓
Database
```

ta thường không muốn converter tự quyết định quá nhiều presentation.

---

# 7. Ví dụ với database

Giả sử lưu:

```python
chapter.content
```

Nếu `body_width=40`:

```text
Python is a powerful programming
language that is easy to learn.
```

Nếu sau này đọc trên:

```text
Desktop
Tablet
Phone
```

thì line wrapping đã bị cố định trong database.

Trong khi:

```text
body_width = 0
```

cho phép lưu content ít phụ thuộc vào UI hơn.

---

# 8. `body_width` và Markdown renderer

Markdown:

```markdown
Python is a powerful programming language
that is easy to learn.
```

và:

```markdown
Python is a powerful programming language that is easy
to learn.
```

về mặt paragraph vẫn có thể được renderer coi là cùng một paragraph, tùy quy tắc Markdown/rendering.

Vì vậy:

> line wrapping trong source Markdown không nhất thiết tương đương với line wrapping trên màn hình.

Đây là lý do không nên nhầm:

```text
source formatting
```

với:

```text
rendered formatting
```

---

# 9. Nhưng `body_width` không phải chỉ ảnh hưởng paragraph

Đây là phần quan trọng.

Ta có:

```text
body_width
│
├── paragraph
├── list
├── link
├── table
├── blockquote
└── một số text blocks khác
```

Do đó không thể hiểu đơn giản:

```text
body_width = "paragraph width"
```

mà chính xác hơn là:

> **độ rộng mục tiêu cho quá trình wrapping của output body.**

---

# 10. `body_width` + list

HTML:

```html
<ul>
    <li>
        Python is a powerful programming language
        that is easy to learn.
    </li>
    <li>
        Rust focuses on safety and performance.
    </li>
</ul>
```

Với:

```python
converter.body_width = 40
```

Markdown có thể được wrap:

```markdown
* Python is a powerful programming
  language that is easy to learn.
* Rust focuses on safety and
  performance.
```

Bạn sẽ thấy indentation của dòng tiếp theo rất quan trọng.

---

# 11. `wrap_list_items`

Đây là option liên quan trực tiếp.

```python
converter.wrap_list_items = True
```

Nó cho phép list item được wrap theo body width.

Mental model:

```text
body_width
     │
     ▼
list item quá dài
     │
     ▼
wrap_list_items
     │
     ▼
continuation line
```

Ví dụ:

```markdown
* Đây là một nội dung rất dài
  được tiếp tục ở dòng kế tiếp.
```

---

# 12. `wrap_list_items = False`

Nếu không muốn converter tự wrap list item:

```python
converter.wrap_list_items = False
```

thì behavior sẽ khác.

Trong crawler, nếu mục tiêu là output canonical và sau đó bạn có bước formatting riêng, bạn nên kiểm thử option này thay vì mặc định tin tưởng output.

---

# 13. `body_width` + link

Đây là nơi mọi chuyện bắt đầu phức tạp.

HTML:

```html
<p>
Visit
<a href="https://www.example.com/a/very/long/path/to/article">
this article
</a>
for more information.
</p>
```

Markdown:

```markdown
Visit [this article](https://www.example.com/a/very/long/path/to/article)
for more information.
```

Nếu:

```python
body_width = 40
```

converter phải quyết định:

```text
wrap trước link?
wrap sau link?
wrap URL?
không wrap link?
```

---

# 14. `wrap_links`

Đây là option liên quan đến vấn đề trên.

Mental model:

```text
body_width
      │
      ▼
long link
      │
      ├── wrap_links = True
      │
      └── wrap_links = False
```

Trong tài liệu/source của `html2text`, option này kiểm soát việc link có tham gia quá trình wrapping hay không.

---

# 15. `protect_links`

Một option khác:

```python
converter.protect_links = True
```

Nó nhằm bảo vệ link khỏi việc wrapping gây ra output Markdown không mong muốn.

Do đó:

```text
body_width
   │
   ├── wrap_links
   │
   └── protect_links
```

là một nhóm configuration nên học cùng nhau.

---

# 16. Đừng test từng option riêng lẻ

Sai:

```text
test body_width
test wrap_links
test protect_links
```

mà không kết hợp.

Tốt hơn:

```text
Case A
body_width = 40
wrap_links = True
protect_links = False

Case B
body_width = 40
wrap_links = False
protect_links = True
```

Sau đó so sánh.

Đây chính là **configuration interaction testing**.

---

# 17. `body_width` + blockquote

HTML:

```html
<blockquote>
    Python is a powerful programming language
    that focuses on readability.
</blockquote>
```

Khi width nhỏ, Markdown có thể cần:

```markdown
> Python is a powerful programming
> language that focuses on
> readability.
```

Ở đây wrapping phải đồng thời đảm bảo:

```text
line wrapping
+
blockquote marker
```

Không thể chỉ dùng:

```python
textwrap.fill()
```

một cách đơn giản sau khi conversion.

---

# 18. Vì sao không nên tự `textwrap.fill()` toàn bộ Markdown?

Giả sử:

````markdown
# Python

```python
def hello():
    print("Hello")
```

> Python is great.
````

Nếu bạn làm:

```python
import textwrap

result = textwrap.fill(markdown, width=40)
```

có nguy cơ phá:

```text
heading
code block
blockquote
list
Markdown syntax
```

Ví dụ:

````text
```python
def hello():
    print(
        "Hello"
    )
````

````

có thể bị xử lý như text bình thường.

**Không nên.**

---

# 19. Code block và `body_width`

Đây là một nguyên tắc quan trọng:

> **Code block phải được coi là opaque content.**

Ví dụ:

```python
def hello():
    if True:
        print("Hello")
````

Không được biến thành:

```python
def hello():
    if True:
    print("Hello")
```

Do đó khi test:

```python
converter.body_width = 20
```

hãy đặc biệt kiểm tra `<pre><code>`.

---

# 20. Test code block

```python
html = """
<pre><code>
def hello():
    print("Hello World")
</code></pre>
"""

converter = html2text.HTML2Text()
converter.body_width = 20

print(converter.handle(html))
```

Kiểm tra:

```text
Indentation có thay đổi không?
Code có bị wrap không?
Fence có bị phá không?
```

Đây là test bắt buộc nếu converter dùng cho documentation.

---

# 21. `body_width` + table

HTML:

```html
<table>
    <tr>
        <th>Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Python</td>
        <td>Programming language</td>
    </tr>
</table>
```

Nếu converter tạo Markdown table:

```markdown
| Name   | Description          |
|--------|----------------------|
| Python | Programming language |
```

thì width trở thành vấn đề khác:

```text
table formatting
       +
column width
       +
body_width
```

Vì vậy table có configuration riêng và chúng ta sẽ không gom nó vào logic paragraph.

---

# 22. `body_width` + Unicode

Ví dụ:

```text
Python là ngôn ngữ lập trình rất mạnh.
```

Nếu có:

```text
Vietnamese
Chinese
Japanese
Emoji
```

thì khái niệm "width" không phải lúc nào cũng đơn giản là:

```python
len(text)
```

Đây là một vấn đề sâu hơn về:

```text
Unicode
display width
terminal width
```

Nhưng với `html2text`, điều bạn cần nhớ hôm nay là:

> Đừng tự xây wrapping Unicode trước khi thực sự cần.

---

# 23. `body_width = 0` không có nghĩa "không có newline"

Đây là lỗi hiểu nhầm phổ biến.

```python
converter.body_width = 0
```

**không có nghĩa**:

```text
HTML
 ↓
xóa tất cả newline
```

Nó chỉ có nghĩa:

```text
không ép body wrap theo width
```

Các semantic block vẫn có thể tạo newline:

```text
<h1>
<p>
<ul>
<li>
<blockquote>
<pre>
```

vẫn có cấu trúc Markdown tương ứng.

---

# 24. `body_width = 0` + `single_line_break`

Hai option này khác nhau.

```python
converter.body_width = 0
converter.single_line_break = True
```

nghĩa gần như:

```text
body_width
    ↓
không wrap theo column

single_line_break
    ↓
thay đổi cách xuống dòng giữa block
```

Đây là lý do roadmap tách:

```text
Buổi 7
body_width

Buổi 11
Whitespace & newline
```

---

# 25. Configuration baseline cho crawler

Với project crawler → Markdown, tôi khuyên bắt đầu từ:

```python
import html2text


converter = html2text.HTML2Text()

converter.body_width = 0

converter.ignore_links = False
converter.ignore_images = False
converter.ignore_emphasis = False

converter.inline_links = True

converter.skip_internal_links = True
```

Sau đó **không chỉnh thêm tùy tiện**.

Ta test output trước.

---

# 26. Tại sao baseline đơn giản tốt?

Bởi vì pipeline:

```text
HTML
 ↓
Cleaner
 ↓
html2text
 ↓
Normalizer
 ↓
Markdown
```

mỗi stage phải có trách nhiệm rõ ràng.

Nếu `html2text` vừa:

```text
convert
wrap
clean
remove
normalize
```

quá nhiều thì rất khó debug.

---

# 27. Một chiến lược rất tốt

Tôi khuyên bạn dùng:

```text
html2text
    ↓
semantic conversion
    ↓
Markdown
    ↓
Markdown normalizer
    ↓
final Markdown
```

Thay vì:

```text
html2text
    ↓
làm mọi thứ
```

Ví dụ:

```python
markdown = converter.handle(html)

markdown = normalize_markdown(markdown)
```

Trong `normalize_markdown()` mới xử lý những thứ như:

```text
trailing whitespace
excessive blank lines
```

và những rule **an toàn**.

---

# 28. Đừng normalize code block bằng regex đơn giản

Ví dụ bạn muốn:

```python
markdown = re.sub(r"\n{3,}", "\n\n", markdown)
```

Nghe có vẻ hợp lý.

Nhưng nếu code block chứa:

```python
text = "\n\n\n"
```

thì bạn có thể phá code.

Do đó:

```text
Markdown normalization
```

phải hiểu:

```text
normal text
vs
code fence
```

Đây là một bài toán parser.

---

# 29. Test matrix

Hôm nay bạn nên xây test matrix nhỏ:

| Case | `body_width` | Nội dung   |
| ---- | -----------: | ---------- |
| 1    |            0 | paragraph  |
| 2    |           40 | paragraph  |
| 3    |           80 | paragraph  |
| 4    |            0 | list       |
| 5    |           40 | list       |
| 6    |            0 | link       |
| 7    |           40 | long link  |
| 8    |           20 | code       |
| 9    |           40 | blockquote |
| 10   |           40 | table      |

Mục tiêu không phải nhớ output.

Mục tiêu là:

> **Quan sát option tác động lên từng loại block như thế nào.**

---

# 30. Tự viết helper để test

```python
import html2text


def convert(html: str, width: int) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = width

    return converter.handle(html)
```

Sau đó:

```python
html = """
<p>
Python is a powerful programming language
that is easy to learn.
</p>
"""

print("WIDTH 40")
print(convert(html, 40))

print("WIDTH 80")
print(convert(html, 80))

print("WIDTH 0")
print(convert(html, 0))
```

Đây là cách rất tốt để khám phá behavior của library.

---

# 31. Viết test bằng `pytest`

Ví dụ:

```python
def test_body_width_zero():
    html = """
    <p>
    Python is a programming language.
    </p>
    """

    result = convert(html, 0)

    assert "Python is a programming language." in result
```

Test không nên quá phụ thuộc vào whitespace cụ thể nếu behavior đó không phải requirement của bạn.

---

# 32. Test behavior thay vì implementation

Không nên:

```python
assert result == "Python is a programming language.\n"
```

nếu requirement chỉ là:

```text
paragraph content được giữ nguyên
```

Tốt hơn:

```python
assert "Python is a programming language." in result
```

Hoặc nếu formatting chính xác là requirement:

```python
assert result == expected
```

Khi đó expected phải được xem là **contract** của application.

---

# 33. Bài tập Buổi 7

## Bài 1

Tạo paragraph dài khoảng 200 ký tự.

Test:

```python
body_width = 20
body_width = 40
body_width = 80
body_width = 0
```

Quan sát.

---

## Bài 2

Tạo:

```html
<ul>
    <li>
        Đây là một list item rất dài...
    </li>
</ul>
```

Test:

```python
body_width = 30
```

với:

```python
wrap_list_items = True
```

và:

```python
wrap_list_items = False
```

So sánh.

---

## Bài 3

Tạo một URL rất dài:

```html
<a href="https://example.com/very/long/path/...">
    Article
</a>
```

Test:

```text
body_width = 40
wrap_links = True
wrap_links = False
protect_links = True
```

Quan sát sự khác nhau.

---

## Bài 4 — Code

Test:

```html
<pre><code>
def hello():
    if True:
        print("Hello World")
</code></pre>
```

với:

```text
body_width = 20
body_width = 40
body_width = 0
```

**Kiểm tra indentation.**

---

# 34. Bài tập quan trọng nhất

Hãy xây:

```python
class MarkdownConverter:
    def __init__(self):
        self.converter = html2text.HTML2Text()

        self.converter.body_width = 0

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

Sau đó tạo 5 fixture:

```text
fixtures/
│
├── paragraph.html
├── list.html
├── links.html
├── code.html
└── article.html
```

Mỗi fixture có expected Markdown.

Đây là bước chuyển từ:

```text
học library
```

sang:

```text
xây converter có test
```

---

# 35. Mental model Buổi 7

Hãy nhớ sơ đồ này:

```text
                    body_width
                        │
             ┌──────────┼──────────┐
             │          │          │
         paragraph     list       link
             │          │          │
             ▼          ▼          ▼
          wrapping   wrapping   wrapping
             │          │          │
             └──────────┼──────────┘
                        │
                        ▼
                     Markdown
```

Nhưng:

```text
<pre><code>
```

phải được đối xử đặc biệt:

```text
Code
 │
 └── preserve content
```

---

# 36. Quy tắc thực chiến

Nếu mục tiêu là:

```text
Web
 ↓
Crawler
 ↓
Markdown
 ↓
Database
```

thì baseline rất hợp lý để bắt đầu là:

```python
converter.body_width = 0
```

vì:

```text
Không ép presentation width
        ↓
Markdown ít bị formatter can thiệp
        ↓
Dễ normalize sau
        ↓
Dễ test
        ↓
Dễ render trên nhiều UI
```

Nhưng **không nên biến `body_width=0` thành quy tắc tuyệt đối**. Nếu mục tiêu của bạn là tạo Markdown để đọc trực tiếp trong terminal/email hoặc output cần giới hạn chiều rộng, `body_width` khác 0 lại có giá trị.

---

## Bài tập cuối buổi

Hãy chạy đúng đoạn này và **tự ghi lại output của 4 trường hợp**:

```python
import html2text

html = """
<h1>Python</h1>

<p>
Python is a powerful programming language that is easy to learn.
</p>

<ul>
    <li>Simple syntax</li>
    <li>Large ecosystem</li>
</ul>

<pre><code>
def hello():
    print("Hello World")
</code></pre>
"""

for width in (20, 40, 80, 0):
    converter = html2text.HTML2Text()
    converter.body_width = width

    print(f"\n===== WIDTH {width} =====")
    print(converter.handle(html))
```

Sau khi hiểu bài này, bạn sẽ có nền tảng để sang **Buổi 8 — Link Configuration**, nơi chúng ta sẽ đào rất sâu vào:

```text
<a>
 │
 ├── inline_links
 ├── reference links
 ├── ignore_links
 ├── protect_links
 ├── skip_internal_links
 ├── use_automatic_links
 ├── long URL
 └── relative URL
```

và đặc biệt là cách kết hợp `html2text` với **URL normalization trong crawler**, vì đây là chỗ `html2text` một mình không đủ để xử lý website thực tế.
