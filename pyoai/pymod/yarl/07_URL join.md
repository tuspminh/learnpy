# Buổi 7 — Join URL với `/` trong `yarl`

Ở buổi này chúng ta tập trung vào một trong những tính năng **quan trọng nhất của `yarl` khi làm crawler**:

> Dùng toán tử `/` để xây dựng URL một cách an toàn, thay vì nối chuỗi bằng `+`.

Đây là phần rất quan trọng trước khi sang xử lý **relative URL → absolute URL** trong crawler.

---

# 1. Vì sao nối URL bằng string dễ lỗi?

Ví dụ:

```python
base = "https://example.com"
path = "/novel/truyen-a"

url = base + path

print(url)
```

Kết quả:

```text
https://example.com/novel/truyen-a
```

Có vẻ ổn.

Nhưng:

```python
base = "https://example.com/"
path = "/novel/truyen-a"

url = base + path

print(url)
```

Kết quả:

```text
https://example.com//novel/truyen-a
```

Hoặc:

```python
base = "https://example.com"
path = "novel/truyen-a"

url = base + path
```

Kết quả:

```text
https://example.comnovel/truyen-a
```

Với crawler, những lỗi kiểu này rất dễ xuất hiện.

---

# 2. `yarl` giải quyết bằng `/`

```python
from yarl import URL

base = URL("https://example.com")

url = base / "novel" / "truyen-a"

print(url)
```

Kết quả:

```text
https://example.com/novel/truyen-a
```

Ta có:

```text
base
  │
  ▼
https://example.com
       │
       │ / "novel"
       ▼
https://example.com/novel
       │
       │ / "truyen-a"
       ▼
https://example.com/novel/truyen-a
```

Đây là cách rất tự nhiên để xây URL.

---

# 3. Chia nhỏ từng bước

```python
from yarl import URL

url = URL("https://example.com")

print(url)

url = url / "novel"
print(url)

url = url / "truyen-a"
print(url)

url = url / "chapter-1"
print(url)
```

Kết quả:

```text
https://example.com
https://example.com/novel
https://example.com/novel/truyen-a
https://example.com/novel/truyen-a/chapter-1
```

Điểm quan trọng:

**`URL` là immutable.**

Mỗi lần `/` tạo ra một URL mới.

---

# 4. Có thể chain nhiều `/`

Thay vì:

```python
url = URL("https://example.com")

url = url / "novel"
url = url / "truyen-a"
url = url / "chapter"
url = url / "1"
```

Có thể viết:

```python
from yarl import URL

url = (
    URL("https://example.com")
    / "novel"
    / "truyen-a"
    / "chapter"
    / "1"
)

print(url)
```

Kết quả:

```text
https://example.com/novel/truyen-a/chapter/1
```

Đây là style rất phù hợp khi xây URL trong crawler.

---

# 5. `/` không phải phép nối string

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com")

url = base / "hello world"

print(url)
```

`yarl` sẽ xử lý việc encoding URL thay vì đơn giản ghép chuỗi.

Điều này đặc biệt quan trọng khi segment chứa Unicode hoặc ký tự đặc biệt.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com") / "truyện-tiên-hiệp"

print(url)
```

URL được serialize thành dạng URL-encoded phù hợp.

Nhưng:

```python
print(url.path)
```

cho phép ta làm việc với path ở dạng dễ đọc.

---

# 6. `/` với nhiều segment

Ví dụ app crawler có cấu trúc:

```text
https://example.com
    /novel
        /kiem-hiep
            /chuong-1
```

Ta viết:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

chapter_url = (
    BASE_URL
    / "novel"
    / "kiem-hiep"
    / "chuong-1"
)

print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep/chuong-1
```

---

# 7. `/` với biến

Đây mới là trường hợp crawler sử dụng rất nhiều.

```python
from yarl import URL

base_url = URL("https://example.com")

novel_slug = "kiem-hiep"
chapter_slug = "chuong-123"

url = (
    base_url
    / "novel"
    / novel_slug
    / chapter_slug
)

print(url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep/chuong-123
```

---

# 8. Xây URL từ object Novel

Giả sử:

```python
class Novel:
    def __init__(self, slug: str):
        self.slug = slug
```

Ta có:

```python
from yarl import URL


BASE_URL = URL("https://example.com")


novel = Novel("kiem-hiep")

novel_url = BASE_URL / "novel" / novel.slug

print(novel_url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep
```

---

# 9. Xây chapter URL

Ví dụ:

```python
from yarl import URL


BASE_URL = URL("https://example.com")

novel_slug = "kiem-hiep"
chapter_slug = "chuong-100"

chapter_url = (
    BASE_URL
    / "novel"
    / novel_slug
    / chapter_slug
)

print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep/chuong-100
```

Đây chính là kiểu logic chúng ta sẽ dùng trong Novel Crawler.

---

# 10. `/` với path bắt đầu bằng `/`

Một điểm **cực kỳ quan trọng**.

Bạn có thể nghĩ:

```python
base = URL("https://example.com/novel")

url = base / "/chapter/1"
```

sẽ thành:

```text
https://example.com/novel/chapter/1
```

Nhưng không nên suy nghĩ về `/` như phép nối string.

Hãy test trực tiếp:

```python
from yarl import URL

base = URL("https://example.com/novel")

print(base / "chapter" / "1")
print(base / "/chapter/1")
```

Segment có `/` bên trong được `yarl` xử lý như một **path segment/path value**, không đơn giản là quy tắc `base + string`.

Vì vậy, khi xây URL từng phần, tốt nhất:

```python
base / "chapter" / "1"
```

thay vì:

```python
base / "/chapter/1"
```

---

# 11. Đừng đưa cả URL vào `/`

`/` phù hợp để thêm **path segment**.

Ví dụ đúng:

```python
url = URL("https://example.com") / "novel" / "abc"
```

Không nên làm:

```python
url = URL("https://example.com") / "https://google.com"
```

Nếu mục đích của bạn là chuyển sang một URL khác, hãy tạo:

```python
url = URL("https://google.com")
```

---

# 12. `/` và query string

`/` chủ yếu thao tác với **path**.

Ví dụ:

```python
from yarl import URL

url = (
    URL("https://example.com")
    / "search"
)

url = url.with_query(
    keyword="python",
    page=2,
)

print(url)
```

Ta có:

```text
https://example.com/search?keyword=python&page=2
```

Đây là cách rất sạch:

```text
URL()
  ↓
/
path
  ↓
with_query()
query
```

---

# 13. Mẫu rất hay dùng trong crawler

```python
from yarl import URL


BASE_URL = URL("https://example.com")


def build_search_url(keyword: str, page: int) -> URL:
    return (
        BASE_URL
        / "search"
    ).with_query(
        keyword=keyword,
        page=page,
    )


url = build_search_url("python", 2)

print(url)
```

Ví dụ kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

# 14. Pagination

Đây là trường hợp rất sát với crawler của chúng ta.

Giả sử:

```text
https://example.com/novels
https://example.com/novels?page=2
https://example.com/novels?page=3
```

Ta có:

```python
from yarl import URL


BASE_URL = URL("https://example.com")


def build_listing_url(page: int) -> URL:
    url = BASE_URL / "novels"

    if page > 1:
        url = url.with_query(page=page)

    return url


for page in range(1, 4):
    print(build_listing_url(page))
```

Kết quả:

```text
https://example.com/novels
https://example.com/novels?page=2
https://example.com/novels?page=3
```

---

# 15. Xây URL bằng `joinpath()`

Ở buổi trước chúng ta đã gặp:

```python
url.joinpath("novel", "abc", "chapter-1")
```

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com")

url = base.joinpath(
    "novel",
    "abc",
    "chapter-1",
)

print(url)
```

Kết quả:

```text
https://example.com/novel/abc/chapter-1
```

So sánh:

```python
url1 = (
    base
    / "novel"
    / "abc"
    / "chapter-1"
)
```

và:

```python
url2 = base.joinpath(
    "novel",
    "abc",
    "chapter-1",
)
```

Cả hai đều thích hợp.

---

# 16. Khi nào dùng `/`?

Trong code crawler, tôi khuyên ưu tiên:

```python
base / "novel" / slug
```

khi URL được xây từng tầng.

Ví dụ:

```python
novel_url = BASE_URL / "novel" / novel_slug

chapter_url = (
    novel_url
    / "chapter"
    / str(chapter_no)
)
```

Rất dễ đọc.

---

# 17. Một ví dụ hoàn chỉnh

Hãy tạo một mini URL builder:

```python
from yarl import URL


class NovelURLBuilder:
    def __init__(self, base_url: str):
        self.base_url = URL(base_url)

    def novel(self, slug: str) -> URL:
        return (
            self.base_url
            / "novel"
            / slug
        )

    def chapter(
        self,
        novel_slug: str,
        chapter_no: int,
    ) -> URL:
        return (
            self.base_url
            / "novel"
            / novel_slug
            / "chapter"
            / str(chapter_no)
        )

    def listing(self, page: int = 1) -> URL:
        url = self.base_url / "novels"

        if page > 1:
            url = url.with_query(page=page)

        return url


builder = NovelURLBuilder(
    "https://example.com"
)


print(
    builder.novel("kiem-hiep")
)

print(
    builder.chapter(
        "kiem-hiep",
        100,
    )
)

print(
    builder.listing(1)
)

print(
    builder.listing(3)
)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep
https://example.com/novel/kiem-hiep/chapter/100
https://example.com/novels
https://example.com/novels?page=3
```

---

# 18. Kiến trúc tư duy

Khi xây URL, chúng ta nên phân biệt rõ:

```text
URL
│
├── scheme
├── host
├── path
│    ├── segment
│    ├── segment
│    └── segment
│
├── query
│
└── fragment
```

`/` chủ yếu giúp chúng ta xây:

```text
path
```

Còn:

```python
with_query(...)
```

xây:

```text
query
```

Ví dụ:

```python
url = (
    URL("https://example.com")
    / "novel"
    / "kiem-hiep"
    / "chapter"
    / "100"
).with_query(
    lang="vi",
    format="html",
)
```

Tư duy rất rõ:

```text
https://example.com
        │
        └── path
             │
             ├── novel
             ├── kiem-hiep
             ├── chapter
             └── 100

        └── query
             ├── lang=vi
             └── format=html
```

---

# 19. Một lỗi kiến trúc nên tránh

Không nên có code kiểu:

```python
url = (
    "https://example.com/"
    + "/novel/"
    + novel_slug
    + "?page="
    + str(page)
)
```

Code này trộn lẫn:

```text
scheme
host
path
query
encoding
```

vào một chuỗi.

Thay vào đó:

```python
url = (
    URL("https://example.com")
    / "novel"
    / novel_slug
).with_query(
    page=page
)
```

Mỗi thành phần có trách nhiệm riêng.

Đây chính là tư duy rất phù hợp với **DDD / Clean Architecture**:

```text
Domain
   │
   │ tạo dữ liệu
   ▼
URL Builder
   │
   ├── path → /
   │
   └── query → with_query()
   │
   ▼
yarl.URL
   │
   ▼
Fetcher
```

---

# 20. Bài tập thực hành

## Bài 1

Tạo:

```python
BASE_URL = URL("https://example.com")
```

Xây:

```text
https://example.com/novels
```

---

## Bài 2

Xây:

```text
https://example.com/novels/kiem-hiep
```

từ:

```python
category = "kiem-hiep"
```

---

## Bài 3

Xây:

```text
https://example.com/novel/kiem-hiep/chapter/100
```

từ:

```python
novel_slug = "kiem-hiep"
chapter_no = 100
```

---

## Bài 4

Xây:

```text
https://example.com/search?keyword=python&page=2
```

bằng:

```python
URL()
/
with_query()
```

---

## Bài 5 — Mini crawler

Viết:

```python
class URLBuilder:
    ...
```

có 3 method:

```python
listing(page)
novel(slug)
chapter(slug, chapter_no)
```

sao cho:

```python
builder.listing(2)
builder.novel("kiem-hiep")
builder.chapter("kiem-hiep", 100)
```

trả về `yarl.URL`.

---

# Tóm tắt Buổi 7

Điểm cần nhớ:

```python
from yarl import URL
```

### Xây path

```python
url / "novel" / "abc" / "chapter"
```

### Xây query

```python
url.with_query(page=2)
```

### Kết hợp

```python
url = (
    URL("https://example.com")
    / "novel"
    / "abc"
).with_query(
    page=2
)
```

### Tư duy

```text
/             → PATH
with_query()  → QUERY
with_fragment() → FRAGMENT
```

Với Novel Crawler, `/` sẽ được sử dụng cực nhiều để xây **novel URL, chapter URL, image URL, pagination URL**.

**Buổi 8 tiếp theo:** **Path Parameters** — xử lý các segment động, slug, ID, chapter number và các trường hợp path có tham số trong crawler.
