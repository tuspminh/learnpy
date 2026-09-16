# Phần IV — URL trong Web Crawler

## Buổi 31 — Relative URL → Absolute URL

Từ bài này, chúng ta chuyển từ việc **học API của `yarl`** sang sử dụng `yarl` trong một crawler thực tế.

Đây là bài nền tảng vì HTML thường không chứa URL đầy đủ.

Ví dụ server trả về:

```html
<a href="/truyen/python-co-ban">
    Python cơ bản
</a>
```

Crawler phải biến:

```text
/truyen/python-co-ban
```

thành:

```text
https://example.com/truyen/python-co-ban
```

Đây chính là:

```text
Relative URL
      ↓
   resolve
      ↓
Absolute URL
```

---

# 1. Relative URL là gì?

URL tuyệt đối:

```text
https://example.com/truyen/python
```

có đầy đủ:

```text
scheme = https
host   = example.com
path   = /truyen/python
```

URL tương đối:

```text
/truyen/python
```

không có:

```text
scheme
host
```

Nó chỉ có ý nghĩa khi đặt trong một URL cơ sở.

Ví dụ:

```text
Base:
https://example.com

Relative:
/truyen/python
```

→

```text
https://example.com/truyen/python
```

---

# 2. Tại sao crawler gặp relative URL liên tục?

HTML website thường viết:

```html
<a href="/truyen/python">
```

thay vì:

```html
<a href="https://example.com/truyen/python">
```

Tương tự:

```html
<a href="/truyen/python?page=2">
<a href="../chapter/10">
<img src="/images/cover.jpg">
<script src="/static/app.js">
<link href="/css/style.css">
```

Parser của crawler sẽ liên tục gặp các dạng này.

Vì vậy cần một URL resolver.

---

# 3. `yarl.URL.join()`

API quan trọng hôm nay:

```python
base_url.join(relative_url)
```

Ví dụ:

```python
from yarl import URL

base_url = URL("https://example.com")
relative_url = URL("/truyen/python")

absolute_url = base_url.join(relative_url)

print(absolute_url)
```

Kết quả:

```text
https://example.com/truyen/python
```

---

# 4. Ví dụ hoàn chỉnh đầu tiên

```python
from yarl import URL


def main() -> None:
    base_url = URL("https://example.com")

    relative_url = URL("/truyen/python")

    absolute_url = base_url.join(relative_url)

    print("Base URL:")
    print(base_url)

    print("\nRelative URL:")
    print(relative_url)

    print("\nAbsolute URL:")
    print(absolute_url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Base URL:
https://example.com

Relative URL:
/truyen/python

Absolute URL:
https://example.com/truyen/python
```

---

# 5. Relative URL phải được hiểu theo base URL

Ví dụ:

```python
base_url = URL("https://example.com/novels/list")
```

và:

```python
relative_url = URL("/novels/python")
```

thì:

```python
base_url.join(relative_url)
```

→

```text
https://example.com/novels/python
```

Nhưng nếu:

```python
relative_url = URL("python")
```

thì nó là relative path.

Kết quả phụ thuộc vào vị trí của `base_url`.

Ví dụ:

```python
base_url = URL("https://example.com/novels/list/")
relative_url = URL("python")

print(base_url.join(relative_url))
```

→

```text
https://example.com/novels/list/python
```

Điểm quan trọng:

> Relative URL không thể được hiểu chính xác nếu không biết base URL.

---

# 6. Base URL nào mới đúng?

Đây là một lỗi crawler rất phổ biến.

Giả sử trang:

```text
https://example.com/novels/page-2
```

HTML:

```html
<a href="chapter-10">
```

Relative URL:

```text
chapter-10
```

Không thể tự quyết định rằng nó là:

```text
https://example.com/chapter-10
```

Base URL đúng là:

```text
https://example.com/novels/page-2
```

và browser sẽ resolve relative URL dựa trên URL của document.

Vì vậy parser nên biết:

```text
page_source
+
page_url
```

chứ không chỉ:

```text
page_source
```

---

# 7. Đây là lý do Parser của Novel Crawler cần `page_url`

Trước đây ta thiết kế parser:

```text
HTML
 ↓
Parser
 ↓
Novel / Chapter
```

Nhưng khi HTML có:

```html
<a href="/novel/python">
```

Parser cần biết trang HTML hiện tại nằm ở đâu.

Do đó tốt hơn:

```text
page_url
     +
page_source
     ↓
   Parser
     ↓
 absolute URLs
```

Ví dụ:

```python
from yarl import URL


def resolve_url(page_url: URL, href: str) -> URL:
    return page_url.join(URL(href))
```

---

# 8. Xây `resolve_url()`

Đây là abstraction đầu tiên của phần crawler.

```python
from yarl import URL


def resolve_url(page_url: URL, href: str) -> URL:
    return page_url.join(URL(href))


page_url = URL(
    "https://example.com/novels/list"
)

href = "/novels/python"

url = resolve_url(page_url, href)

print(url)
```

Kết quả:

```text
https://example.com/novels/python
```

---

# 9. Absolute URL cũng có thể đưa vào `join()`

Ví dụ:

```python
from yarl import URL

base_url = URL("https://example.com/novels")

href = URL("https://cdn.example.com/book/1")

result = base_url.join(href)

print(result)
```

Khi URL được join là absolute, nó có thể trở thành URL đích độc lập:

```text
https://cdn.example.com/book/1
```

Điều này rất hữu ích vì parser không cần phải phân biệt quá sớm:

```text
href = relative?
href = absolute?
```

Ta có thể đưa nó qua một resolver.

---

# 10. Các dạng `href` crawler thường gặp

Trong HTML, bạn có thể gặp:

### Root-relative

```html
<a href="/novel/python">
```

→

```text
https://example.com/novel/python
```

### Path-relative

```html
<a href="chapter-10">
```

→ phụ thuộc base URL.

### Parent-relative

```html
<a href="../chapter-10">
```

→ đi lên một cấp.

### Absolute

```html
<a href="https://example.com/chapter/10">
```

→ đã đầy đủ.

### Query-only

```html
<a href="?page=2">
```

→ giữ document path, thay/đặt query theo quy tắc URL resolution.

### Fragment

```html
<a href="#chapter-10">
```

→ thay đổi fragment.

### Protocol-relative

```html
<a href="//cdn.example.com/image.jpg">
```

→ dùng scheme của base URL.

Đây là lý do **không nên tự nối chuỗi**.

---

# 11. Đừng làm thế này

❌:

```python
absolute_url = base_url + href
```

Vì:

```python
base_url = "https://example.com/novels"
href = "../chapter/10"
```

sẽ không được resolve đúng.

Hoặc:

```python
base_url = "https://example.com"
href = "?page=2"
```

cũng không thể xử lý đúng bằng phép nối string đơn giản.

---

# 12. Đừng dùng `rstrip("/") + "/" + href`

Một cách rất phổ biến:

```python
absolute_url = base_url.rstrip("/") + "/" + href.lstrip("/")
```

Cách này chỉ xử lý được một phần rất nhỏ.

Nó không hiểu đầy đủ:

```text
..
.
?
#
//
scheme
path hierarchy
```

URL resolution là một bài toán riêng.

Hãy để:

```python
yarl
```

xử lý.

---

# 13. Relative URL với `..`

Ví dụ:

```python
from yarl import URL

base_url = URL(
    "https://example.com/novels/python/list"
)

href = "../chapter/10"

result = base_url.join(URL(href))

print(result)
```

URL tương đối:

```text
../chapter/10
```

có nghĩa:

```text
đi lên một cấp
+
chapter/10
```

Đây là một trong những trường hợp nối string sẽ dễ sai.

---

# 14. Relative URL với `.`

Ví dụ:

```python
from yarl import URL

base_url = URL(
    "https://example.com/novels/python/"
)

href = "./chapter/10"

result = base_url.join(URL(href))

print(result)
```

Kết quả được resolve theo hierarchy của URL.

Trong crawler, các dạng:

```text
./
../
../../
```

không hiếm.

---

# 15. Query-only URL

Ví dụ trang:

```text
https://example.com/novels?page=1
```

HTML:

```html
<a href="?page=2">Next</a>
```

Ta làm:

```python
from yarl import URL

base_url = URL(
    "https://example.com/novels?page=1"
)

next_url = base_url.join(
    URL("?page=2")
)

print(next_url)
```

Kết quả:

```text
https://example.com/novels?page=2
```

Đây chính là trường hợp rất quan trọng cho:

# Pagination

Phần IV Buổi 33 chúng ta sẽ xây nó thành logic riêng.

---

# 16. Fragment-only URL

Ví dụ:

```text
https://example.com/novel/1
```

HTML:

```html
<a href="#chapter-10">
```

Resolve:

```python
from yarl import URL

base_url = URL(
    "https://example.com/novel/1"
)

result = base_url.join(
    URL("#chapter-10")
)

print(result)
```

→

```text
https://example.com/novel/1#chapter-10
```

Nhưng nhớ bài 16:

```text
fragment
```

thường không được gửi tới server trong HTTP request.

Vì vậy crawler network layer thường có thể:

```python
request_url = result.with_fragment(None)
```

nếu fragment chỉ phục vụ UI.

---

# 17. Xây `URLResolver`

Bây giờ thay vì để parser trực tiếp gọi:

```python
page_url.join(URL(href))
```

ta có thể tạo:

```python
from yarl import URL


class URLResolver:

    def resolve(
        self,
        base_url: URL,
        href: str,
    ) -> URL:
        return base_url.join(URL(href))
```

Sử dụng:

```python
resolver = URLResolver()

page_url = URL(
    "https://example.com/novels/list"
)

href = "/novels/python"

url = resolver.resolve(
    page_url,
    href,
)

print(url)
```

---

# 18. Có nên tạo class ngay không?

Không nhất thiết.

Với logic đơn giản:

```python
def resolve_url(
    base_url: URL,
    href: str,
) -> URL:
    return base_url.join(URL(href))
```

là đủ.

Trong kiến trúc crawler của bạn, tôi sẽ ưu tiên:

```text
simple function
```

trước.

Chỉ tạo:

```python
URLResolver
```

khi resolver bắt đầu có policy:

```text
- allowed schemes
- strip fragment
- same-origin
- normalize
- canonicalization
- reject javascript:
- reject mailto:
- custom website rules
```

Đây là nguyên tắc **balanced abstraction** mà chúng ta đã dùng khi thiết kế Parser.

---

# 19. `href` không phải lúc nào cũng là URL HTTP

HTML có thể chứa:

```html
<a href="javascript:void(0)">
<a href="mailto:test@example.com">
<a href="tel:123456">
<a href="#">
<a href="">
```

Không phải tất cả đều là URL mà crawler nên request.

Do đó:

```python
URL(href)
```

không đồng nghĩa:

```text
"URL này được phép fetch"
```

Hai trách nhiệm khác nhau:

```text
URL parsing
      ↓
URL object

URL policy
      ↓
có được crawl hay không?
```

Buổi 47 sau này sẽ có:

```text
URL Policy
```

---

# 20. Kiểm tra scheme

Ví dụ:

```python
from yarl import URL

url = URL("javascript:void(0)")

print(url.scheme)
```

Bạn có thể kiểm tra:

```python
if url.scheme not in {"", "http", "https"}:
    # không phải URL HTTP crawler cần
    ...
```

Nhưng cần nhớ:

```text
relative URL
```

có:

```python
url.scheme == ""
```

Ví dụ:

```python
URL("/novel/python")
```

Do đó:

```text
scheme == ""
```

không có nghĩa URL không hợp lệ.

Nó có thể chỉ là **relative URL**.

---

# 21. Resolver thực tế hơn

Ta có thể viết:

```python
from yarl import URL


ALLOWED_SCHEMES = {"http", "https"}


def resolve_url(
    base_url: URL,
    href: str,
) -> URL | None:

    href = href.strip()

    if not href:
        return None

    relative_url = URL(href)

    # Scheme của href nếu có
    if relative_url.scheme:
        if relative_url.scheme not in ALLOWED_SCHEMES:
            return None

    result = base_url.join(relative_url)

    if result.scheme not in ALLOWED_SCHEMES:
        return None

    return result
```

Test:

```python
base_url = URL(
    "https://example.com/novels/list"
)

hrefs = [
    "/novels/python",
    "chapter-1",
    "../chapter-2",
    "https://example.com/chapter/3",
    "javascript:void(0)",
    "",
]

for href in hrefs:
    result = resolve_url(base_url, href)

    print(f"{href!r} -> {result}")
```

Đây đã bắt đầu giống một thành phần thật trong crawler.

---

# 22. Nhưng đừng nhồi quá nhiều logic vào resolver

Chúng ta **chưa nên** đưa vào đây:

```text
deduplication
canonicalization
fetch
retry
proxy
parser
database
```

Resolver chỉ nên tập trung:

```text
href
 +
base URL
 ↓
resolved URL
```

Các concern khác để sau:

```text
Resolver
    ↓
Normalizer
    ↓
Policy
    ↓
Deduplicator
    ↓
Fetcher
```

Đây là kiến trúc rất sạch.

---

# 23. Đưa vào Parser

Giả sử Parser nhận:

```python
page_url: URL
html: str
```

Ví dụ:

```python
from yarl import URL


def parse_links(
    page_url: URL,
    hrefs: list[str],
) -> list[URL]:

    result = []

    for href in hrefs:
        url = page_url.join(URL(href))
        result.append(url)

    return result
```

Test:

```python
page_url = URL(
    "https://example.com/novels/list"
)

hrefs = [
    "/novel/python",
    "/novel/sqlite",
    "/novel/yarl",
]

urls = parse_links(
    page_url,
    hrefs,
)

for url in urls:
    print(url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/novel/sqlite
https://example.com/novel/yarl
```

---

# 24. Đây chính là cầu nối sang `selectolax`

Sau này Parser của bạn sẽ có kiểu:

```text
HTTPX
  ↓
page_source
  ↓
selectolax
  ↓
<a href>
  ↓
href
  ↓
yarl
  ↓
absolute URL
```

Ví dụ:

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_links(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    urls = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if not href:
            continue

        url = page_url.join(URL(href))

        urls.append(url)

    return urls
```

Đây là một đoạn code rất gần với Parser thực tế của Novel Crawler.

---

# 25. Ví dụ hoàn chỉnh: HTML → Absolute URLs

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_links(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    result: list[URL] = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if not href:
            continue

        url = page_url.join(URL(href))

        result.append(url)

    return result


def main() -> None:
    page_url = URL(
        "https://truyen.example/novels/"
    )

    html = """
    <html>
        <body>
            <a href="/novel/python">Python</a>
            <a href="/novel/sqlite">SQLite</a>
            <a href="yarl">Yarl</a>
            <a href="../about">About</a>
        </body>
    </html>
    """

    urls = parse_links(
        page_url,
        html,
    )

    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy các `href` được chuyển thành URL dựa trên:

```python
page_url
```

Đây chính là nền móng cho **ListingParser** và **NovelParser** của crawler.

---

# 26. Một vấn đề cần nhớ: `<base href>`

HTML có thể chứa:

```html
<head>
    <base href="https://example.com/">
</head>
```

Khi đó URL resolution của HTML có thể sử dụng `<base>` thay vì đơn giản chỉ lấy URL của document.

Đây là một case nâng cao.

Ở phiên bản crawler đầu tiên, bạn có thể dùng:

```text
document URL
```

làm base.

Sau này nếu website thực tế cần hỗ trợ `<base href>`, ta có thể thêm:

```text
BaseURLResolver
```

vào Parser infrastructure.

Không nên xây abstraction này ngay từ đầu nếu chưa có nhu cầu.

---

# 27. Kiến trúc sau Buổi 31

Bây giờ pipeline bắt đầu hình thành:

```text
                    HTTPX
                      │
                      ▼
                 page_source
                      │
                      ▼
                  selectolax
                      │
                      ▼
                   href
                      │
                      ▼
                URL Resolver
                      │
                      ▼
                 yarl.URL
                      │
              ┌───────┴────────┐
              ▼                ▼
          Parser          URL Policy
```

Trong đó:

### `selectolax`

Chịu trách nhiệm:

```text
HTML → href
```

### `yarl`

Chịu trách nhiệm:

```text
href → URL
```

### URL Resolver

Chịu trách nhiệm:

```text
relative URL
       +
base URL
       ↓
absolute URL
```

### Fetcher

Sau này chịu trách nhiệm:

```text
URL → HTTP response
```

---

# 28. Nguyên tắc kiến trúc quan trọng

Đừng để Parser làm:

```python
requests.get(...)
```

Đừng để Resolver làm:

```python
httpx.get(...)
```

Đừng để `yarl.URL` biết:

```text
database
repository
retry
proxy
crawler queue
```

Mỗi thành phần một trách nhiệm:

```text
selectolax
    ↓
HTML parsing

yarl
    ↓
URL representation/manipulation

Resolver
    ↓
URL resolution

Policy
    ↓
URL có được crawl?

Fetcher
    ↓
HTTP

Repository
    ↓
Persistence
```

Đây chính là tinh thần **SRP + Clean Architecture**.

---

# 29. Helper nhỏ nên nhớ

Trong crawler, function này sẽ xuất hiện rất nhiều:

```python
from yarl import URL


def resolve_url(
    base_url: URL,
    href: str,
) -> URL:
    return base_url.join(URL(href))
```

Ví dụ:

```python
page_url = URL(
    "https://example.com/novel/python/"
)

print(
    resolve_url(
        page_url,
        "chapter-1",
    )
)
```

---

# 30. Bài tập thực hành

### Bài 1 — Cơ bản

Cho:

```python
base = URL("https://example.com/novels/")
```

resolve:

```text
/novel/python
```

```text
chapter-1
```

```text
../about
```

```text
? page=2
```

và quan sát kết quả.

---

### Bài 2 — Function

Viết:

```python
def resolve_url(
    base_url: URL,
    href: str,
) -> URL:
    ...
```

Không dùng:

```python
+
```

để nối URL.

---

### Bài 3 — HTML

Cho:

```html
<a href="/novel/python">Python</a>
<a href="/novel/sqlite">SQLite</a>
<a href="chapter-1">Chapter 1</a>
<a href="../home">Home</a>
```

Dùng:

```python
selectolax
```

để lấy `href`, sau đó dùng:

```python
yarl
```

để chuyển thành absolute URL.

---

### Bài 4 — Novel Crawler

Thiết kế:

```text
ListingParser
    │
    ├── title
    ├── author
    └── url
```

Trong đó `url` phải luôn là:

```python
yarl.URL
```

và parser nhận:

```python
page_url: URL
page_source: str
```

Ví dụ:

```text
page_url:
https://truyen.example/danh-sach?page=2
```

HTML:

```html
<a href="/truyen/python">
    Python Cơ Bản
</a>
```

Output:

```python
NovelCard(
    title="Python Cơ Bản",
    url=URL("https://truyen.example/truyen/python")
)
```

---

# Tóm tắt Buổi 31

Điều quan trọng nhất hôm nay chỉ cần nhớ:

```python
base_url.join(URL(href))
```

Ví dụ:

```python
base_url = URL("https://example.com/novels/")
href = "../chapter/10"

url = base_url.join(URL(href))
```

**Không dùng string concatenation để resolve URL.**

Pipeline của crawler:

```text
HTML
 │
 ▼
selectolax
 │
 ▼
href="/novel/python"
 │
 ▼
URL(href)
 │
 ▼
base_url.join(...)
 │
 ▼
https://example.com/novel/python
```

Và đây là nền tảng trực tiếp cho:

**Buổi 32 — `<a href>` → URL**, nơi chúng ta sẽ xây một `LinkExtractor` thực tế bằng **selectolax + yarl**, xử lý relative/absolute URL, href rỗng, `#fragment`, `javascript:`, `mailto:` và lọc những link mà crawler không nên đưa vào queue.
