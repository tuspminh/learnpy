# 📘 Selectolax — Buổi 5: Parse danh sách, Card, Table, Article & Pagination

Từ Buổi 1 → 4, bạn đã học:

```text
HTML
 ↓
HTMLParser
 ↓
CSS Selector
 ↓
Node
 ↓
Extract
 ↓
Structured Data
```

Hôm nay chúng ta bắt đầu viết **parser giống crawler thực tế**.

Mục tiêu của buổi này:

* Parse danh sách
* Parse card
* Parse table
* Parse article
* Parse pagination
* Hiểu pattern `collection → item → fields`
* Tránh ghép nhầm dữ liệu giữa các item

---

# 1. Pattern quan trọng nhất: Collection → Item → Field

Hầu hết website đều có cấu trúc:

```text
Container
│
├── Item
│   ├── Field
│   ├── Field
│   └── Field
│
├── Item
│   ├── Field
│   ├── Field
│   └── Field
│
└── Item
    ├── Field
    ├── Field
    └── Field
```

Ví dụ website truyện:

```html
<div class="stories">
    <article class="story">
        ...
    </article>

    <article class="story">
        ...
    </article>
</div>
```

Ta nên làm:

```python
stories = tree.css(".stories article.story")

for story in stories:
    ...
```

Đây là pattern quan trọng nhất của scraping.

---

# 2. Parse danh sách đơn giản

HTML:

```html
<ul class="books">
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
```

Code:

```python
from selectolax.parser import HTMLParser


html = """
<ul class="books">
    <li>Python</li>
    <li>Rust</li>
    <li>Go</li>
</ul>
"""

tree = HTMLParser(html)

books = [
    node.text().strip()
    for node in tree.css(".books li")
]

print(books)
```

Kết quả:

```python
[
    "Python",
    "Rust",
    "Go",
]
```

---

# 3. Parse list có link

HTML:

```html
<ul class="books">
    <li>
        <a href="/python">Python</a>
    </li>

    <li>
        <a href="/rust">Rust</a>
    </li>

    <li>
        <a href="/go">Go</a>
    </li>
</ul>
```

Code:

```python
books = []

for node in tree.css(".books li"):
    link = node.css_first("a")

    books.append({
        "title": link.text().strip(),
        "url": link.attributes.get("href"),
    })
```

Kết quả:

```python
[
    {
        "title": "Python",
        "url": "/python",
    },
    {
        "title": "Rust",
        "url": "/rust",
    },
    {
        "title": "Go",
        "url": "/go",
    },
]
```

Điểm quan trọng:

```python
for node in tree.css(".books li"):
```

`node` chính là **scope của một item**.

---

# 4. Tại sao không lấy riêng tất cả title và URL?

Không nên:

```python
titles = tree.css(".books li a")
urls = tree.css(".books li a")
```

rồi ghép bằng `zip()`.

Với HTML đơn giản có thể chạy, nhưng khi HTML phức tạp:

```text
item 1
item 2 thiếu URL
item 3 có URL
```

rất dễ xảy ra:

```text
Title 1 → URL 1
Title 2 → URL 3
```

Cách an toàn:

```python
for item in items:
    title = ...
    url = ...
```

Giữ **context của item**.

---

# 5. Parse Card

Card là cấu trúc cực kỳ phổ biến.

Ví dụ:

```html
<div class="products">

    <div class="card">
        <h2 class="title">Python</h2>
        <p class="price">100</p>
        <a href="/python">View</a>
    </div>

    <div class="card">
        <h2 class="title">Rust</h2>
        <p class="price">200</p>
        <a href="/rust">View</a>
    </div>

</div>
```

Parser:

```python
cards = []

for card in tree.css(".card"):
    title = card.css_first(".title")
    price = card.css_first(".price")
    link = card.css_first("a")

    cards.append({
        "title": title.text().strip() if title else None,
        "price": price.text().strip() if price else None,
        "url": link.attributes.get("href") if link else None,
    })
```

---

# 6. Tốt hơn: dùng helper

Từ Buổi 4:

```python
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
```

Parser:

```python
cards = []

for card in tree.css(".card"):
    cards.append({
        "title": BaseExtractor.text(
            card.css_first(".title")
        ),
        "price": BaseExtractor.text(
            card.css_first(".price")
        ),
        "url": BaseExtractor.attr(
            card.css_first("a"),
            "href",
        ),
    })
```

Code sạch hơn rất nhiều.

---

# 7. Parse Story Card

Đây là ví dụ sát với crawler truyện.

```html
<div class="stories">

    <article class="story">
        <h2 class="title">Đấu Phá Thương Khung</h2>

        <a class="author" href="/author/thien-tam">
            Thiên Tằm Thổ Đậu
        </a>

        <img
            class="cover"
            src="/images/dptk.jpg"
        >

        <a class="detail" href="/story/dptk">
            Chi tiết
        </a>
    </article>

    <article class="story">
        <h2 class="title">Phàm Nhân Tu Tiên</h2>

        <a class="author" href="/author/wang-yu">
            Vong Ngữ
        </a>

        <img
            class="cover"
            src="/images/phnt.jpg"
        >

        <a class="detail" href="/story/phnt">
            Chi tiết
        </a>
    </article>

</div>
```

Parser:

```python
stories = []

for story in tree.css(".stories .story"):

    title = BaseExtractor.text(
        story.css_first(".title")
    )

    author_node = story.css_first(".author")
    cover_node = story.css_first(".cover")
    detail_node = story.css_first(".detail")

    stories.append({
        "title": title,
        "author": BaseExtractor.text(author_node),
        "author_url": BaseExtractor.attr(
            author_node,
            "href",
        ),
        "cover": BaseExtractor.attr(
            cover_node,
            "src",
        ),
        "url": BaseExtractor.attr(
            detail_node,
            "href",
        ),
    })
```

---

# 8. Parse Table

Table cũng xuất hiện rất nhiều trên website.

HTML:

```html
<table class="stories">
    <thead>
        <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Status</th>
        </tr>
    </thead>

    <tbody>
        <tr>
            <td>Python</td>
            <td>Alice</td>
            <td>Completed</td>
        </tr>

        <tr>
            <td>Rust</td>
            <td>Bob</td>
            <td>Ongoing</td>
        </tr>
    </tbody>
</table>
```

Ta có:

```python
rows = tree.css(".stories tbody tr")

for row in rows:
    cells = row.css("td")

    print([
        cell.text().strip()
        for cell in cells
    ])
```

Kết quả:

```text
["Python", "Alice", "Completed"]
["Rust", "Bob", "Ongoing"]
```

---

# 9. Parse Table thành dictionary

Ta muốn:

```python
{
    "title": "Python",
    "author": "Alice",
    "status": "Completed",
}
```

Code:

```python
stories = []

for row in tree.css(".stories tbody tr"):
    cells = row.css("td")

    if len(cells) < 3:
        continue

    stories.append({
        "title": cells[0].text().strip(),
        "author": cells[1].text().strip(),
        "status": cells[2].text().strip(),
    })
```

---

# 10. Vấn đề: Table không phải lúc nào cũng ổn định

Ví dụ:

```html
<tr>
    <td>Python</td>
    <td>Alice</td>
</tr>
```

Thiếu `status`.

Nếu viết:

```python
status = cells[2]
```

sẽ lỗi.

Do đó:

```python
status = (
    cells[2].text().strip()
    if len(cells) > 2
    else None
)
```

Đây là **defensive parsing**.

---

# 11. Parse Article

Article thường phức tạp hơn card.

Ví dụ:

```html
<article class="article">

    <h1 class="title">
        Python 3.15 có gì mới?
    </h1>

    <div class="meta">
        <span class="author">Alice</span>
        <time datetime="2026-08-27">
            27/08/2026
        </time>
    </div>

    <div class="content">
        <p>Python...</p>
        <p>...</p>
    </div>

</article>
```

Ta chia thành:

```text
Article
├── title
├── metadata
│   ├── author
│   └── published_at
└── content
```

Parser:

```python
article = tree.css_first(".article")

title = BaseExtractor.text(
    article.css_first(".title")
)

author = BaseExtractor.text(
    article.css_first(".author")
)

time_node = article.css_first("time")

published_at = BaseExtractor.attr(
    time_node,
    "datetime",
)

content = article.css_first(".content")
```

---

# 12. Extract article content

Nếu muốn giữ HTML:

```python
content_html = content.html
```

Nếu muốn text:

```python
content_text = content.text().strip()
```

Nếu muốn paragraph:

```python
paragraphs = [
    BaseExtractor.text(p)
    for p in content.css("p")
]
```

---

# 13. Một Article Parser hoàn chỉnh

```python
class ArticleParser:

    def parse(self, html: str) -> dict:
        tree = HTMLParser(html)

        article = tree.css_first("article.article")

        if article is None:
            return {}

        content = article.css_first(".content")

        return {
            "title": BaseExtractor.text(
                article.css_first(".title")
            ),
            "author": BaseExtractor.text(
                article.css_first(".author")
            ),
            "published_at": BaseExtractor.attr(
                article.css_first("time"),
                "datetime",
            ),
            "content_html": (
                content.html
                if content
                else None
            ),
            "content_text": (
                content.text().strip()
                if content
                else None
            ),
        }
```

Đây đã là một parser khá thực tế.

---

# 14. Parse Pagination

Đây là phần **rất quan trọng đối với crawler**.

Giả sử:

```html
<div class="pagination">

    <a href="/stories?page=1">
        1
    </a>

    <a href="/stories?page=2">
        2
    </a>

    <a href="/stories?page=3">
        3
    </a>

    <a class="next" href="/stories?page=2">
        Next
    </a>

</div>
```

Ta có:

```python
next_node = tree.css_first(
    ".pagination a.next"
)

next_url = BaseExtractor.attr(
    next_node,
    "href",
)
```

---

# 15. Pagination kiểu "Next"

Đây là pattern crawler phổ biến:

```python
while url:

    html = fetch(url)

    data = parser.parse(html)

    save(data)

    url = parser.next_page(html)
```

Sơ đồ:

```text
Page 1
  ↓
Page 2
  ↓
Page 3
  ↓
Page 4
  ↓
None
```

---

# 16. Viết `next_page()`

```python
class StoryListParser:

    def next_page(self, html: str) -> str | None:
        tree = HTMLParser(html)

        node = tree.css_first(
            ".pagination a.next"
        )

        return BaseExtractor.attr(
            node,
            "href",
        )
```

Nếu không còn trang:

```python
None
```

---

# 17. Pagination có disabled

Một số website:

```html
<a
    class="next disabled"
    href="#"
>
    Next
</a>
```

Không nên lấy:

```text
#
```

Có thể:

```python
node = tree.css_first(
    ".pagination a.next"
)

if node is None:
    return None

href = node.attributes.get("href")

if not href or href == "#":
    return None

return href
```

---

# 18. Pagination bằng số

Ví dụ:

```html
<div class="pagination">
    <a href="/page/1">1</a>
    <a href="/page/2">2</a>
    <a href="/page/3">3</a>
</div>
```

Lấy:

```python
pages = [
    BaseExtractor.attr(
        node,
        "href",
    )
    for node in tree.css(".pagination a")
]
```

Kết quả:

```python
[
    "/page/1",
    "/page/2",
    "/page/3",
]
```

---

# 19. Nhưng crawler thường không cần lấy toàn bộ page URL

Nếu có:

```text
1 2 3 4 5 6 7 8 9 10
```

và bạn đang ở page 3, có thể chỉ cần:

```text
Next
```

Vì:

```text
current page
     ↓
next page
     ↓
next page
     ↓
...
```

Cách này đơn giản và thường phù hợp với crawler tuần tự.

---

# 20. Xây `StoryListParser`

Ta có thể thiết kế:

```python
class StoryListParser:

    def parse(self, html: str) -> list[dict]:
        tree = HTMLParser(html)

        stories = []

        for node in tree.css("article.story"):
            link = node.css_first("a.title")

            stories.append({
                "title": BaseExtractor.text(link),
                "url": BaseExtractor.attr(
                    link,
                    "href",
                ),
            })

        return stories

    def next_page(self, html: str) -> str | None:
        tree = HTMLParser(html)

        node = tree.css_first(
            ".pagination a.next"
        )

        href = BaseExtractor.attr(
            node,
            "href",
        )

        if not href or href == "#":
            return None

        return href
```

Đây là một thiết kế rất đáng nhớ:

```text
StoryListParser
│
├── parse()
│     ↓
│   stories
│
└── next_page()
      ↓
    next URL
```

---

# 21. Một lỗi rất lớn khi viết parser

Đừng để parser biết quá nhiều về crawler.

Không nên:

```python
class StoryParser:

    def parse(self, url):
        response = httpx.get(url)

        ...

        for page in ...:
            httpx.get(...)

        sqlite3.connect(...)
```

Parser chỉ nên:

```text
HTML
 ↓
Data
```

Còn:

```text
HTTP
 ↓
Fetcher

Data
 ↓
Repository
```

Sẽ thuộc layer khác.

---

# 22. Architecture bắt đầu hình thành

Đây là architecture chúng ta sẽ hướng tới:

```text
                 ┌──────────────┐
                 │    HTTPX     │
                 │   Fetcher    │
                 └──────┬───────┘
                        │
                       HTML
                        │
                        ▼
                 ┌──────────────┐
                 │  Selectolax  │
                 │    Parser    │
                 └──────┬───────┘
                        │
                  Structured Data
                        │
                        ▼
                 ┌──────────────┐
                 │    Model     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Repository   │
                 └──────────────┘
```

Đây chính là nền tảng để sau này chúng ta xây crawler framework.

---

# 23. Mini Project: Story Listing Parser

Hãy xây parser cho HTML:

```html
<div class="story-list">

    <article class="story">
        <a
            class="title"
            href="/story/python"
        >
            Python Mastery
        </a>

        <span class="author">
            Alice
        </span>

        <span class="status">
            Completed
        </span>
    </article>

    <article class="story">
        <a
            class="title"
            href="/story/rust"
        >
            Rust Mastery
        </a>

        <span class="author">
            Bob
        </span>

        <span class="status">
            Ongoing
        </span>
    </article>

</div>

<div class="pagination">
    <a class="next" href="/stories?page=2">
        Next
    </a>
</div>
```

Mục tiêu:

```python
parser = StoryListParser()

stories = parser.parse(html)
next_url = parser.next_page(html)
```

`stories`:

```python
[
    {
        "title": "Python Mastery",
        "url": "/story/python",
        "author": "Alice",
        "status": "Completed",
    },
    {
        "title": "Rust Mastery",
        "url": "/story/rust",
        "author": "Bob",
        "status": "Ongoing",
    },
]
```

`next_url`:

```text
/stories?page=2
```

---

# 🧪 Bài tập Buổi 5

## Bài 1 — List

Parse:

```html
<ul class="categories">
    <li><a href="/python">Python</a></li>
    <li><a href="/rust">Rust</a></li>
    <li><a href="/go">Go</a></li>
</ul>
```

Kết quả:

```python
[
    {"name": "Python", "url": "/python"},
    {"name": "Rust", "url": "/rust"},
    {"name": "Go", "url": "/go"},
]
```

---

## Bài 2 — Card

Parse 3 story card, mỗi card có:

```text
title
author
cover
url
```

---

## Bài 3 — Table

Parse:

```text
title
author
status
```

thành:

```python
list[dict]
```

---

## Bài 4 — Article

Extract:

```text
title
author
published_at
content_html
content_text
```

---

## Bài 5 — Pagination

Viết:

```python
next_page(html) -> str | None
```

Phải xử lý:

```text
không có next
href="#"
class="disabled"
```

---

# 🎯 Điều cần nhớ sau Buổi 5

Có 5 pattern bạn nên thuộc lòng:

### 1. Collection

```python
items = tree.css(".items .item")
```

### 2. Item scope

```python
for item in items:
    ...
```

### 3. Extract field

```python
title = BaseExtractor.text(
    item.css_first(".title")
)
```

### 4. Extract URL

```python
url = BaseExtractor.attr(
    item.css_first("a"),
    "href",
)
```

### 5. Pagination

```python
next_url = parser.next_page(html)

while next_url:
    ...
```

Từ đây Selectolax đã đủ để bạn viết các parser scraping cơ bản. **Buổi 6** chúng ta sẽ đi vào một kỹ năng cực kỳ quan trọng với crawler truyện/article: **làm sạch HTML — loại `script`, `style`, quảng cáo, navigation, comment và chỉ giữ lại phần nội dung cần thiết**.
