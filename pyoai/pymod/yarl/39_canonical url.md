# Buổi 39 — Canonical URL

Đến đây chúng ta đã có:

```text id="w2qv0t"
URL
 ↓
Resolve
 ↓
Normalize
 ↓
Compare
 ↓
Deduplicate
```

Nhưng crawler còn gặp một vấn đề khác:

> Website có thể nói cho chúng ta biết **URL nào là URL chuẩn (canonical URL)** của một resource.

Ví dụ HTML:

```html
<link
    rel="canonical"
    href="https://example.com/novel/python-chapter-1"
/>
```

Đây là **Canonical URL**.

---

# 1. Canonical URL là gì?

Giả sử cùng một nội dung có thể truy cập bằng:

```text id="y8r1cv"
https://example.com/chapter-1
https://example.com/chapter-1/
https://example.com/chapter-1?ref=home
https://example.com/chapter-1?utm_source=facebook
```

Website có thể khai báo:

```html id="5qv8ik"
<link
    rel="canonical"
    href="https://example.com/chapter-1"
/>
```

Ý nghĩa ở đây là:

```text id="9k9x2f"
canonical URL
        ↓
https://example.com/chapter-1
```

---

# 2. Canonical khác normalization

Đây là điểm quan trọng nhất của bài.

### Normalization

Crawler tự áp dụng rule:

```text id="hj7f2r"
https://example.com/chapter-1#top
                ↓
https://example.com/chapter-1
```

### Canonicalization

Website khai báo:

```text id="5zn4k9"
<link rel="canonical"
      href="https://example.com/chapter-1">
```

Nói cách khác:

```text id="xw0v5u"
Normalization
    ↓
Rule của crawler


Canonical
    ↓
Signal / declaration từ website
```

Không nên trộn hai khái niệm này.

---

# 3. Canonical URL nằm ở đâu?

Thông thường trong `<head>`:

```html id="w4z9ve"
<head>
    <title>Chapter 1</title>

    <link
        rel="canonical"
        href="https://example.com/chapter-1"
    >
</head>
```

Với `selectolax`:

```python id="36r9x2"
from selectolax.parser import HTMLParser


tree = HTMLParser(html)

node = tree.css_first(
    'link[rel="canonical"]'
)

if node:
    print(node.attributes.get("href"))
```

---

# 4. Hàm extract canonical URL

Bắt đầu thật đơn giản:

```python id="2ap5jy"
from selectolax.parser import HTMLParser
from yarl import URL


def extract_canonical_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = tree.css_first(
        'link[rel="canonical"]'
    )

    if node is None:
        return None

    href = node.attributes.get("href")

    if not href:
        return None

    href = href.strip()

    if not href:
        return None

    return page_url.join(URL(href))
```

---

# 5. Test với canonical tuyệt đối

HTML:

```python id="u5m7io"
html = """
<html>
<head>
    <link
        rel="canonical"
        href="https://example.com/chapter-1"
    >
</head>
<body>
    Chapter 1
</body>
</html>
"""
```

Code:

```python id="y6j0v6"
page_url = URL(
    "https://example.com/chapter-1?ref=home"
)

canonical = extract_canonical_url(
    page_url,
    html,
)

print(canonical)
```

Kết quả:

```text id="1c6l4q"
https://example.com/chapter-1
```

---

# 6. Canonical có thể là relative URL

Website không bắt buộc phải viết:

```html id="9exzmb"
<link
    rel="canonical"
    href="https://example.com/chapter-1"
>
```

Có thể:

```html id="1f7n9j"
<link
    rel="canonical"
    href="/chapter-1"
>
```

Vì vậy chúng ta không nên:

```python id="04j0t7"
URL(href)
```

rồi coi nó là absolute URL.

Phải dùng:

```python id="6o0z7r"
page_url.join(URL(href))
```

Ví dụ:

```python id="xqv4x7"
page_url = URL(
    "https://example.com/chapter-1?ref=home"
)

href = "/chapter-1"

canonical = page_url.join(URL(href))

print(canonical)
```

Kết quả:

```text id="tqg3lo"
https://example.com/chapter-1
```

---

# 7. Canonical có thể là relative path

Ví dụ:

```html id="9gnm3v"
<link
    rel="canonical"
    href="chapter-1"
>
```

Nếu:

```text id="x99kpb"
page_url =
https://example.com/novel/page-2
```

thì resolver của yarl xử lý:

```python id="8x9twi"
page_url.join(URL("chapter-1"))
```

theo URL resolution rules.

Điểm quan trọng:

> Canonical URL cũng là một URL reference và cần được resolve giống `<a href>`.

---

# 8. Canonical không nhất thiết là URL hiện tại

Ví dụ:

```text id="6jhm08"
Current page:

https://example.com/chapter-1?utm_source=facebook
```

Canonical:

```text id="l7y3v9"
https://example.com/chapter-1
```

Ta có:

```python id="10yq1m"
page_url != canonical_url
```

Nhưng:

```text id="5ljy8r"
current page
      │
      └── canonical → canonical page
```

---

# 9. Canonical và normalization kết hợp thế nào?

Đây là chỗ rất quan trọng trong crawler.

Giả sử:

```text id="nq9qso"
Current:
https://example.com/chapter-1?utm_source=facebook#top
```

Canonical:

```text id="ik2z6e"
https://example.com/chapter-1
```

Ta có:

```text id="h8wjcn"
Current URL
    ↓
Normalize
    ↓
https://example.com/chapter-1?utm_source=facebook
```

Canonical:

```text id="zv2e9c"
https://example.com/chapter-1
```

Hai URL vẫn có thể khác nhau.

Canonical là **một layer khác**.

---

# 10. Đừng tự động thay URL bằng canonical

Đây là lỗi kiến trúc dễ mắc:

```python id="d0u6s8"
url = extract_canonical_url(...)

if url:
    page_url = url
```

Không nên làm như vậy một cách mù quáng.

Canonical là một **signal từ website**, không phải lệnh:

> "Crawler bắt buộc phải thay URL hiện tại bằng URL này."

Crawler cần quyết định theo policy.

---

# 11. Canonical URL có thể được dùng để dedup

Đây là trường hợp hữu ích.

Giả sử:

```text id="h9l6qa"
Page A:
https://example.com/chapter-1?ref=home

Page B:
https://example.com/chapter-1?ref=facebook
```

Cả hai trang đều khai báo:

```html id="i2o6ro"
<link
    rel="canonical"
    href="https://example.com/chapter-1"
>
```

Crawler có thể nhận ra:

```text id="9uvl8d"
A
 └── canonical → chapter-1

B
 └── canonical → chapter-1
```

Từ đó có thể tránh xử lý resource logic hai lần.

Nhưng đây là **policy của crawler**, không phải trách nhiệm của parser.

---

# 12. Canonical parser chỉ nên extract

Đây là kiến trúc rất quan trọng.

Parser:

```text id="1xw8bn"
HTML
 ↓
extract canonical
 ↓
URL | None
```

Không nên để parser:

```text id="90hj0r"
HTML
 ↓
canonical
 ↓
database
 ↓
queue
 ↓
dedup
```

Parser chỉ làm:

```python id="n4j90j"
canonical_url = extract_canonical_url(...)
```

Application layer quyết định phải làm gì.

---

# 13. Validation canonical URL

Website có thể có:

```html id="lx7lqd"
<link
    rel="canonical"
    href="javascript:void(0)"
>
```

hoặc:

```html id="0x7c7x"
<link
    rel="canonical"
    href="mailto:test@example.com"
>
```

Không nên chấp nhận chúng.

Ta có thể kiểm tra:

```python id="5m7gn9"
canonical = page_url.join(URL(href))

if canonical.scheme not in {"http", "https"}:
    return None
```

---

# 14. Hàm hoàn chỉnh hơn

```python id="3x8e2n"
from selectolax.parser import HTMLParser
from yarl import URL


ALLOWED_SCHEMES = {"http", "https"}


def extract_canonical_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = tree.css_first(
        'link[rel="canonical"]'
    )

    if node is None:
        return None

    href = node.attributes.get("href")

    if not href:
        return None

    href = href.strip()

    if not href:
        return None

    raw_url = URL(href)

    if (
        raw_url.scheme
        and raw_url.scheme not in ALLOWED_SCHEMES
    ):
        return None

    canonical = page_url.join(raw_url)

    if canonical.scheme not in ALLOWED_SCHEMES:
        return None

    return canonical
```

---

# 15. Test nhiều trường hợp

```python id="j95d6b"
from yarl import URL


page_url = URL(
    "https://example.com/novel/chapter-1"
)
```

### Case 1 — absolute

```html id="p08g2h"
<link
    rel="canonical"
    href="https://example.com/novel/chapter-1"
>
```

→

```text id="8afg1s"
https://example.com/novel/chapter-1
```

---

### Case 2 — root-relative

```html id="j2b1yr"
<link
    rel="canonical"
    href="/novel/chapter-1"
>
```

→

```text id="5qkg0d"
https://example.com/novel/chapter-1
```

---

### Case 3 — không có canonical

```html id="jvqu7p"
<head>
    <title>Chapter 1</title>
</head>
```

→

```python id="m7z2bb"
None
```

---

### Case 4 — unsupported scheme

```html id="i2l1k4"
<link
    rel="canonical"
    href="javascript:void(0)"
>
```

→

```python id="7b4q0j"
None
```

---

# 16. Nhiều canonical

HTML lỗi có thể có:

```html id="m9v9h4"
<link
    rel="canonical"
    href="/chapter-1"
>

<link
    rel="canonical"
    href="/chapter-2"
>
```

Code:

```python id="0k4rxw"
tree.css('link[rel="canonical"]')
```

có thể trả nhiều node.

Vậy parser phải có policy.

Một policy đơn giản:

> Lấy canonical đầu tiên.

```python id="tw8z86"
nodes = tree.css(
    'link[rel="canonical"]'
)

if not nodes:
    return None

node = nodes[0]
```

Nhưng có thể log warning:

```python id="rlz0q3"
if len(nodes) > 1:
    logger.warning(
        "Multiple canonical URLs found"
    )
```

Đây là cách production crawler nên xử lý: **không âm thầm giả định HTML luôn đúng**.

---

# 17. `rel="canonical"` không nhất thiết phải viết đúng một kiểu?

HTML có thể có:

```html id="bq2kv1"
<link rel="canonical" href="...">
```

Thông thường selector:

```css
link[rel="canonical"]
```

là đủ cho các trang chuẩn.

Nếu muốn robust hơn, có thể kiểm tra:

```python id="u5gg5c"
rel = node.attributes.get("rel", "")
```

và xử lý tokenization nếu cần.

Nhưng với plugin parser của Novel Crawler, tôi khuyên:

> Bắt đầu bằng selector đơn giản; chỉ mở rộng khi website thực tế yêu cầu.

---

# 18. Canonical URL và site boundary

Giả sử trang:

```text id="4sgwob"
https://site-a.com/chapter-1
```

lại khai báo:

```html id="1dfy4h"
<link
    rel="canonical"
    href="https://site-b.com/chapter-1"
>
```

Có nên crawler sang `site-b.com`?

**Không nên tự động.**

Canonical extraction chỉ cho biết:

```text id="6w3eqs"
canonical = site-b.com
```

Còn:

```text id="z52t3m"
Có crawl site-b không?
```

là **URL Policy**.

Ví dụ:

```python id="2g4xv6"
if not policy.is_allowed(canonical_url):
    ...
```

---

# 19. Đây là lý do cần tách Canonical Extractor và URL Policy

Architecture:

```text id="g4p2a6"
HTML
 │
 ▼
Canonical Extractor
 │
 ▼
canonical URL
 │
 ▼
URL Normalizer
 │
 ▼
URL Policy
 │
 ├── allowed
 │
 └── rejected
```

Không nên:

```text id="9nh8j2"
Canonical Extractor
     ↓
     "Nếu canonical khác host thì reject"
```

vì đó là hai responsibility khác nhau.

---

# 20. Canonical và current URL

Có thể tạo một object nhỏ:

```python id="jv19w8"
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class PageURLInfo:
    current: URL
    canonical: URL | None
```

Ví dụ:

```python id="h4if8d"
info = PageURLInfo(
    current=page_url,
    canonical=canonical_url,
)
```

Nhưng hiện tại **chưa cần** nếu project chưa sử dụng thông tin này ở nhiều nơi.

Function:

```python id="zqj7hg"
extract_canonical_url()
```

là đủ.

---

# 21. Canonical trong Novel Crawler

Giả sử crawler fetch:

```text id="bkvn49"
https://site.com/truyen/python?page=2
```

HTML:

```html id="2b12k9"
<link
    rel="canonical"
    href="https://site.com/truyen/python"
>
```

Crawler có:

```text id="pl1w1p"
requested_url
    ↓
https://site.com/truyen/python?page=2

canonical_url
    ↓
https://site.com/truyen/python
```

Thông tin này có thể hữu ích để:

* nhận diện resource logic
* tránh lưu duplicate
* ghi metadata
* debug redirect/canonical behavior
* xây URL identity
* phân tích site structure

---

# 22. Canonical không thay thế HTTP redirect

Đây là distinction rất quan trọng.

Server có thể trả:

```text id="c6v4mw"
301
Location: /chapter-1
```

Đó là:

```text id="34ikg7"
HTTP redirect
```

Còn:

```html id="u1e1s5"
<link rel="canonical" href="/chapter-1">
```

là:

```text id="n1tq3k"
HTML canonical declaration
```

Hai thứ khác nhau.

Pipeline:

```text id="8g2u4h"
HTTP
 │
 ├── Redirect
 │
 ▼
Final response URL
 │
 ▼
HTML
 │
 └── Canonical
```

Không được trộn chúng.

---

# 23. Một pipeline thực tế

Ví dụ Fetcher trả:

```python id="t2by5x"
response_url = URL(
    "https://example.com/chapter-1"
)
```

Parser đọc HTML:

```python id="d2d8tc"
canonical_url = extract_canonical_url(
    response_url,
    html,
)
```

Sau đó:

```python id="c3z7jj"
if canonical_url is not None:
    canonical_url = normalize_url(
        canonical_url
    )
```

Rồi application layer quyết định:

```text id="9xj6z7"
canonical
    ↓
URL Policy
    ↓
Identity / metadata / dedup
```

---

# 24. Canonical identity

Một thiết kế nâng cao có thể dùng:

```text id="q49m83"
identity_url =
    canonical_url
    if canonical_url exists
    else normalized_current_url
```

Ví dụ:

```python id="d4svwp"
identity_url = (
    canonical_url
    if canonical_url is not None
    else normalize_url(current_url)
)
```

Nhưng **đây là policy**, không phải quy tắc URL universal.

Một số website khai báo canonical sai, stale hoặc không phù hợp với crawler.

Vì vậy không nên:

```python id="n6fzkn"
canonical_url == identity
```

một cách tuyệt đối.

---

# 25. Một `CanonicalResolver` đơn giản

Nếu project bắt đầu cần logic fallback:

```python id="4fy9o6"
from yarl import URL


def resolve_canonical(
    current_url: URL,
    canonical_url: URL | None,
) -> URL:

    if canonical_url is None:
        return current_url

    return canonical_url
```

Sau đó:

```python id="v0n2jm"
identity_url = normalize_url(
    resolve_canonical(
        current_url,
        canonical_url,
    )
)
```

Pipeline:

```text id="4vhy58"
Current URL
    │
    ▼
Canonical?
    │
 ┌──┴───┐
No     Yes
 │       │
 ▼       ▼
Current Canonical
    │
    ▼
Normalizer
    │
    ▼
Identity URL
```

Đây là một pattern rất hữu ích cho crawler.

---

# 26. Nhưng canonical có thể sai

Đây là lý do không nên coi canonical như sự thật tuyệt đối.

Ví dụ trang:

```text id="6wqj42"
https://site.com/chapter-10
```

lại khai báo:

```html id="5l5v3f"
<link
    rel="canonical"
    href="https://site.com/chapter-1"
>
```

Nếu crawler mù quáng:

```text id="35k7e9"
chapter-10
    ↓
chapter-1
```

thì identity bị sai.

Do đó production crawler có thể áp dụng:

```text id="h65q5m"
canonical
    ↓
validate
    ↓
policy
    ↓
accept / reject
```

---

# 27. Validation canonical nâng cao

Có thể kiểm tra:

```text id="z14bdw"
1. Scheme hợp lệ?
2. Host hợp lệ?
3. URL có malformed không?
4. Có fragment không?
5. Có nằm trong allowed domain không?
6. Có phù hợp plugin/site policy không?
```

Ví dụ:

```python id="s1kgf8"
def is_valid_canonical(
    url: URL,
) -> bool:

    if url.scheme not in {"http", "https"}:
        return False

    if not url.host:
        return False

    return True
```

Sau đó site policy có thể kiểm tra thêm.

---

# 28. Canonical URL trong plugin architecture

Với kiến trúc plugin của bạn:

```text id="4ygj5o"
plugins/
    truyenfullsource/
        parser/
            novel.py
            chapter.py
            image.py
            canonical.py
```

Có thể có:

```python id="bdj3ec"
class CanonicalParser:
    def parse(
        self,
        page_url: URL,
        html: str,
    ) -> URL | None:
        ...
```

Nhưng tôi chỉ khuyên tạo class nếu plugin thực sự cần.

Ban đầu:

```python id="c7nq20"
extract_canonical_url()
```

là đủ.

---

# 29. Test hoàn chỉnh

```python id="k2r4k8"
from selectolax.parser import HTMLParser
from yarl import URL


def extract_canonical_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = tree.css_first(
        'link[rel="canonical"]'
    )

    if node is None:
        return None

    href = node.attributes.get("href")

    if not href:
        return None

    href = href.strip()

    if not href:
        return None

    raw_url = URL(href)

    if (
        raw_url.scheme
        and raw_url.scheme not in {"http", "https"}
    ):
        return None

    canonical = page_url.join(raw_url)

    if canonical.scheme not in {"http", "https"}:
        return None

    return canonical
```

Test:

```python id="s0y9h8"
def test_absolute_canonical():

    page_url = URL(
        "https://example.com/page"
    )

    html = """
    <link
        rel="canonical"
        href="https://example.com/chapter-1"
    >
    """

    result = extract_canonical_url(
        page_url,
        html,
    )

    assert result == URL(
        "https://example.com/chapter-1"
    )
```

Relative:

```python id="dfv0cj"
def test_relative_canonical():

    page_url = URL(
        "https://example.com/novel/page-2"
    )

    html = """
    <link
        rel="canonical"
        href="/novel/page-1"
    >
    """

    result = extract_canonical_url(
        page_url,
        html,
    )

    assert result == URL(
        "https://example.com/novel/page-1"
    )
```

Không có canonical:

```python id="nycbxj"
def test_missing_canonical():

    page_url = URL(
        "https://example.com/page"
    )

    html = """
    <html>
        <head>
            <title>Hello</title>
        </head>
    </html>
    """

    result = extract_canonical_url(
        page_url,
        html,
    )

    assert result is None
```

---

# 30. Ba khái niệm cần thuộc lòng

Sau Buổi 39, hãy phân biệt thật rõ:

### 1. Normalization

```text id="xv2c6b"
Crawler tự chuẩn hóa representation
```

Ví dụ:

```text id="p8q6gv"
chapter-1#top
       ↓
chapter-1
```

---

### 2. Deduplication

```text id="ihkqki"
Crawler loại URL trùng
```

Ví dụ:

```text id="8l6j0m"
A
A
B
B
C

↓

A
B
C
```

---

### 3. Canonicalization

```text id="d8nqcb"
Website khai báo URL chuẩn
```

Ví dụ:

```html id="kq2v1m"
<link
    rel="canonical"
    href="https://example.com/chapter-1"
>
```

---

# 31. Toàn bộ kiến trúc URL hiện tại

Sau 39 bài:

```text id="p0m9bb"
                         HTML
                           │
                           ▼
                      selectolax
                           │
                ┌──────────┼──────────┐
                │          │          │
              href        src     canonical
                │          │          │
                ▼          ▼          ▼
             yarl.URL   yarl.URL   yarl.URL
                │          │          │
                └──────────┼──────────┘
                           │
                           ▼
                     URL Resolver
                           │
                           ▼
                    URL Normalizer
                           │
                           ▼
                    URL Comparator
                           │
                           ▼
                   URL Deduplicator
                           │
                           ▼
                         Queue
                           │
                           ▼
                        Fetcher
```

Với canonical:

```text id="3nqu4h"
Fetched Page
      │
      ▼
Canonical URL
      │
      ▼
Canonical Validation
      │
      ▼
URL Policy
      │
      ▼
Resource Identity
```

---

# 32. Bài tập thực hành

Hãy xây một hàm:

```python id="4p9q9w"
def get_resource_identity(
    page_url: URL,
    html: str,
) -> URL:
    ...
```

Policy:

1. Tìm:

```html
<link rel="canonical" href="...">
```

2. Nếu có canonical hợp lệ → dùng canonical.
3. Nếu không có → dùng `page_url`.
4. Cuối cùng normalize:

```python
url.with_fragment(None)
```

Ví dụ:

```text id="0f3s0n"
page_url:
https://example.com/chapter-1?ref=facebook#top

canonical:
https://example.com/chapter-1

identity:
https://example.com/chapter-1
```

Nếu không có canonical:

```text id="s6a7bl"
page_url:
https://example.com/chapter-1?ref=facebook#top

identity:
https://example.com/chapter-1?ref=facebook
```

Đây là một bài tập rất tốt để chuẩn bị cho bài cuối của phần này.

---

## Tổng kết

Sau Buổi 39, flow URL của Novel Crawler đã gần hoàn chỉnh:

```text id="krw3es"
                  HTML
                    │
                    ▼
                Extract URL
                    │
                    ▼
              Resolve relative
                    │
                    ▼
                Normalize
                    │
          ┌─────────┴─────────┐
          │                   │
       Current             Canonical
          │                   │
          └─────────┬─────────┘
                    ▼
              Resource Identity
                    │
                    ▼
               Deduplicate
                    │
                    ▼
                  Queue
                    │
                    ▼
                 Fetcher
```

**Buổi 40 — `URLBuilder` cho Novel Crawler** sẽ gom những gì chúng ta đã học thành một component thực tế: xây URL listing, novel, chapter, pagination, search và image theo hướng **DDD + SOLID nhưng không over-engineering**.
