# Buổi 34 — Chapter URL

Ở Buổi 33, chúng ta đã xử lý:

```text
Listing page
    ↓
<a href="...">
    ↓
yarl.URL
    ↓
next_url
```

Hôm nay áp dụng cùng nguyên tắc cho **chapter URL**.

Trong Novel Crawler, đây là một bước rất quan trọng:

```text
Novel Detail
    ↓
Chapter links
    ↓
Chapter URL
    ↓
Fetcher
    ↓
Chapter Parser
```

---

# 1. Bài toán thực tế

Một trang chi tiết truyện có thể có:

```html
<div class="chapter-list">
    <a href="/truyen/python/chuong-1">Chương 1</a>
    <a href="/truyen/python/chuong-2">Chương 2</a>
    <a href="/truyen/python/chuong-3">Chương 3</a>
</div>
```

Trang hiện tại:

```text
https://example.com/truyen/python
```

Crawler cần tạo:

```text
https://example.com/truyen/python/chuong-1
https://example.com/truyen/python/chuong-2
https://example.com/truyen/python/chuong-3
```

Không nên để chapter parser nhận:

```python
"/truyen/python/chuong-1"
```

mà nên nhận:

```python
URL("https://example.com/truyen/python/chuong-1")
```

---

# 2. Chapter URL có thể là relative

Ví dụ:

```html
<a href="chuong-1">Chương 1</a>
```

Với:

```text
https://example.com/truyen/python/
```

thì:

```python
page_url.join(URL("chuong-1"))
```

cho:

```text
https://example.com/truyen/python/chuong-1
```

Đây chính là kiến thức Buổi 31.

---

# 3. Chapter URL có thể là root-relative

```html
<a href="/truyen/python/chuong-1">
    Chương 1
</a>
```

Dùng:

```python
page_url.join(
    URL("/truyen/python/chuong-1")
)
```

→

```text
https://example.com/truyen/python/chuong-1
```

---

# 4. Chapter URL có thể là absolute

```html
<a href="https://example.com/truyen/python/chuong-1">
    Chương 1
</a>
```

Yarl vẫn xử lý được:

```python
page_url.join(URL(href))
```

→

```text
https://example.com/truyen/python/chuong-1
```

Vì vậy chúng ta không cần phân biệt thủ công:

```text
relative
root-relative
absolute
```

---

# 5. Selector phải đặc trưng cho chapter

Không nên:

```python
tree.css("a[href]")
```

rồi coi tất cả là chapter.

Một trang novel có thể có:

```html
<a href="/">Home</a>

<a href="/author/nguyen-van-a">Author</a>

<a href="/truyen/python/chuong-1">Chương 1</a>

<a href="/truyen/python/chuong-2">Chương 2</a>

<a href="/contact">Contact</a>
```

Nếu lấy tất cả:

```python
tree.css("a[href]")
```

thì crawler sẽ thu được cả:

```text
Home
Author
Chapter
Contact
```

Thay vào đó, parser phải sử dụng cấu trúc của website.

Ví dụ:

```html
<div class="chapter-list">
    ...
</div>
```

thì:

```python
tree.css(".chapter-list a[href]")
```

---

# 6. Ví dụ với selectolax

```python
from selectolax.parser import HTMLParser
from yarl import URL


html = """
<div class="chapter-list">

    <a href="/truyen/python/chuong-1">
        Chương 1
    </a>

    <a href="/truyen/python/chuong-2">
        Chương 2
    </a>

    <a href="/truyen/python/chuong-3">
        Chương 3
    </a>

</div>
"""

tree = HTMLParser(html)

for node in tree.css(".chapter-list a[href]"):
    href = node.attributes.get("href")

    print(href)
```

Kết quả:

```text
/truyen/python/chuong-1
/truyen/python/chuong-2
/truyen/python/chuong-3
```

---

# 7. Chuyển sang `yarl.URL`

```python
from selectolax.parser import HTMLParser
from yarl import URL


page_url = URL(
    "https://example.com/truyen/python"
)

html = """
<div class="chapter-list">

    <a href="/truyen/python/chuong-1">
        Chương 1
    </a>

    <a href="/truyen/python/chuong-2">
        Chương 2
    </a>

    <a href="/truyen/python/chuong-3">
        Chương 3
    </a>

</div>
"""

tree = HTMLParser(html)

for node in tree.css(".chapter-list a[href]"):

    href = node.attributes.get("href")

    if not href:
        continue

    url = page_url.join(
        URL(href.strip())
    )

    print(url)
```

Kết quả:

```text
https://example.com/truyen/python/chuong-1
https://example.com/truyen/python/chuong-2
https://example.com/truyen/python/chuong-3
```

---

# 8. Viết `parse_chapter_urls()`

Bây giờ đóng gói thành function:

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_chapter_urls(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    chapter_urls: list[URL] = []

    for node in tree.css(
        ".chapter-list a[href]"
    ):

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        url = page_url.join(
            URL(href)
        )

        chapter_urls.append(url)

    return chapter_urls
```

Sử dụng:

```python
page_url = URL(
    "https://example.com/truyen/python"
)

urls = parse_chapter_urls(
    page_url,
    html,
)

for url in urls:
    print(url)
```

---

# 9. Không nên tin mọi `href`

HTML thực tế có thể bị lỗi:

```html
<div class="chapter-list">

    <a href="/truyen/python/chuong-1">
        Chương 1
    </a>

    <a href="">
        Chương 2
    </a>

    <a>
        Chương 3
    </a>

    <a href="javascript:void(0)">
        Chương 4
    </a>

</div>
```

Do đó:

```python
href = node.attributes.get("href")

if not href:
    continue

href = href.strip()

if not href:
    continue
```

và kiểm tra scheme:

```python
href_url = URL(href)

if href_url.scheme not in ("", "http", "https"):
    continue
```

---

# 10. Phiên bản robust

```python
from selectolax.parser import HTMLParser
from yarl import URL


ALLOWED_SCHEMES = {
    "",
    "http",
    "https",
}


def parse_chapter_urls(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    chapter_urls: list[URL] = []

    for node in tree.css(
        ".chapter-list a[href]"
    ):

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme not in ALLOWED_SCHEMES:
            continue

        chapter_url = page_url.join(
            href_url
        )

        if chapter_url.scheme not in {
            "http",
            "https",
        }:
            continue

        chapter_urls.append(chapter_url)

    return chapter_urls
```

---

# 11. Chapter title cũng rất quan trọng

Thông thường ta không chỉ cần URL.

HTML:

```html
<a href="/truyen/python/chuong-1">
    Chương 1: Giới thiệu Python
</a>
```

Ta có:

```python
title = node.text(strip=True)
```

và:

```python
href = node.attributes.get("href")
```

Kết quả:

```text
title = "Chương 1: Giới thiệu Python"

url = URL(
    "https://example.com/truyen/python/chuong-1"
)
```

Lúc này dữ liệu có dạng:

```text
ChapterLink
├── title
└── url
```

---

# 12. Dùng dataclass

Với crawler của chúng ta, đây là lúc `dataclass` bắt đầu hữu ích.

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class ChapterLink:
    title: str
    url: URL
```

Parser:

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_chapter_links(
    page_url: URL,
    html: str,
) -> list[ChapterLink]:

    tree = HTMLParser(html)

    result: list[ChapterLink] = []

    for node in tree.css(
        ".chapter-list a[href]"
    ):

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        url = page_url.join(href_url)

        if url.scheme not in {
            "http",
            "https",
        }:
            continue

        title = node.text(strip=True)

        result.append(
            ChapterLink(
                title=title,
                url=url,
            )
        )

    return result
```

---

# 13. Test hoàn chỉnh

```python
from dataclasses import dataclass

from selectolax.parser import HTMLParser
from yarl import URL


@dataclass(frozen=True)
class ChapterLink:
    title: str
    url: URL


def parse_chapter_links(
    page_url: URL,
    html: str,
) -> list[ChapterLink]:

    tree = HTMLParser(html)

    result: list[ChapterLink] = []

    for node in tree.css(
        ".chapter-list a[href]"
    ):

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        url = page_url.join(href_url)

        if url.scheme not in {
            "http",
            "https",
        }:
            continue

        title = node.text(strip=True)

        result.append(
            ChapterLink(
                title=title,
                url=url,
            )
        )

    return result


def main():

    page_url = URL(
        "https://example.com/truyen/python/"
    )

    html = """
    <div class="chapter-list">

        <a href="chuong-1">
            Chương 1: Giới thiệu Python
        </a>

        <a href="chuong-2">
            Chương 2: Biến và kiểu dữ liệu
        </a>

        <a href="/truyen/python/chuong-3">
            Chương 3: Function
        </a>

        <a href="https://example.com/truyen/python/chuong-4">
            Chương 4: OOP
        </a>

        <a href="">
            Invalid
        </a>

        <a href="javascript:void(0)">
            JavaScript
        </a>

    </div>
    """

    chapters = parse_chapter_links(
        page_url,
        html,
    )

    for chapter in chapters:
        print("TITLE:", chapter.title)
        print("URL:  ", chapter.url)
        print()


if __name__ == "__main__":
    main()
```

Kết quả:

```text
TITLE: Chương 1: Giới thiệu Python
URL:   https://example.com/truyen/python/chuong-1

TITLE: Chương 2: Biến và kiểu dữ liệu
URL:   https://example.com/truyen/python/chuong-2

TITLE: Chương 3: Function
URL:   https://example.com/truyen/python/chuong-3

TITLE: Chương 4: OOP
URL:   https://example.com/truyen/python/chuong-4
```

---

# 14. `ChapterLink` có phải Domain Entity không?

Chưa chắc.

Hiện tại:

```python
@dataclass(frozen=True)
class ChapterLink:
    title: str
    url: URL
```

nó có thể chỉ là **parser DTO**.

Ta chưa cần biến nó thành:

```text
Chapter Entity
```

vì `Chapter` thực sự có thể chứa:

```text
Chapter
├── id
├── novel_id
├── number
├── title
├── url
├── content
├── created_at
└── ...
```

`ChapterLink` chỉ đại diện cho thông tin chúng ta nhìn thấy trên trang Novel Detail:

```text
title + url
```

Đây là distinction rất hữu ích trong DDD.

---

# 15. Chapter number

Một chapter thường có:

```text
Chương 1
Chương 2
Chương 10
```

hoặc:

```text
Chapter 001
Chapter 002
```

Có thể lấy number bằng regex:

```python
import re


def parse_chapter_number(
    title: str,
) -> int | None:

    match = re.search(
        r"\b(?:chương|chapter)\s*(\d+)",
        title,
        re.IGNORECASE,
    )

    if match is None:
        return None

    return int(match.group(1))
```

Ví dụ:

```python
print(
    parse_chapter_number(
        "Chương 123: Python nâng cao"
    )
)
```

→

```text
123
```

Nhưng **không nên đưa logic này vào `yarl` URL processing**.

Đó là:

```text
Chapter parsing
```

không phải:

```text
URL parsing
```

---

# 16. URL và Chapter Number là hai concern khác nhau

Không nên làm:

```python
chapter_url = ...
chapter_number = ...
chapter_title = ...
chapter_content = ...
```

tất cả trong một function.

Pipeline tốt hơn:

```text
Novel Detail HTML
        │
        ▼
Chapter Link Parser
        │
        ├── title
        └── URL
                │
                ▼
          Chapter URL
                │
                ▼
             Fetcher
                │
                ▼
        Chapter page HTML
                │
                ▼
        Chapter Parser
                │
                ├── number
                ├── title
                └── content
```

Đây chính là architecture mà chúng ta đã thiết kế ở parser track trước đây.

---

# 17. Một vấn đề thực tế: nhiều chapter list

Website có thể chia chapter:

```html
<div class="chapter-list">
    ...
</div>

<div class="chapter-list">
    ...
</div>
```

Selector:

```python
tree.css(".chapter-list a[href]")
```

sẽ lấy tất cả.

Đó là lý do chúng ta không nên dùng:

```python
css_first()
```

ở đây.

`css_first()` phù hợp khi:

```text
next page
cover
title
author
```

thường chỉ có một node.

Còn chapter list:

```text
1
2
3
...
1000
```

phải dùng:

```python
tree.css(...)
```

---

# 18. Không deduplicate ở đây

Có thể website vô tình có:

```html
<a href="/chapter-1">Chương 1</a>
<a href="/chapter-1">Chương 1</a>
```

Parser sẽ trả:

```text
chapter-1
chapter-1
```

Có thể bạn muốn:

```python
set(chapter_urls)
```

nhưng **chưa làm ở đây**.

Pipeline nên là:

```text
Parser
 ↓
raw chapter URLs
 ↓
Normalization
 ↓
Canonicalization
 ↓
Deduplication
 ↓
Queue
```

Chúng ta sẽ học riêng:

```text
36 URL normalization
37 URL comparison
38 URL deduplication
39 Canonical URL
```

---

# 19. Một lỗi kiến trúc cần tránh

Không nên viết:

```python
def parse_chapter_links(page_url, html):
    ...
    database.save(...)
    ...
    queue.add(...)
    ...
    httpx.get(...)
```

Parser chỉ nên:

```text
HTML
 ↓
data
```

Cụ thể:

```python
list[ChapterLink]
```

Application layer mới quyết định:

```text
ChapterLink
 ↓
Repository
Queue
Fetcher
```

---

# 20. Đưa vào `NovelSummary`

Ở parser track của chúng ta, Novel Detail có thể trả:

```text
NovelSummary
├── title
├── author
├── url
├── cover
├── description
├── status
└── chapters
```

Ví dụ:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class ChapterLink:
    title: str
    url: URL


@dataclass(frozen=True)
class NovelSummary:
    title: str
    author: str
    url: URL
    cover: URL | None
    description: str
    status: str
    chapters: list[ChapterLink]
    next_chapter_page: URL | None
```

Luồng:

```text
Novel Detail
      │
      ├── metadata
      │
      ├── chapters
      │
      └── chapter pagination
```

---

# 21. Chapter pagination

Một novel có thể có 5000 chapter nhưng trang chỉ hiển thị:

```text
1 ... 100
```

hoặc:

```text
Chương 1 → Chương 100
```

và có:

```html
<a class="next" href="/truyen/python?page=2">
    Next
</a>
```

Khi đó:

```text
Novel Detail
   │
   ├── Chapter 1
   ├── Chapter 2
   ├── ...
   ├── Chapter 100
   │
   └── next_chapter_page
              ↓
        Novel Detail page 2
```

Về mặt URL, **hoàn toàn giống Pagination ở Buổi 33**.

Khác nhau chỉ ở:

```text
Listing pagination
    → trang listing tiếp theo

Chapter pagination
    → trang chapter list tiếp theo
```

---

# 22. `ChapterLink` và `URL` trong architecture

Ta có:

```text
selectolax
    ↓
href
    ↓
yarl.URL
    ↓
ChapterLink
```

Không nên:

```text
selectolax
    ↓
string URL
    ↓
ChapterLink
```

Tốt hơn:

```python
@dataclass(frozen=True)
class ChapterLink:
    title: str
    url: URL
```

Nhờ vậy mọi tầng phía sau đều có một URL object thống nhất.

---

# 23. Toàn bộ flow của Novel Crawler

Sau Buổi 34:

```text
                    HTTPX
                      │
                      ▼
               Novel Detail HTML
                      │
                      ▼
                  Selectolax
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
      Metadata               Chapter links
                                  │
                                  ▼
                               href
                                  │
                                  ▼
                              yarl.URL
                                  │
                                  ▼
                           ChapterLink
                                  │
                                  ▼
                                Queue
                                  │
                                  ▼
                               HTTPX
                                  │
                                  ▼
                           Chapter HTML
                                  │
                                  ▼
                          Chapter Parser
```

Đây là một pipeline rất sạch:

```text
HTTP
→ Parse
→ URL
→ Queue
→ HTTP
```

---

# 24. Checklist Buổi 34

Bạn cần nắm chắc các điểm sau:

```text
✓ chapter URL là URL bình thường
✓ href có thể relative
✓ href có thể root-relative
✓ href có thể absolute
✓ dùng page_url.join(URL(href))
✓ selector phải đặc trưng cho chapter
✓ không lấy toàn bộ a[href] một cách mù quáng
✓ trả list[URL] hoặc list[ChapterLink]
✓ không fetch trong parser
✓ không lưu database trong parser
✓ không deduplicate trong parser
✓ không tự nối URL bằng string
```

Pipeline:

```text
<a href>
    ↓
selectolax
    ↓
href
    ↓
URL(href)
    ↓
page_url.join(...)
    ↓
Chapter URL
    ↓
ChapterLink
    ↓
Queue
```

Và vị trí của Buổi 34 trong roadmap:

```text
31 Relative URL → Absolute URL
32 <a href> → URL
33 Pagination
👉 34 Chapter URL
35 Image URL
36 URL Normalization
37 URL Comparison
38 URL Deduplication
39 Canonical URL
40 URLBuilder cho Novel Crawler
```

**Điểm cốt lõi của Buổi 34:** `selectolax` chịu trách nhiệm **tìm chapter link trong HTML**, còn `yarl` chịu trách nhiệm **biến `href` thành URL chuẩn**. Hai trách nhiệm này nên được giữ tách biệt.
