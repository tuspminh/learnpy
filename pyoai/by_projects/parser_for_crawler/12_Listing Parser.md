# Phần III — Listing Parser

# Buổi 12 — Listing Parser hoàn chỉnh

Hôm nay chúng ta **đóng gói toàn bộ kiến thức Buổi 8 → 11** thành một Listing Parser có cấu trúc sạch, dễ test và sẵn sàng để sau này gắn vào Crawler.

Mục tiêu cuối buổi:

```text
page_source + current_url
            │
            ▼
     ListingParser
            │
       ┌────┴────┐
       ▼         ▼
    novels    next_url
       │         │
       └────┬────┘
            ▼
       ListingPage
```

---

# 1. Review toàn bộ Phần III

Chúng ta đã đi qua:

```text
Buổi 8
Parse Novel Listing
        ↓
list[NovelSummary]

Buổi 9
Extract Novel Card
        ↓
NovelCardExtractor

Buổi 10
Listing Pagination
        ↓
next_url

Buổi 11
Pagination Robustness
        ↓
safe next_url

Buổi 12
Listing Parser hoàn chỉnh
```

Đầu vào duy nhất:

```python
page_source: str
url: str
```

Đầu ra:

```python
ListingPage
```

---

# 2. Domain Model

Trước tiên kiểm tra lại Domain.

`domain/novel.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str
```

Listing chỉ cần 3 thông tin:

```text
title
author
url
```

Không cần:

```text
cover
description
status
chapters
```

Những thông tin đó thuộc `Novel` detail.

---

# 3. ListingPage

`domain/parser_result.py`

```python
from dataclasses import dataclass

from .novel import NovelSummary


@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Ví dụ:

```python
ListingPage(
    items=[
        NovelSummary(
            title="Novel A",
            author="Author A",
            url="https://example.com/book/a",
        ),
        NovelSummary(
            title="Novel B",
            author="Author B",
            url="https://example.com/book/b",
        ),
    ],
    next_url="https://example.com/truyen?page=2",
)
```

---

# 4. Cấu trúc hoàn chỉnh

Đến Buổi 12, tôi khuyên dùng:

```text
src/
└── crawler/
    ├── domain/
    │   ├── novel.py
    │   ├── parser_result.py
    │   └── parser_error.py
    │
    └── infrastructure/
        └── parser/
            ├── base.py
            ├── context.py
            ├── helpers.py
            ├── required.py
            ├── url_resolver.py
            ├── selectolax_document.py
            │
            └── plugins/
                └── truyenfull/
                    ├── __init__.py
                    ├── listing.py
                    └── novel_card.py
```

Điểm mới đáng chú ý:

```text
listing.py
      │
      └── NovelCardExtractor
```

Chúng ta thực sự tách extraction logic ra.

---

# 5. Vì sao cần `NovelCardExtractor`?

Nếu tất cả nằm trong:

```python
TruyenFullListingParser
```

thì class rất nhanh trở thành:

```text
TruyenFullListingParser
├── parse_listing()
├── extract_novel()
├── extract_title()
├── extract_author()
├── extract_url()
├── extract_next_url()
├── validate_url()
├── ...
```

Trong tương lai parser còn phải xử lý:

```text
Novel Parser
Chapter Parser
Metadata
Image
Status
Description
```

Class sẽ rất lớn.

Do đó:

```text
ListingParser
      │
      ├── NovelCardExtractor
      │
      └── Pagination extraction
```

---

# 6. `NovelCardExtractor`

Tạo:

```text
plugins/truyenfull/novel_card.py
```

Code:

```python
from crawler.domain.novel import NovelSummary

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.required import (
    required_text,
    required_attribute,
)


class NovelCardExtractor:
    TITLE_SELECTOR = ".story-title a"

    AUTHOR_SELECTOR = ".story-author"

    def extract(
        self,
        card,
        context: ParserContext,
    ) -> NovelSummary:

        title_node = card.css_first(self.TITLE_SELECTOR)

        author_node = card.css_first(self.AUTHOR_SELECTOR)

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
```

---

# 7. Trách nhiệm của `NovelCardExtractor`

Nó chỉ làm:

```text
HTML card
   ↓
NovelSummary
```

Không làm:

```text
❌ pagination
❌ HTTP
❌ database
❌ crawl
❌ retry
```

Đây là SRP.

---

# 8. `ListingParser` bây giờ rất rõ ràng

`listing.py`:

```python
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from .novel_card import NovelCardExtractor


class TruyenFullListingParser(BaseSiteParser):
    STORY_SELECTOR = ".story"

    NEXT_SELECTOR = "a.next"

    def __init__(
        self,
        card_extractor: NovelCardExtractor | None = None,
    ):

        self._card_extractor = card_extractor or NovelCardExtractor()

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        context = self.create_context(
            page_source,
            url,
        )

        items = self.parse_novels(context)

        next_url = self.parse_next_page(context)

        return ListingPage(
            items=items,
            next_url=next_url,
        )
```

Ta thấy `parse_listing()` bây giờ rất sạch.

---

# 9. `parse_novels()`

Tiếp tục:

```python
def parse_novels(
    self,
    context: ParserContext,
):
    stories = context.document.all(self.STORY_SELECTOR)

    items = []

    for story in stories:
        novel = self._card_extractor.extract(
            story,
            context,
        )

        items.append(novel)

    return items
```

Flow:

```text
parse_listing()
       │
       ├── parse_novels()
       │       │
       │       ├── card 1
       │       │     ↓
       │       │ NovelSummary
       │       │
       │       ├── card 2
       │       │     ↓
       │       │ NovelSummary
       │       │
       │       └── card 3
       │             ↓
       │          NovelSummary
       │
       └── parse_next_page()
```

---

# 10. `parse_next_page()`

Đây là abstraction nhỏ rất hữu ích:

```python
def parse_next_page(
    self,
    context: ParserContext,
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
```

---

# 11. `is_next_disabled()`

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

Đây là logic của website.

Nếu website khác dùng:

```html
aria-disabled="true"
```

thì parser plugin của website đó có thể override.

---

# 12. Full `listing.py`

Bây giờ ghép lại:

```python
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from .novel_card import NovelCardExtractor


class TruyenFullListingParser(BaseSiteParser):
    STORY_SELECTOR = ".story"

    NEXT_SELECTOR = "a.next"

    def __init__(
        self,
        card_extractor: NovelCardExtractor | None = None,
    ):

        self._card_extractor = card_extractor or NovelCardExtractor()

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        context = self.create_context(
            page_source,
            url,
        )

        items = self.parse_novels(context)

        next_url = self.parse_next_page(context)

        return ListingPage(
            items=items,
            next_url=next_url,
        )

    def parse_novels(
        self,
        context: ParserContext,
    ):

        stories = context.document.all(self.STORY_SELECTOR)

        items = []

        for story in stories:
            novel = self._card_extractor.extract(
                story,
                context,
            )

            items.append(novel)

        return items

    def parse_next_page(
        self,
        context: ParserContext,
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

# 13. Có một cải tiến quan trọng: Type Hint

Ta không nên để:

```python
def parse_novels(...):
```

không có return type.

Domain đã có:

```python
NovelSummary
```

nên viết:

```python
from crawler.domain.novel import NovelSummary
```

và:

```python
def parse_novels(
    self,
    context: ParserContext,
) -> list[NovelSummary]:
```

---

# 14. Full code tốt hơn

```python
from crawler.domain.novel import NovelSummary
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from .novel_card import NovelCardExtractor


class TruyenFullListingParser(BaseSiteParser):
    STORY_SELECTOR = ".story"

    NEXT_SELECTOR = "a.next"

    def __init__(
        self,
        card_extractor: NovelCardExtractor | None = None,
    ):

        self._card_extractor = card_extractor or NovelCardExtractor()

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        context = self.create_context(
            page_source,
            url,
        )

        items = self.parse_novels(context)

        next_url = self.parse_next_page(context)

        return ListingPage(
            items=items,
            next_url=next_url,
        )

    def parse_novels(
        self,
        context: ParserContext,
    ) -> list[NovelSummary]:

        stories = context.document.all(self.STORY_SELECTOR)

        items: list[NovelSummary] = []

        for story in stories:
            novel = self._card_extractor.extract(
                story,
                context,
            )

            items.append(novel)

        return items

    def parse_next_page(
        self,
        context: ParserContext,
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

Đây là phiên bản tôi khuyên dùng ở thời điểm hiện tại.

---

# 15. Tại sao `parse_next_page()` chứ không phải `crawl_next_page()`?

Tên:

```python
parse_next_page()
```

rất quan trọng.

Nó nói chính xác:

> Tôi đọc HTML và tìm URL.

Không nói:

> Tôi sẽ đi đến trang tiếp theo.

Nếu đặt:

```python
crawl_next_page()
```

người đọc có thể nghĩ parser thực hiện HTTP request.

Điều này vi phạm boundary:

```text
HTTPX
   ↓
page_source
   ↓
Parser
```

---

# 16. Test hoàn chỉnh

Bây giờ ta tạo test:

```text
tests/
└── infrastructure/
    └── parser/
        └── truyenfull/
            ├── test_novel_card.py
            └── test_listing.py
```

---

# 17. Test nhiều Novel

```python
from crawler.infrastructure.parser.plugins.truyenfull.listing import (
    TruyenFullListingParser,
)


def test_parse_listing():

    html = """
    <html>
        <body>

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

            <div class="story">

                <h3 class="story-title">
                    <a href="/book/b">
                        Novel B
                    </a>
                </h3>

                <span class="story-author">
                    Author B
                </span>

            </div>

        </body>
    </html>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert len(result.items) == 2

    assert result.items[0].title == "Novel A"
    assert result.items[0].author == "Author A"
    assert result.items[0].url == "https://example.com/book/a"

    assert result.items[1].title == "Novel B"
    assert result.items[1].author == "Author B"
    assert result.items[1].url == "https://example.com/book/b"

    assert result.next_url is None
```

---

# 18. Test listing + pagination

```python
def test_parse_listing_with_pagination():

    html = """
    <html>
        <body>

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
                href="/trang-2"
            >
                Next
            </a>

        </body>
    </html>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert len(result.items) == 1

    assert result.next_url == "https://example.com/trang-2"
```

---

# 19. Test query pagination

```python
def test_parse_query_pagination():

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
        href="?page=2"
    >
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

# 20. Test trang cuối

```python
def test_last_page():

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

    <div class="pagination">

        <a href="/trang-1">
            1
        </a>

        <a href="/trang-2">
            2
        </a>

    </div>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/trang-2",
    )

    assert result.next_url is None
```

---

# 21. Test disabled

```python
def test_disabled_next():

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
        href="/trang-999"
    >
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/trang-2",
    )

    assert result.next_url is None
```

---

# 22. Test thiếu href

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

# 23. Test relative URL

```python
def test_relative_next_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="book/a">
                Novel A
            </a>
        </h3>

        <span class="story-author">
            Author A
        </span>

    </div>

    <a
        class="next"
        href="trang-2"
    >
        Next
    </a>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen/",
    )

    assert result.items[0].url == "https://example.com/truyen/book/a"

    assert result.next_url == "https://example.com/truyen/trang-2"
```

---

# 24. Test lỗi required field

Đây là test rất quan trọng.

HTML:

```html
<div class="story">
    <span class="story-author">
        Author A
    </span>
</div>
```

Thiếu:

```text
title
URL
```

Parser phải raise:

```python
MissingFieldError
```

Ví dụ:

```python
import pytest

from crawler.domain.parser_error import (
    MissingFieldError,
)


def test_missing_title():

    html = """
    <div class="story">

        <span class="story-author">
            Author A
        </span>

    </div>
    """

    parser = TruyenFullListingParser()

    with pytest.raises(MissingFieldError):
        parser.parse_listing(
            html,
            "https://example.com/truyen",
        )
```

---

# 25. Đây là một điểm kiến trúc rất hay

Hãy so sánh:

### Không có next

```text
HTML
 ↓
không tìm thấy next
 ↓
next_url=None
```

**Không lỗi.**

### Thiếu title

```text
HTML
 ↓
card
 ↓
không có title
 ↓
MissingFieldError
```

**Có lỗi.**

Tức là:

```text
Optional pagination
        ≠
Required novel data
```

---

# 26. Dependency Injection xuất hiện

Chúng ta có:

```python
def __init__(
    self,
    card_extractor=None,
):
```

cho phép:

```python
extractor = NovelCardExtractor()

parser = TruyenFullListingParser(card_extractor=extractor)
```

Nhưng quan trọng hơn, test có thể inject fake extractor.

Ví dụ:

```python
class FakeNovelCardExtractor:
    def extract(
        self,
        card,
        context,
    ):

        return NovelSummary(
            title="TEST",
            author="TEST",
            url="https://example.com/test",
        )
```

Sau đó:

```python
parser = TruyenFullListingParser(card_extractor=FakeNovelCardExtractor())
```

Parser không cần biết implementation cụ thể.

Đây chính là **Dependency Inversion / Dependency Injection** mà bạn đã học trong SOLID.

---

# 27. Nhưng có cần Protocol không?

Có thể viết:

```python
from typing import Protocol


class NovelCardExtractorProtocol(Protocol):
    def extract(
        self,
        card,
        context,
    ) -> NovelSummary: ...
```

Sau đó:

```python
def __init__(
    self,
    card_extractor: NovelCardExtractorProtocol,
):
```

Điều này tốt nếu project lớn.

Nhưng ở Buổi 12 tôi **chưa ép abstraction thêm**, vì:

```text
NovelCardExtractor
```

mới chỉ có một implementation.

Nguyên tắc:

> Không tạo abstraction chỉ vì "SOLID nói phải có abstraction".

SOLID không có nghĩa là tạo interface cho mọi class.

---

# 28. Toàn bộ flow hiện tại

Bây giờ Listing Parser của chúng ta đã có kiến trúc:

```text
                   page_source
                       │
                       ▼
                BaseSiteParser
                       │
                       ▼
                ParserContext
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
            parse_novels  parse_next_page
                 │           │
                 ▼           ▼
        NovelCardExtractor  next_url
                 │
                 ▼
          NovelSummary[]
                 │
                 └─────┬─────┘
                       ▼
                  ListingPage
```

---

# 29. HTTPX đứng ở đâu?

HTTPX **không nằm trong parser**.

Toàn bộ hệ thống:

```text
                 HTTPX Fetcher
                      │
                      │ Response
                      ▼
                response.text
                      │
                      ▼
              ListingParser
                      │
                      ▼
                ListingPage
                ├── items
                └── next_url
                      │
                      ▼
             Application Service
                │           │
                ▼           ▼
           Repository    next request
```

Đây chính là boundary mà chúng ta muốn giữ.

---

# 30. Pagination loop thuộc Application

Ví dụ:

```python
class CrawlListingUseCase:
    def __init__(
        self,
        fetcher,
        parser,
        repository,
    ):
        self._fetcher = fetcher
        self._parser = parser
        self._repository = repository

    def execute(
        self,
        start_url: str,
    ):

        visited_urls: set[str] = set()

        current_url = start_url

        while current_url:
            if current_url in visited_urls:
                break

            visited_urls.add(current_url)

            response = self._fetcher.fetch(current_url)

            page = self._parser.parse_listing(
                response.text,
                current_url,
            )

            for novel in page.items:
                self._repository.save(novel)

            current_url = page.next_url
```

Parser không biết đoạn code này tồn tại.

Đó chính là kiến trúc tốt.

---

# 31. Một quyết định thiết kế quan trọng

Bạn có thể thấy `ListingPage` hiện tại:

```python
@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Có thể sau này bạn muốn:

```text
previous_url
page_number
total_pages
```

Không nên thêm ngay.

Chỉ thêm khi website/framework thực sự cần.

Hiện tại crawler chỉ cần:

```text
items
next_url
```

là đủ.

---

# 32. Phần III đã hoàn thành

Roadmap chính xác của chúng ta hiện tại:

```text
# Phần III — Listing Parser

Buổi 8 — Parse Novel Listing          ✅
        page_source → novels

Buổi 9 — Extract Novel Card           ✅
        card → NovelSummary

Buổi 10 — Listing Pagination          ✅
        page → next_url

Buổi 11 — Pagination Robustness       ✅
        safe next_url

Buổi 12 — Listing Parser hoàn chỉnh   ✅
        parse_listing()
        parse_novels()
        parse_next_page()
```

---

# 33. Kiến thức SOLID đã áp dụng

### SRP

```text
HTTPX
  → HTTP

NovelCardExtractor
  → Novel card extraction

ListingParser
  → Listing orchestration

Application
  → Crawl policy

Repository
  → Persistence
```

### OCP

Website mới:

```text
TruyenFullListingParser
TruyenYYListingParser
TruyenCVListingParser
```

không cần sửa crawler core.

### DIP

Application phụ thuộc parser abstraction:

```text
Application
      ↓
ListingParser
      ↑
TruyenFullListingParser
```

không:

```text
Application
      ↓
TruyenFullListingParser
```

---

# 34. Một nguyên tắc cần nhớ

Đây là câu tôi muốn bạn nhớ từ Phần III:

> **Parser trả dữ liệu mà nó nhìn thấy; Application quyết định phải làm gì với dữ liệu đó.**

Ví dụ:

```text
Parser:
"Trang tiếp theo là /trang-2"

Application:
"Đã crawl /trang-2 rồi → không crawl nữa."
```

Parser:

```text
"HTML có 20 novels."
```

Application:

```text
"Novel này đã có trong database → upsert/skip."
```

Parser:

```text
"Title bị thiếu."
```

Application:

```text
"ParserError → log → retry/skip/mark failed."
```

Đây là boundary rất quan trọng khi sau này chúng ta xây crawler production.

---

## Bước tiếp theo — Phần IV: Novel Parser

Sau khi Listing Parser hoàn thành, ta chuyển sang:

```text
# Phần IV — Novel Parser

Buổi 13 — Parse Novel Detail
```

Input:

```text
novel detail page source
```

Output:

```python
NovelPage(
    novel=Novel(
        title=...,
        author=...,
        url=...,
        cover=...,
        description=...,
        status=...,
    ),
    chapters=[...],
    next_url=...,
)
```

Và chúng ta sẽ bắt đầu **từ `title`, `author`, `url` của trang chi tiết**, sau đó mới lần lượt thêm `cover`, `description`, `status`, rồi chapter listing và chapter pagination.
