# Buổi 3 — Parser Interface với `Protocol`

Buổi này chúng ta bắt đầu chuyển từ **Selectolax thuần túy** sang kiến trúc Parser có abstraction rõ ràng.

Mục tiêu:

```text
                     Application
                          │
                          ▼
                  Parser Interface
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
       SiteAParser   SiteBParser   TruyenFullParser
             │            │            │
             └────────────┼────────────┘
                          ▼
                      Selectolax
```

Điểm quan trọng:

> Application biết **Parser interface**, không biết parser cụ thể của website nào.

---

# 1. Vì sao cần Interface?

Nếu crawler viết trực tiếp:

```python
parser = TruyenFullParser()
```

thì application bị phụ thuộc vào một website.

Sau này thêm:

```text
TruyenFull
SiteA
SiteB
SiteC
```

application sẽ thành:

```python
if site == "truyenfull":
    parser = TruyenFullParser()
elif site == "site_a":
    parser = SiteAParser()
elif site == "site_b":
    parser = SiteBParser()
```

Đây là thiết kế không tốt.

Ta muốn:

```python
parser = parser_registry.get(url)

result = parser.parse_listing(
    page_source,
    url,
)
```

Application không cần biết parser cụ thể là gì.

---

# 2. Ba loại Parser

Theo yêu cầu của app, ta có:

```text
Listing Parser
Novel Parser
Chapter Parser
```

Nhưng ở mức abstraction, trước mắt chúng ta sẽ gom thành:

```python
Parser
```

với ba operation:

```python
parse_listing()
parse_novel()
parse_chapter()
```

Sau này khi framework lớn hơn, chúng ta có thể tách interface.

---

# 3. Tạo package

Cấu trúc:

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   └── parser_result.py
    │
    └── infrastructure/
        └── parser/
            ├── __init__.py
            ├── base.py
            └── selectolax_document.py
```

`base.py` sẽ chứa abstraction.

---

# 4. `Protocol` là gì?

Python cho phép chúng ta định nghĩa:

```python
from typing import Protocol
```

Ví dụ:

```python
class Parser(Protocol):

    def parse_listing(self, page_source: str, url: str):
        ...

    def parse_novel(self, page_source: str, url: str):
        ...

    def parse_chapter(self, page_source: str, url: str):
        ...
```

Đây là **structural typing**.

Có nghĩa là class không nhất thiết phải:

```python
class MyParser(Parser):
```

Chỉ cần có đúng các method cần thiết là được xem như phù hợp với `Parser`.

---

# 5. Tại sao dùng `Protocol` thay vì ABC?

Ta có thể dùng:

```python
from abc import ABC, abstractmethod
```

nhưng với Parser framework, `Protocol` rất phù hợp.

Ví dụ:

```python
class Parser(Protocol):

    def parse_listing(self, page_source: str, url: str):
        ...

    def parse_novel(self, page_source: str, url: str):
        ...

    def parse_chapter(self, page_source: str, url: str):
        ...
```

Parser cụ thể:

```python
class TruyenFullParser:

    def parse_listing(self, page_source: str, url: str):
        ...

    def parse_novel(self, page_source: str, url: str):
        ...

    def parse_chapter(self, page_source: str, url: str):
        ...
```

Không cần:

```python
class TruyenFullParser(Parser):
```

Vẫn có thể được type checker xem là `Parser`.

---

# 6. Nhưng return type phải rõ

Đây là chỗ chúng ta cải thiện thiết kế từ Buổi 1.

Không nên:

```python
def parse_listing(...):
    ...
```

Không biết trả về gì.

Ta định nghĩa:

```text
parse_listing()
        ↓
ListingPage

parse_novel()
        ↓
NovelPage

parse_chapter()
        ↓
ChapterPage
```

---

# 7. Domain Models

Giả sử `domain/novel.py`:

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
    cover: str | None
    description: str | None
    status: str | None


@dataclass(frozen=True)
class ChapterSummary:
    title: str
    url: str
```

`domain/chapter.py`:

```python
from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    chapter_no: int | None
    content: str
    url: str
```

---

# 8. Parser Result

Tạo:

```text
domain/parser_result.py
```

Code:

```python
from dataclasses import dataclass

from .novel import (
    Novel,
    NovelSummary,
    ChapterSummary,
)
from .chapter import Chapter


@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None


@dataclass
class NovelPage:
    novel: Novel
    chapters: list[ChapterSummary]
    next_url: str | None


@dataclass
class ChapterPage:
    chapter: Chapter
```

---

# 9. Parser Interface hoàn chỉnh

Bây giờ:

```text
infrastructure/parser/base.py
```

```python
from typing import Protocol

from crawler.domain.parser_result import (
    ListingPage,
    NovelPage,
    ChapterPage,
)


class Parser(Protocol):

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:
        ...

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage:
        ...

    def parse_chapter(
        self,
        page_source: str,
        url: str,
    ) -> ChapterPage:
        ...
```

Đây là abstraction quan trọng của toàn bộ parser framework.

---

# 10. Ý nghĩa của `page_source`

Chú ý:

```python
page_source: str
```

chứ không phải:

```python
response: httpx.Response
```

Không làm:

```python
def parse_listing(
    self,
    response: httpx.Response,
):
```

Vì như vậy Parser lại phụ thuộc HTTPX.

Chúng ta muốn:

```text
HTTPX
   ↓
response.text
   ↓
str
   ↓
Parser
```

---

# 11. URL tại sao vẫn truyền vào Parser?

Ta có:

```python
parse_listing(
    page_source,
    url,
)
```

Tại sao cần URL?

Vì HTML thường chứa:

```html
<a href="/truyen-a">
```

Parser cần biết:

```text
https://example.com
```

để sau này resolve:

```text
/truyen-a
```

thành:

```text
https://example.com/truyen-a
```

Ngoài ra URL hiện tại còn hữu ích cho:

```text
pagination
relative URL
canonical URL
debugging
```

---

# 12. Parser cụ thể

Bây giờ tạo parser giả:

```text
infrastructure/parser/plugins/
└── dummy/
    └── parser.py
```

```python
from crawler.domain.parser_result import (
    ListingPage,
    NovelPage,
    ChapterPage,
)


class DummyParser:

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:

        raise NotImplementedError

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage:

        raise NotImplementedError

    def parse_chapter(
        self,
        page_source: str,
        url: str,
    ) -> ChapterPage:

        raise NotImplementedError
```

Class này **tự động phù hợp với Protocol**.

---

# 13. DIP — Dependency Inversion

Application không nên:

```python
from crawler.infrastructure.parser.plugins.dummy.parser import (
    DummyParser,
)
```

Mà:

```python
from crawler.infrastructure.parser.base import Parser
```

Ví dụ:

```python
class CrawlListingUseCase:

    def __init__(self, parser: Parser):
        self._parser = parser
```

Sau đó:

```python
use_case = CrawlListingUseCase(
    parser=TruyenFullParser()
)
```

hoặc:

```python
use_case = CrawlListingUseCase(
    parser=SiteAParser()
)
```

Use case không thay đổi.

Đây chính là DIP.

---

# 14. Dependency Injection

Ví dụ hoàn chỉnh:

```python
from crawler.infrastructure.parser.base import Parser


class CrawlListingUseCase:

    def __init__(self, parser: Parser):
        self._parser = parser

    def execute(
        self,
        page_source: str,
        url: str,
    ):
        return self._parser.parse_listing(
            page_source=page_source,
            url=url,
        )
```

Sử dụng:

```python
parser = TruyenFullParser()

use_case = CrawlListingUseCase(parser)

result = use_case.execute(
    page_source=html,
    url="https://example.com/truyen"
)
```

Flow:

```text
TruyenFullParser
       │
       │ inject
       ▼
CrawlListingUseCase
       │
       │ Parser interface
       ▼
parse_listing()
```

---

# 15. ISP — Interface Segregation

Ở đây có một vấn đề.

Chúng ta đang có:

```python
class Parser(Protocol):

    parse_listing()
    parse_novel()
    parse_chapter()
```

Nhưng giả sử một component **chỉ cần listing**.

Nó vẫn phụ thuộc vào:

```text
parse_novel()
parse_chapter()
```

Không thật sự lý tưởng.

Một thiết kế tốt hơn là:

```python
class ListingParser(Protocol):

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:
        ...
```

```python
class NovelParser(Protocol):

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage:
        ...
```

```python
class ChapterParser(Protocol):

    def parse_chapter(
        self,
        page_source: str,
        url: str,
    ) -> ChapterPage:
        ...
```

Đây mới là ISP rõ ràng.

---

# 16. Có nên dùng 3 interface không?

**Có.**

Với crawler của chúng ta, tôi khuyên dùng:

```text
Parser
├── ListingParser
├── NovelParser
└── ChapterParser
```

Nhưng cần hiểu:

`Parser` ở đây có thể là **composite capability**, không nhất thiết là interface duy nhất.

Ta có:

```python
class ListingParser(Protocol):
    ...
```

```python
class NovelParser(Protocol):
    ...
```

```python
class ChapterParser(Protocol):
    ...
```

Một website parser có thể implement cả ba:

```python
class TruyenFullParser:
    ...
```

---

# 17. Thiết kế cuối cùng của Interface

`base.py`:

```python
from typing import Protocol

from crawler.domain.parser_result import (
    ListingPage,
    NovelPage,
    ChapterPage,
)


class ListingParser(Protocol):

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:
        ...


class NovelParser(Protocol):

    def parse_novel(
        self,
        page_source: str,
        url: str,
    ) -> NovelPage:
        ...


class ChapterParser(Protocol):

    def parse_chapter(
        self,
        page_source: str,
        url: str,
    ) -> ChapterPage:
        ...


class Parser(
    ListingParser,
    NovelParser,
    ChapterParser,
    Protocol,
):
    pass
```

Ta có:

```text
ListingParser
NovelParser
ChapterParser
       │
       ▼
     Parser
```

---

# 18. Test bằng Type Checking

Tạo:

```python
from crawler.infrastructure.parser.base import Parser


class FakeParser:

    def parse_listing(self, page_source: str, url: str):
        ...

    def parse_novel(self, page_source: str, url: str):
        ...

    def parse_chapter(self, page_source: str, url: str):
        ...


def use_parser(parser: Parser):
    parser.parse_listing(
        "<html></html>",
        "https://example.com",
    )


fake = FakeParser()

use_parser(fake)
```

`FakeParser` không cần kế thừa:

```python
Parser
```

Đây chính là sức mạnh của `Protocol`.

---

# 19. Nhưng runtime có kiểm tra không?

Thông thường:

```python
isinstance(fake, Parser)
```

không dùng được như một ABC thông thường nếu `Protocol` chưa được đánh dấu runtime-checkable.

Nếu cần:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class ListingParser(Protocol):

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:
        ...
```

Sau đó có thể:

```python
isinstance(
    fake,
    ListingParser,
)
```

Tuy nhiên:

> Không nên lạm dụng `runtime_checkable`.

Trong architecture của chúng ta, **type checker + dependency injection** là chính.

---

# 20. Parser Interface chưa chứa Selectolax

Một điều rất quan trọng:

```python
class ListingParser(Protocol):

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ) -> ListingPage:
        ...
```

Không có:

```python
HTMLParser
Node
SelectolaxDocument
```

Interface chỉ nói:

> "Cho tôi HTML và URL, tôi trả cho anh kết quả parse."

Implementation mới quyết định dùng:

```text
Selectolax
BeautifulSoup
lxml
regex
```

Điều này thực hiện OCP/DIP rất tốt.

---

# 21. Architecture hiện tại

Sau 3 buổi:

```text
src/crawler/

domain/
│
├── novel.py
│     ├── Novel
│     ├── NovelSummary
│     └── ChapterSummary
│
├── chapter.py
│     └── Chapter
│
└── parser_result.py
      ├── ListingPage
      ├── NovelPage
      └── ChapterPage


infrastructure/
└── parser/
    │
    ├── base.py
    │     ├── ListingParser
    │     ├── NovelParser
    │     ├── ChapterParser
    │     └── Parser
    │
    └── selectolax_document.py
```

---

# 22. Flow lúc này

```text
                HTTPX Fetcher
                     │
                     │ str
                     ▼
              ┌───────────────┐
              │ Parser        │
              │ Protocol      │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Listing       Novel      Chapter
       Parser        Parser      Parser
          │           │           │
          └───────────┼───────────┘
                      ▼
                  Selectolax
                      │
                      ▼
                 Domain Model
```

Thực tế implementation:

```text
Parser Protocol
       ▲
       │
TruyenFullParser
       │
       ▼
SelectolaxDocument
```

---

# 23. Một quyết định kiến trúc quan trọng

Từ đây trở đi, **không để `SelectolaxDocument` xuất hiện trong application layer**.

Không làm:

```python
class CrawlNovelUseCase:

    def execute(self, page_source):
        document = SelectolaxDocument(page_source)
```

Sai boundary.

Đúng:

```python
class CrawlNovelUseCase:

    def __init__(self, parser: NovelParser):
        self._parser = parser

    def execute(self, page_source, url):
        return self._parser.parse_novel(
            page_source,
            url,
        )
```

Application chỉ thấy:

```text
NovelParser
```

---

# 24. Bài tập Buổi 3

Hãy tạo:

```text
infrastructure/parser/base.py
```

với 4 interface:

```python
ListingParser
NovelParser
ChapterParser
Parser
```

Sau đó tạo:

```python
class FakeParser:
    ...
```

và thử:

```python
def crawl_listing(
    parser: ListingParser,
    page_source: str,
    url: str,
):
    result = parser.parse_listing(
        page_source,
        url,
    )

    return result
```

Mục tiêu của bài này **chưa phải parse HTML**.

Mục tiêu là hiểu:

```text
Application
      │
      │ depends on
      ▼
   Protocol
      ▲
      │
      │ implements structurally
      │
Concrete Parser
```

---

## Tóm tắt Buổi 3

Ta đã xác định được boundary:

```text
HTTPX
  ↓
page_source: str
  ↓
Parser Interface
  ↓
Concrete Site Parser
  ↓
Selectolax
  ↓
Domain Model
```

SOLID:

```text
SRP → Fetcher / Parser / Application tách riêng

OCP → thêm SiteParser không sửa crawler core

LSP → parser cụ thể thay thế interface

ISP → Listing / Novel / Chapter Parser riêng

DIP → Application phụ thuộc Protocol
```

**Buổi 4** chúng ta sẽ làm phần rất quan trọng: **`ParseResult`, validation và `ParserError`**. Ta sẽ thiết kế cách parser báo các tình huống như **HTML không hợp lệ, selector không tìm thấy, thiếu title, URL không hợp lệ, chapter number không parse được**, thay vì để `AttributeError`/`IndexError` văng ra lung tung.
