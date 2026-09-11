Đúng. Theo roadmap bạn vừa chốt, **Buổi 11 là Pagination Robustness**, và chúng ta giữ đúng phạm vi của Phần III — Listing Parser, chưa nhảy sang Buổi 12.

# Phần III — Listing Parser

## Buổi 11 — Pagination Robustness

Mục tiêu hôm nay:

```text
ListingParser
    │
    ├── parse novels
    │
    └── parse next page
             │
             ▼
        next_url
```

Xử lý được:

```text
không có next
next bị thiếu href
relative URL
absolute URL
?page=2
/trang-2
```

Và đặc biệt: **Parser chỉ trả về `next_url`; Parser không tự crawl trang tiếp theo.**

---

# 1. Ôn lại kết quả Buổi 10

Giả sử URL hiện tại:

```text
https://example.com/truyen
```

HTML:

```html
<a class="next" href="/trang-2">
    Trang sau
</a>
```

Parser phải trả:

```python
ListingPage(
    items=[...],
    next_url="https://example.com/trang-2",
)
```

Không phải:

```python
parser.parse_listing()
    ↓
HTTP request trang 2
    ↓
HTTP request trang 3
    ↓
...
```

Đó là nhiệm vụ của Application/Crawler.

---

# 2. Vấn đề của pagination thực tế

Một parser đơn giản:

```python
next_node = document.first("a.next")

href = next_node.attributes.get("href")

return context.resolve_url(href)
```

có thể gặp rất nhiều tình huống.

### Trường hợp A

```html
<a class="next" href="/trang-2">
```

→ hợp lệ.

### Trường hợp B

```html
<a class="next" href="https://example.com/trang-2">
```

→ hợp lệ.

### Trường hợp C

```html
<a class="next" href="?page=2">
```

→ hợp lệ.

### Trường hợp D

```html
<a class="next">
```

→ không có next URL.

### Trường hợp E

```html
<a class="next" href="">
```

→ không có next URL.

### Trường hợp F

Không có:

```html
<a class="next">
```

→ đây là **trang cuối**, không phải parser error.

---

# 3. Phân biệt "không có next" và "parser lỗi"

Đây là nguyên tắc rất quan trọng.

## Không có next

```html
<div class="pagination">
    <a>1</a>
    <a>2</a>
    <a>3</a>
</div>
```

Không có link tiếp theo.

Kết quả:

```python
next_url = None
```

Đây là **valid result**.

---

## Required field bị thiếu

Ví dụ Novel:

```html
<div class="story">
    <!-- thiếu title -->
    <span class="story-author">
        Author A
    </span>
</div>
```

thì:

```python
raise MissingFieldError(...)
```

Đây mới là parser error.

---

# 4. Pagination không phải required field

Do đó:

```text
Novel title   → required
Novel author  → required
Novel URL     → required

Next URL      → optional
```

Đây là lý do chúng ta không dùng:

```python
required_attribute(next_node, ...)
```

cho pagination.

---

# 5. Kiến trúc

Chúng ta đang có:

```text
BaseSiteParser
      │
      └── TruyenFullListingParser
               │
               ├── parse_listing()
               │
               ├── extract_novel()
               │
               └── extract_next_url()
```

Trong Buổi 11, chúng ta làm `extract_next_url()` an toàn hơn.

---

# 6. Case 1 — Không có next

HTML:

```html
<div class="pagination">
    <a href="/trang-1">1</a>
    <a href="/trang-2">2</a>
</div>
```

Code:

```python
next_node = context.document.first(self.NEXT_SELECTOR)

if next_node is None:
    return None
```

Kết quả:

```python
None
```

Đây là logic đúng.

---

# 7. Case 2 — Có next nhưng thiếu href

HTML:

```html
<a class="next">
    Trang sau
</a>
```

Nếu chúng ta làm:

```python
href = next_node.attributes["href"]
```

sẽ có thể phát sinh:

```text
KeyError
```

Không nên.

Dùng helper:

```python
href = get_attribute(
    next_node,
    "href",
)
```

Helper đã học:

```python
def get_attribute(
    node,
    attribute: str,
) -> str | None:

    if node is None:
        return None

    value = node.attributes.get(attribute)

    if value is None:
        return None

    value = value.strip()

    return value or None
```

Kết quả:

```python
None
```

---

# 8. Case 3 — Relative URL

HTML:

```html
<a class="next" href="trang-2">
```

URL hiện tại:

```text
https://example.com/truyen/
```

Không được tự làm:

```python
current_url + href
```

Sai trong nhiều trường hợp.

Phải dùng:

```python
context.resolve_url(href)
```

→

```text
https://example.com/truyen/trang-2
```

---

# 9. Case 4 — Root-relative URL

HTML:

```html
<a class="next" href="/trang-2">
```

Current URL:

```text
https://example.com/truyen/
```

Kết quả:

```text
https://example.com/trang-2
```

`UrlResolver` đã xử lý việc này:

```python
from urllib.parse import urljoin


class UrlResolver:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def resolve(self, url: str) -> str:
        return urljoin(
            self._base_url,
            url,
        )
```

---

# 10. Case 5 — Absolute URL

HTML:

```html
<a
    class="next"
    href="https://example.com/trang-2"
>
    Trang sau
</a>
```

Ta vẫn:

```python
context.resolve_url(href)
```

Kết quả:

```text
https://example.com/trang-2
```

Điểm hay của `urljoin()` là parser không cần:

```python
if href.startswith("http"):
    ...
elif href.startswith("/"):
    ...
else:
    ...
```

---

# 11. Case 6 — Query URL

HTML:

```html
<a class="next" href="?page=2">
    Trang sau
</a>
```

Current:

```text
https://example.com/truyen?page=1
```

Resolver:

```python
context.resolve_url("?page=2")
```

→

```text
https://example.com/truyen?page=2
```

Đây là một trong những lý do `urljoin()` rất hữu ích.

---

# 12. Case 7 — Empty href

HTML:

```html
<a class="next" href="">
    Trang sau
</a>
```

Helper:

```python
get_attribute(...)
```

sẽ trả:

```python
None
```

vì:

```python
value = value.strip()

return value or None
```

Do đó:

```python
if href is None:
    return None
```

---

# 13. Case 8 — `href="#"`

HTML:

```html
<a class="next" href="#">
    Trang sau
</a>
```

Đây thường không phải URL trang tiếp theo.

Ta xử lý:

```python
if href == "#":
    return None
```

---

# 14. Case 9 — `javascript:`

Một số website có:

```html
<a
    class="next"
    href="javascript:void(0)"
>
    Next
</a>
```

Đây không phải URL mà HTTPX có thể fetch.

Ta không nên đưa nó vào:

```text
Fetcher
```

Có thể xử lý:

```python
if href.lower().startswith("javascript:"):
    return None
```

---

# 15. Hàm `extract_next_url()` hoàn chỉnh

Bây giờ ta có:

```python
def extract_next_url(
    self,
    context,
) -> str | None:

    next_node = context.document.first(self.NEXT_SELECTOR)

    # Không có next
    if next_node is None:
        return None

    # Lấy href an toàn
    href = get_attribute(
        next_node,
        "href",
    )

    # Không có href
    if href is None:
        return None

    # Không phải URL thật
    if href == "#":
        return None

    if href.lower().startswith("javascript:"):
        return None

    # Resolve relative → absolute
    return context.resolve_url(href)
```

Đây là core của Buổi 11.

---

# 16. Nhưng còn `disabled`?

Ví dụ:

```html
<a
    class="next disabled"
    href="/trang-99"
>
    Next
</a>
```

Không nên lấy `/trang-99`.

Ta thêm:

```python
def is_next_disabled(
    self,
    node,
) -> bool:

    classes = node.attributes.get(
        "class",
        "",
    )

    return "disabled" in classes.split()
```

Sau đó:

```python
if self.is_next_disabled(next_node):
    return None
```

---

# 17. Full parser

```python
from crawler.domain.novel import NovelSummary
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from crawler.infrastructure.parser.required import (
    required_text,
    required_attribute,
)


class TruyenFullListingParser(BaseSiteParser):
    STORY_SELECTOR = ".story"

    TITLE_SELECTOR = ".story-title a"

    AUTHOR_SELECTOR = ".story-author"

    NEXT_SELECTOR = "a.next"

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        context = self.create_context(
            page_source,
            url,
        )

        stories = context.document.all(self.STORY_SELECTOR)

        items: list[NovelSummary] = []

        for story in stories:
            novel = self.extract_novel(
                story,
                context,
            )

            items.append(novel)

        next_url = self.extract_next_url(context)

        return ListingPage(
            items=items,
            next_url=next_url,
        )

    def extract_novel(
        self,
        story,
        context,
    ) -> NovelSummary:

        title_node = story.css_first(self.TITLE_SELECTOR)

        author_node = story.css_first(self.AUTHOR_SELECTOR)

        title = required_text(
            title_node,
            field="title",
            selector=self.TITLE_SELECTOR,
        )

        author = required_text(
            author_node,
            field="author",
            selector=self.AUTHOR_SELECTOR,
        )

        href = required_attribute(
            title_node,
            attribute="href",
            field="url",
            selector=self.TITLE_SELECTOR,
        )

        novel_url = context.resolve_url(href)

        return NovelSummary(
            title=title,
            author=author,
            url=novel_url,
        )

    def extract_next_url(
        self,
        context,
    ) -> str | None:

        next_node = context.document.first(self.NEXT_SELECTOR)

        if next_node is None:
            return None

        if self.is_next_disabled(next_node):
            return None

        href = get_attribute(
            next_node,
            "href",
        )

        if href is None:
            return None

        if href == "#":
            return None

        if href.lower().startswith("javascript:"):
            return None

        return context.resolve_url(href)

    def is_next_disabled(
        self,
        node,
    ) -> bool:

        classes = node.attributes.get(
            "class",
            "",
        )

        return "disabled" in classes.split()
```

---

# 18. Test toàn bộ pagination

Tạo:

```text
tests/
└── infrastructure/
    └── parser/
        └── test_listing.py
```

## Test 1 — Có next

```python
def test_parse_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a class="next"
       href="/trang-2">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert result.next_url == "https://example.com/trang-2"
```

---

# 19. Test 2 — Không có next

```python
def test_no_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert result.next_url is None
```

Đây là test rất quan trọng.

**Không có pagination không phải lỗi.**

---

# 20. Test 3 — Thiếu href

```python
def test_next_without_href():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a class="next">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert result.next_url is None
```

---

# 21. Test 4 — Query URL

```python
def test_query_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a class="next"
       href="?page=2">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen?page=1",
    )

    assert result.next_url == "https://example.com/truyen?page=2"
```

---

# 22. Test 5 — Absolute URL

```python
def test_absolute_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a
        class="next"
        href="https://example.com/trang-2"
    >
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert result.next_url == "https://example.com/trang-2"
```

---

# 23. Test 6 — `#`

```python
def test_hash_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a class="next"
       href="#">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert result.next_url is None
```

---

# 24. Test 7 — disabled

```python
def test_disabled_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a
        class="next disabled"
        href="/trang-99"
    >
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/trang-10",
    )

    assert result.next_url is None
```

---

# 25. Một vấn đề rất quan trọng: `next` sai

Giả sử:

```html
<div class="pagination">

    <a href="/trang-1">1</a>

    <a href="/trang-2">2</a>

    <a class="next"
       href="/trang-2">
        Next
    </a>

</div>
```

Không vấn đề.

Nhưng:

```html
<a class="next"
   href="/trang-1">
    Next
</a>
```

Parser sẽ trả:

```text
/trang-1
```

Có phải parser sai không?

**Không nhất thiết.**

HTML nói rằng link `next` là `/trang-1`.

Parser không biết crawler đã crawl `/trang-1`.

---

# 26. Ai xử lý vòng lặp?

Application.

Ví dụ:

```python
visited_urls: set[str] = set()

current_url = start_url

while current_url:
    if current_url in visited_urls:
        break

    visited_urls.add(current_url)

    response = fetcher.fetch(current_url)

    page = parser.parse_listing(
        response.text,
        current_url,
    )

    for novel in page.items:
        repository.save(novel)

    current_url = page.next_url
```

Đây là boundary rất đẹp:

```text
Parser
    ↓
"Next URL là X"

Application
    ↓
"X có được phép crawl tiếp không?"
```

---

# 27. Không nên đưa `visited_urls` vào `ListingPage`

Không làm:

```python
@dataclass
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
    visited_urls: set[str]
```

Vì `visited_urls` không phải dữ liệu của HTML.

Nó là **state của crawl session**.

---

# 28. Không nên cho Parser tự kiểm tra database

Không làm:

```python
if repository.exists(next_url):
    ...
```

Parser không biết Repository.

Nếu làm vậy:

```text
Parser
 ↓
Repository
 ↓
Database
```

Parser đã phụ thuộc infrastructure persistence.

DDD/SOLID bị phá vỡ.

---

# 29. Vậy Buổi 11 thực sự đạt được gì?

Chúng ta biến pagination từ:

```python
next_node
    ↓
href
    ↓
urljoin
```

thành:

```text
                 ┌── no node ────────→ None
                 │
next node ───────┼── disabled ───────→ None
                 │
                 ├── no href ────────→ None
                 │
                 ├── # ─────────────→ None
                 │
                 ├── javascript ────→ None
                 │
                 └── valid href
                         ↓
                    resolve URL
                         ↓
                      next_url
```

Đây chính là **Pagination Robustness**.

---

# 30. Kiến trúc sau Buổi 11

```text
                 HTTPX Fetcher
                       │
                       │ page_source
                       ▼
             TruyenFullListingParser
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        NovelSummary[]       next_url
              │                 │
              └────────┬────────┘
                       ▼
                  ListingPage
                       │
                       ▼
                Application
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
         Repository       crawl next page
                                │
                                ▼
                           HTTPX Fetcher
```

---

## Checklist Buổi 11

Sau bài này bạn cần nắm chắc:

* [x] Không có `next` → `next_url=None`
* [x] `next` thiếu `href` → `next_url=None`
* [x] `href=""` → `next_url=None`
* [x] `href="#"` → `next_url=None`
* [x] `javascript:` → không phải URL crawl
* [x] relative URL → `UrlResolver`
* [x] `/trang-2` → `UrlResolver`
* [x] `?page=2` → `UrlResolver`
* [x] absolute URL → giữ đúng URL
* [x] disabled pagination → `None`
* [x] Parser không crawl page tiếp theo
* [x] Parser không quản lý `visited_urls`
* [x] Parser không truy cập Repository
* [x] Application chịu trách nhiệm crawl loop

### Buổi 12 — Listing Parser hoàn chỉnh

Chúng ta sẽ **không thêm abstraction mới một cách tùy tiện**, mà gom những gì đã học thành một `ListingParser` hoàn chỉnh:

```text
parse_listing()
      │
      ├── create_context()
      │
      ├── parse_novels()
      │       └── NovelCardExtractor
      │
      └── parse_next_page()
              │
              └── next_url
```

Đồng thời sẽ thiết kế lại code để API của parser rõ ràng hơn:

```python
result = parser.parse_listing(
    page_source,
    current_url,
)

result.items
result.next_url
```

Sau Buổi 12, **Phần III — Listing Parser** sẽ hoàn tất và chúng ta có thể chuyển sang **Phần IV — Novel Parser**, bắt đầu với `parse_novel()`: `title`, `author`, `url`, `cover`, `description`, `status` và chapter listing.
