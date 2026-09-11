# Phần IV — Novel Parser

# Buổi 14 — Novel Metadata Extractor

Hôm nay chúng ta refactor parser của Buổi 13 để xử lý **metadata extraction** sạch hơn.

Mục tiêu không phải là:

```text
1 field = 1 class
```

mà là:

> **Tách abstraction khi nó thực sự làm giảm coupling, tăng khả năng thay đổi và test.**

Cuối buổi ta sẽ có:

```text
Novel Parser
     │
     ▼
Novel Metadata
     │
     ├── title
     ├── author
     ├── cover
     ├── description
     └── status
```

và chuẩn bị rất tốt cho **Buổi 15 — Chapter Listing**.

---

# 1. Vấn đề của Buổi 13

Buổi 13 chúng ta có:

```python
class TruyenFullNovelParser:

    def extract_title(...)
    def extract_author(...)
    def extract_cover(...)
    def extract_description(...)
    def extract_status(...)
```

Code này **không sai**.

Thực tế với một website đơn giản, đây vẫn là thiết kế tốt.

Nhưng hãy tưởng tượng website trở nên phức tạp:

```text
Title
 ├── h1.book-title
 ├── h1.title
 └── meta[property="og:title"]

Cover
 ├── img.book-cover
 ├── img[data-src]
 ├── img[data-original]
 └── og:image

Description
 ├── .description
 ├── .book-description
 └── meta[name="description"]
```

Lúc này parser sẽ ngày càng phình to.

---

# 2. Mục tiêu của Buổi 14

Chúng ta muốn:

```text
TruyenFullNovelParser
        │
        ▼
NovelMetadataExtractor
        │
        ├── title
        ├── author
        ├── cover
        ├── description
        └── status
```

Nhưng **không nhất thiết**:

```text
TitleExtractor
AuthorExtractor
CoverExtractor
DescriptionExtractor
StatusExtractor
```

năm class riêng biệt.

---

# 3. Nguyên tắc SRP chính xác

Một hiểu lầm phổ biến:

> SRP = một class chỉ được có một method.

Không đúng.

SRP gần với:

> Một class nên có một lý do chính để thay đổi.

Ví dụ:

```text
TruyenFullNovelParser
```

có lý do thay đổi:

```text
"cách parse toàn bộ Novel Detail"
```

Còn:

```text
NovelMetadataExtractor
```

có lý do thay đổi:

```text
"cách trích xuất metadata của Novel"
```

Đây là boundary hợp lý.

---

# 4. Metadata Model

Trước tiên, ta có thể tạo một model trung gian.

`domain/novel.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str


@dataclass
class Novel:
    title: str
    author: str
    url: str
    cover: str | None = None
    description: str | None = None
    status: str | None = None
```

Có hai lựa chọn.

### Cách 1

Extractor trả thẳng:

```python
Novel
```

### Cách 2

Extractor trả:

```python
NovelMetadata
```

Tôi chọn **Cách 2**.

Tại sao?

Vì `Novel` còn có:

```text
url
chapters
domain identity
```

Trong khi metadata chỉ là:

```text
title
author
cover
description
status
```

---

# 5. Tạo `NovelMetadata`

Thêm:

```python
@dataclass(frozen=True)
class NovelMetadata:
    title: str
    author: str
    cover: str | None = None
    description: str | None = None
    status: str | None = None
```

File:

```text
domain/
└── novel.py
```

hoàn chỉnh:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str


@dataclass(frozen=True)
class NovelMetadata:
    title: str
    author: str
    cover: str | None = None
    description: str | None = None
    status: str | None = None


@dataclass
class Novel:
    title: str
    author: str
    url: str
    cover: str | None = None
    description: str | None = None
    status: str | None = None


@dataclass(frozen=True)
class ChapterSummary:
    title: str
    url: str
```

---

# 6. Tại sao `NovelMetadata` frozen?

Parser tạo ra:

```python
NovelMetadata(...)
```

Sau đó parser không cần thay đổi nó.

Vì vậy:

```python
@dataclass(frozen=True)
```

phù hợp.

Nó cũng giúp tránh việc extractor vô tình sửa metadata sau khi tạo.

---

# 7. `NovelMetadataExtractor`

Tạo:

```text
infrastructure/
└── parser/
    └── plugins/
        └── truyenfull/
            ├── listing.py
            ├── novel_card.py
            ├── novel.py
            └── metadata.py
```

`metadata.py`:

```python
from crawler.domain.novel import NovelMetadata

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from crawler.infrastructure.parser.required import (
    required_text,
)


class NovelMetadataExtractor:

    TITLE_SELECTOR = ".book-title"

    AUTHOR_SELECTOR = ".book-author"

    COVER_SELECTOR = ".book-cover img"

    DESCRIPTION_SELECTOR = ".book-description"

    STATUS_SELECTOR = ".book-status"

    def extract(
        self,
        context: ParserContext,
    ) -> NovelMetadata:

        title = self.extract_title(
            context
        )

        author = self.extract_author(
            context
        )

        cover = self.extract_cover(
            context
        )

        description = self.extract_description(
            context
        )

        status = self.extract_status(
            context
        )

        return NovelMetadata(
            title=title,
            author=author,
            cover=cover,
            description=description,
            status=status,
        )
```

---

# 8. Các field extractor vẫn là method

Đây là điểm quan trọng.

Chúng ta **không** làm:

```text
title.py
author.py
cover.py
description.py
status.py
```

mà:

```text
metadata.py
```

với:

```python
extract_title()
extract_author()
extract_cover()
extract_description()
extract_status()
```

Đây là abstraction vừa đủ.

---

# 9. `extract_title()`

```python
def extract_title(
    self,
    context: ParserContext,
) -> str:

    node = context.document.first(
        self.TITLE_SELECTOR
    )

    return required_text(
        node,
        field="title",
        selector=self.TITLE_SELECTOR,
    )
```

---

# 10. `extract_author()`

```python
def extract_author(
    self,
    context: ParserContext,
) -> str:

    node = context.document.first(
        self.AUTHOR_SELECTOR
    )

    return required_text(
        node,
        field="author",
        selector=self.AUTHOR_SELECTOR,
    )
```

---

# 11. `extract_cover()`

```python
def extract_cover(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(
        self.COVER_SELECTOR
    )

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

# 12. `extract_description()`

```python
def extract_description(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(
        self.DESCRIPTION_SELECTOR
    )

    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

---

# 13. `extract_status()`

```python
def extract_status(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(
        self.STATUS_SELECTOR
    )

    if node is None:
        return None

    text = node.text().strip()

    return text or None
```

---

# 14. Full `metadata.py`

Đây là file hoàn chỉnh:

```python
from crawler.domain.novel import NovelMetadata

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
)

from crawler.infrastructure.parser.required import (
    required_text,
)


class NovelMetadataExtractor:

    TITLE_SELECTOR = ".book-title"

    AUTHOR_SELECTOR = ".book-author"

    COVER_SELECTOR = ".book-cover img"

    DESCRIPTION_SELECTOR = ".book-description"

    STATUS_SELECTOR = ".book-status"

    def extract(
        self,
        context: ParserContext,
    ) -> NovelMetadata:

        title = self.extract_title(
            context
        )

        author = self.extract_author(
            context
        )

        cover = self.extract_cover(
            context
        )

        description = self.extract_description(
            context
        )

        status = self.extract_status(
            context
        )

        return NovelMetadata(
            title=title,
            author=author,
            cover=cover,
            description=description,
            status=status,
        )

    def extract_title(
        self,
        context: ParserContext,
    ) -> str:

        node = context.document.first(
            self.TITLE_SELECTOR
        )

        return required_text(
            node,
            field="title",
            selector=self.TITLE_SELECTOR,
        )

    def extract_author(
        self,
        context: ParserContext,
    ) -> str:

        node = context.document.first(
            self.AUTHOR_SELECTOR
        )

        return required_text(
            node,
            field="author",
            selector=self.AUTHOR_SELECTOR,
        )

    def extract_cover(
        self,
        context: ParserContext,
    ) -> str | None:

        node = context.document.first(
            self.COVER_SELECTOR
        )

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

        node = context.document.first(
            self.DESCRIPTION_SELECTOR
        )

        if node is None:
            return None

        text = node.text().strip()

        return text or None

    def extract_status(
        self,
        context: ParserContext,
    ) -> str | None:

        node = context.document.first(
            self.STATUS_SELECTOR
        )

        if node is None:
            return None

        text = node.text().strip()

        return text or None
```

---

# 15. Refactor `TruyenFullNovelParser`

Bây giờ `novel.py` không cần biết selector metadata nữa.

```python
from crawler.domain.novel import Novel

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from .metadata import NovelMetadataExtractor


class TruyenFullNovelParser(
    BaseSiteParser
):

    def __init__(
        self,
        metadata_extractor: NovelMetadataExtractor | None = None,
    ):

        self._metadata_extractor = (
            metadata_extractor
            or NovelMetadataExtractor()
        )

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> Novel:

        context = self.create_context(
            page_source,
            url,
        )

        metadata = self._metadata_extractor.extract(
            context
        )

        return Novel(
            title=metadata.title,
            author=metadata.author,
            url=url,
            cover=metadata.cover,
            description=metadata.description,
            status=metadata.status,
        )
```

Nhìn vào parser bây giờ rất sạch:

```text
parse_novel()
     │
     ├── create_context()
     │
     ├── metadata_extractor.extract()
     │
     └── Novel(...)
```

---

# 16. Đây mới là điểm đáng giá của abstraction

Trước:

```text
TruyenFullNovelParser
│
├── selector title
├── selector author
├── selector cover
├── selector description
├── selector status
│
├── extract_title
├── extract_author
├── extract_cover
├── extract_description
└── extract_status
```

Sau:

```text
TruyenFullNovelParser
        │
        ▼
NovelMetadataExtractor
        │
        ├── title
        ├── author
        ├── cover
        ├── description
        └── status
```

Parser chính tập trung vào **orchestration**.

Extractor tập trung vào **metadata extraction**.

---

# 17. Dependency Injection

Ta đã áp dụng DI:

```python
def __init__(
    self,
    metadata_extractor=None,
):
```

Mặc định:

```python
TruyenFullNovelParser()
```

sẽ tạo:

```python
NovelMetadataExtractor()
```

Nhưng test có thể truyền fake:

```python
class FakeMetadataExtractor:

    def extract(self, context):

        return NovelMetadata(
            title="Test Novel",
            author="Test Author",
        )
```

Sau đó:

```python
parser = TruyenFullNovelParser(
    metadata_extractor=FakeMetadataExtractor()
)
```

---

# 18. Nhưng hiện tại còn một vấn đề

Chúng ta đang type:

```python
metadata_extractor: NovelMetadataExtractor | None
```

Điều này tạo coupling:

```text
TruyenFullNovelParser
       ↓
NovelMetadataExtractor
```

Với project lớn, ta muốn:

```text
TruyenFullNovelParser
       ↓
NovelMetadataExtractor Protocol
       ↑
NovelMetadataExtractor
```

---

# 19. Tạo Protocol

Tạo:

```text
infrastructure/parser/plugins/truyenfull/metadata.py
```

hoặc một file interface riêng nếu sau này dùng chung.

```python
from typing import Protocol

from crawler.domain.novel import NovelMetadata
from crawler.infrastructure.parser.context import (
    ParserContext,
)


class MetadataExtractor(
    Protocol
):

    def extract(
        self,
        context: ParserContext,
    ) -> NovelMetadata:
        ...
```

Sau đó implementation:

```python
class NovelMetadataExtractor:

    def extract(
        self,
        context: ParserContext,
    ) -> NovelMetadata:
        ...
```

Không cần:

```python
class NovelMetadataExtractor(
    MetadataExtractor
):
```

vì `Protocol` hỗ trợ structural typing.

---

# 20. Nhưng có nên tạo Protocol ngay không?

Ở đây tôi khuyên:

**Có thể, nhưng chưa bắt buộc.**

Nếu project hiện tại chỉ có:

```text
TruyenFull
```

thì:

```python
NovelMetadataExtractor
```

đã đủ.

Nếu sau này:

```text
TruyenFullMetadataExtractor
NovelYYMetadataExtractor
NovelZZMetadataExtractor
```

hoặc cần fake/mock thường xuyên, Protocol trở nên hữu ích.

Đây chính là:

> **Abstraction theo nhu cầu, không abstraction theo giáo điều.**

---

# 21. Metadata extraction có thể phức tạp hơn

Ví dụ cover thực tế:

```html
<img
    class="book-cover"
    data-src="/images/book.jpg"
    src="placeholder.jpg"
>
```

Nếu code hiện tại chỉ:

```python
get_attribute(node, "src")
```

thì lấy nhầm:

```text
placeholder.jpg
```

Trong thực tế ta có thể viết:

```python
COVER_ATTRIBUTES = (
    "data-src",
    "data-original",
    "src",
)
```

và:

```python
def extract_cover(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(
        self.COVER_SELECTOR
    )

    if node is None:
        return None

    for attribute in self.COVER_ATTRIBUTES:

        src = get_attribute(
            node,
            attribute,
        )

        if src is not None:
            return context.resolve_url(src)

    return None
```

Đây là lúc `NovelMetadataExtractor` bắt đầu có giá trị thật.

---

# 22. Cải tiến Cover Extractor

Ta có thể viết:

```python
class NovelMetadataExtractor:

    COVER_SELECTOR = ".book-cover img"

    COVER_ATTRIBUTES = (
        "data-src",
        "data-original",
        "src",
    )
```

Sau đó:

```python
def extract_cover(
    self,
    context: ParserContext,
) -> str | None:

    node = context.document.first(
        self.COVER_SELECTOR
    )

    if node is None:
        return None

    for attribute in self.COVER_ATTRIBUTES:

        value = get_attribute(
            node,
            attribute,
        )

        if value is not None:
            return context.resolve_url(
                value
            )

    return None
```

Đây là một ví dụ rất thực tế về **robust parser**.

---

# 23. Test Cover Lazy Loading

```python
def test_cover_uses_data_src():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>

    <div class="book-cover">

        <img
            src="placeholder.jpg"
            data-src="/images/real.jpg"
        >

    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/book/a",
    )

    assert result.cover == (
        "https://example.com/images/real.jpg"
    )
```

---

# 24. Test Description

```python
def test_description():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>

    <div class="book-description">
        <p>Phần giới thiệu truyện.</p>
    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/book/a",
    )

    assert result.description == (
        "Phần giới thiệu truyện."
    )
```

Selectolax:

```python
node.text()
```

sẽ lấy text bên trong `<p>`.

---

# 25. Test toàn bộ metadata

```python
def test_metadata_extractor():

    html = """
    <h1 class="book-title">
        Novel A
    </h1>

    <div class="book-author">
        Author A
    </div>

    <div class="book-cover">
        <img src="/images/a.jpg">
    </div>

    <div class="book-description">
        Description A
    </div>

    <div class="book-status">
        Completed
    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/book/a",
    )

    assert result.title == "Novel A"
    assert result.author == "Author A"

    assert result.cover == (
        "https://example.com/images/a.jpg"
    )

    assert result.description == (
        "Description A"
    )

    assert result.status == "Completed"
```

---

# 26. Test Missing Optional Metadata

```python
def test_missing_optional_metadata():

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

---

# 27. Test required metadata

```python
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

    with pytest.raises(
        MissingFieldError
    ):

        parser.parse_novel(
            html,
            "https://example.com/book/a",
        )
```

---

# 28. Một vấn đề rất quan trọng: Metadata không phải Chapter

Sau Buổi 14, đừng biến:

```text
NovelMetadataExtractor
```

thành:

```text
NovelPageExtractor
```

Nó chỉ làm:

```text
title
author
cover
description
status
```

Chapter list là concern khác:

```text
Novel Page
     │
     ├── Metadata
     │
     └── Chapter Listing
```

Đến Buổi 15 chúng ta sẽ xử lý phần thứ hai.

---

# 29. Kiến trúc sau Buổi 14

```text
                  HTTPX
                    │
                    │ page_source
                    ▼
             NovelParser
                    │
                    ▼
             ParserContext
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
 NovelMetadataExtractor   ChapterListing
          │                   │
          ▼                   ▼
   NovelMetadata         ChapterSummary[]
          │
          └─────────┐
                    ▼
                  Novel
```

**ChapterListing chưa implement hôm nay.**

---

# 30. Một điểm tinh tế về `NovelMetadata`

Có thể bạn sẽ hỏi:

> "Tại sao không để metadata trực tiếp trong `Novel`?"

Hoàn toàn có thể.

Ví dụ:

```python
Novel(
    title=...,
    author=...,
    cover=...,
)
```

Nhưng `NovelMetadata` có ích khi extraction pipeline lớn:

```text
HTML
 ↓
MetadataExtractor
 ↓
NovelMetadata
 ↓
Novel Factory / Parser
 ↓
Novel
```

Nó giúp tách:

```text
extraction data
```

với:

```text
domain entity
```

Đây là một abstraction hợp lý hơn việc tạo 5 class extractor.

---

# 31. SOLID trong Buổi 14

### SRP

```text
NovelParser
→ điều phối Novel parsing

NovelMetadataExtractor
→ trích xuất metadata
```

### OCP

Có thể thay metadata extractor:

```text
TruyenFullMetadataExtractor
NovelYYMetadataExtractor
```

mà không cần sửa orchestration.

### DIP

Parser có thể phụ thuộc abstraction:

```text
NovelParser
    ↓
MetadataExtractor Protocol
    ↑
NovelMetadataExtractor
```

### ISP

Không tạo một interface khổng lồ:

```text
Parser
 ├── parse_listing
 ├── parse_novel
 ├── parse_chapter
 ├── extract_title
 ├── extract_cover
 ├── ...
```

mà mỗi abstraction nhỏ và có mục đích.

---

# 32. Điều chúng ta KHÔNG làm

Không tạo:

```text
TitleExtractor
AuthorExtractor
CoverExtractor
DescriptionExtractor
StatusExtractor
```

chỉ vì mỗi field là một responsibility.

Không tạo:

```text
AbstractNovelMetadataFactory
NovelMetadataBuilder
NovelMetadataStrategy
```

ở thời điểm này.

Không dùng:

```text
Service Locator
```

Không đưa:

```text
HTTPX
```

vào extractor.

Không đưa:

```text
SQLite
```

vào extractor.

---

# 33. Cấu trúc project hiện tại

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   ├── parser_result.py
    │   └── parser_error.py
    │
    └── infrastructure/
        └── parser/
            │
            ├── base.py
            ├── context.py
            ├── helpers.py
            ├── required.py
            ├── url_resolver.py
            ├── selectolax_document.py
            │
            └── plugins/
                └── truyenfull/
                    ├── listing.py
                    ├── novel_card.py
                    ├── novel.py
                    └── metadata.py
```

---

# 34. Flow hoàn chỉnh hiện tại

```text
Listing URL
    │
    ▼
HTTPX
    │
    ▼
ListingParser
    │
    ▼
NovelSummary
    │
    │ novel.url
    ▼
HTTPX
    │
    ▼
NovelParser
    │
    ▼
NovelMetadataExtractor
    │
    ▼
NovelMetadata
    │
    ▼
Novel
```

Và **chưa có chapter**.

---

# 35. Roadmap tiếp theo

```text
Phần IV — Novel Parser

13. Parse Novel Detail              ✅
14. Novel Metadata Extractor        ✅

15. Chapter Listing                 ⬜
16. Chapter Listing Pagination      ⬜
17. Novel Parser hoàn chỉnh         ⬜
```

### Buổi 15 sẽ là bước chuyển rất quan trọng:

Từ:

```text
Novel Detail
│
└── metadata
```

sang:

```text
Novel Detail
│
├── metadata
│
└── chapters
      ├── Chapter 1 → /chuong-1
      ├── Chapter 2 → /chuong-2
      └── Chapter 3 → /chuong-3
```

Chúng ta sẽ xây:

```python
ChapterSummary(
    title="Chương 1",
    url="https://example.com/chuong-1",
)
```

và đặc biệt sẽ giữ đúng nguyên tắc kiến trúc bạn đã đặt ra:

```text
Parser
  → chỉ parse MỘT chapter-list page

Application
  → fetch page 1
  → fetch page 2
  → fetch page 3
  → ...
```

Không để Novel Parser tự gọi HTTP hoặc tự chạy pagination.
