# Buổi 17 — Remove Navigation

Ở Buổi 16, chúng ta học:

```text
HTML
 ↓
AdDetector
 ↓
Remove quảng cáo
```

Hôm nay xử lý **navigation** — những thành phần điều hướng không thuộc nội dung bài viết.

Mục tiêu:

```text
HTML
 ↓
Extract article
 ↓
HTMLCleaner
 ↓
Remove Navigation
 ↓
Clean HTML
 ↓
html2text
 ↓
Markdown
```

---

# 1. Navigation là gì?

Một trang web có thể chứa:

```text
Header
Navbar
Menu
Breadcrumb
Sidebar
Pagination
Category menu
Related links
Footer navigation
Social navigation
```

Ví dụ:

```html
<nav>
    <a href="/">Home</a>
    <a href="/python">Python</a>
    <a href="/tutorial">Tutorial</a>
</nav>

<article>
    <h1>Python asyncio</h1>
    <p>...</p>
</article>
```

Nếu chuyển trực tiếp sang Markdown:

```markdown
[Home](/)

[Python](/python)

[Tutorial](/tutorial)

# Python asyncio

...
```

Navigation trở thành rác.

---

# 2. Navigation khác quảng cáo

Quảng cáo:

```text
"Đừng lấy phần này."
```

Navigation:

```text
"Đây là cách người dùng di chuyển trong website."
```

Ví dụ:

```html
<nav>
    Home
    Categories
    Search
    Login
</nav>
```

Không phải quảng cáo.

Do đó không nên nhét tất cả vào:

```python
AdDetector
```

Mà tạo:

```text
NavigationDetector
```

---

# 3. Strategy đầu tiên: semantic HTML

HTML5 có các tag semantic:

```html
<nav>
<header>
<footer>
<main>
<article>
<aside>
<section>
```

Trong đó:

```html
<nav>
```

là tín hiệu rất mạnh.

Nếu đang clean **article content**, gặp:

```html
<nav>
```

thường có thể remove.

---

# 4. `RemoveSelectorRule`

Chúng ta đã có từ Buổi 16:

```python
class RemoveSelectorRule:

    def __init__(self, selectors):
        self.selectors = list(selectors)

    def apply(self, root):
        for selector in self.selectors:
            for node in root.css(selector):
                node.decompose()
```

Có thể dùng:

```python
navigation_rule = RemoveSelectorRule([
    "nav",
])
```

---

# 5. Nhưng `nav` không phải lúc nào cũng xấu

Ví dụ:

```html
<article>

<h1>Python Tutorial</h1>

<nav>
    <a href="#intro">Introduction</a>
    <a href="#install">Installation</a>
    <a href="#async">Asyncio</a>
</nav>

<p>...</p>

</article>
```

Đây có thể là:

> Table of contents của chính bài viết.

Nếu xóa:

```html
<nav>
```

thì bạn mất Table of Contents.

Vì vậy:

```text
nav ≠ chắc chắn là navigation rác
```

---

# 6. Đây là vấn đề context

Navigation bên ngoài:

```text
<body>
 ├── header
 ├── nav        ← website navigation
 └── article
```

Navigation bên trong article:

```text
<article>
 ├── h1
 ├── nav        ← table of contents
 └── p
```

Hai node đều là:

```html
<nav>
```

nhưng semantic khác nhau.

Đây là một bài học rất quan trọng:

> **DOM context quan trọng hơn selector đơn lẻ.**

---

# 7. Context-aware cleaning

Ta có thể chia:

```text
Global navigation
```

và:

```text
Article navigation
```

Ví dụ:

```text
Global:
<nav class="main-menu">

Article:
<nav class="toc">
```

Ta ưu tiên remove:

```python
"nav.main-menu"
```

thay vì:

```python
"nav"
```

---

# 8. Navigation selectors phổ biến

Một bộ selector ban đầu:

```python
NAV_SELECTORS = [
    "nav",
    ".nav",
    ".navbar",
    ".navigation",
    ".menu",
    ".main-menu",
    ".site-menu",
]
```

Nhưng có vấn đề.

```python
".menu"
```

có thể là:

```html
<div class="menu">
    Recipe ingredients...
</div>
```

hoặc:

```html
<div class="menu">
    Product menu...
</div>
```

Không nên remove mù quáng.

---

# 9. Exact class token

Tương tự Buổi 16:

Không nên:

```python
if "menu" in class_name:
```

Nên tokenize:

```python
classes = node.attributes.get("class", "")

tokens = classes.lower().split()
```

Ví dụ:

```text
"main-menu horizontal"
```

→

```python
[
    "main-menu",
    "horizontal",
]
```

---

# 10. `NavigationDetector`

Ta có thể bắt đầu:

```python
class NavigationDetector:

    NAV_CLASSES = {
        "nav",
        "navbar",
        "navigation",
        "menu",
        "main-menu",
        "site-menu",
    }

    def has_nav_class(self, node) -> bool:
        classes = node.attributes.get("class", "")

        tokens = classes.lower().split()

        return any(
            token in self.NAV_CLASSES
            for token in tokens
        )
```

---

# 11. ID cũng là tín hiệu

Ví dụ:

```html
<div id="main-navigation">
```

Có thể kiểm tra:

```python
def has_nav_id(self, node) -> bool:
    node_id = node.attributes.get("id", "")

    value = node_id.lower()

    keywords = (
        "navigation",
        "navbar",
        "main-menu",
        "site-menu",
    )

    return any(
        keyword in value
        for keyword in keywords
    )
```

---

# 12. Semantic `<nav>` có score cao

Ta có thể xây scoring:

```python
class NavigationDetector:

    def score(self, node) -> int:
        score = 0

        if node.tag == "nav":
            score += 4

        if self.has_nav_class(node):
            score += 3

        if self.has_nav_id(node):
            score += 3

        return score
```

Sau đó:

```python
def is_navigation(self, node) -> bool:
    return self.score(node) >= 4
```

---

# 13. Nhưng scoring chưa đủ

Ví dụ:

```html
<article>
    <nav class="toc">
        ...
    </nav>
</article>
```

Score:

```text
nav = +4
class? = 0
```

→ 4.

Nếu threshold:

```python
score >= 4
```

nó bị remove.

Nhưng chúng ta muốn giữ TOC.

Vì vậy cần thêm:

```text
context
```

---

# 14. Kiểm tra class `toc`

Table of Contents thường có:

```text
toc
table-of-contents
table_of_contents
contents
```

Có thể coi đây là **keep signal**.

```python
TOC_CLASSES = {
    "toc",
    "table-of-contents",
    "table_of_contents",
    "contents",
}
```

---

# 15. `is_toc`

```python
def is_toc(self, node) -> bool:
    classes = node.attributes.get("class", "")

    tokens = classes.lower().split()

    return any(
        token in TOC_CLASSES
        for token in tokens
    )
```

Sau đó:

```python
def is_navigation(self, node) -> bool:

    if self.is_toc(node):
        return False

    return self.score(node) >= 4
```

---

# 16. Đây là một pattern rất hay

Thay vì chỉ có:

```text
REMOVE signal
```

ta có:

```text
REMOVE signals
KEEP signals
```

Ví dụ:

```text
nav                  +4 REMOVE
class="menu"         +3 REMOVE
class="toc"          -5 KEEP
```

Đây chính là tư duy classifier đơn giản.

---

# 17. Navigation bằng link density

Đây là kỹ thuật quan trọng.

Navigation thường có rất nhiều:

```html
<a>
```

Ví dụ:

```html
<nav>
    <a>Home</a>
    <a>Python</a>
    <a>JavaScript</a>
    <a>Rust</a>
    <a>Go</a>
</nav>
```

Trong khi article:

```html
<p>
    Python is a programming language...
</p>
```

có ít link.

Ta có thể tính:

```text
link density =
số lượng link
-----------------
tổng số text/content
```

---

# 18. Đếm link

Selectolax:

```python
links = node.css("a")
```

Số link:

```python
link_count = len(node.css("a"))
```

Text:

```python
text = node.text(strip=True)
```

---

# 19. Một heuristic đơn giản

```python
def link_count(node) -> int:
    return len(node.css("a"))
```

Ví dụ:

```text
Navigation:
10 links

Article:
2 links
```

Navigation có xu hướng:

```text
link_count ↑
```

---

# 20. Link density thực tế

Một cách đơn giản:

```python
def link_density(node) -> float:
    text = node.text(strip=True)

    if not text:
        return 0.0

    link_text = " ".join(
        link.text(strip=True)
        for link in node.css("a")
    )

    return len(link_text) / len(text)
```

Ví dụ:

```text
Navigation:
[Home] [Python] [Tutorial]
```

phần lớn text nằm trong `<a>`.

Do đó:

```text
density ≈ 1
```

Article:

```text
Python is a programming language.
See [documentation] for more information.
```

density thấp hơn.

---

# 21. Nhưng link density không hoàn hảo

Một article có:

```text
10 links
```

cũng có thể có link density cao.

Ví dụ:

```text
List of Python libraries:
Requests
HTTPX
BeautifulSoup
Selectolax
...
```

Đây vẫn là nội dung hợp lệ.

Do đó:

```text
link density
```

chỉ là **signal**, không phải quyết định tuyệt đối.

---

# 22. Kết hợp semantic + class + link density

Một detector tốt hơn:

```text
<nav>                 +4
class="main-menu"     +3
id="navigation"       +3
link density cao      +2
class="toc"           -5
article descendant    -?
```

Sau đó:

```text
score
 ↓
decision
```

---

# 23. Xác định navigation bên ngoài article

Một kiến trúc tốt hơn là:

```text
HTML
 ↓
extract article
 ↓
clean article
```

Nếu chúng ta đã có:

```python
article = extractor.extract(html)
```

thì:

```text
header
main navigation
footer
```

nằm ngoài `article` đã tự động bị loại khỏi phạm vi xử lý.

Đây là lý do **Article Extraction** cực kỳ quan trọng.

---

# 24. Ví dụ

HTML:

```html
<body>

<header>
    <nav class="main-menu">
        Home
        Python
        Tutorials
    </nav>
</header>

<article>
    <h1>Python</h1>

    <p>Hello Python.</p>
</article>

<footer>
    <nav class="footer-menu">
        Privacy
        About
    </nav>
</footer>

</body>
```

Nếu:

```python
article = tree.css_first("article")
```

thì ta chỉ clean:

```text
article
```

Kết quả:

```text
header      ← không đụng
footer      ← không đụng
main nav    ← không đụng
article     ← clean
```

Navigation đã tự nhiên biến mất khỏi output.

---

# 25. Vậy tại sao vẫn cần Navigation Rule?

Có những website:

```html
<article>

    <div class="article-body">

        <div class="navigation">
            Previous | Next
        </div>

        <p>Chapter content...</p>

    </div>

</article>
```

Navigation nằm **bên trong vùng article**.

Lúc này cần:

```text
NavigationRule
```

---

# 26. Các loại navigation

Ta nên phân loại:

```text
1. Site navigation
2. Category navigation
3. Breadcrumb
4. Pagination
5. Previous / Next
6. Table of Contents
7. Related navigation
```

Không phải tất cả đều nên remove.

---

# 27. Breadcrumb

Ví dụ:

```html
<div class="breadcrumb">
    Home > Python > Asyncio
</div>
```

Đây thường là metadata/navigation.

Nếu mục tiêu:

```text
Article → Markdown
```

thì thường remove.

Selector:

```python
BREADCRUMB_SELECTORS = [
    ".breadcrumb",
    ".breadcrumbs",
    "[aria-label='breadcrumb']",
]
```

---

# 28. Pagination

Ví dụ:

```html
<div class="pagination">
    <a>Previous</a>
    <a>1</a>
    <a>2</a>
    <a>3</a>
    <a>Next</a>
</div>
```

Thường không thuộc nội dung.

Có thể:

```python
PAGINATION_SELECTORS = [
    ".pagination",
    ".pager",
    ".page-nav",
]
```

---

# 29. Previous / Next

Một website truyện có thể:

```html
<div class="chapter-navigation">

    <a href="/chapter/10">
        Previous
    </a>

    <a href="/chapter/12">
        Next
    </a>

</div>
```

Nếu crawl chapter:

```text
Previous
Next
```

không nên xuất hiện trong Markdown.

Đây đặc biệt quan trọng với project crawler truyện của bạn.

---

# 30. Site-specific selectors

Ví dụ source A:

```python
source_a_rules = [
    RemoveSelectorRule([
        ".main-menu",
        ".breadcrumb",
        ".chapter-navigation",
    ])
]
```

Source B:

```python
source_b_rules = [
    RemoveSelectorRule([
        "#navbar",
        ".breadcrumbs",
        ".pagination",
    ])
]
```

Engine giống nhau.

Configuration khác nhau.

---

# 31. Navigation Rule

Ta có thể tạo:

```python
class NavigationRemovalRule:

    SELECTORS = [
        "nav",
        ".navbar",
        ".navigation",
        ".main-menu",
        ".breadcrumb",
        ".breadcrumbs",
        ".pagination",
        ".pager",
    ]

    def apply(self, root):
        for selector in self.SELECTORS:
            for node in root.css(selector):
                node.decompose()
```

Nhưng đây là **phiên bản đơn giản**.

Có nguy cơ xóa TOC.

---

# 32. Phiên bản an toàn hơn

```python
class NavigationRemovalRule:

    SELECTORS = [
        ".main-menu",
        ".site-menu",
        ".breadcrumb",
        ".breadcrumbs",
        ".pagination",
        ".pager",
    ]

    def apply(self, root):
        for selector in self.SELECTORS:
            for node in root.css(selector):
                node.decompose()
```

Chúng ta cố tình **không remove mọi `<nav>`**.

---

# 33. Tại sao?

Vì:

```html
<nav>
```

có thể là:

```text
site navigation
```

hoặc:

```text
article TOC
```

Nếu không biết context:

```text
KEEP
```

an toàn hơn.

---

# 34. `aria-label`

HTML hiện đại có:

```html
<nav aria-label="Main navigation">
```

hoặc:

```html
<div aria-label="breadcrumb">
```

Ta có thể sử dụng:

```python
root.css('[aria-label="breadcrumb"]')
```

Ví dụ:

```python
BREADCRUMB_SELECTORS = [
    '[aria-label="breadcrumb"]',
    '[aria-label="Breadcrumb"]',
]
```

---

# 35. Case sensitivity

HTML attribute có thể có:

```text
breadcrumb
Breadcrumb
BREADCRUMB
```

Tùy parser/browser normalization.

Đừng viết quá nhiều assumption.

Nếu website cụ thể:

```python
"[aria-label='breadcrumb']"
```

là đủ.

Nếu cần generic processing, có thể lấy attribute rồi `.lower()`.

---

# 36. Navigation Detector

Một detector có thể:

```python
class NavigationDetector:

    NAV_CLASSES = {
        "navbar",
        "navigation",
        "main-menu",
        "site-menu",
    }

    def score(self, node) -> int:
        score = 0

        if node.tag == "nav":
            score += 4

        classes = node.attributes.get("class", "")
        tokens = classes.lower().split()

        if any(
            token in self.NAV_CLASSES
            for token in tokens
        ):
            score += 3

        return score
```

---

# 37. TOC protection

Thêm:

```python
TOC_CLASSES = {
    "toc",
    "table-of-contents",
    "table_of_contents",
}
```

```python
def is_toc(self, node) -> bool:
    classes = node.attributes.get("class", "")
    tokens = classes.lower().split()

    return any(
        token in TOC_CLASSES
        for token in tokens
    )
```

---

# 38. Decision

```python
def is_navigation(self, node) -> bool:

    if self.is_toc(node):
        return False

    return self.score(node) >= 4
```

Đây là phiên bản đơn giản nhưng thể hiện đúng tư duy.

---

# 39. Rule

```python
class NavigationRemovalRule:

    def __init__(self, detector):
        self.detector = detector

    def apply(self, root):
        candidates = []

        for node in root.css("*"):
            if self.detector.is_navigation(node):
                candidates.append(node)

        for node in candidates:
            node.decompose()
```

Pattern:

```text
find
 ↓
evaluate
 ↓
collect
 ↓
remove
```

Giống Buổi 16.

---

# 40. Một vấn đề mới: nested navigation

Ví dụ:

```html
<div class="navigation">

    <nav>
        <a>Home</a>
    </nav>

</div>
```

Cả hai có thể bị detector.

Nếu remove:

```text
outer div
```

thì:

```text
inner nav
```

cũng biến mất.

Không cần remove cả hai.

Đây là lý do collect candidates rồi cần xử lý parent/child.

---

# 41. Parent/child conflict

Ví dụ:

```text
candidate A
 └── candidate B
```

Nếu A bị remove:

```text
B
```

tự động mất.

Ta chỉ cần remove A.

Có thể sau này xây:

```python
def is_descendant(...)
```

nhưng hiện tại chưa cần quá phức tạp.

---

# 42. Một cách đơn giản

Sort candidate theo DOM depth:

```text
parent
  ↓
child
```

và loại candidate nằm bên trong candidate khác.

Concept:

```text
candidates
 ↓
remove nested candidates
 ↓
decompose
```

Đây là một bài toán DOM algorithm khá thú vị.

---

# 43. Breadcrumb + Navigation + Pagination

Một cleaner thực tế:

```python
cleaner = HTMLCleaner([
    RemoveSelectorRule([
        ".breadcrumb",
        ".breadcrumbs",
        ".pagination",
        ".pager",
        ".main-menu",
        ".site-menu",
    ]),
])
```

Đây có thể đã đủ cho nhiều website.

Không cần ngay lập tức xây AI detector.

---

# 44. Test 1 — Main navigation

```python
def test_remove_main_navigation():
    html = """
    <article>

        <nav class="main-menu">
            Home
            Python
            Tutorial
        </nav>

        <h1>Python</h1>

        <p>Hello Python.</p>

    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    rule = RemoveSelectorRule([
        ".main-menu",
    ])

    rule.apply(article)

    result = article.html

    assert "Home" not in result
    assert "Python" in result
    assert "Hello Python" in result
```

Lưu ý:

```text
Python
```

vẫn còn vì `<h1>` chứa Python.

---

# 45. Test 2 — Breadcrumb

```python
def test_remove_breadcrumb():
    html = """
    <article>

        <div class="breadcrumb">
            Home > Python > Asyncio
        </div>

        <h1>Asyncio</h1>

        <p>Asyncio is...</p>

    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    rule = RemoveSelectorRule([
        ".breadcrumb",
    ])

    rule.apply(article)

    result = article.html

    assert "Home > Python > Asyncio" not in result
    assert "Asyncio" in result
```

---

# 46. Test 3 — TOC phải giữ

```python
def test_keep_toc():
    html = """
    <article>

        <nav class="toc">
            <a href="#intro">Introduction</a>
            <a href="#install">Installation</a>
        </nav>

        <h1>Python</h1>

    </article>
    """
```

Nếu detector của bạn hỗ trợ TOC:

```python
assert detector.is_navigation(toc) is False
```

Đây là một test rất quan trọng.

---

# 47. Test 4 — Article navigation

HTML:

```html
<div class="chapter-navigation">
    <a>Previous</a>
    <a>Next</a>
</div>
```

Rule:

```python
RemoveSelectorRule([
    ".chapter-navigation",
])
```

Phải remove.

Đặc biệt hữu ích cho crawler truyện.

---

# 48. Test 5 — Không xóa content

```html
<div class="content">
    Python tutorial
</div>
```

Detector:

```python
detector.is_navigation(node)
```

phải trả:

```python
False
```

---

# 49. Link density — bài tập

Tạo:

```python
def link_density(node) -> float:
    ...
```

Test:

```html
<div class="menu">
    <a>Home</a>
    <a>Python</a>
    <a>Rust</a>
    <a>Go</a>
</div>
```

và:

```html
<div class="content">
    <p>
        Python is a programming language.
        It is widely used for web development.
    </p>
</div>
```

So sánh:

```python
density_menu
density_content
```

Bạn sẽ thấy sự khác biệt.

---

# 50. Nhưng chưa dùng density để auto-delete

Ở Buổi 17:

```text
link density
```

chỉ để học **signal**.

Đừng vội:

```python
if density > 0.5:
    node.decompose()
```

Vì:

```text
article link list
```

có thể bị xóa.

---

# 51. Navigation và Article Extraction

Một insight quan trọng:

Nếu article extraction tốt:

```text
BODY
 │
 ├── Header
 ├── Navigation
 ├── Sidebar
 │
 └── Article ← lấy cái này
       │
       ├── title
       ├── content
       └── images
```

thì bạn **không cần quá mạnh tay remove navigation**.

Do đó:

```text
Article Extraction
```

và:

```text
Navigation Removal
```

có quan hệ rất chặt.

---

# 52. Thứ tự xử lý

Tôi khuyên:

```text
1. Extract article
2. Remove known unwanted elements
3. Normalize HTML
4. Convert Markdown
```

Không nên:

```text
1. Remove toàn bộ navigation từ document
2. Tìm article
```

vì có thể ảnh hưởng đến cấu trúc giúp extractor nhận diện article.

---

# 53. Pipeline hiện tại

Sau Buổi 17:

```text
                        HTML
                          │
                          ▼
                    Selectolax
                          │
                          ▼
                 ArticleExtractor
                          │
                          ▼
                       Article
                          │
                          ▼
                    HTMLCleaner
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        AdRemovalRule        NavigationRule
              │                       │
              └───────────┬───────────┘
                          ▼
                    Clean HTML
                          │
                          ▼
                      html2text
                          │
                          ▼
                      Markdown
```

---

# 54. Architecture tốt hơn

Tới đây:

```python
cleaner = HTMLCleaner([
    AdRemovalRule(AdDetector()),
    NavigationRemovalRule(NavigationDetector()),
])
```

Cleaner không biết:

```text
ad
navigation
```

Nó chỉ biết:

```python
rule.apply(root)
```

Đây là một abstraction rất đẹp.

---

# 55. Generic rules vs Site rules

Tôi khuyên chia:

```text
Generic
├── script
├── style
└── obvious ad

Site-specific
├── .chapter-navigation
├── .main-menu
├── .breadcrumb
└── .related
```

Ví dụ:

```python
common_rules = [
    RemoveSelectorRule([
        "script",
        "style",
    ]),
]
```

Source truyện:

```python
story_rules = [
    RemoveSelectorRule([
        ".chapter-navigation",
        ".breadcrumb",
        ".share-buttons",
    ]),
]
```

Sau đó:

```python
cleaner = HTMLCleaner([
    *common_rules,
    *story_rules,
])
```

---

# 56. Đây là kiến trúc rất phù hợp crawler

Ví dụ:

```text
sources/
├── source_a/
│   ├── extractor.py
│   └── cleaner.py
│
├── source_b/
│   ├── extractor.py
│   └── cleaner.py
│
└── source_c/
    ├── extractor.py
    └── cleaner.py
```

Mỗi source biết:

```text
HTML structure
selectors
special cases
```

Còn framework biết:

```text
Rule
Cleaner
Converter
Pipeline
```

---

# 57. Bài tập chính của Buổi 17

Hãy xây:

```text
htmlcleaner/
├── cleaner.py
├── rules.py
├── detectors.py
└── tests/
    └── test_navigation.py
```

Với:

```python
class NavigationDetector:
    ...
```

và:

```python
class NavigationRemovalRule:
    ...
```

---

# 58. Yêu cầu

Detector phải nhận diện được ít nhất:

```text
<nav>
.main-menu
.navbar
.navigation
.breadcrumb
.pagination
```

Nhưng **không được tự động xóa**:

```text
.toc
.table-of-contents
```

---

# 59. Bài tập nâng cao

Viết:

```python
def link_density(node) -> float:
    ...
```

Sau đó tạo:

```python
NavigationDetector
```

có score:

```text
<nav>                  +4
.navbar                +3
.navigation            +3
.main-menu             +3
breadcrumb             +3
pagination             +3
high link density      +2
.toc                   -5
```

Thử nghiệm threshold.

---

# 60. Điều cần nhớ

Buổi 17 có 6 ý chính:

```text
1. Navigation không đồng nghĩa với quảng cáo.

2. <nav> là signal mạnh nhưng không phải tuyệt đối.

3. Context của DOM rất quan trọng.

4. Table of Contents có thể nằm trong <nav>
   nên không được remove mù quáng.

5. Link density là heuristic hữu ích,
   nhưng không nên dùng một mình.

6. Article extraction tốt sẽ giảm rất nhiều
   nhu cầu remove navigation.
```

---

## Mental model

Hãy nhớ:

```text
                Navigation
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     selector      class      link density
        │            │            │
        └────────────┼────────────┘
                     ▼
                  signals
                     │
                     ▼
                  context
                     │
              ┌──────┴──────┐
              ▼             ▼
            REMOVE         KEEP
                            ↑
                           TOC
```

Và pipeline chúng ta đang xây ngày càng hoàn chỉnh:

```text
HTTPX
  ↓
HTML
  ↓
Selectolax
  ↓
ArticleExtractor
  ↓
HTMLCleaner
  ├── AdRemovalRule
  └── NavigationRemovalRule
  ↓
Clean HTML
  ↓
html2text
  ↓
Markdown
```

**Buổi 18** sẽ đi sâu vào `script/style`: tại sao `html2text` đã có thể xử lý chúng nhưng trong một HTML-cleaning pipeline chuyên nghiệp vẫn nên có **explicit `ScriptStyleRemovalRule`**, cách xử lý inline JavaScript/CSS, `<noscript>`, `<template>`, event attributes như `onclick`, và vấn đề **không được làm mất nội dung trong `<code>`/`<pre>`**.
