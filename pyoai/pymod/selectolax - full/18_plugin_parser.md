# 📘 Selectolax — Buổi 18: Plugin Parser

Hôm nay chúng ta giải quyết một vấn đề rất thực tế:

> **Một crawler nhưng phải crawl được nhiều website có HTML hoàn toàn khác nhau.**

Ví dụ:

```text
Website A
.chapter-list a

Website B
.list-chapter a

Website C
ul.chapters > li > a
```

Nếu viết:

```python
if site == "A":
    ...
elif site == "B":
    ...
elif site == "C":
    ...
```

thì crawler core sẽ nhanh chóng thành **God Object**.

Thay vào đó:

```text
                    Crawler
                       │
                       ▼
                Parser Interface
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      SiteAParser  SiteBParser  SiteCParser
```

Đây chính là **Plugin Architecture**.

---

# 1. Mục tiêu Buổi 18

Sau buổi này bạn sẽ hiểu:

* Parser Interface
* `ABC`
* Protocol
* Plugin
* Site-specific parser
* Parser Registry
* Parser selection
* Tách crawler core khỏi website
* Open/Closed Principle
* Dependency Inversion
* Dynamic plugin registration

---

# 2. Vấn đề của cách làm cũ

Giả sử crawler có:

```python
class Crawler:

    def crawl(self, url):

        if "site-a.com" in url:
            title = tree.css_first(
                ".story-title"
            )

        elif "site-b.com" in url:
            title = tree.css_first(
                "h1.title"
            )

        elif "site-c.com" in url:
            title = tree.css_first(
                ".novel-name"
            )
```

Ban đầu:

```text
3 website
```

còn chịu được.

Nhưng sau này:

```text
50 website
```

thì:

```python
if ...
elif ...
elif ...
elif ...
...
```

trở thành thảm họa.

---

# 3. Tư duy đúng

Crawler **không nên biết HTML của website**.

Crawler chỉ biết:

```text
Parser
```

Parser chịu trách nhiệm:

```text
HTML
 ↓
Story
Chapter
Pagination
```

Kiến trúc:

```text
HTTPX
  ↓
HTML
  ↓
Crawler
  ↓
Parser Interface
  ↓
Concrete Parser
  ↓
Domain Model
```

---

# 4. Parser Interface

Ta định nghĩa contract:

```python
class Parser:
    ...
```

Parser cần làm gì?

Ví dụ:

```text
can_handle(url)
parse_story()
parse_chapter()
parse_chapter_list()
parse_next_page()
```

Ta có thể định nghĩa:

```python
from abc import ABC, abstractmethod


class Parser(ABC):

    @abstractmethod
    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...


    @abstractmethod
    def parse_story(
        self,
        tree,
        url: str,
    ):
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url: str,
        story_id: int,
    ):
        ...
```

Đây là **interface** của parser.

---

# 5. Vì sao `ABC`?

`ABC` giúp chúng ta nói:

> Mọi parser plugin bắt buộc phải cung cấp các method này.

Ví dụ:

```python
class SiteAParser(Parser):

    def can_handle(self, url):
        ...

    def parse_story(self, tree, url):
        ...

    def parse_chapter(
        self,
        tree,
        url,
        story_id,
    ):
        ...
```

Nếu thiếu abstract method:

```python
SiteAParser()
```

sẽ không instantiate được.

---

# 6. Nhưng `ABC` chưa phải plugin

Đây là điểm quan trọng.

Ta có:

```text
Parser Interface
      │
      ├── SiteAParser
      ├── SiteBParser
      └── SiteCParser
```

Đó mới là **Strategy / polymorphism**.

Plugin architecture cần thêm:

```text
Parser Registry
```

để crawler không hard-code:

```python
SiteAParser()
SiteBParser()
SiteCParser()
```

---

# 7. Domain Models

Tiếp tục sử dụng:

```python
from dataclasses import dataclass, field


@dataclass
class ChapterLink:
    title: str
    url: str
    number: int | None = None


@dataclass
class Story:
    id: int | None
    title: str
    url: str
    author: str | None = None
    description: str | None = None
    categories: list[str] = field(
        default_factory=list
    )
    chapters: list[ChapterLink] = field(
        default_factory=list
    )


@dataclass
class Chapter:
    id: int | None
    story_id: int
    title: str
    url: str
    content: str
    number: int | None = None
```

---

# 8. Tạo Parser Interface

Tôi khuyên tách:

```text
app/
├── domain/
│   └── models.py
│
├── parser/
│   ├── base.py
│   ├── site_a.py
│   ├── site_b.py
│   └── registry.py
```

`base.py`:

```python
from abc import ABC, abstractmethod


class Parser(ABC):

    @abstractmethod
    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...


    @abstractmethod
    def parse_story(
        self,
        tree,
        url: str,
    ):
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url: str,
        story_id: int,
    ):
        ...
```

---

# 9. Site A

Giả sử HTML Site A:

```html
<h1 class="story-title">
    Python Crawler
</h1>

<div class="author">
    Garden
</div>

<div class="chapter-list">
    <a href="/chapter/1">
        Chương 1
    </a>
</div>
```

Parser:

```python
from urllib.parse import urljoin

from .base import Parser
from ..models import (
    Story,
    ChapterLink,
)


class SiteAParser(Parser):

    def can_handle(self, url):
        return "site-a.com" in url


    def parse_story(
        self,
        tree,
        url,
    ):

        title_node = tree.css_first(
            ".story-title"
        )

        if title_node is None:
            raise ValueError(
                "Story title not found"
            )

        author_node = tree.css_first(
            ".author"
        )

        chapters = []

        for node in tree.css(
            ".chapter-list a"
        ):

            href = node.attributes.get(
                "href"
            )

            title = node.text(
                strip=True
            )

            if not href or not title:
                continue

            chapters.append(
                ChapterLink(
                    title=title,
                    url=urljoin(
                        url,
                        href,
                    ),
                )
            )

        return Story(
            id=None,
            title=title_node.text(
                strip=True
            ),
            url=url,
            author=(
                author_node.text(
                    strip=True
                )
                if author_node
                else None
            ),
            chapters=chapters,
        )
```

---

# 10. Site B

Site B lại có HTML:

```html
<h1 class="title">
    Python Crawler
</h1>

<span class="writer">
    Garden
</span>

<div class="list-chapter">
    <a href="/chuong-1">
        Chapter 1
    </a>
</div>
```

Parser:

```python
class SiteBParser(Parser):

    def can_handle(self, url):
        return "site-b.com" in url


    def parse_story(
        self,
        tree,
        url,
    ):

        title_node = tree.css_first(
            "h1.title"
        )

        if title_node is None:
            raise ValueError(
                "Story title not found"
            )

        author_node = tree.css_first(
            ".writer"
        )

        chapters = []

        for node in tree.css(
            ".list-chapter a"
        ):

            href = node.attributes.get(
                "href"
            )

            title = node.text(
                strip=True
            )

            if not href:
                continue

            chapters.append(
                ChapterLink(
                    title=title,
                    url=urljoin(
                        url,
                        href,
                    ),
                )
            )

        return Story(
            id=None,
            title=title_node.text(
                strip=True
            ),
            url=url,
            author=(
                author_node.text(
                    strip=True
                )
                if author_node
                else None
            ),
            chapters=chapters,
        )
```

---

# 11. Crawler không biết Site A/B

Đây là điểm quan trọng nhất.

Crawler không được:

```python
if site_a:
    ...
elif site_b:
    ...
```

Nó chỉ làm:

```python
parser = parser_registry.get_parser(
    url
)

story = parser.parse_story(
    tree,
    url,
)
```

Crawler chỉ biết:

```text
Parser Interface
```

chứ không biết:

```text
SiteAParser
SiteBParser
```

---

# 12. Parser Registry

Tạo:

```text
app/parser/registry.py
```

```python
class ParserRegistry:

    def __init__(self):
        self._parsers = []

    def register(self, parser):
        self._parsers.append(parser)

    def get_parser(self, url):

        for parser in self._parsers:

            if parser.can_handle(url):
                return parser

        raise ValueError(
            f"No parser for {url}"
        )
```

---

# 13. Đăng ký parser

```python
registry = ParserRegistry()

registry.register(
    SiteAParser()
)

registry.register(
    SiteBParser()
)
```

Sau đó:

```python
parser = registry.get_parser(
    "https://site-a.com/story/1"
)
```

→ `SiteAParser`

Còn:

```python
parser = registry.get_parser(
    "https://site-b.com/story/1"
)
```

→ `SiteBParser`

---

# 14. Đây chính là Strategy Pattern

Ta có:

```text
Parser
  ↑
  │
  ├── SiteAParser
  ├── SiteBParser
  └── SiteCParser
```

Runtime chọn:

```text
URL
 ↓
Registry
 ↓
Concrete Parser
```

Đây là polymorphism:

```python
parser.parse_story(...)
```

Không cần biết parser thực tế là class nào.

---

# 15. Crawler Core

Bây giờ crawler:

```python
class StoryCrawler:

    def __init__(
        self,
        fetcher,
        html_parser,
        parser_registry,
        repository,
    ):
        self.fetcher = fetcher
        self.html_parser = html_parser
        self.parser_registry = (
            parser_registry
        )
        self.repository = repository
```

Method:

```python
def crawl_story(
    self,
    url: str,
):

    html = self.fetcher.fetch(
        url
    )

    tree = self.html_parser.parse(
        html
    )

    parser = (
        self.parser_registry.get_parser(
            url
        )
    )

    story = parser.parse_story(
        tree,
        url,
    )

    story_id = (
        self.repository.save(
            story
        )
    )

    return story_id
```

Notice:

**Không có:**

```python
SiteAParser
SiteBParser
```

---

# 16. Đây chính là Open/Closed Principle

Muốn thêm Site C.

Cách cũ:

```python
class Crawler:

    if site_a:
       ...

    elif site_b:
       ...

    elif site_c:
       ...
```

→ sửa Crawler.

Cách mới:

```text
Crawler
   │
   └── ParserRegistry
          │
          ├── SiteA
          ├── SiteB
          └── SiteC
```

Thêm:

```python
registry.register(
    SiteCParser()
)
```

Crawler không thay đổi.

Đây chính là:

> **Open for extension, closed for modification.**

---

# 17. Plugin phải xử lý Chapter

Parser interface:

```python
class Parser(ABC):

    @abstractmethod
    def parse_story(
        self,
        tree,
        url,
    ):
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url,
        story_id,
    ):
        ...
```

Site A:

```python
def parse_chapter(
    self,
    tree,
    url,
    story_id,
):

    title_node = tree.css_first(
        ".chapter-title"
    )

    content_node = tree.css_first(
        ".chapter-content"
    )

    if not title_node:
        raise ValueError(
            "Chapter title not found"
        )

    if not content_node:
        raise ValueError(
            "Chapter content not found"
        )

    return Chapter(
        id=None,
        story_id=story_id,
        title=title_node.text(
            strip=True
        ),
        url=url,
        content=content_node.text(
            separator="\n",
            strip=True,
        ),
    )
```

---

# 18. Crawler Chapter

Crawler:

```python
def crawl_chapter(
    self,
    url: str,
    story_id: int,
):

    html = self.fetcher.fetch(
        url
    )

    tree = self.html_parser.parse(
        html
    )

    parser = (
        self.parser_registry.get_parser(
            url
        )
    )

    chapter = parser.parse_chapter(
        tree,
        url,
        story_id,
    )

    return self.repository.save(
        chapter
    )
```

Một lần nữa:

```text
Crawler
```

không biết CSS selector.

---

# 19. Nhưng có một vấn đề

`can_handle()`:

```python
return "site-a.com" in url
```

khá đơn giản.

Trong production, có thể cần:

```python
class Parser:

    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...
```

Site A:

```python
return urlparse(
    url
).netloc.endswith(
    "site-a.com"
)
```

Không nên:

```python
"site-a.com" in url
```

vì URL có thể chứa domain trong query string.

---

# 20. Tốt hơn: `supports`

Tên:

```python
can_handle()
```

hoặc:

```python
supports()
```

đều được.

Tôi thích:

```python
def supports(
    self,
    url: str,
) -> bool:
```

vì nghĩa rõ:

> Parser này có hỗ trợ URL này không?

---

# 21. Parser Interface hoàn chỉnh

```python
class Parser(ABC):

    @abstractmethod
    def supports(
        self,
        url: str,
    ) -> bool:
        ...


    @abstractmethod
    def parse_story(
        self,
        tree,
        url: str,
    ) -> Story:
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url: str,
        story_id: int,
    ) -> Chapter:
        ...
```

---

# 22. Pagination cũng phải thuộc Plugin

Đây là điểm rất quan trọng.

Site A:

```text
<a class="next">
```

Site B:

```text
<a rel="next">
```

Site C:

```text
button.next-page
```

Vì vậy **Pagination selector không nên nằm trong core crawler**.

Interface:

```python
@abstractmethod
def parse_next_page(
    self,
    tree,
    url: str,
) -> str | None:
    ...
```

---

# 23. Interface đầy đủ

```python
class Parser(ABC):

    @abstractmethod
    def supports(self, url):
        ...


    @abstractmethod
    def parse_story(
        self,
        tree,
        url,
    ):
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url,
        story_id,
    ):
        ...


    @abstractmethod
    def parse_next_page(
        self,
        tree,
        url,
    ):
        ...
```

Bây giờ plugin chịu trách nhiệm toàn bộ **website-specific behavior**.

---

# 24. Site A Pagination

```python
def parse_next_page(
    self,
    tree,
    url,
):

    node = tree.css_first(
        "a.next"
    )

    if node is None:
        return None

    href = node.attributes.get(
        "href"
    )

    if not href:
        return None

    return urljoin(
        url,
        href,
    )
```

Site B:

```python
def parse_next_page(
    self,
    tree,
    url,
):

    node = tree.css_first(
        "a[rel='next']"
    )

    if node is None:
        return None

    href = node.attributes.get(
        "href"
    )

    if not href:
        return None

    return urljoin(
        url,
        href,
    )
```

---

# 25. Đây là Boundary cực kỳ đẹp

Core:

```text
Paginator
```

không cần biết:

```text
.next
a[rel=next]
.pagination-next
```

Nó chỉ gọi:

```python
parser.parse_next_page(
    tree,
    url,
)
```

---

# 26. Paginator mới

```python
class Paginator:

    def __init__(
        self,
        fetcher,
        html_parser,
        parser_registry,
    ):
        self.fetcher = fetcher
        self.html_parser = html_parser
        self.parser_registry = (
            parser_registry
        )

    def crawl(
        self,
        start_url,
    ):

        url = start_url
        visited = set()

        while url:

            if url in visited:
                break

            visited.add(url)

            html = self.fetcher.fetch(
                url
            )

            tree = self.html_parser.parse(
                html
            )

            parser = (
                self.parser_registry
                .get_parser(url)
            )

            result = parser.parse_story(
                tree,
                url,
            )

            yield from result.chapters

            url = parser.parse_next_page(
                tree,
                url,
            )
```

---

# 27. Nhưng ta đang có một thiết kế hơi lệch

`parse_story()` trả:

```text
Story
```

và `Story` có:

```python
chapters
```

Trong khi Pagination chỉ cần:

```text
ChapterLink[]
```

Vì vậy production architecture nên tách:

```text
parse_story()
parse_chapter_links()
parse_next_page()
```

---

# 28. Interface tốt hơn

```python
class Parser(ABC):

    @abstractmethod
    def supports(self, url):
        ...


    @abstractmethod
    def parse_story(
        self,
        tree,
        url,
    ) -> Story:
        ...


    @abstractmethod
    def parse_chapter_links(
        self,
        tree,
        url,
    ) -> list[ChapterLink]:
        ...


    @abstractmethod
    def parse_chapter(
        self,
        tree,
        url,
        story_id,
    ) -> Chapter:
        ...


    @abstractmethod
    def parse_next_page(
        self,
        tree,
        url,
    ) -> str | None:
        ...
```

Đây là thiết kế tôi khuyên dùng cho project cuối.

---

# 29. Tại sao tốt hơn?

Ta có các use case độc lập:

```text
parse_story
       ↓
Story metadata

parse_chapter_links
       ↓
Chapter discovery

parse_next_page
       ↓
Pagination

parse_chapter
       ↓
Chapter content
```

Không method nào phải làm quá nhiều việc.

---

# 30. Parser Registry nâng cao

Hiện tại:

```python
self._parsers = []
```

Có thể thêm:

```python
def register(self, parser):

    if parser in self._parsers:
        return

    self._parsers.append(parser)
```

và:

```python
def get_parser(self, url):

    for parser in self._parsers:

        if parser.supports(url):
            return parser

    raise LookupError(
        f"No parser registered for {url}"
    )
```

---

# 31. Priority

Có thể hai parser cùng match:

```text
GenericParser
SiteAParser
```

Nếu:

```python
GenericParser.supports(url)
```

trả True trước:

```text
SiteAParser
```

sẽ không bao giờ được chọn.

Có thể thêm:

```python
@property
def priority(self):
    return 0
```

Site-specific:

```python
@property
def priority(self):
    return 100
```

Generic:

```python
@property
def priority(self):
    return 0
```

Registry sort:

```python
self._parsers.sort(
    key=lambda p: p.priority,
    reverse=True,
)
```

---

# 32. Nhưng chưa cần over-engineer

Ở project hiện tại:

```text
SiteA
SiteB
SiteC
```

thì:

```python
for parser in parsers:
```

là đủ.

Đừng xây plugin system quá phức tạp khi chưa có nhu cầu.

---

# 33. Plugin Factory

Một cách khác:

```python
PARSERS = {
    "site-a.com": SiteAParser,
    "site-b.com": SiteBParser,
}
```

Sau đó:

```python
parser_cls = PARSERS[domain]

parser = parser_cls()
```

Cách này nhanh nhưng vẫn có vấn đề:

```text
registry phải biết domain
```

và parser registration không linh hoạt bằng:

```python
parser.supports(url)
```

---

# 34. Dependency Injection

Crawler nhận:

```python
parser_registry
```

thay vì tự tạo:

```python
ParserRegistry()
SiteAParser()
SiteBParser()
```

Đây là:

> **Dependency Injection**

Crawler:

```python
class Crawler:

    def __init__(
        self,
        parser_registry,
    ):
        self.parser_registry = (
            parser_registry
        )
```

Test có thể inject registry giả.

---

# 35. Đây chính là DIP

Crawler phụ thuộc vào:

```text
Parser abstraction
```

không phụ thuộc:

```text
SiteAParser
```

Sơ đồ:

```text
           Parser Interface
              ▲       ▲
              │       │
        SiteAParser SiteBParser

              ▲
              │
           Registry
              ▲
              │
           Crawler
```

Cả core và plugin đều xoay quanh abstraction.

---

# 36. Cấu trúc project

Sau Buổi 18, tôi đề xuất:

```text
crawler/
│
├── domain/
│   ├── models.py
│   └── ...
│
├── application/
│   ├── crawler.py
│   ├── paginator.py
│   └── ...
│
├── infrastructure/
│   ├── http/
│   │   └── fetcher.py
│   │
│   └── database/
│       ├── connection.py
│       └── repositories.py
│
├── parsers/
│   ├── base.py
│   ├── registry.py
│   │
│   ├── site_a/
│   │   └── parser.py
│   │
│   └── site_b/
│       └── parser.py
│
└── tests/
```

Đây bắt đầu kết hợp:

```text
Clean Architecture
+
Plugin Architecture
```

---

# 37. Một Plugin thực sự

Ta có thể coi:

```text
parsers/site_a/
```

là một plugin:

```text
site_a/
├── parser.py
├── selectors.py
└── utils.py
```

`selectors.py`:

```python
STORY_TITLE = ".story-title"
AUTHOR = ".author"
CHAPTER_LINK = ".chapter-list a"
NEXT_PAGE = "a.next"
CHAPTER_TITLE = ".chapter-title"
CHAPTER_CONTENT = ".chapter-content"
```

Parser:

```python
from .selectors import (
    STORY_TITLE,
    AUTHOR,
    CHAPTER_LINK,
    NEXT_PAGE,
)
```

---

# 38. Tại sao tách selectors?

Thay vì:

```python
tree.css_first(
    ".story-title"
)
```

rải khắp file.

Ta có:

```python
STORY_TITLE = ".story-title"
```

Nếu website thay HTML:

```text
.story-title
```

→

```text
h1.story-title
```

sửa một chỗ.

---

# 39. Nhưng đừng biến selectors thành config quá sớm

Không nên cố biến mọi thứ thành:

```json
{
    "title": ".story-title",
    "author": ".author",
    "chapter": ".chapter-list a"
}
```

vì website thực tế thường có logic:

```text
if ...
normalize ...
fallback ...
```

Plugin Python vẫn cần code.

---

# 40. Test Plugin

Test riêng Site A:

```python
def test_site_a_supports():

    parser = SiteAParser()

    assert parser.supports(
        "https://site-a.com/story/1"
    )

    assert not parser.supports(
        "https://site-b.com/story/1"
    )
```

---

# 41. Test parser không cần HTTPX

Đây là nguyên tắc rất quan trọng.

```text
HTML fixture
 ↓
Selectolax
 ↓
SiteAParser
 ↓
Story
```

Không cần:

```text
Internet
HTTPX
SQLite
```

Test nhanh và deterministic.

---

# 42. Test Registry

```python
def test_registry():

    registry = ParserRegistry()

    registry.register(
        SiteAParser()
    )

    registry.register(
        SiteBParser()
    )

    parser = registry.get_parser(
        "https://site-a.com/story/1"
    )

    assert isinstance(
        parser,
        SiteAParser,
    )
```

---

# 43. Test Unknown Site

```python
def test_unknown_site():

    registry = ParserRegistry()

    registry.register(
        SiteAParser()
    )

    with pytest.raises(
        LookupError
    ):

        registry.get_parser(
            "https://unknown.com/story/1"
        )
```

---

# 44. Test Crawler với Fake Parser

Đây mới là lợi ích lớn.

Crawler không cần Site A.

Ta tạo:

```python
class FakeParser(Parser):

    def supports(self, url):
        return True

    def parse_story(
        self,
        tree,
        url,
    ):
        return Story(
            id=None,
            title="Test",
            url=url,
        )

    ...
```

Inject:

```python
registry.register(
    FakeParser()
)
```

Crawler test không cần HTML phức tạp.

---

# 45. Plugin Architecture cuối cùng

Ta đạt được:

```text
                    CRAWLER CORE
                         │
                         ▼
                  ParserRegistry
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
         SiteAPlugin SiteBPlugin SiteCPlugin
             │           │           │
             ▼           ▼           ▼
         Selectolax  Selectolax  Selectolax
             │           │           │
             └───────────┼───────────┘
                         ▼
                    Domain Model
                         │
                         ▼
                    Repository
                         │
                         ▼
                       SQLite
```

**Core không biết selector của bất kỳ website nào.**

Đó chính là mục tiêu.

---

# 46. Tư duy quan trọng nhất của Buổi 18

Đừng nghĩ:

> "Làm sao để Selectolax parse được nhiều website?"

Hãy nghĩ:

> **"Làm sao để core crawler không cần biết website cụ thể?"**

Đó là sự khác biệt giữa:

```text
script scraping
```

và:

```text
crawler framework
```

---

# 47. Bài tập Buổi 18

## Bài 1 — Parser Interface

Tạo:

```text
Parser
├── supports()
├── parse_story()
├── parse_chapter_links()
├── parse_chapter()
└── parse_next_page()
```

---

## Bài 2 — Site A

HTML:

```html
<h1 class="story-title">
    Python Crawler
</h1>

<div class="author">
    Garden
</div>

<div class="chapter-list">
    <a href="/chapter/1">
        Chapter 1
    </a>
</div>

<a class="next"
   href="/story/python?page=2">
    Next
</a>
```

Viết:

```python
SiteAParser
```

---

## Bài 3 — Site B

Thay selector:

```text
h1.title
.writer
.list-chapter a
a[rel="next"]
```

Viết:

```python
SiteBParser
```

---

## Bài 4 — Registry

Phải chạy được:

```python
registry = ParserRegistry()

registry.register(
    SiteAParser()
)

registry.register(
    SiteBParser()
)
```

Sau đó:

```python
parser = registry.get_parser(url)
```

---

## Bài 5 — Crawler

Crawler phải **không có**:

```python
if site_a:
```

hoặc:

```python
SiteAParser()
```

hoặc:

```python
SiteBParser()
```

Crawler chỉ:

```python
parser = registry.get_parser(url)
```

---

## Bài 6 — Test

Viết ít nhất:

```text
test_site_a_supports
test_site_b_supports
test_site_a_story
test_site_b_story
test_site_a_chapters
test_site_b_chapters
test_pagination
test_registry
test_unknown_site
```

---

# 🎯 Sau Buổi 18

Kiến trúc hiện tại:

```text
HTTPX
  ↓
Fetcher
  ↓
HTML
  ↓
Selectolax
  ↓
ParserRegistry
  ↓
┌───────────────┐
│ SiteAParser   │
│ SiteBParser   │
│ SiteCParser   │
└───────────────┘
  ↓
Story / Chapter
  ↓
Repository
  ↓
SQLite
```

Và **Buổi 19** sẽ là bước chuyển rất lớn:

```text
                asyncio
                   │
                   ▼
             Async HTTPX
                   │
                   ▼
             Concurrent Fetch
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Chapter1 Chapter2 Chapter3
          │        │        │
          └────────┼────────┘
                   ▼
               Selectolax
                   ▼
                 SQLite
```

Lúc đó chúng ta sẽ giải quyết một vấn đề rất quan trọng: **làm sao crawl hàng trăm chapter đồng thời nhưng vẫn giới hạn concurrency, timeout, retry và không làm website bị quá tải.**
