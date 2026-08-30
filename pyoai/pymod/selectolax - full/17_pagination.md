# 📘 Selectolax — Buổi 17: Pagination & Crawl nhiều Chapter

Hôm nay chúng ta nâng Story Crawler từ:

```text
Story
 ↓
Chapter links
```

thành:

```text
Story
 ↓
Pagination
 ↓
Collect chapter URLs
 ↓
Deduplicate
 ↓
Crawl nhiều chapter
 ↓
Parse
 ↓
Save SQLite
```

Đây là buổi rất quan trọng vì nó bắt đầu xuất hiện **crawl orchestration**.

---

# 1. Bài toán thực tế

Một trang truyện có thể không chứa toàn bộ chapter:

```text
/story/python

Trang 1
├── Chapter 1
├── Chapter 2
├── ...
└── Chapter 20

        ↓ next

Trang 2
├── Chapter 21
├── Chapter 22
├── ...
└── Chapter 40

        ↓ next

Trang 3
├── Chapter 41
└── Chapter 50
```

Crawler phải:

```text
Page 1
 ↓
extract chapters
 ↓
find next page
 ↓
Page 2
 ↓
extract chapters
 ↓
find next page
 ↓
Page 3
 ↓
STOP
```

---

# 2. Kiến trúc hôm nay

Ta sẽ xây:

```text
                    StoryCrawler
                         │
                         ▼
                  Story Page Fetch
                         │
                         ▼
                   Selectolax
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      ChapterParser            Pagination
             │                       │
             ▼                       ▼
      ChapterLink[]               next_url
             │                       │
             └───────────┬───────────┘
                         ▼
                   Chapter URLs
                         │
                         ▼
                  ChapterCrawler
                         │
                         ▼
                  ChapterParser
                         │
                         ▼
                       SQLite
```

---

# 3. Model

Tiếp tục model:

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

# 4. Pagination model

Tôi khuyên tạo một model riêng:

```python
from dataclasses import dataclass


@dataclass
class PageResult:
    items: list[ChapterLink]
    next_url: str | None
```

Ý tưởng:

```text
PageResult
│
├── items
│
└── next_url
```

Ví dụ:

```python
PageResult(
    items=[
        ChapterLink(...),
        ChapterLink(...),
    ],
    next_url="https://example.com/story/python?page=2",
)
```

Trang cuối:

```python
PageResult(
    items=[
        ChapterLink(...),
    ],
    next_url=None,
)
```

---

# 5. Tại sao cần `PageResult`?

Nếu parser chỉ trả:

```python
list[ChapterLink]
```

ta không biết:

```text
còn page tiếp theo?
```

Nếu parser trả:

```python
tuple[list[ChapterLink], str | None]
```

thì khó đọc.

`PageResult` rõ ràng hơn:

```python
result.items
result.next_url
```

---

# 6. HTML Pagination

Giả sử website:

```html
<nav class="pagination">

    <a href="/story/python?page=1">
        1
    </a>

    <a href="/story/python?page=2">
        2
    </a>

    <a href="/story/python?page=3">
        3
    </a>

    <a class="next"
       href="/story/python?page=2">
        Next
    </a>

</nav>
```

Selectolax:

```python
next_node = tree.css_first(
    "a.next"
)
```

---

# 7. Extract next URL

```python
from urllib.parse import urljoin


def extract_next_url(
    tree,
    base_url: str,
) -> str | None:

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
        base_url,
        href,
    )
```

---

# 8. PaginationParser

Tạo:

```text
app/
└── pagination.py
```

```python
from urllib.parse import urljoin


class PaginationParser:

    def extract_next_url(
        self,
        tree,
        base_url: str,
    ) -> str | None:

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
            base_url,
            href,
        )
```

---

# 9. Story page parser

Bây giờ `StoryParser` có thể trả:

```python
PageResult
```

Ví dụ:

```python
class StoryPageParser:

    def parse(
        self,
        tree,
        base_url,
    ) -> PageResult:

        chapters = (
            self._extract_chapters(
                tree,
                base_url,
            )
        )

        next_url = (
            self._extract_next_url(
                tree,
                base_url,
            )
        )

        return PageResult(
            items=chapters,
            next_url=next_url,
        )
```

---

# 10. Extract chapters

```python
def _extract_chapters(
    self,
    tree,
    base_url,
):

    chapters = []

    for node in tree.css(
        ".chapter-list a"
    ):

        title = node.text(
            strip=True
        )

        href = node.attributes.get(
            "href"
        )

        if not title or not href:
            continue

        url = urljoin(
            base_url,
            href,
        )

        chapters.append(
            ChapterLink(
                title=title,
                url=url,
                number=parse_chapter_number(
                    title
                ),
            )
        )

    return chapters
```

---

# 11. Pagination crawler

Bây giờ cần một component chuyên crawl pagination.

Tạo:

```text
app/paginator.py
```

```python
class Paginator:

    def __init__(
        self,
        fetcher,
        parser,
    ):
        self.fetcher = fetcher
        self.parser = parser
```

Method:

```python
def crawl(
    self,
    start_url: str,
):
    ...
```

---

# 12. Implementation đầu tiên

```python
class Paginator:

    def __init__(
        self,
        fetcher,
        parser,
    ):
        self.fetcher = fetcher
        self.parser = parser

    def crawl(
        self,
        start_url: str,
    ):

        url = start_url

        while url:

            html = self.fetcher.fetch(
                url
            )

            tree = self.parser.parse(
                html
            )

            result = (
                self.parser.parse_page(
                    tree,
                    url,
                )
            )

            for item in result.items:
                yield item

            url = result.next_url
```

Nhưng ở đây `Parser` và `parse_page()` đang hơi lẫn trách nhiệm.

Ta sửa architecture.

---

# 13. Tách HTML Parser và Story Page Parser

```text
HTML
 ↓
HTMLParser
 ↓
StoryPageParser
 ↓
PageResult
```

`Parser`:

```python
class Parser:

    def parse(self, html: str):
        if not html.strip():
            raise ValueError(
                "HTML is empty"
            )

        return HTMLParser(html)
```

`StoryPageParser`:

```python
class StoryPageParser:

    def parse_page(
        self,
        tree,
        url,
    ) -> PageResult:

        ...
```

---

# 14. Paginator hoàn chỉnh

```python
class Paginator:

    def __init__(
        self,
        fetcher,
        parser,
        page_parser,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.page_parser = page_parser

    def crawl(
        self,
        start_url: str,
    ):

        url = start_url

        while url:

            html = self.fetcher.fetch(
                url
            )

            tree = self.parser.parse(
                html
            )

            result = (
                self.page_parser.parse_page(
                    tree,
                    url,
                )
            )

            yield from result.items

            url = result.next_url
```

Đây là một **generator pipeline** rất đẹp.

---

# 15. Tại sao dùng `yield`?

Không nên:

```python
items = []

while url:
    ...
    items.extend(result.items)

return items
```

Nếu website có:

```text
10,000 chapters
```

ta sẽ giữ toàn bộ:

```text
10,000 ChapterLink
```

trong RAM.

Với:

```python
yield
```

ta xử lý từng item:

```text
Page 1
 ↓
yield Chapter 1
 ↓
yield Chapter 2
 ↓
...

Page 2
 ↓
yield Chapter 21
```

---

# 16. Nhưng cần chống pagination loop

Website lỗi có thể trả:

```text
Page 1
 ↓
Page 2
 ↓
Page 1
 ↓
Page 2
```

Nếu:

```python
while url:
```

thì crawler chạy vô hạn.

---

# 17. Dùng `visited`

```python
class Paginator:

    def crawl(self, start_url):

        url = start_url

        visited = set()

        while url:

            if url in visited:
                break

            visited.add(url)

            ...
```

Đây là kỹ thuật rất quan trọng trong crawler.

---

# 18. Phiên bản tốt hơn

```python
class Paginator:

    def __init__(
        self,
        fetcher,
        parser,
        page_parser,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.page_parser = page_parser

    def crawl(
        self,
        start_url: str,
    ):

        url = start_url
        visited: set[str] = set()

        while url:

            if url in visited:
                break

            visited.add(url)

            html = self.fetcher.fetch(
                url
            )

            tree = self.parser.parse(
                html
            )

            result = (
                self.page_parser.parse_page(
                    tree,
                    url,
                )
            )

            yield from result.items

            url = result.next_url
```

---

# 19. Deduplicate Chapter URL

Một website có thể chứa:

```text
Page 1
Chapter 1
Chapter 2

Page 2
Chapter 2
Chapter 3
```

Nếu không deduplicate:

```text
Chapter 2
Chapter 2
```

Do đó:

```python
seen_chapters: set[str] = set()
```

---

# 20. Deduplicate trong crawler

```python
seen_chapters = set()

for chapter in paginator.crawl(
    story.url
):

    if chapter.url in seen_chapters:
        continue

    seen_chapters.add(
        chapter.url
    )

    yield chapter
```

---

# 21. Tạo ChapterCrawler

```python
class ChapterCrawler:

    def __init__(
        self,
        fetcher,
        parser,
        chapter_parser,
        repository,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.chapter_parser = (
            chapter_parser
        )
        self.repository = repository
```

---

# 22. `crawl_chapter`

```python
def crawl_chapter(
    self,
    chapter_link: ChapterLink,
    story_id: int,
):

    html = self.fetcher.fetch(
        chapter_link.url
    )

    tree = self.parser.parse(
        html
    )

    chapter = (
        self.chapter_parser.parse(
            tree,
            url=chapter_link.url,
            story_id=story_id,
        )
    )

    self.repository.save(
        chapter
    )

    return chapter
```

---

# 23. StoryCrawler

Bây giờ:

```python
class StoryCrawler:

    def __init__(
        self,
        fetcher,
        parser,
        story_parser,
        story_repository,
        paginator,
        chapter_crawler,
    ):
        ...
```

Đây bắt đầu trở nên lớn.

Vì vậy **đừng nhét tất cả vào một class**.

Ta tách orchestration.

---

# 24. Crawl Story Metadata

```python
def crawl_story(
    url,
):

    html = fetcher.fetch(url)

    tree = parser.parse(html)

    story = story_parser.parse(
        tree,
        url,
    )

    story_id = (
        story_repository.save(
            story
        )
    )

    return story_id
```

Sau đó pagination:

```python
for chapter_link in paginator.crawl(
    url
):
    ...
```

---

# 25. Story + Chapter Pipeline

```python
story_id = crawl_story(
    story_url
)

for chapter_link in paginator.crawl(
    story_url
):

    chapter_crawler.crawl_chapter(
        chapter_link,
        story_id,
    )
```

Luồng:

```text
Story URL
   │
   ▼
StoryParser
   │
   ▼
Story
   │
   ▼
Save Story
   │
   ▼
story_id
   │
   ▼
Paginator
   │
   ├── Chapter 1
   ├── Chapter 2
   ├── Chapter 3
   └── ...
          │
          ▼
    ChapterCrawler
          │
          ▼
    ChapterParser
          │
          ▼
        SQLite
```

---

# 26. Đây chính là Crawl Orchestration

Ta có thể tạo:

```python
class StoryCrawlService:

    def __init__(
        self,
        story_crawler,
        paginator,
        chapter_crawler,
    ):
        self.story_crawler = (
            story_crawler
        )
        self.paginator = paginator
        self.chapter_crawler = (
            chapter_crawler
        )
```

---

# 27. Method `crawl`

```python
def crawl(
    self,
    story_url: str,
):

    story_id = (
        self.story_crawler.crawl_story(
            story_url
        )
    )

    seen = set()

    for chapter_link in (
        self.paginator.crawl(
            story_url
        )
    ):

        if chapter_link.url in seen:
            continue

        seen.add(
            chapter_link.url
        )

        self.chapter_crawler.crawl_chapter(
            chapter_link,
            story_id,
        )
```

Đây là **Application Service** theo đúng tư duy Clean Architecture mà bạn đã học.

---

# 28. Tại sao đây là Application Service?

Nó không biết:

```text
CSS selector
SQL
HTTPX internals
```

Nó chỉ điều phối:

```text
crawl story
 ↓
get chapter links
 ↓
crawl chapters
```

Domain/application orchestration nằm ở đây.

---

# 29. Giới hạn số chapter

Khi debug crawler, không muốn crawl 10.000 chapter.

Cho phép:

```python
max_chapters: int | None = None
```

Ví dụ:

```python
count = 0

for chapter_link in paginator.crawl(
    story_url
):

    if (
        max_chapters is not None
        and count >= max_chapters
    ):
        break

    chapter_crawler.crawl_chapter(
        chapter_link,
        story_id,
    )

    count += 1
```

Chạy:

```text
max_chapters=10
```

→ chỉ crawl 10 chapter.

---

# 30. Giới hạn pagination

Tương tự:

```python
max_pages: int | None = None
```

Paginator:

```python
page_count = 0

while url:

    if (
        max_pages is not None
        and page_count >= max_pages
    ):
        break

    ...

    page_count += 1
```

Cực kỳ hữu ích khi development.

---

# 31. Retry sẽ đặt ở đâu?

Không đặt:

```python
StoryParser
```

vì Parser không biết network.

Không đặt:

```python
ChapterCrawler
```

nếu có thể tránh.

Retry nên nằm gần:

```text
HTTPX
```

tức:

```text
Fetcher
```

Architecture:

```text
ChapterCrawler
      ↓
   Fetcher
      ↓
 Retry
      ↓
   HTTPX
```

Buổi 7 chúng ta đã nói về HTTPX + retry; bây giờ bạn thấy **retry thuộc layer nào**.

---

# 32. Status code

Fetcher:

```python
response = self.client.get(
    url
)

response.raise_for_status()
```

Nếu:

```text
404
```

thì:

```text
ChapterCrawler
 ↓
Fetcher
 ↓
HTTPStatusError
```

Application service có thể quyết định:

```text
retry?
skip?
log?
mark failed?
```

---

# 33. Không nên catch mọi exception

Tránh:

```python
try:
    ...
except Exception:
    pass
```

Đây là anti-pattern.

Nếu HTML parser bug:

```text
TypeError
```

mà bạn nuốt mất:

```text
pass
```

crawler sẽ âm thầm mất dữ liệu.

Tốt hơn:

```python
try:
    ...
except httpx.HTTPError:
    ...
```

và lỗi parse để lộ hoặc log riêng.

---

# 34. Resume Crawl

Đây là một vấn đề cực kỳ quan trọng với crawler truyện.

Giả sử:

```text
1000 chapters
```

Crawler chạy:

```text
Chapter 1 ✓
Chapter 2 ✓
...
Chapter 500 ✓
Chapter 501 ✗
```

Không muốn chạy lại từ đầu.

Vì database có:

```sql
chapters.url UNIQUE
```

crawler có thể:

```text
Chapter 1 → already exists
Chapter 2 → already exists
...
Chapter 500 → already exists
Chapter 501 → crawl
```

Đây là nền móng cho **resume capability**.

---

# 35. Tốt hơn nữa: trạng thái Chapter

Sau này Chapter có thể có:

```text
pending
crawling
success
failed
```

Database:

```text
chapters
├── id
├── story_id
├── url
├── title
├── content
└── status
```

Ví dụ:

```text
Chapter 1   success
Chapter 2   success
Chapter 3   failed
Chapter 4   pending
```

Đây sẽ là bước rất gần với:

```text
Redis Queue
Worker
Retry
```

mà bạn đang học.

---

# 36. Đừng đưa Queue vào hôm nay

Hiện tại:

```text
Paginator
 ↓
for
 ↓
ChapterCrawler
```

Ở tương lai:

```text
Paginator
 ↓
Queue
 ↓
Worker
 ↓
ChapterCrawler
```

Tức là:

```text
Hôm nay

Paginator → ChapterCrawler


Sau này

Paginator → Queue → Worker → ChapterCrawler
```

Đây là một architectural seam rất tốt.

---

# 37. Testing Pagination

Đây là phần bắt buộc.

Fixture page 1:

```html
<div class="chapter-list">
    <a href="/chapter/1">
        Chương 1
    </a>

    <a href="/chapter/2">
        Chương 2
    </a>
</div>

<a class="next"
   href="/story/python?page=2">
    Next
</a>
```

Page 2:

```html
<div class="chapter-list">
    <a href="/chapter/3">
        Chương 3
    </a>
</div>
```

Không có:

```html
<a class="next">
```

---

# 38. FakeFetcher cho pagination

```python
class FakeFetcher:

    def __init__(self, pages):
        self.pages = pages

    def fetch(self, url):
        return self.pages[url]
```

Setup:

```python
pages = {
    "https://example.com/story/python":
        page1_html,

    "https://example.com/story/python?page=2":
        page2_html,
}
```

---

# 39. Test

```python
def test_pagination():

    fetcher = FakeFetcher(
        pages
    )

    parser = Parser()

    page_parser = StoryPageParser()

    paginator = Paginator(
        fetcher,
        parser,
        page_parser,
    )

    chapters = list(
        paginator.crawl(
            "https://example.com/story/python"
        )
    )

    assert len(chapters) == 3

    assert chapters[0].number == 1
    assert chapters[1].number == 2
    assert chapters[2].number == 3
```

---

# 40. Test pagination loop

Fake:

```text
page1 → page2
page2 → page1
```

Crawler phải dừng.

```python
def test_pagination_loop():

    ...

    chapters = list(
        paginator.crawl(
            "https://example.com/page1"
        )
    )

    assert len(chapters) > 0
```

Quan trọng hơn:

```text
test không bị infinite loop
```

---

# 41. Test duplicate chapter

Page 1:

```text
Chapter 1
Chapter 2
```

Page 2:

```text
Chapter 2
Chapter 3
```

Application service phải cho:

```text
Chapter 1
Chapter 2
Chapter 3
```

không phải:

```text
Chapter 1
Chapter 2
Chapter 2
Chapter 3
```

---

# 42. Một điểm cần suy nghĩ: dedup ở đâu?

Có 3 lựa chọn:

### Parser

Không nên.

Parser chỉ nên parse HTML.

### Paginator

Có thể.

Nhưng paginator chỉ nên quan tâm pagination.

### Application Service

**Rất hợp lý.**

```text
Paginator
 ↓
raw ChapterLink
 ↓
Application Service
 ↓
deduplicate
 ↓
ChapterCrawler
```

Database cũng có:

```text
UNIQUE(url)
```

làm lớp bảo vệ cuối cùng.

---

# 43. Defense in depth

Một crawler production nên có nhiều lớp bảo vệ:

```text
Parser
 ↓
validate URL
 ↓
Application
 ↓
deduplicate
 ↓
Repository
 ↓
UNIQUE(url)
```

Không nên phụ thuộc chỉ một lớp.

---

# 44. Architecture sau Buổi 17

```text
                         Story URL
                             │
                             ▼
                       StoryCrawler
                             │
                             ▼
                           Story
                             │
                             ▼
                    StoryRepository
                             │
                             ▼
                         story_id
                             │
                             ▼
                         Paginator
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
            Page 1        Page 2        Page 3
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                     ChapterLink[]
                             │
                             ▼
                        Deduplicate
                             │
                             ▼
                     ChapterCrawler
                             │
                             ▼
                     ChapterParser
                             │
                             ▼
                         Chapter
                             │
                             ▼
                    ChapterRepository
                             │
                             ▼
                          SQLite
```

---

# 🧠 45. Một thay đổi tư duy rất quan trọng

Ở Buổi 16:

```text
Story
 ↓
Chapter Links
```

Ở Buổi 17:

```text
Story
 ↓
Discovery
 ↓
Pagination
 ↓
Deduplication
 ↓
Scheduling
 ↓
Crawling
 ↓
Persistence
```

Đây bắt đầu giống **crawler framework** thực sự.

---

# 📝 Bài tập Buổi 17

### Bài 1 — Pagination

Tạo:

```text
page1.html
page2.html
page3.html
```

và crawler phải lấy được:

```text
Chapter 1
...
Chapter 30
```

---

### Bài 2 — Relative URL

Test:

```text
/chapter/1
chapter/2
https://example.com/chapter/3
```

đều chuyển thành absolute URL.

---

### Bài 3 — Duplicate

Cho:

```text
Page 1:
1
2
3

Page 2:
3
4
5
```

Kết quả:

```text
1
2
3
4
5
```

---

### Bài 4 — Pagination loop

Cho:

```text
page1 → page2
page2 → page1
```

Crawler phải tự dừng.

---

### Bài 5 — Max pages

```python
paginator.crawl(
    start_url,
    max_pages=2,
)
```

chỉ được fetch 2 page.

---

### Bài 6 — Max chapters

```python
crawl_story(
    url,
    max_chapters=10,
)
```

chỉ crawl 10 chapter.

---

# 🎯 Bài tập kiến trúc

Hãy tự trả lời 5 câu này:

**1. Retry nằm ở đâu?**

→ `Fetcher`

**2. CSS Selector nằm ở đâu?**

→ `Parser`

**3. Deduplicate chapter URL nằm ở đâu?**

→ Application/orchestration layer

**4. Duplicate cuối cùng được bảo vệ ở đâu?**

→ SQLite `UNIQUE(url)`

**5. Queue sau này nên chèn ở đâu?**

Hiện tại:

```text
Paginator
   ↓
ChapterCrawler
```

Sau này:

```text
Paginator
   ↓
Queue
   ↓
Worker
   ↓
ChapterCrawler
```

Nếu bạn hiểu được 5 điểm này, thì chúng ta đã có một kiến trúc rất tốt để bước sang **Buổi 18 — Plugin Parser**.

Ở Buổi 18, vấn đề sẽ trở nên thú vị hơn: **Site A dùng `.chapter-list a`, Site B dùng `.list-chapter a`, Site C lại dùng JavaScript/HTML khác hoàn toàn**. Chúng ta sẽ thiết kế:

```text
Crawler Core
     │
     ▼
Parser Interface
     │
     ├── SiteAParser
     ├── SiteBParser
     └── SiteCParser
```

để **core crawler không cần biết website cụ thể**.
