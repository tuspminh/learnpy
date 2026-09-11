# Phần IV — Novel Parser

# Buổi 13 — Parse Novel Detail

Sau khi hoàn thành **Listing Parser**, chúng ta chuyển sang một tầng quan trọng hơn:

```text id="w9qv3p"
Listing Page
    ↓
NovelSummary
    ├── title
    ├── author
    └── url

        ↓ click/fetch

Novel Detail Page
    ↓
Novel
    ├── title
    ├── author
    ├── url
    ├── cover
    ├── description
    └── status
```

Mục tiêu Buổi 13 chỉ tập trung vào **Novel Detail cơ bản**.

Chưa tách metadata thành nhiều extractor — phần đó là **Buổi 14**.

---

# 1. Mục tiêu

Input:

```python id="x3c9d1"
page_source: str
url: str
```

Output:

```python id="1t8y6k"
Novel(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="https://example.com/dau-pha-thuong-khung",
    cover="https://example.com/images/dptk.jpg",
    description="...",
    status="Đang ra",
)
```

Tức là:

```text id="7r4p8m"
page_source
     │
     ▼
Selectolax
     │
     ▼
Novel Parser
     │
     ▼
Novel
```

---

# 2. Domain Model

Chúng ta đã tạo từ Buổi 5:

```python id="lq2d6f"
from dataclasses import dataclass


@dataclass
class Novel:
    title: str

    author: str

    url: str

    cover: str | None = None

    description: str | None = None

    status: str | None = None
```

Điểm quan trọng:

```text id="c3z0qf"
title       required
author      required
url         required

cover       optional
description optional
status      optional
```

---

# 3. Novel Parser khác Listing Parser

Listing:

```text id="7k6b5n"
HTML
 ↓
nhiều card
 ↓
NovelSummary[]
```

Novel detail:

```text id="0drxq8"
HTML
 ↓
một novel
 ↓
Novel
```

Đừng nhầm:

```python id="3cq2bb"
list[NovelSummary]
```

với:

```python id="4ikg8u"
Novel
```

---

# 4. Kiến trúc

Ta có:

```text id="w8r3yz"
HTTPX
  │
  │ page_source
  ▼
NovelParser
  │
  ▼
ParserContext
  │
  ▼
Selectolax DOM
  │
  ├── title
  ├── author
  ├── cover
  ├── description
  └── status
  │
  ▼
Novel
```

HTTPX vẫn hoàn toàn nằm ngoài parser.

---

# 5. Không bắt đầu bằng 5 extractor

Roadmap của bạn rất đúng:

> Buổi 14 mới tách `TitleExtractor`, `AuthorExtractor`, `CoverExtractor`,...

Trong Buổi 13, ta **chưa làm vậy**.

Tại sao?

Nếu ngay lập tức:

```text id="h8g3c1"
NovelParser
    ↓
TitleExtractor
AuthorExtractor
CoverExtractor
DescriptionExtractor
StatusExtractor
```

thì với một parser đơn giản chúng ta có:

```text
1 parser
5 classes
5 files
5 interfaces?
```

Đây có thể là overengineering.

Buổi 13 trước tiên xây một parser rõ ràng.

---

# 6. Ví dụ HTML

Giả sử website có:

```html id="x2p7vk"
<div class="book-detail">

    <h1 class="book-title">
        Đấu Phá Thương Khung
    </h1>

    <div class="book-author">
        Thiên Tằm Thổ Đậu
    </div>

    <div class="book-cover">
        <img
            src="/images/dptk.jpg"
            alt="Đấu Phá Thương Khung"
        >
    </div>

    <div class="book-description">
        Đây là phần giới thiệu truyện.
    </div>

    <div class="book-status">
        Đang ra
    </div>

</div>
```

Parser phải biến thành:

```python id="g9j2lm"
Novel(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="https://example.com/dau-pha-thuong-khung",
    cover="https://example.com/images/dptk.jpg",
    description="Đây là phần giới thiệu truyện.",
    status="Đang ra",
)
```

---

# 7. Selector là infrastructure concern

Các selector:

```python id="b1o4tq"
TITLE_SELECTOR = ".book-title"

AUTHOR_SELECTOR = ".book-author"

COVER_SELECTOR = ".book-cover img"

DESCRIPTION_SELECTOR = ".book-description"

STATUS_SELECTOR = ".book-status"
```

không được đưa vào Domain.

Domain không biết:

```css id="v6ghh8"
.book-title
.book-author
.book-cover img
```

---

# 8. Tạo `novel.py`

Cấu trúc:

```text id="n0b5r4"
plugins/
└── truyenfull/
    ├── listing.py
    ├── novel_card.py
    └── novel.py
```

`novel.py`:

```python id="s3j8yn"
from crawler.domain.novel import Novel
from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)
from crawler.infrastructure.parser.context import (
    ParserContext,
)
from crawler.infrastructure.parser.helpers import (
    get_attribute,
)
from crawler.infrastructure.parser.required import (
    required_text,
)


class TruyenFullNovelParser(BaseSiteParser):
    TITLE_SELECTOR = ".book-title"

    AUTHOR_SELECTOR = ".book-author"

    COVER_SELECTOR = ".book-cover img"

    DESCRIPTION_SELECTOR = ".book-description"

    STATUS_SELECTOR = ".book-status"

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> Novel:

        context = self.create_context(
            page_source,
            url,
        )

        title = self.extract_title(context)

        author = self.extract_author(context)

        cover = self.extract_cover(context)

        description = self.extract_description(context)

        status = self.extract_status(context)

        return Novel(
            title=title,
            author=author,
            url=url,
            cover=cover,
            description=description,
            status=status,
        )
```

---

# 9. Extract title

Title là required.

```python id="tr0f7u"
def extract_title(
    self,
    context: ParserContext,
) -> str:

    node = context.document.first(self.TITLE_SELECTOR)

    return required_text(
        node,
        field="title",
        selector=self.TITLE_SELECTOR,
    )
```

Nếu HTML:

```html id="v1g6pm"
<h1 class="book-title">
    Đấu Phá Thương Khung
</h1>
```

→

```text id="e0d0jq"
"Đấu Phá Thương Khung"
```

---

# 10. Extract author

Tương tự:

```python id="6ceq9w"
def extract_author(
    self,
    context: ParserContext,
) -> str:

    node = context.document.first(self.AUTHOR_SELECTOR)

    return required_text(
        node,
        field="author",
        selector=self.AUTHOR_SELECTOR,
    )
```

---

# 11. Cover là optional

Cover có thể không tồn tại:

```html id="r7b0bh"
<div class="book-cover">
</div>
```

Không nên:

```python id="9s4x51"
required_attribute(...)
```

vì cover là optional.

Ta dùng:

```python id="ecb6s5"
def extract_cover(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(self.COVER_SELECTOR)

    if node is None:
        return None

    src = get_attribute(
        node,
        "src",
    )

    if src is None:
        return None

    return context.resolve_url(src)
```

---

# 12. Tại sao phải resolve cover URL?

HTML:

```html id="x7y0qt"
<img src="/images/book.jpg">
```

Không nên lưu:

```text id="8zyrgo"
/images/book.jpg
```

Domain nên nhận URL hoàn chỉnh:

```text id="5m0fqa"
https://example.com/images/book.jpg
```

Do đó:

```python id="j7j4hm"
context.resolve_url(src)
```

---

# 13. Description là optional

```python id="1u3l7r"
def extract_description(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(self.DESCRIPTION_SELECTOR)

    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

Ví dụ:

```html id="43f0e8"
<div class="book-description">
    Đây là phần giới thiệu truyện.
</div>
```

→:

```text id="5s0i8g"
"Đây là phần giới thiệu truyện."
```

---

# 14. Status cũng optional

```python id="b7h8yl"
def extract_status(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(self.STATUS_SELECTOR)

    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

---

# 15. Full parser

Bây giờ ghép lại:

```python id="j6wq3s"
from crawler.domain.novel import Novel

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from crawler.infrastructure.parser.required import (
    required_text,
)


class TruyenFullNovelParser(BaseSiteParser):
    TITLE_SELECTOR = ".book-title"

    AUTHOR_SELECTOR = ".book-author"

    COVER_SELECTOR = ".book-cover img"

    DESCRIPTION_SELECTOR = ".book-description"

    STATUS_SELECTOR = ".book-status"

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> Novel:

        context = self.create_context(
            page_source,
            url,
        )

        title = self.extract_title(context)

        author = self.extract_author(context)

        cover = self.extract_cover(context)

        description = self.extract_description(context)

        status = self.extract_status(context)

        return Novel(
            title=title,
            author=author,
            url=url,
            cover=cover,
            description=description,
            status=status,
        )

    def extract_title(
        self,
        context: ParserContext,
    ) -> str:

        node = context.document.first(self.TITLE_SELECTOR)

        return required_text(
            node,
            field="title",
            selector=self.TITLE_SELECTOR,
        )

    def extract_author(
        self,
        context: ParserContext,
    ) -> str:

        node = context.document.first(self.AUTHOR_SELECTOR)

        return required_text(
            node,
            field="author",
            selector=self.AUTHOR_SELECTOR,
        )

    def extract_cover(
        self,
        context: ParserContext,
    ) -> str | None:

        node = context.document.first(self.COVER_SELECTOR)

        if node is None:
            return None

        src = get_attribute(
            node,
            "src",
        )

        if src is None:
            return None

        return context.resolve_url(src)

    def extract_description(
        self,
        context: ParserContext,
    ) -> str | None:

        node = context.document.first(self.DESCRIPTION_SELECTOR)

        if node is None:
            return None

        text = node.text().strip()

        return text or None

    def extract_status(
        self,
        context: ParserContext,
    ) -> str | None:

        node = context.document.first(self.STATUS_SELECTOR)

        if node is None:
            return None

        text = node.text().strip()

        return text or None
```

---

# 16. Một điểm cần chú ý: `url`

Ta nhận:

```python id="u6t5nj"
url: str
```

từ caller.

Không cần tìm:

```html
<link rel="canonical">
```

ở Buổi 13.

Ta coi:

```text id="3f9f0r"
url
```

là URL mà Application dùng để fetch trang.

Ví dụ:

```python id="5n8q2k"
parser.parse_novel(
    page_source,
    "https://example.com/book/a",
)
```

thì:

```python id="3hq5qp"
novel.url
```

là:

```text
https://example.com/book/a
```

---

# 17. Vì sao chưa parse canonical URL?

Website có thể có:

```html id="c7txz9"
<link
    rel="canonical"
    href="https://example.com/book/a"
/>
```

Nhưng canonical URL là một vấn đề riêng:

```text id="n7s0yb"
URL identity
canonicalization
redirect
duplicate URL
```

Sau này có thể thiết kế `UrlResolver`/URL policy riêng.

Buổi 13 không cần làm phức tạp.

---

# 18. Test cơ bản

Tạo:

```text id="u8y6bq"
tests/
└── infrastructure/
    └── parser/
        └── truyenfull/
            └── test_novel.py
```

Test:

```python id="4f6y9j"
from crawler.infrastructure.parser.plugins.truyenfull.novel import (
    TruyenFullNovelParser,
)


def test_parse_novel():

    html = """
    <html>
        <body>

            <div class="book-detail">

                <h1 class="book-title">
                    Đấu Phá Thương Khung
                </h1>

                <div class="book-author">
                    Thiên Tằm Thổ Đậu
                </div>

                <div class="book-cover">

                    <img
                        src="/images/dptk.jpg"
                    >

                </div>

                <div class="book-description">
                    Đây là phần giới thiệu truyện.
                </div>

                <div class="book-status">
                    Đang ra
                </div>

            </div>

        </body>
    </html>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/dptk",
    )

    assert result.title == ("Đấu Phá Thương Khung")

    assert result.author == ("Thiên Tằm Thổ Đậu")

    assert result.url == ("https://example.com/dptk")

    assert result.cover == ("https://example.com/images/dptk.jpg")

    assert result.description == ("Đây là phần giới thiệu truyện.")

    assert result.status == "Đang ra"
```

---

# 19. Test optional fields

Đây là test bắt buộc.

```python id="8ljztt"
def test_optional_metadata():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/book/a",
    )

    assert result.title == "Novel A"

    assert result.author == "Author A"

    assert result.cover is None

    assert result.description is None

    assert result.status is None
```

Điều này chứng minh:

```text id="6s5qaj"
optional field missing
        ↓
None
```

không phải:

```text id="zq4z4h"
ParserError
```

---

# 20. Test thiếu title

```python id="9kwm7c"
import pytest

from crawler.domain.parser_error import (
    MissingFieldError,
)


def test_missing_title():

    html = """
    <div class="book-author">
        Author A
    </div>
    """

    parser = TruyenFullNovelParser()

    with pytest.raises(MissingFieldError):
        parser.parse_novel(
            html,
            "https://example.com/book/a",
        )
```

---

# 21. Test thiếu author

```python id="9uwv2g"
def test_missing_author():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>
    """

    parser = TruyenFullNovelParser()

    with pytest.raises(MissingFieldError):
        parser.parse_novel(
            html,
            "https://example.com/book/a",
        )
```

---

# 22. Test cover relative URL

```python id="3j5m3p"
def test_cover_relative_url():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>

    <div class="book-cover">
        <img src="images/a.jpg">
    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/books/",
    )

    assert result.cover == ("https://example.com/books/images/a.jpg")
```

---

# 23. Test cover absolute URL

```python id="o4i2bm"
def test_cover_absolute_url():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>

    <div class="book-cover">
        <img
            src="https://cdn.example.com/a.jpg"
        >
    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/books/a",
    )

    assert result.cover == ("https://cdn.example.com/a.jpg")
```

---

# 24. Tại sao `cover` không dùng `required_attribute()`?

Vì:

```text id="b7f7yu"
Novel
├── title       required
├── author      required
├── url         required
│
├── cover       optional
├── description optional
└── status      optional
```

Nếu:

```html id="t7x9q2"
<div class="book-cover"></div>
```

thì:

```python id="b9q1v3"
cover = None
```

là hợp lệ.

---

# 25. Một vấn đề thực tế: Description có HTML

Ví dụ:

```html id="v4y8wb"
<div class="book-description">

    <p>Novel này kể về...</p>

    <p>Nhân vật chính...</p>

</div>
```

Nếu dùng:

```python id="qj7s4m"
node.text()
```

ta lấy plain text.

Ở Buổi 13 chúng ta **chưa xử lý HTML description nâng cao**.

Sau này có thể cần:

```text id="f6c7se"
HTML description
       ↓
cleaner
       ↓
Markdown/text
```

Đó là concern riêng.

Không nhét `html2text` vào Novel Parser lúc này.

---

# 26. Một nguyên tắc quan trọng về abstraction

Hiện tại chúng ta có:

```text id="m4g8u9"
TruyenFullNovelParser
    ├── extract_title()
    ├── extract_author()
    ├── extract_cover()
    ├── extract_description()
    └── extract_status()
```

Có người sẽ nói:

> "Mỗi method là một responsibility, phải tạo 5 class."

Không nhất thiết.

SRP nói về **trách nhiệm thay đổi**, không phải số lượng method.

Nếu tất cả selector của metadata cùng thay đổi vì:

```text id="n1i0w5"
TruyenFull HTML layout thay đổi
```

thì chúng vẫn thuộc cùng một nhóm trách nhiệm:

> Parse Novel Detail của TruyenFull.

Do đó class hiện tại hoàn toàn hợp lý.

---

# 27. Khi nào mới nên tách Extractor?

Ví dụ sau này:

```text id="6ql4y5"
TitleExtractor
```

được dùng bởi:

```text
NovelParser
ListingParser
SearchParser
RelatedNovelParser
```

hoặc:

```text
CoverExtractor
```

có logic phức tạp:

```text
data-src
src
data-original
picture source
lazy loading
CDN URL
```

lúc đó abstraction có giá trị.

Không phải:

```text
1 field
1 class
```

một cách máy móc.

Đây chính xác là tinh thần roadmap bạn đưa ra ở **Buổi 14**.

---

# 28. Parser Interface

Ta đã có:

```python id="k5gy0p"
class NovelParser(Protocol):
    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage: ...
```

Ở Buổi 3 chúng ta thiết kế `NovelParser` trả `NovelPage`.

Nhưng hôm nay yêu cầu Buổi 13 của roadmap là:

```text id="h9m2ka"
parse_novel()
    ↓
Novel
```

Có một điểm cần thống nhất kiến trúc.

Nếu Novel Parser cuối cùng phải bao gồm:

```text id="1pxyvn"
Novel
 +
ChapterSummary[]
 +
next_url
```

thì API cuối cùng nên là:

```python id="s2x1a4"
NovelPage
```

nhưng **Buổi 13 chỉ parse metadata Novel**.

Vì vậy ở tầng implementation hôm nay ta có thể dùng:

```python id="yj6k4n"
def parse_novel(...) -> Novel
```

Sau khi đến Buổi 15–17, chúng ta sẽ nâng lên thành:

```text id="r2j7d9"
Novel Parser
    ↓
NovelPage
├── novel
├── chapters
└── next_url
```

Đây là tiến hóa tự nhiên, không phải thiết kế lại toàn bộ.

---

# 29. Flow sau Buổi 13

```text id="2a5f4e"
NovelSummary
     │
     │ url
     ▼
Application
     │
     │ fetch
     ▼
HTTPX
     │
     │ page_source
     ▼
TruyenFullNovelParser
     │
     ├── title
     ├── author
     ├── cover
     ├── description
     └── status
     │
     ▼
Novel
```

---

# 30. Phân chia trách nhiệm

| Thành phần           | Trách nhiệm           |
| -------------------- | --------------------- |
| HTTPX Fetcher        | Lấy HTML              |
| `SelectolaxDocument` | HTML → DOM            |
| `ParserContext`      | DOM + URL context     |
| `NovelParser`        | Điều phối parse novel |
| `required_text()`    | Required field        |
| `get_attribute()`    | Optional attribute    |
| `UrlResolver`        | Relative → absolute   |
| `Novel`              | Domain data           |
| Application          | Điều phối crawl       |
| Repository           | Lưu dữ liệu           |

---

# 31. Điều tuyệt đối không làm

Không viết:

```python id="kbrw5j"
class TruyenFullNovelParser:
    def parse_novel(self, url):

        response = httpx.get(url)

        ...
```

Sai architecture.

Phải là:

```python id="yqf70o"
response = fetcher.fetch(url)

novel = parser.parse_novel(
    response.text,
    url,
)
```

---

# 32. Cấu trúc hiện tại

Sau Buổi 13:

```text id="u1i5qg"
infrastructure/
└── parser/
    └── plugins/
        └── truyenfull/
            ├── listing.py
            ├── novel_card.py
            └── novel.py
```

Domain:

```text id="q4f8aj"
domain/
├── novel.py
├── chapter.py
├── parser_result.py
└── parser_error.py
```

---

# 33. Kiến thức chính của Buổi 13

Bạn cần nắm chắc 7 điểm:

### 1.

```text id="8yk2jw"
Listing → NovelSummary
Detail → Novel
```

### 2.

```text id="i8d6a1"
Required:
title
author
url
```

### 3.

```text id="l3w9b7"
Optional:
cover
description
status
```

### 4.

URL ảnh phải đi qua:

```python id="o7j7ba"
context.resolve_url()
```

### 5.

Parser chỉ nhận:

```python id="3t9u0e"
page_source + url
```

### 6.

Parser không HTTP/database.

### 7.

Chưa tách 5 extractor một cách máy móc.

---

# 34. Roadmap hiện tại

```text
Phần I — Foundation
01 Architecture                    ✅
02 Selectolax Foundation           ✅
03 Parser Interface                ✅
04 ParseResult + Validation        ✅

Phần II — Domain
05 Novel Domain Model              ✅
06 Chapter Domain Model            ✅
07 Listing Models                  ✅

Phần III — Listing Parser
08 Parse Novel Listing             ✅
09 Extract Novel Card              ✅
10 Listing Pagination              ✅
11 Pagination Robustness           ✅
12 Listing Parser hoàn chỉnh       ✅

Phần IV — Novel Parser
13 Parse Novel Detail              ✅ ← hôm nay
14 Novel Metadata Extractor        ⬜
15 Chapter Listing                 ⬜
16 Chapter Listing Pagination      ⬜
17 Novel Parser hoàn chỉnh         ⬜
```

## Buổi 14

Chúng ta sẽ lấy chính code hôm nay và **refactor có kiểm soát**:

```text id="s6j1ra"
TruyenFullNovelParser
        │
        ├── metadata
        │      ├── title
        │      ├── author
        │      ├── cover
        │      ├── description
        │      └── status
        │
        └── ?
```

Sau đó quyết định **cái gì đáng tách thành Extractor, cái gì không đáng tách**, sử dụng đúng **SRP + DIP + OCP**, thay vì biến parser thành hàng loạt class nhỏ chỉ để "đủ SOLID".
