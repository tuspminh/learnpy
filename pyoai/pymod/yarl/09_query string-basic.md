# Buổi 9 — Query String cơ bản với `yarl`

Ở Buổi 8 chúng ta đã phân biệt:

```text
PATH
/novel/kiem-hiep

QUERY
?keyword=python&page=2
```

Buổi này tập trung hoàn toàn vào **Query String** — một phần cực kỳ quan trọng khi xây URL cho crawler.

Ví dụ:

```text
https://example.com/search?keyword=python&page=2
```

Trong đó:

```text
https://example.com/search
                    │
                    └── ?keyword=python&page=2
                         ├── keyword = python
                         └── page    = 2
```

---

# 1. Query String là gì?

Query string là phần bắt đầu sau:

```text
?
```

Ví dụ:

```text
https://example.com/search?keyword=python&page=2
```

Query gồm:

```text
keyword=python
page=2
```

Các parameter được nối với nhau bằng:

```text
&
```

Tức:

```text
?keyword=python&page=2
```

---

# 2. Tạo query bằng `with_query()`

Đây là API quan trọng nhất:

```python
with_query()
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search")

url = url.with_query(
    keyword="python",
    page=2,
)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

# 3. `with_query()` không thay đổi URL cũ

`yarl.URL` immutable.

Ví dụ:

```python
from yarl import URL

url1 = URL("https://example.com/search")

url2 = url1.with_query(
    keyword="python"
)

print(url1)
print(url2)
```

Kết quả:

```text
https://example.com/search

https://example.com/search?keyword=python
```

Vì vậy:

```text
url1
 │
 └── with_query()
       │
       ▼
      url2
```

---

# 4. Một parameter

```python
from yarl import URL

url = URL(
    "https://example.com/search"
)

url = url.with_query(
    q="python"
)

print(url)
```

Kết quả:

```text
https://example.com/search?q=python
```

---

# 5. Nhiều parameter

```python
from yarl import URL

url = URL(
    "https://example.com/search"
)

url = url.with_query(
    q="python",
    page=2,
    limit=20,
)

print(url)
```

Kết quả tương đương:

```text
https://example.com/search?q=python&page=2&limit=20
```

---

# 6. Số nguyên tự động được xử lý

Bạn không cần:

```python
page = str(2)
```

Có thể:

```python
url.with_query(
    page=2
)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novels")

url = url.with_query(
    page=3
)

print(url)
```

Kết quả:

```text
https://example.com/novels?page=3
```

Đây là một ưu điểm lớn so với việc tự nối string.

---

# 7. Boolean

Có thể truyền:

```python
url.with_query(
    active=True
)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novels")

url = url.with_query(
    active=True,
)

print(url)
```

Giá trị query được serialize thành dạng chuỗi phù hợp.

Tuy nhiên, khi làm API crawler, **hãy kiểm tra contract của website**.

Có website muốn:

```text
active=true
```

website khác muốn:

```text
active=1
```

`yarl` không quyết định business rule này cho bạn.

---

# 8. Query từ dictionary

Đây là cách rất hữu ích khi parameters được tạo động.

```python
from yarl import URL

params = {
    "keyword": "python",
    "page": 2,
    "limit": 20,
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&limit=20
```

---

# 9. Đây là pattern rất phù hợp với crawler

Ví dụ parser phát hiện:

```python
page = 3
```

Ta có:

```python
params = {
    "page": page,
}
```

Sau đó:

```python
next_url = (
    base_url
    .with_query(params)
)
```

---

# 10. Search URL

Một crawler có thể có:

```text
/search?q=python
```

Code:

```python
from yarl import URL


def build_search_url(
    base_url: URL,
    keyword: str,
) -> URL:

    return (
        base_url
        / "search"
    ).with_query(
        q=keyword
    )


base = URL("https://example.com")

url = build_search_url(
    base,
    "python"
)

print(url)
```

---

# 11. Search + pagination

Đây là trường hợp thực tế hơn:

```python
from yarl import URL


def build_search_url(
    base_url: URL,
    keyword: str,
    page: int = 1,
) -> URL:

    return (
        base_url
        / "search"
    ).with_query(
        q=keyword,
        page=page,
    )


base = URL("https://example.com")

for page in range(1, 4):
    print(
        build_search_url(
            base,
            "python",
            page,
        )
    )
```

Kết quả dạng:

```text
https://example.com/search?q=python&page=1
https://example.com/search?q=python&page=2
https://example.com/search?q=python&page=3
```

---

# 12. Query có Unicode

Đây là điểm rất quan trọng với crawler Việt Nam.

```python
from yarl import URL

url = (
    URL("https://example.com/search")
    .with_query(
        q="truyện tiên hiệp"
    )
)

print(url)
```

`yarl` sẽ xử lý encoding khi serialize URL.

Bạn có thể xem:

```python
print(url.query)
```

và:

```python
print(url.query_string)
```

Query string hiển thị cho con người sẽ khác với representation encoded của URL nếu có ký tự cần escaping.

---

# 13. Query chứa ký tự đặc biệt

Ví dụ:

```python
from yarl import URL

url = (
    URL("https://example.com/search")
    .with_query(
        q="python & asyncio"
    )
)

print(url)
```

Không nên tự:

```python
q.replace(" ", "%20")
```

hoặc:

```python
q.replace("&", "%26")
```

Hãy để `yarl` đảm nhiệm URL encoding.

---

# 14. `query` lấy dữ liệu đã parse

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python&page=2"
)

print(url.query)
```

Sau đó:

```python
print(url.query["q"])
print(url.query["page"])
```

Kết quả:

```text
python
2
```

Lưu ý:

> Query values khi lấy ra thường là string.

Do đó:

```python
page = url.query["page"]
```

cho:

```python
"2"
```

chứ không phải:

```python
2
```

Nếu cần số:

```python
page = int(url.query["page"])
```

---

# 15. `query.get()`

Nếu parameter có thể không tồn tại:

```python
page = url.query.get("page")
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python"
)

page = url.query.get("page")

print(page)
```

Kết quả:

```text
None
```

An toàn hơn:

```python
url.query["page"]
```

vì cách indexing có thể phát sinh `KeyError` nếu key không tồn tại.

---

# 16. `query.get()` với default

```python
page = url.query.get(
    "page",
    "1",
)
```

Nếu URL:

```text
/search?q=python
```

thì:

```text
page = "1"
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python"
)

page = url.query.get(
    "page",
    "1",
)

print(page)
```

---

# 17. Chuyển sang `int`

Đây là pattern thường dùng:

```python
page = int(
    url.query.get("page", "1")
)
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python&page=3"
)

page = int(
    url.query.get("page", "1")
)

print(page)
print(type(page))
```

Kết quả:

```text
3
<class 'int'>
```

---

# 18. Query trong pagination

Giả sử parser nhận:

```text
https://example.com/novels?page=2
```

Ta có:

```python
from yarl import URL

url = URL(
    "https://example.com/novels?page=2"
)

page = int(
    url.query.get("page", "1")
)

print(page)
```

Sau đó có thể:

```python
next_page = page + 1
```

và:

```python
next_url = url.with_query(
    page=next_page
)
```

---

# 19. Cẩn thận: `with_query()` thay query

Đây là điểm cực kỳ quan trọng.

Giả sử:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    q="python",
    page=2,
)
```

URL:

```text
https://example.com/search?q=python&page=2
```

Sau đó:

```python
url2 = url.with_query(
    page=3
)
```

Bạn không nên hiểu điều này là:

```text
giữ q=python
+
đổi page=2 → page=3
```

Mà `with_query()` xây **một query mới**.

Do đó:

```text
url2
```

sẽ chỉ có query được cung cấp cho lần gọi đó.

---

# 20. Nếu muốn thay một parameter

Cách rõ ràng:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    q="python",
    page=2,
)

params = dict(url.query)

params["page"] = "3"

url2 = url.with_query(params)

print(url2)
```

Kết quả:

```text
https://example.com/search?q=python&page=3
```

**Nhưng có một vấn đề:** `dict()` không phù hợp nếu query có duplicate keys.

Ví dụ:

```text
?tag=python&tag=asyncio
```

sẽ được học kỹ ở Buổi 10.

---

# 21. Filter URL

Giả sử website:

```text
/novels?status=completed&page=2
```

Code:

```python
from yarl import URL

url = (
    URL("https://example.com")
    / "novels"
).with_query(
    status="completed",
    page=2,
)

print(url)
```

---

# 22. Sort URL

```python
url = (
    URL("https://example.com")
    / "novels"
).with_query(
    sort="newest",
    page=1,
)
```

Kết quả:

```text
https://example.com/novels?sort=newest&page=1
```

---

# 23. Kết hợp path parameter + query

Đây là mẫu cực kỳ thường gặp:

```python
from yarl import URL

base = URL("https://example.com")

novel_slug = "kiem-hiep"

url = (
    base
    / "novel"
    / novel_slug
).with_query(
    page=2
)

print(url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep?page=2
```

Tư duy:

```text
BASE
 │
 ├── / "novel"
 │
 └── / slug
       │
       ▼
   with_query()
       │
       ▼
     URL
```

---

# 24. Query builder

Khi project lớn hơn, có thể tạo function:

```python
from yarl import URL


def build_listing_url(
    base_url: URL,
    page: int,
    status: str | None = None,
) -> URL:

    params = {
        "page": page,
    }

    if status is not None:
        params["status"] = status

    return (
        base_url
        / "novels"
    ).with_query(params)
```

Test:

```python
base = URL("https://example.com")

print(
    build_listing_url(
        base,
        page=2,
    )
)

print(
    build_listing_url(
        base,
        page=3,
        status="completed",
    )
)
```

---

# 25. Một ví dụ hoàn chỉnh cho crawler

Giả sử website có API/listing:

```text
/novels?page=1
/novels?page=2
/novels?page=3
```

Ta xây:

```python
from yarl import URL


class ListingURLBuilder:

    def __init__(self, base_url: str):
        self.base_url = URL(base_url)

    def build(
        self,
        page: int = 1,
    ) -> URL:

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        return (
            self.base_url
            / "novels"
        ).with_query(
            page=page
        )


builder = ListingURLBuilder(
    "https://example.com"
)


for page in range(1, 4):
    url = builder.build(page)

    print(url)
```

Kết quả:

```text
https://example.com/novels?page=1
https://example.com/novels?page=2
https://example.com/novels?page=3
```

---

# 26. Query và Fetcher

Khi kết hợp với `httpx`, ta thường có:

```python
response = client.get(
    str(url)
)
```

Ví dụ:

```python
from yarl import URL
import httpx


url = (
    URL("https://example.com")
    / "search"
).with_query(
    q="python",
    page=2,
)


with httpx.Client() as client:
    response = client.get(str(url))

print(response.url)
```

Ở đây:

```text
yarl
  ↓
URL construction
  ↓
httpx
  ↓
HTTP request
```

Đây là một kiến trúc rất sạch.

---

# 27. `yarl` không phải HTTP client

Cần phân biệt:

```text
yarl
```

làm:

```text
URL
URL parsing
URL building
URL encoding
```

Còn:

```text
httpx
```

làm:

```text
HTTP GET
HTTP POST
headers
cookies
proxy
timeout
retry...
```

Do đó:

```python
url = URL(...)
```

không request mạng.

Còn:

```python
client.get(str(url))
```

mới thực hiện HTTP request.

---

# 28. Bài tập thực hành

### Bài 1

Tạo:

```text
https://example.com/search?q=python
```

bằng `with_query()`.

---

### Bài 2

Tạo:

```text
https://example.com/search?q=python&page=2&limit=20
```

---

### Bài 3

Tạo URL:

```text
https://example.com/novels?status=completed&page=3
```

bằng dictionary.

---

### Bài 4

Cho:

```python
url = URL(
    "https://example.com/search?q=python&page=5"
)
```

lấy:

```python
q
page
```

sao cho:

```python
q == "python"
page == 5
```

---

### Bài 5 — Crawler

Viết:

```python
def build_listing_url(
    base_url: URL,
    page: int,
    status: str | None = None,
) -> URL:
    ...
```

Sao cho:

```python
build_listing_url(
    URL("https://example.com"),
    2,
)
```

trả về:

```text
https://example.com/novels?page=2
```

và:

```python
build_listing_url(
    URL("https://example.com"),
    3,
    "completed",
)
```

trả về:

```text
https://example.com/novels?page=3&status=completed
```

---

# Tổng kết Buổi 9

API quan trọng nhất:

```python
url.with_query(...)
```

### Một parameter

```python
url.with_query(page=2)
```

### Nhiều parameter

```python
url.with_query(
    page=2,
    limit=20,
)
```

### Dictionary

```python
params = {
    "page": 2,
    "limit": 20,
}

url.with_query(params)
```

### Đọc query

```python
url.query["page"]
```

### An toàn hơn

```python
url.query.get("page")
```

### Query string

```python
url.query_string
```

### Kiến trúc crawler

```text
Path
  ↓
URL / "novels"

Query
  ↓
.with_query(page=2)

       ↓

yarl.URL
       ↓
     httpx
       ↓
     HTTP
```

**Buổi 10 — Query nhiều giá trị** sẽ rất quan trọng vì website thực tế thường có:

```text
?tag=python&tag=asyncio&tag=crawler
```

và chúng ta sẽ học:

```python
url.query.getall("tag")
```

cũng như cách tạo duplicate query parameters bằng `yarl` mà không làm mất dữ liệu.
