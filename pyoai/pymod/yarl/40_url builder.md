# Buổi 40 — Xây dựng `URLBuilder` cho Novel Crawler

Đây là **bài cuối của Phần IV — URL trong Web Crawler**.

Sau 39 bài, chúng ta đã có đủ kiến thức để xây một component thực tế:

```text
URLBuilder
```

Mục tiêu không phải tạo một class khổng lồ, mà là:

> **Tập trung logic xây dựng URL của website vào một nơi, sử dụng `yarl.URL`, dễ test và dễ thay đổi khi website thay đổi.**

---

# 1. Vấn đề thực tế

Trong Novel Crawler, chúng ta có rất nhiều URL:

```text
Trang chủ
    ↓
Listing
    ↓
Novel
    ↓
Chapter
    ↓
Image
```

Ví dụ:

```text
https://site.com/
https://site.com/truyen
https://site.com/truyen?page=2
https://site.com/truyen/python
https://site.com/truyen/python/chuong-1
https://cdn.site.com/images/python.jpg
```

Nếu parser/fetcher tự ghép string:

```python
url = base_url + "/truyen/" + slug
```

sẽ rất nhanh trở thành:

```python
url = (
    base_url
    + "/truyen/"
    + slug
    + "?page="
    + str(page)
)
```

Đây là thứ chúng ta muốn tránh.

---

# 2. Không nên xây URL bằng string

Ví dụ không tốt:

```python
base_url = "https://example.com"

url = (
    base_url
    + "/truyen/"
    + slug
    + "?page="
    + str(page)
)
```

Các vấn đề:

* dễ thiếu `/`
* khó xử lý query
* khó encoding
* khó xử lý Unicode
* dễ tạo URL sai
* khó thay đổi cấu trúc website

Thay vào đó:

```python
from yarl import URL

base_url = URL("https://example.com")

url = (
    base_url
    / "truyen"
    / slug
)
```

---

# 3. `URLBuilder` làm nhiệm vụ gì?

Ta muốn:

```text
URLBuilder
 ├── listing()
 ├── listing_page()
 ├── novel()
 ├── chapter()
 ├── image()
 └── search()
```

Ví dụ:

```python
builder = URLBuilder(
    base_url=URL("https://example.com")
)

builder.listing()
builder.listing_page(2)
builder.novel("python")
builder.chapter("python", "chuong-1")
builder.search("python")
```

---

# 4. Đừng xây một Builder quá generic

Sai lầm:

```python
class URLBuilder:

    def build(
        self,
        scheme=None,
        host=None,
        path=None,
        query=None,
        fragment=None,
        ...
    ):
        ...
```

Class này gần như đang viết lại `yarl.URL`.

Không có lợi ích.

Chúng ta không cần:

```text
GenericURLBuilder
```

mà cần:

```text
NovelSiteURLBuilder
```

vì nó hiểu **URL structure của website truyện**.

---

# 5. Bắt đầu từ `base_url`

```python
from yarl import URL


class URLBuilder:

    def __init__(self, base_url: URL):
        self._base_url = base_url
```

Sử dụng:

```python
builder = URLBuilder(
    URL("https://example.com")
)
```

---

# 6. Method đầu tiên: `home()`

```python
class URLBuilder:

    def __init__(self, base_url: URL):
        self._base_url = base_url

    def home(self) -> URL:
        return self._base_url
```

Test:

```python
builder = URLBuilder(
    URL("https://example.com")
)

print(builder.home())
```

Kết quả:

```text
https://example.com
```

---

# 7. Listing URL

Giả sử website có:

```text
/truyen
```

Ta viết:

```python
def listing(self) -> URL:
    return self._base_url / "truyen"
```

Toàn bộ:

```python
from yarl import URL


class URLBuilder:

    def __init__(self, base_url: URL):
        self._base_url = base_url

    def home(self) -> URL:
        return self._base_url

    def listing(self) -> URL:
        return self._base_url / "truyen"
```

Test:

```python
builder = URLBuilder(
    URL("https://example.com")
)

print(builder.listing())
```

Kết quả:

```text
https://example.com/truyen
```

---

# 8. Pagination

Giả sử website:

```text
/truyen
/truyen?page=2
/truyen?page=3
```

Ta không làm:

```python
return URL(
    f"https://example.com/truyen?page={page}"
)
```

Mà:

```python
def listing_page(self, page: int) -> URL:
    return (
        self._base_url
        / "truyen"
    ).with_query(page=page)
```

Test:

```python
print(builder.listing_page(2))
```

→

```text
https://example.com/truyen?page=2
```

---

# 9. Validate `page`

Không nên cho:

```python
builder.listing_page(-10)
```

hoặc:

```python
builder.listing_page(0)
```

nếu website bắt đầu từ page 1.

```python
def listing_page(self, page: int) -> URL:

    if page < 1:
        raise ValueError(
            "page must be >= 1"
        )

    return (
        self._base_url
        / "truyen"
    ).with_query(page=page)
```

Test:

```python
builder.listing_page(1)
builder.listing_page(2)
```

---

# 10. Novel URL

Giả sử:

```text
/truyen/python
```

Ta viết:

```python
def novel(self, slug: str) -> URL:
    return (
        self._base_url
        / "truyen"
        / slug
    )
```

Test:

```python
print(
    builder.novel("python")
)
```

Kết quả:

```text
https://example.com/truyen/python
```

---

# 11. Không nên tự URL encode slug bằng tay

Không nên:

```python
from urllib.parse import quote

slug = quote(slug)
```

rồi:

```python
URL(...)
```

Yarl đã xử lý URL encoding.

Ta giữ:

```python
slug
```

ở dạng Python string:

```python
return (
    self._base_url
    / "truyen"
    / slug
)
```

---

# 12. Chapter URL

Giả sử:

```text
/truyen/python/chuong-1
```

Ta viết:

```python
def chapter(
    self,
    novel_slug: str,
    chapter_slug: str,
) -> URL:

    return (
        self._base_url
        / "truyen"
        / novel_slug
        / chapter_slug
    )
```

Sử dụng:

```python
url = builder.chapter(
    "python",
    "chuong-1",
)

print(url)
```

Kết quả:

```text
https://example.com/truyen/python/chuong-1
```

---

# 13. Image URL

Image có thể nằm trên CDN:

```text
https://cdn.example.com/images/python.jpg
```

Đây là điểm cần phân biệt:

> `URLBuilder` của site không nhất thiết phải xây mọi image URL.

Nếu HTML đã cung cấp:

```html
<img src="https://cdn.example.com/images/python.jpg">
```

thì parser nên:

```text
src
 ↓
URL(src)
 ↓
resolve
```

không cần:

```python
builder.image(...)
```

---

# 14. Khi nào `image()` hữu ích?

Nếu website có predictable image structure:

```text
/images/{novel_slug}/{chapter}/{page}.jpg
```

thì có thể:

```python
def image(
    self,
    novel_slug: str,
    chapter_slug: str,
    page: int,
) -> URL:

    return (
        self._base_url
        / "images"
        / novel_slug
        / chapter_slug
        / f"{page}.jpg"
    )
```

Nhưng:

> Nếu URL image lấy từ HTML, **không cần xây lại**.

Đây là distinction rất quan trọng giữa:

```text
URL extraction
```

và:

```text
URL construction
```

---

# 15. Search URL

Giả sử:

```text
/search?q=python
```

Ta viết:

```python
def search(self, keyword: str) -> URL:
    return (
        self._base_url
        / "search"
    ).with_query(q=keyword)
```

Test:

```python
print(
    builder.search("python")
)
```

Kết quả:

```text
https://example.com/search?q=python
```

---

# 16. Search + page

Website có:

```text
/search?q=python&page=2
```

Ta có thể:

```python
def search(
    self,
    keyword: str,
    page: int = 1,
) -> URL:

    if page < 1:
        raise ValueError(
            "page must be >= 1"
        )

    return (
        self._base_url
        / "search"
    ).with_query(
        q=keyword,
        page=page,
    )
```

---

# 17. Search nhiều filter

Giả sử:

```text
/search?q=python&author=alice&page=2
```

Ta có:

```python
def search(
    self,
    keyword: str,
    author: str | None = None,
    page: int = 1,
) -> URL:

    if page < 1:
        raise ValueError(
            "page must be >= 1"
        )

    params = {
        "q": keyword,
        "page": page,
    }

    if author:
        params["author"] = author

    return (
        self._base_url
        / "search"
    ).with_query(params)
```

Yarl lo phần encoding query.

---

# 18. Builder hoàn chỉnh phiên bản đầu

```python
from yarl import URL


class URLBuilder:

    def __init__(self, base_url: URL):
        self._base_url = base_url

    def home(self) -> URL:
        return self._base_url

    def listing(self) -> URL:
        return (
            self._base_url
            / "truyen"
        )

    def listing_page(self, page: int) -> URL:

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        return (
            self._base_url
            / "truyen"
        ).with_query(
            page=page
        )

    def novel(self, slug: str) -> URL:
        return (
            self._base_url
            / "truyen"
            / slug
        )

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:

        return (
            self._base_url
            / "truyen"
            / novel_slug
            / chapter_slug
        )

    def search(
        self,
        keyword: str,
        page: int = 1,
    ) -> URL:

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        return (
            self._base_url
            / "search"
        ).with_query(
            q=keyword,
            page=page,
        )
```

---

# 19. Test toàn bộ Builder

```python
from yarl import URL


builder = URLBuilder(
    URL("https://example.com")
)

print("HOME:")
print(builder.home())

print()

print("LISTING:")
print(builder.listing())

print()

print("LISTING PAGE:")
print(builder.listing_page(2))

print()

print("NOVEL:")
print(builder.novel("python"))

print()

print("CHAPTER:")
print(
    builder.chapter(
        "python",
        "chuong-1",
    )
)

print()

print("SEARCH:")
print(
    builder.search(
        "python",
        page=3,
    )
)
```

Kết quả:

```text
HOME:
https://example.com

LISTING:
https://example.com/truyen

LISTING PAGE:
https://example.com/truyen?page=2

NOVEL:
https://example.com/truyen/python

CHAPTER:
https://example.com/truyen/python/chuong-1

SEARCH:
https://example.com/search?q=python&page=3
```

---

# 20. Builder không fetch

Đây là nguyên tắc kiến trúc cực kỳ quan trọng.

Không làm:

```python
class URLBuilder:

    def build_novel(...):
        ...
        response = httpx.get(url)
        ...
```

`URLBuilder` chỉ:

```text
input
 ↓
URL
```

Nó không biết:

```text
HTTP
Proxy
Retry
Timeout
Parser
Database
Queue
```

---

# 21. Builder không parse HTML

Cũng không làm:

```python
class URLBuilder:

    def build_from_html(...):
        ...
```

Parser chịu trách nhiệm:

```text
HTML
 ↓
extract href
 ↓
URL
```

Builder chịu trách nhiệm:

```text
domain data
 ↓
URL
```

Hai hướng hoàn toàn khác nhau.

---

# 22. Builder và Parser

Đây là distinction rất quan trọng:

### Builder

```text
Novel data
     ↓
URL
```

Ví dụ:

```python
builder.chapter(
    "python",
    "chuong-1",
)
```

---

### Parser

```text
HTML
     ↓
href
     ↓
URL
```

Ví dụ:

```python
page_url.join(
    URL(href)
)
```

Do đó:

```text
Builder
→ construct URL
```

còn:

```text
Parser
→ extract URL
```

---

# 23. Builder và Fetcher

Fetcher:

```python
url = builder.chapter(
    "python",
    "chuong-1",
)

response = client.get(
    str(url)
)
```

Fetcher không cần biết URL được xây thế nào.

Nó chỉ nhận:

```python
URL
```

Đây là separation rất đẹp:

```text
URLBuilder
     ↓
    URL
     ↓
Fetcher
     ↓
Response
     ↓
Parser
```

---

# 24. Builder và Domain Model

Trong architecture của bạn, ta có thể có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Novel:
    slug: str
    title: str
```

Builder:

```python
class URLBuilder:

    def novel(self, novel: Novel) -> URL:
        return (
            self._base_url
            / "truyen"
            / novel.slug
        )
```

Nhưng có một câu hỏi:

> Có nên để Builder phụ thuộc trực tiếp vào Domain Entity?

Không nhất thiết.

Phiên bản:

```python
builder.novel(novel.slug)
```

thường đơn giản hơn.

---

# 25. Tại sao `URLBuilder` phù hợp với Plugin Architecture?

Đây là chỗ component này trở nên rất hữu ích.

Bạn có:

```text
plugins/
├── site_a/
│   ├── parser/
│   ├── config.py
│   └── url_builder.py
│
├── site_b/
│   ├── parser/
│   ├── config.py
│   └── url_builder.py
│
└── site_c/
    ├── parser/
    ├── config.py
    └── url_builder.py
```

Mỗi website có URL structure khác nhau.

---

# 26. Site A

```python
class SiteAURLBuilder:

    def novel(self, slug: str) -> URL:
        return (
            self._base_url
            / "truyen"
            / slug
        )
```

Site B:

```python
class SiteBURLBuilder:

    def novel(self, slug: str) -> URL:
        return (
            self._base_url
            / "story"
            / slug
        )
```

Site C:

```python
class SiteCURLBuilder:

    def novel(self, slug: str) -> URL:
        return (
            self._base_url
            / "novel"
            / slug
        )
```

Crawler core không cần biết chi tiết.

---

# 27. Interface cho Builder

Khi có nhiều plugin, chúng ta có thể định nghĩa:

```python
from abc import ABC, abstractmethod
from yarl import URL


class NovelURLBuilder(ABC):

    @abstractmethod
    def listing(self) -> URL:
        ...

    @abstractmethod
    def novel(self, slug: str) -> URL:
        ...

    @abstractmethod
    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:
        ...
```

Site implementation:

```python
class SiteAURLBuilder(NovelURLBuilder):

    def __init__(self, base_url: URL):
        self._base_url = base_url

    def listing(self) -> URL:
        return self._base_url / "truyen"

    def novel(self, slug: str) -> URL:
        return (
            self._base_url
            / "truyen"
            / slug
        )

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:

        return (
            self._base_url
            / "truyen"
            / novel_slug
            / chapter_slug
        )
```

---

# 28. Nhưng đừng tạo interface quá sớm

Nếu chỉ có:

```text
1 website
```

thì:

```python
class URLBuilder:
```

là đủ.

Nếu có:

```text
Site A
Site B
Site C
```

và chúng thực sự có variation:

```text
/truyen/
/story/
/novel/
```

thì abstraction:

```python
NovelURLBuilder
```

mới bắt đầu có giá trị.

Đây là áp dụng đúng tinh thần SOLID:

> **Abstraction should follow variation.**

Không phải:

> "DDD/SOLID thì cái gì cũng phải interface."

---

# 29. Builder với cấu hình

Một cách rất phù hợp với plugin architecture:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class URLConfig:
    listing_path: str
    search_path: str
    novel_path: str
```

Ví dụ:

```python
config = URLConfig(
    listing_path="truyen",
    search_path="search",
    novel_path="truyen",
)
```

Builder:

```python
class URLBuilder:

    def __init__(
        self,
        base_url: URL,
        config: URLConfig,
    ):
        self._base_url = base_url
        self._config = config

    def listing(self) -> URL:
        return (
            self._base_url
            / self._config.listing_path
        )

    def search(
        self,
        keyword: str,
        page: int = 1,
    ) -> URL:

        return (
            self._base_url
            / self._config.search_path
        ).with_query(
            q=keyword,
            page=page,
        )
```

---

# 30. Nhưng cấu hình không nên chứa mọi thứ

Không nên biến:

```python
URLConfig
```

thành:

```python
@dataclass
class URLConfig:
    scheme: str
    host: str
    port: int
    listing: str
    search: str
    novel: str
    chapter: str
    image: str
    page_param: str
    search_param: str
    ...
```

rồi cuối cùng thành một mini framework.

Hãy chỉ đưa những phần **thực sự thay đổi theo site** vào config.

---

# 31. URLBuilder + Value Object

Ở phần Architecture sau này, chúng ta có thể tạo:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class NovelURL:
    value: URL
```

Nhưng chưa cần ngay.

Hiện tại:

```python
yarl.URL
```

đã là một Value Object rất tốt cho URL.

---

# 32. Builder + URL normalization

Một câu hỏi:

> Builder có normalize URL không?

Tôi khuyên:

**Không nhất thiết.**

Builder:

```text
domain data
 ↓
construct
 ↓
URL
```

Normalizer:

```text
URL
 ↓
normalize
 ↓
normalized URL
```

Ví dụ:

```python
url = builder.chapter(
    "python",
    "chuong-1",
)

normalized = normalize_url(url)
```

Tách riêng giúp Builder không bị phụ thuộc vào crawler policy.

---

# 33. Builder + URL validation

Tương tự:

```text
Builder
    ↓
URL
    ↓
URL Policy
```

Không nên để Builder quyết định:

```text
Có được crawl URL này không?
```

Ví dụ:

```python
url = builder.novel("python")

if policy.is_allowed(url):
    queue.put(url)
```

---

# 34. Builder + Deduplicator

Không nên:

```python
builder.novel(...)
```

tự động deduplicate.

Thay vào đó:

```python
url = builder.novel("python")

if deduplicator.add(url):
    queue.put(url)
```

Architecture rất rõ:

```text
Builder
   ↓
URL
   ↓
Normalizer
   ↓
Deduplicator
   ↓
Queue
```

---

# 35. Một `URLBuilder` thực tế cho Novel Crawler

Phiên bản tôi khuyên bạn sử dụng ở giai đoạn hiện tại:

```python
from yarl import URL


class URLBuilder:

    def __init__(self, base_url: URL):
        self._base_url = base_url

    def home(self) -> URL:
        return self._base_url

    def listing(self) -> URL:
        return (
            self._base_url
            / "truyen"
        )

    def listing_page(
        self,
        page: int,
    ) -> URL:

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        return (
            self._base_url
            / "truyen"
        ).with_query(
            page=page
        )

    def novel(
        self,
        slug: str,
    ) -> URL:

        return (
            self._base_url
            / "truyen"
            / slug
        )

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:

        return (
            self._base_url
            / "truyen"
            / novel_slug
            / chapter_slug
        )

    def search(
        self,
        keyword: str,
        page: int = 1,
    ) -> URL:

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        return (
            self._base_url
            / "search"
        ).with_query(
            q=keyword,
            page=page,
        )
```

Đây là mức abstraction **vừa đủ**.

---

# 36. Test bằng `pytest`

```python
from yarl import URL


def test_listing():
    builder = URLBuilder(
        URL("https://example.com")
    )

    assert builder.listing() == URL(
        "https://example.com/truyen"
    )


def test_listing_page():
    builder = URLBuilder(
        URL("https://example.com")
    )

    assert builder.listing_page(2) == URL(
        "https://example.com/truyen?page=2"
    )


def test_novel():
    builder = URLBuilder(
        URL("https://example.com")
    )

    assert builder.novel("python") == URL(
        "https://example.com/truyen/python"
    )


def test_chapter():
    builder = URLBuilder(
        URL("https://example.com")
    )

    assert builder.chapter(
        "python",
        "chuong-1",
    ) == URL(
        "https://example.com/"
        "truyen/python/chuong-1"
    )


def test_search():
    builder = URLBuilder(
        URL("https://example.com")
    )

    assert builder.search(
        "python",
        page=2,
    ) == URL(
        "https://example.com/search"
        "?q=python&page=2"
    )


def test_invalid_page():
    builder = URLBuilder(
        URL("https://example.com")
    )

    try:
        builder.listing_page(0)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )
```

---

# 37. Một vấn đề thú vị: page = 1

Website có thể dùng:

```text
/truyen
```

cho page 1 và:

```text
/truyen?page=2
```

cho page 2.

Khi đó Builder tốt hơn nên:

```python
def listing_page(
    self,
    page: int,
) -> URL:

    if page < 1:
        raise ValueError(
            "page must be >= 1"
        )

    url = (
        self._base_url
        / "truyen"
    )

    if page == 1:
        return url

    return url.with_query(
        page=page
    )
```

Kết quả:

```text
page=1
→ https://example.com/truyen

page=2
→ https://example.com/truyen?page=2
```

Đây là một ví dụ cho thấy:

> URLBuilder chứa **website URL construction rules**, không chỉ nối path.

---

# 38. Pagination kiểu `/trang-2`

Không phải website nào cũng dùng:

```text
?page=2
```

Có website:

```text
/truyen
/truyen/trang-2
/truyen/trang-3
```

Builder:

```python
def listing_page(
    self,
    page: int,
) -> URL:

    if page < 1:
        raise ValueError(
            "page must be >= 1"
        )

    url = (
        self._base_url
        / "truyen"
    )

    if page == 1:
        return url

    return (
        url
        / f"trang-{page}"
    )
```

Như vậy Parser/Fetcher không cần biết pagination representation.

---

# 39. Đây chính là giá trị của URLBuilder

Khi website thay đổi:

```text
/truyen?page=2
```

thành:

```text
/truyen/trang-2
```

ta chỉ sửa:

```python
URLBuilder.listing_page()
```

Không cần sửa:

```text
Fetcher
Queue
Worker
Repository
Use Case
Database
```

Đây là một abstraction có giá trị thực tế.

---

# 40. URLBuilder trong Clean Architecture

Với kiến trúc Novel Crawler của bạn:

```text
                    CLI
                     │
                     ▼
                  UseCase
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
         URLBuilder      Parser
              │             │
              ▼             ▼
            yarl.URL      yarl.URL
              │             │
              └──────┬──────┘
                     ▼
                 URL Policy
                     │
                     ▼
                   Queue
                     │
                     ▼
                  Fetcher
```

`URLBuilder` là một component thuộc phần **site/plugin infrastructure**, không phải domain entity.

---

# 41. Tổng kết toàn bộ Phần IV

Chúng ta bắt đầu từ:

```text
31. Relative URL → Absolute URL
```

để giải quyết:

```text
../chapter-10
```

→

```text
https://site.com/novel/chapter-10
```

---

```text
32. <a href> → URL
```

để extract link từ HTML.

---

```text
33. Pagination
```

để tìm:

```text
next page
```

---

```text
34. Chapter URL
```

để extract chapter links.

---

```text
35. Image URL
```

để xử lý:

```text
<img src="">
```

---

```text
36. URL Normalization
```

để chuẩn hóa identity:

```text
#fragment
```

---

```text
37. URL Comparison
```

để xác định:

```text
A == B ?
```

---

```text
38. URL Deduplication
```

để:

```text
URL → seen set → queue
```

---

```text
39. Canonical URL
```

để hiểu:

```html
<link rel="canonical">
```

---

và cuối cùng:

```text
40. URLBuilder
```

để tập trung URL construction:

```text
Novel
Chapter
Listing
Pagination
Search
Image
```

---

# 42. Kiến trúc URL hoàn chỉnh

Sau Phần IV, component URL của Novel Crawler có thể hình dung như sau:

```text
                       ┌─────────────────┐
                       │   URLBuilder    │
                       └────────┬────────┘
                                │
                       construct URL
                                │
                                ▼
                             yarl.URL
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
        Resolver            Normalizer          Canonical
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                                ▼
                           URL Policy
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

Đây là một foundation rất tốt để chuyển sang phần tiếp theo.

---

# Phần V — `yarl` + Architecture

Tiếp theo chúng ta sẽ không học thêm các API rời rạc của `yarl`, mà đưa `yarl.URL` vào chính **Novel Crawler Architecture**:

```text
41. yarl trong Fetcher
42. yarl trong Parser
43. yarl + httpx
44. yarl + aiohttp
45. Value Object NovelURL
46. URL validation
47. URL policy
48. URL Resolver
49. URL Factory
50. Mini Project — Novel URL Manager
```

Đặc biệt từ **Buổi 41**, chúng ta sẽ nối trực tiếp:

```text
yarl.URL
   ↓
httpx
   ↓
Fetcher
```

để thấy rõ URL nên đi xuyên qua **Fetcher → Parser → Queue → Repository** như thế nào trong kiến trúc Novel Crawler của bạn.
