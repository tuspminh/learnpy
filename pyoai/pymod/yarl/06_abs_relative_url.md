# Buổi 6 — URL tương đối và URL tuyệt đối

Đây là bài **rất quan trọng đối với crawler**. Khi parser đọc HTML, `href` thường không chứa đầy đủ domain:

```html
<a href="/truyen/kiem-hiep">Kiếm Hiệp</a>
```

hoặc:

```html
<a href="chuong-2">Chương 2</a>
```

Trong khi `httpx` cần một URL có thể request được:

```text
https://example.com/truyen/kiem-hiep
```

Mục tiêu của buổi này là hiểu rõ:

```text
Relative URL
     ↓
Base URL
     ↓
Absolute URL
```

---

# 1. Absolute URL là gì?

URL tuyệt đối chứa đầy đủ thông tin cần thiết:

```text
https://example.com/truyen/kiem-hiep
```

Có:

```text
scheme = https
host   = example.com
path   = /truyen/kiem-hiep
```

Trong `yarl`:

```python
from yarl import URL

url = URL("https://example.com/truyen/kiem-hiep")

print(url.is_absolute())
print(url.scheme)
print(url.host)
print(url.path)
```

Kết quả:

```text
True
https
example.com
/truyen/kiem-hiep
```

---

# 2. Relative URL là gì?

URL tương đối không chứa đầy đủ domain.

Ví dụ:

```text
/truyen/kiem-hiep
```

hoặc:

```text
chuong-2
```

hoặc:

```text
../chuong-2
```

Trong HTML, đây là chuyện cực kỳ bình thường:

```html
<a href="/truyen/kiem-hiep">
```

```html
<a href="chuong-2">
```

```html
<img src="/images/cover.jpg">
```

Parser của crawler phải xử lý chúng.

---

# 3. Tạo relative URL bằng `yarl`

```python
from yarl import URL

url = URL("/truyen/kiem-hiep")

print(url)
print(url.is_absolute())
```

Kết quả:

```text
/truyen/kiem-hiep
False
```

Ta có:

```text
URL("/truyen/kiem-hiep")
        │
        └── relative URL
```

---

# 4. Absolute và relative

```python
from yarl import URL

absolute = URL("https://example.com/truyen/kiem-hiep")

relative = URL("/truyen/kiem-hiep")

print(absolute.is_absolute())
print(relative.is_absolute())
```

Kết quả:

```text
True
False
```

---

# 5. Vì sao crawler phải quan tâm?

Giả sử parser lấy được:

```html
<a href="/truyen/kiem-hiep">
    Kiếm Hiệp
</a>
```

Parser nhận:

```python
href = "/truyen/kiem-hiep"
```

Nhưng fetcher cần:

```text
https://example.com/truyen/kiem-hiep
```

Do đó cần:

```text
HTML
 │
 │ href="/truyen/kiem-hiep"
 ▼
Parser
 │
 │ relative URL
 ▼
URL Resolver
 │
 │ base + relative
 ▼
absolute URL
 │
 ▼
Fetcher
```

Đây là một boundary rất quan trọng trong crawler architecture.

---

# 6. `yarl.URL.join()`

`yarl` cung cấp:

```python
URL.join()
```

để resolve một URL tương đối dựa trên một URL cơ sở.

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com")

relative = URL("/truyen/kiem-hiep")

absolute = base.join(relative)

print(absolute)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep
```

Đây là thao tác chúng ta sẽ dùng rất nhiều trong parser.

---

# 7. Ví dụ cơ bản

```python
from yarl import URL


base = URL("https://example.com")

urls = [
    URL("/novels"),
    URL("/novels/kiem-hiep"),
    URL("/images/cover.jpg"),
]

for relative in urls:
    absolute = base.join(relative)
    print(absolute)
```

Kết quả:

```text
https://example.com/novels
https://example.com/novels/kiem-hiep
https://example.com/images/cover.jpg
```

---

# 8. Relative URL không nhất thiết bắt đầu bằng `/`

Đây là điểm rất quan trọng.

Ví dụ:

```text
chuong-2
```

Giả sử trang hiện tại là:

```text
https://example.com/truyen/kiem-hiep/chuong-1
```

Ta có:

```python
from yarl import URL

base = URL("https://example.com/truyen/kiem-hiep/chuong-1")

relative = URL("chuong-2")

result = base.join(relative)

print(result)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep/chuong-2
```

Đây là URL resolution theo quy tắc URL, không phải đơn giản:

```python
base + relative
```

---

# 9. Relative bắt đầu bằng `/`

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com/truyen/kiem-hiep/chuong-1")

relative = URL("/images/cover.jpg")

result = base.join(relative)

print(result)
```

Kết quả:

```text
https://example.com/images/cover.jpg
```

Chú ý:

```text
base:
https://example.com/truyen/kiem-hiep/chuong-1

relative:
/images/cover.jpg

result:
https://example.com/images/cover.jpg
```

`/` ở đầu có nghĩa là bắt đầu từ **root của domain**.

---

# 10. Relative `../`

Ví dụ:

```text
https://example.com/truyen/kiem-hiep/chuong-10
```

Muốn quay lên một cấp:

```text
../
```

Ta có:

```python
from yarl import URL

base = URL("https://example.com/truyen/kiem-hiep/chuong-10")

relative = URL("../")

result = base.join(relative)

print(result)
```

Kết quả tương ứng với việc đi lên một cấp path.

---

# 11. `./`

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com/truyen/kiem-hiep/")

relative = URL("./chuong-2")

print(base.join(relative))
```

`./` biểu thị thư mục hiện tại.

---

# 12. URL hiện tại làm base

Đây là cách chúng ta thường gặp trong parser.

HTML:

```html
<a href="chuong-2">Chương 2</a>
```

Trang hiện tại:

```text
https://example.com/truyen/kiem-hiep/
```

Code:

```python
from yarl import URL


page_url = URL("https://example.com/truyen/kiem-hiep/")

href = "chuong-2"

chapter_url = page_url.join(URL(href))

print(chapter_url)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep/chuong-2
```

---

# 13. Đây là pattern cực kỳ quan trọng

Trong parser:

```python
href = node.attributes.get("href")

relative_url = URL(href)

absolute_url = page_url.join(relative_url)
```

Có thể viết:

```python
from yarl import URL


def resolve_url(
    page_url: URL,
    href: str,
) -> URL:
    return page_url.join(URL(href))
```

Sau đó:

```python
page_url = URL("https://example.com/truyen/kiem-hiep/")

print(resolve_url(page_url, "chuong-2"))

print(resolve_url(page_url, "/images/cover.jpg"))

print(resolve_url(page_url, "/truyen/abc"))
```

---

# 14. `<a href>` trong Novel Parser

Giả sử HTML:

```html
<a href="/truyen/kiem-hiep">
    Kiếm Hiệp
</a>

<a href="/truyen/tien-hiep">
    Tiên Hiệp
</a>
```

Parser có thể làm:

```python
from yarl import URL


page_url = URL("https://example.com/the-loai")

hrefs = [
    "/truyen/kiem-hiep",
    "/truyen/tien-hiep",
]

for href in hrefs:
    url = page_url.join(URL(href))
    print(url)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep
https://example.com/truyen/tien-hiep
```

---

# 15. Một lỗi rất phổ biến

Không nên:

```python
url = URL(page_url + href)
```

Ví dụ:

```python
page_url = "https://example.com/truyen"
href = "/abc"

url = URL(page_url + href)
```

có thể tình cờ hoạt động:

```text
https://example.com/truyen/abc
```

Nhưng:

```python
page_url = "https://example.com/truyen/"
href = "/abc"
```

lại thành:

```text
https://example.com/truyen//abc
```

Và quan trọng hơn, cách này **không xử lý đúng các quy tắc relative URL** như:

```text
../
./
query
fragment
```

Hãy để `yarl` xử lý:

```python
URL(page_url).join(URL(href))
```

---

# 16. `href` có thể là absolute URL

HTML hoàn toàn có thể chứa:

```html
<a href="https://other-site.com/book">
```

Khi đó:

```python
page_url = URL("https://example.com/novels")

href = "https://other-site.com/book"

result = page_url.join(URL(href))

print(result)
```

Kết quả:

```text
https://other-site.com/book
```

Tức là `join()` không đơn giản là:

```text
base + relative
```

Nó thực hiện URL resolution.

---

# 17. Kiểm tra trước khi resolve

Trong crawler, bạn có thể viết:

```python
from yarl import URL


def resolve_url(
    base_url: URL,
    href: str,
) -> URL:

    url = URL(href)

    if url.is_absolute():
        return url

    return base_url.join(url)
```

Test:

```python
base = URL("https://example.com/truyen/")

print(resolve_url(base, "/novel/abc"))

print(resolve_url(base, "chapter-2"))

print(resolve_url(base, "https://other.com/book"))
```

---

# 18. Nhưng có thể đơn giản hơn

Thực tế `join()` đã xử lý absolute URL:

```python
def resolve_url(base_url: URL, href: str) -> URL:
    return base_url.join(URL(href))
```

Đây thường là cách tôi ưu tiên.

---

# 19. `href` rỗng

Parser thực tế sẽ gặp:

```html
<a href="">
```

hoặc:

```html
<a>
```

Không nên blindly:

```python
URL(href)
```

Hãy kiểm tra:

```python
href = node.attributes.get("href")

if not href:
    return None

url = page_url.join(URL(href))
```

---

# 20. `href="#"`

Một trang web có thể có:

```html
<a href="#">Click</a>
```

Đây là fragment URL, không phải link chapter thực sự.

Crawler nên cân nhắc bỏ:

```python
if not href:
    return None

if href.startswith("#"):
    return None
```

---

# 21. `javascript:`

Có thể gặp:

```html
<a href="javascript:void(0)">
```

Không phải URL HTTP.

Có thể lọc:

```python
if href.startswith("javascript:"):
    return None
```

---

# 22. `mailto:`

Tương tự:

```html
<a href="mailto:test@example.com">
```

Crawler truyện thường không muốn crawl loại này.

Ta có thể kiểm tra:

```python
url = URL(href)

if url.scheme not in ("", "http", "https"):
    return None
```

Ví dụ:

```text
/novel/abc
```

có:

```python
scheme == ""
```

Còn:

```text
https://example.com
```

có:

```python
scheme == "https"
```

và:

```text
mailto:test@example.com
```

có:

```python
scheme == "mailto"
```

---

# 23. Một URL Resolver hoàn chỉnh hơn

```python
from yarl import URL


ALLOWED_SCHEMES = {"", "http", "https"}


def resolve_url(
    base_url: URL,
    href: str | None,
) -> URL | None:

    if not href:
        return None

    href = href.strip()

    if not href:
        return None

    if href.startswith("#"):
        return None

    if href.startswith("javascript:"):
        return None

    relative = URL(href)

    if relative.scheme not in ALLOWED_SCHEMES:
        return None

    return base_url.join(relative)
```

Test:

```python
base = URL("https://example.com/truyen/kiem-hiep/")

tests = [
    "/truyen/abc",
    "chuong-2",
    "../abc",
    "https://other.com/book",
    "",
    "#top",
    "javascript:void(0)",
    "mailto:test@example.com",
]

for href in tests:
    result = resolve_url(base, href)

    print(f"{href!r:30} -> {result}")
```

Đây đã bắt đầu giống một component thực tế trong crawler.

---

# 24. Phân biệt `base_url` và `page_url`

Đây là một khái niệm kiến trúc quan trọng.

Không phải lúc nào cũng dùng:

```python
BASE_URL = URL("https://example.com")
```

để resolve link.

Ví dụ trang:

```text
https://example.com/truyen/kiem-hiep/
```

HTML:

```html
<a href="chuong-2">
```

Ta phải resolve dựa trên:

```text
PAGE URL
```

chứ không phải chỉ:

```text
DOMAIN
```

Tức là:

```python
page_url = URL("https://example.com/truyen/kiem-hiep/")

chapter_url = page_url.join(URL("chuong-2"))
```

---

# 25. Trong kiến trúc crawler của chúng ta

Tư duy nên là:

```text
Fetcher
   │
   │ HTTP GET
   ▼
PageSource
   │
   │
   ▼
Parser
   │
   │ href
   ▼
URL Resolver
   │
   │ URL
   ▼
NovelSummary / Chapter
```

Parser không nên tự làm:

```python
"https://example.com" + href
```

Mà nên có một abstraction rõ ràng:

```python
URL Resolver
```

Ví dụ:

```python
class URLResolver:
    def resolve(
        self,
        base_url: URL,
        href: str,
    ) -> URL:
        return base_url.join(URL(href))
```

Sau này chúng ta có thể mở rộng:

```text
URLResolver
│
├── resolve relative URL
├── normalize
├── validate scheme
├── canonicalize
└── deduplicate
```

Những phần này sẽ xuất hiện ở các buổi sau.

---

# 26. Demo gần với Novel Crawler

Giả sử parser nhận:

```python
page_url = URL("https://example.com/the-loai/kiem-hiep")
```

HTML chứa:

```python
hrefs = [
    "/truyen/abc",
    "/truyen/xyz",
    "truyen/local",
    "https://example.com/truyen/external",
]
```

Code:

```python
from yarl import URL


page_url = URL("https://example.com/the-loai/kiem-hiep")

for href in hrefs:
    url = page_url.join(URL(href))
    print(url)
```

Điểm cần đặc biệt chú ý là:

```text
/truyen/abc
```

và:

```text
truyen/local
```

**không giống nhau**.

`/truyen/abc` bắt đầu từ root domain.

Còn `truyen/local` là relative theo URL hiện tại.

---

# 27. Bài tập thực hành

### Bài 1

Cho:

```python
base = URL("https://example.com")
```

Resolve:

```text
/novel/abc
```

---

### Bài 2

Cho:

```python
base = URL("https://example.com/novel/abc/")
```

Resolve:

```text
chapter-1
```

---

### Bài 3

Cho:

```python
base = URL("https://example.com/novel/abc/")
```

Resolve:

```text
/images/cover.jpg
```

---

### Bài 4

Viết:

```python
def resolve_url(
    base_url: URL,
    href: str,
) -> URL: ...
```

Hỗ trợ:

```text
/novel/abc
chapter-1
../chapter-1
https://other.com/book
```

---

### Bài 5 — thực tế nhất

Giả lập HTML parser:

```python
hrefs = [
    "/truyen/a",
    "/truyen/b",
    "truyen/c",
    "#top",
    "",
    "javascript:void(0)",
    "mailto:test@example.com",
]
```

Viết:

```python
resolve_links(page_url, hrefs)
```

chỉ trả về:

```python
list[URL]
```

các URL hợp lệ để crawler request.

---

# Tổng kết Buổi 6

Ba thứ phải nhớ:

### 1. Absolute URL

```python
URL("https://example.com/novel/abc")
```

### 2. Relative URL

```python
URL("/novel/abc")
```

### 3. Resolve

```python
base_url.join(relative_url)
```

Pattern quan trọng nhất:

```python
page_url = URL("https://example.com/novel/abc/")

href = "chapter-2"

chapter_url = page_url.join(URL(href))
```

Kết quả:

```text
https://example.com/novel/abc/chapter-2
```

Và đây chính là nền tảng để sau này chúng ta xây:

```text
<a href>
    ↓
Parser
    ↓
Relative URL
    ↓
URLResolver
    ↓
Absolute URL
    ↓
Fetcher
```

**Buổi 7** mới đi sâu vào **toán tử `/` để xây URL path**, còn **Buổi 8** sẽ tập trung vào **Path Parameters**.
