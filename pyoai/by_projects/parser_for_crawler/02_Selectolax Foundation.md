# Buổi 2 — Selectolax Foundation

Hôm nay chúng ta chưa xây `ListingParser` hoàn chỉnh. Mục tiêu là **nắm chắc Selectolax và tạo một lớp adapter nhỏ**, để các parser phía trên không phụ thuộc trực tiếp quá nhiều vào API của Selectolax.

Kiến trúc:

```text
page_source: str
       │
       ▼
SelectolaxDocument
       │
       ▼
      DOM
       │
       ▼
    Parser
```

---

## 1. Cài Selectolax

```bash
pip install selectolax
```

Kiểm tra:

```python
from selectolax.parser import HTMLParser

html = """
<html>
    <body>
        <h1>Hello</h1>
    </body>
</html>
"""

tree = HTMLParser(html)

print(tree.css_first("h1").text())
```

Kết quả:

```text
Hello
```

---

# 2. `HTMLParser` là gì?

Selectolax nhận HTML:

```python
html = """
<div class="book">
    <h2>Truyện A</h2>
</div>
"""
```

Sau đó:

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html)
```

`tree` đại diện cho toàn bộ DOM.

Ta có thể tìm node:

```python
node = tree.css_first(".book")
```

hoặc:

```python
title = tree.css_first("h2")
```

---

# 3. CSS Selector

Đây là phần **quan trọng nhất đối với crawler parser**.

HTML:

```html
<div class="book">
    <h2 class="title">Truyện A</h2>
    <span class="author">Nguyễn Văn A</span>
</div>
```

### Tag

```python
tree.css_first("h2")
```

### Class

```python
tree.css_first(".title")
```

### ID

```python
tree.css_first("#book-1")
```

### Descendant

```python
tree.css_first(".book .title")
```

### Attribute

```python
tree.css_first("a[href]")
```

### Attribute cụ thể

```python
tree.css_first('a[href="/truyen-a"]')
```

---

# 4. `css_first()`

Khi chỉ cần **một node**:

```python
node = tree.css_first(".title")
```

Ví dụ:

```python
html = """
<div class="book">
    <h2 class="title">Truyện A</h2>
</div>
"""

tree = HTMLParser(html)

node = tree.css_first(".title")

print(node)
```

---

# 5. `css()`

Khi cần nhiều node:

```python
nodes = tree.css(".book")
```

Ví dụ:

```python
html = """
<div class="book">
    <h2>Truyện A</h2>
</div>

<div class="book">
    <h2>Truyện B</h2>
</div>

<div class="book">
    <h2>Truyện C</h2>
</div>
"""

tree = HTMLParser(html)

books = tree.css(".book")

for book in books:
    print(book.text())
```

Kết quả:

```text
Truyện A
Truyện B
Truyện C
```

---

# 6. Lấy text

Node:

```python
node = tree.css_first("h2")
```

Lấy text:

```python
node.text()
```

Ví dụ:

```python
html = """
<h2>
    Truyện A
</h2>
"""

tree = HTMLParser(html)

node = tree.css_first("h2")

print(node.text())
```

Kết quả:

```text
Truyện A
```

---

# 7. Text có khoảng trắng

Crawler thực tế thường gặp:

```html
<h2>
    Truyện A

    <span>Full</span>
</h2>
```

Không nên phụ thuộc vào text thô.

Ta thường chuẩn hóa:

```python
text = node.text().strip()
```

Nhưng với content chapter, sau này chúng ta sẽ cần một hàm normalize riêng.

---

# 8. Lấy attribute

Đây là thao tác cực kỳ quan trọng vì URL nằm trong `href`.

HTML:

```html
<a href="/truyen-a">
    Truyện A
</a>
```

Code:

```python
node = tree.css_first("a")

url = node.attributes.get("href")

print(url)
```

Kết quả:

```text
/truyen-a
```

Tương tự:

```html
<img src="/images/book.jpg">
```

```python
src = tree.css_first("img").attributes.get("src")
```

---

# 9. Không được giả định node luôn tồn tại

Sai:

```python
title = tree.css_first(".title").text()
```

Nếu `.title` không tồn tại:

```python
tree.css_first(".title")
```

có thể trả về:

```python
None
```

và:

```python
None.text()
```

sẽ lỗi.

Ta cần:

```python
node = tree.css_first(".title")

if node is not None:
    title = node.text().strip()
else:
    title = None
```

---

# 10. Viết helper `text()`

Parser sẽ có rất nhiều đoạn kiểu này:

```python
node = tree.css_first(".title")

if node:
    title = node.text().strip()
else:
    title = None
```

Lặp lại rất nhiều.

Ta tạo helper:

```python
def get_text(node) -> str | None:
    if node is None:
        return None

    text = node.text().strip()

    if not text:
        return None

    return text
```

Sử dụng:

```python
title_node = tree.css_first(".title")

title = get_text(title_node)
```

---

# 11. Helper lấy attribute

```python
def get_attribute(node, name: str) -> str | None:
    if node is None:
        return None

    value = node.attributes.get(name)

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return value
```

Dùng:

```python
link = tree.css_first("a")

url = get_attribute(link, "href")
```

---

# 12. Tạo `SelectolaxDocument`

Bây giờ bắt đầu áp dụng SOLID.

Tạo:

```text
infrastructure/
└── parser/
    └── selectolax_document.py
```

Code:

```python
from selectolax.parser import HTMLParser


class SelectolaxDocument:
    def __init__(self, page_source: str):
        self._tree = HTMLParser(page_source)

    def first(self, selector: str):
        return self._tree.css_first(selector)

    def all(self, selector: str):
        return self._tree.css(selector)
```

Bây giờ parser không cần:

```python
HTMLParser(...)
```

trực tiếp.

Nó có thể dùng:

```python
document.first(".title")
```

hoặc:

```python
document.all(".book")
```

---

# 13. Thêm `get_text()`

Ta có thể encapsulate tiếp:

```python
from selectolax.parser import HTMLParser


class SelectolaxDocument:

    def __init__(self, page_source: str):
        self._tree = HTMLParser(page_source)

    def first(self, selector: str):
        return self._tree.css_first(selector)

    def all(self, selector: str):
        return self._tree.css(selector)

    def text(self, selector: str) -> str | None:
        node = self.first(selector)

        if node is None:
            return None

        value = node.text().strip()

        return value or None

    def attribute(
        self,
        selector: str,
        name: str,
    ) -> str | None:

        node = self.first(selector)

        if node is None:
            return None

        value = node.attributes.get(name)

        if value is None:
            return None

        value = value.strip()

        return value or None
```

---

# 14. Test ngay

Tạo:

```text
tests/
└── test_selectolax_document.py
```

Code hoàn chỉnh:

```python
from crawler.infrastructure.parser.selectolax_document import (
    SelectolaxDocument,
)


HTML = """
<html>
    <body>

        <div class="book">
            <h2 class="title">
                Truyện A
            </h2>

            <span class="author">
                Nguyễn Văn A
            </span>

            <a href="/truyen-a">
                Đọc truyện
            </a>
        </div>

        <div class="book">
            <h2 class="title">
                Truyện B
            </h2>

            <span class="author">
                Nguyễn Văn B
            </span>

            <a href="/truyen-b">
                Đọc truyện
            </a>
        </div>

    </body>
</html>
"""


def main():
    document = SelectolaxDocument(HTML)

    print("TITLE:")
    print(document.text(".book .title"))

    print()

    print("AUTHOR:")
    print(document.text(".book .author"))

    print()

    print("URL:")
    print(document.attribute(".book a", "href"))

    print()

    print("BOOKS:")

    books = document.all(".book")

    for book in books:
        print(book.text().strip())


if __name__ == "__main__":
    main()
```

Kết quả tương tự:

```text
TITLE:
Truyện A

AUTHOR:
Nguyễn Văn A

URL:
/truyen-a

BOOKS:
Truyện A
Nguyễn Văn A
Đọc truyện
Truyện B
Nguyễn Văn B
Đọc truyện
```

---

# 15. Nhưng có một vấn đề

Ở đây:

```python
document.text(".book .title")
```

chỉ lấy **node đầu tiên**.

Trong listing:

```text
book 1
book 2
book 3
book 4
...
```

chúng ta cần:

```python
books = document.all(".book")
```

sau đó xử lý **từng book**.

Đây chính là công việc của `ListingParser`.

---

# 16. Node cũng có thể query tiếp

Đây là kỹ thuật rất quan trọng.

Ta có:

```python
books = document.all(".book")
```

Mỗi `book` là một node.

Ta có thể tìm bên trong node đó:

```python
title = book.css_first(".title")
```

Ví dụ:

```python
for book in books:
    title_node = book.css_first(".title")
    author_node = book.css_first(".author")
    link_node = book.css_first("a")

    print(title_node.text())
    print(author_node.text())
    print(link_node.attributes.get("href"))
```

Đây là pattern chúng ta sẽ sử dụng liên tục:

```text
document
   │
   └── find list
          │
          ▼
        item
          │
          ├── title
          ├── author
          └── url
```

---

# 17. Listing thực tế

Giả sử website có:

```html
<div class="list-story">
    
    <div class="story">
        <h3 class="story-title">
            <a href="/truyen-a">
                Truyện A
            </a>
        </h3>

        <div class="story-author">
            Nguyễn Văn A
        </div>
    </div>

    <div class="story">
        <h3 class="story-title">
            <a href="/truyen-b">
                Truyện B
            </a>
        </h3>

        <div class="story-author">
            Nguyễn Văn B
        </div>
    </div>

</div>
```

Parser sẽ làm:

```python
stories = document.all(".story")

for story in stories:

    title_node = story.css_first(".story-title a")
    author_node = story.css_first(".story-author")

    title = title_node.text().strip()
    author = author_node.text().strip()
    url = title_node.attributes.get("href")

    print(title)
    print(author)
    print(url)
```

Kết quả:

```text
Truyện A
Nguyễn Văn A
/truyen-a

Truyện B
Nguyễn Văn B
/truyen-b
```

---

# 18. Tư duy quan trọng: Parser không biết Domain bằng HTML

Selectolax cho chúng ta:

```text
Node
```

Nhưng parser sẽ chuyển:

```text
HTML Node
     ↓
Domain
```

Ví dụ:

```python
NovelSummary(
    title="Truyện A",
    author="Nguyễn Văn A",
    url="/truyen-a",
)
```

Do đó:

```text
Selectolax
     ↓
Infrastructure concern
```

còn:

```text
NovelSummary
     ↓
Domain concern
```

---

# 19. Bài tập thực hành Buổi 2

Hãy tự viết:

```python
html = """
<div class="story">
    <h3>
        <a href="/a">Truyện A</a>
    </h3>
    <span class="author">Tác giả A</span>
</div>

<div class="story">
    <h3>
        <a href="/b">Truyện B</a>
    </h3>
    <span class="author">Tác giả B</span>
</div>
"""
```

Dùng:

```python
SelectolaxDocument
```

để lấy được:

```text
Truyện A | Tác giả A | /a
Truyện B | Tác giả B | /b
```

**Chưa tạo `NovelSummary` ở bài này.**

---

## Những gì cần nhớ sau Buổi 2

```text
HTMLParser
   │
   ├── css_first() → một node
   │
   └── css()       → nhiều node
```

Node:

```text
node.text()
node.attributes
node.css_first()
node.css()
```

Parser:

```text
page_source
    ↓
SelectolaxDocument
    ↓
DOM Node
    ↓
extract data
```

Và nguyên tắc quan trọng nhất:

> **Fetcher lấy HTML. Selectolax đọc HTML. Parser biến HTML thành Domain Model. Parser không gọi HTTP.**

**Buổi 3** chúng ta sẽ thiết kế **Parser Interface bằng `Protocol`**, rồi định nghĩa rõ:

```python
parse_listing(page_source, url)
parse_novel(page_source, url)
parse_chapter(page_source, url)
```

và bắt đầu áp dụng **DIP + ISP + OCP** trước khi xây parser của từng website.
