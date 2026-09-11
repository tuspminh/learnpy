# Phần IV — Novel Parser

# Buổi 15 — Chapter Listing trong Novel

Ở Buổi 14 chúng ta đã tách:

```text
NovelParser
    ↓
NovelMetadataExtractor
    ↓
NovelMetadata
    ↓
Novel
```

Hôm nay thêm phần **danh sách chapter** trên trang chi tiết truyện.

Mục tiêu:

```text
Novel Detail page-source
        │
        ▼
    NovelParser
        │
        ├── Metadata
        │     └── Novel
        │
        └── Chapter Listing
              ├── ChapterSummary
              ├── ChapterSummary
              └── ChapterSummary
```

Quan trọng nhất:

> **Chapter Listing Parser chỉ parse HTML đã được HTTPX lấy về. Nó không fetch chapter.**

---

# 1. Chapter Listing là gì?

Một trang detail có thể có:

```html
<div class="book-detail">

    <h1 class="book-title">
        Đấu Phá Thương Khung
    </h1>

    <div class="book-author">
        Thiên Tằm Thổ Đậu
    </div>

</div>

<div class="chapter-list">

    <ul>
        <li>
            <a href="/chuong-1">
                Chương 1: Tiêu gia
            </a>
        </li>

        <li>
            <a href="/chuong-2">
                Chương 2: Nạp Lan Yên Nhiên
            </a>
        </li>

        <li>
            <a href="/chuong-3">
                Chương 3: Từ hôn
            </a>
        </li>
    </ul>

</div>
```

Parser cần tạo:

```python
[
    ChapterSummary(
        title="Chương 1: Tiêu gia",
        url="https://example.com/chuong-1",
    ),
    ChapterSummary(
        title="Chương 2: Nạp Lan Yên Nhiên",
        url="https://example.com/chuong-2",
    ),
    ChapterSummary(
        title="Chương 3: Từ hôn",
        url="https://example.com/chuong-3",
    ),
]
```

---

# 2. `ChapterSummary` đã có

Từ các buổi trước:

```python
@dataclass(frozen=True)
class ChapterSummary:
    title: str
    url: str
```

Đây là model hoàn toàn khác:

```text
ChapterSummary
```

với:

```text
Chapter
```

`ChapterSummary`:

```text
title
url
```

`Chapter`:

```text
title
chapter_no
content
url
```

---

# 3. Vì sao không parse `Chapter` luôn?

Vì trang Novel Detail chỉ có:

```text
chapter title
chapter URL
```

Không có nội dung chapter.

Muốn có:

```python
Chapter(
    title=...,
    chapter_no=...,
    content=...,
    url=...,
)
```

phải request:

```text
GET /chuong-1
```

Nhưng parser **không được request**.

Flow đúng:

```text
HTTPX
  │
  ▼
Novel Detail HTML
  │
  ▼
NovelParser
  │
  └── ChapterSummary[]
```

Sau đó Application:

```text
ChapterSummary.url
       │
       ▼
     HTTPX
       │
       ▼
 Chapter HTML
       │
       ▼
 ChapterParser
       │
       ▼
    Chapter
```

---

# 4. Tạo `ChapterListExtractor`

Ta không nên nhét tất cả vào:

```python
TruyenFullNovelParser
```

vì parser sẽ bắt đầu thành một class quá lớn.

Kiến trúc:

```text
TruyenFullNovelParser
        │
        ├── NovelMetadataExtractor
        │
        └── ChapterListExtractor
```

Tạo:

```text
infrastructure/
└── parser/
    └── plugins/
        └── truyenfull/
            ├── novel.py
            ├── metadata.py
            ├── novel_card.py
            └── chapter_list.py
```

---

# 5. `ChapterListExtractor`

Tạo file:

```python
# chapter_list.py

from crawler.domain.novel import ChapterSummary

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from crawler.infrastructure.parser.helpers import (
    get_attribute,
    get_text,
)

from crawler.infrastructure.parser.required import (
    required_attribute,
    required_text,
)


class ChapterListExtractor:

    CHAPTER_SELECTOR = ".chapter-list li"

    TITLE_SELECTOR = "a"

    def extract(
        self,
        context: ParserContext,
    ) -> list[ChapterSummary]:

        chapters: list[ChapterSummary] = []

        nodes = context.document.all(
            self.CHAPTER_SELECTOR
        )

        for node in nodes:

            chapter = self.extract_chapter(
                node,
                context,
            )

            chapters.append(chapter)

        return chapters

    def extract_chapter(
        self,
        node,
        context: ParserContext,
    ) -> ChapterSummary:

        title_node = node.css_first(
            self.TITLE_SELECTOR
        )

        title = required_text(
            title_node,
            field="chapter_title",
            selector=self.TITLE_SELECTOR,
        )

        href = required_attribute(
            title_node,
            attribute="href",
            field="chapter_url",
            selector=self.TITLE_SELECTOR,
        )

        chapter_url = context.resolve_url(
            href
        )

        return ChapterSummary(
            title=title,
            url=chapter_url,
        )
```

---

# 6. Tại sao selector là `.chapter-list li`?

HTML:

```html
<div class="chapter-list">

    <li>...</li>
    <li>...</li>
    <li>...</li>

</div>
```

Ta muốn mỗi:

```html
<li>
```

là một chapter.

Sau đó trong từng `li`:

```python
node.css_first("a")
```

để lấy link.

Đây là pattern rất quan trọng:

```text
Container
   ↓
Item
   ↓
Fields
```

---

# 7. Đừng dùng selector toàn trang cho title

Sai:

```python
context.document.first("a")
```

Vì trang detail có thể có hàng chục link:

```text
logo
menu
author
social
chapter
footer
```

Đúng:

```python
node.css_first("a")
```

vì:

```text
node = một chapter item
```

Ta đang nói:

> Trong chapter này, lấy link của chapter.

Đây gọi là **scoped extraction**.

---

# 8. Scoped Extraction

Ví dụ:

```html
<li class="chapter">
    <span class="badge">NEW</span>

    <a href="/chuong-1">
        Chương 1
    </a>

    <span class="date">
        2026
    </span>
</li>
```

Ta làm:

```python
chapter_node = ...

link = chapter_node.css_first("a")
```

thay vì:

```python
document.css_first("a")
```

Đây là một kỹ thuật rất quan trọng khi viết parser production.

---

# 9. URL Resolution

HTML:

```html
<a href="/chuong-1">
```

Current URL:

```text
https://example.com/truyen/dau-pha-thuong-khung
```

Parser phải trả:

```text
https://example.com/chuong-1
```

Nhờ:

```python
context.resolve_url(href)
```

Không viết:

```python
"https://example.com" + href
```

vì link có thể là:

```text
/chuong-1
chuong-1
https://example.com/chuong-1
?page=2
```

`UrlResolver` xử lý chuyện này.

---

# 10. Relative URL

Input:

```html
<a href="chuong-1">
```

Current:

```text
https://example.com/truyen/dptk
```

Có thể resolve thành:

```text
https://example.com/truyen/chuong-1
```

Đó là lý do resolver phải sử dụng URL hiện tại làm base.

---

# 11. Absolute URL

Input:

```html
<a href="https://example.com/chuong-1">
```

thì:

```python
context.resolve_url(...)
```

giữ nguyên URL tuyệt đối.

---

# 12. Query URL

Ví dụ:

```html
<a href="?chapter=1">
```

resolver cũng xử lý được:

```text
https://example.com/truyen/dptk?chapter=1
```

Parser không cần tự phân tích URL.

---

# 13. Empty chapter list

Nếu trang có:

```html
<div class="chapter-list">
</div>
```

thì:

```python
nodes = []
```

và:

```python
return []
```

Đây là behavior hợp lý.

Không nên coi:

```text
không có chapter
```

là lỗi parser bắt buộc.

Có thể là:

* truyện mới tạo
* truyện chưa có chapter
* trang bị giới hạn
* selector đúng nhưng danh sách rỗng

---

# 14. Missing title

Nếu:

```html
<li>
    <a href="/chuong-1"></a>
</li>
```

thì:

```python
required_text(...)
```

sẽ ném:

```text
MissingFieldError
```

Đây là field bắt buộc.

Một `ChapterSummary` không thể có:

```python
title=None
```

theo model hiện tại.

---

# 15. Missing href

Nếu:

```html
<li>
    <a>Chương 1</a>
</li>
```

thì:

```python
required_attribute(...)
```

ném:

```text
MissingFieldError
```

với:

```text
field = chapter_url
```

Đây cũng là field bắt buộc.

---

# 16. Không dùng `get_text()` cho field bắt buộc

Có sự khác biệt:

```python
get_text(node)
```

trả:

```text
str | None
```

Còn:

```python
required_text(node, ...)
```

trả:

```text
str
```

và ném exception nếu thiếu.

Vì:

```text
ChapterSummary
├── title: bắt buộc
└── url: bắt buộc
```

nên dùng:

```python
required_text()
required_attribute()
```

---

# 17. Parser chính

Bây giờ sửa:

```text
novel.py
```

thành:

```python
from crawler.domain.novel import Novel

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from crawler.infrastructure.parser.context import (
    ParserContext,
)

from .metadata import NovelMetadataExtractor
from .chapter_list import ChapterListExtractor


class TruyenFullNovelParser(
    BaseSiteParser
):

    def __init__(
        self,
        metadata_extractor=None,
        chapter_list_extractor=None,
    ):

        self._metadata_extractor = (
            metadata_extractor
            or NovelMetadataExtractor()
        )

        self._chapter_list_extractor = (
            chapter_list_extractor
            or ChapterListExtractor()
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

        metadata = (
            self._metadata_extractor.extract(
                context
            )
        )

        chapters = (
            self._chapter_list_extractor.extract(
                context
            )
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

Có một điểm cần chú ý:

**Hiện tại `Novel` chưa chứa `chapters`.**

Vậy chúng ta parse chapters để làm gì?

Đây chính là chỗ cần điều chỉnh kiến trúc trước khi đi tiếp.

---

# 18. `NovelPage` mới là nơi chứa chapters

Từ roadmap ban đầu ta đã có:

```python
@dataclass
class NovelPage:
    novel: Novel
    chapters: list[ChapterSummary]
    next_url: str | None
```

Vì vậy về mặt kiến trúc, parser hoàn chỉnh cuối cùng phải trả:

```text
NovelPage
```

chứ không phải:

```text
Novel
```

Nhưng Buổi 13 chúng ta cố tình mới làm metadata:

```python
parse_novel() -> Novel
```

Buổi 15 chính là lúc bắt đầu tiến tới:

```python
parse_novel() -> NovelPage
```

Tuy nhiên pagination vẫn để **Buổi 16**.

---

# 19. Refactor ngay từ bây giờ

Ta có thể cho parser trả:

```python
NovelPage(
    novel=novel,
    chapters=chapters,
    next_url=None,
)
```

Nhưng `next_url` chưa học.

Do đó trong Buổi 15 có thể tạm:

```python
next_url=None
```

Đến Buổi 16 thay bằng chapter-list pagination thật.

---

# 20. Parser hoàn chỉnh cho Buổi 15

```python
from crawler.domain.novel import Novel
from crawler.domain.parser_result import NovelPage

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)

from .chapter_list import ChapterListExtractor
from .metadata import NovelMetadataExtractor


class TruyenFullNovelParser(
    BaseSiteParser
):

    def __init__(
        self,
        metadata_extractor=None,
        chapter_list_extractor=None,
    ):

        self._metadata_extractor = (
            metadata_extractor
            or NovelMetadataExtractor()
        )

        self._chapter_list_extractor = (
            chapter_list_extractor
            or ChapterListExtractor()
        )

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage:

        context = self.create_context(
            page_source,
            url,
        )

        metadata = (
            self._metadata_extractor.extract(
                context
            )
        )

        novel = Novel(
            title=metadata.title,
            author=metadata.author,
            url=url,
            cover=metadata.cover,
            description=metadata.description,
            status=metadata.status,
        )

        chapters = (
            self._chapter_list_extractor.extract(
                context
            )
        )

        return NovelPage(
            novel=novel,
            chapters=chapters,
            next_url=None,
        )
```

Đây là bước chuyển kiến trúc quan trọng.

---

# 21. Test đầu tiên

Tạo:

```text
tests/
└── infrastructure/
    └── parser/
        └── plugins/
            └── truyenfull/
                └── test_chapter_list.py
```

Test:

```python
from crawler.infrastructure.parser.plugins.truyenfull.chapter_list import (
    ChapterListExtractor,
)

from crawler.infrastructure.parser.base import (
    BaseSiteParser,
)


def test_extract_chapter_list():

    html = """
    <div class="chapter-list">

        <ul>

            <li>
                <a href="/chuong-1">
                    Chương 1: Tiêu gia
                </a>
            </li>

            <li>
                <a href="/chuong-2">
                    Chương 2: Nạp Lan Yên Nhiên
                </a>
            </li>

            <li>
                <a href="/chuong-3">
                    Chương 3: Từ hôn
                </a>
            </li>

        </ul>

    </div>
    """

    parser = BaseSiteParser()

    context = parser.create_context(
        html,
        "https://example.com/truyen/dptk",
    )

    extractor = ChapterListExtractor()

    chapters = extractor.extract(
        context
    )

    assert len(chapters) == 3

    assert chapters[0].title == (
        "Chương 1: Tiêu gia"
    )

    assert chapters[0].url == (
        "https://example.com/chuong-1"
    )

    assert chapters[1].title == (
        "Chương 2: Nạp Lan Yên Nhiên"
    )

    assert chapters[1].url == (
        "https://example.com/chuong-2"
    )
```

---

# 22. Test empty list

```python
def test_empty_chapter_list():

    html = """
    <div class="chapter-list">
    </div>
    """

    parser = BaseSiteParser()

    context = parser.create_context(
        html,
        "https://example.com/truyen/dptk",
    )

    extractor = ChapterListExtractor()

    chapters = extractor.extract(
        context
    )

    assert chapters == []
```

---

# 23. Test missing title

```python
import pytest

from crawler.domain.parser_error import (
    MissingFieldError,
)


def test_missing_chapter_title():

    html = """
    <div class="chapter-list">

        <li>
            <a href="/chuong-1"></a>
        </li>

    </div>
    """

    parser = BaseSiteParser()

    context = parser.create_context(
        html,
        "https://example.com/truyen/dptk",
    )

    extractor = ChapterListExtractor()

    with pytest.raises(MissingFieldError):

        extractor.extract(context)
```

---

# 24. Test missing URL

```python
def test_missing_chapter_url():

    html = """
    <div class="chapter-list">

        <li>
            <a>Chương 1</a>
        </li>

    </div>
    """

    parser = BaseSiteParser()

    context = parser.create_context(
        html,
        "https://example.com/truyen/dptk",
    )

    extractor = ChapterListExtractor()

    with pytest.raises(MissingFieldError):

        extractor.extract(context)
```

---

# 25. Test absolute URL

```python
def test_absolute_chapter_url():

    html = """
    <div class="chapter-list">

        <li>
            <a href="https://example.com/chuong-1">
                Chương 1
            </a>
        </li>

    </div>
    """

    parser = BaseSiteParser()

    context = parser.create_context(
        html,
        "https://example.com/truyen/dptk",
    )

    extractor = ChapterListExtractor()

    chapters = extractor.extract(
        context
    )

    assert chapters[0].url == (
        "https://example.com/chuong-1"
    )
```

---

# 26. Test Parser + Metadata + Chapter List

Đây mới là integration test quan trọng.

```python
def test_parse_novel_page():

    html = """
    <div class="book-detail">

        <h1 class="book-title">
            Đấu Phá Thương Khung
        </h1>

        <div class="book-author">
            Thiên Tằm Thổ Đậu
        </div>

        <div class="book-cover">
            <img src="/images/dptk.jpg">
        </div>

        <div class="book-description">
            Một câu chuyện tu luyện.
        </div>

        <div class="book-status">
            Đang ra
        </div>

    </div>

    <div class="chapter-list">

        <ul>

            <li>
                <a href="/chuong-1">
                    Chương 1: Tiêu gia
                </a>
            </li>

            <li>
                <a href="/chuong-2">
                    Chương 2: Nạp Lan Yên Nhiên
                </a>
            </li>

        </ul>

    </div>
    """

    parser = TruyenFullNovelParser()

    result = parser.parse_novel(
        html,
        "https://example.com/truyen/dptk",
    )

    assert result.novel.title == (
        "Đấu Phá Thương Khung"
    )

    assert result.novel.author == (
        "Thiên Tằm Thổ Đậu"
    )

    assert len(result.chapters) == 2

    assert result.chapters[0].title == (
        "Chương 1: Tiêu gia"
    )

    assert result.chapters[0].url == (
        "https://example.com/chuong-1"
    )

    assert result.chapters[1].url == (
        "https://example.com/chuong-2"
    )

    assert result.next_url is None
```

---

# 27. Chạy test

```bash
pytest -q
```

Ta kỳ vọng:

```text
.................                                      [100%]
17 passed
```

Số lượng test thực tế tùy toàn bộ project; điều quan trọng là các test mới phải pass.

---

# 28. Một lỗi thiết kế rất dễ mắc

Không làm:

```python
class ChapterListExtractor:

    def extract(self, url):

        response = httpx.get(url)

        ...
```

Sai kiến trúc.

Vì lúc đó:

```text
Parser
  ↓
HTTPX
```

và chúng ta mất boundary:

```text
Fetcher
Parser
```

Đúng:

```python
def extract(
    self,
    context: ParserContext,
):
```

Context chứa:

```text
page-source
current URL
document
URL resolver
```

không chứa HTTP client.

---

# 29. Application mới fetch chapter

Sau này application sẽ làm:

```python
novel_page = novel_parser.parse_novel(
    response.text,
    response.url,
)

for chapter in novel_page.chapters:

    response = fetcher.fetch(
        chapter.url
    )

    chapter_page = chapter_parser.parse_chapter(
        response.text,
        chapter.url,
    )
```

Nhìn boundary:

```text
                Application
                     │
        ┌────────────┴────────────┐
        │                         │
     Fetcher                   Parser
        │                         │
        │ page_source              │
        └────────────►             │
                                  ▼
                           ChapterSummary
```

Parser không biết:

```text
Fetcher
HTTPX
Proxy
Retry
Queue
Database
```

---

# 30. Tại sao `ChapterSummary` immutable?

Ta đã dùng:

```python
@dataclass(frozen=True)
class ChapterSummary:
```

Rất phù hợp.

Sau khi parser phát hiện:

```text
Chương 1
URL /chuong-1
```

thì Application không nên tùy tiện sửa:

```python
chapter.url = "..."
```

Thay đổi chapter URL nên xuất phát từ parser/resolver hoặc một domain operation rõ ràng.

---

# 31. Chapter list không nên thuộc Domain Parser

Một điểm cần phân biệt:

```text
ChapterSummary
```

là Domain Model.

Nhưng:

```python
CHAPTER_SELECTOR = ".chapter-list li"
```

là Infrastructure.

Do đó:

```text
domain/
    novel.py
        ChapterSummary
```

nhưng:

```text
infrastructure/
    parser/
        plugins/
            truyenfull/
                chapter_list.py
```

Không được đưa:

```python
".chapter-list li"
```

vào `domain/`.

---

# 32. SOLID trong thiết kế hôm nay

Ta có:

```text
TruyenFullNovelParser
       │
       ├───────────────┐
       ▼               ▼
MetadataExtractor  ChapterListExtractor
       │               │
       ▼               ▼
NovelMetadata      ChapterSummary[]
```

### SRP

`MetadataExtractor`:

```text
metadata
```

`ChapterListExtractor`:

```text
chapter listing
```

### DIP

Parser không cần biết chi tiết extraction.

Có thể inject:

```python
TruyenFullNovelParser(
    metadata_extractor=...,
    chapter_list_extractor=...,
)
```

### OCP

Sau này có thể thay:

```text
ChapterListExtractor
```

bằng implementation khác mà không sửa toàn bộ parser orchestration.

---

# 33. Nhưng chưa cần tạo 10 Protocol

Hiện tại:

```text
NovelMetadataExtractor
ChapterListExtractor
```

đã đủ abstraction.

Không cần:

```text
IChapterTitleExtractor
IChapterUrlExtractor
IChapterListNodeExtractor
IChapterSummaryFactory
```

Đây là **over-engineering**.

Mục tiêu của SOLID là:

> quản lý dependency và thay đổi tốt hơn,

không phải tạo thật nhiều interface.

---

# 34. Kiến trúc cuối Buổi 15

```text
HTTPX
  │
  │ page_source
  ▼
TruyenFullNovelParser
  │
  ├─────────────────────────┐
  │                         │
  ▼                         ▼
NovelMetadataExtractor   ChapterListExtractor
  │                         │
  ▼                         ▼
NovelMetadata          ChapterSummary[]
  │                         │
  ▼                         │
Novel                       │
  │                         │
  └────────────┬────────────┘
               ▼
           NovelPage
```

Hiện tại:

```python
NovelPage(
    novel=novel,
    chapters=chapters,
    next_url=None,
)
```

---

# 35. Một lưu ý về `next_url`

Đừng vội làm:

```python
chapter_list_extractor
```

tự fetch:

```text
page 1
page 2
page 3
...
```

Ở Buổi 16 chúng ta sẽ xử lý:

```text
Chapter Listing Pagination
```

và sẽ có:

```text
Novel Detail Page 1
       │
       ├── chapters 1–100
       │
       └── next_url
               │
               ▼
        Novel Detail Page 2
               │
               ├── chapters 101–200
               │
               └── next_url
```

Parser chỉ trả:

```python
NovelPage(
    novel=...,
    chapters=[...],
    next_url="..."
)
```

**Application mới quyết định có fetch `next_url` hay không.**

Đây là boundary cực kỳ quan trọng cho crawler production.

---

# 36. Roadmap hiện tại

```text
Phần IV — Novel Parser

13. Parse Novel Detail
   └── Novel metadata                         ✅

14. Novel Metadata Extractor
   ├── metadata abstraction                  ✅
   ├── dependency injection                  ✅
   └── balanced SRP                          ✅

15. Chapter Listing
   ├── ChapterSummary                        ✅
   ├── ChapterListExtractor                  ✅
   ├── scoped extraction                     ✅
   ├── URL resolution                        ✅
   └── NovelPage                             ✅

16. Chapter Listing Pagination               ⬜
17. Novel Parser hoàn chỉnh                  ⬜
```

**Buổi 16** chúng ta sẽ giải quyết một vấn đề thực tế hơn: một truyện có **hàng nghìn chapter**, nhưng trang detail chỉ hiển thị 50/100/200 chapter và có nút **Trang sau / Next**. Ta sẽ thiết kế pagination sao cho parser vẫn chỉ parse **một `page-source`**, còn Application chịu trách nhiệm crawl toàn bộ danh sách chapter.
