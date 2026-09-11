Được. Với yêu cầu này, chúng ta sẽ xây **Parser Framework cho app crawl truyện chữ** theo đúng hướng DDD + SOLID, và **tách hoàn toàn Parser khỏi HTTP**.

Kiến trúc ta sẽ giữ nhất quán với framework crawler trước đây:

```text
HTTPX Client / Fetcher
        │
        │ page-source: str
        ▼
┌──────────────────────┐
│      Parser           │
│   Selectolax          │
└──────────┬───────────┘
           │
           ▼
      Domain Model
           │
           ▼
      Application
```

Parser **không biết HTTPX**, không request URL, không retry, không proxy. Nó chỉ nhận `page_source` và trả về Domain Model.

---

# ROADMAP — PARSER FRAMEWORK

Tôi đề xuất chia thành **30 buổi**, đi từ đơn giản → production-style.

## Phần I — Parser Foundation

### Buổi 1 — Kiến trúc Parser

Thiết kế:

```text
page-source
    ↓
Selectolax
    ↓
DOM
    ↓
Parser
    ↓
Domain Model
```

Phân biệt:

```text
Fetcher
Parser
Domain
Application
```

---

### Buổi 2 — Selectolax Foundation

Học:

```python
HTMLParser
Node
css()
css_first()
text()
attributes
parent
children
```

và xây:

```text
SelectolaxDocument
```

---

### Buổi 3 — Parser Interface

Thiết kế abstraction:

```python
class Parser(Protocol):
    ...
```

SOLID:

* DIP
* ISP
* OCP

---

### Buổi 4 — Parser Result

Thiết kế kết quả parse:

```text
ParseResult
ParseError
ParseStatus
```

để parser không trả về dữ liệu hỗn loạn.

---

# Phần II — Domain Model

## Buổi 5 — Novel Domain Model

```text
Novel
 ├── id
 ├── title
 ├── author
 ├── url
 ├── cover
 ├── description
 └── status
```

---

## Buổi 6 — Chapter Domain Model

```text
Chapter
 ├── title
 ├── chapter_no
 ├── url
 └── content
```

---

## Buổi 7 — Listing Models

Thiết kế:

```text
NovelSummary
ChapterSummary
```

Vì listing **không cần Novel đầy đủ**.

```text
NovelSummary
    title
    author
    url
```

và:

```text
ChapterSummary
    title
    url
```

---

# Phần III — Listing Parser

## Buổi 8 — Parse Novel Listing

Input:

```text
listing page source
```

Output:

```python
list[NovelSummary]
```

Ví dụ:

```text
Novel A
Author A
/url-a

Novel B
Author B
/url-b
```

---

## Buổi 9 — Extract Novel Card

Tách logic:

```text
ListingParser
      ↓
NovelCardExtractor
```

Mục tiêu:

```python
NovelSummary(
    title=...,
    author=...,
    url=...
)
```

---

## Buổi 10 — Listing Pagination

Parse:

```text
trang-2
trang-3
trang-4
```

Output:

```python
next_url
```

Ví dụ:

```text
/current
   ↓
/trang-2
```

---

## Buổi 11 — Pagination Robustness

Xử lý:

```text
không có next
next bị thiếu
relative URL
absolute URL
?page=2
/trang-2
```

---

## Buổi 12 — Listing Parser hoàn chỉnh

Kết hợp:

```text
parse_listing()
parse_next_page()
```

---

# Phần IV — Novel Parser

## Buổi 13 — Parse Novel Detail

Input:

```text
novel detail page-source
```

Output:

```python
Novel(
    title=...,
    author=...,
    url=...,
    cover=...,
    description=...,
    status=...
)
```

---

## Buổi 14 — Novel Metadata Extractor

Tách:

```text
TitleExtractor
AuthorExtractor
CoverExtractor
DescriptionExtractor
StatusExtractor
```

Nhưng chúng ta sẽ cân bằng abstraction, **không tách class một cách máy móc**.

---

## Buổi 15 — Chapter Listing trong Novel

Parse:

```text
Chapter 1 → /chuong-1
Chapter 2 → /chuong-2
Chapter 3 → /chuong-3
```

Output:

```python
list[ChapterSummary]
```

---

## Buổi 16 — Chapter Listing Pagination

Xử lý:

```text
chapter list
      ↓
trang-2
      ↓
trang-3
      ↓
...
```

---

## Buổi 17 — Novel Parser hoàn chỉnh

Một novel page có:

```text
Novel
 ├── metadata
 └── chapters
       ├── page 1
       ├── page 2
       └── page 3
```

Nhưng Parser chỉ parse **từng page**.

Application mới chịu trách nhiệm:

```text
fetch page 1
fetch page 2
fetch page 3
```

Đây là điểm kiến trúc **rất quan trọng**.

---

# Phần V — Chapter Parser

## Buổi 18 — Parse Chapter

Input:

```text
chapter page-source
```

Output:

```python
Chapter(
    title=...,
    chapter_no=...,
    content=...
)
```

---

## Buổi 19 — Extract Chapter Number

Xử lý:

```text
Chương 1
Chương 01
Chapter 1
Chap 1
第1章
```

Thiết kế:

```text
ChapterNumberExtractor
```

---

## Buổi 20 — Parse Content

Xử lý HTML:

```html
<div class="content">
    <p>...</p>
    <p>...</p>
</div>
```

thành:

```text
Paragraph 1

Paragraph 2

Paragraph 3
```

---

## Buổi 21 — Content Cleaner

Xử lý:

```text
ads
script
style
comments
navigation
empty nodes
whitespace
```

---

## Buổi 22 — Chapter Parser hoàn chỉnh

```python
parse_chapter(page_source)
```

---

# Phần VI — Plugin Architecture

## Buổi 23 — Site Parser Plugin

Thiết kế:

```text
Parser
   │
   ├── TruyenFullParser
   ├── SiteAParser
   ├── SiteBParser
   └── SiteCParser
```

---

## Buổi 24 — Parser Plugin Interface

Một plugin:

```python
class SiteParser(Protocol):
    def supports(self, url: str) -> bool:
        ...

    def parse_listing(...):
        ...

    def parse_novel(...):
        ...

    def parse_chapter(...):
        ...
```

---

## Buổi 25 — Parser Registry

```text
URL
 ↓
ParserRegistry
 ↓
SiteParser
```

Ví dụ:

```python
parser = registry.get_parser(url)
```

Crawler core không cần:

```python
if "truyenfull" in url:
    ...
elif "site-a" in url:
    ...
```

---

# Phần VII — Production Parser

## Buổi 26 — URL Resolver

Chuẩn hóa:

```text
/chuong-1
../chuong-1
https://example.com/chuong-1
```

thành URL chuẩn.

---

## Buổi 27 — Parser Error Handling

Thiết kế:

```text
MissingField
InvalidHTML
InvalidURL
InvalidChapterNumber
ParserNotSupported
```

---

## Buổi 28 — Parser Testing

Dùng fixture:

```text
tests/
    fixtures/
        listing.html
        listing_page2.html
        novel.html
        novel_page2.html
        chapter.html
```

Test:

```python
test_parse_listing()
test_parse_novel()
test_parse_chapter()
test_parse_next_page()
```

---

## Buổi 29 — Golden HTML Test

Giữ nguyên HTML thực tế:

```text
HTML
 ↓
Parser
 ↓
Expected Domain Model
```

Để khi website thay đổi HTML, test lập tức phát hiện.

---

# Phần VIII — Integration

## Buổi 30 — Parser + HTTPX + Crawler

Cuối cùng:

```text
                ┌──────────────┐
                │   HTTPX      │
                │   Fetcher    │
                └──────┬───────┘
                       │
                 page_source
                       │
                       ▼
                ┌──────────────┐
                │   Parser     │
                │ Selectolax   │
                └──────┬───────┘
                       │
                       ▼
                 Domain Model
                       │
                       ▼
                ┌──────────────┐
                │ Application  │
                │   Crawler    │
                └──────┬───────┘
                       │
                       ▼
                 Repository
                       │
                       ▼
                    SQLite
```

Trong đó:

**HTTPX Fetcher**

```text
URL
 ↓
HTTP request
 ↓
page_source
```

**Parser**

```text
page_source
 ↓
Selectolax
 ↓
Domain Model
```

**Application**

```text
pagination
retry
crawl order
orchestration
```

**Repository**

```text
Novel
Chapter
 ↓
SQLite
```

Đúng với nguyên tắc trước đây: **parser không gọi HTTP**.

---

# BUỔI 1 — Kiến trúc Parser

Trước tiên chúng ta chưa viết Selectolax code ngay. Ta phải xác định **boundary**.

## 1. Parser không phải Fetcher

Một thiết kế sai:

```python
class NovelParser:

    def parse(self, url):
        response = httpx.get(url)

        tree = HTMLParser(response.text)

        ...
```

Parser đang làm quá nhiều việc:

```text
Parser
 ├── HTTP
 ├── Retry
 ├── Proxy
 ├── Header
 ├── HTML parsing
 └── Domain extraction
```

Điều này vi phạm SRP và DIP.

---

# 2. Thiết kế đúng

Fetcher:

```python
page_source = fetcher.fetch(url)
```

Parser:

```python
novel = parser.parse_novel(
    page_source=page_source,
    url=url,
)
```

Parser **không biết**:

```text
httpx
proxy
timeout
retry
User-Agent
HTTP status
connection
```

Parser chỉ biết:

```text
HTML source
+
URL context
```

---

# 3. Ba loại parser chính

Ta có đúng 3 nhóm:

```text
Listing Parser
Novel Parser
Chapter Parser
```

### Listing

```text
page-source
     ↓
NovelSummary[]
     +
next_page
```

Domain:

```python
NovelSummary(
    title,
    author,
    url,
)
```

---

### Novel

```text
page-source
     ↓
Novel
+
ChapterSummary[]
+
next_page
```

---

### Chapter

```text
page-source
     ↓
Chapter
```

---

# 4. Một điểm thiết kế rất quan trọng

Không nên để:

```python
parse_novel()
```

tự động crawl tất cả chapter pages.

Ví dụ:

```python
def parse_novel(url):
    # request novel page
    # request chapter page 2
    # request chapter page 3
    # ...
```

**Không làm vậy.**

Parser chỉ xử lý:

```text
ONE page → ONE parse result
```

Ví dụ novel page đầu tiên:

```text
novel page 1
       ↓
parse_novel()
       ↓
Novel metadata
ChapterSummary page 1
next_page = page 2
```

Application sẽ làm:

```text
fetch novel page 1
        ↓
parse
        ↓
next = page 2
        ↓
fetch page 2
        ↓
parse
        ↓
next = page 3
        ↓
...
```

Đây là cách tách rất sạch:

```text
Parser       → hiểu HTML
Application  → điều phối crawl
Fetcher      → lấy HTML
Repository   → lưu dữ liệu
```

---

# 5. Domain Model sơ bộ

Chúng ta sẽ có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: str
```

Chapter listing:

```python
@dataclass(frozen=True)
class ChapterSummary:
    title: str
    url: str
```

Novel:

```python
@dataclass
class Novel:
    title: str
    author: str
    url: str
    cover: str | None
    description: str | None
    status: str | None
```

Chapter:

```python
@dataclass
class Chapter:
    title: str
    chapter_no: int | None
    content: str
    url: str
```

Chú ý:

```text
NovelSummary ≠ Novel
ChapterSummary ≠ Chapter
```

Listing chỉ cần dữ liệu nhẹ.

---

# 6. Parse Result

Ta cũng cần pagination.

Thay vì:

```python
return novels, next_url
```

ta có thể tạo:

```python
@dataclass(frozen=True)
class ListingPage:
    items: list[NovelSummary]
    next_url: str | None
```

Novel chapter listing:

```python
@dataclass(frozen=True)
class ChapterPage:
    items: list[ChapterSummary]
    next_url: str | None
```

Novel detail:

```python
@dataclass
class NovelPage:
    novel: Novel
    chapters: list[ChapterSummary]
    next_url: str | None
```

Chapter detail:

```python
@dataclass
class ChapterPage:
    chapter: Chapter
```

Như vậy interface rất rõ:

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

# 7. Cấu trúc thư mục

Ban đầu tôi đề xuất:

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   └── parser_result.py
    │
    ├── application/
    │   └── ...
    │
    ├── infrastructure/
    │   │
    │   └── parser/
    │       ├── base.py
    │       ├── selectolax_document.py
    │       │
    │       └── plugins/
    │           └── truyenfull/
    │               ├── parser.py
    │               ├── listing.py
    │               ├── novel.py
    │               └── chapter.py
    │
    └── ...
```

Nhưng có một nguyên tắc:

> **Domain không import Selectolax.**

Không được:

```python
# domain/novel.py

from selectolax.parser import HTMLParser
```

Domain không biết HTML tồn tại.

---

# 8. Boundary quan trọng nhất

Ta sẽ xây theo pipeline:

```text
                    Infrastructure

HTTPX
  │
  │ str
  ▼
page_source
  │
  ▼
SelectolaxDocument
  │
  │ DOM
  ▼
Site Parser
  │
  │ Domain Model
  ▼
Application
```

Trong đó:

```text
HTTPX → str
Selectolax → DOM
Parser → Domain
```

Mỗi tầng có **một trách nhiệm**.

---

# 9. SOLID áp dụng thế nào?

### S — Single Responsibility

Fetcher:

```text
HTTP
```

Selectolax adapter:

```text
HTML → DOM
```

Parser:

```text
DOM → Domain
```

Application:

```text
orchestration
```

---

### O — Open/Closed

Thêm website mới:

```text
TruyenFull
SiteA
SiteB
```

không sửa crawler core.

Chỉ thêm:

```text
plugins/site_a/
plugins/site_b/
```

---

### L — Liskov Substitution

Crawler có thể dùng:

```python
TruyenFullParser
```

hoặc:

```python
SiteAParser
```

thông qua interface chung.

---

### I — Interface Segregation

Không ép một parser phải implement những thứ nó không cần.

Sau này ta có thể tách:

```text
ListingParser
NovelParser
ChapterParser
```

thay vì một interface khổng lồ.

---

### D — Dependency Inversion

Application phụ thuộc:

```python
Parser interface
```

không phụ thuộc:

```python
TruyenFullParser
SelectolaxParser
```

---

# 10. Flow cuối cùng

Ví dụ crawl listing:

```text
Crawler
   │
   │ URL
   ▼
Fetcher
   │
   │ page_source
   ▼
Parser
   │
   ├── NovelSummary
   ├── NovelSummary
   └── next_url
            │
            ▼
       Application
            │
            │ fetch next_url
            ▼
          Parser
```

Novel:

```text
Novel URL
    │
    ▼
Fetcher
    │
    ▼
Novel Parser
    │
    ├── Novel
    ├── ChapterSummary[]
    └── next_url
             │
             ▼
       Application pagination
```

Chapter:

```text
Chapter URL
     │
     ▼
Fetcher
     │
 page_source
     │
     ▼
Chapter Parser
     │
     ▼
Chapter
```

---

## Bài tập Buổi 1

Trước khi sang **Buổi 2 — Selectolax Foundation**, hãy tạo 4 file:

```text
domain/
    novel.py
    chapter.py
    parser_result.py
```

và viết được các model:

```python
NovelSummary
Novel
ChapterSummary
Chapter
ListingPage
NovelPage
ChapterPage
```

**Chưa cần viết parser.**

Ở **Buổi 2**, chúng ta sẽ bắt đầu từ HTML thực tế:

```html
<div class="item">
    <h3>
        <a href="/truyen-a">Truyện A</a>
    </h3>

    <span class="author">Tác giả A</span>
</div>
```

rồi học cách dùng **Selectolax từng bước**, sau đó tự xây `SelectolaxDocument` trước khi viết `ListingParser`.
