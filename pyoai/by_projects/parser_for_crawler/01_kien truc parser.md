
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
