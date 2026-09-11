# Buổi 10 — Pagination Robustness

Ở Buổi 9, chúng ta đã làm được:

```text
parse_listing()
    │
    ├── extract_novel()
    │
    └── extract_next_url()
                │
                ▼
           ListingPage
           ├── items
           └── next_url
```

Nhưng website thực tế thường không đơn giản như:

```html
<a class="next" href="/truyen?page=2">Next</a>
```

Hôm nay chúng ta làm cho pagination **robust hơn**, nhưng vẫn giữ đúng DDD + SOLID.

---

# 1. Các trường hợp thực tế

Pagination có thể là:

### Dạng 1 — class `next`

```html
<a class="next" href="/truyen?page=2">
    Next
</a>
```

### Dạng 2 — `rel="next"`

```html
<a rel="next" href="/truyen?page=2">
    Next
</a>
```

### Dạng 3 — `.next a`

```html
<li class="next">
    <a href="/truyen?page=2">
        Next
    </a>
</li>
```

### Dạng 4 — trang cuối

```html
<li class="next disabled">
    <a href="#">
        Next
    </a>
</li>
```

### Dạng 5 — URL tương đối

```html
<a class="next" href="trang-2">
```

### Dạng 6 — URL tuyệt đối

```html
<a class="next"
   href="https://example.com/truyen?page=2">
```

Parser phải xử lý được nhưng **không được biến thành một đống logic hỗn loạn**.

---

# 2. Nguyên tắc thiết kế

Có một nguyên tắc quan trọng:

> **Pagination strategy thuộc site parser, không thuộc BaseSiteParser.**

Không nên sửa `BaseSiteParser` mỗi khi gặp website mới.

Ta có:

```text
BaseSiteParser
      ↑
      │
TruyenFullListingParser
TruyenYYListingParser
TruyenCVListingParser
```

Mỗi parser biết HTML của website mình.

---

# 3. Trước tiên: xử lý `disabled`

Giả sử:

```html
<a class="next disabled"
   href="/truyen?page=999">
    Next
</a>
```

Nếu code hiện tại:

```python
next_node = document.first("a.next")
```

thì rất nguy hiểm.

Nó có thể trả:

```text
/truyen?page=999
```

trong khi đây thực tế là trang cuối.

---

# 4. CSS selector có thể xử lý `disabled`

Nếu HTML của site dùng class:

```text
next disabled
```

ta có thể:

```css
a.next:not(.disabled)
```

Tức là:

```python
NEXT_SELECTOR = "a.next:not(.disabled)"
```

Khi đó:

```html
<a class="next disabled">
```

sẽ không match.

---

# 5. Nhưng đừng nghĩ `:not(.disabled)` là universal

Một website có thể dùng:

```html
<li class="next disabled">
```

hoặc:

```html
<a class="next" aria-disabled="true">
```

hoặc:

```html
<a class="next is-disabled">
```

hoặc:

```html
<a class="next" href="#">
```

Do đó không có một selector universal hoàn hảo.

Site parser phải hiểu website cụ thể.

---

# 6. Tách `is_disabled()`

Ta có thể tạo helper nhỏ:

```python
def is_disabled(node) -> bool:
    if node is None:
        return True

    classes = node.attributes.get("class", "")

    class_set = set(
        classes.split()
    )

    return "disabled" in class_set
```

Ví dụ:

```python
if is_disabled(next_node):
    return None
```

Nhưng có một vấn đề.

Nếu `disabled` là:

```html
<a aria-disabled="true">
```

thì helper này không biết.

Vì vậy ta có thể mở rộng **trong site parser**:

```python
def is_next_disabled(self, node) -> bool:
    ...
```

Đây lại là site-specific logic.

---

# 7. Thiết kế tốt hơn

Trong `TruyenFullListingParser`:

```python
NEXT_SELECTOR = "a.next"
```

và:

```python
def is_next_disabled(self, node) -> bool:

    classes = node.attributes.get(
        "class",
        "",
    )

    return "disabled" in classes.split()
```

Sau đó:

```python
def extract_next_url(self, context):

    next_node = context.document.first(
        self.NEXT_SELECTOR
    )

    if next_node is None:
        return None

    if self.is_next_disabled(next_node):
        return None

    ...
```

---

# 8. Full `extract_next_url()`

```python
def extract_next_url(
    self,
    context,
) -> str | None:

    next_node = context.document.first(
        self.NEXT_SELECTOR
    )

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

    return context.resolve_url(
        href,
    )
```

và:

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

---

# 9. Tại sao không đưa `is_disabled()` vào Domain?

Vì:

```text
disabled
class
HTML
attribute
```

đều là presentation/HTML concern.

Domain không cần biết:

```python
class="next disabled"
```

Domain chỉ nhận:

```python
next_url=None
```

Đây là một ví dụ rất rõ của:

```text
Infrastructure
      ↓
Domain
```

---

# 10. Dạng `rel="next"`

Một website có thể không dùng:

```css
a.next
```

mà:

```html
<a rel="next"
   href="/truyen?page=2">
    Next
</a>
```

Parser của website đó có thể:

```python
NEXT_SELECTOR = "a[rel='next']"
```

Đây là CSS attribute selector.

---

# 11. Dạng `.next a`

Nếu HTML:

```html
<li class="next">
    <a href="/truyen?page=2">
        Next
    </a>
</li>
```

thì:

```python
NEXT_SELECTOR = ".next a"
```

Parser không cần biết `li`.

---

# 12. Không nên dùng nhiều selector ngay từ đầu

Có thể bạn sẽ nghĩ:

```python
NEXT_SELECTORS = [
    "a.next",
    "a[rel='next']",
    ".next a",
    ".pagination-next",
]
```

rồi:

```python
for selector in NEXT_SELECTORS:
    ...
```

Cách này có vẻ robust nhưng thực tế có thể gây lỗi.

Ví dụ HTML:

```html
<a class="next disabled"
   href="/page/999">
```

và:

```html
<a rel="next"
   href="/page/2">
```

Selector đầu tiên match nhầm.

Hoặc một trang có:

```html
<a class="next">Related novels</a>
```

Bạn có thể lấy sai link.

**Robust không có nghĩa là càng nhiều fallback càng tốt.**

Robust nghĩa là:

> Hiểu chính xác HTML contract của từng website.

---

# 13. URL `#`

Một trường hợp phổ biến:

```html
<a class="next"
   href="#">
    Next
</a>
```

Nếu:

```python
context.resolve_url("#")
```

thì có thể nhận:

```text
https://example.com/truyen#
```

Đây không phải trang tiếp theo.

Ta cần loại bỏ.

---

# 14. Kiểm tra URL fragment

Có thể viết:

```python
def is_usable_url(url: str) -> bool:
    return url not in {"#", ""}
```

Nhưng tốt hơn là xử lý trong site parser:

```python
href = get_attribute(
    next_node,
    "href",
)

if href is None:
    return None

if href == "#":
    return None
```

Đừng xây một URL validation framework khổng lồ chỉ cho trường hợp này.

---

# 15. URL `javascript:void(0)`

Website có thể:

```html
<a class="next"
   href="javascript:void(0)">
```

Đây không phải URL HTTP.

Có thể kiểm tra:

```python
if href.startswith("javascript:"):
    return None
```

Nhưng nếu website thực sự sử dụng JavaScript để tải page tiếp theo thì parser HTML đơn thuần **không thể tự suy ra URL thật**.

Đó là giới hạn của parser.

Không được giả vờ rằng:

```text
javascript:void(0)
```

có thể biến thành:

```text
?page=2
```

nếu HTML không cung cấp thông tin đó.

---

# 16. Kiểm tra URL scheme

Ở giai đoạn này, ta có thể thêm một helper infrastructure:

```python
from urllib.parse import urlparse


def is_http_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.scheme in {
        "http",
        "https",
    }
```

Nhưng với relative URL:

```text
/page/2
```

thì:

```python
urlparse("/page/2").scheme
```

là rỗng.

Vì vậy phải resolve trước:

```text
relative URL
     ↓
resolve
     ↓
absolute URL
     ↓
validate
```

---

# 17. Một `UrlResolver` tốt hơn

Hiện tại:

```python
class UrlResolver:

    def resolve(self, url):
        return urljoin(
            self._base_url,
            url,
        )
```

Ta có thể giữ nó đơn giản.

Không nên biến thành:

```text
UrlResolver
 ├── validate
 ├── normalize
 ├── canonicalize
 ├── remove tracking
 ├── remove fragment
 ├── decode
 ├── redirect
 ├── HTTP request
 └── ...
```

Đó là overengineering.

---

# 18. Pagination với query string

Ví dụ:

```html
<a class="next"
   href="?page=2">
```

Current URL:

```text
https://example.com/truyen?page=1
```

`urljoin()` sẽ xử lý thành:

```text
https://example.com/truyen?page=2
```

Đây là lý do chúng ta **không tự nối string**.

---

# 19. Pagination dạng `/trang-2`

Current:

```text
https://example.com/truyen
```

HTML:

```html
<a class="next"
   href="/truyen/trang-2">
```

Resolver:

```python
context.resolve_url(
    "/truyen/trang-2"
)
```

→

```text
https://example.com/truyen/trang-2
```

---

# 20. Pagination dạng relative

Current:

```text
https://example.com/truyen/
```

HTML:

```html
<a class="next"
   href="trang-2">
```

→

```text
https://example.com/truyen/trang-2
```

---

# 21. Pagination dạng absolute

```html
<a class="next"
   href="https://example.com/truyen?page=2">
```

→ giữ nguyên.

Do đó tất cả đều đi qua:

```python
context.resolve_url()
```

---

# 22. Chống pagination loop

Đây là phần **Application**, không phải Parser.

Giả sử:

```text
page 1
 ↓
page 2
 ↓
page 2
```

Parser hoàn toàn có thể trả:

```python
next_url = "https://example.com/truyen?page=2"
```

Parser không biết application đã crawl URL đó chưa.

Application phải giữ:

```python
visited_urls: set[str]
```

Ví dụ hoàn chỉnh:

```python
def crawl_listing(
    start_url,
    fetcher,
    parser,
    repository,
):

    visited_urls: set[str] = set()

    current_url = start_url

    while current_url:

        if current_url in visited_urls:
            break

        visited_urls.add(
            current_url
        )

        response = fetcher.fetch(
            current_url
        )

        page = parser.parse_listing(
            response.text,
            current_url,
        )

        for novel in page.items:
            repository.save(novel)

        current_url = page.next_url
```

---

# 23. Tại sao `visited_urls` không nằm trong Parser?

Nếu đưa vào Parser:

```python
parser.visited_urls
```

thì Parser bắt đầu giữ crawler state.

Ví dụ:

```text
Parser
 ├── HTML parsing
 ├── pagination
 ├── visited state
 ├── crawl session
 └── crawl policy
```

SRP bị phá vỡ.

Parser nên gần như stateless:

```text
(page_source, url)
       ↓
     result
```

---

# 24. Pagination cycle

Ví dụ website bị lỗi:

```text
page=1 → page=2
page=2 → page=3
page=3 → page=2
```

Application:

```python
visited_urls = {
    page1,
    page2,
    page3,
}
```

Khi nhận:

```text
page2
```

lần nữa:

```python
if current_url in visited_urls:
    break
```

Crawler dừng.

Đây là một ví dụ rất hay về:

> **Parser phát hiện dữ liệu; Application áp dụng policy.**

---

# 25. Pagination duplicate

Một website có thể trả:

```text
page 1
Novel A
Novel B

page 2
Novel B
Novel C
```

Parser không nhất thiết phải loại `Novel B`.

Tại sao?

Parser chỉ biết:

```text
HTML page 2 chứa Novel B
```

Còn quyết định:

```text
Novel B đã tồn tại chưa?
có update không?
ignore không?
upsert không?
```

là Repository/Application concern.

Đây là một điểm DDD rất quan trọng.

---

# 26. Test disabled

```python
def test_disabled_next():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/1">
                Book 1
            </a>
        </h3>

        <span class="story-author">
            Author 1
        </span>

    </div>

    <a class="next disabled"
       href="/truyen?page=999">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen?page=10",
    )

    assert result.next_url is None
```

---

# 27. Test `#`

```python
def test_hash_next():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/1">
                Book 1
            </a>
        </h3>

        <span class="story-author">
            Author 1
        </span>

    </div>

    <a class="next" href="#">
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

# 28. Test query pagination

```python
def test_query_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/1">
                Book 1
            </a>
        </h3>

        <span class="story-author">
            Author
        </span>

    </div>

    <a class="next" href="?page=2">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen?page=1",
    )

    assert (
        result.next_url
        == "https://example.com/truyen?page=2"
    )
```

---

# 29. Test absolute URL

```python
def test_absolute_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/book/1">
                Book 1
            </a>
        </h3>

        <span class="story-author">
            Author
        </span>

    </div>

    <a
        class="next"
        href="https://example.com/truyen?page=2"
    >
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert (
        result.next_url
        == "https://example.com/truyen?page=2"
    )
```

---

# 30. Một phiên bản parser hoàn chỉnh hơn

Đến cuối Buổi 10, `listing.py` có thể là:

```python
from crawler.domain.novel import NovelSummary
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import BaseSiteParser
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

        stories = context.document.all(
            self.STORY_SELECTOR
        )

        items: list[NovelSummary] = []

        for story in stories:

            novel = self.extract_novel(
                story,
                context,
            )

            items.append(novel)

        next_url = self.extract_next_url(
            context
        )

        return ListingPage(
            items=items,
            next_url=next_url,
        )

    def extract_novel(
        self,
        story,
        context,
    ) -> NovelSummary:

        title_node = story.css_first(
            self.TITLE_SELECTOR
        )

        author_node = story.css_first(
            self.AUTHOR_SELECTOR
        )

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

        novel_url = context.resolve_url(
            href
        )

        return NovelSummary(
            title=title,
            author=author,
            url=novel_url,
        )

    def extract_next_url(
        self,
        context,
    ) -> str | None:

        next_node = context.document.first(
            self.NEXT_SELECTOR
        )

        if next_node is None:
            return None

        if self.is_next_disabled(
            next_node
        ):
            return None

        href = get_attribute(
            next_node,
            "href",
        )

        if href is None:
            return None

        if href == "#":
            return None

        if href.startswith(
            "javascript:"
        ):
            return None

        return context.resolve_url(
            href
        )

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

# 31. Có một điểm cần cải thiện

Bạn có thể thấy:

```python
if href == "#":
    return None

if href.startswith("javascript:"):
    return None
```

đây là logic có tính chất **site/presentation-specific**.

Không nên vội đưa tất cả vào:

```text
UrlResolver
```

vì `UrlResolver` có nhiệm vụ:

```text
relative URL → absolute URL
```

không phải:

```text
"URL này có phải pagination hợp lệ không?"
```

Hai trách nhiệm khác nhau.

---

# 32. Phân chia trách nhiệm sau Buổi 10

```text
SelectolaxDocument
    ↓
HTML → Node

Parser Helper
    ↓
Node → text/attribute

UrlResolver
    ↓
relative URL → absolute URL

TruyenFullListingParser
    ↓
HTML semantics của TruyenFull

Application
    ↓
crawl policy
    ├── loop prevention
    ├── visited URLs
    ├── retry
    ├── max pages
    └── persistence
```

Đây là kiến trúc rất quan trọng cho project crawler của bạn.

---

# 33. Những thứ Parser KHÔNG làm

Parser không:

```text
❌ HTTP request
❌ retry
❌ proxy
❌ User-Agent
❌ database
❌ queue
❌ Redis
❌ visited URL
❌ crawl all pages
❌ concurrency
```

Parser chỉ:

```text
HTML
 ↓
DOM
 ↓
Domain Result
```

---

# 34. Những thứ Application làm

Application:

```text
start_url
    ↓
Fetcher
    ↓
page_source
    ↓
Parser
    ↓
ListingPage
    ↓
Repository
    ↓
next_url
    ↓
Fetcher
```

Và Application quyết định:

```text
├── crawl bao nhiêu trang
├── retry hay skip
├── duplicate xử lý thế nào
├── URL đã visited chưa
├── pause/resume
└── persist thế nào
```

Đây chính là nền tảng để sau này ghép parser vào **crawler framework** lớn của bạn.

---

# 35. Bài tập Buổi 10

### Bài 1

Thử các HTML:

```text
a.next
a[rel="next"]
.next a
```

và tạo parser tương ứng.

### Bài 2

Test:

```html
<a class="next disabled">
```

phải:

```python
next_url is None
```

### Bài 3

Test:

```html
<a class="next" href="#">
```

phải:

```python
next_url is None
```

### Bài 4

Test:

```html
<a class="next"
   href="?page=2">
```

với:

```text
https://example.com/truyen?page=1
```

phải ra:

```text
https://example.com/truyen?page=2
```

### Bài 5 — quan trọng nhất

Viết `CrawlListingUseCase` có:

```python
visited_urls: set[str]
```

để xử lý:

```text
page 1
  ↓
page 2
  ↓
page 3
  ↓
page 2
```

và không bị loop vô hạn.

---

# Roadmap

Đến đây:

```text
01 Architecture                    ✅
02 Selectolax Foundation           ✅
03 Parser Interface                ✅
04 ParseResult + Validation        ✅
05 Domain Model                    ✅
06 BaseSiteParser + URL Resolver   ✅
07 Listing Models + Helpers        ✅
08 Extract Novel Cards             ✅
09 Listing Pagination              ✅
10 Pagination Robustness           ✅
```

## Buổi 11 — Pagination State & Crawl Safety

Buổi 11 chúng ta sẽ đi sâu hơn vào phần **pagination thực chiến**, đặc biệt:

```text
page 1
  ↓
page 2
  ↓
page 3
```

và các vấn đề:

* duplicate URL
* pagination cycle
* canonical URL
* fragment `#`
* query normalization
* URL identity
* max page
* max items
* empty page
* page không có novel
* parser trả `next_url` nhưng crawler có nên đi tiếp hay không

Đây sẽ là buổi nối rất quan trọng giữa **Parser** và **Crawler Application**, nhưng vẫn giữ ranh giới DDD/SOLID.
