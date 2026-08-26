# 📘 Selectolax — Buổi 10: DOM Traversal

Ở Buổi 9, chúng ta học cách **tìm node bằng CSS Selector**.

Hôm nay học cách **di chuyển giữa các node trong DOM**.

Đây là kỹ năng cực kỳ quan trọng khi scraper gặp HTML phức tạp:

```text
CSS Selector
      ↓
   tìm được Node
      ↓
   DOM Traversal
      ↓
parent / child / sibling
      ↓
   lấy dữ liệu
```

---

# 1. DOM là gì?

HTML:

```html
<article class="post">

    <header>
        <h1>Python</h1>
    </header>

    <div class="content">
        <p>Hello</p>
        <p>Selectolax</p>
    </div>

</article>
```

Có thể hình dung:

```text
article.post
│
├── header
│   └── h1
│
└── div.content
    ├── p
    └── p
```

Mỗi HTML element là một **Node**.

Selectolax cho phép chúng ta di chuyển giữa những node này.

---

# 2. Parse HTML

```python
from selectolax.parser import HTMLParser


html = """
<article class="post">

    <header>
        <h1>Python</h1>
    </header>

    <div class="content">
        <p>Hello</p>
        <p>Selectolax</p>
    </div>

</article>
"""

tree = HTMLParser(html)
```

Tìm `article`:

```python
article = tree.css_first("article")
```

---

# 3. Node → parent

Giả sử:

```python
content = tree.css_first(".content")
```

Ta muốn đi lên:

```text
.content
   ↑
article
```

Có thể dùng:

```python
parent = content.parent
```

Sau đó:

```python
print(parent.tag)
```

Kết quả:

```text
article
```

---

# 4. Đây là tư duy rất quan trọng

CSS selector:

```python
content = tree.css_first(".content")
```

Sau đó:

```python
parent = content.parent
```

Ta có:

```text
.content
   ↓
 parent
```

Thay vì phải viết selector cực dài:

```css
article.post > div.content
```

ta có thể:

```python
content = tree.css_first(".content")
article = content.parent
```

---

# 5. Parent nhiều cấp

HTML:

```text
article
└── div.wrapper
    └── div.content
        └── p
```

Nếu đang ở:

```python
p = tree.css_first(".content p")
```

có thể:

```python
content = p.parent
wrapper = content.parent
article = wrapper.parent
```

Tức:

```text
p
↑
content
↑
wrapper
↑
article
```

---

# 6. `parent` có thể là `None`

Không nên giả định node luôn có parent.

Ví dụ:

```python
node = ...

if node.parent:
    print(node.parent.tag)
```

Defensive extraction:

```python
parent = node.parent

if parent is None:
    return None
```

---

# 7. Children

HTML:

```html
<div class="content">
    <p>A</p>
    <p>B</p>
    <p>C</p>
</div>
```

Ta lấy:

```python
content = tree.css_first(".content")
```

Sau đó duyệt children.

Trong Selectolax, API traversal có thể khác tùy version/backend, nên khi làm project thực tế hãy kiểm tra đúng API của version bạn đang cài. Với các phiên bản Selectolax hiện đại, cách thường gặp là dùng các thuộc tính/phương thức traversal của `Node`.

Khái niệm cần nhớ trước:

```text
content
├── p
├── p
└── p
```

---

# 8. `iter()` — duyệt descendants

Một cách rất hữu ích là duyệt toàn bộ node bên dưới một node.

Ví dụ:

```python
content = tree.css_first(".content")

for node in content.iter():
    print(node.tag)
```

Có thể thu được:

```text
div
p
p
p
```

Tức:

```text
content
 ↓
descendants
```

---

# 9. Traversal vs CSS Selector

Có hai cách:

### CSS

```python
nodes = tree.css(
    ".content p"
)
```

### Traversal

```python
content = tree.css_first(".content")

for node in content.iter():
    ...
```

Khi nào dùng cái nào?

### CSS Selector

Tốt khi:

```text
HTML structure rõ
selector ổn định
```

### Traversal

Tốt khi:

```text
đã tìm được node gốc
cần xử lý cấu trúc bên trong
cần kiểm tra từng node
logic phụ thuộc vào quan hệ DOM
```

---

# 10. Ví dụ thực tế: Chapter

Giả sử trang truyện:

```html
<div class="chapter">

    <h1>Chương 1</h1>

    <div class="content">

        <p>Ngày hôm đó...</p>

        <p>Trời rất đẹp.</p>

        <p>...</p>

    </div>

    <div class="navigation">
        ...
    </div>

</div>
```

Ta tìm:

```python
content = tree.css_first(".content")
```

Sau đó chỉ xử lý descendants của `content`.

```python
for node in content.iter():
    ...
```

Như vậy:

```text
navigation
```

không bị lấy nhầm.

---

# 11. Parent traversal thực tế

Một pattern rất hay:

```python
node = tree.css_first(
    ".chapter-title"
)

if node:
    chapter = node.parent
```

Ví dụ HTML:

```html
<div class="chapter">

    <h2 class="chapter-title">
        Chương 1
    </h2>

    <div class="content">
        ...
    </div>

</div>
```

Từ:

```text
.chapter-title
```

đi lên:

```text
.chapter
```

sau đó tìm:

```python
content = chapter.css_first(
    ".content"
)
```

---

# 12. Đây là pattern rất mạnh

```python
title = tree.css_first(
    ".chapter-title"
)

if title:
    chapter = title.parent

    content = chapter.css_first(
        ".content"
    )
```

Tư duy:

```text
Tìm node đặc trưng
       ↓
Đi lên container
       ↓
Tìm dữ liệu liên quan
```

---

# 13. Tại sao cách này tốt?

Giả sử trang có:

```html
<div class="sidebar">
    <div class="content">...</div>
</div>

<div class="chapter">
    <h2 class="chapter-title">...</h2>

    <div class="content">...</div>
</div>
```

Nếu:

```python
tree.css_first(".content")
```

có thể lấy nhầm.

Nhưng:

```python
title = tree.css_first(
    ".chapter-title"
)

chapter = title.parent

content = chapter.css_first(
    ".content"
)
```

chúng ta giới hạn phạm vi tìm kiếm.

Đây là một kỹ thuật rất quan trọng:

> **Scope selector bằng container node.**

---

# 14. Scope selector

Thay vì:

```python
tree.css(
    ".chapter .content"
)
```

ta có:

```python
chapter = tree.css_first(
    ".chapter"
)

content = chapter.css_first(
    ".content"
)
```

Lợi ích:

```text
tree
 ↓
chapter
 ↓
content
```

Parser dễ hiểu hơn.

---

# 15. Sibling

HTML:

```html
<div class="metadata">
    <span>Author</span>
</div>

<div class="content">
    Hello
</div>
```

Ta có:

```text
metadata
   →
content
```

Đây là quan hệ **sibling**.

Sibling nghĩa là:

```text
cùng parent
```

Ví dụ:

```text
parent
├── metadata
└── content
```

---

# 16. Khi sibling hữu ích?

Một website có HTML:

```html
<div class="label">
    Nội dung:
</div>

<div class="value">
    Python là...
</div>
```

Không có class semantic tốt.

Ta có thể:

```text
label
 ↓
next sibling
 ↓
value
```

Đây là lúc DOM traversal rất hữu ích.

---

# 17. Cẩn thận với whitespace

HTML:

```html
<div class="label">
    Author
</div>

<div class="value">
    Garden
</div>
```

Giữa hai node có whitespace/text node.

Vì vậy không nên tự giả định:

```text
next sibling = node kế tiếp trong source
```

mà cần sử dụng API traversal của Selectolax đúng theo version để lấy **element sibling** nếu mục tiêu là element.

---

# 18. Traversal theo cấu trúc

Ví dụ:

```html
<div class="info">

    <div class="row">
        <span class="label">Author</span>
        <span class="value">Garden</span>
    </div>

</div>
```

Ta có:

```python
label = tree.css_first(
    ".label"
)
```

Sau đó có thể đi tới container:

```text
.label
   ↑
.row
```

và từ `.row` tìm:

```python
value = row.css_first(".value")
```

Pattern:

```text
label
  ↓
parent row
  ↓
value
```

---

# 19. Đây là "DOM-relative extraction"

Thay vì:

```python
author = tree.css_first(
    ".author"
)
```

ta có thể:

```python
label = tree.css_first(
    ".label"
)

row = label.parent

value = row.css_first(
    ".value"
)
```

Đây là cách extract dựa trên **quan hệ**, không chỉ dựa trên tên class.

---

# 20. Traversal kết hợp CSS

Đây mới là cách tôi khuyên dùng.

Không nên:

```text
CSS selector OR traversal
```

mà:

```text
CSS selector
     ↓
find anchor
     ↓
DOM traversal
     ↓
CSS selector scoped
```

Ví dụ:

```python
title = tree.css_first(
    ".chapter-title"
)

container = title.parent

content = container.css_first(
    ".chapter-content"
)
```

---

# 21. Anchor Node

Khái niệm rất quan trọng:

```text
Anchor Node
```

là node làm điểm neo.

Ví dụ:

```python
title = tree.css_first(
    ".chapter-title"
)
```

`title` là anchor.

Sau đó:

```text
title
 ↓
parent
 ↓
chapter
 ↓
content
```

---

# 22. Ví dụ crawler truyện

HTML:

```html
<div class="chapter">

    <h1 class="chapter-title">
        Chương 12
    </h1>

    <div class="chapter-content">

        <p>Ngày hôm đó...</p>

        <p>...</p>

    </div>

</div>
```

Extractor:

```python
title = tree.css_first(
    ".chapter-title"
)

if title is None:
    return None

container = title.parent

content = container.css_first(
    ".chapter-content"
)
```

Kết quả:

```text
title
    = Chương 12

content
    = <p>Ngày hôm đó...</p>...
```

---

# 23. Traversal để giới hạn vùng scrape

Đây là một trong những ứng dụng quan trọng nhất.

Giả sử:

```html
<article>

    <div class="content">
        <p>Article</p>

        <div class="related">
            <p>Related article</p>
        </div>

    </div>

</article>
```

Nếu:

```python
tree.css(".content p")
```

sẽ có:

```text
Article
Related article
```

Nếu muốn chỉ paragraph trực tiếp:

```python
content = tree.css_first(".content")

paragraphs = content.css(
    ":scope > p"
)
```

Tùy parser/version, hỗ trợ `:scope` cần được kiểm tra; nếu không muốn phụ thuộc vào nó, traversal trực tiếp children là lựa chọn rõ ràng hơn.

Điểm quan trọng:

> Khi đã có container, hãy xử lý trong phạm vi container đó.

---

# 24. Một chiến lược tốt hơn cho Article Extractor

Thay vì:

```python
tree.css(".article-content p")
```

hãy:

```python
content = tree.css_first(
    ".article-content"
)
```

sau đó:

```python
for node in content.iter():
    ...
```

hoặc chọn children/descendants phù hợp.

Như vậy parser biết rõ:

```text
Đây là vùng nội dung bài viết.
```

---

# 25. Tìm node rồi đi lên

Một pattern phổ biến khác:

```python
image = tree.css_first(
    'img[alt="cover"]'
)

if image:
    container = image.parent
```

Ví dụ:

```html
<div class="book-cover">
    <img
        alt="cover"
        src="cover.jpg"
    >
</div>
```

Từ:

```text
img
 ↓
parent
 ↓
.book-cover
```

---

# 26. Tìm node rồi đi xuống

Ví dụ:

```python
article = tree.css_first(
    "article"
)

if article:
    title = article.css_first(
        "h1"
    )

    content = article.css_first(
        ".content"
    )
```

Đây là:

```text
article
├── h1
└── .content
```

---

# 27. Tìm node rồi đi ngang

Ví dụ:

```text
row
├── label
└── value
```

Ta tìm:

```python
label = row.css_first(
    ".label"
)
```

sau đó tìm sibling element thích hợp hoặc quay về parent:

```python
row = label.parent

value = row.css_first(
    ".value"
)
```

Trong thực tế, **đi lên parent rồi tìm node liên quan** thường rõ ràng và ít fragile hơn việc phụ thuộc quá nhiều vào sibling.

---

# 28. Traversal đệ quy

Bạn có thể duyệt cây:

```python
def walk(node, level=0):
    print(
        "  " * level,
        node.tag,
    )

    for child in node.iter():
        ...
```

Nhưng cần chú ý:

`iter()` thường đã duyệt descendants, nên nếu muốn xây một tree walker đệ quy thực sự, hãy dùng API children của phiên bản Selectolax bạn đang sử dụng.

Ý tưởng:

```text
article
├── header
│   └── h1
└── content
    ├── p
    └── p
```

Traversal:

```text
visit article
  visit header
    visit h1
  visit content
    visit p
    visit p
```

---

# 29. Khi nào cần DOM Traversal?

### CSS selector đủ tốt:

```python
tree.css_first(
    ".article-title"
)
```

Không cần traversal.

### HTML phức tạp:

```text
tìm title
 ↓
parent container
 ↓
tìm content
```

Nên traversal.

### Dữ liệu phụ thuộc quan hệ:

```text
label → value
title → container → content
image → card → title
```

Nên traversal.

---

# 30. Một ví dụ thực tế hơn

HTML:

```html
<div class="story">

    <div class="story-header">

        <h1 class="title">
            Tu Tiên
        </h1>

        <div class="metadata">

            <span class="label">
                Author
            </span>

            <span class="value">
                Nguyễn Văn A
            </span>

        </div>

    </div>

    <div class="story-content">
        ...
    </div>

</div>
```

Ta bắt đầu từ title:

```python
title = tree.css_first(
    ".story .title"
)
```

Đi lên:

```python
header = title.parent
```

Từ `header`:

```python
metadata = header.css_first(
    ".metadata"
)
```

Từ `metadata`:

```python
value = metadata.css_first(
    ".value"
)
```

Kết quả:

```text
Title
 ↓
Header
 ↓
Metadata
 ↓
Author
```

---

# 31. Scoped extraction

Đây là pattern tôi muốn bạn ghi nhớ:

```python
root = tree.css_first(
    ".story"
)

if root is None:
    return None

title = root.css_first(
    ".title"
)

content = root.css_first(
    ".story-content"
)

author = root.css_first(
    ".metadata .value"
)
```

Thay vì tìm toàn bộ document:

```python
tree.css_first(".title")
tree.css_first(".story-content")
tree.css_first(".metadata .value")
```

Ta giới hạn:

```text
tree
 ↓
story
 ↓
mọi extraction
```

---

# 32. Vì sao scoped extraction tốt?

Giả sử trang có:

```text
story
├── title
└── content

sidebar
├── title
└── content
```

Global:

```python
tree.css_first(".title")
```

có thể lấy sidebar.

Scoped:

```python
story = tree.css_first(".story")

title = story.css_first(
    ".title"
)
```

chính xác hơn.

---

# 33. Traversal trong `ArticleExtractor`

Ta có thể thiết kế:

```python
class ArticleExtractor:

    def extract(
        self,
        html: str,
        url: str,
    ):

        tree = HTMLParser(html)

        root = self._find_article_root(
            tree
        )

        if root is None:
            return None

        return Article(
            title=self._extract_title(root),
            content_html=self._extract_content(root),
            author=self._extract_author(root),
        )
```

Điểm quan trọng:

```text
tree
 ↓
article root
 ↓
all extraction
```

---

# 34. `_find_article_root`

```python
def _find_article_root(self, tree):

    return (
        tree.css_first("article")
        or tree.css_first(".article")
        or tree.css_first(".post")
        or tree.css_first(".story")
    )
```

Sau đó:

```python
root = self._find_article_root(tree)
```

---

# 35. Extract title trong root

```python
def _extract_title(self, root):

    node = (
        root.css_first(".article-title")
        or root.css_first(".post-title")
        or root.css_first("h1")
    )

    if node is None:
        return None

    return node.text(strip=True)
```

---

# 36. Extract content trong root

```python
def _extract_content(self, root):

    node = (
        root.css_first(".article-content")
        or root.css_first(".post-content")
        or root.css_first(".entry-content")
    )

    if node is None:
        return None

    return node.html
```

---

# 37. Đây là kiến trúc tốt hơn

Thay vì:

```text
ArticleExtractor
 ├── tree.css_first(...)
 ├── tree.css_first(...)
 ├── tree.css_first(...)
 ├── tree.css_first(...)
 └── tree.css_first(...)
```

ta có:

```text
ArticleExtractor
       │
       ▼
 Article Root
       │
 ├─────┼───────────┐
 ▼     ▼           ▼
title content    author
```

Đây là **scoped DOM traversal**.

---

# 38. Traversal + fallback

Ta có thể viết helper:

```python
def first_match(root, selectors):

    for selector in selectors:

        node = root.css_first(
            selector
        )

        if node is not None:
            return node

    return None
```

Sau đó:

```python
root = first_match(
    tree,
    (
        "article",
        ".article",
        ".post",
        ".story",
    ),
)
```

Và:

```python
title = first_match(
    root,
    (
        ".article-title",
        ".post-title",
        ".title",
        "h1",
    ),
)
```

Rất sạch.

---

# 39. DOM Traversal không thay thế CSS Selector

Sai lầm thường gặp:

> "Học traversal rồi thì không cần CSS."

Không.

Hai kỹ thuật bổ trợ nhau:

```text
CSS Selector
     ↓
Find anchor
     ↓
DOM Traversal
     ↓
Scoped CSS
     ↓
Extract
```

Đây là workflow rất mạnh.

---

# 40. Mental Model

Hãy nhớ 3 thao tác:

```text
FIND
 ↓
MOVE
 ↓
EXTRACT
```

### FIND

```python
node = tree.css_first(...)
```

### MOVE

```python
parent = node.parent
```

hoặc đi vào vùng con / descendants.

### EXTRACT

```python
node.text(strip=True)
```

hoặc:

```python
node.attributes.get("href")
```

---

# 41. Bài tập 1 — Parent

Cho:

```html
<div class="article">
    <div class="content">
        <p>Hello</p>
    </div>
</div>
```

Tìm:

```python
p = tree.css_first("p")
```

Sau đó dùng traversal để lấy:

```text
.content
.article
```

Không được dùng:

```python
tree.css_first(".article")
```

---

# 42. Bài tập 2 — Scoped extraction

Cho:

```html
<div class="sidebar">
    <h1>Sidebar</h1>
</div>

<article>
    <h1>Real Article</h1>

    <div class="content">
        Hello
    </div>
</article>
```

Viết:

```python
article = ...
title = ...
content = ...
```

Kết quả:

```text
Real Article
Hello
```

Không lấy:

```text
Sidebar
```

---

# 43. Bài tập 3 — Anchor

Cho:

```html
<div class="chapter">

    <h2 class="chapter-title">
        Chương 10
    </h2>

    <div class="chapter-content">
        <p>Hello</p>
    </div>

</div>
```

Hãy:

```text
1. tìm chapter-title
2. đi lên parent
3. tìm chapter-content
4. lấy HTML
```

Pipeline phải là:

```text
chapter-title
      ↓
    parent
      ↓
chapter-content
```

---

# 44. Bài tập 4 — Metadata

Cho:

```html
<div class="metadata">

    <span class="label">
        Author
    </span>

    <span class="value">
        Garden
    </span>

</div>
```

Bắt đầu từ:

```python
label = tree.css_first(".label")
```

Hãy tìm:

```text
Garden
```

bằng cách:

```text
label
 ↓
parent
 ↓
.value
```

---

# 45. Bài tập 5 — Chapter extractor

Xây:

```python
@dataclass
class Chapter:
    title: str | None
    content_html: str | None
```

Extractor:

```python
class ChapterExtractor:

    def extract(
        self,
        html: str,
    ) -> Chapter:
        ...
```

Yêu cầu:

```text
1. tìm chapter root
2. tìm title
3. tìm content
4. chỉ extract trong chapter root
```

---

# 46. Bài tập 6 — Thực chiến

HTML:

```html
<body>

    <aside>
        <div class="content">
            Quảng cáo
        </div>
    </aside>

    <main>

        <article class="story">

            <header>
                <h1>Tu Tiên</h1>
            </header>

            <div class="story-content">

                <p>Đoạn 1</p>

                <div class="related">
                    <p>Truyện liên quan</p>
                </div>

                <p>Đoạn 2</p>

            </div>

        </article>

    </main>

</body>
```

Mục tiêu:

```text
title:
Tu Tiên

content:
Đoạn 1
Đoạn 2
```

Không được lấy:

```text
Quảng cáo
Truyện liên quan
```

Hãy suy nghĩ theo:

```text
body
 ↓
article.story
 ↓
story-content
 ↓
direct children
```

---

# 🧠 Tổng kết Buổi 10

Hôm nay bạn cần hình thành tư duy:

```text
                HTML
                  │
                  ▼
          ┌──────────────┐
          │ CSS Selector │
          └──────┬───────┘
                 │
             Anchor Node
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    parent    children   sibling
       │         │         │
       └─────────┼─────────┘
                 ▼
          Scoped Extraction
                 │
                 ▼
               Data
```

Đặc biệt nhớ pattern này:

```python
root = tree.css_first(".story")

if root is None:
    return None

title = root.css_first("h1")
content = root.css_first(
    ".story-content"
)
```

**CSS Selector tìm "đúng vùng", DOM Traversal giúp chúng ta đi trong vùng đó.**

Với crawler truyện của bạn, đây là kỹ thuật cực kỳ hữu ích để tránh lấy nhầm `sidebar`, `related posts`, `advertisement`, `navigation` khi extract nội dung chương.
