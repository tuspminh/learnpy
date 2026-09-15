# Phần III — Query String chuyên sâu

# Buổi 24 — Duplicate Query Parameters

Đây là một buổi **rất quan trọng** nếu bạn muốn xử lý URL crawler một cách chắc chắn.

Ở Buổi 23, chúng ta đã tạo được:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Hôm nay chúng ta tập trung vào vấn đề:

> **Một query parameter có thể xuất hiện nhiều lần. Làm thế nào để đọc, giữ nguyên và thay đổi nó mà không vô tình làm mất dữ liệu?**

---

# 1. Duplicate Query Parameter là gì?

URL:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

có query:

```text
tag=python
tag=sqlite
tag=yarl
```

Key:

```text
tag
```

xuất hiện **3 lần**.

Đây gọi là:

```text
duplicate query parameter
```

Một số website sử dụng pattern này cho:

```text
tag
category
author
genre
id
filter
...
```

Ví dụ:

```text
?genre=fantasy&genre=action
```

hoặc:

```text
?id=10&id=20&id=30
```

---

# 2. Tạo URL

```python id="h4w8cy"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

print(url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

---

# 3. `url.query`

Lấy query:

```python id="xv8k6f"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

print(url.query)
```

`url.query` là một `MultiDict`/query mapping có khả năng biểu diễn duplicate keys.

Đây là điểm quan trọng:

```text
dict
    → thường nhìn query như key → value

MultiDict
    → key → nhiều value
```

---

# 4. `.get()` với duplicate key

Ví dụ:

```python id="b5zkqb"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

print(url.query.get("tag"))
```

Khi có duplicate key, `.get()` **không phải API để lấy toàn bộ các giá trị**.

Thông thường bạn sẽ nhận **một giá trị đại diện**, vì vậy:

> Khi query có duplicate parameters, không nên dùng `.get()` nếu mục tiêu là lấy tất cả values.

Muốn lấy toàn bộ, chúng ta sẽ dùng:

```python id="b74nfp"
url.query.getall("tag")
```

ở phần tiếp theo của bài.

---

# 5. `getall()` — lấy tất cả value

```python id="4t8jtd"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

tags = url.query.getall("tag")

print(tags)
```

Kết quả:

```text
['python', 'sqlite', 'yarl']
```

Đây là API cực kỳ quan trọng:

```python id="0y1x23"
url.query.getall("tag")
```

Mental model:

```text
get()
    ↓
một value

getall()
    ↓
tất cả values
```

---

# 6. Thứ tự được giữ

URL:

```text
?tag=python&tag=sqlite&tag=yarl
```

thì:

```python id="rj1clh"
url.query.getall("tag")
```

cho:

```text
python
sqlite
yarl
```

theo thứ tự xuất hiện.

Điều này rất hữu ích khi query có semantic về thứ tự.

Ví dụ:

```text
?sort=name&sort=rating&sort=updated
```

---

# 7. `getall()` với key không tồn tại

```python id="ajqzgn"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
)

print(url.query.getall("author"))
```

Nếu key không tồn tại, `getall()` có thể yêu cầu bạn cung cấp default hoặc phát sinh lỗi tùy cách gọi/API version.

Trong application code, cách an toàn thường là kiểm tra:

```python id="7fckk7"
if "author" in url.query:
    values = url.query.getall("author")
else:
    values = []
```

Hoặc dùng API phù hợp với version `yarl` bạn đang sử dụng.

---

# 8. Tại sao `dict(url.query)` nguy hiểm?

Đây là phần quan trọng nhất.

Giả sử:

```python id="8xk15d"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

Nếu làm:

```python id="0lzn7q"
params = dict(url.query)

print(params)
```

bạn đang ép một cấu trúc có khả năng chứa duplicate keys thành một `dict`.

Dictionary không thể biểu diễn:

```text
tag = python
tag = sqlite
tag = yarl
```

như ba entries độc lập.

Thông tin duplicate có thể bị mất.

Vì vậy:

```python
dict(url.query)
```

**không phải cách an toàn để chuyển một query có duplicate parameters thành cấu trúc dữ liệu mới.**

---

# 9. Cách giữ nguyên query entries

Dùng:

```python id="v8q5i4"
list(url.query.items())
```

Ví dụ:

```python id="g6p6f4"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

items = list(url.query.items())

print(items)
```

Kết quả:

```text
[
    ('tag', 'python'),
    ('tag', 'sqlite'),
    ('tag', 'yarl')
]
```

Đây chính là cấu trúc chúng ta đã học ở Buổi 23:

```python id="9v5yfc"
list[tuple]
```

---

# 10. Query → List of Tuples → Query

Đây là một workflow rất mạnh.

```text
URL
 ↓
url.query
 ↓
list(url.query.items())
 ↓
modify
 ↓
URL.with_query(...)
 ↓
URL mới
```

Ví dụ:

```python id="t6w4sh"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
)

items = list(url.query.items())

print(items)
```

Ta nhận:

```text
[
    ('tag', 'python'),
    ('tag', 'sqlite')
]
```

Sau đó có thể:

```python id="9i7n4b"
items.append(
    ("tag", "yarl")
)
```

và:

```python id="4i4l4p"
new_url = URL(
    "https://example.com/search"
).with_query(items)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

---

# 11. Thêm một duplicate parameter

Ví dụ:

```python id="f0m2sx"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
)

items = list(url.query.items())

items.append(
    ("tag", "yarl")
)

new_url = url.with_query(items)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

---

# 12. Xóa một value cụ thể

Giả sử:

```text
?tag=python&tag=sqlite&tag=yarl
```

muốn xóa:

```text
tag=sqlite
```

Có thể thao tác trên list entries:

```python id="l2q2wv"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

items = [
    (key, value)
    for key, value in url.query.items()
    if not (
        key == "tag"
        and value == "sqlite"
    )
]

new_url = url.with_query(items)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=yarl
```

---

# 13. Xóa toàn bộ `tag`

Nếu muốn xóa tất cả:

```text
tag=python
tag=sqlite
tag=yarl
```

thì:

```python id="k7e7mc"
items = [
    (key, value)
    for key, value in url.query.items()
    if key != "tag"
]
```

Sau đó:

```python id="s3w0u1"
new_url = url.with_query(items)
```

Kết quả:

```text
https://example.com/search
```

---

# 14. Giữ duplicate nhưng thay value

Ví dụ:

```text
?tag=python&tag=sqlite&tag=yarl
```

muốn đổi:

```text
sqlite
```

thành:

```text
asyncio
```

Ta có:

```python id="1r8j79"
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

items = [
    (
        key,
        "asyncio"
        if key == "tag" and value == "sqlite"
        else value,
    )
    for key, value in url.query.items()
]

new_url = url.with_query(items)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=asyncio&tag=yarl
```

---

# 15. `getall()` rất phù hợp cho Parser

Giả sử parser gặp:

```text
https://example.com/search?genre=fantasy&genre=action
```

Ta có:

```python id="j9r5es"
genres = url.query.getall("genre")
```

Kết quả:

```python id="7h5e0f"
[
    "fantasy",
    "action",
]
```

Sau đó application có thể xử lý:

```python id="v6l5ad"
for genre in genres:
    print(genre)
```

Output:

```text
fantasy
action
```

---

# 16. Novel Crawler — Multi Genre

Đây là ví dụ sát project của bạn.

Giả sử search URL:

```text
https://example.com/novels
?genre=fantasy
&genre=action
&genre=romance
&page=2
```

Code:

```python id="r8t8u7"
from yarl import URL


url = URL(
    "https://example.com/novels"
    "?genre=fantasy"
    "&genre=action"
    "&genre=romance"
    "&page=2"
)

genres = url.query.getall("genre")
page = url.query.get("page")

print("Genres:", genres)
print("Page:", page)
```

Kết quả:

```text
Genres: ['fantasy', 'action', 'romance']
Page: 2
```

Ở đây:

```text
genre
 ↓
nhiều values
 ↓
getall()
```

còn:

```text
page
 ↓
một value
 ↓
get()
```

---

# 17. Đây là mental model rất quan trọng

Query có thể được nhìn như:

```text
Query
 │
 ├── keyword → một value
 │
 ├── page    → một value
 │
 └── genre   → nhiều values
                  │
                  ├── fantasy
                  ├── action
                  └── romance
```

Vì vậy API:

```python id="5z9j8f"
query.get("keyword")
```

và:

```python id="fbp0d9"
query.getall("genre")
```

phục vụ hai trường hợp khác nhau.

---

# 18. Đọc toàn bộ query mà không mất duplicate

Nếu muốn inspect:

```python id="9ad8b2"
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&tag=sqlite"
    "&tag=yarl"
    "&page=2"
)
```

dùng:

```python id="z1a4et"
for key, value in url.query.items():
    print(key, "=", value)
```

Kết quả:

```text
keyword = python
tag = sqlite
tag = yarl
page = 2
```

Đây là cách rất tốt để debug crawler.

---

# 19. `items()` vs `getall()`

### `items()`

```python id="n3t4ot"
url.query.items()
```

cho toàn bộ query entries:

```text
keyword = python
tag = sqlite
tag = yarl
page = 2
```

### `getall("tag")`

```python id="q40rrl"
url.query.getall("tag")
```

chỉ lấy:

```text
sqlite
yarl
```

Mental model:

```text
items()
   ↓
toàn bộ query

getall("tag")
   ↓
tất cả values của tag
```

---

# 20. Tại sao không chỉ dùng `dict`?

Giả sử website gửi:

```text
?tag=python&tag=sqlite
```

Nếu application chuyển ngay thành:

```python id="pm9w3s"
{
    "tag": "sqlite"
}
```

thì:

```text
tag=python
```

đã bị mất.

Điều này có thể dẫn đến bug rất khó phát hiện:

```text
Website
   ↓
URL
   ↓
Parser
   ↓
dict
   ↓
MẤT duplicate
   ↓
URL Builder
   ↓
request sai
```

Vì vậy crawler nên cẩn thận tại boundary:

```text
URL ↔ Query data structure
```

---

# 21. Một `QueryParams` abstraction nhỏ

Nếu project bắt đầu phức tạp, ta có thể tạo abstraction:

```python id="rq6xzg"
from dataclasses import dataclass
from yarl import URL


@dataclass
class QueryParams:

    items: list[tuple[str, str]]

    @classmethod
    def from_url(cls, url: URL):
        return cls(
            list(url.query.items())
        )

    def to_url(self, base_url: URL) -> URL:
        return base_url.with_query(
            self.items
        )
```

Sử dụng:

```python id="t05hvn"
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
)

params = QueryParams.from_url(url)

print(params.items)
```

Kết quả:

```text
[
    ('tag', 'python'),
    ('tag', 'sqlite')
]
```

Sau đó:

```python id="p5x4hh"
params.items.append(
    ("tag", "yarl")
)
```

và:

```python id="o0y9gk"
new_url = params.to_url(
    URL("https://example.com/search")
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

---

# 22. Tuy nhiên, chưa cần abstraction này

Đây là điểm tôi muốn bạn đặc biệt lưu ý khi xây crawler.

Chưa cần ngay:

```text
QueryParams
QueryManager
QueryCollection
QueryFactory
QuerySerializer
```

Nếu requirement chỉ là:

```python id="s1fq1n"
url.query.getall("tag")
```

thì dùng trực tiếp là tốt nhất.

Abstraction chỉ nên xuất hiện khi chúng ta thực sự cần:

```text
read
modify
normalize
deduplicate
canonicalize
rebuild
```

Đây là tư duy mà bạn đã học trong DDD/SOLID.

---

# 23. Complete example — Query manipulation

Đây là chương trình bạn nên chạy thử:

```python id="q9o5os"
from yarl import URL


def main():
    url = URL(
        "https://example.com/search"
        "?keyword=python"
        "&tag=sqlite"
        "&tag=yarl"
        "&page=2"
    )

    print("Original:")
    print(url)

    print("\nAll query items:")

    for key, value in url.query.items():
        print(f"{key} = {value}")

    print("\nAll tags:")

    tags = url.query.getall("tag")

    print(tags)

    print("\nAdd tag:")

    items = list(url.query.items())

    items.append(
        ("tag", "crawler")
    )

    new_url = url.with_query(items)

    print(new_url)

    print("\nRemove sqlite tag:")

    items = [
        (key, value)
        for key, value in new_url.query.items()
        if not (
            key == "tag"
            and value == "sqlite"
        )
    ]

    new_url = new_url.with_query(items)

    print(new_url)


if __name__ == "__main__":
    main()
```

Kết quả logic:

```text
Original:
https://example.com/search?keyword=python&tag=sqlite&tag=yarl&page=2

All query items:
keyword = python
tag = sqlite
tag = yarl
page = 2

All tags:
['sqlite', 'yarl']

Add tag:
https://example.com/search?keyword=python&tag=sqlite&tag=yarl&page=2&tag=crawler

Remove sqlite tag:
https://example.com/search?keyword=python&tag=yarl&page=2&tag=crawler
```

---

# 24. Pattern quan trọng nhất của Buổi 24

Khi cần **đọc tất cả values**:

```python id="k6x0se"
values = url.query.getall("tag")
```

Khi cần **giữ nguyên toàn bộ query entries**:

```python id="y2i6gp"
items = list(url.query.items())
```

Sau khi sửa:

```python id="qk4m10"
new_url = url.with_query(items)
```

Đây là workflow nên nhớ:

```text
URL
 │
 ↓
url.query
 │
 ├── get()       → một value
 │
 ├── getall()    → nhiều values
 │
 └── items()     → toàn bộ key/value entries
                       │
                       ↓
                  list[tuple]
                       │
                       ↓
                 modify
                       │
                       ↓
              with_query()
                       │
                       ↓
                    URL mới
```

---

# 25. Dictionary vs MultiDict vs List/Tuple

| Cấu trúc                  | Duplicate key | Dùng khi           |
| ------------------------- | ------------: | ------------------ |
| `dict`                    |             ❌ | Mỗi key một value  |
| `MultiDict` / `url.query` |             ✅ | Đọc query          |
| `list[tuple]`             |             ✅ | Xây/sửa query      |
| `tuple[tuple]`            |             ✅ | Sequence immutable |

Đặc biệt:

```text
url.query
```

là cấu trúc rất phù hợp để **đọc query có duplicate**.

Còn:

```text
list(url.query.items())
```

rất tiện khi muốn **biến query thành sequence có thể chỉnh sửa rồi đưa trở lại `with_query()`**.

---

# 26. Liên hệ trực tiếp với Novel Crawler

Giả sử Parser phát hiện:

```text
https://example.com/search
?genre=fantasy
&genre=action
&genre=romance
&page=2
```

Parser có thể lấy:

```python id="m0r7x9"
genres = url.query.getall("genre")
```

→

```python id="y3q1lf"
[
    "fantasy",
    "action",
    "romance",
]
```

Application có thể dùng:

```python id="jzq8i1"
page = int(
    url.query.get("page", "1")
)
```

Và nếu cần rebuild URL:

```python id="m8g8e8"
items = list(url.query.items())
```

Không làm:

```python id="k5r6nw"
dict(url.query)
```

một cách vô thức.

---

# 27. 🧠 Tổng kết Buổi 24

### Duplicate query

```text
?tag=python&tag=sqlite
```

### Lấy tất cả values

```python id="zz0vwm"
url.query.getall("tag")
```

### Lấy toàn bộ entries

```python id="e6cr1d"
list(url.query.items())
```

### Không nên làm khi cần bảo toàn duplicate

```python id="b1a2ks"
dict(url.query)
```

### Rebuild

```python id="xq0m4w"
url.with_query(
    list(url.query.items())
)
```

### Mental model

```text
dict
    ↓
one key → one value

query / MultiDict
    ↓
one key → multiple values

list[tuple]
    ↓
explicit sequence of query entries
```

---

# 🧪 Bài tập Buổi 24

## Bài 1

Cho:

```python id="w3s6fu"
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

Lấy tất cả `tag`.

Kết quả:

```python
["python", "sqlite", "yarl"]
```

---

## Bài 2

In toàn bộ query entries bằng:

```python id="3t4f54"
url.query.items()
```

---

## Bài 3

Thêm:

```text
tag=crawler
```

nhưng giữ nguyên các `tag` cũ.

Kết quả:

```text
?tag=python&tag=sqlite&tag=yarl&tag=crawler
```

---

## Bài 4

Xóa:

```text
tag=sqlite
```

nhưng giữ:

```text
tag=python
tag=yarl
tag=crawler
```

---

## Bài 5 — rất quan trọng

Cho:

```text
https://example.com/search
?keyword=python
&tag=sqlite
&tag=yarl
&page=2
```

Hãy giải thích tại sao:

```python id="0wqg8b"
dict(url.query)
```

không phải lựa chọn tốt nếu mục tiêu là **bảo toàn chính xác toàn bộ query parameters**.

---

## Bài 6 — Novel Crawler

Viết:

```python id="12h4gn"
def get_query_values(
    url: URL,
    key: str,
) -> list[str]:
    ...
```

để:

```python id="9t5d2x"
get_query_values(url, "tag")
```

trả về:

```python
["python", "sqlite", "yarl"]
```

---

## Tiếp theo — Buổi 25

```text
### Buổi 25 — `query`
```

Buổi 25 chúng ta sẽ **đi sâu riêng vào `URL.query`**: kiểu dữ liệu thực tế của nó, `MultiDict`, iteration, indexing, `items()`, `keys()`, `values()`, cách đọc query một cách chính xác và cách nó khác `dict` thông thường.
