# Buổi 6 — BaseSiteParser + URL Resolver + Parser Context

Ở Buổi 5 chúng ta đã có **Domain Model**. Bây giờ bắt đầu bước chuyển từ:

```text
HTML
 ↓
Selectolax
 ↓
Domain Model
```

thành một kiến trúc parser thực tế có thể mở rộng cho nhiều website.

Mục tiêu Buổi 6:

```text
page_source
     │
     ▼
BaseSiteParser
     │
     ├── ParserContext
     │      └── URL Resolver
     │
     ▼
Selectolax
     │
     ▼
NovelSummary
```

Và cuối buổi chúng ta sẽ có một `parse_listing()` đầu tiên chạy được.

---

# 1. Vì sao cần BaseSiteParser?

Giả sử sau này crawler hỗ trợ:

```text
TruyenFull
TruyenYY
TruyenCV
TruyenABC
```

Mỗi website có HTML khác nhau:

```text
TruyenFullParser
TruyenYYParser
TruyenCVParser
TruyenABCParser
```

Nhưng tất cả đều cần những chức năng chung:

* nhận `page_source`
* biết URL hiện tại
* resolve relative URL
* tạo Selectolax document
* normalize text
* lấy attribute
* xử lý URL

Nếu copy các logic này vào từng parser thì sẽ thành:

```text
TruyenFullParser
    ├── parse HTML
    ├── resolve URL
    ├── normalize text

TruyenYYParser
    ├── parse HTML
    ├── resolve URL
    ├── normalize text

TruyenCVParser
    ├── parse HTML
    ├── resolve URL
    ├── normalize text
```

Đây là vi phạm **DRY + SRP**.

Ta tạo:

```text
BaseSiteParser
```

để chứa những hành vi dùng chung.

---

# 2. Kiến trúc sau Buổi 6

Cấu trúc:

```text
src/
└── crawler/
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   ├── parser_result.py
    │   └── parser_error.py
    │
    └── infrastructure/
        └── parser/
            ├── base.py
            ├── context.py
            ├── url_resolver.py
            ├── selectolax_document.py
            │
            └── plugins/
                └── truyenfull/
                    └── listing.py
```

Luồng:

```text
HTTPX
   │
   │ page_source
   ▼
TruyenFullListingParser
   │
   ▼
BaseSiteParser
   │
   ├── ParserContext
   │
   ├── SelectolaxDocument
   │
   └── URL Resolver
   │
   ▼
NovelSummary
```

---

# 3. URL Resolver

Đây là thành phần rất quan trọng.

HTML thường không chứa URL tuyệt đối.

Ví dụ:

```html
<a href="/truyen/dau-pha-thuong-khung">
```

hoặc:

```html
<a href="truyen/dau-pha-thuong-khung">
```

hoặc:

```html
<a href="https://example.com/truyen/dau-pha-thuong-khung">
```

Parser cần biến tất cả thành:

```text
https://example.com/truyen/dau-pha-thuong-khung
```

Chúng ta không nên tự nối string:

```python
base_url + href
```

vì sẽ có rất nhiều trường hợp sai.

Python đã có:

```python
urllib.parse.urljoin
```

---

# 4. `url_resolver.py`

Tạo:

```text
infrastructure/parser/url_resolver.py
```

Code hoàn chỉnh:

```python
from urllib.parse import urljoin


class UrlResolver:
    """Resolve relative URLs against a base URL."""

    def __init__(self, base_url: str):
        self._base_url = base_url

    def resolve(self, url: str) -> str:
        return urljoin(self._base_url, url)
```

Ví dụ:

```python
resolver = UrlResolver(
    "https://example.com/truyen"
)

print(
    resolver.resolve(
        "/truyen/dau-pha-thuong-khung"
    )
)
```

Kết quả:

```text
https://example.com/truyen/dau-pha-thuong-khung
```

---

# 5. Test URL Resolver

Tạo:

```text
tests/
└── parser/
    └── test_url_resolver.py
```

```python
from crawler.infrastructure.parser.url_resolver import UrlResolver


def test_resolve_absolute_url():
    resolver = UrlResolver(
        "https://example.com/truyen"
    )

    result = resolver.resolve(
        "https://other.com/book"
    )

    assert result == "https://other.com/book"


def test_resolve_root_relative_url():
    resolver = UrlResolver(
        "https://example.com/truyen"
    )

    result = resolver.resolve(
        "/book/1"
    )

    assert result == "https://example.com/book/1"


def test_resolve_relative_url():
    resolver = UrlResolver(
        "https://example.com/truyen/"
    )

    result = resolver.resolve(
        "book/1"
    )

    assert result == "https://example.com/truyen/book/1"
```

Chạy:

```bash
pytest
```

---

# 6. Parser Context

Bây giờ chúng ta cần một object chứa **context của lần parse hiện tại**.

Parser cần biết:

```text
current URL
page source
URL resolver
document
```

Thay vì truyền hàng loạt thứ:

```python
parse_listing(
    page_source,
    url,
    resolver,
    document,
    ...
)
```

ta gom context lại.

---

# 7. `ParserContext`

Tạo:

```text
infrastructure/parser/context.py
```

```python
from dataclasses import dataclass

from crawler.infrastructure.parser.url_resolver import UrlResolver
from crawler.infrastructure.parser.selectolax_document import (
    SelectolaxDocument,
)


@dataclass
class ParserContext:
    url: str
    document: SelectolaxDocument
    url_resolver: UrlResolver

    def resolve_url(self, url: str) -> str:
        return self.url_resolver.resolve(url)
```

Bây giờ parser có:

```python
context.url
```

và:

```python
context.document
```

và:

```python
context.resolve_url(...)
```

---

# 8. BaseSiteParser

Đây là phần quan trọng nhất của Buổi 6.

Tạo:

```text
infrastructure/parser/base.py
```

```python
from crawler.infrastructure.parser.context import ParserContext
from crawler.infrastructure.parser.selectolax_document import (
    SelectolaxDocument,
)
from crawler.infrastructure.parser.url_resolver import UrlResolver


class BaseSiteParser:
    """Base class containing common parser infrastructure."""

    def create_context(
        self,
        page_source: str,
        url: str,
    ) -> ParserContext:

        document = SelectolaxDocument(page_source)

        resolver = UrlResolver(url)

        return ParserContext(
            url=url,
            document=document,
            url_resolver=resolver,
        )
```

Nó có nhiệm vụ:

```text
page_source
     │
     ▼
SelectolaxDocument
     │
     ▼
UrlResolver
     │
     ▼
ParserContext
```

---

# 9. Nhưng BaseSiteParser không parse Listing

Đây là điểm kiến trúc rất quan trọng.

`BaseSiteParser` **không được biết**:

```text
.title
.author
.story
.chapter
```

vì đây là logic riêng của từng website.

Nó chỉ cung cấp infrastructure chung.

Ví dụ:

```python
class BaseSiteParser:

    def create_context(...):
        ...
```

Nhưng:

```python
class TruyenFullListingParser(BaseSiteParser):

    def parse_listing(...):
        ...
```

mới biết:

```css
.story-list
.story-title
.story-author
```

Đây chính là:

**OCP — Open/Closed Principle**

---

# 10. Xây Listing Parser đầu tiên

Giả sử HTML website có:

```html
<div class="story-list">

    <div class="story">
        <h3 class="story-title">
            <a href="/truyen/dau-pha-thuong-khung">
                Đấu Phá Thương Khung
            </a>
        </h3>

        <span class="story-author">
            Thiên Tằm Thổ Đậu
        </span>
    </div>

    <div class="story">
        <h3 class="story-title">
            <a href="/truyen/pham-nhan-tu-tien">
                Phàm Nhân Tu Tiên
            </a>
        </h3>

        <span class="story-author">
            Vong Ngữ
        </span>
    </div>

</div>
```

Parser sẽ làm:

```text
.story
   │
   ├── .story-title a
   └── .story-author
```

---

# 11. Helper lấy text

Không nên viết:

```python
node.css_first(".story-author").text()
```

vì node có thể không tồn tại.

Tạo helper:

```text
infrastructure/parser/helpers.py
```

```python
def get_text(node) -> str | None:
    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

---

# 12. Listing Parser

Tạo:

```text
infrastructure/parser/plugins/truyenfull/listing.py
```

```python
from crawler.domain.novel import NovelSummary
from crawler.domain.parser_result import ListingPage
from crawler.domain.parser_error import MissingFieldError

from crawler.infrastructure.parser.base import BaseSiteParser
from crawler.infrastructure.parser.helpers import get_text


class TruyenFullListingParser(BaseSiteParser):

    STORY_SELECTOR = ".story"

    TITLE_SELECTOR = ".story-title a"

    AUTHOR_SELECTOR = ".story-author"

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        context = self.create_context(
            page_source,
            url,
        )

        items: list[NovelSummary] = []

        stories = context.document.all(
            self.STORY_SELECTOR
        )

        for story in stories:

            title_node = story.css_first(
                self.TITLE_SELECTOR
            )

            author_node = story.css_first(
                self.AUTHOR_SELECTOR
            )

            title = get_text(title_node)
            author = get_text(author_node)

            if title is None:
                raise MissingFieldError(
                    "title",
                    self.TITLE_SELECTOR,
                )

            if author is None:
                raise MissingFieldError(
                    "author",
                    self.AUTHOR_SELECTOR,
                )

            href = (
                title_node.attributes.get("href")
                if title_node
                else None
            )

            if not href:
                raise MissingFieldError(
                    "url",
                    "href",
                )

            novel_url = context.resolve_url(href)

            items.append(
                NovelSummary(
                    title=title,
                    author=author,
                    url=novel_url,
                )
            )

        return ListingPage(
            items=items,
            next_url=None,
        )
```

---

# 13. Nhìn kỹ luồng `parse_listing()`

Đây là phần cần hiểu thật kỹ.

Ta nhận:

```python
page_source: str
url: str
```

Sau đó:

```python
context = self.create_context(
    page_source,
    url,
)
```

Context chứa:

```text
context
├── url
├── document
└── url_resolver
```

Sau đó:

```python
stories = context.document.all(".story")
```

Selectolax tìm tất cả:

```html
<div class="story">
```

Rồi từng story:

```python
for story in stories:
```

Ta tìm:

```python
title_node = story.css_first(".story-title a")
```

và:

```python
author_node = story.css_first(".story-author")
```

Sau đó:

```python
title = get_text(title_node)
author = get_text(author_node)
```

Cuối cùng:

```python
novel_url = context.resolve_url(href)
```

và tạo:

```python
NovelSummary(...)
```

---

# 14. Test toàn bộ Listing Parser

Tạo:

```text
tests/parser/test_truyenfull_listing.py
```

```python
from crawler.infrastructure.parser.plugins.truyenfull.listing import (
    TruyenFullListingParser,
)


HTML = """
<html>
<body>

<div class="story-list">

    <div class="story">

        <h3 class="story-title">
            <a href="/truyen/dau-pha-thuong-khung">
                Đấu Phá Thương Khung
            </a>
        </h3>

        <span class="story-author">
            Thiên Tằm Thổ Đậu
        </span>

    </div>

    <div class="story">

        <h3 class="story-title">
            <a href="/truyen/pham-nhan-tu-tien">
                Phàm Nhân Tu Tiên
            </a>
        </h3>

        <span class="story-author">
            Vong Ngữ
        </span>

    </div>

</div>

</body>
</html>
"""


def test_parse_listing():

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        page_source=HTML,
        url="https://example.com/truyen",
    )

    assert len(result.items) == 2

    first = result.items[0]

    assert first.title == "Đấu Phá Thương Khung"

    assert first.author == "Thiên Tằm Thổ Đậu"

    assert (
        first.url
        == "https://example.com/truyen/dau-pha-thuong-khung"
    )


def test_parse_second_novel():

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        page_source=HTML,
        url="https://example.com/truyen",
    )

    second = result.items[1]

    assert second.title == "Phàm Nhân Tu Tiên"

    assert second.author == "Vong Ngữ"

    assert (
        second.url
        == "https://example.com/truyen/pham-nhan-tu-tien"
    )
```

---

# 15. Một vấn đề quan trọng: Pagination

Hiện tại:

```python
return ListingPage(
    items=items,
    next_url=None,
)
```

Tạm thời chưa parse pagination.

Ví dụ HTML:

```html
<ul class="pagination">
    <li>
        <a href="/truyen?page=2">2</a>
    </li>

    <li>
        <a href="/truyen?page=3">3</a>
    </li>
</ul>
```

Sau này parser sẽ lấy:

```text
next_url
```

Ví dụ:

```text
https://example.com/truyen?page=2
```

Nhưng **application mới là nơi quyết định fetch tiếp**.

Parser không được làm:

```python
httpx.get(next_url)
```

Tuyệt đối không.

Kiến trúc vẫn là:

```text
Parser
   │
   │ next_url
   ▼
Application
   │
   │ fetch(next_url)
   ▼
HTTPX
   │
   │ page_source
   ▼
Parser
```

---

# 16. Vì sao pagination không nằm trong BaseSiteParser?

Vì mỗi website có HTML pagination khác nhau.

Website A:

```html
<a class="next">
```

Website B:

```html
<li class="next-page">
```

Website C:

```html
<a rel="next">
```

Do đó:

```text
BaseSiteParser
    ↓
common infrastructure
```

còn:

```text
TruyenFullListingParser
    ↓
site-specific selectors
```

---

# 17. SOLID trong Buổi 6

### SRP

`UrlResolver`:

```text
chỉ resolve URL
```

`SelectolaxDocument`:

```text
chỉ làm adapter cho DOM
```

`ParserContext`:

```text
chứa context parse
```

`BaseSiteParser`:

```text
tạo context chung
```

`TruyenFullListingParser`:

```text
parse listing của TruyenFull
```

Mỗi class có một trách nhiệm rõ ràng.

---

### OCP

Muốn thêm:

```text
TruyenYYListingParser
```

không cần sửa:

```text
BaseSiteParser
UrlResolver
ParserContext
```

Chỉ thêm class:

```python
class TruyenYYListingParser(BaseSiteParser):
    ...
```

---

### DIP

Application không nên:

```python
parser = TruyenFullListingParser()
```

mà nên nhận abstraction:

```python
class CrawlListingUseCase:

    def __init__(self, parser):
        self._parser = parser
```

Sau này Dependency Injection sẽ đưa parser vào.

---

# 18. Toàn bộ kiến trúc hiện tại

Sau Buổi 6, chúng ta có:

```text
                         ┌──────────────────┐
                         │      HTTPX       │
                         └────────┬─────────┘
                                  │
                           page_source
                                  │
                                  ▼
                     ┌───────────────────────┐
                     │ TruyenFullListing     │
                     │ Parser                │
                     └───────────┬───────────┘
                                 │
                                 ▼
                       ┌─────────────────┐
                       │ BaseSiteParser  │
                       └────────┬────────┘
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
          ┌─────────────────┐       ┌────────────────┐
          │ Selectolax      │       │ URL Resolver   │
          │ Document        │       │                │
          └────────┬────────┘       └───────┬────────┘
                   │                        │
                   └──────────┬─────────────┘
                              ▼
                       ParserContext
                              │
                              ▼
                       NovelSummary
                              │
                              ▼
                        ListingPage
```

---

# 19. Một nguyên tắc kiến trúc cần nhớ

Từ bây giờ, hãy phân biệt thật rõ:

### Fetcher

```text
URL
 ↓
HTTP
 ↓
page_source
```

### Parser

```text
page_source
 ↓
DOM
 ↓
Domain Model
```

### Application

```text
Fetch
 ↓
Parse
 ↓
Save
 ↓
Next page
```

Không được biến Parser thành:

```text
Parser
 ├── HTTPX
 ├── Retry
 ├── Proxy
 ├── Database
 └── HTML parsing
```

Parser của chúng ta chỉ:

> **HTML → Domain**

---

# 20. Bài tập Buổi 6

Hãy tự viết thêm:

### Bài 1

Test:

```python
UrlResolver(
    "https://example.com/truyen/"
).resolve(
    "/abc"
)
```

kết quả:

```text
https://example.com/abc
```

### Bài 2

Thêm một story:

```html
<div class="story">
    ...
</div>
```

và kiểm tra:

```python
len(result.items) == 3
```

### Bài 3

Thử HTML thiếu author:

```html
<div class="story">
    <h3 class="story-title">
        <a href="/book/test">
            Test Novel
        </a>
    </h3>
</div>
```

Parser phải raise:

```python
MissingFieldError
```

chứ **không được** âm thầm tạo:

```python
author=""
```

---

## Roadmap tiếp theo

Chúng ta đang ở:

```text
01 Architecture                    ✅
02 Selectolax Foundation           ✅
03 Parser Interface                ✅
04 ParseResult + Validation        ✅
05 Domain Model                    ✅
06 BaseSiteParser + URL Resolver   ✅
```

**Buổi 7** sẽ hoàn thiện phần **Listing Models + Parser Helper**, đặc biệt là thiết kế chuẩn cho:

```text
NovelSummary
ListingPage
Pagination
Selector
Required / Optional field
```

để sang **Buổi 8** chúng ta có thể xây `parse-listing` thực chiến một cách sạch sẽ, thay vì viết một parser lớn ngay từ đầu.
