# Buổi 10 — Query nhiều giá trị với `yarl`

Đây là bài cuối của **Phần I — Nền tảng URL** theo roadmap của chúng ta.

Ở Buổi 9, ta xử lý:

```text
?page=2&limit=20
```

Mỗi key chỉ có một value.

Nhưng URL thực tế có thể có **nhiều value cho cùng một key**:

```text
?tag=python&tag=asyncio&tag=crawler
```

Đây là dạng rất quan trọng khi làm crawler vì có thể gặp:

```text
?tag=python&tag=web
?category=novel&category=manga
?id=10&id=20&id=30
```

---

# 1. Duplicate query parameter là gì?

Ví dụ:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Ta có:

```text
tag = python
tag = asyncio
tag = crawler
```

Không phải:

```python
{
    "tag": "python"
}
```

mà về mặt logic là:

```python
{
    "tag": [
        "python",
        "asyncio",
        "crawler",
    ]
}
```

---

# 2. Tạo URL có nhiều giá trị

Với `yarl`, ta có thể truyền **list các tuple**:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query([
    ("tag", "python"),
    ("tag", "asyncio"),
    ("tag", "crawler"),
])

print(url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Đây là cách rất quan trọng cần nhớ.

---

# 3. Vì sao không dùng dictionary?

Nếu viết:

```python
params = {
    "tag": "python",
    "tag": "asyncio",
    "tag": "crawler",
}
```

Python dictionary không thể giữ ba key giống nhau.

Kết quả thực tế chỉ còn:

```python
{
    "tag": "crawler"
}
```

Do đó:

```python
with_query({
    "tag": ...
})
```

không phù hợp để biểu diễn duplicate key.

---

# 4. List of tuples

Thay vào đó:

```python
params = [
    ("tag", "python"),
    ("tag", "asyncio"),
    ("tag", "crawler"),
]
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query(params)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=asyncio&tag=crawler
```

Cấu trúc này rất giống cách HTTP query thực sự được biểu diễn:

```text
key=value
&
key=value
&
key=value
```

---

# 5. Đọc nhiều giá trị bằng `getall()`

Đây là API quan trọng nhất của bài:

```python
url.query.getall("tag")
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=asyncio"
    "&tag=crawler"
)

tags = url.query.getall("tag")

print(tags)
```

Kết quả:

```text
['python', 'asyncio', 'crawler']
```

---

# 6. `get()` và `getall()` khác nhau

Giả sử:

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=asyncio"
    "&tag=crawler"
)
```

### `get()`

```python
print(url.query.get("tag"))
```

sẽ lấy **một value**.

### `getall()`

```python
print(url.query.getall("tag"))
```

lấy **tất cả value**.

Tư duy:

```text
get()
 ↓
một value

getall()
 ↓
nhiều value
```

---

# 7. Ví dụ với filter

Website có URL:

```text
/novels?genre=action&genre=romance&genre=fantasy
```

Ta có:

```python
from yarl import URL

url = URL(
    "https://example.com/novels"
).with_query([
    ("genre", "action"),
    ("genre", "romance"),
    ("genre", "fantasy"),
])

print(url)
```

Kết quả:

```text
https://example.com/novels?genre=action&genre=romance&genre=fantasy
```

---

# 8. Đọc lại

```python
genres = url.query.getall("genre")

print(genres)
```

Kết quả:

```text
['action', 'romance', 'fantasy']
```

Sau đó crawler có thể:

```python
for genre in genres:
    print(genre)
```

---

# 9. Query có cả key đơn và key nhiều giá trị

Ví dụ:

```text
/search?q=python&tag=asyncio&tag=httpx&page=2
```

Ta xây:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query([
    ("q", "python"),
    ("tag", "asyncio"),
    ("tag", "httpx"),
    ("page", 2),
])

print(url)
```

Kết quả:

```text
https://example.com/search?q=python&tag=asyncio&tag=httpx&page=2
```

---

# 10. Đọc từng loại

```python
print(url.query.get("q"))
print(url.query.getall("tag"))
print(url.query.get("page"))
```

Kết quả:

```text
python
['asyncio', 'httpx']
2
```

Lưu ý `page` khi lấy từ URL vẫn là chuỗi:

```python
page = int(url.query.get("page", "1"))
```

---

# 11. `query.items()`

Ta có thể duyệt:

```python
for key, value in url.query.items():
    print(key, value)
```

Với duplicate keys, các cặp vẫn được duyệt riêng:

```text
q python
tag asyncio
tag httpx
page 2
```

Điều này rất hữu ích khi debug crawler.

---

# 12. `query.keys()`

```python
print(list(url.query.keys()))
```

Với duplicate query, key có thể xuất hiện nhiều lần.

Do đó đừng mặc định rằng:

```python
query.keys()
```

luôn là một tập key unique giống dictionary.

Query của URL là một **sequence các cặp key/value**, không nên tư duy quá cứng nhắc như `dict`.

---

# 13. `query.values()`

Tương tự:

```python
print(list(url.query.values()))
```

Bạn có thể thấy toàn bộ values theo thứ tự xuất hiện.

---

# 14. Thứ tự query parameter

Với crawler, đôi khi thứ tự có ý nghĩa đối với:

* cache key
* chữ ký request
* canonical URL
* debugging
* so sánh URL

Ví dụ:

```text
?tag=python&tag=asyncio
```

khác về chuỗi với:

```text
?tag=asyncio&tag=python
```

Vì vậy khi dùng list of tuples:

```python
params = [
    ("tag", "python"),
    ("tag", "asyncio"),
]
```

ta đang biểu diễn một **sequence có thứ tự**.

---

# 15. Một ví dụ với chapter IDs

Giả sử website hỗ trợ:

```text
/download?chapter=10&chapter=11&chapter=12
```

Ta có:

```python
from yarl import URL

chapter_ids = [10, 11, 12]

params = [
    ("chapter", chapter_id)
    for chapter_id in chapter_ids
]

url = (
    URL("https://example.com/download")
    .with_query(params)
)

print(url)
```

Kết quả tương đương:

```text
https://example.com/download?chapter=10&chapter=11&chapter=12
```

---

# 16. Đây là pattern rất hữu ích

Ta có:

```python
chapter_ids = [10, 11, 12]

params = [
    ("chapter", chapter_id)
    for chapter_id in chapter_ids
]
```

Từ:

```python
[10, 11, 12]
```

thành:

```python
[
    ("chapter", 10),
    ("chapter", 11),
    ("chapter", 12),
]
```

rồi:

```python
url.with_query(params)
```

---

# 17. Search nhiều keyword

Ví dụ website:

```text
/search?q=python&q=httpx&q=yarl
```

Ta có:

```python
keywords = [
    "python",
    "httpx",
    "yarl",
]

params = [
    ("q", keyword)
    for keyword in keywords
]

url = (
    URL("https://example.com/search")
    .with_query(params)
)

print(url)
```

---

# 18. Query list không nhất thiết phải duplicate key

Có website dùng:

```text
?tags=python,asyncio,crawler
```

hoặc:

```text
?tags[]=python&tags[]=asyncio
```

hoặc:

```text
?tag=python&tag=asyncio
```

Đây là **quy ước của website/API**, không phải `yarl` tự quyết định.

Nếu website yêu cầu:

```text
?tag=python&tag=asyncio
```

thì dùng:

```python
[
    ("tag", "python"),
    ("tag", "asyncio"),
]
```

---

# 19. Một lỗi phổ biến trong crawler

Giả sử parser lấy được:

```python
tags = [
    "python",
    "asyncio",
    "crawler",
]
```

Developer viết:

```python
params = {
    "tag": tags
}
```

Sau đó:

```python
url.with_query(params)
```

Đây có thể **không tạo ra format mà website mong muốn**.

Nếu website yêu cầu:

```text
?tag=python&tag=asyncio&tag=crawler
```

hãy biểu diễn rõ:

```python
params = [
    ("tag", tag)
    for tag in tags
]
```

---

# 20. Function tiện ích

Ta có thể viết:

```python
from yarl import URL


def build_tag_url(
    base_url: URL,
    tags: list[str],
) -> URL:

    params = [
        ("tag", tag)
        for tag in tags
    ]

    return (
        base_url
        / "search"
    ).with_query(params)
```

Test:

```python
url = build_tag_url(
    URL("https://example.com"),
    [
        "python",
        "asyncio",
        "crawler",
    ],
)

print(url)
```

---

# 21. Một ví dụ hoàn chỉnh cho Novel Crawler

Giả sử crawler có chức năng tìm truyện theo nhiều thể loại:

```python
from yarl import URL


class NovelSearchURLBuilder:

    def __init__(self, base_url: str):
        self.base_url = URL(base_url)

    def build(
        self,
        keyword: str | None = None,
        genres: list[str] | None = None,
        page: int = 1,
    ) -> URL:

        params = []

        if keyword:
            params.append(
                ("q", keyword)
            )

        if genres:
            for genre in genres:
                params.append(
                    ("genre", genre)
                )

        params.append(
            ("page", page)
        )

        return (
            self.base_url
            / "search"
        ).with_query(params)


builder = NovelSearchURLBuilder(
    "https://example.com"
)

url = builder.build(
    keyword="kiếm hiệp",
    genres=[
        "action",
        "fantasy",
        "romance",
    ],
    page=2,
)

print(url)
```

URL sẽ có dạng:

```text
https://example.com/search?q=ki%E1%BA%BFm+hi%E1%BB%87p&genre=action&genre=fantasy&genre=romance&page=2
```

Representation encoding cụ thể có thể khác khi bạn nhìn URL ở dạng raw/human representation, nhưng ý nghĩa query là:

```text
q = kiếm hiệp

genre = action
genre = fantasy
genre = romance

page = 2
```

---

# 22. Đọc lại URL

```python
parsed = URL(
    "https://example.com/search"
    "?q=python"
    "&genre=action"
    "&genre=fantasy"
    "&page=2"
)

keyword = parsed.query.get("q")

genres = parsed.query.getall(
    "genre"
)

page = int(
    parsed.query.get("page", "1")
)

print(keyword)
print(genres)
print(page)
```

Kết quả:

```text
python
['action', 'fantasy']
2
```

---

# 23. `getall()` là API phải nhớ

Nếu URL:

```text
?tag=python&tag=asyncio&tag=httpx
```

Không làm:

```python
tag = url.query.get("tag")
```

nếu bạn cần **tất cả tags**.

Hãy:

```python
tags = url.query.getall("tag")
```

Kết quả:

```python
[
    "python",
    "asyncio",
    "httpx",
]
```

---

# 24. Xử lý khi key không tồn tại

Ví dụ:

```python
url = URL(
    "https://example.com/search?q=python"
)
```

Nếu:

```python
url.query.getall("tag")
```

thì bạn cần lưu ý API này phù hợp cho việc lấy nhiều giá trị của key; khi xây logic production, hãy kiểm tra trường hợp key không tồn tại và xử lý theo contract của code.

Một pattern đơn giản là:

```python
tags = list(
    url.query.getall("tag")
)
```

sau đó:

```python
if not tags:
    print("No tags")
```

---

# 25. Query duplicate và `dict()` — cực kỳ quan trọng

Đừng làm:

```python
params = dict(url.query)
```

nếu URL có:

```text
?tag=python&tag=asyncio&tag=httpx
```

Vì dictionary chỉ có một key:

```python
{
    "tag": "..."
}
```

Bạn có nguy cơ **mất các giá trị duplicate**.

Nếu cần bảo toàn query:

```python
params = list(url.query.items())
```

Sau đó sửa:

```python
params.append(
    ("new_param", "value")
)
```

và tạo URL mới.

---

# 26. Ví dụ bảo toàn duplicate query

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=asyncio"
    "&page=2"
)

params = list(
    url.query.items()
)

print(params)
```

Ta có dạng:

```python
[
    ("tag", "python"),
    ("tag", "asyncio"),
    ("page", "2"),
]
```

Sau đó:

```python
params.append(
    ("tag", "crawler")
)
```

Tạo URL:

```python
new_url = url.with_query(params)

print(new_url)
```

Ta vẫn giữ:

```text
tag=python
tag=asyncio
page=2
tag=crawler
```

---

# 27. Nếu cần thay toàn bộ query

Đây là lúc `with_query()` rất tiện.

```python
new_url = url.with_query([
    ("tag", "python"),
    ("tag", "crawler"),
    ("page", 3),
])
```

Query cũ được thay bằng query mới.

---

# 28. Pattern nên dùng trong crawler

Khi query có thể chứa duplicate:

```text
1. Parse
2. Preserve as list of pairs
3. Modify
4. with_query()
```

Ví dụ:

```python
params = list(url.query.items())

params.append(
    ("tag", "new-tag")
)

new_url = url.with_query(params)
```

Thay vì:

```python
params = dict(url.query)
```

---

# 29. Kiến trúc tổng quát

Sau 10 buổi, chúng ta có thể hình dung `yarl` như sau:

```text
                    yarl.URL
                       │
        ┌──────────────┼──────────────┐
        │              │              │
      scheme          path          query
                       │              │
                       │              ├── get()
                       │              ├── getall()
                       │              └── items()
                       │
                 ┌─────┴─────┐
                 │     │     │
                 /    parent name
```

Xây URL:

```python
URL("https://example.com")
    / "novel"
    / slug
```

Query:

```python
url.with_query(
    page=2
)
```

Multiple query:

```python
url.with_query([
    ("tag", "python"),
    ("tag", "asyncio"),
])
```

---

# 30. Mapping vào Novel Crawler

Đến đây chúng ta đã có đủ kiến thức để xử lý khá nhiều URL thực tế:

### Novel

```python
url = (
    BASE_URL
    / "novel"
    / novel_slug
)
```

### Chapter

```python
url = (
    BASE_URL
    / "novel"
    / novel_slug
    / chapter_slug
)
```

### Pagination

```python
url = url.with_query(
    page=2
)
```

### Search

```python
url = url.with_query(
    q="python",
    page=2,
)
```

### Multiple genres

```python
url = url.with_query([
    ("genre", "action"),
    ("genre", "fantasy"),
    ("genre", "romance"),
])
```

---

# 31. Bài tập thực hành

## Bài 1 — Multiple tags

Tạo:

```text
https://example.com/search?tag=python&tag=asyncio&tag=yarl
```

bằng `yarl`.

---

## Bài 2 — Đọc tất cả tags

Cho:

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=asyncio"
    "&tag=yarl"
)
```

Lấy:

```python
tags
```

kết quả:

```python
[
    "python",
    "asyncio",
    "yarl",
]
```

---

## Bài 3 — Chapter IDs

Từ:

```python
chapter_ids = [10, 20, 30, 40]
```

tạo:

```text
?chapter=10&chapter=20&chapter=30&chapter=40
```

---

## Bài 4 — Search

Viết:

```python
def build_search_url(
    base_url: URL,
    keyword: str,
    tags: list[str],
    page: int,
) -> URL:
    ...
```

Kết quả phải có dạng:

```text
/search?q=python&tag=asyncio&tag=httpx&page=2
```

---

## Bài 5 — Quan trọng

Cho:

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=asyncio"
    "&page=2"
)
```

Thêm:

```text
tag=crawler
```

nhưng **không được làm mất**:

```text
tag=python
tag=asyncio
```

Gợi ý:

```python
params = list(url.query.items())
```

---

# Tổng kết Phần I — Buổi 1 → 10

Chúng ta đã đi qua nền tảng của `yarl`.

```text
01  URL()
02  URL components
03  Immutable URL
04  Path manipulation
05  Query basics
06  Relative / Absolute URL
07  Join URL với /
08  Path parameters
09  Query string
10  Multiple query values
```

Các API quan trọng nhất hiện tại:

```python
URL(...)
```

```python
url / "segment"
```

```python
url.join(...)
```

```python
url.path
```

```python
url.query
```

```python
url.query.get(...)
```

```python
url.query.getall(...)
```

```python
url.query.items()
```

```python
url.with_query(...)
```

Đặc biệt với crawler, hãy ghi nhớ pattern này:

```text
HTML href
    │
    ▼
relative URL
    │
    │ page_url.join(...)
    ▼
absolute URL
    │
    ├── / path / parameters
    │
    └── with_query(...)
             │
             ├── single value
             └── multiple values
    ▼
yarl.URL
    │
    ▼
httpx
```

**Phần II — URL Manipulation** bắt đầu từ **Buổi 11 — `with_scheme()`**, sau đó lần lượt `with_host()`, `with_port()`, `with_path()`, `with_query()`, `with_fragment()`, `with_name()`, `with_suffix()`, `parent` và `origin()`. Đây là phần chúng ta sẽ chuyển từ **đọc URL** sang **biến đổi URL một cách an toàn**.
