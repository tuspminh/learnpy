# Buổi 2 — `HTML2Text` Deep Dive

Hôm nay ta đi sâu vào **class `HTML2Text`**. Đây là phần quan trọng vì khi làm crawler thực tế, bạn gần như luôn cần **cấu hình converter** thay vì gọi đơn giản `html2text.html2text()`.

---

# 1. Ôn lại Buổi 1

Có hai cách chính:

### Cách 1 — nhanh

```python
import html2text

markdown = html2text.html2text(html)
```

### Cách 2 — dùng `HTML2Text`

```python
import html2text

converter = html2text.HTML2Text()

markdown = converter.handle(html)
```

Cách 2 cho phép:

```text
HTML2Text
   │
   ├── configuration
   ├── configuration
   ├── configuration
   │
   └── handle()
```

---

# 2. Tạo converter

Ví dụ:

```python
import html2text

converter = html2text.HTML2Text()

html = """
<h1>Python</h1>

<p>
    Python là <strong>ngôn ngữ lập trình</strong>.
</p>
"""

markdown = converter.handle(html)

print(markdown)
```

Ta có thể coi `converter` là một **object có state**.

```python
converter.ignore_links = True
converter.ignore_images = True
```

Sau đó:

```python
converter.handle(html)
```

sẽ sử dụng configuration hiện tại.

---

# 3. `body_width`

Đây là một option rất đáng chú ý.

```python
converter.body_width = 80
```

Nó quy định độ rộng khi format text.

Ví dụ:

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 40

html = """
<p>
Python là một ngôn ngữ lập trình mạnh,
dễ học và được sử dụng rất rộng rãi.
</p>
"""

print(converter.handle(html))
```

Output có thể được wrap thành nhiều dòng.

---

## Tắt wrapping

Nếu mục tiêu của bạn là crawler → Markdown, thường muốn giữ dòng văn bản dài hơn.

Có thể dùng:

```python
converter.body_width = 0
```

Ví dụ:

```python
converter = html2text.HTML2Text()
converter.body_width = 0
```

Đây là configuration rất đáng nhớ.

### Tư duy:

```text
body_width = 80
        ↓
wrap text

body_width = 0
        ↓
không giới hạn wrapping
```

Trong pipeline crawler, `0` thường hữu ích hơn nếu bạn muốn tự xử lý formatting ở bước sau.

---

# 4. `ignore_links`

Ví dụ:

```python
html = """
<p>
Xem
<a href="https://python.org">Python</a>
</p>
"""
```

Mặc định:

```python
converter = html2text.HTML2Text()

print(converter.handle(html))
```

sẽ tạo Markdown link:

```markdown
Xem [Python](https://python.org)
```

---

Nếu:

```python
converter.ignore_links = True
```

thì link sẽ không được giữ dưới dạng Markdown link.

Tư duy:

```text
<a href="...">Python</a>

       ↓

ignore_links = False
       ↓

[Python](...)

       ↓

ignore_links = True
       ↓

Python
```

---

# 5. Khi nào `ignore_links = True`?

Ví dụ bạn đang tạo:

> Markdown sạch để đọc offline.

Bạn không quan tâm link.

Khi đó:

```python
converter.ignore_links = True
```

có thể hợp lý.

Nhưng nếu bạn đang xây dựng:

> Web article archiver

thì thường nên:

```python
converter.ignore_links = False
```

vì link là dữ liệu.

---

# 6. `ignore_images`

HTML:

```html
<p>
    Python logo:
    <img src="python.png" alt="Python">
</p>
```

Mặc định có thể tạo Markdown image:

```markdown
![Python](python.png)
```

Nếu:

```python
converter.ignore_images = True
```

thì image sẽ bị bỏ qua.

---

## Khi crawl article

Có hai chiến lược.

### Giữ image

```python
converter.ignore_images = False
```

Phù hợp:

```text
Article
 ├── text
 ├── images
 └── links
```

### Bỏ image

```python
converter.ignore_images = True
```

Phù hợp:

```text
Article
 └── text only
```

---

# 7. `ignore_emphasis`

HTML:

```html
<p>
Python là <strong>rất mạnh</strong>.
</p>
```

Mặc định:

```markdown
Python là **rất mạnh**.
```

Nếu:

```python
converter.ignore_emphasis = True
```

thì formatting emphasis sẽ bị loại bỏ.

Có thể hình dung:

```text
<strong>
   ↓
**text**
```

hoặc:

```text
ignore_emphasis = True
   ↓
text
```

---

# 8. `skip_internal_links`

Đây là option rất hữu ích khi xử lý website.

Ví dụ:

```html
<a href="#chapter-1">Chapter 1</a>
```

Đây là **internal anchor**.

Nếu:

```python
converter.skip_internal_links = True
```

thì các link kiểu:

```text
#chapter-1
#comments
#top
```

có thể được bỏ qua.

---

## Vì sao hữu ích?

Một article có thể chứa rất nhiều:

```text
Table of Contents
 ↓
#chapter1
#chapter2
#chapter3
#comments
#footer
```

Khi convert sang Markdown, bạn có thể không muốn giữ tất cả những anchor này.

---

# 9. `protect_links`

Đây là option nâng cao hơn.

```python
converter.protect_links = True
```

Nó liên quan đến việc bảo vệ link trong quá trình xử lý Markdown.

Tại sao cần?

Bởi vì Markdown có cú pháp:

```markdown
[title](url)
```

Trong quá trình xử lý text, một số thao tác formatting có thể ảnh hưởng đến nội dung link.

Có thể hình dung:

```text
HTML
 ↓
parse
 ↓
text formatting
 ↓
link processing
 ↓
Markdown
```

`protect_links` giúp converter bảo vệ link khỏi một số thao tác xử lý text.

---

# 10. Một cấu hình thực tế

Giả sử ta đang xây dựng:

```text
Web Article
     ↓
HTML
     ↓
Markdown
```

Ta có thể bắt đầu:

```python
import html2text


converter = html2text.HTML2Text()

converter.body_width = 0

converter.ignore_links = False
converter.ignore_images = False
converter.ignore_emphasis = False

converter.skip_internal_links = True
```

Sau đó:

```python
markdown = converter.handle(html)
```

---

# 11. Đóng gói thành function

Thay vì viết configuration khắp project:

```python
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
markdown = html_to_markdown(html)
```

Đây là cách tốt hơn.

---

# 12. Tại sao tạo converter bên trong function?

Không nên vội làm:

```python
converter = html2text.HTML2Text()


def html_to_markdown(html):
    return converter.handle(html)
```

rồi dùng converter toàn application nếu bạn chưa kiểm soát được state.

Bởi vì:

```python
converter.ignore_links = True
```

là **state mutable**.

Ví dụ:

```python
converter.ignore_links = True

markdown1 = converter.handle(html1)

converter.ignore_links = False

markdown2 = converter.handle(html2)
```

Converter đã thay đổi state.

Trong application lớn, điều này có thể tạo ra bug khó phát hiện.

---

# 13. Tạo factory

Một pattern tốt hơn:

```python
import html2text


def create_converter() -> html2text.HTML2Text:
    converter = html2text.HTML2Text()

    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False
    converter.skip_internal_links = True

    return converter
```

Sau đó:

```python
converter = create_converter()

markdown = converter.handle(html)
```

Hoặc:

```python
def html_to_markdown(html: str) -> str:
    converter = create_converter()
    return converter.handle(html)
```

Kiến trúc này sẽ rất hữu ích khi chúng ta bước sang project.

---

# 14. Một ví dụ đầy đủ

```python
import html2text


def html_to_markdown(html: str) -> str:
    converter = html2text.HTML2Text()

    converter.body_width = 0

    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False

    converter.skip_internal_links = True

    return converter.handle(html)


html = """
<h1>Python</h1>

<p>
Python là <strong>ngôn ngữ lập trình</strong>.
</p>

<p>
Học <em>Python mỗi ngày</em>.
</p>

<p>
<a href="https://python.org">Python.org</a>
</p>

<img src="python.png" alt="Python">
"""

markdown = html_to_markdown(html)

print(markdown)
```

Pipeline:

```text
                  HTML
                   │
                   ▼
          ┌─────────────────┐
          │    HTML2Text    │
          │                 │
          │ body_width      │
          │ ignore_links    │
          │ ignore_images   │
          │ ignore_emphasis │
          │ skip_internal   │
          └────────┬────────┘
                   │
                   ▼
                Markdown
```

---

# 15. Điều quan trọng: `html2text` không phải HTML Cleaner

Đây là một sai lầm người mới rất dễ mắc.

Cho HTML:

```html
<body>

    <header>Website</header>

    <nav>
        Home
        Login
        Search
    </nav>

    <div class="ads">
        BUY NOW!!!
    </div>

    <article>
        <h1>Python</h1>
        <p>Hello Python</p>
    </article>

    <footer>
        Copyright
    </footer>

</body>
```

Nếu bạn:

```python
markdown = html2text.html2text(html)
```

thì **không có nghĩa `html2text` sẽ tự biết `article` là nội dung chính**.

Nó không phải:

```text
Article Extractor
```

Nó chủ yếu là:

```text
HTML → Markdown
```

---

# 16. Pipeline đúng cho crawler

Với project crawler của bạn, tôi khuyến nghị kiến trúc:

```text
                    HTTPX
                      │
                      ▼
                    HTML
                      │
                      ▼
               Selectolax / BS4
                      │
              ┌───────┴────────┐
              │                │
           Remove            Extract
            ads              article
              │                │
              └───────┬────────┘
                      ▼
                 Clean HTML
                      │
                      ▼
                  html2text
                      │
                      ▼
                   Markdown
```

Đây là điểm nối rất đẹp giữa những thư viện bạn đang học.

---

# 17. Một class thực tế hơn

Ta có thể bắt đầu thiết kế:

```python
import html2text


class MarkdownConverter:

    def __init__(self):
        self.converter = html2text.HTML2Text()

        self.converter.body_width = 0
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.skip_internal_links = True

    def convert(self, html: str) -> str:
        return self.converter.handle(html)
```

Sử dụng:

```python
converter = MarkdownConverter()

markdown = converter.convert(html)
```

Sau này class này có thể phát triển thành:

```text
MarkdownConverter
│
├── configure()
├── convert()
├── normalize()
└── clean_output()
```

---

# 18. Bài tập thực hành

## Bài 1 — Configuration

Cho:

```python
html = """
<h1>Python</h1>

<p>
Python là <strong>ngôn ngữ lập trình</strong>.
</p>

<p>
Học <em>Python</em>.
</p>

<a href="https://python.org">Python.org</a>

<img src="python.png" alt="Python">
"""
```

Tạo **4 converter**:

### Converter A

```text
Giữ tất cả
```

### Converter B

```text
ignore_links = True
```

### Converter C

```text
ignore_images = True
```

### Converter D

```text
ignore_emphasis = True
```

So sánh Markdown.

---

## Bài 2 — `body_width`

Thử:

```python
converter.body_width = 20
```

sau đó:

```python
converter.body_width = 40
```

và:

```python
converter.body_width = 0
```

Quan sát output.

---

# 19. Bài tập quan trọng nhất

Viết:

```python
class MarkdownConverter:
    ...
```

với API:

```python
converter = MarkdownConverter()

markdown = converter.convert(html)
```

Yêu cầu:

```text
body_width = 0
ignore_links = False
ignore_images = False
ignore_emphasis = False
skip_internal_links = True
```

**Không dùng BeautifulSoup hoặc Selectolax ở bài này.**

Mục tiêu là tập trung hiểu `html2text` trước.

---

# 20. Kiến thức cần nhớ

Nếu chỉ nhớ 6 thứ sau Buổi 2:

```python
converter = html2text.HTML2Text()

converter.body_width = 0

converter.ignore_links = False

converter.ignore_images = False

converter.ignore_emphasis = False

converter.skip_internal_links = True

markdown = converter.handle(html)
```

Và nhớ nguyên tắc:

> **`html2text` chuyển HTML → Markdown; nó không thay thế HTML parser/cleaner.**

Buổi 3 chúng ta sẽ đi sâu vào **Link & Image**: `<a>`, `<img>`, absolute/relative URL, reference link, inline link, xử lý link tương đối khi crawl website — phần này rất quan trọng nếu bạn muốn dùng `html2text` trong crawler thực tế.
