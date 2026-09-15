# Buổi 15 — `with_query()`

Hôm nay chúng ta học một phương thức cực kỳ quan trọng của `yarl`:

```python
url.with_query(...)
```

Đây là phương thức dùng để **thay thế query string của URL**.

Vì bạn đang xây Novel Crawler, `with_query()` đặc biệt quan trọng cho:

* `page`
* `keyword`
* `sort`
* `status`
* `category`
* filter
* search
* pagination
* API query parameters

---

# 1. Query string là gì?

Ví dụ:

```text
https://example.com/search?q=python&page=2&sort=new
                         ^^^^^^^^^^^^^^^^^^^^^^^^^
                              query string
```

Trong `yarl`:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2&sort=new")

print(url.query)
print(url.query_string)
```

`query` là một cấu trúc query có thể truy cập theo key.

`query_string` là chuỗi query:

```text
q=python&page=2&sort=new
```

---

# 2. `with_query()` cơ bản

Cú pháp:

```python
new_url = url.with_query(...)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search?q=python")

new_url = url.with_query({"q": "asyncio"})

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/search?q=python
https://example.com/search?q=asyncio
```

URL cũ không thay đổi.

---

# 3. `with_query()` thay toàn bộ query

Đây là điều **quan trọng nhất** cần nhớ.

Cho:

```python
url = URL("https://example.com/search?q=python&page=2&sort=new")
```

Nếu:

```python
new_url = url.with_query({"q": "asyncio"})
```

thì kết quả là:

```text
https://example.com/search?q=asyncio
```

Không phải:

```text
https://example.com/search?q=asyncio&page=2&sort=new
```

Các query cũ:

```text
page=2
sort=new
```

đã bị thay thế.

---

# 4. Đây là điểm rất dễ nhầm

Nhiều người nghĩ:

```python
url.with_query({"page": 3})
```

có nghĩa:

> sửa `page` thành 3, giữ mọi thứ khác.

**Không phải.**

Nó có nghĩa gần hơn với:

> tạo URL mới với query mới là `page=3`.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2&sort=new")

new_url = url.with_query({"page": 3})

print(new_url)
```

Kết quả:

```text
https://example.com/search?page=3
```

---

# 5. `with_query()` với dictionary

Đây là cách phổ biến:

```python
from yarl import URL

url = URL("https://example.com/search")

new_url = url.with_query(
    {
        "q": "python",
        "page": 2,
        "sort": "new",
    }
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?q=python&page=2&sort=new
```

`yarl` sẽ xử lý việc chuyển giá trị thành query parameter.

---

# 6. Giá trị số

Ví dụ:

```python
url = URL("https://example.com/novels")

url = url.with_query(
    {
        "page": 5,
        "limit": 20,
    }
)

print(url)
```

Kết quả:

```text
https://example.com/novels?page=5&limit=20
```

Nhưng khi đọc lại:

```python
print(url.query["page"])
```

giá trị query được biểu diễn dưới dạng text:

```text
5
```

Nếu application cần số:

```python
page = int(url.query["page"])
```

---

# 7. `with_query()` với keyword arguments

Có thể viết:

```python
url = url.with_query(
    q="python",
    page=2,
    sort="new",
)
```

Ví dụ đầy đủ:

```python
from yarl import URL

url = URL("https://example.com/search")

url = url.with_query(
    q="python",
    page=2,
    sort="new",
)

print(url)
```

Kết quả:

```text
https://example.com/search?q=python&page=2&sort=new
```

Đây là syntax khá đẹp khi query đơn giản.

---

# 8. Dictionary phù hợp khi query động

Trong crawler, thường query được tạo từ object:

```python
params = {
    "q": "python",
    "page": 2,
    "sort": "new",
}
```

Sau đó:

```python
url = URL("https://example.com/search").with_query(params)
```

Điều này rất phù hợp khi:

```text
SearchCriteria
      ↓
dict
      ↓
with_query()
      ↓
Search URL
```

---

# 9. Ví dụ Novel Search

Ta xây một class:

```python
from yarl import URL


class NovelSearchURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def build(
        self,
        keyword: str,
        page: int = 1,
    ) -> URL:

        return self._base_url.with_query(
            {
                "q": keyword,
                "page": page,
            }
        )
```

Sử dụng:

```python
builder = NovelSearchURLBuilder(URL("https://example.com/search"))

url = builder.build(
    keyword="python",
    page=2,
)

print(url)
```

Kết quả:

```text
https://example.com/search?q=python&page=2
```

---

# 10. Query có Unicode

Ví dụ tìm truyện:

```python
from yarl import URL

url = URL("https://example.com/search").with_query(
    {
        "q": "tiên hiệp",
        "page": 2,
    }
)

print(url)
```

`yarl` xử lý việc encoding URL.

Bạn không cần tự làm:

```python
quote(...)
```

rồi ghép string thủ công.

---

# 11. Query chứa ký tự đặc biệt

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query(
    {
        "q": "python & asyncio",
    }
)

print(url)
```

Yarl chịu trách nhiệm encode giá trị query phù hợp với URL.

Đây là một ưu điểm lớn so với:

```python
url = "https://example.com/search?q=" + keyword
```

Nếu `keyword` chứa:

```text
&
?
=
space
Unicode
```

thì string concatenation rất dễ tạo URL sai.

---

# 12. `with_query()` + `query`

Ta có thể tạo:

```python
from yarl import URL

url = URL("https://example.com/search").with_query(
    {
        "q": "python",
        "page": 2,
    }
)

print(url.query["q"])
print(url.query["page"])
```

Khi cần số:

```python
page = int(url.query["page"])
```

---

# 13. `with_query()` không phải append query

Ví dụ:

```python
url = URL("https://example.com/search?q=python")

url2 = url.with_query({"page": 2})
```

Kết quả:

```text
https://example.com/search?page=2
```

Không phải:

```text
https://example.com/search?q=python&page=2
```

Muốn **giữ query cũ và thay/thêm một parameter**, chúng ta phải tạo query mới dựa trên query hiện tại.

---

# 14. Cập nhật `page` nhưng giữ các query khác

Đây là pattern cực kỳ quan trọng cho crawler.

Giả sử:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2&sort=new")
```

Ta muốn:

```text
q=python
page=3
sort=new
```

Có thể làm:

```python
params = dict(url.query)

params["page"] = 3

new_url = url.with_query(params)

print(new_url)
```

Kết quả:

```text
https://example.com/search?q=python&page=3&sort=new
```

---

# 15. Đây là pattern pagination rất quan trọng

Viết thành function:

```python
from yarl import URL


def change_page(
    url: URL,
    page: int,
) -> URL:

    params = dict(url.query)

    params["page"] = page

    return url.with_query(params)
```

Sử dụng:

```python
url = URL("https://example.com/search?q=python&page=1&sort=new")

page_2 = change_page(url, 2)
page_3 = change_page(url, 3)

print(page_2)
print(page_3)
```

Kết quả:

```text
https://example.com/search?q=python&page=2&sort=new
https://example.com/search?q=python&page=3&sort=new
```

---

# 16. Nhưng có vấn đề với duplicate query

Ở Buổi 10 chúng ta đã học:

```text
?tag=python&tag=asyncio&tag=crawler
```

Nếu làm:

```python
params = dict(url.query)
```

thì bạn cần **cẩn thận** với các key lặp.

Ví dụ:

```python
url = URL("https://example.com/search?tag=python&tag=asyncio&tag=crawler")
```

Query có:

```text
tag → python
tag → asyncio
tag → crawler
```

Nhưng:

```python
dict(url.query)
```

không phải cách phù hợp để bảo toàn duplicate parameters.

Đối với query có nhiều giá trị, hãy sử dụng list các cặp:

```python
items = list(url.query.items())
```

và thao tác có chủ đích.

Đây là lý do chúng ta đã học duplicate query ở Buổi 10 trước khi đi sâu vào `with_query()`.

---

# 17. `with_query(None)`

Muốn xóa toàn bộ query:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2")

new_url = url.with_query(None)

print(new_url)
```

Kết quả:

```text
https://example.com/search
```

Đây là pattern rất đáng nhớ:

```python
url.with_query(None)
```

→ **xóa query**.

---

# 18. So sánh với `with_path()`

Chúng ta vừa học:

```python
url.with_path("/novel/python")
```

và hôm nay:

```python
url.with_query({"page": 2})
```

Cùng một triết lý:

```text
with_path()
    ↓
thay path

with_query()
    ↓
thay query
```

Cả hai đều:

* không mutate URL
* tạo URL mới
* giữ các thành phần khác

---

# 19. Ví dụ kết hợp `with_path()` + `with_query()`

```python
from yarl import URL

url = URL("https://example.com/old?q=python")

new_url = url.with_path("/search").with_query(
    {
        "q": "asyncio",
        "page": 2,
    }
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?q=asyncio&page=2
```

Transformation:

```text
https://example.com/old?q=python
             │
             │ with_path()
             ▼
https://example.com/search?q=python
             │
             │ with_query()
             ▼
https://example.com/search?q=asyncio&page=2
```

---

# 20. Query builder cho Novel Crawler

Ta có thể xây:

```python
from yarl import URL


class NovelSearchURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def build(
        self,
        keyword: str | None = None,
        page: int = 1,
        sort: str | None = None,
    ) -> URL:

        params: dict[str, object] = {
            "page": page,
        }

        if keyword:
            params["q"] = keyword

        if sort:
            params["sort"] = sort

        return self._base_url.with_query(params)
```

Sử dụng:

```python
builder = NovelSearchURLBuilder(URL("https://example.com/search"))

url = builder.build(
    keyword="python",
    page=2,
    sort="new",
)

print(url)
```

Kết quả:

```text
https://example.com/search?q=python&page=2&sort=new
```

---

# 21. Tách SearchCriteria

Trong kiến trúc DDD/SOLID, ta có thể làm rõ hơn:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NovelSearchCriteria:
    keyword: str | None = None
    page: int = 1
    sort: str | None = None
```

Sau đó:

```python
from yarl import URL


class NovelSearchURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def build(
        self,
        criteria: NovelSearchCriteria,
    ) -> URL:

        params: dict[str, object] = {
            "page": criteria.page,
        }

        if criteria.keyword:
            params["q"] = criteria.keyword

        if criteria.sort:
            params["sort"] = criteria.sort

        return self._base_url.with_query(params)
```

Sử dụng:

```python
criteria = NovelSearchCriteria(
    keyword="python",
    page=3,
    sort="new",
)

builder = NovelSearchURLBuilder(URL("https://example.com/search"))

url = builder.build(criteria)

print(url)
```

Kết quả:

```text
https://example.com/search?q=python&page=3&sort=new
```

Đây là thiết kế rất phù hợp với crawler của bạn:

```text
SearchCriteria
      ↓
URL Builder
      ↓
yarl.URL
      ↓
Fetcher
```

---

# 22. Một vấn đề quan trọng: `None`

Trong builder:

```python
params = {
    "q": keyword,
    "page": page,
    "sort": sort,
}
```

Nếu:

```python
keyword = None
sort = None
```

thì bạn không nhất thiết muốn URL có:

```text
?q=None&sort=None
```

Do đó nên xây params có điều kiện:

```python
params = {
    "page": page,
}

if keyword is not None:
    params["q"] = keyword

if sort is not None:
    params["sort"] = sort
```

Đây là business logic của URL builder, không phải việc của `yarl`.

---

# 23. Pagination chuẩn hơn

Giả sử URL hiện tại:

```text
https://example.com/search?q=python&page=5&sort=new
```

Ta muốn tạo page 6.

```python
from yarl import URL


def next_page(url: URL) -> URL:
    params = dict(url.query)

    current_page = int(params.get("page", 1))

    params["page"] = current_page + 1

    return url.with_query(params)
```

Sử dụng:

```python
url = URL("https://example.com/search?q=python&page=5&sort=new")

print(next_page(url))
```

Kết quả:

```text
https://example.com/search?q=python&page=6&sort=new
```

---

# 24. `with_query()` và pagination của crawler

Luồng:

```text
Listing URL
    │
    ▼
?keyword=python&page=1
    │
    │ parse
    ▼
page = 1
    │
    │ +1
    ▼
page = 2
    │
    ▼
with_query()
    │
    ▼
?keyword=python&page=2
```

Ví dụ:

```python
url = URL("https://example.com/novels").with_query(
    {
        "keyword": "python",
        "page": 1,
    }
)

next_url = url.with_query(
    {
        "keyword": "python",
        "page": 2,
    }
)
```

---

# 25. Đừng nhầm với `URL(..., query=...)`

Bạn cũng có thể tạo URL:

```python
url = URL(
    "https://example.com/search",
    query={
        "q": "python",
        "page": 2,
    },
)
```

Nhưng khi **đã có URL và muốn biến đổi query**, dùng:

```python
url.with_query(...)
```

sẽ rõ ý hơn.

---

# 26. Mini Project hoàn chỉnh

Tạo:

```text
lesson_15.py
```

```python
from dataclasses import dataclass

from yarl import URL


@dataclass(frozen=True)
class NovelSearchCriteria:
    keyword: str | None = None
    page: int = 1
    sort: str | None = None


class NovelSearchURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def build(
        self,
        criteria: NovelSearchCriteria,
    ) -> URL:

        params: dict[str, object] = {
            "page": criteria.page,
        }

        if criteria.keyword is not None:
            params["q"] = criteria.keyword

        if criteria.sort is not None:
            params["sort"] = criteria.sort

        return self._base_url.with_query(params)

    def change_page(
        self,
        url: URL,
        page: int,
    ) -> URL:

        params = dict(url.query)

        params["page"] = page

        return url.with_query(params)


def main() -> None:

    builder = NovelSearchURLBuilder(URL("https://example.com/search"))

    criteria = NovelSearchCriteria(
        keyword="python",
        page=1,
        sort="new",
    )

    url = builder.build(criteria)

    print("Page 1:")
    print(url)

    page_2 = builder.change_page(
        url,
        2,
    )

    print("\nPage 2:")
    print(page_2)

    page_3 = builder.change_page(
        url,
        3,
    )

    print("\nPage 3:")
    print(page_3)

    print("\nOriginal:")
    print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Page 1:
https://example.com/search?q=python&page=1&sort=new

Page 2:
https://example.com/search?q=python&page=2&sort=new

Page 3:
https://example.com/search?q=python&page=3&sort=new

Original:
https://example.com/search?q=python&page=1&sort=new
```

---

# 27. Bài tập

### Bài 1 — Thay query

Cho:

```python
url = URL("https://example.com/search?q=python&page=1")
```

Dùng `with_query()` tạo:

```text
https://example.com/search?q=asyncio&page=2
```

---

### Bài 2 — Xóa query

Cho:

```python
url = URL("https://example.com/search?q=python&page=2")
```

Dùng:

```python
with_query(...)
```

để tạo:

```text
https://example.com/search
```

---

### Bài 3 — Pagination

Viết:

```python
def change_page(url: URL, page: int) -> URL: ...
```

Yêu cầu:

```text
https://example.com/search?q=python&page=1&sort=new
```

→

```text
https://example.com/search?q=python&page=5&sort=new
```

**Không được làm mất `q` và `sort`.**

---

### Bài 4 — Novel Search

Tạo:

```python
@dataclass(frozen=True)
class NovelSearchCriteria:
    keyword: str | None
    page: int
    sort: str | None
    status: str | None
```

Sau đó tạo:

```python
NovelSearchURLBuilder
```

để sinh URL:

```text
https://example.com/search?q=python&page=2&sort=new&status=completed
```

Chỉ đưa parameter vào URL khi giá trị của nó không phải `None`.

---

# Tổng kết Buổi 15

Các phương thức đã học:

```python
url.with_scheme("https")
url.with_host("mirror.example.com")
url.with_port(8080)
url.with_path("/novel/python")
url.with_query(
    {
        "page": 2,
    }
)
```

Riêng `with_query()` phải nhớ **3 điều**:

### 1. Thay toàn bộ query

```python
url.with_query({"page": 2})
```

không tự động giữ query cũ.

### 2. Muốn xóa query

```python
url.with_query(None)
```

### 3. Muốn sửa một parameter nhưng giữ các parameter khác

```python
params = dict(url.query)
params["page"] = 3

new_url = url.with_query(params)
```

Và khi query có **duplicate keys**, không nên tùy tiện chuyển sang `dict`; hãy nhớ kỹ kiến thức Buổi 10 về:

```python
list(url.query.items())
url.query.getall(...)
```

### Bức tranh Phần II hiện tại

```text
URL
 │
 ├── with_scheme()
 ├── with_host()
 ├── with_port()
 ├── with_path()
 └── with_query()
```

**Buổi 16 — `with_fragment()`**: thay đổi fragment (`#chapter-10`, `#top`...), phân biệt fragment với query, và một điểm rất quan trọng cho crawler: **fragment thường không được gửi lên server trong HTTP request**.
