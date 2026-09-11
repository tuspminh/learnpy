# Buổi 9 — Listing Pagination

Hôm nay chúng ta hoàn thiện phần **pagination của `parse-listing`**.

Mục tiêu:

```text
HTML listing
     │
     ├── NovelSummary
     ├── NovelSummary
     ├── NovelSummary
     │
     └── Pagination
            │
            ▼
         next_url
```

Điểm quan trọng nhất:

> **Parser chỉ phát hiện `next_url`. Parser không tự fetch trang tiếp theo.**

---

# 1. Nhắc lại kiến trúc

Hiện tại:

```text
HTTPX
  │
  │ page_source
  ▼
ListingParser
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

Sau đó Application mới làm:

```text
ListingPage
    │
    └── next_url
          │
          ▼
        HTTPX
          │
          ▼
      page_source
          │
          ▼
      ListingParser
```

---

# 2. Tại sao không để Parser tự crawl pagination?

Ví dụ **không được** làm:

```python
def parse_listing(page_source, url):

    ...

    next_url = ...

    response = httpx.get(next_url)

    ...
```

Nếu làm vậy Parser sẽ phụ thuộc vào HTTPX.

Khi đó:

```text
Parser
 ├── Selectolax
 ├── HTTPX
 ├── timeout
 ├── retry
 ├── proxy
 └── pagination
```

Parser đã trở thành crawler.

Sai trách nhiệm.

Thiết kế của chúng ta:

```text
HTTPX Client
    ↓
page_source
    ↓
Parser
    ↓
ListingPage
    ↓
Application
    ↓
HTTPX Client
```

---

# 3. Pagination Model

Hiện tại chúng ta dùng:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Ví dụ trang cuối:

```python
ListingPage(
    items=[...],
    next_url=None,
)
```

Trang còn tiếp:

```python
ListingPage(
    items=[...],
    next_url="https://example.com/truyen?page=2",
)
```

Đây là đủ cho giai đoạn hiện tại.

---

# 4. HTML Pagination đơn giản nhất

Ví dụ:

```html
<ul class="pagination">

    <li>
        <a href="/truyen?page=1">
            1
        </a>
    </li>

    <li>
        <a href="/truyen?page=2">
            2
        </a>
    </li>

    <li>
        <a href="/truyen?page=3">
            3
        </a>
    </li>

    <li>
        <a class="next" href="/truyen?page=2">
            Next
        </a>
    </li>

</ul>
```

Ta chỉ quan tâm:

```css
a.next
```

và lấy:

```text
href
```

---

# 5. Thêm selector

Trong:

```python
TruyenFullListingParser
```

thêm:

```python
NEXT_SELECTOR = "a.next"
```

---

# 6. Tạo `extract_next_url()`

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

    href = get_attribute(
        next_node,
        "href",
    )

    if href is None:
        return None

    return context.resolve_url(
        href
    )
```

Ở đây `next_url` là **optional**.

Không có `a.next`:

```text
None
```

Không có `href`:

```text
None
```

Điều này khác với `title`, `author`, `url`.

---

# 7. Vì sao pagination không dùng `required_attribute()`?

Novel:

```text
title → REQUIRED
author → REQUIRED
url → REQUIRED
```

Pagination:

```text
next_url → OPTIONAL
```

Trang cuối có thể hoàn toàn không có:

```html
<a class="next">
```

Do đó:

```python
get_attribute()
```

là đúng.

Không dùng:

```python
required_attribute()
```

Nếu dùng required:

```python
required_attribute(
    next_node,
    ...
)
```

thì trang cuối sẽ bị coi là lỗi.

Trong khi trang cuối là **trạng thái hợp lệ**.

---

# 8. Refactor `parse_listing()`

Bây giờ:

```python
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
```

Bây giờ cấu trúc cực kỳ rõ:

```text
parse_listing()
│
├── create_context()
│
├── extract novels
│
├── extract next URL
│
└── ListingPage
```

---

# 9. Full code `listing.py`

Để bạn có thể copy và chạy ngay:

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

        href = get_attribute(
            next_node,
            "href",
        )

        if href is None:
            return None

        return context.resolve_url(
            href
        )
```

---

# 10. Test Pagination

HTML:

```python
HTML = """
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

<div class="story">
    <h3 class="story-title">
        <a href="/book/2">
            Book 2
        </a>
    </h3>

    <span class="story-author">
        Author 2
    </span>
</div>

<ul class="pagination">

    <li>
        <a href="/truyen?page=1">
            1
        </a>
    </li>

    <li>
        <a href="/truyen?page=2">
            2
        </a>
    </li>

    <li>
        <a class="next"
           href="/truyen?page=2">
            Next
        </a>
    </li>

</ul>
"""
```

Test:

```python
def test_parse_next_url():

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        HTML,
        "https://example.com/truyen",
    )

    assert (
        result.next_url
        == "https://example.com/truyen?page=2"
    )
```

---

# 11. Test trang cuối

HTML không có next:

```python
HTML_LAST_PAGE = """
<div class="story">

    <h3 class="story-title">
        <a href="/book/10">
            Book 10
        </a>
    </h3>

    <span class="story-author">
        Author 10
    </span>

</div>

<ul class="pagination">

    <li>
        <a href="/truyen?page=1">
            1
        </a>
    </li>

    <li>
        <a href="/truyen?page=2">
            2
        </a>
    </li>

</ul>
"""
```

Test:

```python
def test_last_page():

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        HTML_LAST_PAGE,
        "https://example.com/truyen?page=2",
    )

    assert result.next_url is None
```

Đây là test rất quan trọng.

```text
next_url is None
```

không phải parser failure.

Nó có nghĩa:

> Đây là trang cuối.

---

# 12. Test relative pagination URL

Ví dụ:

```html
<a class="next"
   href="trang-2">
    Next
</a>
```

Current URL:

```text
https://example.com/truyen/
```

Kết quả:

```text
https://example.com/truyen/trang-2
```

Test:

```python
def test_relative_next_url():

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

    <a class="next" href="trang-2">
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen/",
    )

    assert (
        result.next_url
        == "https://example.com/truyen/trang-2"
    )
```

---

# 13. `urljoin()` giúp chúng ta xử lý nhiều kiểu URL

Ví dụ:

```text
current:
https://example.com/truyen/
```

### Root-relative

```text
/book/1
```

→

```text
https://example.com/book/1
```

### Relative

```text
trang-2
```

→

```text
https://example.com/truyen/trang-2
```

### Absolute

```text
https://example.com/truyen?page=2
```

→ giữ nguyên.

Đây là lý do chúng ta tạo:

```python
UrlResolver
```

thay vì tự nối chuỗi.

---

# 14. Nhưng pagination thực tế phức tạp hơn

Một website có thể dùng:

```html
<a rel="next" href="/truyen?page=2">
    Next
</a>
```

thay vì:

```html
<a class="next">
```

Hoặc:

```html
<li class="next">
    <a href="/truyen?page=2">
```

Hoặc:

```html
<a class="pagination-next"
   href="/truyen?page=2">
```

Chúng ta **không nên viết một helper chung kiểu**:

```python
find_next_link()
```

rồi nhét vào đó hàng chục selector.

Ví dụ không nên:

```python
def find_next_link(document):

    selectors = [
        "a.next",
        "a[rel='next']",
        ".next a",
        ".pagination-next",
        ...
    ]

    ...
```

Tại sao?

Vì đây là **site-specific HTML knowledge**.

---

# 15. Site Parser mới quyết định selector

Ví dụ TruyenFull:

```python
NEXT_SELECTOR = "a.next"
```

Website khác:

```python
NEXT_SELECTOR = "a[rel='next']"
```

Website khác:

```python
NEXT_SELECTOR = ".pagination .next a"
```

Đó chính là lý do chúng ta có:

```text
BaseSiteParser
       ↑
       │
TruyenFullParser
TruyenYYParser
TruyenCVParser
```

Base class không biết HTML của từng website.

---

# 16. Một vấn đề nguy hiểm: `Next` nhưng đang disabled

Ví dụ:

```html
<li class="next disabled">
    <a href="#">
        Next
    </a>
</li>
```

Nếu parser chỉ:

```python
next_node = document.first("a.next")
```

thì có thể không tìm được hoặc có thể lấy một link không hợp lệ, tùy HTML.

Một website khác:

```html
<a class="next disabled"
   href="/truyen?page=999">
    Next
</a>
```

thì parser có thể vô tình crawl page 999.

Do đó parser thực tế phải hiểu **semantics của site**.

Ví dụ:

```python
NEXT_SELECTOR = "a.next:not(.disabled)"
```

nếu HTML của site hỗ trợ class `disabled`.

Đây là **site-specific rule**, không phải universal parser rule.

---

# 17. Pagination và Application

Bây giờ giả sử parser trả:

```python
ListingPage(
    items=[A, B, C],
    next_url="https://example.com/truyen?page=2",
)
```

Application có thể làm:

```python
page_url = start_url

while page_url:

    response = fetcher.fetch(page_url)

    page = parser.parse_listing(
        response.text,
        page_url,
    )

    for novel in page.items:
        repository.save(novel)

    page_url = page.next_url
```

Chú ý:

```text
Parser → không loop
Application → loop pagination
```

---

# 18. Tại sao đây là thiết kế tốt?

Application có thể quyết định:

### Crawl tất cả

```python
while page_url:
    ...
```

### Chỉ crawl 3 trang

```python
for _ in range(3):
    ...
```

### Resume từ trang 20

```text
https://example.com/truyen?page=20
```

### Crawl song song

Có thể sau này application orchestration quyết định chiến lược concurrency.

Parser không cần thay đổi.

Đây chính là **Separation of Concerns**.

---

# 19. Pagination không nên chứa state crawler

Không thêm:

```python
@dataclass
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
    current_page: int
    total_pages: int
    visited_pages: set[str]
    retry_count: int
```

vào parser result chỉ vì crawler cần chúng.

`ListingPage` nên biểu diễn:

> **Kết quả parse của một HTML listing page.**

Còn:

```text
visited
retry
crawl depth
queue
worker
```

là Application/Crawler concern.

---

# 20. Một vấn đề rất quan trọng: vòng lặp pagination

Website lỗi có thể trả:

```text
page 1
next → page 2

page 2
next → page 2
```

Nếu Application chỉ:

```python
while page.next_url:
```

sẽ loop vô hạn.

Nhưng **đây không phải trách nhiệm của Parser**.

Crawler/Application có thể giữ:

```python
visited_urls: set[str] = set()
```

Ví dụ:

```python
visited_urls = set()

page_url = start_url

while page_url:

    if page_url in visited_urls:
        break

    visited_urls.add(page_url)

    response = fetcher.fetch(page_url)

    page = parser.parse_listing(
        response.text,
        page_url,
    )

    page_url = page.next_url
```

Parser chỉ nói:

```text
"Trang tiếp theo là URL này."
```

Application quyết định:

```text
"Có nên fetch nó hay không?"
```

Đây là ranh giới cực kỳ quan trọng.

---

# 21. Test lỗi pagination

Nếu:

```html
<a class="next">
    Next
</a>
```

không có `href`.

Ta muốn:

```python
result.next_url is None
```

Test:

```python
def test_next_without_href():

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

# 22. Phân loại lỗi

Sau Buổi 9 ta có cách phân loại rất rõ:

### Novel card thiếu title

```text
ParserError
```

vì:

```text
title = required
```

### Novel card thiếu author

```text
ParserError
```

### Novel card thiếu href

```text
ParserError
```

### Pagination không tồn tại

```text
Không lỗi
next_url = None
```

### Pagination tồn tại nhưng không có href

```text
Không lỗi
next_url = None
```

### Pagination URL tương đối

```text
resolve URL
```

---

# 23. Toàn bộ Listing Parser hiện tại

Chúng ta đã đạt:

```text
                 parse_listing()
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   extract_novel()          extract_next_url()
          │                         │
          ▼                         ▼
   NovelSummary                next_url
          │                         │
          └────────────┬────────────┘
                       ▼
                  ListingPage
```

Đây là một parser structure khá sạch.

---

# 24. SOLID của Buổi 9

### SRP

`extract_novel()`:

```text
Một card → NovelSummary
```

`extract_next_url()`:

```text
Pagination HTML → next_url
```

`parse_listing()`:

```text
Orchestrate hai việc trên
```

---

### OCP

Website khác có pagination khác:

```python
class OtherSiteListingParser(
    BaseSiteParser
):
    NEXT_SELECTOR = "a[rel='next']"
```

Không sửa BaseSiteParser.

---

### DIP

Application phụ thuộc:

```text
ListingParser Protocol
```

không phụ thuộc:

```text
TruyenFullListingParser
```

---

# 25. Bài tập Buổi 9

### Bài 1

Viết test:

```text
<a class="next"
   href="/truyen/trang-3">
```

với current URL:

```text
https://example.com/truyen/trang-2
```

Kết quả phải:

```text
https://example.com/truyen/trang-3
```

---

### Bài 2

Test trang cuối:

```html
<!-- không có a.next -->
```

phải:

```python
assert result.next_url is None
```

---

### Bài 3

Test:

```html
<a class="next">Next</a>
```

không có href.

Kết quả:

```python
assert result.next_url is None
```

---

### Bài 4 — quan trọng

Viết một `CrawlListingUseCase` đơn giản:

```text
start_url
    ↓
fetch
    ↓
parse
    ↓
save novels
    ↓
next_url
    ↓
fetch
    ↓
parse
    ↓
...
```

**Không được để parser gọi HTTPX.**

---

# 26. Roadmap

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
```

### Buổi 10 — Pagination Robustness

Chúng ta sẽ xử lý các trường hợp thực tế hơn:

```text
1 2 3 ... 10 Next
```

```text
Previous 1 2 3 Next
```

```text
rel="next"
```

```text
disabled
```

```text
relative URL
absolute URL
query URL
```

và quan trọng hơn:

```text
page 1
  ↓
page 2
  ↓
page 3
```

sẽ được thiết kế sao cho **không bị duplicate, loop vô hạn hoặc crawl sai trang**.

Sau đó **Buổi 11** mới đi sâu vào các trường hợp pagination “bẩn” của website thực tế.
