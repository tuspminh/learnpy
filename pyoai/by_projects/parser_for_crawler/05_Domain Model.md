# Buổi 5 — Domain Model: Novel, NovelSummary, ChapterSummary

Hôm nay chúng ta quay lại **Domain Layer**. Đây là bước rất quan trọng trước khi viết parser thực tế.

Mục tiêu:

```text
HTML
 ↓
Parser
 ↓
Domain Model
```

Parser không nên trả về `dict` kiểu:

```python
{
    "title": "...",
    "author": "...",
}
```

mà phải trả về object có ý nghĩa trong domain:

```python
NovelSummary(...)
Novel(...)
ChapterSummary(...)
```

---

# 1. Tại sao phải có `NovelSummary`?

Listing page của chúng ta chỉ có:

```text
title
author
url
```

Ví dụ:

```text
Truyện A
Nguyễn Văn A
/truyen-a
```

Trong khi Novel Detail có:

```text
title
author
url
cover
description
status
chapter list
```

Nếu dùng chung:

```python
Novel
```

cho cả hai thì sẽ xảy ra:

```python
Novel(
    title="Truyện A",
    author="Nguyễn Văn A",
    url="/truyen-a",
    cover=None,
    description=None,
    status=None,
)
```

Nhìn vào object không biết:

> `cover=None` là website không có cover hay listing page không chứa cover?

Đây là lý do chúng ta tách:

```text
NovelSummary
    ↓
dữ liệu tối thiểu từ listing

Novel
    ↓
dữ liệu đầy đủ từ detail
```

---

# 2. `NovelSummary`

Tạo:

```text
src/crawler/domain/novel.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str
```

`frozen=True` có ý nghĩa gì?

Listing result là dữ liệu được parser tạo ra.

Sau khi tạo:

```python
novel = NovelSummary(
    title="Truyện A",
    author="Nguyễn Văn A",
    url="https://example.com/truyen-a",
)
```

không nên cho code phía sau tùy ý:

```python
novel.title = "Something else"
```

Domain object này có thể immutable.

---

# 3. Tại sao `Novel` không frozen?

Novel có thể trải qua nhiều lifecycle:

```text
discover
   ↓
metadata updated
   ↓
chapters updated
   ↓
status updated
```

Ví dụ:

```python
novel.status = "completed"
```

Do đó trước mắt:

```python
@dataclass
class Novel:
```

là hợp lý.

Sau này nếu chúng ta xây Aggregate Root nghiêm ngặt hơn, ta sẽ thay đổi cách mutation.

---

# 4. `Novel`

```python
@dataclass
class Novel:
    title: str
    author: str
    url: str
    cover: str | None = None
    description: str | None = None
    status: str | None = None
```

Ví dụ:

```python
novel = Novel(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="https://example.com/dptk",
    cover="https://example.com/dptk.jpg",
    description="...",
    status="Hoàn thành",
)
```

---

# 5. `ChapterSummary`

Chapter listing chỉ có:

```text
title
url
```

Vì vậy:

```python
@dataclass(frozen=True)
class ChapterSummary:
    title: str
    url: str
```

Ví dụ:

```python
ChapterSummary(
    title="Chương 1: Bắt đầu",
    url="https://example.com/chuong-1",
)
```

Nó **không có content**.

---

# 6. `Chapter`

Chapter detail:

```text
title
chapter_no
content
url
```

```python
from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    chapter_no: int | None
    content: str
    url: str
```

Ví dụ:

```python
chapter = Chapter(
    title="Chương 1: Bắt đầu",
    chapter_no=1,
    content="...",
    url="https://example.com/chuong-1",
)
```

---

# 7. `chapter_no` có nên bắt buộc?

Không nhất thiết.

Có website:

```text
Chương 1
Chương 2
Chương 3
```

rất dễ parse.

Nhưng có website:

```text
Phiên ngoại
Ngoại truyện
Lời tác giả
Chương cuối
```

Không phải chapter nào cũng có số.

Do đó:

```python
chapter_no: int | None
```

là hợp lý hơn:

```python
chapter_no: int
```

---

# 8. Nhưng `title` thì sao?

`title` là required.

Không có title:

```text
Chapter
```

không có ý nghĩa.

Tương tự:

```text
NovelSummary
    title   REQUIRED
    author  REQUIRED
    url     REQUIRED
```

---

# 9. `author` có thể `None` không?

Với thiết kế hiện tại:

```python
author: str
```

Tôi khuyến nghị coi author là required đối với **listing**.

Nhưng đây là quyết định phụ thuộc website.

Nếu một website có:

```text
Truyện A
Không rõ tác giả
```

thì parser có thể normalize thành:

```python
author = "Unknown"
```

hoặc chúng ta có thể đổi Domain thành:

```python
author: str | None
```

Điểm quan trọng là:

> Domain phải phản ánh rule của application, không phải ép tất cả website giống nhau một cách máy móc.

Trong project hiện tại, ta giữ:

```python
author: str
```

---

# 10. URL là dữ liệu quan trọng

Một lỗi thiết kế thường gặp:

```python
Novel(
    title="Truyện A",
    author="ABC",
    url="/truyen-a",
)
```

rồi Repository tự quyết định URL.

Tôi muốn Parser chuẩn hóa URL trước khi tạo Domain Model.

Tức là:

```text
HTML
 ↓
href="/truyen-a"
 ↓
Parser URL Resolver
 ↓
"https://example.com/truyen-a"
 ↓
Novel
```

Như vậy Domain nhận URL chuẩn.

Phần URL Resolver chúng ta sẽ học riêng sau.

---

# 11. Có nên tạo `Url` Value Object ngay?

DDD thuần túy có thể làm:

```python
@dataclass(frozen=True)
class Url:
    value: str
```

Nhưng tôi **chưa muốn làm ngay**.

Nếu bây giờ tạo:

```text
Url
Novel
Author
Title
Status
Description
ChapterNumber
```

chúng ta sẽ tạo quá nhiều abstraction trước khi hiểu crawler thực tế.

Hiện tại:

```python
url: str
```

là đủ.

Sau khi Parser chạy thực tế, chúng ta sẽ đánh giá Value Object nào thực sự có invariant.

---

# 12. Domain Model hoàn chỉnh

`domain/novel.py`:

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

# 13. Pagination Model

Bây giờ quay lại:

```text
ListingPage
NovelPage
ChapterPage
```

`domain/parser_result.py`:

```python
from dataclasses import dataclass

from .chapter import Chapter
from .novel import (
    Novel,
    NovelSummary,
    ChapterSummary,
)


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

# 14. Tại sao `next_url` nằm trong Result?

Ví dụ listing:

```text
https://example.com/truyen
```

HTML có:

```html
<a href="/truyen/trang-2">Trang 2</a>
```

Parser trả:

```python
ListingPage(
    items=[...],
    next_url="https://example.com/truyen/trang-2",
)
```

Application sẽ quyết định:

```python
while next_url:
    page_source = fetcher.fetch(next_url)

    result = parser.parse_listing(
        page_source,
        next_url,
    )

    save(result.items)

    next_url = result.next_url
```

Parser **không fetch page 2**.

---

# 15. Novel pagination cũng giống vậy

Novel detail:

```text
Novel
    │
    └── Chapter page 1
             │
             ▼
          page 2
             │
             ▼
          page 3
```

Parser page 1 trả:

```python
NovelPage(
    novel=novel,
    chapters=[
        ChapterSummary(...),
        ChapterSummary(...),
    ],
    next_url="https://example.com/truyen-a/trang-2",
)
```

Application điều phối page 2.

---

# 16. Có nên đưa `chapters` vào `Novel` không?

Đây là câu hỏi DDD khá quan trọng.

Có thể thiết kế:

```python
Novel(
    ...,
    chapters=[...]
)
```

Nhưng tôi **không khuyến nghị ở giai đoạn hiện tại**.

Bởi vì:

```text
Novel metadata
```

và:

```text
Chapter listing
```

có lifecycle khác nhau.

Novel:

```text
title
author
cover
description
status
```

Chapter:

```text
title
url
```

và chapter list có pagination.

Do đó:

```text
Novel
   +
ChapterSummary[]
```

được trả về trong `NovelPage`.

Đây là **Parser Result**, không phải nhất thiết là Aggregate structure.

---

# 17. Phân biệt Domain Entity và Parse Result

Đây là điểm rất quan trọng.

### Entity

```python
Novel(...)
Chapter(...)
```

là domain data.

### Parse Result

```python
NovelPage(...)
ListingPage(...)
ChapterPage(...)
```

là kết quả của quá trình parse.

Ví dụ:

```text
HTML
 ↓
Parser
 ↓
NovelPage
 ├── Novel
 ├── ChapterSummary[]
 └── next_url
```

`next_url` không phải thuộc tính bản chất của Novel.

Nó là:

> thông tin điều hướng của trang HTML hiện tại.

Vì vậy không đặt:

```python
Novel.next_url
```

---

# 18. Tương tự `ListingPage`

Không làm:

```python
NovelSummary.next_url
```

vì:

```text
NovelSummary
```

là một item.

Còn:

```text
ListingPage
```

là container của page.

```text
ListingPage
 ├── items
 └── next_url
```

Rất rõ ràng.

---

# 19. Immutable list?

Hiện tại:

```python
items: list[NovelSummary]
```

là đủ.

Nhưng:

```python
@dataclass(frozen=True)
class ListingPage:
```

không làm list bên trong immutable hoàn toàn.

Ví dụ:

```python
page.items.append(...)
```

vẫn có thể xảy ra.

Nếu sau này cần strict immutability, ta có thể dùng:

```python
tuple[NovelSummary, ...]
```

Nhưng chưa cần.

Tôi ưu tiên:

```python
list
```

vì application sẽ dễ làm việc hơn.

---

# 20. Domain validation

Có nên validate ngay trong dataclass?

Ví dụ:

```python
@dataclass
class Novel:

    def __post_init__(self):
        if not self.title:
            raise ValueError(...)
```

**Có thể**, nhưng chưa nên làm quá nhiều.

Hiện tại Parser đã có:

```text
MissingFieldError
```

nên Parser chịu trách nhiệm:

```text
HTML extraction validation
```

Domain chịu trách nhiệm:

```text
Domain invariant
```

Hai loại validation khác nhau.

---

# 21. Ví dụ phân biệt

HTML:

```html
<h1 class="title"></h1>
```

Parser thấy:

```text
title = ""
```

Đây là:

```text
Parser validation
```

→ `MissingFieldError`.

Nhưng nếu Domain có invariant:

```text
title phải <= 500 ký tự
```

thì:

```text
Domain validation
```

→ `ValueError` hoặc DomainError.

---

# 22. Không nên làm thế này

```python
@dataclass
class Novel:

    def __post_init__(self):
        if not self.title:
            raise MissingFieldError(...)
```

`MissingFieldError` là lỗi **Parser**.

Domain không nên biết:

```text
Parser
Selectolax
CSS selector
HTML
```

Domain chỉ biết invariant của chính nó.

---

# 23. Domain Error sau này

Sau này có thể:

```text
domain/
├── errors.py
├── novel.py
└── chapter.py
```

Ví dụ:

```python
class DomainError(Exception):
    pass
```

Nhưng hôm nay chưa cần.

---

# 24. Test Domain Models

Tạo:

```text
tests/
└── domain/
    ├── test_novel.py
    └── test_chapter.py
```

`test_novel.py`:

```python
from crawler.domain.novel import (
    Novel,
    NovelSummary,
    ChapterSummary,
)


def test_novel_summary():
    novel = NovelSummary(
        title="Truyện A",
        author="Tác giả A",
        url="https://example.com/a",
    )

    assert novel.title == "Truyện A"
    assert novel.author == "Tác giả A"
    assert novel.url == "https://example.com/a"


def test_novel_summary_is_immutable():
    novel = NovelSummary(
        title="Truyện A",
        author="Tác giả A",
        url="https://example.com/a",
    )

    try:
        novel.title = "Truyện B"
    except Exception:
        pass
    else:
        raise AssertionError(
            "NovelSummary should be immutable"
        )


def test_novel():
    novel = Novel(
        title="Truyện A",
        author="Tác giả A",
        url="https://example.com/a",
        cover="https://example.com/a.jpg",
        description="Mô tả",
        status="Đang ra",
    )

    assert novel.title == "Truyện A"
    assert novel.cover.endswith(".jpg")
    assert novel.status == "Đang ra"


def test_novel_optional_fields():
    novel = Novel(
        title="Truyện A",
        author="Tác giả A",
        url="https://example.com/a",
    )

    assert novel.cover is None
    assert novel.description is None
    assert novel.status is None
```

---

# 25. Test Chapter

```python
from crawler.domain.chapter import Chapter
from crawler.domain.novel import ChapterSummary


def test_chapter_summary():
    chapter = ChapterSummary(
        title="Chương 1",
        url="https://example.com/c1",
    )

    assert chapter.title == "Chương 1"
    assert chapter.url == "https://example.com/c1"


def test_chapter():
    chapter = Chapter(
        title="Chương 1",
        chapter_no=1,
        content="Nội dung chương 1",
        url="https://example.com/c1",
    )

    assert chapter.title == "Chương 1"
    assert chapter.chapter_no == 1
    assert chapter.content == "Nội dung chương 1"


def test_chapter_without_number():
    chapter = Chapter(
        title="Ngoại truyện",
        chapter_no=None,
        content="Nội dung",
        url="https://example.com/ngoai-truyen",
    )

    assert chapter.chapter_no is None
```

---

# 26. Test Parser Result

```python
from crawler.domain.novel import (
    NovelSummary,
    Novel,
    ChapterSummary,
)

from crawler.domain.chapter import Chapter

from crawler.domain.parser_result import (
    ListingPage,
    NovelPage,
    ChapterPage,
)


def test_listing_page():
    page = ListingPage(
        items=[
            NovelSummary(
                title="Truyện A",
                author="A",
                url="https://example.com/a",
            ),
            NovelSummary(
                title="Truyện B",
                author="B",
                url="https://example.com/b",
            ),
        ],
        next_url="https://example.com/trang-2",
    )

    assert len(page.items) == 2
    assert page.next_url.endswith("trang-2")


def test_listing_last_page():
    page = ListingPage(
        items=[],
        next_url=None,
    )

    assert page.next_url is None
```

---

# 27. Một lỗi kiến trúc cần tránh

Không tạo:

```python
class NovelParserResult:
    ...
```

rồi nhét:

```text
title
author
url
cover
description
status
chapters
next_page
```

tất cả vào một object duy nhất cho mọi trường hợp.

Ta đã có:

```text
NovelSummary
Novel
ChapterSummary
Chapter
ListingPage
NovelPage
ChapterPage
```

Mỗi object có **một ý nghĩa rõ ràng**.

---

# 28. Mapping giữa HTML và Domain

Đây sẽ là mục tiêu của Parser trong các buổi sau:

```text
LISTING HTML

.story
 ├── title
 ├── author
 └── href

        ↓

NovelSummary
```

---

```text
NOVEL HTML

.book
 ├── title
 ├── author
 ├── cover
 ├── description
 ├── status
 │
 └── chapters
       ├── title
       └── url

        ↓

NovelPage
 ├── Novel
 ├── ChapterSummary[]
 └── next_url
```

---

```text
CHAPTER HTML

.chapter
 ├── title
 ├── chapter number
 └── content

        ↓

ChapterPage
 └── Chapter
```

---

# 29. Architecture sau Buổi 5

```text
                     DOMAIN
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
     Novel          Chapter       Parser Result
       │               │                │
       ├─ Novel        └─ Chapter       ├─ ListingPage
       └─ Summary                       ├─ NovelPage
          └─ ChapterSummary             └─ ChapterPage


                 INFRASTRUCTURE
                       │
                       ▼
                SelectolaxDocument
                       │
                       ▼
                  Site Parser
                       │
                       ▼
                  Domain Model
```

---

# 30. Một nguyên tắc DDD cần nhớ

Đừng nghĩ:

```text
HTML structure = Domain structure
```

Hai cái **không giống nhau**.

Ví dụ HTML:

```text
<div class="story">
    <h3>...</h3>
    <span>...</span>
</div>
```

là cấu trúc của **website**.

Domain:

```python
NovelSummary(
    title=...,
    author=...,
    url=...,
)
```

là cấu trúc của **ứng dụng crawler**.

Parser chính là lớp chuyển đổi:

```text
External World
      │
      ▼
HTML / Website
      │
      ▼
Parser
      │
      ▼
Our Domain
```

Đây chính là lý do Parser nằm ở **Infrastructure/Adapter boundary**, chứ không nằm trong Domain.

---

## Bài tập Buổi 5

Hãy hoàn thiện 3 file:

```text
crawler/
└── domain/
    ├── novel.py
    ├── chapter.py
    └── parser_result.py
```

với:

```text
NovelSummary
Novel
ChapterSummary
Chapter

ListingPage
NovelPage
ChapterPage
```

Sau đó chạy test và kiểm tra các case:

```text
✓ NovelSummary có title/author/url
✓ NovelSummary immutable
✓ Novel có optional cover/description/status
✓ Chapter có chapter_no
✓ Chapter có thể chapter_no=None
✓ ListingPage có next_url
✓ ListingPage cuối có next_url=None
```

---

### Bức tranh chúng ta đã hoàn thành

```text
Buổi 1
Architecture
     ↓
Buổi 2
Selectolax
     ↓
Buổi 3
Parser Protocol
     ↓
Buổi 4
ParserError + Validation
     ↓
Buổi 5
Domain Models
     ↓
Buổi 6
???
```

**Buổi 6** sẽ bắt đầu phần thực chiến: chúng ta sẽ xây **`BaseSiteParser` + URL Resolver + Parser Context**, sau đó dùng một HTML listing giả lập để viết **`parse_listing()` đầu tiên**. Từ đó mới bắt đầu đi sâu vào `NovelCardExtractor`, pagination và các selector đặc thù của từng website.
