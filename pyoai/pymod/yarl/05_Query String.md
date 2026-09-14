# Buổi 5 — Query String trong `yarl`

Hôm nay chúng ta học một phần **rất quan trọng đối với crawler**: xử lý query string.

Ví dụ:

```text
https://example.com/novels?page=2&sort=new
                                  └────────────┘
                                      query
```

Sau bài này bạn sẽ xử lý được:

```text
?page=2
?page=2&limit=20
?sort=new&page=2
?tag=python&tag=asyncio
```

mà không cần tự `split("&")`, `split("=")` hay `replace()`.

---

# 1. Query String là gì?

Một URL:

```text
https://example.com/novels?page=2&sort=new
```

gồm:

```text
https://example.com/novels?page=2&sort=new
                         └───────────────┘
                                query
```

Query gồm các cặp:

```text
page = 2
sort = new
```

Trong `yarl`:

```python id="5c1g3y"
from yarl import URL

url = URL("https://example.com/novels?page=2&sort=new")

print(url.query)
```

---

# 2. `url.query`

```python id="h7gq4j"
from yarl import URL

url = URL("https://example.com/novels?page=2&sort=new")

query = url.query

print(query)
print(type(query))
```

Bạn sẽ thấy query được biểu diễn dưới dạng một cấu trúc multidict của `yarl`/`multidict`, thay vì một string đơn giản.

Điểm quan trọng:

```python id="1jlye2"
url.query
```

cho phép chúng ta làm việc với query **theo key/value**.

---

# 3. Lấy một parameter

Ví dụ:

```python id="t3fjhp"
url = URL("https://example.com/novels?page=2&sort=new")

print(url.query["page"])
print(url.query["sort"])
```

Kết quả:

```text id="9xj9fe"
2
new
```

Lưu ý: giá trị query về bản chất là **string**.

Vì vậy:

```python id="qqg4oa"
page = url.query["page"]

print(type(page))
```

thường là:

```text id="iy9a1p"
<class 'str'>
```

Nếu application cần số:

```python id="txw6k7"
page = int(url.query["page"])
```

---

# 4. `query.get()`

Nếu key có thể không tồn tại, nên dùng:

```python id="x4z85w"
page = url.query.get("page")
```

Ví dụ:

```python id="v0g5d9"
from yarl import URL

url = URL("https://example.com/novels")

print(url.query.get("page"))
```

Kết quả:

```text id="3zpkpj"
None
```

An toàn hơn:

```python id="5x2mni"
page = url.query.get("page", "1")

print(page)
```

→

```text id="t0x25m"
1
```

---

# 5. `[]` và `.get()` khác nhau

### Dùng `[]`

```python id="q4h0fi"
page = url.query["page"]
```

Nếu không tồn tại:

```text
KeyError
```

### Dùng `.get()`

```python id="sy3pl4"
page = url.query.get("page")
```

Nếu không tồn tại:

```text
None
```

Trong parser, khi HTML/URL không chắc chắn, thường:

```python id="qks1pb"
url.query.get("page")
```

an toàn hơn.

---

# 6. Query nhiều parameter

```python id="2p5hzg"
url = URL("https://example.com/novels?page=2&limit=20&sort=new")
```

Có thể:

```python id="trq9gs"
print(url.query.get("page"))
print(url.query.get("limit"))
print(url.query.get("sort"))
```

Kết quả:

```text
2
20
new
```

---

# 7. `query_string`

Nếu muốn lấy toàn bộ query dưới dạng string:

```python id="c16x5p"
print(url.query_string)
```

Kết quả:

```text
page=2&limit=20&sort=new
```

So sánh:

```text id="4cpr8g"
url.query
     ↓
MultiDict-like object

url.query_string
     ↓
"page=2&limit=20&sort=new"
```

---

# 8. Không nên tự parse query

Không nên:

```python id="u1q2fj"
query = "page=2&sort=new"

parts = query.split("&")

for part in parts:
    key, value = part.split("=")
```

Cách này nhanh chóng gặp vấn đề với:

```text
Unicode
URL encoding
empty value
duplicate key
special characters
```

`yarl` đã xử lý những vấn đề này cho chúng ta.

---

# 9. Tạo query bằng `with_query()`

Đây là API cực kỳ quan trọng.

```python id="ng7h9k"
from yarl import URL

url = URL("https://example.com/novels")

new_url = url.with_query(
    page=2,
    sort="new",
)

print(new_url)
```

Kết quả:

```text
https://example.com/novels?page=2&sort=new
```

---

# 10. Query bằng dictionary

```python id="wlq0ty"
params = {
    "page": 2,
    "limit": 20,
    "sort": "new",
}

url = URL("https://example.com/novels")

new_url = url.with_query(params)

print(new_url)
```

Kết quả:

```text
https://example.com/novels?page=2&limit=20&sort=new
```

Đây là cách rất tiện khi query được tạo động.

---

# 11. Pagination thực tế

Đây là nơi `yarl` bắt đầu rất hữu ích cho crawler.

```python id="vqm4fi"
from yarl import URL


base_url = URL("https://example.com/novels")

for page in range(1, 6):
    url = base_url.with_query(page=page)
    print(url)
```

Kết quả:

```text
https://example.com/novels?page=1
https://example.com/novels?page=2
https://example.com/novels?page=3
https://example.com/novels?page=4
https://example.com/novels?page=5
```

---

# 12. Query có nhiều giá trị cùng key

Đây là phần **rất quan trọng**.

URL có thể:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Ở đây:

```text
tag = python
tag = asyncio
tag = crawler
```

Không thể coi query đơn giản là:

```python
dict[str, str]
```

vì một key có nhiều value.

---

# 13. `query.get()` với duplicate key

```python id="v7e2wp"
from yarl import URL

url = URL("https://example.com/search?tag=python&tag=asyncio&tag=crawler")

print(url.query.get("tag"))
```

Bạn sẽ nhận được **một value đại diện cho key đó**, không phải danh sách toàn bộ values.

Vì vậy nếu cần tất cả:

> Dùng `getall()`.

---

# 14. `query.getall()`

```python id="r5n0sm"
from yarl import URL

url = URL("https://example.com/search?tag=python&tag=asyncio&tag=crawler")

tags = url.query.getall("tag")

print(tags)
```

Kết quả tương tự:

```text
['python', 'asyncio', 'crawler']
```

Đây là API cần nhớ:

```python id="5iuf9g"
url.query.getall("tag")
```

→ lấy **tất cả value** của `tag`.

---

# 15. `getall()` khi key không tồn tại

```python id="qj1eaa"
url = URL("https://example.com/search")

print(url.query.getall("tag"))
```

Thay vì `None`, nó có thể báo lỗi nếu key không tồn tại.

Vì vậy khi không chắc key có tồn tại:

```python id="ny8x4m"
if "tag" in url.query:
    tags = url.query.getall("tag")
else:
    tags = []
```

---

# 16. `query.items()`

Có thể duyệt query:

```python id="p4svzt"
from yarl import URL

url = URL("https://example.com/novels?page=2&sort=new")

for key, value in url.query.items():
    print(key, "=", value)
```

Kết quả:

```text
page = 2
sort = new
```

---

# 17. `query.keys()`

```python id="b4my3x"
for key in url.query.keys():
    print(key)
```

Có thể dùng khi cần kiểm tra parameter.

---

# 18. `query.values()`

```python id="y3qrr3"
for value in url.query.values():
    print(value)
```

---

# 19. Duplicate key và `items()`

Với:

```text
?tag=python&tag=asyncio&tag=crawler
```

query là multidict nên duplicate key có thể được giữ.

Đây là một khác biệt quan trọng so với:

```python id="2j7h1n"
dict
```

Nếu bạn làm:

```python id="pj1h7f"
data = {
    "tag": "python",
    "tag": "asyncio",
}
```

Python dictionary chỉ giữ một value cuối cùng.

Còn query của URL có thể biểu diễn:

```text
tag=python
tag=asyncio
tag=crawler
```

---

# 20. Tạo duplicate query

Với nhiều value cho cùng một key, một cách rõ ràng là dùng danh sách các cặp:

```python id="f6js1f"
from yarl import URL

url = URL("https://example.com/search")

new_url = url.with_query(
    [
        ("tag", "python"),
        ("tag", "asyncio"),
        ("tag", "crawler"),
    ]
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Đây là một kỹ thuật quan trọng.

---

# 21. Query với Unicode

Crawler Việt Nam rất dễ gặp:

```text
?keyword=đấu phá thương khung
```

Ta có thể:

```python id="q0otip"
from yarl import URL

url = URL("https://example.com/search")

url = url.with_query(keyword="đấu phá thương khung")

print(url)
```

`yarl` sẽ xử lý encoding phù hợp khi tạo URL.

Bạn không cần tự:

```python
quote(...)
```

trong trường hợp thông thường.

---

# 22. Query chứa ký tự đặc biệt

Ví dụ:

```python id="u8dd5n"
url = URL("https://example.com/search")

url = url.with_query(keyword="Python & AsyncIO")

print(url)
```

URL sẽ được encode đúng cách thay vì bạn tự nối:

```text
?keyword=Python & AsyncIO
```

Đây là lý do sử dụng URL library an toàn hơn string manipulation.

---

# 23. Query và `with_query()` — vấn đề cần nhớ

Giả sử:

```python id="k1j6fw"
url = URL("https://example.com/search?page=2&sort=new")
```

Nếu:

```python id="c6b8q1"
new_url = url.with_query(page=3)
```

thì bạn **không nên kỳ vọng** `sort=new` tự động được giữ lại.

Bạn đang cung cấp query mới:

```text
page=3
```

Để giữ và thay đổi query hiện tại, chúng ta cần tạo dữ liệu query mới.

Ví dụ:

```python id="8ewh5j"
from yarl import URL

url = URL("https://example.com/search?page=2&sort=new")

params = dict(url.query)
params["page"] = "3"

new_url = url.with_query(params)

print(new_url)
```

Kết quả:

```text
https://example.com/search?page=3&sort=new
```

**Nhưng:** cách `dict(url.query)` sẽ không phù hợp nếu bạn cần giữ duplicate keys.

Đó là lý do chúng ta phải hiểu multidict trước khi xây URL manipulation phức tạp.

---

# 24. Xây `QueryParams` cho crawler

Ta có thể tạo một helper đơn giản:

```python id="9if6u7"
from yarl import URL


class Pagination:
    def __init__(self, url: URL):
        self.url = url

    def page(self, page: int) -> URL:
        return self.url.with_query(page=page)


def main() -> None:
    base_url = URL("https://example.com/truyen")

    pagination = Pagination(base_url)

    for page in range(1, 4):
        print(pagination.page(page))


if __name__ == "__main__":
    main()
```

Output:

```text
https://example.com/truyen?page=1
https://example.com/truyen?page=2
https://example.com/truyen?page=3
```

---

# 25. Case study — Parser pagination

Giả sử parser đọc được:

```html
<a href="/truyen?page=2">Trang sau</a>
```

Ta có:

```python id="7m5xqz"
href = "/truyen?page=2"

url = URL(href)

print(url.path)
print(url.query.get("page"))
```

Kết quả:

```text
/truyen
2
```

Parser có thể tạo domain data:

```python id="f7w10w"
page = url.query.get("page")
```

Sau đó:

```python id="zxxbcz"
page_number = int(page)
```

---

# 26. Case study — search URL

Ví dụ crawler có chức năng tìm truyện:

```python id="tpn9o5"
from yarl import URL


def make_search_url(
    base_url: URL,
    keyword: str,
    page: int = 1,
) -> URL:

    return base_url.with_query(
        keyword=keyword,
        page=page,
    )


def main() -> None:
    base_url = URL("https://example.com/search")

    url = make_search_url(
        base_url,
        keyword="đấu phá thương khung",
        page=2,
    )

    print(url)


if __name__ == "__main__":
    main()
```

Kết quả sẽ là URL đã được encode phù hợp.

---

# 27. Case study — Filter

Giả sử website hỗ trợ:

```text
?status=completed
&category=fantasy
&page=2
```

Ta có:

```python id="m7mtc9"
params = {
    "status": "completed",
    "category": "fantasy",
    "page": 2,
}

url = URL("https://example.com/novels").with_query(params)

print(url)
```

Đây là pattern rất phù hợp cho:

```text
ListingRequest
    ↓
Query Parameters
    ↓
URL
    ↓
Fetcher
```

---

# 28. Đừng biến `yarl` thành Domain Model

Trong kiến trúc DDD của crawler, tôi **không khuyến nghị** nhét toàn bộ logic query vào `URL` rồi để domain phụ thuộc trực tiếp vào mọi API của `yarl`.

Ví dụ:

```text
Domain
  ↓
yarl.URL
```

có thể chấp nhận nếu `URL` là một Value Object infrastructure-friendly trong project của bạn, nhưng cần cân nhắc coupling.

Một hướng sạch hơn:

```text
Parser
   ↓
URL
   ↓
URL Value Object
   ↓
Application
   ↓
Fetcher
```

hoặc nếu project chấp nhận `yarl` làm dependency chung:

```text
URL
 ↓
domain/application đều sử dụng URL abstraction
```

Chúng ta sẽ quay lại vấn đề này khi học **`yarl` + DDD**.

---

# 29. Mini project — Query Inspector

Tạo:

```text
lesson_05/
└── main.py
```

Code:

```python id="lzwvne"
from yarl import URL


def inspect_query(url: URL) -> None:
    print("=" * 50)
    print("URL")
    print("=" * 50)
    print(url)

    print()

    print("=" * 50)
    print("QUERY STRING")
    print("=" * 50)
    print(url.query_string)

    print()

    print("=" * 50)
    print("PARAMETERS")
    print("=" * 50)

    for key, value in url.query.items():
        print(f"{key} = {value}")


def main() -> None:
    url = URL(
        "https://example.com/search"
        "?keyword=python"
        "&page=2"
        "&sort=new"
        "&tag=asyncio"
        "&tag=crawler"
    )

    inspect_query(url)

    print()

    print("Page:", url.query.get("page"))
    print("Keyword:", url.query.get("keyword"))
    print("Tags:", url.query.getall("tag"))


if __name__ == "__main__":
    main()
```

Đây là bài thực hành tổng hợp của Buổi 5.

---

# 30. Bài tập

### Bài 1 — Đọc query

Cho:

```python
url = URL("https://example.com/search?keyword=python&page=3&sort=new")
```

Lấy:

```text
keyword
page
sort
```

---

### Bài 2 — Pagination

Viết:

```python
def make_page_url(
    url: URL,
    page: int,
) -> URL: ...
```

Input:

```text
https://example.com/novels
```

Output:

```text
https://example.com/novels?page=1
https://example.com/novels?page=2
https://example.com/novels?page=3
```

---

### Bài 3 — Duplicate query

Cho:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Lấy:

```python
["python", "asyncio", "crawler"]
```

bằng:

```python
query.getall(...)
```

---

### Bài 4 — Tạo filter URL

Viết:

```python
def make_listing_url(
    base_url: URL,
    category: str,
    status: str,
    page: int,
) -> URL: ...
```

Input:

```python
base_url = URL("https://example.com/novels")
```

Output tương tự:

```text
https://example.com/novels?category=fantasy&status=completed&page=2
```

---

### Bài 5 — Novel Crawler

Viết hàm:

```python
def get_page_number(url: URL) -> int: ...
```

Các trường hợp:

```text
https://example.com/truyen?page=5
→ 5

https://example.com/truyen
→ 1
```

Gợi ý:

```python
url.query.get("page")
```

---

# Tổng kết Buổi 5

Các API cần thuộc:

```python
url.query
```

→ query object

```python
url.query_string
```

→ query dạng string

```python
url.query["page"]
```

→ lấy value, có thể `KeyError`

```python
url.query.get("page")
```

→ lấy value an toàn hơn

```python
url.query.getall("tag")
```

→ lấy **tất cả value** khi key lặp

```python
url.query.items()
```

→ duyệt key/value

```python
url.with_query(...)
```

→ tạo URL với query mới

---

### Đặc biệt nhớ 3 trường hợp:

```text
? page=2
        ↓
query["page"]

? page=2&sort=new
        ↓
query.get("page")

? tag=python&tag=asyncio&tag=crawler
        ↓
query.getall("tag")
```

Và trong **Novel Crawler**, query sẽ xuất hiện rất nhiều ở:

```text
Listing Parser
      ↓
Pagination
      ↓
? page=2

Search
      ↓
? keyword=python

Filter
      ↓
? category=fantasy&status=completed

Crawler Queue
      ↓
URL
```

**Buổi 6** chúng ta sẽ học **URL encoding/decoding trong `yarl`**: Unicode tiếng Việt, khoảng trắng, `%20`, `+`, `%2F`, `%3F`, `raw_path`, `raw_query_string`, `human_repr()` và các lỗi encoding thường gặp khi crawler website.
