# Buổi 7 — Listing Models + Parser Helpers + thiết kế Pagination

Ở Buổi 6 chúng ta đã có:

```text
HTTPX
   ↓
page_source
   ↓
BaseSiteParser
   ↓
ParserContext
   ├── SelectolaxDocument
   └── UrlResolver
```

Hôm nay chúng ta **chưa vội viết parser listing hoàn chỉnh**. Mục tiêu là thiết kế lớp nền cho listing thật sạch, để Buổi 8 chỉ tập trung vào việc:

```text
HTML listing
    ↓
extract novels
    ↓
extract pagination
    ↓
ListingPage
```

---

# 1. Listing thực tế cần trả về gì?

Một trang listing ví dụ:

```text
/truyen
```

có:

```text
Novel A
Novel B
Novel C

Trang 1 2 3 4 5
```

Parser không nên trả về một đống dictionary:

```python
[
    {
        "title": "...",
        "author": "...",
        "url": "..."
    }
]
```

Mà trả về Domain Model:

```python
NovelSummary(
    title="...",
    author="...",
    url="..."
)
```

Toàn bộ page:

```python
ListingPage(
    items=[...],
    next_url="..."
)
```

---

# 2. Phân biệt Item và Page

Đây là khái niệm rất quan trọng.

## NovelSummary

Đại diện cho **một truyện trong listing**:

```text
NovelSummary
├── title
├── author
└── url
```

Nó không biết:

```text
pagination
next page
HTML
Selectolax
```

---

## ListingPage

Đại diện cho **một trang listing**:

```text
ListingPage
├── items
│   ├── NovelSummary
│   ├── NovelSummary
│   └── NovelSummary
│
└── next_url
```

Vì vậy:

```text
NovelSummary ≠ ListingPage
```

---

# 3. Vì sao `next_url` phải nằm trong ListingPage?

Ví dụ:

```text
Novel A
Novel B
Novel C
```

không có nghĩa bản thân Novel A biết:

```text
next page = /truyen?page=2
```

Pagination là thuộc tính của **trang listing**, không phải của novel.

Do đó:

```python
ListingPage(
    items=[novel_a, novel_b, novel_c],
    next_url="https://example.com/truyen?page=2"
)
```

là hợp lý.

Không làm:

```python
NovelSummary(
    title="...",
    author="...",
    url="...",
    next_url="..."
)
```

---

# 4. Listing Models hiện tại

Chúng ta đã có ở Buổi 5:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str
```

và:

```python
@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Tuy nhiên hôm nay chúng ta sẽ thiết kế kỹ hơn cách parser tạo ra chúng.

---

# 5. Một nguyên tắc rất quan trọng: Domain không biết HTML

Không được đưa selector vào Domain:

```python
@dataclass
class NovelSummary:
    title_selector: str
```

Không được:

```python
NovelSummary(
    css_selector=".story-title"
)
```

Không được import:

```python
from selectolax.parser import Node
```

vào:

```text
domain/
```

Domain chỉ biết:

```text
title
author
url
```

Còn:

```text
.story-title
.story-author
```

là chuyện của Infrastructure Parser.

---

# 6. Parser Helper

Ở Buổi 6 chúng ta có:

```python
def get_text(node) -> str | None:
    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

Hôm nay ta mở rộng helper.

Tạo:

```text
infrastructure/parser/helpers.py
```

```python
def get_text(node) -> str | None:
    if node is None:
        return None

    text = node.text().strip()

    return text or None


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

---

# 7. Tại sao cần `get_attribute()`?

Thay vì viết lặp đi lặp lại:

```python
href = node.attributes.get("href")

if href:
    href = href.strip()
```

ta chỉ cần:

```python
href = get_attribute(node, "href")
```

Ví dụ:

```python
title_node = story.css_first(".story-title a")

title = get_text(title_node)

href = get_attribute(
    title_node,
    "href",
)
```

---

# 8. Required và Optional

Đây là phần rất quan trọng khi thiết kế parser.

Có hai loại dữ liệu.

### Required

Listing:

```text
title
author
url
```

Nếu thiếu:

```text
ParserError
```

### Optional

Sau này có thể có:

```text
cover
description
status
```

Nếu thiếu:

```text
None
```

Không phải field nào cũng phải raise exception.

---

# 9. Tạo `required_text()`

Tạo:

```text
infrastructure/parser/required.py
```

```python
from crawler.domain.parser_error import MissingFieldError

from crawler.infrastructure.parser.helpers import (
    get_text,
    get_attribute,
)


def required_text(
    node,
    *,
    field: str,
    selector: str,
) -> str:

    value = get_text(node)

    if value is None:
        raise MissingFieldError(
            field,
            selector,
        )

    return value
```

Sử dụng:

```python
title = required_text(
    title_node,
    field="title",
    selector=".story-title a",
)
```

---

# 10. `required_attribute()`

Tiếp tục:

```python
def required_attribute(
    node,
    *,
    attribute: str,
    field: str,
    selector: str,
) -> str:

    value = get_attribute(
        node,
        attribute,
    )

    if value is None:
        raise MissingFieldError(
            field,
            f"{selector}[{attribute}]",
        )

    return value
```

Sử dụng:

```python
href = required_attribute(
    title_node,
    attribute="href",
    field="url",
    selector=".story-title a",
)
```

Code parser sẽ trở nên rõ ràng hơn rất nhiều:

```python
title = required_text(
    title_node,
    field="title",
    selector=".story-title a",
)

author = required_text(
    author_node,
    field="author",
    selector=".story-author",
)

href = required_attribute(
    title_node,
    attribute="href",
    field="url",
    selector=".story-title a",
)
```

Ta đọc code gần giống specification.

---

# 11. Optional field

Nếu field optional:

```python
cover = get_attribute(
    cover_node,
    "src",
)
```

Không dùng:

```python
required_attribute(...)
```

Vì cover có thể không tồn tại.

Ví dụ:

```text
Novel
├── title       REQUIRED
├── author      REQUIRED
├── url         REQUIRED
├── cover       OPTIONAL
├── description OPTIONAL
└── status      OPTIONAL
```

---

# 12. Pagination Model

Bây giờ tới một vấn đề lớn.

Có thể chúng ta chỉ cần:

```python
next_url: str | None
```

Như hiện tại.

Điều này đủ cho crawler tuần tự:

```text
page 1
 ↓
next_url
 ↓
page 2
 ↓
next_url
 ↓
page 3
```

Nhưng hãy nhìn vào bài toán lớn hơn.

Có website:

```text
Trang 1 2 3 4 5 6 7 8 9 10
```

Có website:

```text
‹ Trước 1 2 3 4 Sau ›
```

Có website:

```text
/load-more
```

Có website:

```text
?page=2
```

Có website:

```text
/trang-2
```

Parser không nên cố biến tất cả thành một hệ thống pagination phức tạp ngay bây giờ.

---

# 13. Thiết kế đơn giản trước

Ở giai đoạn hiện tại:

```python
@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Ý nghĩa:

```text
next_url == None
```

→ không còn trang tiếp theo.

Ví dụ:

```python
ListingPage(
    items=[
        NovelSummary(...),
        NovelSummary(...),
    ],
    next_url="https://example.com/truyen?page=2",
)
```

---

# 14. Parser không fetch `next_url`

Đây là quy tắc chúng ta phải giữ từ đầu.

Parser:

```text
HTML
 ↓
phát hiện next link
 ↓
resolve URL
 ↓
return next_url
```

Parser **không làm**:

```python
httpx.get(next_url)
```

Application mới làm:

```python
page = parser.parse_listing(
    page_source,
    url,
)

while page.next_url:

    response = fetcher.fetch(
        page.next_url
    )

    page = parser.parse_listing(
        response.text,
        page.next_url,
    )
```

Đây là separation of concerns.

---

# 15. Pagination không đồng nghĩa với Page Number

Một lỗi thiết kế phổ biến:

```python
ListingPage(
    page_number=2
)
```

rồi application tự tạo:

```python
?page=3
```

Không nên.

Parser nên lấy **link thật từ HTML**.

Ví dụ HTML:

```html
<a class="next" href="/truyen?page=2">
    Sau
</a>
```

Parser:

```text
href
 ↓
resolve
 ↓
https://example.com/truyen?page=2
```

Không cần biết URL sử dụng:

```text
?page=2
```

hay:

```text
/trang-2
```

---

# 16. Helper `optional_url()`

Ta có thể tạo helper:

```python
from crawler.infrastructure.parser.helpers import (
    get_attribute,
)


def optional_url(
    node,
    *,
    resolver,
    attribute: str = "href",
) -> str | None:

    href = get_attribute(
        node,
        attribute,
    )

    if href is None:
        return None

    return resolver.resolve(href)
```

Ví dụ:

```python
next_node = document.first(
    "a.next"
)

next_url = optional_url(
    next_node,
    resolver=context.url_resolver,
)
```

---

# 17. Nhưng có một vấn đề

Nếu:

```html
<a class="next">
```

không có:

```text
href
```

thì:

```python
next_url = None
```

Điều này có thể đúng.

Nhưng nếu website yêu cầu JavaScript:

```html
<a class="next" data-url="/truyen?page=2">
```

thì parser phải được thiết kế riêng cho website.

Đừng biến helper chung thành một thứ quá thông minh:

```python
if href:
    ...
elif data_url:
    ...
elif onclick:
    ...
elif javascript:
    ...
```

Đây là dấu hiệu abstraction bắt đầu quá mức.

**Base helper nên đơn giản. Site parser quyết định HTML semantics.**

---

# 18. Hoàn thiện bộ helper

`helpers.py`:

```python
def get_text(node) -> str | None:
    if node is None:
        return None

    text = node.text().strip()

    return text or None


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

`required.py`:

```python
from crawler.domain.parser_error import MissingFieldError

from crawler.infrastructure.parser.helpers import (
    get_text,
    get_attribute,
)


def required_text(
    node,
    *,
    field: str,
    selector: str,
) -> str:

    value = get_text(node)

    if value is None:
        raise MissingFieldError(
            field,
            selector,
        )

    return value


def required_attribute(
    node,
    *,
    attribute: str,
    field: str,
    selector: str,
) -> str:

    value = get_attribute(
        node,
        attribute,
    )

    if value is None:
        raise MissingFieldError(
            field,
            f"{selector}[{attribute}]",
        )

    return value
```

---

# 19. Refactor Listing Parser

Bây giờ parser của Buổi 6 sẽ được viết sạch hơn.

```python
from crawler.domain.novel import NovelSummary
from crawler.domain.parser_result import ListingPage

from crawler.infrastructure.parser.base import BaseSiteParser
from crawler.infrastructure.parser.required import (
    required_text,
    required_attribute,
)


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

So với Buổi 6, parser bây giờ tập trung vào đúng một việc:

> **Mapping HTML structure → NovelSummary**

Còn việc kiểm tra field đã được helper xử lý.

---

# 20. Tại sao đây là thiết kế tốt hơn?

Parser cũ:

```text
parse_listing()
 ├── tìm node
 ├── lấy text
 ├── kiểm tra None
 ├── lấy attribute
 ├── kiểm tra None
 ├── resolve URL
 └── tạo domain
```

Parser mới:

```text
parse_listing()
 ├── tìm node
 ├── required_text()
 ├── required_text()
 ├── required_attribute()
 ├── resolve URL
 └── tạo domain
```

Parser đọc rõ hơn.

---

# 21. Test Helpers

Tạo:

```text
tests/parser/test_helpers.py
```

```python
from selectolax.parser import HTMLParser

from crawler.infrastructure.parser.helpers import (
    get_text,
    get_attribute,
)


def test_get_text():

    tree = HTMLParser(
        "<h1>  Hello World  </h1>"
    )

    node = tree.css_first("h1")

    assert get_text(node) == "Hello World"


def test_get_text_missing_node():

    assert get_text(None) is None


def test_get_text_empty():

    tree = HTMLParser(
        "<h1>   </h1>"
    )

    node = tree.css_first("h1")

    assert get_text(node) is None


def test_get_attribute():

    tree = HTMLParser(
        '<a href="/book/1">Book</a>'
    )

    node = tree.css_first("a")

    assert (
        get_attribute(node, "href")
        == "/book/1"
    )


def test_get_attribute_missing():

    tree = HTMLParser(
        "<a>Book</a>"
    )

    node = tree.css_first("a")

    assert (
        get_attribute(node, "href")
        is None
    )
```

---

# 22. Test Required Field

```python
import pytest

from selectolax.parser import HTMLParser

from crawler.domain.parser_error import (
    MissingFieldError,
)

from crawler.infrastructure.parser.required import (
    required_text,
)


def test_required_text_success():

    tree = HTMLParser(
        "<h1>Hello</h1>"
    )

    node = tree.css_first("h1")

    result = required_text(
        node,
        field="title",
        selector="h1",
    )

    assert result == "Hello"


def test_required_text_missing():

    with pytest.raises(MissingFieldError):

        required_text(
            None,
            field="title",
            selector="h1",
        )
```

---

# 23. Một câu hỏi kiến trúc rất quan trọng

Tại sao không làm:

```python
class NovelSummary:
    @classmethod
    def from_html(cls, node):
        ...
```

?

Ví dụ:

```python
NovelSummary.from_html(node)
```

Nhìn có vẻ tiện.

Nhưng nó khiến Domain biết:

```text
HTML
Selectolax Node
CSS selector
```

và Domain trở nên phụ thuộc Infrastructure.

Kiến trúc đúng:

```text
Selectolax Node
      ↓
Parser
      ↓
NovelSummary
```

không phải:

```text
Selectolax Node
      ↓
NovelSummary
```

---

# 24. Một câu hỏi khác: tại sao không trả Dictionary?

Có thể viết:

```python
return {
    "title": title,
    "author": author,
    "url": url,
}
```

nhưng khi application lớn dần:

```python
item["title"]
item["author"]
item["url"]
```

sẽ rất dễ typo:

```python
item["titel"]
```

Domain Model giúp type checker và IDE hỗ trợ:

```python
item.title
item.author
item.url
```

Đồng thời domain model có semantic rõ ràng.

---

# 25. Kết quả sau Buổi 7

Kiến trúc hiện tại:

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
               create_context()
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 SelectolaxDocument          UrlResolver
          │                       │
          └──────────┬────────────┘
                     ▼
              ParserContext
                     │
                     ▼
               HTML extraction
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
        title      author       href
          │          │           │
          ▼          ▼           ▼
      required    required    required
          │          │           │
          └──────────┼───────────┘
                     ▼
               NovelSummary
                     │
                     ▼
                ListingPage
                     │
                     ▼
                  next_url
```

---

# 26. Roadmap

Chúng ta đã hoàn thành:

```text
01 Architecture                    ✅
02 Selectolax Foundation           ✅
03 Parser Interface                ✅
04 ParseResult + Validation        ✅
05 Domain Model                    ✅
06 BaseSiteParser + URL Resolver   ✅
07 Listing Models + Helpers        ✅
```

Tiếp theo:

## **Buổi 8 — Parse Listing: Extract Novel Cards**

Chúng ta sẽ bắt đầu **parse-listing thực chiến**:

```text
HTML
 │
 ├── story 1
 │     ├── title
 │     ├── author
 │     └── url
 │
 ├── story 2
 │     ├── title
 │     ├── author
 │     └── url
 │
 └── story 3
       ├── title
       ├── author
       └── url
```

và đặc biệt sẽ thiết kế:

```text
ListingParser
      ↓
extract_story()
      ↓
NovelSummary
```

để parser không trở thành một `parse_listing()` khổng lồ. Sau đó **Buổi 9** mới xử lý pagination `trang-2`, `trang-3` một cách bài bản.
