# Buổi 33 — Pagination URL

Ở Buổi 32, chúng ta đã xây được:

```text
HTML
 ↓
<a href>
 ↓
yarl.URL
 ↓
absolute URL
```

Bây giờ xử lý một vấn đề rất quan trọng của **Novel Crawler**:

```text
Trang 1
   ↓
trang 2
   ↓
trang 3
   ↓
trang 4
   ↓
...
```

Website truyện có thể dùng rất nhiều kiểu pagination:

```text
/truyen?page=2
/truyen?sort=new&page=2
/truyen/trang-2
/truyen/page/2
?page=2
```

Mục tiêu của bài này là xây được:

```text
Pagination
    ↓
extract next page
    ↓
resolve URL bằng yarl
    ↓
Pagination URL
```

---

# 1. Pagination thực chất cũng chỉ là URL

Ví dụ trang hiện tại:

```text
https://example.com/truyen
```

HTML:

```html
<a href="/truyen?page=2">Trang 2</a>
```

Ta lấy:

```python
href = "/truyen?page=2"
```

rồi:

```python
url = page_url.join(URL(href))
```

Kết quả:

```text
https://example.com/truyen?page=2
```

Do đó:

> Pagination không phải một loại URL đặc biệt. Nó chỉ là một URL mà crawler dùng để đi tới trang kế tiếp.

---

# 2. Pagination có nhiều dạng

## Dạng 1 — Query parameter

```html
<a href="/truyen?page=2">2</a>
```

URL:

```text
https://example.com/truyen?page=2
```

---

## Dạng 2 — `?page=2`

Nếu hiện tại:

```text
https://example.com/truyen
```

HTML:

```html
<a href="?page=2">Trang 2</a>
```

thì:

```python
page_url.join(URL("?page=2"))
```

→

```text
https://example.com/truyen?page=2
```

---

## Dạng 3 — `/trang-2`

```html
<a href="/truyen/trang-2">Trang 2</a>
```

→

```text
https://example.com/truyen/trang-2
```

---

## Dạng 4 — relative path

Trang hiện tại:

```text
https://example.com/truyen/
```

HTML:

```html
<a href="trang-2">Trang 2</a>
```

→

```text
https://example.com/truyen/trang-2
```

---

# 3. Đừng đoán URL bằng string

Không nên:

```python
next_url = str(page_url) + "?page=2"
```

hoặc:

```python
next_url = f"{page_url}/trang-{page + 1}"
```

vì website thực tế có thể có:

```text
?page=2
?sort=new&page=2
/trang-2
/page/2
```

Thay vào đó, parser lấy `href` thực tế từ HTML:

```python
href = node.attributes.get("href")

url = page_url.join(URL(href))
```

Parser **đọc website**, không tự đoán website.

---

# 4. HTML pagination đơn giản

Ví dụ:

```html
<nav class="pagination">
    <a href="/truyen">1</a>
    <a href="/truyen?page=2">2</a>
    <a href="/truyen?page=3">3</a>
    <a href="/truyen?page=2">Next</a>
</nav>
```

Dùng selectolax:

```python
from selectolax.parser import HTMLParser
from yarl import URL


html = """
<nav class="pagination">
    <a href="/truyen">1</a>
    <a href="/truyen?page=2">2</a>
    <a href="/truyen?page=3">3</a>
    <a href="/truyen?page=2">Next</a>
</nav>
"""

tree = HTMLParser(html)

for node in tree.css(".pagination a[href]"):
    href = node.attributes.get("href")
    text = node.text(strip=True)

    print(text, href)
```

Kết quả:

```text
1 /truyen
2 /truyen?page=2
3 /truyen?page=3
Next /truyen?page=2
```

---

# 5. Nhưng crawler thường không cần tất cả page

Có hai chiến lược.

### Strategy A — lấy tất cả page

```text
1
2
3
4
5
...
```

### Strategy B — chỉ lấy `Next`

```text
1
 ↓
Next
 ↓
Next
 ↓
Next
```

Với crawler listing, Strategy B thường đơn giản hơn.

```text
parse page 1
     ↓
extract novels
     ↓
extract next URL
     ↓
fetch next
     ↓
parse
     ↓
extract next URL
     ↓
...
```

---

# 6. Tìm `Next`

Ví dụ HTML:

```html
<nav class="pagination">
    <a href="/truyen?page=1">1</a>
    <a href="/truyen?page=2">2</a>
    <a href="/truyen?page=3">3</a>

    <a class="next" href="/truyen?page=2">
        Next
    </a>
</nav>
```

Ta có thể:

```python
next_node = tree.css_first("a.next")
```

Sau đó:

```python
if next_node:
    href = next_node.attributes.get("href")

    if href:
        next_url = page_url.join(URL(href))
```

---

# 7. Viết `parse_next_url()`

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_next_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = tree.css_first("a.next")

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

Sử dụng:

```python
page_url = URL(
    "https://example.com/truyen"
)

html = """
<nav class="pagination">
    <a href="/truyen?page=1">1</a>
    <a href="/truyen?page=2">2</a>
    <a class="next" href="/truyen?page=2">
        Next
    </a>
</nav>
"""

next_url = parse_next_url(
    page_url,
    html,
)

print(next_url)
```

Kết quả:

```text
https://example.com/truyen?page=2
```

---

# 8. Nếu không có Next

Ví dụ trang cuối:

```html
<nav class="pagination">
    <a href="/truyen?page=3">3</a>
</nav>
```

Không có:

```html
<a class="next">
```

thì:

```python
next_url = parse_next_url(page_url, html)

print(next_url)
```

→

```text
None
```

Đây là một design rất đẹp:

```text
URL
    → còn trang tiếp theo

None
    → hết pagination
```

Crawler có thể viết:

```python
while page_url is not None:
    ...
    page_url = parse_next_url(...)
```

---

# 9. Complete crawler pagination loop

Bây giờ ghép vào một crawler nhỏ.

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_next_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = tree.css_first("a.next")

    if node is None:
        return None

    href = node.attributes.get("href")

    if not href:
        return None

    href = href.strip()

    if not href:
        return None

    return page_url.join(URL(href))


def crawl_pagination(
    start_url: URL,
    pages: dict[str, str],
) -> None:

    page_url: URL | None = start_url

    while page_url is not None:

        print(f"Crawl: {page_url}")

        html = pages.get(str(page_url))

        if html is None:
            print("Không có HTML")
            break

        next_url = parse_next_url(
            page_url,
            html,
        )

        page_url = next_url
```

Test:

```python
pages = {
    "https://example.com/truyen": """
        <a class="next"
           href="/truyen?page=2">
           Next
        </a>
    """,

    "https://example.com/truyen?page=2": """
        <a class="next"
           href="/truyen?page=3">
           Next
        </a>
    """,

    "https://example.com/truyen?page=3": """
        <span>Không còn trang tiếp</span>
    """,
}


crawl_pagination(
    URL("https://example.com/truyen"),
    pages,
)
```

Kết quả:

```text
Crawl: https://example.com/truyen
Crawl: https://example.com/truyen?page=2
Crawl: https://example.com/truyen?page=3
```

---

# 10. Pagination kiểu `trang-2`

Website truyện Việt Nam rất hay có dạng:

```text
/truyen/trang-2
/truyen/trang-3
```

HTML:

```html
<a class="next" href="/truyen/trang-2">
    Trang sau
</a>
```

Không cần code riêng.

```python
next_url = page_url.join(
    URL("/truyen/trang-2")
)
```

→

```text
https://example.com/truyen/trang-2
```

Đây chính là lợi ích của việc để **HTML quyết định href**, còn yarl đảm nhiệm URL resolution.

---

# 11. Pagination kiểu `?page=2`

HTML:

```html
<a class="next" href="?page=2">
    Next
</a>
```

Nếu:

```python
page_url = URL(
    "https://example.com/truyen"
)
```

thì:

```python
next_url = page_url.join(
    URL("?page=2")
)
```

→

```text
https://example.com/truyen?page=2
```

Nếu URL hiện tại:

```text
https://example.com/truyen?sort=new
```

thì:

```python
page_url.join(URL("?page=2"))
```

sẽ tạo query mới theo URL reference.

Điểm này rất quan trọng:

> Đừng tự ghép `&page=2` bằng string.

---

# 12. Pagination có thể có `rel="next"`

HTML tốt hơn có thể là:

```html
<a
    rel="next"
    href="/truyen?page=2"
>
    Next
</a>
```

Khi đó selector rất rõ:

```python
node = tree.css_first(
    'a[rel="next"]'
)
```

Đây thường là cách tốt hơn nếu website sử dụng `rel="next"` chuẩn.

---

# 13. Fallback nhiều selector

Website thực tế có thể không thống nhất.

Ví dụ:

```text
a[rel="next"]
a.next
a.pagination-next
```

Có thể viết:

```python
def find_next_node(tree):
    selectors = [
        'a[rel="next"]',
        "a.next",
        "a.pagination-next",
    ]

    for selector in selectors:
        node = tree.css_first(selector)

        if node is not None:
            return node

    return None
```

Sau đó:

```python
def parse_next_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    node = find_next_node(tree)

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

Đây là abstraction hợp lý vì chúng ta có **một business concern rõ ràng**:

```text
Tìm link trang kế tiếp
```

---

# 14. Đừng dựa vào text `"Next"` quá sớm

Có website:

```html
<a href="/trang-2">»</a>
```

Website khác:

```html
<a href="/trang-2">Sau</a>
```

Website khác:

```html
<a href="/trang-2">Next</a>
```

Nếu code:

```python
if node.text(strip=True) == "Next":
```

thì parser dễ hỏng.

Ưu tiên:

```html
rel="next"
```

hoặc:

```css
a.next
```

hoặc selector đặc trưng của website.

---

# 15. Pagination trong Plugin của Novel Crawler

Đây là chỗ kiến trúc của chúng ta bắt đầu rõ ràng hơn.

Plugin:

```text
plugins/
└── truyenfullsource/
    ├── listing_parser.py
    ├── novel_parser.py
    └── chapter_parser.py
```

`listing_parser.py` có thể:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class ListingPage:
    novels: list
    next_url: URL | None
```

Parser:

```python
def parse_listing(
    page_url: URL,
    html: str,
) -> ListingPage:

    novels = ...
    next_url = parse_next_url(
        page_url,
        html,
    )

    return ListingPage(
        novels=novels,
        next_url=next_url,
    )
```

Kết quả:

```text
ListingPage
├── novels
└── next_url
```

---

# 16. Application layer sử dụng nó

Parser không nên tự fetch trang tiếp theo.

Parser chỉ trả:

```python
ListingPage(
    novels=[...],
    next_url=...
)
```

Application:

```python
page = parser.parse(
    page_url,
    page_source,
)

save_novels(page.novels)

if page.next_url:
    queue.add(page.next_url)
```

Kiến trúc:

```text
                Fetcher
                   │
                   ▼
              page_source
                   │
                   ▼
                Parser
                   │
          ┌────────┴────────┐
          ▼                 ▼
       novels           next_url
          │                 │
          ▼                 ▼
     Repository            Queue
```

Đây là cách rất phù hợp với kiến trúc crawler mà chúng ta đã xây dựng trước đó.

---

# 17. Không để parser tự crawl

Không nên:

```python
def parse_listing(url):
    html = httpx.get(url)
    ...
    httpx.get(next_url)
    ...
```

Vì parser lúc này vừa:

```text
HTML parsing
+
HTTP
+
pagination
+
retry
```

vi phạm separation of concerns.

Parser chỉ:

```text
page_source
    ↓
parse
    ↓
domain data
```

Fetcher:

```text
URL
    ↓
HTTP
    ↓
page_source
```

Queue:

```text
URL
    ↓
schedule
```

---

# 18. Chống pagination loop

Một website lỗi có thể trả:

```text
page 1
 ↓
page 2
 ↓
page 2
 ↓
page 2
 ↓
...
```

Nếu chỉ:

```python
while page_url:
```

crawler sẽ chạy vô hạn.

Sau này chúng ta có:

```text
URL Deduplication
```

nhưng ngay từ bây giờ có thể hiểu nguyên tắc:

```python
visited: set[URL] = set()

while page_url is not None:

    if page_url in visited:
        break

    visited.add(page_url)

    ...
```

Yarl `URL` có thể sử dụng trong `set` vì URL object có tính hashable.

Ví dụ:

```python
visited: set[URL] = set()

url = URL("https://example.com/truyen")

visited.add(url)

print(url in visited)
```

→

```text
True
```

Nhưng bài **deduplication** chính thức sẽ là Buổi 38.

---

# 19. Một implementation thực tế hơn

Tạm thời ta có thể viết:

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_next_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    selectors = (
        'a[rel="next"]',
        "a.next",
        "a.pagination-next",
    )

    for selector in selectors:

        node = tree.css_first(selector)

        if node is None:
            continue

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme not in ("", "http", "https"):
            continue

        return page_url.join(href_url)

    return None
```

Điểm hay:

```text
HTML
 ↓
find next
 ↓
href
 ↓
validate scheme
 ↓
yarl
 ↓
absolute URL
```

---

# 20. Test đầy đủ

```python
from selectolax.parser import HTMLParser
from yarl import URL


def parse_next_url(
    page_url: URL,
    html: str,
) -> URL | None:

    tree = HTMLParser(html)

    selectors = (
        'a[rel="next"]',
        "a.next",
        "a.pagination-next",
    )

    for selector in selectors:

        node = tree.css_first(selector)

        if node is None:
            continue

        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme not in ("", "http", "https"):
            continue

        return page_url.join(href_url)

    return None


def test(
    name: str,
    page_url: str,
    html: str,
):
    result = parse_next_url(
        URL(page_url),
        html,
    )

    print(f"{name}:")
    print(f"  {result}")
    print()


test(
    "Query",
    "https://example.com/truyen",
    """
    <a class="next" href="?page=2">
        Next
    </a>
    """,
)

test(
    "Path",
    "https://example.com/truyen/",
    """
    <a class="next" href="trang-2">
        Next
    </a>
    """,
)

test(
    "Root relative",
    "https://example.com/truyen/",
    """
    <a rel="next" href="/truyen/trang-2">
        Sau
    </a>
    """,
)

test(
    "No next",
    "https://example.com/truyen/",
    """
    <span>Trang cuối</span>
    """,
)

test(
    "Invalid scheme",
    "https://example.com/truyen/",
    """
    <a class="next" href="javascript:void(0)">
        Next
    </a>
    """,
)
```

Kết quả mong đợi:

```text
Query:
  https://example.com/truyen?page=2

Path:
  https://example.com/truyen/trang-2

Root relative:
  https://example.com/truyen/trang-2

No next:
  None

Invalid scheme:
  None
```

---

# 21. Một lưu ý quan trọng: `<base href>`

HTML có thể chứa:

```html
<head>
    <base href="https://cdn.example.com/">
</head>
```

và:

```html
<a href="chapter-1">
    Chapter 1
</a>
```

Theo chuẩn HTML, base URL có thể thay đổi cách resolve:

```text
chapter-1
```

Đây là một case nâng cao.

**Chưa xử lý ở Buổi 33.**

Ta sẽ giữ pipeline hiện tại đơn giản:

```text
page_url
    ↓
href
    ↓
page_url.join(URL(href))
```

Sau này nếu gặp crawler thực tế cần hỗ trợ `<base>`, ta bổ sung một:

```text
DocumentBaseResolver
```

thay vì làm `parse_next_url()` trở nên phức tạp.

---

# 22. Vai trò của yarl trong Pagination

Sau Buổi 33, cần nhớ một nguyên tắc:

> **Parser phát hiện `href`; yarl quyết định URL tuyệt đối.**

Ví dụ:

```python
href = node.attributes["href"]

next_url = page_url.join(
    URL(href)
)
```

Không phải:

```python
next_url = f"{page_url}/{href}"
```

---

# 23. Kiến trúc hoàn chỉnh hiện tại

```text
HTTPX
  │
  │ page_source
  ▼
Selectolax
  │
  ├── Novel links
  │
  └── Pagination href
             │
             ▼
          yarl.URL
             │
             ▼
       Absolute URL
             │
             ▼
        Crawl Queue
             │
             ▼
           Fetcher
```

Và trong Listing Parser:

```text
ListingParser
│
├── parse novel cards
│
└── parse next URL
         │
         ▼
     URL | None
```

Đây là nền tảng để Buổi 34 chúng ta xử lý **Chapter URL**:

```text
Novel detail page
        ↓
<a href="...">
        ↓
chapter href
        ↓
yarl.URL
        ↓
Chapter URL
```

và bắt đầu kết nối trực tiếp với kiến trúc:

```text
Novel
 └── Chapter
      └── ChapterURL
```

---

## Tóm tắt Buổi 33

```text
1. Pagination cũng chỉ là URL.
2. Lấy href bằng selectolax.
3. Không tự đoán URL bằng string.
4. Dùng page_url.join(URL(href)).
5. Hỗ trợ ?page=2, /trang-2, relative path...
6. Ưu tiên rel="next" hoặc selector đặc trưng.
7. Không để parser tự fetch trang tiếp theo.
8. Parser trả URL | None.
9. Application/Queue quyết định crawl tiếp.
10. URL deduplication sẽ xử lý sâu ở Buổi 38.
```

Pipeline hiện tại:

```text
31 Relative URL → Absolute URL
             ↓
32 <a href> → URL
             ↓
33 Pagination
             ↓
34 Chapter URL
             ↓
35 Image URL
             ↓
36 URL Normalization
             ↓
37 URL Comparison
             ↓
38 URL Deduplication
             ↓
39 Canonical URL
             ↓
40 URLBuilder
```
