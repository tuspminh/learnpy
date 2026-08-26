# 📘 Selectolax — Buổi 4: Extract dữ liệu

Hôm nay chúng ta chuyển từ:

```text
"Biết tìm Node"
```

sang:

```text
"Tạo ra dữ liệu sạch để lưu vào database"
```

Đây là bước cực kỳ quan trọng nếu mục tiêu của bạn là xây **crawler truyện / article crawler**.

---

# 1. Extraction là gì?

Giả sử HTML:

```html
<article class="story">
    <h2 class="title">Đấu Phá Thương Khung</h2>

    <a class="author" href="/author/thien-tam">
        Thiên Tằm Thổ Đậu
    </a>

    <img class="cover" src="/images/dptk.jpg">

    <p class="description">
        Một câu chuyện tu luyện...
    </p>
</article>
```

Ta cần chuyển thành:

```python
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "author_url": "/author/thien-tam",
    "cover": "/images/dptk.jpg",
    "description": "Một câu chuyện tu luyện..."
}
```

Đây chính là **Extraction**.

---

# 2. Pipeline

Một parser thực tế thường có pipeline:

```text
HTML
 ↓
HTMLParser
 ↓
Find Node
 ↓
Extract
 ↓
Normalize
 ↓
Model
```

Ví dụ:

```text
<h2 class="title">
    Đấu Phá Thương Khung
</h2>

        ↓

"Đấu Phá Thương Khung"
```

---

# 3. Extract text

Cơ bản:

```python
from selectolax.parser import HTMLParser


html = """
<h1>Hello Python</h1>
"""

tree = HTMLParser(html)

node = tree.css_first("h1")

print(node.text())
```

Kết quả:

```text
Hello Python
```

---

# 4. Luôn nghĩ đến whitespace

Website thật thường không đẹp như ví dụ:

```html
<h1>

    Hello Python

</h1>
```

Nếu:

```python
text = node.text()
```

có thể nhận whitespace không mong muốn.

Do đó trong scraper:

```python
text = node.text().strip()
```

Đây nên trở thành **thói quen**.

---

# 5. Tạo `get_text()`

Thay vì lặp:

```python
node = ...
if node:
    text = node.text().strip()
```

hãy tạo helper:

```python
def get_text(node):
    if node is None:
        return None

    return node.text().strip()
```

Dùng:

```python
title = get_text(
    tree.css_first("h1")
)
```

Nếu không có `h1`:

```python
None
```

thay vì:

```text
AttributeError
```

---

# 6. Text mặc định vs text có fallback

Có trường hợp bạn muốn:

```python
"Unknown"
```

nếu Node không tồn tại.

Có thể:

```python
def get_text(node, default=None):
    if node is None:
        return default

    return node.text().strip()
```

Dùng:

```python
author = get_text(
    tree.css_first(".author"),
    default="Unknown",
)
```

---

# 7. Extract attribute

HTML:

```html
<a href="/chapter-1">
    Chapter 1
</a>
```

Lấy Node:

```python
link = tree.css_first("a")
```

Lấy URL:

```python
url = link.attributes.get("href")
```

Kết quả:

```text
/chapter-1
```

---

# 8. Tạo `get_attr()`

Ta tạo helper:

```python
def get_attr(node, name, default=None):
    if node is None:
        return default

    return node.attributes.get(name, default)
```

Dùng:

```python
url = get_attr(link, "href")
```

Hoặc:

```python
image_url = get_attr(image, "src")
```

---

# 9. Extract link

Đây là một pattern cực kỳ phổ biến:

```python
link = tree.css_first("a.chapter")

title = link.text().strip()
url = link.attributes.get("href")
```

Ta có:

```python
{
    "title": title,
    "url": url,
}
```

Ví dụ:

```python
{
    "title": "Chapter 1",
    "url": "/chapter-1",
}
```

---

# 10. Extract nhiều links

HTML:

```html
<div class="chapters">
    <a href="/chapter-1">Chapter 1</a>
    <a href="/chapter-2">Chapter 2</a>
    <a href="/chapter-3">Chapter 3</a>
</div>
```

Code:

```python
chapters = []

for node in tree.css(".chapters a"):
    chapters.append({
        "title": node.text().strip(),
        "url": node.attributes.get("href"),
    })
```

Kết quả:

```python
[
    {
        "title": "Chapter 1",
        "url": "/chapter-1",
    },
    {
        "title": "Chapter 2",
        "url": "/chapter-2",
    },
    {
        "title": "Chapter 3",
        "url": "/chapter-3",
    },
]
```

---

# 11. Extract image

HTML:

```html
<img
    class="cover"
    src="/images/python.jpg"
    alt="Python"
>
```

Code:

```python
image = tree.css_first("img.cover")

src = image.attributes.get("src")
alt = image.attributes.get("alt")
```

Kết quả:

```python
{
    "src": "/images/python.jpg",
    "alt": "Python",
}
```

---

# 12. `src` và `data-src`

Crawler thực tế thường gặp lazy loading:

```html
<img
    class="cover"
    data-src="/images/book.jpg"
>
```

Không có:

```html
src="..."
```

Do đó:

```python
src = (
    image.attributes.get("src")
    or image.attributes.get("data-src")
)
```

Đây là một ví dụ về **defensive extraction**.

---

# 13. Image helper

Ta có thể viết:

```python
def get_image_url(node):
    if node is None:
        return None

    return (
        node.attributes.get("src")
        or node.attributes.get("data-src")
    )
```

Sau này có thể mở rộng:

```python
def get_image_url(node):
    if node is None:
        return None

    return (
        node.attributes.get("src")
        or node.attributes.get("data-src")
        or node.attributes.get("data-original")
    )
```

Rất hữu ích với crawler.

---

# 14. Extract HTML

Đôi khi ta **không muốn text**.

Ví dụ nội dung chương truyện:

```html
<div class="content">
    <p>Chapter 1</p>
    <p>
        <strong>Python</strong>
        is powerful.
    </p>
</div>
```

Nếu:

```python
content.text()
```

ta mất HTML formatting.

Nếu:

```python
content.html
```

ta giữ:

```html
<p>Chapter 1</p>
<p>
    <strong>Python</strong>
    is powerful.
</p>
```

Điều này rất quan trọng khi xây **reading app**.

---

# 15. Text vs HTML

Hãy phân biệt rõ:

```text
node.text()
    ↓
nội dung thuần text
```

và:

```text
node.html
    ↓
HTML bên trong Node
```

Ví dụ:

```html
<div>
    Hello <strong>Python</strong>
</div>
```

Text:

```text
Hello Python
```

HTML:

```html
Hello <strong>Python</strong>
```

---

# 16. Extract paragraph

HTML:

```html
<div class="content">
    <p>Paragraph 1</p>
    <p>Paragraph 2</p>
    <p>Paragraph 3</p>
</div>
```

Code:

```python
paragraphs = [
    node.text().strip()
    for node in tree.css(".content p")
]
```

Kết quả:

```python
[
    "Paragraph 1",
    "Paragraph 2",
    "Paragraph 3",
]
```

---

# 17. Extract article content

Có thể:

```python
content = tree.css_first(".content")

paragraphs = [
    p.text().strip()
    for p in content.css("p")
]
```

Sau đó:

```python
text = "\n\n".join(paragraphs)
```

Kết quả:

```text
Paragraph 1

Paragraph 2

Paragraph 3
```

Đây là cách đơn giản để biến HTML article thành text.

---

# 18. Nhưng đừng vội xóa HTML

Nếu bạn đang xây app đọc truyện, tôi khuyên nên giữ **hai representation**:

```python
{
    "content_html": "...",
    "content_text": "...",
}
```

Ví dụ:

```python
{
    "content_html": "<p>Hello <strong>Python</strong></p>",
    "content_text": "Hello Python",
}
```

Tại sao?

Vì sau này UI có thể cần:

```text
HTML
 ↓
QTextBrowser / WebEngine
```

trong khi search có thể cần:

```text
TEXT
 ↓
FTS / search
```

---

# 19. Extract metadata

HTML:

```html
<div class="story">
    <h1 class="title">Python Mastery</h1>

    <div class="metadata">
        <span class="author">Alice</span>
        <span class="category">Programming</span>
        <span class="status">Completed</span>
    </div>
</div>
```

Parser:

```python
story = tree.css_first(".story")

title = get_text(
    story.css_first(".title")
)

author = get_text(
    story.css_first(".author")
)

category = get_text(
    story.css_first(".category")
)

status = get_text(
    story.css_first(".status")
)
```

Kết quả:

```python
{
    "title": "Python Mastery",
    "author": "Alice",
    "category": "Programming",
    "status": "Completed",
}
```

---

# 20. Một lỗi kiến trúc thường gặp

Không nên viết tất cả vào một function khổng lồ:

```python
def parse(html):
    ...
    ...
    ...
    ...
    ...
    ...
    ...
```

Tốt hơn:

```text
Parser
 │
 ├── extract_title()
 ├── extract_author()
 ├── extract_cover()
 ├── extract_description()
 └── extract_chapters()
```

Ví dụ:

```python
class StoryParser:

    def extract_title(self, node):
        ...

    def extract_author(self, node):
        ...

    def extract_cover(self, node):
        ...

    def extract_chapters(self, node):
        ...
```

Chúng ta sẽ tiến dần đến kiến trúc này.

---

# 21. Xây `BaseExtractor`

Bây giờ hãy nâng cấp helper.

```python
class BaseExtractor:

    @staticmethod
    def text(node, default=None):
        if node is None:
            return default

        return node.text().strip()

    @staticmethod
    def attr(node, name, default=None):
        if node is None:
            return default

        return node.attributes.get(name, default)

    @staticmethod
    def html(node, default=None):
        if node is None:
            return default

        return node.html
```

Dùng:

```python
extractor = BaseExtractor()

title = extractor.text(
    story.css_first("h1")
)

url = extractor.attr(
    story.css_first("a"),
    "href"
)
```

---

# 22. Có thể dùng static method trực tiếp

Không cần tạo object:

```python
title = BaseExtractor.text(
    story.css_first("h1")
)

url = BaseExtractor.attr(
    story.css_first("a"),
    "href"
)
```

---

# 23. Xây `StoryParser`

Bây giờ:

```python
class StoryParser:

    def parse(self, html: str) -> dict:
        tree = HTMLParser(html)

        story = tree.css_first(".story")

        return {
            "title": BaseExtractor.text(
                story.css_first(".title")
            ),
            "author": BaseExtractor.text(
                story.css_first(".author")
            ),
            "cover": BaseExtractor.attr(
                story.css_first("img.cover"),
                "src",
            ),
        }
```

Đây đã khá gần với parser thực tế.

---

# 24. Một parser tốt nên chịu được HTML thiếu dữ liệu

Ví dụ website:

```html
<div class="story">
    <h1 class="title">Python</h1>
</div>
```

Không có:

```text
author
cover
```

Code:

```python
return {
    "title": BaseExtractor.text(
        story.css_first(".title")
    ),
    "author": BaseExtractor.text(
        story.css_first(".author")
    ),
    "cover": BaseExtractor.attr(
        story.css_first("img.cover"),
        "src",
    ),
}
```

Kết quả:

```python
{
    "title": "Python",
    "author": None,
    "cover": None,
}
```

Parser không crash.

Đây là nguyên tắc rất quan trọng:

> **Crawler phải chịu được dữ liệu không hoàn hảo.**

---

# 25. Normalize text

Website có thể chứa:

```text
"  Python   Programming  "
```

Ta muốn:

```text
"Python Programming"
```

Có thể:

```python
def normalize_text(text):
    if text is None:
        return None

    return " ".join(text.split())
```

Ví dụ:

```python
text = "  Python   Programming  "

print(normalize_text(text))
```

Kết quả:

```text
Python Programming
```

---

# 26. Normalize text tốt hơn

Ta có thể đưa vào `BaseExtractor`:

```python
class BaseExtractor:

    @staticmethod
    def text(node, default=None):
        if node is None:
            return default

        return " ".join(node.text().split())
```

Bây giờ:

```python
title = BaseExtractor.text(
    story.css_first(".title")
)
```

sẽ tự động:

```text
trim
+
normalize whitespace
```

---

# 27. Extract nhiều item

Đây là pattern quan trọng:

```python
def extract_chapters(story):
    chapters = []

    for node in story.css(".chapters a"):
        chapters.append({
            "title": BaseExtractor.text(node),
            "url": BaseExtractor.attr(node, "href"),
        })

    return chapters
```

Hoặc list comprehension:

```python
def extract_chapters(story):
    return [
        {
            "title": BaseExtractor.text(node),
            "url": BaseExtractor.attr(node, "href"),
        }
        for node in story.css(".chapters a")
    ]
```

---

# 28. Full example

HTML:

```python
html = """
<article class="story">

    <h1 class="title">
        Python Mastery
    </h1>

    <a class="author" href="/authors/alice">
        Alice
    </a>

    <img
        class="cover"
        src="/images/python.jpg"
        alt="Python"
    >

    <div class="chapters">
        <a href="/chapter/1">Chapter 1</a>
        <a href="/chapter/2">Chapter 2</a>
        <a href="/chapter/3">Chapter 3</a>
    </div>

</article>
"""
```

Parser:

```python
from selectolax.parser import HTMLParser


class BaseExtractor:

    @staticmethod
    def text(node, default=None):
        if node is None:
            return default

        return " ".join(node.text().split())

    @staticmethod
    def attr(node, name, default=None):
        if node is None:
            return default

        return node.attributes.get(name, default)


class StoryParser:

    def parse(self, html: str) -> dict:
        tree = HTMLParser(html)

        story = tree.css_first(".story")

        author = story.css_first(".author")
        cover = story.css_first(".cover")

        chapters = [
            {
                "title": BaseExtractor.text(chapter),
                "url": BaseExtractor.attr(chapter, "href"),
            }
            for chapter in story.css(".chapters a")
        ]

        return {
            "title": BaseExtractor.text(
                story.css_first(".title")
            ),
            "author": BaseExtractor.text(author),
            "author_url": BaseExtractor.attr(
                author,
                "href",
            ),
            "cover": BaseExtractor.attr(
                cover,
                "src",
            ),
            "chapters": chapters,
        }
```

Kết quả:

```python
{
    "title": "Python Mastery",
    "author": "Alice",
    "author_url": "/authors/alice",
    "cover": "/images/python.jpg",
    "chapters": [
        {
            "title": "Chapter 1",
            "url": "/chapter/1",
        },
        {
            "title": "Chapter 2",
            "url": "/chapter/2",
        },
        {
            "title": "Chapter 3",
            "url": "/chapter/3",
        },
    ],
}
```

---

# 29. Một nguyên tắc quan trọng: Parser không nên gọi HTTP

Không nên:

```python
class StoryParser:

    def parse(self, url):
        response = httpx.get(url)
        ...
```

Vì Parser nên chỉ quan tâm:

```text
HTML → Data
```

Còn HTTP:

```text
URL → HTML
```

Nên tách:

```text
Fetcher
   ↓
HTML
   ↓
Parser
   ↓
Data
```

Sau này khi học **Selectolax + HTTPX**, chúng ta sẽ xây:

```text
HTTPX
  ↓
Fetcher
  ↓
Selectolax
  ↓
Parser
  ↓
Model
```

Đây cũng phù hợp với hướng **Clean Architecture / Repository / crawler framework** mà bạn đang học.

---

# 30. Bài tập Buổi 4

Cho HTML:

```html
<article class="story">

    <h1 class="title">
        Đấu Phá Thương Khung
    </h1>

    <a
        class="author"
        href="/author/thien-tam"
    >
        Thiên Tằm Thổ Đậu
    </a>

    <img
        class="cover"
        src="/images/dptk.jpg"
        alt="Đấu Phá Thương Khung"
    >

    <div class="description">
        Một câu chuyện tu luyện hấp dẫn.
    </div>

    <div class="chapters">

        <a href="/chapter/1">
            Chương 1
        </a>

        <a href="/chapter/2">
            Chương 2
        </a>

        <a href="/chapter/3">
            Chương 3
        </a>

    </div>

</article>
```

## Bài 1

Viết:

```python
get_text(node)
```

Có xử lý:

```text
None
whitespace
```

---

## Bài 2

Viết:

```python
get_attr(node, name)
```

Có xử lý Node không tồn tại.

---

## Bài 3

Viết:

```python
extract_story(html)
```

Trả về:

```python
{
    "title": "...",
    "author": "...",
    "author_url": "...",
    "cover": "...",
    "description": "...",
    "chapters": [
        {
            "title": "...",
            "url": "..."
        }
    ]
}
```

---

## Bài 4 — Defensive parsing

Thử xóa:

```html
<a class="author">
```

hoặc:

```html
<img class="cover">
```

Parser **không được crash**.

Kết quả chấp nhận:

```python
{
    "author": None,
    "cover": None,
}
```

---

## Bài 5 — Tách architecture

Tạo:

```text
project/
│
├── extractor.py
└── story_parser.py
```

### `extractor.py`

```python
class BaseExtractor:
    ...
```

### `story_parser.py`

```python
class StoryParser:
    ...
```

Mục tiêu của bài này là bắt đầu hình thành:

```text
Extractor
    ↓
Parser
    ↓
Structured Data
```

---

# 🎯 Tổng kết 4 buổi đầu

Bạn đã đi qua toàn bộ vòng cơ bản:

```text
                    Selectolax
                        │
                        ▼
                    HTMLParser
                        │
                        ▼
                       DOM
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
        CSS Selector          Traversal
              │                   │
              └─────────┬─────────┘
                        ▼
                       Node
                        │
                        ▼
                    Extraction
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
             text      attr      html
                        │
                        ▼
                  Structured Data
```

Từ **Buổi 5**, chúng ta sẽ bắt đầu bước vào **scraping thực tế**: xử lý danh sách, card, table, article, pagination và đặc biệt là cách viết parser không bị phụ thuộc quá chặt vào một cấu trúc HTML duy nhất.
