# Buổi 8 — Parse Listing: Extract Novel Cards

Hôm nay chúng ta bắt đầu phần **parse-listing thực chiến**.

Ở các buổi trước, ta đã xây nền:

```text
Buổi 1  Architecture
Buổi 2  Selectolax
Buổi 3  Parser Interface
Buổi 4  ParseResult + Error
Buổi 5  Domain Model
Buổi 6  BaseSiteParser + URL Resolver
Buổi 7  Listing Model + Helpers
```

Hôm nay tập trung đúng một vấn đề:

> **Làm thế nào biến từng “novel card” trong HTML thành `NovelSummary` một cách sạch sẽ.**

Chưa xử lý pagination sâu; phần đó để **Buổi 9**.

---

# 1. Mục tiêu

Giả sử listing HTML:

```html
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
```

Ta muốn:

```text
HTML card
    ↓
extract_novel()
    ↓
NovelSummary
```

Kết quả:

```python
NovelSummary(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="https://example.com/truyen/dau-pha-thuong-khung",
)
```

---

# 2. Tại sao cần `extract_novel()`?

Một cách viết không tốt:

```python
def parse_listing(...):

    for story in stories:
        title_node = ...
        author_node = ...
        href = ...

        ...
        
        items.append(
            NovelSummary(...)
        )
```

Khi website phức tạp hơn, `parse_listing()` sẽ nhanh chóng thành:

```text
parse_listing()
 ├── tìm card
 ├── parse title
 ├── parse author
 ├── parse url
 ├── parse cover
 ├── parse status
 ├── parse description
 ├── xử lý HTML lỗi
 ├── xử lý selector thay thế
 └── pagination
```

Rất khó test.

Ta tách:

```text
parse_listing()
    │
    ├── tìm tất cả card
    │
    ├── extract_novel(card)
    │
    └── extract_next_url()
```

Đây là decomposition rất quan trọng.

---

# 3. Kiến trúc

```text
TruyenFullListingParser
│
├── parse_listing()
│
├── extract_novel()
│
└── extract_next_url()
```

Hôm nay:

```text
parse_listing()
      │
      ▼
extract_novel()
      │
      ▼
NovelSummary
```

Buổi 9:

```text
parse_listing()
      │
      ├── extract_novel()
      │
      └── extract_next_url()
```

---

# 4. Domain Model

Ta giữ Domain Model rất sạch:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str
```

Parser biết cách tạo object:

```python
NovelSummary(...)
```

nhưng `NovelSummary` không biết HTML.

---

# 5. Tạo một Extractor riêng

Có hai cách.

### Cách A

Để:

```python
extract_novel()
```

ngay trong parser.

### Cách B

Tạo:

```text
NovelCardExtractor
```

Tại giai đoạn hiện tại, tôi khuyên dùng **Cách A**.

Vì nếu tạo quá nhiều class ngay từ đầu:

```text
ListingParser
NovelCardExtractor
TitleExtractor
AuthorExtractor
UrlExtractor
PaginationExtractor
...
```

thì abstraction sẽ quá sớm.

Ta bắt đầu đơn giản:

```python
class TruyenFullListingParser(BaseSiteParser):
    ...
```

---

# 6. Code hoàn chỉnh

File:

```text
src/crawler/infrastructure/parser/plugins/truyenfull/listing.py
```

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

        return ListingPage(
            items=items,
            next_url=None,
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
```

Đây chính là cấu trúc chúng ta muốn.

---

# 7. Đọc `parse_listing()`

Bây giờ `parse_listing()` rất dễ đọc:

```python
def parse_listing(...):

    context = self.create_context(...)

    stories = context.document.all(
        self.STORY_SELECTOR
    )

    items = []

    for story in stories:

        novel = self.extract_novel(
            story,
            context,
        )

        items.append(novel)

    return ListingPage(
        items=items,
        next_url=None,
    )
```

Nó chỉ chịu trách nhiệm:

1. tạo context
2. lấy danh sách card
3. gọi extractor
4. tạo `ListingPage`

Nó **không cần biết chi tiết** title nằm ở đâu.

---

# 8. Đọc `extract_novel()`

Ngược lại, `extract_novel()` chỉ quan tâm **một card**:

```text
story
 │
 ├── title
 ├── author
 └── href
```

Sau đó:

```text
title + author + url
        ↓
NovelSummary
```

Đây là SRP rất rõ.

---

# 9. `extract_novel()` không nhận HTML

Một điểm rất quan trọng.

Ta không viết:

```python
def extract_novel(
    page_source: str
):
```

vì nó sẽ phải parse lại toàn bộ HTML.

Ta truyền:

```python
story
```

là node của **một card**.

```python
def extract_novel(
    self,
    story,
    context,
)
```

Như vậy Selectolax chỉ tìm trong phạm vi card:

```text
<div class="story">
    ← story
    ├── title
    └── author
</div>
```

Thay vì toàn bộ document.

---

# 10. Tại sao phải tìm selector bên trong `story`?

Không nên:

```python
title_nodes = document.all(
    ".story-title a"
)
```

rồi:

```python
author_nodes = document.all(
    ".story-author"
)
```

Sau đó ghép:

```python
title_nodes[0]
author_nodes[0]
```

Cách này rất dễ sai khi HTML bị thiếu hoặc thay đổi.

Ví dụ:

```text
Story 1
  title
  author

Story 2
  title
  thiếu author

Story 3
  title
  author
```

Các list sẽ không còn cùng index.

Cách đúng:

```python
for story in stories:

    title = story.css_first(...)
    author = story.css_first(...)
```

Tức là:

> **Extract tất cả field trong cùng một aggregate HTML node.**

---

# 11. Ví dụ lỗi index

Giả sử:

```html
<div class="story">
    <a class="title">Novel A</a>
    <span class="author">Author A</span>
</div>

<div class="story">
    <a class="title">Novel B</a>
</div>

<div class="story">
    <a class="title">Novel C</a>
    <span class="author">Author C</span>
</div>
```

Nếu lấy riêng:

```python
titles = document.css(".title")
authors = document.css(".author")
```

ta có:

```text
titles:
0 A
1 B
2 C

authors:
0 A
1 C
```

Nếu ghép index:

```python
titles[1] + authors[1]
```

sẽ biến thành:

```text
Novel B + Author C
```

**Sai dữ liệu nghiêm trọng.**

Cách card-scoped:

```python
for story in stories:
    title = story.css_first(".title")
    author = story.css_first(".author")
```

thì Story B sẽ phát hiện:

```text
author = None
```

và `required_text()` raise lỗi.

Đây là lý do pattern này rất quan trọng.

---

# 12. Test `extract_novel()` độc lập

Đây là lợi ích lớn nhất của việc tách method.

Ta có thể test chỉ một card.

```python
from selectolax.parser import HTMLParser

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)
from crawler.infrastructure.parser.context import (
    ParserContext,
)
from crawler.infrastructure.parser.selectolax_document import (
    SelectolaxDocument,
)
from crawler.infrastructure.parser.url_resolver import (
    UrlResolver,
)

from crawler.infrastructure.parser.plugins.truyenfull.listing import (
    TruyenFullListingParser,
)


def test_extract_novel():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/truyen/test">
                Test Novel
            </a>
        </h3>

        <span class="story-author">
            Test Author
        </span>

    </div>
    """

    parser = TruyenFullListingParser()

    document = SelectolaxDocument(html)

    context = ParserContext(
        url="https://example.com/truyen",
        document=document,
        url_resolver=UrlResolver(
            "https://example.com/truyen"
        ),
    )

    story = document.first(
        ".story"
    )

    result = parser.extract_novel(
        story,
        context,
    )

    assert result.title == "Test Novel"

    assert result.author == "Test Author"

    assert (
        result.url
        == "https://example.com/truyen/test"
    )
```

---

# 13. Nhưng có thể test đơn giản hơn

Không nhất thiết phải tự tạo `ParserContext` trong mọi test.

Có thể test thông qua public API:

```python
result = parser.parse_listing(
    HTML,
    "https://example.com/truyen",
)
```

và kiểm tra:

```python
assert result.items[0].title == "..."
```

Đây là **integration-ish test** cho parser.

Còn test `extract_novel()` là **unit test**.

Hai loại đều hữu ích.

---

# 14. Test field bị thiếu

Đây là test rất quan trọng.

```python
import pytest

from crawler.domain.parser_error import (
    MissingFieldError,
)

from crawler.infrastructure.parser.plugins.truyenfull.listing import (
    TruyenFullListingParser,
)


def test_missing_author():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/truyen/test">
                Test Novel
            </a>
        </h3>

    </div>
    """

    parser = TruyenFullListingParser()

    with pytest.raises(MissingFieldError):

        parser.parse_listing(
            html,
            "https://example.com/truyen",
        )
```

Parser không làm:

```python
author = ""
```

mà phát hiện:

```text
Required field 'author' is missing
```

---

# 15. Test URL tương đối

```python
def test_relative_url():

    html = """
    <div class="story">

        <h3 class="story-title">
            <a href="/truyen/test">
                Test Novel
            </a>
        </h3>

        <span class="story-author">
            Author
        </span>

    </div>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    novel = result.items[0]

    assert (
        novel.url
        == "https://example.com/truyen/test"
    )
```

---

# 16. Test nhiều card

```python
def test_multiple_cards():

    html = """
    <div class="story">
        <h3 class="story-title">
            <a href="/book/1">Book 1</a>
        </h3>
        <span class="story-author">Author 1</span>
    </div>

    <div class="story">
        <h3 class="story-title">
            <a href="/book/2">Book 2</a>
        </h3>
        <span class="story-author">Author 2</span>
    </div>

    <div class="story">
        <h3 class="story-title">
            <a href="/book/3">Book 3</a>
        </h3>
        <span class="story-author">Author 3</span>
    </div>
    """

    parser = TruyenFullListingParser()

    result = parser.parse_listing(
        html,
        "https://example.com/truyen",
    )

    assert len(result.items) == 3

    assert result.items[0].title == "Book 1"
    assert result.items[1].title == "Book 2"
    assert result.items[2].title == "Book 3"
```

---

# 17. Một vấn đề thực tế: khoảng trắng

HTML thực tế thường rất xấu:

```html
<h3 class="story-title">
    
    <a href="/book/1">

        Đấu Phá Thương Khung

    </a>

</h3>
```

Helper:

```python
get_text(node)
```

đã xử lý:

```python
text = node.text().strip()
```

nên kết quả:

```text
Đấu Phá Thương Khung
```

Đây là lý do chúng ta không nên để từng parser tự `.strip()` lung tung.

---

# 18. Một vấn đề khác: HTML entity

Ví dụ:

```html
<a>
    Harry &amp; Potter
</a>
```

DOM parser sẽ xử lý HTML entity khi lấy text theo cách phù hợp, để parser làm việc với nội dung văn bản thay vì raw markup.

Do đó parser của chúng ta không nên tự viết:

```python
html.unescape(...)
```

trừ khi có một trường hợp site-specific thực sự cần.

**Đừng xử lý những thứ Selectolax đã xử lý.**

---

# 19. Không nên tạo quá nhiều abstraction

Có thể bạn sẽ nghĩ:

```text
NovelTitleExtractor
NovelAuthorExtractor
NovelUrlExtractor
NovelCardExtractor
NovelSummaryFactory
ListingItemMapper
```

Ngay lập tức.

Không nên.

Hiện tại:

```text
TruyenFullListingParser
    ├── parse_listing()
    └── extract_novel()
```

là đủ.

Khi thấy một abstraction thực sự có lý do tồn tại, ta mới tách.

Đây là nguyên tắc:

> **Abstraction should follow duplication and responsibility, not imagination.**

---

# 20. `extract_novel()` có phải Domain Service không?

**Không.**

Nó đang làm:

```text
HTML Node
 ↓
Domain Object
```

Đây là Infrastructure Parser logic.

Vì vậy nó nằm trong:

```text
infrastructure/parser/plugins/truyenfull/
```

Không nằm trong:

```text
domain/
```

---

# 21. Dependency Direction

Hiện tại dependency:

```text
TruyenFullListingParser
        │
        ├── Domain
        │    └── NovelSummary
        │
        └── Parser Infrastructure
             ├── Selectolax
             ├── Context
             └── URL Resolver
```

Domain không phụ thuộc parser.

Đây là hướng dependency chúng ta muốn:

```text
Infrastructure
      ↓
Domain
```

chứ không:

```text
Domain
   ↓
Selectolax
```

---

# 22. `parse_listing()` hiện tại

Ta có:

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

    items = []

    for story in stories:

        novel = self.extract_novel(
            story,
            context,
        )

        items.append(novel)

    return ListingPage(
        items=items,
        next_url=None,
    )
```

Hãy để ý:

**Nó chưa biết pagination.**

Đây là chủ ý.

Buổi 8 tập trung:

```text
listing → novel cards
```

Buổi 9 tập trung:

```text
listing → pagination
```

---

# 23. Một cải tiến nhỏ: type alias

Hiện tại:

```python
def extract_novel(
    self,
    story,
    context,
)
```

type của `story` chưa rõ.

Selectolax có type riêng tùy phiên bản/API. Chúng ta **không nên kéo type đó vào Domain/Application**, nhưng trong Infrastructure hoàn toàn có thể annotate khi cần.

Ở giai đoạn này, tôi khuyên chưa làm quá phức tạp. Sau khi parser structure ổn định, ta sẽ quay lại typing ở một buổi production-hardening.

---

# 24. Nguyên tắc cốt lõi của Buổi 8

Hãy nhớ pattern:

```text
Document
   │
   ▼
find item nodes
   │
   ▼
for each item
   │
   ▼
extract item
   │
   ├── required title
   ├── required author
   └── required URL
   │
   ▼
Domain Model
```

Không làm:

```text
Document
   ├── tất cả title
   ├── tất cả author
   └── tất cả URL
           ↓
       ghép index
```

**Card-scoped extraction** là pattern rất quan trọng cho crawler.

---

# 25. Cấu trúc hiện tại

Sau Buổi 8:

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
            ├── helpers.py
            ├── required.py
            ├── url_resolver.py
            ├── selectolax_document.py
            │
            └── plugins/
                └── truyenfull/
                    └── listing.py
```

Trong `listing.py`:

```text
TruyenFullListingParser
│
├── parse_listing()
│
└── extract_novel()
```

---

# 26. Roadmap

Đã hoàn thành:

```text
01 Architecture                    ✅
02 Selectolax Foundation           ✅
03 Parser Interface                ✅
04 ParseResult + Validation        ✅
05 Domain Model                    ✅
06 BaseSiteParser + URL Resolver   ✅
07 Listing Models + Helpers        ✅
08 Extract Novel Cards             ✅
```

## Buổi 9 — Listing Pagination

Chúng ta sẽ xử lý phần còn thiếu:

```text
HTML
 │
 ├── Novel 1
 ├── Novel 2
 ├── Novel 3
 │
 └── Pagination
       ├── 1
       ├── 2
       ├── 3
       └── Next
```

Thiết kế:

```text
parse_listing()
      │
      ├── extract_novel()
      │
      └── extract_next_url()
```

và xử lý được các dạng:

```text
<a href="/truyen?page=2">
<a class="next" href="/truyen?page=2">
<a rel="next" href="/truyen?page=2">
<a href="/truyen/trang-2">
```

quan trọng nhất là **parser chỉ trả `next_url`; Application/HTTPX mới chịu trách nhiệm fetch trang tiếp theo**.
